# Monster can holder (Print mode: PETG, Bambu Lab H2C). Run with:
#   python skills/fusion-studio/scripts/fusion_mcp.py run examples/monster-can-holder/build.py --lib
# A free-standing cup for a tall 500 ml can: base, round wall, a finger notch at the front so the can lifts out.
# Prints upright on its base: no supports, no bridges. The can size is an assumed example: measure yours.

def run(_c):
    new_design()

    # measured (assumed for the example: a 500 ml can)
    param("can_dia", "66 mm", "Assumed can diameter: measure the widest point of your can")
    # fit and print
    param("fit_xy", "0.6 mm", "Radial clearance: cans vary and the holder should drop on and off")
    param("wall", "2.4 mm", "Wall thickness, 6 perimeters at 0.4 mm")
    param("base_t", "3.2 mm", "Base thickness")
    param("hold_h", "55 mm", "Height of wall that grips the can")
    param("notch_w", "34 mm", "Finger notch width")
    param("notch_h", "30 mm", "Finger notch depth down from the rim")
    param("rim_r", "0.8 mm", "Rim fillet, soft on the lips")
    param("foot_ch", "0.6 mm", "Bed-contact chamfer, stops elephant foot")
    # derived
    param("in_dia", "can_dia + 2 * fit_xy", "Inside diameter")
    param("out_dia", "in_dia + 2 * wall", "Outside diameter")
    param("total_h", "base_t + hold_h", "Overall height")

    c = component("Can Holder - PRINT")

    s = sketch(c, "Base sketch")
    circle(s, "out_dia")
    body = extrude(c, profiles_by_area(s)[0], "total_h", "new", "Outer cylinder").bodies.item(0)
    body.name = "Can Holder"

    s = sketch(c, "Pocket sketch", "XY", "base_t")
    circle(s, "in_dia")
    extrude(c, profiles_by_area(s)[0], "hold_h + 1 mm", "cut", "Can pocket")

    # finger notch through the front wall (-Y side), cut from the rim down
    s = sketch(c, "Notch sketch", "XZ")
    rect(s, "notch_w", "notch_h + 1 mm", -mm("notch_w") / 2, -(mm("total_h") + 1))
    extrude(c, profiles_by_area(s)[0], "out_dia", "cut", "Finger notch", symmetric=False)

    body = c.bRepBodies.item(0)
    zt = mm("total_h")
    # rim fillet first (circular edges on the top face), then the bed chamfer on the base
    fillet(c, edges_where(body, lambda a, b: a.z > zt - 0.01 and b.z < zt + 0.01), "rim_r", "Rim fillet")
    chamfer(c, edges_where(body, lambda a, b: b.z < 0.01 and b.x - a.x > 20), "foot_ch", "Foot chamfer")
    health()
    report()
    view((0.8, 1.0, 0.9))
