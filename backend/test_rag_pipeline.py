"""Manual test for end-to-end RAG pipeline orchestration.

Run from the backend directory with the virtual environment active:

    python test_rag_pipeline.py
"""

from __future__ import annotations

import sys

from app.rag_pipeline import RAGPipeline

# Ensure UTF-8 output encoding for terminals on Windows
if hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass

TEST_QUESTIONS = [
    "What are the problems with traditional approach for storing data?",
    "Explain normalization in DBMS.",
]


def main() -> None:
    pipeline = RAGPipeline()

    for question in TEST_QUESTIONS:
        print("=" * 50)
        print("Question:")
        print(question)
        print()

        result = pipeline.ask(question=question, top_k=3)

        print("Answer:")
        print(result["answer"])
        print()

        print("Sources:")
        if result["sources"]:
            seen_pages = set()
            for src in result["sources"]:
                entry = (src["source"], src["page_number"])
                if entry not in seen_pages:
                    seen_pages.add(entry)
                    print(f"- {src['source']} — Page {src['page_number']}")
        else:
            print("- None")
        print()


if __name__ == "__main__":
    main()
