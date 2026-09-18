"""Document ingestion service for extracting, chunking, embedding, and storing PDFs.

This module orchestrates existing pipeline stages (document processor, chunker,
embeddings, and vector store) to index uploaded PDF files.
"""

from __future__ import annotations

from pathlib import Path
from typing import TypedDict

from app.chunker import ChunkRecord, chunk_documents
from app.document_processor import PageRecord, extract_pdf_pages
from app.embeddings import GeminiEmbeddings
from app.vector_store import ChromaVectorStore


class IngestionResult(TypedDict):
    """Result summary of a document ingestion run."""

    source: str
    chunks_added: int
    page_count: int


class DocumentIngestionService:
    """Ingest PDF documents into the persistent ChromaDB collection."""

    def __init__(
        self,
        vector_store: ChromaVectorStore | None = None,
        embedder: GeminiEmbeddings | None = None,
    ) -> None:
        self.vector_store = vector_store or ChromaVectorStore()
        self.embedder = embedder or GeminiEmbeddings()

    def ingest_pdf(
        self,
        file_path: str | Path,
        original_filename: str | None = None,
    ) -> IngestionResult:
        """Process a PDF file and store its embedded chunks in ChromaDB.

        Args:
            file_path: Path to the local PDF file (e.g. temporary file).
            original_filename: Original user-provided filename to store in metadata.

        Returns:
            IngestionResult dictionary with source, chunks_added, and page_count.
        """
        path = Path(file_path)
        source_name = original_filename or path.name

        # 1. Extract text and page records from PDF
        pages: list[PageRecord] = extract_pdf_pages(path)

        # Ensure metadata references the clean original filename
        for page in pages:
            page["source"] = source_name

        page_count = len(pages)

        # 2. Split page records into overlapping text chunks
        chunks: list[ChunkRecord] = chunk_documents(pages)

        if not chunks:
            return {
                "source": source_name,
                "chunks_added": 0,
                "page_count": page_count,
            }

        # 3. Generate Gemini embeddings for all chunks
        embeddings = self.embedder.embed_chunks(chunks)

        # 4. Upsert chunks and embeddings into persistent ChromaDB
        chunks_added = self.vector_store.add_chunks(chunks, embeddings)

        return {
            "source": source_name,
            "chunks_added": chunks_added,
            "page_count": page_count,
        }
