# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Neptune CLI is a Python CLI application for the Neptune cloud deployment platform. It provides both a command-line interface and an MCP (Model Context Protocol) server for AI assistant integration.

## Development Commands

```bash
# Install dependencies
uv sync
uv sync --group dev          # Include dev dependencies

# Run the CLI locally
uv run neptune mcp           # Start MCP server (stdio transport)
uv run neptune login         # Authenticate with Neptune
uv run neptune version       # Show version

# Linting and formatting
ruff check src/              # Lint
ruff check --fix src/        # Lint with auto-fix
ruff format src/             # Format

# Build binary (PyInstaller)
uv run pyinstaller neptune.spec --clean --noconfirm

# Pre-commit hooks
pre-commit run --all-files
```

## Architecture

**Entry Points:**

-   `src/neptune_cli/cli.py` - Click-based CLI with commands: `mcp`, `login`, `version`, `upgrade`
-   `src/neptune_cli/mcp.py` - FastMCP server exposing tools for AI assistants

**Core Components:**

-   `client.py` - HTTP API client for Neptune backend
-   `config.py` - Pydantic-based settings (stored in `~/.config/neptune/config.json`)
-   `auth.py` - OAuth callback handler with local HTTP server
-   `version.py` / `upgrade.py` - Version checking and binary auto-update

**MCP Tools (in `mcp.py`):**
The MCP server exposes tools for the full deployment lifecycle: `get_project_schema`, `login`, `add_new_resource`, `provision_resources`, `deploy_project`, `get_deployment_status`, `get_logs`, `wait_for_deployment`, `set_secret_value`, `list_bucket_files`, `get_bucket_object`, `delete_project`, `upgrade_cli`, `info`

**Key Files:**

-   `mcp_instructions.md` - Instructions loaded into MCP server for AI guidance
-   `neptune.spec` - PyInstaller configuration for cross-platform binary builds

## Code Style

-   Python 3.13+
-   Line length: 120 characters
-   Double quotes
-   Ruff for linting (E, F, I rules; E501 ignored)
-   Loguru for logging

## External Dependencies

-   `neptune-common` - Shared types from GitHub (git dependency)
-   `fastmcp` - MCP server implementation
-   `click` - CLI framework
-   `pydantic-settings` - Configuration management
