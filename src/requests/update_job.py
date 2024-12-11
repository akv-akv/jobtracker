from typing import Any, Dict

from src.requests.base_request import InvalidRequest, ValidRequest


class UpdateJobValidRequest(ValidRequest):
    """Request for updating a job."""

    def __init__(self, data: Dict[str, Any]):
        self.data = data


class UpdateJobInvalidRequest(InvalidRequest):
    pass


def build_update_job_request(data: Dict[str, Any]):
    """Factory for creating UpdateJobRequest."""
    if not isinstance(data, dict):
        invalid_req = UpdateJobInvalidRequest()
        invalid_req.add_error("data", "Must be a dictionary.")
        return invalid_req

    required_fields = ["id"]
    invalid_req = UpdateJobInvalidRequest()

    for field in required_fields:
        if field not in data:
            invalid_req.add_error(field, f"'{field}' is required.")

    if invalid_req.has_errors():
        return invalid_req

    return UpdateJobValidRequest(data)
