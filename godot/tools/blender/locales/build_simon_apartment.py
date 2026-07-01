"""XII · HANGED MAN — Simon's apartment. 3rd-floor walk-up in the
FQ row. Single open studio: bed in the NE corner, kitchenette
along the W wall, a battered armchair under the front (S) window
looking at the fire escape. The Hanged Man motif: things suspended
that should be on the ground — a chair tipped over, a single boot
hanging from a coat peg by its laces, an old TV showing snow on a
crate. Natalie's vol5/6 apartment, where Simon's not coming back.
"""
import os, sys
_BT = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
if _BT not in sys.path: sys.path.insert(0, _BT)
from _props import palette as P
from _props.geometry import clear_scene, make_box, make_cyl, export_glb
from _props.structure import make_floor, make_wall, make_ceiling, make_crown_molding
from _props.decor import make_wall_clock, make_floor_plant, make_faded_poster
from _props.safety import (make_smoke_detector, make_sprinkler,
                            make_fluorescent_tube_fixture)

PAL = {"wall": (0.78, 0.74, 0.66, 1.0), "baseboard": (0.32, 0.22, 0.16, 1.0)}
COL_FLOOR_HARDWOOD = (0.52, 0.36, 0.22, 1.0); COL_FLOOR_SEAM = (0.32, 0.22, 0.16, 1.0)
COL_BED_FRAME = (0.32, 0.22, 0.16, 1.0); COL_LINEN = (0.86, 0.82, 0.74, 1.0)
COL_ARMCHAIR = (0.42, 0.30, 0.22, 1.0); COL_KITCHEN_CAB = (0.62, 0.52, 0.42, 1.0)
COL_FRIDGE = (0.78, 0.78, 0.74, 1.0); COL_STOVE = (0.32, 0.32, 0.32, 1.0)
COL_TV_BODY = (0.18, 0.18, 0.20, 1.0); COL_TV_SCREEN_STATIC = (0.62, 0.62, 0.62, 1.0)
COL_CRATE = (0.42, 0.30, 0.22, 1.0); COL_BOOT = (0.32, 0.22, 0.16, 1.0)
COL_FIREESCAPE = (0.32, 0.32, 0.30, 1.0); COL_BRICK_OUTSIDE = (0.62, 0.34, 0.26, 1.0)
COL_WINDOW_GLASS = (0.74, 0.84, 0.86, 0.55); COL_SHIRT_PALE = (0.86, 0.80, 0.72, 1.0)
COL_BRASS = (0.74, 0.56, 0.28, 1.0)

ROOM_W = 5.0; ROOM_D = 7.0; CEIL = 2.80


def build_shell():
    make_floor("Floor", (0.0, ROOM_D/2.0, 0.0), size_x=ROOM_W+0.4, size_y=ROOM_D+0.4,
               palette={"vinyl": COL_FLOOR_HARDWOOD, "seam": COL_FLOOR_SEAM})
    for nm, x, bb in [("Wall_W", -ROOM_W/2.0, +1), ("Wall_E", +ROOM_W/2.0, -1)]:
        make_wall(nm, (x, ROOM_D/2.0, 0), length=ROOM_D+0.4, height=CEIL, axis='Y',
                  palette=PAL, baseboard_face_sign=bb)
    make_wall("Wall_N", (0.0, ROOM_D, 0), length=ROOM_W+0.4, height=CEIL, axis='X',
              palette=PAL, baseboard_face_sign=-1)
    # S wall: door + front window
    make_wall("Wall_S_W", (-1.80, 0.0, 0), length=1.60, height=CEIL, axis='X', palette=PAL)
    make_wall("Wall_S_E", (+1.80, 0.0, 0), length=1.60, height=CEIL, axis='X', palette=PAL)
    make_ceiling("Ceil", (0.0, ROOM_D/2.0, CEIL), size_x=ROOM_W+0.4, size_y=ROOM_D+0.4)
    for nm, ax, length, wx, wy in [("Crown_W",'Y',ROOM_D,-ROOM_W/2.0+0.10,ROOM_D/2.0),
                                    ("Crown_E",'Y',ROOM_D,+ROOM_W/2.0-0.10,ROOM_D/2.0),
                                    ("Crown_N",'X',ROOM_W,0.0,ROOM_D-0.10)]:
        make_crown_molding(nm, wall_x=wx, wall_y=wy, length=length, axis=ax,
                           ceil_z=CEIL, palette={"wood": (0.42, 0.32, 0.22, 1.0)})


def build_front_window_and_fire_escape():
    # Front window (S, between Wall_S_W and Wall_S_E)
    make_box("FrontWindow_Frame", (0.0, 0.04, 1.55), (1.60, 0.04, 1.20), (0.42, 0.32, 0.22, 1.0))
    make_box("FrontWindow_Glass", (0.0, 0.06, 1.55), (1.40, 0.005, 1.00), COL_WINDOW_GLASS)
    # Outside: fire-escape platform + railing visible just past the glass
    make_box("FireEscape_Platform", (0.0, -1.20, 1.10), (2.20, 1.20, 0.04), COL_FIREESCAPE)
    for ri in range(6):
        rx = -1.0 + ri * 0.40
        make_cyl(f"FireEscape_Baluster_{ri}", (rx, -1.80, 1.50), 0.018, 0.80,
                 COL_FIREESCAPE, segments=6)
    make_box("FireEscape_Rail", (0.0, -1.80, 1.90), (2.20, 0.04, 0.04), COL_FIREESCAPE)
    # Brick exterior backdrop
    make_box("Brick_Outside", (0.0, -3.50, 2.0), (16.0, 0.04, 8.0), COL_BRICK_OUTSIDE)


def build_bed():
    # Bed in NE corner, narrow single, sheets rumpled.
    bx, by = +1.40, ROOM_D - 1.30
    make_box("Bed_Frame", (bx, by, 0.20), (1.20, 2.00, 0.30), COL_BED_FRAME)
    make_box("Bed_Mattress", (bx, by, 0.42), (1.10, 1.90, 0.18), COL_LINEN)
    # Rumpled sheet — single thicker box pushed to one side
    make_box("Bed_Sheet", (bx-0.10, by+0.30, 0.58), (1.10, 1.20, 0.10), COL_LINEN)
    make_box("Bed_Pillow", (bx, by+0.86, 0.56), (1.00, 0.30, 0.08), P.PAPER)
    # Bedside crate (no nightstand — Simon never replaced the one
    # that broke). Doubles as the TV stand if rotated; here just a
    # crate-on-end with a lamp.
    cx, cy = +1.40, ROOM_D - 2.70
    make_box("Crate_Nightstand", (cx, cy, 0.30), (0.40, 0.40, 0.60), COL_CRATE)
    # Lamp
    make_cyl("Lamp_Base", (cx, cy, 0.66), 0.06, 0.04, (0.32, 0.32, 0.32, 1.0))
    make_cyl("Lamp_Stem", (cx, cy, 0.84), 0.014, 0.32, (0.32, 0.32, 0.32, 1.0))
    make_cyl("Lamp_Shade", (cx, cy, 1.04), 0.14, 0.16, (0.62, 0.58, 0.50, 1.0))


def build_kitchenette():
    # W wall, S-to-N: stove, counter, fridge
    # Stove (S end)
    sx, sy = -ROOM_W/2.0 + 0.40, 1.20
    make_box("Stove_Body", (sx, sy, 0.45), (0.60, 0.60, 0.90), COL_STOVE)
    make_box("Stove_Top",  (sx, sy, 0.92), (0.60, 0.60, 0.04), (0.18, 0.18, 0.18, 1.0))
    # 4 burners
    for bi, (sgn_x, sgn_y) in enumerate([(-1, -1), (+1, -1), (-1, +1), (+1, +1)]):
        make_cyl(f"Burner_{bi}", (sx + sgn_x*0.16, sy + sgn_y*0.16, 0.94),
                 0.10, 0.02, (0.16, 0.16, 0.16, 1.0), segments=10)
    # Counter (middle)
    cx_, cy_ = -ROOM_W/2.0 + 0.40, 2.40
    make_box("Counter_Top",  (cx_, cy_, 0.94), (0.60, 1.60, 0.04), (0.78, 0.78, 0.72, 1.0))
    make_box("Counter_Body", (cx_, cy_, 0.47), (0.60, 1.60, 0.94), COL_KITCHEN_CAB)
    # Sink
    make_box("Sink", (cx_, cy_-0.30, 0.92), (0.40, 0.40, 0.06), (0.62, 0.62, 0.58, 1.0))
    make_box("Sink_Faucet", (cx_, cy_-0.30, 1.10), (0.04, 0.04, 0.20), (0.62, 0.62, 0.58, 1.0))
    # Coffee maker + sugar jar on the counter
    make_box("CoffeeMaker", (cx_-0.10, cy_+0.30, 1.08), (0.20, 0.20, 0.28), (0.42, 0.30, 0.30, 1.0))
    make_cyl("SugarJar", (cx_+0.20, cy_+0.40, 1.04), 0.06, 0.16, (0.96, 0.86, 0.62, 1.0))
    # Fridge (N end)
    fx, fy = -ROOM_W/2.0 + 0.40, 4.20
    make_box("Fridge_Body", (fx, fy, 0.90), (0.60, 0.70, 1.80), COL_FRIDGE)
    make_box("Fridge_Handle", (fx+0.30, fy-0.30, 1.00), (0.04, 0.04, 0.40), (0.32, 0.32, 0.32, 1.0))


def build_armchair_and_tv():
    # Armchair S of bed, facing the TV-on-crate
    ax, ay = +0.50, 2.40
    make_box("Armchair_Seat", (ax, ay, 0.40), (0.80, 0.70, 0.12), COL_ARMCHAIR)
    make_box("Armchair_Back", (ax, ay+0.30, 0.80), (0.80, 0.16, 0.72), COL_ARMCHAIR)
    make_box("Armchair_Arm_W", (ax-0.46, ay, 0.50), (0.10, 0.70, 0.30), COL_ARMCHAIR)
    make_box("Armchair_Arm_E", (ax+0.46, ay, 0.50), (0.10, 0.70, 0.30), COL_ARMCHAIR)
    # TV on a crate at the W facing the armchair
    tx, ty = -0.50, 2.20
    make_box("TV_Crate", (tx, ty, 0.40), (0.60, 0.50, 0.80), COL_CRATE)
    make_box("TV_Body",  (tx, ty, 0.94), (0.60, 0.50, 0.50), COL_TV_BODY)
    make_box("TV_Screen", (tx+0.26, ty, 0.94), (0.005, 0.40, 0.36), COL_TV_SCREEN_STATIC)
    # Antenna
    for sgn in (-1, +1):
        make_box(f"TV_Antenna_{sgn:+d}", (tx, ty+sgn*0.10, 1.30), (0.008, 0.008, 0.40), P.METAL_BLACK)


def build_hanged_motifs():
    # Tipped-over chair near the kitchen
    tcx, tcy = -1.20, 3.20
    make_box("Tipped_Chair_Back", (tcx, tcy, 0.10), (0.40, 0.06, 0.80), (0.42, 0.30, 0.22, 1.0))
    make_box("Tipped_Chair_Seat", (tcx, tcy+0.30, 0.20), (0.40, 0.40, 0.04), (0.42, 0.30, 0.22, 1.0))
    for li, (sgn_x, sgn_y) in enumerate([(-1, +0), (+1, +0), (-1, +1), (+1, +1)]):
        make_box(f"Tipped_Chair_Leg_{li}", (tcx + sgn_x*0.16, tcy+0.10 + sgn_y*0.20, 0.22),
                 (0.04, 0.04, 0.40), (0.42, 0.30, 0.22, 1.0))
    # Single boot hanging from a coat peg by its laces (W wall)
    pegx, pegy = -ROOM_W/2.0 + 0.10, 5.50
    make_box("Peg_Board", (pegx, pegy, 1.80), (0.06, 0.40, 0.10), (0.32, 0.22, 0.16, 1.0))
    for pi in range(3):
        make_cyl(f"Peg_{pi}", (pegx + 0.04, pegy - 0.16 + pi*0.16, 1.80),
                 0.014, 0.10, COL_BRASS, axis='X', segments=6)
    # The boot dangles from middle peg
    make_box("Boot_Body", (pegx + 0.18, pegy, 1.42), (0.10, 0.16, 0.20), COL_BOOT)
    make_box("Boot_Toe",  (pegx + 0.28, pegy, 1.36), (0.14, 0.16, 0.08), COL_BOOT)
    make_box("Boot_Lace", (pegx + 0.10, pegy, 1.62), (0.005, 0.005, 0.32),
             (0.32, 0.32, 0.32, 1.0))
    # Pale shirt on a hanger nearby (also from another peg) — looks
    # like a body suspended at a glance
    make_box("Shirt_Hanger", (pegx + 0.20, pegy + 0.20, 1.74), (0.30, 0.04, 0.04), P.METAL_BLACK)
    make_box("Shirt_Body", (pegx + 0.30, pegy + 0.20, 1.30), (0.20, 0.34, 0.70), COL_SHIRT_PALE)


def build_ceiling_infra():
    # Single overhead bulb — bare wire
    make_cyl("CeilCord", (0.0, 3.50, CEIL-0.30), 0.006, 0.60, P.METAL_BLACK)
    make_cyl("CeilBulb", (0.0, 3.50, CEIL-0.66), 0.08, 0.10, (0.96, 0.86, 0.62, 1.0))
    # Fluorescent tube over the kitchen counter
    make_fluorescent_tube_fixture("Fluor_Kit", (-ROOM_W/2.0 + 0.60, 2.40, CEIL),
                                   length=1.00, width=0.30,
                                   palette={"diffuser": (0.96, 0.94, 0.86, 1.0)})
    make_smoke_detector("Smoke", (0.0, 3.5, CEIL))
    make_sprinkler("Spr", (-1.0, 3.5, CEIL))


def build_decor():
    make_wall_clock("Clock", (+ROOM_W/2.0-0.05, 4.0, 2.30), frozen_hour=4, frozen_min=15)
    make_floor_plant("Plant_NE", (+ROOM_W/2.0-0.40, 6.60, 0.0),
                     palette={"leaf": (0.40, 0.46, 0.30, 1.0)})
    # Faded poster — vol5 record cover or similar
    make_faded_poster("Poster", (+ROOM_W/2.0-0.05, 2.0, 1.50))


def build_hanged_man_dressing():
    """Scene-description specifics from setup_after_simon.json:
      · "The armchair has the shape of you" · a darker wear-patch
        on the seat cushion + a slightly-deformed back cushion
      · "The chair on the kitchen floor has been tipped over since
        the night he didn't come back" · a tipped-over kitchen
        chair (rotated 90° on its back)
      · "Simon's boot — the one he wore — has been hanging from
        the coat peg by its laces" · a single boot hanging by
        a laced loop from a coat peg
      · "The TV is at static" · static-grey rectangle on the TV
        screen + a few darker noise-streaks
      · "The remote does not have batteries" · the remote on the
        coffee table with its back panel slid off + the empty
        battery compartment showing
    """
    # ── Wear pattern on the armchair (already built by
    # build_armchair_and_tv). Approximate armchair at (-1.0, +2.0).
    chair_cx = -1.0
    chair_cy = +2.0
    seat_z = 0.46
    # Darker wear patch on the seat cushion
    make_box("Armchair_WearPatch",
             (chair_cx, chair_cy, seat_z + 0.055),
             (0.36, 0.34, 0.005),
             (0.32, 0.20, 0.12, 1.0))   # darker velour
    # Wear-line trough across the back-cushion bottom
    make_box("Armchair_BackWearLine",
             (chair_cx, chair_cy + 0.22, 0.78),
             (0.40, 0.005, 0.04),
             (0.30, 0.20, 0.12, 1.0))

    # ── Tipped chair on the kitchen floor ──
    # Kitchenette approx at (+1.5, +2.5)
    tc_x = +1.20
    tc_y = +2.20
    # Chair seat (now horizontal on the floor — z ≈ 0.04, lying flat)
    make_box("TippedChair_Seat",
             (tc_x, tc_y, 0.06),
             (0.42, 0.42, 0.04),
             (0.32, 0.22, 0.14, 1.0))
    # Chair back (now horizontal too — lying flat behind the seat)
    make_box("TippedChair_Back",
             (tc_x - 0.40, tc_y, 0.10),
             (0.04, 0.42, 0.50),
             (0.32, 0.22, 0.14, 1.0))
    # 4 legs sticking up at the corners of the seat
    for sx in (-1, +1):
        for sy in (-1, +1):
            make_box("TippedChair_Leg_%+d_%+d" % (sx, sy),
                     (tc_x + sx * 0.18, tc_y + sy * 0.18, 0.27),
                     (0.04, 0.04, 0.46),
                     (0.32, 0.22, 0.14, 1.0))

    # ── Simon's boot hanging from the coat peg by its laces ──
    # Coat peg on the wall near the front door (south wall)
    peg_x = +1.50
    peg_y = -0.05   # south wall interior face
    peg_z = 1.80
    # Coat peg itself (small brass hook)
    make_box("CoatPeg_Mount",
             (peg_x, peg_y, peg_z),
             (0.08, 0.04, 0.04),
             (0.32, 0.22, 0.14, 1.0))
    make_cyl("CoatPeg_Hook",
             (peg_x, peg_y - 0.04, peg_z),
             0.012, 0.06,
             (0.78, 0.62, 0.30, 1.0),
             segments=6, axis='Y')
    # The boot hanging below the peg
    boot_z = peg_z - 0.24
    # Boot upper (the calf/shaft)
    make_box("SimonBoot_Shaft",
             (peg_x, peg_y - 0.08, boot_z - 0.12),
             (0.12, 0.14, 0.18),
             (0.18, 0.12, 0.08, 1.0))   # dark worn leather
    # Boot foot (the actual foot, angled forward — pointing south)
    make_box("SimonBoot_Foot",
             (peg_x, peg_y - 0.16, boot_z - 0.24),
             (0.12, 0.22, 0.08),
             (0.18, 0.12, 0.08, 1.0))
    # Sole (slightly lighter, lower)
    make_box("SimonBoot_Sole",
             (peg_x, peg_y - 0.16, boot_z - 0.29),
             (0.12, 0.22, 0.02),
             (0.32, 0.22, 0.14, 1.0))
    # Laces hanging from the boot up to the peg (a thin line)
    make_box("SimonBoot_LaceLoop",
             (peg_x, peg_y - 0.04, boot_z + 0.06),
             (0.006, 0.06, 0.14),
             (0.62, 0.50, 0.32, 1.0))

    # ── TV at static + the remote with no batteries ──
    # TV approx at (-1.0, -0.5, 0.6) per build_armchair_and_tv
    tv_x = -1.0
    tv_y = +0.30
    tv_screen_z = 1.20
    # Static-grey screen overlay
    make_box("TV_StaticScreen",
             (tv_x, tv_y - 0.21, tv_screen_z),
             (0.66, 0.005, 0.40),
             (0.62, 0.62, 0.60, 1.0))
    # 6 thin noise streaks across the screen (horizontal scan lines)
    for ni in range(6):
        nz = tv_screen_z - 0.15 + ni * 0.06
        make_box("TV_NoiseLine_%d" % ni,
                 (tv_x, tv_y - 0.211, nz),
                 (0.62, 0.001, 0.006),
                 (0.86, 0.86, 0.86, 1.0))
    # Remote on the coffee table — flipped over with battery compartment open
    # Coffee table approx at (-0.5, +1.5, 0.42)
    remote_x = -0.30
    remote_y = +1.50
    remote_top_z = 0.46
    # Remote body
    make_box("Remote_Body",
             (remote_x, remote_y, remote_top_z + 0.014),
             (0.08, 0.22, 0.028),
             (0.18, 0.16, 0.14, 1.0))
    # Open battery cover (the back panel, slid off to one side)
    make_box("Remote_BatteryCover",
             (remote_x + 0.08, remote_y - 0.04, remote_top_z + 0.010),
             (0.06, 0.10, 0.014),
             (0.20, 0.16, 0.14, 1.0))
    # Empty battery compartment (a darker recess where the cover was)
    make_box("Remote_BatteryCompartment",
             (remote_x, remote_y - 0.05, remote_top_z + 0.030),
             (0.04, 0.08, 0.014),
             (0.08, 0.06, 0.04, 1.0))


def build_hanged_man_wave2_props():
    """Named props from setup_the_first_night.json and
    setup_the_seventh_evening.json.

    the_first_night (11:14 AM Sunday · seven hours after the call):
      · Simon's right boot on the kitchen floor near the tipped
        chair (untied, wear-pattern showing his gait)
      · Simon's left boot by the front door (canonical
        opposite-direction placement)
      · The kitchen chair on its side (the moment · not yet the
        artifact)
      · The kitchenette light on (the only interior light)
      · The kitchen phone with the receiver hanging by its cord
        (from Simon's mother's earlier call)

    the_seventh_evening (7:14 PM · one week + one day later ·
    ten days on the lease):
      · Six empty banker's boxes stacked by the front door
        ($3.99 each from the Metairie office supply)
      · A blue sharpie on the front-door bench (for labeling)
      · The chair now with a small yellow sticky-note taped to
        it (the choice-made-by-choice marker)
      · Landlord's non-renewal form on the kitchen counter (3
        signature lines · two signed)
    """
    # ── the_first_night ────────────────────────────────────────

    # Simon's right boot on the kitchen floor (near tipped chair
    # which is at approximately (+1.20, +1.00) if kitchen is E)
    boot_x = +1.20
    boot_y = +0.60
    make_box("Simon_RightBoot_Sole",
             (boot_x, boot_y, 0.03),
             (0.12, 0.28, 0.02),
             (0.32, 0.20, 0.14, 1.0))    # dark leather
    make_box("Simon_RightBoot_Upper",
             (boot_x, boot_y - 0.06, 0.10),
             (0.12, 0.16, 0.14),
             (0.42, 0.28, 0.18, 1.0))
    # Untied lace splayed
    make_cyl("Simon_RightBoot_Lace_L",
             (boot_x - 0.03, boot_y - 0.04, 0.16),
             0.003, 0.10,
             (0.22, 0.16, 0.10, 1.0), segments=4, axis='X')
    make_cyl("Simon_RightBoot_Lace_R",
             (boot_x + 0.03, boot_y - 0.02, 0.14),
             0.003, 0.08,
             (0.22, 0.16, 0.10, 1.0), segments=4, axis='Y')
    # Wear pattern on outside sole (a darker triangular stripe)
    make_box("Simon_RightBoot_WearPattern",
             (boot_x + 0.05, boot_y, 0.021),
             (0.02, 0.24, 0.001),
             (0.20, 0.14, 0.10, 1.0))

    # Simon's left boot by the front door (front door at approx
    # (0, -1.80) · left boot POINTED opposite the right boot)
    lb_x = -0.30
    lb_y = -1.60
    make_box("Simon_LeftBoot_Sole",
             (lb_x, lb_y, 0.03),
             (0.12, 0.28, 0.02),
             (0.32, 0.20, 0.14, 1.0))
    make_box("Simon_LeftBoot_Upper",
             (lb_x, lb_y + 0.06, 0.10),
             (0.12, 0.16, 0.14),
             (0.42, 0.28, 0.18, 1.0))
    # Wear pattern on outside sole (mirror of right)
    make_box("Simon_LeftBoot_WearPattern",
             (lb_x - 0.05, lb_y, 0.021),
             (0.02, 0.24, 0.001),
             (0.20, 0.14, 0.10, 1.0))

    # The kitchen chair on its side · at (+1.20, +1.00)
    ch_x = +1.20
    ch_y = +1.00
    # Seat (laid horizontal on its side)
    make_box("Simon_TippedChair_Seat",
             (ch_x, ch_y, 0.14),
             (0.34, 0.34, 0.06),
             (0.42, 0.30, 0.22, 1.0))
    # Back (also on its side · perpendicular to the seat)
    make_box("Simon_TippedChair_Back",
             (ch_x + 0.18, ch_y, 0.14),
             (0.04, 0.34, 0.42),
             (0.42, 0.30, 0.22, 1.0))
    # Four legs (now pointing horizontally rather than down)
    for (dx, dy) in [(-0.12, -0.14), (-0.12, +0.14),
                      (-0.28, -0.14), (-0.28, +0.14)]:
        make_cyl("Simon_TippedChair_Leg_%d_%d" % (int(dx*100), int(dy*100)),
                 (ch_x + dx, ch_y + dy, 0.14),
                 0.014, 0.28,
                 (0.32, 0.24, 0.18, 1.0), segments=4, axis='X')

    # Kitchenette light on (a pale glow disc under the ceiling)
    kit_light_x = +1.50
    kit_light_y = -0.20
    make_cyl("SimonKitchenette_LightGlow",
             (kit_light_x, kit_light_y, 2.60),
             0.20, 0.005,
             (0.94, 0.86, 0.62, 0.85), segments=12, axis='Z')
    # Pull cord hanging
    make_cyl("SimonKitchenette_PullCord",
             (kit_light_x - 0.14, kit_light_y, 2.20),
             0.003, 0.60,
             (0.42, 0.34, 0.24, 1.0), segments=4, axis='Z')

    # The kitchen phone with receiver hanging by cord
    # Kitchen wall phone approx at (+2.20, +0.20)
    ph_x = +2.20
    ph_y = +0.20
    make_box("SimonKitchenPhone_Base",
             (ph_x, ph_y, 1.40),
             (0.16, 0.05, 0.24),
             (0.72, 0.60, 0.42, 1.0))    # bakelite tan
    # Receiver hanging (skewed off the base)
    make_box("SimonKitchenPhone_Receiver",
             (ph_x - 0.10, ph_y + 0.02, 0.90),
             (0.18, 0.04, 0.05),
             (0.72, 0.60, 0.42, 1.0))
    # Coiled cord (a stubby spiral · here a chain of segments)
    for ci in range(4):
        make_cyl("SimonKitchenPhone_Cord_%d" % ci,
                 (ph_x - 0.06 + ci * -0.014, ph_y + 0.03, 1.24 - ci * 0.09),
                 0.008, 0.10,
                 (0.42, 0.32, 0.20, 1.0), segments=4, axis='Z')

    # ── the_seventh_evening ────────────────────────────────────

    # Six empty banker's boxes stacked by the front door
    bx_x = -0.60
    bx_y = -1.20
    for bi in range(6):
        # First three stack up, next three at ground level next to
        # the first stack for a staggered "moving day" look
        col = bi // 3
        row = bi % 3
        make_box("BankersBox_%d_%d" % (col, row),
                 (bx_x + col * 0.36, bx_y, 0.14 + row * 0.28),
                 (0.32, 0.30, 0.26),
                 (0.76, 0.64, 0.42, 1.0))
        # Reinforced lid strip
        make_box("BankersBox_Lid_%d_%d" % (col, row),
                 (bx_x + col * 0.36, bx_y, 0.26 + row * 0.28),
                 (0.32, 0.30, 0.02),
                 (0.62, 0.50, 0.32, 1.0))

    # Blue sharpie on the front-door bench (or floor beside boxes)
    make_cyl("BlueSharpie_Body",
             (bx_x + 0.20, bx_y + 0.20, 0.10),
             0.010, 0.14,
             (0.24, 0.34, 0.68, 1.0), segments=6, axis='Y')
    # Cap (darker)
    make_cyl("BlueSharpie_Cap",
             (bx_x + 0.20 + 0.09, bx_y + 0.20, 0.10),
             0.011, 0.04,
             (0.14, 0.20, 0.44, 1.0), segments=6, axis='Y')

    # Small yellow sticky-note on the tipped chair (choice-marker)
    # (Present in seventh-evening state alongside first-night state ·
    # this is a placeholder for the sanctioned-tipped-forever option)
    make_box("SeventhEvening_ChairStickyNote",
             (ch_x - 0.06, ch_y + 0.10, 0.16),
             (0.05, 0.05, 0.0005),
             (0.94, 0.88, 0.42, 1.0))
    # Small handwriting block on the note
    make_box("SeventhEvening_ChairStickyNote_Text",
             (ch_x - 0.06, ch_y + 0.10, 0.161),
             (0.04, 0.001, 0.001),
             (0.20, 0.16, 0.12, 1.0))

    # Landlord's non-renewal form on the kitchen counter
    # (kitchen counter at approx +2.00, +0.60 · z ~0.90)
    nrf_x = +2.00
    nrf_y = +0.60
    counter_z = 0.90
    make_box("NonRenewalForm_Paper",
             (nrf_x, nrf_y, counter_z + 0.010),
             (0.22, 0.30, 0.001),
             (0.94, 0.90, 0.80, 1.0))
    # Three signature lines
    for li in range(3):
        make_box("NonRenewalForm_SigLine_%d" % li,
                 (nrf_x, nrf_y - 0.08 - li * 0.04, counter_z + 0.014),
                 (0.16, 0.001, 0.0005),
                 (0.20, 0.16, 0.12, 1.0))
    # First two signatures done (Marcelle + Prevost)
    for si in range(2):
        make_box("NonRenewalForm_Sig_%d" % si,
                 (nrf_x - 0.02, nrf_y - 0.08 - si * 0.04, counter_z + 0.015),
                 (0.06, 0.006, 0.0005),
                 (0.14, 0.16, 0.44, 1.0))


def main():
    clear_scene()
    build_shell()
    build_front_window_and_fire_escape()
    build_bed()
    build_kitchenette()
    build_armchair_and_tv()
    build_hanged_motifs()
    build_ceiling_infra()
    build_decor()
    build_hanged_man_dressing()
    build_hanged_man_wave2_props()
    out = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                         "../../../assets/3d/locales/simon_apartment.glb"))
    print(f"\n[build_simon_apartment] exporting to {out}")
    export_glb(out)


if __name__ == "__main__":
    main()
