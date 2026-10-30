"""small_wood_field — vol 2's football field at Small Wood High (draft 1,
2026-10-27). The Oregon coast, fall 1997 (_MASTER_TIMELINE: the Small Wood
volumes ~1997-98).

The Deck: "football field and stadium is still nonsense … it's all
illogical nonsense." Vol 2's field scenes were borrowing vol 6's stadium —
a 2026 Texas planned community's field (aluminium stands, the press box,
Coach K's F-250) — for a 1997 Oregon town. Small Wood gets its own:

  points of impact (vol2_ch3): "The Friday night of our first home game was
   raucous. The crowd was electric, the turnout left the minority of town
   still at home"; "The stadium lights hung over the field in a white haze,
   the bleachers stamping and steaming in the cold."; "the pride and joy of
   Small Wood"; a hit and run "two blocks from the stadium"
                                                    → small_wood_field_night
  rewind (vol2_ch3): "The home game, my helmet off while I stood on the
   sidelines."; "they flashed R.I.P. on the scoreboard and people filed out
   and away into the night"; "a candlelight vigil at church across the
   street"                         → small_wood_field_night, insert scoreboard
  interlude one (vol2_ch2): two-a-days in summer — "morning and evening
   sessions of football practice"; May "Content just to sit around half the
   day and watch the boys practice football"   → small_wood_field_dusk

ANDY (2026-10-27): the school is green primary, white secondary; a running
track rings the field; the home stand is covered, under an elevated slanted
roof. PROPOSED (the text gives none of the rest — Andy may correct any of
it): the stand's wood and its press box and fascia sign, the track's red
all-weather surface, the creosoted wooden light poles, the visitors' white
and maroon, the concession shed, the ticket booth, the gravel lot, the
church's steeple, the fir wall.

The gridiron is vol 6's, true scale (build_school_field_evening's ground,
lines and goalposts): x sideline to sideline (0 = midfield), y downfield
(south end line 0, north 109.7), z up; Godot (x, z, -y). The home side is
EAST, the grandstand behind the home bench; visitors' bleachers west; the
gate, the lot and the street south; the church across the street.

DRAFT 3 targets: the grandstand's aisle stairs and the tunnel under it;
the crowd's postures (stamping, arms up); breath and steam as particles;
the vigil's candles across the street (rewind's after-game); the track's
field events (a long-jump pit, the high-jump apron) if Andy wants them;
join the firs and lighten the crowd (the GLB is ~16 MB); Deck framing.
"""
import os, sys, math
_BT = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
if _BT not in sys.path: sys.path.insert(0, _BT)
_HERE = os.path.dirname(os.path.abspath(__file__))
if _HERE not in sys.path: sys.path.insert(0, _HERE)
from _props import palette as P
from _props.geometry import (clear_scene, make_box, make_cyl, make_taper_cyl, make_rot_box,
                             make_chamfer_box, make_tube, join_stock, export_glb)
from _props.trees import make_conifer
from _props.vehicles import make_car
import build_school_field_evening as SF

try:
    import bpy
except ImportError:
    bpy = None

SIDE_X, MID_Y, FIELD_LEN = SF.SIDE_X, SF.MID_Y, SF.FIELD_LEN
NIGHT = "__small_wood_field_night"
DUSK = "__small_wood_field_dusk"

# DRAFT 2 (2026-10-27, Andy): "small wood high is green primary white
# secondary"; "the field has a running track around it"; "Home stand is
# covered with an elevated slanted roof." A 400 m track rings the field
# (straights 84.39 m, inner radius 36.5 m, six 1.22 m lanes — the end zones
# sit inside its curves), so both stands, the poles, the scoreboard, the gate
# and the lot stand outside it.
TRACK_R, LANE, LANES = 36.5, 1.22, 6
TRACK_W = LANE * LANES                          # 7.32
TRACK_HALF = 84.39 / 2.0
TRACK_OUT = TRACK_R + TRACK_W                   # 43.82
TRACK_RED = (0.50, 0.24, 0.18, 1.0)             # all-weather, weathered (proposed)
RAIL_R = TRACK_OUT + 0.4

# the covered home grandstand, east, past the track and its walk
GS_X0 = TRACK_OUT + 2.56          # the front wall's field face (46.38)
GS_LEN = 60.0
GS_ROWS = 14
TREAD, RISE, Z0 = 0.80, 0.42, 1.10
GS_XB = GS_X0 + 0.30 + TREAD * GS_ROWS          # the back wall
ROOF_F = (GS_X0 - 0.8, 10.0)                    # front edge (x, z): the roof stands high
ROOF_B = (GS_XB + 0.5, 12.6)                    # back edge
VIS_D0 = TRACK_OUT + 1.56 - SIDE_X              # the visitors' bleachers' front, past the track
FENCE_S, FENCE_N = -36.0, FIELD_LEN + 42.0      # clear of the track's curves (-31.2 / 140.9)
SCORE_Y = FIELD_LEN + 36.0
SOUTH = -24.0                                   # the lot, the street, the church moved south past the track

PAINT = (0.84, 0.82, 0.76, 1.0)       # weathered white
TRIM = (0.10, 0.34, 0.19, 1.0)        # the school's green
ROOF = (0.20, 0.26, 0.24, 1.0)
SEAT_WOOD = (0.52, 0.40, 0.28, 1.0)
STEP_WOOD = (0.42, 0.36, 0.30, 1.0)
CREOSOTE = (0.26, 0.19, 0.13, 1.0)
LAMP = (1.0, 0.98, 0.90, 1.0)
CONC = (0.56, 0.55, 0.52, 1.0)
GRAVEL = (0.50, 0.48, 0.44, 1.0)
ASPHALT = (0.20, 0.20, 0.22, 1.0)
FIR = (0.12, 0.24, 0.16, 1.0)
FIR_TRUNK = (0.30, 0.22, 0.16, 1.0)
MUD = (0.24, 0.20, 0.14, 1.0)

COATS = [(0.20, 0.28, 0.44, 1.0), (0.46, 0.14, 0.14, 1.0), (0.18, 0.30, 0.22, 1.0), (0.30, 0.28, 0.26, 1.0),
         (0.62, 0.56, 0.44, 1.0), (0.12, 0.12, 0.14, 1.0), (0.54, 0.34, 0.18, 1.0), (0.70, 0.66, 0.20, 1.0),
         (0.36, 0.20, 0.34, 1.0), (0.24, 0.40, 0.50, 1.0)]
SKIN = [(0.86, 0.70, 0.58, 1.0), (0.74, 0.56, 0.42, 1.0), (0.92, 0.78, 0.66, 1.0), (0.56, 0.40, 0.30, 1.0)]
# green primary, white secondary (Andy, 2026-10-27)
HOME_JERSEY, HOME_HELMET = (0.10, 0.36, 0.20, 1.0), (0.10, 0.34, 0.19, 1.0)
HOME_COATS = COATS + [(0.10, 0.36, 0.20, 1.0), (0.88, 0.88, 0.86, 1.0), (0.10, 0.36, 0.20, 1.0), (0.12, 0.30, 0.18, 1.0)]
AWAY_JERSEY, AWAY_HELMET = (0.90, 0.90, 0.88, 1.0), (0.42, 0.10, 0.14, 1.0)
PANTS = (0.88, 0.86, 0.80, 1.0)


def _rng(seed):
    s = [seed & 0x7fffffff or 1]
    def r():
        s[0] = (s[0] * 1103515245 + 12345) & 0x7fffffff
        return s[0] / 0x7fffffff
    return r


def build_field():
    """The gridiron (vol 6's, true scale) and a home field's wear: the
    Oregon fall has the middle of it in mud by the first home game."""
    SF.build_ground()
    SF.build_hashmarks()
    SF.build_goalposts()
    make_box("Ground_Beyond", (0.0, MID_Y - 20.0, -0.06), (420.0, 420.0, 0.04), (0.13, 0.20, 0.12, 1.0))
    # the worn band between the hashes, the goal mouths
    for i, (y0, y1) in enumerate(((SF.GL_S + 6.0, SF.GL_N - 6.0),)):
        make_box(f"Wear_Middle_{i}", (0.0, (y0 + y1) / 2.0, 0.002), (2 * SF.HASH_X - 2.0, y1 - y0, 0.004), (0.22, 0.26, 0.15, 1.0))
    for tag, gy in (("S", SF.GL_S), ("N", SF.GL_N)):
        make_box(f"Mud_GoalMouth_{tag}", (0.0, gy + (2.5 if tag == "S" else -2.5), 0.0045), (9.0, 5.0, 0.004), MUD)
    make_box("Mud_Midfield", (0.0, MID_Y, 0.0045), (12.0, 7.0, 0.004), MUD)


def build_track():
    """The 400 m track round the field (Andy, 2026-10-27): two straights and
    two curves of six lanes, the lane lines white; the end zones sit inside
    the curves. Parts named `_Stock_` join to one mesh per kind."""
    white = (0.90, 0.90, 0.86, 1.0)
    for sx in (-1, +1):
        make_box(f"Track_Stock_Straight_{sx:+d}", (sx * (TRACK_R + TRACK_W / 2.0), MID_Y, -0.01), (TRACK_W, 2 * TRACK_HALF, 0.04), TRACK_RED)
        for i in range(LANES + 1):
            make_box(f"TrackLine_Stock_S{sx:+d}_{i}", (sx * (TRACK_R + i * LANE), MID_Y, 0.012), (0.05, 2 * TRACK_HALF, 0.01), white)
    n = 28
    dth = math.pi / n
    for tag, cy, th0 in (("N", MID_Y + TRACK_HALF, 0.0), ("S", MID_Y - TRACK_HALF, math.pi)):
        for k in range(n):
            th = th0 + (k + 0.5) * dth
            c, sn = math.cos(th), math.sin(th)
            rm = TRACK_R + TRACK_W / 2.0
            make_rot_box(f"Track_Stock_{tag}_{k}", (rm * c, cy + rm * sn, -0.01),
                         (TRACK_W, 2.0 * TRACK_OUT * math.sin(dth / 2.0) + 0.05, 0.04), TRACK_RED, yaw=th)
            for i in range(LANES + 1):
                ri = TRACK_R + i * LANE
                make_rot_box(f"TrackLine_Stock_{tag}{k}_{i}", (ri * c, cy + ri * sn, 0.012),
                             (0.05, 2.0 * ri * math.sin(dth / 2.0) + 0.02, 0.01), white, yaw=th)
    # the start line and the stagger marks on the home straight
    make_box("TrackLine_Stock_Start", (TRACK_R + TRACK_W / 2.0, MID_Y - TRACK_HALF + 2.0, 0.013), (TRACK_W, 0.06, 0.01), white)


def build_grandstand():
    """The covered home grandstand: a concrete front wall on the walk,
    fourteen wooden steps with a bench plank on each, a back wall, end
    walls, a shed roof on a row of posts, the press box on top, the
    school's sign on the fascia."""
    y0, y1 = MID_Y - GS_LEN / 2.0, MID_Y + GS_LEN / 2.0
    make_box("GS_Walk", ((TRACK_OUT + GS_X0) / 2.0, MID_Y, 0.02), (GS_X0 - TRACK_OUT, GS_LEN + 20.0, 0.04), CONC)
    make_box("GS_FrontWall", (GS_X0 + 0.15, MID_Y, Z0 / 2.0), (0.30, GS_LEN, Z0), CONC)
    for k in range(GS_ROWS):
        xa = GS_X0 + 0.30 + TREAD * k
        zt = Z0 + RISE * k
        make_box(f"GS_Step_{k}", (xa + TREAD / 2.0, MID_Y, zt / 2.0), (TREAD, GS_LEN, zt), STEP_WOOD)
        make_box(f"GS_Bench_{k}", (xa + TREAD - 0.22, MID_Y, zt + 0.43), (0.30, GS_LEN - 0.4, 0.05), SEAT_WOOD)
        for b in range(9):
            make_box(f"GS_BenchLeg_{k}_{b}", (xa + TREAD - 0.22, y0 + 1.0 + b * (GS_LEN - 2.0) / 8.0, zt + 0.205),
                     (0.06, 0.06, 0.41), SEAT_WOOD)
    rise = ROOF_B[1] - ROOF_F[1]
    run = ROOF_B[0] - ROOF_F[0]
    make_box("GS_BackWall", (GS_XB + 0.15, MID_Y, ROOF_B[1] / 2.0), (0.30, GS_LEN, ROOF_B[1]), PAINT)
    for tag, ey in (("S", y0), ("N", y1)):
        make_box(f"GS_EndWall_{tag}", ((GS_X0 + GS_XB) / 2.0 + 0.15, ey, ROOF_F[1] / 2.0), (GS_XB - GS_X0 + 0.3, 0.25, ROOF_F[1]), PAINT)
        make_box(f"GS_EndWall_{tag}_Trim", ((GS_X0 + GS_XB) / 2.0 + 0.15, ey, ROOF_F[1] - 0.12), (GS_XB - GS_X0 + 0.4, 0.30, 0.24), TRIM)
    make_rot_box("GS_Roof", ((ROOF_F[0] + ROOF_B[0]) / 2.0, MID_Y, (ROOF_F[1] + ROOF_B[1]) / 2.0),
                 (math.hypot(run, rise), GS_LEN + 1.2, 0.22), ROOF, pitch=-math.atan2(rise, run))
    make_box("GS_Fascia", (ROOF_F[0] - 0.05, MID_Y, ROOF_F[1] - 0.25), (0.10, GS_LEN + 1.2, 0.70), TRIM)
    # the school's sign on the fascia (a hero-art stand-in)
    make_box("GS_Fascia_Sign", (ROOF_F[0] - 0.12, MID_Y, ROOF_F[1] - 0.25), (0.04, 8.0, 0.56), PAINT)
    make_box("GS_Fascia_Sign_Text", (ROOF_F[0] - 0.15, MID_Y, ROOF_F[1] - 0.25), (0.02, 6.6, 0.30), TRIM)
    # the front posts on the wall, the roof's under-beams
    for i in range(9):
        py = y0 + 0.4 + i * (GS_LEN - 0.8) / 8.0
        zr = ROOF_F[1] + (GS_X0 + 0.15 - ROOF_F[0]) * rise / run - 0.12
        make_box(f"GS_Post_{i}", (GS_X0 + 0.15, py, (Z0 + zr) / 2.0), (0.24, 0.24, zr - Z0), TRIM)
        make_rot_box(f"GS_Beam_{i}", ((ROOF_F[0] + ROOF_B[0]) / 2.0, py, (ROOF_F[1] + ROOF_B[1]) / 2.0 - 0.24),
                     (math.hypot(run, rise), 0.16, 0.26), TRIM, pitch=-math.atan2(rise, run))
    # the under-roof lamps (practicals: the .tscn lights them)
    for i in range(6):
        py = y0 + 5.0 + i * (GS_LEN - 10.0) / 5.0
        zr = ROOF_F[1] + (GS_X0 + 4.0 - ROOF_F[0]) * rise / run - 0.40
        make_cyl(f"GS_Bulb_{i}", (GS_X0 + 4.0, py, zr), 0.12, 0.10, LAMP, segments=8)
    # the press box on the roof's back, glass toward the field, its own roof
    pb_x0, pb_x1 = GS_XB - 4.0, GS_XB + 0.3
    pz = ROOF_B[1] - 0.6
    make_box("GS_PressBox", ((pb_x0 + pb_x1) / 2.0, MID_Y, pz + 1.3), (pb_x1 - pb_x0, 9.0, 2.6), PAINT)
    make_box("GS_PressBox_Glass", (pb_x0 - 0.01, MID_Y, pz + 1.45), (0.02, 8.2, 0.9), (0.22, 0.26, 0.30, 1.0))
    for k in range(5):
        make_box(f"GS_PressBox_Mullion_{k}", (pb_x0 - 0.025, MID_Y - 4.1 + k * 2.05, pz + 1.45), (0.02, 0.08, 0.9), TRIM)
    make_box("GS_PressBox_Roof", ((pb_x0 + pb_x1) / 2.0 - 0.2, MID_Y, pz + 2.7), (pb_x1 - pb_x0 + 0.8, 9.6, 0.16), ROOF)
    make_box("GS_PressBox_Glow", (pb_x0 + 0.4, MID_Y, pz + 1.45), (0.02, 7.6, 0.7), (0.96, 0.84, 0.56, 1.0))


def _figure(tag, x, y, z, r, coat, standing=True, helmet=None):
    """A person as three or four parts — legs, torso, head (a cap or a
    helmet) — named `<tag>_Stock_<n>_*` so the crowd joins to one mesh."""
    n = int(r() * 1e9)
    skin = SKIN[int(r() * len(SKIN)) % len(SKIN)]
    h = 0.92 + r() * 0.16
    if standing:
        make_box(f"{tag}_Stock_{n}_L", (x, y, z + 0.38 * h), (0.28, 0.22, 0.76 * h), (0.16, 0.16, 0.20, 1.0) if helmet is None else PANTS)
        tz = z + 0.76 * h
    else:
        tz = z
    make_box(f"{tag}_Stock_{n}_T", (x, y, tz + 0.30 * h), (0.42, 0.28, 0.60 * h), coat)
    make_cyl(f"{tag}_Stock_{n}_H", (x, y, tz + 0.60 * h + 0.14), 0.11, 0.24, helmet or skin, segments=8)
    if helmet is None and r() < 0.3:
        make_cyl(f"{tag}_Stock_{n}_C", (x, y, tz + 0.60 * h + 0.29), 0.115, 0.08, COATS[int(r() * 10) % 10], segments=8)


def build_crowd():
    """Friday night: "the turnout left the minority of town still at home"
    — the home stand full and standing, the visitors' thinner, both teams
    on their sidelines and eleven a side on the field. Night only."""
    r = _rng(1997)
    for k in range(GS_ROWS):
        x = GS_X0 + 0.30 + TREAD * k + 0.35
        z = Z0 + RISE * k
        y = MID_Y - GS_LEN / 2.0 + 0.8
        while y < MID_Y + GS_LEN / 2.0 - 0.8:
            if r() < 0.72:
                _figure("CrowdHome", x + (r() - 0.5) * 0.12, y, z, r, HOME_COATS[int(r() * len(HOME_COATS)) % len(HOME_COATS)])
            y += 0.58 + r() * 0.12
    for s in range(8):
        x = -(SIDE_X + VIS_D0 + s * 0.8 + 0.63)
        z = 0.45 + s * 0.42
        y = MID_Y - 14.0
        while y < MID_Y + 14.0:
            if r() < 0.32:
                _figure("CrowdAway", x, y, z, r, COATS[int(r() * 10) % 10], standing=False)
            y += 0.62
    # the teams on their sidelines, south of the 50 (the sideline view looks north of it)
    for i in range(34):
        _figure("TeamHome", SIDE_X + 2.0 + r() * 2.0, MID_Y - 26.0 + i * 0.5 + r() * 0.2, 0.0, r, HOME_JERSEY, helmet=HOME_HELMET)
    for i in range(30):
        _figure("TeamAway", -(SIDE_X + 2.0 + r() * 2.0), MID_Y - 8.0 + i * 0.55, 0.0, r, AWAY_JERSEY, helmet=AWAY_HELMET)
    # eleven a side at the line of scrimmage, the home team driving north
    los = MID_Y + 12.0
    for i in range(11):
        _figure("PlayHome", -9.0 + i * 1.8 + (r() - 0.5) * 0.4, los - 1.0 - (3.0 if i in (4, 5, 6) and r() < 0.5 else 0.0), 0.0, r, HOME_JERSEY, helmet=HOME_HELMET)
        _figure("PlayAway", -9.0 + i * 1.8 + (r() - 0.5) * 0.4, los + 1.2 + (4.0 if i in (0, 10) else 0.0), 0.0, r, AWAY_JERSEY, helmet=AWAY_HELMET)
    # the officials
    for i, (fx, fy) in enumerate(((0.0, los - 9.0), (SIDE_X - 1.0, los), (-SIDE_X + 1.0, los))):
        _figure("Officials", fx, fy, 0.0, r, (0.92, 0.92, 0.92, 1.0))


def build_practice():
    """Two-a-days at dusk (interlude one): a few players walking off, a
    coach with his clipboard at the 40, a girl sitting in the stands
    watching — May — and her car in the lot. Dusk only."""
    r = _rng(722)
    for i in range(7):
        _figure("Practice", 19.0 + i * 1.4 + r(), SF.GL_S + 30.0 + r() * 6.0, 0.0, r, HOME_JERSEY, helmet=HOME_HELMET)
    _figure("PracticeCoach", SIDE_X - 3.0, SF.GL_S + 36.0, 0.0, r, (0.26, 0.28, 0.32, 1.0))
    _figure("PracticeMay", GS_X0 + 0.30 + TREAD * 3 + 0.35, MID_Y - 6.0, Z0 + RISE * 3 + 0.45, r, (0.70, 0.30, 0.24, 1.0), standing=False)


def build_benches():
    for tag, sx in (("Home", +1), ("Away", -1)):
        for b, yy in enumerate((MID_Y - 18.0, MID_Y - 6.0)):
            make_box(f"Bench_{tag}_{b}", (sx * (SIDE_X + 4.6), yy, 0.45), (0.36, 10.0, 0.06), SEAT_WOOD)
            for l in range(5):
                make_box(f"Bench_{tag}_{b}_Leg_{l}", (sx * (SIDE_X + 4.6), yy - 4.6 + l * 2.3, 0.21), (0.30, 0.08, 0.42), SEAT_WOOD)
        make_cyl(f"Cooler_{tag}", (sx * (SIDE_X + 4.6), MID_Y - 24.0, 0.40), 0.26, 0.62, (0.92, 0.48, 0.14, 1.0), segments=12)
        make_box(f"CoolerTable_{tag}", (sx * (SIDE_X + 4.6), MID_Y - 24.0, 0.04), (0.9, 0.9, 0.08), (0.40, 0.42, 0.40, 1.0))


def build_rail_and_fence():
    """A pipe rail round the field (the crowd stays off it) and the
    chain-link perimeter with its gate and ticket booth south."""
    rail = (0.66, 0.68, 0.70, 1.0)
    # the spectators' rail round the track's outside edge, the oval's own shape
    pts = []
    for sgn, cy in ((+1, MID_Y + TRACK_HALF), (-1, MID_Y - TRACK_HALF)):
        for k in range(15):
            th = (0.0 if sgn > 0 else math.pi) + k * math.pi / 14.0
            pts.append((RAIL_R * math.cos(th), cy + RAIL_R * math.sin(th), 1.10))
    pts.append(pts[0])
    for k, (px, py, _z) in enumerate(pts[:-1]):
        make_cyl(f"Rail_Stock_Post_{k}", (px, py, 0.55), 0.035, 1.10, rail, segments=6)
    for k in range(len(pts) - 1):
        make_tube(f"Rail_Stock_Top_{k}", [pts[k], pts[k + 1]], 0.03, rail, segments=6)
    for sx in (-1, +1):
        for k in range(1, 12):
            py = MID_Y - TRACK_HALF + k * (2 * TRACK_HALF) / 12.0
            make_cyl(f"Rail_Stock_Post_{'E' if sx > 0 else 'W'}{k}", (sx * RAIL_R, py, 0.55), 0.035, 1.10, rail, segments=6)
    link = (0.44, 0.46, 0.46, 1.0)
    fx0, fx1, fy0, fy1 = -(SIDE_X + VIS_D0 + 12.5), GS_XB + 4.0, FENCE_S, FENCE_N
    for name, a, b in (("S_W", (fx0, fy0), (12.0, fy0)), ("S_E", (24.0, fy0), (fx1, fy0)), ("N", (fx0, fy1), (fx1, fy1)),
                       ("W", (fx0, fy0), (fx0, fy1)), ("E", (fx1, fy0), (fx1, fy1))):
        L = math.hypot(b[0] - a[0], b[1] - a[1])
        n = max(1, int(L / 3.0))
        for k in range(n + 1):
            t = k / n
            make_cyl(f"Fence_{name}_Post_{k}", (a[0] + (b[0] - a[0]) * t, a[1] + (b[1] - a[1]) * t, 1.2), 0.03, 2.4, link, segments=6)
        make_tube(f"Fence_{name}_Top", [(a[0], a[1], 2.4), (b[0], b[1], 2.4)], 0.025, link, segments=6)
    # the gate (the gap at x 12..24) and the ticket booth beside it
    make_box("Ticket_Booth", (10.2, fy0 - 1.4, 1.3), (2.4, 2.0, 2.6), PAINT)
    make_box("Ticket_Booth_Roof", (10.2, fy0 - 1.4, 2.68), (2.8, 2.4, 0.16), TRIM)
    # its window and sign face the lot, where the town comes from
    make_box("Ticket_Booth_Window", (10.2, fy0 - 2.41, 1.45), (1.2, 0.02, 0.8), (0.90, 0.80, 0.56, 1.0))
    make_box("Ticket_Booth_Sign", (10.2, fy0 - 2.42, 2.25), (1.8, 0.02, 0.36), TRIM)


def build_light_poles():
    """Six creosoted wooden poles, two crossarms of lamps each, aimed at
    the field — the white haze the lights hang in is the night's fog."""
    hx = TRACK_OUT + 1.3              # on the stand's walk, between the track and the stand
    wx = -(SIDE_X + VIS_D0 + 8 * 0.8 + 2.2)
    for pi, (px, py) in enumerate(((wx, MID_Y - 38.0), (wx, MID_Y), (wx, MID_Y + 38.0),
                                   (hx, MID_Y - 38.0), (hx, MID_Y + 38.0), (hx, MID_Y - 52.0))):
        toward = 1.0 if px < 0 else -1.0
        make_taper_cyl(f"Pole_{pi}", (px, py, 10.5), 0.30, 0.18, 21.0, CREOSOTE, segments=9)
        for ai, az in enumerate((19.4, 20.6)):
            make_box(f"Pole_{pi}_Arm_{ai}", (px + toward * 0.25, py, az), (0.16, 4.4, 0.18), CREOSOTE)
            for li in range(5):
                ly = -1.8 + li * 0.9
                make_cyl(f"Lamp_{pi}_{ai}_{li}", (px + toward * 0.62, py + ly, az + 0.32), 0.20, 0.22, LAMP, axis='X', segments=10)
                make_cyl(f"Lamp_{pi}_{ai}_{li}_Can", (px + toward * 0.48, py + ly, az + 0.32), 0.23, 0.12, (0.20, 0.20, 0.22, 1.0), axis='X', segments=10)


def build_scoreboard():
    """North, past the end zone, on two posts: HOME, VISITOR, the quarter
    and the clock in bulbs; a sponsor's board beneath. (Rewind: "they
    flashed R.I.P. on the scoreboard" — the CG has that moment.)"""
    sy = SCORE_Y                       # past the track's north curve
    for sx in (-3.0, 3.0):
        make_taper_cyl(f"Scoreboard_Post_{sx:+.0f}", (sx, sy + 0.3, 3.6), 0.20, 0.16, 7.2, CREOSOTE, segments=8)
    make_box("Scoreboard_Body", (0.0, sy, 6.6), (7.6, 0.40, 3.4), (0.07, 0.07, 0.08, 1.0))
    make_box("Scoreboard_Trim", (0.0, sy - 0.21, 8.25), (7.6, 0.04, 0.10), TRIM)
    for i, (lx, w, word) in enumerate(((-2.4, 2.2, "HOME"), (2.4, 2.2, "VISITOR"), (0.0, 1.6, "QTR"))):
        make_box(f"Scoreboard_Face_Label_{i}", (lx, sy - 0.21, 7.75 if word != "QTR" else 6.0), (w, 0.02, 0.34), (0.90, 0.88, 0.80, 1.0))
    for i, lx in enumerate((-2.9, -1.9, 1.9, 2.9, -0.5, 0.5, 0.0)):
        lz = 6.85 if i < 4 else (7.6 if i < 6 else 5.45)
        make_box(f"Scoreboard_Face_Digit_{i}", (lx, sy - 0.21, lz), (0.70, 0.02, 1.0 if i < 6 else 0.6), (0.96, 0.66, 0.24, 1.0))
    make_box("Scoreboard_Sponsor", (0.0, sy - 0.05, 4.4), (6.4, 0.10, 1.0), (0.86, 0.84, 0.78, 1.0))
    make_box("Scoreboard_Sponsor_Text", (0.0, sy - 0.11, 4.4), (5.4, 0.02, 0.5), (0.46, 0.14, 0.14, 1.0))


def build_concession():
    """The concession shed in the south-east corner, its window on the
    walk: coffee and cocoa on a cold Friday."""
    cx, cy = GS_X0 + 2.0, -8.5
    make_box("Concession", (cx, cy, 1.5), (6.0, 4.0, 3.0), (0.62, 0.60, 0.56, 1.0))
    make_rot_box("Concession_Roof", (cx, cy, 3.25), (6.8, 4.8, 0.18), ROOF, roll=0.08)
    make_box("Concession_Window", (cx, cy + 2.01, 1.55), (3.2, 0.02, 1.0), (0.96, 0.84, 0.58, 1.0))
    make_box("Concession_Counter", (cx, cy + 2.25, 1.02), (3.4, 0.5, 0.06), PAINT)
    make_rot_box("Concession_Awning", (cx, cy + 2.6, 2.75), (3.8, 1.3, 0.06), TRIM, roll=-0.30)
    make_box("Concession_Sign", (cx, cy + 2.03, 2.30), (3.0, 0.02, 0.40), PAINT)


def build_lot_and_street():
    """South of the gate: the gravel lot, the town's cars of 1997, the
    street, the church across it (the vigil), and the houses — the hit
    and run was "two blocks from the stadium"."""
    make_box("Lot_Gravel", (6.0, -30.0 + SOUTH, -0.035), (110.0, 26.0, 0.04), GRAVEL)
    cars = ((-30.0, -24.0, (0.46, 0.34, 0.20, 1.0), {"hatch": True}), (-24.0, -24.0, (0.30, 0.34, 0.40, 1.0), {}),
            (-18.0, -24.0, (0.62, 0.62, 0.60, 1.0), {"pickup": True}), (-12.0, -24.0, (0.38, 0.12, 0.12, 1.0), {}),
            (-6.0, -24.0, (0.16, 0.22, 0.18, 1.0), {"pickup": True}), (0.0, -24.0, (0.70, 0.68, 0.60, 1.0), {"hatch": True}),
            (30.0, -24.0, (0.20, 0.24, 0.36, 1.0), {}), (36.0, -24.0, (0.52, 0.48, 0.40, 1.0), {"pickup": True}),
            (-27.0, -36.0, (0.24, 0.24, 0.26, 1.0), {}), (-15.0, -36.0, (0.56, 0.20, 0.16, 1.0), {"pickup": True}),
            (3.0, -36.0, (0.40, 0.42, 0.30, 1.0), {"hatch": True}), (21.0, -36.0, (0.70, 0.70, 0.72, 1.0), {}),
            (39.0, -36.0, (0.30, 0.18, 0.12, 1.0), {"pickup": True}))
    for i, (x, y, col, kw) in enumerate(cars):
        make_car(f"LotCar_{i}", x, y + SOUTH, 4.7 if not kw.get("pickup") else 5.3, col, along="Y", **kw)
    make_box("Street", (0.0, -50.0 + SOUTH, -0.03), (300.0, 9.0, 0.03), ASPHALT)
    make_box("Street_Line", (0.0, -50.0 + SOUTH, -0.012), (300.0, 0.12, 0.01), (0.86, 0.74, 0.30, 1.0))
    for i in range(-6, 7):
        make_box(f"Streetlight_{i}_Pole", (i * 24.0, -45.0 + SOUTH, 3.6), (0.16, 0.16, 7.2), (0.40, 0.40, 0.42, 1.0))
        make_box(f"Streetlight_{i}_Head", (i * 24.0, -46.0 + SOUTH, 7.15), (0.30, 1.8, 0.18), (0.30, 0.30, 0.32, 1.0))
    # the church across the street: white clapboard, a gable roof, the steeple
    cx, cy = 14.0, -66.0 + SOUTH
    make_box("Church_Nave", (cx, cy - 8.0, 3.2), (11.0, 18.0, 6.4), PAINT)
    rp = math.atan2(3.6, 5.5)
    for sx in (-1, 1):
        make_rot_box(f"Church_Roof_{'E' if sx > 0 else 'W'}", (cx + sx * 2.85, cy - 8.0, 8.1), (6.6, 18.6, 0.20), (0.24, 0.24, 0.26, 1.0), pitch=sx * rp)
    make_box("Church_Tower", (cx, cy + 2.2, 6.5), (3.4, 3.4, 13.0), PAINT)
    make_box("Church_Belfry", (cx, cy + 2.2, 14.0), (2.8, 2.8, 2.0), (0.30, 0.28, 0.26, 1.0))
    make_taper_cyl("Church_Spire", (cx, cy + 2.2, 18.5), 2.0, 0.05, 7.0, (0.24, 0.24, 0.26, 1.0), segments=4)
    make_box("Church_Door", (cx, cy + 3.92, 1.3), (1.6, 0.04, 2.6), (0.36, 0.20, 0.14, 1.0))
    for k in range(4):
        for sx in (-1, 1):
            make_box(f"Church_Window_{'E' if sx > 0 else 'W'}_{k}", (cx + sx * 5.52, cy - 2.0 - k * 4.0, 3.4), (0.04, 1.2, 2.6), (0.92, 0.78, 0.48, 1.0))
    # houses along the street, two blocks of them
    r = _rng(42)
    for i, hx in enumerate((-70.0, -52.0, -34.0, -16.0, 36.0, 54.0, 72.0, 90.0)):
        w, d, h = 9.0 + r() * 3.0, 8.0 + r() * 3.0, 3.0 + r() * 2.6
        hy = -64.0 + SOUTH - d / 2.0
        col = COATS[int(r() * 10) % 10]
        body = (0.5 + col[0] * 0.5, 0.5 + col[1] * 0.5, 0.5 + col[2] * 0.5, 1.0)
        make_box(f"House_{i}", (hx, hy, h / 2.0), (w, d, h), body)
        for sx in (-1, 1):
            make_rot_box(f"House_{i}_Roof_{sx:+d}", (hx, hy + sx * d / 4.0, h + 0.9), (w + 0.6, d / 2.0 + 0.9, 0.16), (0.22, 0.20, 0.20, 1.0), roll=-sx * 0.42)
        make_box(f"House_{i}_Window", (hx - w / 4.0, hy + d / 2.0 + 0.01, 1.5), (1.6, 0.02, 1.1), (0.94, 0.80, 0.52, 1.0))


def build_firs():
    """The Coast Range comes down to the field on three sides: Douglas
    fir, 25-40 m, and the ridges behind them."""
    r = _rng(1998)
    k = 0
    for (x0, x1, y0, y1, n) in ((-150.0, 150.0, FENCE_N + 8.0, FENCE_N + 44.0, 46),
                                (-130.0, -(SIDE_X + VIS_D0 + 20.0), -30.0, FENCE_N + 8.0, 34),
                                (GS_XB + 10.0, 130.0, -30.0, FENCE_N + 8.0, 34),
                                (-150.0, 150.0, -134.0, -108.0, 30)):
        for _ in range(n):
            make_conifer(f"Fir_Stock_{k}", x0 + r() * (x1 - x0), y0 + r() * (y1 - y0), 24.0 + r() * 16.0, FIR, FIR_TRUNK, skirt=0.22)
            k += 1
    # (2026-10-30: the two N ridges 60 m further out — their footprints reached
    # the fir band and the overlap gate counted 454 trees inside them)
    for i, (hx, hy, rr, hh) in enumerate(((-220.0, 480.0, 260.0, 120.0), (160.0, 530.0, 300.0, 150.0),
                                          (-380.0, 200.0, 220.0, 110.0), (420.0, 160.0, 240.0, 120.0),
                                          (40.0, -430.0, 280.0, 110.0))):
        make_taper_cyl(f"Ridge_{i}", (hx, hy, hh / 2.0 - 4.0), rr, rr * 0.18, hh, (0.10, 0.17, 0.13, 1.0), segments=14)


def _rename(old, new):
    if bpy is None:
        return
    o = bpy.data.objects.get(old)
    if o is not None:
        o.name = new


def main():
    clear_scene()
    build_field()
    build_track()
    build_grandstand()
    SF._stands("Visit", -1, 8, 15.0, MID_Y, d0=VIS_D0)
    build_benches()
    build_rail_and_fence()
    build_light_poles()
    build_scoreboard()
    build_concession()
    build_lot_and_street()
    build_firs()
    build_crowd()
    build_practice()
    try:
        join_stock()
    except Exception as _e:
        print("[join_stock] skipped:", _e)
    # the night's people go with the night, the practice with the dusk
    for nm in ("CrowdHome", "CrowdAway", "TeamHome", "TeamAway", "PlayHome", "PlayAway", "Officials"):
        _rename(nm + "_Stock", nm + NIGHT)
    for nm in ("Practice", "PracticeCoach", "PracticeMay"):
        _rename(nm + "_Stock", nm + DUSK)
    out = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                        "../../../assets/3d/locales/small_wood_field.glb"))
    print(f"\n[build_small_wood_field] exporting to {out}")
    export_glb(out)


if __name__ == "__main__":
    main()
