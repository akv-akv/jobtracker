from abc import ABC, abstractmethod
from typing import List, Optional
from uuid import UUID

from src.domain.entity.resume import Resume


class ResumeRepository(ABC):  # pragma: no cover
    """Abstract base class for a resume repository."""

    @abstractmethod
    def create(self, resume: Resume) -> None:
        pass

    @abstractmethod
    def read(self, resume_id: UUID) -> Optional[Resume]:
        pass

    @abstractmethod
    def update(self, resume_id, data) -> None:
        pass

    @abstractmethod
    def delete(self, resume_id: UUID) -> None:
        pass

    @abstractmethod
    def list(self, filters) -> List[Resume]:
        pass
