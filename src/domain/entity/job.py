from dataclasses import dataclass
from enum import Enum, auto
from typing import Optional

from src.domain.base.root_entity import RootEntity
from src.domain.entity.user import User
from src.domain.enums.country import Country


class JobStatus(Enum):
    ADDED = auto()
    APPLIED = auto()
    INTERVIEWING = auto()
    OFFERED = auto()
    REJECTED = auto()
    ARCHIVED = auto()


class EmploymentType(Enum):
    FULLTIME = auto()
    TEMPORARY = auto()
    CONTRACT = auto()


class WorkSettingType(Enum):
    REMOTE = auto()
    HYBRID = auto()
    ONSITE = auto()


@dataclass(frozen=True)
class Job(RootEntity):
    user: User
    title: str
    company: str
    description: str
    country: Country
    city: str
    work_setting_type: Optional[WorkSettingType]
    status: JobStatus = JobStatus.ADDED
    employment_type: Optional[EmploymentType] = EmploymentType.FULLTIME
    notes: Optional[str] = None
    external_id: Optional[str] = None
    platform: Optional[str] = None
    url: Optional[str] = None
