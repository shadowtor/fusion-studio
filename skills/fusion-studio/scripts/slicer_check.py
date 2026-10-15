#!/usr/bin/env python3
"""Check a model in OrcaSlicer from the command line (no MCP server needed).

  python slicer_check.py part.3mf --material PETG
  python slicer_check.py part.3mf --material ASA --nozzle 0.4 --process "0.20mm Standard"
  python slicer_check.py part.3mf --material PETG --json

It runs the slicer headless three times on the Bambu Lab H2C profiles and reports:
  1. geometry   : size, volume, manifold (watertight) or not
  2. as exported: print time, filament, layers, any support the file already asks for
  3. supports on: the same slice with tree supports forced on. If no support extrusion appears, the orientation needs none.
  4. best orient: the slicer's own pick (--orient). The tool reports whether your orientation matches it.

Finds OrcaSlicer (ORCA_SLICER env var, PATH, Program Files, /Applications) and the Bambu Lab profiles in the Bambu Studio or
OrcaSlicer user folder (ORCA_PROFILES env var or --profiles). Writes G-code only into --outdir (default: next to the 3MF, in
'slicer-check/'). It never edits your presets.

Verified on Windows with OrcaSlicer 2.5.0-dev and the Bambu Studio H2C profiles. Other OS paths are best effort: check.
"""
import argparse, json, os, re, shutil, subprocess, sys, tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
MATS = json.load(open(os.path.join(HERE, "..", "assets", "materials.json"), encoding="utf-8"))["materials"]


def find_exe(arg):
    for c in [arg, os.environ.get("ORCA_SLICER"), shutil.which("orca-slicer"), shutil.which("OrcaSlicer"),
              r"C:\Program Files\OrcaSlicer\orca-slicer.exe", "/Applications/OrcaSlicer.app/Contents/MacOS/OrcaSlicer"]:
        if c and os.path.exists(c):
            return c
    sys.exit("OrcaSlicer not found. Install it, or set ORCA_SLICER to the executable (or pass --exe).")


def find_profiles(arg):
    home = os.path.expanduser("~")
    for c in [arg, os.environ.get("ORCA_PROFILES"),
              os.path.join(os.environ.get("APPDATA", ""), "BambuStudio", "system", "BBL"),
              os.path.join(os.environ.get("APPDATA", ""), "OrcaSlicer", "system", "BBL"),
              os.path.join(home, "Library", "Application Support", "BambuStudio", "system", "BBL"),
              os.path.join(home, "Library", "Application Support", "OrcaSlicer", "system", "BBL"),
              os.path.join(home, ".config", "BambuStudio", "system", "BBL")]:
        if c and os.path.isdir(os.path.join(c, "machine")):
            return c.replace("\\", "/")
    sys.exit("Bambu Lab profiles not found. Open Bambu Studio once so it downloads them, or pass --profiles <.../system/BBL>.")


def flatten(pdir, name):
    """Resolve a process preset's 'inherits' chain into one standalone preset (the CLI cannot resolve inherits for user files)."""
    d = json.load(open(os.path.join(pdir, name + ".json"), encoding="utf-8"))
    base = flatten(pdir, d["inherits"]) if d.get("inherits") else {}
    base.update(d)
    return base


def run(cmd, timeout=600):
    r = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout)
    return r.returncode, (r.stdout or "") + (r.stderr or "")


def gcode_stats(path):
    t = open(path, encoding="utf-8", errors="replace").read()
    g = lambda pat: (re.search(pat, t) or [None, None])[1]
    feats = {}
    for f in re.findall(r"^; FEATURE: (.+)$", t, re.M):
        feats[f.strip()] = feats.get(f.strip(), 0) + 1
    return {"time": g(r"total estimated time: ([^\n]+)"), "layers": g(r"total layer number: (\d+)"),
            "filament_g": g(r"filament used \[g\] = ([\d.]+)"), "filament_cm3": g(r"filament used \[cm3\] = ([\d.]+)"),
            "features": feats, "support_lines": sum(v for k, v in feats.items() if "upport" in k)}


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("model")
    ap.add_argument("--material", default="PETG", choices=list(MATS))
    ap.add_argument("--nozzle", default="0.4")
    ap.add_argument("--process", default="0.20mm Standard")
    ap.add_argument("--printer", default="Bambu Lab H2C", help="profile family, e.g. 'Bambu Lab H2C', 'Bambu Lab X1 Carbon'")
    ap.add_argument("--exe")
    ap.add_argument("--profiles")
    ap.add_argument("--outdir")
    ap.add_argument("--json", action="store_true")
    a = ap.parse_args()

    exe, prof = find_exe(a.exe), find_profiles(a.profiles)
    model = os.path.abspath(a.model)
    out = os.path.abspath(a.outdir or os.path.join(os.path.dirname(model), "slicer-check"))
    os.makedirs(out, exist_ok=True)
    short = a.printer.replace("Bambu Lab ", "")
    machine = "%s/machine/%s %s nozzle.json" % (prof, a.printer, a.nozzle)
    proc_name = "%s @BBL %s" % (a.process, short)
    fil = "%s/filament/%s @BBL %s.json" % (prof, MATS[a.material]["slicer"]["bbl_filament"], short)
    for f in (machine, fil, "%s/process/%s.json" % (prof, proc_name)):
        if not os.path.exists(f):
            sys.exit("Profile not found: %s" % f)
    bed = MATS[a.material]["slicer"]["bed"]
    res = {"model": model, "material": a.material, "bed": bed, "filament_profile": os.path.basename(fil)[:-5]}

    code, txt = run([exe, "--info", model])
    info = dict(re.findall(r"^(\w+) = (\S+)", txt, re.M))
    res["geometry"] = {"size_mm": [float(info.get(k, 0)) for k in ("size_x", "size_y", "size_z")], "volume_mm3": float(info.get("volume", 0)),
                       "manifold": info.get("manifold") == "yes", "facets": int(info.get("number_of_facets", 0))}

    def slice_once(label, process_file, extra=()):
        d = os.path.join(out, label)
        shutil.rmtree(d, ignore_errors=True)
        c, t = run([exe, "--load-settings", "%s;%s" % (machine, process_file), "--load-filaments", fil, "--curr-bed-type", bed,
                    *extra, "--slice", "1", "--outputdir", d, model])
        g = os.path.join(d, "plate_1.gcode")
        if c != 0 or not os.path.exists(g):
            return {"error": t.strip().splitlines()[-2:] or ["slice failed"]}, t
        return gcode_stats(g), t

    res["as_exported"], _ = slice_once("as-exported", "%s/process/%s.json" % (prof, proc_name))
    flat = flatten(os.path.join(prof, "process"), proc_name)
    flat.pop("inherits", None)
    flat.update({"name": "supports forced on", "from": "User", "enable_support": "1", "support_type": "tree(auto)"})
    pf = os.path.join(out, "process-supports.json")
    json.dump(flat, open(pf, "w"), indent=1)
    res["supports_forced"], _ = slice_once("supports-on", pf.replace("\\", "/"))
    res["supports_needed"] = None if "error" in res["supports_forced"] else res["supports_forced"]["support_lines"] > 0
    res["best_orientation"] = None
    c, t = run([exe, "--load-settings", "%s;%s/process/%s.json" % (machine, prof, proc_name), "--load-filaments", fil, "--curr-bed-type", bed,
                "--orient", "1", "--slice", "1", "--outputdir", os.path.join(out, "oriented"), model])
    m = re.search(r"^best:\s*(-?[\d.]+)\s+(-?[\d.]+)\s+(-?[\d.]+)", t, re.M)
    if m:
        v = [float(x) for x in m.groups()]
        res["best_orientation"] = {"up_vector": v, "matches_export": abs(v[2] - 1) < 0.01 and abs(v[0]) < 0.01 and abs(v[1]) < 0.01}

    if a.json:
        print(json.dumps(res, indent=2)); return
    g = res["geometry"]
    print("%s in %s (%s, %s bed)" % (os.path.basename(model), a.material, res["filament_profile"], bed))
    print("  geometry : %.1f x %.1f x %.1f mm, %.2f cm3, %s" % (*g["size_mm"], g["volume_mm3"] / 1000, "watertight" if g["manifold"] else "NOT WATERTIGHT: repair before printing"))
    e = res["as_exported"]
    print("  as exported: " + ("slice failed: %s" % e["error"] if "error" in e else "%s, %s g, %s layers, support lines: %d" % (e["time"], e["filament_g"], e["layers"], e["support_lines"])))
    s = res["supports_forced"]
    if "error" not in s:
        print("  supports on: %s, %s g, support lines: %d  ->  %s" % (s["time"], s["filament_g"], s["support_lines"],
              "supports ARE needed in this orientation" if res["supports_needed"] else "no support generated: this orientation needs none"))
    b = res["best_orientation"]
    if b:
        print("  best orientation by the slicer: up = %s  ->  %s" % (b["up_vector"], "matches your export" if b["matches_export"] else "DIFFERS from your export: compare time and supports"))
    print("  G-code and logs in %s. Confirm in the slicer GUI before printing." % out)


if __name__ == "__main__":
    main()
