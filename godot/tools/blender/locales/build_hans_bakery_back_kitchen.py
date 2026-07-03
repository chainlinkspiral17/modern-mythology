"""HANS'S BAKERY — back kitchen / the long-table room — vol7 hero locale
(Smolvud, OR).

Hans Schenck's back-of-house on Hemlock: the room where the Sunday
gatherings of ch15/ch17 happen and where the four bowls sit on the
table for the first time in fifty-one years. Pre-dawn register —
"the bakery's main room at five fifty-six was warm" — Smolvud 2025
warm-and-floured, NOT industrial-sterile. Serves seven VN scenes:
vol7_ch15_bread / ch15_loft / ch15_wagon / ch17_bakery / ch17_roy /
ch17_aria / ch18_stick. Canon sources baked in:

  · vol7_ch15_loft: "The main room had three long tables: the
    worktable, the cooling rack table, and the dining table Hans had
    moved in in 2046 when his daughter and Per had gotten married"
    — the three-table anatomy IS this room. Greta at the KETTLE;
    "the same brown eyes as Hans's wedding-photo on the wall behind
    her"; Hans opens the BACK DOOR at five forty-eight; "the
    bakery's back-kitchen light" is a foundation-report town marker;
    Per "on the bench in the back kitchen with a coffee".
  · vol7_ch15_bread: seeded rye + the morning's white; butter Greta
    churned at four AM; the jar of plum preserves from '49; small
    dishes of honey; "coffee in a press for the table"; the basket
    of brötchen Per carries in; the window at the side of the
    bakery that looked out on Hemlock (Marina's hands flat on the
    SILL; the Daily Grind across the street); the chapbook "Bowls"
    — cream cover, hand-stitched spine — set in the middle of the
    table.
  · vol7_ch17_bakery: the long dining table SET FOR THIRTEEN —
    "twelve chairs at the table and one extra at the head for
    whoever needed it"; three loaves out: the seeded rye, the dark
    country, and THE BRIOCHE (grandmother's Sunday bread from Bern
    — the table's hero centerpiece); "the coffee was in the press
    at the table's middle"; Tem's bowl-box goes "on the long table
    at the end nearest the back door" → Tem's head is the east end
    (back-door end), Hans's head the west.
  · vol7_ch17_roy: the bell + front counter are AT THE FRONT of the
    bakery — staged beyond the south doorway, off-frame behind the
    VN camera (Background3D preset: Godot (0, 2.30, +0.5) looking
    north through the door gap x −1..+1).
  · vol7_ch17_aria: "Kai and Lena took the empty coffee cups to the
    KITCHENETTE SINK"; dish towels Greta had set out; chairs that
    stack (plain slat chairs); the clock — Roy's bell rings at SIX
    TWELVE, the wall clock is frozen there.
  · vol7_ch15_wagon: Greta's particular wipe-cloth "washed and
    folded in a particular drawer" — the worktable drawers + the
    folded cloth on top; bread goes "from the back to the front
    cases" (front is beyond the south doorway).
  · vol7_ch21_cabin/leaving: rye wrapped in linen on "the wooden
    tray Greta used for transit"; the stacked brioche baskets —
    both live on/under the cooling rack table between van runs.
  · vol7_ch18_stick: brown paper bags "the kind Hans had been
    selling bread in for forty years"; the back door gives onto the
    alley where the trucks park (alley is a 2D bg — door stays a
    closed leaf here).
  · milk_and_honey/_ART_MANIFEST.md: "Hans's back kitchen. The wood
    stove, the floured work surfaces. Where Hans is at five
    fifty-six. The back door." — the wood-fired masonry deck oven
    with the fire BANKED (music_catalog vol7_bread_table: "Kitchen
    fire crackle... table set for nine") anchors the north wall.

CANON-NEGATIVES honored (wave-5 addendum discipline):
  · NO piano — vol7_hymn_fragment: the hymn is "played on a far
    piano in another room of the house". The music stays off-set.
  · NO cedar bowls baked in — the bowls live at the cabin between
    scenes (ch17_aria closes with Tem boxing all four); the on-table
    bowl moment is a CG. An empty table center holds the room.
  · NO register / till / retail cases back here — Greta's front
    counter is beyond the south doorway, off-frame. The scaffold's
    Kwik-Stop vocabulary (snack aisle, endcap, coffee pots,
    register) is removed per the wrong-fixture-vocabulary lesson.
  · NO fluorescent tubes — Smolvud warm register wants pendants
    (Daily Grind lesson), not 90s operator-noir tubes.
  · NO customers, no Roy's spiral box — Roy brings it with him.

No transparency: the Hemlock window is a REAL OPENING with fir
frame + mullions; the pre-dawn street (wet sidewalk, streetlamp,
the Daily Grind facade with its inside light on — ch15_loft: "The
Daily Grind had a light on inside but had not yet flipped the
CLOSED to OPEN") lives outside it. Facade brick matches the
Salty Tome / Lena-apartment Hemlock treatment (0.44, 0.28, 0.22).

Text is scene-side Label3D per the playbook; this script bakes
named vertex-colored panels:
  Chapbook_Cover, BakeSlate_Board, DailyGrind_SignBoard,
  WeddingPhoto_Canvas, Sack_Stencil_{i}, PaperBags_Stack.
"""
import os, sys
_BT = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
if _BT not in sys.path: sys.path.insert(0, _BT)
from _props import palette as P
from _props.geometry import clear_scene, make_box, make_cyl, export_glb
from _props.structure import (make_floor, make_wall, make_ceiling,
                              make_crown_molding, make_door_hinges)
from _props.decor import make_wall_clock
from _props.safety import make_smoke_detector
from _props.cleaning import make_broom_mop

# ── Shell (footprint kept from the scaffold — the .tscn camera and
#    lights are tuned to this 6 × 5 room, south door gap x −1..+1;
#    the gap is the pass-through to the front of the shop) ────────
ROOM_W = 6.0; ROOM_D = 5.0; CEIL = 2.8
PAL_WALL = {"wall": (0.96, 0.84, 0.62, 1.0), "baseboard": (0.62, 0.42, 0.22, 1.0)}
COL_FLOOR = (0.55, 0.42, 0.30, 1.0)       # scrubbed fir boards
COL_SEAM  = (0.33, 0.25, 0.18, 1.0)

# ── Bakery palette (Smolvud warm-and-floured) ────────────────────
COL_WOOD      = (0.48, 0.35, 0.22, 1.0)   # fir fixtures
COL_WOOD_DARK = (0.28, 0.21, 0.15, 1.0)
COL_WOOD_LT   = (0.66, 0.52, 0.34, 1.0)
COL_TABLE     = (0.58, 0.42, 0.26, 1.0)   # the 2046 wedding table
COL_BUTCHER   = (0.72, 0.58, 0.38, 1.0)   # worktable top
COL_FLOUR     = (0.93, 0.90, 0.82, 1.0)   # dust on every surface
COL_LINEN     = (0.88, 0.84, 0.74, 1.0)
COL_CREAM     = (0.90, 0.87, 0.80, 1.0)   # Greta's ceramic
COL_STONE_BLU = (0.38, 0.44, 0.56, 1.0)   # stoneware accents
COL_RYE       = (0.32, 0.21, 0.12, 1.0)   # seeded rye crust
COL_WHITE_LF  = (0.82, 0.64, 0.38, 1.0)   # the morning's white
COL_COUNTRY   = (0.52, 0.34, 0.18, 1.0)   # the dark country
COL_BRIOCHE   = (0.80, 0.54, 0.24, 1.0)   # egg-washed Sunday gold
COL_DOUGH     = (0.90, 0.85, 0.72, 1.0)
COL_RATTAN    = (0.72, 0.58, 0.36, 1.0)   # bannetons / brötchen basket
COL_BRICK     = (0.52, 0.30, 0.22, 1.0)   # oven masonry
COL_BRICK_DK  = (0.36, 0.21, 0.15, 1.0)
COL_IRON      = P.METAL_BLACK
COL_BRASS     = (0.70, 0.57, 0.30, 1.0)
COL_EMBER     = (0.97, 0.52, 0.20, 1.0)   # the banked fire
COL_EMBER_DP  = (0.52, 0.15, 0.06, 1.0)
COL_GLASSISH  = (0.72, 0.78, 0.78, 1.0)   # opaque stand-in (press)
COL_COFFEE    = (0.30, 0.18, 0.10, 1.0)
COL_JAM_PLUM  = (0.36, 0.15, 0.23, 1.0)   # Greta's '49 preserves
COL_HONEY     = (0.85, 0.60, 0.20, 1.0)   # the Yachats hive
COL_BUTTER    = (0.93, 0.85, 0.55, 1.0)
COL_APRON     = (0.90, 0.88, 0.82, 1.0)
COL_SACK      = (0.86, 0.81, 0.68, 1.0)   # cloth flour sacks
COL_SLATE     = (0.15, 0.16, 0.15, 1.0)
COL_CHALK     = (0.88, 0.88, 0.82, 1.0)
COL_CONCRETE  = (0.55, 0.54, 0.51, 1.0)
COL_ASPHALT   = (0.15, 0.15, 0.16, 1.0)   # rain-dark Hemlock
COL_PUDDLE    = (0.30, 0.33, 0.36, 1.0)
COL_BRICK_HEM = (0.44, 0.28, 0.22, 1.0)   # Hemlock brick (Salty Tome sync)
COL_WIN_WARM  = (0.96, 0.80, 0.46, 1.0)   # the Grind's inside light
CHAIR_TINTS   = [COL_WOOD, COL_WOOD_LT, COL_WOOD_DARK, (0.56, 0.40, 0.24, 1.0)]

TABLE_TOP = 0.76      # dining table surface z
WORK_TOP  = 0.90      # worktable surface z
COOL_TOP  = 0.85      # cooling rack table surface z


# ═════════════════════════════════════════════════════════════════
# Local furniture helpers (deterministic, axis-aligned)
# ═════════════════════════════════════════════════════════════════
_DIRS = {'N': (0.0, 1.0), 'S': (0.0, -1.0), 'E': (1.0, 0.0), 'W': (-1.0, 0.0)}

def _chair(prefix, cx, cy, facing, tint):
    """Plain slat kitchen chair (they stack at cleanup, ch17_aria).
    `facing` is the direction the sitter faces."""
    dx, dy = _DIRS[facing]
    make_box(f"{prefix}_Seat", (cx, cy, 0.45), (0.40, 0.40, 0.04), tint)
    for li, (sx, sy) in enumerate([(-1, -1), (+1, -1), (-1, +1), (+1, +1)]):
        make_cyl(f"{prefix}_Leg_{li}", (cx + sx * 0.16, cy + sy * 0.16, 0.225),
                 0.018, 0.45, COL_WOOD_DARK)
    bx, by = cx - dx * 0.19, cy - dy * 0.19
    for pi, sgn in enumerate((-1, +1)):
        px = bx + (sgn * 0.16 if dx == 0 else 0.0)
        py = by + (sgn * 0.16 if dy == 0 else 0.0)
        make_cyl(f"{prefix}_BackPost_{pi}", (px, py, 0.675), 0.016, 0.45, tint)
    slat_sz = (0.36, 0.03, 0.09) if dx == 0 else (0.03, 0.36, 0.09)
    for si, sz_z in enumerate((0.72, 0.86)):
        make_box(f"{prefix}_Slat_{si}", (bx, by, sz_z), slat_sz, tint)

def _cup_saucer(prefix, cx, cy, bz, tint):
    make_cyl(f"{prefix}_Saucer", (cx, cy, bz + 0.006), 0.058, 0.012, COL_CREAM, segments=12)
    make_cyl(f"{prefix}_Cup", (cx, cy, bz + 0.045), 0.035, 0.065, tint)
    make_box(f"{prefix}_Handle", (cx + 0.044, cy, bz + 0.045), (0.014, 0.012, 0.04), tint)

def _small_plate(prefix, cx, cy, bz, tint=COL_CREAM):
    make_cyl(f"{prefix}", (cx, cy, bz + 0.008), 0.085, 0.014, tint, segments=12)

def _batard(prefix, cx, cy, bz, crust, length=0.34, dusted=True):
    """Oblong loaf: body box + embedded top cylinder for the round
    back (playbook: right primitive, not stacked boxes)."""
    make_box(f"{prefix}_Body", (cx, cy, bz + 0.045), (length, 0.15, 0.09), crust)
    make_cyl(f"{prefix}_Back", (cx, cy, bz + 0.085), 0.070, length - 0.06,
             crust, axis='X', segments=8)
    if dusted:
        make_box(f"{prefix}_FlourScore", (cx, cy, bz + 0.152),
                 (length - 0.10, 0.03, 0.006), COL_FLOUR)

def _boule(prefix, cx, cy, bz, crust):
    make_cyl(f"{prefix}_Base", (cx, cy, bz + 0.035), 0.095, 0.07, crust, segments=12)
    make_cyl(f"{prefix}_Dome", (cx, cy, bz + 0.085), 0.070, 0.035, crust, segments=12)
    make_box(f"{prefix}_Score", (cx, cy, bz + 0.108), (0.10, 0.018, 0.005), COL_FLOUR)

def _pendant(prefix, cx, cy, drop=0.60):
    """Warm shaded pendant — bakery, not fluorescent (Daily Grind
    lesson: Smolvud 2025 is pendants, not tube fixtures)."""
    make_cyl(f"{prefix}_Canopy", (cx, cy, CEIL - 0.02), 0.05, 0.04, COL_IRON)
    make_cyl(f"{prefix}_Cord", (cx, cy, CEIL - drop / 2.0), 0.008, drop, COL_IRON)
    make_cyl(f"{prefix}_Shade", (cx, cy, CEIL - drop - 0.065), 0.15, 0.13,
             (0.30, 0.28, 0.24, 1.0), segments=12)
    make_cyl(f"{prefix}_Bulb", (cx, cy, CEIL - drop - 0.135), 0.05, 0.04,
             (0.98, 0.88, 0.62, 1.0))


# ═════════════════════════════════════════════════════════════════
# SHELL — scaffold footprint kept exactly: 6 × 5, south door gap
# x −1..+1 (to the front of the shop), plus the Hemlock window
# opening carved into the WEST wall (ch15_bread: "the window at the
# side of the bakery that looked out on Hemlock"), the sill Marina
# put her hands flat on. Plank ceiling + fir beams, no drop grid.
# ═════════════════════════════════════════════════════════════════
def build_shell():
    make_floor("Floor", (0.0, ROOM_D / 2.0, 0.0), size_x=ROOM_W + 0.4, size_y=ROOM_D + 0.4,
               palette={"vinyl": COL_FLOOR, "seam": COL_SEAM})
    # East wall — solid (back door leaf + slate + hooks live on it)
    make_wall("Wall_E", (ROOM_W / 2.0, ROOM_D / 2.0, 0), length=ROOM_D + 0.4, height=CEIL,
              axis='Y', palette=PAL_WALL, baseboard_face_sign=-1)
    # West wall — window opening y 2.5..4.1 (sill 0.90, head 2.20)
    make_wall("Wall_W_S", (-ROOM_W / 2.0, 1.15, 0), length=2.70, height=CEIL,
              axis='Y', palette=PAL_WALL, baseboard_face_sign=+1)
    make_wall("Wall_W_N", (-ROOM_W / 2.0, 4.65, 0), length=1.10, height=CEIL,
              axis='Y', palette=PAL_WALL, baseboard_face_sign=+1)
    make_box("Wall_W_SillWall", (-ROOM_W / 2.0, 3.3, 0.45), (0.20, 1.60, 0.90), PAL_WALL["wall"])
    make_box("Wall_W_SillBase", (-ROOM_W / 2.0 + 0.06, 3.3, 0.08), (0.06, 1.60, 0.16),
             PAL_WALL["baseboard"])
    make_box("Wall_W_Header", (-ROOM_W / 2.0, 3.3, 2.50), (0.20, 1.60, 0.60), PAL_WALL["wall"])
    # North wall — solid; the oven + cooling racks anchor it
    make_wall("Wall_N", (0.0, ROOM_D, 0), length=ROOM_W + 0.4, height=CEIL, axis='X',
              palette=PAL_WALL, baseboard_face_sign=-1)
    # South wall — scaffold door gap x −1..+1 kept (front of house
    # beyond; camera stands in this gap looking north)
    make_wall("Wall_S_W", (-(ROOM_W / 4.0 + 0.5), 0.0, 0), length=ROOM_W / 2.0 - 1.0,
              height=CEIL, axis='X', palette=PAL_WALL, baseboard_face_sign=+1)
    make_wall("Wall_S_E", (+(ROOM_W / 4.0 + 0.5), 0.0, 0), length=ROOM_W / 2.0 - 1.0,
              height=CEIL, axis='X', palette=PAL_WALL, baseboard_face_sign=+1)
    make_box("Wall_S_AboveDoor", (0.0, 0.0, CEIL - 0.30), (2.0, 0.20, 0.60), PAL_WALL["wall"])
    # Doorway trim to the front (bread goes "from the back to the
    # front cases" through here, ch15_wagon)
    for sgn in (-1, +1):
        make_box(f"FrontDoorway_Post_{sgn:+d}", (sgn * 1.04, 0.0, 1.10),
                 (0.08, 0.24, 2.20), COL_WOOD)
    make_box("FrontDoorway_Header", (0.0, 0.0, 2.26), (2.16, 0.24, 0.12), COL_WOOD)
    # Ceiling — painted planks, fir battens, NO stains (Greta runs
    # a clean house), plus two exposed beams
    make_ceiling("Ceil", (0.0, ROOM_D / 2.0, CEIL), size_x=ROOM_W + 0.4, size_y=ROOM_D + 0.4,
                 palette={"tile": (0.86, 0.80, 0.68, 1.0), "grid": (0.46, 0.35, 0.24, 1.0)},
                 with_stains=False)
    for bi, by in enumerate((1.7, 3.4)):
        make_box(f"Beam_{bi}", (0.0, by, CEIL - 0.09), (ROOM_W + 0.4, 0.20, 0.18),
                 COL_WOOD_DARK)
    for nm, ax, length, wx, wy in [
            ("Crown_W", 'Y', ROOM_D, -ROOM_W / 2.0 + 0.10, ROOM_D / 2.0),
            ("Crown_E", 'Y', ROOM_D, +ROOM_W / 2.0 - 0.10, ROOM_D / 2.0),
            ("Crown_N", 'X', ROOM_W, 0.0, ROOM_D - 0.10),
            ("Crown_S", 'X', ROOM_W, 0.0, +0.10)]:
        make_crown_molding(nm, wall_x=wx, wall_y=wy, length=length, axis=ax,
                           ceil_z=CEIL, palette={"wood": COL_WOOD})


# ═════════════════════════════════════════════════════════════════
# HEMLOCK WINDOW + EXTERIOR — fir frame + mullions in the real
# opening (no glass per playbook). The interior sill board is the
# one Marina stands at with her hands flat (ch15_bread). Outside:
# wet sidewalk, curb, rain-dark street, and the Daily Grind facade
# across Hemlock — inside light ON, pre-dawn (ch15_loft), brick in
# sync with the Salty Tome Hemlock treatment.
# ═════════════════════════════════════════════════════════════════
def build_window_and_exterior():
    wx = -ROOM_W / 2.0   # −3.0 wall plane
    # Frame — sill board proud into the room (hands-flat canon)
    make_box("WinW_Sill", (wx, 3.3, 0.885), (0.24, 1.72, 0.07), COL_WOOD)
    make_box("WinW_Ledge", (wx + 0.14, 3.3, 0.925), (0.14, 1.60, 0.03), COL_WOOD)
    make_box("WinW_Head", (wx, 3.3, 2.235), (0.24, 1.72, 0.07), COL_WOOD)
    for sgn in (-1, +1):
        make_box(f"WinW_Jamb_{sgn:+d}", (wx, 3.3 + sgn * 0.83, 1.56),
                 (0.24, 0.06, 1.42), COL_WOOD)
    make_box("WinW_MullV", (wx, 3.3, 1.56), (0.14, 0.05, 1.32), COL_WOOD)
    make_box("WinW_Transom", (wx, 3.3, 1.85), (0.14, 1.60, 0.05), COL_WOOD)
    # A small pot of chives on the ledge (Greta's kitchen, not decor)
    make_cyl("WinW_HerbPot", (wx + 0.14, 2.85, 0.965), 0.035, 0.05,
             (0.58, 0.38, 0.26, 1.0))
    make_cyl("WinW_HerbLeaves", (wx + 0.14, 2.85, 1.025), 0.030, 0.07,
             (0.40, 0.50, 0.32, 1.0))
    # ── Exterior: Hemlock at five forty-something. The camera's
    # sightlines out this window run oblique-north (rays from Godot
    # (0,2.30,+0.5) through the y 2.5..4.1 opening land on the far
    # facade around y 10.7..16.7) — so the street strips run long
    # and the Grind's lit storefront sits in THAT band, not square
    # to the window. ─────────────────────────────────────────────
    make_box("Ext_Sidewalk", (-4.32, 8.25, -0.03), (2.25, 17.5, 0.06), COL_CONCRETE)
    for si in range(9):
        make_box(f"Ext_SidewalkSeam_{si}", (-4.32, 0.6 + si * 1.9, 0.001),
                 (2.25, 0.02, 0.002), (0.40, 0.39, 0.37, 1.0))
    make_box("Ext_Curb", (-5.53, 8.25, -0.02), (0.16, 17.5, 0.12), (0.46, 0.45, 0.43, 1.0))
    make_box("Ext_Street", (-7.60, 8.25, -0.05), (4.00, 17.5, 0.04), COL_ASPHALT)
    make_box("Ext_Puddle_0", (-6.4, 8.6, -0.028), (0.90, 0.55, 0.002), COL_PUDDLE)
    make_box("Ext_Puddle_1", (-8.3, 10.2, -0.028), (0.70, 1.10, 0.002), COL_PUDDLE)
    make_box("Ext_Puddle_2", (-6.9, 5.2, -0.028), (0.55, 0.80, 0.002), COL_PUDDLE)
    make_box("Ext_FarCurb", (-9.68, 8.25, -0.02), (0.16, 17.5, 0.12), (0.46, 0.45, 0.43, 1.0))
    make_box("Ext_FarSidewalk", (-10.4, 8.25, -0.03), (1.30, 17.5, 0.06), COL_CONCRETE)
    # The Daily Grind across the street — flat facade, warm windows
    # lit from inside ("had a light on inside but had not yet
    # flipped the CLOSED to OPEN"), corner of Cedar and Hemlock.
    make_box("DG_Facade", (-11.20, 9.0, 2.25), (0.30, 18.0, 4.50), COL_BRICK_HEM)
    make_box("DG_Cornice", (-11.14, 9.0, 4.32), (0.42, 18.2, 0.24), (0.30, 0.34, 0.32, 1.0))
    for wi, wy in enumerate((11.8, 14.6)):
        make_box(f"DG_Window_{wi}", (-11.03, wy, 1.55), (0.06, 1.50, 1.45), COL_WIN_WARM)
        make_box(f"DG_WindowFrame_{wi}_T", (-11.02, wy, 2.31), (0.08, 1.62, 0.08), COL_WOOD_DARK)
        make_box(f"DG_WindowFrame_{wi}_B", (-11.02, wy, 0.79), (0.08, 1.62, 0.08), COL_WOOD_DARK)
        make_box(f"DG_WindowMull_{wi}", (-11.01, wy, 1.55), (0.05, 0.06, 1.40), COL_WOOD_DARK)
    make_box("DG_Door", (-11.03, 13.2, 1.10), (0.06, 0.95, 2.20), COL_WOOD_DARK)
    make_box("DG_DoorLite", (-11.00, 13.2, 1.55), (0.04, 0.60, 0.85), COL_WIN_WARM)
    # Hanging shop sign board (lettering scene-side if ever needed)
    make_cyl("DG_SignArm", (-10.85, 12.2, 3.30), 0.015, 0.55, COL_IRON, axis='X')
    make_box("DailyGrind_SignBoard", (-10.72, 12.2, 3.00), (0.05, 0.72, 0.40),
             (0.34, 0.28, 0.22, 1.0))
    # Streetlamp on the far walk — pre-dawn: "the streetlight"
    make_cyl("Lamp_Pole", (-9.9, 10.5, 1.80), 0.045, 3.60, COL_IRON)
    make_cyl("Lamp_Arm", (-9.55, 10.5, 3.55), 0.025, 0.70, COL_IRON, axis='X')
    make_cyl("Lamp_Head", (-9.25, 10.5, 3.48), 0.10, 0.12, COL_IRON, segments=12)
    make_cyl("Lamp_Glow", (-9.25, 10.5, 3.40), 0.075, 0.05, (0.98, 0.92, 0.70, 1.0))


# ═════════════════════════════════════════════════════════════════
# THE DINING TABLE — the hero object. "The dining table Hans had
# moved in in 2046 when his daughter and Per had gotten married and
# the wedding meal had needed somewhere to happen" (ch15_loft). Set
# for the ch17 gathering: twelve chairs + the extra at the head.
# Hans's head is WEST (nearest his oven + kitchenette), Tem's head
# is EAST — "the end nearest the back door" (ch17_bakery).
# ═════════════════════════════════════════════════════════════════
def build_dining_table():
    tcx, tcy = -0.3, 2.45          # table center; x −2.1..1.5
    tl, tw = 3.6, 1.05
    make_box("DiningTable_Top", (tcx, tcy, TABLE_TOP - 0.025), (tl, tw, 0.05), COL_TABLE)
    make_box("DiningTable_Apron", (tcx, tcy, TABLE_TOP - 0.09), (tl - 0.24, tw - 0.24, 0.08),
             COL_WOOD_DARK)
    # Trestle base — two posts + feet + stretcher (a wedding table,
    # not a cafe table)
    for pi, px in enumerate((tcx - tl / 2.0 + 0.45, tcx + tl / 2.0 - 0.45)):
        make_box(f"DiningTable_Post_{pi}", (px, tcy, 0.38), (0.12, 0.60, 0.64), COL_WOOD_DARK)
        make_box(f"DiningTable_Foot_{pi}", (px, tcy, 0.04), (0.16, 0.90, 0.08), COL_WOOD_DARK)
    make_box("DiningTable_Stretcher", (tcx, tcy, 0.22), (tl - 1.1, 0.10, 0.08), COL_WOOD_DARK)
    # ── Twelve chairs + the extra at Tem's head ──────────────────
    side_xs = (-1.72, -0.94, -0.16, +0.62, +1.40)
    for ci, sx in enumerate(side_xs):
        _chair(f"Chair_S_{ci}", sx, 1.55, 'N', CHAIR_TINTS[ci % len(CHAIR_TINTS)])
        _chair(f"Chair_N_{ci}", sx, 3.35, 'S', CHAIR_TINTS[(ci + 2) % len(CHAIR_TINTS)])
    _chair("Chair_Head_Hans", -2.45, 2.45, 'E', CHAIR_TINTS[0])   # west head
    _chair("Chair_Head_Tem", +1.85, 2.45, 'W', CHAIR_TINTS[1])    # east head
    # "one extra at the head for whoever needed it" — Roy's chair,
    # set and waiting beside the east head (ch17_bakery/ch17_roy)
    _chair("Chair_Extra", +1.90, 3.30, 'W', CHAIR_TINTS[2])
    # ── Place settings: cups + small plates. The music manifest
    # calls the ch15 cue "table set for nine"; ch17 seats more —
    # ten settings covers both readings without crowding the geo.
    setting_tints = [COL_CREAM, COL_STONE_BLU, COL_CREAM, COL_CREAM, COL_STONE_BLU]
    for ci, sx in enumerate(side_xs):
        _small_plate(f"Plate_S_{ci}", sx, 2.03, TABLE_TOP)
        _cup_saucer(f"CupSet_S_{ci}", sx + 0.16, 2.13, TABLE_TOP, setting_tints[ci])
        _small_plate(f"Plate_N_{ci}", sx, 2.87, TABLE_TOP)
        _cup_saucer(f"CupSet_N_{ci}", sx - 0.16, 2.77, TABLE_TOP,
                    setting_tints[(ci + 3) % len(setting_tints)])
    build_table_spread(tcy)

def build_table_spread(tcy):
    """The center line of the table, west→east: rye on its board,
    the dark country, butter/preserves/honey, THE BRIOCHE, the
    brötchen basket, the coffee press. Plus the chapbook."""
    # Seeded rye on a cutting board, two slices off (ch15_bread:
    # "Hans had cut a loaf of the seeded rye")
    make_box("RyeBoard", (-1.45, tcy, TABLE_TOP + 0.012), (0.50, 0.30, 0.024), COL_WOOD_LT)
    _batard("Rye", -1.52, tcy + 0.02, TABLE_TOP + 0.024, COL_RYE, length=0.30)
    for si in range(2):
        make_box(f"RyeSlice_{si}", (-1.28 + si * 0.02, tcy - 0.09, TABLE_TOP + 0.032 + si * 0.012),
                 (0.13, 0.11, 0.012), (0.62, 0.46, 0.28, 1.0))
    make_box("BreadKnife_Blade", (-1.36, tcy - 0.155, TABLE_TOP + 0.030), (0.26, 0.025, 0.008),
             P.METAL_STEEL)
    make_box("BreadKnife_Handle", (-1.19, tcy - 0.155, TABLE_TOP + 0.032), (0.09, 0.030, 0.022),
             COL_WOOD_DARK)
    # The dark country (ch17_bakery)
    _batard("Country", -0.85, tcy + 0.05, TABLE_TOP, COL_COUNTRY, length=0.32)
    # Butter Greta churned at four AM + the '49 plum preserves +
    # the small dishes of honey from the Yachats hive (ch15_bread)
    make_box("ButterDish", (-0.42, tcy - 0.14, TABLE_TOP + 0.012), (0.16, 0.11, 0.024), COL_CREAM)
    make_box("ButterPat", (-0.42, tcy - 0.14, TABLE_TOP + 0.045), (0.10, 0.06, 0.04), COL_BUTTER)
    make_cyl("JamJar_Body", (-0.40, tcy + 0.12, TABLE_TOP + 0.055), 0.042, 0.11, COL_JAM_PLUM)
    make_cyl("JamJar_ClothTop", (-0.40, tcy + 0.12, TABLE_TOP + 0.115), 0.048, 0.02, COL_LINEN)
    for hi, (hx, hy) in enumerate([(-0.18, tcy - 0.16), (-0.18, tcy + 0.16)]):
        make_cyl(f"HoneyDish_{hi}", (hx, hy, TABLE_TOP + 0.022), 0.045, 0.044, COL_CREAM,
                 segments=12)
        make_cyl(f"HoneyFill_{hi}", (hx, hy, TABLE_TOP + 0.048), 0.036, 0.012, COL_HONEY,
                 segments=12)
    # THE BRIOCHE — center of the table, on Greta's good plate.
    # "The brioche on the table held the room" (ch17_bakery).
    make_cyl("BriochePlate", (0.12, tcy, TABLE_TOP + 0.010), 0.145, 0.020, COL_CREAM,
             segments=12)
    make_cyl("Brioche_Base", (0.12, tcy, TABLE_TOP + 0.075), 0.115, 0.11, COL_BRIOCHE,
             segments=12)
    make_cyl("Brioche_Waist", (0.12, tcy, TABLE_TOP + 0.145), 0.090, 0.05, COL_BRIOCHE,
             segments=12)
    make_cyl("Brioche_Dome", (0.12, tcy, TABLE_TOP + 0.190), 0.062, 0.055,
             (0.86, 0.62, 0.30, 1.0), segments=12)
    # The basket of the morning's brötchen Per carries in (ch15_bread)
    make_cyl("Basket_Body", (0.62, tcy + 0.04, TABLE_TOP + 0.045), 0.155, 0.09, COL_RATTAN,
             segments=12)
    make_cyl("Basket_Rim", (0.62, tcy + 0.04, TABLE_TOP + 0.095), 0.168, 0.022, COL_WOOD_LT,
             segments=12)
    make_box("Basket_Cloth", (0.62, tcy + 0.04, TABLE_TOP + 0.100), (0.20, 0.20, 0.012),
             COL_LINEN)
    for bi, (bx, by) in enumerate([(0.56, tcy - 0.01), (0.68, tcy + 0.01),
                                   (0.62, tcy + 0.11), (0.57, tcy + 0.09)]):
        make_cyl(f"Broetchen_{bi}", (bx, by, TABLE_TOP + 0.128), 0.042, 0.045, COL_WHITE_LF,
                 segments=8)
    # "The coffee was in the press at the table's middle" — refilled
    # three times by eight-fifteen (ch17_aria)
    make_cyl("Press_Glass", (1.05, tcy - 0.04, TABLE_TOP + 0.085), 0.055, 0.17, COL_GLASSISH,
             segments=12)
    make_cyl("Press_Coffee", (1.05, tcy - 0.04, TABLE_TOP + 0.055), 0.048, 0.09, COL_COFFEE,
             segments=12)
    make_cyl("Press_Lid", (1.05, tcy - 0.04, TABLE_TOP + 0.175), 0.058, 0.018, P.METAL_STEEL)
    make_cyl("Press_Rod", (1.05, tcy - 0.04, TABLE_TOP + 0.205), 0.008, 0.05, P.METAL_STEEL)
    make_cyl("Press_Knob", (1.05, tcy - 0.04, TABLE_TOP + 0.235), 0.020, 0.02, COL_WOOD_DARK)
    make_box("Press_Handle", (1.11, tcy - 0.04, TABLE_TOP + 0.10), (0.016, 0.014, 0.10),
             P.METAL_BLACK)
    make_cyl("Trivet", (1.05, tcy - 0.04, TABLE_TOP + 0.006), 0.075, 0.012, COL_WOOD_DARK,
             segments=12)
    # The chapbook — "Bowls", twenty-some pages, hand-bound, cover
    # plain cream paper (ch15_bread). On the table's south side
    # where Marit set it down; title lettering scene-side.
    make_box("Chapbook_Cover", (0.30, 2.12, TABLE_TOP + 0.008), (0.16, 0.22, 0.014), P.PAPER)
    make_box("Chapbook_TitleBand", (0.30, 2.12, TABLE_TOP + 0.017), (0.09, 0.045, 0.003),
             (0.16, 0.22, 0.40, 1.0))   # the single word printed in dark blue
    make_box("Chapbook_Stitch", (0.225, 2.12, TABLE_TOP + 0.016), (0.010, 0.20, 0.004),
             COL_LINEN)


# ═════════════════════════════════════════════════════════════════
# THE WORKTABLE — east side, run north-south. "The floured work
# surfaces" (art manifest); "the worktable wiped down" (ch15_wagon).
# Fir drawers below — one of them is where Greta's particular cloth
# lives washed-and-folded; the folded cloth sits on top. Balance
# scale, bannetons of proofing dough, bench scraper, rolling pin,
# the brown paper bags. Flour everywhere.
# ═════════════════════════════════════════════════════════════════
def build_worktable():
    wcx, wcy = 2.45, 1.50          # x 2.08..2.83, y 0.40..2.60
    make_box("Worktable_Top", (wcx, wcy, WORK_TOP - 0.035), (0.75, 2.20, 0.07), COL_BUTCHER)
    make_box("Worktable_Frame", (wcx, wcy, WORK_TOP - 0.16), (0.66, 2.10, 0.18), COL_WOOD)
    for li, (sx, sy) in enumerate([(-1, -1), (+1, -1), (-1, +1), (+1, +1)]):
        make_box(f"Worktable_Leg_{li}", (wcx + sx * 0.29, wcy + sy * 0.98, 0.36),
                 (0.08, 0.08, 0.72), COL_WOOD)
    make_box("Worktable_ShelfLow", (wcx, wcy, 0.16), (0.62, 2.00, 0.03), COL_WOOD)
    # Drawer fronts on the west (room-facing) face — Greta's cloth
    # drawer among them (ch15_wagon)
    for di in range(3):
        dy = wcy - 0.70 + di * 0.70
        make_box(f"Worktable_Drawer_{di}", (wcx - 0.34, dy, WORK_TOP - 0.155),
                 (0.03, 0.56, 0.14), COL_WOOD_LT)
        make_cyl(f"Worktable_DrawerKnob_{di}", (wcx - 0.365, dy, WORK_TOP - 0.155),
                 0.016, 0.03, COL_BRASS, axis='X')
    # The particular cloth, washed and folded, on the top's south end
    make_box("Cloth_Greta", (wcx - 0.05, 0.62, WORK_TOP + 0.012), (0.20, 0.15, 0.024),
             (0.72, 0.66, 0.56, 1.0))
    # Flour dusting — the surfaces Hans has been in since three thirty
    for fi, (fx, fy, fw, fl) in enumerate([
            (wcx - 0.08, 1.30, 0.34, 0.45), (wcx + 0.12, 1.85, 0.28, 0.30),
            (wcx - 0.14, 2.30, 0.22, 0.26)]):
        make_box(f"Worktable_FlourDust_{fi}", (fx, fy, WORK_TOP + 0.003), (fw, fl, 0.005),
                 COL_FLOUR)
    # Balance scale + weights (a Smolvud bakery weighs by iron)
    make_box("Scale_Base", (wcx, 1.16, WORK_TOP + 0.02), (0.34, 0.16, 0.04), COL_IRON)
    make_cyl("Scale_Column", (wcx, 1.16, WORK_TOP + 0.11), 0.018, 0.14, COL_IRON)
    make_box("Scale_Beam", (wcx, 1.16, WORK_TOP + 0.185), (0.36, 0.03, 0.025), COL_IRON)
    for si, sgn in enumerate((-1, +1)):
        make_cyl(f"Scale_Chain_{si}", (wcx + sgn * 0.15, 1.16, WORK_TOP + 0.135),
                 0.005, 0.08, P.METAL_STEEL)
        make_cyl(f"Scale_Pan_{si}", (wcx + sgn * 0.15, 1.16, WORK_TOP + 0.085),
                 0.068, 0.016, COL_BRASS, segments=12)
    make_cyl("Scale_DoughLump", (wcx - 0.15, 1.16, WORK_TOP + 0.125), 0.042, 0.05, COL_DOUGH)
    for wi in range(3):
        make_cyl(f"Scale_Weight_{wi}", (wcx + 0.24, 1.00 + wi * 0.09, WORK_TOP + 0.045),
                 0.028 - wi * 0.006, 0.05 - wi * 0.008, COL_IRON)
    # Bannetons — the morning's proof: one open with dough, one
    # resting under its linen
    make_cyl("Banneton_0_Body", (wcx - 0.02, 1.62, WORK_TOP + 0.045), 0.105, 0.09, COL_RATTAN,
             segments=12)
    make_cyl("Banneton_0_Coil", (wcx - 0.02, 1.62, WORK_TOP + 0.075), 0.112, 0.018, COL_WOOD_LT,
             segments=12)
    make_cyl("Banneton_0_Dough", (wcx - 0.02, 1.62, WORK_TOP + 0.105), 0.082, 0.045, COL_DOUGH,
             segments=12)
    make_cyl("Banneton_1_Body", (wcx + 0.03, 1.94, WORK_TOP + 0.045), 0.105, 0.09, COL_RATTAN,
             segments=12)
    make_box("Banneton_1_Linen", (wcx + 0.03, 1.94, WORK_TOP + 0.10), (0.26, 0.26, 0.02),
             COL_LINEN)
    # Bench scraper + rolling pin
    make_box("Scraper_Blade", (wcx - 0.16, 2.12, WORK_TOP + 0.045), (0.012, 0.11, 0.09),
             P.METAL_STEEL)
    make_box("Scraper_Handle", (wcx - 0.16, 2.12, WORK_TOP + 0.105), (0.03, 0.11, 0.03),
             COL_WOOD)
    make_cyl("RollingPin_Body", (wcx + 0.05, 2.38, WORK_TOP + 0.035), 0.035, 0.34, COL_WOOD_LT,
             axis='X')
    for pi, sgn in enumerate((-1, +1)):
        make_cyl(f"RollingPin_Grip_{pi}", (wcx + 0.05 + sgn * 0.22, 2.38, WORK_TOP + 0.035),
                 0.018, 0.09, COL_WOOD, axis='X')
    # Brown paper bags — forty years of them (ch18_stick)
    make_box("PaperBags_Stack", (wcx + 0.22, 0.58, WORK_TOP + 0.045), (0.20, 0.30, 0.09),
             P.PAPER_AGED)
    make_box("PaperBags_Fold", (wcx + 0.22, 0.58, WORK_TOP + 0.095), (0.22, 0.32, 0.012),
             (0.78, 0.68, 0.52, 1.0))
    # The old spiral mixer at the worktable's north end — the one
    # concession to machinery in a hand bakery
    make_box("Mixer_Base", (2.55, 3.05, 0.09), (0.52, 0.52, 0.18), COL_IRON)
    make_box("Mixer_Column", (2.72, 3.05, 0.62), (0.18, 0.30, 0.88), (0.36, 0.38, 0.40, 1.0))
    make_box("Mixer_Head", (2.52, 3.05, 1.10), (0.50, 0.28, 0.22), (0.36, 0.38, 0.40, 1.0))
    make_box("Mixer_Cradle", (2.42, 3.05, 0.545), (0.30, 0.34, 0.05), COL_IRON)
    make_cyl("Mixer_Bowl", (2.42, 3.05, 0.72), 0.17, 0.30, P.METAL_STEEL, segments=12)
    make_cyl("Mixer_Hook", (2.42, 3.05, 0.93), 0.025, 0.14, P.METAL_STEEL)
    make_cyl("Mixer_Knob", (2.52, 2.90, 1.10), 0.024, 0.03, COL_IRON, axis='Y')


# ═════════════════════════════════════════════════════════════════
# THE OVEN — north-east: wood-fired masonry deck oven, the fire
# BANKED (vol7_bread_table: "kitchen fire crackle"; art manifest:
# "the wood stove"). Brick mass, steel deck door, arch band over
# the mouth, firebox glowing low, flue to the ceiling. The peels
# hang on the wall beside it; the wood crate sits at its west end.
# ═════════════════════════════════════════════════════════════════
def build_oven():
    ocx = 1.70                      # body x 0.60..2.80
    make_box("Oven_Body", (ocx, 4.575, 0.95), (2.20, 0.85, 1.90), COL_BRICK)
    make_box("Oven_Plinth", (ocx, 4.55, 0.09), (2.30, 0.95, 0.18), COL_BRICK_DK)
    make_box("Oven_Crown", (ocx, 4.575, 1.945), (2.30, 0.95, 0.09), COL_BRICK_DK)
    # Face layering (room side is −Y; every layer sits PROUD of the
    # last — Gas & Go lesson: nothing buried inside wall thickness):
    #   body face 4.150 > courses 4.140 > trim 4.135 > door 4.105
    #   > lintel 4.120 / keystone 4.100 > firebox stack below.
    # Brick coursing hints on the face
    for ci in range(3):
        make_box(f"Oven_Course_{ci}", (ocx, 4.145, 0.80 + ci * 0.50), (2.20, 0.010, 0.025),
                 COL_BRICK_DK)
    # Deck door — steel, long spring handle, closed on the banked
    # heat. Trim border BEHIND the door leaf, leaf proud of it.
    make_box("Oven_DeckDoorTrim", (ocx, 4.145, 1.32), (1.08, 0.02, 0.56), COL_IRON)
    make_box("Oven_DeckDoor", (ocx, 4.120, 1.32), (0.98, 0.03, 0.46), (0.30, 0.30, 0.32, 1.0))
    make_cyl("Oven_DeckHandle", (ocx, 4.08, 1.14), 0.016, 0.70, P.METAL_STEEL, axis='X')
    for hi, sgn in enumerate((-1, +1)):
        make_box(f"Oven_HandleBracket_{hi}", (ocx + sgn * 0.32, 4.095, 1.17),
                 (0.03, 0.05, 0.06), COL_IRON)
    # Masonry arch over the mouth — soldier-course lintel + keystone
    # + springer blocks (a proud arch DISK would bury the deck door
    # — audit lesson, wave 2)
    make_box("Oven_ArchLintel", (ocx, 4.135, 1.67), (1.16, 0.03, 0.14), COL_BRICK_DK)
    make_box("Oven_ArchKeystone", (ocx, 4.115, 1.68), (0.16, 0.05, 0.18),
             (0.60, 0.56, 0.50, 1.0))
    for si2, sgn in enumerate((-1, +1)):
        make_box(f"Oven_ArchSpringer_{si2}", (ocx + sgn * 0.56, 4.130, 1.63),
                 (0.12, 0.035, 0.10), COL_BRICK_DK)
    # Brass temperature gauge (round, eye level, per playbook) —
    # on the brick west of the deck door
    make_cyl("Oven_GaugeRim", (ocx - 0.75, 4.135, 1.35), 0.062, 0.020, COL_BRASS, axis='Y')
    make_cyl("Oven_Gauge", (ocx - 0.75, 4.120, 1.35), 0.055, 0.014, COL_CREAM, axis='Y')
    make_box("Oven_GaugeNeedle", (ocx - 0.75, 4.108, 1.36), (0.008, 0.004, 0.045), COL_IRON)
    # FIREBOX — low, doors ajar on the banked fire ("kitchen fire
    # crackle"). Layered dark cavity > ember bed > embers > doors,
    # each proud of the last so the glow reads from the room.
    make_box("Oven_FireboxCavity", (ocx, 4.125, 0.52), (0.86, 0.03, 0.40),
             (0.06, 0.04, 0.03, 1.0))
    make_box("Oven_EmberBed", (ocx, 4.100, 0.42), (0.70, 0.03, 0.09), COL_EMBER_DP)
    for ei, (ex, ez, ew) in enumerate([(-0.22, 0.455, 0.16), (0.02, 0.47, 0.20),
                                       (0.24, 0.45, 0.13)]):
        make_box(f"Oven_Ember_{ei}", (ocx + ex, 4.085, ez), (ew, 0.028, 0.045), COL_EMBER)
    for gi, sgn in enumerate((-1, +1)):
        make_box(f"Oven_FireDoor_{gi}", (ocx + sgn * 0.30, 4.070, 0.52), (0.26, 0.025, 0.38),
                 COL_IRON)
        make_cyl(f"Oven_FireDoorKnob_{gi}", (ocx + sgn * 0.18, 4.050, 0.52), 0.014, 0.03,
                 COL_BRASS, axis='Y')
    make_box("Oven_AshDrawer", (ocx, 4.115, 0.245), (0.60, 0.035, 0.12), (0.30, 0.30, 0.32, 1.0))
    make_cyl("Oven_AshPull", (ocx, 4.090, 0.245), 0.012, 0.03, COL_BRASS, axis='Y')
    # Hearth plate on the floor in front of the firebox
    make_box("Oven_HearthPlate", (ocx, 3.92, 0.006), (1.30, 0.45, 0.012), COL_IRON)
    # Flue — hood tiers + round stack through the ceiling
    make_box("Oven_HoodLower", (ocx, 4.575, 2.06), (1.30, 0.70, 0.14), COL_IRON)
    make_box("Oven_HoodUpper", (ocx, 4.575, 2.20), (0.90, 0.52, 0.14), COL_IRON)
    make_cyl("Oven_Flue", (ocx, 4.575, 2.53), 0.14, 0.52, COL_IRON, segments=12)
    make_cyl("Oven_FlueCollar", (ocx, 4.575, 2.74), 0.17, 0.06, COL_IRON, segments=12)
    # Crown ledge keeps the salt crock + the match tin
    make_cyl("Oven_SaltCrock", (ocx + 0.72, 4.42, 2.05), 0.055, 0.12, COL_CREAM)
    make_box("Oven_MatchTin", (ocx + 0.48, 4.42, 2.02), (0.10, 0.07, 0.05),
             (0.62, 0.34, 0.22, 1.0))
    # ── Peels on the wall gap west of the oven ───────────────────
    for pi, px in enumerate((-0.06, 0.32)):
        make_cyl(f"Peel_{pi}_Handle", (px, 4.88, 1.12), 0.020, 1.30, COL_WOOD_LT)
        make_box(f"Peel_{pi}_Blade", (px, 4.86, 1.98), (0.24, 0.035, 0.42), COL_WOOD_LT)
        make_cyl(f"Peel_{pi}_Hook", (px, 4.86, 2.24), 0.012, 0.06, COL_IRON, axis='Y')
    # ── Split-wood crate at the oven's west end ──────────────────
    make_box("WoodCrate", (0.10, 4.55, 0.21), (0.52, 0.48, 0.42), COL_WOOD_DARK,
             open_faces={'+Z'})
    for li in range(4):
        lx = -0.06 + (li % 2) * 0.16
        lz = 0.30 + (li // 2) * 0.11
        make_cyl(f"Log_{li}", (lx, 4.55, lz), 0.055, 0.38, (0.42, 0.30, 0.18, 1.0),
                 axis='Y', segments=8)
    make_cyl("Log_Split", (0.24, 4.48, 0.46), 0.045, 0.34, (0.68, 0.56, 0.38, 1.0),
             axis='Y', segments=8)
    # Flour drift on the floor where the work happens
    for di, (dx, dy, dw, dl) in enumerate([
            (1.9, 3.75, 0.55, 0.30), (2.2, 1.35, 0.40, 0.55), (0.9, 4.15, 0.30, 0.25)]):
        make_box(f"Floor_FlourDrift_{di}", (dx, dy, 0.004), (dw, dl, 0.006), COL_FLOUR)


# ═════════════════════════════════════════════════════════════════
# COOLING RACK TABLE — north-west. The second of the three long
# tables (ch15_loft). The morning's bread cools here before Greta
# carries it "from the back to the front cases": whites on the top
# rack, ryes below, dark country on the table. Greta's wooden
# transit tray + linen-wrapped loaves (ch21 van canon) + the
# brioche baskets stacked beneath.
# ═════════════════════════════════════════════════════════════════
def build_cooling_table():
    ccx, ccy = -1.40, 4.68          # x −2.4..−0.4, y 4.38..4.98
    make_box("CoolTable_Top", (ccx, ccy, COOL_TOP - 0.03), (2.00, 0.60, 0.06), COL_WOOD)
    for li, (sx, sy) in enumerate([(-1, -1), (+1, -1), (-1, +1), (+1, +1)]):
        make_box(f"CoolTable_Leg_{li}", (ccx + sx * 0.90, ccy + sy * 0.22, 0.41),
                 (0.07, 0.07, 0.82), COL_WOOD_DARK)
    # (no low stretcher — the sacks and basket stack live under the
    # east and west halves; a full-span stretcher would run through
    # them, the exact interpenetration the wave-2 audit lesson flags)
    # Wall racks above — two tiers of cooling battens
    for ri, rz in enumerate((1.42, 1.80)):
        make_box(f"Rack_Shelf_{ri}", (ccx, 4.82, rz), (2.00, 0.34, 0.03), COL_WOOD_LT)
        for ki, sgn in enumerate((-1, +1)):
            make_box(f"Rack_Bracket_{ri}_{ki}", (ccx + sgn * 0.86, 4.92, rz - 0.07),
                     (0.03, 0.14, 0.12), COL_IRON)
        for bi in range(3):
            make_box(f"Rack_Batten_{ri}_{bi}", (ccx, 4.72 + bi * 0.10, rz + 0.018),
                     (1.94, 0.02, 0.008), COL_WOOD_DARK)
    # Top rack: the morning's white, boules in a row (ch15_bread)
    for bi in range(5):
        _boule(f"WhiteLoaf_{bi}", ccx - 0.80 + bi * 0.40, 4.82, 1.815, COL_WHITE_LF)
    # Lower rack: seeded ryes
    for bi in range(4):
        _batard(f"RyeLoaf_{bi}", ccx - 0.62 + bi * 0.42, 4.82, 1.435, COL_RYE,
                length=0.30, dusted=(bi % 2 == 0))
    # Table top: dark country batch + the transit tray
    for bi in range(3):
        _batard(f"CountryLoaf_{bi}", ccx - 0.60 + bi * 0.44, 4.62, COOL_TOP, COL_COUNTRY,
                length=0.32, dusted=(bi % 2 == 1))
    # Greta's transit tray — rye wrapped in linen for the van run
    # (vol7_ch21_cabin)
    make_box("TransitTray_Base", (ccx + 0.62, 4.70, COOL_TOP + 0.015), (0.62, 0.42, 0.03),
             COL_WOOD_LT)
    for ti, sgn in enumerate((-1, +1)):
        make_box(f"TransitTray_Rail_{ti}", (ccx + 0.62, 4.70 + sgn * 0.20, COOL_TOP + 0.06),
                 (0.62, 0.03, 0.07), COL_WOOD_LT)
    for wi in range(2):
        make_box(f"TransitTray_LinenLoaf_{wi}", (ccx + 0.48 + wi * 0.30, 4.70, COOL_TOP + 0.09),
                 (0.26, 0.15, 0.11), COL_LINEN)
    # Brioche baskets stacked beneath (vol7_ch21_leaving: Greta
    # "arranging the empty brioche baskets in stacks")
    for si in range(3):
        make_cyl(f"BriocheBasket_{si}", (ccx - 0.55, 4.66, 0.05 + si * 0.09), 0.16, 0.09,
                 COL_RATTAN, segments=12)
    # Flour sacks on a pallet under the table's east half
    make_box("Sack_Pallet", (ccx + 0.55, 4.66, 0.05), (0.80, 0.50, 0.10), COL_WOOD_DARK)
    for ki in range(2):
        kx = ccx + 0.35 + ki * 0.42
        make_box(f"Sack_{ki}", (kx, 4.66, 0.30), (0.36, 0.40, 0.40), COL_SACK)
        make_box(f"Sack_{ki}_Roll", (kx, 4.66, 0.52), (0.40, 0.44, 0.05), COL_SACK)
        make_box(f"Sack_Stencil_{ki}", (kx, 4.435, 0.30), (0.22, 0.006, 0.13),
                 (0.42, 0.34, 0.26, 1.0))
    # The wall clock — frozen at SIX TWELVE, the minute Roy's bell
    # rings at the front (vol7_ch17_roy)
    make_wall_clock("Clock", (-1.40, ROOM_D - 0.10, 2.32), frozen_hour=6, frozen_min=12)


# ═════════════════════════════════════════════════════════════════
# KITCHENETTE + BENCH — west-south wall. The sink the coffee cups
# go to (ch17_aria), Greta's kettle (ch15_loft), the dish towels,
# the cup shelf, the wedding-photo on the wall behind the kettle.
# The bench under the Hemlock window is Per's five-thirty seat
# (ch15_loft: "on the bench in the back kitchen with a coffee").
# ═════════════════════════════════════════════════════════════════
def build_kitchenette():
    kx = -2.70                      # cabinet x −2.92..−2.48
    make_box("Kitchenette_Body", (kx, 1.30, 0.44), (0.44, 1.50, 0.88), COL_WOOD)
    make_box("Kitchenette_Top", (kx, 1.30, 0.905), (0.50, 1.56, 0.05), COL_BUTCHER)
    make_box("Kitchenette_Kick", (kx + 0.225, 1.30, 0.07), (0.02, 1.50, 0.14), COL_WOOD_DARK)
    for di, dy in enumerate((0.85, 1.75)):
        make_box(f"Kitchenette_Door_{di}", (kx + 0.225, dy, 0.50), (0.015, 0.62, 0.66),
                 COL_WOOD_LT)
        make_cyl(f"Kitchenette_Knob_{di}", (kx + 0.25, dy + 0.20, 0.62), 0.014, 0.03,
                 COL_BRASS, axis='X')
    # Sink — inset basin + gooseneck (the kitchenette sink, ch17_aria)
    make_box("Sink_Basin", (kx, 1.72, 0.885), (0.36, 0.40, 0.10), P.METAL_STEEL,
             open_faces={'+Z'})
    make_box("Sink_BasinFloor", (kx, 1.72, 0.845), (0.34, 0.38, 0.01), (0.42, 0.44, 0.46, 1.0))
    make_cyl("Sink_FaucetRiser", (kx - 0.16, 1.72, 1.05), 0.014, 0.24, P.METAL_STEEL)
    make_cyl("Sink_FaucetSpout", (kx - 0.08, 1.72, 1.16), 0.012, 0.18, P.METAL_STEEL, axis='X')
    for hi, hy in enumerate((1.60, 1.84)):
        make_box(f"Sink_Handle_{hi}", (kx - 0.16, hy, 0.955), (0.02, 0.05, 0.02), P.METAL_STEEL)
    # Two washed cups drying on a folded towel beside the basin
    make_box("Sink_DryTowel", (kx, 1.34, 0.937), (0.30, 0.24, 0.014), COL_LINEN)
    for ci in range(2):
        make_cyl(f"Sink_DryCup_{ci}", (kx - 0.06 + ci * 0.13, 1.34, 0.975), 0.036, 0.06,
                 COL_CREAM if ci == 0 else COL_STONE_BLU)
    # Greta's kettle (ch15_loft: "Greta was at the kettle")
    make_cyl("Kettle_Body", (kx, 0.90, 1.005), 0.080, 0.14, P.METAL_STEEL, segments=12)
    make_cyl("Kettle_Lid", (kx, 0.90, 1.085), 0.052, 0.02, P.METAL_STEEL)
    make_cyl("Kettle_Knob", (kx, 0.90, 1.105), 0.014, 0.02, COL_WOOD_DARK)
    make_box("Kettle_Spout_A", (kx + 0.09, 0.90, 0.99), (0.07, 0.018, 0.018), P.METAL_STEEL)
    make_box("Kettle_Spout_B", (kx + 0.135, 0.90, 1.02), (0.04, 0.015, 0.015), P.METAL_STEEL)
    make_box("Kettle_Handle", (kx - 0.09, 0.90, 1.09), (0.03, 0.02, 0.08), COL_WOOD_DARK)
    # The dish towels Greta set out, folded in a stack (ch17_aria)
    make_box("TowelStack_0", (kx, 0.58, 0.945), (0.24, 0.18, 0.02), COL_LINEN)
    make_box("TowelStack_1", (kx + 0.01, 0.58, 0.965), (0.22, 0.17, 0.018),
             (0.72, 0.66, 0.56, 1.0))
    make_box("TowelStack_2", (kx, 0.585, 0.982), (0.23, 0.165, 0.016), COL_STONE_BLU)
    # Towel bar on the cabinet's south end, one towel hanging
    make_cyl("TowelBar", (kx, 0.545, 0.78), 0.010, 0.30, COL_BRASS, axis='X')
    make_box("TowelHanging", (kx, 0.55, 0.63), (0.22, 0.012, 0.28), COL_LINEN)
    # Utensil crock — wooden spoons + whisk hint
    make_cyl("UtensilCrock", (kx, 2.14, 0.985), 0.052, 0.13, COL_STONE_BLU)
    for ui in range(3):
        make_cyl(f"Utensil_{ui}", (kx - 0.03 + ui * 0.03, 2.14 + (ui % 2) * 0.03 - 0.015,
                 1.115), 0.008, 0.16, COL_WOOD_LT)
    # Cup shelf above + Greta's cups
    make_box("CupShelf", (-2.86, 1.25, 1.52), (0.22, 1.20, 0.03), COL_WOOD)
    for ki2, sgn in enumerate((-1, +1)):
        make_box(f"CupShelf_Bracket_{ki2}", (-2.92, 1.25 + sgn * 0.52, 1.44),
                 (0.10, 0.03, 0.13), COL_IRON)
    for mi in range(5):
        tint = (COL_CREAM, COL_STONE_BLU, COL_CREAM, (0.72, 0.30, 0.22, 1.0), COL_CREAM)[mi]
        make_cyl(f"ShelfCup_{mi}_Body", (-2.85, 0.78 + mi * 0.24, 1.568), 0.036, 0.065, tint)
        make_box(f"ShelfCup_{mi}_Handle", (-2.80, 0.78 + mi * 0.24, 1.572),
                 (0.014, 0.012, 0.04), tint)
    # The wedding-photo on the wall behind the kettle (ch15_loft:
    # "the same brown eyes as Hans's wedding-photo on the wall
    # behind her") — sepia print, fir frame
    make_box("WeddingPhoto_Frame", (-2.88, 1.05, 2.02), (0.03, 0.34, 0.42), COL_WOOD_DARK)
    make_box("WeddingPhoto_Canvas", (-2.86, 1.05, 2.02), (0.02, 0.28, 0.36),
             (0.72, 0.62, 0.48, 1.0))
    for si2, sy2 in enumerate((0.98, 1.12)):
        make_box(f"WeddingPhoto_Figure_{si2}", (-2.845, sy2, 1.98), (0.008, 0.08, 0.20),
                 (0.42, 0.34, 0.26, 1.0))
    # ── Per's bench under the Hemlock window ─────────────────────
    make_box("Bench_Seat", (-2.62, 3.35, 0.44), (0.34, 1.10, 0.05), COL_WOOD)
    for bi2, sy3 in enumerate((2.92, 3.78)):
        make_box(f"Bench_Leg_{bi2}", (-2.62, sy3, 0.21), (0.30, 0.06, 0.42), COL_WOOD_DARK)
    make_box("Bench_Stretcher", (-2.62, 3.35, 0.14), (0.06, 0.86, 0.05), COL_WOOD_DARK)
    _cup_saucer("Bench_PerCup", -2.62, 3.02, 0.465, COL_STONE_BLU)
    # Broom in the NW corner — "They cleared. They wiped." is a
    # household liturgy in this room (ch17_aria)
    make_broom_mop("Broom", (-2.80, 4.55, 0.0))


# ═════════════════════════════════════════════════════════════════
# BACK DOOR + EAST WALL — the door Hans opens at five forty-eight,
# that Aud comes in through, that the cast disperses from into the
# alley (ch15_loft / ch17_bakery / ch18_stick). Closed fir leaf.
# The back-kitchen light above it is the foundation-report town
# marker ("Hans's back-kitchen light at four AM", ch15_loft). Hook
# rail with the spare apron; the bake slate; the doormat.
# ═════════════════════════════════════════════════════════════════
def build_back_door():
    wf = ROOM_W / 2.0 - 0.10        # 2.90 east wall inner face
    # Door surround + closed leaf, y 3.55..4.55
    for sgn in (-1, +1):
        make_box(f"BackDoor_Post_{sgn:+d}", (wf + 0.02, 4.05 + sgn * 0.54, 1.10),
                 (0.14, 0.08, 2.20), COL_WOOD)
    make_box("BackDoor_Header", (wf + 0.02, 4.05, 2.26), (0.10, 1.20, 0.12), COL_WOOD)
    make_box("BackDoor_Leaf", (wf + 0.05, 4.05, 1.08), (0.06, 0.96, 2.12), COL_WOOD_DARK)
    for pi in range(2):
        make_box(f"BackDoor_Panel_{pi}", (wf + 0.014, 4.05, 0.70 + pi * 0.85),
                 (0.008, 0.68, 0.62), COL_WOOD)
    make_cyl("BackDoor_Knob", (wf, 3.70, 1.02), 0.028, 0.05, COL_BRASS, axis='X')
    make_box("BackDoor_Deadbolt", (wf - 0.005, 3.70, 1.22), (0.02, 0.05, 0.08), COL_BRASS)
    make_door_hinges("BackDoor_Hinge", edge_x=wf - 0.01, edge_y=4.51,
                     edge_z_centers=[0.35, 1.05, 1.80], axis='Y')
    # THE BACK-KITCHEN LIGHT — small shaded fixture over the door,
    # on before four AM every working day
    make_cyl("DoorLight_Arm", (wf - 0.10, 4.05, 2.52), 0.012, 0.22, COL_IRON, axis='X')
    make_cyl("DoorLight_Shade", (wf - 0.22, 4.05, 2.46), 0.085, 0.09,
             (0.30, 0.28, 0.24, 1.0), segments=12)
    make_cyl("DoorLight_Bulb", (wf - 0.22, 4.05, 2.40), 0.038, 0.035,
             (0.98, 0.88, 0.62, 1.0))
    # Doormat inside the threshold
    make_box("BackDoor_Mat", (wf - 0.42, 4.05, 0.008), (0.55, 0.85, 0.012), P.RUBBER_MAT)
    # Hook rail south of the door — Hans's spare apron + a linen
    # towel (he is IN the other apron and the wool cap, ch17_bakery)
    make_box("HookRail", (wf + 0.02, 3.05, 1.68), (0.03, 0.70, 0.08), COL_WOOD)
    for hi, hy in enumerate((2.80, 3.05, 3.30)):
        make_cyl(f"HookRail_Peg_{hi}", (wf - 0.04, hy, 1.66), 0.013, 0.09, COL_BRASS, axis='X')
    make_box("Apron_Body", (wf - 0.07, 3.05, 1.28), (0.05, 0.30, 0.72), COL_APRON)
    make_box("Apron_Strap", (wf - 0.075, 3.05, 1.68), (0.04, 0.10, 0.10), COL_APRON)
    make_box("Apron_FlourSmudge", (wf - 0.10, 3.03, 1.30), (0.008, 0.16, 0.22), COL_FLOUR)
    make_box("HookTowel", (wf - 0.06, 2.80, 1.44), (0.04, 0.14, 0.40), COL_LINEN)
    # Bake slate north of the door — the day's list in chalk
    # (rows only; lettering scene-side as BakeSlate_Board)
    make_box("BakeSlate_Frame", (wf + 0.02, 4.83, 1.62), (0.03, 0.52, 0.68), COL_WOOD)
    make_box("BakeSlate_Board", (wf - 0.005, 4.83, 1.62), (0.02, 0.44, 0.60), COL_SLATE)
    for ri in range(4):
        make_box(f"BakeSlate_Row_{ri}", (wf - 0.02, 4.86, 1.84 - ri * 0.13),
                 (0.005, 0.30, 0.035), COL_CHALK)
    make_box("BakeSlate_ChalkTray", (wf - 0.02, 4.83, 1.26), (0.05, 0.40, 0.03), COL_WOOD)
    make_cyl("BakeSlate_Chalk", (wf - 0.035, 4.75, 1.29), 0.008, 0.06, COL_CHALK, axis='Y')


# ═════════════════════════════════════════════════════════════════
# SOUTH WALL — mostly behind the VN camera; just enough that turns
# of the establishing shot don't find bare drywall: apron hook on
# the SW pier, a five-gallon proofing bucket by the SE pier.
# ═════════════════════════════════════════════════════════════════
def build_south_wall():
    make_cyl("SW_Hook", (-1.9, 0.14, 1.70), 0.013, 0.09, COL_BRASS, axis='Y')
    make_box("SW_HookApron", (-1.9, 0.17, 1.32), (0.28, 0.05, 0.68), COL_APRON)
    make_cyl("SE_ProofBucket", (1.60, 0.35, 0.19), 0.16, 0.38, COL_CREAM, segments=12)
    make_cyl("SE_ProofBucketLid", (1.60, 0.35, 0.395), 0.165, 0.02, COL_WOOD_LT, segments=12)


# ═════════════════════════════════════════════════════════════════
# CEILING INFRA — warm pendants (three over the dining table, one
# over the worktable, one over the cooling table), smoke detector.
# No fluorescent tubes (canon-negative: Smolvud warmth).
# ═════════════════════════════════════════════════════════════════
def build_ceiling_infra():
    for nm, px, py in [("Pendant_Table_0", -1.5, 2.45), ("Pendant_Table_1", -0.3, 2.45),
                       ("Pendant_Table_2", 0.9, 2.45), ("Pendant_Work", 2.45, 1.5),
                       ("Pendant_Cool", -1.4, 4.35)]:
        _pendant(nm, px, py)
    make_smoke_detector("Smoke", (0.0, 2.5, CEIL))


def main():
    clear_scene()
    build_shell()
    build_window_and_exterior()
    build_dining_table()
    build_worktable()
    build_oven()
    build_cooling_table()
    build_kitchenette()
    build_back_door()
    build_south_wall()
    build_ceiling_infra()
    out = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)),
        "../../../assets/3d/locales/hans_bakery_back_kitchen.glb"))
    print(f"\n[build_hans_bakery_back_kitchen] exporting to {out}")
    export_glb(out)

if __name__ == "__main__":
    main()
