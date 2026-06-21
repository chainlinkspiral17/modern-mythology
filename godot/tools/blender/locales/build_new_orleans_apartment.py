"""VOL 5 · New Orleans Apartment — French-Quarter style. Tall
shuttered windows, ceiling fan, four-poster bed, wrought-iron
balcony view, exposed brick.
"""
import os, sys
_BT = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
if _BT not in sys.path: sys.path.insert(0, _BT)
from _props import palette as P
from _props.geometry import clear_scene, make_box, make_cyl, export_glb
from _props.structure import make_floor, make_wall, make_ceiling, make_crown_molding
from _props.decor import make_wall_clock, make_floor_plant, make_faded_poster
from _props.safety import make_smoke_detector

PAL = {"wall": (0.92, 0.84, 0.66, 1.0), "baseboard": (0.42, 0.28, 0.18, 1.0)}
COL_FLOOR = (0.46, 0.32, 0.20, 1.0); COL_SEAM = (0.22, 0.14, 0.10, 1.0)
COL_BRICK = (0.62, 0.42, 0.34, 1.0); COL_BRICK_SEAM = (0.32, 0.22, 0.18, 1.0)
COL_WROUGHT = (0.16, 0.14, 0.14, 1.0); COL_SHUTTER = (0.42, 0.52, 0.36, 1.0)
COL_BED_WOOD = (0.32, 0.20, 0.14, 1.0); COL_LINEN = (0.92, 0.86, 0.78, 1.0)
ROOM_W = 7.0; ROOM_D = 6.0; CEIL = 3.40

def build_shell():
    make_floor("Floor", (0.0, ROOM_D/2.0, 0.0), size_x=ROOM_W+0.4, size_y=ROOM_D+0.4, palette={"vinyl": COL_FLOOR, "seam": COL_SEAM})
    # East wall is brick
    make_wall("Wall_E", (+ROOM_W/2.0, ROOM_D/2.0, 0), length=ROOM_D+0.4, height=CEIL, axis='Y', palette={"wall": COL_BRICK, "baseboard": COL_BRICK_SEAM}, baseboard_face_sign=-1)
    for r in range(int(CEIL*4)):
        make_box(f"Wall_E_Brick_{r}", (+ROOM_W/2.0-0.04, ROOM_D/2.0, r*0.25+0.12), (0.005, ROOM_D, 0.012), COL_BRICK_SEAM)
    make_wall("Wall_W", (-ROOM_W/2.0, ROOM_D/2.0, 0), length=ROOM_D+0.4, height=CEIL, axis='Y', palette=PAL, baseboard_face_sign=+1)
    make_wall("Wall_N", (0.0, ROOM_D, 0), length=ROOM_W+0.4, height=CEIL, axis='X', palette=PAL, baseboard_face_sign=-1)
    make_wall("Wall_S_W", (-2.5, 0.0, 0), length=2.0, height=CEIL, axis='X', palette=PAL)
    make_wall("Wall_S_E", (+2.5, 0.0, 0), length=2.0, height=CEIL, axis='X', palette=PAL)
    make_ceiling("Ceil", (0.0, ROOM_D/2.0, CEIL), size_x=ROOM_W+0.4, size_y=ROOM_D+0.4, palette={"tile": COL_LINEN})
    for nm, ax, length, wx, wy in [("Crown_W",'Y',ROOM_D,-ROOM_W/2.0+0.10,ROOM_D/2.0),("Crown_E",'Y',ROOM_D,+ROOM_W/2.0-0.10,ROOM_D/2.0),("Crown_N",'X',ROOM_W,0.0,ROOM_D-0.10),("Crown_S",'X',ROOM_W,0.0,+0.10)]:
        make_crown_molding(nm, wall_x=wx, wall_y=wy, length=length, axis=ax, ceil_z=CEIL, palette={"wood": (0.62, 0.42, 0.22, 1.0)})

def build_shuttered_windows():
    # Tall French shutters S wall on either side of door
    for sgn, sx in [(-1, -2.50), (+1, +2.50)]:
        # Window opening with iron balcony rail
        make_box(f"Window_{sgn:+d}_Frame", (sx, 0.0, 1.80), (1.40, 0.04, 2.40), (0.42, 0.32, 0.22, 1.0))
        make_box(f"Window_{sgn:+d}_Glass", (sx, -0.02, 1.80), (1.20, 0.005, 2.20), (0.96, 0.84, 0.62, 0.70))
        # Wrought iron balcony rail (mid-height curls)
        for ri in range(7):
            rx = sx - 0.42 + ri*0.14
            make_cyl(f"Balcony_{sgn:+d}_Bar_{ri}", (rx, -0.08, 0.90), 0.012, 0.60, COL_WROUGHT, axis='Z')
        make_cyl(f"Balcony_{sgn:+d}_Rail", (sx, -0.10, 1.20), 0.020, 1.20, COL_WROUGHT, axis='X')
        # Folded shutters either side
        for shs in (-1, +1):
            make_box(f"Shutter_{sgn:+d}_{shs:+d}", (sx + shs*0.70, 0.02, 1.80), (0.10, 0.04, 2.20), COL_SHUTTER)

def build_bed():
    bx, by = 0.0, 4.80
    # Four-poster bed
    make_box("Bed_Frame", (bx, by, 0.20), (1.80, 2.00, 0.20), COL_BED_WOOD)
    make_box("Bed_Mattress", (bx, by, 0.50), (1.60, 1.80, 0.30), COL_LINEN)
    make_box("Bed_Pillow", (bx, by+0.70, 0.74), (1.40, 0.50, 0.16), P.PAPER)
    # Throw
    make_box("Bed_Throw", (bx, by-0.50, 0.70), (1.40, 0.60, 0.08), (0.62, 0.42, 0.36, 1.0))
    # 4 posts
    for sgn_x in (-1, +1):
        for sgn_y in (-1, +1):
            make_box(f"Bed_Post_{sgn_x:+d}_{sgn_y:+d}", (bx+sgn_x*0.90, by+sgn_y*1.00, 1.10), (0.08, 0.08, 2.00), COL_BED_WOOD)
    # Canopy frame (top rails)
    for sgn_y in (-1, +1):
        make_box(f"Bed_Canopy_X_{sgn_y:+d}", (bx, by+sgn_y*1.00, 2.05), (1.80, 0.06, 0.06), COL_BED_WOOD)
    for sgn_x in (-1, +1):
        make_box(f"Bed_Canopy_Y_{sgn_x:+d}", (bx+sgn_x*0.90, by, 2.05), (0.06, 2.00, 0.06), COL_BED_WOOD)
    # Sheer canopy curtains (drape)
    make_box("Bed_Canopy_Sheer", (bx, by, 1.60), (1.90, 0.04, 0.90), (0.96, 0.92, 0.84, 0.55))

def build_armoire():
    # Wardrobe west wall
    ax, ay = -2.80, 3.0
    make_box("Armoire_Body", (ax, ay, 1.20), (0.50, 1.40, 2.40), COL_BED_WOOD)
    make_box("Armoire_Door_L", (ax+0.21, ay-0.34, 1.20), (0.04, 0.66, 2.30), (0.42, 0.30, 0.20, 1.0))
    make_box("Armoire_Door_R", (ax+0.21, ay+0.34, 1.20), (0.04, 0.66, 2.30), (0.42, 0.30, 0.20, 1.0))
    make_cyl("Armoire_KnobL", (ax+0.24, ay-0.06, 1.20), 0.025, 0.04, (0.86, 0.62, 0.28, 1.0), axis='X')
    make_cyl("Armoire_KnobR", (ax+0.24, ay+0.06, 1.20), 0.025, 0.04, (0.86, 0.62, 0.28, 1.0), axis='X')

def build_decor():
    make_wall_clock("Clock", (-3.45, 2.0, 2.10), frozen_hour=2, frozen_min=14)
    make_faded_poster("PosterW", (-3.45, 1.0, 1.50))
    make_floor_plant("Plant_S", (+2.50, 1.50, 0.0))
    # Ceiling fan
    cx, cy = 0.0, 3.0
    make_cyl("Fan_Stem", (cx, cy, CEIL-0.20), 0.04, 0.30, (0.42, 0.30, 0.20, 1.0))
    make_cyl("Fan_Hub", (cx, cy, CEIL-0.42), 0.18, 0.10, (0.42, 0.30, 0.20, 1.0))
    for bi in range(4):
        import math
        ang = bi * 1.57
        bx_off = math.cos(ang) * 0.50
        by_off = math.sin(ang) * 0.50
        make_box(f"Fan_Blade_{bi}", (cx + bx_off, cy + by_off, CEIL-0.42), (0.80 if bi%2==0 else 0.10, 0.10 if bi%2==0 else 0.80, 0.02), (0.42, 0.30, 0.20, 1.0))

def build_ceiling_infra():
    make_smoke_detector("Smoke", (+1.5, 3.5, CEIL))

def main():
    clear_scene(); build_shell(); build_shuttered_windows(); build_bed(); build_armoire(); build_decor(); build_ceiling_infra()
    out = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "../../../assets/3d/locales/new_orleans_apartment.glb"))
    print(f"\n[build_new_orleans_apartment] exporting to {out}")
    export_glb(out)

if __name__ == "__main__": main()
