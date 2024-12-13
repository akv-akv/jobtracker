from abc import ABC, abstractmethod
from typing import List, Optional
from uuid import UUID

from src.domain.entity.job import Job


class JobRepository(ABC):  # pragma: no cover
    """Abstract base class for a job repository."""

    @abstractmethod
    def create(self, job: Job) -> None:
        pass

    @abstractmethod
    def read(self, job_id: UUID) -> Optional[Job]:
        pass

    @abstractmethod
    def update(self, job_id, data) -> None:
        pass

    @abstractmethod
    def delete(self, job_id: UUID) -> None:
        pass

    @abstractmethod
    def list(self, filters) -> List[Job]:
        pass
