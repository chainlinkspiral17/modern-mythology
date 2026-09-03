"""small_wood_road — the county road past the property, Small Wood,
Oregon (vol1 + vol2). New 2026-09-03 (user: "the stretches of highway
across all the volumes look identical, same geometry, same camera").

vol1 ch3: "EXT. DRIVING AROUND — NIGHT. Good music is playing." vol2
ch1: "I began running along the road — up and down the property ...
Knotted paths leading both up and down the road, twisting alongside
cricks, emerging upon tool shed areas, out-of-the-way pole barns, and
the remains of fallen-in houses. Debris of lives lost in transition."
vol2 ch2: "Gloria was found by the side of the road — beaten and
dishevelled. Her rescuer was a travelling minister."

A narrow two-lane county road with gravel shoulders, the property
fence and gate on the west, the pole barn up the drive, the tool shed,
the chicken coop out back of a small house, the crick crossing under
a culvert with a concrete headwall, a fallen-in house in the field to
the east, Douglas firs standing over everything, a SMALL WOOD 3 sign,
mailboxes at the gate. Nothing here is Louisiana or Texas.

Presets (Background3D), each a different place, height and lens:
  small_wood_road        day · on the west shoulder at the gate, eye
                          1.7, NNE up the road past the pole barn · 60°
  small_wood_road_night  night · the car's hood, eye 1.0 on the
                          centerline, the dashes running into the
                          firs · 70°
  small_wood_roadside    dawn · in the east ditch, eye 0.7, looking
                          along the gravel where the minister stopped · 50°

Coordinate frame: Blender Z-up. Road N-S along y at x 0, ±1200 so
the lines converge. The property gate at y 0 west; the crick at
y 30; the fallen-in house east at y -30. glTF export remaps to Godot
(x, z, -y).
"""
import os, sys, math
_BT = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
if _BT not in sys.path: sys.path.insert(0, _BT)
from _props import palette as P
from _props.geometry import clear_scene, make_box, make_cyl, make_blob, make_wedge, make_gable, export_glb
from _props.detail import make_far_bands
from _props.trees import make_conifer, make_broadleaf
from _props.vehicles import make_car

ASPHALT = (0.22, 0.22, 0.23, 1.0)
GRAVEL = (0.58, 0.54, 0.46, 1.0)
GRASS = (0.36, 0.44, 0.24, 1.0)
FIELD = (0.52, 0.50, 0.30, 1.0)
DIRT = (0.42, 0.34, 0.24, 1.0)
FIR = (0.16, 0.28, 0.18, 1.0)
FIR_LT = (0.22, 0.34, 0.22, 1.0)
TRUNK = (0.32, 0.24, 0.18, 1.0)
WOOD_GRAY = (0.50, 0.46, 0.40, 1.0)
WOOD_RED = (0.46, 0.24, 0.18, 1.0)
TIN = (0.56, 0.58, 0.58, 1.0)
CONCRETE = (0.60, 0.60, 0.58, 1.0)
WATER = (0.28, 0.36, 0.34, 0.8)
ROAD_FAR, ROAD_NEAR = 1200.0, -1200.0


def build_road():
    span = (ROAD_FAR - ROAD_NEAR) / 2.0
    mid = (ROAD_FAR + ROAD_NEAR) / 2.0
    make_box("Ground_Far", (0.0, 0.0, -0.06), (2600.0, 2600.0, 0.02), (0.34, 0.40, 0.24, 1.0))
    make_box("Asphalt", (0.0, mid, 0.0), (3.6, span, 0.04), ASPHALT)
    di = 0
    dy = ROAD_NEAR
    while dy < ROAD_FAR:
        make_box(f"CenterLine_{di}", (0.0, dy, 0.022), (0.08, 1.20, 0.005), (0.90, 0.84, 0.50, 1.0))
        dy += 10.0
        di += 1
    for sgn in (-1, +1):
        make_box(f"Gravel_Shoulder_{sgn:+d}", (sgn * 2.35, mid, 0.01), (1.1, span, 0.02), GRAVEL)
        make_wedge(f"Ditch_{sgn:+d}", (sgn * 3.7, mid, -0.18), (1.6, span, 0.36), GRASS, high_end=("+X" if sgn < 0 else "-X"))
    # frost heaves and patches: a road that has been fixed by the county
    for i in range(30):
        make_box(f"Patch_{i}", ((i % 3 - 1) * 0.9, -300.0 + i * 21.0, 0.021), (1.1, 1.6, 0.002), (0.18, 0.18, 0.19, 1.0))
    # the crick: runs beside the road from the east, crosses under at y 30
    make_box("Crick_Bed", (0.0, 30.0, -0.30), (60.0, 2.4, 0.20), (0.30, 0.28, 0.22, 1.0))
    make_box("Crick_Water_E", (16.0, 30.0, -0.17), (28.0, 1.6, 0.06), WATER)
    make_box("Crick_Water_W", (-16.0, 30.0, -0.17), (28.0, 1.6, 0.06), WATER)
    make_cyl("Culvert_Pipe", (0.0, 30.0, -0.10), 0.55, 8.0, (0.36, 0.36, 0.38, 1.0), axis="X", segments=12)
    for sgn in (-1, 1):
        make_box(f"Culvert_Headwall_{sgn:+d}", (sgn * 4.3, 30.0, 0.25), (0.40, 3.0, 1.10), CONCRETE)
        for pi in range(3):
            make_cyl(f"Crick_Rock_{sgn:+d}_{pi}", (sgn * (6.0 + pi * 2.5), 30.6 - (pi % 2) * 1.0, -0.05), 0.30, 0.30, (0.40, 0.40, 0.38, 1.0), segments=7)
    # county sign, mile post
    make_cyl("County_Sign_Post", (3.2, -60.0, 1.2), 0.05, 2.4, (0.40, 0.42, 0.40, 1.0), segments=6)
    make_box("County_Sign", (3.2, -60.0, 2.6), (0.04, 1.2, 0.50), (0.16, 0.42, 0.24, 1.0))
    make_box("County_Sign_Text", (3.17, -60.0, 2.6), (0.005, 1.0, 0.16), (0.94, 0.94, 0.90, 1.0))
    make_cyl("Mile_Post", (-3.0, 90.0, 0.8), 0.04, 1.6, (0.80, 0.84, 0.62, 1.0), segments=6)


def build_property():
    """The fence, the gate, the drive, the pole barn, the tool shed, the
    small house with the chicken coop out back — the west side."""
    for i in range(0, 48):
        y = -40.0 + i * 3.0
        if 1.5 < y < 4.5:
            continue          # the gate gap
        make_cyl(f"Fence_Post_{i}", (-4.8, y, 0.55), 0.06, 1.10, WOOD_GRAY, segments=6)
    for seg, (y0, y1) in enumerate(((-40.0, 1.5), (4.5, 101.0))):
        make_box(f"Fence_Wire_Top_{seg}", (-4.8, (y0 + y1) / 2.0, 1.02), (0.01, y1 - y0, 0.01), (0.50, 0.50, 0.48, 1.0))
        make_box(f"Fence_Wire_Mid_{seg}", (-4.8, (y0 + y1) / 2.0, 0.62), (0.01, y1 - y0, 0.01), (0.50, 0.50, 0.48, 1.0))
    make_cyl("Gate_Post_S", (-4.8, 1.2, 0.8), 0.10, 1.6, WOOD_GRAY, segments=6)
    make_cyl("Gate_Post_N", (-4.8, 4.8, 0.8), 0.10, 1.6, WOOD_GRAY, segments=6)
    make_box("Gate_Bar_Top", (-4.8, 3.0, 1.15), (0.06, 3.4, 0.08), (0.44, 0.40, 0.34, 1.0))
    make_box("Gate_Bar_Low", (-4.8, 3.0, 0.55), (0.06, 3.4, 0.08), (0.44, 0.40, 0.34, 1.0))
    make_box("Gate_Brace", (-4.8, 3.0, 0.85), (0.05, 0.08, 0.52), (0.44, 0.40, 0.34, 1.0))
    # mailboxes at the gate, the drive up to the barn
    for mi in range(3):
        make_cyl(f"Mailbox_Post_{mi}", (-3.4, -1.6 - mi * 0.5, 0.5), 0.04, 1.0, WOOD_GRAY, segments=6)
        make_box(f"Mailbox_{mi}", (-3.4, -1.6 - mi * 0.5, 1.12), (0.22, 0.40, 0.22), (0.30, 0.32, 0.36, 1.0) if mi else (0.62, 0.20, 0.16, 1.0))
    make_box("Drive_Gravel", (-16.0, 3.0, 0.005), (22.0, 3.2, 0.01), GRAVEL)
    make_box("Drive_Grass_Strip", (-16.0, 3.0, 0.011), (20.0, 0.4, 0.004), GRASS)
    # the pole barn: open front, tin roof on poles
    bx, by = -24.0, 12.0
    make_box("Pole_Barn_Slab", (bx, by, 0.05), (12.0, 9.0, 0.10), CONCRETE)
    for pi, (px, py) in enumerate(((-5.5, -4.0), (0.0, -4.0), (5.5, -4.0), (-5.5, 4.0), (0.0, 4.0), (5.5, 4.0))):
        make_cyl(f"Pole_Barn_Pole_{pi}", (bx + px, by + py, 2.0), 0.14, 3.8, TRUNK, segments=6)
    make_box("Pole_Barn_Back", (bx, by + 4.4, 2.0), (12.0, 0.10, 3.8), WOOD_RED)
    make_box("Pole_Barn_Side_W", (bx - 6.0, by, 2.0), (0.10, 8.8, 3.8), WOOD_RED)
    make_gable("Pole_Barn_Roof", (bx, by, 3.9 + 0.9), (12.8, 9.8, 1.8), TIN, ridge_axis="X")
    make_box("Pole_Barn_Tractor", (bx - 2.5, by + 1.0, 1.0), (2.2, 3.6, 1.8), (0.60, 0.26, 0.12, 1.0))
    make_box("Pole_Barn_Hay", (bx + 3.5, by + 2.0, 0.85), (3.0, 3.0, 1.5), (0.72, 0.60, 0.32, 1.0))
    # the tool shed, the small house, the chicken coop out back
    make_box("Tool_Shed", (-12.0, -12.0, 1.2), (3.0, 2.4, 2.4), WOOD_GRAY)
    make_gable("Tool_Shed_Roof", (-12.0, -12.0, 2.4 + 0.4), (3.4, 2.8, 0.8), TIN, ridge_axis="Y")
    make_box("Tool_Shed_Door", (-10.48, -12.0, 1.0), (0.04, 0.9, 2.0), (0.34, 0.30, 0.26, 1.0))
    make_box("Tool_Shed_Wheelbarrow", (-10.0, -14.2, 0.35), (0.7, 1.3, 0.5), (0.50, 0.30, 0.22, 1.0))
    hx, hy = -18.0, -22.0
    make_box("Small_House", (hx, hy, 1.5), (8.0, 7.0, 3.0), (0.80, 0.78, 0.70, 1.0))
    make_gable("Small_House_Roof", (hx, hy, 3.0 + 1.0), (8.6, 7.6, 2.0), (0.36, 0.30, 0.26, 1.0), ridge_axis="X")
    make_box("Small_House_Porch", (hx + 4.6, hy, 0.15), (1.2, 4.0, 0.30), WOOD_GRAY)
    make_box("Small_House_Door", (hx + 4.02, hy, 1.05), (0.04, 0.9, 2.1), (0.40, 0.28, 0.22, 1.0))
    for wi, wy in enumerate((-2.2, 2.2)):
        make_box(f"Small_House_Win_{wi}", (hx + 4.02, hy + wy, 1.6), (0.04, 1.1, 1.0), (0.96, 0.86, 0.56, 1.0) if wi else (0.16, 0.18, 0.22, 1.0))
    make_box("Chicken_Coop", (hx - 1.0, hy - 6.0, 0.7), (2.4, 1.8, 1.4), WOOD_RED)
    make_wedge("Chicken_Coop_Roof", (hx - 1.0, hy - 6.0, 1.4 + 0.25), (2.6, 2.0, 0.5), TIN, high_end="+Y")
    make_box("Chicken_Run_Floor", (hx + 1.5, hy - 6.0, 0.005), (2.6, 2.4, 0.01), DIRT)
    for ci, (cx, cy) in enumerate(((hx + 0.3, hy - 7.1), (hx + 2.7, hy - 7.1), (hx + 0.3, hy - 4.9), (hx + 2.7, hy - 4.9))):
        make_cyl(f"Chicken_Run_Post_{ci}", (cx, cy, 0.6), 0.03, 1.2, WOOD_GRAY, segments=5)
    make_box("Chicken_Run_Wire_S", (hx + 1.5, hy - 7.1, 0.6), (2.4, 0.01, 1.2), (0.60, 0.62, 0.60, 0.4))
    make_box("Chicken_Run_Wire_E", (hx + 2.7, hy - 6.0, 0.6), (0.01, 2.2, 1.2), (0.60, 0.62, 0.60, 0.4))
    for hi in range(4):
        make_blob(f"Chicken_{hi}", (hx + 0.8 + (hi % 2) * 1.2, hy - 6.6 + (hi // 2) * 1.0, 0.14), 0.12, (0.88, 0.84, 0.76, 1.0), noise=0.2, seed=70 + hi, squash=0.8)


def build_fallen_house():
    """East of the road, in the field: the remains of a fallen-in
    house — a wall still standing, the roof slumped into the room,
    the chimney the only plumb thing left."""
    fx, fy = 18.0, -30.0
    make_box("Fallen_House_Floor", (fx, fy, 0.10), (8.0, 7.0, 0.20), (0.44, 0.40, 0.34, 1.0))
    make_box("Fallen_House_Wall_N", (fx, fy + 3.45, 1.3), (8.0, 0.10, 2.4), WOOD_GRAY)
    make_box("Fallen_House_Wall_W", (fx - 3.95, fy + 1.0, 0.9), (0.10, 4.9, 1.6), WOOD_GRAY)
    make_box("Fallen_House_Wall_E_Stub", (fx + 3.95, fy + 2.5, 0.6), (0.10, 1.9, 1.0), WOOD_GRAY)
    make_wedge("Fallen_House_Roof", (fx, fy + 0.5, 0.20 + 1.15), (7.6, 5.8, 2.3), (0.34, 0.30, 0.26, 1.0), high_end="+Y")
    make_box("Fallen_House_Chimney", (fx + 2.5, fy + 2.8, 2.6), (0.7, 0.7, 5.2), (0.46, 0.32, 0.26, 1.0))
    make_box("Fallen_House_Chimney_Cap", (fx + 2.5, fy + 2.8, 5.25), (0.9, 0.9, 0.10), (0.36, 0.26, 0.22, 1.0))
    for di in range(6):
        make_box(f"Fallen_Debris_{di}", (fx - 3.0 + di * 1.3, fy - 4.2 + (di % 2) * 0.8, 0.12), (1.2, 0.3, 0.24), WOOD_GRAY)
    make_blob("Fallen_House_Bramble", (fx - 3.0, fy - 2.6, 1.0), 1.0, (0.30, 0.38, 0.22, 1.0), noise=0.28, seed=91, squash=0.6)
    make_box("Fallen_House_Path", (9.0, fy + 1.0, 0.004), (10.0, 0.8, 0.008), DIRT)


def build_trees_and_fields():
    """Douglas firs over everything; hay field east, pasture west."""
    # the crick cuts both plates at y 28.8..31.2
    make_box("Field_E_S", (60.0, -60.6, 0.004), (100.0, 178.8, 0.008), FIELD)
    make_box("Field_E_N", (60.0, 90.6, 0.004), (100.0, 118.8, 0.008), FIELD)
    make_box("Pasture_W_S", (-60.0, -40.6, 0.004), (100.0, 138.8, 0.008), GRASS)
    make_box("Pasture_W_N", (-60.0, 90.6, 0.004), (100.0, 118.8, 0.008), GRASS)
    firs = ((-8.0, -48.0, 22.0), (-7.5, -34.0, 19.0), (-9.0, 40.0, 24.0), (-8.0, 58.0, 21.0), (-9.5, 76.0, 23.0), (-8.5, 96.0, 20.0),
            (8.0, -50.0, 20.0), (7.5, 8.0, 22.0), (9.0, 22.0, 18.0), (8.5, 48.0, 24.0), (9.5, 66.0, 21.0), (8.0, 88.0, 23.0),
            (-30.0, 30.0, 26.0), (-36.0, 50.0, 24.0), (30.0, 40.0, 25.0), (34.0, 60.0, 22.0), (26.0, -60.0, 24.0))
    for i, (x, y, h) in enumerate(firs):
        make_conifer(f"Fir_{i}", x, y, h, FIR if i % 2 else FIR_LT, TRUNK)
    make_broadleaf("Gate_Maple", -6.5, -6.0, 9.0, (0.36, 0.44, 0.22, 1.0), TRUNK)
    # hay bales in the east field, a stock tank in the pasture
    for bi in range(5):
        make_cyl(f"Hay_Bale_{bi}", (30.0 + bi * 7.0, 8.0 + (bi % 2) * 6.0, 0.7), 0.7, 1.4, (0.74, 0.62, 0.34, 1.0), axis="Y", segments=10)
    make_cyl("Stock_Tank", (-30.0, -8.0, 0.35), 1.4, 0.7, (0.56, 0.58, 0.58, 1.0), segments=12)
    make_cyl("Stock_Tank_Water", (-30.0, -8.0, 0.705), 1.3, 0.01, WATER, segments=12)


def build_night():
    """vol1's driving: the car on the road for the night preset, its
    headlight spill on the asphalt ahead; the Small Wood lights far up."""
    make_car("Night_Car", 0.9, -22.0, 4.6, (0.30, 0.34, 0.42, 1.0), along="Y", z0=0.02)
    make_box("Headlight_Spill", (0.9, -8.0, 0.0205), (3.2, 24.0, 0.001), (0.34, 0.34, 0.30, 1.0))
    for i in range(3):
        make_box(f"Town_Glow_{i}", (-40.0 + i * 30.0, 400.0, 3.0 + i), (6.0, 0.4, 2.0), (0.60, 0.52, 0.34, 1.0))
    make_box("Church_Steeple", (-20.0, 380.0, 9.0), (2.0, 2.0, 18.0), (0.84, 0.84, 0.80, 1.0))


def build_horizon():
    make_far_bands("FarFirs", (0.14, 0.22, 0.16),
                   [(120.0, 200.0, 26.0, 0.90), (260.0, 320.0, 30.0, 0.72), (520.0, 500.0, 36.0, 0.55)],
                   sides="EW", cx=0.0, cy=0.0, profile="ridge")


def main():
    clear_scene()
    build_road()
    build_property()
    build_fallen_house()
    build_trees_and_fields()
    build_night()
    build_horizon()
    out = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "../../../assets/3d/locales/small_wood_road.glb"))
    print(f"\n[build_small_wood_road] exporting to {out}")
    export_glb(out)


if __name__ == "__main__":
    main()
