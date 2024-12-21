import asyncio
from dataclasses import dataclass
from typing import Any, Optional

import pytest
from sqlalchemy import Boolean, Column, DateTime, Float, MetaData, Table, Text, text
from sqlalchemy.dialects import postgresql
from sqlalchemy.dialects.postgresql import UUID

from src.application.base.manage import Manage
from src.domain.base.root_entity import RootEntity
from src.repository.base.repository import Repository
from src.repository.sql.asyncpg_sql_database import AsyncpgSQLDatabase
from src.repository.sql.sql_gateway import SQLGateway

test_model = Table(
    "test_model",
    MetaData(),
    Column("id", UUID(as_uuid=True), primary_key=True),
    Column("t", Text, nullable=False),
    Column("f", Float, nullable=False),
    Column("b", Boolean, nullable=False),
    Column("updated_at", DateTime(timezone=True), nullable=False),
    Column("created_at", DateTime(timezone=True), nullable=False),
    Column("n", Float, nullable=True),
    Column("json", postgresql.JSONB(astext_type=Text()), nullable=True),
)
# For SQLProvider integration tests
count_query = text("SELECT COUNT(*) FROM test_model")
insert_query = text(
    "INSERT INTO test_model (t, f, b, updated_at) "
    "VALUES ('foo', 1.23, TRUE, '2016-06-22 19:10:25-07') "
    "RETURNING id"
)
update_query = text("UPDATE test_model SET t='bar' WHERE id=:id RETURNING t")


@pytest.fixture
async def postgres_url():
    return "postgres:postgres@localhost:5434"


@pytest.fixture
async def postgres_db_url(postgres_url) -> str:
    from sqlalchemy import create_engine, text

    dbname = "test"
    root_engine = create_engine(
        f"postgresql+psycopg2://{postgres_url}", isolation_level="AUTOCOMMIT"
    )
    with root_engine.connect() as connection:
        connection.execute(text(f"DROP DATABASE IF EXISTS {dbname}"))
        connection.execute(text(f"CREATE DATABASE {dbname}"))
    root_engine.dispose()

    engine = create_engine(
        f"postgresql+psycopg2://{postgres_url}/{dbname}", isolation_level="AUTOCOMMIT"
    )
    with engine.connect() as connection:
        test_model.metadata.drop_all(engine)
        test_model.metadata.create_all(engine)
    engine.dispose()
    return f"{postgres_url}/{dbname}"


@pytest.fixture(scope="session")
def event_loop():
    loop = asyncio.get_event_loop()
    yield loop
    loop.close()


@dataclass(frozen=True)
class Tst(RootEntity):
    t: str
    f: float
    b: bool
    n: Optional[float] = None
    json: Optional[dict[str, Any]] = None


@pytest.fixture(params=[AsyncpgSQLDatabase])
async def database(request, postgres_db_url):
    """Fixture to set up the database."""
    db = request.param(postgres_db_url, pool_size=2)  # pool_size=2 for Conflict test
    yield db
    await db.dispose()


class TstRepository(Repository[Tst]):
    """Repository for Tst entity."""

    pass


class TstManage(Manage[Tst]):
    """Manage layer for Tst entity."""

    pass


class TstSQLGateway(SQLGateway, table=test_model):
    """SQL Gateway for Tst entity."""

    pass


@pytest.fixture
def tst_gateway(database):
    """Fixture for TstSQLGateway."""
    return TstSQLGateway(database)


@pytest.fixture
def manage_job(tst_gateway):
    """Fixture for TstManage."""
    return TstManage(TstRepository(tst_gateway))
