from datetime import datetime
from uuid import uuid4

import pytest

from src.domain.entity.job import Job, JobStatus
from src.repository.job_memory import InMemoryJobRepository
from src.responses.response import ResponseTypes
from src.use_case.update_job import update_job


@pytest.fixture
def repository_with_job():
    repo = InMemoryJobRepository()
    job_id = uuid4()
    repo.create(
        Job(
            id=job_id,
            title="Software Engineer",
            company="TechCorp",
            status=JobStatus.APPLIED,
            country="USA",
            city="NY",
            description="A job opportunity.",
            date_applied=datetime(2023, 1, 10),
            date_updated=datetime(2023, 1, 10),
        )
    )
    return repo


def test_update_job_success(repository_with_job):
    """Test partial update of a job."""
    existing_job = list(repository_with_job.jobs.values())[0]
    update_data = {
        "id": existing_job.id,
        "title": "Senior Software Engineer",  # Updated field
        "city": "San Francisco",  # Updated field
    }

    response = update_job(update_data, repository_with_job)
    updated_job = repository_with_job.read(existing_job.id)

    assert response.type == ResponseTypes.SUCCESS
    assert updated_job.title == "Senior Software Engineer"
    assert updated_job.city == "San Francisco"
    assert updated_job.company == existing_job.company  # Unchanged field


def test_update_job_not_found(repository_with_job):
    """Test updating a non-existent job."""
    update_data = {
        "id": uuid4(),  # Non-existent ID
        "title": "Senior Software Engineer",
    }

    response = update_job(update_data, repository_with_job)

    assert response.type == ResponseTypes.RESOURCE_ERROR
    assert response.message == "Job not found."


def test_update_job_invalid_request(repository_with_job):
    """Test invalid update request."""
    invalid_data = "invalid data"

    response = update_job(invalid_data, repository_with_job)

    assert response.type == ResponseTypes.PARAMETERS_ERROR
    assert response.message == [
        {"message": "Must be a dictionary.", "parameter": "data"}
    ]


def test_update_job_missing_id(repository_with_job):
    """Test update request missing the 'id' field."""
    update_data = {"title": "Senior Software Engineer"}

    response = update_job(update_data, repository_with_job)

    assert response.type == ResponseTypes.PARAMETERS_ERROR
    assert response.message == [{"message": "'id' is required.", "parameter": "id"}]
