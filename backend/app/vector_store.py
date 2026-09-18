"""Persistent ChromaDB storage for precomputed document embeddings.

This module only stores chunks, vectors, and metadata. It does not generate
embeddings or run similarity search.
"""

from __future__ import annotations

from pathlib import Path

import chromadb
from chromadb.api.models.Collection import Collection

DEFAULT_COLLECTION_NAME = "document_knowledge"
PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
DEFAULT_PERSIST_DIRECTORY = PROJECT_ROOT / "data" / "chroma_db"


class ChromaVectorStore:
    """Open a local ChromaDB collection and insert already-embedded chunks."""

    def __init__(
        self,
        persist_directory: str | Path | None = None,
        collection_name: str = DEFAULT_COLLECTION_NAME,
    ) -> None:
        self.persist_directory = Path(persist_directory or DEFAULT_PERSIST_DIRECTORY)
        self.persist_directory.mkdir(parents=True, exist_ok=True)
        self.collection_name = collection_name

        # Persistent client writes the index under data/chroma_db/.
        self.client = chromadb.PersistentClient(path=str(self.persist_directory))

        # embedding_function=None: callers must pass Gemini vectors themselves.
        self.collection: Collection = self.client.get_or_create_collection(
            name=collection_name,
            embedding_function=None,
        )

    def add_chunks(self, chunks: list[dict], embeddings: list[list[float]]) -> int:
        """Store chunk text, Gemini embeddings, and page metadata.

        Existing IDs are updated so the same document can be re-ingested.
        Document IDs are the deterministic ``chunk_id`` values from chunker.py.
        """
        if len(chunks) != len(embeddings):
            raise ValueError(
                "Chunk count and embedding count must match: "
                f"{len(chunks)} chunks vs {len(embeddings)} embeddings."
            )
        if not chunks:
            return 0

        ids: list[str] = []
        documents: list[str] = []
        metadatas: list[dict] = []

        for chunk in chunks:
            metadata = chunk["metadata"]
            chunk_id = str(metadata["chunk_id"])
            ids.append(chunk_id)
            documents.append(chunk["text"])
            metadatas.append(
                {
                    "source": metadata["source"],
                    "page_number": int(metadata["page_number"]),
                    "chunk_id": chunk_id,
                }
            )

        self.collection.upsert(
            ids=ids,
            documents=documents,
            embeddings=embeddings,
            metadatas=metadatas,
        )
        return len(ids)

    def count(self) -> int:
        """Return how many items are currently in the collection."""
        return self.collection.count()
