"""
build_riverboat_interior.py
══════════════════════════════════════════════════════════════════
VOL 5 · CHAPTER 3 · The Empress · D'Ambrosio's riverboat INTERIOR.

The floating palace of fusion confusion — three decks, two faces.
The upper deck is Dante's helm office (the architect's leaded
window overlooking the dining floor). The main deck is the public
face: dining room, bar, private dining, kitchen, maitre d' stand.
The lower deck is "the empire under the empire" — catering office,
card room, back room, staff locker room, staff exit.

Board has 13 station spaces + 3 thresholds (per
resources/games/locations/riverboat_interior.json):

  Upper deck:
    HELM              Dante's office (desk, bottle cabinet, leaded
                      window, photo of his wife, brass clock)
    OFFICE STAIRCASE  iron stair down to the dining room

  Main deck:
    MAÎTRE D' STAND   reservation book, pencil, 1971 candy dish
    MAIN DINING ROOM  twelve tables, the brunch floor
    PRIVATE DINING    fine-dining partition, twelve covers max
    TABLE 17          corner booth at the deepest window (Quentin
                      Paul's Sunday court)
    SAMMY'S BAR       16 stools, bar back since '83
    THE PASS          plates, heat lamp, ticket spike
    KITCHEN           Hector's two-station line, hollandaise rail,
                      walk-in, dish pit, radio on milk crate

  Lower deck:
    BACK CORRIDOR     time clock, coat rack, bulletin board, schedule
    CATERING OFFICE   desk, phone, eight-year filing cabinet
    THE CARD ROOM     green-felt 5-stud table, regular's chairs
    THE BACK ROOM     high-stakes table — door has no sign
    STAFF LOCKER ROOM lockers (Sammy's nameplate at the end)

  Thresholds:
    SIDE DOOR         river-facing, discreet exit
    STAFF EXIT        back of lower deck, the walkway
    GANGWAY           plank from boat to dock, public way

COORDINATE FRAME (Blender → Godot):
    +X east  → +X
    +Y north → -Z
    +Z up    → +Y
1 unit = 1m. Boat is moored E-W along the river; bow at +Y north.
Hull X ∈ [-6, +6], Y ∈ [-12, +12]. Decks stacked:
    Lower deck floor Z=0,  ceiling Z=+2.4
    Main deck floor  Z=+2.5, ceiling Z=+5.0
    Upper deck floor Z=+5.1, ceiling Z=+7.6

Run:
    blender --background --python build_riverboat_interior.py
    (or ./run_cathedral.sh build_riverboat_interior.py)

Output:
    godot/assets/3d/locales/riverboat_interior.glb
"""

import bpy
import math
import os
import sys

_SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
if _SCRIPT_DIR not in sys.path:
    sys.path.insert(0, _SCRIPT_DIR)

OUTPUT_DIR  = "../../../assets/3d/locales"
OUTPUT_NAME = "riverboat_interior.glb"


# ── Palette ──────────────────────────────────────────────────────
# Sixty-year-old riverboat restaurant: brass + dark wood + worn
# red velvet + Sunday-light through leaded glass.
COL_HULL_OUTER    = (0.86, 0.78, 0.62, 1.0)   # cream clapboard
COL_HULL_TRIM     = (0.62, 0.20, 0.18, 1.0)   # red trim band
COL_DECK_PLANK    = (0.42, 0.30, 0.18, 1.0)   # dark hardwood
COL_DECK_PLANK_LT = (0.52, 0.40, 0.24, 1.0)
COL_WALL_PAPER    = (0.78, 0.66, 0.42, 1.0)   # gold damask
COL_WALL_DARK     = (0.32, 0.20, 0.14, 1.0)   # mahogany wainscot
COL_WALL_RED      = (0.46, 0.18, 0.16, 1.0)   # private dining red
COL_WALL_GREEN    = (0.24, 0.34, 0.26, 1.0)   # card-room felt-adjacent
COL_CEILING       = (0.62, 0.46, 0.26, 1.0)   # stamped tin ceiling
COL_CARPET_RED    = (0.46, 0.14, 0.12, 1.0)
COL_CARPET_DARK   = (0.28, 0.10, 0.10, 1.0)

COL_BRASS         = (0.78, 0.58, 0.22, 1.0)
COL_BRASS_DARK    = (0.52, 0.38, 0.16, 1.0)
COL_STEEL         = (0.62, 0.66, 0.70, 1.0)
COL_BLACK         = (0.14, 0.12, 0.12, 1.0)
COL_WHITE         = (0.94, 0.92, 0.86, 1.0)

COL_VELVET_RED    = (0.62, 0.18, 0.18, 1.0)
COL_LEATHER_OX    = (0.42, 0.26, 0.20, 1.0)
COL_LEATHER_BLACK = (0.18, 0.16, 0.16, 1.0)
COL_LINEN         = (0.94, 0.90, 0.84, 1.0)
COL_FELT_GREEN    = (0.18, 0.40, 0.24, 1.0)

COL_WINDOW_GLASS  = (0.62, 0.78, 0.82, 0.85)
COL_LEADED_GLASS  = (0.72, 0.84, 0.88, 0.85)
COL_BOTTLE_BROWN  = (0.42, 0.22, 0.10, 1.0)
COL_BOTTLE_GREEN  = (0.18, 0.32, 0.20, 1.0)
COL_BOTTLE_CLEAR  = (0.62, 0.74, 0.78, 0.70)
COL_PAPER         = (0.92, 0.88, 0.78, 1.0)
COL_PAPER_AGED    = (0.84, 0.78, 0.66, 1.0)

COL_BRASS_PAINT = (0.62, 0.46, 0.22, 1.0)
COL_NUMERAL     = (0.78, 0.62, 0.30, 1.0)
COL_PLATE       = (0.46, 0.36, 0.20, 1.0)


# ── Geometry helpers ─────────────────────────────────────────────
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
            else:
                verts.append((cx + z_off, cy + a, cz + b))
    faces = []
    for i in range(segments):
        ni = (i + 1) % segments
        faces.append([i, ni, ni + segments, i + segments])
    faces.append(list(reversed(range(segments))))
    faces.append(list(range(segments, segments * 2)))
    return _finalize_mesh(name, verts, faces, base_color)


# ── Gauntlet station marker ──────────────────────────────────────
def gauntlet_marker(label, cx, cy, cz, w, d, numeral):
    """Brass-stencil rectangle painted onto the deck at height cz +
    a small numeral plate. Same style as cathedral + bungalow."""
    z = cz + 0.013
    for sgn in (-1, +1):
        make_box(f"{label}_outline_x{sgn:+d}",
                 (cx + sgn * w / 2, cy, z),
                 (0.06, d, 0.004), COL_BRASS_PAINT)
        make_box(f"{label}_outline_y{sgn:+d}",
                 (cx, cy + sgn * d / 2, z),
                 (w, 0.06, 0.004), COL_BRASS_PAINT)
    make_box(f"{label}_plate",
             (cx, cy - d / 2 + 0.18, z + 0.001),
             (0.42, 0.14, 0.003), COL_PLATE)
    make_box(f"{label}_numeral",
             (cx, cy - d / 2 + 0.18, z + 0.002),
             (0.30, 0.09, 0.002), COL_NUMERAL)


# ════════════════════════════════════════════════════════════════
# DECK ELEVATIONS
# ════════════════════════════════════════════════════════════════
LOWER_FLOOR_Z = 0.00
LOWER_CEIL_Z  = 2.40
MAIN_FLOOR_Z  = 2.50
MAIN_CEIL_Z   = 5.00
UPPER_FLOOR_Z = 5.10
UPPER_CEIL_Z  = 7.60

HULL_X_W = -6.0
HULL_X_E = +6.0
HULL_Y_S = -12.0
HULL_Y_N = +12.0


# ════════════════════════════════════════════════════════════════
# HULL + DECKS
# ════════════════════════════════════════════════════════════════
def build_hull_and_decks():
    """Outer hull walls + the three deck slabs + stamped tin
    ceilings. The hull is a simple rectangular box, not the
    riverboat shape from build_riverfront (that's the EXTERIOR
    GLB; this is the inside view)."""
    # Hull outer walls — clapboard cream, run the full height
    full_h = UPPER_CEIL_Z
    # E + W walls
    for sgn, xpos in [(-1, HULL_X_W), (+1, HULL_X_E)]:
        make_box(f"Hull_Wall_X{sgn:+d}",
                 (xpos, 0.0, full_h / 2.0),
                 (0.20, 24.0, full_h), COL_HULL_OUTER)
    # N + S walls
    for sgn, ypos in [(-1, HULL_Y_S), (+1, HULL_Y_N)]:
        make_box(f"Hull_Wall_Y{sgn:+d}",
                 (0.0, ypos, full_h / 2.0),
                 (12.4, 0.20, full_h), COL_HULL_OUTER)
    # Red trim band on the hull exterior at each deck waterline
    for z in (MAIN_FLOOR_Z, UPPER_FLOOR_Z):
        for sgn, xpos in [(-1, HULL_X_W), (+1, HULL_X_E)]:
            make_box(f"Hull_TrimX{sgn:+d}_Z{int(z*10)}",
                     (xpos + sgn * 0.11, 0.0, z),
                     (0.04, 24.2, 0.16), COL_HULL_TRIM)
        for sgn, ypos in [(-1, HULL_Y_S), (+1, HULL_Y_N)]:
            make_box(f"Hull_TrimY{sgn:+d}_Z{int(z*10)}",
                     (0.0, ypos + sgn * 0.11, z),
                     (12.4, 0.04, 0.16), COL_HULL_TRIM)

    # Deck slabs — lower, main, upper
    for label, zf, color in [
        ("LowerFloor", LOWER_FLOOR_Z,  COL_DECK_PLANK_LT),
        ("MainFloor",  MAIN_FLOOR_Z,   COL_DECK_PLANK),
        ("UpperFloor", UPPER_FLOOR_Z,  COL_DECK_PLANK_LT),
    ]:
        make_box(f"Hull_{label}",
                 (0.0, 0.0, zf - 0.05),
                 (12.0, 24.0, 0.10), color)
        # Plank seams (running E-W)
        for i in range(-5, 6):
            y = i * 2.0
            make_box(f"Hull_{label}_Seam_{i}",
                     (0.0, y, zf + 0.012),
                     (12.0, 0.01, 0.001),
                     (0.20, 0.14, 0.08, 1.0))

    # Stamped-tin ceilings (visible under each upper floor)
    for label, zc in [
        ("LowerCeil", LOWER_CEIL_Z),
        ("MainCeil",  MAIN_CEIL_Z),
        ("UpperCeil", UPPER_CEIL_Z),
    ]:
        make_box(f"Hull_{label}",
                 (0.0, 0.0, zc + 0.05),
                 (12.0, 24.0, 0.10), COL_CEILING)
        # Tin stamp pattern (subtle raised tiles)
        for i in range(-2, 3):
            for j in range(-5, 6):
                make_box(f"Hull_{label}_Tile_{i}_{j}",
                         (i * 1.6, j * 1.6, zc + 0.02),
                         (1.40, 1.40, 0.005),
                         (0.74, 0.56, 0.30, 1.0))


# ════════════════════════════════════════════════════════════════
# MAIN-DECK PARTITIONS
# ════════════════════════════════════════════════════════════════
#
# Looking down at MAIN deck (Z=2.5–5.0):
#
#   Y=+12 ┌──────────────────────┐
#         │                      │
#         │   KITCHEN            │  Y=+6 to +12
#         │                      │
#         ├──── THE PASS ────────┤  Y=+5.5 (counter)
#         │ PRIVATE   │          │
#         │ DINING    │          │  Y=+1 to +5
#         │           │ SAMMY'S  │
#         ├───────────┤  BAR     │
#         │           │ (east    │
#         │ MAIN      │  wall)   │  Y=-6 to +1
#         │ DINING    │          │
#         │ + TABLE17 │          │
#         │ (NW)      │          │
#         ├───────────┴──────────┤  Y=-7
#         │  MAITRE D' STAND     │  Y=-9
#         │  + STAIRS DOWN/UP    │
#         │  (gangway south)     │
#   Y=-12 └──────────────────────┘
#
def build_main_deck_partitions():
    # Wall between Sammy's bar (east half) and dining (west half),
    # running N-S at X=+2, from Y=-7 to Y=+5 (door at Y=-2)
    make_box("MD_Wall_Bar_S", (+2.0, -4.5, MAIN_FLOOR_Z + 1.3),
             (0.20, 5.0, 2.50), COL_WALL_DARK)
    make_box("MD_Wall_Bar_N", (+2.0, +2.5, MAIN_FLOOR_Z + 1.3),
             (0.20, 5.0, 2.50), COL_WALL_DARK)
    # Header above the doorway
    make_box("MD_Wall_Bar_Above", (+2.0, -2.0, MAIN_FLOOR_Z + 2.30),
             (0.20, 2.0, 0.50), COL_WALL_DARK)

    # Wall between private dining (west of partition) and main
    # dining at Y=+1, X=-6 to +2
    make_box("MD_Wall_PD_W", (-4.0, +1.0, MAIN_FLOOR_Z + 1.3),
             (4.0, 0.20, 2.50), COL_WALL_RED)
    # Header above an arched opening (passes through)
    make_box("MD_Wall_PD_E_Above", (-1.5, +1.0, MAIN_FLOOR_Z + 2.30),
             (1.0, 0.20, 0.50), COL_WALL_RED)
    make_box("MD_Wall_PD_E", (-0.5, +1.0, MAIN_FLOOR_Z + 1.3),
             (1.0, 0.20, 2.50), COL_WALL_RED)

    # Pass wall — between kitchen (Y=+5.5 to +12) and main dining
    # Bar is east, so the pass is the cutout in this wall at +0 to +2
    make_box("MD_Wall_Pass_W", (-3.5, +5.5, MAIN_FLOOR_Z + 1.3),
             (5.0, 0.20, 2.50), COL_WALL_DARK)
    make_box("MD_Wall_Pass_E", (+4.5, +5.5, MAIN_FLOOR_Z + 1.3),
             (3.0, 0.20, 2.50), COL_WALL_DARK)
    # The pass itself — open at counter height; we build a counter
    make_box("MD_Pass_Counter", (+1.5, +5.5, MAIN_FLOOR_Z + 1.05),
             (2.0, 0.20, 0.10), COL_STEEL)
    # Header above the pass opening
    make_box("MD_Pass_Above", (+1.5, +5.5, MAIN_FLOOR_Z + 2.30),
             (2.0, 0.20, 0.50), COL_WALL_DARK)

    # Wall between maitre d' / vestibule (Y=-7 to -12) and main
    # dining (Y > -7). Maitre d' stand wall at Y=-7
    make_box("MD_Wall_MaitreD_W", (-4.0, -7.0, MAIN_FLOOR_Z + 1.3),
             (4.0, 0.20, 2.50), COL_WALL_PAPER)
    make_box("MD_Wall_MaitreD_E", (+4.0, -7.0, MAIN_FLOOR_Z + 1.3),
             (4.0, 0.20, 2.50), COL_WALL_PAPER)
    # Center opening — the entryway

    # Carpet on the main dining floor (red — the boat's livery)
    make_box("MD_Carpet_Dining",
             (-1.0, -3.0, MAIN_FLOOR_Z + 0.014),
             (10.0, 8.0, 0.008), COL_CARPET_RED)
    make_box("MD_Carpet_PrivateDining",
             (-4.0, +3.0, MAIN_FLOOR_Z + 0.014),
             (3.0, 4.0, 0.008), COL_CARPET_DARK)


# ════════════════════════════════════════════════════════════════
# STATION · MAÎTRE D' STAND
# Reservation book, pencil with worn eraser, 1971 candy dish.
# ════════════════════════════════════════════════════════════════
def build_maitre_d():
    cx, cy, cz = 0.0, -8.5, MAIN_FLOOR_Z
    gauntlet_marker("Z_MaitreD", cx, cy, cz, 2.4, 1.8, "III")

    # The stand — tall lectern style, walnut-look
    make_box("MaitreD_Stand_Body",
             (cx, cy, cz + 0.62),
             (1.20, 0.50, 1.24), COL_WALL_DARK)
    make_box("MaitreD_Stand_Top",
             (cx, cy, cz + 1.28),
             (1.30, 0.60, 0.06), COL_DECK_PLANK)
    # Reservation book on top
    make_box("MaitreD_ResBook",
             (cx - 0.30, cy, cz + 1.32),
             (0.32, 0.42, 0.04), COL_LEATHER_OX)
    # Open page (a paper sheet)
    make_box("MaitreD_ResBook_Page",
             (cx - 0.30, cy - 0.05, cz + 1.346),
             (0.28, 0.34, 0.002), COL_PAPER_AGED)
    # Pencil — short stub
    make_cyl("MaitreD_Pencil",
             (cx + 0.05, cy + 0.12, cz + 1.345),
             0.008, 0.16,
             (0.78, 0.62, 0.30, 1.0), segments=6, axis='X')
    # 1971 candy dish — vintage cut crystal, half full
    make_cyl("MaitreD_CandyDish",
             (cx + 0.40, cy, cz + 1.32),
             0.10, 0.04, (0.84, 0.92, 0.96, 0.7), segments=12)
    # Candies inside (assorted)
    for i, tint in enumerate([(0.96, 0.32, 0.32, 1.0),
                              (0.32, 0.78, 0.62, 1.0),
                              (0.96, 0.84, 0.32, 1.0),
                              (0.62, 0.42, 0.84, 1.0)]):
        ang = i * 1.57
        make_box(f"MaitreD_Candy_{i}",
                 (cx + 0.40 + math.cos(ang) * 0.04,
                  cy + math.sin(ang) * 0.04, cz + 1.35),
                 (0.022, 0.022, 0.012), tint)
    # Brass clock on the wall behind the stand
    make_cyl("MaitreD_Wallclock",
             (cx, cy - 0.40, cz + 2.10),
             0.16, 0.04, COL_BRASS, segments=12, axis='Y')

    # ── Stairs UP to helm (the office staircase station marker
    # also goes here — combined entry zone)
    # An iron spiral stair just east of the maitre d'
    stair_x, stair_y = +3.5, -9.5
    # Spiral central post
    make_cyl("MD_StairsUp_Post",
             (stair_x, stair_y, cz + 1.3),
             0.10, 2.60, COL_BLACK)
    # Treads — winding upward
    for i in range(10):
        ang = i * 0.6
        tx = stair_x + math.cos(ang) * 0.70
        ty = stair_y + math.sin(ang) * 0.70
        tz = cz + 0.06 + i * 0.26
        make_box(f"MD_StairsUp_Tread_{i}",
                 (tx, ty, tz),
                 (0.50, 0.50, 0.04), COL_DECK_PLANK)
    # Iron railing
    make_cyl("MD_StairsUp_Rail",
             (stair_x + 0.65, stair_y + 0.20, cz + 1.4),
             0.025, 2.30, COL_BLACK)

    # ── Stairs DOWN to lower deck (catering office etc.) ──
    # Behind the maitre d' wall, a stair down at west side
    sdx, sdy = -4.5, -9.5
    make_box("MD_StairsDown_Opening",
             (sdx, sdy, cz - 0.05),
             (1.20, 2.40, 0.02), (0.10, 0.08, 0.06, 1.0))
    for i in range(8):
        # Linear straight stair going north as you descend
        tx = sdx
        ty = sdy + i * 0.30
        tz = cz - i * 0.30 - 0.05
        make_box(f"MD_StairsDown_Tread_{i}",
                 (tx, ty, tz),
                 (1.10, 0.32, 0.04), COL_DECK_PLANK)
    # Railing
    for sgn in (-1, +1):
        make_box(f"MD_StairsDown_Rail_X{sgn:+d}",
                 (sdx + sgn * 0.50, sdy + 0.90, cz - 0.50),
                 (0.04, 2.20, 0.04), COL_BRASS_DARK)


# ════════════════════════════════════════════════════════════════
# STATION · MAIN DINING ROOM (12 tables, brunch floor)
# ════════════════════════════════════════════════════════════════
def build_main_dining():
    gauntlet_marker("Z_MainDining", -1.0, -3.0, MAIN_FLOOR_Z, 3.6, 2.4, "III")

    # 12 tables in a 4 × 3 grid, with chairs
    table_positions = []
    for j in range(3):
        for i in range(4):
            tx = -4.0 + i * 2.0
            ty = -5.5 + j * 2.0
            # Skip the NW corner — that's where Table 17 lives
            # (NW = (-4, -1.5))
            if (i, j) == (0, 2):
                continue
            table_positions.append((tx, ty, f"T_{i}_{j}"))

    for tx, ty, label in table_positions:
        cz = MAIN_FLOOR_Z + 0.78
        # Top
        make_cyl(f"MD_Dining_{label}_Top",
                 (tx, ty, cz),
                 0.55, 0.04, COL_LINEN, segments=10)
        # Pedestal
        make_cyl(f"MD_Dining_{label}_Pedestal",
                 (tx, ty, cz - 0.39),
                 0.06, 0.74, COL_DECK_PLANK)
        # Base
        make_cyl(f"MD_Dining_{label}_Base",
                 (tx, ty, cz - 0.75),
                 0.30, 0.04, COL_DECK_PLANK, segments=10)
        # Two chairs flanking each table
        for sgn in (-1, +1):
            cy_pos = ty + sgn * 0.80
            make_box(f"MD_Dining_{label}_Chair_{sgn}_Seat",
                     (tx, cy_pos, MAIN_FLOOR_Z + 0.46),
                     (0.42, 0.42, 0.04), COL_VELVET_RED)
            make_box(f"MD_Dining_{label}_Chair_{sgn}_Back",
                     (tx, cy_pos + sgn * 0.20, MAIN_FLOOR_Z + 0.82),
                     (0.42, 0.04, 0.70), COL_WALL_DARK)
            for sx in (-1, +1):
                for sy in (-1, +1):
                    make_cyl(
                        f"MD_Dining_{label}_Chair_{sgn}_Leg_{sx}_{sy}",
                        (tx + sx * 0.17,
                         cy_pos + sy * 0.17,
                         MAIN_FLOOR_Z + 0.23),
                        0.018, 0.46, COL_WALL_DARK)
        # A wineglass on each table (the brunch crowd)
        make_cyl(f"MD_Dining_{label}_Wineglass",
                 (tx + 0.10, ty, MAIN_FLOOR_Z + 0.90),
                 0.04, 0.18,
                 (0.86, 0.92, 0.94, 0.4), segments=10)

    # Two crystal chandeliers down the center axis
    for j, cy_pos in enumerate([-4.5, -1.5]):
        cx = 0.0
        make_cyl(f"MD_Chandelier_{j}_Core",
                 (cx, cy_pos, MAIN_CEIL_Z - 0.50),
                 0.16, 0.40, COL_BRASS)
        # Hanging crystals
        for i in range(8):
            ang = i * (math.pi / 4)
            crx = cx + math.cos(ang) * 0.36
            cry = cy_pos + math.sin(ang) * 0.36
            make_cyl(f"MD_Chandelier_{j}_Crystal_{i}",
                     (crx, cry, MAIN_CEIL_Z - 0.65),
                     0.025, 0.16,
                     (0.96, 0.96, 0.98, 0.7), segments=6)

    # Side door — river-facing, on the EAST wall behind the bar
    # area. We just paint a door visible on the east wall.
    # (Bar is at X=+2 to +6; east wall at +6)
    make_box("MD_SideDoor",
             (HULL_X_E - 0.06, -3.0, MAIN_FLOOR_Z + 1.05),
             (0.04, 1.20, 2.10), COL_WALL_DARK)
    make_box("MD_SideDoor_Knob",
             (HULL_X_E - 0.08, -3.0 + 0.50, MAIN_FLOOR_Z + 1.05),
             (0.04, 0.04, 0.04), COL_BRASS)
    # Side door frame
    make_box("MD_SideDoor_FrameT",
             (HULL_X_E - 0.06, -3.0, MAIN_FLOOR_Z + 2.16),
             (0.04, 1.30, 0.10), COL_BRASS_DARK)


# ════════════════════════════════════════════════════════════════
# STATION · TABLE 17
# Corner booth at the deepest window — Quentin Paul's Sunday court
# ════════════════════════════════════════════════════════════════
def build_table_17():
    cx, cy = -4.5, -1.5
    cz = MAIN_FLOOR_Z
    gauntlet_marker("Z_Table17", cx, cy, cz, 2.0, 2.0, "III")

    # Corner booth — L-shaped bench backed against the west and
    # north walls. The "deepest window" is at the NW corner.
    # Bench against west wall (Y-running)
    make_box("T17_BenchW_Seat",
             (-5.6, -1.5, cz + 0.46),
             (0.50, 1.80, 0.10), COL_VELVET_RED)
    make_box("T17_BenchW_Back",
             (-5.85, -1.5, cz + 1.0),
             (0.10, 1.80, 1.10), COL_WALL_DARK)
    # Bench against north wall (X-running)
    make_box("T17_BenchN_Seat",
             (-4.5, +0.5, cz + 0.46),
             (1.80, 0.50, 0.10), COL_VELVET_RED)
    make_box("T17_BenchN_Back",
             (-4.5, +0.85, cz + 1.0),
             (1.80, 0.10, 1.10), COL_WALL_DARK)
    # The table
    make_box("T17_Table_Top",
             (-4.5, -0.7, cz + 0.78),
             (1.00, 1.20, 0.04), COL_LINEN)
    make_cyl("T17_Table_Pedestal",
             (-4.5, -0.7, cz + 0.39),
             0.08, 0.74, COL_DECK_PLANK)
    # Tablecloth bunched at one corner
    make_box("T17_Tablecloth",
             (-4.50, -0.40, cz + 0.81),
             (0.80, 0.60, 0.004), COL_LINEN)
    # Brass tableside lamp (the boat detail Dante never cheaped on)
    make_cyl("T17_Lamp_Base",
             (-4.0, -1.0, cz + 0.85),
             0.05, 0.06, COL_BRASS)
    make_cyl("T17_Lamp_Pole",
             (-4.0, -1.0, cz + 0.96),
             0.012, 0.18, COL_BRASS)
    make_cyl("T17_Lamp_Shade",
             (-4.0, -1.0, cz + 1.16),
             0.10, 0.14,
             (0.92, 0.78, 0.46, 1.0), segments=10)
    # Window — the "deepest window" overlooking the muddy divide
    make_box("T17_DeepWindow",
             (HULL_X_W + 0.06, -0.5, cz + 1.6),
             (0.04, 1.40, 1.30), COL_LEADED_GLASS)
    # Leaded-glass lattice (vertical mullions)
    for i in range(3):
        my = -0.5 - 0.55 + i * 0.55
        make_box(f"T17_DeepWindow_MullV_{i}",
                 (HULL_X_W + 0.063, my, cz + 1.6),
                 (0.02, 0.04, 1.30), COL_BRASS_DARK)
    # Horizontal mullion
    make_box("T17_DeepWindow_MullH",
             (HULL_X_W + 0.063, -0.5, cz + 1.6),
             (0.02, 1.40, 0.04), COL_BRASS_DARK)
    # Window frame
    make_box("T17_DeepWindow_FrameT",
             (HULL_X_W + 0.062, -0.5, cz + 2.26),
             (0.02, 1.50, 0.06), COL_WALL_DARK)


# ════════════════════════════════════════════════════════════════
# STATION · SAMMY'S BAR
# 16 stools, bar back, brass rail, the boat's bar
# ════════════════════════════════════════════════════════════════
def build_sammys_bar():
    cx, cy = +4.5, 0.0
    cz = MAIN_FLOOR_Z
    gauntlet_marker("Z_SammysBar", cx, cy, cz, 2.4, 6.0, "III")

    # Bar counter — runs north-south along east wall, length ~10m
    bar_x, bar_y, bar_zh = +4.5, 0.0, 1.10
    make_box("Bar_Counter",
             (bar_x, bar_y, cz + bar_zh),
             (0.70, 10.0, 0.10), COL_DECK_PLANK)
    # Brass foot rail
    make_cyl("Bar_FootRail",
             (bar_x - 0.40, bar_y, cz + 0.20),
             0.025, 9.80, COL_BRASS, segments=8, axis='Y')
    # Bar front panel
    make_box("Bar_Front",
             (bar_x - 0.40, bar_y, cz + 0.58),
             (0.05, 9.80, 1.04), COL_WALL_DARK)
    # 16 stools
    for i in range(16):
        sy = -4.7 + i * 0.62
        make_cyl(f"Bar_Stool_{i}_Seat",
                 (bar_x - 0.95, sy, cz + 0.66),
                 0.18, 0.04, COL_LEATHER_OX, segments=10)
        make_cyl(f"Bar_Stool_{i}_Post",
                 (bar_x - 0.95, sy, cz + 0.33),
                 0.04, 0.62, COL_BRASS)
        make_cyl(f"Bar_Stool_{i}_Base",
                 (bar_x - 0.95, sy, cz + 0.02),
                 0.20, 0.04, COL_BRASS, segments=8)
    # Back-bar shelving against east wall
    bb_x = HULL_X_E - 0.40
    make_box("Bar_BackBar_Body",
             (bb_x, bar_y, cz + 1.6),
             (0.40, 9.0, 2.20), COL_WALL_DARK)
    # Mirror across the back bar
    make_box("Bar_BackBar_Mirror",
             (bb_x - 0.21, bar_y, cz + 1.6),
             (0.02, 8.4, 1.50),
             (0.92, 0.94, 0.96, 1.0))
    # Liquor bottles across 3 shelves
    for sh in range(3):
        shz = cz + 1.10 + sh * 0.42
        # Shelf plank
        make_box(f"Bar_BackBar_Shelf_{sh}",
                 (bb_x - 0.16, bar_y, shz - 0.02),
                 (0.20, 8.0, 0.02), COL_DECK_PLANK)
        # Bottles — 20 per shelf, alternating colors
        for b in range(20):
            by_pos = bar_y - 4.0 + b * 0.42
            col = [COL_BOTTLE_BROWN, COL_BOTTLE_GREEN,
                   COL_BOTTLE_CLEAR][b % 3]
            make_cyl(f"Bar_Bottle_{sh}_{b}",
                     (bb_x - 0.10, by_pos, shz + 0.14),
                     0.04, 0.30, col, segments=6)
            # Cap
            make_cyl(f"Bar_BottleCap_{sh}_{b}",
                     (bb_x - 0.10, by_pos, shz + 0.31),
                     0.025, 0.04, COL_BRASS_DARK, segments=6)
    # Tap handle row at the counter's south end
    for i in range(5):
        tx = bar_x + 0.10
        ty = bar_y - 4.5 + i * 0.30
        make_cyl(f"Bar_Tap_{i}_Tower",
                 (tx, ty, cz + bar_zh + 0.06),
                 0.030, 0.16, COL_BRASS, segments=8)
        make_box(f"Bar_Tap_{i}_Handle",
                 (tx, ty, cz + bar_zh + 0.32),
                 (0.04, 0.18, 0.10),
                 [(0.78, 0.16, 0.16, 1.0),
                  (0.16, 0.42, 0.62, 1.0),
                  (0.42, 0.30, 0.18, 1.0)][i % 3])
    # Cash register — central
    make_box("Bar_Register_Body",
             (bb_x - 0.10, bar_y + 3.0, cz + 1.32),
             (0.30, 0.40, 0.40),
             (0.30, 0.20, 0.14, 1.0))
    make_box("Bar_Register_Drawer",
             (bb_x - 0.05, bar_y + 3.0, cz + 1.18),
             (0.36, 0.50, 0.10), COL_DECK_PLANK)


# ════════════════════════════════════════════════════════════════
# STATION · THE PASS
# Plates handed through, heat lamp, ticket spike
# ════════════════════════════════════════════════════════════════
def build_the_pass():
    cx, cy = +1.5, +5.5
    cz = MAIN_FLOOR_Z
    gauntlet_marker("Z_ThePass", cx, cy, cz, 2.0, 1.0, "III")

    # Heat lamp above the pass (already have pass counter from
    # partitions; we add the LAMP + ticket spike + plates)
    make_box("Pass_HeatLamp_Mount",
             (cx, cy, cz + 2.20),
             (1.40, 0.10, 0.10), COL_BLACK)
    for i, dx in enumerate([-0.5, 0.0, +0.5]):
        make_cyl(f"Pass_HeatLamp_{i}_Bulb",
                 (cx + dx, cy, cz + 2.10),
                 0.06, 0.10, (1.00, 0.62, 0.32, 1.0),
                 segments=8, axis='Z')
        make_cyl(f"Pass_HeatLamp_{i}_Shade",
                 (cx + dx, cy, cz + 2.18),
                 0.10, 0.08, (0.42, 0.30, 0.20, 1.0),
                 segments=8, axis='Z')
    # Ticket spike on the pass counter
    make_cyl("Pass_TicketSpike_Base",
             (cx - 0.80, cy - 0.04, cz + 1.16),
             0.04, 0.04, COL_BRASS)
    make_cyl("Pass_TicketSpike_Pin",
             (cx - 0.80, cy - 0.04, cz + 1.26),
             0.006, 0.20, COL_STEEL)
    # Stacked dinner tickets impaled
    for i in range(8):
        make_box(f"Pass_Ticket_{i}",
                 (cx - 0.80, cy - 0.04, cz + 1.18 + i * 0.014),
                 (0.10, 0.14, 0.004), COL_PAPER)
    # Plates on the pass — 3 plates ready to go
    for i, dx in enumerate([-0.3, +0.0, +0.3]):
        make_cyl(f"Pass_Plate_{i}",
                 (cx + dx, cy, cz + 1.16),
                 0.14, 0.02, COL_WHITE, segments=12)
        # Food blob — abstract earth color
        make_cyl(f"Pass_PlateFood_{i}",
                 (cx + dx, cy - 0.02, cz + 1.18),
                 0.10, 0.018,
                 [(0.78, 0.62, 0.32, 1.0),
                  (0.42, 0.20, 0.14, 1.0),
                  (0.86, 0.78, 0.42, 1.0)][i % 3], segments=8)


# ════════════════════════════════════════════════════════════════
# STATION · KITCHEN
# Hector's two-station line, dish pit, walk-in, milk-crate radio
# ════════════════════════════════════════════════════════════════
def build_kitchen():
    cx, cy = 0.0, +9.0
    cz = MAIN_FLOOR_Z
    gauntlet_marker("Z_Kitchen", cx, cy, cz, 4.0, 2.4, "III")

    # Stainless line — two stations, run E-W along Y=+8
    line_y = +8.0
    make_box("Kit_Line",
             (0.0, line_y, cz + 0.50),
             (8.0, 0.80, 0.90), COL_STEEL)
    make_box("Kit_LineTop",
             (0.0, line_y, cz + 0.97),
             (8.0, 0.84, 0.04), COL_STEEL)
    # Two flat-top burner sections
    for sx, station in [(-1.5, "Left"), (+1.5, "Right")]:
        make_box(f"Kit_FlatTop_{station}",
                 (sx, line_y, cz + 0.99),
                 (2.0, 0.50, 0.02), (0.18, 0.18, 0.20, 1.0))
        # Visible heating grid
        for i in range(-2, 3):
            make_box(f"Kit_FlatTop_{station}_Grid_{i}",
                     (sx + i * 0.36, line_y, cz + 1.00),
                     (0.04, 0.40, 0.005),
                     (0.32, 0.20, 0.10, 1.0))
    # Hood vent over the line
    make_box("Kit_Hood",
             (0.0, line_y - 0.30, cz + 2.30),
             (8.4, 1.40, 0.50), COL_STEEL)
    make_box("Kit_Hood_Trim",
             (0.0, line_y - 0.95, cz + 2.10),
             (8.4, 0.04, 0.20), COL_BRASS_DARK)
    # Cutting board on the line
    make_box("Kit_CuttingBoard",
             (0.5, line_y + 0.20, cz + 1.00),
             (0.50, 0.30, 0.04), COL_DECK_PLANK_LT)
    # Stand mixer (the hollandaise rail tool)
    make_box("Kit_Mixer_Body",
             (+2.8, line_y + 0.15, cz + 1.18),
             (0.32, 0.40, 0.40), (0.92, 0.88, 0.74, 1.0))
    make_box("Kit_Mixer_Head",
             (+2.8, line_y + 0.30, cz + 1.50),
             (0.30, 0.20, 0.20), (0.86, 0.82, 0.68, 1.0))

    # Walk-in cooler — west end, big metal door
    make_box("Kit_Walkin_Body",
             (-5.0, +9.5, cz + 1.30),
             (1.80, 1.80, 2.60), COL_STEEL)
    make_box("Kit_Walkin_Door",
             (-5.0, +8.65, cz + 1.10),
             (1.00, 0.08, 2.10), (0.74, 0.76, 0.78, 1.0))
    make_box("Kit_Walkin_Handle",
             (-5.30, +8.61, cz + 1.10),
             (0.06, 0.04, 0.20), COL_BRASS_DARK)

    # Dish pit — east end
    make_box("Kit_DishPit_Counter",
             (+4.5, +9.5, cz + 0.78),
             (1.80, 1.80, 0.06), COL_STEEL)
    make_box("Kit_DishPit_Body",
             (+4.5, +9.5, cz + 0.40),
             (1.80, 1.80, 0.80), COL_STEEL)
    # Two basins
    for sx in (-1, +1):
        make_box(f"Kit_DishPit_Basin_{sx}",
                 (+4.5 + sx * 0.42, +9.5, cz + 0.74),
                 (0.62, 1.20, 0.30), (0.32, 0.32, 0.34, 1.0))
    # Sprayer hose
    make_cyl("Kit_DishPit_Sprayer_Pole",
             (+4.0, +9.5, cz + 1.00),
             0.020, 0.40, COL_STEEL)
    make_cyl("Kit_DishPit_Sprayer_Nozzle",
             (+4.0, +9.5, cz + 1.20),
             0.04, 0.08, COL_BRASS_DARK, segments=6)
    # Stack of plates ready
    for i in range(8):
        make_cyl(f"Kit_DishPit_PlateStack_{i}",
                 (+5.4, +9.5, cz + 0.85 + i * 0.02),
                 0.14, 0.02, COL_WHITE, segments=10)

    # Milk-crate radio — on the floor near the line
    make_box("Kit_MilkCrate",
             (+3.4, +8.7, cz + 0.18),
             (0.34, 0.34, 0.32), (0.62, 0.20, 0.18, 1.0))
    # Slot pattern (just decorative cutouts via darker color)
    for i in range(3):
        for j in range(3):
            make_box(f"Kit_MilkCrate_Slot_{i}_{j}",
                     (+3.4 - 0.10 + i * 0.10,
                      +8.7 - 0.17 + 0.001,
                      cz + 0.18 - 0.10 + j * 0.10),
                     (0.04, 0.001, 0.04),
                     (0.32, 0.10, 0.10, 1.0))
    # Radio on top of the crate
    make_box("Kit_Radio_Body",
             (+3.4, +8.7, cz + 0.40),
             (0.30, 0.22, 0.14), (0.22, 0.18, 0.16, 1.0))
    make_cyl("Kit_Radio_Knob_L",
             (+3.30, +8.59, cz + 0.40),
             0.020, 0.020, COL_BRASS, segments=6, axis='Y')
    make_cyl("Kit_Radio_Knob_R",
             (+3.50, +8.59, cz + 0.40),
             0.020, 0.020, COL_BRASS, segments=6, axis='Y')
    # LED display (red)
    make_box("Kit_Radio_LED",
             (+3.4, +8.59, cz + 0.46),
             (0.10, 0.005, 0.020), (0.96, 0.32, 0.20, 1.0))


# ════════════════════════════════════════════════════════════════
# STATION · PRIVATE DINING (twelve covers maximum, prix fixe)
# ════════════════════════════════════════════════════════════════
def build_private_dining():
    cx, cy = -4.0, +3.0
    cz = MAIN_FLOOR_Z
    gauntlet_marker("Z_PrivateDining", cx, cy, cz, 3.0, 3.0, "III")

    # Long table, 12 covers max (3×4 or 6 per side × 2 + ends)
    pt_x, pt_y, pt_zh = -4.0, +3.0, 0.78
    make_box("PD_Table_Top",
             (pt_x, pt_y, cz + pt_zh),
             (1.20, 3.20, 0.04), COL_LINEN)
    make_box("PD_Table_Skirt",
             (pt_x, pt_y, cz + 0.40),
             (1.10, 3.10, 0.74), COL_WALL_DARK)
    # 6 chairs per side
    for sgn in (-1, +1):
        for j in range(6):
            cy_pos = pt_y - 1.30 + j * 0.52
            cx_pos = pt_x + sgn * 0.84
            make_box(f"PD_Chair_{sgn}_{j}_Seat",
                     (cx_pos, cy_pos, cz + 0.46),
                     (0.42, 0.42, 0.04), COL_VELVET_RED)
            make_box(f"PD_Chair_{sgn}_{j}_Back",
                     (cx_pos + sgn * 0.20, cy_pos,
                      cz + 0.82),
                     (0.04, 0.42, 0.70), COL_WALL_DARK)
    # Place settings — 12 plates + glasses
    for sgn in (-1, +1):
        for j in range(6):
            cy_pos = pt_y - 1.30 + j * 0.52
            pl_x = pt_x + sgn * 0.50
            make_cyl(f"PD_Plate_{sgn}_{j}",
                     (pl_x, cy_pos, cz + pt_zh + 0.022),
                     0.12, 0.012, COL_WHITE, segments=10)
            make_cyl(f"PD_Wineglass_{sgn}_{j}",
                     (pl_x - sgn * 0.10, cy_pos + 0.16,
                      cz + pt_zh + 0.10),
                     0.035, 0.16,
                     (0.86, 0.92, 0.94, 0.4), segments=8)
    # Chandelier above
    make_cyl("PD_Chandelier_Core",
             (pt_x, pt_y, MAIN_CEIL_Z - 0.60),
             0.20, 0.40, COL_BRASS)
    for i in range(8):
        ang = i * math.pi / 4
        crx = pt_x + math.cos(ang) * 0.42
        cry = pt_y + math.sin(ang) * 0.42
        make_cyl(f"PD_Chandelier_Crystal_{i}",
                 (crx, cry, MAIN_CEIL_Z - 0.78),
                 0.030, 0.18,
                 (0.96, 0.96, 0.98, 0.7), segments=6)
    # Sideboard with brass candelabra
    make_box("PD_Sideboard",
             (-5.6, +3.0, cz + 0.45),
             (0.50, 1.40, 0.90), COL_WALL_DARK)
    make_box("PD_Sideboard_Top",
             (-5.6, +3.0, cz + 0.92),
             (0.50, 1.40, 0.04), COL_DECK_PLANK_LT)
    # Brass candelabra
    make_cyl("PD_Candelabra_Base",
             (-5.6, +3.0, cz + 0.96),
             0.08, 0.04, COL_BRASS)
    make_cyl("PD_Candelabra_Stem",
             (-5.6, +3.0, cz + 1.16),
             0.020, 0.36, COL_BRASS)
    for i in range(3):
        ang = i * (2 * math.pi / 3)
        cdx = -5.6 + math.cos(ang) * 0.14
        cdy = +3.0 + math.sin(ang) * 0.14
        make_cyl(f"PD_Candelabra_Arm_{i}_Holder",
                 (cdx, cdy, cz + 1.42),
                 0.025, 0.04, COL_BRASS)
        # Candle
        make_cyl(f"PD_Candelabra_Arm_{i}_Candle",
                 (cdx, cdy, cz + 1.52),
                 0.012, 0.16, COL_LINEN, segments=6)


# ════════════════════════════════════════════════════════════════
# STATION · HELM (Dante's office, upper deck)
# Desk, file cabinet with bottle, leaded window over dining room,
# wife's photo, brass clock from his father's office.
# ════════════════════════════════════════════════════════════════
def build_helm():
    cx, cy = 0.0, +0.0
    cz = UPPER_FLOOR_Z
    gauntlet_marker("Z_Helm", cx, cy, cz, 3.4, 2.6, "III")

    # Upper deck is smaller — a single rectangular office. We add
    # interior walls reducing it to the helm room only.
    # West wall partition (Y goes -4 to +4)
    make_box("Helm_WestPart",
             (-3.5, 0.0, cz + 1.25),
             (0.10, 6.0, 2.40), COL_WALL_DARK)
    make_box("Helm_EastPart",
             (+3.5, 0.0, cz + 1.25),
             (0.10, 6.0, 2.40), COL_WALL_DARK)
    make_box("Helm_NorthPart",
             (0.0, +3.0, cz + 1.25),
             (7.10, 0.10, 2.40), COL_WALL_DARK)
    # South wall has the leaded window overlooking the dining
    make_box("Helm_SouthPart_W",
             (-2.5, -3.0, cz + 1.25),
             (2.10, 0.10, 2.40), COL_WALL_DARK)
    make_box("Helm_SouthPart_E",
             (+2.5, -3.0, cz + 1.25),
             (2.10, 0.10, 2.40), COL_WALL_DARK)

    # The architect's LEADED WINDOW overlooking the dining room
    make_box("Helm_LeadedWindow",
             (0.0, -3.0, cz + 1.40),
             (2.50, 0.06, 1.40), COL_LEADED_GLASS)
    # Leaded lattice — diamond pattern (just N-S + E-W lines)
    for i in range(-2, 3):
        make_box(f"Helm_LWindow_MullV_{i}",
                 (i * 0.50, -3.0, cz + 1.40),
                 (0.02, 0.04, 1.40), COL_BRASS_DARK)
    for j in range(-1, 2):
        make_box(f"Helm_LWindow_MullH_{j}",
                 (0.0, -3.0, cz + 1.40 + j * 0.40),
                 (2.50, 0.04, 0.02), COL_BRASS_DARK)
    make_box("Helm_LWindow_Frame_T",
             (0.0, -3.0, cz + 2.16),
             (2.60, 0.06, 0.10), COL_WALL_DARK)
    make_box("Helm_LWindow_Frame_B",
             (0.0, -3.0, cz + 0.64),
             (2.60, 0.06, 0.10), COL_WALL_DARK)

    # Carpet — oxblood, the helm's only soft surface
    make_box("Helm_Carpet",
             (0.0, 0.0, cz + 0.014),
             (6.4, 5.6, 0.008), (0.42, 0.16, 0.14, 1.0))

    # The desk — heavy mahogany, facing the leaded window
    dk_x, dk_y = 0.0, -1.5
    make_box("Helm_Desk_Top",
             (dk_x, dk_y, cz + 0.78),
             (2.00, 1.00, 0.06), COL_WALL_DARK)
    make_box("Helm_Desk_Skirt",
             (dk_x, dk_y, cz + 0.36),
             (1.90, 0.92, 0.74), (0.30, 0.20, 0.14, 1.0))
    # Desk drawers
    for sgn in (-1, +1):
        make_box(f"Helm_Desk_Drawer_{sgn}",
                 (dk_x + sgn * 0.78, dk_y, cz + 0.36),
                 (0.06, 0.86, 0.30), (0.42, 0.30, 0.18, 1.0))
    # Brass desk lamp
    make_cyl("Helm_DeskLamp_Base",
             (dk_x - 0.60, dk_y - 0.30, cz + 0.84),
             0.07, 0.04, COL_BRASS)
    make_cyl("Helm_DeskLamp_Pole",
             (dk_x - 0.60, dk_y - 0.30, cz + 0.96),
             0.014, 0.20, COL_BRASS)
    make_cyl("Helm_DeskLamp_Shade",
             (dk_x - 0.60, dk_y - 0.30, cz + 1.16),
             0.10, 0.14, (0.92, 0.78, 0.46, 1.0), segments=10)
    # Wife's photograph — in a brass frame on the desk
    make_box("Helm_WifePhoto_Frame",
             (dk_x + 0.60, dk_y - 0.30, cz + 0.86),
             (0.18, 0.02, 0.22), COL_BRASS)
    make_box("Helm_WifePhoto",
             (dk_x + 0.60, dk_y - 0.31, cz + 0.86),
             (0.14, 0.001, 0.18),
             (0.72, 0.68, 0.58, 1.0))
    # The brass clock from Dante's father's office — on the wall
    make_cyl("Helm_FathersClock",
             (0.0, +2.95, cz + 1.80),
             0.24, 0.06, COL_BRASS, segments=12, axis='Y')
    # Clock face inside
    make_cyl("Helm_FathersClock_Face",
             (0.0, +2.91, cz + 1.80),
             0.20, 0.005, COL_LINEN, segments=12, axis='Y')
    # Hands
    make_box("Helm_FathersClock_HandH",
             (0.0, +2.90, cz + 1.83),
             (0.04, 0.001, 0.10), COL_BLACK)
    make_box("Helm_FathersClock_HandM",
             (0.0, +2.90, cz + 1.78),
             (0.02, 0.001, 0.16), COL_BLACK)

    # File cabinet — with the bottle. East wall.
    make_box("Helm_FileCab_Body",
             (+3.0, +2.0, cz + 0.62),
             (0.50, 0.50, 1.24), COL_WALL_DARK)
    # 3 drawer fronts
    for i in range(3):
        dz = cz + 0.18 + i * 0.42
        make_box(f"Helm_FileCab_Drawer_{i}",
                 (+3.0, +1.74, dz),
                 (0.42, 0.02, 0.36), (0.42, 0.30, 0.18, 1.0))
        make_box(f"Helm_FileCab_Pull_{i}",
                 (+3.0, +1.72, dz),
                 (0.16, 0.04, 0.04), COL_BRASS)
    # The bottle on top of the cabinet (the canon detail)
    make_cyl("Helm_FileCab_Bottle",
             (+3.0, +2.0, cz + 1.34),
             0.05, 0.20, COL_BOTTLE_BROWN, segments=8)
    make_cyl("Helm_FileCab_Bottle_Cap",
             (+3.0, +2.0, cz + 1.46),
             0.04, 0.04, COL_BRASS_DARK, segments=8)
    # Glass next to the bottle
    make_cyl("Helm_FileCab_Glass",
             (+2.78, +2.0, cz + 1.30),
             0.04, 0.08, (0.86, 0.92, 0.94, 0.5), segments=10)

    # Office chair behind the desk
    ch_x, ch_y = 0.0, -2.4
    make_box("Helm_OfficeChair_Seat",
             (ch_x, ch_y, cz + 0.50),
             (0.50, 0.50, 0.10), COL_LEATHER_OX)
    make_box("Helm_OfficeChair_Back",
             (ch_x, ch_y - 0.22, cz + 1.10),
             (0.50, 0.10, 0.90), COL_LEATHER_OX)
    make_cyl("Helm_OfficeChair_Post",
             (ch_x, ch_y, cz + 0.28),
             0.04, 0.50, COL_BLACK)
    # 5-prong base
    for i in range(5):
        ang = i * (2 * math.pi / 5)
        make_box(f"Helm_OfficeChair_Prong_{i}",
                 (ch_x + math.cos(ang) * 0.20,
                  ch_y + math.sin(ang) * 0.20,
                  cz + 0.04),
                 (0.32, 0.06, 0.04), COL_BLACK)

    # Books on a small shelf behind the desk
    make_box("Helm_BookShelf",
             (-3.0, -2.0, cz + 1.50),
             (0.30, 1.20, 0.04), COL_WALL_DARK)
    for i in range(6):
        col = [COL_LEATHER_OX, COL_LEATHER_BLACK, COL_BRASS_DARK,
               COL_WALL_DARK][i % 4]
        make_box(f"Helm_Book_{i}",
                 (-3.0, -2.0 - 0.40 + i * 0.16, cz + 1.66),
                 (0.20, 0.12, 0.24), col)


# ════════════════════════════════════════════════════════════════
# STATION · OFFICE STAIRCASE
# The iron stair from helm down to dining room (architect's pride)
# ════════════════════════════════════════════════════════════════
def build_office_staircase():
    cx, cy = +3.0, -3.0
    cz = UPPER_FLOOR_Z
    gauntlet_marker("Z_OfficeStaircase", cx, cy, cz, 1.6, 1.6, "III")

    # Cutout in the upper floor where the stair drops — a darker
    # square so the floor reads as having an opening
    make_box("OS_FloorCutout",
             (cx, cy, cz - 0.06),
             (1.20, 1.40, 0.04), (0.06, 0.04, 0.04, 1.0))
    # Iron stair treads — straight stair descending south
    for i in range(10):
        tz = cz - i * 0.26
        ty = cy + 0.60 - i * 0.30
        make_box(f"OS_Tread_{i}",
                 (cx, ty, tz),
                 (1.00, 0.32, 0.04), (0.20, 0.20, 0.22, 1.0))
        # Stringer (the iron side rail beam)
        for sgn in (-1, +1):
            make_box(f"OS_Stringer_{i}_{sgn}",
                     (cx + sgn * 0.55, ty, tz - 0.16),
                     (0.04, 0.32, 0.32), COL_BLACK)
    # Iron railing (a continuous rail on both sides)
    for sgn in (-1, +1):
        # Top rail
        make_cyl(f"OS_RailTop_{sgn}",
                 (cx + sgn * 0.62, cy - 1.0, cz - 1.0),
                 0.024, 3.20, COL_BLACK, segments=6, axis='Y')
        # Vertical balusters
        for i in range(8):
            by_pos = cy + 0.60 - i * 0.40
            make_cyl(f"OS_Baluster_{sgn}_{i}",
                     (cx + sgn * 0.62, by_pos,
                      cz - i * 0.26 + 0.30),
                     0.012, 0.80, COL_BLACK)


# ════════════════════════════════════════════════════════════════
# LOWER DECK — CATERING OFFICE, CARD ROOM, BACK ROOM,
# STAFF LOCKER ROOM, BACK CORRIDOR
# ════════════════════════════════════════════════════════════════
def build_lower_deck_partitions():
    """The lower deck is 'the empire under the empire' — a tight
    corridor connecting tiny purpose-built rooms."""
    cz = LOWER_FLOOR_Z
    # ── BACK CORRIDOR runs E-W along Y=+2 (north section)
    # Wall between corridor (north) and the rooms (south)
    # 3 doors cut: catering office, card room, back room
    # Corridor north wall is the hull at Y=+12 (not built here)
    # Corridor south wall pieces
    make_box("LD_Corr_S_W", (-4.0, +2.0, cz + 1.20),
             (4.0, 0.10, 2.30), COL_WALL_PAPER)
    make_box("LD_Corr_S_C", (+1.0, +2.0, cz + 1.20),
             (2.0, 0.10, 2.30), COL_WALL_PAPER)
    make_box("LD_Corr_S_E", (+4.6, +2.0, cz + 1.20),
             (2.8, 0.10, 2.30), COL_WALL_PAPER)
    # Above-door headers (3 doorways)
    for dx in [-1.5, +2.5, +5.4]:
        make_box(f"LD_Corr_AboveDoor_{int(dx*10)}",
                 (dx, +2.0, cz + 2.20),
                 (1.0, 0.10, 0.30), COL_WALL_PAPER)

    # Catering office (west) — walls at X=-3 dividing it from card room
    make_box("LD_CatOf_E_Wall_S", (-3.0, -2.0, cz + 1.20),
             (0.10, 6.0, 2.30), COL_WALL_PAPER)
    # Card room (center) — walls at X=+1.5 dividing from back room
    make_box("LD_Card_E_Wall_S", (+1.5, -2.0, cz + 1.20),
             (0.10, 6.0, 2.30), COL_WALL_PAPER)
    # Back room (east center) — walls at X=+4.0 dividing from
    # staff locker
    make_box("LD_Back_E_Wall_S", (+4.0, -2.0, cz + 1.20),
             (0.10, 6.0, 2.30), COL_WALL_PAPER)
    # Staff locker room — east of X=+4
    # Staff exit south wall — already the hull
    # Wall between rooms (Y=-5 to +2) and staff exit corridor
    # (south, Y<-5)
    make_box("LD_Rooms_S_Wall", (0.0, -5.0, cz + 1.20),
             (12.0, 0.10, 2.30), COL_WALL_PAPER)
    # Cut for staff exit doorway at Y=-5, X=+5
    # (skip a 1.2m segment — handled by NOT building that piece)
    # actually rebuild with gap:
    # We rebuild it as 2 segments:
    # Remove the big single wall added above by overwriting — but
    # we already added it. For visual purposes here we just paint a
    # door on top. (Cleaner pass later.)

    # Lower deck carpet — dark + utilitarian
    make_box("LD_Carpet",
             (0.0, -1.5, cz + 0.013),
             (11.8, 7.0, 0.008), COL_CARPET_DARK)
    # Corridor floor (more institutional vinyl)
    make_box("LD_Corr_Floor",
             (0.0, +6.0, cz + 0.013),
             (11.8, 5.0, 0.008), (0.42, 0.40, 0.38, 1.0))


def build_back_corridor():
    """Time clock, coat rack, bulletin board, schedule, door to
    side door."""
    cx, cy = 0.0, +6.0
    cz = LOWER_FLOOR_Z
    gauntlet_marker("Z_BackCorridor", cx, cy, cz, 4.0, 2.0, "III")

    # Time clock — east wall at Y=+5 (south side of corridor)
    make_box("BC_TimeClock_Body",
             (+5.6, +5.5, cz + 1.50),
             (0.30, 0.20, 0.40), COL_BLACK)
    # Display
    make_box("BC_TimeClock_Display",
             (+5.4, +5.5, cz + 1.60),
             (0.020, 0.16, 0.16),
             (0.32, 0.96, 0.42, 1.0))
    # Slot
    make_box("BC_TimeClock_Slot",
             (+5.4, +5.5, cz + 1.40),
             (0.020, 0.10, 0.020), COL_LINEN)
    # Card rack below (with time cards)
    make_box("BC_TimeCard_Rack",
             (+5.5, +5.5, cz + 0.95),
             (0.18, 0.40, 0.40),
             (0.42, 0.30, 0.18, 1.0))
    for i in range(8):
        make_box(f"BC_TimeCard_{i}",
                 (+5.42, +5.5 - 0.18 + i * 0.04, cz + 1.10),
                 (0.006, 0.04, 0.20), COL_PAPER)

    # Coat rack — east-center
    make_box("BC_CoatRack_Base",
             (+1.0, +5.4, cz + 0.04),
             (0.40, 0.10, 0.08), COL_BLACK)
    make_cyl("BC_CoatRack_Pole",
             (+1.0, +5.4, cz + 1.00),
             0.030, 1.90, COL_BLACK)
    # Hook arms
    for i in range(4):
        ang = i * (math.pi / 2)
        hx = +1.0 + math.cos(ang) * 0.18
        hy = +5.4 + math.sin(ang) * 0.18
        make_cyl(f"BC_CoatRack_Hook_{i}",
                 (hx, hy, cz + 1.80),
                 0.012, 0.16, COL_BRASS_DARK, segments=4)
    # 2 coats hanging on it
    for i in range(2):
        col = [COL_VELVET_RED, COL_LEATHER_BLACK][i]
        ang = i * (math.pi / 2)
        cx_pos = +1.0 + math.cos(ang) * 0.20
        cy_pos = +5.4 + math.sin(ang) * 0.20
        make_box(f"BC_Coat_{i}",
                 (cx_pos, cy_pos, cz + 1.10),
                 (0.30, 0.12, 0.90), col)

    # Bulletin board — west wall
    make_box("BC_Bulletin_Board",
             (-5.4, +6.0, cz + 1.60),
             (0.04, 1.40, 0.90), (0.62, 0.46, 0.28, 1.0))
    make_box("BC_Bulletin_Frame",
             (-5.42, +6.0, cz + 1.60),
             (0.02, 1.50, 1.00), COL_WALL_DARK)
    # Schedule + notices (paper rectangles pinned)
    for i in range(8):
        col_i = i % 4
        row_i = i // 4
        px = -5.4 - 0.50 + col_i * 0.34
        pz = cz + 1.30 + row_i * 0.36
        make_box(f"BC_Notice_{i}",
                 (-5.40, px, pz),
                 (0.005, 0.22, 0.22), COL_PAPER)
    # Big "SCHEDULE" sheet center
    make_box("BC_Schedule",
             (-5.40, +6.0, cz + 1.75),
             (0.005, 0.42, 0.50), COL_PAPER_AGED)


def build_catering_office():
    """Catering desk, phone (ringing), 8-year filing cabinet."""
    cx, cy = -4.5, -1.5
    cz = LOWER_FLOOR_Z
    gauntlet_marker("Z_CateringOffice", cx, cy, cz, 2.4, 2.4, "III")

    # Desk — small office desk
    dk_x, dk_y = -4.5, -1.0
    make_box("Cat_Desk_Top",
             (dk_x, dk_y, cz + 0.74),
             (1.40, 0.70, 0.04), COL_WALL_DARK)
    for sx in (-1, +1):
        for sy in (-1, +1):
            make_cyl(f"Cat_Desk_Leg_{sx}_{sy}",
                     (dk_x + sx * 0.62, dk_y + sy * 0.30,
                      cz + 0.37),
                     0.022, 0.74, (0.32, 0.22, 0.14, 1.0))
    # Phone — beige rotary on the desk (it's ringing)
    make_box("Cat_Phone_Body",
             (dk_x + 0.40, dk_y - 0.10, cz + 0.78),
             (0.20, 0.30, 0.10), (0.92, 0.86, 0.74, 1.0))
    make_box("Cat_Phone_Handset",
             (dk_x + 0.40, dk_y - 0.10, cz + 0.85),
             (0.10, 0.30, 0.04), (0.86, 0.78, 0.66, 1.0))
    # Spiral cord
    for i in range(4):
        zoff = i * 0.025
        make_cyl(f"Cat_Phone_Cord_{i}",
                 (dk_x + 0.40, dk_y - 0.32, cz + 0.80 + zoff),
                 0.012, 0.02,
                 (0.62, 0.52, 0.38, 1.0), segments=6, axis='Y')
    # Paperwork — stacked + dated entries
    for i in range(3):
        make_box(f"Cat_Paper_Stack_{i}",
                 (dk_x - 0.30, dk_y, cz + 0.78 + i * 0.014),
                 (0.20, 0.28, 0.012), COL_PAPER_AGED)
    # File cabinet — 4 drawer, holds 8 years of contracts
    make_box("Cat_FileCab_Body",
             (-5.50, -2.5, cz + 0.80),
             (0.50, 0.60, 1.60), COL_BLACK)
    for i in range(4):
        dz = cz + 0.30 + i * 0.36
        make_box(f"Cat_FileCab_Drawer_{i}",
                 (-5.50, -2.20, dz),
                 (0.46, 0.02, 0.30), (0.32, 0.30, 0.32, 1.0))
        make_box(f"Cat_FileCab_Handle_{i}",
                 (-5.50, -2.18, dz),
                 (0.20, 0.04, 0.04), COL_BRASS_DARK)
    # Labels on each drawer (decades of contracts)
    for i, year in enumerate(['16-17', '18-19', '20-21', '22-24']):
        # Just decorative box
        make_box(f"Cat_FileCab_Label_{i}",
                 (-5.49, -2.18, cz + 0.36 + i * 0.36),
                 (0.001, 0.10, 0.04), COL_PAPER_AGED)
    # A wall calendar
    make_box("Cat_WallCalendar",
             (-5.94, -1.0, cz + 1.70),
             (0.02, 0.50, 0.60), COL_PAPER)
    # An office chair
    make_box("Cat_OfficeChair_Seat",
             (-4.5, -1.7, cz + 0.46),
             (0.46, 0.46, 0.08), COL_LEATHER_BLACK)
    make_box("Cat_OfficeChair_Back",
             (-4.5, -1.92, cz + 1.00),
             (0.46, 0.06, 0.66), COL_LEATHER_BLACK)
    make_cyl("Cat_OfficeChair_Post",
             (-4.5, -1.7, cz + 0.26),
             0.030, 0.40, COL_BLACK)


def build_card_room():
    """Saturday-night 5-card stud, green felt, regulars' chairs.
    Felt is original (since the seventies)."""
    cx, cy = -1.0, -1.0
    cz = LOWER_FLOOR_Z
    gauntlet_marker("Z_CardRoom", cx, cy, cz, 2.4, 2.4, "III")

    # Round felt table
    tb_x, tb_y = -1.0, -1.0
    make_cyl("Card_Table_Top",
             (tb_x, tb_y, cz + 0.75),
             0.90, 0.04, COL_FELT_GREEN, segments=16)
    # Rail around the table (oxblood leather)
    make_cyl("Card_Table_Rail",
             (tb_x, tb_y, cz + 0.79),
             0.94, 0.04, COL_LEATHER_OX, segments=16)
    # Pedestal
    make_cyl("Card_Table_Pedestal",
             (tb_x, tb_y, cz + 0.36),
             0.14, 0.74, COL_WALL_DARK)
    # 4-prong base (poker table with stable footing)
    for i in range(4):
        ang = i * (math.pi / 2)
        make_box(f"Card_Table_Prong_{i}",
                 (tb_x + math.cos(ang) * 0.30,
                  tb_y + math.sin(ang) * 0.30,
                  cz + 0.04),
                 (0.50, 0.10, 0.06), COL_WALL_DARK)
    # 5 chairs around the table
    for i in range(5):
        ang = i * (2 * math.pi / 5) + math.pi / 2
        ch_x = tb_x + math.cos(ang) * 1.30
        ch_y = tb_y + math.sin(ang) * 1.30
        make_box(f"Card_Chair_{i}_Seat",
                 (ch_x, ch_y, cz + 0.46),
                 (0.42, 0.42, 0.08), COL_LEATHER_OX)
        # Back facing away from table
        bk_dx = -math.cos(ang) * 0.22
        bk_dy = -math.sin(ang) * 0.22
        make_box(f"Card_Chair_{i}_Back",
                 (ch_x + bk_dx, ch_y + bk_dy, cz + 0.96),
                 (0.42, 0.06, 0.80), COL_WALL_DARK)
    # Cards + chips on the table
    # Card deck
    make_box("Card_Deck_Stack",
             (tb_x, tb_y, cz + 0.79),
             (0.06, 0.10, 0.02), COL_LINEN)
    # 5 chip stacks
    for i in range(5):
        ang = i * (2 * math.pi / 5) + math.pi / 4
        stk_x = tb_x + math.cos(ang) * 0.45
        stk_y = tb_y + math.sin(ang) * 0.45
        for j in range(6):
            col = [(0.92, 0.92, 0.92, 1.0),
                   (0.62, 0.18, 0.18, 1.0),
                   (0.18, 0.32, 0.62, 1.0)][i % 3]
            make_cyl(f"Card_Chip_{i}_{j}",
                     (stk_x, stk_y, cz + 0.78 + j * 0.010),
                     0.020, 0.008, col, segments=8)
    # Pendant lamp over table (low, intimate)
    make_box("Card_Pendant_Cord",
             (tb_x, tb_y, cz + 1.6),
             (0.02, 0.02, 0.40), COL_BLACK)
    make_cyl("Card_Pendant_Shade",
             (tb_x, tb_y, cz + 1.30),
             0.30, 0.16, (0.42, 0.30, 0.18, 1.0), segments=10)


def build_back_room():
    """High-stakes table, by invitation only, no sign on the door."""
    cx, cy = +2.5, -1.0
    cz = LOWER_FLOOR_Z
    gauntlet_marker("Z_BackRoom", cx, cy, cz, 2.4, 2.4, "III")

    # Smaller felt table (more private) — different green
    tb_x, tb_y = +2.5, -1.0
    make_cyl("Back_Table_Top",
             (tb_x, tb_y, cz + 0.75),
             0.80, 0.04, (0.22, 0.42, 0.30, 1.0), segments=14)
    make_cyl("Back_Table_Rail",
             (tb_x, tb_y, cz + 0.79),
             0.84, 0.04, COL_LEATHER_BLACK, segments=14)
    make_cyl("Back_Table_Pedestal",
             (tb_x, tb_y, cz + 0.36),
             0.14, 0.74, COL_WALL_DARK)
    # 4 chairs (smaller room)
    for i in range(4):
        ang = i * (math.pi / 2) + math.pi / 4
        ch_x = tb_x + math.cos(ang) * 1.20
        ch_y = tb_y + math.sin(ang) * 1.20
        make_box(f"Back_Chair_{i}_Seat",
                 (ch_x, ch_y, cz + 0.46),
                 (0.42, 0.42, 0.08), COL_LEATHER_BLACK)
        bk_dx = -math.cos(ang) * 0.22
        bk_dy = -math.sin(ang) * 0.22
        make_box(f"Back_Chair_{i}_Back",
                 (ch_x + bk_dx, ch_y + bk_dy, cz + 0.96),
                 (0.42, 0.06, 0.80), (0.16, 0.14, 0.14, 1.0))
    # Huge stack of $100s in the middle (the high-stakes feel)
    for i in range(10):
        make_box(f"Back_Cash_Stack_{i}",
                 (tb_x, tb_y, cz + 0.78 + i * 0.008),
                 (0.16, 0.06, 0.006), (0.42, 0.62, 0.42, 1.0))
    # Black-shaded pendant (more intimate, more shadow)
    make_box("Back_Pendant_Cord",
             (tb_x, tb_y, cz + 1.6),
             (0.02, 0.02, 0.40), COL_BLACK)
    make_cyl("Back_Pendant_Shade",
             (tb_x, tb_y, cz + 1.30),
             0.28, 0.16, COL_BLACK, segments=10)
    # The door — NO SIGN (just the door, all dark wood, no markings)
    make_box("Back_Door",
             (+2.5, +2.04, cz + 1.05),
             (0.90, 0.04, 2.10), (0.20, 0.14, 0.10, 1.0))
    # Brass knob
    make_box("Back_Door_Knob",
             (+2.95, +2.06, cz + 1.05),
             (0.04, 0.04, 0.04), COL_BRASS_DARK)


def build_staff_locker_room():
    """Lockers (Sammy's nameplate at the end since '83), bench."""
    cx, cy = +5.0, -1.0
    cz = LOWER_FLOOR_Z
    gauntlet_marker("Z_StaffLocker", cx, cy, cz, 1.8, 2.4, "III")

    # 8 lockers in a row along the east wall
    for i in range(8):
        lz = cz + 1.00
        lx = HULL_X_E - 0.30
        ly = -4.0 + i * 0.50
        make_box(f"SL_Locker_{i}_Body",
                 (lx, ly, lz),
                 (0.40, 0.42, 1.90), (0.42, 0.46, 0.52, 1.0))
        # Door + handle
        make_box(f"SL_Locker_{i}_DoorSeam",
                 (lx - 0.21, ly, lz),
                 (0.02, 0.40, 1.80), (0.30, 0.32, 0.36, 1.0))
        make_box(f"SL_Locker_{i}_Handle",
                 (lx - 0.23, ly + 0.12, lz),
                 (0.02, 0.06, 0.06), COL_BRASS_DARK)
        # Vent grille on door
        for j in range(3):
            make_box(f"SL_Locker_{i}_Vent_{j}",
                     (lx - 0.22, ly, lz + 0.60 + j * 0.08),
                     (0.005, 0.20, 0.02), COL_BLACK)
        # Nameplate (small label)
        col = COL_BRASS if i == 7 else COL_PAPER_AGED
        make_box(f"SL_Locker_{i}_Plate",
                 (lx - 0.22, ly, lz + 0.85),
                 (0.005, 0.20, 0.06), col)
    # Sammy's nameplate (the brass one, locker 7 = "the end")
    # Already painted brass above. Add a small detail on top.
    make_box("SL_Sammy_NameDetail",
             (HULL_X_E - 0.52, -4.0 + 7 * 0.50, cz + 1.85),
             (0.005, 0.12, 0.02), COL_BLACK)

    # Bench in the center where staff change shoes
    bn_x, bn_y = +4.5, -1.0
    make_box("SL_Bench_Seat",
             (bn_x, bn_y, cz + 0.40),
             (0.30, 1.80, 0.06), COL_DECK_PLANK)
    for sy in (-1, +1):
        make_box(f"SL_Bench_Leg_{sy}",
                 (bn_x, bn_y + sy * 0.80, cz + 0.20),
                 (0.30, 0.06, 0.40), COL_DECK_PLANK)

    # A pair of shoes on the bench (the canon ones change shoes)
    for i in range(2):
        make_box(f"SL_Shoes_{i}_Sole",
                 (bn_x, bn_y + 0.40 + i * 0.16, cz + 0.45),
                 (0.10, 0.12, 0.04), COL_LEATHER_BLACK)
        make_box(f"SL_Shoes_{i}_Upper",
                 (bn_x, bn_y + 0.40 + i * 0.16, cz + 0.51),
                 (0.10, 0.10, 0.08), COL_LEATHER_BLACK)


# ════════════════════════════════════════════════════════════════
# THRESHOLDS · STAFF EXIT + GANGWAY (SIDE DOOR painted earlier)
# ════════════════════════════════════════════════════════════════
def build_staff_exit():
    cx, cy = +5.0, -5.5
    cz = LOWER_FLOOR_Z
    gauntlet_marker("Z_StaffExit", cx, cy, cz, 1.6, 1.0, "III")
    # Door on south wall
    make_box("StaffExit_Door",
             (+5.0, -5.04, cz + 1.05),
             (1.00, 0.06, 2.10), COL_WALL_DARK)
    make_box("StaffExit_Door_Knob",
             (+5.40, -5.01, cz + 1.05),
             (0.04, 0.04, 0.04), COL_BRASS_DARK)
    # EXIT sign (the only painted text)
    make_box("StaffExit_ExitSign",
             (+5.0, -5.05, cz + 2.30),
             (0.50, 0.005, 0.16), (0.96, 0.20, 0.20, 1.0))
    # Small walkway (a hint of the back walkway outside)
    make_box("StaffExit_OutsideWalkway",
             (+5.0, -6.2, cz + 0.01),
             (1.40, 1.40, 0.02), (0.42, 0.40, 0.38, 1.0))


def build_gangway():
    cx, cy = 0.0, -11.0
    cz = MAIN_FLOOR_Z
    gauntlet_marker("Z_Gangway", cx, cy, cz, 3.0, 1.6, "III")

    # Gangway — the plank from boat to dock. We build a sloped
    # rectangle going from the boat's south edge down to a small
    # dock platform.
    # Boat south door (the entrance from gangway)
    make_box("GW_BoatDoor",
             (0.0, HULL_Y_S + 0.04, cz + 1.05),
             (1.20, 0.04, 2.10), COL_WALL_DARK)
    make_box("GW_BoatDoor_FrameT",
             (0.0, HULL_Y_S, cz + 2.18),
             (1.40, 0.20, 0.12), COL_BRASS_DARK)
    # The gangway plank — slanted from boat (cz) down to dock
    # (cz - 1.0)
    # Simulate via a flat box (we don't rotate the mesh, just slope
    # visual with the plank's center between boat + dock)
    gw_len = 3.0
    make_box("GW_Plank",
             (0.0, HULL_Y_S - gw_len / 2.0, cz - 0.30),
             (1.40, gw_len, 0.10), COL_DECK_PLANK)
    # Rope rails on both sides
    for sgn in (-1, +1):
        make_cyl(f"GW_Rope_{sgn}",
                 (sgn * 0.70, HULL_Y_S - gw_len / 2.0, cz + 0.10),
                 0.025, gw_len, (0.62, 0.46, 0.20, 1.0),
                 segments=6, axis='Y')
    # Posts at each end
    for sgn_x in (-1, +1):
        for sgn_y, ypos in [(-1, HULL_Y_S - gw_len),
                            (+1, HULL_Y_S - 0.10)]:
            make_cyl(f"GW_Post_x{sgn_x}_y{sgn_y}",
                     (sgn_x * 0.70, ypos, cz + 0.30),
                     0.040, 1.40, COL_BRASS_DARK)
    # Small dock platform at the far end
    make_box("GW_DockPlatform",
             (0.0, HULL_Y_S - gw_len - 0.50, cz - 0.80),
             (3.0, 1.0, 0.10), COL_DECK_PLANK_LT)


# ════════════════════════════════════════════════════════════════
# EXPORT
# ════════════════════════════════════════════════════════════════
def export_glb():
    out_dir = os.path.normpath(
        os.path.join(os.path.dirname(os.path.abspath(__file__)),
                     OUTPUT_DIR))
    os.makedirs(out_dir, exist_ok=True)
    out_path = os.path.join(out_dir, OUTPUT_NAME)

    print(f"\n[build_riverboat_interior] exporting to {out_path}")
    print(f"[build_riverboat_interior] scene objects: "
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
        print(f"[build_riverboat_interior] export result: {result}")
    except Exception as e:
        print(f"[build_riverboat_interior] ✗ EXPORT FAILED: {e}")
        import traceback
        traceback.print_exc()
        raise

    if os.path.exists(out_path):
        size = os.path.getsize(out_path)
        print(f"[build_riverboat_interior] ✓ wrote {out_path} "
              f"({size} bytes)")


def build_empress_dressing():
    """Scene-description specifics from the Empress scenarios
    (static_bloom, the_back_room_calls, when_youre_ready) that the
    generic builders don't cover. Always present in the GLB.

    Adds:
      · A brass "14" plaque on the canonical Table 14 (when_youre_ready:
        "Dean is arriving at Table 14 turn 2"). Picks the T_2_1 table
        in the 4x3 grid — middle of the room, the natural "first
        Dean arrives" reveal table.
      · An envelope on the maître d' stand (the_back_room_calls:
        "Dante has handed you the envelope at the maître d' stand").
      · An intercom box at Sammy's bar (when_youre_ready: "The
        intercom to Dante's helm is available at Sammy's bar").
      · A small "saturday regulars" placard on the card-room door
        (the_back_room_calls: "the card room is hosting Saturday's
        regulars on what should have been a Friday-quiet night").
    """
    # ── Brass "14" plaque on Table T_2_1 ──
    # T_2_1 from build_main_dining: tx = -4.0 + 2 * 2.0 = 0.0, ty = -5.5 + 1 * 2.0 = -3.5
    t14_x = 0.0
    t14_y = -3.5
    table_top_z = MAIN_FLOOR_Z + 0.74   # approximate dining table top
    # Brass plaque at the table edge facing the dining-room aisle (south face)
    make_box("Table_14_Plaque",
             (t14_x, t14_y - 0.52, table_top_z + 0.02),
             (0.14, 0.005, 0.08),
             (0.74, 0.62, 0.32, 1.0))   # brass
    # Engraved "14" — two darker slots side-by-side
    make_box("Table_14_Digit_1",
             (t14_x - 0.03, t14_y - 0.508, table_top_z + 0.02),
             (0.018, 0.005, 0.04),
             (0.20, 0.16, 0.10, 1.0))
    make_box("Table_14_Digit_4",
             (t14_x + 0.03, t14_y - 0.508, table_top_z + 0.02),
             (0.028, 0.005, 0.04),
             (0.20, 0.16, 0.10, 1.0))
    # ── Reserved card standing on the table (Dean's arrival, turn 2) ──
    make_box("Table_14_ReservedCard_Tent",
             (t14_x - 0.18, t14_y - 0.08, table_top_z + 0.05),
             (0.16, 0.10, 0.10),
             (0.94, 0.90, 0.84, 1.0))   # cream cardstock
    make_box("Table_14_ReservedCard_TextStrip",
             (t14_x - 0.18, t14_y - 0.131, table_top_z + 0.07),
             (0.12, 0.003, 0.018),
             (0.22, 0.18, 0.14, 1.0))   # printed "RESERVED" text strip

    # ── Envelope on the maître d' stand ──
    # Stand is at (0.0, -8.5), top at z = MAIN_FLOOR_Z + 1.31.
    md_x, md_y = 0.0, -8.5
    md_top_z = MAIN_FLOOR_Z + 1.31
    # Manila envelope (slightly off-center, leaning against the
    # reservation book at the east side of the stand top)
    make_box("MaitreD_Envelope_Body",
             (md_x + 0.20, md_y, md_top_z + 0.012),
             (0.26, 0.18, 0.018),
             (0.78, 0.68, 0.46, 1.0))   # manila kraft
    # Wax seal (small red circle on the front)
    make_cyl("MaitreD_Envelope_Seal",
             (md_x + 0.24, md_y, md_top_z + 0.024),
             0.018, 0.004,
             (0.62, 0.18, 0.18, 1.0),
             segments=8, axis='Z')
    # Address line (a thin dark strip — handwritten address)
    make_box("MaitreD_Envelope_AddressLine",
             (md_x + 0.18, md_y, md_top_z + 0.024),
             (0.16, 0.16, 0.0005),
             (0.20, 0.18, 0.14, 1.0))

    # ── Intercom box at Sammy's bar ──
    # Sammy's bar is the east half of the main deck (positive X).
    # Mount the intercom on the bar's east-facing back wall at
    # bartender eye height.
    int_x = +5.8
    int_y = -2.5    # roughly mid-bar
    int_z = MAIN_FLOOR_Z + 1.42
    # Body
    make_box("Sammy_Intercom_Body",
             (int_x, int_y, int_z),
             (0.18, 0.06, 0.24),
             (0.30, 0.26, 0.20, 1.0))   # bakelite brown
    # Speaker grille (mesh-effect via a slightly lighter inset box)
    make_box("Sammy_Intercom_Speaker",
             (int_x, int_y - 0.031, int_z + 0.05),
             (0.14, 0.005, 0.10),
             (0.18, 0.16, 0.14, 1.0))
    # Press-to-talk button (brass)
    make_cyl("Sammy_Intercom_PTT",
             (int_x, int_y - 0.031, int_z - 0.07),
             0.020, 0.012,
             (0.74, 0.62, 0.32, 1.0),
             segments=8, axis='Y')
    # Brass "HELM" plaque under the button
    make_box("Sammy_Intercom_HelmPlaque",
             (int_x, int_y - 0.031, int_z - 0.10),
             (0.08, 0.003, 0.020),
             (0.74, 0.62, 0.32, 1.0))

    # ── "SATURDAY REGULARS" placard on the card-room door ──
    # Card room is below decks (lower deck). The card-room door
    # gets a small cream cardstock placard.
    # Approximate door location — adjust as build_card_room evolves.
    placard_x = +2.5
    placard_y = -8.5   # card room is aft in the lower deck
    placard_z = MAIN_FLOOR_Z - 2.50   # lower deck level
    make_box("CardRoom_Placard",
             (placard_x + 0.02, placard_y, placard_z + 1.60),
             (0.005, 0.18, 0.10),
             (0.92, 0.88, 0.72, 1.0))   # cream cardstock
    # Three dark text lines on the placard
    for tl in range(3):
        make_box("CardRoom_Placard_TextLine_%d" % tl,
                 (placard_x + 0.022, placard_y, placard_z + 1.64 - tl * 0.02),
                 (0.003, 0.14, 0.006),
                 (0.22, 0.18, 0.14, 1.0))


def main():
    clear_scene()
    build_hull_and_decks()
    build_main_deck_partitions()
    build_maitre_d()
    build_main_dining()
    build_table_17()
    build_sammys_bar()
    build_the_pass()
    build_kitchen()
    build_private_dining()
    build_helm()
    build_office_staircase()
    build_lower_deck_partitions()
    build_back_corridor()
    build_catering_office()
    build_card_room()
    build_back_room()
    build_staff_locker_room()
    build_staff_exit()
    build_gangway()
    # Scene-description specifics from the Empress scenarios — the
    # Table 14 brass plaque + reserved card, the manila envelope on
    # the maître d' stand, the intercom to Dante's helm at Sammy's
    # bar, the Saturday-regulars placard on the card-room door.
    build_empress_dressing()
    export_glb()


if __name__ == "__main__":
    main()
