"""Semantic retrieval over stored document embeddings.

This module embeds natural-language queries with Gemini and searches the
persistent ChromaDB vector store for the top-k most relevant chunks.
It does not call an LLM to generate answers.
"""

from __future__ import annotations

from typing import Any, TypedDict

from app.embeddings import GeminiEmbeddings
from app.vector_store import ChromaVectorStore


class RetrievalResult(TypedDict):
    """Structured result for a single retrieved chunk."""

    text: str
    source: str
    page_number: int
    chunk_id: str
    distance: float | None


class DocumentRetriever:
    """Retrieve semantically relevant chunks from ChromaDB for a text query."""

    def __init__(
        self,
        vector_store: ChromaVectorStore | None = None,
        embedder: GeminiEmbeddings | None = None,
    ) -> None:
        self.vector_store = vector_store or ChromaVectorStore()
        self.embedder = embedder or GeminiEmbeddings()

    def retrieve(self, query: str, top_k: int = 5) -> list[dict[str, Any]]:
        """Embed the query and retrieve the top_k most relevant chunks from ChromaDB.

        Args:
            query: Natural language query string.
            top_k: Number of relevant chunks to retrieve.

        Returns:
            A list of result dictionaries containing:
            - text: Chunk text content.
            - source: Source document name.
            - page_number: Page number in the original document.
            - chunk_id: Unique deterministic chunk identifier.
            - distance: ChromaDB distance value.
        """
        cleaned_query = (query or "").strip()
        if not cleaned_query:
            return []

        if top_k < 1:
            return []

        total_items = self.vector_store.count()
        if total_items == 0:
            return []

        n_results = min(top_k, total_items)

        # Generate embedding for the query using the existing Gemini embeddings
        query_vector = self.embedder.embed_query(cleaned_query)

        # Query the existing ChromaDB collection
        query_response = self.vector_store.collection.query(
            query_embeddings=[query_vector],
            n_results=n_results,
            include=["documents", "metadatas", "distances"],
        )

        ids_nested = query_response.get("ids", [[]])
        docs_nested = query_response.get("documents", [[]])
        metas_nested = query_response.get("metadatas", [[]])
        dists_nested = query_response.get("distances", [[]])

        if not ids_nested or not ids_nested[0]:
            return []

        ids = ids_nested[0]
        docs = docs_nested[0] if docs_nested else []
        metas = metas_nested[0] if metas_nested else []
        dists = dists_nested[0] if dists_nested else []

        results: list[dict[str, Any]] = []

        for i, chunk_id in enumerate(ids):
            text = docs[i] if i < len(docs) else ""
            meta = metas[i] if (i < len(metas) and metas[i] is not None) else {}
            distance = dists[i] if i < len(dists) else None

            source = str(meta.get("source", ""))
            page_number = int(meta.get("page_number", 0))
            stored_chunk_id = str(meta.get("chunk_id", chunk_id))

            results.append(
                {
                    "text": text,
                    "source": source,
                    "page_number": page_number,
                    "chunk_id": stored_chunk_id,
                    "distance": distance,
                }
            )

        return results
