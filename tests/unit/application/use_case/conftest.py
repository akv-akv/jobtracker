import pytest

from src.application.infrastructure.repository.job import JobRepository
from src.application.manage.job import ManageJob
from src.core.repository.in_memory.in_memory_gateway import InMemoryGateway


@pytest.fixture
def job_manager():
    gateway = InMemoryGateway([])
    return ManageJob(JobRepository(gateway))
