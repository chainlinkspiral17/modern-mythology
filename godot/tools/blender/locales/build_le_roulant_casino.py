"""X · WHEEL OF FORTUNE — Le Roulant Casino. Ex-bank floor: marble
columns, single roulette table at center, slot machine bank along
the W wall, cashier cage on the N wall behind brass bars. Heavy
brass + maroon palette. Cigar smoke fog appropriate at the level.
"""
import os, sys
_BT = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
if _BT not in sys.path: sys.path.insert(0, _BT)
import math
from _props import palette as P
from _props.geometry import clear_scene, make_box, make_cyl, export_glb
from _props.structure import make_floor, make_wall, make_ceiling, make_crown_molding
from _props.decor import make_wall_clock, make_floor_plant
from _props.safety import make_smoke_detector, make_sprinkler, make_security_camera

PAL = {"wall": (0.32, 0.18, 0.18, 1.0), "baseboard": (0.62, 0.46, 0.26, 1.0)}
COL_FLOOR_MARBLE = (0.78, 0.74, 0.66, 1.0); COL_FLOOR_SEAM = (0.42, 0.36, 0.30, 1.0)
COL_COLUMN = (0.86, 0.82, 0.74, 1.0); COL_BRASS = (0.74, 0.56, 0.28, 1.0)
COL_FELT = (0.16, 0.38, 0.24, 1.0); COL_WHEEL_RED = (0.74, 0.20, 0.18, 1.0)
COL_WHEEL_BLACK = (0.10, 0.08, 0.08, 1.0); COL_SLOT_BODY = (0.78, 0.74, 0.70, 1.0)
COL_SLOT_SCREEN = (0.20, 0.16, 0.30, 1.0); COL_CHIP_RED = (0.84, 0.20, 0.18, 1.0)
COL_CHIP_BLUE = (0.20, 0.34, 0.62, 1.0); COL_NEON = (0.96, 0.32, 0.42, 1.0)
COL_CARPET = (0.46, 0.16, 0.16, 1.0)

ROOM_W = 11.0; ROOM_D = 9.0; CEIL = 3.80


def build_shell():
    make_floor("Floor", (0.0, ROOM_D/2.0, 0.0), size_x=ROOM_W+0.4, size_y=ROOM_D+0.4,
               palette={"vinyl": COL_FLOOR_MARBLE, "seam": COL_FLOOR_SEAM})
    # Maroon runner carpet down the center
    make_box("Carpet", (0.0, ROOM_D/2.0, 0.02), (3.20, ROOM_D, 0.005), COL_CARPET)
    for nm, x, bb in [("Wall_W", -ROOM_W/2.0, +1), ("Wall_E", +ROOM_W/2.0, -1)]:
        make_wall(nm, (x, ROOM_D/2.0, 0), length=ROOM_D+0.4, height=CEIL, axis='Y',
                  palette=PAL, baseboard_face_sign=bb)
    make_wall("Wall_N", (0.0, ROOM_D, 0), length=ROOM_W+0.4, height=CEIL, axis='X',
              palette=PAL, baseboard_face_sign=-1)
    make_wall("Wall_S_W", (-3.0, 0.0, 0), length=5.0, height=CEIL, axis='X', palette=PAL)
    make_wall("Wall_S_E", (+3.0, 0.0, 0), length=5.0, height=CEIL, axis='X', palette=PAL)
    make_ceiling("Ceil", (0.0, ROOM_D/2.0, CEIL), size_x=ROOM_W+0.4, size_y=ROOM_D+0.4)
    for nm, ax, length, wx, wy in [("Crown_W",'Y',ROOM_D,-ROOM_W/2.0+0.10,ROOM_D/2.0),
                                    ("Crown_E",'Y',ROOM_D,+ROOM_W/2.0-0.10,ROOM_D/2.0),
                                    ("Crown_N",'X',ROOM_W,0.0,ROOM_D-0.10)]:
        make_crown_molding(nm, wall_x=wx, wall_y=wy, length=length, axis=ax,
                           ceil_z=CEIL, palette={"wood": COL_BRASS})


def build_marble_columns():
    # Four classical columns at corners of the playing floor.
    for ci, (cx, cy) in enumerate([(-3.0, 2.20), (+3.0, 2.20), (-3.0, 6.80), (+3.0, 6.80)]):
        make_cyl(f"Column_{ci}_Base", (cx, cy, 0.20), 0.40, 0.40, COL_COLUMN, segments=12)
        make_cyl(f"Column_{ci}_Shaft", (cx, cy, CEIL/2.0 + 0.20), 0.32, CEIL - 0.80,
                 COL_COLUMN, segments=12)
        make_cyl(f"Column_{ci}_Cap", (cx, cy, CEIL - 0.20), 0.40, 0.40, COL_COLUMN, segments=12)


def build_roulette_table():
    rx, ry = 0.0, 4.50
    # Table base — long oval (approximated as box + rounded ends)
    make_box("Roulette_Base", (rx, ry, 0.40), (2.40, 1.20, 0.80), COL_FELT)
    make_box("Roulette_Top",  (rx, ry, 0.84), (2.50, 1.30, 0.04), (0.32, 0.20, 0.16, 1.0))
    # Roulette wheel at the W end of the table
    wx, wy = rx - 0.85, ry
    make_cyl("Wheel_Outer", (wx, wy, 0.88), 0.46, 0.06, COL_BRASS, segments=24)
    make_cyl("Wheel_Inner", (wx, wy, 0.90), 0.36, 0.04, COL_WHEEL_BLACK, segments=24)
    # 12 pockets alternating red/black/green
    for i in range(12):
        ang = i * (2*math.pi/12)
        px = wx + math.cos(ang) * 0.40
        py = wy + math.sin(ang) * 0.40
        pc = COL_WHEEL_RED if i % 3 else COL_WHEEL_BLACK
        if i == 0: pc = (0.10, 0.42, 0.20, 1.0)
        make_box(f"Wheel_Pocket_{i}", (px, py, 0.92), (0.08, 0.04, 0.02), pc)
    make_cyl("Wheel_Hub", (wx, wy, 0.94), 0.08, 0.04, COL_BRASS, segments=10)
    # Betting felt grid (printed onto top, abstracted as colored squares)
    for col in range(12):
        for row in range(3):
            sx = rx + 0.00 + col * 0.12 - 0.40
            sy = ry - 0.20 + row * 0.20
            pc = COL_WHEEL_RED if (col + row) % 2 else COL_WHEEL_BLACK
            make_box(f"Felt_{col}_{row}", (sx, sy, 0.86), (0.10, 0.18, 0.005), pc)
    # Chip stacks
    for si, (sx, sy, sc) in enumerate([(rx+0.80, ry-0.40, COL_CHIP_RED),
                                        (rx+0.95, ry-0.40, COL_CHIP_BLUE),
                                        (rx+0.80, ry+0.40, COL_CHIP_BLUE),
                                        (rx+0.95, ry+0.40, COL_CHIP_RED)]):
        for li in range(6):
            make_cyl(f"Chip_{si}_{li}", (sx, sy, 0.88 + li*0.018), 0.06, 0.018, sc, segments=10)


def build_slot_bank():
    # Five slot machines along the W wall
    for si in range(5):
        sx = -ROOM_W/2.0 + 0.55
        sy = 1.50 + si * 1.20
        make_box(f"Slot_{si}_Pedestal", (sx, sy, 0.40), (0.60, 0.50, 0.80), COL_SLOT_BODY)
        make_box(f"Slot_{si}_Body", (sx, sy, 1.30, ), (0.60, 0.50, 1.00), COL_SLOT_BODY)
        make_box(f"Slot_{si}_Screen", (sx+0.26, sy, 1.30), (0.005, 0.40, 0.40), COL_SLOT_SCREEN)
        # Three reel windows
        for ri in range(3):
            make_box(f"Slot_{si}_Reel_{ri}", (sx+0.27, sy - 0.16 + ri*0.16, 1.30),
                     (0.005, 0.12, 0.20), (0.92, 0.92, 0.86, 1.0))
        # Crank handle
        make_box(f"Slot_{si}_Crank", (sx+0.30, sy+0.28, 1.00), (0.06, 0.06, 0.20), COL_BRASS)
        make_cyl(f"Slot_{si}_CrankBall", (sx+0.30, sy+0.28, 0.92), 0.05, 0.04, (0.74, 0.20, 0.18, 1.0))


def build_cashier_cage():
    # Cashier window on N wall (right of column) with brass bars
    cx, cy = +3.50, ROOM_D - 0.10
    make_box("Cage_Window_Frame", (cx, cy, 1.60), (1.80, 0.06, 1.20), COL_BRASS)
    make_box("Cage_Counter_Top",   (cx, cy - 0.30, 1.06), (1.80, 0.50, 0.04), COL_BRASS)
    # Vertical brass bars
    for bi in range(8):
        bx = cx - 0.78 + bi * 0.22
        make_cyl(f"Cage_Bar_{bi}", (bx, cy, 1.70), 0.012, 1.10, COL_BRASS, segments=8)
    # "CASHIER" plaque above
    make_box("Cage_Plaque", (cx, cy, 2.40), (0.80, 0.04, 0.20), COL_BRASS)


def build_neon_wheel_sign():
    # Hanging from ceiling, central focal piece
    sx, sy = 0.0, 3.00
    make_cyl("NeonSign_Ring", (sx, sy, CEIL - 0.30), 0.80, 0.04, COL_NEON, segments=20)
    # 8 spokes
    for i in range(8):
        ang = i * (math.pi/4)
        ex = sx + math.cos(ang) * 0.40
        ey = sy + math.sin(ang) * 0.40
        make_box(f"NeonSign_Spoke_{i}", (ex, ey, CEIL-0.30), (0.04, 0.04, 0.04), COL_NEON)
    make_cyl("NeonSign_Hub", (sx, sy, CEIL-0.30), 0.10, 0.04, COL_BRASS, segments=10)


def build_ceiling_infra():
    # Chandelier-style pendants over the table
    for px in [-1.0, +1.0]:
        make_cyl(f"Chandelier_Cord_{px:+.0f}", (px, 4.50, CEIL-0.60), 0.012, 1.20, P.METAL_BLACK)
        make_cyl(f"Chandelier_Bowl_{px:+.0f}", (px, 4.50, CEIL-1.16), 0.20, 0.10, COL_BRASS)
    make_smoke_detector("Smoke", (0.0, 5.0, CEIL))
    make_sprinkler("Spr_W", (-3.0, 4.5, CEIL))
    make_sprinkler("Spr_E", (+3.0, 4.5, CEIL))
    make_security_camera("Cam", (ROOM_W/2.0-0.10, 4.5, CEIL-0.10))


def build_decor():
    make_wall_clock("Clock", (ROOM_W/2.0-0.05, 7.0, 2.30), frozen_hour=4, frozen_min=15)
    make_floor_plant("Plant_SE", (ROOM_W/2.0-0.50, 0.50, 0.0), palette={"leaf": (0.42, 0.30, 0.20, 1.0)})
    make_floor_plant("Plant_SW", (-ROOM_W/2.0+0.50, 0.50, 0.0), palette={"leaf": (0.42, 0.30, 0.20, 1.0)})


def main():
    clear_scene()
    build_shell()
    build_marble_columns()
    build_roulette_table()
    build_slot_bank()
    build_cashier_cage()
    build_neon_wheel_sign()
    build_ceiling_infra()
    build_decor()
    out = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                         "../../../assets/3d/locales/le_roulant_casino.glb"))
    print(f"\n[build_le_roulant_casino] exporting to {out}")
    export_glb(out)


if __name__ == "__main__":
    main()
