import asyncio
from typing import Any, Optional

import pytest
from sqlalchemy import Boolean, Column, DateTime, Enum, Float, MetaData, Table, Text
from sqlalchemy.dialects import postgresql
from sqlalchemy.dialects.postgresql import UUID

from src.application.domain.enums.country import Country
from src.core.domain.root_entity import RootEntity
from src.core.gateway.sql.asyncpg_sql_database import AsyncpgSQLDatabase
from src.core.gateway.sql.sql_gateway import SQLGateway
from src.core.manage import Manage
from src.core.repository.base.mapper import Mapper
from src.core.repository.base.repository import Repository

test_model = Table(
    "test_model",
    MetaData(),
    Column("id", UUID(as_uuid=True), primary_key=True),
    Column("t", Text, nullable=False),
    Column("f", Float, nullable=False),
    Column("b", Boolean, nullable=False),
    Column("c", Enum(Country)),
    Column("updated_at", DateTime(timezone=True), nullable=False),
    Column("created_at", DateTime(timezone=True), nullable=False),
    Column("n", Float, nullable=True),
    Column("jsn", postgresql.JSONB(astext_type=Text()), nullable=True),
)


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


@pytest.fixture(scope="module")
def event_loop():
    loop = asyncio.get_event_loop()
    yield loop
    loop.close()


class Tst(RootEntity):
    t: str
    f: float
    b: bool
    c: Country
    n: Optional[float] = None
    jsn: Optional[dict[str, Any]] = None


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


class TstMapper(Mapper):
    async def to_internal(self, external):
        internal = {
            "id": external.get("id"),
            "t": external.get("t"),
            "f": external.get("f"),
            "b": external.get("b"),
            "c": Country[external.get("c")],
            "n": external.get("n"),
            "jsn": external.get("jsn"),
            "created_at": external.get("created_at"),
            "updated_at": external.get("updated_at"),
        }
        return internal

    async def to_external(self, internal):
        external = {
            "id": internal.get("id"),
            "t": internal.get("t"),
            "f": internal.get("f"),
            "b": internal.get("b"),
            "c": internal.get("c").name,
            "n": internal.get("n"),
            "jsn": internal.get("jsn"),
            "created_at": internal.get("created_at"),
            "updated_at": internal.get("updated_at"),
        }
        return external


class TstSQLGateway(SQLGateway, table=test_model):
    """SQL Gateway for Tst entity."""

    mapper = TstMapper()


@pytest.fixture
def tst_gateway(database):
    """Fixture for TstSQLGateway."""
    return TstSQLGateway(database)


@pytest.fixture
def manage_job(tst_gateway):
    """Fixture for TstManage."""
    return TstManage(TstRepository(tst_gateway))
