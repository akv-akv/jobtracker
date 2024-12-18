from datetime import datetime
from uuid import uuid4

import pytest

from src.domain.entity.job import Job, JobStatus
from src.repository.base.repository import Repository
from src.repository.in_memory_gateway import InMemoryGateway
from src.responses.response import ResponseTypes
from src.use_case.add_job import add_job


class JobRepository(Repository[Job]):
    pass


@pytest.fixture
def repository():
    gateway = InMemoryGateway([])

    repository = JobRepository(gateway)
    return repository


async def test_add_job_success(repository):
    """Test adding a job successfully."""
    data = {
        "id": uuid4(),
        "title": "Software Engineer",
        "company": "TechCorp",
        "status": JobStatus.APPLIED,
        "country": "USA",
        "city": "NY",
        "description": "A challenging job opportunity.",
    }
    response = add_job(data, repository)
    added_job = repository.get(data["id"])

    assert response.type == ResponseTypes.SUCCESS
    assert added_job.title == "Software Engineer"
    assert added_job.company == "TechCorp"


def test_add_job_invalid_request(repository):
    """Test adding a job with invalid input data."""
    invalid_data = "invalid data"

    response = add_job(invalid_data, repository)

    assert response.type == ResponseTypes.PARAMETERS_ERROR
    assert "Must be a dictionary." in response.message[0]["message"]


def test_add_job_duplicate_id(repository):
    """Test adding a job with a duplicate ID."""
    data = {
        "id": uuid4(),
        "title": "Software Engineer",
        "company": "TechCorp",
        "status": JobStatus.APPLIED,
        "country": "USA",
        "city": "NY",
        "description": "A challenging job opportunity.",
        "date_applied": datetime(2023, 1, 10),
        "date_updated": datetime(2023, 1, 10),
    }

    add_job(data, repository)  # First add
    response = add_job(data, repository)  # Attempt duplicate add

    assert response.type == ResponseTypes.PARAMETERS_ERROR
    assert "already exists" in response.message
