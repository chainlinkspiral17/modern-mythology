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
    out = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                         "../../../assets/3d/locales/simon_apartment.glb"))
    print(f"\n[build_simon_apartment] exporting to {out}")
    export_glb(out)


if __name__ == "__main__":
    main()
