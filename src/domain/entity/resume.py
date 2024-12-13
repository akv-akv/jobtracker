from dataclasses import dataclass, field
from datetime import date
from typing import List, Optional
from uuid import UUID


@dataclass
class Experience:
    id: UUID
    employer: str
    position: str
    start_date: date
    description: List[str] = field(default_factory=list)
    employer_details: Optional[str] = None
    employer_website: Optional[str] = None
    job_location: Optional[str] = None
    end_date: Optional[date] = None


@dataclass
class Resume:
    id: UUID
    name: str
    summary: str
    skills: List[str] = field(default_factory=list)
    location: Optional[str] = None
    phone: Optional[str] = None
    email: Optional[str] = None
    linkedin: Optional[str] = None
    version: int = 1
    parent_id: Optional[UUID] = None
    experiences: List[Experience] = field(default_factory=list)
