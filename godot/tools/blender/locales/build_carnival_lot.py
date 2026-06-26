"""VIII · STRENGTH — Abandoned Carnival Lot. Sun-bleached merry-go-
round with chipped paint, faded big-top tent half-erected, striped
ticket booth, the long wagon for the lion cage (empty, door swung
open). Open-air; the 'interior' is the lot — a low limestone wall
marks the property edge.
"""
import os, sys
_BT = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
if _BT not in sys.path: sys.path.insert(0, _BT)
import math
from _props import palette as P
from _props.geometry import clear_scene, make_box, make_cyl, export_glb

COL_DIRT = (0.52, 0.44, 0.32, 1.0); COL_GRASS = (0.46, 0.50, 0.32, 1.0)
COL_LIMESTONE = (0.78, 0.74, 0.66, 1.0); COL_TENT_RED = (0.62, 0.32, 0.30, 1.0)
COL_TENT_WHITE = (0.84, 0.82, 0.74, 1.0); COL_MERRY_BLUE = (0.42, 0.54, 0.66, 1.0)
COL_MERRY_GOLD = (0.74, 0.62, 0.32, 1.0); COL_HORSE_WHITE = (0.86, 0.84, 0.78, 1.0)
COL_HORSE_BROWN = (0.62, 0.42, 0.28, 1.0); COL_BOOTH_STRIPE_R = (0.74, 0.32, 0.28, 1.0)
COL_BOOTH_STRIPE_W = (0.86, 0.84, 0.76, 1.0); COL_CAGE_BARS = (0.38, 0.36, 0.30, 1.0)
COL_WAGON_WOOD = (0.42, 0.30, 0.22, 1.0); COL_FLAG_FADE = (0.62, 0.42, 0.32, 1.0)
COL_SKY = (0.74, 0.78, 0.78, 1.0)

LOT_W = 24.0; LOT_D = 18.0


def build_ground():
    # Dirt lot center, grass perimeter
    make_box("Lot_Dirt", (0.0, 0.0, 0.0), (LOT_W, LOT_D, 0.04), COL_DIRT)
    make_box("Grass_N", (0.0, +LOT_D/2.0 + 2.0, 0.02), (LOT_W + 8.0, 4.0, 0.04), COL_GRASS)
    make_box("Grass_S", (0.0, -LOT_D/2.0 - 2.0, 0.02), (LOT_W + 8.0, 4.0, 0.04), COL_GRASS)
    make_box("Grass_W", (-LOT_W/2.0 - 2.0, 0.0, 0.02), (4.0, LOT_D, 0.04), COL_GRASS)
    make_box("Grass_E", (+LOT_W/2.0 + 2.0, 0.0, 0.02), (4.0, LOT_D, 0.04), COL_GRASS)
    # Sky backdrop
    make_box("SkyBackdrop", (0.0, +LOT_D/2.0 + 20.0, 8.0), (60.0, 0.04, 16.0), COL_SKY)


def build_limestone_wall():
    # Low perimeter wall around the lot, on three sides
    for i in range(12):
        # N edge
        make_box(f"Wall_N_{i}", (-11.0 + i*2.0, +LOT_D/2.0, 0.40), (1.80, 0.30, 0.80),
                 COL_LIMESTONE)
        # S edge
        make_box(f"Wall_S_{i}", (-11.0 + i*2.0, -LOT_D/2.0, 0.40), (1.80, 0.30, 0.80),
                 COL_LIMESTONE)
    for j in range(9):
        make_box(f"Wall_W_{j}", (-LOT_W/2.0, -8.0 + j*2.0, 0.40), (0.30, 1.80, 0.80),
                 COL_LIMESTONE)


def build_big_top():
    # Half-erected big-top tent (3 stripes, conical)
    cx, cy = -6.0, 0.0
    # Center pole
    make_cyl("Tent_Pole", (cx, cy, 4.50), 0.18, 9.00, COL_LIMESTONE, segments=10)
    # Conical tent canopy as stacked cones (16 segments)
    for ti in range(8):
        ang = ti * (math.pi/4)
        for r_i, (r1, r2, z1, z2) in enumerate([(5.50, 0.10, 1.40, 8.50)]):
            # 4 alternating colored strips per slice — approximated as 4 boxes around the cone
            pass
    # Simpler: 8 triangular boxes radiating from the pole
    for ti in range(8):
        ang = ti * (math.pi/4)
        ex = cx + math.cos(ang) * 4.0
        ey = cy + math.sin(ang) * 4.0
        tc = COL_TENT_RED if ti % 2 else COL_TENT_WHITE
        make_box(f"Tent_Slice_{ti}", ((cx+ex)/2.0, (cy+ey)/2.0, 4.50),
                 (3.50, 1.20, 0.20), tc)
    # Top flag
    make_box("Tent_Flag", (cx, cy, 9.50), (0.04, 0.50, 0.40), COL_FLAG_FADE)
    # Hanging cable + half-collapsed side
    make_box("Tent_Cable", (cx+5.50, cy, 2.50), (0.04, 0.04, 4.50), P.METAL_BLACK)
    # 4 anchor stakes
    for sgn_x, sgn_y in [(-1, -1), (+1, -1), (-1, +1), (+1, +1)]:
        ax_, ay_ = cx + sgn_x*5.0, cy + sgn_y*4.0
        make_box(f"Tent_Stake_{sgn_x:+d}_{sgn_y:+d}", (ax_, ay_, 0.40),
                 (0.10, 0.10, 0.80), COL_WAGON_WOOD)


def build_merry_go_round():
    # Sun-bleached carousel — central column + flat roof + 8 horses
    cx, cy = +6.0, 0.0
    # Base
    make_cyl("Carousel_Base", (cx, cy, 0.20), 3.40, 0.40, COL_LIMESTONE, segments=20)
    # Center column
    make_cyl("Carousel_Column", (cx, cy, 2.50), 0.40, 4.20, COL_MERRY_GOLD, segments=12)
    # Flat roof
    make_cyl("Carousel_Roof", (cx, cy, 4.80), 3.60, 0.20, COL_MERRY_BLUE, segments=20)
    # Decorative ring
    make_cyl("Carousel_Ring", (cx, cy, 4.90), 3.40, 0.10, COL_MERRY_GOLD, segments=20)
    # Roof crown (cone abstracted)
    make_cyl("Carousel_Crown", (cx, cy, 5.20), 1.60, 0.30, COL_MERRY_BLUE, segments=12)
    make_cyl("Carousel_FinialBall", (cx, cy, 5.50), 0.20, 0.30, COL_MERRY_GOLD, segments=10)
    # 8 horses on poles
    for hi in range(8):
        ang = hi * (math.pi/4)
        hx = cx + math.cos(ang) * 2.60
        hy = cy + math.sin(ang) * 2.60
        # Vertical pole
        make_cyl(f"Horse_Pole_{hi}", (hx, hy, 1.40), 0.04, 2.80, COL_MERRY_GOLD, segments=8)
        # Horse body
        hc = COL_HORSE_WHITE if hi % 2 else COL_HORSE_BROWN
        make_box(f"Horse_Body_{hi}", (hx, hy, 1.60), (0.80, 0.30, 0.50), hc)
        # Horse head
        make_box(f"Horse_Head_{hi}", (hx + math.cos(ang)*0.40, hy + math.sin(ang)*0.40, 1.90),
                 (0.30, 0.20, 0.30), hc)
        # 4 legs
        for li, (sgn_x, sgn_y) in enumerate([(-1, -1), (+1, -1), (-1, +1), (+1, +1)]):
            make_box(f"Horse_Leg_{hi}_{li}", (hx + sgn_x*0.30, hy + sgn_y*0.10, 1.20),
                     (0.06, 0.06, 0.50), hc)


def build_ticket_booth():
    # Striped octagonal ticket booth near the N entrance
    bx, by = 0.0, +LOT_D/2.0 - 2.0
    make_box("Booth_Base", (bx, by, 0.10), (1.60, 1.60, 0.20), COL_LIMESTONE)
    # Striped walls (5 vertical stripes per side)
    for si in range(5):
        sx = bx - 0.60 + si * 0.30
        sc = COL_BOOTH_STRIPE_R if si % 2 else COL_BOOTH_STRIPE_W
        make_box(f"Booth_Stripe_S_{si}", (sx, by-0.80, 1.20), (0.28, 0.05, 2.20), sc)
        make_box(f"Booth_Stripe_N_{si}", (sx, by+0.80, 1.20), (0.28, 0.05, 2.20), sc)
    for si in range(5):
        sy = by - 0.60 + si * 0.30
        sc = COL_BOOTH_STRIPE_R if si % 2 else COL_BOOTH_STRIPE_W
        make_box(f"Booth_Stripe_W_{si}", (bx-0.80, sy, 1.20), (0.05, 0.28, 2.20), sc)
        make_box(f"Booth_Stripe_E_{si}", (bx+0.80, sy, 1.20), (0.05, 0.28, 2.20), sc)
    # Ticket window (front, S-facing)
    make_box("Booth_Window", (bx, by-0.84, 1.40), (0.50, 0.005, 0.30), (0.78, 0.84, 0.86, 0.55))
    # Conical hat roof
    make_box("Booth_Roof_R", (bx, by, 2.50), (1.80, 1.80, 0.20), COL_BOOTH_STRIPE_R)
    make_box("Booth_Roof_W", (bx, by, 2.70), (1.40, 1.40, 0.20), COL_BOOTH_STRIPE_W)
    make_cyl("Booth_Spire", (bx, by, 3.00), 0.10, 0.60, COL_MERRY_GOLD, segments=8)
    make_box("Booth_Flag", (bx, by, 3.40), (0.04, 0.40, 0.30), COL_FLAG_FADE)


def build_lion_cage_wagon():
    # Empty cage wagon W of carousel — door swung open
    wx, wy = -1.50, -5.50
    # Wagon platform
    make_box("Wagon_Platform", (wx, wy, 0.30), (3.00, 1.60, 0.20), COL_WAGON_WOOD)
    # 4 wheels
    for sgn_x, sgn_y in [(-1, -1), (+1, -1), (-1, +1), (+1, +1)]:
        make_cyl(f"Wagon_Wheel_{sgn_x:+d}_{sgn_y:+d}",
                 (wx + sgn_x*1.10, wy + sgn_y*0.70, 0.30), 0.30, 0.10,
                 COL_WAGON_WOOD, axis='X', segments=10)
    # Cage frame (4 corner posts + bars)
    for sgn_x, sgn_y in [(-1, -1), (+1, -1), (-1, +1), (+1, +1)]:
        make_box(f"Cage_Post_{sgn_x:+d}_{sgn_y:+d}",
                 (wx + sgn_x*1.40, wy + sgn_y*0.70, 1.20), (0.10, 0.10, 1.80), COL_CAGE_BARS)
    # 12 vertical bars on each long side
    for sgn_y in (-1, +1):
        for bi in range(11):
            bx = wx - 1.30 + bi * 0.24
            make_cyl(f"Cage_Bar_S{sgn_y:+d}_{bi}", (bx, wy + sgn_y*0.70, 1.20),
                     0.02, 1.80, COL_CAGE_BARS, segments=6)
    # Cage roof
    make_box("Cage_Roof", (wx, wy, 2.10), (2.80, 1.50, 0.06), COL_CAGE_BARS)
    # Door — swung open at the W end (rotated open ~80°)
    make_box("Cage_Door_OpenLeaf", (wx-2.10, wy-0.30, 1.20), (0.06, 1.20, 1.80), COL_CAGE_BARS)
    # "EMPTY" / faded text plaque on side
    make_box("Cage_Plaque", (wx, wy+0.80, 0.80), (0.80, 0.005, 0.20), (0.92, 0.86, 0.74, 1.0))


def build_strewn_props():
    # A few faded paper signs and tipped barrels
    for bi, (bx, by) in enumerate([(2.0, -7.0), (-3.0, -8.0), (8.0, -6.5)]):
        make_cyl(f"Barrel_{bi}", (bx, by, 0.40), 0.32, 0.80, COL_WAGON_WOOD, segments=8)
    # Faded "STEP RIGHT UP" banner pulled down between two posts
    bp1 = (-5.0, -7.0); bp2 = (-2.0, -7.0)
    make_cyl("BannerPost_1", (bp1[0], bp1[1], 1.40), 0.06, 2.80, COL_WAGON_WOOD, segments=8)
    make_cyl("BannerPost_2", (bp2[0], bp2[1], 1.40), 0.06, 2.80, COL_WAGON_WOOD, segments=8)
    make_box("Banner_Faded", ((bp1[0]+bp2[0])/2.0, bp1[1], 1.40),
             (3.0, 0.005, 0.50), COL_FLAG_FADE)


def build_strength_dressing():
    """Scene-description specifics from setup_the_lion_cage_open.json:
      · "hinges scabbed with rust" on Lila's wagon door
      · Roy's folding chair near the open cage (he's been coming
        every afternoon since September)
      · A small brass plaque on the wagon — Lila's name
      · A feed bucket left in the cage, half-tipped, the way it was
        when she went into the trailer last
    """
    # Existing cage wagon center: (-1.50, -5.50). Door swung open at
    # wx - 2.10 = -3.60. Rust-scabbed hinges at the door pivot.
    wx, wy = -1.50, -5.50
    COL_RUST = (0.42, 0.18, 0.10, 1.0)
    # Two rust-scabbed hinges on the wagon's W door post + the door
    for hz in (0.50, 1.60):
        make_box("Cage_Hinge_Rust_%.1f" % hz,
                 (wx - 1.42, wy - 0.30, hz),
                 (0.18, 0.08, 0.14),
                 COL_RUST)
        # Rust drip below each hinge (a thin streak running down)
        make_box("Cage_Hinge_RustStreak_%.1f" % hz,
                 (wx - 1.42, wy - 0.30, hz - 0.20),
                 (0.05, 0.02, 0.30),
                 (0.32, 0.14, 0.08, 1.0))

    # Roy's folding chair — about 1.5m east of the cage door, facing
    # west toward the open cage
    roy_x, roy_y = -3.20, -5.00
    # Folding chair (light olive canvas, steel frame)
    make_box("Roy_Chair_Seat",
             (roy_x, roy_y, 0.46),
             (0.40, 0.40, 0.04),
             (0.42, 0.46, 0.32, 1.0))
    make_box("Roy_Chair_Back",
             (roy_x, roy_y + 0.18, 0.80),
             (0.40, 0.04, 0.46),
             (0.42, 0.46, 0.32, 1.0))
    for sgn_x, sgn_y in [(-1, -1), (+1, -1), (-1, +1), (+1, +1)]:
        make_box("Roy_Chair_Leg_%+d_%+d" % (sgn_x, sgn_y),
                 (roy_x + sgn_x * 0.18, roy_y + sgn_y * 0.18, 0.23),
                 (0.02, 0.02, 0.46),
                 (0.32, 0.32, 0.32, 1.0))
    # A bottle of something on the ground next to the chair
    make_cyl("Roy_Bottle_Body",
             (roy_x + 0.30, roy_y - 0.10, 0.10),
             0.035, 0.20,
             (0.32, 0.20, 0.12, 0.85),
             segments=8, axis='Z')

    # Lila's plaque on the wagon side (brass, weathered)
    make_box("Cage_LilaPlaque",
             (wx, wy + 0.81, 0.95),
             (0.40, 0.005, 0.12),
             (0.74, 0.56, 0.22, 1.0))
    # Engraved name (darker streak across the plaque)
    make_box("Cage_LilaPlaque_Name",
             (wx, wy + 0.815, 0.95),
             (0.30, 0.003, 0.04),
             (0.20, 0.14, 0.08, 1.0))

    # The feed bucket inside the cage — sitting upright at the back
    # of the cage where it was left when Lila walked out for the
    # last time
    make_cyl("Cage_FeedBucket_Body",
             (wx + 0.30, wy + 0.30, 0.42),
             0.12, 0.24,
             (0.42, 0.32, 0.20, 1.0),
             segments=10, axis='Z')
    # Bucket rim (slightly wider)
    make_cyl("Cage_FeedBucket_Rim",
             (wx + 0.30, wy + 0.30, 0.54),
             0.13, 0.012,
             (0.32, 0.22, 0.14, 1.0),
             segments=10, axis='Z')
    # Some pellets/feed scattered next to the bucket
    for pi in range(5):
        pdx = -0.10 + (pi % 3) * 0.08
        pdy = -0.16 + (pi // 3) * 0.06
        make_box("Cage_Feed_%d" % pi,
                 (wx + 0.20 + pdx, wy + 0.10 + pdy, 0.31),
                 (0.04, 0.04, 0.02),
                 (0.62, 0.46, 0.22, 1.0))


def main():
    clear_scene()
    build_ground()
    build_limestone_wall()
    build_big_top()
    build_merry_go_round()
    build_ticket_booth()
    build_lion_cage_wagon()
    build_strewn_props()
    build_strength_dressing()
    out = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                         "../../../assets/3d/locales/carnival_lot.glb"))
    print(f"\n[build_carnival_lot] exporting to {out}")
    export_glb(out)


if __name__ == "__main__":
    main()
