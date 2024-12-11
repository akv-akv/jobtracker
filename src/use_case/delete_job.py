from src.repository.job_base import JobRepository
from src.requests.delete_job import DeleteJobInvalidRequest, build_delete_job_request
from src.responses.response import ResponseFailure, ResponseSuccess, ResponseTypes


def delete_job(id, repository: JobRepository):
    """Use case for adding a job."""
    request = build_delete_job_request(id)

    if isinstance(request, DeleteJobInvalidRequest):
        return ResponseFailure(ResponseTypes.PARAMETERS_ERROR, request.errors)

    try:
        repository.delete(id)
        return ResponseSuccess(id)
    except ValueError as e:
        return ResponseFailure(ResponseTypes.PARAMETERS_ERROR, str(e))
    except Exception as exc:
        return ResponseFailure(ResponseTypes.SYSTEM_ERROR, str(exc))
