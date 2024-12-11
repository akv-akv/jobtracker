from datetime import datetime
from uuid import uuid4

import pytest

from src.domain.entity.job import Job, JobStatus
from src.repository.job_memory import InMemoryJobRepository
from src.responses.response import ResponseTypes
from src.use_case.list_jobs import list_jobs


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
            date_applied=datetime(2023, 1, 2),
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


def test_list_jobs_success_without_filters(repository_with_jobs):
    """Test listing all jobs without filters."""
    response = list_jobs(filters=None, repository=repository_with_jobs)

    assert response.type == ResponseTypes.SUCCESS
    assert len(response.value) == 3
    assert {job.title for job in response.value} == {
        "Software Engineer",
        "Product Manager",
        "Data Scientist",
    }


@pytest.mark.parametrize(
    "filters,expected_titles",
    [
        ({"status": ["APPLIED"]}, ["Software Engineer"]),
        ({"status": ["INTERVIEWING"]}, ["Product Manager"]),
        ({"status": ["REJECTED"]}, ["Data Scientist"]),
    ],
)
def test_list_jobs_with_status_filter(repository_with_jobs, filters, expected_titles):
    """Test listing jobs with a status filter."""
    response = list_jobs(filters=filters, repository=repository_with_jobs)

    assert response.type == ResponseTypes.SUCCESS
    assert {job.title for job in response.value} == set(expected_titles)


@pytest.mark.parametrize(
    "filters,expected_titles",
    [
        ({"company": "TechCorp"}, ["Software Engineer"]),
        ({"company": "BizCorp"}, ["Product Manager"]),
        ({"company": "DataCorp"}, ["Data Scientist"]),
    ],
)
def test_list_jobs_with_company_filter(repository_with_jobs, filters, expected_titles):
    """Test listing jobs with a company filter."""
    response = list_jobs(filters=filters, repository=repository_with_jobs)

    assert response.type == ResponseTypes.SUCCESS
    assert {job.title for job in response.value} == set(expected_titles)


@pytest.mark.parametrize(
    "filters,expected_titles",
    [
        ({"country": "USA"}, ["Software Engineer", "Product Manager"]),
        ({"country": "Canada"}, ["Data Scientist"]),
    ],
)
def test_list_jobs_with_country_filter(repository_with_jobs, filters, expected_titles):
    """Test listing jobs with a country filter."""
    response = list_jobs(filters=filters, repository=repository_with_jobs)

    assert response.type == ResponseTypes.SUCCESS
    assert {job.title for job in response.value} == set(expected_titles)


@pytest.mark.parametrize(
    "filters,expected_titles",
    [
        (
            {"date_applied__gt": "2023-01-01"},
            ["Software Engineer", "Product Manager", "Data Scientist"],
        ),
        ({"date_applied__lt": "2023-03-01"}, ["Software Engineer", "Data Scientist"]),
        ({"date_updated__lt": "2023-06-01"}, ["Data Scientist"]),
    ],
)
def test_list_jobs_with_date_filters(repository_with_jobs, filters, expected_titles):
    """Test listing jobs with date filters."""
    response = list_jobs(filters=filters, repository=repository_with_jobs)

    assert response.type == ResponseTypes.SUCCESS
    assert {job.title for job in response.value} == set(expected_titles)


def test_list_jobs_with_invalid_filters(repository_with_jobs):
    """Test listing jobs with invalid filters."""
    filters = {"invalid_key": "value"}
    response = list_jobs(filters=filters, repository=repository_with_jobs)

    assert response.type == ResponseTypes.PARAMETERS_ERROR
    assert response.message == [
        {"message": "Key 'invalid_key' is not accepted", "parameter": "filters"}
    ]


def test_list_jobs_with_empty_repository():
    """Test listing jobs when the repository is empty."""
    repo = InMemoryJobRepository()  # Empty repository
    response = list_jobs(filters=None, repository=repo)

    assert response.type == ResponseTypes.SUCCESS
    assert len(response.value) == 0
