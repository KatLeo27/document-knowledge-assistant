"""Manual test for grounded answer generation with Gemini LLM.

Run from the backend directory with the virtual environment active:

    python test_generator.py
"""

from __future__ import annotations

import sys

from app.generator import DocumentAnswerGenerator
from app.retriever import DocumentRetriever

# Ensure UTF-8 output encoding for terminals on Windows
if hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass

TEST_QUESTIONS = [
    "Explain ACID properties in DBMS.",
    "Explain normalization in DBMS.",
]


def main() -> None:
    retriever = DocumentRetriever()
    generator = DocumentAnswerGenerator()

    for idx, question in enumerate(TEST_QUESTIONS, start=1):
        print("=" * 60)
        print(f"TEST {idx}")
        print("=" * 60)
        print(f"Question:\n{question}\n")

        # 1. Retrieve top 3 chunks
        chunks = retriever.retrieve(query=question, top_k=3)

        # 2. Generate grounded answer
        result = generator.generate(question=question, chunks=chunks)

        print(f"Answer:\n{result['answer']}\n")

        print("Sources:")
        if result["sources"]:
            # Deduplicate source file + page number for clean listing
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
