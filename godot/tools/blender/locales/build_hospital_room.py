"""hospital_room — vol5-7 locale (auto-generated placement script)."""
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

ROOM_W = 5.0; ROOM_D = 5.0; CEIL = 2.8
PAL_WALL = {"wall":(0.74,0.74,0.70,1.0),"baseboard":(0.32,0.30,0.28,1.0)}
COL_FLOOR = (0.62,0.58,0.52,1.0); COL_SEAM = (0.32,0.30,0.28,1.0); COL_WOOD = (0.42,0.32,0.22,1.0)
COL_ACCENT = (0.86,0.62,0.28,1.0)

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

BED_X = -0.2; BED_Y = 2.6

def build_bed():
    bx, by = BED_X, BED_Y
    frame=(0.62,0.60,0.58,1.0); mattress=(0.90,0.90,0.86,1.0); board=(0.82,0.82,0.80,1.0)
    make_box("Bed_Frame", (bx, by, 0.36), (0.98, 2.00, 0.16), frame)
    for k,(ox,oy) in enumerate([(-0.44,-0.90),(0.44,-0.90),(-0.44,0.90),(0.44,0.90)]):
        make_box(f"Bed_Leg_{k}", (bx+ox, by+oy, 0.16), (0.06,0.06,0.32), P.METAL_STEEL)
    make_box("Bed_Mattress", (bx, by, 0.52), (0.92, 1.94, 0.16), mattress)
    make_box("Bed_Incline", (bx, by+0.74, 0.58), (0.90, 0.44, 0.14), mattress)
    make_box("Bed_Pillow", (bx, by+0.72, 0.66), (0.66, 0.36, 0.12), (0.96,0.96,0.92,1.0))
    make_box("Bed_Blanket", (bx, by-0.45, 0.60), (0.94, 1.00, 0.08), (0.52,0.70,0.72,1.0))
    make_box("Bed_Headboard", (bx, by+1.02, 0.62), (1.00, 0.06, 0.60), board)
    make_box("Bed_Footboard", (bx, by-1.02, 0.52), (1.00, 0.06, 0.40), board)
    for ri, ox in enumerate((-0.50, 0.50)):
        make_box(f"Bed_Rail_{ri}", (bx+ox, by-0.20, 0.66), (0.03, 0.90, 0.10), P.METAL_STEEL)
        make_cyl(f"Bed_RailPostA_{ri}", (bx+ox, by-0.62, 0.58), 0.015, 0.20, P.METAL_STEEL)
        make_cyl(f"Bed_RailPostB_{ri}", (bx+ox, by+0.22, 0.58), 0.015, 0.20, P.METAL_STEEL)

def build_monitor():
    mx, my = 1.1, 3.5
    make_cyl("Vitals_Base", (mx, my, 0.03), 0.22, 0.05, P.METAL_BLACK, segments=12)
    make_cyl("Vitals_Pole", (mx, my, 0.75), 0.025, 1.44, P.METAL_STEEL)
    make_box("Vitals_Monitor", (mx, my, 1.42), (0.34, 0.28, 0.30), (0.16,0.16,0.18,1.0))
    make_box("Vitals_Screen", (mx-0.18, my, 1.42), (0.02, 0.22, 0.24), (0.06,0.10,0.14,1.0))
    make_box("Vitals_Wave", (mx-0.19, my-0.02, 1.48), (0.005, 0.16, 0.03), (0.32,0.92,0.42,1.0))
    make_box("Vitals_Num1", (mx-0.19, my+0.05, 1.36), (0.005, 0.05, 0.04), (0.32,0.86,0.92,1.0))
    make_box("Vitals_Num2", (mx-0.19, my-0.05, 1.36), (0.005, 0.05, 0.04), (0.96,0.72,0.32,1.0))

def build_iv():
    ix, iy = -1.4, 3.4
    make_cyl("IV_Hub", (ix, iy, 0.05), 0.06, 0.06, P.METAL_STEEL)
    for k,(dx,dy) in enumerate([(0.20,0.0),(0.06,0.19),(-0.16,0.12),(-0.16,-0.12),(0.06,-0.19)]):
        make_box(f"IV_Foot_{k}", (ix+dx*0.6, iy+dy*0.6, 0.02), (0.14,0.04,0.03), P.METAL_STEEL)
    make_cyl("IV_Pole", (ix, iy, 1.05), 0.02, 2.00, P.METAL_STEEL)
    make_box("IV_Hook", (ix, iy-0.08, 1.98), (0.03,0.16,0.03), P.METAL_STEEL)
    make_box("IV_Bag", (ix, iy-0.12, 1.72), (0.10, 0.16, 0.26), (0.86,0.90,0.86,1.0))
    make_cyl("IV_Chamber", (ix, iy-0.12, 1.52), 0.02, 0.10, (0.78,0.86,0.90,1.0))
    make_box("IV_Line", (ix+0.02, iy-0.30, 1.10), (0.008, 0.60, 0.008), (0.84,0.84,0.82,1.0))

def build_curtain():
    rail_z = CEIL-0.20
    make_cyl("Curtain_Rail", (0.0, 1.9, rail_z), 0.02, ROOM_W-0.6, P.METAL_STEEL, axis='X')
    for bi, bx in enumerate((-2.0, 2.0)):
        make_cyl(f"Curtain_Bracket_{bi}", (bx, 1.9, rail_z-0.05), 0.015, 0.10, P.METAL_STEEL)
    make_box("Curtain_Fabric", (1.2, 1.9, rail_z-0.85), (2.0, 0.03, 1.60), (0.60,0.74,0.70,1.0))
    for i in range(6):
        make_box(f"Curtain_Pleat_{i}", (0.3+i*0.34, 1.88, rail_z-0.85), (0.02, 0.02, 1.58), (0.50,0.64,0.60,1.0))

def build_chair():
    cx, cy = -1.7, 1.6
    seat=(0.42,0.52,0.56,1.0)
    make_box("Chair_Seat", (cx, cy, 0.45), (0.44,0.44,0.06), seat)
    make_box("Chair_Back", (cx-0.19, cy, 0.70), (0.05,0.44,0.46), seat)
    for k,(ox,oy) in enumerate([(-0.18,-0.18),(0.18,-0.18),(-0.18,0.18),(0.18,0.18)]):
        make_box(f"Chair_Leg_{k}", (cx+ox, cy+oy, 0.22), (0.05,0.05,0.42), P.METAL_STEEL)
    for ai, oy in enumerate((-0.22,0.22)):
        make_box(f"Chair_Arm_{ai}", (cx, cy+oy, 0.62), (0.42,0.05,0.05), seat)

def build_tray_table():
    tx, ty = 0.7, 2.0
    make_box("Tray_Top", (tx, ty, 0.88), (0.60, 0.42, 0.04), (0.86,0.84,0.80,1.0))
    make_box("Tray_Post", (tx+0.34, ty, 0.45), (0.04,0.04,0.86), P.METAL_STEEL)
    make_box("Tray_Foot", (tx+0.34, ty, 0.03), (0.10,0.44,0.05), P.METAL_STEEL)
    make_cyl("Tray_Cup", (tx-0.10, ty, 0.94), 0.05, 0.10, (0.92,0.90,0.86,1.0))

def build_window():
    make_window("Window", (1.3, ROOM_D-0.06, 1.55), width=1.6, height=1.5)

def build_ceiling_infra():
    for j in range(2):
        ypos = ROOM_D * (0.30 + j * 0.40)
        make_fluorescent_tube_fixture(f"Fluor_{j}", (0.0, ypos, CEIL), length=1.40, width=0.34)
    make_smoke_detector("Smoke", (0.0, ROOM_D/2.0, CEIL))

def main():
    clear_scene()
    build_shell()
    build_bed()
    build_monitor()
    build_iv()
    build_curtain()
    build_chair()
    build_tray_table()
    build_window()
    build_ceiling_infra()
    out = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)),
        "../../../assets/3d/locales/hospital_room.glb"))
    print(f"\n[build_hospital_room] exporting to {out}")
    export_glb(out)

if __name__ == "__main__":
    main()
