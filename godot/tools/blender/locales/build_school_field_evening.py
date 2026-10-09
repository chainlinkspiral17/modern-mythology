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
looking downfield — the whole field runs away from it.

DRAFT 4 (2026-09-18, lore/_VISUAL_PROGRAM.md §3): tapered light poles
on base plates with conduit and a transformer box, hooded lamps,
lathed fence posts and a chain-link mesh, the four staged vehicles from
the vehicle kit, Eileen's chair a folding chair; an exterior's WEAR
(the worn band between the hashes, the goal mouths, dirt under both
benches, the sideline path from the gate, the gate's tread); D3 (the
field house's light over its door — the corkboard is read under it —
the scoreboard's cable and box, the goalposts' pads). The .tscn gains
the field-house lamp.

DRAFT 5 (2026-10-09) — the prose's geography. vol6 ch22 puts Eileen
"Third row, behind the home bench"; drafts 1-4 had the only stands on
the WEST sideline and the home bench (Coach K's stopwatch, the helmet
rack) EAST, so her chair sat across the field in the visitors' seats.
The home stands are now east, behind the home bench: open aluminium
rows (seat plank, footboard, posts every 3 m, tie beams, the back
guard rail, the aisle rail — the bleachers' underside was a draft-5
target), the PRESS BOX on top with its stair; a visitors' stand west;
the floodlight poles behind both. Coach K's truck is what ch13 says —
"the white Ford F-250 with the camper shell and the ladder rack and the
tape job on the driver's-side mirror" — not a bare red pickup, and
`insert truck` frames it (it framed Coach Dale's truck by the shed).

DRAFT 6 targets: the synthetic track ("the back stretch of the
synthetic track", ch19) — a real one rings the field, so the lot, the
gate and the field house move south and the stands outward; figures
with a pose; the scoreboard's digits as digits; the lot's lamp
practicals at dusk; Deck framing.
"""
import os, sys, math
_BT = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
if _BT not in sys.path: sys.path.insert(0, _BT)
from _props import palette as P
from _props.geometry import (clear_scene, make_box, make_cyl, make_lathe, make_tube,
                             make_rot_box, make_chamfer_box, make_taper_cyl, export_glb)

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
    # Ball rests on the tee (tee top 0.06; ball r 0.055 → centre 0.115)
    make_cyl("Ball", (0.0, MID_Y, 0.115), 0.055, 0.28, (0.42, 0.24, 0.14, 1.0), axis='X', segments=8)


def build_goalposts():
    # ON the end lines. HS: crossbar 10ft (3.05) high, 23'4" (7.11)
    # wide; uprights another 6m above the crossbar.
    for tag, gy in (("S", 0.0), ("N", FIELD_LEN)):
        make_cyl(f"Goal_{tag}_Post", (0.0, gy, 1.52), 0.10, 3.05, COL_GOAL, segments=8)
        make_box(f"Goal_{tag}_Cross", (0.0, gy, 3.05), (7.11, 0.10, 0.10), COL_GOAL)
        for ux in (-3.56, 3.56):
            make_cyl(f"Goal_{tag}_Up_{'L' if ux < 0 else 'R'}",
                     (ux, gy, 3.05 + 3.0), 0.06, 6.0, COL_GOAL, segments=8)


HOME_SIDE = +1                 # the home bench, its stands and the press box are EAST


def _stands(tag, sign, rows, half_len, cy, d0=6.0, press_box=False):
    """Open aluminium stands (draft 5, 2026-10-09): a seat plank and a
    footboard per row on posts every 3 m, tie beams, the back guard
    rail, the aisle handrail — not the solid stepped block of drafts
    1-4 (the bleachers' underside was a draft-5 target). `sign` +1
    builds east of the east sideline, -1 west of the west one; d is
    the depth from the stands' front edge, SIDE_X + d0 off centre."""
    def X(d): return sign * (SIDE_X + d0 + d)
    alum, plank = (0.66, 0.68, 0.70, 1.0), (0.74, 0.76, 0.78, 1.0)
    y0, y1 = cy - half_len, cy + half_len
    seat_top = lambda s: 0.45 + s * 0.42
    for s in range(rows):
        S = seat_top(s)
        make_box(f"{tag}_Seat_{s}", (X(s * 0.8 + 0.63), cy, S - 0.025), (0.30, 2 * half_len, 0.05), plank)
        if s:
            make_box(f"{tag}_Foot_{s}", (X(s * 0.8 + 0.225), cy, S - 0.42 - 0.025), (0.45, 2 * half_len, 0.05), alum)
    n = int(round(2 * half_len / 3.0))
    for k in range(n + 1):
        py = y0 + 0.15 + k * (2 * half_len - 0.3) / n
        for s in range(rows):
            S = seat_top(s)
            make_box(f"{tag}_Post_{k}_{s}", (X(s * 0.8 + 0.63), py, (S - 0.05) / 2.0), (0.06, 0.06, S - 0.05), alum)
            if s:
                F = S - 0.42
                make_box(f"{tag}_FootPost_{k}_{s}", (X(s * 0.8 + 0.225), py, (F - 0.05) / 2.0), (0.06, 0.06, F - 0.05), alum)
        dd = (rows - 1) * 0.8 + 0.63
        make_box(f"{tag}_Tie_{k}", (X(dd / 2.0 + 0.1), py, 0.30), (dd + 0.06, 0.05, 0.08), alum)
    # the back guard rail behind the top row
    top, back = seat_top(rows - 1), rows * 0.8 - 0.05
    for k in range(n + 1):
        py = y0 + 0.15 + k * (2 * half_len - 0.3) / n
        make_box(f"{tag}_BackPost_{k}", (X(back), py, (top + 1.05) / 2.0), (0.05, 0.05, top + 1.05), alum)
    make_box(f"{tag}_BackRail", (X(back), cy, top + 1.05), (0.06, 2 * half_len, 0.05), alum)
    make_box(f"{tag}_BackRail_Mid", (X(back), cy, top + 0.55), (0.04, 2 * half_len, 0.04), alum)
    # the aisle handrail up the middle, on posts that stand on the footboards
    for s in range(1, rows):
        F = seat_top(s) - 0.42
        make_box(f"{tag}_Aisle_Post_{s}", (X(s * 0.8 + 0.10), cy, F + 0.45), (0.04, 0.04, 0.90), alum)
    make_tube(f"{tag}_Aisle_Rail", [(X(0.8 + 0.10), cy, seat_top(1) - 0.42 + 0.92), (X((rows - 1) * 0.8 + 0.10), cy, seat_top(rows - 1) - 0.42 + 0.92)],
              0.022, alum, segments=6)
    # the concrete walk in front of the stands
    make_box(f"{tag}_Walk", (X(-1.0), cy, 0.02), (2.0, 2 * half_len + 2.0, 0.04), (0.56, 0.55, 0.52, 1.0))
    if press_box:
        pd0, pd1, pz = rows * 0.8 + 0.05, rows * 0.8 + 2.85, top
        pw = 10.0
        make_box(f"{tag}_PressBox", (X((pd0 + pd1) / 2.0), cy, pz + 1.25), (pd1 - pd0, pw, 2.5), (0.82, 0.80, 0.74, 1.0))
        make_box(f"{tag}_PressBox_Roof", (X((pd0 + pd1) / 2.0 - 0.15), cy, pz + 2.56), (pd1 - pd0 + 0.6, pw + 0.4, 0.12), (0.30, 0.36, 0.52, 1.0))
        make_box(f"{tag}_PressBox_Glass", (X(pd0 - 0.005), cy, pz + 1.40), (0.01, pw - 0.6, 0.80), (0.30, 0.36, 0.40, 1.0))
        for k in range(5):
            make_box(f"{tag}_PressBox_Mullion_{k}", (X(pd0 - 0.012), cy - pw / 2.0 + 0.3 + k * (pw - 0.6) / 4.0, pz + 1.40), (0.012, 0.06, 0.80), (0.30, 0.36, 0.52, 1.0))
        make_box(f"{tag}_PressBox_Sign", (X(pd0 - 0.01), cy, pz + 2.20), (0.01, 4.2, 0.40), (0.55, 0.14, 0.14, 1.0))
        make_box(f"{tag}_PressBox_Sign_Text", (X(pd0 - 0.016), cy, pz + 2.20), (0.004, 3.4, 0.18), (0.92, 0.90, 0.84, 1.0))
        for i, (dd, yy) in enumerate(((pd0 + 0.15, -1), (pd1 - 0.15, -1), (pd0 + 0.15, 1), (pd1 - 0.15, 1))):
            make_box(f"{tag}_PressBox_Leg_{i}", (X(dd), cy + yy * (pw / 2.0 - 0.15), pz / 2.0), (0.14, 0.14, pz), (0.40, 0.42, 0.44, 1.0))
        # the stair up its back to its door
        for st in range(12):
            make_box(f"{tag}_PressBox_Stair_{st}", (X(pd1 + 0.45), cy + pw / 2.0 - 0.6 - st * 0.28, (st + 1) * pz / 12.0 - 0.02), (0.90, 0.28, 0.04), (0.40, 0.42, 0.44, 1.0))
        make_box(f"{tag}_PressBox_Stair_Stringer", (X(pd1 + 0.92), cy + pw / 2.0 - 2.2, pz / 2.0), (0.04, 3.6, pz), (0.40, 0.42, 0.44, 1.0))


def build_bleachers():
    """HOME stands east, behind the home bench — "Third row, behind
    the home bench" (vol6 ch22). Drafts 1-4 built them along the WEST
    sideline, across the field from the home bench, so Eileen's chair
    sat in the visitors' stands. A smaller visitors' stand west."""
    _stands("Bleach", HOME_SIDE, 9, 18.0, MID_Y, press_box=True)
    _stands("VisBleach", -HOME_SIDE, 5, 12.0, MID_Y)


def build_spectators():
    coats = [(0.42,0.30,0.34,1.0),(0.30,0.36,0.44,1.0),(0.46,0.42,0.30,1.0),
             (0.36,0.44,0.38,1.0),(0.52,0.40,0.36,1.0),(0.34,0.34,0.40,1.0)]
    skin = (0.62, 0.48, 0.40, 1.0)
    pants = (0.26, 0.28, 0.32, 1.0)
    home = [(2,-14.0),(2,-3.5),(2,3.0),(3,8.5),(3,-2.0),(4,-10.0),(4,5.5),(4,13.0),
            (5,0.5),(5,-6.0),(6,-12.5),(6,3.5),(6,9.0),(7,-3.5),(7,15.0),(8,6.0)]
    away = [(1,-6.0),(1,4.5),(2,-1.0),(3,7.0),(3,-8.5),(4,2.0)]
    for tag, sign, seats in (("Fan", HOME_SIDE, home), ("VisFan", -HOME_SIDE, away)):
        for si, (step, yo) in enumerate(seats):
            S = 0.45 + step * 0.42
            px = sign * (SIDE_X + 6.0 + step * 0.8 + 0.63)
            lx = sign * (SIDE_X + 6.0 + step * 0.8 + 0.39)
            py = MID_Y + yo
            col = coats[(si + (3 if sign < 0 else 0)) % len(coats)]
            make_box(f"{tag}_{si}_Torso", (px, py, S + 0.24), (0.34, 0.34, 0.48), col)
            make_cyl(f"{tag}_{si}_Head", (px, py, S + 0.56), 0.10, 0.16, skin, segments=8)   # on the shoulders
            make_box(f"{tag}_{si}_Legs", (lx, py, S - 0.21), (0.18, 0.30, 0.42), pants)


def build_players():
    """A practice scrimmage at the south 35 — human figures are the
    scale reference that makes 120 yards READ as 120 yards (user:
    "maybe reads as too big, if those lil things are supposed to be
    players" — the lil things were drill cones; these are players).
    Home wine-red vs practice whites, two lines across the ball."""
    skin = (0.62, 0.48, 0.40, 1.0)
    wine = (0.55, 0.14, 0.14, 1.0)     # school colors (ben's jersey)
    whites = (0.86, 0.86, 0.82, 1.0)
    pants = (0.78, 0.76, 0.70, 1.0)
    line_y = GL_S + 35.0 * YD
    xs = (-6.0, -4.0, -2.0, 0.0, 2.0, 4.0, 6.0)
    for side, (jersey, dy) in enumerate(((wine, -0.8), (whites, +0.8))):
        for pi, px in enumerate(xs):
            tag = f"P{side}_{pi}"
            py = line_y + dy
            make_box(f"Player_{tag}_Legs", (px, py, 0.42), (0.34, 0.26, 0.84), pants)
            make_box(f"Player_{tag}_Torso", (px, py, 1.10), (0.46, 0.30, 0.52), jersey)
            make_cyl(f"Player_{tag}_Head", (px, py, 1.46), 0.11, 0.18, skin, segments=8)   # on the shoulders (2026-09-22)
            make_cyl(f"Player_{tag}_Helmet", (px, py, 1.54), 0.125, 0.10, jersey, segments=8)
    # QB in the gun + a back, home side
    for tag, (px, py) in (("QB", (0.0, line_y - 3.2)), ("RB", (1.4, line_y - 4.6))):
        make_box(f"Player_{tag}_Legs", (px, py, 0.42), (0.34, 0.26, 0.84), pants)
        make_box(f"Player_{tag}_Torso", (px, py, 1.10), (0.46, 0.30, 0.52), wine)
        make_cyl(f"Player_{tag}_Head", (px, py, 1.46), 0.11, 0.18, skin, segments=8)
        make_cyl(f"Player_{tag}_Helmet", (px, py, 1.54), 0.125, 0.10, wine, segments=8)
    # Coach K on the home sideline at the line of scrimmage
    make_box("Coach_Legs", (SIDE_X + 1.2, line_y, 0.46), (0.36, 0.28, 0.92), (0.30, 0.30, 0.34, 1.0))
    make_box("Coach_Torso", (SIDE_X + 1.2, line_y, 1.18), (0.48, 0.32, 0.52), (0.30, 0.36, 0.52, 1.0))
    make_cyl("Coach_Head", (SIDE_X + 1.2, line_y, 1.53), 0.11, 0.18, skin, segments=8)


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
        make_cyl(f"Cooler_{wi}_Body", (hx + 1.0, wy, 0.30), 0.24, 0.60, (0.92, 0.48, 0.18, 1.0), segments=12)   # on the ground (2026-09-22)
        make_cyl(f"Cooler_{wi}_Lid", (hx + 1.0, wy, 0.62), 0.25, 0.06, (0.92, 0.90, 0.86, 1.0), segments=12)
        make_box(f"Cooler_{wi}_Spigot", (hx + 0.74, wy, 0.20), (0.06, 0.05, 0.05), P.METAL_BLACK)
    rx = hx + 1.6
    # (2026-09-22: two bars and five helmets in the air — the rack's
    # uprights, and the helmets sit on the lower bar)
    for uy in (MID_Y - 6.45, MID_Y - 3.55):
        make_box(f"Rack_Upright_{uy:.0f}", (rx, uy, 0.565), (0.06, 0.06, 1.13), COL_METAL)
    make_box("Rack_Bar_T", (rx, MID_Y - 5.0, 1.10), (0.06, 3.0, 0.06), COL_METAL)
    make_box("Rack_Bar_B", (rx, MID_Y - 5.0, 0.60), (0.06, 3.0, 0.06), COL_METAL)
    for hi in range(5):
        hy = MID_Y - 6.2 + hi * 0.6
        make_cyl(f"Rack_Helmet_{hi}", (rx, hy, 0.74), 0.11, 0.14, (0.30, 0.36, 0.52, 1.0), axis='Y', segments=10)


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
    make_box("Score_QtrBox", (sx, sy - 0.24, 5.55), (0.7, 0.06, 0.7), (0.94, 0.30, 0.22, 1.0))   # under the clock, on the panel (2026-09-22)


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
        make_box(f"Chain_Link_{li}", (cx, ly, 0.015), (0.03, (y1 - y0) / links * 0.6, 0.03), P.METAL_STEEL)   # on the turf (2026-09-22)
    make_cyl("Down_Pole", (cx, y0 - 1.8, 1.0), 0.03, 2.0, COL_METAL, segments=6)
    make_box("Down_Box", (cx, y0 - 1.8, 2.1), (0.40, 0.10, 0.40), (0.94, 0.82, 0.28, 1.0))
    make_box("Down_Num", (cx - 0.06, y0 - 1.8, 2.1), (0.005, 0.20, 0.24), P.METAL_BLACK)


def build_floodlights():
    # Six poles, three per side, 18m — Friday night lights that read
    # from anywhere on the field.
    # x +-33.9: the west row must clear the BACK of the stands
    # (the mid pole used to stand inside the risers).
    # draft 5: the poles stand behind the stands (home east at +18, visitors west at -12)
    wx, ex = -(SIDE_X + 12.0), +(SIDE_X + 18.0)
    for pi, (px, py) in enumerate(((wx, GL_S + 15.0 * YD), (wx, MID_Y), (wx, GL_N - 15.0 * YD),
                                   (ex, GL_S + 15.0 * YD), (ex, MID_Y), (ex, GL_N - 15.0 * YD))):
        # draft 4 (2026-09-18): a tapered pole on its base plate, the
        # conduit up the field side, a transformer box at the foot
        make_lathe(f"Pole_{pi}", (px, py, 0.0), [(0.34, 0.0), (0.34, 0.04), (0.19, 0.06), (0.17, 6.0), (0.13, 12.0), (0.10, 18.0), (0.0, 18.0)], COL_POLE, segments=10)
        make_tube(f"Pole_{pi}_Conduit", [(px + (1.0 if px < 0 else -1.0) * 0.20, py + 0.10, 0.4), (px + (1.0 if px < 0 else -1.0) * 0.19, py + 0.10, 16.4)], 0.03, (0.36, 0.36, 0.38, 1.0), segments=5)
        make_chamfer_box(f"Pole_{pi}_Box", (px + (1.0 if px < 0 else -1.0) * 0.45, py + 0.55, 0.35), (0.40, 0.30, 0.70), (0.36, 0.38, 0.36, 1.0), chamfer=0.015)   # on the ground (2026-09-22)
        toward = 1.0 if px < 0 else -1.0
        # Bank faces the FIELD: wide along y, hung on the field side
        # of its pole.
        make_box(f"Bank_{pi}", (px + toward * 0.55, py, 17.2), (0.40, 2.6, 1.5), P.METAL_BLACK)
        for li in range(12):
            ly = -1.0 + (li % 4) * 0.66
            lz = -0.5 + (li // 4) * 0.5
            make_cyl(f"Lamp_{pi}_{li}", (px + toward * 0.80, py + ly, 17.2 + lz),
                     0.14, 0.10, COL_LAMP, axis='X', segments=8)
            make_cyl(f"Lamp_{pi}_{li}_Hood", (px + toward * 0.74, py + ly, 17.2 + lz),
                     0.17, 0.06, (0.22, 0.22, 0.24, 1.0), axis='X', segments=10)


def build_fence():
    # Perimeter chain-link behind the north end zone (banner fence)
    n = 26
    fw = FIELD_W + 12.0
    fy = FIELD_LEN + 2.6
    for i in range(n):
        fx = -fw / 2.0 + i * (fw / (n - 1))
        make_lathe(f"FencePost_{i}", (fx, fy, 0.0), [(0.03, 0.0), (0.03, 1.18), (0.035, 1.20), (0.0, 1.22)], COL_METAL, segments=6)
    make_box("Fence_Mesh", (0.0, fy, 0.62), (fw, 0.008, 1.10), (0.62, 0.64, 0.66, 0.28))   # draft 4: the chain-link reads
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
    # on the house's north face (y -6.80); 2026-09-22: 4-6 cm off it
    make_box("Field_House_Door", (-16.0, -6.77, 1.05), (0.90, 0.06, 2.10), (0.30, 0.32, 0.36, 1.0))
    make_box("Corkboard", (-13.2, -6.775, 1.55), (1.40, 0.05, 1.00), (0.52, 0.38, 0.26, 1.0))
    make_box("Corkboard_Frame", (-13.2, -6.78, 1.55), (1.50, 0.04, 1.10), wood)
    make_box("DepthChart_Sheet", (-13.2, -6.745, 1.60), (0.30, 0.01, 0.42), (0.92, 0.90, 0.82, 1.0))
    # Parking lot + the staged vehicles
    make_box("Parking_Lot", (0.0, -12.0, 0.01), (56.0, 16.0, 0.04), (0.24, 0.24, 0.26, 1.0))
    for si in range(10):
        make_box(f"Lot_Stripe_{si}", (-18.0 + si * 4.0, -6.4, 0.035), (0.10, 2.2, 0.01), (0.72, 0.70, 0.60, 1.0))
    # draft 4: the staged vehicles from the vehicle kit
    from _props.vehicles import make_car
    make_car("CoachK_Truck", 13.5, -6.5, 5.6, (0.90, 0.90, 0.88, 1.0), pickup=True, along="Y", z0=0.03)
    # draft 5: "the white Ford F-250 with the camper shell and the ladder
    # rack and the tape job on the driver's-side mirror" (vol6 ch13) — it was red and bare
    fx, fy, fz = 13.5, -6.5, 0.03
    make_box("CoachK_Truck_Camper_Shell", (fx, fy - 1.675, fz + 1.62), (1.70, 2.05, 0.26), (0.88, 0.88, 0.86, 1.0))
    for sgn in (-1, 1):
        make_box(f"CoachK_Truck_Camper_Window_{sgn:+d}", (fx + sgn * 0.855, fy - 1.675, fz + 1.63), (0.01, 1.50, 0.16), (0.20, 0.22, 0.26, 1.0))
    make_box("CoachK_Truck_Camper_Rear_Glass", (fx, fy - 2.705, fz + 1.62), (1.40, 0.01, 0.20), (0.20, 0.22, 0.26, 1.0))
    for i, (dx, dy) in enumerate(((-0.78, -2.6), (0.78, -2.6), (-0.78, -0.75), (0.78, -0.75))):
        make_box(f"CoachK_Truck_Rack_Post_{i}", (fx + dx, fy + dy, fz + 1.90), (0.05, 0.05, 0.30), (0.20, 0.20, 0.22, 1.0))
    for i, dy in enumerate((-2.6, -0.75)):
        make_box(f"CoachK_Truck_Rack_Cross_{i}", (fx, fy + dy, fz + 2.07), (1.66, 0.06, 0.05), (0.20, 0.20, 0.22, 1.0))
    for sgn in (-1, 1):
        make_box(f"CoachK_Truck_Rack_Rail_{sgn:+d}", (fx + sgn * 0.60, fy - 0.80, fz + 2.115), (0.05, 4.20, 0.04), (0.20, 0.20, 0.22, 1.0))
    make_box("CoachK_Truck_Ladder", (fx - 0.10, fy - 0.80, fz + 2.13), (0.42, 4.10, 0.07), (0.70, 0.70, 0.72, 1.0))
    make_box("CoachK_Truck_Mirror_Tape", (fx - 1.112, fy + 0.60, fz + 1.10), (0.008, 0.10, 0.04), (0.70, 0.70, 0.66, 1.0))
    make_car("Civic", -22.0, -11.4, 4.4, (0.55, 0.58, 0.62, 1.0), along="Y", z0=0.03)
    make_car("Tacoma", -8.4, -12.9, 5.0, (0.24, 0.30, 0.26, 1.0), pickup=True, along="Y", z0=0.03)
    # Eileen's folding chair — THIRD ROW OF THE HOME STANDS, behind the home
    # bench (draft 5: the stands moved east), on row 2's footboard facing the field
    ex_ = HOME_SIDE * (SIDE_X + 6.0 + 2 * 0.8 + 0.225)
    ey_ = MID_Y - 9.5
    bench_top = 0.45 + 2 * 0.42 - 0.42          # row 2's footboard top
    for sgn in (-1, 1):
        make_rot_box(f"Eileen_Chair_Leg_{sgn:+d}", (ex_, ey_ + sgn * 0.17, bench_top + 0.20), (0.025, 0.025, 0.46), (0.30, 0.30, 0.32, 1.0), yaw=0.0, roll=sgn * 0.55)
        make_rot_box(f"Eileen_Chair_LegB_{sgn:+d}", (ex_, ey_ - sgn * 0.17, bench_top + 0.20), (0.025, 0.025, 0.46), (0.30, 0.30, 0.32, 1.0), yaw=0.0, roll=-sgn * 0.55)
    make_chamfer_box("Eileen_Chair_Seat", (ex_, ey_, bench_top + 0.40), (0.42, 0.42, 0.03), (0.36, 0.42, 0.55, 1.0), chamfer=0.008)
    make_rot_box("Eileen_Chair_Back", (ex_ + HOME_SIDE * 0.20, ey_, bench_top + 0.60), (0.03, 0.42, 0.36), (0.32, 0.38, 0.50, 1.0), pitch=HOME_SIDE * 0.15)
    # Equipment shed + Coach Dale's truck, beyond the NW corner
    make_box("Equip_Shed", (-30.0, FIELD_LEN + 6.0, 1.3), (4.0, 3.0, 2.6), (0.48, 0.42, 0.34, 1.0))
    make_box("Equip_Shed_Roof", (-30.0, FIELD_LEN + 6.0, 2.75), (4.4, 3.4, 0.3), (0.34, 0.30, 0.26, 1.0))
    make_box("Equip_Shed_Door", (-30.0, FIELD_LEN + 4.46, 1.05), (1.3, 0.06, 2.1), (0.30, 0.26, 0.22, 1.0))
    make_car("Dale_Pickup", -30.0, FIELD_LEN + 11.3, 5.0, (0.44, 0.40, 0.34, 1.0), pickup=True, along="Y", z0=-0.03)
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


def build_hero_props_2026_09():
    """HERO PROPS FOR THE BLIND CUES (shot_marker_audit, 2026-09-01).

    Four distinct cues. Eileen's folding chair already exists
    (SYNONYMS folding_chair -> eileen_chair). Built:

    - THE VINTON BUS ("pulls into the lot at four oh-three"):
      flat-front school bus on the lot's east half — body, window
      band, black rub stripe, bumper, four wheels.
    - COACH K'S STOPWATCH ("partly theater ... the prop that gives
      the team the data point"): on the home bench with its strap,
      where ritual props rest between drills.
    - BEN'S PHONE (Maya's three forty-six text): face-up further
      down the same bench.
    """
    bus_yellow = (0.85, 0.62, 0.16, 1.0)
    # ── THE VINTON BUS · lot east half ──
    make_box("Vinton_Bus_Body", (10.0, -12.0, 1.45), (8.50, 2.40, 1.90), bus_yellow)
    make_box("Vinton_Bus_Windows", (10.0, -10.785, 1.95), (7.00, 0.030, 0.50),
             (0.26, 0.30, 0.36, 1.0))
    make_box("Vinton_Bus_Stripe", (10.0, -10.785, 1.30), (7.80, 0.030, 0.12),
             (0.12, 0.12, 0.13, 1.0))
    make_box("Vinton_Bus_Bumper", (14.30, -12.0, 0.75), (0.10, 2.30, 0.25),
             (0.30, 0.30, 0.32, 1.0))
    for wi, (wx2, wy2) in enumerate(((7.0, -10.65), (13.0, -10.65),
                                     (7.0, -13.35), (13.0, -13.35))):
        make_cyl(f"Vinton_Bus_Wheel_{wi}", (wx2, wy2, 0.42), 0.42, 0.30,
                 (0.13, 0.13, 0.14, 1.0), axis='Y', segments=10)
    # ── THE STOPWATCH · home bench (top 0.50) ──
    make_cyl("Coach_Stopwatch", (26.4, 44.0, 0.506), 0.030, 0.012,
             (0.82, 0.82, 0.84, 1.0), segments=10)
    make_cyl("Stopwatch_Crown", (26.4, 43.972, 0.517), 0.006, 0.010,
             (0.55, 0.55, 0.58, 1.0), segments=6)
    make_box("Stopwatch_Strap", (26.4, 44.075, 0.5015), (0.012, 0.090, 0.003),
             (0.16, 0.16, 0.18, 1.0))
    # ── BEN'S PHONE · same bench, further north ──
    make_box("Bens_Phone", (26.4, 48.5, 0.5055), (0.070, 0.140, 0.011),
             (0.13, 0.13, 0.15, 1.0))


def build_horizon_2026_08():
    """STUMP HUNT: evening treelines past the fences, centered on the
    FIELD (cy=55) so the first band clears the 110m gridiron + the
    scoreboard instead of standing on the 50-yard line."""
    # GROUND under everything out past the last band (2026-08-09,
    # user: "no ground on any of the roads — a flat expanse of
    # nothing"). Locale-colored so exteriors stop sharing a void.
    make_box("Ground_Far", (0.0, 55.0, -0.03), (1240.0, 1240.0, 0.02),
             (0.15, 0.24, 0.13, 1.0))
    from _props.detail import make_far_bands
    make_far_bands("FarTrees", (0.13, 0.20, 0.11),
                   [(95.0, 110.0, 8.0, 0.90), (180.0, 170.0, 11.0, 0.70),
                    (330.0, 260.0, 14.0, 0.52), (540.0, 400.0, 17.0, 0.40)],
                   cy=55.0, profile="treeline")


def build_draft4_2026_09():
    """DRAFT 4 (2026-09-18, lore/_VISUAL_PROGRAM.md §3; 8 placements).
    An exterior's wear is where the grass is gone: the worn band between
    the hashes, the goal mouths, the dirt under both benches, the path
    along the home sideline from the gate, the tread inside the gate.
    D3: the field house's light over its door (the corkboard climax is
    read under it), the scoreboard's cable, the goalposts' pads. D5
    exists (the 08 horizon); the lot's stripes stay.
    """
    from _props.detail import make_traffic_wear, make_floor_stain
    worn = (0.30, 0.34, 0.20, 1.0)
    dirt = (0.36, 0.30, 0.20, 1.0)
    make_box("Wear_Middle_Band", (0.0, MID_Y, 0.0012), (HASH_X * 2.0 - 1.0, 60.0, 0.006), (0.20, 0.33, 0.17, 1.0))
    for gy in (GL_S + 2.0, GL_N - 2.0):
        make_floor_stain(f"Wear_Goalmouth_{gy:.0f}", (0.0, gy), radius=3.2, tint=worn, segments=14)
    for by_ in (MID_Y - 8.0, MID_Y + 8.0):
        ex_ = (SIDE_X + 2.0) if by_ < MID_Y else -(SIDE_X + 2.0)
        make_box(f"Wear_Bench_Dirt_{by_:.0f}", (ex_ + (0.6 if by_ < MID_Y else -0.6), by_, 0.001), (1.6, 12.4, 0.004), dirt)
    make_traffic_wear("Wear_Path_Sideline", [(10.5, -2.6), (18.0, 4.0), (SIDE_X + 1.2, 20.0), (SIDE_X + 1.2, 44.0)], width=1.2, tint=dirt)
    make_floor_stain("Wear_Gate_Tread", (10.5, -3.0), radius=1.6, tint=dirt, segments=12)
    # ── D3 ──
    # against the house face
    make_lathe("FieldHouse_Lamp_Canopy", (-16.0, -6.72, 2.55), [(0.08, 0.0), (0.08, 0.02), (0.02, 0.04), (0.0, 0.04)], (0.30, 0.30, 0.32, 1.0), segments=8)
    make_lathe("FieldHouse_Lamp_Glass", (-16.0, -6.70, 2.33), [(0.03, 0.0), (0.07, 0.04), (0.075, 0.14), (0.05, 0.22), (0.0, 0.23)], (0.96, 0.90, 0.72, 0.9), segments=10)   # under its canopy (2026-09-22)
    make_tube("Score_Cable", [(0.0, FIELD_LEN + 9.0, 5.8), (0.0, FIELD_LEN + 9.1, 3.0), (0.6, FIELD_LEN + 9.6, 0.0)], 0.02, (0.16, 0.16, 0.18, 1.0), segments=5)
    make_chamfer_box("Score_Box", (1.2, FIELD_LEN + 9.8, 0.30), (0.60, 0.40, 0.60), (0.36, 0.38, 0.36, 1.0), chamfer=0.015)
    for tag, gy in (("S", 0.0), ("N", FIELD_LEN)):
        make_lathe(f"Goal_{tag}_Pad", (0.0, gy, 0.0), [(0.20, 0.0), (0.20, 1.8), (0.12, 1.9), (0.0, 1.9)], (0.30, 0.36, 0.52, 1.0), segments=10)


def main():
    clear_scene()
    build_ground()
    build_hashmarks()
    build_goalposts()
    build_bleachers()
    build_spectators()
    build_benches()
    build_players()
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
    build_hero_props_2026_09()
    build_draft4_2026_09()
    export_glb(out)


if __name__ == "__main__":
    main()
