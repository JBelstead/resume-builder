from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models.experience import WorkExperience
from app.models.profile import UserProfile
from app.schemas.experience import ExperienceCreate, ExperienceResponse, ExperienceUpdate

router = APIRouter(tags=["experience"])


async def _require_profile(db: AsyncSession) -> UserProfile:
    result = await db.execute(select(UserProfile).limit(1))
    profile = result.scalar_one_or_none()
    if not profile:
        raise HTTPException(status_code=404, detail="Profile not found — create a profile first")
    return profile


@router.get("/experience", response_model=list[ExperienceResponse])
async def list_experience(db: AsyncSession = Depends(get_db)) -> list[WorkExperience]:
    profile = await _require_profile(db)
    result = await db.execute(
        select(WorkExperience)
        .where(WorkExperience.user_profile_id == profile.id)
        .order_by(WorkExperience.start_date.desc())
    )
    return list(result.scalars().all())


@router.post("/experience", response_model=ExperienceResponse, status_code=201)
async def create_experience(
    data: ExperienceCreate, db: AsyncSession = Depends(get_db)
) -> WorkExperience:
    profile = await _require_profile(db)
    entry = WorkExperience(user_profile_id=profile.id, **data.model_dump())
    db.add(entry)
    await db.commit()
    await db.refresh(entry)
    return entry


@router.put("/experience/{entry_id}", response_model=ExperienceResponse)
async def update_experience(
    entry_id: int, data: ExperienceUpdate, db: AsyncSession = Depends(get_db)
) -> WorkExperience:
    result = await db.execute(select(WorkExperience).where(WorkExperience.id == entry_id))
    entry = result.scalar_one_or_none()
    if not entry:
        raise HTTPException(status_code=404, detail="Work experience not found")
    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(entry, field, value)
    await db.commit()
    await db.refresh(entry)
    return entry


@router.delete("/experience/{entry_id}", status_code=204)
async def delete_experience(entry_id: int, db: AsyncSession = Depends(get_db)) -> None:
    result = await db.execute(select(WorkExperience).where(WorkExperience.id == entry_id))
    entry = result.scalar_one_or_none()
    if not entry:
        raise HTTPException(status_code=404, detail="Work experience not found")
    await db.delete(entry)
    await db.commit()
