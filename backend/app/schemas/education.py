from datetime import date

from pydantic import BaseModel, model_validator


class EducationBase(BaseModel):
    institution: str
    degree: str
    field_of_study: str | None = None
    start_date: date | None = None
    end_date: date | None = None
    gpa: str | None = None
    description: str | None = None

    @model_validator(mode="after")
    def end_after_start(self) -> "EducationBase":
        if self.end_date and self.start_date and self.end_date < self.start_date:
            raise ValueError("end_date must be on or after start_date")
        return self


class EducationCreate(EducationBase):
    pass


class EducationUpdate(BaseModel):
    institution: str | None = None
    degree: str | None = None
    field_of_study: str | None = None
    start_date: date | None = None
    end_date: date | None = None
    gpa: str | None = None
    description: str | None = None


class EducationResponse(EducationBase):
    id: int
    user_profile_id: int

    model_config = {"from_attributes": True}
