from enum import Enum
from typing import Optional

from src.application.domain.entity.user import User
from src.application.domain.enums.country import Country
from src.core.domain.root_entity import RootEntity


class JobStatus(Enum):
    """Enumeration for the status of a job application."""

    ADDED = "added"  # Job added to the tracker
    APPLIED = "applied"  # Application submitted
    INTERVIEWING = "interviewing"  # Interview process ongoing
    OFFERED = "offered"  # Job offer received
    REJECTED = "rejected"  # Application rejected
    ARCHIVED = "archived"  # Job archived (no further action)


class EmploymentType(Enum):
    """Enumeration for types of employment."""

    FULLTIME = "fulltime"  # Full-time employment
    TEMPORARY = "temporary"  # Temporary employment
    CONTRACT = "contract"  # Contract-based employment


class WorkSettingType(Enum):
    """Enumeration for work setting preferences."""

    REMOTE = "remote"  # Remote work
    HYBRID = "hybrid"  # Combination of remote and onsite work
    ONSITE = "onsite"  # Onsite work


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
