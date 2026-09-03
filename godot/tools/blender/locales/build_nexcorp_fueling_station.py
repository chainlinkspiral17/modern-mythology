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
COL_ACCENT = (0.18,0.32,0.50,1.0)  # NexCorp navy — a bruise that doesn't know it's a bruise yet

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
    # make_counter's `depth` is the X extent, `length` the Y —
    # so length>depth built this counter ROTATED 90 DEGREES:
    # a narrow face against the wall and the run jutting into
    # the room. Swapped 2026-08-12 (same bug as the New
    # Orleans bar and the pit stop's lunch counter).
    top_z = make_counter("Register", (ROOM_W/4.0, ROOM_D-1.5, 0.0), length=1.00, depth=2.40, height=0.95,
                         palette={"formica": COL_WOOD, "top": (0.18, 0.12, 0.20, 1.0), "kick": (0.18, 0.12, 0.20, 1.0)})
    make_register("RegisterMachine", (ROOM_W/4.0, ROOM_D-1.5-0.30, top_z))

def build_endcaps():
    for ei, ex in enumerate([-3.0, +3.0]):
        # y+1.0 put endcap 1 inside the register counter (which
        # spans x 0.8-3.2 at y 4.0-5.0). Endcaps flank the aisle
        # mouth, forward of the register.
        make_endcap(f"EndCap_{ei}", (ex, ROOM_D/2.0 - 0.9, 0.0))

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
    # SIX pumps on three islands, navy-branded — "The unmarked van
    # is at pump six" needs a pump six to be at
    for isl, px in enumerate((wx - 1.6, wx - 3.4, wx - 5.2)):
        make_box(f"PumpIsland_{isl}_Base", (px, ROOM_D/2.0, 0.10), (1.20, 2.00, 0.20), (0.36, 0.36, 0.38, 1.0))
        for pi, py in enumerate([ROOM_D/2.0-0.7, ROOM_D/2.0+0.7]):
            n = isl * 2 + pi
            make_box(f"Pump_{n}_Body", (px, py, 0.85), (0.40, 0.50, 1.40), COL_ACCENT)
            make_box(f"Pump_{n}_Screen", (px-0.22, py, 1.15), (0.02, 0.34, 0.30), (0.12, 0.16, 0.20, 1.0))
            make_box(f"Pump_{n}_NumTag", (px-0.22, py, 1.52), (0.015, 0.14, 0.14), (0.90, 0.90, 0.92, 1.0))
            make_cyl(f"Pump_{n}_Hose", (px-0.24, py+0.28, 0.90), 0.02, 0.50, P.METAL_BLACK)
    make_box("Canopy_Beam", (wx - 3.4, ROOM_D/2.0, 3.20), (5.4, 2.60, 0.30), (0.90, 0.90, 0.92, 1.0))
    make_box("Canopy_Trim", (wx - 3.4, ROOM_D/2.0, 3.02), (5.5, 2.70, 0.08), COL_ACCENT)
    for ci, (cx2, cy) in enumerate([(wx-1.1, ROOM_D/2.0-0.9), (wx-1.1, ROOM_D/2.0+0.9),
                                     (wx-5.7, ROOM_D/2.0-0.9), (wx-5.7, ROOM_D/2.0+0.9)]):
        make_cyl(f"Canopy_Post_{ci}", (cx2, cy, 1.70), 0.08, 3.00, P.METAL_STEEL, segments=8)
    # No-smoking placard + waste bin at the island end
    make_box("NoSmoking_Placard", (wx-1.6, ROOM_D/2.0-1.15, 1.60), (0.04, 0.26, 0.20), (0.90, 0.90, 0.92, 1.0))
    make_box("NoSmoking_Bar", (wx-1.6, ROOM_D/2.0-1.16, 1.60), (0.03, 0.22, 0.04), (0.72, 0.20, 0.18, 1.0))
    make_cyl("Pump_Bin", (wx-1.0, ROOM_D/2.0-1.3, 0.40), 0.20, 0.80, (0.30, 0.32, 0.34, 1.0), segments=10)

def build_brand_and_register():
    # Backlit brand sign on the north wall behind the register
    make_box("BrandSign", (ROOM_W/4.0, ROOM_D-0.06, 2.10), (1.60, 0.06, 0.50), COL_ACCENT)
    # Impulse-buy rack in front of the register counter
    for r in range(3):
        for c in range(5):
            make_box(f"Impulse_{r}_{c}", (ROOM_W/4.0-0.72+c*0.36, ROOM_D-1.5-0.62, 0.62+r*0.22),
                     (0.14, 0.03, 0.16), P.SNACK_TINTS[(r+c) % len(P.SNACK_TINTS)])

def build_hero_props():
    """2026-08-03 hero-prop pass: the restroom (Boyd's whole "Nine
    Minutes" scene — and the Demon in the plumbing), the entry door,
    the dumpster Vince's sedan waits near, the vape back-bar, the
    security dome, the pole sign."""
    # Restroom alcove off the N wall: door, tiled wall, toilet, pipe
    make_box("Restroom_Door", (-2.4, ROOM_D-0.05, 1.03), (0.80, 0.06, 2.05), (0.62, 0.60, 0.56, 1.0))
    make_box("Restroom_Plaque", (-2.4, ROOM_D-0.09, 1.75), (0.22, 0.02, 0.10), (0.30, 0.34, 0.44, 1.0))
    # Alcove built as an attached box behind the wall
    make_box("Restroom_Shell", (-2.4, ROOM_D+0.85, 1.20), (2.0, 1.7, 2.40), (0.66, 0.68, 0.66, 1.0))
    make_box("Restroom_Tile", (-2.4, ROOM_D+1.62, 1.10), (1.8, 0.05, 2.0), (0.78, 0.82, 0.80, 1.0))
    make_box("Restroom_Toilet_Base", (-2.4, ROOM_D+1.25, 0.22), (0.40, 0.55, 0.44), (0.90, 0.90, 0.88, 1.0))
    make_box("Restroom_Toilet_Tank", (-2.4, ROOM_D+1.50, 0.62), (0.42, 0.18, 0.40), (0.90, 0.90, 0.88, 1.0))
    make_cyl("Restroom_Sink", (-1.7, ROOM_D+1.35, 0.80), 0.18, 0.10, (0.90, 0.90, 0.88, 1.0), segments=10)
    # The plumbing run (something for the plumbing-class Demon to
    # live in): exposed pipe from the restroom down the back wall
    make_cyl("Plumbing_Run", (-1.2, ROOM_D-0.10, 1.9), 0.035, 2.6, (0.52, 0.50, 0.46, 1.0), axis='X', segments=8)
    # Entry door leaf with push-bar
    make_box("Entry_Door", (0.0, 0.03, 1.02), (1.90, 0.04, 2.04), (0.30, 0.30, 0.34, 1.0))
    make_box("Entry_Door_Glass", (0.0, 0.02, 1.20), (1.50, 0.02, 1.55), (0.66, 0.78, 0.86, 0.4))
    make_box("Entry_PushBar", (0.0, 0.06, 1.05), (1.30, 0.03, 0.06), (0.60, 0.62, 0.64, 1.0))
    # Dumpster on the lot side away from the pumps
    make_box("Dumpster", (5.2, 7.6, 0.60), (1.80, 1.20, 1.20), (0.24, 0.36, 0.30, 1.0))
    make_box("Dumpster_Lid", (5.2, 7.6, 1.24), (1.84, 1.24, 0.08), (0.20, 0.30, 0.26, 1.0))
    # Vape/cig back-bar behind the register
    make_box("Vape_Backbar", (ROOM_W/4.0, ROOM_D-0.25, 1.75), (1.80, 0.30, 0.70), (0.30, 0.30, 0.34, 1.0))
    for r in range(2):
        for c in range(6):
            make_box(f"Vape_Pack_{r}_{c}", (ROOM_W/4.0-0.75+c*0.30, ROOM_D-0.38, 1.55+r*0.32),
                     (0.14, 0.03, 0.18), P.SNACK_TINTS[(r*3+c) % len(P.SNACK_TINTS)])
    # Security dome covering register + door line
    make_cyl("Security_Dome", (0.0, 5.7, 2.72), 0.10, 0.08, (0.16, 0.16, 0.20, 1.0), segments=10)
    # Fuel-price pole sign out west
    make_cyl("Price_Pole", (-9.0, 1.0, 2.5), 0.12, 5.0, P.METAL_STEEL, segments=8)
    make_box("Price_Sign", (-9.0, 1.0, 5.4), (0.15, 1.6, 1.4), COL_ACCENT)
    for di in range(3):
        make_box(f"Price_Digits_{di}", (-8.91, 1.0, 5.75 - di * 0.40), (0.02, 1.2, 0.26), (0.94, 0.94, 0.90, 1.0))


def build_hero_props_2026_09():
    """HERO PROPS FOR THE BLIND CUES (shot_marker_audit, 2026-09-01).

    Three cues, none with geometry:
    - BOYD'S PHONE ("He calls his handler. The handler does not
      pick up."): face-up on the register counter.
    - THE BADGE + THE CASH: Doyle's NAPD courtesy badge ("a small
      leather wallet with a New Auburn shield") and the three
      hundred-dollar bills she hands him — both on the dash of
      Doyle's dark sedan, parked on a new forecourt pad south of
      the canopy, hollow-bodied so the dash reads through the
      windshield.
    """
    dark = (0.16, 0.17, 0.20, 1.0)
    make_box("Boyds_Phone", (1.5, 4.55, 1.0055), (0.070, 0.140, 0.011), (0.13, 0.13, 0.15, 1.0))
    # ── Doyle's sedan · forecourt pad south of the canopy ──
    make_box("Forecourt_Pad", (-6.25, 0.2, -0.03), (6.0, 3.0, 0.05), (0.40, 0.40, 0.41, 1.0))
    make_box("Doyle_Sedan_Pan", (-6.25, 0.2, 0.40), (4.40, 1.80, 0.10), dark)
    make_box("Doyle_Sedan_Side_S", (-6.25, -0.67, 0.72), (4.40, 0.06, 0.55), dark)
    make_box("Doyle_Sedan_Side_N", (-6.25, 1.07, 0.72), (4.40, 0.06, 0.55), dark)
    make_box("Doyle_Sedan_Hood", (-4.6, 0.2, 0.75), (1.10, 1.68, 0.60), dark)
    make_box("Doyle_Sedan_Trunk", (-7.9, 0.2, 0.75), (1.10, 1.68, 0.60), dark)
    make_box("Doyle_Sedan_Roof", (-6.25, 0.2, 1.43), (2.20, 1.80, 0.06), dark)
    make_box("Doyle_Sedan_Windshield", (-5.13, 0.2, 1.22), (0.04, 1.60, 0.36), (0.60, 0.70, 0.76, 0.35))
    make_box("Doyle_Sedan_Dash", (-5.3, 0.2, 0.98), (0.30, 1.60, 0.06), (0.12, 0.12, 0.13, 1.0))
    for wi, (wx, wy) in enumerate(((-7.45, -0.795), (-5.05, -0.795), (-7.45, 1.195), (-5.05, 1.195))):
        make_cyl(f"Doyle_Sedan_Wheel_{wi}", (wx, wy, 0.32), 0.32, 0.25, (0.12, 0.12, 0.13, 1.0), axis='Y', segments=10)
    # THE BADGE · open leather wallet on the dash, shield inside
    make_box("Courtesy_Badge_Wallet", (-5.3, 0.55, 1.014), (0.11, 0.08, 0.008), (0.30, 0.20, 0.14, 1.0))
    make_box("Courtesy_Badge_Shield", (-5.3, 0.57, 1.0195), (0.035, 0.035, 0.003), (0.72, 0.60, 0.30, 1.0))
    # THE CASH · three hundreds, fanned on the dash
    for bi, (dx, dy) in enumerate(((0.0, 0.0), (0.012, -0.014), (0.024, -0.028))):
        make_box(f"Cash_Bill_{bi}", (-5.30 + dx, -0.30 + dy, 1.0115 + bi * 0.0012), (0.156, 0.066, 0.001), (0.62, 0.68, 0.56, 1.0))


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
    build_hero_props()
    build_hero_props_2026_09()
    out = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)),
        "../../../assets/3d/locales/nexcorp_fueling_station.glb"))
    print(f"\n[build_nexcorp_fueling_station] exporting to {out}")
    export_glb(out)

if __name__ == "__main__":
    main()
