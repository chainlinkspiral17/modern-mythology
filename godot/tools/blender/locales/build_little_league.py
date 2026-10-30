"""little_league — vol 3's ballfield in Texas, August, the last game of the
season (draft 1, 2026-10-17).

The user: "go ahead and start working on backgrounds for vol 1-4 as needed."
The text never says "Little League" — "in our league there were only seven
to a game" — and dates nothing; the narrator has just turned thirteen.
"The heat of an August in Texas, well past 110 degrees."

What the scenes say, and where it is here:
  "The dugout was full because we were up to bat. I was sitting next to Dad
   and a kid named Cody. Dad gripped the bench beneath him"
                                       → the home dugout on the third-base
                                         side, its bench, the bat rack
  "The crowd bleachers held parents and younger siblings on metal steps ...
   Dirty children played at their feet with the sand and trash on pavement.
   Pink gum stuck to everything, sunflower seed shells lay spat back out"
                                       → Bleacher_*, the pavement, Gum_/Seed_
  "ambulances could be heard pulling into the parking lot every so often"
                                       → the lot past the bleachers
  "I sat on third ... the dusty home plate"                → the diamond
  "Chris stepped forward and down the mound"               → Mound, Rubber
  "I was guarding first base"          → the bags, the base paths' dust
  the convenience stand: "pictures of ice cream bars taped to it", "a large
   metal fridge", the bright pink Kid's Coppertone         → Stand_*

Blender: x east, y north, z up; Godot (x, z, -y). Home plate at the origin;
the third-base line runs west (-x), the first-base line north (+y), 60 ft
(18.3 m) between bases, the mound 46 ft out; the fence 61 m round.

DRAFT 2 (pass 157): the dugout setup moved onto the bench (it stood in the
mouth and saw a beige slab); the presets carry a sky in their env (the flat
default read as a grey wall through the post); a far treeline.
DRAFT 3 targets: the infield's grass and its dirt arc (the skin is one
square now), the outfield fence's signs and the foul poles, a scoreboard
only if the text wants one (it does not), the visitors' bleachers, the
spray bottle and Terry's clipboard as hand props at the dugout, the heat
shimmer as a mood, Deck framing.
"""
import os, sys, math
_BT = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
if _BT not in sys.path: sys.path.insert(0, _BT)
from _props.geometry import (clear_scene, make_box, make_cyl, make_chamfer_box, make_rot_box, make_prism, make_blob,
                             make_lathe, join_stock, export_glb)
from _props.vehicles import make_car
from _props.trees import make_broadleaf
from _props.detail import make_far_bands

try:
    import bpy
except ImportError:
    bpy = None

BASE = 18.3
FIRST, SECOND, THIRD = (0.0, BASE), (-BASE, BASE), (-BASE, 0.0)
MOUND = (-9.9, 9.9)
FENCE_R = 61.0
GRASS = (0.46, 0.56, 0.26, 1.0); GRASS_DRY = (0.62, 0.60, 0.34, 1.0)
DIRT = (0.70, 0.52, 0.36, 1.0); DIRT_DARK = (0.60, 0.44, 0.30, 1.0)
CHALK = (0.96, 0.96, 0.94, 1.0)
CONCRETE = (0.74, 0.72, 0.68, 1.0); PAVEMENT = (0.44, 0.44, 0.44, 1.0)
METAL = (0.70, 0.72, 0.74, 1.0); FENCE = (0.40, 0.42, 0.42, 1.0)
CINDER = (0.78, 0.76, 0.70, 1.0)


def join_named(prefix, out_name):
    if bpy is None:
        return
    objs = [o for o in bpy.data.objects if o.type == 'MESH' and o.name.startswith(prefix)]
    if len(objs) < 2:
        return
    bpy.ops.object.select_all(action='DESELECT')
    for o in objs:
        o.select_set(True)
    bpy.context.view_layer.objects.active = objs[0]
    bpy.ops.object.join()
    objs[0].name = out_name
    bpy.ops.object.select_all(action='DESELECT')


def build_field():
    # the ground: dry grass out to past the fence, the dirt square of the infield
    make_cyl("Field_Grass", (0.0, 0.0, -0.02), 90.0, 0.04, GRASS_DRY, segments=48)
    make_cyl("Outfield_Grass", (-14.0, 14.0, 0.002), 52.0, 0.004, GRASS, segments=40)
    make_box("Infield_Dirt", (-BASE / 2.0, BASE / 2.0, 0.006), (BASE + 5.0, BASE + 5.0, 0.012), DIRT)
    make_box("Home_Dirt", (0.0, 0.0, 0.008), (6.0, 6.0, 0.012), DIRT)
    make_lathe("Mound", (MOUND[0], MOUND[1], 0.0), [(0.0, 0.20), (1.0, 0.16), (2.4, 0.04), (2.7, 0.0), (0.0, 0.0)], DIRT_DARK,
               segments=20)
    make_rot_box("Mound_Rubber", (MOUND[0], MOUND[1], 0.205), (0.61, 0.15, 0.02), CHALK, yaw=math.pi / 4.0)
    # the bags and home plate
    for nm, (x, y) in (("First", FIRST), ("Second", SECOND), ("Third", THIRD)):
        make_rot_box(f"Base_{nm}", (x, y, 0.04), (0.38, 0.38, 0.08), CHALK, yaw=math.pi / 4.0 if nm == "Second" else 0.0)
    make_prism("Home_Plate", (0.0, 0.0, 0.016),
               [(0.0, -0.31), (0.31, 0.0), (0.31, 0.22), (-0.31, 0.22), (-0.31, 0.0)], 0.02, CHALK, axis="Z",
               yaw=-math.pi / 4.0)
    # chalk: the foul lines out to the fence, the batter's boxes, the base paths' dust
    make_box("Foul_Line_3B", (-FENCE_R / 2.0, 0.0, 0.016), (FENCE_R, 0.08, 0.006), CHALK)
    make_box("Foul_Line_1B", (0.0, FENCE_R / 2.0, 0.016), (0.08, FENCE_R, 0.006), CHALK)
    for s in (-1, 1):
        cx, cy = (s * 0.9 + 0.0, -s * 0.9 + 0.0)
        for k, (dx, dy, w, h) in enumerate(((0.0, 0.6, 1.0, 0.05), (0.0, -0.6, 1.0, 0.05), (0.5, 0.0, 0.05, 1.2), (-0.5, 0.0, 0.05, 1.2))):
            make_rot_box(f"Batter_Box_{s:+d}_{k}", (cx + dx * 0.707 - dy * 0.707, cy + dx * 0.707 + dy * 0.707, 0.016), (w, h, 0.006),
                         CHALK, yaw=math.pi / 4.0)
    # the outfield fence: chain-link panels in a quarter arc, a yellow top rail
    n = 24
    for k in range(n):
        a0 = math.pi / 2.0 + (k / n) * (math.pi / 2.0)
        a1 = math.pi / 2.0 + ((k + 1) / n) * (math.pi / 2.0)
        am = (a0 + a1) / 2.0
        x, y = FENCE_R * math.cos(am), FENCE_R * math.sin(am)
        L = 2.0 * FENCE_R * math.sin((a1 - a0) / 2.0)
        make_rot_box(f"Fence_Out_Panel_{k}", (x, y, 0.9), (L, 0.04, 1.8), FENCE, yaw=am + math.pi / 2.0)
        make_rot_box(f"Fence_Out_Rail_{k}", (x, y, 1.82), (L, 0.07, 0.07), (0.92, 0.80, 0.20, 1.0), yaw=am + math.pi / 2.0)
        make_cyl(f"Fence_Out_Post_{k}", (FENCE_R * math.cos(a0), FENCE_R * math.sin(a0), 0.92), 0.04, 1.84, METAL, segments=6)
    # the backstop behind home: three tall chain-link panels round the plate,
    # each its frame and its wires (an opaque panel read as a wall)
    for k, (cx, cy, yaw) in enumerate(((5.2, -1.0, math.pi / 2.0 - 0.15), (3.0, -3.6, math.pi / 4.0), (0.4, -5.6, 0.15))):
        c, s_ = math.cos(yaw), math.sin(yaw)
        make_rot_box(f"Backstop_Rail_{k}", (cx, cy, 4.82), (4.0, 0.08, 0.08), METAL, yaw=yaw)
        make_rot_box(f"Backstop_Kick_{k}", (cx, cy, 0.30), (4.0, 0.06, 0.60), (0.36, 0.36, 0.36, 1.0), yaw=yaw)
        for j in range(14):
            z = 0.75 + j * 0.30
            make_rot_box(f"Backstop_Wire_H_{k}_{j}", (cx, cy, z), (4.0, 0.012, 0.012), (0.56, 0.58, 0.58, 1.0), yaw=yaw)
        for j in range(9):
            u = -1.8 + j * 0.45
            make_rot_box(f"Backstop_Wire_V_{k}_{j}", (cx + u * c, cy + u * s_, 2.55), (0.012, 0.012, 4.50), (0.56, 0.58, 0.58, 1.0), yaw=yaw)
    for k, (x, y) in enumerate(((6.1, 1.2), (4.6, -2.6), (1.8, -5.2), (-1.6, -6.1))):
        make_cyl(f"Backstop_Post_{k}", (x, y, 2.42), 0.05, 4.84, METAL, segments=6)


def build_dugout():
    """The home dugout on the third-base side: a cinder-block shell, its roof,
    the bench along the back wall, the chain-link front, the mouth at the
    home-plate end."""
    x0, x1, y0, y1, h = -14.0, -6.0, -8.6, -6.0, 2.2
    cx, cy = (x0 + x1) / 2.0, (y0 + y1) / 2.0
    make_box("Dugout_Floor", (cx, cy, 0.01), (x1 - x0, y1 - y0, 0.02), CONCRETE)
    make_box("Dugout_Wall_Back", (cx, y0 - 0.10, h / 2.0), (x1 - x0 + 0.4, 0.2, h), CINDER)
    make_box("Dugout_Wall_W", (x0 - 0.10, cy, h / 2.0), (0.2, y1 - y0, h), CINDER)
    make_box("Dugout_Wall_E", (x1 + 0.10, y0 + 0.6, h / 2.0), (0.2, 1.2, h), CINDER)
    make_box("Dugout_Roof", (cx, cy, h + 0.08), (x1 - x0 + 0.6, y1 - y0 + 0.6, 0.16), (0.56, 0.56, 0.58, 1.0))
    make_box("Dugout_Front_Wall", (cx - 0.5, y1, 0.4), (x1 - x0 - 1.0, 0.2, 0.8), CINDER)
    for k in range(9):
        make_cyl(f"Dugout_Front_Post_{k}", (x0 + 0.1 + k * 0.85, y1, 1.5), 0.03, 1.4, METAL, segments=6)
    make_box("Dugout_Front_Rail", (cx - 0.5, y1, 2.18), (x1 - x0 - 1.0, 0.06, 0.06), METAL)
    # the front's chain link as its wires (an opaque panel would hide the field)
    for k, z in enumerate((1.20, 1.60, 2.00)):
        make_box(f"Dugout_Front_Wire_{k}", (cx - 0.5, y1 + 0.035, z), (x1 - x0 - 1.1, 0.008, 0.008), (0.50, 0.52, 0.52, 1.0))
    # the bench, full: gloves, a water jug, hats on it
    make_box("Dugout_Bench_Seat", (cx, y0 + 0.35, 0.44), (x1 - x0 - 0.6, 0.36, 0.05), (0.62, 0.48, 0.30, 1.0))
    for k in range(5):
        make_box(f"Dugout_Bench_Leg_{k}", (x0 + 0.6 + k * 1.7, y0 + 0.35, 0.21), (0.06, 0.30, 0.42), METAL)
    for k, x in enumerate((-12.8, -11.2, -9.4, -7.6)):
        make_chamfer_box(f"Glove_Bench_{k}", (x, y0 + 0.35, 0.51), (0.24, 0.20, 0.08), ((0.46, 0.30, 0.18, 1.0), (0.14, 0.12, 0.12, 1.0))[k % 2],
                         chamfer=0.03)
    make_cyl("Water_Jug", (x0 + 0.5, y0 + 0.35, 0.62), 0.16, 0.30, (0.86, 0.30, 0.20, 1.0), segments=12)
    make_cyl("Water_Jug_Lid", (x0 + 0.5, y0 + 0.35, 0.78), 0.12, 0.03, CHALK, segments=12)
    # the bat rack on the back wall, bats and helmets
    make_box("Bat_Rack", (x1 - 1.4, y0 + 0.06, 1.2), (1.2, 0.10, 0.08), (0.62, 0.48, 0.30, 1.0))
    for k in range(6):
        make_rot_box(f"Bat_{k}", (x1 - 1.9 + k * 0.2, y0 + 0.12, 0.72), (0.05, 0.05, 0.80), ((0.70, 0.56, 0.38, 1.0), METAL)[k % 2], roll=0.10)
    for k in range(3):
        make_blob(f"Helmet_{k}", (x1 - 2.8 + k * 0.4, y0 + 0.35, 0.56), 0.12, (0.10, 0.20, 0.50, 1.0), noise=0.0, seed=k, squash=0.85)
    # the on-deck: a bat leaning at the dugout's mouth (Chris warming up outside it)
    make_rot_box("Bat_OnDeck", (x1 + 0.45, y1 + 0.6, 0.42), (0.05, 0.05, 0.84), (0.70, 0.56, 0.38, 1.0), pitch=0.25)
    make_box("OnDeck_Circle", (x1 + 2.5, y1 + 1.8, 0.004), (1.5, 1.5, 0.006), DIRT_DARK)


def build_crowd_side():
    """Behind home and down the first-base side: the metal bleachers on
    pavement, the gum and the seeds, the convenience stand, the lot."""
    make_box("Pavement", (8.0, -16.0, 0.0), (36.0, 16.0, 0.02), PAVEMENT)
    # the bleachers: four metal steps rising south, facing the field
    bx0, bx1 = 2.0, 14.0
    for k in range(4):
        y = -8.4 - k * 0.7
        z = 0.42 + k * 0.40
        make_box(f"Bleacher_Seat_{k}", ((bx0 + bx1) / 2.0, y, z), (bx1 - bx0, 0.30, 0.04), METAL)
        make_box(f"Bleacher_Foot_{k}", ((bx0 + bx1) / 2.0, y + 0.32, z - 0.22), (bx1 - bx0, 0.28, 0.03), METAL)
    for k in range(5):
        x = bx0 + 0.2 + k * (bx1 - bx0 - 0.4) / 4.0
        make_rot_box(f"Bleacher_Frame_{k}", (x, -9.45, 1.08), (0.06, 0.06, 2.6), (0.56, 0.58, 0.60, 1.0), roll=-0.62)
        for r in range(4):        # a leg under each step, seat and footboard on it
            zr = 0.42 + r * 0.40
            make_box(f"Bleacher_Frame_{k}_Leg_{r}", (x, -8.4 - r * 0.7 + 0.155, (zr - 0.02) / 2.0), (0.06, 0.61, zr - 0.02), (0.56, 0.58, 0.60, 1.0))
        make_box(f"Bleacher_Frame_Leg_{k}", (x, -10.7, 0.80), (0.06, 0.06, 1.60), (0.56, 0.58, 0.60, 1.0))
    # the pink gum and the spat shells on the pavement round them
    for k in range(40):
        x = bx0 + (k * 37 % 120) / 10.0
        y = -7.6 - (k * 53 % 50) / 10.0
        if k % 3 == 0:
            make_cyl(f"Gum_Stock_{k}", (x, y, 0.012), 0.025, 0.004, (0.94, 0.52, 0.66, 1.0), segments=6)
        else:
            make_rot_box(f"Seed_Stock_{k}", (x, y, 0.012), (0.018, 0.008, 0.004), (0.30, 0.28, 0.26, 1.0), yaw=k * 0.7)
    make_cyl("Trash_Barrel", (bx0 - 0.8, -9.0, 0.45), 0.30, 0.90, (0.30, 0.40, 0.30, 1.0), segments=12)
    # the convenience stand: a cinder-block shack, its serving window on the
    # N face, the pictures of ice cream bars taped to the counter, the fridge
    sx0, sx1, sy0, sy1, sh = 12.0, 16.0, -16.0, -13.0, 2.8
    scx, scy = (sx0 + sx1) / 2.0, (sy0 + sy1) / 2.0
    make_box("Stand_Wall_S", (scx, sy0, sh / 2.0), (sx1 - sx0, 0.2, sh), CINDER)
    make_box("Stand_Wall_W", (sx0, scy, sh / 2.0), (0.2, sy1 - sy0, sh), CINDER)
    make_box("Stand_Wall_E", (sx1, scy, sh / 2.0), (0.2, sy1 - sy0, sh), CINDER)
    make_box("Stand_Wall_N_Low", (scx, sy1, 0.5), (sx1 - sx0, 0.2, 1.0), CINDER)
    make_box("Stand_Wall_N_High", (scx, sy1, 2.45), (sx1 - sx0, 0.2, 0.7), CINDER)
    for s in (-1, 1):
        make_box(f"Stand_Window_Jamb_{s:+d}", (scx + s * 1.85, sy1, 1.55), (0.3, 0.2, 1.1), CINDER)
    make_box("Stand_Roof", (scx, scy, sh + 0.06), (sx1 - sx0 + 0.6, sy1 - sy0 + 0.8, 0.12), (0.62, 0.30, 0.24, 1.0))
    make_box("Stand_Floor", (scx, scy, 0.01), (sx1 - sx0, sy1 - sy0, 0.02), CONCRETE)
    make_box("Stand_Counter", (scx, sy1 + 0.12, 1.02), (3.4, 0.44, 0.05), (0.86, 0.84, 0.80, 1.0))
    for k in range(5):
        make_box(f"Stand_IceCream_Pic_{k}", (scx - 1.4 + k * 0.7, sy1 + 0.11, 0.80), (0.24, 0.004, 0.30),
                 ((0.90, 0.80, 0.50, 1.0), (0.60, 0.36, 0.24, 1.0), (0.94, 0.62, 0.70, 1.0), (0.40, 0.60, 0.86, 1.0), (0.96, 0.92, 0.80, 1.0))[k])
    make_box("Stand_Fridge", (sx0 + 0.6, sy0 + 0.5, 0.95), (0.80, 0.70, 1.90), METAL)
    make_box("Stand_Fridge_Handle", (sx0 + 0.95, sy0 + 0.86, 1.1), (0.03, 0.03, 0.50), (0.40, 0.40, 0.42, 1.0))
    make_box("Stand_Fryer", (sx1 - 0.6, sy0 + 0.45, 0.48), (0.70, 0.60, 0.96), (0.60, 0.60, 0.62, 1.0))
    make_box("Stand_Back_Shelf", (scx, sy0 + 0.25, 1.40), (1.6, 0.30, 0.03), (0.62, 0.48, 0.30, 1.0))
    make_cyl("Coppertone_Pink", (scx - 0.4, sy0 + 0.25, 1.49), 0.035, 0.16, (0.96, 0.46, 0.66, 1.0), segments=10)
    make_cyl("Soda_64oz", (scx + 0.6, sy1 + 0.12, 1.16), 0.065, 0.24, (0.90, 0.20, 0.18, 1.0), segments=12)
    make_cyl("Soda_64oz_Straw", (scx + 0.62, sy1 + 0.12, 1.33), 0.006, 0.12, CHALK, segments=6)
    make_box("Onion_Rings_Tray", (scx - 0.2, sy1 + 0.12, 1.06), (0.26, 0.18, 0.03), (0.92, 0.88, 0.80, 1.0))
    for k in range(4):
        make_cyl(f"Onion_Ring_{k}", (scx - 0.28 + k * 0.05, sy1 + 0.12, 1.085), 0.035, 0.02, (0.80, 0.56, 0.26, 1.0), segments=10)
    # the parking lot past the stand: cars in the sun, a tree or two
    make_box("Lot", (0.0, -32.0, 0.0), (60.0, 18.0, 0.02), (0.36, 0.36, 0.36, 1.0))
    for k in range(9):
        make_box(f"Lot_Stripe_{k}", (-16.0 + k * 4.0, -30.0, 0.012), (0.10, 5.0, 0.004), CHALK)
    cols = [(0.70, 0.12, 0.10, 1.0), (0.86, 0.86, 0.84, 1.0), (0.20, 0.30, 0.50, 1.0), (0.30, 0.30, 0.32, 1.0), (0.60, 0.56, 0.44, 1.0)]
    for k in range(7):
        make_car(f"Lot_Car_{k}", -14.0 + k * 4.0 + 2.0, -30.0, 4.4, cols[k % 5], pickup=(k % 3 == 0), along="Y")
    for k, (x, y) in enumerate(((-26.0, -24.0), (22.0, -26.0), (-30.0, 6.0))):
        make_broadleaf(f"Tree_{k}", x, y, 7.0, (0.30, 0.42, 0.22, 1.0), (0.34, 0.26, 0.20, 1.0))
    # pass 157: the ground ended at the grass disc's edge against a bare sky;
    # a far treeline round the field (the lot's road side open)
    make_far_bands("Treeline", (0.30, 0.40, 0.24, 1.0), [(110.0, 150.0, 9.0, 0.92), (160.0, 220.0, 12.0, 0.78)], sides="NEW",
                   cx=-10.0, cy=10.0)


def build_visitors():
    """The visitors' dugout down the first-base line, for the far side of the frame."""
    x0, x1, y0, y1, h = 6.0, 8.6, 6.0, 14.0, 2.2
    cx, cy = (x0 + x1) / 2.0, (y0 + y1) / 2.0
    make_box("Vis_Dugout_Floor", (cx, cy, 0.01), (x1 - x0, y1 - y0, 0.02), CONCRETE)
    make_box("Vis_Dugout_Wall_Back", (x1 + 0.10, cy, h / 2.0), (0.2, y1 - y0 + 0.4, h), CINDER)
    make_box("Vis_Dugout_Wall_N", (cx, y1 + 0.10, h / 2.0), (x1 - x0, 0.2, h), CINDER)
    make_box("Vis_Dugout_Wall_S", (cx, y0 - 0.10, h / 2.0), (x1 - x0, 0.2, h), CINDER)
    make_box("Vis_Dugout_Roof", (cx, cy, h + 0.08), (x1 - x0 + 0.6, y1 - y0 + 0.6, 0.16), (0.56, 0.56, 0.58, 1.0))
    make_box("Vis_Dugout_Front_Wall", (x0, cy, 0.5), (0.2, y1 - y0 - 1.0, 1.0), CINDER)
    make_box("Vis_Dugout_Bench", (x1 - 0.35, cy, 0.44), (0.36, y1 - y0 - 0.6, 0.05), (0.62, 0.48, 0.30, 1.0))
    for k in range(5):
        make_box(f"Vis_Dugout_Bench_Leg_{k}", (x1 - 0.35, y0 + 0.6 + k * 1.7, 0.21), (0.30, 0.06, 0.42), METAL)


def build_game_2026_10():
    """DRAFT 3 (2026-10-30): the field was empty in every frame — "half the
    people in attendance" hollering at nobody. Two states of the same game,
    stripped per preset (Background3D `strip`):
      Game_Bat_*   — "we were up to bat": the visitors in the field (grey and
                     blue), Chris at the plate ("All Chris had to do at bat"),
                     their catcher, the umpire  → dugout, third_base, stand
      Game_Field_* — the narrator's team in the field (white and red), Chris
                     on the mound "pulling his glove and throwing arm to his
                     chest", our catcher, a visiting batter, the umpire; no one
                     at first or second (the narrator's own bags: the camera)
                                                 → mound, first_base, home_plate
    And the crowd on the bleachers, standing, both states.
    Draft 4 targets: a catcher's crouch (the figures only stand), the bat
    and gloves as props in hand, the coaches at the boxes, dust kicked up."""
    from _props.figures import make_standing_figure
    home_top, home_pants = (0.94, 0.94, 0.92, 1.0), (0.94, 0.94, 0.92, 1.0)
    vis_top, vis_pants = (0.56, 0.58, 0.60, 1.0), (0.56, 0.58, 0.60, 1.0)
    cap_home, cap_vis = (0.70, 0.14, 0.12, 1.0), (0.16, 0.24, 0.46, 1.0)
    ump = (0.12, 0.12, 0.14, 1.0)

    def face_home(x, y):
        return math.atan2(-x, -y)

    def player(nm, x, y, top, pants, cap, h=1.56, heading=None, arms="down"):
        hd = face_home(x, y) if heading is None else heading
        make_standing_figure(nm, x, y, heading=hd, h=h, coat=top, pants=pants, hair=cap, arms=arms)

    fielders = {"P": (-9.9, 9.9), "C": (0.75, -0.75), "SS": (-22.0, 11.0), "3B": (-19.5, 2.4),
                "LF": (-38.0, 16.0), "CF": (-34.0, 34.0), "RF": (-16.0, 38.0), "1B": (-1.4, 19.2), "2B": (-9.0, 22.6)}
    # -- we're up to bat: the visitors field all nine; Chris bats --
    for pos, (x, y) in fielders.items():
        player(f"Game_Bat_Vis_{pos}", x, y, vis_top, vis_pants, cap_vis, h=(1.10 if pos == "C" else 1.56),
               arms=("front" if pos in ("P", "C", "SS", "3B", "1B", "2B") else "down"))
    player("Game_Bat_Chris", -0.75, -0.75, home_top, home_pants, cap_home, h=1.60, heading=math.pi / 4.0, arms="front")
    make_rot_box("Game_Bat_Chris_Bat", (-0.62, -0.88, 1.55), (0.06, 0.06, 0.80), (0.70, 0.56, 0.36, 1.0), roll=0.5, pitch=-0.3)
    player("Game_Bat_Umpire", 1.45, -1.45, ump, ump, ump, h=1.80, arms="front")
    # -- we're in the field: Chris pitching, our catcher, their batter --
    for pos in ("P", "C", "SS", "3B", "LF", "CF", "RF"):
        x, y = fielders[pos]
        player(f"Game_Field_Home_{pos}", x, y, home_top, home_pants, cap_home, h=(1.10 if pos == "C" else (1.62 if pos == "P" else 1.56)),
               arms=("front" if pos in ("P", "C", "SS", "3B") else "down"))
    player("Game_Field_Vis_Batter", -0.75, -0.75, vis_top, vis_pants, cap_vis, h=1.58, heading=math.pi / 4.0, arms="front")
    make_rot_box("Game_Field_Vis_Bat", (-0.62, -0.88, 1.55), (0.06, 0.06, 0.80), (0.66, 0.54, 0.36, 1.0), roll=0.5, pitch=-0.3)
    player("Game_Field_Umpire", 1.45, -1.45, ump, ump, ump, h=1.80, arms="front")
    # -- the crowd on the bleachers (seats z 0.42 + k * 0.40 at y -8.4 - k * 0.7), standing to holler --
    import random
    rnd = random.Random(1311)
    shirts = ((0.86, 0.30, 0.26, 1.0), (0.30, 0.46, 0.66, 1.0), (0.92, 0.90, 0.80, 1.0), (0.40, 0.54, 0.34, 1.0),
              (0.92, 0.74, 0.30, 1.0), (0.60, 0.40, 0.56, 1.0), (0.24, 0.24, 0.26, 1.0))
    n = 0
    for k in range(4):
        for j in range(7):
            if rnd.random() < 0.35:
                continue
            x = 2.8 + j * 1.6 + rnd.uniform(-0.3, 0.3)
            kid = rnd.random() < 0.3
            make_standing_figure(f"Crowd_{n}", x, -8.4 - k * 0.7, heading=rnd.uniform(-0.3, 0.3), h=(1.20 if kid else rnd.uniform(1.62, 1.84)),
                                 coat=shirts[rnd.randrange(len(shirts))], pants=(0.30, 0.32, 0.40, 1.0) if rnd.random() < 0.6 else (0.70, 0.62, 0.50, 1.0),
                                 arms=("down", "folded", "front")[rnd.randrange(3)], z0=0.42 + k * 0.40 + 0.02)
            n += 1
    # dirty children at their feet on the pavement
    for i, (x, y) in enumerate(((3.4, -7.4), (6.2, -7.2), (11.0, -7.6))):
        make_standing_figure(f"Crowd_Kid_{i}", x, y, heading=rnd.uniform(0, 6.28), h=1.0, coat=shirts[(i * 3) % len(shirts)],
                             pants=(0.30, 0.32, 0.40, 1.0))


def main():
    clear_scene()
    build_field()
    build_dugout()
    build_crowd_side()
    build_visitors()
    build_game_2026_10()
    try:
        join_stock()
        join_named("Fence_Out_", "Fence_Outfield")
        join_named("Backstop_Wire_", "Backstop_Wires")
    except Exception as _e:
        print("[join] skipped:", _e)
    out = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                        "../../../assets/3d/locales/little_league.glb"))
    print(f"\n[build_little_league] exporting to {out}")
    export_glb(out)


if __name__ == "__main__":
    main()
