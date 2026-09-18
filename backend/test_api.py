"""Test script for FastAPI backend endpoints.

Run from backend directory:

    python test_api.py
"""

from __future__ import annotations

import json
import sys

from fastapi.testclient import TestClient

from app.main import app

# Ensure UTF-8 output encoding for terminals on Windows
if hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass

client = TestClient(app)


def test_root() -> None:
    print("=" * 50)
    print("Testing GET /")
    print("=" * 50)
    response = client.get("/")
    print(f"Status Code: {response.status_code}")
    print(f"Response Body: {json.dumps(response.json(), indent=2)}")
    print()


def test_docs() -> None:
    print("=" * 50)
    print("Testing GET /docs")
    print("=" * 50)
    response = client.get("/docs")
    print(f"Status Code: {response.status_code}")
    print(f"Docs Available: {'Swagger UI' in response.text}")
    print()


def test_query_in_context() -> None:
    print("=" * 50)
    print("Testing POST /query (In-context Question)")
    print("=" * 50)
    payload = {
        "question": "What are the problems with traditional approach for storing data?"
    }
    print(f"Request: {json.dumps(payload, indent=2)}")
    response = client.post("/query", json=payload)
    print(f"Status Code: {response.status_code}")
    print("Response:")
    print(json.dumps(response.json(), indent=2))
    print()


def test_query_out_of_context() -> None:
    print("=" * 50)
    print("Testing POST /query (Out-of-context Question)")
    print("=" * 50)
    payload = {
        "question": "Explain normalization in DBMS."
    }
    print(f"Request: {json.dumps(payload, indent=2)}")
    response = client.post("/query", json=payload)
    print(f"Status Code: {response.status_code}")
    print("Response:")
    print(json.dumps(response.json(), indent=2))
    print()


def test_query_empty() -> None:
    print("=" * 50)
    print("Testing POST /query (Empty Question - Validation Test)")
    print("=" * 50)
    payload = {"question": "   "}
    response = client.post("/query", json=payload)
    print(f"Status Code: {response.status_code}")
    print("Response:")
    print(json.dumps(response.json(), indent=2))
    print()


def main() -> None:
    test_root()
    test_docs()
    test_query_in_context()
    test_query_out_of_context()
    test_query_empty()


if __name__ == "__main__":
    main()
