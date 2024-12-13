#! /usr/bin/env python
import os
from uuid import uuid4

import typer
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from manage import configure_app
from src.repository.job_postgres import JobRepositoryPostgres
from src.responses.response import ResponseFailure, ResponseSuccess, ResponseTypes
from src.use_case.add_job import add_job as add_job_use_case
from src.use_case.delete_job import delete_job as delete_job_use_case
from src.use_case.list_jobs import list_jobs as list_jobs_use_case
from src.use_case.update_job import update_job as update_job_use_case

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
        f"postgresql+psycopg2://{db_config['USER']}:"
        f"{db_config['PASSWORD']}@{db_config['HOST']}:"
        f"{db_config['PORT']}/{db_config['NAME']}"
    )


def get_repository():
    """Initialize repository with a session."""
    database_url = get_database_url()
    engine = create_engine(database_url)
    Session = sessionmaker(bind=engine)
    session = Session()
    return JobRepositoryPostgres(session)


@app.command()
def add_job(
    title: str = typer.Argument(..., help="Title of the job."),
    company: str = typer.Argument(..., help="Company offering the job."),
    status: str = typer.Option("APPLIED", help="Job status."),
    country: str = typer.Option("UAE", help="Country of the job."),
    city: str = typer.Option("Remote", help="City of the job."),
    description_file: str = typer.Option(
        None, help="Path to a file containing the job description."
    ),
):
    """Add a new job."""
    if description_file:
        with open(description_file, "r") as f:
            description = f.read()
    else:
        typer.echo(
            "Enter the job description. Press Ctrl+D (or Ctrl+Z on Windows) when done:"
        )
        description = typer.get_text_stream("stdin").read()

    data = {
        "id": uuid4(),
        "title": title,
        "company": company,
        "status": status,
        "country": country,
        "city": city,
        "description": description.strip(),
    }

    repository = get_repository()
    response = add_job_use_case(data, repository)

    if response.type == ResponseTypes.SUCCESS:
        typer.echo(
            f"Job '{response.value.title}' at "
            f"'{response.value.company}' added successfully (id = {response.value.id})."
        )
    else:
        typer.echo(f"Error: {response.message}")


@app.command()
def delete_job(
    id: str = typer.Argument(..., help="Id of the job."),
):
    # Use the repository and execute the use case
    repository = get_repository()
    response = delete_job_use_case(id, repository)

    if response.type == ResponseTypes.SUCCESS:
        typer.echo(f"Job '{response.value}' was deleted successfully.")
    else:
        typer.echo(f"Error: {response.message}")


@app.command()
def list_jobs(
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
    filters = {
        "status": status,
        "company": company,
        "country": country,
        "city": city,
        "date_applied__gt": date_applied_gt,
        "date_applied__lt": date_applied_lt,
    }
    filters = {k: v for k, v in filters.items() if v is not None}

    repository = get_repository()
    response = list_jobs_use_case(filters, repository)

    if isinstance(response, ResponseSuccess):
        for job in response.value:
            typer.echo(f"{job.id}: {job.title} at {job.company} ({job.status.name})")
    elif isinstance(response, ResponseFailure):
        typer.echo(f"Error: {response.message}")


@app.command()
def update_job(
    job_id: str = typer.Argument(..., help="ID of the job to update."),
    title: str = typer.Option(None, help="New title for the job."),
    company: str = typer.Option(None, help="New company name."),
    status: str = typer.Option(
        None, help="New status (APPLIED, INTERVIEWING, OFFERED, REJECTED)."
    ),
    country: str = typer.Option(None, help="New country for the job."),
    city: str = typer.Option(None, help="New city for the job."),
    description: str = typer.Option(None, help="New description for the job."),
):
    """Update an existing job."""
    data = {
        "id": job_id,
        "title": title,
        "company": company,
        "status": status,
        "country": country,
        "city": city,
        "description": description,
    }
    data = {k: v for k, v in data.items() if v is not None}

    repository = get_repository()
    response = update_job_use_case(data, repository)

    if response.type == ResponseTypes.SUCCESS:
        typer.echo(f"Job '{response.value.title}' updated successfully.")
    else:
        typer.echo(f"Error: {response.message}")


if __name__ == "__main__":
    app()
