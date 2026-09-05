# _props/geometry.py
# ════════════════════════════════════════════════════════════════
# Geometry primitives + Blender scene helpers used by every locale
# builder. Vertex-coloured, no PBR — matches the rest of the
# 3D pipeline (per CLAUDE.md "vertex-coloured locale geometry").
#
# Two primitives:
#   · make_box  — axis-aligned 6-face box with optional open faces
#   · make_cyl  — N-segment cylinder (default 8) about X / Y / Z
# Both attach a "Col" vertex-color layer initialised to base_color
# so the GLB export carries the colour without needing a material.
#
# clear_scene wipes Blender state — call at the top of every
# builder's main() so re-running the script doesn't accumulate
# objects from a prior run.
# ════════════════════════════════════════════════════════════════
import math
try:
    import bpy   # type: ignore
except ImportError:
    bpy = None   # Allow import outside Blender (lint / tests)


def clear_scene():
    if bpy is None:
        return
    for obj in list(bpy.data.objects):
        bpy.data.objects.remove(obj, do_unlink=True)
    for mesh in list(bpy.data.meshes):
        bpy.data.meshes.remove(mesh, do_unlink=True)


def _finalize_mesh(name, verts, faces, base_color):
    if bpy is None:
        return None
    mesh = bpy.data.meshes.new(name + "_mesh")
    mesh.from_pydata(verts, [], faces)
    mesh.update()
    if not mesh.vertex_colors:
        mesh.vertex_colors.new(name="Col")
    layer = mesh.vertex_colors["Col"]
    for poly in mesh.polygons:
        for li in poly.loop_indices:
            layer.data[li].color = base_color
    obj = bpy.data.objects.new(name, mesh)
    bpy.context.collection.objects.link(obj)
    return obj


def make_box(name, center, size, base_color, open_faces=None):
    """6-face axis-aligned box centered at `center` with `size`
    (full XYZ dimensions). open_faces is an optional set of face
    tags ('+X','-X','+Y','-Y','+Z','-Z') to omit for inset hollows."""
    open_faces = open_faces or set()
    cx, cy, cz = center
    sx, sy, sz = size
    hx, hy, hz = sx / 2.0, sy / 2.0, sz / 2.0
    verts = [
        (cx-hx, cy-hy, cz-hz), (cx+hx, cy-hy, cz-hz),
        (cx+hx, cy+hy, cz-hz), (cx-hx, cy+hy, cz-hz),
        (cx-hx, cy-hy, cz+hz), (cx+hx, cy-hy, cz+hz),
        (cx+hx, cy+hy, cz+hz), (cx-hx, cy+hy, cz+hz),
    ]
    face_defs = [('-Z',(0,3,2,1)), ('+Z',(4,5,6,7)),
                 ('-Y',(0,1,5,4)), ('+Y',(2,3,7,6)),
                 ('-X',(3,0,4,7)), ('+X',(1,2,6,5))]
    out_faces = [vids for tag, vids in face_defs if tag not in open_faces]
    return _finalize_mesh(name, verts, out_faces, base_color)


def make_cyl(name, center, radius, height, base_color,
             segments=8, axis='Z'):
    """N-segment cylinder. axis='Z' (default — height along Z),
    'X', or 'Y'. Segments default 8 — bump up to 12-16 for very
    prominent cylinders that read at close range."""
    cx, cy, cz = center
    h2 = height / 2.0
    verts = []
    for ring in (0, 1):
        z_off = -h2 if ring == 0 else h2
        for i in range(segments):
            ang = 2.0 * math.pi * i / segments
            a = math.cos(ang) * radius
            b = math.sin(ang) * radius
            if axis == 'Z':
                verts.append((cx + a, cy + b, cz + z_off))
            elif axis == 'Y':
                verts.append((cx + a, cy + z_off, cz + b))
            else:    # 'X'
                verts.append((cx + z_off, cy + a, cz + b))
    faces = []
    for i in range(segments):
        ni = (i + 1) % segments
        faces.append([i, ni, ni + segments, i + segments])
    faces.append(list(reversed(range(segments))))
    faces.append(list(range(segments, segments * 2)))
    return _finalize_mesh(name, verts, faces, base_color)


def export_glb(out_path, *, export_lights=False, export_cameras=False):
    """Standard glTF export — select-all + use_selection=False so
    every object lands in the GLB. Defaults match what all our
    locale builders need."""
    if bpy is None:
        return
    import os
    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    bpy.ops.object.select_all(action='SELECT')
    base = {'filepath': out_path, 'export_format': 'GLB',
            'use_selection': False, 'export_apply': True,
            'export_lights': export_lights,
            'export_cameras': export_cameras}
    rna = bpy.ops.export_scene.gltf.get_rna_type()
    legacy = {}
    if 'export_colors' in rna.properties:  legacy['export_colors'] = True
    if 'export_normals' in rna.properties: legacy['export_normals'] = True
    bpy.ops.export_scene.gltf(**base, **legacy)
    if os.path.exists(out_path):
        size = os.path.getsize(out_path)
        print(f"[props.export_glb] wrote {out_path} ({size} bytes)")


# ════════════════════════════════════════════════════════════════
# DE-MINECRAFT VOCABULARY (2026-08-04)
# ════════════════════════════════════════════════════════════════
# "Lighting won't fix the minecraft, blender will." Correct: with
# only axis-aligned make_box / make_cyl, every locale is literally
# built from blocks — hard 90° edges, flat facets, no slopes, no
# organics. These primitives grow the vocabulary. All pure pydata
# (no bpy.ops, no modifiers), deterministic, vertex-coloured like
# the originals.
#
#   make_chamfer_box  the box replacement — edges cut at `chamfer`
#                     so they catch light instead of knifing it
#   make_wedge        right-triangular prism · ramps, hoods, banks
#   make_gable        symmetric triangular prism · ROOFS
#   make_taper_cyl    frustum · trunks, shades, funnels (r_top=0
#                     makes a cone)
#   make_dome         UV hemisphere · tanks, hills, awnings
#   make_blob         noise-displaced sphere · TREE CROWNS, rocks,
#                     bushes — the organic silhouette boxes can't do
#
# All accept `yaw` (radians, about Z at the object's own center) —
# rotation was banned because free rotation made the coordinate
# frame illegible; yaw-only through this parameter keeps footprints
# reasoned about in plan view while killing the everything-faces-
# the-same-way grid look.
#
# Winding is computed, not hand-tracked: every face is checked
# against the outward direction from the shape's center and flipped
# if inward, so no primitive can ship invisible faces.


def _yaw_rot(verts, center, yaw):
    if not yaw:
        return verts
    cx, cy, cz = center
    c, s = math.cos(yaw), math.sin(yaw)
    out = []
    for (x, y, z) in verts:
        dx, dy = x - cx, y - cy
        out.append((cx + dx * c - dy * s, cy + dx * s + dy * c, z))
    return out


def _fix_winding(verts, faces, center):
    cx, cy, cz = center
    fixed = []
    for f in faces:
        v0, v1, v2 = verts[f[0]], verts[f[1]], verts[f[2]]
        e1 = (v1[0]-v0[0], v1[1]-v0[1], v1[2]-v0[2])
        e2 = (v2[0]-v0[0], v2[1]-v0[1], v2[2]-v0[2])
        nx = e1[1]*e2[2] - e1[2]*e2[1]
        ny = e1[2]*e2[0] - e1[0]*e2[2]
        nz = e1[0]*e2[1] - e1[1]*e2[0]
        mx = sum(verts[i][0] for i in f) / len(f) - cx
        my = sum(verts[i][1] for i in f) / len(f) - cy
        mz = sum(verts[i][2] for i in f) / len(f) - cz
        fixed.append(list(reversed(f))
                     if nx*mx + ny*my + nz*mz < 0 else list(f))
    return fixed


def _h01g(a, b, c=0):
    n = (a * 374761393 + b * 668265263 + c * 1442695041) & 0xFFFFFFFF
    n = ((n ^ (n >> 13)) * 1274126177) & 0xFFFFFFFF
    return ((n ^ (n >> 16)) & 0xFFFF) / 65536.0


def make_chamfer_box(name, center, size, base_color,
                     chamfer=0.05, yaw=0.0):
    """Box with every edge cut back by `chamfer` — the single
    biggest de-blocking move: a zero-radius edge reads as CAD, a
    cut edge catches a highlight and reads as a made thing. Use for
    counters, furniture, appliances, vehicles, machine bodies."""
    cx, cy, cz = center
    hx, hy, hz = size[0]/2.0, size[1]/2.0, size[2]/2.0
    c = min(chamfer, hx * 0.45, hy * 0.45, hz * 0.45)
    verts, idx = [], {}
    for i in (-1, 1):
        for j in (-1, 1):
            for k in (-1, 1):
                idx[(i, j, k, 'x')] = len(verts)
                verts.append((cx + i*hx, cy + j*(hy-c), cz + k*(hz-c)))
                idx[(i, j, k, 'y')] = len(verts)
                verts.append((cx + i*(hx-c), cy + j*hy, cz + k*(hz-c)))
                idx[(i, j, k, 'z')] = len(verts)
                verts.append((cx + i*(hx-c), cy + j*(hy-c), cz + k*hz))
    faces = []
    for i in (-1, 1):   # X faces
        faces.append([idx[(i, -1, -1, 'x')], idx[(i, 1, -1, 'x')],
                      idx[(i, 1, 1, 'x')], idx[(i, -1, 1, 'x')]])
    for j in (-1, 1):   # Y faces
        faces.append([idx[(-1, j, -1, 'y')], idx[(1, j, -1, 'y')],
                      idx[(1, j, 1, 'y')], idx[(-1, j, 1, 'y')]])
    for k in (-1, 1):   # Z faces
        faces.append([idx[(-1, -1, k, 'z')], idx[(1, -1, k, 'z')],
                      idx[(1, 1, k, 'z')], idx[(-1, 1, k, 'z')]])
    for i in (-1, 1):   # 12 edge chamfer quads
        for j in (-1, 1):
            faces.append([idx[(i, j, -1, 'x')], idx[(i, j, 1, 'x')],
                          idx[(i, j, 1, 'y')], idx[(i, j, -1, 'y')]])
    for i in (-1, 1):
        for k in (-1, 1):
            faces.append([idx[(i, -1, k, 'x')], idx[(i, 1, k, 'x')],
                          idx[(i, 1, k, 'z')], idx[(i, -1, k, 'z')]])
    for j in (-1, 1):
        for k in (-1, 1):
            faces.append([idx[(-1, j, k, 'y')], idx[(1, j, k, 'y')],
                          idx[(1, j, k, 'z')], idx[(-1, j, k, 'z')]])
    for i in (-1, 1):   # 8 corner triangles
        for j in (-1, 1):
            for k in (-1, 1):
                faces.append([idx[(i, j, k, 'x')], idx[(i, j, k, 'y')],
                              idx[(i, j, k, 'z')]])
    verts = _yaw_rot(verts, center, yaw)
    return _finalize_mesh(name, verts, _fix_winding(verts, faces, center),
                          base_color)


def make_wedge(name, center, size, base_color, yaw=0.0, high_end='+Y'):
    """Right-triangular prism: full height at `high_end` ('+Y','-Y',
    '+X','-X'), zero at the other. Ramps, car hoods, lean-to roofs,
    embankments."""
    cx, cy, cz = center
    hx, hy, hz = size[0]/2.0, size[1]/2.0, size[2]/2.0
    lo, hi = cz - hz, cz + hz
    if high_end in ('+Y', '-Y'):
        s = 1 if high_end == '+Y' else -1
        verts = [(cx-hx, cy-s*hy, lo), (cx+hx, cy-s*hy, lo),
                 (cx+hx, cy+s*hy, lo), (cx-hx, cy+s*hy, lo),
                 (cx-hx, cy+s*hy, hi), (cx+hx, cy+s*hy, hi)]
    else:
        s = 1 if high_end == '+X' else -1
        verts = [(cx-s*hx, cy-hy, lo), (cx-s*hx, cy+hy, lo),
                 (cx+s*hx, cy+hy, lo), (cx+s*hx, cy-hy, lo),
                 (cx+s*hx, cy-hy, hi), (cx+s*hx, cy+hy, hi)]
    faces = [[0, 1, 2, 3], [0, 1, 5, 4], [2, 3, 4, 5],
             [0, 3, 4], [1, 2, 5]]
    verts = _yaw_rot(verts, center, yaw)
    return _finalize_mesh(name, verts, _fix_winding(verts, faces, center),
                          base_color)


def make_gable(name, center, size, base_color, yaw=0.0, ridge_axis='X'):
    """Symmetric triangular prism — ridge along `ridge_axis`, full
    `size` footprint, apex at +Z. THE roof shape: every flat-topped
    building in the project can carry one of these instead of a
    slab lid."""
    cx, cy, cz = center
    hx, hy, hz = size[0]/2.0, size[1]/2.0, size[2]/2.0
    lo, hi = cz - hz, cz + hz
    if ridge_axis == 'X':
        verts = [(cx-hx, cy-hy, lo), (cx+hx, cy-hy, lo),
                 (cx+hx, cy+hy, lo), (cx-hx, cy+hy, lo),
                 (cx-hx, cy, hi), (cx+hx, cy, hi)]
        faces = [[0, 1, 2, 3], [0, 1, 5, 4], [2, 3, 4, 5],
                 [0, 3, 4], [1, 2, 5]]
    else:
        verts = [(cx-hx, cy-hy, lo), (cx+hx, cy-hy, lo),
                 (cx+hx, cy+hy, lo), (cx-hx, cy+hy, lo),
                 (cx, cy-hy, hi), (cx, cy+hy, hi)]
        faces = [[0, 1, 2, 3], [0, 1, 4], [2, 3, 5],
                 [1, 2, 5, 4], [0, 3, 5, 4]]
    verts = _yaw_rot(verts, center, yaw)
    return _finalize_mesh(name, verts, _fix_winding(verts, faces, center),
                          base_color)


def make_taper_cyl(name, center, r_bottom, r_top, height, base_color,
                   segments=10, axis='Z'):
    """Frustum — r_top=0 gives a cone. Tree trunks taper; lamp
    shades flare; a straight cylinder is a pipe and almost nothing
    else in the world is a pipe."""
    cx, cy, cz = center
    h2 = height / 2.0
    verts = []
    apex_top = r_top <= 1e-6
    for ring, (z_off, rr) in enumerate(((-h2, r_bottom), (h2, r_top))):
        if ring == 1 and apex_top:
            break
        for i in range(segments):
            ang = 2.0 * math.pi * i / segments
            a, b = math.cos(ang) * rr, math.sin(ang) * rr
            if axis == 'Z':
                verts.append((cx + a, cy + b, cz + z_off))
            elif axis == 'Y':
                verts.append((cx + a, cy + z_off, cz + b))
            else:
                verts.append((cx + z_off, cy + a, cz + b))
    faces = []
    if apex_top:
        apex = len(verts)
        if axis == 'Z':
            verts.append((cx, cy, cz + h2))
        elif axis == 'Y':
            verts.append((cx, cy + h2, cz))
        else:
            verts.append((cx + h2, cy, cz))
        for i in range(segments):
            faces.append([i, (i + 1) % segments, apex])
        faces.append(list(reversed(range(segments))))
    else:
        for i in range(segments):
            ni = (i + 1) % segments
            faces.append([i, ni, ni + segments, i + segments])
        faces.append(list(reversed(range(segments))))
        faces.append(list(range(segments, segments * 2)))
    return _finalize_mesh(name, verts, _fix_winding(verts, faces, center),
                          base_color)


def _uv_sphere(center, radius, rings, segments, squash, noise, seed):
    cx, cy, cz = center
    verts = [(cx, cy, cz + radius * squash)]
    for r in range(1, rings):
        phi = math.pi * r / rings
        for s in range(segments):
            th = 2.0 * math.pi * s / segments
            k = 1.0 + (0.0 if not noise
                       else (_h01g(r, s, seed) - 0.5) * 2.0 * noise)
            rr = radius * k
            verts.append((cx + rr * math.sin(phi) * math.cos(th),
                          cy + rr * math.sin(phi) * math.sin(th),
                          cz + rr * math.cos(phi) * squash))
    verts.append((cx, cy, cz - radius * squash))
    faces = []
    for s in range(segments):
        faces.append([0, 1 + s, 1 + (s + 1) % segments])
    for r in range(rings - 2):
        base = 1 + r * segments
        for s in range(segments):
            ns = (s + 1) % segments
            faces.append([base + s, base + segments + s,
                          base + segments + ns, base + ns])
    last = len(verts) - 1
    base = 1 + (rings - 2) * segments
    for s in range(segments):
        faces.append([last, base + (s + 1) % segments, base + s])
    return verts, faces


def make_dome(name, center, radius, base_color, rings=4, segments=10,
              squash=1.0):
    """UV hemisphere sitting on its equator (base at center z).
    Tanks, hills, awning crowns, boulder tops."""
    cx, cy, cz = center
    verts, faces = _uv_sphere((cx, cy, cz), radius, rings * 2,
                              segments, squash, 0.0, 0)
    keep = [i for i, v in enumerate(verts) if v[2] >= cz - 1e-6]
    remap = {old: new for new, old in enumerate(keep)}
    verts2 = [verts[i] for i in keep]
    faces2 = [[remap[i] for i in f] for f in faces
              if all(i in remap for i in f)]
    rim = [remap[i] for i in keep
           if abs(verts[i][2] - cz) < radius * 0.35 and i != 0]
    if len(rim) >= 3:
        cxy = (cx, cy, cz)
        rim.sort(key=lambda i: math.atan2(verts2[i][1] - cy,
                                          verts2[i][0] - cx))
        faces2.append(list(reversed(rim)))
    return _finalize_mesh(name, verts2,
                          _fix_winding(verts2, faces2,
                                       (cx, cy, cz + radius * 0.4)),
                          base_color)


def make_blob(name, center, radius, base_color, noise=0.22, seed=0,
              rings=5, segments=9, squash=0.8):
    """Noise-displaced sphere — the organic silhouette a box cannot
    make. Tree crowns, bushes, rocks, hay, cloud puffs. Deterministic
    per `seed`; lumpy low-poly on purpose (the facets ARE the
    foliage read at our art scale)."""
    verts, faces = _uv_sphere(center, radius, rings, segments,
                              squash, noise, seed)
    return _finalize_mesh(name, verts, _fix_winding(verts, faces, center),
                          base_color)


# ════════════════════════════════════════════════════════════════
# DETAIL DRAFT 1 primitives (2026-09-05, user: "3d scenes are still
# feeling real primitive. basic cubes and rectangles when the objects
# and environments need far more detail and complexity.")
#
# Every set was assembled from boxes, cylinders and blobs. These five
# give a builder curved silhouettes, arbitrary footprints, swept
# lines, tilted members and rolling ground:
#   · make_lathe      a revolved profile — bottles, basins, posts with
#                     caps, hydrants, tires, lamp shades, bollards
#   · make_prism      an extruded polygon on any axis — L-plans,
#                     hexagons, car side-profiles, W-beam guardrails,
#                     stair stringers, road segments at a yaw
#   · make_tube       a polyline swept with a ring — wires with sag,
#                     pipes, handrails, hoses, branches, chains
#   · make_rot_box    a box with yaw + pitch + roll — leaning posts,
#                     slumped roofs, open doors, planks on the ground
#   · make_heightfield a grid of heights — lawns that roll, ditches,
#                     dunes, the ground under everything
# Each one is registered in the audit recorder (locale_geometry_audit
# _RECORDERS) with its bounding box; an unregistered primitive is
# invisible to every gate.
# ════════════════════════════════════════════════════════════════

def _gen_lathe(center, profile, segments, loop=False):
    """profile: [(radius, z_offset), ...] bottom→top, z relative to
    center z. A zero radius at an end closes it to a point. loop=True
    joins the last ring back to the first (a torus — a steering
    wheel, a footring, a tire from a section profile) and skips the
    caps."""
    cx, cy, cz = center
    rings = []
    verts = []
    for (r, dz) in profile:
        if r <= 1e-6:
            rings.append([len(verts)])
            verts.append((cx, cy, cz + dz))
        else:
            ring = []
            for s in range(segments):
                th = 2.0 * math.pi * s / segments
                ring.append(len(verts))
                verts.append((cx + r * math.cos(th), cy + r * math.sin(th), cz + dz))
            rings.append(ring)
    faces = []
    for a, b in zip(rings, rings[1:]):
        if len(a) == 1 and len(b) == 1:
            continue
        if len(a) == 1:
            for s in range(segments):
                faces.append([a[0], b[(s + 1) % segments], b[s]])
        elif len(b) == 1:
            for s in range(segments):
                faces.append([a[s], a[(s + 1) % segments], b[0]])
        else:
            for s in range(segments):
                ns = (s + 1) % segments
                faces.append([a[s], a[ns], b[ns], b[s]])
    if loop and len(rings[0]) > 1 and len(rings[-1]) > 1:
        a, b = rings[-1], rings[0]
        for s in range(segments):
            ns = (s + 1) % segments
            faces.append([a[s], a[ns], b[ns], b[s]])
        return verts, faces
    # caps where the profile starts / ends open
    if len(rings[0]) > 1:
        faces.append(list(reversed(rings[0])))
    if len(rings[-1]) > 1:
        faces.append(list(rings[-1]))
    return verts, faces


def make_lathe(name, center, profile, base_color, segments=12, yaw=0.0, loop=False):
    """Revolve `profile` ([(radius, z_off), ...] bottom→top, z_off
    relative to center) about the vertical through `center`. The
    bottle, the basin, the post with a cap, the tire, the shade.
    loop=True makes a torus from a closed section profile."""
    verts, faces = _gen_lathe(center, profile, segments, loop)
    verts = _yaw_rot(verts, center, yaw)
    return _finalize_mesh(name, verts, _fix_winding(verts, faces, center), base_color)


def _gen_prism(center, polygon, length, axis):
    """polygon: [(u, v), ...] in the plane perpendicular to `axis`
    (counter-clockwise), relative to center; the prism runs
    ±length/2 along the axis. Plane mapping:
      axis Z: (u, v) → (x, y)      axis X: (u, v) → (y, z)
      axis Y: (u, v) → (x, z)"""
    cx, cy, cz = center
    n = len(polygon)
    h = length / 2.0
    def pt(u, v, w):
        if axis == "Z":
            return (cx + u, cy + v, cz + w)
        if axis == "X":
            return (cx + w, cy + u, cz + v)
        return (cx + u, cy + w, cz + v)
    verts = [pt(u, v, -h) for (u, v) in polygon] + [pt(u, v, h) for (u, v) in polygon]
    faces = [list(range(n)), list(range(n, 2 * n))]
    for i in range(n):
        j = (i + 1) % n
        faces.append([i, j, n + j, n + i])
    return verts, faces


def make_prism(name, center, polygon, length, base_color, axis="Z", yaw=0.0):
    """Extrude a polygon along `axis`. Any footprint (L-plans, bays,
    hexagons), any side profile (a car body, a W-beam, a stair
    stringer, a roof with eaves) becomes one solid. Concave polygons
    render fine in Godot's importer (Blender triangulates n-gons);
    keep them simple (< 24 points) and counter-clockwise."""
    verts, faces = _gen_prism(center, polygon, length, axis.upper())
    verts = _yaw_rot(verts, center, yaw)
    return _finalize_mesh(name, verts, _fix_winding(verts, faces, center), base_color)


def _gen_tube(path, radius, segments):
    """Sweep a `segments`-gon ring along the polyline `path`."""
    def sub(a, b): return (a[0] - b[0], a[1] - b[1], a[2] - b[2])
    def add(a, b): return (a[0] + b[0], a[1] + b[1], a[2] + b[2])
    def mul(a, k): return (a[0] * k, a[1] * k, a[2] * k)
    def norm(a):
        l = math.sqrt(a[0] ** 2 + a[1] ** 2 + a[2] ** 2) or 1.0
        return (a[0] / l, a[1] / l, a[2] / l)
    def cross(a, b):
        return (a[1] * b[2] - a[2] * b[1], a[2] * b[0] - a[0] * b[2], a[0] * b[1] - a[1] * b[0])
    verts, rings = [], []
    n = len(path)
    for i, p in enumerate(path):
        t = norm(sub(path[min(i + 1, n - 1)], path[max(i - 1, 0)]))
        up = (0.0, 0.0, 1.0) if abs(t[2]) < 0.9 else (1.0, 0.0, 0.0)
        u = norm(cross(t, up))
        v = cross(u, t)
        ring = []
        for s in range(segments):
            th = 2.0 * math.pi * s / segments
            off = add(mul(u, radius * math.cos(th)), mul(v, radius * math.sin(th)))
            ring.append(len(verts))
            verts.append(add(p, off))
        rings.append(ring)
    faces = []
    for a, b in zip(rings, rings[1:]):
        for s in range(segments):
            ns = (s + 1) % segments
            faces.append([a[s], a[ns], b[ns], b[s]])
    faces.append(list(reversed(rings[0])))
    faces.append(list(rings[-1]))
    return verts, faces


def make_tube(name, path, radius, base_color, segments=6):
    """A polyline swept with a ring. Wires (build the sag into the
    path with `catenary`), pipes, conduit, handrails, hoses, branches,
    chains, cables — anything that is a LINE with thickness."""
    verts, faces = _gen_tube(path, radius, segments)
    c = (sum(p[0] for p in path) / len(path), sum(p[1] for p in path) / len(path),
         sum(p[2] for p in path) / len(path))
    return _finalize_mesh(name, verts, _fix_winding(verts, faces, c), base_color)


def catenary(a, b, sag, n=8):
    """A path from point a to point b that hangs by `sag` at the
    middle — wires between poles, a chain across a road, a clothesline."""
    out = []
    for i in range(n + 1):
        t = i / n
        x = a[0] + (b[0] - a[0]) * t
        y = a[1] + (b[1] - a[1]) * t
        z = a[2] + (b[2] - a[2]) * t - sag * (1.0 - (2.0 * t - 1.0) ** 2)
        out.append((x, y, z))
    return out


def _rot3(verts, center, yaw, pitch, roll):
    cx, cy, cz = center
    cy_, sy_ = math.cos(yaw), math.sin(yaw)
    cp, sp = math.cos(pitch), math.sin(pitch)
    cr, sr = math.cos(roll), math.sin(roll)
    out = []
    for (x, y, z) in verts:
        dx, dy, dz = x - cx, y - cy, z - cz
        # roll about local X, pitch about local Y, yaw about Z
        dy, dz = dy * cr - dz * sr, dy * sr + dz * cr
        dx, dz = dx * cp + dz * sp, -dx * sp + dz * cp
        dx, dy = dx * cy_ - dy * sy_, dx * sy_ + dy * cy_
        out.append((cx + dx, cy + dy, cz + dz))
    return out


def make_rot_box(name, center, size, base_color, yaw=0.0, pitch=0.0, roll=0.0):
    """A box turned on any axis. The leaning fence post, the plank on
    the ground, the roof slab slumped into the ruin, the door standing
    open at forty degrees, the ladder against the wall."""
    cx, cy, cz = center
    hx, hy, hz = size[0] / 2.0, size[1] / 2.0, size[2] / 2.0
    verts = [(cx - hx, cy - hy, cz - hz), (cx + hx, cy - hy, cz - hz),
             (cx + hx, cy + hy, cz - hz), (cx - hx, cy + hy, cz - hz),
             (cx - hx, cy - hy, cz + hz), (cx + hx, cy - hy, cz + hz),
             (cx + hx, cy + hy, cz + hz), (cx - hx, cy + hy, cz + hz)]
    faces = [[0, 1, 2, 3], [4, 5, 6, 7], [0, 1, 5, 4], [1, 2, 6, 5], [2, 3, 7, 6], [3, 0, 4, 7]]
    verts = _rot3(verts, center, yaw, pitch, roll)
    return _finalize_mesh(name, verts, _fix_winding(verts, faces, center), base_color)


def rot_box_bbox(center, size, yaw=0.0, pitch=0.0, roll=0.0):
    """Axis-aligned half-extents of a rotated box (for the audits)."""
    cx, cy, cz = center
    hx, hy, hz = size[0] / 2.0, size[1] / 2.0, size[2] / 2.0
    corners = [(cx + i * hx, cy + j * hy, cz + k * hz) for i in (-1, 1) for j in (-1, 1) for k in (-1, 1)]
    r = _rot3(corners, center, yaw, pitch, roll)
    return (max(abs(v[0] - cx) for v in r), max(abs(v[1] - cy) for v in r), max(abs(v[2] - cz) for v in r))


def _gen_heightfield(origin, cell, heights, skirt):
    """heights[row][col] = z at (origin.x + col*cell, origin.y +
    row*cell). A skirt drops the rim to origin.z - skirt so the
    patch has no visible knife edge."""
    ox, oy, oz = origin
    rows, cols = len(heights), len(heights[0])
    verts = []
    for r in range(rows):
        for c in range(cols):
            verts.append((ox + c * cell, oy + r * cell, oz + heights[r][c]))
    faces = []
    for r in range(rows - 1):
        for c in range(cols - 1):
            a = r * cols + c
            faces.append([a, a + 1, a + cols + 1, a + cols])
    if skirt > 0.0:
        base = len(verts)
        rim = []
        for c in range(cols): rim.append((0, c))
        for r in range(1, rows): rim.append((r, cols - 1))
        for c in range(cols - 2, -1, -1): rim.append((rows - 1, c))
        for r in range(rows - 2, 0, -1): rim.append((r, 0))
        for (r, c) in rim:
            verts.append((ox + c * cell, oy + r * cell, oz - skirt))
        m = len(rim)
        for i in range(m):
            (r0, c0), (r1, c1) = rim[i], rim[(i + 1) % m]
            faces.append([r0 * cols + c0, r1 * cols + c1, base + (i + 1) % m, base + i])
        faces.append([base + i for i in range(m - 1, -1, -1)])
    return verts, faces


def make_heightfield(name, origin, cell, heights, base_color, skirt=0.3):
    """A rolling surface from a grid of heights. `origin` is the SW
    corner (x, y, base z); `heights` is rows (y) of cols (x). Lawns
    that are not planes, bar ditches, dunes, the shoulder that falls
    away, the ground under a whole set."""
    verts, faces = _gen_heightfield(origin, cell, heights, skirt)
    rows, cols = len(heights), len(heights[0])
    c = (origin[0] + (cols - 1) * cell / 2.0, origin[1] + (rows - 1) * cell / 2.0, origin[2])
    return _finalize_mesh(name, verts, faces, base_color)


def heightfield_bbox(origin, cell, heights, skirt=0.3):
    rows, cols = len(heights), len(heights[0])
    zs = [h for row in heights for h in row]
    lo, hi = min(zs), max(zs)
    cx = origin[0] + (cols - 1) * cell / 2.0
    cy = origin[1] + (rows - 1) * cell / 2.0
    cz = origin[2] + (hi + (lo - skirt)) / 2.0
    return ((cx, cy, cz), ((cols - 1) * cell / 2.0, (rows - 1) * cell / 2.0, (hi - (lo - skirt)) / 2.0))


def rolling_heights(rows, cols, amp, seed=0, base=0.0, bumps=3):
    """A deterministic gently-rolling height grid (sum of a few
    cosines + hashed noise) for make_heightfield."""
    out = []
    for r in range(rows):
        row = []
        for c in range(cols):
            z = base
            for k in range(1, bumps + 1):
                z += amp / k * (math.cos(0.9 * k * c / max(cols - 1, 1) * math.pi * 2 + seed + k) *
                                math.sin(0.7 * k * r / max(rows - 1, 1) * math.pi * 2 + seed * 0.7))
            z += (_h01g(r, c, seed) - 0.5) * amp * 0.25
            row.append(z)
        out.append(row)
    return out
