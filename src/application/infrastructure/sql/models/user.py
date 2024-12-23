from uuid import uuid4

from sqlalchemy import Column, DateTime, MetaData, String, Table, func
from sqlalchemy.dialects.postgresql import UUID

user_metadata = MetaData()

user_table = Table(
    "users",
    user_metadata,
    Column("id", UUID(as_uuid=True), primary_key=True, default=uuid4),
    Column("name", String, nullable=False),
    Column(
        "created_at", DateTime(timezone=True), nullable=False, server_default=func.now()
    ),
    Column("updated_at", DateTime(timezone=True), nullable=False),
)
