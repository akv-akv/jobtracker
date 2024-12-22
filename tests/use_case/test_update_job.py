from uuid import uuid4

import pytest

from src.application.domain.entity.job import JobStatus, WorkSettingType
from src.application.domain.entity.user import User
from src.application.domain.enums.country import Country
from src.application.use_case.update_job import update_job
from src.core.responses.response import ResponseTypes


@pytest.fixture
def job_id():
    return uuid4()


@pytest.fixture
async def job_manager_with_job(job_manager, job_id):
    data = {
        "id": job_id,
        "user": User.create(name="Kirill"),
        "title": "Software Engineer",
        "company": "TechCorp",
        "status": JobStatus.APPLIED,
        "country": Country.UnitedStates,
        "work_setting_type": WorkSettingType.ONSITE,
        "city": "NY",
        "description": "A challenging job opportunity.",
    }
    await job_manager.create(data)
    return job_manager


async def test_update_job_success(job_manager_with_job, job_id):
    """Test partial update of a job."""
    update_data = {
        "id": job_id,
        "title": "Senior Software Engineer",  # Updated field
        "city": "San Francisco",  # Updated field
    }

    response = await update_job(update_data, job_manager_with_job)
    updated_job = await job_manager_with_job.retrieve(job_id)

    assert response.type == ResponseTypes.SUCCESS
    assert updated_job.title == "Senior Software Engineer"
    assert updated_job.city == "San Francisco"
    assert updated_job.company == "TechCorp"  # Unchanged field


async def test_update_job_not_found(job_manager_with_job):
    """Test updating a non-existent job."""
    update_data = {
        "id": uuid4(),  # Non-existent ID
        "title": "Senior Software Engineer",
    }

    response = await update_job(update_data, job_manager_with_job)

    assert response.type == ResponseTypes.SYSTEM_ERROR
    assert "does not exist" in response.message


async def test_update_job_invalid_request(job_manager_with_job):
    """Test invalid update request."""
    invalid_data = "invalid data"

    response = await update_job(invalid_data, job_manager_with_job)

    assert response.type == ResponseTypes.PARAMETERS_ERROR
    assert response.message == [
        {"message": "Must be a dictionary.", "parameter": "data"}
    ]


async def test_update_job_missing_id(job_manager_with_job):
    """Test update request missing the 'id' field."""
    update_data = {"title": "Senior Software Engineer"}

    response = await update_job(update_data, job_manager_with_job)

    assert response.type == ResponseTypes.PARAMETERS_ERROR
    assert response.message == [{"message": "'id' is required.", "parameter": "id"}]
