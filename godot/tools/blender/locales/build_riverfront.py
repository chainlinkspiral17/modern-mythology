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


# ════════════════════════════════════════════════════════════════
# THE RIVERBOAT EXTERIOR
# ════════════════════════════════════════════════════════════════

def build_riverboat():
    """The boat's exterior shell. Hull + decks + paddle-wheel + smokestack + helm."""
    # Main hull — the white clapboard mass that holds the diner inside
    hull_z = RIVER_LEVEL_Z + BOAT_HULL_H / 2
    make_box("Boat_Hull", (0, 0, hull_z), (BOAT_W, BOAT_L, BOAT_HULL_H), COL_HULL)

    # Red trim band along the hull (signature riverboat motif)
    band_z = RIVER_LEVEL_Z + 0.55
    make_box("Boat_Trim_W", (-BOAT_W/2 - 0.01, 0, band_z), (0.05, BOAT_L * 0.98, 0.15), COL_HULL_BAND)
    make_box("Boat_Trim_E", (BOAT_W/2 + 0.01, 0, band_z),  (0.05, BOAT_L * 0.98, 0.15), COL_HULL_BAND)
    make_box("Boat_Trim_S", (0, -BOAT_L/2 - 0.01, band_z), (BOAT_W * 0.98, 0.05, 0.15), COL_HULL_BAND)
    make_box("Boat_Trim_N", (0, BOAT_L/2 + 0.01, band_z),  (BOAT_W * 0.98, 0.05, 0.15), COL_HULL_BAND)

    # The main deck (a flat platform on top of the hull — players can walk this)
    deck_z = RIVER_LEVEL_Z + BOAT_HULL_H + DECK_H / 2
    make_box("Boat_MainDeck", (0, 0, deck_z), (BOAT_W + 0.4, BOAT_L + 0.4, DECK_H), COL_DECK_WOOD)

    # Wraparound porch railings (brass)
    rail_z = deck_z + 0.50
    for side in ("W", "E"):
        x = -BOAT_W/2 - 0.2 if side == "W" else BOAT_W/2 + 0.2
        make_box(f"Boat_Rail_{side}", (x, 0, rail_z), (0.05, BOAT_L, 0.05), COL_BRASS)
    for side in ("S", "N"):
        y = -BOAT_L/2 - 0.2 if side == "S" else BOAT_L/2 + 0.2
        make_box(f"Boat_Rail_{side}", (0, y, rail_z), (BOAT_W, 0.05, 0.05), COL_BRASS)
    # Railing vertical posts every 1.5m
    post_color = COL_BRASS
    for i in range(int(BOAT_L / 1.5)):
        y = -BOAT_L/2 + 0.75 + i * 1.5
        make_box(f"Boat_Post_W_{i}", (-BOAT_W/2 - 0.2, y, deck_z + 0.25), (0.04, 0.04, 0.50), post_color)
        make_box(f"Boat_Post_E_{i}", (BOAT_W/2 + 0.2, y, deck_z + 0.25),  (0.04, 0.04, 0.50), post_color)

    # The paddle-wheel housing (signature red, on the +Y end — upriver end)
    pw_y = BOAT_L / 2 + 2.0
    pw_z = RIVER_LEVEL_Z + 1.6
    make_box("Boat_PaddleHousing", (0, pw_y, pw_z), (BOAT_W * 0.7, 0.4, 2.6), COL_PADDLE_HOUSING)
    # Paddle-wheel blades (octagonal arrangement, faked as 8 narrow rectangles)
    pw_axle_z = pw_z
    n_blades = 8
    blade_r = 1.0
    for i in range(n_blades):
        angle = math.radians(i * (360.0 / n_blades))
        bx = math.cos(angle) * blade_r
        bz = math.sin(angle) * blade_r + pw_axle_z
        make_box(f"PaddleBlade_{i}", (bx, pw_y, bz), (0.04, BOAT_W * 0.5, 0.32), COL_PADDLE_BLADES)

    # The smokestack (forward of helm, +Y end of boat)
    stack_y = BOAT_L / 2 - 4.0
    stack_z = deck_z + 3.0
    make_box("Boat_Smokestack", (0, stack_y, stack_z), (0.7, 0.7, 5.0), COL_SMOKESTACK)
    # Crown ring at the top of the smokestack
    make_box("Boat_Stack_Crown", (0, stack_y, stack_z + 2.6), (1.0, 1.0, 0.15), COL_BRASS)

    # The helm cabin (small wooden cabin on the deck where Dante sat)
    helm_y = BOAT_L / 4
    helm_z = deck_z + DECK_H / 2 + HELM_H / 2
    make_box("Boat_Helm_Walls", (0, helm_y, helm_z), (HELM_W, HELM_L, HELM_H), COL_HELM_WALL)
    # The leaded window on the south side (looking down at the dining room)
    make_box("Boat_Helm_Window", (0, helm_y - HELM_L/2 - 0.01, helm_z + 0.4), (1.8, 0.05, 1.0), COL_HELM_WINDOW)
    # Helm roof
    helm_roof_z = helm_z + HELM_H / 2 + 0.1
    make_box("Boat_Helm_Roof", (0, helm_y, helm_roof_z), (HELM_W + 0.4, HELM_L + 0.4, 0.2), COL_HELM_ROOF)

    # Main roof (sloped) — over the main dining room area, south of the helm
    main_roof_z = deck_z + 2.0
    make_box("Boat_MainRoof_lower", (0, -2, main_roof_z),       (BOAT_W * 0.95, BOAT_L * 0.55, 0.3), COL_ROOF)
    make_box("Boat_MainRoof_upper", (0, -2, main_roof_z + 0.6), (BOAT_W * 0.75, BOAT_L * 0.40, 0.3), COL_ROOF)

    # The gangway — connects boat to the parking lot at south end
    gw_y = -BOAT_L/2 - 1.5
    gw_z = deck_z - 0.05
    make_box("Boat_Gangway", (0, gw_y, gw_z), (2.2, 3.0, 0.12), COL_DECK_WOOD)
    # Gangway brass railings
    make_box("Gangway_Rail_W", (-1.05, gw_y, gw_z + 0.55), (0.04, 3.0, 0.04), COL_BRASS)
    make_box("Gangway_Rail_E", (1.05, gw_y, gw_z + 0.55),  (0.04, 3.0, 0.04), COL_BRASS)


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

    # Sodium streetlight at the northeast corner of the lot
    pole_x = lot_w / 2 - 1.0
    pole_y = lot_y + lot_l / 2 - 1.0
    make_box("Sodium_Pole", (pole_x, pole_y, 3.0), (0.15, 0.15, 6.0), COL_SODIUM_POLE)
    # Light fixture at top, angled
    make_box("Sodium_Head", (pole_x - 0.6, pole_y, 5.9), (0.6, 0.4, 0.25), COL_SODIUM_HEAD)
    # Arm connecting head to pole
    make_box("Sodium_Arm", (pole_x - 0.3, pole_y, 5.95), (0.6, 0.08, 0.08), COL_SODIUM_POLE)

    # 3 parked cars
    cars = [
        (-10.0, lot_y - 0.5, COL_CAR_BODY_A),
        (-4.0,  lot_y - 0.5, COL_CAR_BODY_B),
        (3.0,   lot_y + 0.5, COL_CAR_BODY_C),
    ]
    for i, (cx, cy, col) in enumerate(cars):
        # body
        make_box(f"Car_{i}_body", (cx, cy, lot_z + 0.45), (1.7, 4.0, 0.50), col)
        # cabin (slightly narrower box above the body)
        make_box(f"Car_{i}_cabin", (cx, cy - 0.3, lot_z + 0.95), (1.55, 2.4, 0.55), col)
        # windows (darker thin slabs on each side of cabin)
        make_box(f"Car_{i}_winL", (cx - 0.78, cy - 0.3, lot_z + 0.95), (0.02, 2.0, 0.40), COL_CAR_GLASS)
        make_box(f"Car_{i}_winR", (cx + 0.78, cy - 0.3, lot_z + 0.95), (0.02, 2.0, 0.40), COL_CAR_GLASS)
        make_box(f"Car_{i}_winF", (cx, cy - 1.55, lot_z + 0.95), (1.55, 0.02, 0.40), COL_CAR_GLASS)
        make_box(f"Car_{i}_winB", (cx, cy + 0.95, lot_z + 0.95), (1.55, 0.02, 0.40), COL_CAR_GLASS)


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
    buildings = [
        (-2.0,  -22.0, 6.0,  8.0, 8.0),
        (-4.5,  -8.0,  7.5,  10.0, 12.0),
        (-1.0,  6.0,   5.0,  6.0, 7.0),
        (-3.5,  22.0,  9.0,  9.0, 11.0),
    ]
    for i, (dx, y, w, l, h) in enumerate(buildings):
        bx = shore_x + dx
        make_box(f"OppositeBldg_{i}", (bx, y, shore_z + h / 2), (w, l, h), COL_FAR_BUILDING)

    # Tree line (cypresses and pines) along the shore, sparse
    tree_y_positions = [-38, -30, -16, -2, 8, 18, 30, 38]
    for i, y in enumerate(tree_y_positions):
        is_cypress = (i % 2 == 0)
        tree_x = shore_x + 5.0 + (i % 3) * 0.8   # slight zig-zag
        canopy_color = COL_TREE_CANOPY_B if is_cypress else COL_TREE_CANOPY_A
        trunk_h = 5.5 if is_cypress else 4.5
        canopy_size = 3.0 if is_cypress else 2.2
        make_box(f"OppoTree_{i}_trunk", (tree_x, y, shore_z + trunk_h / 2), (0.3, 0.3, trunk_h), COL_TREE_TRUNK)
        make_box(f"OppoTree_{i}_canopy",
                 (tree_x, y, shore_z + trunk_h + canopy_size / 2 - 0.5),
                 (canopy_size, canopy_size, canopy_size * 1.3),
                 canopy_color)


# ════════════════════════════════════════════════════════════════
# OTHER BOATS IN THE RIVER
# ════════════════════════════════════════════════════════════════

def build_other_boats():
    """A few small boats scattered in the river. Tugboats and fishing skiffs."""
    # Tugboat (upriver from D'Ambrosio's, northeast)
    tx, ty = -22.0, 28.0
    tz = RIVER_LEVEL_Z + 0.8
    make_box("Tugboat_Hull", (tx, ty, tz - 0.4), (4.0, 8.0, 1.2), COL_OTHER_BOAT_A)
    make_box("Tugboat_Cabin", (tx, ty - 1.0, tz + 0.7), (2.6, 3.0, 1.4), COL_HELM_WALL)
    make_box("Tugboat_Stack", (tx, ty - 0.5, tz + 2.2), (0.5, 0.5, 1.8), COL_SMOKESTACK)
    make_box("Tugboat_Window", (tx, ty - 2.51, tz + 0.7), (1.6, 0.05, 0.5), COL_HELM_WINDOW)

    # Fishing skiff (downriver, west)
    sx, sy = -28.0, -18.0
    sz = RIVER_LEVEL_Z + 0.4
    make_box("Skiff_Hull", (sx, sy, sz - 0.15), (1.6, 4.5, 0.4), COL_OTHER_BOAT_B)
    # Small outboard motor at +Y end
    make_box("Skiff_Motor", (sx, sy + 2.5, sz + 0.15), (0.30, 0.45, 0.50), COL_SMOKESTACK)
    # Bench seat in middle
    make_box("Skiff_Bench", (sx, sy, sz + 0.10), (1.2, 0.30, 0.04), COL_DECK_WOOD)

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
        # tall narrow cypress
        trunk_h = 7.0 + (i % 3) * 0.8
        make_box(f"Cypress_{i}_trunk", (cx, cy, bayou_z + trunk_h / 2),
                 (0.45, 0.45, trunk_h), COL_TREE_TRUNK)
        # canopy (light, feathery shape — faked as a small tapered stack)
        canopy_z = bayou_z + trunk_h
        make_box(f"Cypress_{i}_canopy_lower", (cx, cy, canopy_z + 0.5),
                 (2.4, 2.4, 1.0), COL_TREE_CANOPY_B)
        make_box(f"Cypress_{i}_canopy_upper", (cx, cy, canopy_z + 1.5),
                 (1.5, 1.5, 1.0), COL_TREE_CANOPY_B)
        # Spanish moss (every other tree, hanging at trunk midpoint)
        if i % 2 == 0:
            moss_z = bayou_z + trunk_h * 0.65
            make_box(f"Cypress_{i}_moss", (cx + 0.30, cy, moss_z),
                     (0.20, 0.18, 0.80), COL_MOSS)

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
