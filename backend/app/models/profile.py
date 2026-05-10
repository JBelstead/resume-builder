from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import DateTime, String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base

if TYPE_CHECKING:
    from app.models.certification import Certification
    from app.models.education import Education
    from app.models.experience import WorkExperience


class UserProfile(Base):
    __tablename__ = "user_profiles"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    email: Mapped[str | None] = mapped_column(String(255))
    phone: Mapped[str | None] = mapped_column(String(50))
    github_url: Mapped[str | None] = mapped_column(String(500))
    linkedin_url: Mapped[str | None] = mapped_column(String(500))
    website_url: Mapped[str | None] = mapped_column(String(500))
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now(), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, server_default=func.now(), onupdate=func.now(), nullable=False
    )

    educations: Mapped[list[Education]] = relationship(
        "Education", back_populates="profile", cascade="all, delete-orphan"
    )
    certifications: Mapped[list[Certification]] = relationship(
        "Certification", back_populates="profile", cascade="all, delete-orphan"
    )
    experiences: Mapped[list[WorkExperience]] = relationship(
        "WorkExperience", back_populates="profile", cascade="all, delete-orphan"
    )
