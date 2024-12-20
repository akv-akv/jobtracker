import asyncio

import pytest
from sqlalchemy import (
    Boolean,
    Column,
    DateTime,
    Float,
    Integer,
    MetaData,
    Table,
    Text,
    text,
)
from sqlalchemy.dialects import postgresql

test_model = Table(
    "test_model",
    MetaData(),
    Column("id", Integer, primary_key=True, autoincrement=True),
    Column("t", Text, nullable=False),
    Column("f", Float, nullable=False),
    Column("b", Boolean, nullable=False),
    Column("updated_at", DateTime(timezone=True), nullable=False),
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
