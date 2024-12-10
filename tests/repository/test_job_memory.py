from datetime import datetime
from uuid import uuid4

import pytest

from src.domain.entity.job import Job, JobStatus
from src.repository.job_memory import InMemoryJobRepository


@pytest.fixture
def repository():
    """Fixture to provide a fresh repository for each test."""
    return InMemoryJobRepository()


@pytest.fixture
def sample_job():
    """Fixture to provide a sample job instance."""
    return Job(
        id=uuid4(),
        title="Software Engineer",
        company="Tech Corp",
        status=JobStatus.APPLIED,
        country="USA",
        city="New York",
        description="A challenging and rewarding job opportunity.",
    )


def test_create_job(repository, sample_job):
    """Test creating a job."""
    repository.create(sample_job)
    assert repository.read(sample_job.id) == sample_job


def test_create_duplicate_job(repository, sample_job):
    """Test creating a duplicate job raises an error."""
    repository.create(sample_job)
    with pytest.raises(ValueError, match="Job with id .* already exists."):
        repository.create(sample_job)


def test_read_job(repository, sample_job):
    """Test reading a job by ID."""
    repository.create(sample_job)
    job = repository.read(sample_job.id)
    assert job == sample_job


def test_read_nonexistent_job(repository):
    """Test reading a non-existent job returns None."""
    job = repository.read(uuid4())
    assert job is None


def test_update_job(repository, sample_job):
    """Test updating an existing job."""
    repository.create(sample_job)
    updated_title = "Senior Software Engineer"
    sample_job.title = updated_title

    repository.update(sample_job)
    job = repository.read(sample_job.id)
    assert job.title == updated_title


def test_update_nonexistent_job(repository, sample_job):
    """Test updating a non-existent job raises an error."""
    with pytest.raises(ValueError, match="Job with id .* does not exist."):
        repository.update(sample_job)


def test_delete_job(repository, sample_job):
    """Test deleting a job."""
    repository.create(sample_job)
    repository.delete(sample_job.id)
    assert repository.read(sample_job.id) is None


def test_delete_nonexistent_job(repository):
    """Test deleting a non-existent job raises an error."""
    with pytest.raises(ValueError, match="Job with id .* does not exist."):
        repository.delete(uuid4())


def test_list_jobs(repository, sample_job):
    """Test listing all jobs."""
    repository.create(sample_job)
    jobs = repository.list()
    assert len(jobs) == 1
    assert jobs[0] == sample_job


def test_list_jobs_empty(repository):
    """Test listing jobs when repository is empty."""
    jobs = repository.list()
    assert jobs == []


@pytest.fixture
def add_two_jobs(repository):
    repository.jobs = {
        uuid4(): Job(
            id=uuid4(),
            title="Engineer",
            company="TechCorp",
            status=JobStatus.APPLIED,
            country="USA",
            city="NY",
            description="Job 1",
            date_applied=datetime(2023, 1, 2),
            date_updated=datetime(2023, 6, 15),
        ),
        uuid4(): Job(
            id=uuid4(),
            title="Manager",
            company="BizCorp",
            status=JobStatus.INTERVIEWING,
            country="USA",
            city="SF",
            description="Job 2",
            date_applied=datetime(2023, 3, 1),
            date_updated=datetime(2023, 7, 20),
        ),
    }
    return repository


def test_list_jobs_with_date_filters(repository):
    filters = {"date_applied__gt": "2023-01-01"}
    result = repository.list(filters)
    assert len(result) == 2

    filters = {"date_applied__lt": "2023-03-01"}
    result = repository.list(filters)
    assert len(result) == 1
    assert result[0].title == "Engineer"

    filters = {"date_updated__lt": "2023-07-01"}
    result = repository.list(filters)
    assert len(result) == 1
    assert result[0].title == "Engineer"


def test_list_jobs_with_multiple_filters(repository):
    filters = {
        "status": ["APPLIED"],
        "company": "TechCorp",
        "date_applied__gt": "2023-01-01",
    }
    result = repository.list(filters)
    assert len(result) == 1
    assert result[0].status == JobStatus.APPLIED
    assert result[0].company == "TechCorp"
