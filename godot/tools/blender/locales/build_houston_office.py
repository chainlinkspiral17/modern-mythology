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
COL_SCREEN = (0.20, 0.34, 0.46, 1.0); COL_ACCENT_WARM = (0.72, 0.30, 0.22, 1.0)
COL_BOOKCASE = (0.40, 0.30, 0.20, 1.0); COL_CREDENZA = (0.36, 0.27, 0.18, 1.0)
COL_BOOK_TINTS = [(0.62,0.26,0.22,1.0),(0.24,0.34,0.46,1.0),(0.30,0.42,0.30,1.0),
                  (0.52,0.44,0.24,1.0),(0.44,0.30,0.42,1.0),(0.30,0.30,0.34,1.0)]
COL_BLIND = (0.86, 0.84, 0.78, 1.0)
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
    # Large mullioned window N wall, looking at downtown
    make_window("Window_N", (0.0, ROOM_D, 1.65), width=5.0, height=2.0,
                palette={"glass": COL_GLASS})

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
        # Monitor (bezel + inset glowing screen face + stand)
        make_box(f"Cub_{ci}_Monitor", (cx, cy+0.20, 1.00), (0.50, 0.04, 0.30), COL_MONITOR)
        make_box(f"Cub_{ci}_MonScreen", (cx, cy+0.178, 1.00), (0.44, 0.005, 0.24), COL_SCREEN)
        make_box(f"Cub_{ci}_MonStand", (cx, cy+0.20, 0.80), (0.10, 0.10, 0.16), P.METAL_BLACK)
        make_box(f"Cub_{ci}_MonFoot", (cx, cy+0.20, 0.73), (0.24, 0.18, 0.02), P.METAL_BLACK)
        # Keyboard + a mug + a small paper tray on the desk
        make_box(f"Cub_{ci}_KB", (cx, cy-0.12, 0.75), (0.44, 0.15, 0.02), (0.28, 0.28, 0.30, 1.0))
        make_cyl(f"Cub_{ci}_Mug", (cx+0.55, cy-0.05, 0.79), 0.04, 0.10, COL_ACCENT_WARM)
        make_box(f"Cub_{ci}_Papers", (cx-0.55, cy+0.05, 0.745), (0.24, 0.30, 0.02), P.PAPER)
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
    make_box("Manager_MonScreen", (ox, oy+0.178, 1.05), (0.54, 0.005, 0.30), COL_SCREEN)
    make_box("Manager_MonFoot", (ox, oy+0.20, 0.75), (0.30, 0.20, 0.02), P.METAL_BLACK)
    # Desk phone (base + handset)
    make_box("Manager_Phone_Base", (ox+0.42, oy-0.05, 0.76), (0.20, 0.24, 0.06), P.METAL_BLACK)
    make_box("Manager_Phone_Handset", (ox+0.42, oy-0.14, 0.80), (0.22, 0.06, 0.05), (0.12,0.12,0.14,1.0))
    # Papers / blotter
    make_box("Manager_Blotter", (ox-0.10, oy-0.05, 0.745), (0.60, 0.40, 0.01), (0.30,0.28,0.30,1.0))
    make_box("Manager_Papers", (ox-0.10, oy-0.05, 0.755), (0.26, 0.34, 0.02), P.PAPER)
    make_cyl("Manager_Lamp_Base", (ox+0.50, oy+0.20, 0.74), 0.06, 0.02, P.METAL_BLACK)
    make_cyl("Manager_Lamp_Arm",  (ox+0.50, oy+0.20, 0.90), 0.012, 0.30, P.METAL_BLACK)
    make_cyl("Manager_Lamp_Head", (ox+0.50, oy+0.30, 1.05), 0.06, 0.08, P.METAL_BLACK)
    # Pen cup
    make_cyl("Manager_PenCup", (ox-0.45, oy+0.20, 0.80), 0.04, 0.10, P.METAL_STEEL)

def build_exec_furniture():
    """Executive furnishings around the manager's glass office (SW):
    a bookcase w/ books, two filing cabinets w/ pulls, a low credenza,
    two guest chairs facing the desk, a framed diploma."""
    # Bookcase against the W wall in the manager office
    bcx, bcy = -4.72, 2.4
    make_box("Bookcase_Body", (bcx, bcy, 1.05), (0.36, 1.60, 2.10), COL_BOOKCASE)
    make_box("Bookcase_Back", (bcx-0.16, bcy, 1.05), (0.04, 1.56, 2.06), COL_TRIM)
    for si, sz in enumerate([0.40, 0.90, 1.40, 1.90]):
        make_box(f"Bookcase_Shelf_{si}", (bcx, bcy, sz), (0.32, 1.56, 0.03), COL_TRIM)
        # Row of spine-out books per shelf
        for bi in range(9):
            by = bcy - 0.68 + bi*0.155
            h = 0.28 + (bi % 3)*0.04
            make_box(f"Bookcase_Book_{si}_{bi}", (bcx+0.02, by, sz+0.02+h/2.0),
                     (0.24, 0.13, h), COL_BOOK_TINTS[(si*3+bi) % len(COL_BOOK_TINTS)])
    # Two filing cabinets, SW corner along W wall
    for fi, fy in enumerate([0.55, 1.20]):
        fx = -4.66
        make_box(f"Filing_{fi}_Body", (fx, fy, 0.66), (0.46, 0.56, 1.32), P.METAL_STEEL)
        for di in range(3):
            dz = 0.28 + di*0.42
            make_box(f"Filing_{fi}_Drawer_{di}", (fx+0.22, fy, dz), (0.02, 0.50, 0.36), (0.56,0.58,0.60,1.0))
            make_box(f"Filing_{fi}_Pull_{di}", (fx+0.24, fy, dz), (0.02, 0.18, 0.03), P.METAL_BLACK)
    # Low credenza against the S wall behind the desk
    crx, cry = -3.5, 0.35
    make_box("Credenza_Body", (crx, cry, 0.42), (2.00, 0.44, 0.84), COL_CREDENZA)
    make_box("Credenza_Top", (crx, cry, 0.86), (2.08, 0.50, 0.04), COL_DESK)
    for pi, px in enumerate([-0.55, +0.05, +0.65]):
        make_box(f"Credenza_Door_{pi}", (crx+px, cry-0.22, 0.42), (0.56, 0.02, 0.72), COL_CREDENZA)
        make_box(f"Credenza_Pull_{pi}", (crx+px+0.22, cry-0.24, 0.42), (0.03, 0.02, 0.14), P.METAL_BLACK)
    # A framed photo + a small trophy on the credenza top
    make_box("Credenza_Photo", (crx-0.60, cry+0.05, 0.98), (0.24, 0.04, 0.20), COL_TRIM)
    make_cyl("Credenza_Trophy_Cup", (crx+0.55, cry, 1.00), 0.06, 0.10, P.METAL_STEEL)
    make_box("Credenza_Trophy_Base", (crx+0.55, cry, 0.905), (0.10, 0.10, 0.05), COL_TRIM)
    # Two guest chairs facing the manager desk (north side)
    for gi, gx in enumerate([-3.95, -3.05]):
        gy = 2.55
        make_box(f"Guest_{gi}_Seat", (gx, gy, 0.46), (0.44, 0.44, 0.06), COL_CHAIR)
        make_box(f"Guest_{gi}_Back", (gx, gy+0.20, 0.78), (0.44, 0.05, 0.56), COL_CHAIR)
        for li,(lx,ly) in enumerate([(gx-0.18,gy-0.18),(gx+0.18,gy-0.18),(gx-0.18,gy+0.18),(gx+0.18,gy+0.18)]):
            make_box(f"Guest_{gi}_Leg_{li}", (lx, ly, 0.23), (0.03, 0.03, 0.46), P.METAL_BLACK)
    # Framed diploma on the W wall of the manager office
    make_box("Diploma_Frame", (-4.95, 1.5, 1.90), (0.03, 0.44, 0.34), COL_TRIM)
    make_box("Diploma_Mat", (-4.94, 1.5, 1.90), (0.02, 0.36, 0.26), P.PAPER)

def build_window_blinds():
    # Horizontal venetian blinds over the N window (partly open)
    for bi in range(14):
        bz = 0.65 + bi*0.11
        make_box(f"Blind_Slat_{bi}", (0.0, ROOM_D-0.10, bz), (4.90, 0.02, 0.03), COL_BLIND)
    make_box("Blind_Header", (0.0, ROOM_D-0.11, 2.78), (5.0, 0.08, 0.08), COL_TRIM)
    make_cyl("Blind_Cord", (2.30, ROOM_D-0.12, 1.80), 0.006, 1.90, COL_TRIM)

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
    clear_scene(); build_shell(); build_cubicles(); build_glass_office(); build_exec_furniture(); build_window_blinds(); build_decor(); build_ceiling_infra()
    out = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "../../../assets/3d/locales/houston_office.glb"))
    print(f"\n[build_houston_office] exporting to {out}")
    export_glb(out)

if __name__ == "__main__": main()
