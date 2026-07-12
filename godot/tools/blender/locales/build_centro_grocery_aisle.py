"""Centro Grocery — main aisle — vol6 placement script."""
import os, sys
_BT = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
if _BT not in sys.path: sys.path.insert(0, _BT)
from _props import palette as P
from _props.geometry import clear_scene, make_box, make_cyl, export_glb
from _props.structure import make_floor, make_wall, make_ceiling, make_crown_molding, make_window
from _props.store_fixtures import make_counter, make_counter_bullnose, make_register
from _props.shelving import make_snack_aisle, make_endcap
from _props.food_service import make_coffee_pots, make_donut_display
from _props.decor import make_wall_clock, make_floor_plant, make_faded_poster, make_calendar
from _props.safety import make_smoke_detector, make_hvac_vent, make_fluorescent_tube_fixture, make_ceiling_speaker

ROOM_W = 10.0; ROOM_D = 8.0; CEIL = 3.0
PAL_WALL = {"wall": (0.88, 0.88, 0.86, 1.0), "baseboard": (0.42, 0.42, 0.40, 1.0)}
COL_FLOOR = (0.78, 0.78, 0.74, 1.0); COL_SEAM = (0.42, 0.42, 0.40, 1.0); COL_WOOD = (0.62, 0.62, 0.60, 1.0)
COL_ACCENT = (0.32, 0.62, 0.42, 1.0)

def build_shell():
    make_floor("Floor", (0.0, ROOM_D/2.0, 0.0), size_x=ROOM_W+0.4, size_y=ROOM_D+0.4,
               palette={"vinyl": COL_FLOOR, "seam": COL_SEAM})
    for nm, x, bb in [("Wall_W", -ROOM_W/2.0, +1), ("Wall_E", +ROOM_W/2.0, -1)]:
        make_wall(nm, (x, ROOM_D/2.0, 0), length=ROOM_D+0.4, height=CEIL, axis='Y',
                  palette=PAL_WALL, baseboard_face_sign=bb)
    make_wall("Wall_N", (0.0, ROOM_D, 0), length=ROOM_W+0.4, height=CEIL, axis='X',
              palette=PAL_WALL, baseboard_face_sign=-1)
    make_wall("Wall_S_W", (-(ROOM_W/4.0+0.5), 0.0, 0), length=ROOM_W/2.0-1.0, height=CEIL, axis='X', palette=PAL_WALL)
    make_wall("Wall_S_E", (+(ROOM_W/4.0+0.5), 0.0, 0), length=ROOM_W/2.0-1.0, height=CEIL, axis='X', palette=PAL_WALL)
    make_box("Wall_S_AboveDoor", (0.0, 0.0, CEIL-0.30), (2.0, 0.20, 0.60), PAL_WALL["wall"])
    make_ceiling("Ceil", (0.0, ROOM_D/2.0, CEIL), size_x=ROOM_W+0.4, size_y=ROOM_D+0.4)
    for nm, ax, length, wx, wy in [
            ("Crown_W", 'Y', ROOM_D, -ROOM_W/2.0+0.10, ROOM_D/2.0),
            ("Crown_E", 'Y', ROOM_D, +ROOM_W/2.0-0.10, ROOM_D/2.0),
            ("Crown_N", 'X', ROOM_W, 0.0, ROOM_D-0.10),
            ("Crown_S", 'X', ROOM_W, 0.0, +0.10)]:
        make_crown_molding(nm, wall_x=wx, wall_y=wy, length=length, axis=ax, ceil_z=CEIL, palette={"wood": COL_WOOD})

def build_aisles():
    for ai in range(2):
        ay = ROOM_D * (0.35 + ai * 0.30)
        make_snack_aisle(f"Aisle_{ai}", (0.0, ay, 0.0), length=6.0, shelf_count=5)

def build_endcaps():
    for ei, ex in enumerate([-3.5, +3.5]):
        make_endcap(f"EndCap_{ei}", (ex, ROOM_D/2.0+1.0, 0.0))

def build_floor_grid():
    # Cross-seams for grid tile floor
    for j in range(int(ROOM_D)+1):
        make_box(f"FloorTile_Y_{j}", (0.0, float(j), 0.005), (ROOM_W, 0.02, 0.001), COL_SEAM)

def build_fluor():
    pass  # already handled in build_ceiling_infra

def build_ceiling_infra():
    for j in range(2):
        ypos = ROOM_D * (0.30 + j * 0.40)
        make_fluorescent_tube_fixture(f"Fluor_{j}", (0.0, ypos, CEIL), length=1.40, width=0.34)
    make_smoke_detector("Smoke", (0.0, ROOM_D/2.0, CEIL))
    make_hvac_vent("HVAC", (-ROOM_W/4.0, ROOM_D-0.5, CEIL), width=0.80, depth=0.40)

def build_dressing():
    """Grocery flavour: a shopping cart, a chest freezer along the east
    wall, a hanging aisle-number sign, a stack of hand baskets by the
    entrance, and a wet-floor cone."""
    # Shopping cart — open wire basket on a splayed frame with wheels
    cx, cy = -1.6, 2.4
    make_box("Cart_Basket", (cx, cy, 0.62), (0.46, 0.66, 0.36), (0.72, 0.74, 0.78, 1.0))
    make_box("Cart_Basket_Floor", (cx, cy, 0.44), (0.44, 0.62, 0.02), (0.72, 0.74, 0.78, 1.0))
    make_cyl("Cart_Handle", (cx, cy+0.36, 0.86), 0.02, 0.44, P.METAL_STEEL, axis='X', segments=8)
    for wi, (wx, wy) in enumerate([(-0.20, -0.28), (0.20, -0.28), (-0.20, 0.28), (0.20, 0.28)]):
        make_cyl(f"Cart_Wheel_{wi}", (cx+wx, cy+wy, 0.06), 0.06, 0.05, P.METAL_BLACK, axis='X', segments=8)
    # Chest freezer, east wall (body + frosty glass lid)
    fx = ROOM_W/2.0 - 0.6
    make_box("Freezer_Body", (fx, ROOM_D-2.0, 0.45), (0.90, 1.80, 0.90), (0.82, 0.86, 0.90, 1.0))
    make_box("Freezer_Lid", (fx, ROOM_D-2.0, 0.94), (0.86, 1.72, 0.04), (0.80, 0.90, 0.96, 0.5))
    make_box("Freezer_Kick", (fx, ROOM_D-2.0, 0.06), (0.90, 1.80, 0.12), P.METAL_STEEL)
    # Hanging aisle-number sign over the aisle mouth
    make_cyl("AisleSign_Wire_L", (-0.6, ROOM_D/2.0, CEIL-0.35), 0.006, 0.60, P.METAL_STEEL)
    make_cyl("AisleSign_Wire_R", (0.6, ROOM_D/2.0, CEIL-0.35), 0.006, 0.60, P.METAL_STEEL)
    make_box("AisleSign_Board", (0.0, ROOM_D/2.0, CEIL-0.68), (0.90, 0.05, 0.34), COL_ACCENT)
    # Stack of hand baskets by the south entrance
    for bi in range(4):
        make_box(f"Basket_{bi}", (-ROOM_W/2.0+0.7, 0.6, 0.14+bi*0.10), (0.34, 0.24, 0.10), (0.62, 0.30, 0.24, 1.0))
    # Wet-floor cone
    make_cyl("Cone_Body", (1.4, 1.2, 0.18), 0.14, 0.36, (0.96, 0.72, 0.20, 1.0), segments=10)
    make_box("Cone_Base", (1.4, 1.2, 0.02), (0.30, 0.30, 0.04), (0.96, 0.72, 0.20, 1.0))

def main():
    clear_scene()
    build_shell()
    build_aisles()
    build_endcaps()
    build_floor_grid()
    build_fluor()
    build_ceiling_infra()
    build_dressing()
    out = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)),
        "../../../assets/3d/locales/centro_grocery_aisle.glb"))
    print(f"\n[build_centro_grocery_aisle] exporting to {out}")
    export_glb(out)

if __name__ == "__main__":
    main()
