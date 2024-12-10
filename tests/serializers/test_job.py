import json

from hypothesis import given

from src.serializers.job import JobJsonEncoder
from tests.src.domain.entity.test_job import job_strategy


@given(job=job_strategy())
def test_job_serializer(job):
    """Test the serialization of Job instances."""
    serialized_job = json.dumps(job, cls=JobJsonEncoder)
    job_dict = json.loads(serialized_job)

    assert job_dict["id"] == str(job.id)
    assert job_dict["status"] == job.status.value
    assert job_dict["title"] == job.title
    assert job_dict["company"] == job.company
    assert job_dict["country"] == job.country
    assert job_dict["city"] == job.city
    assert job_dict["description"] == job.description
    assert job_dict["notes"] == job.notes
    assert job_dict["external_id"] == job.external_id
    assert job_dict["platform"] == job.platform
    assert job_dict["date_applied"] == job.date_applied.isoformat()
    assert job_dict["date_updated"] == job.date_updated.isoformat()
