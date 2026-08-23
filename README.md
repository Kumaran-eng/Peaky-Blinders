# ABC College Chatbot

A trusted, document-grounded chatbot for ABC College. Students can ask questions about the shared college documents, while administrators securely manage the knowledge base.

The chatbot answers only when the uploaded documents contain sufficient evidence. If evidence is unavailable, it responds:

> I don't know based on the provided documents.

## Features

- Student chat interface with no sign-in required
- Password-protected admin dashboard
- Upload and index PDF, DOCX, and TXT documents
- PDF page-aware source citations
- Clickable source chips that open the cited document
- Strict evidence retrieval before the LLM is called
- Knowledge-gap tracking for unanswered questions
- Admin analytics, uploaded-document list, and recent-question history

## How it works

```text
Document upload
  -> text extraction
  -> chunking
  -> Sentence Transformer embeddings
  -> FAISS vector search index

Student question
  -> question embedding
  -> relevant evidence retrieval
  -> similarity check
  -> Groq LLM grounded answer
  -> answer with real document sources
```

## Tech stack

- Python and FastAPI
- SQLite and SQLAlchemy
- PyMuPDF for PDF extraction
- python-docx for DOCX extraction
- LangChain `RecursiveCharacterTextSplitter`
- Sentence Transformers (`all-MiniLM-L6-v2`)
- FAISS for semantic retrieval
- Groq for answer generation
- HTML, CSS, and vanilla JavaScript frontend

## Project structure

```text
backend/
  rag/          # extraction, chunking, embeddings, FAISS, prompts
  routes/       # chat, document, and admin APIs
  services/     # application business logic
frontend/       # student chat and password-protected admin UI
data/uploads/   # local uploaded documents (not committed)
vector_db/      # local FAISS files (not committed)
tests/          # backend and RAG tests
```

## Setup

1. Create and activate a virtual environment:

```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
```

2. Install dependencies:

```powershell
pip install -r requirements.txt
```

3. Create a `.env` file in the project root:

```env
GROQ_API_KEY=your_groq_api_key
GROQ_MODEL=openai/gpt-oss-20b

ADMIN_PASSWORD=choose_a_strong_private_password

EMBEDDING_MODEL=all-MiniLM-L6-v2
TOP_K=5
SIMILARITY_THRESHOLD=0.35

DATABASE_URL=sqlite:///./doctrust.db
UPLOAD_DIR=data/uploads
PROCESSED_DIR=data/processed
VECTOR_DB_DIR=vector_db
```

Never commit `.env`: it contains the Groq API key and admin password.

## Run the application

```powershell
.\venv\Scripts\python.exe -m uvicorn backend.main:app --reload --host 127.0.0.1 --port 8000
```

Open:

- Student landing page: `http://127.0.0.1:8000/`
- Student chat: `http://127.0.0.1:8000/chat`
- Admin dashboard: `http://127.0.0.1:8000/admin`
- API documentation: `http://127.0.0.1:8000/docs`

## Student and admin access

### Students

Students use `/chat` without a password. They can ask questions using the same shared knowledge base managed by the administrator.

### Administrator

The `/admin` dashboard requires `ADMIN_PASSWORD` from `.env`. The password is verified on the server; the browser receives only an HTTP-only session cookie.

Admin-only actions include:

- Uploading and indexing documents
- Viewing document records
- Viewing analytics and recent questions
- Viewing knowledge gaps
- Removing document records

## API endpoints

| Method | Endpoint | Purpose |
| --- | --- | --- |
| `POST` | `/api/chat/` | Ask a document-grounded question |
| `POST` | `/api/documents/upload` | Upload and index a PDF, DOCX, or TXT file (admin only) |
| `GET` | `/api/documents/view/{filename}` | Open a cited indexed document |
| `POST` | `/api/admin/login` | Start an admin session |
| `POST` | `/api/admin/logout` | End an admin session |
| `GET` | `/api/admin/documents` | List documents (admin only) |
| `GET` | `/api/admin/knowledge-gaps` | List unanswered questions (admin only) |
| `GET` | `/api/admin/analytics` | View dashboard counts (admin only) |

## Testing

Run the chat API tests:

```powershell
.\venv\Scripts\python.exe -m pytest tests\test_chat.py -v
```

Run the RAG tests:

```powershell
.\venv\Scripts\python.exe -m pytest tests\test_rag.py -v
```

## Security notes

- Do not put `GROQ_API_KEY` or `ADMIN_PASSWORD` in frontend files.
- `.env`, SQLite data, uploaded documents, and FAISS files are ignored by Git.
- For HTTPS deployment, set `ADMIN_COOKIE_SECURE=True` in `.env`.
- Deleting a document through the dashboard removes its database record. Vector-level deletion is not currently implemented, so rebuild the index when a full removal is required.
