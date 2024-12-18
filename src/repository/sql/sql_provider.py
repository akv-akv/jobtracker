from contextlib import asynccontextmanager
from typing import Any, AsyncIterator, Dict, Sequence

from sqlalchemy.ext.asyncio import AsyncConnection, AsyncEngine
from sqlalchemy.sql import Executable, text


class SQLProvider:
    """
    Base class for SQL database operations.
    """

    def __init__(self, connection: AsyncConnection):
        self.connection = connection

    async def execute(
        self, query: Executable, bind_params: Dict[str, Any] | None = None
    ) -> list[Dict[str, Any]]:
        async with self.connection.begin():
            result = await self.connection.execute(query, bind_params or {})
            rows = await result.fetchall()  # type: ignore
            return [dict(row) for row in rows]

    @asynccontextmanager
    async def transaction(self) -> AsyncIterator["SQLProvider"]:
        async with self.connection.begin():
            yield self

    @asynccontextmanager
    async def testing_transaction(self) -> AsyncIterator["SQLProvider"]:
        """
        Use SAVEPOINT for transactional testing.
        """
        async with self.connection.begin():
            await self.connection.execute(text("SAVEPOINT test_savepoint"))
            try:
                yield self
                await self.connection.execute(text("RELEASE SAVEPOINT test_savepoint"))
            except Exception:
                await self.connection.execute(
                    text("ROLLBACK TO SAVEPOINT test_savepoint")
                )
                raise


class SQLDatabase(SQLProvider):
    """
    Concrete implementation of SQLProvider for specific database operations.
    """

    def __init__(self, connection: AsyncConnection, engine: AsyncEngine):
        super().__init__(connection)
        self.engine = engine

    async def execute_autocommit(self, query: Executable) -> None:
        async with self.engine.connect() as conn:
            async with conn.begin():
                await conn.execute(query)

    async def create_database(self, name: str) -> None:
        """
        Creates a new database with the given name.
        """
        await self.execute_autocommit(text(f"CREATE DATABASE {name}"))

    async def create_extension(self, name: str) -> None:
        """
        Creates a database extension if it does not already exist.
        """
        await self.execute_autocommit(text(f"CREATE EXTENSION IF NOT EXISTS {name}"))

    async def drop_database(self, name: str) -> None:
        """
        Drops the specified database if it exists.
        """
        await self.execute_autocommit(text(f"DROP DATABASE IF EXISTS {name}"))

    async def truncate_tables(self, names: Sequence[str]) -> None:
        """
        Truncates the specified tables.
        """
        quoted = [f'"{name}"' for name in names]
        await self.execute_autocommit(text(f"TRUNCATE TABLE {', '.join(quoted)}"))
