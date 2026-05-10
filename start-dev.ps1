#Requires -Version 5.1
<#
.SYNOPSIS
    Starts all Resume Builder services for local development.

.DESCRIPTION
    1. Starts Ollama in Docker (with Llama 3.3 model)
    2. Activates the Python venv and starts the FastAPI backend
    3. Installs frontend deps if needed and starts the Vite dev server
    4. Opens the browser when the backend is ready

.NOTES
    Run once: Set-ExecutionPolicy -Scope CurrentUser RemoteSigned
#>

param (
    [switch]$SkipBrowser   # Pass -SkipBrowser to suppress auto-open
)

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

$Root    = $PSScriptRoot
$Backend = Join-Path $Root 'backend'
$Frontend = Join-Path $Root 'frontend'
$Venv    = Join-Path $Backend '.venv'
$EnvFile = Join-Path $Root '.env'

# ─── Helpers ──────────────────────────────────────────────────────────────────

function Write-Step([string]$Msg) {
    Write-Host "`n==> $Msg" -ForegroundColor Cyan
}

function Write-Ok([string]$Msg) {
    Write-Host "    [ok] $Msg" -ForegroundColor Green
}

function Write-Warn([string]$Msg) {
    Write-Host "    [!]  $Msg" -ForegroundColor Yellow
}

function Assert-Command([string]$Name) {
    if (-not (Get-Command $Name -ErrorAction SilentlyContinue)) {
        Write-Host "`n[ERROR] '$Name' not found in PATH. Please install it and retry." -ForegroundColor Red
        exit 1
    }
}

# ─── Prerequisites ─────────────────────────────────────────────────────────────

Write-Step 'Checking prerequisites'
Assert-Command 'docker'
Assert-Command 'python'
Assert-Command 'node'
Assert-Command 'npm'
Write-Ok 'docker, python, node, npm all found'

# ─── .env file ─────────────────────────────────────────────────────────────────

if (-not (Test-Path $EnvFile)) {
    Write-Step 'Creating .env from .env.example'
    Copy-Item (Join-Path $Root '.env.example') $EnvFile
    Write-Ok '.env created (using defaults)'
} else {
    Write-Ok '.env already exists'
}

# ─── Python venv ───────────────────────────────────────────────────────────────

Write-Step 'Setting up Python virtual environment'

if (-not (Test-Path $Venv)) {
    Write-Warn 'No .venv found — creating one now (this takes a moment)...'
    & python -m venv $Venv
    Write-Ok "Virtual environment created at $Venv"
}

$Pip     = Join-Path $Venv 'Scripts\pip.exe'
$Uvicorn = Join-Path $Venv 'Scripts\uvicorn.exe'

if (-not (Test-Path $Uvicorn)) {
    Write-Warn 'Installing backend dependencies...'
    & $Pip install -r (Join-Path $Backend 'requirements.txt') --quiet
    Write-Ok 'Backend dependencies installed'
} else {
    Write-Ok 'Backend dependencies already installed'
}

# ─── Frontend deps ─────────────────────────────────────────────────────────────

Write-Step 'Checking frontend dependencies'
$NodeModules = Join-Path $Frontend 'node_modules'

if (-not (Test-Path $NodeModules)) {
    Write-Warn 'node_modules not found — running npm install...'
    Push-Location $Frontend
    & npm install --silent
    Pop-Location
    Write-Ok 'Frontend dependencies installed'
} else {
    Write-Ok 'node_modules already present'
}

# ─── Start Ollama ──────────────────────────────────────────────────────────────

Write-Step 'Starting Ollama (Docker)'

$OllamaRunning = docker ps --filter 'name=resume-builder-ollama' --format '{{.Names}}' 2>$null
if ($OllamaRunning) {
    Write-Ok 'Ollama container already running'
} else {
    Write-Host '    Starting ollama container (model download may take several minutes on first run)...' -ForegroundColor Gray
    docker compose -f (Join-Path $Root 'docker-compose.yml') up -d ollama
    Write-Ok 'Ollama container started'
}

# Wait for Ollama to be healthy
Write-Host '    Waiting for Ollama to be ready...' -ForegroundColor Gray
$Tries = 0
$MaxTries = 60
do {
    Start-Sleep -Seconds 2
    $Tries++
    try {
        $null = Invoke-WebRequest -Uri 'http://localhost:11434/api/tags' -UseBasicParsing -TimeoutSec 2 -ErrorAction Stop
        $OllamaReady = $true
    } catch {
        $OllamaReady = $false
    }
} while (-not $OllamaReady -and $Tries -lt $MaxTries)

if (-not $OllamaReady) {
    Write-Warn 'Ollama did not become ready in time. The backend will show "LLM unavailable" until it does.'
} else {
    Write-Ok 'Ollama is ready'
}

# ─── Start Backend ─────────────────────────────────────────────────────────────

Write-Step 'Starting FastAPI backend (port 8000)'

$BackendCmd = "Set-Location '$Backend'; & '$Uvicorn' app.main:app --reload --port 8000"
Start-Process powershell -ArgumentList "-NoExit", "-Command", $BackendCmd -WindowStyle Normal
Write-Ok 'Backend started in a new window'

# Wait until the backend is accepting connections
Write-Host '    Waiting for backend to be ready...' -ForegroundColor Gray
$Tries = 0
$MaxTries = 30
do {
    Start-Sleep -Seconds 1
    $Tries++
    try {
        $null = Invoke-WebRequest -Uri 'http://localhost:8000/api/health' -UseBasicParsing -TimeoutSec 1 -ErrorAction Stop
        $BackendReady = $true
    } catch {
        $BackendReady = $false
    }
} while (-not $BackendReady -and $Tries -lt $MaxTries)

if ($BackendReady) {
    Write-Ok 'Backend is ready at http://localhost:8000'
} else {
    Write-Warn 'Backend did not respond in time — it may still be starting. Check the backend window.'
}

# ─── Start Frontend ────────────────────────────────────────────────────────────

Write-Step 'Starting Vite dev server (port 5173)'

$FrontendCmd = "Set-Location '$Frontend'; npm run dev"
Start-Process powershell -ArgumentList "-NoExit", "-Command", $FrontendCmd -WindowStyle Normal
Write-Ok 'Frontend started in a new window'

# ─── Open browser ──────────────────────────────────────────────────────────────

if (-not $SkipBrowser) {
    Start-Sleep -Seconds 2
    Write-Step 'Opening browser'
    Start-Process 'http://localhost:5173'
    Write-Ok 'Opened http://localhost:5173'
}

# ─── Summary ───────────────────────────────────────────────────────────────────

Write-Host ''
Write-Host '─────────────────────────────────────────────' -ForegroundColor DarkGray
Write-Host '  Resume Builder is running' -ForegroundColor Green
Write-Host ''
Write-Host '  App       : http://localhost:5173'
Write-Host '  API docs  : http://localhost:8000/docs'
Write-Host '  Ollama    : http://localhost:11434'
Write-Host ''
Write-Host '  To stop:' -ForegroundColor Yellow
Write-Host '    Close the backend and frontend windows'
Write-Host '    docker compose stop ollama'
Write-Host '─────────────────────────────────────────────' -ForegroundColor DarkGray
