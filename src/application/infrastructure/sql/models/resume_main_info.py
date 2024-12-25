from datetime import datetime
from uuid import uuid4

from sqlalchemy import ARRAY, Column, DateTime, ForeignKey, MetaData, String, Table
from sqlalchemy.dialects.postgresql import UUID

resume_main_info_metadata = MetaData()


resume_main_info_table = Table(
    "resume_main_info",
    resume_main_info_metadata,
    Column("id", UUID(as_uuid=True), primary_key=True, default=uuid4),
    Column("user_id", UUID(as_uuid=True), ForeignKey("users.id"), nullable=False),
    Column("applicant_name", String, nullable=False),
    Column("summary", String, nullable=True),
    Column("location", String, nullable=True),
    Column("phone", String, nullable=True),
    Column("email", String, nullable=True),
    Column("linkedin", String, nullable=True),
    Column("resume_name", String, nullable=True),
    Column("parent_id", UUID(as_uuid=True)),
    Column("skills", ARRAY(String)),
    Column(
        "created_at", DateTime(timezone=True), nullable=False, default=datetime.utcnow
    ),
    Column("updated_at", DateTime(timezone=True), nullable=True),
)
