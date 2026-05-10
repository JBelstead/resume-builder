from datetime import date

from pydantic import BaseModel, field_validator, model_validator


class CertificationBase(BaseModel):
    name: str
    issuer: str
    issue_date: date | None = None
    expiry_date: date | None = None
    credential_id: str | None = None
    credential_url: str | None = None

    @model_validator(mode="after")
    def expiry_after_issue(self) -> "CertificationBase":
        if self.expiry_date and self.issue_date and self.expiry_date < self.issue_date:
            raise ValueError("expiry_date must be on or after issue_date")
        return self

    @field_validator("credential_url", mode="before")
    @classmethod
    def validate_url(cls, v: str | None) -> str | None:
        if v is None or v == "":
            return None
        if not v.startswith(("http://", "https://")):
            raise ValueError("credential_url must start with http:// or https://")
        return v


class CertificationCreate(CertificationBase):
    pass


class CertificationUpdate(BaseModel):
    name: str | None = None
    issuer: str | None = None
    issue_date: date | None = None
    expiry_date: date | None = None
    credential_id: str | None = None
    credential_url: str | None = None


class CertificationResponse(CertificationBase):
    id: int
    user_profile_id: int

    model_config = {"from_attributes": True}
