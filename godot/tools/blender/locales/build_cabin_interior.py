"""Doc Reyes' cabin — Alsea north fork — vol7 hero locale.

Third-most-used VN background of the volume (27 scenes). Olaf and
Eddvard built the cabin in '79 (vol7_ch10_cabin); Tem has kept it
since her grandfather Eddvard died in '42. PNW register: cedar
everything, the woodstove as hearth-center, kerosene light, small
and warm and weathered. Canon sources baked in:

  · vol7_ch1_morning (the volume's opening): rain on the cedar
    roof; the small bedroom with the WINDOW ABOVE THE BED that HAS
    NO CURTAIN and never has — gray-green cedars at five-thirty;
    the Pendleton wool blanket (Washougal mill, the cabin has
    three); the short hallway to the main room; the main room
    holds the wood stove, the small wooden table beside the
    kerosene lamp, two armchairs, and the daybed where Kai slept;
    the thermometer above the door (nailed there in 1979); the
    copper kettle with the dent; the 1973 cast-iron skillet; the
    camp stove + metal cone filter (the coffee setup since 2031);
    the John Frank novel, the clay dish of rosemary, and three
    SCUMM sticks in waxed-paper sleeves on the table; toast in the
    small wire rack on the stove; butter in the pottery dish;
    eggs on the small shelf by the cold-box; the wool socks on
    the small shelf by the door; the south-facing window with the
    porch and the cedars beyond.
  · vol7_ch4_finn: the peg by the door where Finn hangs the wet
    coat; the SHELF ABOVE THE KEROSENE LAMP where the small cedar
    bowl (Olaf's carving, warm since July) lives; Tem banks the
    stove with the cedar in the basket beside it.
  · vol7_ch4_alone: fire built back up from the basket, kettle
    set, the thermometer read at fifty-eight.
  · vol7_ch10_cabin: "the reader was on the shelf where it had
    been since '46"; Eddvard's desk with the drawers; the porch
    Tem waits on with her coffee.
  · vol7_ch19_cedar / music vol7_four_bowls: the FOUR CEDAR BOWLS
    warm on the table facing the door; Brandon's notebook and the
    thumb-size carved cedar (Olaf's open hand holding the bell)
    beside them; the crow on the back of one of the chairs; the
    crow's perch Lena and Kai brought up; mint tea for seven;
    "the stove banked higher than she banks it in the mornings,
    kerosene light".
  · music vol7_cabin_woodstove: "damper-pull tick + a log settling
    at the back of the firebox + plank floor cooling".

Shell footprint kept from the scaffold (6 x 6, CEIL 2.8, door gap
x -1..+1 in the south wall) — the Background3D camera preset and
the .tscn lights are tuned to it. Windows are REAL OPENINGS with
cedar frames + mullions, no glass, per the playbook no-transparency
rule — and the bedroom window gets NO CURTAIN (vol7_ch1 canon,
explicit). Kerosene fixtures are geometry only; real Light3D stays
scene-side. Exterior: porch with railing + steps, firewood under
the eave, and gray-green cedars filling every opening.
"""
import os, sys
_BT = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
if _BT not in sys.path: sys.path.insert(0, _BT)
from _props import palette as P
from _props.geometry import clear_scene, make_box, make_cyl, export_glb
from _props.structure import make_floor, make_wall, make_ceiling, make_door_hinges

# ── Shell (footprint kept from the scaffold) ─────────────────────
ROOM_W = 6.0; ROOM_D = 6.0; CEIL = 2.8

# ── Cabin palette (cedar-and-iron, muted PNW) ────────────────────
COL_CEDAR_WALL = (0.55, 0.41, 0.28, 1.0)   # interior cedar planks
COL_CEDAR_DARK = (0.30, 0.22, 0.15, 1.0)   # trim / seams / rafters
COL_CEDAR_WARM = (0.62, 0.44, 0.28, 1.0)   # carved cedar (bowls)
COL_FLOOR      = (0.46, 0.34, 0.23, 1.0)   # fir floorboards
COL_FLOOR_SEAM = (0.26, 0.18, 0.12, 1.0)
COL_CEILING    = (0.50, 0.37, 0.25, 1.0)
COL_WOOD       = (0.48, 0.35, 0.22, 1.0)   # furniture walnut-ish
COL_WOOD_LT    = (0.64, 0.50, 0.33, 1.0)
COL_IRON       = (0.15, 0.14, 0.13, 1.0)   # stove / hardware
COL_COPPER     = (0.70, 0.44, 0.28, 1.0)   # the kettle
COL_BRASS      = (0.70, 0.57, 0.30, 1.0)
COL_EMBER      = (0.92, 0.44, 0.16, 1.0)   # banked firebox glow
COL_CREAM      = (0.90, 0.87, 0.80, 1.0)   # pottery / enamel
COL_ENAMEL_BLU = (0.42, 0.50, 0.56, 1.0)   # enamelware
COL_GLASSISH   = (0.74, 0.78, 0.76, 1.0)   # opaque jar-glass stand-in
COL_AMBER      = (0.62, 0.42, 0.22, 1.0)   # coffee / lamp fuel
COL_WICKER     = (0.60, 0.46, 0.28, 1.0)   # firewood basket
COL_BARK       = (0.34, 0.26, 0.18, 1.0)   # log rounds
COL_LOG_END    = (0.72, 0.60, 0.42, 1.0)   # split-wood end grain
COL_STONE      = (0.48, 0.47, 0.44, 1.0)   # hearth pad
COL_STONE_DK   = (0.36, 0.35, 0.33, 1.0)
COL_WOOL_A     = (0.58, 0.30, 0.22, 1.0)   # armchair rust wool
COL_WOOL_B     = (0.44, 0.51, 0.44, 1.0)   # armchair sage wool
COL_RAINCOAT   = (0.38, 0.36, 0.26, 1.0)   # wax canvas
COL_CROW       = (0.10, 0.10, 0.13, 1.0)
COL_PLANT      = (0.36, 0.47, 0.32, 1.0)   # rosemary
COL_CEDAR_FOL  = (0.30, 0.40, 0.33, 1.0)   # gray-green cedar canopy
COL_CEDAR_FOL2 = (0.26, 0.35, 0.28, 1.0)
COL_TRUNK      = (0.32, 0.24, 0.17, 1.0)
COL_EARTH      = (0.28, 0.24, 0.18, 1.0)   # wet forest floor
COL_DECK       = (0.40, 0.31, 0.22, 1.0)   # weathered porch boards
# Pendleton stripes (the Washougal mill pattern — three blankets:
# bed / daybed throw / armchair fold, vol7_ch1_morning)
PENDLETON = [
    (0.58, 0.30, 0.22, 1.0),   # rust
    (0.34, 0.48, 0.46, 1.0),   # teal
    (0.90, 0.87, 0.80, 1.0),   # cream
    (0.22, 0.20, 0.18, 1.0),   # charcoal
]
CHAIR_TINTS = [COL_WOOD, COL_WOOD_LT, COL_CEDAR_DARK, (0.52, 0.34, 0.20, 1.0)]

PAL_WALL = {"wall": COL_CEDAR_WALL, "baseboard": COL_CEDAR_DARK}

TABLE_X, TABLE_Y = -0.35, 2.85     # the small wooden table
STOVE_X, STOVE_Y = 0.80, 5.45      # the woodstove (hearth-center)


# ═════════════════════════════════════════════════════════════════
# Local helpers (deterministic, axis-aligned)
# ═════════════════════════════════════════════════════════════════
_DIRS = {'N': (0.0, 1.0), 'S': (0.0, -1.0), 'E': (1.0, 0.0), 'W': (-1.0, 0.0)}

def _chair(prefix, cx, cy, facing, tint):
    """Plain cabin chair. `facing` is the sitter's direction."""
    dx, dy = _DIRS[facing]
    make_box(f"{prefix}_Seat", (cx, cy, 0.45), (0.40, 0.40, 0.04), tint)
    for li, (sx, sy) in enumerate([(-1, -1), (+1, -1), (-1, +1), (+1, +1)]):
        make_cyl(f"{prefix}_Leg_{li}", (cx + sx * 0.16, cy + sy * 0.16, 0.225),
                 0.018, 0.45, COL_CEDAR_DARK)
    bx, by = cx - dx * 0.19, cy - dy * 0.19
    for pi, sgn in enumerate((-1, +1)):
        px = bx + (sgn * 0.16 if dx == 0 else 0.0)
        py = by + (sgn * 0.16 if dy == 0 else 0.0)
        make_cyl(f"{prefix}_BackPost_{pi}", (px, py, 0.675), 0.016, 0.45, tint)
    slat_sz = (0.36, 0.03, 0.09) if dx == 0 else (0.03, 0.36, 0.09)
    for si, sz_z in enumerate((0.72, 0.86)):
        make_box(f"{prefix}_Slat_{si}", (bx, by, sz_z), slat_sz, tint)

def _armchair(prefix, cx, cy, facing, tint):
    """Wool-upholstered armchair (two in the main room, vol7_ch1)."""
    dx, dy = _DIRS[facing]
    make_box(f"{prefix}_Base", (cx, cy, 0.22), (0.62, 0.62, 0.30), tint)
    make_box(f"{prefix}_Cushion", (cx + dx * 0.05, cy + dy * 0.05, 0.42),
             (0.50 + abs(dx) * 0.02, 0.50 + abs(dy) * 0.02, 0.12), tint)
    bx, by = cx - dx * 0.24, cy - dy * 0.24
    bsz = (0.16, 0.62, 0.60) if dx != 0 else (0.62, 0.16, 0.60)
    make_box(f"{prefix}_Back", (bx, by, 0.62), bsz, tint)
    for ai, sgn in enumerate((-1, +1)):
        ax = cx + (sgn * 0.30 if dx == 0 else 0.0)
        ay = cy + (sgn * 0.30 if dy == 0 else 0.0)
        asz = (0.58, 0.12, 0.26) if dx == 0 else (0.12, 0.58, 0.26)
        make_box(f"{prefix}_Arm_{ai}", (ax, ay, 0.50), asz, tint)
    for fi, (sx, sy) in enumerate([(-1, -1), (+1, -1), (-1, +1), (+1, +1)]):
        make_cyl(f"{prefix}_Foot_{fi}", (cx + sx * 0.24, cy + sy * 0.24, 0.035),
                 0.022, 0.07, COL_CEDAR_DARK)

def _pendleton(prefix, center, size, axis='X'):
    """Wool blanket slab + mill-pattern stripes on the top face."""
    cx, cy, cz = center
    sx, sy, sz = size
    make_box(f"{prefix}_Body", center, size, PENDLETON[0])
    n = 4
    for si in range(n):
        tint = PENDLETON[(si + 1) % len(PENDLETON)]
        if axis == 'X':
            px = cx - sx / 2.0 + (si + 0.5) * sx / n
            make_box(f"{prefix}_Stripe_{si}", (px, cy, cz + sz / 2.0 + 0.004),
                     (sx / n * 0.55, sy * 0.96, 0.006), tint)
        else:
            py = cy - sy / 2.0 + (si + 0.5) * sy / n
            make_box(f"{prefix}_Stripe_{si}", (cx, py, cz + sz / 2.0 + 0.004),
                     (sx * 0.96, sy / n * 0.55, 0.006), tint)

def _bowl(prefix, cx, cy, base_z, r=0.085, tint=COL_CEDAR_WARM):
    """Carved cedar bowl — Olaf's hand (vol7_ch10 / ch19)."""
    make_cyl(f"{prefix}_Body", (cx, cy, base_z + 0.028), r, 0.056, tint, segments=12)
    make_cyl(f"{prefix}_Well", (cx, cy, base_z + 0.058), r * 0.78, 0.004,
             COL_CEDAR_DARK, segments=12)

def _enamel_mug(prefix, cx, cy, base_z, tint=COL_ENAMEL_BLU):
    make_cyl(f"{prefix}_Body", (cx, cy, base_z + 0.048), 0.038, 0.095, tint)
    make_box(f"{prefix}_Handle", (cx + 0.048, cy, base_z + 0.050),
             (0.016, 0.014, 0.05), tint)

def _kerosene_table_lamp(prefix, cx, cy, base_z):
    """The kerosene lamp beside which the small table sits
    (vol7_ch1_morning — unlit in the gray morning; lit ch19)."""
    make_cyl(f"{prefix}_Base", (cx, cy, base_z + 0.015), 0.055, 0.03, COL_BRASS, segments=12)
    make_cyl(f"{prefix}_Stem", (cx, cy, base_z + 0.055), 0.016, 0.05, COL_BRASS)
    make_cyl(f"{prefix}_Font", (cx, cy, base_z + 0.125), 0.058, 0.09, COL_AMBER, segments=12)
    make_cyl(f"{prefix}_Collar", (cx, cy, base_z + 0.180), 0.030, 0.02, COL_BRASS)
    make_cyl(f"{prefix}_Knob", (cx + 0.045, cy, base_z + 0.175), 0.012, 0.024,
             COL_BRASS, axis='X')
    make_cyl(f"{prefix}_Chimney", (cx, cy, base_z + 0.285), 0.034, 0.19,
             COL_GLASSISH, segments=12)

def _cedar_tree(prefix, cx, cy, base_z, scale):
    """Stylized western redcedar — trunk + stacked canopy tiers
    (round geometry, never boxes). Gray-green per vol7_ch1."""
    s = scale
    make_cyl(f"{prefix}_Trunk", (cx, cy, base_z + 0.75 * s), 0.10 * s, 1.5 * s,
             COL_TRUNK, segments=8)
    tiers = [(1.10, 1.35), (0.88, 2.20), (0.62, 3.00), (0.38, 3.70)]
    for ti, (tr, tz) in enumerate(tiers):
        tint = COL_CEDAR_FOL if ti % 2 == 0 else COL_CEDAR_FOL2
        make_cyl(f"{prefix}_Tier_{ti}", (cx, cy, base_z + tz * s), tr * s, 0.85 * s,
                 tint, segments=8)
    make_cyl(f"{prefix}_Tip", (cx, cy, base_z + 4.35 * s), 0.16 * s, 0.55 * s,
             COL_CEDAR_FOL2, segments=8)


# ═════════════════════════════════════════════════════════════════
# SHELL — scaffold footprint kept: 6 x 6, CEIL 2.8, door gap
# x -1..+1 in the south wall. Openings carved for the south-facing
# window (main room, vol7_ch1) and the bedroom window in the west
# wall. Plank walls, fir floor, plank ceiling with cedar rafters.
# ═════════════════════════════════════════════════════════════════
def build_shell():
    make_floor("Floor", (0.0, ROOM_D / 2.0, 0.0), size_x=ROOM_W + 0.4, size_y=ROOM_D + 0.4,
               palette={"vinyl": COL_FLOOR, "seam": COL_FLOOR_SEAM})
    # East wall — solid (daybed / desk / cold-box live here)
    make_wall("Wall_E", (+ROOM_W / 2.0, ROOM_D / 2.0, 0), length=ROOM_D + 0.4, height=CEIL,
              axis='Y', palette=PAL_WALL, baseboard_face_sign=-1)
    # West wall — bedroom window opening y 4.5..5.6 (sill 0.95,
    # head 2.05) above the bed. NO CURTAIN — vol7_ch1 canon: the
    # window has not had one in three summers and never gets one.
    make_wall("Wall_W_S", (-ROOM_W / 2.0, 2.15, 0), length=4.70, height=CEIL,
              axis='Y', palette=PAL_WALL, baseboard_face_sign=+1)
    make_wall("Wall_W_N", (-ROOM_W / 2.0, 5.90, 0), length=0.60, height=CEIL,
              axis='Y', palette=PAL_WALL, baseboard_face_sign=+1)
    make_box("Wall_W_SillFill", (-ROOM_W / 2.0, 5.05, 0.475), (0.20, 1.10, 0.95),
             COL_CEDAR_WALL)
    make_box("Wall_W_HeadFill", (-ROOM_W / 2.0, 5.05, 2.425), (0.20, 1.10, 0.75),
             COL_CEDAR_WALL)
    # North wall — solid (stove heat shield, kitchen shelves)
    make_wall("Wall_N", (0.0, ROOM_D, 0), length=ROOM_W + 0.4, height=CEIL,
              axis='X', palette=PAL_WALL, baseboard_face_sign=-1)
    # South wall — door gap x -1..+1 kept from the scaffold; window
    # opening x 1.5..2.7 (sill 0.85, head 2.15) = the south-facing
    # window Lena watches the rain and the porch through.
    make_wall("Wall_S_W", (-(ROOM_W / 4.0 + 0.5), 0.0, 0), length=ROOM_W / 2.0 - 1.0,
              height=CEIL, axis='X', palette=PAL_WALL, baseboard_face_sign=+1)
    make_box("Wall_S_E_PierW", (1.25, 0.0, CEIL / 2.0), (0.50, 0.20, CEIL), COL_CEDAR_WALL)
    make_box("Wall_S_E_PierE", (2.85, 0.0, CEIL / 2.0), (0.30, 0.20, CEIL), COL_CEDAR_WALL)
    make_box("Wall_S_E_SillFill", (2.10, 0.0, 0.425), (1.20, 0.20, 0.85), COL_CEDAR_WALL)
    make_box("Wall_S_E_HeadFill", (2.10, 0.0, 2.475), (1.20, 0.20, 0.65), COL_CEDAR_WALL)
    make_box("Wall_S_E_Base", (2.10, 0.16, 0.08), (1.60, 0.06, 0.16), COL_CEDAR_DARK)
    make_box("Wall_S_AboveDoor", (0.0, 0.0, CEIL - 0.30), (2.0, 0.20, 0.60), COL_CEDAR_WALL)
    # Ceiling — plank, no drop grid, with exposed cedar rafters
    make_ceiling("Ceil", (0.0, ROOM_D / 2.0, CEIL), size_x=ROOM_W + 0.4, size_y=ROOM_D + 0.4,
                 palette={"tile": COL_CEILING, "grid": COL_CEDAR_DARK},
                 with_grid=False, with_stains=False)
    for ri, ry in enumerate((1.5, 3.0, 4.5)):
        make_box(f"Rafter_{ri}", (0.0, ry, CEIL - 0.09), (ROOM_W + 0.4, 0.14, 0.18),
                 COL_CEDAR_DARK)
    # Horizontal plank seams on the interior wall faces
    for zi, sz in enumerate((0.55, 1.10, 1.65, 2.20)):
        make_box(f"PlankSeam_N_{zi}", (0.0, ROOM_D - 0.095, sz),
                 (ROOM_W + 0.3, 0.005, 0.015), COL_CEDAR_DARK)
        make_box(f"PlankSeam_E_{zi}", (ROOM_W / 2.0 - 0.095, ROOM_D / 2.0, sz),
                 (0.005, ROOM_D + 0.3, 0.015), COL_CEDAR_DARK)
        make_box(f"PlankSeam_W_{zi}", (-ROOM_W / 2.0 + 0.095, 2.15, sz),
                 (0.005, 4.60, 0.015), COL_CEDAR_DARK)


# ═════════════════════════════════════════════════════════════════
# BEDROOM — NW corner behind a plank partition; the short hallway
# is the doorway nook (vol7_ch1: "left the small bedroom and
# crossed the short hallway to the main room"). Bed along the west
# wall UNDER THE CURTAINLESS WINDOW; Pendleton blanket #1.
# ═════════════════════════════════════════════════════════════════
def build_bedroom():
    # Partition: south run (doorway gap x -2.2..-1.42) + east run
    make_box("BedroomWall_S", (-2.60, 3.90, CEIL / 2.0), (0.80, 0.12, CEIL), COL_CEDAR_WALL)
    make_box("BedroomWall_S_Header", (-1.81, 3.90, 2.45), (0.78, 0.12, 0.70), COL_CEDAR_WALL)
    make_box("BedroomWall_E", (-1.36, 5.05, CEIL / 2.0), (0.12, 2.30, CEIL), COL_CEDAR_WALL)
    for sgn, jx in ((-1, -2.24), (+1, -1.38)):
        make_box(f"BedroomDoor_Jamb_{sgn:+d}", (jx, 3.90, 1.05), (0.08, 0.16, 2.10),
                 COL_CEDAR_DARK)
    make_box("BedroomDoor_HeadTrim", (-1.81, 3.90, 2.14), (0.94, 0.16, 0.08), COL_CEDAR_DARK)
    # Bedroom window frame + mullions in the west-wall opening.
    # NO CURTAIN — hard canon (vol7_ch1_morning).
    wx = -ROOM_W / 2.0
    make_box("BedWin_Sill", (wx, 5.05, 0.935), (0.26, 1.22, 0.06), COL_CEDAR_DARK)
    make_box("BedWin_Ledge", (wx + 0.14, 5.05, 0.975), (0.14, 1.10, 0.03), COL_CEDAR_DARK)
    make_box("BedWin_Head", (wx, 5.05, 2.065), (0.26, 1.22, 0.06), COL_CEDAR_DARK)
    for sgn in (-1, +1):
        make_box(f"BedWin_Jamb_{sgn:+d}", (wx, 5.05 + sgn * 0.58, 1.50),
                 (0.26, 0.06, 1.10), COL_CEDAR_DARK)
    make_box("BedWin_MullV", (wx, 5.05, 1.50), (0.16, 0.05, 1.06), COL_CEDAR_DARK)
    make_box("BedWin_MullH", (wx, 5.05, 1.50), (0.16, 1.06, 0.05), COL_CEDAR_DARK)
    # The bed — under the window, head at the north wall
    make_box("Bed_Frame", (-2.42, 5.05, 0.18), (1.00, 1.90, 0.16), COL_WOOD)
    for li, (sx, sy) in enumerate([(-1, -1), (+1, -1), (-1, +1), (+1, +1)]):
        make_cyl(f"Bed_Leg_{li}", (-2.42 + sx * 0.44, 5.05 + sy * 0.88, 0.06),
                 0.028, 0.12, COL_CEDAR_DARK)
    make_box("Bed_Headboard", (-2.42, 5.94, 0.55), (1.00, 0.06, 0.65), COL_WOOD)
    make_box("Bed_Mattress", (-2.42, 5.05, 0.335), (0.94, 1.84, 0.15), COL_CREAM)
    # Pendleton blanket #1 (Washougal mill, vol7_ch1_morning)
    _pendleton("Bed_Pendleton", (-2.42, 4.85, 0.435), (0.96, 1.36, 0.06), axis='Y')
    make_box("Bed_Pillow", (-2.42, 5.72, 0.45), (0.62, 0.34, 0.10), COL_CREAM)
    # Nightstand stool + candle + a book
    make_cyl("Nightstand_Top", (-1.72, 5.72, 0.42), 0.17, 0.035, COL_WOOD_LT, segments=12)
    for li in range(3):
        ang = [(-0.10, -0.10), (0.12, -0.06), (0.0, 0.12)][li]
        make_cyl(f"Nightstand_Leg_{li}", (-1.72 + ang[0], 5.72 + ang[1], 0.20),
                 0.016, 0.40, COL_CEDAR_DARK)
    make_cyl("Nightstand_CandleDish", (-1.76, 5.70, 0.447), 0.045, 0.014, COL_BRASS)
    make_cyl("Nightstand_Candle", (-1.76, 5.70, 0.494), 0.014, 0.08, COL_CREAM)
    make_box("Nightstand_Book", (-1.66, 5.78, 0.452), (0.13, 0.18, 0.025),
             (0.40, 0.30, 0.24, 1.0))
    # Rag rug beside the bed
    for ri, (rr, tint) in enumerate([(0.34, COL_WOOL_A), (0.24, COL_CREAM),
                                     (0.13, COL_WOOL_B)]):
        make_cyl(f"BedRug_{ri}", (-1.70, 4.65, 0.004 + ri * 0.004), rr, 0.006,
                 tint, segments=12)


# ═════════════════════════════════════════════════════════════════
# WOODSTOVE — the hearth-center. Banked firebox (vol7 music:
# "damper-pull tick + a log settling at the back of the firebox"),
# the dented copper kettle, the 1973 skillet, the wire toast rack,
# the cedar basket Tem banks the stove from (vol7_ch4_alone).
# ═════════════════════════════════════════════════════════════════
def build_woodstove():
    sx, sy = STOVE_X, STOVE_Y
    # Stone hearth pad + wall heat shield
    make_box("Hearth_Pad", (sx, sy - 0.10, 0.03), (1.30, 1.15, 0.06), COL_STONE)
    for ti, (tx, ty) in enumerate([(-0.38, -0.30), (0.10, -0.42), (0.42, -0.18),
                                   (-0.10, 0.05), (0.35, 0.22)]):
        make_box(f"Hearth_Stone_{ti}", (sx + tx, sy + ty - 0.10, 0.062),
                 (0.30, 0.24, 0.008), COL_STONE_DK)
    make_box("HeatShield", (sx, ROOM_D - 0.115, 1.05), (1.00, 0.03, 0.80), P.METAL_STEEL)
    # Cast-iron box stove on legs
    for li, (lx, ly) in enumerate([(-1, -1), (+1, -1), (-1, +1), (+1, +1)]):
        make_cyl(f"Stove_Leg_{li}", (sx + lx * 0.24, sy + ly * 0.18, 0.12),
                 0.025, 0.18, COL_IRON)
    make_box("Stove_Body", (sx, sy, 0.475), (0.62, 0.50, 0.55), COL_IRON)
    make_box("Stove_TopPlate", (sx, sy, 0.765), (0.68, 0.56, 0.03), COL_IRON)
    make_cyl("Stove_LidRing", (sx - 0.14, sy, 0.783), 0.085, 0.012, COL_IRON, segments=12)
    # Firebox door on the south face — hinges, handle, draft vents,
    # a banked-ember glow behind the slots
    make_box("Stove_Door", (sx, sy - 0.265, 0.50), (0.34, 0.03, 0.34), COL_IRON)
    for hi in range(2):
        make_cyl(f"Stove_DoorHinge_{hi}", (sx - 0.155, sy - 0.27, 0.40 + hi * 0.20),
                 0.014, 0.05, COL_IRON)
    make_cyl("Stove_Handle", (sx + 0.14, sy - 0.29, 0.50), 0.014, 0.09, COL_BRASS, axis='X')
    make_box("Stove_Ember", (sx, sy - 0.278, 0.385), (0.22, 0.005, 0.035), COL_EMBER)
    for vi in range(3):
        make_box(f"Stove_Vent_{vi}", (sx - 0.07 + vi * 0.07, sy - 0.283, 0.385),
                 (0.02, 0.006, 0.045), COL_IRON)
    # Stovepipe up through the ceiling, with the damper pull
    make_cyl("Stovepipe", (sx, sy + 0.08, 1.79), 0.080, 2.02, COL_IRON, segments=12)
    make_cyl("Stovepipe_DamperPull", (sx + 0.09, sy + 0.08, 1.55), 0.010, 0.10,
             COL_BRASS, axis='X')
    make_cyl("Stovepipe_Collar", (sx, sy + 0.08, 2.77), 0.125, 0.05, COL_IRON, segments=12)
    # The copper kettle — with the dent nobody talks about (vol7_ch1)
    make_cyl("Kettle_Body", (sx - 0.14, sy, 0.865), 0.100, 0.155, COL_COPPER, segments=12)
    make_box("Kettle_Dent", (sx - 0.045, sy + 0.045, 0.86), (0.035, 0.035, 0.06),
             (0.55, 0.33, 0.20, 1.0))
    make_cyl("Kettle_Lid", (sx - 0.14, sy, 0.950), 0.068, 0.02, COL_COPPER, segments=12)
    make_cyl("Kettle_Knob", (sx - 0.14, sy, 0.972), 0.016, 0.025, COL_CEDAR_DARK)
    make_box("Kettle_SpoutA", (sx - 0.035, sy, 0.885), (0.07, 0.020, 0.020), COL_COPPER)
    make_box("Kettle_SpoutB", (sx + 0.005, sy, 0.915), (0.035, 0.017, 0.017), COL_COPPER)
    for bi, bx in enumerate((-0.205, -0.075)):
        make_box(f"Kettle_Bail_{bi}", (sx + bx, sy, 1.010), (0.014, 0.014, 0.10), COL_BRASS)
    make_box("Kettle_BailTop", (sx - 0.14, sy, 1.062), (0.145, 0.016, 0.016), COL_BRASS)
    # The small wire rack toast is made on (vol7_ch1_morning)
    for wi in range(4):
        make_box(f"ToastRack_Wire_{wi}", (sx + 0.14 + wi * 0.045, sy - 0.10, 0.790),
                 (0.008, 0.22, 0.008), P.METAL_STEEL)
    make_box("ToastRack_Cross", (sx + 0.21, sy - 0.10, 0.802), (0.16, 0.008, 0.008),
             P.METAL_STEEL)
    # The 1973 cast-iron skillet, hung on the north wall
    make_cyl("Skillet_Pan", (-0.05, ROOM_D - 0.135, 1.32), 0.125, 0.030, COL_IRON,
             axis='Y', segments=12)
    make_box("Skillet_Handle", (-0.05, ROOM_D - 0.135, 1.15), (0.035, 0.025, 0.22), COL_IRON)
    make_cyl("Skillet_Nail", (-0.05, ROOM_D - 0.115, 1.46), 0.008, 0.05, COL_IRON, axis='Y')
    # The cedar basket beside the stove (Tem banks from it)
    make_cyl("WoodBasket_Body", (0.02, 5.42, 0.20), 0.235, 0.40, COL_WICKER, segments=12)
    make_cyl("WoodBasket_Rim", (0.02, 5.42, 0.405), 0.250, 0.03, COL_CEDAR_DARK, segments=12)
    for gi, (gx, gy) in enumerate([(-0.08, -0.05), (0.07, 0.06), (0.00, -0.10)]):
        make_cyl(f"WoodBasket_Log_{gi}", (0.02 + gx, 5.42 + gy, 0.36), 0.048, 0.30,
                 COL_BARK)
        make_cyl(f"WoodBasket_LogEnd_{gi}", (0.02 + gx, 5.42 + gy, 0.512), 0.040, 0.006,
                 COL_LOG_END)
    # Poker + ash shovel on a wall rail
    make_box("StoveTool_Rail", (1.55, ROOM_D - 0.105, 1.15), (0.30, 0.03, 0.04), COL_IRON)
    make_cyl("StoveTool_Poker", (1.48, ROOM_D - 0.13, 0.78), 0.008, 0.72, COL_IRON)
    make_box("StoveTool_PokerHook", (1.48, ROOM_D - 0.13, 1.15), (0.02, 0.02, 0.05), COL_IRON)
    make_cyl("StoveTool_Shovel", (1.63, ROOM_D - 0.13, 0.80), 0.008, 0.68, COL_IRON)
    make_box("StoveTool_ShovelBlade", (1.63, ROOM_D - 0.13, 0.50), (0.07, 0.02, 0.10), COL_IRON)
    # Braided rug between table and hearth
    for ri, (rr, tint) in enumerate([(0.72, COL_WOOL_A), (0.52, COL_CREAM),
                                     (0.30, COL_WOOL_B)]):
        make_cyl(f"HearthRug_{ri}", (0.05, 4.40, 0.004 + ri * 0.004), rr, 0.006,
                 tint, segments=16)


# ═════════════════════════════════════════════════════════════════
# KITCHEN — NE corner. Plank counter with the camp stove + metal
# cone filter (the coffee setup since 2031, vol7_ch1), wash basin,
# bread on the cutting board, the pottery butter dish, pantry
# shelves (mint tea for seven — vol7 music vol7_four_bowls), the
# wooden cold-box with the egg shelf beside it (vol7_ch1).
# ═════════════════════════════════════════════════════════════════
def build_kitchen():
    # Counter run along the north wall
    make_box("Counter_Body", (2.35, 5.55, 0.44), (1.35, 0.55, 0.88), COL_WOOD)
    make_box("Counter_Top", (2.35, 5.55, 0.905), (1.45, 0.62, 0.05), COL_WOOD_LT)
    make_box("Counter_Kick", (2.35, 5.265, 0.06), (1.35, 0.02, 0.12), COL_CEDAR_DARK)
    for pi in range(3):
        make_box(f"Counter_Plank_{pi}", (1.93 + pi * 0.42, 5.272, 0.50),
                 (0.36, 0.012, 0.72), COL_WOOD_LT if pi % 2 == 0 else COL_WOOD)
    # Camp stove (green two-burner) + the metal cone + carafe
    make_box("CampStove_Body", (1.95, 5.55, 0.985), (0.36, 0.28, 0.11), COL_WOOL_B)
    for bi, bx in enumerate((1.87, 2.03)):
        make_cyl(f"CampStove_Burner_{bi}", (bx, 5.55, 1.046), 0.055, 0.012, COL_IRON)
        make_cyl(f"CampStove_Knob_{bi}", (bx, 5.40, 0.985), 0.016, 0.025,
                 COL_IRON, axis='Y')
    make_cyl("ConeFilter_Carafe", (2.28, 5.62, 0.99), 0.052, 0.12, COL_AMBER, segments=12)
    make_cyl("ConeFilter_Lower", (2.28, 5.62, 1.068), 0.036, 0.03, P.METAL_STEEL)
    make_cyl("ConeFilter_Upper", (2.28, 5.62, 1.115), 0.058, 0.06, P.METAL_STEEL)
    # Wash basin (no plumbing — enamel jug beside it)
    make_box("Basin_Shell", (2.78, 5.52, 0.885), (0.36, 0.32, 0.10), P.METAL_STEEL,
             open_faces={'+Z'})
    make_box("Basin_Floor", (2.78, 5.52, 0.845), (0.34, 0.30, 0.01), (0.44, 0.46, 0.48, 1.0))
    make_cyl("WaterJug_Body", (2.52, 5.75, 1.045), 0.075, 0.28, COL_CREAM, segments=12)
    make_cyl("WaterJug_Neck", (2.52, 5.75, 1.20), 0.042, 0.04, COL_CREAM)
    make_box("WaterJug_Handle", (2.60, 5.75, 1.10), (0.016, 0.014, 0.14), COL_ENAMEL_BLU)
    # Cutting board + bread + the pottery butter dish (vol7_ch1)
    make_box("CuttingBoard", (2.45, 5.38, 0.94), (0.32, 0.22, 0.02), COL_WOOD_LT)
    make_box("BreadLoaf", (2.40, 5.40, 0.99), (0.17, 0.12, 0.08), (0.72, 0.54, 0.32, 1.0))
    for si in range(2):
        make_box(f"BreadSlice_{si}", (2.55, 5.34 + si * 0.045, 0.958),
                 (0.10, 0.018, 0.075), (0.86, 0.74, 0.52, 1.0))
    make_cyl("ButterDish_Base", (2.10, 5.36, 0.917), 0.055, 0.014, COL_CREAM, segments=12)
    make_cyl("ButterDish_Dome", (2.10, 5.36, 0.947), 0.045, 0.05, COL_CREAM, segments=12)
    make_cyl("ButterDish_Knob", (2.10, 5.36, 0.980), 0.012, 0.018, COL_CREAM)
    # Under-counter pots
    make_cyl("Counter_DutchOven", (2.35, 5.50, 0.14), 0.13, 0.16, COL_IRON, segments=12)
    make_cyl("Counter_Pot", (2.70, 5.50, 0.12), 0.095, 0.12, P.METAL_STEEL, segments=12)
    # Pantry shelves on the north wall
    for si, sz in enumerate((1.52, 1.88)):
        make_box(f"PantryShelf_{si}", (2.35, 5.78, sz), (1.30, 0.22, 0.03), COL_WOOD)
        for ki, sgn in enumerate((-1, +1)):
            make_box(f"PantryShelf_{si}_Bracket_{ki}", (2.35 + sgn * 0.55, 5.86, sz - 0.06),
                     (0.03, 0.10, 0.10), COL_CEDAR_DARK)
    # Lower shelf: jars (beans / flour / MINT TEA for seven / rice),
    # tins, the salt-cod package from Per's mother (vol7_ch19)
    jar_fills = [(0.52, 0.40, 0.26, 1.0), (0.88, 0.84, 0.74, 1.0),
                 (0.38, 0.52, 0.34, 1.0),   # the mint tea
                 (0.80, 0.72, 0.55, 1.0)]
    for ji, fill in enumerate(jar_fills):
        jx = 1.85 + ji * 0.22
        make_cyl(f"PantryJar_{ji}_Glass", (jx, 5.76, 1.615), 0.055, 0.16,
                 COL_GLASSISH, segments=12)
        make_cyl(f"PantryJar_{ji}_Fill", (jx, 5.76, 1.59), 0.046, 0.09, fill, segments=12)
        make_cyl(f"PantryJar_{ji}_Lid", (jx, 5.76, 1.70), 0.058, 0.018, COL_CEDAR_DARK)
    for ti in range(2):
        make_cyl(f"PantryTin_{ti}", (2.80 + ti * 0.14, 5.78, 1.60), 0.048, 0.13,
                 COL_ENAMEL_BLU if ti == 0 else P.METAL_STEEL)
    make_box("SaltCod_Package", (2.62, 5.78, 1.565), (0.16, 0.10, 0.06), P.PAPER_AGED)
    make_box("SaltCod_Twine", (2.62, 5.78, 1.598), (0.17, 0.02, 0.012), P.TWINE)
    # Upper shelf: teapot (mint tea for seven), enamel mugs, plates
    make_cyl("Teapot_Body", (1.92, 5.78, 1.965), 0.075, 0.13, COL_ENAMEL_BLU, segments=12)
    make_cyl("Teapot_Lid", (1.92, 5.78, 2.036), 0.045, 0.02, COL_ENAMEL_BLU)
    make_cyl("Teapot_Knob", (1.92, 5.78, 2.056), 0.012, 0.02, COL_CEDAR_DARK)
    make_box("Teapot_Spout", (2.00, 5.78, 1.99), (0.07, 0.018, 0.018), COL_ENAMEL_BLU)
    make_box("Teapot_Handle", (1.83, 5.78, 1.99), (0.016, 0.014, 0.09), COL_ENAMEL_BLU)
    for mi in range(4):
        tint = COL_ENAMEL_BLU if mi % 2 == 0 else COL_CREAM
        _enamel_mug(f"ShelfMug_{mi}", 2.16 + mi * 0.16, 5.78, 1.895, tint)
    for pi in range(3):
        make_cyl(f"PlateStack_{pi}", (2.88, 5.78, 1.905 + pi * 0.018), 0.075, 0.014,
                 COL_CREAM, segments=12)
    # The cold-box (wooden icebox, east wall) + the small shelf by
    # it where the eggs live (vol7_ch1_morning)
    make_box("Icebox_Body", (2.60, 4.55, 0.525), (0.60, 0.55, 1.05), COL_WOOD)
    make_box("Icebox_Top", (2.60, 4.55, 1.065), (0.64, 0.59, 0.03), COL_WOOD_LT)
    for di, dz in enumerate((0.72, 0.28)):
        make_box(f"Icebox_Door_{di}", (2.285, 4.55, dz), (0.03, 0.44, 0.34), COL_WOOD_LT)
        make_box(f"Icebox_Latch_{di}", (2.265, 4.38, dz), (0.02, 0.03, 0.06), COL_BRASS)
        make_cyl(f"Icebox_Hinge_{di}", (2.285, 4.74, dz), 0.012, 0.06, COL_BRASS)
    make_box("EggShelf", (2.81, 4.55, 1.42), (0.18, 0.55, 0.03), COL_WOOD)
    make_box("EggShelf_Bracket", (2.86, 4.55, 1.34), (0.08, 0.03, 0.13), COL_CEDAR_DARK)
    make_cyl("EggBowl", (2.80, 4.44, 1.462), 0.075, 0.055, COL_CREAM, segments=12)
    for ei in range(4):
        ex, ey = [(-0.03, -0.02), (0.03, -0.02), (0.0, 0.03), (0.0, -0.05)][ei]
        make_cyl(f"Egg_{ei}", (2.80 + ex, 4.44 + ey, 1.505), 0.020, 0.032, COL_CREAM)
    make_box("EggBasketCloth", (2.82, 4.70, 1.445), (0.10, 0.12, 0.015), COL_WOOL_A)


# ═════════════════════════════════════════════════════════════════
# TABLE — the small wooden table beside the kerosene lamp. On it:
# the lamp, the John Frank novel, the clay dish of rosemary, three
# SCUMM sticks in waxed-paper sleeves (all vol7_ch1_morning), the
# FOUR CEDAR BOWLS facing the door + Brandon's notebook + the
# thumb-size carved cedar (vol7_ch19_cedar). The crow on the back
# of one of the chairs (vol7_ch19). Lantern hung from the rafter.
# ═════════════════════════════════════════════════════════════════
def build_table_zone():
    tx, ty = TABLE_X, TABLE_Y
    make_box("Table_Top", (tx, ty, 0.745), (1.30, 0.90, 0.04), COL_WOOD)
    make_box("Table_Apron", (tx, ty, 0.685), (1.14, 0.74, 0.08), COL_WOOD)
    for li, (sx, sy) in enumerate([(-1, -1), (+1, -1), (-1, +1), (+1, +1)]):
        make_cyl(f"Table_Leg_{li}", (tx + sx * 0.55, ty + sy * 0.35, 0.36),
                 0.028, 0.72, COL_CEDAR_DARK)
    # Four mismatched chairs — Tem / Lena / Kai / "the chair for
    # Per" (vol7_ch10)
    _chair("Chair_N", tx, ty + 0.72, 'S', CHAIR_TINTS[0])
    _chair("Chair_S", tx, ty - 0.72, 'N', CHAIR_TINTS[1])
    _chair("Chair_E", tx + 0.78, ty, 'W', CHAIR_TINTS[2])
    _chair("Chair_W", tx - 0.78, ty, 'E', CHAIR_TINTS[3])
    # The kerosene lamp (unlit at the gray hour; lit at ch19 dinner)
    _kerosene_table_lamp("TableLamp", tx - 0.42, ty + 0.22, 0.765)
    # The John Frank novel
    make_box("JohnFrankNovel", (tx + 0.05, ty + 0.28, 0.782), (0.14, 0.20, 0.035),
             (0.34, 0.42, 0.44, 1.0))
    make_box("JohnFrankNovel_Pages", (tx + 0.115, ty + 0.28, 0.782), (0.012, 0.19, 0.028),
             P.PAPER)
    # The small clay dish with the rosemary (burning since Saturday)
    make_cyl("RosemaryDish", (tx - 0.12, ty + 0.30, 0.777), 0.055, 0.024,
             (0.62, 0.42, 0.32, 1.0), segments=12)
    for ri in range(3):
        make_box(f"Rosemary_{ri}", (tx - 0.14 + ri * 0.025, ty + 0.29 + (ri % 2) * 0.02,
                 0.805), (0.012, 0.012, 0.05), COL_PLANT)
    # Three SCUMM sticks in waxed-paper sleeves (vol7_ch1_morning)
    for si in range(3):
        sx0 = tx + 0.30 + si * 0.005
        sy0 = ty - 0.02 - si * 0.075
        make_box(f"ScummStick_{si}_Sleeve", (sx0, sy0, 0.775), (0.15, 0.055, 0.018),
                 P.PAPER_AGED)
        make_box(f"ScummStick_{si}_End", (sx0 + 0.082, sy0, 0.775), (0.018, 0.03, 0.012),
                 COL_IRON)
    # THE FOUR BOWLS — warm on the table, facing the door
    # (vol7_ch19 / music vol7_four_bowls)
    for bi, (bx, by) in enumerate([(-0.28, -0.26), (-0.09, -0.30),
                                   (0.10, -0.26), (0.29, -0.30)]):
        _bowl(f"CedarBowl_{bi}", tx + bx, ty + by, 0.765)
    # Brandon's notebook + Olaf's thumb-size cedar (the open hand
    # holding the bell) beside the bowls (vol7_ch19_cedar)
    make_box("BrandonNotebook", (tx + 0.42, ty + 0.24, 0.777), (0.12, 0.16, 0.025),
             (0.26, 0.22, 0.18, 1.0))
    make_box("CedarPiece_Bell", (tx + 0.44, ty + 0.10, 0.772), (0.05, 0.03, 0.015),
             COL_CEDAR_WARM)
    # The crow — on the back of one of the chairs (vol7_ch19_cedar)
    cx, cy = tx, ty + 0.91          # top slat of Chair_N
    make_cyl("Crow_Body", (cx, cy, 0.965), 0.042, 0.12, COL_CROW, axis='X', segments=12)
    make_cyl("Crow_Head", (cx + 0.075, cy, 1.00), 0.030, 0.055, COL_CROW, axis='X')
    make_box("Crow_Beak", (cx + 0.12, cy, 0.995), (0.032, 0.013, 0.013),
             (0.24, 0.22, 0.20, 1.0))
    make_box("Crow_Tail", (cx - 0.085, cy, 0.985), (0.085, 0.032, 0.012), COL_CROW)
    for li, ly in enumerate((-0.02, +0.02)):
        make_cyl(f"Crow_Leg_{li}", (cx - 0.01, cy + ly, 0.925), 0.004, 0.05,
                 (0.24, 0.22, 0.20, 1.0))
    # Hanging kerosene lantern from the mid rafter over the table
    make_cyl("HangLantern_Hook", (tx, 3.0, 2.545), 0.016, 0.05, COL_IRON)
    make_cyl("HangLantern_Chain", (tx, 3.0, 2.36), 0.007, 0.32, COL_IRON)
    make_cyl("HangLantern_Cap", (tx, 3.0, 2.185), 0.055, 0.035, COL_IRON, segments=12)
    make_cyl("HangLantern_Chimney", (tx, 3.0, 2.10), 0.038, 0.14, COL_GLASSISH, segments=12)
    make_cyl("HangLantern_Font", (tx, 3.0, 1.995), 0.052, 0.07, COL_IRON, segments=12)


# ═════════════════════════════════════════════════════════════════
# WEST WALL — the SHELF ABOVE THE KEROSENE LAMP: Olaf's small cedar
# bowl (warm since July, vol7_ch4_finn) + the reader that has been
# on the shelf since '46 (vol7_ch10). A bracketed wall lamp with a
# reflector beneath the shelf carries the kerosene register.
# ═════════════════════════════════════════════════════════════════
def build_west_wall():
    wf = -ROOM_W / 2.0 + 0.10       # interior face -2.90
    make_box("LampShelf", (wf + 0.09, 2.90, 1.72), (0.18, 0.70, 0.03), COL_WOOD)
    for ki, sgn in enumerate((-1, +1)):
        make_box(f"LampShelf_Bracket_{ki}", (wf + 0.05, 2.90 + sgn * 0.28, 1.64),
                 (0.10, 0.03, 0.13), COL_CEDAR_DARK)
    # Olaf's bowl — the one Finn lifts and holds a long count
    _bowl("OlafBowl", wf + 0.10, 2.72, 1.735, r=0.070)
    # The reader, propped against the wall (on the shelf since '46)
    make_box("Reader", (wf + 0.045, 3.05, 1.83), (0.025, 0.13, 0.17),
             (0.20, 0.20, 0.22, 1.0))
    make_box("Reader_Screen", (wf + 0.059, 3.05, 1.84), (0.004, 0.105, 0.13),
             (0.55, 0.56, 0.52, 1.0))
    # Wall-mounted kerosene lamp with steel reflector, under the
    # shelf ("the shelf above the kerosene lamp", vol7_ch4_finn)
    make_box("WallLamp_Bracket", (wf + 0.035, 2.90, 1.22), (0.07, 0.04, 0.04), COL_IRON)
    make_cyl("WallLamp_Reflector", (wf + 0.015, 2.90, 1.42), 0.095, 0.015,
             P.METAL_STEEL, axis='X', segments=12)
    make_cyl("WallLamp_Font", (wf + 0.10, 2.90, 1.27), 0.045, 0.07, COL_AMBER, segments=12)
    make_cyl("WallLamp_Chimney", (wf + 0.10, 2.90, 1.385), 0.028, 0.14,
             COL_GLASSISH, segments=12)


# ═════════════════════════════════════════════════════════════════
# SEATING — the two armchairs (vol7_ch1: "two armchairs"), a side
# table, the daybed on the east wall where Kai slept (Pendleton
# throw #2, folded blanket #3 on an armchair), and the crow's
# perch Lena and Kai brought up (vol7_ch19_cedar).
# ═════════════════════════════════════════════════════════════════
def build_seating():
    _armchair("Armchair_A", -2.30, 3.35, 'E', COL_WOOL_A)
    _armchair("Armchair_B", -2.45, 1.80, 'N', COL_WOOL_B)
    # Pendleton #3 folded over Armchair_B's arm
    _pendleton("ArmchairFold_Pendleton", (-2.15, 1.80, 0.68), (0.14, 0.50, 0.10), axis='Y')
    make_cyl("SideTable_Top", (-2.62, 2.55, 0.50), 0.20, 0.035, COL_WOOD_LT, segments=12)
    make_cyl("SideTable_Column", (-2.62, 2.55, 0.26), 0.035, 0.46, COL_CEDAR_DARK)
    make_cyl("SideTable_Base", (-2.62, 2.55, 0.025), 0.13, 0.05, COL_CEDAR_DARK, segments=12)
    _enamel_mug("SideTable_Mug", -2.64, 2.57, 0.518, COL_CREAM)
    # The daybed (east wall) — frame, mattress, Kai's rumpled
    # blanket, pillow, Pendleton throw folded at the foot
    make_box("Daybed_Frame", (2.55, 1.90, 0.20), (0.80, 1.95, 0.14), COL_WOOD)
    for li, (sx, sy) in enumerate([(-1, -1), (+1, -1), (-1, +1), (+1, +1)]):
        make_cyl(f"Daybed_Leg_{li}", (2.55 + sx * 0.34, 1.90 + sy * 0.90, 0.065),
                 0.026, 0.13, COL_CEDAR_DARK)
    make_box("Daybed_Backrail", (2.92, 1.90, 0.62), (0.06, 1.95, 0.55), COL_WOOD)
    make_box("Daybed_Mattress", (2.55, 1.90, 0.345), (0.74, 1.89, 0.15), COL_CREAM)
    make_box("Daybed_Blanket", (2.55, 1.72, 0.445), (0.70, 1.10, 0.06),
             (0.48, 0.44, 0.36, 1.0))
    make_box("Daybed_BlanketRumple", (2.42, 1.32, 0.492), (0.36, 0.42, 0.05),
             (0.44, 0.40, 0.33, 1.0))
    make_box("Daybed_Pillow", (2.55, 2.68, 0.46), (0.52, 0.32, 0.10), COL_CREAM)
    _pendleton("Daybed_Pendleton", (2.55, 1.06, 0.455), (0.70, 0.40, 0.07), axis='X')
    # The crow's perch (brought up from Finn's apartment, ch19 —
    # the crow settled on the chair instead; the perch stands by
    # the daybed anyway)
    make_cyl("CrowPerch_Base", (2.42, 0.55, 0.02), 0.15, 0.04, COL_CEDAR_DARK, segments=12)
    make_cyl("CrowPerch_Pole", (2.42, 0.55, 0.62), 0.018, 1.16, COL_WOOD)
    make_cyl("CrowPerch_Crossbar", (2.42, 0.55, 1.21), 0.014, 0.40, COL_WOOD, axis='X')


# ═════════════════════════════════════════════════════════════════
# DESK — Eddvard's writing desk on the east wall; the drawer held
# Olaf's carved cedar for sixty-six years (vol7_ch19_cedar).
# ═════════════════════════════════════════════════════════════════
def build_desk():
    make_box("Desk_Top", (2.62, 3.50, 0.76), (0.56, 0.90, 0.035), COL_WOOD)
    for li, (sx, sy) in enumerate([(-1, -1), (+1, -1), (-1, +1), (+1, +1)]):
        make_box(f"Desk_Leg_{li}", (2.62 + sx * 0.24, 3.50 + sy * 0.41, 0.37),
                 (0.05, 0.05, 0.74), COL_WOOD)
    make_box("Desk_DrawerBank", (2.62, 3.50, 0.62), (0.52, 0.86, 0.24), COL_WOOD)
    for di, dy in enumerate((3.28, 3.72)):
        make_box(f"Desk_DrawerFace_{di}", (2.345, dy, 0.62), (0.03, 0.36, 0.18),
                 COL_WOOD_LT)
        make_cyl(f"Desk_Knob_{di}", (2.325, dy, 0.62), 0.016, 0.03, COL_BRASS, axis='X')
    make_box("Desk_Papers", (2.60, 3.62, 0.785), (0.24, 0.32, 0.012), P.PAPER_AGED)
    make_box("Desk_PapersTop", (2.58, 3.58, 0.796), (0.20, 0.28, 0.006), P.PAPER)
    make_cyl("Desk_Pencil", (2.56, 3.36, 0.784), 0.006, 0.14, COL_AMBER, axis='Y')


# ═════════════════════════════════════════════════════════════════
# DOOR ZONE — plank door (west leaf of the scaffold gap; east half
# stands open to the porch, the way Tem holds it), the thermometer
# nailed above the door in 1979, the coat pegs (Finn's wet coat),
# the wool-sock shelf by the door, boots, drip mat (vol7_ch1/ch4).
# ═════════════════════════════════════════════════════════════════
def build_door_zone():
    # Jambs + head trim inside the scaffold's x -1..+1 gap
    for sgn in (-1, +1):
        make_box(f"Door_Jamb_{sgn:+d}", (sgn * 0.96, 0.0, 1.10), (0.08, 0.16, 2.20),
                 COL_CEDAR_DARK)
    make_box("Door_HeadTrim", (0.0, 0.0, 2.24), (2.00, 0.16, 0.08), COL_CEDAR_DARK)
    # Plank door leaf (west half; the east half of the opening is
    # left clear — door-standing-open canon + camera sightline)
    make_box("Door_Leaf", (-0.48, 0.0, 1.06), (0.92, 0.06, 2.12), COL_WOOD)
    for pi in range(4):
        make_box(f"Door_PlankSeam_{pi}", (-0.825 + pi * 0.23, 0.035, 1.06),
                 (0.012, 0.005, 2.04), COL_CEDAR_DARK)
    for bi, bz in enumerate((0.55, 1.60)):
        make_box(f"Door_Batten_{bi}", (-0.48, 0.045, bz), (0.84, 0.025, 0.10),
                 COL_CEDAR_DARK)
    make_cyl("Door_Latch", (-0.10, 0.05, 1.02), 0.022, 0.05, COL_IRON, axis='Y')
    make_box("Door_LatchPlate", (-0.10, 0.036, 1.02), (0.05, 0.008, 0.12), COL_IRON)
    make_door_hinges("Door_Hinge", edge_x=-0.93, edge_y=0.0,
                     edge_z_centers=[0.35, 1.05, 1.80], axis='X')
    # The thermometer above the door — nailed there by Tem's
    # grandfather in 1979 (vol7_ch1: fifty-five; ch4: fifty-eight)
    make_box("Thermometer_Plate", (0.35, 0.105, 2.42), (0.09, 0.014, 0.26), COL_CREAM)
    make_box("Thermometer_Column", (0.35, 0.115, 2.40), (0.016, 0.006, 0.18),
             (0.72, 0.24, 0.20, 1.0))
    make_cyl("Thermometer_Bulb", (0.35, 0.115, 2.315), 0.014, 0.012,
             (0.72, 0.24, 0.20, 1.0), axis='Y')
    # Coat pegs west of the door (the peg Finn hangs the wet coat
    # on, vol7_ch4_finn) + wax canvas coat + drip mat
    make_box("PegRail", (-2.05, 0.115, 1.62), (1.10, 0.03, 0.08), COL_WOOD)
    for hi, hx in enumerate((-2.50, -2.20, -1.90, -1.60)):
        make_cyl(f"Peg_{hi}", (hx, 0.16, 1.60), 0.014, 0.10, COL_CEDAR_DARK, axis='Y')
    make_box("PegCoat_Body", (-2.20, 0.20, 1.20), (0.34, 0.06, 0.76), COL_RAINCOAT)
    make_box("PegCoat_Hood", (-2.20, 0.20, 1.62), (0.22, 0.07, 0.12), COL_RAINCOAT)
    make_box("PegCoat_Flap", (-2.20, 0.235, 1.16), (0.10, 0.012, 0.60),
             (0.32, 0.30, 0.22, 1.0))
    make_box("DripMat", (-2.05, 0.42, 0.006), (1.10, 0.50, 0.01), P.RUBBER_MAT)
    # The small shelf by the door — the wool socks the cabin keeps
    # for anyone who arrives without their own (vol7_ch1_morning)
    make_box("SockShelf", (-2.05, 0.20, 0.95), (0.60, 0.18, 0.03), COL_WOOD)
    make_box("SockShelf_Bracket", (-2.05, 0.145, 0.87), (0.08, 0.05, 0.13), COL_CEDAR_DARK)
    for si in range(3):
        tint = (0.60, 0.58, 0.52, 1.0) if si % 2 == 0 else COL_CREAM
        make_cyl(f"SockRoll_{si}", (-2.22 + si * 0.17, 0.22, 1.00), 0.042, 0.07,
                 tint, axis='Y')
    # Muck boots by the door
    for bi, bx in enumerate((-1.32, -1.18)):
        make_box(f"Boot_{bi}_Foot", (bx, 0.38, 0.045), (0.11, 0.26, 0.09), COL_IRON)
        make_cyl(f"Boot_{bi}_Shaft", (bx, 0.46, 0.19), 0.052, 0.22, COL_IRON)
    # Entry mat inside the door
    make_box("EntryMat", (0.0, 0.65, 0.008), (1.40, 0.75, 0.012), (0.36, 0.30, 0.22, 1.0))


# ═════════════════════════════════════════════════════════════════
# SOUTH WINDOW — cedar frame + mullions in the wall opening (no
# glass per playbook). The window Lena watches the rain and Kai on
# the porch through (vol7_ch1_morning).
# ═════════════════════════════════════════════════════════════════
def build_south_window():
    make_box("SWin_Sill", (2.10, 0.0, 0.825), (1.32, 0.24, 0.06), COL_CEDAR_DARK)
    make_box("SWin_Ledge", (2.10, 0.13, 0.865), (1.20, 0.14, 0.03), COL_CEDAR_DARK)
    make_box("SWin_Head", (2.10, 0.0, 2.175), (1.32, 0.24, 0.06), COL_CEDAR_DARK)
    for sgn in (-1, +1):
        make_box(f"SWin_Jamb_{sgn:+d}", (2.10 + sgn * 0.63, 0.0, 1.50),
                 (0.06, 0.24, 1.30), COL_CEDAR_DARK)
    make_box("SWin_MullV", (2.10, 0.0, 1.50), (0.05, 0.14, 1.26), COL_CEDAR_DARK)
    make_box("SWin_MullH", (2.10, 0.0, 1.50), (1.16, 0.14, 0.05), COL_CEDAR_DARK)


# ═════════════════════════════════════════════════════════════════
# EXTERIOR — the porch Tem waits on with her coffee (vol7_ch10),
# the railing Kai stands at for fifteen minutes (vol7_ch1), steps
# to the clearing, dry firewood under the eave, and the gray-green
# cedars in every opening. The creek runs behind the cabin — heard,
# not seen (vol7_ch1) — so no water is modeled.
# ═════════════════════════════════════════════════════════════════
def build_exterior():
    # Porch deck + board seams
    make_box("Porch_Deck", (0.0, -1.05, -0.05), (6.60, 1.90, 0.08), COL_DECK)
    for bi in range(8):
        make_box(f"Porch_BoardSeam_{bi}", (-2.88 + bi * 0.82, -1.05, -0.008),
                 (0.015, 1.88, 0.004), COL_CEDAR_DARK)
    # Posts + porch roof (the eave the rain comes off)
    for pi, px in enumerate((-3.05, -1.05, 1.05, 3.05)):
        make_cyl(f"Porch_Post_{pi}", (px, -1.90, 1.22), 0.06, 2.48, COL_CEDAR_DARK)
    make_box("Porch_Roof", (0.0, -1.02, 2.50), (6.80, 2.16, 0.08), COL_CEDAR_DARK)
    make_box("Porch_Fascia", (0.0, -2.10, 2.42), (6.80, 0.05, 0.14), COL_CEDAR_WALL)
    # Railing — break at the steps x -0.7..+0.7 (Kai stood here)
    for seg, (x0, x1) in enumerate([(-3.0, -0.7), (0.7, 3.0)]):
        n_posts = 4
        for pi in range(n_posts):
            px = x0 + (x1 - x0) * pi / (n_posts - 1)
            make_cyl(f"PorchRail_{seg}_Post_{pi}", (px, -1.90, 0.475), 0.030, 0.95,
                     COL_CEDAR_DARK)
        make_box(f"PorchRail_{seg}_Top", ((x0 + x1) / 2.0, -1.90, 0.965),
                 (x1 - x0 + 0.10, 0.08, 0.05), COL_WOOD)
        make_box(f"PorchRail_{seg}_Mid", ((x0 + x1) / 2.0, -1.90, 0.52),
                 (x1 - x0, 0.045, 0.045), COL_CEDAR_DARK)
    # Steps down to the clearing
    make_box("Porch_Step_0", (0.0, -2.18, -0.14), (1.40, 0.34, 0.10), COL_DECK)
    make_box("Porch_Step_1", (0.0, -2.50, -0.26), (1.40, 0.34, 0.10), COL_DECK)
    # Ground — wet forest floor south + west (the clearing)
    make_box("Ground_S", (0.0, -4.30, -0.40), (14.0, 4.60, 0.10), COL_EARTH)
    make_box("Ground_W", (-5.30, 3.00, -0.20), (4.20, 8.00, 0.10), COL_EARTH)
    make_box("Ground_Path", (0.0, -3.30, -0.345), (1.30, 1.60, 0.012),
             (0.36, 0.32, 0.26, 1.0))
    # Dry firewood stacked under the eave (east of the door)
    for r in range(3):
        for c in range(6):
            make_cyl(f"WoodPile_{r}_{c}", (1.45 + c * 0.15, -0.32, 0.075 + r * 0.14),
                     0.065, 0.42, COL_BARK, axis='Y')
            make_cyl(f"WoodPileEnd_{r}_{c}", (1.45 + c * 0.15, -0.54, 0.075 + r * 0.14),
                     0.055, 0.008, COL_LOG_END, axis='Y')
    # The chopping block by the steps
    make_cyl("ChoppingBlock", (-1.60, -2.60, -0.14), 0.19, 0.42, COL_BARK, segments=12)
    make_cyl("ChoppingBlock_Top", (-1.60, -2.60, 0.075), 0.175, 0.008, COL_LOG_END,
             segments=12)
    # THE CEDARS — gray-green at five-thirty (vol7_ch1). South
    # stand fills the door gap + south window; west stand fills the
    # curtainless bedroom window.
    south_stand = [(-4.6, -3.4, 1.30), (-2.1, -4.4, 1.00), (0.9, -4.7, 1.20),
                   (3.4, -3.9, 0.85), (5.1, -4.6, 1.35), (-5.6, -4.8, 1.10)]
    for ti, (cx, cy, s) in enumerate(south_stand):
        _cedar_tree(f"CedarS_{ti}", cx, cy, -0.35, s)
    west_stand = [(-4.7, 4.9, 1.30), (-5.9, 5.9, 0.95), (-4.5, 3.1, 1.05),
                  (-6.2, 4.0, 1.20), (-4.9, 6.8, 0.85)]
    for ti, (cx, cy, s) in enumerate(west_stand):
        _cedar_tree(f"CedarW_{ti}", cx, cy, -0.15, s)


def main():
    clear_scene()
    build_shell()
    build_bedroom()
    build_woodstove()
    build_kitchen()
    build_table_zone()
    build_west_wall()
    build_seating()
    build_desk()
    build_door_zone()
    build_south_window()
    build_exterior()
    out = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)),
        "../../../assets/3d/locales/cabin_interior.glb"))
    print(f"\n[build_cabin_interior] exporting to {out}")
    export_glb(out)

if __name__ == "__main__":
    main()
