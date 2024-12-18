from src.domain.entity.job import Job
from src.repository.base.repository import Repository
from src.requests.add_job import AddJobInvalidRequest, build_add_job_request
from src.responses.response import ResponseFailure, ResponseSuccess, ResponseTypes


async def add_job(data, repository: Repository):
    """Use case for adding a job."""
    request = build_add_job_request(data)

    if isinstance(request, AddJobInvalidRequest):
        return ResponseFailure(ResponseTypes.PARAMETERS_ERROR, request.errors)

    try:
        job = Job.create(**request.data)
        await repository.add(job)
        return ResponseSuccess(job)
    except ValueError as e:
        return ResponseFailure(ResponseTypes.PARAMETERS_ERROR, str(e))
    except Exception as exc:
        return ResponseFailure(ResponseTypes.SYSTEM_ERROR, str(exc))
