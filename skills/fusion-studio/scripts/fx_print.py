"""fx_print: Print-mode helpers that run INSIDE Fusion, after fx_lib (the client prepends MATERIALS, fx_lib, then this file).

Build direction is +Z with the bed at the lowest Z of each body. Everything here reads geometry only, or creates parameters
and a test coupon. It does not replace the slicer: confirm orientation and supports there, and calibrate fits with fit_coupon().
"""
import math


def print_profile(material):
    """Create the material's print parameters in the design and return the profile dict.
    Fits are DIAMETRAL: the total gap across both sides (per side is half). fit_* already include the material offset.
    Use them in expressions, for example pocket_w = tile_w + fit_close. They are starting values: calibrate with fit_coupon()."""
    m = MATERIALS["materials"][material]
    base = MATERIALS["fit_base_diametral_mm"]
    for k in ("press", "close", "free"):
        param("fit_" + k, "%.3f mm" % max(0.0, base[k] + m["fit_offset_mm"]),
              "%s fit, diametral (total), %s starting value" % (k, material))
    param("min_wall", "%.2f mm" % m["min_wall_mm"], "Thinnest wall to design, %s" % material)
    param("min_feature", "%.2f mm" % m["min_feature_mm"], "Thinnest rib or pin to design, %s" % material)
    param("hole_comp", "%.2f mm" % m["hole_comp_mm"], "Add to small round hole diameters, they print undersized, %s" % material)
    for n in m["notes"]:
        print("NOTE %s: %s" % (material, n))
    if m["enclosure"]:
        print("NOTE %s: needs an enclosed, heated chamber and ventilation." % material)
    return m


def _samples(face, n=4):
    """(point, outward normal) pairs on a face, from an n x n grid in parameter space."""
    ev = face.evaluator
    r = ev.parametricRange()
    pts = []
    for i in range(n):
        for j in range(n):
            u = r.minPoint.x + (r.maxPoint.x - r.minPoint.x) * (i + 0.5) / n
            v = r.minPoint.y + (r.maxPoint.y - r.minPoint.y) * (j + 0.5) / n
            pts.append(adsk.core.Point2D.create(u, v))
    okp, ps = ev.getPointsAtParameters(pts)
    okn, ns = ev.getNormalsAtParameters(pts)
    if not (okp and okn):
        return []
    return [(ps[k], ns[k]) for k in range(len(pts))]


def _wall_at(comp, p, n):
    """Distance in mm from p straight into the material (against outward normal n) to the next surface, or None."""
    o = P3(p.x - n.x * 0.002, p.y - n.y * 0.002, p.z - n.z * 0.002)
    d = adsk.core.Vector3D.create(-n.x, -n.y, -n.z)
    hits = adsk.core.ObjectCollection.create()
    comp.findBRepUsingRay(o, d, adsk.fusion.BRepEntityTypes.BRepFaceEntityType, 0.0005, False, hits)
    best = None
    for h in hits:
        dist = o.distanceTo(h) * 10
        if dist > 0.02 and (best is None or dist < best):
            best = dist
    return best


def print_check(material):
    """Check every body against the material profile. Prints OK / WARN / INFO lines and returns the number of warnings.
    Checks: bed fit, thin walls (ray probe), overhangs and bridges (face normals against +Z), small and horizontal round holes."""
    m = MATERIALS["materials"][material]
    warns = 0
    for comp in design().allComponents:
        for body in comp.bRepBodies:
            tag = "%s / %s" % (comp.name, body.name)
            bb = body.boundingBox
            z0 = bb.minPoint.z * 10
            sz = [(bb.maxPoint.x - bb.minPoint.x) * 10, (bb.maxPoint.y - bb.minPoint.y) * 10, (bb.maxPoint.z - bb.minPoint.z) * 10]
            if not all(s <= b for s, b in zip(sorted(sz), (305, 320, 325))):
                warns += 1
                print("WARN %s: %.0f x %.0f x %.0f mm may not fit the bed" % (tag, sz[0], sz[1], sz[2]))
            thin, over, bridges, holes = [], [], [], []
            for face in body.faces:
                if face.area * 100 < 1.0:
                    continue
                fb = face.boundingBox
                pts = _samples(face, 4 if face.geometry.surfaceType == adsk.core.SurfaceTypes.PlaneSurfaceType else 8)
                st = face.geometry.surfaceType
                if st in (adsk.core.SurfaceTypes.PlaneSurfaceType, adsk.core.SurfaceTypes.CylinderSurfaceType):
                    # fillets and chamfers taper by design, so only flat and round faces are probed for wall thickness
                    for p, n in (pts if len(pts) == 16 else _samples(face, 4))[::3]:
                        w = _wall_at(comp, p, n)
                        if w is not None and 0.1 < w < m["min_wall_mm"] - 0.01:  # under 0.1 mm is a ray grazing an edge
                            thin.append((w, p))
                if fb.maxPoint.z * 10 < z0 + 1.0:
                    continue  # first-layer chamfer or fillet on the bed edge: the recommended fix, not an overhang
                bad = [n for p, n in pts if n.z < 0 and p.z * 10 > z0 + 0.05
                       and math.degrees(math.asin(min(1.0, -n.z))) > m["overhang_max_deg"] + 0.5]
                if bad:
                    flat = (all(-n.z > 0.98 for n in bad)
                            and face.geometry.surfaceType == adsk.core.SurfaceTypes.PlaneSurfaceType)
                    span = min(fb.maxPoint.x - fb.minPoint.x, fb.maxPoint.y - fb.minPoint.y) * 10
                    (bridges if flat else over).append((face, span, len(bad) / float(len(pts)), fb.minPoint.z * 10))
                if face.geometry.surfaceType == adsk.core.SurfaceTypes.CylinderSurfaceType and pts:
                    g = face.geometry
                    p, n = pts[0]
                    if ((p.x - g.origin.x) * n.x + (p.y - g.origin.y) * n.y + (p.z - g.origin.z) * n.z) < 0:
                        holes.append((g.radius * 20, abs(g.axis.z) < 0.5))
            if thin:
                warns += 1
                w, p = min(thin, key=lambda t: t[0])
                print("WARN %s: wall down to %.2f mm near (%.1f, %.1f, %.1f), the profile wants at least %.1f mm (%d probe points)" %
                      (tag, w, p.x * 10, p.y * 10, p.z * 10, m["min_wall_mm"], len(thin)))
            for face, span, frac, fz in bridges:
                if span > m["bridge_max_mm"]:
                    warns += 1
                    print("WARN %s: flat ceiling at z=%.1f mm spans %.1f mm, bridge limit %.0f mm: add a rib, a support, or split the part" %
                          (tag, fz, span, m["bridge_max_mm"]))
            for face, span, frac, fz in over:
                warns += 1
                print("WARN %s: face from z=%.1f mm overhangs past %d deg from vertical (%d%% of samples): expect supports, or add a chamfer, fillet or teardrop" %
                      (tag, fz, m["overhang_max_deg"], round(frac * 100)))
            for dia, horizontal in holes:
                if dia < 6.0:
                    print("INFO %s: round hole %.2f mm%s: draw it at %.2f mm (hole_comp) so it prints at size%s" %
                          (tag, dia, " (horizontal)" if horizontal else "", dia + m["hole_comp_mm"],
                           ", and use a teardrop or 45 degree diamond top" if horizontal else ""))
                elif horizontal:
                    warns += 1
                    print("WARN %s: horizontal hole %.1f mm: the upper half overhangs, use a teardrop or support" % (tag, dia))
            if not (thin or bridges or over):
                print("OK   %s: walls, overhangs and bridges within limits (%.1f x %.1f x %.1f mm)" % (tag, sz[0], sz[1], sz[2]))
    if m["enclosure"]:
        print("INFO this material needs an enclosed chamber: avoid long flat bed faces, sharp corners and thin tall features.")
    print("print_check: %d warning(s). Confirm orientation and supports in the slicer, calibrate fits with fit_coupon()." % warns)
    return warns


def fit_coupon(nominal_mm=10.0, clearances=(0.1, 0.2, 0.3, 0.4), height_mm=6.0):
    """Fit test print: a plate with round holes and a bar with matching pins. Hole = nominal + diametral clearance.
    Print both, find the clearance that gives the fit you want, then set fit_* to it. Hole 1 (left) is the tightest."""
    n = len(clearances)
    pitch = nominal_mm + 8.0
    plate_w, plate_h = pitch * n + 4.0, nominal_mm + 14.0
    param("coupon_nom", "%.2f mm" % nominal_mm, "Coupon nominal pin diameter")
    param("coupon_t", "3 mm", "Coupon plate thickness")
    param("coupon_pin_h", "%.2f mm" % height_mm, "Coupon pin height")
    comp = component("Fit Coupon - PRINT")
    s = sketch(comp, "Plate sketch")
    rect(s, "%.3f mm" % plate_w, "%.3f mm" % plate_h, 0, 0)
    for i, c in enumerate(clearances):
        circle(s, "coupon_nom + %.3f mm" % c, 2.0 + pitch * (i + 0.5), plate_h / 2.0)
    plate = extrude(comp, profiles_by_area(s)[0], "coupon_t", "new", "Hole plate").bodies.item(0)
    plate.name = "Fit Coupon Holes"
    s2 = sketch(comp, "Pins sketch")
    y0 = -plate_h - 6.0
    rect(s2, "%.3f mm" % plate_w, "%.3f mm" % plate_h, 0, y0)
    for i in range(n):
        circle(s2, "coupon_nom", 2.0 + pitch * (i + 0.5), y0 + plate_h / 2.0)
    ps = profiles_by_area(s2)
    base = extrude(comp, ps[0], "coupon_t", "new", "Pin bar").bodies.item(0)
    base.name = "Fit Coupon Pins"
    for p in ps[1:]:
        extrude(comp, p, "coupon_t + coupon_pin_h", "join", "Pin", bodies=[base])
    print("fit coupon: holes = %.2f mm + [%s] mm diametral. Hole 1 is the tightest." %
          (nominal_mm, ", ".join("%.2f" % c for c in clearances)))
    return comp
