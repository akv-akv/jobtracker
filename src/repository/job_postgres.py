from typing import List, Optional, Type
from uuid import uuid4

from sqlalchemy import Column, Date, Enum, String, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.ext.declarative import DeclarativeMeta
from sqlalchemy.orm import Session, declarative_base

from src.domain.entity.job import Job, JobStatus
from src.repository.base_postgres import BasePostgresRepository

Base: Type[DeclarativeMeta] = declarative_base()


class JobSQLModel(Base):
    __tablename__ = "jobs"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    title = Column(String(100), nullable=False)
    company = Column(String(100), nullable=False)
    status = Column(Enum(JobStatus), nullable=False)
    country = Column(String(50))
    city = Column(String(50))
    description = Column(Text)
    notes = Column(Text, nullable=True)
    external_id = Column(String(250), nullable=True)
    platform = Column(String(250), nullable=True)
    date_applied = Column(Date)
    date_updated = Column(Date)

    @classmethod
    def from_domain(cls, job: Job):
        """Convert a Job domain object to a SQLAlchemy ORM object."""
        return cls(
            id=job.id,
            title=job.title,
            company=job.company,
            status=job.status,
            country=job.country,
            city=job.city,
            description=job.description,
            notes=job.notes,
            external_id=job.external_id,
            platform=job.platform,
            date_applied=job.date_applied,
            date_updated=job.date_updated,
        )

    def to_domain(self) -> Job:
        """Convert a SQLAlchemy ORM object to a Job domain object."""
        return Job(
            id=self.id,
            title=self.title,
            company=self.company,
            status=self.status,
            country=self.country,
            city=self.city,
            description=self.description,
            notes=self.notes,
            external_id=self.external_id,
            platform=self.platform,
            date_applied=self.date_applied,
            date_updated=self.date_updated,
        )


class JobRepositoryPostgres(BasePostgresRepository[JobSQLModel, Job]):
    """PostgreSQL repository for managing Job entities."""

    def __init__(self, session: Session):
        super().__init__(
            session=session,
            model=JobSQLModel,
            to_domain=lambda orm_obj: orm_obj.to_domain(),
            from_domain=lambda domain_obj: JobSQLModel.from_domain(domain_obj),
        )

    def list(self, filters: Optional[dict] = None) -> List[Job]:
        """List jobs with optional filters."""
        query = self.session.query(self.model)
        if filters:
            if "status" in filters:
                query = query.filter(self.model.status.in_(filters["status"]))
            if "company" in filters:
                query = query.filter(self.model.company == filters["company"])
            if "country" in filters:
                query = query.filter(self.model.country == filters["country"])
            if "city" in filters:
                query = query.filter(self.model.city == filters["city"])
            if "date_applied__gt" in filters:
                query = query.filter(
                    self.model.date_applied >= filters["date_applied__gt"]
                )
            if "date_applied__lt" in filters:
                query = query.filter(
                    self.model.date_applied <= filters["date_applied__lt"]
                )
        return [job_sql.to_domain() for job_sql in query.all()]
