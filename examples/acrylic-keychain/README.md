# Acrylic keychain

Mode: **Showcase**. Not printed: this is the picture for a crowdfunding page and the starting point for an exploded-view clip.

Four parts at real material thickness: two 3 mm clear acrylic layers, a 0.2 mm printed art sheet between them, and a chrome split ring through the hole. One parameter, `explode_gap`, spreads the parts along Z (14 mm in `build.py`, 0 for the assembled view).

| File | What it is |
|---|---|
| `build.py` | Builds the parts and leaves them exploded: `python skills/fusion-studio/scripts/fusion_mcp.py run examples/acrylic-keychain/build.py --lib` |
| `assembled.py` | Moves the parts back together and frames the view (run after `build.py`, same `--lib`) |
| `exploded.png`, `assembled.png` | Transparent-background screenshots |
| `keychain.obj`, `keychain.mtl`, `keychain.step` | Exports, written in the assembled position |

Check results from the live build: 17 timeline features, 0 problems. Moving parts with `occurrence.transform2` adds no timeline items.

**Not covered:** the art sheet is a flat colour. Real artwork goes on as a decal or texture, or you composite it over the PNG. Fusion's API in this version has no FBX export, so a video editor gets OBJ. Export the OBJ again with the parts exploded if you need that pose as a mesh.
