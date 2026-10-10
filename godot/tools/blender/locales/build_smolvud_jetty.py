"""smolvud_jetty — the jetty at Smolvud, Oregon (vol7 Frequency Interlude II).

NEW SET (2026-10-10). The interlude's segment "[ AT A JETTY, SMOLVUD,
OREGON — fog ]" played on the Cape Perpetua overlook's fog. The prose:

  "The Frog has been here for an hour. The Frog will be here for another
  four. The Frog is not, technically, fishing. The Frog is waiting.
  Around four in the afternoon, three young people will pass this jetty
  without noticing him ... The Frog will roll a fresh smoke ... The fog
  will accept the smoke. The fog will not give it back."

A rubble-mound jetty at the river mouth, 90 m out from the shore:
  · THE JETTY: the core under its armour of basalt, two rows a side,
    interlocked; the gravel crest path up its spine from the ramp at the
    root; the roundhead at the tip with the green navigation light on its
    concrete base and its daymark.
  · THE FROG'S PLACE, a third of the way out on the channel side: the
    flat boulder with an old cushion on it, the tobacco tin and papers;
    the five-gallon bucket holding the butt of a rod whose line goes down
    into the channel — not, technically, fishing; the tackle box; the
    thermos.
  · THE SHORE: the beach falling into the surf east of the jetty, the
    channel west of it; the shore path the three will walk along at four
    o'clock, its railing, a bench, a bin, two lamp posts, the jetty sign.
  · Across the channel the harbor: the floats, the pilings, three boats.
    Behind, Smolvud low on its rise, a dozen roofs going grey in the fog.

Coordinate frame: Blender Z-up. The shore runs along x; the sea is +Y;
the jetty runs out along +Y from the root at y=-6. Sea level z=0, the
land at z=1.8, the jetty crest at z=3.1. glTF export remaps to Godot
(x, z, -y).

Draft 2 targets: the three young people's way past at the jetty root
(the path's wet sheen, footprints in the sand); the gulls; the Frog's
smoke as a NONSOLID wisp; the tide line on the rocks.
"""
import math
import os
import random
import sys
_BT = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
if _BT not in sys.path: sys.path.insert(0, _BT)
from _props.geometry import clear_scene, make_box, make_cyl, make_rot_box, export_glb

LAND_Z = 1.8
CREST_Z = 3.1
J_Y0, J_Y1 = 2.0, 80.0           # crest path from the top of the ramp to the roundhead

COL_SEA = (0.22, 0.30, 0.32, 1.0)
COL_SAND = (0.66, 0.62, 0.52, 1.0)
COL_GRASS = (0.44, 0.48, 0.32, 1.0)
COL_GRAVEL = (0.50, 0.48, 0.44, 1.0)
COL_ASPHALT = (0.34, 0.34, 0.35, 1.0)
COL_CONCRETE = (0.62, 0.62, 0.60, 1.0)
COL_FOAM = (0.86, 0.88, 0.86, 1.0)
COL_DARK = (0.16, 0.16, 0.18, 1.0)
COL_GREEN = (0.16, 0.50, 0.30, 1.0)
ROCK_COLS = ((0.30, 0.30, 0.32, 1.0), (0.36, 0.35, 0.34, 1.0), (0.26, 0.27, 0.28, 1.0), (0.40, 0.39, 0.37, 1.0))
ROCK_WET = ((0.20, 0.22, 0.20, 1.0), (0.24, 0.26, 0.22, 1.0))


def build_ground():
    """The shore: the land at 1.8 m, the beach slab falling into the surf east of
    the jetty, a steeper bank into the channel west of it; and the sea. (Boxes and
    two sloped slabs: the audits record a heightfield as its bounding box.)"""
    make_box("Shore_Land", (0.0, -54.0, LAND_Z / 2.0 - 1.0), (240.0, 94.4, LAND_Z + 2.0), COL_SAND)
    for nm, x0, x1, y1, z1 in (("Shore_Sand_E", 2.0, 120.0, 16.0, -0.8), ("Shore_Sand_W", -120.0, -2.0, 4.0, -2.5)):
        run, drop = y1 + 6.8, LAND_Z - z1
        ang = -math.atan2(drop, run)
        L = math.hypot(run, drop)
        make_rot_box(nm, ((x0 + x1) / 2.0, (y1 - 6.8) / 2.0, (LAND_Z + z1) / 2.0 - 0.15), (x1 - x0, L, 0.30), COL_SAND, roll=ang)
    make_box("Sea_Water", (0.0, 140.0, -0.02), (480.0, 300.0, 0.04), COL_SEA)
    # the surf on the beach east of the jetty, and against the jetty's east rocks
    for k in range(10):
        make_box(f"Surf_Foam_Beach_{k}", (10.0 + k * 9.0, 9.0 + (k % 3) * 0.8, 0.01), (7.5, 0.5, 0.02), COL_FOAM)
    for k in range(12):
        make_box(f"Surf_Foam_Jetty_{k}", (5.9, 8.0 + k * 6.0, 0.01), (1.2, 4.0, 0.02), COL_FOAM)
    # dune grass on the land's seaward edge
    rnd = random.Random(8)
    for k in range(26):
        gx = rnd.uniform(-60, 60)
        if abs(gx) < 6:
            continue
        make_box(f"Dune_Grass_{k}", (gx, rnd.uniform(-14, -11), LAND_Z + 0.2), (rnd.uniform(1.0, 2.4), rnd.uniform(0.6, 1.2), 0.4), COL_GRASS)


def build_jetty():
    rnd = random.Random(17)
    # the core: the rubble mound under its armour (rock against rock is geology)
    L = J_Y1 + 6.0 - J_Y0
    cyy = (J_Y0 + J_Y1 + 6.0) / 2.0
    make_box("Jetty_Rock_Core_Low", (0.0, cyy, 0.0), (10.0, L, 3.2), (0.26, 0.26, 0.27, 1.0))
    make_box("Jetty_Rock_Core_High", (0.0, cyy, 2.30), (6.0, L, 1.4), (0.28, 0.28, 0.29, 1.0))
    # the crest path and the ramp up to it from the shore path
    make_box("Jetty_Crest_Path", (0.0, (J_Y0 + J_Y1) / 2.0, CREST_Z - 0.05), (3.2, J_Y1 - J_Y0, 0.10), COL_GRAVEL)
    rise = CREST_Z - LAND_Z
    run = J_Y0 + 6.8                          # from the shore path's N edge
    ang = math.atan2(rise, run)
    rc = (0.0, J_Y0 - run / 2.0, (LAND_Z + CREST_Z) / 2.0 - 0.05)
    make_rot_box("Jetty_Ramp_Path", rc, (3.2, math.hypot(run, rise), 0.10), COL_GRAVEL, roll=ang)
    # the rubble under the ramp, down into the sand
    make_rot_box("Jetty_Rock_Ramp_Fill", (0.0, rc[1], rc[2] - 0.80), (4.0, math.hypot(run, rise), 1.50), (0.28, 0.28, 0.29, 1.0), roll=ang)
    # the armour: two rows a side, every 1.6 m, turned every which way
    k = 0
    y = J_Y0 + 1.0
    while y < J_Y1 + 2.0:
        for s in (-1, 1):
            sx = rnd.uniform(1.6, 2.2)
            make_rot_box(f"Riprap_Low{k}_Boulder", (s * rnd.uniform(4.4, 5.0), y + rnd.uniform(-0.3, 0.3), rnd.uniform(0.7, 1.0)),
                         (sx, rnd.uniform(1.4, 2.0), rnd.uniform(1.2, 1.6)), ROCK_WET[k % 2],
                         yaw=rnd.uniform(-0.4, 0.4), pitch=rnd.uniform(-0.25, 0.25), roll=rnd.uniform(-0.25, 0.25))
            make_rot_box(f"Riprap_High{k}_Boulder", (s * rnd.uniform(2.45, 2.80), y + rnd.uniform(-0.3, 0.3), rnd.uniform(2.35, 2.60)),
                         (rnd.uniform(1.2, 1.6), rnd.uniform(1.1, 1.5), rnd.uniform(1.0, 1.3)), ROCK_COLS[(k + (s > 0)) % 4],
                         yaw=rnd.uniform(-0.5, 0.5), pitch=rnd.uniform(-0.3, 0.3), roll=rnd.uniform(-0.3, 0.3))
            k += 1
        y += 1.6
    # the roundhead at the tip
    for m in range(14):
        a = math.pi * (m / 13.0)
        r = rnd.uniform(4.0, 5.2)
        make_rot_box(f"Riprap_Head{m}_Boulder", (r * math.cos(a), J_Y1 + 4.0 + r * math.sin(a) * 0.9, rnd.uniform(1.0, 2.2)),
                     (rnd.uniform(1.6, 2.2), rnd.uniform(1.5, 2.0), rnd.uniform(1.3, 1.8)), ROCK_COLS[m % 4],
                     yaw=rnd.uniform(-0.6, 0.6), pitch=rnd.uniform(-0.3, 0.3), roll=rnd.uniform(-0.3, 0.3))
    # the navigation light on its concrete base at the tip, its daymark, its lamp
    ny = J_Y1 + 3.0
    nb = 3.0                                  # the core's top, past the crest path's end
    make_cyl("Nav_Light_Base", (0.0, ny, nb + 0.45), 1.1, 0.90, COL_CONCRETE, segments=16)
    make_box("Nav_Light_Tower", (0.0, ny, nb + 0.90 + 2.0), (0.50, 0.50, 4.0), (0.80, 0.80, 0.78, 1.0))
    make_box("Nav_Light_Daymark", (0.0, ny - 0.27, nb + 3.4), (1.10, 0.04, 1.10), COL_GREEN)
    make_box("Nav_Light_Daymark_Border", (0.0, ny - 0.292, nb + 3.4), (0.90, 0.004, 0.90), (0.94, 0.94, 0.92, 1.0))
    make_cyl("Nav_Light_Lamp", (0.0, ny, nb + 5.10), 0.20, 0.40, (0.30, 0.86, 0.46, 1.0), segments=12)
    make_cyl("Nav_Light_Lamp_Cap", (0.0, ny, nb + 5.34), 0.24, 0.08, COL_DARK, segments=12)


def build_frog():
    """The Frog's place on the channel side: not, technically, fishing."""
    fy = 34.0
    top = CREST_Z
    # the flat boulder he sits on, its old cushion, the tobacco tin and papers
    make_rot_box("Frog_Seat_Rock", (-1.95, fy, top + 0.0), (1.00, 0.90, 0.70), ROCK_COLS[1], yaw=0.12)
    seat = top + 0.35
    make_box("Frog_Cushion", (-1.90, fy, seat + 0.025), (0.46, 0.42, 0.05), (0.40, 0.28, 0.20, 1.0))
    make_box("Frog_Tobacco_Tin", (-1.62, fy - 0.28, seat + 0.012), (0.11, 0.08, 0.024), (0.62, 0.30, 0.16, 1.0))
    make_box("Frog_Rolling_Papers", (-1.60, fy - 0.15, seat + 0.006), (0.07, 0.04, 0.012), (0.90, 0.88, 0.80, 1.0))
    # the bucket, holding the butt of the rod; the line going down into the channel
    bx, by = -1.00, fy - 0.60
    make_cyl("Frog_Bucket", (bx, by, top + 0.18), 0.15, 0.36, (0.92, 0.88, 0.80, 1.0), segments=12)
    make_cyl("Frog_Bucket_Rim", (bx, by, top + 0.355), 0.155, 0.02, (0.80, 0.76, 0.68, 1.0), segments=12)
    p = -0.87
    d = (math.sin(p), 0.0, math.cos(p))
    butt = (bx, by, top + 0.20)
    rl = 2.6
    make_rot_box("Frog_Rod", (butt[0] + d[0] * rl / 2.0, by, butt[2] + d[2] * rl / 2.0), (0.025, 0.025, rl), (0.20, 0.20, 0.22, 1.0), pitch=p)
    tip = (butt[0] + d[0] * rl, by, butt[2] + d[2] * rl)
    wet = (-6.4, by, 0.0)
    ll = math.dist(tip, wet)
    lp = math.atan2(tip[0] - wet[0], tip[2] - wet[2])
    make_rot_box("Frog_Rod_Line_Thread", ((tip[0] + wet[0]) / 2.0, by, (tip[2] + wet[2]) / 2.0), (0.004, 0.004, ll), (0.84, 0.84, 0.82, 1.0), pitch=lp)
    # the tackle box, the thermos
    make_box("Frog_Tackle_Box", (-0.55, fy + 0.40, top + 0.08), (0.40, 0.22, 0.16), (0.24, 0.40, 0.30, 1.0))
    make_box("Frog_Tackle_Box_Handle", (-0.55, fy + 0.40, top + 0.18), (0.20, 0.03, 0.04), COL_DARK)
    make_cyl("Frog_Thermos", (-0.90, fy + 0.85, top + 0.16), 0.045, 0.32, (0.24, 0.36, 0.30, 1.0), segments=10)
    make_cyl("Frog_Thermos_Cup", (-0.90, fy + 0.85, top + 0.34), 0.05, 0.05, (0.60, 0.60, 0.58, 1.0), segments=10)


def build_shore():
    """The path the three will walk along at four o'clock, and what stands on it."""
    pz = LAND_Z
    make_box("Shore_Path", (0.0, -8.0, pz + 0.01), (120.0, 2.4, 0.04), COL_ASPHALT)
    for s in (-1, 1):
        for k in range(8):
            px = s * (3.0 + k * 3.0)
            make_cyl(f"Path_Rail_Post_{s:+d}_{k}", (px, -6.7, pz + 0.50), 0.04, 1.00, (0.46, 0.40, 0.32, 1.0), segments=6)
        make_box(f"Path_Rail_Top_{s:+d}", (s * 13.5, -6.7, pz + 1.02), (21.2, 0.08, 0.06), (0.46, 0.40, 0.32, 1.0))
        make_box(f"Path_Rail_Mid_{s:+d}", (s * 13.5, -6.7, pz + 0.55), (21.2, 0.06, 0.05), (0.46, 0.40, 0.32, 1.0))
    make_box("Path_Bench_Seat", (7.5, -9.6, pz + 0.45), (1.60, 0.42, 0.05), (0.50, 0.40, 0.30, 1.0))
    make_box("Path_Bench_Back", (7.5, -9.80, pz + 0.75), (1.60, 0.05, 0.36), (0.50, 0.40, 0.30, 1.0))
    for e in (-1, 1):
        make_box(f"Path_Bench_Leg_{e:+d}", (7.5 + e * 0.70, -9.65, pz + 0.21), (0.06, 0.40, 0.42), COL_DARK)
        make_box(f"Path_Bench_Back_Post_{e:+d}", (7.5 + e * 0.70, -9.80, pz + 0.66), (0.06, 0.05, 0.48), COL_DARK)
    make_cyl("Path_Bin", (9.2, -9.6, pz + 0.45), 0.25, 0.90, (0.24, 0.30, 0.26, 1.0), segments=12)
    for k, lx in enumerate((-12.0, 12.0)):
        make_cyl(f"Path_Lamp_{k}_Post", (lx, -9.4, pz + 2.0), 0.06, 4.0, COL_DARK, segments=8)
        make_box(f"Path_Lamp_{k}_Head", (lx, -9.4, pz + 4.10), (0.36, 0.36, 0.22), COL_DARK)
    make_cyl("Jetty_Sign_Post", (2.4, -6.4, pz + 0.90), 0.04, 1.80, COL_DARK, segments=6)
    make_box("Jetty_Sign", (2.4, -6.44, pz + 1.62), (0.70, 0.03, 0.46), (0.94, 0.80, 0.20, 1.0))
    make_box("Jetty_Sign_Text", (2.4, -6.457, pz + 1.62), (0.56, 0.004, 0.28), COL_DARK)


def build_harbor_and_town():
    rnd = random.Random(41)
    # across the channel: the floats, the pilings, three boats
    hx = -48.0
    make_box("Harbor_Dock_Float_Main", (hx, 18.0, 0.15), (2.4, 40.0, 0.30), (0.52, 0.48, 0.40, 1.0))
    for k in range(4):
        make_box(f"Harbor_Dock_Float_Finger_{k}", (hx + 5.2, 4.0 + k * 9.0, 0.15), (8.0, 1.4, 0.30), (0.52, 0.48, 0.40, 1.0))
    for k in range(9):
        make_cyl(f"Harbor_Piling_{k}", (hx - 1.6, -1.0 + k * 5.0, 1.2), 0.20, 4.0, (0.30, 0.26, 0.22, 1.0), segments=8)
    for k, (bx, by) in enumerate(((hx + 5.0, 8.5), (hx + 5.4, 17.5), (hx + 5.0, 26.5))):
        col = ((0.84, 0.82, 0.76, 1.0), (0.30, 0.46, 0.62, 1.0), (0.70, 0.26, 0.20, 1.0))[k]
        make_box(f"Boat_{k}_Hull", (bx, by, 0.45), (8.0, 2.6, 1.30), col)
        make_box(f"Boat_{k}_Cabin", (bx - 1.0, by, 1.65), (2.6, 2.0, 1.10), (0.88, 0.88, 0.84, 1.0))
        make_cyl(f"Boat_{k}_Mast", (bx + 1.2, by, 1.10 + 1.9), 0.08, 3.8, COL_DARK, segments=6)   # stepped on the deck
    make_box("Far_Shore_Headland", (-170.0, 40.0, 4.0), (80.0, 140.0, 12.0), (0.34, 0.38, 0.30, 1.0))
    # Smolvud low on its rise behind the shore, going grey in the fog
    placed = 0
    feet = []
    for k in range(60):
        x = rnd.uniform(-70, 70)
        y = rnd.uniform(-90, -24)
        if abs(x) < 8 and y > -30:
            continue
        w, d, h = rnd.uniform(6, 10), rnd.uniform(6, 9), rnd.uniform(3.0, 6.5)
        if any(abs(x - fx) < (w + fw) / 2.0 + 2.0 and abs(y - fy) < (d + fd) / 2.0 + 2.0 for fx, fy, fw, fd in feet):
            continue                          # a yard between every two houses
        feet.append((x, y, w, d))
        col = ((0.86, 0.84, 0.78, 1.0), (0.56, 0.64, 0.70, 1.0), (0.76, 0.66, 0.42, 1.0), (0.62, 0.58, 0.52, 1.0))[k % 4]
        base = LAND_Z
        make_box(f"Town_House_{placed}", (x, y, base + h / 2.0), (w, d, h), col)
        hd = d / 4.0 + 0.25
        rz = base + h + hd * math.sin(0.5) + 0.075 - 0.02      # the eave sits on the wall top
        make_rot_box(f"Town_House_{placed}_Roof_N", (x, y + d / 4.0, rz), (w + 0.4, 2.0 * hd, 0.15), (0.30, 0.30, 0.32, 1.0), roll=-0.5)
        make_rot_box(f"Town_House_{placed}_Roof_S", (x, y - d / 4.0, rz), (w + 0.4, 2.0 * hd, 0.15), (0.30, 0.30, 0.32, 1.0), roll=0.5)
        placed += 1
        if placed >= 14:
            break
    for k in range(12):
        tx, ty = rnd.uniform(-90, 90), rnd.uniform(-96, -40)
        make_cyl(f"Town_Tree_{k}_Trunk", (tx, ty, LAND_Z + 2.0), 0.25, 4.0, (0.30, 0.24, 0.18, 1.0), segments=6)
        make_cyl(f"Town_Tree_{k}_Crown", (tx, ty, LAND_Z + 7.0), 2.0, 7.0, (0.20, 0.30, 0.22, 1.0), segments=8)


def main():
    clear_scene()
    build_ground()
    build_jetty()
    build_frog()
    build_shore()
    build_harbor_and_town()
    out = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)),
        "../../../assets/3d/locales/smolvud_jetty.glb"))
    print(f"\n[build_smolvud_jetty] exporting to {out}")
    export_glb(out)


if __name__ == "__main__":
    main()
