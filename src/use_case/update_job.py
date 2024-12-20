from src.repository.base.repository import Repository
from src.requests.update_job import UpdateJobInvalidRequest, build_update_job_request
from src.responses.response import ResponseFailure, ResponseSuccess, ResponseTypes


async def update_job(data, repository: Repository):
    """Update only the specified fields of a job."""
    # Build the request and validate it
    request = build_update_job_request(data)
    if isinstance(request, UpdateJobInvalidRequest):
        return ResponseFailure(ResponseTypes.PARAMETERS_ERROR, request.errors)

    try:
        # Fetch the existing job from the repository
        job = await repository.get(request.data["id"])
        if not job:
            return ResponseFailure(ResponseTypes.RESOURCE_ERROR, "Job not found.")
        # Save the updated job back to the repository
        await repository.update(job.id, data)
        job = await repository.get(request.data["id"])
        return ResponseSuccess(job)
    except ValueError as e:
        return ResponseFailure(ResponseTypes.PARAMETERS_ERROR, str(e))
    except Exception as exc:
        return ResponseFailure(ResponseTypes.SYSTEM_ERROR, str(exc))
