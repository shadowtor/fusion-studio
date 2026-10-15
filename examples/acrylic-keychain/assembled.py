# Moves the keychain parts to the assembled position (explode_gap 0) and frames the view. Run after build.py, same --lib.
import math
def run(_c):
    root = design().rootComponent
    occs = {o.component.name: o for o in root.occurrences}
    def put(occ, x, y, z, rot=0.0):
        m = adsk.core.Matrix3D.create()
        if rot: m.setToRotation(math.radians(rot), adsk.core.Vector3D.create(0, 1, 0), adsk.core.Point3D.create(0, 0, 0))
        m.translation = adsk.core.Vector3D.create(x / 10, y / 10, z / 10); occ.transform2 = m
    hx, hy = mm("hole_inset"), mm("key_h") - mm("hole_inset"); zmid = (2*mm("acr_t")+mm("art_t"))/2
    put(occs["Back Acrylic - SHOWCASE"],0,0,0); put(occs["Art Sheet - SHOWCASE"],0,0,0); put(occs["Front Acrylic - SHOWCASE"],0,0,0)
    put(occs["Split Ring - SHOWCASE"], hx, hy+mm("ring_R"), zmid, 90)
    view((1.0, 0.7, 0.9))
