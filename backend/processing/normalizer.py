from __future__ import annotations

import re
from difflib import SequenceMatcher

from backend.processing.cleaner import clean_text


NON_WORD_RE = re.compile(r"[^\w\s-]", re.UNICODE)
WHITESPACE_RE = re.compile(r"\s+")


def _canonicalize(text: str) -> str:
    normalized = clean_text(text).lower()
    normalized = NON_WORD_RE.sub(" ", normalized)
    normalized = WHITESPACE_RE.sub(" ", normalized).strip()
    if normalized.endswith("ies") and len(normalized) > 4:
        normalized = normalized[:-3] + "y"
    elif normalized.endswith("s") and len(normalized) > 3 and not normalized.endswith("ss"):
        normalized = normalized[:-1]
    return normalized


def _looks_similar(candidate: str, existing: str) -> bool:
    if candidate == existing:
        return True
    if not candidate or not existing:
        return False

    candidate_tokens = set(candidate.split())
    existing_tokens = set(existing.split())
    if candidate_tokens and existing_tokens:
        overlap = len(candidate_tokens & existing_tokens) / len(candidate_tokens | existing_tokens)
        if overlap >= 0.8:
            return True

    return SequenceMatcher(a=candidate, b=existing).ratio() >= 0.88


def normalize_concepts(concepts: list[str]) -> list[str]:
    canonical_concepts: list[str] = []
    for raw_concept in concepts:
        canonical = _canonicalize(raw_concept)
        if not canonical:
            continue
        if any(_looks_similar(canonical, existing) for existing in canonical_concepts):
            continue
        canonical_concepts.append(canonical)
    return canonical_concepts
