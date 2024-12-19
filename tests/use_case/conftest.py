import pytest

from src.domain.entity.job import Job
from src.repository.base.repository import Repository
from src.repository.in_memory.in_memory_gateway import InMemoryGateway


class JobRepository(Repository[Job]):
    pass


@pytest.fixture
def repository():
    gateway = InMemoryGateway([])
    repository = JobRepository(gateway)
    return repository
