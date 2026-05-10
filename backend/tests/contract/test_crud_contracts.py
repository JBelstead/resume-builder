"""Contract tests for education, certifications, and experience CRUD endpoints."""

import pytest
from httpx import AsyncClient, ASGITransport
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker

from app.main import app
from app.database import Base, get_db

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
    async def override_get_db():
        yield session

    app.dependency_overrides[get_db] = override_get_db
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as c:
        yield c
    app.dependency_overrides.clear()


@pytest.fixture
async def profile_client(client: AsyncClient):
    await client.put("/api/profile", json={"name": "Test User"})
    return client


# ─── Education ───────────────────────────────────────────────────────────────

@pytest.mark.asyncio
async def test_list_education_requires_profile(client: AsyncClient):
    resp = await client.get("/api/education")
    assert resp.status_code == 404


@pytest.mark.asyncio
async def test_create_education(profile_client: AsyncClient):
    resp = await profile_client.post(
        "/api/education",
        json={"institution": "MIT", "degree": "BSc", "field_of_study": "CS"},
    )
    assert resp.status_code == 201
    assert resp.json()["institution"] == "MIT"


@pytest.mark.asyncio
async def test_create_education_invalid_dates(profile_client: AsyncClient):
    resp = await profile_client.post(
        "/api/education",
        json={"institution": "MIT", "degree": "BSc", "start_date": "2020-01-01", "end_date": "2019-01-01"},
    )
    assert resp.status_code == 422


@pytest.mark.asyncio
async def test_update_education(profile_client: AsyncClient):
    create = await profile_client.post(
        "/api/education", json={"institution": "MIT", "degree": "BSc"}
    )
    edu_id = create.json()["id"]
    resp = await profile_client.put(f"/api/education/{edu_id}", json={"degree": "MSc"})
    assert resp.status_code == 200
    assert resp.json()["degree"] == "MSc"


@pytest.mark.asyncio
async def test_update_education_404(profile_client: AsyncClient):
    resp = await profile_client.put("/api/education/9999", json={"degree": "PhD"})
    assert resp.status_code == 404


@pytest.mark.asyncio
async def test_delete_education(profile_client: AsyncClient):
    create = await profile_client.post(
        "/api/education", json={"institution": "MIT", "degree": "BSc"}
    )
    edu_id = create.json()["id"]
    resp = await profile_client.delete(f"/api/education/{edu_id}")
    assert resp.status_code == 204
    list_resp = await profile_client.get("/api/education")
    assert all(e["id"] != edu_id for e in list_resp.json())


# ─── Certifications ───────────────────────────────────────────────────────────

@pytest.mark.asyncio
async def test_create_certification(profile_client: AsyncClient):
    resp = await profile_client.post(
        "/api/certifications",
        json={"name": "AWS SAA", "issuer": "Amazon", "issue_date": "2023-01-01"},
    )
    assert resp.status_code == 201
    assert resp.json()["name"] == "AWS SAA"


@pytest.mark.asyncio
async def test_create_certification_422_on_invalid_payload(profile_client: AsyncClient):
    resp = await profile_client.post("/api/certifications", json={"issuer": "Amazon"})
    assert resp.status_code == 422


@pytest.mark.asyncio
async def test_delete_certification_404(profile_client: AsyncClient):
    resp = await profile_client.delete("/api/certifications/9999")
    assert resp.status_code == 404


# ─── Experience ───────────────────────────────────────────────────────────────

@pytest.mark.asyncio
async def test_create_experience(profile_client: AsyncClient):
    resp = await profile_client.post(
        "/api/experience",
        json={"company": "Acme", "role": "Engineer", "start_date": "2021-01-01"},
    )
    assert resp.status_code == 201
    assert resp.json()["company"] == "Acme"


@pytest.mark.asyncio
async def test_create_experience_invalid_dates(profile_client: AsyncClient):
    resp = await profile_client.post(
        "/api/experience",
        json={"company": "Acme", "role": "Eng", "start_date": "2022-01-01", "end_date": "2021-01-01"},
    )
    assert resp.status_code == 422


@pytest.mark.asyncio
async def test_update_experience_404(profile_client: AsyncClient):
    resp = await profile_client.put("/api/experience/9999", json={"role": "Lead"})
    assert resp.status_code == 404


@pytest.mark.asyncio
async def test_delete_experience(profile_client: AsyncClient):
    create = await profile_client.post(
        "/api/experience", json={"company": "Acme", "role": "Eng"}
    )
    exp_id = create.json()["id"]
    resp = await profile_client.delete(f"/api/experience/{exp_id}")
    assert resp.status_code == 204
