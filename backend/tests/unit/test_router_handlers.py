"""Direct route-handler invocation tests.

Calls async route-handler functions without going through the ASGI layer so
pytest-cov can track lines that follow `await` expressions inside the handlers.
"""

import pytest
from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from app.database import Base
from app.models.profile import UserProfile
from app.routers.certifications import (
    create_certification,
    delete_certification,
    list_certifications,
    update_certification,
)
from app.routers.education import (
    create_education,
    delete_education,
    list_education,
    update_education,
)
from app.routers.experience import (
    create_experience,
    delete_experience,
    list_experience,
    update_experience,
)
from app.routers.profile import get_profile, upsert_profile
from app.schemas.certification import CertificationCreate, CertificationUpdate
from app.schemas.education import EducationCreate, EducationUpdate
from app.schemas.experience import ExperienceCreate, ExperienceUpdate
from app.schemas.profile import ProfileCreate

TEST_DB_URL = "sqlite+aiosqlite:///:memory:"


@pytest.fixture
async def db():
    engine = create_async_engine(TEST_DB_URL)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    factory = async_sessionmaker(engine, expire_on_commit=False)
    async with factory() as session:
        yield session
    await engine.dispose()


@pytest.fixture
async def db_with_profile(db: AsyncSession):
    profile = UserProfile(name="Direct Test User", email="direct@test.com")
    db.add(profile)
    await db.commit()
    return db


# ─── Profile router ───────────────────────────────────────────────────────────


@pytest.mark.asyncio
async def test_get_profile_404_direct(db: AsyncSession):
    with pytest.raises(HTTPException) as exc:
        await get_profile(db=db)
    assert exc.value.status_code == 404


@pytest.mark.asyncio
async def test_get_profile_success_direct(db_with_profile: AsyncSession):
    result = await get_profile(db=db_with_profile)
    assert result.name == "Direct Test User"


@pytest.mark.asyncio
async def test_upsert_profile_create_direct(db: AsyncSession):
    result = await upsert_profile(data=ProfileCreate(name="Created"), db=db)
    assert result.name == "Created"
    assert result.id is not None


@pytest.mark.asyncio
async def test_upsert_profile_update_direct(db_with_profile: AsyncSession):
    result = await upsert_profile(
        data=ProfileCreate(name="Updated", email="new@test.com"),
        db=db_with_profile,
    )
    assert result.name == "Updated"
    assert result.email == "new@test.com"


# ─── Certifications router ────────────────────────────────────────────────────


@pytest.mark.asyncio
async def test_list_certifications_direct(db_with_profile: AsyncSession):
    result = await list_certifications(db=db_with_profile)
    assert result == []


@pytest.mark.asyncio
async def test_create_certification_direct(db_with_profile: AsyncSession):
    cert = await create_certification(
        data=CertificationCreate(name="AWS SAA", issuer="Amazon"),
        db=db_with_profile,
    )
    assert cert.name == "AWS SAA"
    assert cert.id is not None


@pytest.mark.asyncio
async def test_update_certification_direct(db_with_profile: AsyncSession):
    cert = await create_certification(
        data=CertificationCreate(name="AWS SAA", issuer="Amazon"),
        db=db_with_profile,
    )
    updated = await update_certification(
        entry_id=cert.id,
        data=CertificationUpdate(name="AWS SAP"),
        db=db_with_profile,
    )
    assert updated.name == "AWS SAP"


@pytest.mark.asyncio
async def test_update_certification_404_direct(db_with_profile: AsyncSession):
    with pytest.raises(HTTPException) as exc:
        await update_certification(
            entry_id=99999,
            data=CertificationUpdate(name="X"),
            db=db_with_profile,
        )
    assert exc.value.status_code == 404


@pytest.mark.asyncio
async def test_delete_certification_direct(db_with_profile: AsyncSession):
    cert = await create_certification(
        data=CertificationCreate(name="AWS SAA", issuer="Amazon"),
        db=db_with_profile,
    )
    await delete_certification(entry_id=cert.id, db=db_with_profile)
    remaining = await list_certifications(db=db_with_profile)
    assert remaining == []


# ─── Education router ─────────────────────────────────────────────────────────


@pytest.mark.asyncio
async def test_list_education_direct(db_with_profile: AsyncSession):
    result = await list_education(db=db_with_profile)
    assert result == []


@pytest.mark.asyncio
async def test_create_education_direct(db_with_profile: AsyncSession):
    edu = await create_education(
        data=EducationCreate(institution="MIT", degree="BSc"),
        db=db_with_profile,
    )
    assert edu.institution == "MIT"


@pytest.mark.asyncio
async def test_update_education_direct(db_with_profile: AsyncSession):
    edu = await create_education(
        data=EducationCreate(institution="MIT", degree="BSc"),
        db=db_with_profile,
    )
    updated = await update_education(
        entry_id=edu.id,
        data=EducationUpdate(degree="PhD"),
        db=db_with_profile,
    )
    assert updated.degree == "PhD"


@pytest.mark.asyncio
async def test_update_education_404_direct(db_with_profile: AsyncSession):
    with pytest.raises(HTTPException) as exc:
        await update_education(
            entry_id=99999,
            data=EducationUpdate(degree="PhD"),
            db=db_with_profile,
        )
    assert exc.value.status_code == 404


@pytest.mark.asyncio
async def test_delete_education_direct(db_with_profile: AsyncSession):
    edu = await create_education(
        data=EducationCreate(institution="MIT", degree="BSc"),
        db=db_with_profile,
    )
    await delete_education(entry_id=edu.id, db=db_with_profile)
    remaining = await list_education(db=db_with_profile)
    assert remaining == []


@pytest.mark.asyncio
async def test_delete_education_404_direct(db_with_profile: AsyncSession):
    with pytest.raises(HTTPException) as exc:
        await delete_education(entry_id=99999, db=db_with_profile)
    assert exc.value.status_code == 404


# ─── Experience router ────────────────────────────────────────────────────────


@pytest.mark.asyncio
async def test_list_experience_direct(db_with_profile: AsyncSession):
    result = await list_experience(db=db_with_profile)
    assert result == []


@pytest.mark.asyncio
async def test_create_experience_direct(db_with_profile: AsyncSession):
    exp = await create_experience(
        data=ExperienceCreate(company="Acme", role="Engineer"),
        db=db_with_profile,
    )
    assert exp.company == "Acme"


@pytest.mark.asyncio
async def test_update_experience_direct(db_with_profile: AsyncSession):
    exp = await create_experience(
        data=ExperienceCreate(company="Acme", role="Engineer"),
        db=db_with_profile,
    )
    updated = await update_experience(
        entry_id=exp.id,
        data=ExperienceUpdate(role="Lead"),
        db=db_with_profile,
    )
    assert updated.role == "Lead"


@pytest.mark.asyncio
async def test_update_experience_404_direct(db_with_profile: AsyncSession):
    with pytest.raises(HTTPException) as exc:
        await update_experience(
            entry_id=99999,
            data=ExperienceUpdate(role="Lead"),
            db=db_with_profile,
        )
    assert exc.value.status_code == 404


@pytest.mark.asyncio
async def test_delete_experience_direct(db_with_profile: AsyncSession):
    exp = await create_experience(
        data=ExperienceCreate(company="Acme", role="Engineer"),
        db=db_with_profile,
    )
    await delete_experience(entry_id=exp.id, db=db_with_profile)
    remaining = await list_experience(db=db_with_profile)
    assert remaining == []


@pytest.mark.asyncio
async def test_delete_experience_404_direct(db_with_profile: AsyncSession):
    with pytest.raises(HTTPException) as exc:
        await delete_experience(entry_id=99999, db=db_with_profile)
    assert exc.value.status_code == 404
