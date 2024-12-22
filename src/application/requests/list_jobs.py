from collections.abc import Mapping
from datetime import datetime
from typing import Any, Dict, Optional, Union

from src.core.base_request import InvalidRequest, ValidRequest
from src.core.repository.base.filter import ComparisonFilter, ComparisonOperator, Filter
from src.core.repository.base.pagination import PageOptions

DATE_FILTERS = [
    "created_at__eq",
    "created_at__gt",
    "created_at__lt",
    "updated_at__eq",
    "updated_at__gt",
    "updated_at__lt",
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

    def __init__(self, filters: list[Filter], params: Optional[PageOptions]):
        self.filters = filters
        self.params = params


class ListJobsInvalidRequest(InvalidRequest):
    pass


def parse_date(date_str: str) -> datetime:
    try:
        return datetime.strptime(date_str, "%Y-%m-%d")
    except ValueError:
        raise ValueError(f"Invalid date format: {date_str}. Expected YYYY-MM-DD.")


def build_job_list_request(
    filters: Optional[Dict[str, Any]] = None, params: Optional[Dict[str, Any]] = None
) -> Union[ListJobsValidRequest, ListJobsInvalidRequest]:
    invalid_req = ListJobsInvalidRequest()
    filter_objects: list[Filter] = []
    params_object = None

    if filters:
        if not isinstance(filters, Mapping):
            invalid_req.add_error("filters", "Must be a dictionary")
            return invalid_req

        for key, value in filters.items():
            if key not in ACCEPTED_FILTERS:
                invalid_req.add_error("filters", f"Key '{key}' is not accepted")
                continue

            try:
                # Use Filter factory or similar functionality
                if key in DATE_FILTERS:
                    operator = key.split("__")[-1]  # e.g., `gt`, `lt`, `eq`
                    parsed_value = parse_date(value)
                    filter_objects.append(
                        ComparisonFilter(
                            field=key.split("__")[0],
                            operator=ComparisonOperator(operator),
                            values=[parsed_value],
                        )
                    )
                else:
                    filter_objects.append(
                        Filter(
                            field=key,
                            values=value if isinstance(value, list) else [value],
                        )
                    )
            except Exception as e:
                invalid_req.add_error(key, str(e))
                continue

        if invalid_req.has_errors():
            return invalid_req
    if params:
        try:
            params_object = PageOptions(**params)
        except Exception as e:
            invalid_req.add_error(key, str(e))
    return ListJobsValidRequest(filters=filter_objects, params=params_object)
