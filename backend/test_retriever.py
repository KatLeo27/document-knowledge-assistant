"""Manual test for semantic retrieval from ChromaDB.

Run from the backend directory with the virtual environment active:

    python test_retriever.py
"""

from __future__ import annotations

import sys

from app.retriever import DocumentRetriever

# Ensure UTF-8 output encoding for terminals that default to CP1252 on Windows
if hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass

TEST_QUERIES = [
    "What is normalization in DBMS?",
    "What is a primary key?",
    "Explain ACID properties.",
    "What is a transaction?",
]


def main() -> None:
    retriever = DocumentRetriever()
    queries = sys.argv[1:] if len(sys.argv) > 1 else TEST_QUERIES

    for query in queries:
        print("=" * 50)
        print(f"Query: {query}")
        print("=" * 50)
        print()

        results = retriever.retrieve(query=query, top_k=3)

        if not results:
            print("No matching chunks found.\n")
            continue

        for rank, item in enumerate(results, start=1):
            snippet = item["text"][:200].replace("\r\n", " ").replace("\n", " ").strip()
            if len(item["text"]) > 200:
                snippet += "..."

            print(f"Rank {rank}")
            print(f"Source: {item['source']}")
            print(f"Page: {item['page_number']}")
            print(f"Chunk ID: {item['chunk_id']}")
            print(f"Distance: {item['distance']}")
            print(f"Text: {snippet}")
            print()


if __name__ == "__main__":
    main()
