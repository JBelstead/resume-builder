# API Contract: AI Resume Builder

**Base URL**: `http://localhost:8000/api`
**Protocol**: HTTP/1.1 REST
**Content-Type**: `application/json` (all request and response bodies)
**Auth**: None (single-user local application)
**Error format**: All errors return `{ "detail": "<message>" }` with the appropriate
HTTP status code.

---

## Profile

### GET /profile

Retrieve the user's profile. Returns 404 if no profile has been created yet.

**Response 200**:
```json
{
  "id": 1,
  "name": "Jane Smith",
  "email": "jane@example.com",
  "phone": "+1 555 000 1234",
  "github_url": "https://github.com/janesmith",
  "linkedin_url": "https://linkedin.com/in/janesmith",
  "website_url": "https://janesmith.dev",
  "created_at": "2026-05-10T10:00:00",
  "updated_at": "2026-05-10T10:00:00"
}
```

**Response 404**: Profile not yet created.

---

### PUT /profile

Create or update (upsert) the user's profile.

**Request body**:
```json
{
  "name": "Jane Smith",
  "email": "jane@example.com",
  "phone": "+1 555 000 1234",
  "github_url": "https://github.com/janesmith",
  "linkedin_url": "https://linkedin.com/in/janesmith",
  "website_url": "https://janesmith.dev"
}
```

**Validation**: `name` is required and must be non-empty. URL fields, if present, must
begin with `http://` or `https://`.

**Response 200**: Returns the full profile object (same shape as GET /profile).

**Response 422**: Validation error with field-level detail.

---

## Education

### GET /education

List all education entries for the user, ordered by `start_date` descending.

**Response 200**:
```json
[
  {
    "id": 1,
    "institution": "University of Technology",
    "degree": "Bachelor of Science",
    "field_of_study": "Computer Science",
    "start_date": "2018-09-01",
    "end_date": "2022-06-30",
    "gpa": "3.9 / 4.0",
    "description": null
  }
]
```

---

### POST /education

Add a new education entry.

**Request body**:
```json
{
  "institution": "University of Technology",
  "degree": "Bachelor of Science",
  "field_of_study": "Computer Science",
  "start_date": "2018-09-01",
  "end_date": "2022-06-30",
  "gpa": "3.9 / 4.0",
  "description": null
}
```

**Validation**: `institution`, `degree`, and `start_date` are required. `end_date`
must be ≥ `start_date` if provided.

**Response 201**: Returns the created entry.

---

### PUT /education/{id}

Update an existing education entry by ID.

**Request body**: Same shape as POST /education (all fields optional; only provided
fields are updated).

**Response 200**: Returns the updated entry.
**Response 404**: Entry not found.

---

### DELETE /education/{id}

Delete an education entry by ID.

**Response 204**: No content.
**Response 404**: Entry not found.

---

## Certifications

### GET /certifications

List all certification entries, ordered by `issue_date` descending.

**Response 200**:
```json
[
  {
    "id": 1,
    "name": "AWS Certified Solutions Architect",
    "issuer": "Amazon Web Services",
    "issue_date": "2025-03-01",
    "expiry_date": "2028-03-01",
    "credential_id": "ABC-12345",
    "credential_url": "https://aws.amazon.com/verify/ABC-12345"
  }
]
```

---

### POST /certifications

Add a new certification entry.

**Request body**:
```json
{
  "name": "AWS Certified Solutions Architect",
  "issuer": "Amazon Web Services",
  "issue_date": "2025-03-01",
  "expiry_date": "2028-03-01",
  "credential_id": "ABC-12345",
  "credential_url": "https://aws.amazon.com/verify/ABC-12345"
}
```

**Validation**: `name`, `issuer`, and `issue_date` are required.

**Response 201**: Returns the created entry.

---

### PUT /certifications/{id}

Update an existing certification entry.

**Response 200**: Returns the updated entry.
**Response 404**: Entry not found.

---

### DELETE /certifications/{id}

Delete a certification entry.

**Response 204**: No content.
**Response 404**: Entry not found.

---

## Work Experience

### GET /experience

List all work experience entries, ordered by `start_date` descending.

**Response 200**:
```json
[
  {
    "id": 1,
    "company": "Acme Corp",
    "role": "Senior Software Engineer",
    "start_date": "2022-07-01",
    "end_date": null,
    "location": "Remote",
    "description": "Led backend API development\nImproved CI pipeline reducing build time by 40%",
    "skills": "Python,FastAPI,PostgreSQL,Docker"
  }
]
```

**Note**: `end_date: null` means the position is current.

---

### POST /experience

Add a new work experience entry.

**Request body**:
```json
{
  "company": "Acme Corp",
  "role": "Senior Software Engineer",
  "start_date": "2022-07-01",
  "end_date": null,
  "location": "Remote",
  "description": "Led backend API development\nImproved CI pipeline reducing build time by 40%",
  "skills": "Python,FastAPI,PostgreSQL,Docker"
}
```

**Validation**: `company`, `role`, and `start_date` are required.

**Response 201**: Returns the created entry.

---

### PUT /experience/{id}

Update a work experience entry.

**Response 200**: Returns the updated entry.
**Response 404**: Entry not found.

---

### DELETE /experience/{id}

Delete a work experience entry.

**Response 204**: No content.
**Response 404**: Entry not found.

---

## Resume Generation

### POST /resume/generate

Submit a job description (text or URL) to generate a tailored resume. This is a
synchronous operation that may take up to 30 seconds under normal conditions while
the LLM processes the request. The server enforces a hard 60-second timeout; if the
LLM has not responded by then, a 504 is returned.

**Request body**: At least one of `job_description_text` or `job_description_url`
must be non-null. If both are provided, `job_description_text` takes precedence and
`job_description_url` is ignored.

```json
{
  "job_description_text": "We are looking for a Senior Python Engineer...",
  "job_description_url": null
}
```

Or with URL:
```json
{
  "job_description_text": null,
  "job_description_url": "https://jobs.example.com/senior-python-engineer"
}
```

**Response 201**:
```json
{
  "id": 42,
  "job_title": "Senior Python Engineer",
  "company_name": "Example Corp",
  "job_description_url": null,
  "pdf_path": "/absolute/path/to/resumes/42/resume.pdf",
  "html_path": "/absolute/path/to/resumes/42/resume.html",
  "created_at": "2026-05-10T14:30:00"
}
```

**Response 400**: No profile data exists to generate from; user must complete profile first.
**Response 502**: LLM service (Ollama) is unreachable.
**Response 504**: LLM request timed out (exceeded 60-second server-side hard limit; expected completion is ≤30 seconds under normal conditions).
**Response 422**: Neither `job_description_text` nor `job_description_url` provided,
or URL fetch failed.

---

### GET /resume

List all previously generated resumes, ordered by `created_at` descending.

**Response 200**:
```json
[
  {
    "id": 42,
    "job_title": "Senior Python Engineer",
    "company_name": "Example Corp",
    "job_description_url": null,
    "created_at": "2026-05-10T14:30:00"
  }
]
```

---

### GET /resume/{id}

Get full details of a specific resume including the LLM output.

**Response 200**:
```json
{
  "id": 42,
  "job_title": "Senior Python Engineer",
  "company_name": "Example Corp",
  "job_description_text": "We are looking for...",
  "job_description_url": null,
  "llm_output": "{\"summary\": \"...\", \"experience_highlights\": [...]}",
  "pdf_path": "/absolute/path/resumes/42/resume.pdf",
  "html_path": "/absolute/path/resumes/42/resume.html",
  "created_at": "2026-05-10T14:30:00"
}
```

**Response 404**: Resume not found.

---

### GET /resume/{id}/download

Download the generated PDF file for a resume.

**Response 200**: File response with `Content-Type: application/pdf` and
`Content-Disposition: attachment; filename="resume.pdf"`.

**Response 404**: Resume or PDF file not found.

---

### DELETE /resume/{id}

Delete a resume record and its associated files.

**Response 204**: No content.
**Response 404**: Resume not found.

---

## Health

### GET /health

Lightweight health check endpoint for development and Docker Compose readiness probes.

**Response 200**:
```json
{ "status": "ok" }
```
