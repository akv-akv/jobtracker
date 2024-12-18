from json import JSONEncoder
from typing import Any

from src.domain.entity.job import Job


class JobJsonEncoder(JSONEncoder):
    def default(self, o: Any) -> Any:
        # Handle Job instance
        if isinstance(o, Job):
            return {
                "id": str(o.id),
                "title": o.title,
                "company": o.company,
                "status": o.status.name,
                "country": o.country.value,
                "city": o.city,
                "description": o.description,
                "notes": o.notes,
                "external_id": o.external_id,
                "platform": o.platform,
                "created_at": o.created_at.isoformat(),
                "updated_at": o.updated_at.isoformat(),
            }
        # Default fallback
        return super().default(o)
