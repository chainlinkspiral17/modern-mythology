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


def main():
    clear_scene()
    build_shell()
    build_aquarium_tanks()
    build_retail_counter()
    build_pegboard_walls()
    build_screened_porch_and_door()
    build_ceiling_infra()
    build_decor()
    out = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                         "../../../assets/3d/locales/frog_knows_best.glb"))
    print(f"\n[build_frog_knows_best] exporting to {out}")
    export_glb(out)


if __name__ == "__main__":
    main()
