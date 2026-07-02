"""VOL 5 · New Orleans Bar — cameo. Long mahogany bar, brass rail,
bottle wall, pendant lamps, jukebox in corner.
"""
import os, sys
_BT = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
if _BT not in sys.path: sys.path.insert(0, _BT)
from _props import palette as P
from _props.geometry import clear_scene, make_box, make_cyl, export_glb
from _props.structure import make_floor, make_wall, make_ceiling, make_crown_molding, make_window
from _props.store_fixtures import make_counter, make_counter_bullnose
from _props.decor import make_wall_clock
from _props.safety import make_fluorescent_tube_fixture, make_smoke_detector, make_ceiling_speaker

PAL = {"wall": (0.42, 0.30, 0.22, 1.0), "baseboard": (0.18, 0.12, 0.10, 1.0)}
COL_FLOOR = (0.32, 0.22, 0.16, 1.0); COL_SEAM = (0.18, 0.12, 0.10, 1.0)
COL_BAR = (0.42, 0.28, 0.18, 1.0); COL_TOP = (0.22, 0.14, 0.10, 1.0); COL_BRASS = (0.86, 0.62, 0.28, 1.0)
COL_BOTTLE_AMBER = (0.78, 0.42, 0.16, 1.0); COL_BOTTLE_CLEAR = (0.78, 0.84, 0.86, 0.55); COL_BOTTLE_GREEN = (0.32, 0.42, 0.20, 1.0)
ROOM_W = 9.0; ROOM_D = 6.0; CEIL = 3.20

def build_shell():
    make_floor("Floor", (0.0, ROOM_D/2.0, 0.0), size_x=ROOM_W+0.4, size_y=ROOM_D+0.4, palette={"vinyl": COL_FLOOR, "seam": COL_SEAM})
    for nm, x, bb in [("Wall_W", -ROOM_W/2.0, +1), ("Wall_E", +ROOM_W/2.0, -1)]:
        make_wall(nm, (x, ROOM_D/2.0, 0), length=ROOM_D+0.4, height=CEIL, axis='Y', palette=PAL, baseboard_face_sign=bb)
    make_wall("Wall_N", (0.0, ROOM_D, 0), length=ROOM_W+0.4, height=CEIL, axis='X', palette=PAL, baseboard_face_sign=-1)
    make_wall("Wall_S_W", (-3.0, 0.0, 0), length=2.4, height=CEIL, axis='X', palette=PAL)
    make_wall("Wall_S_E", (+3.0, 0.0, 0), length=2.4, height=CEIL, axis='X', palette=PAL)
    make_ceiling("Ceil", (0.0, ROOM_D/2.0, CEIL), size_x=ROOM_W+0.4, size_y=ROOM_D+0.4, palette={"tile": (0.30, 0.22, 0.14, 1.0), "grid": (0.18, 0.12, 0.10, 1.0)})
    for nm, ax, length, wx, wy in [("Crown_W",'Y',ROOM_D,-ROOM_W/2.0+0.10,ROOM_D/2.0),("Crown_E",'Y',ROOM_D,+ROOM_W/2.0-0.10,ROOM_D/2.0),("Crown_N",'X',ROOM_W,0.0,ROOM_D-0.10),("Crown_S",'X',ROOM_W,0.0,+0.10)]:
        make_crown_molding(nm, wall_x=wx, wall_y=wy, length=length, axis=ax, ceil_z=CEIL, palette={"wood": COL_BRASS})
    make_window("Window_SW", (-2.0, 0.0, 1.60), width=1.40, height=1.20)
    make_window("Window_SE", (+2.0, 0.0, 1.60), width=1.40, height=1.20)

def build_bar():
    top_z = make_counter("Bar", (0.0, 4.5, 0.0), length=7.0, depth=1.20, height=1.10, palette={"formica": COL_BAR, "top": COL_TOP, "kick": (0.18, 0.10, 0.06, 1.0)})
    make_counter_bullnose("Bar", (-0.60, 4.5, top_z), length=7.0, palette={"top": COL_TOP})
    # Brass foot rail (cylinder along south face)
    make_cyl("Bar_FootRail", (-0.62, 4.5, 0.18), 0.025, 7.0, COL_BRASS, axis='Y', segments=8)
    # 5 bar stools (south side)
    for si, sx in enumerate([-2.4, -1.2, 0.0, +1.2, +2.4]):
        make_cyl(f"Stool_{si}_Seat", (sx, 3.20, 0.78), 0.18, 0.06, COL_BAR)
        make_cyl(f"Stool_{si}_Pillar", (sx, 3.20, 0.40), 0.04, 0.74, COL_BRASS)
        make_cyl(f"Stool_{si}_Foot", (sx, 3.20, 0.04), 0.16, 0.04, COL_BRASS)
    # Bottle wall north of bar (mounted shelves)
    for shf in range(3):
        sz = top_z + 0.30 + shf*0.40
        make_box(f"Bottle_Shelf_{shf}", (0.0, 5.40, sz), (6.4, 0.20, 0.02), COL_TOP)
        for bi in range(20):
            bx = -3.0 + bi*0.32
            tint = [COL_BOTTLE_AMBER, COL_BOTTLE_CLEAR, COL_BOTTLE_GREEN][(shf+bi)%3]
            make_cyl(f"Bottle_{shf}_{bi}", (bx, 5.40, sz+0.16), 0.05, 0.30, tint)
    # Back mirror (long horizontal — bartender's reflection canon)
    make_box("Bar_Mirror", (0.0, 5.92, top_z+0.85), (6.4, 0.02, 1.50), (0.78, 0.84, 0.86, 0.85))

def build_jukebox():
    # Wurlitzer-style jukebox SE corner
    jx, jy = +3.80, 1.20
    make_box("Jukebox_Body", (jx, jy, 0.75), (0.80, 0.60, 1.50), (0.78, 0.42, 0.16, 1.0))
    make_box("Jukebox_TopArch", (jx, jy, 1.70), (0.80, 0.60, 0.40), (0.62, 0.32, 0.14, 1.0))
    make_box("Jukebox_Glass", (jx, jy-0.31, 1.10), (0.70, 0.04, 0.50), (0.32, 0.22, 0.18, 0.55))
    make_box("Jukebox_LightBar", (jx, jy-0.32, 1.50), (0.70, 0.02, 0.10), (0.96, 0.78, 0.42, 1.0))

def build_decor():
    make_wall_clock("Clock", (0.0, ROOM_D-0.05, 2.60), frozen_hour=11, frozen_min=47)
    # Pendant lamps over bar
    for pi, px in enumerate([-2.0, 0.0, +2.0]):
        make_cyl(f"Pendant_{pi}_Cord", (px, 4.5, CEIL-0.30), 0.005, 0.40, P.METAL_BLACK)
        make_box(f"Pendant_{pi}_Shade", (px, 4.5, CEIL-0.70), (0.30, 0.30, 0.30), (0.92, 0.74, 0.32, 1.0))

def build_ceiling_infra():
    for j, ypos in enumerate([2.0, 3.5]):
        make_fluorescent_tube_fixture(f"Fluor_{j}", (0.0, ypos, CEIL), length=1.20, width=0.30, palette={"tube": (0.62, 0.38, 0.18, 1.0)})
    make_smoke_detector("Smoke", (-2.0, 3.0, CEIL))
    make_ceiling_speaker("Speaker", (+2.0, 3.0, CEIL))

def main():
    clear_scene(); build_shell(); build_bar(); build_jukebox(); build_decor(); build_ceiling_infra()
    out = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "../../../assets/3d/locales/new_orleans_bar.glb"))
    print(f"\n[build_new_orleans_bar] exporting to {out}")
    export_glb(out)

if __name__ == "__main__": main()
