from typing import Any

from src.repository.job_base import JobRepository
from src.requests.job_list_request import InvalidRequest, build_job_list_request
from src.responses.response import ResponseFailure, ResponseSuccess, ResponseTypes


def list_jobs(
    filters: Any, repository: JobRepository
) -> ResponseSuccess | ResponseFailure:
    request = build_job_list_request(filters)
    if isinstance(request, InvalidRequest):
        return ResponseFailure(ResponseTypes.PARAMETERS_ERROR, request.errors)

    try:
        jobs = repository.list(request.filters)
        return ResponseSuccess(jobs)
    except Exception as exc:
        return ResponseFailure(ResponseTypes.SYSTEM_ERROR, exc)
