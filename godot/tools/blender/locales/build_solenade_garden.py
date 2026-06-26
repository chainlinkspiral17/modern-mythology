"""XIX · SUN — Solenade Memorial Garden. Walled garden with a
single oak in the center, brick paths, a simple bronze sundial, a
low limestone bench wall along the perimeter. Open sky overhead.
Frank's dust-motes beat — the most generous light in the whole
arcana sequence.
"""
import os, sys
_BT = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
if _BT not in sys.path: sys.path.insert(0, _BT)
import math
from _props import palette as P
from _props.geometry import clear_scene, make_box, make_cyl, export_glb

COL_BRICK_PATH = (0.62, 0.36, 0.26, 1.0); COL_BRICK_SEAM = (0.42, 0.22, 0.16, 1.0)
COL_GRASS = (0.42, 0.56, 0.32, 1.0); COL_GRASS_DARK = (0.32, 0.46, 0.26, 1.0)
COL_LIMESTONE = (0.86, 0.82, 0.74, 1.0); COL_OAK_TRUNK = (0.42, 0.30, 0.22, 1.0)
COL_OAK_FOLIAGE_HI = (0.62, 0.74, 0.42, 1.0); COL_OAK_FOLIAGE_LO = (0.42, 0.56, 0.30, 1.0)
COL_SUNDIAL = (0.74, 0.56, 0.28, 1.0); COL_SKY = (0.62, 0.78, 0.86, 1.0)
COL_HEDGE = (0.32, 0.46, 0.28, 1.0); COL_FLOWERS_W = (0.96, 0.92, 0.84, 1.0)
COL_FLOWERS_Y = (0.96, 0.86, 0.42, 1.0); COL_FLOWERS_R = (0.96, 0.42, 0.32, 1.0)
COL_BENCH_WOOD = (0.42, 0.30, 0.22, 1.0)

GARDEN_R = 8.0  # radius of the walled garden
WALL_H = 1.20


def build_ground():
    # Grass disc
    make_cyl("Ground_Grass", (0.0, 0.0, 0.0), GARDEN_R + 0.4, 0.04,
             COL_GRASS, segments=32)
    # Cross-axis brick paths (N-S, E-W) intersecting at center
    make_box("Path_NS", (0.0, 0.0, 0.02), (1.20, 2*GARDEN_R, 0.04), COL_BRICK_PATH)
    make_box("Path_EW", (0.0, 0.0, 0.02), (2*GARDEN_R, 1.20, 0.04), COL_BRICK_PATH)
    # Brick seam stripes (subtle parallel lines)
    for si in range(11):
        sx = -GARDEN_R + 0.4 + si * 1.40
        make_box(f"Path_Seam_NS_{si}", (sx, 0.0, 0.025), (0.04, 1.20, 0.005), COL_BRICK_SEAM)
        make_box(f"Path_Seam_EW_{si}", (0.0, sx, 0.025), (1.20, 0.04, 0.005), COL_BRICK_SEAM)
    # Central plaza (slightly larger brick circle)
    make_cyl("Plaza", (0.0, 0.0, 0.025), 1.80, 0.005, COL_BRICK_PATH, segments=20)


def build_perimeter_wall_and_benches():
    # Limestone bench wall hugging the garden perimeter (12 segments)
    SEGS = 12
    for si in range(SEGS):
        ang = si * (2*math.pi/SEGS)
        next_ang = (si+1) * (2*math.pi/SEGS)
        ma = (ang + next_ang)/2.0
        mx = math.cos(ma) * GARDEN_R
        my = math.sin(ma) * GARDEN_R
        # Wall block
        chord = 2 * GARDEN_R * math.sin(math.pi/SEGS)
        make_box(f"Wall_{si}", (mx, my, WALL_H/2.0),
                 (chord*1.05, 0.30, WALL_H), COL_LIMESTONE)
        # Bench seat in front of each wall segment
        bx = math.cos(ma) * (GARDEN_R - 0.50)
        by = math.sin(ma) * (GARDEN_R - 0.50)
        make_box(f"Bench_Seat_{si}", (bx, by, 0.46), (chord*0.65, 0.36, 0.06), COL_BENCH_WOOD)
        # Bench legs (2)
        for sgn in (-1, +1):
            lx = bx + math.cos(ma + math.pi/2) * (sgn * chord*0.25)
            ly = by + math.sin(ma + math.pi/2) * (sgn * chord*0.25)
            make_box(f"Bench_Leg_{si}_{sgn:+d}", (lx, ly, 0.23),
                     (0.06, 0.30, 0.46), COL_BENCH_WOOD)


def build_central_oak():
    # Buttressed base + tall trunk + 4 stacked foliage clusters
    make_cyl("Oak_Base", (0.0, 0.0, 0.50), 1.00, 1.00, COL_OAK_TRUNK, segments=14)
    make_cyl("Oak_Trunk", (0.0, 0.0, 3.50), 0.60, 4.00, COL_OAK_TRUNK, segments=14)
    # Branching foliage (5 clusters)
    foliage_positions = [(0.0, 0.0, 6.50), (1.50, 0.50, 6.80), (-1.20, 1.40, 6.60),
                          (0.80, -1.80, 6.40), (-1.80, -1.00, 6.70)]
    for fi, (fx, fy, fz) in enumerate(foliage_positions):
        # Lower (darker) hemisphere
        make_cyl(f"Oak_Foliage_Lo_{fi}", (fx, fy, fz), 2.20, 1.60, COL_OAK_FOLIAGE_LO, segments=12)
        # Upper (brighter) cap
        make_cyl(f"Oak_Foliage_Hi_{fi}", (fx, fy, fz + 1.20), 1.80, 1.40, COL_OAK_FOLIAGE_HI, segments=12)


def build_sundial():
    # Bronze sundial S of the oak, on a small plinth
    sx, sy = 0.0, -3.40
    make_cyl("Sundial_Plinth", (sx, sy, 0.30), 0.40, 0.60, COL_LIMESTONE, segments=12)
    make_cyl("Sundial_Plate", (sx, sy, 0.66), 0.36, 0.04, COL_SUNDIAL, segments=18)
    # Triangular gnomon (approximated as a thin angled box)
    make_box("Sundial_Gnomon", (sx, sy, 0.74), (0.02, 0.30, 0.18), COL_SUNDIAL)
    # 12 hour ticks around the plate edge
    for hi in range(12):
        ang = hi * (math.pi/6)
        tx = sx + math.cos(ang) * 0.32
        ty = sy + math.sin(ang) * 0.32
        make_box(f"Sundial_Tick_{hi}", (tx, ty, 0.68), (0.02, 0.02, 0.02), COL_OAK_TRUNK)


def build_hedges_and_flowerbeds():
    # Four flowerbeds in the quadrants between the cross paths
    for qi, (qx, qy) in enumerate([(+3.0, +3.0), (-3.0, +3.0), (-3.0, -3.0), (+3.0, -3.0)]):
        # Hedge border (low square)
        make_box(f"Hedge_{qi}_N", (qx, qy + 1.40, 0.40), (3.20, 0.20, 0.40), COL_HEDGE)
        make_box(f"Hedge_{qi}_S", (qx, qy - 1.40, 0.40), (3.20, 0.20, 0.40), COL_HEDGE)
        make_box(f"Hedge_{qi}_W", (qx - 1.40, qy, 0.40), (0.20, 3.20, 0.40), COL_HEDGE)
        make_box(f"Hedge_{qi}_E", (qx + 1.40, qy, 0.40), (0.20, 3.20, 0.40), COL_HEDGE)
        # Flowers inside (a few dots of each colour)
        for fi in range(9):
            fc = [COL_FLOWERS_W, COL_FLOWERS_Y, COL_FLOWERS_R][fi % 3]
            fx = qx - 1.0 + (fi % 3) * 1.0
            fy = qy - 1.0 + (fi // 3) * 1.0
            make_cyl(f"Flower_{qi}_{fi}", (fx, fy, 0.30), 0.18, 0.02, fc, segments=8)


def build_pergola_arch_at_n_entry():
    # Simple wooden pergola arch at the N entrance to the cross path
    for sgn_x in (-1, +1):
        make_box(f"Pergola_Post_N_{sgn_x:+d}", (sgn_x*0.80, GARDEN_R - 0.20, 1.30),
                 (0.10, 0.10, 2.60), COL_BENCH_WOOD)
    make_box("Pergola_Top", (0.0, GARDEN_R - 0.20, 2.70), (1.80, 0.30, 0.10), COL_BENCH_WOOD)
    # Climbing vine on it
    for vi in range(6):
        make_cyl(f"PergolaVine_{vi}", (-0.60 + vi*0.24, GARDEN_R - 0.20, 1.80),
                 0.04, 1.20, COL_OAK_FOLIAGE_LO, segments=6)


def build_sky_and_sun():
    # Sky dome (large box backdrop in cross of cardinal axes)
    make_box("Sky_N", (0.0, GARDEN_R + 14.0, 8.0), (40.0, 0.04, 16.0), COL_SKY)
    make_box("Sky_S", (0.0, -GARDEN_R - 14.0, 8.0), (40.0, 0.04, 16.0), COL_SKY)
    make_box("Sky_W", (-GARDEN_R - 14.0, 0.0, 8.0), (0.04, 40.0, 16.0), COL_SKY)
    make_box("Sky_E", (+GARDEN_R + 14.0, 0.0, 8.0), (0.04, 40.0, 16.0), COL_SKY)
    # A faint sun disc to the SE
    make_cyl("SunDisc", (+8.0, -10.0, 11.0), 1.20, 0.04, (0.96, 0.92, 0.78, 1.0),
             axis='Y', segments=20)


def build_sun_dressing():
    """Scene-description specifics from setup_the_work_is_to_sit.json:
      · Frank's specific east bench under the central oak (already
        built, but mark the bench with a slightly-worn seat where
        Frank has sat every Wednesday since November) + a small
        brass plaque on the bench
      · The open Galway Kinnell book lying face-down on the bench
        next to the wear spot (Frank's reading position)
      · Pepper the Bouchon's spaniel · a low-poly dog roaming the
        garden, currently at a bench two away from Frank's
      · The afternoon shadow under the oak · a slightly-darker
        circle on the grass marking the canopy's current
        projection (2:18 PM, before the 3-hour drift)
    """
    # Central oak approx at (0, 0); east bench at (+3.5, 0) facing west
    bench_cx = +3.5
    bench_cy = 0.0
    bench_seat_z = 0.44

    # Worn wear-patch on Frank's seat
    make_box("Frank_Bench_WearPatch",
             (bench_cx - 0.20, bench_cy, bench_seat_z + 0.045),
             (0.40, 0.30, 0.005),
             (0.30, 0.20, 0.12, 1.0))   # darker wood from wear
    # Small brass plaque on the bench back
    make_box("Frank_Bench_Plaque",
             (bench_cx, bench_cy + 0.18, bench_seat_z + 0.40),
             (0.16, 0.005, 0.05),
             (0.78, 0.62, 0.30, 1.0))
    # Engraved text on the plaque (dark slot)
    make_box("Frank_Bench_Plaque_Engraving",
             (bench_cx, bench_cy + 0.181, bench_seat_z + 0.40),
             (0.12, 0.001, 0.020),
             (0.18, 0.14, 0.10, 1.0))

    # The open Galway Kinnell book, face-down on the bench seat
    make_box("Kinnell_Book_Cover",
             (bench_cx + 0.16, bench_cy + 0.04, bench_seat_z + 0.06),
             (0.14, 0.20, 0.020),
             (0.42, 0.32, 0.20, 1.0))   # forest-green cloth
    # Slightly-visible top of pages (the book is face down, so this
    # is the bottom edge of the open pages showing)
    make_box("Kinnell_Book_PagesEdge",
             (bench_cx + 0.16, bench_cy + 0.04, bench_seat_z + 0.073),
             (0.13, 0.19, 0.001),
             (0.94, 0.90, 0.80, 1.0))
    # A bookmark ribbon sticking out
    make_box("Kinnell_Book_Bookmark",
             (bench_cx + 0.16, bench_cy + 0.14, bench_seat_z + 0.078),
             (0.012, 0.20, 0.001),
             (0.62, 0.20, 0.18, 1.0))   # red satin ribbon

    # Pepper the Bouchon's spaniel — currently two benches away
    # to the SE
    pep_x = +1.0
    pep_y = -2.5
    # Body
    make_box("Pepper_Body",
             (pep_x, pep_y, 0.18),
             (0.40, 0.22, 0.18),
             (0.94, 0.86, 0.66, 1.0))   # spaniel cream
    # Head
    make_box("Pepper_Head",
             (pep_x - 0.22, pep_y, 0.22),
             (0.16, 0.16, 0.14),
             (0.94, 0.86, 0.66, 1.0))
    # Ears (two pendulous flaps)
    for sgn in (-1, +1):
        make_box("Pepper_Ear_%+d" % sgn,
                 (pep_x - 0.22, pep_y + sgn * 0.08, 0.16),
                 (0.08, 0.04, 0.10),
                 (0.62, 0.46, 0.26, 1.0))   # brown
    # Tail
    make_box("Pepper_Tail",
             (pep_x + 0.22, pep_y, 0.22),
             (0.10, 0.04, 0.06),
             (0.94, 0.86, 0.66, 1.0))
    # 4 paws
    for sx in (-1, +1):
        for sy in (-1, +1):
            make_box("Pepper_Paw_%+d_%+d" % (sx, sy),
                     (pep_x + sx * 0.16, pep_y + sy * 0.08, 0.04),
                     (0.06, 0.06, 0.04),
                     (0.94, 0.86, 0.66, 1.0))

    # Afternoon shadow under the oak — darker circle on the grass
    make_cyl("OakShadow_Current",
             (0.0, 0.0, 0.001),
             3.20, 0.001,
             (0.20, 0.30, 0.18, 1.0),
             segments=14, axis='Z')
    # A second slightly-larger lighter ring beyond — the shadow will
    # drift into this over the next 3 hours
    make_cyl("OakShadow_3HourDrift_Ring",
             (0.40, 0.0, 0.0005),
             3.40, 0.001,
             (0.30, 0.40, 0.28, 0.4),
             segments=14, axis='Z')


def main():
    clear_scene()
    build_ground()
    build_perimeter_wall_and_benches()
    build_central_oak()
    build_sundial()
    build_hedges_and_flowerbeds()
    build_pergola_arch_at_n_entry()
    build_sky_and_sun()
    build_sun_dressing()
    out = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                         "../../../assets/3d/locales/solenade_garden.glb"))
    print(f"\n[build_solenade_garden] exporting to {out}")
    export_glb(out)


if __name__ == "__main__":
    main()
