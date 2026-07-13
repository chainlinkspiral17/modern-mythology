"""VOL 5 · Montreal Apartment — winter scene cameo.
Small Mile-End apartment: radiator under window, hardwood floors,
heavy curtains, French-press on the counter, books everywhere.
"""
import os, sys
_BT = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
if _BT not in sys.path: sys.path.insert(0, _BT)
from _props import palette as P
from _props.geometry import clear_scene, make_box, make_cyl, export_glb
from _props.structure import make_floor, make_wall, make_ceiling, make_window, make_crown_molding
from _props.store_fixtures import make_counter, make_counter_bullnose
from _props.decor import make_wall_clock, make_faded_poster, make_floor_plant
from _props.safety import make_smoke_detector, make_fluorescent_tube_fixture

PAL = {"wall": (0.92, 0.88, 0.78, 1.0), "baseboard": (0.42, 0.32, 0.22, 1.0)}
COL_FLOOR = (0.62, 0.46, 0.30, 1.0); COL_SEAM = (0.32, 0.22, 0.14, 1.0)
COL_WOOD = (0.42, 0.30, 0.18, 1.0); COL_CURTAIN = (0.52, 0.32, 0.32, 1.0)
COL_RADIATOR = (0.86, 0.80, 0.72, 1.0); COL_BOOK_SPINES = [(0.62, 0.32, 0.30, 1.0), (0.42, 0.52, 0.62, 1.0), (0.56, 0.48, 0.32, 1.0), (0.32, 0.42, 0.32, 1.0)]
ROOM_W = 6.0; ROOM_D = 5.0; CEIL = 2.80

def build_shell():
    make_floor("Floor", (0.0, ROOM_D/2.0, 0.0), size_x=ROOM_W+0.4, size_y=ROOM_D+0.4, palette={"vinyl": COL_FLOOR, "seam": COL_SEAM})
    for nm, x, ax, bb in [("Wall_W", -ROOM_W/2.0, 'Y', +1), ("Wall_E", +ROOM_W/2.0, 'Y', -1)]:
        make_wall(nm, (x, ROOM_D/2.0, 0), length=ROOM_D+0.4, height=CEIL, axis=ax, palette=PAL, baseboard_face_sign=bb)
    make_wall("Wall_N", (0.0, ROOM_D, 0), length=ROOM_W+0.4, height=CEIL, axis='X', palette=PAL, baseboard_face_sign=-1)
    make_wall("Wall_S_W", (-2.0, 0.0, 0), length=2.0, height=CEIL, axis='X', palette=PAL)
    make_wall("Wall_S_E", (+2.0, 0.0, 0), length=2.0, height=CEIL, axis='X', palette=PAL)
    make_box("Wall_S_AboveDoor", (0.0, 0.0, CEIL-0.30), (2.0, 0.20, 0.60), PAL["wall"])
    make_ceiling("Ceil", (0.0, ROOM_D/2.0, CEIL), size_x=ROOM_W+0.4, size_y=ROOM_D+0.4)
    for nm, ax, length, wx, wy in [("Crown_W",'Y',ROOM_D,-ROOM_W/2.0+0.10,ROOM_D/2.0),("Crown_E",'Y',ROOM_D,+ROOM_W/2.0-0.10,ROOM_D/2.0),("Crown_N",'X',ROOM_W,0.0,ROOM_D-0.10),("Crown_S",'X',ROOM_W,0.0,+0.10)]:
        make_crown_molding(nm, wall_x=wx, wall_y=wy, length=length, axis=ax, ceil_z=CEIL, palette={"wood": COL_WOOD})
    # Tall north window with snow-light through
    make_box("Window_N_Frame", (0.0, ROOM_D-0.04, 1.60), (2.20, 0.04, 2.00), P.METAL_STEEL)
    make_box("Window_N_Glass", (0.0, ROOM_D-0.06, 1.60), (2.00, 0.005, 1.80), (0.78, 0.84, 0.92, 0.65))
    # Heavy curtains either side
    for cs in (-1, +1):
        make_box(f"Curtain_{cs:+d}", (cs*1.30, ROOM_D-0.08, 1.60), (0.20, 0.06, 2.00), COL_CURTAIN)

COL_SOFA = (0.46, 0.36, 0.42, 1.0); COL_CHAIR = (0.42, 0.44, 0.40, 1.0)
COL_RUG = (0.52, 0.28, 0.26, 1.0); COL_THROW = (0.72, 0.58, 0.34, 1.0)

def build_living():
    # Living area rug
    make_box("Rug", (-0.70, 1.90, 0.015), (2.5, 2.3, 0.02), COL_RUG)
    make_box("Rug_Border", (-0.70, 1.90, 0.018), (2.3, 2.1, 0.008), (0.64, 0.40, 0.34, 1.0))
    # Sofa facing north toward the snow-lit window (base + back + arms +
    # cushions + legs + a tossed winter throw).
    sx, sy = -0.70, 1.15
    make_box("Sofa_Base", (sx, sy, 0.30), (1.70, 0.85, 0.18), COL_SOFA)
    make_box("Sofa_Back", (sx, sy-0.42, 0.62), (1.70, 0.18, 0.52), COL_SOFA)
    for ax in (-0.85, 0.85):
        make_box(f"Sofa_Arm_{'L' if ax<0 else 'R'}", (sx+ax, sy, 0.44), (0.18, 0.85, 0.34), COL_SOFA)
    for ci in range(3):
        make_box(f"Sofa_SeatCushion_{ci}", (sx-0.55+ci*0.55, sy+0.06, 0.42), (0.50, 0.70, 0.14), (0.52, 0.42, 0.48, 1.0))
        make_box(f"Sofa_BackCushion_{ci}", (sx-0.55+ci*0.55, sy-0.34, 0.66), (0.48, 0.14, 0.40), (0.52, 0.42, 0.48, 1.0))
    for i, (lx, ly) in enumerate([(-0.78,-0.38),(0.78,-0.38),(-0.78,0.38),(0.78,0.38)]):
        make_box(f"Sofa_Leg_{i}", (sx+lx, sy+ly, 0.12), (0.06, 0.06, 0.24), COL_WOOD)
    make_box("Sofa_Throw", (sx+0.5, sy+0.10, 0.50), (0.60, 0.66, 0.10), COL_THROW)
    # Coffee table north of the sofa, on the rug
    tx, ty = -0.70, 2.45
    make_box("Coffee_Top", (tx, ty, 0.42), (1.10, 0.60, 0.05), COL_WOOD)
    for i, (lx, ly) in enumerate([(-0.50,-0.24),(0.50,-0.24),(-0.50,0.24),(0.50,0.24)]):
        make_box(f"Coffee_Leg_{i}", (tx+lx, ty+ly, 0.21), (0.05, 0.05, 0.42), COL_WOOD)
    make_box("Coffee_Books", (tx-0.28, ty, 0.48), (0.30, 0.24, 0.06), COL_BOOK_SPINES[1])
    make_cyl("Coffee_Mug", (tx+0.28, ty+0.08, 0.49), 0.05, 0.10, (0.62, 0.32, 0.30, 1.0), segments=10)
    # Armchair to the west, angled toward the coffee table
    ax, ay = -2.30, 2.30
    make_box("Chair_Base", (ax, ay, 0.32), (0.72, 0.76, 0.16), COL_CHAIR)
    make_box("Chair_Back", (ax-0.30, ay, 0.66), (0.16, 0.76, 0.52), COL_CHAIR)
    for arm in (-0.42, 0.42):
        make_box(f"ArmC_Arm_{'S' if arm<0 else 'N'}", (ax, ay+arm, 0.46), (0.72, 0.14, 0.30), COL_CHAIR)
    make_box("Chair_Cushion", (ax, ay, 0.44), (0.56, 0.62, 0.14), (0.50, 0.52, 0.48, 1.0))
    make_box("Chair_Throw", (ax-0.10, ay+0.30, 0.52), (0.40, 0.24, 0.08), COL_THROW)
    for i, (lx, ly) in enumerate([(-0.30,-0.32),(0.30,-0.32),(-0.30,0.32),(0.30,0.32)]):
        make_box(f"ArmC_Leg_{i}", (ax+lx, ay+ly, 0.12), (0.06, 0.06, 0.24), COL_WOOD)
    # Bookshelf east wall — overflowing
    sx2 = +2.50
    for shf in range(6):
        sz = 0.20 + shf*0.40
        make_box(f"BookShelf_{shf}", (sx2, 2.5, sz), (0.40, 1.40, 0.02), COL_WOOD)
        for bi in range(7):
            bx = sx2; by = 2.5 - 0.50 + bi*0.16
            spine = COL_BOOK_SPINES[(shf*3+bi)%len(COL_BOOK_SPINES)]
            make_box(f"Book_{shf}_{bi}", (bx, by, sz+0.16), (0.10, 0.12, 0.30), spine)
    make_box("BookShelf_Side_S", (sx2+0.02, 1.78, 1.40), (0.44, 0.04, 2.40), COL_WOOD)
    make_box("BookShelf_Side_N", (sx2+0.02, 3.22, 1.40), (0.44, 0.04, 2.40), COL_WOOD)

def build_dining_nook():
    # Small bistro dining nook east-centre, between bookshelf & kitchen.
    tx, ty = 1.35, 3.55
    make_cyl("Dine_Pedestal", (tx, ty, 0.36), 0.06, 0.72, COL_WOOD, segments=8)
    make_cyl("Dine_Foot", (tx, ty, 0.03), 0.28, 0.05, (0.32, 0.22, 0.14, 1.0), segments=12)
    make_cyl("Dine_Top", (tx, ty, 0.74), 0.42, 0.05, COL_WOOD, segments=16)
    make_cyl("Dine_Plate", (tx-0.14, ty, 0.78), 0.10, 0.02, (0.86, 0.84, 0.80, 1.0), segments=12)
    make_cyl("Dine_Mug", (tx+0.16, ty+0.10, 0.80), 0.045, 0.09, (0.42, 0.52, 0.62, 1.0), segments=10)
    for ci, (cx3, cy3) in enumerate([(tx-0.62, ty), (tx+0.62, ty)]):
        make_box(f"Dine_Chair_{ci}_Seat", (cx3, cy3, 0.46), (0.40, 0.40, 0.05), COL_WOOD)
        bxo = -0.18 if cx3 < tx else 0.18
        make_box(f"Dine_Chair_{ci}_Back", (cx3+bxo, cy3, 0.72), (0.04, 0.40, 0.46), COL_WOOD)
        for i, (lx, ly) in enumerate([(-0.16,-0.16),(0.16,-0.16),(-0.16,0.16),(0.16,0.16)]):
            make_box(f"Dine_Chair_{ci}_Leg_{i}", (cx3+lx, cy3+ly, 0.22), (0.04, 0.04, 0.44), COL_WOOD)

def build_floor_lamp():
    # Arc floor lamp in the SW corner beside the sofa.
    lx, ly = -2.72, 0.85
    make_cyl("FloorLamp_Base", (lx, ly, 0.03), 0.16, 0.06, P.METAL_BLACK, segments=12)
    make_cyl("FloorLamp_Pole", (lx, ly, 0.95), 0.02, 1.80, P.METAL_STEEL, segments=8)
    make_cyl("FloorLamp_Shade", (lx, ly, 1.80), 0.16, 0.22, (0.94, 0.86, 0.62, 1.0), segments=12)

def build_kitchenette():
    # Tiny corner kitchen N-E
    cx, cy = +2.5, 4.5
    top_z = make_counter("Kitch", (cx, cy, 0.0), length=1.20, depth=0.70, height=0.92, palette={"formica": (0.74, 0.62, 0.42, 1.0), "top": (0.32, 0.22, 0.14, 1.0), "kick": (0.32, 0.22, 0.14, 1.0)})
    make_counter_bullnose("Kitch", (cx-0.35, cy, top_z), length=1.20, palette={"top": (0.32, 0.22, 0.14, 1.0)})
    # French press
    make_cyl("FrenchPress_Body", (cx-0.20, cy, top_z+0.12), 0.06, 0.20, (0.78, 0.84, 0.86, 0.55))
    make_cyl("FrenchPress_Plunger", (cx-0.20, cy, top_z+0.26), 0.012, 0.10, P.METAL_STEEL)
    make_cyl("FrenchPress_Lid", (cx-0.20, cy, top_z+0.30), 0.06, 0.02, P.METAL_BLACK)
    # Coffee in press
    make_cyl("FrenchPress_Coffee", (cx-0.20, cy, top_z+0.08), 0.05, 0.10, (0.18, 0.10, 0.06, 1.0))
    # Mug
    make_cyl("Mug", (cx+0.20, cy, top_z+0.06), 0.05, 0.10, (0.62, 0.32, 0.30, 1.0))

def build_radiator_under_window():
    # Cast-iron radiator under the N window
    rx, ry = 0.0, ROOM_D-0.20
    for fi in range(6):
        make_box(f"Radiator_Fin_{fi}", (rx-0.55+fi*0.22, ry, 0.40), (0.06, 0.16, 0.80), COL_RADIATOR)
    make_box("Radiator_Top", (rx, ry, 0.82), (1.40, 0.20, 0.04), COL_RADIATOR)
    make_box("Radiator_Pipe", (rx-0.70, ry+0.06, 0.30), (0.04, 0.06, 0.60), COL_RADIATOR)

def build_decor():
    make_wall_clock("Clock", (-2.95, 2.5, 2.10), frozen_hour=10, frozen_min=33)
    make_faded_poster("Poster", (+2.95, 0.8, 1.60))
    make_faded_poster("Art_W", (-2.95, 1.1, 1.65), palette={"body": (0.52, 0.56, 0.60, 1.0)})
    make_floor_plant("Plant", (-2.0, 4.0, 0.0))
    # Stack of books on floor
    for bi in range(5):
        col = COL_BOOK_SPINES[bi%len(COL_BOOK_SPINES)]
        make_box(f"FloorBook_{bi}", (-1.20, 0.80, 0.04+bi*0.05), (0.30, 0.22, 0.05), col)

def build_ceiling_infra():
    for j, ypos in enumerate([1.5, 3.5]):
        make_fluorescent_tube_fixture(f"Fluor_{j}", (0.0, ypos, CEIL), length=1.20, width=0.32)
    make_smoke_detector("Smoke", (0.0, 2.5, CEIL))

def main():
    clear_scene(); build_shell(); build_living(); build_dining_nook(); build_floor_lamp(); build_kitchenette(); build_radiator_under_window(); build_decor(); build_ceiling_infra()
    out = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "../../../assets/3d/locales/montreal_apartment.glb"))
    print(f"\n[build_montreal_apartment] exporting to {out}")
    export_glb(out)

if __name__ == "__main__": main()
