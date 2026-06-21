"""IX · HERMIT — Bayou Lighthouse. Interior of the 18m tall
whitewashed brick lighthouse on a cypress-pile platform. Spiral
iron staircase corkscrewing up the central wall, brass Fresnel
lens visible at the top through a hatch, a single keeper's bunk
and writing desk on the ground floor. Cypress-water view through
the lower window.
"""
import os, sys
_BT = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
if _BT not in sys.path: sys.path.insert(0, _BT)
import math
from _props import palette as P
from _props.geometry import clear_scene, make_box, make_cyl, export_glb
from _props.structure import make_floor, make_ceiling
from _props.decor import make_wall_clock, make_calendar
from _props.safety import make_smoke_detector, make_sprinkler

COL_BRICK_WHITE = (0.86, 0.84, 0.78, 1.0); COL_BRICK_SEAM = (0.62, 0.58, 0.52, 1.0)
COL_FLOOR_PLANK = (0.62, 0.42, 0.28, 1.0); COL_FLOOR_SEAM = (0.32, 0.22, 0.16, 1.0)
COL_STAIR_IRON = (0.32, 0.30, 0.28, 1.0); COL_BRASS = (0.74, 0.56, 0.28, 1.0)
COL_LENS_GLASS = (0.86, 0.84, 0.72, 0.65); COL_BUNK = (0.62, 0.52, 0.40, 1.0)
COL_LINEN = (0.92, 0.90, 0.84, 1.0); COL_DESK = (0.42, 0.30, 0.22, 1.0)
COL_BAYOU_WATER = (0.20, 0.28, 0.22, 0.65); COL_CYPRESS = (0.32, 0.22, 0.16, 1.0)
COL_PAPER = (0.92, 0.86, 0.74, 1.0); COL_OIL_LAMP = (0.96, 0.62, 0.28, 1.0)

RADIUS = 2.40; CEIL = 6.00  # ground floor; lens stage rises above


def build_cylindrical_shell():
    make_floor("Floor", (0.0, 0.0, 0.0), size_x=RADIUS*2 + 0.4, size_y=RADIUS*2 + 0.4,
               palette={"vinyl": COL_FLOOR_PLANK, "seam": COL_FLOOR_SEAM})
    # Curved wall — approximate cylinder with 16 short wall segments
    SEGS = 16
    for si in range(SEGS):
        ang = si * (2*math.pi/SEGS)
        next_ang = (si+1) * (2*math.pi/SEGS)
        mx = math.cos((ang + next_ang)/2.0) * RADIUS
        my = math.sin((ang + next_ang)/2.0) * RADIUS
        # Box oriented tangentially
        chord = 2 * RADIUS * math.sin(math.pi/SEGS)
        thickness = 0.20
        # Approximate orientation via short boxes — pure axis-aligned blob (acceptable for vertex-color scene)
        make_box(f"WallSeg_{si}", (mx, my, CEIL/2.0),
                 (chord*1.05, thickness, CEIL), COL_BRICK_WHITE)
    # Ceiling
    make_ceiling("Ceil", (0.0, 0.0, CEIL), size_x=RADIUS*2 + 0.4, size_y=RADIUS*2 + 0.4)
    # Hatch in ceiling (cutout faked with darker square)
    make_box("Ceil_Hatch", (0.0, +0.80, CEIL-0.02), (0.80, 0.80, 0.04), (0.10, 0.08, 0.06, 1.0))


def build_spiral_stair():
    # 16-step iron spiral hugging the W wall, going clockwise upward
    STEPS = 16
    inner_r = 0.40
    outer_r = RADIUS - 0.30
    center_pole_h = CEIL
    # Center pole
    make_cyl("Stair_Pole", (0.0, 0.0, center_pole_h/2.0), 0.10, center_pole_h, COL_STAIR_IRON)
    for si in range(STEPS):
        ang = si * (2*math.pi/STEPS) + math.pi  # start at W side
        mx = math.cos(ang) * (inner_r + outer_r)/2.0
        my = math.sin(ang) * (inner_r + outer_r)/2.0
        sz = (si + 1) * (center_pole_h / STEPS) - 0.10
        # Tread
        make_box(f"Stair_Tread_{si}", (mx, my, sz), (0.50, 0.40, 0.04), COL_STAIR_IRON)
        # Banister post (every other)
        if si % 2 == 0:
            bx = math.cos(ang) * (outer_r - 0.06)
            by = math.sin(ang) * (outer_r - 0.06)
            make_cyl(f"Stair_Banister_{si}", (bx, by, sz + 0.40), 0.025, 0.80, COL_STAIR_IRON)


def build_keepers_quarters():
    # Single bunk against the S inner wall arc
    bx, by = 0.0, -RADIUS + 0.80
    make_box("Bunk_Frame", (bx, by, 0.30), (1.80, 0.80, 0.20), COL_BUNK)
    make_box("Bunk_Mattress", (bx, by, 0.46), (1.70, 0.74, 0.12), COL_LINEN)
    make_box("Bunk_Pillow", (bx-0.65, by, 0.56), (0.40, 0.60, 0.08), COL_PAPER)
    make_box("Bunk_Quilt", (bx+0.20, by, 0.54), (1.20, 0.74, 0.06), (0.62, 0.36, 0.24, 1.0))
    # Writing desk against the E wall
    dx, dy = +RADIUS - 0.80, -0.20
    make_box("Desk_Top", (dx, dy, 0.74), (0.80, 0.50, 0.04), COL_DESK)
    make_box("Desk_Drawer", (dx, dy, 0.52), (0.78, 0.46, 0.20), COL_DESK)
    for sgn in (-1, +1):
        make_box(f"Desk_Leg_{sgn:+d}", (dx + sgn*0.34, dy, 0.36), (0.06, 0.46, 0.72), COL_DESK)
    # Logbook + oil lamp on the desk
    make_box("Desk_Logbook", (dx-0.20, dy, 0.78), (0.24, 0.32, 0.04), COL_PAPER)
    make_box("Desk_Pencil", (dx-0.20, dy+0.18, 0.78), (0.16, 0.02, 0.01), (0.62, 0.42, 0.20, 1.0))
    # Oil lamp
    make_cyl("Lamp_Base", (dx+0.28, dy, 0.80), 0.06, 0.08, COL_BRASS)
    make_cyl("Lamp_Reservoir", (dx+0.28, dy, 0.92), 0.05, 0.10, COL_LENS_GLASS)
    make_cyl("Lamp_Chimney", (dx+0.28, dy, 1.08), 0.04, 0.18, COL_LENS_GLASS)
    make_cyl("Lamp_Flame", (dx+0.28, dy, 1.00), 0.018, 0.04, COL_OIL_LAMP)


def build_bayou_view_window():
    # Single arched window on the N side, cypress water + tree visible
    make_box("Window_N_Frame", (0.0, +RADIUS-0.04, 2.20), (1.40, 0.04, 1.40), COL_BRASS)
    make_box("Window_N_Glass", (0.0, +RADIUS-0.06, 2.20), (1.20, 0.005, 1.20),
             (0.78, 0.84, 0.86, 0.50))
    # Outside backdrop — bayou water + cypress at distance
    make_box("Bayou_Backdrop_Water", (0.0, +RADIUS + 6.0, 0.50), (12.0, 0.04, 1.00),
             COL_BAYOU_WATER)
    for ti, (tx, tz) in enumerate([(-3.0, 4.0), (-1.0, 3.6), (+2.0, 4.2), (+4.0, 3.8)]):
        make_cyl(f"Cypress_Distant_{ti}", (tx, +RADIUS + 6.0, tz/2.0 + 1.0),
                 0.20, tz, COL_CYPRESS, segments=8)
        make_cyl(f"Cypress_Distant_Foliage_{ti}", (tx, +RADIUS + 6.0, tz + 1.2),
                 0.80, 0.80, (0.32, 0.42, 0.30, 1.0), segments=8)
    # Sky panel above
    make_box("Sky_Panel", (0.0, +RADIUS + 8.0, 6.0), (12.0, 0.04, 5.0), (0.62, 0.66, 0.62, 1.0))


def build_lens_stage_above():
    # The Fresnel lens visible THROUGH the ceiling hatch. We won't
    # model the upper floor, but a brass-glass lens disk floating
    # above the hatch reads correctly when the camera glances up.
    lx, ly, lz = 0.0, +0.80, CEIL + 0.40
    # Brass plate around lens
    make_cyl("Lens_Plate", (lx, ly, lz), 0.50, 0.06, COL_BRASS, segments=20)
    # The glass lens itself — stacked rings
    for li in range(4):
        make_cyl(f"Lens_Ring_{li}", (lx, ly, lz + 0.04 + li*0.10),
                 0.42 - li*0.08, 0.08, COL_LENS_GLASS, segments=20)
    # Brass crown
    make_cyl("Lens_Crown", (lx, ly, lz + 0.50), 0.20, 0.06, COL_BRASS, segments=12)


def build_ceiling_infra():
    make_smoke_detector("Smoke", (0.0, 0.0, CEIL-0.05))
    make_sprinkler("Spr", (1.40, -1.40, CEIL-0.05))


def build_decor():
    # Wall clock on the E wall, brass calendar on the W wall
    make_wall_clock("Clock", (+RADIUS-0.05, +1.20, 2.40), frozen_hour=4, frozen_min=15)
    make_calendar("Calendar", (-RADIUS+0.05, +1.20, 2.30))
    # Coiled rope on the floor
    for ri in range(3):
        make_cyl(f"Rope_Coil_{ri}", (-RADIUS+1.20, -1.40, 0.10 + ri*0.05),
                 0.18 - ri*0.04, 0.04, (0.62, 0.46, 0.26, 1.0), segments=12)
    # A pair of oilskin coats hanging by the door (S)
    for ci, cx in enumerate([-0.30, +0.30]):
        make_box(f"Coat_{ci}", (cx, -RADIUS + 0.20, 1.40), (0.40, 0.06, 1.20),
                 (0.32, 0.28, 0.22, 1.0))


def main():
    clear_scene()
    build_cylindrical_shell()
    build_spiral_stair()
    build_keepers_quarters()
    build_bayou_view_window()
    build_lens_stage_above()
    build_ceiling_infra()
    build_decor()
    out = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                         "../../../assets/3d/locales/bayou_lighthouse.glb"))
    print(f"\n[build_bayou_lighthouse] exporting to {out}")
    export_glb(out)


if __name__ == "__main__":
    main()
