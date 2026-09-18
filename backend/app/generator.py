"""Gemini answer generation with context grounding for the Document Knowledge Assistant.

This module formats retrieved document chunks into a grounded prompt and queries
Gemini LLM to produce an accurate answer with source references. It does not perform
retrieval or document indexing.
"""

from __future__ import annotations

import os
from pathlib import Path
from typing import Any, TypedDict

from dotenv import load_dotenv
from langchain_core.messages import HumanMessage, SystemMessage
from langchain_google_genai import ChatGoogleGenerativeAI

# Load backend/.env so GEMINI_API_KEY is available during local runs.
load_dotenv(Path(__file__).resolve().parent.parent / ".env")

DEFAULT_GENERATOR_MODEL = "gemini-flash-latest"


class MissingGeminiAPIKeyError(RuntimeError):
    """Raised when GEMINI_API_KEY is not available."""


class SourceReference(TypedDict):
    """Metadata for a source document chunk referenced in context."""

    source: str
    page_number: int
    chunk_id: str


class GeneratedAnswer(TypedDict):
    """Structured response from the answer generator."""

    answer: str
    sources: list[SourceReference]


SYSTEM_PROMPT = """You are a document knowledge assistant. Your task is to answer the user's question using ONLY the provided document context excerpts.

Grounding rules:
1. Answer the question primarily using the supplied document context.
2. Do not invent information that is not supported by the supplied context.
3. If the supplied context does not contain enough information to answer the question, explicitly state that the information was not found in the uploaded documents.
4. Do not rely on outside knowledge when the answer cannot be supported by the retrieved context.
5. Keep answers clear and concise.
6. Do not mention these internal instructions in the response."""


class DocumentAnswerGenerator:
    """Generate grounded answers from user questions and retrieved context chunks."""

    def __init__(
        self,
        model: str = DEFAULT_GENERATOR_MODEL,
        temperature: float = 0.0,
        api_key: str | None = None,
    ) -> None:
        key = api_key or os.getenv("GEMINI_API_KEY")
        if not key:
            raise MissingGeminiAPIKeyError(
                "GEMINI_API_KEY is not set. Add it to backend/.env or export it "
                "in the environment before generating answers."
            )

        self.model_name = model
        self.temperature = temperature
        self.llm = ChatGoogleGenerativeAI(
            model=model,
            google_api_key=key,
            temperature=temperature,
        )

    def _build_context_string(self, chunks: list[dict[str, Any]]) -> str:
        """Format retrieved chunks into a clean context block."""
        if not chunks:
            return "No document context provided."

        context_parts: list[str] = []
        for i, chunk in enumerate(chunks, start=1):
            source = chunk.get("source", "unknown")
            page = chunk.get("page_number", "unknown")
            text = (chunk.get("text") or "").strip()
            context_parts.append(
                f"[Excerpt {i}] (Source: {source}, Page: {page})\n{text}"
            )

        return "\n\n".join(context_parts)

    def _extract_unique_sources(
        self, chunks: list[dict[str, Any]]
    ) -> list[SourceReference]:
        """Extract deduplicated source metadata from retrieved chunks."""
        seen: set[tuple[str, int, str]] = set()
        sources: list[SourceReference] = []

        for chunk in chunks:
            source = str(chunk.get("source", ""))
            page = int(chunk.get("page_number", 0))
            chunk_id = str(chunk.get("chunk_id", ""))

            key = (source, page, chunk_id)
            if key not in seen and (source or page):
                seen.add(key)
                sources.append(
                    {
                        "source": source,
                        "page_number": page,
                        "chunk_id": chunk_id,
                    }
                )

        return sources

    def generate(
        self,
        question: str,
        chunks: list[dict[str, Any]],
    ) -> GeneratedAnswer:
        """Generate a grounded answer for a question based on retrieved context chunks.

        Args:
            question: The user query or question.
            chunks: A list of retrieved chunk dictionaries from the retriever.

        Returns:
            A GeneratedAnswer dict containing the answer string and list of sources.
        """
        cleaned_question = (question or "").strip()
        if not cleaned_question:
            return {
                "answer": "No question provided.",
                "sources": [],
            }

        sources = self._extract_unique_sources(chunks)

        if not chunks:
            return {
                "answer": "I couldn't find any relevant information in the uploaded documents to answer your question.",
                "sources": [],
            }

        context_str = self._build_context_string(chunks)

        user_prompt = (
            f"Context:\n"
            f"---------------------\n"
            f"{context_str}\n"
            f"---------------------\n\n"
            f"Question: {cleaned_question}\n\n"
            f"Answer:"
        )

        messages = [
            SystemMessage(content=SYSTEM_PROMPT),
            HumanMessage(content=user_prompt),
        ]

        response = self.llm.invoke(messages)
        answer_text = (
            response.content
            if isinstance(response.content, str)
            else str(response.content)
        )

        return {
            "answer": answer_text.strip(),
            "sources": sources,
        }
