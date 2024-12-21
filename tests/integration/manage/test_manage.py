from datetime import datetime, timezone

import pytest

pytestmark = pytest.mark.integration


@pytest.mark.asyncio
async def test_manage_create(manage_job):
    """Test the create functionality of the manage layer."""
    data = {
        "t": "foo",
        "f": 1.23,
        "b": True,
        "updated_at": datetime(2016, 6, 22, 19, 10, 25, tzinfo=timezone.utc),
    }

    # Use the manage layer to create a new entry
    created = await manage_job.create(data)

    # Validate the created data (add additional checks as needed)
    assert created.t == data["t"]
    assert created.f == data["f"]
    assert created.b == data["b"]
    assert created.updated_at == data["updated_at"]
