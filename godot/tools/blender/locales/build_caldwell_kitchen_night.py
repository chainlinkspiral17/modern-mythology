"""caldwell_kitchen_night — vol5-7 locale (auto-generated placement script)."""
import os, sys
_BT = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
if _BT not in sys.path: sys.path.insert(0, _BT)
from _props.furniture import make_table, make_chair
from _props import palette as P
from _props.geometry import clear_scene, make_box, make_cyl, export_glb
from _props.views import make_view
from _props.structure import make_floor, make_wall, make_ceiling, make_crown_molding, make_window, make_wall_with_openings
from _props.store_fixtures import make_counter, make_counter_bullnose, make_register
from _props.shelving import make_snack_aisle, make_endcap
from _props.food_service import make_coffee_pots
from _props.decor import make_wall_clock, make_floor_plant, make_faded_poster, make_calendar
from _props.safety import make_smoke_detector, make_hvac_vent, make_fluorescent_tube_fixture
from _props.detail import (make_traffic_wear, make_floor_stain,
                           make_wall_tint_band, make_threshold,
                           make_wall_outlet, make_light_switch)

# 2026-09-25: the counter run and the stove stood at ROOM_D-0.45 — 0.55 m off the N wall in every kitchen from this template; ROOM_D-0.45 puts their backs on the wall face
ROOM_W = 6.0; ROOM_D = 5.0; CEIL = 2.6
PAL_WALL = {"wall":(0.92,0.86,0.74,1.0),"baseboard":(0.42,0.32,0.22,1.0)}
COL_FLOOR = (0.74,0.58,0.38,1.0); COL_SEAM = (0.42,0.30,0.18,1.0); COL_WOOD = (0.46,0.34,0.22,1.0)
COL_ACCENT = (0.62,0.42,0.22,1.0)
# Linda Caldwell's kitchen on the kit (2026-10-08): pale sage cabinets,
# cream laminate with a chrome edge, the pink tile, chrome pulls
from _props import kitchen_kit as K
from _props.geometry import make_lathe, make_tube
Y_BACK = ROOM_D - 0.10
TOP_Z = 0.92
SINK_X, RANGE_X = -1.5, ROOM_W/4.0
SAGE = (0.64, 0.72, 0.60, 1.0); SAGE_DK = (0.52, 0.60, 0.50, 1.0)
CREAM = (0.92, 0.88, 0.78, 1.0); CHROME = (0.80, 0.82, 0.84, 1.0)
PINK = (0.90, 0.74, 0.74, 1.0)

def build_shell():
    make_floor("Floor", (0.0, ROOM_D/2.0, 0.0), size_x=ROOM_W+0.4, size_y=ROOM_D+0.4,
               palette={"vinyl": COL_FLOOR, "seam": COL_SEAM})
    for nm, x, bb in [("Wall_W", -ROOM_W/2.0, +1), ("Wall_E", +ROOM_W/2.0, -1)]:
        make_wall(nm, (x, ROOM_D/2.0, 0), length=ROOM_D+0.4, height=CEIL, axis='Y', palette=PAL_WALL, baseboard_face_sign=bb)
    make_wall_with_openings("Wall_N", (0.0, ROOM_D, 0), length=ROOM_W+0.4, height=CEIL, axis='X', palette=PAL_WALL, baseboard_face_sign=-1, openings=[(-1.5, 1.52, 1.20, 1.00)])   # cut 2026-10-07: its window was a pane on a solid wall
    make_wall("Wall_S_W", (-(ROOM_W/4.0+0.5), 0.0, 0), length=ROOM_W/2.0-1.0, height=CEIL, axis='X', palette=PAL_WALL, baseboard_face_sign=+1)
    make_wall("Wall_S_E", (+(ROOM_W/4.0+0.5), 0.0, 0), length=ROOM_W/2.0-1.0, height=CEIL, axis='X', palette=PAL_WALL, baseboard_face_sign=+1)
    make_box("Wall_S_AboveDoor", (0.0, 0.0, CEIL-0.30), (2.0, 0.20, 0.60), PAL_WALL["wall"])
    make_ceiling("Ceil", (0.0, ROOM_D/2.0, CEIL), size_x=ROOM_W+0.4, size_y=ROOM_D+0.4, with_grid=False)

def build_counter():
    """The N run on the kitchen kit (2026-10-08: a store counter and a box
    stove). The sink under the window — "Maya, in the kitchen, pouring
    herself a glass of water before bed, pauses at the window" — the
    range, uppers clear of the window and the clock, the pink tile, and
    the sill with the radio on it ("The radio, on the windowsill, stays
    off")."""
    K.base_run("Counter", -ROOM_W/2.0 + 0.10, ROOM_W/2.0 - 0.10, Y_BACK, top_z=TOP_Z,
               body=SAGE, top=CREAM, edge=CHROME, pull=CHROME, rail=SAGE_DK,
               gaps=[(RANGE_X - 0.38, RANGE_X + 0.38)])
    K.sink("Sink", SINK_X, Y_BACK, TOP_Z)
    K.range_("Stove", RANGE_X, Y_BACK, TOP_Z)
    for nm, a, b in (("Upper_W", -ROOM_W/2.0 + 0.10, SINK_X - 0.75), ("Upper_Mid", 0.40, RANGE_X - 0.42),
                     ("Upper_E", RANGE_X + 0.42, ROOM_W/2.0 - 0.10)):
        K.upper_run(nm, a, b, Y_BACK, z0=1.46, z1=2.20, body=SAGE, pull=CHROME, rail=SAGE_DK)
    K.backsplash("Splash", -ROOM_W/2.0 + 0.10, ROOM_W/2.0 - 0.10, Y_BACK, TOP_Z, 1.00, tile=PINK,
                 grout=(0.78, 0.62, 0.62, 1.0))
    # the sill, and her radio on it — off
    make_box("Window_Sill", (SINK_X, Y_BACK - 0.07, 1.005), (1.34, 0.14, 0.03), CREAM)
    rx = SINK_X - 0.38
    make_box("Sill_Radio", (rx, Y_BACK - 0.08, 1.02 + 0.07), (0.26, 0.11, 0.14), (0.88, 0.82, 0.68, 1.0))
    make_box("Sill_Radio_Grille", (rx - 0.05, Y_BACK - 0.1355, 1.02 + 0.07), (0.12, 0.002, 0.10), (0.46, 0.34, 0.24, 1.0))
    make_cyl("Sill_Radio_Dial", (rx + 0.08, Y_BACK - 0.138, 1.02 + 0.07), 0.03, 0.006, (0.94, 0.86, 0.56, 1.0), axis='Y', segments=12)
    make_box("Sill_Radio_Handle", (rx, Y_BACK - 0.08, 1.02 + 0.15), (0.16, 0.02, 0.02), (0.46, 0.34, 0.24, 1.0))
    # the percolator on the back burner
    make_lathe("Percolator", (RANGE_X + 0.19, Y_BACK - 0.33 + 0.16, TOP_Z), [(0.07, 0.0), (0.08, 0.04), (0.06, 0.20), (0.05, 0.24), (0.0, 0.24)],
               CHROME, segments=12)
    make_lathe("Percolator_Knob", (RANGE_X + 0.19, Y_BACK - 0.33 + 0.16, TOP_Z + 0.24), [(0.02, 0.0), (0.02, 0.03), (0.0, 0.04)],
               (0.70, 0.74, 0.78, 1.0), segments=8)
    make_tube("Percolator_Spout", [(RANGE_X + 0.25, Y_BACK - 0.17, TOP_Z + 0.16), (RANGE_X + 0.29, Y_BACK - 0.17, TOP_Z + 0.20)], 0.01, CHROME)

def build_table():
    tx, ty = 0.0, ROOM_D/2.0
    # DETAIL DRAFT 3 (2026-09-06): the table and its four chairs through the
    # furniture kit — turned legs, aprons, a stretcher; spindled chair backs
    # turned away from the table. Names keep Table_Top / Chair_N_Seat.
    make_table("Table", tx, ty, w=1.20, d=0.80, h=0.76, wood=COL_WOOD)
    for ci, (cx, cy, yaw) in enumerate([(tx-0.80, ty, -1.5708), (tx+0.80, ty, 1.5708), (tx, ty-0.62, 0.0), (tx, ty+0.62, 3.1416)]):
        make_chair(f"Chair_{ci}", cx, cy, yaw=yaw, wood=COL_WOOD)

def build_fridge():
    fx, fy = +ROOM_W/2.0 - 0.55, 1.0
    make_box("Fridge_Body", (fx, fy, 1.00), (0.70, 0.70, 2.00), (0.82, 0.82, 0.84, 1.0))
    make_box("Fridge_DoorTop", (fx-0.34, fy, 1.50), (0.04, 0.66, 0.80), (0.82, 0.82, 0.84, 1.0))
    make_box("Fridge_DoorBot", (fx-0.34, fy, 0.40), (0.04, 0.66, 1.00), (0.82, 0.82, 0.84, 1.0))
    make_box("Fridge_Handle", (fx-0.38, fy-0.20, 1.30), (0.04, 0.04, 0.50), P.METAL_STEEL)

def build_dressing():
    cw_x = -ROOM_W/4.0; cw_y = ROOM_D-0.45
    make_calendar("Calendar", (-ROOM_W/2.0+0.05, 2.0, 1.6))
    tx, ty = 0.0, ROOM_D/2.0
    make_box("NapkinHolder", (tx, ty, 0.82), (0.14, 0.06, 0.12), (0.86, 0.84, 0.80, 1.0))
    make_cyl("Salt", (tx+0.16, ty, 0.80), 0.025, 0.10, (0.92, 0.92, 0.90, 1.0), segments=8)
    make_cyl("Pepper", (tx+0.22, ty, 0.80), 0.025, 0.10, (0.28, 0.24, 0.22, 1.0), segments=8)
    make_floor_plant("Plant", (-ROOM_W/2.0+0.5, 0.7, 0.0), palette={"leaf": (0.36, 0.48, 0.30, 1.0), "pot": (0.60, 0.40, 0.26, 1.0)})

def build_clock():
    make_wall_clock("Clock", (0.0, 4.900, CEIL-0.50), frozen_hour=11, frozen_min=5, facing='-Y')

def build_ceiling_infra():
    # Domestic light, not shop tubes (hero-prop pass)
    make_cyl("Ceiling_Dome", (0.0, 2.2, CEIL-0.10), 0.15, 0.14, (0.94, 0.88, 0.70, 1.0), segments=12)
    make_smoke_detector("Smoke", (0.9, 2.2, CEIL))


def build_hero_props():
    """2026-08-03 tail pass: the night window Maya pauses at (the
    dogs), the water glass, the stair mouth, burners + oven face on
    the blank stove."""
    make_window("Window_N", (-1.5, ROOM_D-0.10, 1.52), width=1.20, height=1.00, see_through=True)
    make_cyl("Water_Glass", (SINK_X + 0.62, Y_BACK - 0.40, TOP_Z + 0.06), 0.035, 0.12, (0.55, 0.62, 0.66, 0.5), segments=8)
    make_box("Stair_Newel", (0.92, 0.15, 0.60), (0.10, 0.10, 1.20), (0.46, 0.34, 0.22, 1.0))
    for s in range(3):
        make_box(f"Stair_Tread_{s}", (1.4, 0.20 + s * 0.28, (0.185 + s * 0.18) / 2.0), (0.80, 0.28, 0.185 + s * 0.18), (0.46, 0.34, 0.22, 1.0))   # solid step (2026-09-08)
    # (2026-10-08: the burners and oven face are the kit range's own)



def build_detail_pass_2026_08():
    """D2 surface breakup + first D3 (generic template pass per
    lore/_SET_DETAIL_PLAYBOOK.md): the entry walk-line, a work-zone
    stain, ceiling gather on the long walls, a threshold, and the
    switch/outlet pair every room earns. Per-locale wear
    PERSONALITY (whose feet, whose spills) is the next pass."""
    wear = (COL_FLOOR[0] * 0.88, COL_FLOOR[1] * 0.88, COL_FLOOR[2] * 0.88, 1.0)
    stain = (COL_FLOOR[0] * 0.82, COL_FLOOR[1] * 0.82, COL_FLOOR[2] * 0.82, 1.0)
    pw = PAL_WALL["wall"]
    band = (pw[0] * 0.90, pw[1] * 0.90, pw[2] * 0.88, 1.0)
    make_traffic_wear("Wear_Entry", [(0.0, 0.6), (0.0, ROOM_D * 0.55)],
                      width=0.75, tint=wear)
    make_floor_stain("Stain_WorkZone", (ROOM_W * 0.22, ROOM_D * 0.62),
                     radius=0.24, tint=stain)
    make_wall_tint_band("Band_W", (-ROOM_W / 2.0 + 0.105, ROOM_D / 2.0, 0.0),
                        length=ROOM_D - 0.4, axis='Y', band_z=CEIL - 0.16, tint=band)
    make_wall_tint_band("Band_E", (ROOM_W / 2.0 - 0.105, ROOM_D / 2.0, 0.0),
                        length=ROOM_D - 0.4, axis='Y', band_z=CEIL - 0.16, tint=band)
    make_threshold("Threshold_Entry", (0.0, 0.10), width=1.9, axis='X')
    make_light_switch("Switch_Entry", (1.15, 0.0), axis='X', face_sign=1, aged=True)
    make_wall_outlet("Outlet_W", (-ROOM_W / 2.0, ROOM_D * 0.35), axis='Y',
                     face_sign=1, aged=True)
    make_wall_outlet("Outlet_E", (ROOM_W / 2.0, ROOM_D * 0.70), axis='Y',
                     face_sign=-1, aged=True)


def main():
    clear_scene()
    build_shell()
    build_counter()
    build_table()
    build_fridge()
    build_dressing()
    build_clock()
    build_ceiling_infra()
    build_hero_props()
    build_detail_pass_2026_08()
    # what is outside the window (2026-10-07, _props/views.py)
    make_view("View_N", "N", ROOM_D, -1.5, kind="back", ground_z=0.0, seed=9)
    out = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)),
        "../../../assets/3d/locales/caldwell_kitchen_night.glb"))
    print(f"\n[build_caldwell_kitchen_night] exporting to {out}")
    export_glb(out)

if __name__ == "__main__":
    main()
