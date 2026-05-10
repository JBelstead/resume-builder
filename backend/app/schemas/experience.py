from datetime import date

from pydantic import BaseModel, model_validator


class ExperienceBase(BaseModel):
    company: str
    role: str
    start_date: date | None = None
    end_date: date | None = None
    location: str | None = None
    description: str | None = None
    skills: str | None = None

    @model_validator(mode="after")
    def end_after_start(self) -> "ExperienceBase":
        if self.end_date and self.start_date and self.end_date < self.start_date:
            raise ValueError("end_date must be on or after start_date")
        return self


class ExperienceCreate(ExperienceBase):
    pass


class ExperienceUpdate(BaseModel):
    company: str | None = None
    role: str | None = None
    start_date: date | None = None
    end_date: date | None = None
    location: str | None = None
    description: str | None = None
    skills: str | None = None


class ExperienceResponse(ExperienceBase):
    id: int
    user_profile_id: int

    model_config = {"from_attributes": True}
