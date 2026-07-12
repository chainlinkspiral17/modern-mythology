"""cabin_interior — vol5-7 locale (auto-generated placement script)."""
import os, sys
_BT = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
if _BT not in sys.path: sys.path.insert(0, _BT)
from _props import palette as P
from _props.geometry import clear_scene, make_box, make_cyl, export_glb
from _props.structure import make_floor, make_wall, make_ceiling, make_crown_molding, make_window
from _props.store_fixtures import make_counter, make_counter_bullnose, make_register
from _props.shelving import make_snack_aisle, make_endcap
from _props.food_service import make_coffee_pots
from _props.decor import make_wall_clock, make_floor_plant, make_faded_poster, make_calendar
from _props.safety import make_smoke_detector, make_hvac_vent, make_fluorescent_tube_fixture

ROOM_W = 6.0; ROOM_D = 6.0; CEIL = 2.8
PAL_WALL = {"wall":(0.62,0.46,0.32,1.0),"baseboard":(0.32,0.22,0.14,1.0)}
COL_FLOOR = (0.42,0.30,0.20,1.0); COL_SEAM = (0.22,0.14,0.10,1.0); COL_WOOD = (0.42,0.30,0.18,1.0)
COL_ACCENT = (0.96,0.62,0.32,1.0)

def build_shell():
    make_floor("Floor", (0.0, ROOM_D/2.0, 0.0), size_x=ROOM_W+0.4, size_y=ROOM_D+0.4,
               palette={"vinyl": COL_FLOOR, "seam": COL_SEAM})
    for nm, x, bb in [("Wall_W", -ROOM_W/2.0, +1), ("Wall_E", +ROOM_W/2.0, -1)]:
        make_wall(nm, (x, ROOM_D/2.0, 0), length=ROOM_D+0.4, height=CEIL, axis='Y', palette=PAL_WALL, baseboard_face_sign=bb)
    make_wall("Wall_N", (0.0, ROOM_D, 0), length=ROOM_W+0.4, height=CEIL, axis='X', palette=PAL_WALL, baseboard_face_sign=-1)
    make_wall("Wall_S_W", (-(ROOM_W/4.0+0.5), 0.0, 0), length=ROOM_W/2.0-1.0, height=CEIL, axis='X', palette=PAL_WALL)
    make_wall("Wall_S_E", (+(ROOM_W/4.0+0.5), 0.0, 0), length=ROOM_W/2.0-1.0, height=CEIL, axis='X', palette=PAL_WALL)
    make_box("Wall_S_AboveDoor", (0.0, 0.0, CEIL-0.30), (2.0, 0.20, 0.60), PAL_WALL["wall"])
    make_ceiling("Ceil", (0.0, ROOM_D/2.0, CEIL), size_x=ROOM_W+0.4, size_y=ROOM_D+0.4)

def build_counter():
    top_z = make_counter("Counter", (-ROOM_W/4.0, ROOM_D-1.0, 0.0), length=2.40, depth=0.70, height=0.92,
                         palette={"formica": (0.78, 0.66, 0.42, 1.0), "top": (0.32, 0.22, 0.14, 1.0), "kick": (0.32, 0.22, 0.14, 1.0)})
    make_counter_bullnose("Counter", (-ROOM_W/4.0-0.35, ROOM_D-1.0, top_z), length=2.40)

def build_table():
    tx, ty = 0.0, ROOM_D/2.0
    make_cyl("Table_Top", (tx, ty, 0.74), 0.55, 0.04, COL_WOOD)
    make_cyl("Table_Pedestal", (tx, ty, 0.37), 0.06, 0.70, COL_WOOD)
    for ci in range(4):
        import math
        ang = ci * 1.57
        cx, cy = tx + math.cos(ang)*1.10, ty + math.sin(ang)*1.10
        make_box(f"Chair_{ci}_Seat", (cx, cy, 0.44), (0.42, 0.42, 0.04), COL_WOOD)

def build_chairs():
    for ci, cx in enumerate([-1.5, +1.5]):
        cy = ROOM_D/2.0
        make_box(f"Rocker_{ci}_Seat", (cx, cy, 0.46), (0.50, 0.46, 0.04), COL_WOOD)

def build_ceiling_infra():
    for j in range(2):
        ypos = ROOM_D * (0.30 + j * 0.40)
        make_fluorescent_tube_fixture(f"Fluor_{j}", (0.0, ypos, CEIL), length=1.40, width=0.34)
    make_smoke_detector("Smoke", (0.0, ROOM_D/2.0, CEIL))



def build_cabin_detail():
    """Scene-standard deep pass (2026-07-12). The vol7 cabin (27
    instances) was walls + table + chairs + a bare counter. Adds the
    rustic warmth the room needs: a cast-iron potbelly wood stove
    with stovepipe + ember glow, a split-firewood stack, a braided
    oval rug under the table, a hurricane lantern on the table, a
    hanging pot rack + percolator on the kitchenette counter, a
    curtained window on the east wall, a wool blanket over a rocker,
    and a shelf of mason jars. make_box/make_cyl only. Room x -3..3,
    y 0..6.4; counter at west wall x -1.9, y 3.8-6.2; table at
    (0,3); door south y0."""
    import math as _m
    iron = (0.14, 0.14, 0.16, 1.0)
    iron_wm = (0.20, 0.19, 0.20, 1.0)
    wood = (0.44, 0.32, 0.20, 1.0)
    wood_dk = (0.34, 0.24, 0.15, 1.0)
    # ── Potbelly wood stove in the NE corner (x 2.3, y 5.4) ──
    sx, sy = 2.3, 5.4
    make_cyl("Stove_Belly", (sx, sy, 0.55), 0.35, 0.7, iron, segments=12)
    make_cyl("Stove_Waist", (sx, sy, 0.95), 0.28, 0.16, iron_wm, segments=12)
    make_cyl("Stove_Top", (sx, sy, 1.08), 0.32, 0.08, iron, segments=12)
    make_box("Stove_Door", (sx - 0.34, sy, 0.5), (0.04, 0.26, 0.30), iron_wm)
    make_box("Stove_EmberGlow", (sx - 0.355, sy, 0.5), (0.02, 0.16, 0.18), (0.95, 0.45, 0.15, 1.0))
    make_box("Stove_Legs_hint", (sx, sy, 0.12), (0.5, 0.5, 0.12), iron)
    # Stovepipe up to the ceiling with an elbow
    make_cyl("Stove_Pipe", (sx, sy, 1.8), 0.09, 1.4, iron_wm, segments=8)
    make_cyl("Stove_Pipe_Elbow", (sx, sy + 0.2, 2.5), 0.09, 0.5, iron_wm, segments=8, axis='Y')
    # Coffee pot on the stovetop
    make_cyl("Stove_CoffeePot", (sx, sy, 1.19), 0.09, 0.14, (0.20, 0.24, 0.30, 1.0), segments=8)
    make_box("Stove_CoffeePot_Spout", (sx - 0.11, sy, 1.20), (0.06, 0.03, 0.03), iron)
    # ── Split-firewood stack beside the stove ──
    for r in range(3):
        for c in range(4):
            fy = 4.5 + c * 0.16
            fz = 0.12 + r * 0.16 + (0.0 if c % 2 == 0 else 0.02)
            make_cyl(f"Firewood_{r}_{c}", (2.7, fy, fz), 0.075, 0.5,
                     wood if (r + c) % 2 else wood_dk, segments=6, axis='X')
    # ── Braided oval rug under the table (concentric discs) ──
    for i, (rr, col) in enumerate([(1.5, (0.46, 0.30, 0.24, 1.0)),
                                   (1.1, (0.54, 0.40, 0.28, 1.0)),
                                   (0.7, (0.40, 0.28, 0.22, 1.0))]):
        make_cyl(f"Rug_Ring_{i}", (0.0, 3.0, 0.008 + i * 0.002), rr, 0.006,
                 col, segments=16)
    # ── Hurricane lantern on the table ──
    make_cyl("Lantern_Base", (0.35, 2.7, 0.83), 0.05, 0.05, iron, segments=8)
    make_cyl("Lantern_Glass", (0.35, 2.7, 0.93), 0.04, 0.13, (0.96, 0.86, 0.55, 0.8), segments=8)
    make_cyl("Lantern_Flame", (0.35, 2.7, 0.96), 0.012, 0.05, (1.0, 0.7, 0.2, 1.0), segments=5)
    make_cyl("Lantern_Cap", (0.35, 2.7, 1.02), 0.045, 0.04, iron, segments=8)
    make_box("Lantern_Bail", (0.35, 2.7, 1.10), (0.002, 0.09, 0.06), iron)
    # ── Hanging pot rack over the kitchenette counter (west, x-1.6) ──
    make_box("PotRack_Bar", (-1.5, 5.0, 2.0), (0.04, 1.4, 0.04), iron)
    for i, (py, r, h, col) in enumerate([(4.6, 0.11, 0.14, iron), (5.0, 0.13, 0.16, (0.55,0.35,0.18,1)),
                                         (5.4, 0.10, 0.12, iron)]):
        make_cyl(f"PotRack_Hook_{i}", (-1.5, py, 1.9), 0.006, 0.16, iron_wm, segments=4)
        make_cyl(f"PotRack_Pot_{i}", (-1.5, py, 1.72), r, h, col, segments=10)
    # ── Percolator + mason jars on the counter top (z 1.0) ──
    make_cyl("Counter_Percolator", (-1.55, 4.2, 1.13), 0.08, 0.24, (0.60, 0.62, 0.64, 1.0), segments=10)
    make_cyl("Counter_Percolator_Knob", (-1.55, 4.2, 1.27), 0.02, 0.03, iron, segments=6)
    for i in range(4):
        make_cyl(f"Counter_Jar_{i}", (-1.55, 5.4 + i * 0.22, 1.11), 0.055, 0.22,
                 (0.80, 0.82, 0.72, 0.85), segments=8)
        make_cyl(f"Counter_Jar_{i}_Lid", (-1.55, 5.4 + i * 0.22, 1.23), 0.056, 0.03, iron, segments=8)
    # ── Curtained window on the EAST wall (x 3) ──
    make_box("Window_E_Frame", (2.96, 2.5, 1.6), (0.04, 1.4, 1.1), wood_dk)
    make_box("Window_E_Glass", (2.98, 2.5, 1.6), (0.02, 1.24, 0.94), (0.42, 0.52, 0.55, 0.6))
    make_box("Window_E_MullV", (2.97, 2.5, 1.6), (0.02, 0.05, 0.94), wood_dk)
    make_box("Window_E_MullH", (2.97, 2.5, 1.6), (0.02, 1.24, 0.05), wood_dk)
    for sgn in (-1, +1):
        make_box("Window_E_Curtain_%+d" % sgn, (2.9, 2.5 + sgn * 0.55, 1.6),
                 (0.05, 0.34, 1.14), (0.60, 0.28, 0.24, 1.0))
    # ── Wool blanket draped over Rocker_1 (at 1.5, 3.0) ──
    make_box("Rocker1_Blanket_Seat", (1.5, 3.0, 0.53), (0.5, 0.44, 0.04), (0.42, 0.46, 0.55, 1.0))
    make_box("Rocker1_Blanket_Drape", (1.5, 3.28, 0.35), (0.46, 0.04, 0.34), (0.38, 0.42, 0.50, 1.0))
    # ── Framed small landscape + antler mount on north wall ──
    make_box("NorthWall_Frame", (-0.6, 6.28, 1.9), (0.5, 0.03, 0.4), wood_dk)
    make_box("NorthWall_Frame_Art", (-0.6, 6.27, 1.9), (0.42, 0.02, 0.32), (0.46, 0.52, 0.44, 1.0))
    for sgn in (-1, +1):
        make_cyl("Antler_%+d" % sgn, (0.8 + sgn * 0.18, 6.28, 2.1), 0.02, 0.4,
                 (0.78, 0.74, 0.62, 1.0), segments=5)
        make_cyl("Antler_%+d_Tine" % sgn, (0.8 + sgn * 0.30, 6.28, 2.25), 0.015, 0.2,
                 (0.78, 0.74, 0.62, 1.0), segments=4)


def main():
    clear_scene()
    build_shell()
    build_counter()
    build_table()
    build_chairs()
    build_ceiling_infra()
    out = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)),
        "../../../assets/3d/locales/cabin_interior.glb"))
    print(f"\n[build_cabin_interior] exporting to {out}")
    build_cabin_detail()
    export_glb(out)

if __name__ == "__main__":
    main()
