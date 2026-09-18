"""Test suite for full document management API.

Endpoints tested:
- GET /
- GET /documents
- POST /upload
- POST /query
- DELETE /documents/{filename}

Run from backend directory:

    python test_doc_management.py
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

from fastapi.testclient import TestClient

from app.main import app

# Ensure UTF-8 output encoding for terminals on Windows
if hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass

client = TestClient(app)
SAMPLE_DIR = Path(__file__).resolve().parent.parent / "data" / "sample-documents"
PYTHON_PDF = SAMPLE_DIR / "Python_Basics.pdf"


def main() -> None:
    print("=" * 60)
    print("1. Testing GET / (Health check)")
    print("=" * 60)
    res = client.get("/")
    print(f"Status: {res.status_code}")
    print(f"Body: {json.dumps(res.json(), indent=2)}\n")

    print("=" * 60)
    print("2. Testing GET /documents (List initial documents)")
    print("=" * 60)
    res = client.get("/documents")
    print(f"Status: {res.status_code}")
    print(f"Body: {json.dumps(res.json(), indent=2)}\n")

    print("=" * 60)
    print("3. Testing POST /query (Query before modifications)")
    print("=" * 60)
    res = client.post("/query", json={"question": "What are the problems with traditional approach for storing data?"})
    print(f"Status: {res.status_code}")
    print(f"Answer: {res.json().get('answer')[:120]}...")
    print(f"Sources: {json.dumps(res.json().get('sources'), indent=2)}\n")

    print("=" * 60)
    print("4. Testing DELETE /documents/Python_Basics.pdf (Delete specific document)")
    print("=" * 60)
    res = client.delete("/documents/Python_Basics.pdf")
    print(f"Status: {res.status_code}")
    print(f"Body: {json.dumps(res.json(), indent=2)}\n")

    print("=" * 60)
    print("5. Testing GET /documents (Verify Python_Basics.pdf was removed)")
    print("=" * 60)
    res = client.get("/documents")
    print(f"Status: {res.status_code}")
    print(f"Body: {json.dumps(res.json(), indent=2)}\n")

    print("=" * 60)
    print("6. Testing DELETE /documents/non_existent.pdf (404 Test)")
    print("=" * 60)
    res = client.delete("/documents/non_existent.pdf")
    print(f"Status: {res.status_code}")
    print(f"Body: {json.dumps(res.json(), indent=2)}\n")

    print("=" * 60)
    print("7. Testing POST /upload (Re-upload Python_Basics.pdf)")
    print("=" * 60)
    with open(PYTHON_PDF, "rb") as f:
        res = client.post("/upload", files={"file": ("Python_Basics.pdf", f, "application/pdf")})
    print(f"Status: {res.status_code}")
    print(f"Body: {json.dumps(res.json(), indent=2)}\n")

    print("=" * 60)
    print("8. Testing GET /documents (Verify both documents are present)")
    print("=" * 60)
    res = client.get("/documents")
    print(f"Status: {res.status_code}")
    print(f"Body: {json.dumps(res.json(), indent=2)}\n")

    print("=" * 60)
    print("9. Testing POST /query (Verify both documents are queryable)")
    print("=" * 60)
    res1 = client.post("/query", json={"question": "Who created Python?"})
    print(f"Query 1 (Python) -> Status: {res1.status_code}, Answer: {res1.json().get('answer')}")
    res2 = client.post("/query", json={"question": "What is Database?"})
    print(f"Query 2 (DBMS)   -> Status: {res2.status_code}, Answer: {res2.json().get('answer')[:120]}...\n")


if __name__ == "__main__":
    main()
