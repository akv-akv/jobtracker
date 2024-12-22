from datetime import datetime
from uuid import uuid4

from sqlalchemy import Column, DateTime, MetaData, String, Table
from sqlalchemy.dialects.postgresql import UUID

from manage import get_database_url
from src.application.domain.entity.user import User
from src.core.manage import Manage
from src.core.repository.base.repository import Repository
from src.core.repository.sql.asyncpg_sql_database import AsyncpgSQLDatabase
from src.core.repository.sql.sql_gateway import SQLGateway

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


class ManageUser(Manage[User]):
    pass


class UserRepository(Repository[User]):
    pass


class UserSQLGateway(SQLGateway, table=user_table):
    pass


db = AsyncpgSQLDatabase(get_database_url("production"))

user_gateway = UserSQLGateway(db)
manage_user = ManageUser(UserRepository(user_gateway))
