from src.application.requests.resume_main_info.add_resume_main_info import (
    AddResumeMainInfoInvalidRequest,
    build_add_resume_main_info_request,
)
from src.core.manage import Manage
from src.core.responses.response import ResponseFailure, ResponseSuccess, ResponseTypes


async def add_resume_main_info(data: dict, manager: Manage):
    """
    Use case for adding a resum asynchronously.

    Args:
        data (dict): Input data to create the resume_main_info.
        repository (Repository): The repository to interact with the persistence layer.

    Returns:
        ResponseSuccess or ResponseFailure: The result of the operation.
    """
    # Build the request object
    request = build_add_resume_main_info_request(data)

    # Validate the request
    if isinstance(request, AddResumeMainInfoInvalidRequest):
        return ResponseFailure(ResponseTypes.PARAMETERS_ERROR, request.errors)

    try:
        # Add the resume_main_info to the repository
        response = await manager.create(request.data)

        # Return a success response with the created resume_main_info
        return ResponseSuccess(response)

    except ValueError as e:
        # Handle validation errors and return a failure response
        return ResponseFailure(ResponseTypes.PARAMETERS_ERROR, str(e))

    except Exception as exc:
        # Handle unexpected system errors
        return ResponseFailure(ResponseTypes.SYSTEM_ERROR, str(exc))
