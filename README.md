# InquireAI

**inquireAI** is a multi-document AI knowledge assistant that uses **Retrieval-Augmented Generation (RAG)** to answer questions based on information contained in uploaded documents.

Instead of relying entirely on an LLM's pretrained knowledge, inquireAI retrieves relevant information from the user's documents and provides it as context to the language model before generating an answer. This helps keep responses grounded in the available knowledge base and reduces unsupported or hallucinated answers.

---

## ✨ Features

* 📄 **Multi-document support** — Upload and work with multiple PDF documents.
* 🔍 **Semantic search** — Find relevant document sections based on meaning rather than exact keyword matching.
* 🧠 **RAG-powered answers** — Retrieved document context is provided to the LLM before generating responses.
* 📚 **Source citations** — Answers include the source document and page numbers used for retrieval.
* 🛡️ **Grounded responses** — The system is instructed not to invent information that is not supported by the uploaded documents.
* 🚫 **Out-of-context detection** — When relevant information cannot be found in the knowledge base, inquireAI can indicate that the information is unavailable rather than relying on unsupported knowledge.
* 💬 **Interactive chat** — Ask follow-up questions within the knowledge base.
* 🗂️ **Document management** — View indexed documents and remove documents from the knowledge base.
* ⚡ **Fast semantic retrieval** — Uses vector similarity search to efficiently find relevant chunks.

---

## 🧠 How inquireAI Works

inquireAI follows a two-stage RAG architecture: **indexing** and **querying**.

### 1. Document Indexing

When a PDF is uploaded:

```text
PDF Document
     ↓
Text Extraction
     ↓
Page-aware Text
     ↓
Text Chunking
     ↓
Gemini Embeddings
     ↓
ChromaDB
```

The document is first processed using **PyMuPDF** to extract its text while preserving page information.

The extracted content is then divided into smaller overlapping chunks using LangChain's `RecursiveCharacterTextSplitter`.

Each chunk is converted into a numerical vector representation using Google's Gemini embedding model and stored in **ChromaDB** along with metadata such as:

* Source filename
* Page number
* Chunk ID

---

### 2. Question Answering

When a user asks a question:

```text
User Question
      ↓
Query Embedding
      ↓
ChromaDB Similarity Search
      ↓
Top-K Relevant Chunks
      ↓
Context Construction
      ↓
Gemini LLM
      ↓
Grounded Answer
      ↓
Source Citations
```

The question is converted into an embedding using the same embedding model used during document indexing.

ChromaDB performs a similarity search to identify the most relevant document chunks.

These retrieved chunks are then provided to the Gemini language model as context.

The model generates an answer based primarily on the retrieved information and returns the associated document sources.

---

## 🏗️ System Architecture

```text
                         ┌─────────────────────┐
                         │    User / Browser   │
                         └──────────┬──────────┘
                                    │
                                    ▼
                         ┌─────────────────────┐
                         │    React Frontend   │
                         └──────────┬──────────┘
                                    │
                              HTTP Requests
                                    │
                                    ▼
                         ┌─────────────────────┐
                         │   FastAPI Backend   │
                         └──────────┬──────────┘
                                    │
                         ┌──────────┴──────────┐
                         │                     │
                         ▼                     ▼
                ┌─────────────────┐   ┌─────────────────┐
                │ Document        │   │ RAG Pipeline    │
                │ Ingestion       │   │                 │
                └────────┬────────┘   └────────┬────────┘
                         │                     │
                         ▼                     ▼
                ┌─────────────────┐   ┌─────────────────┐
                │ PyMuPDF         │   │ Semantic        │
                │ Extraction      │   │ Retriever       │
                └────────┬────────┘   └────────┬────────┘
                         │                     │
                         ▼                     ▼
                ┌─────────────────┐   ┌─────────────────┐
                │ LangChain       │   │ ChromaDB        │
                │ Chunking        │   │ Vector Search   │
                └────────┬────────┘   └────────┬────────┘
                         │                     │
                         ▼                     ▼
                ┌─────────────────┐   ┌─────────────────┐
                │ Gemini          │   │ Retrieved       │
                │ Embeddings      │   │ Context         │
                └────────┬────────┘   └────────┬────────┘
                         │                     │
                         └──────────┬──────────┘
                                    ▼
                         ┌─────────────────────┐
                         │     Gemini LLM      │
                         └──────────┬──────────┘
                                    │
                                    ▼
                         ┌─────────────────────┐
                         │ Grounded Answer +   │
                         │ Source Citations    │
                         └─────────────────────┘
```

---

## 🛠️ Tech Stack

### Frontend

* **React**
* **Vite**
* **JavaScript**
* **CSS**

The frontend provides the document management interface, upload workflow, conversational interface, loading/error states, and source display.

### Backend

* **Python**
* **FastAPI**
* **Uvicorn**

FastAPI provides the API layer connecting the frontend with the RAG pipeline.

### Document Processing

* **PyMuPDF**

Used for extracting text from PDF documents while preserving page-level information for source citations.

### RAG / AI

* **LangChain**
* **Google Gemini**
* **Gemini Embeddings**
* **Gemini LLM**

LangChain is used for document chunking and orchestration of the retrieval/generation workflow.

### Vector Database

* **ChromaDB**

Used to store document embeddings and perform semantic similarity search.

---

## 📂 Project Structure

```text
inquireAI/
│
├── backend/
│   ├── app/
│   │   ├── document_processor.py
│   │   ├── chunker.py
│   │   ├── embeddings.py
│   │   ├── vector_store.py
│   │   ├── retriever.py
│   │   ├── generator.py
│   │   ├── rag_pipeline.py
│   │   ├── ingestion.py
│   │   └── main.py
│   │
│   ├── test_document_processor.py
│   ├── test_chunker.py
│   ├── test_embeddings.py
│   ├── test_vector_store.py
│   ├── test_retriever.py
│   ├── test_generator.py
│   └── test_rag_pipeline.py
│
├── frontend/
│   └── ...
│
├── data/
│   └── sample_documents/
│
├── evaluation/
│   └── ...
│
├── screenshots/
│   └── ...
│
├── .gitignore
├── README.md
└── requirements.txt
```

---

## 🔄 RAG Pipeline Components

### Document Processor

Responsible for extracting text from uploaded PDFs.

It preserves page-level metadata so that retrieved information can later be traced back to its original page.

### Chunker

Splits extracted text into smaller overlapping chunks.

Current configuration:

```text
Chunk size: 1000 characters
Chunk overlap: 150 characters
```

The overlap helps preserve contextual continuity between neighboring chunks.

### Embedding Model

Each document chunk is converted into a vector representation using:

```text
gemini-embedding-001
```

The same embedding approach is used to convert user questions into vectors during retrieval.

### Vector Store

ChromaDB stores:

```text
Document chunk
Embedding
Source filename
Page number
Chunk ID
```

This allows the system to perform semantic similarity searches.

### Retriever

The retriever:

1. Receives the user's question.
2. Creates an embedding for the question.
3. Searches ChromaDB.
4. Retrieves the top-k relevant chunks.
5. Returns the chunks and their metadata.

### Generator

The generator receives:

```text
User Question
+
Retrieved Context
```

and sends them to the Gemini LLM with grounding instructions.

The model is instructed to avoid inventing information that cannot be supported by the retrieved context.

### RAG Pipeline

The RAG pipeline orchestrates the complete query workflow:

```text
Question
   ↓
Retriever
   ↓
Relevant Chunks
   ↓
Generator
   ↓
Answer + Sources
```

This separation keeps retrieval and generation modular and easier to test independently.

---

## 🔐 Grounding & Hallucination Handling

A key design goal of inquireAI is to keep responses grounded in the user's uploaded knowledge base.

The generator is instructed to:

* use the retrieved document context as the primary source of information;
* avoid inventing unsupported facts;
* avoid relying on external knowledge when the retrieved context is insufficient;
* explicitly indicate when the requested information cannot be found in the uploaded documents.

For example, if the uploaded document contains information about DBMS fundamentals but does not discuss normalization, a question such as:

```text
Explain normalization in DBMS.
```

should result in an indication that sufficient information was not found in the uploaded knowledge base.

This behavior is important because a RAG application should not simply produce an answer whenever an LLM knows one. It should distinguish between **what the knowledge base contains** and **what the model may know independently**.

---

## 📖 Source Citations

Retrieved document chunks retain their original metadata.

Each generated answer can therefore be associated with sources such as:

```text
DBMS.pdf — Page 1
DBMS.pdf — Page 2
```

This provides traceability between the generated response and the underlying knowledge source.

---

## 🧪 Evaluation

The system was tested at multiple stages rather than evaluating only the final chatbot.

### Document Processing

Verified that:

* PDFs can be read successfully.
* Text is extracted correctly.
* Page numbers are preserved.

### Chunking

Verified that:

* documents are divided into manageable chunks;
* chunk overlap is maintained;
* metadata and deterministic chunk IDs are preserved.

### Embeddings

Verified that:

* document chunks can be converted into embeddings;
* query embeddings can be generated successfully.

### Vector Storage

Verified that:

* embeddings are stored in ChromaDB;
* metadata is preserved;
* vectors can be retrieved through similarity search.

### Retrieval

Tested queries such as:

```text
What are the problems with traditional approach for storing data?
```

and verified that relevant sections of the DBMS document were retrieved.

### Grounding

The system was also tested with questions outside the uploaded document's knowledge scope.

The expected behavior is to acknowledge insufficient information rather than generate an unsupported answer.

---


## 🔑 Environment Variables

The application uses environment variables for API credentials.

Example:

```env
GEMINI_API_KEY=your_gemini_api_key
```

API keys should never be committed to the repository.

The `.env` file is excluded through `.gitignore`.

---

## 📡 API Overview

The backend exposes endpoints for:

| Method | Endpoint                | Description                               |
| ------ | ----------------------- | ----------------------------------------- |
| GET    | `/`                     | API health check                          |
| POST   | `/query`                | Ask a question against the knowledge base |
| POST   | `/upload`               | Upload and index a PDF                    |
| GET    | `/documents`            | List indexed documents                    |
| DELETE | `/documents/{filename}` | Remove a document from the knowledge base |

---

## 💡 Example Workflow

### Upload

Upload:

```text
DBMS.pdf
```

The document is processed and indexed.

### Ask

```text
What are the problems with the traditional approach for storing data?
```

### Retrieve

The system searches the vector database for relevant document chunks.

### Generate

Gemini receives the retrieved context and generates a grounded response.

### Cite

The response includes sources such as:

```text
DBMS.pdf — Page 1
DBMS.pdf — Page 2
```

---

## 🎯 Design Goals

inquireAI was designed around four principles:

### 1. Grounded

Answers should be based on the user's documents.

### 2. Traceable

Users should be able to identify where information came from.

### 3. Modular

Document processing, embeddings, retrieval, generation, and orchestration are separated into independent components.

### 4. Usable

The technical RAG pipeline is presented through a simple, visually engaging knowledge workspace rather than exposing unnecessary implementation complexity to the user.

---

## ⚠️ Current Limitations

* PDF is currently the primary supported document format.
* Retrieval quality depends on document structure and chunking.
* Scanned/image-only PDFs may require additional OCR processing.
* The system's responses depend on the quality and completeness of the uploaded documents.
* Local ChromaDB storage is primarily intended for the MVP/development environment.
* Large document collections may require additional optimization for production workloads.

---

## 🔮 Future Improvements

Potential improvements include:

* 🔎 Improved retrieval using hybrid search and reranking.
* 📊 Automated retrieval and answer evaluation.
* 🧠 Improved query rewriting for complex questions.
* 💬 Persistent conversation history.
* 👥 User accounts and private knowledge bases.
* ☁️ Scalable cloud vector storage.
* 📄 Better handling of scanned PDFs and OCR.
* 🔗 More detailed source-level citations.
* ⚡ Streaming responses.
* 📈 Analytics for retrieval quality and document usage.
