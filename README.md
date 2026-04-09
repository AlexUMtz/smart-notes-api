# Smart Notes API

A production-ready REST API for intelligent note management with JWT authentication and AI-powered features. Built with FastAPI, PostgreSQL, and LangChain.

---

## Features

- **JWT Authentication** — secure registration and login with bcrypt password hashing
- **Notes CRUD** — create, read, update, and delete personal notes with ownership validation
- **AI Summarization** — summarize notes using OpenAI SDK or LangChain LCEL
- **AI Improvement** — improve note writing quality with LLM assistance
- **Token Control** — automatic input truncation and output limits via tiktoken
- **Layered Architecture** — Router → Service → Repository pattern with domain exceptions
- **Interactive Docs** — auto-generated Swagger UI at `/docs`

---

## Tech Stack

| Layer | Technology |
|---|---|
| Framework | FastAPI |
| Database | PostgreSQL + SQLAlchemy ORM |
| Auth | JWT (python-jose) + bcrypt (passlib) |
| AI — Direct | OpenAI SDK (gpt-4o-mini) |
| AI — Orchestration | LangChain LCEL |
| Token Counting | tiktoken |
| Validation | Pydantic v2 |
| Version Control | Git + GitHub |

---

## Architecture

```
app/
├── main.py                  # FastAPI app entry point
├── config.py                # Pydantic Settings — reads from .env
├── database.py              # SQLAlchemy engine and session
├── dependencies.py          # get_current_user — JWT verification
├── exceptions.py            # Domain exceptions (no FastAPI coupling)
├── models/
│   ├── user.py              # User ORM model
│   └── note.py              # Note ORM model with ForeignKey
├── schemas/
│   ├── user.py              # UserCreate, UserResponse
│   └── note.py              # NoteCreate, NoteUpdate, NoteResponse
├── repositories/
│   ├── user_repository.py   # UserRepository — DB access layer
│   └── note_repository.py   # NoteRepository — DB access layer
├── services/
│   ├── auth_service.py      # AuthService — register, login logic
│   ├── notes_service.py     # NotesService — CRUD + ownership validation
│   └── ai_service.py        # AIService — OpenAI SDK + LangChain LCEL
├── routers/
│   ├── auth.py              # POST /auth/register, /auth/login
│   ├── notes.py             # GET/POST/PUT/DELETE /notes
│   └── ai.py                # POST /ai/notes/{id}/summarize, /improve
└── utils/
    ├── security.py          # hash_password, verify_password, JWT utils
    └── token_counter.py     # count_tokens, truncate_to_token_limit
```

### Design decisions

**Services are framework-agnostic** — no FastAPI imports in service layer. Services raise domain exceptions (`NoteNotFoundError`, `NotOwnerError`) and routers convert them to `HTTPException`. This makes services independently testable without mocking HTTP.

**Repository pattern** — all database access is encapsulated in repositories. Services never write raw SQLAlchemy queries.

**Dual AI implementation** — each AI endpoint has two variants: one using the OpenAI SDK directly and one using LangChain LCEL chains. This demonstrates understanding of both approaches and the abstraction tradeoffs between them.

**Token control** — all LLM calls go through `token_counter.py` which truncates content exceeding `MAX_INPUT_TOKENS` before sending to the API, preventing unexpected costs.

---

## Endpoints

### Auth

| Method | Endpoint | Description | Auth |
|---|---|---|---|
| POST | `/auth/register` | Register a new user | No |
| POST | `/auth/login` | Login and receive JWT token | No |

### Notes

| Method | Endpoint | Description | Auth |
|---|---|---|---|
| GET | `/notes/` | List all notes for current user | Yes |
| GET | `/notes/{id}` | Get a specific note | Yes |
| POST | `/notes/` | Create a new note | Yes |
| PUT | `/notes/{id}` | Update a note (partial update supported) | Yes |
| DELETE | `/notes/{id}` | Delete a note | Yes |

### AI

| Method | Endpoint | Description | Auth |
|---|---|---|---|
| POST | `/ai/notes/{id}/summarize` | Summarize note — OpenAI SDK | Yes |
| POST | `/ai/notes/{id}/summarize-lc` | Summarize note — LangChain LCEL | Yes |
| POST | `/ai/notes/{id}/improve` | Improve note writing — OpenAI SDK | Yes |
| POST | `/ai/notes/{id}/improve-lc` | Improve note writing — LangChain LCEL | Yes |

> All `/notes` and `/ai` endpoints require `Authorization: Bearer <token>` header.
> Notes are scoped to the authenticated user — accessing another user's note returns `403 Forbidden`.

---

## Getting Started

### Prerequisites

- Python 3.10+
- PostgreSQL running locally

### Installation

```bash
# Clone the repository
git clone https://github.com/YOUR_USERNAME/smart-notes-api.git
cd smart-notes-api

# Create and activate virtual environment
python -m venv venv
venv\Scripts\activate  # Windows
# source venv/bin/activate  # macOS/Linux

# Install dependencies
pip install -r requirements.txt
```

### Environment Variables

Create a `.env` file in the project root based on `.env.example`:

```env
DATABASE_URL=postgresql://postgres:YOUR_PASSWORD@localhost:5432/smart_notes_db
SECRET_KEY=your-secret-key-here
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
OPENAI_API_KEY=sk-...
```

Generate a secure `SECRET_KEY`:

```bash
python -c "import secrets; print(secrets.token_hex(32))"
```

### Database Setup

Create the database in PostgreSQL:

```sql
CREATE DATABASE smart_notes_db;
```

Tables are created automatically on first run via SQLAlchemy `create_all`.

### Run

```bash
uvicorn app.main:app --reload
```

API available at `http://127.0.0.1:8000`
Interactive docs at `http://127.0.0.1:8000/docs`

---

## Usage Example

### 1. Register

```bash
curl -X POST http://localhost:8000/auth/register \
  -H "Content-Type: application/json" \
  -d '{"email": "user@example.com", "username": "user", "password": "password123"}'
```

### 2. Login

```bash
curl -X POST http://localhost:8000/auth/login \
  -d "username=user@example.com&password=password123"
```

### 3. Create a note

```bash
curl -X POST http://localhost:8000/notes/ \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"title": "My note", "content": "Content to summarize or improve."}'
```

### 4. Summarize with AI

```bash
curl -X POST http://localhost:8000/ai/notes/1/summarize \
  -H "Authorization: Bearer YOUR_TOKEN"
```

Response:

```json
{
  "note_id": 1,
  "title": "My note",
  "summary": "AI-generated summary of your note.",
  "tokens_used": {
    "input": 45,
    "output": 30,
    "total": 75
  },
  "engine": "openai-sdk"
}
```

---

## AI Implementation

Two parallel implementations are available for each AI endpoint:

**OpenAI SDK direct** (`/summarize`, `/improve`):

```python
response = openai_client.chat.completions.create(
    model="gpt-4o-mini",
    messages=[...],
    max_tokens=300
)
```

**LangChain LCEL** (`/summarize-lc`, `/improve-lc`):

```python
chain = ChatPromptTemplate.from_messages([...]) | llm | StrOutputParser()
result = chain.invoke({"content": note.content})
```

Both produce equivalent results. The LCEL version demonstrates how LangChain abstracts the prompt → LLM → parser pipeline, which becomes significantly more powerful in complex chains with retrievers, memory, or agents (RAG pipelines, AI agents).

### Save improved content

The `/improve` endpoint returns the improved text without saving it. To persist the result:

```
POST /ai/notes/{id}/improve  →  returns improved_content
PUT  /notes/{id}             →  save with {"content": improved_content}
```

This avoids making a second LLM call and ensures the user saves exactly what they reviewed.

---

## Error Handling

| Status | Meaning |
|---|---|
| `201 Created` | Resource created successfully |
| `204 No Content` | Resource deleted successfully |
| `400 Bad Request` | Validation error in request body |
| `401 Unauthorized` | Missing, invalid, or expired JWT token |
| `403 Forbidden` | Authenticated but not owner of resource |
| `404 Not Found` | Resource does not exist |
| `409 Conflict` | Email or username already registered |
| `422 Unprocessable` | Request body failed Pydantic validation |

---

## Commit History

```
feat: add AI summarize and improve endpoints with OpenAI SDK and LangChain LCEL
feat: add notes CRUD with ownership validation
feat: implement JWT authentication
feat: database models and configuration
```

---

## License

MIT
