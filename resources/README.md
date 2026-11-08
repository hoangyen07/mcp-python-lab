# MCP Client Lab

This lab teaches you how to build Model Context Protocol (MCP) clients with Python.

## What You'll Learn
- STDIO transport connections
- Tool invocation patterns
- Resource reading via URIs
- Prompt template usage

## Installation
Requires Python 3.13. Run these commands from the project root:

```bash
python3 -m venv .venv
.venv/bin/pip install -r requirements.txt
```

`requirements.txt` pins `fastmcp==2.12.5`, `mcp==1.16.0` and `pydantic==2.11.10`.
Keep these versions: `mcp` 1.16.0 fails to import with `pydantic` 2.12 or newer.

## Running the Server
```bash
.venv/bin/python mcp_server.py
```

The server uses STDIO, so it waits for an MCP client to connect and looks idle in a terminal.

## Getting Started
Follow the lab instructions to build your first MCP client!