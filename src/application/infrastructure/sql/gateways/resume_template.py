from src.application.infrastructure.sql.models.resume_template import (
    resume_template_table,
)
from src.core.gateway.sql.sql_gateway import SQLGateway


class ResumeTemplateSQLGateway(SQLGateway, table=resume_template_table):
    pass
