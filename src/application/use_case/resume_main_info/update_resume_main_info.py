from src.application.requests.resume_main_info.update_resume_main_info import (
    UpdateJobInvalidRequest,
    build_update_resume_main_info_request,
)
from src.core.manage import Manage
from src.core.responses.response import ResponseFailure, ResponseSuccess, ResponseTypes


async def update_resume_main_info_use_case(data, resume_main_info_manager: Manage):
    """Update only the specified fields of a resume_main_info."""
    # Build the request and validate it
    request = build_update_resume_main_info_request(data)
    if isinstance(request, UpdateJobInvalidRequest):
        return ResponseFailure(ResponseTypes.PARAMETERS_ERROR, request.errors)

    try:
        # Fetch the existing resume_main_info from the repository
        resume_main_info = await resume_main_info_manager.retrieve(request.data["id"])
        if not resume_main_info:
            return ResponseFailure(ResponseTypes.RESOURCE_ERROR, "Resume not found.")
        # Save the updated resume_main_info back to the repository
        for key, value in resume_main_info.__dict__.items():
            if key not in data and key not in ["updated_at"]:
                data[key] = value

        data["parent_id"] = data["id"]
        del data["id"]
        del data["created_at"]

        # Create a new record in the repository
        resume_main_info = await resume_main_info_manager.create(data)
        print(resume_main_info)
        return ResponseSuccess(resume_main_info)
    except ValueError as e:
        return ResponseFailure(ResponseTypes.PARAMETERS_ERROR, str(e))
    except Exception as exc:
        return ResponseFailure(ResponseTypes.SYSTEM_ERROR, str(exc))
