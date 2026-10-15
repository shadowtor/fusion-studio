#!/usr/bin/env python3
"""Tiny stdlib client for the local Autodesk Fusion MCP server (default http://127.0.0.1:27182/mcp).

Use it from a shell when the MCP tools are not loaded in the agent, or to run files instead of pasting scripts.

  python fusion_mcp.py ping                       # server + Fusion version + active document
  python fusion_mcp.py run script.py [--lib]      # run a Python file inside Fusion (--lib prepends fx_lib.py)
  python fusion_mcp.py eval "print(1+1)"          # run an inline snippet
  python fusion_mcp.py shot out.png [--dir iso-top-right] [--w 1600 --h 1000] [--transparent]
  python fusion_mcp.py api "ExtrudeFeatures" [--filter adsk.fusion]   # API docs lookup
  python fusion_mcp.py undo | redo
  python fusion_mcp.py tools                      # list the server's tools

Env: FUSION_MCP_URL overrides the endpoint. Exit code is 1 when Fusion reports an error.
"""
import argparse, base64, json, os, pprint, sys, urllib.request

URL = os.environ.get("FUSION_MCP_URL", "http://127.0.0.1:27182/mcp")
HERE = os.path.dirname(os.path.abspath(__file__))
_sid = None


def rpc(method, params=None, _id=1, notify=False):
    global _sid
    body = {"jsonrpc": "2.0", "method": method}
    if params is not None:
        body["params"] = params
    if not notify:
        body["id"] = _id
    h = {"Content-Type": "application/json", "Accept": "application/json"}
    if _sid:
        h["MCP-Session-Id"] = _sid
    req = urllib.request.Request(URL, json.dumps(body).encode(), h)
    with urllib.request.urlopen(req, timeout=300) as r:
        _sid = r.headers.get("MCP-Session-Id") or _sid
        raw = r.read().decode("utf-8", "replace")
    return json.loads(raw) if raw.strip() else {}


def connect():
    try:
        rpc("initialize", {"protocolVersion": "2025-03-26", "capabilities": {},
                           "clientInfo": {"name": "fusion-studio", "version": "1"}})
    except OSError as e:
        sys.exit(f"Cannot reach {URL} ({e}). Start Fusion, then enable the MCP server (Preferences > API / MCP).")
    rpc("notifications/initialized", notify=True)


def call(tool, args):
    r = rpc("tools/call", {"name": tool, "arguments": args}, 2)
    if "error" in r:
        sys.exit("RPC error: " + json.dumps(r["error"]))
    res = r["result"]
    return res.get("isError", False), res.get("content", [])


def text_of(content):
    return "\n".join(c.get("text", "") for c in content if c.get("type") == "text")


def run_script(src, read_only=False):
    obj = {"script": src}
    if read_only:
        obj["readOnly"] = True
    err, content = call("fusion_mcp_execute", {"featureType": "script", "object": obj})
    return err, text_of(content)


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("cmd", choices=["ping", "run", "eval", "shot", "api", "undo", "redo", "tools"])
    ap.add_argument("arg", nargs="?")
    ap.add_argument("--lib", action="store_true", help="prepend fx_lib.py to the script")
    ap.add_argument("--ro", action="store_true", help="read-only script (allowed while a dialog is open)")
    ap.add_argument("--dir", default="iso-top-right")
    ap.add_argument("--w", type=int, default=1600)
    ap.add_argument("--h", type=int, default=1000)
    ap.add_argument("--filter")
    ap.add_argument("--transparent", action="store_true", help="shot: transparent background (showcase cut-outs)")
    a = ap.parse_args()
    connect()
    if a.cmd == "tools":
        for t in rpc("tools/list", _id=3)["result"]["tools"]:
            print(t["name"])
    elif a.cmd == "ping":
        err, out = run_script(
            "import adsk.core\n"
            "def run(_c):\n"
            "    app = adsk.core.Application.get()\n"
            "    d = app.activeDocument\n"
            "    print('Fusion', app.version, '| document:', d.name if d else None)\n", True)
        print(out); sys.exit(1 if err else 0)
    elif a.cmd in ("run", "eval"):
        src = open(a.arg, encoding="utf-8").read() if a.cmd == "run" else a.arg
        if a.cmd == "eval" and "def run" not in src:
            src = "import adsk.core, adsk.fusion\ndef run(_c):\n" + "\n".join("    " + l for l in src.splitlines())
        if a.lib:
            # multi-line literal on purpose: Fusion silently runs nothing when a script has a line of several KB
            mats = pprint.pformat(json.load(open(os.path.join(HERE, "..", "assets", "materials.json"), encoding="utf-8")), width=100)
            src = ("MATERIALS = " + mats + "\n"
                   + open(os.path.join(HERE, "fx_lib.py"), encoding="utf-8").read() + "\n\n"
                   + open(os.path.join(HERE, "fx_print.py"), encoding="utf-8").read() + "\n\n" + src)
        err, out = run_script(src, a.ro)
        print(out); sys.exit(1 if err else 0)
    elif a.cmd == "shot":
        err, content = call("fusion_mcp_read", {"queryType": "screenshot", "direction": a.dir, "width": a.w,
                                                 "height": a.h, "transparentBackground": a.transparent})
        for c in content:
            data = c.get("data") or c.get("base64Data")
            if not data and c.get("type") == "text":
                try:
                    data = json.loads(c["text"]).get("base64Data")
                except ValueError:
                    pass
            if data:
                open(a.arg, "wb").write(base64.b64decode(data)); print("wrote", a.arg); return
        print(text_of(content)[:500]); sys.exit(1)
    elif a.cmd == "api":
        args = {"queryType": "apiDocumentation", "searchPattern": a.arg, "apiCategory": "all"}
        if a.filter:
            args["filter"] = a.filter
        print(text_of(call("fusion_mcp_read", args)[1])[:6000])
    else:
        print(text_of(call("fusion_mcp_update", {"featureType": a.cmd})[1]))


if __name__ == "__main__":
    main()
