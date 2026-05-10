from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models.education import Education
from app.models.profile import UserProfile
from app.schemas.education import EducationCreate, EducationResponse, EducationUpdate

router = APIRouter(tags=["education"])


async def _require_profile(db: AsyncSession) -> UserProfile:
    result = await db.execute(select(UserProfile).limit(1))
    profile = result.scalar_one_or_none()
    if not profile:
        raise HTTPException(status_code=404, detail="Profile not found — create a profile first")
    return profile


@router.get("/education", response_model=list[EducationResponse])
async def list_education(db: AsyncSession = Depends(get_db)) -> list[Education]:
    profile = await _require_profile(db)
    result = await db.execute(
        select(Education).where(Education.user_profile_id == profile.id).order_by(Education.start_date.desc())
    )
    return list(result.scalars().all())


@router.post("/education", response_model=EducationResponse, status_code=201)
async def create_education(data: EducationCreate, db: AsyncSession = Depends(get_db)) -> Education:
    profile = await _require_profile(db)
    entry = Education(user_profile_id=profile.id, **data.model_dump())
    db.add(entry)
    await db.commit()
    await db.refresh(entry)
    return entry


@router.put("/education/{entry_id}", response_model=EducationResponse)
async def update_education(entry_id: int, data: EducationUpdate, db: AsyncSession = Depends(get_db)) -> Education:
    result = await db.execute(select(Education).where(Education.id == entry_id))
    entry = result.scalar_one_or_none()
    if not entry:
        raise HTTPException(status_code=404, detail="Education entry not found")
    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(entry, field, value)
    await db.commit()
    await db.refresh(entry)
    return entry


@router.delete("/education/{entry_id}", status_code=204)
async def delete_education(entry_id: int, db: AsyncSession = Depends(get_db)) -> None:
    result = await db.execute(select(Education).where(Education.id == entry_id))
    entry = result.scalar_one_or_none()
    if not entry:
        raise HTTPException(status_code=404, detail="Education entry not found")
    await db.delete(entry)
    await db.commit()
