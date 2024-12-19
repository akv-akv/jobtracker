from dataclasses import dataclass
from typing import List
from unittest import mock
from uuid import uuid4

import pytest

from src.domain.base.exceptions import DoesNotExist
from src.domain.base.root_entity import RootEntity
from src.repository.base.filter import Filter
from src.repository.base.pagination import Page, PageOptions
from src.repository.base.repository import Repository
from src.repository.in_memory.in_memory_gateway import InMemoryGateway


@dataclass(frozen=True)
class User(RootEntity):
    name: str


@pytest.fixture
def users():
    return [
        User.create(id=uuid4(), name="a"),
        User.create(id=uuid4(), name="b"),
        User.create(id=uuid4(), name="c"),
    ]


class UserRepository(Repository[User]):
    pass


@pytest.fixture
def user_repository(users: List[User]):
    return UserRepository(
        gateway=InMemoryGateway(data=[user.to_dict() for user in users])
    )


@pytest.fixture
def page_options():
    return PageOptions(limit=10, offset=0, order_by="id")


def test_entity_attr(user_repository):
    assert user_repository.entity is User


async def test_get(user_repository, users):
    actual = await user_repository.get(users[0].id)
    assert actual.name == users[0].name


async def test_get_does_not_exist(user_repository):
    with pytest.raises(DoesNotExist):
        await user_repository.get(uuid4())


@mock.patch.object(Repository, "filter")
async def test_all(filter_m, user_repository, page_options):
    filter_m.return_value = Page(total=0, items=[])
    assert await user_repository.all(page_options) is filter_m.return_value
    filter_m.assert_awaited_once_with([], params=page_options)


async def test_add(user_repository: UserRepository):
    actual = await user_repository.add(User.create(name="d"))
    assert actual.name == "d"


async def test_add_dict(user_repository: UserRepository):
    actual = await user_repository.add({"name": "d"})
    assert actual.name == "d"


async def test_add_dict_validates(user_repository: UserRepository):
    with pytest.raises(Exception):
        await user_repository.add({"id": 123})


@pytest.mark.parametrize("optimistic", [False, True])
async def test_update(user_repository: UserRepository, optimistic: bool, users):
    actual = await user_repository.update(
        id=users[1].id, values={"name": "updated"}, optimistic=optimistic
    )
    assert actual.name == "updated"


@pytest.mark.parametrize("optimistic", [False, True])
async def test_update_does_not_exist(user_repository: UserRepository, optimistic: bool):
    with pytest.raises(DoesNotExist):
        await user_repository.update(
            id=uuid4(), values={"name": "new_name"}, optimistic=optimistic
        )


@pytest.mark.parametrize("optimistic", [False, True])
async def test_update_validates(
    user_repository: UserRepository, optimistic: bool, users
):
    with pytest.raises(Exception):
        await user_repository.update(
            id=users[0].id, values={"id": uuid4()}, optimistic=optimistic
        )


async def test_remove(user_repository: UserRepository, users):
    assert await user_repository.remove(users[1].id)


async def test_remove_does_not_exist(user_repository: UserRepository):
    assert not await user_repository.remove(uuid4())


async def test_upsert_updates(user_repository: UserRepository, users):
    actual = await user_repository.upsert(User.create(id=users[0].id, name="updated"))
    assert actual.name == "updated"


async def test_upsert_adds(user_repository: UserRepository):
    new_id = uuid4()
    actual = await user_repository.upsert(User.create(id=new_id, name="new_user"))
    assert actual.name == "new_user"


@mock.patch.object(InMemoryGateway, "count")
async def test_filter(count_m, user_repository: UserRepository, users):
    actual = await user_repository.filter([Filter(field="name", values=["b"])])
    assert actual.total == 1
    assert actual.items[0].name == "b"
    assert not count_m.called


@mock.patch.object(InMemoryGateway, "count")
async def test_filter_with_pagination(
    count_m, user_repository: UserRepository, users, page_options
):
    actual = await user_repository.filter(
        [Filter(field="name", values=["b"])], page_options
    )
    assert actual.total == 1
    assert actual.items[0].name == "b"
    assert actual.limit == page_options.limit
    assert actual.offset == page_options.offset
    assert not count_m.called


@mock.patch.object(Repository, "filter")
async def test_by(filter_m, user_repository: UserRepository, page_options):
    filter_m.return_value = Page(total=0, items=[])
    assert await user_repository.by("name", "b", page_options) is filter_m.return_value
    filter_m.assert_awaited_once_with(
        [Filter(field="name", values=["b"])], params=page_options
    )


@mock.patch.object(InMemoryGateway, "exists")
async def test_exists(gateway_exists, user_repository):
    gateway_exists.return_value = True
    assert await user_repository.exists([Filter(field="name", values=["b"])])


@mock.patch.object(InMemoryGateway, "count")
async def test_count(count_m, user_repository):
    count_m.return_value = 1
    assert await user_repository.count([]) == 1
