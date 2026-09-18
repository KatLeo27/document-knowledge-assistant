"""Gemini embedding generation for document chunks and queries.

This module only creates vectors. It does not store them in ChromaDB or
generate answers.
"""

from __future__ import annotations

import os
from pathlib import Path

from dotenv import load_dotenv
from langchain_google_genai import GoogleGenerativeAIEmbeddings

# Load backend/.env so GEMINI_API_KEY is available during local runs.
load_dotenv(Path(__file__).resolve().parent.parent / ".env")

# Change this constant when Google deprecates the current embedding model.
EMBEDDING_MODEL = "gemini-embedding-001"


class MissingGeminiAPIKeyError(RuntimeError):
    """Raised when GEMINI_API_KEY is not available."""


class GeminiEmbeddings:
    """Reusable wrapper around LangChain's Gemini embedding model.

    The underlying LangChain object is exposed as ``client`` so a later
    ChromaDB stage can pass it in directly.
    """

    def __init__(
        self,
        model: str = EMBEDDING_MODEL,
        api_key: str | None = None,
    ) -> None:
        key = api_key or os.getenv("GEMINI_API_KEY")
        if not key:
            raise MissingGeminiAPIKeyError(
                "GEMINI_API_KEY is not set. Add it to backend/.env or export it "
                "in the environment before generating embeddings."
            )

        self.model_name = model
        self.client = GoogleGenerativeAIEmbeddings(
            model=model,
            google_api_key=key,
        )

    def embed_query(self, text: str) -> list[float]:
        """Embed a single search query."""
        return self.client.embed_query(text)

    def embed_texts(self, texts: list[str]) -> list[list[float]]:
        """Embed a list of raw strings (one vector per string)."""
        if not texts:
            return []
        return self.client.embed_documents(texts)

    def embed_chunks(self, chunks: list[dict]) -> list[list[float]]:
        """Embed chunk records from ``chunk_documents()``.

        Returns vectors in the same order as the input chunks so metadata
        from those records can be paired with embeddings later.
        """
        texts = [chunk["text"] for chunk in chunks]
        return self.embed_texts(texts)
