from sqlalchemy import MetaData

from src.application.infrastructure.sql.models.job import job_metadata
from src.application.infrastructure.sql.models.user import user_metadata

metadata = MetaData()

# Combine all individual metadata objects
for meta in [job_metadata, user_metadata]:
    for table in meta.tables.values():
        table.tometadata(metadata)
