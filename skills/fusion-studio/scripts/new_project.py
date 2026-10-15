#!/usr/bin/env python3
"""Create a fusion-studio project folder.

  python new_project.py "Can holder" --mode print --material PETG [--printer "Bambu Lab H2C"] [--dir projects]

Modes: print | showcase | apparel. Makes <dir>/<slug>/{project.json,build/,shots/,exports/}.
"""
import argparse, json, os, re

MODES = {
    "print": ["3mf per printed part", "step"],
    "showcase": ["png (transparent) per angle", "obj", "step"],
    "apparel": ["png views", "step", "artwork placement notes"],
}

ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
ap.add_argument("name")
ap.add_argument("--mode", required=True, choices=MODES)
ap.add_argument("--material", default="PETG")
ap.add_argument("--printer", default="Bambu Lab H2C")
ap.add_argument("--dir", default=".")
a = ap.parse_args()

slug = re.sub(r"[^a-z0-9]+", "-", a.name.lower()).strip("-")
root = os.path.join(a.dir, slug)
for d in ("build", "shots", "exports"):
    os.makedirs(os.path.join(root, d), exist_ok=True)
proj = {"name": a.name, "mode": a.mode, "deliverables": MODES[a.mode], "assumptions": [], "open_questions": []}
if a.mode == "print":
    proj.update({"material": a.material, "printer": a.printer, "nozzle_mm": 0.4, "first_test_print": ""})
path = os.path.join(root, "project.json")
if os.path.exists(path):
    raise SystemExit(f"{path} exists, not overwriting")
json.dump(proj, open(path, "w"), indent=2)
print("created", root)
