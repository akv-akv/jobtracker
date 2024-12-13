from src.domain.entity.resume import Resume
from src.repository.resume_base import ResumeRepository
from src.requests.add_resume import AddResumeInvalidRequest, build_add_resume_request
from src.responses.response import ResponseFailure, ResponseSuccess, ResponseTypes


def add_resume(data, repository: ResumeRepository):
    """Use case for adding a resume."""
    request = build_add_resume_request(data)

    if isinstance(request, AddResumeInvalidRequest):
        return ResponseFailure(ResponseTypes.PARAMETERS_ERROR, request.errors)

    try:
        resume = Resume(**request.data)
        repository.create(resume)
        return ResponseSuccess(resume)
    except ValueError as e:
        return ResponseFailure(ResponseTypes.PARAMETERS_ERROR, str(e))
    except Exception as exc:
        return ResponseFailure(ResponseTypes.SYSTEM_ERROR, str(exc))
