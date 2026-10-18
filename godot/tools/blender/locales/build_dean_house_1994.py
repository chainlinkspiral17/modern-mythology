"""dean_house_1994 — vol 2's chapter vii: the rented house up the Alsea where
"N. Dean" keeps his dream journal, March 1994, before dawn (draft 2,
2026-10-18).

The user: "go ahead and start working on backgrounds for vol 1-4 as needed."
Then (2026-10-18): "Dean's house can be the same layout, just dressed
different. There is the idea of two overlapping houses in the dreams. The
house is ten miles inland from the coast but 'on the coast'."
So the bedroom here is the narrator's bedroom of small_wood_ranch — the
same walls, window and door from `_props/small_wood_house.py` — dressed for
Dean's rented house in 1994: white walls gone grey, a thin curtain where the
other house has plank blinds, the register over the furnace, the sheets
thrown. Draft 1 (earlier the same day) had its own room; this replaces it.

"the Little Switzerland road, our house a white dot up the Alsea"; "the
river behind our house"; "the rented house".
  "Woke up at 3:50 with my jaw hurting."; "Furnace kicked on under the
   floor, same as every morning at four"; "the river was loud"
                                         → dean_bedroom_1994
  "Went down to the basement in socks, didn't turn on the monitor."
  "Graph paper. Drew the town like the dream draws it, one road, buildings
   propped on nothing"; "Under it I wrote SCUMM, like on the side of the
   boxes those games come in"; "Wrote slow sticks across the top of the
   graph paper and underlined it twice like it was the name of a band."
  "Called Cale at quarter past four"; "Outside the window well it's raining
   in long lines that reach the ground"; "it's getting light enough to see
   the Hagstrom place across the pasture"
                                         → dean_basement_1994 (the well sits
                                           under the bedroom's window)
Nothing later than early 1994: a beige desktop, a CRT left off, floppies, a
corded phone. No brands.

Blender: x east, y north, z up; Godot (x, z, -y). The bedroom is the shared
room (x -1.9..1.9, y 0..4.2); the hall S of it holds the stair down; the
basement runs under both, floor at z -2.5. The pasture climbs north to the
Hagstrom place so the well can see it.

DRAFT 3 targets: the rest of the ground floor on the shared plan (the
kitchen, the front door) so both houses are whole; the house from outside,
the white dot up the river; the river behind it; the graph paper as a real
drawing.
"""
import os, sys, math
_BT = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
if _BT not in sys.path: sys.path.insert(0, _BT)
from _props.geometry import (clear_scene, make_box, make_cyl, make_chamfer_box, make_rot_box, make_blob, make_lathe,
                             join_stock, export_glb)
from _props.structure import make_wall
from _props.furniture import make_bed, make_chair, make_table
from _props.small_wood_house import W, D, CEIL, T, WIN_X, WIN_W, WIN_H, WIN_Z, DOOR_X, bedroom_shell

PAL = {"wall": (0.80, 0.80, 0.76, 1.0), "baseboard": (0.42, 0.36, 0.30, 1.0)}
CONC = (0.52, 0.52, 0.50, 1.0); CONC_DARK = (0.42, 0.42, 0.40, 1.0)
BEIGE = (0.80, 0.76, 0.66, 1.0)
BZ = -2.5                                    # the basement floor
BED, BASE = "__dean_bedroom_1994", "__dean_basement_1994"
GRASS = (0.30, 0.38, 0.24, 1.0)
BX0, BX1, BY0, BY1 = -2.2, 3.4, -2.8, D + 0.2    # the basement's walls (outer lines)
WELL_X0, WELL_X1 = WIN_X - 0.70, WIN_X + 0.70    # under the bedroom window


def build_bedroom():
    """The shared room, dressed for Dean's rented house in 1994."""
    bedroom_shell(PAL, ((0.50, 0.40, 0.30, 1.0), (0.42, 0.34, 0.26, 1.0)), (0.86, 0.86, 0.84, 1.0), prefix="Dean_")
    # a thin curtain half drawn where the other house has its plank blinds
    make_box("Dean_Curtain_Rod", (WIN_X, D - 0.115, WIN_Z + WIN_H / 2.0 + 0.10), (WIN_W + 0.40, 0.03, 0.03), (0.30, 0.30, 0.32, 1.0))
    make_box("Dean_Curtain_Drawn", (WIN_X - WIN_W / 2.0 + 0.05, D - 0.14, WIN_Z - 0.03), (0.40, 0.03, WIN_H + 0.26), (0.66, 0.70, 0.72, 1.0))
    # the bed where the narrator's is (the two rooms overlap), the sheets thrown
    make_bed("Dean_Bed", -W / 2.0 + 0.10 + 0.50, D - 0.10 - 0.98, head="+Y", w=0.99, d=1.92, made=False,
             blanket_col=(0.30, 0.34, 0.40, 1.0), sheet_col=(0.88, 0.88, 0.86, 1.0))
    make_rot_box("Dean_Bed_Sheet_Thrown", (-W / 2.0 + 0.10 + 0.50 + 0.36, 2.4, 0.50), (0.30, 0.90, 0.10), (0.88, 0.88, 0.86, 1.0), pitch=0.5)
    # the nightstand and its clock (3:50), a glass of water; no lamp is on
    nx, ny = -W / 2.0 + 0.10 + 1.25, D - 0.10 - 0.24
    make_box("Dean_Nightstand", (nx, ny, 0.29), (0.42, 0.40, 0.58), (0.36, 0.30, 0.26, 1.0))
    make_box("Dean_Alarm_Clock", (nx - 0.06, ny + 0.04, 0.625), (0.20, 0.10, 0.09), (0.12, 0.12, 0.12, 1.0))
    make_box("Dean_Alarm_Clock_Face_Glow", (nx - 0.06, ny - 0.012, 0.63), (0.14, 0.004, 0.04), (0.92, 0.26, 0.16, 1.0))
    make_cyl("Dean_Water_Glass", (nx + 0.12, ny - 0.06, 0.64), 0.035, 0.12, (0.78, 0.82, 0.84, 1.0), segments=10)
    # the register in the floor (the furnace below it)
    rx, ry = 1.0, 1.6
    make_box("Dean_Floor_Register_Grate", (rx, ry, 0.003), (0.30, 0.14, 0.006), (0.30, 0.30, 0.30, 1.0))
    for k in range(5):
        make_box(f"Dean_Floor_Register_Slot_{k}", (rx - 0.12 + k * 0.06, ry, 0.0065), (0.02, 0.12, 0.001), (0.08, 0.08, 0.08, 1.0))
    # a chair with yesterday's clothes on the E wall; the dresser on the S
    # wall where the other house has its own; a school bag; the door open
    make_chair("Dean_Chair", W / 2.0 - 0.10 - 0.30, 2.6, yaw=math.pi / 2.0, wood=(0.40, 0.30, 0.22, 1.0))
    make_box("Dean_Chair_Clothes", (W / 2.0 - 0.10 - 0.30, 2.6, 0.50), (0.40, 0.40, 0.08), (0.30, 0.34, 0.44, 1.0))
    make_box("Dean_Dresser", (-0.70, 0.10 + 0.25, 0.48), (0.86, 0.48, 0.96), (0.56, 0.50, 0.42, 1.0))
    make_box("Dean_Dresser_Books", (-0.80, 0.30, 1.02), (0.30, 0.24, 0.12), (0.40, 0.24, 0.20, 1.0))
    make_chamfer_box("Dean_School_Bag", (0.30, 0.50, 0.16), (0.40, 0.24, 0.32), (0.20, 0.28, 0.40, 1.0), chamfer=0.06)
    make_box("Dean_Door_Open", (DOOR_X + 0.43, 0.10 + 0.40, 0.995), (0.04, 0.80, 1.99), (0.70, 0.62, 0.50, 1.0))
    make_box("Dean_Rug", (0.10, 2.10, 0.006), (1.40, 1.00, 0.012), (0.40, 0.30, 0.26, 1.0))


def build_hall():
    """The hall S of the room, the stair down to the basement in its E end."""
    fz, col = -0.02, (0.46, 0.36, 0.26, 1.0)
    make_box("Hall_Floor_W", ((BX0 + 2.2) / 2.0, -1.4, fz), (2.2 - BX0, 2.6, 0.04), col)
    make_box("Hall_Floor_E", ((3.1 + BX1) / 2.0, -1.4, fz), (BX1 - 3.1, 2.6, 0.04), col)
    make_box("Hall_Floor_S", (2.65, -2.6, fz), (0.9, 0.2, 0.04), col)
    make_wall("Hall_Wall_S", ((BX0 + BX1) / 2.0, BY0, 0), length=BX1 - BX0, height=CEIL, thickness=T, axis='X', palette=PAL,
              baseboard_face_sign=+1)
    make_wall("Hall_Wall_E", (BX1, -1.45, 0), length=2.5, height=CEIL, thickness=T, axis='Y', palette=PAL, baseboard_face_sign=-1)
    make_wall("Hall_Wall_W", (BX0, -1.45, 0), length=2.5, height=CEIL, thickness=T, axis='Y', palette=PAL, baseboard_face_sign=+1)
    make_box("Hall_Ceil", ((BX0 + BX1) / 2.0, -1.4, CEIL + 0.04), (BX1 - BX0, 2.8, 0.08), (0.86, 0.86, 0.84, 1.0))


def build_basement():
    wt = 0.25
    cx, cy = (BX0 + BX1) / 2.0, (BY0 + BY1) / 2.0
    make_box("Basement_Floor_Slab", (cx, cy, BZ - 0.05), (BX1 - BX0, BY1 - BY0, 0.10), CONC)
    make_box("Basement_Wall_S", (cx, BY0 + wt / 2.0, BZ / 2.0), (BX1 - BX0, wt, -BZ), CONC_DARK)
    make_box("Basement_Wall_W", (BX0 + wt / 2.0, cy, BZ / 2.0), (wt, BY1 - BY0 - 2 * wt, -BZ), CONC_DARK)
    make_box("Basement_Wall_E", (BX1 - wt / 2.0, cy, BZ / 2.0), (wt, BY1 - BY0 - 2 * wt, -BZ), CONC_DARK)
    wz0, wz1 = -1.0, -0.15
    yn = BY1 - wt / 2.0
    make_box("Basement_Wall_N_W", ((BX0 + WELL_X0) / 2.0, yn, BZ / 2.0), (WELL_X0 - BX0, wt, -BZ), CONC_DARK)
    make_box("Basement_Wall_N_E", ((WELL_X1 + BX1) / 2.0, yn, BZ / 2.0), (BX1 - WELL_X1, wt, -BZ), CONC_DARK)
    make_box("Basement_Wall_N_Below", ((WELL_X0 + WELL_X1) / 2.0, yn, (BZ + wz0) / 2.0), (WELL_X1 - WELL_X0, wt, wz0 - BZ), CONC_DARK)
    make_box("Basement_Wall_N_Above", ((WELL_X0 + WELL_X1) / 2.0, yn, wz1 / 2.0), (WELL_X1 - WELL_X0, wt, -wz1), CONC_DARK)
    for s in (-1, 1):
        make_box(f"Well_Window_Frame_Jamb_{s:+d}", ((WELL_X0 + WELL_X1) / 2.0 + s * ((WELL_X1 - WELL_X0) / 2.0 - 0.03), yn, (wz0 + wz1) / 2.0),
                 (0.06, wt + 0.02, wz1 - wz0), (0.70, 0.70, 0.68, 1.0))
    for zz in (wz0 + 0.03, wz1 - 0.03):
        make_box(f"Well_Window_Frame_Rail_{zz:.2f}", ((WELL_X0 + WELL_X1) / 2.0, yn, zz), (WELL_X1 - WELL_X0 - 0.12, wt + 0.02, 0.06),
                 (0.70, 0.70, 0.68, 1.0))
    # the underside of the floor above: subfloor (cut for the stair), joists
    sub = (0.56, 0.46, 0.34, 1.0)
    make_box("Basement_Ceil_Subfloor_N", (cx, (0.1 + BY1) / 2.0 - 0.0, -0.10), (BX1 - BX0, BY1 - 0.1, 0.08), sub)
    make_box("Basement_Ceil_Subfloor_SW", ((BX0 + 2.2) / 2.0, (BY0 - 0.0 + 0.1) / 2.0, -0.10), (2.2 - BX0, 0.1 - BY0, 0.08), sub)
    make_box("Basement_Ceil_Subfloor_SE", ((3.1 + BX1) / 2.0, (BY0 + 0.1) / 2.0, -0.10), (BX1 - 3.1, 0.1 - BY0, 0.08), sub)
    for k in range(13):
        make_box(f"Basement_Joist_{k}", (BX0 + 0.35 + k * 0.40, (0.1 + BY1) / 2.0, -0.24), (0.05, BY1 - 0.1 - 2 * wt, 0.20), (0.50, 0.40, 0.28, 1.0))
    # the stair down from the hall (open treads, S to N as it descends)
    for k in range(9):
        make_box(f"Basement_Stair_Tread_{k}", (2.65, -2.27 + k * 0.25, -0.25 - k * 0.25 - 0.02), (0.80, 0.26, 0.04), (0.50, 0.40, 0.28, 1.0))
    ang = math.atan2(2.25, 2.0)
    for s in (-1, 1):
        make_rot_box(f"Basement_Stair_Stringer_{s:+d}", (2.65 + s * 0.42, -1.27, -1.27), (0.05, 3.0, 0.26), (0.46, 0.36, 0.24, 1.0), roll=-ang)
    # the furnace under the bedroom's register, its riser; the water heater
    fx, fy = 1.8, 1.6
    make_box("Furnace", (fx, fy, BZ + 0.80), (0.80, 0.70, 1.60), (0.60, 0.58, 0.52, 1.0))
    make_box("Furnace_Plenum", (fx, fy, BZ + 1.85), (0.70, 0.60, 0.50), (0.66, 0.66, 0.64, 1.0))
    make_box("Furnace_Duct_Trunk", ((fx + 1.0) / 2.0 - 0.05, fy, -0.44), (fx - 1.0 + 0.5, 0.36, 0.26), (0.70, 0.70, 0.68, 1.0))
    make_box("Furnace_Pilot_Glow", (fx, fy - 0.352, BZ + 0.30), (0.08, 0.004, 0.06), (1.0, 0.56, 0.20, 1.0))
    make_cyl("Water_Heater", (fx + 1.0, fy + 0.70, BZ + 0.75), 0.28, 1.50, (0.80, 0.78, 0.72, 1.0), segments=14)
    # the desk under the window well: graph paper, the beige computer and the
    # CRT left off, floppies, the corded phone, the lamp he draws by
    dx, dy = WIN_X, BY1 - wt - 0.36
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
    # the shelf of game boxes on the W wall, the cold floor's rug
    sx = BX0 + wt + 0.18
    for lvl in range(3):
        make_box(f"Basement_Shelf_{lvl}", (sx, 1.0, BZ + 0.50 + lvl * 0.50), (0.36, 1.6, 0.03), (0.50, 0.42, 0.30, 1.0))
    for s in (-1, 1):
        make_box(f"Basement_Shelf_Upright_{s:+d}", (sx, 1.0 + s * 0.79, BZ + 0.80), (0.36, 0.03, 1.60), (0.46, 0.38, 0.26, 1.0))
    for k in range(10):
        lvl, i = k // 4, k % 4
        if lvl > 2:
            break
        make_box(f"Game_Box_{k}", (sx, 0.45 + i * 0.32, BZ + 0.515 + lvl * 0.50 + 0.15), (0.24, 0.06 + (k % 2) * 0.02, 0.30),
                 ((0.70, 0.30, 0.20, 1.0), (0.20, 0.36, 0.60, 1.0), (0.80, 0.70, 0.30, 1.0), (0.30, 0.50, 0.36, 1.0))[k % 4])
    make_box("Basement_Rug", (dx, dy - 0.8, BZ + 0.004), (1.6, 1.2, 0.008), (0.46, 0.30, 0.24, 1.0))


def build_outside():
    """North of the house: the window well (under the bedroom window), the
    rain, the pasture climbing to the Hagstrom place."""
    yw = BY1
    make_box("Well_Gravel_Ground", ((WELL_X0 + WELL_X1) / 2.0, yw + 0.55, -1.05), (WELL_X1 - WELL_X0 + 0.6, 0.90, 0.10), (0.50, 0.48, 0.44, 1.0))
    for k in range(7):
        a = math.pi * (k + 0.5) / 7.0
        make_rot_box(f"Well_Liner_Wall_{k}", ((WELL_X0 + WELL_X1) / 2.0 + 0.95 * math.cos(a), yw + 0.95 * math.sin(a) * 0.95, -0.50),
                     (0.04, 0.46, 1.10), ((0.62, 0.62, 0.64, 1.0), (0.52, 0.52, 0.54, 1.0))[k % 2], yaw=a)
    make_rot_box("Well_Bank_Ground", (WIN_X, yw + 1.9, -0.45), (3.4, 1.8, 0.20), (0.36, 0.30, 0.24, 1.0), roll=0.50)
    make_box("Yard_Ground_W", (WIN_X - 12.0, yw + 5.0, -0.06), (20.4, 10.0, 0.12), GRASS)
    make_box("Yard_Ground_E", (WIN_X + 12.0, yw + 5.0, -0.06), (20.4, 10.0, 0.12), GRASS)
    make_box("Yard_Ground_N", (WIN_X, yw + 7.0, -0.06), (3.6, 6.0, 0.12), GRASS)
    make_box("Yard_Ground_House", (0.6, -12.0, -0.06), (40.0, 18.0, 0.12), GRASS)
    th = 0.30
    y0h = yw + 10.0
    top = 125.0 * math.tan(th)
    make_rot_box("Pasture_Hill_Ground", (WIN_X, y0h + 62.5, top / 2.0 - 0.5), (160.0, 125.0 / math.cos(th), 1.0), GRASS, roll=th)
    make_box("Hagstrom_Yard_Ground", (WIN_X, y0h + 147.0, top - 0.5), (160.0, 44.0, 1.0), GRASS)
    for k in range(9):
        y = y0h + 15.0 + k * 12.0
        make_box(f"Pasture_Fence_Post_{k}", (-14.0, y, (y - y0h) * math.tan(th) + 0.6), (0.10, 0.10, 1.2), (0.40, 0.32, 0.24, 1.0))
    hy, hz = y0h + 135.0, top
    make_box("Hagstrom_House", (6.0, hy, hz + 2.4), (9.0, 7.0, 5.0), (0.70, 0.68, 0.62, 1.0))
    make_box("Hagstrom_Roof", (6.0, hy, hz + 5.2), (9.6, 7.6, 0.6), (0.24, 0.22, 0.22, 1.0))
    make_box("Hagstrom_Barn", (-8.0, hy + 4.0, hz + 3.0), (7.0, 10.0, 6.0), (0.46, 0.24, 0.20, 1.0))
    for k in range(8):
        make_blob(f"Hill_Fir_{k}", (-30.0 + k * 9.0, y0h + 151.0 + (k % 3) * 5.0, top + 5.0), 3.0, (0.14, 0.20, 0.14, 1.0),
                  noise=0.3, seed=k, squash=2.0)
    for k in range(14):
        make_box(f"Rain_Water_Streak_Bed_{k}", (WIN_X - 0.6 + k * 0.09, D + 0.5 + (k % 3) * 0.3, 1.5 + (k % 2) * 0.3), (0.006, 0.006, 1.6),
                 (0.70, 0.74, 0.80, 1.0))
    for k in range(14):
        make_box(f"Rain_Water_Streak_Well_{k}", (WELL_X0 + k * 0.10, yw + 1.2 + (k % 3) * 0.4, 0.4), (0.006, 0.006, 1.4),
                 (0.70, 0.74, 0.80, 1.0))
    make_box("Sky_Predawn" + BED, (0.0, 186.0, 60.0), (500.0, 0.2, 240.0), (0.06, 0.08, 0.12, 1.0))
    make_box("Sky_First_Light" + BASE, (0.0, 186.0, 60.0), (500.0, 0.2, 240.0), (0.46, 0.50, 0.56, 1.0))


def main():
    clear_scene()
    build_bedroom()
    build_hall()
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


if __name__ == "__main__":
    main()
