from typing import List, Optional
from uuid import UUID

from src.core.domain.root_entity import RootEntity


class ResumeMainInfo(RootEntity):
    user_id: UUID
    applicant_name: str
    skills: List[str] = []
    summary: Optional[str] = None
    location: Optional[str] = None
    phone: Optional[str] = None
    email: Optional[str] = None
    linkedin: Optional[str] = None
    parent_id: Optional[UUID] = None
    resume_name: Optional[str] = None
