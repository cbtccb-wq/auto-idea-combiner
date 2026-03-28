from __future__ import annotations

from pathlib import Path

import chromadb


class ChromaStore:
    def __init__(self, persist_dir: str) -> None:
        path = Path(persist_dir).expanduser()
        path.mkdir(parents=True, exist_ok=True)
        self._client = chromadb.PersistentClient(path=str(path))
        self._collection = self._client.get_or_create_collection(name="concepts")

    def upsert(self, concepts: list[str], embeddings: list[list[float]], ids: list[str]) -> None:
        if not concepts:
            return
        self._collection.upsert(
            ids=ids,
            documents=concepts,
            embeddings=embeddings,
            metadatas=[{"concept": concept} for concept in concepts],
        )

    def query_similar(self, embedding: list[float], n_results: int = 20) -> list[dict]:
        if not embedding:
            return []
        result = self._collection.query(
            query_embeddings=[embedding],
            n_results=n_results,
            include=["documents", "metadatas", "distances"],
        )
        ids = result.get("ids", [[]])[0]
        documents = result.get("documents", [[]])[0]
        metadatas = result.get("metadatas", [[]])[0]
        distances = result.get("distances", [[]])[0]
        return [
            {
                "id": item_id,
                "concept": document,
                "metadata": metadata or {},
                "distance": distance,
            }
            for item_id, document, metadata, distance in zip(ids, documents, metadatas, distances, strict=False)
        ]

    def get_all_concepts(self) -> list[dict]:
        result = self._collection.get(include=["documents", "metadatas", "embeddings"])
        ids = result.get("ids", [])
        documents = result.get("documents", [])
        metadatas = result.get("metadatas", [])
        embeddings = result.get("embeddings", [])
        return [
            {
                "id": item_id,
                "concept": document,
                "metadata": metadata or {},
                "embedding": embedding,
            }
            for item_id, document, metadata, embedding in zip(ids, documents, metadatas, embeddings, strict=False)
        ]
