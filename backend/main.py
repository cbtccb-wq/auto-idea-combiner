from __future__ import annotations

import asyncio
import json
import logging
import re
import sys
from collections import Counter
from contextlib import asynccontextmanager
from pathlib import Path
from typing import Literal
from uuid import uuid4

if __package__ in {None, ""}:
    sys.path.append(str(Path(__file__).resolve().parent.parent))

from fastapi import Depends, FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from sqlmodel import Session, desc, select

from backend.combiner.distance import compute_distance
from backend.combiner.selector import select_combinations
from backend.config import get_settings
from backend.embedding.chroma_store import ChromaStore
from backend.embedding.generator import EmbeddingGenerator
from backend.feedback.learner import update_weights
from backend.llm.factory import get_llm
from backend.llm.prompts import build_idea_generation_prompt
from backend.models.db import (
    Concept,
    Feedback,
    IdeaCard,
    ScoreWeights,
    create_db_and_tables,
    engine,
    get_session,
)
from backend.processing.cleaner import clean_text
from backend.processing.extractor import extract_keywords, extract_nouns
from backend.processing.normalizer import normalize_concepts
from backend.scoring.scorer import score_idea
from backend.collectors.local_files import get_recent_files


ALLOWED_RATINGS = {"great", "ok", "no", "closer", "further", "practical", "wilder"}
WEIGHT_KEYS = ("novelty", "relevance", "distance", "feasibility", "fun", "api_fit")
JSON_BLOCK_RE = re.compile(r"\{.*\}", re.DOTALL)

settings = get_settings()
logging.basicConfig(level=getattr(logging, settings.log_level.upper(), logging.INFO))
logger = logging.getLogger("auto-idea-combiner")
embedding_generator: EmbeddingGenerator | None = None
chroma_store: ChromaStore | None = None

def _load_all_models() -> None:
    _get_embedding_generator()
    extract_keywords("warmup startup text for model initialization")
    extract_nouns("warmup")


@asynccontextmanager
async def lifespan(app: FastAPI):
    create_db_and_tables()
    _get_chroma_store()
    logger.info("Loading models (first run may take a few minutes)...")
    await asyncio.to_thread(_load_all_models)
    logger.info("All models ready.")
    with Session(engine) as session:
        _ensure_score_weights(session)
    yield


app = FastAPI(title="Auto Idea Combiner Backend", lifespan=lifespan)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:1420", "tauri://localhost"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class IngestRequest(BaseModel):
    dirs: list[str] = Field(default_factory=list)
    texts: list[str] = Field(default_factory=list)


class GenerateIdeasRequest(BaseModel):
    detail_level: str = Field(default="standard")
    n_ideas: int = Field(default=3, ge=1, le=10)


class FeedbackRequest(BaseModel):
    idea_card_id: str
    rating: Literal["great", "ok", "no", "closer", "further", "practical", "wilder"]


class SettingsUpdateRequest(BaseModel):
    weights: dict[str, float]


def _get_embedding_generator() -> EmbeddingGenerator:
    global embedding_generator
    if embedding_generator is None:
        embedding_generator = EmbeddingGenerator(settings.embedding_model)
    return embedding_generator


def _get_chroma_store() -> ChromaStore:
    global chroma_store
    if chroma_store is None:
        chroma_store = ChromaStore(str(settings.resolved_chroma_persist_dir))
    return chroma_store


def _normalize_weights(weights: dict[str, float]) -> dict[str, float]:
    normalized = {key: max(0.0, float(weights.get(key, 0.0))) for key in WEIGHT_KEYS}
    total = sum(normalized.values()) or 1.0
    return {key: round(value / total, 6) for key, value in normalized.items()}


def _current_weight_values(session: Session) -> dict[str, float]:
    latest = session.exec(select(ScoreWeights).order_by(desc(ScoreWeights.updated_at))).first()
    if latest:
        return {
            "novelty": latest.novelty,
            "relevance": latest.relevance,
            "distance": latest.distance,
            "feasibility": latest.feasibility,
            "fun": latest.fun,
            "api_fit": latest.api_fit,
        }
    return _normalize_weights(settings.score_weights())


def _ensure_score_weights(session: Session) -> dict[str, float]:
    current = _current_weight_values(session)
    latest = session.exec(select(ScoreWeights).order_by(desc(ScoreWeights.updated_at))).first()
    if latest:
        return current

    session.add(ScoreWeights(**current))
    session.commit()
    return current


def _coerce_text(value: object) -> str:
    if value is None:
        return ""
    if isinstance(value, str):
        return value.strip()
    return json.dumps(value, ensure_ascii=False)


def _extract_json(raw_text: str) -> dict | None:
    if not raw_text.strip():
        return None

    cleaned = raw_text.strip().removeprefix("```json").removeprefix("```").removesuffix("```").strip()
    candidates = [cleaned]
    match = JSON_BLOCK_RE.search(cleaned)
    if match:
        candidates.append(match.group(0))

    for candidate in candidates:
        try:
            parsed = json.loads(candidate)
        except json.JSONDecodeError:
            continue
        if isinstance(parsed, dict):
            return parsed
    return None


def _build_user_context(session: Session) -> str:
    recent_concepts = session.exec(
        select(Concept).order_by(desc(Concept.frequency), desc(Concept.created_at)).limit(8)
    ).all()
    if not recent_concepts:
        return "ユーザー文脈はまだありません。幅広く使える汎用的なアイデアを優先してください。"
    joined = ", ".join(concept.text for concept in recent_concepts)
    return f"最近の関心トピック: {joined}"


def _fallback_idea(
    concept_a: str,
    concept_b: str,
    distance_category: str,
    detail_level: str,
) -> dict[str, str]:
    detail_suffix = {
        "brief": "まずは最小構成で試せる形にする。",
        "deep": "プロダクトとワークフローの詳細まで踏み込む。",
    }.get(detail_level, "素早く検証できる小さいスコープに収める。")
    distance_label = {"near": "近い", "mid": "中程度の", "far": "遠い"}.get(distance_category, distance_category)
    return {
        "title": f"{concept_a} × {concept_b} ラボ",
        "summary": (
            f"{concept_a} と {concept_b} を組み合わせた軽量デスクトップコンセプト。"
            f"日常の意思決定をサポートします。{detail_suffix}"
        ),
        "why_interesting": (
            f"{distance_label}距離の組み合わせにより、既存ツールにない独自の視点が生まれます。"
        ),
        "target_user": (
            f"{concept_a} に関心を持ち、{concept_b} を仕事や趣味に活かしたい人。"
        ),
        "main_tech": "FastAPI バックエンド、ローカル検索 API、LLM API、Tauri デスクトップ UI",
        "mvp_outline": (
            f"{concept_a} に関連する入力を受け取り、{concept_b} の視点で再解釈して提案を返す。"
        ),
        "differentiator": f"{concept_a} と {concept_b} の距離感を可視化・調整できる点が差別化になる。",
        "fun_point": (
            f"{concept_a} と {concept_b} の距離を近づけたり遠ざけたりして、意図的にアイデアの角度を変えられる。"
        ),
        "risks": "ターゲットが広すぎる可能性があり、出力品質が低いとリピート利用に影響する。",
    }


def _idea_card_from_payload(
    payload: dict,
    concept_a: str,
    concept_b: str,
    detail_level: str,
    scores: dict,
) -> IdeaCard:
    return IdeaCard(
        title=_coerce_text(payload.get("title")) or f"{concept_a} x {concept_b}",
        concept_a=concept_a,
        concept_b=concept_b,
        summary=_coerce_text(payload.get("summary")),
        why_interesting=_coerce_text(payload.get("why_interesting")),
        target_user=_coerce_text(payload.get("target_user")),
        main_tech=_coerce_text(payload.get("main_tech")),
        mvp_outline=_coerce_text(payload.get("mvp_outline")),
        differentiator=_coerce_text(payload.get("differentiator")),
        fun_point=_coerce_text(payload.get("fun_point")),
        risks=_coerce_text(payload.get("risks")),
        novelty_score=scores["novelty_score"],
        relevance_score=scores["relevance_score"],
        distance_score=scores["distance_score"],
        feasibility_score=scores["feasibility_score"],
        fun_score=scores["fun_score"],
        api_fit_score=scores["api_fit_score"],
        total_score=scores["total_score"],
        detail_level=detail_level,
    )


def _gather_text_sources(payload: IngestRequest) -> list[dict]:
    sources: list[dict] = []
    scan_dirs = payload.dirs or settings.expanded_local_scan_dirs

    for text in payload.texts:
        if clean_text(text):
            sources.append({"source": "manual", "content": text})

    for item in get_recent_files(scan_dirs, max_files=50):
        if clean_text(item["content"]):
            sources.append({"source": item["path"], "content": item["content"]})

    return sources



@app.get("/api/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.post("/api/ingest")
def ingest(payload: IngestRequest, session: Session = Depends(get_session)) -> dict[str, int]:
    text_sources = _gather_text_sources(payload)
    if not text_sources:
        return {"concepts_added": 0}

    extracted_pairs: list[tuple[str, str]] = []
    for item in text_sources:
        source = item["source"]
        content = clean_text(item["content"])
        concepts = normalize_concepts(extract_keywords(content, top_n=10) + extract_nouns(content)[:15])
        extracted_pairs.extend((concept, source) for concept in concepts)

    if not extracted_pairs:
        return {"concepts_added": 0}

    counts = Counter(concept for concept, _ in extracted_pairs)
    source_map: dict[str, str] = {}
    for concept, source in extracted_pairs:
        source_map.setdefault(concept, source)

    concept_texts = list(counts.keys())
    embeddings = _get_embedding_generator().encode(concept_texts)
    new_concepts = 0
    chroma_ids: list[str] = []

    for concept_text, embedding in zip(concept_texts, embeddings, strict=False):
        existing = session.exec(select(Concept).where(Concept.text == concept_text)).first()
        if existing:
            existing.frequency += counts[concept_text]
            if not existing.source or existing.source == "unknown":
                existing.source = source_map[concept_text]
            embedding_id = existing.embedding_id
        else:
            embedding_id = str(uuid4())
            session.add(
                Concept(
                    text=concept_text,
                    source=source_map[concept_text],
                    embedding_id=embedding_id,
                    frequency=counts[concept_text],
                )
            )
            new_concepts += 1
        chroma_ids.append(embedding_id)

    session.commit()
    _get_chroma_store().upsert(concept_texts, embeddings, chroma_ids)
    return {"concepts_added": new_concepts}


@app.post("/api/ideas/generate", response_model=list[IdeaCard])
def generate_ideas(
    payload: GenerateIdeasRequest,
    session: Session = Depends(get_session),
) -> list[IdeaCard]:
    vector_concepts = _get_chroma_store().get_all_concepts()
    if len(vector_concepts) < 2:
        raise HTTPException(status_code=400, detail="At least two concepts are required")

    candidate_pairs = select_combinations(vector_concepts)
    if not candidate_pairs:
        raise HTTPException(status_code=400, detail="Unable to find concept combinations")

    weights = _ensure_score_weights(session)
    user_context = _build_user_context(session)

    llm = None
    try:
        llm = get_llm(settings.llm_provider, settings)
    except ValueError as exc:
        logger.warning("LLM unavailable, falling back to template generation: %s", exc)

    created_cards: list[IdeaCard] = []
    for concept_a, concept_b, distance_category in candidate_pairs[: payload.n_ideas]:
        concept_a_text = str(concept_a.get("concept") or concept_a.get("text") or "")
        concept_b_text = str(concept_b.get("concept") or concept_b.get("text") or "")
        _ea = concept_a.get("embedding")
        _eb = concept_b.get("embedding")
        distance_value = compute_distance(_ea if _ea is not None else [], _eb if _eb is not None else [])
        prompt = build_idea_generation_prompt(
            concept_a=concept_a_text,
            concept_b=concept_b_text,
            distance_category=distance_category,
            user_context=user_context,
            detail_level=payload.detail_level,
        )

        generated_payload: dict | None = None
        if llm is not None:
            try:
                generated_payload = _extract_json(llm.generate(prompt))
            except Exception as exc:
                logger.warning("LLM generation failed, using fallback idea: %s", exc)

        if generated_payload is None:
            generated_payload = _fallback_idea(
                concept_a=concept_a_text,
                concept_b=concept_b_text,
                distance_category=distance_category,
                detail_level=payload.detail_level,
            )

        generated_payload["distance_category"] = distance_category
        generated_payload["distance_value"] = distance_value
        generated_payload["user_context"] = user_context
        scores = score_idea(generated_payload, weights)
        idea_card = _idea_card_from_payload(
            payload=generated_payload,
            concept_a=concept_a_text,
            concept_b=concept_b_text,
            detail_level=payload.detail_level,
            scores=scores,
        )
        session.add(idea_card)
        created_cards.append(idea_card)

    session.commit()
    for card in created_cards:
        session.refresh(card)
    return created_cards


@app.get("/api/ideas", response_model=list[IdeaCard])
def list_ideas(session: Session = Depends(get_session)) -> list[IdeaCard]:
    return list(session.exec(select(IdeaCard).order_by(desc(IdeaCard.created_at)).limit(20)).all())


@app.post("/api/feedback")
def submit_feedback(payload: FeedbackRequest, session: Session = Depends(get_session)) -> dict[str, bool]:
    if payload.rating not in ALLOWED_RATINGS:
        raise HTTPException(status_code=400, detail="Invalid rating")

    idea_card = session.get(IdeaCard, payload.idea_card_id)
    if idea_card is None:
        raise HTTPException(status_code=404, detail="Idea card not found")

    session.add(Feedback(idea_card_id=payload.idea_card_id, rating=payload.rating))
    session.commit()

    updated_weights = update_weights(
        feedback_history=[{"rating": payload.rating}],
        current_weights=_current_weight_values(session),
    )
    session.add(ScoreWeights(**updated_weights))
    session.commit()
    return {"ok": True}


@app.get("/api/concepts/map")
def get_concepts_map(session: Session = Depends(get_session)) -> dict[str, list]:
    concepts = list(
        session.exec(
            select(Concept).order_by(desc(Concept.frequency), desc(Concept.created_at)).limit(100)
        ).all()
    )
    embedding_items = {item["id"]: item for item in _get_chroma_store().get_all_concepts()}

    nodes = [
        {
            "id": concept.embedding_id,
            "label": concept.text,
            "frequency": concept.frequency,
            "source": concept.source,
        }
        for concept in concepts
    ]

    edges: list[dict] = []
    for index, left in enumerate(concepts):
        left_embedding = embedding_items.get(left.embedding_id, {}).get("embedding")
        if left_embedding is None:
            continue
        for right in concepts[index + 1 :]:
            right_embedding = embedding_items.get(right.embedding_id, {}).get("embedding")
            if right_embedding is None:
                continue
            distance = compute_distance(left_embedding, right_embedding)
            if distance >= 0.38:
                continue
            edges.append(
                {
                    "source": left.embedding_id,
                    "target": right.embedding_id,
                    "weight": round(1.0 - distance, 4),
                    "distance": round(distance, 4),
                }
            )

    return {"nodes": nodes, "edges": edges}


@app.get("/api/settings")
def get_settings_endpoint(session: Session = Depends(get_session)) -> dict[str, dict[str, float]]:
    return {"weights": _ensure_score_weights(session)}


@app.put("/api/settings")
def update_settings(
    payload: SettingsUpdateRequest,
    session: Session = Depends(get_session),
) -> dict[str, dict[str, float]]:
    merged = _current_weight_values(session)
    for key, value in payload.weights.items():
        if key not in WEIGHT_KEYS:
            raise HTTPException(status_code=400, detail=f"Unknown weight: {key}")
        merged[key] = float(value)

    normalized = _normalize_weights(merged)
    session.add(ScoreWeights(**normalized))
    session.commit()
    return {"weights": normalized}
