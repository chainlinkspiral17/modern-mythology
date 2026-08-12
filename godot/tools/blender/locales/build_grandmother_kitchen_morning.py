"""Abuela's Kitchen — morning — vol6 placement script."""
import os, sys
_BT = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
if _BT not in sys.path: sys.path.insert(0, _BT)
from _props import palette as P
from _props.geometry import clear_scene, make_box, make_chamfer_box, make_cyl, export_glb
from _props.structure import make_floor, make_wall, make_ceiling, make_crown_molding, make_window
from _props.store_fixtures import make_counter, make_counter_bullnose, make_register
from _props.shelving import make_snack_aisle, make_endcap
from _props.food_service import make_coffee_pots, make_donut_display
from _props.decor import make_wall_clock, make_floor_plant, make_faded_poster, make_calendar
from _props.safety import make_smoke_detector, make_hvac_vent, make_fluorescent_tube_fixture, make_ceiling_speaker

ROOM_W = 5.0; ROOM_D = 5.0; CEIL = 2.6
PAL_WALL = {"wall": (0.96, 0.84, 0.62, 1.0), "baseboard": (0.62, 0.42, 0.22, 1.0)}
COL_FLOOR = (0.62, 0.46, 0.30, 1.0); COL_SEAM = (0.32, 0.22, 0.14, 1.0); COL_WOOD = (0.42, 0.30, 0.18, 1.0)
COL_ACCENT = (0.78, 0.42, 0.22, 1.0)

def build_shell():
    make_floor("Floor", (0.0, ROOM_D/2.0, 0.0), size_x=ROOM_W+0.4, size_y=ROOM_D+0.4,
               palette={"vinyl": COL_FLOOR, "seam": COL_SEAM})
    for nm, x, bb in [("Wall_W", -ROOM_W/2.0, +1), ("Wall_E", +ROOM_W/2.0, -1)]:
        make_wall(nm, (x, ROOM_D/2.0, 0), length=ROOM_D+0.4, height=CEIL, axis='Y',
                  palette=PAL_WALL, baseboard_face_sign=bb)
    make_wall("Wall_N", (0.0, ROOM_D, 0), length=ROOM_W+0.4, height=CEIL, axis='X',
              palette=PAL_WALL, baseboard_face_sign=-1)
    make_wall("Wall_S_W", (-(ROOM_W/4.0+0.5), 0.0, 0), length=ROOM_W/2.0-1.0, height=CEIL, axis='X', palette=PAL_WALL)
    make_wall("Wall_S_E", (+(ROOM_W/4.0+0.5), 0.0, 0), length=ROOM_W/2.0-1.0, height=CEIL, axis='X', palette=PAL_WALL)
    make_box("Wall_S_AboveDoor", (0.0, 0.0, CEIL-0.30), (2.0, 0.20, 0.60), PAL_WALL["wall"])
    make_ceiling("Ceil", (0.0, ROOM_D/2.0, CEIL), size_x=ROOM_W+0.4, size_y=ROOM_D+0.4)
    for nm, ax, length, wx, wy in [
            ("Crown_W", 'Y', ROOM_D, -ROOM_W/2.0+0.10, ROOM_D/2.0),
            ("Crown_E", 'Y', ROOM_D, +ROOM_W/2.0-0.10, ROOM_D/2.0),
            ("Crown_N", 'X', ROOM_W, 0.0, ROOM_D-0.10),
            ("Crown_S", 'X', ROOM_W, 0.0, +0.10)]:
        make_crown_molding(nm, wall_x=wx, wall_y=wy, length=length, axis=ax, ceil_z=CEIL, palette={"wood": COL_WOOD})

def build_counter():
    top_z = make_counter("Counter", (-ROOM_W/4.0, ROOM_D-1.0, 0.0), length=2.40, depth=0.70, height=0.92,
                         palette={"formica": (0.78, 0.66, 0.42, 1.0), "top": (0.32, 0.22, 0.14, 1.0), "kick": (0.32, 0.22, 0.14, 1.0)})
    make_counter_bullnose("Counter", (-ROOM_W/4.0-0.35, ROOM_D-1.0, top_z), length=2.40)
    # Sink
    make_box("Sink_Bowl", (-ROOM_W/4.0, ROOM_D-1.0, 0.86), (0.50, 0.40, 0.12), (0.86, 0.86, 0.84, 1.0))
    make_cyl("Sink_Faucet", (-ROOM_W/4.0, ROOM_D-1.10, top_z+0.04), 0.015, 0.30, P.METAL_STEEL)
    # Stove
    # (stove lives in build_stove() — the duplicate that used to sit
    # here collided with it on export)

def build_table():
    tx, ty = 0.0, ROOM_D/2.0
    make_cyl("Table_Top", (tx, ty, 0.74), 0.55, 0.04, COL_WOOD)
    make_cyl("Table_Pedestal", (tx, ty, 0.37), 0.06, 0.70, COL_WOOD)
    make_cyl("Table_Foot", (tx, ty, 0.04), 0.30, 0.04, COL_WOOD)
    for ci in range(4):
        import math
        ang = ci * 1.57
        cx, cy = tx + math.cos(ang)*0.82, ty + math.sin(ang)*0.82
        make_box(f"Chair_{ci}_Seat", (cx, cy, 0.44), (0.42, 0.42, 0.04), COL_WOOD)
        make_box(f"Chair_{ci}_Back", (cx + math.cos(ang)*0.18, cy + math.sin(ang)*0.18, 0.72), (0.42, 0.04, 0.56), COL_WOOD)
        for li, (lx, ly) in enumerate([(-0.17, -0.17), (0.17, -0.17), (-0.17, 0.17), (0.17, 0.17)]):
            make_box(f"Chair_{ci}_Leg_{li}", (cx+lx, cy+ly, 0.22), (0.05, 0.05, 0.42), COL_WOOD)

def build_stove():
    sx, sy = +ROOM_W/4.0, ROOM_D-1.0
    make_chamfer_box("Stove_Body", (sx, sy, 0.45), (0.80, 0.70, 0.90), (0.92, 0.88, 0.82, 1.0))
    make_box("Stove_Top", (sx, sy, 0.92), (0.80, 0.70, 0.04), P.METAL_BLACK)
    for bi, (bx, by) in enumerate([(-0.22, -0.16), (+0.22, -0.16), (-0.22, +0.16), (+0.22, +0.16)]):
        make_cyl(f"Burner_{bi}", (sx+bx, sy+by, 0.94), 0.08, 0.02, P.METAL_STEEL)

def build_clock():
    make_wall_clock("Clock", (0.0, ROOM_D-0.05, CEIL-0.50), frozen_hour=8, frozen_min=15)

def build_ceiling_infra():
    # An abuela's kitchen: flush dome + a warm pendant over the
    # table, not office tubes
    make_cyl("Ceiling_Dome", (0.0, 2.0, CEIL-0.10), 0.16, 0.16, (0.96, 0.90, 0.72, 1.0), segments=12)
    make_cyl("Table_Pendant_Cord", (0.0, ROOM_D/2.0, CEIL-0.14), 0.008, 0.28, P.METAL_BLACK)
    make_cyl("Table_Pendant_Shade", (0.0, ROOM_D/2.0, CEIL-0.36), 0.15, 0.15, (0.72, 0.52, 0.30, 1.0), segments=12)
    make_smoke_detector("Smoke", (0.9, ROOM_D/2.0, CEIL))


def build_dressing():
    """Grandmotherly warmth: a china hutch of stacked plates + cups, a
    braided oval rug under the table, a tea kettle on the stove, a pie
    + fruit bowl on the table, potted herbs on the counter, and a
    corner floor plant."""
    # China hutch against the west wall
    hx = -ROOM_W/2.0 + 0.28
    make_chamfer_box("Hutch_Body", (hx, ROOM_D/2.0, 1.05), (0.44, 1.20, 2.10), COL_WOOD)
    for sh in range(3):
        make_box(f"Hutch_Glass_{sh}", (hx-0.20, ROOM_D/2.0, 1.20+sh*0.02), (0.02, 1.10, 0.02), (0.78, 0.84, 0.90, 0.4))
        for pi in range(4):
            make_cyl(f"Hutch_Plate_{sh}_{pi}", (hx-0.10, ROOM_D/2.0-0.45+pi*0.30, 1.30+sh*0.42), 0.12, 0.03, (0.90, 0.86, 0.82, 1.0), segments=12)
    # Braided oval rug under the table
    make_cyl("Rug", (0.0, ROOM_D/2.0, 0.008), 1.30, 0.006, (0.72, 0.46, 0.34, 1.0), segments=20)
    # Tea kettle on the stove
    kx, ky = ROOM_W/4.0, ROOM_D-1.0
    make_cyl("Kettle_Body", (kx-0.2, ky, 1.02), 0.10, 0.16, (0.72, 0.68, 0.30, 1.0), segments=12)
    make_cyl("Kettle_Spout", (kx-0.30, ky, 1.06), 0.02, 0.10, (0.72, 0.68, 0.30, 1.0), axis='X', segments=6)
    make_cyl("Kettle_Handle", (kx-0.2, ky, 1.18), 0.015, 0.14, P.METAL_BLACK, axis='X', segments=6)
    # Pie + fruit bowl on the table
    make_cyl("Pie", (-0.18, ROOM_D/2.0, 0.79), 0.14, 0.05, (0.82, 0.62, 0.34, 1.0), segments=14)
    make_cyl("FruitBowl", (0.18, ROOM_D/2.0, 0.80), 0.14, 0.07, (0.66, 0.62, 0.50, 1.0), segments=14)
    for fi, fc in enumerate([(0.86, 0.62, 0.22, 1.0), (0.72, 0.24, 0.20, 1.0), (0.56, 0.62, 0.28, 1.0)]):
        make_cyl(f"Fruit_{fi}", (0.14+fi*0.05, ROOM_D/2.0, 0.86), 0.04, 0.08, fc, segments=8)
    # Potted herbs on the counter
    for hi, hc in enumerate([(0.36, 0.52, 0.30, 1.0), (0.42, 0.56, 0.34, 1.0)]):
        make_cyl(f"HerbPot_{hi}", (-ROOM_W/4.0-0.6+hi*0.3, ROOM_D-1.0, 1.00), 0.06, 0.12, (0.66, 0.40, 0.26, 1.0), segments=8)
        make_cyl(f"Herb_{hi}", (-ROOM_W/4.0-0.6+hi*0.3, ROOM_D-1.0, 1.14), 0.07, 0.14, hc, segments=8)
    # Corner floor plant
    make_floor_plant("Plant", (ROOM_W/2.0-0.5, 0.7, 0.0), palette={"leaf": (0.36, 0.48, 0.30, 1.0), "pot": (0.62, 0.42, 0.28, 1.0)})

def build_hero_props():
    """2026-08-03 hero-prop pass. THE KITCHEN WINDOW she has been at
    every morning since June — over the sink, looking at the
    driveway — with the sill radio (San Antonio news in Spanish),
    the small wooden salt box, the microwave, the yellow chipped
    plate, the exterior screen door, the stair mouth."""
    make_window("Kitchen_Window", (-ROOM_W/4.0, ROOM_D-0.05, 1.52), width=1.40, height=1.00)
    make_box("Window_Sill", (-ROOM_W/4.0, ROOM_D-0.20, 1.02), (1.55, 0.22, 0.05), COL_WOOD)
    # The kitchen radio, just a radio
    make_chamfer_box("Kitchen_Radio", (-1.75, ROOM_D-0.20, 1.12), (0.24, 0.14, 0.14), (0.44, 0.30, 0.22, 1.0))
    make_cyl("Radio_Dial", (-1.66, ROOM_D-0.28, 1.12), 0.03, 0.02, (0.86, 0.82, 0.72, 1.0), axis='Y', segments=8)
    # The small wooden salt box
    make_chamfer_box("Salt_Box", (-0.95, ROOM_D-0.20, 1.095), (0.10, 0.10, 0.09), (0.58, 0.44, 0.28, 1.0))
    # Microwave, counter east end
    make_chamfer_box("Microwave", (-0.45, ROOM_D-1.0, 1.14), (0.50, 0.38, 0.30), (0.82, 0.80, 0.76, 1.0))
    make_chamfer_box("Microwave_Door", (-0.45, ROOM_D-1.20, 1.14), (0.38, 0.02, 0.22), (0.20, 0.20, 0.22, 1.0))
    # The yellow plate with the chip, set at his place
    make_cyl("Yellow_Plate", (0.0, ROOM_D/2.0-0.30, 0.77), 0.12, 0.012, (0.90, 0.82, 0.38, 1.0), segments=14)
    make_box("Plate_Chip", (0.115, ROOM_D/2.0-0.30, 0.775), (0.02, 0.02, 0.014), (0.96, 0.93, 0.74, 1.0))
    # Exterior screen door to the porch, E wall
    make_box("Porch_Door", (ROOM_W/2.0-0.05, 1.5, 1.05), (0.05, 0.90, 2.10), (0.62, 0.50, 0.36, 1.0))
    make_box("Porch_Door_Screen", (ROOM_W/2.0-0.08, 1.5, 1.25), (0.02, 0.64, 1.30), (0.42, 0.42, 0.40, 0.45))
    # Stair mouth at the S gap edge (up + the sopa-de-pollo down)
    make_box("Stair_Newel", (0.92, 0.15, 0.60), (0.10, 0.10, 1.20), COL_WOOD)
    for s in range(3):
        make_box(f"Stair_Tread_{s}", (1.35, 0.20 - s * 0.0, 0.16 + s * 0.18), (0.75, 0.28, 0.05), COL_WOOD)


def main():
    clear_scene()
    build_shell()
    build_counter()
    build_table()
    build_stove()
    build_dressing()
    build_hero_props()
    build_clock()
    build_ceiling_infra()
    out = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)),
        "../../../assets/3d/locales/grandmother_kitchen_morning.glb"))
    print(f"\n[build_grandmother_kitchen_morning] exporting to {out}")
    export_glb(out)

if __name__ == "__main__":
    main()
