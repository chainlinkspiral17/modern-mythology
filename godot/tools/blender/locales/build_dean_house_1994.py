"""dean_house_1994 — vol 2's chapter vii: the rented house up the Alsea where
"N. Dean" keeps his dream journal, March 1994, before dawn (draft 1,
2026-10-18).

The user: "go ahead and start working on backgrounds for vol 1-4 as needed."
"the Little Switzerland road, our house a white dot up the Alsea"; "the river
behind our house"; "the rented house". The bedroom is barely described; the
basement is where the work is:
  "Woke up at 3:50 with my jaw hurting."; "Furnace kicked on under the
   floor, same as every morning at four"; "the river was loud"
                                         → dean_bedroom_1994 (the bedroom
                                           sits over the furnace)
  "Went down to the basement in socks, didn't turn on the monitor."
  "Graph paper. Drew the town like the dream draws it, one road, buildings
   propped on nothing"; "Under it I wrote SCUMM, like on the side of the
   boxes those games come in"; "Wrote slow sticks across the top of the
   graph paper and underlined it twice like it was the name of a band."
  "Called Cale at quarter past four"; "Outside the window well it's raining
   in long lines that reach the ground"; "it's getting light enough to see
   the Hagstrom place across the pasture"
                                         → dean_basement_1994
Nothing later than early 1994: a beige desktop, a CRT left off, floppies, a
corded phone. The text names no brands and neither does the set. Whether
this house is the narrator's grandmother's ranch (small_wood_ranch) is the
author's call (Timeline / the brief's knot): it is built apart.

Blender: x east, y north, z up; Godot (x, z, -y). The ground floor at z 0
(the bedroom x 0..3.6, y 1.6..5); the basement under the whole house,
x -1..6, y -1..5, floor at z -2.5. The pasture runs north from the well and
climbs a hill to the Hagstrom place, so it reads from below grade.

DRAFT 2 targets: the rest of the ground floor (the kitchen, the hall to the
door); the house from outside, the white dot up the river; the river behind
it as a view; the graph paper as a real drawing (an image on the sheet).
"""
import os, sys, math
_BT = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
if _BT not in sys.path: sys.path.insert(0, _BT)
from _props.geometry import (clear_scene, make_box, make_cyl, make_chamfer_box, make_rot_box, make_blob, make_lathe,
                             join_stock, export_glb)
from _props.structure import make_floor, make_wall, make_wall_with_openings
from _props.furniture import make_bed, make_chair

H, T = 2.4, 0.16
PAL = {"wall": (0.80, 0.80, 0.76, 1.0), "baseboard": (0.42, 0.36, 0.30, 1.0)}
CONC = (0.52, 0.52, 0.50, 1.0); CONC_DARK = (0.42, 0.42, 0.40, 1.0)
BEIGE = (0.80, 0.76, 0.66, 1.0)
BZ = -2.5                                    # the basement floor
BED, BASE = "__dean_bedroom_1994", "__dean_basement_1994"
GRASS = (0.30, 0.38, 0.24, 1.0)


def build_bedroom():
    x0, x1, y0, y1 = 0.0, 3.6, 1.6, 5.0
    make_floor("Bedroom_Floor", ((x0 + x1) / 2.0, (y0 + y1) / 2.0, 0.0), size_x=x1 - x0, size_y=y1 - y0,
               palette={"vinyl": (0.50, 0.40, 0.30, 1.0), "seam": (0.42, 0.34, 0.26, 1.0)})
    make_box("Bedroom_Ceil", ((x0 + x1) / 2.0, (y0 + y1) / 2.0, H + 0.04), (x1 - x0 + 0.2, y1 - y0 + 0.2, 0.08), (0.86, 0.86, 0.84, 1.0))
    make_wall_with_openings("Bedroom_Wall_N", (1.8, y1, 0), length=3.6 + T, height=H, thickness=T, axis='X', palette=PAL,
                            baseboard_face_sign=-1, openings=[(1.8, 1.5, 1.0, 1.2)])
    make_wall_with_openings("Bedroom_Wall_S", (1.8, y0, 0), length=3.6 + T, height=H, thickness=T, axis='X', palette=PAL,
                            baseboard_face_sign=+1, openings=[(0.7, 1.0, 0.80, 2.0)])
    make_wall("Bedroom_Wall_W", (x0, (y0 + y1) / 2.0, 0), length=y1 - y0 - T, height=H, thickness=T, axis='Y', palette=PAL,
              baseboard_face_sign=+1)
    make_wall("Bedroom_Wall_E", (x1, (y0 + y1) / 2.0, 0), length=y1 - y0 - T, height=H, thickness=T, axis='Y', palette=PAL,
              baseboard_face_sign=-1)
    # the window's frame and sash (no glass: the rain is outside it)
    for s in (-1, 1):
        make_box(f"Bedroom_Window_Frame_Jamb_{s:+d}", (1.8 + s * 0.47, y1, 1.5), (0.06, T + 0.02, 1.2), (0.92, 0.92, 0.90, 1.0))
    for zz in (0.93, 1.5, 2.07):
        make_box(f"Bedroom_Window_Frame_Rail_{zz:.2f}", (1.8, y1, zz), (0.88, T + 0.02, 0.06), (0.92, 0.92, 0.90, 1.0))
    make_box("Bedroom_Window_Sill", (1.8, y1 - 0.12, 0.89), (1.10, 0.10, 0.03), (0.92, 0.92, 0.90, 1.0))
    # the bed along the E wall, head N, the sheets thrown back
    make_bed("Dean_Bed", x1 - T / 2.0 - 0.50, 3.9, head="+Y", w=0.95, d=1.95, made=False, blanket_col=(0.30, 0.34, 0.40, 1.0))
    make_rot_box("Dean_Bed_Sheet_Thrown", (x1 - T / 2.0 - 0.50 - 0.40, 3.4, 0.50), (0.30, 0.90, 0.10), (0.88, 0.88, 0.86, 1.0), pitch=0.5)
    # the register in the floor (the furnace below), a chair with clothes,
    # a dresser, the door
    make_box("Floor_Register_Grate", (1.2, 2.6, 0.003), (0.30, 0.14, 0.006), (0.30, 0.30, 0.30, 1.0))
    for k in range(5):
        make_box(f"Floor_Register_Slot_{k}", (1.08 + k * 0.06, 2.6, 0.0065), (0.02, 0.12, 0.001), (0.08, 0.08, 0.08, 1.0))
    make_chair("Bedroom_Chair", 0.55, 4.5, yaw=-math.pi / 2.0, wood=(0.40, 0.30, 0.22, 1.0))
    make_box("Bedroom_Chair_Clothes", (0.55, 4.5, 0.50), (0.40, 0.40, 0.08), (0.30, 0.34, 0.44, 1.0))
    make_box("Dresser", (x0 + T / 2.0 + 0.24, 3.4, 0.48), (0.48, 1.00, 0.96), (0.50, 0.38, 0.26, 1.0))
    make_box("Dresser_Top_Books", (x0 + T / 2.0 + 0.24, 3.2, 1.02), (0.24, 0.30, 0.12), (0.40, 0.24, 0.20, 1.0))
    make_box("Bedroom_Door_Open", (0.7 + 0.40, y0 + T / 2.0 + 0.42, 1.0), (0.04, 0.80, 2.0), (0.70, 0.62, 0.50, 1.0))
    make_box("Bedroom_Rug", (2.0, 3.0, 0.004), (1.4, 1.0, 0.008), (0.40, 0.30, 0.26, 1.0))


def build_ground_floor():
    """The rest of the ground floor: just its floor (with the stair hole)
    and its outer walls, so the bedroom door opens on a dark hall."""
    make_box("Hall_Floor_S", (2.5, 0.25, -0.02), (7.0, 2.5, 0.04), (0.46, 0.36, 0.26, 1.0))
    make_box("Hall_Floor_E", (5.75, 3.3, -0.02), (0.50, 3.4, 0.04), (0.46, 0.36, 0.26, 1.0))
    make_box("Hall_Floor_W", (-0.5, 3.3, -0.02), (1.0, 3.4, 0.04), (0.46, 0.36, 0.26, 1.0))
    make_wall("House_Wall_S", (2.5, -1.0, 0), length=7.0, height=H, thickness=T, axis='X', palette=PAL, baseboard_face_sign=+1)
    make_wall("House_Wall_W", (-1.0, 2.0, 0), length=6.0 - T, height=H, thickness=T, axis='Y', palette=PAL, baseboard_face_sign=+1)
    make_wall("House_Wall_E", (6.0, 2.0, 0), length=6.0 - T, height=H, thickness=T, axis='Y', palette=PAL, baseboard_face_sign=-1)


def build_basement():
    x0, x1, y0, y1 = -1.0, 6.0, -1.0, 5.0
    wt = 0.25
    make_box("Basement_Floor_Slab", ((x0 + x1) / 2.0, (y0 + y1) / 2.0, BZ - 0.05), (x1 - x0, y1 - y0, 0.10), CONC)
    # the walls (concrete, poured): the N wall holds the window well
    make_box("Basement_Wall_S", ((x0 + x1) / 2.0, y0 + wt / 2.0, BZ / 2.0), (x1 - x0, wt, -BZ), CONC_DARK)
    make_box("Basement_Wall_W", (x0 + wt / 2.0, (y0 + y1) / 2.0, BZ / 2.0), (wt, y1 - y0 - 2 * wt, -BZ), CONC_DARK)
    make_box("Basement_Wall_E", (x1 - wt / 2.0, (y0 + y1) / 2.0, BZ / 2.0), (wt, y1 - y0 - 2 * wt, -BZ), CONC_DARK)
    wx0, wx1, wz0, wz1 = 0.9, 2.3, -1.0, -0.15
    yn = y1 - wt / 2.0
    make_box("Basement_Wall_N_W", ((x0 + wx0) / 2.0, yn, BZ / 2.0), (wx0 - x0, wt, -BZ), CONC_DARK)
    make_box("Basement_Wall_N_E", ((wx1 + x1) / 2.0, yn, BZ / 2.0), (x1 - wx1, wt, -BZ), CONC_DARK)
    make_box("Basement_Wall_N_Below", ((wx0 + wx1) / 2.0, yn, (BZ + wz0) / 2.0), (wx1 - wx0, wt, wz0 - BZ), CONC_DARK)
    make_box("Basement_Wall_N_Above", ((wx0 + wx1) / 2.0, yn, wz1 / 2.0), (wx1 - wx0, wt, -wz1), CONC_DARK)
    for s in (-1, 1):
        make_box(f"Well_Window_Frame_Jamb_{s:+d}", ((wx0 + wx1) / 2.0 + s * ((wx1 - wx0) / 2.0 - 0.03), yn, (wz0 + wz1) / 2.0),
                 (0.06, wt + 0.02, wz1 - wz0), (0.70, 0.70, 0.68, 1.0))
    for zz in (wz0 + 0.03, wz1 - 0.03):
        make_box(f"Well_Window_Frame_Rail_{zz:.2f}", ((wx0 + wx1) / 2.0, yn, zz), (wx1 - wx0 - 0.12, wt + 0.02, 0.06), (0.70, 0.70, 0.68, 1.0))
    # the underside of the floor above: joists, the subfloor, the stair hole
    make_box("Basement_Ceil_Subfloor_W", (1.65, 2.0, -0.10), (5.3, 6.0, 0.08), (0.56, 0.46, 0.34, 1.0))
    make_box("Basement_Ceil_Subfloor_E", (5.75, 3.3, -0.10), (0.50, 3.4, 0.08), (0.56, 0.46, 0.34, 1.0))
    for k in range(12):
        make_box(f"Basement_Joist_{k}", (-0.7 + k * 0.40, 2.0, -0.24), (0.05, 6.0 - 2 * wt, 0.20), (0.50, 0.40, 0.28, 1.0))
    # the stair up (open treads against the E side)
    for k in range(10):
        make_box(f"Basement_Stair_Tread_{k}", (4.95, 1.4 - k * 0.24, BZ + 0.25 * (k + 1) - 0.02), (0.90, 0.26, 0.04), (0.50, 0.40, 0.28, 1.0))
    for s in (-1, 1):
        make_rot_box(f"Basement_Stair_Stringer_{s:+d}", (4.95 + s * 0.47, 0.30, BZ / 2.0 + 0.05), (0.05, 3.5, 0.26),
                     (0.46, 0.36, 0.24, 1.0), roll=-math.atan2(-BZ, 2.4))
    # the furnace (under the bedroom), its duct, the pilot; the water heater
    fx, fy = 3.0, 3.2
    make_box("Furnace", (fx, fy, BZ + 0.80), (0.80, 0.70, 1.60), (0.60, 0.58, 0.52, 1.0))
    make_box("Furnace_Plenum", (fx, fy, BZ + 1.85), (0.70, 0.60, 0.50), (0.66, 0.66, 0.64, 1.0))
    make_box("Furnace_Duct_Trunk", (fx - 1.4, fy, -0.44), (2.4, 0.40, 0.26), (0.70, 0.70, 0.68, 1.0))
    make_box("Furnace_Duct_Riser", (fx, fy, BZ + 2.22), (0.40, 0.40, 0.24), (0.70, 0.70, 0.68, 1.0))
    make_box("Furnace_Pilot_Glow", (fx, fy - 0.352, BZ + 0.30), (0.08, 0.004, 0.06), (1.0, 0.56, 0.20, 1.0))
    make_cyl("Water_Heater", (fx + 1.10, fy + 0.40, BZ + 0.75), 0.28, 1.50, (0.80, 0.78, 0.72, 1.0), segments=14)
    # the desk under the window: graph paper, the beige computer and the
    # CRT left off, floppies, the corded phone; a shelf of game boxes
    dx, dy = 1.6, y1 - wt - 0.36
    make_table("Basement_Desk", dx, dy, w=2.2, d=0.70, h=0.74, wood=(0.56, 0.46, 0.34, 1.0), z0=BZ)
    top = BZ + 0.74
    make_box("Graph_Paper", (dx - 0.30, dy - 0.10, top + 0.003), (0.22, 0.28, 0.004), (0.94, 0.96, 0.92, 1.0))
    for k in range(6):
        make_box(f"Graph_Paper_Grid_{k}", (dx - 0.40 + k * 0.04, dy - 0.10, top + 0.0055), (0.002, 0.27, 0.001), (0.60, 0.72, 0.80, 1.0))
    make_rot_box("Graph_Paper_Road", (dx - 0.30, dy - 0.12, top + 0.006), (0.18, 0.006, 0.001), (0.16, 0.16, 0.18, 1.0), yaw=0.2)
    for k in range(4):
        make_box(f"Graph_Paper_Building_{k}", (dx - 0.36 + k * 0.04, dy - 0.07, top + 0.006), (0.020, 0.030, 0.001), (0.16, 0.16, 0.18, 1.0))
    for k in range(8):
        a = k * 0.9
        make_box(f"Graph_Paper_Spiral_{k}", (dx - 0.24 + 0.01 * k * math.cos(a), dy - 0.18 + 0.01 * k * math.sin(a), top + 0.006),
                 (0.006, 0.006, 0.001), (0.16, 0.16, 0.18, 1.0))
    make_box("Graph_Paper_Title_Slow_Sticks", (dx - 0.30, dy + 0.01, top + 0.006), (0.14, 0.012, 0.001), (0.16, 0.16, 0.18, 1.0))
    for k in range(2):
        make_box(f"Graph_Paper_Underline_{k}", (dx - 0.30, dy - 0.005 - k * 0.008, top + 0.006), (0.15, 0.002, 0.001), (0.16, 0.16, 0.18, 1.0))
    make_box("Graph_Paper_Scumm_Word", (dx - 0.30, dy - 0.22, top + 0.006), (0.08, 0.010, 0.001), (0.16, 0.16, 0.18, 1.0))
    make_rot_box("Pencil", (dx - 0.12, dy - 0.18, top + 0.005), (0.16, 0.008, 0.008), (0.90, 0.76, 0.20, 1.0), yaw=0.5)
    make_box("Computer_Case", (dx + 0.55, dy + 0.04, top + 0.07), (0.44, 0.40, 0.14), BEIGE)
    make_box("Computer_Floppy_Slot", (dx + 0.55, dy + 0.04 - 0.201, top + 0.08), (0.12, 0.002, 0.01), (0.20, 0.20, 0.20, 1.0))
    make_chamfer_box("CRT_Monitor", (dx + 0.55, dy + 0.06, top + 0.14 + 0.19), (0.40, 0.40, 0.38), BEIGE, chamfer=0.03)
    make_box("CRT_Screen_Off", (dx + 0.55, dy + 0.06 - 0.202, top + 0.14 + 0.20), (0.32, 0.004, 0.26), (0.08, 0.09, 0.09, 1.0))
    make_box("Keyboard", (dx + 0.50, dy - 0.24, top + 0.015), (0.44, 0.16, 0.03), BEIGE)
    for k in range(3):
        make_box(f"Floppy_Disk_{k}", (dx + 0.92, dy - 0.10 + k * 0.012, top + 0.002 + k * 0.004), (0.09, 0.09, 0.003),
                 (0.12, 0.12, 0.14, 1.0))
    make_box("Phone_Base", (dx - 0.85, dy + 0.05, top + 0.035), (0.20, 0.22, 0.07), (0.84, 0.82, 0.76, 1.0))
    make_rot_box("Phone_Handset", (dx - 0.85, dy + 0.05, top + 0.085), (0.06, 0.22, 0.04), (0.84, 0.82, 0.76, 1.0), yaw=0.1)
    make_box("Phone_Cord", (dx - 0.72, dy - 0.04, top + 0.006), (0.12, 0.012, 0.012), (0.80, 0.78, 0.72, 1.0))
    make_box("Desk_Lamp_Base", (dx - 0.55, dy + 0.18, top + 0.015), (0.14, 0.14, 0.03), (0.20, 0.20, 0.22, 1.0))
    make_rot_box("Desk_Lamp_Arm", (dx - 0.55, dy + 0.12, top + 0.22), (0.02, 0.02, 0.40), (0.20, 0.20, 0.22, 1.0), roll=0.3)
    make_lathe("Desk_Lamp_Shade_Glow", (dx - 0.55, dy + 0.02, top + 0.36), [(0.0, 0.0), (0.08, 0.0), (0.05, 0.10), (0.0, 0.10)],
               (0.96, 0.88, 0.66, 1.0), segments=12)
    make_chair("Desk_Chair", dx, dy - 0.72, yaw=0.0, wood=(0.36, 0.30, 0.24, 1.0), z0=BZ)
    # the shelf of game boxes on the W wall, the socks-cold rug
    sx = x0 + wt + 0.18
    for lvl in range(3):
        make_box(f"Basement_Shelf_{lvl}", (sx, 2.4, BZ + 0.50 + lvl * 0.50), (0.36, 1.6, 0.03), (0.50, 0.42, 0.30, 1.0))
    for s in (-1, 1):
        make_box(f"Basement_Shelf_Upright_{s:+d}", (sx, 2.4 + s * 0.79, BZ + 0.80), (0.36, 0.03, 1.60), (0.46, 0.38, 0.26, 1.0))
    for k in range(10):
        lvl, i = k // 4, k % 4
        if lvl > 2:
            break
        make_box(f"Game_Box_{k}", (sx, 1.85 + i * 0.32, BZ + 0.515 + lvl * 0.50 + 0.15), (0.24, 0.06 + (k % 2) * 0.02, 0.30),
                 ((0.70, 0.30, 0.20, 1.0), (0.20, 0.36, 0.60, 1.0), (0.80, 0.70, 0.30, 1.0), (0.30, 0.50, 0.36, 1.0))[k % 4])
    make_box("Basement_Rug", (dx, dy - 0.8, BZ + 0.004), (1.6, 1.2, 0.008), (0.46, 0.30, 0.24, 1.0))


def build_outside():
    """North of the house: the window well, the rain, the pasture climbing
    a hill to the Hagstrom place; the river is sound only."""
    y1 = 5.0
    # the window well: its corrugated liner, gravel, the bank behind it
    wx0, wx1 = 0.9, 2.3
    make_box("Well_Gravel_Ground", ((wx0 + wx1) / 2.0, y1 + 0.55, -1.05), (wx1 - wx0 + 0.6, 0.90, 0.10), (0.50, 0.48, 0.44, 1.0))
    for k in range(7):
        a = math.pi * (k + 0.5) / 7.0
        cx = (wx0 + wx1) / 2.0 + 0.95 * math.cos(a)
        cy = y1 + 0.95 * math.sin(a) * 0.95
        make_rot_box(f"Well_Liner_Wall_{k}", (cx, cy, -0.50), (0.04, 0.46, 1.10), ((0.62, 0.62, 0.64, 1.0), (0.52, 0.52, 0.54, 1.0))[k % 2],
                     yaw=a)
    make_rot_box("Well_Bank_Ground", (1.6, y1 + 1.9, -0.45), (3.4, 1.8, 0.20), (0.36, 0.30, 0.24, 1.0), roll=0.50)
    # the yard and pasture north of the house, then the hill
    make_box("Yard_Ground_W", (-10.0, 10.0, -0.06), (20.0, 10.0 + 0.0, 0.12), GRASS)
    make_box("Yard_Ground_E", (14.0, 10.0, -0.06), (24.0, 10.0, 0.12), GRASS)
    make_box("Yard_Ground_N", (1.6, 12.0, -0.06), (8.0, 6.0, 0.12), GRASS)
    make_box("Yard_Ground_House", (2.5, -10.0, -0.06), (40.0, 18.0, 0.12), GRASS)
    th = 0.30
    top = 125.0 * math.tan(th)              # the hill's brow at y 140
    make_rot_box("Pasture_Hill_Ground", (1.6, 77.5, top / 2.0 - 0.5), (160.0, 125.0 / math.cos(th), 1.0), GRASS, roll=th)
    make_box("Hagstrom_Yard_Ground", (1.6, 162.0, top - 0.5), (160.0, 44.0, 1.0), GRASS)
    for k in range(9):
        y = 30.0 + k * 12.0
        make_box(f"Pasture_Fence_Post_{k}", (-14.0, y, (y - 15.0) * math.tan(th) + 0.6), (0.10, 0.10, 1.2), (0.40, 0.32, 0.24, 1.0))
    hy = 150.0
    hz = top
    make_box("Hagstrom_House", (6.0, hy, hz + 2.4), (9.0, 7.0, 5.0), (0.70, 0.68, 0.62, 1.0))
    make_box("Hagstrom_Roof", (6.0, hy, hz + 5.2), (9.6, 7.6, 0.6), (0.24, 0.22, 0.22, 1.0))
    make_box("Hagstrom_Barn", (-8.0, hy + 4.0, hz + 3.0), (7.0, 10.0, 6.0), (0.46, 0.24, 0.20, 1.0))
    for k in range(8):
        make_blob(f"Hill_Fir_{k}", (-30.0 + k * 9.0, 166.0 + (k % 3) * 5.0, top + 5.0), 3.0,
                  (0.14, 0.20, 0.14, 1.0), noise=0.3, seed=k, squash=2.0)
    # the rain in long lines that reach the ground (outside both windows)
    for k in range(14):
        make_box(f"Rain_Water_Streak_Bed_{k}", (1.2 + k * 0.09, y1 + 0.5 + (k % 3) * 0.3, 1.5 + (k % 2) * 0.3), (0.006, 0.006, 1.6),
                 (0.70, 0.74, 0.80, 1.0))
    for k in range(14):
        make_box(f"Rain_Water_Streak_Well_{k}", (0.9 + k * 0.10, y1 + 1.2 + (k % 3) * 0.4, 0.4), (0.006, 0.006, 1.4),
                 (0.70, 0.74, 0.80, 1.0))
    # the sky per hour: before dawn (bedroom), first light (basement)
    make_box("Sky_Predawn" + BED, (0.0, 186.0, 60.0), (500.0, 0.2, 240.0), (0.06, 0.08, 0.12, 1.0))
    make_box("Sky_First_Light" + BASE, (0.0, 186.0, 60.0), (500.0, 0.2, 240.0), (0.46, 0.50, 0.56, 1.0))


def main():
    clear_scene()
    build_bedroom()
    build_ground_floor()
    build_basement()
    build_outside()
    try:
        join_stock()
    except Exception as _e:
        print("[join_stock] skipped:", _e)
    out = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                        "../../../assets/3d/locales/dean_house_1994.glb"))
    print(f"\n[build_dean_house_1994] exporting to {out}")
    export_glb(out)


from _props.furniture import make_table  # noqa: E402  (kept beside its one use above)

if __name__ == "__main__":
    main()
