from uuid import uuid4

from src.domain.entity.job import Job, JobStatus, WorkSettingType
from src.domain.entity.user import User
from src.domain.enums.country import Country
from src.responses.response import ResponseTypes
from src.use_case.add_job import add_job


async def test_add_job_success(job_manager):
    """Test adding a job successfully."""
    data = {
        "id": uuid4(),
        "user": User.create(name="Kirill"),
        "title": "Software Engineer",
        "company": "TechCorp",
        "status": JobStatus.APPLIED,
        "country": Country.UnitedStates,
        "work_setting_type": WorkSettingType.ONSITE,
        "city": "NY",
        "description": "A challenging job opportunity.",
    }
    Job.create(**data)
    response = await add_job(data, job_manager)
    print(response)
    assert response.type == ResponseTypes.SUCCESS

    added_job = await job_manager.retrieve(data["id"])
    assert added_job.title == "Software Engineer"
    assert added_job.company == "TechCorp"


async def test_add_job_invalid_request(job_manager):
    """Test adding a job with invalid input data."""
    invalid_data = "invalid data"

    response = await add_job(invalid_data, job_manager)

    assert response.type == ResponseTypes.PARAMETERS_ERROR
    assert "Must be a dictionary." in response.message[0]["message"]


async def test_add_job_duplicate_id(job_manager):
    """Test adding a job with a duplicate ID."""
    data = {
        "id": uuid4(),
        "user": User.create(name="Kirill"),
        "title": "Software Engineer",
        "company": "TechCorp",
        "status": JobStatus.APPLIED,
        "country": Country.UnitedStates,
        "work_setting_type": WorkSettingType.HYBRID,
        "city": "NY",
        "description": "A challenging job opportunity.",
    }

    # First add
    response = await add_job(data, job_manager)
    # Attempt duplicate add
    response = await add_job(data, job_manager)

    assert response.type == ResponseTypes.SYSTEM_ERROR
    assert "already exists" in response.message
