"""Integration tests for resume history endpoints (US3)."""

import json
import pytest
from datetime import datetime
from pathlib import Path
from httpx import AsyncClient, ASGITransport
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker

from app.main import app
from app.database import Base, get_db
from app.models.resume import Resume

TEST_DB_URL = "sqlite+aiosqlite:///:memory:"


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
async def seeded_resume(session: AsyncSession, tmp_path: Path):
    pdf = tmp_path / "resume.pdf"
    pdf.write_bytes(b"%PDF fake")
    html_file = tmp_path / "resume.html"
    html_file.write_text("<html></html>")

    resume = Resume(
        job_title="Backend Engineer",
        company_name="Acme Corp",
        job_description_text="Python developer",
        llm_output=json.dumps({"summary": "Good dev"}),
        pdf_path=str(pdf),
        html_path=str(html_file),
        created_at=datetime.utcnow(),
    )
    session.add(resume)
    await session.commit()
    await session.refresh(resume)
    return resume


@pytest.mark.asyncio
async def test_list_resumes_empty(client: AsyncClient):
    resp = await client.get("/api/resume")
    assert resp.status_code == 200
    assert resp.json() == []


@pytest.mark.asyncio
async def test_list_resumes_returns_items(client: AsyncClient, seeded_resume: Resume):
    resp = await client.get("/api/resume")
    assert resp.status_code == 200
    assert len(resp.json()) == 1
    assert resp.json()[0]["job_title"] == "Backend Engineer"


@pytest.mark.asyncio
async def test_get_resume_detail(client: AsyncClient, seeded_resume: Resume):
    resp = await client.get(f"/api/resume/{seeded_resume.id}")
    assert resp.status_code == 200
    body = resp.json()
    assert body["company_name"] == "Acme Corp"
    assert "llm_output" in body


@pytest.mark.asyncio
async def test_get_resume_404(client: AsyncClient):
    resp = await client.get("/api/resume/9999")
    assert resp.status_code == 404


@pytest.mark.asyncio
async def test_download_resume(client: AsyncClient, seeded_resume: Resume):
    resp = await client.get(f"/api/resume/{seeded_resume.id}/download")
    assert resp.status_code == 200
    assert resp.headers["content-type"] == "application/pdf"
    assert "attachment" in resp.headers["content-disposition"]


@pytest.mark.asyncio
async def test_download_resume_404_missing_file(client: AsyncClient, session: AsyncSession):
    resume = Resume(
        job_title="Test",
        company_name=None,
        llm_output="{}",
        pdf_path="/nonexistent/path/resume.pdf",
        created_at=datetime.utcnow(),
    )
    session.add(resume)
    await session.commit()
    await session.refresh(resume)

    resp = await client.get(f"/api/resume/{resume.id}/download")
    assert resp.status_code == 404


@pytest.mark.asyncio
async def test_delete_resume(client: AsyncClient, seeded_resume: Resume):
    resume_id = seeded_resume.id
    resp = await client.delete(f"/api/resume/{resume_id}")
    assert resp.status_code == 204

    resp = await client.get(f"/api/resume/{resume_id}")
    assert resp.status_code == 404


@pytest.mark.asyncio
async def test_delete_resume_404(client: AsyncClient):
    resp = await client.delete("/api/resume/9999")
    assert resp.status_code == 404
