#! /usr/bin/env python
import asyncio
import os
from functools import wraps
from typing import Optional
from uuid import UUID

import typer

from application import JobRepository, ManageJob, ManageUser, UserRepository
from infrastructure import JobSQLGateway, UserSQLGateway
from manage import configure_app
from src.domain.entity.job import EmploymentType, JobStatus, WorkSettingType
from src.domain.enums.country import Country
from src.repository.base.pagination import PageOptions
from src.repository.sql.asyncpg_sql_database import AsyncpgSQLDatabase
from src.use_case.add_job import add_job as add_job_use_case

# from src.use_case.delete_job import delete_job as delete_job_use_case
# from src.use_case.list_jobs import list_jobs as list_jobs_use_case
# from src.use_case.update_job import update_job as update_job_use_case

# from src.repository.job_postgres import JobRepositoryPostgres


app = typer.Typer(help="Job Tracker CLI Tool")


def get_database_url() -> str:
    """Load the database configuration dynamically."""
    configure_app(
        "production"
    )  # Replace with the desired environment (e.g., testing, development)
    db_config = {
        "USER": os.getenv("POSTGRES_USER"),
        "PASSWORD": os.getenv("POSTGRES_PASSWORD"),
        "HOST": os.getenv("POSTGRES_HOSTNAME"),
        "PORT": os.getenv("POSTGRES_PORT"),
        "NAME": os.getenv("APPLICATION_DB"),
    }
    return (
        f"{db_config['USER']}:"
        f"{db_config['PASSWORD']}@{db_config['HOST']}:"
        f"{db_config['PORT']}/{db_config['NAME']}"
    )


db = AsyncpgSQLDatabase(get_database_url())


job_gateway = JobSQLGateway(db)
manage_job = ManageJob(JobRepository(job_gateway))
user_gateway = UserSQLGateway(db)
manage_user = ManageUser(UserRepository(user_gateway))


def typer_async(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        return asyncio.run(f(*args, **kwargs))

    return wrapper


@app.command()
@typer_async
async def add_user(
    name: str = typer.Argument(..., help="User name"),
):
    """Add a new user."""
    data = {"name": name}
    # Call the create method in ManageJob
    response = await manage_user.create(data)

    if response:
        typer.echo(f"User '{response.name}' added successfully (id = {response.id}).")
    else:
        typer.echo("Error: User was not added")


@app.command()
@typer_async
async def add_job(
    user_id: str = typer.Argument(..., help="User ID who owns the job."),
    title: str = typer.Argument(..., help="Title of the job."),
    company: str = typer.Argument(..., help="Company offering the job."),
    status: JobStatus = typer.Option(JobStatus.ADDED.value, help="Job status."),
    country: str = typer.Option(
        Country.UnitedArabEmirates.value, help="Country of the job."
    ),
    city: str = typer.Option("Remote", help="City of the job."),
    work_setting_type: Optional[WorkSettingType] = typer.Option(
        None, help="Work setting type (REMOTE, HYBRID, ONSITE)."
    ),
    employment_type: Optional[EmploymentType] = typer.Option(
        EmploymentType.FULLTIME.value,
        help="Employment type (FULLTIME, TEMPORARY, CONTRACT).",
    ),
    notes: Optional[str] = typer.Option(None, help="Additional notes about the job."),
    external_id: Optional[str] = typer.Option(None, help="External ID of the job."),
    platform: Optional[str] = typer.Option(
        None, help="Platform where the job is listed."
    ),
    url: Optional[str] = typer.Option(None, help="URL of the job listing."),
    description_file: str = typer.Option(
        None, help="Path to a file containing the job description."
    ),
):
    """Add a new job."""
    # Load description from file or input
    if description_file:
        with open(description_file, "r") as f:
            description = f.read()
    else:
        typer.echo(
            "Enter the job description. Press Ctrl+D (or Ctrl+Z on Windows) when done:"
        )
        description = typer.get_text_stream("stdin").read()

    user = await manage_user.retrieve(UUID(user_id))
    if not user:
        typer.echo(f"Error: User with ID {user_id} not found.")
        return

    # Prepare job data
    data = {
        "user": user,
        "title": title,
        "company": company,
        "description": description.strip(),
        "country": Country(country),
        "city": city,
        "work_setting_type": work_setting_type,
        "status": status,
        "employment_type": employment_type,
        "notes": notes,
        "external_id": external_id,
        "platform": platform,
        "url": url,
    }

    response = await add_job_use_case(data, manage_job)
    print(response.message)
    if response:
        typer.echo(
            f"Job '{response.title}' at "
            f"'{response.company}' added successfully (id = {response.id})."
        )
    else:
        typer.echo("Job creation failed")


@app.command()
@typer_async
async def delete_job(
    id: str = typer.Argument(..., help="Id of the job."),
):
    job = await manage_job.destroy(UUID(id))

    if job:
        typer.echo(f"Job '{id}' was deleted successfully.")
    else:
        typer.echo("Error:")


@app.command()
@typer_async
async def delete_user(
    id: str = typer.Argument(..., help="Id of the user."),
):
    try:
        job = await manage_user.destroy(UUID(id))
        if job:
            typer.echo(f"User '{id}' was deleted successfully.")
    except Exception as e:
        print(e)


@app.command()
@typer_async
async def list_jobs(
    status: list[str] = typer.Option(
        None, "--status", "-s", help="Filter by job status."
    ),
    company: str = typer.Option(
        None, "--company", "-c", help="Filter by company name."
    ),
    country: str = typer.Option(None, "--country", help="Filter by country."),
    city: str = typer.Option(None, "--city", help="Filter by city."),
    date_applied_gt: str = typer.Option(
        None,
        "--date-applied-gt",
        help="Filter by jobs applied after this date (YYYY-MM-DD).",
    ),
    date_applied_lt: str = typer.Option(
        None,
        "--date-applied-lt",
        help="Filter by jobs applied before this date (YYYY-MM-DD).",
    ),
):
    """List jobs with optional filters."""
    # filters = {
    #     "status": status,
    #     "company": company,
    #     "country": country,
    #     "city": city,
    #     "date_applied__gt": date_applied_gt,
    #     "date_applied__lt": date_applied_lt,
    # }
    offset = 0
    total_retrieved = 0

    while True:
        # Prepare pagination options
        params = PageOptions(
            limit=2,
            offset=offset,
            order_by="created_at",
            ascending=True,
            # cursor=datetime
        )

        # Fetch a page of jobs
        response = await manage_job.list(params=params)

        # Check for success
        if not response.items:
            break

        # Display retrieved jobs
        for job in response.items:
            typer.echo(f"{job.id}: {job.title} at {job.company} ({job.status})")

        # Update pagination details
        total_retrieved += len(response.items)
        offset += len(response.items)

        typer.echo(f"Retrieved {total_retrieved}/{response.total} jobs.")

        # Break if all jobs are retrieved
        if total_retrieved >= response.total:
            break


@app.command()
@typer_async
async def update_job(
    job_id: str = typer.Argument(..., help="ID of the job to update."),
    title: str = typer.Option(None, help="New title for the job."),
    company: str = typer.Option(None, help="New company name."),
    status: JobStatus = typer.Option(
        None, help="New status (APPLIED, INTERVIEWING, OFFERED, REJECTED)."
    ),
    country: str = typer.Option(None, help="New country for the job."),
    city: str = typer.Option(None, help="New city for the job."),
    description: str = typer.Option(None, help="New description for the job."),
):
    """Update an existing job."""
    data = {
        "title": title,
        "company": company,
        "status": status,
        "country": country,
        "city": city,
        "description": description,
    }
    data = {k: v for k, v in data.items() if v is not None}

    response = await manage_job.update(UUID(job_id), data)
    print(response)

    if response:
        (f"Job '{job_id}' updated successfully.")
    else:
        typer.echo("Error: ")


if __name__ == "__main__":
    asyncio.run(app())
