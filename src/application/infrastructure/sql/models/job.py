from datetime import datetime
from uuid import uuid4

from sqlalchemy import Column, DateTime, Enum, ForeignKey, MetaData, String, Table, Text
from sqlalchemy.dialects.postgresql import UUID

from src.application.domain.entity.job import EmploymentType, JobStatus, WorkSettingType
from src.application.domain.enums.country import Country

job_metadata = MetaData()

job_table = Table(
    "jobs",
    job_metadata,
    Column("id", UUID(as_uuid=True), primary_key=True, default=uuid4),
    Column("user_id", UUID(as_uuid=True), ForeignKey("users.id"), nullable=False),
    Column("title", String, nullable=False),
    Column("company", String, nullable=False),
    Column("description", Text, nullable=False),
    Column("country", Enum(Country), nullable=True),
    Column("city", String, nullable=False),
    Column("work_setting_type", Enum(WorkSettingType), nullable=True),
    Column("status", Enum(JobStatus), nullable=False),
    Column("employment_type", Enum(EmploymentType), nullable=True),
    Column("notes", Text, nullable=True),
    Column("external_id", String, nullable=True),
    Column("platform", String, nullable=True),
    Column("url", String, nullable=True),
    Column(
        "created_at", DateTime(timezone=True), nullable=False, default=datetime.utcnow
    ),
    Column("updated_at", DateTime(timezone=True), nullable=True),
)
