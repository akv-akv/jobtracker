from datetime import datetime, timezone
from uuid import UUID

import pytest

from src.application.domain.enums.country import Country

pytestmark = pytest.mark.integration


@pytest.fixture
def data():
    data = {
        "t": "foo",
        "f": 1.23,
        "b": True,
        "c": Country.UnitedArabEmirates,
        "updated_at": datetime(2016, 6, 22, 19, 10, 25, tzinfo=timezone.utc),
    }
    return data


async def test_manage_create(manage_job, data):
    """Test the create functionality of the manage layer."""
    created = await manage_job.create(data)

    assert created.t == data["t"]
    assert created.f == data["f"]
    assert created.b == data["b"]
    assert created.updated_at == data["updated_at"]


async def test_manage_retrieve(manage_job, data):
    """Test the create functionality of the manage layer."""
    created = await manage_job.create(data)
    id = created.id

    assert isinstance(id, UUID)
    retrieved = await manage_job.retrieve(id)

    assert retrieved.t == data["t"]
    assert retrieved.f == data["f"]
    assert retrieved.b == data["b"]
    assert retrieved.updated_at == data["updated_at"]


async def test_manage_update(manage_job, data):
    """Test the create functionality of the manage layer."""
    created = await manage_job.create(data)
    id = created.id
    data["c"] = Country.Oman
    updated = await manage_job.update(id, data)

    assert updated.c != created.c
    assert isinstance(updated.c, Country)
