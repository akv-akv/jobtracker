from typing import Any, Dict

from src.core.base_request import InvalidRequest, ValidRequest


class UpdateResumeMainInfoValidRequest(ValidRequest):
    """Request for updating a main_info."""

    def __init__(self, data: Dict[str, Any]):
        self.data = data


class UpdateResumeMainInfoInvalidRequest(InvalidRequest):
    pass


def build_update_resume_main_info_request(data: Dict[str, Any]):
    """Factory for creating UpdateResumeMainInfoRequest."""
    if not isinstance(data, dict):
        invalid_req = UpdateResumeMainInfoInvalidRequest()
        invalid_req.add_error("data", "Must be a dictionary.")
        return invalid_req

    required_fields = ["id"]
    invalid_req = UpdateResumeMainInfoInvalidRequest()

    for field in required_fields:
        if field not in data:
            invalid_req.add_error(field, f"'{field}' is required.")

    if invalid_req.has_errors():
        return invalid_req

    return UpdateResumeMainInfoValidRequest(data)
