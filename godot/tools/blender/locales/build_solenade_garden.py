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


def build_sun_wave2_props():
    """Named props from setup_the_ten_am_watering.json and
    setup_the_shared_bench.json. Additive to build_sun_dressing.

    the_ten_am_watering (Saturday 10:14 AM · pre-shift with Bouchon):
      · Perimeter tap on the south wall where Bouchon runs both hoses
      · Two garden hoses coiled on the pergola arch's crossbeam
      · Old brass wand + new plastic-tipped wand on the ground
        against the pergola post
      · Bouchon's thermos + two enamel mugs on the central-oak bench
        (blue-striped enamel · the Wave-2 detail)
      · Salvia bed at NW · dark-green-heavy looking, water beading
        on the leaves from Tuesday

    the_shared_bench (Wednesday 2:04 PM · six weeks after):
      · Rufus Wagner sitting on Frank's oak bench (dressed in a
        Sunday jacket on a Wednesday · a folded newspaper next to him)
      · Rufus's hat in his hands (a straw fedora on the bench arm)
      · The south bench across the path (Frank's new home for the
        afternoon)
      · The east bench behind the oak (visible but not sat on)
    """
    # ── the_ten_am_watering ─────────────────────────────────────

    # Perimeter tap on the south wall · south = -Y in our coord frame
    tap_x = 0.0
    tap_y = -GARDEN_R + 0.20
    tap_z = 0.40
    make_cyl("Tap_Body",
             (tap_x, tap_y, tap_z),
             0.03, 0.14,
             (0.62, 0.62, 0.60, 1.0), segments=8, axis='Z')
    make_cyl("Tap_Handle",
             (tap_x, tap_y - 0.08, tap_z + 0.14),
             0.02, 0.10,
             (0.72, 0.68, 0.62, 1.0), segments=6, axis='Y')
    make_cyl("Tap_Spout",
             (tap_x, tap_y - 0.06, tap_z + 0.04),
             0.014, 0.06,
             (0.62, 0.62, 0.60, 1.0), segments=8, axis='Y')

    # Two garden hoses coiled on the pergola arch's crossbeam
    # (Pergola is at N entry · approximately (0, GARDEN_R-0.6, ...))
    pergola_x = 0.0
    pergola_y = GARDEN_R - 0.60
    hose_z = 2.00   # coiled around the crossbeam
    for hi, (dx, col) in enumerate([(-0.20, (0.24, 0.62, 0.30, 1.0)),
                                     (+0.20, (0.22, 0.30, 0.44, 1.0))]):
        # Coil represented as a stubby torus (approximation via a
        # short vertical cylinder in the pergola's shadow)
        make_cyl("PergolaHose_Coil_%d" % hi,
                 (pergola_x + dx, pergola_y, hose_z),
                 0.10, 0.06,
                 col, segments=10, axis='Z')

    # Two wands leaning against a pergola post · brass one + plastic-
    # tipped new one
    make_cyl("Wand_BrassOld_Shaft",
             (pergola_x - 0.60, pergola_y + 0.20, 0.60),
             0.010, 1.20,
             (0.78, 0.62, 0.30, 1.0), segments=6, axis='Z')
    make_cyl("Wand_BrassOld_Tip",
             (pergola_x - 0.60, pergola_y + 0.20, 1.18),
             0.020, 0.08,
             (0.68, 0.52, 0.24, 1.0), segments=8, axis='Z')
    make_cyl("Wand_NewPlastic_Shaft",
             (pergola_x - 0.50, pergola_y + 0.20, 0.60),
             0.012, 1.20,
             (0.72, 0.74, 0.76, 1.0), segments=6, axis='Z')
    make_cyl("Wand_NewPlastic_Tip",
             (pergola_x - 0.50, pergola_y + 0.20, 1.18),
             0.024, 0.10,
             (0.42, 0.68, 0.44, 1.0), segments=8, axis='Z')  # green

    # Bouchon's thermos + two enamel mugs on the central-oak bench
    # (bench at (+3.5, 0), seat_z = 0.44). Mugs canonically blue-
    # striped enamel · we approximate with white body + blue rim.
    bench_cx = +3.5
    bench_cy = 0.0
    seat_z = 0.44
    make_cyl("Bouchon_Thermos_Body",
             (bench_cx - 0.14, bench_cy - 0.06, seat_z + 0.12),
             0.04, 0.24,
             (0.42, 0.20, 0.16, 1.0), segments=10, axis='Z')
    make_cyl("Bouchon_Thermos_Cap",
             (bench_cx - 0.14, bench_cy - 0.06, seat_z + 0.25),
             0.045, 0.03,
             (0.28, 0.18, 0.14, 1.0), segments=10, axis='Z')
    for mi, dx in enumerate([+0.08, +0.18]):
        make_cyl("Bouchon_Mug_%d_Body" % mi,
                 (bench_cx + dx, bench_cy - 0.06, seat_z + 0.05),
                 0.035, 0.09,
                 (0.94, 0.92, 0.90, 1.0), segments=8, axis='Z')
        # Blue rim stripe
        make_cyl("Bouchon_Mug_%d_Rim" % mi,
                 (bench_cx + dx, bench_cy - 0.06, seat_z + 0.10),
                 0.036, 0.008,
                 (0.24, 0.42, 0.68, 1.0), segments=8, axis='Z')

    # Salvia bed at NW · dark-green heavy looking
    salvia_x = -3.5
    salvia_y = +3.5
    # Elevated bed frame (limestone)
    make_box("SalviaBed_Frame_N",
             (salvia_x, salvia_y + 0.40, 0.08),
             (1.20, 0.06, 0.16),
             COL_LIMESTONE)
    make_box("SalviaBed_Frame_S",
             (salvia_x, salvia_y - 0.40, 0.08),
             (1.20, 0.06, 0.16),
             COL_LIMESTONE)
    make_box("SalviaBed_Frame_E",
             (salvia_x + 0.58, salvia_y, 0.08),
             (0.06, 0.80, 0.16),
             COL_LIMESTONE)
    make_box("SalviaBed_Frame_W",
             (salvia_x - 0.58, salvia_y, 0.08),
             (0.06, 0.80, 0.16),
             COL_LIMESTONE)
    # Salvia plants (dark green heavy)
    for pi, (dx, dy) in enumerate([(-0.30, -0.20), (-0.10, +0.10), (+0.20, -0.10),
                                    (+0.30, +0.20), (+0.10, -0.20)]):
        # Plant base
        make_cyl("SalviaBed_Plant_%d" % pi,
                 (salvia_x + dx, salvia_y + dy, 0.28),
                 0.10, 0.30,
                 (0.22, 0.38, 0.20, 1.0), segments=6, axis='Z')  # dark green
        # Flower stalks (deep purple, indicating salvia)
        make_cyl("SalviaBed_Flower_%d" % pi,
                 (salvia_x + dx, salvia_y + dy, 0.50),
                 0.03, 0.16,
                 (0.32, 0.20, 0.42, 1.0), segments=6, axis='Z')

    # ── the_shared_bench ────────────────────────────────────────

    # Rufus's folded newspaper on the oak bench (S side of Frank's
    # spot · the bench_cx already has Frank's wear-patch)
    make_box("Rufus_Newspaper",
             (bench_cx + 0.06, bench_cy + 0.20, seat_z + 0.045),
             (0.14, 0.18, 0.010),
             (0.88, 0.86, 0.80, 1.0))
    # Small newspaper text lines (visible fold)
    for ni in range(4):
        make_box("Rufus_Newspaper_Line_%d" % ni,
                 (bench_cx + 0.06, bench_cy + 0.14 + ni * 0.032, seat_z + 0.052),
                 (0.10, 0.014, 0.0005),
                 (0.24, 0.22, 0.20, 1.0))

    # Rufus's straw fedora resting on the bench arm
    fedora_x = bench_cx + 0.24
    fedora_y = bench_cy + 0.24
    fedora_z = seat_z + 0.06
    make_cyl("Rufus_Fedora_Brim",
             (fedora_x, fedora_y, fedora_z),
             0.14, 0.010,
             (0.82, 0.68, 0.42, 1.0), segments=12, axis='Z')
    make_cyl("Rufus_Fedora_Crown",
             (fedora_x, fedora_y, fedora_z + 0.05),
             0.08, 0.10,
             (0.82, 0.68, 0.42, 1.0), segments=10, axis='Z')
    # Dark band around the crown
    make_cyl("Rufus_Fedora_Band",
             (fedora_x, fedora_y, fedora_z + 0.01),
             0.081, 0.015,
             (0.32, 0.24, 0.18, 1.0), segments=10, axis='Z')

    # The south bench across the path from the oak (Frank's new
    # afternoon home). Approximate at (0, -3.5)
    south_bench_x = 0.0
    south_bench_y = -3.5
    make_box("SouthBench_Seat",
             (south_bench_x, south_bench_y, 0.44),
             (0.80, 0.30, 0.06),
             COL_BENCH_WOOD)
    make_box("SouthBench_Back",
             (south_bench_x, south_bench_y - 0.14, 0.72),
             (0.80, 0.06, 0.36),
             COL_BENCH_WOOD)
    # Two iron legs
    for sx in (-1, +1):
        make_cyl("SouthBench_Leg_%+d" % sx,
                 (south_bench_x + sx * 0.34, south_bench_y, 0.22),
                 0.02, 0.44,
                 (0.20, 0.18, 0.18, 1.0), segments=6, axis='Z')

    # The east bench (behind the oak trunk · visible but not sat on)
    east_bench_x = +0.30   # just SE of the oak trunk
    east_bench_y = -0.70
    make_box("EastBench_Seat",
             (east_bench_x, east_bench_y, 0.44),
             (0.70, 0.28, 0.06),
             COL_BENCH_WOOD)
    make_box("EastBench_Back",
             (east_bench_x, east_bench_y - 0.13, 0.72),
             (0.70, 0.06, 0.36),
             COL_BENCH_WOOD)


def build_sun_props_pass():
    """Scene-standard PROPS pass (2026-07-13). This garden was already
    dense, but the identity lacked a FOUNTAIN/BIRDBATH and GARDEN LAMPS.
    Add both as compound props (garden-lamp practicals go in the tscn).
    (Outdoor origin-centered garden; no +Z audit applies — the two
    existing bounce omnis are left untouched.)
    """
    # ── Birdbath on the W path arm ──
    bb_x, bb_y = -5.0, 0.0
    make_cyl("Birdbath_Base", (bb_x, bb_y, 0.10), 0.34, 0.20, COL_LIMESTONE, segments=14)
    make_cyl("Birdbath_Column", (bb_x, bb_y, 0.55), 0.14, 0.70, COL_LIMESTONE, segments=12)
    make_cyl("Birdbath_Bowl", (bb_x, bb_y, 0.94), 0.42, 0.14, COL_LIMESTONE, segments=18)
    make_cyl("Birdbath_Water", (bb_x, bb_y, 0.99), 0.36, 0.02,
             (0.58, 0.74, 0.82, 0.80), segments=18)
    make_box("Birdbath_Bird_Body", (bb_x + 0.34, bb_y, 1.04), (0.08, 0.06, 0.08),
             (0.42, 0.42, 0.46, 1.0))
    make_box("Birdbath_Bird_Head", (bb_x + 0.40, bb_y, 1.10), (0.05, 0.05, 0.05),
             (0.42, 0.42, 0.46, 1.0))
    make_box("Birdbath_Bird_Tail", (bb_x + 0.28, bb_y, 1.06), (0.06, 0.03, 0.03),
             (0.34, 0.34, 0.38, 1.0))

    # ── A pair of garden path lamps flanking the N entry path ──
    for li, lx in enumerate([-1.5, +1.5]):
        ly = 5.8
        make_cyl("GardenLamp_%d_Base" % li, (lx, ly, 0.10), 0.12, 0.20,
                 (0.24, 0.22, 0.20, 1.0), segments=10)
        make_cyl("GardenLamp_%d_Post" % li, (lx, ly, 1.20), 0.05, 2.00,
                 (0.24, 0.22, 0.20, 1.0), segments=8)
        for cxo, cyo in [(-1, -1), (1, -1), (-1, 1), (1, 1)]:
            make_box("GardenLamp_%d_Frame_%+d_%+d" % (li, cxo, cyo),
                     (lx + cxo*0.10, ly + cyo*0.10, 2.35), (0.03, 0.03, 0.34),
                     (0.24, 0.22, 0.20, 1.0))
        make_box("GardenLamp_%d_Glass" % li, (lx, ly, 2.35), (0.18, 0.18, 0.30),
                 (0.98, 0.90, 0.62, 0.6))
        make_box("GardenLamp_%d_Cap" % li, (lx, ly, 2.56), (0.28, 0.28, 0.06),
                 (0.24, 0.22, 0.20, 1.0))
        make_cyl("GardenLamp_%d_Finial" % li, (lx, ly, 2.64), 0.03, 0.10,
                 (0.74, 0.56, 0.28, 1.0), segments=8)


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
    build_sun_wave2_props()
    build_sun_props_pass()
    out = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                         "../../../assets/3d/locales/solenade_garden.glb"))
    print(f"\n[build_solenade_garden] exporting to {out}")
    export_glb(out)


if __name__ == "__main__":
    main()
