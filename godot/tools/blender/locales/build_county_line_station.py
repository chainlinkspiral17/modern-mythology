"""county_line_station — the gas station at the county line (vol5 ch18 "The Moon").

NEW SET (2026-10-10). The scene played in Miriam's Subaru. The prose:

  "They reached the county line at seven fifty-two AM. Miriam pulled into
  a gas station just past the sign. She got out, stretched, filled the
  tank, came back." · "She stood at the edge of the gas station parking
  lot and watched the Subaru pull out, turn west, cross the overpass, and
  disappear." · "The crow landed, instead, on the traffic light above the
  gas-station exit." · "Then she went inside the gas station. Bought
  coffee. Sat on the metal bench beside the ice machine. Waited for the
  eight-thirty bus."

A two-island country station on a Louisiana parish road, the morning of
a Tuesday in spring:
  · THE FORECOURT: an unbranded red-and-white canopy over two islands,
    the Subaru at the near pump with its filler door open, the lot.
  · THE STORE: a low block building, its glass front, the ICE machine
    against it and THE METAL BENCH beside the ice machine, the propane
    cage, the bus-stop sign at the lot's edge.
  · THE EXIT: the station's exit onto the road, the traffic light on its
    mast arm above it with THE CROW on the arm.
  · THE ROAD: two lanes past the station, climbing west to the OVERPASS
    over the bayou; the parish-line sign at the lot's east end.
  · THE BAYOU: the water and its cypress along the south, the treeline
    north, the morning haze.

Coordinate frame: Blender Z-up. The road runs along x at y = +14 (north
of the lot); the overpass climbs to the west (−x); the store's front at
y = −6, facing north onto the lot. glTF export remaps to Godot (x, z, −y).

Draft 2 targets: the eight-thirty bus coming in from the west; the
Subaru's open filler door and the hose in it; the sign's parish name once
the prose gives one.
"""
import math
import os
import random
import sys
_BT = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
if _BT not in sys.path: sys.path.insert(0, _BT)
from _props.geometry import clear_scene, make_box, make_cyl, make_rot_box, make_blob, export_glb
from _props.vehicles import make_car
from _props.creatures import make_crow

ROAD_Y = 14.0
STORE_Y = -6.0                  # the store's front wall (faces +y, the lot)
ISLANDS = (-6.0, 2.0)
CANOPY_Z = 4.8

COL_ASPHALT = (0.30, 0.30, 0.31, 1.0)
COL_CONCRETE = (0.70, 0.69, 0.66, 1.0)
COL_WHITE = (0.92, 0.92, 0.90, 1.0)
COL_RED = (0.72, 0.16, 0.14, 1.0)
COL_BLOCK = (0.78, 0.74, 0.64, 1.0)       # painted block
COL_DARK = (0.16, 0.16, 0.18, 1.0)
COL_STEEL = (0.66, 0.68, 0.70, 1.0)
COL_GLASS = (0.70, 0.78, 0.82, 0.30)
COL_GRASS = (0.40, 0.50, 0.28, 1.0)
COL_WATER = (0.26, 0.32, 0.26, 1.0)
COL_CYPRESS = (0.30, 0.42, 0.26, 1.0)
COL_SUBARU = (0.16, 0.27, 0.21, 1.0)      # Miriam's dark green Subaru, immaculate (build_miriam_subaru.SUBARU)


def build_ground():
    make_box("Ground_Grass", (0.0, 0.0, -0.07), (400.0, 300.0, 0.06), COL_GRASS)
    make_box("Lot_Asphalt", (0.0, 3.0, -0.03), (40.0, 18.0, 0.06), COL_ASPHALT)
    make_box("Lot_Apron_Exit", (14.0, 11.0, -0.028), (8.0, 6.0, 0.06), COL_ASPHALT)
    # the road past the lot, and its climb to the overpass in the west
    make_box("Road_Parish", (20.0, ROAD_Y, -0.025), (160.0, 8.0, 0.05), (0.26, 0.26, 0.27, 1.0))
    make_box("Road_Parish_Centerline", (20.0, ROAD_Y, 0.004), (160.0, 0.12, 0.01), (0.92, 0.80, 0.20, 1.0))
    rise, run = 6.0, 50.0
    ang = math.atan2(rise, run)
    L = math.hypot(run, rise)
    make_rot_box("Road_Overpass_Ramp", (-60.0 - run / 2.0, ROAD_Y, rise / 2.0 - 0.025), (L, 8.0, 0.05), (0.26, 0.26, 0.27, 1.0), pitch=ang)
    make_rot_box("Road_Overpass_Ramp_Fill", (-60.0 - run / 2.0, ROAD_Y, rise / 2.0 - 1.0), (L, 7.6, 1.90), (0.44, 0.40, 0.32, 1.0), pitch=ang)
    make_box("Road_Overpass_Deck", (-130.0, ROAD_Y, rise - 0.025), (40.0, 8.0, 0.05), (0.26, 0.26, 0.27, 1.0))
    make_box("Road_Overpass_Girder", (-130.0, ROAD_Y, rise - 0.60), (40.0, 8.4, 1.10), COL_CONCRETE)
    for k in range(3):
        make_box(f"Road_Overpass_Pier_{k}", (-120.0 - k * 10.0, ROAD_Y, (rise - 1.15) / 2.0), (1.2, 7.0, rise - 1.15), COL_CONCRETE)
    for e in (-1, 1):
        make_box(f"Road_Overpass_Rail_{e:+d}", (-130.0, ROAD_Y + e * 4.1, rise + 0.55), (40.0, 0.20, 1.10), COL_CONCRETE)
    # the bayou the overpass crosses, and the one along the south
    make_box("Bayou_Water_West", (-130.0, 0.0, -0.09), (24.0, 200.0, 0.04), COL_WATER)
    make_box("Bayou_Water_South", (0.0, -60.0, -0.09), (400.0, 40.0, 0.04), COL_WATER)
    rnd = random.Random(23)
    for k in range(26):
        tx = rnd.uniform(-150, 150); ty = rnd.uniform(-44, -34) if k % 2 else rnd.uniform(28, 44)
        h = rnd.uniform(9.0, 15.0)
        make_cyl(f"Cypress_{k}_Trunk", (tx, ty, h / 2.0), 0.35, h, (0.40, 0.34, 0.28, 1.0), segments=8)
        make_blob(f"Cypress_{k}_Crown", (tx, ty, h + 1.5), rnd.uniform(3.0, 4.5), COL_CYPRESS, noise=0.25, seed=400 + k, squash=0.9)
    # the parish-line sign at the lot's east end, and the bus-stop sign
    make_cyl("Parish_Sign_Post_0", (24.0, ROAD_Y - 5.6, 1.6), 0.06, 3.2, COL_STEEL, segments=6)
    make_cyl("Parish_Sign_Post_1", (26.2, ROAD_Y - 5.6, 1.6), 0.06, 3.2, COL_STEEL, segments=6)
    make_box("Parish_Sign", (25.1, ROAD_Y - 5.56, 2.6), (2.60, 0.04, 1.00), (0.16, 0.42, 0.26, 1.0))
    make_box("Parish_Sign_Text", (25.1, ROAD_Y - 5.535, 2.75), (2.0, 0.004, 0.24), COL_WHITE)
    make_box("Parish_Sign_Text_2", (25.1, ROAD_Y - 5.535, 2.40), (1.4, 0.004, 0.16), COL_WHITE)
    make_cyl("Bus_Stop_Sign_Post", (8.0, ROAD_Y - 5.2, 1.3), 0.03, 2.6, COL_STEEL, segments=6)
    make_box("Bus_Stop_Sign", (8.0, ROAD_Y - 5.17, 2.45), (0.40, 0.02, 0.50), (0.20, 0.36, 0.66, 1.0))


def build_forecourt():
    cy = 3.0
    make_box("Canopy_Deck", (-2.0, cy, CANOPY_Z + 0.30), (18.0, 10.0, 0.60), COL_WHITE)
    for e in (-1, 1):
        make_box(f"Canopy_Fascia_Band_{e:+d}", (-2.0, cy + e * 5.02, CANOPY_Z + 0.32), (18.0, 0.04, 0.40), COL_RED)
    for e in (-1, 1):
        make_box(f"Canopy_Fascia_Band_X{e:+d}", (-2.0 + e * 9.02, cy, CANOPY_Z + 0.32), (0.04, 10.0, 0.40), COL_RED)
    for k, ix in enumerate(ISLANDS):
        make_cyl(f"Canopy_Column_{k}", (ix, cy, (0.16 + CANOPY_Z) / 2.0), 0.22, CANOPY_Z - 0.16, COL_WHITE, segments=12)
        make_box(f"Canopy_Light_{k}", (ix + 2.5, cy, CANOPY_Z - 0.01), (1.2, 0.6, 0.02), (0.98, 0.98, 0.94, 1.0))
        make_box(f"Island_{k}_Curb", (ix, cy, 0.08), (1.20, 6.0, 0.16), COL_CONCRETE)
        for d, py in enumerate((cy - 1.6, cy + 1.6)):
            n = k * 2 + d + 1
            make_box(f"Pump_{n}_Body", (ix, py, 0.16 + 0.85), (0.70, 1.00, 1.70), COL_WHITE)
            make_box(f"Pump_{n}_Band", (ix, py, 0.16 + 1.55), (0.72, 1.02, 0.26), COL_RED)
            for s in (-1, 1):
                make_box(f"Pump_{n}_Display_{s:+d}", (ix + s * 0.352, py, 0.16 + 1.15), (0.004, 0.44, 0.28), (0.12, 0.14, 0.16, 1.0))
                make_box(f"Pump_{n}_Nozzle_{s:+d}", (ix + s * 0.39, py + 0.34, 0.16 + 0.90), (0.08, 0.06, 0.24), COL_DARK)
                make_cyl(f"Pump_{n}_Hose_{s:+d}", (ix + s * 0.38, py + 0.40, 0.16 + 0.50), 0.02, 0.76, COL_DARK, segments=6)
    # Miriam's Subaru at pump 1, nose west, Natalie's door toward the store
    make_car("Subaru_Wagon", ISLANDS[0] - 2.4, cy, 4.6, COL_SUBARU, along="Y", hatch=True)   # alongside the island, nose north


def build_store():
    x0, x1 = -4.0, 12.0
    d = 10.0
    cx = (x0 + x1) / 2.0
    make_box("Store_Block", (cx, STORE_Y - d / 2.0, 1.7), (x1 - x0, d, 3.4), COL_BLOCK)
    make_box("Store_Roof", (cx, STORE_Y - d / 2.0, 3.52), (x1 - x0 + 0.6, d + 0.6, 0.24), (0.42, 0.42, 0.44, 1.0))
    make_box("Store_Parapet_Band", (cx, STORE_Y + 0.02, 3.2), (x1 - x0, 0.04, 0.44), COL_RED)
    make_box("Store_Front_Glass", (cx - 1.0, STORE_Y + 0.01, 1.45), (7.0, 0.01, 2.40), COL_GLASS)
    for m in range(5):
        make_box(f"Store_Front_Mullion_{m}", (cx - 1.0 - 3.5 + m * 1.75, STORE_Y + 0.02, 1.45), (0.06, 0.08, 2.40), COL_DARK)
    make_box("Store_Door", (cx + 3.6, STORE_Y + 0.03, 1.15), (0.92, 0.04, 2.30), COL_DARK)
    make_box("Store_Door_Glass", (cx + 3.6, STORE_Y + 0.035, 1.2), (0.76, 0.01, 2.0), COL_GLASS)
    make_box("Store_Walk", (cx, STORE_Y + 1.0, 0.03), (x1 - x0 + 2.0, 2.0, 0.06), COL_CONCRETE)
    # the ICE machine against the front, THE METAL BENCH beside it
    make_box("Ice_Machine", (x0 + 1.4, STORE_Y + 0.46, 0.06 + 0.95), (1.40, 0.80, 1.90), COL_WHITE)
    make_box("Ice_Machine_Band", (x0 + 1.4, STORE_Y + 0.862, 0.06 + 1.30), (1.30, 0.004, 0.40), (0.20, 0.50, 0.80, 1.0))
    make_box("Ice_Machine_Door_Seam", (x0 + 1.4, STORE_Y + 0.862, 0.06 + 0.70), (0.02, 0.004, 1.20), COL_DARK)
    bx = x0 + 3.2
    make_box("Metal_Bench_Seat", (bx, STORE_Y + 0.50, 0.06 + 0.45), (1.60, 0.40, 0.04), COL_STEEL)
    for k in range(5):
        make_box(f"Metal_Bench_Slat_{k}", (bx, STORE_Y + 0.33 + k * 0.085, 0.06 + 0.472), (1.56, 0.06, 0.006), (0.56, 0.58, 0.60, 1.0))
    make_box("Metal_Bench_Back", (bx, STORE_Y + 0.31, 0.06 + 0.47 + 0.22), (1.60, 0.04, 0.44), COL_STEEL)   # standing on the seat's back edge
    for e in (-1, 1):
        make_box(f"Metal_Bench_Leg_{e:+d}", (bx + e * 0.72, STORE_Y + 0.48, 0.06 + 0.215), (0.05, 0.36, 0.43), COL_STEEL)
    make_cyl("Bench_Coffee_Cup", (bx + 0.55, STORE_Y + 0.50, 0.06 + 0.47 + 0.06), 0.04, 0.12, COL_WHITE, segments=8)
    # the propane cage and the newspaper box
    make_box("Propane_Cage", (x1 - 1.6, STORE_Y + 0.50, 0.06 + 0.75), (1.40, 0.80, 1.50), (0.40, 0.42, 0.44, 1.0))
    make_box("Newspaper_Box", (x1 - 3.2, STORE_Y + 0.40, 0.06 + 0.55), (0.46, 0.46, 1.10), (0.20, 0.36, 0.66, 1.0))


def build_exit():
    """The exit onto the road, the traffic light over it, the crow on the mast arm."""
    ex = 14.0
    make_cyl("Traffic_Light_Pole", (ex + 4.6, ROAD_Y - 5.0, 3.0), 0.14, 6.0, COL_STEEL, segments=8)
    make_box("Traffic_Light_Arm", (ex + 1.6, ROAD_Y - 5.0, 5.9), (6.0, 0.14, 0.14), COL_STEEL)
    make_box("Traffic_Light_Head", (ex, ROAD_Y - 5.0, 5.33), (0.34, 0.30, 1.0), (0.20, 0.22, 0.20, 1.0))   # hung from the arm
    for k, col in enumerate(((0.80, 0.16, 0.14, 1.0), (0.86, 0.64, 0.14, 1.0), (0.20, 0.70, 0.30, 1.0))):
        make_cyl(f"Traffic_Light_Lamp_{k}", (ex, ROAD_Y - 5.0 - 0.155, 5.63 - k * 0.30), 0.10, 0.02, col, segments=10, axis='Y')
    make_crow("Exit_Crow", ex - 1.2, ROAD_Y - 5.0, 5.97, facing=-1.0, scale=1.0)


def main():
    clear_scene()
    build_ground()
    build_forecourt()
    build_store()
    build_exit()
    out = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)),
        "../../../assets/3d/locales/county_line_station.glb"))
    print(f"\n[build_county_line_station] exporting to {out}")
    export_glb(out)


if __name__ == "__main__":
    main()
