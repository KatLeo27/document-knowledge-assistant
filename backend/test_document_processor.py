"""Manual smoke test for PDF page extraction.

Run from the backend directory with the virtual environment active:

    python test_document_processor.py
"""

from pathlib import Path

from app.document_processor import extract_pdf_pages

# Repo root is one level above backend/
PROJECT_ROOT = Path(__file__).resolve().parent.parent
SAMPLE_PDF = PROJECT_ROOT / "data" / "sample-documents" / "DBMS.pdf"


def main() -> None:
    pages = extract_pdf_pages(SAMPLE_PDF)

    print(f"Pages processed: {len(pages)}")

    if not pages:
        print("No pages were extracted.")
        return

    first = pages[0]
    preview = first["text"][:500]

    print(f"Page number: {first['page_number']}")
    print(f"Source: {first['source']}")
    print("First 500 characters of page 1:")
    print(preview)


if __name__ == "__main__":
    main()
