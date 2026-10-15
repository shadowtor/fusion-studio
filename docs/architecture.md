# Architecture

```
agent  --(MCP tools, or fusion_mcp.py over HTTP)-->  Fusion MCP server (127.0.0.1:27182)  -->  Fusion (Python API)
```

The Fusion MCP server exposes four tools: `fusion_mcp_execute` (runs a Python script in the active design, plus document and export actions),
`fusion_mcp_read` (API docs, screenshots, documents, active command), `fusion_mcp_update` (undo, redo) and `fusion_mcp_electronics_read`.
The skill uses the first three. Everything it builds goes through `featureType: "script"`.

| File | Runs | Job |
|---|---|---|
| `scripts/fusion_mcp.py` | on your machine | Calls the server: ping, run a file, screenshot, API lookup, undo |
| `scripts/fx_lib.py` | inside Fusion | Parameters, components, parametric sketches, extrude, fillet, health check, report, export. Prepended with `--lib` |
| `scripts/fx_print.py` | inside Fusion | Print mode: `print_profile`, `print_check`, `fit_coupon`. Prepended after `fx_lib.py` with `--lib` |
| `assets/materials.json` | read by both | Per-filament limits and the slicer profile names. Injected into scripts as `MATERIALS` |
| `scripts/slicer_check.py` | on your machine | Runs OrcaSlicer headless: geometry, slice, forced supports, best orientation |
| `scripts/new_project.py` | on your machine | Creates the project folder and `project.json` for the chosen mode |
| `scripts/check_setup.py` | on your machine | Confirms Python and the server |
| `references/*.md` | read by the agent | Modes, print rules, API notes |

Design choices:

- **Scripts, not one tool per operation.** The server takes whole scripts, so the skill gives the agent a small library and rules instead of wrapping each feature.
- **Parameters before geometry.** Fit problems are found by test prints, so the cheapest fix is one number.
- **A fresh document per design.** The skill never edits a document that was open before it started.
- **The screenshot is the check.** Numbers can all be right while the model is the wrong shape.
