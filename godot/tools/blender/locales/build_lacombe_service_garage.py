"""VII · CHARIOT — Old Lacombe Service Garage. Two-bay repair
garage attached to a small gas pump island. Hydraulic lift in
bay 1, tow truck up on jacks in bay 2 (partial), parts pegboard
on the back wall, oil drums in the corner, a beat-up vending
machine in the office vestibule. The drive itself in stasis.
"""
import os, sys
_BT = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
if _BT not in sys.path: sys.path.insert(0, _BT)
from _props import palette as P
from _props.geometry import clear_scene, make_box, make_cyl, export_glb
from _props.structure import make_floor, make_wall, make_ceiling, make_crown_molding
from _props.decor import make_wall_clock, make_faded_poster, make_calendar
from _props.safety import (make_smoke_detector, make_sprinkler,
                            make_fluorescent_tube_fixture, make_security_camera)

PAL = {"wall": (0.72, 0.68, 0.58, 1.0), "baseboard": (0.32, 0.28, 0.22, 1.0)}
COL_FLOOR_CONCRETE = (0.46, 0.44, 0.42, 1.0); COL_SEAM = (0.28, 0.26, 0.24, 1.0)
COL_OIL_STAIN = (0.18, 0.14, 0.12, 1.0); COL_LIFT_YELLOW = (0.86, 0.74, 0.20, 1.0)
COL_TRUCK_BODY = (0.42, 0.30, 0.22, 1.0); COL_TIRE = (0.16, 0.14, 0.14, 1.0)
COL_PARTS_RED = (0.74, 0.22, 0.20, 1.0); COL_PEGBOARD = (0.62, 0.46, 0.30, 1.0)
COL_PUMP = (0.78, 0.78, 0.74, 1.0); COL_PUMP_TOP = (0.62, 0.18, 0.18, 1.0)
COL_OIL_DRUM = (0.32, 0.28, 0.18, 1.0); COL_VEND_BLUE = (0.20, 0.42, 0.62, 1.0)
COL_TOOLBOX_RED = (0.74, 0.22, 0.20, 1.0)

ROOM_W = 10.0; ROOM_D = 9.0; CEIL = 4.20  # garage ceiling is taller


def build_shell():
    make_floor("Floor", (0.0, ROOM_D/2.0, 0.0), size_x=ROOM_W+0.4, size_y=ROOM_D+0.4,
               palette={"vinyl": COL_FLOOR_CONCRETE, "seam": COL_SEAM})
    # Oil stains on the concrete — abstract puddles
    for si, (sx, sy, sr) in enumerate([(+2.0, 3.0, 0.80), (-2.0, 4.5, 0.60),
                                        (0.0, 5.5, 0.50), (+3.0, 7.0, 0.40)]):
        make_cyl(f"Oil_{si}", (sx, sy, 0.01), sr, 0.003, COL_OIL_STAIN, segments=10)
    for nm, x, bb in [("Wall_W", -ROOM_W/2.0, +1), ("Wall_E", +ROOM_W/2.0, -1)]:
        make_wall(nm, (x, ROOM_D/2.0, 0), length=ROOM_D+0.4, height=CEIL, axis='Y',
                  palette=PAL, baseboard_face_sign=bb)
    make_wall("Wall_N", (0.0, ROOM_D, 0), length=ROOM_W+0.4, height=CEIL, axis='X',
              palette=PAL, baseboard_face_sign=-1)
    # S wall has TWO big roll-up bay doors (open / partial)
    make_wall("Wall_S_W", (-4.20, 0.0, 0), length=1.40, height=CEIL, axis='X', palette=PAL)
    make_wall("Wall_S_Mid", (0.0, 0.0, 0), length=1.60, height=CEIL, axis='X', palette=PAL)
    make_wall("Wall_S_E", (+4.20, 0.0, 0), length=1.40, height=CEIL, axis='X', palette=PAL)
    # Roll-up door tracks above the bays (signal of bay doors)
    make_box("Bay_Door_W_Track", (-2.50, 0.10, 3.80), (2.20, 0.10, 0.20), COL_PEGBOARD)
    make_box("Bay_Door_E_Track", (+2.50, 0.10, 3.80), (2.20, 0.10, 0.20), COL_PEGBOARD)
    make_ceiling("Ceil", (0.0, ROOM_D/2.0, CEIL), size_x=ROOM_W+0.4, size_y=ROOM_D+0.4)
    for nm, ax, length, wx, wy in [("Crown_W",'Y',ROOM_D,-ROOM_W/2.0+0.10,ROOM_D/2.0),
                                    ("Crown_E",'Y',ROOM_D,+ROOM_W/2.0-0.10,ROOM_D/2.0),
                                    ("Crown_N",'X',ROOM_W,0.0,ROOM_D-0.10)]:
        make_crown_molding(nm, wall_x=wx, wall_y=wy, length=length, axis=ax,
                           ceil_z=CEIL, palette={"wood": COL_PEGBOARD})


def build_hydraulic_lift():
    # Bay 1 (W) — empty lift, arms down
    lx, ly = -2.50, 4.50
    make_box("Lift_Base",  (lx, ly, 0.06), (0.80, 0.40, 0.12), COL_LIFT_YELLOW)
    make_cyl("Lift_Post_S", (lx, ly-0.30, 1.50), 0.10, 3.00, COL_LIFT_YELLOW, segments=10)
    make_cyl("Lift_Post_N", (lx, ly+0.30, 1.50), 0.10, 3.00, COL_LIFT_YELLOW, segments=10)
    # Lift arms (down position)
    for sgn in (-1, +1):
        make_box(f"Lift_Arm_{sgn:+d}_S", (lx + sgn*0.80, ly-0.30, 0.46),
                 (1.50, 0.10, 0.10), COL_LIFT_YELLOW)
        make_box(f"Lift_Arm_{sgn:+d}_N", (lx + sgn*0.80, ly+0.30, 0.46),
                 (1.50, 0.10, 0.10), COL_LIFT_YELLOW)


def build_tow_truck():
    # Bay 2 (E) — partially-disassembled tow truck on jack stands
    tx, ty = +2.50, 4.50
    # Cab
    make_box("Truck_Cab", (tx, ty-1.10, 1.40), (1.60, 1.00, 1.00), COL_TRUCK_BODY)
    make_box("Truck_Hood", (tx, ty-0.30, 1.20), (1.40, 0.80, 0.30), COL_TRUCK_BODY)
    # Bed + boom
    make_box("Truck_Bed", (tx, ty+0.80, 1.20), (1.60, 1.40, 0.40), COL_TRUCK_BODY)
    make_box("Truck_Boom", (tx, ty+1.50, 2.00), (0.20, 2.00, 0.20), (0.32, 0.32, 0.32, 1.0))
    # Hook
    make_box("Truck_Hook", (tx, ty+2.40, 1.80), (0.10, 0.30, 0.20), (0.32, 0.32, 0.32, 1.0))
    # Jack stands (4) instead of wheels
    for sgn_x in (-1, +1):
        for sgn_y in (-1, +1):
            jsy = ty - 0.80 + (sgn_y+1)*0.80
            make_box(f"JackStand_{sgn_x:+d}_{sgn_y:+d}", (tx+sgn_x*0.60, jsy, 0.30),
                     (0.20, 0.20, 0.60), COL_TIRE)
    # Removed wheel pile next to the truck
    for wi in range(2):
        make_cyl(f"Wheel_Pile_{wi}", (tx-1.50, ty + wi*0.30 - 0.20, 0.30 + wi*0.16),
                 0.30, 0.14, COL_TIRE, axis='X', segments=12)


def build_parts_pegboard_and_workbench():
    # N wall: pegboard with tool silhouettes
    make_box("Pegboard", (0.0, ROOM_D-0.06, 2.20), (4.00, 0.02, 1.40), COL_PEGBOARD)
    for ti in range(10):
        tx = -1.80 + ti * 0.40
        make_box(f"Peg_Tool_{ti}", (tx, ROOM_D-0.10, 2.20),
                 (0.06, 0.005, 0.36), (0.18, 0.18, 0.20, 1.0))
    # Workbench below
    make_box("Bench_Top",  (0.0, ROOM_D-0.50, 0.96), (3.60, 0.50, 0.06), (0.22, 0.16, 0.12, 1.0))
    make_box("Bench_Body", (0.0, ROOM_D-0.50, 0.46), (3.60, 0.50, 0.92), (0.32, 0.24, 0.18, 1.0))
    # Toolbox
    make_box("Toolbox", (-1.40, ROOM_D-0.50, 1.10), (0.50, 0.30, 0.30), COL_TOOLBOX_RED)
    # Bench vise
    make_box("Vise_Base", (+1.40, ROOM_D-0.50, 1.04), (0.16, 0.16, 0.12), (0.32, 0.32, 0.32, 1.0))
    make_box("Vise_Jaw_F", (+1.40, ROOM_D-0.40, 1.14), (0.20, 0.04, 0.14), (0.32, 0.32, 0.32, 1.0))
    make_box("Vise_Jaw_B", (+1.40, ROOM_D-0.56, 1.14), (0.20, 0.04, 0.14), (0.32, 0.32, 0.32, 1.0))


def build_pump_island_in_front_of_bays():
    # Visible through the S bay openings — small pump island at S edge.
    px = -ROOM_W/2.0 + 2.50
    make_box("Pump_Island", (0.0, -1.20, 0.04), (2.40, 0.80, 0.08), (0.62, 0.62, 0.58, 1.0))
    for sgn in (-1, +1):
        pcx = sgn * 0.80
        make_box(f"Pump_Body_{sgn:+d}", (pcx, -1.20, 0.50), (0.30, 0.40, 0.90), COL_PUMP)
        make_box(f"Pump_Top_{sgn:+d}", (pcx, -1.20, 1.04), (0.30, 0.40, 0.20), COL_PUMP_TOP)
        # Display window
        make_box(f"Pump_Display_{sgn:+d}", (pcx, -1.40, 0.80), (0.20, 0.005, 0.20),
                 (0.18, 0.42, 0.34, 1.0))
        # Hose
        make_box(f"Pump_Hose_{sgn:+d}", (pcx, -1.10, 0.70), (0.04, 0.04, 0.40), P.METAL_BLACK)
    # Pole sign in the distance
    make_cyl("Pole", (0.0, -4.0, 3.0), 0.10, 6.0, P.METAL_BLACK)
    make_box("PoleSign", (0.0, -4.0, 5.80), (1.60, 0.10, 0.80), COL_PUMP_TOP)


def build_oil_drums_and_vending():
    # Oil drums in NW corner
    for di in range(3):
        dx = -ROOM_W/2.0 + 0.70
        dy = ROOM_D - 1.80 + di * 0.60
        make_cyl(f"OilDrum_{di}", (dx, dy, 0.50), 0.30, 1.00, COL_OIL_DRUM, segments=10)
        make_cyl(f"OilDrum_Top_{di}", (dx, dy, 1.02), 0.32, 0.02, P.METAL_BLACK, segments=10)
    # Vending machine in SE corner (the office vestibule)
    vx, vy = +ROOM_W/2.0 - 0.40, 1.00
    make_box("Vending_Body", (vx, vy, 0.90), (0.40, 0.50, 1.80), COL_VEND_BLUE)
    make_box("Vending_Window", (vx-0.18, vy, 1.20), (0.005, 0.40, 0.80), (0.78, 0.84, 0.86, 0.55))
    # Bottles inside (column of three)
    for bi in range(3):
        make_cyl(f"Vend_Bottle_{bi}", (vx-0.10, vy, 0.90 + bi*0.30),
                 0.04, 0.20, (0.74, 0.22, 0.20, 1.0), segments=8)


def build_ceiling_infra():
    for j, ypos in enumerate([2.5, 5.5]):
        make_fluorescent_tube_fixture(f"Fluor_{j}", (0.0, ypos, CEIL),
                                       length=2.00, width=0.32,
                                       palette={"diffuser": (0.96, 0.94, 0.86, 1.0)})
    make_smoke_detector("Smoke", (0.0, 4.5, CEIL))
    make_sprinkler("Spr_W", (-2.5, 4.5, CEIL))
    make_sprinkler("Spr_E", (+2.5, 4.5, CEIL))
    make_security_camera("Cam", (+ROOM_W/2.0-0.10, 4.5, CEIL-0.20))


def build_decor():
    make_wall_clock("Clock", (-ROOM_W/2.0+0.05, 1.5, 2.30), frozen_hour=4, frozen_min=15)
    make_calendar("Calendar", (+ROOM_W/2.0-0.05, 6.5, 2.20))
    make_faded_poster("Poster_Pinup", (-ROOM_W/2.0+0.05, 6.5, 1.80))


def main():
    clear_scene()
    build_shell()
    build_hydraulic_lift()
    build_tow_truck()
    build_parts_pegboard_and_workbench()
    build_pump_island_in_front_of_bays()
    build_oil_drums_and_vending()
    build_ceiling_infra()
    build_decor()
    out = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                         "../../../assets/3d/locales/lacombe_service_garage.glb"))
    print(f"\n[build_lacombe_service_garage] exporting to {out}")
    export_glb(out)


if __name__ == "__main__":
    main()
