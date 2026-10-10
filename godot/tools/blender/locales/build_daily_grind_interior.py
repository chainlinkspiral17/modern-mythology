"""daily_grind_interior — the Daily Grind, Smolvud (vol 7): Soren's coffee
shop on Main, where Lena works the bar.

DRAFT 3 (2026-10-10) — rebuilt from the prose at the size such a place
really is. Drafts 1-2 were a 7 x 6 m box under a 2.8 m ceiling: one
counter, three tables, a nook. Vol 7 says:

  "Lena opened the Daily Grind at six oh-four. She unlocked the back
  door ... The unlocking woke the heat-pump compressor that ran the
  hot-water lines for the espresso bar ... She turned on the lights. She
  turned on the espresso machine. She filled the ceramic milk pitchers
  from the cooler and set them on the bar in the order the morning
  regulars liked their drinks pulled ... She drank it standing at the
  bar looking through the front window at the slate-gray light over
  Main." · "The bell over the door rang at six-eleven." · "Wren came in
  at six-eleven for her hot chocolate and her ten minutes at the corner
  table" · "The marshmallow was a single small one, hand-cut from a slab
  that Hans the baker on Hemlock made and sold to the Daily Grind for a
  stack of tokens" · "Kai was at the corner table with his laptop open
  and his phone beside it." · "He sat in the fourth chair." · the OPEN /
  CLOSED sign in the door; the alley shortcut at the back; Lena's studio
  "a back room behind the Daily Grind".

So: the ground floor of an old brick commercial building on a corner of
Main, 12 x 10 m under a 3.6 m pressed-tin ceiling, glass on the two street
sides:
  · THE BAR along the back, facing the front window: the pastry case of
    Hans's bread and pastries, the register with its token reader and tip
    jar, the two-group machine with the five ceramic milk pitchers lined
    up beside it, the grinder, the hand-off with Wren's hot chocolate and
    its marshmallow, the under-counter milk cooler; behind it the back
    bar — sink, pour-over station and kettle, hot-water tower, the decaf
    grinder, cups, bags of beans, the batch brewer — the open shelves of
    mugs, the chalkboard menu, and the insulated copper lines coming down
    from the heat pump.
  · THE CORNER TABLE in the SW, where the two window walls meet: four
    chairs, Kai's laptop and phone, the Frequency paperback, Wren's
    notebook, Finn's duffel on the floor by the fourth chair.
  · The window bar on Main with three stools, two two-tops along the side
    windows, five round tables, the banquette on the brick wall with
    LENA'S PAINTINGS over it on a track light, the lounge (couch, two
    armchairs, the book swap shelf, the floor lamp) in the NW, the
    community board, the condiment station by the door, the door with its
    bell and its OPEN / CLOSED sign.
  · The back hall past the N wall: the restroom, the hot-water tank, the
    back door to the alley under its EXIT sign.
  · Outside: Main on the S, the cross street on the W, and the tower on
    the hill past the corner, "longer than the town".

Coordinate frame: Blender Z-up; y=0 is the Main Street (S) front, +Y back
to the bar; walls x=+-6, back wall y=10, the hall to y=12.6. glTF export
remaps to Godot (x, z, -y).

Draft 4 targets: the rain on the glass (streaks on the window line, the
wet street's sheen); the studio door off the alley visible through the
back door's window; morning vs afternoon dressing (the chairs up on the
tables before six-oh-four); a second room of the building over the
transom (the stair to Soren's upstairs).
"""
import math
import os
import random
import sys
_BT = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
if _BT not in sys.path: sys.path.insert(0, _BT)
from _props import palette as P
from _props.geometry import clear_scene, make_box, make_cyl, make_lathe, make_rot_box, export_glb
from _props.views import make_view
from _props.structure import make_floor, make_wall, make_window, make_wall_with_openings
from _props.furniture import make_chair, make_stool
from _props.decor import make_floor_plant
from _props.safety import make_smoke_detector, make_fluorescent_tube_fixture

X0, X1 = -6.0, 6.0
Y0, Y1 = 0.0, 10.0
CEIL = 3.6
HALL_Y1 = 12.6                   # the back hall's N wall
HALL_X1 = -0.4                   # the back hall's E wall
HALL_DOOR_X = -1.6               # the opening from the cafe into the hall

PAL_WALL = {"wall": (0.82, 0.76, 0.66, 1.0), "baseboard": (0.30, 0.22, 0.16, 1.0)}
COL_BRICK = (0.56, 0.30, 0.22, 1.0)
COL_MORTAR = (0.70, 0.62, 0.52, 1.0)
COL_FLOOR = (0.56, 0.42, 0.30, 1.0)       # old fir
COL_SEAM = (0.36, 0.26, 0.18, 1.0)
COL_TIN = (0.86, 0.82, 0.70, 1.0)
COL_FIR = (0.60, 0.44, 0.30, 1.0)         # the counter's reclaimed boards
COL_FIR_DK = (0.46, 0.32, 0.22, 1.0)
COL_WOOD = (0.42, 0.30, 0.20, 1.0)
COL_TOP = (0.20, 0.18, 0.16, 1.0)         # soapstone counter top
COL_STEEL = P.METAL_STEEL
COL_BLACK = P.METAL_BLACK
COL_CHROME = (0.80, 0.80, 0.78, 1.0)
COL_FRAME = (0.16, 0.28, 0.24, 1.0)       # the storefront's green
COL_GLASS = (0.70, 0.78, 0.82, 0.30)      # LocaleGlass draws vertex alpha as real transparency
COL_CERAMIC = (0.92, 0.90, 0.84, 1.0)
COL_CHALK = (0.14, 0.16, 0.15, 1.0)
COL_COUCH = (0.40, 0.32, 0.26, 1.0)
COL_CUSH = (0.50, 0.40, 0.32, 1.0)
COL_PAPER = (0.94, 0.92, 0.86, 1.0)
COL_BULB = (0.98, 0.88, 0.62, 1.0)
COL_COPPER = (0.72, 0.42, 0.24, 1.0)


# ═══════════════════════════════════════════════════════════ the shell
def build_shell():
    make_floor("Floor", (0.0, (Y0 + Y1) / 2.0, 0.0), size_x=X1 - X0 + 0.4, size_y=Y1 - Y0 + 0.4,
               palette={"vinyl": COL_FLOOR, "seam": COL_SEAM})
    make_box("Hall_Floor", ((X0 + HALL_X1) / 2.0, (Y1 + HALL_Y1) / 2.0, -0.05), (HALL_X1 - X0 + 0.2, HALL_Y1 - Y1 + 0.2, 0.10),
             (0.50, 0.50, 0.48, 1.0))
    # W wall (the cross street): two big windows; it runs on past the cafe as the hall's W wall
    make_wall_with_openings("Wall_W", (X0, (Y0 + HALL_Y1) / 2.0, 0), length=HALL_Y1 - Y0 + 0.4, height=CEIL, axis='Y',
                            palette=PAL_WALL, baseboard_face_sign=+1,
                            openings=[(2.4, 1.70, 4.0, 2.4), (6.4, 1.70, 2.4, 2.4)])
    # E wall: the exposed brick, its courses picked out in mortar
    make_wall("Wall_E", (X1, (Y0 + Y1) / 2.0, 0), length=Y1 - Y0 + 0.4, height=CEIL, axis='Y',
              palette={"wall": COL_BRICK, "baseboard": (0.30, 0.22, 0.16, 1.0)}, baseboard_face_sign=-1)
    for k in range(1, 12):
        make_box(f"Wall_E_Mortar_{k}", (X1 - 0.101, (Y0 + Y1) / 2.0, 0.16 + k * 0.29), (0.004, Y1 - Y0 - 0.02, 0.012), COL_MORTAR)
    # S wall (Main): the big window, the second window, the door, the small window by the door
    make_wall_with_openings("Wall_S", (0.0, Y0, 0), length=X1 - X0 + 0.4, height=CEIL, axis='X', palette=PAL_WALL,
                            baseboard_face_sign=+1,
                            openings=[(-3.1, 1.70, 5.4, 2.4), (1.3, 1.70, 2.6, 2.4), (3.4, 1.15, 1.0, 2.3), (5.0, 1.70, 1.4, 2.4)])
    # N wall, with the opening to the back hall
    make_wall_with_openings("Wall_N", (0.0, Y1, 0), length=X1 - X0 + 0.4, height=CEIL, axis='X', palette=PAL_WALL,
                            baseboard_face_sign=-1, openings=[(HALL_DOOR_X, 1.05, 0.95, 2.10)])
    # the windows: frames and mullions in the storefront green; the glass is vertex-alpha
    for k, (cx, w) in enumerate(((-3.1, 5.4), (1.3, 2.6), (5.0, 1.4))):
        make_window(f"Win_S_{k}", (cx, Y0 + 0.10, 1.70), width=w, height=2.4, room_dir=+1, see_through=True,
                    palette={"frame": COL_FRAME}, cross_mullion=(w > 2.0))
        make_box(f"Win_S_{k}_Glass", (cx, Y0 + 0.02, 1.70), (w, 0.01, 2.4), COL_GLASS)
        make_box(f"Win_S_{k}_Stool", (cx, Y0 + 0.17, 0.49), (w + 0.10, 0.14, 0.03), COL_FIR_DK)   # the inside sill
    for k, (cy, w) in enumerate(((2.4, 4.0), (6.4, 2.4))):
        make_window(f"Win_W_{k}", (X0 + 0.10, cy, 1.70), width=w, height=2.4, axis='Y', room_dir=+1, see_through=True,
                    palette={"frame": COL_FRAME}, cross_mullion=True)
        make_box(f"Win_W_{k}_Glass", (X0 + 0.02, cy, 1.70), (0.01, w, 2.4), COL_GLASS)
        make_box(f"Win_W_{k}_Stool", (X0 + 0.17, cy, 0.49), (0.14, w + 0.10, 0.03), COL_FIR_DK)
    # the front door: a green-framed glass door, the bell over it, the OPEN / CLOSED sign
    dx = 3.4
    for e in (-1, 1):
        make_box(f"Front_Door_Stile_{e:+d}", (dx + e * 0.44, Y0 + 0.02, 1.14), (0.10, 0.05, 2.28), COL_FRAME)
    make_box("Front_Door_Rail_Top", (dx, Y0 + 0.02, 2.22), (0.78, 0.05, 0.12), COL_FRAME)
    make_box("Front_Door_Rail_Bottom", (dx, Y0 + 0.02, 0.15), (0.78, 0.05, 0.30), COL_FRAME)
    make_box("Front_Door_Glass", (dx, Y0 + 0.02, 1.23), (0.78, 0.01, 1.86), COL_GLASS)
    make_box("Front_Door_Pull", (dx - 0.44, Y0 + 0.07, 1.05), (0.03, 0.05, 0.40), COL_CHROME)   # on the stile
    make_box("Door_Sign_Hook", (dx, Y0 + 0.06, 2.13), (0.04, 0.04, 0.10), COL_CHROME)            # on the top rail
    make_cyl("Door_Sign_String", (dx, Y0 + 0.07, 1.96), 0.003, 0.24, COL_BLACK, segments=4)
    make_box("Door_Sign_Closed", (dx, Y0 + 0.07, 1.72), (0.36, 0.01, 0.24), (0.86, 0.20, 0.16, 1.0))   # it reads CLOSED inside: the shop is open
    make_box("Door_Sign_Closed_Text", (dx, Y0 + 0.076, 1.72), (0.26, 0.002, 0.07), COL_PAPER)
    make_box("DoorBell_Arm", (dx + 0.30, Y0 + 0.16, 2.40), (0.03, 0.14, 0.03), COL_CHROME)
    make_cyl("DoorBell", (dx + 0.30, Y0 + 0.24, 2.34), 0.05, 0.07, (0.82, 0.72, 0.42, 1.0), segments=10)
    make_box("Door_Mat", (dx, 0.75, 0.005), (1.20, 0.80, 0.01), (0.24, 0.20, 0.18, 1.0))
    # the pressed-tin ceiling: a plane and its panel ribs
    make_box("Ceil_Tin", (0.0, (Y0 + Y1) / 2.0, CEIL + 0.05), (X1 - X0 + 0.4, Y1 - Y0 + 0.4, 0.10), COL_TIN)
    for k in range(1, 20):
        make_box(f"Ceil_Tin_Rib_X_{k}", (X0 + k * 0.60, (Y0 + Y1) / 2.0, CEIL - 0.01), (0.03, Y1 - Y0, 0.02), (0.76, 0.72, 0.60, 1.0))
    for k in range(1, 17):
        make_box(f"Ceil_Tin_Rib_Y_{k}", (0.0, Y0 + k * 0.60, CEIL - 0.008), (X1 - X0, 0.03, 0.016), (0.76, 0.72, 0.60, 1.0))
    make_smoke_detector("Smoke", (-1.5, 5.0, CEIL))


def build_hall():
    """The back hall: the restroom, the hot-water tank, the back door to the alley."""
    pal = {"wall": (0.80, 0.78, 0.72, 1.0), "baseboard": (0.30, 0.22, 0.16, 1.0)}
    make_wall("Hall_Wall_E", (HALL_X1, (Y1 + HALL_Y1) / 2.0, 0), length=HALL_Y1 - Y1, height=CEIL, axis='Y', palette=pal, baseboard_face_sign=-1)
    make_wall_with_openings("Hall_Wall_N", ((X0 + HALL_X1) / 2.0, HALL_Y1, 0), length=HALL_X1 - X0 + 0.2, height=CEIL, axis='X',
                            palette=pal, baseboard_face_sign=-1, openings=[(-3.2, 1.05, 1.00, 2.10)])
    make_box("Hall_Ceil", ((X0 + HALL_X1) / 2.0, (Y1 + HALL_Y1) / 2.0, 2.75), (HALL_X1 - X0, HALL_Y1 - Y1 - 0.2, 0.10), (0.84, 0.84, 0.80, 1.0))
    make_fluorescent_tube_fixture("Hall_Fluor", (-3.2, 11.3, 2.70), length=1.2, width=0.30)
    # the back door (closed), its push bar and the EXIT sign
    make_box("Back_Door", (-3.2, HALL_Y1, 1.04), (0.94, 0.05, 2.08), (0.36, 0.30, 0.24, 1.0))
    make_box("Back_Door_Bar", (-3.2, HALL_Y1 - 0.06, 1.02), (0.70, 0.06, 0.06), COL_STEEL)
    make_box("Back_Door_Window", (-3.2, HALL_Y1 - 0.028, 1.65), (0.24, 0.006, 0.40), (0.30, 0.34, 0.38, 1.0))
    make_box("Exit_Sign", (-3.2, HALL_Y1 - 0.13, 2.35), (0.36, 0.06, 0.18), (0.90, 0.20, 0.16, 1.0))
    # the restroom door on the hall's W end, with its sign
    make_box("Restroom_Door", (X0 + 0.12, 11.3, 1.04), (0.04, 0.90, 2.08), (0.70, 0.62, 0.50, 1.0))
    make_box("Restroom_Door_Knob", (X0 + 0.16, 11.65, 1.00), (0.04, 0.05, 0.05), COL_CHROME)
    make_box("Restroom_Sign", (X0 + 0.142, 11.3, 1.62), (0.004, 0.18, 0.18), (0.20, 0.36, 0.56, 1.0))
    # the hot-water tank the heat pump feeds, the mop sink, the supply shelf
    make_cyl("HeatPump_Tank", (-0.82, 12.05, 0.82), 0.32, 1.64, (0.86, 0.86, 0.84, 1.0), segments=14)
    make_cyl("HeatPump_Tank_Line_0", (-0.68, 12.05, 2.20), 0.018, 1.12, COL_COPPER, segments=6)
    make_cyl("HeatPump_Tank_Line_1", (-0.96, 12.05, 2.20), 0.018, 1.12, COL_COPPER, segments=6)
    make_box("Mop_Sink", (-5.5, 12.15, 0.25), (0.60, 0.70, 0.50), (0.80, 0.80, 0.78, 1.0))
    make_box("Supply_Shelf", (-1.70, 12.35, 1.00), (1.00, 0.36, 0.03), COL_STEEL)
    make_box("Supply_Shelf_Post_L", (-2.18, 12.35, 0.50), (0.03, 0.36, 1.00), COL_STEEL)
    make_box("Supply_Shelf_Post_R", (-1.22, 12.35, 0.50), (0.03, 0.36, 1.00), COL_STEEL)
    for k in range(4):
        make_box(f"Supply_Box_{k}", (-2.07 + k * 0.24, 12.35, 1.14), (0.22, 0.30, 0.25), (0.78, 0.66, 0.48, 1.0))


# ══════════════════════════════════════════════════════════════ the bar
TOP = 1.02          # the front counter's top face
BB_TOP = 0.94       # the back bar's top face


def build_counter():
    cy = 8.0
    # the counter body E of the pastry case, clad in fir boards, under the soapstone top
    make_box("Counter_Body", (3.4, cy, 0.49), (5.0, 0.60, 0.98), COL_FIR_DK)
    make_box("Counter_Top", (3.40, cy, TOP - 0.02), (5.0, 0.76, 0.04), COL_TOP)   # E of the pastry case
    for k in range(33):
        make_box(f"Counter_Board_{k}", (0.98 + k * 0.15, cy - 0.305, 0.49), (0.13, 0.01, 0.94),
                 COL_FIR if k % 3 else (0.54, 0.40, 0.28, 1.0))
    make_box("Counter_Kick", (3.4, cy - 0.29, 0.04), (5.0, 0.04, 0.08), COL_BLACK)
    # the pastry case: a fir base, a glass box, Hans's bread and pastries on two decks
    px0, px1 = -0.6, 0.9
    pcx = (px0 + px1) / 2.0
    make_box("Pastry_Case_Base", (pcx, cy, 0.40), (px1 - px0, 0.60, 0.80), COL_FIR_DK)
    make_box("Pastry_Case_Deck", (pcx, cy, 0.82), (px1 - px0, 0.60, 0.04), COL_WOOD)
    for e, ex in enumerate((px0 + 0.02, px1 - 0.02)):
        make_box(f"Pastry_Case_End_{e}", (ex, cy, 1.13), (0.04, 0.60, 0.58), COL_WOOD)
    make_box("Pastry_Case_Glass_Front", (pcx, cy - 0.29, 1.13), (px1 - px0 - 0.08, 0.01, 0.58), COL_GLASS)
    make_box("Pastry_Case_Glass_Top", (pcx, cy, 1.425), (px1 - px0 - 0.08, 0.60, 0.01), COL_GLASS)
    make_box("Pastry_Case_Shelf", (pcx, cy + 0.06, 1.12), (px1 - px0 - 0.08, 0.40, 0.02), COL_GLASS)
    for k in range(5):                                       # croissants on the lower deck
        make_cyl(f"Pastry_Croissant_{k}", (px0 + 0.22 + k * 0.25, cy - 0.10, 0.87), 0.035, 0.14, (0.86, 0.60, 0.28, 1.0), segments=8, axis='X')
    for k in range(3):                                       # Hans's loaves on the lower deck behind
        make_cyl(f"Pastry_Loaf_{k}", (px0 + 0.30 + k * 0.45, cy + 0.15, 0.90), 0.06, 0.30, (0.66, 0.42, 0.20, 1.0), segments=10, axis='X')
    for k in range(6):                                       # muffins and scones on the shelf
        if k % 2:
            make_cyl(f"Pastry_Muffin_{k}", (px0 + 0.20 + k * 0.21, cy + 0.02, 1.16), 0.04, 0.06, (0.52, 0.32, 0.18, 1.0), segments=8)
        else:
            make_box(f"Pastry_Scone_{k}", (px0 + 0.20 + k * 0.21, cy + 0.02, 1.155), (0.09, 0.09, 0.05), (0.84, 0.66, 0.40, 1.0))
    # the register: the tablet on its stand, the token reader, the tip jar with its tokens
    rx = 1.55
    make_box("Register_Stand", (rx, cy + 0.10, TOP + 0.08), (0.06, 0.06, 0.16), COL_BLACK)
    make_rot_box("Register_Tablet", (rx, cy + 0.10, TOP + 0.26), (0.26, 0.02, 0.19), COL_BLACK, pitch=0.0, roll=0.0)
    make_box("Register_Tablet_Screen", (rx, cy + 0.111, TOP + 0.26), (0.23, 0.002, 0.16), (0.40, 0.56, 0.62, 1.0))
    make_box("Register_Stand_Foot", (rx, cy + 0.10, TOP + 0.005), (0.16, 0.12, 0.01), COL_BLACK)
    make_cyl("Token_Reader", (rx - 0.30, cy - 0.20, TOP + 0.015), 0.05, 0.03, (0.24, 0.24, 0.26, 1.0), segments=10)
    make_cyl("Token_Reader_Ring", (rx - 0.30, cy - 0.20, TOP + 0.031), 0.035, 0.002, (0.40, 0.70, 0.62, 1.0), segments=10)
    make_cyl("Tip_Jar", (rx + 0.32, cy - 0.20, TOP + 0.08), 0.055, 0.16, COL_GLASS, segments=10)
    for k in range(6):
        make_cyl(f"Tip_Jar_Token_{k}", (rx + 0.32 + 0.02 * ((k % 3) - 1), cy - 0.20 + 0.015 * (k % 2), TOP + 0.006 + k * 0.004),
                 0.012, 0.004, (0.72, 0.62, 0.30, 1.0), segments=8)
    # the machine: a two-group, its face to the barista (N), its back to the room
    mx, my = 3.1, 7.95
    make_box("Espresso_Body", (mx, my, TOP + 0.23), (0.95, 0.55, 0.42), COL_CHROME)
    make_box("Espresso_Top", (mx, my, TOP + 0.46), (0.95, 0.55, 0.04), (0.30, 0.22, 0.14, 1.0))
    make_box("Espresso_Badge", (mx, my - 0.279, TOP + 0.30), (0.30, 0.006, 0.08), (0.30, 0.22, 0.14, 1.0))
    make_box("Espresso_Drip_Tray", (mx, my + 0.34, TOP + 0.02), (0.88, 0.14, 0.04), COL_STEEL)
    for g, gx in enumerate((mx - 0.24, mx + 0.24)):
        make_cyl(f"Espresso_Group_{g}", (gx, my + 0.30, TOP + 0.30), 0.05, 0.06, COL_CHROME, segments=10, axis='Y')
        make_cyl(f"Espresso_Portafilter_{g}", (gx, my + 0.31, TOP + 0.23), 0.04, 0.04, COL_STEEL, segments=10)
        make_box(f"Espresso_Portafilter_{g}_Handle", (gx, my + 0.42, TOP + 0.23), (0.03, 0.18, 0.03), COL_BLACK)
        make_cyl(f"Espresso_Gauge_{g}", (gx, my + 0.278, TOP + 0.40), 0.03, 0.006, COL_PAPER, segments=10, axis='Y')
    for s, sx in enumerate((mx - 0.44, mx + 0.44)):
        make_cyl(f"Espresso_Wand_{s}", (sx, my + 0.29, TOP + 0.24), 0.007, 0.22, COL_CHROME, segments=6)
    for k in range(6):                                           # cups warming on top
        make_cyl(f"Espresso_Warm_Cup_{k}", (mx - 0.35 + k * 0.14, my + 0.05, TOP + 0.52), 0.035, 0.07, COL_CERAMIC, segments=8)
    # "the ceramic milk pitchers ... in the order the morning regulars liked their drinks pulled"
    for k in range(5):
        col = ((0.92, 0.90, 0.84, 1.0), (0.30, 0.44, 0.58, 1.0), (0.92, 0.90, 0.84, 1.0), (0.72, 0.52, 0.34, 1.0), (0.92, 0.90, 0.84, 1.0))[k]
        make_lathe(f"Milk_Pitcher_{k}", (2.10 + k * 0.10, cy + 0.24, TOP), [(0.0, 0.0), (0.038, 0.0), (0.040, 0.06), (0.034, 0.11), (0.036, 0.13), (0.0, 0.13)],
                   col, segments=10)
    # the grinder and the knock box
    make_box("Grinder_Body", (3.95, cy + 0.05, TOP + 0.20), (0.20, 0.26, 0.40), COL_BLACK)
    make_lathe("Grinder_Hopper", (3.95, cy + 0.05, TOP + 0.40), [(0.0, 0.0), (0.04, 0.0), (0.09, 0.16), (0.0, 0.16)], (0.70, 0.74, 0.76, 1.0), segments=10)
    make_cyl("Grinder_Beans", (3.95, cy + 0.05, TOP + 0.50), 0.065, 0.05, (0.24, 0.14, 0.08, 1.0), segments=10)
    make_box("Knock_Box", (4.30, cy + 0.22, TOP + 0.06), (0.16, 0.16, 0.12), COL_BLACK)
    # the hand-off: PICK UP, a lid stack, Wren's hot chocolate with its single marshmallow
    make_box("Pickup_Plank", (5.05, cy - 0.10, TOP + 0.02), (0.80, 0.40, 0.04), COL_FIR)
    make_box("Pickup_Sign", (5.05, cy + 0.08, TOP + 0.14), (0.40, 0.02, 0.20), COL_CHALK)       # standing on the plank
    make_box("Pickup_Sign_Text", (5.05, cy + 0.068, TOP + 0.15), (0.28, 0.002, 0.06), COL_PAPER)
    make_lathe("Wren_Hot_Chocolate", (4.85, cy - 0.16, TOP + 0.04), [(0.0, 0.0), (0.04, 0.0), (0.045, 0.09), (0.0, 0.09)], (0.30, 0.44, 0.58, 1.0), segments=10)
    make_cyl("Wren_Hot_Chocolate_Top", (4.85, cy - 0.16, TOP + 0.124), 0.040, 0.004, (0.42, 0.26, 0.16, 1.0), segments=10)
    make_box("Marshmallow", (4.86, cy - 0.155, TOP + 0.137), (0.022, 0.022, 0.022), (0.98, 0.97, 0.94, 1.0))
    make_cyl("Lid_Stack", (5.35, cy - 0.12, TOP + 0.02), 0.045, 0.04, COL_PAPER, segments=8)
    make_cyl("Cup_Stack", (5.35, cy + 0.10, TOP + 0.14), 0.045, 0.24, COL_PAPER, segments=8)
    # the under-counter milk cooler on the barista's side
    make_box("Milk_Cooler_Door", (2.30, cy + 0.31, 0.46), (0.60, 0.02, 0.70), (0.66, 0.70, 0.72, 1.0))
    make_box("Milk_Cooler_Handle", (2.30, cy + 0.33, 0.76), (0.40, 0.02, 0.03), COL_CHROME)
    # the gate at the counter's W end
    make_box("Counter_Gate", (px0 - 0.03, 8.83, 0.50), (0.04, 0.88, 1.00), COL_FIR_DK)
    make_box("Counter_Gate_Post", (px0 - 0.03, 9.29, 0.50), (0.06, 0.06, 1.00), COL_WOOD)


def build_back_bar():
    bx0, bx1 = HALL_X1, X1 - 0.10
    bcx = (bx0 + bx1) / 2.0
    by = Y1 - 0.10 - 0.30
    make_box("Back_Bar_Base", (bcx, by, (BB_TOP - 0.04) / 2.0), (bx1 - bx0, 0.60, BB_TOP - 0.04), COL_FIR_DK)
    make_box("Back_Bar_Top", (bcx, by, BB_TOP - 0.02), (bx1 - bx0, 0.62, 0.04), COL_TOP)
    n = 10
    for k in range(n):
        w = (bx1 - bx0) / n
        make_box(f"Back_Bar_Door_{k}", (bx0 + (k + 0.5) * w, by - 0.305, 0.46), (w - 0.03, 0.01, 0.76), COL_FIR)
    t = BB_TOP
    # the sink and its faucet
    make_box("Back_Bar_Sink", (0.15, by, t - 0.005), (0.50, 0.40, 0.01), COL_STEEL)
    make_cyl("Back_Bar_Faucet", (0.15, by + 0.22, t + 0.15), 0.012, 0.30, COL_CHROME, segments=6)
    make_box("Back_Bar_Faucet_Spout", (0.15, by + 0.12, t + 0.29), (0.02, 0.20, 0.02), COL_CHROME)
    # the pour-over station: a stand with three cones, the gooseneck kettle
    make_box("PourOver_Stand", (1.30, by, t + 0.12), (0.62, 0.20, 0.03), COL_WOOD)
    for e in (-1, 1):
        make_box(f"PourOver_Stand_Leg_{e:+d}", (1.30 + e * 0.29, by, t + 0.06), (0.03, 0.20, 0.12), COL_WOOD)
    for k in range(3):
        make_lathe(f"PourOver_Cone_{k}", (1.10 + k * 0.20, by, t + 0.135), [(0.0, 0.0), (0.025, 0.0), (0.06, 0.09), (0.0, 0.09)], COL_CERAMIC, segments=10)
    make_cyl("Kettle_Body", (1.85, by - 0.05, t + 0.07), 0.07, 0.14, COL_BLACK, segments=10)
    make_rot_box("Kettle_Spout", (1.95, by - 0.05, t + 0.15), (0.16, 0.012, 0.012), COL_BLACK, pitch=0.0, roll=0.0)
    # the hot-water tower and the decaf grinder
    make_box("HotWater_Dispenser", (2.45, by + 0.05, t + 0.25), (0.28, 0.30, 0.50), COL_CHROME)
    make_box("HotWater_Dispenser_Spout", (2.45, by - 0.12, t + 0.30), (0.03, 0.06, 0.03), COL_BLACK)
    make_box("Decaf_Grinder", (3.05, by + 0.05, t + 0.18), (0.18, 0.24, 0.36), (0.50, 0.30, 0.20, 1.0))
    make_lathe("Decaf_Grinder_Hopper", (3.05, by + 0.05, t + 0.36), [(0.0, 0.0), (0.04, 0.0), (0.08, 0.14), (0.0, 0.14)], (0.70, 0.74, 0.76, 1.0), segments=10)
    # the cups, the bags of beans, the batch brewer and its airpots
    for s in range(3):
        for h in range(4):
            make_cyl(f"Cup_Column_{s}_{h}", (3.60 + s * 0.12, by - 0.05, t + 0.035 + h * 0.07), 0.045, 0.07, COL_CERAMIC, segments=8)
    for k in range(3):
        make_box(f"Beans_Bag_{k}", (4.30 + k * 0.18, by + 0.10, t + 0.14), (0.15, 0.10, 0.28),
                 ((0.62, 0.48, 0.30, 1.0), (0.22, 0.30, 0.26, 1.0), (0.62, 0.48, 0.30, 1.0))[k])
        make_box(f"Beans_Bag_{k}_Label", (4.30 + k * 0.18, by + 0.049, t + 0.14), (0.10, 0.002, 0.08), COL_PAPER)
    make_box("Batch_Brewer", (5.30, by + 0.05, t + 0.30), (0.40, 0.36, 0.60), COL_CHROME)
    for k in range(2):
        make_cyl(f"Airpot_{k}", (5.15 + k * 0.30, by - 0.18, t + 0.17), 0.065, 0.34, COL_BLACK, segments=10)
    # the open shelves of mugs and jars, on their brackets
    face = Y1 - 0.10
    for s, z in enumerate((1.55, 1.95)):
        make_box(f"Shelf_{s}", (2.70, face - 0.14, z), (5.80, 0.28, 0.04), COL_WOOD)
        for b in range(5):
            make_box(f"Shelf_{s}_Bracket_{b}", (0.0 + b * 1.4, face - 0.07, z - 0.08), (0.03, 0.14, 0.12), COL_BLACK)
        for k in range(16):
            if (k + s) % 5 == 4:
                make_cyl(f"Shelf_{s}_Jar_{k}", (0.10 + k * 0.35, face - 0.14, z + 0.13), 0.06, 0.22, (0.40, 0.26, 0.16, 1.0), segments=8)
            else:
                make_cyl(f"Shelf_{s}_Mug_{k}", (0.10 + k * 0.35, face - 0.14, z + 0.07), 0.045, 0.10,
                         (COL_CERAMIC, (0.30, 0.44, 0.58, 1.0), (0.72, 0.52, 0.34, 1.0))[(k + s) % 3], segments=8)
    for k in range(3):                       # the pothos trailing off the top shelf
        make_cyl(f"Shelf_1_Pothos_{k}_Pot", (0.80 + k * 2.2, face - 0.14, 2.06), 0.07, 0.18, (0.70, 0.46, 0.32, 1.0), segments=8)
        make_box(f"Shelf_1_Pothos_{k}_Vine", (0.80 + k * 2.2, face - 0.27, 1.85), (0.10, 0.02, 0.46), (0.28, 0.46, 0.24, 1.0))
    # the chalkboard menu over the shelves
    make_box("Menu_Board_Frame", (2.70, face - 0.02, 2.75), (3.80, 0.04, 1.00), COL_WOOD)
    make_box("Menu_Board", (2.70, face - 0.045, 2.75), (3.60, 0.01, 0.86), COL_CHALK)
    chalk = ((0.88, 0.86, 0.80, 1.0), (0.72, 0.84, 0.74, 1.0), (0.90, 0.80, 0.62, 1.0))
    make_box("Menu_Board_Title", (2.70, face - 0.051, 3.08), (1.40, 0.002, 0.10), chalk[0])
    for col in range(2):
        for r in range(5):
            make_box(f"Menu_Board_Row_{col}_{r}", (1.55 + col * 1.85, face - 0.051, 2.90 - r * 0.13), (1.10, 0.002, 0.035), chalk[(r + col) % 3])
            make_box(f"Menu_Board_Price_{col}_{r}", (2.30 + col * 1.85, face - 0.051, 2.90 - r * 0.13), (0.20, 0.002, 0.035), chalk[2])
    # the copper hot-water lines down from the heat pump, in their foam
    for k, lx in enumerate((5.62, 5.74)):
        make_cyl(f"HeatPump_Line_{k}", (lx, face - 0.04, (BB_TOP + CEIL) / 2.0), 0.022, CEIL - BB_TOP, (0.20, 0.20, 0.22, 1.0), segments=6)
        make_cyl(f"HeatPump_Line_{k}_Copper", (lx, face - 0.04, BB_TOP + 0.10), 0.016, 0.20, COL_COPPER, segments=6)


# ═══════════════════════════════════════════════════════════ the seating
def _round_table(prefix, tx, ty, chairs=((-1, 0), (1, 0))):
    make_cyl(f"{prefix}_Top", (tx, ty, 0.74), 0.36, 0.04, COL_WOOD, segments=16)
    make_cyl(f"{prefix}_Pedestal", (tx, ty, 0.37), 0.04, 0.70, COL_BLACK, segments=8)
    make_cyl(f"{prefix}_Foot", (tx, ty, 0.02), 0.24, 0.04, COL_BLACK, segments=12)
    for ci, (sx, sy) in enumerate(chairs):
        yaw = {(-1, 0): -math.pi / 2.0, (1, 0): math.pi / 2.0, (0, -1): 0.0, (0, 1): math.pi}[(sx, sy)]
        make_chair(f"{prefix}_Chair_{ci}", tx + sx * 0.60, ty + sy * 0.60, yaw=yaw, wood=COL_WOOD, w=0.42)


def _square_table(prefix, tx, ty, s=0.60, top_col=COL_WOOD):
    make_box(f"{prefix}_Top", (tx, ty, 0.74), (s, s, 0.04), top_col)
    for i, (lx, ly) in enumerate(((-1, -1), (1, -1), (-1, 1), (1, 1))):
        make_box(f"{prefix}_Leg_{i}", (tx + lx * (s / 2.0 - 0.04), ty + ly * (s / 2.0 - 0.04), 0.36), (0.04, 0.04, 0.72), COL_BLACK)


def build_corner_table():
    """THE CORNER TABLE, SW, where the two window walls meet: four chairs."""
    tx, ty = -4.85, 1.40
    _square_table("CornerTable", tx, ty, s=0.90)
    make_chair("CornerTable_Chair_S", tx, ty - 0.62, yaw=0.0, wood=COL_WOOD, w=0.42)
    make_chair("CornerTable_Chair_N", tx, ty + 0.62, yaw=math.pi, wood=COL_WOOD, w=0.42)          # "the fourth chair"
    make_chair("CornerTable_Chair_W", tx - 0.62, ty, yaw=-math.pi / 2.0, wood=COL_WOOD, w=0.42)   # Kai's, back to the side window
    make_chair("CornerTable_Chair_E", tx + 0.62, ty, yaw=math.pi / 2.0, wood=COL_WOOD, w=0.42)    # Tem's, across from him
    t = 0.76
    # Kai's laptop (open) and his phone beside it
    make_box("Kai_Laptop_Base", (tx - 0.22, ty - 0.05, t + 0.009), (0.32, 0.22, 0.018), (0.60, 0.62, 0.64, 1.0))
    # hinged on the far (E) edge, the display facing Kai in the W chair
    make_box("Kai_Laptop_Screen", (tx - 0.066, ty - 0.05, t + 0.12), (0.012, 0.32, 0.21), (0.60, 0.62, 0.64, 1.0))
    make_box("Kai_Laptop_Display", (tx - 0.073, ty - 0.05, t + 0.12), (0.002, 0.29, 0.18), (0.40, 0.56, 0.70, 1.0))
    make_box("Kais_Phone", (tx - 0.25, ty + 0.22, t + 0.0055), (0.070, 0.140, 0.011), (0.13, 0.13, 0.15, 1.0))
    # the Frequency paperback, Wren's notebook
    make_box("Frequency_Book", (tx + 0.12, ty + 0.30, t + 0.010), (0.130, 0.200, 0.020), (0.62, 0.50, 0.36, 1.0))
    make_cyl("Frequency_Book_Dial", (tx + 0.12, ty + 0.30, t + 0.0215), 0.035, 0.002, (0.28, 0.28, 0.30, 1.0), segments=10)
    make_box("Wrens_Notebook", (tx + 0.30, ty + 0.20, t + 0.005), (0.110, 0.150, 0.010), (0.30, 0.44, 0.58, 1.0))
    make_box("Wrens_Notebook_Wire", (tx + 0.361, ty + 0.20, t + 0.006), (0.010, 0.150, 0.012), (0.55, 0.56, 0.58, 1.0))
    # the coffees: Kai's, and the one Lena set in front of Tem
    make_lathe("CornerTable_Cup_Kai", (tx - 0.15, ty - 0.30, t), [(0.0, 0.0), (0.04, 0.0), (0.045, 0.09), (0.0, 0.09)], COL_CERAMIC, segments=10)
    make_lathe("CornerTable_Cup_Tem", (tx + 0.28, ty - 0.10, t), [(0.0, 0.0), (0.04, 0.0), (0.045, 0.09), (0.0, 0.09)], (0.30, 0.44, 0.58, 1.0), segments=10)
    # Finn's duffel on the floor by the fourth chair
    make_box("Duffel", (tx + 0.65, ty + 1.05, 0.15), (0.55, 0.28, 0.30), (0.36, 0.40, 0.34, 1.0))
    make_box("Duffel_Strap", (tx + 0.65, ty + 1.05, 0.312), (0.42, 0.06, 0.024), (0.26, 0.28, 0.24, 1.0))
    # the pendant over it
    _pendant("Pendant_Corner", tx, ty, 2.30)


def build_seating():
    # the window bar on Main: a fir ledge on two steel legs, three stools
    make_box("Window_Bar_Top", (-2.35, 0.36, 1.04), (3.10, 0.34, 0.04), COL_FIR)
    for k, lx in enumerate((-3.80, -0.90)):
        make_box(f"Window_Bar_Leg_{k}", (lx, 0.36, 0.51), (0.05, 0.05, 1.02), COL_BLACK)
    for k, sx in enumerate((-3.30, -2.35, -1.40)):
        make_stool(f"Window_Bar_Stool_{k}", sx, 0.88, h=0.76, wood=COL_WOOD)
    make_lathe("Window_Bar_Cup", (-2.95, 0.40, 1.06), [(0.0, 0.0), (0.04, 0.0), (0.045, 0.09), (0.0, 0.09)], COL_CERAMIC, segments=10)
    # the two two-tops along the side windows
    for k, ty in enumerate((3.55, 5.55)):
        _square_table(f"SideTable_{k}", -5.30, ty)
        make_chair(f"SideTable_{k}_Chair_S", -5.30, ty - 0.55, yaw=0.0, wood=COL_WOOD, w=0.42)
        make_chair(f"SideTable_{k}_Chair_N", -5.30, ty + 0.55, yaw=math.pi, wood=COL_WOOD, w=0.42)
    # five round tables in the room
    for k, (tx, ty) in enumerate(((-2.60, 3.00), (-0.20, 3.00), (-2.60, 5.40), (-0.20, 5.40), (1.60, 4.20))):
        _round_table(f"Table_{k}", tx, ty)
        _pendant(f"Pendant_Table_{k}", tx, ty, 2.45)
    make_lathe("Table_1_Cup", (-0.10, 3.05, 0.76), [(0.0, 0.0), (0.04, 0.0), (0.045, 0.09), (0.0, 0.09)], COL_CERAMIC, segments=10)
    make_box("Table_3_Newspaper", (-0.25, 5.35, 0.765), (0.30, 0.40, 0.01), (0.86, 0.84, 0.80, 1.0))
    # the banquette on the brick, three tables and their chairs
    make_box("Banquette_Seat", (5.62, 3.50, 0.22), (0.56, 4.20, 0.44), COL_COUCH)
    make_box("Banquette_Cushion", (5.60, 3.50, 0.47), (0.52, 4.16, 0.06), (0.46, 0.22, 0.20, 1.0))
    make_box("Banquette_Back", (5.80, 3.50, 0.75), (0.20, 4.20, 0.56), (0.46, 0.22, 0.20, 1.0))
    for k, ty in enumerate((2.00, 3.50, 5.00)):
        _square_table(f"BanqTable_{k}", 5.00, ty)
        make_chair(f"BanqTable_{k}_Chair", 4.38, ty, yaw=-math.pi / 2.0, wood=COL_WOOD, w=0.42)
    make_lathe("BanqTable_1_Cup", (5.05, 3.45, 0.76), [(0.0, 0.0), (0.04, 0.0), (0.045, 0.09), (0.0, 0.09)], (0.72, 0.52, 0.34, 1.0), segments=10)
    # LENA'S PAINTINGS on the brick over the banquette, a price card by each, the track over them
    rnd = random.Random(49)
    for k, (cy, w, h) in enumerate(((2.00, 0.90, 0.70), (3.50, 1.20, 0.90), (5.00, 0.80, 0.80))):
        make_box(f"Painting_{k}", (X1 - 0.12, cy, 1.95), (0.04, w, h), (0.90, 0.88, 0.82, 1.0))
        for m in range(5):
            make_box(f"Painting_{k}_Mark_{m}", (X1 - 0.141, cy + rnd.uniform(-w / 3, w / 3), 1.95 + rnd.uniform(-h / 3, h / 3)),
                     (0.002, rnd.uniform(0.10, w * 0.5), rnd.uniform(0.06, h * 0.4)),
                     ((0.20, 0.30, 0.46, 1.0), (0.70, 0.40, 0.20, 1.0), (0.16, 0.16, 0.18, 1.0), (0.46, 0.56, 0.48, 1.0), (0.84, 0.70, 0.40, 1.0))[(k + m) % 5])
        make_box(f"Painting_{k}_Card", (X1 - 0.103, cy + w / 2.0 + 0.12, 1.65), (0.006, 0.10, 0.07), COL_PAPER)
    make_box("Track_Rail", (5.10, 3.50, CEIL - 0.02), (0.05, 4.40, 0.04), COL_BLACK)
    for k, cy in enumerate((2.00, 3.50, 5.00)):
        make_cyl(f"Track_Head_{k}_Stem", (5.10, cy, CEIL - 0.09), 0.012, 0.10, COL_BLACK, segments=6)
        make_rot_box(f"Track_Head_{k}_Lamp", (5.16, cy, CEIL - 0.17), (0.14, 0.08, 0.08), COL_BLACK, pitch=0.0, roll=0.0)
    # the condiment station by the door, on the E wall
    make_box("Condiment_Cabinet", (5.62, 0.75, 0.45), (0.52, 0.80, 0.90), COL_FIR_DK)
    make_box("Condiment_Top", (5.62, 0.75, 0.92), (0.56, 0.84, 0.04), COL_TOP)
    make_box("Condiment_Napkins", (5.55, 0.48, 1.00), (0.16, 0.10, 0.12), COL_BLACK)
    make_box("Condiment_Sugar_Caddy", (5.55, 0.75, 0.98), (0.20, 0.10, 0.08), COL_CHROME)
    make_cyl("Condiment_Water_Jug", (5.62, 1.02, 1.09), 0.10, 0.30, COL_GLASS, segments=12)
    make_cyl("Condiment_Water_Jug_Lid", (5.62, 1.02, 1.25), 0.09, 0.02, COL_CHROME, segments=12)


def build_lounge():
    """The NW corner: the couch on the N wall, two armchairs, the low table,
    the book-swap shelf, the floor lamp, the rug, the community board."""
    make_box("Lounge_Rug", (-4.10, 8.25, 0.005), (3.20, 2.80, 0.01), (0.46, 0.30, 0.24, 1.0))
    cx, cy = -4.20, Y1 - 0.10 - 0.45
    make_box("Couch_Base", (cx, cy, 0.20), (2.00, 0.86, 0.40), COL_COUCH)
    make_box("Couch_Back", (cx, cy + 0.33, 0.62), (2.00, 0.20, 0.44), COL_COUCH)
    for e in (-1, 1):
        make_box(f"Couch_Arm_{e:+d}", (cx + e * 0.92, cy - 0.03, 0.55), (0.16, 0.80, 0.30), COL_COUCH)
    for k in range(2):
        make_box(f"Couch_SeatCush_{k}", (cx - 0.42 + k * 0.84, cy - 0.06, 0.46), (0.82, 0.64, 0.12), COL_CUSH)
        make_box(f"Couch_BackCush_{k}", (cx - 0.42 + k * 0.84, cy + 0.17, 0.70), (0.80, 0.14, 0.40), COL_CUSH)
    # the two armchairs, facing each other across the low table
    for k, (ax, sgn) in enumerate(((-5.35, +1), (-3.05, -1))):
        ay = 7.30
        make_box(f"Armchair_{k}_Base", (ax, ay, 0.20), (0.70, 0.74, 0.40), COL_COUCH)
        make_box(f"Armchair_{k}_Back", (ax - sgn * 0.28, ay, 0.66), (0.16, 0.74, 0.52), COL_COUCH)
        for e in (-1, 1):
            make_box(f"Armchair_{k}_Arm_{e:+d}", (ax, ay + e * 0.30, 0.52), (0.62, 0.14, 0.24), COL_COUCH)
        make_box(f"Armchair_{k}_Cush", (ax + sgn * 0.05, ay, 0.46), (0.52, 0.46, 0.12), COL_CUSH)
    make_box("Lounge_Table_Top", (-4.20, 7.70, 0.42), (0.90, 0.60, 0.04), COL_WOOD)
    for i, (lx, ly) in enumerate(((-0.40, -0.25), (0.40, -0.25), (-0.40, 0.25), (0.40, 0.25))):
        make_box(f"Lounge_Table_Leg_{i}", (-4.20 + lx, 7.70 + ly, 0.20), (0.04, 0.04, 0.40), COL_BLACK)
    make_box("Lounge_Board_Game", (-4.30, 7.65, 0.455), (0.36, 0.36, 0.03), (0.72, 0.30, 0.22, 1.0))
    # the book-swap shelf on the W wall N of the window, a carcass with its paperbacks
    sx, sy0, sy1 = X0 + 0.10 + 0.15, 7.95, 9.65
    scy = (sy0 + sy1) / 2.0
    for e, ey in enumerate((sy0, sy1)):
        make_box(f"BookSwap_Side_{e}", (sx, ey, 0.90), (0.30, 0.02, 1.80), COL_WOOD)
    make_box("BookSwap_Back", (X0 + 0.11, scy, 0.90), (0.02, sy1 - sy0, 1.80), COL_WOOD)
    make_box("BookSwap_Top", (sx, scy, 1.81), (0.30, sy1 - sy0, 0.02), COL_WOOD)
    rnd = random.Random(7)
    for s in range(4):
        z = 0.06 + s * 0.44
        make_box(f"BookSwap_Shelf_{s}", (sx, scy, z), (0.28, sy1 - sy0 - 0.03, 0.02), COL_WOOD)
        y = sy0 + 0.06
        b = 0
        while y < sy1 - 0.10:
            w = rnd.uniform(0.025, 0.045)
            h = rnd.uniform(0.17, 0.22)
            make_box(f"BookSwap_Book_{s}_{b}", (sx + 0.02, y + w / 2.0, z + 0.01 + h / 2.0), (0.13, w, h),
                     ((0.62, 0.20, 0.16, 1.0), (0.22, 0.34, 0.52, 1.0), (0.84, 0.78, 0.60, 1.0), (0.24, 0.42, 0.30, 1.0), (0.80, 0.56, 0.24, 1.0))[b % 5])
            y += w + 0.004
            b += 1
    make_box("BookSwap_Sign", (sx + 0.12, scy, 1.90), (0.02, 0.60, 0.16), COL_CHALK)   # standing on the top
    # the floor lamp in the corner
    make_cyl("Floor_Lamp_Base", (-5.55, 9.55, 0.02), 0.16, 0.04, COL_BLACK, segments=12)
    make_cyl("Floor_Lamp_Pole", (-5.55, 9.55, 0.80), 0.015, 1.52, COL_BLACK, segments=6)
    make_cyl("Floor_Lamp_Shade", (-5.55, 9.55, 1.60), 0.20, 0.26, (0.90, 0.80, 0.60, 1.0), segments=14)
    make_cyl("Floor_Lamp_Bulb", (-5.55, 9.55, 1.52), 0.04, 0.06, COL_BULB, segments=8)
    # the community board on the N wall by the hall door
    make_box("Community_Board", (-2.70, Y1 - 0.12, 1.75), (0.90, 0.04, 0.70), (0.70, 0.56, 0.38, 1.0))
    rnd = random.Random(12)
    for k in range(7):
        make_box(f"Community_Board_Flyer_{k}", (-3.05 + (k % 4) * 0.22, Y1 - 0.142, 1.92 - (k // 4) * 0.30),
                 (0.16, 0.004, 0.22), (COL_PAPER, (0.96, 0.86, 0.50, 1.0), (0.70, 0.84, 0.92, 1.0))[k % 3])
    make_floor_plant("Plant_Hall", (-2.70, 9.45, 0.0))
    make_floor_plant("Plant_Window", (-0.55, 0.55, 0.0))


def _pendant(prefix, x, y, bulb_z):
    """An exposed-bulb pendant: the canopy on the tin, the cord, the cage, the bulb."""
    make_cyl(f"{prefix}_Canopy", (x, y, CEIL - 0.02), 0.06, 0.04, COL_BLACK, segments=10)
    make_cyl(f"{prefix}_Cord", (x, y, (CEIL - 0.04 + bulb_z + 0.08) / 2.0), 0.006, CEIL - 0.04 - (bulb_z + 0.08), COL_BLACK, segments=4)
    make_cyl(f"{prefix}_Socket", (x, y, bulb_z + 0.06), 0.025, 0.05, (0.62, 0.48, 0.24, 1.0), segments=8)
    make_cyl(f"{prefix}_Bulb", (x, y, bulb_z), 0.045, 0.08, COL_BULB, segments=10)


def build_bar_pendants():
    for k, px in enumerate((1.0, 2.6, 4.2)):
        make_cyl(f"Pendant_Bar_{k}_Canopy", (px, 8.0, CEIL - 0.02), 0.07, 0.04, COL_BLACK, segments=10)
        make_cyl(f"Pendant_Bar_{k}_Cord", (px, 8.0, (CEIL - 0.04 + 2.66) / 2.0), 0.006, CEIL - 0.04 - 2.66, COL_BLACK, segments=4)
        make_lathe(f"Pendant_Bar_{k}_Shade", (px, 8.0, 2.46), [(0.0, 0.20), (0.04, 0.20), (0.18, 0.0), (0.0, 0.0)], (0.20, 0.34, 0.30, 1.0), segments=14)
        make_cyl(f"Pendant_Bar_{k}_Bulb", (px, 8.0, 2.50), 0.045, 0.08, COL_BULB, segments=10)


# ═══════════════════════════════════════════════════════════ the outside
def build_outside():
    make_view("View_S", "S", Y0, 0.0, kind="street", ground_z=0.0, seed=3)      # Main
    make_view("View_W", "W", X0, 6.0, kind="street", ground_z=0.0, span=12.0, seed=9)   # the cross street
    # "There is a tower on the hill that has been there longer than the town."
    make_box("Hill_Beyond", (-40.0, -72.0, 9.0), (70.0, 30.0, 18.0), (0.30, 0.36, 0.28, 1.0))
    make_cyl("Watch_Tower", (-36.0, -70.0, 25.0), 1.6, 14.0, (0.26, 0.24, 0.28, 1.0), segments=10)
    make_cyl("Watch_Tower_Cap", (-36.0, -70.0, 32.4), 2.0, 0.8, (0.22, 0.20, 0.24, 1.0), segments=10)


def main():
    clear_scene()
    build_shell()
    build_hall()
    build_counter()
    build_back_bar()
    build_bar_pendants()
    build_corner_table()
    build_seating()
    build_lounge()
    build_outside()
    out = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)),
        "../../../assets/3d/locales/daily_grind_interior.glb"))
    print(f"\n[build_daily_grind_interior] exporting to {out}")
    export_glb(out)


if __name__ == "__main__":
    main()
