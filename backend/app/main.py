"""FastAPI application entry point for the Document Knowledge Assistant.

This module exposes REST endpoints to query the grounded RAG pipeline.
"""

from __future__ import annotations

import logging
from typing import Any

from fastapi import FastAPI, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field, field_validator

from app.rag_pipeline import RAGPipeline

logger = logging.getLogger("document_knowledge_assistant")
logging.basicConfig(level=logging.INFO)

app = FastAPI(
    title="Document Knowledge Assistant API",
    description="RAG-powered Q&A API for document knowledge using Gemini and ChromaDB.",
    version="1.0.0",
)

# Enable CORS for local dev / frontend integration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Instantiate the shared RAG pipeline
pipeline = RAGPipeline()


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


@app.get("/", summary="Health check / root endpoint")
def root() -> dict[str, str]:
    """Return status indicating that the API service is active."""
    return {"message": "Document Knowledge Assistant API is running"}


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
