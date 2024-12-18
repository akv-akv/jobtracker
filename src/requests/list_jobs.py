from collections.abc import Mapping
from datetime import datetime
from typing import Any, Dict, Optional, Union

from src.domain.entity.job import JobStatus
from src.requests.base_request import InvalidRequest, ValidRequest

DATE_FILTERS = [
    "date_applied__eq",
    "date_applied__gt",
    "date_applied__lt",
    "date_updated__eq",
    "date_updated__gt",
    "date_updated__lt",
]

TEXT_FILTERS = [
    "status",
    "company",
    "country",
    "city",
]

ACCEPTED_FILTERS = DATE_FILTERS + TEXT_FILTERS


class ListJobsValidRequest(ValidRequest):
    """Request for adding a job."""

    def __init__(self, filters: Optional[dict]):
        self.filters = filters


class ListJobsInvalidRequest(InvalidRequest):
    pass


def parse_date(date_str: str) -> datetime:
    try:
        return datetime.strptime(date_str, "%Y-%m-%d")
    except ValueError:
        raise ValueError(f"Invalid date format: {date_str}. Expected YYYY-MM-DD.")


def build_job_list_request(
    filters: Optional[Dict[str, Any]] = None,
) -> Union[ListJobsValidRequest, ListJobsInvalidRequest]:
    invalid_req = ListJobsInvalidRequest()

    print(filters)

    if filters:
        if not isinstance(filters, Mapping):
            invalid_req.add_error("filters", "Must be a dictionary")
            return invalid_req

        for key, value in filters.items():
            if key not in ACCEPTED_FILTERS:
                invalid_req.add_error("filters", f"Key '{key}' is not accepted")
                continue

            if key in DATE_FILTERS:
                try:
                    filters[key] = parse_date(value)
                except ValueError as e:
                    invalid_req.add_error(key, str(e))
                    continue

            # Validate multiple statuses
            if key == "status":
                if not isinstance(value, list):
                    invalid_req.add_error("status", "Must be a list of statuses")
                    continue
                try:
                    filters[key] = [
                        JobStatus[status] if isinstance(status, str) else status
                        for status in value
                    ]
                except KeyError as e:
                    invalid_req.add_error("status", f"Invalid status: {str(e)}")
                    continue

            # Validate date filters
            if key.startswith("date_applied") or key.startswith("date_updated"):
                try:
                    datetime.strptime(value, "%Y-%m-%d")
                except ValueError:
                    invalid_req.add_error(key, f"Invalid date format: {value}")

        if invalid_req.has_errors():
            return invalid_req

    return ListJobsValidRequest(filters=filters)
