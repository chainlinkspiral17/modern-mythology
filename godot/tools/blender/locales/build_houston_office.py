"""VOL 5 · Houston Office — Emperor chapter.
Generic corporate office: glass partition, cubicle row, fluorescents.
"""
import os, sys
_BT = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
if _BT not in sys.path: sys.path.insert(0, _BT)
from _props import palette as P
from _props.geometry import clear_scene, make_box, make_cyl, export_glb
from _props.structure import make_floor, make_wall, make_ceiling, make_window, make_crown_molding
from _props.decor import make_wall_clock, make_floor_plant
from _props.safety import make_smoke_detector, make_hvac_vent, make_fluorescent_tube_fixture, make_ceiling_speaker, make_security_camera

PAL_WALL = {"wall": (0.86, 0.84, 0.80, 1.0), "baseboard": (0.32, 0.30, 0.28, 1.0)}
COL_CARPET = (0.32, 0.30, 0.32, 1.0); COL_CARPET_SEAM = (0.22, 0.20, 0.22, 1.0)
COL_DESK = (0.42, 0.32, 0.22, 1.0); COL_PARTITION = (0.62, 0.62, 0.60, 1.0)
COL_CHAIR = (0.18, 0.16, 0.18, 1.0); COL_MONITOR = (0.10, 0.12, 0.14, 1.0)
COL_GLASS = (0.78, 0.84, 0.86, 0.50); COL_TRIM = (0.32, 0.28, 0.24, 1.0)
ROOM_W = 10.0; ROOM_D = 7.0; CEIL = 2.80

def build_shell():
    make_floor("Floor", (0.0, ROOM_D/2.0, 0.0), size_x=ROOM_W+0.4, size_y=ROOM_D+0.4,
               palette={"vinyl": COL_CARPET, "seam": COL_CARPET_SEAM})
    for nm, x, ax, length, bb in [
            ("Wall_W", -ROOM_W/2.0, 'Y', ROOM_D+0.4, +1),
            ("Wall_E", +ROOM_W/2.0, 'Y', ROOM_D+0.4, -1)]:
        make_wall(nm, (x, ROOM_D/2.0, 0), length=length, height=CEIL, axis=ax, palette=PAL_WALL, baseboard_face_sign=bb)
    make_wall("Wall_N", (0.0, ROOM_D, 0), length=ROOM_W+0.4, height=CEIL, axis='X', palette=PAL_WALL, baseboard_face_sign=-1)
    make_wall("Wall_S", (0.0, 0.0, 0), length=ROOM_W+0.4, height=CEIL, axis='X', palette=PAL_WALL, baseboard_face_sign=+1)
    make_ceiling("Ceil", (0.0, ROOM_D/2.0, CEIL), size_x=ROOM_W+0.4, size_y=ROOM_D+0.4)
    for nm, ax, length, wx, wy in [("Crown_W",'Y',ROOM_D,-ROOM_W/2.0+0.10,ROOM_D/2.0),("Crown_E",'Y',ROOM_D,+ROOM_W/2.0-0.10,ROOM_D/2.0),("Crown_N",'X',ROOM_W,0.0,ROOM_D-0.10),("Crown_S",'X',ROOM_W,0.0,+0.10)]:
        make_crown_molding(nm, wall_x=wx, wall_y=wy, length=length, axis=ax, ceil_z=CEIL, palette={"wood": COL_TRIM})
    # Large window N wall, looking at downtown
    make_box("Window_N_Frame", (0.0, ROOM_D-0.04, 1.65), (5.0, 0.04, 2.20), P.METAL_STEEL)
    make_box("Window_N_Glass", (0.0, ROOM_D-0.06, 1.65), (4.80, 0.005, 2.00), COL_GLASS)

def build_cubicles():
    # 3 cubicles in centre, partitioned
    for ci, cx in enumerate([-2.5, 0.0, +2.5]):
        cy = 3.5
        # Partition walls (chest-high)
        for px_off, pn in [(-0.90, 'L'), (+0.90, 'R')]:
            make_box(f"Cub_{ci}_Part_{pn}", (cx+px_off, cy, 0.85), (0.04, 1.20, 1.70), COL_PARTITION)
        make_box(f"Cub_{ci}_Back", (cx, cy+0.60, 0.85), (1.80, 0.04, 1.70), COL_PARTITION)
        # Desk
        make_box(f"Cub_{ci}_Desk", (cx, cy, 0.72), (1.60, 0.70, 0.04), COL_DESK)
        for li, (lx, ly) in enumerate([(cx-0.74,cy-0.30),(cx+0.74,cy-0.30),(cx-0.74,cy+0.30),(cx+0.74,cy+0.30)]):
            make_box(f"Cub_{ci}_DeskLeg_{li}", (lx, ly, 0.36), (0.04, 0.04, 0.72), COL_TRIM)
        # Monitor
        make_box(f"Cub_{ci}_Monitor", (cx, cy+0.20, 1.00), (0.50, 0.04, 0.30), COL_MONITOR)
        make_box(f"Cub_{ci}_MonStand", (cx, cy+0.20, 0.80), (0.10, 0.10, 0.16), P.METAL_BLACK)
        # Chair
        make_box(f"Cub_{ci}_ChairSeat", (cx, cy-0.50, 0.50), (0.42, 0.42, 0.04), COL_CHAIR)
        make_box(f"Cub_{ci}_ChairBack", (cx, cy-0.70, 0.80), (0.42, 0.04, 0.60), COL_CHAIR)
        make_cyl(f"Cub_{ci}_ChairBase", (cx, cy-0.50, 0.06), 0.20, 0.04, P.METAL_BLACK)

def build_glass_office():
    # Manager's glass-walled office at S-W
    ox, oy = -3.5, 1.5
    # Glass partition (south + east faces)
    make_box("Office_PartS", (ox, oy-1.0, 1.40), (2.00, 0.04, 2.20), COL_GLASS)
    make_box("Office_PartE", (ox+1.0, oy, 1.40), (0.04, 2.00, 2.20), COL_GLASS)
    # Door frame in partition
    make_box("Office_DoorFrame", (ox+1.0, oy-0.80, 1.05), (0.04, 0.80, 0.05), P.METAL_BLACK)
    # Manager desk
    make_box("Manager_Desk", (ox, oy, 0.72), (1.40, 0.70, 0.04), COL_DESK)
    make_box("Manager_DeskMod", (ox-0.40, oy, 0.36), (0.40, 0.60, 0.70), COL_DESK)
    # Leather chair (taller)
    make_box("Manager_Chair", (ox, oy-0.70, 0.55), (0.50, 0.50, 0.06), COL_CHAIR)
    make_box("Manager_ChairBack", (ox, oy-0.92, 0.95), (0.50, 0.06, 0.90), COL_CHAIR)
    # Monitor + lamp
    make_box("Manager_Monitor", (ox, oy+0.20, 1.05), (0.60, 0.04, 0.36), COL_MONITOR)
    make_cyl("Manager_Lamp_Base", (ox+0.50, oy+0.20, 0.74), 0.06, 0.02, P.METAL_BLACK)
    make_cyl("Manager_Lamp_Arm",  (ox+0.50, oy+0.20, 0.90), 0.012, 0.30, P.METAL_BLACK)
    make_cyl("Manager_Lamp_Head", (ox+0.50, oy+0.30, 1.05), 0.06, 0.08, P.METAL_BLACK)
    # Pen cup
    make_cyl("Manager_PenCup", (ox-0.45, oy+0.20, 0.80), 0.04, 0.10, P.METAL_STEEL)

def build_decor():
    make_wall_clock("Clock", (0.0, ROOM_D-0.05, 2.30), frozen_hour=2, frozen_min=15)
    make_floor_plant("Plant_NE", (+4.0, ROOM_D-1.0, 0.0))
    make_floor_plant("Plant_NW", (-4.0, ROOM_D-1.0, 0.0))
    # Water cooler
    make_box("WaterCooler_Body", (+4.6, 1.0, 0.55), (0.40, 0.40, 1.10), (0.86, 0.86, 0.84, 1.0))
    make_cyl("WaterCooler_Jug", (+4.6, 1.0, 1.30), 0.18, 0.40, (0.78, 0.86, 0.92, 0.55))
    make_box("WaterCooler_Spout", (+4.6, 0.80, 0.85), (0.10, 0.04, 0.06), P.METAL_BLACK)

def build_ceiling_infra():
    for j, ypos in enumerate([2.0, 4.5, 6.5]):
        for i in range(-1, 2):
            make_fluorescent_tube_fixture(f"Fluor_{j}_{i}", (i*2.4, ypos, CEIL), length=1.40, width=0.32)
    make_smoke_detector("Smoke", (0.0, 3.5, CEIL))
    make_hvac_vent("HVAC", (-2.0, 5.5, CEIL), width=1.00, depth=0.50)
    make_security_camera("Cam", (3.5, 5.5, CEIL))
    make_ceiling_speaker("Speaker", (1.5, 4.0, CEIL))

def main():
    clear_scene(); build_shell(); build_cubicles(); build_glass_office(); build_decor(); build_ceiling_infra()
    out = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "../../../assets/3d/locales/houston_office.glb"))
    print(f"\n[build_houston_office] exporting to {out}")
    export_glb(out)

if __name__ == "__main__": main()
