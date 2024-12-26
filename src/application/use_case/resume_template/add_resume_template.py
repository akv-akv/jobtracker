from typing import Any

from src.application.requests.resume_template.add_resume_template import (
    AddResumeTemplateInvalidRequest,
    build_add_resume_template_request,
)
from src.core.manage import Manage
from src.core.responses.response import ResponseFailure, ResponseSuccess, ResponseTypes


async def add_resume_template(data: dict[str, Any], manager: Manage):
    """
    Use case for adding a resume template asynchronously.

    Args:
        data (dict): Input data to create the resume_template.
        repository (Repository): The repository to interact with the persistence layer.

    Returns:
        ResponseSuccess or ResponseFailure: The result of the operation.
    """
    # Build the request object
    request = build_add_resume_template_request(data)

    # Validate the request
    if isinstance(request, AddResumeTemplateInvalidRequest):
        return ResponseFailure(ResponseTypes.PARAMETERS_ERROR, request.errors)

    try:
        # Add the resume_template to the repository
        response = await manager.create(request.data)

        # Return a success response with the created resume_template
        return ResponseSuccess(response)

    except ValueError as e:
        # Handle validation errors and return a failure response
        return ResponseFailure(ResponseTypes.PARAMETERS_ERROR, str(e))

    except Exception as exc:
        # Handle unexpected system errors
        return ResponseFailure(ResponseTypes.SYSTEM_ERROR, str(exc))
