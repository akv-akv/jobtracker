from datetime import datetime, timezone

import pytest
from sqlalchemy import text

from src.repository.sql.sql_gateway import SQLDatabase, SQLGateway
from src.repository.sql.sqlalchemy_async_sql_database import SQLAlchemyAsyncSQLDatabase
from tests.integration.conftest import test_model


@pytest.fixture(scope="session", params=[SQLAlchemyAsyncSQLDatabase])
async def database(request, postgres_db_url):
    # pool_size=2 for Conflict test
    db = request.param(postgres_db_url, pool_size=2)
    yield db
    await db.dispose()


class TstSQLGateway(SQLGateway, table=test_model):
    pass


@pytest.fixture
async def test_transaction(database: SQLDatabase):
    async with database.testing_transaction() as test_transaction:
        yield test_transaction


@pytest.fixture
def sql_gateway(test_transaction):
    return TstSQLGateway(test_transaction)


@pytest.fixture
def obj():
    return {
        "t": "foo",
        "f": 1.23,
        "b": True,
        "updated_at": datetime(2016, 6, 23, 2, 10, 25, tzinfo=timezone.utc),
        "n": None,
        "json": {"foo": 2},
    }


@pytest.fixture
async def obj_in_db(test_transaction, obj):
    res = await test_transaction.execute(
        text(
            "INSERT INTO test_model (t, f, b, updated_at, json) "
            "VALUES ('foo', 1.23, TRUE, '2016-06-22 19:10:25-07', '{\"foo\"\\:2}') "
            "RETURNING id"
        )
    )
    return {"id": res[0]["id"], **obj}


@pytest.mark.integration
async def test_get(sql_gateway, obj_in_db):
    actual = await sql_gateway.get(obj_in_db["id"])

    assert isinstance(actual, dict)
    assert actual == obj_in_db
    assert actual is not obj_in_db
