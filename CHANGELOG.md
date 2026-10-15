# Changelog

## 1.1.0

- Print mode designs for the filament: `assets/materials.json` (ten filaments), `print_profile()`, `print_check()` and `fit_coupon()` in `fx_print.py`. Fits are diametral. Reference: `materials.md`.
- `slicer_check.py` checks a model in OrcaSlicer from the command line (watertight, time, filament, support need, best orientation). `slicer.md` also covers the GUI and the optional orcaslicer-mcp route.
- Fix: the client no longer sends single lines of several KB, which made Fusion run nothing and return an empty result.
- Can holder example: notch corners filleted after `print_check` found a knife edge.

## 1.0.0

- Skill `fusion-studio`: mode selector (Print, Showcase, Apparel), parameters-first workflow, verification steps.
- `fusion_mcp.py` stdlib client for the Fusion MCP server, `fx_lib.py` helpers that run inside Fusion, `new_project.py`, `check_setup.py`.
- References: modes, print rules (Bambu Lab H2C defaults, PLA, PETG, ASA), Fusion API notes.
- Examples built in a live Fusion session: a Monster can holder (Print mode, 3MF and STEP) and an acrylic keychain with an exploded view (Showcase mode, transparent PNGs, OBJ and STEP).
- Website, social card, installer, packager, smoke test, CI.
