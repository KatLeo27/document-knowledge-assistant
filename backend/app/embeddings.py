"""Gemini embedding generation for document chunks and queries.

This module only creates vectors. It does not store them in ChromaDB or
generate answers.
"""

from __future__ import annotations

import os
import time
from pathlib import Path

from dotenv import load_dotenv
from langchain_google_genai import GoogleGenerativeAIEmbeddings

# Load backend/.env so GEMINI_API_KEY is available during local runs.
load_dotenv(Path(__file__).resolve().parent.parent / ".env")

# Change this constant when Google deprecates the current embedding model.
EMBEDDING_MODEL = "gemini-embedding-001"

# Conservative defaults: small batches plus a short pause reduce burst traffic
# against the free-tier embedding quota. These are not a way to exceed quota.
DEFAULT_EMBED_BATCH_SIZE = 8
DEFAULT_EMBED_BATCH_DELAY_SECONDS = 0.4


class MissingGeminiAPIKeyError(RuntimeError):
    """Raised when GEMINI_API_KEY is not available."""


class GeminiQuotaExceededError(RuntimeError):
    """Raised when Gemini returns HTTP 429 / RESOURCE_EXHAUSTED."""


def _is_quota_error(exc: BaseException) -> bool:
    """Detect Gemini rate-limit / quota failures from the exception text."""
    message = str(exc).upper()
    return (
        "429" in message
        or "RESOURCE_EXHAUSTED" in message
        or "QUOTA" in message
    )


class GeminiEmbeddings:
    """Reusable wrapper around LangChain's Gemini embedding model.

    The underlying LangChain object is exposed as ``client`` so a later
    ChromaDB stage can pass it in directly.
    """

    def __init__(
        self,
        model: str = EMBEDDING_MODEL,
        api_key: str | None = None,
        batch_size: int = DEFAULT_EMBED_BATCH_SIZE,
        batch_delay_seconds: float = DEFAULT_EMBED_BATCH_DELAY_SECONDS,
    ) -> None:
        key = api_key or os.getenv("GEMINI_API_KEY")
        if not key:
            raise MissingGeminiAPIKeyError(
                "GEMINI_API_KEY is not set. Add it to backend/.env or export it "
                "in the environment before generating embeddings."
            )
        if batch_size < 1:
            raise ValueError("batch_size must be at least 1.")
        if batch_delay_seconds < 0:
            raise ValueError("batch_delay_seconds cannot be negative.")

        self.model_name = model
        self.batch_size = batch_size
        self.batch_delay_seconds = batch_delay_seconds
        self.client = GoogleGenerativeAIEmbeddings(
            model=model,
            google_api_key=key,
        )

    def embed_query(self, text: str) -> list[float]:
        """Embed a single search query."""
        try:
            return self.client.embed_query(text)
        except Exception as exc:
            self._raise_if_quota_error(exc)
            raise

    def embed_text(self, text: str) -> list[float]:
        """Alias for ``embed_query`` so single-text callers stay readable."""
        return self.embed_query(text)

    def embed_texts(self, texts: list[str]) -> list[list[float]]:
        """Embed a list of strings in order, one API batch at a time."""
        if not texts:
            return []

        embeddings: list[list[float]] = []
        total = len(texts)

        for start in range(0, total, self.batch_size):
            batch = texts[start : start + self.batch_size]
            try:
                batch_vectors = self.client.embed_documents(batch)
            except Exception as exc:
                self._raise_if_quota_error(exc)
                raise

            if len(batch_vectors) != len(batch):
                raise RuntimeError(
                    "Gemini returned a different number of embeddings than texts "
                    f"in the batch starting at index {start}: "
                    f"{len(batch)} texts vs {len(batch_vectors)} embeddings."
                )

            embeddings.extend(batch_vectors)

            # Pause only between batches, never after the last one.
            has_more = start + self.batch_size < total
            if has_more and self.batch_delay_seconds > 0:
                time.sleep(self.batch_delay_seconds)

        return embeddings

    def embed_chunks(self, chunks: list[dict]) -> list[list[float]]:
        """Embed chunk records from ``chunk_documents()``.

        Returns vectors in the same order as the input chunks so metadata
        from those records can be paired with embeddings later.
        """
        texts = [chunk["text"] for chunk in chunks]
        return self.embed_texts(texts)

    @staticmethod
    def _raise_if_quota_error(exc: BaseException) -> None:
        if not _is_quota_error(exc):
            return
        raise GeminiQuotaExceededError(
            "Gemini embedding quota was reached (HTTP 429 / RESOURCE_EXHAUSTED). "
            "The free-tier request limit has been exceeded. Wait and retry later, "
            "or reduce batch size / ingest fewer chunks per run. "
            "This client does not retry automatically."
        ) from exc
