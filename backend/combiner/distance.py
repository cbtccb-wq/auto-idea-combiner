from __future__ import annotations

import math


def compute_distance(emb_a: list[float], emb_b: list[float]) -> float:
    if emb_a is None or emb_b is None or len(emb_a) == 0 or len(emb_b) == 0 or len(emb_a) != len(emb_b):
        return 1.0

    dot_product = sum(a * b for a, b in zip(emb_a, emb_b, strict=False))
    norm_a = math.sqrt(sum(value * value for value in emb_a))
    norm_b = math.sqrt(sum(value * value for value in emb_b))
    if norm_a == 0 or norm_b == 0:
        return 1.0
    cosine_similarity = dot_product / (norm_a * norm_b)
    cosine_similarity = max(-1.0, min(1.0, cosine_similarity))
    return 1.0 - cosine_similarity


def categorize_distance(distance: float) -> str:
    if distance < 0.2:
        return "near"
    if distance < 0.45:
        return "mid"
    return "far"
