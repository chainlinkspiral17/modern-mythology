"""Centro Grocery — main aisle — vol6 placement script.

Enriched from a two-aisle stub (aisles + endcaps + a few dressing
props, ~34 calls) to a real supermarket floor: a north-wall
REFRIGERATED cooler wall, a CHECKOUT lane (conveyor + register + card
terminal + candy rack + queue rail), an angled PRODUCE stand, a
west-wall DRY-GOODS shelf run (cans + boxes + bread), a small BAKERY /
coffee kiosk, per-aisle hanging NUMBER signs, plus more carts/baskets
and lived-in decor. Room: door/S wall at blender y=0, extends +Y;
interior lands at godot -Z. Props kept inside the 10.0 x 8.0 footprint.
"""
import os, sys
_BT = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
if _BT not in sys.path: sys.path.insert(0, _BT)
from _props import palette as P
from _props.geometry import clear_scene, make_box, make_cyl, export_glb
from _props.structure import make_floor, make_wall, make_ceiling, make_crown_molding, make_window
from _props.store_fixtures import (make_counter, make_counter_bullnose, make_register,
                                   make_credit_card_terminal)
from _props.shelving import make_snack_aisle, make_endcap
from _props.food_service import make_coffee_pots, make_donut_display
from _props.coolers_drinks import make_cooler_row, make_soda_bottle_pyramid
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
    # A soda-bottle pyramid display at the west endcap mouth
    make_soda_bottle_pyramid("SodaPyr", (-3.5, 1.6, 0.60), tiers=3, base_count=4)

def build_cooler_wall():
    # Refrigerated reach-in wall along the north wall — dairy / drinks.
    make_cooler_row("Cooler", 7.4, [-3.4, -1.1, 1.2, 3.5], cz=1.45,
                    shelves=5, cans_per_shelf=6, sixpacks_per_shelf=4)

def build_aisle_signs():
    # Hanging numbered aisle signs over each aisle's south mouth.
    for ai in range(2):
        ay = ROOM_D * (0.35 + ai * 0.30) - 3.0
        for wo in (-0.6, 0.6):
            make_cyl(f"AisleNum_{ai}_Wire_{'L' if wo<0 else 'R'}", (wo, ay, CEIL-0.35), 0.006, 0.60, P.METAL_STEEL)
        make_box(f"AisleNum_{ai}_Board", (0.0, ay, CEIL-0.68), (0.80, 0.05, 0.34), COL_ACCENT)
        make_box(f"AisleNum_{ai}_Num", (0.0, ay-0.03, CEIL-0.68), (0.20, 0.02, 0.22), P.PAPER)

def build_checkout():
    # Checkout lane near the SE entrance: conveyor counter + register +
    # card terminal + a queue rail + an impulse candy rack on the lane.
    cx, cy = 2.6, 1.6
    top_z = make_counter("Checkout", (cx, cy, 0.0), length=2.20, depth=0.80, height=0.90,
                         palette={"formica": (0.62, 0.66, 0.68, 1.0),
                                  "top": (0.24, 0.26, 0.28, 1.0), "kick": (0.24, 0.26, 0.28, 1.0)})
    # Black rubber conveyor belt inset in the counter top
    make_box("Checkout_Belt", (cx-0.05, cy, top_z+0.02), (0.44, 1.80, 0.03), (0.12, 0.12, 0.14, 1.0))
    for gi in range(6):
        make_box(f"Checkout_BeltRib_{gi}", (cx-0.05, cy-0.8+gi*0.32, top_z+0.035), (0.44, 0.02, 0.01), (0.24, 0.24, 0.26, 1.0))
    make_register("RegisterMachine", (cx+0.10, cy+0.70, top_z))
    make_credit_card_terminal("CardTerm", (cx-0.28, cy-0.55, top_z))
    # Order divider bar on the belt
    make_box("Checkout_Divider", (cx-0.05, cy+0.20, top_z+0.06), (0.40, 0.03, 0.05), (0.72, 0.20, 0.18, 1.0))
    # Queue guide rail (customer side, west)
    make_cyl("Queue_Post_S", (cx-0.9, cy-0.9, 0.5), 0.02, 1.0, P.METAL_STEEL)
    make_cyl("Queue_Post_N", (cx-0.9, cy+0.9, 0.5), 0.02, 1.0, P.METAL_STEEL)
    make_box("Queue_Rail", (cx-0.9, cy, 0.95), (0.03, 1.80, 0.04), P.METAL_STEEL)
    # Impulse candy rack facing the lane (west face of the counter)
    for ri in range(3):
        rz = top_z - 0.16 - ri*0.24
        make_box(f"Candy_Shelf_{ri}", (cx-0.42, cy, rz), (0.05, 1.60, 0.03), P.METAL_STEEL)
        for cc in range(6):
            make_box(f"Candy_{ri}_{cc}", (cx-0.45, cy-0.70+cc*0.28, rz+0.08),
                     (0.04, 0.16, 0.12), P.SNACK_TINTS[(ri+cc) % len(P.SNACK_TINTS)])

def build_produce():
    # Angled two-tier produce stand in the SW, piled with fruit/veg.
    px, py = -3.6, 2.4
    make_box("Produce_Base", (px, py, 0.30), (1.40, 1.40, 0.60), (0.42, 0.30, 0.20, 1.0))
    make_box("Produce_Tier1", (px, py-0.10, 0.66), (1.40, 1.20, 0.06), (0.52, 0.38, 0.26, 1.0))
    make_box("Produce_Tier2", (px, py+0.30, 0.92), (1.40, 0.60, 0.06), (0.52, 0.38, 0.26, 1.0))
    # Piles of produce (short cylinders grouped by colour)
    prod_cols = [(0.82, 0.24, 0.20, 1.0), (0.92, 0.58, 0.20, 1.0), (0.86, 0.82, 0.32, 1.0),
                 (0.36, 0.54, 0.28, 1.0), (0.62, 0.30, 0.42, 1.0)]
    for gi in range(5):
        gx = px - 0.5 + gi*0.26
        col = prod_cols[gi % len(prod_cols)]
        for kk in range(4):
            make_cyl(f"Produce_{gi}_{kk}", (gx + (kk%2)*0.08, py-0.30 + (kk//2)*0.10, 0.74),
                     0.05, 0.08, col, segments=8)
    # Leafy greens on the upper tier
    for li in range(4):
        make_box(f"Greens_{li}", (px-0.4+li*0.26, py+0.30, 1.00), (0.18, 0.18, 0.12), (0.34, 0.50, 0.26, 1.0))
    # A hanging scale over the produce
    make_box("Produce_Scale_Body", (px+0.5, py, 1.55), (0.24, 0.24, 0.16), P.METAL_STEEL)
    make_cyl("Produce_Scale_Rod", (px+0.5, py, 1.85), 0.01, 0.60, P.METAL_STEEL)
    make_box("Produce_Scale_Pan", (px+0.5, py, 1.42), (0.30, 0.30, 0.03), (0.72, 0.74, 0.78, 1.0))

def build_dry_goods():
    # West-wall shelf run of canned goods + boxed dry goods + bread.
    wx = -ROOM_W/2.0 + 0.20
    make_box("Dry_Back", (wx-0.06, 5.5, 1.4), (0.06, 3.6, 2.6), (0.72, 0.72, 0.68, 1.0))
    for lv, sz in enumerate([0.45, 0.95, 1.45, 1.95]):
        make_box(f"Dry_Shelf_{lv}", (wx, 5.5, sz), (0.34, 3.6, 0.04), P.METAL_STEEL)
        for pi in range(9):
            py = 5.5 - 1.7 + pi*0.42
            tint = P.SNACK_TINTS[(lv+pi) % len(P.SNACK_TINTS)]
            if (lv + pi) % 2 == 0:
                make_cyl(f"Dry_Can_{lv}_{pi}", (wx+0.10, py, sz+0.10), 0.05, 0.18, tint, segments=8)
            else:
                make_box(f"Dry_Box_{lv}_{pi}", (wx+0.10, py, sz+0.14), (0.22, 0.20, 0.26), tint)

def build_bakery():
    # Small bakery / coffee kiosk along the east wall.
    bx, by = ROOM_W/2.0 - 0.7, 3.4
    top_z = make_counter("Bakery", (bx, by, 0.0), length=1.60, depth=0.70, height=0.92,
                         palette={"formica": (0.74, 0.62, 0.42, 1.0),
                                  "top": (0.32, 0.22, 0.14, 1.0), "kick": (0.32, 0.22, 0.14, 1.0)})
    make_donut_display("Donuts", (bx-0.10, by-0.45, top_z), tiers=3)
    make_coffee_pots("CoffeePots", (bx-0.05, by+0.55, top_z), pots=3)
    make_box("Bakery_Sign", (bx, by-0.30, 2.20), (0.05, 1.00, 0.36), (0.86, 0.62, 0.30, 1.0))

def build_floor_grid():
    # Cross-seams for grid tile floor
    for j in range(int(ROOM_D)+1):
        make_box(f"FloorTile_Y_{j}", (0.0, float(j), 0.005), (ROOM_W, 0.02, 0.001), COL_SEAM)

def build_fluor():
    pass  # already handled in build_ceiling_infra

def build_ceiling_infra():
    for j, xpos in enumerate([-2.5, 0.0, 2.5]):
        make_fluorescent_tube_fixture(f"Fluor_{j}", (xpos, ROOM_D*0.35, CEIL), length=1.60, width=0.34)
        make_fluorescent_tube_fixture(f"Fluor_N_{j}", (xpos, ROOM_D*0.65, CEIL), length=1.60, width=0.34)
    make_smoke_detector("Smoke", (0.0, ROOM_D/2.0, CEIL))
    make_hvac_vent("HVAC", (-ROOM_W/4.0, ROOM_D-0.5, CEIL), width=0.80, depth=0.40)
    make_ceiling_speaker("Speaker", (ROOM_W/4.0, 2.0, CEIL))

def build_storefront():
    make_window("Win_S", (-3.0, 0.10, 1.55), width=2.60, height=1.50)

def build_more_decor():
    make_wall_clock("Clock", (0.0, ROOM_D-0.11, CEIL-0.55), frozen_hour=5, frozen_min=48)
    make_calendar("Calendar", (ROOM_W/2.0-0.05, 1.6, 1.70))
    make_faded_poster("Poster_W", (-ROOM_W/2.0+0.05, 7.2, 1.70))
    make_floor_plant("Plant", (ROOM_W/2.0-0.6, 0.7, 0.0))
    # A second nested shopping cart near the entrance
    cx, cy = 0.9, 1.0
    make_box("Cart2_Basket", (cx, cy, 0.62), (0.46, 0.66, 0.36), (0.72, 0.74, 0.78, 1.0))
    make_box("Cart2_Floor", (cx, cy, 0.44), (0.44, 0.62, 0.02), (0.72, 0.74, 0.78, 1.0))
    make_cyl("Cart2_Handle", (cx, cy+0.36, 0.86), 0.02, 0.44, P.METAL_STEEL, axis='X', segments=8)
    for wi, (wx, wy) in enumerate([(-0.20,-0.28),(0.20,-0.28),(-0.20,0.28),(0.20,0.28)]):
        make_cyl(f"Cart2_Wheel_{wi}", (cx+wx, cy+wy, 0.06), 0.06, 0.05, P.METAL_BLACK, axis='X', segments=8)

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
    build_storefront()
    build_aisles()
    build_endcaps()
    build_cooler_wall()
    build_aisle_signs()
    build_checkout()
    build_produce()
    build_dry_goods()
    build_bakery()
    build_floor_grid()
    build_fluor()
    build_ceiling_infra()
    build_dressing()
    build_more_decor()
    out = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)),
        "../../../assets/3d/locales/centro_grocery_aisle.glb"))
    print(f"\n[build_centro_grocery_aisle] exporting to {out}")
    export_glb(out)

if __name__ == "__main__":
    main()
