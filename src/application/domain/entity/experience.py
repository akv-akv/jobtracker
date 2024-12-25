from datetime import date
from typing import List, Optional
from uuid import UUID

from src.core.domain.root_entity import RootEntity


class Experience(RootEntity):
    user_id: UUID
    job_title: str
    company_name: str
    start_date: date
    end_date: Optional[date]
    location: Optional[str]
    company_description: Optional[str]
    bullet_points: Optional[List[str]]
