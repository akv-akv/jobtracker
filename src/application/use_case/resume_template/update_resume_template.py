from src.application.requests.resume_template.update_resume_template import (
    UpdateResumeTemplateInvalidRequest,
    build_update_resume_template_request,
)
from src.core.manage import Manage
from src.core.responses.response import ResponseFailure, ResponseSuccess, ResponseTypes


async def update_resume_template_use_case(data, resume_template_manager: Manage):
    """Update only the specified fields of a resume_template."""
    # Build the request and validate it
    request = build_update_resume_template_request(data)
    if isinstance(request, UpdateResumeTemplateInvalidRequest):
        return ResponseFailure(ResponseTypes.PARAMETERS_ERROR, request.errors)

    try:
        # Fetch the existing resume_template from the repository
        resume_template = await resume_template_manager.retrieve(request.data["id"])
        if not resume_template:
            return ResponseFailure(ResponseTypes.RESOURCE_ERROR, "Template not found.")
        # Save the updated resume_template back to the repository
        for key, value in resume_template.__dict__.items():
            if key not in data and key not in ["updated_at"]:
                data[key] = value

        data["parent_id"] = data["id"]
        del data["id"]
        del data["created_at"]

        # Create a new record in the repository
        resume_template = await resume_template_manager.create(data)
        print(resume_template)
        return ResponseSuccess(resume_template)
    except ValueError as e:
        return ResponseFailure(ResponseTypes.PARAMETERS_ERROR, str(e))
    except Exception as exc:
        return ResponseFailure(ResponseTypes.SYSTEM_ERROR, str(exc))
