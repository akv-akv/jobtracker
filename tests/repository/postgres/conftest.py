# import pytest
# import sqlalchemy
# from sqlalchemy.orm import sessionmaker

# from src.repository.job_postgres import Base, JobSQLModel


# @pytest.fixture(scope="session")
# def pg_session_empty(app_configuration):
#     """Set up an empty PostgreSQL test database session."""
#     conn_str = "postgresql+psycopg2://{}:{}@{}:{}/{}".format(
#         app_configuration["POSTGRES_USER"],
#         app_configuration["POSTGRES_PASSWORD"],
#         app_configuration["POSTGRES_HOSTNAME"],
#         app_configuration["POSTGRES_PORT"],
#         app_configuration["APPLICATION_DB"],
#     )
#     engine = sqlalchemy.create_engine(conn_str)
#     connection = engine.connect()

#     Base.metadata.create_all(engine)
#     Base.metadata.bind = engine

#     DBSession = sessionmaker(bind=engine)
#     session = DBSession()

#     yield session

#     session.close()
#     connection.close()


# @pytest.fixture(scope="session")
# def pg_test_job_data():
#     """Provide test data for jobs."""
#     return [
#         {
#             "id": "f853578c-fc0f-4e65-81b8-566c5dffa35a",
#             "title": "Software Engineer",
#             "company": "TechCorp",
#             "status": "APPLIED",
#             "country": "USA",
#             "city": "New York",
#             "description": "Great opportunity",
#             "date_applied": "2023-01-01",
#             "date_updated": "2023-01-10",
#         },
#         {
#             "id": "fe2c3195-aeff-487a-a08f-e0bdc0ec6e9a",
#             "title": "Data Scientist",
#             "company": "DataCorp",
#             "status": "INTERVIEWING",
#             "country": "Canada",
#             "city": "Toronto",
#             "description": "Data science role",
#             "date_applied": "2023-02-01",
#             "date_updated": "2023-02-10",
#         },
#     ]


# @pytest.fixture(scope="function")
# def pg_session_with_jobs(pg_session_empty, pg_test_job_data):
#     """Set up a PostgreSQL session preloaded with test job data."""
#     for data in pg_test_job_data:
#         job = JobSQLModel(
#             id=data["id"],
#             title=data["title"],
#             company=data["company"],
#             status=data["status"],
#             country=data["country"],
#             city=data["city"],
#             description=data["description"],
#             date_applied=data["date_applied"],
#             date_updated=data["date_updated"],
#         )
#         pg_session_empty.add(job)
#         pg_session_empty.commit()

#     yield pg_session_empty

#     pg_session_empty.query(JobSQLModel).delete()
