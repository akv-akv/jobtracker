from dataclasses import dataclass
from datetime import date
from enum import Enum, auto
from typing import Optional
from uuid import UUID


class JobStatus(Enum):
    APPLIED = auto()
    INTERVIEWING = auto()
    OFFERED = auto()
    REJECTED = auto()


@dataclass
class Job:
    id: UUID
    title: str
    company: str
    status: JobStatus
    country: str
    city: str
    description: str
    notes: Optional[str] = None
    external_id: Optional[str] = None
    platform: Optional[str] = None
    date_applied: date = date.today()
    date_updated: date = date.today()
