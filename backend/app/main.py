"""FastAPI application entry point for the Document Knowledge Assistant.

This module exposes REST endpoints to query the grounded RAG pipeline,
ingest PDF documents into Chroma Cloud, and manage indexed knowledge.
"""

from __future__ import annotations

import logging
import os
from pathlib import Path
import shutil
import tempfile
from typing import Any

from dotenv import load_dotenv
from fastapi import Depends, FastAPI, File, HTTPException, UploadFile, status
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field, field_validator

from app.document_processor import (
    MAX_PDF_PAGES,
    MAX_PDF_SIZE_BYTES,
    PDFNoTextError,
    PDFOpenError,
    PDFPageLimitExceededError,
)
from app.ingestion import DocumentIngestionService
from app.rag_pipeline import RAGPipeline
from app.rate_limiter import query_rate_limiter, upload_rate_limiter

# Load backend/.env for environment variables
load_dotenv(Path(__file__).resolve().parent.parent / ".env")

logger = logging.getLogger("document_knowledge_assistant")
logging.basicConfig(level=logging.INFO)

app = FastAPI(
    title="InquireAI Document Knowledge API",
    description="RAG-powered Q&A API for document knowledge using Gemini and Chroma Cloud.",
    version="1.0.0",
)

# Build CORS allowed origins
DEFAULT_ORIGINS = [
    "http://localhost:5173",
    "http://127.0.0.1:5173",
    "http://localhost:3000",
    "http://127.0.0.1:3000",
]

frontend_env_url = (os.getenv("FRONTEND_URL") or "").strip()
allowed_origins_set = set(DEFAULT_ORIGINS)
if frontend_env_url:
    allowed_origins_set.add(frontend_env_url.rstrip("/"))

app.add_middleware(
    CORSMiddleware,
    allow_origins=list(allowed_origins_set),
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

MAX_QUESTION_LENGTH = 1000


class QueryRequest(BaseModel):
    """Incoming search/question query."""

    question: str = Field(
        ...,
        description="The natural language question to ask (max 1000 characters).",
        examples=["What are the problems with traditional approach for storing data?"],
    )
    top_k: int = Field(
        5,
        ge=1,
        le=5,
        description="Number of chunks to retrieve (capped at 5).",
    )

    @field_validator("question")
    @classmethod
    def validate_question(cls, value: str) -> str:
        trimmed = (value or "").strip()
        if not trimmed:
            raise ValueError("Question cannot be empty or blank.")
        if len(trimmed) > MAX_QUESTION_LENGTH:
            raise ValueError(
                f"Question exceeds the maximum length of {MAX_QUESTION_LENGTH} characters "
                f"({len(trimmed)} characters received)."
            )
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
    already_indexed: bool = False


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


class HealthResponse(BaseModel):
    """Health check status response."""

    status: str


@app.get(
    "/health",
    response_model=HealthResponse,
    summary="Lightweight service health check",
)
def health() -> dict[str, str]:
    """Return quick health status without invoking external LLM APIs."""
    return {"status": "ok"}


@app.get("/", summary="Root endpoint")
def root() -> dict[str, str]:
    """Return status confirming that the InquireAI API service is running."""
    return {"message": "InquireAI Document Knowledge API is running"}


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
    dependencies=[Depends(upload_rate_limiter)],
)
def upload_document(file: UploadFile = File(...)) -> dict[str, Any]:
    """Upload a PDF document, chunk it, embed it, and index it into Chroma Cloud."""
    if not file.filename:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Uploaded file must have a filename.",
        )

    safe_filename = Path(file.filename).name
    if not safe_filename.lower().endswith(".pdf"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid file type. Only PDF documents (.pdf) are supported.",
        )

    tmp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".pdf")
    temp_path = Path(tmp_file.name)

    try:
        # Stream file to disk while enforcing max file size (10 MB)
        bytes_written = 0
        chunk_size = 1024 * 1024  # 1 MB chunk

        while True:
            chunk = file.file.read(chunk_size)
            if not chunk:
                break
            bytes_written += len(chunk)
            if bytes_written > MAX_PDF_SIZE_BYTES:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Uploaded file exceeds the maximum allowed size of {MAX_PDF_SIZE_BYTES // (1024 * 1024)} MB.",
                )
            tmp_file.write(chunk)

        tmp_file.close()

        if bytes_written == 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="The uploaded PDF file is empty.",
            )

        # Ingest document (with page limit, text check, and duplicate check)
        result = ingestion_service.ingest_pdf(
            file_path=temp_path,
            original_filename=safe_filename,
        )

        return {
            "message": result["message"],
            "source": result["source"],
            "chunks_added": result["chunks_added"],
            "already_indexed": result.get("already_indexed", False),
        }
    except HTTPException:
        raise
    except PDFPageLimitExceededError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        ) from exc
    except PDFNoTextError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        ) from exc
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
    dependencies=[Depends(query_rate_limiter)],
)
def query_documents(request: QueryRequest) -> dict[str, Any]:
    """Execute a grounded RAG query using Chroma Cloud and Gemini LLM."""
    try:
        top_k = min(max(1, request.top_k), 5)
        result = pipeline.ask(question=request.question, top_k=top_k)
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

