from uuid import uuid4

from src.application.domain.entity.job import JobStatus, WorkSettingType
from src.application.domain.enums.country import Country
from src.application.requests.add_job import build_add_job_request


def test_build_add_job_request_empty_data():
    request = build_add_job_request(data={})
    assert bool(request) is False


def test_build_add_job_request_incomplete_data():
    data = {"title": "Data engineer"}
    request = build_add_job_request(data=data)
    assert bool(request) is False
    assert request.has_errors()


def test_build_add_job_request_complete_data():
    data = {
        "user_id": uuid4(),
        "title": "Data engineer",
        "company": "Awesome Employer",
        "description": "Test description",
        "country": Country.UnitedStates,
        "city": "NYC",
        "status": JobStatus.ADDED,
        "work_setting_type": WorkSettingType.HYBRID,
    }
    request = build_add_job_request(data=data)
    assert bool(request) is True
