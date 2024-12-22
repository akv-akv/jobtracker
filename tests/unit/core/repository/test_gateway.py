from datetime import datetime, timezone
from unittest import mock
from uuid import uuid4

import pytest

from src.core.domain.exceptions import AlreadyExists, DoesNotExist
from src.core.repository.base.filter import Filter
from src.core.repository.base.pagination import PageOptions
from src.core.repository.in_memory.in_memory_gateway import InMemoryGateway

ids = [uuid4() for i in range(3)]


@pytest.fixture
def in_memory_gateway():
    return InMemoryGateway(
        data=[
            {
                "id": ids[0],
                "name": "a",
                "updated_at": datetime(2020, 1, 1, tzinfo=timezone.utc),
            },
            {
                "id": ids[1],
                "name": "b",
                "updated_at": datetime(2020, 1, 2, tzinfo=timezone.utc),
            },
            {
                "id": ids[2],
                "name": "c",
                "updated_at": datetime(2020, 1, 3, tzinfo=timezone.utc),
            },
        ]
    )


# Test `get` method
@pytest.mark.parametrize(
    "id, expected",
    [
        (
            ids[0],
            {
                "id": ids[0],
                "name": "a",
                "updated_at": datetime(2020, 1, 1, tzinfo=timezone.utc),
            },
        ),
        (uuid4(), None),
    ],
)
async def test_get(in_memory_gateway, id, expected):
    actual = await in_memory_gateway.get(id)
    assert actual == expected


# Test `add` method
async def test_add(in_memory_gateway):
    id = uuid4()
    record = {"id": id, "name": "d"}
    await in_memory_gateway.add(record)
    print(in_memory_gateway.data)
    assert in_memory_gateway.data[id] == record


async def test_add_already_exists(in_memory_gateway):
    with pytest.raises(AlreadyExists):
        await in_memory_gateway.add({"id": ids[0], "name": "duplicate"})


# Test `update` method
async def test_update(in_memory_gateway):
    record = {"id": ids[2], "name": "updated", "updated_at": datetime.now(timezone.utc)}
    await in_memory_gateway.update(record)
    assert in_memory_gateway.data[ids[2]]["name"] == "updated"


async def test_update_does_not_exist(in_memory_gateway):
    with pytest.raises(DoesNotExist):
        await in_memory_gateway.update({"id": uuid4(), "name": "nonexistent"})


# Test `remove` method
@pytest.mark.parametrize("id, expected", [(ids[2], True), (uuid4(), False)])
async def test_remove(in_memory_gateway, id, expected):
    assert await in_memory_gateway.remove(id) == expected


# Test `filter` method
async def test_filter(in_memory_gateway):
    actual = await in_memory_gateway.filter([Filter(field="name", values=["b"])])
    assert actual == [
        {
            "id": ids[1],
            "name": "b",
            "updated_at": datetime(2020, 1, 2, 0, 0, tzinfo=timezone.utc),
        }
    ]


async def test_filter_with_params(in_memory_gateway):
    params = PageOptions(limit=2, offset=0, order_by="updated_at", ascending=True)
    actual = await in_memory_gateway.filter([], params=params)
    assert [item["id"] for item in actual] == [ids[0], ids[1]]


# Test `count` method
async def test_count(in_memory_gateway):
    actual = await in_memory_gateway.count([Filter(field="name", values=["a"])])
    assert actual == 1


# Test `exists` method
@pytest.mark.parametrize(
    "filters, expected",
    [
        ([Filter(field="name", values=["b"])], True),
        ([Filter(field="name", values=["z"])], False),
    ],
)
async def test_exists(in_memory_gateway, filters, expected):
    assert await in_memory_gateway.exists(filters) == expected


# Test `update_transactional`
@mock.patch.object(InMemoryGateway, "update")
async def test_update_transactional(update_mock):
    record = {
        "id": ids[2],
        "name": "c",
        "updated_at": datetime(2020, 1, 3, tzinfo=timezone.utc),
    }
    gateway = InMemoryGateway([record])
    await gateway.update_transactional(ids[2], lambda x: {"name": x["name"] + "x"})
    update_mock.assert_awaited_once_with(
        {"name": "cx"}, if_unmodified_since=record["updated_at"]
    )
