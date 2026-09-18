"""Split extracted PDF pages into overlapping text chunks.

This module only chunks already-extracted page records. It does not open
PDFs, create embeddings, or talk to a vector store.
"""

from __future__ import annotations

from typing import TypedDict

from langchain_text_splitters import RecursiveCharacterTextSplitter


# Initial RAG chunk settings. Tune later if retrieval quality needs it.
DEFAULT_CHUNK_SIZE = 1000
DEFAULT_CHUNK_OVERLAP = 150


class ChunkMetadata(TypedDict):
    source: str
    page_number: int
    chunk_id: str


class ChunkRecord(TypedDict):
    text: str
    metadata: ChunkMetadata


def _make_chunk_id(source: str, page_number: int, chunk_index: int) -> str:
    """Build a stable ID from filename, page, and in-page chunk index."""
    return f"{source}::page_{page_number}::chunk_{chunk_index}"


def chunk_documents(
    documents: list[dict],
    chunk_size: int = DEFAULT_CHUNK_SIZE,
    chunk_overlap: int = DEFAULT_CHUNK_OVERLAP,
) -> list[ChunkRecord]:
    """Split page-level records into overlapping character chunks.

    Args:
        documents: Page records from PDF extraction. Each item should have
            ``text``, ``page_number``, and ``source``.
        chunk_size: Maximum characters per chunk.
        chunk_overlap: Characters shared between consecutive chunks.

    Returns:
        Chunk records. Empty pages produce no chunks so later stages do not
        store blank embeddings.
    """
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap,
    )

    chunks: list[ChunkRecord] = []

    for page in documents:
        page_text = (page.get("text") or "").strip()
        if not page_text:
            continue

        source = page.get("source", "unknown")
        page_number = int(page.get("page_number", 0))
        pieces = splitter.split_text(page_text)

        for chunk_index, piece in enumerate(pieces):
            chunks.append(
                {
                    "text": piece,
                    "metadata": {
                        "source": source,
                        "page_number": page_number,
                        "chunk_id": _make_chunk_id(source, page_number, chunk_index),
                    },
                }
            )

    return chunks
