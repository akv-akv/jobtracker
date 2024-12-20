#! /usr/bin/env python

import json
import os
import signal
import subprocess
import time
from typing import Optional

import psycopg2
import typer
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT

app = typer.Typer(help="Management CLI for Job Tracker")


# Ensure an environment variable exists and has a value
def setenv(variable: str, default: str):
    os.environ[variable] = os.getenv(variable, default)


setenv("APPLICATION_CONFIG", "production")

APPLICATION_CONFIG_PATH = "config"
DOCKER_PATH = "docker"


def app_config_file(config: Optional[str]) -> str:
    return os.path.join(APPLICATION_CONFIG_PATH, f"{config}.json")


def docker_compose_file(config: Optional[str]) -> str:
    return os.path.join(DOCKER_PATH, f"{config}.yml")


def read_json_configuration(config: Optional[str]) -> dict:
    """Read configuration from the relative JSON file."""
    with open(app_config_file(config)) as f:
        config_data = json.load(f)

    # Convert the config into a usable Python dictionary
    config_data = {i["name"]: i["value"] for i in config_data}
    return config_data


def configure_app(config: Optional[str]):
    """Load application configuration."""
    configuration = read_json_configuration(config)
    for key, value in configuration.items():
        setenv(key, value)


def docker_compose_cmdline(commands_string: Optional[str] = None) -> list:
    """Generate the Docker Compose command line."""
    config = os.getenv("APPLICATION_CONFIG")
    configure_app(config)

    compose_file = docker_compose_file(config)

    if not os.path.isfile(compose_file):
        raise ValueError(f"The file {compose_file} does not exist")

    command_line = [
        "docker-compose",
        "-p",
        config,
        "-f",
        compose_file,
    ]

    if commands_string:
        command_line.extend(commands_string.split(" "))

    return command_line


def run_sql(statements: list):
    """Run SQL statements on the database."""
    conn = psycopg2.connect(
        dbname=os.getenv("POSTGRES_DB"),
        user=os.getenv("POSTGRES_USER"),
        password=os.getenv("POSTGRES_PASSWORD"),
        host=os.getenv("POSTGRES_HOSTNAME"),
        port=os.getenv("POSTGRES_PORT"),
    )

    conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
    cursor = conn.cursor()
    for statement in statements:
        cursor.execute(statement)

    cursor.close()
    conn.close()


def wait_for_logs(cmdline: list, message: str):
    """Wait for a specific message in Docker logs."""
    logs = subprocess.check_output(cmdline)
    while message not in logs.decode("utf-8"):
        time.sleep(1)
        logs = subprocess.check_output(cmdline)


@app.command()
def compose(
    subcommand: list[str] = typer.Argument(..., help="Docker Compose subcommands"),
):
    """
    Run Docker Compose commands.
    """
    configure_app(os.getenv("APPLICATION_CONFIG"))
    cmdline = docker_compose_cmdline() + subcommand

    typer.echo(f"Running command: {' '.join(cmdline)}")
    try:
        process = subprocess.Popen(cmdline)
        process.wait()
    except KeyboardInterrupt:
        process.send_signal(signal.SIGINT)
        process.wait()


@app.command()
def init_postgres():
    """
    Initialize the Postgres database.
    """
    configure_app(os.getenv("APPLICATION_CONFIG"))

    try:
        run_sql([f"CREATE DATABASE {os.getenv('APPLICATION_DB')}"])
    except psycopg2.errors.DuplicateDatabase:
        typer.echo(
            f"The database {os.getenv('APPLICATION_DB')}"
            " already exists and will not be recreated."
        )


@app.command()
def test(args: list[str] = typer.Argument(..., help="Arguments to pass to pytest")):
    """
    Run integration tests.
    """
    os.environ["APPLICATION_CONFIG"] = "testing"
    configure_app(os.getenv("APPLICATION_CONFIG"))

    typer.echo("Starting Docker services...")
    cmdline = docker_compose_cmdline("up -d")
    subprocess.call(cmdline)

    typer.echo("Waiting for Postgres to be ready...")
    cmdline = docker_compose_cmdline("logs postgres")
    wait_for_logs(cmdline, "ready to accept connections")

    # run_sql([f"CREATE DATABASE {os.getenv('APPLICATION_DB')}"])

    typer.echo("Running tests...")
    pytest_cmd = [
        "pytest",
        "-svv",
        "--cov=application",
        "--cov-report=term-missing",
    ]
    pytest_cmd.extend(args)
    subprocess.call(pytest_cmd)

    typer.echo("Stopping Docker services...")
    cmdline = docker_compose_cmdline("down")
    subprocess.call(cmdline)


if __name__ == "__main__":
    app()
