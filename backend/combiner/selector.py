from __future__ import annotations

from backend.combiner.distance import categorize_distance, compute_distance


def select_combinations(
    concepts: list[dict],
    n_near: int = 2,
    n_mid: int = 3,
    n_far: int = 2,
) -> list[tuple]:
    grouped: dict[str, list[tuple[dict, dict, str, float]]] = {"near": [], "mid": [], "far": []}
    seen_pairs: set[tuple[str, str]] = set()

    for index, concept_a in enumerate(concepts):
        embedding_a = concept_a.get("embedding")
        concept_a_text = str(concept_a.get("concept") or concept_a.get("text") or "").strip()
        if not concept_a_text or not embedding_a:
            continue

        for concept_b in concepts[index + 1 :]:
            embedding_b = concept_b.get("embedding")
            concept_b_text = str(concept_b.get("concept") or concept_b.get("text") or "").strip()
            if not concept_b_text or not embedding_b:
                continue

            pair_key = tuple(sorted((concept_a_text, concept_b_text)))
            if pair_key in seen_pairs:
                continue
            seen_pairs.add(pair_key)

            distance = compute_distance(embedding_a, embedding_b)
            category = categorize_distance(distance)
            grouped[category].append((concept_a, concept_b, category, distance))

    grouped["near"].sort(key=lambda item: item[3])
    grouped["mid"].sort(key=lambda item: abs(item[3] - 0.325))
    grouped["far"].sort(key=lambda item: item[3], reverse=True)

    selected: list[tuple] = []
    selected.extend((a, b, category) for a, b, category, _ in grouped["near"][:n_near])
    selected.extend((a, b, category) for a, b, category, _ in grouped["mid"][:n_mid])
    selected.extend((a, b, category) for a, b, category, _ in grouped["far"][:n_far])

    if selected:
        return selected

    for category in ("mid", "near", "far"):
        if grouped[category]:
            a, b, distance_category, _ = grouped[category][0]
            return [(a, b, distance_category)]
    return []
