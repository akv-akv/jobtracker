from src.repository.job_base import JobRepository
from src.requests.update_job import UpdateJobInvalidRequest, build_update_job_request
from src.responses.response import ResponseFailure, ResponseSuccess, ResponseTypes


def update_job(data, repository: JobRepository):
    """Update only the specified fields of a job."""
    # Build the request and validate it
    request = build_update_job_request(data)
    if isinstance(request, UpdateJobInvalidRequest):
        return ResponseFailure(ResponseTypes.PARAMETERS_ERROR, request.errors)

    try:
        # Fetch the existing job from the repository
        job = repository.read(request.data["id"])
        if not job:
            return ResponseFailure(ResponseTypes.RESOURCE_ERROR, "Job not found.")
        # Save the updated job back to the repository
        repository.update(job.id, data)
        job = repository.read(request.data["id"])
        return ResponseSuccess(job)
    except ValueError as e:
        return ResponseFailure(ResponseTypes.PARAMETERS_ERROR, str(e))
    except Exception as exc:
        return ResponseFailure(ResponseTypes.SYSTEM_ERROR, str(exc))
