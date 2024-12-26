from src.application.infrastructure.sql.models.job import job_table
from src.application.interface.mappers.job import JobMapper
from src.core.gateway.sql.sql_gateway import SQLGateway


class JobSQLGateway(SQLGateway, table=job_table):
    mapper = JobMapper()
