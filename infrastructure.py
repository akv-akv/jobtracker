from typing import Any, Dict

from sql_models import job_table, user_table
from src.repository.base.mapper import Mapper
from src.repository.sql.sql_gateway import SQLGateway


class JobMapper(Mapper):
    def to_internal(self, external: Any) -> dict[str, Any]:
        """
        Converts a Job entity into a dictionary for database insertion.
        Overrides the parent `to_internal` method.
        """
        return {
            "id": external.get("id"),
            "user": external.get("user_id"),
            "title": external.get("title"),
            "company": external.get("company"),
            "description": external.get("description"),
            "country": external.get("country"),
            "city": external.get("city"),
            "work_setting_type": external.get("work_setting_type"),
            "status": external.get("status"),
            "employment_type": external.get("employment_type"),
            "notes": external.get("notes"),
            "external_id": external.get("external_id"),
            "platform": external.get("platform"),
            "url": external.get("url"),
            "created_at": external.get("created_at"),
            "updated_at": external.get("updated_at"),
        }

    def to_external(self, internal: Dict[str, Any]) -> Dict[str, Any]:
        """
        Converts a database record dictionary into an external
        dictionary representation.
        Overrides the parent `to_external` method.
        """
        print(internal)

        return {
            "id": internal["id"],
            # "user": internal["user_id"],
            "title": internal["title"],
            "company": internal["company"],
            "description": internal["description"],
            "country": internal["country"],
            "city": internal["city"],
            "work_setting_type": internal[
                "work_setting_type"
            ],  # Pass as-is (already a string or None)
            "status": internal["status"],  # Pass as-is (already a string)
            "employment_type": internal[
                "employment_type"
            ],  # Pass as-is (already a string or None)
            "notes": internal.get("notes"),
            "external_id": internal.get("external_id"),
            "platform": internal.get("platform"),
            "url": internal.get("url"),
            "created_at": internal.get("created_at"),
            "updated_at": internal.get("updated_at"),
        }


class JobSQLGateway(SQLGateway, table=job_table):
    mapper = JobMapper()


class UserSQLGateway(SQLGateway, table=user_table):
    pass
