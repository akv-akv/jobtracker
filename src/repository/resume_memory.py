from typing import List, Optional
from uuid import UUID

from src.domain.entity.resume import Resume
from src.repository.resume_base import ResumeRepository


class InMemoryResumeRepository(ResumeRepository):
    """In-memory implementation of the ResumeRepository."""

    def __init__(self):
        self.resumes = {}

    def create(self, resume: Resume) -> None:
        if resume.id in self.resumes:
            raise ValueError(f"Resume with id {resume.id} already exists.")
        self.resumes[resume.id] = resume

    def read(self, resume_id: UUID) -> Optional[Resume]:
        return self.resumes.get(resume_id)

    def update(self, resume_id, data) -> None:
        if resume_id not in self.resumes:
            raise ValueError(f"Resume with id {resume_id} does not exist.")
        resume = self.resumes[resume_id]
        for key, value in data.items():
            if hasattr(resume, key):
                setattr(resume, key, value)

    def delete(self, resume_id: UUID) -> None:
        if resume_id not in self.resumes:
            raise ValueError(f"Resume with id {resume_id} does not exist.")
        del self.resumes[resume_id]

    def list(self, filters: Optional[dict] = None) -> List[Resume]:
        resumes = self.resumes.values()

        if filters is None:
            return list(resumes)

        if "version" in filters:
            resumes = [
                resume for resume in resumes if resume.version == filters["version"]
            ]

        if "resume_name" in filters:
            resumes = [
                resume
                for resume in resumes
                if resume.resume_name == filters["resume_name"]
            ]

        return sorted(resumes, key=lambda resume: resume.version)
