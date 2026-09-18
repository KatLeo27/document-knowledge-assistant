"""FastAPI application entry point for the Document Knowledge Assistant.

This module exposes REST endpoints to query the grounded RAG pipeline.
"""

from __future__ import annotations

import logging
import shutil
import tempfile
from pathlib import Path
from typing import Any

from fastapi import FastAPI, File, HTTPException, UploadFile, status
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field, field_validator

from app.document_processor import PDFOpenError
from app.ingestion import DocumentIngestionService
from app.rag_pipeline import RAGPipeline

logger = logging.getLogger("document_knowledge_assistant")
logging.basicConfig(level=logging.INFO)

app = FastAPI(
    title="Document Knowledge Assistant API",
    description="RAG-powered Q&A API for document knowledge using Gemini and ChromaDB.",
    version="1.0.0",
)

ALLOWED_ORIGINS = [
    "http://localhost:5173",
    "http://127.0.0.1:5173",
    "http://localhost:3000",
    "http://127.0.0.1:3000",
]

# Enable CORS for local dev / frontend integration
app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Shared RAG pipeline and Ingestion service
pipeline = RAGPipeline()
ingestion_service = DocumentIngestionService(
    vector_store=pipeline.retriever.vector_store,
    embedder=pipeline.retriever.embedder,
)


class QueryRequest(BaseModel):
    """Incoming search/question query."""

    question: str = Field(
        ...,
        description="The natural language question to ask.",
        examples=["What are the problems with traditional approach for storing data?"],
    )

    @field_validator("question")
    @classmethod
    def validate_question(cls, value: str) -> str:
        trimmed = (value or "").strip()
        if not trimmed:
            raise ValueError("Question cannot be empty or blank.")
        return trimmed


class SourceItem(BaseModel):
    """Source citation item."""

    source: str
    page_number: int
    chunk_id: str | None = None


class QueryResponse(BaseModel):
    """Grounded query response."""

    answer: str
    sources: list[SourceItem]


class UploadResponse(BaseModel):
    """Response model for uploaded and indexed document."""

    message: str
    source: str
    chunks_added: int


class DocumentInfo(BaseModel):
    """Information about an indexed document."""

    source: str
    chunk_count: int


class DocumentListResponse(BaseModel):
    """Response model for list of indexed documents."""

    documents: list[DocumentInfo]


class DeleteDocumentResponse(BaseModel):
    """Response model for deleted document."""

    message: str
    source: str
    chunks_deleted: int


@app.get("/", summary="Health check / root endpoint")
def root() -> dict[str, str]:
    """Return status indicating that the API service is active."""
    return {"message": "Document Knowledge Assistant API is running"}


@app.get(
    "/documents",
    response_model=DocumentListResponse,
    summary="List all indexed documents",
)
def list_documents() -> dict[str, Any]:
    """Return a list of currently indexed document sources and chunk counts."""
    try:
        documents = pipeline.retriever.vector_store.list_documents()
        return {"documents": documents}
    except Exception as exc:
        logger.exception("Error retrieving document list: %s", exc)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An internal error occurred while retrieving indexed documents.",
        ) from exc


@app.delete(
    "/documents/{filename}",
    response_model=DeleteDocumentResponse,
    summary="Delete an indexed document by filename",
)
def delete_document(filename: str) -> dict[str, Any]:
    """Delete all chunks belonging to a specific source document."""
    # Sanitize filename (prevent path traversal)
    safe_filename = Path(filename).name
    if not safe_filename:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Filename cannot be empty.",
        )

    try:
        chunks_deleted = pipeline.retriever.vector_store.delete_document(safe_filename)
        if chunks_deleted == 0:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Document '{safe_filename}' not found in the index.",
            )

        return {
            "message": f"Document '{safe_filename}' deleted successfully",
            "source": safe_filename,
            "chunks_deleted": chunks_deleted,
        }
    except HTTPException:
        raise
    except Exception as exc:
        logger.exception("Error deleting document '%s': %s", safe_filename, exc)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An internal error occurred while deleting the document.",
        ) from exc


@app.post(
    "/upload",
    response_model=UploadResponse,
    summary="Upload and index a PDF document",
)
def upload_document(file: UploadFile = File(...)) -> dict[str, Any]:
    """Upload a PDF document, chunk it, embed it, and index it into ChromaDB."""
    if not file.filename:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Uploaded file must have a filename.",
        )

    # Sanitize filename (prevent path traversal)
    safe_filename = Path(file.filename).name
    if not safe_filename.lower().endswith(".pdf"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid file type. Only PDF documents (.pdf) are supported.",
        )

    # Save to a temporary file for processing
    tmp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".pdf")
    temp_path = Path(tmp_file.name)

    try:
        shutil.copyfileobj(file.file, tmp_file)
        tmp_file.close()

        if temp_path.stat().st_size == 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="The uploaded PDF file is empty.",
            )

        # Ingest document
        result = ingestion_service.ingest_pdf(
            file_path=temp_path,
            original_filename=safe_filename,
        )

        return {
            "message": "Document indexed successfully",
            "source": result["source"],
            "chunks_added": result["chunks_added"],
        }
    except HTTPException:
        raise
    except PDFOpenError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid or corrupted PDF file: {exc}",
        ) from exc
    except Exception as exc:
        logger.exception("Error ingesting document '%s': %s", safe_filename, exc)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An internal error occurred during document indexing.",
        ) from exc
    finally:
        file.file.close()
        if temp_path.exists():
            temp_path.unlink(missing_ok=True)


@app.post(
    "/query",
    response_model=QueryResponse,
    summary="Ask a question against indexed documents",
)
def query_documents(request: QueryRequest) -> dict[str, Any]:
    """Execute a grounded RAG query using the existing pipeline."""
    try:
        result = pipeline.ask(question=request.question)
        return {
            "answer": result["answer"],
            "sources": result["sources"],
        }
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        ) from exc
    except Exception as exc:
        logger.exception("Error processing RAG query: %s", exc)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An internal error occurred while generating the answer.",
        ) from exc
