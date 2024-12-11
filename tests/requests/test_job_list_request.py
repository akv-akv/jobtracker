from src.requests.list_jobs import build_job_list_request


def test_build_job_list_request_no_filters():
    request = build_job_list_request()

    assert request.filters is None
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

    assert request.filters == filters
    assert bool(request) is True


def test_build_job_list_request_invalid_date():
    filters = {"date_applied__eq": "invalid-date"}
    request = build_job_list_request(filters=filters)

    assert request.has_errors()
    assert request.errors[0]["parameter"] == "date_applied__eq"
    assert "Invalid date format" in request.errors[0]["message"]
    assert bool(request) is False


def test_build_job_list_request_valid_filters():
    filters = {
        "status": ["APPLIED", "INTERVIEWINGp"],
        "date_applied__gt": "2023-01-01",
        "date_updated__lt": "2023-12-31",
    }
    request = build_job_list_request(filters=filters)

    assert request.filters == filters
    assert bool(request) is True
