"""
build_roberts_house.py
══════════════════════════════════════════════════════════════════
VOL 5 · CHAPTER 6 · The Lovers · the Roberts family house.

A small one-story house on a quiet street in Graustark.
Three of the four Lovers scenarios run here:

  he_waved              · 8:45 AM · the drip, the curb, the Polaroid
  the_faucet_wins       · 8:18 AM · coffee + damp earth, the bird
  today_the_drip_can_win· 2:14 PM · the long hours, Mackenzie's
                                    sister's casserole, the
                                    Polaroid already on the hall
                                    table

(The fourth Lovers scenario — sanctuary_on_cursed_ground — runs
at the separate roadside_chapel locale.)

Layout (per the canon scene_descriptions):

  FRONT YARD + CURB     small lawn, gate, curb at street (where
                        Mrs. Theriot's station wagon parks)
  FRONT PORCH           two steps, screen door, an unused boot tray
  FRONT HALLWAY         narrow strip just inside the front door,
                        wood floor, a small table where the
                        Polaroid lands and an upright phone niche
                        on the wall
  LIVING ROOM           couch, coffee table, side chair, picture
                        window onto the front yard
  KITCHEN               sink under the south window (looking onto
                        the back fence + the bird), the drip
                        faucet, coffee pot, kitchen table with
                        two chairs, a half-shelf of mugs
  BACK YARD             a short fence beyond the kitchen window,
                        the fence wire where the bird deliberates
  BACK PORCH            single step, screen door
  BEDROOM (NW)          unmade bed, dresser (peek-only)

Thresholds:
  FRONT DOOR   south side, screen + storm + sticky latch
  BACK DOOR    north side, screen only
  PORCH        accessible

COORDINATE FRAME (Blender → Godot):
    +X east   → +X
    +Y north  → -Z
    +Z up     → +Y
1 unit = 1 m.

Footprint (interior): +X ∈ [-5.0, +5.0], +Y ∈ [0, +6.0]
Front porch: Y ∈ [-1.6, 0]
Front yard + curb: Y ∈ [-7.0, -1.6]
Back porch: Y ∈ [+6.0, +6.8]
Back yard fence: Y ∈ [+6.8, +9.0]

Run:
    blender --background --python build_roberts_house.py
    (or ./run_cathedral.sh build_roberts_house.py)

Output:
    godot/assets/3d/locales/roberts_house.glb
"""

import bpy
import math
import os
import sys

_SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
if _SCRIPT_DIR not in sys.path:
    sys.path.insert(0, _SCRIPT_DIR)

OUTPUT_DIR  = "../../../assets/3d/locales"
OUTPUT_NAME = "roberts_house.glb"


# ── Palette ──────────────────────────────────────────────────────
# A real lived-in 90s house. Worn linoleum, soft cream walls, the
# wood floor that was nice in 1978 and still is. The kitchen is
# the warmest room because the kitchen is the room they use.

COL_FLOOR_WOOD   = (0.46, 0.32, 0.20, 1.0)   # living room + hallway
COL_FLOOR_LINO   = (0.78, 0.72, 0.60, 1.0)   # kitchen linoleum
COL_WALL_CREAM   = (0.92, 0.86, 0.72, 1.0)
COL_WALL_KITCHEN = (0.86, 0.84, 0.74, 1.0)   # a touch cooler than living room
COL_WALL_OUTER   = (0.78, 0.66, 0.48, 1.0)   # exterior tan siding
COL_TRIM_WHITE   = (0.95, 0.92, 0.88, 1.0)
COL_CEILING      = (0.88, 0.84, 0.78, 1.0)

COL_DOOR         = (0.40, 0.28, 0.18, 1.0)
COL_DOORFRAME    = (0.30, 0.20, 0.12, 1.0)
COL_WINDOW_GLASS = (0.58, 0.74, 0.82, 0.85)
COL_WINDOW_FRAME = (0.30, 0.20, 0.12, 1.0)
COL_SCREEN_MESH  = (0.34, 0.32, 0.28, 0.75)

COL_FABRIC_COUCH = (0.62, 0.50, 0.38, 1.0)
COL_FABRIC_PILLOW = (0.74, 0.32, 0.28, 1.0)
COL_CHAIR_VINYL  = (0.74, 0.64, 0.46, 1.0)
COL_RUG          = (0.46, 0.36, 0.30, 1.0)

COL_METAL_BRASS  = (0.78, 0.62, 0.30, 1.0)
COL_METAL_STEEL  = (0.62, 0.66, 0.70, 1.0)
COL_METAL_BLACK  = (0.16, 0.14, 0.14, 1.0)
COL_METAL_FAUCET = (0.74, 0.74, 0.74, 1.0)

COL_PAPER         = (0.92, 0.88, 0.78, 1.0)
COL_PAPER_POLAROID = (0.94, 0.92, 0.88, 1.0)
COL_POLAROID_FRAME = (0.86, 0.84, 0.78, 1.0)
COL_PHONE_BAKELITE = (0.30, 0.26, 0.20, 1.0)

COL_COFFEE_POT    = (0.18, 0.16, 0.18, 1.0)   # black plastic carafe
COL_COFFEE_LIQUID = (0.30, 0.16, 0.08, 1.0)
COL_GREEN_HERB    = (0.30, 0.42, 0.22, 1.0)
COL_BROWN_EARTH   = (0.34, 0.24, 0.16, 1.0)
COL_FENCE_WOOD    = (0.42, 0.32, 0.22, 1.0)
COL_BIRD          = (0.40, 0.34, 0.26, 1.0)   # sparrow-grey-brown
COL_LAWN          = (0.42, 0.50, 0.30, 1.0)
COL_ASPHALT       = (0.20, 0.20, 0.20, 1.0)
COL_CONCRETE      = (0.72, 0.70, 0.66, 1.0)
COL_CASSEROLE_DISH = (0.86, 0.50, 0.30, 1.0)   # corningware orange


# ── Geometry helpers (mirror the bungalow style) ─────────────────

def clear_scene():
    for o in list(bpy.data.objects):
        bpy.data.objects.remove(o, do_unlink=True)
    for m in list(bpy.data.meshes):
        bpy.data.meshes.remove(m)
    for mat in list(bpy.data.materials):
        bpy.data.materials.remove(mat)


def _vc_material(name, rgba):
    mat = bpy.data.materials.new(name)
    mat.use_nodes = False
    mat.diffuse_color = rgba
    return mat


def make_box(name, center, size, rgba, open_faces=None):
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=center)
    o = bpy.context.active_object
    o.name = name
    o.scale = (size[0]/2.0, size[1]/2.0, size[2]/2.0)
    bpy.ops.object.transform_apply(scale=True)
    o.data.materials.append(_vc_material(name + "_mat", rgba))
    return o


def make_cyl(name, center, radius, height, rgba, segments=10, axis='Z'):
    bpy.ops.mesh.primitive_cylinder_add(radius=radius, depth=height,
                                         vertices=segments, location=center)
    o = bpy.context.active_object
    o.name = name
    if axis == 'X':
        o.rotation_euler = (0, math.radians(90), 0)
    elif axis == 'Y':
        o.rotation_euler = (math.radians(90), 0, 0)
    bpy.ops.object.transform_apply(rotation=True)
    o.data.materials.append(_vc_material(name + "_mat", rgba))
    return o


def make_sphere_low(name, center, radius, rgba, rings=2, segments=8):
    bpy.ops.mesh.primitive_uv_sphere_add(radius=radius, location=center,
                                          segments=segments,
                                          ring_count=rings)
    o = bpy.context.active_object
    o.name = name
    o.data.materials.append(_vc_material(name + "_mat", rgba))
    return o


# ── Dimensions ───────────────────────────────────────────────────

# Interior footprint
H_X_W = -5.0    # west exterior wall
H_X_E = +5.0    # east exterior wall
H_Y_S = +0.0    # south exterior wall (front)
H_Y_N = +6.0    # north exterior wall (back)
WALL_T = 0.10   # wall thickness
CEIL_Z = 2.55

# Interior partitions
# East/west split: kitchen is on the east, living room + hallway
# on the west. Bedroom is in the NW corner.
PART_WEST_EAST_X = +1.0   # divider between living and kitchen
PART_BEDROOM_Y   = +4.0   # divider between living and bedroom


# ── Shell ────────────────────────────────────────────────────────

def build_shell():
    # Floor — split into wood (living + hall) and linoleum (kitchen)
    # Wood floor (west of partition)
    make_box("Floor_Wood",
             ((H_X_W + PART_WEST_EAST_X) / 2.0, (H_Y_S + H_Y_N) / 2.0, -0.02),
             (PART_WEST_EAST_X - H_X_W, H_Y_N - H_Y_S, 0.04),
             COL_FLOOR_WOOD)
    # Linoleum (kitchen, east of partition)
    make_box("Floor_Linoleum",
             ((PART_WEST_EAST_X + H_X_E) / 2.0, (H_Y_S + H_Y_N) / 2.0, -0.02),
             (H_X_E - PART_WEST_EAST_X, H_Y_N - H_Y_S, 0.04),
             COL_FLOOR_LINO)

    # Ceiling
    make_box("Ceiling",
             ((H_X_W + H_X_E) / 2.0, (H_Y_S + H_Y_N) / 2.0, CEIL_Z + 0.05),
             (H_X_E - H_X_W, H_Y_N - H_Y_S, 0.10),
             COL_CEILING)

    # Exterior walls (interior side colored cream; exterior in the
    # outer ring colored tan). Build as a single thick box per side
    # so they read closed-shell.
    # South (front) wall — has the front door + the picture window
    make_box("Wall_S",
             ((H_X_W + H_X_E) / 2.0, H_Y_S - WALL_T / 2.0, CEIL_Z / 2.0),
             (H_X_E - H_X_W, WALL_T, CEIL_Z),
             COL_WALL_CREAM)
    # North (back) wall
    make_box("Wall_N",
             ((H_X_W + H_X_E) / 2.0, H_Y_N + WALL_T / 2.0, CEIL_Z / 2.0),
             (H_X_E - H_X_W, WALL_T, CEIL_Z),
             COL_WALL_CREAM)
    # West (side) wall
    make_box("Wall_W",
             (H_X_W - WALL_T / 2.0, (H_Y_S + H_Y_N) / 2.0, CEIL_Z / 2.0),
             (WALL_T, H_Y_N - H_Y_S, CEIL_Z),
             COL_WALL_CREAM)
    # East (side) wall
    make_box("Wall_E",
             (H_X_E + WALL_T / 2.0, (H_Y_S + H_Y_N) / 2.0, CEIL_Z / 2.0),
             (WALL_T, H_Y_N - H_Y_S, CEIL_Z),
             COL_WALL_CREAM)

    # Exterior siding strip outside each wall (for the curb-side view)
    for name, cx, cy, sx, sy in [
        ("Siding_S", (H_X_W + H_X_E) / 2.0, H_Y_S - 0.30, H_X_E - H_X_W, 0.20),
        ("Siding_N", (H_X_W + H_X_E) / 2.0, H_Y_N + 0.30, H_X_E - H_X_W, 0.20),
        ("Siding_W", H_X_W - 0.30, (H_Y_S + H_Y_N) / 2.0, 0.20, H_Y_N - H_Y_S),
        ("Siding_E", H_X_E + 0.30, (H_Y_S + H_Y_N) / 2.0, 0.20, H_Y_N - H_Y_S),
    ]:
        make_box(name,
                 (cx, cy, CEIL_Z / 2.0 + 0.10),
                 (sx, sy, CEIL_Z + 0.20),
                 COL_WALL_OUTER)


def build_interior_partitions():
    # Living/Kitchen divider — wall runs Y from H_Y_S to PART_BEDROOM_Y
    make_box("Part_LivKit",
             (PART_WEST_EAST_X, (H_Y_S + PART_BEDROOM_Y) / 2.0, CEIL_Z / 2.0),
             (WALL_T, PART_BEDROOM_Y - H_Y_S, CEIL_Z),
             COL_WALL_CREAM)
    # Bedroom partition — runs X from H_X_W to PART_WEST_EAST_X at Y=PART_BEDROOM_Y
    make_box("Part_BedLiv",
             ((H_X_W + PART_WEST_EAST_X) / 2.0, PART_BEDROOM_Y, CEIL_Z / 2.0),
             (PART_WEST_EAST_X - H_X_W, WALL_T, CEIL_Z),
             COL_WALL_CREAM)
    # Bedroom doorway gap — overwrite a section of the bedroom wall
    # with a doorway-sized hole. Easiest path: build the wall as two
    # halves with a gap. (We already built it solid; instead carve
    # an open door fixture in front of the gap region.)
    # We'll just add a door fixture overlay below.


# ── Front porch + front door + picture window ────────────────────

def build_front_facade():
    # Picture window in the south wall, west of the door
    pw_x = -2.5
    pw_y = H_Y_S
    pw_w, pw_h = 1.80, 1.20
    pw_cz = 1.40
    make_box("FrontPicWindow_Glass",
             (pw_x, pw_y, pw_cz),
             (pw_w, 0.04, pw_h),
             COL_WINDOW_GLASS)
    # Mullions (one vertical, one horizontal)
    make_box("FrontPicWindow_MullV",
             (pw_x, pw_y, pw_cz),
             (0.04, 0.06, pw_h),
             COL_WINDOW_FRAME)
    make_box("FrontPicWindow_MullH",
             (pw_x, pw_y, pw_cz),
             (pw_w, 0.06, 0.04),
             COL_WINDOW_FRAME)
    # Sill
    make_box("FrontPicWindow_Sill",
             (pw_x, pw_y - 0.05, pw_cz - pw_h / 2.0 - 0.04),
             (pw_w + 0.10, 0.12, 0.04),
             COL_TRIM_WHITE)

    # Front door at the south wall — east of the picture window
    fd_x = +1.5
    fd_y = H_Y_S
    fd_w, fd_h = 0.86, 2.00
    # Door body (slightly inset)
    make_box("FrontDoor_Body",
             (fd_x, fd_y - 0.02, fd_h / 2.0),
             (fd_w, 0.04, fd_h),
             COL_DOOR)
    # Storm door (forward of the body, lighter wood)
    make_box("FrontDoor_StormFrame",
             (fd_x, fd_y - 0.10, fd_h / 2.0),
             (fd_w + 0.04, 0.02, fd_h),
             (0.62, 0.42, 0.26, 1.0))
    # Storm door glass
    make_box("FrontDoor_StormGlass",
             (fd_x, fd_y - 0.105, fd_h / 2.0 + 0.20),
             (fd_w - 0.10, 0.005, fd_h - 0.50),
             COL_WINDOW_GLASS)
    # Brass knob (the "sticky latch")
    make_sphere_low("FrontDoor_Knob",
                    (fd_x + fd_w / 2.0 - 0.10, fd_y - 0.04, 1.00),
                    0.030, COL_METAL_BRASS)
    # Strike plate
    make_box("FrontDoor_Strike",
             (fd_x + fd_w / 2.0 - 0.10, fd_y - 0.022, 1.00),
             (0.10, 0.003, 0.16),
             COL_METAL_BRASS)
    # WELCOME mat
    make_box("FrontDoor_Mat",
             (fd_x, fd_y - 0.50, 0.015),
             (fd_w + 0.20, 0.50, 0.025),
             (0.32, 0.26, 0.20, 1.0))
    # Two porch steps + porch slab
    make_box("Porch_Slab",
             ((H_X_W + H_X_E) / 2.0, H_Y_S - 0.80, 0.05),
             (H_X_E - H_X_W, 1.40, 0.10),
             COL_CONCRETE)
    for s in range(2):
        make_box("Porch_Step_%d" % s,
                 (0.0, H_Y_S - 1.50 - s * 0.25, 0.025 - s * 0.10),
                 (2.40, 0.30, 0.10),
                 COL_CONCRETE)
    # Boot tray (canvas the porch as lived-in)
    make_box("Porch_BootTray",
             (fd_x + 0.50, fd_y - 0.50, 0.05),
             (0.40, 0.30, 0.06),
             COL_METAL_STEEL)


# ── Front yard + curb ────────────────────────────────────────────

def build_front_yard_and_curb():
    # Lawn (the front yard)
    make_box("FrontLawn",
             ((H_X_W + H_X_E) / 2.0, -3.5, -0.045),
             (H_X_E - H_X_W + 1.0, 4.0, 0.02),
             COL_LAWN)
    # Concrete walkway from porch to sidewalk
    make_box("Walkway",
             (1.5, -3.5, -0.040),
             (1.20, 4.0, 0.025),
             COL_CONCRETE)
    # Sidewalk (running E-W across the yard's south edge)
    make_box("Sidewalk",
             (0.0, -5.6, -0.040),
             (H_X_E - H_X_W + 2.0, 1.20, 0.025),
             COL_CONCRETE)
    # Curb (a thin lip just south of the sidewalk)
    make_box("Curb",
             (0.0, -6.30, -0.020),
             (H_X_E - H_X_W + 2.0, 0.20, 0.06),
             COL_CONCRETE)
    # Asphalt street (south of curb)
    make_box("Street",
             (0.0, -7.30, -0.060),
             (H_X_E - H_X_W + 4.0, 1.80, 0.04),
             COL_ASPHALT)
    # The CURB SPOT where Mrs. Theriot's station wagon parks — a
    # subtle oil stain on the asphalt so the parking spot reads as
    # canonical.
    make_box("CurbOilSpot",
             (-1.0, -6.85, -0.039),
             (1.80, 0.80, 0.001),
             (0.16, 0.14, 0.12, 1.0))

    # Front fence (a small picket fence at the yard's south edge)
    # — just a low decorative fence at the sidewalk side.
    for fi in range(7):
        fx = -3.6 + fi * 1.20
        make_box("FrontFence_Post_%d" % fi,
                 (fx, -5.05, 0.30),
                 (0.06, 0.06, 0.66),
                 COL_FENCE_WOOD)
    # Horizontal rail
    make_box("FrontFence_Rail",
             (0.0, -5.05, 0.30),
             (8.50, 0.04, 0.08),
             COL_FENCE_WOOD)
    # 4 picket boards between posts (decorative — sparse for low-poly)
    for fi in range(7):
        fx = -3.0 + fi * 1.20
        make_box("FrontFence_Picket_%d" % fi,
                 (fx, -5.05, 0.18),
                 (0.04, 0.025, 0.40),
                 COL_FENCE_WOOD)


# ── Front hallway · the Polaroid table, the phone ────────────────

def build_front_hallway():
    # The hallway is the strip just inside the front door — roughly
    # X in [0.6, 2.4], Y in [0, 1.6]. A small rug, a hall table, and
    # an upright wall phone in the niche to the west.

    # Hall rug (a small runner just inside the door)
    make_box("Hall_Rug",
             (1.5, 0.80, 0.012),
             (1.20, 1.40, 0.018),
             COL_RUG)
    # Hall table — narrow, just west of the door
    table_cx = 0.40
    table_cy = 0.60
    table_top_z = 0.78
    make_box("HallTable_Top",
             (table_cx, table_cy, table_top_z),
             (0.50, 0.30, 0.04),
             COL_DOOR)
    for sx in (-1, +1):
        for sy in (-1, +1):
            make_box("HallTable_Leg_%+d_%+d" % (sx, sy),
                     (table_cx + sx * 0.20, table_cy + sy * 0.12, table_top_z / 2.0),
                     (0.04, 0.04, table_top_z),
                     COL_DOORFRAME)
    # ── The Polaroid · the central beat ──
    # Per setup_he_waved: "The Polaroid is the central beat — opening
    # it advances doubt sharply." setup_today_the_drip_can_win: "The
    # Polaroid is on the front hallway table; the morning has already
    # happened." Placed face-up on the hall table.
    polaroid_x = table_cx
    polaroid_y = table_cy - 0.05
    # Polaroid backing (the white border)
    make_box("Polaroid_Backing",
             (polaroid_x, polaroid_y, table_top_z + 0.012),
             (0.090, 0.108, 0.002),
             COL_POLAROID_FRAME)
    # Image area (slightly inset, faded blue-grey + soft figure hints)
    make_box("Polaroid_Image",
             (polaroid_x, polaroid_y + 0.008, table_top_z + 0.014),
             (0.078, 0.078, 0.0005),
             (0.62, 0.62, 0.58, 1.0))
    # A small dark figure-silhouette in the image (deliberately ambiguous)
    make_box("Polaroid_Figure",
             (polaroid_x, polaroid_y + 0.008, table_top_z + 0.0145),
             (0.018, 0.026, 0.0003),
             (0.32, 0.28, 0.24, 1.0))
    # Polaroid white bottom strip (the canonical handwriting space)
    # Already covered by the backing's white extending below; add a
    # thin pencil mark to read as someone's handwritten word
    make_box("Polaroid_Pencil",
             (polaroid_x - 0.02, polaroid_y - 0.044, table_top_z + 0.0146),
             (0.026, 0.005, 0.0003),
             (0.30, 0.24, 0.18, 1.0))

    # ── Wall phone in the west niche ──
    # An upright wall-mounted phone, bakelite-brown, with a small
    # paper notepad above it.
    phone_x = -0.50
    phone_y = 0.10
    phone_z = 1.30
    # Phone body
    make_box("Phone_Body",
             (phone_x, phone_y, phone_z),
             (0.18, 0.10, 0.28),
             COL_PHONE_BAKELITE)
    # Handset cradle (top)
    make_box("Phone_Cradle",
             (phone_x, phone_y - 0.04, phone_z + 0.18),
             (0.20, 0.06, 0.04),
             (0.20, 0.16, 0.14, 1.0))
    # Handset (resting on the cradle)
    make_box("Phone_Handset",
             (phone_x, phone_y - 0.06, phone_z + 0.22),
             (0.22, 0.05, 0.04),
             (0.20, 0.16, 0.14, 1.0))
    # Coiled cord (a few segments)
    for s in range(4):
        make_cyl("Phone_Cord_%d" % s,
                 (phone_x - 0.10, phone_y - 0.05 + s * 0.03, phone_z + 0.06 + s * 0.015),
                 0.008, 0.04,
                 (0.20, 0.16, 0.14, 1.0), segments=4, axis='Y')
    # Notepad above the phone (the family contact list)
    make_box("Phone_Notepad",
             (phone_x, phone_y, phone_z + 0.55),
             (0.18, 0.005, 0.22),
             COL_PAPER)
    # A few hand-written lines on the notepad (darker streaks)
    for li in range(5):
        make_box("Phone_NotepadLine_%d" % li,
                 (phone_x, phone_y - 0.003, phone_z + 0.62 - li * 0.04),
                 (0.14, 0.002, 0.005),
                 (0.30, 0.26, 0.20, 1.0))


# ── Living room · the couch, the picture window ──────────────────

def build_living_room():
    # Living room is roughly X in [-5, 0.9], Y in [0.5, 4.0]
    lr_cx, lr_cy = -2.5, 2.2

    # Couch · south-facing toward the picture window
    couch_cy = 2.4
    couch_cx = -2.5
    couch_w, couch_d = 2.20, 0.90
    couch_seat_z = 0.46
    # Base
    make_box("Couch_Base",
             (couch_cx, couch_cy, couch_seat_z / 2.0),
             (couch_w, couch_d, couch_seat_z),
             COL_FABRIC_COUCH)
    # Backrest (along the north edge, taller)
    make_box("Couch_Back",
             (couch_cx, couch_cy + couch_d / 2.0 - 0.08, 0.85),
             (couch_w, 0.16, 0.50),
             COL_FABRIC_COUCH)
    # Two seat cushions
    for s in (-1, +1):
        make_box("Couch_Cushion_%+d" % s,
                 (couch_cx + s * 0.55, couch_cy, couch_seat_z + 0.05),
                 (1.00, couch_d - 0.20, 0.10),
                 COL_FABRIC_COUCH)
    # Two pillows (one red, one cream)
    make_box("Couch_Pillow_L",
             (couch_cx - 0.85, couch_cy + couch_d / 2.0 - 0.16, couch_seat_z + 0.18),
             (0.30, 0.16, 0.32),
             COL_FABRIC_PILLOW)
    make_box("Couch_Pillow_R",
             (couch_cx + 0.85, couch_cy + couch_d / 2.0 - 0.16, couch_seat_z + 0.18),
             (0.30, 0.16, 0.32),
             (0.86, 0.80, 0.66, 1.0))

    # Coffee table
    ct_cx, ct_cy = -2.5, 1.5
    ct_top_z = 0.42
    make_box("CoffeeTable_Top",
             (ct_cx, ct_cy, ct_top_z),
             (1.10, 0.50, 0.04),
             COL_DOOR)
    for sx in (-1, +1):
        for sy in (-1, +1):
            make_box("CoffeeTable_Leg_%+d_%+d" % (sx, sy),
                     (ct_cx + sx * 0.48, ct_cy + sy * 0.20, ct_top_z / 2.0),
                     (0.06, 0.06, ct_top_z),
                     COL_DOORFRAME)
    # A coffee mug on the table (a beat-anchor for "the morning")
    make_cyl("LivingMug_Body",
             (ct_cx - 0.30, ct_cy + 0.10, ct_top_z + 0.055),
             0.045, 0.10,
             (0.94, 0.90, 0.82, 1.0), segments=10, axis='Z')
    make_box("LivingMug_Handle",
             (ct_cx - 0.30, ct_cy + 0.10 - 0.062, ct_top_z + 0.055),
             (0.018, 0.022, 0.052),
             (0.94, 0.90, 0.82, 1.0))
    # Two stacked magazines/folded letters on the table
    for s in range(2):
        make_box("LivingTable_Paper_%d" % s,
                 (ct_cx + 0.20, ct_cy - 0.10, ct_top_z + 0.022 + s * 0.005),
                 (0.32, 0.22, 0.004),
                 (0.86, 0.82, 0.74 + s * 0.04, 1.0))

    # Side chair (east of the couch)
    sc_cx, sc_cy = -0.60, 2.4
    make_box("SideChair_Seat",
             (sc_cx, sc_cy, 0.46),
             (0.60, 0.60, 0.10),
             COL_CHAIR_VINYL)
    make_box("SideChair_Back",
             (sc_cx, sc_cy + 0.26, 0.85),
             (0.60, 0.08, 0.60),
             COL_CHAIR_VINYL)
    for sx in (-1, +1):
        for sy in (-1, +1):
            make_box("SideChair_Leg_%+d_%+d" % (sx, sy),
                     (sc_cx + sx * 0.24, sc_cy + sy * 0.24, 0.23),
                     (0.04, 0.04, 0.46),
                     COL_METAL_BLACK)

    # Living room rug under the coffee table
    make_box("Living_Rug",
             (ct_cx, ct_cy + 0.2, 0.011),
             (2.20, 1.60, 0.018),
             COL_RUG)


# ── Kitchen · the drip faucet, the coffee pot, the table ─────────

def build_kitchen():
    # Kitchen is east of the partition (X > 1.0). The sink is under
    # the south window facing the back fence; the back window looks
    # north onto the fence + the bird.

    # ── North window over the sink (the bird-on-the-wire window) ──
    kw_x = +3.0
    kw_y = H_Y_N
    kw_w, kw_h = 1.40, 0.90
    kw_cz = 1.45
    make_box("KitchenWin_Glass",
             (kw_x, kw_y, kw_cz),
             (kw_w, 0.04, kw_h),
             COL_WINDOW_GLASS)
    make_box("KitchenWin_MullV",
             (kw_x, kw_y, kw_cz),
             (0.04, 0.06, kw_h),
             COL_WINDOW_FRAME)
    make_box("KitchenWin_MullH",
             (kw_x, kw_y, kw_cz),
             (kw_w, 0.06, 0.04),
             COL_WINDOW_FRAME)
    make_box("KitchenWin_Sill",
             (kw_x, kw_y - 0.05, kw_cz - kw_h / 2.0 - 0.04),
             (kw_w + 0.10, 0.12, 0.04),
             COL_TRIM_WHITE)

    # ── Counter + sink under the north window ──
    cnt_y = H_Y_N - 0.40
    cnt_top_z = 0.92
    # Counter base
    make_box("Kitchen_CounterBase",
             (+3.0, cnt_y, cnt_top_z / 2.0),
             (3.40, 0.66, cnt_top_z),
             (0.78, 0.70, 0.58, 1.0))
    # Counter top (formica · cream + a darker speckle would help
    # but we keep low-poly: a single flat top)
    make_box("Kitchen_CounterTop",
             (+3.0, cnt_y, cnt_top_z + 0.02),
             (3.42, 0.68, 0.04),
             (0.86, 0.82, 0.70, 1.0))
    # Sink basin (a recessed dark box in the counter top, slightly
    # under-flush)
    sink_cx = +3.0
    sink_cy = cnt_y
    make_box("Kitchen_Sink_Basin",
             (sink_cx, sink_cy, cnt_top_z + 0.005),
             (0.60, 0.40, 0.08),
             (0.30, 0.30, 0.30, 1.0))
    # Sink rim (chrome surround)
    make_box("Kitchen_Sink_Rim",
             (sink_cx, sink_cy, cnt_top_z + 0.045),
             (0.66, 0.46, 0.005),
             COL_METAL_STEEL)
    # ── The drip faucet · the central beat ──
    # Per setup_he_waved: "The drip is the drip."
    # Per setup_the_faucet_wins: "you and Philip have already been
    # at the faucet together this morning."
    faucet_cx = sink_cx
    faucet_cy = sink_cy + 0.16
    faucet_base_z = cnt_top_z + 0.05
    # Faucet base
    make_cyl("Kitchen_Faucet_Base",
             (faucet_cx, faucet_cy, faucet_base_z),
             0.030, 0.05, COL_METAL_FAUCET,
             segments=8, axis='Z')
    # Faucet neck (curved arch — built as two segments: vertical + horizontal)
    make_cyl("Kitchen_Faucet_Neck_V",
             (faucet_cx, faucet_cy, faucet_base_z + 0.12),
             0.018, 0.20, COL_METAL_FAUCET,
             segments=8, axis='Z')
    make_cyl("Kitchen_Faucet_Spout",
             (faucet_cx, faucet_cy - 0.08, faucet_base_z + 0.22),
             0.018, 0.16, COL_METAL_FAUCET,
             segments=8, axis='Y')
    # Two handles (hot/cold)
    for sgn, name in ((-1, "Cold"), (+1, "Hot")):
        make_cyl("Kitchen_Faucet_Handle_%s" % name,
                 (faucet_cx + sgn * 0.10, faucet_cy, faucet_base_z + 0.04),
                 0.022, 0.05, COL_METAL_FAUCET,
                 segments=6, axis='Z')
        make_box("Kitchen_Faucet_Lever_%s" % name,
                 (faucet_cx + sgn * 0.10, faucet_cy, faucet_base_z + 0.075),
                 (0.06, 0.014, 0.014),
                 COL_METAL_FAUCET)
    # The drip · a thin vertical streak from the spout down to the
    # basin, frozen mid-fall. Reads as the canonical drip.
    make_cyl("Kitchen_Faucet_Drip",
             (faucet_cx, faucet_cy - 0.16, faucet_base_z + 0.10),
             0.004, 0.12,
             (0.78, 0.86, 0.92, 0.85), segments=4, axis='Z')
    # A small puddle at the bottom of the basin where the drip lands
    make_cyl("Kitchen_Faucet_Puddle",
             (faucet_cx, faucet_cy - 0.16, cnt_top_z - 0.030),
             0.040, 0.005,
             (0.62, 0.74, 0.82, 0.8), segments=10, axis='Z')

    # ── Coffee pot · the kitchen smells like coffee ──
    cp_cx = +1.7
    cp_cy = cnt_y
    # Pot base (black plastic carafe)
    make_box("Coffee_Pot_Base",
             (cp_cx, cp_cy, cnt_top_z + 0.07),
             (0.18, 0.18, 0.14),
             COL_COFFEE_POT)
    # Carafe (a cylinder above the base, semi-clear with brown liquid)
    make_cyl("Coffee_Carafe_Glass",
             (cp_cx + 0.04, cp_cy, cnt_top_z + 0.20),
             0.052, 0.18,
             (0.86, 0.86, 0.88, 0.5), segments=10, axis='Z')
    make_cyl("Coffee_Carafe_Liquid",
             (cp_cx + 0.04, cp_cy, cnt_top_z + 0.18),
             0.048, 0.12,
             COL_COFFEE_LIQUID, segments=10, axis='Z')
    # Carafe handle
    make_box("Coffee_Carafe_Handle",
             (cp_cx - 0.05, cp_cy, cnt_top_z + 0.21),
             (0.018, 0.06, 0.08),
             COL_COFFEE_POT)
    # Top of the machine (where the basket sits)
    make_box("Coffee_Pot_Top",
             (cp_cx, cp_cy, cnt_top_z + 0.40),
             (0.16, 0.16, 0.10),
             COL_COFFEE_POT)
    # Water reservoir (north side of the pot)
    make_box("Coffee_Pot_Reservoir",
             (cp_cx, cp_cy + 0.10, cnt_top_z + 0.30),
             (0.16, 0.04, 0.40),
             (0.30, 0.30, 0.34, 0.65))

    # ── Mug shelf (a half-shelf with 4 mugs) ──
    shelf_cx = +4.5
    shelf_cy = cnt_y
    shelf_z = cnt_top_z + 0.50
    make_box("Mug_Shelf",
             (shelf_cx, shelf_cy, shelf_z),
             (0.60, 0.22, 0.025),
             COL_DOOR)
    # 4 mugs
    for mi in range(4):
        mx = shelf_cx - 0.22 + mi * 0.14
        col = [(0.94, 0.90, 0.82, 1.0),
               (0.62, 0.46, 0.30, 1.0),
               (0.42, 0.52, 0.62, 1.0),
               (0.86, 0.66, 0.38, 1.0)][mi]
        make_cyl("Mug_%d_Body" % mi,
                 (mx, shelf_cy, shelf_z + 0.065),
                 0.038, 0.10, col,
                 segments=8, axis='Z')

    # ── Kitchen table + two chairs ──
    kt_cx, kt_cy = +2.5, +2.2
    kt_top_z = 0.74
    # Table top
    make_box("KitchenTable_Top",
             (kt_cx, kt_cy, kt_top_z),
             (1.20, 0.80, 0.04),
             COL_DOOR)
    # 4 legs
    for sx in (-1, +1):
        for sy in (-1, +1):
            make_box("KitchenTable_Leg_%+d_%+d" % (sx, sy),
                     (kt_cx + sx * 0.52, kt_cy + sy * 0.32, kt_top_z / 2.0),
                     (0.05, 0.05, kt_top_z),
                     COL_DOORFRAME)
    # 2 chairs (north + south sides)
    for cy_off, name in ((+0.60, "N"), (-0.60, "S")):
        ch_cx = kt_cx
        ch_cy = kt_cy + cy_off
        make_box("KitchenChair_%s_Seat" % name,
                 (ch_cx, ch_cy, 0.46),
                 (0.42, 0.42, 0.04),
                 COL_DOOR)
        make_box("KitchenChair_%s_Back" % name,
                 (ch_cx, ch_cy + (+0.18 if cy_off > 0 else -0.18), 0.78),
                 (0.42, 0.04, 0.50),
                 COL_DOOR)
        for sx in (-1, +1):
            for sy in (-1, +1):
                make_box("KitchenChair_%s_Leg_%+d_%+d" % (name, sx, sy),
                         (ch_cx + sx * 0.18, ch_cy + sy * 0.18, 0.23),
                         (0.04, 0.04, 0.46),
                         COL_DOORFRAME)
    # ── The casserole on the kitchen table ──
    # Per setup_today_the_drip_can_win: "Mackenzie's sister is in
    # the kitchen with her casserole." Corningware orange, foil top.
    make_box("Casserole_Dish",
             (kt_cx, kt_cy + 0.10, kt_top_z + 0.06),
             (0.40, 0.28, 0.10),
             COL_CASSEROLE_DISH)
    make_box("Casserole_Foil",
             (kt_cx, kt_cy + 0.10, kt_top_z + 0.118),
             (0.42, 0.30, 0.004),
             (0.86, 0.86, 0.86, 1.0))
    # A small handwritten note on top of the foil ("FOR PHILIP")
    make_box("Casserole_Note",
             (kt_cx - 0.10, kt_cy + 0.10, kt_top_z + 0.122),
             (0.10, 0.08, 0.0005),
             COL_PAPER)
    make_box("Casserole_NoteLine",
             (kt_cx - 0.10, kt_cy + 0.10, kt_top_z + 0.1228),
             (0.08, 0.014, 0.0003),
             (0.30, 0.24, 0.18, 1.0))


# ── Back yard · the fence + the bird ─────────────────────────────

def build_back_yard():
    # Lawn behind the house
    make_box("BackLawn",
             (0.0, +7.6, -0.045),
             (H_X_E - H_X_W + 1.0, 2.20, 0.02),
             COL_LAWN)
    # Back fence (a low wood fence at Y=+8.6, just past the lawn)
    fence_cy = +8.6
    for fi in range(7):
        fx = -3.6 + fi * 1.20
        make_box("BackFence_Post_%d" % fi,
                 (fx, fence_cy, 0.50),
                 (0.08, 0.08, 1.10),
                 COL_FENCE_WOOD)
    # Top rail
    make_box("BackFence_TopRail",
             (0.0, fence_cy, 0.95),
             (8.50, 0.04, 0.06),
             COL_FENCE_WOOD)
    # Mid rail (this is the "fence wire" line — render as a thin
    # cable on top of the rail since the_faucet_wins says "the bird
    # is on the fence wire deliberating")
    make_cyl("BackFence_Wire",
             (0.0, fence_cy + 0.04, 0.99),
             0.005, 8.50,
             COL_METAL_STEEL, segments=4, axis='X')
    # 8 horizontal planks between posts
    for fi in range(7):
        fx = -3.0 + fi * 1.20
        for plank_z, plank_h in ((0.20, 0.18), (0.50, 0.18), (0.80, 0.18)):
            make_box("BackFence_Plank_%d_z%.0f" % (fi, plank_z * 100),
                     (fx, fence_cy, plank_z),
                     (1.10, 0.025, plank_h),
                     COL_FENCE_WOOD)
    # ── The bird · sparrow-sized, on the wire, deliberating ──
    # Position the bird directly outside the kitchen window so the
    # vantage from the sink reads it. Kitchen window center at x=+3.0.
    bird_x = +3.2
    bird_y = fence_cy + 0.04
    bird_z = 1.04
    make_sphere_low("Bird_Body", (bird_x, bird_y, bird_z), 0.06, COL_BIRD)
    # Head
    make_sphere_low("Bird_Head", (bird_x - 0.04, bird_y, bird_z + 0.05), 0.04, COL_BIRD)
    # Beak
    make_box("Bird_Beak",
             (bird_x - 0.08, bird_y, bird_z + 0.04),
             (0.02, 0.012, 0.012),
             (0.62, 0.46, 0.20, 1.0))
    # Tail
    make_box("Bird_Tail",
             (bird_x + 0.06, bird_y, bird_z + 0.02),
             (0.05, 0.020, 0.018),
             COL_BIRD)
    # Two feet (tiny brown boxes)
    for sgn in (-1, +1):
        make_box("Bird_Foot_%+d" % sgn,
                 (bird_x + sgn * 0.015, bird_y + 0.005, bird_z - 0.064),
                 (0.006, 0.006, 0.020),
                 (0.42, 0.30, 0.20, 1.0))

    # A few clumps of damp earth in the back yard (the_faucet_wins:
    # "the kitchen smells like coffee and damp earth")
    for i, (dx, dy) in enumerate([(-1.6, +7.4), (-0.4, +7.6), (+2.2, +7.2)]):
        make_box("BackYard_EarthClump_%d" % i,
                 (dx, dy, 0.015),
                 (0.30, 0.30, 0.03),
                 COL_BROWN_EARTH)


# ── Back porch + back door ───────────────────────────────────────

def build_back_porch():
    bd_x = -2.0
    bd_y = H_Y_N
    bd_w, bd_h = 0.86, 2.00
    # Back door body
    make_box("BackDoor_Body",
             (bd_x, bd_y + 0.02, bd_h / 2.0),
             (bd_w, 0.04, bd_h),
             COL_DOOR)
    # Screen door (just outside)
    make_box("BackDoor_ScreenFrame",
             (bd_x, bd_y + 0.10, bd_h / 2.0),
             (bd_w + 0.04, 0.02, bd_h),
             (0.62, 0.42, 0.26, 1.0))
    make_box("BackDoor_ScreenMesh",
             (bd_x, bd_y + 0.105, bd_h / 2.0),
             (bd_w - 0.10, 0.005, bd_h - 0.20),
             COL_SCREEN_MESH)
    # Knob
    make_sphere_low("BackDoor_Knob",
                    (bd_x + bd_w / 2.0 - 0.10, bd_y + 0.04, 1.00),
                    0.030, COL_METAL_BRASS)
    # Back porch slab (small)
    make_box("BackPorch_Slab",
             (bd_x, H_Y_N + 0.40, 0.05),
             (1.40, 0.80, 0.10),
             COL_CONCRETE)


# ── Bedroom (peek-only · NW corner) ──────────────────────────────

def build_bedroom_peek():
    # Bedroom doorway (an open opening in the south bedroom wall)
    # — just put a doorframe + interior color shift to read as a
    # different room.
    bd_x = -3.0
    bd_y = PART_BEDROOM_Y
    bd_w, bd_h = 0.90, 2.00
    # Doorframe (left)
    make_box("BedroomDoor_FrameL",
             (bd_x - bd_w/2.0 - 0.04, bd_y, bd_h / 2.0),
             (0.06, WALL_T + 0.04, bd_h),
             COL_DOORFRAME)
    make_box("BedroomDoor_FrameR",
             (bd_x + bd_w/2.0 + 0.04, bd_y, bd_h / 2.0),
             (0.06, WALL_T + 0.04, bd_h),
             COL_DOORFRAME)
    # Lintel
    make_box("BedroomDoor_Lintel",
             (bd_x, bd_y, bd_h + 0.04),
             (bd_w + 0.20, WALL_T + 0.04, 0.06),
             COL_DOORFRAME)
    # Cover up the partition wall in the doorway gap by overlaying
    # a darker color box (reads as the opening)
    make_box("BedroomDoor_Gap",
             (bd_x, bd_y, bd_h / 2.0),
             (bd_w, WALL_T + 0.02, bd_h),
             (0.16, 0.14, 0.16, 1.0))

    # Bed (peek through the doorway — just the foot of the bed)
    bed_cx = -3.5
    bed_cy = +5.4
    # Mattress
    make_box("Bedroom_Bed_Mattress",
             (bed_cx, bed_cy, 0.40),
             (1.40, 1.90, 0.18),
             (0.86, 0.80, 0.66, 1.0))
    # Headboard (north, against back wall)
    make_box("Bedroom_Bed_Headboard",
             (bed_cx, bed_cy + 0.95, 0.85),
             (1.50, 0.06, 0.80),
             COL_DOOR)
    # Bedside lamp (small)
    make_cyl("Bedroom_Lamp_Base",
             (bed_cx - 0.95, bed_cy + 0.5, 0.52),
             0.05, 0.04, COL_METAL_BRASS,
             segments=6, axis='Z')
    make_cyl("Bedroom_Lamp_Post",
             (bed_cx - 0.95, bed_cy + 0.5, 0.66),
             0.012, 0.20, COL_METAL_BRASS,
             segments=4, axis='Z')
    make_box("Bedroom_Lamp_Shade",
             (bed_cx - 0.95, bed_cy + 0.5, 0.84),
             (0.16, 0.16, 0.10),
             (0.86, 0.78, 0.62, 1.0))


# ── Export ───────────────────────────────────────────────────────

def export_glb():
    out_dir = os.path.abspath(os.path.join(_SCRIPT_DIR, OUTPUT_DIR))
    os.makedirs(out_dir, exist_ok=True)
    out_path = os.path.join(out_dir, OUTPUT_NAME)
    # Select all
    bpy.ops.object.select_all(action='SELECT')
    bpy.ops.export_scene.gltf(
        filepath=out_path,
        export_format='GLB',
        export_apply=True,
        use_selection=True,
        export_materials='EXPORT',
    )
    print("[build_roberts_house] exported %s" % out_path)


def main():
    clear_scene()
    build_shell()
    build_interior_partitions()
    build_front_facade()
    build_front_yard_and_curb()
    build_front_hallway()
    build_living_room()
    build_kitchen()
    build_back_yard()
    build_back_porch()
    build_bedroom_peek()
    export_glb()


if __name__ == "__main__":
    main()
