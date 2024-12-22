from uuid import uuid4

from src.application.requests.add_resume import build_add_resume_request


def test_build_add_resume_request_no_data():
    request = build_add_resume_request({})

    assert request.has_errors()
    assert request.errors[0]["parameter"] == "data"
    assert request.errors[0]["message"] == "Must not be empty."
    assert bool(request) is False


def test_build_add_resume_request_invalid_data():
    request = build_add_resume_request(data=5)

    assert request.has_errors()
    assert request.errors[0]["parameter"] == "data"
    assert request.errors[0]["message"] == "Must be a dictionary."
    assert bool(request) is False


def test_build_add_resume_request_valid_data():
    data = {
        "id": uuid4,
        "candidate_name": "Some Random Name",
    }
    request = build_add_resume_request(data=data)

    assert request.data == data
    assert bool(request) is True
