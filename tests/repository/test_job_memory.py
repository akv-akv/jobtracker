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
        date_applied=datetime(2023, 1, 1),
        date_updated=datetime(2023, 1, 2),
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
    data = {"title": "Senior Software Engineer"}
    repository.update(job_id=sample_job.id, data=data)
    job = repository.read(sample_job.id)
    assert job.title == data["title"]


def test_update_nonexistent_job(repository, sample_job):
    """Test updating a non-existent job raises an error."""
    with pytest.raises(ValueError, match="Job with id .* does not exist."):
        repository.update(sample_job.id, {})


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
def repository_with_jobs():
    """Fixture to populate the repository with sample jobs."""
    repo = InMemoryJobRepository()
    repo.create(
        Job(
            id=uuid4(),
            title="Software Engineer",
            company="TechCorp",
            status=JobStatus.APPLIED,
            country="USA",
            city="NY",
            description="Job 1",
            date_applied=datetime(2023, 1, 10),
            date_updated=datetime(2023, 6, 15),
        )
    )
    repo.create(
        Job(
            id=uuid4(),
            title="Product Manager",
            company="BizCorp",
            status=JobStatus.INTERVIEWING,
            country="USA",
            city="SF",
            description="Job 2",
            date_applied=datetime(2023, 3, 5),
            date_updated=datetime(2023, 7, 20),
        )
    )
    repo.create(
        Job(
            id=uuid4(),
            title="Data Scientist",
            company="DataCorp",
            status=JobStatus.REJECTED,
            country="Canada",
            city="Toronto",
            description="Job 3",
            date_applied=datetime(2023, 2, 15),
            date_updated=datetime(2023, 5, 30),
        )
    )
    return repo


def test_list_all_jobs(repository_with_jobs):
    """Test listing all jobs without filters."""
    result = repository_with_jobs.list()
    assert len(result) == 3  # Ensure all jobs are returned


@pytest.mark.parametrize(
    "filters,expected_titles",
    [
        ({"status": [JobStatus.APPLIED]}, ["Software Engineer"]),
        ({"status": [JobStatus.INTERVIEWING]}, ["Product Manager"]),
        ({"status": [JobStatus.REJECTED]}, ["Data Scientist"]),
    ],
)
def test_list_jobs_by_status(repository_with_jobs, filters, expected_titles):
    """Test listing jobs filtered by status."""
    result = repository_with_jobs.list(filters)
    titles = [job.title for job in result]
    assert titles == expected_titles


@pytest.mark.parametrize(
    "filters,expected_titles",
    [
        ({"company": "TechCorp"}, ["Software Engineer"]),
        ({"company": "BizCorp"}, ["Product Manager"]),
        ({"company": "DataCorp"}, ["Data Scientist"]),
    ],
)
def test_list_jobs_by_company(repository_with_jobs, filters, expected_titles):
    """Test listing jobs filtered by company."""
    result = repository_with_jobs.list(filters)
    titles = [job.title for job in result]
    assert titles == expected_titles


@pytest.mark.parametrize(
    "filters,expected_titles",
    [
        ({"country": "USA"}, ["Software Engineer", "Product Manager"]),
        ({"country": "Canada"}, ["Data Scientist"]),
    ],
)
def test_list_jobs_by_country(repository_with_jobs, filters, expected_titles):
    """Test listing jobs filtered by country."""
    result = repository_with_jobs.list(filters)
    titles = [job.title for job in result]
    assert titles == expected_titles


@pytest.mark.parametrize(
    "filters,expected_titles",
    [
        ({"city": "NY"}, ["Software Engineer"]),
        ({"city": "SF"}, ["Product Manager"]),
        ({"city": "Toronto"}, ["Data Scientist"]),
    ],
)
def test_list_jobs_by_city(repository_with_jobs, filters, expected_titles):
    """Test listing jobs filtered by city."""
    result = repository_with_jobs.list(filters)
    titles = [job.title for job in result]
    assert titles == expected_titles


@pytest.mark.parametrize(
    "filters,expected_titles",
    [
        ({"date_applied__eq": datetime(2023, 1, 10)}, ["Software Engineer"]),
        (
            {"date_applied__gt": datetime(2023, 2, 1)},
            ["Product Manager", "Data Scientist"],
        ),
        (
            {"date_applied__lt": datetime(2023, 3, 1)},
            ["Software Engineer", "Data Scientist"],
        ),
    ],
)
def test_list_jobs_by_date_applied(repository_with_jobs, filters, expected_titles):
    """Test listing jobs filtered by date_applied."""
    result = repository_with_jobs.list(filters)
    titles = [job.title for job in result]
    assert titles == expected_titles


@pytest.mark.parametrize(
    "filters,expected_titles",
    [
        ({"date_updated__eq": datetime(2023, 6, 15)}, ["Software Engineer"]),
        (
            {"date_updated__gt": datetime(2023, 6, 1)},
            ["Software Engineer", "Product Manager"],
        ),
        ({"date_updated__lt": datetime(2023, 6, 1)}, ["Data Scientist"]),
    ],
)
def test_list_jobs_by_date_updated(repository_with_jobs, filters, expected_titles):
    """Test listing jobs filtered by date_updated."""
    result = repository_with_jobs.list(filters)
    titles = [job.title for job in result]
    assert titles == expected_titles


def test_list_jobs_with_multiple_filters(repository_with_jobs):
    """Test listing jobs with multiple filters."""
    filters = {
        "status": [JobStatus.APPLIED],
        "company": "TechCorp",
        "country": "USA",
        "date_applied__gt": datetime(2023, 1, 1),
    }
    result = repository_with_jobs.list(filters)
    titles = [job.title for job in result]
    assert len(result) == 1
    assert titles == ["Software Engineer"]
