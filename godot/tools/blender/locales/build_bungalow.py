"""
build_bungalow.py
══════════════════════════════════════════════════════════════════
VOL 5 · CHAPTER 2 · The Priestess · Elicia Duchane's bungalow.

A small one-bedroom Westbrook-side bungalow with a converted
laundry-alcove studio for her show. The 10 named stations from
resources/games/locations/elicia_bungalow.json are built into the
walkable footprint:

  LIVING ROOM        cardboard boxes along the wall, side table
                     with the Whispers script page, warped floor
  THE STUDIO         converted laundry alcove, overhead light,
                     mic boom, Anya's chair
  THE EDITING DESK   laptop, two external drives, headphones, cold
                     coffee
  THE BOOKSHELF      thrift tarot decks, mirror shard, framing
                     books, cookie box
  THE KITCHEN        teacup, basil plant (dying), listing kettle
  THE BEDROOM        unmade bed, dresser with face-down picture,
                     laundry pile
  THE BATHROOM       mirror over sink, medicine cabinet
  THE STORAGE CLOSET five boxes of Pomegranate Hour material
                     (behind the studio)
  THE PORCH          two wicker chairs (one missing left arm),
                     ashtray, unhung wind chime
  THE BACK YARD      dying garden, rosemary bush, basil bed +
                     tomatoes (against canon, second August)

Thresholds:
  FRONT DOOR  south side, screen + storm, sticky latch, WELCOME mat
  BACK GATE   onto the alley, hinges complain
  ROOF        kitchen fire escape ladder up; flat roof, the
              wide-shot vantage on dusk Graustark

COORDINATE FRAME (Blender → Godot):
    +X east   → +X
    +Y north  → -Z
    +Z up     → +Y
1 unit = 1 m. Bungalow footprint is +X ∈ [-5, +5], +Y ∈ [0, +6];
front porch hangs out at Y ∈ [-2.5, 0]; back yard at Y ∈ [+6, +10].

Run:
    blender --background --python build_bungalow.py
    (or ./run_cathedral.sh build_bungalow.py)

Output:
    godot/assets/3d/locales/bungalow.glb
"""

import bpy
import math
import os
import sys

_SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
if _SCRIPT_DIR not in sys.path:
    sys.path.insert(0, _SCRIPT_DIR)

OUTPUT_DIR  = "../../../assets/3d/locales"
OUTPUT_NAME = "bungalow.glb"


# ── Palette ──────────────────────────────────────────────────────
# Westbrook bungalow: warm hardwood, soft creams, pale teals — a
# space made habitable by accumulation, not by design.
COL_FLOOR_WOOD  = (0.46, 0.32, 0.20, 1.0)   # warped hardwood
COL_FLOOR_TILE  = (0.78, 0.72, 0.62, 1.0)   # bathroom + kitchen tile
COL_WALL_CREAM  = (0.92, 0.86, 0.72, 1.0)   # interior walls
COL_WALL_TEAL   = (0.62, 0.74, 0.72, 1.0)   # bedroom accent
COL_WALL_OUTER  = (0.86, 0.74, 0.58, 1.0)   # exterior siding
COL_TRIM_WHITE  = (0.95, 0.92, 0.88, 1.0)
COL_CEILING     = (0.88, 0.84, 0.78, 1.0)
COL_DOOR        = (0.40, 0.28, 0.18, 1.0)
COL_DOORFRAME   = (0.32, 0.22, 0.14, 1.0)
COL_WINDOW_GLASS = (0.58, 0.74, 0.82, 0.85)
COL_WINDOW_FRAME = (0.30, 0.20, 0.12, 1.0)

COL_FABRIC_LINEN  = (0.86, 0.80, 0.66, 1.0)
COL_FABRIC_SHEET  = (0.74, 0.78, 0.84, 1.0)
COL_FABRIC_RUG    = (0.62, 0.42, 0.36, 1.0)
COL_WICKER        = (0.72, 0.58, 0.34, 1.0)

COL_METAL_BRASS = (0.78, 0.62, 0.30, 1.0)
COL_METAL_STEEL = (0.62, 0.66, 0.70, 1.0)
COL_METAL_BLACK = (0.16, 0.14, 0.14, 1.0)

COL_CARDBOARD   = (0.72, 0.58, 0.36, 1.0)
COL_PAPER       = (0.92, 0.88, 0.78, 1.0)
COL_PAPER_DARK  = (0.78, 0.70, 0.54, 1.0)
COL_BOOK_RED    = (0.62, 0.20, 0.18, 1.0)
COL_BOOK_BLUE   = (0.22, 0.32, 0.52, 1.0)
COL_BOOK_GREEN  = (0.26, 0.40, 0.28, 1.0)
COL_BOOK_BLACK  = (0.18, 0.16, 0.18, 1.0)

COL_GREEN_LEAF  = (0.32, 0.52, 0.26, 1.0)
COL_GREEN_DYING = (0.50, 0.46, 0.22, 1.0)   # the basil
COL_GREEN_HERB  = (0.28, 0.40, 0.22, 1.0)   # rosemary
COL_SOIL        = (0.22, 0.16, 0.10, 1.0)
COL_TOMATO      = (0.72, 0.18, 0.16, 1.0)

COL_BRASS_PAINT = (0.62, 0.46, 0.22, 1.0)   # gauntlet floor stencil
COL_NUMERAL     = (0.78, 0.62, 0.30, 1.0)
COL_PLATE       = (0.46, 0.36, 0.20, 1.0)

# Tarot-deck box tints (the bookshelf)
TAROT_TINTS = [
    (0.62, 0.20, 0.36, 1.0),
    (0.22, 0.36, 0.52, 1.0),
    (0.42, 0.32, 0.56, 1.0),
    (0.30, 0.46, 0.36, 1.0),
    (0.78, 0.62, 0.30, 1.0),
]


# ── Geometry helpers (vendored from build_riverfront.py) ──────────
def clear_scene():
    for obj in list(bpy.data.objects):
        bpy.data.objects.remove(obj, do_unlink=True)
    for mesh in list(bpy.data.meshes):
        bpy.data.meshes.remove(mesh, do_unlink=True)


def _finalize_mesh(name, verts, faces, base_color):
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
        ('-Z', (0,3,2,1)), ('+Z', (4,5,6,7)),
        ('-Y', (0,1,5,4)), ('+Y', (2,3,7,6)),
        ('-X', (3,0,4,7)), ('+X', (1,2,6,5)),
    ]
    out_faces = [vids for tag, vids in face_defs if tag not in open_faces]
    return _finalize_mesh(name, verts, out_faces, base_color)


def make_cyl(name, center, radius, height, base_color,
             segments=8, axis='Z'):
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
            else:  # 'X'
                verts.append((cx + z_off, cy + a, cz + b))
    faces = []
    for i in range(segments):
        ni = (i + 1) % segments
        faces.append([i, ni, ni + segments, i + segments])
    faces.append(list(reversed(range(segments))))
    faces.append(list(range(segments, segments * 2)))
    return _finalize_mesh(name, verts, faces, base_color)


def make_prism(name, center, size, base_color):
    """Triangular prism (roof peak running along Y)."""
    cx, cy, cz = center
    sx, sy, sz = size
    hx, hy, hz = sx/2, sy/2, sz/2
    verts = [
        (cx-hx, cy-hy, cz-hz), (cx+hx, cy-hy, cz-hz),
        (cx+hx, cy+hy, cz-hz), (cx-hx, cy+hy, cz-hz),
        (cx,    cy-hy, cz+hz), (cx,    cy+hy, cz+hz),
    ]
    faces = [
        [0, 1, 2, 3],          # bottom
        [0, 4, 1],             # south end
        [2, 5, 3],             # north end
        [0, 3, 5, 4],          # west slope
        [1, 4, 5, 2],          # east slope
    ]
    return _finalize_mesh(name, verts, faces, base_color)


# ── Gauntlet station marker ──────────────────────────────────────
def gauntlet_marker(label, cx, cy, w, d, numeral):
    """Paint a brass-stencil rectangle on the floor + a numeral
    plate. Mirrors build_cathedral_interior._zone_marker style so
    the two locations read as the same gauntlet system."""
    Z_PAINT = 0.063
    for sgn in (-1, +1):
        make_box(f"{label}_outline_x{sgn:+d}",
                 (cx + sgn * w / 2, cy, Z_PAINT),
                 (0.06, d, 0.005), COL_BRASS_PAINT)
        make_box(f"{label}_outline_y{sgn:+d}",
                 (cx, cy + sgn * d / 2, Z_PAINT),
                 (w, 0.06, 0.005), COL_BRASS_PAINT)
    make_box(f"{label}_plate",
             (cx, cy - d / 2 + 0.18, Z_PAINT + 0.001),
             (0.42, 0.14, 0.004), COL_PLATE)
    make_box(f"{label}_numeral",
             (cx, cy - d / 2 + 0.18, Z_PAINT + 0.0015),
             (0.30, 0.09, 0.002), COL_NUMERAL)


# ════════════════════════════════════════════════════════════════
# BUILDING SHELL
# ════════════════════════════════════════════════════════════════
INTERIOR_X_W = -5.0   # west wall
INTERIOR_X_E =  5.0   # east wall
INTERIOR_Y_S =  0.0   # south (front) wall
INTERIOR_Y_N =  6.0   # north (back) wall
CEIL_Z       =  2.70  # interior ceiling
ROOF_Z       =  3.20  # exterior flat-roof top (accessible)


def build_shell():
    """Slab floor + four exterior walls + flat roof. The roof is
    accessible — flat with a low parapet so the ROOF threshold
    station works as a walkable vantage."""
    # Slab — concrete-coloured underbase + hardwood deck on top
    make_box("Slab",
             (0.0, (INTERIOR_Y_S + INTERIOR_Y_N) / 2.0, -0.05),
             (10.4, 6.4, 0.10), (0.42, 0.40, 0.38, 1.0))
    make_box("Floor_Hardwood",
             (0.0, (INTERIOR_Y_S + INTERIOR_Y_N) / 2.0, 0.005),
             (10.0, 6.0, 0.02), COL_FLOOR_WOOD)
    # Plank seams — running east-west, so the warp reads
    for i in range(-2, 3):
        y = (INTERIOR_Y_S + INTERIOR_Y_N) / 2.0 + i * 1.0
        make_box(f"Floor_Seam_{i}",
                 (0.0, y, 0.012), (10.0, 0.01, 0.001),
                 (0.32, 0.22, 0.14, 1.0))

    # Exterior walls — east/west/north/south
    # South wall has front-door opening
    make_box("Wall_S_W", (-3.4, INTERIOR_Y_S, 1.35),
             (3.2, 0.20, 2.70), COL_WALL_OUTER)
    make_box("Wall_S_E", (+3.4, INTERIOR_Y_S, 1.35),
             (3.2, 0.20, 2.70), COL_WALL_OUTER)
    make_box("Wall_S_AboveDoor", (0.0, INTERIOR_Y_S, 2.50),
             (1.6, 0.20, 0.40), COL_WALL_OUTER)
    # North wall has the back-door (kitchen → yard) cutout
    make_box("Wall_N_W", (-3.4, INTERIOR_Y_N, 1.35),
             (3.2, 0.20, 2.70), COL_WALL_OUTER)
    make_box("Wall_N_E", (+3.4, INTERIOR_Y_N, 1.35),
             (3.2, 0.20, 2.70), COL_WALL_OUTER)
    make_box("Wall_N_AboveDoor", (0.0, INTERIOR_Y_N, 2.50),
             (1.6, 0.20, 0.40), COL_WALL_OUTER)
    # East/West walls — full height, no cuts
    make_box("Wall_E", (INTERIOR_X_E, 3.0, 1.35),
             (0.20, 6.0, 2.70), COL_WALL_OUTER)
    make_box("Wall_W", (INTERIOR_X_W, 3.0, 1.35),
             (0.20, 6.0, 2.70), COL_WALL_OUTER)

    # Front door + back door
    make_box("FrontDoor", (0.0, INTERIOR_Y_S - 0.04, 1.05),
             (1.40, 0.04, 2.10), COL_DOOR)
    make_box("FrontDoor_Frame_T", (0.0, INTERIOR_Y_S, 2.18),
             (1.60, 0.22, 0.12), COL_DOORFRAME)
    # Screen door overlay (paler, in front)
    make_box("FrontDoor_Screen", (0.0, INTERIOR_Y_S - 0.10, 1.05),
             (1.40, 0.02, 2.10), (0.62, 0.60, 0.52, 0.6))
    # Sticky latch — brass knob with a notable extrusion
    make_cyl("FrontDoor_Latch",
             (0.55, INTERIOR_Y_S - 0.10, 1.05), 0.06, 0.06,
             COL_METAL_BRASS, segments=8, axis='Y')

    make_box("BackDoor", (0.0, INTERIOR_Y_N + 0.04, 1.05),
             (1.40, 0.04, 2.10), COL_DOOR)
    make_box("BackDoor_Frame_T", (0.0, INTERIOR_Y_N, 2.18),
             (1.60, 0.22, 0.12), COL_DOORFRAME)

    # WELCOME mat — outside the front door, cursive
    make_box("WelcomeMat",
             (0.0, INTERIOR_Y_S - 0.90, 0.012),
             (1.20, 0.80, 0.02), COL_FABRIC_RUG)
    make_box("WelcomeMat_Letters",
             (0.0, INTERIOR_Y_S - 0.90, 0.014),
             (0.80, 0.18, 0.002), COL_TRIM_WHITE)

    # Windows — south wall (living room), east wall (studio),
    # west wall (bedroom + bathroom), north wall (kitchen)
    for wx, wy, label in [(-2.5, INTERIOR_Y_S, "Win_LR"),
                          (+3.0, INTERIOR_Y_S, "Win_Studio_S")]:
        make_box(label, (wx, wy, 1.50), (1.10, 0.06, 1.00),
                 COL_WINDOW_GLASS)
        make_box(label + "_Frame_T", (wx, wy, 2.05),
                 (1.20, 0.06, 0.08), COL_WINDOW_FRAME)
        make_box(label + "_Frame_B", (wx, wy, 0.95),
                 (1.20, 0.06, 0.08), COL_WINDOW_FRAME)
    # Studio east window (the room is on the east side)
    make_box("Win_Studio_E", (INTERIOR_X_E, +1.8, 1.65),
             (0.06, 0.90, 0.80), COL_WINDOW_GLASS)
    # Kitchen north window (where the basil dies)
    make_box("Win_Kitchen", (+2.8, INTERIOR_Y_N, 1.55),
             (1.30, 0.06, 0.90), COL_WINDOW_GLASS)
    make_box("Win_Kitchen_FrameT", (+2.8, INTERIOR_Y_N, 2.05),
             (1.40, 0.06, 0.08), COL_WINDOW_FRAME)
    make_box("Win_Kitchen_FrameB", (+2.8, INTERIOR_Y_N, 1.05),
             (1.40, 0.06, 0.08), COL_WINDOW_FRAME)
    # Bedroom west window
    make_box("Win_Bedroom", (INTERIOR_X_W, +4.5, 1.55),
             (0.06, 1.20, 0.90), COL_WINDOW_GLASS)
    # Bathroom small frosted west window
    make_box("Win_Bathroom", (INTERIOR_X_W, +1.0, 1.85),
             (0.06, 0.50, 0.40), (0.80, 0.84, 0.82, 0.7))

    # Ceiling — single slab; we cut a small notch where the studio's
    # overhead light hangs but otherwise this is one piece
    make_box("Ceiling",
             (0.0, (INTERIOR_Y_S + INTERIOR_Y_N) / 2.0, CEIL_Z),
             (10.0, 6.0, 0.10), COL_CEILING)
    # Flat roof above (player walks on this when on the ROOF)
    make_box("Roof_Slab",
             (0.0, (INTERIOR_Y_S + INTERIOR_Y_N) / 2.0, ROOF_Z),
             (10.4, 6.4, 0.10), (0.32, 0.24, 0.18, 1.0))
    # Low parapet around the roof so the player has a visual edge
    for sgn in (-1, +1):
        make_box(f"Roof_Parapet_E{sgn:+d}",
                 (INTERIOR_X_E * sgn + sgn * 0.1,
                  3.0, ROOF_Z + 0.30),
                 (0.20, 6.5, 0.50), (0.62, 0.52, 0.38, 1.0))
    for sgn, y_pos in [(-1, INTERIOR_Y_S - 0.1),
                       (+1, INTERIOR_Y_N + 0.1)]:
        make_box(f"Roof_Parapet_NS{sgn:+d}",
                 (0.0, y_pos, ROOF_Z + 0.30),
                 (10.5, 0.20, 0.50), (0.62, 0.52, 0.38, 1.0))


# ════════════════════════════════════════════════════════════════
# INTERIOR PARTITIONS — divide the interior into rooms
# ════════════════════════════════════════════════════════════════
#
# Floor plan (looking down, +Y north):
#
#   Y=+6  ┌────────────────────────────────────┐  back yard above
#         │ BEDROOM         │   KITCHEN        │
#   Y=+3  ├───────────┬─────┴──────────────────┤
#         │ BATH      │ STORAGE       │ STUDIO │
#         │           │ CLOSET        │ +ED    │
#   Y=+1.5├───────────┤               │ DESK   │
#         │           │ LIVING ROOM   │        │
#         │ (corridor)│ + BOOKSHELF   │        │
#   Y=0   └───────────┴───────────────┴────────┘  front porch below
#         X=-5   X=-2.5         X=+1.5      X=+5
#
def build_partitions():
    """Interior partitions splitting the bungalow's 10m × 6m
    footprint into seven rooms. Wall thickness 0.10m. Each wall
    is named so future passes can move/break them."""
    # ── East-west mid-wall at Y=+3 splitting front and back of house
    # Run W-end to start of kitchen-bedroom door opening
    make_box("Mid_S_W", (-3.0, +3.0, 1.35),
             (4.0, 0.10, 2.70), COL_WALL_CREAM)
    # Door opening between living room and bedroom corridor — 0.9m
    # cut at X=-1
    make_box("Mid_S_Mid", (-0.5, +3.0, 1.35),
             (0.0, 0.10, 2.70), COL_WALL_CREAM)
    # E section
    make_box("Mid_S_E", (+2.0, +3.0, 1.35),
             (5.0, 0.10, 2.70), COL_WALL_CREAM)
    # Above-door header for symmetry — covers bedroom passage
    make_box("Mid_S_Above_Bed", (-1.0, +3.0, 2.45),
             (1.0, 0.10, 0.50), COL_WALL_CREAM)

    # ── North-south wall at X=-2.5 splitting bathroom from corridor
    make_box("NS_Bath", (-2.5, +0.75, 1.35),
             (0.10, 1.50, 2.70), COL_WALL_CREAM)
    # Bathroom door at Y=+2.0 (0.8m wide gap)
    make_box("NS_Bath_Above_Door", (-2.5, +1.95, 2.40),
             (0.10, 0.10, 0.60), COL_WALL_CREAM)
    # Continues up to Y=+3
    make_box("NS_Bath_Top", (-2.5, +2.40, 1.35),
             (0.10, 0.10, 2.70), COL_WALL_CREAM)

    # ── North-south wall at X=+1.5 splitting living room from studio
    # Door cut at Y=+1.5 (1.0m wide)
    make_box("NS_Studio_S", (+1.5, +0.5, 1.35),
             (0.10, 1.00, 2.70), COL_WALL_CREAM)
    make_box("NS_Studio_N", (+1.5, +2.5, 1.35),
             (0.10, 1.00, 2.70), COL_WALL_CREAM)
    make_box("NS_Studio_AboveDoor", (+1.5, +1.5, 2.45),
             (0.10, 1.00, 0.50), COL_WALL_CREAM)

    # ── Storage closet wall — splits the back of the studio into a
    # small closet at the south corner (the OLD laundry room, now
    # the storage room for Pomegranate Hour boxes).
    make_box("Closet_W", (-1.0, +2.0, 1.35),
             (0.10, 2.00, 2.70), COL_WALL_CREAM)
    # Closet wraps around — north wall at Y=+3 is shared with mid_S
    # E wall — short stub closing the closet
    make_box("Closet_S", (-0.0, +1.0, 1.35),
             (2.0, 0.10, 2.70), COL_WALL_CREAM)
    # Closet door at X=-0.7 (sliding door, depicted shut)
    # (Actually we leave a 0.7m opening on the east wall; closing
    # wall doesn't continue past door.)

    # ── Bedroom accent wall — paint a darker teal on bedroom side
    make_box("BedroomAccentWall_N",
             (-3.0, INTERIOR_Y_N - 0.11, 1.35),
             (4.0, 0.02, 2.70), COL_WALL_TEAL)

    # ── Bathroom + kitchen tile floors override hardwood
    make_box("Bathroom_Tile",
             (-3.75, +0.75, 0.013),
             (2.50, 1.50, 0.010), COL_FLOOR_TILE)
    make_box("Kitchen_Tile",
             (+1.95, +4.5, 0.013),
             (6.10, 3.00, 0.010), COL_FLOOR_TILE)
    # Grout lines on kitchen tile — subtle grid
    for i in range(-3, 4):
        x = +1.95 + i * 0.80
        make_box(f"Kitchen_Grout_X_{i}",
                 (x, +4.5, 0.015), (0.005, 3.00, 0.001),
                 (0.42, 0.36, 0.28, 1.0))
    for i in range(-1, 3):
        y = +4.5 + i * 0.80
        make_box(f"Kitchen_Grout_Y_{i}",
                 (+1.95, y, 0.015), (6.10, 0.005, 0.001),
                 (0.42, 0.36, 0.28, 1.0))


# ════════════════════════════════════════════════════════════════
# STATION I · THE LIVING ROOM
# Cardboard boxes along the east wall, warped hardwood, side table
# with the Whispers script page. Two years half-packed.
# ════════════════════════════════════════════════════════════════
LIVING_CX, LIVING_CY = -0.5, +1.6


def build_living_room():
    gauntlet_marker("Z_LivingRoom", LIVING_CX, LIVING_CY, 3.4, 2.2, "II")

    # ── Cardboard moving boxes stacked along the (north partition)
    # of the living room — staggered heights, taped + labeled
    boxes = [
        # (x, y, w, d, h, label_color, label_text_present)
        (-0.2, +2.6, 0.50, 0.50, 0.50, True),
        (+0.4, +2.6, 0.50, 0.45, 0.50, False),
        (+1.0, +2.6, 0.55, 0.50, 0.50, True),
        (-0.2, +2.6, 0.50, 0.45, 0.40),   # stacked on first
        (+0.4, +2.6, 0.50, 0.40, 0.40),
    ]
    # Re-emit with stack heights
    z = 0.25
    make_box("LR_Box_1", (-0.2, +2.6, z),
             (0.50, 0.50, 0.50), COL_CARDBOARD)
    make_box("LR_Box_2", (+0.4, +2.6, z),
             (0.50, 0.45, 0.50), COL_CARDBOARD)
    make_box("LR_Box_3", (+1.0, +2.6, z),
             (0.55, 0.50, 0.50), COL_CARDBOARD)
    # Stack on top
    make_box("LR_Box_4", (-0.2, +2.65, z + 0.45),
             (0.46, 0.42, 0.40), COL_CARDBOARD)
    make_box("LR_Box_5", (+0.7, +2.60, z + 0.45),
             (0.60, 0.45, 0.40), COL_CARDBOARD)
    # Tape strips on the lids
    for i, bx in enumerate([-0.2, +0.4, +1.0, -0.2, +0.7]):
        bz = (z + 0.50 + 0.001) if i < 3 else (z + 0.45 + 0.40 + 0.001)
        make_box(f"LR_Box_Tape_{i}",
                 (bx, +2.6, bz),
                 (0.06, 0.40, 0.002), COL_PAPER)
    # Marker labels — illegible at this scale, but visible
    for i, (bx, by) in enumerate([(-0.2, +2.6), (+0.4, +2.6), (+1.0, +2.6)]):
        make_box(f"LR_Box_Label_{i}",
                 (bx - 0.20, by - 0.255, z + 0.25),
                 (0.16, 0.004, 0.06), COL_PAPER)

    # ── Side table next to the (south, facing the window) seating —
    # with the Whispers script page on it
    table_x, table_y = -2.2, +1.8
    make_box("LR_SideTable_Top",
             (table_x, table_y, 0.62),
             (0.50, 0.40, 0.03), (0.46, 0.32, 0.22, 1.0))
    for sx in (-1, +1):
        for sy in (-1, +1):
            make_cyl(f"LR_SideTable_Leg_{sx}_{sy}",
                     (table_x + sx * 0.20, table_y + sy * 0.15, 0.30),
                     0.018, 0.60, (0.36, 0.24, 0.16, 1.0))
    # The Whispers script page — single sheet on top
    make_box("LR_ScriptPage",
             (table_x + 0.04, table_y + 0.05, 0.638),
             (0.21, 0.27, 0.003), COL_PAPER)
    # A red ink scribble across it (Elicia's notes)
    make_box("LR_ScriptPage_Mark",
             (table_x - 0.04, table_y + 0.02, 0.640),
             (0.08, 0.18, 0.001), COL_BOOK_RED)

    # ── Reading chair — a single tired armchair facing the south
    # window. The chair you sat in too long, in '23.
    ch_x, ch_y = -1.6, +0.8
    make_box("LR_Chair_Seat",
             (ch_x, ch_y, 0.42),
             (0.70, 0.65, 0.20), (0.52, 0.40, 0.32, 1.0))
    make_box("LR_Chair_Back",
             (ch_x, ch_y + 0.30, 0.95),
             (0.70, 0.12, 0.90), (0.52, 0.40, 0.32, 1.0))
    make_box("LR_Chair_ArmL",
             (ch_x - 0.32, ch_y - 0.02, 0.66),
             (0.10, 0.62, 0.30), (0.42, 0.32, 0.26, 1.0))
    make_box("LR_Chair_ArmR",
             (ch_x + 0.32, ch_y - 0.02, 0.66),
             (0.10, 0.62, 0.30), (0.42, 0.32, 0.26, 1.0))

    # ── Floor lamp behind the chair
    make_cyl("LR_FloorLamp_Pole",
             (ch_x + 0.50, ch_y - 0.30, 0.80),
             0.018, 1.60, COL_METAL_BLACK)
    make_box("LR_FloorLamp_Base",
             (ch_x + 0.50, ch_y - 0.30, 0.03),
             (0.26, 0.26, 0.04), COL_METAL_BLACK)
    make_cyl("LR_FloorLamp_Shade",
             (ch_x + 0.50, ch_y - 0.30, 1.65),
             0.18, 0.28, (0.92, 0.84, 0.66, 1.0), segments=10)

    # ── Warped-floor hint — a single plank pushed up slightly
    # (the warp the flavor mentions)
    make_box("LR_FloorWarp",
             (-1.0, +1.6, 0.030),
             (0.18, 1.40, 0.025), (0.36, 0.24, 0.14, 1.0))


# ════════════════════════════════════════════════════════════════
# STATION · THE STUDIO  +  STATION · THE EDITING DESK
# Converted laundry alcove. Overhead light, mic boom, Anya's chair.
# Editing desk inside: laptop, two external drives, headphones,
# coffee cup with one cold inch.
# ════════════════════════════════════════════════════════════════
STUDIO_CX, STUDIO_CY = +3.2, +1.8


def build_studio_and_editing_desk():
    gauntlet_marker("Z_Studio", STUDIO_CX - 0.4, STUDIO_CY + 0.6, 1.6, 1.2, "II")
    gauntlet_marker("Z_EditingDesk", STUDIO_CX + 0.5, STUDIO_CY - 0.6, 1.2, 1.0, "II")

    # ── Overhead light bracket (the "powerful overhead light") ──
    # Big can light slung from the ceiling on a frame
    make_box("Studio_LightBracket",
             (STUDIO_CX, STUDIO_CY + 0.4, CEIL_Z - 0.05),
             (0.80, 0.60, 0.04), COL_METAL_BLACK)
    make_cyl("Studio_OverheadLight",
             (STUDIO_CX, STUDIO_CY + 0.4, CEIL_Z - 0.30),
             0.22, 0.30, COL_METAL_STEEL)
    # Bright bulb visible inside
    make_box("Studio_OverheadBulb",
             (STUDIO_CX, STUDIO_CY + 0.4, CEIL_Z - 0.42),
             (0.30, 0.30, 0.04), (0.98, 0.94, 0.78, 1.0))

    # ── Microphone boom — the small mic boom on a stand ──
    boom_x, boom_y = STUDIO_CX - 0.5, STUDIO_CY + 0.5
    make_cyl("Studio_BoomStand_Base",
             (boom_x, boom_y, 0.02),
             0.20, 0.04, COL_METAL_BLACK)
    make_cyl("Studio_BoomStand_Pole",
             (boom_x, boom_y, 0.90),
             0.018, 1.70, COL_METAL_BLACK)
    # Horizontal arm
    make_box("Studio_BoomStand_Arm",
             (boom_x + 0.32, boom_y, 1.70),
             (0.70, 0.025, 0.025), COL_METAL_BLACK)
    # Cardioid mic shape at end
    make_cyl("Studio_Mic",
             (boom_x + 0.62, boom_y, 1.66),
             0.04, 0.18, COL_METAL_BLACK, segments=8, axis='Z')
    make_cyl("Studio_Mic_Mesh",
             (boom_x + 0.62, boom_y, 1.78),
             0.05, 0.10, (0.32, 0.30, 0.30, 1.0), segments=8, axis='Z')
    # Pop filter — flat circle in front
    make_cyl("Studio_PopFilter",
             (boom_x + 0.55, boom_y, 1.74),
             0.06, 0.014, (0.18, 0.16, 0.16, 1.0), segments=10, axis='Y')

    # ── Anya's chair — a director's-style chair facing the mic ──
    ay_x, ay_y = STUDIO_CX - 0.6, STUDIO_CY - 0.4
    make_box("Studio_AnyaChair_Seat",
             (ay_x, ay_y, 0.50),
             (0.46, 0.46, 0.06), (0.36, 0.20, 0.14, 1.0))
    make_box("Studio_AnyaChair_Back",
             (ay_x, ay_y + 0.20, 0.85),
             (0.46, 0.05, 0.40), (0.36, 0.20, 0.14, 1.0))
    for sx in (-1, +1):
        for sy in (-1, +1):
            make_cyl(f"Studio_AnyaChair_Leg_{sx}_{sy}",
                     (ay_x + sx * 0.18, ay_y + sy * 0.18, 0.25),
                     0.014, 0.50, COL_METAL_BLACK)

    # ── EDITING DESK — desk along the studio's east wall ──
    desk_x, desk_y = STUDIO_CX + 0.5, STUDIO_CY - 0.5
    make_box("Studio_Desk_Top",
             (desk_x, desk_y, 0.72),
             (1.40, 0.65, 0.04), (0.36, 0.26, 0.18, 1.0))
    for sx in (-1, +1):
        for sy in (-1, +1):
            make_cyl(f"Studio_Desk_Leg_{sx}_{sy}",
                     (desk_x + sx * 0.62, desk_y + sy * 0.28, 0.36),
                     0.020, 0.72, (0.24, 0.18, 0.12, 1.0))
    # Laptop — open
    make_box("Studio_Laptop_Base",
             (desk_x, desk_y, 0.755),
             (0.40, 0.30, 0.02), COL_METAL_STEEL)
    make_box("Studio_Laptop_Screen",
             (desk_x, desk_y - 0.16, 0.96),
             (0.40, 0.02, 0.30), COL_METAL_STEEL)
    # Screen glow (lit content)
    make_box("Studio_Laptop_ScreenGlow",
             (desk_x, desk_y - 0.151, 0.96),
             (0.36, 0.001, 0.26), (0.42, 0.56, 0.78, 1.0))
    # Two external drives — stacked, humming
    make_box("Studio_HD_1",
             (desk_x + 0.48, desk_y, 0.762),
             (0.16, 0.22, 0.04), (0.20, 0.20, 0.22, 1.0))
    make_box("Studio_HD_2",
             (desk_x + 0.48, desk_y, 0.808),
             (0.16, 0.22, 0.04), (0.20, 0.20, 0.22, 1.0))
    # Tiny green activity LEDs on each
    make_box("Studio_HD_LED1",
             (desk_x + 0.55, desk_y + 0.10, 0.762 + 0.020),
             (0.012, 0.012, 0.004), (0.32, 0.98, 0.40, 1.0))
    make_box("Studio_HD_LED2",
             (desk_x + 0.55, desk_y + 0.10, 0.808 + 0.020),
             (0.012, 0.012, 0.004), (0.32, 0.98, 0.40, 1.0))
    # Closed-back headphones — drape on the desk corner
    make_cyl("Studio_HP_CupL",
             (desk_x - 0.42, desk_y + 0.06, 0.78),
             0.07, 0.05, (0.10, 0.10, 0.12, 1.0), segments=8, axis='Z')
    make_cyl("Studio_HP_CupR",
             (desk_x - 0.28, desk_y + 0.06, 0.78),
             0.07, 0.05, (0.10, 0.10, 0.12, 1.0), segments=8, axis='Z')
    make_cyl("Studio_HP_Band",
             (desk_x - 0.35, desk_y + 0.06, 0.83),
             0.08, 0.18, (0.14, 0.14, 0.18, 1.0), segments=8, axis='X')
    # Coffee cup with cold inch
    make_cyl("Studio_CoffeeCup",
             (desk_x - 0.50, desk_y - 0.20, 0.78),
             0.045, 0.10, COL_TRIM_WHITE, segments=10)
    make_cyl("Studio_CoffeeContents",
             (desk_x - 0.50, desk_y - 0.20, 0.81),
             0.040, 0.02, (0.20, 0.10, 0.06, 1.0), segments=10)
    # Studio acoustic foam panel on the east wall
    make_box("Studio_FoamPanel_1",
             (INTERIOR_X_E - 0.06, STUDIO_CY + 0.7, 1.60),
             (0.04, 1.20, 0.80), (0.30, 0.30, 0.32, 1.0))


# ════════════════════════════════════════════════════════════════
# STATION · THE BOOKSHELF
# Thrift tarot decks (one sticky with wine), mirror shard, framing
# books, hauntology books, doc-turn books, half-eaten cookies.
# ════════════════════════════════════════════════════════════════
BOOK_CX, BOOK_CY = +1.0, +2.6


def build_bookshelf():
    gauntlet_marker("Z_Bookshelf", BOOK_CX, BOOK_CY, 1.5, 0.7, "II")

    # ── Bookshelf — mounted against the studio's west wall (which
    # is the partition between living room and studio)
    sh_x = +1.4   # just west of the studio partition
    sh_y = +2.6
    shelf_h = 1.80
    make_box("Bookshelf_Frame",
             (sh_x, sh_y, shelf_h / 2.0),
             (0.20, 1.50, shelf_h), (0.38, 0.26, 0.18, 1.0))
    # 4 horizontal shelves
    for i in range(4):
        sz = 0.18 + i * 0.45
        make_box(f"Bookshelf_Plate_{i}",
                 (sh_x - 0.02, sh_y, sz),
                 (0.18, 1.48, 0.025), (0.42, 0.30, 0.20, 1.0))

    # Shelf 0 (lowest) — thrift tarot deck boxes (5 colors)
    for i, tint in enumerate(TAROT_TINTS):
        bx_y = sh_y - 0.60 + i * 0.30
        make_box(f"Bookshelf_TarotDeck_{i}",
                 (sh_x - 0.02, bx_y, 0.18 + 0.06),
                 (0.10, 0.13, 0.08), tint)
    # One of them sticky with spilled wine — dark drip mark
    make_box("Bookshelf_TarotDeck_WineStain",
             (sh_x - 0.07, sh_y - 0.30, 0.18 + 0.001),
             (0.07, 0.09, 0.001), (0.32, 0.08, 0.12, 1.0))

    # Shelf 1 — framing books (chunky textbooks)
    shelf_1_z = 0.18 + 1 * 0.45 + 0.13
    book_colors = [COL_BOOK_BLUE, COL_BOOK_RED, COL_BOOK_GREEN,
                   COL_BOOK_BLACK, COL_BOOK_BLUE, COL_BOOK_RED]
    for i, col in enumerate(book_colors):
        bx_y = sh_y - 0.65 + i * 0.22
        make_box(f"Bookshelf_S1_Book_{i}",
                 (sh_x - 0.04, bx_y, shelf_1_z),
                 (0.14, 0.18, 0.26), col)

    # Shelf 2 — hauntology + doc-turn books, leaning sideways
    shelf_2_z = 0.18 + 2 * 0.45 + 0.13
    book_colors_2 = [COL_BOOK_BLACK, COL_BOOK_RED, COL_BOOK_GREEN,
                     COL_BOOK_BLUE, COL_BOOK_BLACK]
    for i, col in enumerate(book_colors_2):
        bx_y = sh_y - 0.50 + i * 0.20
        # Tilt every other one slightly using slightly different
        # heights to suggest a lean
        h = 0.24 if i % 2 == 0 else 0.20
        make_box(f"Bookshelf_S2_Book_{i}",
                 (sh_x - 0.04, bx_y, shelf_2_z),
                 (0.12, 0.16, h), col)
    # A book lying flat across the others (the latest reading)
    make_box("Bookshelf_S2_FlatBook",
             (sh_x - 0.06, sh_y + 0.55, shelf_2_z),
             (0.16, 0.22, 0.04), COL_BOOK_BLUE)

    # Shelf 3 (top) — mirror shard + cookie box
    shelf_3_z = 0.18 + 3 * 0.45 + 0.13
    # Mirror shard — angular, slightly off-axis
    make_box("Bookshelf_MirrorShard",
             (sh_x - 0.06, sh_y - 0.50, shelf_3_z),
             (0.10, 0.14, 0.01), (0.92, 0.94, 0.96, 1.0))
    make_box("Bookshelf_MirrorShard_Frame",
             (sh_x - 0.06, sh_y - 0.50, shelf_3_z + 0.002),
             (0.04, 0.06, 0.012), COL_METAL_STEEL)
    # Half-eaten cookie box ("nice cookies somebody gave you")
    make_box("Bookshelf_CookieBox",
             (sh_x - 0.05, sh_y + 0.20, shelf_3_z + 0.04),
             (0.14, 0.20, 0.08), (0.78, 0.62, 0.34, 1.0))
    make_box("Bookshelf_CookieBox_Lid",
             (sh_x - 0.05, sh_y + 0.10, shelf_3_z + 0.085),
             (0.14, 0.10, 0.004), (0.62, 0.46, 0.22, 1.0))
    # Two visible cookies inside
    for i in range(2):
        make_cyl(f"Bookshelf_Cookie_{i}",
                 (sh_x - 0.05, sh_y + 0.24 + i * 0.04,
                  shelf_3_z + 0.058),
                 0.030, 0.012, (0.78, 0.62, 0.42, 1.0), segments=10)


# ════════════════════════════════════════════════════════════════
# STATION · THE KITCHEN
# Teacup (mother's), basil plant on windowsill (dying), kettle
# that boils to one side (the listing burner).
# ════════════════════════════════════════════════════════════════
KIT_CX, KIT_CY = +2.5, +4.5


def build_kitchen():
    gauntlet_marker("Z_Kitchen", KIT_CX, KIT_CY, 3.6, 2.4, "II")

    # ── Counter along the north wall ──
    counter_y = INTERIOR_Y_N - 0.40
    make_box("Kitchen_Counter",
             (+2.5, counter_y, 0.90),
             (5.00, 0.60, 0.06), COL_TRIM_WHITE)
    # Counter base cabinets
    make_box("Kitchen_BaseCabinet",
             (+2.5, counter_y, 0.42),
             (5.00, 0.55, 0.84), (0.62, 0.46, 0.30, 1.0))
    # Cabinet door splits
    for i in range(-2, 3):
        x = +2.5 + i * 1.0
        make_box(f"Kitchen_CabSeam_{i}",
                 (x, counter_y - 0.28, 0.42),
                 (0.012, 0.01, 0.80), (0.20, 0.14, 0.10, 1.0))
    # Sink — recessed into the counter
    make_box("Kitchen_SinkBasin",
             (+1.6, counter_y - 0.04, 0.84),
             (0.50, 0.36, 0.10), COL_METAL_STEEL)
    make_cyl("Kitchen_Faucet",
             (+1.6, counter_y + 0.16, 1.05),
             0.016, 0.20, COL_METAL_BRASS, segments=8)
    make_box("Kitchen_FaucetHandle",
             (+1.6, counter_y + 0.18, 1.18),
             (0.10, 0.04, 0.04), COL_METAL_BRASS)
    # Stovetop — 4 burners, one listing (slightly off-center)
    make_box("Kitchen_Stove",
             (+3.4, counter_y, 0.95),
             (0.80, 0.55, 0.04), (0.12, 0.12, 0.14, 1.0))
    for i, (bx, by) in enumerate([(+3.2, counter_y - 0.12),
                                   (+3.6, counter_y - 0.12),
                                   (+3.2, counter_y + 0.12),
                                   (+3.6, counter_y + 0.12)]):
        make_cyl(f"Kitchen_Burner_{i}",
                 (bx, by, 0.972),
                 0.10, 0.006, (0.16, 0.14, 0.14, 1.0), segments=10)
    # Kettle — sits on the listing burner (slightly tilted via
    # rotated position rather than mesh rotation)
    kx, ky = +3.6 + 0.04, counter_y + 0.12 - 0.04  # offset = list
    make_cyl("Kitchen_Kettle_Body",
             (kx, ky, 1.05),
             0.10, 0.12, (0.18, 0.18, 0.22, 1.0), segments=10)
    make_cyl("Kitchen_Kettle_Top",
             (kx, ky, 1.135),
             0.08, 0.04, (0.22, 0.22, 0.26, 1.0), segments=10)
    # Spout
    make_cyl("Kitchen_Kettle_Spout",
             (kx + 0.10, ky, 1.10),
             0.020, 0.10, (0.18, 0.18, 0.22, 1.0),
             segments=6, axis='X')

    # ── Refrigerator — east end of counter run
    make_box("Kitchen_Fridge",
             (+4.5, counter_y, 0.95),
             (0.80, 0.65, 1.80), (0.92, 0.90, 0.86, 1.0))
    make_box("Kitchen_Fridge_DoorSeam",
             (+4.5, counter_y - 0.33, 1.10),
             (0.78, 0.01, 0.10), (0.62, 0.58, 0.54, 1.0))
    # Magnets + receipt
    make_box("Kitchen_Fridge_Receipt",
             (+4.5, counter_y - 0.335, 1.20),
             (0.10, 0.001, 0.16), COL_PAPER)
    make_box("Kitchen_Fridge_Magnet1",
             (+4.4, counter_y - 0.335, 1.35),
             (0.04, 0.004, 0.03), COL_BOOK_RED)
    make_box("Kitchen_Fridge_Magnet2",
             (+4.6, counter_y - 0.335, 1.45),
             (0.04, 0.004, 0.03), COL_BOOK_BLUE)

    # ── Upper cabinets ──
    make_box("Kitchen_UpperCab",
             (+2.5, counter_y + 0.04, 1.95),
             (5.00, 0.40, 0.70), (0.78, 0.62, 0.46, 1.0))

    # ── Basil plant on the windowsill (THE one that's dying) ──
    bsl_x = +2.8  # under the kitchen window
    bsl_y = INTERIOR_Y_N - 0.16
    make_cyl("Kitchen_BasilPot",
             (bsl_x, bsl_y, 0.99),
             0.09, 0.10, (0.62, 0.40, 0.30, 1.0), segments=10)
    # Leaves — dying / yellow-green
    for i in range(5):
        ang = i * 1.257
        lx = bsl_x + math.cos(ang) * 0.05
        ly = bsl_y + math.sin(ang) * 0.04
        make_box(f"Kitchen_BasilLeaf_{i}",
                 (lx, ly, 1.10 + i * 0.02),
                 (0.06, 0.06, 0.02), COL_GREEN_DYING)
    # The basil's main stem
    make_cyl("Kitchen_BasilStem",
             (bsl_x, bsl_y, 1.06),
             0.008, 0.16, (0.40, 0.32, 0.16, 1.0), segments=4)

    # ── Mother's teacup — sits on the counter near the sink ──
    # (picked up and put down three times this week)
    tc_x, tc_y = +2.1, counter_y + 0.10
    make_cyl("Kitchen_Teacup_Body",
             (tc_x, tc_y, 0.96),
             0.038, 0.06, (0.95, 0.92, 0.88, 1.0), segments=10)
    # Saucer
    make_cyl("Kitchen_Teacup_Saucer",
             (tc_x, tc_y, 0.932),
             0.064, 0.006, (0.90, 0.86, 0.82, 1.0), segments=12)
    # Handle (cube approx)
    make_box("Kitchen_Teacup_Handle",
             (tc_x + 0.052, tc_y, 0.98),
             (0.010, 0.020, 0.030), (0.95, 0.92, 0.88, 1.0))
    # Steam rising — a few tiny rising boxes
    for i in range(3):
        make_box(f"Kitchen_TeacupSteam_{i}",
                 (tc_x + (i - 1) * 0.02, tc_y, 1.04 + i * 0.04),
                 (0.012, 0.012, 0.015), (0.96, 0.96, 0.96, 0.6))

    # ── Small dining table in the kitchen area
    dt_x, dt_y = +2.5, +3.8
    make_box("Kitchen_DiningTable_Top",
             (dt_x, dt_y, 0.74),
             (1.20, 0.80, 0.04), (0.46, 0.32, 0.20, 1.0))
    for sx in (-1, +1):
        for sy in (-1, +1):
            make_cyl(f"Kitchen_DiningTable_Leg_{sx}_{sy}",
                     (dt_x + sx * 0.50, dt_y + sy * 0.32, 0.37),
                     0.024, 0.74, (0.32, 0.22, 0.14, 1.0))
    # One chair
    for sgn in (-1, +1):
        cy_pos = dt_y + sgn * 0.60
        make_box(f"Kitchen_Chair_{sgn}_Seat",
                 (dt_x, cy_pos, 0.46),
                 (0.42, 0.42, 0.04), (0.46, 0.32, 0.20, 1.0))
        make_box(f"Kitchen_Chair_{sgn}_Back",
                 (dt_x, cy_pos + sgn * 0.20, 0.78),
                 (0.42, 0.04, 0.60), (0.46, 0.32, 0.20, 1.0))
        for sx in (-1, +1):
            for sy in (-1, +1):
                make_cyl(f"Kitchen_Chair_{sgn}_Leg_{sx}_{sy}",
                         (dt_x + sx * 0.17, cy_pos + sy * 0.17, 0.23),
                         0.018, 0.46, (0.32, 0.22, 0.14, 1.0))

    # ── Fire escape ladder up to roof — on the east kitchen wall ──
    fe_x = INTERIOR_X_E - 0.06
    fe_y = +4.5
    make_box("Kitchen_FireEscape_Rail_L",
             (fe_x, fe_y - 0.25, (CEIL_Z + ROOF_Z) / 2.0 + 0.4),
             (0.04, 0.04, 4.00), COL_METAL_BLACK)
    make_box("Kitchen_FireEscape_Rail_R",
             (fe_x, fe_y + 0.25, (CEIL_Z + ROOF_Z) / 2.0 + 0.4),
             (0.04, 0.04, 4.00), COL_METAL_BLACK)
    for i in range(9):
        rz = 0.20 + i * 0.36
        make_box(f"Kitchen_FireEscape_Rung_{i}",
                 (fe_x, fe_y, rz),
                 (0.04, 0.50, 0.025), COL_METAL_BLACK)


# ════════════════════════════════════════════════════════════════
# STATION · THE BEDROOM
# Unmade bed, dresser with face-down picture, laundry pile.
# ════════════════════════════════════════════════════════════════
BED_CX, BED_CY = -3.0, +4.5


def build_bedroom():
    gauntlet_marker("Z_Bedroom", BED_CX, BED_CY, 3.4, 2.4, "II")

    # ── Bed — queen-size, unmade. Headboard against the north wall
    bd_x, bd_y = -3.0, +4.7
    make_box("Bedroom_Bed_Frame",
             (bd_x, bd_y, 0.30),
             (1.50, 2.00, 0.20), (0.36, 0.24, 0.16, 1.0))
    make_box("Bedroom_Bed_Mattress",
             (bd_x, bd_y, 0.50),
             (1.40, 1.95, 0.20), (0.92, 0.86, 0.74, 1.0))
    # Headboard
    make_box("Bedroom_Bed_Headboard",
             (bd_x, bd_y + 1.00, 0.95),
             (1.50, 0.10, 1.00), (0.32, 0.22, 0.14, 1.0))
    # Unmade — duvet bunched, pulled to one side
    make_box("Bedroom_Bed_Duvet_Bunch",
             (bd_x + 0.15, bd_y - 0.20, 0.66),
             (1.20, 1.50, 0.16), COL_FABRIC_SHEET)
    # Pillow askew
    make_box("Bedroom_Bed_Pillow",
             (bd_x - 0.30, bd_y + 0.80, 0.66),
             (0.50, 0.32, 0.10), COL_TRIM_WHITE)

    # ── Dresser — opposite the bed (south part of room)
    dr_x, dr_y = -3.0, +3.4
    make_box("Bedroom_Dresser_Body",
             (dr_x, dr_y, 0.50),
             (1.40, 0.50, 1.00), (0.32, 0.20, 0.14, 1.0))
    # Drawers (3 drawers visible)
    for i in range(3):
        dz = 0.20 + i * 0.30
        make_box(f"Bedroom_Dresser_Drawer_{i}_Front",
                 (dr_x, dr_y - 0.26, dz),
                 (1.32, 0.02, 0.24), (0.40, 0.28, 0.18, 1.0))
        make_box(f"Bedroom_Dresser_Knob_{i}_L",
                 (dr_x - 0.30, dr_y - 0.27, dz),
                 (0.04, 0.02, 0.04), COL_METAL_BRASS)
        make_box(f"Bedroom_Dresser_Knob_{i}_R",
                 (dr_x + 0.30, dr_y - 0.27, dz),
                 (0.04, 0.02, 0.04), COL_METAL_BRASS)
    # The face-down picture
    make_box("Bedroom_Dresser_Picture",
             (dr_x + 0.30, dr_y, 1.005),
             (0.22, 0.16, 0.012), (0.32, 0.22, 0.14, 1.0))
    # Back of frame visible (face down)
    make_box("Bedroom_Dresser_PictureBack",
             (dr_x + 0.30, dr_y, 1.013),
             (0.20, 0.14, 0.002), (0.22, 0.16, 0.10, 1.0))

    # ── Laundry pile (MrMyst's last visit) — corner of the room
    lp_x, lp_y = -4.6, +5.5
    # Several small fabric chunks piled
    for i in range(6):
        ang = i * 1.05
        lx = lp_x + math.cos(ang) * 0.10
        ly = lp_y + math.sin(ang) * 0.08
        h = 0.10 + (i % 3) * 0.05
        tint = [COL_FABRIC_LINEN, COL_FABRIC_SHEET,
                (0.62, 0.32, 0.30, 1.0)][i % 3]
        make_box(f"Bedroom_Laundry_{i}",
                 (lx, ly, 0.05 + i * 0.04),
                 (0.30, 0.24, h), tint)

    # ── Bedside lamp on the dresser
    make_cyl("Bedroom_LampBase",
             (dr_x - 0.40, dr_y, 1.04),
             0.06, 0.04, COL_METAL_BRASS)
    make_cyl("Bedroom_LampPole",
             (dr_x - 0.40, dr_y, 1.16),
             0.012, 0.20, COL_METAL_BRASS)
    make_cyl("Bedroom_LampShade",
             (dr_x - 0.40, dr_y, 1.30),
             0.08, 0.14, (0.86, 0.78, 0.62, 1.0), segments=10)


# ════════════════════════════════════════════════════════════════
# STATION · THE BATHROOM
# Mirror over sink (whole — not the shard), medicine cabinet w/
# expired prescription. Small, west-side off the corridor.
# ════════════════════════════════════════════════════════════════
BATH_CX, BATH_CY = -3.75, +0.75


def build_bathroom():
    gauntlet_marker("Z_Bathroom", BATH_CX, BATH_CY, 1.8, 1.0, "II")

    # ── Sink + vanity (west wall)
    sn_x = INTERIOR_X_W + 0.40
    sn_y = +0.75
    make_box("Bathroom_Vanity",
             (sn_x, sn_y, 0.42),
             (0.60, 1.10, 0.84), (0.92, 0.86, 0.72, 1.0))
    make_box("Bathroom_Counter",
             (sn_x, sn_y, 0.86),
             (0.62, 1.12, 0.04), COL_TRIM_WHITE)
    make_box("Bathroom_SinkBasin",
             (sn_x, sn_y, 0.84),
             (0.40, 0.36, 0.06), COL_TRIM_WHITE)
    make_cyl("Bathroom_Faucet",
             (sn_x + 0.10, sn_y - 0.18, 0.96),
             0.014, 0.16, COL_METAL_BRASS, segments=8)
    # Mirror over sink (the WHOLE one)
    make_box("Bathroom_Mirror",
             (INTERIOR_X_W + 0.06, sn_y, 1.45),
             (0.04, 0.80, 0.70), (0.94, 0.96, 0.98, 1.0))
    make_box("Bathroom_Mirror_Frame",
             (INTERIOR_X_W + 0.062, sn_y, 1.45),
             (0.02, 0.84, 0.74), (0.42, 0.32, 0.20, 1.0))

    # Medicine cabinet (built into the wall behind/above the mirror)
    make_box("Bathroom_MedCab",
             (INTERIOR_X_W + 0.10, sn_y + 0.55, 1.50),
             (0.20, 0.30, 0.60), (0.32, 0.22, 0.14, 1.0))
    # Visible inside — an empty prescription bottle on the shelf
    # (a slightly orange tinted cylinder)
    make_cyl("Bathroom_Rx",
             (INTERIOR_X_W + 0.16, sn_y + 0.55, 1.46),
             0.020, 0.08, (0.78, 0.42, 0.22, 1.0), segments=8)

    # Toilet — south side of bathroom
    tlt_x, tlt_y = -2.95, +0.25
    make_box("Bathroom_Toilet_Tank",
             (tlt_x, tlt_y, 0.84),
             (0.40, 0.20, 0.50), COL_TRIM_WHITE)
    make_box("Bathroom_Toilet_Bowl",
             (tlt_x, tlt_y + 0.30, 0.32),
             (0.40, 0.50, 0.36), COL_TRIM_WHITE)

    # Tub — full east side of bathroom
    tb_x, tb_y = -2.8, +1.10
    make_box("Bathroom_Tub_Body",
             (tb_x, tb_y, 0.30),
             (0.70, 1.20, 0.60), COL_TRIM_WHITE)
    make_box("Bathroom_Tub_Interior",
             (tb_x, tb_y, 0.38),
             (0.55, 1.05, 0.48), (0.84, 0.82, 0.80, 1.0))

    # Towel
    make_box("Bathroom_Towel",
             (sn_x, sn_y + 0.45, 1.10),
             (0.20, 0.30, 0.02), (0.42, 0.62, 0.66, 1.0))


# ════════════════════════════════════════════════════════════════
# STATION · THE STORAGE CLOSET
# 5 boxes of Pomegranate Hour material. Closed since November.
# Behind the studio (south of studio, north of front porch).
# ════════════════════════════════════════════════════════════════
CL_CX, CL_CY = +0.4, +1.5


def build_storage_closet():
    gauntlet_marker("Z_StorageCloset", CL_CX, CL_CY, 1.8, 1.6, "II")

    # ── 5 stacked boxes, dusty, labeled POMEGRANATE HOUR ──
    bx_y = +1.5
    layout = [
        (-0.5, +1.3, 0.45, 0.45, 0.45),
        (+0.0, +1.3, 0.45, 0.45, 0.45),
        (+0.5, +1.3, 0.45, 0.45, 0.45),
        (-0.2, +1.3, 0.45, 0.40, 0.40),   # stacked on row 1
        (+0.3, +1.3, 0.40, 0.40, 0.40),
    ]
    z_offsets = [0.25, 0.25, 0.25, 0.70, 0.70]
    for i, ((px, py, w, d, h), z) in enumerate(zip(layout, z_offsets)):
        make_box(f"Closet_PHBox_{i}",
                 (px, py, z), (w, d, h),
                 (0.62, 0.50, 0.32, 1.0))   # darker than living-room boxes (dust)
        # Tape strip on lid
        make_box(f"Closet_PHBox_{i}_Tape",
                 (px, py, z + h / 2 + 0.001),
                 (0.06, d - 0.10, 0.002), COL_PAPER)
        # Faded label
        make_box(f"Closet_PHBox_{i}_Label",
                 (px - 0.16, py - d / 2 - 0.001, z),
                 (0.20, 0.001, 0.06), COL_PAPER_DARK)
    # A few hard drives stacked on top of the boxes
    for i in range(3):
        make_box(f"Closet_HD_{i}",
                 (+0.2, +1.4, 0.95 + i * 0.04),
                 (0.15, 0.20, 0.03), (0.20, 0.20, 0.22, 1.0))
    # Cassette tapes — a small pile
    for i in range(5):
        make_box(f"Closet_Tape_{i}",
                 (-0.5 + i * 0.08, +1.5, 0.96),
                 (0.07, 0.10, 0.014), (0.18, 0.16, 0.16, 1.0))
    # A disc case — the never-finished pilot episode
    make_box("Closet_DiscCase",
             (+0.0, +1.7, 0.98),
             (0.13, 0.14, 0.014), (0.10, 0.10, 0.12, 1.0))
    make_box("Closet_DiscCase_Label",
             (+0.0, +1.7, 0.988),
             (0.10, 0.10, 0.001), COL_PAPER)

    # Door — slatted, mostly closed (we leave a small visible slit)
    # The east edge of the closet is at X=+1.4; door is at +1.45
    make_box("Closet_Door",
             (+1.40, +1.5, 1.10),
             (0.04, 1.40, 2.20), (0.42, 0.30, 0.20, 1.0))
    # Slats
    for i in range(8):
        sz = 0.30 + i * 0.20
        make_box(f"Closet_Door_Slat_{i}",
                 (+1.38, +1.5, sz),
                 (0.02, 1.30, 0.05), (0.36, 0.24, 0.16, 1.0))


# ════════════════════════════════════════════════════════════════
# STATION · THE PORCH
# 2 wicker chairs (one missing left arm), ashtray, unhung wind
# chime. Front of bungalow, south of front door.
# ════════════════════════════════════════════════════════════════
PORCH_CX, PORCH_CY = 0.0, -1.2


def build_porch():
    # Porch deck
    make_box("Porch_Deck",
             (0.0, -1.2, 0.05),
             (8.0, 2.4, 0.10), (0.42, 0.30, 0.18, 1.0))
    # Porch deck planks
    for i in range(-3, 4):
        x = i * 1.0
        make_box(f"Porch_Plank_{i}",
                 (x, -1.2, 0.105),
                 (0.05, 2.40, 0.01), (0.28, 0.20, 0.12, 1.0))
    # Porch roof (covered porch — supports drop down)
    make_box("Porch_Roof",
             (0.0, -1.2, 2.60),
             (8.4, 2.6, 0.08), COL_WALL_OUTER)
    # Porch roof slope (front edge slightly lower)
    make_box("Porch_Roof_FrontEdge",
             (0.0, -2.40, 2.40),
             (8.6, 0.06, 0.30), (0.42, 0.32, 0.22, 1.0))
    # Porch posts
    for x in (-3.8, +3.8):
        make_box(f"Porch_Post_{int(x*10)}",
                 (x, -2.30, 1.30),
                 (0.16, 0.16, 2.60), COL_DOORFRAME)

    # Gauntlet marker on porch
    gauntlet_marker("Z_Porch", PORCH_CX, PORCH_CY, 2.4, 1.6, "II")

    # ── Two wicker chairs, one missing left arm ──
    # Chair A (west — has both arms)
    ax, ay = -1.6, -1.4
    make_box("Porch_ChairA_Seat",
             (ax, ay, 0.42),
             (0.55, 0.55, 0.06), COL_WICKER)
    make_box("Porch_ChairA_Back",
             (ax, ay + 0.24, 0.82),
             (0.55, 0.06, 0.70), COL_WICKER)
    make_box("Porch_ChairA_ArmL",
             (ax - 0.28, ay, 0.62),
             (0.05, 0.50, 0.30), COL_WICKER)
    make_box("Porch_ChairA_ArmR",
             (ax + 0.28, ay, 0.62),
             (0.05, 0.50, 0.30), COL_WICKER)
    for sx in (-1, +1):
        for sy in (-1, +1):
            make_cyl(f"Porch_ChairA_Leg_{sx}_{sy}",
                     (ax + sx * 0.22, ay + sy * 0.22, 0.21),
                     0.018, 0.42, (0.42, 0.32, 0.20, 1.0))
    # Chair B (east — MISSING LEFT ARM)
    bx, by = +1.4, -1.4
    make_box("Porch_ChairB_Seat",
             (bx, by, 0.42),
             (0.55, 0.55, 0.06), COL_WICKER)
    make_box("Porch_ChairB_Back",
             (bx, by + 0.24, 0.82),
             (0.55, 0.06, 0.70), COL_WICKER)
    # NOTE: only right arm. The flavor's "missing left arm" — the
    # left arm rest is gone (the snapped wicker).
    make_box("Porch_ChairB_ArmR",
             (bx + 0.28, by, 0.62),
             (0.05, 0.50, 0.30), COL_WICKER)
    # A broken stump where the left arm used to be
    make_box("Porch_ChairB_ArmL_Broken",
             (bx - 0.28, by + 0.16, 0.62),
             (0.05, 0.08, 0.10), (0.46, 0.32, 0.20, 1.0))
    for sx in (-1, +1):
        for sy in (-1, +1):
            make_cyl(f"Porch_ChairB_Leg_{sx}_{sy}",
                     (bx + sx * 0.22, by + sy * 0.22, 0.21),
                     0.018, 0.42, (0.42, 0.32, 0.20, 1.0))

    # ── Ashtray on a small side table between the chairs ──
    st_x, st_y = +0.0, -1.4
    make_cyl("Porch_SideTable_Top",
             (st_x, st_y, 0.56),
             0.20, 0.02, (0.32, 0.22, 0.14, 1.0))
    make_cyl("Porch_SideTable_Pedestal",
             (st_x, st_y, 0.28),
             0.05, 0.50, (0.42, 0.30, 0.18, 1.0))
    # Ashtray itself — small glass dish, EMPTY
    make_cyl("Porch_Ashtray",
             (st_x, st_y, 0.58),
             0.08, 0.014, (0.78, 0.82, 0.86, 0.6), segments=10)

    # ── Wind chime — UNHUNG, lying coiled on the porch floor by
    # the east post (the flavor: "have not, in two years, hung")
    wc_x, wc_y = +3.4, -1.8
    make_box("Porch_WindChime_Hub",
             (wc_x, wc_y, 0.12),
             (0.10, 0.10, 0.04), (0.62, 0.46, 0.22, 1.0))
    # Coiled string (folded)
    for i in range(4):
        make_box(f"Porch_WindChime_Pipe_{i}",
                 (wc_x + i * 0.04 - 0.06, wc_y - 0.10, 0.10),
                 (0.02, 0.18, 0.04), COL_METAL_BRASS)


# ════════════════════════════════════════════════════════════════
# STATION · THE BACK YARD
# Dying garden, rosemary (alive), basil bed with tomatoes (against
# canon — second August in a row).
# ════════════════════════════════════════════════════════════════
YARD_CX, YARD_CY = 0.0, +8.0


def build_back_yard():
    # Yard ground
    make_box("Yard_Ground",
             (0.0, +8.0, -0.02),
             (10.0, 4.0, 0.04), (0.36, 0.40, 0.22, 1.0))
    # Patchier dying turf — overlapping darker patches
    for i in range(6):
        ang = i * 1.05
        yx = math.cos(ang) * 3.0
        yy = +7.5 + math.sin(ang) * 1.2
        make_box(f"Yard_PatchDying_{i}",
                 (yx, yy, -0.01),
                 (1.20, 0.80, 0.012), (0.48, 0.44, 0.22, 1.0))
    # Back fence
    make_box("Yard_Fence_N",
             (0.0, +10.0, 0.85),
             (10.0, 0.08, 1.70), (0.62, 0.46, 0.28, 1.0))
    for i in range(-4, 5):
        x = i * 1.0
        make_box(f"Yard_FencePost_{i}",
                 (x, +10.0, 0.85),
                 (0.10, 0.10, 1.80), (0.42, 0.30, 0.18, 1.0))
    # Side fences (east/west)
    for sgn in (-1, +1):
        make_box(f"Yard_Fence_E{sgn:+d}",
                 (sgn * 5.0, +8.0, 0.85),
                 (0.08, 4.0, 1.70), (0.62, 0.46, 0.28, 1.0))

    # Gauntlet marker
    gauntlet_marker("Z_BackYard", YARD_CX, YARD_CY, 3.0, 2.0, "II")

    # ── Rosemary bush (alive, scruffy) ──
    rsm_x, rsm_y = +3.2, +7.6
    for i in range(7):
        ang = i * 0.90
        lx = rsm_x + math.cos(ang) * 0.18
        ly = rsm_y + math.sin(ang) * 0.16
        make_box(f"Yard_Rosemary_Bunch_{i}",
                 (lx, ly, 0.16),
                 (0.18, 0.18, 0.30), COL_GREEN_HERB)
    # Woody stem at center
    make_cyl("Yard_Rosemary_Stem",
             (rsm_x, rsm_y, 0.10),
             0.04, 0.20, (0.32, 0.22, 0.14, 1.0), segments=6)

    # ── Basil bed (against canon, second August in a row,
    # planted tomatoes here too) ──
    # Raised bed frame
    bb_x, bb_y = -2.8, +7.6
    for sgn, axis in [(-1, 'x'), (+1, 'x'), (-1, 'y'), (+1, 'y')]:
        if axis == 'x':
            make_box(f"Yard_BasilBed_Frame_x{sgn:+d}",
                     (bb_x + sgn * 0.80, bb_y, 0.10),
                     (0.05, 1.40, 0.20), (0.42, 0.30, 0.18, 1.0))
        else:
            make_box(f"Yard_BasilBed_Frame_y{sgn:+d}",
                     (bb_x, bb_y + sgn * 0.70, 0.10),
                     (1.65, 0.05, 0.20), (0.42, 0.30, 0.18, 1.0))
    # Soil inside
    make_box("Yard_BasilBed_Soil",
             (bb_x, bb_y, 0.06),
             (1.50, 1.30, 0.10), COL_SOIL)
    # Basil plants (the canon row — yard ones look HEALTHIER than
    # the kitchen one)
    for i in range(4):
        bx2 = bb_x - 0.60 + i * 0.40
        # Tuft of leaves
        for j in range(4):
            ang = j * 1.57
            lx = bx2 + math.cos(ang) * 0.06
            ly = bb_y - 0.25 + math.sin(ang) * 0.05
            make_box(f"Yard_BasilBed_Leaf_{i}_{j}",
                     (lx, ly, 0.20),
                     (0.06, 0.06, 0.04), COL_GREEN_LEAF)
        # Stem
        make_cyl(f"Yard_BasilBed_Stem_{i}",
                 (bx2, bb_y - 0.25, 0.14),
                 0.008, 0.10, (0.30, 0.22, 0.14, 1.0), segments=4)
    # Tomato cage(s) — 2 cages with one fruit each, against canon
    for i in range(2):
        tc_x = bb_x - 0.40 + i * 0.80
        tc_y = bb_y + 0.20
        # 3-ring tomato cage frame
        for ring_z in (0.20, 0.40, 0.60):
            for j in range(6):
                ang = j * 1.047
                px = tc_x + math.cos(ang) * 0.16
                py = tc_y + math.sin(ang) * 0.16
                # Hexagonal vertical posts at this ring
                if ring_z == 0.20:
                    make_cyl(f"Yard_TomatoCage_{i}_Post_{j}",
                             (px, py, 0.40), 0.005, 0.80,
                             COL_METAL_STEEL, segments=4)
            # ring itself
            make_cyl(f"Yard_TomatoCage_{i}_Ring_{ring_z}",
                     (tc_x, tc_y, ring_z), 0.18, 0.01,
                     COL_METAL_STEEL, segments=10)
        # The single tomato — bright red
        make_cyl(f"Yard_Tomato_{i}",
                 (tc_x, tc_y + 0.04, 0.36),
                 0.05, 0.08, COL_TOMATO, segments=10)
        # Plant body — green leaves around the cage
        for j in range(3):
            make_box(f"Yard_TomatoLeaves_{i}_{j}",
                     (tc_x + (j - 1) * 0.10, tc_y, 0.36),
                     (0.10, 0.20, 0.18), COL_GREEN_LEAF)

    # ── Back gate — west end of fence ──
    make_box("Yard_BackGate",
             (-4.4, +10.0, 0.85),
             (0.80, 0.06, 1.50), (0.42, 0.30, 0.18, 1.0))
    make_box("Yard_BackGate_Hinge",
             (-4.04, +10.04, 1.20),
             (0.04, 0.10, 0.08), COL_METAL_BLACK)
    # Sign on gate (the welcome mat counterpart — none here)

    # A single bird-bath in the center of the back yard
    make_cyl("Yard_BirdBath_Base",
             (0.0, +8.5, 0.20),
             0.10, 0.40, (0.62, 0.60, 0.56, 1.0))
    make_cyl("Yard_BirdBath_Bowl",
             (0.0, +8.5, 0.46),
             0.32, 0.04, (0.74, 0.72, 0.66, 1.0), segments=12)
    # Water in the bowl
    make_cyl("Yard_BirdBath_Water",
             (0.0, +8.5, 0.49),
             0.28, 0.01, (0.42, 0.58, 0.66, 0.8), segments=12)


# ════════════════════════════════════════════════════════════════
# THRESHOLDS — front door already built in shell. Roof access.
# ════════════════════════════════════════════════════════════════
def build_roof_features():
    """Mark the ROOF threshold and add a small skylight + chimney
    on the flat roof so the player has things to read up there."""
    gauntlet_marker("Z_Roof", -1.0, +1.0, 2.0, 1.5, "II")
    # Skylight — a glass panel over the kitchen
    make_box("Roof_Skylight_Frame",
             (+2.8, +4.0, ROOF_Z + 0.10),
             (1.00, 1.20, 0.06), COL_METAL_BLACK)
    make_box("Roof_Skylight_Glass",
             (+2.8, +4.0, ROOF_Z + 0.13),
             (0.88, 1.08, 0.02), (0.42, 0.58, 0.74, 0.75))
    # Chimney
    make_box("Roof_Chimney_Body",
             (-3.0, +3.5, ROOF_Z + 0.50),
             (0.50, 0.40, 1.00), (0.48, 0.36, 0.28, 1.0))
    make_box("Roof_Chimney_Cap",
             (-3.0, +3.5, ROOF_Z + 1.04),
             (0.58, 0.48, 0.04), (0.32, 0.24, 0.18, 1.0))
    # Solar panel — small one, dirty (Elicia's '21 install)
    make_box("Roof_SolarPanel",
             (-1.5, +4.0, ROOF_Z + 0.18),
             (1.40, 1.00, 0.04), (0.18, 0.20, 0.30, 1.0))
    # A folding chair Elicia leaves up here (the wide-shot vantage)
    fc_x, fc_y = +1.0, +1.5
    make_box("Roof_FoldChair_Seat",
             (fc_x, fc_y, ROOF_Z + 0.50),
             (0.42, 0.42, 0.04), (0.42, 0.30, 0.18, 1.0))
    make_box("Roof_FoldChair_Back",
             (fc_x, fc_y + 0.20, ROOF_Z + 0.85),
             (0.42, 0.04, 0.66), (0.42, 0.30, 0.18, 1.0))
    for sx in (-1, +1):
        for sy in (-1, +1):
            make_cyl(f"Roof_FoldChair_Leg_{sx}_{sy}",
                     (fc_x + sx * 0.18, fc_y + sy * 0.18,
                      ROOF_Z + 0.25),
                     0.014, 0.50, COL_METAL_BLACK)


# ════════════════════════════════════════════════════════════════
# EXPORT
# ════════════════════════════════════════════════════════════════
def export_glb():
    out_dir = os.path.normpath(
        os.path.join(os.path.dirname(os.path.abspath(__file__)),
                     OUTPUT_DIR))
    os.makedirs(out_dir, exist_ok=True)
    out_path = os.path.join(out_dir, OUTPUT_NAME)

    print(f"\n[build_bungalow] exporting to {out_path}")
    print(f"[build_bungalow] scene objects: "
          f"{len(bpy.context.scene.objects)}")

    bpy.ops.object.select_all(action='SELECT')
    base = {
        'filepath': out_path, 'export_format': 'GLB',
        'use_selection': False, 'export_apply': True,
        'export_lights': False, 'export_cameras': False,
    }
    rna = bpy.ops.export_scene.gltf.get_rna_type()
    legacy = {}
    if 'export_colors' in rna.properties:
        legacy['export_colors'] = True
    if 'export_normals' in rna.properties:
        legacy['export_normals'] = True

    try:
        result = bpy.ops.export_scene.gltf(**base, **legacy)
        print(f"[build_bungalow] export result: {result}")
    except Exception as e:
        print(f"[build_bungalow] ✗ EXPORT FAILED: {e}")
        import traceback
        traceback.print_exc()
        raise

    if os.path.exists(out_path):
        size = os.path.getsize(out_path)
        print(f"[build_bungalow] ✓ wrote {out_path} ({size} bytes)")


def build_priestess_dressing():
    """Scene-description specifics from the Priestess scenarios
    (broken_glass_fractal, packing, the_comforting_void) that the
    generic builders don't cover. Always present in the GLB.

    Adds:
      · The CRT monitor on the editing desk showing Anya (broken_glass:
        "Anya is on the editing screen"). Beige case + dark screen
        + a small face-silhouette on the screen to anchor "Anya".
      · A second smaller monitor next to it showing John's email window
        (broken_glass: "John's email window is open"). Two CRTs side
        by side on the editing desk.
      · The Master Reel — a reel-to-reel tape deck on the editing
        desk (broken_glass / comforting_void: "Master Reel at 2/3").
      · A pager / phone on the desk with a printed text stream (broken_
        glass: "Mackenzie has been on text for an hour").
      · The basil plant getting two visibly-yellow leaves stuck
        on (broken_glass: "two yellow leaves"). Adds two small
        yellow-green box "leaves" to the existing dying-basil
        in the kitchen window.
      · A small wall-mounted PH-tapes label on the storage closet
        door (the_comforting_void: "the PH tapes are pullable from
        this scenario").
    """
    # ── Editing desk location (matches build_studio_and_editing_desk).
    desk_cx = STUDIO_CX + 0.5
    desk_cy = STUDIO_CY - 0.6
    desk_top_z = 0.74

    # ── Two CRT monitors side by side ──
    # Left (the bigger one) — Anya's editing screen
    anya_cx = desk_cx - 0.32
    anya_cy = desk_cy - 0.04
    # Beige case body
    make_box("Priestess_AnyaMonitor_Case",
             (anya_cx, anya_cy, desk_top_z + 0.18),
             (0.38, 0.36, 0.36),
             (0.86, 0.82, 0.74, 1.0))   # period-correct beige
    # Dark glass screen (slightly forward of the case)
    make_box("Priestess_AnyaMonitor_Screen",
             (anya_cx, anya_cy - 0.18, desk_top_z + 0.20),
             (0.30, 0.02, 0.24),
             (0.10, 0.10, 0.12, 1.0))
    # Anya's face — a small silhouette on the screen. A peach-toned
    # oval-ish box for the face + two dark dots for eyes.
    make_box("Priestess_AnyaMonitor_Face",
             (anya_cx, anya_cy - 0.181, desk_top_z + 0.21),
             (0.14, 0.005, 0.16),
             (0.72, 0.60, 0.48, 1.0))
    for sgn in (-1, +1):
        make_box("Priestess_AnyaMonitor_Eye_%+d" % sgn,
                 (anya_cx + sgn * 0.025, anya_cy - 0.182, desk_top_z + 0.24),
                 (0.014, 0.003, 0.014),
                 (0.18, 0.12, 0.10, 1.0))
    # Hint of a microphone pickup at the bottom of the screen
    make_box("Priestess_AnyaMonitor_MicHint",
             (anya_cx, anya_cy - 0.182, desk_top_z + 0.15),
             (0.04, 0.003, 0.014),
             (0.32, 0.28, 0.22, 1.0))

    # Right (the smaller one) — John's email window
    john_cx = desk_cx + 0.28
    john_cy = desk_cy - 0.04
    make_box("Priestess_JohnMonitor_Case",
             (john_cx, john_cy, desk_top_z + 0.14),
             (0.28, 0.28, 0.28),
             (0.86, 0.82, 0.74, 1.0))
    make_box("Priestess_JohnMonitor_Screen",
             (john_cx, john_cy - 0.14, desk_top_z + 0.16),
             (0.22, 0.02, 0.18),
             (0.10, 0.10, 0.12, 1.0))
    # Email window — white panel with two text-line strips
    make_box("Priestess_JohnMonitor_EmailBg",
             (john_cx, john_cy - 0.141, desk_top_z + 0.16),
             (0.18, 0.003, 0.13),
             (0.92, 0.92, 0.88, 1.0))
    for line in range(3):
        make_box("Priestess_JohnMonitor_EmailLine_%d" % line,
                 (john_cx, john_cy - 0.142, desk_top_z + 0.20 - line * 0.025),
                 (0.13, 0.003, 0.006),
                 (0.18, 0.18, 0.18, 1.0))

    # ── The Master Reel — reel-to-reel deck ──
    reel_cx = desk_cx - 0.04
    reel_cy = desk_cy + 0.30
    # Body
    make_box("Priestess_MasterReel_Body",
             (reel_cx, reel_cy, desk_top_z + 0.10),
             (0.46, 0.34, 0.20),
             (0.20, 0.18, 0.16, 1.0))
    # Two reel disks on top
    for sgn in (-1, +1):
        make_cyl("Priestess_MasterReel_Disk_%+d" % sgn,
                 (reel_cx + sgn * 0.14, reel_cy, desk_top_z + 0.22),
                 0.080, 0.020,
                 (0.78, 0.62, 0.42, 1.0),
                 segments=12, axis='Z')
        # Center spindle hub
        make_cyl("Priestess_MasterReel_Hub_%+d" % sgn,
                 (reel_cx + sgn * 0.14, reel_cy, desk_top_z + 0.232),
                 0.018, 0.012, COL_METAL_BLACK,
                 segments=6, axis='Z')
    # Small VU meter on the front face (cream rectangle)
    make_box("Priestess_MasterReel_VU",
             (reel_cx, reel_cy - 0.171, desk_top_z + 0.14),
             (0.12, 0.003, 0.06),
             (0.92, 0.88, 0.78, 1.0))

    # ── Pager + printed text stream (Mackenzie's hour of texts) ──
    pager_x = desk_cx + 0.18
    pager_y = desk_cy + 0.20
    # Pager body (small black brick)
    make_box("Priestess_Pager_Body",
             (pager_x, pager_y, desk_top_z + 0.012),
             (0.06, 0.10, 0.024),
             (0.10, 0.10, 0.12, 1.0))
    # Tiny LCD strip
    make_box("Priestess_Pager_LCD",
             (pager_x, pager_y, desk_top_z + 0.025),
             (0.05, 0.06, 0.002),
             (0.62, 0.86, 0.68, 1.0))   # phosphor-mint LCD
    # Printed text scroll spilling off the desk
    for s in range(4):
        make_box("Priestess_TextScroll_%d" % s,
                 (pager_x - 0.10, pager_y + 0.08 + s * 0.04, desk_top_z + 0.005),
                 (0.10, 0.04, 0.003),
                 (0.94, 0.92, 0.86, 1.0))
        # A thin black text line on each printed strip
        make_box("Priestess_TextScroll_Line_%d" % s,
                 (pager_x - 0.10, pager_y + 0.08 + s * 0.04, desk_top_z + 0.0065),
                 (0.08, 0.03, 0.0005),
                 (0.20, 0.18, 0.16, 1.0))

    # ── Two yellow leaves on the kitchen basil ──
    # The basil's existing geometry uses COL_GREEN_DYING. Two small
    # yellow-tinted boxes stuck on as the canonical "two yellow leaves."
    # The kitchen window where the basil dies — approximate location
    # from comments.
    basil_x = +2.6   # kitchen east-side counter
    basil_y = +1.4   # near the north kitchen window
    basil_z = 0.92   # on the windowsill
    for li, (lx_off, ly_off, lz_off) in enumerate([
        (+0.04, +0.02, +0.18),
        (-0.03, -0.02, +0.14),
    ]):
        make_box("Priestess_BasilYellowLeaf_%d" % li,
                 (basil_x + lx_off, basil_y + ly_off, basil_z + lz_off),
                 (0.05, 0.025, 0.012),
                 (0.86, 0.78, 0.32, 1.0))   # autumn-yellow

    # ── PH tapes label on the storage closet door ──
    # Storage closet has its own builder; this just adds a small
    # masking-tape label on the door so the storage reads as the
    # PH-tape archive.
    closet_door_x = -3.0   # approximate storage closet door location
    closet_door_y = -0.8
    make_box("Priestess_PHTapes_Label",
             (closet_door_x + 0.02, closet_door_y, 1.62),
             (0.005, 0.18, 0.06),
             (0.92, 0.88, 0.72, 1.0))   # cream masking tape
    # Hand-printed letters as a darker streak
    make_box("Priestess_PHTapes_Letters",
             (closet_door_x + 0.022, closet_door_y, 1.62),
             (0.003, 0.14, 0.012),
             (0.22, 0.18, 0.14, 1.0))




def build_packing_dressing():
    """Asset-improvement pass (2026-07-11): the living strip read as
    bare wall + one chair. Adds the mid-move clutter the Priestess
    prose lives in: a braided rug, taped box stacks, framed photos
    leaning face-to-wall, a rolled rug, packing tape on the side
    table, and a floor lamp beside the chair (its glow is an
    OmniLight3D in bungalow.tscn)."""
    cardboard = (0.55, 0.42, 0.26, 1.0)
    tape      = (0.72, 0.62, 0.40, 1.0)
    # Braided rug under the living strip
    make_cyl("LR_Rug", (-1.7, 1.35, 0.008), 0.85, 0.012,
             (0.40, 0.28, 0.22, 1.0), segments=14)
    make_cyl("LR_Rug_Ring", (-1.7, 1.35, 0.015), 0.62, 0.008,
             (0.30, 0.20, 0.18, 1.0), segments=14)
    # Two more box stacks south of the chair (by the front window)
    make_box("LR_Box_6", (-1.55, 0.45, 0.24), (0.48, 0.42, 0.48), cardboard)
    make_box("LR_Box_7", (-1.55, 0.45, 0.66), (0.42, 0.38, 0.36), cardboard)
    make_box("LR_Box_7_Tape", (-1.55, 0.45, 0.845), (0.44, 0.10, 0.012), tape)
    make_box("LR_Box_8", (-2.15, 2.55, 0.21), (0.44, 0.40, 0.42), cardboard)
    # Framed photos leaning face-to-wall (west wall, packed away)
    for i in range(3):
        make_box(f"LR_Frame_{i}", (-2.42 + i * 0.035, 2.30 + i * 0.06, 0.28),
                 (0.03, 0.42 - i * 0.06, 0.55 - i * 0.08),
                 (0.30 + i * 0.05, 0.24 + i * 0.04, 0.18, 1.0))
    # Rolled rug leaning in the SW corner
    make_cyl("LR_RolledRug", (-2.35, 0.32, 0.65), 0.11, 1.3,
             (0.46, 0.34, 0.24, 1.0), segments=8)
    # Packing tape roll + marker on the side table
    make_cyl("LR_TapeRoll", (-2.25, 1.72, 0.67), 0.06, 0.04, tape, segments=8)
    make_box("LR_Marker", (-2.05, 1.85, 0.655), (0.12, 0.03, 0.025),
             (0.12, 0.12, 0.14, 1.0))
    # Floor lamp beside the chair (glow = FloorLampGlow in the tscn)
    make_cyl("LR_FloorLamp_Base", (-2.3, 0.9, 0.02), 0.16, 0.04,
             (0.20, 0.18, 0.16, 1.0), segments=8)
    make_cyl("LR_FloorLamp_Pole", (-2.3, 0.9, 0.75), 0.02, 1.45,
             (0.26, 0.22, 0.18, 1.0), segments=6)
    make_cyl("LR_FloorLamp_Shade", (-2.3, 0.9, 1.58), 0.16, 0.22,
             (0.88, 0.76, 0.52, 1.0), segments=10)


def main():
    clear_scene()
    build_shell()
    build_partitions()
    build_living_room()
    build_studio_and_editing_desk()
    build_bookshelf()
    build_kitchen()
    build_bedroom()
    build_bathroom()
    build_storage_closet()
    build_porch()
    build_back_yard()
    build_roof_features()
    # Scene-description specifics from the Priestess scenarios —
    # Anya's monitor, John's email window, the Master Reel, the
    # pager + Mackenzie's text scroll, the basil's two yellow
    # leaves, PH-tapes label on the storage closet door.
    build_priestess_dressing()
    build_packing_dressing()
    export_glb()


if __name__ == "__main__":
    main()
