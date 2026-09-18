"""Manual smoke test for page-to-chunk splitting.

Run from the backend directory with the virtual environment active:

    python test_chunker.py
"""

import sys
from pathlib import Path

from app.chunker import chunk_documents
from app.document_processor import extract_pdf_pages

# PDF text can include symbols that Windows consoles cannot encode.
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(errors="replace")

PROJECT_ROOT = Path(__file__).resolve().parent.parent
SAMPLE_PDF = PROJECT_ROOT / "data" / "sample-documents" / "DBMS.pdf"


def main() -> None:
    pages = extract_pdf_pages(SAMPLE_PDF)
    chunks = chunk_documents(pages)

    print(f"Total pages extracted: {len(pages)}")
    print(f"Total chunks generated: {len(chunks)}")
    print()

    preview_count = min(3, len(chunks))
    print(f"First {preview_count} chunks:")
    print("-" * 60)

    for chunk in chunks[:preview_count]:
        metadata = chunk["metadata"]
        text = chunk["text"]
        print(f"chunk_id: {metadata['chunk_id']}")
        print(f"source: {metadata['source']}")
        print(f"page_number: {metadata['page_number']}")
        print(f"character_count: {len(text)}")
        print("text preview:")
        print(text[:300])
        print("-" * 60)


if __name__ == "__main__":
    main()
