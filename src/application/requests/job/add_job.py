from enum import Enum
from typing import Any, Dict, Union

from src.core.base_request import InvalidRequest, ValidRequest


class AddJobValidRequest(ValidRequest):
    """Request for adding a job."""

    def __init__(self, data: Dict[str, Any]):
        self.data = data


class AddJobInvalidRequest(InvalidRequest):
    pass


class JobStatus(Enum):
    ADDED = "added"
    APPLIED = "applied"
    INTERVIEWING = "interviewing"
    OFFERED = "offered"
    REJECTED = "rejected"
    ARCHIVED = "archived"


class WorkSettingType(Enum):
    REMOTE = "remote"
    HYBRID = "hybrid"
    ONSITE = "onsite"


def build_add_job_request(
    data: Dict[str, Any],
) -> Union[AddJobValidRequest, AddJobInvalidRequest]:
    """Factory for creating AddJobRequest."""
    if not isinstance(data, dict):
        invalid_req = AddJobInvalidRequest()
        invalid_req.add_error("data", "Must be a dictionary.")
        return invalid_req

    required_fields = [
        "user_id",
        "title",
        "company",
        "description",
        "country",
        "city",
        "status",
        "work_setting_type",
    ]
    invalid_req = AddJobInvalidRequest()

    # Validate required fields
    for field in required_fields:
        if field not in data:
            invalid_req.add_error(field, f"'{field}' is required.")
    if invalid_req.has_errors():
        return invalid_req

    return AddJobValidRequest(data)
