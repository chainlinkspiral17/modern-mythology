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


def build_hermit_dressing():
    """Scene-description specifics from setup_watch_kept.json:
      · "logbook lies open on the desk; last entry, 0214 LAMP STEADY
        NO TRAFFIC"
      · "radio has been dead-air since the cold front lifted at
        midnight"
      · A coffee mug + thermos · the third hour of the vigil
      · Wall calendar · the last Tuesday of the manned station
        circled in red
    """
    desk_cx = 0.0
    desk_cy = +1.10
    desk_top_z = 0.78

    # Logbook open on the desk
    log_x = desk_cx - 0.10
    log_y = desk_cy
    make_box("Logbook_Cover",
             (log_x - 0.18, log_y, desk_top_z + 0.014),
             (0.20, 0.30, 0.020),
             (0.20, 0.32, 0.22, 1.0))   # dark green ledger
    make_box("Logbook_LeftPage",
             (log_x - 0.06, log_y, desk_top_z + 0.024),
             (0.22, 0.28, 0.002),
             (0.94, 0.90, 0.78, 1.0))
    make_box("Logbook_RightPage",
             (log_x + 0.16, log_y, desk_top_z + 0.024),
             (0.22, 0.28, 0.002),
             (0.94, 0.90, 0.78, 1.0))
    # 8 horizontal rule lines on each page
    for li in range(8):
        for px in (log_x - 0.06, log_x + 0.16):
            make_box("Logbook_Line_%d_%.2f" % (li, px),
                     (px, log_y, desk_top_z + 0.026),
                     (0.20, 0.26 - li * 0.03, 0.0005),
                     (0.62, 0.58, 0.50, 1.0))
    # The 02:14 entry (a darker text-band on the right page bottom)
    make_box("Logbook_LastEntry",
             (log_x + 0.16, log_y - 0.10, desk_top_z + 0.027),
             (0.18, 0.018, 0.0005),
             (0.20, 0.16, 0.12, 1.0))
    # Fountain pen lying across
    make_cyl("Logbook_Pen",
             (log_x + 0.22, log_y - 0.06, desk_top_z + 0.030),
             0.006, 0.18,
             (0.18, 0.16, 0.14, 1.0),
             segments=6, axis='X')
    # Nib (brass)
    make_box("Logbook_PenNib",
             (log_x + 0.30, log_y - 0.06, desk_top_z + 0.030),
             (0.020, 0.008, 0.006),
             (0.78, 0.62, 0.30, 1.0))

    # Radio (dead-air)
    radio_x = desk_cx - 0.50
    radio_y = desk_cy + 0.10
    make_box("Radio_Body",
             (radio_x, radio_y, desk_top_z + 0.10),
             (0.36, 0.22, 0.20),
             (0.28, 0.22, 0.18, 1.0))
    make_box("Radio_Speaker",
             (radio_x - 0.08, radio_y - 0.111, desk_top_z + 0.10),
             (0.14, 0.005, 0.14),
             (0.10, 0.08, 0.06, 1.0))
    make_cyl("Radio_DialFace",
             (radio_x + 0.10, radio_y - 0.111, desk_top_z + 0.13),
             0.05, 0.005,
             (0.92, 0.86, 0.62, 1.0),
             segments=10, axis='Y')
    make_box("Radio_DialNeedle",
             (radio_x + 0.10, radio_y - 0.114, desk_top_z + 0.16),
             (0.003, 0.003, 0.04),
             (0.62, 0.20, 0.18, 1.0))
    make_box("Radio_FreqDisplay",
             (radio_x + 0.10, radio_y - 0.114, desk_top_z + 0.07),
             (0.08, 0.005, 0.018),
             (0.62, 0.46, 0.18, 1.0))
    for ki, kx_off in enumerate([-0.13, -0.01]):
        make_cyl("Radio_Knob_%d" % ki,
                 (radio_x + kx_off, radio_y - 0.114, desk_top_z + 0.02),
                 0.018, 0.012,
                 (0.42, 0.32, 0.20, 1.0),
                 segments=6, axis='Y')

    # Coffee mug + thermos
    mug_x = desk_cx + 0.45
    mug_y = desk_cy
    make_cyl("HermitMug_Body",
             (mug_x, mug_y, desk_top_z + 0.06),
             0.040, 0.11,
             (0.92, 0.88, 0.80, 1.0),
             segments=10, axis='Z')
    make_cyl("HermitMug_Stripe",
             (mug_x, mug_y, desk_top_z + 0.075),
             0.042, 0.020,
             (0.20, 0.34, 0.52, 1.0),
             segments=10, axis='Z')
    make_cyl("Thermos_Body",
             (mug_x + 0.14, mug_y, desk_top_z + 0.16),
             0.050, 0.30,
             (0.62, 0.62, 0.62, 1.0),
             segments=10, axis='Z')
    make_cyl("Thermos_Cap",
             (mug_x + 0.14, mug_y, desk_top_z + 0.34),
             0.045, 0.04,
             (0.62, 0.20, 0.16, 1.0),
             segments=10, axis='Z')

    # Wall calendar with the last Tuesday circled
    cal_x = desk_cx + 0.50
    cal_y = +2.40
    cal_cz = 1.70
    make_box("Calendar_Backing",
             (cal_x, cal_y - 0.005, cal_cz),
             (0.40, 0.005, 0.50),
             (0.94, 0.90, 0.80, 1.0))
    make_box("Calendar_Photo",
             (cal_x, cal_y - 0.006, cal_cz + 0.14),
             (0.34, 0.005, 0.18),
             (0.30, 0.36, 0.40, 1.0))
    # 5 × 7 date grid
    for ri in range(5):
        for ci in range(7):
            dx = cal_x - 0.16 + ci * 0.054
            dz = cal_cz - 0.04 - ri * 0.05
            make_box("Calendar_Cell_%d_%d" % (ri, ci),
                     (dx, cal_y - 0.007, dz),
                     (0.04, 0.0005, 0.04),
                     (0.18, 0.18, 0.18, 1.0))
    # Red circle on row 3 col 2 (the last Tuesday)
    cx = cal_x - 0.16 + 2 * 0.054
    cz = cal_cz - 0.04 - 3 * 0.05
    make_cyl("Calendar_TuesdayCircle_Outer",
             (cx, cal_y - 0.008, cz),
             0.030, 0.0005,
             (0.86, 0.18, 0.16, 1.0),
             segments=10, axis='Y')
    make_cyl("Calendar_TuesdayCircle_Inner",
             (cx, cal_y - 0.0083, cz),
             0.022, 0.0005,
             (0.94, 0.90, 0.80, 1.0),
             segments=10, axis='Y')


def build_hermit_wave2_props():
    """Named props from setup_the_relief_techs_arrival.json and
    setup_the_storm_visit.json.

    the_relief_techs_arrival (11:14 AM Friday · handover):
      · Marcus Yancey's Coast Guard-navy laptop bag with gold badge
      · Tasha Reid's silver firmware kit case with two latches
      · Estelle's father's brass octant in green-stripe kitchen
        towel on the bunk, with the calibration card peeking out

    the_storm_visit (11:48 PM · mid-August squall):
      · The Theriot skiff's bow lamp still glowing after landing
      · USCG Venice radio on the writing desk with red POWER LED
        + mic on coiled cord
      · Kerosene reserve heater in the bunk room (glow + flicker)
      · Cypriane's round 7-year-old-hand midnight log entry
    """
    desk_x = 0.0
    desk_y = -1.20
    desk_top_z = 0.78

    # ── the_relief_techs_arrival ────────────────────────────────
    lb_x = desk_x - 0.60
    lb_y = desk_y + 0.30
    make_box("MarcusLaptopBag_Body",
             (lb_x, lb_y, 0.32),
             (0.36, 0.14, 0.32),
             (0.14, 0.16, 0.20, 1.0))
    make_box("MarcusLaptopBag_Strap",
             (lb_x, lb_y, 0.52),
             (0.14, 0.03, 0.02),
             (0.14, 0.16, 0.20, 1.0))
    make_box("MarcusLaptopBag_Badge",
             (lb_x + 0.08, lb_y - 0.07, 0.44),
             (0.05, 0.001, 0.03),
             (0.86, 0.72, 0.20, 1.0))

    fk_x = lb_x + 0.30
    fk_y = lb_y
    make_box("TashaFirmwareKit_Body",
             (fk_x, fk_y, 0.24),
             (0.26, 0.16, 0.10),
             (0.86, 0.86, 0.88, 1.0))
    for cx in (-0.08, +0.08):
        make_box("TashaFirmwareKit_Latch_%d" % int(cx*100),
                 (fk_x + cx, fk_y - 0.09, 0.24),
                 (0.02, 0.005, 0.02),
                 (0.62, 0.62, 0.64, 1.0))

    bunk_x = -2.00
    bunk_y = +2.50
    bunk_top_z = 0.50
    make_box("Octant_Towel_Bundle",
             (bunk_x, bunk_y, bunk_top_z + 0.08),
             (0.30, 0.24, 0.10),
             (0.94, 0.90, 0.82, 1.0))
    for si in range(3):
        make_box("Octant_Towel_Stripe_%d" % si,
                 (bunk_x, bunk_y - 0.08 + si * 0.08, bunk_top_z + 0.13),
                 (0.28, 0.02, 0.001),
                 (0.32, 0.56, 0.36, 1.0))
    make_cyl("Octant_BrassCorner",
             (bunk_x + 0.08, bunk_y - 0.02, bunk_top_z + 0.12),
             0.05, 0.02,
             (0.78, 0.62, 0.30, 1.0), segments=10, axis='Z')
    make_box("Octant_CalibrationCard",
             (bunk_x + 0.12, bunk_y + 0.08, bunk_top_z + 0.11),
             (0.05, 0.03, 0.001),
             (0.92, 0.88, 0.72, 1.0))

    # ── the_storm_visit ────────────────────────────────────────
    # Bow lamp glow (persists across visits · a nod to the arrival)
    make_cyl("TheriotSkiff_BowLamp",
             (+2.00, -3.20, 0.60),
             0.04, 0.04,
             (0.94, 0.86, 0.42, 1.0), segments=10, axis='Y')
    make_cyl("TheriotSkiff_BowLampGlow",
             (+2.00, -3.15, 0.60),
             0.10, 0.005,
             (0.94, 0.86, 0.42, 0.35), segments=12, axis='Y')

    make_box("USCG_Radio_Body",
             (desk_x - 0.24, desk_y + 0.08, desk_top_z + 0.06),
             (0.20, 0.16, 0.12),
             (0.14, 0.14, 0.16, 1.0))
    make_box("USCG_Radio_Grille",
             (desk_x - 0.24, desk_y + 0.16, desk_top_z + 0.06),
             (0.18, 0.001, 0.10),
             (0.10, 0.10, 0.10, 1.0))
    make_cyl("USCG_Radio_LED",
             (desk_x - 0.30, desk_y + 0.16, desk_top_z + 0.14),
             0.006, 0.008,
             (0.94, 0.24, 0.20, 1.0), segments=6, axis='Y')
    make_box("USCG_Radio_Mic_Body",
             (desk_x - 0.30, desk_y - 0.04, desk_top_z + 0.20),
             (0.06, 0.04, 0.10),
             (0.14, 0.14, 0.16, 1.0))
    make_cyl("USCG_Radio_Mic_Cord",
             (desk_x - 0.30, desk_y + 0.02, desk_top_z + 0.20),
             0.008, 0.06,
             (0.32, 0.30, 0.32, 1.0), segments=6, axis='Y')

    heater_x = -1.00
    heater_y = +2.60
    make_box("KeroseneHeater_Body",
             (heater_x, heater_y, 0.36),
             (0.24, 0.28, 0.42),
             (0.42, 0.40, 0.38, 1.0))
    make_cyl("KeroseneHeater_Vent",
             (heater_x, heater_y - 0.15, 0.36),
             0.08, 0.02,
             (0.10, 0.08, 0.08, 1.0), segments=12, axis='Y')
    make_cyl("KeroseneHeater_Glow",
             (heater_x, heater_y - 0.16, 0.36),
             0.06, 0.005,
             (0.94, 0.42, 0.20, 1.0), segments=12, axis='Y')
    make_box("KeroseneHeater_Flame",
             (heater_x, heater_y - 0.14, 0.42),
             (0.02, 0.008, 0.04),
             (0.96, 0.72, 0.24, 0.85))

    # Cypriane's round 7-year-old midnight log entry
    lb_book_x = desk_x
    lb_book_y = desk_y - 0.02
    for li in range(3):
        make_box("Cypriane_LogEntry_Line_%d" % li,
                 (lb_book_x + 0.08, lb_book_y - 0.08 + li * 0.04, desk_top_z + 0.025),
                 (0.08, 0.02, 0.0005),
                 (0.24, 0.20, 0.60, 1.0))
    make_box("Cypriane_LogEntry_Signature",
             (lb_book_x + 0.06, lb_book_y - 0.18, desk_top_z + 0.026),
             (0.10, 0.03, 0.0005),
             (0.24, 0.20, 0.60, 1.0))


def main():
    clear_scene()
    build_cylindrical_shell()
    build_spiral_stair()
    build_keepers_quarters()
    build_bayou_view_window()
    build_lens_stage_above()
    build_ceiling_infra()
    build_decor()
    build_hermit_dressing()
    build_hermit_wave2_props()
    out = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                         "../../../assets/3d/locales/bayou_lighthouse.glb"))
    print(f"\n[build_bayou_lighthouse] exporting to {out}")
    export_glb(out)


if __name__ == "__main__":
    main()
