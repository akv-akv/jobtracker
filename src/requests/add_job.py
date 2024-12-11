from typing import Any, Dict

from src.requests.base_request import InvalidRequest, ValidRequest


class AddJobValidRequest(ValidRequest):
    """Request for adding a job."""

    def __init__(self, data: Dict[str, Any]):
        self.data = data


class AddJobInvalidRequest(InvalidRequest):
    pass


def build_add_job_request(data: Dict[str, Any]):
    """Factory for creating AddJobRequest."""
    if not isinstance(data, dict):
        invalid_req = AddJobInvalidRequest()
        invalid_req.add_error("data", "Must be a dictionary.")
        return invalid_req

    required_fields = [
        "id",
        "title",
        "company",
        "status",
        "country",
        "city",
        "description",
    ]
    invalid_req = AddJobInvalidRequest()

    for field in required_fields:
        if field not in data:
            invalid_req.add_error(field, f"'{field}' is required.")

    if invalid_req.has_errors():
        return invalid_req

    return AddJobValidRequest(data)
