"""school_field_evening — vol6 EXTERIOR: the school football field at
dusk. Friday-night-lights energy at TRUE SCALE.

2026-08-09 REBUILD (user: "football field scale is off, football field
lines and measurements and goal placements are all wrong"): the field
was a 20 x 14m toy with 6 yard lines and goalposts standing INSIDE the
playing surface. Now a real high-school gridiron:

  · 120yd x 53 1/3yd (109.7 x 48.8m): 100yd of field + two 10yd
    end zones. y=0 is the SOUTH END LINE; goal lines at y 9.14 and
    100.58; north end line at 109.73.
  · yard lines every 5yd goal-line-to-goal-line (21 lines), hash
    ticks every yard at the HS inbound lines (x +-8.13), abstract
    yard numbers every 10yd, mow stripes every 5yd.
  · goalposts ON THE END LINES: crossbar at 3.05m, HS width 7.11m,
    uprights to 9.1m.
  · pylons at all eight end-zone corners; six 18m light poles;
    36m home stands; scoreboard beyond the north end zone.

Coords: x = sideline-to-sideline (0 = midfield), y = downfield,
z = up. The Background3D camera sits just behind the south end line
looking downfield — the whole field runs away from it."""
import os, sys, math
_BT = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
if _BT not in sys.path: sys.path.insert(0, _BT)
from _props import palette as P
from _props.geometry import clear_scene, make_box, make_cyl, export_glb

YD = 0.9144
FIELD_W   = 53.333 * YD          # 48.77 sideline to sideline
FIELD_LEN = 120.0 * YD           # 109.73 end line to end line
EZ        = 10.0 * YD            # end-zone depth 9.14
GL_S      = EZ                   # south goal line y
GL_N      = FIELD_LEN - EZ       # north goal line y
MID_Y     = FIELD_LEN / 2.0      # the 50: 54.86
SIDE_X    = FIELD_W / 2.0        # 24.38
HASH_X    = 53.333 * YD / 6.0    # HS inbound lines at 1/3 width: 8.13

COL_TURF  = (0.18, 0.32, 0.16, 1.0)
COL_TURF2 = (0.22, 0.38, 0.20, 1.0)
COL_EZ    = (0.15, 0.26, 0.20, 1.0)   # end-zone turf, cooler + darker
COL_LINE  = (0.86, 0.88, 0.82, 1.0)
COL_METAL = (0.60, 0.62, 0.66, 1.0)
COL_POLE  = (0.28, 0.28, 0.30, 1.0)
COL_GOAL  = (0.94, 0.82, 0.28, 1.0)
COL_LAMP  = (1.0, 0.98, 0.90, 1.0)


def build_ground():
    # End zones (their own turf color)
    make_box("Turf_EZ_S", (0.0, GL_S / 2.0, -0.02), (FIELD_W, EZ, 0.04), COL_EZ)
    make_box("Turf_EZ_N", (0.0, GL_N + EZ / 2.0, -0.02), (FIELD_W, EZ, 0.04), COL_EZ)
    # Mow stripes every 5yd between the goal lines (20 bands)
    band = 5.0 * YD
    for i in range(20):
        c = COL_TURF if i % 2 == 0 else COL_TURF2
        make_box(f"Turf_{i}", (0.0, GL_S + i * band + band / 2.0, -0.02),
                 (FIELD_W, band, 0.04), c)
    # Surround apron (grass beyond the lines, out to the fences)
    make_box("Apron_Grass", (0.0, MID_Y, -0.03), (FIELD_W + 22.0, FIELD_LEN + 24.0, 0.04),
             (0.16, 0.26, 0.14, 1.0))
    # Yard lines every 5yd, goal line to goal line (21 incl. both GLs)
    for k in range(21):
        ly = GL_S + k * band
        w = 0.14 if k in (0, 20) else 0.10   # goal lines read heavier
        make_box(f"YardLine_{k}", (0.0, ly, 0.001), (FIELD_W, w, 0.02), COL_LINE)
    # End lines
    for tag, ey in (("S", 0.0), ("N", FIELD_LEN)):
        make_box(f"EndLine_{tag}", (0.0, ey, 0.001), (FIELD_W, 0.14, 0.02), COL_LINE)
    # Sidelines, full length
    for sx in (-SIDE_X, +SIDE_X):
        make_box(f"Sideline_{'L' if sx < 0 else 'R'}", (sx, MID_Y, 0.001),
                 (0.14, FIELD_LEN, 0.02), COL_LINE)
    # Abstract yard numbers every 10yd (both sides): a digit-pair slab
    # ~2yd tall with its top toward the near sideline, 9yd inboard.
    for k in range(1, 10):
        ny = GL_S + k * 10.0 * YD
        for sx in (-1, +1):
            make_box(f"Num_{k}0_{'L' if sx < 0 else 'R'}",
                     (sx * (SIDE_X - 9.0 * YD), ny, 0.0015),
                     (1.2, 1.8, 0.02), COL_LINE)


def build_hashmarks():
    # Hash ticks every yard at the HS inbound lines (skip the 5yd
    # multiples — the full yard lines carry those).
    for hx in (-HASH_X, +HASH_X):
        tag = 'L' if hx < 0 else 'R'
        for yard in range(1, 100):
            if yard % 5 == 0:
                continue
            make_box(f"Hash_{tag}_{yard}", (hx, GL_S + yard * YD, 0.0015),
                     (0.60, 0.08, 0.02), COL_LINE)
    # Pylons at all eight end-zone corners
    for px in (-SIDE_X, +SIDE_X):
        for py in (0.0, GL_S, GL_N, FIELD_LEN):
            make_box(f"Pylon_{px:+.0f}_{py:.0f}", (px, py, 0.22),
                     (0.10, 0.10, 0.45), (0.94, 0.44, 0.16, 1.0))
    # A football teed up at the 50
    make_cyl("Tee", (0.0, MID_Y, 0.03), 0.06, 0.06, (0.92, 0.72, 0.20, 1.0), segments=10)
    make_cyl("Ball", (0.0, MID_Y, 0.14), 0.055, 0.28, (0.42, 0.24, 0.14, 1.0), axis='X', segments=8)


def build_goalposts():
    # ON the end lines. HS: crossbar 10ft (3.05) high, 23'4" (7.11)
    # wide; uprights another 6m above the crossbar.
    for tag, gy in (("S", 0.0), ("N", FIELD_LEN)):
        make_cyl(f"Goal_{tag}_Post", (0.0, gy, 1.52), 0.10, 3.05, COL_GOAL, segments=8)
        make_box(f"Goal_{tag}_Cross", (0.0, gy, 3.05), (7.11, 0.10, 0.10), COL_GOAL)
        for ux in (-3.56, 3.56):
            make_cyl(f"Goal_{tag}_Up_{'L' if ux < 0 else 'R'}",
                     (ux, gy, 3.05 + 3.0), 0.06, 6.0, COL_GOAL, segments=8)


def build_bleachers():
    # Home stands, west sideline, 36m long centered on the 50,
    # 2.6m back from the sideline.
    bx = -(SIDE_X + 2.6)
    for step in range(9):
        h = 0.4 + step * 0.42
        make_box(f"Bleach_Riser_{step}", (bx - step * 0.55, MID_Y, h * 0.5),
                 (0.55, 36.0, h), COL_METAL)
        make_box(f"Bleach_Bench_{step}", (bx - step * 0.55, MID_Y, h + 0.05),
                 (0.50, 36.0, 0.06), (0.44, 0.36, 0.26, 1.0))
    for ly in (MID_Y - 16.0, MID_Y + 16.0):
        make_box(f"Bleach_Leg_{ly:.0f}", (bx - 2.4, ly, 1.7), (5.0, 0.10, 0.10), COL_METAL)
    for ry in (MID_Y - 18.0, MID_Y + 18.0):
        make_box(f"Bleach_Rail_{ry:.0f}", (bx - 1.6, ry, 1.5), (3.4, 0.06, 0.06), COL_METAL)
    # Center aisle handrail
    make_box("Bleach_Aisle_Rail", (bx - 2.2, MID_Y, 1.4), (4.6, 0.06, 0.06), COL_METAL)


def build_spectators():
    # Friday-night crowd scattered up the stands.
    bx = -(SIDE_X + 2.6)
    coats = [(0.42,0.30,0.34,1.0),(0.30,0.36,0.44,1.0),(0.46,0.42,0.30,1.0),
             (0.36,0.44,0.38,1.0),(0.52,0.40,0.36,1.0),(0.34,0.34,0.40,1.0)]
    skin = (0.62, 0.48, 0.40, 1.0)
    seats = [(2,-14.0),(2,-6.5),(2,3.0),(3,8.5),(3,-2.0),(4,-10.0),(4,5.5),(4,13.0),
             (5,0.5),(5,-6.0),(6,-12.5),(6,3.5),(6,9.0),(7,-3.5),(7,15.0),(8,6.0)]
    for si, (step, yo) in enumerate(seats):
        h = 0.4 + step * 0.42
        seat_top = h + 0.08
        px = bx - step * 0.55
        py = MID_Y + yo
        col = coats[si % len(coats)]
        make_box(f"Fan_{si}_Torso", (px, py, seat_top + 0.24), (0.34, 0.34, 0.46), col)
        make_cyl(f"Fan_{si}_Head", (px, py, seat_top + 0.58), 0.10, 0.16, skin, segments=8)


def build_benches():
    # Team benches: home east, visiting west (canon: "Visiting bench.
    # Move it."), 12m long, flanking the 50, 2m off the sidelines.
    for bi, (home, by) in enumerate(((True, MID_Y - 8.0), (False, MID_Y + 8.0))):
        ex = +(SIDE_X + 2.0) if home else -(SIDE_X + 2.0)
        back_dx = 0.24 if home else -0.24
        col = (0.30, 0.36, 0.52, 1.0) if home else (0.52, 0.30, 0.30, 1.0)
        make_box(f"Bench_{bi}_Seat", (ex, by, 0.46), (0.50, 12.0, 0.08), (0.42, 0.34, 0.26, 1.0))
        make_box(f"Bench_{bi}_Back", (ex + back_dx, by, 0.70), (0.06, 12.0, 0.40), col)
        for lo in (-5.4, 5.4):
            make_box(f"Bench_{bi}_Leg_{'S' if lo < 0 else 'N'}", (ex, by + lo, 0.22),
                     (0.46, 0.08, 0.44), COL_METAL)
    # Water coolers + helmet rack behind the HOME (east) bench
    hx = SIDE_X + 2.0
    for wi, wy in enumerate((MID_Y - 15.0, MID_Y + 2.0)):
        make_cyl(f"Cooler_{wi}_Body", (hx + 1.0, wy, 0.34), 0.24, 0.60, (0.92, 0.48, 0.18, 1.0), segments=12)
        make_cyl(f"Cooler_{wi}_Lid", (hx + 1.0, wy, 0.66), 0.25, 0.06, (0.92, 0.90, 0.86, 1.0), segments=12)
        make_box(f"Cooler_{wi}_Spigot", (hx + 0.74, wy, 0.24), (0.06, 0.05, 0.05), P.METAL_BLACK)
    rx = hx + 1.6
    make_box("Rack_Bar_T", (rx, MID_Y - 5.0, 1.10), (0.06, 3.0, 0.06), COL_METAL)
    make_box("Rack_Bar_B", (rx, MID_Y - 5.0, 0.60), (0.06, 3.0, 0.06), COL_METAL)
    for hi in range(5):
        hy = MID_Y - 6.2 + hi * 0.6
        make_cyl(f"Rack_Helmet_{hi}", (rx, hy, 0.84), 0.11, 0.14, (0.30, 0.36, 0.52, 1.0), axis='Y', segments=10)


def build_scoreboard():
    # Beyond the north end zone, big enough to read from the south side.
    sx, sy = 0.0, FIELD_LEN + 9.0
    for po in (-3.6, 3.6):
        make_cyl(f"Score_Post_{'L' if po < 0 else 'R'}", (sx + po, sy, 3.0), 0.16, 6.0, COL_POLE, segments=8)
    make_box("Score_Panel", (sx, sy, 7.6), (9.0, 0.40, 3.6), (0.10, 0.12, 0.16, 1.0))
    make_box("Score_Header", (sx, sy - 0.22, 9.15), (9.4, 0.12, 0.9), (0.30, 0.36, 0.52, 1.0))
    amber = (0.98, 0.66, 0.18, 1.0)
    for li, lx in enumerate((-2.8, +2.8)):   # HOME / GUEST
        make_box(f"Score_LabelBG_{li}", (sx + lx, sy - 0.22, 8.5), (2.2, 0.08, 0.5), (0.62, 0.66, 0.72, 1.0))
        for di in range(2):
            make_box(f"Score_Digit_{li}_{di}", (sx + lx - 0.6 + di * 1.2, sy - 0.24, 7.4),
                     (0.8, 0.06, 1.2), amber)
    for di in range(4):
        make_box(f"Score_Clock_{di}", (sx - 1.35 + di * 0.9, sy - 0.24, 6.1), (0.5, 0.06, 0.8), amber)
    make_box("Score_QtrBox", (sx, sy - 0.24, 5.2), (0.7, 0.06, 0.7), (0.94, 0.30, 0.22, 1.0))


def build_first_down_chain():
    # Chain crew, east sideline, working the south 40s: the two rods
    # a true 10yd apart, the down box at the trailing rod.
    cx = +(SIDE_X + 1.0)
    y0 = GL_S + 31.0 * YD
    y1 = y0 + 10.0 * YD
    for pi, py in enumerate((y0, y1)):
        make_cyl(f"Chain_Pole_{pi}", (cx, py, 0.9), 0.03, 1.8, COL_METAL, segments=6)
        make_box(f"Chain_Cap_{pi}", (cx, py, 1.9), (0.14, 0.14, 0.20), (0.94, 0.62, 0.16, 1.0))
    links = 24
    for li in range(links):
        ly = y0 + (li + 0.5) * (y1 - y0) / links
        make_box(f"Chain_Link_{li}", (cx, ly, 0.16), (0.03, (y1 - y0) / links * 0.6, 0.03), P.METAL_STEEL)
    make_cyl("Down_Pole", (cx, y0 - 1.8, 1.0), 0.03, 2.0, COL_METAL, segments=6)
    make_box("Down_Box", (cx, y0 - 1.8, 2.1), (0.40, 0.10, 0.40), (0.94, 0.82, 0.28, 1.0))
    make_box("Down_Num", (cx - 0.06, y0 - 1.8, 2.1), (0.005, 0.20, 0.24), P.METAL_BLACK)


def build_floodlights():
    # Six poles, three per side, 18m — Friday night lights that read
    # from anywhere on the field.
    # x +-33.9: the west row must clear the BACK of the stands
    # (the mid pole used to stand inside the risers).
    for pi, (px, py) in enumerate(((-(SIDE_X + 9.5), GL_S + 15.0 * YD),
                                   (-(SIDE_X + 9.5), MID_Y),
                                   (-(SIDE_X + 9.5), GL_N - 15.0 * YD),
                                   (+(SIDE_X + 9.5), GL_S + 15.0 * YD),
                                   (+(SIDE_X + 9.5), MID_Y),
                                   (+(SIDE_X + 9.5), GL_N - 15.0 * YD))):
        make_cyl(f"Pole_{pi}", (px, py, 9.0), 0.16, 18.0, COL_POLE, segments=8)
        toward = 1.0 if px < 0 else -1.0
        # Bank faces the FIELD: wide along y, hung on the field side
        # of its pole.
        make_box(f"Bank_{pi}", (px + toward * 0.55, py, 17.2), (0.40, 2.6, 1.5), P.METAL_BLACK)
        for li in range(12):
            ly = -1.0 + (li % 4) * 0.66
            lz = -0.5 + (li // 4) * 0.5
            make_cyl(f"Lamp_{pi}_{li}", (px + toward * 0.80, py + ly, 17.2 + lz),
                     0.14, 0.10, COL_LAMP, axis='X', segments=8)


def build_fence():
    # Perimeter chain-link behind the north end zone (banner fence)
    n = 26
    fw = FIELD_W + 12.0
    fy = FIELD_LEN + 2.6
    for i in range(n):
        fx = -fw / 2.0 + i * (fw / (n - 1))
        make_cyl(f"FencePost_{i}", (fx, fy, 0.6), 0.03, 1.2, COL_METAL, segments=6)
    make_box("FenceRail_Top", (0.0, fy, 1.15), (fw, 0.03, 0.04), COL_METAL)
    make_box("FenceRail_Mid", (0.0, fy, 0.60), (fw, 0.03, 0.04), COL_METAL)


def build_banners():
    # Booster banners zip-tied to the north fence.
    cols = [(0.52, 0.20, 0.22, 1.0), (0.20, 0.34, 0.52, 1.0), (0.24, 0.42, 0.30, 1.0),
            (0.58, 0.46, 0.20, 1.0), (0.44, 0.30, 0.46, 1.0), (0.30, 0.44, 0.46, 1.0)]
    for bi in range(6):
        bxc = -22.0 + bi * 8.8
        make_box(f"Banner_{bi}", (bxc, FIELD_LEN + 2.55, 0.85), (5.6, 0.04, 0.70), cols[bi % len(cols)])
        make_box(f"Banner_{bi}_Text", (bxc, FIELD_LEN + 2.52, 0.85), (4.2, 0.02, 0.24), (0.92, 0.90, 0.84, 1.0))


def build_hero_props():
    """Narrative anchors (canon positions rescaled): THE FIELD GATE at
    the south/parking end, the corkboard on the field house (depth-
    chart climax), the parking lot + staged vehicles, Eileen's folding
    chair alone in the third row, the equipment shed + Coach Dale's
    truck beyond the northwest corner, cart + drill cones, spigots."""
    steel = (0.48, 0.50, 0.52, 1.0)
    wood = (0.42, 0.30, 0.18, 1.0)
    # South fence run + swing gate (between field and parking)
    for i, fx in enumerate((2.0, 5.2, 8.4, 12.6, 15.8, 19.0, 22.2, 25.4)):
        # the 8.4->12.6 bay is the swing gate's opening
        make_cyl(f"SFence_Post_{i}", (fx, -3.0, 0.9), 0.05, 1.8, steel, segments=6)
    make_cyl("SFence_Rail", (13.2, -3.0, 1.78), 0.035, 24.0, steel, segments=6, axis='X')
    make_box("Field_Gate", (10.5, -3.0, 0.90), (2.8, 0.06, 1.7), steel)
    make_box("Field_Gate_Mesh", (10.5, -3.02, 0.90), (2.6, 0.02, 1.5), (0.55, 0.57, 0.58, 0.35))
    # Field house + THE CORKBOARD outside its door
    make_box("Field_House", (-14.0, -8.5, 1.45), (7.0, 3.4, 2.9), (0.55, 0.50, 0.44, 1.0))
    make_box("Field_House_Roof", (-14.0, -8.5, 3.02), (7.5, 3.9, 0.24), (0.32, 0.28, 0.24, 1.0))
    make_box("Field_House_Door", (-16.0, -6.74, 1.05), (0.90, 0.06, 2.10), (0.30, 0.32, 0.36, 1.0))
    make_box("Corkboard", (-13.2, -6.72, 1.55), (1.40, 0.05, 1.00), (0.52, 0.38, 0.26, 1.0))
    make_box("Corkboard_Frame", (-13.2, -6.74, 1.55), (1.50, 0.04, 1.10), wood)
    make_box("DepthChart_Sheet", (-13.2, -6.69, 1.60), (0.30, 0.01, 0.42), (0.92, 0.90, 0.82, 1.0))
    # Parking lot + the staged vehicles
    make_box("Parking_Lot", (0.0, -12.0, 0.01), (56.0, 16.0, 0.04), (0.24, 0.24, 0.26, 1.0))
    for si in range(10):
        make_box(f"Lot_Stripe_{si}", (-18.0 + si * 4.0, -6.4, 0.035), (0.10, 2.2, 0.01), (0.72, 0.70, 0.60, 1.0))
    make_box("F250_Body", (13.5, -6.8, 0.85), (2.0, 4.6, 0.85), (0.62, 0.20, 0.18, 1.0))
    make_box("F250_Cab", (13.5, -5.8, 1.45), (1.85, 1.7, 0.60), (0.62, 0.20, 0.18, 1.0))
    make_box("F250_Glass", (13.5, -5.8, 1.48), (1.65, 1.5, 0.45), (0.14, 0.16, 0.20, 1.0))
    make_box("Civic_Body", (-22.0, -11.5, 0.62), (1.75, 4.0, 0.60), (0.55, 0.58, 0.62, 1.0))
    make_box("Civic_Cabin", (-22.0, -11.3, 1.08), (1.6, 2.0, 0.48), (0.50, 0.53, 0.57, 1.0))
    make_box("Tacoma_Body", (-10.0, -13.0, 0.78), (1.9, 4.4, 0.75), (0.24, 0.30, 0.26, 1.0))
    make_box("Tacoma_Cab", (-10.0, -12.0, 1.35), (1.75, 1.6, 0.55), (0.24, 0.30, 0.26, 1.0))
    # Eileen's folding chair — third row, south of the crowd
    bx = -(SIDE_X + 2.6)
    make_box("Eileen_Chair_Seat", (bx - 2 * 0.55, MID_Y - 17.0, 1.35), (0.42, 0.42, 0.03), (0.36, 0.42, 0.55, 1.0))
    make_box("Eileen_Chair_Back", (bx - 2 * 0.55 - 0.2, MID_Y - 17.0, 1.65), (0.03, 0.42, 0.36), (0.32, 0.38, 0.50, 1.0))
    # Equipment shed + Coach Dale's truck, beyond the NW corner
    make_box("Equip_Shed", (-30.0, FIELD_LEN + 6.0, 1.3), (4.0, 3.0, 2.6), (0.48, 0.42, 0.34, 1.0))
    make_box("Equip_Shed_Roof", (-30.0, FIELD_LEN + 6.0, 2.75), (4.4, 3.4, 0.3), (0.34, 0.30, 0.26, 1.0))
    make_box("Equip_Shed_Door", (-30.0, FIELD_LEN + 4.46, 1.05), (1.3, 0.06, 2.1), (0.30, 0.26, 0.22, 1.0))
    make_box("Dale_Truck_Body", (-30.0, FIELD_LEN + 10.6, 0.80), (1.9, 4.2, 0.78), (0.44, 0.40, 0.34, 1.0))
    make_box("Dale_Truck_Cab", (-30.0, FIELD_LEN + 9.6, 1.38), (1.75, 1.6, 0.55), (0.44, 0.40, 0.34, 1.0))
    # Equipment cart + the morning's drill cones (south 20s)
    make_box("Equip_Cart", (SIDE_X + 3.4, GL_S + 8.0, 0.45), (0.9, 1.4, 0.70), steel)
    for wi, (wx, wy) in enumerate(((SIDE_X + 3.0, GL_S + 7.4), (SIDE_X + 3.8, GL_S + 7.4),
                                   (SIDE_X + 3.0, GL_S + 8.6), (SIDE_X + 3.8, GL_S + 8.6))):
        make_cyl(f"Equip_Cart_Wheel_{wi}", (wx, wy, 0.10), 0.10, 0.06, (0.10, 0.10, 0.11, 1.0), segments=8, axis='X')
    for ci, (cx, cy) in enumerate(((-4.0, GL_S + 10.0), (-1.5, GL_S + 12.5), (1.0, GL_S + 10.8),
                                   (3.5, GL_S + 14.0), (-2.5, GL_S + 16.5), (0.5, GL_S + 15.5),
                                   (3.0, GL_S + 18.0), (5.0, GL_S + 12.0))):
        make_cyl(f"Cone_{ci}", (cx, cy, 0.12), 0.10, 0.24, (0.92, 0.46, 0.14, 1.0), segments=8)
        make_box(f"Cone_{ci}_Base", (cx, cy, 0.015), (0.22, 0.22, 0.03), (0.86, 0.40, 0.12, 1.0))
    # Spigots off the east sideline near the south end
    for pi, py in enumerate((GL_S + 2.0, GL_S + 2.6)):
        make_cyl(f"Spigot_{pi}_Pipe", (SIDE_X + 3.0, py, 0.45), 0.025, 0.90, steel, segments=6)
        make_box(f"Spigot_{pi}_Tap", (SIDE_X + 2.92, py, 0.88), (0.10, 0.04, 0.04), (0.66, 0.52, 0.24, 1.0))


def build_horizon_2026_08():
    """STUMP HUNT: evening treelines past the fences, centered on the
    FIELD (cy=55) so the first band clears the 110m gridiron + the
    scoreboard instead of standing on the 50-yard line."""
    from _props.detail import make_far_bands
    make_far_bands("FarTrees", (0.13, 0.20, 0.11),
                   [(95.0, 110.0, 8.0, 0.90), (180.0, 170.0, 11.0, 0.70),
                    (330.0, 260.0, 14.0, 0.52), (540.0, 400.0, 17.0, 0.40)],
                   cy=55.0, profile="treeline")


def main():
    clear_scene()
    build_ground()
    build_hashmarks()
    build_goalposts()
    build_bleachers()
    build_spectators()
    build_benches()
    build_scoreboard()
    build_first_down_chain()
    build_floodlights()
    build_fence()
    build_banners()
    build_hero_props()
    out = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)),
        "../../../assets/3d/locales/school_field_evening.glb"))
    print(f"\n[build_school_field_evening] exporting to {out}")
    build_horizon_2026_08()
    export_glb(out)


if __name__ == "__main__":
    main()
