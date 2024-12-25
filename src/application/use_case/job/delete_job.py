from src.application.requests.job.delete_job import (
    DeleteJobInvalidRequest,
    build_delete_job_request,
)
from src.core.manage import Manage
from src.core.responses.response import ResponseFailure, ResponseSuccess, ResponseTypes


async def delete_job(id, job_manager: Manage):
    """Use case for adding a job."""
    request = build_delete_job_request(id)

    if isinstance(request, DeleteJobInvalidRequest):
        return ResponseFailure(ResponseTypes.PARAMETERS_ERROR, request.errors)

    response = await job_manager.destroy(id)
    return (
        ResponseSuccess(id)
        if response
        else ResponseFailure(
            ResponseTypes.PARAMETERS_ERROR, f"Job with id {id} does not exist"
        )
    )
