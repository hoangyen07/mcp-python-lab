# MCP Client Lab

A minimal Model Context Protocol (MCP) client and server in Python. The client launches the server as a subprocess and talks to it over STDIO, so you can list and call tools, read resources and fetch prompts from an interactive prompt.

## Project Structure

| File | Purpose |
|---|---|
| `mcp_server.py` | FastMCP server with `echo` and `write_file` tools, a `file://resources/{filename}` resource and a `review_file` prompt |
| `mcp_client.py` | Interactive client built on the official `mcp` SDK |
| `resources/` | Files the server exposes as resources |
| `output/` | Where `write_file` saves files (created on first use, ignored by git) |

## Installation

Requires Python 3.13. From the project root:

```bash
python3 -m venv .venv
.venv/bin/pip install -r requirements.txt
```

`requirements.txt` pins `fastmcp==2.12.5`, `mcp==1.16.0` and `pydantic==2.11.10`. Keep these versions: `mcp` 1.16.0 fails to import with `pydantic` 2.12 or newer.

## Usage

Run the client and pass it the server script:

```bash
.venv/bin/python mcp_client.py mcp_server.py
```

Use the venv's Python. The client starts the server with the same interpreter that runs the client, so the server needs the same packages.

Available commands:

| Command | What it does |
|---|---|
| `tools` | List the server's tools |
| `call` | Call a tool, e.g. `echo` with `{"text": "hello"}` |
| `resources` | List resource templates |
| `read` | Read a resource, e.g. `file://resources/README.md` |
| `prompts` | List prompts and their arguments |
| `prompt` | Get a prompt, e.g. `review_file` with `{"filename": "README.md"}` |
| `quit` | Exit |

## Understanding the Client Flow

### Connection Flow

```text
1. Launch client with server script path
   ↓
2. Create StdioServerParameters
   ↓
3. Launch server as subprocess via stdio_client
   ↓
4. Create ClientSession with read/write streams
   ↓
5. Call session.initialize() (MCP handshake)
   ↓
6. Ready for operations
```

### Example: Resource Reading Flow

```text
User: types "read"
   ↓
User: enters "file://resources/README.md"
   ↓
Client: calls session.read_resource(uri)
   ↓
[JSON-RPC request sent via stdin]
   ↓
Server: receives request with URI "file://resources/README.md"
   ↓
Server: matches URI to template pattern "file://resources/{filename}"
   ↓
Server: extracts parameter: filename = "README.md"
   ↓
Server: calls read_resource_file("README.md")
   ↓
Server: function reads file and returns content
   ↓
[JSON-RPC response sent via stdout]
   ↓
Client: receives result object
   ↓
Client: displays result.contents[0].text
```

If the file does not exist, `read_resource_file` raises `FileNotFoundError`. The client receives an MCP error instead of content and prints it.

### Key Components

- **`StdioServerParameters`**: defines how to launch the server subprocess.
- **`stdio_client`**: creates the STDIO transport and returns `(read_stream, write_stream)`.
- **`ClientSession`**: manages the MCP protocol, handling JSON-RPC, message IDs and protocol negotiation.
- **`AsyncExitStack`**: ensures proper cleanup by closing the streams and terminating the subprocess.
- **`FastMCP`**: simplifies server creation with decorators and automatic schema generation.
