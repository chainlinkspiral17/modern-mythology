"""lake_house — vol 3's "acceptable losses": Terry's house on the lake, the
last weekend of summer (draft 1, 2026-10-18).

The user: "go ahead and start working on backgrounds for vol 1-4 as needed."
"The car ride to the country, to a large man-made lake in the middle of
nowhere" (unnamed; Texas; not the vol 6 boat ramp at Lake Palestine).
  "A barbecue is set up, something is smoking underneath the lid"; "a big
   home on the lake, a boathouse out back"; Terry "pushes the screen door
   open with his back"                   → the front (lake_house_day)
  Chris's room: "There's a cot set up for me by the window"; "I set my shit
   down in the corner"; "autographed Texas Ranger posters all over"; "A
   television is in the corner with a pile of tapes"; "a stack of
   magazines"; "The room is clean and sterile." That night the boys play
   five-card stud across from each other, candy, a licorice stick; the cot,
   its pillow, the zippered sleeping bag; "the light still on"
                                         → chris_room_day / chris_room_night
  the bathroom, "the middle of the night or early in the morning"
                                         → lake_bath_night
  the dock: "polished wood"; Dad "sitting with his legs over the water";
   "Light breaks on the water in long white seams, far boats trailing
   their wakes like chalk"; "Sailboats and speedboats", "hot air balloons
   take off on some distant" shore       → lake_dock_day
  morning: the kitchen, a table, "watching the sun crawl over the
   horizon. Terry is outside the window fishing off the dock"; "the
   sliding glass door"                   → lake_dock_dawn (from the table)
The sun rises over the lake, so the lake lies EAST of the house.

Blender: x east, y north, z up; Godot (x, z, -y). House x -10..10,
y -8..8; the shore at x 22; the dock runs east from (22, -4).

DRAFT 2 (2026-10-23, pass 156): the sweep sheet read it as a bare beige
box with a grey slab behind it. The windows are the kit's (frame, stool,
casing, glass) in place of empty frames; white lap siding with casings
and sills on all four faces, shutters on the front, corner boards; the
per-hour sky PLANES are gone (their ends showed as the slab) and each
preset carries its sky in its env.
DRAFT 3 targets: the boathouse's inside and the ski boat; Terry at the
dock's end as a silhouette pass (people are the VN's sprites, so only if
the director asks); the hall and the parents' door; the drive's car.
"""
import os, sys, math
_BT = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
if _BT not in sys.path: sys.path.insert(0, _BT)
from _props.geometry import (clear_scene, make_box, make_cyl, make_chamfer_box, make_rot_box, make_blob, make_lathe, make_gable,
                             join_stock, export_glb)
from _props.structure import make_floor, make_wall, make_wall_with_openings, make_window, make_lap_siding
from _props.furniture import make_bed, make_chair, make_table, make_lamp
from _props.trees import make_broadleaf

H, T = 2.7, 0.20
WALL = (0.90, 0.88, 0.82, 1.0); BASE = (0.60, 0.56, 0.50, 1.0)
PAL = {"wall": WALL, "baseboard": BASE}
EXT = (0.78, 0.74, 0.64, 1.0); ROOF = (0.34, 0.30, 0.28, 1.0); EXT_SIDING = (0.88, 0.87, 0.80, 1.0)
OAK = (0.62, 0.48, 0.32, 1.0); DOCK = (0.64, 0.48, 0.30, 1.0)
LAWN = (0.36, 0.46, 0.24, 1.0); WATER = (0.30, 0.36, 0.32, 1.0)
DOOR = (0.86, 0.84, 0.80, 1.0); TRIM = (0.94, 0.94, 0.92, 1.0)
DAY = "__lake_house_day__lake_dock_day__chris_room_day"
DAWN = "__lake_dock_dawn"
OUT = "__lake_house_day__lake_dock_day"    # long names: Blender cuts at 63 characters
NIGHT = "__chris_room_night__lake_bath_night"
SHORE = 22.0
WL = -0.40                                  # the lake's surface below the lawn


def frame_window(name, wall_axis, along, at, cz, w, h, depth=T):
    """A white frame in an opening — the sliding door's. (Draft 2: the
    windows are the kit's make_window; this stays for the slider.)"""
    for s in (-1, 1):
        if wall_axis == 'X':
            make_box(f"{name}_Frame_Jamb_{s:+d}", (along + s * (w / 2.0 - 0.03), at, cz), (0.06, depth + 0.02, h), TRIM)
        else:
            make_box(f"{name}_Frame_Jamb_{s:+d}", (at, along + s * (w / 2.0 - 0.03), cz), (depth + 0.02, 0.06, h), TRIM)
    for s, zz in ((-1, cz - h / 2.0 + 0.03), (1, cz + h / 2.0 - 0.03)):
        if wall_axis == 'X':
            make_box(f"{name}_Frame_Rail_{s:+d}", (along, at, zz), (w - 0.12, depth + 0.02, 0.06), TRIM)
        else:
            make_box(f"{name}_Frame_Rail_{s:+d}", (at, along, zz), (depth + 0.02, w - 0.12, 0.06), TRIM)


def build_shell():
    make_floor("House_Floor", (0.0, 0.0, 0.0), size_x=20.0, size_y=16.0,
               palette={"vinyl": (0.66, 0.52, 0.36, 1.0), "seam": (0.58, 0.46, 0.32, 1.0)}, style="plank")
    make_box("House_Ceil", (0.0, 0.0, H + 0.04), (20.4, 16.4, 0.08), (0.94, 0.94, 0.92, 1.0))
    make_gable("House_Roof", (0.0, 0.0, H + 0.08 + 1.30), (21.6, 17.6, 2.60), ROOF, ridge_axis='X')
    # exterior walls and their openings (along = absolute x or y)
    make_wall_with_openings("Wall_S", (0.0, -8.0, 0), length=20.4, height=H, thickness=T, axis='X', palette=PAL,
                            baseboard_face_sign=+1, openings=[(-2.0, 1.05, 0.96, 2.1), (5.0, 1.45, 1.8, 1.3), (-8.0, 1.45, 1.4, 1.3)])
    make_wall_with_openings("Wall_N", (0.0, 8.0, 0), length=20.4, height=H, thickness=T, axis='X', palette=PAL,
                            baseboard_face_sign=-1, openings=[(-6.5, 1.45, 1.6, 1.3), (6.0, 1.55, 1.6, 1.0)])
    make_wall_with_openings("Wall_W", (-10.0, 0.0, 0), length=16.0, height=H, thickness=T, axis='Y', palette=PAL,
                            baseboard_face_sign=+1, openings=[(-2.0, 1.95, 0.6, 0.5)])
    make_wall_with_openings("Wall_E", (10.0, 0.0, 0), length=16.0, height=H, thickness=T, axis='Y', palette=PAL,
                            baseboard_face_sign=-1, openings=[(-2.5, 1.05, 2.4, 2.1), (3.0, 1.45, 2.0, 1.3)])
    # draft 2 (pass 156): real windows — the kit's frame, stool and casing
    # and a glass pane (draft 1's were empty white frames)
    for nm, ax, al, at, cz, w, h in (("Win_Kitchen_S", 'X', 5.0, -8.0, 1.45, 1.8, 1.3), ("Win_SW", 'X', -8.0, -8.0, 1.45, 1.4, 1.3),
                                     ("Win_Chris", 'X', -6.5, 8.0, 1.45, 1.6, 1.3), ("Win_Kitchen_N", 'X', 6.0, 8.0, 1.55, 1.6, 1.0),
                                     ("Win_Bath", 'Y', -2.0, -10.0, 1.95, 0.6, 0.5), ("Win_Table", 'Y', 3.0, 10.0, 1.45, 2.0, 1.3)):
        rd = -1 if at > 0 else 1
        anchor = (al, at + rd * 0.10, cz) if ax == 'X' else (at + rd * 0.10, al, cz)
        make_window(nm, anchor, width=w - 0.10, height=h - 0.08, axis=ax, room_dir=rd, see_through=True,
                    cross_mullion=(nm != "Win_Bath"), palette={"frame": TRIM})
        pane = (w, 0.02, h) if ax == 'X' else (0.02, w, h)
        make_box(nm + "_Pane", (al, at, cz) if ax == 'X' else (at, al, cz), pane, (0.80, 0.86, 0.90, 0.25))
    # the outside: white lap siding on all four faces, corner boards
    for nm, ax, line, a0, a1, ops, rs in (("S", 'X', -8.0 - T / 2.0, -10.0 - T / 2.0, 10.0 + T / 2.0,
                                           [(-2.0, 1.05, 0.96, 2.1), (5.0, 1.45, 1.8, 1.3), (-8.0, 1.45, 1.4, 1.3)], +1),
                                          ("N", 'X', 8.0 + T / 2.0, -10.0 - T / 2.0, 10.0 + T / 2.0,
                                           [(-6.5, 1.45, 1.6, 1.3), (6.0, 1.55, 1.6, 1.0)], -1),
                                          ("W", 'Y', -10.0 - T / 2.0, -8.0 - T / 2.0, 8.0 + T / 2.0, [(-2.0, 1.95, 0.6, 0.5)], +1),
                                          ("E", 'Y', 10.0 + T / 2.0, -8.0 - T / 2.0, 8.0 + T / 2.0,
                                           [(-2.5, 1.05, 2.4, 2.1), (3.0, 1.45, 2.0, 1.3)], -1)):
        make_lap_siding(f"Siding_{nm}", ax, line, a0 - 0.022, a1 + 0.022, ops, rs, height=H, color=EXT_SIDING,
                        trim_col=TRIM, shutters=(nm == "S"))
    for k, (cx, cy) in enumerate(((-10.0, -8.0), (10.0, -8.0), (-10.0, 8.0), (10.0, 8.0))):
        make_box(f"Corner_Board_{k}", (cx + (0.132 if cx > 0 else -0.132), cy + (0.132 if cy > 0 else -0.132), H / 2.0), (0.12, 0.12, H), TRIM)
    make_box("Win_Table_Mullion", (10.0, 3.0, 1.45), (T + 0.02, 0.05, 1.2), TRIM)
    # the sliding glass door: its frame, the fixed half, the open half
    frame_window("Slider", 'Y', -2.5, 10.0, 1.05, 2.4, 2.1)
    # the panels as stiles and rails (a solid board over the glass reads as
    # a wall: window_backing_audit); the open one slid behind the fixed one
    for nm, px, py in (("Slider_Fixed", 10.03, -3.1), ("Slider_Open", 9.96, -2.9)):
        for s_ in (-1, 1):
            make_box(f"{nm}_Stile_{s_:+d}", (px, py + s_ * 0.53, 1.05), (0.05, 0.06, 2.0), TRIM)
        for zz in (0.08, 2.02):
            make_box(f"{nm}_Rail_{zz:.2f}", (px, py, zz), (0.05, 1.0, 0.06), TRIM)
    make_box("Slider_Fixed_Panel_Glass", (10.03, -3.1, 1.05), (0.02, 1.0, 1.88), (0.70, 0.78, 0.80, 1.0))
    # interior walls: Chris's room x -10..-2, y 2..8; the hall y 0..2;
    # the bathroom x -10..-6, y -4..0; the parents' room x -2..2, y 2..8
    make_wall_with_openings("Wall_Chris_S", (-6.0, 2.0, 0), length=8.0, height=H, thickness=0.12, axis='X', palette=PAL,
                            baseboard_face_sign=+1, openings=[(-3.2, 1.0, 0.86, 2.0)])
    make_wall("Wall_Chris_E", (-2.0, 5.0, 0), length=5.88, height=H, thickness=0.12, axis='Y', palette=PAL, baseboard_face_sign=-1)
    make_wall_with_openings("Wall_Parents_S", (0.0, 2.0, 0), length=3.88, height=H, thickness=0.12, axis='X', palette=PAL,
                            baseboard_face_sign=-1, openings=[(0.0, 1.0, 0.86, 2.0)])
    make_wall("Wall_Kitchen_W", (2.0, 4.0, 0), length=7.8, height=H, thickness=0.12, axis='Y', palette=PAL, baseboard_face_sign=+1)
    make_wall_with_openings("Wall_Bath_N", (-8.0, 0.0, 0), length=3.88, height=H, thickness=0.12, axis='X', palette=PAL,
                            baseboard_face_sign=-1, openings=[(-7.0, 1.0, 0.80, 2.0)])
    make_wall("Wall_Bath_E", (-6.0, -2.0, 0), length=4.12, height=H, thickness=0.12, axis='Y', palette=PAL, baseboard_face_sign=+1)
    make_wall("Wall_Bath_S", (-8.0, -4.0, 0), length=3.88, height=H, thickness=0.12, axis='X', palette=PAL, baseboard_face_sign=+1)
    make_wall_with_openings("Wall_SW_E", (-6.0, -6.0, 0), length=3.88, height=H, thickness=0.12, axis='Y', palette=PAL,
                            baseboard_face_sign=+1, openings=[(-5.2, 1.0, 0.80, 2.0)])
    make_box("Door_SW_Shut", (-6.0, -5.2, 1.0), (0.04, 0.78, 2.0), DOOR)
    make_box("Door_Parents_Shut", (0.0, 2.0, 1.0), (0.78, 0.04, 2.0), DOOR)
    make_box("Door_Chris_Open", (-3.2 + 0.41, 2.06 + 0.40, 1.0), (0.04, 0.80, 2.0), DOOR)
    make_box("Door_Bath_Open", (-7.0 + 0.41, -0.06 - 0.40, 1.0), (0.04, 0.80, 2.0), DOOR)
    # the front door and its screen door, standing open
    make_box("Front_Door_Open", (-2.0 - 0.46, -8.0 + 0.10 + 0.44, 1.05), (0.04, 0.86, 2.06), (0.60, 0.44, 0.30, 1.0))
    sx, sy = -2.0 + 0.40, -8.0 - 0.10 - 0.42
    for s in (-1, 1):
        make_box(f"Screen_Door_Frame_Stile_{s:+d}", (sx, sy + s * 0.40, 1.03), (0.04, 0.05, 2.04), TRIM)
    for zz in (0.06, 1.03, 2.02):
        make_box(f"Screen_Door_Frame_Rail_{zz:.2f}", (sx, sy, zz), (0.04, 0.76, 0.06), TRIM)
    for k in range(8):
        make_box(f"Screen_Door_Mesh_Wire_{k}", (sx, sy, 0.16 + k * 0.24), (0.01, 0.76, 0.006), (0.40, 0.42, 0.42, 1.0))
    make_box("Front_Step_Slab", (-2.0, -9.0, 0.06), (2.4, 1.6, 0.12), (0.62, 0.60, 0.56, 1.0))


def build_chris_room():
    x0, x1, y0, y1 = -9.9, -2.06, 2.06, 7.9
    # Chris's bed along the W wall, head W, made tight
    make_bed("Chris_Bed", x0 + 0.06 + 0.98, 4.2, head="-X", w=1.0, d=1.95, made=True, blanket_col=(0.20, 0.30, 0.56, 1.0))
    # the cot by the window (N wall), the pillow, the sleeping bag
    cx, cy = -6.5, y1 - 0.06 - 0.40
    for s in (-1, 1):
        for t in (-1, 1):
            make_box(f"Cot_Leg_{s:+d}{t:+d}", (cx + s * 0.88, cy + t * 0.32, 0.18), (0.03, 0.03, 0.36), (0.40, 0.40, 0.38, 1.0))
    make_box("Cot_Canvas", (cx, cy, 0.38), (1.90, 0.72, 0.04), (0.40, 0.44, 0.30, 1.0))
    make_box("Cot_Pillow", (cx - 0.70, cy, 0.46), (0.40, 0.56, 0.12), (0.94, 0.93, 0.90, 1.0))
    make_box("Cot_Sleeping_Bag" + DAY, (cx + 0.20, cy, 0.44), (1.40, 0.66, 0.08), (0.20, 0.42, 0.30, 1.0))
    make_box("Cot_Sleeping_Bag_Open" + NIGHT, (cx + 0.20, cy, 0.44), (1.40, 0.66, 0.08), (0.20, 0.42, 0.30, 1.0))
    make_rot_box("Cot_Sleeping_Bag_Flap" + NIGHT, (cx + 0.20, cy - 0.46, 0.36), (1.40, 0.30, 0.04), (0.70, 0.30, 0.20, 1.0), roll=-0.9)
    # the corner where the narrator's things go (NW), his bag
    make_chamfer_box("Duffel_Bag", (x0 + 0.45, y1 - 0.40, 0.17), (0.70, 0.34, 0.34), (0.16, 0.18, 0.24, 1.0), chamfer=0.10)
    make_box("Backpack", (x0 + 0.35, y1 - 0.90, 0.22), (0.30, 0.22, 0.44), (0.50, 0.20, 0.18, 1.0))
    # the TV in the NE corner on a low stand, the pile of tapes
    tx, ty = x1 - 0.40, y1 - 0.36
    make_box("TV_Stand", (tx, ty, 0.25), (0.70, 0.56, 0.50), (0.30, 0.24, 0.20, 1.0))
    make_chamfer_box("TV_Set", (tx, ty - 0.02, 0.73), (0.56, 0.44, 0.46), (0.14, 0.14, 0.14, 1.0), chamfer=0.03)
    make_rot_box("TV_Screen", (tx - 0.14, ty - 0.18, 0.75), (0.40, 0.006, 0.32), (0.10, 0.12, 0.14, 1.0), yaw=0.0)
    for k in range(7):
        make_box(f"Tape_Stock_{k}", (tx - 0.10 + (k % 2) * 0.04, ty + 0.10 - 0.62, 0.012 + k * 0.026), (0.19, 0.11, 0.025),
                 (0.10, 0.10, 0.10, 1.0))
    # the dresser on the E wall, the magazines stacked square on it
    make_box("Dresser", (x1 - 0.26, 4.6, 0.45), (0.50, 1.20, 0.90), OAK)
    for k in range(3):
        make_box(f"Dresser_Drawer_Line_{k}", (x1 - 0.512, 4.6, 0.25 + k * 0.28), (0.004, 1.10, 0.02), (0.44, 0.34, 0.22, 1.0))
    for k in range(6):
        make_box(f"Magazine_Stock_{k}", (x1 - 0.30, 4.40, 0.906 + k * 0.012), (0.27, 0.21, 0.010),
                 ((0.86, 0.20, 0.20, 1.0), (0.20, 0.30, 0.66, 1.0), (0.92, 0.90, 0.86, 1.0))[k % 3])
    make_lathe("Dresser_Trophy", (x1 - 0.30, 4.95, 0.90), [(0.0, 0.0), (0.06, 0.0), (0.06, 0.06), (0.02, 0.08), (0.02, 0.16),
                                                          (0.06, 0.22), (0.07, 0.30), (0.0, 0.30)], (0.86, 0.72, 0.30, 1.0), segments=10)
    # the posters, all over: autographed Rangers, Pudge, Nolan Ryan's 5000th
    k = 0
    for (px, py, ax) in [(-9.0, y1, 'N'), (-8.2, y1, 'N'), (-4.6, y1, 'N'), (-3.4, y1, 'N'),
                         (x0, 3.1, 'W'), (x0, 5.6, 'W'), (x0, 6.8, 'W'),
                         (x1, 3.2, 'E'), (x1, 6.0, 'E'), (x1, 7.0, 'E'),
                         (-8.4, y0, 'S'), (-6.6, y0, 'S'), (-5.0, y0, 'S')]:
        col = ((0.12, 0.22, 0.56, 1.0), (0.80, 0.16, 0.18, 1.0), (0.92, 0.92, 0.90, 1.0))[k % 3]
        z = 1.55 + (k % 2) * 0.08
        if ax == 'N':
            make_box(f"Poster_{k}", (px, y1 - 0.003, z), (0.62, 0.006, 0.88), col)
            make_box(f"Poster_{k}_Signature", (px, y1 - 0.008, z - 0.30), (0.30, 0.004, 0.04), (0.06, 0.06, 0.08, 1.0))
        elif ax == 'S':
            make_box(f"Poster_{k}", (px, y0 + 0.003, z), (0.62, 0.006, 0.88), col)
            make_box(f"Poster_{k}_Signature", (px, y0 + 0.008, z - 0.30), (0.30, 0.004, 0.04), (0.06, 0.06, 0.08, 1.0))
        else:
            xx = x0 + 0.003 if ax == 'W' else x1 - 0.003
            sx = 0.005 if ax == 'W' else -0.005
            make_box(f"Poster_{k}", (xx, py, z), (0.006, 0.62, 0.88), col)
            make_box(f"Poster_{k}_Signature", (xx + sx, py, z - 0.30), (0.004, 0.30, 0.04), (0.06, 0.06, 0.08, 1.0))
        k += 1
    # the overhead light (on all night), the rug
    make_cyl("Chris_Ceiling_Fixture_Glow", (-6.0, 5.0, H - 0.05), 0.22, 0.08, (0.98, 0.96, 0.90, 1.0), segments=14)
    make_box("Chris_Rug", (-6.0, 5.0, 0.004), (2.4, 1.8, 0.008), (0.60, 0.62, 0.66, 1.0))
    # that night: the card game on the floor in the corner, the candy
    gx, gy = -8.4, 6.5
    for k in range(5):
        make_rot_box(f"Card_Hand_A_{k}" + NIGHT, (gx - 0.30 + k * 0.05, gy - 0.25, 0.011), (0.06, 0.09, 0.002), (0.96, 0.96, 0.94, 1.0), yaw=k * 0.2)
        make_rot_box(f"Card_Hand_B_{k}" + NIGHT, (gx + 0.30 + k * 0.05, gy + 0.22, 0.011), (0.06, 0.09, 0.002), (0.96, 0.96, 0.94, 1.0), yaw=-k * 0.2)
    make_box("Card_Deck" + NIGHT, (gx, gy, 0.020), (0.06, 0.09, 0.024), (0.70, 0.16, 0.16, 1.0))
    make_chamfer_box("Candy_Bag" + NIGHT, (gx + 0.40, gy - 0.40, 0.12), (0.26, 0.16, 0.24), (0.90, 0.80, 0.30, 1.0), chamfer=0.04)
    for k in range(6):
        make_box(f"Candy_Wrapper_{k}" + NIGHT, (gx - 0.2 + k * 0.12, gy + (k % 2) * 0.16 - 0.05, 0.012), (0.05, 0.03, 0.006),
                 ((0.90, 0.30, 0.30, 1.0), (0.30, 0.60, 0.90, 1.0), (0.96, 0.84, 0.30, 1.0))[k % 3])
    make_rot_box("Licorice_Stick" + NIGHT, (gx + 0.10, gy + 0.40, 0.015), (0.28, 0.014, 0.014), (0.50, 0.06, 0.06, 1.0), yaw=0.6)


def build_bath():
    """x -9.9..-6.06, y -3.94..-0.06: the tub along the S wall, the toilet,
    the vanity and mirror on the E wall; the light on over the mirror."""
    make_box("Bath_Tile_Floor", (-8.0, -2.0, 0.004), (3.84, 3.88, 0.008), (0.86, 0.88, 0.86, 1.0))
    make_box("Tub_Body", (-8.0, -3.94 + 0.38, 0.28), (3.0, 0.76, 0.56), (0.94, 0.94, 0.92, 1.0))
    make_box("Tub_Inner_Dark", (-8.0, -3.56, 0.565), (2.7, 0.56, 0.01), (0.80, 0.82, 0.82, 1.0))
    make_box("Tub_Curtain_Rod", (-7.98, -3.94 + 0.78, 2.02), (3.84, 0.02, 0.02), (0.70, 0.70, 0.72, 1.0))
    make_box("Tub_Curtain", (-8.9, -3.94 + 0.78, 1.36), (1.6, 0.02, 1.28), (0.56, 0.70, 0.76, 1.0))
    # the toilet against the W wall, lid up
    # (2026-10-30: a bowl, not a box — the pedestal narrowing to the floor,
    # the seat's ring down)
    make_lathe("Toilet_Bowl", (-9.9 + 0.40, -1.6, 0.0), [(0.0, 0.0), (0.13, 0.0), (0.12, 0.10), (0.15, 0.24), (0.20, 0.36), (0.19, 0.39), (0.0, 0.39)],
               (0.96, 0.96, 0.94, 1.0), segments=16)
    make_cyl("Toilet_Seat_Ring", (-9.9 + 0.40, -1.6, 0.405), 0.205, 0.03, (0.94, 0.94, 0.92, 1.0), segments=16)
    make_box("Toilet_Tank", (-9.9 + 0.12, -1.6, 0.62), (0.20, 0.46, 0.44), (0.96, 0.96, 0.94, 1.0))
    make_rot_box("Toilet_Lid_Up", (-9.9 + 0.25, -1.6, 0.66), (0.03, 0.38, 0.44), (0.96, 0.96, 0.94, 1.0), pitch=-0.15)
    make_box("Toilet_Paper_Roll_Mounted", (-9.85, -1.0, 0.70), (0.10, 0.12, 0.12), (0.96, 0.96, 0.94, 1.0))
    # the vanity on the E wall, the mirror, the light over it
    vx = -6.06 - 0.28
    make_box("Vanity_Cabinet", (vx, -1.6, 0.42), (0.56, 1.20, 0.84), (0.76, 0.68, 0.56, 1.0))
    make_box("Vanity_Counter", (vx, -1.6, 0.86), (0.58, 1.24, 0.04), (0.90, 0.88, 0.84, 1.0))
    make_box("Vanity_Basin", (vx, -1.6, 0.882), (0.36, 0.44, 0.006), (0.96, 0.96, 0.94, 1.0))
    make_box("Vanity_Mirror_Mounted", (-6.06 - 0.012, -1.6, 1.50), (0.02, 1.00, 0.80), (0.66, 0.72, 0.76, 1.0))
    make_box("Vanity_Light_Bar_Mounted", (-6.06 - 0.05, -1.6, 2.02), (0.08, 0.80, 0.10), (0.92, 0.90, 0.80, 1.0))
    for k in range(4):
        make_blob(f"Vanity_Bulb_Glow_{k}", (-6.06 - 0.10, -1.9 + k * 0.2, 2.00), 0.04, (1.0, 0.96, 0.84, 1.0), noise=0.0, seed=k)
    make_box("Towel_Bar_Mounted", (-8.0, -0.08, 1.20), (0.70, 0.04, 0.03), (0.70, 0.70, 0.72, 1.0))
    make_box("Towel_Hang", (-8.0, -0.11, 0.92), (0.50, 0.02, 0.56), (0.70, 0.86, 0.88, 1.0))
    make_box("Bath_Mat", (-8.4, -2.9, 0.012), (0.80, 0.50, 0.010), (0.70, 0.86, 0.88, 1.0))
    # (2026-10-30) the small frosted window over the toilet's corner, black
    # with the hour; a waste basket, a magazine on the tank, a night light
    wx = -9.94 + 0.005
    make_box("Bath_Window_Frame", (wx, -2.6, 1.65), (0.02, 0.70, 0.86), (0.90, 0.88, 0.84, 1.0))
    make_box("Bath_Window_Frosted", (wx + 0.012, -2.6, 1.65), (0.004, 0.58, 0.74), (0.14, 0.16, 0.22, 1.0))
    make_box("Bath_Window_Muntin", (wx + 0.016, -2.6, 1.65), (0.004, 0.58, 0.03), (0.90, 0.88, 0.84, 1.0))
    make_cyl("Bath_Waste_Basket", (-9.62, -2.35, 0.14), 0.12, 0.28, (0.80, 0.84, 0.86, 1.0), segments=14)
    make_box("Bath_Magazine", (-9.8, -1.52, 0.846), (0.16, 0.22, 0.012), (0.70, 0.30, 0.24, 1.0))
    make_box("Bath_Night_Light", (-6.06 - 0.02, -0.7, 0.32), (0.03, 0.06, 0.08), (1.0, 0.90, 0.60, 1.0))


def build_kitchen():
    """x 2.06..9.9, y -7.9..7.9: the counter on the N wall, the table by the
    E window looking at the dock, the sliding glass door."""
    make_box("Counter_Run", (6.0, 7.9 - 0.32, 0.45), (6.4, 0.64, 0.90), (0.70, 0.62, 0.48, 1.0))
    make_box("Counter_Top", (6.0, 7.9 - 0.32, 0.92), (6.44, 0.66, 0.04), (0.88, 0.86, 0.80, 1.0))
    make_box("Upper_Cabinets_W", (3.9, 7.9 - 0.18, 1.90), (2.2, 0.36, 0.80), (0.70, 0.62, 0.48, 1.0))
    make_box("Upper_Cabinets_E", (8.4, 7.9 - 0.18, 1.90), (2.2, 0.36, 0.80), (0.70, 0.62, 0.48, 1.0))
    make_box("Fridge", (2.06 + 0.40, 6.6, 0.90), (0.76, 0.76, 1.80), (0.92, 0.92, 0.90, 1.0))
    make_box("Cereal_Box", (7.4, 7.6, 1.08), (0.20, 0.07, 0.30), (0.86, 0.56, 0.20, 1.0))
    # the table by the E window, four chairs, the granola box
    tx, ty = 8.4, 3.0
    make_table("Kitchen_Table", tx, ty, w=1.0, d=1.6, h=0.75, wood=OAK)
    make_chair("Kitchen_Chair_W", tx - 0.80, ty, yaw=-math.pi / 2.0, wood=OAK)
    make_chair("Kitchen_Chair_S", tx, ty - 1.10, yaw=0.0, wood=OAK)
    make_chair("Kitchen_Chair_N", tx, ty + 1.10, yaw=math.pi, wood=OAK)
    make_box("Granola_Box", (tx - 0.20, ty - 0.30, 0.902), (0.20, 0.07, 0.30), (0.40, 0.56, 0.30, 1.0))
    make_box("Granola_Box_Base", (tx - 0.20, ty - 0.30, 0.756), (0.20, 0.07, 0.004), (0.40, 0.56, 0.30, 1.0))
    # the living room beyond (x -6..2, y -8..0): a sofa, a low table
    make_box("Sofa_Base", (-2.0, -5.0, 0.24), (2.2, 0.90, 0.48), (0.56, 0.50, 0.42, 1.0))
    make_box("Sofa_Back", (-2.0, -5.38, 0.70), (2.2, 0.16, 0.50), (0.56, 0.50, 0.42, 1.0))
    make_box("Low_Table", (-2.0, -3.6, 0.20), (1.2, 0.60, 0.40), OAK)


def build_grounds():
    # the lawn to the shore, the drive, the barbecue smoking at the front
    make_box("Lawn_Ground", (-9.0, 0.0, -0.06), (62.0, 120.0, 0.12), LAWN)
    make_box("Drive_Gravel", (-16.0, -20.0, 0.004), (4.0, 24.0, 0.008), (0.62, 0.58, 0.50, 1.0))
    make_box("Drive_Turnaround_Gravel", (-10.0, -11.0, 0.004), (12.0, 5.0, 0.008), (0.62, 0.58, 0.50, 1.0))
    bx, by = -5.0, -10.4
    for k in range(3):
        a = k * 2.0 * math.pi / 3.0
        make_rot_box(f"Barbecue_Leg_{k}", (bx + 0.22 * math.cos(a), by + 0.22 * math.sin(a), 0.36), (0.03, 0.03, 0.74),
                     (0.16, 0.16, 0.16, 1.0), roll=0.18 * math.sin(a), pitch=0.18 * math.cos(a))
    make_lathe("Barbecue_Kettle", (bx, by, 0.66), [(0.0, 0.0), (0.22, 0.02), (0.29, 0.12), (0.30, 0.22), (0.0, 0.22)],
               (0.12, 0.12, 0.13, 1.0), segments=16)
    make_lathe("Barbecue_Lid", (bx, by, 0.88), [(0.30, 0.0), (0.28, 0.10), (0.18, 0.20), (0.0, 0.24)], (0.12, 0.12, 0.13, 1.0), segments=16)
    for k in range(5):
        make_blob(f"Barbecue_Smoke_Cloud_{k}", (bx + 0.10 * k, by + 0.05 * k, 1.30 + k * 0.38), 0.18 + k * 0.06, (0.80, 0.80, 0.80, 1.0),
                  noise=0.3, seed=40 + k)
    # the deck off the sliding door, the steps to the lawn
    make_box("Deck_Boards", (11.6, -2.5, 0.20), (3.0, 5.0, 0.08), DOCK)
    for k in range(6):
        make_box(f"Deck_Board_Seam_{k}", (11.6, -4.8 + k * 0.9, 0.242), (3.0, 0.02, 0.004), (0.46, 0.34, 0.22, 1.0))
    for s in (-1, 1):
        for t in (-1, 1):
            make_box(f"Deck_Post_{s:+d}{t:+d}", (11.6 + s * 1.4, -2.5 + t * 2.4, 0.08), (0.12, 0.12, 0.16), (0.44, 0.34, 0.24, 1.0))
    # the shore: the bank falling to the water, reeds
    make_rot_box("Shore_Bank", (SHORE + 0.6, 0.0, -0.22), (1.6, 120.0, 0.20), (0.46, 0.40, 0.30, 1.0), pitch=0.28)
    for k in range(10):
        make_blob(f"Shore_Reed_Plant_{k}", (SHORE + 0.5, -40.0 + k * 9.0 + (k % 3), 0.10), 0.35, (0.40, 0.48, 0.26, 1.0), noise=0.4,
                  seed=60 + k, squash=1.4)
    make_box("Lake_Water", (SHORE + 84.0, 0.0, WL), (168.0, 400.0, 0.04), WATER)
    # the dock: polished wood, east from the shore at y -4, its pilings
    dy, dx0, dx1 = -4.0, SHORE - 0.6, SHORE + 15.0
    make_box("Dock_Deck", ((dx0 + dx1) / 2.0, dy, 0.10), (dx1 - dx0, 2.2, 0.08), DOCK)
    for k in range(int((dx1 - dx0) / 0.6)):
        make_box(f"Dock_Plank_Seam_{k}", (dx0 + 0.3 + k * 0.6, dy, 0.142), (0.02, 2.2, 0.004), (0.50, 0.36, 0.22, 1.0))
    for k in range(6):
        for s in (-1, 1):
            make_cyl(f"Dock_Piling_{k}_{s:+d}", (dx0 + 1.2 + k * 2.8, dy + s * 1.0, -0.70), 0.10, 1.52, (0.40, 0.32, 0.24, 1.0), segments=8)
    make_box("Dock_Cleat_Mounted", (dx1 - 0.3, dy + 0.9, 0.17), (0.24, 0.06, 0.06), (0.30, 0.30, 0.32, 1.0))
    make_box("Ski_Boots_Pair", (dx1 - 0.8, dy - 0.3, 0.19), (0.30, 0.26, 0.10), (0.20, 0.30, 0.60, 1.0))
    make_box("Shirt_Bundle", (dx1 - 1.6, dy + 0.70, 0.17), (0.34, 0.24, 0.06), (0.86, 0.86, 0.84, 1.0))
    make_box("Fishing_Rod_Holder_Mounted__lake_dock_dawn", (dx1 - 0.2, dy - 1.05, 0.30), (0.06, 0.06, 0.30), (0.30, 0.30, 0.32, 1.0))
    make_rot_box("Fishing_Rod_Hang__lake_dock_dawn", (dx1 + 0.6, dy - 1.05, 1.0), (2.2, 0.02, 0.02), (0.20, 0.18, 0.16, 1.0), pitch=-0.6)
    make_box("Tackle_Box__lake_dock_dawn", (dx1 - 1.0, dy - 0.6, 0.24), (0.40, 0.22, 0.20), (0.30, 0.50, 0.30, 1.0))
    # the boathouse out back, astride the shore N of the dock
    hx, hy = SHORE + 2.0, 8.0
    make_box("Boathouse_Wall_N", (hx, hy + 2.6, 0.9), (8.0, 0.16, 2.6), (0.56, 0.40, 0.30, 1.0))
    make_box("Boathouse_Wall_S", (hx, hy - 2.6, 0.9), (8.0, 0.16, 2.6), (0.56, 0.40, 0.30, 1.0))
    make_box("Boathouse_Wall_W", (hx - 4.0, hy, 0.9), (0.16, 5.36, 2.6), (0.56, 0.40, 0.30, 1.0))
    make_box("Boathouse_Door_W", (hx - 4.09, hy, 0.95), (0.02, 0.90, 1.9), (0.40, 0.28, 0.20, 1.0))
    make_rot_box("Boathouse_Roof_N", (hx, hy + 1.4, 2.62), (8.6, 3.1, 0.12), ROOF, roll=0.40)
    make_rot_box("Boathouse_Roof_S", (hx, hy - 1.4, 2.62), (8.6, 3.1, 0.12), ROOF, roll=-0.40)
    make_box("Boathouse_Gable_Dark", (hx + 3.98, hy, 1.6), (0.02, 5.1, 1.2), (0.12, 0.10, 0.08, 1.0))
    # trees round the lot
    for k, (x, y) in enumerate(((-24.0, 14.0), (-20.0, -4.0), (-26.0, -26.0), (-6.0, 18.0), (6.0, 20.0), (14.0, -18.0), (-14.0, 24.0))):
        make_broadleaf(f"Lot_Tree_{k}", x, y, 7.0 + (k % 3), (0.26, 0.38, 0.20, 1.0), (0.36, 0.28, 0.20, 1.0))


def build_lake():
    """Out on the lake: the boats, the wakes, the light's seams, the far
    shore and the balloons over it; the sky per hour."""
    # sailboats and speedboats with their wakes
    for k, (x, y, yaw) in enumerate(((70.0, 30.0, 0.3), (120.0, -40.0, -0.2), (150.0, 50.0, 0.6))):
        make_chamfer_box(f"Sailboat_Hull_{k}", (x, y, WL + 0.30), (5.0, 1.6, 0.70), (0.94, 0.94, 0.92, 1.0), chamfer=0.25, yaw=yaw)
        make_cyl(f"Sailboat_Mast_{k}", (x, y, WL + 4.4), 0.06, 7.6, (0.80, 0.80, 0.80, 1.0), segments=6)
        make_rot_box(f"Sailboat_Sail_{k}", (x - 1.0 * math.cos(yaw), y - 1.0 * math.sin(yaw), WL + 4.0), (1.9, 0.03, 6.0),
                     (0.96, 0.95, 0.90, 1.0), yaw=yaw, pitch=0.12)
    for k, (x, y, yaw) in enumerate(((48.0, -22.0, 0.1), (95.0, 8.0, 2.6))):
        make_chamfer_box(f"Speedboat_Hull_{k}", (x, y, WL + 0.26), (4.6, 1.8, 0.56), ((0.86, 0.20, 0.18, 1.0), (0.94, 0.94, 0.92, 1.0))[k],
                         chamfer=0.20, yaw=yaw)
        for j in range(4):
            d = 3.4 + j * 3.2
            make_rot_box(f"Speedboat_Wake_{k}_{j}", (x - d * math.cos(yaw), y - d * math.sin(yaw), WL + 0.03),
                         (3.0, 1.0 + j * 0.9, 0.02), (0.86, 0.88, 0.86, 1.0), yaw=yaw)
    for k in range(7):                      # the long white seams of light
        make_rot_box(f"Water_Seam_Light_{k}" + OUT, (36.0 + k * 16.0, -10.0 + (k % 3) * 9.0, WL + 0.025), (12.0, 0.30, 0.01),
                     (0.94, 0.96, 0.94, 1.0), yaw=0.15 * (k % 2))
    for k in range(5):                      # the sun's road on the water at dawn
        make_box(f"Water_Sun_Road_{k}" + DAWN, (50.0 + k * 26.0, -8.0 - k * 3.6, WL + 0.025), (24.0, 1.0 + k * 0.8, 0.01), (1.0, 0.78, 0.50, 1.0))
    # the far shore: trees in a band, the balloons lifting off it
    make_box("Far_Shore_Band", (SHORE + 158.0, 0.0, 2.0), (4.0, 340.0, 6.0), (0.20, 0.28, 0.20, 1.0))
    for k, (y, z, col) in enumerate(((-120.0, 40.0, (0.90, 0.30, 0.20, 1.0)), (-60.0, 70.0, (0.96, 0.80, 0.24, 1.0)),
                                     (20.0, 30.0, (0.30, 0.50, 0.86, 1.0)), (90.0, 55.0, (0.80, 0.30, 0.60, 1.0)))):
        make_blob(f"Far_Balloon_{k}" + OUT, (SHORE + 140.0, y * 0.3, z * 0.3), 3.6, col, noise=0.0, seed=k, squash=1.15)
        make_box(f"Far_Balloon_{k}_Basket" + OUT, (SHORE + 140.0, y * 0.3, z * 0.3 - 5.0), (0.9, 0.9, 0.8), (0.50, 0.38, 0.24, 1.0))
    # (draft 2: the four sky PLANES per hour are gone — 200 m walls whose ends
    # showed as a grey slab behind the house; the presets' env carries the
    # sky now. The dawn sun's disc stays.)
    make_blob("Sky_Sun_Disc_Glow" + DAWN, (SHORE + 164.0, -26.0, 6.5), 5.0, (1.0, 0.86, 0.60, 1.0), noise=0.0, seed=9, squash=1.0)


def main():
    clear_scene()
    build_shell()
    build_chris_room()
    build_bath()
    build_kitchen()
    build_grounds()
    build_lake()
    try:
        join_stock()
    except Exception as _e:
        print("[join_stock] skipped:", _e)
    out = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                        "../../../assets/3d/locales/lake_house.glb"))
    print(f"\n[build_lake_house] exporting to {out}")
    export_glb(out)


if __name__ == "__main__":
    main()
