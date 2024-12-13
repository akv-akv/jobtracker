#! /usr/bin/env python

import json
import os
import subprocess
import time
from typing import Optional

import psycopg2
import typer
from dotenv import load_dotenv
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT

app = typer.Typer(help="Management CLI for Job Tracker")

APPLICATION_CONFIG_PATH = "config"
DOCKER_PATH = "docker"


def setenv(variable, default):
    """Ensure an environment variable exists and has a value."""
    os.environ[variable] = os.getenv(variable, default)


def app_config_file(config: str) -> str:
    return os.path.join(APPLICATION_CONFIG_PATH, f"{config}.json")


def docker_compose_file(config: Optional[str]) -> str:
    """Generate the path to the Docker Compose file."""
    if not config:
        raise ValueError("The APPLICATION_CONFIG environment variable is not set.")
    return os.path.join(DOCKER_PATH, f"{config}.yml")


def read_json_configuration(config: str) -> dict:
    """Read configuration from the relative JSON file."""
    with open(app_config_file(config)) as f:
        config_data = json.load(f)

    # Convert the config into a usable Python dictionary
    config_data = {i["name"]: i["value"] for i in config_data}
    return config_data


def configure_app(config: Optional[str]):
    """Load application configuration from .env or JSON."""
    if not config:
        raise ValueError("The APPLICATION_CONFIG environment variable is not set.")
    dotenv_path = os.path.join(APPLICATION_CONFIG_PATH, f"{config}.env")
    if os.path.exists(dotenv_path):
        load_dotenv(dotenv_path)
    else:
        configuration = read_json_configuration(config)
        for key, value in configuration.items():
            setenv(key, value)


def docker_compose_cmdline(commands_string: Optional[str] = None) -> list:
    """Generate the docker compose command line."""
    config = os.getenv("APPLICATION_CONFIG")
    configure_app(config)

    compose_file = docker_compose_file(config)

    if not os.path.isfile(compose_file):
        raise ValueError(f"The file {compose_file} does not exist")

    command_line = [
        "docker",
        "compose",
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
    """Wait for a specific message in the logs."""
    while True:
        try:
            logs = subprocess.check_output(cmdline)
            if message in logs.decode("utf-8"):
                break
        except subprocess.CalledProcessError as e:
            print(f"Error running command: {e.cmd}")
            print(f"Output: {e.output.decode('utf-8')}")
        time.sleep(1)


@app.command()
def test(args: list[str] = typer.Argument([], help="Arguments to pass to pytest")):
    """
    Run integration tests using Docker and pytest.
    """
    config = os.getenv("APPLICATION_CONFIG", "testing")
    configure_app(config)

    # Start Docker services
    typer.echo("Starting Docker services...")
    cmdline = docker_compose_cmdline("up -d")
    subprocess.call(cmdline)

    # Wait for Postgres to be ready
    typer.echo("Waiting for Postgres to be ready...")
    cmdline = docker_compose_cmdline("logs postgres")
    wait_for_logs(cmdline, "ready to accept connections")

    # Create the test database
    typer.echo("Creating test database...")
    run_sql([f"CREATE DATABASE {os.getenv('APPLICATION_DB')}"])

    # Run tests with explicit test directory
    typer.echo("Running tests...")
    pytest_cmd = [
        "pytest",
        "-svv",
        "--cov=application",
        "--cov-report=term-missing",
        "--integration",
        "tests",
    ]
    pytest_cmd.extend(args)
    subprocess.call(pytest_cmd)

    # Stop Docker services
    typer.echo("Stopping Docker services...")
    cmdline = docker_compose_cmdline("down")
    subprocess.call(cmdline)


if __name__ == "__main__":
    app()
