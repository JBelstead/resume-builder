from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models.profile import UserProfile
from app.schemas.profile import ProfileCreate, ProfileResponse

router = APIRouter(tags=["profile"])


@router.get("/profile", response_model=ProfileResponse)
async def get_profile(db: AsyncSession = Depends(get_db)) -> UserProfile:
    result = await db.execute(select(UserProfile).limit(1))
    profile = result.scalar_one_or_none()
    if not profile:
        raise HTTPException(status_code=404, detail="Profile not found")
    return profile


@router.put("/profile", response_model=ProfileResponse)
async def upsert_profile(data: ProfileCreate, db: AsyncSession = Depends(get_db)) -> UserProfile:
    result = await db.execute(select(UserProfile).limit(1))
    profile = result.scalar_one_or_none()
    if profile:
        for field, value in data.model_dump().items():
            setattr(profile, field, value)
    else:
        profile = UserProfile(**data.model_dump())
        db.add(profile)
    await db.commit()
    await db.refresh(profile)
    return profile
