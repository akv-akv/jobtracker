from sqlalchemy import MetaData

from src.application.infrastructure.sql.models.job import job_metadata
from src.application.infrastructure.sql.models.resume_main_info import (
    resume_main_info_metadata,
)
from src.application.infrastructure.sql.models.resume_template import (
    resume_template_metadata,
)
from src.application.infrastructure.sql.models.user import user_metadata

metadata = MetaData()

combined_metadata = [
    job_metadata,
    user_metadata,
    resume_main_info_metadata,
    resume_template_metadata,
]

# Combine all individual metadata objects
for meta in combined_metadata:
    for table in meta.tables.values():
        table.tometadata(metadata)
