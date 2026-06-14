"""
build_riverfront.py
══════════════════════════════════════════════════════════════════
VOL 5 SHARED LOCALE · the D'Ambrosio's riverfront environment.

The full exterior context around the boat — used by:
  · the Fool (the diner is moored here)
  · the Empress (Nicola's floor, same boat interior)
  · the Emperor (Dante's helm, on the boat's upper deck)
  · the Hierophant (Paul arrives via the parking lot)
  · vol 6 reference (the boat is GONE in vol6 canon — the
    ghost site is here, just dock pilings at low tide; this
    GLB ships the WITH-boat version, vol6 can hide the boat
    node to render the post-Sinkhole state)

Builds:
  · the riverboat exterior (clapboard hull, brass rails, paddle-
    wheel, smokestack, wraparound porch, gangway, upper deck
    with the helm cabin where Dante sat)
  · the parking lot adjacent to the boat (asphalt, painted lines,
    sodium streetlight, a few parked cars)
  · the river water plane underneath and extending to opposite
    shore
  · the opposite shoreline (strip of land, cypress trees, a few
    far industrial buildings)
  · 2-3 other boats scattered in the river (tugboats, fishing
    skiffs)
  · the bayou section (cypress trees in swamp water, Spanish
    moss hint, a small pier)

"Basic for now, fill out later" per the user. Geometry is rough
primitives; vertex colors carry material identifiers.

Run:
    blender --background --python build_riverfront.py
    (or ./run_cathedral.sh build_riverfront.py)

Output:
    godot/assets/3d/locales/riverfront.glb
"""

import bpy
import math
import os
import sys
from mathutils import Vector

# Allow `import cursive_type` from the same directory (Blender's -P
# does not auto-add the script's directory to sys.path).
_SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
if _SCRIPT_DIR not in sys.path:
    sys.path.insert(0, _SCRIPT_DIR)
import cursive_type

OUTPUT_DIR = "../../../assets/3d/locales"
OUTPUT_NAME = "riverfront.glb"

# ── world layout (Blender coords; Godot import rotates Z-up to Y-up) ──

# Boat sits at origin. North (+Y) is upriver. South (-Y) is the parking lot.
# West (-X) is the open river → opposite shore far -X. East (+X) is the bayou.

BOAT_W = 12.0   # boat width (east-west, perpendicular to river current)
BOAT_L = 24.0   # boat length (north-south, along the river)
BOAT_HULL_H = 1.8
DECK_H = 0.5
HELM_W = 5.0
HELM_L = 4.5
HELM_H = 2.6

# LAYOUT — the boat sits PARALLEL to the shoreline, moored alongside.
# Bow at +Y (north / upriver), stern at -Y (south / downriver).
# Paddle wheel hangs off the stern. The boat's PORT (left, -X) side
# faces the shore where the parking lot and dock are. The boat's
# STARBOARD (right, +X) side faces the open river toward the opposite
# shore. The bayou is up-river on the starboard side.

PARKING_X = -BOAT_W / 2 - 18.0    # parking lot 18m west of boat (port)
PARKING_Y_CENTER = 0.0            # parking lot lined up with boat center
RIVER_LEVEL_Z = -0.3

OPPOSITE_X = 120.0    # far starboard shore (east, across the wide river)
BAYOU_X = 55.0        # bayou pushed back so the river has a real lane
BRIDGE_Y = -95.0      # distant bridge downriver to the south
DOCK_Z = 0.35         # dock deck sits 35cm above the water surface
# River traffic lane: between boat (X≈±6) and bayou tree-line (X≈37),
# there are ~30m of clear water — wide enough for two riverboats to
# pass alongside D'Ambrosio's at the same time.

# ── palette ──
COL_HULL          = (0.82, 0.78, 0.66, 1.0)    # white clapboard, aged
COL_HULL_BAND     = (0.50, 0.20, 0.16, 1.0)    # the red trim band along the hull
COL_DECK_WOOD     = (0.42, 0.30, 0.20, 1.0)
COL_BRASS         = (0.78, 0.58, 0.26, 1.0)
COL_PADDLE_HOUSING= (0.50, 0.18, 0.14, 1.0)    # red paddle-wheel housing (signature)
COL_PADDLE_BLADES = (0.50, 0.35, 0.22, 1.0)    # weathered wood blades
COL_SMOKESTACK    = (0.28, 0.22, 0.16, 1.0)
COL_ROOF          = (0.30, 0.24, 0.18, 1.0)    # roof shingles
COL_HELM_WALL     = (0.62, 0.50, 0.34, 1.0)    # the small wooden helm cabin
COL_HELM_ROOF     = (0.22, 0.18, 0.14, 1.0)
COL_HELM_WINDOW   = (0.50, 0.40, 0.32, 1.0)    # window in dim warm interior light
COL_ASPHALT       = (0.18, 0.18, 0.18, 1.0)
COL_PAINT_LINE    = (0.65, 0.62, 0.45, 1.0)    # faded yellow parking lines
COL_SODIUM_POLE   = (0.20, 0.18, 0.14, 1.0)
COL_SODIUM_HEAD   = (0.92, 0.62, 0.30, 1.0)
COL_CAR_BODY_A    = (0.32, 0.30, 0.34, 1.0)    # grey car
COL_CAR_BODY_B    = (0.40, 0.22, 0.18, 1.0)    # dark red car
COL_CAR_BODY_C    = (0.62, 0.52, 0.30, 1.0)    # gold/beige car
COL_CAR_GLASS     = (0.18, 0.20, 0.24, 1.0)
COL_RIVER         = (0.28, 0.40, 0.50, 1.0)    # warm muddy gulf-coast river
COL_BAYOU_WATER   = (0.20, 0.28, 0.22, 1.0)    # tannin-stained swampwater
COL_SHORELINE     = (0.32, 0.26, 0.18, 1.0)
COL_TREE_TRUNK    = (0.22, 0.16, 0.10, 1.0)
COL_TREE_CANOPY_A = (0.20, 0.32, 0.18, 1.0)    # pine green
COL_TREE_CANOPY_B = (0.30, 0.38, 0.22, 1.0)    # cypress lighter green
COL_MOSS          = (0.55, 0.52, 0.36, 1.0)    # Spanish moss
COL_FAR_BUILDING  = (0.42, 0.40, 0.36, 1.0)    # weathered industrial
COL_OTHER_BOAT_A  = (0.62, 0.50, 0.34, 1.0)    # tugboat
COL_OTHER_BOAT_B  = (0.38, 0.32, 0.24, 1.0)    # fishing skiff
COL_PIER_WOOD     = (0.40, 0.28, 0.18, 1.0)


# ── helpers ──

def clear_scene():
    bpy.ops.object.select_all(action='SELECT')
    bpy.ops.object.delete(use_global=False)
    for c in (bpy.data.meshes, bpy.data.materials, bpy.data.images):
        for item in list(c):
            if item.users == 0:
                c.remove(item)


def make_box(name, center, size, base_color, open_faces=None):
    open_faces = open_faces or set()
    cx, cy, cz = center
    sx, sy, sz = size
    hx, hy, hz = sx/2, sy/2, sz/2
    verts = [
        (cx-hx, cy-hy, cz-hz), (cx+hx, cy-hy, cz-hz),
        (cx+hx, cy+hy, cz-hz), (cx-hx, cy+hy, cz-hz),
        (cx-hx, cy-hy, cz+hz), (cx+hx, cy-hy, cz+hz),
        (cx+hx, cy+hy, cz+hz), (cx-hx, cy+hy, cz+hz),
    ]
    face_defs = [
        ('-Z', (0,3,2,1), ( 0, 0,-1)),
        ('+Z', (4,5,6,7), ( 0, 0, 1)),
        ('-Y', (0,1,5,4), ( 0,-1, 0)),
        ('+Y', (2,3,7,6), ( 0, 1, 0)),
        ('-X', (3,0,4,7), (-1, 0, 0)),
        ('+X', (1,2,6,5), ( 1, 0, 0)),
    ]
    mesh = bpy.data.meshes.new(name + "_mesh")
    out_verts, out_faces, out_colors = [], [], []
    vmap = {}
    def vidx(v_orig, normal):
        key = (v_orig, tuple(normal))
        if key in vmap: return vmap[key]
        idx = len(out_verts)
        out_verts.append(verts[v_orig])
        out_colors.append(base_color)
        vmap[key] = idx
        return idx
    for tag, vids, normal in face_defs:
        if tag in open_faces: continue
        out_faces.append([vidx(v, normal) for v in vids])
    mesh.from_pydata(out_verts, [], out_faces)
    mesh.update()
    if not mesh.vertex_colors:
        mesh.vertex_colors.new(name="Col")
    layer = mesh.vertex_colors["Col"]
    for poly in mesh.polygons:
        for li in poly.loop_indices:
            v = mesh.loops[li].vertex_index
            layer.data[li].color = out_colors[v]
    obj = bpy.data.objects.new(name, mesh)
    bpy.context.collection.objects.link(obj)
    return obj


def make_cyl(name, center, radius, height, base_color, segments=8, axis='Z', caps=True):
    """Lowpoly cylinder (PS2-era). Default 8 segments — keep it chunky.
    axis='Z' (vertical), 'Y' or 'X' for horizontal."""
    cx, cy, cz = center
    h2 = height / 2.0
    verts = []
    # build the two rings
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
            else:  # 'X'
                verts.append((cx + z_off, cy + a, cz + b))
    faces = []
    # side quads
    for i in range(segments):
        ni = (i + 1) % segments
        bot_a = i
        bot_b = ni
        top_a = i + segments
        top_b = ni + segments
        faces.append([bot_a, bot_b, top_b, top_a])
    # caps
    if caps:
        bot_ring = list(range(segments))
        top_ring = list(range(segments, segments * 2))
        # bottom cap (reverse winding so it faces -axis)
        faces.append(list(reversed(bot_ring)))
        # top cap
        faces.append(top_ring)
    return _finalize_mesh(name, verts, faces, base_color)


def make_prism(name, center, size, base_color, pitch_axis='Y'):
    """Triangular prism (sloped roof). The triangle cross-section lies
    in the X-Z plane by default (pitch_axis='Y'); a peak runs along Y.
    size = (width, length, peak_height)."""
    cx, cy, cz = center
    sx, sy, sz = size
    hx, hy = sx / 2.0, sy / 2.0
    # 6 verts: rectangular base + ridge line at the top center
    base_z = cz
    peak_z = cz + sz
    if pitch_axis == 'Y':
        verts = [
            (cx - hx, cy - hy, base_z),  # 0
            (cx + hx, cy - hy, base_z),  # 1
            (cx + hx, cy + hy, base_z),  # 2
            (cx - hx, cy + hy, base_z),  # 3
            (cx, cy - hy, peak_z),       # 4 ridge south
            (cx, cy + hy, peak_z),       # 5 ridge north
        ]
        faces = [
            [0, 3, 2, 1],   # base
            [0, 1, 4],      # south triangle
            [3, 5, 2],      # north triangle (note winding so normal faces +Y)
            [0, 4, 5, 3],   # west slope
            [1, 2, 5, 4],   # east slope
        ]
    else:  # pitch_axis == 'X'
        verts = [
            (cx - hx, cy - hy, base_z),
            (cx + hx, cy - hy, base_z),
            (cx + hx, cy + hy, base_z),
            (cx - hx, cy + hy, base_z),
            (cx - hx, cy, peak_z),
            (cx + hx, cy, peak_z),
        ]
        faces = [
            [0, 3, 2, 1],
            [0, 3, 4],
            [1, 5, 2],
            [0, 4, 5, 1],
            [3, 2, 5, 4],
        ]
    return _finalize_mesh(name, verts, faces, base_color)


def make_ramp(name, start_top, end_top, width, thickness, base_color, width_axis='Y'):
    """A sloped plank running from start_top to end_top, with given
    perpendicular width and bottom thickness. The 'top' surface goes
    from start_top to end_top in 3D. width_axis selects which axis the
    width spans ('X' or 'Y'); the other and Z carry the slope.

    Used for gangways and ramps — anywhere a flat plank tilts between
    two heights (real-world gangways slope ~15-25° from horizontal)."""
    sx, sy, sz = start_top
    ex, ey, ez = end_top
    hw = width / 2.0
    if width_axis == 'Y':
        verts = [
            (sx, sy - hw, sz - thickness),  # 0 — start bottom -Y
            (ex, ey - hw, ez - thickness),  # 1 — end   bottom -Y
            (ex, ey + hw, ez - thickness),  # 2 — end   bottom +Y
            (sx, sy + hw, sz - thickness),  # 3 — start bottom +Y
            (sx, sy - hw, sz),              # 4 — start top    -Y
            (ex, ey - hw, ez),              # 5 — end   top    -Y
            (ex, ey + hw, ez),              # 6 — end   top    +Y
            (sx, sy + hw, sz),              # 7 — start top    +Y
        ]
    else:  # 'X'
        verts = [
            (sx - hw, sy, sz - thickness),
            (ex - hw, ey, ez - thickness),
            (ex + hw, ey, ez - thickness),
            (sx + hw, sy, sz - thickness),
            (sx - hw, sy, sz),
            (ex - hw, ey, ez),
            (ex + hw, ey, ez),
            (sx + hw, sy, sz),
        ]
    faces = [
        [0, 3, 2, 1],   # bottom
        [4, 5, 6, 7],   # top
        [0, 1, 5, 4],   # one side
        [2, 3, 7, 6],   # other side
        [1, 2, 6, 5],   # downhill end
        [3, 0, 4, 7],   # uphill end
    ]
    return _finalize_mesh(name, verts, faces, base_color)


def make_sphere(name, center, radius, base_color, subdivisions=0):
    """Lowpoly sphere via icosahedron (12 verts, 20 faces). subdivisions
    > 0 subdivides each triangle into 4 — 1 = 42 verts/80 faces, 2 =
    162 verts/320 faces. For PS2-era clouds/canopies subdivisions=0 is
    plenty.

    Returns an organic round mesh, the opposite of a box. Use for
    clouds, foliage canopies, bulb shapes, anything that should NOT
    read as cubic."""
    cx, cy, cz = center
    t = (1.0 + math.sqrt(5.0)) / 2.0
    raw = [
        (-1.0,    t,  0.0), ( 1.0,    t,  0.0),
        (-1.0,   -t,  0.0), ( 1.0,   -t,  0.0),
        ( 0.0, -1.0,    t), ( 0.0,  1.0,    t),
        ( 0.0, -1.0,   -t), ( 0.0,  1.0,   -t),
        (   t,  0.0, -1.0), (   t,  0.0,  1.0),
        (  -t,  0.0, -1.0), (  -t,  0.0,  1.0),
    ]
    norm = radius / math.sqrt(1.0 + t * t)
    verts = [(cx + v[0] * norm, cy + v[1] * norm, cz + v[2] * norm) for v in raw]
    faces = [
        [0, 11,  5], [0,  5,  1], [0,  1,  7], [0,  7, 10], [0, 10, 11],
        [1,  5,  9], [5, 11,  4], [11, 10, 2], [10, 7,  6], [7,  1,  8],
        [3,  9,  4], [3,  4,  2], [3,  2,  6], [3,  6,  8], [3,  8,  9],
        [4,  9,  5], [2,  4, 11], [6,  2, 10], [8,  6,  7], [9,  8,  1],
    ]
    # Subdivide if requested — each triangle becomes 4 smaller triangles
    for _ in range(subdivisions):
        new_verts = list(verts)
        edge_mid = {}
        def mid(a, b):
            key = (min(a, b), max(a, b))
            if key in edge_mid:
                return edge_mid[key]
            va = verts[a]
            vb = verts[b]
            mx = (va[0] + vb[0]) / 2.0
            my = (va[1] + vb[1]) / 2.0
            mz = (va[2] + vb[2]) / 2.0
            # project back onto sphere surface
            dx = mx - cx
            dy = my - cy
            dz = mz - cz
            r = math.sqrt(dx * dx + dy * dy + dz * dz)
            scale = radius / r if r > 0 else 1.0
            new_verts.append((cx + dx * scale, cy + dy * scale, cz + dz * scale))
            idx = len(new_verts) - 1
            edge_mid[key] = idx
            return idx
        new_faces = []
        for (a, b, c) in faces:
            ab = mid(a, b)
            bc = mid(b, c)
            ca = mid(c, a)
            new_faces.append([a,  ab, ca])
            new_faces.append([b,  bc, ab])
            new_faces.append([c,  ca, bc])
            new_faces.append([ab, bc, ca])
        verts = new_verts
        faces = new_faces
    return _finalize_mesh(name, verts, faces, base_color)


def make_tube_segment(name, p_start, p_end, radius, base_color, segments=6):
    """A cylindrical tube between two arbitrary 3D points. The tube's
    axis follows the line from p_start to p_end with proper orientation
    (no axis-aligned stair-stepping). Used for neon strokes, ropes,
    pipes, anything that needs to draw a diagonal line in 3D."""
    sx, sy, sz = p_start
    ex, ey, ez = p_end
    dx = ex - sx; dy = ey - sy; dz = ez - sz
    length = math.sqrt(dx * dx + dy * dy + dz * dz)
    if length < 0.001:
        return None
    # unit axis along the segment
    ux = dx / length; uy = dy / length; uz = dz / length
    # build two orthogonal perpendicular unit vectors
    if abs(uz) < 0.9:
        # u × (0,0,1)
        p1x = uy * 1.0 - uz * 0.0
        p1y = uz * 0.0 - ux * 1.0
        p1z = ux * 0.0 - uy * 0.0
    else:
        # u × (1,0,0)
        p1x = uy * 0.0 - uz * 0.0
        p1y = uz * 1.0 - ux * 0.0
        p1z = ux * 0.0 - uy * 1.0
    p1_len = math.sqrt(p1x * p1x + p1y * p1y + p1z * p1z)
    if p1_len < 1e-6:
        return None
    p1x /= p1_len; p1y /= p1_len; p1z /= p1_len
    # p2 = u × p1
    p2x = uy * p1z - uz * p1y
    p2y = uz * p1x - ux * p1z
    p2z = ux * p1y - uy * p1x
    verts = []
    for end_idx in (0, 1):
        ex_, ey_, ez_ = (sx, sy, sz) if end_idx == 0 else (ex, ey, ez)
        for i in range(segments):
            ang = 2.0 * math.pi * i / segments
            ca = math.cos(ang); sa = math.sin(ang)
            offx = (p1x * ca + p2x * sa) * radius
            offy = (p1y * ca + p2y * sa) * radius
            offz = (p1z * ca + p2z * sa) * radius
            verts.append((ex_ + offx, ey_ + offy, ez_ + offz))
    faces = []
    for i in range(segments):
        ni = (i + 1) % segments
        faces.append([i, ni, ni + segments, i + segments])
    faces.append(list(reversed(range(segments))))         # start cap
    faces.append(list(range(segments, segments * 2)))     # end cap
    return _finalize_mesh(name, verts, faces, base_color)


def make_torus(name, center, major_r, minor_r, base_color,
               major_seg=12, minor_seg=6, axis='Z'):
    """A torus — major_r is the radius of the ring centre, minor_r is
    the cross-section radius of the tube itself. axis='Z' means the
    ring lies flat in the X-Y plane (ring through which a vertical
    pole could pass). 'X' / 'Y' rotate that orientation."""
    cx, cy, cz = center
    verts = []
    for i in range(major_seg):
        u = 2.0 * math.pi * i / major_seg
        cu = math.cos(u); su = math.sin(u)
        for j in range(minor_seg):
            v = 2.0 * math.pi * j / minor_seg
            cv = math.cos(v); sv = math.sin(v)
            r_off = major_r + minor_r * cv
            tube_h = minor_r * sv
            if axis == 'Z':
                px = cx + r_off * cu; py = cy + r_off * su; pz = cz + tube_h
            elif axis == 'Y':
                px = cx + r_off * cu; py = cy + tube_h;     pz = cz + r_off * su
            else:  # 'X'
                px = cx + tube_h;     py = cy + r_off * cu; pz = cz + r_off * su
            verts.append((px, py, pz))
    faces = []
    for i in range(major_seg):
        ni = (i + 1) % major_seg
        for j in range(minor_seg):
            nj = (j + 1) % minor_seg
            a = i  * minor_seg + j
            b = ni * minor_seg + j
            c = ni * minor_seg + nj
            d = i  * minor_seg + nj
            faces.append([a, b, c, d])
    return _finalize_mesh(name, verts, faces, base_color)


def make_neon_dambrosios(label, panel_center, face_axis, face_sign, scale=1.0):
    """Draw cursive 'D'Ambrosio's' red neon on a sign panel face,
    using the Bezier-based cursive_type tool for smooth curves and
    proper kerning.

    panel_center: (x, y, z) world position of the panel face centre.
    face_axis: 'Y' if the panel normal points along ±Y, 'X' for ±X.
    face_sign: +1 or -1 — direction along face_axis the face points.
    scale: overall size multiplier.
    """
    NEON_RED = (1.0, 0.18, 0.20, 1.0)
    NEON_GLOW = (1.0, 0.35, 0.40, 1.0)
    TUBE_R = 0.060 * scale
    H = 0.65 * scale         # capital height
    cx, cy, cz = panel_center

    def lx(local_x):
        # Mirror so text reads correctly from the viewer of THIS face.
        # 'Y' panel: viewer-left = +X * sign(face). 'X' panel:
        # viewer-left = +Y * (-sign(face)). Different formulae.
        if face_axis == 'Y':
            return -local_x * face_sign
        else:  # 'X'
            return local_x * face_sign

    def _place(panel_x, panel_z, normal_off=0.0):
        if face_axis == 'Y':
            return (cx + lx(panel_x), cy + face_sign * normal_off, cz + panel_z)
        else:
            return (cx + face_sign * normal_off, cy + lx(panel_x), cz + panel_z)

    # cursive_type's draw_tube callback — converts panel-local (x, z)
    # endpoints into world coords via _place(), then emits a tube
    def draw_tube(name, a, b):
        p1 = _place(a[0], a[1], 0.0)
        p2 = _place(b[0], b[1], 0.0)
        make_tube_segment(f"Neon_{label}_{name}", p1, p2, TUBE_R, NEON_RED, segments=5)

    text = "D'Ambrosio's"
    # Centre the text horizontally on the panel: compute its width,
    # start at -width/2 so the midpoint lands at panel_x = 0.
    text_w = cursive_type.text_width(text, cap_height=H, kerning=0.04)
    text_start_x = -text_w / 2.0
    baseline_z = 0.0
    pen_end_x = cursive_type.render_text(
        text, text_start_x, baseline_z, H, draw_tube,
        samples_per_segment=8, kerning=0.04, name_prefix=label,
    )

    # Underline swoosh — proper downward arc beneath the baseline.
    # Spans the full text plus a little margin on each side.
    u_left = text_start_x - 0.10
    u_right = pen_end_x + 0.05
    u_dip = 0.20 * scale
    N_u = 32
    for i in range(N_u):
        t0 = i / N_u
        t1 = (i + 1) / N_u
        ux0 = u_left + t0 * (u_right - u_left)
        ux1 = u_left + t1 * (u_right - u_left)
        uz0 = -0.10 * scale - math.sin(t0 * math.pi) * u_dip
        uz1 = -0.10 * scale - math.sin(t1 * math.pi) * u_dip
        p1 = _place(ux0, uz0, 0.0)
        p2 = _place(ux1, uz1, 0.0)
        make_tube_segment(f"Neon_{label}_underline_{i}", p1, p2,
                          TUBE_R * 0.85, NEON_RED, segments=5)

    # Halo glow spheres behind major letter loops (D, A, m, b, o, o)
    # placed slightly INSET toward the panel face so they bloom behind
    # the tubes, not in front. Positions are approximate centers of
    # each major loop computed from the text layout.
    halo_positions = []
    pen_x = text_start_x
    for ch in text:
        if ch in ('D', 'A', 'm', 'b', 'o'):
            glyph = cursive_type.GLYPHS.get(ch)
            if glyph:
                halo_positions.append((pen_x + glyph['advance'] * H * 0.5,
                                       H * 0.45))
        glyph = cursive_type.GLYPHS.get(ch)
        if glyph:
            pen_x += glyph['advance'] * H + 0.04 * H
    for hi, (hx_, hz_) in enumerate(halo_positions):
        pos = _place(hx_, hz_, -0.020)
        make_sphere(f"Neon_{label}_halo_{hi}", pos, 0.18 * scale, NEON_GLOW)


def _finalize_mesh(name, verts, faces, base_color):
    """Build a mesh from verts/faces (already in world coords) with
    flat per-loop vertex colour = base_color."""
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


# ════════════════════════════════════════════════════════════════
# THE RIVERBOAT EXTERIOR
# ════════════════════════════════════════════════════════════════

def build_riverboat():
    """A proper Mississippi paddle-wheeler at PS2 polycount.

    Three stacked decks (boiler / saloon / hurricane) + pilothouse on
    top + paired forward smokestacks + stern paddle wheel. Banks of
    arched windows on every cabin face, gingerbread arches between
    every column, decorative cresting along every roofline.

    Floor plan (Blender +Y is forward / bow, -Y is aft / stern):
        Z 14m  pilothouse roof crest + finial
        Z 12m  pilothouse
        Z 10m  smokestack tops + cresting
        Z  9m  hurricane deck (top open promenade)
        Z  6m  saloon deck (second cabin)
        Z  3m  boiler deck (main dining + porches all around)
        Z  0m  waterline
        Z -2m  paddle wheel + housing astern
    """

    # ── colour additions for the proper Mark-Twain era trim ──────
    col_gingerbread = (0.78, 0.72, 0.58, 1.0)   # ornate cream fretwork
    col_window_warm = (0.92, 0.78, 0.42, 1.0)   # warm lit interior windows
    col_window_dark = (0.32, 0.36, 0.42, 1.0)   # unlit windows
    col_crest      = (0.55, 0.20, 0.16, 1.0)    # red roof cresting
    col_column     = (0.85, 0.82, 0.72, 1.0)    # white column shafts

    # ════════════════════════════════════════════════════════════
    # HULL — beveled, three-tier, with prow taper
    # ════════════════════════════════════════════════════════════
    h0_z = RIVER_LEVEL_Z + 0.35
    make_box("Hull_Lower", (0, 0, h0_z), (BOAT_W + 0.40, BOAT_L + 0.30, 0.70), COL_HULL)
    h1_z = RIVER_LEVEL_Z + 0.95
    make_box("Hull_Mid",   (0, 0, h1_z), (BOAT_W,        BOAT_L,        0.50), COL_HULL)
    h2_z = RIVER_LEVEL_Z + 1.45
    make_box("Hull_Upper", (0, 0, h2_z), (BOAT_W - 0.40, BOAT_L - 0.30, 0.50), COL_HULL)
    # Prow taper — three stepped narrower boxes extending past +Y end
    bow_y = BOAT_L / 2
    for i, (frac, off_y) in enumerate([(0.85, 0.6), (0.60, 1.3), (0.30, 1.9)]):
        make_box(f"Hull_Bow_{i}", (0, bow_y + off_y, h1_z),
                 (BOAT_W * frac, 0.7, 0.85), COL_HULL)
    # Sternpost (back end taper, less pronounced)
    make_box("Hull_Stern", (0, -bow_y - 0.6, h1_z), (BOAT_W * 0.7, 0.7, 0.85), COL_HULL)

    # Red trim band wrapping the hull
    band_z = RIVER_LEVEL_Z + 1.30
    make_box("Trim_W", (-BOAT_W/2 - 0.03, 0, band_z), (0.08, BOAT_L * 0.98, 0.20), COL_HULL_BAND)
    make_box("Trim_E", ( BOAT_W/2 + 0.03, 0, band_z), (0.08, BOAT_L * 0.98, 0.20), COL_HULL_BAND)
    make_box("Trim_S", (0, -BOAT_L/2 - 0.03, band_z), (BOAT_W * 0.98, 0.08, 0.20), COL_HULL_BAND)
    make_box("Trim_N", (0,  BOAT_L/2 + 0.03, band_z), (BOAT_W * 0.98, 0.08, 0.20), COL_HULL_BAND)
    # Lower trim line nearer the waterline
    make_box("Trim_LowW", (-BOAT_W/2 - 0.03, 0, RIVER_LEVEL_Z + 0.50), (0.06, BOAT_L * 0.95, 0.12), COL_HULL_BAND)
    make_box("Trim_LowE", ( BOAT_W/2 + 0.03, 0, RIVER_LEVEL_Z + 0.50), (0.06, BOAT_L * 0.95, 0.12), COL_HULL_BAND)

    # ════════════════════════════════════════════════════════════
    # BOILER DECK (main / dining-room level) — Z ≈ 1.95
    # The wide platform extends past the hull on all sides; a row of
    # columns supports the saloon deck above with gingerbread arches.
    # ════════════════════════════════════════════════════════════
    BD_W = BOAT_W + 2.0    # 14m wide — extends 1m past hull both sides
    BD_L = BOAT_L + 1.0    # 25m long
    BD_Z = 1.95
    make_box("Boiler_Deck", (0, 0, BD_Z), (BD_W, BD_L, 0.20), COL_DECK_WOOD)
    # Plank stripes
    for i in range(10):
        py = -BD_L/2 + 1.0 + i * (BD_L - 2.0) / 9.0
        make_box(f"Boiler_Plank_{i}", (0, py, BD_Z + 0.105),
                 (BD_W - 0.2, 0.04, 0.01), (0.32, 0.22, 0.14, 1.0))

    # ── DINING-ROOM CABIN (the structure sitting on the boiler deck) ──
    # Narrower than the deck so a wide porch wraps it on all sides.
    DR_W = BOAT_W - 0.6    # 11.4m
    DR_L = BOAT_L - 3.0    # 21m (leaves 1.5m porches fore and aft)
    DR_H = 3.0
    DR_Z = BD_Z + 0.10 + DR_H / 2.0
    make_box("DR_Walls_W", (-DR_W/2, 0, DR_Z), (0.20, DR_L, DR_H), COL_HULL)
    make_box("DR_Walls_E", ( DR_W/2, 0, DR_Z), (0.20, DR_L, DR_H), COL_HULL)
    make_box("DR_Walls_S", (0, -DR_L/2, DR_Z), (DR_W, 0.20, DR_H), COL_HULL)
    make_box("DR_Walls_N", (0,  DR_L/2, DR_Z), (DR_W, 0.20, DR_H), COL_HULL)

    # Arched windows along the east and west sides of the dining room.
    # 10 per side. Each window: a warm glowing pane + a frame ring +
    # a small "arch" cap above.
    n_wins = 10
    win_w = 0.70
    win_h = 1.40
    win_z = DR_Z + 0.20
    for side, sx, normal in (("W", -DR_W/2 - 0.11, -1), ("E",  DR_W/2 + 0.11, 1)):
        for i in range(n_wins):
            wy = -DR_L/2 + 1.2 + i * (DR_L - 2.4) / (n_wins - 1)
            lit = ((i + (0 if side == "W" else 1)) % 3) != 2
            wcol = col_window_warm if lit else col_window_dark
            make_box(f"DR_Win_{side}_{i}",       (sx, wy, win_z), (0.06, win_w, win_h), wcol)
            # frame
            make_box(f"DR_WinFrame_{side}_{i}_L", (sx, wy - win_w/2 - 0.02, win_z),  (0.07, 0.04, win_h + 0.08), COL_HELM_ROOF)
            make_box(f"DR_WinFrame_{side}_{i}_R", (sx, wy + win_w/2 + 0.02, win_z),  (0.07, 0.04, win_h + 0.08), COL_HELM_ROOF)
            make_box(f"DR_WinFrame_{side}_{i}_B", (sx, wy, win_z - win_h/2 - 0.02),  (0.07, win_w + 0.08, 0.04), COL_HELM_ROOF)
            # arched cap (a small prism on top — fakes the rounded top)
            make_prism(f"DR_WinArch_{side}_{i}", (sx, wy, win_z + win_h/2 + 0.05),
                       (0.07, win_w + 0.10, 0.20), COL_HELM_ROOF, pitch_axis='X')

    # Grand-entry archway on the stern face (-Y) — three tall arches
    for i, ax in enumerate([-3.0, 0.0, 3.0]):
        make_box(f"DR_GrandEntry_{i}_Frame_L", (ax - 0.90, -DR_L/2 - 0.11, DR_Z),        (0.10, 0.05, DR_H - 0.4), COL_HELM_ROOF)
        make_box(f"DR_GrandEntry_{i}_Frame_R", (ax + 0.90, -DR_L/2 - 0.11, DR_Z),        (0.10, 0.05, DR_H - 0.4), COL_HELM_ROOF)
        make_box(f"DR_GrandEntry_{i}_Glass",    (ax, -DR_L/2 - 0.11, DR_Z),               (1.65, 0.04, DR_H - 0.5), col_window_warm)
        make_prism(f"DR_GrandEntry_{i}_Arch",   (ax, -DR_L/2 - 0.11, DR_Z + DR_H/2 - 0.20),
                   (1.85, 0.05, 0.40), COL_HELM_ROOF, pitch_axis='X')
    # Forward gable on the bow face (+Y)
    make_box("DR_BowFace", (0, DR_L/2 + 0.11, DR_Z), (DR_W, 0.04, DR_H - 0.5), COL_HULL)

    # ── COLUMNS supporting the saloon deck above the porch ──
    # Run along the outside of the dining-room walls, at the deck edges
    col_h = DR_H + 0.30
    col_z = BD_Z + 0.10 + col_h / 2.0
    n_cols = 8
    for side, sx in (("W", -BD_W/2 + 0.40), ("E", BD_W/2 - 0.40)):
        for i in range(n_cols):
            cy = -BD_L/2 + 1.5 + i * (BD_L - 3.0) / (n_cols - 1)
            make_cyl(f"Col_{side}_{i}", (sx, cy, col_z), 0.16, col_h, col_column, segments=8)
            # Gingerbread arch — fretwork piece at the top between columns
            if i < n_cols - 1:
                cy_next = -BD_L/2 + 1.5 + (i + 1) * (BD_L - 3.0) / (n_cols - 1)
                cy_mid = (cy + cy_next) / 2.0
                # the fretwork "scallop" between columns: a small thin box hung from the top
                make_box(f"Fret_{side}_{i}", (sx, cy_mid, BD_Z + 0.10 + col_h - 0.10),
                         (0.06, (cy_next - cy) * 0.85, 0.30), col_gingerbread)
                # arched curve — a small prism hanging below the fret
                make_prism(f"FretArch_{side}_{i}", (sx, cy_mid, BD_Z + 0.10 + col_h - 0.40),
                           (0.06, (cy_next - cy) * 0.75, 0.20), col_gingerbread, pitch_axis='X')

    # Fore and aft columns (4 across each end)
    for end_label, ey in (("S", -BD_L/2 + 0.40), ("N", BD_L/2 - 0.40)):
        for i, ex in enumerate([-BD_W/2 + 1.5, -BD_W/2 + 4.5, BD_W/2 - 4.5, BD_W/2 - 1.5]):
            make_cyl(f"Col_{end_label}_{i}", (ex, ey, col_z), 0.16, col_h, col_column, segments=8)

    # ── PORCH RAILINGS on the boiler deck ──
    rail_z = BD_Z + 0.55
    for side, sx in (("W", -BD_W/2 + 0.20), ("E",  BD_W/2 - 0.20)):
        make_box(f"BDeck_Rail_{side}_top", (sx, 0, rail_z + 0.40), (0.06, BD_L - 1.0, 0.06), COL_BRASS)
        make_box(f"BDeck_Rail_{side}_mid", (sx, 0, rail_z),         (0.04, BD_L - 1.0, 0.04), COL_BRASS)
        make_box(f"BDeck_Rail_{side}_low", (sx, 0, rail_z - 0.30),  (0.04, BD_L - 1.0, 0.04), COL_BRASS)
        # spindles
        for i in range(int((BD_L - 1.0) / 0.30)):
            sy = -BD_L/2 + 0.5 + 0.30 + i * 0.30
            make_box(f"BDeck_Spindle_{side}_{i}", (sx, sy, rail_z), (0.025, 0.025, 0.85), col_column)

    # ════════════════════════════════════════════════════════════
    # SALOON DECK (second story) — Z ≈ 5.4
    # ════════════════════════════════════════════════════════════
    SD_W = BD_W - 1.0       # narrower than boiler deck (12m)
    SD_L = BD_L - 1.0       # 24m
    SD_Z = BD_Z + 0.10 + col_h + 0.10   # sits on top of the columns
    make_box("Saloon_Deck", (0, 0, SD_Z), (SD_W, SD_L, 0.20), COL_DECK_WOOD)
    # Plank stripes
    for i in range(10):
        py = -SD_L/2 + 1.0 + i * (SD_L - 2.0) / 9.0
        make_box(f"Saloon_Plank_{i}", (0, py, SD_Z + 0.105),
                 (SD_W - 0.2, 0.04, 0.01), (0.32, 0.22, 0.14, 1.0))

    # ── SALOON CABIN ──
    SC_W = SD_W - 1.4
    SC_L = SD_L - 3.0
    SC_H = 3.0
    SC_Z = SD_Z + 0.10 + SC_H / 2.0
    make_box("SC_Walls_W", (-SC_W/2, 0, SC_Z), (0.20, SC_L, SC_H), COL_HULL)
    make_box("SC_Walls_E", ( SC_W/2, 0, SC_Z), (0.20, SC_L, SC_H), COL_HULL)
    make_box("SC_Walls_S", (0, -SC_L/2, SC_Z), (SC_W, 0.20, SC_H), COL_HULL)
    make_box("SC_Walls_N", (0,  SC_L/2, SC_Z), (SC_W, 0.20, SC_H), COL_HULL)

    # Saloon-deck arched windows (these are the staterooms — smaller)
    n_swins = 8
    swin_w = 0.55
    swin_h = 1.20
    swin_z = SC_Z + 0.10
    for side, sx in (("W", -SC_W/2 - 0.11), ("E",  SC_W/2 + 0.11)):
        for i in range(n_swins):
            wy = -SC_L/2 + 1.2 + i * (SC_L - 2.4) / (n_swins - 1)
            lit = ((i + (1 if side == "W" else 0)) % 4) != 3
            wcol = col_window_warm if lit else col_window_dark
            make_box(f"SC_Win_{side}_{i}", (sx, wy, swin_z), (0.06, swin_w, swin_h), wcol)
            make_box(f"SC_WinFrame_{side}_{i}_L", (sx, wy - swin_w/2 - 0.02, swin_z),  (0.07, 0.04, swin_h + 0.08), COL_HELM_ROOF)
            make_box(f"SC_WinFrame_{side}_{i}_R", (sx, wy + swin_w/2 + 0.02, swin_z),  (0.07, 0.04, swin_h + 0.08), COL_HELM_ROOF)
            make_prism(f"SC_WinArch_{side}_{i}", (sx, wy, swin_z + swin_h/2 + 0.04),
                       (0.07, swin_w + 0.10, 0.16), COL_HELM_ROOF, pitch_axis='X')

    # Saloon-deck columns + gingerbread (same pattern as boiler deck)
    sc_col_h = SC_H + 0.30
    sc_col_z = SD_Z + 0.10 + sc_col_h / 2.0
    n_scols = 8
    for side, sx in (("W", -SD_W/2 + 0.30), ("E", SD_W/2 - 0.30)):
        for i in range(n_scols):
            cy = -SD_L/2 + 1.5 + i * (SD_L - 3.0) / (n_scols - 1)
            make_cyl(f"SCol_{side}_{i}", (sx, cy, sc_col_z), 0.13, sc_col_h, col_column, segments=8)
            if i < n_scols - 1:
                cy_next = -SD_L/2 + 1.5 + (i + 1) * (SD_L - 3.0) / (n_scols - 1)
                cy_mid = (cy + cy_next) / 2.0
                make_box(f"SFret_{side}_{i}", (sx, cy_mid, SD_Z + 0.10 + sc_col_h - 0.10),
                         (0.05, (cy_next - cy) * 0.85, 0.24), col_gingerbread)
                make_prism(f"SFretArch_{side}_{i}", (sx, cy_mid, SD_Z + 0.10 + sc_col_h - 0.32),
                           (0.05, (cy_next - cy) * 0.70, 0.18), col_gingerbread, pitch_axis='X')

    # Saloon railings (lighter — thinner)
    sd_rail_z = SD_Z + 0.55
    for side, sx in (("W", -SD_W/2 + 0.15), ("E",  SD_W/2 - 0.15)):
        make_box(f"SDeck_Rail_{side}_top", (sx, 0, sd_rail_z + 0.30), (0.04, SD_L - 1.0, 0.04), COL_BRASS)
        make_box(f"SDeck_Rail_{side}_mid", (sx, 0, sd_rail_z),         (0.03, SD_L - 1.0, 0.03), COL_BRASS)
        for i in range(int((SD_L - 1.0) / 0.30)):
            sy = -SD_L/2 + 0.5 + 0.30 + i * 0.30
            make_box(f"SDeck_Spindle_{side}_{i}", (sx, sy, sd_rail_z), (0.02, 0.02, 0.70), col_column)

    # ════════════════════════════════════════════════════════════
    # HURRICANE DECK (third — open top) — Z ≈ 8.5
    # ════════════════════════════════════════════════════════════
    HD_W = SD_W - 1.0
    HD_L = SD_L - 1.0
    HD_Z = SC_Z + SC_H / 2.0 + 0.30
    make_box("Hurricane_Deck", (0, 0, HD_Z), (HD_W, HD_L, 0.18), COL_DECK_WOOD)
    # Light railing around the perimeter
    hd_rail_z = HD_Z + 0.50
    for side, sx in (("W", -HD_W/2), ("E",  HD_W/2)):
        make_box(f"HDeck_Rail_{side}_top", (sx, 0, hd_rail_z + 0.20), (0.04, HD_L, 0.04), COL_BRASS)
        for i in range(int(HD_L / 0.40)):
            sy = -HD_L/2 + 0.20 + 0.40 + i * 0.40
            make_box(f"HDeck_Spindle_{side}_{i}", (sx, sy, hd_rail_z), (0.02, 0.02, 0.55), col_column)
    for end_label, ey in (("S", -HD_L/2), ("N", HD_L/2)):
        make_box(f"HDeck_Rail_{end_label}_top", (0, ey, hd_rail_z + 0.20), (HD_W, 0.04, 0.04), COL_BRASS)

    # ════════════════════════════════════════════════════════════
    # PILOTHOUSE on top of hurricane deck — Z ≈ 10.5
    # ════════════════════════════════════════════════════════════
    PH_W = 4.0
    PH_L = 3.8
    PH_H = 2.6
    PH_Y_OFF = 3.5         # forward of center
    PH_Z = HD_Z + 0.09 + PH_H / 2.0
    make_box("PH_Walls_W", (-PH_W/2, PH_Y_OFF, PH_Z), (0.18, PH_L, PH_H), COL_HELM_WALL)
    make_box("PH_Walls_E", ( PH_W/2, PH_Y_OFF, PH_Z), (0.18, PH_L, PH_H), COL_HELM_WALL)
    make_box("PH_Walls_S", (0, PH_Y_OFF - PH_L/2, PH_Z), (PH_W, 0.18, PH_H), COL_HELM_WALL)
    make_box("PH_Walls_N", (0, PH_Y_OFF + PH_L/2, PH_Z), (PH_W, 0.18, PH_H), COL_HELM_WALL)

    # Big windows on all four sides — pilothouse is mostly glass
    for side, sx, sy, sz_off in (
        ("W", -PH_W/2 - 0.10, PH_Y_OFF, 0.30),
        ("E",  PH_W/2 + 0.10, PH_Y_OFF, 0.30),
    ):
        make_box(f"PH_Win_{side}", (sx, sy, PH_Z + sz_off), (0.06, PH_L - 0.4, PH_H - 0.7), col_window_warm)
        # mullion grid (2 vertical, 1 horizontal)
        for mv in (-0.7, 0.0, 0.7):
            make_box(f"PH_Mull_{side}_v_{mv}", (sx, sy + mv, PH_Z + sz_off), (0.07, 0.04, PH_H - 0.7), COL_HELM_ROOF)
        make_box(f"PH_Mull_{side}_h", (sx, sy, PH_Z + sz_off), (0.07, PH_L - 0.4, 0.04), COL_HELM_ROOF)
    for end, ey in (("S", PH_Y_OFF - PH_L/2 - 0.10), ("N", PH_Y_OFF + PH_L/2 + 0.10)):
        make_box(f"PH_Win_{end}", (0, ey, PH_Z + 0.30), (PH_W - 0.4, 0.06, PH_H - 0.7), col_window_warm)
        for mv in (-1.2, 0.0, 1.2):
            make_box(f"PH_Mull_{end}_v_{mv}", (mv, ey, PH_Z + 0.30), (0.04, 0.07, PH_H - 0.7), COL_HELM_ROOF)
        make_box(f"PH_Mull_{end}_h", (0, ey, PH_Z + 0.30), (PH_W - 0.4, 0.07, 0.04), COL_HELM_ROOF)

    # Pilothouse roof — bell-shaped: short box base + tapering prism + finial
    ph_roof_base_z = PH_Z + PH_H / 2.0 + 0.10
    make_box("PH_Roof_Eave", (0, PH_Y_OFF, ph_roof_base_z), (PH_W + 0.5, PH_L + 0.5, 0.10), COL_HELM_ROOF)
    make_prism("PH_Roof_Slope", (0, PH_Y_OFF, ph_roof_base_z + 0.05),
               (PH_W + 0.3, PH_L + 0.3, 1.20), COL_HELM_ROOF, pitch_axis='X')
    # Finial pole + ball on top
    make_cyl("PH_Finial_Pole", (0, PH_Y_OFF, ph_roof_base_z + 1.45), 0.05, 0.60, COL_BRASS, segments=6)
    make_cyl("PH_Finial_Ball", (0, PH_Y_OFF, ph_roof_base_z + 1.85), 0.16, 0.30, COL_BRASS, segments=8)

    # Roof cresting along the saloon-cabin roof (a decorative red ridge)
    sc_roof_z = SC_Z + SC_H / 2.0 + 0.18
    make_box("SC_Roof", (0, 0, sc_roof_z), (SC_W + 0.5, SC_L + 0.5, 0.16), COL_HELM_ROOF)
    # Cresting strip along the ridge
    for i in range(int(SC_L / 0.40)):
        cy = -SC_L/2 + 0.20 + i * 0.40
        make_box(f"SC_Crest_{i}", (0, cy, sc_roof_z + 0.18), (0.10, 0.10, 0.16), col_crest)

    # Roof cresting along the dining-room cabin roof
    dr_roof_z = DR_Z + DR_H / 2.0 + 0.18
    make_box("DR_Roof", (0, 0, dr_roof_z), (DR_W + 0.5, DR_L + 0.5, 0.16), COL_HELM_ROOF)
    for i in range(int(DR_L / 0.40)):
        cy = -DR_L/2 + 0.20 + i * 0.40
        make_box(f"DR_Crest_{i}", (0, cy, dr_roof_z + 0.18), (0.10, 0.10, 0.16), col_crest)

    # ════════════════════════════════════════════════════════════
    # TWIN SMOKESTACKS — forward of pilothouse, rising from main deck
    # ════════════════════════════════════════════════════════════
    stack_y = -BOAT_L / 2 + 16.0   # forward, but not all the way to the bow
    stack_h = 11.5
    stack_base_z = BD_Z + 0.10
    stack_center_z = stack_base_z + stack_h / 2.0
    for label, sx in (("W", -1.8), ("E", 1.8)):
        # base flange
        make_cyl(f"Stack_{label}_Flange", (sx, stack_y, stack_base_z + 0.20), 0.50, 0.40, COL_BRASS, segments=8)
        # main shaft
        make_cyl(f"Stack_{label}_Shaft", (sx, stack_y, stack_center_z), 0.36, stack_h, COL_SMOKESTACK, segments=8)
        # ornamental rings every 3m up the shaft
        for ri in range(3):
            ring_z = stack_base_z + 1.5 + ri * 3.0
            make_cyl(f"Stack_{label}_Ring_{ri}", (sx, stack_y, ring_z), 0.42, 0.10, COL_BRASS, segments=8)
        # decorative crown at the top — flared
        make_cyl(f"Stack_{label}_Crown", (sx, stack_y, stack_base_z + stack_h + 0.05), 0.55, 0.30, COL_BRASS, segments=8)
        # the toothed crown ring (spikes on top — characteristic of riverboat stacks)
        crown_top_z = stack_base_z + stack_h + 0.30
        for ti in range(8):
            ang = 2.0 * math.pi * ti / 8.0
            tx = sx + math.cos(ang) * 0.45
            ty_off = math.sin(ang) * 0.45
            make_box(f"Stack_{label}_Tooth_{ti}", (tx, stack_y + ty_off, crown_top_z),
                     (0.10, 0.10, 0.40), COL_BRASS)

    # ════════════════════════════════════════════════════════════
    # PADDLE WHEEL — bigger, with proper housing
    # ════════════════════════════════════════════════════════════
    pw_y = -BOAT_L / 2 - 2.0   # AFT of stern (stern-wheeler)
    pw_z = RIVER_LEVEL_Z + 2.4
    pw_radius = 2.4
    pw_blade_n = 12

    # Housing — 5 stacked panels approximating a curved arc
    house_h_total = 5.4
    house_w = BOAT_W * 0.85
    for ti, (zoff, wfrac) in enumerate([(-2.5, 0.85), (-1.4, 0.95), (0.0, 1.0), (1.4, 0.95), (2.5, 0.85)]):
        make_box(f"PWHouse_tier_{ti}", (0, pw_y, pw_z + zoff), (house_w * wfrac, 0.50, 1.20), COL_PADDLE_HOUSING)
    # back wall of housing
    make_box("PWHouse_Back", (0, pw_y + 0.35, pw_z), (house_w, 0.10, house_h_total), COL_PADDLE_HOUSING)
    # housing crown — decorative top ridge
    for i in range(int(house_w / 0.50)):
        cx = -house_w/2 + 0.25 + i * 0.50
        make_box(f"PWHouse_Crest_{i}", (cx, pw_y, pw_z + 2.85), (0.12, 0.50, 0.20), col_crest)

    # Hub and axle (cylinder along X)
    make_cyl("PW_Axle", (0, pw_y, pw_z), 0.30, BOAT_W * 0.75, COL_BRASS, segments=8, axis='X')
    make_cyl("PW_HubL", (-BOAT_W * 0.35, pw_y, pw_z), 0.55, 0.30, COL_BRASS, segments=10, axis='X')
    make_cyl("PW_HubR", ( BOAT_W * 0.35, pw_y, pw_z), 0.55, 0.30, COL_BRASS, segments=10, axis='X')

    # Outer rims — proper toruses around the hub on each side of the
    # wheel (left + right end-caps of the paddle assembly).
    rim_y_L = pw_y - BOAT_W * 0.30
    rim_y_R = pw_y + BOAT_W * 0.30
    make_torus("PW_Rim_L", (0, rim_y_L, pw_z),
               major_r=pw_radius, minor_r=0.08, base_color=COL_PADDLE_BLADES,
               major_seg=pw_blade_n, minor_seg=6, axis='Y')
    make_torus("PW_Rim_R", (0, rim_y_R, pw_z),
               major_r=pw_radius, minor_r=0.08, base_color=COL_PADDLE_BLADES,
               major_seg=pw_blade_n, minor_seg=6, axis='Y')
    # Spokes (real angled cylinders from hub to rim, not axis-aligned
    # box hacks) + blades at the rim
    blade_len = BOAT_W * 0.75
    for i in range(pw_blade_n):
        ang = 2.0 * math.pi * i / pw_blade_n
        bx = math.cos(ang) * pw_radius
        bz = math.sin(ang) * pw_radius + pw_z
        # Spoke L (left end of axle to rim L)
        make_tube_segment(f"PW_Spoke_L_{i}",
                          (0, rim_y_L, pw_z),
                          (bx, rim_y_L, bz),
                          0.05, COL_PADDLE_BLADES, segments=5)
        # Spoke R
        make_tube_segment(f"PW_Spoke_R_{i}",
                          (0, rim_y_R, pw_z),
                          (bx, rim_y_R, bz),
                          0.05, COL_PADDLE_BLADES, segments=5)
        # Blade plank at the rim, running along the axle
        make_box(f"PW_Blade_{i}", (bx, pw_y, bz),
                 (0.10, blade_len, 0.55), COL_PADDLE_BLADES)
        # Cross-brace between the two rims at this blade position
        make_tube_segment(f"PW_Brace_{i}",
                          (bx, rim_y_L, bz),
                          (bx, rim_y_R, bz),
                          0.04, COL_BRASS, segments=4)

    # ════════════════════════════════════════════════════════════
    # BELL on the hurricane deck (just aft of pilothouse)
    # ════════════════════════════════════════════════════════════
    bell_y = PH_Y_OFF - PH_L / 2.0 - 1.5
    bell_base_z = HD_Z + 0.10
    # bell support frame — two posts and a cross-beam
    make_box("Bell_PostL", (-0.45, bell_y, bell_base_z + 0.75), (0.10, 0.10, 1.50), COL_HULL)
    make_box("Bell_PostR", ( 0.45, bell_y, bell_base_z + 0.75), (0.10, 0.10, 1.50), COL_HULL)
    make_box("Bell_Beam",  (0, bell_y, bell_base_z + 1.50), (1.10, 0.10, 0.10), COL_HULL)
    # the bell itself — tapered (use two stacked cylinders)
    make_cyl("Bell_Body", (0, bell_y, bell_base_z + 1.10), 0.20, 0.35, COL_BRASS, segments=10)
    make_cyl("Bell_Lip",  (0, bell_y, bell_base_z + 0.92), 0.28, 0.10, COL_BRASS, segments=10)

    # ════════════════════════════════════════════════════════════
    # LIFEBUOYS on rails — proper TORUS now, not a chain of boxes.
    # A red base ring with 4 white "strap" toruses oriented
    # perpendicular to the main ring (the canonical red+white pattern).
    # ════════════════════════════════════════════════════════════
    for i, (lx_l, ly_l) in enumerate([(-BD_W/2 - 0.20, -7.0), (-BD_W/2 - 0.20, 5.0),
                                       ( BD_W/2 + 0.20, -7.0), ( BD_W/2 + 0.20, 5.0)]):
        ring_cz = BD_Z + 0.85
        # Main ring — axis along X so the ring hangs vertical, presenting
        # its face outboard (so it reads from the player's POV on the dock)
        make_torus(f"Lifebuoy_{i}_ring", (lx_l, ly_l, ring_cz),
                   major_r=0.42, minor_r=0.08, base_color=(0.85, 0.20, 0.18, 1.0),
                   major_seg=14, minor_seg=6, axis='X')
        # 4 white "strap" rings around the ring at quarter angles —
        # each is a small torus wrapped around the main ring's tube
        for si, ang_deg in enumerate([0, 90, 180, 270]):
            ang = math.radians(ang_deg)
            sx_l = lx_l
            sy_l = ly_l + math.cos(ang) * 0.42
            sz_l = ring_cz + math.sin(ang) * 0.42
            make_torus(f"Lifebuoy_{i}_strap_{si}", (sx_l, sy_l, sz_l),
                       major_r=0.10, minor_r=0.05, base_color=(0.94, 0.90, 0.78, 1.0),
                       major_seg=8, minor_seg=4,
                       axis='Y' if (si % 2 == 0) else 'Z')

    # ════════════════════════════════════════════════════════════
    # GANGWAY — angled plank from the boat's port deck DOWN to the
    # dock deck. Real gangways slope ~15-25°. From BD_Z+top of
    # decking ~2.05 down to DOCK_Z+0.10 ~0.45, ~1.6m drop over ~3m
    # run = ~28° slope.
    # ════════════════════════════════════════════════════════════
    # Calculated to land on the dock east edge ≈ X=-6.7
    gw_start_x = -BD_W / 2.0 + 0.20         # at the port edge of the boat deck
    gw_start_z = BD_Z + 0.10                # boat boiler deck surface
    gw_end_x   = gw_start_x - 3.20          # dock-ward
    gw_end_z   = DOCK_Z + 0.10              # dock surface
    make_ramp("Gangway_Slope",
              (gw_start_x, 0.0, gw_start_z),
              (gw_end_x,   0.0, gw_end_z),
              2.4, 0.14, COL_DECK_WOOD, width_axis='Y')
    # Plank lines across the gangway (4 cross-stripes for grip)
    for i in range(8):
        t = (i + 0.5) / 8.0
        ppx = gw_start_x + t * (gw_end_x - gw_start_x)
        ppz = gw_start_z + t * (gw_end_z - gw_start_z) + 0.005
        make_box(f"Gangway_Tread_{i}", (ppx, 0.0, ppz),
                 (0.10, 2.3, 0.02), (0.20, 0.14, 0.08, 1.0))
    # Sloping railings (boxes from start corner to end corner, two heights)
    for side, sy_r in (("N", 1.20), ("S", -1.20)):
        # top rail — a slanted thin box approximated via make_ramp
        make_ramp(f"Gangway_Rail_{side}_top",
                  (gw_start_x, sy_r, gw_start_z + 0.95),
                  (gw_end_x,   sy_r, gw_end_z + 0.95),
                  0.06, 0.04, COL_BRASS, width_axis='Y')
        # vertical posts at intervals
        for i in range(5):
            t = (i + 0.5) / 5.0
            ppx = gw_start_x + t * (gw_end_x - gw_start_x)
            ppz = gw_start_z + t * (gw_end_z - gw_start_z)
            make_box(f"Gangway_Post_{side}_{i}", (ppx, sy_r, ppz + 0.48),
                     (0.05, 0.05, 0.95), COL_BRASS)

    # Gangway entry arch on the boat's PORT wall of the dining cabin
    arch_x = -DR_W/2 - 0.5
    make_box("Entry_Arch_F", (arch_x, -1.2, BD_Z + 1.3), (0.15, 0.15, 2.5), COL_HULL)
    make_box("Entry_Arch_A", (arch_x,  1.2, BD_Z + 1.3), (0.15, 0.15, 2.5), COL_HULL)
    make_prism("Entry_Arch_Top", (arch_x, 0, BD_Z + 2.55), (0.20, 2.6, 0.50), col_gingerbread, pitch_axis='Y')

    # ════════════════════════════════════════════════════════════
    # ON-BOAT D'AMBROSIO'S NEON SIGN — mounted on the saloon-cabin's
    # PORT wall, facing -X (the parking lot / player approach).
    # Per the vol5 exterior concept art: the diner's main signage sits
    # ATOP the boat itself, not just on a roadside pole. This makes
    # the boat unmistakably D'Ambrosio's from the parking lot.
    # ════════════════════════════════════════════════════════════
    # Sign sits ATOP the saloon cabin (above the roof, on its own
    # mounting posts) like a billboard / marquee — NOT on the wall
    # where it would cover the staterooms' arched windows.
    # Per the vol5 exterior concept: the sign rides on top of the
    # upper structure, big enough to read from the parking lot.
    saloon_roof_z = SC_Z + SC_H / 2.0 + 0.20      # top of the saloon cabin roof
    boat_sign_w  = 7.6                            # large — readable from across the lot
    boat_sign_h  = 2.4
    boat_sign_cx = -SC_W / 2.0 - 0.05             # outboard on the port side
    boat_sign_cy = 0.0                            # centred on the boat's length
    boat_sign_cz = saloon_roof_z + boat_sign_h / 2.0 + 0.4   # elevated above the roof
    # Two stout mounting posts going from the saloon roof up to the
    # bottom of the sign panel
    for post_idx, post_y in enumerate([-boat_sign_w * 0.35, boat_sign_w * 0.35]):
        post_h = boat_sign_cz - boat_sign_h/2.0 - saloon_roof_z
        post_cz = saloon_roof_z + post_h / 2.0
        make_box(f"BoatSign_Post_{post_idx}", (boat_sign_cx + 0.10, post_y, post_cz),
                 (0.18, 0.18, post_h), (0.30, 0.26, 0.22, 1.0))
    # Dark backing panel — face normal points -X (toward parking lot)
    make_box("BoatSign_Panel", (boat_sign_cx - 0.04, boat_sign_cy, boat_sign_cz),
             (0.05, boat_sign_w, boat_sign_h), (0.10, 0.08, 0.08, 1.0))
    # Frame trims
    fy = boat_sign_cx - 0.08
    make_box("BoatSign_FrameTop", (fy, boat_sign_cy, boat_sign_cz + boat_sign_h/2 + 0.10),
             (0.06, boat_sign_w + 0.22, 0.14), (0.32, 0.26, 0.20, 1.0))
    make_box("BoatSign_FrameLow", (fy, boat_sign_cy, boat_sign_cz - boat_sign_h/2 - 0.10),
             (0.06, boat_sign_w + 0.22, 0.14), (0.32, 0.26, 0.20, 1.0))
    make_box("BoatSign_FrameFwd", (fy, boat_sign_cy + boat_sign_w/2 + 0.10, boat_sign_cz),
             (0.06, 0.14, boat_sign_h + 0.22), (0.32, 0.26, 0.20, 1.0))
    make_box("BoatSign_FrameAft", (fy, boat_sign_cy - boat_sign_w/2 - 0.10, boat_sign_cz),
             (0.06, 0.14, boat_sign_h + 0.22), (0.32, 0.26, 0.20, 1.0))
    # Cursive neon on the panel face. Big scale (2.0x) so the neon
    # fills ~85% of the 7.6m panel — no more "lots of black space"
    # around tiny letters. cursive_type auto-centres the text.
    make_neon_dambrosios("Boat_Port",
                          (boat_sign_cx - 0.08, boat_sign_cy, boat_sign_cz),
                          face_axis='X', face_sign=-1, scale=2.0)

    # Hawser bollards (mooring posts) on the boiler deck along the PORT rail
    for i, by_p in enumerate([-5.0, 5.0]):
        make_cyl(f"Bollard_{i}", (-BD_W/2 + 0.5, by_p, BD_Z + 0.40), 0.18, 0.70, (0.32, 0.30, 0.28, 1.0), segments=8)
        make_cyl(f"Bollard_Cap_{i}", (-BD_W/2 + 0.5, by_p, BD_Z + 0.78), 0.22, 0.10, (0.32, 0.30, 0.28, 1.0), segments=8)


# ════════════════════════════════════════════════════════════════
# THE PARKING LOT
# ════════════════════════════════════════════════════════════════

def build_parking_lot():
    """Parking lot on the PORT (-X) side of the boat, parallel to the
    shoreline. Long axis along Y (along the boat), short axis along X.
    East edge of the lot meets the west end of the dock."""
    lot_cx = PARKING_X - 6.0       # lot center X
    lot_cy = PARKING_Y_CENTER
    lot_x_w = 22.0                  # short (perpendicular to shore)
    lot_y_l = 36.0                  # long  (along the shore)
    lot_z = -0.02
    make_box("Parking_Asphalt", (lot_cx, lot_cy, lot_z), (lot_x_w, lot_y_l, 0.04), COL_ASPHALT)

    # Curb stones around perimeter (concrete edging)
    curb_col = (0.55, 0.52, 0.48, 1.0)
    make_box("Curb_S", (lot_cx, lot_cy - lot_y_l/2, 0.10), (lot_x_w, 0.20, 0.18), curb_col)
    make_box("Curb_N", (lot_cx, lot_cy + lot_y_l/2, 0.10), (lot_x_w, 0.20, 0.18), curb_col)
    make_box("Curb_W", (lot_cx - lot_x_w/2, lot_cy, 0.10), (0.20, lot_y_l, 0.18), curb_col)
    make_box("Curb_E", (lot_cx + lot_x_w/2, lot_cy, 0.10), (0.20, lot_y_l, 0.18), curb_col)

    # Painted parking lines — two rows of bays running along the X axis
    # (cars perpendicular to the shoreline, parked nose-to-east-or-west)
    for row_idx, row_x_off in enumerate([-4.5, 4.5]):
        for i in range(11):
            ly_p = -lot_y_l/2 + 3.0 + i * 3.0
            make_box(f"ParkingLine_{row_idx}_{i}",
                     (lot_cx + row_x_off, lot_cy + ly_p, lot_z + 0.025),
                     (3.5, 0.10, 0.005),
                     COL_PAINT_LINE)
        # row divider stripe
        make_box(f"ParkingDivider_{row_idx}",
                 (lot_cx + row_x_off - 1.8, lot_cy, lot_z + 0.025),
                 (0.10, lot_y_l - 1.0, 0.005),
                 COL_PAINT_LINE)

    # Yellow speed bumps across the lot's west (entrance) side
    bump_col = (0.72, 0.55, 0.20, 1.0)
    for i in range(2):
        by = -8.0 + i * 16.0
        make_prism(f"SpeedBump_{i}", (lot_cx - lot_x_w/2 + 4.0, lot_cy + by, lot_z),
                   (0.50, 2.4, 0.10), bump_col, pitch_axis='X')

    # Storm drain along the boat-side curb
    make_box("StormDrain", (lot_cx + lot_x_w/2 - 1.0, lot_cy - 12.0, lot_z + 0.02),
             (0.5, 1.0, 0.02), (0.10, 0.10, 0.10, 1.0))
    for i in range(5):
        make_box(f"StormDrain_Slat_{i}", (lot_cx + lot_x_w/2 - 1.0, lot_cy - 12.4 + i * 0.20, lot_z + 0.03),
                 (0.45, 0.04, 0.01), (0.20, 0.18, 0.16, 1.0))

    # Sodium streetlights — 3 poles around the lot perimeter
    sodium_poles = [
        (lot_cx, lot_cy - lot_y_l/2 + 1.0, ( 0,  1)),   # south side (sweeps north into lot)
        (lot_cx, lot_cy + lot_y_l/2 - 1.0, ( 0, -1)),   # north side (sweeps south)
        (lot_cx - lot_x_w/2 + 1.0, lot_cy, ( 1,  0)),   # west side (sweeps east)
    ]
    for si, (px, py, (sweep_x, sweep_y)) in enumerate(sodium_poles):
        make_cyl(f"Sodium_Pole_{si}", (px, py, 3.0), 0.10, 6.0, COL_SODIUM_POLE, segments=8)
        make_cyl(f"Sodium_Base_{si}", (px, py, 0.15), 0.18, 0.30, COL_SODIUM_POLE, segments=8)
        arm_off_x = 0.5 * sweep_x
        arm_off_y = 0.5 * sweep_y
        head_off_x = 0.8 * sweep_x
        head_off_y = 0.8 * sweep_y
        if sweep_x != 0:
            make_box(f"Sodium_Arm_{si}", (px + arm_off_x, py, 5.95), (0.7, 0.08, 0.08), COL_SODIUM_POLE)
            make_prism(f"Sodium_Head_{si}", (px + head_off_x, py, 5.78), (0.5, 0.8, 0.22), COL_SODIUM_HEAD, pitch_axis='X')
            make_box(f"Sodium_Lens_{si}", (px + head_off_x, py, 5.72), (0.42, 0.62, 0.04), (1.0, 0.72, 0.30, 1.0))
        else:
            make_box(f"Sodium_Arm_{si}", (px, py + arm_off_y, 5.95), (0.08, 0.7, 0.08), COL_SODIUM_POLE)
            make_prism(f"Sodium_Head_{si}", (px, py + head_off_y, 5.78), (0.8, 0.5, 0.22), COL_SODIUM_HEAD, pitch_axis='Y')
            make_box(f"Sodium_Lens_{si}", (px, py + head_off_y, 5.72), (0.62, 0.42, 0.04), (1.0, 0.72, 0.30, 1.0))

    # ── 8 PARKED CARS — bodies oriented along X (head/trunk face east/west) ──
    # Two rows: row 0 cars at row_x = -4.5 facing west, row 1 at row_x = +4.5 facing east
    # (so each row's cars nose into their parking line)
    cars = [
        (-4.5, -13.0, COL_CAR_BODY_A, -1),
        (-4.5,  -9.0, COL_CAR_BODY_B, -1),
        (-4.5,  -5.0, COL_CAR_BODY_C, -1),
        (-4.5,   1.0, (0.30, 0.35, 0.50, 1.0), -1),
        (-4.5,   8.0, (0.65, 0.60, 0.55, 1.0), -1),
        (-4.5,  13.0, COL_CAR_BODY_A, -1),
        ( 4.5,  -8.0, COL_CAR_BODY_C,  1),
        ( 4.5,   6.0, COL_CAR_BODY_B,  1),
    ]
    for i, (row_x_off, ly, col, facing) in enumerate(cars):
        cx = lot_cx + row_x_off
        cy = lot_cy + ly
        # facing = -1 → nose at -X, facing = +1 → nose at +X
        front_off_x = -2.0 * facing
        back_off_x  =  2.0 * facing
        # Lower / mid body — long axis along X (since car points along X).
        # The body is now tapered at the corners using small spheres so
        # the car silhouette reads less boxy from a distance.
        make_box(f"Car_{i}_body_low", (cx, cy, lot_z + 0.30), (4.0, 1.75, 0.30), col)
        make_box(f"Car_{i}_body_mid", (cx, cy, lot_z + 0.60), (4.1, 1.70, 0.30), col)
        # Corner spheres at each body corner to round the silhouette
        for ssi, (sox, soy) in enumerate([(-1.95, -0.78), (1.95, -0.78), (-1.95, 0.78), (1.95, 0.78)]):
            make_sphere(f"Car_{i}_corner_{ssi}", (cx + sox, cy + soy, lot_z + 0.45),
                        0.30, col)
        # Hood — PRISM sloping DOWN toward the front (not a flat slab).
        # pitch_axis='Y' would peak along Y; we want peak along X (toward
        # the cabin), bottom along -X (front of car). Use 'X' to put the
        # ridge along the X axis; size=(width, length_along_x, peak_height).
        # But the prism builder peaks UP — to get a hood sloping FROM
        # the cabin DOWN to the front, we use a prism in two parts:
        #   - a low flat slab covering the front
        #   - a small wedge rising as it approaches the cabin
        # Simpler: use make_prism with pitch_axis='X' so the ridge
        # crosses the car perpendicular to the hood, then offset so the
        # ridge sits at the cabin edge.
        hood_x_center = cx + front_off_x * 0.55
        make_prism(f"Car_{i}_hood",
                   (hood_x_center, cy, lot_z + 0.78),
                   (1.6, 1.60, 0.20), col, pitch_axis='Y')
        trunk_x_center = cx + back_off_x * 0.55
        make_prism(f"Car_{i}_trunk",
                   (trunk_x_center, cy, lot_z + 0.78),
                   (1.4, 1.60, 0.16), col, pitch_axis='Y')
        # Cabin — base box, with rounded corner spheres on top and a
        # gently sloped (low-prism) roof so the greenhouse doesn't sit
        # under a flat board.
        make_box(f"Car_{i}_cabin", (cx, cy, lot_z + 1.00), (1.6, 1.55, 0.50), col)
        roof_col = (col[0] * 0.65, col[1] * 0.65, col[2] * 0.65, 1.0)
        make_prism(f"Car_{i}_roof",
                   (cx, cy, lot_z + 1.25),
                   (1.55, 1.45, 0.12), roof_col, pitch_axis='Y')
        # Cabin top corner spheres for round greenhouse profile
        for rci, (rox, roy) in enumerate([(-0.78, -0.75), (0.78, -0.75), (-0.78, 0.75), (0.78, 0.75)]):
            make_sphere(f"Car_{i}_cabinCorner_{rci}", (cx + rox, cy + roy, lot_z + 1.20),
                        0.20, col)
        # Windshield (front of cabin), rear window
        make_box(f"Car_{i}_windshield", (cx + front_off_x * 0.425, cy, lot_z + 1.05), (0.06, 1.45, 0.45), COL_CAR_GLASS)
        make_box(f"Car_{i}_rearwin",    (cx + back_off_x * 0.425,  cy, lot_z + 1.05), (0.06, 1.45, 0.42), COL_CAR_GLASS)
        # Side windows
        make_box(f"Car_{i}_winN", (cx, cy + 0.78, lot_z + 1.05), (1.5, 0.02, 0.40), COL_CAR_GLASS)
        make_box(f"Car_{i}_winS", (cx, cy - 0.78, lot_z + 1.05), (1.5, 0.02, 0.40), COL_CAR_GLASS)
        # Headlights (front) — two side-by-side at the +/-Y from car center along the X-facing front
        head_col = (0.95, 0.92, 0.65, 1.0)
        tail_col = (0.85, 0.18, 0.16, 1.0)
        fx = cx + front_off_x
        rx = cx + back_off_x
        make_box(f"Car_{i}_headL", (fx, cy - 0.55, lot_z + 0.45), (0.04, 0.30, 0.18), head_col)
        make_box(f"Car_{i}_headR", (fx, cy + 0.55, lot_z + 0.45), (0.04, 0.30, 0.18), head_col)
        make_box(f"Car_{i}_tailL", (rx, cy - 0.55, lot_z + 0.45), (0.04, 0.30, 0.18), tail_col)
        make_box(f"Car_{i}_tailR", (rx, cy + 0.55, lot_z + 0.45), (0.04, 0.30, 0.18), tail_col)
        # Bumpers
        bump_col = (0.18, 0.18, 0.18, 1.0)
        make_box(f"Car_{i}_bumpF", (fx + 0.01 * facing, cy, lot_z + 0.25), (0.06, 1.75, 0.18), bump_col)
        make_box(f"Car_{i}_bumpR", (rx - 0.01 * facing, cy, lot_z + 0.25), (0.06, 1.75, 0.18), bump_col)
        # Side mirrors
        mir_col = (col[0] * 0.8, col[1] * 0.8, col[2] * 0.8, 1.0)
        make_box(f"Car_{i}_mirN", (cx + front_off_x * 0.35, cy + 0.85, lot_z + 1.10), (0.18, 0.08, 0.10), mir_col)
        make_box(f"Car_{i}_mirS", (cx + front_off_x * 0.35, cy - 0.85, lot_z + 1.10), (0.18, 0.08, 0.10), mir_col)
        # Grille (front, facing X direction)
        grille_col = (0.20, 0.18, 0.16, 1.0)
        make_box(f"Car_{i}_grille", (fx - 0.02 * facing, cy, lot_z + 0.40), (0.04, 1.30, 0.20), grille_col)
        # Wheels (axles along Y now, since car points along X)
        tire_col = (0.08, 0.08, 0.08, 1.0)
        for wi, (wx_off, wy_off) in enumerate([(-1.4, -0.78), (-1.4, 0.78), (1.4, -0.78), (1.4, 0.78)]):
            make_cyl(f"Car_{i}_wheel_{wi}", (cx + wx_off, cy + wy_off, lot_z + 0.16),
                     0.28, 0.20, tire_col, segments=8, axis='Y')
            make_cyl(f"Car_{i}_hub_{wi}", (cx + wx_off, cy + wy_off + (0.11 if wy_off > 0 else -0.11), lot_z + 0.16),
                     0.10, 0.04, COL_BRASS, segments=6, axis='Y')

    # ── DUMPSTER in the NW corner ──
    dx_d = lot_cx - lot_x_w/2 + 2.0
    dy_d = lot_cy + lot_y_l/2 - 2.0
    dump_col = (0.18, 0.28, 0.30, 1.0)
    make_box("Dumpster_Body", (dx_d, dy_d, 0.55), (1.6, 2.4, 1.10), dump_col)
    make_prism("Dumpster_Lid", (dx_d, dy_d, 1.10), (1.6, 2.4, 0.20), (0.14, 0.20, 0.22, 1.0), pitch_axis='Y')
    make_box("Dumpster_HingeBand", (dx_d + 0.81, dy_d, 1.10), (0.06, 2.4, 0.04), COL_BRASS)
    make_box("Dumpster_Tag", (dx_d - 0.81, dy_d - 0.6, 0.55), (0.04, 1.0, 0.30), (0.85, 0.55, 0.20, 1.0))
    for wi, (wox, woy) in enumerate([(-0.7, -1.0), (0.7, -1.0), (-0.7, 1.0), (0.7, 1.0)]):
        make_cyl(f"Dumpster_Wheel_{wi}", (dx_d + wox, dy_d + woy, 0.10), 0.10, 0.10,
                 (0.10, 0.10, 0.10, 1.0), segments=6, axis='Y')

    # ── PHONE POLE at the SW corner ──
    pp_x = lot_cx - lot_x_w/2 - 1.0
    pp_y = lot_cy - lot_y_l/2 + 1.5
    make_cyl("PhonePole_Shaft", (pp_x, pp_y, 5.5), 0.18, 11.0, (0.42, 0.30, 0.20, 1.0), segments=8)
    make_box("PhonePole_Crossbar_top", (pp_x, pp_y, 9.8), (0.10, 2.4, 0.10), (0.42, 0.30, 0.20, 1.0))
    make_box("PhonePole_Crossbar_low", (pp_x, pp_y, 8.6), (0.10, 2.0, 0.10), (0.42, 0.30, 0.20, 1.0))
    make_cyl("PhonePole_Transformer", (pp_x, pp_y + 0.35, 8.2), 0.22, 0.55, (0.40, 0.38, 0.34, 1.0), segments=8)
    for ii, iy in enumerate([-1.0, -0.4, 0.4, 1.0]):
        make_cyl(f"PhonePole_Insulator_{ii}", (pp_x, pp_y + iy, 9.95), 0.06, 0.18, (0.85, 0.80, 0.72, 1.0), segments=6)

    # ── NEWSPAPER BOX rank along the dock-side curb ──
    np_x = lot_cx + lot_x_w/2 - 0.6
    for ni, (ny_off, col) in enumerate([(-3.0, (0.72, 0.20, 0.16, 1.0)),
                                          (-2.0, (0.20, 0.40, 0.62, 1.0)),
                                          (-1.0, (0.30, 0.30, 0.30, 1.0))]):
        make_box(f"NewsBox_{ni}_body", (np_x, lot_cy + ny_off, 0.50), (0.45, 0.45, 0.95), col)
        make_box(f"NewsBox_{ni}_top",  (np_x, lot_cy + ny_off, 1.03), (0.50, 0.50, 0.10), (col[0]*0.6, col[1]*0.6, col[2]*0.6, 1.0))
        make_box(f"NewsBox_{ni}_window", (np_x + 0.23, lot_cy + ny_off, 0.65), (0.04, 0.30, 0.30), (0.85, 0.82, 0.72, 1.0))
        make_box(f"NewsBox_{ni}_slot",   (np_x + 0.23, lot_cy + ny_off, 0.30), (0.02, 0.10, 0.04), (0.10, 0.10, 0.10, 1.0))

    # ── ASH CAN near the gangway entry (north end of dock side) ──
    ac_x = lot_cx + lot_x_w/2 - 0.5
    ac_y = lot_cy + 1.6
    make_cyl("AshCan_Body", (ac_x, ac_y, 0.55), 0.28, 1.10, (0.22, 0.20, 0.18, 1.0), segments=8)
    make_cyl("AshCan_Top",  (ac_x, ac_y, 1.10), 0.32, 0.10, (0.45, 0.42, 0.36, 1.0), segments=8)
    make_cyl("AshCan_Sand", (ac_x, ac_y, 1.18), 0.20, 0.04, (0.65, 0.60, 0.50, 1.0), segments=8)

    # ── BUS BENCH near the curb ──
    bb_x = lot_cx + lot_x_w/2 - 0.6
    bb_y = lot_cy - 4.5
    make_box("BusBench_Seat", (bb_x, bb_y, 0.45), (0.40, 1.8, 0.10), (0.30, 0.22, 0.16, 1.0))
    make_box("BusBench_Back", (bb_x + 0.16, bb_y, 0.85), (0.06, 1.8, 0.70), (0.30, 0.22, 0.16, 1.0))
    for li, ly_off in enumerate([-0.80, 0.80]):
        make_box(f"BusBench_Leg_{li}", (bb_x, bb_y + ly_off, 0.22), (0.40, 0.10, 0.45), (0.18, 0.18, 0.18, 1.0))

    # ── "D'Ambrosio's" SIGN — pole + dark panel + cursive RED NEON ──
    # Sign sits at the south-east entry corner of the lot, panel face
    # parallel to the lot edge (faces +Y / -Y so road traffic sees it).
    sign_x = lot_cx + lot_x_w/2 + 0.5
    sign_y = lot_cy - lot_y_l/2 + 2.0
    make_cyl("Sign_Pole", (sign_x, sign_y, 3.6), 0.14, 7.2, (0.26, 0.24, 0.22, 1.0), segments=8)
    # The dark mounting panel — sized so the cursive script has real
    # breathing room. Letters are positioned with 1.5x previous spacing
    # so the D'A cluster reads instead of smearing.
    sign_w = 6.4
    sign_h = 2.0
    sign_z = 5.7
    make_box("Sign_Panel_N", (sign_x, sign_y + 0.08, sign_z), (sign_w, 0.05, sign_h), (0.12, 0.10, 0.10, 1.0))
    make_box("Sign_Panel_S", (sign_x, sign_y - 0.08, sign_z), (sign_w, 0.05, sign_h), (0.12, 0.10, 0.10, 1.0))
    # frame trims
    for face_y, label in ((0.10, "N"), (-0.10, "S")):
        make_box(f"Sign_Frame_{label}_top", (sign_x, sign_y + face_y, sign_z + sign_h/2 + 0.06),
                 (sign_w + 0.20, 0.06, 0.12), (0.32, 0.26, 0.20, 1.0))
        make_box(f"Sign_Frame_{label}_low", (sign_x, sign_y + face_y, sign_z - sign_h/2 - 0.06),
                 (sign_w + 0.20, 0.06, 0.12), (0.32, 0.26, 0.20, 1.0))
        make_box(f"Sign_Frame_{label}_L",   (sign_x - sign_w/2 - 0.06, sign_y + face_y, sign_z),
                 (0.12, 0.06, sign_h + 0.20), (0.32, 0.26, 0.20, 1.0))
        make_box(f"Sign_Frame_{label}_R",   (sign_x + sign_w/2 + 0.06, sign_y + face_y, sign_z),
                 (0.12, 0.06, sign_h + 0.20), (0.32, 0.26, 0.20, 1.0))

    # ── CURSIVE RED NEON: D'Ambrosio's — both faces of the pole sign,
    # via the shared module-level helper. Scaled up to fill the panel
    # (was 1.0 → too much black margin on the 6.4m wide sign).
    make_neon_dambrosios("Pole_N", (sign_x, sign_y + 0.10, sign_z),
                          face_axis='Y', face_sign=+1, scale=1.4)
    make_neon_dambrosios("Pole_S", (sign_x, sign_y - 0.10, sign_z),
                          face_axis='Y', face_sign=-1, scale=1.4)


# ════════════════════════════════════════════════════════════════
# THE RIVER
# ════════════════════════════════════════════════════════════════

def build_ground():
    """A single continuous ground plane covering the entire bayou-city
    area at z = -0.05. Without this, the world is a collection of
    floating asphalt patches (parking lot, frontage road, strip-mall
    lot, opposite shore) with unfilled gray Godot-void between them.

    Real bayou-city ground is a mix of:
      · low dirt/scrub between developed lots
      · grass patches around houses
      · concrete sidewalks along roads
    We approximate that with one base layer (warm dirt/grass tone)
    plus smaller patches of sidewalk and lawn dropped on top."""
    # Base ground — covers from west of the highway overpass to east
    # of the opposite shore, full N-S length of the world.
    make_box("Ground_Base", (10.0, 0.0, -0.10), (340.0, 340.0, 0.10),
             (0.34, 0.32, 0.24, 1.0))   # warm dirt with a hint of green
    # Grass / scrub patches scattered to break up the uniform dirt
    grass_col = (0.30, 0.36, 0.22, 1.0)
    grass_patches = [
        # (cx, cy, w, l)
        (-90, -75, 22, 14),
        (-70, -55, 16, 12),
        (-95, -20, 20, 18),
        (-78,  20, 14, 16),
        (-92,  55, 20, 14),
        (-70,  85, 18, 12),
        ( 70, -75, 18, 14),
        ( 80, -25, 22, 16),
        ( 78,  20, 18, 14),
        ( 80,  60, 22, 16),
        ( 70,  95, 18, 14),
    ]
    for gi, (gx, gy, gw, gl) in enumerate(grass_patches):
        make_box(f"Ground_Grass_{gi}", (gx, gy, -0.04), (gw, gl, 0.02), grass_col)


def build_river():
    """The water plane the boat sits on. Extends east to the opposite
    (starboard) shore. The port side is the parking-lot land, not water."""
    river_extent_x = 80.0
    river_extent_y = 160.0
    # Center the river east of the boat (positive X bias)
    make_box("River_Water",
             (15.0, 0, RIVER_LEVEL_Z - 0.01),
             (river_extent_x, river_extent_y, 0.02),
             COL_RIVER,
             open_faces={'-Z'})


def build_road_network():
    """Driveways and sidewalks connecting the developed patches so the
    layout reads as a functional bayou-city block instead of floating
    asphalt islands.

    Connects:
      · frontage road ↔ parking-lot entrance (south curb cut)
      · frontage road ↔ gas-station forecourt
      · frontage road ↔ strip-mall lot
      · frontage road ↔ highway overpass (an access ramp to the west)
      · parking lot ↔ dock (a strip of asphalt continuing east)
    Plus concrete sidewalks along each major edge."""

    asphalt = (0.18, 0.18, 0.18, 1.0)
    concrete = (0.62, 0.60, 0.55, 1.0)
    line = (0.70, 0.62, 0.30, 1.0)

    # ── Sidewalk along the parking lot's west side (between lot and frontage)
    make_box("Sidewalk_LotW", (-43.0, 0.0, -0.02), (3.0, 36.0, 0.06), concrete)
    # ── Sidewalk along the strip mall's east side (between mall lot and frontage)
    make_box("Sidewalk_MallE", (-44.0, 30.0, -0.02), (1.4, 36.0, 0.06), concrete)
    # ── Sidewalk along the gas station's east side
    make_box("Sidewalk_GasE", (-44.0, -38.0, -0.02), (1.4, 20.0, 0.06), concrete)

    # ── Driveway from frontage road → parking lot (south curb cut)
    make_box("Drive_LotToFront_S", (-39.0, -16.5, -0.02), (8.0, 5.0, 0.04), asphalt)
    # painted lines
    make_box("Drive_LotToFront_S_line", (-39.0, -16.5, 0.005),
             (0.08, 4.5, 0.005), line)

    # ── Driveway from frontage road → parking lot (north curb cut)
    make_box("Drive_LotToFront_N", (-39.0, 16.5, -0.02), (8.0, 5.0, 0.04), asphalt)
    make_box("Drive_LotToFront_N_line", (-39.0, 16.5, 0.005),
             (0.08, 4.5, 0.005), line)

    # ── Gas-station forecourt apron + curb cut from frontage road
    make_box("Drive_GasApron", (-46.0, -38.0, -0.02), (14.0, 18.0, 0.04), asphalt)
    # entry/exit markings
    make_box("Drive_Gas_line_W", (-50.0, -38.0, 0.005), (0.08, 14.0, 0.005), line)
    make_box("Drive_Gas_line_E", (-42.0, -38.0, 0.005), (0.08, 14.0, 0.005), line)

    # ── Driveway from frontage to highway overpass (west, runs into the
    # distance — implies the highway has an on-ramp out west)
    make_box("Drive_HwyRamp", (-82.0, 60.0, -0.02), (60.0, 6.0, 0.04), asphalt)
    make_box("Drive_HwyRamp_line", (-82.0, 60.0, 0.005), (50.0, 0.08, 0.005), line)

    # ── Asphalt continuation from parking lot east curb to the dock
    # (so there's no gap between lot and dock — currently floats)
    make_box("Drive_LotToDock", (-15.0, 0.0, -0.02), (10.0, 16.0, 0.04), asphalt)
    make_box("Drive_LotToDock_line", (-15.0, 0.0, 0.005), (8.0, 0.08, 0.005), line)

    # ── Crosswalk paint where the parking-lot driveways meet the frontage
    crosswalk_col = (0.85, 0.82, 0.74, 1.0)
    for ci in range(6):
        cx_o = -42.0 + ci * 0.6
        make_box(f"Crosswalk_S_{ci}", (cx_o, -16.5, 0.008),
                 (0.30, 3.5, 0.005), crosswalk_col)
        make_box(f"Crosswalk_N_{ci}", (cx_o, 16.5, 0.008),
                 (0.30, 3.5, 0.005), crosswalk_col)


# ════════════════════════════════════════════════════════════════
# THE DOCK — wooden pier between parking lot and boat hull
# ════════════════════════════════════════════════════════════════

def build_dock():
    """Wooden dock running PARALLEL to the boat between the parking lot
    and the boat's port side. Long axis along Y (along the boat),
    short axis along X. Carries cargo, mooring bollards, lanterns,
    coiled rope, lobster traps."""
    DK_L = 14.0   # along the boat (Y)
    # X span: from parking east edge to boat port edge
    parking_east_x = (PARKING_X - 6.0) + 22.0/2.0   # lot_cx + lot_x_w/2 = -19
    boat_port_x = -BOAT_W / 2 - 0.5                  # boat hull port edge ≈ -6.5
    dock_x_start = parking_east_x + 0.4              # ≈ -18.6
    dock_x_end   = boat_port_x - 0.2                 # ≈ -6.7
    dock_cx = (dock_x_start + dock_x_end) / 2.0
    dock_w  = dock_x_end - dock_x_start              # ≈ 11.9
    dock_cy = 0.0                                    # centered on boat
    dock_z = DOCK_Z                                  # raised above water
    make_box("Dock_Deck", (dock_cx, dock_cy, dock_z), (dock_w, DK_L, 0.20), COL_DECK_WOOD)
    # Stringers under the deck (visible joists running along the long axis)
    for si, sy_str in enumerate([-DK_L/2 + 0.5, -DK_L/4, 0.0, DK_L/4, DK_L/2 - 0.5]):
        make_box(f"Dock_Stringer_{si}", (dock_cx, sy_str, dock_z - 0.18), (dock_w - 0.3, 0.10, 0.16), (0.28, 0.18, 0.10, 1.0))
    # Ramp from dock west edge down to the parking-lot curb
    ramp_top_x = dock_x_start
    ramp_btm_x = dock_x_start - 1.6
    make_ramp("Dock_RampToLot",
              (ramp_top_x, 0, dock_z + 0.10),
              (ramp_btm_x, 0, 0.12),
              2.4, 0.12, COL_DECK_WOOD, width_axis='Y')
    # ramp railings
    for side, sy_r in (("S", -1.20), ("N", 1.20)):
        make_box(f"Dock_RampRail_{side}_top",
                 ((ramp_top_x + ramp_btm_x) / 2, sy_r, (dock_z + 0.10 + 0.12) / 2 + 0.75),
                 (abs(ramp_top_x - ramp_btm_x) + 0.1, 0.04, 0.04), COL_BRASS)
        for ii in range(3):
            t = (ii + 0.5) / 3.0
            rx_p = ramp_btm_x + t * (ramp_top_x - ramp_btm_x)
            rz_p = 0.12 + t * (dock_z + 0.10 - 0.12)
            make_box(f"Dock_RampPost_{side}_{ii}", (rx_p, sy_r, rz_p + 0.40),
                     (0.04, 0.04, 0.80), COL_BRASS)
    # plank lines along the long axis (Y) — visible deck stripes
    for i in range(int(DK_L / 0.30)):
        py_p = -DK_L/2 + 0.20 + i * 0.30
        make_box(f"Dock_Plank_{i}", (dock_cx, dock_cy + py_p, dock_z + 0.105),
                 (dock_w - 0.2, 0.04, 0.01), (0.30, 0.20, 0.12, 1.0))

    # Pilings driven from the river bed up THROUGH the dock deck —
    # they stand visibly proud of the deck (real docks always have
    # this: the piling tops cap the structure)
    piling_top_z = dock_z + 0.50          # 50cm proud of deck
    piling_bot_z = RIVER_LEVEL_Z - 1.8    # deep into river bed
    piling_h = piling_top_z - piling_bot_z
    piling_cz = (piling_top_z + piling_bot_z) / 2.0
    for row_idx, px_p in enumerate([dock_x_start + 0.5, dock_cx - 2.0, dock_cx + 2.0, dock_x_end - 0.5]):
        for ci, cy_p in enumerate([-DK_L/2 + 0.4, -DK_L/4, DK_L/4, DK_L/2 - 0.4]):
            make_cyl(f"Dock_Piling_{row_idx}_{ci}", (px_p, cy_p, piling_cz), 0.18, piling_h,
                     COL_PIER_WOOD, segments=6)
            # cap (a small darker disc on top of each piling)
            make_cyl(f"Dock_PilingCap_{row_idx}_{ci}", (px_p, cy_p, piling_top_z - 0.02),
                     0.22, 0.06, (0.22, 0.16, 0.10, 1.0), segments=6)

    # Mooring bollards on the BOAT side (east edge of dock) — these are
    # where the boat's lines tie off
    for i, by in enumerate([-DK_L/2 + 1.4, 0.0, DK_L/2 - 1.4]):
        bx_b = dock_x_end - 0.6
        make_cyl(f"Dock_Bollard_{i}", (bx_b, by, dock_z + 0.50), 0.22, 0.80, (0.32, 0.30, 0.26, 1.0), segments=8)
        make_cyl(f"Dock_Bollard_Cap_{i}", (bx_b, by, dock_z + 0.92), 0.28, 0.12, (0.32, 0.30, 0.26, 1.0), segments=8)
        # mooring rope arcing up to the boat's hull (X direction from bollard to boat)
        for ri in range(6):
            rt = ri / 5.0
            rx_r = bx_b + rt * (boat_port_x + 0.2 - bx_b)
            ry_r = by
            rz_r = dock_z + 0.92 + rt * 1.40
            sag = math.sin(rt * math.pi) * 0.20
            make_box(f"Dock_Rope_{i}_seg_{ri}", (rx_r, ry_r, rz_r - sag),
                     (0.20, 0.08, 0.08), (0.55, 0.40, 0.25, 1.0))

    # Cargo: crate stack on the north end of the dock
    crate_col = (0.55, 0.35, 0.20, 1.0)
    crate_band = (0.32, 0.22, 0.14, 1.0)
    crate_origin_x = dock_cx + 1.0
    crate_origin_y = DK_L/2 - 2.5
    for ci, (ox, oy, oz, sw, sl, sh) in enumerate([
        (0,    0,   0,    1.0, 1.0, 0.8),
        (1.1,  0,   0,    1.0, 1.0, 0.8),
        (0,    0,   0.85, 1.0, 1.0, 0.8),
        (1.1,  0,   0.85, 1.0, 1.0, 0.8),
        (0.55, -1.1, 0,   1.2, 1.2, 1.0),
        (0.55, -1.1, 1.05, 1.0, 1.0, 0.8),
    ]):
        cx_c = crate_origin_x + ox
        cy_c = crate_origin_y + oy
        cz_c = dock_z + 0.10 + oz + sh / 2.0
        make_box(f"Crate_{ci}", (cx_c, cy_c, cz_c), (sw, sl, sh), crate_col)
        make_box(f"Crate_{ci}_band1", (cx_c + sw/2 + 0.01, cy_c, cz_c), (0.03, sl, sh * 0.7), crate_band)
        make_box(f"Crate_{ci}_band2", (cx_c - sw/2 - 0.01, cy_c, cz_c), (0.03, sl, sh * 0.7), crate_band)

    # 3 rusty drums south end
    for di, (dx_off, dy_off) in enumerate([(0, 0), (0.85, 0.0), (0.42, -0.85)]):
        dx_d = dock_cx - 0.5 + dx_off
        dy_d = -DK_L/2 + 3.0 + dy_off
        make_cyl(f"Drum_{di}", (dx_d, dy_d, dock_z + 0.10 + 0.45), 0.40, 0.90, (0.55, 0.30, 0.20, 1.0), segments=8)
        make_cyl(f"Drum_{di}_top", (dx_d, dy_d, dock_z + 0.10 + 0.92), 0.42, 0.04, (0.42, 0.22, 0.14, 1.0), segments=8)
        make_cyl(f"Drum_{di}_band", (dx_d, dy_d, dock_z + 0.10 + 0.45), 0.42, 0.08, (0.32, 0.18, 0.12, 1.0), segments=8)

    # Coiled rope pile (center of dock, parking side)
    for ri in range(3):
        make_cyl(f"RopeCoil_{ri}", (dock_cx - 2.0, dock_cy + 1.0, dock_z + 0.12 + ri * 0.08),
                 0.45 - ri * 0.05, 0.07, (0.55, 0.40, 0.25, 1.0), segments=10)

    # Lobster trap stack
    trap_col = (0.40, 0.30, 0.18, 1.0)
    for ti, ox in enumerate([0, 0.85, 1.7]):
        tx_p = dock_cx - 2.5
        ty_p = dock_cy - 3.5
        make_box(f"LobsterTrap_{ti}", (tx_p + ox, ty_p, dock_z + 0.10 + 0.20), (0.70, 0.90, 0.40), trap_col)
        for si in range(4):
            make_box(f"LobsterTrap_{ti}_slat_{si}", (tx_p + ox + 0.37, ty_p + (-0.3 + si * 0.20), dock_z + 0.10 + 0.20),
                     (0.04, 0.04, 0.40), (0.55, 0.45, 0.30, 1.0))

    # Dock lanterns at the north and south corners
    for li, (lx_l, ly_l) in enumerate([(dock_x_start + 0.3, -DK_L/2 - 0.4),
                                         (dock_x_end - 0.3,   DK_L/2 + 0.4)]):
        make_cyl(f"DockLamp_Pole_{li}", (lx_l, ly_l, dock_z + 1.5), 0.08, 3.0, (0.30, 0.22, 0.14, 1.0), segments=6)
        make_box(f"DockLamp_Housing_{li}", (lx_l, ly_l, dock_z + 3.1), (0.30, 0.30, 0.40), (0.20, 0.18, 0.14, 1.0))
        make_box(f"DockLamp_Glow_{li}",    (lx_l, ly_l, dock_z + 3.0), (0.22, 0.22, 0.26), (1.0, 0.78, 0.36, 1.0))
        make_prism(f"DockLamp_Cap_{li}", (lx_l, ly_l, dock_z + 3.32), (0.34, 0.34, 0.16), (0.20, 0.18, 0.14, 1.0), pitch_axis='Y')

    # Dock railings on N/S edges (open on the boat side and parking side)
    for side, sy_e in (("S", -DK_L/2 - 0.05), ("N", DK_L/2 + 0.05)):
        make_box(f"Dock_Rail_{side}_top", (dock_cx, sy_e, dock_z + 1.0), (dock_w - 0.4, 0.05, 0.05), COL_BRASS)
        make_box(f"Dock_Rail_{side}_mid", (dock_cx, sy_e, dock_z + 0.6), (dock_w - 0.4, 0.04, 0.04), COL_BRASS)
        for ii in range(int((dock_w - 0.4) / 0.6)):
            sx_e = dock_x_start + 0.3 + ii * 0.6
            make_box(f"Dock_Spindle_{side}_{ii}", (sx_e, sy_e, dock_z + 0.55), (0.04, 0.04, 0.95), (0.32, 0.30, 0.26, 1.0))


# ════════════════════════════════════════════════════════════════
# OPPOSITE SHORELINE
# ════════════════════════════════════════════════════════════════

def build_opposite_shore():
    """Far STARBOARD shore (east side, across the river): industrial
    sprawl with refinery, water tower, smokestack plumes, billboards,
    power lines, plus a tree line."""
    shore_x = OPPOSITE_X
    shore_w = 18.0
    shore_l = 220.0       # extended from 110 so the shore runs the full river length, no cutoff
    shore_z = RIVER_LEVEL_Z + 0.20
    # Shore land mass — extends FURTHER east (+X) from shore_x
    make_box("OppositeShore_Land",
             (shore_x + shore_w / 2, 0, shore_z),
             (shore_w, shore_l, 0.40),
             COL_SHORELINE)
    # Riprap line at the river-facing edge (west edge of the shore strip)
    rip_col = (0.42, 0.38, 0.32, 1.0)
    for i in range(40):
        ry = -shore_l/2 + 2.0 + i * (shore_l - 4.0) / 39.0
        offset = ((i * 17) % 7 - 3) * 0.08
        size = 0.50 + ((i * 13) % 5) * 0.12
        make_box(f"Shore_Rock_{i}", (shore_x - 0.5 + offset, ry, RIVER_LEVEL_Z + 0.22),
                 (size, size, size * 0.7), rip_col)

    # Wider variety of buildings — refinery cluster + warehouses + small structures
    # dx is offset INLAND from the shoreline. With the shore now on the
    # starboard (+X) side, inland is the +X direction, so dx values are
    # positive. Buildings spread along the full 220m shoreline so the
    # highway / industrial sprawl doesn't cut off in wide shots.
    buildings = [
        (1.5,  -98.0,  4.0,  5.0,  5.0,  None, 'shed'),
        (3.0,  -86.0,  6.0,  8.0,  7.5,  None, 'warehouse'),
        (2.0,  -74.0,  5.0,  6.0,  6.0,  None, 'shed'),
        (5.0,  -60.0,  7.5, 10.0, 11.0,  None, 'refinery'),
        (3.5,  -48.0,  6.0,  7.0,  7.5,  None, 'warehouse'),
        (1.0,  -42.0,  4.0,  6.0,  4.0,  None, 'shed'),
        (2.5,  -32.0,  6.0,  7.0,  6.5,  None, 'warehouse'),
        (4.0,  -22.0,  6.5,  8.5,  8.0,  None, 'warehouse'),
        (5.5,  -10.0,  8.0, 10.0, 12.0,  None, 'refinery'),
        (6.0,   2.0,   8.5, 12.0, 14.0,  None, 'refinery'),
        (3.0,  12.0,   5.0,  6.0,  7.0,  None, 'warehouse'),
        (1.5,  20.0,   4.0,  5.0,  5.5,  None, 'shed'),
        (4.0,  30.0,   7.0,  9.0, 10.0,  None, 'warehouse'),
        (2.0,  40.0,   5.0,  6.5,  6.5,  None, 'warehouse'),
        (3.5,  54.0,   6.5,  8.0,  8.5,  None, 'warehouse'),
        (5.5,  68.0,   8.0,  9.0, 12.0,  None, 'refinery'),
        (2.0,  82.0,   5.0,  6.5,  6.0,  None, 'warehouse'),
        (1.5,  94.0,   4.0,  5.0,  5.0,  None, 'shed'),
    ]
    lit = (0.95, 0.78, 0.40, 1.0)
    dark = (0.18, 0.16, 0.14, 1.0)
    for i, (dx, y, w, l, h, col_o, kind) in enumerate(buildings):
        bx = shore_x + dx
        body_col = col_o if col_o else COL_FAR_BUILDING
        if kind == 'refinery':
            body_col = (0.36, 0.32, 0.28, 1.0)
        elif kind == 'shed':
            body_col = (0.46, 0.40, 0.32, 1.0)
        make_box(f"OppositeBldg_{i}", (bx, y, shore_z + h / 2), (w, l, h), body_col)
        # window grid on the river-facing (-X) side — the side facing
        # toward the boat
        rows = max(2, int(h / 2.2))
        cols = max(2, int(l / 2.0))
        for ri in range(rows):
            for ci in range(cols):
                wx = bx - w/2 - 0.02
                wy = y - l/2 + (ci + 0.5) * (l / cols)
                wz = shore_z + 1.0 + (ri + 0.5) * ((h - 1.0) / rows)
                seed = (i * 23 + ri * 7 + ci * 11) & 0xFF
                col = lit if (seed % 100) < 35 else dark
                make_box(f"OppositeBldg_{i}_win_{ri}_{ci}", (wx, wy, wz),
                         (0.04, l / cols * 0.55, (h - 1.0) / rows * 0.55), col)
        # parapet / roof cap
        make_box(f"OppositeBldg_{i}_cap", (bx, y, shore_z + h + 0.15),
                 (w + 0.2, l + 0.2, 0.30), (0.32, 0.30, 0.26, 1.0))
        # refinery extras: smokestack rising from the roof
        if kind == 'refinery':
            make_cyl(f"OppositeBldg_{i}_Stack", (bx + 1.0, y - 1.0, shore_z + h + 4.5),
                     0.50, 9.0, (0.24, 0.20, 0.16, 1.0), segments=8)
            make_cyl(f"OppositeBldg_{i}_StackCap", (bx + 1.0, y - 1.0, shore_z + h + 9.1),
                     0.65, 0.20, COL_BRASS, segments=8)
            # smoke plume drifting downwind
            for pi in range(5):
                make_box(f"OppositeBldg_{i}_Smoke_{pi}",
                         (bx + 1.0 + pi * 1.2, y - 1.0 - pi * 0.4, shore_z + h + 9.5 + pi * 0.6),
                         (1.4 + pi * 0.3, 1.4 + pi * 0.3, 0.7 + pi * 0.15),
                         (0.55, 0.50, 0.46, 1.0))
            # exterior pipework on the RIVER-facing wall (-X side of the building)
            for pi in range(3):
                pz = shore_z + 1.5 + pi * 1.4
                make_cyl(f"OppositeBldg_{i}_Pipe_{pi}", (bx - w/2 - 0.30, y, pz),
                         0.18, l - 0.4, (0.32, 0.30, 0.28, 1.0), segments=6, axis='Y')
                make_box(f"OppositeBldg_{i}_PipeSup_{pi}", (bx - w/2 - 0.16, y, pz - 0.25),
                         (0.18, 0.10, 0.50), (0.32, 0.30, 0.28, 1.0))
        # warehouse: rolling door on the river-facing (-X) side
        if kind == 'warehouse':
            door_col = (0.32, 0.30, 0.26, 1.0)
            make_box(f"OppositeBldg_{i}_Door", (bx - w/2 - 0.02, y, shore_z + 1.6),
                     (0.05, l * 0.4, 3.0), door_col)
            for di in range(4):
                make_box(f"OppositeBldg_{i}_DoorLine_{di}", (bx - w/2 - 0.06, y, shore_z + 0.4 + di * 0.7),
                         (0.02, l * 0.4 - 0.1, 0.03), (0.18, 0.16, 0.14, 1.0))

    # ── WATER TOWER (silhouette landmark, far back / inland) ──
    wt_x = shore_x + 11.0
    wt_y = -2.0
    # 4 legs (cylinders)
    for li, (lx_off, ly_off) in enumerate([(-1.5, -1.5), (1.5, -1.5), (-1.5, 1.5), (1.5, 1.5)]):
        make_cyl(f"WaterTower_Leg_{li}", (wt_x + lx_off, wt_y + ly_off, shore_z + 8.0),
                 0.15, 16.0, (0.32, 0.28, 0.24, 1.0), segments=6)
    # cross braces
    for bi in range(3):
        bz = shore_z + 3.0 + bi * 4.5
        make_box(f"WaterTower_Brace_S_{bi}", (wt_x, wt_y - 1.5, bz), (3.0, 0.10, 0.10), (0.32, 0.28, 0.24, 1.0))
        make_box(f"WaterTower_Brace_N_{bi}", (wt_x, wt_y + 1.5, bz), (3.0, 0.10, 0.10), (0.32, 0.28, 0.24, 1.0))
        make_box(f"WaterTower_Brace_W_{bi}", (wt_x - 1.5, wt_y, bz), (0.10, 3.0, 0.10), (0.32, 0.28, 0.24, 1.0))
        make_box(f"WaterTower_Brace_E_{bi}", (wt_x + 1.5, wt_y, bz), (0.10, 3.0, 0.10), (0.32, 0.28, 0.24, 1.0))
    # tank
    make_cyl("WaterTower_Tank", (wt_x, wt_y, shore_z + 17.5), 2.5, 4.0, (0.55, 0.50, 0.44, 1.0), segments=10)
    make_prism("WaterTower_Roof", (wt_x, wt_y, shore_z + 19.5), (5.4, 5.4, 1.4), (0.34, 0.30, 0.26, 1.0), pitch_axis='X')
    # finial
    make_cyl("WaterTower_Finial", (wt_x, wt_y, shore_z + 20.8), 0.06, 0.80, (0.24, 0.20, 0.16, 1.0), segments=6)

    # ── BILLBOARD facing the river (sits right at the water's edge) ──
    bb_x = shore_x - 0.5
    bb_y = -12.0
    make_cyl("Billboard_Pole_L", (bb_x - 1.6, bb_y, shore_z + 3.5), 0.15, 7.0, (0.30, 0.28, 0.24, 1.0), segments=6)
    make_cyl("Billboard_Pole_R", (bb_x + 1.6, bb_y, shore_z + 3.5), 0.15, 7.0, (0.30, 0.28, 0.24, 1.0), segments=6)
    make_box("Billboard_Panel", (bb_x, bb_y, shore_z + 6.5), (4.5, 0.12, 2.5), (0.72, 0.62, 0.42, 1.0))
    make_box("Billboard_Frame_T", (bb_x, bb_y, shore_z + 7.8), (4.7, 0.16, 0.10), (0.30, 0.28, 0.24, 1.0))
    make_box("Billboard_Frame_B", (bb_x, bb_y, shore_z + 5.2), (4.7, 0.16, 0.10), (0.30, 0.28, 0.24, 1.0))
    # decorative band suggesting big lettering
    make_box("Billboard_Text", (bb_x, bb_y - 0.07, shore_z + 6.5), (3.6, 0.04, 0.80), (0.40, 0.16, 0.14, 1.0))

    # ── POWER-LINE PYLON row along the shore (between river and buildings) ──
    for pi, py in enumerate([-88.0, -60.0, -30.0, 0.0, 30.0, 60.0, 90.0]):
        pylon_x = shore_x - 4.0
        # tapered lattice tower (3 stacked boxes narrowing)
        for ti, (ts, tz_off, th) in enumerate([(2.2, 4.0, 8.0), (1.6, 11.5, 6.0), (1.0, 16.0, 3.0)]):
            make_box(f"Pylon_{pi}_seg_{ti}", (pylon_x, py, shore_z + tz_off), (ts, ts, th), (0.30, 0.28, 0.24, 1.0))
            # X-brace suggestion (just two diagonal-ish bars)
            make_box(f"Pylon_{pi}_seg_{ti}_xbrace_a", (pylon_x, py, shore_z + tz_off), (ts * 1.05, 0.06, 0.06), (0.30, 0.28, 0.24, 1.0))
            make_box(f"Pylon_{pi}_seg_{ti}_xbrace_b", (pylon_x, py, shore_z + tz_off), (0.06, ts * 1.05, 0.06), (0.30, 0.28, 0.24, 1.0))
        # cross-arm with insulators
        cx_z = shore_z + 19.0
        make_box(f"Pylon_{pi}_arm_top", (pylon_x, py, cx_z), (5.5, 0.20, 0.15), (0.30, 0.28, 0.24, 1.0))
        make_box(f"Pylon_{pi}_arm_low", (pylon_x, py, cx_z - 2.0), (4.5, 0.20, 0.15), (0.30, 0.28, 0.24, 1.0))
        # insulators
        for ii, ix in enumerate([-2.4, -1.0, 1.0, 2.4]):
            make_cyl(f"Pylon_{pi}_insulator_{ii}", (pylon_x + ix, py, cx_z + 0.30), 0.08, 0.40, (0.85, 0.80, 0.72, 1.0), segments=6)
        # finial / aircraft warning light
        make_cyl(f"Pylon_{pi}_finial", (pylon_x, py, shore_z + 19.5), 0.10, 0.80, (0.85, 0.20, 0.18, 1.0), segments=6)

    # Power-line cables between pylons (just thin horizontal boxes between adjacent pylons)
    pylon_ys = [-88.0, -60.0, -30.0, 0.0, 30.0, 60.0, 90.0]
    for ai in range(len(pylon_ys) - 1):
        ya = pylon_ys[ai]
        yb = pylon_ys[ai + 1]
        ymid = (ya + yb) / 2.0
        length = abs(yb - ya)
        for li, lx_off in enumerate([-2.4, -1.0, 1.0, 2.4]):
            make_box(f"PowerLine_{ai}_cable_{li}", (shore_x - 4.0 + lx_off, ymid, shore_z + 18.6),
                     (0.05, length, 0.05), (0.18, 0.18, 0.18, 1.0))

    # ── BIG TREE LINE — extended along the full 220m shoreline ──
    tree_positions = [
        -105, -98, -90, -82, -75, -68, -60, -53, -45, -38,
         -32, -25, -18, -11,  -5,  2,   8,   14,  21,  28,
          35,  42,  49,  56,  63,  70,  77,  84,  91,  98, 105,
    ]
    for i, y in enumerate(tree_positions):
        kind = i % 3  # 0 = cypress, 1 = pine, 2 = oak
        zig = ((i % 5) - 2) * 0.7
        # trees grow on the shore land mass, +X from shore_x (inland)
        tree_x = shore_x + 8.0 + zig
        canopy_color = COL_TREE_CANOPY_B if kind == 0 else (COL_TREE_CANOPY_A if kind == 1 else (0.36, 0.40, 0.26, 1.0))
        trunk_h = 7.0 if kind == 0 else (5.5 if kind == 1 else 5.0)
        trunk_low_h = trunk_h * 0.55
        trunk_up_h = trunk_h * 0.45
        make_cyl(f"OppoTree_{i}_trunk_low", (tree_x, y, shore_z + trunk_low_h / 2),
                 0.22, trunk_low_h, COL_TREE_TRUNK, segments=6)
        make_cyl(f"OppoTree_{i}_trunk_up",  (tree_x, y, shore_z + trunk_low_h + trunk_up_h / 2),
                 0.14, trunk_up_h, COL_TREE_TRUNK, segments=6)
        canopy_size = 3.4 if kind == 0 else (2.4 if kind == 1 else 3.6)
        canopy_base_z = shore_z + trunk_h - 0.4
        if kind == 1:
            # pine — conical: tapered cylinder stack (keeps the conifer shape)
            for ci, (r_mul, dz) in enumerate([(1.0, 0.0), (0.75, 0.9), (0.50, 1.7), (0.30, 2.4)]):
                cr = canopy_size * 0.5 * r_mul
                make_cyl(f"OppoTree_{i}_pine_{ci}", (tree_x, y, canopy_base_z + dz + cr * 0.5),
                         cr, cr * 1.2, canopy_color, segments=6)
        else:
            # cypress / oak — sphere clusters (organic, not boxy)
            for ci, (ox, oy, sz_mul, dz_off) in enumerate([
                (0.0, 0.0, 1.0, 0.4),
                (-0.6, 0.4, 0.70, 0.8),
                (0.6, -0.4, 0.75, 0.7),
                (0.0, 0.6, 0.55, 1.1),
            ]):
                cr = canopy_size * 0.55 * sz_mul
                make_sphere(f"OppoTree_{i}_canopy_{ci}",
                            (tree_x + ox, y + oy, canopy_base_z + dz_off + cr * 0.4),
                            cr,
                            canopy_color)

    # ── FOREGROUND scrub bushes at the river-facing shoreline ──
    bush_col = (0.30, 0.36, 0.22, 1.0)
    for bi, by in enumerate([-100, -88, -75, -62, -50, -36, -25, -14, -3,
                              7, 19, 28, 38, 47, 60, 72, 84, 96]):
        bx_b = shore_x - 0.8 + ((bi % 3) - 1) * 0.4
        for ci, (ox, oy, sz_v) in enumerate([(0.0, 0.0, 0.8), (-0.4, 0.2, 0.6), (0.4, -0.1, 0.65)]):
            make_box(f"Shore_Bush_{bi}_{ci}", (bx_b + ox, by + oy, shore_z + 0.40),
                     (sz_v, sz_v, sz_v * 0.7), bush_col)


# ════════════════════════════════════════════════════════════════
# OTHER BOATS IN THE RIVER
# ════════════════════════════════════════════════════════════════

def build_other_boats():
    """Multiple other vessels scattered across the river — tugboats,
    fishing skiffs, barge, small motor cruiser, rowboat, channel buoys."""
    # ── Tugboat (upriver, starboard / north-east of boat) ──
    tx, ty = 22.0, 28.0
    tz = RIVER_LEVEL_Z + 0.8
    make_box("Tugboat_Hull_low", (tx, ty, tz - 0.6), (4.2, 8.0, 0.6), COL_OTHER_BOAT_A)
    make_box("Tugboat_Hull_up",  (tx, ty, tz - 0.1), (4.0, 7.6, 0.5), COL_OTHER_BOAT_A)
    make_box("Tugboat_Hull_bow", (tx, ty - 4.2, tz - 0.4), (3.2, 0.7, 0.7), COL_OTHER_BOAT_A)
    make_box("Tugboat_Cabin",    (tx, ty - 1.0, tz + 0.7), (2.6, 3.0, 1.4), COL_HELM_WALL)
    make_prism("Tugboat_Cabin_Roof", (tx, ty - 1.0, tz + 1.40), (2.8, 3.2, 0.4), COL_HELM_ROOF, pitch_axis='X')
    make_cyl("Tugboat_Stack", (tx, ty - 0.5, tz + 2.2), 0.32, 1.8, COL_SMOKESTACK, segments=8)
    make_cyl("Tugboat_StackCap", (tx, ty - 0.5, tz + 3.05), 0.40, 0.10, COL_BRASS, segments=8)
    # ring bands on stack
    for ri in range(2):
        make_cyl(f"Tugboat_Stack_Ring_{ri}", (tx, ty - 0.5, tz + 1.8 + ri * 0.6), 0.36, 0.06, COL_BRASS, segments=8)
    make_box("Tugboat_Window", (tx, ty - 2.51, tz + 0.7), (1.6, 0.05, 0.5), COL_HELM_WINDOW)
    make_box("Tugboat_Win_Mullion_v", (tx, ty - 2.52, tz + 0.7), (0.04, 0.04, 0.5), COL_HELM_ROOF)
    make_box("Tugboat_Win_Mullion_h", (tx, ty - 2.52, tz + 0.7), (1.6, 0.04, 0.04), COL_HELM_ROOF)
    # rear deck cargo (small crates)
    for ci in range(2):
        make_box(f"Tugboat_Crate_{ci}", (tx + (-0.5 + ci * 1.0), ty + 2.5, tz + 0.4),
                 (0.7, 0.9, 0.7), (0.55, 0.35, 0.20, 1.0))
    # railings around the deck
    for side, sx_off in (("W", -1.95), ("E", 1.95)):
        make_box(f"Tugboat_Rail_{side}", (tx + sx_off, ty, tz + 0.6), (0.05, 6.5, 0.05), COL_BRASS)
        for ii in range(8):
            sy_off = -3.0 + ii * 0.85
            make_box(f"Tugboat_Spindle_{side}_{ii}", (tx + sx_off, ty + sy_off, tz + 0.4),
                     (0.04, 0.04, 0.50), COL_BRASS)
    # nav lights (red port / green starboard)
    make_box("Tugboat_NavL", (tx - 1.95, ty - 3.0, tz + 0.6), (0.10, 0.10, 0.15), (0.85, 0.18, 0.16, 1.0))
    make_box("Tugboat_NavR", (tx + 1.95, ty - 3.0, tz + 0.6), (0.10, 0.10, 0.15), (0.30, 0.85, 0.30, 1.0))
    # tires hung on hull as fenders
    for fi, fy in enumerate([-1.5, 0.0, 1.5]):
        make_cyl(f"Tugboat_Fender_{fi}", (tx - 2.15, ty + fy, tz - 0.4), 0.20, 0.20,
                 (0.10, 0.10, 0.10, 1.0), segments=8, axis='X')

    # ── Fishing skiff (downriver, starboard) ──
    sx, sy = 18.0, -22.0
    sz = RIVER_LEVEL_Z + 0.4
    make_box("Skiff_Hull_low", (sx, sy, sz - 0.30), (1.8, 4.5, 0.30), COL_OTHER_BOAT_B)
    make_box("Skiff_Hull_up",  (sx, sy, sz),       (1.6, 4.3, 0.30), COL_OTHER_BOAT_B)
    make_cyl("Skiff_MotorLeg", (sx, sy + 2.45, sz - 0.15), 0.06, 0.45, (0.18, 0.16, 0.14, 1.0), segments=6)
    make_box("Skiff_Motor", (sx, sy + 2.45, sz + 0.20), (0.30, 0.45, 0.40), COL_SMOKESTACK)
    make_box("Skiff_Bench", (sx, sy, sz + 0.18), (1.2, 0.30, 0.06), COL_DECK_WOOD)
    make_box("Skiff_Bow", (sx, sy - 2.40, sz - 0.05), (1.0, 0.6, 0.30), COL_OTHER_BOAT_B)
    # tackle box & rod on the bench
    make_box("Skiff_Tackle", (sx - 0.4, sy + 0.3, sz + 0.30), (0.35, 0.20, 0.18), (0.20, 0.35, 0.45, 1.0))
    make_box("Skiff_Rod",    (sx + 0.4, sy - 0.5, sz + 0.30), (0.04, 2.5, 0.04), (0.15, 0.15, 0.15, 1.0))

    # ── Anchored barge with containers (far downriver, starboard) ──
    bx, by = 12.0, -42.0
    bz = RIVER_LEVEL_Z + 0.5
    make_box("Barge_Hull", (bx, by, bz - 0.25), (5.5, 14.0, 0.6), COL_OTHER_BOAT_A)
    make_box("Barge_Deck", (bx, by, bz + 0.10), (5.4, 13.8, 0.10), COL_DECK_WOOD)
    # stacks of containers (varied colors)
    container_colors = [(0.55, 0.20, 0.16, 1.0), (0.30, 0.40, 0.50, 1.0),
                         (0.40, 0.42, 0.32, 1.0), (0.62, 0.50, 0.28, 1.0)]
    for i in range(3):
        for j in range(2):
            for k in range(2):
                cx = bx - 1.8 + i * 1.8
                cy = by - 5.0 + j * 3.5
                cz_c = bz + 0.95 + k * 1.5
                col = container_colors[(i + j + k) % len(container_colors)]
                make_box(f"Barge_Container_{i}_{j}_{k}", (cx, cy, cz_c),
                         (1.6, 3.2, 1.4), col)
                # container door details (just stripes for panel suggestion)
                make_box(f"Barge_Container_{i}_{j}_{k}_doorline_a", (cx, cy + 1.60, cz_c),
                         (1.6, 0.03, 1.4), (col[0] * 0.6, col[1] * 0.6, col[2] * 0.6, 1.0))
                make_box(f"Barge_Container_{i}_{j}_{k}_doorline_b", (cx + 0.40, cy + 1.61, cz_c),
                         (0.05, 0.04, 1.4), (col[0] * 0.6, col[1] * 0.6, col[2] * 0.6, 1.0))

    # ── Motor cruiser (small pleasure boat, starboard) ──
    mx, my = 28.0, -30.0
    mz_b = RIVER_LEVEL_Z + 0.6
    make_box("Cruiser_Hull_low", (mx, my, mz_b - 0.4), (2.6, 6.0, 0.6), (0.85, 0.82, 0.74, 1.0))
    make_box("Cruiser_Hull_up",  (mx, my, mz_b + 0.1), (2.4, 5.8, 0.5), (0.85, 0.82, 0.74, 1.0))
    make_box("Cruiser_Cabin",    (mx, my - 0.5, mz_b + 0.9), (2.0, 2.6, 1.0), (0.85, 0.82, 0.74, 1.0))
    make_prism("Cruiser_CabinRoof", (mx, my - 0.5, mz_b + 1.40), (2.2, 2.8, 0.30), (0.55, 0.20, 0.16, 1.0), pitch_axis='X')
    make_box("Cruiser_Windshield", (mx, my - 1.85, mz_b + 0.95), (1.6, 0.04, 0.50), COL_CAR_GLASS)
    make_box("Cruiser_BackWin",    (mx, my + 0.85, mz_b + 0.95), (1.6, 0.04, 0.50), COL_CAR_GLASS)
    # bow point
    make_box("Cruiser_Bow", (mx, my - 3.20, mz_b - 0.30), (1.6, 1.0, 0.40), (0.85, 0.82, 0.74, 1.0))
    # antenna
    make_cyl("Cruiser_Antenna", (mx + 0.7, my + 1.2, mz_b + 2.3), 0.02, 1.6, (0.20, 0.20, 0.20, 1.0), segments=4)
    # bimini top frame
    for bi, bx_b in enumerate([-0.8, 0.8]):
        make_cyl(f"Cruiser_BiminiFrame_{bi}", (mx + bx_b, my + 1.6, mz_b + 1.6), 0.04, 1.4, COL_BRASS, segments=4)

    # ── Rowboat (tied off near the bayou mouth) ──
    rbx, rby = 14.0, -8.0
    rbz = RIVER_LEVEL_Z + 0.2
    make_box("Rowboat_Hull", (rbx, rby, rbz - 0.10), (1.4, 3.4, 0.25), (0.42, 0.30, 0.20, 1.0))
    # benches
    for bi, byo in enumerate([-0.8, 0.0, 0.8]):
        make_box(f"Rowboat_Bench_{bi}", (rbx, rby + byo, rbz + 0.10), (1.2, 0.16, 0.05), (0.30, 0.20, 0.12, 1.0))
    # oars resting across the bow
    make_box("Rowboat_OarL", (rbx - 0.4, rby - 0.8, rbz + 0.15), (0.06, 2.2, 0.06), (0.55, 0.40, 0.25, 1.0))
    make_box("Rowboat_OarR", (rbx + 0.4, rby - 0.8, rbz + 0.15), (0.06, 2.2, 0.06), (0.55, 0.40, 0.25, 1.0))
    # oar blades
    make_box("Rowboat_OarL_blade", (rbx - 0.4, rby + 0.3, rbz + 0.15), (0.15, 0.50, 0.04), (0.55, 0.40, 0.25, 1.0))
    make_box("Rowboat_OarR_blade", (rbx + 0.4, rby + 0.3, rbz + 0.15), (0.15, 0.50, 0.04), (0.55, 0.40, 0.25, 1.0))

    # ── Channel marker buoys (3 floating in the starboard river) ──
    for bi, (buoyx, buoy_y, b_red) in enumerate([(8.0, -28.0, True), (14.0, 8.0, False),
                                                  (6.0, 16.0, True)]):
        b_col = (0.85, 0.20, 0.18, 1.0) if b_red else (0.30, 0.85, 0.30, 1.0)
        make_cyl(f"Buoy_{bi}_body", (buoyx, buoy_y, RIVER_LEVEL_Z + 0.3), 0.45, 0.70, b_col, segments=8)
        make_cyl(f"Buoy_{bi}_cap",  (buoyx, buoy_y, RIVER_LEVEL_Z + 0.70), 0.48, 0.10, (0.20, 0.18, 0.16, 1.0), segments=8)
        # light on top
        make_cyl(f"Buoy_{bi}_light", (buoyx, buoy_y, RIVER_LEVEL_Z + 0.90), 0.15, 0.20,
                 (1.0, 0.78, 0.40, 1.0) if b_red else (0.85, 1.0, 0.85, 1.0), segments=6)
        # mooring chain hint (a small cylinder going down into the water)
        make_cyl(f"Buoy_{bi}_chain", (buoyx, buoy_y, RIVER_LEVEL_Z - 0.4), 0.06, 0.8, (0.18, 0.18, 0.18, 1.0), segments=4)


# ════════════════════════════════════════════════════════════════
# THE BAYOU
# ════════════════════════════════════════════════════════════════

def build_bayou():
    """Navigable bayou east of the boat. References: Honey Island Swamp /
    Atchafalaya Basin — cypress-tupelo swamp with a winding open
    channel down the center wide enough for a flat-bottomed boat to
    pass. Mixed species, randomized sizes, organic placement.

    Tree species included:
      · bald cypress  (tall, knees, draping moss)
      · water tupelo  (shorter, swollen base, dense canopy)
      · live oak      (spread crown, gnarly multi-trunk)
      · palmetto      (short, fan canopy)
      · dead snag     (just a leaning broken trunk)

    A central CHANNEL (4m wide, running N-S) is kept clear of trees so
    the bayou actually reads as navigable water rather than a forest."""
    bayou_w = 40.0
    bayou_l = 90.0
    bayou_z = RIVER_LEVEL_Z + 0.02
    bayou_x = BAYOU_X
    CHANNEL_HALF = 2.5   # 5m-wide clear channel down the middle
    make_box("Bayou_Water",
             (bayou_x, 0, bayou_z - 0.005),
             (bayou_w, bayou_l, 0.01),
             COL_BAYOU_WATER,
             open_faces={'-Z'})

    # ── tree species helpers ──────────────────────────────────────
    def _hash(n):
        return (math.sin(n * 12.9898) * 43758.5453) % 1.0

    def _bald_cypress(tag, cx, cy, scale):
        trunk_h = 7.5 * scale
        seg = trunk_h / 3.0
        base_r = 0.45 * scale
        # flared swollen base — wider at waterline
        make_cyl(f"{tag}_base", (cx, cy, bayou_z + 0.30), base_r, 0.60, COL_TREE_TRUNK, segments=6)
        make_cyl(f"{tag}_trunk_low", (cx, cy, bayou_z + seg * 0.5 + 0.60),
                 0.32 * scale, seg, COL_TREE_TRUNK, segments=6)
        make_cyl(f"{tag}_trunk_mid", (cx, cy, bayou_z + seg * 1.5 + 0.60),
                 0.23 * scale, seg, COL_TREE_TRUNK, segments=6)
        make_cyl(f"{tag}_trunk_up",  (cx, cy, bayou_z + seg * 2.5 + 0.60),
                 0.15 * scale, seg, COL_TREE_TRUNK, segments=6)
        # Canopy — overlapping spheres (NOT boxes) for organic silhouette
        canopy_z = bayou_z + trunk_h + 0.60
        make_sphere(f"{tag}_canopy_a", (cx, cy, canopy_z + 0.7 * scale),
                    1.35 * scale, COL_TREE_CANOPY_B)
        make_sphere(f"{tag}_canopy_b", (cx - 0.45 * scale, cy + 0.35 * scale, canopy_z + 1.5 * scale),
                    1.10 * scale, COL_TREE_CANOPY_B)
        make_sphere(f"{tag}_canopy_c", (cx + 0.40 * scale, cy - 0.30 * scale, canopy_z + 2.1 * scale),
                    0.80 * scale, COL_TREE_CANOPY_B)
        make_sphere(f"{tag}_canopy_d", (cx + 0.10 * scale, cy + 0.50 * scale, canopy_z + 1.8 * scale),
                    0.65 * scale, COL_TREE_CANOPY_B)
        # knees around the base (irregular, varied heights)
        n_knees = 3 + int(_hash(cx * 7 + cy) * 3)
        for ki in range(n_knees):
            ang = _hash(cx + cy + ki * 17) * 6.28
            rad = base_r + 0.40 + _hash(cx + ki * 31) * 0.50
            kh = 0.20 + _hash(cy * 13 + ki) * 0.35
            kx = cx + math.cos(ang) * rad
            ky = cy + math.sin(ang) * rad
            make_cyl(f"{tag}_knee_{ki}", (kx, ky, bayou_z + kh / 2.0 + 0.05),
                     0.08 + _hash(ki * 7 + cx) * 0.05, kh, COL_TREE_TRUNK, segments=4)
        # moss strands (long, draping)
        n_moss = 1 + int(_hash(cx * 5 + cy * 3) * 4)
        for mi in range(n_moss):
            mx = cx + (_hash(cx + mi * 11) - 0.5) * 0.6
            my = cy + (_hash(cy + mi * 13) - 0.5) * 0.6
            mz = bayou_z + trunk_h * (0.55 + _hash(mi * 17) * 0.25) + 0.60
            mh = 0.7 + _hash(mi * 19 + cx) * 0.8
            make_box(f"{tag}_moss_{mi}", (mx, my, mz), (0.14, 0.14, mh), COL_MOSS)

    def _water_tupelo(tag, cx, cy, scale):
        # Tupelo: distinct swollen base, shorter than cypress, broader canopy
        trunk_h = 5.5 * scale
        base_r = 0.70 * scale
        make_cyl(f"{tag}_base", (cx, cy, bayou_z + 0.40), base_r, 0.80, COL_TREE_TRUNK, segments=8)
        make_cyl(f"{tag}_trunk", (cx, cy, bayou_z + trunk_h / 2 + 0.80),
                 0.28 * scale, trunk_h, COL_TREE_TRUNK, segments=6)
        canopy_z = bayou_z + trunk_h + 0.80
        # Tupelo canopy: wider, rounder than cypress — three big spheres
        canopy_col = (0.24, 0.34, 0.16, 1.0)
        make_sphere(f"{tag}_canopy_a", (cx, cy, canopy_z + 0.9 * scale),
                    1.85 * scale, canopy_col)
        make_sphere(f"{tag}_canopy_b", (cx - 0.6 * scale, cy + 0.4 * scale, canopy_z + 1.7 * scale),
                    1.30 * scale, canopy_col)
        make_sphere(f"{tag}_canopy_c", (cx + 0.7 * scale, cy - 0.4 * scale, canopy_z + 1.5 * scale),
                    1.20 * scale, canopy_col)
        make_sphere(f"{tag}_canopy_d", (cx + 0.2 * scale, cy + 0.7 * scale, canopy_z + 2.0 * scale),
                    0.90 * scale, canopy_col)

    def _live_oak(tag, cx, cy, scale):
        # Spread-crown oak: thick gnarly trunk, low spreading branches, wide canopy
        trunk_h = 3.5 * scale
        trunk_col = (0.26, 0.20, 0.14, 1.0)
        make_cyl(f"{tag}_trunk", (cx, cy, bayou_z + trunk_h / 2 + 0.10),
                 0.50 * scale, trunk_h, trunk_col, segments=6)
        # 3-4 main branches angling out from the top of the trunk
        branch_z = bayou_z + trunk_h + 0.10
        canopy_col = (0.30, 0.36, 0.22, 1.0)
        for bi in range(4):
            ang = bi * (3.14159 / 2.0) + _hash(cx + bi * 23) * 0.5
            br_len = 2.5 * scale
            # angled branch as a proper tube cylinder between trunk top and branch tip
            bx_tip = cx + math.cos(ang) * br_len
            by_tip = cy + math.sin(ang) * br_len
            bz_tip = branch_z + 0.7 * scale
            make_tube_segment(f"{tag}_branch_{bi}",
                              (cx, cy, branch_z),
                              (bx_tip, by_tip, bz_tip),
                              0.16 * scale, trunk_col, segments=6)
            # leaf cluster sphere at the end of each branch
            make_sphere(f"{tag}_cluster_{bi}", (bx_tip, by_tip, bz_tip + 0.4 * scale),
                        1.30 * scale, canopy_col)
        # central canopy mass — a big sphere over the trunk
        make_sphere(f"{tag}_canopy_main", (cx, cy, branch_z + 1.8 * scale),
                    1.90 * scale, canopy_col)

    def _palmetto(tag, cx, cy, scale):
        # Short palmetto — squat trunk + radiating fronds
        trunk_h = 1.2 * scale
        make_cyl(f"{tag}_trunk", (cx, cy, bayou_z + trunk_h / 2 + 0.05),
                 0.25 * scale, trunk_h, (0.32, 0.22, 0.14, 1.0), segments=6)
        frond_z = bayou_z + trunk_h + 0.05
        frond_col = (0.36, 0.44, 0.22, 1.0)
        # 6 fan-blade fronds radiating outward
        for fi in range(6):
            ang = fi * (3.14159 / 3.0)
            fx = cx + math.cos(ang) * 0.7 * scale
            fy = cy + math.sin(ang) * 0.7 * scale
            # the fan width spans along the angle direction
            make_box(f"{tag}_frond_{fi}", (fx, fy, frond_z + 0.2 * scale),
                     (1.0 * scale, 1.0 * scale, 0.10 * scale), frond_col)
        # central crown
        make_box(f"{tag}_crown", (cx, cy, frond_z + 0.15 * scale),
                 (0.5 * scale, 0.5 * scale, 0.25 * scale), frond_col)

    def _dead_snag(tag, cx, cy, scale):
        # Just a leaning broken trunk with a couple of stub branches
        h = 4.5 * scale
        # the trunk is slightly tilted (we'll just offset top)
        lean_x = (_hash(cx + 13) - 0.5) * 0.6
        lean_y = (_hash(cy + 7) - 0.5) * 0.6
        # use a long thin box for the trunk
        make_box(f"{tag}_trunk", (cx + lean_x * 0.5, cy + lean_y * 0.5, bayou_z + h / 2 + 0.05),
                 (0.30 * scale, 0.30 * scale, h), (0.22, 0.16, 0.12, 1.0))
        # broken top
        make_box(f"{tag}_broken_top", (cx + lean_x, cy + lean_y, bayou_z + h + 0.05),
                 (0.50 * scale, 0.50 * scale, 0.20), (0.18, 0.14, 0.10, 1.0))
        # 2 stub branches
        for si in range(2):
            ang = _hash(cx + si * 11) * 6.28
            sx_ = cx + math.cos(ang) * 0.8 * scale
            sy_ = cy + math.sin(ang) * 0.8 * scale
            sz_ = bayou_z + h * (0.55 + si * 0.20) + 0.05
            make_box(f"{tag}_stub_{si}", (sx_, sy_, sz_),
                     (0.4 * scale, 0.10 * scale, 0.10 * scale), (0.18, 0.14, 0.10, 1.0))

    # ── PLACE TREES — randomized organic positions, leaving the
    # central channel clear ──
    tree_count = 0
    placed = []
    rng_seed = 7
    species_funcs = [_bald_cypress, _water_tupelo, _live_oak, _palmetto, _dead_snag]
    species_weights = [0.40, 0.25, 0.10, 0.18, 0.07]
    cum_weights = []
    acc = 0.0
    for w in species_weights:
        acc += w
        cum_weights.append(acc)

    # Generate ~50 tree positions via Poisson-like sampling with min distance
    MIN_DIST_SQ = 2.6 * 2.6
    attempts = 0
    while tree_count < 50 and attempts < 800:
        attempts += 1
        u = _hash(rng_seed * 7.123 + attempts)
        v = _hash(rng_seed * 11.234 + attempts * 3)
        local_x = (u - 0.5) * (bayou_w - 4)
        local_y = (v - 0.5) * (bayou_l - 4)
        # skip the central N-S channel
        if abs(local_x) < CHANNEL_HALF + 0.3 * _hash(attempts * 19):
            continue
        cx = bayou_x + local_x
        cy = local_y
        # reject if too close to an existing tree
        too_close = False
        for (px, py) in placed:
            if (cx - px) ** 2 + (cy - py) ** 2 < MIN_DIST_SQ:
                too_close = True
                break
        if too_close:
            continue
        placed.append((cx, cy))
        # pick species
        sp = _hash(attempts * 23.7)
        species_idx = 0
        for si, cw in enumerate(cum_weights):
            if sp < cw:
                species_idx = si
                break
        # scale varies 0.7 to 1.4
        scale = 0.7 + _hash(attempts * 29.31) * 0.7
        tag = f"BayouTree_{tree_count:03d}"
        species_funcs[species_idx](tag, cx, cy, scale)
        tree_count += 1

    # ── REEDS & GRASS clumps at the bayou edges ──
    reed_col = (0.42, 0.46, 0.22, 1.0)
    for ri in range(30):
        rx = bayou_x - 18.0 + ((ri * 73) % 36)
        ry = -38.0 + ((ri * 89) % 76)
        # cluster of 4-5 thin tall boxes per reed clump
        for ki in range(5):
            offx = ((ri * 13 + ki * 7) % 7 - 3) * 0.06
            offy = ((ri * 19 + ki * 11) % 7 - 3) * 0.06
            rh = 0.6 + ((ri * 17 + ki) % 3) * 0.2
            make_box(f"Reed_{ri}_{ki}", (rx + offx, ry + offy, bayou_z + rh / 2 + 0.05),
                     (0.04, 0.04, rh), reed_col)

    # ── LILY PADS (flat disks on water) ──
    pad_col = (0.30, 0.45, 0.22, 1.0)
    pad_flower = (0.92, 0.82, 0.72, 1.0)
    for li in range(18):
        lx_p = bayou_x - 14.0 + ((li * 67) % 28)
        ly_p = -34.0 + ((li * 53) % 68)
        make_cyl(f"LilyPad_{li}", (lx_p, ly_p, bayou_z + 0.03),
                 0.35 + ((li * 23) % 4) * 0.06, 0.04, pad_col, segments=6)
        if li % 4 == 0:
            make_cyl(f"LilyPad_{li}_flower", (lx_p + 0.10, ly_p, bayou_z + 0.10),
                     0.12, 0.10, pad_flower, segments=6)

    # ── FALLEN LOGS (alligator-suggesting half-submerged boxes) ──
    log_col = (0.22, 0.16, 0.12, 1.0)
    for li, (lx_l, ly_l, lyaw) in enumerate([
        (bayou_x - 6, -18, 0.3), (bayou_x + 4, 0, -0.5),
        (bayou_x + 8, 22, 0.1), (bayou_x - 12, 18, -0.2),
    ]):
        make_box(f"FallenLog_{li}", (lx_l, ly_l, bayou_z + 0.10),
                 (0.6, 3.0, 0.30), log_col)
        # exposed root cluster on one end
        for ri in range(3):
            make_box(f"FallenLog_{li}_root_{ri}", (lx_l + ((ri % 2) * 0.3 - 0.15), ly_l - 1.6, bayou_z + 0.25 + ri * 0.05),
                     (0.10, 0.30, 0.08), log_col)

    # ── FISHING CAMP SHACK on stilts (north end) ──
    sh_x = bayou_x + 12.0
    sh_y = 28.0
    # 4 stilts going down into the water
    for si, (sx_s, sy_s) in enumerate([(-1.6, -1.6), (1.6, -1.6), (-1.6, 1.6), (1.6, 1.6)]):
        make_cyl(f"Shack_Stilt_{si}", (sh_x + sx_s, sh_y + sy_s, bayou_z + 1.0), 0.18, 2.5,
                 COL_PIER_WOOD, segments=6)
        # cross-bracing
        if si < 2:
            make_box(f"Shack_Brace_{si}", (sh_x + sx_s, sh_y + sy_s + 1.6, bayou_z + 0.6),
                     (0.10, 3.2, 0.10), COL_PIER_WOOD)
    # platform deck
    make_box("Shack_Platform", (sh_x, sh_y, bayou_z + 2.3), (4.0, 4.0, 0.20), COL_PIER_WOOD)
    # plank stripes
    for pi in range(6):
        make_box(f"Shack_Plank_{pi}", (sh_x, sh_y - 1.5 + pi * 0.6, bayou_z + 2.41),
                 (3.9, 0.04, 0.02), (0.30, 0.20, 0.12, 1.0))
    # shack walls
    sw_h = 2.4
    make_box("Shack_Wall_S", (sh_x, sh_y - 1.5, bayou_z + 2.3 + sw_h/2 + 0.10), (3.0, 0.10, sw_h), (0.46, 0.40, 0.32, 1.0))
    make_box("Shack_Wall_N", (sh_x, sh_y + 1.5, bayou_z + 2.3 + sw_h/2 + 0.10), (3.0, 0.10, sw_h), (0.46, 0.40, 0.32, 1.0))
    make_box("Shack_Wall_W", (sh_x - 1.5, sh_y, bayou_z + 2.3 + sw_h/2 + 0.10), (0.10, 3.0, sw_h), (0.46, 0.40, 0.32, 1.0))
    make_box("Shack_Wall_E", (sh_x + 1.5, sh_y, bayou_z + 2.3 + sw_h/2 + 0.10), (0.10, 3.0, sw_h), (0.46, 0.40, 0.32, 1.0))
    # door (a darker rectangle)
    make_box("Shack_Door", (sh_x - 0.6, sh_y - 1.51, bayou_z + 2.3 + 1.0), (0.80, 0.05, 1.9), (0.22, 0.16, 0.10, 1.0))
    # small window
    make_box("Shack_Window", (sh_x + 0.8, sh_y - 1.51, bayou_z + 2.3 + 1.5), (0.60, 0.05, 0.50), (1.0, 0.78, 0.40, 1.0))
    make_box("Shack_Window_Mullion", (sh_x + 0.8, sh_y - 1.52, bayou_z + 2.3 + 1.5), (0.04, 0.05, 0.50), (0.20, 0.16, 0.10, 1.0))
    # sloped tin roof
    make_prism("Shack_Roof", (sh_x, sh_y, bayou_z + 2.3 + sw_h + 0.10), (3.4, 3.4, 0.9), (0.46, 0.42, 0.40, 1.0), pitch_axis='Y')
    # rusty stovepipe poking out
    make_cyl("Shack_Stovepipe", (sh_x - 0.8, sh_y + 0.5, bayou_z + 2.3 + sw_h + 1.0), 0.12, 1.4, (0.32, 0.20, 0.16, 1.0), segments=6)
    make_cyl("Shack_Stovepipe_cap", (sh_x - 0.8, sh_y + 0.5, bayou_z + 2.3 + sw_h + 1.75), 0.20, 0.10, (0.42, 0.30, 0.24, 1.0), segments=6)
    # ladder going down from the platform
    for li_l in range(5):
        make_box(f"Shack_Ladder_step_{li_l}", (sh_x - 1.9, sh_y - 1.4, bayou_z + 0.4 + li_l * 0.45),
                 (0.40, 0.06, 0.04), (0.42, 0.30, 0.20, 1.0))
    for sv in (-1.9, -1.9):
        make_box(f"Shack_Ladder_rail", (sv, sh_y - 1.4, bayou_z + 1.4), (0.06, 0.06, 2.4), (0.42, 0.30, 0.20, 1.0))
    # nets hanging on the side wall
    make_box("Shack_Net", (sh_x + 1.55, sh_y - 0.5, bayou_z + 2.3 + 1.2), (0.04, 1.0, 1.2), (0.55, 0.50, 0.30, 1.0))

    # ── ABANDONED FLAT-BOTTOM BOAT half-sunk in the reeds ──
    ab_x = bayou_x - 10.0
    ab_y = 4.0
    make_box("AbandonBoat_Hull", (ab_x, ab_y, bayou_z + 0.10), (1.5, 3.4, 0.30), (0.42, 0.30, 0.18, 1.0))
    make_box("AbandonBoat_Bench", (ab_x, ab_y, bayou_z + 0.30), (1.3, 0.20, 0.05), (0.30, 0.22, 0.14, 1.0))
    # broken oar across the hull
    make_box("AbandonBoat_OarBroken", (ab_x + 0.4, ab_y - 0.3, bayou_z + 0.40), (0.06, 1.4, 0.06), (0.55, 0.40, 0.25, 1.0))

    # ── WOODEN PIER (existing, expanded) ──
    pier_x = bayou_x - 16.0
    pier_y = -2.0
    pier_z = RIVER_LEVEL_Z + 0.30
    make_box("Bayou_Pier", (pier_x, pier_y, pier_z), (4.0, 1.6, 0.14), COL_PIER_WOOD)
    for pi_pl in range(8):
        make_box(f"Bayou_Pier_Plank_{pi_pl}", (pier_x - 1.8 + pi_pl * 0.50, pier_y, pier_z + 0.08),
                 (0.04, 1.5, 0.02), (0.30, 0.20, 0.12, 1.0))
    for i in range(6):
        px = pier_x - 1.8 + (i % 3) * 1.8
        py = pier_y - 0.7 + (i // 3) * 1.4
        make_cyl(f"Pier_Piling_{i}", (px, py, RIVER_LEVEL_Z + 0.05),
                 0.14, 0.80, COL_PIER_WOOD, segments=6)
    # pier railing
    for side, sx_o in (("W", -2.0), ("E", 2.0)):
        make_box(f"Bayou_Pier_Rail_{side}", (pier_x + sx_o, pier_y, pier_z + 0.6),
                 (0.05, 1.4, 0.05), COL_BRASS)

    # ── PADDLEBOAT moored at the bayou pier ──
    pb_x = pier_x - 0.5
    pb_y = pier_y + 1.5
    make_box("Paddleboat_Hull", (pb_x, pb_y, bayou_z + 0.10), (1.2, 2.4, 0.30), (0.42, 0.30, 0.18, 1.0))
    # bench
    make_box("Paddleboat_Bench", (pb_x, pb_y, bayou_z + 0.30), (1.0, 0.18, 0.05), (0.30, 0.22, 0.14, 1.0))
    # paddle/pole lying across
    make_box("Paddleboat_Pole", (pb_x + 0.3, pb_y, bayou_z + 0.40), (0.05, 2.4, 0.05), (0.55, 0.40, 0.25, 1.0))


# ════════════════════════════════════════════════════════════════
# EXPORT
# ════════════════════════════════════════════════════════════════

def export_glb():
    out_dir = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), OUTPUT_DIR))
    os.makedirs(out_dir, exist_ok=True)
    out_path = os.path.join(out_dir, OUTPUT_NAME)

    print(f"\n[build_riverfront] exporting to {out_path}")
    print(f"[build_riverfront] scene objects: {len(bpy.context.scene.objects)}")

    bpy.ops.object.select_all(action='SELECT')
    base = {
        'filepath': out_path, 'export_format': 'GLB',
        'use_selection': False, 'export_apply': True,
        'export_lights': False, 'export_cameras': False,
    }
    rna = bpy.ops.export_scene.gltf.get_rna_type()
    legacy = {}
    if 'export_colors' in rna.properties: legacy['export_colors'] = True
    if 'export_normals' in rna.properties: legacy['export_normals'] = True

    try:
        result = bpy.ops.export_scene.gltf(**base, **legacy)
        print(f"[build_riverfront] export result: {result}")
    except Exception as e:
        print(f"[build_riverfront] ✗ EXPORT FAILED: {e}")
        import traceback; traceback.print_exc()
        raise

    if os.path.exists(out_path):
        size = os.path.getsize(out_path)
        print(f"[build_riverfront] ✓ wrote {out_path} ({size} bytes)")
    else:
        raise RuntimeError("GLB not written")


def build_near_shore():
    """The PORT-side (-X) near shore behind the parking lot. Provides
    set decoration so when the player looks west / north / south from
    the parking lot they see civilisation, not empty plane.

    Layout:
      · A frontage road parallel to the parking lot, with a gas
        station and a strip mall as the foreground commercial strip.
      · A second tier of bayou trees + industrial silhouettes further
        west to fill the deep distance.
      · A highway overpass crossing in the far distance (N-S) for
        depth — visible behind the strip-mall roofline."""

    NEAR_FRONTAGE_X = -52.0    # commercial strip just west of the parking lot
    NEAR_DEEP_X = -85.0        # second tier of distance
    NEAR_HIGHWAY_X = -115.0    # far-distance highway overpass
    shore_z = -0.05
    asphalt = (0.18, 0.18, 0.18, 1.0)
    curb = (0.55, 0.52, 0.48, 1.0)

    # ── Frontage road running N-S parallel to the parking lot ──
    make_box("NearShore_Road", (NEAR_FRONTAGE_X + 12.0, 0, shore_z),
             (8.0, 220.0, 0.04), asphalt)
    # painted yellow center line, dashed
    for i in range(36):
        ly = -108 + i * 6.0
        make_box(f"NearShore_RoadLine_{i}", (NEAR_FRONTAGE_X + 12.0, ly, shore_z + 0.02),
                 (0.10, 2.5, 0.005), (0.70, 0.62, 0.30, 1.0))

    # ════════════════════════════════════════════════════════════
    # GAS STATION — south end of the frontage road
    # ════════════════════════════════════════════════════════════
    gs_x = NEAR_FRONTAGE_X
    gs_y = -38.0
    # Canopy roof — large flat slab over the pumps
    canopy_z = 4.6
    make_box("GasStation_Canopy", (gs_x, gs_y, canopy_z),
             (10.0, 8.0, 0.40), (0.85, 0.82, 0.74, 1.0))
    # Canopy underside trim (where the bright fluorescent lights would be)
    make_box("GasStation_CanopyUnder", (gs_x, gs_y, canopy_z - 0.22),
             (9.6, 7.6, 0.06), (0.95, 0.92, 0.85, 1.0))
    # Brand colour band along the canopy edge (red stripe)
    make_box("GasStation_Band_W", (gs_x - 5.05, gs_y, canopy_z),
             (0.10, 8.0, 0.30), (0.78, 0.20, 0.18, 1.0))
    make_box("GasStation_Band_S", (gs_x, gs_y - 4.05, canopy_z),
             (10.0, 0.10, 0.30), (0.78, 0.20, 0.18, 1.0))
    # 4 canopy support pillars
    for pi, (px_o, py_o) in enumerate([(-3.5, -3.0), (3.5, -3.0), (-3.5, 3.0), (3.5, 3.0)]):
        make_cyl(f"GasStation_Pillar_{pi}", (gs_x + px_o, gs_y + py_o, canopy_z / 2),
                 0.22, canopy_z, (0.85, 0.82, 0.74, 1.0), segments=6)
    # Fuel pump islands — 2 pumps under the canopy
    for pi, py_o in enumerate([-1.5, 1.5]):
        # concrete island
        make_box(f"GasStation_Island_{pi}", (gs_x, gs_y + py_o, 0.10),
                 (3.5, 1.2, 0.20), curb)
        # the pump unit
        make_box(f"GasStation_Pump_{pi}_body", (gs_x, gs_y + py_o, 0.80),
                 (1.1, 0.55, 1.10), (0.40, 0.42, 0.42, 1.0))
        make_box(f"GasStation_Pump_{pi}_screen", (gs_x, gs_y + py_o - 0.30, 1.10),
                 (0.70, 0.04, 0.30), (0.30, 0.85, 0.55, 1.0))   # green digit display
        make_cyl(f"GasStation_Pump_{pi}_hose", (gs_x + 0.40, gs_y + py_o, 1.20),
                 0.04, 0.50, (0.10, 0.10, 0.10, 1.0), segments=4)
    # Small attached convenience store building (north of the canopy)
    store_y = gs_y + 8.0
    make_box("GasStation_Store_Body", (gs_x, store_y, 2.1), (8.0, 6.0, 4.2), (0.85, 0.82, 0.74, 1.0))
    make_box("GasStation_Store_Roof", (gs_x, store_y, 4.3), (8.4, 6.4, 0.20), (0.32, 0.30, 0.26, 1.0))
    # store windows (lit warm yellow)
    make_box("GasStation_Store_Window_W", (gs_x - 4.05, store_y, 1.8),
             (0.05, 4.0, 1.8), (0.95, 0.78, 0.40, 1.0))
    make_box("GasStation_Store_Window_E", (gs_x + 4.05, store_y, 1.8),
             (0.05, 4.0, 1.8), (0.95, 0.78, 0.40, 1.0))
    # internal mullions
    for mi in range(3):
        my_o = -1.2 + mi * 1.2
        make_box(f"GasStation_Store_Mullion_W_{mi}", (gs_x - 4.06, store_y + my_o, 1.8),
                 (0.05, 0.06, 1.8), (0.30, 0.26, 0.20, 1.0))
        make_box(f"GasStation_Store_Mullion_E_{mi}", (gs_x + 4.06, store_y + my_o, 1.8),
                 (0.05, 0.06, 1.8), (0.30, 0.26, 0.20, 1.0))
    # Tall illuminated price sign on a pole at the road
    sign_pole_x = gs_x + 6.5
    sign_pole_y = gs_y - 2.0
    make_cyl("GasStation_Sign_Pole", (sign_pole_x, sign_pole_y, 5.5), 0.16, 11.0,
             (0.30, 0.28, 0.24, 1.0), segments=6)
    make_box("GasStation_Sign_Panel", (sign_pole_x, sign_pole_y, 8.5),
             (3.0, 0.12, 2.4), (0.78, 0.20, 0.18, 1.0))   # red brand panel
    make_box("GasStation_Sign_Price", (sign_pole_x, sign_pole_y + 0.10, 8.5),
             (2.4, 0.04, 1.6), (0.95, 0.92, 0.65, 1.0))   # yellow price strip

    # ════════════════════════════════════════════════════════════
    # STRIP MALL — north end of the frontage road
    # ════════════════════════════════════════════════════════════
    sm_x = NEAR_FRONTAGE_X
    sm_y = 30.0
    sm_w = 8.0
    sm_l = 36.0
    sm_h = 4.6
    make_box("StripMall_Body", (sm_x, sm_y, sm_h / 2), (sm_w, sm_l, sm_h),
             (0.78, 0.74, 0.66, 1.0))
    # Flat roof + parapet
    make_box("StripMall_Roof", (sm_x, sm_y, sm_h + 0.10), (sm_w + 0.4, sm_l + 0.4, 0.20),
             (0.32, 0.30, 0.26, 1.0))
    make_box("StripMall_Parapet_E", (sm_x + sm_w/2 + 0.05, sm_y, sm_h + 0.40),
             (0.10, sm_l + 0.4, 0.40), (0.65, 0.58, 0.48, 1.0))
    # Storefront awning running the full length (red stripe like the gas station band)
    awning_z = 2.8
    make_box("StripMall_Awning", (sm_x + sm_w/2 + 0.20, sm_y, awning_z),
             (0.30, sm_l - 1.0, 0.30), (0.78, 0.20, 0.18, 1.0))
    # 6 storefront windows running along the east face (toward the road/parking)
    for si in range(6):
        fy = -sm_l/2 + 3.0 + si * (sm_l - 6.0) / 5.0
        # lit interior visible through plate glass
        make_box(f"StripMall_Win_{si}", (sm_x + sm_w/2 + 0.02, fy, 1.8),
                 (0.04, 4.4, 2.8), (0.95, 0.85, 0.50, 1.0))
        # window mullion separators
        make_box(f"StripMall_Mullion_{si}_T", (sm_x + sm_w/2 + 0.04, fy, 3.2),
                 (0.05, 4.5, 0.08), (0.30, 0.26, 0.20, 1.0))
        make_box(f"StripMall_Mullion_{si}_B", (sm_x + sm_w/2 + 0.04, fy, 0.40),
                 (0.05, 4.5, 0.08), (0.30, 0.26, 0.20, 1.0))
        # vertical divider between shops
        if si < 5:
            div_y = -sm_l/2 + 3.0 + (si + 0.5) * (sm_l - 6.0) / 5.0
            make_box(f"StripMall_Divider_{si}", (sm_x + sm_w/2 + 0.04, div_y + 2.2, 1.8),
                     (0.06, 0.12, 2.8), (0.30, 0.26, 0.20, 1.0))
    # Storefront signs above each window — a colourful band
    sign_colors = [
        (0.85, 0.32, 0.20, 1.0), (0.20, 0.55, 0.80, 1.0),
        (0.62, 0.30, 0.78, 1.0), (0.85, 0.62, 0.22, 1.0),
        (0.30, 0.78, 0.55, 1.0), (0.78, 0.55, 0.30, 1.0),
    ]
    for si in range(6):
        fy = -sm_l/2 + 3.0 + si * (sm_l - 6.0) / 5.0
        make_box(f"StripMall_Sign_{si}", (sm_x + sm_w/2 + 0.10, fy, 3.75),
                 (0.05, 4.0, 0.60), sign_colors[si % len(sign_colors)])
    # Strip-mall parking lot in front
    make_box("StripMall_Lot", (sm_x + sm_w/2 + 4.0, sm_y, -0.02),
             (6.0, sm_l, 0.04), asphalt)
    for li in range(7):
        ly = -sm_l/2 + 3.0 + li * (sm_l - 6.0) / 6.0
        make_box(f"StripMall_LotLine_{li}", (sm_x + sm_w/2 + 4.0, ly, 0.005),
                 (4.5, 0.08, 0.005), (0.70, 0.62, 0.30, 1.0))
    # A few parked cars in the strip-mall lot — small / silhouette-only
    for ci, (cx_o, cy_o, col) in enumerate([
        (3.0, -10.0, (0.40, 0.20, 0.18, 1.0)),
        (3.0,  -2.0, (0.30, 0.35, 0.50, 1.0)),
        (3.0,   8.0, (0.55, 0.50, 0.45, 1.0)),
        (5.5,  14.0, (0.35, 0.35, 0.38, 1.0)),
    ]):
        cx_p = sm_x + sm_w/2 + cx_o
        cy_p = sm_y + cy_o
        make_box(f"StripMall_Car_{ci}_body", (cx_p, cy_p, 0.45), (1.7, 4.0, 0.55), col)
        make_box(f"StripMall_Car_{ci}_cabin", (cx_p, cy_p, 1.00), (1.5, 2.4, 0.50), col)

    # ════════════════════════════════════════════════════════════
    # DEEP DISTANCE — second tier of bayou trees + industrial
    # silhouettes further west to give the view depth
    # ════════════════════════════════════════════════════════════
    # Mixed tree line
    deep_tree_positions = [
        -105, -92, -78, -62, -48, -32, -18, -4, 10, 22, 36, 50, 64, 78, 92, 106,
    ]
    for ti, ty in enumerate(deep_tree_positions):
        kind = ti % 3
        zig = ((ti * 7) % 5 - 2) * 0.6
        tx = NEAR_DEEP_X - 2.0 + zig
        canopy_col = (0.22, 0.30, 0.18, 1.0) if kind == 0 else (
                     (0.28, 0.34, 0.22, 1.0) if kind == 1 else (0.34, 0.30, 0.20, 1.0))
        trunk_h = 6.5 if kind == 1 else 5.5
        make_cyl(f"NearDeep_Trunk_{ti}", (tx, ty, trunk_h / 2),
                 0.18, trunk_h, COL_TREE_TRUNK, segments=6)
        # Sphere canopy
        for ci, (ox, oz_off, r_mul) in enumerate([(0.0, 0.0, 1.0), (-0.4, 0.7, 0.7), (0.3, 1.2, 0.6)]):
            make_sphere(f"NearDeep_Canopy_{ti}_{ci}",
                        (tx + ox, ty, trunk_h + oz_off),
                        1.1 * r_mul, canopy_col)

    # Industrial silhouettes between the tree line and the distant highway
    for ii, (iy, iw, il, ih, has_stack) in enumerate([
        (-70.0, 8.0, 12.0, 11.0, True),
        (-42.0, 6.0,  9.0,  7.0, False),
        ( -8.0, 10.0, 14.0, 16.0, True),    # a tall refinery
        ( 30.0, 7.0, 10.0,  9.0, False),
        ( 60.0, 9.0, 12.0, 13.0, True),
        ( 88.0, 6.0,  8.0,  6.5, False),
    ]):
        ix = NEAR_DEEP_X - 10.0
        make_box(f"NearDeep_Bldg_{ii}", (ix, iy, ih / 2), (iw, il, ih),
                 (0.30, 0.28, 0.26, 1.0))
        if has_stack:
            make_cyl(f"NearDeep_Stack_{ii}", (ix - 1.0, iy - 1.0, ih + 4.0),
                     0.40, 8.0, (0.20, 0.18, 0.16, 1.0), segments=8)
            # smoke plume
            for pi in range(4):
                make_sphere(f"NearDeep_Smoke_{ii}_{pi}",
                            (ix - 1.0 + pi * 1.0, iy - 1.0 - pi * 0.3, ih + 8.5 + pi * 0.7),
                            1.3 + pi * 0.25, (0.55, 0.52, 0.48, 1.0))
        # parapet roof cap
        make_box(f"NearDeep_BldgCap_{ii}", (ix, iy, ih + 0.15),
                 (iw + 0.2, il + 0.2, 0.25), (0.36, 0.32, 0.28, 1.0))
        # row of small lit windows on the river-facing (+X) wall
        rows = max(2, int(ih / 3.0))
        cols = max(2, int(il / 3.0))
        for ri in range(rows):
            for cj in range(cols):
                wy = iy - il/2 + (cj + 0.5) * (il / cols)
                wz = 1.0 + (ri + 0.5) * ((ih - 1.0) / rows)
                seed = (ii * 31 + ri * 11 + cj * 7) & 0xFF
                col = (0.95, 0.78, 0.42, 1.0) if (seed % 100) < 28 else (0.18, 0.16, 0.14, 1.0)
                make_box(f"NearDeep_Win_{ii}_{ri}_{cj}", (ix + iw/2 + 0.03, wy, wz),
                         (0.04, il / cols * 0.5, (ih - 1.0) / rows * 0.5), col)

    # Tall water tower (silhouette landmark, far back)
    wt_x = NEAR_DEEP_X - 22.0
    wt_y = 10.0
    for li, (lx_off, ly_off) in enumerate([(-1.5, -1.5), (1.5, -1.5), (-1.5, 1.5), (1.5, 1.5)]):
        make_cyl(f"NearDeep_WaterTower_Leg_{li}", (wt_x + lx_off, wt_y + ly_off, 8.0),
                 0.14, 16.0, (0.30, 0.26, 0.22, 1.0), segments=4)
    make_cyl("NearDeep_WaterTower_Tank", (wt_x, wt_y, 17.5), 2.4, 4.0,
             (0.52, 0.48, 0.42, 1.0), segments=10)
    make_prism("NearDeep_WaterTower_Roof", (wt_x, wt_y, 19.5),
               (5.2, 5.2, 1.4), (0.32, 0.30, 0.26, 1.0), pitch_axis='X')

    # ════════════════════════════════════════════════════════════
    # FAR-DISTANCE HIGHWAY OVERPASS running N-S behind the strip mall
    # ════════════════════════════════════════════════════════════
    hwy_x = NEAR_HIGHWAY_X
    hwy_z = 9.0
    hwy_w = 5.0
    hwy_length = 200.0
    # The deck — a continuous box along Y
    make_box("Hwy_Deck", (hwy_x, 0, hwy_z), (hwy_w, hwy_length, 0.60),
             (0.40, 0.38, 0.34, 1.0))
    # Concrete piers every 20m
    for pi in range(11):
        py = -100 + pi * 20.0
        make_box(f"Hwy_Pier_{pi}", (hwy_x, py, hwy_z / 2),
                 (1.6, 1.4, hwy_z), (0.55, 0.52, 0.46, 1.0))
        # foot
        make_box(f"Hwy_Pier_{pi}_foot", (hwy_x, py, 0.25),
                 (2.4, 2.2, 0.50), (0.50, 0.47, 0.42, 1.0))
    # Guard-rail along both edges of the deck (low silhouette boxes)
    make_box("Hwy_Rail_W", (hwy_x - hwy_w/2 - 0.10, 0, hwy_z + 0.55),
             (0.10, hwy_length, 0.40), (0.46, 0.42, 0.38, 1.0))
    make_box("Hwy_Rail_E", (hwy_x + hwy_w/2 + 0.10, 0, hwy_z + 0.55),
             (0.10, hwy_length, 0.40), (0.46, 0.42, 0.38, 1.0))
    # Sparse vehicles on the highway (small silhouettes)
    for vi, vy in enumerate([-72, -28, 6, 38, 78]):
        col = (0.55, 0.20, 0.18, 1.0) if vi % 2 == 0 else (0.30, 0.32, 0.36, 1.0)
        make_box(f"Hwy_Veh_{vi}", (hwy_x, vy, hwy_z + 0.95), (2.6, 5.0, 0.7), col)
    # Highway sign overhead — gantry-style, faces port
    sign_y = -10.0
    make_cyl("Hwy_Gantry_W", (hwy_x - hwy_w/2 - 0.40, sign_y, hwy_z + 3.0),
             0.18, 5.0, (0.46, 0.42, 0.38, 1.0), segments=6)
    make_cyl("Hwy_Gantry_E", (hwy_x + hwy_w/2 + 0.40, sign_y, hwy_z + 3.0),
             0.18, 5.0, (0.46, 0.42, 0.38, 1.0), segments=6)
    make_box("Hwy_Gantry_Top", (hwy_x, sign_y, hwy_z + 5.5),
             (hwy_w + 1.0, 0.30, 0.20), (0.46, 0.42, 0.38, 1.0))
    make_box("Hwy_Sign", (hwy_x, sign_y - 0.25, hwy_z + 4.6),
             (4.5, 0.10, 1.6), (0.18, 0.36, 0.28, 1.0))   # green interstate-style sign


def build_far_horizons():
    """Fill the deep distance to the NORTH (upriver, beyond the boat's
    bow) and SOUTH (downriver, beyond the bridge) so a 360° pan from
    the parking lot always lands on something. Without this the
    cinematic shots have visible cardboard-cutout horizons.

    NORTH: a small river town at far +Y — church spire, water tower,
    cluster of small houses, distant tree-line behind.
    SOUTH: a port-industrial complex beyond the bridge — container
    cranes, refinery silhouettes, tall smokestacks, ship cranes."""

    # ════════════════════════════════════════════════════════════
    # NORTH HORIZON — small river town
    # ════════════════════════════════════════════════════════════
    NORTH_Y = 150.0
    town_z = RIVER_LEVEL_Z + 0.30

    # ground strip the town sits on (port-side + main-channel side)
    make_box("North_TownGround", (10.0, NORTH_Y, town_z - 0.20),
             (140.0, 30.0, 0.40), COL_SHORELINE)

    # ── Church spire — focal landmark
    spire_x, spire_y = -30.0, NORTH_Y - 4.0
    # Main body
    make_box("North_Church_Body", (spire_x, spire_y, town_z + 4.0),
             (5.0, 6.0, 8.0), (0.78, 0.74, 0.66, 1.0))
    # Sloped roof
    make_prism("North_Church_Roof", (spire_x, spire_y, town_z + 8.0),
               (5.4, 6.4, 2.2), (0.48, 0.20, 0.16, 1.0), pitch_axis='X')
    # Bell tower base
    make_box("North_Church_Tower", (spire_x - 1.5, spire_y - 1.5, town_z + 7.0),
             (2.6, 2.6, 14.0), (0.78, 0.74, 0.66, 1.0))
    # Tower roof — short prism
    make_prism("North_Church_TowerRoof", (spire_x - 1.5, spire_y - 1.5, town_z + 14.0),
               (3.0, 3.0, 2.0), (0.48, 0.20, 0.16, 1.0), pitch_axis='X')
    # Spire — tall thin prism on top of the bell tower
    for si, (sz_off, sr) in enumerate([(0.0, 1.4), (2.0, 1.0), (4.0, 0.6)]):
        make_cyl(f"North_Spire_{si}", (spire_x - 1.5, spire_y - 1.5, town_z + 16.0 + sz_off),
                 sr, 2.0, (0.48, 0.20, 0.16, 1.0), segments=6)
    # Cross at the very top
    make_box("North_Spire_Cross_V", (spire_x - 1.5, spire_y - 1.5, town_z + 22.5),
             (0.10, 0.10, 0.70), COL_BRASS)
    make_box("North_Spire_Cross_H", (spire_x - 1.5, spire_y - 1.5, town_z + 22.3),
             (0.40, 0.10, 0.10), COL_BRASS)

    # ── Water tower — second landmark
    wt_x = 20.0
    wt_y = NORTH_Y + 6.0
    for li, (lx_off, ly_off) in enumerate([(-1.5, -1.5), (1.5, -1.5), (-1.5, 1.5), (1.5, 1.5)]):
        make_cyl(f"North_WT_Leg_{li}", (wt_x + lx_off, wt_y + ly_off, 8.0),
                 0.14, 16.0, (0.30, 0.28, 0.24, 1.0), segments=6)
    make_cyl("North_WT_Tank", (wt_x, wt_y, 17.5), 2.2, 4.0, (0.55, 0.52, 0.46, 1.0), segments=10)
    make_prism("North_WT_Roof", (wt_x, wt_y, 19.5), (5.0, 5.0, 1.4),
               (0.32, 0.30, 0.26, 1.0), pitch_axis='X')

    # ── Cluster of small houses scattered along the town strip
    house_specs = [
        # (x, y_off, w, l, h, roof_color, body_color)
        (-50.0, 1.5, 4.0, 5.0, 3.2, (0.36, 0.22, 0.18, 1.0), (0.78, 0.72, 0.62, 1.0)),
        (-42.0, -2.0, 4.5, 5.5, 3.4, (0.42, 0.32, 0.22, 1.0), (0.62, 0.55, 0.45, 1.0)),
        (-15.0, 1.0, 5.0, 6.0, 3.6, (0.30, 0.28, 0.22, 1.0), (0.85, 0.80, 0.70, 1.0)),
        ( -5.0, -1.5, 4.0, 5.0, 3.2, (0.40, 0.22, 0.20, 1.0), (0.72, 0.66, 0.56, 1.0)),
        ( 35.0, 2.0, 4.5, 5.5, 3.4, (0.36, 0.32, 0.24, 1.0), (0.78, 0.72, 0.62, 1.0)),
        ( 48.0, -1.0, 4.0, 5.0, 3.2, (0.42, 0.22, 0.18, 1.0), (0.68, 0.62, 0.52, 1.0)),
        ( 60.0, 1.5, 5.0, 6.0, 3.6, (0.30, 0.30, 0.26, 1.0), (0.85, 0.80, 0.72, 1.0)),
    ]
    for hi, (hx, hy_o, hw, hl, hh, roof_c, body_c) in enumerate(house_specs):
        hy = NORTH_Y + hy_o
        make_box(f"North_House_{hi}_Body", (hx, hy, town_z + hh / 2),
                 (hw, hl, hh), body_c)
        make_prism(f"North_House_{hi}_Roof", (hx, hy, town_z + hh),
                   (hw + 0.4, hl + 0.4, 2.0), roof_c, pitch_axis='Y')
        # A lit window on the side facing the river
        seed = (hi * 13) & 0xFF
        if seed % 100 < 60:
            make_box(f"North_House_{hi}_Window", (hx, hy - hl/2 - 0.04, town_z + hh * 0.55),
                     (hw * 0.4, 0.04, hh * 0.35), (0.95, 0.80, 0.42, 1.0))
        # Chimney
        if hi % 2 == 0:
            make_box(f"North_House_{hi}_Chimney", (hx + hw * 0.25, hy + hl * 0.10, town_z + hh + 1.5),
                     (0.40, 0.40, 1.6), (0.42, 0.30, 0.24, 1.0))

    # ── Tree line behind the town
    for ti in range(20):
        tx = -55.0 + ti * 6.0
        ty = NORTH_Y + 10.0 + ((ti * 7) % 5 - 2) * 0.6
        trunk_h = 5.5 + ((ti * 11) % 4) * 0.7
        make_cyl(f"North_Tree_{ti}_Trunk", (tx, ty, town_z + trunk_h / 2),
                 0.20, trunk_h, COL_TREE_TRUNK, segments=6)
        canopy_col = (0.22, 0.32, 0.18, 1.0) if ti % 2 == 0 else (0.30, 0.36, 0.22, 1.0)
        make_sphere(f"North_Tree_{ti}_Canopy", (tx, ty, town_z + trunk_h + 0.6),
                    1.30, canopy_col)
        if ti % 3 == 1:
            make_sphere(f"North_Tree_{ti}_Canopy2", (tx - 0.5, ty + 0.4, town_z + trunk_h + 1.3),
                        0.95, canopy_col)

    # ════════════════════════════════════════════════════════════
    # SOUTH HORIZON — port-industrial complex past the bridge
    # ════════════════════════════════════════════════════════════
    SOUTH_Y = -150.0
    port_z = RIVER_LEVEL_Z + 0.30

    # ground strip for the port
    make_box("South_PortGround", (10.0, SOUTH_Y, port_z - 0.20),
             (160.0, 28.0, 0.40), (0.24, 0.24, 0.24, 1.0))

    # ── Container yard with stacked containers ──
    container_colors = [
        (0.55, 0.20, 0.16, 1.0), (0.30, 0.40, 0.50, 1.0),
        (0.40, 0.42, 0.32, 1.0), (0.62, 0.50, 0.28, 1.0),
        (0.20, 0.30, 0.40, 1.0), (0.50, 0.30, 0.20, 1.0),
    ]
    for ci in range(24):
        cx = -65.0 + (ci % 8) * 3.5
        cy = SOUTH_Y - 2.0 + (ci // 8) * 4.2
        cz_off = ((ci * 7) % 3) * 1.5         # varied stack heights
        col = container_colors[ci % len(container_colors)]
        make_box(f"South_Container_{ci}", (cx, cy, port_z + 0.7 + cz_off),
                 (1.6, 3.2, 1.4), col)

    # ── Container cranes — large gantry shapes
    for cni, cn_x in enumerate([-25.0, 5.0, 35.0]):
        cn_y = SOUTH_Y + 4.0
        # gantry legs
        for li, (lx_o, ly_o) in enumerate([(-4.0, -3.0), (4.0, -3.0), (-4.0, 3.0), (4.0, 3.0)]):
            make_box(f"South_Crane_{cni}_Leg_{li}",
                     (cn_x + lx_o, cn_y + ly_o, port_z + 6.0),
                     (0.5, 0.5, 12.0), (0.46, 0.42, 0.38, 1.0))
        # cross-girder at the top
        make_box(f"South_Crane_{cni}_GirderS", (cn_x, cn_y - 3.0, port_z + 12.5),
                 (9.0, 0.6, 0.6), (0.46, 0.42, 0.38, 1.0))
        make_box(f"South_Crane_{cni}_GirderN", (cn_x, cn_y + 3.0, port_z + 12.5),
                 (9.0, 0.6, 0.6), (0.46, 0.42, 0.38, 1.0))
        # boom — long horizontal arm reaching out toward the river
        make_box(f"South_Crane_{cni}_Boom", (cn_x, cn_y, port_z + 13.5),
                 (0.6, 18.0, 0.8), (0.46, 0.42, 0.38, 1.0))
        # operator cab partway up
        make_box(f"South_Crane_{cni}_Cab", (cn_x, cn_y, port_z + 11.0),
                 (1.2, 1.4, 1.4), (0.78, 0.20, 0.18, 1.0))
        # warning light on top
        make_cyl(f"South_Crane_{cni}_Warn", (cn_x, cn_y, port_z + 13.0),
                 0.20, 0.30, (1.0, 0.45, 0.20, 1.0), segments=6)

    # ── Refinery cluster — tall stacks + tanks
    # Storage tanks (large cylinders)
    for ti, (tx_o, ty_o, tr) in enumerate([
        (45.0, -1.0, 3.2), (54.0, 2.0, 2.8), (62.0, -2.0, 3.5),
        (70.0, 1.0, 2.4),
    ]):
        make_cyl(f"South_Tank_{ti}", (tx_o, SOUTH_Y + ty_o, port_z + 3.0),
                 tr, 6.0, (0.50, 0.46, 0.40, 1.0), segments=10)
        # band ring
        make_cyl(f"South_Tank_{ti}_Band", (tx_o, SOUTH_Y + ty_o, port_z + 5.5),
                 tr + 0.05, 0.15, (0.32, 0.30, 0.26, 1.0), segments=10)
    # Refinery stacks — very tall narrow cylinders
    for si, (sx_o, sy_o, sh) in enumerate([
        (80.0, 0.0, 18.0), (84.0, 3.0, 15.0), (88.0, -1.0, 22.0),
    ]):
        make_cyl(f"South_RefStack_{si}", (sx_o, SOUTH_Y + sy_o, port_z + sh / 2),
                 0.50, sh, (0.22, 0.20, 0.18, 1.0), segments=8)
        make_cyl(f"South_RefStack_{si}_Cap", (sx_o, SOUTH_Y + sy_o, port_z + sh - 0.10),
                 0.65, 0.20, COL_BRASS, segments=8)
        # smoke plume
        for pi in range(4):
            make_sphere(f"South_RefSmoke_{si}_{pi}",
                        (sx_o + pi * 1.2, SOUTH_Y + sy_o - pi * 0.4, port_z + sh + 1.5 + pi * 0.7),
                        1.2 + pi * 0.25, (0.42, 0.40, 0.38, 1.0))
    # Flare stack — orange tip suggesting active gas flare
    make_cyl("South_Flare", (74.0, SOUTH_Y + 2.0, port_z + 7.0),
             0.35, 14.0, (0.22, 0.20, 0.18, 1.0), segments=6)
    make_sphere("South_FlareFlame", (74.0, SOUTH_Y + 2.0, port_z + 14.5),
                0.80, (1.0, 0.62, 0.20, 1.0))

    # ── A second tier of warehouses lining the port front
    for wi, (wx, ww, wl, wh) in enumerate([
        (-50.0, 8.0, 6.0, 5.5), (-32.0, 7.0, 6.0, 4.8),
        ( -8.0, 9.0, 7.0, 7.0), ( 12.0, 6.0, 5.5, 5.0),
        ( 28.0, 8.0, 6.0, 6.0),
    ]):
        make_box(f"South_Warehouse_{wi}", (wx, SOUTH_Y - 10.0, port_z + wh / 2),
                 (ww, wl, wh), (0.36, 0.34, 0.30, 1.0))
        make_box(f"South_Warehouse_{wi}_Cap", (wx, SOUTH_Y - 10.0, port_z + wh + 0.15),
                 (ww + 0.2, wl + 0.2, 0.20), (0.46, 0.42, 0.38, 1.0))


def build_distant_atmosphere():
    """Big-scale far-distance landmarks visible behind everything else.
    A distant bridge upriver, far hills on the horizon, a few low cloud
    shelves."""

    # ── Far hills on the horizon behind the opposite (starboard) shore ──
    for hi, (hx, hy, hw, hl, hh) in enumerate([
        (OPPOSITE_X + 22, -45, 18, 32, 8),
        (OPPOSITE_X + 28, -10, 25, 35, 12),
        (OPPOSITE_X + 24,  20, 20, 30, 10),
        (OPPOSITE_X + 30,  45, 22, 28, 14),
    ]):
        make_box(f"FarHill_{hi}", (hx, hy, RIVER_LEVEL_Z + hh / 2),
                 (hw, hl, hh), (0.32, 0.36, 0.36, 1.0))

    # ── Distant bridge downriver (truss bridge crossing river to south) ──
    br_y = BRIDGE_Y
    br_x_span = abs(OPPOSITE_X) + 4.0
    br_cx = OPPOSITE_X / 2.0
    br_z = RIVER_LEVEL_Z + 10.0
    # bridge deck
    make_box("Bridge_Deck", (br_cx, br_y, br_z), (br_x_span, 2.0, 0.6), (0.38, 0.34, 0.30, 1.0))
    # truss panels along both sides
    for side, sy_o in (("S", -1.10), ("N", 1.10)):
        make_box(f"Bridge_TopChord_{side}", (br_cx, br_y + sy_o, br_z + 3.5),
                 (br_x_span, 0.20, 0.30), (0.38, 0.34, 0.30, 1.0))
        # vertical members
        for vi in range(12):
            vx_o = -br_x_span/2 + 1.0 + vi * (br_x_span - 2.0) / 11.0
            make_box(f"Bridge_Vert_{side}_{vi}", (br_cx + vx_o, br_y + sy_o, br_z + 1.8),
                     (0.18, 0.18, 3.6), (0.38, 0.34, 0.30, 1.0))
        # diagonal X-brace suggestion (just two crossing horizontals)
        make_box(f"Bridge_Diag_{side}_a", (br_cx, br_y + sy_o, br_z + 2.2),
                 (br_x_span, 0.16, 0.16), (0.38, 0.34, 0.30, 1.0))
        make_box(f"Bridge_Diag_{side}_b", (br_cx, br_y + sy_o, br_z + 1.4),
                 (br_x_span, 0.16, 0.16), (0.38, 0.34, 0.30, 1.0))
    # bridge piers going down into the water (3 piers across)
    for pi in range(3):
        px_p = br_cx + (-1 + pi) * br_x_span * 0.35
        make_box(f"Bridge_Pier_{pi}", (px_p, br_y, RIVER_LEVEL_Z + 5.0),
                 (1.4, 2.6, 10.0), (0.42, 0.40, 0.36, 1.0))
        # pier footing
        make_box(f"Bridge_Pier_{pi}_foot", (px_p, br_y, RIVER_LEVEL_Z + 0.20),
                 (2.0, 3.4, 0.40), (0.42, 0.40, 0.36, 1.0))

    # ── Cloud shelves — clusters of overlapping spheres (NOT boxes).
    # Each cloud is 6-8 lowpoly spheres of varying radius offset around
    # a center point, with the bottom ones flatter/wider to suggest the
    # underside of a cumulus shelf.
    cloud_centers = [
        (-10, -40, 24), (14, -10, 28), (-22, 20, 22),
        (  8,  50, 26), (30, -28, 30), (-35, -5, 25),
        ( 50, 30, 27),
    ]
    cloud_colors = [
        (0.78, 0.74, 0.68, 1.0),
        (0.74, 0.70, 0.64, 1.0),
        (0.70, 0.66, 0.60, 1.0),
        (0.72, 0.69, 0.65, 1.0),
    ]
    for ci_c, (cx, cy, cz_c) in enumerate(cloud_centers):
        # mass body — three biggest puffs forming the bulk
        make_sphere(f"Cloud_{ci_c}_a", (cx, cy, cz_c),         3.8, cloud_colors[0])
        make_sphere(f"Cloud_{ci_c}_b", (cx + 3.5, cy - 0.5, cz_c + 0.6), 3.2, cloud_colors[1])
        make_sphere(f"Cloud_{ci_c}_c", (cx - 3.0, cy + 0.8, cz_c + 0.3), 3.0, cloud_colors[2])
        # smaller offset puffs for organic silhouette
        make_sphere(f"Cloud_{ci_c}_d", (cx + 6.0, cy + 1.5, cz_c + 0.4), 2.2, cloud_colors[1])
        make_sphere(f"Cloud_{ci_c}_e", (cx - 5.5, cy - 1.0, cz_c - 0.2), 2.4, cloud_colors[3])
        make_sphere(f"Cloud_{ci_c}_f", (cx + 1.5, cy + 3.0, cz_c + 1.5), 2.0, cloud_colors[0])
        make_sphere(f"Cloud_{ci_c}_g", (cx - 1.5, cy - 3.5, cz_c + 1.2), 1.8, cloud_colors[2])
        make_sphere(f"Cloud_{ci_c}_h", (cx + 4.5, cy + 3.5, cz_c + 1.6), 1.6, cloud_colors[1])

    # ── A sandy beach strip on the boat's stern (downriver of paddle wheel) ──
    sand_col = (0.62, 0.55, 0.40, 1.0)
    sand_y = -BOAT_L / 2 - 8.0
    make_box("Sand_Strip", (0, sand_y, -0.45), (16.0, 1.8, 0.10), sand_col)
    for ri_s in range(5):
        rx_s = -6.0 + ri_s * 3.0
        make_box(f"Sand_Rock_{ri_s}", (rx_s, sand_y + ((ri_s % 2) * 0.4 - 0.2), -0.35),
                 (0.4, 0.4, 0.2), (0.42, 0.38, 0.32, 1.0))


def main():
    clear_scene()
    # Ground first so all other geometry sits ON it, not floating in
    # Godot-void. Roads next so subsequent feature builds (parking lot,
    # dock, gas station, etc.) sit ON the road surface where they
    # overlap.
    build_ground()
    build_road_network()
    build_riverboat()
    build_parking_lot()
    build_dock()
    build_river()
    build_near_shore()
    build_opposite_shore()
    build_other_boats()
    build_bayou()
    build_far_horizons()
    build_distant_atmosphere()
    export_glb()


if __name__ == "__main__":
    main()
