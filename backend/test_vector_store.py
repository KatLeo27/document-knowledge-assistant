"""Manual smoke test for persistent ChromaDB storage.

Run from the backend directory with the virtual environment active:

    python test_vector_store.py
"""

from pathlib import Path

from app.chunker import chunk_documents
from app.document_processor import extract_pdf_pages
from app.embeddings import GeminiEmbeddings
from app.vector_store import ChromaVectorStore

PROJECT_ROOT = Path(__file__).resolve().parent.parent
SAMPLE_PDF = PROJECT_ROOT / "data" / "sample-documents" / "DBMS.pdf"


# Development-only limit so this test does not embed the whole PDF every run.
TEST_CHUNK_LIMIT = 5


def main() -> None:
    pages = extract_pdf_pages(SAMPLE_PDF)
    chunks = chunk_documents(pages)
    test_chunks = chunks[:TEST_CHUNK_LIMIT]

    print(f"Total chunks generated from the PDF: {len(chunks)}")
    print(f"Chunks selected for this test: {len(test_chunks)}")

    embedder = GeminiEmbeddings()
    embeddings = embedder.embed_chunks(test_chunks)

    store = ChromaVectorStore()
    inserted = store.add_chunks(test_chunks, embeddings)
    sample = store.collection.peek(limit=1)

    print(f"Number of chunks being inserted: {inserted}")
    print(f"Collection name: {store.collection_name}")
    print(f"Items in collection after insertion: {store.count()}")

    if sample["ids"]:
        print(f"Sample item ID: {sample['ids'][0]}")
        print(f"Sample item metadata: {sample['metadatas'][0]}")
    else:
        print("No sample item was returned from the collection.")


if __name__ == "__main__":
    main()
