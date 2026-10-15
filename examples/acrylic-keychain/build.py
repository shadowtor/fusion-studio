# Acrylic keychain (Showcase mode: not printed, shown on a crowdfunding page and in video). Run with:
#   python skills/fusion-studio/scripts/fusion_mcp.py run examples/acrylic-keychain/build.py --lib
# Four parts: front acrylic, printed art sheet, back acrylic, split ring. One parameter, explode_gap, spreads them
# along Z for the exploded view. Set it to 0 for the assembled view.

import math


def put(occ, x, y, z, rot_y_deg=0.0):
    """Place an occurrence: optional rotation about Y, then a translation (mm)."""
    m = adsk.core.Matrix3D.create()
    if rot_y_deg:
        m.setToRotation(math.radians(rot_y_deg), adsk.core.Vector3D.create(0, 1, 0), adsk.core.Point3D.create(0, 0, 0))
    m.translation = adsk.core.Vector3D.create(x / 10, y / 10, z / 10)
    occ.transform2 = m


def run(_c):
    d = new_design()
    root = d.rootComponent

    # product
    param("key_w", "50 mm", "Keychain width")
    param("key_h", "38 mm", "Keychain height")
    param("acr_t", "3 mm", "Acrylic sheet thickness, each of the two layers")
    param("art_t", "0.2 mm", "Printed art sheet between the acrylic layers")
    param("corner_r", "5 mm", "Outline corner radius")
    param("hole_dia", "5 mm", "Ring hole")
    param("hole_inset", "6.5 mm", "Hole centre from the top and left edges")
    param("ring_R", "8 mm", "Split ring centre-line radius")
    param("wire_d", "1.6 mm", "Split ring wire diameter")
    # presentation
    param("explode_gap", "14 mm", "Space between parts in the exploded view (0 = assembled)")

    def outline(comp, name, z_expr, t_expr, hole=True):
        s = sketch(comp, name + " sketch", "XY", z_expr)
        rect(s, "key_w", "key_h", 0, 0)
        if hole:
            circle(s, "hole_dia", mm("hole_inset"), mm("key_h") - mm("hole_inset"))
        prof = profiles_by_area(s)[0]
        body = extrude(comp, prof, t_expr, "new", name).bodies.item(0)
        body.name = name
        fillet(comp, edges_where(body, lambda a, b: b.z - a.z > 0.01 and (b.x - a.x) < 0.01 and (b.y - a.y) < 0.01
                                 and ((a.x < 0.01 or a.x > mm("key_w") - 0.01) and (a.y < 0.01 or a.y > mm("key_h") - 0.01))),
               "corner_r", name + " corners")
        return body

    # parts are modelled at their assembled position, then moved by explode_gap
    back = component("Back Acrylic - SHOWCASE")
    outline(back, "Back Acrylic", None, "acr_t")
    art = component("Art Sheet - SHOWCASE")
    outline(art, "Art Sheet", "acr_t", "art_t")
    front = component("Front Acrylic - SHOWCASE")
    outline(front, "Front Acrylic", "acr_t + art_t", "acr_t")

    # ring: a torus drawn flat (axis = Z), then stood up so it passes through the hole
    ring = component("Split Ring - SHOWCASE")
    s = sketch(ring, "Ring section", "XZ")
    s.sketchCurves.sketchCircles.addByCenterRadius(P3(mm("ring_R") / 10, 0, 0), mm("wire_d") / 20)
    axis = s.sketchCurves.sketchLines.addByTwoPoints(P3(0, -1, 0), P3(0, 1, 0))
    i = ring.features.revolveFeatures.createInput(profiles_by_area(s)[0], axis, adsk.fusion.FeatureOperations.NewBodyFeatureOperation)
    i.setAngleExtent(False, V.createByString("360 deg"))
    ring.features.revolveFeatures.add(i).name = "Ring revolve"
    ring.bRepBodies.item(0).name = "Split Ring"

    # assembled placement of the ring: its lowest point sits in the hole, plane of the ring perpendicular to the keychain
    hx, hy = mm("hole_inset"), mm("key_h") - mm("hole_inset")
    zmid = (2 * mm("acr_t") + mm("art_t")) / 2
    occs = {o.component.name: o for o in root.occurrences}

    def place(gap):
        put(occs["Back Acrylic - SHOWCASE"], 0, 0, -gap)
        put(occs["Art Sheet - SHOWCASE"], 0, 0, 0)
        put(occs["Front Acrylic - SHOWCASE"], 0, 0, gap)
        # torus axis is Z; rotate 90 deg about Y so the axis lies along X, ring plane = YZ plane
        put(occs["Split Ring - SHOWCASE"], hx, hy + mm("ring_R"), zmid, 90)

    for comp, look in ((back, "Acrylic (Clear)"), (front, "Acrylic (Clear)"), (art, "Plastic - Glossy (Red)"), (ring, "Chrome")):
        appearance(comp.bRepBodies.item(0), look)

    health()
    place(0)
    print("assembled, parts overlap check done by eye in the screenshot")
    place(mm("explode_gap"))
    view((1.0, 0.7, 0.9))
