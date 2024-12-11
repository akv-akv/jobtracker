from uuid import uuid4

import pytest

from src.domain.entity.job import Job, JobStatus
from src.repository.job_memory import InMemoryJobRepository
from src.responses.response import ResponseTypes
from src.use_case.delete_job import delete_job


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
        )
    )
    return repo


def test_delete_job_success(repository_with_job):
    """Test deleting a job successfully."""
    existing_job = list(repository_with_job.jobs.values())[0]
    response = delete_job(existing_job.id, repository_with_job)

    assert response.type == ResponseTypes.SUCCESS
    assert response.value == existing_job.id
    assert len(repository_with_job.list()) == 0


def test_delete_job_not_found(repository_with_job):
    """Test deleting a non-existent job."""
    response = delete_job(uuid4(), repository_with_job)

    assert response.type == ResponseTypes.PARAMETERS_ERROR
    assert "Job with id" in response.message
    assert "does not exist" in response.message


def test_delete_job_invalid_id(repository_with_job):
    """Test delete request with an invalid job ID."""
    invalid_id = "not-a-uuid"

    response = delete_job(invalid_id, repository_with_job)

    assert response.type == ResponseTypes.PARAMETERS_ERROR
    assert [{"message": "Must be UUID.", "parameter": "id"}] == response.message
