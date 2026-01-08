import click

from neptune_mcp.auth import serve_callback_handler
from neptune_mcp.config import SETTINGS
from neptune_mcp.observability import init_langtrace


@click.group(invoke_without_command=True)
@click.option(
    "--disable-telemetry",
    is_flag=True,
    default=False,
    help="Disable all telemetry/tracing (also supports NEPTUNE_MCP_DISABLE_TELEMETRY=1).",
)
@click.option(
    "--langtrace-api-key",
    default=None,
    help="Langtrace API key. If set, enables Langtrace telemetry for this run.",
)
@click.pass_context
def cli(ctx, disable_telemetry: bool, langtrace_api_key: str | None):
    """Start a Neptune MCP server (stdio) for the current project"""
    import os

    if disable_telemetry:
        # Set env var so any later imports (including neptune_mcp.mcp) can see it.
        os.environ["NEPTUNE_MCP_DISABLE_TELEMETRY"] = "1"

    if langtrace_api_key:
        # Must be set before init_langtrace() to ensure SDK initializes properly.
        os.environ["LANGTRACE_API_KEY"] = langtrace_api_key

    # Initialize telemetry *before* importing the MCP server module.
    init_langtrace()

    if ctx.invoked_subcommand is None:
        from neptune_mcp.mcp import mcp as mcp_server

        mcp_server.run()


@cli.command()
@click.option("--transport", "-t", help="Transport to use for MCP", default="stdio")
@click.option("--host", "-h", help="Host to use for MCP for HTTP transport", default="0.0.0.0")
@click.option("--port", "-p", help="Port to use for MCP for HTTP transport", default=8001)
def mcp(transport: str | None, host: str | None, port: int | None):
    """Start an MCP session for the current project"""
    from neptune_mcp.mcp import mcp as mcp_server

    if transport == "stdio":
        mcp_server.run()
    elif transport == "http":
        mcp_server.run(transport=transport, host=host, port=port)


@cli.command()
def login():
    """Authenticate with Neptune"""
    port, httpd, thread = serve_callback_handler()

    from urllib.parse import urlencode
    import webbrowser

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
