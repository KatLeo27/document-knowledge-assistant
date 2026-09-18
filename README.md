# InquireAI — Document Knowledge Assistant

**InquireAI** is a multi-document AI knowledge assistant that uses **Retrieval-Augmented Generation (RAG)** to answer questions based on information contained in uploaded documents.

Powered by **Chroma Cloud** for hosted vector storage and **Google Gemini** for embeddings and grounded language generation, InquireAI retrieves relevant excerpts from your indexed PDF documents, generates grounded answers, and cites exact page numbers and chunk identifiers.

---

## ✨ Features & Protections

- 📄 **Multi-Document PDF Ingestion**: Upload, index, and query multiple PDF documents.
- ☁️ **Chroma Cloud Vector Database**: Fully hosted, persistent vector search with `chromadb.CloudClient`.
- 🧠 **Grounded Q&A**: Gemini synthesizes answers strictly grounded in retrieved document context to eliminate hallucinations.
- 📚 **Source Citations**: Every response cites the source filename, page number, and chunk context.
- ⚡ **Duplicate Prevention**: Re-uploading an existing document checks Chroma Cloud first and skips re-embedding to conserve API quota.
- 🛡️ **Upload Safety Limits**:
  - Max file size: **10 MB**
  - Max page count: **50 pages**
  - Validated PDF format (rejects non-PDF and corrupted files)
  - Text validation (rejects empty or un-extractable scanned files)
- ⏱️ **Rate Limiting & Abuse Protection**:
  - **Queries**: 10 requests / minute / client IP
  - **Uploads**: 3 uploads / hour / client IP
  - Serverless-compatible sliding window rate limiter
- 🔍 **Query Limits**: Capped at 1,000 characters per question and `top_k <= 5` retrieval depth.
- 🌐 **Independent Vercel Deployment**: Dedicated frontend and backend deployment configs.

---

## 🏗️ System Architecture

```text
                           ┌────────────────────────┐
                           │      User / Client     │
                           └───────────┬────────────┘
                                       │
                                       ▼
             ┌────────────────────────────────────────────────────┐
             │            React / Vite Frontend (Vercel)          │
             └─────────────────────────┬──────────────────────────┘
                                       │  REST API (VITE_API_URL)
                                       ▼
             ┌────────────────────────────────────────────────────┐
             │             FastAPI Backend (Vercel)               │
             │   - Sliding-Window Rate Limiting (IP-based)        │
             │   - Safety Checks (10MB, 50 pgs, Text validation)  │
             └─────────────┬──────────────────────────┬───────────┘
                           │                          │
              [Document Ingestion]              [Query Workflow]
                           │                          │
                           ▼                          ▼
             ┌─────────────────────────┐   ┌─────────────────────────┐
             │     PyMuPDF (fitz)      │   │  Gemini Embeddings API  │
             │  (Page-aware extract)   │   │  (gemini-embedding-001) │
             └─────────────┬───────────┘   └──────────┬──────────────┘
                           │                          │
                           ▼                          ▼
             ┌─────────────────────────┐   ┌─────────────────────────┐
             │ LangChain Text Splitter │   │ Chroma Cloud Search     │
             │ (1000 chunk / 150 over) │   │ (api.trychroma.com)     │
             └─────────────┬───────────┘   └──────────┬──────────────┘
                           │                          │
                           ▼                          ▼
             ┌─────────────────────────┐   ┌─────────────────────────┐
             │  Gemini Embeddings API  │   │  Gemini Flash LLM       │
             │  (gemini-embedding-001) │   │  (Grounded Generation)  │
             └─────────────┬───────────┘   └──────────┬──────────────┘
                           │                          │
                           ▼                          ▼
             ┌─────────────────────────┐   ┌─────────────────────────┐
             │ Chroma Cloud Database   │   │ Answer + Page Citations │
             │ (Collection: document_  │   │ Returned to User        │
             │  knowledge)             │   │                         │
             └─────────────────────────┘   └─────────────────────────┘
```

---

## 🛠️ Tech Stack

- **Frontend**: React 18, Vite, Lucide Icons, Custom Pastel Workspace Theme
- **Backend**: Python 3.11+, FastAPI, Uvicorn, Pydantic
- **PDF Extraction**: PyMuPDF (`fitz`)
- **Chunking**: LangChain `RecursiveCharacterTextSplitter`
- **Embeddings & LLM**: Google Gemini (`gemini-embedding-001`, `gemini-flash-latest` / `gemini-2.5-flash`)
- **Vector Database**: Chroma Cloud (`chromadb.CloudClient`)
- **Deployment**: Vercel (Frontend & Backend as separate projects)

---

## 🔑 Environment Variables

### Backend (`backend/.env`)

| Variable | Description | Example |
| :--- | :--- | :--- |
| `GEMINI_API_KEY` | Google Gemini API Key | `AIzaSy...` |
| `CHROMA_API_KEY` | Chroma Cloud API Key | `ck-...` |
| `CHROMA_TENANT` | Chroma Cloud Tenant UUID | `18a9352d-...` |
| `CHROMA_DATABASE` | Chroma Cloud Database Name | `inquireai` |
| `FRONTEND_URL` | Deployed Frontend URL (for CORS) | `https://inquireai.vercel.app` |

### Frontend (`frontend/.env` / `frontend/.env.local`)

| Variable | Description | Example |
| :--- | :--- | :--- |
| `VITE_API_URL` | Backend FastAPI API Base URL | `https://inquireai-backend.vercel.app` |

---

## 💻 Local Development

### 1. Backend Setup

```bash
cd backend
python -m venv venv

# Windows
.\venv\Scripts\activate
# macOS / Linux
source venv/bin/activate

pip install -r requirements.txt
cp .env.example .env
# Fill in your GEMINI_API_KEY, CHROMA_API_KEY, CHROMA_TENANT, CHROMA_DATABASE

# Start the FastAPI server
uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload
```

Health check:
`GET http://127.0.0.1:8000/health` -> `{"status": "ok"}`

### 2. Frontend Setup

```bash
cd frontend
npm install
cp .env.example .env.local
# Set VITE_API_URL=http://localhost:8000 in .env.local

# Start the Vite dev server
npm run dev
```

The frontend will be available at `http://localhost:5173/`.

---

## 🚀 Deployment Guide (Separate Vercel Projects)

The frontend and backend are deployed as **two independent projects** on Vercel.

### 1. Deploy the Backend to Vercel

1. In your **Vercel Dashboard**, click **Add New Project**.
2. Import this GitHub repository.
3. Set **Root Directory** to `backend`.
4. Framework Preset: **Other** (Vercel automatically detects `vercel.json` with `@vercel/python`).
5. Add the Environment Variables:
   - `GEMINI_API_KEY`
   - `CHROMA_API_KEY`
   - `CHROMA_TENANT`
   - `CHROMA_DATABASE`
   - `FRONTEND_URL` (Set to your frontend's Vercel URL once deployed)
6. Click **Deploy**. Note the assigned backend URL (e.g., `https://inquireai-backend.vercel.app`).

### 2. Deploy the Frontend to Vercel

1. In your **Vercel Dashboard**, click **Add New Project**.
2. Import this GitHub repository.
3. Set **Root Directory** to `frontend`.
4. Framework Preset: **Vite**.
5. Build Command: `npm run build` (Output Directory: `dist`).
6. Add the Environment Variable:
   - `VITE_API_URL`: Your deployed FastAPI backend URL (e.g., `https://inquireai-backend.vercel.app`).
7. Click **Deploy**.
8. In the Backend Vercel project settings, make sure `FRONTEND_URL` matches your deployed frontend URL.

---

## 📡 API Endpoints

| Method | Endpoint | Description |
| :--- | :--- | :--- |
| `GET` | `/health` | API health check (`{"status": "ok"}`) |
| `GET` | `/` | API status & version |
| `GET` | `/documents` | List all indexed documents, chunk counts, and metadata |
| `POST` | `/query` | Grounded RAG search (`{"question": "...", "top_k": 5}`) |
| `POST` | `/upload` | Upload and index a PDF file (multipart form data) |
| `DELETE` | `/documents/{filename}` | Delete all chunks for a specific document |

---

## 📄 License

MIT License. Built for multi-document research and grounded intelligence.
