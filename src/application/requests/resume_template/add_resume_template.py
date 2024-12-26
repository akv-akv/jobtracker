from typing import Any, Dict, Union

from src.core.base_request import InvalidRequest, ValidRequest


class AddResumeTemplateValidRequest(ValidRequest):
    """Request for adding a job."""

    def __init__(self, data: Dict[str, Any]):
        self.data = data


class AddResumeTemplateInvalidRequest(InvalidRequest):
    pass


def build_add_resume_template_request(
    data: dict[str, Any],
) -> Union[AddResumeTemplateValidRequest, AddResumeTemplateInvalidRequest]:
    if not isinstance(data, dict):
        invalid_req = AddResumeTemplateInvalidRequest()
        invalid_req.add_error("data", "Must be a dictionary.")
        return invalid_req

    required_fields = [
        "resume_template",
    ]
    invalid_req = AddResumeTemplateInvalidRequest()

    # Validate required fields
    for field in required_fields:
        if field not in data:
            invalid_req.add_error(field, f"'{field}' is required.")
    if invalid_req.has_errors():
        return invalid_req

    return AddResumeTemplateValidRequest(data)
