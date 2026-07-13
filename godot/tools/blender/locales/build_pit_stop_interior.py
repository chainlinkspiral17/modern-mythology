"""pit_stop_interior — vol5-7 convenience-store / gas-station shop.

Was near-empty (walls + two aisles + a lone register). Enriched to
real convenience-store density: a reach-in cooler wall of drinks, a
coffee + roller-grill + hot-case station, a full checkout counter
(bullnose, register, card terminal, impulse candy rack, tobacco rack
+ lottery behind), snack gondolas + endcaps, a soda-bottle pyramid,
a chip pegboard, front windows with sale posters, and lived-in decor
(clock, calendar, plant, trash can, floor mat, banner, crown).

Room: door/S wall at blender y=0, extends +Y; interior lands at
godot -Z. All props kept inside the 7.0 x 6.0 footprint.
"""
import os, sys
_BT = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
if _BT not in sys.path: sys.path.insert(0, _BT)
from _props import palette as P
from _props.geometry import clear_scene, make_box, make_cyl, export_glb
from _props.structure import make_floor, make_wall, make_ceiling, make_crown_molding, make_window
from _props.store_fixtures import (make_counter, make_counter_bullnose, make_register,
                                   make_cigarette_rack, make_lottery_display,
                                   make_credit_card_terminal)
from _props.shelving import make_snack_aisle, make_endcap, make_pegboard_chip_rack
from _props.food_service import (make_coffee_pots, make_taquito_roller, make_hot_food_case,
                                 make_paper_cup_stack, make_sugar_creamer_caddy)
from _props.coolers_drinks import make_cooler_row, make_soda_bottle_pyramid
from _props.cleaning import make_trash_can
from _props.decor import (make_wall_clock, make_floor_plant, make_faded_poster,
                          make_calendar, make_air_freshener_tree)
from _props.signage import make_hanging_banner
from _props.safety import (make_smoke_detector, make_hvac_vent,
                           make_fluorescent_tube_fixture, make_security_camera)

ROOM_W = 7.0; ROOM_D = 6.0; CEIL = 2.8
PAL_WALL = {"wall":(0.88,0.88,0.86,1.0),"baseboard":(0.42,0.42,0.40,1.0)}
COL_FLOOR = (0.78,0.78,0.74,1.0); COL_SEAM = (0.42,0.42,0.40,1.0); COL_WOOD = (0.62,0.62,0.60,1.0)
COL_ACCENT = (0.32,0.62,0.42,1.0)

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
    for nm, ax, length, wx, wy in [
            ("Crown_W", 'Y', ROOM_D, -ROOM_W/2.0+0.10, ROOM_D/2.0),
            ("Crown_E", 'Y', ROOM_D, +ROOM_W/2.0-0.10, ROOM_D/2.0),
            ("Crown_N", 'X', ROOM_W, 0.0, ROOM_D-0.10)]:
        make_crown_molding(nm, wall_x=wx, wall_y=wy, length=length, axis=ax, ceil_z=CEIL, palette={"wood": COL_WOOD})

def build_windows():
    # Storefront glass in the two south wall segments, with taped sale
    # posters (thin-Y bright rectangles facing into the room).
    for tag, wx in [("SW", -2.25), ("SE", 2.25)]:
        make_window(f"Win_{tag}", (wx, 0.10, 1.55), width=1.80, height=1.40)
        for pi, (dx, dz, col) in enumerate([
                (-0.55, 1.85, (0.94, 0.28, 0.22, 1.0)),
                (0.55, 1.20, (0.98, 0.84, 0.30, 1.0))]):
            make_box(f"WinPoster_{tag}_{pi}", (wx+dx, 0.14, dz), (0.42, 0.006, 0.30), col)

def build_cooler_wall():
    # Reach-in beverage cooler bank along the north wall.
    make_cooler_row("Cooler", 5.4, [-1.9, 0.3, 2.5], cz=1.30,
                    shelves=5, cans_per_shelf=6, sixpacks_per_shelf=4)
    # Brand banner mounted above the coolers.
    make_hanging_banner("CoolBanner", (0.3, 5.2, CEIL), width=2.60, height=0.34,
                        bg_color=(0.20, 0.42, 0.66, 1.0))

def build_aisles():
    for ai, ay in enumerate([2.4, 3.9]):
        make_snack_aisle(f"Aisle_{ai}", (0.0, ay, 0.0), length=4.4, shelf_count=5)
    # Endcaps at the west mouth of each aisle.
    for ei, ay in enumerate([2.4, 3.9]):
        make_endcap(f"EndCap_{ei}", (-2.6, ay, 0.0),
                    palette={"header": COL_ACCENT})

def build_coffee_station():
    # West-wall counter carrying the drip-coffee + hot-food line.
    cx = -2.95
    top_z = make_counter("Coffee", (cx, 4.3, 0.0), length=2.20, depth=0.70, height=0.90,
                         palette={"formica": (0.74, 0.70, 0.64, 1.0),
                                  "top": (0.24, 0.24, 0.26, 1.0),
                                  "kick": (0.24, 0.24, 0.26, 1.0)})
    make_coffee_pots("CoffeePots", (cx+0.05, 4.3, top_z), pots=3)
    make_paper_cup_stack("CupStack", (cx+0.05, 3.5, top_z), count=16)
    make_sugar_creamer_caddy("SugarCaddy", (cx+0.05, 5.2, top_z))
    make_hot_food_case("HotCase", (cx+0.02, 3.4, top_z+0.30), hot_items=4)
    # Roller grill on the counter's north end (taquitos / dogs).
    make_taquito_roller("Roller", (cx+0.05, 5.0, top_z+0.14), count=3)

def build_checkout():
    # Front-east checkout so the clerk sees the door.
    cx, cy = 2.30, 1.65
    top_z = make_counter("Register", (cx, cy, 0.0), length=2.40, depth=1.00, height=0.95,
                         palette={"formica": COL_WOOD, "top": (0.18, 0.14, 0.16, 1.0),
                                  "kick": (0.18, 0.14, 0.16, 1.0)})
    make_counter_bullnose("Register", (cx-0.55, cy, top_z), length=2.40,
                          palette={"top": (0.18, 0.14, 0.16, 1.0)})
    make_register("RegisterMachine", (cx+0.10, cy-0.30, top_z))
    make_credit_card_terminal("CardTerm", (cx-0.30, cy+0.60, top_z))
    make_air_freshener_tree("Fresheners", (cx+0.05, cy+0.85, top_z+0.60))
    # Impulse candy rack on the customer face of the counter.
    for ri in range(3):
        rz = top_z - 0.18 - ri * 0.26
        make_box(f"ImpulseShelf_{ri}", (cx-0.52, cy, rz), (0.06, 2.20, 0.03), P.METAL_STEEL)
        for ci in range(8):
            tint = P.SNACK_TINTS[(ri + ci) % len(P.SNACK_TINTS)]
            make_box(f"ImpulseBar_{ri}_{ci}", (cx-0.55, cy-0.95+ci*0.27, rz+0.08),
                     (0.05, 0.16, 0.14), tint)
    # Tobacco rack + lottery on the east wall behind the clerk.
    make_cigarette_rack("Cigs", (ROOM_W/2.0-0.12, cy, 1.20),
                        shelves=3, columns=10, col_span=0.24)
    make_lottery_display("Lotto", (ROOM_W/2.0-0.12, cy+1.6, 1.30))

def build_grab_and_go():
    # Soda-bottle pyramid display near the entrance + a chip pegboard.
    make_soda_bottle_pyramid("SodaPyr", (-1.5, 0.9, 0.60), tiers=3, base_count=4)
    make_pegboard_chip_rack("Chips", (-ROOM_W/2.0+0.06, 1.6, 1.50), rows=3, cols=4)

def build_decor():
    make_wall_clock("Clock", (0.0, ROOM_D-0.11, CEIL-0.55), frozen_hour=7, frozen_min=42)
    make_calendar("Calendar", (-ROOM_W/2.0+0.13, 4.3, 1.80))
    make_faded_poster("Poster_E", (ROOM_W/2.0-0.05, 4.6, 1.60))
    make_floor_plant("Plant", (-ROOM_W/2.0+0.5, 5.5, 0.0))
    make_trash_can("Trash", (1.0, 0.7, 0.0), branded=False,
                   palette={"body": (0.30, 0.30, 0.32, 1.0)})
    # Rubber entry mat at the door.
    make_box("FloorMat", (0.0, 0.7, 0.02), (1.60, 1.00, 0.02), P.RUBBER_MAT)

def build_ceiling_infra():
    for j, ypos in enumerate([1.6, 3.2, 4.8]):
        make_fluorescent_tube_fixture(f"Fluor_{j}", (0.0, ypos, CEIL), length=1.60, width=0.36)
    make_smoke_detector("Smoke", (-1.5, ROOM_D/2.0, CEIL))
    make_hvac_vent("HVAC", (1.5, ROOM_D-0.6, CEIL), width=0.80, depth=0.40)
    make_security_camera("SecCam", (2.6, 1.0, CEIL))

def main():
    clear_scene()
    build_shell()
    build_windows()
    build_cooler_wall()
    build_aisles()
    build_coffee_station()
    build_checkout()
    build_grab_and_go()
    build_decor()
    build_ceiling_infra()
    out = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)),
        "../../../assets/3d/locales/pit_stop_interior.glb"))
    print(f"\n[build_pit_stop_interior] exporting to {out}")
    export_glb(out)

if __name__ == "__main__":
    main()
