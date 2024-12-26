from datetime import datetime
from uuid import uuid4

from sqlalchemy import Column, DateTime, MetaData, Table, Text
from sqlalchemy.dialects.postgresql import UUID

resume_template_metadata = MetaData()


resume_template_table = Table(
    "resume_template",
    resume_template_metadata,
    Column("id", UUID(as_uuid=True), primary_key=True, default=uuid4),
    Column("resume_template", Text, nullable=False),
    Column("parent_id", UUID(as_uuid=True)),
    Column(
        "created_at", DateTime(timezone=True), nullable=False, default=datetime.utcnow
    ),
    Column("updated_at", DateTime(timezone=True), nullable=True),
)
