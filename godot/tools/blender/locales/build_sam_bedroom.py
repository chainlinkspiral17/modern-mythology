"""Sam's Bedroom — vol6 — SAM MILLER, upstairs at 1428 Meadowlark Circle
(Chief Miller's daughter; she works the Kwik Stop eight to four and
drives the Corolla).

DRAFT 5 (2026-10-09, the overnight run): THE WRONG PERSON. Drafts 1-4
dressed this as "Sam (the kid protagonist; into Cosmic Comics and video
games) ... boyish ... his door": a captain's bed, comic longboxes, a CRT
and a console, a skateboard, stickers on HIS door. Every scene that uses
the preset (vol6 ch0, ch1, ch3, ch4, ch5, ch6, ch15) is Sam Miller's:
  "She looks around her cornflower blue bedroom. The fan is still going.
   The fan still clicks on the third rotation, then the sixth, then the
   ninth." · "She is at her desk now, in her pajamas, with the lamp on
   against the grey of the storm. She is making a list ... WEDNESDAY
   LIST." · "She crosses to the window. She looks out at the cul-de-sac
   ... The NexCorp logo on the mailbox" · "Outside, the cracked
   sprinkler head throws its angled jet across the sidewalk" · "Sam's
   phone, on her dresser, buzzes." · "She wakes at 03:04. She writes the
   dream down." · "She goes to the closet. She gets dressed for work."
Rebuilt as hers:
  - cornflower-blue walls, white trim, a light carpet;
  - THE FAN: a five-blade ceiling fan with its light kit and pull chain;
  - the window on the cul-de-sac (sheers and drapes), and past it, two
    floors down, the front lawn with THE CRACKED SPRINKLER throwing its
    arc onto the sidewalk's grey stripe, the street, the houses across,
    the mailboxes with the NexCorp logo;
  - the bed with the nightstand, the lamp, the dream notebook;
  - the desk with the lamp, the legal pad (the WEDNESDAY LIST), the
    corkboard over it (the shift schedule, a photo strip);
  - the dresser with her phone, the mirror, the Kwik Stop name tag;
  - the closet, the Kwik Stop polo hanging on its door for the morning;
  - a bookshelf, a laundry basket, a rug, her door.
Coordinate frame: Blender Z-up. y=0 is the door (S) wall; the window is
in the N wall over the cul-de-sac. glTF export remaps to Godot (x, z, -y).

Draft 6 targets: the fan's blades turning (a rotation script, or the
blades as a blur card); her parents' room down the hall for ch3's
"insert door"; the sprinkler's wet sidewalk at 6:12; Deck framing.
"""
import math
import os, sys
_BT = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
if _BT not in sys.path: sys.path.insert(0, _BT)
from _props import palette as P
from _props.geometry import (clear_scene, make_box, make_chamfer_box, make_cyl, make_lathe,
                             make_tube, make_rot_box, export_glb)
from _props.structure import make_floor, make_wall, make_ceiling, make_crown_molding, make_wall_with_openings
from _props.views import make_view
from _props.decor import make_floor_plant
from _props.furniture import make_bed, make_chair, make_lamp
from _props.detail import make_traffic_wear, make_floor_stain, make_light_switch, make_wall_outlet

ROOM_W = 4.8; ROOM_D = 5.6; CEIL = 2.6
XW, XE, YS, YN = -ROOM_W / 2.0 + 0.10, ROOM_W / 2.0 - 0.10, 0.10, ROOM_D - 0.10
PAL_WALL = {"wall": (0.50, 0.62, 0.86, 1.0), "baseboard": (0.92, 0.92, 0.90, 1.0)}   # cornflower blue, white trim
COL_CARPET = (0.74, 0.70, 0.62, 1.0); COL_SEAM = (0.73, 0.69, 0.61, 1.0)   # carpet: no tile seams
COL_OAK = (0.66, 0.52, 0.36, 1.0); COL_OAK_DK = (0.54, 0.42, 0.28, 1.0)
COL_WHITE = (0.92, 0.92, 0.90, 1.0)
COL_BEDDING = (0.90, 0.90, 0.88, 1.0); COL_QUILT = (0.58, 0.68, 0.88, 1.0)
COL_KWIK = (0.78, 0.18, 0.16, 1.0)       # the Kwik Stop red
DOOR = (1.30, 1.04, 0.86, 2.08)
WIN = (0.0, 1.50, 1.30, 1.10)


def build_shell():
    make_floor("Floor", (0.0, ROOM_D / 2.0, 0.0), size_x=ROOM_W + 0.4, size_y=ROOM_D + 0.4,
               palette={"vinyl": COL_CARPET, "seam": COL_SEAM})
    make_wall("Wall_W", (-ROOM_W / 2.0, ROOM_D / 2.0, 0), length=ROOM_D + 0.4, height=CEIL, axis='Y', palette=PAL_WALL, baseboard_face_sign=+1)
    make_wall("Wall_E", (ROOM_W / 2.0, ROOM_D / 2.0, 0), length=ROOM_D + 0.4, height=CEIL, axis='Y', palette=PAL_WALL, baseboard_face_sign=-1)
    make_wall_with_openings("Wall_N", (0.0, ROOM_D, 0), length=ROOM_W + 0.4, height=CEIL, axis='X', palette=PAL_WALL,
                            baseboard_face_sign=-1, openings=[WIN])
    make_wall_with_openings("Wall_S", (0.0, 0.0, 0), length=ROOM_W + 0.4, height=CEIL, axis='X', palette=PAL_WALL,
                            baseboard_face_sign=+1, openings=[DOOR])
    make_ceiling("Ceil", (0.0, ROOM_D / 2.0, CEIL), size_x=ROOM_W + 0.4, size_y=ROOM_D + 0.4,
                 with_grid=False, with_stains=False, palette={"tile": (0.94, 0.94, 0.92, 1.0)})
    for nm, ax, length, wx, wy in [("Crown_W", 'Y', ROOM_D, XW, ROOM_D / 2.0), ("Crown_E", 'Y', ROOM_D, XE, ROOM_D / 2.0),
                                    ("Crown_N", 'X', ROOM_W, 0.0, YN), ("Crown_S", 'X', ROOM_W, 0.0, YS)]:
        make_crown_molding(nm, wall_x=wx, wall_y=wy, length=length, axis=ax, ceil_z=CEIL, palette={"wood": COL_WHITE})
    # her door, closed: a six-panel leaf, the knob, the casing
    dx = DOOR[0]
    make_box("Bedroom_Door_Leaf", (dx, 0.0, 1.035), (0.84, 0.045, 2.07), COL_WHITE)
    for i, (oz, h) in enumerate(((0.45, 0.62), (1.18, 0.50), (1.74, 0.42))):
        for j, ox in enumerate((-0.19, 0.19)):
            make_box(f"Bedroom_Door_Panel_{i}_{j}", (dx + ox, 0.026, oz), (0.30, 0.008, h), (0.88, 0.88, 0.86, 1.0))
    make_cyl("Bedroom_Door_Knob", (dx - 0.32, 0.05, 0.98), 0.03, 0.05, (0.72, 0.64, 0.40, 1.0), segments=10, axis='Y')
    for nm, x in (("A", dx - DOOR[2] / 2.0 - 0.035), ("B", dx + DOOR[2] / 2.0 + 0.035)):
        make_box(f"Bedroom_Door_Casing_{nm}", (x, YS + 0.01, 1.07), (0.07, 0.02, 2.14), COL_WHITE)
    make_box("Bedroom_Door_Casing_Head", (dx, YS + 0.01, 2.115), (DOOR[2] + 0.14, 0.02, 0.07), COL_WHITE)
    make_light_switch("Switch_Door", (dx - 0.62, 0.0), axis='X', face_sign=1, z=1.20)


def build_fan():
    """THE FAN — "The fan still clicks on the third rotation." Canopy,
    downrod, motor, five blades on irons, the light kit, the pull chain."""
    fx, fy = 0.0, 2.9
    make_cyl("Fan_Canopy", (fx, fy, CEIL - 0.04), 0.08, 0.08, COL_WHITE, segments=12)
    make_cyl("Fan_Downrod", (fx, fy, CEIL - 0.20), 0.015, 0.26, COL_WHITE, segments=6)
    make_cyl("Fan_Motor", (fx, fy, CEIL - 0.37), 0.13, 0.10, COL_WHITE, segments=14)
    for k in range(5):
        a = math.radians(k * 72.0 + 12.0)
        r = 0.42
        make_rot_box(f"Fan_Blade_{k}", (fx + r * math.cos(a), fy + r * math.sin(a), CEIL - 0.37), (0.56, 0.13, 0.012), COL_OAK, yaw=a)
        make_rot_box(f"Fan_Blade_Iron_{k}", (fx + 0.14 * math.cos(a), fy + 0.14 * math.sin(a), CEIL - 0.37), (0.12, 0.04, 0.02), COL_WHITE, yaw=a)
    make_lathe("Fan_Light_Kit", (fx, fy, CEIL - 0.55), [(0.0, 0.0), (0.08, 0.01), (0.12, 0.06), (0.12, 0.13), (0.0, 0.13)], (0.96, 0.94, 0.86, 1.0), segments=14)
    make_cyl("Fan_Pull_Chain", (fx + 0.06, fy, CEIL - 0.64), 0.003, 0.18, (0.70, 0.66, 0.50, 1.0), segments=4)
    make_cyl("Fan_Pull_Fob", (fx + 0.06, fy, CEIL - 0.74), 0.012, 0.03, (0.70, 0.66, 0.50, 1.0), segments=6)


def build_window():
    """The window on the cul-de-sac: frame, the glass, sheers and drapes;
    the view two floors down."""
    wx, wz, ww, wh = WIN
    for nm, c, sz in (("Head", (wx, ROOM_D, wz + wh / 2.0 - 0.035), (ww, 0.10, 0.07)),
                      ("Sill", (wx, ROOM_D, wz - wh / 2.0 + 0.035), (ww, 0.10, 0.07)),
                      ("JambW", (wx - ww / 2.0 + 0.035, ROOM_D, wz), (0.07, 0.10, wh - 0.14)),
                      ("JambE", (wx + ww / 2.0 - 0.035, ROOM_D, wz), (0.07, 0.10, wh - 0.14)),
                      ("Mullion", (wx, ROOM_D, wz), (0.04, 0.06, wh - 0.14))):
        make_box(f"Window_Frame_{nm}", c, sz, COL_WHITE)
    make_box("Window_Glass", (wx, ROOM_D, wz), (ww - 0.14, 0.01, wh - 0.14), (0.62, 0.70, 0.78, 0.45))
    make_box("Window_Stool", (wx, YN - 0.07, wz - wh / 2.0 - 0.015), (ww + 0.16, 0.16, 0.03), COL_WHITE)
    rz = wz + wh / 2.0 + 0.16
    make_cyl("Curtain_Rod", (wx, YN - 0.10, rz), 0.012, ww + 0.80, (0.76, 0.72, 0.62, 1.0), segments=6, axis='X')
    for k, x in enumerate((wx - ww / 2.0 - 0.32, wx + ww / 2.0 + 0.32)):
        make_box(f"Curtain_Rod_Bracket_{k}", (x, YN - 0.05, rz), (0.02, 0.10, 0.02), (0.76, 0.72, 0.62, 1.0))
    for nm, x in (("W", wx - ww / 2.0 - 0.14), ("E", wx + ww / 2.0 + 0.14)):
        make_box(f"Curtain_Drape_{nm}", (x, YN - 0.10, (rz - 0.012 + 0.30) / 2.0), (0.34, 0.06, rz - 0.012 - 0.30), (0.88, 0.86, 0.80, 1.0))
    make_box("Curtain_Sheer", (wx + ww / 2.0 - 0.10, YN - 0.13, (rz - 0.012 + 0.90) / 2.0), (0.26, 0.012, rz - 0.012 - 0.90), (0.96, 0.96, 0.94, 0.6))   # drawn aside: it renders opaque
    # the front of the house two floors down: lawn, walk, street, the
    # houses across and their NexCorp-logo mailboxes
    make_view("View_Front", "N", ROOM_D, 0.0, kind="front", ground_z=-3.0, seed=4, logo_mailbox=True)
    # THE CRACKED SPRINKLER: the head in the lawn, its angled jet across
    # the sidewalk, the grey stripe it etched in the concrete
    g = -3.0
    sx, sy = 0.4, ROOM_D + 3.2
    make_cyl("Sprinkler_Head", (sx, sy, g + 0.03), 0.04, 0.06, (0.20, 0.20, 0.20, 1.0), segments=8)
    make_box("Sprinkler_Head_Crack", (sx + 0.03, sy, g + 0.05), (0.005, 0.03, 0.03), (0.70, 0.70, 0.66, 1.0))
    make_tube("Sprinkler_Jet", [(sx, sy, g + 0.06), (sx + 0.4, sy + 1.6, g + 0.95), (sx + 0.8, sy + 3.4, g + 1.15), (sx + 1.1, sy + 5.0, g + 0.55), (sx + 1.25, sy + 5.75, g + 0.02)],
              0.018, (0.78, 0.86, 0.92, 0.6), segments=5)
    make_box("Sidewalk_Stripe", (sx + 1.25, ROOM_D + 0.1 + 8.9, g + 0.006), (0.30, 1.18, 0.004), (0.44, 0.44, 0.44, 1.0))


def build_bed():
    """The bed, head to the W wall; the nightstand with the lamp and the
    dream notebook ("She wakes at 03:04. She writes the dream down.")."""
    bx, by = XW + 1.02, 3.55
    top = make_bed("Bed", bx, by, head="-X", w=1.40, d=2.0, style="frame", frame_col=COL_OAK,
                   mattress_col=(0.90, 0.89, 0.85, 1.0), sheet_col=COL_BEDDING, blanket_col=COL_QUILT,
                   pillow_col=COL_BEDDING, pillows=2, made=False)
    nx, ny = XW + 0.25, by + 0.95
    make_box("Nightstand", (nx, ny, 0.30), (0.44, 0.40, 0.60), COL_WHITE)
    make_box("Nightstand_Drawer", (nx + 0.225, ny, 0.47), (0.012, 0.34, 0.14), (0.88, 0.88, 0.86, 1.0))
    make_lamp("Bedside_Lamp", nx - 0.05, ny + 0.06, base_z=0.60, h=0.46, shade_col=(0.94, 0.92, 0.84, 1.0), body_col=(0.80, 0.78, 0.70, 1.0))
    make_box("Dream_Notebook", (nx + 0.06, ny - 0.10, 0.6075), (0.15, 0.21, 0.015), (0.30, 0.42, 0.62, 1.0))
    make_box("Dream_Notebook_Pen", (nx + 0.06, ny - 0.10, 0.619), (0.01, 0.14, 0.008), (0.12, 0.12, 0.14, 1.0))
    make_box("Bedside_Water", (nx + 0.14, ny + 0.10, 0.65), (0.06, 0.06, 0.10), (0.80, 0.84, 0.88, 0.6))
    make_wall_outlet("Outlet_Bed", (-ROOM_W / 2.0, ny + 0.30), axis='Y', face_sign=1)
    make_tube("Bedside_Lamp_Cord", [(nx - 0.05, ny + 0.12, 0.61), (XW + 0.02, ny + 0.20, 0.58), (XW + 0.02, ny + 0.30, 0.32)], 0.004, (0.20, 0.20, 0.20, 1.0), segments=4)
    make_box("Bed_Slippers", (bx + 1.15, by - 0.55, 0.03), (0.24, 0.26, 0.06), (0.86, 0.76, 0.80, 1.0))
    make_box("Rug", (-0.15, 3.30, 0.008), (1.10, 1.60, 0.008), (0.40, 0.48, 0.66, 1.0))
    # a framed print over the bed
    make_box("Bed_Print_Frame", (XW + 0.015, by, 1.62), (0.03, 0.70, 0.52), COL_OAK_DK)
    make_box("Bed_Print_Image", (XW + 0.032, by, 1.62), (0.004, 0.60, 0.42), (0.80, 0.74, 0.58, 1.0))
    make_box("Bed_Print_Field", (XW + 0.035, by + 0.08, 1.58), (0.003, 0.30, 0.20), (0.46, 0.56, 0.38, 1.0))


def build_desk():
    """The desk on the E wall: the lamp, the legal pad with the WEDNESDAY
    LIST, pens, the corkboard over it."""
    dx, dy = XE - 0.30, 2.70
    make_box("Desk_Top", (dx, dy, 0.74), (0.60, 1.24, 0.04), COL_OAK)
    for li, (ox, oy) in enumerate(((-0.26, -0.58), (0.26, -0.58), (-0.26, 0.58), (0.26, 0.58))):
        make_box(f"Desk_Leg_{li}", (dx + ox, dy + oy, 0.36), (0.04, 0.04, 0.72), COL_OAK_DK)
    make_box("Desk_Drawer", (dx, dy - 0.30, 0.66), (0.56, 0.50, 0.12), COL_OAK_DK)
    make_box("Desk_Drawer_Front", (dx - 0.285, dy - 0.30, 0.66), (0.01, 0.46, 0.10), COL_OAK)
    make_chair("Desk_Chair", dx - 0.62, dy + 0.05, yaw=-math.pi / 2.0, wood=COL_OAK, seat_col=COL_QUILT, w=0.42)
    make_lamp("Desk_Lamp", dx + 0.12, dy + 0.42, base_z=0.76, h=0.48, shade_col=(0.30, 0.42, 0.66, 1.0), body_col=(0.80, 0.78, 0.70, 1.0))
    make_box("Legal_Pad", (dx - 0.06, dy - 0.05, 0.764), (0.22, 0.30, 0.008), (0.96, 0.90, 0.44, 1.0))
    # the top sheet: WEDNESDAY LIST in block capitals, the items under it
    make_box("Wednesday_List_Header", (dx - 0.06, dy - 0.17, 0.7685), (0.16, 0.03, 0.001), (0.12, 0.12, 0.16, 1.0))
    for k in range(5):
        make_box(f"Wednesday_List_Line_{k}", (dx - 0.06, dy - 0.11 + k * 0.045, 0.7685), (0.17, 0.008, 0.001), (0.20, 0.22, 0.40, 1.0))
    make_box("Desk_Pen", (dx + 0.10, dy - 0.02, 0.765), (0.01, 0.14, 0.01), (0.12, 0.14, 0.30, 1.0))
    make_lathe("Desk_Mug_Pens", (dx + 0.16, dy - 0.45, 0.76), [(0.0, 0.0), (0.04, 0.0), (0.04, 0.10), (0.0, 0.10)], (0.92, 0.88, 0.80, 1.0), segments=10)
    # the corkboard: the Kwik Stop shift schedule, a photo strip, a ticket stub
    cz = 1.55
    make_box("Corkboard", (XE - 0.015, dy, cz), (0.03, 1.00, 0.66), (0.70, 0.54, 0.36, 1.0))
    make_box("Corkboard_Frame", (XE - 0.012, dy, cz), (0.024, 1.06, 0.72), COL_OAK_DK)
    for k, (oy, oz, w, h, col) in enumerate(((-0.28, 0.08, 0.26, 0.34, (0.94, 0.94, 0.92, 1.0)), (0.05, 0.12, 0.08, 0.26, (0.30, 0.30, 0.32, 1.0)),
                                             (0.22, -0.10, 0.20, 0.14, (0.82, 0.62, 0.70, 1.0)), (-0.05, -0.18, 0.14, 0.10, COL_KWIK))):
        make_box(f"Corkboard_Pinned_{k}", (XE - 0.033, dy + oy, cz + oz), (0.004, w, h), col)
    make_wall_outlet("Outlet_Desk", (ROOM_W / 2.0, dy + 0.45), axis='Y', face_sign=-1, z=0.30)


def build_dresser_closet():
    """The dresser by the door (her phone on it, the mirror, the name
    tag), the closet with the work polo hanging on its door."""
    ddx, ddy = -1.15, YS + 0.26
    make_box("Dresser", (ddx, ddy, 0.46), (1.10, 0.48, 0.92), COL_WHITE)
    for i in range(3):
        for j, ox in enumerate((-0.27, 0.27)):
            make_box(f"Dresser_Drawer_{i}_{j}", (ddx + ox, ddy + 0.245, 0.18 + i * 0.27), (0.50, 0.012, 0.22), (0.88, 0.88, 0.86, 1.0))
            make_box(f"Dresser_Drawer_{i}_{j}_Pull", (ddx + ox, ddy + 0.255, 0.22 + i * 0.27), (0.10, 0.012, 0.015), (0.72, 0.64, 0.40, 1.0))
    make_box("Sams_Phone", (ddx + 0.25, ddy + 0.05, 0.9255), (0.072, 0.145, 0.011), (0.14, 0.14, 0.16, 1.0))
    make_box("Sams_Phone_Screen", (ddx + 0.25, ddy + 0.05, 0.9315), (0.062, 0.128, 0.001), (0.32, 0.44, 0.58, 1.0))
    make_box("Kwik_Name_Tag", (ddx - 0.10, ddy + 0.08, 0.923), (0.08, 0.025, 0.006), COL_KWIK)
    make_lathe("Dresser_Dish", (ddx - 0.32, ddy + 0.02, 0.92), [(0.0, 0.0), (0.05, 0.0), (0.08, 0.025), (0.07, 0.03), (0.0, 0.008)], (0.80, 0.76, 0.86, 1.0), segments=12)
    make_box("Car_Keys", (ddx - 0.32, ddy + 0.02, 0.935), (0.06, 0.03, 0.01), (0.70, 0.70, 0.66, 1.0))
    make_box("Dresser_Mirror_Frame", (ddx, YS + 0.02, 1.42), (0.80, 0.03, 0.70), COL_WHITE)
    make_box("Dresser_Mirror", (ddx, YS + 0.037, 1.42), (0.70, 0.004, 0.60), (0.70, 0.76, 0.82, 1.0))
    make_box("Dresser_Mirror_Photo", (ddx + 0.30, YS + 0.041, 1.62), (0.08, 0.003, 0.11), (0.86, 0.80, 0.70, 1.0))
    # the closet on the E wall's S end: bifold doors, the polo on the top rail
    cy0, cy1 = 0.45, 1.65
    for k in range(4):
        y = cy0 + (cy1 - cy0) * (k + 0.5) / 4.0
        make_box(f"Closet_Door_Leaf_{k}", (XE - 0.02, y, 1.04), (0.03, (cy1 - cy0) / 4.0 - 0.01, 2.06), COL_WHITE)
        make_box(f"Closet_Door_Leaf_{k}_Louvre", (XE - 0.037, y, 1.35), (0.004, (cy1 - cy0) / 4.0 - 0.08, 0.90), (0.86, 0.86, 0.84, 1.0))
    make_box("Closet_Casing_Head", (XE - 0.01, (cy0 + cy1) / 2.0, 2.11), (0.02, cy1 - cy0 + 0.14, 0.07), COL_WHITE)
    make_box("Kwik_Polo_Hanger", (XE - 0.05, 1.05, 2.07), (0.04, 0.36, 0.02), (0.30, 0.26, 0.22, 1.0))
    make_box("Kwik_Polo", (XE - 0.07, 1.05, 1.74), (0.05, 0.46, 0.64), COL_KWIK)
    make_box("Kwik_Polo_Collar", (XE - 0.073, 1.05, 2.04), (0.052, 0.18, 0.04), (0.66, 0.14, 0.12, 1.0))
    make_box("Kwik_Polo_Logo", (XE - 0.096, 0.96, 1.92), (0.002, 0.08, 0.05), (0.96, 0.92, 0.80, 1.0))
    # the laundry basket by the closet
    make_lathe("Laundry_Basket", (XE - 0.40, 1.95, 0.0), [(0.0, 0.0), (0.20, 0.0), (0.23, 0.40), (0.21, 0.40), (0.18, 0.02), (0.0, 0.02)], (0.86, 0.86, 0.84, 1.0), segments=14)
    make_box("Laundry_Top", (XE - 0.40, 1.95, 0.38), (0.30, 0.26, 0.04), (0.44, 0.52, 0.70, 1.0))


def build_bookshelf():
    """The bookshelf on the N wall E of the window (paperbacks, the
    yearbooks, a plant on top)."""
    bx, by, w, h, d = 1.65, YN - 0.15, 0.80, 1.60, 0.30
    make_box("Bookshelf_Back", (bx, YN - 0.01, h / 2.0), (w, 0.02, h), COL_WHITE)
    for nm, ox in (("A", -w / 2.0 + 0.01), ("B", w / 2.0 - 0.01)):
        make_box(f"Bookshelf_Side_{nm}", (bx + ox, by, h / 2.0), (0.02, d, h), COL_WHITE)
    for si, z in enumerate((0.04, 0.42, 0.80, 1.18, 1.59)):
        make_box(f"Bookshelf_Shelf_{si}", (bx, by, z), (w - 0.04, d, 0.025), COL_WHITE)
    for si, z in enumerate((0.0525, 0.4325, 0.8125, 1.1925)):
        x = bx - w / 2.0 + 0.04
        k = 0
        while x < bx + w / 2.0 - 0.06:
            t = 0.03 + 0.01 * ((k + si) % 3)
            hh = 0.20 + 0.03 * ((k * 2 + si) % 4)
            make_box(f"Bookshelf_Book_{si}_{k}", (x + t / 2.0, by + 0.02, z + hh / 2.0), (t, 0.20, hh), P.SNACK_TINTS[(k + si * 3) % len(P.SNACK_TINTS)])
            x += t + 0.003
            k += 1
            if k == 9 and si == 1:
                x += 0.10
    make_floor_plant("Plant", (bx - 0.18, by, 1.6025), palette={"leaf": (0.36, 0.52, 0.34, 1.0), "pot": (0.86, 0.80, 0.72, 1.0)})


def build_wear():
    dk = (COL_CARPET[0] * 0.88, COL_CARPET[1] * 0.88, COL_CARPET[2] * 0.88, 1.0)
    make_traffic_wear("Wear_Path", [(DOOR[0], 0.5), (DOOR[0], 1.9), (0.0, 2.4), (-0.6, 3.6)], width=0.55, tint=dk)
    make_floor_stain("Wear_Chair", (XE - 0.92, 2.75), radius=0.28, tint=dk, segments=10)
    make_floor_stain("Wear_Window", (0.0, YN - 0.45), radius=0.30, tint=dk, segments=10)


def main():
    clear_scene()
    build_shell()
    build_fan()
    build_window()
    build_bed()
    build_desk()
    build_dresser_closet()
    build_bookshelf()
    build_wear()
    out = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)),
        "../../../assets/3d/locales/sam_bedroom.glb"))
    print(f"\n[build_sam_bedroom] exporting to {out}")
    export_glb(out)


if __name__ == "__main__":
    main()
