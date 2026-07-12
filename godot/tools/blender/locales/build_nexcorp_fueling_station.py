"""nexcorp_fueling_station — vol5-7 locale (auto-generated placement script)."""
import os, sys
_BT = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
if _BT not in sys.path: sys.path.insert(0, _BT)
from _props import palette as P
from _props.geometry import clear_scene, make_box, make_cyl, export_glb
from _props.structure import make_floor, make_wall, make_ceiling, make_crown_molding, make_window
from _props.store_fixtures import make_counter, make_counter_bullnose, make_register
from _props.shelving import make_snack_aisle, make_endcap
from _props.food_service import make_coffee_pots
from _props.decor import make_wall_clock, make_floor_plant, make_faded_poster, make_calendar
from _props.safety import make_smoke_detector, make_hvac_vent, make_fluorescent_tube_fixture

ROOM_W = 8.0; ROOM_D = 6.0; CEIL = 2.8
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

def build_register_counter():
    top_z = make_counter("Register", (ROOM_W/4.0, ROOM_D-1.5, 0.0), length=2.40, depth=1.00, height=0.95,
                         palette={"formica": COL_WOOD, "top": (0.18, 0.12, 0.20, 1.0), "kick": (0.18, 0.12, 0.20, 1.0)})
    make_register("RegisterMachine", (ROOM_W/4.0, ROOM_D-1.5-0.30, top_z))

def build_endcaps():
    for ei, ex in enumerate([-3.0, +3.0]):
        make_endcap(f"EndCap_{ei}", (ex, ROOM_D/2.0+1.0, 0.0))

def build_ceiling_infra():
    for j in range(2):
        ypos = ROOM_D * (0.30 + j * 0.40)
        make_fluorescent_tube_fixture(f"Fluor_{j}", (0.0, ypos, CEIL), length=1.40, width=0.34)
    make_smoke_detector("Smoke", (0.0, ROOM_D/2.0, CEIL))

def build_coolers():
    # Reach-in glass-door fridge bank along the east wall
    cx = ROOM_W/2.0 - 0.4
    for i in range(3):
        cy = 1.6 + i*1.4
        make_box(f"Cooler_{i}_Body", (cx, cy, 1.05), (0.70, 1.30, 2.10), (0.80, 0.82, 0.86, 1.0))
        make_box(f"Cooler_{i}_Glass", (cx-0.34, cy, 1.15), (0.03, 1.20, 1.70), (0.72, 0.86, 0.94, 0.45))
        for r in range(4):
            for c in range(4):
                make_box(f"Cooler_{i}_Can_{r}_{c}", (cx-0.20, cy-0.5+c*0.32, 0.55+r*0.42),
                         (0.14, 0.10, 0.16), P.SNACK_TINTS[(i+r+c) % len(P.SNACK_TINTS)])

def build_aisles():
    for ai in range(2):
        make_snack_aisle(f"Aisle_{ai}", (-1.2, 1.8+ai*1.6, 0.0), length=3.0, shelf_count=4)

def build_coffee_hotcase():
    # Coffee station on a short NW counter
    make_box("CoffeeCounter", (-ROOM_W/2.0+0.9, ROOM_D-1.0, 0.45), (1.40, 0.60, 0.90), COL_WOOD)
    make_coffee_pots("Coffee", (-ROOM_W/2.0+0.9, ROOM_D-1.0, 0.94), pots=2)
    # Roller-grill hot case on the register counter
    hx = ROOM_W/4.0
    make_box("HotCase", (hx-0.7, ROOM_D-1.5, 1.08), (0.50, 0.40, 0.30), (0.86, 0.72, 0.34, 1.0))
    for ri in range(4):
        make_cyl(f"Roller_{ri}", (hx-0.85+ri*0.10, ROOM_D-1.5, 1.18), 0.03, 0.34, (0.62, 0.42, 0.28, 1.0), axis='Y', segments=8)

def build_storefront():
    # West-wall storefront window + a fuel-pump island and canopy beyond
    # the glass — the beat that says "fueling station."
    wx = -ROOM_W/2.0
    make_box("Storefront_Frame", (wx+0.04, ROOM_D/2.0, 1.40), (0.06, 2.60, 1.80), P.METAL_STEEL)
    make_box("Storefront_Glass", (wx+0.06, ROOM_D/2.0, 1.40), (0.02, 2.40, 1.60), (0.66, 0.78, 0.86, 0.40))
    px = wx - 1.6
    make_box("PumpIsland_Base", (px, ROOM_D/2.0, 0.10), (1.20, 2.00, 0.20), (0.36, 0.36, 0.38, 1.0))
    for pi, py in enumerate([ROOM_D/2.0-0.7, ROOM_D/2.0+0.7]):
        make_box(f"Pump_{pi}_Body", (px, py, 0.85), (0.40, 0.50, 1.40), (0.86, 0.28, 0.24, 1.0))
        make_box(f"Pump_{pi}_Screen", (px-0.22, py, 1.15), (0.02, 0.34, 0.30), (0.12, 0.16, 0.20, 1.0))
        make_cyl(f"Pump_{pi}_Hose", (px-0.24, py+0.28, 0.90), 0.02, 0.50, P.METAL_BLACK)
    make_box("Canopy_Beam", (px, ROOM_D/2.0, 3.20), (1.60, 2.60, 0.30), (0.90, 0.90, 0.92, 1.0))
    for ci, cy in enumerate([ROOM_D/2.0-0.9, ROOM_D/2.0+0.9]):
        make_cyl(f"Canopy_Post_{ci}", (px+0.5, cy, 1.70), 0.08, 3.00, P.METAL_STEEL, segments=8)

def build_brand_and_register():
    # Backlit brand sign on the north wall behind the register
    make_box("BrandSign", (ROOM_W/4.0, ROOM_D-0.06, 2.10), (1.60, 0.06, 0.50), COL_ACCENT)
    # Impulse-buy rack in front of the register counter
    for r in range(3):
        for c in range(5):
            make_box(f"Impulse_{r}_{c}", (ROOM_W/4.0-0.72+c*0.36, ROOM_D-1.5-0.62, 0.62+r*0.22),
                     (0.14, 0.03, 0.16), P.SNACK_TINTS[(r+c) % len(P.SNACK_TINTS)])

def main():
    clear_scene()
    build_shell()
    build_register_counter()
    build_endcaps()
    build_coolers()
    build_aisles()
    build_coffee_hotcase()
    build_storefront()
    build_brand_and_register()
    build_ceiling_infra()
    out = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)),
        "../../../assets/3d/locales/nexcorp_fueling_station.glb"))
    print(f"\n[build_nexcorp_fueling_station] exporting to {out}")
    export_glb(out)

if __name__ == "__main__":
    main()
