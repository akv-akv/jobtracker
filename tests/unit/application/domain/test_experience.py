from datetime import date
from typing import Optional
from uuid import UUID, uuid4

from src.application.domain.entity.experience import Experience
from src.core.domain.versioned_root_entity import VersionedRootEntity


def test_create_experience():
    data = {
        "user_id": uuid4(),
        "job_title": "Senior Data Engineer",
        "company_name": "Random company",
        "start_date": date(2024, 1, 2),
        "end_date": None,
        "location": "Remote",
        "company_description": None,
        "bullet_points": [
            "Achieved X by doing Y leading to Z impact",
            "Optimized X by Y percent in Z months",
        ],
    }
    obj = Experience.create(**data)
    assert isinstance(obj, Experience)
    assert issubclass(Experience, VersionedRootEntity)
    assert isinstance(obj.user_id, UUID)
    assert isinstance(obj.bullet_points, list)
    assert len(obj.bullet_points) == 2
    assert isinstance(obj.start_date, date)
    assert isinstance(obj.end_date, Optional[date])
