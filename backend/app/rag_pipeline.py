"""End-to-end RAG pipeline orchestration for the Document Knowledge Assistant.

This module coordinates the DocumentRetriever and DocumentAnswerGenerator components
to answer questions grounded in the indexed document collection.
"""

from __future__ import annotations

from typing import Any, TypedDict

from app.generator import DocumentAnswerGenerator, SourceReference
from app.retriever import DocumentRetriever, RetrievalResult


class RAGResponse(TypedDict):
    """Structured response from the RAG pipeline."""

    answer: str
    sources: list[SourceReference]
    retrieved_chunks: list[RetrievalResult]


class RAGPipeline:
    """Orchestrate semantic retrieval and grounded answer generation."""

    def __init__(
        self,
        retriever: DocumentRetriever | None = None,
        generator: DocumentAnswerGenerator | None = None,
    ) -> None:
        self.retriever = retriever or DocumentRetriever()
        self.generator = generator or DocumentAnswerGenerator()

    def ask(self, question: str, top_k: int = 5) -> RAGResponse:
        """Run the complete RAG query flow.

        Args:
            question: Natural language question from the user.
            top_k: Number of relevant context chunks to retrieve.

        Returns:
            A dictionary containing:
            - answer: The grounded response string from Gemini.
            - sources: Deduplicated list of source document and page references.
            - retrieved_chunks: The raw retrieved chunks used as context.
        """
        cleaned_question = (question or "").strip()
        if not cleaned_question:
            return {
                "answer": "No question provided.",
                "sources": [],
                "retrieved_chunks": [],
            }

        # 1. Retrieve top-k relevant chunks from the vector store
        retrieved_chunks = self.retriever.retrieve(query=cleaned_question, top_k=top_k)

        # 2. Generate grounded answer from retrieved context
        generated = self.generator.generate(
            question=cleaned_question,
            chunks=retrieved_chunks,
        )

        return {
            "answer": generated["answer"],
            "sources": generated["sources"],
            "retrieved_chunks": retrieved_chunks,
        }
