from src.application.infrastructure.sql.models.user import user_table
from src.core.gateway.sql.sql_gateway import SQLGateway


class UserSQLGateway(SQLGateway, table=user_table):
    pass
