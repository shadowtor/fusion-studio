---
name: fusion-studio
description: Design 3D models together with the user inside Autodesk Fusion through its local MCP server (http://127.0.0.1:27182/mcp). Asks up front whether the project is a 3D-printed part (PLA/PETG/ASA and others, default printer Bambu Lab H2C), a showcase piece that will not be printed (acrylic keychains, exploded views for crowdfunding or video), or a clothing and brand mockup, then builds a parametric model from measurements, checks it, screenshots it and exports it. Use when the user wants to model, tune, review or export anything in Fusion.
---

# fusion-studio

You model in Fusion by sending Python scripts to its MCP server. The user supplies photos, measurements and taste. You build the model, look at it, and fix it.

## 0. Connect (always first)

```bash
python <skill>/scripts/fusion_mcp.py ping
```

Prints the Fusion version and the open document. If the `fusion_mcp_*` MCP tools are loaded use those (`fusion_mcp_execute` with `featureType: "script"`, `fusion_mcp_read` for screenshots and API docs, `fusion_mcp_update` for undo). Otherwise the client does the same from a shell. If `ping` cannot connect, tell the user to start Fusion and enable its MCP server. Do not guess.

Rules that protect the user's work:
- **Never edit a document that was already open.** `new_design()` in `fx_lib.py` opens a fresh one. Read open documents only with `--ro`.
- **Never save, close or overwrite** unless asked. Exports go in the project folder.
- Do not wrap `run()` in try/except. A raised error is how you learn what failed.
- Scripts cannot modify while a command dialog is open. Ask the user to close it, or use `--ro` to inspect.

## 1. Pick the mode (the selector)

Ask with one question, recommending **Print** unless the brief says otherwise. Do not start modelling before this is answered.

| Mode | For | Built as | Finish |
|---|---|---|---|
| **Print** | Parts printed on the user's printer: holders, brackets, enclosures, keychains | Fit tolerances, wall rules, orientation, one component per printed part | 3MF per part + STEP |
| **Showcase** | Items that are shown, not printed: acrylic keychains for a crowdfunding page, exploded views for video | Look first: layered parts, thickness of real materials, exploded layout | PNG on transparent background, OBJ, STEP |
| **Apparel** | Clothing brand mockups: hang tags, labels, trims, buttons, zip pulls, packaging, display pieces | Flat artwork on 3D trims, real material thickness | PNG views, STEP, artwork placement notes |

Details: [references/modes.md](references/modes.md). For Print, also ask the **material** (PLA, PETG, ASA, other) and use the Bambu Lab H2C unless told otherwise: [references/print-rules.md](references/print-rules.md).

Then run `python <skill>/scripts/new_project.py <name> --mode print|showcase|apparel` to create the project folder (`project.json`, `build/`, `shots/`, `exports/`).

## 2. Brief and measurements

Ask for what you cannot invent: the real size of anything the model must fit (a can, a phone, a key), the material, the wall style, and reference photos. Say which numbers are assumed and put them in `project.json` under `assumptions`. A missing dimension becomes a named parameter with an obvious default, never a buried number.

## 3. Parameters first

Everything measurable becomes a user parameter with a comment, in three groups: **measured** (can diameter), **fit** (clearances, wall) and **derived** (expressions built from the others). Names are 3+ characters with an underscore (`can_dia`): single letters such as `w`, `h`, `t` collide with unit names and Fusion refuses them. Sketch dimensions and extrude distances take the parameter expressions, so changing one number changes the model. Read [references/fusion-api.md](references/fusion-api.md) before writing the first script.

## 4. Build in small scripts

Prepend the helper library with `--lib`:

```bash
python <skill>/scripts/fusion_mcp.py run build/01_body.py --lib
python <skill>/scripts/fusion_mcp.py shot shots/01.png --dir iso-top-right
```

`fx_lib.py` gives you `new_design, param, component, sketch, rect, circle, extrude, box, fillet, chamfer, edges_where, appearance, view, health, report, export`. One component per physical part, named `<Part> - PRINT` or `- SHOWCASE`. Fillets go last. **Look at every screenshot** before moving on. If the picture and the numbers disagree, trust the picture and find the bug.

Unknown API? `fusion_mcp.py api "ExtrudeFeatures" --filter adsk.fusion` returns the live docs. Prefer that to memory.

## 5. Verify before saying done

1. `health()` reports 0 problems.
2. **Parametric test:** change the main measured parameter, check `health()` and `report()` again, set it back. A model that breaks here is not finished.
3. Screenshots from at least iso, front and one section or underside view, read by you.
4. Print mode: `report()` fits the bed, wall and bridge checks from `print-rules.md`, orientation stated, supports stated.
5. Say what is **not** proven. A model that looks right has not been test printed. Name the first test print and which parameter to tune after it.

## 6. Export and hand over

Print: `export(body, path, "3mf")` for each part, plus `step`. Showcase: transparent PNG per angle (`shot` uses a transparent background when asked), OBJ for video tools. Apparel: PNG views and STEP. Then give the user: files, parameter list, assumptions, the first test to run.

## What this skill does not do

- It does not slice, send to the printer or choose slicer settings beyond what `print-rules.md` states as starting points.
- It does not replace a test print. Clearances are starting values for a 0.4 mm nozzle, not guarantees.
- It cannot see the user's photos unless they share them. Ask for dimensions rather than estimating from a picture.
- It does not model fabric. Apparel mode covers trims, labels, tags, hardware and packaging.
