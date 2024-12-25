from uuid import uuid4

import pytest

from src.application.domain.entity.job import JobStatus, WorkSettingType
from src.application.domain.enums.country import Country
from src.application.use_case.job.delete_job import delete_job
from src.core.responses.response import ResponseTypes


@pytest.fixture
def job_id():
    return uuid4()


@pytest.fixture
async def job_manager_with_job(job_manager, job_id):
    data = {
        "id": job_id,
        "user_id": uuid4(),
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


async def test_delete_job_success(job_manager_with_job, job_id):
    """Test deleting a job successfully."""
    assert await job_manager_with_job.count(filters=[]) == 1
    response = await delete_job(job_id, job_manager_with_job)

    assert response.type == ResponseTypes.SUCCESS
    assert response.value == job_id
    assert await job_manager_with_job.count(filters=[]) == 0


async def test_delete_job_not_found(job_manager_with_job):
    """Test deleting a non-existent job."""
    assert await job_manager_with_job.count(filters=[]) == 1
    response = await delete_job(uuid4(), job_manager_with_job)
    assert await job_manager_with_job.count(filters=[]) == 1
    assert response.type == ResponseTypes.PARAMETERS_ERROR
    assert "Job with id" in response.message
    assert "does not exist" in response.message


async def test_delete_job_invalid_id(job_manager_with_job):
    """Test delete request with an invalid job ID."""
    invalid_id = "not-a-uuid"

    response = await delete_job(invalid_id, job_manager_with_job)

    assert response.type == ResponseTypes.PARAMETERS_ERROR
    assert [{"message": "Must be UUID.", "parameter": "id"}] == response.message
