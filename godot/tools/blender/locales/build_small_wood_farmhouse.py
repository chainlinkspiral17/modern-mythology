"""small_wood_farmhouse — vol 2's farmhouse in the country outside Small Wood
at night (draft 1, 2026-10-18).

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
    make_box("Upper_Storey_Wall_N", (-1.0, 10.0, H + 0.08 + 1.25), (14.4, 0.20, 2.5), SIDING)
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


def build_porch_and_yard():
    # the front porch along the S wall: its boards, posts, roof, rail; the
    # chair, the spit cup, the bottle, the cats
    make_box("Front_Porch_Deck", (-4.0, -1.3, 0.10), (8.4, 2.4, 0.12), (0.44, 0.36, 0.28, 1.0))
    for k in range(8):
        make_box(f"Front_Porch_Board_Seam_{k}", (-7.6 + k * 1.05, -1.3, 0.162), (0.02, 2.4, 0.004), (0.34, 0.28, 0.22, 1.0))
    for k in range(4):
        make_box(f"Front_Porch_Post_{k}", (-8.0 + k * 2.6, -2.4, 1.28), (0.12, 0.12, 2.24), TRIM)
    make_box("Front_Porch_Roof", (-4.0, -1.3, 2.46), (8.8, 2.8, 0.12), ROOF)
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
    make_box("Yard_Ground", (6.0, 0.0, -0.06), (60.0, 60.0, 0.12), GRASS)
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


def main():
    clear_scene()
    build_house()
    build_porch_and_yard()
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
