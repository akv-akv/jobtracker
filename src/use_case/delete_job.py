from src.repository.base.repository import Repository
from src.requests.delete_job import DeleteJobInvalidRequest, build_delete_job_request
from src.responses.response import ResponseFailure, ResponseSuccess, ResponseTypes


async def delete_job(id, repository: Repository):
    """Use case for adding a job."""
    request = build_delete_job_request(id)

    if isinstance(request, DeleteJobInvalidRequest):
        return ResponseFailure(ResponseTypes.PARAMETERS_ERROR, request.errors)

    response = await repository.remove(id)
    return (
        ResponseSuccess(id)
        if response
        else ResponseFailure(
            ResponseTypes.PARAMETERS_ERROR, f"Job with id {id} does not exist"
        )
    )
