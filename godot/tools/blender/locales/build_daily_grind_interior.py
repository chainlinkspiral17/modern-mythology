"""daily_grind_interior — the Daily Grind coffee shop (sibling idiom to
cafe_olimpico). Espresso bar + machine, pastry case, chalkboard menu,
café tables with chairs, a couch/armchair nook. Warm pendant lighting
(see .tscn).
"""
import os, sys
_BT = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
if _BT not in sys.path: sys.path.insert(0, _BT)
from _props import palette as P
from _props.geometry import clear_scene, make_box, make_cyl, export_glb
from _props.structure import make_floor, make_wall, make_ceiling
from _props.store_fixtures import make_register
from _props.food_service import make_coffee_pots, make_donut_display, make_paper_cup_stack, make_sugar_creamer_caddy
from _props.decor import make_floor_plant
from _props.safety import make_smoke_detector

ROOM_W = 7.0; ROOM_D = 6.0; CEIL = 2.8
PAL_WALL = {"wall":(0.72,0.66,0.56,1.0),"baseboard":(0.34,0.28,0.22,1.0)}
COL_FLOOR = (0.54,0.44,0.34,1.0); COL_SEAM = (0.32,0.26,0.20,1.0)
COL_WOOD = (0.42,0.30,0.20,1.0); COL_COUNTER_TOP = (0.22,0.16,0.12,1.0)
COL_STEEL = P.METAL_STEEL; COL_BLACK = P.METAL_BLACK
COL_ESPRESSO = (0.78,0.78,0.74,1.0); COL_ESPRESSO_TRIM = (0.32,0.22,0.14,1.0)
COL_CHALK = (0.14,0.16,0.15,1.0); COL_COUCH = (0.40,0.32,0.26,1.0)
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

def build_service_counter():
    # Espresso bar running along X in front of the north wall.
    top_z = 1.03
    make_box("Counter_Front", (-0.4, 5.2, 0.47), (5.6, 0.60, 0.94), COL_WOOD)
    make_box("Counter_Top",   (-0.4, 5.14, top_z), (5.8, 0.80, 0.06), COL_COUNTER_TOP)
    make_box("Counter_Kick",  (-0.4, 4.90, 0.10), (5.6, 0.05, 0.20), COL_BLACK)
    # Espresso machine (2-group, chrome).
    ex, ey = -1.9, 5.25
    make_box("Espresso_Body", (ex, ey, top_z+0.28), (1.20, 0.46, 0.54), COL_ESPRESSO)
    make_box("Espresso_TopHat", (ex, ey, top_z+0.60), (1.20, 0.46, 0.10), COL_ESPRESSO_TRIM)
    for gi in range(2):
        gx = ex - 0.26 + gi*0.52
        make_cyl(f"Espresso_Group_{gi}_Head", (gx, ey-0.20, top_z+0.18), 0.06, 0.10, COL_ESPRESSO_TRIM)
        make_cyl(f"Espresso_Group_{gi}_Spout", (gx, ey-0.20, top_z+0.10), 0.02, 0.08, COL_STEEL)
        make_cyl(f"Espresso_Cup_{gi}", (gx, ey-0.20, top_z+0.04), 0.04, 0.06, P.PAPER)
    make_cyl("Espresso_SteamWand", (ex+0.54, ey-0.10, top_z+0.28), 0.012, 0.28, COL_STEEL)
    make_paper_cup_stack("CupStack", (ex-0.66, ey+0.02, top_z), count=16)
    # Drip coffee pots (make_coffee_pots — was imported but never used).
    make_coffee_pots("Coffee", (0.5, 5.25, top_z), pots=2)
    # Pastry case at the east end.
    make_donut_display("Pastry", (2.0, 5.28, top_z))
    # Register on the counter top.
    make_register("Register", (2.95, 5.05, top_z))
    # Condiment / sugar caddy at the west end.
    make_sugar_creamer_caddy("Caddy", (-3.0, 4.95, top_z))

def build_chalkboard():
    cx, cz, y = -0.5, 2.05, 5.90
    make_box("Chalk_Frame", (cx, y, cz), (2.40, 0.04, 0.90), COL_WOOD)
    make_box("Chalk_Board", (cx, y-0.02, cz), (2.20, 0.02, 0.74), COL_CHALK)
    # Menu text rows (faint chalk lines).
    chalk_cols = [(0.86,0.84,0.78,1.0),(0.72,0.82,0.72,1.0),(0.86,0.78,0.62,1.0)]
    for r in range(4):
        make_box(f"Chalk_Row_{r}", (cx-0.30, y-0.03, cz+0.24 - r*0.16), (1.10, 0.002, 0.03), chalk_cols[r % 3])
        make_box(f"Chalk_Price_{r}", (cx+0.72, y-0.03, cz+0.24 - r*0.16), (0.26, 0.002, 0.03), (0.86,0.72,0.42,1.0))

def _make_cafe_table(prefix, tx, ty):
    make_cyl(f"{prefix}_Top", (tx, ty, 0.74), 0.38, 0.04, COL_WOOD, segments=16)
    make_cyl(f"{prefix}_Pedestal", (tx, ty, 0.37), 0.05, 0.70, COL_ESPRESSO_TRIM)
    make_cyl(f"{prefix}_Foot", (tx, ty, 0.03), 0.22, 0.04, COL_ESPRESSO_TRIM, segments=12)
    make_cyl(f"{prefix}_Saucer", (tx, ty, 0.77), 0.06, 0.006, P.PAPER)
    make_cyl(f"{prefix}_Cup", (tx, ty, 0.81), 0.04, 0.06, P.PAPER)
    for ci, (ox, oy) in enumerate([(-0.58, 0.0), (0.58, 0.0)]):
        cx, cy = tx + ox, ty + oy
        make_cyl(f"{prefix}_Chair_{ci}_Seat", (cx, cy, 0.46), 0.18, 0.04, COL_WOOD, segments=12)
        make_box(f"{prefix}_Chair_{ci}_Back", (cx + (0.16 if ox < 0 else -0.16), cy, 0.72), (0.04, 0.36, 0.52), COL_WOOD)
        for li, (lx, ly) in enumerate([(-0.13,-0.13),(0.13,-0.13),(-0.13,0.13),(0.13,0.13)]):
            make_cyl(f"{prefix}_Chair_{ci}_Leg_{li}", (cx+lx, cy+ly, 0.23), 0.012, 0.46, COL_BLACK)

def build_tables():
    _make_cafe_table("Table_0", -2.0, 2.3)
    _make_cafe_table("Table_1", 0.4, 1.9)
    _make_cafe_table("Table_2", 2.3, 2.7)

def build_lounge():
    # Couch + armchair + low table nook in the SW corner.
    cx = -2.9
    make_box("Couch_Base", (cx, 4.0, 0.24), (0.70, 1.60, 0.22), COL_COUCH)
    make_box("Couch_Back", (cx-0.27, 4.0, 0.56), (0.16, 1.60, 0.52), COL_COUCH)
    for ay in (3.25, 4.75):
        make_box(f"Couch_Arm_{ay:.0f}", (cx, ay, 0.40), (0.66, 0.16, 0.34), COL_COUCH)
    for ci, cy in enumerate([3.62, 4.38]):
        make_box(f"Couch_SeatCush_{ci}", (cx+0.02, cy, 0.40), (0.58, 0.60, 0.14), (0.50,0.40,0.32,1.0))
        make_box(f"Couch_BackCush_{ci}", (cx-0.16, cy, 0.60), (0.18, 0.58, 0.38), (0.50,0.40,0.32,1.0))
    # Low coffee table
    make_box("Lounge_Table_Top", (cx+1.0, 4.0, 0.42), (0.66, 0.90, 0.05), COL_WOOD)
    for li, (lx, ly) in enumerate([(-0.28,-0.38),(0.28,-0.38),(-0.28,0.38),(0.28,0.38)]):
        make_cyl(f"Lounge_Table_Leg_{li}", (cx+1.0+lx, 4.0+ly, 0.20), 0.02, 0.40, COL_BLACK)
    make_box("Lounge_Magazine", (cx+1.0, 4.0, 0.46), (0.24, 0.30, 0.02), (0.72,0.42,0.28,1.0))
    # Armchair facing the couch
    ax = cx + 1.9
    make_box("Armchair_Base", (ax, 4.0, 0.24), (0.62, 0.62, 0.22), COL_COUCH)
    make_box("Armchair_Back", (ax+0.25, 4.0, 0.56), (0.14, 0.62, 0.52), COL_COUCH)
    for ay in (3.70, 4.30):
        make_box(f"Armchair_Arm_{ay:.0f}", (ax, ay, 0.40), (0.58, 0.14, 0.34), COL_COUCH)
    make_box("Armchair_Cush", (ax, 4.0, 0.40), (0.54, 0.54, 0.14), (0.50,0.40,0.32,1.0))

def build_pendants():
    for pi, (px, py) in enumerate([(-1.5, 5.0), (1.0, 5.0), (0.0, 2.3)]):
        make_cyl(f"Pendant_{pi}_Cord", (px, py, CEIL-0.28), 0.006, 0.36, COL_BLACK)
        make_cyl(f"Pendant_{pi}_Shade", (px, py, CEIL-0.58), 0.15, 0.16, (0.86,0.58,0.28,1.0), segments=12)
        make_cyl(f"Pendant_{pi}_Bulb", (px, py, CEIL-0.66), 0.05, 0.06, (0.98,0.88,0.62,1.0))

def build_decor():
    make_floor_plant("Plant_SE", (ROOM_W/2.0-0.55, 0.60, 0.0))

def build_ceiling_infra():
    make_smoke_detector("Smoke", (0.0, ROOM_D/2.0, CEIL))

def main():
    clear_scene()
    build_shell()
    build_service_counter()
    build_chalkboard()
    build_tables()
    build_lounge()
    build_pendants()
    build_decor()
    build_ceiling_infra()
    out = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)),
        "../../../assets/3d/locales/daily_grind_interior.glb"))
    print(f"\n[build_daily_grind_interior] exporting to {out}")
    export_glb(out)

if __name__ == "__main__":
    main()
