from uuid import UUID

from hypothesis import given, strategies as st
from hypothesis.strategies import composite

from src.application.domain.entity.job import (
    EmploymentType,
    Job,
    JobStatus,
    WorkSettingType,
)
from src.application.domain.enums.country import Country


@composite
def country_strategy(draw):
    """Hypothesis strategy to generate Country instances."""
    return draw(st.sampled_from(list(Country)))


@composite
def job_strategy(draw):
    """Hypothesis strategy to generate Job instances."""
    return Job.create(
        user_id=draw(st.uuids(version=4)),
        title=draw(st.text(min_size=1, max_size=100)),
        company=draw(st.text(min_size=1, max_size=100)),
        description=draw(st.text(min_size=1, max_size=2500)),
        country=draw(country_strategy()),
        city=draw(st.text(min_size=1, max_size=50)),
        work_setting_type=draw(st.sampled_from(list(WorkSettingType))),
        status=draw(st.sampled_from(list(JobStatus))),
        employment_type=draw(st.sampled_from(list(EmploymentType))),
        notes=draw(st.text(min_size=0, max_size=1000)),
        external_id=draw(st.text(min_size=0, max_size=250)),
        platform=draw(st.text(min_size=0, max_size=250)),
        url=draw(st.text(min_size=0, max_size=500)),
    )


@given(job=job_strategy())
def test_job_init(job):
    """Test Job initialization with Hypothesis."""
    assert isinstance(job, Job)
    assert isinstance(job.id, UUID)
    assert isinstance(job.user_id, UUID)
    assert isinstance(job.country, Country)
    assert len(job.title) > 0
    assert job.status in JobStatus
    assert job.work_setting_type in WorkSettingType
    assert job.employment_type in EmploymentType
    assert job.created_at is not None
    assert job.updated_at is not None
