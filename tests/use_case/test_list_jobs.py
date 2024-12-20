from uuid import uuid4

import pytest

from src.domain.entity.job import JobStatus, WorkSettingType
from src.domain.entity.user import User
from src.domain.enums.country import Country
from src.repository.base.repository import Repository
from src.repository.in_memory.in_memory_gateway import InMemoryGateway
from src.responses.response import ResponseTypes
from src.use_case.list_jobs import list_jobs


@pytest.fixture
async def repository_with_jobs(repository):
    """Fixture to populate the repository with sample jobs."""
    jobs = [
        {
            "id": uuid4(),
            "user": User.create(name="Kirill"),
            "title": "Software Engineer",
            "company": "TechCorp",
            "status": JobStatus.APPLIED,
            "country": Country.US,
            "work_setting_type": WorkSettingType.ONSITE,
            "city": "NY",
            "description": "A challenging job opportunity.",
        },
        {
            "id": uuid4(),
            "user": User.create(name="Kirill"),
            "title": "Product Manager",
            "company": "BizCorp",
            "status": JobStatus.INTERVIEWING,
            "country": Country.US,
            "work_setting_type": WorkSettingType.ONSITE,
            "city": "NY",
            "description": "A challenging job opportunity.",
        },
        {
            "id": uuid4(),
            "user": User.create(name="Kirill"),
            "title": "Data Scientist",
            "company": "DataCorp",
            "status": JobStatus.REJECTED,
            "country": Country.CA,
            "work_setting_type": WorkSettingType.ONSITE,
            "city": "NY",
            "description": "A challenging job opportunity.",
        },
    ]
    for job in jobs:
        await repository.add(job)
    return repository


async def test_list_jobs_success_without_filters(repository_with_jobs):
    """Test listing all jobs without filters."""
    response = await list_jobs(
        filters=None, params=None, repository=repository_with_jobs
    )
    assert response.type == ResponseTypes.SUCCESS
    assert response.value.total == 3
    assert {job.title for job in response.value.items} == {
        "Software Engineer",
        "Product Manager",
        "Data Scientist",
    }


async def test_list_jobs_success_with_limit(repository_with_jobs):
    """Test listing all jobs without filters."""
    params = {"limit": 1}
    response = await list_jobs(
        filters=None, params=params, repository=repository_with_jobs
    )
    assert response.type == ResponseTypes.SUCCESS
    assert response.value.total == 3
    assert len(response.value.items) == 1
    assert {job.title for job in response.value.items} == {
        "Software Engineer",
    }


async def test_list_jobs_success_with_limit_and_offset(repository_with_jobs):
    """Test listing all jobs without filters."""
    params = {"limit": 1, "offset": 1}
    response = await list_jobs(
        filters=None, params=params, repository=repository_with_jobs
    )
    assert response.type == ResponseTypes.SUCCESS
    assert response.value.total == 3
    assert len(response.value.items) == 1
    assert {job.title for job in response.value.items} == {
        "Product Manager",
    }


@pytest.mark.parametrize(
    "filters,expected_titles",
    [
        ({"status": JobStatus.APPLIED}, ["Software Engineer"]),
        ({"status": JobStatus.INTERVIEWING}, ["Product Manager"]),
        ({"status": JobStatus.REJECTED}, ["Data Scientist"]),
    ],
)
async def test_list_jobs_with_status_filter(
    repository_with_jobs, filters, expected_titles
):
    """Test listing jobs with a status filter."""
    response = await list_jobs(
        filters=filters, params=None, repository=repository_with_jobs
    )

    assert response.type == ResponseTypes.SUCCESS
    assert {job.title for job in response.value.items} == set(expected_titles)


@pytest.mark.parametrize(
    "filters,expected_titles",
    [
        ({"company": "TechCorp"}, ["Software Engineer"]),
        ({"company": "BizCorp"}, ["Product Manager"]),
        ({"company": "DataCorp"}, ["Data Scientist"]),
    ],
)
async def test_list_jobs_with_company_filter(
    repository_with_jobs, filters, expected_titles
):
    """Test listing jobs with a company filter."""
    response = await list_jobs(
        filters=filters, params=None, repository=repository_with_jobs
    )

    assert response.type == ResponseTypes.SUCCESS
    assert {job.title for job in response.value.items} == set(expected_titles)


@pytest.mark.parametrize(
    "filters,expected_titles",
    [
        ({"country": Country.US}, ["Software Engineer", "Product Manager"]),
        ({"country": Country.CA}, ["Data Scientist"]),
    ],
)
async def test_list_jobs_with_country_filter(
    repository_with_jobs, filters, expected_titles
):
    """Test listing jobs with a country filter."""
    response = await list_jobs(filters=filters, repository=repository_with_jobs)

    assert response.type == ResponseTypes.SUCCESS
    assert {job.title for job in response.value.items} == set(expected_titles)


# @pytest.mark.parametrize(
#     "filters,expected_titles",
#     [
#         (
#             {"created_at__gt": "2023-01-01"},
#             ["Software Engineer", "Product Manager", "Data Scientist"],
#         ),
#         ({"updated_at__lt": "2023-03-01"}, []),
#         ({"created_at__lt": "2023-06-01"}, []),
#     ],
# )
# async def test_list_jobs_with_date_filters(
#     repository_with_jobs, filters, expected_titles
# ):
#     """Test listing jobs with date filters."""
#     response = await list_jobs(filters=filters, repository=repository_with_jobs)

#     assert response.value.items == ""
#     assert response.type == ResponseTypes.SUCCESS
#     assert {job.title for job in response.value.items} == set(expected_titles)


async def test_list_jobs_with_invalid_filters(repository_with_jobs):
    """Test listing jobs with invalid filters."""
    filters = {"invalid_key": "value"}
    response = await list_jobs(filters=filters, repository=repository_with_jobs)

    assert response.type == ResponseTypes.PARAMETERS_ERROR
    assert response.message == [
        {"message": "Key 'invalid_key' is not accepted", "parameter": "filters"}
    ]


async def test_list_jobs_with_empty_repository():
    """Test listing jobs when the repository is empty."""
    repo = Repository(InMemoryGateway([]))  # Empty repository
    response = await list_jobs(filters=None, repository=repo)

    assert response.type == ResponseTypes.SUCCESS
    assert len(response.value.items) == 0
