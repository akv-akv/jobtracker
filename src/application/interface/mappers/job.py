from typing import Any, Dict

from src.application.domain.entity.job import EmploymentType, JobStatus, WorkSettingType
from src.application.domain.enums.country import Country
from src.core.repository.base.mapper import Mapper


class JobMapper(Mapper):
    async def to_internal(self, external: Dict[str, Any]) -> Dict[str, Any]:
        return {
            "id": external.get("id"),
            "user_id": external.get("user_id"),
            "title": external.get("title"),
            "company": external.get("company"),
            "description": external.get("description"),
            "country": (
                Country[external["country"]] if external.get("country") else None
            ),
            "city": external.get("city"),
            "work_setting_type": (
                WorkSettingType[external["work_setting_type"]]
                if external.get("work_setting_type")
                else None
            ),
            "status": JobStatus[external["status"]] if external.get("status") else None,
            "employment_type": (
                EmploymentType[external["employment_type"]]
                if external.get("employment_type")
                else None
            ),
            "notes": external.get("notes"),
            "external_id": external.get("external_id"),
            "platform": external.get("platform"),
            "url": external.get("url"),
            "created_at": external.get("created_at"),
            "updated_at": external.get("updated_at"),
        }

    async def to_external(self, internal: Dict[str, Any]) -> Dict[str, Any]:
        return {
            "id": internal["id"],
            "user_id": internal["user_id"],
            "title": internal["title"],
            "company": internal["company"],
            "description": internal["description"],
            "country": internal["country"].name,
            "city": internal["city"],
            "work_setting_type": (
                internal["work_setting_type"].name
                if internal.get("work_setting_type")
                else None
            ),
            "status": internal["status"].name if internal.get("status") else None,
            "employment_type": (
                internal["employment_type"].name
                if internal.get("employment_type")
                else None
            ),
            "notes": internal.get("notes"),
            "external_id": internal.get("external_id"),
            "platform": internal.get("platform"),
            "url": internal.get("url"),
            "created_at": internal.get("created_at"),
            "updated_at": internal.get("updated_at"),
        }
