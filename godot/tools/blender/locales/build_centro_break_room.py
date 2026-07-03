"""
build_centro_break_room.py · v2 (hero pass)
══════════════════════════════════════════════════════════════════
VOL 6 · Centro Foods — the break room, off the dock corridor.
The four-AM-break room. One store, two rooms — this file and
build_centro_grocery_aisle.py share a byte-identical palette
block (KEEP IN SYNC marker below).

Canon sources (read before dressing):
  · vol6_ch10_night_shift.json — the room's own inventory: "a
    card table with four mismatched chairs. A microwave that has
    been at Centro since 2009. A refrigerator with a sign that
    says LABEL YOUR FOOD OR IT GETS THROWN OUT in a hand that
    is Jessa's. A bulletin board with a printed schedule and a
    printed inventory countdown — INVENTORY FRIDAY NIGHT — 12 AM
    SHARP — ALL HANDS — and a printed safety reminder from the
    corporate office about not propping the cooler doors with
    milk crates." Plus: the coffee pot Jessa keeps going on the
    counter (paper cups); a single exterior door onto the
    loading dock; Doug's chair against the back wall.
  · vol6_ch18_stockroom.json — "the radio above the microwave
    plays the Tejano station Marisol has, since 2019, put on
    every shift"; the small dishwasher Jessa runs at the end of
    every shift; the jacket hook by the door; the coffee pot
    ("Coffee's hot").
  · vol6_ch22_inventory.json — Russell's folded Express-News
    left on the table ("finish that crossword on the third
    page, kid"); Doug's chair against the wall; the break-room
    corridor to the dock.

Register: SAME STORE, BACK OF HOUSE. The corporate register is
present only as paper (the printed countdown, the corporate
safety memo, the teal letterhead); everything physical is worn
and personal — the 2009 microwave, the mismatched chairs, the
one hand-lettered sign in the whole building (Jessa's, on the
fridge). The contrast between printed and hand-lettered IS the
room.

Canon-negatives (deliberately NOT built):
  · NO vending machine (scaffold had one). The ch10 inventory
    doesn't include it and nobody buys from one all volume —
    food back here is from home (Marisol's tupperware, Russell's
    banana), from El Rancho, or from Jessa's coffee pot.
  · NO lockers. Belongings live on the jacket hooks and in the
    cubby behind the front register (ch16).
  · NO Muzak ceiling speaker. The corporate ambient loop is a
    sales-floor thing; the music back here is Marisol's Tejano
    radio above the microwave (ch18).
  · NO round pedestal table (scaffold had one) — canon says CARD
    TABLE: square top, thin tubular legs.
  · ONE fluorescent fixture, not two — a 5×4 m back room gets a
    single twin-tube housing.

Footprint (unchanged from scaffold / Background3D preset):
  Interior X ∈ [-2.5, +2.5], Y ∈ [0, +4], ceiling Z = 2.6
  Door gap at south centre (X ∈ [-1, +1]) → the dock corridor.
  Steel exterior door to the dock in the north wall.
  Card table centre; counter run on the east wall (the coffee
  pot's warm burner ties the scene's Fill light practical);
  fridge NW corner; bulletin board west wall.

Run:
    blender --background --python build_centro_break_room.py
Output:
    godot/assets/3d/locales/centro_break_room.glb
"""
import os, sys
_BT = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
if _BT not in sys.path: sys.path.insert(0, _BT)
from _props import palette as P
from _props.geometry import clear_scene, make_box, make_cyl, export_glb
from _props.structure import make_floor, make_wall, make_ceiling, make_door_hinges
from _props.decor import make_wall_clock
from _props.cleaning import make_trash_can
from _props.food_service import make_paper_cup_stack, make_sugar_creamer_caddy
from _props.safety import (make_smoke_detector, make_hvac_vent,
                           make_fluorescent_tube_fixture)

ROOM_W = 5.0; ROOM_D = 4.0; CEIL = 2.6

# ═══ CENTRO FOODS SHARED PALETTE — KEEP IN SYNC ══════════════════
# One store, two rooms: this block is byte-identical in
# build_centro_grocery_aisle.py and build_centro_break_room.py.
# If you edit a constant here, edit BOTH files and verify:
#   awk '/CENTRO_PALETTE_BEGIN/,/CENTRO_PALETTE_END/' <file> | md5sum
# CENTRO_PALETTE_BEGIN
BRAND_TEAL       = (0.16, 0.42, 0.44, 1.0)   # Centro Foods teal — the polo color (vol6 ch10)
BRAND_TEAL_DARK  = (0.10, 0.28, 0.30, 1.0)
BRAND_CREAM      = (0.94, 0.92, 0.84, 1.0)   # sign lettering band
COL_FLOOR_SALES  = (0.80, 0.79, 0.74, 1.0)   # buffed VCT, sales floor
COL_FLOOR_BACK   = (0.62, 0.58, 0.52, 1.0)   # scuffed back-of-house vinyl
COL_FLOOR_SEAM   = (0.55, 0.53, 0.48, 1.0)
COL_FLOOR_SCUFF  = (0.44, 0.42, 0.38, 1.0)
COL_WALL_SALES   = (0.90, 0.89, 0.85, 1.0)
COL_WALL_BACK    = (0.78, 0.76, 0.68, 1.0)
COL_BASEBOARD    = (0.36, 0.35, 0.33, 1.0)
COL_STEEL        = (0.66, 0.68, 0.70, 1.0)
COL_METAL_DARK   = (0.22, 0.22, 0.24, 1.0)
COL_GONDOLA      = (0.88, 0.88, 0.86, 1.0)   # white shelving steel
COL_CARDBOARD    = (0.72, 0.56, 0.38, 1.0)
COL_PALLET_WOOD  = (0.60, 0.48, 0.34, 1.0)
COL_CAN_LID      = (0.78, 0.80, 0.82, 1.0)
# One tint per planogram run — chain shelf discipline (Gas & Go
# lesson: the register lives in the geometry).
CENTRO_CAN_RUNS = [
    (0.72, 0.28, 0.22, 1.0),   # stewed-tomato red (vol6 ch10)
    (0.86, 0.74, 0.44, 1.0),   # corn gold
    (0.44, 0.54, 0.36, 1.0),   # green-bean sage
    (0.92, 0.88, 0.78, 1.0),   # cream-of-mushroom (vol6 ch22, row 4F)
    (0.36, 0.44, 0.56, 1.0),   # house-brand blue
    (0.78, 0.52, 0.28, 1.0),   # chicken-soup amber
]
CENTRO_DRY_RUNS = [
    (0.86, 0.66, 0.34, 1.0),   # honey-oat gold
    (0.94, 0.82, 0.52, 1.0),   # cream wheat
    (0.56, 0.58, 0.42, 1.0),   # sage olive
    (0.62, 0.38, 0.26, 1.0),   # bran rust
    (0.42, 0.52, 0.56, 1.0),   # muted teal (house brand)
]
# CENTRO_PALETTE_END

PAL_WALL = {"wall": COL_WALL_BACK, "baseboard": COL_BASEBOARD}

# Break-room-only shades
COL_ALMOND_AGED  = (0.84, 0.82, 0.74, 1.0)   # 2009-appliance almond
COL_CABINET      = (0.58, 0.50, 0.40, 1.0)
COL_COUNTERTOP   = (0.70, 0.62, 0.48, 1.0)
COL_CORK         = (0.60, 0.44, 0.30, 1.0)
COL_MARKER_INK   = (0.16, 0.16, 0.20, 1.0)   # Jessa's hand
COL_COFFEE       = (0.16, 0.10, 0.06, 1.0)
COL_BURNER_GLOW  = (1.00, 0.78, 0.32, 1.0)   # the pot Jessa keeps going


# ════════════════════════════════════════════════════════════════
# SHELL — footprint unchanged; back-of-house beige, no crown
# molding, hand-placed ceiling stains (the default stain spread
# would land outside this small footprint).
# ════════════════════════════════════════════════════════════════
def build_shell():
    make_floor("Floor", (0.0, ROOM_D / 2.0, 0.0),
               size_x=ROOM_W + 0.4, size_y=ROOM_D + 0.4,
               palette={"vinyl": COL_FLOOR_BACK, "seam": COL_FLOOR_SEAM})
    for nm, x, bb in [("Wall_W", -ROOM_W / 2.0, +1), ("Wall_E", +ROOM_W / 2.0, -1)]:
        make_wall(nm, (x, ROOM_D / 2.0, 0), length=ROOM_D + 0.4, height=CEIL,
                  axis='Y', palette=PAL_WALL, baseboard_face_sign=bb)
    make_wall("Wall_N", (0.0, ROOM_D, 0), length=ROOM_W + 0.4, height=CEIL,
              axis='X', palette=PAL_WALL, baseboard_face_sign=-1)
    make_wall("Wall_S_W", (-(ROOM_W / 4.0 + 0.5), 0.0, 0),
              length=ROOM_W / 2.0 - 1.0, height=CEIL, axis='X', palette=PAL_WALL)
    make_wall("Wall_S_E", (+(ROOM_W / 4.0 + 0.5), 0.0, 0),
              length=ROOM_W / 2.0 - 1.0, height=CEIL, axis='X', palette=PAL_WALL)
    make_box("Wall_S_AboveDoor", (0.0, 0.0, CEIL - 0.30), (2.0, 0.20, 0.60),
             COL_WALL_BACK)
    make_ceiling("Ceil", (0.0, ROOM_D / 2.0, CEIL),
                 size_x=ROOM_W + 0.4, size_y=ROOM_D + 0.4, with_stains=False)
    for si, (sx, sy) in enumerate([(-1.2, 3.2), (0.8, 1.0)]):
        make_box(f"CentroB_CeilStain_{si}", (sx, sy, CEIL + 0.025),
                 (0.70, 0.70, 0.003), P.CEILING_STAIN)
    # Worn entry mat inside the corridor door
    make_box("CentroB_EntryMat", (0.0, 0.55, 0.012),
             (1.40, 0.70, 0.02), P.RUBBER_MAT)


# ════════════════════════════════════════════════════════════════
# CARD TABLE + FOUR MISMATCHED CHAIRS (vol6 ch10 — the canon
# furniture list). Square folding-leg card table, and four chairs
# that agree on nothing: a metal folding chair, a wooden kitchen
# chair, a faded plastic stacker, and a cast-off office chair.
# Russell's folded Express-News sits on the table (ch22).
# ════════════════════════════════════════════════════════════════
TABLE_X, TABLE_Y = 0.0, 2.0

def build_card_table():
    tx, ty = TABLE_X, TABLE_Y
    make_box("CentroB_CardTable_Top", (tx, ty, 0.72),
             (0.90, 0.90, 0.045), (0.52, 0.42, 0.30, 1.0))
    for ei, (exo, eyo, w, d) in enumerate([
            (0.0, -0.45, 0.92, 0.03), (0.0, +0.45, 0.92, 0.03),
            (-0.45, 0.0, 0.03, 0.92), (+0.45, 0.0, 0.03, 0.92)]):
        make_box(f"CentroB_CardTable_Edge_{ei}", (tx + exo, ty + eyo, 0.72),
                 (w, d, 0.05), COL_METAL_DARK)
    for li, (lxo, lyo) in enumerate([(-0.38, -0.38), (+0.38, -0.38),
                                     (-0.38, +0.38), (+0.38, +0.38)]):
        make_cyl(f"CentroB_CardTable_Leg_{li}", (tx + lxo, ty + lyo, 0.35),
                 0.018, 0.70, COL_METAL_DARK)
    # Russell's folded newspaper, left for the kid (ch22).
    # Table top surface is z = 0.72 + 0.0225 = 0.7425.
    make_box("CentroB_ExpressNews_Bottom", (tx + 0.18, ty + 0.12, 0.7475),
             (0.32, 0.24, 0.010), P.NEWSPRINT)
    make_box("CentroB_ExpressNews_Top", (tx + 0.16, ty + 0.14, 0.7565),
             (0.30, 0.22, 0.008), P.NEWSPRINT)
    make_box("CentroB_ExpressNews_Fold", (tx + 0.03, ty + 0.13, 0.754),
             (0.02, 0.24, 0.014), P.PAPER_AGED)
    # A paper coffee cup somebody hasn't bussed yet
    make_cyl("CentroB_TableCup", (tx - 0.26, ty - 0.20, 0.79),
             0.040, 0.095, P.PAPER)


def _chair_folding(tag, cx, cy, back_dx, back_dy, tint):
    """Metal folding chair — thin frame, hard panels."""
    make_box(f"CentroB_Chair{tag}_Seat", (cx, cy, 0.45),
             (0.40, 0.40, 0.025), tint)
    make_box(f"CentroB_Chair{tag}_Back",
             (cx + back_dx * 0.19, cy + back_dy * 0.19, 0.78),
             (0.40 if back_dy else 0.03, 0.40 if back_dx else 0.03, 0.36), tint)
    for li, (lxo, lyo) in enumerate([(-0.17, -0.17), (+0.17, -0.17),
                                     (-0.17, +0.17), (+0.17, +0.17)]):
        make_cyl(f"CentroB_Chair{tag}_Leg_{li}", (cx + lxo, cy + lyo, 0.22),
                 0.012, 0.44, COL_METAL_DARK)


def build_chairs():
    tx, ty = TABLE_X, TABLE_Y
    # 1 · metal folding chair, sage-gray (south seat, faces table)
    _chair_folding("Fold", tx, ty - 0.72, 0, -1, (0.44, 0.48, 0.42, 1.0))
    # 2 · wooden kitchen chair (east seat)
    wx, wy, wood = tx + 0.72, ty, (0.52, 0.38, 0.24, 1.0)
    make_box("CentroB_ChairWood_Seat", (wx, wy, 0.45), (0.42, 0.42, 0.04), wood)
    for li, (lxo, lyo) in enumerate([(-0.18, -0.18), (+0.18, -0.18),
                                     (-0.18, +0.18), (+0.18, +0.18)]):
        make_box(f"CentroB_ChairWood_Leg_{li}", (wx + lxo, wy + lyo, 0.22),
                 (0.04, 0.04, 0.44), wood)
    for pi in (-1, +1):
        make_box(f"CentroB_ChairWood_Post_{pi:+d}", (wx + 0.19, wy + pi * 0.18, 0.72),
                 (0.04, 0.04, 0.58), wood)
    for si2, sz in enumerate([0.72, 0.86, 1.00]):
        make_box(f"CentroB_ChairWood_Slat_{si2}", (wx + 0.19, wy, sz),
                 (0.03, 0.34, 0.06), wood)
    # 3 · faded plastic stacking chair (west seat)
    px, py, shell = tx - 0.72, ty, (0.80, 0.52, 0.30, 1.0)
    make_box("CentroB_ChairPlastic_Seat", (px, py, 0.44), (0.42, 0.40, 0.05), shell)
    make_box("CentroB_ChairPlastic_Back", (px - 0.20, py, 0.72), (0.05, 0.40, 0.50), shell)
    for li, (lxo, lyo) in enumerate([(-0.16, -0.16), (+0.16, -0.16),
                                     (-0.16, +0.16), (+0.16, +0.16)]):
        make_cyl(f"CentroB_ChairPlastic_Leg_{li}", (px + lxo, py + lyo, 0.21),
                 0.014, 0.42, COL_STEEL)
    # 4 · cast-off office chair (north seat)
    ox, oy, navy = tx, ty + 0.72, (0.28, 0.32, 0.44, 1.0)
    make_box("CentroB_ChairOffice_Seat", (ox, oy, 0.48), (0.44, 0.44, 0.09), navy)
    make_box("CentroB_ChairOffice_Back", (ox, oy + 0.22, 0.82), (0.42, 0.08, 0.46), navy)
    make_cyl("CentroB_ChairOffice_Post", (ox, oy, 0.28), 0.025, 0.34, COL_METAL_DARK)
    make_cyl("CentroB_ChairOffice_Base", (ox, oy, 0.06), 0.24, 0.05,
             COL_METAL_DARK, segments=10)
    # 5 · Doug's chair, against the back wall (ch10/ch18/ch22 —
    # "the chair against the back wall"), facing the room.
    _chair_folding("Doug", 1.60, 3.62, 0, +1, (0.40, 0.44, 0.48, 1.0))


# ════════════════════════════════════════════════════════════════
# REFRIGERATOR — NW corner, with THE hand-lettered sign (Jessa's
# hand, ch10): LABEL YOUR FOOD OR IT GETS THROWN OUT. Marker
# strokes abstracted as uneven ink bands — deliberately crooked
# next to all the printed paper in this store.
# ════════════════════════════════════════════════════════════════
def build_fridge():
    fx, fy = -2.02, 3.38
    make_box("CentroB_Fridge_Body", (fx, fy, 0.85), (0.70, 0.68, 1.70),
             COL_ALMOND_AGED)
    make_box("CentroB_Fridge_DoorSeam", (fx, fy - 0.345, 1.12),
             (0.66, 0.005, 0.015), COL_BASEBOARD)
    for hz, hh in [(1.32, 0.26), (0.84, 0.38)]:
        make_box(f"CentroB_Fridge_Handle_{int(hz*100)}",
                 (fx + 0.26, fy - 0.37, hz), (0.035, 0.03, hh), COL_METAL_DARK)
    # Jessa's sign — taped a little off square (offset strips)
    make_box("CentroB_Fridge_Sign", (fx - 0.04, fy - 0.348, 1.42),
             (0.30, 0.005, 0.22), P.PAPER)
    for bi, (bxo, bw) in enumerate([(-0.02, 0.24), (0.02, 0.18), (-0.01, 0.22)]):
        make_box(f"CentroB_Fridge_SignInk_{bi}",
                 (fx - 0.04 + bxo, fy - 0.351, 1.48 - bi * 0.055),
                 (bw, 0.002, 0.030), COL_MARKER_INK)
    make_box("CentroB_Fridge_SignTape", (fx - 0.04, fy - 0.352, 1.525),
             (0.08, 0.002, 0.025), (0.86, 0.84, 0.78, 1.0))
    for mi, mcol in enumerate([(0.72, 0.28, 0.22, 1.0),
                               (0.36, 0.44, 0.56, 1.0),
                               (0.86, 0.74, 0.44, 1.0)]):
        make_cyl(f"CentroB_Fridge_Magnet_{mi}",
                 (fx - 0.18 + mi * 0.10, fy - 0.348, 1.02),
                 0.018, 0.008, mcol, axis='Y')


# ════════════════════════════════════════════════════════════════
# COUNTER RUN — east wall. The coffee pot Jessa keeps going (its
# amber burner is the practical for the scene's warm Fill light),
# paper cups, sugar caddy, the 2009 microwave, Marisol's Tejano
# radio on a shelf ABOVE the microwave (ch18), and the small
# dishwasher below (ch18).
# ════════════════════════════════════════════════════════════════
def build_counter():
    face_x = ROOM_W / 2.0 - 0.10          # east wall interior face
    cx = face_x - 0.30                    # counter centreline
    run_cy, run_l = 2.10, 2.00
    make_box("CentroB_Counter_Base", (cx, run_cy, 0.44),
             (0.56, run_l, 0.88), COL_CABINET)
    make_box("CentroB_Counter_Top", (cx - 0.02, run_cy, 0.90),
             (0.62, run_l + 0.04, 0.04), COL_COUNTERTOP)
    make_box("CentroB_Counter_Backsplash", (face_x - 0.02, run_cy, 1.00),
             (0.03, run_l, 0.16), COL_COUNTERTOP)
    for di, dy in enumerate([1.55, 2.65]):
        make_box(f"CentroB_Counter_DoorSeam_{di}", (cx - 0.285, dy, 0.42),
                 (0.005, 0.015, 0.72), COL_BASEBOARD)
        make_box(f"CentroB_Counter_Knob_{di}", (cx - 0.30, dy + 0.12, 0.70),
                 (0.02, 0.03, 0.03), COL_METAL_DARK)
    # ── Coffee machine + the pot that is always going ────────────
    # L-shaped drip machine: base plate + rear tower + brew head
    # overhanging the pot. The pot sits in the OPEN front recess —
    # never buried inside a solid body (playbook: audit
    # intersections). Counter top surface is z = 0.92.
    mx, my = cx + 0.06, 2.72
    make_box("CentroB_Coffee_BasePlate", (mx, my, 0.935),
             (0.26, 0.30, 0.03), COL_METAL_DARK)
    make_box("CentroB_Coffee_Tower", (mx + 0.09, my, 1.15),
             (0.10, 0.30, 0.40), COL_METAL_DARK)
    make_box("CentroB_Coffee_Head", (mx, my, 1.30),
             (0.28, 0.30, 0.10), COL_METAL_DARK)
    make_box("CentroB_Coffee_Basket", (mx - 0.02, my, 1.21),
             (0.10, 0.16, 0.06), COL_STEEL)
    make_cyl("CentroB_Coffee_Burner", (mx - 0.05, my, 0.958),
             0.10, 0.015, COL_BURNER_GLOW, segments=10)
    make_cyl("CentroB_Coffee_Pot", (mx - 0.05, my, 1.04),
             0.085, 0.14, COL_COFFEE, segments=10)
    make_cyl("CentroB_Coffee_PotRim", (mx - 0.05, my, 1.115),
             0.088, 0.012, COL_STEEL, segments=10)
    make_box("CentroB_Coffee_PotHandle", (mx - 0.17, my, 1.05),
             (0.035, 0.03, 0.10), COL_METAL_DARK)
    make_box("CentroB_Coffee_Switch", (mx + 0.09, my - 0.16, 1.00),
             (0.02, 0.005, 0.03), (0.86, 0.42, 0.32, 1.0))
    make_paper_cup_stack("CentroB_Cups", (cx + 0.10, 2.40, 0.928), count=12)
    make_sugar_creamer_caddy("CentroB_Caddy", (cx + 0.05, 2.14, 0.96))
    # ── The 2009 microwave (ch10) ────────────────────────────────
    wx, wy = cx + 0.02, 1.42
    make_box("CentroB_Microwave_Body", (wx, wy, 1.08), (0.42, 0.55, 0.32),
             COL_ALMOND_AGED)
    make_box("CentroB_Microwave_Door", (wx - 0.215, wy - 0.06, 1.08),
             (0.01, 0.38, 0.26), (0.16, 0.16, 0.18, 1.0))
    make_box("CentroB_Microwave_Handle", (wx - 0.225, wy - 0.27, 1.08),
             (0.015, 0.03, 0.24), COL_METAL_DARK)
    make_box("CentroB_Microwave_Clock", (wx - 0.215, wy + 0.17, 1.16),
             (0.005, 0.08, 0.03), (0.32, 0.62, 0.42, 1.0))
    # ── Marisol's radio, on a shelf above the microwave (ch18) ───
    sx, sy = face_x - 0.20, 1.42
    make_box("CentroB_RadioShelf", (sx, sy, 1.62), (0.36, 0.50, 0.03),
             COL_CABINET)
    for bi2, byo in enumerate([-0.18, +0.18]):
        make_box(f"CentroB_RadioShelf_Bracket_{bi2}",
                 (face_x - 0.06, sy + byo, 1.54), (0.10, 0.03, 0.14), COL_STEEL)
    make_box("CentroB_Radio_Body", (sx, sy, 1.72), (0.18, 0.32, 0.16),
             (0.26, 0.24, 0.24, 1.0))
    make_box("CentroB_Radio_Grille", (sx - 0.093, sy - 0.06, 1.72),
             (0.005, 0.14, 0.12), (0.40, 0.38, 0.36, 1.0))
    for ki, kyo in enumerate([0.09, 0.14]):
        make_cyl(f"CentroB_Radio_Knob_{ki}", (sx - 0.095, sy + kyo, 1.70),
                 0.014, 0.012, COL_STEEL, axis='X')
    make_cyl("CentroB_Radio_Antenna", (sx + 0.05, sy + 0.13, 1.94),
             0.004, 0.30, COL_STEEL)
    # ── The small dishwasher Jessa runs every shift-end (ch18) ───
    make_box("CentroB_Dishwasher_Front", (cx - 0.295, 1.10, 0.46),
             (0.02, 0.52, 0.68), COL_STEEL)
    make_box("CentroB_Dishwasher_Bar", (cx - 0.315, 1.10, 0.72),
             (0.02, 0.40, 0.03), COL_METAL_DARK)
    make_box("CentroB_Dishwasher_Light", (cx - 0.307, 1.30, 0.60),
             (0.005, 0.02, 0.02), (0.32, 0.62, 0.42, 1.0))
    # Trash can at the counter's south end
    make_trash_can("CentroB_Trash", (1.55, 0.55, 0.0),
                   palette={"body": (0.45, 0.46, 0.44, 1.0)}, branded=False)


# ════════════════════════════════════════════════════════════════
# BULLETIN BOARD — west wall. Everything on it is PRINTED (the
# corporate register): the schedule grid, the inventory countdown
# (INVENTORY FRIDAY NIGHT — 12 AM SHARP — ALL HANDS, with its red
# urgency band), and the corporate safety memo about not propping
# the cooler doors with milk crates (teal letterhead). ch10.
# ════════════════════════════════════════════════════════════════
def build_bulletin_board():
    face_x = -(ROOM_W / 2.0 - 0.10)       # west wall interior face
    bx = face_x + 0.035
    by, bz = 1.70, 1.50
    make_box("CentroB_Board_Cork", (bx, by, bz), (0.05, 1.30, 0.85), COL_CORK)
    for fi, (fyo, fzo, w, h) in enumerate([
            (0.0, +0.44, 1.36, 0.04), (0.0, -0.44, 1.36, 0.04),
            (-0.67, 0.0, 0.04, 0.92), (+0.67, 0.0, 0.04, 0.92)]):
        make_box(f"CentroB_Board_Frame_{fi}", (bx, by + fyo, bz + fzo),
                 (0.06, w, h), COL_PALLET_WOOD)
    px = bx + 0.030
    # Printed schedule grid
    make_box("CentroB_Board_Schedule", (px, by - 0.38, bz + 0.10),
             (0.005, 0.30, 0.40), P.PAPER)
    for ri in range(4):
        make_box(f"CentroB_Board_ScheduleRow_{ri}",
                 (px + 0.003, by - 0.38, bz + 0.24 - ri * 0.09),
                 (0.002, 0.24, 0.010), COL_METAL_DARK)
    # INVENTORY FRIDAY NIGHT — 12 AM SHARP — ALL HANDS
    make_box("CentroB_Board_Countdown", (px, by + 0.02, bz + 0.14),
             (0.005, 0.34, 0.26), P.PAPER)
    make_box("CentroB_Board_CountdownBand", (px + 0.003, by + 0.02, bz + 0.21),
             (0.002, 0.30, 0.06), (0.72, 0.28, 0.22, 1.0))
    make_box("CentroB_Board_CountdownText", (px + 0.003, by + 0.02, bz + 0.10),
             (0.002, 0.26, 0.05), COL_MARKER_INK)
    # Corporate safety memo — teal letterhead, small print
    make_box("CentroB_Board_SafetyMemo", (px, by + 0.42, bz + 0.08),
             (0.005, 0.24, 0.32), P.PAPER)
    make_box("CentroB_Board_SafetyHead", (px + 0.003, by + 0.42, bz + 0.20),
             (0.002, 0.20, 0.05), BRAND_TEAL)
    for ri in range(3):
        make_box(f"CentroB_Board_SafetyLine_{ri}",
                 (px + 0.003, by + 0.42, bz + 0.11 - ri * 0.05),
                 (0.002, 0.18, 0.015), COL_METAL_DARK)
    # An older, sun-aged posting nobody has taken down
    make_box("CentroB_Board_OldNotice", (px, by - 0.05, bz - 0.26),
             (0.005, 0.22, 0.16), P.PAPER_AGED)
    for pi2, (pyo, pzo, pcol) in enumerate([
            (-0.38, 0.31, (0.72, 0.28, 0.22, 1.0)),
            (+0.02, 0.28, (0.36, 0.44, 0.56, 1.0)),
            (+0.42, 0.25, (0.86, 0.74, 0.44, 1.0)),
            (-0.05, -0.17, (0.44, 0.54, 0.36, 1.0))]):
        make_cyl(f"CentroB_Board_Pin_{pi2}", (px + 0.006, by + pyo, bz + pzo),
                 0.010, 0.012, pcol, axis='X')


# ════════════════════════════════════════════════════════════════
# DOCK DOOR + HOOKS + CLOCK — the single exterior door onto the
# loading dock (ch10; Diego's second-break door), the jacket
# hooks by the corridor door (ch18), and the wall clock frozen
# at 4:03 — the minute Jessa walks in on every four-AM break.
# ════════════════════════════════════════════════════════════════
def build_doors_and_walls():
    face_y = ROOM_D - 0.10                # north wall interior face
    # Steel dock door, north wall west-of-centre. x = -1.00 keeps
    # the frame 16cm clear of the fridge's swing zone (fridge east
    # face at x = -1.67).
    dx = -1.00
    make_box("CentroB_DockDoor", (dx, face_y - 0.04, 1.02),
             (0.90, 0.06, 2.05), (0.46, 0.50, 0.54, 1.0))
    make_box("CentroB_DockDoor_Frame_T", (dx, face_y - 0.045, 2.10),
             (1.02, 0.07, 0.10), COL_METAL_DARK)
    for sgn in (-1, +1):
        make_box(f"CentroB_DockDoor_Frame_{sgn:+d}",
                 (dx + sgn * 0.51, face_y - 0.045, 1.02),
                 (0.06, 0.07, 2.05), COL_METAL_DARK)
    make_cyl("CentroB_DockDoor_PanicBar", (dx, face_y - 0.10, 1.02),
             0.022, 0.62, COL_STEEL, axis='X')
    make_box("CentroB_DockDoor_Kick", (dx, face_y - 0.075, 0.18),
             (0.80, 0.01, 0.30), COL_STEEL)
    make_door_hinges("CentroB_DockDoor_Hinge",
                     edge_x=dx - 0.44, edge_y=face_y - 0.04,
                     edge_z_centers=[0.35, 1.02, 1.70], axis='X')
    make_box("CentroB_DockSign_BG", (dx, face_y - 0.02, 2.28),
             (0.50, 0.02, 0.16), BRAND_TEAL_DARK)
    make_box("CentroB_DockSign_Text", (dx, face_y - 0.035, 2.28),
             (0.36, 0.005, 0.07), BRAND_CREAM)
    # Wall clock, north wall, frozen at 4:03 — Jessa comes in at
    # four oh-three on every break (ch10).
    make_wall_clock("CentroB_Clock", (0.55, face_y - 0.02, 2.05),
                    frozen_hour=4, frozen_min=3)
    # Jacket hooks inside the corridor door (ch18 — Diego "pulls
    # his jacket off the hook"), on the SE wall segment.
    hy = 0.12
    make_box("CentroB_HookRail", (1.75, hy + 0.02, 1.62),
             (0.90, 0.03, 0.06), COL_PALLET_WOOD)
    for hi in range(4):
        make_cyl(f"CentroB_Hook_{hi}", (1.45 + hi * 0.20, hy + 0.06, 1.58),
                 0.013, 0.09, COL_METAL_DARK, axis='Y')


# ════════════════════════════════════════════════════════════════
# CEILING INFRA + FLOOR WEAR — one twin-tube fluorescent (small
# back room, single fixture), smoke detector, HVAC. NO Muzak
# speaker back here (canon-negative — the radio is the music).
# ════════════════════════════════════════════════════════════════
def build_ceiling_infra():
    make_fluorescent_tube_fixture("CentroB_Fluor", (0.0, 2.0, CEIL),
                                  length=1.30, width=0.32)
    make_smoke_detector("CentroB_Smoke", (-1.2, 1.3, CEIL))
    make_hvac_vent("CentroB_HVAC", (-1.25, 3.45, CEIL), width=0.70, depth=0.35)


def build_floor_details():
    for i, (sx, sy) in enumerate([
            (0.0, 1.05), (0.35, 1.75), (-0.4, 2.3),
            (1.75, 1.5), (-1.9, 2.9)]):
        make_box(f"CentroB_Scuff_{i}", (sx, sy, 0.008),
                 (0.26, 0.16, 0.001), COL_FLOOR_SCUFF)


def main():
    clear_scene()
    build_shell()
    build_card_table()
    build_chairs()
    build_fridge()
    build_counter()
    build_bulletin_board()
    build_doors_and_walls()
    build_ceiling_infra()
    build_floor_details()
    out = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)),
        "../../../assets/3d/locales/centro_break_room.glb"))
    print(f"\n[build_centro_break_room] exporting to {out}")
    export_glb(out)


if __name__ == "__main__":
    main()
