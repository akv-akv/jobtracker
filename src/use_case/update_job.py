from src.application.base.manage import Manage
from src.requests.update_job import UpdateJobInvalidRequest, build_update_job_request
from src.responses.response import ResponseFailure, ResponseSuccess, ResponseTypes


async def update_job(data, job_manager: Manage):
    """Update only the specified fields of a job."""
    # Build the request and validate it
    request = build_update_job_request(data)
    if isinstance(request, UpdateJobInvalidRequest):
        return ResponseFailure(ResponseTypes.PARAMETERS_ERROR, request.errors)

    try:
        # Fetch the existing job from the repository
        job = await job_manager.retrieve(request.data["id"])
        if not job:
            return ResponseFailure(ResponseTypes.RESOURCE_ERROR, "Job not found.")
        # Save the updated job back to the repository
        await job_manager.update(job.id, data)
        job = await job_manager.retrieve(request.data["id"])
        return ResponseSuccess(job)
    except ValueError as e:
        return ResponseFailure(ResponseTypes.PARAMETERS_ERROR, str(e))
    except Exception as exc:
        return ResponseFailure(ResponseTypes.SYSTEM_ERROR, str(exc))
