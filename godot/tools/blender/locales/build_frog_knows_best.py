"""XXI · WORLD — Frog Knows Best, Aquarium & Bait Shop. Small
wooden roadside shop, screened porch attached. Inside: a column
of three glass aquarium tanks N (bayou minnow / cypress catfish /
the namesake bullfrog), retail counter S, walls of bait-and-tackle
peg displays, a chest cooler of nightcrawlers. Painted frog above
the door. The World card — the loop completed in a small tank.
"""
import os, sys
_BT = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
if _BT not in sys.path: sys.path.insert(0, _BT)
from _props import palette as P
from _props.geometry import clear_scene, make_box, make_cyl, export_glb
from _props.structure import make_floor, make_wall, make_ceiling, make_crown_molding
from _props.decor import make_wall_clock, make_calendar, make_faded_poster
from _props.safety import (make_smoke_detector, make_sprinkler,
                            make_fluorescent_tube_fixture, make_bug_zapper)
from _props.signage import make_hanging_banner

PAL = {"wall": (0.62, 0.46, 0.28, 1.0), "baseboard": (0.32, 0.22, 0.16, 1.0)}
COL_FLOOR_WOOD = (0.52, 0.36, 0.24, 1.0); COL_SEAM = (0.32, 0.22, 0.16, 1.0)
COL_COUNTER = (0.42, 0.30, 0.22, 1.0); COL_COUNTER_TOP = (0.62, 0.42, 0.28, 1.0)
COL_TANK_FRAME = (0.18, 0.18, 0.20, 1.0); COL_TANK_GLASS = (0.62, 0.84, 0.86, 0.55)
COL_WATER_MURKY = (0.32, 0.46, 0.32, 0.65); COL_GRAVEL = (0.42, 0.38, 0.32, 1.0)
COL_FROG_GREEN = (0.32, 0.62, 0.36, 1.0); COL_FROG_BELLY = (0.86, 0.84, 0.62, 1.0)
COL_CATFISH = (0.32, 0.28, 0.22, 1.0); COL_MINNOW = (0.74, 0.78, 0.82, 1.0)
COL_PLANT_WET = (0.32, 0.52, 0.30, 1.0); COL_PEGBOARD = (0.62, 0.46, 0.30, 1.0)
COL_LURE_R = (0.86, 0.32, 0.20, 1.0); COL_LURE_Y = (0.96, 0.86, 0.42, 1.0)
COL_LURE_B = (0.20, 0.42, 0.74, 1.0); COL_TIN_ROOF = (0.62, 0.62, 0.62, 1.0)
COL_FROG_SIGN = (0.32, 0.62, 0.36, 1.0); COL_NIGHTCRAWLER_BOX = (0.86, 0.78, 0.62, 1.0)

ROOM_W = 6.0; ROOM_D = 7.0; CEIL = 2.80


def build_shell():
    make_floor("Floor", (0.0, ROOM_D/2.0, 0.0), size_x=ROOM_W+0.4, size_y=ROOM_D+0.4,
               palette={"vinyl": COL_FLOOR_WOOD, "seam": COL_SEAM})
    for nm, x, bb in [("Wall_W", -ROOM_W/2.0, +1), ("Wall_E", +ROOM_W/2.0, -1)]:
        make_wall(nm, (x, ROOM_D/2.0, 0), length=ROOM_D+0.4, height=CEIL, axis='Y',
                  palette=PAL, baseboard_face_sign=bb)
    make_wall("Wall_N", (0.0, ROOM_D, 0), length=ROOM_W+0.4, height=CEIL, axis='X',
              palette=PAL, baseboard_face_sign=-1)
    # S wall — door + screened-porch opening (no glass, open frame)
    make_wall("Wall_S_W", (-2.20, 0.0, 0), length=1.40, height=CEIL, axis='X', palette=PAL)
    make_wall("Wall_S_E", (+2.20, 0.0, 0), length=1.40, height=CEIL, axis='X', palette=PAL)
    make_ceiling("Ceil", (0.0, ROOM_D/2.0, CEIL), size_x=ROOM_W+0.4, size_y=ROOM_D+0.4)
    for nm, ax, length, wx, wy in [("Crown_W",'Y',ROOM_D,-ROOM_W/2.0+0.10,ROOM_D/2.0),
                                    ("Crown_E",'Y',ROOM_D,+ROOM_W/2.0-0.10,ROOM_D/2.0),
                                    ("Crown_N",'X',ROOM_W,0.0,ROOM_D-0.10)]:
        make_crown_molding(nm, wall_x=wx, wall_y=wy, length=length, axis=ax,
                           ceil_z=CEIL, palette={"wood": COL_COUNTER})


def build_aquarium_tanks():
    # Three side-by-side tanks on a long shelf along the N wall
    shelf_y = ROOM_D - 0.50
    make_box("Tank_Shelf", (0.0, shelf_y, 0.80), (5.20, 0.80, 0.06), COL_COUNTER)
    make_box("Tank_Shelf_Front", (0.0, shelf_y - 0.40, 0.40),
             (5.20, 0.04, 0.80), COL_COUNTER)
    for ti, (tx, label, water, fish_color) in enumerate([
        (-1.70, "Minnows",    COL_WATER_MURKY, COL_MINNOW),
        (+0.00, "Catfish",    COL_WATER_MURKY, COL_CATFISH),
        (+1.70, "Frog",       COL_WATER_MURKY, COL_FROG_GREEN),
    ]):
        # Tank glass walls (5 sides)
        make_box(f"Tank_{ti}_Glass_F", (tx, shelf_y - 0.30, 1.30),
                 (1.40, 0.005, 0.96), COL_TANK_GLASS)
        make_box(f"Tank_{ti}_Glass_B", (tx, shelf_y + 0.30, 1.30),
                 (1.40, 0.005, 0.96), COL_TANK_GLASS)
        make_box(f"Tank_{ti}_Glass_W", (tx - 0.70, shelf_y, 1.30),
                 (0.005, 0.62, 0.96), COL_TANK_GLASS)
        make_box(f"Tank_{ti}_Glass_E", (tx + 0.70, shelf_y, 1.30),
                 (0.005, 0.62, 0.96), COL_TANK_GLASS)
        # Tank frame (top + bottom rims)
        for fz in [0.84, 1.80]:
            make_box(f"Tank_{ti}_Frame_F_{fz:.0f}", (tx, shelf_y - 0.30, fz),
                     (1.42, 0.04, 0.04), COL_TANK_FRAME)
            make_box(f"Tank_{ti}_Frame_B_{fz:.0f}", (tx, shelf_y + 0.30, fz),
                     (1.42, 0.04, 0.04), COL_TANK_FRAME)
        # Water + gravel
        make_box(f"Tank_{ti}_Water", (tx, shelf_y, 1.30), (1.30, 0.55, 0.80), water)
        make_box(f"Tank_{ti}_Gravel", (tx, shelf_y, 0.92), (1.30, 0.55, 0.10), COL_GRAVEL)
        # Plants in tank
        for pi in range(3):
            px_ = tx - 0.40 + pi * 0.40
            make_box(f"Tank_{ti}_Plant_{pi}", (px_, shelf_y + 0.10, 1.30),
                     (0.04, 0.06, 0.50), COL_PLANT_WET)
        # Fish / occupant
        if ti == 0:  # minnow shoal
            for mi in range(6):
                mx = tx - 0.40 + (mi % 3) * 0.40
                mz = 1.20 + (mi // 3) * 0.30
                make_box(f"Minnow_{mi}", (mx, shelf_y, mz),
                         (0.10, 0.04, 0.04), fish_color)
        elif ti == 1:  # catfish on the bottom
            make_box("Catfish_Body", (tx, shelf_y, 1.00), (0.40, 0.16, 0.10), fish_color)
            make_box("Catfish_Tail", (tx + 0.20, shelf_y, 1.00), (0.10, 0.10, 0.10), fish_color)
            # Whisker barbels
            for wi, sgn in enumerate([-1, +1]):
                make_box(f"Catfish_Barbel_{wi}", (tx - 0.20, shelf_y + sgn*0.06, 1.00),
                         (0.10, 0.005, 0.005), fish_color)
        elif ti == 2:  # bullfrog atop a half-submerged log
            make_cyl("Frog_Log", (tx, shelf_y, 1.04), 0.18, 0.40,
                     (0.32, 0.22, 0.16, 1.0), axis='Y', segments=8)
            make_box("Frog_Body", (tx, shelf_y, 1.30), (0.30, 0.24, 0.16), fish_color)
            make_box("Frog_Belly", (tx, shelf_y - 0.05, 1.22), (0.26, 0.04, 0.08), COL_FROG_BELLY)
            # Eyes
            for sgn in (-1, +1):
                make_cyl(f"Frog_Eye_{sgn:+d}", (tx + sgn*0.08, shelf_y - 0.02, 1.42),
                         0.04, 0.04, COL_FROG_BELLY, segments=8)
        # Tank label plaque
        make_box(f"Tank_{ti}_Label", (tx, shelf_y - 0.32, 0.92),
                 (0.40, 0.005, 0.10), P.PAPER)


def build_retail_counter():
    cy = 2.20
    make_box("Counter_Top",  (0.0, cy, 0.96), (3.00, 0.60, 0.04), COL_COUNTER_TOP)
    make_box("Counter_Body", (0.0, cy, 0.48), (3.00, 0.60, 0.96), COL_COUNTER)
    # Register
    make_box("Register_Body", (-1.20, cy, 1.16), (0.40, 0.40, 0.30), (0.42, 0.30, 0.22, 1.0))
    # Tackle wall hook for prices
    make_box("PriceChalkboard", (0.0, cy, 1.50), (0.60, 0.005, 0.40), (0.18, 0.20, 0.18, 1.0))
    # Nightcrawler chest cooler
    nx, ny = +2.40, 2.20
    make_box("Nightcrawler_Cooler_Body", (nx, ny, 0.40), (0.80, 0.60, 0.80), COL_NIGHTCRAWLER_BOX)
    make_box("Nightcrawler_Cooler_Lid", (nx, ny, 0.84), (0.80, 0.60, 0.08), COL_COUNTER)
    # Sticker
    make_box("Cooler_Sticker", (nx, ny - 0.31, 0.50), (0.20, 0.005, 0.20), COL_LURE_R)


def build_pegboard_walls():
    # Tackle pegboards along the W and E walls
    for side, wx, sign in [("W", -ROOM_W/2.0 + 0.06, +1), ("E", +ROOM_W/2.0 - 0.06, -1)]:
        make_box(f"Pegboard_{side}", (wx, ROOM_D/2.0 + 1.5, 1.60),
                 (0.04, 3.00, 1.40), COL_PEGBOARD)
        for ti in range(15):
            tx = wx + sign * 0.04
            tz = 1.00 + (ti // 3) * 0.20
            ty = ROOM_D/2.0 + 0.40 + (ti % 3) * 0.80
            tc = [COL_LURE_R, COL_LURE_Y, COL_LURE_B][ti % 3]
            make_box(f"Lure_{side}_{ti}", (tx, ty, tz), (0.005, 0.06, 0.12), tc)
            # Hook below the lure
            make_cyl(f"Hook_{side}_{ti}", (tx, ty, tz - 0.10), 0.008, 0.06,
                     (0.62, 0.62, 0.58, 1.0), segments=6)


def build_screened_porch_and_door():
    # Door (S, between the two S wall segments)
    make_box("Door", (0.0, 0.04, 1.05), (1.00, 0.08, 2.10), COL_COUNTER)
    make_cyl("Door_Knob", (0.30, -0.02, 1.00), 0.04, 0.04, (0.62, 0.62, 0.58, 1.0), axis='Y')
    # Painted frog sign over the door
    make_box("Frog_Sign_BG", (0.0, 0.04, 2.40), (1.40, 0.04, 0.50), COL_FROG_SIGN)
    make_box("Frog_Sign_Belly", (0.0, 0.02, 2.40), (0.005, 1.10, 0.30), COL_FROG_BELLY)
    # Screened porch backdrop (visible through the doorway)
    make_box("Porch_Floor", (0.0, -1.60, 0.04), (4.00, 3.20, 0.08), COL_FLOOR_WOOD)
    # Porch posts
    for sgn_x in (-1, +1):
        for sgn_y in (-1, +1):
            make_box(f"Porch_Post_{sgn_x:+d}_{sgn_y:+d}",
                     (sgn_x*1.90, -1.60 + sgn_y*1.40, 1.30),
                     (0.10, 0.10, 2.60), COL_COUNTER)
    # Tin roof above the porch
    make_box("Porch_Roof", (0.0, -1.60, 3.10), (4.40, 3.40, 0.10), COL_TIN_ROOF)
    # Mesh-screen walls (W + S + E)
    for sx in [-1.95, +1.95]:
        make_box(f"PorchScreen_W_{sx:+.0f}", (sx, -1.60, 2.20),
                 (0.04, 3.20, 1.80), (0.42, 0.46, 0.38, 0.40))
    make_box("PorchScreen_S", (0.0, -3.18, 2.20), (4.00, 0.04, 1.80), (0.42, 0.46, 0.38, 0.40))


def build_ceiling_infra():
    for j, (xpos, ypos) in enumerate([(-1.0, 2.0), (+1.0, 2.0), (-1.0, 5.0), (+1.0, 5.0)]):
        make_fluorescent_tube_fixture(f"Fluor_{j}", (xpos, ypos, CEIL),
                                       length=1.20, width=0.30,
                                       palette={"diffuser": (1.0, 0.98, 0.92, 1.0)})
    make_bug_zapper("BugZap", (-ROOM_W/2.0 + 0.15, 1.20, 2.40))
    make_smoke_detector("Smoke", (0.0, 3.5, CEIL))
    make_sprinkler("Spr", (0.0, 4.5, CEIL))
    # Hanging "BAIT" banner
    make_hanging_banner("BaitBanner", (0.0, 3.50, CEIL), width=1.60, height=0.32,
                         bg_color=COL_LURE_R, text_color=P.PAPER)


def build_decor():
    make_wall_clock("Clock", (+ROOM_W/2.0-0.05, 4.5, 2.30), frozen_hour=4, frozen_min=15)
    make_calendar("Calendar", (-ROOM_W/2.0+0.05, 4.5, 2.20))
    make_faded_poster("FrogPoster", (-ROOM_W/2.0+0.05, 1.6, 1.50))


def build_world_dressing():
    """Scene-description specifics from setup_lease_ends_today.json:
      · Three aquarium tanks · minnows / catfish / Theroux the
        bullfrog · already built; augment with tank labels
        (handwritten name cards on each)
      · Lily's jar (the tadpole jar she's bringing) is NOT here
        yet at 6:48 AM · but the spot where she'll set it on
        the counter is marked with a folded "FOR LILY" cardstock
      · The till to count · register drawer on the counter, open,
        with neat bill stacks visible
      · Em's keys on a brass hook by the door · the keys Ezra
        will hand over at 8:00
      · The lease document on the counter · ready to be signed
        out · with a brass pen on top
      · A morning customer's coffee mug on the counter (a regular
        who'll be by at 7:42)
    """
    # Aquarium tanks approx along (0, +2.0) — three tanks side by side
    tanks_y = +2.0
    tank_top_z = 1.10
    # Tank labels on the front (handwritten name cards)
    for ti, (lx, label_chars) in enumerate([(-2.4, "MINNOWS"), (0.0, "CATFISH"), (+2.4, "THEROUX")]):
        # Cream label backing
        make_box("Tank_Label_%d_Backing" % ti,
                 (lx, tanks_y - 0.32, tank_top_z - 0.10),
                 (0.30, 0.005, 0.08),
                 (0.94, 0.90, 0.80, 1.0))
        # Dark text (a single name-line stroke)
        make_box("Tank_Label_%d_Text" % ti,
                 (lx, tanks_y - 0.321, tank_top_z - 0.10),
                 (0.20, 0.001, 0.022),
                 (0.18, 0.16, 0.10, 1.0))
        # Smaller "OWNER: EM" tag below
        make_box("Tank_Label_%d_OwnerTag" % ti,
                 (lx, tanks_y - 0.321, tank_top_z - 0.16),
                 (0.16, 0.001, 0.008),
                 (0.62, 0.50, 0.30, 1.0))

    # "FOR LILY" cardstock spot on the counter
    rc_x = 0.0
    rc_y = -1.0
    counter_z = 1.00
    make_box("ForLily_Cardstock",
             (rc_x - 0.40, rc_y + 0.20, counter_z + 0.012),
             (0.16, 0.20, 0.001),
             (0.94, 0.90, 0.80, 1.0))
    # Two dark text lines on the cardstock
    for li in range(2):
        make_box("ForLily_TextLine_%d" % li,
                 (rc_x - 0.40, rc_y + 0.20, counter_z + 0.013),
                 (0.10, 0.020 - li * 0.005, 0.0005),
                 (0.18, 0.16, 0.10, 1.0))

    # Open register drawer with bill stacks
    reg_x = rc_x + 0.50
    make_box("Register_Body",
             (reg_x, rc_y, counter_z + 0.16),
             (0.50, 0.40, 0.30),
             (0.42, 0.32, 0.20, 1.0))
    # Drawer pulled out (south side, lower)
    make_box("Register_Drawer_Open",
             (reg_x, rc_y - 0.30, counter_z + 0.06),
             (0.46, 0.30, 0.10),
             (0.32, 0.22, 0.14, 1.0))
    # 4 bill stacks visible in the drawer
    for bi in range(4):
        bx = reg_x - 0.16 + bi * 0.10
        make_box("Register_BillStack_%d" % bi,
                 (bx, rc_y - 0.30, counter_z + 0.105),
                 (0.08, 0.18, 0.024),
                 (0.42, 0.62, 0.42, 1.0) if bi % 2 == 0 else (0.62, 0.62, 0.50, 1.0))
    # Coin tray (right side of drawer, smaller)
    make_box("Register_CoinTray",
             (reg_x + 0.18, rc_y - 0.30, counter_z + 0.085),
             (0.12, 0.18, 0.014),
             (0.62, 0.62, 0.60, 1.0))

    # Em's keys on a brass hook by the door
    # Door approx at (+3.0, -2.5)
    door_x = +3.0
    door_y = -2.5
    # Brass hook
    make_cyl("EmKeys_Hook",
             (door_x - 0.04, door_y, 1.50),
             0.012, 0.05,
             (0.78, 0.62, 0.30, 1.0),
             segments=6, axis='X')
    # Key ring (brass loop)
    make_cyl("EmKeys_Ring",
             (door_x - 0.06, door_y, 1.42),
             0.030, 0.005,
             (0.78, 0.62, 0.30, 1.0),
             segments=10, axis='X')
    # Three keys hanging from the ring
    for ki, kx_off in enumerate([-0.020, 0.0, +0.020]):
        make_box("EmKeys_Key_%d" % ki,
                 (door_x - 0.06 + kx_off, door_y, 1.36),
                 (0.008, 0.025, 0.08),
                 (0.78, 0.62, 0.30, 1.0))

    # The lease document on the counter, ready to be signed out
    make_box("LeaseDoc_Paper",
             (rc_x - 0.10, rc_y + 0.04, counter_z + 0.012),
             (0.22, 0.32, 0.002),
             (0.94, 0.90, 0.80, 1.0))
    # Letterhead at top
    make_box("LeaseDoc_Letterhead",
             (rc_x - 0.10, rc_y + 0.16, counter_z + 0.013),
             (0.20, 0.06, 0.0005),
             (0.20, 0.16, 0.12, 1.0))
    # Signature line at the bottom (a darker line)
    make_box("LeaseDoc_SignatureLine",
             (rc_x - 0.10, rc_y - 0.10, counter_z + 0.013),
             (0.18, 0.005, 0.0005),
             (0.18, 0.16, 0.10, 1.0))
    # Brass pen lying on top
    make_cyl("LeaseDoc_BrassPen",
             (rc_x - 0.04, rc_y, counter_z + 0.018),
             0.005, 0.14,
             (0.78, 0.62, 0.30, 1.0),
             segments=6, axis='Y')

    # Morning-customer coffee mug on the counter (Ezra's, half drunk)
    mug_x = rc_x - 0.60
    mug_y = rc_y + 0.10
    make_cyl("EzraMug_Body",
             (mug_x, mug_y, counter_z + 0.06),
             0.040, 0.10,
             (0.92, 0.88, 0.80, 1.0),
             segments=10, axis='Z')
    # Coffee level (half-drunk)
    make_cyl("EzraMug_Liquid",
             (mug_x, mug_y, counter_z + 0.07),
             0.036, 0.020,
             (0.30, 0.18, 0.10, 1.0),
             segments=10, axis='Z')


def build_world_wave2_props():
    """Named props from setup_the_walk_through_with_the_new_tenants
    and setup_the_year_ago_first_open.

    walk_through (9:14 AM · Aurélie's black composition notebook +
    Ferdinand's 35mm Nikon + Em's till counting sheet on the
    counter).

    year_ago_first_open (5:48 AM · Em's nine-step yellow legal-pad
    opening sheet in the register drawer, the black safe in the
    back office behind a framed license, Régis's olive-green pickup
    at 7 AM outside the front door, the OPEN sign flipped on the
    interior door hook).
    """
    counter_z = 0.90

    # Aurélie's black composition notebook · open on the counter
    aur_x = +0.60
    aur_y = -0.20
    make_box("Aurelie_Notebook_Cover",
             (aur_x, aur_y, counter_z + 0.014),
             (0.16, 0.22, 0.014),
             (0.10, 0.08, 0.06, 1.0))
    make_box("Aurelie_Notebook_Page",
             (aur_x + 0.08, aur_y, counter_z + 0.022),
             (0.15, 0.21, 0.001),
             (0.94, 0.90, 0.80, 1.0))
    make_box("Aurelie_Notebook_Speckle",
             (aur_x - 0.04, aur_y, counter_z + 0.0145),
             (0.03, 0.20, 0.0005),
             (0.24, 0.20, 0.16, 1.0))
    for li in range(10):
        make_box("Aurelie_Notebook_Line_%d" % li,
                 (aur_x + 0.08, aur_y - 0.09 + li * 0.02, counter_z + 0.023),
                 (0.13, 0.008, 0.0005),
                 (0.28, 0.22, 0.18, 1.0))
    make_cyl("Aurelie_Pencil",
             (aur_x - 0.12, aur_y + 0.10, counter_z + 0.014),
             0.006, 0.16,
             (0.94, 0.86, 0.32, 1.0), segments=6, axis='Y')

    # Ferdinand's 35mm Nikon · body + lens + red badge + strap
    ferd_x = +1.00
    ferd_y = -0.20
    make_box("Ferdinand_Nikon_Body",
             (ferd_x, ferd_y, counter_z + 0.06),
             (0.14, 0.10, 0.10),
             (0.12, 0.12, 0.14, 1.0))
    make_cyl("Ferdinand_Nikon_Lens",
             (ferd_x, ferd_y - 0.08, counter_z + 0.06),
             0.045, 0.07,
             (0.14, 0.14, 0.16, 1.0), segments=10, axis='Y')
    make_box("Ferdinand_Nikon_Badge",
             (ferd_x + 0.04, ferd_y + 0.052, counter_z + 0.07),
             (0.05, 0.001, 0.010),
             (0.78, 0.16, 0.16, 1.0))
    make_box("Ferdinand_Nikon_Strap",
             (ferd_x + 0.20, ferd_y, counter_z + 0.010),
             (0.24, 0.020, 0.002),
             (0.14, 0.14, 0.16, 1.0))

    # Em's till counting sheet on the counter (~1978 carbon-back form)
    till_x = +0.20
    till_y = -0.40
    make_box("EmsTillSheet_Paper",
             (till_x, till_y, counter_z + 0.014),
             (0.20, 0.28, 0.001),
             (0.92, 0.88, 0.78, 1.0))
    for li in range(8):
        make_box("EmsTillSheet_Field_%d" % li,
                 (till_x, till_y + 0.10 - li * 0.028, counter_z + 0.015),
                 (0.18, 0.010, 0.0005),
                 (0.28, 0.22, 0.18, 1.0))
    make_box("EmsTillSheet_CarbonEdge",
             (till_x, till_y - 0.14, counter_z + 0.0155),
             (0.20, 0.01, 0.0005),
             (0.28, 0.34, 0.62, 1.0))

    # Em's nine-step opening sheet · yellow legal-pad, in the drawer
    open_x = -0.10
    open_y = -0.40
    make_box("EmsOpeningSheet_YellowPaper",
             (open_x, open_y, counter_z + 0.014),
             (0.14, 0.20, 0.001),
             (0.94, 0.88, 0.42, 1.0))
    for ri in range(9):
        make_box("EmsOpeningSheet_Rule_%d" % ri,
                 (open_x, open_y + 0.08 - ri * 0.020, counter_z + 0.0145),
                 (0.13, 0.001, 0.0005),
                 (0.42, 0.56, 0.78, 1.0))
    for si in range(9):
        make_box("EmsOpeningSheet_Step_%d" % si,
                 (open_x - 0.02, open_y + 0.075 - si * 0.020, counter_z + 0.0148),
                 (0.10, 0.008, 0.0005),
                 (0.22, 0.18, 0.14, 1.0))

    # The safe in the back office · behind the framed license
    safe_x = +2.00
    safe_y = +2.60
    make_box("BackOffice_Safe_Body",
             (safe_x, safe_y, 0.32),
             (0.44, 0.36, 0.60),
             (0.12, 0.12, 0.12, 1.0))
    make_cyl("BackOffice_Safe_Dial",
             (safe_x, safe_y - 0.19, 0.42),
             0.08, 0.02,
             (0.72, 0.72, 0.70, 1.0), segments=12, axis='Y')
    make_box("BackOffice_Safe_Brand",
             (safe_x, safe_y - 0.185, 0.58),
             (0.12, 0.001, 0.020),
             (0.86, 0.86, 0.84, 1.0))
    make_cyl("BackOffice_Safe_Handle",
             (safe_x + 0.06, safe_y - 0.19, 0.36),
             0.008, 0.10,
             (0.62, 0.62, 0.60, 1.0), segments=6, axis='X')
    make_box("BackOffice_License_Frame",
             (safe_x, safe_y - 0.15, 0.94),
             (0.30, 0.005, 0.22),
             (0.62, 0.46, 0.24, 1.0))
    make_box("BackOffice_License_Paper",
             (safe_x, safe_y - 0.152, 0.94),
             (0.24, 0.001, 0.18),
             (0.94, 0.92, 0.86, 1.0))

    # Régis's olive-green pickup · outside the front door
    truck_x = 0.0
    truck_y = -3.90
    truck_z = 0.60
    make_box("Regis_Pickup_Cab",
             (truck_x, truck_y, truck_z),
             (1.20, 0.90, 1.20),
             (0.34, 0.42, 0.24, 1.0))
    make_box("Regis_Pickup_Bed",
             (truck_x + 0.90, truck_y, truck_z - 0.10),
             (1.40, 0.90, 0.80),
             (0.34, 0.42, 0.24, 1.0))
    for wx in (-0.50, +1.20):
        for wy in (-0.55, +0.55):
            make_cyl("Regis_Pickup_Wheel_%d_%d" % (int(wx*100), int(wy*100)),
                     (truck_x + wx, truck_y + wy, 0.30),
                     0.28, 0.14,
                     (0.10, 0.08, 0.08, 1.0), segments=10, axis='Y')

    # OPEN sign on the interior door hook
    make_box("OpenSign_Backing",
             (-0.10, -2.20, 1.50),
             (0.24, 0.005, 0.10),
             (0.94, 0.94, 0.90, 1.0))
    make_box("OpenSign_Text",
             (-0.10, -2.202, 1.50),
             (0.18, 0.001, 0.06),
             (0.22, 0.62, 0.28, 1.0))


def build_bait_shop_gear():
    """PROPS-focus enrichment (2026-07-13): the bait-and-tackle gear
    the shop's identity calls for — a floor rod rack of rods, a live-
    bait aerator bucket, a minnow dip net, and a bobber display card."""
    # Floor rod rack of five fishing rods, SE corner near the door
    rack_x, rack_y = +2.55, 0.95
    make_box("RodRack_Base", (rack_x, rack_y, 0.06), (0.60, 0.34, 0.12), COL_COUNTER)
    make_box("RodRack_Back", (rack_x, rack_y + 0.14, 0.70), (0.60, 0.05, 1.20), COL_PEGBOARD)
    for ri in range(5):
        rx = rack_x - 0.24 + ri * 0.12
        make_cyl(f"Rod_{ri}_Blank", (rx, rack_y, 1.10), 0.010, 1.90,
                 (0.18, 0.16, 0.16, 1.0), segments=6)
        make_cyl(f"Rod_{ri}_Grip", (rx, rack_y, 0.26), 0.022, 0.28,
                 (0.72, 0.58, 0.36, 1.0), segments=6)
        make_cyl(f"Rod_{ri}_Reel", (rx + 0.05, rack_y, 0.46), 0.05, 0.05,
                 (0.42, 0.44, 0.46, 1.0), axis='X', segments=8)

    # Live-bait aerator bucket by the counter
    bx, by = +1.30, 1.30
    make_cyl("BaitBucket_Body", (bx, by, 0.18), 0.16, 0.36, (0.86, 0.86, 0.82, 1.0), segments=12)
    make_cyl("BaitBucket_Lid", (bx, by, 0.37), 0.16, 0.03, (0.72, 0.72, 0.68, 1.0), segments=12)
    make_box("BaitBucket_Pump", (bx, by, 0.44), (0.10, 0.08, 0.08), (0.30, 0.34, 0.30, 1.0))
    make_cyl("BaitBucket_AirLine", (bx - 0.04, by, 0.28), 0.006, 0.30,
             (0.42, 0.42, 0.44, 1.0), segments=4)

    # Minnow dip net leaning by the W tank end
    nx, ny = -2.55, 5.20
    make_cyl("DipNet_Handle", (nx, ny, 0.80), 0.014, 1.50, (0.72, 0.58, 0.36, 1.0), segments=6)
    make_cyl("DipNet_Hoop", (nx, ny, 1.58), 0.18, 0.03, (0.42, 0.44, 0.46, 1.0), segments=12)
    make_cyl("DipNet_Mesh", (nx, ny, 1.44), 0.16, 0.22, (0.40, 0.52, 0.34, 0.45), segments=12)

    # Bobber/float display card on the counter top
    cx, cy, cz = +0.90, 2.20, 1.00
    make_box("BobberCard_Back", (cx, cy, cz + 0.26), (0.30, 0.02, 0.34), (0.78, 0.62, 0.42, 1.0))
    for row in range(3):
        for col in range(4):
            ox = -0.10 + col * 0.07
            oz = 0.14 + row * 0.10
            make_cyl(f"Bobber_{row}_{col}_R", (cx + ox, cy - 0.02, cz + oz + 0.02),
                     0.024, 0.02, COL_LURE_R, axis='Y', segments=8)
            make_cyl(f"Bobber_{row}_{col}_W", (cx + ox, cy - 0.02, cz + oz - 0.01),
                     0.024, 0.02, (0.92, 0.92, 0.90, 1.0), axis='Y', segments=8)


def main():
    clear_scene()
    build_shell()
    build_aquarium_tanks()
    build_retail_counter()
    build_pegboard_walls()
    build_screened_porch_and_door()
    build_ceiling_infra()
    build_decor()
    build_bait_shop_gear()
    build_world_dressing()
    build_world_wave2_props()
    out = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                         "../../../assets/3d/locales/frog_knows_best.glb"))
    print(f"\n[build_frog_knows_best] exporting to {out}")
    export_glb(out)


if __name__ == "__main__":
    main()
