from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models.certification import Certification
from app.models.profile import UserProfile
from app.schemas.certification import CertificationCreate, CertificationResponse, CertificationUpdate

router = APIRouter(tags=["certifications"])


async def _require_profile(db: AsyncSession) -> UserProfile:
    result = await db.execute(select(UserProfile).limit(1))
    profile = result.scalar_one_or_none()
    if not profile:
        raise HTTPException(status_code=404, detail="Profile not found — create a profile first")
    return profile


@router.get("/certifications", response_model=list[CertificationResponse])
async def list_certifications(db: AsyncSession = Depends(get_db)) -> list[Certification]:
    profile = await _require_profile(db)
    result = await db.execute(
        select(Certification)
        .where(Certification.user_profile_id == profile.id)
        .order_by(Certification.issue_date.desc())
    )
    return list(result.scalars().all())


@router.post("/certifications", response_model=CertificationResponse, status_code=201)
async def create_certification(
    data: CertificationCreate, db: AsyncSession = Depends(get_db)
) -> Certification:
    profile = await _require_profile(db)
    entry = Certification(user_profile_id=profile.id, **data.model_dump())
    db.add(entry)
    await db.commit()
    await db.refresh(entry)
    return entry


@router.put("/certifications/{entry_id}", response_model=CertificationResponse)
async def update_certification(
    entry_id: int, data: CertificationUpdate, db: AsyncSession = Depends(get_db)
) -> Certification:
    result = await db.execute(select(Certification).where(Certification.id == entry_id))
    entry = result.scalar_one_or_none()
    if not entry:
        raise HTTPException(status_code=404, detail="Certification not found")
    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(entry, field, value)
    await db.commit()
    await db.refresh(entry)
    return entry


@router.delete("/certifications/{entry_id}", status_code=204)
async def delete_certification(entry_id: int, db: AsyncSession = Depends(get_db)) -> None:
    result = await db.execute(select(Certification).where(Certification.id == entry_id))
    entry = result.scalar_one_or_none()
    if not entry:
        raise HTTPException(status_code=404, detail="Certification not found")
    await db.delete(entry)
    await db.commit()
