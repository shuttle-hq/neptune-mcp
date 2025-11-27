import os

import click

from loguru import logger as log


from neptune_cli.client import Client
from neptune_cli.mcp import mcp as mcp_server


@click.group()
def cli():
    """AI-native cloud platform for your backend"""
    pass


@cli.group()
def ai():
    """AI-powered commands for Shuttle"""
    pass


@ai.command()
def init():
    """AI-assisted project initialization

    Currently not implemented.
    """
    raise NotImplementedError("AI init command is not implemented yet")


@ai.command()
def deploy():
    """AI-assisted deployment command

    Currently not implemented.
    """
    raise NotImplementedError("AI deploy command is not implemented yet")


@ai.command()
def fix():
    """AI-assisted code fixing command

    Currently not implemented.
    """
    raise NotImplementedError("AI fix command is not implemented yet")


@ai.command()
def mcp():
    """Start an MCP session for the current project"""
    mcp_server.run()


@cli.command()
def deploy():
    """Deploy the current project

    Currently not implemented.
    """
    raise NotImplementedError("deploy command is not implemented yet")


@cli.command()
def rollback():
    """Rollback the current deployment

    Currently not implemented.
    """
    raise NotImplementedError("rollback command is not implemented yet")


@cli.command()
def status():
    """Show status of the current deployment"""

    client = Client()

    if not os.path.exists("shuttle.json"):
        log.error("shuttle.json not found in the current directory")
        return

    with open("shuttle.json", "r") as f:
        project_data = f.read()

    from shuttle_aws_platform.models.api import PutProjectRequest

    project_request = PutProjectRequest.model_validate_json(project_data)

    project = client.get_project(project_request.name)
    if project is None:
        log.error(f"Project '{project_request.name}' not found; was it deployed?")
        return

    log.info(f"Project '{project.name}' status: {project.state}")
    for resource in project.resources:
        log.info(
            f" - Resource '{resource.name}' ({resource.kind}) status: {resource.status}"
        )
    for service, status in project.service_status.items():
        log.info(f" - Service '{service}' status: {status}")


@cli.command()
def logs():
    """Show logs for the current deployment"""
    raise NotImplementedError("logs command is not implemented yet")


@cli.command()
@click.option("--username", "-u", help="Username for login")
def login(username: str | None):
    """Authenticate with Shuttle

    Currently not implemented.
    """
    raise NotImplementedError("login command is not implemented yet")


if __name__ == "__main__":
    cli()
