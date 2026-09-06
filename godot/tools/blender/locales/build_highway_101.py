"""highway_101 — the coast highway north of Yachats, vol7 ch22 (The
Drive). New 2026-09-03.

"The road north of Yachats was a two-lane state highway running close
to the coast. The cedars on the inland side were the cedars Tem had
been at the cabin in for thirty-one years. The ocean on the seaward
side ..." "The turn for the old-Yachats bluff was not signed. The road
had been bypassed thirty years ago. A green metal road-marker reading
Old Yachats Road sat at the turn with a chain across it the way roads
get when they have been county-decommissioned."

The seaward side is WEST: a guardrail on posts, the drop to the water,
the swell line at the base of the bluff, the Pacific out to a gray
horizon. Inland is a wall of cedars and a rock cut. Ahead, the
old-Yachats headland rises with the tower's bluff on it. The
decommissioned turn with its chain and marker at y 160.

Presets (Background3D):
  highway_101        dusk · the truck's hood height (1.15) on the
                      northbound lane, the ocean left, cedars right,
                      the headland ahead · 62°
  highway_101_turn   dusk · at the chained turn, eye 1.6, WNW at the
                      chain and the green marker, the spur going off
                      to the bluff · 52°

Coordinate frame: Blender Z-up. Highway N-S along y at x 0, ±1200.
Sea level z -22. glTF export remaps to Godot (x, z, -y).
"""
import os, sys, math
_BT = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
if _BT not in sys.path: sys.path.insert(0, _BT)
from _props import palette as P
from _props.geometry import clear_scene, make_box, make_cyl, make_blob, make_wedge, make_tube, make_lathe, catenary, export_glb
from _props.detail import make_far_bands
from _props.trees import make_conifer
from _props.vehicles import make_car
from _props.detail import make_guardrail, make_road_bend

ASPHALT = (0.24, 0.24, 0.25, 1.0)
SHOULDER = (0.44, 0.42, 0.36, 1.0)
GRAVEL = (0.56, 0.52, 0.46, 1.0)
ROCK = (0.34, 0.33, 0.32, 1.0)
ROCK_DK = (0.26, 0.26, 0.26, 1.0)
CEDAR = (0.14, 0.26, 0.18, 1.0)
CEDAR_LT = (0.20, 0.32, 0.22, 1.0)
TRUNK = (0.34, 0.24, 0.16, 1.0)
SEA = (0.30, 0.40, 0.44, 1.0)
FOAM = (0.82, 0.86, 0.86, 1.0)
STEEL = (0.62, 0.64, 0.66, 1.0)
SALAL = (0.24, 0.36, 0.22, 1.0)
SEA_Z = -22.0
ROAD_FAR, ROAD_NEAR = 1200.0, -1200.0


def build_road():
    BEND_Y = 250.0
    span = (BEND_Y - ROAD_NEAR)
    mid = (BEND_Y + ROAD_NEAR) / 2.0
    # the land the road sits on: a shelf, rock below it to the sea
    make_box("Ground_Far", (60.0, 0.0, -0.06), (2400.0, 2600.0, 0.02), (0.20, 0.28, 0.20, 1.0))
    make_box("Roadbed", (2.0, mid, -0.5), (16.0, span, 0.9), ROCK_DK)
    make_box("Road_Asphalt", (0.0, mid, 0.0), (7.2, span, 0.04), ASPHALT)
    di = 0
    dy = ROAD_NEAR
    while dy < BEND_Y - 1.0:
        make_box(f"Road_CenterLine_{di}", (0.0, dy, 0.022), (0.10, 1.50, 0.005), (0.92, 0.86, 0.50, 1.0))
        dy += 12.0
        di += 1
    for sgn in (-1, +1):
        make_box(f"Road_EdgeLine_{sgn:+d}", (sgn * 3.4, mid, 0.022), (0.08, span, 0.005), (0.92, 0.92, 0.88, 1.0))
        make_box(f"Road_Shoulder_{sgn:+d}", (sgn * 4.3, mid, 0.01), (1.4, span, 0.02), SHOULDER)
    # the seaward guardrail: W-beam on posts (a gap at the old-Yachats spur, y 155..165)
    make_guardrail("Guardrail_S", -5.4, ROAD_NEAR, 154.75, side=1, steel=STEEL)
    make_guardrail("Guardrail_N", -5.4, 165.25, BEND_Y, side=1, steel=STEEL)
    # the highway bends inland around the headland: 28 degrees east, then the run
    make_road_bend("Road_Bend", 0.0, BEND_Y, 0.0, 28.0, 140.0, 900.0, 7.2, asphalt=ASPHALT, line=(0.92, 0.86, 0.50, 1.0),
                   edge=(0.92, 0.92, 0.88, 1.0), shoulder_w=1.4, shoulder=SHOULDER, seg_len=10.0)
    # the drop to the sea: a long wedge falling west from the shelf
    make_wedge("Sea_Bluff", (-15.0 - 12.0, mid, (SEA_Z + -0.95) / 2.0), (24.0, span, -0.95 - SEA_Z), ROCK, high_end="+X")
    make_box("Sea", (-160.0, 0.0, SEA_Z - 0.05), (260.0, 2600.0, 0.10), SEA)
    make_box("Swell_Line", (-40.6, 0.0, SEA_Z + 0.012), (1.0, 2600.0, 0.024), FOAM)
    make_box("Swell_Line_2", (-43.2, 0.0, SEA_Z + 0.006), (0.6, 2600.0, 0.012), FOAM)
    # sea stacks
    for i, (x, y, r, s) in enumerate(((-58.0, 90.0, 6.0, 1), (-70.0, 260.0, 8.0, 2), (-52.0, -140.0, 5.0, 3), (-66.0, 520.0, 7.0, 4))):
        make_blob(f"Sea_Stack_{i}", (x, y, SEA_Z + r * 1.6), r, ROCK, noise=0.30, seed=s, squash=1.2)


def build_inland():
    """Cedars in a wall east of the road, a rock cut where the highway
    was straightened, salal at the foot of the trees."""
    cedars = []
    for i in range(0, 80):
        y = -240.0 + i * 6.0
        x = 9.0 + (i * 7) % 4 * 1.2
        h = 18.0 + (i * 5) % 7 * 1.4
        cedars.append((x, y, h))
        if i % 3 == 0:
            cedars.append((x + 8.0 + (i % 5), y + 2.5, h - 3.0))
    for i, (x, y, h) in enumerate(cedars):
        if 40.0 < y < 120.0:
            continue      # the rock cut
        make_conifer(f"Cedar_{i}", x, y, h, CEDAR if i % 2 else CEDAR_LT, TRUNK)
    make_box("Rock_Cut", (10.5, 80.0, 6.0), (6.0, 80.0, 12.0), ROCK)
    make_box("Rock_Cut_Face_Band", (7.49, 80.0, 3.0), (0.02, 80.0, 1.2), ROCK_DK)
    for i in range(10):
        make_blob(f"Rock_Cut_Rubble_{i}", (6.4, 44.0 + i * 8.0, 0.48), 0.5, ROCK_DK, noise=0.3, seed=20 + i, squash=0.7)
    for i in range(24):
        y = -230.0 + i * 20.0
        if 40.0 < y < 120.0:
            continue
        make_blob(f"Salal_{i}", (6.6, y, 0.72), 0.9, SALAL, noise=0.26, seed=50 + i, squash=0.55)


def build_headland_and_turn():
    """The old-Yachats headland rising ahead to the north-west with the
    bluff on it; the decommissioned turn with its chain and marker."""
    make_blob("Headland_Mass", (-98.0, 380.0, 26.0), 40.0, (0.24, 0.32, 0.22, 1.0), noise=0.22, seed=7, squash=0.5)
    # the turn: a gravel spur west off the shoulder at y 160, chained
    make_box("Old_Yachats_Spur", (-9.0, 160.0, 0.006), (9.0, 4.0, 0.012), GRAVEL)
    make_box("Old_Yachats_Spur_Far", (-20.0, 163.0, 0.006), (14.0, 4.0, 0.012), GRAVEL)
    for nm, py in (("S", 157.6), ("N", 162.4)):
        make_lathe(f"Chain_Post_{nm}", (-6.6, py, 0.0), [(0.07, 0.0), (0.06, 0.9), (0.08, 0.94), (0.08, 1.0), (0.0, 1.02)], (0.36, 0.36, 0.38, 1.0), segments=8)
    make_tube("Chain", catenary((-6.6, 157.6, 0.92), (-6.6, 162.4, 0.92), 0.38, n=10), 0.022, (0.30, 0.30, 0.32, 1.0), segments=6)
    make_box("Chain_Sign", (-6.6, 160.0, 0.66), (0.02, 0.40, 0.26), (0.92, 0.88, 0.30, 1.0))
    make_cyl("Road_Marker_Post", (-5.0, 156.5, 1.0), 0.04, 2.0, (0.40, 0.42, 0.40, 1.0), segments=6)
    make_box("Road_Marker", (-5.0, 156.5, 2.2), (0.04, 0.90, 0.30), (0.16, 0.42, 0.24, 1.0))
    make_box("Road_Marker_Text", (-4.97, 156.5, 2.2), (0.005, 0.76, 0.10), (0.94, 0.94, 0.90, 1.0))
    # the guardrail has a gap at the spur
    make_box("Guardrail_End_S", (-5.4, 155.0, 0.72), (0.09, 0.5, 0.34), (0.86, 0.72, 0.20, 1.0))
    make_box("Guardrail_End_N", (-5.4, 165.5, 0.72), (0.09, 0.5, 0.34), (0.86, 0.72, 0.20, 1.0))
    # Tem's truck northbound for the hood preset
    make_car("Tem_Truck", 1.8, 8.0, 5.6, (0.44, 0.40, 0.34, 1.0), pickup=True, along="Y", z0=0.02)
    make_cyl("Mile_Marker", (4.6, 120.0, 0.9), 0.04, 1.8, (0.80, 0.84, 0.62, 1.0), segments=6)


def build_horizon():
    make_far_bands("FarRidge", (0.16, 0.24, 0.18),
                   [(200.0, 300.0, 40.0, 0.85), (420.0, 480.0, 55.0, 0.65)],
                   sides="E", cx=60.0, cy=0.0, profile="ridge")
    make_box("Sea_Horizon_Haze", (-320.0, 0.0, 6.0), (30.0, 2600.0, 12.0), (0.74, 0.78, 0.80, 1.0))


def main():
    clear_scene()
    build_road()
    build_inland()
    build_headland_and_turn()
    build_horizon()
    out = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "../../../assets/3d/locales/highway_101.glb"))
    print(f"\n[build_highway_101] exporting to {out}")
    export_glb(out)


if __name__ == "__main__":
    main()
