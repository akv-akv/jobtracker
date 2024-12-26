from unittest.mock import AsyncMock, patch

import pytest
from sqlalchemy.ext.asyncio import AsyncConnection, AsyncEngine
from sqlalchemy.sql import text

from src.core.gateway.sql.sql_provider import SQLDatabase, SQLProvider


@pytest.fixture
def mock_connection():
    return AsyncMock(spec=AsyncConnection)


@pytest.fixture
def mock_engine():
    return AsyncMock(spec=AsyncEngine)


@pytest.fixture
def sql_provider(mock_connection):
    return SQLProvider(connection=mock_connection)


@pytest.fixture
def sql_database(mock_connection, mock_engine):
    return SQLDatabase(connection=mock_connection, engine=mock_engine)


async def test_execute(sql_provider, mock_connection):
    # Mock fetchall response
    mock_connection.execute.return_value.fetchall.return_value = [
        {"id": 1, "name": "test"},
        {"id": 2, "name": "example"},
    ]

    query = text("SELECT * FROM table")
    result = await sql_provider.execute(query)

    mock_connection.execute.assert_called_once_with(query, {})
    assert result == [{"id": 1, "name": "test"}, {"id": 2, "name": "example"}]


async def test_transaction(sql_provider, mock_connection):
    async with sql_provider.transaction() as provider:
        assert provider == sql_provider

    mock_connection.begin.assert_called_once()


async def test_testing_transaction_success(sql_provider, mock_connection):
    async with sql_provider.testing_transaction() as provider:
        assert provider == sql_provider

    assert any(
        "SAVEPOINT test_savepoint" in str(call[0][0])
        for call in mock_connection.execute.call_args_list
    ), "SAVEPOINT test_savepoint not called"

    assert any(
        "RELEASE SAVEPOINT test_savepoint" in str(call[0][0])
        for call in mock_connection.execute.call_args_list
    ), "RELEASE SAVEPOINT test_savepoint not called"


async def test_testing_transaction_failure(sql_provider, mock_connection):
    mock_connection.execute.side_effect = Exception("Test Exception")

    with pytest.raises(Exception, match="Test Exception"):
        async with sql_provider.testing_transaction():
            pass

    print("Mock execute call arguments:", mock_connection.execute.call_args_list)

    mock_connection.execute.assert_called_once()

    assert any(
        "SAVEPOINT test_savepoint" in str(call[0][0])
        for call in mock_connection.execute.call_args_list
    ), "SAVEPOINT test_savepoint not called"


@pytest.mark.parametrize(
    "method_name, sql, args",
    [
        ("create_database", "CREATE DATABASE test_db", ["test_db"]),
        ("create_extension", "CREATE EXTENSION IF NOT EXISTS pgcrypto", ["pgcrypto"]),
        ("drop_database", "DROP DATABASE IF EXISTS test_db", ["test_db"]),
    ],
)
async def test_sql_methods(sql_database, method_name, sql, args):
    with patch.object(sql_database, "execute_autocommit") as mock_execute_autocommit:
        method = getattr(sql_database, method_name)
        await method(*args)
        sql_query = mock_execute_autocommit.call_args[0][0]
        assert str(sql_query) == sql


async def test_truncate_tables(sql_database):
    sql_database.execute_autocommit = AsyncMock()

    await sql_database.truncate_tables(["table1", "table2"])

    sql_query = sql_database.execute_autocommit.call_args[0][0]
    assert str(sql_query) == 'TRUNCATE TABLE "table1", "table2"'
