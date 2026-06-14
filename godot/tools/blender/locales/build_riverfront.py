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

    # Spokes + outer rim + blades
    blade_len = BOAT_W * 0.75
    for i in range(pw_blade_n):
        ang = 2.0 * math.pi * i / pw_blade_n
        cos_a = math.cos(ang)
        sin_a = math.sin(ang)
        # SPOKE from hub to rim — use whichever axis is dominant for a clean axis-aligned box
        if abs(cos_a) > abs(sin_a):
            sp_w = abs(cos_a) * pw_radius
            sp_h = 0.06
            cx = cos_a * pw_radius / 2.0
            cz = sin_a * pw_radius / 2.0
            make_box(f"PWSpoke_L_{i}", (cx, pw_y - BOAT_W * 0.30, pw_z + cz), (sp_w, 0.06, sp_h), COL_PADDLE_BLADES)
            make_box(f"PWSpoke_R_{i}", (cx, pw_y + BOAT_W * 0.30, pw_z + cz), (sp_w, 0.06, sp_h), COL_PADDLE_BLADES)
        else:
            sp_h = abs(sin_a) * pw_radius
            sp_w = 0.06
            cx = cos_a * pw_radius / 2.0
            cz = sin_a * pw_radius / 2.0
            make_box(f"PWSpoke_L_{i}", (cx, pw_y - BOAT_W * 0.30, pw_z + cz), (sp_w, 0.06, sp_h), COL_PADDLE_BLADES)
            make_box(f"PWSpoke_R_{i}", (cx, pw_y + BOAT_W * 0.30, pw_z + cz), (sp_w, 0.06, sp_h), COL_PADDLE_BLADES)
        # BLADE plank at the rim, running along the axle
        bx = cos_a * pw_radius
        bz = sin_a * pw_radius + pw_z
        make_box(f"PWBlade_{i}", (bx, pw_y, bz), (0.08, blade_len, 0.50), COL_PADDLE_BLADES)
        # RIM segment connecting this blade to the next (a chord piece)
        ang_next = 2.0 * math.pi * (i + 1) / pw_blade_n
        bx_n = math.cos(ang_next) * pw_radius
        bz_n = math.sin(ang_next) * pw_radius + pw_z
        rim_cx = (bx + bx_n) / 2.0
        rim_cz = (bz + bz_n) / 2.0
        rim_dx = bx_n - bx
        rim_dz = bz_n - bz
        rim_len = math.sqrt(rim_dx * rim_dx + rim_dz * rim_dz)
        # always use an X-aligned thin rim segment to keep the geometry axis-aligned
        make_box(f"PWRim_L_{i}", (rim_cx, pw_y - BOAT_W * 0.30, rim_cz),
                 (abs(rim_dx) + 0.08, 0.06, max(abs(rim_dz), 0.08)), COL_PADDLE_BLADES)
        make_box(f"PWRim_R_{i}", (rim_cx, pw_y + BOAT_W * 0.30, rim_cz),
                 (abs(rim_dx) + 0.08, 0.06, max(abs(rim_dz), 0.08)), COL_PADDLE_BLADES)

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
    # LIFEBUOYS on rails (4 — two per side, boiler-deck level)
    # ════════════════════════════════════════════════════════════
    for i, (lx, ly) in enumerate([(-BD_W/2 - 0.20, -7.0), (-BD_W/2 - 0.20, 5.0),
                                   ( BD_W/2 + 0.20, -7.0), ( BD_W/2 + 0.20, 5.0)]):
        ring_z = BD_Z + 0.85
        ring_r = 0.40
        for j in range(12):
            ang = 2.0 * math.pi * j / 12.0
            rx = lx + math.sin(ang) * 0.04
            ry = ly + math.cos(ang) * ring_r
            rz = ring_z + math.sin(ang) * ring_r
            col = (0.85, 0.20, 0.18, 1.0) if (j % 2 == 0) else (0.92, 0.88, 0.78, 1.0)
            make_box(f"Lifebuoy_{i}_seg_{j}", (rx, ry, rz), (0.10, 0.12, 0.12), col)

    # ════════════════════════════════════════════════════════════
    # GANGWAY — connects boiler deck to parking-lot ground
    # ════════════════════════════════════════════════════════════
    gw_y = -BD_L/2 - 1.5
    gw_z = BD_Z - 0.05
    make_box("Gangway_Deck", (0, gw_y, gw_z), (2.4, 3.4, 0.14), COL_DECK_WOOD)
    for i in range(5):
        gpx = -0.95 + i * 0.475
        make_box(f"Gangway_Plank_{i}", (gpx, gw_y, gw_z + 0.08),
                 (0.04, 3.4, 0.01), (0.30, 0.20, 0.12, 1.0))
    # Railings + posts
    make_box("Gangway_Rail_W_top", (-1.15, gw_y, gw_z + 0.85), (0.05, 3.4, 0.05), COL_BRASS)
    make_box("Gangway_Rail_E_top", ( 1.15, gw_y, gw_z + 0.85), (0.05, 3.4, 0.05), COL_BRASS)
    make_box("Gangway_Rail_W_mid", (-1.15, gw_y, gw_z + 0.45), (0.04, 3.4, 0.04), COL_BRASS)
    make_box("Gangway_Rail_E_mid", ( 1.15, gw_y, gw_z + 0.45), (0.04, 3.4, 0.04), COL_BRASS)
    for i in range(4):
        gpy = gw_y - 1.4 + i * 0.95
        make_box(f"Gangway_Post_W_{i}", (-1.15, gpy, gw_z + 0.45), (0.05, 0.05, 0.85), COL_BRASS)
        make_box(f"Gangway_Post_E_{i}", ( 1.15, gpy, gw_z + 0.45), (0.05, 0.05, 0.85), COL_BRASS)

    # Gangway entry arch on the boat — frames the entry from gangway onto boiler deck
    arch_y = -DR_L/2 - 0.5
    make_box("Entry_Arch_L", (-1.2, arch_y, BD_Z + 1.3), (0.15, 0.15, 2.5), COL_HULL)
    make_box("Entry_Arch_R", ( 1.2, arch_y, BD_Z + 1.3), (0.15, 0.15, 2.5), COL_HULL)
    make_prism("Entry_Arch_Top", (0, arch_y, BD_Z + 2.55), (2.6, 0.20, 0.50), col_gingerbread, pitch_axis='X')

    # Hawser bollards (mooring posts) on the boiler deck near the gangway
    for i, bx in enumerate([-1.8, 1.8]):
        make_cyl(f"Bollard_{i}", (bx, -BD_L/2 + 0.5, BD_Z + 0.40), 0.18, 0.70, (0.32, 0.30, 0.28, 1.0), segments=8)
        make_cyl(f"Bollard_Cap_{i}", (bx, -BD_L/2 + 0.5, BD_Z + 0.78), 0.22, 0.10, (0.32, 0.30, 0.28, 1.0), segments=8)


# ════════════════════════════════════════════════════════════════
# THE PARKING LOT
# ════════════════════════════════════════════════════════════════

def build_parking_lot():
    """Asphalt strip south of the boat. Painted lines, sodium lights,
    8 parked cars, dumpster, phone pole, newspaper boxes, ash can,
    speed bumps, curb stones, bus shelter, signage."""
    lot_w = 36.0
    lot_l = 22.0
    lot_y = PARKING_Y - 8.0   # shifted south to make room for a real dock
    lot_z = -0.02
    make_box("Parking_Asphalt", (0, lot_y, lot_z), (lot_w, lot_l, 0.04), COL_ASPHALT)

    # Curb stones around perimeter (a low concrete edging)
    curb_col = (0.55, 0.52, 0.48, 1.0)
    make_box("Curb_S", (0, lot_y - lot_l/2, 0.10), (lot_w, 0.20, 0.18), curb_col)
    make_box("Curb_N", (0, lot_y + lot_l/2, 0.10), (lot_w, 0.20, 0.18), curb_col)
    make_box("Curb_W", (-lot_w/2, lot_y, 0.10), (0.20, lot_l, 0.18), curb_col)
    make_box("Curb_E", ( lot_w/2, lot_y, 0.10), (0.20, lot_l, 0.18), curb_col)

    # Two rows of painted parking lines (10 spaces total)
    for row_idx, row_y_off in enumerate([-4.5, 4.5]):
        for i in range(11):
            lx = -lot_w/2 + 3.0 + i * 3.0
            make_box(f"ParkingLine_{row_idx}_{i}",
                     (lx, lot_y + row_y_off, lot_z + 0.025),
                     (0.10, 3.5, 0.005),
                     COL_PAINT_LINE)
        # row label stripes (parking lot dividers)
        make_box(f"ParkingDivider_{row_idx}",
                 (0, lot_y + row_y_off - 1.8, lot_z + 0.025),
                 (lot_w - 1.0, 0.10, 0.005),
                 COL_PAINT_LINE)

    # Yellow speed bumps across the entry
    bump_col = (0.72, 0.55, 0.20, 1.0)
    for i in range(2):
        bx = -8.0 + i * 16.0
        make_prism(f"SpeedBump_{i}", (bx, lot_y - lot_l/2 + 4.0, lot_z),
                   (2.4, 0.50, 0.10), bump_col, pitch_axis='Y')

    # Storm drain grate (a darker recessed rectangle)
    make_box("StormDrain", (-12.0, lot_y - lot_l/2 + 1.0, lot_z + 0.02),
             (1.0, 0.5, 0.02), (0.10, 0.10, 0.10, 1.0))
    # Grate slats
    for i in range(5):
        make_box(f"StormDrain_Slat_{i}", (-12.4 + i * 0.20, lot_y - lot_l/2 + 1.0, lot_z + 0.03),
                 (0.04, 0.45, 0.01), (0.20, 0.18, 0.16, 1.0))

    # Sodium streetlights — three poles around the lot perimeter
    sodium_poles = [
        ( lot_w/2 - 1.0,   lot_y + lot_l/2 - 1.0, -1),  # NE corner
        (-lot_w/2 + 1.0,   lot_y + lot_l/2 - 1.0,  1),  # NW corner
        ( 0,               lot_y - lot_l/2 + 1.0,  0),  # center south
    ]
    for si, (px, py, sweep_dir) in enumerate(sodium_poles):
        make_cyl(f"Sodium_Pole_{si}", (px, py, 3.0), 0.10, 6.0, COL_SODIUM_POLE, segments=8)
        # base flange
        make_cyl(f"Sodium_Base_{si}", (px, py, 0.15), 0.18, 0.30, COL_SODIUM_POLE, segments=8)
        # arm + head — sweep toward the lot
        if sweep_dir != 0:
            arm_off = -0.5 * sweep_dir
            head_off = -0.8 * sweep_dir
        else:
            arm_off = 0.0
            head_off = 0.0
        make_box(f"Sodium_Arm_{si}", (px + arm_off, py, 5.95), (0.7, 0.08, 0.08), COL_SODIUM_POLE)
        make_prism(f"Sodium_Head_{si}", (px + head_off, py, 5.78), (0.8, 0.5, 0.22), COL_SODIUM_HEAD, pitch_axis='Y')
        make_box(f"Sodium_Lens_{si}", (px + head_off, py, 5.72), (0.62, 0.42, 0.04), (1.0, 0.72, 0.30, 1.0))

    # ── 8 PARKED CARS (was 3 — now a full lot) ──────────────────────
    cars = [
        (-13.0, lot_y - 4.5,  COL_CAR_BODY_A, 0),
        ( -9.0, lot_y - 4.5,  COL_CAR_BODY_B, 0),
        ( -5.0, lot_y - 4.5,  COL_CAR_BODY_C, 0),
        ( -1.0, lot_y - 4.5,  (0.30, 0.35, 0.50, 1.0), 0),   # blue
        (  6.0, lot_y - 4.5,  (0.65, 0.60, 0.55, 1.0), 0),   # off-white
        ( 11.0, lot_y - 4.5,  COL_CAR_BODY_A, 0),
        (-10.0, lot_y + 4.5,  COL_CAR_BODY_C, 1),            # 180-deg flipped
        (  4.0, lot_y + 4.5,  COL_CAR_BODY_B, 1),
    ]
    for i, (cx, cy, col, flipped) in enumerate(cars):
        front_off = -2.0 if flipped == 0 else 2.0
        back_off  =  2.0 if flipped == 0 else -2.0
        # Lower / mid body / hood / trunk / cabin / roof
        make_box(f"Car_{i}_body_low", (cx, cy, lot_z + 0.30), (1.75, 4.0, 0.30), col)
        make_box(f"Car_{i}_body_mid", (cx, cy, lot_z + 0.60), (1.70, 4.1, 0.30), col)
        hood_dim_y = 1.4
        make_box(f"Car_{i}_hood",     (cx, cy + front_off * 0.65, lot_z + 0.78), (1.65, hood_dim_y, 0.10), col)
        make_box(f"Car_{i}_trunk",    (cx, cy + back_off * 0.65, lot_z + 0.78),  (1.65, hood_dim_y, 0.10), col)
        make_box(f"Car_{i}_cabin",    (cx, cy, lot_z + 1.00), (1.55, 1.6, 0.50), col)
        roof_col = (col[0] * 0.65, col[1] * 0.65, col[2] * 0.65, 1.0)
        make_box(f"Car_{i}_roof",     (cx, cy, lot_z + 1.27), (1.45, 1.55, 0.04), roof_col)
        make_box(f"Car_{i}_windshield", (cx, cy + front_off * 0.425, lot_z + 1.05), (1.45, 0.06, 0.45), COL_CAR_GLASS)
        make_box(f"Car_{i}_rearwin",    (cx, cy + back_off * 0.425, lot_z + 1.05),  (1.45, 0.06, 0.42), COL_CAR_GLASS)
        make_box(f"Car_{i}_winL", (cx - 0.78, cy, lot_z + 1.05), (0.02, 1.5, 0.40), COL_CAR_GLASS)
        make_box(f"Car_{i}_winR", (cx + 0.78, cy, lot_z + 1.05), (0.02, 1.5, 0.40), COL_CAR_GLASS)
        # Headlights / taillights
        head_col = (0.95, 0.92, 0.65, 1.0)
        tail_col = (0.85, 0.18, 0.16, 1.0)
        fy = cy + front_off
        ry = cy + back_off
        make_box(f"Car_{i}_headL", (cx - 0.55, fy, lot_z + 0.45), (0.30, 0.04, 0.18), head_col)
        make_box(f"Car_{i}_headR", (cx + 0.55, fy, lot_z + 0.45), (0.30, 0.04, 0.18), head_col)
        make_box(f"Car_{i}_tailL", (cx - 0.55, ry, lot_z + 0.45), (0.30, 0.04, 0.18), tail_col)
        make_box(f"Car_{i}_tailR", (cx + 0.55, ry, lot_z + 0.45), (0.30, 0.04, 0.18), tail_col)
        # Bumpers
        bump_col = (0.18, 0.18, 0.18, 1.0)
        make_box(f"Car_{i}_bumpF", (cx, fy + (0.01 * (1 if flipped == 0 else -1)), lot_z + 0.25), (1.75, 0.06, 0.18), bump_col)
        make_box(f"Car_{i}_bumpR", (cx, ry + (0.01 * (1 if flipped == 0 else -1)), lot_z + 0.25), (1.75, 0.06, 0.18), bump_col)
        # Side mirrors
        mir_col = (col[0] * 0.8, col[1] * 0.8, col[2] * 0.8, 1.0)
        make_box(f"Car_{i}_mirL", (cx - 0.85, cy + front_off * 0.35, lot_z + 1.10), (0.08, 0.18, 0.10), mir_col)
        make_box(f"Car_{i}_mirR", (cx + 0.85, cy + front_off * 0.35, lot_z + 1.10), (0.08, 0.18, 0.10), mir_col)
        # Grille (front)
        grille_col = (0.20, 0.18, 0.16, 1.0)
        make_box(f"Car_{i}_grille", (cx, fy - 0.02 * (1 if flipped == 0 else -1), lot_z + 0.40), (1.30, 0.04, 0.20), grille_col)
        # Wheels + hubcaps
        tire_col = (0.08, 0.08, 0.08, 1.0)
        for wi, (wx, wy) in enumerate([(-0.78, -1.4), (0.78, -1.4), (-0.78, 1.4), (0.78, 1.4)]):
            make_cyl(f"Car_{i}_wheel_{wi}", (cx + wx, cy + wy, lot_z + 0.16),
                     0.28, 0.20, tire_col, segments=8, axis='X')
            make_cyl(f"Car_{i}_hub_{wi}",   (cx + wx + (0.11 if wx > 0 else -0.11), cy + wy, lot_z + 0.16),
                     0.10, 0.04, COL_BRASS, segments=6, axis='X')

    # ── DUMPSTER (back of the lot, near a building hint) ────────────
    dx, dy = lot_w/2 - 3.0, lot_y + lot_l/2 - 2.0
    dump_col = (0.18, 0.28, 0.30, 1.0)   # municipal dark teal
    make_box("Dumpster_Body", (dx, dy, 0.55), (2.4, 1.6, 1.10), dump_col)
    # angled lid
    make_prism("Dumpster_Lid", (dx, dy, 1.10), (2.4, 1.6, 0.20), (0.14, 0.20, 0.22, 1.0), pitch_axis='X')
    # rusty hinge band
    make_box("Dumpster_HingeBand", (dx, dy + 0.81, 1.10), (2.4, 0.06, 0.04), COL_BRASS)
    # graffiti tag (a bright stripe)
    make_box("Dumpster_Tag", (dx - 0.6, dy - 0.81, 0.55), (1.0, 0.04, 0.30), (0.85, 0.55, 0.20, 1.0))
    # wheels (4 small cylinders)
    for wi, (wx, wy) in enumerate([(-1.0, -0.7), (1.0, -0.7), (-1.0, 0.7), (1.0, 0.7)]):
        make_cyl(f"Dumpster_Wheel_{wi}", (dx + wx, dy + wy, 0.10), 0.10, 0.10, (0.10, 0.10, 0.10, 1.0), segments=6, axis='X')

    # ── PHONE POLE with crossbar, transformer, lines hint ──────────
    pp_x = -lot_w/2 + 1.5
    pp_y = lot_y - lot_l/2 - 1.0
    make_cyl("PhonePole_Shaft", (pp_x, pp_y, 5.5), 0.18, 11.0, (0.42, 0.30, 0.20, 1.0), segments=8)
    # crossbar
    make_box("PhonePole_Crossbar_top", (pp_x, pp_y, 9.8), (2.4, 0.10, 0.10), (0.42, 0.30, 0.20, 1.0))
    make_box("PhonePole_Crossbar_low", (pp_x, pp_y, 8.6), (2.0, 0.10, 0.10), (0.42, 0.30, 0.20, 1.0))
    # transformer canister
    make_cyl("PhonePole_Transformer", (pp_x + 0.35, pp_y, 8.2), 0.22, 0.55, (0.40, 0.38, 0.34, 1.0), segments=8)
    # insulators (small ceramics atop the crossbar)
    for ii, ix in enumerate([-1.0, -0.4, 0.4, 1.0]):
        make_cyl(f"PhonePole_Insulator_{ii}", (pp_x + ix, pp_y, 9.95), 0.06, 0.18, (0.85, 0.80, 0.72, 1.0), segments=6)

    # ── NEWSPAPER BOX rank (3 boxes side by side) ───────────────────
    np_y = lot_y - lot_l/2 + 0.6
    for ni, (nx, col) in enumerate([(-3.0, (0.72, 0.20, 0.16, 1.0)),
                                     (-2.0, (0.20, 0.40, 0.62, 1.0)),
                                     (-1.0, (0.30, 0.30, 0.30, 1.0))]):
        make_box(f"NewsBox_{ni}_body", (nx, np_y, 0.50), (0.45, 0.45, 0.95), col)
        make_box(f"NewsBox_{ni}_top",  (nx, np_y, 1.03), (0.50, 0.50, 0.10), (col[0]*0.6, col[1]*0.6, col[2]*0.6, 1.0))
        # window slot showing the cover
        make_box(f"NewsBox_{ni}_window", (nx, np_y - 0.23, 0.65), (0.30, 0.04, 0.30), (0.85, 0.82, 0.72, 1.0))
        # coin slot
        make_box(f"NewsBox_{ni}_slot", (nx, np_y - 0.23, 0.30), (0.10, 0.02, 0.04), (0.10, 0.10, 0.10, 1.0))

    # ── CIGARETTE / ASH CAN near the gangway entry ──────────────────
    ac_x = 1.6
    ac_y = lot_y - lot_l/2 + 0.5
    make_cyl("AshCan_Body", (ac_x, ac_y, 0.55), 0.28, 1.10, (0.22, 0.20, 0.18, 1.0), segments=8)
    make_cyl("AshCan_Top",  (ac_x, ac_y, 1.10), 0.32, 0.10, (0.45, 0.42, 0.36, 1.0), segments=8)
    # the sand-filled receptacle on top
    make_cyl("AshCan_Sand", (ac_x, ac_y, 1.18), 0.20, 0.04, (0.65, 0.60, 0.50, 1.0), segments=8)

    # ── BUS-STOP BENCH near the entry curb ─────────────────────────
    bb_x = -3.5
    bb_y = lot_y - lot_l/2 + 0.6
    make_box("BusBench_Seat", (bb_x, bb_y, 0.45), (1.8, 0.40, 0.10), (0.30, 0.22, 0.16, 1.0))
    make_box("BusBench_Back", (bb_x, bb_y + 0.16, 0.85), (1.8, 0.06, 0.70), (0.30, 0.22, 0.16, 1.0))
    for li, lx_off in enumerate([-0.80, 0.80]):
        make_box(f"BusBench_Leg_{li}", (bb_x + lx_off, bb_y, 0.22), (0.10, 0.40, 0.45), (0.18, 0.18, 0.18, 1.0))

    # ── "D'AMBROSIO'S" SIGN POLE at lot entry ──────────────────────
    sign_x = lot_w/2 - 2.0
    sign_y = lot_y - lot_l/2 - 0.5
    make_cyl("Sign_Pole", (sign_x, sign_y, 3.5), 0.12, 7.0, (0.30, 0.28, 0.24, 1.0), segments=8)
    # double sign panels (two-sided)
    make_box("Sign_Panel_W", (sign_x - 0.06, sign_y, 5.5), (0.04, 2.4, 1.6), (0.55, 0.20, 0.16, 1.0))
    make_box("Sign_Panel_E", (sign_x + 0.06, sign_y, 5.5), (0.04, 2.4, 1.6), (0.55, 0.20, 0.16, 1.0))
    # gold letter strip (just a bright bar — readable as "lettering" at PS2 distance)
    make_box("Sign_Text_W", (sign_x - 0.09, sign_y, 5.5), (0.02, 1.8, 0.4), (0.95, 0.78, 0.42, 1.0))
    make_box("Sign_Text_E", (sign_x + 0.09, sign_y, 5.5), (0.02, 1.8, 0.4), (0.95, 0.78, 0.42, 1.0))
    # sign frame (top and bottom trim)
    make_box("Sign_Frame_W_top", (sign_x - 0.06, sign_y, 6.32), (0.05, 2.5, 0.10), (0.30, 0.28, 0.24, 1.0))
    make_box("Sign_Frame_W_low", (sign_x - 0.06, sign_y, 4.68), (0.05, 2.5, 0.10), (0.30, 0.28, 0.24, 1.0))
    make_box("Sign_Frame_E_top", (sign_x + 0.06, sign_y, 6.32), (0.05, 2.5, 0.10), (0.30, 0.28, 0.24, 1.0))
    make_box("Sign_Frame_E_low", (sign_x + 0.06, sign_y, 4.68), (0.05, 2.5, 0.10), (0.30, 0.28, 0.24, 1.0))

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
# THE DOCK — wooden pier between parking lot and boat hull
# ════════════════════════════════════════════════════════════════

def build_dock():
    """Wooden dock extending from the parking-lot edge to the boat hull.
    Carries the gangway, mooring bollards, cargo, lanterns, ropes."""
    DK_W = 8.0
    # dock spans the gap between parking lot (PARKING_Y - 8 + 11 ≈ -21) and boat hull (Y ≈ -12)
    dock_y_start = PARKING_Y - 8.0 + 11.0   # north edge of parking lot
    dock_y_end   = -BOAT_L / 2 - 0.3         # south edge of boat hull
    dock_cy = (dock_y_start + dock_y_end) / 2.0
    dock_l = dock_y_end - dock_y_start
    dock_z = -0.40   # top of dock just above water
    make_box("Dock_Deck", (0, dock_cy, dock_z), (DK_W, dock_l, 0.20), COL_DECK_WOOD)
    # plank lines along the dock
    for i in range(int(dock_l / 0.30)):
        py = dock_y_start + 0.20 + i * 0.30
        make_box(f"Dock_Plank_{i}", (0, py, dock_z + 0.105),
                 (DK_W - 0.2, 0.04, 0.01), (0.30, 0.20, 0.12, 1.0))

    # Pilings driven into the river under the dock (8 along each side + cross-rows)
    piling_zc = -1.8
    piling_h = 3.0
    for row_idx, py in enumerate([dock_y_start + 0.5, dock_cy - 1.5, dock_cy + 1.5, dock_y_end - 0.5]):
        for ci, cx in enumerate([-DK_W/2 + 0.2, -DK_W/4, DK_W/4, DK_W/2 - 0.2]):
            make_cyl(f"Dock_Piling_{row_idx}_{ci}", (cx, py, piling_zc), 0.16, piling_h,
                     COL_PIER_WOOD, segments=6)

    # Heavy mooring bollards along the dock edges (boat side)
    for i, bx in enumerate([-DK_W/2 + 0.6, DK_W/2 - 0.6]):
        by = dock_y_end - 0.6
        make_cyl(f"Dock_Bollard_{i}", (bx, by, dock_z + 0.50), 0.22, 0.80, (0.32, 0.30, 0.26, 1.0), segments=8)
        make_cyl(f"Dock_Bollard_Cap_{i}", (bx, by, dock_z + 0.92), 0.28, 0.12, (0.32, 0.30, 0.26, 1.0), segments=8)
        # mooring rope — a thick segmented line from the bollard up to the boat trim
        for ri in range(6):
            rt = ri / 5.0
            rx = bx
            ry = by + rt * (dock_y_end + 0.3 - by)
            rz = dock_z + 0.92 + rt * (1.40)   # arcing up to the boat hull
            sag = math.sin(rt * math.pi) * 0.20   # rope sags in the middle
            make_box(f"Dock_Rope_{i}_seg_{ri}", (rx, ry, rz - sag),
                     (0.08, 0.20, 0.08), (0.55, 0.40, 0.25, 1.0))

    # Cargo: stacked wooden crates, a couple of metal drums, fishing nets
    # Crate stack on the east side of the dock
    crate_col = (0.55, 0.35, 0.20, 1.0)
    crate_band = (0.32, 0.22, 0.14, 1.0)
    crate_origin = (DK_W/2 - 1.0, dock_y_start + 2.0)
    for ci, (ox, oy, oz, sw, sl, sh) in enumerate([
        (0,    0,   0,    1.0, 1.0, 0.8),
        (0,    1.1, 0,    1.0, 1.0, 0.8),
        (0,    0,   0.85, 1.0, 1.0, 0.8),
        (0,    1.1, 0.85, 1.0, 1.0, 0.8),
        (-1.1, 0.55, 0,   1.2, 1.2, 1.0),
        (-1.1, 0.55, 1.05, 1.0, 1.0, 0.8),
    ]):
        cx = crate_origin[0] + ox
        cy = crate_origin[1] + oy
        cz_c = dock_z + 0.10 + oz + sh / 2.0
        make_box(f"Crate_{ci}", (cx, cy, cz_c), (sw, sl, sh), crate_col)
        # banding for crate-ness
        make_box(f"Crate_{ci}_band1", (cx, cy + sl/2 + 0.01, cz_c), (sw, 0.03, sh * 0.7), crate_band)
        make_box(f"Crate_{ci}_band2", (cx, cy - sl/2 - 0.01, cz_c), (sw, 0.03, sh * 0.7), crate_band)
    # Three rusty drums on the west side
    for di, (dx_off, dy_off) in enumerate([(0, 0), (0.85, 0.0), (0.42, 0.85)]):
        dx_d = -DK_W/2 + 1.0 + dx_off
        dy_d = dock_y_start + 3.0 + dy_off
        make_cyl(f"Drum_{di}", (dx_d, dy_d, dock_z + 0.10 + 0.45), 0.40, 0.90, (0.55, 0.30, 0.20, 1.0), segments=8)
        make_cyl(f"Drum_{di}_top", (dx_d, dy_d, dock_z + 0.10 + 0.92), 0.42, 0.04, (0.42, 0.22, 0.14, 1.0), segments=8)
        # rust band
        make_cyl(f"Drum_{di}_band", (dx_d, dy_d, dock_z + 0.10 + 0.45), 0.42, 0.08, (0.32, 0.18, 0.12, 1.0), segments=8)

    # Coiled rope pile
    for ri in range(3):
        make_cyl(f"RopeCoil_{ri}", (-2.0, dock_y_start + 5.0, dock_z + 0.12 + ri * 0.08),
                 0.45 - ri * 0.05, 0.07, (0.55, 0.40, 0.25, 1.0), segments=10)

    # Lobster trap stack
    trap_col = (0.40, 0.30, 0.18, 1.0)
    for ti, oy in enumerate([0, 0.85, 1.7]):
        ty_p = dock_y_start + 7.5
        make_box(f"LobsterTrap_{ti}", (-3.0, ty_p + oy, dock_z + 0.10 + 0.20), (0.90, 0.70, 0.40), trap_col)
        # slat detail
        for si in range(4):
            make_box(f"LobsterTrap_{ti}_slat_{si}", (-3.0 + (-0.3 + si * 0.20), ty_p + oy + 0.37, dock_z + 0.10 + 0.20),
                     (0.04, 0.04, 0.40), (0.55, 0.45, 0.30, 1.0))

    # ── Dock lanterns (two wooden lamp posts) ──
    for li, (lx, ly) in enumerate([(-DK_W/2 - 0.4, dock_cy - 2.0), (DK_W/2 + 0.4, dock_cy + 2.0)]):
        make_cyl(f"DockLamp_Pole_{li}", (lx, ly, dock_z + 1.5), 0.08, 3.0, (0.30, 0.22, 0.14, 1.0), segments=6)
        # lantern housing
        make_box(f"DockLamp_Housing_{li}", (lx, ly, dock_z + 3.1), (0.30, 0.30, 0.40), (0.20, 0.18, 0.14, 1.0))
        # glowing pane
        make_box(f"DockLamp_Glow_{li}",    (lx, ly, dock_z + 3.0), (0.22, 0.22, 0.26), (1.0, 0.78, 0.36, 1.0))
        # peaked cap
        make_prism(f"DockLamp_Cap_{li}", (lx, ly, dock_z + 3.32), (0.34, 0.34, 0.16), (0.20, 0.18, 0.14, 1.0), pitch_axis='X')

    # ── Dock railings on the east/west edges ──
    for side, sx in (("W", -DK_W/2 - 0.05), ("E", DK_W/2 + 0.05)):
        make_box(f"Dock_Rail_{side}_top", (sx, dock_cy, dock_z + 1.0), (0.05, dock_l - 0.4, 0.05), COL_BRASS)
        make_box(f"Dock_Rail_{side}_mid", (sx, dock_cy, dock_z + 0.6), (0.04, dock_l - 0.4, 0.04), COL_BRASS)
        for ii in range(int((dock_l - 0.4) / 0.6)):
            sy = dock_y_start + 0.3 + ii * 0.6
            make_box(f"Dock_Spindle_{side}_{ii}", (sx, sy, dock_z + 0.55), (0.04, 0.04, 0.95), (0.32, 0.30, 0.26, 1.0))


# ════════════════════════════════════════════════════════════════
# OPPOSITE SHORELINE
# ════════════════════════════════════════════════════════════════

def build_opposite_shore():
    """Far shore: industrial sprawl with refinery, water tower, smokestack
    plumes, billboards, power lines, plus a tree line."""
    shore_x = OPPOSITE_X
    shore_w = 18.0
    shore_l = 110.0
    shore_z = RIVER_LEVEL_Z + 0.20
    make_box("OppositeShore_Land",
             (shore_x - shore_w / 2, 0, shore_z),
             (shore_w, shore_l, 0.40),
             COL_SHORELINE)
    # Riprap / boulder line at the shoreline (a row of irregular blocks)
    rip_col = (0.42, 0.38, 0.32, 1.0)
    for i in range(22):
        ry = -shore_l/2 + 2.0 + i * (shore_l - 4.0) / 21.0
        offset = ((i * 17) % 7 - 3) * 0.08
        size = 0.50 + ((i * 13) % 5) * 0.12
        make_box(f"Shore_Rock_{i}", (shore_x + 6.5 + offset, ry, RIVER_LEVEL_Z + 0.22),
                 (size, size, size * 0.7), rip_col)

    # Wider variety of buildings — refinery cluster + warehouses + small structures
    buildings = [
        # (dx_from_shore_x, y, w, l, h, color_override or None, kind)
        (-1.0,  -42.0,  4.0,  6.0,  4.0,  None, 'shed'),
        (-2.5,  -32.0,  6.0,  7.0,  6.5,  None, 'warehouse'),
        (-4.0,  -22.0,  6.5,  8.5,  8.0,  None, 'warehouse'),
        (-5.5,  -10.0,  8.0, 10.0, 12.0,  None, 'refinery'),
        (-6.0,   2.0,   8.5, 12.0, 14.0,  None, 'refinery'),
        (-3.0,  12.0,   5.0,  6.0,  7.0,  None, 'warehouse'),
        (-1.5,  20.0,   4.0,  5.0,  5.5,  None, 'shed'),
        (-4.0,  30.0,   7.0,  9.0, 10.0,  None, 'warehouse'),
        (-2.0,  40.0,   5.0,  6.5,  6.5,  None, 'warehouse'),
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
        # window grid on the river-facing (+X) side
        rows = max(2, int(h / 2.2))
        cols = max(2, int(l / 2.0))
        for ri in range(rows):
            for ci in range(cols):
                wx = bx + w/2 + 0.02
                wy = y - l/2 + (ci + 0.5) * (l / cols)
                wz = shore_z + 1.0 + (ri + 0.5) * ((h - 1.0) / rows)
                seed = (i * 23 + ri * 7 + ci * 11) & 0xFF
                col = lit if (seed % 100) < 35 else dark
                make_box(f"OppositeBldg_{i}_win_{ri}_{ci}", (wx, wy, wz),
                         (0.04, l / cols * 0.55, (h - 1.0) / rows * 0.55), col)
        # parapet / roof cap
        make_box(f"OppositeBldg_{i}_cap", (bx, y, shore_z + h + 0.15),
                 (w + 0.2, l + 0.2, 0.30), (0.32, 0.30, 0.26, 1.0))
        # refinery extras: tall narrow smokestack rising from the roof
        if kind == 'refinery':
            make_cyl(f"OppositeBldg_{i}_Stack", (bx - 1.0, y - 1.0, shore_z + h + 4.5),
                     0.50, 9.0, (0.24, 0.20, 0.16, 1.0), segments=8)
            make_cyl(f"OppositeBldg_{i}_StackCap", (bx - 1.0, y - 1.0, shore_z + h + 9.1),
                     0.65, 0.20, COL_BRASS, segments=8)
            # smoke plume (a series of tinted boxes drifting eastward)
            for pi in range(5):
                make_box(f"OppositeBldg_{i}_Smoke_{pi}",
                         (bx - 1.0 + pi * 1.2, y - 1.0 - pi * 0.4, shore_z + h + 9.5 + pi * 0.6),
                         (1.4 + pi * 0.3, 1.4 + pi * 0.3, 0.7 + pi * 0.15),
                         (0.55, 0.50, 0.46, 1.0))
            # exterior pipework — a couple of horizontal pipes along the side
            for pi in range(3):
                pz = shore_z + 1.5 + pi * 1.4
                make_cyl(f"OppositeBldg_{i}_Pipe_{pi}", (bx + w/2 + 0.30, y, pz),
                         0.18, l - 0.4, (0.32, 0.30, 0.28, 1.0), segments=6, axis='Y')
                # pipe support brackets
                make_box(f"OppositeBldg_{i}_PipeSup_{pi}", (bx + w/2 + 0.16, y, pz - 0.25),
                         (0.18, 0.10, 0.50), (0.32, 0.30, 0.28, 1.0))
        # warehouse: large rolling-door rectangle on the river side
        if kind == 'warehouse':
            door_col = (0.32, 0.30, 0.26, 1.0)
            make_box(f"OppositeBldg_{i}_Door", (bx + w/2 + 0.02, y, shore_z + 1.6),
                     (0.05, l * 0.4, 3.0), door_col)
            # door panel lines
            for di in range(4):
                make_box(f"OppositeBldg_{i}_DoorLine_{di}", (bx + w/2 + 0.06, y, shore_z + 0.4 + di * 0.7),
                         (0.02, l * 0.4 - 0.1, 0.03), (0.18, 0.16, 0.14, 1.0))

    # ── WATER TOWER (silhouette landmark, far back) ──
    wt_x = shore_x - 11.0
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

    # ── BILLBOARD on the shoreline ──
    bb_x = shore_x + 5.5
    bb_y = -12.0
    make_cyl("Billboard_Pole_L", (bb_x - 1.6, bb_y, shore_z + 3.5), 0.15, 7.0, (0.30, 0.28, 0.24, 1.0), segments=6)
    make_cyl("Billboard_Pole_R", (bb_x + 1.6, bb_y, shore_z + 3.5), 0.15, 7.0, (0.30, 0.28, 0.24, 1.0), segments=6)
    make_box("Billboard_Panel", (bb_x, bb_y, shore_z + 6.5), (4.5, 0.12, 2.5), (0.72, 0.62, 0.42, 1.0))
    make_box("Billboard_Frame_T", (bb_x, bb_y, shore_z + 7.8), (4.7, 0.16, 0.10), (0.30, 0.28, 0.24, 1.0))
    make_box("Billboard_Frame_B", (bb_x, bb_y, shore_z + 5.2), (4.7, 0.16, 0.10), (0.30, 0.28, 0.24, 1.0))
    # decorative band suggesting big lettering
    make_box("Billboard_Text", (bb_x, bb_y - 0.07, shore_z + 6.5), (3.6, 0.04, 0.80), (0.40, 0.16, 0.14, 1.0))

    # ── POWER-LINE PYLON row crossing along the shore ──
    for pi, py in enumerate([-44.0, -16.0, 14.0, 42.0]):
        pylon_x = shore_x + 4.0
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
    pylon_ys = [-44.0, -16.0, 14.0, 42.0]
    for ai in range(len(pylon_ys) - 1):
        ya = pylon_ys[ai]
        yb = pylon_ys[ai + 1]
        ymid = (ya + yb) / 2.0
        length = abs(yb - ya)
        for li, lx_off in enumerate([-2.4, -1.0, 1.0, 2.4]):
            # cable sags slightly in the middle — fake by lowering Z a bit
            make_box(f"PowerLine_{ai}_cable_{li}", (shore_x + 4.0 + lx_off, ymid, shore_z + 18.6),
                     (0.05, length, 0.05), (0.18, 0.18, 0.18, 1.0))

    # ── BIG TREE LINE — denser, more variety (16 trees) ──
    tree_positions = [
        -50, -45, -38, -34, -28, -22, -17, -11, -6, -1,
         4,  10,  16,  22,  29,  36,  44,  50,
    ]
    for i, y in enumerate(tree_positions):
        kind = i % 3  # 0 = cypress, 1 = pine, 2 = oak
        zig = ((i % 5) - 2) * 0.7
        tree_x = shore_x + 7.5 + zig
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
            # pine — conical stack
            for ci, (sz_mul, dz) in enumerate([(1.0, 0.0), (0.75, 0.9), (0.50, 1.7), (0.30, 2.4)]):
                cs = canopy_size * sz_mul
                make_box(f"OppoTree_{i}_pine_{ci}", (tree_x, y, canopy_base_z + dz),
                         (cs, cs, cs * 0.6), canopy_color)
        else:
            # cypress / oak — multi-cluster
            for ci, (ox, oy, sz_mul) in enumerate([(0.0, 0.0, 1.0), (-0.5, 0.3, 0.75),
                                                    (0.5, -0.3, 0.80), (0.0, 0.5, 0.60)]):
                cs = canopy_size * sz_mul
                make_box(f"OppoTree_{i}_canopy_{ci}",
                         (tree_x + ox, y + oy, canopy_base_z + cs * 0.4 + ((ci % 2) * 0.4)),
                         (cs, cs, cs * 1.1),
                         canopy_color)

    # ── FOREGROUND scrub bushes at the shoreline ──
    bush_col = (0.30, 0.36, 0.22, 1.0)
    for bi, by in enumerate([-46, -36, -25, -14, -3, 7, 19, 28, 38, 47]):
        bx_b = shore_x + 6.3 + ((bi % 3) - 1) * 0.4
        for ci, (ox, oy, sz_v) in enumerate([(0.0, 0.0, 0.8), (-0.4, 0.2, 0.6), (0.4, -0.1, 0.65)]):
            make_box(f"Shore_Bush_{bi}_{ci}", (bx_b + ox, by + oy, shore_z + 0.40),
                     (sz_v, sz_v, sz_v * 0.7), bush_col)


# ════════════════════════════════════════════════════════════════
# OTHER BOATS IN THE RIVER
# ════════════════════════════════════════════════════════════════

def build_other_boats():
    """Multiple other vessels scattered across the river — tugboats,
    fishing skiffs, barge, small motor cruiser, rowboat, channel buoys."""
    # ── Tugboat (upriver, northeast) ──
    tx, ty = -22.0, 28.0
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

    # ── Fishing skiff (downriver, west) ──
    sx, sy = -28.0, -18.0
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

    # ── Anchored barge with containers ──
    bx, by = -8.0, -42.0
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

    # ── Motor cruiser (small pleasure boat) ──
    mx, my = -16.0, -30.0
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

    # ── Channel marker buoys (3 floating in the river) ──
    for bi, (buoyx, buoy_y, b_red) in enumerate([(-2.0, -28.0, True), (4.0, 8.0, False),
                                                  (-6.0, 16.0, True)]):
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
    """Bayou east of the boat. Dense cypress, fallen logs, reeds, lily
    pads, a fishing camp shack on stilts, abandoned boat, paddleboat."""
    bayou_w = 40.0
    bayou_l = 80.0
    bayou_z = RIVER_LEVEL_Z + 0.02
    bayou_x = BAYOU_X
    make_box("Bayou_Water",
             (bayou_x, 0, bayou_z - 0.005),
             (bayou_w, bayou_l, 0.01),
             COL_BAYOU_WATER,
             open_faces={'-Z'})

    # ── 26 CYPRESS (was 12) — denser swamp ──
    cypress_positions = [
        (bayou_x - 14, -32), (bayou_x - 6,  -28), (bayou_x + 2,  -24),
        (bayou_x + 10, -22), (bayou_x - 16, -20), (bayou_x - 8,  -16),
        (bayou_x + 4,  -14), (bayou_x + 12, -10), (bayou_x - 12, -8),
        (bayou_x - 2,  -4),  (bayou_x + 6,  -2),  (bayou_x - 10, 2),
        (bayou_x - 18,  6),  (bayou_x + 0,  8),   (bayou_x + 10, 6),
        (bayou_x + 16,  4),  (bayou_x - 14, 14),  (bayou_x - 4,  16),
        (bayou_x + 6,  18),  (bayou_x + 14, 14),  (bayou_x - 8,  24),
        (bayou_x + 4,  26),  (bayou_x + 12, 24),  (bayou_x - 16, 30),
        (bayou_x - 6,  32),  (bayou_x + 8,  34),
    ]
    for i, (cx, cy) in enumerate(cypress_positions):
        trunk_h = 7.0 + (i % 5) * 0.7
        seg = trunk_h / 3.0
        # flared base (cypress "knees" — wider at the water)
        make_cyl(f"Cypress_{i}_base", (cx, cy, bayou_z + 0.25), 0.40, 0.50, COL_TREE_TRUNK, segments=6)
        make_cyl(f"Cypress_{i}_trunk_low", (cx, cy, bayou_z + seg * 0.5 + 0.50),
                 0.30, seg, COL_TREE_TRUNK, segments=6)
        make_cyl(f"Cypress_{i}_trunk_mid", (cx, cy, bayou_z + seg * 1.5 + 0.50),
                 0.22, seg, COL_TREE_TRUNK, segments=6)
        make_cyl(f"Cypress_{i}_trunk_up",  (cx, cy, bayou_z + seg * 2.5 + 0.50),
                 0.15, seg, COL_TREE_TRUNK, segments=6)
        canopy_z = bayou_z + trunk_h + 0.50
        make_box(f"Cypress_{i}_canopy_lower", (cx, cy, canopy_z + 0.5),
                 (2.6, 2.6, 1.0), COL_TREE_CANOPY_B)
        make_box(f"Cypress_{i}_canopy_mid",   (cx - 0.15, cy + 0.15, canopy_z + 1.3),
                 (2.0, 2.0, 0.9), COL_TREE_CANOPY_B)
        make_box(f"Cypress_{i}_canopy_upper", (cx + 0.10, cy - 0.10, canopy_z + 2.0),
                 (1.4, 1.4, 0.8), COL_TREE_CANOPY_B)
        # cypress knees around the base (little stumps sticking up)
        for ki in range(3):
            ang_k = (i * 37 + ki * 120) % 360
            kx = cx + math.cos(math.radians(ang_k)) * 0.85
            ky = cy + math.sin(math.radians(ang_k)) * 0.85
            make_cyl(f"Cypress_{i}_knee_{ki}", (kx, ky, bayou_z + 0.15), 0.10, 0.35,
                     COL_TREE_TRUNK, segments=4)
        # Spanish moss (more of it, longer)
        if i % 2 == 0:
            moss_z = bayou_z + trunk_h * 0.70 + 0.50
            make_box(f"Cypress_{i}_moss_a", (cx + 0.30, cy, moss_z),
                     (0.18, 0.16, 1.10), COL_MOSS)
            make_box(f"Cypress_{i}_moss_b", (cx - 0.25, cy + 0.10, moss_z + 0.15),
                     (0.14, 0.14, 0.90), COL_MOSS)
            make_box(f"Cypress_{i}_moss_c", (cx + 0.05, cy - 0.30, moss_z - 0.30),
                     (0.12, 0.12, 1.20), COL_MOSS)

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


def build_distant_atmosphere():
    """Big-scale far-distance landmarks visible behind everything else.
    A distant bridge upriver, far hills on the horizon, a few low cloud
    shelves."""

    # ── Far hills on the horizon behind the opposite shore ──
    for hi, (hx, hy, hw, hl, hh) in enumerate([
        (OPPOSITE_X - 22, -45, 18, 32, 8),
        (OPPOSITE_X - 28, -10, 25, 35, 12),
        (OPPOSITE_X - 24,  20, 20, 30, 10),
        (OPPOSITE_X - 30,  45, 22, 28, 14),
    ]):
        make_box(f"FarHill_{hi}", (hx, hy, RIVER_LEVEL_Z + hh / 2),
                 (hw, hl, hh), (0.32, 0.36, 0.36, 1.0))

    # ── Distant bridge upriver (a far-off truss bridge crossing the river) ──
    br_y = 70.0
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

    # ── A few low cloud shelves drifting overhead ──
    for ci_c, (cx, cy, cz_c, cw, cl) in enumerate([
        (-10, -40, 24, 14, 10),
        ( 14, -10, 28, 18, 12),
        (-22,  20, 22, 16, 12),
        (  8,  50, 26, 20, 14),
        ( 30, -28, 30, 14, 10),
    ]):
        # main cloud body
        make_box(f"Cloud_{ci_c}_a", (cx, cy, cz_c), (cw, cl, 1.8), (0.72, 0.68, 0.62, 1.0))
        # offset puffs for organic feel
        make_box(f"Cloud_{ci_c}_b", (cx + cw * 0.20, cy + cl * 0.15, cz_c + 0.6),
                 (cw * 0.55, cl * 0.55, 1.4), (0.78, 0.74, 0.68, 1.0))
        make_box(f"Cloud_{ci_c}_c", (cx - cw * 0.15, cy + cl * 0.20, cz_c + 0.3),
                 (cw * 0.65, cl * 0.45, 1.2), (0.70, 0.66, 0.60, 1.0))
        make_box(f"Cloud_{ci_c}_d", (cx + cw * 0.10, cy - cl * 0.10, cz_c + 0.5),
                 (cw * 0.50, cl * 0.50, 1.3), (0.74, 0.70, 0.64, 1.0))

    # ── A sandy beach strip between the dock and the boat hull ──
    sand_col = (0.62, 0.55, 0.40, 1.0)
    sand_y = -BOAT_L / 2 - 4.0
    make_box("Sand_Strip", (0, sand_y, -0.45), (14.0, 1.6, 0.10), sand_col)
    # a few rocks scattered
    for ri_s in range(5):
        rx_s = -5.0 + ri_s * 2.5
        make_box(f"Sand_Rock_{ri_s}", (rx_s, sand_y + ((ri_s % 2) * 0.4 - 0.2), -0.35),
                 (0.4, 0.4, 0.2), (0.42, 0.38, 0.32, 1.0))


def main():
    clear_scene()
    build_riverboat()
    build_parking_lot()
    build_dock()
    build_river()
    build_opposite_shore()
    build_other_boats()
    build_bayou()
    build_distant_atmosphere()
    export_glb()


if __name__ == "__main__":
    main()
