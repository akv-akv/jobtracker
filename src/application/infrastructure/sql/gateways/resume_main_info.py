from src.application.infrastructure.sql.models.resume_main_info import (
    resume_main_info_table,
)
from src.core.repository.sql.sql_gateway import SQLGateway


class ResumeMainInfoSQLGateway(SQLGateway, table=resume_main_info_table):
    pass
