"""VOL 5 · New Orleans Room — small hotel / boarding-house room.
Single bed, washbasin, single bulb on cord, peeling wallpaper,
sash window. Spare and worn.
"""
import os, sys
_BT = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
if _BT not in sys.path: sys.path.insert(0, _BT)
from _props import palette as P
from _props.geometry import clear_scene, make_box, make_cyl, export_glb
from _props.structure import make_floor, make_wall, make_ceiling, make_crown_molding
from _props.decor import make_wall_clock, make_faded_poster
from _props.safety import make_smoke_detector

PAL = {"wall": (0.86, 0.78, 0.62, 1.0), "baseboard": (0.42, 0.30, 0.20, 1.0)}
COL_FLOOR = (0.42, 0.30, 0.18, 1.0); COL_SEAM = (0.22, 0.14, 0.10, 1.0)
COL_BED_FRAME = (0.32, 0.28, 0.24, 1.0); COL_LINEN = (0.86, 0.82, 0.74, 1.0)
COL_BASIN = (0.92, 0.92, 0.88, 1.0); COL_FAUCET = (0.62, 0.62, 0.60, 1.0)
COL_BULB = (0.96, 0.86, 0.46, 1.0); COL_WALLPAPER_PEEL = (0.62, 0.46, 0.32, 1.0)
ROOM_W = 4.0; ROOM_D = 5.0; CEIL = 2.80

def build_shell():
    make_floor("Floor", (0.0, ROOM_D/2.0, 0.0), size_x=ROOM_W+0.4, size_y=ROOM_D+0.4, palette={"vinyl": COL_FLOOR, "seam": COL_SEAM})
    for nm, x, bb in [("Wall_W", -ROOM_W/2.0, +1), ("Wall_E", +ROOM_W/2.0, -1)]:
        make_wall(nm, (x, ROOM_D/2.0, 0), length=ROOM_D+0.4, height=CEIL, axis='Y', palette=PAL, baseboard_face_sign=bb)
    make_wall("Wall_N", (0.0, ROOM_D, 0), length=ROOM_W+0.4, height=CEIL, axis='X', palette=PAL, baseboard_face_sign=-1)
    make_wall("Wall_S_W", (-1.5, 0.0, 0), length=1.2, height=CEIL, axis='X', palette=PAL)
    make_wall("Wall_S_E", (+1.5, 0.0, 0), length=1.2, height=CEIL, axis='X', palette=PAL)
    make_ceiling("Ceil", (0.0, ROOM_D/2.0, CEIL), size_x=ROOM_W+0.4, size_y=ROOM_D+0.4)
    for nm, ax, length, wx, wy in [("Crown_W",'Y',ROOM_D,-ROOM_W/2.0+0.10,ROOM_D/2.0),("Crown_E",'Y',ROOM_D,+ROOM_W/2.0-0.10,ROOM_D/2.0),("Crown_N",'X',ROOM_W,0.0,ROOM_D-0.10),("Crown_S",'X',ROOM_W,0.0,+0.10)]:
        make_crown_molding(nm, wall_x=wx, wall_y=wy, length=length, axis=ax, ceil_z=CEIL, palette={"wood": (0.42, 0.30, 0.20, 1.0)})
    # Sash window N wall
    make_box("Window_N_Frame", (0.0, ROOM_D-0.04, 1.60), (1.40, 0.04, 1.40), (0.42, 0.30, 0.20, 1.0))
    make_box("Window_N_Glass", (0.0, ROOM_D-0.06, 1.60), (1.20, 0.005, 1.20), (0.78, 0.84, 0.86, 0.55))
    make_box("Window_N_Mull", (0.0, ROOM_D-0.05, 1.60), (1.20, 0.04, 0.04), (0.42, 0.30, 0.20, 1.0))
    # Peeling wallpaper strips on E wall
    for pi in range(3):
        py = 1.0 + pi*1.5
        make_box(f"Peel_{pi}", (ROOM_W/2.0-0.06, py, 1.50 + (pi%2)*0.20), (0.005, 0.36, 0.50), COL_WALLPAPER_PEEL)

def build_bed():
    bx, by = 0.0, 3.5
    make_box("Bed_Frame_Bot", (bx, by, 0.20), (1.20, 1.80, 0.20), COL_BED_FRAME)
    make_box("Bed_Mattress", (bx, by, 0.40), (1.10, 1.70, 0.16), COL_LINEN)
    make_box("Bed_Pillow", (bx, by+0.62, 0.50), (1.00, 0.36, 0.10), P.PAPER)
    make_box("Bed_Sheet", (bx, by-0.30, 0.50), (1.00, 0.80, 0.04), COL_LINEN)
    # Head/foot board
    make_box("Bed_HeadBoard", (bx, by+0.92, 0.70), (1.20, 0.04, 0.80), COL_BED_FRAME)
    make_box("Bed_FootBoard", (bx, by-0.92, 0.46), (1.20, 0.04, 0.50), COL_BED_FRAME)
    # Nightstand
    make_box("Nightstand", (-1.60, 4.0, 0.40), (0.40, 0.40, 0.80), COL_BED_FRAME)
    # Glass of water on nightstand
    make_cyl("Glass_Water", (-1.60, 4.0, 0.84), 0.04, 0.12, (0.78, 0.84, 0.86, 0.50))

def build_washbasin():
    # Small porcelain washbasin in corner
    wx, wy = +1.60, 4.50
    make_box("Basin_Bracket", (wx, wy, 0.74), (0.04, 0.50, 0.10), COL_FAUCET)
    make_box("Basin_Bowl", (wx-0.20, wy, 0.84), (0.36, 0.46, 0.16), COL_BASIN)
    make_cyl("Basin_Faucet", (wx-0.20, wy, 1.00), 0.012, 0.20, COL_FAUCET)
    make_box("Basin_Spout", (wx-0.30, wy, 1.10), (0.10, 0.04, 0.04), COL_FAUCET)
    make_cyl("Basin_DrainPipe", (wx-0.20, wy, 0.40), 0.025, 0.50, COL_FAUCET)
    # Towel hanging
    make_box("Basin_Towel", (wx-0.30, wy-0.30, 0.60), (0.02, 0.30, 0.40), (0.78, 0.62, 0.42, 1.0))

def build_decor():
    make_wall_clock("Clock", (-1.95, 2.0, 2.10), frozen_hour=11, frozen_min=24)
    make_faded_poster("Poster", (+1.95, 2.0, 1.50))
    # Single chair
    make_box("Chair_Seat", (-1.20, 2.0, 0.46), (0.40, 0.40, 0.04), COL_BED_FRAME)
    make_box("Chair_Back", (-1.20, 2.18, 0.70), (0.40, 0.04, 0.50), COL_BED_FRAME)
    # Suitcase on floor
    make_box("Suitcase", (+1.20, 1.50, 0.10), (0.50, 0.36, 0.20), (0.42, 0.30, 0.18, 1.0))
    # Strap detail
    make_box("Suitcase_Strap", (+1.20, 1.50, 0.22), (0.04, 0.40, 0.005), (0.86, 0.62, 0.28, 1.0))

def build_ceiling_infra():
    # Bare bulb on cord (only light)
    make_cyl("Bulb_Cord", (0.0, 2.5, CEIL-0.30), 0.005, 0.60, P.METAL_BLACK)
    make_cyl("Bulb_Socket", (0.0, 2.5, CEIL-0.66), 0.025, 0.06, (0.62, 0.62, 0.60, 1.0))
    make_cyl("Bulb_Glass", (0.0, 2.5, CEIL-0.80), 0.06, 0.12, COL_BULB)
    make_smoke_detector("Smoke", (+1.0, 1.5, CEIL))

def main():
    clear_scene(); build_shell(); build_bed(); build_washbasin(); build_decor(); build_ceiling_infra()
    out = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "../../../assets/3d/locales/new_orleans_room.glb"))
    print(f"\n[build_new_orleans_room] exporting to {out}")
    export_glb(out)

if __name__ == "__main__": main()
