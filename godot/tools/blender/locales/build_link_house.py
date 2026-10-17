"""link_house — vol 3's family house in Texas (draft 1, 2026-10-17).

The user: "go ahead and start working on backgrounds for vol 1-4 as needed."
Vol 3's home scenes (the bg_places group once called andy_family_house) play
in one single-storey brick ranch: nine scene uses across the kitchen at
evening, the living room at night, the bathroom by day and before dawn, and
Andy's room by day, by night and by the bedside lamp. Two of the group's old
stems were somebody else's place: the blanket fort is the Chau house
(chau_house) and the Dallas closet is June's (they stay stand-ins).

What the scenes say, and where it is here:
  "Tony is looking at me, across from the table. The magazine sits between
   us."                                  → the dining table, two chairs
                                           facing, Magazine on the table
  "Nick was asleep on the couch when she came to me, the television showing
   a scary movie marathon."              → Sofa facing the TV on Wall_W,
                                           a blanket and a pillow on it;
                                           the TV's glow is the night key
  "My dad puts his ear to the bathroom door."  → the bathroom door on the
                                           hall, half open; tub, toilet,
                                           vanity under one light bar
  "I'm in the bathroom. It's the middle of the night or early in the
   morning."                             → the same room, the vanity light
                                           only (the night preset)
  "I rummage through my bedroom for a book" → Andy's room: the bookcase on
                                           its W wall, the bed, the bedside
                                           lamp, the desk under the N window

Plan (Blender: x east, y north, z up; Godot (x, z, -y)), 13 x 10.5 m,
ceiling 2.6:
  y 0.0..5.5   living room (x -6.5..-0.3) open to the kitchen and dining
               (x -0.3..6.5); front windows and the front door on Wall_S
  y 5.5..6.7   the hall, end to end
  y 6.7..10.5  the second bedroom (x -6.5..-1.2, door shut), the bathroom
               (x -1.2..1.6), Andy's room (x 1.6..6.5)

DRAFT 2 targets: the second bedroom's interior (its door is shut in every
view); the lake house's bathroom for vol3_family_bathroom_night if the
text means a different room ("The lake house · before dawn"); wear and
clutter (school photos down the hall, the fridge door, a laundry basket);
the backyard beyond the N windows as more than make_view's lawn; per-preset
props (the magazine only in the Uncle Nick scenes); Deck-verified framing.
"""
import os, sys
_BT = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
if _BT not in sys.path: sys.path.insert(0, _BT)
from _props.geometry import clear_scene, make_box, make_cyl, make_chamfer_box, make_lathe, make_tube, export_glb
from _props.views import make_view
from _props.structure import make_floor, make_wall, make_ceiling, make_window, make_wall_with_openings
from _props.furniture import make_bed, make_chair, make_table, make_lamp, make_pendant
from _props.decor import make_faded_poster
from _props.safety import make_smoke_detector
from _props.detail import (make_traffic_wear, make_threshold, make_wall_outlet, make_light_switch,
                           make_thermostat, make_wall_tint_band)
from _props import kitchen_kit as K

X0, X1 = -6.5, 6.5
Y0, Y1 = 0.0, 10.5
HALL_S, HALL_N = 5.5, 6.7          # the hall's two walls (centre lines)
BATH_W, BATH_E = -1.2, 1.6         # the bathroom's side walls
CEIL = 2.6
T = 0.20                           # wall thickness

PAL_WALL = {"wall": (0.86, 0.80, 0.68, 1.0), "baseboard": (0.92, 0.90, 0.84, 1.0)}   # builder beige, white trim
PAL_BATH = {"wall": (0.80, 0.84, 0.80, 1.0), "baseboard": (0.92, 0.90, 0.84, 1.0)}   # a sage bathroom
CARPET = (0.62, 0.56, 0.46, 1.0); CARPET_SEAM = (0.56, 0.50, 0.41, 1.0)
VINYL = (0.80, 0.76, 0.66, 1.0); VINYL_SEAM = (0.70, 0.66, 0.57, 1.0)
TILE = (0.88, 0.87, 0.82, 1.0); TILE_SEAM = (0.70, 0.69, 0.65, 1.0)
OAK = (0.62, 0.46, 0.28, 1.0); OAK_DARK = (0.42, 0.30, 0.18, 1.0)
DOOR_WHITE = (0.93, 0.92, 0.88, 1.0)
SOFA = (0.46, 0.36, 0.28, 1.0); SOFA_CUSH = (0.52, 0.41, 0.32, 1.0)
ENAMEL = (0.95, 0.95, 0.93, 1.0); CHROME = (0.78, 0.79, 0.80, 1.0)
BLACK = (0.08, 0.08, 0.09, 1.0)
DOOR_H = 2.05


def wall_x(name, y, x0, x1, openings=(), face=+1, pal=PAL_WALL):
    """A wall along X from x0 to x1 at y; openings as (x_centre, z_centre, w, h)."""
    ln, cx = x1 - x0, (x0 + x1) / 2.0
    if openings:
        make_wall_with_openings(name, (cx, y, 0), length=ln, height=CEIL, thickness=T, axis='X',
                                palette=pal, baseboard_face_sign=face, openings=list(openings))
    else:
        make_wall(name, (cx, y, 0), length=ln, height=CEIL, thickness=T, axis='X', palette=pal,
                  baseboard_face_sign=face)


def wall_y(name, x, y0, y1, openings=(), face=+1, pal=PAL_WALL):
    ln, cy = y1 - y0, (y0 + y1) / 2.0
    if openings:
        make_wall_with_openings(name, (x, cy, 0), length=ln, height=CEIL, thickness=T, axis='Y',
                                palette=pal, baseboard_face_sign=face, openings=list(openings))
    else:
        make_wall(name, (x, cy, 0), length=ln, height=CEIL, thickness=T, axis='Y', palette=pal,
                  baseboard_face_sign=face)


def door_casing(name, x, y, w, axis='X'):
    """A white casing round a door opening in a wall at (x, y), both faces."""
    h = DOOR_H
    for side in (-1, 1):
        off = side * (T / 2.0 + 0.008)
        if axis == 'X':
            make_box(f"{name}_Head_{side:+d}", (x, y + off, h + 0.04), (w + 0.14, 0.016, 0.08), DOOR_WHITE)
            for s in (-1, 1):
                make_box(f"{name}_Leg_{side:+d}_{s:+d}", (x + s * (w / 2.0 + 0.035), y + off, h / 2.0), (0.07, 0.016, h), DOOR_WHITE)
        else:
            make_box(f"{name}_Head_{side:+d}", (x + off, y, h + 0.04), (0.016, w + 0.14, 0.08), DOOR_WHITE)
            for s in (-1, 1):
                make_box(f"{name}_Leg_{side:+d}_{s:+d}", (x + off, y + s * (w / 2.0 + 0.035), h / 2.0), (0.016, 0.07, h), DOOR_WHITE)


def build_shell():
    # floors: carpet in the living room, hall and bedrooms; vinyl in the kitchen; tile in the bath
    make_floor("Floor_Living", (-3.40, 2.75, 0.0), size_x=6.2, size_y=5.5, palette={"vinyl": CARPET, "seam": CARPET_SEAM})
    make_floor("Floor_Kitchen", (3.10, 2.75, 0.0), size_x=6.8, size_y=5.5, palette={"vinyl": VINYL, "seam": VINYL_SEAM})
    make_floor("Floor_Hall", (0.0, 6.10, 0.0), size_x=13.4, size_y=1.2, palette={"vinyl": CARPET, "seam": CARPET_SEAM})
    make_floor("Floor_Bed2", (-3.85, 8.60, 0.0), size_x=5.3, size_y=3.8, palette={"vinyl": CARPET, "seam": CARPET_SEAM})
    make_floor("Floor_Bath", (0.20, 8.60, 0.0), size_x=2.8, size_y=3.8, palette={"vinyl": TILE, "seam": TILE_SEAM})
    make_floor("Floor_Bedroom", (4.05, 8.60, 0.0), size_x=4.9, size_y=3.8, palette={"vinyl": CARPET, "seam": CARPET_SEAM})
    make_ceiling("Ceil", (0.0, (Y0 + Y1) / 2.0, CEIL), size_x=X1 - X0 + 0.4, size_y=Y1 - Y0 + 0.4,
                 with_grid=False, with_stains=False, palette={"tile": (0.94, 0.93, 0.89, 1.0)})

    # exterior: Wall_S has the living window, the front door, the kitchen window
    wall_x("Wall_S", Y0, X0 - 0.1, X1 + 0.1, face=+1, openings=[(-4.2, 1.45, 2.0, 1.40), (-1.0, DOOR_H / 2.0, 0.95, DOOR_H),
                                                                 (4.2, 1.50, 1.60, 1.20)])
    wall_x("Wall_N", Y1, X0 - 0.1, X1 + 0.1, face=-1, openings=[(-4.0, 1.45, 1.40, 1.30), (-0.30, 1.85, 0.70, 0.55),
                                                                 (4.0, 1.45, 1.40, 1.30)])
    wall_y("Wall_W", X0, Y0, Y1, face=+1)
    wall_y("Wall_E", X1, Y0, Y1, face=-1, openings=[(2.2, 1.45, 1.60, 1.30)])
    # the hall: the living room's wide cased opening and the kitchen's door on its S wall;
    # three doors on its N wall
    wall_x("Wall_Hall_S", HALL_S, X0, X1, face=-1, openings=[(-3.0, 1.05, 1.60, 2.10), (0.50, DOOR_H / 2.0, 0.95, DOOR_H)])
    wall_x("Wall_Hall_N", HALL_N, X0, X1, face=-1, openings=[(-4.0, DOOR_H / 2.0, 0.86, DOOR_H),
                                                                    (0.20, DOOR_H / 2.0, 0.81, DOOR_H),
                                                                    (3.20, DOOR_H / 2.0, 0.86, DOOR_H)])
    # interior walls run into the walls they meet (centre line to centre line), so every joint is a joint
    wall_y("Wall_Bath_W", BATH_W, HALL_N, Y1, face=+1, pal=PAL_BATH)
    wall_y("Wall_Bath_E", BATH_E, HALL_N, Y1, face=-1, pal=PAL_BATH)
    for nm, x, y, w, ax in (("Case_Front", -1.0, Y0, 0.95, 'X'), ("Case_Living", -3.0, HALL_S, 1.60, 'X'),
                            ("Case_Kitchen", 0.50, HALL_S, 0.95, 'X'), ("Case_Bed2", -4.0, HALL_N, 0.86, 'X'),
                            ("Case_Bath", 0.20, HALL_N, 0.81, 'X'), ("Case_Bedroom", 3.20, HALL_N, 0.86, 'X')):
        door_casing(nm, x, y, w, ax)

    # windows: front windows see the street, back windows the yard; the bath's is frosted
    make_window("Win_Living", (-4.2, Y0 + 0.10, 1.45), width=2.0, height=1.40, see_through=True, room_dir=+1)
    make_window("Win_Kitchen", (4.2, Y0 + 0.10, 1.50), width=1.60, height=1.20, see_through=True, room_dir=+1)
    make_window("Win_Bed2", (-4.0, Y1 - 0.10, 1.45), width=1.40, height=1.30, see_through=True)
    make_window("Win_Bedroom", (4.0, Y1 - 0.10, 1.45), width=1.40, height=1.30, see_through=True)
    make_window("Win_Dining", (X1 - 0.10, 2.2, 1.45), width=1.60, height=1.30, axis='Y', see_through=True)
    make_window("Win_Bath", (-0.30, Y1 - 0.10, 1.85), width=0.70, height=0.55, cross_mullion=False,
                palette={"glass": (0.86, 0.90, 0.90, 0.85), "warm": (0.92, 0.92, 0.88, 0.9)})
    # blinds half down in the front and bedroom windows (a Texas house keeps the sun out)
    for nm, x, y, w, z_top, drop, sgn in (("Blind_Living", -4.2, Y0 + 0.17, 2.0, 2.15, 0.55, +1),
                                          ("Blind_Kitchen", 4.2, Y0 + 0.17, 1.6, 2.10, 0.35, +1),
                                          ("Blind_Bedroom", 4.0, Y1 - 0.17, 1.4, 2.10, 0.50, -1)):
        make_box(f"{nm}_Rail", (x, y, z_top), (w + 0.06, 0.05, 0.05), DOOR_WHITE)
        for k in range(int(drop / 0.05)):
            make_box(f"{nm}_Slat_{k}", (x, y, z_top - 0.05 - k * 0.05), (w, 0.03, 0.006), (0.94, 0.93, 0.89, 1.0))

    # doors: the front door shut, the bathroom's half open (into the room, hinge on its E jamb),
    # Andy's open against its W wall, the second bedroom's shut
    make_box("Door_Front", (-1.0, Y0 + 0.03, DOOR_H / 2.0), (0.92, 0.045, DOOR_H - 0.02), (0.36, 0.20, 0.14, 1.0))
    make_cyl("Door_Front_Knob", (-0.66, Y0 + 0.0825, 0.98), 0.03, 0.06, (0.70, 0.58, 0.30, 1.0), axis='Y', segments=10)
    make_box("Door_Bed2", (-4.0, HALL_N + 0.02, DOOR_H / 2.0), (0.84, 0.04, DOOR_H - 0.02), DOOR_WHITE)
    make_cyl("Door_Bed2_Knob", (-3.68, HALL_N - 0.025, 0.98), 0.028, 0.05, CHROME, axis='Y', segments=10)
    # the bath door swung 95 degrees into the bathroom on its E-jamb hinge,
    # flat to the room's east side, so the doorway (and the camera in it)
    # sees the toilet, the tub and the vanity
    import math
    a = math.radians(95.0)
    hx, hy, dw = 0.20 + 0.405, HALL_N + 0.12, 0.79
    dx, dy = -math.cos(a), math.sin(a)
    from _props.geometry import make_rot_box
    make_rot_box("Door_Bath", (hx + dx * dw / 2.0, hy + dy * dw / 2.0, DOOR_H / 2.0),
                 (dw, 0.04, DOOR_H - 0.02), DOOR_WHITE, yaw=math.atan2(dy, dx))
    make_box("Door_Bedroom", (2.80, HALL_N + 0.10 + 0.43, DOOR_H / 2.0), (0.04, 0.84, DOOR_H - 0.02), DOOR_WHITE)


def build_living():
    """The living room: the TV on Wall_W, the sofa facing it, Nick's blanket."""
    # the TV stand and a 2000s 32-inch CRT on it, its screen toward the room (+x)
    make_box("TV_Stand", (X0 + 0.34, 2.80, 0.27), (0.48, 1.50, 0.54), OAK_DARK)
    for k, y in enumerate((2.38, 3.22)):
        make_box(f"TV_Stand_Door_{k}", (X0 + 0.585, y, 0.27), (0.012, 0.62, 0.44), OAK)
    make_box("TV_Body", (X0 + 0.40, 2.80, 0.86), (0.56, 0.80, 0.64), (0.14, 0.14, 0.15, 1.0))
    make_box("TV_Bezel", (X0 + 0.685, 2.80, 0.88), (0.02, 0.78, 0.58), (0.10, 0.10, 0.11, 1.0))
    make_box("TV_Screen", (X0 + 0.697, 2.80, 0.90), (0.006, 0.64, 0.48), (0.30, 0.42, 0.58, 1.0))
    make_box("VCR", (X0 + 0.36, 2.18, 0.58), (0.30, 0.24, 0.08), (0.12, 0.12, 0.13, 1.0))       # on the stand beside the set
    for k in range(6):
        make_box(f"Tapes_{k}", (X0 + 0.34, 3.30 + k * 0.03, 0.59), (0.19, 0.025, 0.10), (0.16 + k * 0.05, 0.12, 0.12, 1.0))
    # the sofa, facing west to the TV (its back to the kitchen)
    sx, sy, sl = -3.30, 2.80, 2.20
    make_box("Sofa_Base", (sx, sy, 0.17), (0.92, sl, 0.34), SOFA)         # down to the carpet
    make_box("Sofa_Back", (sx + 0.37, sy, 0.62), (0.20, sl, 0.60), SOFA)
    for s in (-1, 1):
        make_box(f"Sofa_Arm_{s:+d}", (sx, sy + s * (sl / 2.0 - 0.10), 0.44), (0.90, 0.20, 0.42), SOFA)
    for k, cy in enumerate((sy - 0.62, sy, sy + 0.62)):
        make_box(f"Sofa_SeatCush_{k}", (sx - 0.06, cy, 0.41), (0.66, 0.60, 0.14), SOFA_CUSH)
        make_box(f"Sofa_BackCush_{k}", (sx + 0.20, cy, 0.66), (0.20, 0.58, 0.40), SOFA_CUSH)
    # Nick asleep here: a pillow at the south arm and a crocheted afghan half off
    make_chamfer_box("Sofa_Pillow", (sx - 0.08, sy - 0.80, 0.53), (0.42, 0.32, 0.12), (0.92, 0.90, 0.84, 1.0), chamfer=0.04)
    make_box("Sofa_Afghan", (sx - 0.12, sy + 0.10, 0.495), (0.70, 1.40, 0.03), (0.66, 0.30, 0.22, 1.0))
    make_box("Sofa_Afghan_Hang", (sx - 0.465, sy + 0.10, 0.295), (0.03, 1.20, 0.40), (0.66, 0.30, 0.22, 1.0))
    # the coffee table, a rug, the recliner, an end table with the lamp
    make_box("Rug_Living", (-4.70, 2.80, 0.006), (2.40, 2.00, 0.012), (0.48, 0.36, 0.30, 1.0))
    make_table("CoffeeTable", -4.70, 2.80, w=0.60, d=1.10, h=0.42, wood=OAK)
    make_box("CoffeeTable_Remote", (-4.62, 2.60, 0.435), (0.05, 0.18, 0.02), BLACK)
    make_cyl("CoffeeTable_Mug", (-4.80, 3.05, 0.47), 0.04, 0.09, (0.82, 0.78, 0.70, 1.0), segments=10)
    rx, ry = -5.20, 4.75
    make_box("Recliner_Base", (rx, ry, 0.24), (0.80, 0.80, 0.28), (0.36, 0.30, 0.26, 1.0))
    make_box("Recliner_Back", (rx, ry + 0.33, 0.70), (0.80, 0.22, 0.70), (0.36, 0.30, 0.26, 1.0))
    for s in (-1, 1):
        make_box(f"Recliner_Arm_{s:+d}", (rx + s * 0.36, ry, 0.48), (0.16, 0.80, 0.30), (0.36, 0.30, 0.26, 1.0))
    make_box("Recliner_Cush", (rx, ry - 0.05, 0.42), (0.52, 0.62, 0.10), (0.40, 0.34, 0.30, 1.0))
    make_box("EndTable", (-3.30, 4.25, 0.29), (0.50, 0.50, 0.58), OAK)
    make_lamp("Lamp_Living", -3.30, 4.25, base_z=0.58, h=0.62)
    # a bookcase against the hall wall, family photos on top
    bx = -5.70
    make_box("Bookcase_Back", (bx, HALL_S - 0.115, 0.95), (1.00, 0.02, 1.90), OAK_DARK)
    for s in (-1, 1):
        make_box(f"Bookcase_Side_{s:+d}", (bx + s * 0.49, HALL_S - 0.26, 0.95), (0.02, 0.28, 1.90), OAK)
    for b in range(5):
        z = 0.05 + b * 0.45
        make_box(f"Bookcase_Board_{b}", (bx, HALL_S - 0.26, z), (0.96, 0.28, 0.02), OAK)
        if b < 4:
            for i in range(10 - b):
                h = 0.20 + ((i * 5 + b) % 4) * 0.03
                make_box(f"Bookcase_Book_{b}_{i}", (bx - 0.42 + i * 0.085, HALL_S - 0.28, z + 0.01 + h / 2.0),
                         (0.06, 0.20, h), ((0.30 + 0.07 * (i % 4)), 0.22 + 0.05 * (b % 3), 0.18, 1.0))
    for k in range(3):
        make_box(f"Bookcase_Frame_{k}", (bx - 0.30 + k * 0.30, HALL_S - 0.30, 1.97), (0.18, 0.02, 0.22), (0.20, 0.16, 0.12, 1.0))
    make_box("Bookcase_Top", (bx, HALL_S - 0.26, 1.905), (1.00, 0.30, 0.02), OAK)
    # the ceiling fan over the sofa
    make_cyl("Fan_Rod", (-3.90, 2.80, CEIL - 0.15), 0.015, 0.30, (0.60, 0.50, 0.30, 1.0), segments=6)
    make_cyl("Fan_Hub", (-3.90, 2.80, CEIL - 0.34), 0.11, 0.12, (0.60, 0.50, 0.30, 1.0), segments=12)
    import math
    from _props.geometry import make_rot_box
    for k in range(5):
        a = k * 2 * math.pi / 5
        make_rot_box(f"Fan_Blade_{k}", (-3.90 + math.cos(a) * 0.42, 2.80 + math.sin(a) * 0.42, CEIL - 0.36),
                     (0.62, 0.14, 0.012), OAK_DARK, yaw=a)
    make_lathe("Fan_Globe", (-3.90, 2.80, CEIL - 0.52), [(0.0, 0.0), (0.09, 0.03), (0.10, 0.08), (0.0, 0.12)],
               (0.96, 0.92, 0.80, 1.0), segments=10)


def build_kitchen():
    """The kitchen along the hall wall; the dining table under the E window."""
    yb = HALL_S - T / 2.0          # the kitchen run's back: the hall wall's south face
    K.base_run("Kit_Base", 1.30, 5.20, yb, gaps=[(2.95, 3.71), (4.35, 4.95)])
    K.range_("Kit_Range", 3.33, yb, 0.98)
    K.dishwasher("Kit_DW", 4.65, yb - 0.62, 0.98)
    make_box("Kit_DW_Toe", (4.65, yb - 0.60, 0.05), (0.58, 0.06, 0.10), (0.20, 0.20, 0.21, 1.0))   # the kick under the panel
    K.sink("Kit_Sink", 2.10, yb, 0.98)
    K.upper_run("Kit_Upper", 1.30, 5.20, yb)
    K.backsplash("Kit_Splash", 1.30, 5.20, yb, 0.98, 1.46)
    K.fridge("Kit_Fridge", 5.75, yb)
    # what sits on the counter: a toaster, a coffee maker, the mail
    make_box("Kit_Toaster", (1.55, yb - 0.28, 1.08), (0.28, 0.18, 0.20), CHROME)
    make_box("Kit_Coffee", (4.95, yb - 0.24, 1.15), (0.22, 0.26, 0.34), BLACK)
    make_box("Kit_Mail", (2.60, yb - 0.40, 0.99), (0.26, 0.20, 0.02), (0.92, 0.90, 0.84, 1.0))
    # the dining table: father and son across it, the magazine between them
    tx, ty = 4.10, 2.20
    make_table("Dining", tx, ty, w=1.50, d=0.90, h=0.75, wood=OAK)
    make_chair("Chair_S", tx, ty - 0.70, yaw=0.0, wood=OAK)            # faces north, to the table
    make_chair("Chair_N", tx, ty + 0.70, yaw=3.14159, wood=OAK)        # faces south
    make_chair("Chair_W", tx - 1.02, ty, yaw=-1.5708, wood=OAK)        # faces east
    make_box("Magazine", (tx + 0.05, ty - 0.02, 0.757), (0.21, 0.28, 0.006), (0.86, 0.30, 0.24, 1.0))
    make_box("Magazine_Cover", (tx + 0.05, ty - 0.02, 0.761), (0.17, 0.12, 0.002), (0.94, 0.86, 0.60, 1.0))
    make_cyl("Dining_Glass", (tx - 0.40, ty - 0.25, 0.81), 0.035, 0.11, (0.70, 0.78, 0.80, 0.5), segments=10)
    make_pendant("Pendant_Dining", tx, ty, CEIL - 0.85, CEIL, shade_col=(0.56, 0.44, 0.30, 1.0))
    # a ceiling fixture over the kitchen
    make_cyl("Kit_Ceiling_Light", (3.40, 3.80, CEIL - 0.05), 0.24, 0.08, (0.96, 0.94, 0.86, 1.0), segments=14)


def _tub(x0, x1, y0, y1):
    """A built-in tub between the walls: the apron, the rim, the basin."""
    cx, cy, w, d = (x0 + x1) / 2.0, (y0 + y1) / 2.0, x1 - x0, y1 - y0
    make_box("Tub_Apron", (cx, y0 + 0.04, 0.24), (w, 0.08, 0.48), ENAMEL)
    make_box("Tub_Rim_S", (cx, y0 + 0.06, 0.49), (w, 0.12, 0.03), ENAMEL)
    make_box("Tub_Rim_N", (cx, y1 - 0.05, 0.49), (w, 0.10, 0.03), ENAMEL)
    for s, xx in ((-1, x0 + 0.05), (1, x1 - 0.05)):
        make_box(f"Tub_Rim_{s:+d}", (xx, cy, 0.49), (0.10, d, 0.03), ENAMEL)
    make_box("Tub_Basin", (cx, cy + 0.02, 0.075), (w - 0.20, d - 0.22, 0.15), (0.90, 0.90, 0.88, 1.0))
    make_box("Tub_Wall_Tile", (cx, y1 - 0.004, 1.20), (w, 0.008, 1.40), (0.90, 0.92, 0.90, 1.0))
    make_cyl("Tub_Spout", (x1 - 0.12, y1 - 0.08, 0.62), 0.022, 0.14, CHROME, axis='Y', segments=8)
    make_cyl("Tub_Shower_Arm", (x1 - 0.30, y1 - 0.08, 1.95), 0.012, 0.16, CHROME, axis='Y', segments=6)
    make_cyl("Tub_Shower_Head", (x1 - 0.30, y1 - 0.18, 1.92), 0.045, 0.05, CHROME, axis='Y', segments=10)
    # the curtain rod over the apron, the curtain half drawn toward the W wall
    make_cyl("Tub_Rod", (cx, y0 + 0.06, 2.05), 0.012, w, CHROME, axis='X', segments=6)
    for k in range(6):
        make_box(f"Tub_Curtain_{k}", (x0 + 0.10 + k * 0.10, y0 + 0.06 + (0.03 if k % 2 else 0.0), 1.42),
                 (0.10, 0.02, 1.24), (0.74, 0.84, 0.86, 1.0))


def build_bath():
    """Tub on Wall_N under the frosted window, the toilet on the W wall, the
    vanity and its light bar on the E wall."""
    xi0, xi1 = BATH_W + T / 2.0, BATH_E - T / 2.0
    yn = Y1 - T / 2.0
    _tub(xi0, xi0 + 1.52, yn - 0.76, yn)
    # the tile wainscot round the other walls
    for nm, x, a in (("Wainscot_W", xi0 + 0.004, 'Y'), ("Wainscot_E", xi1 - 0.004, 'Y')):
        make_box(nm, (x, (HALL_N + yn) / 2.0 - 0.40, 0.60), (0.008, yn - HALL_N - 0.90, 1.20), (0.90, 0.92, 0.90, 1.0))
    # toilet: tank against the W wall, facing east
    ty = 8.30
    make_box("Toilet_Tank", (xi0 + 0.11, ty, 0.62), (0.20, 0.44, 0.38), ENAMEL)
    make_box("Toilet_Tank_Lid", (xi0 + 0.115, ty, 0.825), (0.22, 0.46, 0.03), ENAMEL)
    make_box("Toilet_Flush", (xi0 + 0.22, ty + 0.15, 0.74), (0.01, 0.06, 0.02), CHROME)
    make_lathe("Toilet_Bowl", (xi0 + 0.48, ty, 0.0), [(0.13, 0.0), (0.10, 0.08), (0.12, 0.25), (0.19, 0.40), (0.0, 0.40)], ENAMEL, segments=12)
    make_box("Toilet_Seat", (xi0 + 0.48, ty, 0.415), (0.42, 0.38, 0.03), (0.90, 0.89, 0.86, 1.0))
    make_box("Toilet_Paper", (xi0 + 0.03, ty - 0.42, 0.68), (0.06, 0.12, 0.12), (0.96, 0.96, 0.94, 1.0))
    # vanity on the E wall: cabinet, top, basin, faucet; the mirror and the light bar over it
    vy = 8.35
    make_box("Vanity_Cab", (xi1 - 0.28, vy, 0.40), (0.55, 1.00, 0.80), OAK)
    for k, dy in enumerate((-0.25, 0.25)):
        make_box(f"Vanity_Door_{k}", (xi1 - 0.556, vy + dy, 0.40), (0.012, 0.46, 0.66), (0.66, 0.50, 0.32, 1.0))
    make_box("Vanity_Top", (xi1 - 0.29, vy, 0.82), (0.58, 1.04, 0.04), (0.92, 0.90, 0.86, 1.0))
    make_box("Vanity_Basin", (xi1 - 0.30, vy, 0.835), (0.36, 0.44, 0.012), (0.82, 0.82, 0.80, 1.0))
    make_cyl("Vanity_Faucet", (xi1 - 0.08, vy, 0.90), 0.02, 0.14, CHROME, segments=8)
    make_box("Vanity_Mirror", (xi1 - 0.008, vy, 1.45), (0.012, 0.96, 0.82), (0.78, 0.84, 0.86, 1.0))
    make_box("Vanity_LightBar", (xi1 - 0.05, vy, 1.98), (0.08, 0.80, 0.08), CHROME)
    for k in range(4):
        make_lathe(f"Vanity_Bulb_{k}", (xi1 - 0.11, vy - 0.30 + k * 0.20, 1.93), [(0.0, 0.0), (0.04, 0.02), (0.045, 0.06), (0.0, 0.10)],
                   (0.98, 0.96, 0.86, 1.0), segments=8)
    make_box("Towel_Bar", (xi1 - 0.015, 9.30, 1.15), (0.03, 0.60, 0.02), CHROME)
    make_box("Towel", (xi1 - 0.035, 9.30, 0.92), (0.03, 0.50, 0.46), (0.42, 0.56, 0.62, 1.0))
    make_box("Bath_Mat", (0.10, 9.20, 0.006), (0.50, 0.80, 0.012), (0.46, 0.58, 0.62, 1.0))
    make_cyl("Bath_Ceiling_Fan", (0.20, 8.00, CEIL - 0.03), 0.16, 0.05, (0.94, 0.94, 0.92, 1.0), segments=10)


def build_bedroom():
    """Andy's room: the bed's head on Wall_E, the lamp, the desk under the N
    window, the bookcase on the W wall, the closet on the S wall."""
    xi0, xi1 = BATH_E + T / 2.0, X1 - T / 2.0
    yi0, yi1 = HALL_N + T / 2.0, Y1 - T / 2.0
    make_bed("Bed", xi1 - 0.975 - 0.02, 8.30, head="+X", w=1.35, d=1.95, blanket_col=(0.30, 0.36, 0.46, 1.0))
    make_box("Nightstand", (xi1 - 0.24, 9.45, 0.30), (0.44, 0.44, 0.60), OAK)
    make_lamp("Lamp_Bed", xi1 - 0.24, 9.45, base_z=0.60, h=0.52)
    make_box("Nightstand_Book", (xi1 - 0.20, 9.30, 0.615), (0.16, 0.22, 0.03), (0.42, 0.20, 0.16, 1.0))
    make_box("Nightstand_Clock", (xi1 - 0.30, 9.60, 0.645), (0.10, 0.18, 0.09), BLACK)
    make_box("Nightstand_Clock_Face", (xi1 - 0.356, 9.60, 0.65), (0.004, 0.13, 0.04), (0.86, 0.20, 0.14, 1.0))
    # the desk under the window and its lamp
    dx = 4.00
    make_box("Desk_Top", (dx, yi1 - 0.305, 0.74), (1.30, 0.62, 0.03), OAK_DARK)   # back edge against the wall
    for s in (-1, 1):
        make_box(f"Desk_Side_{s:+d}", (dx + s * 0.63, yi1 - 0.32, 0.365), (0.03, 0.60, 0.73), OAK_DARK)
    make_chair("Desk_Chair", dx, yi1 - 0.95, yaw=0.0, wood=OAK_DARK)
    make_lamp("Lamp_Desk", dx + 0.48, yi1 - 0.22, base_z=0.755, h=0.42, shade_col=(0.30, 0.42, 0.34, 1.0))
    make_box("Desk_Papers", (dx - 0.20, yi1 - 0.36, 0.76), (0.30, 0.22, 0.01), (0.96, 0.95, 0.92, 1.0))
    # the bookcase on the W wall, books packed and a few lying flat
    bx = xi0 + 0.15
    for s in range(2):
        by = 8.32 + s * 0.92          # clear of the door's swing (doorway_audit: 0.9 m each side of the leaf)
        make_box(f"Shelf_{s}_Back", (xi0 + 0.01, by, 0.95), (0.02, 0.88, 1.90), OAK_DARK)
        for side in (-1, 1):
            make_box(f"Shelf_{s}_Side_{side:+d}", (bx, by + side * 0.43, 0.95), (0.28, 0.02, 1.90), OAK)
        for b in range(5):
            z = 0.05 + b * 0.45
            make_box(f"Shelf_{s}_Board_{b}", (bx, by, z), (0.28, 0.84, 0.02), OAK)
            if b < 4:
                n = 8 - (b + s) % 3
                for i in range(n):
                    h = 0.19 + ((i * 3 + b + s) % 4) * 0.03
                    make_box(f"Shelf_{s}_Book_{b}_{i}", (bx + 0.02, by - 0.36 + i * 0.09, z + 0.01 + h / 2.0),
                             (0.20, 0.065, h), (0.26 + 0.08 * ((i + s) % 4), 0.20 + 0.06 * (b % 3), 0.20 + 0.05 * (i % 2), 1.0))
        make_box(f"Shelf_{s}_Top", (bx, by, 1.905), (0.28, 0.88, 0.02), OAK)
    make_box("Shelf_Flat_Books", (bx + 0.02, 8.77, 1.94), (0.22, 0.30, 0.06), (0.52, 0.30, 0.20, 1.0))
    # the closet on the S wall: two bifold pairs
    cx = 5.20
    for k in range(4):
        make_box(f"Closet_Leaf_{k}", (cx - 0.66 + k * 0.44, yi0 + 0.025, 1.02), (0.42, 0.03, 2.02), DOOR_WHITE)
    make_box("Closet_Head", (cx, yi0 + 0.03, 2.08), (1.82, 0.04, 0.06), DOOR_WHITE)
    # a dresser in the NW corner (clear of the door's swing), posters over the bed
    make_box("Dresser", (2.45, yi1 - 0.25, 0.45), (0.90, 0.48, 0.90), OAK)
    for k in range(3):
        make_box(f"Dresser_Drawer_{k}", (2.45, yi1 - 0.496, 0.18 + k * 0.27), (0.84, 0.012, 0.22), (0.68, 0.52, 0.32, 1.0))
    make_box("Dresser_Box", (2.25, yi1 - 0.25, 0.95), (0.30, 0.22, 0.10), (0.24, 0.20, 0.18, 1.0))
    make_faded_poster("Poster_Bed", (xi1 - 0.006, 8.30, 1.65), into_room=-1)
    make_box("Rug_Bedroom", (3.90, 8.40, 0.006), (1.60, 1.10, 0.012), (0.30, 0.34, 0.40, 1.0))
    make_cyl("Bedroom_Ceiling_Light", (4.05, 8.60, CEIL - 0.05), 0.20, 0.08, (0.96, 0.94, 0.86, 1.0), segments=12)


def build_bed2():
    """The second bedroom behind its shut door: enough that the window
    from the yard is not a void (its interior is draft 2)."""
    make_bed("Bed2", -3.90, 9.20, head="+Y", w=1.50, d=2.00, blanket_col=(0.56, 0.48, 0.40, 1.0))
    make_box("Bed2_Dresser", (-6.10, 8.00, 0.45), (0.48, 1.10, 0.90), OAK)


def build_hall_and_infra():
    make_box("Hall_Runner", (0.0, 6.10, 0.006), (9.00, 0.80, 0.012), (0.40, 0.30, 0.26, 1.0))
    for k, x in enumerate((-2.2, -1.4, 1.4, 2.3)):
        make_box(f"Hall_Photo_{k}", (x, HALL_N - T / 2.0 - 0.012, 1.55 + (k % 2) * 0.12), (0.30, 0.02, 0.38), (0.24, 0.18, 0.14, 1.0))
        make_box(f"Hall_Photo_{k}_Print", (x, HALL_N - T / 2.0 - 0.024, 1.55 + (k % 2) * 0.12), (0.24, 0.004, 0.30),
                 ((0.70, 0.62, 0.50, 1.0) if k % 2 else (0.56, 0.62, 0.66, 1.0)))
    make_cyl("Hall_Light", (0.0, 6.10, CEIL - 0.05), 0.16, 0.08, (0.96, 0.94, 0.86, 1.0), segments=12)
    make_smoke_detector("Smoke_Hall", (-1.8, 6.10, CEIL))
    make_thermostat("Thermostat", (-1.6, HALL_S), axis='X', face_sign=1)
    make_light_switch("Switch_Bath", (0.80, HALL_N), axis='X', face_sign=-1)
    make_light_switch("Switch_Bedroom", (2.65, HALL_N), axis='X', face_sign=-1)
    make_light_switch("Switch_Front", (-0.30, Y0), axis='X', face_sign=1)
    make_wall_outlet("Outlet_TV", (X0, 3.60), axis='Y', face_sign=1)
    make_wall_outlet("Outlet_Bed", (X1, 9.00), axis='Y', face_sign=-1)
    make_wall_outlet("Outlet_Kitchen", (1.10, HALL_S), axis='X', face_sign=-1)
    make_threshold("Threshold_Bath", (0.20, HALL_N), width=0.8, axis='X')
    wear = (CARPET[0] * 0.88, CARPET[1] * 0.88, CARPET[2] * 0.88, 1.0)
    make_traffic_wear("Wear_Front_To_Hall", [(-1.0, 0.4), (-2.2, 3.0), (-3.0, 5.6)], width=0.7, tint=wear)
    make_traffic_wear("Wear_Hall", [(-3.0, 6.1), (3.2, 6.1)], width=0.6, tint=wear)
    pw = PAL_WALL["wall"]
    make_wall_tint_band("Band_Living_W", (X0 + 0.105, 2.75, 0.0), length=5.0, axis='Y', band_z=CEIL - 0.16,
                        tint=(pw[0] * 0.92, pw[1] * 0.92, pw[2] * 0.90, 1.0))


def main():
    clear_scene()
    build_shell()
    build_living()
    build_kitchen()
    build_bath()
    build_bedroom()
    build_bed2()
    build_hall_and_infra()
    # through the front windows the street; through the back ones the yard
    make_view("View_S", "S", Y0, 0.0, kind="front", ground_z=0.0, seed=3)
    make_view("View_N", "N", Y1, 0.0, kind="back", ground_z=0.0, seed=5)
    make_view("View_E", "E", X1, 2.2, kind="back", ground_z=0.0, seed=8)
    out = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                        "../../../assets/3d/locales/link_house.glb"))
    print(f"\n[build_link_house] exporting to {out}")
    export_glb(out)


if __name__ == "__main__":
    main()
