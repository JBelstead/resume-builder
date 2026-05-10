---
description: "Task list for AI Resume Builder implementation"
---
# Tasks: AI Resume Builder

**Input**: Design documents from `/specs/001-ai-resume-builder/`**Prerequisites**: plan.md ✅ | spec.md ✅ | research.md ✅ | data-model.md ✅ | contracts/api.md ✅ | quickstart.md ✅

**Testing**: TDD is mandatory per the project constitution. Test tasks appear before implementation tasks within each phase. Tests MUST be written and confirmed failing before their corresponding implementation tasks begin.

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `[ID] [P?] [Story?] Description`

- **\[P\]**: Can run in parallel (different files, no shared dependencies)
- **\[Story\]**: Which user story this task belongs to (US1, US2, US3)
- Include exact file paths in all task descriptions

## Path Conventions

- Backend source: `backend/app/`
- Backend tests: `backend/tests/`
- Frontend source: `frontend/src/`
- Frontend tests: `frontend/tests/`

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Project scaffolding — no user story work begins until Phase 2 is complete.

- [ ] T001 Create backend/ directory structure: `backend/app/models/`, `backend/app/schemas/`, `backend/app/routers/`, `backend/app/services/`, `backend/app/templates/`, `backend/tests/contract/`, `backend/tests/integration/`, `backend/tests/unit/`

- [ ] T002 Create `backend/requirements.txt` (fastapi, uvicorn, sqlalchemy\[asyncio\], aiosqlite, alembic, pydantic&gt;=2, httpx, beautifulsoup4, jinja2, weasyprint, python-dotenv) and `backend/requirements-dev.txt` (pytest, pytest-asyncio, httpx, coverage)

- [ ] T003 \[P\] Initialise Vue 3 + Vite project in `frontend/` with Vue Router 4, Pinia, and Axios (`npm create vue@latest`)

- [ ] T004 \[P\] Create `docker-compose.yml` at repository root with three services: `ollama` (port 11434, model volume), `backend` (port 8000, depends on ollama), `frontend` (port 5173)

- [ ] T005 \[P\] Create `.env.example` with variables: `OLLAMA_BASE_URL`, `OLLAMA_MODEL`, `DATABASE_URL`, `RESUME_OUTPUT_DIR`, `CORS_ORIGINS`

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core infrastructure that MUST be complete before ANY user story can start.

**⚠️ CRITICAL**: No user story work begins until this phase is fully complete.

- [ ] T006 Create SQLAlchemy 2 async engine and `AsyncSession` factory in `backend/app/database.py`; include `get_db` dependency for FastAPI route injection

- [ ] T007 Initialise Alembic in `backend/` with async SQLite target; configure `env.py` to import all models for autogenerate support

- [ ] T008 \[P\] Create FastAPI application instance in `backend/app/main.py` with `CORSMiddleware` (reads allowed origins from env), lifespan startup (run `alembic upgrade head`), and `/health` route returning `{"status": "ok"}`

- [ ] T009 \[P\] Set up Vue Router 4 in `frontend/src/router/index.js` with two routes: `/` → `ProfileView` and `/generate` → `ResumeGeneratorView`; use hash mode

- [ ] T010 \[P\] Create `frontend/src/App.vue` with a navigation bar containing links to both pages (`/` and `/generate`)

- [ ] T011 \[P\] Create `frontend/src/services/api.js` as an Axios instance targeting `http://localhost:8000/api`; export typed helper functions for each resource (`profile`, `education`, `certifications`, `experience`, `resume`)

**Checkpoint**: Foundation complete — all user stories can now begin in parallel.

---

## Phase 3: User Story 1 — Manage Personal Profile (Priority: P1) 🎯 MVP

**Goal**: Users can enter, save, and edit their full professional profile (personal info, education, certifications, and work experience) with persistence across sessions.

**Independent Test**: Open the app fresh, complete all four profile sections, save, restart the backend, reload the page, and confirm all entries are pre-populated and editable.

### Tests for User Story 1 ⚠️ Write these FIRST — confirm they FAIL before T014

- [ ] T012 \[P\] \[US1\] Write failing contract tests for `GET /profile`, `PUT /profile` in `backend/tests/contract/test_api_contracts.py`; assert correct status codes, response shapes, and validation rejections

- [ ] T013 \[P\] \[US1\] Write failing contract tests for `GET/POST/PUT/DELETE /education`, `/certifications`, `/experience` in `backend/tests/contract/test_api_contracts.py`; include 404 on missing ID and 422 on invalid payload

### Implementation for User Story 1

- [ ] T014 \[P\] \[US1\] Create `UserProfile` SQLAlchemy model (id, name, email, phone, github_url, linkedin_url, website_url, created_at, updated_at) in `backend/app/models/profile.py`

- [ ] T015 \[P\] \[US1\] Create `Education` SQLAlchemy model (id, user_profile_id FK, institution, degree, field_of_study, start_date, end_date, gpa, description) in `backend/app/models/education.py`

- [ ] T016 \[P\] \[US1\] Create `Certification` SQLAlchemy model (id, user_profile_id FK, name, issuer, issue_date, expiry_date, credential_id, credential_url) in `backend/app/models/certification.py`

- [ ] T017 \[P\] \[US1\] Create `WorkExperience` SQLAlchemy model (id, user_profile_id FK, company, role, start_date, end_date, location, description, skills) in `backend/app/models/experience.py`

- [ ] T018 \[P\] \[US1\] Create Pydantic v2 request/response schemas for `UserProfile` in `backend/app/schemas/profile.py`; include URL validators and non-empty name check

- [ ] T019 \[P\] \[US1\] Create Pydantic v2 schemas for `Education` in `backend/app/schemas/education.py`; validate `end_date >= start_date` when both provided

- [ ] T020 \[P\] \[US1\] Create Pydantic v2 schemas for `Certification` in `backend/app/schemas/certification.py`; validate `expiry_date >= issue_date` when provided

- [ ] T021 \[P\] \[US1\] Create Pydantic v2 schemas for `WorkExperience` in `backend/app/schemas/experience.py`; validate `end_date >= start_date` when provided

- [ ] T022 \[US1\] Generate Alembic autogenerate migration for `user_profiles`, `educations`, `certifications`, `work_experiences` tables in `backend/alembic/versions/`; verify migration applies cleanly with `alembic upgrade head`

- [ ] T023 \[P\] \[US1\] Implement `GET /profile` (return 404 when absent) and `PUT /profile` (upsert) endpoint handlers in `backend/app/routers/profile.py`

- [ ] T024 \[P\] \[US1\] Implement `GET /education`, `POST /education`, `PUT /education/{id}`, `DELETE /education/{id}` in `backend/app/routers/education.py`

- [ ] T025 \[P\] \[US1\] Implement `GET /certifications`, `POST /certifications`, `PUT /certifications/{id}`, `DELETE /certifications/{id}` in `backend/app/routers/certifications.py`

- [ ] T026 \[P\] \[US1\] Implement `GET /experience`, `POST /experience`, `PUT /experience/{id}`, `DELETE /experience/{id}` in `backend/app/routers/experience.py`

- [ ] T027 \[US1\] Register profile, education, certifications, and experience routers in `backend/app/main.py` under `/api` prefix

- [ ] T028 \[P\] \[US1\] Create `PersonalInfoForm.vue` component (name, email, phone, GitHub URL, LinkedIn URL, website URL fields with save button) in `frontend/src/components/profile/PersonalInfoForm.vue`

- [ ] T029 \[P\] \[US1\] Create `EducationList.vue` (displays entries, edit/delete actions) and `EducationForm.vue` (add/edit form modal) in `frontend/src/components/profile/`

- [ ] T030 \[P\] \[US1\] Create `CertificationList.vue` and `CertificationForm.vue` in `frontend/src/components/profile/`

- [ ] T031 \[P\] \[US1\] Create `ExperienceList.vue` and `ExperienceForm.vue` (with skills comma-separated input and "current position" toggle for no end date) in `frontend/src/components/profile/`

- [ ] T032 \[US1\] Implement Pinia `profile` store in `frontend/src/stores/profile.js` with actions for fetch/save profile, and full CRUD for education, certifications, and experience via `api.js`

- [ ] T033 \[US1\] Implement `ProfileView.vue` composing `PersonalInfoForm`, `EducationList`, `CertificationList`, `ExperienceList` with loading states and success/error feedback in `frontend/src/views/ProfileView.vue`

- [ ] T034 \[P\] \[US1\] Write unit tests for profile, education, certification, and experience router handlers in `backend/tests/unit/test_profile_routers.py`

- [ ] T035 \[P\] \[US1\] Write integration test covering complete profile CRUD lifecycle (create → read → update → delete each entity) in `backend/tests/integration/test_profile.py`

**Checkpoint**: User Story 1 fully functional — profile survives backend restart and all CRUD operations work independently.

---

## Phase 4: User Story 2 — Generate Tailored Resume (Priority: P1)

**Goal**: Given a populated profile, a user submits a job description (text or URL) and receives a tailored resume PDF with all sections populated from their profile data.

**Independent Test**: With a populated profile, paste a sample job description, click Generate, wait ≤30s, confirm a PDF is returned and contains the user's name, at least one experience entry, and the education section.

### Tests for User Story 2 ⚠️ Write these FIRST — confirm they FAIL before T042

- [ ] T036 \[P\] \[US2\] Write failing unit tests for `LLMService` in `backend/tests/unit/test_llm_service.py`; mock Ollama HTTP responses to test prompt construction, JSON parsing, and timeout handling

- [ ] T037 \[P\] \[US2\] Write failing unit tests for `JobParser` in `backend/tests/unit/test_job_parser.py`; test URL fetch with mocked responses, HTML stripping, and error on unreachable URL

- [ ] T038 \[P\] \[US2\] Write failing unit tests for `ResumeGenerator` in `backend/tests/unit/test_resume_generator.py`; test LLM output → Jinja2 context mapping and PDF file creation with mocked services

### Implementation for User Story 2

- [ ] T039 \[US2\] Create `Resume` SQLAlchemy model (id, job_title, company_name, job_description_text, job_description_url, llm_output, pdf_path, html_path, created_at) in `backend/app/models/resume.py`

- [ ] T040 \[US2\] Create Pydantic v2 schemas for `Resume` (generate request, response, list item) in `backend/app/schemas/resume.py`; validate at-least-one-of text/url constraint

- [ ] T041 \[US2\] Generate Alembic migration for `resumes` table in `backend/alembic/versions/`; verify with `alembic upgrade head`

- [ ] T042 \[US2\] Implement `LLMService` in `backend/app/services/llm.py`: async `httpx` POST to Ollama `/api/chat`, structured JSON system prompt, 60s timeout, raises `LLMUnavailableError` and `LLMTimeoutError`

- [ ] T043 \[US2\] Implement `JobParser` in `backend/app/services/job_parser.py`: async fetch URL with `httpx`, extract body text via `BeautifulSoup4` (strip script/style/nav), raise `JobURLError` on failure

- [ ] T044 \[US2\] Create Jinja2 1-column resume template `backend/app/templates/resume.html.j2` with sections: header (name, email, phone, GitHub, LinkedIn, website), summary, experience (loop, shows "Present" for null end_date), education, certifications; include print-safe CSS

- [ ] T045 \[US2\] Implement `ResumeGenerator` in `backend/app/services/resume_generator.py`: fetch full user profile from DB, build LLM prompt with profile JSON + job description, call `LLMService`, parse JSON response, render Jinja2 template, generate PDF via WeasyPrint, save both HTML and PDF to `RESUME_OUTPUT_DIR/<resume_id>/`, persist `Resume` record

- [ ] T046 \[US2\] Implement `POST /resume/generate` endpoint in `backend/app/routers/resume.py`: validate profile exists (return 400 if not), call `ResumeGenerator`, return 201 with resume metadata; map `LLMUnavailableError` → 502, `LLMTimeoutError` → 504, `JobURLError` → 422

- [ ] T047 \[US2\] Register resume router in `backend/app/main.py` under `/api` prefix

- [ ] T048 \[US2\] Implement `JobDescriptionInput.vue` with a tab control (Text / URL), textarea for pasted text, URL input field, and a Submit button; emit `submit` event with payload in `frontend/src/components/resume/JobDescriptionInput.vue`

- [ ] T049 \[US2\] Implement Pinia `resume` store in `frontend/src/stores/resume.js` with `generate(payload)` action tracking `status` (idle/loading/success/error) and storing the returned resume record

- [ ] T050 \[US2\] Implement `ResumeGeneratorView.vue` composing `JobDescriptionInput`, a loading spinner during generation, a success panel with PDF download link, and user-friendly error messages for 400/502/504/422 responses in `frontend/src/views/ResumeGeneratorView.vue`

- [ ] T051 \[US2\] Write integration test covering full generation flow: seed profile data → `POST /resume/generate` with mocked Ollama → assert 201, PDF file created on disk, resume record in DB in `backend/tests/integration/test_resume_generation.py`

**Checkpoint**: User Story 2 fully functional — submit a job description with a populated profile and receive a downloadable PDF resume.

---

## Phase 5: User Story 3 — Access Previously Generated Resumes (Priority: P2)

**Goal**: Users can view a list of all previously generated resumes, download any as PDF, and delete entries they no longer need — without re-submitting the job description.

**Independent Test**: After generating two resumes, navigate to the Generate page, see both listed with job title and date, download each, confirm correct PDF content, then delete one and confirm it disappears from the list.

### Implementation for User Story 3

- [ ] T052 \[P\] \[US3\] Implement `GET /resume` (list, ordered by created_at desc) and `GET /resume/{id}` (detail including llm_output) in `backend/app/routers/resume.py`

- [ ] T053 \[P\] \[US3\] Implement `GET /resume/{id}/download` (file response, Content-Type: application/pdf, Content-Disposition: attachment) in `backend/app/routers/resume.py`; return 404 if PDF file missing from disk

- [ ] T054 \[P\] \[US3\] Implement `DELETE /resume/{id}` (delete DB record and remove `resumes/<id>/` directory) in `backend/app/routers/resume.py`

- [ ] T055 \[US3\] Create `ResumeHistoryList.vue` component displaying past resumes in a table (job title, company, date, Download button, Delete button) in `frontend/src/components/resume/ResumeHistoryList.vue`

- [ ] T056 \[US3\] Extend Pinia `resume` store with `fetchHistory()`, `downloadResume(id)`, and `deleteResume(id)` actions in `frontend/src/stores/resume.js`

- [ ] T057 \[US3\] Add `ResumeHistoryList` below `JobDescriptionInput` in `ResumeGeneratorView.vue`; fetch history on mount and refresh after each generation or deletion in `frontend/src/views/ResumeGeneratorView.vue`

- [ ] T058 \[P\] \[US3\] Write integration tests for `GET /resume`, `GET /resume/{id}`, `GET /resume/{id}/download`, and `DELETE /resume/{id}` in `backend/tests/integration/test_resume_history.py`

**Checkpoint**: All three user stories independently functional and testable.

---

## Phase 6: Polish & Cross-Cutting Concerns

**Purpose**: Hardening, accessibility, and end-to-end validation across all stories.

- [ ] T059 \[P\] Add loading skeleton / spinner to all async operations in Vue components (profile save, each CRUD action, resume generation); ensure visible feedback within 100ms of user action (constitution §III)

- [ ] T060 \[P\] Add error boundary component in `frontend/src/App.vue` catching unhandled promise rejections; display toast/banner with actionable message and dismiss button

- [ ] T061 \[P\] Verify no-profile guard on `POST /resume/generate` returns 400 with message "Complete your profile before generating a resume" in `backend/app/routers/resume.py`; add corresponding UI message in `ResumeGeneratorView.vue`

- [ ] T062 \[P\] Write Vitest component tests for `PersonalInfoForm.vue`, `JobDescriptionInput.vue`, and `ResumeHistoryList.vue` in `frontend/tests/components/`

- [ ] T063 \[P\] Audit all outbound network calls in the backend: assert only `localhost:11434` (Ollama) and user-supplied job URLs are ever contacted; document in `backend/app/services/` module docstrings (constitution §FR-009)

- [x] T064 Run quickstart.md end-to-end validation: `docker compose up` → fill full profile → submit job description → confirm PDF downloads correctly → delete resume → confirm removed from history

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies — start immediately
- **Foundational (Phase 2)**: Depends on Phase 1 completion — BLOCKS all user stories
- **US1 (Phase 3)**: Depends on Foundational phase only — independent of US2, US3
- **US2 (Phase 4)**: Depends on Foundational phase; also depends on US1 models being migrated (T022) since it reads the profile from the database
- **US3 (Phase 5)**: Depends on US2 (extends the same `/resume` router)
- **Polish (Phase 6)**: Depends on all user stories being complete

### User Story Dependencies

- **US1**: Standalone — no dependency on US2 or US3
- **US2**: Depends on profile data existing in DB (T022 migration must be applied)
- **US3**: Depends on US2 (resume records must exist to list/download/delete)

### Within Each Phase

- Contract/unit tests MUST be written and failing before implementation tasks begin (TDD)
- Models → Schemas → Alembic migration → Routers (backend sequencing per story)
- Pinia store → View (frontend sequencing per story)
- Tasks marked \[P\] within the same phase can run simultaneously

---

## Parallel Execution Example: Phase 3 (User Story 1)

```text
# Run simultaneously after T011 (foundation complete):
T012: contract tests for profile endpoints
T013: contract tests for education/certifications/experience endpoints

# Then run simultaneously (after T012, T013 confirmed failing):
T014: UserProfile model
T015: Education model
T016: Certification model
T017: WorkExperience model
T018: UserProfile schemas
T019: Education schemas
T020: Certification schemas
T021: WorkExperience schemas

# Then sequentially:
T022: Alembic migration (needs all models)

# Then run simultaneously:
T023: profile router
T024: education router
T025: certifications router
T026: experience router
T028: PersonalInfoForm.vue
T029: EducationList + EducationForm
T030: CertificationList + CertificationForm
T031: ExperienceList + ExperienceForm

# Then sequentially:
T027: register routers
T032: Pinia profile store (needs components)
T033: ProfileView.vue (needs store)

# Then simultaneously:
T034: unit tests for routers
T035: integration test for CRUD lifecycle
```

---

## Implementation Strategy

### MVP First (User Stories 1 + 2 Only)

1. Complete Phase 1: Setup
2. Complete Phase 2: Foundational (CRITICAL — blocks everything)
3. Complete Phase 3: User Story 1 (profile management)
4. **STOP and VALIDATE**: Save profile, restart backend, reload — all data persists ✅
5. Complete Phase 4: User Story 2 (resume generation)
6. **STOP and VALIDATE**: Submit job description → PDF downloads ✅
7. Deploy/demo as MVP

### Incremental Delivery

1. Setup + Foundational → skeleton app running
2. User Story 1 → profile management works → validate independently
3. User Story 2 → resume generation works → validate independently
4. User Story 3 → history management → validate independently
5. Polish → production-ready hardening

---

## Notes

- `[P]` tasks have no shared file dependencies — safe to run in parallel
- `[US?]` label maps each task to its user story for traceability
- TDD order is enforced by the project constitution: write tests → confirm failure → implement
- Commit after each completed phase or logical group
- Stop at each **Checkpoint** to independently validate the story before moving on
- Total tasks: **64** | US1: 24 | US2: 16 | US3: 7 | Setup/Foundation/Polish: 17