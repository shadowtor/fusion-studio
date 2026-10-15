#!/usr/bin/env python3
"""Check that Python, the Fusion MCP server and a design document are reachable. Exit 1 on FAIL."""
import json, os, sys, urllib.request

URL = os.environ.get("FUSION_MCP_URL", "http://127.0.0.1:27182/mcp")
bad = 0
print("OK   Python", sys.version.split()[0]) if sys.version_info >= (3, 8) else print("FAIL Python 3.8+ needed")
try:
    req = urllib.request.Request(URL, json.dumps({"jsonrpc": "2.0", "id": 1, "method": "initialize", "params": {
        "protocolVersion": "2025-03-26", "capabilities": {}, "clientInfo": {"name": "check", "version": "1"}}}).encode(),
        {"Content-Type": "application/json", "Accept": "application/json"})
    r = json.load(urllib.request.urlopen(req, timeout=5))
    print("OK  ", "MCP server at", URL, "-", r["result"]["serverInfo"]["name"])
except Exception as e:
    print("FAIL cannot reach", URL, "-", e, "\n     Start Fusion and enable its MCP server, or set FUSION_MCP_URL.")
    bad = 1
sys.exit(bad)
