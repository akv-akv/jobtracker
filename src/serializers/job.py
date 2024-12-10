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
                "status": o.status.value,
                "country": o.country,
                "city": o.city,
                "description": o.description,
                "notes": o.notes,
                "external_id": o.external_id,
                "platform": o.platform,
                "date_applied": o.date_applied.isoformat(),
                "date_updated": o.date_updated.isoformat(),
            }
        # Default fallback
        return super().default(o)
