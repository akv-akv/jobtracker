from uuid import uuid4

import pytest

from src.domain.entity.job import Job, JobStatus, WorkSettingType
from src.domain.entity.user import User
from src.domain.enums.country import Country
from src.responses.response import ResponseTypes
from src.use_case.delete_job import delete_job


@pytest.fixture
def job_id():
    return uuid4()


@pytest.fixture
async def repository_with_job(repository, job_id):
    data = {
        "id": job_id,
        "user": User.create(name="Kirill"),
        "title": "Software Engineer",
        "company": "TechCorp",
        "status": JobStatus.APPLIED,
        "country": Country.US,
        "work_setting_type": WorkSettingType.ONSITE,
        "city": "NY",
        "description": "A challenging job opportunity.",
    }
    job = Job.create(**data)
    await repository.add(job)
    return repository


async def test_delete_job_success(repository_with_job, job_id):
    """Test deleting a job successfully."""
    assert await repository_with_job.count(filters=[]) == 1
    response = await delete_job(job_id, repository_with_job)

    assert response.type == ResponseTypes.SUCCESS
    assert response.value == job_id
    assert await repository_with_job.count(filters=[]) == 0


async def test_delete_job_not_found(repository_with_job):
    """Test deleting a non-existent job."""
    assert await repository_with_job.count(filters=[]) == 1
    response = await delete_job(uuid4(), repository_with_job)
    assert await repository_with_job.count(filters=[]) == 1
    assert response.type == ResponseTypes.PARAMETERS_ERROR
    assert "Job with id" in response.message
    assert "does not exist" in response.message


async def test_delete_job_invalid_id(repository_with_job):
    """Test delete request with an invalid job ID."""
    invalid_id = "not-a-uuid"

    response = await delete_job(invalid_id, repository_with_job)

    assert response.type == ResponseTypes.PARAMETERS_ERROR
    assert [{"message": "Must be UUID.", "parameter": "id"}] == response.message
