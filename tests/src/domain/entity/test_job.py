from datetime import date
from uuid import UUID

from hypothesis import given, strategies as st
from hypothesis.strategies import composite

from src.domain.entity.job import Job, JobStatus


@composite
def job_strategy(draw):
    """Hypothesis strategy to generate Job instances."""
    return Job(
        id=draw(st.uuids()),
        title=draw(st.text(min_size=1, max_size=100)),
        company=draw(st.text(min_size=1, max_size=100)),
        status=draw(st.sampled_from(JobStatus)),
        country=draw(st.text(min_size=1, max_size=50)),
        city=draw(st.text(min_size=1, max_size=50)),
        description=draw(st.text(min_size=1, max_size=2500)),
        notes=draw(st.text(min_size=0, max_size=1000)),
        external_id=draw(st.text(min_size=0, max_size=250)),
        platform=draw(st.text(min_size=0, max_size=250)),
        date_applied=draw(st.dates(max_value=date.today())),
        date_updated=draw(st.dates(max_value=date.today())),
    )


@given(job=job_strategy())
def test_job_init(job):
    """Test Job initialization with Hypothesis."""
    assert isinstance(job, Job)
    assert isinstance(job.id, UUID)
    assert len(job.title) > 0
    assert job.status in JobStatus
    assert job.date_applied <= date.today()
    assert job.date_updated <= date.today()


@given(job=job_strategy())
def test_job_to_dict(job):
    """Test the to_dict method with Hypothesis."""
    job_dict = job.to_dict()
    assert job_dict["id"] == job.id
    assert job_dict["status"] == job.status
    assert job_dict["title"] == job.title
    assert job_dict["date_applied"] == job.date_applied
    assert isinstance(job_dict, dict)


@given(job=job_strategy())
def test_job_from_dict(job):
    """Test the from_dict method with Hypothesis."""
    job_dict = job.to_dict()
    job1 = Job.from_dict(job_dict)
    job2 = Job.from_dict(job_dict)
    assert job1 == job2
