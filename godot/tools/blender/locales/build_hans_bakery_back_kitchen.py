"""hans_bakery_back_kitchen — vol5-7 locale (auto-generated placement script)."""
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

ROOM_W = 6.0; ROOM_D = 5.0; CEIL = 2.8
PAL_WALL = {"wall":(0.96,0.84,0.62,1.0),"baseboard":(0.62,0.42,0.22,1.0)}
COL_FLOOR = (0.62,0.46,0.30,1.0); COL_SEAM = (0.32,0.22,0.14,1.0); COL_WOOD = (0.42,0.30,0.18,1.0)
COL_ACCENT = (0.78,0.42,0.22,1.0)

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

def build_stove():
    # Commercial deck oven: stainless body, two glass doors with warm
    # interiors + bar handles, a vent hood above.
    sx, sy = +ROOM_W/4.0, ROOM_D-1.0
    make_box("Oven_Body", (sx, sy, 0.75), (1.00, 0.80, 1.50), (0.80, 0.82, 0.86, 1.0))
    for di, dz in enumerate([0.55, 1.05]):
        make_box(f"Oven_Door_{di}", (sx-0.42, sy, dz), (0.06, 0.66, 0.40), (0.28, 0.24, 0.22, 1.0))
        make_box(f"Oven_Window_{di}", (sx-0.46, sy, dz), (0.02, 0.46, 0.24), (1.0, 0.62, 0.26, 0.8))
        make_cyl(f"Oven_Handle_{di}", (sx-0.50, sy, dz-0.24), 0.02, 0.60, P.METAL_STEEL, axis='Y', segments=8)
    make_box("Oven_Hood", (sx, sy, 1.70), (1.10, 0.90, 0.30), P.METAL_STEEL)

def build_bakery():
    """Back-of-house bakery: a rolling speed rack of sheet trays + loaves,
    a flour-dusted prep table with dough balls + a rolling pin, stacked
    flour sacks, and a wall shelf of mixing bowls."""
    # Speed rack (rolling tray rack) near the centre
    rx, ry = -0.3, ROOM_D/2.0 - 0.3
    make_box("Rack_Frame", (rx, ry, 0.90), (0.70, 0.60, 1.80), P.METAL_STEEL)
    for ti, tz in enumerate([0.4, 0.7, 1.0, 1.3, 1.6]):
        make_box(f"Rack_Tray_{ti}", (rx, ry, tz), (0.64, 0.54, 0.03), (0.72, 0.72, 0.74, 1.0))
        for li in range(3):
            make_cyl(f"Rack_Loaf_{ti}_{li}", (rx-0.2+li*0.2, ry, tz+0.06), 0.06, 0.26, (0.72, 0.52, 0.30, 1.0), axis='X', segments=8)
    for wi, wx in enumerate([-0.36, 0.36]):
        make_cyl(f"Rack_Wheel_{wi}", (rx+wx, ry, 0.04), 0.05, 0.05, P.METAL_BLACK, axis='X', segments=8)
    # Flour-dusted prep table with dough balls + rolling pin
    tx, ty = -ROOM_W/4.0, ROOM_D/2.0 - 0.8
    make_box("Prep_Top", (tx, ty, 0.90), (1.20, 0.70, 0.06), (0.86, 0.84, 0.80, 1.0))
    for i, (lx, ly) in enumerate([(-0.54, -0.3), (0.54, -0.3), (-0.54, 0.3), (0.54, 0.3)]):
        make_box(f"Prep_Leg_{i}", (tx+lx, ty+ly, 0.45), (0.06, 0.06, 0.90), P.METAL_STEEL)
    for di in range(4):
        make_cyl(f"Dough_{di}", (tx-0.35+di*0.24, ty-0.1, 0.96), 0.07, 0.08, (0.90, 0.86, 0.74, 1.0), segments=10)
    make_cyl("RollingPin", (tx+0.2, ty+0.22, 0.95), 0.04, 0.44, COL_WOOD, axis='X', segments=8)
    # Stacked flour sacks in the SW corner
    for si, (sx2, sz) in enumerate([(-ROOM_W/2.0+0.6, 0.22), (-ROOM_W/2.0+0.55, 0.62), (-ROOM_W/2.0+0.85, 0.22)]):
        make_box(f"FlourSack_{si}", (sx2, 0.7, sz), (0.34, 0.30, 0.42), (0.88, 0.84, 0.76, 1.0))
    # Wall shelf of mixing bowls, west wall
    make_box("BowlShelf", (-ROOM_W/2.0+0.14, ROOM_D-1.4, 1.7), (0.10, 1.20, 0.06), COL_WOOD)
    for bi in range(3):
        make_cyl(f"Bowl_{bi}", (-ROOM_W/2.0+0.30, ROOM_D-1.9+bi*0.5, 1.80), 0.14, 0.16, P.METAL_STEEL, segments=12)

def build_clock():
    make_wall_clock("Clock", (0.0, ROOM_D-0.05, CEIL-0.50), frozen_hour=8, frozen_min=15)

def build_ceiling_infra():
    for j in range(2):
        ypos = ROOM_D * (0.30 + j * 0.40)
        make_fluorescent_tube_fixture(f"Fluor_{j}", (0.0, ypos, CEIL), length=1.40, width=0.34)
    make_smoke_detector("Smoke", (0.0, ROOM_D/2.0, CEIL))

def main():
    clear_scene()
    build_shell()
    build_counter()
    build_stove()
    build_bakery()
    build_clock()
    build_ceiling_infra()
    out = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)),
        "../../../assets/3d/locales/hans_bakery_back_kitchen.glb"))
    print(f"\n[build_hans_bakery_back_kitchen] exporting to {out}")
    export_glb(out)

if __name__ == "__main__":
    main()
