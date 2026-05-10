from datetime import datetime

from pydantic import BaseModel, field_validator


class ProfileBase(BaseModel):
    name: str
    email: str | None = None
    phone: str | None = None
    github_url: str | None = None
    linkedin_url: str | None = None
    website_url: str | None = None

    @field_validator("name")
    @classmethod
    def name_not_empty(cls, v: str) -> str:
        if not v.strip():
            raise ValueError("name must not be empty")
        return v.strip()

    @field_validator("github_url", "linkedin_url", "website_url", mode="before")
    @classmethod
    def validate_url(cls, v: str | None) -> str | None:
        if v is None or v == "":
            return None
        if not v.startswith(("http://", "https://")):
            raise ValueError("URL must start with http:// or https://")
        return v


class ProfileCreate(ProfileBase):
    pass


class ProfileResponse(ProfileBase):
    id: int
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}
