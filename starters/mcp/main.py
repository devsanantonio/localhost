"""San Antonio's open data as tools for your own coding agent: a small MCP server.

The Model Context Protocol lets an agent like Claude Code, Claude Desktop or
Cursor call tools. This server gives it four: search every publisher's layers,
look inside any layer, list the starters in this repo, and run one. It speaks
MCP over stdin and stdout, in the standard library only, like every starter
here. Your agent runs it on your machine, on your own model account.

    claude mcp add localhost-210 -- python3 /path/to/localhost/starters/mcp/main.py

Each dataset belongs to its publisher. The server hands your agent the same
rules as AGENTS.md: credit every source, follow VIA's license, no neighborhood
crime rankings, leave survey layers alone.
"""
import importlib.util
import json
import os
import re
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
STARTERS = os.path.dirname(HERE)
PROTOCOL = "2025-06-18"

INSTRUCTIONS = """Tools for San Antonio's open data, from devsanantonio/localhost. Rules for anything you build or say with it:
1. Credit every source with the credit line each tool returns (City: "Data: City of San Antonio Open Data, CC BY 4.0").
2. VIA's data is only for helping transit riders. Never use VIA's logos or describe a project as VIA's or made with VIA.
3. Never claim affiliation: "built on City of San Antonio open data", never "with the City" or "in partnership with".
4. No rankings or scores of neighborhoods from police (SAPD) data.
5. Leave survey and feedback layers alone; they can hold people's names and addresses.
6. The 1897 Residence and Employment layers are about real people: use them for history in aggregate only.
7. creek-levels and low-water-crossings are not flood warnings. Point people to weather.gov/ewx and BexarFlood.org.
If a request would break one of these, say which rule and suggest an alternative."""


def load_peek():
    spec = importlib.util.spec_from_file_location("peek", os.path.join(STARTERS, "peek", "main.py"))
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def starters():
    """Every starter in the repo, with the first line of its docstring."""
    out = {}
    for name in sorted(os.listdir(STARTERS)):
        path = os.path.join(STARTERS, name, "main.py")
        if name == "mcp" or not os.path.isfile(path):
            continue
        with open(path) as f:
            doc = re.search(r'"""(.*?)\n', f.read())
        out[name] = doc.group(1).strip() if doc else ""
    return out


def run_starter(name, args):
    if name not in starters():
        raise ValueError(f"No starter named {name!r}. list_starters shows them all.")
    if not isinstance(args, list) or len(args) > 12 or not all(isinstance(a, str) and len(a) < 200 for a in args):
        raise ValueError("args must be a short list of strings, like [\"--district\", \"5\"].")
    # A list, never a shell string, so an argument can't run anything else.
    done = subprocess.run([sys.executable, os.path.join(STARTERS, name, "main.py"), *args, "--json"],
                          capture_output=True, text=True, timeout=180, cwd=os.path.join(STARTERS, name))
    if done.returncode != 0:
        raise RuntimeError((done.stderr or done.stdout).strip()[-1500:] or f"{name} exited with {done.returncode}")
    return json.loads(done.stdout)


TOOLS = [
    {"name": "find_layers",
     "description": "Search every San Antonio publisher's public map layers (City, Bexar County, River Authority, "
                    "Alamo Area MPO, Opportunity Home, Edwards Aquifer Authority) for a word. Newest first.",
     "inputSchema": {"type": "object", "properties": {"word": {"type": "string", "description": "e.g. flood, permits, parks"}},
                     "required": ["word"], "additionalProperties": False}},
    {"name": "describe_layer",
     "description": "Look inside one layer or service by its address: row count, last change, fields, sample rows "
                    "and the publisher's credit line. A service address lists the layers inside it.",
     "inputSchema": {"type": "object", "properties": {
         "address": {"type": "string", "description": "…/FeatureServer/0 or …/MapServer/0, or a service address"},
         "rows": {"type": "integer", "minimum": 1, "maximum": 25, "default": 5}},
         "required": ["address"], "additionalProperties": False}},
    {"name": "list_starters",
     "description": "List the repo's starters: small programs that each answer one kind of question about San Antonio "
                    "(311 by district, permits near a point, next bus, creek levels, the aquifer, funded road projects…).",
     "inputSchema": {"type": "object", "properties": {}, "additionalProperties": False}},
    {"name": "run_starter",
     "description": "Run a starter and get its answer as JSON. args are the starter's own options, without --json, e.g. "
                    "[\"--district\", \"5\"] for 311-by-district or [\"--near\", \"29.4241,-98.4936\"].",
     "inputSchema": {"type": "object", "properties": {
         "name": {"type": "string"}, "args": {"type": "array", "items": {"type": "string"}, "default": []}},
         "required": ["name"], "additionalProperties": False}},
]


def call(name, arguments):
    if name == "find_layers":
        return load_peek().find(arguments["word"])
    if name == "describe_layer":
        peek = load_peek()
        url = arguments["address"].split("?")[0].rstrip("/")
        info = peek.get(url)
        return peek.layer(url, info, int(arguments.get("rows", 5))) if "fields" in info else peek.service(url, info)
    if name == "list_starters":
        return [{"name": n, "about": about} for n, about in starters().items()]
    if name == "run_starter":
        return run_starter(arguments["name"], arguments.get("args", []))
    raise ValueError(f"Unknown tool {name!r}")


def handle(msg):
    method, params = msg.get("method"), msg.get("params") or {}
    if method == "initialize":
        return {"protocolVersion": params.get("protocolVersion", PROTOCOL), "capabilities": {"tools": {}},
                "serverInfo": {"name": "localhost-210", "version": "1.0.0"}, "instructions": INSTRUCTIONS}
    if method == "ping":
        return {}
    if method == "tools/list":
        return {"tools": TOOLS}
    if method == "tools/call":
        try:
            result = call(params.get("name"), params.get("arguments") or {})
            return {"content": [{"type": "text", "text": json.dumps(result, indent=2)}], "isError": False}
        except SystemExit as e:   # peek reports a service's own error this way
            return {"content": [{"type": "text", "text": str(e)}], "isError": True}
        except Exception as e:
            return {"content": [{"type": "text", "text": f"{type(e).__name__}: {e}"}], "isError": True}
    raise LookupError(method)


if __name__ == "__main__":
    for line in sys.stdin:
        if not line.strip():
            continue
        msg = json.loads(line)
        if "id" not in msg:        # a notification, such as notifications/initialized: no reply
            continue
        try:
            reply = {"jsonrpc": "2.0", "id": msg["id"], "result": handle(msg)}
        except LookupError:
            reply = {"jsonrpc": "2.0", "id": msg["id"], "error": {"code": -32601, "message": f"Method not found: {msg.get('method')}"}}
        sys.stdout.write(json.dumps(reply) + "\n")
        sys.stdout.flush()
