"""Faust's studio apartment — vol1's most-played interior (the 4am
act-one waking, the lullaby, the dream-states, the painting day).

DRAFT 3 (2026-10-09, the overnight run): the room was a 6 x 5 m box
with a 2.7 m ceiling, no bathroom, a mirror cabinet over the kitchen
sink and the books lost inside a dark case. The prose asks for more:
  "Faust wakes at four a.m. with the sound of an alarm. He pulls a
   tug of water" · "looks in the mirror at his early-morning haggard
   … opens the mirror to get his vitamins" · "puts on his medical
   blue uniform and white jacket and heads to work" · "Faust
   bicycles to work" · "Paintings on walls and floors" · "John gets
   up. To the bathroom. Pukes in the toilet."
So: a second-floor walk-up studio, 8.0 x 6.6 m under a 2.95 m
ceiling, with
  - a BATHROOM in the SE corner (its own walls, the door ajar on a
    lit vanity: the mirror cabinet open on the vitamins, the toilet,
    a tub behind a half-drawn curtain);
  - the entry door in the S wall, the hooks beside it carrying the
    blue scrubs and the white coat, his shoes and bag under them,
    the bicycle leaning on the bathroom's outer wall;
  - the kitchenette along the W wall (fridge, counter, hot plate,
    sink, wall cupboards) and a two-chair cafe table;
  - a four-bay bookcase as a CARCASS (the books stand to the front of
    the shelves, of unequal heights, a few lying flat), the reading
    chair and floor lamp in front of it;
  - the bed in the NW corner under his biggest canvas, the
    nightstand with the alarm (4:00), the water glass, the journal;
    the dresser with a stack of drug-rep sample boxes; the wall
    clock stopped at four;
  - the PAINTING CORNER by the E window: easel on a drop cloth, the
    elemental canvas, a paint table with palette and brush jar, a
    stool, canvases leaned on the wall and laid on the floor; the
    radiator under the window; a desk under a second, N window.

Coordinate frame: Blender Z-up. y=0 is the door (south) wall; +Y
runs back into the room; walls centred on x=+-4.0, y=0 and y=6.6
(20 cm thick: room faces at x=+-3.9, y=0.1, y=6.5), ceiling 2.95.
glTF export remaps to Godot (x, z, -y).

Vantages wired in Background3D.CAMERA_PRESETS:
  faust_bedroom       — mid-room looking NW at the bed corner.
  faust_apartment_day — inside the door, the whole studio in one
                        wide: bed far left, painting corner right.

Draft 4 targets: the hall beyond the entry door (a cracked-open
variant for the morning exit); a second bathroom insert (the toilet,
for the waking's last line); the bookcase's titles as a readable
insert; dust on the radiator and a paint-crusted floor around the
easel; Deck framing of both presets.
"""
import math
import os, sys
_BT = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
if _BT not in sys.path: sys.path.insert(0, _BT)
from _props.geometry import clear_scene, make_box, make_cyl, make_rot_box, make_tube, make_lathe, export_glb
from _props.structure import make_floor, make_wall, make_ceiling, make_wall_with_openings, make_frame_ring
from _props.furniture import make_bed, make_chair, make_table, make_stool, make_lamp
from _props.objects import make_drinking_glass, make_mug, make_jar
from _props.decor import make_wall_clock
from _props.detail import make_wall_outlet, make_light_switch, make_floor_stain, make_traffic_wear
from _props.views import make_view

ROOM_W = 8.0      # x in [-4, 4]
ROOM_D = 6.6      # y in [0, 6.6]
CEIL = 2.95
XW, XE = -ROOM_W / 2.0 + 0.10, ROOM_W / 2.0 - 0.10    # room faces
YS, YN = 0.10, ROOM_D - 0.10

COL_WALL = (0.52, 0.50, 0.43, 1.0)      # warm gray-green plaster
COL_BASE = (0.28, 0.24, 0.18, 1.0)
COL_FLOOR = (0.38, 0.27, 0.16, 1.0)     # old fir boards
COL_SEAM = (0.27, 0.19, 0.11, 1.0)
COL_CEIL = (0.50, 0.48, 0.44, 1.0)
COL_BEDFRAME = (0.28, 0.20, 0.14, 1.0)
COL_MATTRESS = (0.72, 0.68, 0.58, 1.0)
COL_BLANKET = (0.46, 0.17, 0.15, 1.0)   # deep red
COL_PILLOW = (0.80, 0.76, 0.66, 1.0)
COL_WOOD = (0.32, 0.23, 0.15, 1.0)
COL_WOOD_LT = (0.46, 0.34, 0.21, 1.0)
COL_LAMP = (1.00, 0.86, 0.55, 1.0)      # warm bulb — blooms via glow
COL_SHADE = (0.66, 0.52, 0.32, 1.0)
COL_GLASS = (0.40, 0.48, 0.58, 0.6)
COL_FRAME = (0.22, 0.20, 0.17, 1.0)
COL_CURTAIN = (0.58, 0.46, 0.30, 1.0)
COL_CANVAS = (0.86, 0.82, 0.72, 1.0)
COL_STRETCHER = (0.62, 0.52, 0.36, 1.0)
COL_RUG = (0.34, 0.26, 0.36, 1.0)
COL_RUG_EDGE = (0.22, 0.17, 0.25, 1.0)
COL_STEEL = (0.58, 0.60, 0.61, 1.0)
COL_ENAMEL = (0.86, 0.86, 0.82, 1.0)
COL_TILE = (0.72, 0.74, 0.70, 1.0)
COL_COUNTER = (0.40, 0.44, 0.38, 1.0)   # green-painted cabinets
COL_TOP = (0.70, 0.68, 0.62, 1.0)
COL_SCRUBS = (0.30, 0.46, 0.66, 1.0)    # "his medical blue uniform"
COL_COAT = (0.90, 0.90, 0.88, 1.0)      # "and white jacket"
COL_BIKE = (0.50, 0.18, 0.15, 1.0)
COL_TIRE = (0.12, 0.12, 0.12, 1.0)
COL_UPHOL = (0.36, 0.40, 0.30, 1.0)     # moss velvet armchair
COL_DROP = (0.58, 0.55, 0.47, 1.0)

SPINES = [
    (0.48, 0.20, 0.16, 1.0), (0.22, 0.30, 0.24, 1.0), (0.62, 0.54, 0.38, 1.0),
    (0.24, 0.22, 0.34, 1.0), (0.58, 0.40, 0.20, 1.0), (0.44, 0.46, 0.48, 1.0),
    (0.32, 0.15, 0.12, 1.0), (0.18, 0.26, 0.32, 1.0), (0.78, 0.74, 0.62, 1.0),
]
# the three elementals and the rest of his palette
PAINT = [(0.28, 0.42, 0.60, 1.0), (0.82, 0.80, 0.72, 1.0), (0.76, 0.32, 0.16, 1.0),
         (0.66, 0.56, 0.22, 1.0), (0.30, 0.46, 0.30, 1.0), (0.46, 0.22, 0.40, 1.0),
         (0.14, 0.14, 0.18, 1.0)]

# openings (centre along the wall, z centre, width, height)
DOOR_S = (-0.45, 1.05, 0.92, 2.10)
WIN_E = (4.10, 1.70, 1.90, 1.70)
WIN_N = (2.60, 1.75, 1.30, 1.50)
BATH_X0, BATH_YN = 1.78, 2.46          # bathroom outer faces (W, N)
BATH_DOOR = (2.65, 1.025, 0.80, 2.05)


def build_shell():
    make_floor("Floor", (0.0, ROOM_D / 2.0, 0.0), size_x=ROOM_W + 0.4,
               size_y=ROOM_D + 0.4, palette={"vinyl": COL_FLOOR, "seam": COL_SEAM})
    pal = {"wall": COL_WALL, "baseboard": COL_BASE}
    make_wall("Wall_W", (-ROOM_W / 2.0, ROOM_D / 2.0, 0), length=ROOM_D + 0.4,
              height=CEIL, axis='Y', palette=pal, baseboard_face_sign=+1)
    make_wall_with_openings("Wall_E", (ROOM_W / 2.0, ROOM_D / 2.0, 0), length=ROOM_D + 0.4,
                            height=CEIL, axis='Y', palette=pal, baseboard_face_sign=-1, openings=[WIN_E])
    make_wall_with_openings("Wall_N", (0.0, ROOM_D, 0), length=ROOM_W + 0.4, height=CEIL,
                            axis='X', palette=pal, baseboard_face_sign=-1, openings=[WIN_N])
    make_wall_with_openings("Wall_S", (0.0, 0.0, 0), length=ROOM_W + 0.4, height=CEIL,
                            axis='X', palette=pal, baseboard_face_sign=+1, openings=[DOOR_S])
    make_ceiling("Ceil", (0.0, ROOM_D / 2.0, CEIL), size_x=ROOM_W + 0.4,
                 size_y=ROOM_D + 0.4, with_grid=False, with_stains=False,
                 palette={"tile": COL_CEIL})
    # a picture rail all round, 40 cm under the ceiling (a 1920s walk-up)
    pr = CEIL - 0.40
    make_box("Picture_Rail_W", (XW + 0.012, ROOM_D / 2.0, pr), (0.024, ROOM_D - 0.2, 0.035), COL_BASE)
    make_box("Picture_Rail_N_W", ((XW + WIN_N[0] - WIN_N[2] / 2.0) / 2.0, YN - 0.012, pr), (WIN_N[0] - WIN_N[2] / 2.0 - XW, 0.024, 0.035), COL_BASE)
    make_box("Picture_Rail_S_W", ((XW + DOOR_S[0] - DOOR_S[2] / 2.0) / 2.0, YS + 0.012, pr), (DOOR_S[0] - DOOR_S[2] / 2.0 - XW, 0.024, 0.035), COL_BASE)
    # Entry door: S wall, closed, chained (4 am)
    dx = DOOR_S[0]
    make_box("Entry_Door_Leaf", (dx, 0.0, 1.045), (0.90, 0.045, 2.09), COL_WOOD)
    for i, zc in enumerate((0.55, 1.50)):
        make_box(f"Entry_Door_Panel_{i}", (dx, 0.03, zc), (0.62, 0.015, 0.70), (0.28, 0.20, 0.13, 1.0))
    make_cyl("Entry_Door_Knob", (dx + 0.34, 0.06, 1.00), 0.032, 0.055, COL_STEEL, segments=10, axis='Y')
    make_box("Entry_Door_Deadbolt", (dx + 0.34, 0.035, 1.30), (0.07, 0.025, 0.07), COL_STEEL)
    make_tube("Entry_Door_Chain", [(dx + 0.31, 0.04, 1.42), (dx + 0.36, 0.045, 1.36), (dx + 0.42, 0.04, 1.40)], 0.006, COL_STEEL, segments=4)
    make_box("Entry_Door_Peephole", (dx, 0.03, 1.55), (0.03, 0.02, 0.03), COL_STEEL)
    a0, a1 = dx - DOOR_S[2] / 2.0, dx + DOOR_S[2] / 2.0
    for nm, x in (("A", a0 - 0.035), ("B", a1 + 0.035)):
        make_box(f"Entry_Door_Casing_{nm}", (x, YS + 0.01, 1.08), (0.07, 0.02, 2.16), COL_BASE)
    make_box("Entry_Door_Casing_Head", (dx, YS + 0.01, 2.135), (DOOR_S[2] + 0.14, 0.02, 0.07), COL_BASE)
    make_light_switch("Switch_Entry", (a1 + 0.22, 0.0), axis='X', face_sign=+1, z=1.20)
    # Rug in the middle of the room, the path worn to the bed
    make_box("Rug", (-0.6, 3.5, 0.008), (2.9, 2.1, 0.012), COL_RUG)
    for nm, y in (("S", 2.50), ("N", 4.50)):
        make_box(f"Rug_Edge_{nm}", (-0.6, y, 0.016), (2.9, 0.10, 0.006), COL_RUG_EDGE)
    make_traffic_wear("Floor_Wear", [(-0.45, 0.45), (-0.9, 2.0), (-1.6, 4.0), (-1.95, 5.2)], width=0.6)


def build_bathroom():
    """SE corner, x 1.90..3.90, y 0.10..2.34 inside. The door in its
    N wall stands open into it on the lit vanity: mirror cabinet over
    the basin (open, the vitamins on its shelf), toilet on the S wall
    beside it, a tub along the E wall behind a half-drawn curtain."""
    pal = {"wall": COL_WALL, "baseboard": COL_BASE}
    t = 0.12
    make_wall("Bath_Wall_W", (BATH_X0 + t / 2.0, (YS + BATH_YN) / 2.0, 0), length=BATH_YN - YS,
              height=CEIL, thickness=t, axis='Y', palette=pal, baseboard_face_sign=-1)
    make_wall_with_openings("Bath_Wall_N", ((BATH_X0 + XE) / 2.0, BATH_YN - t / 2.0, 0), length=XE - BATH_X0,
                            height=CEIL, thickness=t, axis='X', palette=pal, baseboard_face_sign=+1,
                            openings=[BATH_DOOR])
    xi0, yi1 = BATH_X0 + t, BATH_YN - t           # inside faces 1.90 / 2.34
    make_box("Bath_Floor_Tile", ((xi0 + XE) / 2.0, (YS + yi1) / 2.0, 0.004), (XE - xi0, yi1 - YS, 0.008), COL_TILE)
    # tile wainscot on the inside faces (S and E walls, W partition)
    make_box("Bath_Wainscot_S", ((xi0 + XE) / 2.0, YS + 0.005, 0.60), (XE - xi0, 0.01, 1.20), (0.80, 0.82, 0.78, 1.0))
    make_box("Bath_Wainscot_E", (XE - 0.005, (YS + yi1) / 2.0 + 0.0, 0.60), (0.01, yi1 - YS - 0.02, 1.20), (0.80, 0.82, 0.78, 1.0))
    make_box("Bath_Wainscot_Cap_S", ((xi0 + XE) / 2.0, YS + 0.015, 1.21), (XE - xi0, 0.03, 0.03), (0.62, 0.64, 0.60, 1.0))
    # door: hinged at the E jamb, standing open 60 degrees into the room
    o0, o1 = BATH_DOOR[0] - BATH_DOOR[2] / 2.0, BATH_DOOR[0] + BATH_DOOR[2] / 2.0
    hx, hy, ln, th = o1 - 0.01, yi1 - 0.03, 0.78, 0.04
    a = math.radians(60.0)
    make_rot_box("Bath_Door_Leaf", (hx - ln / 2.0 * math.cos(a), hy - ln / 2.0 * math.sin(a), 1.015),
                 (ln, th, 2.03), (0.80, 0.78, 0.70, 1.0), yaw=a)
    kx, ky = hx - (ln - 0.07) * math.cos(a), hy - (ln - 0.07) * math.sin(a)
    make_cyl("Bath_Door_Knob", (kx + 0.04 * math.sin(a), ky - 0.04 * math.cos(a), 1.0), 0.028, 0.05, COL_STEEL, segments=8)
    for nm, x in (("A", o0 - 0.035), ("B", o1 + 0.035)):
        make_box(f"Bath_Door_Casing_{nm}", (x, BATH_YN + 0.01, 1.06), (0.07, 0.02, 2.12), COL_BASE)
    make_box("Bath_Door_Casing_Head", (BATH_DOOR[0], BATH_YN + 0.01, 2.085), (BATH_DOOR[2] + 0.14, 0.02, 0.07), COL_BASE)
    make_light_switch("Switch_Bath", (o0 - 0.20, BATH_YN - 0.108), axis='X', face_sign=+1, z=1.20)
    # pedestal basin on the S wall
    sx = 2.40
    make_lathe("Bath_Sink_Pedestal", (sx, 0.30, 0.0), [(0.11, 0.0), (0.08, 0.10), (0.065, 0.45), (0.10, 0.70), (0.0, 0.70)], COL_ENAMEL, segments=12)
    make_box("Bath_Sink_Basin", (sx, 0.31, 0.77), (0.52, 0.42, 0.14), COL_ENAMEL)
    make_box("Bath_Sink_Bowl", (sx, 0.33, 0.835), (0.38, 0.28, 0.012), (0.62, 0.64, 0.64, 1.0))
    make_cyl("Bath_Sink_Faucet", (sx, 0.15, 0.89), 0.016, 0.10, COL_STEEL, segments=6)
    make_box("Bath_Sink_Spout", (sx, 0.19, 0.93), (0.025, 0.08, 0.02), COL_STEEL)
    for i, ox in enumerate((-0.09, 0.09)):
        make_cyl(f"Bath_Sink_Tap_{i}", (sx + ox, 0.15, 0.86), 0.022, 0.04, COL_STEEL, segments=6)
    make_cyl("Bath_Toothbrush_Cup", (sx - 0.20, 0.16, 0.89), 0.03, 0.10, (0.70, 0.78, 0.82, 0.7), segments=8)
    make_box("Bath_Soap", (sx + 0.20, 0.18, 0.85), (0.08, 0.05, 0.02), (0.86, 0.80, 0.66, 1.0))
    # the MIRROR CABINET — open, the vitamins on its shelf
    mz0, mz1, mw = 1.26, 1.90, 0.50
    cz = (mz0 + mz1) / 2.0
    make_box("Mirror_Cabinet_Back", (sx, YS + 0.01, cz), (mw, 0.02, mz1 - mz0), COL_ENAMEL)
    for nm, x in (("A", sx - mw / 2.0 + 0.01), ("B", sx + mw / 2.0 - 0.01)):
        make_box(f"Mirror_Cabinet_Side_{nm}", (x, YS + 0.07, cz), (0.02, 0.10, mz1 - mz0), COL_ENAMEL)
    for nm, z in (("Bottom", mz0 + 0.01), ("Top", mz1 - 0.01), ("Shelf", 1.58)):
        make_box(f"Mirror_Cabinet_{nm}", (sx, YS + 0.07, z), (mw - 0.04, 0.10, 0.02), COL_ENAMEL)
    # the mirror door is hinged on its W edge and swung right back (it
    # stood across the cabinet's mouth at 35 degrees and hid the vitamins)
    hx2, hy2, lw = sx - mw / 2.0, YS + 0.13, mw - 0.02
    b = math.radians(110.0)
    make_rot_box("Mirror_Door_Leaf", (hx2 + lw / 2.0 * math.cos(b), hy2 + lw / 2.0 * math.sin(b), cz),
                 (lw, 0.02, mz1 - mz0 - 0.02), (0.70, 0.78, 0.82, 1.0), yaw=b)
    for i, (ox, h, col) in enumerate(((-0.14, 0.09, (0.66, 0.52, 0.24, 1.0)), (-0.06, 0.11, (0.86, 0.86, 0.84, 1.0)),
                                      (0.04, 0.07, (0.56, 0.30, 0.20, 1.0)))):
        make_cyl(f"Vitamin_Bottle_{i}", (sx + ox, YS + 0.07, 1.59 + h / 2.0), 0.024, h, col, segments=8)
        make_cyl(f"Vitamin_Bottle_{i}_Cap", (sx + ox, YS + 0.07, 1.59 + h + 0.01), 0.026, 0.02, (0.92, 0.92, 0.90, 1.0), segments=8)
    make_box("Razor", (sx + 0.08, YS + 0.07, mz0 + 0.03), (0.14, 0.03, 0.02), (0.30, 0.30, 0.34, 1.0))
    make_cyl("Shave_Cream", (sx - 0.12, YS + 0.07, mz0 + 0.09), 0.03, 0.14, (0.86, 0.30, 0.22, 1.0), segments=8)
    make_box("Bath_Vanity", (sx, YS + 0.05, 2.02), (0.44, 0.08, 0.09), COL_LAMP)
    make_box("Bath_Vanity_Plate", (sx, YS + 0.005, 2.02), (0.50, 0.01, 0.13), COL_STEEL)
    # toilet beside the basin
    tx = 3.10
    make_box("Toilet_Tank", (tx, 0.20, 0.62), (0.44, 0.20, 0.38), COL_ENAMEL)
    make_box("Toilet_Tank_Lid", (tx, 0.20, 0.825), (0.46, 0.22, 0.03), COL_ENAMEL)
    make_box("Toilet_Flush", (tx - 0.15, 0.305, 0.74), (0.06, 0.01, 0.02), COL_STEEL)
    make_lathe("Toilet_Bowl", (tx, 0.52, 0.0), [(0.13, 0.0), (0.10, 0.08), (0.12, 0.25), (0.19, 0.40), (0.0, 0.40)], COL_ENAMEL, segments=12)
    make_box("Toilet_Seat", (tx, 0.52, 0.415), (0.38, 0.42, 0.03), (0.82, 0.80, 0.76, 1.0))
    make_box("Toilet_Lid_Leaf", (tx, 0.34, 0.65), (0.38, 0.03, 0.44), (0.82, 0.80, 0.76, 1.0))
    make_cyl("Toilet_Paper", (tx - 0.36, 0.30, 0.62), 0.055, 0.11, (0.94, 0.94, 0.92, 1.0), segments=10, axis='X')
    make_box("Toilet_Paper_Bracket", (tx - 0.36, 0.21, 0.62), (0.13, 0.18, 0.02), COL_STEEL)
    # tub along the E wall
    bx0, bx1, by0, by1, bh = 3.36, XE, 0.84, yi1, 0.54
    bxc, byc = (bx0 + bx1) / 2.0, (by0 + by1) / 2.0
    make_box("Tub_Side_W", (bx0 + 0.04, byc, bh / 2.0), (0.08, by1 - by0, bh), COL_ENAMEL)
    make_box("Tub_Side_E", (bx1 - 0.03, byc, bh / 2.0), (0.06, by1 - by0, bh), COL_ENAMEL)
    for nm, y in (("S", by0 + 0.03), ("N", by1 - 0.03)):
        make_box(f"Tub_End_{nm}", (bxc, y, bh / 2.0), (bx1 - bx0 - 0.14, 0.06, bh), COL_ENAMEL)
    make_box("Tub_Basin", (bxc, byc, 0.06), (bx1 - bx0 - 0.14, by1 - by0 - 0.12, 0.12), (0.80, 0.82, 0.80, 1.0))
    make_box("Tub_Drain", (bxc, by0 + 0.20, 0.122), (0.06, 0.06, 0.004), COL_STEEL)
    make_cyl("Shower_Pipe", (XE - 0.04, by1 - 0.10, 1.40), 0.015, 1.70, COL_STEEL, segments=6)
    make_box("Shower_Head", (XE - 0.10, by1 - 0.10, 2.22), (0.12, 0.08, 0.05), COL_STEEL)
    make_cyl("Shower_Rod", (bx0 + 0.02, (YS + yi1) / 2.0, 2.10), 0.012, yi1 - YS, COL_STEEL, segments=6, axis='Y')
    make_box("Shower_Curtain", (bx0 + 0.02, 1.80, 1.38), (0.03, 1.00, 1.42), (0.62, 0.70, 0.66, 1.0))
    make_box("Shower_Curtain_Bunch", (bx0 + 0.02, 1.16, 1.38), (0.08, 0.16, 1.42), (0.62, 0.70, 0.66, 1.0))
    make_cyl("Bath_Shampoo", (bx1 - 0.03, by0 + 0.30, bh + 0.09), 0.025, 0.18, (0.36, 0.56, 0.50, 1.0), segments=8)
    # towel rail on the partition, a bath mat
    make_cyl("Towel_Rail", (xi0 + 0.05, 1.30, 1.25), 0.012, 0.56, COL_STEEL, segments=6, axis='Y')
    for nm, y in (("A", 1.04), ("B", 1.56)):
        make_box(f"Towel_Rail_Bracket_{nm}", (xi0 + 0.025, y, 1.25), (0.05, 0.02, 0.02), COL_STEEL)
    make_box("Towel", (xi0 + 0.05, 1.30, 1.01), (0.026, 0.44, 0.46), (0.42, 0.54, 0.62, 1.0))
    make_box("Bath_Mat", (2.50, 1.20, 0.012), (0.70, 0.46, 0.008), (0.62, 0.54, 0.44, 1.0))
    make_cyl("Bath_Ceiling_Fixture", (2.90, 1.22, CEIL - 0.03), 0.14, 0.05, (0.88, 0.88, 0.84, 1.0), segments=12)


def build_entry():
    """The hooks by the door with the work clothes, shoes, bag; the
    bicycle on the bathroom's outer wall."""
    a1 = DOOR_S[0] + DOOR_S[2] / 2.0
    rx = a1 + 0.62
    make_box("Coat_Hook_Board", (rx, YS + 0.01, 1.74), (0.70, 0.02, 0.09), COL_WOOD_LT)
    for i, ox in enumerate((-0.24, 0.0, 0.24)):
        make_box(f"Coat_Hook_{i}", (rx + ox, YS + 0.045, 1.72), (0.02, 0.05, 0.02), COL_STEEL)
    # "his medical blue uniform and white jacket"
    make_box("Scrubs_Top", (rx - 0.24, YS + 0.075, 1.40), (0.44, 0.04, 0.62), COL_SCRUBS)
    make_box("Scrubs_Collar", (rx - 0.24, YS + 0.075, 1.705), (0.16, 0.042, 0.03), (0.24, 0.38, 0.56, 1.0))
    make_box("White_Coat", (rx + 0.20, YS + 0.085, 1.22), (0.50, 0.06, 0.99), COL_COAT)
    make_box("White_Coat_Lapel", (rx + 0.20, YS + 0.117, 1.52), (0.14, 0.004, 0.36), (0.80, 0.80, 0.78, 1.0))
    make_box("White_Coat_Pocket", (rx + 0.09, YS + 0.117, 1.36), (0.11, 0.004, 0.10), (0.84, 0.84, 0.82, 1.0))
    make_box("White_Coat_Pen", (rx + 0.07, YS + 0.121, 1.42), (0.01, 0.006, 0.08), (0.18, 0.22, 0.42, 1.0))
    make_box("Scrubs_Pants", (rx + 0.0, YS + 0.07, 1.30), (0.30, 0.03, 0.80), COL_SCRUBS)
    for i, (ox, col) in enumerate(((-0.30, (0.16, 0.16, 0.18, 1.0)), (0.05, (0.86, 0.86, 0.84, 1.0)))):
        for j in (-1, 1):
            make_box(f"Shoe_{i}_{j:+d}", (rx + ox + j * 0.06, YS + 0.20, 0.045), (0.10, 0.27, 0.09), col)
    make_rot_box("Work_Bag", (rx + 0.42, YS + 0.12, 0.17), (0.38, 0.12, 0.30), (0.26, 0.22, 0.18, 1.0), pitch=0.0, roll=0.20)
    # the bicycle, leaning on the bathroom's W wall, wheels to the floor
    bxl = BATH_X0 - 0.25
    yr, yf, rw = 0.56, 1.58, 0.33
    for nm, y in (("Rear", yr), ("Front", yf)):
        make_cyl(f"Bike_Wheel_{nm}", (bxl, y, rw), rw, 0.035, COL_TIRE, segments=18, axis='X')
        make_cyl(f"Bike_Wheel_{nm}_Rim", (bxl, y, rw), rw - 0.04, 0.04, (0.66, 0.66, 0.64, 1.0), segments=18, axis='X')
        make_cyl(f"Bike_Wheel_{nm}_Hub", (bxl, y, rw), 0.04, 0.10, COL_STEEL, segments=8, axis='X')
    bb = (bxl, 0.98, 0.30)
    seat = (bxl, 0.84, 0.80)
    head = (bxl, 1.46, 0.84)
    make_tube("Bike_Frame_Seat", [bb, seat], 0.016, COL_BIKE)
    make_tube("Bike_Frame_Down", [bb, (bxl, 1.43, 0.72)], 0.018, COL_BIKE)
    make_tube("Bike_Frame_Top", [seat, head], 0.016, COL_BIKE)
    make_tube("Bike_Frame_Stay", [bb, (bxl, yr, rw)], 0.012, COL_BIKE)
    make_tube("Bike_Frame_SeatStay", [seat, (bxl, yr, rw)], 0.011, COL_BIKE)
    make_tube("Bike_Frame_Fork", [head, (bxl, yf, rw)], 0.014, COL_BIKE)
    make_tube("Bike_Seatpost", [seat, (bxl, 0.81, 0.90)], 0.012, COL_STEEL)
    make_box("Bike_Saddle", (bxl, 0.80, 0.925), (0.10, 0.26, 0.05), (0.14, 0.12, 0.10, 1.0))
    make_tube("Bike_Stem", [head, (bxl, 1.47, 0.98)], 0.013, COL_STEEL)
    make_cyl("Bike_Handlebar", (bxl, 1.47, 0.99), 0.012, 0.46, COL_STEEL, segments=6, axis='X')
    make_cyl("Bike_Crank", (bxl + 0.022, bb[1], bb[2]), 0.07, 0.01, COL_STEEL, segments=10, axis='X')
    make_box("Bike_Pedal", (bxl + 0.045, bb[1] + 0.05, bb[2] - 0.05), (0.06, 0.06, 0.02), (0.14, 0.14, 0.14, 1.0))
    make_box("Bike_Lock", (bxl - 0.025, 0.91, 0.55), (0.03, 0.10, 0.14), (0.16, 0.16, 0.18, 1.0))
    make_box("Bike_Light", (bxl + 0.10, 1.47, 0.955), (0.05, 0.05, 0.05), (0.92, 0.88, 0.70, 1.0))


def build_kitchenette():
    """W wall, S end: fridge, a counter run with hot plate and sink,
    wall cupboards; a two-chair cafe table."""
    fx, fy = XW + 0.33, YS + 0.38
    make_box("Fridge", (fx, fy, 0.78), (0.64, 0.66, 1.56), COL_ENAMEL)
    make_box("Fridge_Seam", (fx + 0.322, fy, 1.18), (0.004, 0.62, 0.012), (0.60, 0.60, 0.58, 1.0))
    make_box("Fridge_Handle", (fx + 0.34, fy + 0.26, 0.90), (0.03, 0.03, 0.40), COL_STEEL)
    make_box("Fridge_Handle_Top", (fx + 0.34, fy + 0.26, 1.36), (0.03, 0.03, 0.14), COL_STEEL)
    make_box("Fridge_Postcard", (fx + 0.3225, fy - 0.12, 1.40), (0.005, 0.15, 0.10), (0.70, 0.52, 0.40, 1.0))
    make_box("Fridge_Magnet_List", (fx + 0.3225, fy + 0.06, 0.95), (0.005, 0.12, 0.20), (0.92, 0.90, 0.80, 1.0))
    make_box("Cereal_Box", (fx - 0.10, fy - 0.05, 1.71), (0.20, 0.07, 0.30), (0.78, 0.56, 0.20, 1.0))
    make_box("Fridge_Fan_Box", (fx + 0.12, fy + 0.10, 1.59), (0.24, 0.24, 0.06), (0.30, 0.26, 0.22, 1.0))
    cy0, cy1 = YS + 0.76, 2.26
    ccy, cl = (cy0 + cy1) / 2.0, cy1 - cy0
    make_box("Kit_Counter", (XW + 0.29, ccy, 0.44), (0.58, cl, 0.88), COL_COUNTER)
    make_box("Kit_Toe", (XW + 0.57, ccy, 0.05), (0.02, cl, 0.10), (0.20, 0.20, 0.18, 1.0))
    for i in range(3):
        y = cy0 + cl * (i + 0.5) / 3.0
        make_box(f"Kit_Door_{i}", (XW + 0.585, y, 0.48), (0.01, cl / 3.0 - 0.04, 0.64), (0.46, 0.50, 0.44, 1.0))
        make_box(f"Kit_Door_{i}_Pull", (XW + 0.595, y + cl / 6.0 - 0.07, 0.72), (0.012, 0.02, 0.10), COL_STEEL)
    make_box("Kit_Top", (XW + 0.31, ccy, 0.905), (0.62, cl + 0.04, 0.04), COL_TOP)
    sy = cy1 - 0.36
    make_box("Kit_Sink", (XW + 0.32, sy, 0.928), (0.40, 0.44, 0.006), COL_STEEL)
    make_box("Kit_Sink_Bowl", (XW + 0.32, sy, 0.932), (0.32, 0.36, 0.004), (0.40, 0.42, 0.44, 1.0))
    make_cyl("Kit_Faucet", (XW + 0.07, sy, 1.03), 0.018, 0.20, COL_STEEL, segments=6)
    make_box("Kit_Faucet_Spout", (XW + 0.15, sy, 1.12), (0.16, 0.025, 0.025), COL_STEEL)
    make_box("Dish_Rack", (XW + 0.32, sy - 0.40, 0.975), (0.34, 0.30, 0.10), (0.70, 0.70, 0.68, 1.0))
    for i in range(3):
        make_box(f"Dish_Rack_Plate_{i}", (XW + 0.32, sy - 0.48 + i * 0.07, 1.06), (0.24, 0.012, 0.16), (0.88, 0.86, 0.80, 1.0))
    hy = cy0 + 0.30
    make_box("Hotplate", (XW + 0.32, hy, 0.95), (0.32, 0.54, 0.05), (0.18, 0.18, 0.18, 1.0))
    for i, oy in enumerate((-0.13, 0.13)):
        make_cyl(f"Hotplate_Burner_{i}", (XW + 0.32, hy + oy, 0.977), 0.09, 0.006, (0.30, 0.20, 0.16, 1.0), segments=12)
    make_cyl("Kettle", (XW + 0.32, hy - 0.13, 1.07), 0.09, 0.18, COL_STEEL, segments=12)
    make_box("Kettle_Handle", (XW + 0.32, hy - 0.13, 1.17), (0.03, 0.14, 0.03), (0.14, 0.14, 0.14, 1.0))
    make_mug("Kit_Mug", XW + 0.36, cy1 - 0.08, 0.925, (0.72, 0.30, 0.22, 1.0))
    make_jar("Kit_Jar_Coffee", XW + 0.12, cy0 + 0.66, 0.925, (0.36, 0.24, 0.16, 1.0))
    # wall cupboards (closed) and a tile splash
    make_box("Kit_Splash", (XW + 0.005, ccy, 1.21), (0.01, cl, 0.56), (0.70, 0.72, 0.66, 1.0))
    make_box("Kit_Cupboard", (XW + 0.17, ccy, 1.86), (0.34, cl, 0.70), COL_COUNTER)
    for i in range(3):
        y = cy0 + cl * (i + 0.5) / 3.0
        make_box(f"Kit_Cupboard_Door_{i}", (XW + 0.345, y, 1.86), (0.01, cl / 3.0 - 0.04, 0.64), (0.46, 0.50, 0.44, 1.0))
    make_box("Kit_Cupboard_Light", (XW + 0.25, ccy, 1.495), (0.12, 0.60, 0.02), (0.92, 0.90, 0.80, 1.0))
    make_wall_outlet("Outlet_Kit", (-ROOM_W / 2.0, cy0 + 0.10), axis='Y', face_sign=+1, z=1.05)
    # cafe table and two chairs
    make_table("Cafe_Table", -2.55, 1.15, w=0.70, d=0.70, h=0.74, wood=COL_WOOD, top_col=COL_WOOD_LT)
    make_chair("Cafe_Chair_N", -2.55, 1.74, yaw=math.pi, wood=COL_WOOD)
    make_chair("Cafe_Chair_E", -1.96, 1.15, yaw=math.pi / 2.0, wood=COL_WOOD)
    make_box("Mail_Stack", (-2.68, 1.05, 0.745), (0.22, 0.15, 0.01), (0.92, 0.90, 0.84, 1.0))
    make_box("Mail_Envelope", (-2.66, 1.07, 0.753), (0.20, 0.10, 0.004), (0.80, 0.70, 0.52, 1.0))
    make_box("Pill_Organizer", (-2.40, 1.24, 0.755), (0.20, 0.06, 0.025), (0.50, 0.62, 0.76, 1.0))
    make_box("Keys", (-2.36, 1.02, 0.745), (0.07, 0.04, 0.01), COL_STEEL)


def _book_row(prefix, x_front, y0, y1, z, seed):
    """Books standing on a shelf, spines flush with its FRONT edge (they
    were centred deep in the case and read as a dark slab), unequal
    heights, a gap or two, now and then a short stack lying flat."""
    y = y0 + 0.01
    i = 0
    while y < y1 - 0.04:
        r = (seed * 7 + i * 13) % 17
        if r == 3 and y < y1 - 0.24:      # a lying stack
            h_st = 0.0
            for k in range(3):
                th = 0.03 + 0.01 * ((r + k) % 2)
                make_box(f"{prefix}_Flat_{i}_{k}", (x_front - 0.11, y + 0.11, z + h_st + th / 2.0), (0.20, 0.21, th), SPINES[(seed + i + k) % len(SPINES)])
                h_st += th
            y += 0.24
        elif r == 9:                      # a gap
            y += 0.05
        else:
            t = 0.025 + 0.008 * (r % 4)
            h = 0.19 + 0.025 * ((r * 3) % 5)
            d = 0.17 + 0.02 * (r % 3)
            make_box(f"{prefix}_Book_{i}", (x_front - d / 2.0, y + t / 2.0, z + h / 2.0), (d, t, h), SPINES[(seed + i * 5) % len(SPINES)])
            y += t + 0.002
        i += 1


def build_bookcase_reading():
    """W wall, middle: a four-bay bookcase CARCASS (back on the wall,
    sides, dividers, top, shelves), the reading chair and lamp."""
    y0, y1, top, dep = 2.50, 4.30, 2.20, 0.32
    xc, xf = XW + dep / 2.0, XW + dep
    yc = (y0 + y1) / 2.0
    make_box("Case_Back", (XW + 0.01, yc, top / 2.0), (0.02, y1 - y0, top), COL_WOOD)
    make_box("Case_Plinth", (xc + 0.01, yc, 0.04), (dep - 0.02, y1 - y0, 0.08), COL_WOOD)
    make_box("Case_Top", (xc, yc, top - 0.0125), (dep + 0.02, y1 - y0 + 0.04, 0.025), COL_WOOD)
    bays = 4
    bw = (y1 - y0) / bays
    for i in range(bays + 1):
        yy = y0 + i * bw
        yy = min(max(yy, y0 + 0.0125), y1 - 0.0125)
        make_box(f"Case_Side_{i}", (xc + 0.01, yy, (top - 0.025) / 2.0), (dep - 0.02, 0.025, top - 0.025), COL_WOOD)
    levels = (0.08, 0.50, 0.92, 1.34, 1.76)
    for zi, z in enumerate(levels):
        for bi in range(bays):
            ya, yb = y0 + bi * bw + 0.0125, y0 + (bi + 1) * bw - 0.0125
            if zi > 0:
                make_box(f"Case_Shelf_{zi}_{bi}", (xc + 0.01, (ya + yb) / 2.0, z - 0.0125), (dep - 0.02, yb - ya, 0.025), COL_WOOD_LT)
            if (zi, bi) == (4, 2):
                # the top shelf's third bay: rolled canvases, a jar of brushes
                for k in range(3):
                    make_cyl(f"Case_Rolled_Canvas_{k}", (xf - 0.10, ya + 0.06 + k * 0.11, z + 0.045 + (0.0 if k != 1 else 0.0)), 0.045, 0.20, COL_CANVAS, segments=8, axis='X')
                continue
            if (zi, bi) == (2, 1):
                # a gap with a small framed photo standing in it
                make_rot_box("Case_Photo", (xf - 0.08, (ya + yb) / 2.0 + 0.10, z + 0.09), (0.02, 0.14, 0.18), COL_FRAME, roll=0.0, pitch=0.0, yaw=0.0)
                _book_row(f"Case_{zi}_{bi}", xf - 0.01, ya, (ya + yb) / 2.0 - 0.02, z, zi * 4 + bi)
                continue
            _book_row(f"Case_{zi}_{bi}", xf - 0.01, ya, yb, z, zi * 4 + bi)
    # the reading chair, facing the room and the E window
    ax, ay = -2.42, 3.10
    make_box("Armchair_Base", (ax, ay, 0.20), (0.82, 0.82, 0.32), COL_UPHOL)
    for li, (ox, oy) in enumerate(((-0.36, -0.36), (0.36, -0.36), (-0.36, 0.36), (0.36, 0.36))):
        make_box(f"Armchair_Foot_{li}", (ax + ox, ay + oy, 0.02), (0.05, 0.05, 0.04), COL_WOOD)
    make_box("Armchair_Cushion", (ax + 0.08, ay, 0.42), (0.64, 0.54, 0.12), (0.40, 0.44, 0.33, 1.0))
    make_box("Armchair_Back", (ax - 0.32, ay, 0.70), (0.18, 0.82, 0.68), COL_UPHOL)
    for nm, oy in (("S", -0.34), ("N", 0.34)):
        make_box(f"Armchair_Arm_{nm}", (ax + 0.09, ay + oy, 0.48), (0.64, 0.14, 0.24), COL_UPHOL)
    make_box("Armchair_Throw", (ax - 0.32, ay + 0.12, 1.045), (0.20, 0.50, 0.03), (0.70, 0.62, 0.40, 1.0))
    make_box("Armchair_Book", (ax + 0.10, ay + 0.34, 0.615), (0.16, 0.12, 0.03), SPINES[3])
    # floor lamp south of the chair
    lx, ly = -2.98, 2.42
    make_lathe("FloorLamp_Base", (lx, ly, 0.0), [(0.0, 0.0), (0.15, 0.0), (0.14, 0.03), (0.02, 0.05), (0.0, 0.05)], (0.20, 0.18, 0.16, 1.0), segments=12)
    make_cyl("FloorLamp_Pole", (lx, ly, 0.78), 0.012, 1.46, (0.30, 0.26, 0.20, 1.0), segments=6)
    make_lathe("FloorLamp_Shade", (lx, ly, 1.42), [(0.20, 0.0), (0.14, 0.26), (0.0, 0.26)], COL_SHADE, segments=14)
    make_cyl("FloorLamp_Bulb", (lx, ly, 1.48), 0.03, 0.06, COL_LAMP, segments=8)
    make_tube("FloorLamp_Cord", [(lx, ly + 0.08, 0.02), (XW + 0.02, ly + 0.4, 0.02), (XW + 0.02, ly + 0.4, 0.30)], 0.005, (0.12, 0.12, 0.12, 1.0), segments=4)
    make_wall_outlet("Outlet_Reading", (-ROOM_W / 2.0, ly + 0.40), axis='Y', face_sign=+1)
    # a little side table N of the chair: mug, ashtray-less (he drinks water)
    make_lathe("Side_Table", (ax + 0.10, ay + 0.74, 0.0), [(0.16, 0.0), (0.03, 0.02), (0.025, 0.50), (0.20, 0.52), (0.20, 0.55), (0.0, 0.55)], COL_WOOD, segments=14)
    make_mug("Side_Table_Mug", ax + 0.16, ay + 0.70, 0.55, (0.86, 0.84, 0.78, 1.0))


def build_bed():
    """NW corner: the bed, headboard on the N wall, his biggest canvas
    over it; nightstand east of it with the 4am kit."""
    bx, by_head = -2.85, YN - 0.08
    make_box("Bed_Headboard", (bx, YN - 0.04, 0.72), (1.72, 0.08, 0.96), COL_BEDFRAME)
    make_box("Bed_Headboard_Cap", (bx, YN - 0.05, 1.215), (1.78, 0.10, 0.03), COL_BEDFRAME)
    make_bed("Bed", bx, by_head - 1.0, head="+Y", w=1.60, d=2.0, style="platform",
             frame_col=COL_BEDFRAME, mattress_col=COL_MATTRESS, sheet_col=COL_MATTRESS,
             blanket_col=COL_BLANKET, pillow_col=COL_PILLOW, pillows=2, made=False, headboard=False)
    # nightstand: carcass with a drawer, the alarm, the water, the journal
    nx, ny, nh = -1.70, YN - 0.23, 0.58
    make_box("Nightstand", (nx, ny, nh / 2.0), (0.50, 0.44, nh), COL_WOOD)
    make_box("Nightstand_Drawer", (nx, ny - 0.225, nh - 0.12), (0.42, 0.012, 0.14), COL_WOOD_LT)
    make_box("Nightstand_Drawer_Pull", (nx, ny - 0.235, nh - 0.12), (0.08, 0.01, 0.015), COL_STEEL)
    make_box("Nightstand_Opening", (nx, ny - 0.215, 0.20), (0.42, 0.012, 0.24), (0.16, 0.12, 0.08, 1.0))
    make_lamp("NLamp", nx - 0.12, ny + 0.08, base_z=nh, h=0.50, shade_col=COL_SHADE)
    make_box("Alarm_Clock", (nx + 0.12, ny + 0.08, nh + 0.065), (0.17, 0.09, 0.13), (0.20, 0.18, 0.16, 1.0))
    make_box("Alarm_Face", (nx + 0.12, ny + 0.033, nh + 0.07), (0.13, 0.005, 0.07), (0.86, 0.22, 0.18, 1.0))
    make_box("Journal", (nx + 0.02, ny - 0.11, nh + 0.0175), (0.20, 0.15, 0.035), (0.24, 0.22, 0.34, 1.0))
    make_box("Journal_Pen", (nx + 0.02, ny - 0.11, nh + 0.04), (0.14, 0.01, 0.01), (0.12, 0.12, 0.12, 1.0))
    make_drinking_glass("Water_Glass", nx + 0.17, ny - 0.10, nh)
    make_box("Bed_Slippers", (-1.95, YN - 2.30, 0.03), (0.24, 0.26, 0.06), (0.36, 0.30, 0.26, 1.0))
    make_wall_outlet("Outlet_Bed", (nx + 0.36, ROOM_D), axis='X', face_sign=-1)
    make_tube("NLamp_Cord", [(nx - 0.12, ny + 0.16, nh + 0.01), (nx - 0.12, YN - 0.01, nh - 0.02), (nx + 0.36, YN - 0.01, 0.30)], 0.004, (0.12, 0.12, 0.12, 1.0), segments=4)
    # the wall clock, stopped at four — "it is always almost 4am somewhere"
    make_wall_clock("Clock", (-0.85, YN, 2.20), frozen_hour=4, frozen_min=0, facing='-Y')


def _painting(prefix, center, w, h, facing, seed, fields=4):
    """A stretched canvas hung on (or leaned at) a wall: the canvas, its
    stretcher edge, colour fields laid on its face. `facing` is the
    direction the painted face looks: '-Y', '+Y', '-X', '+X'."""
    cx, cy, cz = center
    th = 0.035
    along_x = facing in ('-Y', '+Y')
    sgn = -1.0 if facing.startswith('-') else 1.0
    size = (w, th, h) if along_x else (th, w, h)
    make_box(f"{prefix}_Canvas", center, size, COL_STRETCHER)
    face_off = sgn * (th / 2.0 + 0.002)
    fc = (cx, cy + face_off, cz) if along_x else (cx + face_off, cy, cz)
    make_box(f"{prefix}_Ground", fc, (w - 0.02, 0.004, h - 0.02) if along_x else (0.004, w - 0.02, h - 0.02), PAINT[(seed + 3) % len(PAINT)])
    for k in range(fields):
        r = (seed * 11 + k * 7) % 13
        fw = w * (0.22 + 0.05 * (r % 4))
        fh = h * (0.25 + 0.06 * ((r * 3) % 5))
        u = (-w / 2.0 + fw / 2.0 + 0.03) + (w - fw - 0.06) * ((r * 5 % 13) / 12.0)
        v = (-h / 2.0 + fh / 2.0 + 0.03) + (h - fh - 0.06) * ((r * 7 % 13) / 12.0)
        off = sgn * (th / 2.0 + 0.005 + 0.002 * k)
        if along_x:
            make_box(f"{prefix}_Field_{k}", (cx + u, cy + off, cz + v), (fw, 0.003, fh), PAINT[(seed + k) % len(PAINT)])
        else:
            make_box(f"{prefix}_Field_{k}", (cx + off, cy + u, cz + v), (0.003, fw, fh), PAINT[(seed + k) % len(PAINT)])


def build_paintings():
    """'Paintings on walls and floors.' Hung on the walls; leaned in a
    stack on the E wall; two laid on the floor drying."""
    d = 0.035 / 2.0
    _painting("Painting_Bed", (-2.85, YN - d, 1.80), 1.30, 0.86, '-Y', 1, fields=5)
    _painting("Painting_N", (0.55, YN - d, 1.62), 0.62, 0.80, '-Y', 4)
    _painting("Painting_S_0", (-2.20, YS + d, 1.62), 0.70, 0.90, '+Y', 2)
    _painting("Painting_S_1", (-1.42, YS + d, 1.78), 0.46, 0.56, '+Y', 6, fields=3)
    _painting("Painting_BathW", (BATH_X0 - d, 1.20, 1.78), 0.80, 0.62, '-X', 5)
    _painting("Painting_E", (XE - d, 5.90, 1.85), 0.50, 0.66, '-X', 3, fields=3)
    # leaned on the E wall N of the window, faces in, stretchers to the room
    for i, (w, h) in enumerate(((0.70, 0.92), (0.60, 0.76), (0.52, 0.62))):
        x = XE - 0.03 - i * 0.045
        make_rot_box(f"Leaned_Canvas_{i}_Canvas", (x - 0.02, 5.95, h / 2.0 - 0.002), (0.035, w, h), COL_STRETCHER, roll=0.0)
        make_box(f"Leaned_Canvas_{i}_Back", (x - 0.04, 5.95, h / 2.0), (0.004, w - 0.06, h - 0.06), COL_CANVAS)
    # two on the floor by the easel, face up, drying
    for i, (cx, cy, w, h, sd) in enumerate(((1.15, 4.70, 0.70, 0.56, 7), (0.50, 4.30, 0.50, 0.40, 9))):
        make_box(f"Floor_Canvas_{i}_Canvas", (cx, cy, 0.0175), (w, h, 0.035), COL_STRETCHER)
        make_box(f"Floor_Canvas_{i}_Ground", (cx, cy, 0.037), (w - 0.02, h - 0.02, 0.004), PAINT[sd % len(PAINT)])
        for k in range(3):
            r = (sd * 5 + k * 3) % 7
            make_box(f"Floor_Canvas_{i}_Field_{k}", (cx - w * 0.25 + w * 0.25 * k, cy + h * (0.12 * (r % 3) - 0.12), 0.040 + 0.001 * k),
                     (w * 0.28, h * 0.50, 0.002), PAINT[(sd + k + 1) % len(PAINT)])


def build_window_e():
    """E wall window over the radiator, curtains half-drawn."""
    wy, wz, ww, wh = WIN_E[0], WIN_E[1], WIN_E[2], WIN_E[3]
    wc = ROOM_W / 2.0
    make_frame_ring("Win_E_Frame", (wc, wy, wz), (0.10, ww, wh), COL_FRAME, bar=0.08)
    make_box("Win_E_Glass", (wc, wy, wz), (0.02, ww - 0.16, wh - 0.16), COL_GLASS)
    make_box("Win_E_Mullion_V", (wc, wy, wz), (0.06, 0.05, wh - 0.16), COL_FRAME)
    make_box("Win_E_Mullion_H", (wc, wy, wz + 0.10), (0.06, ww - 0.16, 0.05), COL_FRAME)
    make_box("Win_E_Sill", (XE - 0.07, wy, wz - wh / 2.0 - 0.02), (0.16, ww + 0.16, 0.04), COL_FRAME)
    # rod, brackets, curtains bunched at both ends
    rx, rz = XE - 0.09, wz + wh / 2.0 + 0.14
    make_cyl("Curtain_Rod", (rx, wy, rz), 0.015, ww + 0.70, COL_STEEL, segments=6, axis='Y')
    for i, yb in enumerate((wy - ww / 2.0 - 0.25, wy + ww / 2.0 + 0.25)):
        make_box(f"Curtain_Rod_Bracket_{i}", ((rx + XE) / 2.0, yb, rz), (XE - rx, 0.025, 0.025), COL_STEEL)
    for nm, yc in (("S", wy - ww / 2.0 - 0.02), ("N", wy + ww / 2.0 + 0.02)):
        make_box(f"Curtain_{nm}", (rx, yc, (rz - 0.015 + 0.30) / 2.0), (0.12, 0.46, rz - 0.015 - 0.30), COL_CURTAIN)
    # radiator under the sill: cast-iron columns on feet, the riser pipe
    ry0, ry1 = wy - 0.62, wy + 0.62
    n = 14
    for i in range(n):
        y = ry0 + (ry1 - ry0) * (i + 0.5) / n
        make_box(f"Radiator_Column_{i}", (XE - 0.11, y, 0.42), (0.14, 0.055, 0.58), (0.56, 0.54, 0.50, 1.0))
    make_box("Radiator_Top", (XE - 0.11, wy, 0.715), (0.14, ry1 - ry0, 0.012), (0.56, 0.54, 0.50, 1.0))
    for nm, y in (("S", ry0 + 0.04), ("N", ry1 - 0.04)):
        make_box(f"Radiator_Foot_{nm}", (XE - 0.11, y, 0.065), (0.12, 0.05, 0.13), (0.46, 0.44, 0.40, 1.0))
    make_cyl("Radiator_Pipe", (XE - 0.06, ry0 - 0.06, 0.20), 0.02, 0.40, COL_STEEL, segments=6)
    make_cyl("Radiator_Valve", (XE - 0.06, ry0 - 0.06, 0.42), 0.035, 0.05, (0.66, 0.50, 0.26, 1.0), segments=8)
    make_lathe("Sill_Plant_Pot", (XE - 0.08, wy + 0.70, wz - wh / 2.0), [(0.0, 0.0), (0.06, 0.0), (0.08, 0.13), (0.0, 0.13)], (0.62, 0.36, 0.24, 1.0), segments=10)
    make_cyl("Sill_Plant_Foliage", (XE - 0.08, wy + 0.70, wz - wh / 2.0 + 0.20), 0.10, 0.14, (0.28, 0.42, 0.24, 1.0), segments=8)


def build_painting_corner():
    """By the E window: easel on a drop cloth, the elemental canvas, the
    paint table with palette and brush jar, a stool."""
    make_box("Drop_Cloth", (2.30, 3.55, 0.006), (1.90, 1.60, 0.008), COL_DROP)
    for i, (ox, oy, rr, k) in enumerate(((-0.4, 0.2, 0.10, 0), (0.3, -0.3, 0.07, 2), (0.5, 0.4, 0.05, 5), (-0.2, -0.5, 0.06, 1))):
        make_floor_stain(f"Drop_Cloth_Drip_{i}", (2.30 + ox, 3.55 + oy), radius=rr, floor_z=0.006, tint=PAINT[k])
    ex, ey = 2.30, 3.70
    for i, (lx, ly) in enumerate(((ex - 0.34, ey - 0.06), (ex + 0.34, ey - 0.06))):
        make_rot_box(f"Easel_Leg_{i}", (lx, ly, 0.86), (0.04, 0.04, 1.74), COL_WOOD_LT, roll=0.0, pitch=0.0)
    make_rot_box("Easel_Leg_Back", (ex, ey + 0.30, 0.74), (0.04, 0.04, 1.52), COL_WOOD_LT, roll=-0.24)
    make_box("Easel_Mast", (ex, ey - 0.06, 1.05), (0.05, 0.04, 2.10), COL_WOOD_LT)
    make_box("Easel_Ledge", (ex, ey - 0.12, 0.76), (0.80, 0.10, 0.04), COL_WOOD_LT)
    make_box("Easel_Brace", (ex, ey - 0.06, 0.40), (0.70, 0.03, 0.04), COL_WOOD_LT)
    make_box("Easel_Clamp", (ex, ey - 0.10, 1.83), (0.10, 0.06, 0.05), COL_WOOD_LT)
    # the painting in progress — "three elementals — water on the
    # left, fire on the right, air in the middle"
    cz, cw, chh = 1.29, 0.80, 1.02
    make_box("Easel_Canvas", (ex, ey - 0.10, cz), (cw, 0.035, chh), COL_STRETCHER)
    make_box("Easel_Canvas_Ground", (ex, ey - 0.12, cz), (cw - 0.02, 0.004, chh - 0.02), COL_CANVAS)
    make_box("Canvas_Water", (ex - 0.24, ey - 0.124, cz - 0.04), (0.20, 0.004, 0.72), (0.28, 0.40, 0.60, 1.0))
    make_box("Canvas_Air", (ex, ey - 0.126, cz + 0.04), (0.18, 0.004, 0.80), (0.82, 0.82, 0.76, 1.0))
    make_box("Canvas_Fire", (ex + 0.24, ey - 0.124, cz - 0.06), (0.20, 0.004, 0.70), (0.76, 0.32, 0.16, 1.0))
    make_box("Canvas_Fire_Core", (ex + 0.24, ey - 0.128, cz - 0.14), (0.08, 0.004, 0.30), (0.92, 0.66, 0.24, 1.0))
    make_box("Canvas_Water_Swell", (ex - 0.26, ey - 0.128, cz + 0.12), (0.10, 0.004, 0.26), (0.40, 0.56, 0.72, 1.0))
    make_stool("Easel_Stool", ex - 0.05, ey - 0.78, h=0.62, wood=COL_WOOD)
    make_box("Easel_Stool_Rag", (ex - 0.05, ey - 0.78, 0.585), (0.18, 0.14, 0.012), (0.66, 0.40, 0.30, 1.0))
    # paint table between the easel and the bathroom wall
    tx, ty = 3.30, 2.87
    make_box("PaintTable_Top", (tx, ty, 0.68), (0.62, 0.52, 0.04), COL_WOOD)
    for lx, ly in ((tx - 0.27, ty - 0.22), (tx + 0.27, ty - 0.22), (tx - 0.27, ty + 0.22), (tx + 0.27, ty + 0.22)):
        make_box(f"PaintTable_Leg_{lx:.2f}_{ly:.2f}", (lx, ly, 0.33), (0.04, 0.04, 0.66), COL_WOOD)
    make_box("PaintTable_Shelf", (tx, ty, 0.18), (0.58, 0.48, 0.02), COL_WOOD)
    for i, col in enumerate((PAINT[0], PAINT[2], PAINT[3], PAINT[1], PAINT[5])):
        make_rot_box(f"Paint_Tube_{i}", (tx - 0.22 + i * 0.07, ty + 0.15, 0.715), (0.035, 0.11, 0.03), col, yaw=0.15 * (i - 2))
    make_cyl("Palette", (tx - 0.04, ty - 0.08, 0.705), 0.15, 0.01, (0.56, 0.42, 0.26, 1.0), segments=14)
    for i, (ox, oy, k) in enumerate(((-0.08, 0.04, 0), (-0.02, 0.09, 2), (0.05, 0.07, 3), (0.08, -0.02, 1), (0.0, -0.08, 5))):
        make_cyl(f"Palette_Dab_{i}", (tx - 0.04 + ox, ty - 0.08 + oy, 0.713), 0.022, 0.006, PAINT[k], segments=8)
    make_cyl("Brush_Jar", (tx + 0.21, ty - 0.12, 0.775), 0.055, 0.15, COL_GLASS, segments=10)
    for i, (ox, oy, h) in enumerate(((-0.02, 0.0, 0.30), (0.02, 0.01, 0.26), (0.0, -0.02, 0.32), (0.01, 0.02, 0.24))):
        make_rot_box(f"Brush_{i}", (tx + 0.21 + ox, ty - 0.12 + oy, 0.70 + h / 2.0), (0.008, 0.008, h), (0.70, 0.52, 0.30, 1.0), roll=0.08 * (i - 1.5))
    make_box("Turpentine_Can", (tx + 0.20, ty + 0.12, 0.775), (0.10, 0.07, 0.15), (0.62, 0.58, 0.40, 1.0))
    make_box("Paint_Rag", (tx + 0.02, ty - 0.20, 0.705), (0.16, 0.10, 0.01), (0.70, 0.62, 0.52, 1.0))
    for i in range(3):
        make_box(f"PaintTable_Shelf_Can_{i}", (tx - 0.18 + i * 0.18, ty, 0.24), (0.11, 0.11, 0.10), PAINT[(i * 2 + 1) % len(PAINT)])


def build_dresser_desk():
    """N wall: dresser between the nightstand and the hung canvas, the
    desk under the N window."""
    dx, dy, dh = -0.70, YN - 0.25, 0.95
    make_box("Dresser", (dx, dy, dh / 2.0), (1.10, 0.48, dh), COL_WOOD)
    for i in range(3):
        z = 0.18 + i * 0.27
        for j, ox in enumerate((-0.27, 0.27)):
            make_box(f"Dresser_Drawer_{i}_{j}", (dx + ox, dy - 0.245, z), (0.50, 0.012, 0.23), COL_WOOD_LT)
            make_box(f"Dresser_Drawer_{i}_{j}_Pull", (dx + ox, dy - 0.255, z + 0.04), (0.10, 0.012, 0.015), COL_STEEL)
    # "your legal and commercial medicinal liaison": drug-rep samples
    for i, (ox, w, h, col) in enumerate(((-0.40, 0.18, 0.06, (0.86, 0.86, 0.88, 1.0)), (-0.40, 0.16, 0.05, (0.58, 0.72, 0.84, 1.0)),
                                         (-0.40, 0.17, 0.05, (0.90, 0.80, 0.40, 1.0)))):
        z = dh + sum((0.06, 0.05, 0.05)[:i]) + h / 2.0
        make_box(f"Sample_Box_{i}", (dx + ox, dy - 0.02, z), (w, 0.10, h), col)
    make_lathe("Dresser_Brush_Jar", (dx - 0.10, dy + 0.06, dh), [(0.0, 0.0), (0.05, 0.0), (0.05, 0.13), (0.0, 0.13)], (0.40, 0.46, 0.50, 0.8), segments=10)
    for i in range(3):
        make_rot_box(f"Dresser_Brush_{i}", (dx - 0.10 + 0.012 * (i - 1), dy + 0.06, dh + 0.17), (0.007, 0.007, 0.26), (0.62, 0.46, 0.28, 1.0), roll=0.10 * (i - 1))
    make_rot_box("Dresser_Photo", (dx + 0.20, dy + 0.14, dh + 0.10), (0.16, 0.02, 0.20), COL_FRAME, roll=0.0)
    make_box("Dresser_Wallet", (dx + 0.40, dy - 0.10, dh + 0.012), (0.11, 0.08, 0.024), (0.24, 0.16, 0.10, 1.0))
    make_box("Dresser_Watch", (dx + 0.30, dy - 0.12, dh + 0.008), (0.05, 0.10, 0.016), COL_STEEL)
    # desk under the N window
    kx = WIN_N[0]
    make_table("Desk", kx, YN - 0.30, w=1.30, d=0.60, h=0.75, wood=COL_WOOD, top_col=COL_WOOD_LT)
    make_chair("Desk_Chair", kx - 0.10, YN - 0.95, yaw=0.0, wood=COL_WOOD)
    make_lamp("Desk_Lamp", kx + 0.48, YN - 0.18, base_z=0.75, h=0.45, shade_col=(0.30, 0.40, 0.34, 1.0))
    make_box("Desk_Sketchbook", (kx - 0.18, YN - 0.36, 0.765), (0.36, 0.26, 0.03), (0.20, 0.18, 0.16, 1.0))
    make_box("Desk_Sketch", (kx - 0.18, YN - 0.36, 0.7815), (0.33, 0.23, 0.003), COL_CANVAS)
    make_box("Desk_Papers", (kx + 0.22, YN - 0.34, 0.755), (0.24, 0.30, 0.01), (0.92, 0.90, 0.84, 1.0))
    make_cyl("Desk_Pencil_Cup", (kx - 0.50, YN - 0.20, 0.80), 0.04, 0.10, (0.36, 0.30, 0.24, 1.0), segments=8)
    for i in range(3):
        make_rot_box(f"Desk_Pencil_{i}", (kx - 0.50 + 0.01 * (i - 1), YN - 0.20, 0.88), (0.007, 0.007, 0.17), (0.86, 0.70, 0.22, 1.0), roll=0.12 * (i - 1))
    # N window over the desk
    wx, wz, ww, wh = WIN_N[0], WIN_N[1], WIN_N[2], WIN_N[3]
    make_frame_ring("Win_N_Frame", (wx, ROOM_D, wz), (ww, 0.10, wh), COL_FRAME, bar=0.08)
    make_box("Win_N_Glass", (wx, ROOM_D, wz), (ww - 0.16, 0.02, wh - 0.16), COL_GLASS)
    make_box("Win_N_Mullion", (wx, ROOM_D, wz + 0.05), (ww - 0.16, 0.06, 0.05), COL_FRAME)
    make_box("Win_N_Sill", (wx, YN - 0.06, wz - wh / 2.0 - 0.02), (ww + 0.12, 0.14, 0.04), COL_FRAME)
    make_wall_outlet("Outlet_Desk", (wx + 0.80, ROOM_D), axis='X', face_sign=-1)


def build_fixtures():
    # bare bulb on a cord, room centre, a ceiling rose
    make_cyl("Ceiling_Rose", (-0.40, 3.40, CEIL - 0.015), 0.09, 0.03, COL_CEIL, segments=12)
    make_cyl("Bulb_Cord", (-0.40, 3.40, CEIL - 0.24), 0.006, 0.42, COL_FRAME, segments=4)
    make_cyl("Bulb_Socket", (-0.40, 3.40, CEIL - 0.48), 0.022, 0.06, (0.20, 0.18, 0.16, 1.0), segments=8)
    make_lathe("Bulb", (-0.40, 3.40, CEIL - 0.60), [(0.0, 0.0), (0.03, 0.01), (0.04, 0.05), (0.02, 0.09), (0.0, 0.09)], COL_LAMP, segments=10)
    make_cyl("Smoke_Detector", (0.40, 1.40, CEIL - 0.02), 0.07, 0.04, (0.92, 0.92, 0.90, 1.0), segments=12)


def main():
    clear_scene()
    build_shell()
    build_bathroom()
    build_entry()
    build_kitchenette()
    build_bookcase_reading()
    build_bed()
    build_paintings()
    build_window_e()
    build_painting_corner()
    build_dresser_desk()
    build_fixtures()
    # what is outside the windows (2026-10-07, _props/views.py)
    make_view("View_E", "E", ROOM_W / 2.0, WIN_E[0], kind="street", ground_z=-6.0, seed=25)   # two floors down: the street at 4 AM
    make_view("View_N", "N", ROOM_D, WIN_N[0], kind="back", ground_z=-6.0, seed=7)
    out = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)),
        "../../../assets/3d/locales/faust_apartment.glb"))
    print(f"\n[build_faust_apartment] exporting to {out}")
    export_glb(out)


if __name__ == "__main__":
    main()
