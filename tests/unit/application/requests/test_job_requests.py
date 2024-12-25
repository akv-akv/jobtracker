from datetime import datetime

from src.application.requests.job.list_jobs import build_job_list_request
from src.core.repository.base.filter import ComparisonFilter, ComparisonOperator, Filter


def test_build_job_list_request_no_filters():
    request = build_job_list_request()

    assert request.filters == []
    assert bool(request) is True


def test_build_job_list_request_invalid_filters():
    request = build_job_list_request(filters=5)

    assert request.has_errors()
    assert request.errors[0]["parameter"] == "filters"
    assert request.errors[0]["message"] == "Must be a dictionary"
    assert bool(request) is False


def test_build_job_list_request_unaccepted_filter():
    request = build_job_list_request(filters={"invalid_key": "value"})

    assert request.has_errors()
    assert request.errors[0]["parameter"] == "filters"
    assert request.errors[0]["message"] == "Key 'invalid_key' is not accepted"
    assert bool(request) is False


def test_build_job_list_request_multiple_statuses():
    filters = {"status": ["APPLIED", "INTERVIEWING"]}
    request = build_job_list_request(filters=filters)

    assert request.filters == [
        Filter(field="status", values=["APPLIED", "INTERVIEWING"])
    ]
    assert bool(request) is True


def test_build_job_list_request_invalid_date():
    filters = {"created_at__eq": "invalid-date"}
    request = build_job_list_request(filters=filters)

    assert request.has_errors()
    assert request.errors[0]["parameter"] == "created_at__eq"
    assert "Invalid date format" in request.errors[0]["message"]
    assert bool(request) is False


def test_build_job_list_request_valid_filters():
    filters = {
        "status": ["APPLIED", "INTERVIEWING"],
        "created_at__gt": "2023-01-01",
        "created_at__lt": "2023-12-31",
    }
    request = build_job_list_request(filters=filters)

    expected = [
        Filter(field="status", values=["APPLIED", "INTERVIEWING"]),
        ComparisonFilter(
            field="created_at",
            values=[datetime(2023, 1, 1, 0, 0)],
            operator=ComparisonOperator.GT,
        ),
        ComparisonFilter(
            field="created_at",
            values=[datetime(2023, 12, 31, 0, 0)],
            operator=ComparisonOperator.LT,
        ),
    ]

    assert request.filters == expected
    assert bool(request) is True
