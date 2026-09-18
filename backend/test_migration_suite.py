import io
import pymupdf as fitz
from fastapi.testclient import TestClient

from app.main import app
from app.vector_store import ChromaVectorStore

client = TestClient(app)

def test_1_health_check():
    print('Testing GET /health...')
    resp = client.get('/health')
    assert resp.status_code == 200, f'Health check failed: {resp.text}'
    assert resp.json() == {'status': 'ok'}
    print('  [PASS] GET /health returned 200 ok')

def test_2_root():
    print('Testing GET /...')
    resp = client.get('/')
    assert resp.status_code == 200
    print('  [PASS] GET / returned 200')

def test_3_chroma_cloud_connection():
    print('Testing Chroma Cloud connection...')
    store = ChromaVectorStore()
    assert store.is_cloud is True, 'Expected Chroma Cloud connection'
    count = store.count()
    assert count > 0, f'Expected chunks in Chroma Cloud, got {count}'
    docs = store.list_documents()
    sources = [d['source'] for d in docs]
    assert 'DBMS.pdf' in sources, f'DBMS.pdf not found in {sources}'
    print(f'  [PASS] Chroma Cloud connected with {count} chunks across {len(docs)} documents: {sources}')

def test_4_query_dbms():
    print('Testing RAG query against existing DBMS.pdf...')
    resp = client.post('/query', json={'question': 'What are ACID properties in database management?'})
    assert resp.status_code == 200, f'Query failed: {resp.text}'
    data = resp.json()
    assert 'answer' in data and len(data['answer']) > 0
    assert 'sources' in data and len(data['sources']) > 0
    print('  [PASS] RAG query returned grounded answer with citations:')
    print('    Sources:', [s['source'] + ' p.' + str(s['page_number']) for s in data['sources']])

def test_5_long_question_rejection():
    print('Testing rejection of excessively long question (>1000 chars)...')
    long_q = 'What is ' + ('very long text ' * 100)
    resp = client.post('/query', json={'question': long_q})
    assert resp.status_code == 400 or resp.status_code == 422, f'Expected 400/422, got {resp.status_code}'
    print('  [PASS] Excessively long question rejected with HTTP', resp.status_code)

def test_6_duplicate_upload_prevention():
    print('Testing duplicate upload protection for DBMS.pdf...')
    doc = fitz.open()
    page = doc.new_page()
    page.insert_text((50, 72), 'DBMS test text content.')
    pdf_bytes = doc.tobytes()
    doc.close()

    resp = client.post(
        '/upload',
        files={'file': ('DBMS.pdf', io.BytesIO(pdf_bytes), 'application/pdf')}
    )
    assert resp.status_code == 200
    data = resp.json()
    assert data.get('already_indexed') is True, f'Expected already_indexed=True, got {data}'
    assert data.get('chunks_added') == 0
    print('  [PASS] Duplicate upload prevented without re-embedding:', data['message'])

def test_7_empty_pdf_rejection():
    print('Testing empty PDF rejection...')
    resp = client.post(
        '/upload',
        files={'file': ('empty.pdf', io.BytesIO(b''), 'application/pdf')}
    )
    assert resp.status_code == 400
    print('  [PASS] Empty PDF rejected with HTTP 400')

def test_8_page_limit_rejection():
    print('Testing 50+ page limit rejection...')
    doc = fitz.open()
    for _ in range(55):
        p = doc.new_page()
        p.insert_text((50, 72), 'Page content text.')
    pdf_bytes = doc.tobytes()
    doc.close()

    resp = client.post(
        '/upload',
        files={'file': ('large_pages.pdf', io.BytesIO(pdf_bytes), 'application/pdf')}
    )
    assert resp.status_code == 400
    assert '50 pages' in resp.text
    print('  [PASS] 55-page PDF rejected with HTTP 400:', resp.json().get('detail'))

if __name__ == '__main__':
    print('=== RUNNING MIGRATION VERIFICATION SUITE ===')
    test_1_health_check()
    test_2_root()
    test_3_chroma_cloud_connection()
    test_4_query_dbms()
    test_5_long_question_rejection()
    test_6_duplicate_upload_prevention()
    test_7_empty_pdf_rejection()
    test_8_page_limit_rejection()
    print('=== ALL 8 VERIFICATION TESTS PASSED SUCCESSFULLY! ===')
