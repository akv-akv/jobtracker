#! /usr/bin/env python
import asyncio
from functools import wraps
from typing import Optional
from uuid import UUID

import typer

from manage import get_database_url
from src.application.domain.entity.job import EmploymentType, JobStatus, WorkSettingType
from src.application.domain.enums.country import Country
from src.application.infrastructure.repository.job import JobRepository
from src.application.infrastructure.repository.resume_main_info import (
    ResumeMainInfoRepository,
)
from src.application.infrastructure.repository.user import UserRepository
from src.application.infrastructure.sql.gateways.job import JobSQLGateway
from src.application.infrastructure.sql.gateways.resume_main_info import (
    ResumeMainInfoSQLGateway,
)
from src.application.infrastructure.sql.gateways.user import UserSQLGateway
from src.application.manage.job import ManageJob
from src.application.manage.resume_main_info import ManageResumeMainInfo
from src.application.manage.user import ManageUser
from src.application.use_case.job.add_job import add_job as add_job_use_case
from src.application.use_case.resume_main_info.add_resume_main_info import (
    add_resume_main_info as add_resume_main_info_use_case,
)
from src.application.use_case.resume_main_info.update_resume_main_info import (
    update_resume_main_info_use_case,
)
from src.core.gateway.sql.asyncpg_sql_database import AsyncpgSQLDatabase
from src.core.repository.base.pagination import PageOptions
from src.core.responses.response import ResponseTypes

# from src.application.use_case.delete_job import delete_job as delete_job_use_case
# from src.application.use_case.list_jobs import list_jobs as list_jobs_use_case
# from src.application.use_case.update_job import update_job as update_job_use_case

app = typer.Typer(help="Job Tracker CLI Tool")

db = AsyncpgSQLDatabase(get_database_url("production"))

job_gateway = JobSQLGateway(db)
manage_job = ManageJob(JobRepository(job_gateway))
user_gateway = UserSQLGateway(db)
manage_user = ManageUser(UserRepository(user_gateway))
resume_main_info_gateway = ResumeMainInfoSQLGateway(db)
manage_resume_main_info = ManageResumeMainInfo(
    ResumeMainInfoRepository(resume_main_info_gateway)
)


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
    title: str = typer.Argument(..., help="Title of the job."),
    company: str = typer.Argument(..., help="Company offering the job."),
    user_id: str = typer.Option(
        "be2ffb22-4b5b-4875-8b9a-06eb02d24421", help="User ID who owns the job."
    ),
    status: JobStatus = typer.Option(JobStatus.ADDED.value, help="Job status."),
    country: str = typer.Option(
        Country.UnitedArabEmirates.name, help="Country of the job."
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
        "user_id": user_id,
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
    # print(response.message)
    if response.type == ResponseTypes.SUCCESS:
        typer.echo(
            f"Job '{response.value.title}' at "
            f"'{response.value.company}' added successfully (id = {response.value.id})."
        )
    else:
        typer.echo(f"Job creation failed: {response.value}")


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
    if response:
        (f"Job '{job_id}' updated successfully.")
    else:
        typer.echo("Error: ")


@app.command()
@typer_async
async def add_resume_main_info(
    applicant_name: str = typer.Argument(..., help="Applicant name."),
    skills: str = typer.Argument(..., help="List of skills separated by comma."),
    user_id: str = typer.Option(
        "be2ffb22-4b5b-4875-8b9a-06eb02d24421", help="User ID who owns the job."
    ),
):
    """Add a new resume main info."""
    user = await manage_user.retrieve(UUID(user_id))
    if not user:
        typer.echo(f"Error: User with ID {user_id} not found.")
        return

    # Prepare job data
    data = {
        "user_id": user.id,
        "applicant_name": applicant_name,
        "skills": skills.split(","),
    }
    print(data)
    response = await add_resume_main_info_use_case(data, manage_resume_main_info)
    # print(response.message)
    if response.type == ResponseTypes.SUCCESS:
        typer.echo(f"Resume main info added successfully (id = {response.value.id}).")
    else:
        typer.echo(f"Job creation failed: {response.value}")


@app.command()
@typer_async
async def update_resume_main_info(
    resume_main_info_id: UUID = typer.Argument(
        ..., help="ID of the resume_main_info to update."
    ),
    resume_name: str = typer.Option(None, help="New resume_name"),
):
    """Update an existing job."""
    data = {
        "id": resume_main_info_id,
        "resume_name": resume_name,
    }
    data = {k: v for k, v in data.items() if v is not None}
    response = await update_resume_main_info_use_case(
        data, resume_main_info_manager=manage_resume_main_info
    )
    print(response)
    if response.type == ResponseTypes.SUCCESS:
        typer.echo(f"Resume main info updated successfully (id = {response.value.id}).")
    else:
        typer.echo(f"Resume update failed: {response.value}")


if __name__ == "__main__":
    asyncio.run(app())
