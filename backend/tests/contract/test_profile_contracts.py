"""Contract tests for GET /profile and PUT /profile endpoints."""

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


@pytest.mark.asyncio
async def test_get_profile_returns_404_when_none(client: AsyncClient):
    resp = await client.get("/api/profile")
    assert resp.status_code == 404


@pytest.mark.asyncio
async def test_put_profile_creates_profile(client: AsyncClient):
    resp = await client.put("/api/profile", json={"name": "Jane Smith"})
    assert resp.status_code == 200
    body = resp.json()
    assert body["name"] == "Jane Smith"
    assert "id" in body


@pytest.mark.asyncio
async def test_put_profile_updates_existing(client: AsyncClient):
    await client.put("/api/profile", json={"name": "Jane Smith"})
    resp = await client.put(
        "/api/profile",
        json={"name": "Jane Updated", "email": "jane@example.com"},
    )
    assert resp.status_code == 200
    assert resp.json()["name"] == "Jane Updated"


@pytest.mark.asyncio
async def test_get_profile_returns_profile_after_creation(client: AsyncClient):
    await client.put("/api/profile", json={"name": "Alice"})
    resp = await client.get("/api/profile")
    assert resp.status_code == 200
    assert resp.json()["name"] == "Alice"


@pytest.mark.asyncio
async def test_put_profile_rejects_empty_name(client: AsyncClient):
    resp = await client.put("/api/profile", json={"name": ""})
    assert resp.status_code == 422


@pytest.mark.asyncio
async def test_put_profile_rejects_invalid_url(client: AsyncClient):
    resp = await client.put("/api/profile", json={"name": "Bob", "github_url": "not-a-url"})
    assert resp.status_code == 422


@pytest.mark.asyncio
async def test_put_profile_accepts_all_optional_fields(client: AsyncClient):
    payload = {
        "name": "Bob",
        "email": "bob@example.com",
        "phone": "+1 555 000 0000",
        "github_url": "https://github.com/bob",
        "linkedin_url": "https://linkedin.com/in/bob",
        "website_url": "https://bob.dev",
    }
    resp = await client.put("/api/profile", json=payload)
    assert resp.status_code == 200
    body = resp.json()
    assert body["github_url"] == "https://github.com/bob"
