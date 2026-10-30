"""small_wood_farmhouse — THE LINK HOME, vol 2's house in the country
outside Small Wood (draft 1, 2026-10-18; unified 2026-10-27).

UNIFIED (Andy, 2026-10-27): "the points of impact family lives in the link
home after they move out" — and, asked, "Small Wood house, unified". The
narrator's room (small_wood_ranch's bedroom: the plank blinds, the clock
radio, the reading lamp) is upstairs in THIS house, north-west, its window in
the north wall; the renters' night below is the same house four years on.
The second house stands in the field south-east of the yard. The ranch
presets (ranch_bedroom_night / _lamp / _day, ranch_home_day,
ranch_second_house) now load this set; build_small_wood_ranch.py keeps the
room's dressing (build_bedroom, build_second_house), placed here by an
offset applied to the objects in Blender and to the audits' recording alike.

The user: "go ahead and start working on backgrounds for vol 1-4 as needed."
The grandmother's two-storey house ("the farm house we had occupied", "the
family home"), seen on two nights years apart:
  points_of_impact (the renters' night): "two large picture windows that
   killed the heating bill, but provided a gorgeous view of the valley";
   "She walked down the stairs, grabbing an afghan blanket off the
   banister"; "the small, barely working television"; the kitchen window
   "past the fruit-bearing trees" to the workshop light that "held steady
   across the dark yard"; "the service porch", "the secondary service
   door", "the garage port not twenty feet from her"; "the moon hidden
   behind clouds"                         → farm_living_night (and the
                                            kitchen window as a spare view)
  loose_pages: "A cold ugly night to spit into a cup on the porch."
   "Chew, whiskey and hormonal cats circling and screeching." "Dad is
   passed out, inside on his recliner"; the pick-up; a page "Held up to the
   window"                                → farm_porch_night
The upstairs (the girls' room, the master bedroom with its two hall doors)
is a shell here: draft 2.

Blender: x east, y north, z up; Godot (x, z, -y). The living room x -8..0,
y 0..10 (picture windows on the W wall, over the valley); the kitchen
x 0..6, y 4..10; the service porch x 6..9, y 0..4; the front porch along
the S wall; the workshop across the yard to the east.

DRAFT 2 targets: the upstairs; the night after (broken glass, the imploded
picture window) as its own state if a scene asks; the valley's far lights;
the renters' things vs the narrator's family's things per scene.
"""
import os, sys, math
_BT = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
if _BT not in sys.path: sys.path.insert(0, _BT)
from _props.geometry import (clear_scene, make_box, make_cyl, make_chamfer_box, make_rot_box, make_blob, make_lathe, make_gable,
                             join_stock, export_glb)
from _props.structure import make_floor, make_wall, make_wall_with_openings
from _props.furniture import make_table, make_chair, make_lamp
from _props.trees import make_broadleaf
try:
    import bpy
except ImportError:
    bpy = None
_HERE = os.path.dirname(os.path.abspath(__file__))
if _HERE not in sys.path: sys.path.insert(0, _HERE)

H, T = 2.5, 0.20
PAL = {"wall": (0.80, 0.76, 0.66, 1.0), "baseboard": (0.40, 0.32, 0.24, 1.0)}
TRIM = (0.86, 0.84, 0.78, 1.0); WOOD = (0.46, 0.34, 0.22, 1.0)
SIDING = (0.82, 0.80, 0.74, 1.0); ROOF = (0.26, 0.24, 0.24, 1.0)
GRASS = (0.24, 0.30, 0.20, 1.0)
LIVE, PORCH, KITCH = "__farm_living_night", "__farm_porch_night", "__farm_kitchen_window"


def frame(name, axis, along, at, cz, w, h):
    for s in (-1, 1):
        if axis == 'X':
            make_box(f"{name}_Frame_Jamb_{s:+d}", (along + s * (w / 2.0 - 0.03), at, cz), (0.06, T + 0.02, h), TRIM)
        else:
            make_box(f"{name}_Frame_Jamb_{s:+d}", (at, along + s * (w / 2.0 - 0.03), cz), (T + 0.02, 0.06, h), TRIM)
    for zz in (cz - h / 2.0 + 0.03, cz + h / 2.0 - 0.03):
        if axis == 'X':
            make_box(f"{name}_Frame_Rail_{zz:.2f}", (along, at, zz), (w - 0.12, T + 0.02, 0.06), TRIM)
        else:
            make_box(f"{name}_Frame_Rail_{zz:.2f}", (at, along, zz), (T + 0.02, w - 0.12, 0.06), TRIM)


def build_house():
    make_floor("Ground_Floor", (-1.0, 5.0, 0.0), size_x=14.0, size_y=10.0,
               palette={"vinyl": (0.46, 0.34, 0.22, 1.0), "seam": (0.38, 0.28, 0.18, 1.0)}, style="plank")
    # the ceiling and the floor above are cut round the stair's hole
    # (x -1.2..-0.1, y 6.0..9.5)
    cc = (0.84, 0.82, 0.76, 1.0)
    make_box("Ground_Ceil_W", (-4.7, 5.0, H + 0.04), (7.0, 10.4, 0.08), cc)
    make_box("Ground_Ceil_E", (3.05, 5.0, H + 0.04), (6.3, 10.4, 0.08), cc)
    make_box("Ground_Ceil_Mid_S", (-0.65, 2.9, H + 0.04), (1.1, 6.2, 0.08), cc)
    make_box("Ground_Ceil_Mid_N", (-0.65, 9.85, H + 0.04), (1.1, 0.7, 0.08), cc)
    make_wall_with_openings("Wall_W", (-8.0, 5.0, 0), length=10.4, height=H, thickness=T, axis='Y', palette=PAL,
                            baseboard_face_sign=+1, openings=[(3.8, 1.35, 2.2, 1.5), (7.6, 1.35, 2.2, 1.5)])
    make_wall_with_openings("Wall_S", (-1.0, 0.0, 0), length=14.4, height=H, thickness=T, axis='X', palette=PAL,
                            baseboard_face_sign=+1, openings=[(-1.2, 1.0, 0.9, 2.0), (-5.0, 1.35, 1.2, 1.2)])
    make_wall("Wall_N", (-1.0, 10.0, 0), length=14.4, height=H, thickness=T, axis='X', palette=PAL, baseboard_face_sign=-1)
    make_wall_with_openings("Wall_E", (6.0, 5.0, 0), length=10.4, height=H, thickness=T, axis='Y', palette=PAL,
                            baseboard_face_sign=-1, openings=[(7.0, 1.45, 1.2, 1.0), (2.0, 1.0, 0.86, 2.0)])
    make_wall_with_openings("Wall_Kitchen_W", (0.0, 7.0, 0), length=6.0, height=H, thickness=0.12, axis='Y', palette=PAL,
                            baseboard_face_sign=+1, openings=[(4.9, 1.0, 1.0, 2.1)])
    make_wall("Wall_Kitchen_S", (3.0, 4.0, 0), length=6.0, height=H, thickness=0.12, axis='X', palette=PAL, baseboard_face_sign=-1)
    for nm, ax, al, at, cz, w, h in (("Picture_Window_S", 'Y', 3.8, -8.0, 1.35, 2.2, 1.5), ("Picture_Window_N", 'Y', 7.6, -8.0, 1.35, 2.2, 1.5),
                                     ("Porch_Window", 'X', -5.0, 0.0, 1.35, 1.2, 1.2), ("Kitchen_Window", 'Y', 7.0, 6.0, 1.45, 1.2, 1.0)):
        frame(nm, ax, al, at, cz, w, h)
    make_box("Front_Door_Shut" + KITCH, (-1.2, 0.0, 1.0), (0.88, 0.04, 2.0), (0.50, 0.36, 0.24, 1.0))
    make_box("Front_Door_Ajar" + LIVE + PORCH, (-1.2 + 0.44, 0.10 + 0.30, 1.0), (0.04, 0.60, 2.0), (0.50, 0.36, 0.24, 1.0))
    make_box("Service_Door_Shut", (6.0, 2.0, 1.0), (0.04, 0.84, 2.0), (0.64, 0.56, 0.44, 1.0))
    # the stair along the kitchen wall, its banister, the afghan on it
    for k in range(12):
        make_box(f"Stair_Tread_{k}", (-0.6, 4.4 + k * 0.42, 0.10 + k * 0.20), (1.0, 0.44, 0.20 * (k + 1)), WOOD)
    for k in range(13):
        make_box(f"Banister_Baluster_{k}", (-1.14, 4.4 + k * 0.42, 0.20 * k + 0.55), (0.03, 0.03, 0.90), TRIM)
    make_rot_box("Banister_Rail", (-1.14, 4.4 + 6 * 0.42, 1.0 + 6 * 0.20 + 0.02), (0.06, 13 * 0.43 / math.cos(0.444), 0.06), WOOD, roll=0.444)
    make_box("Banister_Newel", (-1.14, 4.2, 0.55), (0.10, 0.10, 1.10), WOOD)
    make_rot_box("Afghan_On_Banister" + PORCH + KITCH, (-1.20, 4.8, 1.16), (0.12, 0.60, 0.40), (0.60, 0.40, 0.30, 1.0), roll=0.444)
    # the living room: the couch, the small TV, the recliner by the porch
    # window, a lamp, a rug; the afghan on the couch for the renters' night
    make_box("Couch_Base", (-4.4, 6.0, 0.22), (2.2, 0.90, 0.44), (0.50, 0.44, 0.34, 1.0))
    make_box("Couch_Back", (-4.4, 5.62, 0.66), (2.2, 0.16, 0.48), (0.50, 0.44, 0.34, 1.0))
    make_box("Afghan_On_Couch" + LIVE, (-3.8, 6.1, 0.46), (0.80, 0.70, 0.04), (0.60, 0.40, 0.30, 1.0))
    make_box("TV_Stand", (-4.4, 9.9 - 0.30, 0.30), (0.90, 0.50, 0.60), WOOD)
    make_chamfer_box("TV_Small", (-4.4, 9.9 - 0.30, 0.80), (0.46, 0.40, 0.40), (0.20, 0.18, 0.16, 1.0), chamfer=0.03)
    make_box("TV_Screen_Glow", (-4.4, 9.9 - 0.30 - 0.202, 0.80), (0.34, 0.004, 0.26), (0.54, 0.60, 0.76, 1.0))
    make_rot_box("TV_Rabbit_Ears", (-4.36, 9.9 - 0.30, 1.14), (0.02, 0.02, 0.30), (0.70, 0.70, 0.70, 1.0), pitch=0.5)
    make_lamp("Recliner_Lamp", -5.7, 0.40, base_z=0.0, h=1.45)       # Dad's reading lamp (pass 170)
    make_box("Recliner_Base", (-5.0, 1.0, 0.24), (0.86, 0.90, 0.48), (0.40, 0.30, 0.24, 1.0))
    make_rot_box("Recliner_Back", (-5.0, 0.60, 0.78), (0.86, 0.16, 0.66), (0.40, 0.30, 0.24, 1.0), roll=0.30)
    make_box("Recliner_Footrest", (-5.0, 1.70, 0.34), (0.70, 0.50, 0.10), (0.40, 0.30, 0.24, 1.0))
    make_box("Recliner_Footrest_Arm", (-5.0, 1.50, 0.33), (0.10, 0.10, 0.12), (0.20, 0.20, 0.20, 1.0))
    make_lamp("Living_Lamp", -7.5, 5.7, base_z=0.0, h=1.40)
    make_box("Living_Rug", (-4.4, 7.4, 0.004), (2.6, 1.8, 0.008), (0.46, 0.32, 0.26, 1.0))
    make_box("Tea_Mug_Honey" + LIVE, (-4.05, 9.72, 0.65), (0.08, 0.08, 0.10), (0.86, 0.84, 0.78, 1.0))
    make_box("Reading_Glasses" + LIVE, (-4.05, 9.45, 0.605), (0.12, 0.04, 0.01), (0.20, 0.20, 0.22, 1.0))
    # the kitchen: the sink under the E window, counters, the table
    make_box("Kitchen_Counter", (6.0 - 0.10 - 0.32, 7.0, 0.45), (0.64, 3.0, 0.90), (0.66, 0.60, 0.48, 1.0))
    make_box("Kitchen_Counter_Top", (6.0 - 0.10 - 0.33, 7.0, 0.92), (0.66, 3.04, 0.04), (0.84, 0.82, 0.76, 1.0))
    make_box("Kitchen_Sink_Basin", (6.0 - 0.10 - 0.33, 7.0, 0.942), (0.40, 0.56, 0.004), (0.70, 0.72, 0.74, 1.0))
    make_box("Kitchen_Sink_Mug" + KITCH, (6.0 - 0.10 - 0.33, 7.1, 0.99), (0.08, 0.08, 0.10), (0.86, 0.84, 0.78, 1.0))
    build_kitchen_2026_10()
    make_table("Kitchen_Table", 2.6, 7.2, w=1.2, d=0.9, h=0.75, wood=WOOD)
    for k, (dx, yaw) in enumerate(((-0.80, -math.pi / 2.0), (0.80, math.pi / 2.0))):
        make_chair(f"Kitchen_Chair_{k}", 2.6 + dx, 7.2, yaw=yaw, wood=WOOD)
    # the service porch: its small window, the jackets, the outer door
    make_box("Service_Porch_Floor", (7.5, 2.0, 0.02), (2.8, 3.8, 0.04), (0.50, 0.48, 0.44, 1.0))
    make_box("Service_Porch_Wall_E", (9.0, 2.0, 1.2), (0.12, 4.12, 2.4), SIDING)
    make_box("Service_Porch_Wall_N", (7.5, 4.0, 1.2), (3.0, 0.12, 2.4), SIDING)
    make_box("Service_Porch_Wall_S_W", (6.685, 0.0, 1.2), (1.37, 0.12, 2.4), SIDING)
    make_box("Service_Porch_Wall_S_E", (8.615, 0.0, 1.2), (0.77, 0.12, 2.4), SIDING)
    make_box("Service_Porch_Wall_S_Over", (7.8, 0.0, 2.25), (0.86, 0.12, 0.3), SIDING)
    make_box("Service_Porch_Outer_Door", (7.8, 0.0, 1.05), (0.86, 0.04, 2.1), (0.64, 0.56, 0.44, 1.0))
    make_box("Service_Porch_Roof", (7.5, 2.0, 2.46), (3.4, 4.4, 0.12), ROOF)
    # the upper storey as a shell (its windows dark), the roof over all
    make_box("Upper_Storey_Wall_S", (-1.0, 0.0, H + 0.08 + 1.25), (14.4, 0.20, 2.5), SIDING)
    # (2026-10-27) the narrator's room's own N wall (with its window) stands at
    # x -7.8..-4.0; the storey's outer wall runs either side of it
    make_box("Upper_Storey_Wall_N_W", (-8.1, 10.0, H + 0.08 + 1.25), (0.20, 0.20, 2.5), SIDING)
    make_box("Upper_Storey_Wall_N_E", (1.2, 10.0, H + 0.08 + 1.25), (10.0, 0.20, 2.5), SIDING)
    make_box("Upper_Storey_Wall_W", (-8.1, 5.0, H + 0.08 + 1.25), (0.20, 9.8, 2.5), SIDING)
    make_box("Upper_Storey_Wall_E", (6.1, 5.0, H + 0.08 + 1.25), (0.20, 9.8, 2.5), SIDING)
    uf = (0.46, 0.34, 0.22, 1.0)
    make_box("Upper_Storey_Floor_W", (-4.6, 5.0, H + 0.11), (6.8, 9.8, 0.06), uf)
    make_box("Upper_Storey_Floor_E", (2.95, 5.0, H + 0.11), (6.1, 9.8, 0.06), uf)
    make_box("Upper_Storey_Floor_Mid_S", (-0.65, 3.05, H + 0.11), (1.1, 5.9, 0.06), uf)
    make_box("Upper_Storey_Floor_Mid_N", (-0.65, 9.7, H + 0.11), (1.1, 0.4, 0.06), uf)
    for k, x in enumerate((-5.0, -1.0, 3.0)):
        make_box(f"Upper_Window_Dark_{k}", (x, -0.115, H + 1.4), (1.0, 0.03, 1.1), (0.06, 0.06, 0.08, 1.0))
    make_gable("House_Roof", (-1.0, 5.0, 2 * H + 0.16 + 1.3), (15.0, 11.0, 2.6), ROOF, ridge_axis='X')


def build_kitchen_2026_10():
    """points of impact (vol 2 ch3): "She put her cup in the sink of the
    kitchen and ran it under water. She looked out the kitchen window, past
    the fruit-bearing trees and saw the light from the workshop." DRAFT 2:
    the kitchen was a counter under a small window in a blank wall —
    - the window dressed: cafe curtains on a rod, a sill with a plant and a
      jar, the faucet and its handles over the sink, a dish rack
    - upper cabinets either side of the window, the counter's drawers and
      doors, a canister set, the toaster
    - the stove and the fridge on the N wall, a calendar, a towel on the
      oven bar
    - out the window, the yard light on its pole by the workshop (the
      tscn's Workshop_Light is its practical)
    Draft 3 targets: the water running (a ribbon from the tap), steam off
    the cup, the trees' fruit, the linoleum's pattern."""
    ex = 6.0 - 0.10                         # the E wall's inner face
    cab = (0.70, 0.64, 0.50, 1.0)
    # the faucet and its handles behind the basin, a dish rack to the S
    make_cyl("Kitchen_Faucet_Base", (ex - 0.06, 7.0, 0.98), 0.03, 0.08, (0.80, 0.80, 0.82, 1.0), segments=8)
    make_box("Kitchen_Faucet_Spout", (ex - 0.18, 7.0, 1.04), (0.24, 0.025, 0.025), (0.80, 0.80, 0.82, 1.0))   # on its base
    for i, dy in enumerate((-0.12, 0.12)):
        make_cyl(f"Kitchen_Faucet_Handle_{i}", (ex - 0.06, 7.0 + dy, 0.97), 0.022, 0.05, (0.80, 0.80, 0.82, 1.0), segments=8)
    make_box("Kitchen_Dish_Rack", (ex - 0.33, 6.30, 1.00), (0.36, 0.44, 0.12), (0.84, 0.84, 0.86, 1.0))
    for i in range(4):
        make_rot_box(f"Kitchen_Dish_Rack_Plate_{i}", (ex - 0.33, 6.16 + i * 0.09, 1.10), (0.24, 0.015, 0.22), (0.92, 0.90, 0.84, 1.0), pitch=0.0, roll=0.15)
    # the cafe curtains on their rod over the lower half of the window (sill 0.95, head 1.95)
    make_cyl("Kitchen_Curtain_Rod", (ex - 0.04, 7.0, 1.48), 0.008, 1.40, (0.70, 0.66, 0.50, 1.0), axis='Y', segments=6)
    for s in (-1, 1):
        for k in range(3):
            make_box(f"Kitchen_Curtain_{s:+d}_{k}", (ex - 0.05 - 0.01 * (k % 2), 7.0 + s * (0.42 + k * 0.08), 1.22), (0.015, 0.09, 0.50),
                     (0.90, 0.86, 0.72, 1.0))
    make_box("Kitchen_Window_Sill", (ex - 0.06, 7.0, 0.955), (0.12, 1.30, 0.03), (0.86, 0.84, 0.78, 1.0))
    make_cyl("Kitchen_Sill_Plant_Pot", (ex - 0.06, 6.62, 1.02), 0.05, 0.10, (0.70, 0.40, 0.30, 1.0), segments=10)
    make_blob("Kitchen_Sill_Plant", (ex - 0.06, 6.62, 1.13), 0.08, (0.30, 0.46, 0.26, 1.0), noise=0.4, seed=7, squash=0.9)
    make_cyl("Kitchen_Sill_Jar", (ex - 0.06, 7.40, 1.03), 0.04, 0.12, (0.80, 0.86, 0.80, 1.0), segments=10)
    # upper cabinets either side of the window
    for s, cy in ((-1, 5.95), (1, 8.05)):
        make_box(f"Kitchen_Upper_Cabinet_{s:+d}", (ex - 0.17, cy, 1.85), (0.34, 0.80, 0.70), cab)
        make_box(f"Kitchen_Upper_Cabinet_Seam_{s:+d}", (ex - 0.345, cy, 1.85), (0.005, 0.01, 0.66), (0.40, 0.34, 0.26, 1.0))
        for j in (-1, 1):
            make_box(f"Kitchen_Upper_Cabinet_Pull_{s:+d}{j:+d}", (ex - 0.35, cy + j * 0.05, 1.62), (0.01, 0.02, 0.06), (0.80, 0.78, 0.70, 1.0))
    # the counter's doors and drawers (its W face at x ex - 0.64)
    fx = ex - 0.645
    for k in range(5):
        cy = 5.75 + k * 0.62
        make_box(f"Kitchen_Counter_Door_{k}", (fx, cy, 0.42), (0.01, 0.56, 0.62), cab)
        make_box(f"Kitchen_Counter_Drawer_{k}", (fx, cy, 0.82), (0.01, 0.56, 0.12), cab)
        make_box(f"Kitchen_Counter_Pull_{k}", (fx - 0.01, cy, 0.82), (0.01, 0.10, 0.02), (0.80, 0.78, 0.70, 1.0))
    for i, (cy, h) in enumerate(((8.15, 0.24), (8.30, 0.20), (8.43, 0.16))):
        make_cyl(f"Kitchen_Canister_{i}", (ex - 0.30, cy, 0.94 + h / 2.0), 0.065, h, (0.86, 0.80, 0.62, 1.0), segments=12)
    make_chamfer_box("Kitchen_Toaster", (ex - 0.30, 5.85, 1.03), (0.18, 0.28, 0.18), (0.80, 0.80, 0.82, 1.0), chamfer=0.03)
    # the stove and the fridge on the N wall (face y 9.9), the calendar, the towel
    make_box("Kitchen_Stove", (4.4, 9.9 - 0.33, 0.45), (0.76, 0.66, 0.90), (0.92, 0.90, 0.84, 1.0))
    make_box("Kitchen_Stove_Back", (4.4, 9.9 - 0.04, 1.06), (0.76, 0.08, 0.32), (0.92, 0.90, 0.84, 1.0))
    for i in range(4):
        make_cyl(f"Kitchen_Stove_Burner_{i}", (4.4 - 0.18 + 0.36 * (i % 2), 9.9 - 0.45 + 0.24 * (i // 2), 0.905), 0.09, 0.01, (0.16, 0.16, 0.16, 1.0), segments=12)
    make_box("Kitchen_Oven_Bar", (4.4, 9.9 - 0.67, 0.80), (0.60, 0.02, 0.02), (0.80, 0.80, 0.82, 1.0))
    make_box("Kitchen_Oven_Towel", (4.25, 9.9 - 0.68, 0.66), (0.22, 0.01, 0.30), (0.70, 0.30, 0.26, 1.0))
    make_chamfer_box("Kitchen_Fridge", (1.0, 9.9 - 0.36, 0.88), (0.76, 0.72, 1.76), (0.92, 0.90, 0.84, 1.0), chamfer=0.04)
    make_box("Kitchen_Fridge_Handle", (1.32, 9.9 - 0.73, 1.10), (0.03, 0.02, 0.50), (0.80, 0.80, 0.82, 1.0))
    make_box("Kitchen_Calendar", (2.6, 9.9 - 0.006, 1.55), (0.36, 0.006, 0.50), (0.92, 0.90, 0.86, 1.0))
    make_box("Kitchen_Calendar_Picture", (2.6, 9.9 - 0.012, 1.68), (0.30, 0.004, 0.20), (0.40, 0.52, 0.40, 1.0))


def build_siding_2026_10():
    """(2026-10-30) the S facade read as one flat white slab at night: lap
    siding courses every 20 cm on both storeys, broken round the door and
    the windows, corner boards at the ends. Draft 3: the E and W gables."""
    def runs(x0, x1, holes):
        out, cur = [], x0
        for a, b in sorted(holes):
            if a > cur:
                out.append((cur, a))
            cur = max(cur, b)
        if cur < x1:
            out.append((cur, x1))
        return out
    dark = (0.64, 0.62, 0.58, 1.0)
    ground_holes = (((-1.2 - 0.48, -1.2 + 0.48), 0.0, 2.05), ((-5.0 - 0.64, -5.0 + 0.64), 0.72, 1.98))
    upper_holes = tuple(((x - 0.54, x + 0.54), H + 0.82, H + 1.98) for x in (-5.0, -1.0, 3.0))
    k = 0
    for zlist, holes in ((tuple(0.30 + i * 0.20 for i in range(11)), ground_holes),
                         (tuple(H + 0.28 + i * 0.20 for i in range(12)), upper_holes)):
        for z in zlist:
            hx = [xr for xr, z0, z1 in holes if z0 <= z <= z1]
            for a, b in runs(-8.2, 6.2, hx):
                make_box(f"Siding_Course_Stock_{k}", ((a + b) / 2.0, -0.112, z), (b - a, 0.012, 0.018), dark)
                k += 1
    for x in (-8.2, 6.2):
        make_box(f"Siding_Corner_Board_{x:+.1f}", (x, -0.115, (2 * H + 0.2) / 2.0), (0.14, 0.02, 2 * H + 0.2), TRIM)


def build_porch_and_yard():
    # the front porch along the S wall: its boards, posts, roof, rail; the
    # chair, the spit cup, the bottle, the cats
    make_box("Front_Porch_Deck", (-4.0, -1.3, 0.10), (8.4, 2.4, 0.12), (0.44, 0.36, 0.28, 1.0))
    for k in range(8):
        make_box(f"Front_Porch_Board_Seam_{k}", (-7.6 + k * 1.05, -1.3, 0.162), (0.02, 2.4, 0.004), (0.34, 0.28, 0.22, 1.0))
    for k in range(4):
        make_box(f"Front_Porch_Post_{k}", (-8.0 + k * 2.6, -2.4, 1.28), (0.12, 0.12, 2.24), TRIM)
    make_box("Front_Porch_Roof", (-4.0, -1.3, 2.46), (8.8, 2.8, 0.12), ROOF)
    # (round 3) the porch's bare bulb under its roof (the tscn's Porch_Bulb)
    make_cyl("Front_Porch_Bulb_Base", (-3.4, -1.0, 2.37), 0.05, 0.06, (0.30, 0.28, 0.26, 1.0), segments=10)
    make_blob("Front_Porch_Bulb_Glow", (-3.4, -1.0, 2.29), 0.05, (1.0, 0.90, 0.66, 1.0), noise=0.02, seed=2, squash=1.2)
    for k in range(3):
        make_box(f"Front_Porch_Rail_{k}", (-6.7 + k * 2.6, -2.4, 0.90), (2.48, 0.06, 0.06), TRIM)
    make_box("Front_Porch_Step", (-1.2, -2.8, 0.06), (1.2, 0.6, 0.12), (0.44, 0.36, 0.28, 1.0))
    make_chair("Porch_Chair", -2.6, -1.0, yaw=math.pi, wood=(0.40, 0.32, 0.24, 1.0), z0=0.16)
    make_cyl("Porch_Spit_Cup", (-2.0, -1.4, 0.21), 0.04, 0.10, (0.86, 0.84, 0.80, 1.0), segments=10)
    make_lathe("Porch_Whiskey_Bottle", (-1.9, -1.15, 0.16), [(0.0, 0.0), (0.045, 0.0), (0.045, 0.20), (0.015, 0.26), (0.015, 0.30), (0.0, 0.30)],
               (0.50, 0.32, 0.12, 1.0), segments=8)
    for k, (x, y, s) in enumerate(((-3.6, -1.9, 0.14), (-0.6, -3.4, 0.13), (-5.2, -1.2, 0.12))):
        zz = 0.16 + s * 0.8 if y > -2.4 else s * 0.8
        make_blob(f"Cat_{k}", (x, y, zz), s, (0.20, 0.18, 0.16, 1.0), noise=0.2, seed=k, squash=0.8)
        make_blob(f"Cat_{k}_Head", (x + 0.14, y, zz + s * 0.7), s * 0.55, (0.20, 0.18, 0.16, 1.0), noise=0.1, seed=10 + k, squash=1.0)
    # the yard: grass, the gravel drive, the carport within twenty feet of
    # the service porch, the pick-up
    make_box("Yard_Ground", (12.0, -6.0, -0.06), (96.0, 84.0, 0.12), GRASS)   # out past the second house
    make_box("Drive_Gravel", (11.0, -12.0, 0.005), (4.0, 20.0, 0.01), (0.46, 0.44, 0.40, 1.0))
    for s in (-1, 1):
        for t in (-1, 1):
            make_box(f"Carport_Post_{s:+d}{t:+d}", (11.0 + s * 1.8, -4.5 + t * 2.6, 1.15), (0.10, 0.10, 2.3), (0.40, 0.40, 0.40, 1.0))
    make_box("Carport_Roof", (11.0, -4.5, 2.34), (4.2, 5.8, 0.08), (0.50, 0.50, 0.50, 1.0))
    make_chamfer_box("Carport_Car_Body", (11.0, -4.5, 0.70), (1.8, 4.4, 0.80), (0.30, 0.32, 0.36, 1.0), chamfer=0.15)
    make_chamfer_box("Carport_Car_Cabin", (11.0, -4.7, 1.30), (1.6, 2.2, 0.44), (0.16, 0.18, 0.20, 1.0), chamfer=0.10)
    for s in (-1, 1):
        for t in (-1, 1):
            make_cyl(f"Carport_Car_Wheel_{s:+d}{t:+d}", (11.0 + s * 0.80, -4.5 + t * 1.4, 0.32), 0.32, 0.22,
                     (0.10, 0.10, 0.10, 1.0), axis='X', segments=12)
    make_chamfer_box("Pickup_Bed" + PORCH, (-3.0, -9.0, 0.70), (1.9, 2.0, 0.70), (0.40, 0.20, 0.16, 1.0), chamfer=0.08)
    make_chamfer_box("Pickup_Cab" + PORCH, (-3.0, -7.3, 0.95), (1.9, 1.5, 1.20), (0.40, 0.20, 0.16, 1.0), chamfer=0.10)
    make_chamfer_box("Pickup_Hood" + PORCH, (-3.0, -6.1, 0.70), (1.9, 1.0, 0.70), (0.40, 0.20, 0.16, 1.0), chamfer=0.10)
    for s in (-1, 1):
        for t in (-1, 1):
            make_cyl(f"Pickup_Wheel_{s:+d}{t:+d}" + PORCH, (-3.0 + s * 0.90, -7.6 + t * 1.5, 0.36), 0.36, 0.24,
                     (0.10, 0.10, 0.10, 1.0), axis='X', segments=12)
    # the fruit trees between the kitchen and the workshop, the workshop
    for k in range(6):
        make_broadleaf(f"Fruit_Tree_{k}", 12.0 + (k % 3) * 4.0, 5.0 + (k // 3) * 5.0, 4.0, (0.10, 0.14, 0.10, 1.0), (0.20, 0.16, 0.12, 1.0))
    wx, wy = 26.0, 7.0
    make_box("Workshop_Shed", (wx, wy, 1.5), (6.0, 5.0, 3.0), (0.36, 0.32, 0.28, 1.0))
    make_gable("Workshop_Roof", (wx, wy, 3.0 + 0.7), (6.6, 5.6, 1.4), (0.30, 0.30, 0.32, 1.0), ridge_axis='Y')
    make_box("Workshop_Window_Glow", (wx - 3.02, wy, 1.6), (0.04, 1.4, 1.0), (1.0, 0.84, 0.56, 1.0))
    make_box("Workshop_Door_Light_Glow", (wx - 3.02, wy - 1.8, 1.0), (0.04, 0.9, 2.0), (0.96, 0.80, 0.52, 1.0))
    # the yard light on its pole by the workshop's door (2026-10-30): "The
    # workshop light held steady across the dark yard"
    make_cyl("Workshop_Yard_Light_Pole", (wx - 4.0, wy - 3.0, 2.5), 0.08, 5.0, (0.36, 0.30, 0.24, 1.0), segments=8)
    make_box("Workshop_Yard_Light_Arm", (wx - 4.3, wy - 3.0, 4.9), (0.70, 0.06, 0.06), (0.36, 0.30, 0.24, 1.0))
    make_lathe("Workshop_Yard_Light_Shade", (wx - 4.6, wy - 3.0, 4.70), [(0.30, 0.0), (0.18, 0.12), (0.04, 0.18)], (0.30, 0.36, 0.30, 1.0), segments=12)
    make_blob("Workshop_Yard_Light_Bulb_Glow", (wx - 4.6, wy - 3.0, 4.72), 0.07, (1.0, 0.90, 0.64, 1.0), noise=0.02, seed=1, squash=1.1)
    for k in range(5):
        make_rot_box(f"Scrap_Metal_{k}", (wx + 4.2, wy - 1.6 + k * 0.7, 0.03 + k * 0.01), (0.8, 0.10, 0.06 + k * 0.02), (0.36, 0.34, 0.32, 1.0),
                     yaw=k * 0.8)
    make_box("Egg_Stand_Table", (4.0, -20.0, 0.40), (1.2, 0.6, 0.80), WOOD)
    make_box("Egg_Stand_Sign", (4.0, -20.28, 1.05), (0.8, 0.03, 0.5), (0.86, 0.84, 0.78, 1.0))
    # west: the land falls to the valley; ridges beyond, the cloud over the moon
    make_rot_box("Valley_Slope_Ground", (-40.0, 5.0, -10.0), (64.0, 120.0, 1.0), GRASS, pitch=0.32)
    for k in range(4):
        make_box(f"Far_Ridge_Band_{k}", (-100.0 - k * 22.0, 0.0, -10.0 + k * 5.0), (0.2, 360.0, 20.0 + k * 6.0),
                 ((0.06, 0.07, 0.08, 1.0), (0.05, 0.06, 0.07, 1.0))[k % 2])
    make_box("Far_Cloud_Band_Moonlit", (-178.0, 0.0, 46.0), (0.2, 360.0, 22.0), (0.16, 0.18, 0.22, 1.0))
    # 2026-10-23: the two black sky slabs are gone — the preset env draws the
    # clouded night sky (Background3D._apply_preset_env), and a slab's end read
    # as a hard edge over the porch roof.


# where the ranch's rooms stand in the Link home (blender metres)
ROOM_AT = (-5.9, 5.8, H + 0.143)       # the narrator's room, upstairs NW (its N wall on the house's)
SECOND_AT = (0.0, -14.0, 0.0)          # the second house, in the field SE of the yard


def _placed(build, at, prefix, drop=()):
    """Run a ranch room builder, then move what it made to `at` and name it
    `prefix…` — in Blender, and in the audits' recording (their _props
    stubs append to locale_geometry_audit.BOXES), so the gates see the room
    where it stands. Parts whose names start with `drop` (the ranch's painted
    window backdrops: here the real yard is outside) are removed."""
    A = sys.modules.get("locale_geometry_audit")
    mark_boxes = len(A.BOXES) if A is not None else 0
    real = bpy is not None and not isinstance(getattr(bpy, "data", 0.0), float)
    # (by iteration: the dry-run gate's stand-in collection is a list, no .keys())
    before = set(o.name for o in bpy.data.objects) if real else set()
    build()
    dx, dy, dz = at
    if real:
        for o in [o for o in bpy.data.objects if o.name not in before]:
            if o.name.startswith(drop):
                bpy.data.objects.remove(o, do_unlink=True)
                continue
            if o.parent is None:
                o.location = (o.location[0] + dx, o.location[1] + dy, o.location[2] + dz)
            o.name = prefix + o.name
    if A is not None:
        kept = []
        for (n, c, h) in A.BOXES[mark_boxes:]:
            if str(n).startswith(drop):
                continue
            kept.append((prefix + str(n), (c[0] + dx, c[1] + dy, c[2] + dz), h))
        A.BOXES[mark_boxes:] = kept


def main():
    clear_scene()
    import build_small_wood_ranch as RANCH
    # (round 6) the ranch room's far firs ride up with the room to the second
    # storey (they stood 2.2 m in the air); here they are dropped and
    # planted on the ground where they stood, as conifers
    _placed(RANCH.build_bedroom, ROOM_AT, "LR_", drop=("View_N", "Fir_Far"))
    from _props.trees import make_conifer
    for k in range(9):
        make_conifer(f"Fir_Far_{k}", -20.0 + k * 5.0 + ROOM_AT[0], 4.2 + 34.0 + (k % 3) * 4.0 + ROOM_AT[1], 10.0 + (k % 4) * 1.5,
                     (0.12, 0.20, 0.14, 1.0), (0.24, 0.20, 0.16, 1.0), skirt=0.16)
    _placed(RANCH.build_second_house, SECOND_AT, "LS_", drop=("SH_View_E",))
    build_house()
    build_porch_and_yard()
    build_siding_2026_10()
    try:
        join_stock()
    except Exception as _e:
        print("[join_stock] skipped:", _e)
    out = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                        "../../../assets/3d/locales/small_wood_farmhouse.glb"))
    print(f"\n[build_small_wood_farmhouse] exporting to {out}")
    export_glb(out)


if __name__ == "__main__":
    main()
