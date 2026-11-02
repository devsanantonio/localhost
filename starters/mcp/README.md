# MCP: San Antonio's open data, as tools for your agent

The [Model Context Protocol](https://modelcontextprotocol.io) lets a coding agent call tools. This is a small MCP server, one standard-library Python file like every starter here, that gives your agent four:

| Tool | What it does |
|---|---|
| `find_layers` | Search every publisher's public layers for a word |
| `describe_layer` | Fields, row count, last change, sample rows and the credit line for any layer |
| `list_starters` | The starters in this repo, one line each |
| `run_starter` | Run one and get its answer as JSON, e.g. `311-by-district` with `["--district", "5"]` |

It runs on your machine, with your agent, on your own model account. Nothing is hosted.

## Add it

**Claude Code**

```sh
claude mcp add localhost-210 -- python3 /path/to/localhost/starters/mcp/main.py
```

**Claude Desktop, Cursor and others** that take a JSON config:

```json
{
  "mcpServers": {
    "localhost-210": {
      "command": "python3",
      "args": ["/path/to/localhost/starters/mcp/main.py"]
    }
  }
}
```

Then ask: *"Which council district calls 311 most about potholes?"*, *"What's the aquifer at today?"*, *"Find layers about bike lanes and tell me what's in the newest one."*

## Rules travel with it

The server hands your agent the same rules as [AGENTS.md](../../AGENTS.md) when it connects: credit every source, VIA's data only for helping riders, no affiliation claims, no neighborhood crime rankings, leave survey layers alone, and the flood starters are not warnings. If a request would break one, the agent is told to say so and suggest something else.

## How it works

MCP over stdio is JSON-RPC, one message per line. The server answers `initialize`, `tools/list` and `tools/call`. `run_starter` runs `python3 starters/<name>/main.py <args> --json` as a list of arguments, never through a shell, and only for starters that exist in this folder.

Try it by hand:

```sh
printf '%s\n' '{"jsonrpc":"2.0","id":1,"method":"tools/call","params":{"name":"list_starters","arguments":{}}}' | python3 main.py
```

## Source

The data comes from each starter's own source, and each answer carries its credit line. The full list of terms is in [ATTRIBUTION.md](../../ATTRIBUTION.md).
