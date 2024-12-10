from datetime import datetime
from typing import List, Optional
from uuid import UUID

from src.domain.entity.job import Job
from src.repository.job_base import JobRepository


class InMemoryJobRepository(JobRepository):
    """In-memory implementation of the JobRepository."""

    def __init__(self):
        self.jobs = {}

    def create(self, job: Job) -> None:
        if job.id in self.jobs:
            raise ValueError(f"Job with id {job.id} already exists.")
        self.jobs[job.id] = job

    def read(self, job_id: UUID) -> Optional[Job]:
        return self.jobs.get(job_id)

    def update(self, job: Job) -> None:
        if job.id not in self.jobs:
            raise ValueError(f"Job with id {job.id} does not exist.")
        self.jobs[job.id] = job

    def delete(self, job_id: UUID) -> None:
        if job_id not in self.jobs:
            raise ValueError(f"Job with id {job_id} does not exist.")
        del self.jobs[job_id]

    def list(self, filters: Optional[dict] = None) -> List[Job]:
        jobs = self.jobs.values()

        if filters is None:
            return list(jobs)

        if "status" in filters:
            jobs = [job for job in jobs if job.status in filters["status"]]

        if "company" in filters:
            jobs = [job for job in jobs if job.company == filters["company"]]

        if "country" in filters:
            jobs = [job for job in jobs if job.country == filters["country"]]

        if "city" in filters:
            jobs = [job for job in jobs if job.city == filters["city"]]

        # Apply date filters using the helper function
        jobs = self._apply_date_filters(jobs, filters, "date_applied")
        jobs = self._apply_date_filters(jobs, filters, "date_updated")

        return list(jobs)

    def _apply_date_filters(
        self, jobs: List[Job], filters: dict, date_field: str
    ) -> List[Job]:
        """
        Apply date filters (__eq, __gt, __lt) to
        the given list of jobs based on the specified field.
        """
        date_eq = filters.get(f"{date_field}__eq")
        date_gt = filters.get(f"{date_field}__gt")
        date_lt = filters.get(f"{date_field}__lt")

        if date_eq:
            date_eq = datetime.strptime(date_eq, "%Y-%m-%d")
            jobs = [job for job in jobs if getattr(job, date_field) == date_eq]

        if date_gt:
            date_gt = datetime.strptime(date_gt, "%Y-%m-%d")
            jobs = [job for job in jobs if getattr(job, date_field) >= date_gt]

        if date_lt:
            date_lt = datetime.strptime(date_lt, "%Y-%m-%d")
            jobs = [job for job in jobs if getattr(job, date_field) <= date_lt]

        return jobs
