from typing import List, Optional
from uuid import UUID

from src.core.domain.root_entity import RootEntity


class ResumeMainInfo(RootEntity):
    user_id: UUID
    resume_main_info_id: UUID
    experience_ids: List[UUID]
    version_name: Optional[str]
