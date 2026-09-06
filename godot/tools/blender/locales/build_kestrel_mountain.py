"""kestrel_mountain — the mountain path inside the 2034 stick, and the
square at its foot. vol7 ch11 (Kestrel Mountain), re-homed off
cabin_road (2026-09-03).

"He was on a path. The path was dirt. The path was on the side of a
mountain that rose to his left and fell away on his right. The
mountain was, by the texture of the rock face beside him, basalt ...
The path was wide enough for a person." The cloud sitting on the top
of the mountain; the town in the valley far below with the shape of a
town in the European Alps, a square. The stations: "a stone hut at the
side of the path. The hut had a low door. The door was open. There was
a wooden bench inside" (the wise old man — cast); the stream that
"came out of the rocks above and crossed the path," the plank, and on
the plank the cedar bowl with the spiral and the figures; "a stone
bench at a turn where the path bent left"; the bend that "did not
quite match the topography," and at the bend "the hedge was about
waist-high. The hedge had red berries on it." And at the end, walked
out: "the path opened onto a square paved in old stone ... At the
square's center was a fountain — three stone basins stacked ... on
the rim of the lower basin a row of figures carved into the stone.
The carvings on the rim were the Major Arcana."

The mountain is a cliff mass west of the path and a long drop wedge
east of it, per segment; the path climbs as ramps between flat
station segments. The cloud is beyond the last segment. The square is
at the foot, south of the path start, at the same level — the valley
proper is a lower terrace further east where the rest of the town
sits small.

Coordinate frame: Blender Z-up. Path start at (0, -10, 0) running
north (+y); ten 8 m segments to y 70; the square centered (0, -22).
glTF export remaps to Godot (x, z, -y).

DRAFT 1 (2026-09-03): ten path segments (ramps + flats) with cliff
mass west and drop wedges east, the mountain mass beyond, the valley
terrace with the small far town and church, the stone hut with its
open low door and the bench inside, the stream gap with its water,
the plank and the bowl on it, the third-station bench, the hedge with
red berries at the bend, the cloud over the top, the square with its
paving, the three-basin fountain with twenty-two rim figures, the
alpine buildings around the square, lamp posts, far ridges.
Draft 2 targets: switchbacks instead of a straight climb, scree and
rubble on the path edges, the corridor behind the hedge as its own
locale (nodes 41-128, the basement and the boy at the desk), the
Major Arcana figures as distinct silhouettes.
"""
import os, sys, math
_BT = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
if _BT not in sys.path: sys.path.insert(0, _BT)
from _props import palette as P
from _props.geometry import clear_scene, make_box, make_cyl, make_blob, make_wedge, make_gable, make_taper_cyl, make_lathe, make_rot_box, export_glb
from _props.detail import make_far_bands

DIRT = (0.42, 0.36, 0.28, 1.0)
BASALT = (0.30, 0.29, 0.30, 1.0)
BASALT_WARM = (0.36, 0.33, 0.31, 1.0)
BASALT_DK = (0.22, 0.22, 0.24, 1.0)
GRASS = (0.34, 0.42, 0.26, 1.0)
STONE = (0.56, 0.54, 0.50, 1.0)
STONE_DK = (0.46, 0.44, 0.40, 1.0)
WATER = (0.42, 0.56, 0.62, 0.7)
WOOD = (0.48, 0.38, 0.26, 1.0)
CEDAR = (0.62, 0.44, 0.28, 1.0)
HEDGE = (0.22, 0.34, 0.20, 1.0)
BERRY = (0.78, 0.14, 0.12, 1.0)
CLOUD = (0.84, 0.85, 0.86, 0.6)
WALL = (0.80, 0.74, 0.62, 1.0)
ROOF = (0.44, 0.30, 0.24, 1.0)
PAVING = (0.50, 0.48, 0.44, 1.0)

SEG = 8.0
Y0 = -10.0
# segment kinds: ramp rises 1.2 over the segment; flat holds the level
KINDS = ("ramp", "flat", "ramp", "ramp", "flat", "ramp", "flat", "ramp", "ramp", "flat")
VALLEY_Z = -15.0


def seg_levels():
    z = 0.0
    out = []
    for k in KINDS:
        z0 = z
        z1 = z + (1.2 if k == "ramp" else 0.0)
        out.append((z0, z1))
        z = z1
    return out


def build_path_and_mountain():
    make_box("Ground_Far", (0.0, 0.0, VALLEY_Z - 0.41), (700.0, 700.0, 0.02), (0.24, 0.28, 0.22, 1.0))
    make_box("Valley_Floor", (60.0, 20.0, VALLEY_Z - 0.15), (200.0, 260.0, 0.30), GRASS)
    # the mountain mass west of everything, the cliff the path is cut into
    make_box("Mountain_Mass", (-70.0, 30.0, 15.0), (100.0, 160.0, 30.0), BASALT_DK)
    levels = seg_levels()
    for i, ((z0, z1), kind) in enumerate(zip(levels, KINDS)):
        y0 = Y0 + i * SEG
        ym = y0 + SEG / 2.0
        # the path itself: a ramp (wedge + support) or a flat step
        if kind == "ramp":
            if z0 > 0.0:
                make_box(f"Path_Support_{i}", (0.0, ym, z0 / 2.0), (3.0, SEG, z0), DIRT)
            make_wedge(f"Path_Ramp_{i}", (0.0, ym, z0 + 0.6), (3.0, SEG, 1.2), DIRT, high_end="+Y")
        else:
            if i == 4:
                # the stream crosses the path here: two halves with a 1 m gap
                make_box(f"Path_Flat_{i}_S", (0.0, y0 + 1.75, z1 / 2.0), (3.0, 3.5, z1), DIRT)
                make_box(f"Path_Flat_{i}_N", (0.0, y0 + 6.25, z1 / 2.0), (3.0, 3.5, z1), DIRT)
            else:
                make_box(f"Path_Flat_{i}", (0.0, ym, z1 / 2.0), (3.0, SEG, z1), DIRT)
        # cliff mass west of the path, stepping up with it
        cliff_h = z1 + 9.0
        ledge = 3.5 if i in (1, 6) else 0.0    # station ledges for the hut / the bench + hedge
        make_box(f"Cliff_{i}", (-1.5 - ledge - (18.5 - ledge) / 2.0, ym, cliff_h / 2.0), (18.5 - ledge, SEG, cliff_h), BASALT if i % 2 else BASALT_WARM)
        if ledge:
            make_box(f"Ledge_{i}", (-1.5 - ledge / 2.0, ym, z1 / 2.0), (ledge, SEG, z1), DIRT)
        # the drop east of the path, down to the valley terrace
        top = z1
        make_wedge(f"Drop_{i}", (1.5 + 38.5 / 2.0, ym, (VALLEY_Z + top) / 2.0), (38.5, SEG, top - VALLEY_Z), GRASS if i % 3 else (0.38, 0.40, 0.30, 1.0), high_end="-X")
        # rock texture: a few boulders on the cliff face's foot and the drop's shoulder
        make_blob(f"Cliff_Rock_{i}", (-1.5 - ledge - 0.9, y0 + 2.0 + (i % 3), cliff_h + 0.7), 0.55, BASALT_DK, noise=0.28, seed=60 + i, squash=0.8)
    return levels


def build_stations(levels):
    # ── first station: the stone hut on the ledge, low door open, the bench inside
    z = levels[1][1]
    hx, hy = -3.3, Y0 + 1 * SEG + 4.0
    make_box("Hut_Wall_W", (hx - 1.45, hy, z + 1.1), (0.30, 3.2, 2.2), STONE)
    make_box("Hut_Wall_N", (hx, hy + 1.45, z + 1.1), (2.6, 0.30, 2.2), STONE)
    make_box("Hut_Wall_S", (hx, hy - 1.45, z + 1.1), (2.6, 0.30, 2.2), STONE)
    make_box("Hut_Wall_E_Left", (hx + 1.45, hy + 0.95, z + 1.1), (0.30, 1.30, 2.2), STONE)
    make_box("Hut_Wall_E_Right", (hx + 1.45, hy - 0.95, z + 1.1), (0.30, 1.30, 2.2), STONE)
    make_box("Hut_Door_Lintel", (hx + 1.45, hy, z + 1.95), (0.30, 0.60, 0.50), STONE_DK)
    make_box("Hut_Door_Open", (hx + 1.75, hy + 0.55, z + 0.85), (0.06, 0.70, 1.70), WOOD)
    make_gable("Hut_Roof", (hx, hy, z + 2.2 + 0.45), (3.4, 3.6, 0.9), STONE_DK, ridge_axis="Y")
    # slate slabs laid up both slopes (the roof reads as stone, not a tent)
    for sgn in (-1, 1):
        for ci in range(3):
            t = 0.2 + ci * 0.3
            make_rot_box(f"Hut_Slate_{sgn:+d}_{ci}", (hx + sgn * (1.7 - t * 1.7), hy + (ci % 2) * 0.3 - 0.15, z + 2.2 + t * 0.9 + 0.05),
                         (0.55, 1.1, 0.05), (0.42, 0.42, 0.44, 1.0) if ci % 2 else (0.38, 0.38, 0.40, 1.0), roll=0.0, pitch=sgn * 0.49)
    make_box("Hut_Bench", (hx - 0.6, hy, z + 0.45), (0.50, 1.80, 0.06), WOOD)
    for li, dy in enumerate((-0.7, 0.7)):
        make_box(f"Hut_Bench_Leg_{li}", (hx - 0.6, hy + dy, z + 0.21), (0.40, 0.08, 0.42), WOOD)
    make_box("Hut_Floor_Worn", (hx + 0.4, hy, z + 0.0015), (1.2, 1.0, 0.003), (0.48, 0.42, 0.34, 1.0))
    # ── second station: the stream across the path, the plank, the bowl on the plank
    z = levels[4][1]
    gy = Y0 + 4 * SEG + 4.0
    make_box("Stream_Bed", (0.0, gy, (z - 0.4) / 2.0), (3.0, 1.0, z - 0.4), BASALT_DK)
    make_box("Stream_Water", (0.0, gy, z - 0.35), (3.0, 1.0, 0.10), WATER)
    make_box("Stream_Foam_0", (-1.1, gy, z - 0.298), (0.30, 0.20, 0.004), (0.86, 0.90, 0.90, 1.0))
    make_box("Stream_Foam_1", (0.9, gy + 0.2, z - 0.298), (0.24, 0.16, 0.004), (0.86, 0.90, 0.90, 1.0))
    make_box("Stream_Source_Rock", (-1.0, gy, z + 0.5), (1.0, 1.4, 1.0), BASALT_DK)
    make_box("Stream_Source_Fall", (-0.4, gy, z + 0.35), (0.30, 0.50, 1.30), WATER)
    make_box("Plank", (0.3, gy, z + 0.03), (0.40, 1.60, 0.06), WOOD)
    make_cyl("Bowl", (0.3, gy, z + 0.06 + 0.03), 0.065, 0.06, CEDAR, segments=12)
    make_cyl("Bowl_Hollow", (0.3, gy, z + 0.06 + 0.0605), 0.05, 0.001, (0.46, 0.32, 0.20, 1.0), segments=12)
    # ── third station: the stone bench at the turn, the bend, the hedge with red berries
    z = levels[6][1]
    by = Y0 + 6 * SEG + 2.5
    make_box("Bench_Seat", (-2.2, by, z + 0.47), (0.55, 1.60, 0.10), STONE)
    for li, dy in enumerate((-0.6, 0.6)):
        make_box(f"Bench_Leg_{li}", (-2.2, by + dy, z + 0.21), (0.45, 0.20, 0.42), STONE_DK)
    make_box("Bench_Bread_Crumbs", (-2.05, by + 0.2, z + 0.5215), (0.10, 0.08, 0.003), (0.74, 0.62, 0.42, 1.0))
    hy = Y0 + 6 * SEG + 6.4
    for hi, hxx in enumerate((-4.4, -3.2, -2.0)):
        make_blob(f"Hedge_{hi}", (hxx, hy, z + 0.55), 0.45, HEDGE, noise=0.22, seed=90 + hi, squash=0.8)
        for bi in range(3):
            a = math.pi / 2.0 + (bi - 1) * 0.7
            make_box(f"Hedge_Berry_{hi}_{bi}", (hxx + 0.62 * math.cos(a), hy - 0.62 * math.sin(a), z + 0.55 + 0.1 * bi), (0.03, 0.03, 0.03), BERRY)
    make_box("Bend_Wear", (-3.2, hy - 0.9, z + 0.0015), (2.8, 0.6, 0.003), (0.46, 0.40, 0.32, 1.0))


def build_cloud():
    for i, (x, y, r, s) in enumerate(((-6.0, 82.0, 6.0, 101), (4.0, 84.0, 6.5, 102), (14.0, 82.0, 6.0, 103),
                                      (0.0, 92.0, 7.0, 104), (10.0, 94.0, 6.5, 105), (-10.0, 92.0, 6.0, 106))):
        make_blob(f"Cloud_{i}", (x, y, 14.0 + r * 0.2), r, CLOUD, noise=0.16, seed=s, squash=0.5)
    make_box("Cloud_Cap", (10.5, 100.0, 22.0), (59.0, 30.0, 14.0), (0.84, 0.85, 0.86, 0.5))


def build_square():
    """The square at the foot of the mountain: old stone paving, the
    three-basin fountain with the Major Arcana carved around the lower
    rim, alpine buildings on three sides, lamp posts."""
    sx, sy = 0.0, -22.0
    make_box("Square_Paving", (sx, sy, -0.15), (30.0, 24.0, 0.30), PAVING)
    for i in range(9):
        make_box(f"Paving_Line_{i}", (sx - 12.0 + i * 3.0, sy, 0.001), (0.05, 24.0, 0.002), (0.42, 0.40, 0.36, 1.0))
    for i in range(7):
        make_box(f"Paving_Line_Y_{i}", (sx, sy - 9.0 + i * 3.0, 0.001), (30.0, 0.05, 0.002), (0.42, 0.40, 0.36, 1.0))
    # the fountain
    # lathed: a stepped base, three basins with lips, two balusters, a finial
    make_lathe("Fountain_Base", (sx, sy, 0.0), [(3.4, 0.0), (3.4, 0.12), (3.25, 0.16), (3.25, 0.20), (0.0, 0.20)], STONE_DK, segments=24)
    make_lathe("Fountain_Lower_Basin", (sx, sy, 0.20), [(0.0, 0.0), (2.6, 0.0), (2.95, 0.10), (3.05, 0.30), (3.02, 0.44), (2.90, 0.50), (2.70, 0.50), (0.0, 0.50)], STONE, segments=24)
    make_cyl("Fountain_Lower_Water", (sx, sy, 0.71), 2.66, 0.02, WATER, segments=24)
    make_lathe("Fountain_Mid_Pedestal", (sx, sy, 0.72), [(0.0, 0.0), (0.62, 0.0), (0.50, 0.10), (0.36, 0.30), (0.34, 0.55), (0.44, 0.75), (0.56, 0.86), (0.60, 0.90), (0.0, 0.90)], STONE_DK, segments=12)
    make_lathe("Fountain_Mid_Basin", (sx, sy, 1.62), [(0.0, 0.0), (1.45, 0.0), (1.66, 0.10), (1.74, 0.24), (1.70, 0.33), (1.55, 0.35), (0.0, 0.35)], STONE, segments=20)
    make_cyl("Fountain_Mid_Water", (sx, sy, 1.98), 1.50, 0.02, WATER, segments=20)
    make_lathe("Fountain_Upper_Pedestal", (sx, sy, 1.99), [(0.0, 0.0), (0.44, 0.0), (0.34, 0.08), (0.26, 0.28), (0.24, 0.50), (0.32, 0.68), (0.42, 0.78), (0.44, 0.80), (0.0, 0.80)], STONE_DK, segments=10)
    make_lathe("Fountain_Upper_Basin", (sx, sy, 2.79), [(0.0, 0.0), (0.72, 0.0), (0.88, 0.10), (0.94, 0.22), (0.88, 0.30), (0.78, 0.30), (0.0, 0.30)], STONE, segments=16)
    make_cyl("Fountain_Upper_Water", (sx, sy, 3.10), 0.74, 0.02, WATER, segments=16)
    make_lathe("Fountain_Finial", (sx, sy, 3.11), [(0.0, 0.0), (0.20, 0.0), (0.14, 0.10), (0.10, 0.30), (0.16, 0.42), (0.06, 0.52), (0.0, 0.56)], STONE_DK, segments=8)
    # water falling from the upper rims: streaks outside the pedestals
    for fi in range(4):
        a = fi * math.pi / 2.0 + math.pi / 4.0
        make_box(f"Fountain_Fall_Upper_{fi}", (sx + 0.92 * math.cos(a), sy + 0.92 * math.sin(a), 2.39), (0.05, 0.05, 0.78), WATER)
        make_box(f"Fountain_Fall_Mid_{fi}", (sx + 1.72 * math.cos(a), sy + 1.72 * math.sin(a), 1.17), (0.05, 0.05, 0.88), WATER)
    # the Major Arcana on the rim of the lower basin: twenty-two figures
    for fi in range(22):
        a = fi * 2.0 * math.pi / 22.0
        fx, fy = sx + 2.9 * math.cos(a), sy + 2.9 * math.sin(a)
        h = 0.10 + 0.04 * (fi % 3)
        make_box(f"Fountain_Figure_{fi}", (fx, fy, 0.70 + h / 2.0), (0.10, 0.10, h), STONE_DK)
        make_box(f"Fountain_Figure_{fi}_Head", (fx, fy, 0.70 + h + 0.03), (0.06, 0.06, 0.06), STONE_DK)
    # the town around the square
    bl = ((-11.0, -33.5, 6.0, 5.0, 6.5, "X"), (-3.0, -34.0, 7.0, 5.5, 7.5, "X"), (6.0, -33.5, 6.5, 5.0, 6.0, "X"),
          (-17.2, -26.0, 5.0, 7.0, 7.0, "Y"), (-17.2, -17.0, 5.0, 6.0, 6.0, "Y"), (17.5, -26.0, 5.0, 7.0, 6.5, "Y"), (17.5, -17.0, 5.0, 6.0, 7.0, "Y"))
    for bi, (bx, by, bw, bd, bh, ax) in enumerate(bl):
        make_box(f"Town_Building_{bi}", (bx, by, bh / 2.0), (bw, bd, bh), WALL if bi % 2 else (0.74, 0.66, 0.56, 1.0))
        make_gable(f"Town_Building_{bi}_Roof", (bx, by, bh + 0.9), (bw + 0.4, bd + 0.4, 1.8), ROOF, ridge_axis=ax)
        for wi in range(3):
            wy = by + (bd / 2.0 + 0.01) if ax == "X" else by - bd / 2.0 + 1.2 + wi * 1.6
            wx = bx - bw / 2.0 + 1.2 + wi * 1.6 if ax == "X" else bx - (bw / 2.0 + 0.01) * (1 if bx > 0 else -1)
            make_box(f"Town_Building_{bi}_Win_{wi}", (wx, wy, 2.0), (0.7 if ax == "X" else 0.02, 0.02 if ax == "X" else 0.7, 1.0), (0.96, 0.80, 0.46, 1.0))
    make_box("Church_Tower", (-3.0, -40.0, 6.0), (3.0, 3.0, 12.0), WALL)
    make_taper_cyl("Church_Spire", (-3.0, -40.0, 14.0), 2.0, 0.0, 4.0, ROOF, segments=4)
    for li, (lx, ly) in enumerate(((-9.0, -14.0), (9.0, -14.0), (-9.0, -30.0), (9.0, -30.0))):
        make_cyl(f"Square_Lamp_{li}_Post", (lx, ly, 1.8), 0.06, 3.6, (0.20, 0.20, 0.22, 1.0), segments=8)
        make_box(f"Square_Lamp_{li}_Head", (lx, ly, 3.75), (0.30, 0.30, 0.30), (0.98, 0.86, 0.56, 1.0))
    # the rest of the town, small, on the valley terrace to the east
    for ti in range(14):
        tx = 32.0 + (ti % 5) * 7.0 + (ti % 2) * 2.0
        ty = -44.0 + (ti // 5) * 9.0 + (ti % 3) * 1.5
        make_box(f"Valley_House_{ti}", (tx, ty, VALLEY_Z + 2.0), (4.0, 4.0, 4.0), WALL if ti % 2 else (0.72, 0.66, 0.56, 1.0))
        make_gable(f"Valley_House_{ti}_Roof", (tx, ty, VALLEY_Z + 4.0 + 0.8), (4.4, 4.4, 1.6), ROOF, ridge_axis="X")
    make_box("Valley_Church_Tower", (48.0, -30.0, VALLEY_Z + 6.0), (2.5, 2.5, 12.0), WALL)
    make_taper_cyl("Valley_Church_Spire", (48.0, -30.0, VALLEY_Z + 14.0), 1.7, 0.0, 4.0, ROOF, segments=4)


def build_horizon():
    make_far_bands("FarRidge", (0.28, 0.32, 0.30),
                   [(150.0, 200.0, 24.0, 0.85), (260.0, 300.0, 30.0, 0.65), (420.0, 420.0, 36.0, 0.48)],
                   sides="ES", cx=40.0, cy=0.0, profile="ridge")


def main():
    clear_scene()
    levels = build_path_and_mountain()
    build_stations(levels)
    build_cloud()
    build_square()
    build_horizon()
    out = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)),
        "../../../assets/3d/locales/kestrel_mountain.glb"))
    print(f"\n[build_kestrel_mountain] exporting to {out}")
    export_glb(out)


if __name__ == "__main__":
    main()
