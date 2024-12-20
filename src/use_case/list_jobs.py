from typing import Any, Optional

from src.repository.base.repository import Repository
from src.requests.list_jobs import InvalidRequest, build_job_list_request
from src.responses.response import ResponseFailure, ResponseSuccess, ResponseTypes


async def list_jobs(
    filters: Any, repository: Repository, params: Optional[dict[str, Any]] = None
) -> ResponseSuccess | ResponseFailure:
    request = build_job_list_request(filters, params)
    if isinstance(request, InvalidRequest):
        return ResponseFailure(ResponseTypes.PARAMETERS_ERROR, request.errors)

    try:
        print(request.params)
        jobs = await repository.filter(filters=request.filters, params=request.params)
        return ResponseSuccess(jobs)
    except Exception as exc:
        return ResponseFailure(ResponseTypes.SYSTEM_ERROR, exc)
