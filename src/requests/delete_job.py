from uuid import UUID

from src.requests.base_request import InvalidRequest, ValidRequest


class DeleteJobValidRequest(ValidRequest):
    """Request for adding a job."""

    def __init__(self, id: UUID):
        self.id = id


class DeleteJobInvalidRequest(InvalidRequest):
    pass


def build_delete_job_request(id: UUID):
    """Factory for creating AddJobRequest."""
    if not isinstance(id, UUID):
        invalid_req = DeleteJobInvalidRequest()
        invalid_req.add_error("id", "Must be UUID.")
        return invalid_req

    return DeleteJobValidRequest(id)
