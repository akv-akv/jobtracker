import pytest

from src.application.job import JobRepository, ManageJob
from src.core.repository.in_memory.in_memory_gateway import InMemoryGateway


@pytest.fixture
def job_manager():
    gateway = InMemoryGateway([])
    return ManageJob(JobRepository(gateway))
