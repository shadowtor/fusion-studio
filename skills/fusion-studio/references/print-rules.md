# Print rules (starting points, not guarantees)

These are conservative defaults for a 0.4 mm nozzle and 0.2 mm layers. Every value is a **parameter** in the model so a test print can correct it. Where a number depends on the filament brand or the printer's calibration, it says so.

## Printer: Bambu Lab H2C (default)

- Build volume reported as 305 x 320 x 325 mm for single-nozzle printing, 300 x 320 x 325 mm dual-nozzle, 330 x 320 x 325 mm total across both nozzles. Sources disagree by a few millimetres on the left-nozzle height, so check Bambu's spec page before printing anything near the edge. `fx_lib.report()` checks bodies against 305 x 320 x 325.
- Hotend up to 350 C, heated bed up to 120 C, active chamber heating to 65 C, hardened-steel nozzles in 0.2, 0.4, 0.6 and 0.8 mm.
- Multi-material through nozzle swapping (Vortek). A single-colour part does not care.
- Source: Bambu Lab's [H2C announcement](https://blog.bambulab.com/bambu-lab-h2c-where-multi-material-vortek-system-meets-engineering-precision) and independent reviews. Re-check if the user has a different firmware or bed plate.

## Materials

| | PLA | PETG | ASA |
|---|---|---|---|
| Good for | Display, prototypes, rigid parts indoors | Everyday parts, keychains, clips, some flex | Outdoor, car interior, UV exposure |
| Watch for | Softens in a hot car, brittle on thin snap parts | Stringing, creeps under constant load, sticks hard to smooth plates | Warps without an enclosure, fumes: ventilate |
| Snap fits and living hinges | Poor | Good | Good |
| Fit allowance | Tightest | Add a little over PLA | Add a little over PETG |

State the material in `project.json`. Clearances below are for PETG. Tighten for PLA by about 0.05 mm, loosen for ASA by about 0.05 mm, then confirm with a test print. Shrinkage differs by brand and enclosure temperature, so there is no universal scale factor: never apply one without a test.

## Fits (per side, 0.4 mm nozzle)

| Fit | Clearance |
|---|---|
| Press fit (parts that should not come apart) | 0.05 to 0.1 mm |
| Snug sliding (tile in a pocket, lid on a box) | 0.2 to 0.3 mm |
| Free sliding or rotating (hinge pin, dial) | 0.3 to 0.4 mm |
| Loose, tolerant of warp (large parts) | 0.4 to 0.5 mm |

Small round holes print undersized. Add 0.1 to 0.2 mm to holes under about 6 mm and to magnet pockets, then test.

## Geometry

- Wall thickness: at least 3 perimeters (1.2 mm). Use multiples of 0.4 so the slicer does not leave gaps. 2.4 mm gives 6 perimeters.
- Minimum feature: 0.8 mm for anything that must survive handling. 0.4 mm details exist but break.
- Overhangs: 45 degrees or steeper print clean. A small shelf under 2 mm wide is fine. Bridges: keep under 20 mm where you can, and say so when you do not.
- Corners: radius 1 mm or more on outer vertical corners. Sharp interior corners crack, add a 0.5 mm fillet.
- First layer: a 0.4 mm chamfer on bed-contact edges stops elephant foot.
- Holes for keyrings: 4 mm minimum, 5 mm comfortable, with at least 3 mm of material around.
- Tensile loads go across layer lines, never along: a keyring eye should lie flat on the bed so the layers run around the hole.
- Text and logos: emboss or deboss at least 0.6 mm deep and 1 mm stroke.

## Orientation checklist (state it in the handover)

1. Which face is on the bed.
2. Where supports are needed (aim for none).
3. Which direction layers run relative to the main load.
4. Which bridges exist and how long.
5. What surface finish the visible face gets (bed side is smoother with a smooth plate, the top is layered).

## Hardware

Magnets, screws and heat-set inserts are measured and parameterised like anything else. Ask the user for the real diameter and thickness, add 0.1 to 0.2 mm radial clearance for glue-in magnets, and say which magnet polarity the design assumes. Inserts need the maker's hole size: ask for the datasheet value.
