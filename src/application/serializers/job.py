from json import JSONEncoder
from typing import Any

from src.application.domain.entity.job import Job


class JobJsonEncoder(JSONEncoder):
    def default(self, o: Any) -> Any:
        # Handle Job instance
        if isinstance(o, Job):
            return {
                "id": str(o.id),
                "title": o.title,
                "company": o.company,
                "status": o.status.name,
            }
        # Default fallback
        return super().default(o)
