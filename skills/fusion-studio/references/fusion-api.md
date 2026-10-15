# Fusion API notes for scripts run over MCP

Verified against Fusion 2705.1 while building the example in this repo. Everything here has been run unless marked **check**.

## Execution

- The script must define `def run(_context):`. Anything printed comes back as the result. An exception comes back as the error with a line number: the line number counts the prepended `fx_lib.py` when you use `--lib`.
- **Never put a line of several KB in a script** (a big JSON blob on one line, say). Fusion then runs nothing and returns an empty `message` with `success: true`, with no error. Format data as a multi-line literal. An empty result from a script that should print is this failure until proven otherwise.
- Results arrive as JSON (`message`, `success`). `fusion_mcp.py` unwraps them.
- Scripts that create or change anything cannot run while a command dialog is open (the user is mid-sketch or mid-extrude). Ask them to close it, or pass `--ro` for inspection.
- `app.documents.add(...)` creates a new document and makes it active. Failed runs leave half-built documents behind, so build in one new document and keep scripts re-runnable by starting each project script with `new_design()` only once.

## Units

The API works in **centimetres**. Anything you pass as a plain float is cm. Pass strings with units (`"27.7 mm"`) or parameter expressions, or divide millimetres by 10. `fx_lib` does this for you.

## Parameters

- Names need 3+ characters with an underscore. `w`, `h`, `t`, `r` fail with "param name is not valid" because they collide with unit symbols.
- Create with `design.userParameters.add(name, ValueInput.createByString("35.7 mm"), "mm", "comment")`. Expressions may refer to other parameters.
- Change a value by setting `.expression`. The whole timeline recomputes. Do this in your parametric test.
- Sketch dimensions: `dim.parameter.expression = "pocket_l"`. Extrude distances: `setDistanceExtent(False, ValueInput.createByString("pocket_d"))`. Both stay linked.

## Components and bodies

- The root component cannot be renamed. Name your own components.
- `occurrences.addNewComponent(Matrix3D.create())` creates a component. Activate it with `occ.activate()` (not `activateComponent`).
- Sketches on a component's planes go through `comp.sketches.add(plane)`. Offset planes come from `constructionPlanes.createInput().setByOffset(base, ValueInput.createByString("back_plate"))`.

## Features that worked

- Extrude: new, join, cut. A profile on an offset plane extruded in the plane's positive normal direction cuts material above it.
- Profile choice: sketch profiles come back unordered. Sort by `areaProperties().area` to pick the one you want (a ring around a hole is larger than the hole).
- Fillet: `createInput()` then `addConstantRadiusEdgeSet(edges, ValueInput, True)`. Pick edges by bounding box (see `edges_where`), never by index: indices change when the timeline changes.
- Health: iterate `design.timeline` and read `healthState` and `errorOrWarningMessage`.
- Export: `exportManager.createC3MFExportOptions(body, path)`, `createSTLExportOptions`, `createSTEPExportOptions(path, rootComponent)`. Use forward slashes in Windows paths inside raw strings.

## Orientation and views

- New designs are Y-up. A part modelled with its height along Z lies on its side in the cube views (`front`, `iso-top-right`). Call `view((x, y, z))` from `fx_lib` before a screenshot: it sets a Z-up orthographic camera, fits the design, and you shoot with `--dir current`.
- Sketch axes: on the `XZ` plane the sketch y axis is **world -Z**, so a rectangle meant for z = 20..50 mm needs y = -50..-20. Read `sketch.xDirection` and `sketch.yDirection` when unsure. A cut extruded from the XZ plane goes one way only: check which side it hit.
- Check a screenshot before assuming which face you are looking at.

## Showcase techniques that worked

- **Exploded view:** keep each part in its own component and set `occurrence.transform2` to a `Matrix3D` with a translation (and a rotation, `setToRotation`, where needed). One `explode_gap` parameter drives the offsets inside the script. Moving occurrences this way adds no timeline items.
- **Revolve:** a circle sketched on `XZ` plus a sketch line as the axis, `revolveFeatures.createInput(profile, axisLine, op)` then `setAngleExtent(False, ValueInput.createByString("360 deg"))`, gives a torus (split ring).
- **Appearances:** `appearance(body, "Acrylic (Clear)")` in `fx_lib` copies a look from the Fusion Appearance Library into the design. `Acrylic (Clear)`, `Chrome`, `Plastic - Glossy (Red)` exist.
- **Transparent PNGs:** `fusion_mcp.py shot out.png --dir current --transparent`.
- **Mesh export:** `exportManager.createOBJExportOptions(rootComponent, path)` works and writes `.obj` plus `.mtl`. This Fusion version (2705.1) has no `createFBXExportOptions`.
- The OBJ is written at the parts' current positions. Export once assembled and once exploded if the video editor needs both.

## Looking things up

`fusion_mcp.py api "<regex>" --filter adsk.fusion` queries the live API docs. Use it for anything not listed here (loft, patterns, joints, sweep) and **check** the signature before use.
