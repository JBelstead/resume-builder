# Quickstart: AI Resume Builder

**Branch**: `001-ai-resume-builder`
**Date**: 2026-05-10

## Prerequisites

| Tool | Minimum version | Purpose |
|------|----------------|---------|
| Docker + Docker Compose | 24.x / 2.x | Runs Ollama (Llama 3.3) |
| Python | 3.11+ | Backend runtime |
| Node.js | 20 LTS+ | Frontend build toolchain |
| ~3 GB free disk | — | Llama 3.2:3b model weights |

> **Note**: The Llama 3.2:3b model download (~2 GB) happens automatically on first
> `docker compose up`. Subsequent starts are instant.

---

## Option A: Full Docker Compose (recommended)

Everything runs inside Docker — no local Python or Node.js install needed beyond
Docker itself.

```bash
# 1. Clone and enter the project
git clone <repo-url> resume-builder
cd resume-builder

# 2. Copy environment config (edit if needed — defaults work out of the box)
cp .env.example .env

# 3. Start all services (first run downloads the Llama 3.3 model — be patient)
docker compose up

# 4. Open the application
#    Frontend: http://localhost:5173
#    Backend API docs: http://localhost:8000/docs
```

To stop: `Ctrl+C` then `docker compose down`.

---

## Option B: Native development (faster iteration)

Run Ollama in Docker, backend and frontend natively.

### Step 1 — Start Ollama

```bash
docker compose up ollama
# Wait until you see: "Listening on 0.0.0.0:11434"
```

### Step 2 — Backend

```bash
cd backend

# Create and activate a virtual environment
python -m venv .venv
source .venv/bin/activate        # macOS/Linux
# .venv\Scripts\activate         # Windows PowerShell

# Install dependencies
pip install -r requirements.txt

# Copy environment config
cp .env.example .env

# Run database migrations (creates SQLite database on first run)
alembic upgrade head

# Start the API server
uvicorn app.main:app --reload --port 8000
```

API is now at `http://localhost:8000`. Interactive docs at `http://localhost:8000/docs`.

### Step 3 — Frontend

In a separate terminal:

```bash
cd frontend

# Install dependencies
npm install

# Start the Vite dev server
npm run dev
```

Frontend is now at `http://localhost:5173`.

---

## Verifying Everything Works

1. Open `http://localhost:5173` in your browser.
2. Navigate to the **Profile** page and fill in your name and at least one work
   experience entry. Click **Save**.
3. Navigate to the **Generate Resume** page.
4. Paste a job description into the text field and click **Generate**.
5. Wait up to 30 seconds. The generated resume should appear and a PDF download link
   should be shown.

---

## Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `OLLAMA_BASE_URL` | `http://localhost:11434` | Ollama API base URL |
| `OLLAMA_MODEL` | `llama3.2:3b` | Model name to use for generation |
| `DATABASE_URL` | `sqlite+aiosqlite:///./resume_builder.db` | SQLite connection string |
| `RESUME_OUTPUT_DIR` | `./resumes` | Directory for generated resume files |
| `CORS_ORIGINS` | `http://localhost:5173,http://localhost:4173` | Allowed frontend origins |

---

## Running Tests

```bash
# Backend tests
cd backend
pip install -r requirements-dev.txt
pytest tests/ -v

# Frontend tests
cd frontend
npm run test
```

---

## Troubleshooting

**"LLM service unreachable" error**
Ensure the Ollama container is running: `docker compose ps`. If not, run
`docker compose up ollama`.

**PDF download is empty or fails**
WeasyPrint requires system fonts. If running natively, install the font packages
for your OS (e.g., `apt install fonts-liberation` on Debian/Ubuntu).

**Job URL returns no content**
The job board may use JavaScript rendering. Paste the job description text manually
instead.

**Model not found (Ollama)**
Run `docker compose exec ollama ollama pull llama3.2:3b` to manually trigger the download.
