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
    """The counter runs E-W just NORTH of the kitchen alcove, parallel
    to its order-window face. Stools face NORTH (into the room) so
    the player walking past the counter sees seated patrons + cook
    through the order window behind. Back-bar is BEHIND the counter
    (south side, against kitchen wall)."""
    # Counter center at Y=-3.5 (kitchen back-wall at Y=-4.4, so the
    # counter is a 0.8m strip with its south edge ~0.5m from kitchen)
    cy = -3.5
    counter_top_z = 1.05
    # Main counter — runs from X=-7 to +3 (10m long)
    make_box("Counter_Top", (-2.0, cy, counter_top_z),
             (10.0, 0.8, 0.06), COL_FORMICA)
    # Front of counter (NORTH side — customer-facing, vinyl) —
    # this is the side stools sit against
    make_box("Counter_Front", (-2.0, cy + 0.40, 0.50),
             (10.0, 0.05, 1.00), COL_WOOD_TRIM)
    # Brass foot rail along the customer (north) side — round cylinder
    make_cyl("Counter_Brass_Rail", (-2.0, cy + 0.42, 0.18),
             0.024, 10.0, COL_BRASS, segments=8, axis='X')
    # Brass rail bracket caps at each end
    for end_sgn in (-1, +1):
        make_cyl(f"Counter_Brass_Rail_Cap_{end_sgn:+d}",
                 (-2.0 + end_sgn * 5.0, cy + 0.42, 0.18),
                 0.040, 0.10, COL_BRASS, segments=8, axis='X')
    # Back of counter (SOUTH side — the cook side, faces kitchen)
    make_box("Counter_Back", (-2.0, cy - 0.40, 0.50),
             (10.0, 0.05, 1.00), COL_BAR_WOOD)
    # 8 counter stools in front of the counter (north side)
    # — chrome post + foot ring + round vinyl seat (cylinder)
    n_stools = 8
    for i in range(n_stools):
        sx = -6.5 + i * (12.0 / (n_stools + 1)) * 0.85
        sy = cy + 0.85
        # Stool post (chrome cylinder)
        make_cyl(f"Stool_{i}_post", (sx, sy, 0.36),
                 0.04, 0.70, COL_BRASS, segments=6, axis='Z')
        # Foot ring (cylinder, broader)
        make_cyl(f"Stool_{i}_foot_ring", (sx, sy, 0.20),
                 0.16, 0.025, COL_BRASS, segments=8, axis='Z')
        # Round vinyl seat (low disc cylinder)
        make_cyl(f"Stool_{i}_seat", (sx, sy, 0.72),
                 0.20, 0.06, COL_VINYL_RED, segments=12, axis='Z')
        # Cushion crown (slightly smaller, slightly above)
        make_cyl(f"Stool_{i}_seat_crown", (sx, sy, 0.76),
                 0.17, 0.025, COL_VINYL_RED_DK, segments=12, axis='Z')
    # Back-bar shelving — runs BEHIND the counter on the kitchen
    # side, against the kitchen back-wall (Y=-4.4)
    make_box("BackBar_LowShelf", (-2.0, cy - 0.55, 1.10),
             (10.0, 0.30, 0.04), COL_WOOD_TRIM)
    make_box("BackBar_HighShelf", (-2.0, cy - 0.55, 1.80),
             (10.0, 0.30, 0.04), COL_WOOD_TRIM)
    # Pass-through gap framing (where the cook hands plates out
    # through the order window — top of counter near west end)
    make_box("PassThrough_Frame", (-5.5, cy - 0.42, 1.85),
             (3.0, 0.04, 0.06), COL_WOOD_TRIM)
    # Coffee maker on the back bar
    make_box("CoffeeMaker", (+1.5, cy - 0.55, 1.34),
             (0.50, 0.40, 0.40), COL_KITCHEN_STEEL)
    make_box("CoffeeMaker_Pot",
             (+1.5, cy - 0.55, 1.20),
             (0.18, 0.18, 0.20),
             (0.30, 0.18, 0.10, 1.0))
    # Toaster on the back bar
    make_box("Toaster", (+2.5, cy - 0.55, 1.30),
             (0.36, 0.22, 0.20), COL_KITCHEN_STEEL)
    # Two-tier glass dessert / cake stand
    make_box("DessertStand_Base", (-3.5, cy - 0.55, 1.16),
             (0.40, 0.30, 0.06), COL_KITCHEN_STEEL)
    make_box("DessertStand_Dome", (-3.5, cy - 0.55, 1.42),
             (0.36, 0.26, 0.46), COL_PIE_CASE_GLASS)
    # Soda fountain dispenser
    make_box("SodaFountain_Body", (-2.0, cy - 0.55, 1.38),
             (0.60, 0.32, 0.50), COL_KITCHEN_STEEL)
    for s in (-1, 0, +1):
        make_box(f"SodaFountain_Tap_{s:+d}",
                 (-2.0 + s * 0.18, cy - 0.40, 1.30),
                 (0.06, 0.06, 0.18), COL_BRASS)
    # The call bell on the counter (kitchen side)
    make_box("CallBell", (-4.5, cy, 1.12),
             (0.10, 0.10, 0.08), COL_BRASS)


BOOTH_POSITIONS = []   # (prefix, table_center_x, table_center_y) — filled by builders, used by build_table_dressings


# ── booth dimensions (a real diner-comfortable design) ──
# Bench: 1.50m wide × 0.48m deep × 0.45m tall.
# Backrest: 0.06m thick × 1.50m wide × 0.70m tall, top at z=1.15.
# Table: 0.85m × 0.65m × 0.04m, top at z=0.74.
# Leg gap (bench-front to bench-front): 0.65m.
# Total perpendicular footprint backrest-to-backrest: 1.73m.
SEAT_DEPTH    = 0.48
SEAT_WIDTH    = 1.50
SEAT_TOP_Z    = 0.45
BACK_H        = 0.70
BACK_THICK    = 0.06
TABLE_LEN     = 0.85    # along bench-axis
TABLE_DEPTH   = 0.65    # along leg-gap-axis (must fit inside leg gap)
TABLE_TOP_Z   = 0.74
LEG_GAP       = 0.65    # bench-front to bench-front
BOOTH_TOTAL   = BACK_THICK + SEAT_DEPTH + LEG_GAP + SEAT_DEPTH + BACK_THICK  # 1.73


def _build_booth_bench(prefix, side_label, center_x, center_y, axis_along, with_backrest):
    """One bench unit: seat + (optional) backrest + cushion seams + headrest crown.

    `axis_along`     : 'X' or 'Y' — direction the bench is LONG (matches its 1.50m dimension).
    `center_x/y`     : bench center on the floor plan.
    `with_backrest`  : True for booth's outer benches, False if this side faces a shared spine
                       (the spine has its own backrest pair).
    """
    seat_z = SEAT_TOP_Z / 2.0
    if axis_along == 'X':
        seat_size = (SEAT_WIDTH, SEAT_DEPTH, SEAT_TOP_Z)
    else:
        seat_size = (SEAT_DEPTH, SEAT_WIDTH, SEAT_TOP_Z)
    # Seat slab
    make_box(f"{prefix}_{side_label}_seat",
             (center_x, center_y, seat_z),
             seat_size, COL_VINYL_RED)
    # Cushion seam strip running along the seat front edge — suggests upholstered seam
    if axis_along == 'X':
        seam_off = (0.0, -SEAT_DEPTH / 2 + 0.06, 0.0)
        seam_size = (SEAT_WIDTH - 0.08, 0.04, 0.018)
    else:
        seam_off = (-SEAT_DEPTH / 2 + 0.06, 0.0, 0.0)
        seam_size = (0.04, SEAT_WIDTH - 0.08, 0.018)
    make_box(f"{prefix}_{side_label}_seat_seam",
             (center_x + seam_off[0], center_y + seam_off[1], SEAT_TOP_Z - 0.01),
             seam_size, COL_VINYL_RED_DK)
    # Tufted button rows — three small dimples along the seat
    for t in range(3):
        frac = -1 + t  # -1, 0, +1
        if axis_along == 'X':
            bx = center_x + frac * 0.40
            by = center_y
        else:
            bx = center_x
            by = center_y + frac * 0.40
        make_box(f"{prefix}_{side_label}_tuft_{t}",
                 (bx, by, SEAT_TOP_Z - 0.005),
                 (0.04, 0.04, 0.010), COL_VINYL_RED_DK)
    if not with_backrest:
        return
    # Backrest — taller for comfort
    back_offset = SEAT_DEPTH / 2 + BACK_THICK / 2
    if axis_along == 'X':
        back_pos_y_offset = back_offset
        back_size = (SEAT_WIDTH, BACK_THICK, BACK_H)
    else:
        back_pos_y_offset = 0.0
        back_size = (BACK_THICK, SEAT_WIDTH, BACK_H)
    # which side of the bench does the backrest sit on? side_label encodes that
    # Convention: side_label ends with the cardinal direction the bench's BACK FACE points.
    # 'S' → backrest is on the south side of bench (further -Y), bench faces +Y
    sign_map = {'N': +1, 'S': -1, 'E': +1, 'W': -1}
    back_side = side_label[-1]
    back_sign = sign_map[back_side]
    if axis_along == 'X':
        bx_off, by_off = 0.0, back_sign * back_offset
    else:
        bx_off, by_off = back_sign * back_offset, 0.0
    back_z = SEAT_TOP_Z + BACK_H / 2.0
    make_box(f"{prefix}_{side_label}_back",
             (center_x + bx_off, center_y + by_off, back_z),
             back_size, COL_VINYL_RED_DK)
    # Headrest crown — a slightly darker top piece, sticks 2cm proud
    if axis_along == 'X':
        crown_size = (SEAT_WIDTH + 0.04, BACK_THICK + 0.03, 0.05)
    else:
        crown_size = (BACK_THICK + 0.03, SEAT_WIDTH + 0.04, 0.05)
    make_box(f"{prefix}_{side_label}_crown",
             (center_x + bx_off, center_y + by_off, SEAT_TOP_Z + BACK_H + 0.025),
             crown_size, COL_WOOD_TRIM)
    # Vertical seam strips on the backrest (button-tuft column suggestion)
    for c in range(3):
        frac = -1 + c
        if axis_along == 'X':
            cx_off, cy_off = frac * 0.45, by_off - back_sign * (BACK_THICK / 2 + 0.005)
            stripe_size = (0.025, 0.012, BACK_H - 0.10)
        else:
            cx_off, cy_off = bx_off - back_sign * (BACK_THICK / 2 + 0.005), frac * 0.45
            stripe_size = (0.012, 0.025, BACK_H - 0.10)
        make_box(f"{prefix}_{side_label}_back_stripe_{c}",
                 (center_x + cx_off, center_y + cy_off, back_z),
                 stripe_size, COL_VINYL_RED)


def _build_booth_table(prefix, cx, cy, axis_along):
    """Center-post table with chrome edge band and table-number plaque.
    `axis_along` matches the bench long axis (so the table's long side
    is parallel to the benches)."""
    if axis_along == 'X':
        top_size = (TABLE_LEN, TABLE_DEPTH, 0.04)
    else:
        top_size = (TABLE_DEPTH, TABLE_LEN, 0.04)
    make_box(f"{prefix}_table_top", (cx, cy, TABLE_TOP_Z), top_size, COL_FORMICA)
    # Chrome edge band — slightly larger, slightly thinner, lower so it shows as the table's "rim"
    if axis_along == 'X':
        band_size = (TABLE_LEN + 0.02, TABLE_DEPTH + 0.02, 0.02)
    else:
        band_size = (TABLE_DEPTH + 0.02, TABLE_LEN + 0.02, 0.02)
    make_box(f"{prefix}_table_band",
             (cx, cy, TABLE_TOP_Z - 0.03), band_size, COL_BRASS)
    # Pedestal: chrome cylinder + cast-iron foot disc
    make_cyl(f"{prefix}_table_post",
             (cx, cy, TABLE_TOP_Z / 2),
             0.045, TABLE_TOP_Z - 0.04, COL_BRASS, segments=8, axis='Z')
    make_cyl(f"{prefix}_table_foot",
             (cx, cy, 0.03),
             0.22, 0.04, (0.16, 0.14, 0.12, 1.0), segments=10, axis='Z')
    # Pendant lamp above the table — chrome stem, enameled cone shade, warm bulb
    lamp_z = TABLE_TOP_Z + 0.70
    wire_top_z = D_H - 0.05
    make_cyl(f"{prefix}_lamp_stem",
             (cx, cy, (lamp_z + wire_top_z) / 2),
             0.012, wire_top_z - lamp_z, COL_PAYPHONE_DARK, segments=4, axis='Z')
    make_cyl(f"{prefix}_lamp_canopy",
             (cx, cy, wire_top_z - 0.02), 0.07, 0.04,
             COL_BRASS, segments=8, axis='Z')
    make_sphere_low(f"{prefix}_lamp_shade",
                    (cx, cy, lamp_z), 0.18,
                    (0.86, 0.62, 0.32, 1.0), rings=2, segments=8)
    make_sphere_low(f"{prefix}_lamp_bulb",
                    (cx, cy, lamp_z - 0.16), 0.05,
                    (0.96, 0.92, 0.74, 1.0), rings=2, segments=6)
    # Table-number plaque on the table surface (corner, away from the diners)
    if axis_along == 'X':
        plaque_off = (TABLE_LEN / 2 - 0.10, -TABLE_DEPTH / 2 + 0.10, 0.0)
    else:
        plaque_off = (-TABLE_DEPTH / 2 + 0.10, TABLE_LEN / 2 - 0.10, 0.0)
    make_box(f"{prefix}_table_number",
             (cx + plaque_off[0], cy + plaque_off[1], TABLE_TOP_Z + 0.022),
             (0.07, 0.07, 0.005), COL_BRASS)


def build_alcove_booths():
    """Classic American-diner alcove layout: a single row of booths
    along the river-window wall. Each booth is a tight alcove jutting
    OUT from the wall, with a tall divider between it and the next
    booth — so the dividers, not the benches, form the long shared
    line you see along the wall.

    Reference: classic diner reference photo provided by user
    (image 4d0884e1-5186.jpg). Photo features:
      · 4 booths in a row along a window wall
      · Each booth ≈ 1.2m wide × 1.7m deep
      · Square tables (~0.7m × 0.7m)
      · Tall divider walls between booths (~1.1m above floor)
      · Pendant lamp directly above each table
      · Bench backrest height ≈ chest-of-seated-customer
    """
    # Per-booth dimensions
    bench_w   = 1.20    # bench long-axis (along the wall)
    bench_d   = 0.48    # bench depth (perpendicular to wall)
    seat_top  = 0.45
    back_h    = 0.70    # top at z=1.15
    div_thick = 0.06
    table_sz  = 0.70    # square
    leg_gap   = 0.80    # bench-front to bench-front (just enough for legs + small table)

    # Per-booth total Y extent (booth + its right-side divider) is bench_w + div_thick = 1.26
    # 4 booths + 5 dividers = 4×1.20 + 5×0.06 = 5.10m. Center the row at Y=+0.50.
    n_booths = 4
    booth_unit_y = bench_w + div_thick
    total_y = n_booths * bench_w + (n_booths + 1) * div_thick
    row_center_y = +0.50
    row_y_start = row_center_y - total_y / 2.0

    # X positions (window at -9, depth grows toward +X)
    wall_x         = -D_W / 2                  # -9.0
    wall_back_x    = wall_x + 0.05 + div_thick / 2.0   # -8.92 (wall-side backrest center)
    wall_bench_x   = wall_back_x + div_thick / 2.0 + bench_d / 2.0  # -8.65
    table_x        = wall_bench_x + bench_d / 2.0 + leg_gap / 2.0   # -8.01
    aisle_bench_x  = table_x + leg_gap / 2.0 + bench_d / 2.0        # -7.37
    aisle_back_x   = aisle_bench_x + bench_d / 2.0 + div_thick / 2.0 # -7.10
    booth_depth_total = (aisle_back_x + div_thick / 2.0) - (wall_back_x - div_thick / 2.0)  # 1.88

    # ── End-dividers (the tall walls between adjacent booths) ──
    div_center_x = (wall_back_x + aisle_back_x) / 2.0
    div_top_z = seat_top + back_h           # 1.15
    for d in range(n_booths + 1):
        dy = row_y_start + d * (bench_w + div_thick) + div_thick / 2.0
        make_box(f"Alcove_Divider_{d}",
                 (div_center_x, dy, div_top_z / 2.0),
                 (booth_depth_total + 0.04, div_thick, div_top_z),
                 COL_VINYL_RED_DK)
        # Crown molding cap (a slightly darker wood band on top)
        make_box(f"Alcove_Divider_{d}_Crown",
                 (div_center_x, dy, div_top_z + 0.025),
                 (booth_depth_total + 0.06, div_thick + 0.04, 0.05),
                 COL_WOOD_TRIM)
        # Wood baseboard at the floor
        make_box(f"Alcove_Divider_{d}_Baseboard",
                 (div_center_x, dy, 0.05),
                 (booth_depth_total + 0.06, div_thick + 0.04, 0.10),
                 COL_WOOD_TRIM)

    # ── Per-booth benches + table + pendant ──
    for i in range(n_booths):
        # Booth's Y center
        by = row_y_start + (i + 0.5) * (bench_w + div_thick) + div_thick / 2.0
        prefix = f"Booth_{i + 1}"

        # ── Window-side bench (back to wall) ──
        # Seat slab
        make_box(f"{prefix}_seat_W",
                 (wall_bench_x, by, seat_top / 2.0),
                 (bench_d, bench_w, seat_top), COL_VINYL_RED)
        # Front seam piping on the aisle-facing edge
        make_box(f"{prefix}_seat_W_seam",
                 (wall_bench_x + bench_d / 2.0 - 0.04, by, seat_top - 0.012),
                 (0.04, bench_w - 0.08, 0.020), COL_VINYL_RED_DK)
        # Tufted button-dimples (3 across)
        for t in range(3):
            tx = wall_bench_x
            ty = by + (-1 + t) * 0.32
            make_box(f"{prefix}_seat_W_tuft_{t}",
                     (tx, ty, seat_top - 0.008),
                     (0.05, 0.05, 0.012), COL_VINYL_RED_DK)
        # Backrest pressed to the wall
        back_z = seat_top + back_h / 2.0
        make_box(f"{prefix}_back_W",
                 (wall_back_x, by, back_z),
                 (div_thick, bench_w, back_h), COL_VINYL_RED_DK)
        # Vertical stripes on backrest (tufted column hint)
        for c in range(3):
            sy = by + (-1 + c) * 0.36
            make_box(f"{prefix}_back_W_stripe_{c}",
                     (wall_back_x + div_thick / 2.0 + 0.005, sy, back_z),
                     (0.012, 0.025, back_h - 0.10), COL_VINYL_RED)

        # ── Aisle-side bench (back to aisle) ──
        make_box(f"{prefix}_seat_A",
                 (aisle_bench_x, by, seat_top / 2.0),
                 (bench_d, bench_w, seat_top), COL_VINYL_RED)
        make_box(f"{prefix}_seat_A_seam",
                 (aisle_bench_x - bench_d / 2.0 + 0.04, by, seat_top - 0.012),
                 (0.04, bench_w - 0.08, 0.020), COL_VINYL_RED_DK)
        for t in range(3):
            tx = aisle_bench_x
            ty = by + (-1 + t) * 0.32
            make_box(f"{prefix}_seat_A_tuft_{t}",
                     (tx, ty, seat_top - 0.008),
                     (0.05, 0.05, 0.012), COL_VINYL_RED_DK)
        make_box(f"{prefix}_back_A",
                 (aisle_back_x, by, back_z),
                 (div_thick, bench_w, back_h), COL_VINYL_RED_DK)
        for c in range(3):
            sy = by + (-1 + c) * 0.36
            make_box(f"{prefix}_back_A_stripe_{c}",
                     (aisle_back_x - div_thick / 2.0 - 0.005, sy, back_z),
                     (0.012, 0.025, back_h - 0.10), COL_VINYL_RED)

        # ── Square formica table ──
        table_top_z = 0.74
        make_box(f"{prefix}_table_top",
                 (table_x, by, table_top_z),
                 (table_sz, table_sz, 0.04), COL_FORMICA)
        # Chrome band rim
        make_box(f"{prefix}_table_band",
                 (table_x, by, table_top_z - 0.03),
                 (table_sz + 0.02, table_sz + 0.02, 0.02), COL_BRASS)
        # Chrome center post
        make_cyl(f"{prefix}_table_post",
                 (table_x, by, table_top_z / 2.0),
                 0.045, table_top_z - 0.04, COL_BRASS, segments=8, axis='Z')
        # Cast-iron floor disc
        make_cyl(f"{prefix}_table_foot",
                 (table_x, by, 0.03),
                 0.22, 0.04, (0.16, 0.14, 0.12, 1.0), segments=10, axis='Z')

        # ── Pendant lamp directly above the table ──
        wire_top_z = D_H - 0.05
        lamp_z = table_top_z + 0.70
        make_cyl(f"{prefix}_lamp_canopy",
                 (table_x, by, wire_top_z - 0.02),
                 0.07, 0.04, COL_BRASS, segments=8, axis='Z')
        make_cyl(f"{prefix}_lamp_stem",
                 (table_x, by, (lamp_z + wire_top_z) / 2.0),
                 0.012, wire_top_z - lamp_z,
                 COL_PAYPHONE_DARK, segments=4, axis='Z')
        # Conical shade (low sphere stand-in — flattened)
        make_sphere_low(f"{prefix}_lamp_shade",
                        (table_x, by, lamp_z), 0.20,
                        (0.86, 0.62, 0.32, 1.0), rings=2, segments=10)
        # Visible warm bulb
        make_sphere_low(f"{prefix}_lamp_bulb",
                        (table_x, by, lamp_z - 0.18), 0.05,
                        (0.98, 0.92, 0.74, 1.0), rings=2, segments=6)

        # Tiny table-number plaque
        make_box(f"{prefix}_table_number",
                 (table_x + table_sz / 2.0 - 0.08,
                  by - table_sz / 2.0 + 0.08, table_top_z + 0.022),
                 (0.07, 0.07, 0.005), COL_BRASS)

        # Register for table dressings
        BOOTH_POSITIONS.append((prefix, table_x, by, 'Y'))


def build_freestanding_tables():
    """Two small 2-top tables on the open center floor, between the
    booth row and the east wall. Adds variety without crowding."""
    # Position the tables in clear floor space — between alcove booths
    # (which span X=-9 to ~-7) and the new vestibule wall at X=+5.
    # Stay south of the hallway opening and out of the door-traffic lane.
    table_specs = [
        ("Bistro_1", -3.5, -1.0),
        ("Bistro_2", -1.0, +2.5),
        ("Bistro_3", +2.5, +3.5),
    ]
    table_top_z = 0.74
    for prefix, tx, ty in table_specs:
        # Round table top (low cylinder)
        make_cyl(f"{prefix}_top", (tx, ty, table_top_z),
                 0.42, 0.04, COL_FORMICA, segments=14, axis='Z')
        # Chrome edge band
        make_cyl(f"{prefix}_band", (tx, ty, table_top_z - 0.03),
                 0.43, 0.02, COL_BRASS, segments=14, axis='Z')
        # Center post
        make_cyl(f"{prefix}_post", (tx, ty, table_top_z / 2.0),
                 0.045, table_top_z - 0.04, COL_BRASS, segments=8, axis='Z')
        # Cast-iron base
        make_cyl(f"{prefix}_foot", (tx, ty, 0.03),
                 0.24, 0.04, (0.16, 0.14, 0.12, 1.0), segments=10, axis='Z')
        # Two bentwood chairs flanking the table (just suggestive)
        for ang_deg, label in [(180, 'S'), (0, 'N')]:
            ang = math.radians(ang_deg)
            cx = tx + 0.60 * math.cos(ang)
            cy = ty + 0.60 * math.sin(ang)
            # Seat
            make_cyl(f"{prefix}_chair_{label}_seat", (cx, cy, 0.46),
                     0.18, 0.04, COL_WOOD_TRIM, segments=10, axis='Z')
            # 4 legs
            for lx in (-1, +1):
                for ly in (-1, +1):
                    make_box(f"{prefix}_chair_{label}_leg_{lx:+d}_{ly:+d}",
                             (cx + lx * 0.12, cy + ly * 0.12, 0.23),
                             (0.025, 0.025, 0.46), COL_WOOD_TRIM)
            # Backrest (a curved hint via 3 short verticals + a top arc box)
            back_dy = 0.13 if ang_deg == 0 else -0.13
            for bx_off in (-0.10, 0.0, +0.10):
                make_box(f"{prefix}_chair_{label}_back_{bx_off:+.2f}",
                         (cx + bx_off, cy + back_dy, 0.78),
                         (0.025, 0.04, 0.60), COL_WOOD_TRIM)
            make_box(f"{prefix}_chair_{label}_back_top",
                     (cx, cy + back_dy, 1.06),
                     (0.30, 0.05, 0.04), COL_WOOD_TRIM)
        BOOTH_POSITIONS.append((prefix, tx, ty, 'Y'))


# ────────────────────────────────────────────────────────────────
# SCULPT HELPERS — cylinders, spheres, curved primitives.
# Lessons applied from the character work: asymmetric cross-
# sections give "this isn't a stack of boxes" reads. Use these
# for stool seats, hanging lamps, brass rails, clock face — the
# things at eye-level that benefit most from a non-blocky read.
# ────────────────────────────────────────────────────────────────

def make_cyl(name, center, radius, height, color, segments=8, axis='Z'):
    """Low-poly cylinder. axis = 'X' / 'Y' / 'Z' selects the
    cylinder's long axis."""
    import math
    cx, cy, cz = center
    h2 = height / 2.0
    verts = []
    for cap_sgn in (-1, +1):
        for i in range(segments):
            ang = 2 * math.pi * i / segments
            r0 = radius * math.cos(ang)
            r1 = radius * math.sin(ang)
            if axis == 'Z':
                verts.append((cx + r0, cy + r1, cz + cap_sgn * h2))
            elif axis == 'X':
                verts.append((cx + cap_sgn * h2, cy + r0, cz + r1))
            else:  # 'Y'
                verts.append((cx + r0, cy + cap_sgn * h2, cz + r1))
    # caps
    cap_lo = len(verts)
    if axis == 'Z':   verts.append((cx, cy, cz - h2))
    elif axis == 'X': verts.append((cx - h2, cy, cz))
    else:             verts.append((cx, cy - h2, cz))
    cap_hi = len(verts)
    if axis == 'Z':   verts.append((cx, cy, cz + h2))
    elif axis == 'X': verts.append((cx + h2, cy, cz))
    else:             verts.append((cx, cy + h2, cz))
    faces = []
    for i in range(segments):
        j = (i + 1) % segments
        # side quad
        faces.append([i, j, segments + j, segments + i])
        # bottom triangle
        faces.append([cap_lo, j, i])
        # top triangle
        faces.append([cap_hi, segments + i, segments + j])
    mesh = bpy.data.meshes.new(f"{name}_mesh")
    mesh.from_pydata(verts, [], faces)
    mesh.update(calc_edges=True)
    for poly in mesh.polygons:
        poly.use_smooth = False
    if not mesh.vertex_colors:
        mesh.vertex_colors.new(name="Col")
    vc = mesh.vertex_colors[0]
    for poly in mesh.polygons:
        for li in poly.loop_indices:
            vc.data[li].color = color
    obj = bpy.data.objects.new(name, mesh)
    bpy.context.collection.objects.link(obj)
    return obj


def make_sphere_low(name, center, radius, color, rings=3, segments=8):
    """Low-poly UV sphere. rings = horizontal divisions between
    poles; segments = vertical divisions around. ~3 rings × 8
    segments = 24 verts total."""
    import math
    cx, cy, cz = center
    verts = []
    # Top pole
    top_i = len(verts); verts.append((cx, cy, cz + radius))
    # Rings between poles
    ring_starts = []
    for r in range(1, rings):
        theta = math.pi * r / rings
        rz = math.cos(theta) * radius
        rh = math.sin(theta) * radius
        ring_starts.append(len(verts))
        for s in range(segments):
            phi = 2 * math.pi * s / segments
            verts.append((cx + rh * math.cos(phi),
                          cy + rh * math.sin(phi),
                          cz + rz))
    # Bottom pole
    bot_i = len(verts); verts.append((cx, cy, cz - radius))
    faces = []
    # Top cap (triangles from top pole to first ring)
    r0 = ring_starts[0]
    for s in range(segments):
        s1 = (s + 1) % segments
        faces.append([top_i, r0 + s, r0 + s1])
    # Middle rings
    for r in range(len(ring_starts) - 1):
        ra = ring_starts[r]; rb = ring_starts[r + 1]
        for s in range(segments):
            s1 = (s + 1) % segments
            faces.append([ra + s, ra + s1, rb + s1, rb + s])
    # Bottom cap
    rL = ring_starts[-1]
    for s in range(segments):
        s1 = (s + 1) % segments
        faces.append([bot_i, rL + s1, rL + s])
    mesh = bpy.data.meshes.new(f"{name}_mesh")
    mesh.from_pydata(verts, [], faces)
    mesh.update(calc_edges=True)
    for poly in mesh.polygons:
        poly.use_smooth = False
    if not mesh.vertex_colors:
        mesh.vertex_colors.new(name="Col")
    vc = mesh.vertex_colors[0]
    for poly in mesh.polygons:
        for li in poly.loop_indices:
            vc.data[li].color = color
    obj = bpy.data.objects.new(name, mesh)
    bpy.context.collection.objects.link(obj)
    return obj


# build_center_back_to_back_booths removed — user feedback was that the
# packed center booth pairs were "cramped and nightmarish" and trapped
# the hero figure inside the cluster. Layout is now a single row of
# alcove booths along the river window (build_alcove_booths) + a few
# free-standing bistro tables (build_freestanding_tables) on open floor.

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


# ────────────────────────────────────────────────────────────────
# INTERIOR PARTITIONS — vestibule + bar room + private dining
# ────────────────────────────────────────────────────────────────
# The east half of the diner (X > +5) is partitioned into three
# annex rooms separated from the main dining floor by interior
# walls. The hostess stand sits in the central VESTIBULE and
# routes patrons to the BAR (north), PRIVATE DINING (south), or
# the MAIN DINING floor (west).
#
#     +Y north
#     ┌─────────────────────┐
#     │  Bar Room   X=+5..9 │
#     │             Y=+1..6 │
#     ├──── door (Y=+1) ────┤
#     │  Vestibule  X=+5..9 │
#     │  (hostess)  Y=-2..+1│
#     ├──── door (Y=-2) ────┤
#     │  Private    X=+5..9 │
#     │  Dining     Y=-6..-2│
#     └─────────────────────┘
# Main dining floor: X=-9..+5, the full Y range.

VEST_X_W = +5.0     # west wall of the eastern annex stack
ANNEX_DOOR_W = 0.90


def build_interior_partitions():
    """Three new interior walls that split off the eastern annex
    rooms from the main dining floor + the cross-walls between
    annexes. Each wall is built as 2-3 wall segments with a door
    opening cut out."""
    # ── East-annex west wall at X=VEST_X_W, running full Y range ──
    # Opening 1: archway connecting main floor to vestibule
    #   (the hostess can see/wave the player through to the main floor)
    arch_y_center = -0.5
    arch_w = 1.60
    arch_h = 2.50
    # Wall segments north + south of the archway, then a lintel above
    seg_n_y_center = (D_D/2 + (arch_y_center + arch_w/2)) / 2.0
    seg_n_y_len    = D_D/2 - (arch_y_center + arch_w/2)
    seg_s_y_center = (-D_D/2 + (arch_y_center - arch_w/2)) / 2.0
    seg_s_y_len    = (arch_y_center - arch_w/2) - (-D_D/2)
    make_box("VestWall_W_segN",
             (VEST_X_W, seg_n_y_center, D_H/2),
             (0.10, seg_n_y_len, D_H), COL_WALL_INTERIOR)
    make_box("VestWall_W_segS",
             (VEST_X_W, seg_s_y_center, D_H/2),
             (0.10, seg_s_y_len, D_H), COL_WALL_INTERIOR)
    # Lintel above the arch
    make_box("VestWall_W_lintel",
             (VEST_X_W, arch_y_center, arch_h + (D_H - arch_h)/2),
             (0.10, arch_w, D_H - arch_h), COL_WALL_INTERIOR)
    # Decorative wood trim around the archway (a fat moulding)
    make_box("VestWall_W_arch_trim_top",
             (VEST_X_W - 0.04, arch_y_center, arch_h - 0.04),
             (0.06, arch_w + 0.20, 0.10), COL_WOOD_TRIM)
    for sgn in (-1, +1):
        make_box(f"VestWall_W_arch_trim_side_{sgn:+d}",
                 (VEST_X_W - 0.04, arch_y_center + sgn * arch_w/2, arch_h/2),
                 (0.06, 0.10, arch_h), COL_WOOD_TRIM)

    # ── Vestibule ↔ Bar wall at Y=+1.0, X = VEST_X_W to D_W/2 ──
    bar_door_x_center = +7.0
    door_w = ANNEX_DOOR_W
    door_h = 2.20
    wall_len_E = D_W/2 - (bar_door_x_center + door_w/2)
    wall_len_W = (bar_door_x_center - door_w/2) - VEST_X_W
    make_box("BarPartition_W_seg",
             (VEST_X_W + wall_len_W/2, +1.0, D_H/2),
             (wall_len_W, 0.10, D_H), COL_WALL_INTERIOR)
    make_box("BarPartition_E_seg",
             (D_W/2 - wall_len_E/2, +1.0, D_H/2),
             (wall_len_E, 0.10, D_H), COL_WALL_INTERIOR)
    # Above the door
    make_box("BarPartition_lintel",
             (bar_door_x_center, +1.0, door_h + (D_H - door_h)/2),
             (door_w, 0.10, D_H - door_h), COL_WALL_INTERIOR)
    # Door frame (sits inside the opening — wood)
    make_box("BarDoor_Jamb_L",
             (bar_door_x_center - door_w/2 - 0.025, +1.0, door_h/2),
             (0.05, 0.14, door_h), COL_WOOD_TRIM)
    make_box("BarDoor_Jamb_R",
             (bar_door_x_center + door_w/2 + 0.025, +1.0, door_h/2),
             (0.05, 0.14, door_h), COL_WOOD_TRIM)
    make_box("BarDoor_Header",
             (bar_door_x_center, +1.0, door_h + 0.06),
             (door_w + 0.20, 0.14, 0.10), COL_WOOD_TRIM)

    # ── Vestibule ↔ Private Dining wall at Y=-2.0 ──
    pd_door_x_center = +5.8
    wall_len_E2 = D_W/2 - (pd_door_x_center + door_w/2)
    wall_len_W2 = (pd_door_x_center - door_w/2) - VEST_X_W
    make_box("PrivPartition_W_seg",
             (VEST_X_W + wall_len_W2/2, -2.0, D_H/2),
             (wall_len_W2, 0.10, D_H), COL_WALL_INTERIOR)
    make_box("PrivPartition_E_seg",
             (D_W/2 - wall_len_E2/2, -2.0, D_H/2),
             (wall_len_E2, 0.10, D_H), COL_WALL_INTERIOR)
    make_box("PrivPartition_lintel",
             (pd_door_x_center, -2.0, door_h + (D_H - door_h)/2),
             (door_w, 0.10, D_H - door_h), COL_WALL_INTERIOR)
    make_box("PrivDoor_Jamb_L",
             (pd_door_x_center - door_w/2 - 0.025, -2.0, door_h/2),
             (0.05, 0.14, door_h), COL_WOOD_TRIM)
    make_box("PrivDoor_Jamb_R",
             (pd_door_x_center + door_w/2 + 0.025, -2.0, door_h/2),
             (0.05, 0.14, door_h), COL_WOOD_TRIM)
    make_box("PrivDoor_Header",
             (pd_door_x_center, -2.0, door_h + 0.06),
             (door_w + 0.20, 0.14, 0.10), COL_WOOD_TRIM)
    # Brass numerals "17" stenciled on the lintel (Hierophant canon —
    # the Sunday brunch ritual table sits inside this room)
    make_box("PrivDoor_Num1",
             (pd_door_x_center - 0.05, -1.99, door_h + 0.10),
             (0.06, 0.005, 0.10), COL_BRASS)
    make_box("PrivDoor_Num7",
             (pd_door_x_center + 0.05, -1.99, door_h + 0.10),
             (0.06, 0.005, 0.10), COL_BRASS)


def build_bar_room():
    """A real, working cocktail bar inside the NE annex room
    (X=+5..+9, Y=+1..+6).

    Per canon: 'closed cocktail bar to the parking-lot side' — but
    the user has now asked us to BUILD it. Treat as 'recently
    re-opened, dim, lived-in.' The bar runs E-W along the north
    wall, with stools facing it from the south. Back-bar bottles
    against the building's north wall (with the actual outer
    parking-lot window cropped by the bar's height).
    """
    # Floor accent (a slightly darker tile so the bar room reads as
    # its own space from the main floor)
    bar_room_cx = (VEST_X_W + D_W/2) / 2.0
    bar_room_cy = (1.0 + D_D/2) / 2.0
    make_box("BarRoom_Accent_Floor",
             (bar_room_cx, bar_room_cy, 0.025),
             (D_W/2 - VEST_X_W - 0.20, D_D/2 - 1.0 - 0.20, 0.005),
             (0.18, 0.10, 0.06, 1.0))
    # ── The bar itself (E-W counter, customer-side south) ──
    bar_cx = bar_room_cx
    bar_cy = D_D/2 - 1.0   # bar face is 1.0m south of the north wall
    bar_top_z = 1.10
    bar_len = D_W/2 - VEST_X_W - 1.20    # 2.80m
    make_box("Bar_Top", (bar_cx, bar_cy, bar_top_z),
             (bar_len, 0.70, 0.06), COL_BAR_WOOD)
    # Bar front (south-facing customer side) — vinyl pad strip
    make_box("Bar_Front",
             (bar_cx, bar_cy - 0.35, 0.55),
             (bar_len, 0.04, 1.10), COL_VINYL_RED_DK)
    # Brass foot rail
    make_cyl("Bar_FootRail", (bar_cx, bar_cy - 0.36, 0.18),
             0.024, bar_len, COL_BRASS, segments=8, axis='X')
    for end_sgn in (-1, +1):
        make_cyl(f"Bar_FootRailCap_{end_sgn:+d}",
                 (bar_cx + end_sgn * bar_len/2, bar_cy - 0.36, 0.18),
                 0.040, 0.10, COL_BRASS, segments=8, axis='X')
    # Bar-back (the cabinet behind the bartender, with bottles)
    back_bar_y = bar_cy + 0.50
    make_box("BarBack_Cabinet_Lower",
             (bar_cx, back_bar_y, 0.65),
             (bar_len, 0.40, 1.30), COL_BAR_WOOD)
    # 3 bottle shelves
    for s in range(3):
        sz = 1.45 + s * 0.40
        make_box(f"BarBack_Shelf_{s}",
                 (bar_cx, back_bar_y - 0.10, sz),
                 (bar_len, 0.20, 0.03), COL_WOOD_TRIM)
        # Bottles on this shelf — 6-8 cylinders of various tints
        n_bottles = 7
        for b in range(n_bottles):
            bx = bar_cx - bar_len/2 + 0.20 + b * (bar_len - 0.40) / (n_bottles - 1)
            by = back_bar_y - 0.10
            bottle_color = [
                (0.18, 0.32, 0.20, 1.0),    # gin / olive-green glass
                (0.42, 0.20, 0.10, 1.0),    # whisky brown
                (0.62, 0.46, 0.20, 1.0),    # bourbon amber
                (0.30, 0.18, 0.34, 1.0),    # something dark purple
                (0.86, 0.74, 0.36, 1.0),    # rum / honey
                (0.20, 0.16, 0.34, 1.0),    # blueish liqueur
                (0.74, 0.20, 0.18, 1.0),    # vermouth red
            ][(b + s) % 7]
            make_cyl(f"Bottle_{s}_{b}",
                     (bx, by, sz + 0.16), 0.035, 0.30,
                     bottle_color, segments=6, axis='Z')
            # Cap
            make_cyl(f"Bottle_{s}_{b}_Cap",
                     (bx, by, sz + 0.32), 0.018, 0.04,
                     (0.10, 0.08, 0.06, 1.0), segments=4, axis='Z')
    # Backbar MIRROR (a darker reflective slab between shelves) —
    # adds the canonical "bar with a long mirror behind it" silhouette
    make_box("BarBack_Mirror",
             (bar_cx, back_bar_y + 0.18, 2.30),
             (bar_len - 0.20, 0.04, 1.10),
             (0.10, 0.10, 0.12, 1.0))
    make_box("BarBack_Mirror_Frame",
             (bar_cx, back_bar_y + 0.16, 2.30),
             (bar_len, 0.06, 1.25), COL_WOOD_TRIM)

    # Bar stools (taller than diner stools — chrome posts + leather seats)
    n_bar_stools = 4
    stool_y = bar_cy - 0.95
    for i in range(n_bar_stools):
        sx = bar_cx - bar_len/2 + 0.45 + i * (bar_len - 0.90) / (n_bar_stools - 1)
        # Post
        make_cyl(f"BarStool_{i}_post", (sx, stool_y, 0.40),
                 0.04, 0.80, COL_BRASS, segments=6, axis='Z')
        # Foot ring
        make_cyl(f"BarStool_{i}_foot", (sx, stool_y, 0.22),
                 0.18, 0.025, COL_BRASS, segments=8, axis='Z')
        # Leather padded seat (slightly larger than diner stool)
        make_cyl(f"BarStool_{i}_seat", (sx, stool_y, 0.82),
                 0.22, 0.07, (0.32, 0.18, 0.10, 1.0), segments=10, axis='Z')
        # Low back hook on chrome rod
        make_cyl(f"BarStool_{i}_back_rod", (sx, stool_y + 0.16, 1.05),
                 0.016, 0.40, COL_BRASS, segments=4, axis='Z')
        make_box(f"BarStool_{i}_back_pad", (sx, stool_y + 0.18, 1.20),
                 (0.32, 0.04, 0.16), (0.32, 0.18, 0.10, 1.0))

    # A round 2-top cocktail table in the SW corner of the bar room
    ct_x, ct_y = VEST_X_W + 0.95, +2.0
    make_cyl("BarCocktailTable_Top", (ct_x, ct_y, 0.92),
             0.34, 0.04, COL_FORMICA, segments=10, axis='Z')
    make_cyl("BarCocktailTable_Post", (ct_x, ct_y, 0.45),
             0.035, 0.90, COL_BRASS, segments=6, axis='Z')
    make_cyl("BarCocktailTable_Foot", (ct_x, ct_y, 0.03),
             0.20, 0.04, (0.16, 0.14, 0.12, 1.0), segments=8, axis='Z')
    # Two bistro chairs at the cocktail table
    for ang_deg, label in [(120, 'NE'), (-120, 'SE')]:
        ang = math.radians(ang_deg)
        cx = ct_x + 0.50 * math.cos(ang)
        cy = ct_y + 0.50 * math.sin(ang)
        make_cyl(f"BarChair_{label}_seat", (cx, cy, 0.46),
                 0.16, 0.04, COL_WOOD_TRIM, segments=10, axis='Z')
        for lx in (-1, +1):
            for ly in (-1, +1):
                make_box(f"BarChair_{label}_leg_{lx:+d}_{ly:+d}",
                         (cx + lx*0.11, cy + ly*0.11, 0.23),
                         (0.025, 0.025, 0.46), COL_WOOD_TRIM)
        make_box(f"BarChair_{label}_back",
                 (cx, cy + (0.12 if ang_deg > 0 else -0.12), 0.78),
                 (0.30, 0.04, 0.50), COL_WOOD_TRIM)

    # Pendant lamp over the cocktail table
    lamp_z = 0.92 + 0.85
    make_cyl("BarTable_Lamp_Wire",
             (ct_x, ct_y, (lamp_z + D_H - 0.05)/2),
             0.012, (D_H - 0.05) - lamp_z,
             COL_PAYPHONE_DARK, segments=4, axis='Z')
    make_sphere_low("BarTable_Lamp_Shade", (ct_x, ct_y, lamp_z),
                    0.20, (0.66, 0.42, 0.22, 1.0), rings=2, segments=8)
    make_sphere_low("BarTable_Lamp_Bulb", (ct_x, ct_y, lamp_z - 0.18),
                    0.05, (0.98, 0.84, 0.56, 1.0), rings=2, segments=6)

    # Pendant strip over the bar itself — 3 small drop fixtures
    for i in range(3):
        plx = bar_cx - bar_len/2 + 0.40 + i * (bar_len - 0.80) / 2.0
        ply = bar_cy
        plz = 2.10
        make_cyl(f"BarPendant_{i}_Wire",
                 (plx, ply, (plz + D_H - 0.05)/2),
                 0.010, (D_H - 0.05) - plz,
                 COL_PAYPHONE_DARK, segments=4, axis='Z')
        make_cyl(f"BarPendant_{i}_Shade",
                 (plx, ply, plz), 0.14, 0.16,
                 (0.52, 0.30, 0.16, 1.0), segments=8, axis='Z')
        make_sphere_low(f"BarPendant_{i}_Bulb",
                        (plx, ply, plz - 0.12), 0.04,
                        (0.96, 0.78, 0.42, 1.0), rings=2, segments=6)

    # Single bar-tap detail (sits on the customer side of the bar)
    tap_x = bar_cx + 0.50
    make_cyl("BarTap_Body", (tap_x, bar_cy, bar_top_z + 0.18),
             0.025, 0.30, COL_BRASS, segments=6, axis='Z')
    make_cyl("BarTap_Handle", (tap_x, bar_cy - 0.10, bar_top_z + 0.30),
             0.018, 0.18, (0.32, 0.18, 0.10, 1.0), segments=6, axis='Z')

    # An old jukebox tucked in the corner (SE of bar room)
    jb_x, jb_y = D_W/2 - 0.6, +1.6
    make_box("Jukebox_Body", (jb_x, jb_y, 0.65),
             (0.40, 0.55, 1.30), (0.32, 0.20, 0.12, 1.0))
    # Curved arched glass front
    make_box("Jukebox_Glass", (jb_x - 0.16, jb_y, 1.05),
             (0.04, 0.45, 0.50), (0.30, 0.45, 0.62, 1.0))
    # Side neon trim strips
    for sgn in (-1, +1):
        make_box(f"Jukebox_Neon_{sgn:+d}",
                 (jb_x - 0.10, jb_y + sgn * 0.25, 1.05),
                 (0.04, 0.025, 0.65), (0.78, 0.32, 0.96, 1.0))
    # Speaker grill at the bottom
    make_box("Jukebox_Speaker", (jb_x - 0.16, jb_y, 0.40),
             (0.02, 0.40, 0.30), (0.18, 0.14, 0.10, 1.0))


def build_private_dining_room():
    """The Hierophant's Table — a small formal dining room in the
    SE annex (X=+5..+9, Y=-6..-2). Long table for 6, sideboard,
    a single chandelier. Per Hierophant canon: 'Table 17 of
    D'Ambrosio's (Sunday brunch).' This is that table."""
    pd_cx = (VEST_X_W + D_W/2) / 2.0    # +7.0
    pd_cy = (-D_D/2 + (-2.0)) / 2.0     # -4.0
    # Dark wood floor accent
    make_box("PrivDining_Floor_Accent",
             (pd_cx, pd_cy, 0.025),
             (D_W/2 - VEST_X_W - 0.20, 4.0 - 0.20, 0.005),
             (0.18, 0.10, 0.06, 1.0))
    # Tablecloth-covered long table (E-W)
    table_w = 2.40
    table_d = 1.00
    table_top_z = 0.76
    make_box("PrivTable_Top", (pd_cx, pd_cy, table_top_z),
             (table_w, table_d, 0.04), (0.92, 0.88, 0.78, 1.0))
    # Tablecloth drape (a thin curtain hanging down on each side)
    for sgn in (-1, +1):
        make_box(f"PrivTable_Cloth_NS_{sgn:+d}",
                 (pd_cx, pd_cy + sgn * (table_d/2 + 0.002), table_top_z - 0.30),
                 (table_w + 0.04, 0.004, 0.60),
                 (0.92, 0.88, 0.78, 1.0))
        make_box(f"PrivTable_Cloth_EW_{sgn:+d}",
                 (pd_cx + sgn * (table_w/2 + 0.002), pd_cy, table_top_z - 0.30),
                 (0.004, table_d + 0.04, 0.60),
                 (0.92, 0.88, 0.78, 1.0))
    # 6 wooden chairs (3 north, 3 south)
    chair_h = 1.05
    for s_i, sgn in enumerate([+1, -1]):
        cy = pd_cy + sgn * 0.85
        for c_i in range(3):
            cx = pd_cx - 0.80 + c_i * 0.80
            # Seat
            make_box(f"PrivChair_{s_i}_{c_i}_seat",
                     (cx, cy, 0.46), (0.42, 0.44, 0.06), COL_WOOD_TRIM)
            # 4 legs
            for lx in (-1, +1):
                for ly in (-1, +1):
                    make_box(f"PrivChair_{s_i}_{c_i}_leg_{lx:+d}_{ly:+d}",
                             (cx + lx*0.18, cy + ly*0.19, 0.23),
                             (0.04, 0.04, 0.46), COL_WOOD_TRIM)
            # Tall ladder-back (toward outside of the table)
            back_dy = sgn * 0.19
            for bx_off in (-0.16, 0.0, +0.16):
                make_box(f"PrivChair_{s_i}_{c_i}_backpost_{bx_off:+.2f}",
                         (cx + bx_off, cy + back_dy, 0.78),
                         (0.04, 0.05, 0.60), COL_WOOD_TRIM)
            make_box(f"PrivChair_{s_i}_{c_i}_back_top",
                     (cx, cy + back_dy, 1.10),
                     (0.40, 0.06, 0.06), COL_WOOD_TRIM)
            # Seat cushion (vinyl red)
            make_box(f"PrivChair_{s_i}_{c_i}_cushion",
                     (cx, cy, 0.50), (0.38, 0.40, 0.04), COL_VINYL_RED)
    # Chairs at each END (head + foot of the table)
    for end_i, sgn_x in enumerate([+1, -1]):
        cx = pd_cx + sgn_x * (table_w/2 + 0.45)
        cy = pd_cy
        make_box(f"PrivChair_end_{end_i}_seat",
                 (cx, cy, 0.46), (0.42, 0.44, 0.06), COL_WOOD_TRIM)
        for lx in (-1, +1):
            for ly in (-1, +1):
                make_box(f"PrivChair_end_{end_i}_leg_{lx:+d}_{ly:+d}",
                         (cx + lx*0.18, cy + ly*0.19, 0.23),
                         (0.04, 0.04, 0.46), COL_WOOD_TRIM)
        back_dx = sgn_x * 0.19
        for bz_off in (-0.16, 0.0, +0.16):
            make_box(f"PrivChair_end_{end_i}_backpost_{bz_off:+.2f}",
                     (cx + back_dx, cy + bz_off, 0.78),
                     (0.05, 0.04, 0.60), COL_WOOD_TRIM)
        make_box(f"PrivChair_end_{end_i}_back_top",
                 (cx + back_dx, cy, 1.10),
                 (0.06, 0.40, 0.06), COL_WOOD_TRIM)

    # Sideboard against the south wall (Y=-D_D/2)
    sb_y = -D_D/2 + 0.30
    make_box("PrivSideboard_Body", (pd_cx, sb_y, 0.50),
             (2.40, 0.55, 0.95), COL_WOOD_TRIM)
    # Top
    make_box("PrivSideboard_Top", (pd_cx, sb_y, 1.00),
             (2.50, 0.60, 0.04), (0.30, 0.18, 0.10, 1.0))
    # 3 cabinet door panels
    for d in range(3):
        dx = pd_cx - 0.80 + d * 0.80
        make_box(f"PrivSideboard_Door_{d}",
                 (dx, sb_y - 0.28, 0.50),
                 (0.65, 0.005, 0.75), (0.22, 0.14, 0.08, 1.0))
        # Handle
        make_box(f"PrivSideboard_Handle_{d}",
                 (dx + 0.20, sb_y - 0.30, 0.55),
                 (0.10, 0.02, 0.018), COL_BRASS)
    # Decanter + glasses on the sideboard
    make_cyl("PrivDecanter", (pd_cx - 0.70, sb_y - 0.10, 1.16),
             0.07, 0.30, (0.62, 0.42, 0.22, 1.0), segments=8, axis='Z')
    make_cyl("PrivDecanter_Stopper", (pd_cx - 0.70, sb_y - 0.10, 1.34),
             0.04, 0.06, (0.78, 0.62, 0.36, 1.0), segments=6, axis='Z')
    for g in range(4):
        gx = pd_cx - 0.20 + g * 0.20
        make_cyl(f"PrivGlass_{g}",
                 (gx, sb_y - 0.10, 1.10),
                 0.035, 0.10, (0.86, 0.90, 0.92, 1.0), segments=6, axis='Z')

    # Tarot stack on the table center (Hierophant table marker)
    make_box("Table17_TarotStack",
             (pd_cx, pd_cy, table_top_z + 0.04),
             (0.10, 0.16, 0.04), (0.92, 0.88, 0.72, 1.0))
    # Top card face up — the Hierophant
    make_box("Table17_TopCard",
             (pd_cx + 0.05, pd_cy + 0.10, table_top_z + 0.025),
             (0.10, 0.16, 0.004), (0.94, 0.90, 0.72, 1.0))
    # Symbol on the card (gold dot suggesting a sigil)
    make_box("Table17_TopCard_Sigil",
             (pd_cx + 0.05, pd_cy + 0.10, table_top_z + 0.028),
             (0.04, 0.06, 0.002), COL_BRASS)
    # Brass table-number plaque "17"
    make_box("Table17_Plaque",
             (pd_cx + table_w/2 - 0.10, pd_cy - table_d/2 + 0.10, table_top_z + 0.022),
             (0.08, 0.08, 0.005), COL_BRASS)

    # Chandelier — multi-tier brass with 4 candle-bulbs
    ch_z_top = D_H - 0.10
    ch_z_low = ch_z_top - 0.90
    make_cyl("PrivChandelier_Chain",
             (pd_cx, pd_cy, (ch_z_top + ch_z_low)/2.0),
             0.014, ch_z_top - ch_z_low,
             COL_BRASS, segments=4, axis='Z')
    make_cyl("PrivChandelier_Body",
             (pd_cx, pd_cy, ch_z_low),
             0.10, 0.20, COL_BRASS, segments=8, axis='Z')
    # 4 arms with bulbs (cardinal directions)
    for ang_deg in (0, 90, 180, 270):
        ang = math.radians(ang_deg)
        ax = pd_cx + 0.36 * math.cos(ang)
        ay = pd_cy + 0.36 * math.sin(ang)
        # Arm (horizontal cylinder)
        if abs(math.sin(ang)) > 0.5:
            make_cyl(f"PrivChandelier_Arm_{ang_deg}",
                     ((pd_cx + ax)/2, (pd_cy + ay)/2, ch_z_low),
                     0.014, 0.36, COL_BRASS, segments=4, axis='Y')
        else:
            make_cyl(f"PrivChandelier_Arm_{ang_deg}",
                     ((pd_cx + ax)/2, (pd_cy + ay)/2, ch_z_low),
                     0.014, 0.36, COL_BRASS, segments=4, axis='X')
        # Candle cup
        make_cyl(f"PrivChandelier_Cup_{ang_deg}",
                 (ax, ay, ch_z_low + 0.04),
                 0.04, 0.06, COL_BRASS, segments=6, axis='Z')
        # Candle bulb (warm sphere)
        make_sphere_low(f"PrivChandelier_Bulb_{ang_deg}",
                        (ax, ay, ch_z_low + 0.14), 0.05,
                        (0.98, 0.86, 0.56, 1.0), rings=2, segments=6)

    # Framed painting on the west wall (interior of the private room)
    make_box("PrivPainting_Frame",
             (VEST_X_W + 0.06, pd_cy + 0.5, 1.80),
             (0.04, 0.70, 0.90), COL_PHOTO_FRAME)
    make_box("PrivPainting_Canvas",
             (VEST_X_W + 0.09, pd_cy + 0.5, 1.80),
             (0.02, 0.60, 0.80), (0.32, 0.22, 0.16, 1.0))


def build_storage_closet_and_bbs():
    """A small storage closet off the back hallway with the dim
    BBS terminal canonical to the room. Per user direction: 'BBS
    terminal, in a dark corner of the room, probably a storage
    closet.' Accessed by a door on the east wall of the back
    hallway."""
    # The hallway east wall is at X = HALL_W/2 = +2.5, Y from D_D/2
    # (=+6) to D_D/2 + HALL_D (=+8.4). The closet annex extends EAST
    # of the hallway from X=+2.5 to +4.0, Y=+7.0 to +8.4 (1.5×1.4 m).
    cl_x_min, cl_x_max = +2.5, +4.0
    cl_y_min, cl_y_max = +7.0, +8.4
    cl_cx = (cl_x_min + cl_x_max) / 2.0
    cl_cy = (cl_y_min + cl_y_max) / 2.0
    cl_w = cl_x_max - cl_x_min
    cl_d = cl_y_max - cl_y_min
    # Floor and ceiling
    make_box("Closet_Floor", (cl_cx, cl_cy, -0.05),
             (cl_w, cl_d, 0.10),
             (0.20, 0.16, 0.10, 1.0), open_faces={'-Z'})
    make_box("Closet_Ceiling", (cl_cx, cl_cy, D_H + 0.05),
             (cl_w, cl_d, 0.10), (0.08, 0.06, 0.04, 1.0), open_faces={'+Z'})
    # East wall (outer wall, where the closet ends)
    make_box("Closet_Wall_E", (cl_x_max + 0.05, cl_cy, D_H/2),
             (0.10, cl_d, D_H), COL_WALL_INTERIOR)
    # North wall
    make_box("Closet_Wall_N", (cl_cx, cl_y_max + 0.05, D_H/2),
             (cl_w, 0.10, D_H), COL_WALL_INTERIOR)
    # South wall
    make_box("Closet_Wall_S", (cl_cx, cl_y_min - 0.05, D_H/2),
             (cl_w, 0.10, D_H), COL_WALL_INTERIOR)
    # West wall is shared with hallway east wall — break the hallway
    # east wall to insert a door. Hallway east wall built in
    # build_back_hallway already spans the full hall length; we
    # rebuild that wall's geometry here to leave a door opening at
    # Y around +7.6.
    # The hallway east wall in build_back_hallway lives at X=HALL_W/2+0.05;
    # rather than refactor that, we just add a DOOR FRAME at that
    # exact position and let the player walk through. In Godot, the
    # collision box is the static body in the .tscn, not this mesh.
    door_y = (cl_y_min + cl_y_max) / 2.0    # +7.7
    door_h = 2.05
    make_box("ClosetDoor_Panel",
             (cl_x_min - 0.02, door_y, door_h/2),
             (0.04, 0.80, door_h), (0.18, 0.12, 0.08, 1.0))
    make_box("ClosetDoor_Knob",
             (cl_x_min - 0.05, door_y + 0.30, 1.05),
             (0.03, 0.06, 0.06), COL_BRASS)
    # Tarot card pinned to the door (gauntlet flavor — this closet
    # is "for staff only" but the door has a hand-tacked card)
    make_box("ClosetDoor_Card",
             (cl_x_min - 0.045, door_y - 0.15, 1.55),
             (0.005, 0.14, 0.20), COL_CARD_PAPER)
    make_box("ClosetDoor_Card_Sigil",
             (cl_x_min - 0.043, door_y - 0.15, 1.55),
             (0.005, 0.05, 0.08), COL_BRASS)

    # ── INSIDE: dim shelves + the BBS terminal on a small desk ──
    # A small wooden desk against the east wall of the closet
    desk_x = cl_x_max - 0.45
    desk_y = cl_cy
    desk_top_z = 0.72
    make_box("ClosetDesk_Top", (desk_x, desk_y, desk_top_z),
             (0.50, cl_d - 0.30, 0.04), COL_WOOD_TRIM)
    # Front and side panels
    make_box("ClosetDesk_Front",
             (desk_x - 0.24, desk_y, 0.36),
             (0.04, cl_d - 0.30, 0.70), COL_BAR_WOOD)
    make_box("ClosetDesk_Back",
             (desk_x + 0.24, desk_y, 0.36),
             (0.04, cl_d - 0.30, 0.70), COL_BAR_WOOD)
    # ── BBS Terminal (beige case, phosphor green CRT screen) ──
    crt_x, crt_y, crt_z = desk_x, desk_y - 0.10, desk_top_z + 0.20
    make_box("BBS_Case_Diner", (crt_x, crt_y, crt_z),
             (0.42, 0.40, 0.36),
             (0.30, 0.28, 0.22, 1.0))   # beige
    # Screen bezel (dark recess)
    make_box("BBS_Bezel_Diner",
             (crt_x - 0.20, crt_y, crt_z + 0.02),
             (0.02, 0.32, 0.26),
             (0.10, 0.18, 0.12, 1.0))
    # Phosphor green screen
    make_box("BBS_Screen_Diner",
             (crt_x - 0.22, crt_y, crt_z + 0.02),
             (0.005, 0.28, 0.22),
             (0.30, 0.92, 0.50, 1.0))
    # 5 scanline-rows (slightly darker green)
    for i in range(5):
        line_z = crt_z - 0.08 + i * 0.04
        make_box(f"BBS_Scan_{i}",
                 (crt_x - 0.225, crt_y, line_z),
                 (0.003, 0.20, 0.010), (0.20, 0.62, 0.32, 1.0))
    # Keyboard
    make_box("BBS_KB_Diner",
             (crt_x - 0.30, crt_y, desk_top_z + 0.025),
             (0.16, 0.36, 0.025), (0.18, 0.16, 0.14, 1.0))
    for r in range(4):
        kx = crt_x - 0.30 - 0.05 + r * 0.03
        make_box(f"BBS_KeyRow_Diner_{r}",
                 (kx, crt_y, desk_top_z + 0.041),
                 (0.022, 0.32, 0.010), (0.32, 0.30, 0.26, 1.0))
    # Tarot card sleeve next to keyboard — a stack of pulled cards
    # waiting to be entered into the BBS log
    make_box("BBS_CardStack_Diner",
             (crt_x - 0.10, crt_y + 0.20, desk_top_z + 0.022),
             (0.08, 0.14, 0.04), COL_CARD_PAPER)
    make_box("BBS_CardStack_Top",
             (crt_x - 0.10, crt_y + 0.20, desk_top_z + 0.045),
             (0.08, 0.14, 0.003), COL_CARD_PINK)
    # Wooden stool tucked under the desk
    make_cyl("ClosetStool_Seat",
             (desk_x - 0.20, desk_y, 0.50),
             0.17, 0.04, COL_WOOD_TRIM, segments=10, axis='Z')
    for lx in (-1, +1):
        for ly in (-1, +1):
            make_box(f"ClosetStool_Leg_{lx:+d}_{ly:+d}",
                     (desk_x - 0.20 + lx*0.11, desk_y + ly*0.11, 0.25),
                     (0.025, 0.025, 0.50), COL_WOOD_TRIM)
    # Wall shelves above the BBS (4 horizontal slats with bottles/boxes)
    for s in range(2):
        sh_z = 1.80 + s * 0.50
        make_box(f"Closet_Shelf_{s}",
                 (cl_cx, cl_cy, sh_z),
                 (cl_w - 0.30, cl_d - 0.30, 0.025), COL_WOOD_TRIM)
        # A few boxes/jars on each shelf
        for b in range(3):
            bx = cl_cx - 0.30 + b * 0.30
            by = cl_cy
            make_box(f"Closet_Item_{s}_{b}",
                     (bx, by, sh_z + 0.10),
                     (0.16, 0.14, 0.20),
                     [
                         (0.42, 0.30, 0.18, 1.0),
                         (0.30, 0.42, 0.22, 1.0),
                         (0.62, 0.42, 0.24, 1.0),
                     ][b])
    # A broom + mop in the corner (canon storage closet)
    broom_x, broom_y = cl_x_min + 0.20, cl_y_max - 0.20
    make_cyl("Closet_Broom_Handle", (broom_x, broom_y, 0.80),
             0.014, 1.60, COL_WOOD_TRIM, segments=4, axis='Z')
    make_box("Closet_Broom_Head", (broom_x, broom_y, 0.06),
             (0.30, 0.10, 0.10), COL_BAR_WOOD)
    make_cyl("Closet_Mop_Handle", (broom_x + 0.20, broom_y, 0.78),
             0.014, 1.56, COL_BRASS, segments=4, axis='Z')
    make_cyl("Closet_Mop_Head", (broom_x + 0.20, broom_y, 0.06),
             0.10, 0.08, (0.62, 0.50, 0.32, 1.0), segments=8, axis='Z')


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
    cy = -3.5   # counter Y (matches new kitchen-side build_counter)
    counter_top_z = 1.10
    # Pie display case — glass dome + 2 visible pies + base
    pcx = -0.5
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
    """Salt + pepper + napkin dispenser + sugar caddy + ketchup bottle
    on every booth table. Reads from the BOOTH_POSITIONS list populated
    by the booth builders so this stays in sync."""
    table_z = TABLE_TOP_Z
    for i, (prefix, tx, ty, axis_along) in enumerate(BOOTH_POSITIONS):
        # Use the table's two principal axes:
        #   axis_long = bench axis (table's long dimension)
        #   axis_short = the leg-gap axis (table's short dimension)
        # We arrange condiments AT THE FAR END of the table (away from
        # players sitting across), grouped tight.
        if axis_along == 'Y':
            long_axis_off = lambda d: (0.0, d, 0.0)
            short_axis_off = lambda d: (d, 0.0, 0.0)
        else:
            long_axis_off = lambda d: (d, 0.0, 0.0)
            short_axis_off = lambda d: (0.0, d, 0.0)
        # Anchor at one end of the long axis (~0.30m from table center)
        anchor_long = +0.28
        anchor = (tx + long_axis_off(anchor_long)[0],
                  ty + long_axis_off(anchor_long)[1])
        # Salt shaker
        sx_off = short_axis_off(+0.08)
        make_box(f"Salt_{i}", (anchor[0] + sx_off[0], anchor[1] + sx_off[1], table_z + 0.07),
                 (0.06, 0.06, 0.12), COL_SALT)
        make_box(f"Salt_Cap_{i}", (anchor[0] + sx_off[0], anchor[1] + sx_off[1], table_z + 0.14),
                 (0.05, 0.05, 0.025), COL_BRASS)
        # Pepper shaker (paired next to salt)
        px_off = short_axis_off(-0.08)
        make_box(f"Pepper_{i}", (anchor[0] + px_off[0], anchor[1] + px_off[1], table_z + 0.07),
                 (0.06, 0.06, 0.12), COL_PEPPER)
        make_box(f"Pepper_Cap_{i}", (anchor[0] + px_off[0], anchor[1] + px_off[1], table_z + 0.14),
                 (0.05, 0.05, 0.025), COL_BRASS)
        # Napkin dispenser (further toward end of table)
        nd_long = long_axis_off(+0.10)
        make_box(f"NapkinDispenser_{i}",
                 (anchor[0] + nd_long[0], anchor[1] + nd_long[1], table_z + 0.09),
                 (0.10 if axis_along == 'Y' else 0.18, 0.18 if axis_along == 'Y' else 0.10, 0.17),
                 COL_KITCHEN_STEEL)
        make_box(f"Napkins_{i}",
                 (anchor[0] + nd_long[0], anchor[1] + nd_long[1], table_z + 0.105),
                 (0.08 if axis_along == 'Y' else 0.14, 0.14 if axis_along == 'Y' else 0.08, 0.13),
                 COL_NAPKIN)
        # Ketchup bottle — squat red cylinder with darker cap
        kt_off = long_axis_off(-0.08)
        make_cyl(f"Ketchup_Body_{i}",
                 (anchor[0] + kt_off[0], anchor[1] + kt_off[1], table_z + 0.06),
                 0.030, 0.12, (0.72, 0.18, 0.14, 1.0), segments=8, axis='Z')
        make_cyl(f"Ketchup_Neck_{i}",
                 (anchor[0] + kt_off[0], anchor[1] + kt_off[1], table_z + 0.14),
                 0.018, 0.04, (0.72, 0.18, 0.14, 1.0), segments=6, axis='Z')
        make_cyl(f"Ketchup_Cap_{i}",
                 (anchor[0] + kt_off[0], anchor[1] + kt_off[1], table_z + 0.17),
                 0.020, 0.025, (0.96, 0.94, 0.88, 1.0), segments=6, axis='Z')
        # Sugar caddy (glass jar with metal lid)
        sg_off = (long_axis_off(-0.08)[0] + short_axis_off(-0.10)[0],
                  long_axis_off(-0.08)[1] + short_axis_off(-0.10)[1])
        make_box(f"Sugar_Jar_{i}",
                 (anchor[0] + sg_off[0], anchor[1] + sg_off[1], table_z + 0.06),
                 (0.07, 0.07, 0.12), (0.92, 0.86, 0.68, 1.0))
        make_box(f"Sugar_Lid_{i}",
                 (anchor[0] + sg_off[0], anchor[1] + sg_off[1], table_z + 0.13),
                 (0.075, 0.075, 0.020), COL_BRASS)
        # Coffee cup on a saucer on the OTHER end of the table (suggests a seated diner)
        cup_long = long_axis_off(-0.22)
        cup_short = short_axis_off(+0.10)
        cup_x = anchor[0] - long_axis_off(anchor_long)[0] + cup_long[0] + cup_short[0]
        cup_y = anchor[1] - long_axis_off(anchor_long)[1] + cup_long[1] + cup_short[1]
        make_cyl(f"Saucer_{i}",
                 (cup_x, cup_y, table_z + 0.01),
                 0.07, 0.010, (0.96, 0.92, 0.84, 1.0), segments=10, axis='Z')
        make_cyl(f"CoffeeCup_{i}",
                 (cup_x, cup_y, table_z + 0.05),
                 0.040, 0.07, (0.96, 0.92, 0.84, 1.0), segments=8, axis='Z')
        # Coffee liquid (dark disc at cup top)
        make_cyl(f"CoffeeLiquid_{i}",
                 (cup_x, cup_y, table_z + 0.085),
                 0.034, 0.004, (0.18, 0.10, 0.06, 1.0), segments=8, axis='Z')


def build_wall_decor():
    """Wall clock + framed photos + neon sign. Things players see
    looking AT the walls while walking around."""
    # Wall clock — circular face on the north wall
    clock_cz = D_H - 0.80
    clock_cy = D_D/2 - 0.18
    # Outer round bezel (cylinder pressed against wall)
    make_cyl("WallClock_Bezel",
             (0, clock_cy, clock_cz),
             0.42, 0.10, COL_PHOTO_FRAME,
             segments=24, axis='Y')
    # Face (lighter cylinder slightly forward)
    make_cyl("WallClock_Face",
             (0, clock_cy - 0.04, clock_cz),
             0.36, 0.03, COL_CLOCK_FACE,
             segments=24, axis='Y')
    # 12 hour-marker pips around the face (small dark boxes)
    import math as _cm
    for h in range(12):
        ang = _cm.radians(90 - h * 30)
        mx = _cm.cos(ang) * 0.30
        mz = _cm.sin(ang) * 0.30
        # Major pips at 12, 3, 6, 9; minor for others
        is_major = (h % 3 == 0)
        size_h = 0.06 if is_major else 0.03
        thick = 0.025 if is_major else 0.018
        make_box(f"WallClock_Pip_{h}",
                 (mx, clock_cy - 0.06, clock_cz + mz),
                 (thick, 0.02, size_h),
                 (0.18, 0.16, 0.14, 1.0))
    # Hands set to 3:47 — minute hand at +47min angle (just past 9),
    # hour hand between 3 and 4 (about 3.78/12 around).
    minute_ang = _cm.radians(90 - 47 * 6)        # -192°
    hour_ang   = _cm.radians(90 - (3 + 47/60) * 30)  # -23° approx
    # Minute hand (longer, thinner)
    mh_x = _cm.cos(minute_ang) * 0.16
    mh_z = _cm.sin(minute_ang) * 0.16
    make_box("WallClock_MinuteHand",
             (mh_x, clock_cy - 0.07, clock_cz + mh_z),
             (0.32, 0.018, 0.03),
             (0.18, 0.16, 0.14, 1.0))
    # Hour hand (shorter, thicker)
    hh_x = _cm.cos(hour_ang) * 0.10
    hh_z = _cm.sin(hour_ang) * 0.10
    make_box("WallClock_HourHand",
             (hh_x, clock_cy - 0.075, clock_cz + hh_z),
             (0.20, 0.024, 0.04),
             (0.18, 0.16, 0.14, 1.0))
    # Center hub
    make_cyl("WallClock_Hub",
             (0, clock_cy - 0.08, clock_cz),
             0.04, 0.02, COL_BRASS,
             segments=8, axis='Y')
    # Framed photos along the SOUTH wall, above the booth/seating zone
    # (high enough that booths and people don't occlude them)
    for i in range(5):
        fx = -6.0 + i * 3.0
        # Frame
        make_box(f"WallPhoto_Frame_{i}",
                 (fx, -D_D/2 + 0.08, 2.80),
                 (0.55, 0.04, 0.42), COL_PHOTO_FRAME)
        make_box(f"WallPhoto_Image_{i}",
                 (fx, -D_D/2 + 0.05, 2.80),
                 (0.45, 0.02, 0.34), COL_NAPKIN)
    # Neon "OPEN" sign in the front window (south, parking-lot side)
    make_box("NeonOpenSign",
             (+5.0, D_D/2 - 0.10, 2.30),
             (1.20, 0.06, 0.45), (0.95, 0.32, 0.62, 1.0))
    # Chalkboard daily-specials sign on the south wall, next to the entry
    make_box("Chalkboard_Frame",
             (D_W/2 - 4.5, -D_D/2 + 0.08, 1.70),
             (1.40, 0.05, 0.90), COL_WOOD_TRIM)
    make_box("Chalkboard_Slate",
             (D_W/2 - 4.5, -D_D/2 + 0.05, 1.70),
             (1.28, 0.02, 0.78), (0.10, 0.12, 0.10, 1.0))
    # A few chalk-line streaks (suggestion of writing)
    for i in range(4):
        line_z = 1.95 - i * 0.16
        line_w = 0.85 - i * 0.10
        make_box(f"Chalkboard_Line_{i}",
                 (D_W/2 - 4.7, -D_D/2 + 0.03, line_z),
                 (line_w, 0.005, 0.025),
                 (0.86, 0.86, 0.80, 1.0))


def build_entry_props():
    """Hostess stand + coat rack INSIDE the vestibule, where the
    hostess routes patrons between three doors (main floor / bar /
    private dining)."""
    # Hostess podium central-east of the vestibule, slightly east of
    # the archway into the main floor, facing the front door.
    px, py = +7.6, -0.5
    make_box("HostessStand_Base", (px, py, 0.60),
             (0.50, 0.50, 1.20), COL_WOOD_TRIM)
    make_box("HostessStand_Top", (px, py, 1.24),
             (0.56, 0.56, 0.08), (0.50, 0.36, 0.22, 1.0))
    # Menu stack
    make_box("Menus_Stack", (px + 0.12, py - 0.10, 1.30),
             (0.20, 0.12, 0.10), COL_VINYL_RED)
    # Reservation book on the podium (open, with a pen across it)
    make_box("Reservation_Book", (px - 0.10, py + 0.05, 1.30),
             (0.24, 0.18, 0.03), (0.32, 0.18, 0.10, 1.0))
    make_box("Reservation_Book_Pages",
             (px - 0.10, py + 0.05, 1.318),
             (0.22, 0.16, 0.005), COL_NAPKIN)
    make_cyl("Reservation_Pen",
             (px - 0.05, py + 0.10, 1.330),
             0.005, 0.13, COL_BRASS, segments=4, axis='X')
    # Pen cup
    make_cyl("Pen_Cup", (px + 0.18, py + 0.18, 1.32),
             0.030, 0.07, COL_BRASS, segments=6, axis='Z')
    # Three small brass signs on the podium edge — pointing patrons
    # to the three rooms
    for i, (label, lx_off, ly_off) in enumerate([
        ("Sign_MainDining", -0.20, -0.20),
        ("Sign_Bar",        +0.00, -0.20),
        ("Sign_PrivDining", +0.20, -0.20),
    ]):
        make_box(label,
                 (px + lx_off, py + ly_off, 1.30),
                 (0.12, 0.01, 0.05), COL_BRASS)
    # Small banker's lamp on the podium (warm pool of light)
    lamp_x, lamp_y = px - 0.18, py - 0.18
    make_box("HostessLamp_Base",
             (lamp_x, lamp_y, 1.30),
             (0.10, 0.10, 0.04), COL_BRASS)
    make_cyl("HostessLamp_Post",
             (lamp_x, lamp_y, 1.40),
             0.014, 0.20, COL_BRASS, segments=4, axis='Z')
    make_box("HostessLamp_Shade",
             (lamp_x, lamp_y - 0.08, 1.50),
             (0.20, 0.16, 0.06),
             (0.30, 0.42, 0.22, 1.0))   # green banker's shade

    # Coat rack just inside the front door, in the vestibule SE
    cr_x, cr_y = D_W/2 - 0.7, -1.5
    make_box("CoatRack_Pole", (cr_x, cr_y, 0.95),
             (0.06, 0.06, 1.90), COL_WOOD_TRIM)
    make_box("CoatRack_Base", (cr_x, cr_y, 0.03),
             (0.50, 0.50, 0.06), COL_WOOD_TRIM)
    for h in range(4):
        ang = h * 1.5708
        import math as _m
        hx = cr_x + 0.20 * _m.cos(ang)
        hy = cr_y + 0.20 * _m.sin(ang)
        make_box(f"CoatHook_{h}", (hx, hy, 1.78),
                 (0.04, 0.04, 0.12), COL_BRASS)
    make_box("Jacket_Draped",
             (cr_x + 0.18, cr_y, 1.40),
             (0.22, 0.06, 0.50), (0.32, 0.40, 0.52, 1.0))


def build_bald_cypress(name_prefix, cx, cy, base_z=0.0, height=3.5,
                       canopy_color=(0.30, 0.38, 0.22, 1.0),
                       trunk_color=(0.32, 0.26, 0.16, 1.0),
                       moss_color=(0.55, 0.52, 0.36, 1.0),
                       with_knees=True, with_moss=True):
    """Bald-cypress tree port from build_riverfront.py.

    Anatomy: 3-segment tapered trunk + 4-sphere overlapping canopy +
    radiating knees at the base + Spanish moss curtains.
    Used to populate the river view through the diner window."""
    # Trunk: 3 cylinders, each taller and skinnier
    tr_segs = [
        (0.16, 0.50),
        (0.13, 0.50 + height * 0.30),
        (0.10, 0.50 + height * 0.60),
    ]
    cum_h = base_z
    for s_i, (r, seg_h) in enumerate(tr_segs):
        if s_i == 0:
            seg_len = seg_h
        else:
            seg_len = seg_h - tr_segs[s_i - 1][1]
        z_center = cum_h + seg_len / 2.0
        make_cyl(f"{name_prefix}_trunk_{s_i}",
                 (cx, cy, z_center),
                 r, seg_len, trunk_color, segments=6, axis='Z')
        cum_h += seg_len
    # Canopy: 4 overlapping spheres
    canopy_z = base_z + height * 0.70
    for s_i, (ox, oy, oz, r) in enumerate([
        ( 0.0,  0.0, +0.10, 0.95),
        (+0.45, +0.10, -0.05, 0.65),
        (-0.30, +0.30, +0.20, 0.55),
        (+0.10, -0.40, -0.10, 0.55),
    ]):
        make_sphere_low(f"{name_prefix}_canopy_{s_i}",
                        (cx + ox, cy + oy, canopy_z + oz),
                        r, canopy_color, rings=3, segments=8)
    # Knees: 5 small cylinders radiating around the base
    if with_knees:
        for k in range(5):
            ang = math.radians(k * 72 + 18)
            kx = cx + 0.50 * math.cos(ang)
            ky = cy + 0.50 * math.sin(ang)
            kh = 0.18 + 0.06 * ((k * 7) % 4)
            make_cyl(f"{name_prefix}_knee_{k}",
                     (kx, ky, base_z + kh / 2.0),
                     0.06, kh, trunk_color, segments=4, axis='Z')
    # Spanish moss curtains: thin tall boxes dangling from the canopy
    if with_moss:
        for m in range(3):
            ang = math.radians(m * 110)
            mx = cx + 0.55 * math.cos(ang)
            my = cy + 0.55 * math.sin(ang)
            make_box(f"{name_prefix}_moss_{m}",
                     (mx, my, canopy_z - 0.30),
                     (0.06, 0.04, 0.80), moss_color)


def build_enhanced_river_view():
    """Detailed bayou-river view visible through the diner's river
    window — ported from the riverfront scene's `build_river` /
    `build_opposite_shore` / `build_bayou` so the diner and the
    riverfront look out on the SAME water.

    Layout (all WEST of the diner, all visible through the river
    window at X=-9):
      · NEAR water + foreground reeds + lily pads + cattails
      · MID river surface with current-line ripples + a passing skiff
      · FAR shore strip with mud bank + reed line + cane field
      · Cypress cluster on the far shore (with knees + Spanish moss)
      · DISTANT industrial silhouette behind cypress
    """
    # Water levels and X distances (all relative to wall at X=-9)
    river_top_z = -2.0           # water surface ~2m below diner floor
    porch_edge_x = -D_W/2 - 2.4   # the porch ends here (built earlier)
    near_bank_x  = porch_edge_x - 0.3   # just past porch
    mid_river_x  = -D_W/2 - 22.0
    far_bank_x   = -D_W/2 - 45.0
    cane_x       = -D_W/2 - 50.0
    distant_x    = -D_W/2 - 70.0

    # ── MAIN water surface (warm muddy gulf-coast blue per riverfront canon) ──
    make_box("RV_Water_Main",
             (mid_river_x, 0, river_top_z),
             (50.0, 80.0, 0.10),
             (0.28, 0.40, 0.50, 1.0))
    # River bed visible at the edges (darker muddy stripe)
    make_box("RV_RiverBed",
             (mid_river_x, 0, river_top_z - 0.10),
             (50.0, 80.0, 0.10),
             (0.30, 0.26, 0.18, 1.0))
    # Current-line ripples (thin darker stripes parallel to current)
    for w in range(8):
        wy = -30 + w * 8
        make_box(f"RV_Ripple_{w}",
                 (mid_river_x, wy, river_top_z + 0.06),
                 (50.0, 0.30, 0.02),
                 (0.18, 0.28, 0.36, 1.0))
    # ── NEAR-BANK foreground: mud strip + reeds + cattails + lily pads ──
    make_box("RV_NearBank_Mud",
             (near_bank_x - 0.5, 0, river_top_z + 0.06),
             (1.0, 80.0, 0.02),
             (0.30, 0.22, 0.14, 1.0))
    # Reed clumps in the shallows
    for r in range(14):
        ry = -7 + r * 1.1
        rx = near_bank_x - 0.6 - (r % 3) * 0.4
        # 3 thin tall blades per clump
        for blade in range(3):
            bx = rx + (blade - 1) * 0.06
            bz = river_top_z + 0.10 + 0.50 + (blade * 0.07)
            make_box(f"RV_Reed_{r}_{blade}",
                     (bx, ry + (blade - 1) * 0.05, bz),
                     (0.018, 0.018, 0.70 + blade * 0.06),
                     (0.42, 0.46, 0.22, 1.0))
        # Cattail head (small brown cylinder on top of one blade)
        if r % 3 == 0:
            make_cyl(f"RV_Cattail_{r}",
                     (rx, ry, river_top_z + 1.10),
                     0.022, 0.14,
                     (0.42, 0.26, 0.14, 1.0), segments=6, axis='Z')
    # Lily pads (flat discs floating on the water)
    for l in range(7):
        lx = near_bank_x - 1.6 - (l % 3) * 0.4
        ly = -4 + l * 1.4
        make_cyl(f"RV_LilyPad_{l}",
                 (lx, ly, river_top_z + 0.06),
                 0.32, 0.012,
                 (0.30, 0.42, 0.22, 1.0), segments=8, axis='Z')
        # Occasional flower (small white sphere)
        if l % 3 == 1:
            make_sphere_low(f"RV_LilyFlower_{l}",
                            (lx + 0.05, ly + 0.05, river_top_z + 0.10),
                            0.07,
                            (0.94, 0.92, 0.84, 1.0),
                            rings=2, segments=6)
    # ── MID-RIVER drifting elements ──
    # A passing skiff with a figure-silhouette poling it (suggestion)
    skiff_x = mid_river_x + 4.0
    skiff_y = +6.0
    make_box("RV_PassingSkiff_Hull",
             (skiff_x, skiff_y, river_top_z + 0.20),
             (1.4, 3.6, 0.32),
             (0.30, 0.20, 0.14, 1.0))
    make_box("RV_PassingSkiff_Bench",
             (skiff_x, skiff_y + 0.4, river_top_z + 0.42),
             (1.0, 0.20, 0.10),
             (0.42, 0.28, 0.18, 1.0))
    # Pole figure
    make_cyl("RV_PassingSkiff_Pole",
             (skiff_x, skiff_y - 0.4, river_top_z + 1.0),
             0.018, 2.8,
             (0.30, 0.22, 0.14, 1.0), segments=4, axis='Z')
    # A piece of driftwood
    make_box("RV_Driftwood_A",
             (mid_river_x - 4, -3, river_top_z + 0.05),
             (1.8, 0.12, 0.06),
             (0.20, 0.14, 0.08, 1.0))
    make_box("RV_Driftwood_B",
             (mid_river_x + 6, +2, river_top_z + 0.05),
             (1.2, 0.10, 0.06),
             (0.18, 0.12, 0.06, 1.0))
    # ── FAR SHORE mud bank ──
    make_box("RV_FarBank_Mud",
             (far_bank_x, 0, river_top_z + 0.30),
             (3.0, 80.0, 0.50),
             (0.32, 0.22, 0.14, 1.0))
    # Reed line on the far bank (a strip of vertical short boxes)
    for r in range(20):
        ry = -22 + r * 2.3
        make_box(f"RV_FarReed_{r}",
                 (far_bank_x + 1.4, ry, river_top_z + 1.0),
                 (0.20, 0.12, 1.20),
                 (0.36, 0.40, 0.20, 1.0))
    # ── CYPRESS CLUSTER on the far shore ──
    cypress_specs = [
        (far_bank_x - 0.5, -14,  4.0),
        (far_bank_x - 1.2,  -8,  4.5),
        (far_bank_x + 0.8,  -2,  3.5),
        (far_bank_x - 0.8,  +3,  4.8),
        (far_bank_x + 0.2,  +9,  3.8),
        (far_bank_x - 1.4, +15,  4.2),
        (far_bank_x + 1.0, +20,  3.4),
    ]
    for i, (tx, ty, th) in enumerate(cypress_specs):
        build_bald_cypress(
            f"RV_Cypress_{i}",
            tx, ty, base_z=river_top_z + 0.50,
            height=th,
            canopy_color=(0.30, 0.38, 0.22, 1.0),
            trunk_color=(0.30, 0.24, 0.16, 1.0),
            moss_color=(0.55, 0.52, 0.36, 1.0),
            with_knees=True, with_moss=True,
        )
    # ── CANE FIELD strip behind the cypress ──
    for c in range(40):
        cy_c = -22 + c * 1.2
        # Two cane stalks per slot, slightly varied
        make_box(f"RV_Cane_A_{c}",
                 (cane_x, cy_c, river_top_z + 1.6),
                 (0.06, 0.06, 2.4),
                 (0.38, 0.42, 0.22, 1.0))
        make_box(f"RV_Cane_B_{c}",
                 (cane_x + 0.12, cy_c + 0.06, river_top_z + 1.5),
                 (0.05, 0.05, 2.2),
                 (0.36, 0.40, 0.20, 1.0))
    # ── DISTANT industrial silhouette ──
    # A refinery / warehouse outline far back
    make_box("RV_Distant_Warehouse",
             (distant_x, -8, river_top_z + 2.5),
             (4.0, 14.0, 4.0),
             (0.18, 0.16, 0.14, 1.0))
    # Two stack chimneys
    make_box("RV_Distant_Stack_A",
             (distant_x + 1.5, -4, river_top_z + 5.5),
             (0.50, 0.50, 5.0),
             (0.14, 0.12, 0.10, 1.0))
    make_box("RV_Distant_Stack_B",
             (distant_x + 1.5, -8, river_top_z + 5.5),
             (0.50, 0.50, 4.5),
             (0.14, 0.12, 0.10, 1.0))
    # Distant refinery (a horizontal rectangular silhouette with a few towers)
    make_box("RV_Distant_Refinery",
             (distant_x + 2.0, +6, river_top_z + 2.0),
             (3.0, 10.0, 3.5),
             (0.20, 0.16, 0.14, 1.0))
    for t in range(3):
        ty = +2 + t * 3
        make_box(f"RV_Distant_Tower_{t}",
                 (distant_x + 2.0, ty, river_top_z + 5.0),
                 (0.30, 0.30, 4.0),
                 (0.16, 0.14, 0.12, 1.0))


def build_gauntlet_decor():
    """Tarot Gauntlet flavor scattered through the diner so the
    space reads as canonical to the card game even with no
    interactive overlay yet.

    Per _TAROT_GAUNTLET_SCENARIOS: D'Ambrosio's IS the Fool location.
    Set decoration only — game logic lives in script, not geometry.
    """
    # ── Tarot card stack on the counter, near the order spike ──
    cy = -3.5
    counter_top_z = 1.05
    spike_x = -1.5
    deck_x = spike_x - 0.50
    # The deck of cards (a small box stack)
    make_box("Gauntlet_DeckBase",
             (deck_x, cy + 0.10, counter_top_z + 0.08),
             (0.12, 0.18, 0.06), COL_CARD_PAPER)
    # 3 cards fanned out beside the deck (face up)
    fan_cards = [
        (deck_x + 0.18, cy + 0.06, COL_CARD_PAPER),
        (deck_x + 0.32, cy + 0.14, COL_CARD_PINK),
        (deck_x + 0.42, cy + 0.20, COL_CARD_GREEN),
    ]
    for i, (fx, fy, col) in enumerate(fan_cards):
        make_box(f"Gauntlet_FanCard_{i}",
                 (fx, fy, counter_top_z + 0.022),
                 (0.10, 0.16, 0.004), col)
        # Sigil dot on each card
        make_box(f"Gauntlet_FanCard_{i}_Sigil",
                 (fx, fy, counter_top_z + 0.025),
                 (0.03, 0.04, 0.002), COL_BRASS)
    # A patron-left coffee cup beside the cards (suggests a player
    # mid-game)
    make_cyl("Gauntlet_PatronCup_Saucer",
             (deck_x - 0.20, cy + 0.18, counter_top_z + 0.015),
             0.08, 0.012, COL_NAPKIN, segments=10, axis='Z')
    make_cyl("Gauntlet_PatronCup_Body",
             (deck_x - 0.20, cy + 0.18, counter_top_z + 0.06),
             0.045, 0.08, COL_NAPKIN, segments=8, axis='Z')
    make_cyl("Gauntlet_PatronCup_Coffee",
             (deck_x - 0.20, cy + 0.18, counter_top_z + 0.10),
             0.040, 0.004, (0.18, 0.10, 0.06, 1.0), segments=8, axis='Z')
    # ── Tarot-print framed prints on the south wall (between the
    # existing photos) ──
    arcana_specs = [
        # (x, color_dark, color_accent) — each suggests a different arcana
        (-7.5, COL_VINYL_RED, COL_BRASS),     # Fool
        (-1.5, COL_PAYPHONE_DARK, COL_BRASS), # Magician
        (+3.5, COL_VINYL_RED, COL_PHOTO_FRAME), # Hierophant
    ]
    for i, (px, base, accent) in enumerate(arcana_specs):
        # Frame
        make_box(f"Gauntlet_ArcanaFrame_{i}",
                 (px, -D_D/2 + 0.10, 1.40),
                 (0.40, 0.04, 0.62), COL_PHOTO_FRAME)
        # Card field (the card itself — same proportions as a real tarot)
        make_box(f"Gauntlet_ArcanaCard_{i}",
                 (px, -D_D/2 + 0.07, 1.40),
                 (0.32, 0.02, 0.54), COL_CARD_PAPER)
        # Brass arcana sigil at the top
        make_box(f"Gauntlet_ArcanaSigil_{i}",
                 (px, -D_D/2 + 0.06, 1.56),
                 (0.10, 0.005, 0.10), accent)
        # Title strip at the bottom
        make_box(f"Gauntlet_ArcanaTitle_{i}",
                 (px, -D_D/2 + 0.06, 1.20),
                 (0.26, 0.005, 0.04), base)
    # ── A small "Now Playing" gauntlet-themed chalkboard near the
    # hostess stand (in the vestibule), listing house rules ──
    cb_x, cb_y = +6.5, +0.7
    make_box("Gauntlet_HouseRules_Frame",
             (cb_x, cb_y, 1.90),
             (0.50, 0.04, 0.70), COL_WOOD_TRIM)
    make_box("Gauntlet_HouseRules_Slate",
             (cb_x, cb_y + 0.025, 1.90),
             (0.42, 0.005, 0.60),
             (0.10, 0.12, 0.10, 1.0))
    # 5 chalk lines (suggesting handwritten gauntlet rules)
    for i in range(5):
        line_z = 2.10 - i * 0.10
        line_w = 0.32 - (i % 2) * 0.08
        make_box(f"Gauntlet_HouseRules_Line_{i}",
                 (cb_x - 0.04, cb_y + 0.029, line_z),
                 (line_w, 0.003, 0.016),
                 (0.92, 0.90, 0.84, 1.0))
    # ── Visitor-meeple-like figurine collection on a small shelf
    # near the cardwall ──
    sh_x, sh_y, sh_z = +1.5, D_D/2 + 1.0, 1.60
    make_box("Gauntlet_VisitorShelf",
             (sh_x, sh_y, sh_z),
             (1.20, 0.20, 0.025), COL_WOOD_TRIM)
    # 7 meeples (small humanoid shapes)
    meeple_colors = [
        COL_VINYL_RED, COL_BRASS, COL_CARD_PINK,
        COL_CARD_GREEN, COL_PHOTO_FRAME, COL_PAYPHONE_DARK,
        (0.42, 0.32, 0.18, 1.0),
    ]
    for m in range(7):
        mx = sh_x - 0.50 + m * 0.16
        # Body (small box)
        make_box(f"Gauntlet_Meeple_{m}_Body",
                 (mx, sh_y, sh_z + 0.07),
                 (0.05, 0.05, 0.10), meeple_colors[m])
        # Head (smaller box on top)
        make_box(f"Gauntlet_Meeple_{m}_Head",
                 (mx, sh_y, sh_z + 0.15),
                 (0.04, 0.04, 0.04), meeple_colors[m])
    # ── A dice cup (with 2 dice spilling out) on the hostess podium ──
    px, py = +7.6, -0.5    # matches hostess stand
    make_cyl("Gauntlet_DiceCup",
             (px - 0.20, py + 0.05, 1.30),
             0.045, 0.10, COL_BAR_WOOD, segments=8, axis='Z')
    make_box("Gauntlet_Die1",
             (px - 0.30, py + 0.10, 1.295),
             (0.04, 0.04, 0.04), COL_NAPKIN)
    make_box("Gauntlet_Die2",
             (px - 0.10, py - 0.05, 1.295),
             (0.04, 0.04, 0.04), COL_NAPKIN)
    # Dice pips (a couple of dark dots on top)
    make_box("Gauntlet_Die1_Pip",
             (px - 0.30, py + 0.10, 1.316),
             (0.012, 0.012, 0.002), COL_PAYPHONE_DARK)
    make_box("Gauntlet_Die2_Pip",
             (px - 0.10, py - 0.05, 1.316),
             (0.012, 0.012, 0.002), COL_PAYPHONE_DARK)


def build_exterior_hints():
    """Steamboat exterior visible through the river-side window
    (-X) + parking-lot exterior visible through the east windows
    (+X). The player looking out of either window should see a
    real-feeling outside.

    Per _VOL5_WIKI canon: 'weathered diner complex moored on the
    river bank — white clapboard exterior, brass rails, a
    wraparound porch over the water.'"""

    # ── WRAPAROUND STEAMBOAT PORCH (west / river side) ──
    porch_d = 2.4               # extends 2.4m out from the building
    porch_z = 0.0
    porch_y_center = 0.0
    # Main deck running the full N-S length, west of the building
    make_box("Porch_Deck_W",
             (-D_W/2 - porch_d/2, porch_y_center, porch_z),
             (porch_d, D_D, 0.08),
             (0.40, 0.30, 0.18, 1.0))
    # Deck plank seams (5 longitudinal stripes)
    for i in range(5):
        plank_y = -D_D/2 + (i + 0.5) * (D_D / 5)
        make_box(f"Porch_Plank_Seam_{i}",
                 (-D_W/2 - porch_d/2, plank_y, porch_z + 0.045),
                 (porch_d - 0.1, 0.025, 0.01),
                 (0.20, 0.14, 0.08, 1.0))
    # Wrap-around: short porch segments at N and S ends extending
    # past the building corners
    for side, sy in [("N", +D_D/2 + 0.5), ("S", -D_D/2 - 0.5)]:
        make_box(f"Porch_Deck_{side}",
                 (-D_W/2 - 0.5, sy, porch_z),
                 (porch_d + 1.0, 1.0, 0.08),
                 (0.40, 0.30, 0.18, 1.0))
    # ── BRASS RAILING along the porch outer edge ──
    rail_x = -D_W/2 - porch_d + 0.05
    # Top rail (long horizontal cylinder)
    make_cyl("Porch_Rail_Top",
             (rail_x, 0, 0.95),
             0.035, D_D + 1.5, COL_BRASS,
             segments=8, axis='Y')
    # Mid rail
    make_cyl("Porch_Rail_Mid",
             (rail_x, 0, 0.55),
             0.025, D_D + 1.5, COL_BRASS,
             segments=8, axis='Y')
    # Posts every 1.5m
    n_posts = int((D_D + 1.5) / 1.5)
    for i in range(n_posts + 1):
        py = -(D_D + 1.5)/2 + i * (D_D + 1.5) / n_posts
        make_cyl(f"Porch_Rail_Post_{i}",
                 (rail_x, py, 0.50),
                 0.04, 1.05, COL_BRASS,
                 segments=6, axis='Z')
    # ── DOCK CLEAT (mooring point on the porch edge) ──
    # The river surface + far-bank + cypress + cane fields are now
    # built by build_enhanced_river_view() (a riverfront-quality view).
    # The porch's moored-skiff lives here so it's anchored to the porch
    # geometry rather than the river surface.
    river_top_z = -2.0
    boat_cx, boat_cy = -D_W/2 - 3.5, -1.5
    make_box("Moored_Skiff_Hull",
             (boat_cx, boat_cy, river_top_z + 0.30),
             (1.6, 4.0, 0.50),
             (0.36, 0.24, 0.16, 1.0))
    make_box("Moored_Skiff_Bench",
             (boat_cx, boat_cy + 0.5, river_top_z + 0.65),
             (1.2, 0.20, 0.12),
             (0.46, 0.32, 0.22, 1.0))
    make_cyl("Porch_Cleat",
             (rail_x + 0.10, -2.0, 0.10),
             0.06, 0.30, COL_BRASS,
             segments=6, axis='X')
    # ── PARKING LOT (east side) — kept minimal, sodium light pole ──
    make_cyl("Sodium_Pole",
             (D_W/2 + 4.0, -D_D/2 - 1.0, 3.0),
             0.06, 6.0, (0.20, 0.18, 0.14, 1.0),
             segments=6, axis='Z')
    # Sodium fixture (curved horizontal head)
    make_box("Sodium_Fixture_Arm",
             (D_W/2 + 3.0, -D_D/2 - 1.0, 5.7),
             (2.0, 0.10, 0.10),
             (0.20, 0.18, 0.14, 1.0))
    make_box("Sodium_Fixture_Head",
             (D_W/2 + 2.0, -D_D/2 - 1.0, 5.5),
             (0.6, 0.4, 0.40),
             (0.92, 0.72, 0.34, 1.0))
    # Parking lot asphalt patch (visible through the south windows)
    make_box("Parking_Asphalt",
             (D_W/2 + 6.0, 0.0, 0.02),
             (10.0, D_D + 6.0, 0.04),
             (0.18, 0.18, 0.18, 1.0))
    # White parking stripes
    for p in range(6):
        sx = D_W/2 + 2.0 + p * 1.8
        make_box(f"Parking_Stripe_{p}",
                 (sx, 1.5, 0.05),
                 (0.10, 4.5, 0.02),
                 (0.86, 0.84, 0.78, 1.0))


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
    build_alcove_booths()
    build_freestanding_tables()
    build_table_dressings()
    build_kitchen_alcove()
    build_interior_partitions()
    build_bar_room()
    build_private_dining_room()
    build_storage_closet_and_bbs()
    build_back_hallway()
    build_ceiling_fans()
    build_wall_decor()
    build_entry_props()
    build_gauntlet_decor()
    build_enhanced_river_view()
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
