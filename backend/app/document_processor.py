"""PDF text extraction for the Document Knowledge Assistant.

This module is intentionally standalone: it only opens a PDF, pulls text
from each page, and returns structured page records. Chunking, embeddings,
and APIs live elsewhere.
"""

from __future__ import annotations

from pathlib import Path
from typing import TypedDict

import pymupdf as fitz  # PyMuPDF (fitz is the historical module name)


class PageRecord(TypedDict):
    """One page of extracted PDF text plus its source metadata."""

    text: str
    page_number: int
    source: str


class PDFOpenError(Exception):
    """Raised when a PDF cannot be opened or read."""


def extract_pdf_pages(file_path: str | Path) -> list[PageRecord]:
    """Extract text from every page of a PDF.

    Args:
        file_path: Path to a local PDF file.

    Returns:
        A list of records, one per page, each containing:
        - text: extracted page text (empty string if the page has no text)
        - page_number: 1-based page index
        - source: original filename (not the full path)

    Raises:
        PDFOpenError: if the file is missing, not a PDF, or cannot be opened.
    """
    path = Path(file_path)

    try:
        # fitz.open raises FileNotFoundError / empty-file / format errors
        # depending on what is wrong with the path.
        document = fitz.open(path)
    except Exception as exc:
        raise PDFOpenError(
            f"Unable to open PDF at '{path}': {exc}"
        ) from exc

    source = path.name
    records: list[PageRecord] = []

    try:
        for page_index, page in enumerate(document):
            # get_text() can return None on unusual pages; treat that as empty.
            raw_text = page.get_text() or ""
            # Keep the record even when the page is blank so page numbers stay
            # aligned with the original document.
            records.append(
                {
                    "text": raw_text.strip(),
                    "page_number": page_index + 1,
                    "source": source,
                }
            )
    finally:
        document.close()

    return records
