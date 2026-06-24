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
D_W = 18.0   # east-west — MAIN shell only. The portside (west)
             # extension lives outside this and adds WEST_EXT_W more.
D_D = 12.0   # north-south
D_H = 3.4    # ceiling height
WEST_EXT_W = 6.0   # portside extension width (X=-15..-9)
WEST_EXT_DOOR_W = 2.0   # opening from main floor → west extension corridor

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
    """Floor, ceiling, four walls. Big picture windows running flush
    along the whole west and east walls, with only a small solid
    margin at each end. NO solid glass slab in the opening — the
    window is just an empty cutout so the player sees straight through
    to the bayou view.

    Per user direction: "the windows in the diner need to be larger,
    more picture-window, running flush with the whole wall except
    maybe a few feet at each end. the windows need to be able to see
    through to the outside, not be solid material."
    """
    # floor
    make_box("Floor", (0, 0, -0.05), (D_W, D_D, 0.10), COL_FLOOR_TILE, open_faces={'-Z'})
    # ceiling
    make_box("Ceiling", (0, 0, D_H + 0.05), (D_W, D_D, 0.10), COL_CEILING, open_faces={'+Z'})

    # ── WEST wall of MAIN shell (X=-9) — now an INTERIOR partition
    # between the main floor and the new portside extension. Two
    # door openings:
    #   1) Y=+5  (1.6m) → main floor → bar in the extension's NW
    #   2) Y=-3.25 (1.4m) → formal hallway → formal dining in the
    #      extension's SW  (per the L-hallway design)
    door1_y, door1_w = +5.0, 1.6
    door2_y, door2_w = -3.25, 1.4
    door_h = 2.20
    # Segments along X=-9 from south to north:
    #   -6.0 .. door2_y-w/2   (S of formal-dining door)
    #   door2_y-w/2 .. door2_y+w/2  (door 2)
    #   door2_y+w/2 .. door1_y-w/2  (between doors)
    #   door1_y-w/2 .. door1_y+w/2  (door 1)
    #   door1_y+w/2 .. +6.0   (N of bar door)
    breaks_w = [
        (-D_D/2,                 door2_y - door2_w/2,  "Wall_W_seg_SS"),
        (door2_y + door2_w/2,    door1_y - door1_w/2,  "Wall_W_seg_mid"),
        (door1_y + door1_w/2,    +D_D/2,               "Wall_W_seg_NN"),
    ]
    for y_lo, y_hi, name in breaks_w:
        seg_len = y_hi - y_lo
        if seg_len < 0.02:
            continue
        make_box(name,
                 (-D_W/2 - 0.05, (y_lo + y_hi) / 2, D_H/2),
                 (0.10, seg_len, D_H), COL_WALL_INTERIOR)
    # Lintels above both doors
    for door_y, door_w_v, suffix in [(door1_y, door1_w, "bar"),
                                       (door2_y, door2_w, "formal")]:
        make_box(f"Wall_W_doorLintel_{suffix}",
                 (-D_W/2 - 0.05, door_y, door_h + (D_H - door_h)/2),
                 (0.10, door_w_v, D_H - door_h), COL_WALL_INTERIOR)
        # Door frame jambs + header
        for sgn in (-1, +1):
            make_box(f"Wall_W_doorJamb_{suffix}_{sgn:+d}",
                     (-D_W/2 - 0.04, door_y + sgn * (door_w_v/2 + 0.025),
                      door_h/2),
                     (0.06, 0.05, door_h), COL_WOOD_TRIM)
        make_box(f"Wall_W_doorHeader_{suffix}",
                 (-D_W/2 - 0.04, door_y, door_h + 0.06),
                 (0.06, door_w_v + 0.20, 0.10), COL_WOOD_TRIM)
    # Brass plaque "BAR" above the north door
    make_box("Wall_W_doorPlaque_BAR",
             (-D_W/2 - 0.03, door1_y, door_h + 0.20),
             (0.04, door1_w * 0.45, 0.10), COL_BRASS)
    # Brass plaque "FORMAL" above the south door
    make_box("Wall_W_doorPlaque_FORMAL",
             (-D_W/2 - 0.03, door2_y, door_h + 0.20),
             (0.04, door2_w * 0.70, 0.10), COL_BRASS)

    # ── EAST wall (parking-lot side) — front door + picture window ──
    door_w = 1.4
    door_h = 2.2
    # The east wall is partially occupied by the east-annex partition;
    # the main shell east wall faces parking. Window above the door
    # zone runs the full length of the wall except for end margins.
    e_win_w = 10.0
    e_win_h = 2.0
    e_win_base = 0.85
    e_upper_h = D_H - (e_win_base + e_win_h)
    e_side_d = (D_D - e_win_w) / 2
    # Lower (below window) — broken by the front door
    # South of door
    south_seg_y_lo = -D_D/2
    south_seg_y_hi = -door_w / 2 - 0.30
    south_seg_len = south_seg_y_hi - south_seg_y_lo
    make_box("Wall_E_lower_S",
             (D_W/2 + 0.05, (south_seg_y_lo + south_seg_y_hi) / 2,
              e_win_base / 2),
             (0.10, south_seg_len, e_win_base), COL_WALL_INTERIOR)
    # Below door (small sill)
    make_box("Wall_E_doorSill",
             (D_W/2 + 0.05, 0, 0.05),
             (0.10, door_w + 0.60, 0.10), COL_WOOD_TRIM)
    # North of door
    north_seg_y_lo = door_w / 2 + 0.30
    north_seg_y_hi = D_D/2
    north_seg_len = north_seg_y_hi - north_seg_y_lo
    make_box("Wall_E_lower_N",
             (D_W/2 + 0.05, (north_seg_y_lo + north_seg_y_hi) / 2,
              e_win_base / 2),
             (0.10, north_seg_len, e_win_base), COL_WALL_INTERIOR)
    # Wall above door (between door top and bottom of window)
    if door_h < e_win_base:
        # Door is shorter than window base — fill the gap
        make_box("Wall_E_above_door_fill",
                 (D_W/2 + 0.05, 0, (door_h + e_win_base) / 2),
                 (0.10, door_w + 0.60, e_win_base - door_h),
                 COL_WALL_INTERIOR)
    # Above the picture window
    make_box("Wall_E_above",
             (D_W/2 + 0.05, 0, e_win_base + e_win_h + e_upper_h / 2),
             (0.10, D_D, e_upper_h), COL_WALL_INTERIOR)
    # End-walls flanking the picture window
    make_box("Wall_E_S_of_window",
             (D_W/2 + 0.05, -D_D/2 + e_side_d / 2,
              e_win_base + e_win_h / 2),
             (0.10, e_side_d, e_win_h), COL_WALL_INTERIOR)
    make_box("Wall_E_N_of_window",
             (D_W/2 + 0.05, D_D/2 - e_side_d / 2,
              e_win_base + e_win_h / 2),
             (0.10, e_side_d, e_win_h), COL_WALL_INTERIOR)
    # Mullions + brass frame for the east picture window
    n_mull_v = 5
    for c in range(1, n_mull_v):
        mx_y = -e_win_w/2 + c * e_win_w / n_mull_v
        make_box(f"EastWindow_MullV_{c}",
                 (D_W/2 + 0.04, mx_y, e_win_base + e_win_h / 2),
                 (0.02, 0.06, e_win_h), COL_BRASS)
    make_box("EastWindow_MullH",
             (D_W/2 + 0.04, 0, e_win_base + e_win_h / 2),
             (0.02, e_win_w, 0.06), COL_BRASS)
    make_box("EastWindow_FrameT",
             (D_W/2 + 0.03, 0, e_win_base + e_win_h + 0.06),
             (0.04, e_win_w + 0.20, 0.12), COL_BRASS)
    make_box("EastWindow_FrameB",
             (D_W/2 + 0.03, 0, e_win_base - 0.06),
             (0.04, e_win_w + 0.20, 0.12), COL_BRASS)
    for sgn in (-1, +1):
        make_box(f"EastWindow_FrameSide_{sgn:+d}",
                 (D_W/2 + 0.03, sgn * (e_win_w/2 + 0.06),
                  e_win_base + e_win_h / 2),
                 (0.04, 0.12, e_win_h + 0.24), COL_BRASS)

    # ── NORTH wall — back-hallway opening (center) + bar-annex door
    #    (west of center, leads to the new port-side bar)
    bar_door_x = -6.0
    bar_door_w = 1.40
    # West-of-hall section: from X=-D_W/2 to X=-HALL_W/2, broken by
    # the bar door
    wn_W_x_W = -D_W/2
    wn_W_x_E = -HALL_W/2
    # West segment of the west wall (X=-D_W/2 to X=bar_door_x-bar_door_w/2)
    seg_W_len = (bar_door_x - bar_door_w/2) - wn_W_x_W
    make_box("Wall_N_segW_W",
             (wn_W_x_W + seg_W_len/2, D_D/2 + 0.05, D_H/2),
             (seg_W_len, 0.10, D_H), COL_WALL_INTERIOR)
    # East segment of the west wall (X=bar_door_x+bar_door_w/2 to X=-HALL_W/2)
    seg_E_len = wn_W_x_E - (bar_door_x + bar_door_w/2)
    make_box("Wall_N_segW_E",
             ((bar_door_x + bar_door_w/2) + seg_E_len/2,
              D_D/2 + 0.05, D_H/2),
             (seg_E_len, 0.10, D_H), COL_WALL_INTERIOR)
    # Lintel above bar door
    bar_door_h = 2.20
    make_box("Wall_N_BarDoor_Lintel",
             (bar_door_x, D_D/2 + 0.05,
              bar_door_h + (D_H - bar_door_h)/2),
             (bar_door_w, 0.10, D_H - bar_door_h), COL_WALL_INTERIOR)
    # East-of-hall section (X=+HALL_W/2 to X=+D_W/2)
    wn_E_x_W = HALL_W/2
    wn_E_x_E = D_W/2
    we_len = wn_E_x_E - wn_E_x_W
    make_box("Wall_N_segE",
             (wn_E_x_W + we_len/2, D_D/2 + 0.05, D_H/2),
             (we_len, 0.10, D_H), COL_WALL_INTERIOR)
    # Lintel above the hallway opening
    make_box("Wall_N_above_hall",
             (0, D_D/2 + 0.05, D_H - 0.5),
             (HALL_W, 0.10, 1.0), COL_WALL_INTERIOR)

    # ── SOUTH wall (porch side) ──
    make_box("Wall_S", (0, -D_D/2 - 0.05, D_H/2),
             (D_W, 0.10, D_H), COL_WALL_INTERIOR)


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


def build_the_leap_dressing():
    """Scene-description specifics from setup_the_leap.json that
    aren't covered by the generic shell / counter / booth builders.
    Always present in the GLB (a single GLB serves all 3 scenarios);
    reads as canonical John-Frank-at-3:47AM detail at any time of day.

    Things this adds:
      · The fluorescent over Booth_6 that "ticks like Morse code
        somebody almost remembers" — a distinct fixture above
        Booth_6 (north end of the alcove row, by=+3.75).
      · A small brass plaque on Booth_6's divider reading "BOOTH 6".
      · John Frank's rag draped over the counter edge at the
        canonical station, next to the wear spot.
      · An empty coffee mug + the ring it left on the formica
        beside the rag.
      · A small brass bell over the front door (so "tonight, for
        the first time, you can hear the door" reads as visible
        hardware).
    """
    # ── Booth_6 fluorescent fixture ──
    # Booth_6 is at by=+3.75 per the south→north alcove numbering.
    # Distinct from the diner-wide ceiling fans — a single dedicated
    # 4-foot tube over the booth's table.
    booth6_by = +3.75
    booth6_table_x = -D_W / 2 + 0.05 + 1.45 - 0.10 - 0.35  # mid of bench/table area
    fluor_z = D_H - 0.18
    # Housing
    make_box("Booth6_Fluor_Housing",
             (booth6_table_x, booth6_by, fluor_z),
             (1.10, 0.20, 0.10),
             (0.86, 0.86, 0.82, 1.0))
    # Tube — bright white-ish (reads as a cold fluorescent vs the
    # warmer counter lighting)
    make_cyl("Booth6_Fluor_Tube",
             (booth6_table_x, booth6_by, fluor_z - 0.06),
             0.022, 1.00,
             (0.96, 0.98, 0.92, 1.0),
             segments=8, axis='X')
    # End caps
    for sgn in (-1, +1):
        make_box("Booth6_Fluor_Cap_%+d" % sgn,
                 (booth6_table_x + sgn * 0.52, booth6_by, fluor_z - 0.06),
                 (0.03, 0.06, 0.06), COL_KITCHEN_STEEL)
    # ── Booth_6 brass plaque on the south divider ──
    # The divider south of Booth_6 (between Booth_5 and Booth_6) at
    # dy = +3.0 (booth_y_span midpoint). Plaque sits on the divider
    # at booth-eye level so a seated patron sees it from across the
    # table.
    plaque_x = -D_W / 2 + 0.10
    plaque_y = booth6_by - 0.74   # south face of the south divider
    make_box("Booth6_Plaque",
             (plaque_x + 0.04, plaque_y, 1.18),
             (0.06, 0.005, 0.10),
             COL_BRASS)
    # Tiny engraved "6" — a darker slot in the brass
    make_box("Booth6_Plaque_Numeral",
             (plaque_x + 0.04, plaque_y - 0.003, 1.18),
             (0.022, 0.005, 0.05),
             (0.18, 0.16, 0.12, 1.0))

    # ── John Frank's rag on the counter edge ──
    # Just patron-side of the wear spot, draped over the edge so a
    # corner hangs below the counter top.
    cy = -3.5
    counter_top_z = 1.10
    rag_x = -0.55
    rag_y = cy - 0.32   # at the patron edge of the counter
    make_box("JFRag_Top",
             (rag_x, rag_y + 0.02, counter_top_z + 0.012),
             (0.22, 0.14, 0.012),
             (0.74, 0.66, 0.42, 1.0))   # off-white linen, lightly stained
    # Folded corner draping below the edge (a thin tab on the south side)
    make_box("JFRag_Drape",
             (rag_x + 0.08, rag_y - 0.10, counter_top_z - 0.06),
             (0.10, 0.02, 0.14),
             (0.66, 0.58, 0.36, 1.0))

    # ── Empty coffee mug + the ring it left ──
    mug_x = -1.15
    mug_y = cy - 0.18
    # Mug body (a short squat cylinder · ceramic white-cream)
    make_cyl("CoffeeMug_Body",
             (mug_x, mug_y, counter_top_z + 0.055),
             0.045, 0.10,
             (0.94, 0.90, 0.82, 1.0),
             segments=10, axis='Z')
    # Mug rim (slightly wider, very thin · darker ceramic)
    make_cyl("CoffeeMug_Rim",
             (mug_x, mug_y, counter_top_z + 0.105),
             0.050, 0.008,
             (0.82, 0.76, 0.66, 1.0),
             segments=10, axis='Z')
    # Handle (small box on the south side)
    make_box("CoffeeMug_Handle",
             (mug_x, mug_y - 0.062, counter_top_z + 0.055),
             (0.018, 0.022, 0.052),
             (0.94, 0.90, 0.82, 1.0))
    # The ring it left — a thin darker circle on the formica next to
    # where the mug currently sits (the mug has been moved; the ring
    # remembers). Two concentric pancakes — outer (stained ring),
    # inner (cleaner where mug bottom blocked).
    ring_x = mug_x + 0.18
    ring_y = mug_y - 0.02
    make_cyl("CoffeeRing_Outer",
             (ring_x, ring_y, counter_top_z + 0.0008),
             0.048, 0.0008,
             (0.62, 0.52, 0.38, 1.0),
             segments=14, axis='Z')
    make_cyl("CoffeeRing_Inner",
             (ring_x, ring_y, counter_top_z + 0.0012),
             0.038, 0.0008,
             COL_FORMICA,
             segments=12, axis='Z')

    # ── Door bell over the front door (east annex, X≈+9, Y≈-1.5)
    # so the player "can hear the door." Brass shopkeeper bell on
    # a spring, mounted to the lintel.
    door_x = D_W / 2 - 0.10   # just inside the front door
    door_y = -1.5
    door_lintel_z = 2.05
    # Spring — a thin vertical brass coil-like cylinder
    make_cyl("DoorBell_Spring",
             (door_x, door_y, door_lintel_z - 0.06),
             0.012, 0.10, COL_BRASS,
             segments=4, axis='Z')
    # Bell body (a small dome — using a low-poly sphere)
    make_sphere_low("DoorBell_Body",
                    (door_x, door_y, door_lintel_z - 0.16),
                    0.045,
                    COL_BRASS, rings=2, segments=8)
    # Clapper (small box hanging just under the bell)
    make_box("DoorBell_Clapper",
             (door_x, door_y, door_lintel_z - 0.21),
             (0.012, 0.012, 0.040),
             (0.42, 0.32, 0.22, 1.0))


def build_jukebox(cx, cy, base_z=0.0):
    """A standing diner-style jukebox · the Wurlitzer-shaped silhouette
    referenced in setup_evening_service.json ("the jukebox skipping")
    and the host script SPACE_MAP 'jukebox' vantage at (-10.5, +5.0).
    Stands ~1.5m tall, faces SOUTH so the patron reads the marquee
    walking up from the bar room's south doorway.
    """
    # Base cabinet — wood with rounded shoulders. Three stacked boxes
    # of decreasing width fake the Wurlitzer shoulder curve.
    make_box("Jukebox_Base",
             (cx, cy, base_z + 0.20),
             (0.80, 0.50, 0.40), COL_WOOD_TRIM)
    make_box("Jukebox_Mid",
             (cx, cy, base_z + 0.60),
             (0.74, 0.46, 0.40), COL_WOOD_TRIM)
    make_box("Jukebox_Shoulder",
             (cx, cy, base_z + 0.95),
             (0.66, 0.42, 0.30), COL_WOOD_TRIM)
    # Glass marquee dome (lit, amber)
    make_box("Jukebox_Marquee",
             (cx, cy - 0.04, base_z + 1.22),
             (0.58, 0.34, 0.28),
             (0.96, 0.74, 0.42, 1.0))
    # Two coin-glow tube lights flanking the marquee (vapor-orange)
    for sgn in (-1, +1):
        make_cyl("Jukebox_Tube_%+d" % sgn,
                 (cx + sgn * 0.32, cy - 0.18, base_z + 1.22),
                 0.018, 0.36, (0.98, 0.62, 0.32, 1.0),
                 segments=6, axis='Z')
    # Selection-button panel (chrome strip across the front)
    make_box("Jukebox_ButtonStrip",
             (cx, cy - 0.255, base_z + 0.85),
             (0.50, 0.005, 0.10), COL_KITCHEN_STEEL)
    # Title-strip backer (cream paper under glass — read as the
    # printed track list when the player looks closely)
    make_box("Jukebox_TitleStrip",
             (cx, cy - 0.255, base_z + 0.72),
             (0.50, 0.005, 0.06),
             (0.92, 0.86, 0.72, 1.0))
    # Coin slot (small brass)
    make_box("Jukebox_CoinSlot",
             (cx + 0.22, cy - 0.255, base_z + 1.00),
             (0.06, 0.005, 0.04), COL_BRASS)


def build_west_extension():
    """The portside (west) extension — extends the building 6m further
    west to give the FORMAL DINING and the BAR proper port-side
    windows and a generous footprint. Plus a connecting corridor
    that opens into the main floor through a doorway in the old
    X=-9 wall.

    Per user direction: 'extend the whole portside wall out further.'

    Layout (X=-15..-9, Y=-6..+6):
        Y=+2..+6   →  Bar Room (port windows on the W wall)
        Y=-1..+2   →  Connecting corridor (door at the main-floor side
                       opens at Y≈+1; entry into bar/formal)
        Y=-6..-1   →  Formal Dining Room (port windows on the W wall)
    """
    EX_X_W = -D_W / 2 - WEST_EXT_W      # -15
    EX_X_E = -D_W / 2                    # -9
    EX_cx  = (EX_X_W + EX_X_E) / 2.0     # -12
    EX_d   = D_D                          # 12 (matches main shell)
    EX_cy  = 0.0

    # Floor + ceiling
    make_box("WestExt_Floor",
             (EX_cx, EX_cy, -0.05),
             (WEST_EXT_W, EX_d, 0.10),
             COL_FLOOR_TILE, open_faces={'-Z'})
    make_box("WestExt_Ceiling",
             (EX_cx, EX_cy, D_H + 0.05),
             (WEST_EXT_W, EX_d, 0.10),
             COL_CEILING, open_faces={'+Z'})
    # External flat roof slab — the riverboat superstructure rises
    # over the main shell only; this extension is a 1-story annex
    # with a tarred flat roof viewed from outside.
    make_box("WestExt_Roof_Exterior",
             (EX_cx, EX_cy, D_H + 0.15),
             (WEST_EXT_W + 0.20, EX_d + 0.20, 0.10),
             (0.20, 0.16, 0.12, 1.0))
    # Red trim cornice around the roof perimeter
    for label, x, y, sx, sy in [
        ("W", EX_X_W - 0.10, EX_cy, 0.06, EX_d + 0.20),
        ("N", EX_cx, EX_d/2 + 0.10, WEST_EXT_W + 0.20, 0.06),
        ("S", EX_cx, -EX_d/2 - 0.10, WEST_EXT_W + 0.20, 0.06),
    ]:
        make_box(f"WestExt_RoofTrim_{label}",
                 (x, y, D_H + 0.20),
                 (sx, sy, 0.18), (0.50, 0.20, 0.16, 1.0))

    # Floor accent (formal dining gets a dark hardwood floor; bar gets
    # a warm wood floor; corridor stays tile)
    make_box("WestExt_FormalFloor",
             (EX_cx, -3.5, 0.025),
             (WEST_EXT_W - 0.20, 4.8, 0.005),
             (0.18, 0.10, 0.06, 1.0))
    make_box("WestExt_BarFloor",
             (EX_cx, +4.0, 0.025),
             (WEST_EXT_W - 0.20, 3.8, 0.005),
             (0.32, 0.22, 0.14, 1.0))

    # ── NEW outer west wall (X=-15) — picture window facing river ──
    win_w = 10.0
    win_h = 2.5
    win_base = 0.85
    upper_h = D_H - (win_base + win_h)
    side_d = (EX_d - win_w) / 2
    make_box("WestExt_OuterWall_below",
             (EX_X_W - 0.05, EX_cy, win_base / 2),
             (0.10, EX_d, win_base), COL_WALL_INTERIOR)
    make_box("WestExt_OuterWall_above",
             (EX_X_W - 0.05, EX_cy,
              win_base + win_h + upper_h / 2),
             (0.10, EX_d, upper_h), COL_WALL_INTERIOR)
    make_box("WestExt_OuterWall_S",
             (EX_X_W - 0.05, -EX_d/2 + side_d / 2,
              win_base + win_h / 2),
             (0.10, side_d, win_h), COL_WALL_INTERIOR)
    make_box("WestExt_OuterWall_N",
             (EX_X_W - 0.05, +EX_d/2 - side_d / 2,
              win_base + win_h / 2),
             (0.10, side_d, win_h), COL_WALL_INTERIOR)
    # Picture-window brass mullions + frame (NO glass slab, per the
    # "see-through" lesson — leaving the opening empty so the bayou
    # geometry is visible directly)
    for c in range(1, 5):
        my = -win_w / 2 + c * win_w / 5
        make_box(f"WestExt_Win_MullV_{c}",
                 (EX_X_W - 0.04, my, win_base + win_h / 2),
                 (0.02, 0.06, win_h), COL_BRASS)
    make_box("WestExt_Win_MullH",
             (EX_X_W - 0.04, EX_cy, win_base + win_h / 2),
             (0.02, win_w, 0.06), COL_BRASS)
    make_box("WestExt_Win_FrameT",
             (EX_X_W - 0.03, EX_cy, win_base + win_h + 0.06),
             (0.04, win_w + 0.20, 0.12), COL_BRASS)
    make_box("WestExt_Win_FrameB",
             (EX_X_W - 0.03, EX_cy, win_base - 0.06),
             (0.04, win_w + 0.20, 0.12), COL_BRASS)
    for sgn in (-1, +1):
        make_box(f"WestExt_Win_FrameSide_{sgn:+d}",
                 (EX_X_W - 0.03, sgn * (win_w / 2 + 0.06),
                  win_base + win_h / 2),
                 (0.04, 0.12, win_h + 0.24), COL_BRASS)
    # Stone sill on the interior side of the picture window
    make_box("WestExt_Win_Sill",
             (EX_X_W + 0.18, EX_cy, win_base - 0.04),
             (0.36, win_w + 0.20, 0.08), (0.30, 0.20, 0.14, 1.0))

    # ── NORTH wall (Y=+6) of extension ──
    make_box("WestExt_NorthWall",
             (EX_cx, EX_d/2 + 0.05, D_H/2),
             (WEST_EXT_W + 0.20, 0.10, D_H), COL_WALL_INTERIOR)
    # ── SOUTH wall (Y=-6) of extension ──
    make_box("WestExt_SouthWall",
             (EX_cx, -EX_d/2 - 0.05, D_H/2),
             (WEST_EXT_W + 0.20, 0.10, D_H), COL_WALL_INTERIOR)

    # ── INTERNAL PARTITIONS inside the extension ──
    # Wall at Y=+2 separating bar (north) from corridor (south of bar)
    bar_part_door_x = EX_cx
    bar_part_door_w = 1.20
    bar_part_door_h = 2.20
    seg_w_len = (bar_part_door_x - bar_part_door_w/2) - EX_X_W
    seg_e_len = EX_X_E - (bar_part_door_x + bar_part_door_w/2)
    make_box("WestExt_BarPartition_W",
             (EX_X_W + seg_w_len/2, +2.0, D_H/2),
             (seg_w_len, 0.10, D_H), COL_WALL_INTERIOR)
    make_box("WestExt_BarPartition_E",
             (EX_X_E - seg_e_len/2, +2.0, D_H/2),
             (seg_e_len, 0.10, D_H), COL_WALL_INTERIOR)
    make_box("WestExt_BarPartition_lintel",
             (bar_part_door_x, +2.0,
              bar_part_door_h + (D_H - bar_part_door_h)/2),
             (bar_part_door_w, 0.10, D_H - bar_part_door_h),
             COL_WALL_INTERIOR)
    # Door frame
    for sgn in (-1, +1):
        make_box(f"WestExt_BarPartition_Jamb_{sgn:+d}",
                 (bar_part_door_x + sgn * (bar_part_door_w/2 + 0.025),
                  +2.0, bar_part_door_h/2),
                 (0.05, 0.14, bar_part_door_h), COL_WOOD_TRIM)
    make_box("WestExt_BarPartition_Header",
             (bar_part_door_x, +2.0, bar_part_door_h + 0.06),
             (bar_part_door_w + 0.20, 0.14, 0.10), COL_WOOD_TRIM)
    # Brass "BAR" sign above
    make_box("WestExt_BarPartition_Sign",
             (bar_part_door_x, +2.0 - 0.03, bar_part_door_h + 0.30),
             (0.60, 0.06, 0.16), COL_BAR_WOOD)
    for i, c in enumerate("BAR"):
        make_box(f"WestExt_BarSign_Char_{i}",
                 (bar_part_door_x + (i - 1) * 0.16, +2.0 - 0.04,
                  bar_part_door_h + 0.30),
                 (0.10, 0.005, 0.08), COL_BRASS)

    # Wall at Y=-1 separating corridor (north of it) from formal
    # dining (south of it)
    formal_part_door_x = EX_cx
    formal_part_door_w = 1.40
    formal_part_door_h = 2.20
    seg_w_len2 = (formal_part_door_x - formal_part_door_w/2) - EX_X_W
    seg_e_len2 = EX_X_E - (formal_part_door_x + formal_part_door_w/2)
    make_box("WestExt_FormalPartition_W",
             (EX_X_W + seg_w_len2/2, -1.0, D_H/2),
             (seg_w_len2, 0.10, D_H), COL_WALL_INTERIOR)
    make_box("WestExt_FormalPartition_E",
             (EX_X_E - seg_e_len2/2, -1.0, D_H/2),
             (seg_e_len2, 0.10, D_H), COL_WALL_INTERIOR)
    make_box("WestExt_FormalPartition_lintel",
             (formal_part_door_x, -1.0,
              formal_part_door_h + (D_H - formal_part_door_h)/2),
             (formal_part_door_w, 0.10, D_H - formal_part_door_h),
             COL_WALL_INTERIOR)
    for sgn in (-1, +1):
        make_box(f"WestExt_FormalPartition_Jamb_{sgn:+d}",
                 (formal_part_door_x + sgn * (formal_part_door_w/2 + 0.025),
                  -1.0, formal_part_door_h/2),
                 (0.05, 0.14, formal_part_door_h), COL_WOOD_TRIM)
    make_box("WestExt_FormalPartition_Header",
             (formal_part_door_x, -1.0, formal_part_door_h + 0.06),
             (formal_part_door_w + 0.20, 0.14, 0.10), COL_WOOD_TRIM)
    # Brass "FORMAL DINING" sign
    make_box("WestExt_FormalPartition_Sign",
             (formal_part_door_x, -1.0 - 0.03, formal_part_door_h + 0.30),
             (1.60, 0.06, 0.16), COL_BAR_WOOD)
    for i, c in enumerate("FORMAL"):
        make_box(f"WestExt_FormalSign_Char_{i}",
                 (formal_part_door_x + (i - 2.5) * 0.20,
                  -1.0 - 0.04, formal_part_door_h + 0.30),
                 (0.14, 0.005, 0.08), COL_BRASS)

    # ── BAR (NORTH section of extension, Y=+2..+6) ──
    # The bar runs E-W along the NORTH wall with bar stools on the
    # south (customer) side. Customers face north — the back-bar is
    # against the building's outer north wall.
    bar_top_z = 1.10
    bar_cy = +4.5
    bar_cx_int = EX_cx
    bar_len = WEST_EXT_W - 1.20    # 4.8m
    make_box("WestBar_Top", (bar_cx_int, bar_cy, bar_top_z),
             (bar_len, 0.70, 0.06), COL_BAR_WOOD)
    make_box("WestBar_Front",
             (bar_cx_int, bar_cy - 0.35, 0.55),
             (bar_len, 0.04, 1.10), COL_VINYL_RED_DK)
    make_cyl("WestBar_FootRail", (bar_cx_int, bar_cy - 0.36, 0.18),
             0.024, bar_len, COL_BRASS, segments=8, axis='X')
    # Back-bar cabinet against north wall
    bb_y = +5.7
    make_box("WestBar_BackCab",
             (bar_cx_int, bb_y, 0.65),
             (bar_len, 0.30, 1.30), COL_BAR_WOOD)
    for s in range(3):
        sz = 1.45 + s * 0.40
        make_box(f"WestBar_BackShelf_{s}",
                 (bar_cx_int, bb_y + 0.05, sz),
                 (bar_len, 0.20, 0.03), COL_WOOD_TRIM)
        # 8 bottles per shelf
        for b in range(8):
            bx = bar_cx_int - bar_len/2 + 0.30 + b * (bar_len - 0.60) / 7
            tints = [
                (0.18, 0.32, 0.20, 1.0),
                (0.42, 0.20, 0.10, 1.0),
                (0.62, 0.46, 0.20, 1.0),
                (0.30, 0.18, 0.34, 1.0),
                (0.86, 0.74, 0.36, 1.0),
                (0.20, 0.16, 0.34, 1.0),
                (0.74, 0.20, 0.18, 1.0),
            ]
            make_cyl(f"WestBar_Bottle_{s}_{b}",
                     (bx, bb_y + 0.05, sz + 0.16), 0.035, 0.30,
                     tints[(b + s) % 7], segments=6, axis='Z')
    # Backbar mirror
    make_box("WestBar_Mirror",
             (bar_cx_int, bb_y + 0.16, 2.40),
             (bar_len - 0.20, 0.04, 1.20), (0.30, 0.34, 0.40, 1.0))
    make_box("WestBar_MirrorFrame",
             (bar_cx_int, bb_y + 0.14, 2.40),
             (bar_len, 0.06, 1.35), COL_WOOD_TRIM)
    # 6 bar stools facing the bar
    n_stools = 6
    for i in range(n_stools):
        sx = bar_cx_int - bar_len/2 + 0.55 + i * (bar_len - 1.10) / (n_stools - 1)
        sy = bar_cy - 1.00
        make_cyl(f"WestBar_Stool_{i}_post", (sx, sy, 0.40),
                 0.04, 0.80, COL_BRASS, segments=6, axis='Z')
        make_cyl(f"WestBar_Stool_{i}_foot", (sx, sy, 0.22),
                 0.18, 0.025, COL_BRASS, segments=8, axis='Z')
        make_cyl(f"WestBar_Stool_{i}_seat", (sx, sy, 0.82),
                 0.22, 0.07, (0.32, 0.18, 0.10, 1.0), segments=10, axis='Z')
        make_cyl(f"WestBar_Stool_{i}_back_rod", (sx, sy - 0.16, 1.05),
                 0.016, 0.40, COL_BRASS, segments=4, axis='Z')
        make_box(f"WestBar_Stool_{i}_back_pad", (sx, sy - 0.18, 1.20),
                 (0.32, 0.04, 0.16), (0.32, 0.18, 0.10, 1.0))
    # 2 port-window cocktail tables (where patrons face the river)
    for i, tx in enumerate([EX_X_W + 1.6, EX_X_W + 4.4]):
        ty = +3.0
        make_cyl(f"WestBar_PortTable_{i}_Top",
                 (tx, ty, 0.92),
                 0.40, 0.04, COL_FORMICA, segments=12, axis='Z')
        make_cyl(f"WestBar_PortTable_{i}_Post",
                 (tx, ty, 0.46),
                 0.035, 0.92, COL_BRASS, segments=6, axis='Z')
        make_cyl(f"WestBar_PortTable_{i}_Foot",
                 (tx, ty, 0.03),
                 0.22, 0.04, (0.16, 0.14, 0.12, 1.0), segments=10, axis='Z')
        for sgn in (-1, +1):
            make_cyl(f"WestBar_PortStool_{i}_{sgn:+d}",
                     (tx, ty + sgn * 0.55, 0.82), 0.20, 0.07,
                     (0.32, 0.18, 0.10, 1.0), segments=10, axis='Z')
    # 3 pendant lamps over the bar
    for i, plx in enumerate([bar_cx_int - 1.6, bar_cx_int, bar_cx_int + 1.6]):
        plz = 2.40
        make_cyl(f"WestBar_Pendant_{i}_Wire",
                 (plx, bar_cy, (plz + D_H - 0.05) / 2),
                 0.010, (D_H - 0.05) - plz,
                 COL_PAYPHONE_DARK, segments=4, axis='Z')
        make_cyl(f"WestBar_Pendant_{i}_Shade",
                 (plx, bar_cy, plz), 0.16, 0.18,
                 (0.52, 0.30, 0.16, 1.0), segments=8, axis='Z')
        make_sphere_low(f"WestBar_Pendant_{i}_Bulb",
                        (plx, bar_cy, plz - 0.16), 0.05,
                        (0.96, 0.78, 0.42, 1.0), rings=2, segments=6)

    # ── CORRIDOR (Y=-1..+2) — the formal-hallway transition zone.
    # Has a small console table + a few framed paintings.
    cor_cx = EX_cx
    cor_cy = +0.5
    # Console table against the south wall of the corridor (Y=-1)
    make_box("WestExt_Corridor_Console",
             (EX_cx, +1.6, 0.78),
             (1.20, 0.36, 0.04), (0.40, 0.26, 0.16, 1.0))
    for lx in (-1, +1):
        for ly in (-1, +1):
            make_box(f"WestExt_Corridor_ConsoleLeg_{lx:+d}_{ly:+d}",
                     (EX_cx + lx * 0.55, +1.6 + ly * 0.16, 0.39),
                     (0.04, 0.04, 0.78), (0.30, 0.20, 0.10, 1.0))
    # Vase + a brass-trimmed framed painting on the south partition
    make_cyl("WestExt_Corridor_Vase",
             (EX_cx, +1.6, 0.92),
             0.07, 0.22, (0.32, 0.46, 0.40, 1.0), segments=8, axis='Z')
    # Brass picture frame above the console (looking south at the
    # north face of the formal-partition)
    make_box("WestExt_Corridor_Painting_Frame",
             (EX_cx, -1.0 + 0.06, 2.00),
             (1.00, 0.04, 0.70), COL_PHOTO_FRAME)
    make_box("WestExt_Corridor_Painting_Canvas",
             (EX_cx, -1.0 + 0.08, 2.00),
             (0.90, 0.02, 0.60), (0.30, 0.20, 0.14, 1.0))
    # Runner rug
    make_box("WestExt_Corridor_Rug",
             (EX_cx + 0.5, cor_cy, 0.014),
             (WEST_EXT_W - 1.50, 1.80, 0.006),
             (0.42, 0.22, 0.16, 1.0))

    # ── FORMAL DINING (Y=-6..-1) — large, formal, port-side view ──
    pd_cx = EX_cx
    pd_cy = -3.5
    table_w = 3.20
    table_d = 1.10
    table_top_z = 0.76
    # White-linen table
    make_box("WestFormal_Table_Top", (pd_cx, pd_cy, table_top_z),
             (table_w, table_d, 0.04), (0.94, 0.90, 0.78, 1.0))
    for sgn in (-1, +1):
        make_box(f"WestFormal_Cloth_NS_{sgn:+d}",
                 (pd_cx, pd_cy + sgn * (table_d/2 + 0.002),
                  table_top_z - 0.30),
                 (table_w + 0.04, 0.004, 0.60),
                 (0.94, 0.90, 0.78, 1.0))
        make_box(f"WestFormal_Cloth_EW_{sgn:+d}",
                 (pd_cx + sgn * (table_w/2 + 0.002), pd_cy,
                  table_top_z - 0.30),
                 (0.004, table_d + 0.04, 0.60),
                 (0.94, 0.90, 0.78, 1.0))
    # Brass table runner
    make_box("WestFormal_TableRunner",
             (pd_cx, pd_cy, table_top_z + 0.022),
             (table_w - 0.20, 0.32, 0.004),
             (0.62, 0.42, 0.24, 1.0))
    # Place settings (5 per side = 10 total)
    for side_sgn in (-1, +1):
        for p in range(5):
            sx = pd_cx - 1.30 + p * 0.65
            sy = pd_cy + side_sgn * 0.34
            # Charger
            make_cyl(f"WestFormal_Charger_{side_sgn:+d}_{p}",
                     (sx, sy, table_top_z + 0.030),
                     0.16, 0.010, (0.62, 0.42, 0.24, 1.0),
                     segments=10, axis='Z')
            # Plate
            make_cyl(f"WestFormal_Plate_{side_sgn:+d}_{p}",
                     (sx, sy, table_top_z + 0.045),
                     0.14, 0.012, (0.94, 0.92, 0.88, 1.0),
                     segments=10, axis='Z')
            # Knife + fork
            make_box(f"WestFormal_Knife_{side_sgn:+d}_{p}",
                     (sx + 0.20, sy, table_top_z + 0.025),
                     (0.20, 0.02, 0.005), COL_BRASS)
            make_box(f"WestFormal_Fork_{side_sgn:+d}_{p}",
                     (sx - 0.20, sy, table_top_z + 0.025),
                     (0.20, 0.02, 0.005), COL_BRASS)
            # Wine glass
            make_cyl(f"WestFormal_Glass_{side_sgn:+d}_{p}",
                     (sx + 0.04, sy - side_sgn * 0.22, table_top_z + 0.10),
                     0.030, 0.16, (0.86, 0.92, 0.94, 1.0),
                     segments=6, axis='Z')
    # 10 formal chairs (5 per long side)
    for side_sgn in (-1, +1):
        for c in range(5):
            cx_ch = pd_cx - 1.30 + c * 0.65
            cy_ch = pd_cy + side_sgn * 0.90
            make_box(f"WestFormal_Chair_{side_sgn:+d}_{c}_Seat",
                     (cx_ch, cy_ch, 0.46),
                     (0.42, 0.44, 0.06), (0.32, 0.20, 0.12, 1.0))
            for lx in (-1, +1):
                for ly in (-1, +1):
                    make_box(f"WestFormal_Chair_{side_sgn:+d}_{c}_Leg_{lx:+d}_{ly:+d}",
                             (cx_ch + lx * 0.18, cy_ch + ly * 0.19, 0.23),
                             (0.04, 0.04, 0.46), (0.32, 0.20, 0.12, 1.0))
            back_dy = side_sgn * 0.19
            for bx_off in (-0.16, 0.0, +0.16):
                make_box(f"WestFormal_Chair_{side_sgn:+d}_{c}_Back_{bx_off:+.2f}",
                         (cx_ch + bx_off, cy_ch + back_dy, 0.82),
                         (0.04, 0.04, 0.70), (0.32, 0.20, 0.12, 1.0))
            make_box(f"WestFormal_Chair_{side_sgn:+d}_{c}_BackTop",
                     (cx_ch, cy_ch + back_dy, 1.16),
                     (0.40, 0.05, 0.05), (0.32, 0.20, 0.12, 1.0))
            make_box(f"WestFormal_Chair_{side_sgn:+d}_{c}_Cushion",
                     (cx_ch, cy_ch, 0.50), (0.40, 0.40, 0.04),
                     COL_VINYL_RED_DK)
    # Captain chairs at the heads
    for end_i, sgn_x in enumerate([+1, -1]):
        ecx = pd_cx + sgn_x * (table_w/2 + 0.45)
        ecy = pd_cy
        make_box(f"WestFormal_Head_{end_i}_Seat",
                 (ecx, ecy, 0.46), (0.46, 0.46, 0.06),
                 (0.32, 0.20, 0.12, 1.0))
        for lx in (-1, +1):
            for ly in (-1, +1):
                make_box(f"WestFormal_Head_{end_i}_Leg_{lx:+d}_{ly:+d}",
                         (ecx + lx * 0.20, ecy + ly * 0.20, 0.23),
                         (0.04, 0.04, 0.46), (0.32, 0.20, 0.12, 1.0))
        back_dx = sgn_x * 0.20
        for bz_off in (-0.18, 0.0, +0.18):
            make_box(f"WestFormal_Head_{end_i}_Back_{bz_off:+.2f}",
                     (ecx + back_dx, ecy + bz_off, 0.82),
                     (0.05, 0.04, 0.70), (0.32, 0.20, 0.12, 1.0))
    # ── Large brass chandelier over the formal table ──
    ch_z_top = D_H - 0.10
    ch_z_low = ch_z_top - 1.20
    make_cyl("WestFormal_Chandelier_Chain",
             (pd_cx, pd_cy, (ch_z_top + ch_z_low) / 2),
             0.014, ch_z_top - ch_z_low, COL_BRASS, segments=4, axis='Z')
    make_cyl("WestFormal_Chandelier_Body",
             (pd_cx, pd_cy, ch_z_low),
             0.16, 0.28, COL_BRASS, segments=12, axis='Z')
    # 8 candle bulbs in two tiers (4 + 4)
    for tier_i, ring_r in enumerate([0.50, 0.75]):
        for ang_i in range(4):
            ang = math.radians(ang_i * 90 + tier_i * 45)
            ax = pd_cx + ring_r * math.cos(ang)
            ay = pd_cy + ring_r * math.sin(ang)
            make_cyl(f"WestFormal_Chandelier_Cup_{tier_i}_{ang_i}",
                     (ax, ay, ch_z_low + 0.06),
                     0.04, 0.08, COL_BRASS, segments=6, axis='Z')
            make_sphere_low(f"WestFormal_Chandelier_Bulb_{tier_i}_{ang_i}",
                            (ax, ay, ch_z_low + 0.20), 0.06,
                            (0.98, 0.86, 0.56, 1.0), rings=2, segments=6)
    # ── Sideboard against the EAST wall of the formal room (X=-9
    # partition wall, which is the building's old west wall) ──
    sb_x = EX_X_E - 0.30
    sb_y = pd_cy
    make_box("WestFormal_Sideboard_Body", (sb_x, sb_y, 0.50),
             (0.55, 3.00, 0.95), (0.40, 0.26, 0.16, 1.0))
    make_box("WestFormal_Sideboard_Top", (sb_x, sb_y, 1.00),
             (0.60, 3.10, 0.04), (0.30, 0.18, 0.10, 1.0))
    for d in range(4):
        dy = sb_y - 1.20 + d * 0.80
        make_box(f"WestFormal_Sideboard_Door_{d}",
                 (sb_x - 0.28, dy, 0.50),
                 (0.005, 0.70, 0.80), (0.26, 0.16, 0.10, 1.0))
        make_box(f"WestFormal_Sideboard_Handle_{d}",
                 (sb_x - 0.30, dy + 0.25, 0.55),
                 (0.02, 0.10, 0.018), COL_BRASS)
    # Decanter + candelabra + glasses on the sideboard
    make_cyl("WestFormal_Decanter",
             (sb_x - 0.10, sb_y - 1.0, 1.18),
             0.08, 0.32, (0.74, 0.60, 0.32, 1.0), segments=8, axis='Z')
    make_cyl("WestFormal_Candelabra",
             (sb_x - 0.10, sb_y, 1.20),
             0.025, 0.40, COL_BRASS, segments=6, axis='Z')
    for cnd in range(3):
        ang = math.radians(cnd * 120 - 60)
        cx_off = 0.12 * math.cos(ang)
        cy_off = 0.12 * math.sin(ang)
        make_cyl(f"WestFormal_Candle_{cnd}",
                 (sb_x - 0.10 + cx_off, sb_y + cy_off, 1.42),
                 0.020, 0.18, (0.96, 0.92, 0.82, 1.0),
                 segments=4, axis='Z')
        make_sphere_low(f"WestFormal_CandleFlame_{cnd}",
                        (sb_x - 0.10 + cx_off, sb_y + cy_off, 1.56),
                        0.04, (0.98, 0.78, 0.32, 1.0),
                        rings=2, segments=4)
    for g in range(4):
        gx = sb_x - 0.10
        gy = sb_y + 0.60 + g * 0.15
        make_cyl(f"WestFormal_Glass_{g}",
                 (gx, gy, 1.10),
                 0.035, 0.10, (0.86, 0.90, 0.92, 1.0), segments=6, axis='Z')


def build_alcove_booths():
    """Classic American-diner alcove booths along the river-window
    wall. CORRECTED orientation (per reference photo + iterations):

      · Benches run PERPENDICULAR to the window wall (long-axis = X)
      · Each booth is a U-shape opening EAST to the aisle
      · Two benches face each other across a small square table
      · Adjacent booths share a back-to-back divider (each divider
        IS a pair of back-to-back bench backrests, capped with crown
        molding)
      · Dividers only run from the wall to just past the table —
        the booth's east edge is OPEN so patrons walk straight in

      window wall (X=-9)        aisle
       │                          │
       │  [divider]               │
       │  ┌─ north bench ─┐       │
       │  │      ┌──┐     │       │
       │  │ ◯    │T │   ◯ │←OPEN──┤  patron enters from here
       │  │      └──┘     │       │
       │  └─ south bench ─┘       │
       │  [divider]               │
    """
    # ── Dimensions ──
    bench_len    = 1.45    # bench long-axis (perpendicular to wall, X)
    bench_depth  = 0.50    # bench Y-extent
    seat_top_z   = 0.45
    back_h       = 0.70    # backrest height above seat → top at z=1.15
    div_thick    = 0.06
    table_sz     = 0.70    # square table
    booth_y_span = 1.50    # full N-S extent of one booth (incl. divider thickness)
    n_booths     = 6

    # X positions
    wall_x      = -D_W / 2                     # -9
    bench_x_W   = wall_x + 0.05 + bench_len / 2.0   # bench starts at X=-8.95, center at -8.225
    bench_x_E   = wall_x + 0.05 + bench_len          # =-7.50 (east end of bench)
    table_cx    = bench_x_E - 0.10 - table_sz / 2.0  # table just inside the bench east end
    div_x_W     = wall_x + 0.05                       # -8.95 (divider starts here, at wall)
    div_x_E     = bench_x_E + 0.10                    # -7.40 (divider ends here — open east beyond)
    div_cx      = (div_x_W + div_x_E) / 2.0           # -8.175
    div_len_x   = div_x_E - div_x_W                   # 1.55

    # Row total Y span and center
    total_y_span = n_booths * booth_y_span
    row_center_y = +0.0       # centered on the room
    row_y_lo     = row_center_y - total_y_span / 2.0
    row_y_hi     = row_center_y + total_y_span / 2.0

    div_top_z = seat_top_z + back_h            # 1.15

    # ── Build n+1 dividers across the row ──
    # Each divider is a thin wall + crown molding cap + baseboard,
    # spanning the booth depth from the wall to just past the table.
    for d in range(n_booths + 1):
        dy = row_y_lo + d * booth_y_span
        make_box(f"Alcove_Divider_{d}",
                 (div_cx, dy, div_top_z / 2.0),
                 (div_len_x, div_thick, div_top_z), COL_VINYL_RED_DK)
        # Vertical tuft seams on each face of the divider (one set
        # per booth-facing side — north face and south face)
        for face_sgn in (-1, +1):
            for c in range(2):
                sx_off = -0.4 + c * 0.8
                make_box(f"Alcove_Divider_{d}_seam_{face_sgn:+d}_{c}",
                         (div_cx + sx_off,
                          dy + face_sgn * (div_thick / 2.0 + 0.005),
                          div_top_z / 2.0 + 0.05),
                         (0.025, 0.012, div_top_z - 0.20),
                         COL_VINYL_RED)
        # Crown molding cap (full divider length + slight overhang)
        make_box(f"Alcove_Divider_{d}_crown",
                 (div_cx, dy, div_top_z + 0.025),
                 (div_len_x + 0.04, div_thick + 0.04, 0.05),
                 COL_WOOD_TRIM)
        # Wood baseboard at the floor
        make_box(f"Alcove_Divider_{d}_base",
                 (div_cx, dy, 0.05),
                 (div_len_x + 0.04, div_thick + 0.04, 0.10),
                 COL_WOOD_TRIM)
        # The east end of each divider gets a tall finial post (so
        # the row looks finished where it opens to the aisle)
        make_box(f"Alcove_Divider_{d}_finial",
                 (div_x_E + 0.06, dy, div_top_z / 2.0 + 0.05),
                 (0.12, div_thick + 0.05, div_top_z + 0.20),
                 COL_WOOD_TRIM)

    # ── Build n booths between adjacent dividers ──
    for i in range(n_booths):
        by = row_y_lo + (i + 0.5) * booth_y_span    # booth Y center
        prefix = f"Booth_{i + 1}"

        # Bench Y offsets: each bench sits AGAINST a divider
        # North bench: backrest at dy_N = by + booth_y_span/2
        # South bench: backrest at dy_S = by - booth_y_span/2
        dy_N = by + booth_y_span / 2.0
        dy_S = by - booth_y_span / 2.0
        # Bench seat center is bench_depth/2 + div_thick/2 inward
        north_bench_cy = dy_N - div_thick / 2.0 - bench_depth / 2.0
        south_bench_cy = dy_S + div_thick / 2.0 + bench_depth / 2.0

        # ── NORTH bench (customer sits facing SOUTH) ──
        # Seat slab
        make_box(f"{prefix}_NorthBench_Seat",
                 (bench_x_W, north_bench_cy, seat_top_z / 2.0),
                 (bench_len, bench_depth, seat_top_z), COL_VINYL_RED)
        # Cushion seam strip along the seat front edge (south face)
        make_box(f"{prefix}_NorthBench_Seam",
                 (bench_x_W, north_bench_cy - bench_depth / 2.0 + 0.04,
                  seat_top_z - 0.012),
                 (bench_len - 0.06, 0.04, 0.020), COL_VINYL_RED_DK)
        # 3 button-tuft dimples across the seat
        for t in range(3):
            tx = bench_x_W - 0.40 + t * 0.40
            make_box(f"{prefix}_NorthBench_Tuft_{t}",
                     (tx, north_bench_cy, seat_top_z - 0.005),
                     (0.04, 0.04, 0.012), COL_VINYL_RED_DK)

        # ── SOUTH bench (customer sits facing NORTH) ──
        make_box(f"{prefix}_SouthBench_Seat",
                 (bench_x_W, south_bench_cy, seat_top_z / 2.0),
                 (bench_len, bench_depth, seat_top_z), COL_VINYL_RED)
        make_box(f"{prefix}_SouthBench_Seam",
                 (bench_x_W, south_bench_cy + bench_depth / 2.0 - 0.04,
                  seat_top_z - 0.012),
                 (bench_len - 0.06, 0.04, 0.020), COL_VINYL_RED_DK)
        for t in range(3):
            tx = bench_x_W - 0.40 + t * 0.40
            make_box(f"{prefix}_SouthBench_Tuft_{t}",
                     (tx, south_bench_cy, seat_top_z - 0.005),
                     (0.04, 0.04, 0.012), COL_VINYL_RED_DK)

        # ── Small square formica table between the benches ──
        table_top_z = 0.74
        make_box(f"{prefix}_Table_Top",
                 (table_cx, by, table_top_z),
                 (table_sz, table_sz, 0.04), COL_FORMICA)
        # Chrome edge band rim
        make_box(f"{prefix}_Table_Band",
                 (table_cx, by, table_top_z - 0.03),
                 (table_sz + 0.02, table_sz + 0.02, 0.02), COL_BRASS)
        # Chrome center post + cast-iron foot
        make_cyl(f"{prefix}_Table_Post",
                 (table_cx, by, table_top_z / 2.0),
                 0.045, table_top_z - 0.04, COL_BRASS, segments=8, axis='Z')
        make_cyl(f"{prefix}_Table_Foot",
                 (table_cx, by, 0.03),
                 0.22, 0.04, (0.16, 0.14, 0.12, 1.0),
                 segments=10, axis='Z')

        # ── Pendant lamp directly above the table ──
        wire_top_z = D_H - 0.05
        lamp_z = table_top_z + 0.85
        make_cyl(f"{prefix}_Lamp_Canopy",
                 (table_cx, by, wire_top_z - 0.02),
                 0.07, 0.04, COL_BRASS, segments=8, axis='Z')
        make_cyl(f"{prefix}_Lamp_Stem",
                 (table_cx, by, (lamp_z + wire_top_z) / 2.0),
                 0.012, wire_top_z - lamp_z,
                 COL_PAYPHONE_DARK, segments=4, axis='Z')
        make_sphere_low(f"{prefix}_Lamp_Shade",
                        (table_cx, by, lamp_z), 0.20,
                        (0.86, 0.62, 0.32, 1.0), rings=2, segments=10)
        make_sphere_low(f"{prefix}_Lamp_Bulb",
                        (table_cx, by, lamp_z - 0.18), 0.05,
                        (0.98, 0.92, 0.74, 1.0), rings=2, segments=6)

        # ── Small brass table-number plaque ──
        make_box(f"{prefix}_Table_Number",
                 (table_cx + table_sz / 2.0 - 0.08,
                  by - table_sz / 2.0 + 0.08, table_top_z + 0.022),
                 (0.07, 0.07, 0.005), COL_BRASS)

        # Register for table dressings
        BOOTH_POSITIONS.append((prefix, table_cx, by, 'X'))


def build_freestanding_tables():
    """Two small 2-top tables on the open center floor, between the
    booth row and the east wall. Adds variety without crowding."""
    # Position the tables in clear floor space. With the new
    # private-dining room at X=-1..+5, Y=-2.5..+1, bistros must
    # avoid that pocket plus the alcove-booth row along X=-9..-7.
    table_specs = [
        ("Bistro_1", -4.5, -1.5),   # SW main floor, west of PD
        ("Bistro_2", -3.5, +2.5),   # NW main floor, north of PD
        ("Bistro_3", +2.5, +3.5),   # N main floor, north of PD
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

def build_riverboat_galley():
    """The full riverboat galley — a long, narrow, stainless-and-brass
    cook line spanning the entire south side of the diner from the
    west wall to the private-dining partition. Feeds three rooms:

      · Main counter (via the existing pass-through frame at X=-5.5)
      · Main dining floor (servers walk plates north through the
        counter-back side)
      · Private dining Table 17 (via a new service door at X=+5,
        the galley's east wall)

    Layout (W → E along the south wall, under a continuous hood):
      reach-in cooler · cold prep · char-broiler · flat-top griddle
      · 6-burner range + oven · double fryer · salamander shelf
      · steam table · plating/garnish · 3-bay sink + dish machine

    Footprint: ~13.9m × 2.0m × 3.4m. Floor is kitchen tile (covers
    the diner-floor checkerboard in this zone).
    """
    K_X_W = -D_W/2 + 0.05      # -8.95
    K_X_E = +5.0 - 0.05         # +4.95
    K_Y_S = -D_D/2 + 0.05       # -5.95
    K_Y_N = -3.95               # just behind Counter_Back at Y=-3.9
    cx_k = (K_X_W + K_X_E) / 2.0
    cy_k = (K_Y_S + K_Y_N) / 2.0

    # ── Floor (kitchen tile painting over the diner checker) ──
    make_box("Galley_Floor", (cx_k, cy_k, 0.045),
             (K_X_E - K_X_W, K_Y_N - K_Y_S, 0.05),
             COL_KITCHEN_TILE)
    # Tile grout grid (light visible lines)
    n_tiles_x = int((K_X_E - K_X_W) / 0.5)
    n_tiles_y = int((K_Y_N - K_Y_S) / 0.5)
    for i in range(1, n_tiles_x):
        gx = K_X_W + i * (K_X_E - K_X_W) / n_tiles_x
        make_box(f"Galley_Grout_V_{i}", (gx, cy_k, 0.075),
                 (0.025, K_Y_N - K_Y_S, 0.005),
                 (0.50, 0.46, 0.40, 1.0))
    for j in range(1, n_tiles_y):
        gy = K_Y_S + j * (K_Y_N - K_Y_S) / n_tiles_y
        make_box(f"Galley_Grout_H_{j}", (cx_k, gy, 0.075),
                 (K_X_E - K_X_W, 0.025, 0.005),
                 (0.50, 0.46, 0.40, 1.0))

    # ── HOT LINE along the south wall (Y ≈ -5.55) ──
    line_cy = -5.55
    line_top_z = 0.85
    line_d = 0.70

    # 1) Reach-in cooler (tall stainless box) — X=-8 .. -7
    make_box("Galley_ReachIn",
             (-7.5, line_cy, 0.95),
             (1.0, 0.65, 1.90), COL_KITCHEN_STEEL)
    make_box("Galley_ReachIn_Door",
             (-7.5, line_cy - 0.33, 0.95),
             (0.85, 0.04, 1.80), (0.52, 0.52, 0.54, 1.0))
    make_cyl("Galley_ReachIn_Handle",
             (-7.5, line_cy - 0.36, 0.95),
             0.012, 0.40, COL_BRASS, segments=4, axis='Z')

    # 2) Cold prep station — X=-7 .. -5.5
    make_box("Galley_ColdPrep_Body",
             (-6.25, line_cy, line_top_z / 2),
             (1.5, line_d, line_top_z), COL_KITCHEN_STEEL)
    make_box("Galley_ColdPrep_Top",
             (-6.25, line_cy, line_top_z + 0.02),
             (1.5, line_d, 0.04), (0.72, 0.72, 0.70, 1.0))
    make_box("Galley_ColdPrep_Board",
             (-6.25, line_cy - 0.12, line_top_z + 0.06),
             (0.60, 0.40, 0.04), (0.86, 0.74, 0.50, 1.0))
    for i, col in enumerate([(0.42, 0.58, 0.28, 1.0),
                              (0.62, 0.42, 0.30, 1.0),
                              (0.86, 0.78, 0.50, 1.0)]):
        ix = -6.85 + i * 0.40
        make_box(f"Galley_ColdPrep_Pan_{i}",
                 (ix, line_cy + 0.15, line_top_z + 0.005),
                 (0.30, 0.22, 0.06), col)

    # 3) Char-broiler — X=-5.5 .. -4
    make_box("Galley_Charbroil_Body",
             (-4.75, line_cy, line_top_z / 2),
             (1.5, line_d, line_top_z), COL_KITCHEN_STEEL)
    make_box("Galley_Charbroil_Top",
             (-4.75, line_cy, line_top_z + 0.02),
             (1.5, line_d, 0.04), (0.25, 0.20, 0.18, 1.0))
    for g in range(8):
        gx = -5.40 + g * 0.18
        make_box(f"Galley_Charbroil_Bar_{g}",
                 (gx, line_cy, line_top_z + 0.05),
                 (0.04, line_d - 0.10, 0.012),
                 (0.10, 0.08, 0.06, 1.0))
        make_box(f"Galley_Charbroil_Glow_{g}",
                 (gx, line_cy, line_top_z + 0.03),
                 (0.04, line_d - 0.15, 0.008),
                 (0.78, 0.32, 0.18, 1.0))
    for k in range(3):
        kx = -5.30 + k * 0.50
        make_cyl(f"Galley_Charbroil_Knob_{k}",
                 (kx, line_cy - line_d / 2 - 0.02, line_top_z - 0.10),
                 0.03, 0.04, COL_BRASS, segments=6, axis='Y')

    # 4) Flat-top griddle — X=-4 .. -2.5
    make_box("Galley_Griddle_Body",
             (-3.25, line_cy, line_top_z / 2),
             (1.5, line_d, line_top_z), COL_KITCHEN_STEEL)
    make_box("Galley_Griddle_Surface",
             (-3.25, line_cy, line_top_z + 0.025),
             (1.4, line_d - 0.04, 0.05),
             (0.18, 0.16, 0.14, 1.0))
    make_box("Galley_Griddle_GreaseChan",
             (-3.25, line_cy - line_d / 2 + 0.04, line_top_z + 0.015),
             (1.30, 0.05, 0.03), (0.12, 0.10, 0.08, 1.0))
    # Spatula resting on the griddle
    make_box("Galley_Griddle_Spatula_Head",
             (-3.40, line_cy + 0.10, line_top_z + 0.05),
             (0.10, 0.20, 0.005), COL_KITCHEN_STEEL)
    make_cyl("Galley_Griddle_Spatula_Handle",
             (-3.40, line_cy + 0.25, line_top_z + 0.05),
             0.012, 0.20, (0.42, 0.32, 0.20, 1.0),
             segments=4, axis='Y')

    # 5) 6-burner range + oven — X=-2.5 .. -1
    make_box("Galley_Range_Body",
             (-1.75, line_cy, line_top_z / 2),
             (1.5, line_d, line_top_z), COL_KITCHEN_STEEL)
    make_box("Galley_Range_OvenDoor",
             (-1.75, line_cy - line_d / 2 - 0.02, 0.40),
             (1.35, 0.04, 0.55), (0.45, 0.45, 0.47, 1.0))
    make_cyl("Galley_Range_OvenHandle",
             (-1.75, line_cy - line_d / 2 - 0.05, 0.40),
             0.018, 1.10, COL_BRASS, segments=4, axis='X')
    # 6 burners (2 rows × 3 cols) + blue flames on two of them
    for r in range(2):
        for c in range(3):
            bx = -2.30 + c * 0.50
            by = line_cy - 0.15 + r * 0.30
            make_cyl(f"Galley_Range_Grate_{r}_{c}",
                     (bx, by, line_top_z + 0.02),
                     0.16, 0.012, (0.10, 0.08, 0.06, 1.0),
                     segments=6, axis='Z')
            make_cyl(f"Galley_Range_Head_{r}_{c}",
                     (bx, by, line_top_z + 0.005),
                     0.10, 0.025, (0.20, 0.18, 0.14, 1.0),
                     segments=8, axis='Z')
            if (r, c) in [(0, 1), (1, 2)]:
                make_sphere_low(f"Galley_Range_Flame_{r}_{c}",
                                (bx, by, line_top_z + 0.07),
                                0.07, (0.42, 0.66, 0.96, 1.0),
                                rings=2, segments=6)
    # 6 control knobs along the apron
    for k in range(6):
        kx = -2.30 + k * 0.22
        make_cyl(f"Galley_Range_Knob_{k}",
                 (kx, line_cy - line_d / 2 - 0.02, line_top_z - 0.12),
                 0.025, 0.04, COL_BRASS, segments=6, axis='Y')
    # An active pot on a burner (with lid + handle)
    make_cyl("Galley_Range_Pot",
             (-1.80, line_cy - 0.15, line_top_z + 0.16),
             0.16, 0.22, (0.42, 0.32, 0.22, 1.0), segments=10, axis='Z')
    make_cyl("Galley_Range_Pot_Lid",
             (-1.80, line_cy - 0.15, line_top_z + 0.27),
             0.17, 0.020, COL_KITCHEN_STEEL, segments=10, axis='Z')
    make_box("Galley_Range_Pot_Handle",
             (-1.60, line_cy - 0.15, line_top_z + 0.15),
             (0.16, 0.030, 0.030), (0.20, 0.16, 0.10, 1.0))

    # 6) Double-basket fryer — X=-1 .. 0
    make_box("Galley_Fryer_Body",
             (-0.5, line_cy, line_top_z / 2),
             (1.0, line_d, line_top_z), COL_KITCHEN_STEEL)
    for w in range(2):
        wx = -0.75 + w * 0.50
        make_box(f"Galley_Fryer_Well_{w}",
                 (wx, line_cy, line_top_z - 0.04),
                 (0.40, line_d - 0.10, 0.20),
                 (0.20, 0.16, 0.10, 1.0))
        make_box(f"Galley_Fryer_Oil_{w}",
                 (wx, line_cy, line_top_z + 0.02),
                 (0.38, line_d - 0.12, 0.04),
                 (0.86, 0.66, 0.20, 1.0))
        make_cyl(f"Galley_Fryer_BasketHandle_{w}",
                 (wx, line_cy - 0.15, line_top_z + 0.20),
                 0.012, 0.35, COL_KITCHEN_STEEL, segments=4, axis='Z')

    # 7) Salamander broiler on a shelf above the range (z ≈ 1.7)
    sal_z = line_top_z + 0.85
    make_box("Galley_Salamander",
             (-1.75, line_cy + 0.05, sal_z),
             (1.4, 0.55, 0.30), (0.30, 0.30, 0.32, 1.0))
    make_box("Galley_Salamander_Element",
             (-1.75, line_cy + 0.05, sal_z - 0.13),
             (1.20, 0.40, 0.020), (0.96, 0.32, 0.16, 1.0))
    for sgn in (-1, +1):
        make_box(f"Galley_Salamander_Bracket_{sgn:+d}",
                 (-1.75 + sgn * 0.65, line_cy + 0.30, line_top_z + 0.45),
                 (0.04, 0.04, 0.70), COL_KITCHEN_STEEL)

    # 8) Steam table — X=0 .. +1.5
    make_box("Galley_SteamTable_Body",
             (+0.75, line_cy, line_top_z / 2),
             (1.5, line_d, line_top_z), COL_KITCHEN_STEEL)
    well_colors = [
        (0.78, 0.42, 0.20, 1.0),    # red sauce
        (0.86, 0.74, 0.50, 1.0),    # mashed potatoes
        (0.50, 0.38, 0.20, 1.0),    # gravy
        (0.42, 0.58, 0.30, 1.0),    # peas / greens
    ]
    for w, col in enumerate(well_colors):
        wx = +0.10 + w * 0.36
        make_box(f"Galley_SteamTable_Well_{w}",
                 (wx, line_cy, line_top_z),
                 (0.30, line_d - 0.10, 0.04), (0.50, 0.50, 0.52, 1.0))
        make_box(f"Galley_SteamTable_Food_{w}",
                 (wx, line_cy, line_top_z + 0.03),
                 (0.28, line_d - 0.14, 0.05), col)
    # Sneeze guard (light glass slab forward)
    make_box("Galley_SteamTable_Guard",
             (+0.75, line_cy + line_d / 2 - 0.10, line_top_z + 0.30),
             (1.40, 0.04, 0.40), (0.78, 0.84, 0.86, 1.0))

    # 9) Plating / garnish station — X=+1.5 .. +3
    make_box("Galley_Plating_Body",
             (+2.25, line_cy, line_top_z / 2),
             (1.5, line_d, line_top_z), COL_KITCHEN_STEEL)
    make_box("Galley_Plating_Top",
             (+2.25, line_cy, line_top_z + 0.02),
             (1.5, line_d, 0.04), (0.72, 0.72, 0.70, 1.0))
    for p in range(4):
        make_cyl(f"Galley_Plating_Plate_{p}",
                 (+2.80, line_cy - 0.20, line_top_z + 0.06 + p * 0.012),
                 0.13, 0.010, (0.92, 0.90, 0.84, 1.0),
                 segments=10, axis='Z')
    for sb, col in enumerate([(0.76, 0.16, 0.16, 1.0),
                               (0.86, 0.78, 0.42, 1.0),
                               (0.40, 0.30, 0.20, 1.0)]):
        make_cyl(f"Galley_Plating_Squeeze_{sb}",
                 (+1.70 + sb * 0.16, line_cy + 0.18, line_top_z + 0.13),
                 0.025, 0.20, col, segments=8, axis='Z')
        make_cyl(f"Galley_Plating_Squeeze_Cap_{sb}",
                 (+1.70 + sb * 0.16, line_cy + 0.18, line_top_z + 0.24),
                 0.018, 0.04, (0.30, 0.30, 0.32, 1.0),
                 segments=6, axis='Z')

    # 10) 3-bay sink + dish machine — X=+3 .. +4.95
    make_box("Galley_Sink_Body",
             (+4.0, line_cy, line_top_z / 2),
             (1.95, line_d, line_top_z), COL_KITCHEN_STEEL)
    for s in range(3):
        sx = +3.30 + s * 0.55
        make_box(f"Galley_Sink_Bay_{s}",
                 (sx, line_cy, line_top_z - 0.03),
                 (0.50, line_d - 0.08, 0.30),
                 (0.40, 0.40, 0.42, 1.0))
        if s == 1:
            make_box(f"Galley_Sink_Water_{s}",
                     (sx, line_cy, line_top_z - 0.08),
                     (0.46, line_d - 0.12, 0.04),
                     (0.42, 0.56, 0.66, 1.0))
    # Faucet riser + swing-arm + spray head
    make_cyl("Galley_Sink_FaucetRiser",
             (+4.0, line_cy + 0.20, line_top_z + 0.30),
             0.022, 0.50, COL_BRASS, segments=6, axis='Z')
    make_cyl("Galley_Sink_FaucetArm",
             (+3.80, line_cy + 0.10, line_top_z + 0.50),
             0.018, 0.55, COL_BRASS, segments=6, axis='X')
    make_box("Galley_Sink_SprayHead",
             (+3.45, line_cy + 0.10, line_top_z + 0.40),
             (0.05, 0.05, 0.12), COL_BRASS)
    make_cyl("Galley_Sink_SprayHose",
             (+3.45, line_cy + 0.10, line_top_z + 0.30),
             0.012, 0.18, (0.20, 0.18, 0.16, 1.0),
             segments=4, axis='Z')
    # Drying rack with 5 clean plates
    make_box("Galley_DryRack",
             (+4.60, line_cy - 0.10, line_top_z + 0.10),
             (0.36, 0.40, 0.20), COL_KITCHEN_STEEL)
    for p in range(5):
        make_cyl(f"Galley_DryRack_Plate_{p}",
                 (+4.55, line_cy - 0.20 + p * 0.06, line_top_z + 0.20),
                 0.06, 0.020, (0.92, 0.90, 0.84, 1.0),
                 segments=8, axis='Y')

    # ── CONTINUOUS HOOD VENT above the cook line ──
    hood_z = 2.10
    hood_x_W, hood_x_E = -5.5, +1.0
    hood_w = hood_x_E - hood_x_W
    hood_cx = (hood_x_W + hood_x_E) / 2
    make_box("Galley_Hood_Body",
             (hood_cx, line_cy + 0.05, hood_z + 0.30),
             (hood_w + 0.10, line_d + 0.20, 0.60),
             (0.50, 0.50, 0.52, 1.0))
    make_box("Galley_Hood_Rim",
             (hood_cx, line_cy - line_d / 2, hood_z),
             (hood_w + 0.10, 0.06, 0.04),
             (0.32, 0.32, 0.34, 1.0))
    # 6 baffle filters
    for b in range(6):
        bx = hood_x_W + 0.10 + b * (hood_w - 0.20) / 6
        make_box(f"Galley_Hood_Baffle_{b}",
                 (bx, line_cy + 0.05, hood_z + 0.05),
                 (0.18, line_d + 0.10, 0.04),
                 (0.30, 0.30, 0.34, 1.0))
    # Vent stack rising through the ceiling toward the smokestacks
    make_cyl("Galley_Hood_Stack",
             (hood_cx, line_cy, D_H - 0.20),
             0.18, D_H - hood_z - 0.50,
             (0.40, 0.40, 0.42, 1.0), segments=8, axis='Z')

    # ── POT RACK overhead (west end, above prep area) ──
    pr_x_W, pr_x_E = -8.2, -5.5
    pr_cx = (pr_x_W + pr_x_E) / 2
    pr_z = 2.30
    for bz in (pr_z - 0.02, pr_z + 0.02):
        make_cyl(f"Galley_PotRack_Bar_z{bz:.2f}",
                 (pr_cx, line_cy + 0.05, bz),
                 0.018, pr_x_E - pr_x_W,
                 COL_BRASS, segments=6, axis='X')
    for cb in range(int((pr_x_E - pr_x_W) / 0.5) + 1):
        cbx = pr_x_W + cb * 0.5
        make_cyl(f"Galley_PotRack_Cross_{cb}",
                 (cbx, line_cy + 0.05, pr_z),
                 0.014, line_d - 0.10,
                 COL_BRASS, segments=4, axis='Y')
    # Hanging pots — now WITH copper. User asked for "more formal
    # kitchen" — copper bottoms catch the warmth, brass handles read.
    COL_COPPER       = (0.74, 0.44, 0.20, 1.0)
    COL_COPPER_DEEP  = (0.62, 0.34, 0.14, 1.0)
    COL_COPPER_HI    = (0.86, 0.58, 0.28, 1.0)
    for i, (px, pr, ph, pc) in enumerate([
        (-7.8, 0.18, 0.22, COL_COPPER),
        (-7.2, 0.16, 0.18, COL_COPPER_DEEP),
        (-6.6, 0.20, 0.16, (0.30, 0.30, 0.32, 1.0)),  # one stainless saucepan
        (-6.0, 0.15, 0.20, COL_COPPER),
        (-5.7, 0.14, 0.14, COL_COPPER_HI),
    ]):
        make_cyl(f"Galley_HangPot_{i}",
                 (px, line_cy + 0.05, pr_z - 0.30),
                 pr, ph, pc, segments=8, axis='Z')
        # Brass rim around the lip of each pot
        make_cyl(f"Galley_HangPot_{i}_Rim",
                 (px, line_cy + 0.05, pr_z - 0.30 + ph/2 + 0.005),
                 pr + 0.005, 0.012, COL_BRASS, segments=8, axis='Z')
        # Brass handle on the side of each pot
        make_cyl(f"Galley_HangPot_{i}_Handle",
                 (px + pr + 0.04, line_cy + 0.05, pr_z - 0.30),
                 0.010, 0.10, COL_BRASS, segments=4, axis='X')
        # S-hook from pot up to the rack
        make_cyl(f"Galley_HangPot_{i}_Hook",
                 (px, line_cy + 0.05, pr_z - 0.18),
                 0.012, 0.20, COL_BRASS, segments=4, axis='Z')
    # ── Additional formal touches: a copper saucier pan on the line ──
    make_cyl("Galley_Saucier",
             (-3.0, line_cy + 0.10, line_top_z + 0.10),
             0.13, 0.08, COL_COPPER, segments=10, axis='Z')
    make_cyl("Galley_Saucier_Rim",
             (-3.0, line_cy + 0.10, line_top_z + 0.14),
             0.135, 0.012, COL_BRASS, segments=10, axis='Z')
    make_cyl("Galley_Saucier_Handle",
             (-3.0 - 0.20, line_cy + 0.10, line_top_z + 0.12),
             0.012, 0.26, COL_BRASS, segments=4, axis='X')
    # ── Copper ladles hanging on a brass hook line beside the
    #    pot rack (3 small ladles dangling) ──
    for li in range(3):
        lx = pr_x_E + 0.30 + li * 0.20
        make_cyl(f"Galley_Ladle_{li}_Bowl",
                 (lx, line_cy + 0.10, pr_z - 0.36),
                 0.06, 0.04, COL_COPPER, segments=8, axis='Z')
        make_cyl(f"Galley_Ladle_{li}_Handle",
                 (lx, line_cy + 0.10, pr_z - 0.20),
                 0.008, 0.30, COL_BRASS, segments=4, axis='Z')
        make_cyl(f"Galley_Ladle_{li}_Hook",
                 (lx, line_cy + 0.10, pr_z - 0.05),
                 0.010, 0.06, COL_BRASS, segments=4, axis='Z')

    # ── EXPO / PLATING LINE along north edge (Y≈-4.05) ──
    expo_cy = -4.10
    expo_top_z = 0.92
    expo_d = 0.25
    make_box("Galley_Expo_Body",
             (cx_k, expo_cy, expo_top_z / 2),
             (K_X_E - K_X_W - 0.20, expo_d, expo_top_z),
             COL_KITCHEN_STEEL)
    make_box("Galley_Expo_Top",
             (cx_k, expo_cy, expo_top_z + 0.02),
             (K_X_E - K_X_W - 0.20, expo_d, 0.04),
             (0.72, 0.72, 0.70, 1.0))
    # Heat lamps (5)
    for h in range(5):
        hx = K_X_W + 0.5 + h * (K_X_E - K_X_W - 1.0) / 4
        make_cyl(f"Galley_HeatLamp_{h}_Housing",
                 (hx, expo_cy, 1.80),
                 0.08, 0.16, (0.50, 0.50, 0.52, 1.0),
                 segments=8, axis='Z')
        make_sphere_low(f"Galley_HeatLamp_{h}_Bulb",
                        (hx, expo_cy, 1.72),
                        0.06, (0.96, 0.42, 0.18, 1.0),
                        rings=2, segments=6)
        make_cyl(f"Galley_HeatLamp_{h}_Cord",
                 (hx, expo_cy, (1.92 + D_H - 0.05) / 2),
                 0.008, (D_H - 0.05) - 1.92,
                 (0.10, 0.08, 0.06, 1.0), segments=4, axis='Z')
    # Ticket rail with hanging order tickets
    make_cyl("Galley_TicketRail",
             (cx_k, expo_cy - 0.05, 1.55),
             0.010, K_X_E - K_X_W - 0.40,
             COL_BRASS, segments=4, axis='X')
    for ti, tx in enumerate([-7.0, -5.5, -3.5, -1.8, +0.5, +2.0, +3.5]):
        make_box(f"Galley_Ticket_{ti}",
                 (tx, expo_cy - 0.05, 1.45),
                 (0.10, 0.005, 0.18), (0.92, 0.88, 0.74, 1.0))
        make_box(f"Galley_TicketOrder_{ti}",
                 (tx, expo_cy - 0.055, 1.42),
                 (0.06, 0.003, 0.04), (0.18, 0.16, 0.14, 1.0))
    # 2 plates ready on the expo line
    for p_i, (px, color) in enumerate([
        (-3.0, (0.86, 0.62, 0.38, 1.0)),
        (+2.6, (0.86, 0.74, 0.50, 1.0)),
    ]):
        make_cyl(f"Galley_ExpoPlate_{p_i}",
                 (px, expo_cy, expo_top_z + 0.06),
                 0.14, 0.012, (0.92, 0.90, 0.84, 1.0),
                 segments=10, axis='Z')
        make_sphere_low(f"Galley_ExpoPlate_Food_{p_i}",
                        (px, expo_cy, expo_top_z + 0.08),
                        0.08, color, rings=2, segments=6)
    # Chrome service bell at the west end of the expo line
    make_sphere_low("Galley_ExpoBell",
                    (-7.5, expo_cy, expo_top_z + 0.10),
                    0.07, COL_BRASS, rings=2, segments=8)

    # ── SUBWAY-TILE BACKSPLASH along the south wall ──
    make_box("Galley_Backsplash",
             (cx_k, K_Y_S + 0.05, line_top_z + 0.50),
             (K_X_E - K_X_W - 0.20, 0.04, 1.20),
             (0.86, 0.84, 0.76, 1.0))
    for r in range(5):
        rz = line_top_z + 0.10 + r * 0.20
        make_box(f"Galley_Backsplash_Grout_{r}",
                 (cx_k, K_Y_S + 0.03, rz),
                 (K_X_E - K_X_W - 0.30, 0.005, 0.015),
                 (0.50, 0.46, 0.40, 1.0))

    # ── KNIFE STRIP (magnetic) on the west wall ──
    make_box("Galley_KnifeStrip",
             (K_X_W + 0.04, line_cy + 0.30, 1.70),
             (0.04, 0.40, 0.50), (0.42, 0.32, 0.20, 1.0))
    for k in range(4):
        kz = 1.55 + k * 0.10
        ky_off = -0.10 + k * 0.10
        make_box(f"Galley_Knife_{k}_Blade",
                 (K_X_W + 0.10, line_cy + 0.20 + ky_off * 0, kz),
                 (0.04, 0.04, 0.28), (0.86, 0.86, 0.88, 1.0))
        make_box(f"Galley_Knife_{k}_Handle",
                 (K_X_W + 0.10, line_cy + 0.20 + ky_off * 0, kz - 0.18),
                 (0.04, 0.04, 0.08), (0.22, 0.14, 0.08, 1.0))

    # ── ANTI-FATIGUE MAT in front of the cook line ──
    make_box("Galley_Mat",
             (cx_k - 0.50, -5.00, 0.072),
             (K_X_E - K_X_W - 2.5, 0.50, 0.020),
             (0.16, 0.14, 0.12, 1.0))
    n_tread = int((K_X_E - K_X_W - 2.5) / 0.30)
    for g in range(n_tread):
        gx = (cx_k - 0.50) - (K_X_E - K_X_W - 2.5) / 2 + (g + 0.5) * 0.30
        make_box(f"Galley_Mat_Tread_{g}",
                 (gx, -5.00, 0.082),
                 (0.020, 0.44, 0.003),
                 (0.30, 0.28, 0.26, 1.0))

    # ── GALLEY SERVICE DOOR PANEL (the wall opening is cut by
    #    build_interior_partitions; we just place the door + hardware) ──
    door_cy = (-4.85 + -3.95) / 2
    door_h = 2.05
    # Stainless service door (sits just east of the wall plane)
    make_box("Galley_ServiceDoor_Panel",
             (+5.04, door_cy, door_h / 2 + 0.02),
             (0.04, 0.85, door_h), COL_KITCHEN_STEEL)
    # Round porthole window in the door
    make_cyl("Galley_ServiceDoor_Porthole",
             (+5.07, door_cy, 1.45),
             0.10, 0.02, (0.42, 0.50, 0.56, 1.0),
             segments=10, axis='X')
    make_cyl("Galley_ServiceDoor_PortholeRing",
             (+5.07, door_cy, 1.45),
             0.12, 0.025, COL_BRASS,
             segments=10, axis='X')
    # Stainless push-plate (kick plate at the bottom)
    make_box("Galley_ServiceDoor_KickPlate",
             (+5.07, door_cy, 0.30),
             (0.02, 0.78, 0.20),
             (0.86, 0.86, 0.88, 1.0))
    # Wooden frame jambs + header
    for sy in (-4.85, -3.95):
        make_box(f"Galley_ServiceDoor_Jamb_{sy:.2f}",
                 (+5.0, sy, 1.05),
                 (0.14, 0.04, 2.10), COL_WOOD_TRIM)
    make_box("Galley_ServiceDoor_Header",
             (+5.0, door_cy, 2.12),
             (0.14, 0.95, 0.10), COL_WOOD_TRIM)
    # "OUT" sign above the door (red, brass-framed) — visible from inside
    # the kitchen so the cook knows which way the door swings
    make_box("Galley_ServiceDoor_OutSign",
             (+4.92, door_cy, 2.30),
             (0.02, 0.30, 0.10), COL_VINYL_RED)
    make_box("Galley_ServiceDoor_OutFrame",
             (+4.91, door_cy, 2.30),
             (0.015, 0.34, 0.14), COL_BRASS)


# ────────────────────────────────────────────────────────────────
# INTERIOR PARTITIONS — four-room east annex stack
# ────────────────────────────────────────────────────────────────
# Per user direction: bigger private dining, more room in entry, a
# hallway between vestibule and private/formal dining rooms, formal
# dining replaces the bar (bar moves to the NORTH annex with
# port-side windows).
#
#     +Y north
#     ┌─────────────────────┐
#     │  Formal Dining      │  X=+5..+9, Y=+1..+6  (5×4 = 20m²)
#     │  (east windows)     │
#     ├── door (Y=+1) ──────┤
#     │  Vestibule          │  X=+5..+9, Y=-1..+1  (2×4 =  8m²)
#     │  (hostess, larger)  │
#     ├── door (Y=-1) ──────┤
#     │  Annex Hallway      │  X=+5..+9, Y=-2.5..-1 (1.5×4 = 6m²)
#     │  W→main, S→private  │
#     ├── door (Y=-2.5) ────┤
#     │  Private Dining     │  X=+5..+9, Y=-6..-2.5 (3.5×4=14m²)
#     │  (Table 17)         │
#     └─────────────────────┘
# Bar moves to a new NORTH ANNEX (X=-9..-2.5, Y=+6..+10) with
# port-side windows on its west wall.

VEST_X_W           = +5.0      # west wall of the eastern annex stack
ANNEX_DOOR_W       = 0.90
# Y boundaries between annex rooms (top of formal=+6, going south)
FORMAL_HALL_Y      = +1.0      # vestibule north wall (extended foyer above is empty space, was old formal dining)
VEST_HALL_Y        = -1.0      # vestibule ↔ entry hallway south
ENTRY_HALL_S_Y     = -3.95     # entry hallway south end (matches galley N edge); L-bend zone Y=-3.95..-2.5
FORMAL_HALL_N_Y    = -2.5      # formal hallway north wall = PD south wall
HALL_PD_Y          = -2.5      # alias (legacy name kept for compat)
PD_W_X             = +2.0      # private dining west wall (small side room off the host stand)
PD_N_Y             = +1.0      # private dining north wall


def _annex_wall_with_door(prefix, y, door_x_center, door_w=0.90,
                           door_h=2.20, label_brass=None):
    """Helper: build a partition wall across the east-annex stack at
    a given Y, with one door opening cut at door_x_center.

    The wall runs X = VEST_X_W .. D_W/2, with a door gap and a lintel
    above. Optionally stencils a brass numeral set on the lintel.
    """
    wall_len_E = D_W / 2 - (door_x_center + door_w / 2)
    wall_len_W = (door_x_center - door_w / 2) - VEST_X_W
    if wall_len_W > 0.02:
        make_box(f"{prefix}_W_seg",
                 (VEST_X_W + wall_len_W / 2, y, D_H / 2),
                 (wall_len_W, 0.10, D_H), COL_WALL_INTERIOR)
    if wall_len_E > 0.02:
        make_box(f"{prefix}_E_seg",
                 (D_W / 2 - wall_len_E / 2, y, D_H / 2),
                 (wall_len_E, 0.10, D_H), COL_WALL_INTERIOR)
    # Lintel
    make_box(f"{prefix}_lintel",
             (door_x_center, y, door_h + (D_H - door_h) / 2),
             (door_w, 0.10, D_H - door_h), COL_WALL_INTERIOR)
    # Door frame (wood jambs + header)
    make_box(f"{prefix}_jamb_L",
             (door_x_center - door_w / 2 - 0.025, y, door_h / 2),
             (0.05, 0.14, door_h), COL_WOOD_TRIM)
    make_box(f"{prefix}_jamb_R",
             (door_x_center + door_w / 2 + 0.025, y, door_h / 2),
             (0.05, 0.14, door_h), COL_WOOD_TRIM)
    make_box(f"{prefix}_header",
             (door_x_center, y, door_h + 0.06),
             (door_w + 0.20, 0.14, 0.10), COL_WOOD_TRIM)
    if label_brass:
        for i, c in enumerate(label_brass):
            spacing = 0.06
            cx = door_x_center + (i - (len(label_brass) - 1) / 2.0) * spacing
            make_box(f"{prefix}_num_{i}",
                     (cx, y + 0.01, door_h + 0.18),
                     (0.045, 0.005, 0.10), COL_BRASS)


def build_interior_partitions():
    """L-shape hallway + private dining in the elbow.

    Per user direction: 90 deg hallway from the entrance going south
    (left from entrance / right from diner), then turning 90 deg west
    toward formal dining. Private dining sits in the L's elbow.

    Layout (in the east annex + main shell south middle):

         +6 ─────────────────────────────────────────
           [ enlarged VESTIBULE / coat-foyer ]   X=+5..+9
         +1 ──── FORMAL_HALL_Y ───────────
           [ vestibule + hostess          ]   Y=-1..+1
         -1 ──── VEST_HALL_Y ───
           [ ENTRY HALLWAY (going south)  ]   X=+5..+9, Y=-3.95..-1
       -3.95 ──── ENTRY_HALL_S_Y ───
           [ BATHROOMS + closet           ]   X=+5..+9, Y=-6..-3.95
         -6 ─────────────────────────────────

         L-bend opening at X=+5, Y=-3.95..-2.5 (east annex W wall is
         CUT in this Y range to let the formal hallway pass through).

    The FORMAL HALLWAY runs E->W:
         X=-9..+5, Y=-3.95..-2.5 (1.45m tall corridor)
         Hits the X=-9 partition wall at the door cut by build_shell
         at Y=-3.25 (door 2). That door opens into formal dining
         inside the west extension.

    PRIVATE DINING in the L-elbow:
         X=-1..+5, Y=-2.5..+1 (6m x 3.5m = 21 m^2)
         North wall at PD_N_Y=+1, west wall at PD_W_X=-1, east wall
         shared with east annex (X=+5), south wall shared with formal
         hallway (Y=-2.5). PD has one door on its south wall opening
         INTO the formal hallway.
    """
    # ── East-annex west wall (X=+5) — multi-segmented because the
    # L-bend opening cuts through it at Y=-3.95..-2.5 ──
    # Plus an archway from main floor into the vestibule at Y=+3 (in
    # the enlarged vestibule zone, above PD).
    vest_arch_y = +3.0
    vest_arch_w = 1.80
    arch_h = 2.50
    pd_arch_y = -0.0    # door from main floor into PD west wall (X=-1)
    pd_arch_w = 1.20

    # Solid segments along X=+5 (annex W wall):
    breaks = [
        (-D_D/2,                ENTRY_HALL_S_Y,         "VestWall_W_BR"),    # bathroom range (south)
        (FORMAL_HALL_N_Y,       vest_arch_y - vest_arch_w/2, "VestWall_W_PDeast"),  # solid wall north of formal-hall, south of vestibule arch
        (vest_arch_y + vest_arch_w/2, +D_D/2,           "VestWall_W_FoyerN"),
    ]
    for y_lo, y_hi, name in breaks:
        seg_len = y_hi - y_lo
        if seg_len < 0.02:
            continue
        make_box(name,
                 (VEST_X_W, (y_lo + y_hi)/2, D_H/2),
                 (0.10, seg_len, D_H), COL_WALL_INTERIOR)
    # Lintel above the vestibule arch
    make_box("VestWall_W_vestArch_lintel",
             (VEST_X_W, vest_arch_y, arch_h + (D_H - arch_h)/2),
             (0.10, vest_arch_w, D_H - arch_h), COL_WALL_INTERIOR)
    # Lintel above the L-bend opening (south of -2.5, north of -3.95)
    make_box("VestWall_W_LbendLintel",
             (VEST_X_W, (ENTRY_HALL_S_Y + FORMAL_HALL_N_Y)/2,
              2.20 + (D_H - 2.20)/2),
             (0.10, FORMAL_HALL_N_Y - ENTRY_HALL_S_Y, D_H - 2.20),
             COL_WALL_INTERIOR)
    # Trim around the vestibule arch
    make_box("VestArch_trim_top",
             (VEST_X_W - 0.04, vest_arch_y, arch_h - 0.04),
             (0.06, vest_arch_w + 0.20, 0.10), COL_WOOD_TRIM)
    for sgn in (-1, +1):
        make_box(f"VestArch_side_{sgn:+d}",
                 (VEST_X_W - 0.04,
                  vest_arch_y + sgn * vest_arch_w/2,
                  arch_h/2),
                 (0.06, 0.10, arch_h), COL_WOOD_TRIM)

    # ── Cross-walls inside the east annex ──
    # Vestibule south wall (Y=-1, splits vestibule from entry hallway)
    _annex_wall_with_door("VestHallPartition", VEST_HALL_Y,
                          door_x_center=+7.0, door_w=1.20)
    # Bathroom partition at ENTRY_HALL_S_Y (south of entry hallway)
    _annex_wall_with_door("BathroomPartition", ENTRY_HALL_S_Y,
                          door_x_center=+7.0, door_w=0.90)

    # ── Formal hallway north wall (Y=-2.5, X=-9..+5) ──
    # PD south wall (same wall, just from PD perspective)
    # Door at X=+3 lets patrons step from the formal hallway INTO PD.
    # PD south wall at Y=-2.5 — partial. Spans from PD west wall
    # (X=-1) to east annex west wall (X=+5). This is a SOLID
    # partition; PD's door is on its west wall instead. (We do NOT
    # extend this wall across the entire main shell, which would
    # bisect the counter + galley + booth row.)
    pd_s_len = VEST_X_W - PD_W_X       # 6m
    make_box("PD_SouthWall",
             ((PD_W_X + VEST_X_W) / 2, FORMAL_HALL_N_Y, D_H/2),
             (pd_s_len, 0.10, D_H), COL_WALL_INTERIOR)
    fh_door_h = 2.10    # reused below

    # ── Private dining west wall (X=-1) + north wall (Y=+1) ──
    # West wall has an archway at PD_N_Y=+1..-2.5 — wait actually no,
    # the west wall is solid (PD only has door on south wall to formal
    # hall). For atmosphere, add an archway opening from main floor.
    # Use a narrow door at Y=-1 on the PD west wall.
    pd_w_door_y = -1.5
    pd_w_door_w = 0.90
    seg_s_y = FORMAL_HALL_N_Y
    seg_n_y = PD_N_Y
    # West wall segments
    make_box("PD_WestWall_S",
             (PD_W_X, (seg_s_y + (pd_w_door_y - pd_w_door_w/2))/2, D_H/2),
             (0.10, (pd_w_door_y - pd_w_door_w/2) - seg_s_y, D_H),
             COL_WALL_INTERIOR)
    make_box("PD_WestWall_N",
             (PD_W_X, ((pd_w_door_y + pd_w_door_w/2) + seg_n_y)/2, D_H/2),
             (0.10, seg_n_y - (pd_w_door_y + pd_w_door_w/2), D_H),
             COL_WALL_INTERIOR)
    make_box("PD_WestWall_Lintel",
             (PD_W_X, pd_w_door_y, fh_door_h + (D_H - fh_door_h)/2),
             (0.10, pd_w_door_w, D_H - fh_door_h), COL_WALL_INTERIOR)
    for sgn in (-1, +1):
        make_box(f"PD_WestWall_Jamb_{sgn:+d}",
                 (PD_W_X - 0.04, pd_w_door_y + sgn * (pd_w_door_w/2 + 0.025),
                  fh_door_h/2),
                 (0.06, 0.05, fh_door_h), COL_WOOD_TRIM)
    make_box("PD_WestWall_Header",
             (PD_W_X - 0.04, pd_w_door_y, fh_door_h + 0.06),
             (0.06, pd_w_door_w + 0.20, 0.10), COL_WOOD_TRIM)
    # North wall (Y=+1) of PD — solid partition (no door)
    pd_n_len = VEST_X_W - PD_W_X
    make_box("PD_NorthWall",
             ((PD_W_X + VEST_X_W)/2, PD_N_Y, D_H/2),
             (pd_n_len, 0.10, D_H), COL_WALL_INTERIOR)


def build_formal_dining_room():
    """Formal dining in the NE annex (replaces the former bar room).
    X=+5..+9, Y=+1..+6 (5 x 4 = 20 sq m). Larger than the old bar.
    East wall (X=+9) has the picture window facing the porch/parking
    so diners see outside while eating.

    Per user direction: 'the formal dining room can have windows
    looking out over portside, as well.'
    """
    cx = (VEST_X_W + D_W / 2) / 2.0     # +7.0
    cy = (FORMAL_HALL_Y + D_D / 2) / 2.0  # +3.5
    room_w = D_W / 2 - VEST_X_W          # 4.0
    room_d = D_D / 2 - FORMAL_HALL_Y     # 5.0

    # Floor accent (warm wood plank look — formal-dining flooring)
    make_box("Formal_Floor_Accent", (cx, cy, 0.025),
             (room_w - 0.20, room_d - 0.20, 0.005),
             (0.22, 0.14, 0.08, 1.0))

    # ── Long formal dining table running E-W ──
    table_w = 2.80
    table_d = 1.00
    table_top_z = 0.76
    table_cx, table_cy = cx, cy
    make_box("Formal_Table_Top", (table_cx, table_cy, table_top_z),
             (table_w, table_d, 0.04), (0.94, 0.90, 0.78, 1.0))
    # White linen tablecloth (drape on all four sides)
    for sgn in (-1, +1):
        make_box(f"Formal_Cloth_NS_{sgn:+d}",
                 (table_cx, table_cy + sgn * (table_d/2 + 0.002),
                  table_top_z - 0.30),
                 (table_w + 0.04, 0.004, 0.60),
                 (0.94, 0.90, 0.78, 1.0))
        make_box(f"Formal_Cloth_EW_{sgn:+d}",
                 (table_cx + sgn * (table_w/2 + 0.002), table_cy,
                  table_top_z - 0.30),
                 (0.004, table_d + 0.04, 0.60),
                 (0.94, 0.90, 0.78, 1.0))
    # Brass center-runner (formal touch)
    make_box("Formal_Table_Runner", (table_cx, table_cy, table_top_z + 0.022),
             (table_w - 0.20, 0.30, 0.004), (0.62, 0.42, 0.24, 1.0))
    # Place settings (4 along the table on each side = 8 total)
    for side_sgn in (-1, +1):
        for p in range(4):
            sx = table_cx - 1.05 + p * 0.70
            sy = table_cy + side_sgn * 0.32
            # Plate
            make_cyl(f"Formal_Plate_{side_sgn:+d}_{p}",
                     (sx, sy, table_top_z + 0.045),
                     0.14, 0.012, (0.94, 0.92, 0.88, 1.0),
                     segments=10, axis='Z')
            # Charger plate (slightly larger underneath)
            make_cyl(f"Formal_Charger_{side_sgn:+d}_{p}",
                     (sx, sy, table_top_z + 0.030),
                     0.16, 0.010, (0.62, 0.42, 0.24, 1.0),
                     segments=10, axis='Z')
            # Cutlery (knife and fork as thin boxes)
            make_box(f"Formal_Knife_{side_sgn:+d}_{p}",
                     (sx + 0.20, sy, table_top_z + 0.025),
                     (0.20, 0.02, 0.005), COL_BRASS)
            make_box(f"Formal_Fork_{side_sgn:+d}_{p}",
                     (sx - 0.20, sy, table_top_z + 0.025),
                     (0.20, 0.02, 0.005), COL_BRASS)
            # Wine glass
            make_cyl(f"Formal_Glass_{side_sgn:+d}_{p}",
                     (sx + 0.04, sy - side_sgn * 0.22, table_top_z + 0.10),
                     0.030, 0.16, (0.86, 0.92, 0.94, 1.0),
                     segments=6, axis='Z')

    # 8 formal chairs (4 per long side)
    for side_sgn in (-1, +1):
        for c in range(4):
            cx_ch = table_cx - 1.05 + c * 0.70
            cy_ch = table_cy + side_sgn * 0.85
            make_box(f"Formal_Chair_{side_sgn:+d}_{c}_Seat",
                     (cx_ch, cy_ch, 0.46),
                     (0.42, 0.44, 0.06), (0.32, 0.20, 0.12, 1.0))
            # 4 legs
            for lx in (-1, +1):
                for ly in (-1, +1):
                    make_box(f"Formal_Chair_{side_sgn:+d}_{c}_Leg_{lx:+d}_{ly:+d}",
                             (cx_ch + lx * 0.18, cy_ch + ly * 0.19, 0.23),
                             (0.04, 0.04, 0.46), (0.32, 0.20, 0.12, 1.0))
            # Tall ladder-back (outward-facing side)
            back_dy = side_sgn * 0.19
            for bx_off in (-0.16, 0.0, +0.16):
                make_box(f"Formal_Chair_{side_sgn:+d}_{c}_Back_{bx_off:+.2f}",
                         (cx_ch + bx_off, cy_ch + back_dy, 0.82),
                         (0.04, 0.04, 0.70), (0.32, 0.20, 0.12, 1.0))
            make_box(f"Formal_Chair_{side_sgn:+d}_{c}_BackTop",
                     (cx_ch, cy_ch + back_dy, 1.16),
                     (0.40, 0.05, 0.05), (0.32, 0.20, 0.12, 1.0))
            # Damask seat cushion
            make_box(f"Formal_Chair_{side_sgn:+d}_{c}_Cushion",
                     (cx_ch, cy_ch, 0.50), (0.40, 0.40, 0.04),
                     COL_VINYL_RED_DK)
    # Captain chairs at the heads of the table
    for end_i, sgn_x in enumerate([+1, -1]):
        ecx = table_cx + sgn_x * (table_w / 2 + 0.45)
        ecy = table_cy
        make_box(f"Formal_HeadChair_{end_i}_Seat",
                 (ecx, ecy, 0.46), (0.46, 0.46, 0.06),
                 (0.32, 0.20, 0.12, 1.0))
        for lx in (-1, +1):
            for ly in (-1, +1):
                make_box(f"Formal_HeadChair_{end_i}_Leg_{lx:+d}_{ly:+d}",
                         (ecx + lx * 0.20, ecy + ly * 0.20, 0.23),
                         (0.04, 0.04, 0.46), (0.32, 0.20, 0.12, 1.0))
        back_dx = sgn_x * 0.20
        for bz_off in (-0.18, 0.0, +0.18):
            make_box(f"Formal_HeadChair_{end_i}_Back_{bz_off:+.2f}",
                     (ecx + back_dx, ecy + bz_off, 0.82),
                     (0.05, 0.04, 0.70), (0.32, 0.20, 0.12, 1.0))

    # ── Sideboard against the NORTH wall (Y=+6 area) ──
    sb_y = D_D / 2 - 0.30
    make_box("Formal_Sideboard_Body", (cx, sb_y, 0.50),
             (3.0, 0.55, 0.95), (0.40, 0.26, 0.16, 1.0))
    make_box("Formal_Sideboard_Top", (cx, sb_y, 1.00),
             (3.10, 0.60, 0.04), (0.30, 0.18, 0.10, 1.0))
    # 4 cabinet doors
    for d in range(4):
        dx_local = cx - 1.20 + d * 0.80
        make_box(f"Formal_Sideboard_Door_{d}",
                 (dx_local, sb_y - 0.28, 0.50),
                 (0.70, 0.005, 0.80), (0.26, 0.16, 0.10, 1.0))
        make_box(f"Formal_Sideboard_Handle_{d}",
                 (dx_local + 0.25, sb_y - 0.30, 0.55),
                 (0.10, 0.02, 0.018), COL_BRASS)
    # Decorative items on the sideboard
    # Crystal decanter
    make_cyl("Formal_Decanter", (cx - 1.10, sb_y - 0.10, 1.18),
             0.08, 0.32, (0.74, 0.60, 0.32, 1.0), segments=8, axis='Z')
    make_cyl("Formal_Decanter_Stopper",
             (cx - 1.10, sb_y - 0.10, 1.38),
             0.05, 0.08, (0.86, 0.74, 0.42, 1.0), segments=6, axis='Z')
    # Candelabra
    make_cyl("Formal_Candelabra_Base", (cx, sb_y - 0.10, 1.06),
             0.10, 0.06, COL_BRASS, segments=10, axis='Z')
    make_cyl("Formal_Candelabra_Stem", (cx, sb_y - 0.10, 1.20),
             0.025, 0.20, COL_BRASS, segments=6, axis='Z')
    for cnd in range(3):
        ang = math.radians(cnd * 120 - 60)
        cx_off = 0.10 * math.cos(ang)
        cy_off = 0.10 * math.sin(ang)
        make_cyl(f"Formal_Candle_{cnd}",
                 (cx + cx_off, sb_y - 0.10 + cy_off, 1.36),
                 0.018, 0.16, (0.96, 0.92, 0.82, 1.0),
                 segments=4, axis='Z')
        make_sphere_low(f"Formal_CandleFlame_{cnd}",
                        (cx + cx_off, sb_y - 0.10 + cy_off, 1.48),
                        0.04, (0.98, 0.78, 0.32, 1.0),
                        rings=2, segments=4)
    # Framed mirror above the sideboard
    make_box("Formal_Mirror_Frame", (cx, sb_y + 0.10, 2.10),
             (1.40, 0.05, 1.20), (0.40, 0.26, 0.14, 1.0))
    make_box("Formal_Mirror_Glass", (cx, sb_y + 0.12, 2.10),
             (1.20, 0.02, 1.00), (0.50, 0.54, 0.60, 1.0))

    # ── Brass chandelier overhead ──
    ch_z_top = D_H - 0.10
    ch_z_low = ch_z_top - 1.10
    make_cyl("Formal_Chandelier_Chain",
             (table_cx, table_cy, (ch_z_top + ch_z_low) / 2),
             0.014, ch_z_top - ch_z_low, COL_BRASS, segments=4, axis='Z')
    make_cyl("Formal_Chandelier_Body",
             (table_cx, table_cy, ch_z_low),
             0.14, 0.24, COL_BRASS, segments=10, axis='Z')
    # 6 candle bulbs in two rings (3 + 3)
    for ring_i, ring_r in enumerate([0.40, 0.62]):
        for ang_i in range(3):
            ang = math.radians(ang_i * 120 + ring_i * 60)
            ax = table_cx + ring_r * math.cos(ang)
            ay = table_cy + ring_r * math.sin(ang)
            make_cyl(f"Formal_Chandelier_Arm_{ring_i}_{ang_i}",
                     ((table_cx + ax) / 2, (table_cy + ay) / 2, ch_z_low - 0.04),
                     0.014, ring_r, COL_BRASS, segments=4,
                     axis='X' if abs(math.cos(ang)) > 0.5 else 'Y')
            make_cyl(f"Formal_Chandelier_Cup_{ring_i}_{ang_i}",
                     (ax, ay, ch_z_low + 0.06),
                     0.04, 0.08, COL_BRASS, segments=6, axis='Z')
            make_sphere_low(f"Formal_Chandelier_Bulb_{ring_i}_{ang_i}",
                            (ax, ay, ch_z_low + 0.18), 0.06,
                            (0.98, 0.86, 0.56, 1.0), rings=2, segments=6)


def build_private_dining_room():
    """Private dining as a small side room off the host stand.
    NEW DIMS (post-playtest): X=+2..+5 (3m wide), Y=-2.5..+1 (3.5m
    deep) = ~10 sq m. The east wall (X=+5) is shared with the
    vestibule; the host can seat VIPs to this room directly off the
    entry. Door is on the west wall (X=+2) at Y=-1.5 (1m wide)
    opening into the main diner floor. The OLD location had the
    room dominating the middle of the diner (X=-1..+5); shrinking
    east frees up the central floor.
    """
    pd_y_lo = -2.5            # FORMAL_HALL_N_Y
    pd_y_hi = +1.0            # PD_N_Y
    pd_x_w  = +2.0            # PD_W_X (was -1.0)
    pd_x_e  = +5.0            # VEST_X_W (shared with east annex)
    pd_cx = (pd_x_w + pd_x_e) / 2.0    # +3.5
    pd_cy = (pd_y_lo + pd_y_hi) / 2.0  # -0.75
    pd_w  = pd_x_e - pd_x_w            # 3
    pd_d  = pd_y_hi - pd_y_lo          # 3.5

    # Dark hardwood floor accent
    make_box("PrivDining_Floor_Accent", (pd_cx, pd_cy, 0.025),
             (pd_w - 0.20, pd_d - 0.20, 0.005),
             (0.18, 0.10, 0.06, 1.0))

    # ── Tablecloth-covered table (sized for the 3m wide room) ──
    table_w = 1.60
    table_d = 1.00
    table_top_z = 0.76
    make_box("PrivTable_Top", (pd_cx, pd_cy, table_top_z),
             (table_w, table_d, 0.04), (0.92, 0.88, 0.78, 1.0))
    for sgn in (-1, +1):
        make_box(f"PrivTable_Cloth_NS_{sgn:+d}",
                 (pd_cx, pd_cy + sgn * (table_d/2 + 0.002),
                  table_top_z - 0.30),
                 (table_w + 0.04, 0.004, 0.60),
                 (0.92, 0.88, 0.78, 1.0))
        make_box(f"PrivTable_Cloth_EW_{sgn:+d}",
                 (pd_cx + sgn * (table_w/2 + 0.002), pd_cy,
                  table_top_z - 0.30),
                 (0.004, table_d + 0.04, 0.60),
                 (0.92, 0.88, 0.78, 1.0))
    # 4 chairs (2 per long side, sized to the smaller room)
    for s_i, sgn in enumerate([+1, -1]):
        cy = pd_cy + sgn * 0.85
        for c_i in range(2):
            cx = pd_cx - 0.40 + c_i * 0.80
            make_box(f"PrivChair_{s_i}_{c_i}_seat",
                     (cx, cy, 0.46), (0.42, 0.44, 0.06), COL_WOOD_TRIM)
            for lx in (-1, +1):
                for ly in (-1, +1):
                    make_box(f"PrivChair_{s_i}_{c_i}_leg_{lx:+d}_{ly:+d}",
                             (cx + lx * 0.18, cy + ly * 0.19, 0.23),
                             (0.04, 0.04, 0.46), COL_WOOD_TRIM)
            back_dy = sgn * 0.19
            for bx_off in (-0.16, 0.0, +0.16):
                make_box(f"PrivChair_{s_i}_{c_i}_backpost_{bx_off:+.2f}",
                         (cx + bx_off, cy + back_dy, 0.82),
                         (0.04, 0.05, 0.66), COL_WOOD_TRIM)
            make_box(f"PrivChair_{s_i}_{c_i}_back_top",
                     (cx, cy + back_dy, 1.16),
                     (0.40, 0.06, 0.06), COL_WOOD_TRIM)
            make_box(f"PrivChair_{s_i}_{c_i}_cushion",
                     (cx, cy, 0.50), (0.38, 0.40, 0.04), COL_VINYL_RED)
    # Captain chairs at the heads
    for end_i, sgn_x in enumerate([+1, -1]):
        cx = pd_cx + sgn_x * (table_w/2 + 0.45)
        cy = pd_cy
        make_box(f"PrivChair_end_{end_i}_seat",
                 (cx, cy, 0.46), (0.42, 0.44, 0.06), COL_WOOD_TRIM)
        for lx in (-1, +1):
            for ly in (-1, +1):
                make_box(f"PrivChair_end_{end_i}_leg_{lx:+d}_{ly:+d}",
                         (cx + lx * 0.18, cy + ly * 0.19, 0.23),
                         (0.04, 0.04, 0.46), COL_WOOD_TRIM)
        back_dx = sgn_x * 0.19
        for bz_off in (-0.16, 0.0, +0.16):
            make_box(f"PrivChair_end_{end_i}_backpost_{bz_off:+.2f}",
                     (cx + back_dx, cy + bz_off, 0.82),
                     (0.05, 0.04, 0.66), COL_WOOD_TRIM)
        make_box(f"PrivChair_end_{end_i}_back_top",
                 (cx + back_dx, cy, 1.16),
                 (0.06, 0.40, 0.06), COL_WOOD_TRIM)

    # Tarot deck centerpiece (Table 17 Hierophant)
    make_box("Table17_TarotStack",
             (pd_cx, pd_cy, table_top_z + 0.04),
             (0.10, 0.16, 0.04), (0.92, 0.88, 0.72, 1.0))
    make_box("Table17_TopCard",
             (pd_cx + 0.05, pd_cy + 0.10, table_top_z + 0.025),
             (0.10, 0.16, 0.004), (0.94, 0.90, 0.72, 1.0))
    make_box("Table17_TopCard_Sigil",
             (pd_cx + 0.05, pd_cy + 0.10, table_top_z + 0.028),
             (0.04, 0.06, 0.002), COL_BRASS)
    make_box("Table17_Plaque",
             (pd_cx + table_w/2 - 0.10, pd_cy - table_d/2 + 0.10,
              table_top_z + 0.022),
             (0.08, 0.08, 0.005), COL_BRASS)

    # ── Brass chandelier ──
    ch_z_top = D_H - 0.10
    ch_z_low = ch_z_top - 0.90
    make_cyl("PrivChandelier_Chain",
             (pd_cx, pd_cy, (ch_z_top + ch_z_low) / 2.0),
             0.014, ch_z_top - ch_z_low, COL_BRASS, segments=4, axis='Z')
    make_cyl("PrivChandelier_Body",
             (pd_cx, pd_cy, ch_z_low),
             0.10, 0.20, COL_BRASS, segments=8, axis='Z')
    for ang_deg in (0, 90, 180, 270):
        ang = math.radians(ang_deg)
        ax = pd_cx + 0.30 * math.cos(ang)
        ay = pd_cy + 0.30 * math.sin(ang)
        make_cyl(f"PrivChandelier_Cup_{ang_deg}",
                 (ax, ay, ch_z_low + 0.04),
                 0.04, 0.06, COL_BRASS, segments=6, axis='Z')
        make_sphere_low(f"PrivChandelier_Bulb_{ang_deg}",
                        (ax, ay, ch_z_low + 0.14), 0.05,
                        (0.98, 0.86, 0.56, 1.0), rings=2, segments=6)

    # ── Sideboard against the NORTH wall of PD (Y=+1), sized to
    #     the smaller room ──
    sb_y = pd_y_hi - 0.30
    make_box("PrivSideboard_Body", (pd_cx, sb_y, 0.50),
             (1.80, 0.55, 0.95), COL_WOOD_TRIM)
    make_box("PrivSideboard_Top", (pd_cx, sb_y, 1.00),
             (1.90, 0.60, 0.04), (0.30, 0.18, 0.10, 1.0))
    for d in range(3):
        dx_local = pd_cx - 0.60 + d * 0.60
        make_box(f"PrivSideboard_Door_{d}",
                 (dx_local, sb_y + 0.28, 0.50),
                 (0.65, 0.005, 0.75), (0.22, 0.14, 0.08, 1.0))
        make_box(f"PrivSideboard_Handle_{d}",
                 (dx_local + 0.20, sb_y + 0.30, 0.55),
                 (0.10, 0.02, 0.018), COL_BRASS)
    make_cyl("PrivDecanter", (pd_cx - 0.70, sb_y + 0.10, 1.16),
             0.07, 0.30, (0.62, 0.42, 0.22, 1.0), segments=8, axis='Z')
    make_cyl("PrivDecanter_Stopper", (pd_cx - 0.70, sb_y + 0.10, 1.34),
             0.04, 0.06, (0.78, 0.62, 0.36, 1.0), segments=6, axis='Z')
    for g in range(4):
        gx = pd_cx - 0.20 + g * 0.20
        make_cyl(f"PrivGlass_{g}",
                 (gx, sb_y + 0.10, 1.10),
                 0.035, 0.10, (0.86, 0.90, 0.92, 1.0), segments=6, axis='Z')


def build_southeast_bathroom():
    """The former SE annex (X=+5..+9, Y=-6..-3.95) is now repurposed
    as the public bathroom + a small staff supply closet. Accessed
    from the entry hallway via a door at Y=-3.95 (built by
    build_interior_partitions BathroomPartition).

    Layout:
        Y=-6..-5.5  : staff supply closet (small)
        Y=-5.5..-3.95 : bathroom (2 stalls + sink + mirror)
    """
    BR_X_W = VEST_X_W                  # +5
    BR_X_E = D_W / 2                    # +9
    BR_cx = (BR_X_W + BR_X_E) / 2       # +7
    # Tile floor for the bathroom zone
    make_box("BR_Floor_Tile",
             (BR_cx, -4.7, 0.022),
             (BR_X_E - BR_X_W - 0.20, 1.45, 0.005),
             (0.86, 0.84, 0.76, 1.0))
    # Tile grout grid
    for i in range(1, 6):
        gx = BR_X_W + i * (BR_X_E - BR_X_W) / 6
        make_box(f"BR_Grout_V_{i}", (gx, -4.7, 0.027),
                 (0.025, 1.40, 0.003), (0.50, 0.46, 0.40, 1.0))
    # Bathroom partition between supply closet (south) + bathroom (north)
    make_box("BR_Partition",
             (BR_cx, -5.5, D_H/2),
             (BR_X_E - BR_X_W, 0.10, D_H), COL_WALL_INTERIOR)
    # 2 toilet stalls (small partition walls + toilets)
    for st in range(2):
        stall_cx = BR_X_W + 0.8 + st * 1.2
        # Stall side walls
        for sgn_x in (-1, +1):
            make_box(f"BR_Stall_{st}_Wall_{sgn_x:+d}",
                     (stall_cx + sgn_x * 0.50, -4.4, 1.20),
                     (0.04, 1.20, 1.80), (0.78, 0.76, 0.72, 1.0))
        # Stall door (lower / hinged style)
        make_box(f"BR_Stall_{st}_Door",
                 (stall_cx, -3.85, 1.20),
                 (0.90, 0.02, 1.60), (0.62, 0.40, 0.20, 1.0))
        # Toilet bowl (cylinder + box tank)
        make_cyl(f"BR_Stall_{st}_ToiletBowl",
                 (stall_cx, -4.7, 0.20),
                 0.18, 0.30, (0.94, 0.92, 0.86, 1.0), segments=10, axis='Z')
        make_box(f"BR_Stall_{st}_ToiletTank",
                 (stall_cx, -5.05, 0.65),
                 (0.40, 0.18, 0.50), (0.94, 0.92, 0.86, 1.0))
    # Sink + mirror against the east wall
    make_box("BR_Sink_Counter",
             (BR_X_E - 0.30, -4.5, 0.85),
             (0.50, 1.00, 0.04), (0.74, 0.74, 0.72, 1.0))
    make_cyl("BR_Sink_Basin",
             (BR_X_E - 0.30, -4.5, 0.84),
             0.18, 0.06, (0.86, 0.86, 0.82, 1.0), segments=10, axis='Z')
    make_cyl("BR_Sink_Faucet",
             (BR_X_E - 0.30, -4.5 + 0.15, 1.00),
             0.025, 0.16, COL_BRASS, segments=6, axis='Z')
    make_box("BR_Mirror",
             (BR_X_E - 0.08, -4.5, 1.40),
             (0.04, 0.80, 0.70), (0.50, 0.54, 0.58, 1.0))
    make_box("BR_Mirror_Frame",
             (BR_X_E - 0.07, -4.5, 1.40),
             (0.05, 0.86, 0.76), COL_WOOD_TRIM)
    # Hand-dryer + paper-towel dispenser (boxes against east wall)
    make_box("BR_HandDryer",
             (BR_X_E - 0.05, -4.5 + 0.60, 1.30),
             (0.10, 0.20, 0.30), (0.46, 0.44, 0.42, 1.0))
    # Trash bin (corner)
    make_cyl("BR_TrashBin",
             (BR_X_W + 0.30, -4.0, 0.30),
             0.16, 0.60, (0.30, 0.30, 0.32, 1.0), segments=8, axis='Z')

    # ── Supply closet (south of bathroom) ──
    SC_cx = BR_cx
    SC_cy = -5.75
    make_box("SC_Floor",
             (SC_cx, SC_cy, 0.022),
             (BR_X_E - BR_X_W - 0.20, 0.40, 0.005),
             (0.30, 0.22, 0.14, 1.0))
    # Two shelf units against north and east walls
    for unit_i, (ux, uy, uw_x, uw_y) in enumerate([
        (BR_X_W + 0.60, -5.85, 1.00, 0.20),
        (BR_X_E - 0.20, -5.75, 0.20, 0.40),
    ]):
        for sh in range(3):
            sz = 0.40 + sh * 0.50
            make_box(f"SC_Shelf_{unit_i}_{sh}",
                     (ux, uy, sz), (uw_x, uw_y, 0.04), COL_WOOD_TRIM)
    # Stacked boxes + cleaning supplies
    for b in range(3):
        bx = BR_X_W + 0.8 + b * 0.40
        make_box(f"SC_Box_{b}",
                 (bx, -5.80, 0.30),
                 (0.30, 0.30, 0.50),
                 [(0.42, 0.32, 0.18, 1.0),
                  (0.62, 0.42, 0.30, 1.0),
                  (0.32, 0.42, 0.22, 1.0)][b])
    # Mop and broom in corner (vertical cylinders)
    make_cyl("SC_Broom_Handle",
             (BR_X_W + 0.25, -5.85, 0.90),
             0.014, 1.70, COL_WOOD_TRIM, segments=4, axis='Z')
    make_cyl("SC_Mop_Handle",
             (BR_X_W + 0.42, -5.85, 0.85),
             0.014, 1.60, COL_BRASS, segments=4, axis='Z')


def build_annex_hallway():
    """The hallway in the east annex stack between the vestibule and
    the dining rooms. Y=-2.5..-1, X=+5..+9. Plain corridor with a few
    framed paintings, a small console table, and a runner rug.
    """
    hall_y_lo = HALL_PD_Y       # -2.5
    hall_y_hi = VEST_HALL_Y     # -1
    cx = (VEST_X_W + D_W / 2) / 2.0    # +7
    cy = (hall_y_lo + hall_y_hi) / 2.0  # -1.75
    hall_w = D_W / 2 - VEST_X_W         # 4
    hall_d = hall_y_hi - hall_y_lo      # 1.5
    # Runner rug down the center (Y-axis)
    make_box("AnnexHall_Rug", (cx, cy, 0.014),
             (hall_w - 0.40, hall_d - 0.20, 0.006),
             (0.42, 0.22, 0.16, 1.0))
    # Console table against the east wall (X=+9 interior)
    cons_x = D_W / 2 - 0.20
    make_box("AnnexHall_Console_Top", (cons_x, cy, 0.78),
             (0.36, 1.20, 0.04), (0.40, 0.26, 0.16, 1.0))
    for lx in (-1, +1):
        for ly in (-1, +1):
            make_box(f"AnnexHall_Console_Leg_{lx:+d}_{ly:+d}",
                     (cons_x + lx * 0.14, cy + ly * 0.55, 0.39),
                     (0.04, 0.04, 0.78), (0.30, 0.20, 0.10, 1.0))
    # Decorative item: lamp + small flower vase
    make_cyl("AnnexHall_LampBase",
             (cons_x, cy - 0.30, 0.86), 0.07, 0.06,
             COL_BRASS, segments=8, axis='Z')
    make_cyl("AnnexHall_LampPost",
             (cons_x, cy - 0.30, 1.05), 0.018, 0.30,
             COL_BRASS, segments=4, axis='Z')
    make_sphere_low("AnnexHall_LampShade",
                    (cons_x, cy - 0.30, 1.30), 0.13,
                    (0.62, 0.42, 0.22, 1.0), rings=2, segments=8)
    make_cyl("AnnexHall_Vase",
             (cons_x, cy + 0.40, 0.84),
             0.06, 0.18, (0.32, 0.46, 0.40, 1.0), segments=8, axis='Z')
    # 3 framed paintings on the west and east walls
    for i, (px, py, ny) in enumerate([
        (VEST_X_W + 0.06, cy + 0.40, 1),
        (VEST_X_W + 0.06, cy - 0.40, 1),
        (D_W/2 - 0.06,    cy + 0.55, -1),
    ]):
        make_box(f"AnnexHall_Painting_{i}_Frame",
                 (px, py, 1.80), (0.04, 0.50, 0.40),
                 (0.40, 0.26, 0.16, 1.0))
        make_box(f"AnnexHall_Painting_{i}_Canvas",
                 (px + 0.018 * (-1 if px < VEST_X_W + 0.5 else 1),
                  py, 1.80),
                 (0.02, 0.42, 0.32), (0.30, 0.20, 0.14, 1.0))


def build_north_annex_bar():
    """The bar moves out of the diner main shell into a NEW north
    annex with port-side (west) windows looking out over the river.
    Annex footprint: X=-9..-2.5, Y=+6..+10 (6.5 x 4 = 26 sq m).

    Per user direction: 'the bar can be expanded and have windows
    looking out over portside.'

    A doorway through the main-shell north wall at X=-6 connects
    the main floor to the bar.
    """
    BAR_X_W = -D_W / 2                    # -9
    BAR_X_E = -HALL_W / 2                 # -2.5 (shares wall with back hallway)
    BAR_Y_S = D_D / 2                     # +6 (main shell N wall)
    BAR_Y_N = D_D / 2 + 4.0               # +10 (annex extends 4m north)
    cx_bar = (BAR_X_W + BAR_X_E) / 2.0    # -5.75
    cy_bar = (BAR_Y_S + BAR_Y_N) / 2.0    # +8
    bar_w = BAR_X_E - BAR_X_W             # 6.5
    bar_d = BAR_Y_N - BAR_Y_S             # 4

    # Floor (warm wood plank — bar room flooring)
    make_box("Bar_Floor", (cx_bar, cy_bar, -0.05),
             (bar_w, bar_d, 0.10), (0.32, 0.22, 0.14, 1.0),
             open_faces={'-Z'})
    # Ceiling (dark, intimate)
    make_box("Bar_Ceiling", (cx_bar, cy_bar, D_H + 0.05),
             (bar_w, bar_d, 0.10), (0.10, 0.08, 0.06, 1.0),
             open_faces={'+Z'})
    # ── Walls ──
    # West wall — picture window facing port (river)
    bar_win_w = 5.0
    bar_win_h = 2.2
    bar_win_base = 0.9
    bar_win_upper = D_H - (bar_win_base + bar_win_h)
    bar_win_side = (bar_d - bar_win_w) / 2.0
    # Lower below window
    make_box("Bar_Wall_W_lower",
             (BAR_X_W - 0.05, cy_bar, bar_win_base / 2),
             (0.10, bar_d, bar_win_base), COL_BOAT_HULL if False else COL_WALL_INTERIOR)
    # Above
    make_box("Bar_Wall_W_above",
             (BAR_X_W - 0.05, cy_bar,
              bar_win_base + bar_win_h + bar_win_upper / 2),
             (0.10, bar_d, bar_win_upper), COL_WALL_INTERIOR)
    # End-walls north/south of window
    make_box("Bar_Wall_W_S",
             (BAR_X_W - 0.05, BAR_Y_S + bar_win_side / 2,
              bar_win_base + bar_win_h / 2),
             (0.10, bar_win_side, bar_win_h), COL_WALL_INTERIOR)
    make_box("Bar_Wall_W_N",
             (BAR_X_W - 0.05, BAR_Y_N - bar_win_side / 2,
              bar_win_base + bar_win_h / 2),
             (0.10, bar_win_side, bar_win_h), COL_WALL_INTERIOR)
    # Brass picture-window frame + mullions (no glass slab —
    # see-through picture window)
    for c in range(1, 4):
        my = -bar_win_w / 2 + c * bar_win_w / 4
        make_box(f"BarWin_W_MullV_{c}",
                 (BAR_X_W - 0.04, cy_bar + my, bar_win_base + bar_win_h / 2),
                 (0.02, 0.06, bar_win_h), COL_BRASS)
    make_box("BarWin_W_MullH",
             (BAR_X_W - 0.04, cy_bar, bar_win_base + bar_win_h / 2),
             (0.02, bar_win_w, 0.06), COL_BRASS)
    make_box("BarWin_W_FrameT",
             (BAR_X_W - 0.03, cy_bar, bar_win_base + bar_win_h + 0.06),
             (0.04, bar_win_w + 0.20, 0.12), COL_BRASS)
    make_box("BarWin_W_FrameB",
             (BAR_X_W - 0.03, cy_bar, bar_win_base - 0.06),
             (0.04, bar_win_w + 0.20, 0.12), COL_BRASS)
    for sgn in (-1, +1):
        make_box(f"BarWin_W_FrameSide_{sgn:+d}",
                 (BAR_X_W - 0.03, cy_bar + sgn * (bar_win_w / 2 + 0.06),
                  bar_win_base + bar_win_h / 2),
                 (0.04, 0.12, bar_win_h + 0.24), COL_BRASS)

    # North wall (Y=BAR_Y_N) — solid plus small north window
    n_win_w = 3.0
    n_win_h = 1.6
    n_win_base = 1.1
    n_win_side = (bar_w - n_win_w) / 2.0
    n_win_upper = D_H - (n_win_base + n_win_h)
    make_box("Bar_Wall_N_lower",
             (cx_bar, BAR_Y_N + 0.05, n_win_base / 2),
             (bar_w, 0.10, n_win_base), COL_WALL_INTERIOR)
    make_box("Bar_Wall_N_above",
             (cx_bar, BAR_Y_N + 0.05,
              n_win_base + n_win_h + n_win_upper / 2),
             (bar_w, 0.10, n_win_upper), COL_WALL_INTERIOR)
    make_box("Bar_Wall_N_W",
             (BAR_X_W + n_win_side / 2, BAR_Y_N + 0.05,
              n_win_base + n_win_h / 2),
             (n_win_side, 0.10, n_win_h), COL_WALL_INTERIOR)
    make_box("Bar_Wall_N_E",
             (BAR_X_E - n_win_side / 2, BAR_Y_N + 0.05,
              n_win_base + n_win_h / 2),
             (n_win_side, 0.10, n_win_h), COL_WALL_INTERIOR)
    # Brass frame
    for c in range(1, 3):
        mx = -n_win_w / 2 + c * n_win_w / 3
        make_box(f"BarWin_N_MullV_{c}",
                 (cx_bar + mx, BAR_Y_N + 0.04, n_win_base + n_win_h / 2),
                 (0.06, 0.02, n_win_h), COL_BRASS)
    make_box("BarWin_N_FrameT",
             (cx_bar, BAR_Y_N + 0.03, n_win_base + n_win_h + 0.06),
             (n_win_w + 0.20, 0.04, 0.12), COL_BRASS)
    make_box("BarWin_N_FrameB",
             (cx_bar, BAR_Y_N + 0.03, n_win_base - 0.06),
             (n_win_w + 0.20, 0.04, 0.12), COL_BRASS)

    # South wall (shared with main shell N wall at Y=+6) — interrupted
    # by a doorway at X=-6 (1.4m wide). The main-shell N wall is
    # built by build_shell — we need to BREAK it here. We do that by
    # overlaying a wood-frame doorway gap "indicator" rather than
    # modifying build_shell. NOTE: the existing Wall_N_E_of_hall in
    # build_shell still spans the main floor's full north wall.
    # To make this work, the bar door rendering goes through that
    # wall — players still see the door geometry, but the wall
    # behind it isn't physically broken in the mesh. (A later pass
    # can refactor build_shell to take a parameter for the bar door
    # cut.)
    bar_door_x = -6.0
    bar_door_w = 1.40
    bar_door_h = 2.20
    # Door frame jambs + header
    make_box("BarDoor_Jamb_L",
             (bar_door_x - bar_door_w / 2 - 0.025, BAR_Y_S,
              bar_door_h / 2),
             (0.05, 0.14, bar_door_h), COL_WOOD_TRIM)
    make_box("BarDoor_Jamb_R",
             (bar_door_x + bar_door_w / 2 + 0.025, BAR_Y_S,
              bar_door_h / 2),
             (0.05, 0.14, bar_door_h), COL_WOOD_TRIM)
    make_box("BarDoor_Header",
             (bar_door_x, BAR_Y_S, bar_door_h + 0.06),
             (bar_door_w + 0.20, 0.14, 0.10), COL_WOOD_TRIM)
    # Brass "BAR" sign above the door (visible from main floor)
    make_box("BarDoor_Sign",
             (bar_door_x, BAR_Y_S - 0.03, bar_door_h + 0.30),
             (0.60, 0.06, 0.16), COL_BAR_WOOD)
    for i, c in enumerate("BAR"):
        make_box(f"BarDoor_Sign_Char_{i}",
                 (bar_door_x + (i - 1) * 0.16, BAR_Y_S - 0.04,
                  bar_door_h + 0.30),
                 (0.10, 0.005, 0.08), COL_BRASS)

    # East wall (shared with back hallway) — solid, simple
    make_box("Bar_Wall_E", (BAR_X_E + 0.05, cy_bar, D_H / 2),
             (0.10, bar_d, D_H), COL_WALL_INTERIOR)

    # ── BAR COUNTER running E-W along the south wall (port-view side
    #    — patrons sit at the bar looking through the W picture
    #    window) ──
    bar_top_z = 1.10
    bar_len = bar_w - 1.20
    bar_cy_int = BAR_Y_S + 0.8     # bar 0.8m north of the south wall
    bar_cx_int = cx_bar
    make_box("Bar_Top", (bar_cx_int, bar_cy_int, bar_top_z),
             (bar_len, 0.70, 0.06), COL_BAR_WOOD)
    make_box("Bar_Front",
             (bar_cx_int, bar_cy_int - 0.35, 0.55),
             (bar_len, 0.04, 1.10), COL_VINYL_RED_DK)
    make_cyl("Bar_FootRail", (bar_cx_int, bar_cy_int - 0.36, 0.18),
             0.024, bar_len, COL_BRASS, segments=8, axis='X')
    # Back-bar shelves against the south wall
    bb_y = BAR_Y_S + 0.20
    make_box("BarBack_Cabinet",
             (bar_cx_int, bb_y, 0.65),
             (bar_len, 0.30, 1.30), COL_BAR_WOOD)
    for s in range(3):
        sz = 1.45 + s * 0.40
        make_box(f"BarBack_Shelf_{s}",
                 (bar_cx_int, bb_y + 0.05, sz),
                 (bar_len, 0.20, 0.03), COL_WOOD_TRIM)
        for b in range(9):
            bx = bar_cx_int - bar_len / 2 + 0.20 + b * (bar_len - 0.40) / 8
            bottle_color = [
                (0.18, 0.32, 0.20, 1.0),
                (0.42, 0.20, 0.10, 1.0),
                (0.62, 0.46, 0.20, 1.0),
                (0.30, 0.18, 0.34, 1.0),
                (0.86, 0.74, 0.36, 1.0),
                (0.20, 0.16, 0.34, 1.0),
                (0.74, 0.20, 0.18, 1.0),
            ][(b + s) % 7]
            make_cyl(f"Bottle_N_{s}_{b}",
                     (bx, bb_y + 0.05, sz + 0.16), 0.035, 0.30,
                     bottle_color, segments=6, axis='Z')
    # Backbar mirror (the iconic "bar with a mirror behind it")
    make_box("BarBack_Mirror",
             (bar_cx_int, bb_y + 0.16, 2.40),
             (bar_len - 0.20, 0.04, 1.20),
             (0.30, 0.34, 0.40, 1.0))
    make_box("BarBack_Mirror_Frame",
             (bar_cx_int, bb_y + 0.14, 2.40),
             (bar_len, 0.06, 1.35), COL_WOOD_TRIM)

    # Bar stools (6 — facing south, customers look at the back-bar
    # and the river through the W window over their shoulder)
    n_stools = 6
    for i in range(n_stools):
        sx = bar_cx_int - bar_len/2 + 0.55 + i * (bar_len - 1.10) / (n_stools - 1)
        sy = bar_cy_int - 1.00
        # Post
        make_cyl(f"BarStool_N_{i}_post", (sx, sy, 0.40),
                 0.04, 0.80, COL_BRASS, segments=6, axis='Z')
        # Foot ring
        make_cyl(f"BarStool_N_{i}_foot", (sx, sy, 0.22),
                 0.18, 0.025, COL_BRASS, segments=8, axis='Z')
        # Leather seat
        make_cyl(f"BarStool_N_{i}_seat", (sx, sy, 0.82),
                 0.22, 0.07, (0.32, 0.18, 0.10, 1.0), segments=10, axis='Z')
        # Low back
        make_cyl(f"BarStool_N_{i}_back_rod", (sx, sy - 0.16, 1.05),
                 0.016, 0.40, COL_BRASS, segments=4, axis='Z')
        make_box(f"BarStool_N_{i}_back_pad", (sx, sy - 0.18, 1.20),
                 (0.32, 0.04, 0.16), (0.32, 0.18, 0.10, 1.0))

    # Two cocktail 2-tops along the north (window-side) wall, for
    # patrons who want to face the river through the picture window
    for i, (tx, ty) in enumerate([(BAR_X_W + 1.5, BAR_Y_N - 1.3),
                                    (BAR_X_E - 1.5, BAR_Y_N - 1.3)]):
        make_cyl(f"BarPort_Table_{i}_Top", (tx, ty, 0.92),
                 0.40, 0.04, COL_FORMICA, segments=12, axis='Z')
        make_cyl(f"BarPort_Table_{i}_Post", (tx, ty, 0.46),
                 0.035, 0.92, COL_BRASS, segments=6, axis='Z')
        make_cyl(f"BarPort_Table_{i}_Foot", (tx, ty, 0.03),
                 0.22, 0.04, (0.16, 0.14, 0.12, 1.0), segments=10, axis='Z')
        # Two stools (facing each other across the table)
        for sgn in (-1, +1):
            sx = tx
            sy = ty + sgn * 0.55
            make_cyl(f"BarPort_Stool_{i}_{sgn:+d}",
                     (sx, sy, 0.82), 0.20, 0.07,
                     (0.32, 0.18, 0.10, 1.0), segments=10, axis='Z')

    # Pendant lamps over the bar (3)
    for i, plx in enumerate([bar_cx_int - 2.0, bar_cx_int, bar_cx_int + 2.0]):
        plz = 2.40
        make_cyl(f"BarPendant_{i}_Wire",
                 (plx, bar_cy_int, (plz + D_H - 0.05) / 2),
                 0.010, (D_H - 0.05) - plz,
                 COL_PAYPHONE_DARK, segments=4, axis='Z')
        make_cyl(f"BarPendant_{i}_Shade",
                 (plx, bar_cy_int, plz), 0.16, 0.18,
                 (0.52, 0.30, 0.16, 1.0), segments=8, axis='Z')
        make_sphere_low(f"BarPendant_{i}_Bulb",
                        (plx, bar_cy_int, plz - 0.16), 0.05,
                        (0.96, 0.78, 0.42, 1.0), rings=2, segments=6)


COL_BOAT_HULL = (0.82, 0.78, 0.66, 1.0)   # for hull-skin extensions


def build_hull_extensions():
    """Extend the riverboat hull clapboard skin to cover the back
    hallway exterior + BBS closet annex + new north bar annex.
    Fixes the 'wall by the closet seems to be exposed to the
    elements' complaint — those walls now have a proper clapboard
    skin matching the rest of the boat.
    """
    skin_t = 0.06
    COL_TRIM = (0.50, 0.20, 0.16, 1.0)    # red trim band

    # Back hallway exterior (north of main shell, X=-2.5..+2.5,
    # Y=+6..+8.4). The hallway's outer walls are the building's
    # external skin from here. Wrap with clapboard.
    HX_W, HX_E = -HALL_W / 2, HALL_W / 2
    HY_S, HY_N = D_D / 2, D_D / 2 + HALL_D
    # West skin
    make_box("Hull_Hall_W",
             (HX_W - 0.06, (HY_S + HY_N) / 2, D_H / 2),
             (skin_t, HALL_D, D_H), COL_BOAT_HULL)
    # East skin (only south of the closet opening; closet covers north)
    closet_door_y = +7.7
    # Lower segment (south of closet door)
    seg_s_len = closet_door_y - 0.45 - HY_S
    if seg_s_len > 0.05:
        make_box("Hull_Hall_E_S",
                 (HX_E + 0.06, HY_S + seg_s_len / 2, D_H / 2),
                 (skin_t, seg_s_len, D_H), COL_BOAT_HULL)
    # Upper segment (north of closet door — but the closet is east
    # of here so this section is INSIDE the building if we count
    # the closet)
    # Actually the closet sits at X=+2.5..+4, Y=+7..+8.4. So between
    # closet south wall (Y=+7) and the door area (Y=+7.45..+7.95), we
    # need skin from Y=+6.95 to +7.45 maybe. Just simpler: wrap from
    # Y=closet door bottom (+7.45) upward to the hallway's north end
    # (where the closet's east wall takes over).
    # The closet occupies Y=+7..+8.4 east of X=+2.5. North of Y=+8.4
    # there's nothing — the closet's north wall is the boundary.
    # Hallway north wall (Y=+8.4) — wrap with skin
    make_box("Hull_Hall_N",
             ((HX_W + HX_E) / 2, HY_N + 0.06, D_H / 2),
             (HALL_W, skin_t, D_H), COL_BOAT_HULL)
    # Red trim band at the hallway eaves
    band_z = D_H - 0.20
    make_box("Hull_Hall_Cornice_W",
             (HX_W - 0.08, (HY_S + HY_N) / 2, band_z),
             (skin_t + 0.04, HALL_D + 0.20, 0.16),
             (0.86, 0.82, 0.72, 1.0))
    make_box("Hull_Hall_Cornice_N",
             ((HX_W + HX_E) / 2, HY_N + 0.08, band_z),
             (HALL_W + 0.20, skin_t + 0.04, 0.16),
             (0.86, 0.82, 0.72, 1.0))

    # ── BBS Closet annex: X=+2.5..+4, Y=+7..+8.4 ──
    CX_W, CX_E = +2.5, +4.0
    CY_S, CY_N = +7.0, +8.4
    # East skin
    make_box("Hull_Closet_E",
             (CX_E + 0.06, (CY_S + CY_N) / 2, D_H / 2),
             (skin_t, CY_N - CY_S, D_H), COL_BOAT_HULL)
    # North skin
    make_box("Hull_Closet_N",
             ((CX_W + CX_E) / 2, CY_N + 0.06, D_H / 2),
             (CX_E - CX_W, skin_t, D_H), COL_BOAT_HULL)
    # South skin
    make_box("Hull_Closet_S",
             ((CX_W + CX_E) / 2, CY_S - 0.06, D_H / 2),
             (CX_E - CX_W, skin_t, D_H), COL_BOAT_HULL)
    # Cornices
    make_box("Hull_Closet_Cornice_E",
             (CX_E + 0.08, (CY_S + CY_N) / 2, band_z),
             (skin_t + 0.04, CY_N - CY_S + 0.20, 0.16),
             (0.86, 0.82, 0.72, 1.0))
    make_box("Hull_Closet_Cornice_N",
             ((CX_W + CX_E) / 2, CY_N + 0.08, band_z),
             (CX_E - CX_W + 0.20, skin_t + 0.04, 0.16),
             (0.86, 0.82, 0.72, 1.0))

    # ── New North-Annex Bar: X=-9..-2.5, Y=+6..+10 ──
    BX_W, BX_E = -D_W / 2, -HALL_W / 2
    BY_S, BY_N = D_D / 2, D_D / 2 + 4.0
    # West skin (river side — covered separately by bar room's
    # picture window. Skin around the window)
    bar_win_base = 0.9
    bar_win_h = 2.2
    bar_win_w = 5.0
    bar_cy = (BY_S + BY_N) / 2
    # Skin below window
    make_box("Hull_BarAnnex_W_below",
             (BX_W - 0.06, bar_cy, bar_win_base / 2),
             (skin_t, BY_N - BY_S, bar_win_base), COL_BOAT_HULL)
    # Skin above window
    upper_h = D_H - (bar_win_base + bar_win_h)
    make_box("Hull_BarAnnex_W_above",
             (BX_W - 0.06, bar_cy, bar_win_base + bar_win_h + upper_h / 2),
             (skin_t, BY_N - BY_S, upper_h), COL_BOAT_HULL)
    # Skin north/south of window
    side_d = (BY_N - BY_S - bar_win_w) / 2
    make_box("Hull_BarAnnex_W_S",
             (BX_W - 0.06, BY_S + side_d / 2,
              bar_win_base + bar_win_h / 2),
             (skin_t, side_d, bar_win_h), COL_BOAT_HULL)
    make_box("Hull_BarAnnex_W_N",
             (BX_W - 0.06, BY_N - side_d / 2,
              bar_win_base + bar_win_h / 2),
             (skin_t, side_d, bar_win_h), COL_BOAT_HULL)
    # North skin (with windows already cut by the bar room itself —
    # use 2 strip skins)
    n_win_w_local = 3.0
    n_win_h_local = 1.6
    n_win_base_local = 1.1
    cx_bar = (BX_W + BX_E) / 2
    n_win_side = (BX_E - BX_W - n_win_w_local) / 2.0
    n_win_upper = D_H - (n_win_base_local + n_win_h_local)
    make_box("Hull_BarAnnex_N_lower",
             (cx_bar, BY_N + 0.06, n_win_base_local / 2),
             (BX_E - BX_W, skin_t, n_win_base_local), COL_BOAT_HULL)
    make_box("Hull_BarAnnex_N_above",
             (cx_bar, BY_N + 0.06,
              n_win_base_local + n_win_h_local + n_win_upper / 2),
             (BX_E - BX_W, skin_t, n_win_upper), COL_BOAT_HULL)
    make_box("Hull_BarAnnex_N_W",
             (BX_W + n_win_side / 2, BY_N + 0.06,
              n_win_base_local + n_win_h_local / 2),
             (n_win_side, skin_t, n_win_h_local), COL_BOAT_HULL)
    make_box("Hull_BarAnnex_N_E",
             (BX_E - n_win_side / 2, BY_N + 0.06,
              n_win_base_local + n_win_h_local / 2),
             (n_win_side, skin_t, n_win_h_local), COL_BOAT_HULL)
    # Cornices on bar annex
    make_box("Hull_BarAnnex_Cornice_W",
             (BX_W - 0.08, bar_cy, band_z),
             (skin_t + 0.04, BY_N - BY_S + 0.20, 0.16),
             (0.86, 0.82, 0.72, 1.0))
    make_box("Hull_BarAnnex_Cornice_N",
             (cx_bar, BY_N + 0.08, band_z),
             (BX_E - BX_W + 0.20, skin_t + 0.04, 0.16),
             (0.86, 0.82, 0.72, 1.0))
    # Red trim band on bar annex outer walls
    trim_z = 0.95
    make_box("Hull_BarAnnex_RedBand_W",
             (BX_W - 0.08, bar_cy, trim_z),
             (skin_t + 0.04, BY_N - BY_S + 0.20, 0.18),
             COL_TRIM)
    make_box("Hull_BarAnnex_RedBand_N",
             (cx_bar, BY_N + 0.08, trim_z),
             (BX_E - BX_W + 0.20, skin_t + 0.04, 0.18), COL_TRIM)

    # ── NEW: Portside extension hull skin (X=-15..-9, Y=-6..+6) ──
    EX_X_W = -D_W / 2 - WEST_EXT_W      # -15
    EX_X_E = -D_W / 2                    # -9
    EX_Y_S = -D_D / 2                    # -6
    EX_Y_N =  D_D / 2                    # +6
    ex_cx  = (EX_X_W + EX_X_E) / 2.0     # -12
    ex_cy  = (EX_Y_S + EX_Y_N) / 2.0     # 0
    ex_d   = EX_Y_N - EX_Y_S             # 12
    # West outer wall — skin AROUND the picture window
    ex_win_w_local = 10.0
    ex_win_h_local = 2.5
    ex_win_base_local = 0.85
    ex_upper_local = D_H - (ex_win_base_local + ex_win_h_local)
    ex_side_local = (ex_d - ex_win_w_local) / 2
    make_box("Hull_WestExt_W_below",
             (EX_X_W - 0.06, ex_cy, ex_win_base_local / 2),
             (skin_t, ex_d, ex_win_base_local), COL_BOAT_HULL)
    make_box("Hull_WestExt_W_above",
             (EX_X_W - 0.06, ex_cy,
              ex_win_base_local + ex_win_h_local + ex_upper_local / 2),
             (skin_t, ex_d, ex_upper_local), COL_BOAT_HULL)
    make_box("Hull_WestExt_W_S",
             (EX_X_W - 0.06, EX_Y_S + ex_side_local / 2,
              ex_win_base_local + ex_win_h_local / 2),
             (skin_t, ex_side_local, ex_win_h_local), COL_BOAT_HULL)
    make_box("Hull_WestExt_W_N",
             (EX_X_W - 0.06, EX_Y_N - ex_side_local / 2,
              ex_win_base_local + ex_win_h_local / 2),
             (skin_t, ex_side_local, ex_win_h_local), COL_BOAT_HULL)
    # North wall skin
    make_box("Hull_WestExt_N",
             (ex_cx, EX_Y_N + 0.06, D_H / 2),
             (WEST_EXT_W, skin_t, D_H), COL_BOAT_HULL)
    # South wall skin
    make_box("Hull_WestExt_S",
             (ex_cx, EX_Y_S - 0.06, D_H / 2),
             (WEST_EXT_W, skin_t, D_H), COL_BOAT_HULL)
    # Cornices
    make_box("Hull_WestExt_Cornice_W",
             (EX_X_W - 0.08, ex_cy, band_z),
             (skin_t + 0.04, ex_d + 0.20, 0.16),
             (0.86, 0.82, 0.72, 1.0))
    make_box("Hull_WestExt_Cornice_N",
             (ex_cx, EX_Y_N + 0.08, band_z),
             (WEST_EXT_W + 0.20, skin_t + 0.04, 0.16),
             (0.86, 0.82, 0.72, 1.0))
    make_box("Hull_WestExt_Cornice_S",
             (ex_cx, EX_Y_S - 0.08, band_z),
             (WEST_EXT_W + 0.20, skin_t + 0.04, 0.16),
             (0.86, 0.82, 0.72, 1.0))
    # Red trim band at z=0.95 wrapping the extension's outer walls
    make_box("Hull_WestExt_RedBand_W",
             (EX_X_W - 0.08, ex_cy, trim_z),
             (skin_t + 0.04, ex_d + 0.20, 0.18), COL_TRIM)
    make_box("Hull_WestExt_RedBand_N",
             (ex_cx, EX_Y_N + 0.08, trim_z),
             (WEST_EXT_W + 0.20, skin_t + 0.04, 0.18), COL_TRIM)
    make_box("Hull_WestExt_RedBand_S",
             (ex_cx, EX_Y_S - 0.08, trim_z),
             (WEST_EXT_W + 0.20, skin_t + 0.04, 0.18), COL_TRIM)


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
    """Two slow industrial ceiling fans — cylinder motor housing,
    downrod from ceiling, 4 angled blades, glass light globe.
    Previous version was boxy; user flagged "rectangular ceiling
    fans" — this rebuild uses cylinders / spheres for the parts that
    read as round in real fans."""
    fan_z = D_H - 0.30           # motor housing center height
    for label, (fx, fy) in [
        ("N", (-3.0, 0.5)),
        ("S", (+3.0, 0.5)),
    ]:
        # Ceiling-mount canopy (flat disc against ceiling)
        make_cyl(f"Fan_{label}_Canopy",
                 (fx, fy, D_H - 0.04),
                 0.12, 0.06, COL_FAN_HOUSING, segments=12, axis='Z')
        # Downrod (slim cylinder dropping from canopy to motor)
        downrod_top = D_H - 0.08
        downrod_bot = fan_z + 0.08
        make_cyl(f"Fan_{label}_Downrod",
                 (fx, fy, (downrod_top + downrod_bot) / 2),
                 0.022, downrod_top - downrod_bot,
                 COL_FAN_HOUSING, segments=6, axis='Z')
        # Motor housing (cylinder — the round drum that real fans have)
        make_cyl(f"Fan_{label}_Housing",
                 (fx, fy, fan_z),
                 0.22, 0.22, COL_FAN_HOUSING, segments=14, axis='Z')
        # Cap top + bottom plates (slightly larger discs)
        make_cyl(f"Fan_{label}_Housing_Top",
                 (fx, fy, fan_z + 0.115),
                 0.24, 0.02,
                 (0.42, 0.36, 0.30, 1.0), segments=14, axis='Z')
        make_cyl(f"Fan_{label}_Housing_Btm",
                 (fx, fy, fan_z - 0.115),
                 0.24, 0.02,
                 (0.42, 0.36, 0.30, 1.0), segments=14, axis='Z')
        # 4 blades radiating from the motor — long, slim, slightly
        # darker on the leading edge (suggests pitch)
        import math as _m
        for b in range(4):
            ang = b * (_m.pi / 2)     # 0°, 90°, 180°, 270°
            ux, uy = _m.cos(ang), _m.sin(ang)
            blade_len = 0.78
            blade_w   = 0.20
            blade_h   = 0.020
            # blade center is ~0.30 away from the motor along the
            # radial direction (so inner edge of blade meets the
            # housing); blade slightly tilted is faked by sitting
            # 1.5 cm below the housing midline
            bx = fx + (0.30 + blade_len / 2) * ux
            by = fy + (0.30 + blade_len / 2) * uy
            bz = fan_z - 0.02
            # Choose box size based on blade orientation
            if abs(ux) > abs(uy):
                bw_x, bw_y = blade_len, blade_w
            else:
                bw_x, bw_y = blade_w, blade_len
            make_box(f"Fan_{label}_Blade_{b}",
                     (bx, by, bz),
                     (bw_x, bw_y, blade_h), COL_FAN_BLADE)
            # Leading edge trim (slightly darker thin strip on one
            # side of the blade — suggests blade pitch / shadow)
            edge_off_x = -uy * (blade_w / 2 - 0.012)
            edge_off_y = +ux * (blade_w / 2 - 0.012)
            edge_size_x = blade_len if abs(ux) > abs(uy) else 0.018
            edge_size_y = 0.018 if abs(ux) > abs(uy) else blade_len
            make_box(f"Fan_{label}_BladeEdge_{b}",
                     (bx + edge_off_x, by + edge_off_y, bz + 0.005),
                     (edge_size_x, edge_size_y, 0.006),
                     (0.42, 0.36, 0.30, 1.0))
            # Brass blade arm bracket (between housing and blade)
            arm_x = fx + 0.26 * ux
            arm_y = fy + 0.26 * uy
            make_box(f"Fan_{label}_BladeArm_{b}",
                     (arm_x, arm_y, fan_z - 0.06),
                     (0.04 if abs(ux) > abs(uy) else 0.06,
                      0.04 if abs(uy) > abs(ux) else 0.06,
                      0.10), COL_BRASS)
        # Pull-chain (thin dangling cord with small ball at the end)
        make_cyl(f"Fan_{label}_PullChain",
                 (fx + 0.08, fy + 0.04, fan_z - 0.32),
                 0.005, 0.30, (0.40, 0.32, 0.18, 1.0),
                 segments=4, axis='Z')
        make_sphere_low(f"Fan_{label}_PullChain_Ball",
                        (fx + 0.08, fy + 0.04, fan_z - 0.48),
                        0.025, COL_BRASS, rings=2, segments=4)
        # Light fixture below the fan — brass cup + sphere globe
        make_cyl(f"Fan_{label}_GlobeMount",
                 (fx, fy, fan_z - 0.26),
                 0.10, 0.06, COL_BRASS, segments=8, axis='Z')
        make_sphere_low(f"Fan_{label}_Globe",
                        (fx, fy, fan_z - 0.46),
                        0.22, (0.96, 0.92, 0.78, 1.0),
                        rings=3, segments=10)


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

    # ── John Frank's wear spot on the formica ──
    # Per setup_the_leap.json scene_description: "You have been wiping
    # this spot of formica for eleven years." Subtle darker patch at
    # the canonical counter vantage (host SPACE_MAP "counter" =
    # (-0.85, -4.1) south of the counter, so the wear is just patron-
    # side of where John Frank stands behind it).
    make_box("Counter_WearSpot",
             (-0.85, cy - 0.15, counter_top_z + 0.001),
             (0.50, 0.32, 0.001),
             (0.74, 0.72, 0.66, 1.0))  # subtly darker than COL_FORMICA
    # ── Faith the dog · curled under the counter ──
    # Per setup_the_leap.json: "Faith — the dog whose name you stopped
    # saying — is curled under the counter." Tiny low-poly geometry
    # at the canonical John Frank station, just under the counter
    # overhang. Three boxes (body / head / tail) read as a sleeping
    # mid-sized dog from any walkable vantage.
    faith_x = -0.85
    faith_y = cy + 0.30   # under the patron side overhang
    faith_z = 0.12        # on the floor
    # Body (longer than wide)
    make_box("Faith_Body",
             (faith_x, faith_y, faith_z + 0.10),
             (0.42, 0.30, 0.20),
             (0.62, 0.46, 0.30, 1.0))   # warm brown fur
    # Head (smaller box, slightly forward of the body)
    make_box("Faith_Head",
             (faith_x - 0.20, faith_y, faith_z + 0.12),
             (0.18, 0.22, 0.18),
             (0.62, 0.46, 0.30, 1.0))
    # Snout (darker, tucked into the head)
    make_box("Faith_Snout",
             (faith_x - 0.28, faith_y, faith_z + 0.08),
             (0.10, 0.14, 0.08),
             (0.42, 0.30, 0.20, 1.0))
    # Curled tail (small box on the other side of the body)
    make_box("Faith_Tail",
             (faith_x + 0.22, faith_y + 0.08, faith_z + 0.06),
             (0.10, 0.06, 0.08),
             (0.62, 0.46, 0.30, 1.0))
    # Two paws peeking out
    for px_off in (-0.10, +0.10):
        make_box(f"Faith_Paw_{px_off:+.2f}",
                 (faith_x + px_off, faith_y - 0.14, faith_z + 0.04),
                 (0.06, 0.06, 0.06),
                 (0.74, 0.58, 0.40, 1.0))


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
    # Framed photos relocated to the EAST ANNEX PARTITION WALL, facing
    # west into the main dining floor (south wall is now occupied by
    # the riverboat galley line). 5 photos along the upper Y range.
    for i, fy in enumerate([+1.5, +2.6, +3.7, +4.8, +5.5]):
        make_box(f"WallPhoto_Frame_{i}",
                 (+4.93, fy, 2.40),
                 (0.04, 0.55, 0.42), COL_PHOTO_FRAME)
        make_box(f"WallPhoto_Image_{i}",
                 (+4.92, fy, 2.40),
                 (0.02, 0.45, 0.34), COL_NAPKIN)
    # Neon "OPEN" sign in the front window (south of front-door area —
    # still on south wall above galley, high enough to clear the hood)
    make_box("NeonOpenSign",
             (+6.5, D_D/2 - 0.10, 2.30),
             (1.20, 0.06, 0.45), (0.95, 0.32, 0.62, 1.0))
    # Chalkboard daily-specials — moved AGAIN to the east-annex
    # west wall in the VESTIBULE section (Y=-0.2, above the L-bend
    # opening). Visible to arriving patrons standing at the hostess.
    make_box("Chalkboard_Frame",
             (+4.93, -0.2, 1.70),
             (0.04, 1.20, 0.90), COL_WOOD_TRIM)
    make_box("Chalkboard_Slate",
             (+4.91, -0.2, 1.70),
             (0.02, 1.10, 0.78), (0.10, 0.12, 0.10, 1.0))
    for i in range(4):
        line_z = 1.95 - i * 0.16
        line_w = 0.85 - i * 0.10
        make_box(f"Chalkboard_Line_{i}",
                 (+4.90, -0.2 - 0.05, line_z),
                 (0.005, line_w, 0.025),
                 (0.86, 0.86, 0.80, 1.0))


def build_entry_props():
    """Hostess stand + coat rack INSIDE the vestibule, where the
    hostess routes patrons between three doors (main floor / bar /
    private dining). REBUILT post-playtest — the original had a
    1m³ podium with five accessories overlapping the top edge,
    reading as a mess. New: wider, slightly shorter podium; lamp
    moved to the far back corner so the surface reads clean; menu
    stack in brown leather instead of bright red; reservation book
    centered; small brass signs moved to the front face (no
    floating row above the top)."""
    # Hostess podium centered E-W in the vestibule (X=+7, midway
    # between the main-floor archway at X=+5 and the front-door
    # zone at X=+9), pulled to the SOUTH side of the vestibule
    # (Y=-0.7) so the north half stays a clear traffic lane between
    # the front door and the archway. Wider footprint (0.80 x 0.50
    # vs old 0.50 x 0.50) reads as a proper podium instead of a
    # tall narrow cube; the podium's long axis runs E-W so it
    # doesn't block N-S traffic.
    px, py = +7.0, -0.7
    pod_top_z = 1.08
    make_box("HostessStand_Base", (px, py, pod_top_z / 2.0),
             (0.80, 0.50, pod_top_z), COL_WOOD_TRIM)
    # Slanted "lectern" top — the patron-facing side is lower for
    # the reservation book to read at an angle.
    make_box("HostessStand_Top", (px, py, pod_top_z + 0.025),
             (0.86, 0.56, 0.05), (0.42, 0.30, 0.18, 1.0))
    # Reservation book centered on the slanted top.
    make_box("Reservation_Book", (px, py, pod_top_z + 0.075),
             (0.26, 0.20, 0.03), (0.32, 0.18, 0.10, 1.0))
    make_box("Reservation_Book_Pages",
             (px, py, pod_top_z + 0.094),
             (0.24, 0.18, 0.005), COL_NAPKIN)
    make_cyl("Reservation_Pen",
             (px + 0.05, py + 0.12, pod_top_z + 0.105),
             0.005, 0.13, COL_BRASS, segments=4, axis='X')
    # Menus stacked at the back-right corner (no longer the loud
    # bright-red read — brown leather binders).
    make_box("Menus_Stack",
             (px + 0.28, py + 0.15, pod_top_z + 0.08),
             (0.18, 0.14, 0.10), (0.30, 0.18, 0.10, 1.0))
    # Pen cup at the FRONT-RIGHT corner (was back-left, overlapped
    # the lamp).
    make_cyl("Pen_Cup",
             (px + 0.28, py - 0.15, pod_top_z + 0.06),
             0.028, 0.07, COL_BRASS, segments=6, axis='Z')
    # Four small brass signs on the FRONT face of the base (was a
    # floating row above the top — moved down so the top reads
    # clean and the signs read as proper brass routing plaques).
    for i, label in enumerate(["Sign_MainDining", "Sign_Bar",
                               "Sign_Formal", "Sign_Private"]):
        sx_off = -0.30 + i * 0.20
        make_box(label,
                 (px + sx_off, py - 0.252, 0.85),
                 (0.16, 0.005, 0.07), COL_BRASS)
    # Banker's lamp moved to the FAR-BACK-LEFT corner so the
    # podium surface stays clear. Smaller shade too.
    lamp_x, lamp_y = px - 0.28, py + 0.18
    make_box("HostessLamp_Base",
             (lamp_x, lamp_y, pod_top_z + 0.04),
             (0.09, 0.09, 0.04), COL_BRASS)
    make_cyl("HostessLamp_Post",
             (lamp_x, lamp_y, pod_top_z + 0.16),
             0.012, 0.20, COL_BRASS, segments=4, axis='Z')
    make_box("HostessLamp_Shade",
             (lamp_x, lamp_y, pod_top_z + 0.30),
             (0.16, 0.12, 0.05),
             (0.20, 0.34, 0.18, 1.0))   # green banker's shade, dimmer

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
    # ── Three framed arcana prints relocated to the east-annex
    # partition wall (south wall is now the galley). Each lives in a
    # thematically appropriate spot rather than a row on one wall:
    #   · Fool       → main dining floor, east-annex wall lower section
    #   · Magician   → back hallway, west wall near the BBS closet
    #   · Hierophant → private dining interior (Table 17 = Hierophant)
    arcana_specs = [
        # (label, surface_x, surface_y, normal_axis, base, accent)
        # normal_axis 'X' → frame is flat against an east/west wall;
        # normal_axis 'Y' → frame is flat against a north/south wall.
        # Fool — on the east-annex W wall north of vestibule arch
        # (above the L-bend opening so it isn't floating in a gap).
        ("Fool",       +4.92, +4.5, 'X', COL_VINYL_RED,    COL_BRASS),
        # Magician — back hallway west wall (near BBS closet)
        ("Magician",   -2.45, +7.0, 'X', COL_PAYPHONE_DARK, COL_BRASS),
        # Hierophant — INSIDE the new PD, on its NORTH wall facing
        # the table from above (PD spans Y=-2.5..+1; mount the print
        # on the inside face of the Y=+1 north wall)
        ("Hierophant", +2.0,  +0.94, 'Y', COL_VINYL_RED,    COL_PHOTO_FRAME),
    ]
    for i, (label, sx, sy, nax, base, accent) in enumerate(arcana_specs):
        if nax == 'X':
            frame_sz  = (0.04, 0.40, 0.62)
            card_sz   = (0.02, 0.32, 0.54)
            sigil_sz  = (0.005, 0.10, 0.10)
            title_sz  = (0.005, 0.26, 0.04)
        else:
            frame_sz  = (0.40, 0.04, 0.62)
            card_sz   = (0.32, 0.02, 0.54)
            sigil_sz  = (0.10, 0.005, 0.10)
            title_sz  = (0.26, 0.005, 0.04)
        make_box(f"Gauntlet_ArcanaFrame_{label}",
                 (sx, sy, 1.50), frame_sz, COL_PHOTO_FRAME)
        make_box(f"Gauntlet_ArcanaCard_{label}",
                 (sx + (0.01 if nax == 'X' else 0.0),
                  sy + (0.0 if nax == 'X' else 0.01), 1.50),
                 card_sz, COL_CARD_PAPER)
        make_box(f"Gauntlet_ArcanaSigil_{label}",
                 (sx + (0.015 if nax == 'X' else 0.0),
                  sy + (0.0 if nax == 'X' else 0.015), 1.66),
                 sigil_sz, accent)
        make_box(f"Gauntlet_ArcanaTitle_{label}",
                 (sx + (0.015 if nax == 'X' else 0.0),
                  sy + (0.0 if nax == 'X' else 0.015), 1.30),
                 title_sz, base)
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
    # ── A dice cup (with 2 dice spilling out) at the FRONT-LEFT
    # corner of the rebuilt podium ──
    px, py = +7.0, -0.7    # matches hostess stand (rebuilt + centered post-playtest)
    pod_top_z = 1.13       # matches rebuilt podium top (1.08 + 0.05 slanted top)
    make_cyl("Gauntlet_DiceCup",
             (px - 0.28, py - 0.10, pod_top_z + 0.05),
             0.040, 0.10, COL_BAR_WOOD, segments=8, axis='Z')
    make_box("Gauntlet_Die1",
             (px - 0.18, py - 0.10, pod_top_z + 0.02),
             (0.04, 0.04, 0.04), COL_NAPKIN)
    make_box("Gauntlet_Die2",
             (px - 0.22, py - 0.18, pod_top_z + 0.02),
             (0.04, 0.04, 0.04), COL_NAPKIN)
    # Dice pips (a couple of dark dots on top)
    make_box("Gauntlet_Die1_Pip",
             (px - 0.18, py - 0.10, pod_top_z + 0.041),
             (0.012, 0.012, 0.002), COL_PAYPHONE_DARK)
    make_box("Gauntlet_Die2_Pip",
             (px - 0.22, py - 0.18, pod_top_z + 0.041),
             (0.012, 0.012, 0.002), COL_PAYPHONE_DARK)


def build_riverboat_superstructure():
    """Riverboat features rising from the diner shell so the building
    reads as 'half-restaurant, half-riverboat-architecture' per canon
    (_VOL5_WIKI). Matches the boat in build_riverfront.py:

      · 3 stacked decks: main porch (Z=0) + saloon walking deck
        (Z=3.5) + hurricane promenade (Z=6.1)
      · Saloon-deck cabin (a second story above the diner)
      · Pilothouse on the hurricane deck
      · Twin smokestacks rising 11.5m above the main deck
      · Half stern paddle wheel visible on the south side
      · Gangway plank from the porch down to the dock level
      · Aged white clapboard + red trim band + brass railings
        (the riverfront palette)
    """
    # ── Riverboat palette (matches build_riverfront.py) ──
    COL_BOAT_HULL   = (0.82, 0.78, 0.66, 1.0)   # aged white clapboard
    COL_BOAT_TRIM   = (0.50, 0.20, 0.16, 1.0)   # red trim band
    COL_BOAT_DECK   = (0.42, 0.32, 0.18, 1.0)   # weathered teak plank
    COL_BOAT_SEAM   = (0.20, 0.14, 0.08, 1.0)
    COL_BOAT_STACK  = (0.10, 0.08, 0.06, 1.0)   # smokestack black
    COL_BOAT_WHEEL  = (0.62, 0.40, 0.22, 1.0)   # paddle-wheel wood
    COL_BOAT_GINGER = (0.86, 0.82, 0.72, 1.0)   # gingerbread fretwork

    # ── Repaint clapboard of the existing diner shell exterior to
    # match the riverboat hull — done by overlaying a 5cm "skin" of
    # clapboard slats around the outside of the existing walls ──
    skin_t = 0.06   # thin skin clapboard slabs
    # West-wall clapboard skin REMOVED — the old X=-9 wall is now
    # interior partition between the main floor and the new portside
    # extension. The clapboard skin for the ACTUAL outer west wall
    # at X=-15 is built by build_hull_extensions instead.
    # North wall hull skin (minus hallway opening)
    make_box("Hull_N_E_of_hall",
             (D_W/2 * 0.65, D_D/2 + 0.06, D_H / 2),
             (D_W - HALL_W, skin_t, D_H), COL_BOAT_HULL)
    make_box("Hull_N_above_hall",
             (0, D_D/2 + 0.06, D_H - 0.5),
             (HALL_W, skin_t, 1.0), COL_BOAT_HULL)
    # South wall hull skin (single piece)
    make_box("Hull_S",
             (0, -D_D/2 - 0.06, D_H / 2),
             (D_W + 0.20, skin_t, D_H), COL_BOAT_HULL)
    # Red trim band wrapping around the hull at the porch-roof line (z = 0.95m)
    band_z = 0.95
    band_h = 0.18
    for label, x, y, sx, sy in [
        ("W", -D_W/2 - 0.08, 0, skin_t + 0.02, D_D + 0.30),
        ("S", 0, -D_D/2 - 0.08, D_W + 0.30, skin_t + 0.02),
        ("N", 0, D_D/2 + 0.08, D_W + 0.30, skin_t + 0.02),
    ]:
        make_box(f"Hull_RedBand_{label}",
                 (x, y, band_z), (sx, sy, band_h), COL_BOAT_TRIM)
    # A higher cornice band just below the roof (white + red dentil)
    cornice_z = D_H - 0.20
    for label, x, y, sx, sy in [
        ("W", -D_W/2 - 0.08, 0, skin_t + 0.04, D_D + 0.30),
        ("S", 0, -D_D/2 - 0.08, D_W + 0.30, skin_t + 0.04),
        ("N", 0, D_D/2 + 0.08, D_W + 0.30, skin_t + 0.04),
    ]:
        make_box(f"Hull_Cornice_{label}",
                 (x, y, cornice_z), (sx, sy, 0.16), COL_BOAT_GINGER)

    # ════════════════════════════════════════════════════════════════
    # SALOON DECK — the walking surface ABOVE the diner roof
    # ════════════════════════════════════════════════════════════════
    saloon_deck_z = D_H + 0.10        # 3.5m
    # Deck wraps the WHOLE building including the new west portside
    # extension — so when the player looks at the boat from outside,
    # there's no step/dropoff between the main shell roof and the
    # extension roof. The saloon cabin still sits at the original
    # main-shell location; the extra deck west of it is open
    # walkway (which is canonical for riverboat upper decks).
    deck_overhang = 1.0
    deck_total_w = D_W + WEST_EXT_W           # 24 m combined building width
    deck_w = deck_total_w + 2 * deck_overhang  # 26 m with overhangs
    deck_d = D_D + 2 * deck_overhang
    deck_cx = (-D_W/2 - WEST_EXT_W + D_W/2) / 2.0   # = -WEST_EXT_W/2 = -3
    # The walking surface itself (one big slab — cabin sits on top
    # of the main-shell portion; west portion is open walkway)
    make_box("BoilerDeck_Slab",
             (deck_cx, 0, saloon_deck_z),
             (deck_w, deck_d, 0.10), COL_BOAT_DECK)
    # Plank seams running E-W along the deck
    n_seams = 12
    for i in range(1, n_seams):
        py = -deck_d / 2 + i * deck_d / n_seams
        make_box(f"BoilerDeck_Plank_{i}",
                 (deck_cx, py, saloon_deck_z + 0.055),
                 (deck_w - 0.2, 0.02, 0.005), COL_BOAT_SEAM)
    # Deck-edge moulding (cornice-like rim)
    deck_x_W = deck_cx - deck_w / 2.0
    deck_x_E = deck_cx + deck_w / 2.0
    for label, x, y, sx, sy in [
        ("W", deck_x_W, 0, 0.06, deck_d),
        ("E", deck_x_E, 0, 0.06, deck_d),
        ("N", deck_cx, +deck_d/2, deck_w, 0.06),
        ("S", deck_cx, -deck_d/2, deck_w, 0.06),
    ]:
        make_box(f"BoilerDeck_Edge_{label}",
                 (x, y, saloon_deck_z + 0.02),
                 (sx, sy, 0.12), COL_BOAT_TRIM)

    # ── Saloon cabin: a 2nd-story superstructure on the boiler deck ──
    saloon_w = D_W - 2.0
    saloon_d = D_D - 2.0
    saloon_h = 2.6
    saloon_floor_z = saloon_deck_z + 0.05
    saloon_cz = saloon_floor_z + saloon_h / 2.0
    # Walls (four sides) — clapboard
    for label, x, y, sx, sy in [
        ("W", -saloon_w/2, 0, 0.12, saloon_d),
        ("E", +saloon_w/2, 0, 0.12, saloon_d),
        ("N", 0, +saloon_d/2, saloon_w, 0.12),
        ("S", 0, -saloon_d/2, saloon_w, 0.12),
    ]:
        make_box(f"Saloon_Wall_{label}",
                 (x, y, saloon_cz), (sx, sy, saloon_h), COL_BOAT_HULL)
    # A row of windows around the saloon (decorative — dark recesses)
    sa_win_h = 1.20
    sa_win_w = 0.70
    sa_win_z = saloon_floor_z + 0.70
    n_win_long = 10   # along the W and E sides (N-S, count)
    n_win_short = 6   # along the N and S sides
    for w in range(n_win_long):
        wy = -saloon_d/2 + (w + 0.5) * saloon_d / n_win_long
        for sgn_x, side in [(-1, 'W'), (+1, 'E')]:
            make_box(f"Saloon_Window_{side}_{w}",
                     (sgn_x * (saloon_w/2 + 0.005), wy,
                      sa_win_z),
                     (0.02, sa_win_w, sa_win_h),
                     (0.30, 0.36, 0.42, 1.0))
            # Brass frame around each window
            make_box(f"Saloon_Window_{side}_{w}_FrameT",
                     (sgn_x * (saloon_w/2 + 0.012), wy,
                      sa_win_z + sa_win_h/2 + 0.03),
                     (0.012, sa_win_w + 0.08, 0.06), COL_BRASS)
            make_box(f"Saloon_Window_{side}_{w}_FrameB",
                     (sgn_x * (saloon_w/2 + 0.012), wy,
                      sa_win_z - sa_win_h/2 - 0.03),
                     (0.012, sa_win_w + 0.08, 0.06), COL_BRASS)
    for w in range(n_win_short):
        wx = -saloon_w/2 + (w + 0.5) * saloon_w / n_win_short
        for sgn_y, side in [(-1, 'S'), (+1, 'N')]:
            make_box(f"Saloon_Window_{side}_{w}",
                     (wx, sgn_y * (saloon_d/2 + 0.005),
                      sa_win_z),
                     (sa_win_w, 0.02, sa_win_h),
                     (0.30, 0.36, 0.42, 1.0))
            make_box(f"Saloon_Window_{side}_{w}_FrameT",
                     (wx, sgn_y * (saloon_d/2 + 0.012),
                      sa_win_z + sa_win_h/2 + 0.03),
                     (sa_win_w + 0.08, 0.012, 0.06), COL_BRASS)
            make_box(f"Saloon_Window_{side}_{w}_FrameB",
                     (wx, sgn_y * (saloon_d/2 + 0.012),
                      sa_win_z - sa_win_h/2 - 0.03),
                     (sa_win_w + 0.08, 0.012, 0.06), COL_BRASS)
    # Saloon red trim band at the wall midpoint
    saloon_band_z = saloon_floor_z + 0.30
    for label, x, y, sx, sy in [
        ("W", -saloon_w/2 - 0.07, 0, 0.04, saloon_d + 0.10),
        ("E", +saloon_w/2 + 0.07, 0, 0.04, saloon_d + 0.10),
        ("N", 0, +saloon_d/2 + 0.07, saloon_w + 0.10, 0.04),
        ("S", 0, -saloon_d/2 - 0.07, saloon_w + 0.10, 0.04),
    ]:
        make_box(f"Saloon_RedBand_{label}",
                 (x, y, saloon_band_z), (sx, sy, 0.14), COL_BOAT_TRIM)
    # Saloon roof — a slight cantilever above the cabin
    saloon_roof_z = saloon_floor_z + saloon_h + 0.05
    make_box("Saloon_Roof",
             (0, 0, saloon_roof_z),
             (saloon_w + 0.40, saloon_d + 0.40, 0.12), COL_BOAT_DECK)
    # Roof rim trim
    for label, x, y, sx, sy in [
        ("W", -(saloon_w + 0.40)/2, 0, 0.04, saloon_d + 0.40),
        ("E", +(saloon_w + 0.40)/2, 0, 0.04, saloon_d + 0.40),
        ("N", 0, +(saloon_d + 0.40)/2, saloon_w + 0.40, 0.04),
        ("S", 0, -(saloon_d + 0.40)/2, saloon_w + 0.40, 0.04),
    ]:
        make_box(f"SaloonRoof_Edge_{label}",
                 (x, y, saloon_roof_z + 0.07),
                 (sx, sy, 0.08), COL_BOAT_TRIM)

    # ── Brass railings around the BOILER deck walking surface ──
    rail_top_z = saloon_deck_z + 1.00
    rail_mid_z = saloon_deck_z + 0.55
    rail_low_z = saloon_deck_z + 0.20
    # Top + mid rails on the perimeter, broken by the saloon cabin
    # (we just run rails on the OUTER edge of the walkway). Now
    # wraps the combined building footprint at X=deck_x_W..deck_x_E.
    for x_rail, suffix in [(deck_x_W, 'W'), (deck_x_E, 'E')]:
        for z, r in [(rail_top_z, 0.030), (rail_mid_z, 0.022), (rail_low_z, 0.018)]:
            make_cyl(f"BD_Rail_{suffix}_z{z:.2f}",
                     (x_rail, 0, z), r, deck_d, COL_BRASS,
                     segments=6, axis='Y')
    for sgn_y in (-1, +1):
        y_rail = sgn_y * deck_d / 2
        for z, r in [(rail_top_z, 0.030), (rail_mid_z, 0.022), (rail_low_z, 0.018)]:
            make_cyl(f"BD_Rail_Y_{sgn_y:+d}_z{z:.2f}",
                     (deck_cx, y_rail, z), r, deck_w, COL_BRASS,
                     segments=6, axis='X')
    # Stanchions every 1.5m around the (now wider) perimeter
    spacing = 1.5
    n_post_y = int(deck_d / spacing)
    for i in range(n_post_y + 1):
        py = -deck_d/2 + i * deck_d / n_post_y
        for x_rail, suffix in [(deck_x_W, 'W'), (deck_x_E, 'E')]:
            make_cyl(f"BD_Stanchion_{suffix}_{i}",
                     (x_rail, py, saloon_deck_z + 0.55),
                     0.025, 1.10, COL_BRASS, segments=4, axis='Z')
    n_post_x = int(deck_w / spacing)
    for i in range(n_post_x + 1):
        px = deck_x_W + i * deck_w / n_post_x
        for sgn_y in (-1, +1):
            make_cyl(f"BD_Stanchion_Y_{sgn_y:+d}_{i}",
                     (px, sgn_y * deck_d/2, saloon_deck_z + 0.55),
                     0.025, 1.10, COL_BRASS, segments=4, axis='Z')

    # ════════════════════════════════════════════════════════════════
    # HURRICANE DECK — open promenade ABOVE the saloon cabin
    # ════════════════════════════════════════════════════════════════
    hurricane_z = saloon_roof_z + 0.05
    hurricane_w = saloon_w + 0.40
    hurricane_d = saloon_d + 0.40
    # Walking surface
    make_box("HurricaneDeck_Slab",
             (0, 0, hurricane_z),
             (hurricane_w, hurricane_d, 0.10), COL_BOAT_DECK)
    # Plank seams
    for i in range(1, 10):
        py = -hurricane_d/2 + i * hurricane_d/10
        make_box(f"Hurricane_Plank_{i}",
                 (0, py, hurricane_z + 0.055),
                 (hurricane_w - 0.2, 0.02, 0.005), COL_BOAT_SEAM)
    # Lighter brass railing (2-tier) around the hurricane deck
    for sgn_x in (-1, +1):
        x_rail = sgn_x * hurricane_w/2
        for z in (hurricane_z + 0.95, hurricane_z + 0.50):
            make_cyl(f"HD_Rail_{sgn_x:+d}_z{z:.2f}",
                     (x_rail, 0, z), 0.022, hurricane_d,
                     COL_BRASS, segments=6, axis='Y')
    for sgn_y in (-1, +1):
        y_rail = sgn_y * hurricane_d/2
        for z in (hurricane_z + 0.95, hurricane_z + 0.50):
            make_cyl(f"HD_Rail_Y_{sgn_y:+d}_z{z:.2f}",
                     (0, y_rail, z), 0.022, hurricane_w,
                     COL_BRASS, segments=6, axis='X')
    # Stanchions
    n_post = 8
    for i in range(n_post + 1):
        py = -hurricane_d/2 + i * hurricane_d/n_post
        for sgn_x in (-1, +1):
            make_cyl(f"HD_Stanch_{sgn_x:+d}_{i}",
                     (sgn_x * hurricane_w/2, py, hurricane_z + 0.55),
                     0.022, 1.00, COL_BRASS, segments=4, axis='Z')

    # ════════════════════════════════════════════════════════════════
    # PILOTHOUSE on the hurricane deck (forward-of-center)
    # ════════════════════════════════════════════════════════════════
    pilot_w, pilot_d, pilot_h = 3.6, 3.0, 2.40
    pilot_cy = hurricane_d/2 - pilot_d/2 - 0.40   # forward-of-center
    pilot_floor_z = hurricane_z + 0.10
    pilot_cz = pilot_floor_z + pilot_h/2
    # Walls
    for label, x, y, sx, sy in [
        ("W", -pilot_w/2, pilot_cy, 0.10, pilot_d),
        ("E", +pilot_w/2, pilot_cy, 0.10, pilot_d),
        ("N", 0, pilot_cy + pilot_d/2, pilot_w, 0.10),
        ("S", 0, pilot_cy - pilot_d/2, pilot_w, 0.10),
    ]:
        make_box(f"Pilot_Wall_{label}",
                 (x, y, pilot_cz), (sx, sy, pilot_h), COL_BOAT_HULL)
    # Big windows on all 4 sides
    pw_z = pilot_floor_z + 1.40
    for sgn_x, side in [(-1, 'W'), (+1, 'E')]:
        make_box(f"Pilot_Win_{side}",
                 (sgn_x * (pilot_w/2 + 0.005), pilot_cy, pw_z),
                 (0.02, pilot_d - 0.40, 1.20), (0.32, 0.38, 0.44, 1.0))
    for sgn_y, side in [(-1, 'S'), (+1, 'N')]:
        make_box(f"Pilot_Win_{side}",
                 (0, pilot_cy + sgn_y * (pilot_d/2 + 0.005), pw_z),
                 (pilot_w - 0.40, 0.02, 1.20), (0.32, 0.38, 0.44, 1.0))
    # Pitched roof (a single sloped slab, simulated by a tilted box —
    # but to avoid rotations, use two stepped slabs hinting at a pitch)
    make_box("Pilot_Roof_Lo",
             (0, pilot_cy, pilot_floor_z + pilot_h + 0.05),
             (pilot_w + 0.40, pilot_d + 0.40, 0.10), COL_BOAT_TRIM)
    make_box("Pilot_Roof_Hi",
             (0, pilot_cy, pilot_floor_z + pilot_h + 0.20),
             (pilot_w - 0.30, pilot_d - 0.30, 0.10), COL_BOAT_TRIM)
    # Finial on top
    make_cyl("Pilot_Finial",
             (0, pilot_cy, pilot_floor_z + pilot_h + 0.40),
             0.04, 0.50, COL_BRASS, segments=4, axis='Z')
    make_sphere_low("Pilot_Finial_Ball",
                    (0, pilot_cy, pilot_floor_z + pilot_h + 0.70),
                    0.08, COL_BRASS, rings=2, segments=6)

    # ════════════════════════════════════════════════════════════════
    # SMOKESTACKS — twin, forward on the boiler deck, 11.5m tall
    # ════════════════════════════════════════════════════════════════
    stack_h = 11.5
    stack_base_z = saloon_deck_z + 0.10
    stack_top_z = stack_base_z + stack_h
    stack_cz = (stack_base_z + stack_top_z) / 2
    # Position: 2.5m apart, forward of the saloon cabin (positive Y, "north")
    stack_y = D_D/2 - 1.5
    for sgn_x in (-1, +1):
        sx = sgn_x * 2.0
        # Tall body
        make_cyl(f"Stack_{sgn_x:+d}_Body",
                 (sx, stack_y, stack_cz),
                 0.30, stack_h, COL_BOAT_STACK, segments=8, axis='Z')
        # Decorative crown at the top (flared)
        make_cyl(f"Stack_{sgn_x:+d}_Crown",
                 (sx, stack_y, stack_top_z + 0.05),
                 0.42, 0.10, COL_BOAT_STACK, segments=10, axis='Z')
        # Crown filigree (two narrow rings under the crown)
        for ri, ring_z in enumerate([stack_top_z - 0.20, stack_top_z - 0.50]):
            make_cyl(f"Stack_{sgn_x:+d}_Ring_{ri}",
                     (sx, stack_y, ring_z), 0.33, 0.04,
                     COL_BOAT_GINGER, segments=12, axis='Z')
        # Cross-tie between the two stacks at top (a single rod connecting them)
        # Only on one side to avoid duplicates
    # Twin-stack cross tie
    make_cyl("Stack_CrossTie",
             (0, stack_y, stack_top_z - 0.80),
             0.025, 4.0, COL_BOAT_STACK, segments=4, axis='X')

    # ════════════════════════════════════════════════════════════════
    # STERN PADDLE WHEEL — partial visible on the SOUTH side
    # ════════════════════════════════════════════════════════════════
    # The boat is moored facing north; the paddle is at the stern
    # (south end), partly submerged. We show ~half the wheel above
    # the porch deck level, on the building's south side.
    wheel_cz = -0.5    # axle is below the deck level
    wheel_r = 2.4
    # Side housings (two big circular "boxes" suggesting a paddle box)
    for sgn_x in (-1, +1):
        wx = sgn_x * 3.5
        # Wheel hub (one cylinder on the axis pointing E-W)
        make_cyl(f"Wheel_{sgn_x:+d}_Hub",
                 (wx, -D_D/2 - 1.5, wheel_cz),
                 0.20, 0.40, COL_BOAT_STACK, segments=8, axis='X')
        # 8 paddle blades radiating around the hub (top half visible only —
        # we still make all 8 since some are partially submerged)
        for b in range(8):
            ang = math.radians(b * 45)
            rx = wheel_r * math.cos(ang)
            rz = wheel_r * math.sin(ang)
            if rz < -2.5:    # the truly-underwater blades — skip
                continue
            make_box(f"Wheel_{sgn_x:+d}_Blade_{b}",
                     (wx, -D_D/2 - 1.5, wheel_cz + rz),
                     (0.20, 0.40, 0.10), COL_BOAT_WHEEL)
            # Spoke from hub to blade
            spoke_z_center = wheel_cz + rz / 2
            spoke_len = abs(rz)
            if spoke_len > 0.20:
                make_box(f"Wheel_{sgn_x:+d}_Spoke_{b}",
                         (wx, -D_D/2 - 1.5, spoke_z_center),
                         (0.06, 0.30, spoke_len),
                         COL_BOAT_WHEEL)
    # Cross-bar connecting the two paddle-box hubs (the actual paddle axle)
    make_cyl("Wheel_Axle",
             (0, -D_D/2 - 1.5, wheel_cz),
             0.10, 7.0, COL_BOAT_STACK, segments=6, axis='X')

    # ════════════════════════════════════════════════════════════════
    # GANGWAY — angled plank from porch (Z=0) down to dock level
    # ════════════════════════════════════════════════════════════════
    # The gangway slopes from the porch (z=0) to the dock (~z=-1.5),
    # angled down toward the west (river) over 4m. We approximate
    # the slope by stacking three slightly-offset plank segments.
    # Gangway anchored to the NEW outer porch edge (porch outer at
    # X=-D_W/2 - WEST_EXT_W - porch_d = -17.4). It slopes down to
    # the river ~4m further west.
    gw_start_x = -D_W/2 - WEST_EXT_W - 2.3   # near porch edge
    gw_end_x   = -D_W/2 - WEST_EXT_W - 6.0   # out into the river
    for s_i in range(4):
        frac = s_i / 4.0
        nfrac = (s_i + 1) / 4.0
        x0 = gw_start_x - (gw_start_x - gw_end_x) * frac
        x1 = gw_start_x - (gw_start_x - gw_end_x) * nfrac
        z0 = -frac * 1.5
        z1 = -nfrac * 1.5
        gx = (x0 + x1) / 2
        gz = (z0 + z1) / 2
        gw_len = abs(x1 - x0) + 0.05
        make_box(f"Gangway_Seg_{s_i}",
                 (gx, -2.0, gz), (gw_len, 1.20, 0.08), COL_BOAT_DECK)
        # Plank seam down the middle
        make_box(f"Gangway_Seam_{s_i}",
                 (gx, -2.0, gz + 0.045),
                 (gw_len - 0.05, 0.015, 0.005), COL_BOAT_SEAM)
    # Brass rope-line on each side of the gangway
    for sgn_y in (-1, +1):
        for s_i in range(4):
            frac = (s_i + 0.5) / 4.0
            x_mid = gw_start_x - (gw_start_x - gw_end_x) * frac
            z_mid = -frac * 1.5 + 0.85
            make_cyl(f"Gangway_Rope_{sgn_y:+d}_{s_i}",
                     (x_mid, -2.0 + sgn_y * 0.55, z_mid),
                     0.014, (gw_start_x - gw_end_x) / 4 + 0.05,
                     COL_BRASS, segments=4, axis='X')
        # Stanchion posts along the gangway side
        for p in range(5):
            frac = p / 4.0
            x_p = gw_start_x - (gw_start_x - gw_end_x) * frac
            z_p = -frac * 1.5
            make_cyl(f"Gangway_Post_{sgn_y:+d}_{p}",
                     (x_p, -2.0 + sgn_y * 0.55, z_p + 0.45),
                     0.025, 0.90, COL_BRASS, segments=4, axis='Z')

    # ── Gingerbread fretwork between the boiler-deck stanchions ──
    # (this is the trademark riverboat detail per build_riverfront)
    fretwork_z = saloon_deck_z + 0.85
    # West side fretwork (visible from the river view) — wraps the
    # NEW outer west edge of the boiler deck at deck_x_W (was -9, now
    # -16) so the gingerbread sits where the player actually sees it.
    for i in range(int(deck_d / spacing)):
        py = -deck_d/2 + (i + 0.5) * deck_d / int(deck_d / spacing)
        make_box(f"BD_Fretwork_W_{i}",
                 (deck_x_W - 0.04, py, fretwork_z),
                 (0.04, spacing - 0.20, 0.20), COL_BOAT_GINGER)


def build_exterior_hints():
    """Steamboat exterior visible through the river-side window
    (-X) + parking-lot exterior visible through the east windows
    (+X). The player looking out of either window should see a
    real-feeling outside.

    Per _VOL5_WIKI canon: 'weathered diner complex moored on the
    river bank — white clapboard exterior, brass rails, a
    wraparound porch over the water.'"""

    # ── WRAPAROUND STEAMBOAT PORCH (west / river side) ──
    # Now anchored against the NEW outer west wall (X=-15), not the
    # OLD shell wall (X=-9). Porch sits AGAINST the formal-dining /
    # bar / corridor exterior, with brass rails on its outer edge.
    porch_d = 2.4               # extends 2.4m further west of the building
    porch_z = 0.0
    porch_y_center = 0.0
    new_west_x = -D_W/2 - WEST_EXT_W      # -15
    porch_outer_x = new_west_x - porch_d  # -17.4
    porch_cx = new_west_x - porch_d / 2.0 # -16.2
    # Main deck running the full N-S length, west of the extension
    make_box("Porch_Deck_W",
             (porch_cx, porch_y_center, porch_z),
             (porch_d, D_D, 0.08),
             (0.40, 0.30, 0.18, 1.0))
    # Deck plank seams (5 longitudinal stripes)
    for i in range(5):
        plank_y = -D_D/2 + (i + 0.5) * (D_D / 5)
        make_box(f"Porch_Plank_Seam_{i}",
                 (porch_cx, plank_y, porch_z + 0.045),
                 (porch_d - 0.1, 0.025, 0.01),
                 (0.20, 0.14, 0.08, 1.0))
    # Wrap-around: short porch segments at N and S ends extending
    # past the building corners
    for side, sy in [("N", +D_D/2 + 0.5), ("S", -D_D/2 - 0.5)]:
        make_box(f"Porch_Deck_{side}",
                 (new_west_x - 0.5, sy, porch_z),
                 (porch_d + 1.0, 1.0, 0.08),
                 (0.40, 0.30, 0.18, 1.0))
    # ── BRASS RAILING along the porch outer edge ──
    rail_x = porch_outer_x + 0.05
    # Top rail
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
    # ── MOORED SKIFF + dock cleat (all relative to the new porch X) ──
    river_top_z = -2.0
    boat_cx, boat_cy = porch_outer_x - 2.0, -1.5
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
    # ── PARKING LOT + STREETSCAPE (east + south of building) ──
    # User flagged sparse exterior detail. The diner's "land side"
    # (east) needs more than a sodium pole + 6 white stripes — needs
    # cars, sidewalks, road, far-side buildings, signage, atmosphere.
    build_diner_streetscape()


def build_diner_streetscape():
    """Full exterior atmosphere east and south of the building:
    parking lot with parked vehicles, sidewalk, River Road, far-side
    storefronts, multiple sodium-light poles, signage, bench,
    mailbox, fire hydrant, trash can, phone booth, etc. Builds the
    night-arrival scene that's visible from the diner's east picture
    window AND from the riverfront scene looking back at the diner.
    """
    COL_ASPHALT     = (0.10, 0.10, 0.11, 1.0)
    COL_ASPHALT_HI  = (0.16, 0.16, 0.18, 1.0)
    COL_STRIPE      = (0.86, 0.84, 0.78, 1.0)
    COL_SIDEWALK    = (0.36, 0.34, 0.30, 1.0)
    COL_CURB        = (0.24, 0.22, 0.20, 1.0)
    COL_POLE_DARK   = (0.18, 0.16, 0.14, 1.0)
    COL_SODIUM_GLOW = (0.96, 0.72, 0.32, 1.0)
    COL_CAR_BODY_A  = (0.58, 0.20, 0.18, 1.0)   # maroon sedan
    COL_CAR_BODY_B  = (0.32, 0.36, 0.42, 1.0)   # slate blue
    COL_CAR_BODY_C  = (0.18, 0.18, 0.18, 1.0)   # black truck
    COL_CAR_BODY_D  = (0.72, 0.68, 0.50, 1.0)   # tan station wagon
    COL_CAR_WINDOW  = (0.10, 0.14, 0.18, 1.0)
    COL_CAR_TIRE    = (0.06, 0.06, 0.06, 1.0)
    COL_BRICK_FAR   = (0.30, 0.22, 0.18, 1.0)
    COL_WINDOW_LIT  = (0.86, 0.74, 0.40, 1.0)   # warm-lit shop window
    COL_WINDOW_DARK = (0.10, 0.12, 0.14, 1.0)
    COL_HYDRANT_R   = (0.72, 0.18, 0.14, 1.0)
    COL_PHONEBOOTH  = (0.30, 0.40, 0.48, 1.0)
    COL_PB_TRIM     = (0.86, 0.78, 0.42, 1.0)

    # ── Parking lot asphalt (a bigger lot east of the diner) ──
    LOT_X_W = D_W/2 + 0.5
    LOT_X_E = D_W/2 + 14.0
    LOT_Y_S = -D_D/2 - 0.5
    LOT_Y_N = D_D/2 + 0.5
    make_box("Lot_Asphalt",
             ((LOT_X_W + LOT_X_E) / 2, (LOT_Y_S + LOT_Y_N) / 2, 0.005),
             (LOT_X_E - LOT_X_W, LOT_Y_N - LOT_Y_S, 0.02),
             COL_ASPHALT)
    # Concrete sidewalk between asphalt and the diner's east wall
    make_box("Lot_Sidewalk",
             ((D_W/2 + LOT_X_W) / 2, 0, 0.012),
             (LOT_X_W - D_W/2, D_D + 0.8, 0.008),
             COL_SIDEWALK)
    # Curb edge between sidewalk and asphalt
    make_box("Lot_Curb",
             (LOT_X_W, 0, 0.05),
             (0.10, D_D + 0.8, 0.06), COL_CURB)
    # Parking stripes in two rows (head-to-head parking)
    n_stalls = 8
    stall_w  = 1.20
    for row_sgn, row_y in [("S", -3.5), ("N", +2.5)]:
        for p in range(n_stalls + 1):
            sx = LOT_X_W + 1.0 + p * (stall_w)
            make_box(f"Lot_Stripe_{row_sgn}_{p}",
                     (sx, row_y, 0.025),
                     (0.10, 2.2, 0.005), COL_STRIPE)
    # Center divider lane stripe (long dash pattern)
    for d in range(6):
        sx = LOT_X_W + 0.8 + d * 1.8
        make_box(f"Lot_Lane_Dash_{d}",
                 (sx, -0.5, 0.025),
                 (1.0, 0.10, 0.005), COL_STRIPE)
    # Painted "DINER" lettering on the asphalt (a couple of
    # block-letter rectangles, no real font — just suggestion)
    for li, lx in enumerate([LOT_X_W + 6.5, LOT_X_W + 7.4,
                              LOT_X_W + 8.3, LOT_X_W + 9.2,
                              LOT_X_W + 10.1]):
        make_box(f"Lot_DinerLetter_{li}",
                 (lx, +0.5, 0.022),
                 (0.50, 0.80, 0.004), COL_STRIPE)

    # ── Parked vehicles (4 — head-in, two on each row) ──
    car_specs = [
        # (X, Y, color, length, width, height, has_truck_bed)
        (LOT_X_W + 1.6, -3.5, COL_CAR_BODY_A, 4.6, 1.8, 1.40, False),
        (LOT_X_W + 4.0, -3.5, COL_CAR_BODY_C, 5.4, 2.0, 1.80, True),
        (LOT_X_W + 1.6, +2.5, COL_CAR_BODY_B, 4.4, 1.7, 1.35, False),
        (LOT_X_W + 4.0, +2.5, COL_CAR_BODY_D, 4.8, 1.8, 1.50, False),
    ]
    for i, (cx, cy, col, L, W, H, is_truck) in enumerate(car_specs):
        # Lower body (chassis + wheel-well area)
        make_box(f"Car_{i}_LowerBody",
                 (cx, cy, 0.40),
                 (W, L, 0.50), col)
        # Upper body / cabin (greenhouse)
        cab_len = L * (0.55 if is_truck else 0.62)
        cab_off = (L - cab_len) / 2 * (-0.2 if is_truck else 0)
        make_box(f"Car_{i}_Cabin",
                 (cx, cy + cab_off, 0.78),
                 (W - 0.10, cab_len, H - 0.55), col)
        # Greenhouse glass (4 windows as a single dark band)
        make_box(f"Car_{i}_Windshield",
                 (cx, cy + cab_off + cab_len/2 - 0.05, 0.90),
                 (W - 0.20, 0.04, H - 0.75), COL_CAR_WINDOW)
        make_box(f"Car_{i}_RearWindow",
                 (cx, cy + cab_off - cab_len/2 + 0.05, 0.90),
                 (W - 0.20, 0.04, H - 0.75), COL_CAR_WINDOW)
        # Side windows
        for sgn in (-1, +1):
            make_box(f"Car_{i}_SideWindow_{sgn:+d}",
                     (cx + sgn * (W/2 - 0.04), cy + cab_off, 0.90),
                     (0.04, cab_len - 0.15, H - 0.78),
                     COL_CAR_WINDOW)
        # Truck bed for the pickup
        if is_truck:
            bed_len = L - cab_len - 0.10
            bed_off = -L/2 + bed_len/2 + 0.05
            make_box(f"Car_{i}_TruckBed",
                     (cx, cy + bed_off, 0.55),
                     (W, bed_len, 0.40), col)
            make_box(f"Car_{i}_TruckBed_Inset",
                     (cx, cy + bed_off, 0.65),
                     (W - 0.14, bed_len - 0.10, 0.20),
                     (0.10, 0.10, 0.10, 1.0))
        # 4 wheels
        for wx in (-1, +1):
            for wy in (-1, +1):
                wxp = cx + wx * (W/2 + 0.02)
                wyp = cy + wy * (L/2 - 0.55)
                make_cyl(f"Car_{i}_Wheel_{wx:+d}_{wy:+d}",
                         (wxp, wyp, 0.30),
                         0.30, 0.18, COL_CAR_TIRE,
                         segments=10, axis='X')
                make_cyl(f"Car_{i}_Hub_{wx:+d}_{wy:+d}",
                         (wxp, wyp, 0.30),
                         0.14, 0.20, (0.42, 0.42, 0.44, 1.0),
                         segments=8, axis='X')
        # Headlights (off — dark amber lenses)
        for sgn in (-1, +1):
            make_box(f"Car_{i}_Headlight_{sgn:+d}",
                     (cx + sgn * (W/2 - 0.18), cy + L/2 - 0.04, 0.60),
                     (0.20, 0.04, 0.16),
                     (0.86, 0.78, 0.42, 1.0))
        # Tail lights (red)
        for sgn in (-1, +1):
            make_box(f"Car_{i}_Taillight_{sgn:+d}",
                     (cx + sgn * (W/2 - 0.16), cy - L/2 + 0.04, 0.60),
                     (0.16, 0.04, 0.14),
                     (0.86, 0.20, 0.16, 1.0))
        # License plate
        make_box(f"Car_{i}_Plate",
                 (cx, cy - L/2 + 0.03, 0.40),
                 (0.40, 0.02, 0.14),
                 (0.92, 0.88, 0.72, 1.0))

    # ── Three sodium-light poles spread across the lot ──
    for label, (px, py) in [
        ("NE",  (LOT_X_E - 1.0, +3.0)),
        ("SE",  (LOT_X_E - 1.0, -3.5)),
        ("Mid", (LOT_X_W + 7.0, -0.5)),
    ]:
        # Pole base (cast iron square)
        make_box(f"Pole_{label}_Base",
                 (px, py, 0.20),
                 (0.30, 0.30, 0.40), COL_POLE_DARK)
        # Pole shaft
        make_cyl(f"Pole_{label}_Shaft",
                 (px, py, 3.0),
                 0.06, 5.5, COL_POLE_DARK, segments=6, axis='Z')
        # Arm extending toward the diner
        arm_dir = -1 if px > 0 else +1
        make_box(f"Pole_{label}_Arm",
                 (px + arm_dir * 0.8, py, 5.7),
                 (1.8, 0.08, 0.08), COL_POLE_DARK)
        # Cobra-head sodium fixture
        make_box(f"Pole_{label}_Head",
                 (px + arm_dir * 1.6, py, 5.60),
                 (0.55, 0.36, 0.28), COL_POLE_DARK)
        # Sodium glow lens (warm orange)
        make_box(f"Pole_{label}_Lens",
                 (px + arm_dir * 1.6, py, 5.48),
                 (0.48, 0.30, 0.06), COL_SODIUM_GLOW)

    # ── River Road (E-W running south of the building) ──
    ROAD_Y_N = -D_D/2 - 1.0
    ROAD_Y_S = -D_D/2 - 5.0
    ROAD_X_W = -D_W/2 - 12.0
    ROAD_X_E =  D_W/2 + 16.0
    make_box("RiverRoad_Asphalt",
             ((ROAD_X_W + ROAD_X_E) / 2,
              (ROAD_Y_N + ROAD_Y_S) / 2, 0.01),
             (ROAD_X_E - ROAD_X_W, ROAD_Y_N - ROAD_Y_S, 0.03),
             COL_ASPHALT)
    # Center yellow double-line
    for sgn in (-1, +1):
        make_box(f"RiverRoad_CenterLine_{sgn:+d}",
                 ((ROAD_X_W + ROAD_X_E) / 2,
                  (ROAD_Y_N + ROAD_Y_S) / 2 + sgn * 0.10, 0.025),
                 (ROAD_X_E - ROAD_X_W - 0.5, 0.08, 0.004),
                 (0.86, 0.74, 0.20, 1.0))
    # Dashed lane edges (white)
    for d in range(int((ROAD_X_E - ROAD_X_W) / 2.5)):
        sx = ROAD_X_W + 1.0 + d * 2.5
        make_box(f"RiverRoad_Dash_N_{d}",
                 (sx, ROAD_Y_N - 0.3, 0.025),
                 (1.2, 0.10, 0.004), COL_STRIPE)
        make_box(f"RiverRoad_Dash_S_{d}",
                 (sx, ROAD_Y_S + 0.3, 0.025),
                 (1.2, 0.10, 0.004), COL_STRIPE)
    # Sidewalk between road north edge and the building south wall /
    # porch
    make_box("RiverRoad_NorthSidewalk",
             ((ROAD_X_W + ROAD_X_E) / 2,
              (ROAD_Y_N + (-D_D/2 - 0.5)) / 2, 0.015),
             (ROAD_X_E - ROAD_X_W, 0.5, 0.012),
             COL_SIDEWALK)
    # Sidewalk on the south side of the road too
    SW_S_Y = ROAD_Y_S - 0.5
    make_box("RiverRoad_SouthSidewalk",
             ((ROAD_X_W + ROAD_X_E) / 2, SW_S_Y, 0.015),
             (ROAD_X_E - ROAD_X_W, 1.0, 0.012),
             COL_SIDEWALK)

    # ── Far-side storefronts across the River Road ──
    far_y = SW_S_Y - 2.5
    storefronts = [
        # (label, X_center, X_width, height, base_color, n_lit_windows)
        ("Pawn",    -8.0,  5.0, 4.0, COL_BRICK_FAR, 2),
        ("Tackle",  -2.0,  4.0, 3.6, (0.36, 0.30, 0.22, 1.0), 1),
        ("Cafe",    +3.0,  4.5, 3.8, (0.40, 0.28, 0.22, 1.0), 3),
        ("Auto",    +9.0,  5.5, 4.2, (0.26, 0.24, 0.22, 1.0), 1),
        ("Liquor", +15.0,  4.0, 3.8, COL_BRICK_FAR, 2),
    ]
    for label, fx, fw, fh, col, n_lit in storefronts:
        # Main facade
        make_box(f"Far_{label}_Wall",
                 (fx, far_y, fh / 2),
                 (fw, 1.5, fh), col)
        # Cornice band at the top
        make_box(f"Far_{label}_Cornice",
                 (fx, far_y - 0.05, fh - 0.10),
                 (fw + 0.20, 0.08, 0.18),
                 (0.20, 0.16, 0.12, 1.0))
        # Roof line
        make_box(f"Far_{label}_Roof",
                 (fx, far_y, fh + 0.10),
                 (fw + 0.10, 1.4, 0.10),
                 (0.16, 0.14, 0.12, 1.0))
        # Front windows (lit or dark)
        n_win = 4
        for w in range(n_win):
            wx = fx - fw/2 + 0.5 + w * ((fw - 1.0) / (n_win - 1))
            lit = (w < n_lit)
            wc = COL_WINDOW_LIT if lit else COL_WINDOW_DARK
            make_box(f"Far_{label}_Window_{w}",
                     (wx, far_y + 0.78, 2.20),
                     (0.65, 0.04, 0.85), wc)
            # Window frame
            make_box(f"Far_{label}_WindowFrame_{w}",
                     (wx, far_y + 0.79, 2.20),
                     (0.72, 0.02, 0.92),
                     (0.10, 0.08, 0.06, 1.0))
        # Hanging sign over the door (a small box with brass trim)
        make_box(f"Far_{label}_Sign",
                 (fx, far_y + 0.85, 3.10),
                 (fw * 0.5, 0.04, 0.40),
                 (0.20, 0.16, 0.12, 1.0))
        make_box(f"Far_{label}_Sign_Text",
                 (fx, far_y + 0.86, 3.10),
                 (fw * 0.4, 0.02, 0.20),
                 (0.86, 0.78, 0.42, 1.0))
        # Front door (dark)
        door_x = fx
        make_box(f"Far_{label}_Door",
                 (door_x, far_y + 0.78, 1.10),
                 (0.95, 0.04, 2.20),
                 (0.18, 0.14, 0.10, 1.0))
        # Door handle
        make_cyl(f"Far_{label}_Door_Handle",
                 (door_x + 0.35, far_y + 0.79, 1.05),
                 0.02, 0.10, COL_BRASS, segments=4, axis='Y')

    # ── Street lights along River Road (4) ──
    for label, sx in [("R1", -10), ("R2", -2), ("R3", +6), ("R4", +14)]:
        sy = (ROAD_Y_N - 0.5)    # on the north sidewalk
        make_cyl(f"StreetLight_{label}_Pole",
                 (sx, sy, 2.8),
                 0.05, 5.2, COL_POLE_DARK, segments=6, axis='Z')
        # Acorn-style fixture (sphere)
        make_sphere_low(f"StreetLight_{label}_Globe",
                        (sx, sy, 5.5),
                        0.20, (0.96, 0.88, 0.62, 1.0),
                        rings=3, segments=10)
        make_cyl(f"StreetLight_{label}_Cap",
                 (sx, sy, 5.72),
                 0.08, 0.10, COL_POLE_DARK, segments=6, axis='Z')

    # ── Streetscape props on the north sidewalk ──
    # Fire hydrant near the entry
    make_cyl("Hydrant_Body",
             (D_W/2 + 1.5, ROAD_Y_N - 0.3, 0.30),
             0.14, 0.60, COL_HYDRANT_R, segments=8, axis='Z')
    make_cyl("Hydrant_Cap",
             (D_W/2 + 1.5, ROAD_Y_N - 0.3, 0.65),
             0.12, 0.08, COL_HYDRANT_R, segments=8, axis='Z')
    for hsgn in (-1, +1):
        make_cyl(f"Hydrant_Side_{hsgn:+d}",
                 (D_W/2 + 1.5 + hsgn * 0.18, ROAD_Y_N - 0.3, 0.45),
                 0.06, 0.06, COL_HYDRANT_R, segments=6, axis='X')

    # Mailbox (USPS blue) further east
    make_box("Mailbox_Body",
             (D_W/2 + 5.5, ROAD_Y_N - 0.3, 0.65),
             (0.50, 0.40, 0.50), (0.20, 0.32, 0.56, 1.0))
    make_box("Mailbox_Top",
             (D_W/2 + 5.5, ROAD_Y_N - 0.3, 0.92),
             (0.50, 0.40, 0.04), (0.16, 0.26, 0.46, 1.0))
    make_box("Mailbox_Pull",
             (D_W/2 + 5.5, ROAD_Y_N - 0.10, 0.78),
             (0.30, 0.04, 0.10),
             (0.16, 0.26, 0.46, 1.0))
    make_cyl("Mailbox_Leg",
             (D_W/2 + 5.5, ROAD_Y_N - 0.3, 0.20),
             0.04, 0.40, (0.18, 0.18, 0.18, 1.0), segments=4, axis='Z')

    # Trash can (chrome)
    make_cyl("TrashCan_Body",
             (D_W/2 + 3.0, ROAD_Y_N - 0.3, 0.45),
             0.22, 0.90, (0.34, 0.34, 0.36, 1.0), segments=10, axis='Z')
    make_cyl("TrashCan_Lid",
             (D_W/2 + 3.0, ROAD_Y_N - 0.3, 0.92),
             0.24, 0.04, (0.20, 0.20, 0.22, 1.0), segments=10, axis='Z')

    # Bench (a 2-person sidewalk bench)
    bench_x = D_W/2 + 7.5
    bench_y = ROAD_Y_N - 0.4
    make_box("Bench_Seat",
             (bench_x, bench_y, 0.42),
             (1.40, 0.40, 0.06), (0.30, 0.20, 0.12, 1.0))
    for sgn in (-1, +1):
        make_cyl(f"Bench_Leg_{sgn:+d}",
                 (bench_x + sgn * 0.55, bench_y, 0.21),
                 0.04, 0.42, COL_POLE_DARK, segments=4, axis='Z')
    # Backrest
    for r in range(3):
        rz = 0.65 + r * 0.10
        make_box(f"Bench_BackRail_{r}",
                 (bench_x, bench_y + 0.16, rz),
                 (1.40, 0.04, 0.05), (0.30, 0.20, 0.12, 1.0))

    # Phone booth (red British-style, but classic American glass-and-aluminum)
    pb_x = D_W/2 + 10.0
    pb_y = ROAD_Y_N - 0.6
    make_box("PhoneBooth_Body",
             (pb_x, pb_y, 1.05),
             (0.85, 0.85, 2.10), COL_PHONEBOOTH)
    # Glass panels (3 sides — north open)
    for sgn_x in (-1, +1):
        make_box(f"PhoneBooth_GlassEW_{sgn_x:+d}",
                 (pb_x + sgn_x * 0.41, pb_y, 1.20),
                 (0.02, 0.78, 1.40),
                 (0.50, 0.62, 0.70, 1.0))
    make_box("PhoneBooth_GlassS",
             (pb_x, pb_y - 0.41, 1.20),
             (0.78, 0.02, 1.40),
             (0.50, 0.62, 0.70, 1.0))
    # Top cap
    make_box("PhoneBooth_Top",
             (pb_x, pb_y, 2.18),
             (0.92, 0.92, 0.16), COL_PHONEBOOTH)
    # "TELEPHONE" sign band
    make_box("PhoneBooth_Sign",
             (pb_x, pb_y, 1.92),
             (0.84, 0.84, 0.18), COL_PB_TRIM)
    # Receiver inside (a small dark box hanging)
    make_box("PhoneBooth_Phone",
             (pb_x, pb_y + 0.30, 1.30),
             (0.20, 0.08, 0.30), (0.18, 0.16, 0.14, 1.0))

    # Stop-sign at the far corner of the lot
    stop_x = LOT_X_E - 0.5
    stop_y = ROAD_Y_N - 0.3
    make_cyl("StopSign_Pole",
             (stop_x, stop_y, 1.50),
             0.04, 3.0, COL_POLE_DARK, segments=6, axis='Z')
    # Octagonal stop sign — approximated by a flattened cylinder
    make_cyl("StopSign_Face",
             (stop_x, stop_y - 0.06, 2.50),
             0.35, 0.04, COL_HYDRANT_R, segments=8, axis='Y')
    # White "STOP" letters (small thin slabs)
    make_box("StopSign_LetterBg",
             (stop_x, stop_y - 0.085, 2.50),
             (0.40, 0.01, 0.10),
             (0.94, 0.92, 0.86, 1.0))

    # Painted "PARKING" arrow on the lot floor
    make_box("Lot_Arrow_Shaft",
             (LOT_X_W + 2.5, -0.5, 0.022),
             (1.2, 0.16, 0.005), COL_STRIPE)
    make_box("Lot_Arrow_HeadL",
             (LOT_X_W + 3.0, -0.55, 0.022),
             (0.30, 0.08, 0.005), COL_STRIPE)
    make_box("Lot_Arrow_HeadR",
             (LOT_X_W + 3.0, -0.45, 0.022),
             (0.30, 0.08, 0.005), COL_STRIPE)

    # Power lines + utility poles along the road (3 poles)
    for upi, upx in enumerate([-10, +4, +16]):
        upy = SW_S_Y - 0.3
        # Pole
        make_cyl(f"UtilPole_{upi}_Body",
                 (upx, upy, 5.0),
                 0.10, 10.0, (0.36, 0.28, 0.18, 1.0),
                 segments=6, axis='Z')
        # Cross-arm
        make_box(f"UtilPole_{upi}_CrossArm",
                 (upx, upy, 9.0),
                 (2.40, 0.10, 0.10),
                 (0.36, 0.28, 0.18, 1.0))
        # 3 insulators on the cross-arm
        for ix in (-1, 0, +1):
            make_cyl(f"UtilPole_{upi}_Insulator_{ix:+d}",
                     (upx + ix * 1.0, upy, 9.18),
                     0.08, 0.16, (0.86, 0.86, 0.84, 1.0),
                     segments=6, axis='Z')

    # ── Diner's own "D'AMBROSIO'S" neon sign on the south facade,
    #    above the porch (matches the screenshot the user shared from
    #    the riverfront view) ──
    sign_y = -D_D/2 - 0.30
    make_box("DinerSign_Backing",
             (0, sign_y, D_H + 1.0),
             (8.0, 0.10, 1.20), (0.18, 0.14, 0.10, 1.0))
    # Neon "D'AMBROSIO'S" text — a wide red glow slab + dark backer
    make_box("DinerSign_Neon",
             (0, sign_y - 0.06, D_H + 1.0),
             (7.0, 0.06, 0.90),
             (0.96, 0.18, 0.16, 1.0))
    # Underline accent (white tube)
    make_box("DinerSign_Underline",
             (0, sign_y - 0.05, D_H + 0.46),
             (6.8, 0.04, 0.06),
             (0.92, 0.88, 0.74, 1.0))


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
    # close_booth_6 — looking west at booth 6 from the aisle.
    # Booth_6 is at the NORTH end of the alcove row (by=+3.75 per
    # build_alcove_booths' south→north numbering); the marker Y
    # was stale at 2.5 before — now matches the actual booth.
    add_camera("cam_close_booth_6", (-D_W/2 + 2.5, 3.75, 1.40), (math.radians(85), 0, math.radians(-90)))
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
    build_west_extension()           # NEW portside extension (bar + formal dining)
    build_floor_checkerboard()
    build_counter()
    build_counter_accessories()
    build_alcove_booths()
    build_freestanding_tables()
    build_table_dressings()
    build_riverboat_galley()
    build_interior_partitions()
    # NOTE: formal dining + bar both moved to the WEST extension
    # (build_west_extension). The old NE-annex formal, the north-
    # annex bar, AND the old annex_hallway are DISABLED. The entry
    # hallway is now the open zone inside the east annex between
    # vestibule (Y=-1) and bathroom partition (Y=-3.95), with the
    # L-bend opening at Y=-3.95..-2.5 letting the hallway turn west
    # toward the main floor / PD / formal dining beyond.
    # build_formal_dining_room()
    # build_annex_hallway()
    build_private_dining_room()          # NEW location: L-elbow
    build_southeast_bathroom()           # repurposed old PD footprint
    build_storage_closet_and_bbs()
    build_back_hallway()
    # build_north_annex_bar()
    build_hull_extensions()
    build_ceiling_fans()
    build_wall_decor()
    build_entry_props()
    # Jukebox at the host SPACE_MAP 'jukebox' vantage (-10.5, +5.0)
    # in the west-extension bar room. Per setup_evening_service.json
    # flavor: "the jukebox skipping". Facing south so the marquee
    # reads from the bar's south doorway approach.
    build_jukebox(-10.5, 5.0)
    # Scene-description specifics from setup_the_leap.json — the
    # Booth_6 fluorescent, the brass plaque, John Frank's rag, the
    # empty mug and the ring it left, the brass door bell. Always
    # present; reads as canonical detail across all 3 scenarios.
    build_the_leap_dressing()
    build_gauntlet_decor()
    build_enhanced_river_view()
    build_exterior_hints()
    build_riverboat_superstructure()
    # Camera markers intentionally NOT added — same issue as the
    # Cathedral build had with FrasierEye hijacking the active
    # camera. Will re-introduce as named cinematic markers once
    # the framing system is wired up properly via Godot Node3D
    # markers instead of camera nodes.
    # add_camera_markers()  # DISABLED
    export_glb()


if __name__ == "__main__":
    main()
