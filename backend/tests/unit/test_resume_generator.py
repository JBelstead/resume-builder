"""Unit tests for ResumeGenerator."""

import json
from unittest.mock import AsyncMock, patch

import pytest
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from app.database import Base
from app.models.profile import UserProfile
from app.models.resume import Resume
from app.services.resume_generator import ResumeBuildError, ResumeGenerator

TEST_DB_URL = "sqlite+aiosqlite:///:memory:"

VALID_LLM_OUTPUT = json.dumps(
    {
        "summary": "Experienced engineer with FastAPI expertise.",
        "skills_to_emphasize": ["Python", "FastAPI", "Docker"],
        "experience_highlights": [
            "Led migration to microservices",
            "Reduced latency by 40%",
        ],
        "job_title": "Senior Backend Engineer",
        "company_name": "Acme Corp",
    }
)


@pytest.fixture
async def db_session():
    engine = create_async_engine(TEST_DB_URL)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    factory = async_sessionmaker(engine, expire_on_commit=False)
    async with factory() as session:
        yield session
    await engine.dispose()


@pytest.fixture
async def db_with_profile(db_session: AsyncSession):
    profile = UserProfile(name="Jane Smith", email="jane@example.com")
    db_session.add(profile)
    await db_session.commit()
    await db_session.refresh(profile)
    return db_session


@pytest.mark.asyncio
async def test_generate_creates_resume_record(db_with_profile: AsyncSession):
    with (
        patch.object(
            ResumeGenerator,
            "_call_llm",
            new=AsyncMock(return_value=json.loads(VALID_LLM_OUTPUT)),
        ),
        patch.object(
            ResumeGenerator,
            "_save_files",
            return_value=("/tmp/1/resume.pdf", "/tmp/1/resume.html"),
        ),
    ):
        generator = ResumeGenerator(db_with_profile)
        resume = await generator.generate("Software engineer role at Acme")

    assert isinstance(resume, Resume)
    assert resume.id is not None
    assert resume.job_title == "Senior Backend Engineer"
    assert resume.company_name == "Acme Corp"


@pytest.mark.asyncio
async def test_malformed_llm_json_raises_and_no_record_saved(db_session: AsyncSession):
    profile = UserProfile(name="Jane Smith")
    db_session.add(profile)
    await db_session.commit()

    with patch.object(
        ResumeGenerator,
        "_call_llm",
        new=AsyncMock(side_effect=ResumeBuildError("bad json")),
    ):
        generator = ResumeGenerator(db_session)
        with pytest.raises(ResumeBuildError):
            await generator.generate("some job")

    from sqlalchemy import select

    result = await db_session.execute(select(Resume))
    assert result.scalar_one_or_none() is None


@pytest.mark.asyncio
async def test_experience_highlights_in_template_context(db_with_profile: AsyncSession):
    llm_data = json.loads(VALID_LLM_OUTPUT)
    rendered_html: list[str] = []

    original_render = ResumeGenerator._render_template

    def capture_render(self, *args, **kwargs):
        html = original_render(self, *args, **kwargs)
        rendered_html.append(html)
        return html

    with (
        patch.object(ResumeGenerator, "_call_llm", new=AsyncMock(return_value=llm_data)),
        patch.object(ResumeGenerator, "_render_template", capture_render),
        patch.object(
            ResumeGenerator,
            "_save_files",
            return_value=("/tmp/1/r.pdf", "/tmp/1/r.html"),
        ),
    ):
        generator = ResumeGenerator(db_with_profile)
        await generator.generate("Job description")

    assert rendered_html, "Template was never rendered"
    assert "Led migration to microservices" in rendered_html[0]
    assert "Key Achievements" in rendered_html[0]
