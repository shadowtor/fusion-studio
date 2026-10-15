# Monster can holder

Mode: **Print**. Material: PETG. Printer: Bambu Lab H2C.

A free-standing cup for a tall 500 ml can: a 3.2 mm base, a 2.4 mm round wall that grips the lower 55 mm of the can, and a finger notch in the front wall so the can lifts out. It prints upright on its base with no supports and no bridges. A 0.6 mm chamfer on the base edge stops elephant foot and a 0.8 mm fillet softens the rim.

| File | What it is |
|---|---|
| `build.py` | The whole model as one script: `python skills/fusion-studio/scripts/fusion_mcp.py run examples/monster-can-holder/build.py --lib` |
| `can-holder.3mf`, `can-holder.step` | Exports |
| `iso.png`, `iso-transparent.png` | Screenshots from Fusion, the second with a transparent background |

Check results from the live build: 11 timeline features, 0 problems, 72 x 72 x 58.2 mm, 39.2 cm3, fits the bed. Changing `can_dia` from 66 to 70 mm and back kept 0 problems and moved the outside diameter from 72 to 76 mm and back.

**Material check:** `print_profile("PETG")` loads the PETG limits and `print_check("PETG")` reports 0 warnings. The first version warned about a 0.6 mm sliver where the planar finger notch cuts the round wall. Filleting the notch corners (`notch_r`) fixed it.

**Slicer check** (`slicer_check.py`, OrcaSlicer 2.5.0-dev, Bambu Lab H2C, 0.20 mm Standard, Bambu PETG Basic, Textured PEI): watertight, 1 h 32 min, 36.7 g, 291 layers. With tree supports forced on it still generates none, and OrcaSlicer's own best orientation is the one exported.

**Not proven:** fit. The 66 mm can diameter is an assumption for a 500 ml can, not a measurement of yours, and nothing has been printed. Measure the widest point of your can, set `can_dia`, print once, then tune `fit_xy` (0.6 mm per side).
