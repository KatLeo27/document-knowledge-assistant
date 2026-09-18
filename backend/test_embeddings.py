"""Manual smoke test for Gemini embeddings.

Run from the backend directory with the virtual environment active:

    python test_embeddings.py
"""

from pathlib import Path

from app.chunker import chunk_documents
from app.document_processor import extract_pdf_pages
from app.embeddings import GeminiEmbeddings

PROJECT_ROOT = Path(__file__).resolve().parent.parent
SAMPLE_PDF = PROJECT_ROOT / "data" / "sample-documents" / "DBMS.pdf"


def main() -> None:
    pages = extract_pdf_pages(SAMPLE_PDF)
    chunks = chunk_documents(pages)
    sample_chunks = chunks[:3]

    embedder = GeminiEmbeddings()
    vectors = embedder.embed_chunks(sample_chunks)

    if not vectors:
        print("No embeddings were generated.")
        return

    first_vector = vectors[0]
    first_chunk = sample_chunks[0]
    metadata = first_chunk["metadata"]

    print(f"Number of chunks embedded: {len(vectors)}")
    print(f"Embedding dimension: {len(first_vector)}")
    print(f"First few values of the first embedding: {first_vector[:8]}")
    print(f"Source: {metadata['source']}")
    print(f"Page number: {metadata['page_number']}")
    print(f"Chunk ID: {metadata['chunk_id']}")
    print(f"Embedding model: {embedder.model_name}")


if __name__ == "__main__":
    main()
