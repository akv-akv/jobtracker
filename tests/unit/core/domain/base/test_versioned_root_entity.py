from datetime import datetime, timezone
from unittest import mock
from uuid import UUID

import pytest

from src.core.domain.versioned_root_entity import VersionedRootEntity

# Example entity extending RootEntity


class User(VersionedRootEntity):
    name: str


@pytest.fixture
def patched_now():
    SOME_DATETIME = datetime(2023, 1, 1, tzinfo=timezone.utc)
    with mock.patch("src.core.domain.root_entity.now", return_value=SOME_DATETIME):
        yield SOME_DATETIME


def test_create(patched_now):
    obj = User.create(**{"name": "Bob"})

    assert isinstance(obj.id, UUID)  # UUID is auto-generated if not provided
    assert obj.name == "Bob"
    assert obj.created_at == patched_now  # Use the patched timestamp
    assert obj.updated_at == patched_now
    assert obj.version == 1


def test_update(patched_now):
    user = User.create(**{"name": "Bob"})
    new_version = user.update(**{"name": "John"})

    assert new_version is not user  # New instance should be returned
    assert new_version.name == "John"
    assert new_version.id == user.id
    assert new_version.version == user.version + 1
    assert new_version.updated_at == patched_now
