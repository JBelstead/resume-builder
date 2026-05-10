"""Integration tests for resume generation (US2)."""

import json
import pytest
from pathlib import Path
from unittest.mock import AsyncMock, patch
from httpx import AsyncClient, ASGITransport
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker

from app.main import app
from app.database import Base, get_db
from app.services.resume_generator import ResumeGenerator

TEST_DB_URL = "sqlite+aiosqlite:///:memory:"

VALID_LLM_OUTPUT = json.dumps({
    "summary": "Strong Python developer with FastAPI expertise.",
    "skills_to_emphasize": ["Python", "FastAPI"],
    "experience_highlights": ["Built REST APIs serving 1M users"],
    "job_title": "Backend Engineer",
    "company_name": "Acme Corp",
})


@pytest.fixture
async def session():
    engine = create_async_engine(TEST_DB_URL)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    factory = async_sessionmaker(engine, expire_on_commit=False)
    async with factory() as s:
        yield s
    await engine.dispose()


@pytest.fixture
async def client(session: AsyncSession):
    async def override():
        yield session

    app.dependency_overrides[get_db] = override
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as c:
        yield c
    app.dependency_overrides.clear()


@pytest.fixture
async def client_with_profile(client: AsyncClient):
    await client.put("/api/profile", json={"name": "Jane Smith", "email": "jane@example.com"})
    await client.post("/api/experience", json={"company": "Acme", "role": "Engineer", "start_date": "2020-01-01"})
    return client


@pytest.mark.asyncio
async def test_generate_returns_400_with_no_profile(client: AsyncClient):
    resp = await client.post(
        "/api/resume/generate",
        json={"job_description_text": "Looking for a Python developer"},
    )
    assert resp.status_code == 400
    assert "profile" in resp.json()["detail"].lower()


@pytest.mark.asyncio
async def test_generate_returns_400_message_exact(client: AsyncClient):
    resp = await client.post(
        "/api/resume/generate",
        json={"job_description_text": "Python developer needed"},
    )
    assert resp.status_code == 400
    assert resp.json()["detail"] == "Complete your profile before generating a resume"


@pytest.mark.asyncio
async def test_generate_creates_resume_record(client_with_profile: AsyncClient, tmp_path: Path):
    with (
        patch.object(ResumeGenerator, "_call_llm", new=AsyncMock(return_value=json.loads(VALID_LLM_OUTPUT))),
        patch.object(ResumeGenerator, "_save_files", return_value=(
            str(tmp_path / "1" / "resume.pdf"),
            str(tmp_path / "1" / "resume.html"),
        )),
    ):
        resp = await client_with_profile.post(
            "/api/resume/generate",
            json={"job_description_text": "Python developer needed"},
        )

    assert resp.status_code == 201
    body = resp.json()
    assert body["job_title"] == "Backend Engineer"
    assert body["company_name"] == "Acme Corp"
    assert "id" in body


@pytest.mark.asyncio
async def test_generate_returns_422_without_any_input(client_with_profile: AsyncClient):
    resp = await client_with_profile.post("/api/resume/generate", json={})
    assert resp.status_code == 422
