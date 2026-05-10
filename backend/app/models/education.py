from datetime import date

from sqlalchemy import Date, ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class Education(Base):
    __tablename__ = "educations"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_profile_id: Mapped[int] = mapped_column(ForeignKey("user_profiles.id"), nullable=False)
    institution: Mapped[str] = mapped_column(String(255), nullable=False)
    degree: Mapped[str] = mapped_column(String(255), nullable=False)
    field_of_study: Mapped[str | None] = mapped_column(String(255))
    start_date: Mapped[date] = mapped_column(Date, nullable=False)
    end_date: Mapped[date | None] = mapped_column(Date)
    gpa: Mapped[str | None] = mapped_column(String(20))
    description: Mapped[str | None] = mapped_column(Text)

    profile: Mapped["UserProfile"] = relationship("UserProfile", back_populates="educations")  # noqa: F821
