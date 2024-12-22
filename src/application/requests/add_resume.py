from typing import Any, Dict

from src.core.base_request import InvalidRequest, ValidRequest


class AddResumeValidRequest(ValidRequest):
    """Request for adding a resume."""

    def __init__(self, data: Dict[str, Any]):
        self.data = data


class AddResumeInvalidRequest(InvalidRequest):
    pass


def build_add_resume_request(data: Dict[str, Any]):
    """Factory for creating AddresumeRequest."""
    invalid_req = AddResumeInvalidRequest()

    if not isinstance(data, dict):
        invalid_req.add_error("data", "Must be a dictionary.")
        return invalid_req

    if not data:
        invalid_req.add_error("data", "Must not be empty.")

    required_fields = [
        "id",
        "candidate_name",
    ]
    for field in required_fields:
        if field not in data:
            invalid_req.add_error(field, f"'{field}' is required.")

    if invalid_req.has_errors():
        return invalid_req

    return AddResumeValidRequest(data)
