from datetime import datetime

from pydantic import BaseModel, model_validator


class ResumeGenerateRequest(BaseModel):
    job_description_text: str | None = None
    job_description_url: str | None = None

    @model_validator(mode="after")
    def at_least_one(self) -> "ResumeGenerateRequest":
        if not self.job_description_text and not self.job_description_url:
            raise ValueError("Provide either job_description_text or job_description_url")
        # Text takes precedence; clear URL if both provided
        if self.job_description_text and self.job_description_url:
            self.job_description_url = None
        return self


class ResumeListItem(BaseModel):
    id: int
    job_title: str | None
    company_name: str | None
    job_description_url: str | None
    created_at: datetime

    model_config = {"from_attributes": True}


class ResumeResponse(ResumeListItem):
    job_description_text: str | None
    llm_output: str
    pdf_path: str | None
    html_path: str | None

    model_config = {"from_attributes": True}


class ResumeCreateResponse(BaseModel):
    id: int
    job_title: str | None
    company_name: str | None
    job_description_url: str | None
    pdf_path: str | None
    html_path: str | None
    created_at: datetime

    model_config = {"from_attributes": True}
