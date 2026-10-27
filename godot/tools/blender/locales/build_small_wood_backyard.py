"""small_wood_backyard — vol 2's "mayhune": her fifteenth birthday in the
backyard, Small Wood, Oregon, the late 1990s (draft 1, 2026-10-27).

It played on vol 6's 2026 Texas backyard (Kowalski's). The text:
  "Her family had set-up a large table out in the backyard. It was summer,
   of course."; "The small children played in a sprinkler, on a slip and
   slide. The bright husks of broken water balloons were not well hidden in
   the tall grass."; "He would sit in the grass, let his brothers and
   sisters wrestle him to the wet carpet."; "He drank cherry soda"; "a mash
   of cake and cream"; "The sound of a fog horn off in the distance, birds
   overhead."; she "loved animals and was preoccupied with breeding rabbits"
   (at nine — the hutches are still along the fence).
                                         → small_wood_backyard_party

PROPOSED: the house (a 1970s single-storey with a deck and a slider), the
fence, the colours of everything. Late-90s Oregon coast: grey-bright summer
sky, Douglas fir over the fence, a cedar-board fence silvered by weather.

Blender: x east, y north, z up; Godot (x, z, -y). The house's back wall
on y 0 facing north into the yard (y 0..24, x -12..12), the firs past
the back fence at y 26.

DRAFT 2 targets: the kids in the sprinkler as figures with a pose; the
presents unwrapped on the table; her window above (her room, which the
scene goes up to after); the neighbours' roofs; Deck framing.
"""
import os, sys, math
_BT = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
if _BT not in sys.path: sys.path.insert(0, _BT)
from _props.geometry import (clear_scene, make_box, make_cyl, make_rot_box, make_blob, make_tube,
                             join_stock, export_glb)
from _props.trees import make_conifer, make_shrub
from _props.furniture import make_chair

GRASS = (0.34, 0.46, 0.24, 1.0)
GRASS_TALL = (0.42, 0.50, 0.28, 1.0)
WET = (0.24, 0.36, 0.20, 1.0)
SIDING = (0.70, 0.66, 0.54, 1.0)
TRIM = (0.92, 0.90, 0.84, 1.0)
DECK = (0.52, 0.40, 0.28, 1.0)
FENCE = (0.58, 0.56, 0.52, 1.0)
FIR = (0.12, 0.24, 0.16, 1.0)
TRUNK = (0.30, 0.22, 0.16, 1.0)


def _rng(seed):
    s = [seed & 0x7fffffff or 1]
    def r():
        s[0] = (s[0] * 1103515245 + 12345) & 0x7fffffff
        return s[0] / 0x7fffffff
    return r


def build_house():
    """The back of a single-storey 1970s house: siding, two windows, the
    sliding glass door onto a low deck, the eave and the roof."""
    make_box("House_Back_Wall", (0.0, -0.1, 1.4), (18.0, 0.2, 2.8), SIDING)
    for k in range(14):
        make_box(f"House_Siding_Line_{k}", (0.0, 0.005, 0.2 + k * 0.2), (18.0, 0.01, 0.02), (0.60, 0.56, 0.46, 1.0))
    for k, wx in enumerate((-6.0, 5.4)):
        make_box(f"House_Window_{k}", (wx, 0.02, 1.6), (1.6, 0.04, 1.1), (0.30, 0.34, 0.36, 1.0))
        make_box(f"House_Window_{k}_Trim", (wx, 0.03, 1.6), (1.8, 0.02, 1.3), TRIM)
        make_box(f"House_Window_{k}_Glass", (wx, 0.05, 1.6), (1.6, 0.01, 1.1), (0.30, 0.34, 0.36, 1.0))
    make_box("Slider_Frame", (0.0, 0.03, 1.05), (2.4, 0.04, 2.1), TRIM)
    make_box("Slider_Glass", (0.0, 0.05, 1.05), (2.2, 0.01, 1.95), (0.32, 0.38, 0.40, 1.0))
    make_box("House_Eave", (0.0, 0.6, 2.9), (18.6, 1.4, 0.16), TRIM)
    make_rot_box("House_Roof", (0.0, -2.6, 3.9), (18.8, 7.0, 0.2), (0.30, 0.28, 0.28, 1.0), roll=-0.32)
    make_box("Deck", (0.0, 1.8, 0.25), (8.0, 3.6, 0.10), DECK)
    for k in range(4):
        make_box(f"Deck_Step_{k}", (0.0, 3.8 + k * 0.0, 0.10), (2.0, 0.5, 0.20), DECK)
    for k in range(9):
        make_box(f"Deck_Board_Seam_{k}", (-4.0 + k * 1.0, 1.8, 0.302), (0.02, 3.6, 0.004), (0.40, 0.30, 0.20, 1.0))
    make_box("Deck_Grill", (3.2, 1.2, 0.75), (0.6, 0.5, 0.8), (0.12, 0.12, 0.12, 1.0))
    make_cyl("Deck_Grill_Lid", (3.2, 1.2, 1.25), 0.32, 0.25, (0.12, 0.12, 0.12, 1.0), segments=12)


def build_yard():
    """The yard: lawn, its long-grass edges, the cedar fence, the hutches,
    the firs beyond."""
    make_box("Lawn", (0.0, 12.0, -0.03), (26.0, 26.0, 0.06), GRASS)
    make_box("Ground_Beyond", (0.0, 20.0, -0.08), (160.0, 120.0, 0.04), (0.28, 0.36, 0.22, 1.0))
    r = _rng(1997)
    for k in range(70):
        side = k % 3
        if side == 0:
            gx, gy = -11.5 + r() * 1.6, 2.0 + r() * 22.0
        elif side == 1:
            gx, gy = 9.9 + r() * 1.6, 2.0 + r() * 22.0
        else:
            gx, gy = -11.0 + r() * 22.0, 22.4 + r() * 1.4
        make_shrub(f"TallGrass_Stock_{k}", gx, gy, h=0.35 + r() * 0.3, r=0.3 + r() * 0.25, col=GRASS_TALL, segments=6)
    # the cedar-board fence, silvered
    for name, a, b in (("W", (-12.0, 0.0), (-12.0, 24.0)), ("E", (12.0, 0.0), (12.0, 24.0)), ("N", (-12.0, 24.0), (12.0, 24.0))):
        L = math.hypot(b[0] - a[0], b[1] - a[1])
        ax = 'X' if b[1] == a[1] else 'Y'
        cx, cy = (a[0] + b[0]) / 2.0, (a[1] + b[1]) / 2.0
        make_box(f"Fence_{name}", (cx, cy, 0.9), (L if ax == 'X' else 0.05, L if ax == 'Y' else 0.05, 1.8), FENCE)
        n = int(L / 2.4)
        for k in range(n + 1):
            t = k / n
            px, py = a[0] + (b[0] - a[0]) * t, a[1] + (b[1] - a[1]) * t
            make_box(f"Fence_{name}_Post_{k}", (px, py, 0.95), (0.10, 0.10, 1.9), (0.48, 0.46, 0.42, 1.0))
    # the rabbit hutches along the east fence (she bred rabbits at nine)
    for k in range(3):
        hy = 15.0 + k * 1.4
        make_box(f"Hutch_{k}", (11.1, hy, 0.9), (1.0, 1.2, 0.7), (0.56, 0.48, 0.36, 1.0))
        make_box(f"Hutch_{k}_Mesh", (10.59, hy, 0.95), (0.02, 1.0, 0.5), (0.42, 0.42, 0.40, 1.0))
        for s in (-1, 1):
            make_box(f"Hutch_{k}_Leg_{s:+d}", (11.1, hy + s * 0.5, 0.28), (0.08, 0.08, 0.56), (0.40, 0.32, 0.24, 1.0))
    make_blob("Rabbit", (10.9, 16.4, 1.30), 0.14, (0.86, 0.82, 0.76, 1.0), noise=0.1, seed=3, squash=0.8)
    # Douglas fir over the back fence
    for k in range(16):
        make_conifer(f"Fir_Stock_{k}", -30.0 + k * 4.0 + r() * 2.0, 30.0 + r() * 14.0, 18.0 + r() * 14.0, FIR, TRUNK, skirt=0.24)


def build_party():
    """The table, the sprinkler and the slip and slide, the balloon husks."""
    tx, ty = -3.0, 8.0
    make_box("Party_Table_Top", (tx, ty, 0.74), (3.6, 1.0, 0.04), (0.96, 0.94, 0.90, 1.0))
    make_box("Party_Tablecloth", (tx, ty, 0.60), (3.7, 1.1, 0.28), (0.90, 0.56, 0.62, 1.0))
    for sx in (-1, 1):
        for sy in (-1, 1):
            make_box(f"Party_Table_Leg_{sx:+d}{sy:+d}", (tx + sx * 1.6, ty + sy * 0.4, 0.36), (0.05, 0.05, 0.72), (0.70, 0.70, 0.70, 1.0))
    make_cyl("Party_Cake", (tx - 0.4, ty, 0.84), 0.20, 0.16, (0.96, 0.90, 0.86, 1.0), segments=16)
    make_cyl("Party_Cake_Cut", (tx - 0.4, ty - 0.1, 0.92), 0.06, 0.02, (0.56, 0.30, 0.22, 1.0), segments=8)
    for k in range(6):
        make_cyl(f"Party_Plate_{k}", (tx - 1.4 + k * 0.55, ty + (0.32 if k % 2 else -0.32), 0.765), 0.11, 0.01, (0.96, 0.96, 0.94, 1.0), segments=12)
    for k in range(5):
        make_cyl(f"Party_Soda_{k}", (tx - 1.2 + k * 0.6, ty + 0.1, 0.82), 0.033, 0.12, (0.78, 0.10, 0.20, 1.0), segments=8)   # cherry soda
    for k, col in enumerate(((0.30, 0.50, 0.86, 1.0), (0.96, 0.80, 0.24, 1.0), (0.40, 0.76, 0.46, 1.0))):
        make_box(f"Party_Present_{k}", (tx + 0.8 + k * 0.32, ty - 0.1, 0.84), (0.26, 0.24, 0.18), col)
    make_box("Party_Ice_Cream", (tx + 0.2, ty + 0.3, 0.82), (0.18, 0.14, 0.12), (0.92, 0.88, 0.80, 1.0))
    # folding chairs along both long sides, one pushed back where she sat
    for k, (cx_, cy_, yaw) in enumerate(((tx - 1.0, ty - 0.85, 0.0), (tx + 0.4, ty - 0.85, 0.0),
                                          (tx - 1.0, ty + 0.85, math.pi), (tx + 0.4, ty + 1.15, math.pi + 0.2))):
        make_chair(f"Party_Chair_{k}", cx_, cy_, yaw=yaw, wood=(0.86, 0.86, 0.84, 1.0))
    # the slip and slide down the lawn, the sprinkler at its head, wet grass round both
    make_box("SlipSlide", (4.5, 13.0, 0.012), (1.0, 7.0, 0.01), (0.96, 0.84, 0.20, 1.0))
    make_box("SlipSlide_Stripe", (4.5, 13.0, 0.014), (0.16, 7.0, 0.01), (0.20, 0.50, 0.86, 1.0))
    make_box("Wet_Grass", (4.5, 13.0, 0.002), (3.2, 9.0, 0.004), WET)
    make_cyl("Sprinkler_Base", (4.5, 9.0, 0.04), 0.10, 0.06, (0.30, 0.60, 0.30, 1.0), segments=10)
    make_box("Sprinkler_Arm", (4.5, 9.0, 0.10), (0.60, 0.04, 0.03), (0.60, 0.62, 0.64, 1.0))
    make_tube("Garden_Hose", [(4.5, 9.0, 0.03), (6.0, 6.0, 0.03), (7.5, 3.0, 0.03), (8.5, 0.3, 0.3)], 0.02, (0.20, 0.44, 0.22, 1.0), segments=5)
    r = _rng(15)
    for k in range(18):
        bx = -10.6 + r() * 2.2 if k % 2 else 9.0 + r() * 2.0
        by = 3.0 + r() * 19.0
        make_box(f"Balloon_Husk_Stock_{k}", (bx, by, 0.04), (0.10, 0.07, 0.01),
                 ((0.96, 0.30, 0.40, 1.0), (0.30, 0.60, 0.96, 1.0), (0.96, 0.86, 0.24, 1.0), (0.50, 0.86, 0.40, 1.0))[k % 4])


def main():
    clear_scene()
    build_house()
    build_yard()
    build_party()
    try:
        join_stock()
    except Exception as _e:
        print("[join_stock] skipped:", _e)
    out = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                        "../../../assets/3d/locales/small_wood_backyard.glb"))
    print(f"\n[build_small_wood_backyard] exporting to {out}")
    export_glb(out)


if __name__ == "__main__":
    main()
