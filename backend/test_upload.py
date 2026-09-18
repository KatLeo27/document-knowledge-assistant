"""Test script for document upload endpoint and multi-document retrieval.

Run from the backend directory:

    python test_upload.py
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

from fastapi.testclient import TestClient

from app.main import app, pipeline

# Ensure UTF-8 output encoding for terminals on Windows
if hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass

client = TestClient(app)
SAMPLE_DIR = Path(__file__).resolve().parent.parent / "data" / "sample-documents"
DBMS_PDF = SAMPLE_DIR / "DBMS.pdf"
PYTHON_PDF = SAMPLE_DIR / "Python_Basics.pdf"


def main() -> None:
    print("=" * 60)
    print("1. Initial ChromaDB Collection State")
    print("=" * 60)
    initial_count = pipeline.retriever.vector_store.count()
    print(f"Collection count before test: {initial_count} chunks\n")

    print("=" * 60)
    print("2. Uploading existing document (DBMS.pdf) - Idempotency Test")
    print("=" * 60)
    with open(DBMS_PDF, "rb") as f:
        response = client.post(
            "/upload",
            files={"file": ("DBMS.pdf", f, "application/pdf")},
        )
    print(f"Status Code: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
    count_after_dbms = pipeline.retriever.vector_store.count()
    print(f"Collection count after re-uploading DBMS.pdf: {count_after_dbms} chunks (No duplicates added)\n")

    print("=" * 60)
    print("3. Uploading second document (Python_Basics.pdf)")
    print("=" * 60)
    with open(PYTHON_PDF, "rb") as f:
        response = client.post(
            "/upload",
            files={"file": ("Python_Basics.pdf", f, "application/pdf")},
        )
    print(f"Status Code: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
    count_after_python = pipeline.retriever.vector_store.count()
    print(f"Collection count after uploading Python_Basics.pdf: {count_after_python} chunks\n")

    print("=" * 60)
    print("4. Querying the newly uploaded document (Python_Basics.pdf)")
    print("=" * 60)
    query_payload = {"question": "Who created Python and in what year was it released?"}
    response = client.post("/query", json=query_payload)
    print(f"Status Code: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}\n")

    print("=" * 60)
    print("5. Querying the original document (DBMS.pdf)")
    print("=" * 60)
    query_payload = {"question": "What are the problems with traditional approach for storing data?"}
    response = client.post("/query", json=query_payload)
    print(f"Status Code: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}\n")

    print("=" * 60)
    print("6. Invalid Upload Validation Tests")
    print("=" * 60)
    # Non-pdf extension
    response = client.post(
        "/upload",
        files={"file": ("notes.txt", b"some text content", "text/plain")},
    )
    print(f"Non-PDF Upload Status: {response.status_code}, Detail: {response.json().get('detail')}")

    # Empty pdf
    response = client.post(
        "/upload",
        files={"file": ("empty.pdf", b"", "application/pdf")},
    )
    print(f"Empty PDF Upload Status: {response.status_code}, Detail: {response.json().get('detail')}\n")


if __name__ == "__main__":
    main()
