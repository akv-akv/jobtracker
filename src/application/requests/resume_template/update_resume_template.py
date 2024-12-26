from typing import Any, Dict

from src.core.base_request import InvalidRequest, ValidRequest


class UpdateResumeTemplateValidRequest(ValidRequest):
    """Request for updating a template."""

    def __init__(self, data: Dict[str, Any]):
        self.data = data


class UpdateResumeTemplateInvalidRequest(InvalidRequest):
    pass


def build_update_resume_template_request(data: Dict[str, Any]):
    """Factory for creating UpdateResumeTemplateRequest."""
    if not isinstance(data, dict):
        invalid_req = UpdateResumeTemplateInvalidRequest()
        invalid_req.add_error("data", "Must be a dictionary.")
        return invalid_req

    required_fields = ["id", "resume_template"]
    invalid_req = UpdateResumeTemplateInvalidRequest()

    for field in required_fields:
        if field not in data:
            invalid_req.add_error(field, f"'{field}' is required.")

    if invalid_req.has_errors():
        return invalid_req

    return UpdateResumeTemplateValidRequest(data)
