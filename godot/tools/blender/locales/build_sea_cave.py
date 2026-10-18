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
"""
import os, sys, math
_BT = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
if _BT not in sys.path: sys.path.insert(0, _BT)
from _props.geometry import (clear_scene, make_box, make_cyl, make_blob, make_rot_box, make_chamfer_box, make_heightfield,
                             rolling_heights, join_stock, export_glb)

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
    # rolling up beyond it; their first rows ramp from flat so no step shows
    px, py = ox - 4.0, oy + 6.0
    hx0, hx1, hy0, hy1 = px - 2.7, px + 2.7, py - 1.8, py + 1.8
    x0, x1, y0, y1 = ox - 80.0, ox + 80.0, oy - 60.0, oy + 60.0
    for nm, (ax, bx_, ay, by_) in {"S": (x0, x1, y0, hy0), "N": (x0, x1, hy1, y1),
                                   "W": (x0, hx0, hy0, hy1), "E": (hx1, x1, hy0, hy1)}.items():
        make_box(f"Riverbed_Flat_Sand_Ground_{nm}", ((ax + bx_) / 2.0, (ay + by_) / 2.0, -0.10), (bx_ - ax, by_ - ay, 0.20), SAND)
    hf = rolling_heights(20, 32, 0.8, seed=7, base=0.0, bumps=4)
    hf = [[z * min(1.0, r / 4.0) for z in row] for r, row in enumerate(hf)]
    make_heightfield("Riverbed_Dunes_Ground", (x0, y1, 0.0), 5.0, hf, SAND)
    make_box("Riverbed_Channel", (ox + 10.0, oy - 10.0, -0.05), (6.0, 140.0, 0.30), WET_SAND)
    make_box("Riverbed_Water", (ox + 10.0, oy - 10.0, 0.06), (2.2, 140.0, 0.02), (0.40, 0.48, 0.48, 1.0))
    for k in range(12):
        make_blob(f"River_Stone_{k}", (ox + 8.0 + (k % 3) * 1.8, oy - 30.0 + k * 5.0, 0.10), 0.25, (0.50, 0.48, 0.44, 1.0),
                  noise=0.3, seed=130 + k, squash=0.5)
    # the dig: a pit, the spoil heap, the red car body's sliver
    make_box("Dig_Pit_Floor", (px, py, -0.70), (5.0, 3.2, 0.10), WET_SAND)
    for s in (-1, 1):
        make_box(f"Dig_Pit_Wall_{s:+d}", (px + s * 2.6, py, -0.30), (0.20, 3.2, 0.90), WET_SAND)
        make_box(f"Dig_Pit_End_{s:+d}", (px, py + s * 1.7, -0.30), (5.4, 0.20, 0.90), WET_SAND)
    make_chamfer_box("Mercedes_Body", (px, py, -0.25), (4.2, 1.7, 0.70), (0.66, 0.10, 0.08, 1.0), chamfer=0.20)
    make_chamfer_box("Mercedes_Top", (px - 0.3, py, 0.20), (1.6, 1.5, 0.30), (0.12, 0.12, 0.12, 1.0), chamfer=0.10)
    make_blob("Dig_Spoil_Sand", (px + 5.0, py + 1.0, 0.0), 2.2, SAND, noise=0.2, seed=150, squash=0.35)
    make_rot_box("Dig_Shovel", (px + 3.4, py - 1.6, 0.55), (0.06, 0.06, 1.30), (0.50, 0.40, 0.28, 1.0), roll=0.4)
    make_box("Metal_Detector_Shaft", (px + 3.0, py - 2.2, 0.02), (1.20, 0.04, 0.04), (0.30, 0.30, 0.32, 1.0))
    make_cyl("Metal_Detector_Coil", (px + 2.3, py - 2.2, 0.015), 0.14, 0.03, (0.20, 0.20, 0.22, 1.0), segments=12)
    # the bungalow, small in the distance
    bx, by = ox - 30.0, oy + 40.0
    make_box("Bungalow_Body", (bx, by, 1.4), (7.0, 5.0, 2.8), (0.86, 0.82, 0.70, 1.0))
    make_rot_box("Bungalow_Roof_N", (bx, by + 1.25, 3.25), (7.6, 2.9, 0.12), (0.40, 0.30, 0.26, 1.0), roll=0.35)
    make_rot_box("Bungalow_Roof_S", (bx, by - 1.25, 3.25), (7.6, 2.9, 0.12), (0.40, 0.30, 0.26, 1.0), roll=-0.35)
    make_box("Bungalow_Door", (bx + 1.0, by - 2.52, 1.0), (0.9, 0.04, 2.0), (0.36, 0.28, 0.22, 1.0))
    make_box("Riverbed_Sky", (ox, oy + 170.0, 60.0), (500.0, 0.2, 240.0), (0.72, 0.80, 0.88, 1.0))
    for k in range(8):
        if abs(ox - 20.0 + k * 6.0 - (ox + 10.0)) < 4.0:
            continue                # not in the channel
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
