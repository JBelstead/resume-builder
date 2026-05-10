import shutil
from pathlib import Path

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import FileResponse
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models.profile import UserProfile
from app.models.resume import Resume
from app.schemas.resume import ResumeCreateResponse, ResumeGenerateRequest, ResumeListItem, ResumeResponse
from app.services.job_parser import JobParser, JobURLError
from app.services.llm import LLMTimeoutError, LLMUnavailableError
from app.services.resume_generator import ResumeBuildError, ResumeGenerator

router = APIRouter(tags=["resume"])


@router.post("/resume/generate", response_model=ResumeCreateResponse, status_code=201)
async def generate_resume(
    data: ResumeGenerateRequest, db: AsyncSession = Depends(get_db)
) -> Resume:
    result = await db.execute(select(UserProfile).limit(1))
    if not result.scalar_one_or_none():
        raise HTTPException(
            status_code=400,
            detail="Complete your profile before generating a resume",
        )

    job_description = data.job_description_text or ""
    job_description_url: str | None = None

    if data.job_description_url and not data.job_description_text:
        job_description_url = str(data.job_description_url)
        try:
            job_description = await JobParser().fetch(job_description_url)
        except JobURLError as exc:
            raise HTTPException(status_code=422, detail=str(exc)) from exc
    elif data.job_description_text:
        if data.job_description_url:
            job_description_url = str(data.job_description_url)

    generator = ResumeGenerator(db)
    try:
        resume = await generator.generate(
            job_description=job_description,
            job_description_url=job_description_url,
        )
    except ResumeBuildError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc
    except LLMTimeoutError as exc:
        raise HTTPException(status_code=504, detail="LLM timed out; try again later") from exc
    except LLMUnavailableError as exc:
        raise HTTPException(status_code=502, detail="LLM service unavailable") from exc

    return resume


@router.get("/resume", response_model=list[ResumeListItem])
async def list_resumes(db: AsyncSession = Depends(get_db)) -> list[Resume]:
    result = await db.execute(select(Resume).order_by(Resume.created_at.desc()))
    return list(result.scalars().all())


@router.get("/resume/{resume_id}", response_model=ResumeResponse)
async def get_resume(resume_id: int, db: AsyncSession = Depends(get_db)) -> Resume:
    result = await db.execute(select(Resume).where(Resume.id == resume_id))
    resume = result.scalar_one_or_none()
    if not resume:
        raise HTTPException(status_code=404, detail="Resume not found")
    return resume


@router.get("/resume/{resume_id}/download")
async def download_resume(resume_id: int, db: AsyncSession = Depends(get_db)) -> FileResponse:
    result = await db.execute(select(Resume).where(Resume.id == resume_id))
    resume = result.scalar_one_or_none()
    if not resume:
        raise HTTPException(status_code=404, detail="Resume not found")
    if not resume.pdf_path or not Path(resume.pdf_path).exists():
        raise HTTPException(status_code=404, detail="PDF file not found on disk")
    filename = f"resume_{resume_id}.pdf"
    return FileResponse(
        path=resume.pdf_path,
        media_type="application/pdf",
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
    )


@router.delete("/resume/{resume_id}", status_code=204)
async def delete_resume(resume_id: int, db: AsyncSession = Depends(get_db)) -> None:
    result = await db.execute(select(Resume).where(Resume.id == resume_id))
    resume = result.scalar_one_or_none()
    if not resume:
        raise HTTPException(status_code=404, detail="Resume not found")
    if resume.pdf_path:
        resume_dir = Path(resume.pdf_path).parent
        if resume_dir.exists():
            shutil.rmtree(resume_dir)
    await db.delete(resume)
    await db.commit()
