from typing import Any, Dict, Union

from src.core.base_request import InvalidRequest, ValidRequest


class AddResumeMainInfoValidRequest(ValidRequest):
    """Request for adding a job."""

    def __init__(self, data: Dict[str, Any]):
        self.data = data


class AddResumeMainInfoInvalidRequest(InvalidRequest):
    pass


def build_add_resume_main_info_request(
    data: Dict[str, Any],
) -> Union[AddResumeMainInfoValidRequest, AddResumeMainInfoInvalidRequest]:
    """Factory for creating AddResumeMainInfoRequest."""
    if not isinstance(data, dict):
        invalid_req = AddResumeMainInfoInvalidRequest()
        invalid_req.add_error("data", "Must be a dictionary.")
        return invalid_req

    required_fields = [
        "applicant_name",
        "skills",
    ]
    invalid_req = AddResumeMainInfoInvalidRequest()

    # Validate required fields
    for field in required_fields:
        if field not in data:
            invalid_req.add_error(field, f"'{field}' is required.")
    if invalid_req.has_errors():
        return invalid_req

    return AddResumeMainInfoValidRequest(data)
