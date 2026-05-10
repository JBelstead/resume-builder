# Research: AI Resume Builder

**Feature**: 001-ai-resume-builder
**Date**: 2026-05-10

## Decision Log

### 1. LLM Integration — Ollama API

**Decision**: Interface with Llama 3.3 through the Ollama REST API (`POST /api/generate`
or `POST /api/chat`), running as a Docker container on `localhost:11434`.

**Rationale**: Ollama exposes a simple HTTP API that requires no Python SDK; it keeps the
backend dependency footprint minimal (just `httpx` for async HTTP). The `/api/chat`
endpoint with a system prompt is preferred over `/api/generate` because it supports
structured conversation and is easier to control response format.

**Alternatives considered**:
- llama-cpp-python: Would require loading the model in-process, consuming significant
  RAM and coupling model lifecycle to the Python process. Rejected in favour of
  Ollama's container isolation.
- LangChain: Adds substantial abstraction overhead for a single-model, single-prompt
  use case. Rejected as unnecessary complexity.

---

### 2. Job URL Parsing

**Decision**: Use `httpx` (async) to fetch the URL content and `BeautifulSoup4` with the
`html.parser` backend to extract visible text from `<body>`, stripping `<script>`,
`<style>`, and `<nav>` tags.

**Rationale**: Most public job boards render their content server-side; a simple HTTP GET
is sufficient. `BeautifulSoup4` is already a common FastAPI ecosystem dependency.
No headless browser is needed for the scope of this application.

**Alternatives considered**:
- Playwright/Selenium: Required for JavaScript-rendered pages (e.g., Workday, Greenhouse
  SPA variants). Adds significant complexity and a browser binary dependency. Deferred
  to a future enhancement if users report failures on specific boards.
- `newspaper3k`: Good for news articles but not optimized for job posting HTML structure.

**Known limitation**: JavaScript-only job boards (fully client-rendered) will return
empty or skeleton content. The UI will surface a clear error and prompt the user to
paste the text manually.

---

### 3. Resume PDF Generation

**Decision**: Use Jinja2 to render the resume as an HTML file, then convert to PDF with
WeasyPrint.

**Rationale**: WeasyPrint produces high-quality, CSS-driven PDFs and is a pure-Python
dependency. The 1-column layout specified is straightforward CSS. The rendered HTML
file is also saved alongside the PDF so users can view it in a browser.

**Alternatives considered**:
- ReportLab: Programmatic PDF construction is verbose and makes template maintenance
  difficult. Rejected for this layout-heavy use case.
- wkhtmltopdf: Requires a native binary and has been abandoned upstream. Rejected.
- Puppeteer/headless Chrome: Excellent quality but adds a Node.js/browser runtime
  dependency to the Python backend. Rejected.

---

### 4. ORM and Database Access

**Decision**: SQLAlchemy 2 (async engine with `aiosqlite`) with declarative models.
Alembic for schema migrations.

**Rationale**: SQLAlchemy 2's async support integrates cleanly with FastAPI's async
handlers. Alembic provides forward-compatible migrations if the schema evolves.
Using SQLite keeps the stack fully local with zero configuration.

**Alternatives considered**:
- Raw `sqlite3` module: No ORM means duplicated query logic and no migration support.
- Tortoise ORM: Less mature ecosystem; SQLAlchemy is the standard for FastAPI.

---

### 5. LLM Prompt Design

**Decision**: Use a structured system prompt that instructs Llama 3.3 to return a JSON
object with keys matching the resume sections: `summary`, `experience_highlights`
(list), `skills_to_emphasize` (list). The backend then maps these into the Jinja2
template.

**Rationale**: Returning structured JSON from the LLM avoids fragile text parsing.
Llama 3.3 (70B) reliably follows JSON format instructions when prompted explicitly.
The prompt includes the full profile data and the job description as context.

**Prompt structure**:
```
System: You are a professional resume writer. Given a candidate's profile and a job
description, extract and tailor the most relevant content. Respond ONLY with valid
JSON matching this schema: { "summary": "...", "experience_highlights": [...],
"skills_to_emphasize": [...] }

User: --- PROFILE ---
{profile_json}

--- JOB DESCRIPTION ---
{job_description}
```

---

### 6. Frontend State Management

**Decision**: Pinia stores for profile data and resume generation state. No server-side
rendering; Vue Router in hash mode to avoid requiring a server for the SPA.

**Rationale**: Pinia is the official Vue 3 state management solution. Two stores
(`profile` and `resume`) map cleanly to the two application pages. Hash-mode routing
ensures the SPA works when served directly from `localhost` without a proxy.

---

### 7. CORS Configuration

**Decision**: FastAPI backend configured with CORS middleware allowing `http://localhost:5173`
(Vite dev server) and `http://localhost:4173` (Vite preview). In production-like
local usage, both frontend and backend are served from localhost so no CORS issues arise.

---

### 8. Docker Compose Topology

**Decision**: Three services in `docker-compose.yml`:
1. `ollama` — Official Ollama image, exposes port 11434, with a volume for model storage.
2. `backend` — Python FastAPI app, built from `backend/`, exposes port 8000.
3. `frontend` — Node.js Vite dev server, built from `frontend/`, exposes port 5173.

An `ollama-init` one-shot service runs `ollama pull llama3.3` on first startup to
download the model automatically.

**Alternatives considered**:
- Running backend and frontend natively (no Docker for those services): Valid for
  development but Docker Compose gives a single `docker compose up` experience.
  Both approaches will be documented in quickstart.md.
