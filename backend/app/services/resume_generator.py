"""Orchestrates LLM call → Jinja2 render → WeasyPrint PDF."""

import json
import os
from pathlib import Path

from jinja2 import Environment, FileSystemLoader, select_autoescape
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from weasyprint import HTML

from app.config import settings
from app.models.certification import Certification
from app.models.education import Education
from app.models.experience import WorkExperience
from app.models.profile import UserProfile
from app.models.resume import Resume
from app.services.llm import LLMService

_SYSTEM_PROMPT = """You are a professional resume writer. Given a candidate's full profile
and a job description, tailor the most relevant content for the role.
Respond ONLY with valid JSON matching this exact schema — no extra text:
{
  "summary": "<2-3 sentence professional summary tailored to this job>",
  "skills_to_emphasize": ["skill1", "skill2", "..."],
  "experience_highlights": ["<top achievement/responsibility relevant to this job>", "..."],
  "job_title": "<inferred job title from description or empty string>",
  "company_name": "<inferred company name from description or empty string>"
}"""


class ResumeBuildError(Exception):
    pass


class ResumeGenerator:
    def __init__(self, db: AsyncSession) -> None:
        self._db = db
        self._llm = LLMService()
        templates_dir = Path(__file__).parent.parent / "templates"
        self._jinja_env = Environment(
            loader=FileSystemLoader(str(templates_dir)),
            autoescape=select_autoescape(["html"]),
        )

    async def generate(
        self,
        job_description: str,
        job_description_url: str | None = None,
    ) -> Resume:
        profile, educations, certifications, experiences = await self._load_profile()
        llm_data = await self._call_llm(profile, educations, certifications, experiences, job_description)
        html_content = self._render_template(profile, educations, certifications, experiences, llm_data)

        # Persist resume record first to get the ID for file paths
        resume = Resume(
            job_title=llm_data.get("job_title") or None,
            company_name=llm_data.get("company_name") or None,
            job_description_text=job_description,
            job_description_url=job_description_url,
            llm_output=json.dumps(llm_data),
        )
        self._db.add(resume)
        await self._db.flush()  # get resume.id without committing

        pdf_path, html_path = self._save_files(resume.id, html_content)
        resume.pdf_path = pdf_path
        resume.html_path = html_path
        await self._db.commit()
        await self._db.refresh(resume)
        return resume

    async def _load_profile(
        self,
    ) -> tuple[UserProfile, list[Education], list[Certification], list[WorkExperience]]:
        result = await self._db.execute(select(UserProfile).limit(1))
        profile = result.scalar_one_or_none()
        if not profile:
            raise ResumeBuildError("no_profile")

        educations = list(
            (await self._db.execute(
                select(Education).where(Education.user_profile_id == profile.id).order_by(Education.start_date.desc())
            )).scalars().all()
        )
        certifications = list(
            (await self._db.execute(
                select(Certification).where(Certification.user_profile_id == profile.id).order_by(Certification.issue_date.desc())
            )).scalars().all()
        )
        experiences = list(
            (await self._db.execute(
                select(WorkExperience).where(WorkExperience.user_profile_id == profile.id).order_by(WorkExperience.start_date.desc())
            )).scalars().all()
        )
        return profile, educations, certifications, experiences

    async def _call_llm(
        self,
        profile: UserProfile,
        educations: list[Education],
        certifications: list[Certification],
        experiences: list[WorkExperience],
        job_description: str,
    ) -> dict[str, object]:
        profile_data = {
            "name": profile.name,
            "experience": [
                {
                    "company": e.company,
                    "role": e.role,
                    "description": e.description or "",
                    "skills": e.skills or "",
                }
                for e in experiences
            ],
            "education": [
                {"institution": ed.institution, "degree": ed.degree, "field": ed.field_of_study or ""}
                for ed in educations
            ],
            "certifications": [
                {"name": c.name, "issuer": c.issuer} for c in certifications
            ],
        }
        user_message = (
            f"--- PROFILE ---\n{json.dumps(profile_data, indent=2)}\n\n"
            f"--- JOB DESCRIPTION ---\n{job_description}"
        )
        raw = await self._llm.generate(_SYSTEM_PROMPT, user_message)
        try:
            data = json.loads(raw)
        except json.JSONDecodeError as exc:
            raise ResumeBuildError(f"LLM returned non-JSON output: {raw[:200]}") from exc
        if not isinstance(data, dict):
            raise ResumeBuildError("LLM output was not a JSON object")
        return data

    def _render_template(
        self,
        profile: UserProfile,
        educations: list[Education],
        certifications: list[Certification],
        experiences: list[WorkExperience],
        llm_data: dict[str, object],
    ) -> str:
        template = self._jinja_env.get_template("resume.html.j2")
        return template.render(
            profile=profile,
            educations=educations,
            certifications=certifications,
            experiences=experiences,
            summary=llm_data.get("summary", ""),
            skills=llm_data.get("skills_to_emphasize", []),
            experience_highlights=llm_data.get("experience_highlights", []),
        )

    def _save_files(self, resume_id: int, html_content: str) -> tuple[str, str]:
        output_dir = Path(settings.resume_output_dir) / str(resume_id)
        output_dir.mkdir(parents=True, exist_ok=True)
        html_path = str(output_dir / "resume.html")
        pdf_path = str(output_dir / "resume.pdf")
        with open(html_path, "w", encoding="utf-8") as f:
            f.write(html_content)
        HTML(string=html_content).write_pdf(pdf_path)
        return pdf_path, html_path
