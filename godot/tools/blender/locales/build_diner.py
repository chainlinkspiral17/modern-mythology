"""
build_diner.py
══════════════════════════════════════════════════════════════════
VOL 5 · CHAPTER 0 · THE FOOL · D'Ambrosio's diner.

Run:
    blender --background --python build_diner.py

Output:
    godot/assets/3d/locales/diner.glb

Geometry: ~3-5k triangles. Per-face vertex colors as MATERIAL
identifiers (warm wood, formica white, vinyl red, brass, river-
blue glass, brick exterior, etc.) — NOT baked lighting. The
locale's lighting lives in the Godot .tscn file as runtime
Light3D nodes, swappable by mood (lunch / dusk / 3:47_am /
night / precipice).

Canon (per _VOL5_WIKI.md):
    "A weathered diner complex moored on the river bank — half-
    restaurant, half-riverboat-architecture. White clapboard
    exterior, brass rails, a wraparound porch over the water.
    Inside: counter at center, vinyl booths along the windows,
    kitchen alcove on the river side, a closed cocktail bar to
    the parking-lot side, a back hallway with payphone + bathroom
    + the card-pinned wall."

Thresholds: PARKING LOT (sodium light, asphalt) and RIVER WINDOW
(cold blue, moving water). The PRECIPICE DOOR appears mid-run as
a too-tall narrow door that doesn't match the trim — included
in the geometry but flagged to be hidden until a scene script
reveals it.
"""

import bpy
import math
import os
from mathutils import Vector

OUTPUT_DIR = "../../../assets/3d/locales"
OUTPUT_NAME = "diner.glb"

# ────────────────────────────────────────────────────────────────
# DINER FOOTPRINT
# ────────────────────────────────────────────────────────────────

# The diner is a single open dining room, roughly 18m × 12m × 3.4m.
# +X is east (parking-lot side · sodium light). -X is west (river side · cold blue).
# +Y is north (back hallway). -Y is south (front porch / parking entrance).
D_W = 18.0   # east-west
D_D = 12.0   # north-south
D_H = 3.4    # ceiling height

# the back hallway (a small corridor at +Y end, containing payphone + bathroom + card wall)
HALL_W = 5.0   # east-west span of the hallway
HALL_D = 2.4   # north-south depth of the hallway (extends BEYOND the main room)

# ────────────────────────────────────────────────────────────────
# PALETTE · per-face MATERIAL identifier (no baked lighting)
# ────────────────────────────────────────────────────────────────
# These are FLAT diffuse base colors. The Godot scene's lights
# will bring them to life dynamically.

COL_FLOOR_TILE     = (0.78, 0.74, 0.62, 1.0)   # diner-tile cream
COL_WALL_INTERIOR  = (0.85, 0.82, 0.70, 1.0)   # white-going-cream
COL_WALL_EXTERIOR  = (0.82, 0.78, 0.66, 1.0)   # white clapboard
COL_CEILING        = (0.70, 0.66, 0.56, 1.0)   # ceiling-tile
COL_FORMICA        = (0.88, 0.84, 0.72, 1.0)   # counter surface
COL_VINYL_RED      = (0.62, 0.18, 0.16, 1.0)   # booth vinyl
COL_VINYL_RED_DK   = (0.45, 0.14, 0.12, 1.0)   # booth shadow
COL_WOOD_TRIM      = (0.42, 0.28, 0.18, 1.0)   # booth wood
COL_BRASS          = (0.78, 0.58, 0.26, 1.0)   # brass railing
COL_BAR_WOOD       = (0.32, 0.22, 0.14, 1.0)   # closed cocktail bar
COL_KITCHEN_STEEL  = (0.62, 0.62, 0.60, 1.0)   # stainless
COL_KITCHEN_TILE   = (0.86, 0.84, 0.76, 1.0)   # kitchen wall tile
COL_RIVER_GLASS    = (0.30, 0.45, 0.60, 1.0)   # river-window blue (the glass itself, before light)
COL_PARKING_GLASS  = (0.50, 0.46, 0.30, 1.0)   # parking-lot window (sodium tint baked in)
COL_PAYPHONE_DARK  = (0.18, 0.16, 0.14, 1.0)   # payphone body
COL_CARDWALL       = (0.62, 0.55, 0.40, 1.0)   # corkboard backing
COL_CARD_PAPER     = (0.86, 0.80, 0.66, 1.0)   # pinned cards
COL_CARD_PINK      = (0.85, 0.55, 0.55, 1.0)   # one pink card
COL_CARD_GREEN     = (0.55, 0.70, 0.45, 1.0)   # one green card
COL_PRECIPICE_DOOR = (0.18, 0.14, 0.10, 1.0)   # the too-tall narrow door
COL_FLOOR_TILE_DK  = (0.30, 0.26, 0.18, 1.0)   # diner-tile dark check
COL_CLOCK_FACE     = (0.96, 0.92, 0.84, 1.0)   # white clock face
COL_PIE_CASE_GLASS = (0.78, 0.84, 0.86, 1.0)   # pie display glass
COL_REGISTER       = (0.40, 0.32, 0.22, 1.0)   # cash register brown
COL_PIE_FILLING    = (0.74, 0.36, 0.22, 1.0)   # cherry / pumpkin
COL_PIE_CRUST      = (0.86, 0.74, 0.50, 1.0)
COL_FAN_BLADE      = (0.86, 0.82, 0.74, 1.0)
COL_FAN_HOUSING    = (0.32, 0.28, 0.22, 1.0)
COL_SALT           = (0.96, 0.94, 0.88, 1.0)
COL_PEPPER         = (0.18, 0.16, 0.14, 1.0)
COL_NAPKIN         = (0.94, 0.92, 0.86, 1.0)
COL_PHOTO_FRAME    = (0.30, 0.22, 0.16, 1.0)

# ────────────────────────────────────────────────────────────────
# HELPERS
# ────────────────────────────────────────────────────────────────

def clear_scene():
    bpy.ops.object.select_all(action='SELECT')
    bpy.ops.object.delete(use_global=False)
    for c in (bpy.data.meshes, bpy.data.materials, bpy.data.images):
        for item in list(c):
            if item.users == 0:
                c.remove(item)


def make_box(name, center, size, base_color, open_faces=None):
    """Build a box mesh with FLAT per-face vertex colors (the base_color, no lighting bake).
    The Godot runtime lighting will shade these."""
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
        out_colors.append(base_color)   # NO baked light — flat
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


# ────────────────────────────────────────────────────────────────
# BUILD STEPS
# ────────────────────────────────────────────────────────────────

def build_shell():
    """Floor, ceiling, four walls (with window cutouts faked by sub-walls)."""
    # floor
    make_box("Floor", (0, 0, -0.05), (D_W, D_D, 0.10), COL_FLOOR_TILE, open_faces={'-Z'})
    # ceiling
    make_box("Ceiling", (0, 0, D_H + 0.05), (D_W, D_D, 0.10), COL_CEILING, open_faces={'+Z'})

    # WEST wall (river side) — has the big river window
    win_w = 8.0
    win_h = 2.0
    win_base = 0.9
    # lower below window
    make_box("Wall_W_lower", (-D_W/2 - 0.05, 0, win_base/2), (0.10, D_D, win_base), COL_WALL_INTERIOR)
    # upper above window
    upper_h = D_H - (win_base + win_h)
    make_box("Wall_W_upper", (-D_W/2 - 0.05, 0, win_base + win_h + upper_h/2), (0.10, D_D, upper_h), COL_WALL_INTERIOR)
    # narrow sides of the window
    side_d = (D_D - win_w) / 2
    make_box("Wall_W_S_of_window", (-D_W/2 - 0.05, -D_D/2 + side_d/2, win_base + win_h/2), (0.10, side_d, win_h), COL_WALL_INTERIOR)
    make_box("Wall_W_N_of_window", (-D_W/2 - 0.05, D_D/2 - side_d/2, win_base + win_h/2), (0.10, side_d, win_h), COL_WALL_INTERIOR)
    # the river-window glass (thin slab in the opening)
    make_box("RiverWindow_Glass", (-D_W/2 - 0.04, 0, win_base + win_h/2), (0.02, win_w, win_h), COL_RIVER_GLASS)

    # EAST wall (parking-lot side) — has the front door and parking-lot windows
    door_w = 1.4
    door_h = 2.2
    # the wall has a door near center-south and a long window strip above
    # south of door
    make_box("Wall_E_S_of_door", (D_W/2 + 0.05, -D_D/2 + (D_D/2 - door_w/2 - 0.6)/2 - 0.3,  door_h/2), (0.10, D_D/2 - door_w/2 - 0.3, door_h), COL_WALL_INTERIOR)
    # north of door, lower
    make_box("Wall_E_N_of_door_lower", (D_W/2 + 0.05, door_w/2 + 0.3 + (D_D/2 - door_w/2 - 0.3)/2, door_h/2), (0.10, D_D/2 - door_w/2 - 0.3, door_h), COL_WALL_INTERIOR)
    # above the door
    make_box("Wall_E_above_door", (D_W/2 + 0.05, 0, door_h + (D_H - door_h)/2), (0.10, D_D, D_H - door_h), COL_WALL_INTERIOR)
    # the parking-lot window strip (long horizontal at upper-mid height)
    make_box("ParkingWindow_Glass", (D_W/2 + 0.04, 0, 2.4), (0.02, D_D * 0.7, 0.6), COL_PARKING_GLASS)

    # NORTH wall — has the back-hallway opening (left open)
    hall_opening_x_center = 0
    make_box("Wall_N_E_of_hall", (D_W/2 * 0.65, D_D/2 + 0.05, D_H/2), (D_W - HALL_W, 0.10, D_H), COL_WALL_INTERIOR)
    make_box("Wall_N_above_hall", (0, D_D/2 + 0.05, D_H - 0.5), (HALL_W, 0.10, 1.0), COL_WALL_INTERIOR)

    # SOUTH wall — has the front porch / parking-lot side
    make_box("Wall_S", (0, -D_D/2 - 0.05, D_H/2), (D_W, 0.10, D_H), COL_WALL_INTERIOR)


def build_counter():
    """The counter at center. Long horizontal formica surface with stools and a back-bar."""
    # main counter (runs east-west across the room, centered)
    cy = 0.5
    make_box("Counter_Top", (0, cy, 1.05), (8.0, 0.8, 0.06), COL_FORMICA)
    # counter front (the visible side toward the south — vinyl-faced)
    make_box("Counter_Front", (0, cy - 0.4, 0.50), (8.0, 0.05, 1.00), COL_WOOD_TRIM)
    # counter brass foot-rail
    make_box("Counter_Brass_Rail", (0, cy - 0.42, 0.18), (8.0, 0.04, 0.04), COL_BRASS)
    # six stools in front of the counter
    for i in range(6):
        sx = -3.5 + i * 1.4
        # stool base
        make_box(f"Stool_{i}_base", (sx, cy - 0.85, 0.35), (0.30, 0.30, 0.70), COL_BRASS)
        # stool top (vinyl)
        make_box(f"Stool_{i}_top", (sx, cy - 0.85, 0.72), (0.36, 0.36, 0.06), COL_VINYL_RED)

    # back bar (a low backsplash + shelf behind the counter)
    make_box("BackBar_Shelf", (0, cy + 0.45, 1.10), (7.8, 0.30, 0.04), COL_WOOD_TRIM)
    # the coffee maker on the back bar
    make_box("CoffeeMaker", (-2.0, cy + 0.50, 1.30), (0.50, 0.40, 0.40), COL_KITCHEN_STEEL)
    # the call bell on the counter near the kitchen side
    make_box("CallBell", (-3.0, cy, 1.12), (0.10, 0.10, 0.08), COL_BRASS)


def build_booths():
    """Vinyl booths along the windows. Six booths total: four against the +X wall, two against the -X wall.

    Realistic diner proportions:
        seat        · 0.55m deep · 0.42m tall (seat top at 0.42m above floor)
        backrest    · 0.10m deep · 0.55m tall (top at 0.97m — about chest height seated)
        table top   · 0.04m thick at z=0.74m (slightly below standing belt height)
        2 booth     · 1.4m wide (room for two diners shoulder-to-shoulder)
    """
    def _booth(prefix: str, bx: float, by: float) -> None:
        # ── seats (two parallel benches facing each other) ──
        seat_top_z = 0.42
        seat_z = seat_top_z / 2.0   # center of the seat slab
        # south-side seat (facing north — diner sits facing the wall)
        make_box(f"{prefix}_seat_S", (bx, by - 0.50, seat_z), (1.4, 0.55, 0.42), COL_VINYL_RED)
        # north-side seat (facing south — diner sits facing the counter / aisle)
        make_box(f"{prefix}_seat_N", (bx, by + 0.50, seat_z), (1.4, 0.55, 0.42), COL_VINYL_RED)

        # ── backrests (thin tall slabs behind each seat) ──
        back_h = 0.55
        back_center_z = seat_top_z + back_h / 2.0   # backrest stacks on top of seat
        make_box(f"{prefix}_back_S", (bx, by - 0.77, back_center_z), (1.4, 0.06, back_h), COL_VINYL_RED_DK)
        make_box(f"{prefix}_back_N", (bx, by + 0.77, back_center_z), (1.4, 0.06, back_h), COL_VINYL_RED_DK)

        # ── table ──
        table_top_z = 0.74
        make_box(f"{prefix}_table", (bx, by, table_top_z), (1.10, 0.70, 0.04), COL_FORMICA)
        # narrow center post supporting the table
        make_box(f"{prefix}_post", (bx, by, table_top_z / 2.0), (0.06, 0.06, table_top_z), COL_BRASS)

        # ── hanging lamp above the table ──
        # lamp shade hangs ~50cm above the table top
        lamp_z = table_top_z + 0.50
        make_box(f"{prefix}_lamp", (bx, by, lamp_z), (0.18, 0.18, 0.10), (0.90, 0.75, 0.50, 1.0))
        # wire goes up from the lamp toward the ceiling
        wire_top_z = D_H - 0.05
        wire_center_z = (lamp_z + wire_top_z) / 2.0
        wire_len = wire_top_z - lamp_z
        make_box(f"{prefix}_lamp_wire", (bx, by, wire_center_z), (0.010, 0.010, wire_len), COL_PAYPHONE_DARK)

    # booths along east wall (parking-lot side) — booths 1, 2, 3, 4
    booth_east_y = [-4.0, -1.5, 1.5, 4.0]
    for i, by in enumerate(booth_east_y, start=1):
        bx = D_W/2 - 1.4   # interior side of the east wall
        _booth(f"Booth_{i}", bx, by)

    # booths along west wall (river side) — booth 5, 6
    booth_west_y = [-3.0, 2.5]
    for i, by in enumerate(booth_west_y, start=5):
        bx = -D_W/2 + 1.4
        _booth(f"Booth_{i}", bx, by)


def build_kitchen_alcove():
    """The kitchen alcove on the west (river) side. Stainless prep surfaces + grill + order window."""
    kx = -D_W/2 + 1.5
    ky = -D_D/2 + 1.2
    # the alcove footprint (a raised tile floor)
    make_box("Kitchen_Floor", (kx + 1.5, ky - 0.4, 0.02), (3.0, 1.6, 0.04), COL_KITCHEN_TILE)
    # grill (a long stainless surface)
    make_box("Kitchen_Grill", (kx + 1.5, ky, 0.80), (2.6, 0.7, 0.20), COL_KITCHEN_STEEL)
    # prep table
    make_box("Kitchen_Prep", (kx + 1.5, ky - 1.0, 0.85), (2.6, 0.6, 0.06), COL_KITCHEN_STEEL)
    # the back wall (interior) — kitchen tile
    make_box("Kitchen_Backwall", (kx + 1.5, ky + 0.40, 1.50), (3.0, 0.05, 1.80), COL_KITCHEN_TILE)
    # order window (a cutout in the south side — faked as a darker rectangle on the back wall)
    make_box("Kitchen_OrderWindow", (kx + 1.5, ky + 0.38, 1.70), (1.0, 0.02, 0.50), (0.20, 0.18, 0.14, 1.0))


def build_cocktail_bar():
    """The closed cocktail bar on the east (parking-lot) side. Wooden bar surface, stools turned upside down."""
    bx = D_W/2 - 1.5
    by = -D_D/2 + 1.5
    # the bar itself (longer than the counter, but un-served)
    make_box("CocktailBar_Top", (bx, by, 1.10), (0.7, 4.0, 0.08), COL_BAR_WOOD)
    # the back-bar shelving (a low cabinet against the wall)
    make_box("CocktailBar_BackShelf", (bx + 0.4, by, 1.40), (0.05, 4.0, 1.20), COL_BAR_WOOD)
    # bar stools (upturned — visible legs)
    for i in range(4):
        sy = by - 1.6 + i * 1.0
        make_box(f"CocktailBar_Stool_{i}", (bx - 0.5, sy, 1.20), (0.3, 0.3, 0.40), COL_BAR_WOOD)
        # the seat (now on top because upturned)
        make_box(f"CocktailBar_Stool_{i}_seat", (bx - 0.5, sy, 1.50), (0.35, 0.35, 0.04), COL_VINYL_RED)


def build_back_hallway():
    """The back hallway extending +Y from the main room. Contains payphone + bathroom door + card wall."""
    hx_center = 0
    hy_center = D_D/2 + HALL_D/2
    # floor extension
    make_box("Hall_Floor", (hx_center, hy_center, -0.05), (HALL_W, HALL_D, 0.10), COL_FLOOR_TILE, open_faces={'-Z'})
    # ceiling extension
    make_box("Hall_Ceiling", (hx_center, hy_center, D_H + 0.05), (HALL_W, HALL_D, 0.10), COL_CEILING, open_faces={'+Z'})
    # walls — west, east, north (closed at the far end)
    make_box("Hall_Wall_W", (hx_center - HALL_W/2 - 0.05, hy_center, D_H/2), (0.10, HALL_D, D_H), COL_WALL_INTERIOR)
    make_box("Hall_Wall_E", (hx_center + HALL_W/2 + 0.05, hy_center, D_H/2), (0.10, HALL_D, D_H), COL_WALL_INTERIOR)
    make_box("Hall_Wall_N", (hx_center, hy_center + HALL_D/2 + 0.05, D_H/2), (HALL_W, 0.10, D_H), COL_WALL_INTERIOR)

    # payphone mounted on the east wall of the hallway
    py_x = HALL_W/2 - 0.18
    py_y = hy_center - 0.6
    make_box("Payphone_Body", (py_x, py_y, 1.40), (0.12, 0.25, 0.50), COL_PAYPHONE_DARK)
    make_box("Payphone_Receiver", (py_x - 0.10, py_y - 0.12, 1.50), (0.08, 0.07, 0.18), COL_PAYPHONE_DARK)
    make_box("Payphone_Keypad", (py_x - 0.08, py_y, 1.40), (0.05, 0.10, 0.12), (0.48, 0.42, 0.32, 1.0))
    # phone-book chained below
    make_box("Payphone_Book", (py_x - 0.06, py_y, 0.95), (0.08, 0.20, 0.15), (0.62, 0.50, 0.32, 1.0))
    # the coiled cord
    for i in range(4):
        cy_off = -0.05 - i * 0.04
        cz = 1.30 - i * 0.05
        make_box(f"Payphone_Cord_{i}", (py_x - 0.10, py_y + cy_off, cz), (0.012, 0.022, 0.012), (0.10, 0.08, 0.06, 1.0))

    # bathroom door on the west wall of the hallway
    bd_x = -HALL_W/2 + 0.10
    bd_y = hy_center + 0.5
    make_box("Bathroom_Door", (bd_x, bd_y, 1.10), (0.05, 0.90, 2.10), COL_WOOD_TRIM)
    # bathroom door sign (a small darker rectangle)
    make_box("Bathroom_Sign", (bd_x - 0.03, bd_y, 1.95), (0.02, 0.15, 0.08), (0.20, 0.16, 0.10, 1.0))

    # the card wall — pinned cards on a corkboard panel on the north wall
    cw_x = hx_center
    cw_y = hy_center + HALL_D/2 - 0.04
    make_box("CardWall_Corkboard", (cw_x, cw_y, 1.50), (3.0, 0.02, 1.40), COL_CARDWALL)
    # individual cards pinned to the corkboard (a small grid of slightly varied colors and sizes)
    card_specs = [
        # (offset_x, offset_z, w, h, color)
        (-1.20,  0.40, 0.30, 0.40, COL_CARD_PAPER),
        (-0.85,  0.30, 0.25, 0.35, COL_CARD_PINK),
        (-0.45,  0.45, 0.32, 0.42, COL_CARD_PAPER),
        ( 0.00,  0.35, 0.40, 0.50, COL_CARD_GREEN),
        ( 0.50,  0.40, 0.28, 0.38, COL_CARD_PAPER),
        ( 0.90,  0.30, 0.30, 0.40, COL_CARD_PAPER),
        ( 1.20,  0.42, 0.24, 0.30, COL_CARD_PINK),
        (-1.10, -0.10, 0.34, 0.44, COL_CARD_PAPER),
        (-0.50, -0.05, 0.28, 0.36, COL_CARD_PAPER),
        ( 0.10, -0.10, 0.30, 0.40, COL_CARD_PAPER),
        ( 0.70, -0.15, 0.32, 0.42, COL_CARD_GREEN),
        ( 1.10,  0.00, 0.28, 0.36, COL_CARD_PAPER),
        (-0.80, -0.45, 0.30, 0.40, COL_CARD_PAPER),
        (-0.10, -0.50, 0.36, 0.46, COL_CARD_PINK),
        ( 0.50, -0.45, 0.30, 0.40, COL_CARD_PAPER),
    ]
    for i, (ox, oz, w, h, col) in enumerate(card_specs):
        make_box(f"CardWall_Card_{i}", (cw_x + ox, cw_y - 0.012, 1.50 + oz), (w, 0.002, h), col)

    # ── THE PRECIPICE DOOR ──
    # A too-tall narrow door that doesn't match the trim. Placed at
    # the far end of the hallway (north wall), positioned and sized
    # deliberately wrong. Trim color doesn't match the rest.
    # Reveal-able by scene script — exported by default but Godot
    # can hide the node until the scene triggers it.
    pd_x = hx_center + 1.20
    pd_y = hy_center + HALL_D/2 - 0.04
    pd_h = 2.85   # too tall
    pd_w = 0.65   # too narrow
    make_box("Precipice_Door", (pd_x, pd_y - 0.01, pd_h/2), (pd_w, 0.04, pd_h), COL_PRECIPICE_DOOR)
    # the frame (slightly off-shade)
    frame_color = (0.32, 0.20, 0.12, 1.0)
    make_box("Precipice_Door_Frame_L", (pd_x - pd_w/2 - 0.03, pd_y - 0.01, pd_h/2), (0.06, 0.05, pd_h), frame_color)
    make_box("Precipice_Door_Frame_R", (pd_x + pd_w/2 + 0.03, pd_y - 0.01, pd_h/2), (0.06, 0.05, pd_h), frame_color)
    make_box("Precipice_Door_Frame_T", (pd_x, pd_y - 0.01, pd_h + 0.03), (pd_w + 0.12, 0.05, 0.06), frame_color)


def build_floor_checkerboard():
    """Dark-tile squares laid over the cream floor in a checkerboard
    pattern. Adds the canonical 1950s-diner read at eye-level when
    the player looks down."""
    tile = 0.6
    z = 0.04
    nx = int(D_W / tile)
    ny = int(D_D / tile)
    for i in range(nx):
        for j in range(ny):
            if (i + j) % 2 != 0:
                continue
            cx = -D_W/2 + (i + 0.5) * tile
            cy = -D_D/2 + (j + 0.5) * tile
            make_box(
                f"FloorTile_{i}_{j}",
                center=(cx, cy, z),
                size=(tile * 0.92, tile * 0.92, 0.02),
                base_color=COL_FLOOR_TILE_DK,
            )


def build_ceiling_fans():
    """Two slow industrial ceiling fans — housing + 4 blades each."""
    fan_z = D_H - 0.30
    for label, (fx, fy) in [
        ("N", (-3.0, 0.5)),
        ("S", (+3.0, 0.5)),
    ]:
        # Mounting plate
        make_box(
            f"Fan_{label}_Mount",
            center=(fx, fy, D_H - 0.10),
            size=(0.50, 0.50, 0.15), base_color=COL_FAN_HOUSING)
        # Motor housing
        make_box(
            f"Fan_{label}_Housing",
            center=(fx, fy, fan_z - 0.10),
            size=(0.40, 0.40, 0.20), base_color=COL_FAN_HOUSING)
        # 4 blades + counter-cross pair
        for b in range(4):
            ang = b * 1.5708    # 90° steps
            import math as _m
            cx = fx + 0.4 * _m.cos(ang)
            cy = fy + 0.4 * _m.sin(ang)
            if b % 2 == 0:
                size = (0.80, 0.18, 0.04)
            else:
                size = (0.18, 0.80, 0.04)
            make_box(
                f"Fan_{label}_Blade_{b}",
                center=(cx, cy, fan_z - 0.18),
                size=size, base_color=COL_FAN_BLADE)
        # Light fixture below the fan
        make_box(
            f"Fan_{label}_GlobeMount",
            center=(fx, fy, fan_z - 0.32),
            size=(0.18, 0.18, 0.08), base_color=COL_FAN_HOUSING)
        make_box(
            f"Fan_{label}_Globe",
            center=(fx, fy, fan_z - 0.50),
            size=(0.40, 0.40, 0.28),
            base_color=(0.96, 0.92, 0.78, 1.0))


def build_counter_accessories():
    """Pie case + cash register + ticket spike + sugar caddies on
    the counter. These are eye-level reads."""
    cy = 0.5    # counter Y (matches build_counter)
    counter_top_z = 1.10
    # Pie display case — glass dome + 2 visible pies + base
    pcx = +2.6
    make_box("PieCase_Base", (pcx, cy + 0.10, counter_top_z + 0.04),
             (0.80, 0.50, 0.08), COL_FORMICA)
    # Glass dome (a single tall box with light glass color)
    make_box("PieCase_Glass", (pcx, cy + 0.10, counter_top_z + 0.45),
             (0.78, 0.48, 0.70), COL_PIE_CASE_GLASS)
    # Pies inside (two visible)
    make_box("Pie_Cherry", (pcx - 0.20, cy + 0.10, counter_top_z + 0.16),
             (0.24, 0.24, 0.08), COL_PIE_FILLING)
    make_box("Pie_Cherry_Crust",
             (pcx - 0.20, cy + 0.10, counter_top_z + 0.18),
             (0.26, 0.26, 0.04), COL_PIE_CRUST)
    make_box("Pie_Apple", (pcx + 0.18, cy + 0.10, counter_top_z + 0.16),
             (0.24, 0.24, 0.08), COL_PIE_CRUST)
    # Cash register at the south end (entry side)
    rcx = -3.6
    make_box("Register_Body",
             (rcx, cy, counter_top_z + 0.18),
             (0.55, 0.45, 0.32), COL_REGISTER)
    make_box("Register_Drawer",
             (rcx, cy - 0.15, counter_top_z + 0.06),
             (0.55, 0.20, 0.12), (0.32, 0.26, 0.18, 1.0))
    make_box("Register_Top",
             (rcx, cy, counter_top_z + 0.36),
             (0.42, 0.32, 0.06), (0.20, 0.16, 0.12, 1.0))
    # Ticket spike (thin tall iron spike + a few papers)
    make_box("TicketSpike_Base",
             (-1.5, cy + 0.30, counter_top_z + 0.04),
             (0.08, 0.08, 0.08), COL_BRASS)
    make_box("TicketSpike_Rod",
             (-1.5, cy + 0.30, counter_top_z + 0.18),
             (0.02, 0.02, 0.20), (0.10, 0.10, 0.10, 1.0))
    # 3 sugar caddies along the counter
    for i in range(3):
        scx = -2.5 + i * 2.5
        make_box(f"SugarCaddy_{i}",
                 (scx, cy - 0.05, counter_top_z + 0.07),
                 (0.10, 0.10, 0.10), COL_KITCHEN_STEEL)
        make_box(f"SugarCaddyTop_{i}",
                 (scx, cy - 0.05, counter_top_z + 0.13),
                 (0.06, 0.06, 0.02), COL_BRASS)


def build_table_dressings():
    """Salt + pepper + napkin dispenser on each booth table.
    Booths are along the +X (east) wall and -X (west) wall."""
    # The booths in build_booths are positioned at:
    # East wall (+X): 4 booths
    # West wall (-X): 2 booths
    # Each booth table is at the booth center between two benches.
    # We don't have direct access to the booth coords from the builder
    # so we re-derive (this matches the placement in build_booths).
    east_xs = [3.0, 5.0, 7.0, 9.0]    # 4 east booths
    west_xs = [-3.0, -5.0]            # 2 west booths
    booths = [(x, +4.5) for x in east_xs] + [(x, -4.5) for x in west_xs]
    for i, (bx, by) in enumerate(booths):
        # Salt shaker (cream/white)
        make_box(f"Salt_{i}",
                 (bx + 0.18, by, 1.10),
                 (0.08, 0.08, 0.14), COL_SALT)
        make_box(f"Salt_Cap_{i}",
                 (bx + 0.18, by, 1.18),
                 (0.06, 0.06, 0.03), COL_BRASS)
        # Pepper shaker (dark)
        make_box(f"Pepper_{i}",
                 (bx - 0.18, by, 1.10),
                 (0.08, 0.08, 0.14), COL_PEPPER)
        make_box(f"Pepper_Cap_{i}",
                 (bx - 0.18, by, 1.18),
                 (0.06, 0.06, 0.03), COL_BRASS)
        # Napkin dispenser (chunky horizontal box)
        make_box(f"NapkinDispenser_{i}",
                 (bx, by - 0.18, 1.10),
                 (0.20, 0.10, 0.16), COL_KITCHEN_STEEL)
        # Napkins peeking out (cream slab)
        make_box(f"Napkins_{i}",
                 (bx, by - 0.18, 1.12),
                 (0.18, 0.04, 0.12), COL_NAPKIN)


def build_wall_decor():
    """Wall clock + framed photos + neon sign. Things players see
    looking AT the walls while walking around."""
    # Wall clock on the north wall (above the kitchen alcove)
    make_box("WallClock_Frame",
             (0, D_D/2 - 0.15, D_H - 0.80),
             (0.80, 0.10, 0.80), COL_PHOTO_FRAME)
    make_box("WallClock_Face",
             (0, D_D/2 - 0.21, D_H - 0.80),
             (0.66, 0.05, 0.66), COL_CLOCK_FACE)
    # Clock hands (two thin dark strips, suggested time ~3:47 AM)
    make_box("WallClock_HourHand",
             (0, D_D/2 - 0.24, D_H - 0.82),
             (0.08, 0.02, 0.18), (0.18, 0.16, 0.14, 1.0))
    make_box("WallClock_MinuteHand",
             (0, D_D/2 - 0.24, D_H - 0.74),
             (0.04, 0.02, 0.30), (0.18, 0.16, 0.14, 1.0))
    # 4 framed photos along the east wall (booth side)
    for i in range(4):
        fy = -3.5 + i * 2.3
        # Frame
        make_box(f"WallPhoto_Frame_{i}",
                 (D_W/2 - 0.08, fy, 2.20),
                 (0.05, 0.50, 0.60), COL_PHOTO_FRAME)
        # Photo (cream rectangle inside)
        make_box(f"WallPhoto_Image_{i}",
                 (D_W/2 - 0.12, fy, 2.20),
                 (0.02, 0.40, 0.50), COL_NAPKIN)
    # Neon "OPEN" sign in the front window (south, parking-lot side)
    make_box("NeonOpenSign",
             (-2.2, D_D/2 - 0.10, 2.20),
             (1.20, 0.06, 0.50), (0.95, 0.32, 0.62, 1.0))


def build_entry_props():
    """Coat rack + hostess stand near the parking-lot entry."""
    # Hostess podium at the south-east corner near the door
    px, py = D_W/2 - 2.0, D_D/2 - 1.5
    make_box("HostessStand_Base", (px, py, 0.60),
             (0.60, 0.40, 1.20), COL_WOOD_TRIM)
    make_box("HostessStand_Top", (px, py, 1.24),
             (0.65, 0.45, 0.08), (0.50, 0.36, 0.22, 1.0))
    make_box("Menus_Stack", (px + 0.10, py - 0.10, 1.30),
             (0.20, 0.12, 0.10), COL_VINYL_RED)
    # Coat rack to the right of the entrance
    cr_x, cr_y = D_W/2 - 0.6, D_D/2 - 0.6
    make_box("CoatRack_Pole", (cr_x, cr_y, 0.95),
             (0.06, 0.06, 1.90), COL_WOOD_TRIM)
    make_box("CoatRack_Base", (cr_x, cr_y, 0.03),
             (0.50, 0.50, 0.06), COL_WOOD_TRIM)
    # Hooks (suggestive — small crossbars near the top)
    for h in range(4):
        ang = h * 1.5708
        import math as _m
        hx = cr_x + 0.20 * _m.cos(ang)
        hy = cr_y + 0.20 * _m.sin(ang)
        make_box(f"CoatHook_{h}", (hx, hy, 1.78),
                 (0.04, 0.04, 0.12), COL_BRASS)
    # A draped jacket on one of the hooks
    make_box("Jacket_Draped",
             (cr_x + 0.18, cr_y, 1.40),
             (0.22, 0.06, 0.50), (0.32, 0.40, 0.52, 1.0))


def build_exterior_hints():
    """Small exterior cues — the wraparound porch over the water, sodium pole hint."""
    # porch deck on the west (river) side, extending out
    porch_y_center = 0
    make_box("Porch_Deck", (-D_W/2 - 1.0, porch_y_center, 0.0), (2.0, D_D, 0.08), (0.40, 0.30, 0.18, 1.0))
    # porch railing brass
    make_box("Porch_Rail", (-D_W/2 - 2.0, porch_y_center, 0.85), (0.05, D_D, 0.05), COL_BRASS)

    # sodium streetlight pole on the east (parking lot) side, suggested
    make_box("Sodium_Pole", (D_W/2 + 2.5, -D_D/2 - 1.0, 3.0), (0.10, 0.10, 6.0), (0.20, 0.18, 0.14, 1.0))
    # sodium fixture at top
    make_box("Sodium_Fixture", (D_W/2 + 2.5, -D_D/2 - 1.0, 5.8), (0.45, 0.30, 0.20), (0.85, 0.65, 0.30, 1.0))


# ────────────────────────────────────────────────────────────────
# CAMERA MARKERS (exported as Blender cameras; Godot reads them as Camera3D nodes)
# ────────────────────────────────────────────────────────────────

def add_camera(name, location, rotation_euler, lens=35.0):
    cam_data = bpy.data.cameras.new(name=name)
    cam_data.lens = lens
    cam = bpy.data.objects.new(name, cam_data)
    cam.location = location
    cam.rotation_euler = rotation_euler
    bpy.context.collection.objects.link(cam)


def add_camera_markers():
    # player_entry — at the front door, looking in
    add_camera("cam_player_entry", (D_W/2 - 1.5, -3.0, 1.65), (math.radians(82), 0, math.radians(180)))
    # wide — establishing shot from a corner
    add_camera("cam_wide", (D_W/2 - 0.5, -D_D/2 + 0.5, 2.40), (math.radians(70), 0, math.radians(225)))
    # close_counter — at the counter, looking at the back bar
    add_camera("cam_close_counter", (-1.5, -0.3, 1.50), (math.radians(80), 0, math.radians(0)))
    # close_booth_6 — looking at booth 6 (the canonical booth)
    add_camera("cam_close_booth_6", (-D_W/2 + 2.5, 2.5, 1.40), (math.radians(85), 0, math.radians(-90)))
    # close_payphone — in the back hallway at the payphone
    add_camera("cam_close_payphone", (HALL_W/2 - 1.0, D_D/2 + 0.5, 1.45),
               (math.radians(80), 0, math.radians(-90)))
    # close_cardwall — looking at the corkboard
    add_camera("cam_close_cardwall", (0, D_D/2 + HALL_D - 0.6, 1.55),
               (math.radians(85), 0, math.radians(0)))
    # close_precipice — looking at the precipice door (used when revealed)
    add_camera("cam_close_precipice", (1.2, D_D/2 + HALL_D - 0.8, 1.50),
               (math.radians(80), 0, math.radians(0)))
    # river_window — looking out at the river
    add_camera("cam_river_window", (-D_W/2 + 1.0, 0, 1.80),
               (math.radians(85), 0, math.radians(-90)))


# ────────────────────────────────────────────────────────────────
# EXPORT
# ────────────────────────────────────────────────────────────────

def export_glb():
    out_dir = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), OUTPUT_DIR))
    os.makedirs(out_dir, exist_ok=True)
    out_path = os.path.join(out_dir, OUTPUT_NAME)

    print(f"\n[build_diner] exporting to {out_path}")
    print(f"[build_diner] scene objects: {len(bpy.context.scene.objects)}")

    bpy.ops.object.select_all(action='SELECT')
    base = {
        'filepath': out_path, 'export_format': 'GLB',
        'use_selection': False, 'export_apply': True,
        'export_lights': True, 'export_cameras': False,   # was True; hijacks Godot's active camera
    }
    rna = bpy.ops.export_scene.gltf.get_rna_type()
    legacy = {}
    if 'export_colors' in rna.properties: legacy['export_colors'] = True
    if 'export_normals' in rna.properties: legacy['export_normals'] = True

    try:
        result = bpy.ops.export_scene.gltf(**base, **legacy)
        print(f"[build_diner] export result: {result}")
    except Exception as e:
        print(f"[build_diner] ✗ EXPORT FAILED: {e}")
        import traceback; traceback.print_exc()
        raise

    if os.path.exists(out_path):
        size = os.path.getsize(out_path)
        print(f"[build_diner] ✓ wrote {out_path} ({size} bytes)")
    else:
        raise RuntimeError("GLB not written")


def main():
    clear_scene()
    build_shell()
    build_floor_checkerboard()
    build_counter()
    build_counter_accessories()
    build_booths()
    build_table_dressings()
    build_kitchen_alcove()
    build_cocktail_bar()
    build_back_hallway()
    build_ceiling_fans()
    build_wall_decor()
    build_entry_props()
    build_exterior_hints()
    # Camera markers intentionally NOT added — same issue as the
    # Cathedral build had with FrasierEye hijacking the active
    # camera. Will re-introduce as named cinematic markers once
    # the framing system is wired up properly via Godot Node3D
    # markers instead of camera nodes.
    # add_camera_markers()  # DISABLED
    export_glb()


if __name__ == "__main__":
    main()
