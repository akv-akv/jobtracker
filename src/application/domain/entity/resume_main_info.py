from typing import List, Optional
from uuid import UUID

from src.core.domain.versioned_root_entity import VersionedRootEntity


class ResumeMainInfo(VersionedRootEntity):
    user_id: UUID
    title: str
    applicant_name: str
    summary: Optional[str] = None
    skills: List[str] = []
    location: Optional[str] = None
    phone: Optional[str] = None
    email: Optional[str] = None
    linkedin: Optional[str] = None
    parent_id: Optional[UUID] = None
    resume_name: Optional[str] = None
