from datetime import datetime, timezone
from uuid import UUID

import pytest

from src.application.domain.entity.job import EmploymentType, JobStatus, WorkSettingType
from src.application.domain.enums.country import Country
from src.application.interface.mappers.job import JobMapper


@pytest.fixture
def job_mapper():
    return JobMapper()


@pytest.mark.parametrize(
    "external_job, expected_internal",
    [
        # Full valid input
        (
            {
                "id": UUID("40f478ce-1128-4eaa-b9c3-0f0d5e0bb789"),
                "user_id": UUID("d265a881-0530-4dae-b3d8-dd5d4f6a55a6"),
                "title": "Data Engineer",
                "company": "Tech Co",
                "description": "Job Description",
                "country": "UnitedStates",
                "city": "Remote",
                "work_setting_type": "REMOTE",
                "status": "ADDED",
                "employment_type": "FULLTIME",
                "notes": "Some notes",
                "external_id": "123",
                "platform": "LinkedIn",
                "url": "https://example.com",
                "created_at": datetime(2024, 12, 23, 10, 53, 19, tzinfo=timezone.utc),
                "updated_at": datetime(2024, 12, 23, 10, 55, 19, tzinfo=timezone.utc),
            },
            {
                "id": UUID("40f478ce-1128-4eaa-b9c3-0f0d5e0bb789"),
                "user_id": UUID("d265a881-0530-4dae-b3d8-dd5d4f6a55a6"),
                "title": "Data Engineer",
                "company": "Tech Co",
                "description": "Job Description",
                "country": Country.UnitedStates,
                "city": "Remote",
                "work_setting_type": WorkSettingType.REMOTE,
                "status": JobStatus.ADDED,
                "employment_type": EmploymentType.FULLTIME,
                "notes": "Some notes",
                "external_id": "123",
                "platform": "LinkedIn",
                "url": "https://example.com",
                "created_at": datetime(2024, 12, 23, 10, 53, 19, tzinfo=timezone.utc),
                "updated_at": datetime(2024, 12, 23, 10, 55, 19, tzinfo=timezone.utc),
            },
        ),
        # Missing optional fields
        (
            {
                "id": UUID("40f478ce-1128-4eaa-b9c3-0f0d5e0bb789"),
                "user_id": UUID("d265a881-0530-4dae-b3d8-dd5d4f6a55a6"),
                "title": "Data Engineer",
                "company": "Tech Co",
                "description": "Job Description",
                "country": "UnitedStates",
                "city": "Remote",
                "status": "ADDED",
            },
            {
                "id": UUID("40f478ce-1128-4eaa-b9c3-0f0d5e0bb789"),
                "user_id": UUID("d265a881-0530-4dae-b3d8-dd5d4f6a55a6"),
                "title": "Data Engineer",
                "company": "Tech Co",
                "description": "Job Description",
                "country": Country.UnitedStates,
                "city": "Remote",
                "work_setting_type": None,
                "status": JobStatus.ADDED,
                "employment_type": None,
                "notes": None,
                "external_id": None,
                "platform": None,
                "url": None,
                "created_at": None,
                "updated_at": None,
            },
        ),
    ],
)
@pytest.mark.asyncio
async def test_to_internal(job_mapper, external_job, expected_internal):
    result = await job_mapper.to_internal(external_job)
    assert result == expected_internal


@pytest.mark.parametrize(
    "internal_job, expected_external",
    [
        # Full valid internal input
        (
            {
                "id": UUID("40f478ce-1128-4eaa-b9c3-0f0d5e0bb789"),
                "user_id": UUID("d265a881-0530-4dae-b3d8-dd5d4f6a55a6"),
                "title": "Data Engineer",
                "company": "Tech Co",
                "description": "Job Description",
                "country": Country.UnitedStates,
                "city": "Remote",
                "work_setting_type": WorkSettingType.REMOTE,
                "status": JobStatus.ADDED,
                "employment_type": EmploymentType.FULLTIME,
                "notes": "Some notes",
                "external_id": "123",
                "platform": "LinkedIn",
                "url": "https://example.com",
                "created_at": datetime(2024, 12, 23, 10, 53, 19, tzinfo=timezone.utc),
                "updated_at": datetime(2024, 12, 23, 10, 55, 19, tzinfo=timezone.utc),
            },
            {
                "id": UUID("40f478ce-1128-4eaa-b9c3-0f0d5e0bb789"),
                "user_id": UUID("d265a881-0530-4dae-b3d8-dd5d4f6a55a6"),
                "title": "Data Engineer",
                "company": "Tech Co",
                "description": "Job Description",
                "country": "UnitedStates",
                "city": "Remote",
                "work_setting_type": "REMOTE",
                "status": "ADDED",
                "employment_type": "FULLTIME",
                "notes": "Some notes",
                "external_id": "123",
                "platform": "LinkedIn",
                "url": "https://example.com",
                "created_at": datetime(2024, 12, 23, 10, 53, 19, tzinfo=timezone.utc),
                "updated_at": datetime(2024, 12, 23, 10, 55, 19, tzinfo=timezone.utc),
            },
        )
    ],
)
@pytest.mark.asyncio
async def test_to_external(job_mapper, internal_job, expected_external):
    result = await job_mapper.to_external(internal_job)
    assert result == expected_external
