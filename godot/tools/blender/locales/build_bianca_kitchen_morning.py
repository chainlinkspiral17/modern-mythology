"""bianca_kitchen_morning — vol5-7 locale (auto-generated placement script)."""
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
from _props.detail import (make_traffic_wear, make_floor_stain,
                           make_wall_tint_band, make_threshold,
                           make_wall_outlet, make_light_switch)

ROOM_W = 6.0; ROOM_D = 5.0; CEIL = 2.6
PAL_WALL = {"wall":(0.92,0.86,0.74,1.0),"baseboard":(0.42,0.32,0.22,1.0)}
COL_FLOOR = (0.74,0.58,0.38,1.0); COL_SEAM = (0.42,0.30,0.18,1.0); COL_WOOD = (0.46,0.34,0.22,1.0)
COL_ACCENT = (0.62,0.42,0.22,1.0)

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
    # make_counter's `depth` is the X extent, `length` the Y —
    # so length>depth built this counter ROTATED 90 DEGREES:
    # a narrow face against the wall and the run jutting into
    # the room. Swapped 2026-08-12 (same bug as the New
    # Orleans bar and the pit stop's lunch counter).
    top_z = make_counter("Counter", (-ROOM_W/4.0, ROOM_D-1.35, 0.0), length=0.70, depth=2.40, height=0.92,
                         palette={"formica": (0.78, 0.66, 0.42, 1.0), "top": (0.32, 0.22, 0.14, 1.0), "kick": (0.32, 0.22, 0.14, 1.0)})
    make_counter_bullnose("Counter", (-ROOM_W/4.0, ROOM_D-1.35 - 0.35, top_z), length=2.40, axis='X')
    # Sink + faucet (was missing)
    make_box("Sink_Bowl", (-ROOM_W/4.0, ROOM_D-1.0, 0.86), (0.50, 0.40, 0.12), (0.86, 0.86, 0.84, 1.0))
    make_cyl("Sink_Faucet", (-ROOM_W/4.0, ROOM_D-1.10, top_z+0.04), 0.015, 0.30, P.METAL_STEEL)
    make_box("Sink_Faucet_Spout", (-ROOM_W/4.0, ROOM_D-1.20, top_z+0.28), (0.03, 0.16, 0.03), P.METAL_STEEL)
    # Stove (was missing)
    make_box("Stove_Body", (ROOM_W/4.0, ROOM_D-1.0, 0.45), (0.70, 0.70, 0.92), (0.86, 0.84, 0.80, 1.0))
    make_box("Stove_Top", (ROOM_W/4.0, ROOM_D-1.0, 0.92), (0.70, 0.70, 0.04), P.METAL_BLACK)
    for bi, (bx, by) in enumerate([(-0.16, -0.16), (0.16, -0.16), (-0.16, 0.16), (0.16, 0.16)]):
        make_cyl(f"Stove_Burner_{bi}", (ROOM_W/4.0+bx, ROOM_D-1.0+by, 0.95), 0.09, 0.02, P.METAL_STEEL)
    # Coffee maker on the counter (make_coffee_pots was imported/unused)
    make_coffee_pots("Coffee", (-ROOM_W/4.0-0.90, ROOM_D-1.0, top_z), pots=1)

def build_table():
    tx, ty = 0.0, ROOM_D/2.0
    make_box("Table_Top", (tx, ty, 0.74), (1.20, 0.80, 0.04), COL_WOOD)
    for li in range(4):
        lx = tx + (-0.54, +0.54, -0.54, +0.54)[li]
        ly = ty + (-0.34, -0.34, +0.34, +0.34)[li]
        make_box(f"Table_Leg_{li}", (lx, ly, 0.36), (0.04, 0.04, 0.72), COL_WOOD)
    # Chairs with backs + legs (were missing)
    for ci, (cx, cy) in enumerate([(tx-0.80, ty), (tx+0.80, ty), (tx, ty-0.62), (tx, ty+0.62)]):
        make_box(f"Chair_{ci}_Seat", (cx, cy, 0.44), (0.40, 0.40, 0.04), COL_WOOD)
        ddx, ddy = cx - tx, cy - ty
        if abs(ddx) >= abs(ddy):
            make_box(f"Chair_{ci}_Back", (cx + (0.18 if ddx > 0 else -0.18), cy, 0.70), (0.04, 0.40, 0.48), COL_WOOD)
        else:
            make_box(f"Chair_{ci}_Back", (cx, cy + (0.18 if ddy > 0 else -0.18), 0.70), (0.40, 0.04, 0.48), COL_WOOD)
        for k, (ox, oy) in enumerate([(-0.16, -0.16), (0.16, -0.16), (-0.16, 0.16), (0.16, 0.16)]):
            make_box(f"Chair_{ci}_Leg_{k}", (cx+ox, cy+oy, 0.22), (0.05, 0.05, 0.42), COL_WOOD)
    # Breakfast centerpiece: napkin holder + salt/pepper + fruit bowl
    make_box("NapkinHolder", (tx-0.20, ty, 0.82), (0.14, 0.06, 0.12), (0.86, 0.84, 0.80, 1.0))
    make_cyl("Salt", (tx+0.02, ty, 0.80), 0.025, 0.10, (0.92, 0.92, 0.90, 1.0), segments=8)
    make_cyl("Pepper", (tx+0.08, ty, 0.80), 0.025, 0.10, (0.28, 0.24, 0.22, 1.0), segments=8)
    make_cyl("FruitBowl", (tx+0.30, ty, 0.78), 0.14, 0.08, (0.72, 0.60, 0.40, 1.0), segments=12)
    for fi, (fx, fy, fc) in enumerate([(0.30, 0.0, (0.86, 0.42, 0.28, 1.0)), (0.36, 0.06, (0.90, 0.74, 0.28, 1.0)), (0.26, -0.04, (0.62, 0.72, 0.36, 1.0))]):
        make_cyl(f"Fruit_{fi}", (tx+fx, ty+fy, 0.86), 0.05, 0.10, fc, segments=8)

def build_fridge():
    fx, fy = +ROOM_W/2.0 - 0.50, 1.0
    make_box("Fridge_Body", (fx, fy, 1.00), (0.70, 0.70, 2.00), (0.86, 0.84, 0.80, 1.0))
    make_box("Fridge_DoorTop", (fx-0.34, fy, 1.50), (0.04, 0.66, 0.80), (0.86, 0.84, 0.80, 1.0))
    make_box("Fridge_DoorBot", (fx-0.34, fy, 0.40), (0.04, 0.66, 1.00), (0.86, 0.84, 0.80, 1.0))
    make_box("Fridge_Handle", (fx-0.38, fy-0.20, 1.30), (0.04, 0.04, 0.50), P.METAL_STEEL)

def build_dressing():
    make_calendar("Calendar", (-ROOM_W/2.0+0.05, 2.0, 1.6))
    make_floor_plant("Plant", (-ROOM_W/2.0+0.5, 0.7, 0.0), palette={"leaf": (0.36, 0.48, 0.30, 1.0), "pot": (0.60, 0.40, 0.26, 1.0)})

def build_clock():
    make_wall_clock("Clock", (0.0, ROOM_D-0.12, CEIL-0.50), frozen_hour=4, frozen_min=48)

def build_ceiling_infra():
    # Domestic light, not shop tubes (hero-prop pass)
    make_cyl("Ceiling_Dome", (0.0, 2.2, CEIL-0.10), 0.15, 0.14, (0.94, 0.88, 0.70, 1.0), segments=12)
    make_smoke_detector("Smoke", (0.9, 2.2, CEIL))


def build_hero_props():
    """2026-08-03 tail pass: the kitchen window on the dark
    cul-de-sac, the kettle, the toaster under the clock, the
    dishwasher, the back door + green terrycloth robe, the
    grinder."""
    make_window("Window_N", (-1.5, ROOM_D-0.10, 1.52), width=1.30, height=1.05)
    make_cyl("Kettle", (1.34, 3.84, 1.05), 0.09, 0.18, (0.62, 0.64, 0.65, 1.0), segments=10)
    make_box("Toaster", (-0.55, 3.60, 1.04), (0.28, 0.18, 0.16), (0.72, 0.72, 0.70, 1.0))
    make_box("Dishwasher_Face", (-1.85, 3.00, 0.42), (0.03, 0.60, 0.84), (0.80, 0.78, 0.74, 1.0))
    make_box("Back_Door", (ROOM_W/2.0-0.05, 3.4, 1.05), (0.05, 0.90, 2.10), (0.62, 0.50, 0.36, 1.0))
    make_cyl("Robe_Hook", (ROOM_W/2.0-0.12, 3.05, 1.62), 0.015, 0.06, (0.30, 0.28, 0.26, 1.0), axis='X', segments=6)
    make_box("Green_Robe", (ROOM_W/2.0-0.18, 3.05, 1.24), (0.10, 0.20, 0.76), (0.30, 0.52, 0.36, 1.0))
    make_cyl("Grinder", (-1.55, 3.00, 1.06), 0.05, 0.20, (0.24, 0.24, 0.26, 1.0), segments=8)



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
    out = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)),
        "../../../assets/3d/locales/bianca_kitchen_morning.glb"))
    print(f"\n[build_bianca_kitchen_morning] exporting to {out}")
    export_glb(out)

if __name__ == "__main__":
    main()
