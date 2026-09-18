"""PDF text extraction for the Document Knowledge Assistant.

This module is intentionally standalone: it only opens a PDF, pulls text
from each page, and returns structured page records. Chunking, embeddings,
and APIs live elsewhere.
"""

from __future__ import annotations

from pathlib import Path
from typing import TypedDict

import pymupdf as fitz  # PyMuPDF (fitz is the historical module name)


MAX_PDF_PAGES = 50
MAX_PDF_SIZE_BYTES = 10 * 1024 * 1024  # 10 MB


class PageRecord(TypedDict):
    """One page of extracted PDF text plus its source metadata."""

    text: str
    page_number: int
    source: str


class PDFOpenError(Exception):
    """Raised when a PDF cannot be opened or read."""


class PDFPageLimitExceededError(Exception):
    """Raised when a PDF exceeds the maximum page limit."""


class PDFNoTextError(Exception):
    """Raised when a PDF contains no extractable text across all pages."""


def extract_pdf_pages(
    file_path: str | Path,
    max_pages: int = MAX_PDF_PAGES,
) -> list[PageRecord]:
    """Extract text from every page of a PDF with safety limits.

    Args:
        file_path: Path to a local PDF file.
        max_pages: Maximum number of pages allowed.

    Returns:
        A list of records, one per page, each containing:
        - text: extracted page text (empty string if the page has no text)
        - page_number: 1-based page index
        - source: original filename (not the full path)

    Raises:
        PDFOpenError: if the file is missing, not a PDF, or cannot be opened.
        PDFPageLimitExceededError: if page count > max_pages.
        PDFNoTextError: if 0 extractable characters are found across all pages.
    """
    path = Path(file_path)

    try:
        document = fitz.open(path)
    except Exception as exc:
        raise PDFOpenError(
            f"Unable to open or parse PDF at '{path}': {exc}"
        ) from exc

    try:
        total_pages = len(document)
        if total_pages == 0:
            raise PDFOpenError("The uploaded PDF has 0 pages.")

        if total_pages > max_pages:
            raise PDFPageLimitExceededError(
                f"PDF exceeds the maximum limit of {max_pages} pages (document has {total_pages} pages)."
            )

        source = path.name
        records: list[PageRecord] = []
        total_text_length = 0

        for page_index, page in enumerate(document):
            raw_text = page.get_text() or ""
            stripped = raw_text.strip()
            total_text_length += len(stripped)

            records.append(
                {
                    "text": stripped,
                    "page_number": page_index + 1,
                    "source": source,
                }
            )

        if total_text_length == 0:
            raise PDFNoTextError(
                "The uploaded PDF contains no extractable text. Scanned images without OCR are not supported."
            )

        return records
    finally:
        document.close()
