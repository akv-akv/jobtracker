from src.domain.entity.job import Job
from src.repository.base.repository import Repository
from src.requests.add_job import AddJobInvalidRequest, build_add_job_request
from src.responses.response import ResponseFailure, ResponseSuccess, ResponseTypes


async def add_job(data: dict, repository: Repository):
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
        # Create a job entity from the request data
        job = Job.create(**request.data)
        # Add the job to the repository
        await repository.add(job)
        # print(request.data)

        # Return a success response with the created job
        return ResponseSuccess(job)

    except ValueError as e:
        # Handle validation errors and return a failure response
        return ResponseFailure(ResponseTypes.PARAMETERS_ERROR, str(e))

    except Exception as exc:
        # Handle unexpected system errors
        return ResponseFailure(ResponseTypes.SYSTEM_ERROR, str(exc))
