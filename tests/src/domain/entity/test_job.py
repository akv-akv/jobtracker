from datetime import date

from hypothesis import given, strategies as st

from src.domain.entity.job import Job, JobStatus


@given(
    id=st.uuids(),
    title=st.text(min_size=1, max_size=100),
    company=st.text(min_size=1, max_size=100),
    status=st.sampled_from(JobStatus),
    country=st.text(min_size=1, max_size=50),
    city=st.text(min_size=1, max_size=50),
    description=st.text(min_size=1, max_size=2500),
    notes=st.text(min_size=0, max_size=1000),
    external_id=st.text(min_size=0, max_size=250),
    platform=st.text(min_size=0, max_size=250),
    date_applied=st.dates(max_value=date.today()),
    date_updated=st.dates(max_value=date.today()),
)
def test_job_entity_with_enum(
    id,
    title,
    company,
    status,
    country,
    city,
    description,
    notes,
    external_id,
    platform,
    date_applied,
    date_updated,
):
    job = Job(
        id=id,
        title=title,
        company=company,
        status=status,
        country=country,
        city=city,
        description=description,
        notes=notes,
        external_id=external_id,
        platform=platform,
        date_applied=date_applied,
        date_updated=date_updated,
    )
    assert job.status in JobStatus
    assert job.date_applied <= date.today()
