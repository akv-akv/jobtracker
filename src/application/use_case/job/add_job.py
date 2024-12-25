from src.application.requests.job.add_job import (
    AddJobInvalidRequest,
    build_add_job_request,
)
from src.core.manage import Manage
from src.core.responses.response import ResponseFailure, ResponseSuccess, ResponseTypes


async def add_job(data: dict, manager: Manage):
    """
    Use case for adding a job asynchronously.

    Args:
        data (dict): Input data to create the job.
        repository (Repository): The repository to interact with the persistence layer.

    Returns:
        ResponseSuccess or ResponseFailure: The result of the operation.
    """
    # Build the request object
    request = build_add_job_request(data)

    # Validate the request
    if isinstance(request, AddJobInvalidRequest):
        return ResponseFailure(ResponseTypes.PARAMETERS_ERROR, request.errors)

    try:
        # Add the job to the repository
        response = await manager.create(request.data)

        # Return a success response with the created job
        return ResponseSuccess(response)

    except ValueError as e:
        # Handle validation errors and return a failure response
        return ResponseFailure(ResponseTypes.PARAMETERS_ERROR, str(e))

    except Exception as exc:
        # Handle unexpected system errors
        return ResponseFailure(ResponseTypes.SYSTEM_ERROR, str(exc))
