from contextlib import asynccontextmanager
from datetime import datetime, timezone
from enum import Enum as PyEnum
from typing import Any, AsyncIterator
from unittest import mock

import pytest
from sqlalchemy import (
    Column,
    DateTime,
    Enum,
    ForeignKey,
    Integer,
    MetaData,
    Table,
    Text,
)
from sqlalchemy.dialects import postgresql
from sqlalchemy.sql import Executable

from src.core.domain.exceptions import Conflict, DoesNotExist
from src.core.repository.base.filter import Filter
from src.core.repository.base.mapper import Mapper
from src.core.repository.base.pagination import PageOptions
from src.core.repository.sql.sql_gateway import SQLGateway
from src.core.repository.sql.sql_provider import SQLProvider

DIALECT = postgresql.dialect()


class FakeSQLDatabase(SQLProvider):
    def __init__(self):
        self.queries: list[list[Executable]] = []
        self.result = mock.Mock(return_value=[])

    async def execute(
        self, query: Executable, _: dict[str, Any] | None = None
    ) -> list[dict[str, Any]]:
        self.queries.append([query])
        return self.result()

    @asynccontextmanager
    async def transaction(self) -> AsyncIterator["SQLProvider"]:  # type: ignore
        x = FakeSQLTransaction(result=self.result)
        self.queries.append(x.queries)
        yield x


class FakeSQLTransaction(SQLProvider):
    def __init__(self, result: mock.Mock):
        self.queries: list[Executable] = []
        self.result = result

    async def execute(
        self, query: Executable, _: dict[str, Any] | None = None
    ) -> list[dict[str, Any]]:
        self.queries.append(query)
        return self.result()


def assert_query_equal(q: Executable, expected: str, literal_binds: bool = True):
    """There are two ways of 'binding' parameters (for testing!):

    literal_binds=True: use the built-in sqlalchemy way,
        which fails on some datatypes (Range)
    literal_binds=False: do it yourself using %,
        there is no 'mogrify' so don't expect quotes.
    """
    assert isinstance(q, Executable)
    compiled = q.compile(
        compile_kwargs={"literal_binds": literal_binds},
        dialect=postgresql.dialect(),
    )
    if not literal_binds:
        actual = str(compiled) % compiled.params
    else:
        actual = str(compiled)
    actual = actual.replace("\n", "").replace("  ", " ")
    assert actual == expected, actual


class MyEnum(PyEnum):
    one = "one"
    two = "two"
    three = "three"


author = Table(
    "author",
    MetaData(),
    Column("id", Integer, primary_key=True, autoincrement=True),
    Column("name", Text, nullable=False),
    Column("updated_at", DateTime(timezone=True), nullable=False),
)


book = Table(
    "book",
    MetaData(),
    Column("id", Integer, primary_key=True, autoincrement=True),
    Column("title", Text, nullable=False),
    Column("book_type", Enum(MyEnum, name="myenum")),
    Column(
        "author_id",
        Integer,
        ForeignKey("author.id", ondelete="CASCADE", name="book_author_id_fkey"),
        nullable=False,
    ),
)


class BookMapper(Mapper):
    async def to_external(self, internal):
        return {
            "id": internal.get("id"),
            "title": internal.get("title"),
            "book_type": internal.get("book_type"),
            "author_id": internal.get("author_id"),
        }


ALL_FIELDS = "author.id, author.name, author.updated_at"
BOOK_FIELDS = "book.id, book.title, book.book_type, book.author_id"


class TstSQLGateway(SQLGateway, table=author):
    pass


class TstRelatedSQLGateway(SQLGateway, table=book):
    mapper = BookMapper()


@pytest.fixture
def sql_gateway():
    return TstSQLGateway(FakeSQLDatabase())


@pytest.fixture
def related_sql_gateway():
    return TstRelatedSQLGateway(FakeSQLDatabase())


@pytest.mark.parametrize(
    "filters,sql",
    [
        ([], " WHERE true"),
        ([Filter(field="name", values=[])], " WHERE false"),
        ([Filter(field="name", values=["foo"])], " WHERE author.name = 'foo'"),
        (
            [Filter(field="name", values=["foo", "bar"])],
            " WHERE author.name IN ('foo', 'bar')",
        ),
        ([Filter(field="nonexisting", values=["foo"])], " WHERE false"),
        (
            [Filter(field="id", values=[1]), Filter(field="name", values=["foo"])],
            " WHERE author.id = 1 AND author.name = 'foo'",
        ),
    ],
)
async def test_filter(sql_gateway, filters, sql):
    sql_gateway.provider.result.return_value = [{"id": 2, "name": "foo"}]
    assert await sql_gateway.filter(filters) == [{"id": 2, "name": "foo"}]
    assert len(sql_gateway.provider.queries) == 1
    assert_query_equal(
        sql_gateway.provider.queries[0][0],
        f"SELECT {ALL_FIELDS} FROM author{sql}",
    )


@pytest.mark.parametrize(
    "page_options,sql",
    [
        (None, ""),
        (
            PageOptions(limit=5, order_by="id"),
            " ORDER BY author.id ASC LIMIT 5 OFFSET 0",
        ),
        (
            PageOptions(limit=5, offset=2, order_by="id", ascending=False),
            " ORDER BY author.id DESC LIMIT 5 OFFSET 2",
        ),
    ],
)
async def test_filter_with_pagination(sql_gateway, page_options, sql):
    sql_gateway.provider.result.return_value = [{"id": 2, "name": "foo"}]
    assert await sql_gateway.filter([], params=page_options) == [
        {"id": 2, "name": "foo"}
    ]
    assert len(sql_gateway.provider.queries) == 1
    assert_query_equal(
        sql_gateway.provider.queries[0][0],
        f"SELECT {ALL_FIELDS} FROM author WHERE true{sql}",
    )


async def test_filter_with_pagination_and_filter(sql_gateway):
    sql_gateway.provider.result.return_value = [{"id": 2, "name": "foo"}]
    assert await sql_gateway.filter(
        [Filter(field="name", values=["foo"])],
        params=PageOptions(limit=5, order_by="id"),
    ) == [{"id": 2, "name": "foo"}]
    assert len(sql_gateway.provider.queries) == 1
    assert_query_equal(
        sql_gateway.provider.queries[0][0],
        (
            f"SELECT {ALL_FIELDS} FROM author "
            f"WHERE author.name = 'foo' "
            f"ORDER BY author.id ASC LIMIT 5 OFFSET 0"
        ),
    )


@pytest.mark.parametrize(
    "filters,sql",
    [
        ([], " WHERE true"),
        ([Filter(field="name", values=[])], " WHERE false"),
        ([Filter(field="name", values=["foo"])], " WHERE author.name = 'foo'"),
        (
            [Filter(field="name", values=["foo", "bar"])],
            " WHERE author.name IN ('foo', 'bar')",
        ),
        ([Filter(field="nonexisting", values=["foo"])], " WHERE false"),
        (
            [Filter(field="id", values=[1]), Filter(field="name", values=["foo"])],
            " WHERE author.id = 1 AND author.name = 'foo'",
        ),
    ],
)
async def test_count(sql_gateway, filters, sql):
    sql_gateway.provider.result.return_value = [{"count": 4}]
    assert await sql_gateway.count(filters) == 4
    assert len(sql_gateway.provider.queries) == 1
    assert_query_equal(
        sql_gateway.provider.queries[0][0],
        f"SELECT count(*) AS count FROM author{sql}",
    )


async def test_count_related_gateway(related_sql_gateway):
    related_sql_gateway.provider.result.return_value = [{"count": 4}]
    assert await related_sql_gateway.count([]) == 4
    assert len(related_sql_gateway.provider.queries) == 1
    assert_query_equal(
        related_sql_gateway.provider.queries[0][0],
        "SELECT count(*) AS count FROM book WHERE true",
    )


@mock.patch.object(SQLGateway, "filter")
async def test_get(filter_m, sql_gateway):
    filter_m.return_value = [{"id": 2, "name": "foo"}]
    assert await sql_gateway.get(2) == filter_m.return_value[0]
    assert len(sql_gateway.provider.queries) == 0
    filter_m.assert_awaited_once_with([Filter(field="id", values=[2])], params=None)


@mock.patch.object(SQLGateway, "filter")
async def test_get_does_not_exist(filter_m, sql_gateway):
    filter_m.return_value = []
    assert await sql_gateway.get(2) is None
    assert len(sql_gateway.provider.queries) == 0
    filter_m.assert_awaited_once_with([Filter(field="id", values=[2])], params=None)


@pytest.mark.parametrize(
    "record,sql",
    [
        ({}, "DEFAULT VALUES"),
        ({"name": "foo"}, "(name) VALUES ('foo')"),
        ({"id": None, "name": "foo"}, "(name) VALUES ('foo')"),
        ({"id": 2, "name": "foo"}, "(id, name) VALUES (2, 'foo')"),
        ({"name": "foo", "nonexisting": 2}, "(name) VALUES ('foo')"),
    ],
)
async def test_add(sql_gateway, record, sql):
    records = [{"id": 2, "name": "foo"}]
    sql_gateway.provider.result.return_value = records
    assert await sql_gateway.add(record) == records[0]
    assert len(sql_gateway.provider.queries) == 1
    assert_query_equal(
        sql_gateway.provider.queries[0][0],
        (f"INSERT INTO author {sql} RETURNING {ALL_FIELDS}"),
    )


@pytest.mark.parametrize(
    "record,if_unmodified_since,sql",
    [
        (
            {"id": 2, "name": "foo"},
            None,
            "SET id=2, name='foo' WHERE author.id = 2",
        ),
        ({"id": 2, "other": "foo"}, None, "SET id=2 WHERE author.id = 2"),
        (
            {"id": 2, "name": "foo"},
            datetime(2010, 1, 1, tzinfo=timezone.utc),
            (
                "SET id=2, name='foo' WHERE author.id = 2 "
                "AND author.updated_at = '2010-01-01 00:00:00+00:00'"
            ),
        ),
    ],
)
async def test_update(sql_gateway, record, if_unmodified_since, sql):
    records = [{"id": 2, "name": "foo"}]
    sql_gateway.provider.result.return_value = records
    assert await sql_gateway.update(record, if_unmodified_since) == records[0]
    assert len(sql_gateway.provider.queries) == 1
    assert_query_equal(
        sql_gateway.provider.queries[0][0],
        (f"UPDATE author {sql} RETURNING {ALL_FIELDS}"),
    )


async def test_update_does_not_exist(sql_gateway):
    sql_gateway.provider.result.return_value = []
    with pytest.raises(DoesNotExist):
        await sql_gateway.update({"id": 2})
    assert len(sql_gateway.provider.queries) == 1


@mock.patch.object(SQLGateway, "exists")
async def test_update_if_unmodified_since_does_not_exist(exists_m, sql_gateway):
    exists_m.return_value = False
    sql_gateway.provider.result.return_value = []
    with pytest.raises(DoesNotExist):
        await sql_gateway.update(
            {"id": 2}, if_unmodified_since=datetime(2010, 1, 1, tzinfo=timezone.utc)
        )
    assert len(sql_gateway.provider.queries) == 1
    exists_m.assert_awaited_once_with([Filter(field="id", values=[2])])


@mock.patch.object(SQLGateway, "exists")
async def test_update_if_unmodified_since_conflict(exists_m, sql_gateway):
    exists_m.return_value = True
    sql_gateway.provider.result.return_value = []
    with pytest.raises(Conflict):
        await sql_gateway.update(
            {"id": 2}, if_unmodified_since=datetime(2010, 1, 1, tzinfo=timezone.utc)
        )
    assert len(sql_gateway.provider.queries) == 1
    exists_m.assert_awaited_once_with([Filter(field="id", values=[2])])


async def test_remove(sql_gateway):
    sql_gateway.provider.result.return_value = [{"id": 2}]
    assert (await sql_gateway.remove(2)) is True
    assert len(sql_gateway.provider.queries) == 1
    assert_query_equal(
        sql_gateway.provider.queries[0][0],
        ("DELETE FROM author WHERE author.id = 2 RETURNING author.id"),
    )


async def test_remove_does_not_exist(sql_gateway):
    sql_gateway.provider.result.return_value = []
    assert (await sql_gateway.remove(2)) is False
    assert len(sql_gateway.provider.queries) == 1
    assert_query_equal(
        sql_gateway.provider.queries[0][0],
        ("DELETE FROM author WHERE author.id = 2 RETURNING author.id"),
    )


async def test_upsert(sql_gateway):
    record = {"id": 2, "name": "foo"}
    sql_gateway.provider.result.return_value = [record]
    assert await sql_gateway.upsert(record) == record
    assert len(sql_gateway.provider.queries) == 1
    assert_query_equal(
        sql_gateway.provider.queries[0][0],
        (
            f"INSERT INTO author (id, name) VALUES (2, 'foo') "
            f"ON CONFLICT (id) DO UPDATE SET "
            f"id = %(param_1)s, name = %(param_2)s "
            f"RETURNING {ALL_FIELDS}"
        ),
    )


@mock.patch.object(SQLGateway, "add")
async def test_upsert_no_id(add_m, sql_gateway):
    add_m.return_value = {"id": 5, "name": "foo"}
    assert await sql_gateway.upsert({"name": "foo"}) == add_m.return_value

    add_m.assert_awaited_once_with({"name": "foo"})
    assert len(sql_gateway.provider.queries) == 0


async def test_get_related_one_to_many(related_sql_gateway: SQLGateway):
    authors = [{"id": 2}, {"id": 3}]
    books = [
        {"id": 3, "title": "x", "book_type": "one", "author_id": 2},
        {"id": 4, "title": "y", "book_type": "two", "author_id": 2},
    ]
    related_sql_gateway.provider.result.return_value = books
    await related_sql_gateway._get_related_one_to_many(
        items=authors,
        field_name="books",
        fk_name="author_id",
    )

    assert authors == [{"id": 2, "books": books}, {"id": 3, "books": []}]
    assert len(related_sql_gateway.provider.queries) == 1
    assert_query_equal(
        related_sql_gateway.provider.queries[0][0],
        (
            "SELECT book.id, book.title, book.book_type, book.author_id "
            "FROM book WHERE book.author_id IN (2, 3)"
        ),
    )


@pytest.mark.parametrize(
    "books,current_books,expected_queries,query_results",
    [
        # no change
        (
            [{"id": 3, "title": "x", "book_type": "one", "author_id": 2}],
            [{"id": 3, "title": "x", "book_type": "one", "author_id": 2}],
            [],
            [],
        ),
        # added a book (without an id)
        (
            [{"title": "x", "book_type": "one", "author_id": 2}],
            [],
            [
                "INSERT INTO book (title, book_type, author_id) VALUES ('x', 'one', 2) "
                f"RETURNING {BOOK_FIELDS}"
            ],
            [[{"id": 3, "title": "x", "book_type": "one", "author_id": 2}]],
        ),
        # added a book (with an id)
        (
            [{"id": 3, "title": "x", "book_type": "one", "author_id": 2}],
            [],
            [
                "INSERT INTO book (id, title, book_type, "
                "author_id) VALUES (3, 'x', 'one', 2) "
                f"RETURNING {BOOK_FIELDS}"
            ],
            [[{"id": 3, "title": "x", "book_type": "one", "author_id": 2}]],
        ),
        # updated a book
        (
            [{"id": 3, "title": "x", "book_type": "one", "author_id": 2}],
            [{"id": 3, "title": "a", "book_type": "one", "author_id": 2}],
            [
                "UPDATE book SET id=3, title='x', book_type='one', "
                "author_id=2 WHERE book.id = 3 "
                f"RETURNING {BOOK_FIELDS}"
            ],
            [[{"id": 3, "title": "x", "book_type": "one", "author_id": 2}]],
        ),
        # replaced a book with a new one
        (
            [{"title": "x", "book_type": "one", "author_id": 2}],
            [{"id": 15, "title": "a", "book_type": "one", "author_id": 2}],
            [
                "INSERT INTO book (title, book_type, author_id) VALUES ('x', 'one', 2) "
                f"RETURNING {BOOK_FIELDS}",
                "DELETE FROM book WHERE book.id = 15 RETURNING book.id",
            ],
            [
                [{"id": 3, "title": "x", "book_type": "one", "author_id": 2}],
                [{"id": 15}],
            ],
        ),
    ],
)
async def test_set_related_one_to_many(
    related_sql_gateway: SQLGateway,
    books,
    current_books,
    expected_queries,
    query_results,
):
    author = {"id": 2, "books": books}
    related_sql_gateway.provider.result.side_effect = [current_books] + query_results
    result = author.copy()
    await related_sql_gateway._set_related_one_to_many(
        item=author,
        result=result,
        field_name="books",
        fk_name="author_id",
    )

    assert result == {
        "id": 2,
        "books": [{"id": 3, "title": "x", "book_type": "one", "author_id": 2}],
    }
    assert len(related_sql_gateway.provider.queries) == len(expected_queries) + 1
    assert_query_equal(
        related_sql_gateway.provider.queries[0][0],
        f"SELECT {BOOK_FIELDS} FROM book WHERE book.author_id = 2",
    )
    for (actual_query,), expected_query in zip(
        related_sql_gateway.provider.queries[1:], expected_queries
    ):
        assert_query_equal(actual_query, expected_query)


async def test_update_transactional(sql_gateway):
    existing = {"id": 2, "name": "foo"}
    expected = {"id": 2, "name": "bar"}
    sql_gateway.provider.result.side_effect = ([existing], [expected])
    actual = await sql_gateway.update_transactional(
        2, lambda x: {"id": x["id"], "name": "bar"}
    )
    assert actual == expected

    (queries,) = sql_gateway.provider.queries
    assert len(queries) == 2
    assert_query_equal(
        queries[0],
        f"SELECT {ALL_FIELDS} FROM author WHERE author.id = 2 FOR UPDATE",
    )
    assert_query_equal(
        queries[1],
        (
            "UPDATE author SET id=2, name='bar' WHERE author.id = 2 "
            f"RETURNING {ALL_FIELDS}"
        ),
    )


@pytest.mark.parametrize(
    "filters,sql",
    [
        ([], " WHERE true"),
        ([Filter(field="name", values=[])], " WHERE false"),
        ([Filter(field="name", values=["foo"])], " WHERE author.name = 'foo'"),
        (
            [Filter(field="name", values=["foo", "bar"])],
            " WHERE author.name IN ('foo', 'bar')",
        ),
        ([Filter(field="nonexisting", values=["foo"])], " WHERE false"),
        (
            [Filter(field="id", values=[1]), Filter(field="name", values=["foo"])],
            " WHERE author.id = 1 AND author.name = 'foo'",
        ),
    ],
)
async def test_exists(sql_gateway, filters, sql):
    sql_gateway.provider.result.return_value = [{"exists": True}]
    assert await sql_gateway.exists(filters) is True
    assert len(sql_gateway.provider.queries) == 1
    assert_query_equal(
        sql_gateway.provider.queries[0][0],
        f"SELECT true AS exists FROM author{sql} LIMIT 1",
    )
