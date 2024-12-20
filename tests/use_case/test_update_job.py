from uuid import uuid4

import pytest

from src.domain.entity.job import Job, JobStatus, WorkSettingType
from src.domain.entity.user import User
from src.domain.enums.country import Country
from src.responses.response import ResponseTypes
from src.use_case.add_job import add_job
from src.use_case.update_job import update_job


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
    Job.create(**data)
    await add_job(data, repository)
    return repository


async def test_update_job_success(repository_with_job, job_id):
    """Test partial update of a job."""
    update_data = {
        "id": job_id,
        "title": "Senior Software Engineer",  # Updated field
        "city": "San Francisco",  # Updated field
    }

    response = await update_job(update_data, repository_with_job)
    updated_job = await repository_with_job.get(job_id)

    assert response.type == ResponseTypes.SUCCESS
    assert updated_job.title == "Senior Software Engineer"
    assert updated_job.city == "San Francisco"
    assert updated_job.company == "TechCorp"  # Unchanged field


async def test_update_job_not_found(repository_with_job):
    """Test updating a non-existent job."""
    update_data = {
        "id": uuid4(),  # Non-existent ID
        "title": "Senior Software Engineer",
    }

    response = await update_job(update_data, repository_with_job)

    assert response.type == ResponseTypes.SYSTEM_ERROR
    assert "does not exist" in response.message


async def test_update_job_invalid_request(repository_with_job):
    """Test invalid update request."""
    invalid_data = "invalid data"

    response = await update_job(invalid_data, repository_with_job)

    assert response.type == ResponseTypes.PARAMETERS_ERROR
    assert response.message == [
        {"message": "Must be a dictionary.", "parameter": "data"}
    ]


async def test_update_job_missing_id(repository_with_job):
    """Test update request missing the 'id' field."""
    update_data = {"title": "Senior Software Engineer"}

    response = await update_job(update_data, repository_with_job)

    assert response.type == ResponseTypes.PARAMETERS_ERROR
    assert response.message == [{"message": "'id' is required.", "parameter": "id"}]
