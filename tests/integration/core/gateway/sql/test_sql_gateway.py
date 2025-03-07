from datetime import datetime, timezone

import pytest
from asyncpg.exceptions import NotNullViolationError
from sqlalchemy import text
from sqlalchemy.exc import IntegrityError

from src.core.domain.exceptions import AlreadyExists, Conflict, DoesNotExist
from src.core.gateway.sql.asyncpg_sql_database import AsyncpgSQLDatabase
from src.core.gateway.sql.sql_gateway import SQLDatabase, SQLGateway
from src.core.repository.base.filter import Filter

from .conftest import test_model

pytestmark = pytest.mark.integration


@pytest.fixture(params=[AsyncpgSQLDatabase])
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
async def sql_gateway(test_transaction):
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


async def test_get(sql_gateway, obj_in_db):
    actual = await sql_gateway.get(obj_in_db["id"])
    assert isinstance(actual, dict)
    assert actual == obj_in_db
    assert actual is not obj_in_db


async def test_get_not_found(sql_gateway, obj_in_db):
    assert await sql_gateway.get(obj_in_db["id"] + 1) is None


async def test_add(sql_gateway, test_transaction, obj):
    created = await sql_gateway.add(obj)

    id = created.pop("id")
    assert isinstance(id, int)
    assert created is not obj
    assert created == obj

    res = await test_transaction.execute(
        text(f"SELECT * FROM test_model WHERE id = {id}")
    )
    assert res[0]["t"] == obj["t"]


async def test_add_id_exists(sql_gateway, obj_in_db):
    with pytest.raises(
        AlreadyExists, match=f"record with id={obj_in_db['id']} already exists"
    ):
        await sql_gateway.add(obj_in_db)


@pytest.mark.parametrize("id", [10, None, "delete"])
async def test_add_integrity_error(sql_gateway, obj, id):
    obj.pop("t")  # will cause the IntegrityError
    if id != "delete":
        obj["id"] = id
    with pytest.raises((NotNullViolationError, IntegrityError)):  # depends on backend
        await sql_gateway.add(obj)


async def test_add_unkown_column(sql_gateway, obj):
    created = await sql_gateway.add({"unknown": "foo", **obj})

    created.pop("id")
    assert created == obj


async def test_update(sql_gateway, test_transaction, obj_in_db):
    obj_in_db["t"] = "bar"

    updated = await sql_gateway.update(obj_in_db)

    assert updated is not obj_in_db
    assert updated == obj_in_db

    res = await test_transaction.execute(
        text(f"SELECT * FROM test_model WHERE id = {obj_in_db['id']}")
    )
    assert res[0]["t"] == "bar"


async def test_update_not_found(sql_gateway, obj):
    obj["id"] = 42

    with pytest.raises(DoesNotExist):
        await sql_gateway.update(obj)


async def test_update_unkown_column(sql_gateway, obj_in_db):
    obj_in_db["t"] = "bar"
    updated = await sql_gateway.update({"unknown": "foo", **obj_in_db})

    assert updated == obj_in_db


async def test_upsert_does_add(sql_gateway, test_transaction, obj):
    obj["id"] = 42
    created = await sql_gateway.upsert(obj)

    assert created is not obj
    assert created == obj

    res = await test_transaction.execute(text("SELECT * FROM test_model WHERE id = 42"))
    assert res[0]["t"] == obj["t"]


async def test_upsert_does_update(sql_gateway, test_transaction, obj_in_db):
    obj_in_db["t"] = "bar"
    updated = await sql_gateway.upsert(obj_in_db)

    assert updated is not obj_in_db
    assert updated == obj_in_db

    res = await test_transaction.execute(
        text(f"SELECT * FROM test_model WHERE id = {obj_in_db['id']}")
    )
    assert res[0]["t"] == "bar"


async def test_remove(sql_gateway, test_transaction, obj_in_db):
    assert await sql_gateway.remove(obj_in_db["id"])

    res = await test_transaction.execute(
        text(f"SELECT COUNT(*) FROM test_model WHERE id = {obj_in_db['id']}")
    )
    assert res[0]["count"] == 0


async def test_remove_not_found(sql_gateway):
    assert not await sql_gateway.remove(42)


async def test_update_if_unmodified_since(sql_gateway, obj_in_db):
    obj_in_db["t"] = "bar"

    updated = await sql_gateway.update(
        obj_in_db, if_unmodified_since=obj_in_db["updated_at"]
    )

    assert updated == obj_in_db


@pytest.mark.parametrize(
    "if_unmodified_since", [datetime.now(timezone.utc), datetime(2010, 1, 1)]
)
async def test_update_if_unmodified_since_not_ok(
    sql_gateway, obj_in_db, if_unmodified_since
):
    obj_in_db["t"] = "bar"

    with pytest.raises(Conflict):
        await sql_gateway.update(obj_in_db, if_unmodified_since=if_unmodified_since)


@pytest.mark.parametrize(
    "filters,match",
    [
        ([], True),
        ([Filter(field="t", values=["foo"])], True),
        ([Filter(field="t", values=["bar"])], False),
        ([Filter(field="t", values=["foo"]), Filter(field="f", values=[1.23])], True),
        ([Filter(field="t", values=["foo"]), Filter(field="f", values=[1.24])], False),
        ([Filter(field="nonexisting", values=["foo"])], False),
        ([Filter(field="t", values=[])], False),
        ([Filter(field="t", values=["foo", "bar"])], True),
    ],
)
async def test_filter(filters, match, sql_gateway, obj_in_db):
    actual = await sql_gateway.filter(filters)

    assert actual == ([obj_in_db] if match else [])


@pytest.fixture
async def obj2_in_db(test_transaction, obj):
    res = await test_transaction.execute(
        text(
            "INSERT INTO test_model (t, f, b, updated_at) "
            "VALUES ('bar', 1.24, TRUE, '2018-06-22 19:10:25-07') "
            "RETURNING id"
        )
    )
    return {"id": res[0]["id"], **obj}


@pytest.mark.parametrize(
    "filters,expected",
    [
        ([], 2),
        ([Filter(field="t", values=["foo"])], 1),
        ([Filter(field="t", values=["bar"])], 1),
        ([Filter(field="t", values=["baz"])], 0),
    ],
)
async def test_count(filters, expected, sql_gateway, obj_in_db, obj2_in_db):
    actual = await sql_gateway.count(filters)
    assert actual == expected


@pytest.mark.parametrize(
    "filters,expected",
    [
        ([], True),
        ([Filter(field="t", values=["foo"])], True),
        ([Filter(field="t", values=["bar"])], True),
        ([Filter(field="t", values=["baz"])], False),
    ],
)
async def test_exists(filters, expected, sql_gateway, obj_in_db, obj2_in_db):
    actual = await sql_gateway.exists(filters)
    assert actual == expected


async def test_truncate(database: SQLDatabase, obj):
    gateway = TstSQLGateway(database)
    await gateway.add(obj)
    assert await gateway.exists([])
    await database.truncate_tables(["test_model"])
    assert not await gateway.exists([])
