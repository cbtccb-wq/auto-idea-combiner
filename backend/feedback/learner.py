from __future__ import annotations


WEIGHT_KEYS = ("novelty", "relevance", "distance", "feasibility", "fun", "api_fit")
ADJUSTMENTS = {
    "wilder": {"novelty": 0.08, "distance": 0.08, "fun": 0.06, "feasibility": -0.03},
    "practical": {"relevance": 0.07, "feasibility": 0.08, "distance": -0.05, "novelty": -0.03},
    "closer": {"relevance": 0.05, "feasibility": 0.03, "distance": -0.04},
    "further": {"distance": 0.07, "novelty": 0.05, "fun": 0.03},
    "great": {"novelty": 0.02, "relevance": 0.02, "feasibility": 0.02, "fun": 0.02},
    "ok": {"relevance": 0.01, "feasibility": 0.01},
    "no": {"relevance": 0.03, "feasibility": 0.03, "novelty": -0.04, "fun": -0.03},
}


def _normalize(weights: dict[str, float]) -> dict[str, float]:
    sanitized = {key: max(0.01, float(weights.get(key, 0.0))) for key in WEIGHT_KEYS}
    total = sum(sanitized.values()) or 1.0
    return {key: round(value / total, 6) for key, value in sanitized.items()}


def update_weights(feedback_history: list[dict], current_weights: dict) -> dict:
    updated = {key: float(current_weights.get(key, 0.0)) for key in WEIGHT_KEYS}

    for feedback in feedback_history:
        rating = str(feedback.get("rating") or "").lower()
        adjustments = ADJUSTMENTS.get(rating)
        if not adjustments:
            continue
        for key, delta in adjustments.items():
            updated[key] = updated.get(key, 0.0) + delta

    return _normalize(updated)
