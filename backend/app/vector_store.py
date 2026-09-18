"""Persistent ChromaDB storage for precomputed document embeddings.

This module supports Chroma Cloud and local PersistentClient fallback.
It only stores chunks, vectors, and metadata. It does not generate
embeddings or run similarity search.
"""

from __future__ import annotations

import os
from pathlib import Path
from typing import Any

import chromadb
from chromadb.api.models.Collection import Collection
from dotenv import load_dotenv

# Load backend/.env so Chroma environment variables are available.
load_dotenv(Path(__file__).resolve().parent.parent / ".env")

DEFAULT_COLLECTION_NAME = "document_knowledge"
DEFAULT_DATABASE = "inquireai"
PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
DEFAULT_PERSIST_DIRECTORY = PROJECT_ROOT / "data" / "chroma_db"


class ChromaVectorStore:
    """Connect to Chroma Cloud or local ChromaDB collection."""

    def __init__(
        self,
        persist_directory: str | Path | None = None,
        collection_name: str = DEFAULT_COLLECTION_NAME,
    ) -> None:
        self.collection_name = collection_name
        self.persist_directory = Path(persist_directory or DEFAULT_PERSIST_DIRECTORY)

        chroma_api_key = os.getenv("CHROMA_API_KEY")
        chroma_tenant = os.getenv("CHROMA_TENANT")
        chroma_database = os.getenv("CHROMA_DATABASE", DEFAULT_DATABASE)

        if chroma_api_key:
            # Connect to Chroma Cloud using official CloudClient API
            self.client = chromadb.CloudClient(
                tenant=chroma_tenant,
                database=chroma_database,
                api_key=chroma_api_key,
            )
            self.is_cloud = True
        else:
            # Fallback to local PersistentClient if no Cloud credentials provided
            self.persist_directory.mkdir(parents=True, exist_ok=True)
            self.client = chromadb.PersistentClient(path=str(self.persist_directory))
            self.is_cloud = False

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

    def list_documents(self) -> list[dict[str, Any]]:
        """Return a summary of indexed documents with chunk counts."""
        if self.count() == 0:
            return []

        data = self.collection.get(include=["metadatas"])
        metadatas = data.get("metadatas") or []

        counts: dict[str, int] = {}
        for meta in metadatas:
            if meta and "source" in meta:
                source = str(meta["source"])
                counts[source] = counts.get(source, 0) + 1

        return [
            {"source": source, "chunk_count": count}
            for source, count in sorted(counts.items())
        ]

    def delete_document(self, source: str) -> int:
        """Delete all chunks belonging to a specific source document.

        Returns:
            The number of chunks deleted.
        """
        existing = self.collection.get(where={"source": source})
        existing_ids = existing.get("ids") or []
        if not existing_ids:
            return 0

        self.collection.delete(where={"source": source})
        return len(existing_ids)

    def has_document(self, source: str) -> bool:
        """Check whether chunks for the given source document already exist."""
        if self.count() == 0:
            return False
        existing = self.collection.get(where={"source": source}, limit=1)
        existing_ids = existing.get("ids") or []
        return len(existing_ids) > 0

