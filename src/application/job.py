from datetime import datetime
from typing import Any, Dict
from uuid import uuid4

from sqlalchemy import Column, DateTime, Enum, ForeignKey, MetaData, String, Table, Text
from sqlalchemy.dialects.postgresql import UUID

from manage import get_database_url
from src.application.domain.entity.job import (
    EmploymentType,
    Job,
    JobStatus,
    WorkSettingType,
)
from src.application.domain.enums.country import Country
from src.application.user import manage_user
from src.core.manage import Manage
from src.core.repository.base.mapper import Mapper
from src.core.repository.base.repository import Repository
from src.core.repository.sql.asyncpg_sql_database import AsyncpgSQLDatabase
from src.core.repository.sql.sql_gateway import SQLGateway

metadata = MetaData()

# Jobs Table
job_table = Table(
    "jobs",
    metadata,
    Column("id", UUID(as_uuid=True), primary_key=True, default=uuid4),
    Column("user_id", UUID(as_uuid=True), ForeignKey("users.id"), nullable=False),
    Column("title", String, nullable=False),
    Column("company", String, nullable=False),
    Column("description", Text, nullable=False),
    Column("country", Enum(Country)),
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


class ManageJob(Manage[Job]):
    pass


class JobRepository(Repository[Job]):
    pass


class JobMapper(Mapper):
    async def to_internal(self, external: Any) -> dict[str, Any]:
        """
        Converts external replesentation into a dictionary
        with internal type attributes.
        Overrides the parent `to_internal` method.
        """
        # print(external)
        user = (
            await manage_user.retrieve(external.get("user_id"))
            if external.get("user_id")
            else None
        )
        try:
            result = {
                "id": external.get("id"),
                "user": user,
                "title": external.get("title"),
                "company": external.get("company"),
                "description": external.get("description"),
                "country": Country[external.get("country")],
                "city": external.get("city"),
                "work_setting_type": external.get("work_setting_type"),
                "status": external.get("status"),
                "employment_type": EmploymentType(
                    external.get("employment_type").value
                ),
                "notes": external.get("notes"),
                "external_id": external.get("external_id"),
                "platform": external.get("platform"),
                "url": external.get("url"),
                "created_at": external.get("created_at"),
                "updated_at": external.get("updated_at"),
            }
        except Exception as e:
            print(e)
            return external
        return result

    async def to_external(self, internal: Dict[str, Any]) -> Dict[str, Any]:
        """
        Converts a database record dictionary into an external
        dictionary representation.
        Overrides the parent `to_external` method.
        """
        return {
            "id": internal["id"],
            "user_id": internal["user"].id,
            "title": internal["title"],
            "company": internal["company"],
            "description": internal["description"],
            "country": internal["country"].name,
            "city": internal["city"],
            "work_setting_type": getattr(
                internal.get("work_setting_type"), "name", None
            ),
            "status": getattr(internal.get("status"), "name", None),
            "employment_type": getattr(internal.get("employment_type"), "name", None),
            "notes": internal.get("notes"),
            "external_id": internal.get("external_id"),
            "platform": internal.get("platform"),
            "url": internal.get("url"),
            "created_at": internal.get("created_at"),
            "updated_at": internal.get("updated_at"),
        }


class JobSQLGateway(SQLGateway, table=job_table):
    mapper = JobMapper()


db = AsyncpgSQLDatabase(get_database_url("production"))

job_gateway = JobSQLGateway(db)
manage_job = ManageJob(JobRepository(job_gateway))
