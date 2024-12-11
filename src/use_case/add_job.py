from src.domain.entity.job import Job
from src.repository.job_base import JobRepository
from src.requests.add_job import AddJobInvalidRequest, build_add_job_request
from src.responses.response import ResponseFailure, ResponseSuccess, ResponseTypes


def add_job(data, repository: JobRepository):
    """Use case for adding a job."""
    request = build_add_job_request(data)

    if isinstance(request, AddJobInvalidRequest):
        return ResponseFailure(ResponseTypes.PARAMETERS_ERROR, request.errors)

    try:
        job = Job(**request.data)
        repository.create(job)
        return ResponseSuccess(job)
    except ValueError as e:
        return ResponseFailure(ResponseTypes.PARAMETERS_ERROR, str(e))
    except Exception as exc:
        return ResponseFailure(ResponseTypes.SYSTEM_ERROR, str(exc))
