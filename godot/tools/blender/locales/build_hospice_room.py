"""VOL 5 · Hospice Room — late chapter, end-of-life palliative care.
Adjustable bed, IV stand, monitor, chair for visitor, soft window
light, gentle palette.
"""
import os, sys
_BT = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
if _BT not in sys.path: sys.path.insert(0, _BT)
from _props import palette as P
from _props.geometry import clear_scene, make_box, make_cyl, export_glb
from _props.structure import make_floor, make_wall, make_ceiling, make_crown_molding
from _props.decor import make_wall_clock, make_floor_plant, make_faded_poster
from _props.safety import make_smoke_detector, make_fluorescent_tube_fixture, make_sprinkler

# Warm, home-like palette (hospice reads gentle, not clinical)
PAL = {"wall": (0.90, 0.84, 0.74, 1.0), "baseboard": (0.62, 0.52, 0.40, 1.0)}
COL_FLOOR = (0.66, 0.52, 0.38, 1.0); COL_SEAM = (0.48, 0.36, 0.26, 1.0)
COL_BED_FRAME = (0.68, 0.60, 0.52, 1.0); COL_LINEN = (0.96, 0.94, 0.88, 1.0)
COL_CHAIR = (0.60, 0.40, 0.34, 1.0); COL_MEDICAL = (0.86, 0.86, 0.84, 1.0)
COL_MONITOR_SCREEN = (0.12, 0.42, 0.32, 1.0); COL_IV_BAG = (0.86, 0.92, 0.86, 1.0)
COL_PLANT_LEAF = (0.42, 0.52, 0.36, 1.0)
COL_BLANKET = (0.62, 0.70, 0.58, 1.0); COL_THROW = (0.72, 0.54, 0.42, 1.0)
COL_LAMP_SHADE = (0.96, 0.86, 0.66, 1.0); COL_DRESSER = (0.56, 0.42, 0.28, 1.0)
COL_VASE = (0.42, 0.56, 0.62, 1.0)
COL_FLOWER = [(0.88, 0.46, 0.52, 1.0), (0.92, 0.74, 0.36, 1.0), (0.80, 0.56, 0.78, 1.0)]
ROOM_W = 6.0; ROOM_D = 5.5; CEIL = 2.80

def build_shell():
    make_floor("Floor", (0.0, ROOM_D/2.0, 0.0), size_x=ROOM_W+0.4, size_y=ROOM_D+0.4, palette={"vinyl": COL_FLOOR, "seam": COL_SEAM})
    for nm, x, bb in [("Wall_W", -ROOM_W/2.0, +1), ("Wall_E", +ROOM_W/2.0, -1)]:
        make_wall(nm, (x, ROOM_D/2.0, 0), length=ROOM_D+0.4, height=CEIL, axis='Y', palette=PAL, baseboard_face_sign=bb)
    make_wall("Wall_N", (0.0, ROOM_D, 0), length=ROOM_W+0.4, height=CEIL, axis='X', palette=PAL, baseboard_face_sign=-1)
    make_wall("Wall_S_W", (-2.0, 0.0, 0), length=2.0, height=CEIL, axis='X', palette=PAL)
    make_wall("Wall_S_E", (+2.0, 0.0, 0), length=2.0, height=CEIL, axis='X', palette=PAL)
    make_ceiling("Ceil", (0.0, ROOM_D/2.0, CEIL), size_x=ROOM_W+0.4, size_y=ROOM_D+0.4)
    for nm, ax, length, wx, wy in [("Crown_W",'Y',ROOM_D,-ROOM_W/2.0+0.10,ROOM_D/2.0),("Crown_E",'Y',ROOM_D,+ROOM_W/2.0-0.10,ROOM_D/2.0),("Crown_N",'X',ROOM_W,0.0,ROOM_D-0.10),("Crown_S",'X',ROOM_W,0.0,+0.10)]:
        make_crown_molding(nm, wall_x=wx, wall_y=wy, length=length, axis=ax, ceil_z=CEIL, palette={"wood": (0.62, 0.58, 0.54, 1.0)})
    # Large window N wall (soft natural light)
    make_box("Window_N_Frame", (0.0, ROOM_D-0.04, 1.55), (2.40, 0.04, 1.80), COL_MEDICAL)
    make_box("Window_N_Glass", (0.0, ROOM_D-0.06, 1.55), (2.20, 0.005, 1.60), (0.92, 0.92, 0.86, 0.50))
    # Curtain rails / sheer curtains
    make_box("Window_N_Curtain_L", (-1.40, ROOM_D-0.08, 1.55), (0.30, 0.04, 1.80), COL_LINEN)
    make_box("Window_N_Curtain_R", (+1.40, ROOM_D-0.08, 1.55), (0.30, 0.04, 1.80), COL_LINEN)

def build_hospital_bed():
    bx, by = 0.0, 3.20
    # Adjustable bed — head section raised slightly
    make_box("Bed_Frame", (bx, by, 0.30), (1.20, 2.20, 0.20), COL_BED_FRAME)
    # Mattress base (flat)
    make_box("Bed_Mattress_Lower", (bx, by-0.40, 0.50), (1.10, 1.20, 0.18), COL_LINEN)
    # Mattress upper (raised at head)
    make_box("Bed_Mattress_Upper", (bx, by+0.50, 0.62), (1.10, 1.00, 0.20), COL_LINEN)
    # Pillow
    make_box("Bed_Pillow", (bx, by+0.92, 0.86), (1.00, 0.30, 0.10), P.PAPER)
    # Side rails
    for sgn in (-1, +1):
        make_box(f"Bed_Rail_{sgn:+d}", (bx + sgn*0.62, by, 0.74), (0.04, 1.80, 0.10), COL_MEDICAL)
        # Vertical posts of rail
        for vi in range(4):
            make_cyl(f"Bed_RailPost_{sgn:+d}_{vi}", (bx + sgn*0.62, by - 0.70 + vi*0.50, 0.60), 0.012, 0.30, COL_MEDICAL)
    # Foot panel
    make_box("Bed_Foot", (bx, by-1.10, 0.60), (1.20, 0.04, 0.60), COL_BED_FRAME)
    # Wheels (4)
    for sgn_x in (-1, +1):
        for sgn_y in (-1, +1):
            make_cyl(f"Bed_Wheel_{sgn_x:+d}_{sgn_y:+d}", (bx+sgn_x*0.54, by+sgn_y*1.04, 0.10), 0.08, 0.04, P.METAL_BLACK, axis='X')
    # Bed controls dangling
    make_box("Bed_Controls", (bx+0.70, by-0.20, 0.40), (0.10, 0.06, 0.20), COL_MEDICAL)
    # Soft sage blanket folded over the lower half of the bed
    make_box("Bed_Blanket", (bx, by-0.55, 0.61), (1.14, 1.05, 0.06), COL_BLANKET)
    make_box("Bed_Blanket_Fold", (bx, by-0.02, 0.66), (1.14, 0.22, 0.05), COL_BLANKET)

def build_iv_stand_and_monitor():
    # IV stand beside bed
    ix, iy = +1.0, 4.20
    make_cyl("IV_Pole", (ix, iy, 1.00), 0.012, 2.00, COL_MEDICAL)
    make_cyl("IV_Base", (ix, iy, 0.04), 0.20, 0.04, COL_MEDICAL)
    # IV bag at top
    make_box("IV_Bag", (ix-0.10, iy, 1.70), (0.04, 0.16, 0.30), COL_IV_BAG)
    make_cyl("IV_Hook", (ix-0.10, iy, 1.90), 0.012, 0.04, COL_MEDICAL)
    make_cyl("IV_Tube", (ix-0.10, iy, 1.20), 0.005, 0.80, COL_IV_BAG)
    # Vitals monitor on a cart
    mx, my = -1.0, 4.20
    make_box("Monitor_Cart_Base", (mx, my, 0.05), (0.50, 0.50, 0.10), COL_MEDICAL)
    for wi, (wx, wy) in enumerate([(mx-0.22, my-0.22),(mx+0.22, my-0.22),(mx-0.22, my+0.22),(mx+0.22, my+0.22)]):
        make_cyl(f"Monitor_Wheel_{wi}", (wx, wy, 0.04), 0.04, 0.04, P.METAL_BLACK, axis='X')
    make_cyl("Monitor_Pole", (mx, my, 0.60), 0.04, 1.10, COL_MEDICAL)
    make_box("Monitor_Body", (mx, my, 1.20), (0.40, 0.30, 0.30), COL_MEDICAL)
    make_box("Monitor_Screen", (mx, my-0.16, 1.22), (0.34, 0.005, 0.22), COL_MONITOR_SCREEN)
    # Vitals waveform — abstracted as small lines on the screen
    for li in range(8):
        make_box(f"Monitor_Wave_{li}", (mx - 0.14 + li*0.04, my-0.165, 1.22), (0.02, 0.005, 0.02), (0.62, 0.96, 0.62, 1.0))

def build_visitor_chair_and_decor():
    # Comfortable visitor armchair (upholstered, w/ arms) south of bed
    cx, cy = -1.20, 1.80
    make_box("VisitorChair_Seat", (cx, cy, 0.46), (0.56, 0.56, 0.14), COL_CHAIR)
    make_box("VisitorChair_Back", (cx, cy+0.26, 0.82), (0.56, 0.12, 0.72), COL_CHAIR)
    for sgn in (-1, +1):
        make_box(f"VisitorChair_Arm_{sgn:+d}", (cx+sgn*0.30, cy, 0.62), (0.10, 0.52, 0.18), COL_CHAIR)
    for li, (lx, ly) in enumerate([(cx-0.24,cy-0.24),(cx+0.24,cy-0.24),(cx-0.24,cy+0.24),(cx+0.24,cy+0.24)]):
        make_box(f"VisitorChair_Leg_{li}", (lx, ly, 0.19), (0.05, 0.05, 0.38), (0.40, 0.28, 0.18, 1.0))
    # A knit throw draped over the armrest
    make_box("VisitorChair_Throw", (cx-0.30, cy+0.02, 0.70), (0.16, 0.44, 0.10), COL_THROW)
    # Small bedside table (warm wood top)
    tx, ty = +1.50, 2.50
    make_box("BedTable_Top", (tx, ty, 0.74), (0.52, 0.42, 0.04), COL_DRESSER)
    make_cyl("BedTable_Pole", (tx, ty, 0.37), 0.025, 0.70, COL_MEDICAL)
    make_box("BedTable_Shelf", (tx, ty, 0.40), (0.46, 0.36, 0.03), COL_DRESSER)
    # Glass of water + photo frame on bedside table
    make_cyl("WaterGlass", (tx-0.16, ty, 0.82), 0.04, 0.10, (0.78, 0.84, 0.86, 0.55))
    make_box("PhotoFrame", (tx+0.16, ty-0.06, 0.86), (0.14, 0.02, 0.16), (0.46, 0.34, 0.22, 1.0))
    # Bedside lamp (base + column + warm shade)
    make_cyl("BedLamp_Base", (tx+0.02, ty+0.10, 0.78), 0.07, 0.03, (0.46, 0.34, 0.22, 1.0), segments=10, axis='Z')
    make_cyl("BedLamp_Column", (tx+0.02, ty+0.10, 0.92), 0.015, 0.24, (0.62, 0.52, 0.40, 1.0), segments=8, axis='Z')
    make_cyl("BedLamp_Shade", (tx+0.02, ty+0.10, 1.10), 0.11, 0.14, COL_LAMP_SHADE, segments=12, axis='Z')
    # A vase of flowers on the bedside table
    make_cyl("Vase_Body", (tx-0.02, ty-0.12, 0.82), 0.05, 0.16, COL_VASE, segments=10, axis='Z')
    for fi in range(3):
        a = fi * 2.0
        make_cyl(f"Flower_Stem_{fi}", (tx-0.02, ty-0.12, 0.98), 0.006, 0.14, COL_PLANT_LEAF, segments=4, axis='Z')
        make_cyl(f"Flower_Bloom_{fi}", (tx-0.02 + 0.04*(fi-1), ty-0.12, 1.08 + fi*0.02),
                 0.035, 0.03, COL_FLOWER[fi % len(COL_FLOWER)], segments=8, axis='Z')
    # Small dresser against the W wall
    dxx, dyy = -2.62, 3.40
    make_box("Dresser_Body", (dxx, dyy, 0.44), (0.50, 1.00, 0.88), COL_DRESSER)
    make_box("Dresser_Top", (dxx, dyy, 0.90), (0.54, 1.04, 0.04), (0.46, 0.34, 0.22, 1.0))
    for di in range(3):
        dz = 0.22 + di*0.24
        make_box(f"Dresser_Drawer_{di}", (dxx+0.24, dyy, dz), (0.02, 0.90, 0.20), (0.48, 0.36, 0.24, 1.0))
        make_box(f"Dresser_Pull_{di}", (dxx+0.26, dyy, dz), (0.02, 0.14, 0.03), (0.72, 0.60, 0.34, 1.0))
    # A folded runner cloth + a small framed photo on the dresser top
    make_box("Dresser_Runner", (dxx, dyy, 0.93), (0.44, 0.60, 0.02), COL_BLANKET)
    make_box("Dresser_Photo", (dxx-0.02, dyy+0.28, 1.02), (0.14, 0.02, 0.16), (0.46, 0.34, 0.22, 1.0))
    # Gentle wall crucifix on the W wall above the dresser
    make_box("Cross_Vert", (-2.95, dyy, 1.75), (0.03, 0.06, 0.34), (0.46, 0.34, 0.22, 1.0))
    make_box("Cross_Horiz", (-2.95, dyy, 1.80), (0.03, 0.24, 0.06), (0.46, 0.34, 0.22, 1.0))
    # Plant by window
    make_floor_plant("Plant", (-2.50, ROOM_D-0.50, 0.0), palette={"leaf": COL_PLANT_LEAF})
    make_wall_clock("Clock", (-2.95, 1.5, 2.10), frozen_hour=4, frozen_min=15)
    make_faded_poster("Poster", (+2.95, 2.0, 1.50), palette={"body": (0.80, 0.70, 0.52, 1.0)})

def build_ceiling_infra():
    for j, ypos in enumerate([1.8, 3.8]):
        make_fluorescent_tube_fixture(f"Fluor_{j}", (0.0, ypos, CEIL), length=1.20, width=0.32, palette={"diffuser": (1.0, 0.98, 0.92, 1.0)})
    make_smoke_detector("Smoke", (0.0, 2.5, CEIL))
    make_sprinkler("Spr", (-1.0, 2.5, CEIL))

def main():
    clear_scene(); build_shell(); build_hospital_bed(); build_iv_stand_and_monitor(); build_visitor_chair_and_decor(); build_ceiling_infra()
    out = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "../../../assets/3d/locales/hospice_room.glb"))
    print(f"\n[build_hospice_room] exporting to {out}")
    export_glb(out)

if __name__ == "__main__": main()
