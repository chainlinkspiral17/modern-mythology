"""sea_cave — vol 2's coast: Julie's sea cave, and the riverbed sand of
Charles's dig (draft 1, 2026-10-18).

The user: "go ahead and start working on backgrounds for vol 1-4 as needed."
THE CAVE (origin, its mouth to the south) — vol2_ch9: reached from "Woods
by the shore" by "the dirt path", across the beach. Inside, "sharp volcanic
rock" slick with "soft green scum algae"; "Way in the back" a "small spout"
that pumps up sea water, the narrow hole the later scenes call "the
sinkhole", draining "under rock". Far enough back "the tide couldn't drag
me free", yet "The cave filled up with water" at high tide. Three visits:
  flotsam    first light, "white blue", the sun not yet up (cave_dawn)
  art_class  low tide, the shells and husks at the sinkhole (cave_low_tide)
  truck      the tide coming in, the body gone (cave_tide_in)
The sea's level and what lies at the hole are per view (`__<preset>`).
THE RIVERBED (x 80..) — vol2_ch5: sand "near a riverbed off the way of the
roads and beaches", a bungalow somewhere near, and the hole where a red
1969 Mercedes convertible came out of the sand. Plain, empty, big.

Blender: x east, y north, z up; Godot (x, z, -y).

DRAFT 2 targets: the shore woods and the dirt path; other caves along the
beach; the cave's rock as a sculpted shell rather than lumps; whether the
body shows in the dawn view (the author's call); the riverbed's car whole
in a separate view; Deck framing.

DRAFT 2 (2026-11-02, the riverbed): the pit dug out round the whole car (a
week's work), the car modelled (profile body, canvas top, chrome, wheels),
the channel cut into the sand, the sky card gone, dunes to the west.
DRAFT 3 targets: meander the channel and run it under the north dunes; the
week's kit (wheelbarrow, bucket, tarp); the bungalow's porch and window;
sun shadows to seat the car in its pit.
"""
import os, sys, math
_BT = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
if _BT not in sys.path: sys.path.insert(0, _BT)
from _props.geometry import (clear_scene, make_box, make_cyl, make_blob, make_rot_box, make_chamfer_box, make_heightfield, make_prism,
                             make_tube, rolling_heights, join_stock, export_glb)

try:
    import bpy
except ImportError:
    bpy = None

BASALT = (0.14, 0.13, 0.13, 1.0); BASALT_2 = (0.20, 0.19, 0.18, 1.0)
ALGAE = (0.22, 0.32, 0.16, 1.0)
SAND = (0.70, 0.64, 0.52, 1.0); WET_SAND = (0.52, 0.48, 0.40, 1.0)
SEA = (0.30, 0.42, 0.46, 1.0)
CL, CW, CH = 18.0, 6.0, 4.2          # the cave: 18 m deep from its mouth, 6 wide, 4.2 high
HOLE = (0.4, CL - 1.4)


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


def build_cave():
    """A long chamber under the headland: a rock floor, walls and roof of
    rough basalt lumps over a solid shell, the mouth open to the beach."""
    # the shell (keeps every view enclosed) and the floor
    make_box("Cave_Floor", (0.0, CL / 2.0, -0.10), (CW + 2.0, CL, 0.20), BASALT)
    for s in (-1, 1):
        make_box(f"Cave_Rock_Shell_Wall_{s:+d}", (s * (CW / 2.0 + 0.6), CL / 2.0, CH / 2.0), (1.2, CL, CH + 0.4), BASALT)
    make_box("Cave_Rock_Shell_Roof", (0.0, CL / 2.0, CH + 0.4), (CW + 2.4, CL, 0.8), BASALT)
    make_box("Cave_Rock_Shell_Back", (0.0, CL + 0.5, CH / 2.0), (CW + 2.4, 1.0, CH + 0.4), BASALT)
    # the headland above and round the mouth
    make_box("Headland_Rock_Mass", (0.0, CL / 2.0 + 2.0, CH + 4.0), (40.0, CL + 8.0, 8.0), (0.26, 0.24, 0.22, 1.0))
    for s in (-1, 1):
        make_box(f"Headland_Rock_Flank_{s:+d}", (s * 12.5, CL / 2.0, CH / 2.0), (19.0, CL, CH), (0.24, 0.22, 0.20, 1.0))
    # the sharp lumps lining walls and roof, narrowing toward the back
    k = 0
    for j in range(10):
        y = 0.8 + j * 1.75
        narrow = j / 9.0 * 0.9
        for s in (-1, 1):
            for z in (0.5, 1.6, 2.8):
                make_blob(f"Rock_Stock_{k}", (s * (CW / 2.0 - 0.15 - narrow), y + (k % 3) * 0.3, z), 0.8 + (k % 3) * 0.15,
                          (BASALT, BASALT_2)[k % 2], noise=0.35, seed=k)
                k += 1
        for x in (-1.6, 0.0, 1.6):
            make_blob(f"Rock_Stock_{k}", (x * (1.0 - narrow * 0.5), y, CH - 0.15 - narrow * 0.8), 0.9, (BASALT, BASALT_2)[k % 2],
                      noise=0.35, seed=k)
            k += 1
    # the floor: rough rock, the algae slick in sheets
    for j in range(14):
        for i in range(4):
            x, y = -2.0 + i * 1.3 + (j % 2) * 0.4, 1.0 + j * 1.2
            make_blob(f"Floor_Rock_Stock_{j}_{i}", (x, y, 0.02), 0.45, BASALT_2, noise=0.30, seed=j * 4 + i, squash=0.30)
    for j in range(9):
        make_box(f"Seaweed_Algae_Stock_{j}", (-1.4 + (j % 3) * 1.4, 4.0 + j * 1.3, 0.006), (1.2, 1.0, 0.012), ALGAE)
    # the spout / sinkhole way in the back: a ring of sharp rock round a black throat
    hx, hy = HOLE
    make_cyl("Sinkhole_Throat", (hx, hy, 0.005), 0.45, 0.02, (0.02, 0.02, 0.03, 1.0), segments=16)
    for k in range(8):
        a = k * math.pi / 4.0
        make_blob(f"Sinkhole_Lip_{k}", (hx + math.cos(a) * 0.62, hy + math.sin(a) * 0.62, 0.12), 0.26, BASALT, noise=0.40, seed=50 + k)
    make_cyl("Spout_Water__cave_dawn__cave_low_tide", (hx, hy, 0.02), 0.40, 0.02, (0.40, 0.56, 0.60, 1.0), segments=16)
    # art class: the shells and husks dropped at the sinkhole
    for k in range(7):
        a = 1.4 + k * 0.62          # round the lip on the cave's open side
        make_blob(f"Husk_{k}__cave_low_tide", (hx + math.cos(a) * 0.80, hy + math.sin(a) * 0.70, 0.16), 0.07,
                  ((0.80, 0.76, 0.66, 1.0), (0.64, 0.30, 0.20, 1.0), (0.86, 0.82, 0.74, 1.0))[k % 3], noise=0.2, seed=70 + k, squash=0.5)
    # the tide coming in (truck): the sea over the floor, foam at the rock
    make_box("Tide_In_Water__cave_tide_in", (0.0, CL / 2.0 - 1.0, 0.16), (CW, CL - 2.0, 0.02), (0.28, 0.40, 0.44, 1.0))
    for k in range(10):
        make_blob(f"Tide_Foam_{k}__cave_tide_in", (-2.4 + (k % 5) * 1.2, 2.0 + k * 1.4, 0.18), 0.22, (0.86, 0.90, 0.90, 1.0),
                  noise=0.3, seed=90 + k, squash=0.25)
    # the beach outside, the sea, and the sky card per view
    make_box("Beach_Sand", (0.0, -10.0, -0.05), (60.0, 20.0, 0.10), SAND)
    make_box("Beach_Wet", (0.0, -18.0, -0.03), (60.0, 6.0, 0.04), WET_SAND)
    make_box("Sea_Low_Water__cave_dawn__cave_low_tide", (0.0, -60.0, -0.10), (120.0, 78.0, 0.04), SEA)
    make_box("Sea_High_Water__cave_tide_in", (0.0, -50.0, 0.10), (120.0, 98.0, 0.04), (0.26, 0.38, 0.42, 1.0))
    make_box("Sky_Dawn__cave_dawn", (0.0, -120.0, 25.0), (260.0, 0.2, 60.0), (0.82, 0.88, 0.94, 1.0))
    make_box("Sky_Grey__cave_low_tide__cave_tide_in", (0.0, -120.0, 25.0), (260.0, 0.2, 60.0), (0.70, 0.72, 0.74, 1.0))
    for k in range(6):
        make_blob(f"Beach_Rock_{k}", (-14.0 + k * 5.6, -6.0 - (k % 3) * 3.0, 0.3), 0.9 + (k % 2) * 0.5, BASALT_2, noise=0.35, seed=110 + k)


def build_riverbed():
    """Charles's ground: open sand by a riverbed, the bungalow far off, the
    pit with a sliver of red bodywork."""
    ox, oy = 200.0, 0.0
    # the flat sand round the dig (a real hole where the pit is), the dunes
    # rolling up beyond it; their first rows ramp from flat so no step shows.
    # (2026-11-02, draft 2) "Charles excavated the machine by himself over
    # the course of a week": the pit is dug out round the whole car now, its
    # sand walls at the angle sand stands at, a ramp cut up the west end, the
    # spoil thrown back in heaps, the car down on the floor with its top up
    px, py = ox - 4.0, oy + 6.0
    FL, FW, DEPTH, SLOPE = 3.2, 1.7, 1.0, 0.70          # floor half-sizes, depth, wall run
    RAMP = 2.6
    hx0, hx1, hy0, hy1 = px - FL - RAMP, px + FL + SLOPE, py - FW - SLOPE, py + FW + SLOPE
    x0, x1, y0, y1 = ox - 80.0, ox + 80.0, oy - 60.0, oy + 60.0
    # (draft 2) the river channel is CUT into the sand: the ground stops at
    # its banks, which slope down to wet sand and a thread of water (it sat
    # 10 cm proud of the sand, a ridge across the view)
    CX, CH, CD = ox + 10.0, 3.0, 0.45                 # channel centre x, half-width at the rim, depth
    for nm, (ax, bx_, ay, by_) in {"S": (x0, x1, y0, hy0), "N": (x0, x1, hy1, y1),
                                   "W": (x0, hx0, hy0, hy1), "E": (hx1, x1, hy0, hy1)}.items():
        for part, (qa, qb) in (("", (ax, min(bx_, CX - CH))), ("_Far", (max(ax, CX + CH), bx_))):
            if qb - qa > 0.01:
                make_box(f"Riverbed_Flat_Sand_Ground_{nm}{part}", ((qa + qb) / 2.0, (ay + by_) / 2.0, -0.10), (qb - qa, by_ - ay, 0.20), SAND)
    hf = rolling_heights(20, 32, 0.8, seed=7, base=0.0, bumps=4)
    hf = [[z * min(1.0, r / 4.0) for z in row] for r, row in enumerate(hf)]
    make_heightfield("Riverbed_Dunes_Ground", (x0, y1, 0.0), 5.0, hf, SAND)
    make_box("Riverbed_Channel", (CX, oy, -CD - 0.10), (2.0 * CH - 1.4, 120.0, 0.20), WET_SAND)
    bank = math.atan2(0.7, CD)
    for s in (-1, 1):
        make_rot_box(f"Riverbed_Channel_Bank_{'E' if s > 0 else 'W'}", (CX + s * (CH - 0.35), oy, -CD / 2.0),
                     (0.10, 120.0, math.hypot(0.7, CD)), WET_SAND, pitch=s * bank)
    make_box("Riverbed_Water", (CX, oy, -CD + 0.03), (2.2, 120.0, 0.02), (0.40, 0.48, 0.48, 1.0))
    for k in range(12):
        make_blob(f"River_Stone_{k}", (CX - 1.8 + (k % 3) * 1.8, oy - 30.0 + k * 5.0, -CD + 0.08), 0.25, (0.50, 0.48, 0.44, 1.0),
                  noise=0.3, seed=130 + k, squash=0.5)
    # the dig: the floor, three sloped walls and the ramp, all wet sand
    zf = -DEPTH
    make_box("Dig_Pit_Floor", (px, py, zf - 0.05), (2.0 * FL, 2.0 * FW, 0.10), WET_SAND)
    tilt = math.atan2(SLOPE, DEPTH)
    slant = math.hypot(SLOPE, DEPTH)
    make_rot_box("Dig_Pit_Wall_E", (px + FL + SLOPE / 2.0 + 0.05, py, zf / 2.0), (0.12, 2.0 * (FW + SLOPE), slant),
                 WET_SAND, pitch=tilt)
    for s in (-1, 1):
        make_rot_box(f"Dig_Pit_Wall_{'N' if s > 0 else 'S'}", (px + (SLOPE - RAMP) / 2.0, py + s * (FW + SLOPE / 2.0 + 0.05), zf / 2.0),
                     (2.0 * FL + SLOPE + RAMP, 0.12, slant), WET_SAND, roll=-s * tilt)
    ramp = math.atan2(DEPTH, RAMP)
    make_rot_box("Dig_Pit_Ramp", (px - FL - RAMP / 2.0, py, zf / 2.0 - 0.05), (math.hypot(RAMP, DEPTH), 2.0 * FW, 0.10),
                 WET_SAND, pitch=ramp)
    # the car on the pit floor: a 1969 Mercedes-Benz, red, convertible top
    # up; the nose east. Body a side profile across its width, the top black
    # canvas, the windscreen raked, chrome at the ends, the wheels to the rims
    RED, CANVAS, CHROME = (0.66, 0.10, 0.08, 1.0), (0.10, 0.10, 0.11, 1.0), (0.70, 0.70, 0.68, 1.0)
    cz = zf
    body = [(-2.25, 0.30), (2.22, 0.30), (2.28, 0.52), (2.20, 0.78), (1.00, 0.86), (-1.60, 0.86), (-2.22, 0.80), (-2.28, 0.52)]
    make_prism("Mercedes_Body", (px, py, cz), body, 1.76, RED, axis="Y")
    top = [(0.20, 0.86), (0.05, 1.30), (-0.95, 1.32), (-1.45, 0.86)]
    make_prism("Mercedes_Top", (px, py, cz), top, 1.62, CANVAS, axis="Y")
    screen = [(0.62, 0.86), (0.24, 1.28), (0.08, 1.28), (0.46, 0.86)]
    make_prism("Mercedes_Windscreen", (px, py, cz), screen, 1.56, (0.22, 0.26, 0.28, 1.0), axis="Y")
    for s in (-1, 1):
        make_box(f"Mercedes_Bumper_{'F' if s > 0 else 'R'}", (px + s * 2.30, py, cz + 0.44), (0.08, 1.80, 0.10), CHROME)
        for t in (-1, 1):
            make_cyl(f"Mercedes_Wheel_{'F' if s > 0 else 'R'}{'L' if t > 0 else 'R'}", (px + s * 1.42, py + t * 0.78, cz + 0.33),
                     0.33, 0.22, (0.12, 0.12, 0.12, 1.0), segments=14, axis="Y")
    make_box("Mercedes_Grille", (px + 2.27, py, cz + 0.62), (0.06, 0.42, 0.26), CHROME)
    # a drift of sand still on the hood and the deck, the week not quite done
    make_blob("Mercedes_Hood_Sand", (px + 1.55, py + 0.2, cz + 0.84), 0.55, SAND, noise=0.3, seed=171, squash=0.18)
    make_blob("Mercedes_Deck_Sand", (px - 1.95, py - 0.3, cz + 0.82), 0.40, SAND, noise=0.3, seed=172, squash=0.18)
    # the spoil thrown back off the north and east rims
    make_blob("Dig_Spoil_Sand", (px + FL + SLOPE + 2.6, py + 0.8, 0.0), 2.2, SAND, noise=0.2, seed=150, squash=0.35)
    make_blob("Dig_Spoil_North", (px - 0.5, py + FW + SLOPE + 2.4, 0.0), 2.0, SAND, noise=0.2, seed=151, squash=0.30)
    # the tools on the south rim, where the camera comes in
    make_rot_box("Dig_Shovel", (px + 3.4, py - FW - SLOPE - 0.9, 0.55), (0.06, 0.06, 1.30), (0.50, 0.40, 0.28, 1.0), roll=0.4)
    make_box("Metal_Detector_Shaft", (px + 2.6, py - FW - SLOPE - 1.4, 0.02), (1.20, 0.04, 0.04), (0.30, 0.30, 0.32, 1.0))
    make_cyl("Metal_Detector_Coil", (px + 1.9, py - FW - SLOPE - 1.4, 0.015), 0.14, 0.03, (0.20, 0.20, 0.22, 1.0), segments=12)
    dy = py - FW - SLOPE - 1.4
    make_box("Metal_Detector_Control_Box", (px + 2.85, dy, 0.085), (0.20, 0.11, 0.09), (0.16, 0.17, 0.18, 1.0))
    make_box("Metal_Detector_Grip", (px + 3.02, dy, 0.07), (0.12, 0.05, 0.06), (0.10, 0.10, 0.10, 1.0))
    make_box("Metal_Detector_Arm_Cuff", (px + 3.18, dy, 0.07), (0.06, 0.12, 0.06), (0.10, 0.10, 0.10, 1.0))
    # (draft 3) the week's kit: "Charles excavated the machine by himself
    # over the course of a week": the wheelbarrow at the head of the ramp he
    # cut, a bucket upturned by the south rim, the tarp on the sand with the
    # water jug and stones on its corners
    wx, wy = px - FL - RAMP - 1.3, py - 0.4
    rust, steel = (0.46, 0.30, 0.20, 1.0), (0.30, 0.30, 0.32, 1.0)
    make_prism("Barrow_Tray", (wx, wy, 0.0), [(-0.42, 0.34), (0.28, 0.34), (0.48, 0.68), (-0.54, 0.68)], 0.62, rust, axis="Y")
    make_cyl("Barrow_Wheel", (wx + 0.66, wy, 0.20), 0.20, 0.10, (0.12, 0.12, 0.12, 1.0), segments=14, axis="Y")
    for s_ in (-1, 1):
        make_tube(f"Barrow_Fork_{s_:+d}", [(wx + 0.20, wy + s_ * 0.10, 0.36), (wx + 0.66, wy + s_ * 0.07, 0.20)], 0.018, steel, segments=5)
        make_tube(f"Barrow_Handle_{s_:+d}", [(wx + 0.20, wy + s_ * 0.24, 0.36), (wx - 0.40, wy + s_ * 0.27, 0.40),
                                             (wx - 1.15, wy + s_ * 0.29, 0.55)], 0.020, (0.50, 0.40, 0.28, 1.0), segments=5)
        make_rot_box(f"Barrow_Leg_{s_:+d}", (wx - 0.36, wy + s_ * 0.24, 0.19), (0.04, 0.04, 0.36), steel, pitch=0.12)
    make_blob("Barrow_Load_Sand", (wx - 0.04, wy, 0.66), 0.36, SAND, noise=0.25, seed=180, squash=0.35)
    make_cyl("Kit_Bucket", (px - 2.4, py - FW - SLOPE - 0.6, 0.15), 0.15, 0.30, (0.62, 0.64, 0.62, 1.0), segments=12)
    tx, ty = px - 4.4, py + FW + SLOPE + 2.2
    make_rot_box("Kit_Tarp", (tx, ty, 0.006), (2.4, 1.8, 0.012), (0.24, 0.36, 0.56, 1.0), yaw=0.25)
    for k, (dx, dy_) in enumerate(((-1.05, -0.78), (1.05, -0.78), (-1.05, 0.78), (1.05, 0.78))):
        c, s2 = 0.968, 0.247
        make_blob(f"Kit_Tarp_Stone_{k}", (tx + dx * c - dy_ * s2, ty + dx * s2 + dy_ * c, 0.07), 0.10, (0.50, 0.48, 0.44, 1.0),
                  noise=0.3, seed=190 + k, squash=0.7)
    make_cyl("Kit_Water_Jug", (tx + 0.4, ty + 0.1, 0.17), 0.12, 0.30, (0.84, 0.86, 0.90, 1.0), segments=12)
    make_cyl("Kit_Water_Jug_Cap", (tx + 0.4, ty + 0.1, 0.345), 0.04, 0.05, (0.20, 0.40, 0.70, 1.0), segments=8)
    make_rot_box("Kit_Pick", (tx - 0.5, ty - 0.2, 0.03), (0.90, 0.05, 0.05), (0.50, 0.40, 0.28, 1.0), yaw=1.1)
    make_rot_box("Kit_Pick_Head", (tx - 0.5 + 0.40 * 0.454, ty - 0.2 + 0.40 * 0.891, 0.04), (0.06, 0.55, 0.05), steel, yaw=1.1)
    # the bungalow, small in the distance
    bx, by = ox - 30.0, oy + 40.0
    make_box("Bungalow_Body", (bx, by, 1.4), (7.0, 5.0, 2.8), (0.86, 0.82, 0.70, 1.0))
    make_rot_box("Bungalow_Roof_N", (bx, by + 1.25, 3.25), (7.6, 2.9, 0.12), (0.40, 0.30, 0.26, 1.0), roll=0.35)
    make_rot_box("Bungalow_Roof_S", (bx, by - 1.25, 3.25), (7.6, 2.9, 0.12), (0.40, 0.30, 0.26, 1.0), roll=-0.35)
    make_box("Bungalow_Door", (bx + 1.0, by - 2.52, 1.0), (0.9, 0.04, 2.0), (0.36, 0.28, 0.22, 1.0))
    # (draft 3) "he'd rented a bungalow nearby": a place someone lives in for
    # a week — the front porch under its own shed roof, two windows either
    # side of the door, a chimney pipe, a chair on the porch
    trim, glass = (0.94, 0.92, 0.86, 1.0), (0.22, 0.26, 0.30, 1.0)
    make_box("Bungalow_Porch_Deck", (bx + 0.5, by - 3.4, 0.10), (5.0, 1.8, 0.20), (0.56, 0.46, 0.34, 1.0))
    for k, px_ in enumerate((bx - 1.85, bx + 2.85)):
        make_box(f"Bungalow_Porch_Post_{k}", (px_, by - 4.2, 1.23), (0.12, 0.12, 2.06), trim)
    make_rot_box("Bungalow_Porch_Roof", (bx + 0.5, by - 3.45, 2.38), (5.4, 2.1, 0.08), (0.40, 0.30, 0.26, 1.0), roll=0.18)
    make_box("Bungalow_Porch_Beam", (bx + 0.5, by - 4.2, 2.30), (5.0, 0.14, 0.14), trim)
    for k, wx_ in enumerate((bx - 1.6, bx + 2.6)):
        make_box(f"Bungalow_Window_{k}", (wx_, by - 2.52, 1.55), (1.1, 0.04, 1.0), glass)
        make_box(f"Bungalow_Window_{k}_Sill", (wx_, by - 2.56, 1.02), (1.3, 0.10, 0.05), trim)
        make_box(f"Bungalow_Window_{k}_Head", (wx_, by - 2.545, 2.09), (1.3, 0.05, 0.08), trim)
    make_cyl("Bungalow_Chimney_Pipe", (bx - 2.2, by + 0.9, 3.8), 0.10, 1.4, (0.26, 0.26, 0.28, 1.0), segments=8)
    make_box("Bungalow_Porch_Chair_Seat", (bx - 0.9, by - 3.3, 0.62), (0.50, 0.46, 0.05), (0.62, 0.50, 0.34, 1.0))
    make_box("Bungalow_Porch_Chair_Back", (bx - 0.9, by - 3.07, 0.92), (0.50, 0.05, 0.55), (0.62, 0.50, 0.34, 1.0))
    for k, (cx2, cy2) in enumerate(((-0.22, -0.2), (0.22, -0.2), (-0.22, 0.2), (0.22, 0.2))):
        make_box(f"Bungalow_Porch_Chair_Leg_{k}", (bx - 0.9 + cx2, by - 3.3 + cy2, 0.405), (0.04, 0.04, 0.41), (0.62, 0.50, 0.34, 1.0))
    # (draft 2) the sky card went: 500 m wide, its end stood mid-frame once
    # the camera turned north-west; the sky is the environment's now. The
    # dunes rise WEST of the flat so the sand never ends in a line (the cave's
    # headland, 200 m off, is stripped from this view in its preset)
    wc, wr = 13, 44
    west = [[(1.0 - c / float(wc - 1)) ** 1.5 * 4.5 + (0.6 * math.sin(r * 0.55 + c * 0.9) * (1.0 - c / float(wc - 1)))
             for c in range(wc)] for r in range(wr)]
    make_heightfield("Riverbed_West_Dunes_Ground", (x0 - 5.0 * (wc - 1), y0, 0.0), 5.0, west, SAND)
    for k in range(8):
        gx, gy = ox - 20.0 + k * 6.0, oy + 20.0 - (k % 3) * 8.0
        if abs(gx - CX) < CH + 1.0:
            continue                # not in the channel
        if hx0 - 1.0 < gx < hx1 + 1.0 and hy0 - 1.0 < gy < hy1 + 1.0:
            continue                # not in the dig
        make_blob(f"Dune_Grass_{k}", (ox - 20.0 + k * 6.0, oy + 20.0 - (k % 3) * 8.0, 0.4), 0.9, (0.50, 0.56, 0.36, 1.0),
                  noise=0.4, seed=160 + k, squash=0.5)


def main():
    clear_scene()
    build_cave()
    build_riverbed()
    try:
        join_stock()
    except Exception as _e:
        print("[join_stock] skipped:", _e)
    out = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                        "../../../assets/3d/locales/sea_cave.glb"))
    print(f"\n[build_sea_cave] exporting to {out}")
    export_glb(out)


if __name__ == "__main__":
    main()
