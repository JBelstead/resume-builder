from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings
from app.database import engine
from app.routers import certifications, education, experience, profile, resume


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    import asyncio

    from alembic.config import Config

    from alembic import command

    alembic_cfg = Config("alembic.ini")
    loop = asyncio.get_event_loop()
    # Run in a thread so alembic's internal asyncio.run() works without
    # conflicting with the already-running FastAPI event loop.
    await loop.run_in_executor(None, command.upgrade, alembic_cfg, "head")
    yield
    await engine.dispose()


app = FastAPI(title="Resume Builder API", version="1.0.0", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(profile.router, prefix="/api")
app.include_router(education.router, prefix="/api")
app.include_router(certifications.router, prefix="/api")
app.include_router(experience.router, prefix="/api")
app.include_router(resume.router, prefix="/api")


@app.get("/api/health")
async def health() -> dict[str, str]:
    return {"status": "ok"}
