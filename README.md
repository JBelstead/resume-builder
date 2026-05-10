# Resume Builder

A local AI-powered resume builder. Fill in your profile once, then paste a job
description (or a job posting URL) and get a tailored PDF resume in under 30 seconds —
all running on your machine, no data sent to any cloud service.

## How it works

1. **Profile page** — enter your personal info, education, certifications, and work history.
2. **Generate page** — paste a job description or provide a URL.
3. The app feeds your profile and the job description to a locally-running **Llama 3.3**
   model (via Ollama) and gets back a tailored summary, highlighted skills, and key achievements.
4. A one-page PDF resume is generated and available for download.
5. All past resumes are saved and accessible from the Generate page.

---

## Prerequisites

| Tool | Minimum version | Notes |
|------|----------------|-------|
| [Docker Desktop](https://www.docker.com/products/docker-desktop/) | 24.x | Runs Ollama + the app |
| [Python](https://www.python.org/downloads/) | 3.11+ | Only needed for native dev mode |
| [Node.js](https://nodejs.org/) | 20 LTS | Only needed for native dev mode |
| Free disk space | ~8 GB | For the Llama 3.3 model weights |

> The Llama 3.3 model (~6 GB) is downloaded automatically on first start.
> Subsequent starts are instant.

---

## Quick start — Docker (recommended)

The easiest way. Everything runs in containers; no local Python or Node.js needed.

```powershell
# 1. Copy environment config (defaults work out of the box)
cp .env.example .env

# 2. Start all services  (first run: model download takes several minutes)
docker compose up

# 3. Open the app
start http://localhost:5173
```

To stop: `Ctrl+C`, then `docker compose down`.

**Or use the startup script** (see [Startup script](#startup-script) below).

---

## Native dev mode (faster iteration)

Run Ollama in Docker, backend and frontend directly on your machine.

### 1. Ollama

```powershell
docker compose up ollama
# wait until you see "Listening on 0.0.0.0:11434"
```

### 2. Backend

```powershell
cd backend

# Create virtual environment
python -m venv .venv
.venv\Scripts\Activate.ps1          # PowerShell
# source .venv/bin/activate         # bash/zsh

# Install dependencies
pip install -r requirements.txt

# Copy env file (only needed once)
cp .env.example .env

# Start the API server  (migrations run automatically on startup)
uvicorn app.main:app --reload --port 8000
```

API docs: `http://localhost:8000/docs`

### 3. Frontend

Open a second terminal:

```powershell
cd frontend
npm install
npm run dev
```

App: `http://localhost:5173`

---

## Startup script

`start-dev.ps1` (in the project root) automates the native dev setup.
It starts Ollama, the backend, and the frontend in separate windows and
opens the browser when the backend is ready.

```powershell
# First time only — allow local scripts to run
Set-ExecutionPolicy -Scope CurrentUser RemoteSigned

# Run the startup script
.\start-dev.ps1
```

To stop everything: close the terminal windows that were opened, then run:

```powershell
docker compose stop ollama
```

---

## Using the app

1. Open `http://localhost:5173`.
2. Go to **Profile** → fill in your name and at least one work experience entry → **Save Profile**.
3. Go to **Generate Resume** → paste a job description or enter a job posting URL → **Generate Resume**.
4. Wait up to 30 seconds. A success panel appears with a **Download PDF** button.
5. Past resumes appear in the history table below — you can download or delete them.

---

## Environment variables

All variables live in `.env` at the project root (copy from `.env.example`).

| Variable | Default | Description |
|----------|---------|-------------|
| `OLLAMA_BASE_URL` | `http://localhost:11434` | Ollama API URL (don't change for Docker) |
| `OLLAMA_MODEL` | `llama3.3` | Model to use — must be pulled in Ollama |
| `DATABASE_URL` | `sqlite+aiosqlite:///./resume_builder.db` | SQLite path (relative to `backend/`) |
| `RESUME_OUTPUT_DIR` | `./resumes` | Where generated PDFs are stored |
| `CORS_ORIGINS` | `http://localhost:5173,...` | Allowed frontend origins |

---

## Running tests

```powershell
# Backend  (requires virtual environment activated)
cd backend
pip install -r requirements-dev.txt
pytest tests/ -v --cov=app

# Frontend
cd frontend
npm install
npm run test:unit
```

---

## Troubleshooting

**"LLM service unreachable"**
Ollama isn't running. Run `docker compose up ollama` and wait for it to be healthy.

**"Complete your profile" error on Generate page**
You need at least a name saved on the Profile page before generating.

**PDF download fails or is blank**
On native mode, WeasyPrint needs system font libraries. On Debian/Ubuntu:
`sudo apt install fonts-liberation libpango-1.0-0`. On Windows, fonts are
bundled with the Docker image — use Docker mode if you hit this.

**Job URL returns no text**
Some job boards use JavaScript rendering that can't be fetched server-side.
Paste the job description text directly instead.

**Ollama model not found**
Trigger a manual pull:
```powershell
docker compose exec ollama ollama pull llama3.3
```
