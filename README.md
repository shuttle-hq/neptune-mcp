# neptune-cli-python

## Prerequisites

* Python 3.13 or later
* [uv][uv] 0.9.x

## Getting Started

Make sure you are also running the `neptune-aws-platform` locally (by default this will look for it at
`localhost:8000`).

```
git clone https://github.com/shuttle-hq/neptune-cli-python.git
cd neptune-cli-python
git submodule update --init --recursive

# Install the CLI
uv tool install -e .
```

For example, for Cursor, you can go to Cursor Settings -> Tools & MCP -> New MCP Server:

```json
{
  "mcpServers": {
    "neptune": {
      "type": "stdio",
      "command": "neptune",
      "args": ["mcp"]
    }
  }
}
```

Alternatively, you can run the MCP server with HTTP transport and let your local IDE connect to it:

```shell
uv run neptune mcp --transport=http
```

By default, the server will be available on http://0.0.0.0:8001/mcp, and the MCP configuration for Cursor will be:

```json
{
  "mcpServers": {
    "neptune": {
      "url": "http://0.0.0.0:8001/mcp"
    }
  }
}
```

[uv]: https://docs.astral.sh/uv/
