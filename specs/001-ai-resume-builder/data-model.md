# Data Model: AI Resume Builder

**Feature**: 001-ai-resume-builder
**Date**: 2026-05-10

## Storage Overview

| Layer | Technology | Purpose |
|-------|-----------|---------|
| Structured data | SQLite (via SQLAlchemy 2 + aiosqlite) | Profile, education, certs, experience, resume metadata |
| Resume files | Local filesystem (`resumes/` directory) | Generated PDF and HTML resume files |

---

## Entity Definitions

### UserProfile

The single user's personal and contact information. Only one row is expected to exist.

| Field | Type | Constraints | Description |
|-------|------|-------------|-------------|
| `id` | INTEGER | PK, auto-increment | Internal identifier |
| `name` | TEXT | NOT NULL | Full name as it appears on the resume |
| `email` | TEXT | nullable | Contact email |
| `phone` | TEXT | nullable | Contact phone number |
| `github_url` | TEXT | nullable | Full GitHub profile URL |
| `linkedin_url` | TEXT | nullable | Full LinkedIn profile URL |
| `website_url` | TEXT | nullable | Personal website / portfolio URL |
| `created_at` | DATETIME | NOT NULL, default now | Record creation timestamp |
| `updated_at` | DATETIME | NOT NULL, default now | Last update timestamp (auto-updated) |

**Validation rules**:
- `name` must be non-empty after stripping whitespace.
- URL fields, if provided, must start with `http://` or `https://`.

---

### Education

An academic qualification entry. A user may have zero or more.

| Field | Type | Constraints | Description |
|-------|------|-------------|-------------|
| `id` | INTEGER | PK, auto-increment | Internal identifier |
| `user_profile_id` | INTEGER | FK → UserProfile.id, NOT NULL | Owning profile |
| `institution` | TEXT | NOT NULL | School or university name |
| `degree` | TEXT | NOT NULL | Degree type (e.g., "Bachelor of Science") |
| `field_of_study` | TEXT | nullable | Major or discipline |
| `start_date` | DATE | NOT NULL | Enrolment start date |
| `end_date` | DATE | nullable | Graduation date; NULL means "in progress" |
| `gpa` | TEXT | nullable | GPA string (e.g., "3.8 / 4.0"); text to support different scales |
| `description` | TEXT | nullable | Additional notes (honours, thesis, etc.) |

**Validation rules**:
- `end_date`, if set, must be ≥ `start_date`.
- `gpa`, if provided, must be non-empty.

---

### Certification

A professional certification or licence. A user may have zero or more.

| Field | Type | Constraints | Description |
|-------|------|-------------|-------------|
| `id` | INTEGER | PK, auto-increment | Internal identifier |
| `user_profile_id` | INTEGER | FK → UserProfile.id, NOT NULL | Owning profile |
| `name` | TEXT | NOT NULL | Certification title |
| `issuer` | TEXT | NOT NULL | Issuing organization |
| `issue_date` | DATE | NOT NULL | Date awarded |
| `expiry_date` | DATE | nullable | Expiry date; NULL means no expiry |
| `credential_id` | TEXT | nullable | Unique credential ID from issuer |
| `credential_url` | TEXT | nullable | Verification URL |

**Validation rules**:
- `expiry_date`, if set, must be ≥ `issue_date`.
- `credential_url`, if provided, must be a valid URL.

---

### WorkExperience

A job role held by the user. A user may have zero or more.

| Field | Type | Constraints | Description |
|-------|------|-------------|-------------|
| `id` | INTEGER | PK, auto-increment | Internal identifier |
| `user_profile_id` | INTEGER | FK → UserProfile.id, NOT NULL | Owning profile |
| `company` | TEXT | NOT NULL | Employer name |
| `role` | TEXT | NOT NULL | Job title |
| `start_date` | DATE | NOT NULL | Employment start date |
| `end_date` | DATE | nullable | Employment end date; NULL means "current" |
| `location` | TEXT | nullable | City, Country or "Remote" |
| `description` | TEXT | nullable | Bullet-point responsibilities, one per line |
| `skills` | TEXT | nullable | Comma-separated skill keywords |

**Validation rules**:
- `end_date`, if set, must be ≥ `start_date`.
- `description` lines are newline-separated; the service layer splits on `\n` for rendering.

---

### Resume

Metadata for a generated resume. The actual content files are on disk.

| Field | Type | Constraints | Description |
|-------|------|-------------|-------------|
| `id` | INTEGER | PK, auto-increment | Internal identifier |
| `job_title` | TEXT | nullable | Extracted or inferred job title from description |
| `company_name` | TEXT | nullable | Extracted or inferred company name |
| `job_description_text` | TEXT | nullable | Raw job description text (pasted or fetched) |
| `job_description_url` | TEXT | nullable | Source URL if provided |
| `llm_output` | TEXT | NOT NULL | Raw JSON returned by the LLM |
| `pdf_path` | TEXT | nullable | Absolute path to generated PDF on disk |
| `html_path` | TEXT | nullable | Absolute path to generated HTML on disk |
| `created_at` | DATETIME | NOT NULL, default now | Generation timestamp |

**Validation rules**:
- At least one of `job_description_text` or `job_description_url` must be non-null at
  creation time.
- `llm_output` must be valid JSON before the record is committed.

---

## Relationships

```text
UserProfile 1 ──< Education        (one profile, many education entries)
UserProfile 1 ──< Certification    (one profile, many certification entries)
UserProfile 1 ──< WorkExperience   (one profile, many work experience entries)
Resume             (standalone — snapshot at generation time, not FK-linked to profile)
```

**Note on Resume isolation**: The Resume entity stores the raw LLM output as a snapshot.
It is intentionally not FK-linked to profile sub-entities because the profile may be
edited after a resume is generated; the historical resume must remain stable.

---

## File Storage

Generated resume files are stored under a `resumes/` directory at the repository root
(or a configurable path via the `RESUME_OUTPUT_DIR` environment variable).

```text
resumes/
└── <resume_id>/
    ├── resume.pdf
    └── resume.html
```

The `pdf_path` and `html_path` fields on the `Resume` entity store the absolute paths
to these files at generation time.

---

## Schema Migrations

Alembic is used for all schema changes. Migration scripts live in `backend/alembic/`.
The initial migration creates all five tables. Subsequent migrations follow the
constitution's versioning principle: breaking schema changes increment MAJOR version.
