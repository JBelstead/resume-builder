# Implementation Plan: AI Resume Builder

**Branch**: `001-ai-resume-builder` | **Date**: 2026-05-10 | **Spec**: [spec.md](spec.md)
**Input**: Feature specification from `/specs/001-ai-resume-builder/spec.md`

**Note**: This plan is filled in by the `/speckit-plan` command.

## Summary

A single-user, fully local web application that stores professional profile data and
uses a locally-hosted Llama 3.3 LLM to generate tailored resumes from submitted job
descriptions. The backend is a FastAPI (Python) REST API persisting to SQLite; the
frontend is a two-page Vue 3 SPA. No data leaves the user's machine.

## Technical Context

**Language/Version**: Python 3.11 (backend), JavaScript/ES2022 + Vue 3 (frontend)
**Primary Dependencies**: FastAPI, SQLAlchemy 2, Uvicorn, Pydantic v2, BeautifulSoup4
(job URL parsing), Jinja2 (resume HTML template), WeasyPrint (PDF generation);
Vue 3, Vite, Vue Router 4, Pinia, Axios
**Storage**: SQLite via SQLAlchemy (profile data); local filesystem directory (resume files)
**Testing**: pytest + httpx (backend); Vitest + Vue Test Utils (frontend)
**Target Platform**: Localhost desktop browser (no deployment)
**Project Type**: Web application — Python FastAPI backend + Vue 3 SPA frontend
**Performance Goals**: Resume generation ≤30s (LLM-bound); page LCP ≤2.5s; PDF export ≤3s
**Constraints**: No external network calls for data; all storage local; Docker required
for Llama 3.3 via Ollama; single-user, no auth
**Scale/Scope**: Single user, single machine; no concurrency requirements beyond one
simultaneous LLM request

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-checked after Phase 1 design.*

| Principle | Gate | Status | Notes |
|-----------|------|--------|-------|
| I. Code Quality | Typed APIs (Pydantic schemas), functions ≤40 lines, no dead code | ✅ PASS | Enforced via Pydantic v2 + type annotations throughout |
| II. Testing Standards | TDD, ≥80% unit coverage on business logic, independent tests | ✅ PASS | pytest for backend services; Vitest for Vue components |
| III. UX Consistency | WCAG 2.1 AA, 100ms feedback, design system tokens | ✅ PASS | Loading states required for LLM generation; 2-page layout is simple and consistent |
| IV. Performance | LCP ≤2.5s, TTI ≤4s, bundle ≤250KB gzip, PDF export ≤3s | ✅ PASS | PDF rendering (template only) is fast; LLM latency is separately bounded by SC-002 |

*Post-Phase 1 re-check*: No violations introduced. WeasyPrint PDF rendering from a
pre-generated HTML template completes well within 3s. LLM call time is user-visible
and covered by SC-002 (≤30s total), not by the PDF export gate.

## Project Structure

### Documentation (this feature)

```text
specs/001-ai-resume-builder/
├── plan.md              # This file
├── research.md          # Phase 0 output
├── data-model.md        # Phase 1 output
├── quickstart.md        # Phase 1 output
├── contracts/           # Phase 1 output
│   └── api.md
└── tasks.md             # Phase 2 output (/speckit-tasks command)
```

### Source Code (repository root)

```text
backend/
├── app/
│   ├── main.py                     # FastAPI app init, CORS, router registration
│   ├── database.py                 # SQLAlchemy engine + session factory
│   ├── models/                     # ORM table definitions
│   │   ├── profile.py
│   │   ├── education.py
│   │   ├── certification.py
│   │   ├── experience.py
│   │   └── resume.py
│   ├── schemas/                    # Pydantic v2 request/response schemas
│   │   ├── profile.py
│   │   ├── education.py
│   │   ├── certification.py
│   │   ├── experience.py
│   │   └── resume.py
│   ├── routers/                    # FastAPI route handlers (thin controllers)
│   │   ├── profile.py
│   │   ├── education.py
│   │   ├── certifications.py
│   │   ├── experience.py
│   │   └── resume.py
│   ├── services/                   # Business logic layer
│   │   ├── llm.py                  # Ollama HTTP client wrapper
│   │   ├── job_parser.py           # URL fetch + HTML text extraction
│   │   └── resume_generator.py     # Orchestrates LLM call + Jinja2 rendering
│   └── templates/
│       └── resume.html.j2          # Jinja2 1-column resume template
├── tests/
│   ├── contract/
│   │   └── test_api_contracts.py
│   ├── integration/
│   │   └── test_resume_generation.py
│   └── unit/
│       ├── test_llm_service.py
│       ├── test_job_parser.py
│       └── test_resume_generator.py
├── requirements.txt
├── requirements-dev.txt
└── .env.example

frontend/
├── src/
│   ├── App.vue
│   ├── main.js
│   ├── router/
│   │   └── index.js
│   ├── views/
│   │   ├── ProfileView.vue         # Page 1: personal info management
│   │   └── ResumeGeneratorView.vue # Page 2: job description input + history
│   ├── components/
│   │   ├── profile/
│   │   │   ├── PersonalInfoForm.vue
│   │   │   ├── EducationList.vue
│   │   │   ├── EducationForm.vue
│   │   │   ├── CertificationList.vue
│   │   │   ├── CertificationForm.vue
│   │   │   ├── ExperienceList.vue
│   │   │   └── ExperienceForm.vue
│   │   └── resume/
│   │       ├── JobDescriptionInput.vue
│   │       └── ResumeHistoryList.vue
│   ├── services/
│   │   └── api.js                  # Axios wrapper for all backend calls
│   └── stores/
│       ├── profile.js              # Pinia: profile, education, certs, experience
│       └── resume.js               # Pinia: generation state + history
├── package.json
└── vite.config.js

docker-compose.yml                  # Orchestrates Ollama + backend + frontend dev
.env.example
```

**Structure Decision**: Web app layout (backend/ + frontend/) — distinct API server and
browser client developed and served independently, communicating over localhost HTTP.

## Complexity Tracking

> No constitution violations to justify. All design choices are proportionate to the
> feature requirements.
