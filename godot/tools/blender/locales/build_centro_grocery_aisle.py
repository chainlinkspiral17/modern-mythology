"""Centro Grocery — main aisle — vol6 placement script.

Enriched from a two-aisle stub (aisles + endcaps + a few dressing
props, ~34 calls) to a real supermarket floor: a north-wall
REFRIGERATED cooler wall, a CHECKOUT lane (conveyor + register + card
terminal + candy rack + queue rail), an angled PRODUCE stand, a
west-wall DRY-GOODS shelf run (cans + boxes + bread), a small BAKERY /
coffee kiosk, per-aisle hanging NUMBER signs, plus more carts/baskets
and lived-in decor. Room: door/S wall at blender y=0, extends +Y;
interior lands at godot -Z. Props kept inside the 10.0 x 8.0 footprint.

DRAFT 4 (2026-09-18, lore/_VISUAL_PROGRAM.md §3): wire shopping carts
(a local `make_shopping_cart` — the class goes to _props on its third
room), the wet-floor cone a cone, fruit round, the produce scale with
its dial, pan and chains, lathed queue posts, hand-truck and pallet-jack
wheels, the cooler door's handle; the store's first WEAR (entry path,
both aisle lanes, endcap scuffs, the belt's centre, the wet spot, cart
lines, the cooler door's arc); D3 (cords to a floor box, the EXIT sign
and its conduit, the compressor grille, a floor drain); D5 (the lot:
asphalt, walk, curb, stripes, a parked car, the cart corral, a lamp
post, the strip across). The .tscn gains the EXIT sign's glow.

DRAFT 5 targets: the aisles' facings as products with faces (the
inventory chapter runs on them); the cooler wall's doors with handles
and price strips; the meat trays' contents; the bakery's donuts as
rings; the checkout's bag rack and bags; Deck: the sheet's establish and
`insert scanner`.
"""
import os, sys, math
_BT = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
if _BT not in sys.path: sys.path.insert(0, _BT)
from _props import palette as P
from _props.geometry import (clear_scene, make_box, make_chamfer_box, make_cyl, make_lathe,
                             make_tube, make_rot_box, export_glb)
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
    make_wall("Wall_S_W", (-(ROOM_W/4.0+0.5), 0.0, 0), length=ROOM_W/2.0-1.0, height=CEIL, axis='X', palette=PAL_WALL, baseboard_face_sign=+1)
    make_wall("Wall_S_E", (+(ROOM_W/4.0+0.5), 0.0, 0), length=ROOM_W/2.0-1.0, height=CEIL, axis='X', palette=PAL_WALL, baseboard_face_sign=+1)
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
        # Shelf-edge price-tag rails (the inventory chapter runs on
        # facings and tags)
        for side in (-1, 1):
            for lvl in range(5):
                make_box(f"TagRail_{ai}_{side}_{lvl}", (0.0, ay + side * 0.35, 0.30 + lvl * 0.36),   # on the shelf faces (2026-09-22: 28 cm out)
                         (6.0, 0.012, 0.035), (0.94, 0.94, 0.92, 1.0))
    # Two more runs so "Aisle Seven … Aisle Nine" reads as a store,
    # not a pair
    # (2026-09-22) Aisle_2 was a 4.4 m gondola at y 2.72 — bodily
    # INSIDE Aisle_0 at y 2.80. Removed; three runs read as a store.
    make_snack_aisle("Aisle_3", (0.0, ROOM_D * 0.80, 0.0), length=6.0, shelf_count=5)

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
        for wo in (-0.35, 0.35):   # inside the board's width; board top to the ceiling (2026-09-22: 5 cm short, 20 cm outside)
            make_cyl(f"AisleNum_{ai}_Wire_{'L' if wo<0 else 'R'}", (wo, ay, CEIL-0.255), 0.006, 0.51, P.METAL_STEEL)
        make_box(f"AisleNum_{ai}_Board", (0.0, ay, CEIL-0.68), (0.80, 0.05, 0.34), COL_ACCENT)
        make_box(f"AisleNum_{ai}_Num", (0.0, ay-0.03, CEIL-0.68), (0.20, 0.02, 0.22), P.PAPER)
        # Legible numerals: 7 and 9 (the prose counts twelve aisles;
        # these two are named)
        if ai == 0:
            make_box(f"AisleNum_{ai}_D_Top", (0.0, ay-0.045, CEIL-0.60), (0.14, 0.012, 0.03), (0.18, 0.18, 0.20, 1.0))
            make_box(f"AisleNum_{ai}_D_Diag", (0.02, ay-0.045, CEIL-0.70), (0.03, 0.012, 0.16), (0.18, 0.18, 0.20, 1.0))
        else:
            make_cyl(f"AisleNum_{ai}_D_Ring", (0.0, ay-0.045, CEIL-0.63), 0.055, 0.012, (0.18, 0.18, 0.20, 1.0), axis='Y', segments=10)
            make_box(f"AisleNum_{ai}_D_Tail", (0.05, ay-0.045, CEIL-0.72), (0.03, 0.012, 0.12), (0.18, 0.18, 0.20, 1.0))

def build_checkout():
    # Checkout lane near the SE entrance: conveyor counter + register +
    # card terminal + a queue rail + an impulse candy rack on the lane.
    cx, cy = 3.55, 1.75
    top_z = make_counter("Checkout", (cx, cy, 0.0), length=2.20, depth=0.80, height=0.90,
                         palette={"formica": (0.62, 0.66, 0.68, 1.0),
                                  "top": (0.24, 0.26, 0.28, 1.0), "kick": (0.24, 0.26, 0.28, 1.0)})
    # Black rubber conveyor belt inset in the counter top
    make_box("Checkout_Belt", (cx-0.05, cy, top_z+0.02), (0.44, 1.80, 0.03), (0.12, 0.12, 0.14, 1.0))
    for gi in range(6):
        make_box(f"Checkout_BeltRib_{gi}", (cx-0.05, cy-0.8+gi*0.32, top_z+0.035), (0.44, 0.02, 0.01), (0.24, 0.24, 0.26, 1.0))
    make_register("RegisterMachine", (cx+0.10, cy+0.70, top_z))
    make_credit_card_terminal("CardTerm", (cx-0.44, cy-0.72, top_z))
    # Order divider bar on the belt
    make_box("Checkout_Divider", (cx-0.05, cy+0.20, top_z+0.06), (0.40, 0.03, 0.05), (0.72, 0.20, 0.18, 1.0))
    # Queue guide rail (customer side, west)
    for qi, qy in (("S", cy-0.9), ("N", cy+0.9)):
        make_lathe(f"Queue_Post_{qi}", (cx-0.9, qy, 0.0), [(0.14, 0.0), (0.13, 0.02), (0.03, 0.04), (0.02, 0.95), (0.03, 0.98), (0.0, 0.98)], P.METAL_STEEL, segments=10)
    make_tube("Queue_Rail", [(cx-0.9, cy-0.9, 0.95), (cx-0.9, cy+0.9, 0.95)], 0.014, P.METAL_STEEL, segments=6)
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
    make_chamfer_box("Produce_Base", (px, py, 0.30), (1.40, 1.40, 0.60), (0.42, 0.30, 0.20, 1.0))
    make_box("Produce_Tier1", (px, py-0.10, 0.66), (1.40, 1.20, 0.06), (0.52, 0.38, 0.26, 1.0))
    make_box("Produce_Tier2", (px, py+0.30, 0.92), (1.40, 0.60, 0.06), (0.52, 0.38, 0.26, 1.0))
    # Piles of produce (short cylinders grouped by colour)
    prod_cols = [(0.82, 0.24, 0.20, 1.0), (0.92, 0.58, 0.20, 1.0), (0.86, 0.82, 0.32, 1.0),
                 (0.36, 0.54, 0.28, 1.0), (0.62, 0.30, 0.42, 1.0)]
    for gi in range(5):
        gx = px - 0.5 + gi*0.26
        col = prod_cols[gi % len(prod_cols)]
        for kk in range(4):
            # draft 4: fruit is round
            make_lathe(f"Produce_{gi}_{kk}", (gx + (kk%2)*0.08, py-0.30 + (kk//2)*0.10, 0.69),
                       [(0.0, 0.0), (0.035, 0.008), (0.05, 0.035), (0.048, 0.065), (0.03, 0.085), (0.0, 0.09)], col, segments=8)
    # Leafy greens on the upper tier
    for li in range(4):
        make_box(f"Greens_{li}", (px-0.4+li*0.26, py+0.30, 1.00), (0.18, 0.18, 0.12), (0.34, 0.50, 0.26, 1.0))
    # A hanging scale over the produce
    make_lathe("Produce_Scale_Body", (px+0.5, py, 1.47), [(0.12, 0.0), (0.13, 0.02), (0.13, 0.14), (0.10, 0.16), (0.0, 0.16)], P.METAL_STEEL, segments=12)
    make_cyl("Produce_Scale_Dial", (px+0.5, py-0.132, 1.55), 0.09, 0.006, (0.92, 0.92, 0.88, 1.0), axis='Y', segments=14)
    make_tube("Produce_Scale_Rod", [(px+0.5, py, 1.63), (px+0.5, py, 2.15)], 0.008, P.METAL_STEEL, segments=5)
    make_lathe("Produce_Scale_Pan", (px+0.5, py, 1.30), [(0.0, 0.0), (0.16, 0.0), (0.18, 0.03), (0.16, 0.04), (0.0, 0.035)], (0.72, 0.74, 0.78, 1.0), segments=14)
    for ci2 in range(3):
        ang2 = ci2 * 2.094
        make_tube(f"Produce_Scale_Chain_{ci2}", [(px+0.5 + 0.15 * math.cos(ang2), py + 0.15 * math.sin(ang2), 1.34), (px+0.5, py, 1.47)], 0.003, P.METAL_STEEL, segments=4)

def build_dry_goods():
    # West-wall shelf run of canned goods + boxed dry goods + bread.
    wx = -ROOM_W/2.0 + 0.20
    make_box("Dry_Back", (wx-0.06, 4.1, 1.4), (0.06, 3.6, 2.6), (0.72, 0.72, 0.68, 1.0))
    for lv, sz in enumerate([0.45, 0.95, 1.45, 1.95]):
        make_box(f"Dry_Shelf_{lv}", (wx, 4.1, sz), (0.34, 3.6, 0.04), P.METAL_STEEL)
        for pi in range(9):
            py = 4.1 - 1.7 + pi*0.42
            tint = P.SNACK_TINTS[(lv+pi) % len(P.SNACK_TINTS)]
            if (lv + pi) % 2 == 0:
                make_cyl(f"Dry_Can_{lv}_{pi}", (wx+0.10, py, sz+0.10), 0.05, 0.18, tint, segments=8)
            else:
                make_box(f"Dry_Box_{lv}_{pi}", (wx+0.10, py, sz+0.14), (0.22, 0.20, 0.26), tint)

def build_bakery():
    # Small bakery / coffee kiosk along the east wall.
    bx, by = ROOM_W/2.0 - 0.7, 3.75   # clear of the checkout's N end (2026-09-22)
    top_z = make_counter("Bakery", (bx, by, 0.0), length=1.60, depth=0.70, height=0.92,
                         palette={"formica": (0.74, 0.62, 0.42, 1.0),
                                  "top": (0.32, 0.22, 0.14, 1.0), "kick": (0.32, 0.22, 0.14, 1.0)})
    make_donut_display("Donuts", (bx-0.10, by-0.45, top_z), tiers=3)
    make_coffee_pots("CoffeePots", (bx-0.05, by+0.55, top_z), pots=3)
    make_box("Bakery_Sign", (ROOM_W/2.0 - 0.125, by-0.30, 2.20), (0.05, 1.00, 0.36), (0.86, 0.62, 0.30, 1.0))   # on the E wall (2026-09-22: 0.6 m off it)

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
    # anchored on the wall's room face, built toward the room (2026-09-23: the glass was inside the wall)
    make_window("Win_S", (-3.0, 0.10, 1.55), width=2.60, height=1.50, room_dir=+1)

def make_shopping_cart(prefix, cx, cy, yaw_open=True):
    """A wire cart (draft 4, 2026-09-18): a frame of tubes, basket rails,
    a handle with grips, lathed casters — not a box on four discs."""
    wire = (0.72, 0.74, 0.78, 1.0)
    rails = []
    for zi, bz in enumerate((0.46, 0.60, 0.74)):
        w = 0.22 + zi * 0.02
        d = 0.32 + zi * 0.02
        make_tube(f"{prefix}_Rail_{zi}", [(cx - w, cy - d, bz), (cx + w, cy - d, bz), (cx + w, cy + d, bz), (cx - w, cy + d, bz), (cx - w, cy - d, bz)], 0.006, wire, segments=5)
    for ci, (u, v) in enumerate(((-1, -1), (1, -1), (-1, 1), (1, 1))):
        make_tube(f"{prefix}_Upright_{ci}", [(cx + u * 0.22, cy + v * 0.32, 0.44), (cx + u * 0.26, cy + v * 0.36, 0.80)], 0.007, wire, segments=5)
    for vi in range(6):
        vx = cx - 0.20 + vi * 0.08
        make_tube(f"{prefix}_Vert_{vi}", [(vx, cy - 0.32, 0.46), (vx, cy - 0.34, 0.76)], 0.004, wire, segments=4)
        make_tube(f"{prefix}_VertB_{vi}", [(vx, cy + 0.32, 0.46), (vx, cy + 0.34, 0.76)], 0.004, wire, segments=4)
    make_box(f"{prefix}_Floor", (cx, cy, 0.45), (0.44, 0.62, 0.012), wire)
    for u in (-1, 1):
        make_tube(f"{prefix}_Leg_{u:+d}", [(cx + u * 0.20, cy - 0.28, 0.10), (cx + u * 0.20, cy - 0.28, 0.44), (cx + u * 0.20, cy + 0.28, 0.44), (cx + u * 0.20, cy + 0.28, 0.10)], 0.01, P.METAL_STEEL, segments=5)
    make_tube(f"{prefix}_Handle", [(cx - 0.26, cy + 0.36, 0.80), (cx - 0.26, cy + 0.42, 0.92), (cx + 0.26, cy + 0.42, 0.92), (cx + 0.26, cy + 0.36, 0.80)], 0.012, P.METAL_STEEL, segments=6)
    make_cyl(f"{prefix}_Grip", (cx, cy + 0.42, 0.92), 0.018, 0.30, (0.72, 0.20, 0.18, 1.0), axis='X', segments=8)
    for wi, (u, v) in enumerate(((-1, -1), (1, -1), (-1, 1), (1, 1))):
        make_lathe(f"{prefix}_Caster_{wi}", (cx + u * 0.20, cy + v * 0.28, 0.02), [(0.0, 0.0), (0.04, 0.005), (0.045, 0.06), (0.03, 0.09), (0.0, 0.10)], P.METAL_BLACK, segments=8)


def build_more_decor():
    make_wall_clock("Clock", (0.0, 7.900, CEIL-0.55), frozen_hour=5, frozen_min=48, facing='-Y')
    make_calendar("Calendar", (ROOM_W/2.0-0.05, 1.6, 1.70))
    make_faded_poster("Poster_W", (-ROOM_W/2.0+0.05 + 0.0535, 7.2, 1.70), into_room=+1)
    make_floor_plant("Plant", (ROOM_W/2.0-0.6, 0.40, 0.0))
    # A second shopping cart near the entrance
    make_shopping_cart("Cart2", 0.0, 1.35)   # just inside the entrance (2026-09-22: the deli took its spot)

def build_dressing():
    """Grocery flavour: a shopping cart, a chest freezer along the east
    wall, a hanging aisle-number sign, a stack of hand baskets by the
    entrance, and a wet-floor cone."""
    # Shopping cart — open wire basket on a splayed frame with wheels
    make_shopping_cart("Cart", -1.6, 3.85)   # in the corridor (2026-09-22: it straddled Aisle_0's face)
    # Chest freezer, east wall (body + frosty glass lid)
    # (2026-09-22 re-plan) the E wall could not hold checkout + bakery
    # + deli + meat case + freezer — the deli sat inside the bakery
    # and the meat case inside the checkout lane. Freezer to the S
    # wall's W section under the window; deli to the W wall; meat
    # case to the E wall's north end where the docstring always said.
    fx, fy = -2.9, 0.57
    make_chamfer_box("Freezer_Body", (fx, fy, 0.45), (1.80, 0.90, 0.90), (0.82, 0.86, 0.90, 1.0))
    make_box("Freezer_Lid", (fx, fy, 0.92), (1.72, 0.86, 0.04), (0.80, 0.90, 0.96, 0.5))   # lid ON the body (was 2 cm over it)
    make_box("Freezer_Kick", (fx, fy, 0.06), (1.80, 0.90, 0.12), P.METAL_STEEL)
    # Hanging aisle-number sign over the aisle mouth
    make_cyl("AisleSign_Wire_L", (-0.40, ROOM_D/2.0, CEIL-0.255), 0.006, 0.51, P.METAL_STEEL)
    make_cyl("AisleSign_Wire_R", (0.40, ROOM_D/2.0, CEIL-0.255), 0.006, 0.51, P.METAL_STEEL)
    make_box("AisleSign_Board", (0.0, ROOM_D/2.0, CEIL-0.68), (0.90, 0.05, 0.34), COL_ACCENT)
    # Stack of hand baskets by the south entrance
    for bi in range(4):
        make_box(f"Basket_{bi}", (-ROOM_W/2.0+0.7, 0.6, 0.05+bi*0.10), (0.34, 0.24, 0.10), (0.62, 0.30, 0.24, 1.0))   # from the floor (2026-09-22)
    # Wet-floor cone
    make_chamfer_box("Cone_Base", (1.4, 1.30, 0.02), (0.30, 0.30, 0.04), (0.96, 0.72, 0.20, 1.0), chamfer=0.01)
    make_lathe("Cone_Body", (1.4, 1.30, 0.04), [(0.13, 0.0), (0.12, 0.05), (0.03, 0.62), (0.0, 0.64)], (0.96, 0.72, 0.20, 1.0), segments=12)   # draft 4: a cone
    make_box("Cone_Sign", (1.4, 1.222, 0.36), (0.12, 0.002, 0.10), (0.16, 0.16, 0.18, 1.0))   # a sleeve on the cone's face (2026-09-25: it ran through the cone's axis)

def build_departments():
    """2026-08-03 hero-prop pass: meat counter, deli case, the
    pallet + hand truck + forgotten pallet jack, the propped cooler
    door + milk crate, the frozen run, the cardboard bale, the
    register cubby, the leaking dented can."""
    steel = (0.60, 0.62, 0.63, 1.0)
    glass = (0.55, 0.62, 0.66, 0.4)
    # Meat counter, E wall north end
    mcx, mcy = 4.35, 5.85   # E wall, between the endcap and the cooler run
    make_chamfer_box("Meat_Case_Body", (mcx, mcy, 0.55), (1.10, 2.40, 1.10), (0.86, 0.86, 0.84, 1.0))
    # the sneeze glass as a railed frame + glints (2026-09-24: a 2.3 m
    # slab — no alpha in this pipeline — standing over the trays)
    for pe, dy_ in (("S", -1.13), ("N", 1.13)):
        make_box(f"Meat_Case_Glass_Post_{pe}", (mcx - 0.53, mcy + dy_, 1.36), (0.04, 0.04, 0.52), steel)
    make_box("Meat_Case_Glass_Rail", (mcx - 0.53, mcy, 1.635), (0.04, 2.30, 0.03), steel)
    for gi, (gy, gw) in enumerate(((-0.70, 0.03), (-0.60, 0.012), (0.55, 0.02))):
        make_box(f"Meat_Case_Glint_{gi}", (mcx - 0.53, mcy + gy, 1.36), (0.004, gw, 0.52), (0.86, 0.90, 0.92, 1.0))
    for mi in range(4):
        make_box(f"Meat_Tray_{mi}", (mcx, mcy - 0.80 + mi * 0.55, 1.13), (0.60, 0.42, 0.06),
                 [(0.72, 0.32, 0.30, 1.0), (0.80, 0.46, 0.42, 1.0)][mi % 2])
    # Deli case + wipe-down worktop
    dcx, dcy = 1.70, 0.60   # S wall E section, between the entrance and the queue; glass faces north
    make_chamfer_box("Deli_Case_Body", (dcx, dcy, 0.55), (1.60, 1.00, 1.10), (0.86, 0.86, 0.84, 1.0))
    make_box("Deli_Case_Glass", (dcx, dcy + 0.47, 1.28), (1.50, 0.04, 0.50), glass)
    make_box("Deli_Worktop", (dcx, dcy - 0.33, 0.92), (1.50, 0.30, 0.05), steel)
    # Pallet + hand truck + the forgotten pallet jack
    make_box("Pallet", (-1.0, 1.55, 0.08), (1.00, 1.20, 0.16), (0.62, 0.48, 0.30, 1.0))
    make_chamfer_box("Pallet_Load", (-1.0, 1.55, 0.46), (0.90, 1.05, 0.60), (0.68, 0.56, 0.38, 1.0))
    make_rot_box("HandTruck_Frame", (-1.9, 1.5, 0.60), (0.08, 0.40, 1.20), (0.62, 0.28, 0.24, 1.0), roll=0.0)
    make_box("HandTruck_Toe", (-1.86, 1.5, 0.04), (0.30, 0.44, 0.03), steel)
    for wi3, wy3 in enumerate((1.28, 1.72)):
        make_lathe(f"HandTruck_Wheel_{wi3}", (-1.94, wy3, 0.0), [(0.0, 0.0), (0.12, 0.0), (0.12, 0.05), (0.0, 0.05)], P.METAL_BLACK, segments=10)
    make_box("PalletJack_Forks", (2.3, 1.60, 0.08), (0.56, 1.20, 0.12), (0.86, 0.52, 0.16, 1.0))   # reach the tiller (2026-09-22: 5 cm short)
    make_box("PalletJack_Tiller", (2.3, 2.20, 0.55), (0.08, 0.10, 0.90), (0.30, 0.30, 0.32, 1.0))
    # Cooler swing door propped open with the milk crate (sticking
    # lock since July)
    make_box("Cooler_Door_Leaf", (-3.72, 7.375, 1.00), (0.30, 0.05, 1.90), (0.82, 0.84, 0.86, 1.0))   # against the frame (2026-09-22: 2.5 cm off it)
    make_tube("Cooler_Door_Handle", [(-3.60, 7.34, 0.85), (-3.60, 7.30, 0.85), (-3.60, 7.30, 1.15), (-3.60, 7.34, 1.15)], 0.012, steel, segments=6)   # standoffs meet the leaf
    make_box("Milk_Crate_Prop", (-3.55, 7.19, 0.14), (0.32, 0.32, 0.28), (0.30, 0.44, 0.62, 1.0))   # against the leaf it props
    # Frozen run: upright glass doors, W wall north end
    make_chamfer_box("Frozen_Bank", (-4.62, 6.8, 1.10), (0.55, 1.70, 2.20), (0.80, 0.84, 0.88, 1.0))
    for fi in range(3):
        make_box(f"Frozen_Door_{fi}", (-4.34, 6.25 + fi * 0.56, 1.15), (0.03, 0.50, 1.80), glass)
    # The cardboard bale at the aisle's north mouth
    make_chamfer_box("Card_Bale", (-4.15, 4.35, 0.70), (0.90, 0.80, 1.40), (0.44, 0.48, 0.52, 1.0))
    make_box("Card_Bale_Lid", (-4.15, 4.35, 1.42), (0.86, 0.76, 0.05), steel)
    make_box("Card_Bale_Stack", (-4.15, 4.30, 0.90), (0.70, 0.60, 0.30), (0.66, 0.54, 0.36, 1.0))
    # Register cubby (Diego's backpack)
    # cashier side, against the counter's back (2026-09-22: it sat 18 cm
    # inside the counter front AND inside the meat case)
    make_chamfer_box("Register_Cubby", (4.12, 1.6, 0.45), (0.36, 1.20, 0.90), (0.46, 0.42, 0.36, 1.0))
    make_chamfer_box("Cubby_Backpack", (4.12, 1.4, 0.30), (0.28, 0.30, 0.42), (0.30, 0.36, 0.30, 1.0))
    # The dented can of cream of mushroom, leaking under row 4F
    make_cyl("Dented_Can", (1.2, 2.22, 0.055), 0.05, 0.11, (0.84, 0.80, 0.70, 1.0), axis='X', segments=10)
    make_cyl("Can_Puddle", (1.28, 2.20, 0.006), 0.09, 0.005, (0.72, 0.68, 0.56, 1.0), segments=10)


def build_hero_props_2026_09():
    """HERO PROPS FOR THE BLIND CUES (shot_marker_audit, 2026-09-01).

    Six distinct cues fire on Centro; the pallet existed (marker
    only). Built here, each at its prose station:

    - THE COOLER THERMOMETER ("the thermometer Russell mounted
      inside the cooler door ... has been at thirty-six"): small
      body + red needle on the ajar Cooler_Door_Leaf's inner face.
    - THE FIVE ("He pushes a five across the table"): flat on the
      checkout belt between two ribs — the closest thing this
      locale has to a table across which money slides.
    - THE CHAIN-ISSUED SCANNER (inventory night, canned soup):
      resting on the second shelf at the aisle's east head where
      Diego set it between passes.
    - RUSSELL'S CLIPBOARD ("taps his pen on the clipboard twice"):
      flat on the pallet load, clip and pen with it.
    - DIEGO'S PHONE ("He takes his phone out of his back pocket"):
      face-up beside the clipboard on the pallet load.
    """
    steel = (0.62, 0.63, 0.64, 1.0)
    # ── THE COOLER THERMOMETER · inner face of the door leaf ──
    make_box("Cooler_Thermometer", (-3.70, 7.344, 1.45), (0.050, 0.012, 0.140),
             (0.90, 0.89, 0.86, 1.0))
    make_box("Thermometer_Needle", (-3.70, 7.336, 1.43), (0.008, 0.004, 0.030),
             (0.80, 0.22, 0.18, 1.0))
    # ── THE FIVE · on the checkout belt, between ribs ──
    make_box("Five_Dollar_Bill", (3.50, 1.42, 0.9614), (0.156, 0.066, 0.0015),
             (0.62, 0.68, 0.56, 1.0))
    # ── THE CHAIN-ISSUED SCANNER · shelf 1, east aisle head ──
    make_box("Chain_Scanner", (2.55, 2.48, 0.7825), (0.060, 0.150, 0.045),
             (0.22, 0.22, 0.25, 1.0))
    make_box("Scanner_Window", (2.55, 2.4014, 0.7825), (0.036, 0.006, 0.020),
             (0.70, 0.24, 0.20, 1.0))
    # ── RUSSELL'S CLIPBOARD + PEN · flat on the pallet load ──
    make_box("Russell_Clipboard", (-1.0, 1.40, 0.766), (0.240, 0.320, 0.012),
             (0.55, 0.42, 0.28, 1.0))
    make_box("Clipboard_Sheet", (-1.0, 1.41, 0.7735), (0.210, 0.280, 0.002),
             (0.94, 0.93, 0.88, 1.0))
    make_box("Clipboard_Clip", (-1.0, 1.255, 0.782), (0.060, 0.030, 0.020), steel)
    make_cyl("Russell_Pen", (-0.94, 1.47, 0.7795), 0.005, 0.130,
             (0.24, 0.28, 0.52, 1.0), axis='Y', segments=6)
    # ── DIEGO'S PHONE · beside the clipboard ──
    make_box("Diegos_Phone", (-0.70, 1.70, 0.7655), (0.070, 0.140, 0.011),
             (0.13, 0.13, 0.15, 1.0))


def build_draft4_2026_09():
    """DRAFT 4 (2026-09-18, lore/_VISUAL_PROGRAM.md §3; 9 placements).
    The store had departments and no shift. WEAR: the entry path to the
    checkout and down both aisles; endcap kick scuffs; the belt's worn
    centre; the wet spot under the cone's warning; cart-wheel lines by
    the parked cart; the cooler door's floor arc. D3: the register and
    the card terminal on a cord to the floor box; the EXIT sign over
    the door and its conduit; the cooler wall's compressor grille at
    the base of the north wall; a floor drain under the cooler door.
    D5: the lot outside the storefront — asphalt, a curb, a parked car,
    the cart corral, a lamp post, the strip across the street.
    """
    from _props.detail import make_traffic_wear, make_floor_stain, make_scuff_band, make_far_bands
    from _props.vehicles import make_car
    tile_dk = (0.66, 0.66, 0.62, 1.0)
    # ── WEAR ──
    make_traffic_wear("Wear_Path_Entry_A", [(0.0, 0.5), (1.4, 1.2), (2.6, 1.75)], width=0.55, tint=tile_dk)
    make_traffic_wear("Wear_Path_B", [(-2.8, 2.0), (0.0, 2.0), (2.8, 2.05)], width=0.50, tint=tile_dk)
    make_traffic_wear("Wear_Path_C", [(-2.8, 4.6), (0.0, 4.6), (2.8, 4.6)], width=0.50, tint=tile_dk)
    for ei, ex in enumerate([-3.5, +3.5]):
        make_scuff_band(f"Wear_Kick_End_{ei}", (ex, ROOM_D/2.0 + 1.0 - 0.45), 0.9, axis='X', height=0.05, band_z=0.03, tint=(0.50, 0.50, 0.46, 1.0))
    make_box("Wear_Belt_Centre", (3.50, 1.75, 0.9616), (0.30, 1.50, 0.002), (0.20, 0.20, 0.22, 1.0))
    make_floor_stain("Wear_Wet_Spot", (1.55, 1.45), radius=0.22, tint=(0.70, 0.70, 0.68, 1.0), segments=10)
    for li, lx in enumerate((-1.80, -1.40)):
        make_box(f"Wear_Wheel_Line_{li}", (lx, 3.05, 0.004), (0.02, 1.10, 0.003), (0.60, 0.60, 0.56, 1.0))
    make_floor_stain("Wear_Arc_Cooler", (-3.55, 7.05), radius=0.30, tint=(0.68, 0.68, 0.64, 1.0), segments=10)
    # ── D3 ──
    make_box("Floor_Box", (4.10, 2.30, 0.02), (0.14, 0.14, 0.04), (0.42, 0.42, 0.40, 1.0))
    # each cord as straight segments: the recorder boxes a tube by its
    # whole path, and an L-run's box swallows the counter
    cord = (0.16, 0.16, 0.18, 1.0)
    make_tube("Cord_1_A", [(3.88, 2.45, 0.97), (4.02, 2.45, 0.97)], 0.006, cord, segments=4)   # from the register's back, ON the top (2026-09-22: inside the slab)
    make_tube("Cord_1_B", [(4.03, 2.45, 0.97), (4.03, 2.45, 0.03)], 0.006, cord, segments=4)
    make_tube("Cord_1_C", [(4.03, 2.45, 0.03), (4.05, 2.37, 0.03)], 0.006, cord, segments=4)
    # card-terminal cord: south around the belt, over the back edge,
    # along the floor around the cubby to the floor box (2026-09-22:
    # it ran inside the counter top and through the cubby)
    make_tube("Cord_2_A0", [(3.11, 0.90, 0.966), (3.11, 0.80, 0.966)], 0.006, cord, segments=4)
    make_tube("Cord_2_A", [(3.11, 0.80, 0.966), (4.01, 0.80, 0.966)], 0.006, cord, segments=4)
    make_tube("Cord_2_B", [(4.01, 0.80, 0.966), (4.01, 0.80, 0.03)], 0.006, cord, segments=4)
    make_tube("Cord_2_C", [(4.01, 0.80, 0.03), (4.36, 0.80, 0.03)], 0.006, cord, segments=4)
    make_tube("Cord_2_D", [(4.36, 0.80, 0.03), (4.36, 2.30, 0.03)], 0.006, cord, segments=4)
    make_tube("Cord_2_E", [(4.36, 2.30, 0.03), (4.17, 2.30, 0.03)], 0.006, cord, segments=4)
    make_box("Exit_Sign", (0.0, 0.14, CEIL - 0.42), (0.34, 0.06, 0.18), (0.94, 0.94, 0.90, 1.0))
    make_box("Exit_Sign_Letters", (0.0, 0.105, CEIL - 0.42), (0.24, 0.004, 0.10), (0.90, 0.16, 0.14, 1.0))
    make_tube("Exit_Sign_Conduit", [(0.0, 0.14, CEIL - 0.33), (0.0, 0.14, CEIL - 0.02)], 0.008, (0.62, 0.62, 0.60, 1.0), segments=5)
    make_box("Compressor_Grille", (-2.5, ROOM_D - 0.115, 0.18), (1.60, 0.03, 0.26), (0.30, 0.30, 0.32, 1.0))   # on the wall face (2026-09-22: inside the wall)
    for si in range(6):
        make_box(f"Compressor_Grille_Slat_{si}", (-2.5, ROOM_D - 0.13, 0.08 + si * 0.04), (1.50, 0.004, 0.012), (0.62, 0.62, 0.60, 1.0))
    make_lathe("Floor_Drain", (-3.2, 6.9, 0.0), [(0.0, 0.0), (0.08, 0.0), (0.09, 0.006), (0.0, 0.008)], (0.36, 0.36, 0.38, 1.0), segments=12)
    # ── D5 · the lot ──
    make_box("Lot_Asphalt", (0.0, -7.0, -0.06), (24.0, 13.0, 0.10), (0.26, 0.26, 0.27, 1.0))
    make_box("Lot_Walk", (0.0, -1.0, -0.03), (20.0, 1.8, 0.06), (0.62, 0.60, 0.56, 1.0))
    make_box("Lot_Curb", (0.0, -1.95, -0.05), (20.0, 0.12, 0.14), (0.55, 0.53, 0.50, 1.0))
    for si in range(6):
        make_box(f"Lot_Stripe_{si}", (-6.0 + si * 2.6, -4.6, -0.008), (0.10, 4.4, 0.006), (0.86, 0.84, 0.72, 1.0))
    make_car("Lot_Car", -3.6, -4.9, 4.5, (0.60, 0.60, 0.62, 1.0), along="Y", z0=-0.01)
    for ci, cx2 in enumerate((4.2, 6.4)):
        make_tube(f"Corral_Rail_{ci}", [(cx2, -3.2, 0.02), (cx2, -3.2, 0.95), (cx2, -6.2, 0.95), (cx2, -6.2, 0.02)], 0.02, (0.62, 0.62, 0.60, 1.0), segments=6)
    make_box("Corral_Sign", (5.3, -6.25, 1.12), (2.24, 0.04, 0.30), (0.32, 0.62, 0.42, 1.0))   # on the rails, rail to rail (2026-09-22: 23 cm over them, 0.5 m short of each)
    make_lathe("Lot_Lamp_Post", (8.5, -4.0, 0.0), [(0.16, 0.0), (0.10, 0.10), (0.07, 5.8), (0.08, 6.0), (0.0, 6.0)], (0.30, 0.30, 0.32, 1.0), segments=8)
    make_box("Lot_Lamp_Head", (8.5, -4.0, 6.05), (0.70, 0.30, 0.16), (0.30, 0.30, 0.32, 1.0))
    make_far_bands("Far", (0.46, 0.44, 0.42, 1.0), [(18.0, 20.0, 5.0, 0.85), (26.0, 26.0, 7.0, 0.7)], sides="S", cy=0.0, profile="roofline")


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
    build_departments()
    build_hero_props_2026_09()
    build_draft4_2026_09()
    out = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)),
        "../../../assets/3d/locales/centro_grocery_aisle.glb"))
    print(f"\n[build_centro_grocery_aisle] exporting to {out}")
    export_glb(out)

if __name__ == "__main__":
    main()
