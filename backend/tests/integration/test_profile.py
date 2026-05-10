"""Integration tests: full profile CRUD lifecycle."""

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
    async def override():
        yield session

    app.dependency_overrides[get_db] = override
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as c:
        yield c
    app.dependency_overrides.clear()


@pytest.mark.asyncio
async def test_full_profile_lifecycle(client: AsyncClient):
    # Create
    resp = await client.put("/api/profile", json={"name": "Alice"})
    assert resp.status_code == 200
    assert resp.json()["name"] == "Alice"

    # Read
    resp = await client.get("/api/profile")
    assert resp.status_code == 200
    assert resp.json()["name"] == "Alice"

    # Update
    resp = await client.put("/api/profile", json={"name": "Alice Updated"})
    assert resp.json()["name"] == "Alice Updated"

    # Only one profile exists
    resp = await client.get("/api/profile")
    assert resp.json()["name"] == "Alice Updated"


@pytest.mark.asyncio
async def test_full_education_lifecycle(client: AsyncClient):
    await client.put("/api/profile", json={"name": "Alice"})

    # Create
    resp = await client.post("/api/education", json={"institution": "MIT", "degree": "BSc"})
    assert resp.status_code == 201
    edu_id = resp.json()["id"]

    # List
    resp = await client.get("/api/education")
    assert any(e["id"] == edu_id for e in resp.json())

    # Update
    resp = await client.put(f"/api/education/{edu_id}", json={"degree": "MSc"})
    assert resp.json()["degree"] == "MSc"

    # Delete
    resp = await client.delete(f"/api/education/{edu_id}")
    assert resp.status_code == 204
    resp = await client.get("/api/education")
    assert all(e["id"] != edu_id for e in resp.json())


@pytest.mark.asyncio
async def test_full_certification_lifecycle(client: AsyncClient):
    await client.put("/api/profile", json={"name": "Alice"})

    resp = await client.post(
        "/api/certifications",
        json={"name": "AWS SAA", "issuer": "Amazon"},
    )
    assert resp.status_code == 201
    cert_id = resp.json()["id"]

    resp = await client.put(f"/api/certifications/{cert_id}", json={"name": "AWS SAP"})
    assert resp.json()["name"] == "AWS SAP"

    resp = await client.delete(f"/api/certifications/{cert_id}")
    assert resp.status_code == 204


@pytest.mark.asyncio
async def test_full_experience_lifecycle(client: AsyncClient):
    await client.put("/api/profile", json={"name": "Alice"})

    resp = await client.post(
        "/api/experience",
        json={"company": "Acme", "role": "Engineer", "start_date": "2020-01-01"},
    )
    assert resp.status_code == 201
    exp_id = resp.json()["id"]

    resp = await client.put(f"/api/experience/{exp_id}", json={"role": "Senior Engineer"})
    assert resp.json()["role"] == "Senior Engineer"

    resp = await client.delete(f"/api/experience/{exp_id}")
    assert resp.status_code == 204
