"""Unit tests for profile, education, certification, and experience routers."""

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


@pytest.fixture
async def with_profile(client: AsyncClient):
    await client.put("/api/profile", json={"name": "Test User"})
    return client


# ─── Profile router ───────────────────────────────────────────────────────────

@pytest.mark.asyncio
async def test_health(client: AsyncClient):
    resp = await client.get("/api/health")
    assert resp.status_code == 200
    assert resp.json() == {"status": "ok"}


@pytest.mark.asyncio
async def test_profile_not_found(client: AsyncClient):
    assert (await client.get("/api/profile")).status_code == 404


@pytest.mark.asyncio
async def test_profile_upsert(client: AsyncClient):
    resp = await client.put("/api/profile", json={"name": "Alice"})
    assert resp.status_code == 200
    first_id = resp.json()["id"]

    resp2 = await client.put("/api/profile", json={"name": "Alice B"})
    assert resp2.status_code == 200
    assert resp2.json()["id"] == first_id  # same record updated


# ─── Education router ─────────────────────────────────────────────────────────

@pytest.mark.asyncio
async def test_education_crud(with_profile: AsyncClient):
    c = with_profile
    post = await c.post("/api/education", json={"institution": "MIT", "degree": "BSc"})
    assert post.status_code == 201
    eid = post.json()["id"]

    assert (await c.put(f"/api/education/{eid}", json={"degree": "PhD"})).json()["degree"] == "PhD"
    assert (await c.delete(f"/api/education/{eid}")).status_code == 204
    assert all(e["id"] != eid for e in (await c.get("/api/education")).json())


# ─── Certifications router ────────────────────────────────────────────────────

@pytest.mark.asyncio
async def test_certification_crud(with_profile: AsyncClient):
    c = with_profile
    post = await c.post("/api/certifications", json={"name": "AWS SAA", "issuer": "Amazon"})
    assert post.status_code == 201
    cid = post.json()["id"]

    assert (await c.put(f"/api/certifications/{cid}", json={"name": "AWS SAP"})).json()["name"] == "AWS SAP"
    assert (await c.delete(f"/api/certifications/{cid}")).status_code == 204


# ─── Experience router ────────────────────────────────────────────────────────

@pytest.mark.asyncio
async def test_experience_crud(with_profile: AsyncClient):
    c = with_profile
    post = await c.post("/api/experience", json={"company": "Acme", "role": "Eng"})
    assert post.status_code == 201
    xid = post.json()["id"]

    assert (await c.put(f"/api/experience/{xid}", json={"role": "Lead"})).json()["role"] == "Lead"
    assert (await c.delete(f"/api/experience/{xid}")).status_code == 204
