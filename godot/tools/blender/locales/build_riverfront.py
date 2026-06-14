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
from mathutils import Vector

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

PARKING_Y = -BOAT_L / 2 - 12.0   # parking lot 12m south of the boat
RIVER_LEVEL_Z = -0.3              # water plane sits 0.3m below origin

# Opposite shore (west)
OPPOSITE_X = -45.0   # far western shore
# Bayou (east)
BAYOU_X = 28.0

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
    """The boat's exterior shell. PS2-era polycount: hull is a stepped
    bevel, smokestack is a chunky 8-sided cylinder, paddle wheel has a
    proper hub + spokes + blades, the pilothouse roof is a sloped
    prism, windows have mullions."""

    # ── HULL — stepped tapering bevel, three tiers ──────────────
    # tier 0: widest at waterline
    h0_z = RIVER_LEVEL_Z + 0.35
    make_box("Boat_Hull_Lower", (0, 0, h0_z), (BOAT_W + 0.40, BOAT_L + 0.30, 0.70), COL_HULL)
    # tier 1: mid hull (slightly narrower fore/aft, fakes the bow taper)
    h1_z = RIVER_LEVEL_Z + 0.95
    make_box("Boat_Hull_Mid",   (0, 0, h1_z), (BOAT_W,        BOAT_L,        0.50), COL_HULL)
    # tier 2: upper hull (the gunwale strip, narrower again)
    h2_z = RIVER_LEVEL_Z + 1.45
    make_box("Boat_Hull_Upper", (0, 0, h2_z), (BOAT_W - 0.40, BOAT_L - 0.30, 0.50), COL_HULL)

    # Bow chamfers — short angled boxes at +Y end to fake a pointed prow
    bow_y = BOAT_L / 2
    make_box("Boat_Bow_Chamfer_W", (-BOAT_W/2 + 1.2, bow_y + 0.4, h1_z), (1.6, 1.0, 0.80), COL_HULL)
    make_box("Boat_Bow_Chamfer_E", ( BOAT_W/2 - 1.2, bow_y + 0.4, h1_z), (1.6, 1.0, 0.80), COL_HULL)
    make_box("Boat_Bow_Tip",       (0, bow_y + 1.0, h1_z),                (3.0, 0.8, 0.80), COL_HULL)

    # Red trim band along the hull (signature riverboat motif)
    band_z = RIVER_LEVEL_Z + 1.30
    make_box("Boat_Trim_W", (-BOAT_W/2 - 0.03, 0, band_z), (0.06, BOAT_L * 0.98, 0.18), COL_HULL_BAND)
    make_box("Boat_Trim_E", (BOAT_W/2 + 0.03, 0, band_z),  (0.06, BOAT_L * 0.98, 0.18), COL_HULL_BAND)
    make_box("Boat_Trim_S", (0, -BOAT_L/2 - 0.03, band_z), (BOAT_W * 0.98, 0.06, 0.18), COL_HULL_BAND)
    make_box("Boat_Trim_N", (0, BOAT_L/2 + 0.03, band_z),  (BOAT_W * 0.98, 0.06, 0.18), COL_HULL_BAND)

    # ── MAIN DECK ─────────────────────────────────────────────
    deck_z = RIVER_LEVEL_Z + BOAT_HULL_H + DECK_H / 2
    make_box("Boat_MainDeck", (0, 0, deck_z), (BOAT_W + 0.4, BOAT_L + 0.4, DECK_H), COL_DECK_WOOD)
    # Deck plank lines — thin stripes across the deck top so the surface reads
    deck_top_z = deck_z + DECK_H / 2 + 0.005
    for i in range(8):
        y = -BOAT_L/2 + 1.5 + i * (BOAT_L - 3.0) / 7.0
        make_box(f"Boat_DeckPlank_{i}", (0, y, deck_top_z),
                 (BOAT_W + 0.3, 0.05, 0.01), (0.32, 0.22, 0.14, 1.0))

    # ── PORCH RAILINGS (brass) ────────────────────────────────
    rail_z = deck_z + 0.50
    for side in ("W", "E"):
        x = -BOAT_W/2 - 0.2 if side == "W" else BOAT_W/2 + 0.2
        make_box(f"Boat_Rail_{side}", (x, 0, rail_z), (0.05, BOAT_L, 0.05), COL_BRASS)
    for side in ("S", "N"):
        y = -BOAT_L/2 - 0.2 if side == "S" else BOAT_L/2 + 0.2
        make_box(f"Boat_Rail_{side}", (0, y, rail_z), (BOAT_W, 0.05, 0.05), COL_BRASS)
    # Vertical posts every 1.5m, with a mid-rail for visual density
    for i in range(int(BOAT_L / 1.5)):
        y = -BOAT_L/2 + 0.75 + i * 1.5
        make_box(f"Boat_Post_W_{i}", (-BOAT_W/2 - 0.2, y, deck_z + 0.25), (0.04, 0.04, 0.50), COL_BRASS)
        make_box(f"Boat_Post_E_{i}", (BOAT_W/2 + 0.2, y, deck_z + 0.25),  (0.04, 0.04, 0.50), COL_BRASS)
    # Mid-rail
    for side in ("W", "E"):
        x = -BOAT_W/2 - 0.2 if side == "W" else BOAT_W/2 + 0.2
        make_box(f"Boat_MidRail_{side}", (x, 0, deck_z + 0.25), (0.03, BOAT_L, 0.03), COL_BRASS)

    # ── PADDLE WHEEL HOUSING (curved-feeling shell faked as a chunky red box) ──
    pw_y = BOAT_L / 2 + 2.0
    pw_z = RIVER_LEVEL_Z + 1.6
    pw_radius = 1.4
    # housing as 3 stacked panels approximating an arc (fakes curvature)
    make_box("Boat_PaddleHousing_lower", (0, pw_y, pw_z - 0.9),  (BOAT_W * 0.7,  0.40, 0.40), COL_PADDLE_HOUSING)
    make_box("Boat_PaddleHousing_mid",   (0, pw_y, pw_z + 0.05), (BOAT_W * 0.78, 0.40, 1.60), COL_PADDLE_HOUSING)
    make_box("Boat_PaddleHousing_upper", (0, pw_y, pw_z + 1.05), (BOAT_W * 0.72, 0.40, 0.40), COL_PADDLE_HOUSING)
    # Housing back wall (between housing and the boat stern)
    make_box("Boat_PaddleHousing_back", (0, pw_y - 0.45, pw_z), (BOAT_W * 0.78, 0.10, 2.60), COL_PADDLE_HOUSING)

    # ── ACTUAL PADDLE WHEEL ─────────────────────────────────
    # hub axle running across the housing
    make_cyl("PaddleWheel_Axle", (0, pw_y, pw_z), 0.18, BOAT_W * 0.55,
             COL_BRASS, segments=8, axis='X')
    # outer rim (8-segment ring made of short box chord pieces)
    n_blades = 8
    blade_len = BOAT_W * 0.50
    for i in range(n_blades):
        angle = math.radians(i * (360.0 / n_blades))
        bx = math.cos(angle) * pw_radius
        bz = math.sin(angle) * pw_radius + pw_z
        # spoke from hub to rim
        spoke_cx = bx / 2.0
        spoke_cz = (bz + pw_z) / 2.0
        spoke_len = pw_radius
        spoke_ang = angle
        # use a long thin box rotated approximately along the spoke
        # (kept axis-aligned for simplicity — wobble hides the join)
        if abs(math.cos(angle)) > abs(math.sin(angle)):
            make_box(f"PaddleSpoke_{i}",
                     (spoke_cx, pw_y, pw_z + math.sin(angle) * pw_radius / 2.0),
                     (abs(math.cos(angle)) * pw_radius + 0.04, 0.10, 0.06),
                     COL_PADDLE_BLADES)
        else:
            make_box(f"PaddleSpoke_{i}",
                     (math.cos(angle) * pw_radius / 2.0, pw_y, pw_z + math.sin(angle) * pw_radius / 2.0),
                     (0.06, 0.10, abs(math.sin(angle)) * pw_radius + 0.04),
                     COL_PADDLE_BLADES)
        # the blade at the rim — flat plank running along the axle
        make_box(f"PaddleBlade_{i}", (bx, pw_y, bz),
                 (0.06, blade_len, 0.40), COL_PADDLE_BLADES)

    # ── SMOKESTACK — 8-segment cylinder ──────────────────────
    stack_y = BOAT_L / 2 - 4.0
    stack_base_z = deck_z + DECK_H / 2
    stack_h = 5.0
    stack_z = stack_base_z + stack_h / 2.0
    make_cyl("Boat_Smokestack", (0, stack_y, stack_z), 0.40, stack_h,
             COL_SMOKESTACK, segments=8)
    # brass cap ring at the top — a flat short cylinder
    make_cyl("Boat_Stack_Cap", (0, stack_y, stack_base_z + stack_h - 0.05),
             0.50, 0.18, COL_BRASS, segments=8)
    # base flange where it meets the deck
    make_cyl("Boat_Stack_Base", (0, stack_y, stack_base_z + 0.10),
             0.50, 0.20, COL_BRASS, segments=8)

    # ── HELM CABIN (the pilothouse) ──────────────────────────
    helm_y = BOAT_L / 4
    helm_z = deck_z + DECK_H / 2 + HELM_H / 2
    make_box("Boat_Helm_Walls", (0, helm_y, helm_z), (HELM_W, HELM_L, HELM_H), COL_HELM_WALL)
    # Big leaded window on the south side (looking down at the dining room)
    # — window pane itself, then a cross mullion to mark "leaded"
    win_z = helm_z + 0.4
    make_box("Boat_Helm_Window", (0, helm_y - HELM_L/2 - 0.01, win_z), (1.8, 0.05, 1.0), COL_HELM_WINDOW)
    # vertical mullion
    make_box("Boat_Helm_Win_VMullion", (0, helm_y - HELM_L/2 - 0.02, win_z), (0.04, 0.04, 1.0), COL_HELM_ROOF)
    # horizontal mullion
    make_box("Boat_Helm_Win_HMullion", (0, helm_y - HELM_L/2 - 0.02, win_z), (1.8, 0.04, 0.04), COL_HELM_ROOF)
    # Side windows (smaller, on east/west walls)
    for side, sx in (("W", -HELM_W/2), ("E", HELM_W/2)):
        make_box(f"Boat_Helm_SideWin_{side}", (sx + (0.03 if side == "E" else -0.03), helm_y, win_z),
                 (0.05, 1.2, 0.7), COL_HELM_WINDOW)
        make_box(f"Boat_Helm_SideWin_{side}_Mullion", (sx, helm_y, win_z),
                 (0.05, 0.04, 0.7), COL_HELM_ROOF)

    # Helm sloped roof — a prism with the ridge running east-west
    helm_roof_base_z = helm_z + HELM_H / 2 + 0.05
    make_prism("Boat_Helm_Roof", (0, helm_y, helm_roof_base_z),
               (HELM_W + 0.5, HELM_L + 0.5, 0.7), COL_HELM_ROOF, pitch_axis='X')

    # ── MAIN ROOF (sloped over the main dining room) ─────────
    main_roof_z = deck_z + 1.85
    make_prism("Boat_MainRoof", (0, -2.0, main_roof_z),
               (BOAT_W * 0.95, BOAT_L * 0.55, 0.9), COL_ROOF, pitch_axis='Y')
    # Roof eave overhang
    make_box("Boat_MainRoof_Eave", (0, -2.0, main_roof_z - 0.02),
             (BOAT_W * 1.02, BOAT_L * 0.58, 0.06), COL_ROOF)

    # ── LIFEBUOYS on rails (4 — two per side) ───────────────
    for i, (lx, ly) in enumerate([(-BOAT_W/2 - 0.30, -6.0), (-BOAT_W/2 - 0.30, 4.0),
                                   ( BOAT_W/2 + 0.30, -6.0), ( BOAT_W/2 + 0.30, 4.0)]):
        # ring approximated as a chunky donut from a 12-segment loop of short boxes
        ring_z = deck_z + 0.30
        ring_r = 0.35
        for j in range(12):
            ang = 2.0 * math.pi * j / 12.0
            rx = lx + math.sin(ang) * 0.02   # always touching the railing edge
            ry = ly + math.cos(ang) * ring_r
            rz = ring_z + math.sin(ang) * ring_r
            # alternate red/white segments for the lifebuoy stripes
            col = (0.85, 0.20, 0.18, 1.0) if (j % 2 == 0) else (0.92, 0.88, 0.78, 1.0)
            make_box(f"Lifebuoy_{i}_seg_{j}", (rx, ry, rz), (0.10, 0.12, 0.12), col)

    # ── GANGWAY ─────────────────────────────────────────────
    gw_y = -BOAT_L/2 - 1.5
    gw_z = deck_z - 0.05
    make_box("Boat_Gangway", (0, gw_y, gw_z), (2.2, 3.0, 0.12), COL_DECK_WOOD)
    # gangway plank lines
    for i in range(4):
        gpx = -0.8 + i * 0.55
        make_box(f"Boat_Gangway_Plank_{i}", (gpx, gw_y, gw_z + 0.07),
                 (0.04, 3.0, 0.01), (0.30, 0.20, 0.12, 1.0))
    # Gangway brass railings + posts
    make_box("Gangway_Rail_W", (-1.05, gw_y, gw_z + 0.55), (0.04, 3.0, 0.04), COL_BRASS)
    make_box("Gangway_Rail_E", (1.05, gw_y, gw_z + 0.55),  (0.04, 3.0, 0.04), COL_BRASS)
    for i in range(3):
        gpy = gw_y - 1.25 + i * 1.25
        make_box(f"Gangway_Post_W_{i}", (-1.05, gpy, gw_z + 0.28), (0.04, 0.04, 0.50), COL_BRASS)
        make_box(f"Gangway_Post_E_{i}", ( 1.05, gpy, gw_z + 0.28), (0.04, 0.04, 0.50), COL_BRASS)


# ════════════════════════════════════════════════════════════════
# THE PARKING LOT
# ════════════════════════════════════════════════════════════════

def build_parking_lot():
    """Asphalt strip south of the boat. Painted lines, sodium light, a few cars."""
    lot_w = 30.0
    lot_l = 18.0
    lot_y = PARKING_Y
    lot_z = -0.02
    make_box("Parking_Asphalt", (0, lot_y, lot_z), (lot_w, lot_l, 0.04), COL_ASPHALT)

    # Painted parking lines (4 spaces, faded yellow strokes)
    line_y_start = lot_y - lot_l / 2 + 2.0
    for i in range(5):
        lx = -lot_w / 2 + 4.0 + i * 5.0
        make_box(f"ParkingLine_{i}",
                 (lx, lot_y, lot_z + 0.025),
                 (0.10, 4.0, 0.005),
                 COL_PAINT_LINE)

    # Sodium streetlight at the northeast corner of the lot — pole as
    # an 8-sided cylinder, lamp head as a tapered prism
    pole_x = lot_w / 2 - 1.0
    pole_y = lot_y + lot_l / 2 - 1.0
    make_cyl("Sodium_Pole", (pole_x, pole_y, 3.0), 0.10, 6.0, COL_SODIUM_POLE, segments=8)
    # Arm connecting head to pole
    make_box("Sodium_Arm", (pole_x - 0.3, pole_y, 5.95), (0.6, 0.08, 0.08), COL_SODIUM_POLE)
    # Light fixture — slope it forward so the lamp face points down-and-out
    make_prism("Sodium_Head", (pole_x - 0.6, pole_y, 5.78), (0.7, 0.5, 0.20), COL_SODIUM_HEAD, pitch_axis='Y')
    # Glowing lens underneath (small bright box facing down)
    make_box("Sodium_Lens", (pole_x - 0.6, pole_y, 5.74), (0.55, 0.40, 0.04), (1.0, 0.72, 0.30, 1.0))

    # 3 parked cars — PS2-era detail: stepped body for profile, 4 wheels,
    # headlights and taillights, separate windshield
    cars = [
        (-10.0, lot_y - 0.5, COL_CAR_BODY_A),
        (-4.0,  lot_y - 0.5, COL_CAR_BODY_B),
        (3.0,   lot_y + 0.5, COL_CAR_BODY_C),
    ]
    for i, (cx, cy, col) in enumerate(cars):
        # Lower body (wider at the bottom, narrower at the wheel arches)
        make_box(f"Car_{i}_body_low", (cx, cy, lot_z + 0.30), (1.75, 4.0, 0.30), col)
        # Mid body
        make_box(f"Car_{i}_body_mid", (cx, cy, lot_z + 0.60), (1.70, 4.1, 0.30), col)
        # Hood (front section, shorter)
        hood_dim_y = 1.4
        make_box(f"Car_{i}_hood",     (cx, cy - 1.30, lot_z + 0.78), (1.65, hood_dim_y, 0.10), col)
        # Trunk (rear section)
        make_box(f"Car_{i}_trunk",    (cx, cy + 1.30, lot_z + 0.78), (1.65, hood_dim_y, 0.10), col)
        # Cabin / greenhouse (between hood and trunk, taller)
        make_box(f"Car_{i}_cabin",    (cx, cy, lot_z + 1.00), (1.55, 1.6, 0.50), col)
        # Cabin roof (slightly inset darker — fakes a vinyl top)
        roof_col = (col[0] * 0.65, col[1] * 0.65, col[2] * 0.65, 1.0)
        make_box(f"Car_{i}_roof",     (cx, cy, lot_z + 1.27), (1.45, 1.55, 0.04), roof_col)
        # Windshield (front slope, fake an angled glass strip)
        make_box(f"Car_{i}_windshield", (cx, cy - 0.85, lot_z + 1.05), (1.45, 0.06, 0.45), COL_CAR_GLASS)
        # Rear window
        make_box(f"Car_{i}_rearwin", (cx, cy + 0.85, lot_z + 1.05), (1.45, 0.06, 0.42), COL_CAR_GLASS)
        # Side windows
        make_box(f"Car_{i}_winL", (cx - 0.78, cy, lot_z + 1.05), (0.02, 1.5, 0.40), COL_CAR_GLASS)
        make_box(f"Car_{i}_winR", (cx + 0.78, cy, lot_z + 1.05), (0.02, 1.5, 0.40), COL_CAR_GLASS)
        # Headlights (two glowing rectangles on the front)
        head_col = (0.95, 0.92, 0.65, 1.0)
        make_box(f"Car_{i}_headL", (cx - 0.55, cy - 2.0, lot_z + 0.45), (0.30, 0.04, 0.18), head_col)
        make_box(f"Car_{i}_headR", (cx + 0.55, cy - 2.0, lot_z + 0.45), (0.30, 0.04, 0.18), head_col)
        # Taillights (red rectangles on rear)
        tail_col = (0.85, 0.18, 0.16, 1.0)
        make_box(f"Car_{i}_tailL", (cx - 0.55, cy + 2.0, lot_z + 0.45), (0.30, 0.04, 0.18), tail_col)
        make_box(f"Car_{i}_tailR", (cx + 0.55, cy + 2.0, lot_z + 0.45), (0.30, 0.04, 0.18), tail_col)
        # Bumpers
        bump_col = (0.18, 0.18, 0.18, 1.0)
        make_box(f"Car_{i}_bumpF", (cx, cy - 2.01, lot_z + 0.25), (1.75, 0.06, 0.18), bump_col)
        make_box(f"Car_{i}_bumpR", (cx, cy + 2.01, lot_z + 0.25), (1.75, 0.06, 0.18), bump_col)
        # 4 wheels (8-segment cylinders, axis along X)
        tire_col = (0.08, 0.08, 0.08, 1.0)
        for wi, (wx, wy) in enumerate([(-0.78, -1.4), (0.78, -1.4), (-0.78, 1.4), (0.78, 1.4)]):
            make_cyl(f"Car_{i}_wheel_{wi}", (cx + wx, cy + wy, lot_z + 0.16),
                     0.28, 0.20, tire_col, segments=8, axis='X')
            # hubcap (small cylinder offset along the wheel axis)
            make_cyl(f"Car_{i}_hub_{wi}",   (cx + wx + (0.11 if wx > 0 else -0.11), cy + wy, lot_z + 0.16),
                     0.10, 0.04, COL_BRASS, segments=6, axis='X')


# ════════════════════════════════════════════════════════════════
# THE RIVER
# ════════════════════════════════════════════════════════════════

def build_river():
    """The water plane the boat sits on. Extends west to the opposite shore, east toward bayou."""
    # Main river expanse — large flat plane at water level
    river_extent_x = 80.0
    river_extent_y = 100.0
    make_box("River_Water",
             (-15, 0, RIVER_LEVEL_Z - 0.01),
             (river_extent_x, river_extent_y, 0.02),
             COL_RIVER,
             open_faces={'-Z'})


# ════════════════════════════════════════════════════════════════
# OPPOSITE SHORELINE
# ════════════════════════════════════════════════════════════════

def build_opposite_shore():
    """Strip of land at the far western edge of the river. Trees + a couple of industrial buildings."""
    shore_x = OPPOSITE_X
    shore_w = 14.0   # depth of the shore strip (into the distance from water)
    shore_l = 90.0   # length along the river
    shore_z = RIVER_LEVEL_Z + 0.20
    make_box("OppositeShore_Land",
             (shore_x - shore_w / 2, 0, shore_z),
             (shore_w, shore_l, 0.40),
             COL_SHORELINE)

    # Far industrial buildings (a few rectangular boxes at varied heights)
    # — with a scatter of lit windows facing the river (east side of each)
    buildings = [
        (-2.0,  -22.0, 6.0,  8.0, 8.0),
        (-4.5,  -8.0,  7.5,  10.0, 12.0),
        (-1.0,  6.0,   5.0,  6.0, 7.0),
        (-3.5,  22.0,  9.0,  9.0, 11.0),
    ]
    lit = (0.95, 0.78, 0.40, 1.0)
    dark = (0.18, 0.16, 0.14, 1.0)
    for i, (dx, y, w, l, h) in enumerate(buildings):
        bx = shore_x + dx
        make_box(f"OppositeBldg_{i}", (bx, y, shore_z + h / 2), (w, l, h), COL_FAR_BUILDING)
        # window grid on the river-facing (+X) side
        rows = max(2, int(h / 2.2))
        cols = max(2, int(l / 2.0))
        for ri in range(rows):
            for ci in range(cols):
                wx = bx + w/2 + 0.02
                wy = y - l/2 + (ci + 0.5) * (l / cols)
                wz = shore_z + 1.0 + (ri + 0.5) * ((h - 1.0) / rows)
                # ~35% of windows lit
                seed = (i * 23 + ri * 7 + ci * 11) & 0xFF
                col = lit if (seed % 100) < 35 else dark
                make_box(f"OppositeBldg_{i}_win_{ri}_{ci}", (wx, wy, wz),
                         (0.04, l / cols * 0.55, (h - 1.0) / rows * 0.55), col)
        # parapet / roof cap
        make_box(f"OppositeBldg_{i}_cap", (bx, y, shore_z + h + 0.15),
                 (w + 0.2, l + 0.2, 0.30), (0.32, 0.30, 0.26, 1.0))

    # Tree line (cypresses and pines) along the shore, sparse
    # Tapered trunks (2-segment) + multi-cluster canopies
    tree_y_positions = [-38, -30, -16, -2, 8, 18, 30, 38]
    for i, y in enumerate(tree_y_positions):
        is_cypress = (i % 2 == 0)
        tree_x = shore_x + 5.0 + (i % 3) * 0.8   # slight zig-zag
        canopy_color = COL_TREE_CANOPY_B if is_cypress else COL_TREE_CANOPY_A
        trunk_h = 5.5 if is_cypress else 4.5
        # tapered trunk: lower wider, upper narrower
        trunk_low_h = trunk_h * 0.55
        trunk_up_h = trunk_h * 0.45
        make_cyl(f"OppoTree_{i}_trunk_low", (tree_x, y, shore_z + trunk_low_h / 2),
                 0.20, trunk_low_h, COL_TREE_TRUNK, segments=6)
        make_cyl(f"OppoTree_{i}_trunk_up",  (tree_x, y, shore_z + trunk_low_h + trunk_up_h / 2),
                 0.13, trunk_up_h, COL_TREE_TRUNK, segments=6)
        # canopy cluster — 3 offset boxes for organic feel
        canopy_size = 3.0 if is_cypress else 2.2
        canopy_base_z = shore_z + trunk_h - 0.4
        for ci, (ox, oy, sz_mul) in enumerate([(0.0, 0.0, 1.0), (-0.4, 0.3, 0.7), (0.4, -0.2, 0.75)]):
            cs = canopy_size * sz_mul
            make_box(f"OppoTree_{i}_canopy_{ci}",
                     (tree_x + ox, y + oy, canopy_base_z + cs * 0.4),
                     (cs, cs, cs * 1.1),
                     canopy_color)


# ════════════════════════════════════════════════════════════════
# OTHER BOATS IN THE RIVER
# ════════════════════════════════════════════════════════════════

def build_other_boats():
    """A few small boats scattered in the river. Tugboats and fishing skiffs."""
    # Tugboat (upriver from D'Ambrosio's, northeast)
    tx, ty = -22.0, 28.0
    tz = RIVER_LEVEL_Z + 0.8
    # stepped hull (bevel)
    make_box("Tugboat_Hull_low", (tx, ty, tz - 0.6), (4.2, 8.0, 0.6), COL_OTHER_BOAT_A)
    make_box("Tugboat_Hull_up",  (tx, ty, tz - 0.1), (4.0, 7.6, 0.5), COL_OTHER_BOAT_A)
    make_box("Tugboat_Cabin", (tx, ty - 1.0, tz + 0.7), (2.6, 3.0, 1.4), COL_HELM_WALL)
    make_prism("Tugboat_Cabin_Roof", (tx, ty - 1.0, tz + 1.40), (2.8, 3.2, 0.4), COL_HELM_ROOF, pitch_axis='X')
    # cylindrical stack with cap
    make_cyl("Tugboat_Stack", (tx, ty - 0.5, tz + 2.2), 0.25, 1.8, COL_SMOKESTACK, segments=8)
    make_cyl("Tugboat_StackCap", (tx, ty - 0.5, tz + 3.05), 0.32, 0.10, COL_BRASS, segments=8)
    make_box("Tugboat_Window", (tx, ty - 2.51, tz + 0.7), (1.6, 0.05, 0.5), COL_HELM_WINDOW)
    make_box("Tugboat_Win_Mullion", (tx, ty - 2.52, tz + 0.7), (1.6, 0.04, 0.04), COL_HELM_ROOF)

    # Fishing skiff (downriver, west) — chunkier prow
    sx, sy = -28.0, -18.0
    sz = RIVER_LEVEL_Z + 0.4
    make_box("Skiff_Hull_low", (sx, sy, sz - 0.30), (1.8, 4.5, 0.30), COL_OTHER_BOAT_B)
    make_box("Skiff_Hull_up",  (sx, sy, sz),       (1.6, 4.3, 0.30), COL_OTHER_BOAT_B)
    # Outboard motor at +Y end (cylinder leg + box housing)
    make_cyl("Skiff_MotorLeg", (sx, sy + 2.45, sz - 0.15), 0.06, 0.45, (0.18, 0.16, 0.14, 1.0), segments=6)
    make_box("Skiff_Motor", (sx, sy + 2.45, sz + 0.20), (0.30, 0.45, 0.40), COL_SMOKESTACK)
    # Bench seat in middle
    make_box("Skiff_Bench", (sx, sy, sz + 0.18), (1.2, 0.30, 0.06), COL_DECK_WOOD)
    # bow point
    make_box("Skiff_Bow", (sx, sy - 2.40, sz - 0.05), (1.0, 0.6, 0.30), COL_OTHER_BOAT_B)

    # Anchored barge way downriver, far south
    bx, by = -8.0, -42.0
    bz = RIVER_LEVEL_Z + 0.5
    make_box("Barge_Hull", (bx, by, bz - 0.25), (5.5, 14.0, 0.6), COL_OTHER_BOAT_A)
    # Stack of containers
    for i in range(3):
        for j in range(2):
            cx = bx - 2.0 + i * 2.0
            cy = by - 5.0 + j * 3.5
            make_box(f"Barge_Container_{i}_{j}", (cx, cy, bz + 0.8), (1.8, 3.2, 1.4),
                     (0.30, 0.32, 0.40, 1.0))


# ════════════════════════════════════════════════════════════════
# THE BAYOU
# ════════════════════════════════════════════════════════════════

def build_bayou():
    """The bayou section east of the boat. Cypress trees in dark swampwater + small pier."""
    bayou_w = 35.0
    bayou_l = 70.0
    bayou_z = RIVER_LEVEL_Z + 0.02   # slightly higher water tint
    bayou_x = BAYOU_X
    # Bayou water (tannin-stained, darker than the main river)
    make_box("Bayou_Water",
             (bayou_x, 0, bayou_z - 0.005),
             (bayou_w, bayou_l, 0.01),
             COL_BAYOU_WATER,
             open_faces={'-Z'})

    # Cypress trees rising out of the swampwater
    cypress_positions = [
        (bayou_x - 12, -28),
        (bayou_x - 8,  -20),
        (bayou_x + 2,  -16),
        (bayou_x - 14, -8),
        (bayou_x - 4,  -2),
        (bayou_x + 8,  4),
        (bayou_x - 10, 10),
        (bayou_x + 0,  18),
        (bayou_x - 6,  24),
        (bayou_x + 6,  30),
        (bayou_x - 12, 32),
        (bayou_x + 12, -6),
    ]
    for i, (cx, cy) in enumerate(cypress_positions):
        # tall narrow cypress — tapered cylindrical trunk (3 segments)
        trunk_h = 7.0 + (i % 3) * 0.8
        seg = trunk_h / 3.0
        make_cyl(f"Cypress_{i}_trunk_low", (cx, cy, bayou_z + seg * 0.5),
                 0.30, seg, COL_TREE_TRUNK, segments=6)
        make_cyl(f"Cypress_{i}_trunk_mid", (cx, cy, bayou_z + seg * 1.5),
                 0.22, seg, COL_TREE_TRUNK, segments=6)
        make_cyl(f"Cypress_{i}_trunk_up",  (cx, cy, bayou_z + seg * 2.5),
                 0.15, seg, COL_TREE_TRUNK, segments=6)
        # canopy — tapered 3-tier stack with slight horizontal offset for organic feel
        canopy_z = bayou_z + trunk_h
        make_box(f"Cypress_{i}_canopy_lower", (cx, cy, canopy_z + 0.5),
                 (2.4, 2.4, 1.0), COL_TREE_CANOPY_B)
        make_box(f"Cypress_{i}_canopy_mid",   (cx - 0.15, cy + 0.15, canopy_z + 1.3),
                 (1.9, 1.9, 0.9), COL_TREE_CANOPY_B)
        make_box(f"Cypress_{i}_canopy_upper", (cx + 0.10, cy - 0.10, canopy_z + 2.0),
                 (1.3, 1.3, 0.8), COL_TREE_CANOPY_B)
        # Spanish moss (every other tree, hanging at trunk midpoint)
        if i % 2 == 0:
            moss_z = bayou_z + trunk_h * 0.65
            make_box(f"Cypress_{i}_moss_a", (cx + 0.30, cy, moss_z),
                     (0.18, 0.16, 0.80), COL_MOSS)
            make_box(f"Cypress_{i}_moss_b", (cx - 0.25, cy + 0.10, moss_z + 0.15),
                     (0.14, 0.14, 0.65), COL_MOSS)

    # Small wooden pier extending into the bayou (where someone might tie a flat-bottomed boat)
    pier_x = bayou_x - 14.0
    pier_y = -2.0
    pier_z = RIVER_LEVEL_Z + 0.30
    make_box("Bayou_Pier", (pier_x, pier_y, pier_z), (3.0, 1.4, 0.12), COL_PIER_WOOD)
    # 4 pier pilings under the deck
    for i in range(4):
        px = pier_x - 1.2 + (i % 2) * 2.4
        py = pier_y - 0.55 + (i // 2) * 1.1
        make_box(f"Pier_Piling_{i}", (px, py, RIVER_LEVEL_Z + 0.05),
                 (0.18, 0.18, 0.50), COL_PIER_WOOD)


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


def main():
    clear_scene()
    build_riverboat()
    build_parking_lot()
    build_river()
    build_opposite_shore()
    build_other_boats()
    build_bayou()
    export_glb()


if __name__ == "__main__":
    main()
