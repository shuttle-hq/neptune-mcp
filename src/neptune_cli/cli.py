import os

import click

from loguru import logger as log


from neptune_cli.client import Client
from neptune_cli.config import SETTINGS
from neptune_cli.mcp import mcp as mcp_server
from neptune_cli.auth import serve_callback_handler


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

    if not os.path.exists("neptune.json"):
        log.error("neptune.json not found in the current directory")
        return

    with open("neptune.json", "r") as f:
        project_data = f.read()

    from neptune_aws_platform.models.api import PutProjectRequest

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
def login():
    """Authenticate with Neptune
    """
    port, httpd, thread = serve_callback_handler()
    
    import webbrowser

    from urllib.parse import urlencode
    params = urlencode({"redirect_uri": f"http://localhost:{port}/callback"})
    
    login_url = f"{SETTINGS.api_base_url}/auth/login?{params}"
    if not webbrowser.open(login_url):
        print("Please open the following URL in a browser to log in:")
        print()
        print(f"    {login_url}")
        print()

    thread.join()

    if httpd.access_token is not None:
        SETTINGS.access_token = httpd.access_token
        SETTINGS.save_to_file()

    print(httpd.callback_received and "Login successful!" or "Login failed.")


if __name__ == "__main__":
    cli()
