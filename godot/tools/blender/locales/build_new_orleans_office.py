"""VOL 5 · New Orleans Office — period law/insurance office. Heavy
oak desk, leather chair, wood paneling, banker's-lamp green-glass.
"""
import os, sys
_BT = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
if _BT not in sys.path: sys.path.insert(0, _BT)
from _props import palette as P
from _props.geometry import clear_scene, make_box, make_cyl, export_glb
from _props.structure import make_floor, make_wall, make_ceiling, make_window, make_crown_molding
from _props.decor import make_wall_clock, make_faded_poster, make_floor_plant
from _props.safety import make_fluorescent_tube_fixture, make_smoke_detector

PAL = {"wall": (0.46, 0.32, 0.22, 1.0), "baseboard": (0.22, 0.16, 0.12, 1.0)}
COL_FLOOR = (0.42, 0.30, 0.20, 1.0); COL_SEAM = (0.22, 0.16, 0.12, 1.0)
COL_OAK = (0.46, 0.32, 0.20, 1.0); COL_OAK_DARK = (0.22, 0.14, 0.10, 1.0); COL_BRASS = (0.86, 0.62, 0.28, 1.0)
COL_LEATHER = (0.32, 0.20, 0.14, 1.0); COL_BANKER_GREEN = (0.20, 0.46, 0.22, 1.0)
COL_BOOK = [(0.62, 0.32, 0.30, 1.0), (0.42, 0.30, 0.18, 1.0), (0.30, 0.42, 0.32, 1.0), (0.42, 0.42, 0.18, 1.0)]
ROOM_W = 7.0; ROOM_D = 6.0; CEIL = 3.20

def build_shell():
    make_floor("Floor", (0.0, ROOM_D/2.0, 0.0), size_x=ROOM_W+0.4, size_y=ROOM_D+0.4, palette={"vinyl": COL_FLOOR, "seam": COL_SEAM})
    for nm, x, bb in [("Wall_W", -ROOM_W/2.0, +1), ("Wall_E", +ROOM_W/2.0, -1)]:
        make_wall(nm, (x, ROOM_D/2.0, 0), length=ROOM_D+0.4, height=CEIL, axis='Y', palette=PAL, baseboard_face_sign=bb)
    make_wall("Wall_N", (0.0, ROOM_D, 0), length=ROOM_W+0.4, height=CEIL, axis='X', palette=PAL, baseboard_face_sign=-1)
    make_wall("Wall_S", (0.0, 0.0, 0), length=ROOM_W+0.4, height=CEIL, axis='X', palette=PAL, baseboard_face_sign=+1)
    make_ceiling("Ceil", (0.0, ROOM_D/2.0, CEIL), size_x=ROOM_W+0.4, size_y=ROOM_D+0.4, palette={"tile": (0.62, 0.42, 0.22, 1.0)})
    for nm, ax, length, wx, wy in [("Crown_W",'Y',ROOM_D,-ROOM_W/2.0+0.10,ROOM_D/2.0),("Crown_E",'Y',ROOM_D,+ROOM_W/2.0-0.10,ROOM_D/2.0),("Crown_N",'X',ROOM_W,0.0,ROOM_D-0.10),("Crown_S",'X',ROOM_W,0.0,+0.10)]:
        make_crown_molding(nm, wall_x=wx, wall_y=wy, length=length, axis=ax, ceil_z=CEIL, palette={"wood": COL_OAK_DARK})
    # Tall window E wall (afternoon sun)
    make_box("Window_E_Frame", (ROOM_W/2.0-0.04, 3.0, 1.80), (0.04, 1.80, 2.20), P.METAL_BLACK)
    make_box("Window_E_Glass", (ROOM_W/2.0-0.06, 3.0, 1.80), (0.005, 1.70, 2.00), (0.96, 0.86, 0.62, 0.70))
    # Wainscoting along west wall (vertical wood panels)
    for pi in range(6):
        py = 0.5 + pi*1.0
        make_box(f"Wainscot_W_{pi}", (-ROOM_W/2.0+0.06, py, 0.55), (0.005, 0.96, 1.10), COL_OAK_DARK)

def build_desk_and_chair():
    # Heavy oak desk in centre
    dx, dy = 0.0, 3.5
    make_box("Desk_Top", (dx, dy, 0.76), (2.20, 1.00, 0.06), COL_OAK)
    # Modesty panel front
    make_box("Desk_Front", (dx, dy-0.50, 0.40), (2.20, 0.05, 0.70), COL_OAK_DARK)
    # Side panels (with drawers)
    for sgn in (-1, +1):
        make_box(f"Desk_Side_{sgn:+d}", (dx+sgn*1.05, dy, 0.40), (0.10, 1.00, 0.74), COL_OAK_DARK)
        # 3 drawers
        for di in range(3):
            make_box(f"Desk_Drawer_{sgn:+d}_{di}", (dx+sgn*1.05, dy-0.40, 0.62 - di*0.22), (0.04, 0.50, 0.16), COL_OAK)
            make_cyl(f"Desk_DrawerKnob_{sgn:+d}_{di}", (dx+sgn*1.10, dy-0.40, 0.62 - di*0.22), 0.025, 0.04, COL_BRASS, axis='X')
    # Leather executive chair
    make_box("Chair_Seat", (dx, dy-0.80, 0.50), (0.62, 0.50, 0.10), COL_LEATHER)
    make_box("Chair_Back", (dx, dy-1.02, 1.10), (0.62, 0.06, 1.20), COL_LEATHER)
    make_cyl("Chair_Pillar", (dx, dy-0.80, 0.27), 0.05, 0.46, P.METAL_BLACK)
    make_cyl("Chair_Base", (dx, dy-0.80, 0.04), 0.30, 0.04, P.METAL_BLACK)
    # Banker's lamp
    make_box("Lamp_Shade", (dx-0.60, dy+0.20, 1.02), (0.36, 0.16, 0.14), COL_BANKER_GREEN)
    make_cyl("Lamp_Arm", (dx-0.60, dy+0.20, 0.90), 0.012, 0.20, COL_BRASS)
    make_cyl("Lamp_Base", (dx-0.60, dy+0.20, 0.80), 0.08, 0.04, COL_BRASS)
    # Phone (old corded)
    make_box("Phone_Base", (dx+0.50, dy+0.20, 0.80), (0.20, 0.30, 0.08), COL_LEATHER)
    make_box("Phone_Handset", (dx+0.30, dy+0.10, 0.84), (0.22, 0.05, 0.05), COL_LEATHER)
    # Papers + inkwell
    make_box("Papers", (dx, dy+0.10, 0.80), (0.36, 0.26, 0.02), P.PAPER)
    make_cyl("Inkwell", (dx-0.40, dy+0.10, 0.80), 0.04, 0.06, COL_OAK_DARK)

def build_bookcase_and_filing():
    # Floor-to-near-ceiling bookcase west wall
    for shf in range(6):
        sz = 0.30 + shf*0.45
        make_box(f"BookCase_Shelf_{shf}", (-3.0, 3.0, sz), (0.40, 2.40, 0.04), COL_OAK_DARK)
        for bi in range(10):
            make_box(f"Book_{shf}_{bi}", (-3.0, 1.9 + bi*0.22, sz + 0.18), (0.16, 0.18, 0.36), COL_BOOK[(shf+bi)%len(COL_BOOK)])
    # Filing cabinet north-east
    make_box("Filing_Body", (+3.0, 5.5, 0.65), (0.50, 0.60, 1.30), COL_OAK_DARK)
    for di in range(4):
        make_box(f"Filing_Drawer_{di}", (+3.0, 5.20, 1.20 - di*0.30), (0.46, 0.04, 0.26), COL_OAK)
        make_box(f"Filing_Handle_{di}", (+3.0, 5.18, 1.20 - di*0.30), (0.16, 0.04, 0.02), COL_BRASS)

def build_decor():
    make_wall_clock("Clock", (0.0, ROOM_D-0.05, 2.50), frozen_hour=3, frozen_min=42)
    make_faded_poster("DiplomaW", (-3.45, 4.5, 2.10), palette={"body": P.PAPER_AGED})
    make_faded_poster("DiplomaE", (-3.45, 4.5, 1.55), palette={"body": P.PAPER_AGED})
    make_floor_plant("Plant", (+2.5, 1.0, 0.0))

def build_ceiling_infra():
    # Single overhead pendant (warm)
    make_cyl("Pendant_Cord", (0.0, 3.0, CEIL-0.30), 0.005, 0.60, P.METAL_BLACK)
    make_cyl("Pendant_Shade", (0.0, 3.0, CEIL-0.80), 0.26, 0.20, COL_BANKER_GREEN)
    make_smoke_detector("Smoke", (0.0, 1.5, CEIL))

def main():
    clear_scene(); build_shell(); build_desk_and_chair(); build_bookcase_and_filing(); build_decor(); build_ceiling_infra()
    out = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "../../../assets/3d/locales/new_orleans_office.glb"))
    print(f"\n[build_new_orleans_office] exporting to {out}")
    export_glb(out)

if __name__ == "__main__": main()
