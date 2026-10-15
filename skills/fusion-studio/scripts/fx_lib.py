"""fx_lib: helpers that run INSIDE Fusion (prepend with `fusion_mcp.py run file.py --lib`).

Conventions it enforces: millimetres, every dimension a named user parameter with a comment, one component per physical
part named "<Part> - PRINT" (or "- SHOWCASE"), sketches driven by parameter expressions, fillets late, health check at the end.
Fusion API lengths are centimetres internally; these helpers take millimetres or parameter expressions.
"""
import adsk.core, adsk.fusion

app = adsk.core.Application.get()
V = adsk.core.ValueInput
P3 = adsk.core.Point3D.create


def design():
    return adsk.fusion.Design.cast(app.activeProduct)


def new_design():
    """Create a fresh, empty parametric design document (never touches the open ones) and return the Design in mm."""
    app.documents.add(adsk.core.DocumentTypes.FusionDesignDocumentType)
    d = design()
    d.designType = adsk.fusion.DesignTypes.ParametricDesignType
    d.fusionUnitsManager.distanceDisplayUnits = adsk.fusion.DistanceUnits.MillimeterDistanceUnits
    return d


def param(name, expr, comment=""):
    """Create or update a user parameter. expr like '27.7 mm', 'can_dia + 2 * fit_xy', '45 deg', '3' (unitless)."""
    ps = design().userParameters
    p = ps.itemByName(name)
    if p:
        p.expression = expr
        if comment:
            p.comment = comment
        return p
    unit = "deg" if "deg" in expr else "mm"
    return ps.add(name, V.createByString(expr), unit, comment)


def mm(name):
    """Value of a parameter in millimetres."""
    return design().userParameters.itemByName(name).value * 10.0


def component(name, activate=True):
    occ = design().rootComponent.occurrences.addNewComponent(adsk.core.Matrix3D.create())
    occ.component.name = name
    if activate:
        occ.activate()
    return occ.component


def plane(comp, which="XY", offset_expr=None):
    base = {"XY": comp.xYConstructionPlane, "XZ": comp.xZConstructionPlane, "YZ": comp.yZConstructionPlane}[which]
    if not offset_expr:
        return base
    i = comp.constructionPlanes.createInput()
    i.setByOffset(base, V.createByString(offset_expr))
    return comp.constructionPlanes.add(i)


def sketch(comp, name, which="XY", offset_expr=None):
    s = comp.sketches.add(plane(comp, which, offset_expr))
    s.name = name
    return s


def rect(s, w_expr, h_expr, x_mm=0.0, y_mm=0.0):
    """Corner rectangle, lower-left at (x,y) mm, width/height driven by parameter expressions."""
    r = s.sketchCurves.sketchLines.addTwoPointRectangle(P3(x_mm / 10, y_mm / 10, 0), P3(x_mm / 10 + 1, y_mm / 10 + 1, 0))
    ls = [r.item(i) for i in range(4)]
    horiz = [l for l in ls if abs(l.startSketchPoint.geometry.y - l.endSketchPoint.geometry.y) < 1e-9][0]
    vert = [l for l in ls if abs(l.startSketchPoint.geometry.x - l.endSketchPoint.geometry.x) < 1e-9][0]
    H, Vt = adsk.fusion.DimensionOrientations.HorizontalDimensionOrientation, adsk.fusion.DimensionOrientations.VerticalDimensionOrientation
    dh = s.sketchDimensions.addDistanceDimension(horiz.startSketchPoint, horiz.endSketchPoint, H, P3(x_mm / 10, y_mm / 10 - 0.5, 0))
    dv = s.sketchDimensions.addDistanceDimension(vert.startSketchPoint, vert.endSketchPoint, Vt, P3(x_mm / 10 - 0.5, y_mm / 10, 0))
    dh.parameter.expression = w_expr
    dv.parameter.expression = h_expr
    return r


def circle(s, d_expr, cx_mm=0.0, cy_mm=0.0):
    c = s.sketchCurves.sketchCircles.addByCenterRadius(P3(cx_mm / 10, cy_mm / 10, 0), 0.25)
    d = s.sketchDimensions.addDiameterDimension(c, P3(cx_mm / 10 + 0.5, cy_mm / 10 + 0.5, 0))
    d.parameter.expression = d_expr
    return c


def profiles_by_area(s):
    """Sketch profiles, largest first (a rectangle with a hole inside gives the ring first, then the hole)."""
    return sorted(s.profiles, key=lambda p: p.areaProperties().area, reverse=True)


def extrude(comp, profile, dist_expr, op="new", name=None, symmetric=False, bodies=None):
    """op: new | join | cut | intersect. dist_expr like 'can_h + 1 mm'; a negative value flips direction."""
    ops = {"new": adsk.fusion.FeatureOperations.NewBodyFeatureOperation, "join": adsk.fusion.FeatureOperations.JoinFeatureOperation,
           "cut": adsk.fusion.FeatureOperations.CutFeatureOperation, "intersect": adsk.fusion.FeatureOperations.IntersectFeatureOperation}
    i = comp.features.extrudeFeatures.createInput(profile, ops[op])
    if symmetric:
        i.setSymmetricExtent(V.createByString(dist_expr), True)
    else:
        i.setDistanceExtent(False, V.createByString(dist_expr))
    if bodies and op != "new":
        i.participantBodies = bodies
    f = comp.features.extrudeFeatures.add(i)
    if name:
        f.name = name
    return f


def box(comp, name, w_expr, h_expr, d_expr, x_mm=0.0, y_mm=0.0, z_expr=None, op="new"):
    """Parametric block: width (X) x height (Y) x depth (Z), optionally lifted by z_expr. Returns the extrude feature."""
    s = sketch(comp, name + " sketch", "XY", z_expr)
    rect(s, w_expr, h_expr, x_mm, y_mm)
    return extrude(comp, profiles_by_area(s)[0], d_expr, op, name)


def _edgeset(edges):
    es = adsk.core.ObjectCollection.create()
    for e in edges:
        es.add(e)
    return es


def fillet(comp, edges, r_expr, name=None):
    i = comp.features.filletFeatures.createInput()
    i.addConstantRadiusEdgeSet(_edgeset(edges), V.createByString(r_expr), True)
    f = comp.features.filletFeatures.add(i)
    if name:
        f.name = name
    return f


def chamfer(comp, edges, d_expr, name=None):
    i = comp.features.chamferFeatures.createInput2()
    i.chamferEdgeSets.addEqualDistanceChamferEdgeSet(_edgeset(edges), V.createByString(d_expr), True)
    f = comp.features.chamferFeatures.add(i)
    if name:
        f.name = name
    return f


def edges_where(body, test):
    """Edges whose bounding box (mm) satisfies test(lo, hi), e.g. vertical edges: lambda a, b: b.z - a.z > 1."""
    out = []
    for e in body.edges:
        bb = e.boundingBox
        a = P3(bb.minPoint.x * 10, bb.minPoint.y * 10, bb.minPoint.z * 10)
        b = P3(bb.maxPoint.x * 10, bb.maxPoint.y * 10, bb.maxPoint.z * 10)
        if test(a, b):
            out.append(e)
    return out


def health():
    """Print every timeline item that is not healthy. Returns the number of problems."""
    t = design().timeline
    bad = 0
    for i in range(t.count):
        it = t.item(i)
        if it.healthState != adsk.fusion.FeatureHealthStates.HealthyFeatureHealthState:
            bad += 1
            print("UNHEALTHY", it.name, "-", it.errorOrWarningMessage)
    print("timeline items:", t.count, "problems:", bad)
    return bad


def report(bed=(305, 320, 325)):
    """Per-body size, volume and bed fit. Default bed: Bambu Lab H2C single-nozzle volume in mm (verify against the spec page)."""
    for c in design().allComponents:
        for b in c.bRepBodies:
            bb = b.boundingBox
            sz = [(bb.maxPoint.x - bb.minPoint.x) * 10, (bb.maxPoint.y - bb.minPoint.y) * 10, (bb.maxPoint.z - bb.minPoint.z) * 10]
            fit = all(s <= m for s, m in zip(sorted(sz), sorted(bed)))
            print("%s / %s: %.2f x %.2f x %.2f mm, %.3f cm3, solid=%s, fits bed=%s" %
                  (c.name, b.name, sz[0], sz[1], sz[2], b.volume, b.isSolid, fit))


def export(body, path, fmt="3mf"):
    """Export one body (3mf / stl) or the whole design (step / f3d). `path` has no extension."""
    em = design().exportManager
    if fmt == "3mf":
        o = em.createC3MFExportOptions(body, path + ".3mf")
    elif fmt == "stl":
        o = em.createSTLExportOptions(body, path + ".stl")
        o.meshRefinement = adsk.fusion.MeshRefinementSettings.MeshRefinementHigh
    elif fmt == "step":
        o = em.createSTEPExportOptions(path + ".step", design().rootComponent)
    else:
        o = em.createFusionArchiveExportOptions(path + ".f3d", design().rootComponent)
    em.execute(o)
    print("exported", path + "." + fmt)


def view(eye=(1.0, 1.0, 0.8), up=(0.0, 0.0, 1.0)):
    """Point the camera at the design from a direction (eye is a direction, not a position), with Z up, then fit.
    Fusion's world is Y-up, so parts modelled with their height along Z look like they lie on their side in the standard
    cube views. Call view() before a screenshot (`fusion_mcp.py shot --dir current`)."""
    vp = app.activeViewport
    bb = design().rootComponent.boundingBox
    c = P3((bb.minPoint.x + bb.maxPoint.x) / 2, (bb.minPoint.y + bb.maxPoint.y) / 2, (bb.minPoint.z + bb.maxPoint.z) / 2)
    cam = vp.camera
    cam.isSmoothTransition = False
    cam.cameraType = adsk.core.CameraTypes.OrthographicCameraType
    cam.target = c
    cam.upVector = adsk.core.Vector3D.create(*up)
    cam.eye = P3(c.x + eye[0] * 50, c.y + eye[1] * 50, c.z + eye[2] * 50)
    vp.camera = cam
    vp.fit()


def appearance(body, name):
    """Apply a Fusion Appearance Library look to a body, e.g. 'Acrylic (Clear)', 'Chrome', 'Plastic - Glossy (Red)'.
    Look names up with: [a.name for a in app.materialLibraries.itemByName('Fusion Appearance Library').appearances]."""
    lib = app.materialLibraries.itemByName("Fusion Appearance Library")
    src = lib.appearances.itemByName(name)
    mine = design().appearances.itemByName(name) or design().appearances.addByCopy(src, name)
    body.appearance = mine
