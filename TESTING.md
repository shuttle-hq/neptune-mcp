# Neptune Alpha Testing Guide

Welcome to Neptune alpha testing! This guide covers three ways to interact with Neptune:

1. **CLI** — Direct command-line usage
2. **CLI + AGENTS.md** — AI coding assistants with the AGENTS.md file
3. **CLI + MCP** — AI assistants via Model Context Protocol

---

## Prerequisites

-   **Python 3.12+** — Required for the CLI
-   **[uv](https://docs.astral.sh/uv/)** — Python package installer
-   **Docker** — Required for building and deploying applications
-   **AI Token** — Provided for alpha testers

---

## Installation

```bash
# Clone the repository
git clone https://github.com/shuttle-hq/neptune-cli-python.git
cd neptune-cli-python
git checkout CLI-porting

# Install the CLI
uv tool install -e .

# Verify installation
neptune --version
```

To reinstall after updates:

```bash
uv tool install -e . --force --reinstall
```

---

## Environment Setup

Set the required environment variable:

```bash
export NEPTUNE_AI_TOKEN=d1be6dcfea9f8a6d9ab3ef4f01e038bada71719fbefaf01a5e97b5758a2c75dc
```

Or create a `.env` file in your project directory or `~/.config/neptune/.env`:

```bash
NEPTUNE_AI_TOKEN=d1be6dcfea9f8a6d9ab3ef4f01e038bada71719fbefaf01a5e97b5758a2c75dc
```

---

# UX 1: CLI (Direct Command Line)

## Quick Start

```bash
# 1. Login to Neptune
neptune login

# 2. Navigate to your project
cd my-project

# 3. Initialize
neptune init

# 4. Generate neptune.json
neptune generate spec

# 5. Deploy
neptune deploy

# 6. Check status
neptune status

# 7. View logs
neptune logs
```

## Complete Command Reference

| Command                                | Description                                  |
| -------------------------------------- | -------------------------------------------- |
| `neptune login`                        | Authenticate with Neptune (opens browser)    |
| `neptune login --api-key <key>`        | Authenticate with an API key                 |
| `neptune logout`                       | Log out of Neptune                           |
| `neptune init`                         | Initialize a new project (creates AGENTS.md) |
| `neptune deploy`                       | Build and deploy the current project         |
| `neptune deploy -y`                    | Deploy without confirmation prompts          |
| `neptune status`                       | Show current deployment status               |
| `neptune logs`                         | View deployment logs                         |
| `neptune logs --follow`                | Stream logs in real-time                     |
| `neptune wait`                         | Wait for deployment to complete              |
| `neptune list`                         | List all your projects                       |
| `neptune delete`                       | Delete current project                       |
| `neptune delete --project-name <name>` | Delete a specific project                    |
| `neptune lint`                         | Run AI lint on current project               |
| `neptune dockerfile`                   | Get Dockerfile guidance for your project     |
| `neptune schema`                       | Show neptune.json schema                     |

### Resource Management

```bash
# Get info about resource types
neptune resource info Database
neptune resource info StorageBucket
neptune resource info Secret

# Provision resources (before deployment)
neptune resource provision

# Set a secret value
neptune resource secret set MY_SECRET_NAME

# Get database connection info
neptune resource database info my-database

# List files in a bucket
neptune resource bucket list my-bucket

# Download a file from a bucket
neptune resource bucket get my-bucket path/to/file.txt
```

### Generate Commands

```bash
# Generate shell completions
neptune generate completions bash > ~/.bash_completion.d/neptune
neptune generate completions zsh > ~/.zfunc/_neptune

# Generate spec (neptune.json)
neptune generate spec

# Generate/update Agents.md
neptune generate agents
```

### Global Options

```bash
neptune --debug <command>           # Enable debug output
neptune --output json <command>     # JSON output mode
neptune --working-directory /path <command>  # Run in different directory
neptune -v <command>                # Verbose output
```

## Example: Full Deployment Workflow

```bash
# Navigate to your project
cd my-fastapi-app

# Login
neptune login

# Initialize project
neptune init

# Generate neptune.json configuration
neptune generate spec

# Review generated neptune.json
cat neptune.json

# Check Dockerfile guidance (if no Dockerfile exists)
neptune dockerfile

# Optionally run AI lint to check for issues
neptune lint

# Create Dockerfile based on guidance, then deploy
neptune deploy -y

# Wait for deployment
neptune wait

# Check status and get URL
neptune status

# View logs
neptune logs --follow
```

---

# UX 2: CLI + AGENTS.md

This approach uses an `AGENTS.md` file that AI coding assistants (like Cursor, Copilot, Windsurf) can read to understand how to deploy your project to Neptune.

## Quick Start

```bash
neptune login

# Option A: New project — init automatically creates AGENTS.md
neptune init

# Option B: Existing project — generate AGENTS.md
neptune generate agents
```

That's it! The CLI fetches the latest Neptune instructions from the server and creates/updates `AGENTS.md` in your project.

## How It Works

1. **`neptune init`** — When initializing a new project, `AGENTS.md` is automatically created with Neptune deployment instructions
2. **`neptune generate agents`** — For existing projects, this command creates or updates `AGENTS.md`
3. **Versioned content** — The instructions are fetched from Neptune's server and versioned, so running `generate agents` again will update to the latest version if needed

## What Gets Created

The generated `AGENTS.md` contains Neptune-specific instructions that AI assistants can read, including:

-   Deployment workflow steps
-   How to configure `neptune.json`
-   Resource types (Database, StorageBucket, Secret)
-   Dockerfile requirements
-   Available CLI commands

If you already have an `AGENTS.md` file with other content, the Neptune instructions are appended (or the Neptune section is updated if it already exists).

## Usage with AI Assistants

Once `AGENTS.md` exists in your project, ask your AI assistant:

> "Deploy this project to Neptune"

> "Set up Neptune deployment with a PostgreSQL database"

> "Check the Neptune deployment status"

> "Show me the Neptune logs"

The AI will read the `AGENTS.md` file and execute the appropriate CLI commands.

---

# UX 3: CLI + MCP (Model Context Protocol)

MCP provides a direct integration between AI assistants and Neptune, allowing the AI to call Neptune tools directly without needing to execute CLI commands.

## Quick Start

```bash
neptune login
```

### 1. Configure Your AI Assistant

**For Cursor/VS Code**, add to your MCP settings (`.cursor/mcp.json` or settings):

```json
{
    "servers": {
        "neptune": {
            "type": "stdio",
            "command": "neptune",
            "args": ["mcp"]
        }
    }
}
```

**Alternative: HTTP Transport**

Start the MCP server:

```bash
neptune mcp --transport http --port 8001
```

Then configure:

```json
{
    "mcpServers": {
        "neptune": {
            "url": "http://localhost:8001/mcp"
        }
    }
}
```

### 2. Use with AI Assistant

Once configured, simply ask your AI assistant to deploy:

> "Deploy this project to Neptune"

> "Create a neptune.json for this project with a Postgres database"

> "Show me the deployment status"

> "What are the logs from my Neptune deployment?"

The AI assistant will use the MCP tools directly.

## Available MCP Tools

| Tool                           | Description                                                     |
| ------------------------------ | --------------------------------------------------------------- |
| `get_project_schema`           | Get JSON schema for neptune.json                                |
| `add_new_resource`             | Get info about resource types (Database, StorageBucket, Secret) |
| `get_dockerfile_guidance`      | Get Dockerfile example for your project type                    |
| `provision_resources`          | Provision cloud resources from neptune.json                     |
| `deploy_project`               | Build and deploy the application                                |
| `get_deployment_status`        | Check current deployment status                                 |
| `wait_for_deployment`          | Wait for deployment to complete                                 |
| `list_projects`                | List all your projects                                          |
| `delete_project`               | Delete a project and its resources                              |
| `get_logs`                     | Get deployment logs                                             |
| `run_ai_lint`                  | Run AI lint to check for issues                                 |
| `set_secret_value`             | Set a secret value (prompts for input)                          |
| `get_database_connection_info` | Get database connection details                                 |
| `list_bucket_files`            | List files in a storage bucket                                  |
| `get_bucket_object`            | Download an object from a bucket                                |

## MCP Workflow

The AI assistant will typically follow this workflow:

1. **Schema** → `get_project_schema` to understand neptune.json format
2. **Resources** → `add_new_resource` to learn about resource types
3. **Create Config** → Create neptune.json file
4. **Dockerfile** → `get_dockerfile_guidance` if no Dockerfile exists
5. **Lint** → `run_ai_lint` to check for configuration issues (optional)
6. **Provision** → `provision_resources` to create infrastructure
7. **Secrets** → `set_secret_value` for any secrets
8. **Deploy** → `deploy_project` to build and deploy
9. **Monitor** → `get_deployment_status`, `get_logs` to monitor

---

# Testing Scenarios

Please test the following scenarios and report any issues:

## Basic Deployment

1. Create a simple Python/Node.js/Go application
2. Deploy to Neptune using your preferred UX (CLI, AGENTS.md, or MCP)
3. Verify the deployment is accessible via the provided URL
4. Check logs work correctly

## With Database

1. Create an application that uses PostgreSQL
2. Add a Database resource to neptune.json
3. Deploy and verify database connectivity
4. Test `neptune resource database info <name>` returns valid credentials

## With Secrets

1. Create an application that needs environment variables
2. Add Secret resources to neptune.json
3. Set secret values with `neptune resource secret set`
4. Deploy and verify the application can access the secrets

## With Storage Bucket

1. Create an application that uses file storage
2. Add a StorageBucket resource
3. Deploy and verify bucket operations work
4. Test `neptune resource bucket list` and `neptune resource bucket get`

## AI Lint

1. Create a project with intentional issues
2. Run `neptune lint` or MCP `run_ai_lint`
3. Verify lint catches configuration problems
4. Fix issues and re-run lint to confirm they are resolved

## Multiple Projects

1. Deploy multiple projects
2. Use `neptune list` to see all projects
3. Switch between projects with `--working-directory`
4. Delete a project with `neptune delete`

---

# Troubleshooting

## Common Issues

TBD
