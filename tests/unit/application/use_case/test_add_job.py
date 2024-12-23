from uuid import uuid4

from src.application.domain.entity.job import JobStatus, WorkSettingType
from src.application.domain.enums.country import Country
from src.application.use_case.add_job import add_job
from src.core.responses.response import ResponseTypes


async def test_add_job_success(job_manager):
    """Test adding a job successfully."""
    data = {
        "id": uuid4(),
        "user_id": uuid4(),
        "title": "Software Engineer",
        "company": "TechCorp",
        "status": "applied",
        "country": "US",
        "work_setting_type": "onsite",
        "city": "NY",
        "description": "A challenging job opportunity.",
    }
    response = await add_job(data, job_manager)
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
        "user_id": uuid4(),
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
