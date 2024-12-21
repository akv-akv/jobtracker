from datetime import datetime
from uuid import uuid4

from sqlalchemy import Column, DateTime, Enum, ForeignKey, MetaData, String, Table, Text
from sqlalchemy.dialects.postgresql import UUID

from src.domain.enums.country import Country

metadata = MetaData()

# Users Table
user_table = Table(
    "users",
    metadata,
    Column("id", UUID(as_uuid=True), primary_key=True, default=uuid4),
    Column("name", String, nullable=False),
    Column(
        "created_at", DateTime(timezone=True), nullable=False, default=datetime.utcnow
    ),
    Column("updated_at", DateTime(timezone=True), nullable=True),
)

# Jobs Table
job_table = Table(
    "jobs",
    metadata,
    Column("id", UUID(as_uuid=True), primary_key=True, default=uuid4),
    Column("user_id", UUID(as_uuid=True), ForeignKey("users.id"), nullable=False),
    Column("title", String, nullable=False),
    Column("company", String, nullable=False),
    Column("description", Text, nullable=False),
    Column("country", Enum(Country)),  # Store ISO code as string
    Column("city", String, nullable=False),
    Column("work_setting_type", String, nullable=True),  # Store Enum as string
    Column("status", String, nullable=False),  # Store Enum as string
    Column("employment_type", String, nullable=True),  # Store Enum as string
    Column("notes", Text, nullable=True),
    Column("external_id", String, nullable=True),
    Column("platform", String, nullable=True),
    Column("url", String, nullable=True),
    Column(
        "created_at", DateTime(timezone=True), nullable=False, default=datetime.utcnow
    ),
    Column("updated_at", DateTime(timezone=True), nullable=True),
)
