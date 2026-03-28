from __future__ import annotations

import re


WEIGHT_KEYS = ("novelty", "relevance", "distance", "feasibility", "fun", "api_fit")
TOKEN_RE = re.compile(r"[\w-]+", re.UNICODE)


def _normalize_weights(weights: dict) -> dict[str, float]:
    normalized = {key: max(0.0, float(weights.get(key, 0.0))) for key in WEIGHT_KEYS}
    total = sum(normalized.values()) or 1.0
    return {key: value / total for key, value in normalized.items()}


def _tokenize(text: str) -> set[str]:
    return {token.lower() for token in TOKEN_RE.findall(text or "")}


def score_idea(idea: dict, weights: dict) -> dict:
    normalized_weights = _normalize_weights(weights)

    distance_category = str(idea.get("distance_category") or "mid").lower()
    distance_value = float(idea.get("distance_value") or 0.35)
    distance_score_map = {"near": 0.38, "mid": 0.68, "far": 0.95}
    novelty_score_map = {"near": 0.32, "mid": 0.64, "far": 0.92}

    distance_score = max(
        0.0,
        min(1.0, (distance_score_map.get(distance_category, 0.65) + distance_value) / 2.0),
    )
    novelty_score = max(
        0.0,
        min(1.0, (novelty_score_map.get(distance_category, 0.6) + distance_value) / 2.0),
    )

    user_context_tokens = _tokenize(str(idea.get("user_context") or ""))
    idea_tokens = _tokenize(
        " ".join(
            [
                str(idea.get("summary") or ""),
                str(idea.get("why_interesting") or ""),
                str(idea.get("target_user") or ""),
                str(idea.get("main_tech") or ""),
            ]
        )
    )
    if not user_context_tokens:
        relevance_score = 0.5
    else:
        overlap = len(user_context_tokens & idea_tokens)
        relevance_score = max(0.25, min(1.0, overlap / max(1, len(user_context_tokens))))

    main_tech = str(idea.get("main_tech") or "").lower()
    complexity_penalties = sum(
        keyword in main_tech
        for keyword in ("blockchain", "robotics", "hardware", "custom model", "edge ai", "on-device training")
    )
    feasibility_bonus = sum(
        keyword in main_tech for keyword in ("api", "web", "fastapi", "slack", "notion", "github", "automation")
    )
    feasibility_score = max(0.1, min(1.0, 0.75 + 0.08 * feasibility_bonus - 0.12 * complexity_penalties))

    fun_point = str(idea.get("fun_point") or "")
    fun_score = max(0.15, min(1.0, len(fun_point.strip()) / 80.0))

    api_fit_score = 0.9 if "api" in main_tech else 0.45

    scored = {
        "novelty_score": round(novelty_score, 4),
        "relevance_score": round(relevance_score, 4),
        "distance_score": round(distance_score, 4),
        "feasibility_score": round(feasibility_score, 4),
        "fun_score": round(fun_score, 4),
        "api_fit_score": round(api_fit_score, 4),
    }
    total_score = sum(scored[f"{key}_score"] * normalized_weights[key] for key in WEIGHT_KEYS)
    scored["total_score"] = round(total_score, 4)
    return scored
