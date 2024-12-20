# from datetime import date
# from uuid import uuid4

# import pytest

# from src.domain.entity.job import Job, JobStatus
# from src.repository.job_postgres import JobRepositoryPostgres

# pytestmark = pytest.mark.integration


# def test_repository_list_jobs_without_filters(pg_session_with_jobs):
#     """Test listing jobs without filters."""
#     repo = JobRepositoryPostgres(pg_session_with_jobs)
#     jobs = repo.list()
#     assert len(jobs) == 2


# def test_repository_list_jobs_with_status_filter(pg_session_with_jobs):
#     """Test listing jobs with status filter."""
#     repo = JobRepositoryPostgres(pg_session_with_jobs)
#     jobs = repo.list(filters={"status": ["APPLIED"]})
#     assert len(jobs) == 1
#     assert jobs[0].title == "Software Engineer"


# def test_repository_create_and_read_job(pg_session_empty):
#     """Test creating and reading a job."""
#     repo = JobRepositoryPostgres(pg_session_empty)
#     job = Job(
#         id=uuid4(),
#         title="Backend Developer",
#         company="Techie Inc",
#         status=JobStatus.OFFERED,
#         country="USA",
#         city="San Francisco",
#         description="Backend development",
#         date_applied=date(2023, 5, 1),
#         date_updated=date(2023, 5, 10),
#     )
#     repo.create(job)
#     fetched_job = repo.read(job.id)
#     assert fetched_job.title == "Backend Developer"


# def test_repository_update_job(pg_session_with_jobs):
#     """Test updating a job."""
#     repo = JobRepositoryPostgres(pg_session_with_jobs)
#     job_id = "f853578c-fc0f-4e65-81b8-566c5dffa35a"
#     data = {"title": "Updated Software Engineer", "status": "OFFERED"}
#     repo.update(job_id, data)
#     updated_job = repo.read(job_id)
#     assert updated_job.title == "Updated Software Engineer"
#     assert updated_job.status == JobStatus.OFFERED
