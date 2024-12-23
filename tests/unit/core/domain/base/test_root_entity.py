from datetime import datetime, timezone
from unittest import mock
from uuid import UUID, uuid4

import pytest
from pydantic import ValidationError

from src.core.domain.root_entity import RootEntity

# Example entity extending RootEntity


class User(RootEntity):
    name: str


@pytest.fixture
def user():
    return User(
        id=uuid4(),
        name="jan",
        created_at=datetime(2010, 1, 1, tzinfo=timezone.utc),
        updated_at=datetime(2020, 1, 1, tzinfo=timezone.utc),
    )


@pytest.fixture
def patched_now():
    SOME_DATETIME = datetime(2023, 1, 1, tzinfo=timezone.utc)
    with mock.patch("src.core.domain.root_entity.now", return_value=SOME_DATETIME):
        yield SOME_DATETIME


def test_create(patched_now):
    obj = User.create(name="piet")

    assert isinstance(obj.id, UUID)  # UUID is auto-generated if not provided
    assert obj.name == "piet"
    assert obj.created_at == patched_now
    assert obj.updated_at == patched_now


def test_create_with_id():
    id = uuid4()
    obj = User.create(id=id, name="piet")

    assert obj.id == id
    assert obj.name == "piet"


def test_create_with_wrong_type_id():
    with pytest.raises(ValidationError) as e:
        User.create(id=1, name="piet")

    assert "UUID input should be a string, bytes or UUID object" in str(e.value)


def test_update(user, patched_now):
    actual = user.update(name="piet")

    assert actual is not user  # New instance should be returned
    assert actual.name == "piet"
    assert actual.updated_at == patched_now
    assert actual.created_at == user.created_at  # `created_at` should remain unchanged


def test_update_including_id(user):
    with pytest.raises(Exception) as e:
        user.update(id=uuid4(), name="piet")

    assert "Cannot change the id of an entity" in str(e.value)


@pytest.mark.parametrize("new_id", [None, 42, uuid4()])
def test_update_with_wrong_id(user, new_id):
    with pytest.raises(Exception, match="Cannot change the id of an entity"):
        user.update(id=new_id, name="piet")


def test_hashable(user):
    user2 = user.update(name="piet")
    assert len({user, user2}) == 2  # Both should be distinct in a set


def test_equality():
    user1 = User.create(name="jan")
    user2 = user1.update(name="jan")
    user3 = user1

    assert user1 != user2
    assert user1 == user3


@pytest.mark.parametrize(
    "invalid_field,value,expected_exception,expected_message",
    [
        (
            "created_at",
            "not-a-datetime",
            ValueError,
            "Cannot change the created_at timestamp",
        ),
        (
            "updated_at",
            "not-a-datetime",
            ValidationError,
            "Input should be a valid datetime or date",
        ),
    ],
)
def test_invalid_dates(
    user, invalid_field, value, expected_exception, expected_message
):
    with pytest.raises(expected_exception) as e:
        user.update(**{invalid_field: value})

    assert expected_message in str(e.value)


# Entity with UUID as ID
class WithUUID(RootEntity):
    id: UUID


def test_generate_uuid():
    entity = WithUUID.create()
    assert isinstance(entity.id, UUID)


@pytest.mark.parametrize(
    "user1, user2, expected_equal",
    [
        (
            User(
                id=uuid4(),
                name="jan",
                created_at=datetime(2010, 1, 1, tzinfo=timezone.utc),
                updated_at=datetime(2020, 1, 1, tzinfo=timezone.utc),
            ),
            User(
                id=uuid4(),
                name="jan",
                created_at=datetime(2010, 1, 1, tzinfo=timezone.utc),
                updated_at=datetime(2020, 1, 1, tzinfo=timezone.utc),
            ),
            False,
        ),
        (
            User(
                id=uuid4(),
                name="jan",
                created_at=datetime(2010, 1, 1, tzinfo=timezone.utc),
                updated_at=datetime(2020, 1, 1, tzinfo=timezone.utc),
            ),
            User(
                id=uuid4(),
                name="different",
                created_at=datetime(2010, 1, 1, tzinfo=timezone.utc),
                updated_at=datetime(2020, 1, 1, tzinfo=timezone.utc),
            ),
            False,
        ),
        (
            user,
            user,
            True,
        ),
    ],
)
def test_hash_behavior(user1, user2, expected_equal):
    hash_1 = user1.__hash__
    hash_2 = user2.__hash__
    assert (hash_1 == hash_2) == expected_equal
