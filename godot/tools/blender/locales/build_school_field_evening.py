"""Live Oak Field — the New Auburn high-school football field at
evening — vol6 hero locale (9 VN bg refs across vol6_ch13_two_a_days,
vol6_ch19_depthchart, vol6_ch19_chains, vol6_ch22_vinton,
vol6_ch10_night_shift).

Music manifest binds vol6_live_oak_field ("Live Oak Field ·
Two-A-Days") to ch13 + ch14 — desc: "Cleat on Bermuda grass +
cicadas at 6:15 AM + a far whistle's three short bursts." The field
is NAMED for the live oak: one hero oak stands off the east straight
of the track.

Canon baked in (chapter JSON : node):
  · vol6_ch13_two_a_days:6-8 — Coach K's white Ford F-250 with the
    camper shell, the ladder rack, and the TAPE JOB on the
    driver's-side mirror, parked at the head of the lot, the spot
    closest to the field gate. Equipment cart with cones, the rope
    ladder, the canvas bag of mouthguards.
  · vol6_ch13_two_a_days:20/22/133-134 — Brent's immaculate black
    F-150, Tucker's Tacoma, Ben's Civic four spaces down.
  · vol6_ch13_two_a_days:28 — the asphalt road that runs the
    PERIMETER of the school grounds; the gap in the fence behind
    the field house. :79/:87 the field gate. :88 "Cones. Three
    lines." :115 Brent finds Ben at the COOLER (sideline).
  · vol6_ch19_depthchart:6 — "the back stretch of the SYNTHETIC
    TRACK at six oh-eight AM" (three easy miles). :67-76 the
    CORKBOARD outside the field-house door with the depth-chart
    sheet. :117 the EQUIPMENT SHED at the back of the school field
    with the small lot behind it.
  · vol6_ch22_vinton:32/:46 — the home BLEACHERS; Eileen's folding
    chair, THE ONLY folding chair in the third row, behind the home
    bench; the thermos set on the bench at her right. :55 home
    bleachers draw 120-150 (small-town scale — 5 rows, not a
    stadium). :28 the two coaches meet at the fifty. :68 goalposts
    + scoreboard implied (missed PAT, 0-7, "the home crowd is
    quiet"). Visiting bench opposite.
  · vol6_ch19_chains:72-84 — the 6 PM walk-through: the field in
    evening light, Coach K at the bench.

Canon-negative: no press box, no concession stand (never in prose —
a Texas scrimmage field, not a stadium).

Camera preset (Background3D.gd): (0, 2.30, +0.5) / yaw 180 / fov 60
— same convention as every scaffold: content lives at Blender y >= 0,
camera stands just inside the SOUTH GOAL LINE looking north down the
length of the field. Yard lines march away in depth; north goalpost,
scoreboard and school massing hold the horizon; home bleachers +
lot left, the live oak right.

Exterior discipline (playbook 2026-06-14): continuous GROUND first,
then circulation (perimeter road, parking lot, walks, the track),
THEN features. Chain-link is post-and-rail with EMPTY openings (no
transparency). Field markings are thin overlay slabs lifted ABOVE
the grass slab top. Diagonals (oak limbs, aisle handrail) use a
local make_tube — never stair-stepped boxes. Track curves are single
chorded arc-slab meshes, winding per build_harmony_terrain's
_emit_raised_sidewalk convention (top face CCW seen from +Z).
"""
import os, sys, math
_BT = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
if _BT not in sys.path: sys.path.insert(0, _BT)
from _props.geometry import clear_scene, make_box, make_cyl, export_glb, _finalize_mesh

# ── Layout constants (Blender Z-up, 1 unit = 1 m) ─────────────────
FIELD_HW  = 24.4            # field half-width (160 ft)
YD        = 0.9144
GL_S      = -5.0            # south goal line (camera stands just inside it)
GL_N      = GL_S + 100 * YD             # 86.44 — north goal line
EL_S      = GL_S - 10 * YD              # -14.14 — south end line
EL_N      = GL_N + 10 * YD              # 95.58 — north end line
MID_Y     = (GL_S + GL_N) / 2.0         # 40.72 — the fifty
HASH_X    = 8.13            # HS hash marks: field thirds (53'4" apart)

FIELD_TOP = 0.08            # crowned Bermuda slab top
TRACK_TOP = 0.06
LOT_TOP   = 0.04

TRK_R_IN  = 33.5            # track inner edge radius / straight inset
TRK_LANES = 6
TRK_LANE_W = 1.22
TRK_W     = TRK_LANES * TRK_LANE_W      # 7.32
TRK_R_OUT = TRK_R_IN + TRK_W            # 40.82
TRK_CY_S  = 8.0             # curve centers (field corners clear R_IN)
TRK_CY_N  = 73.44

FENCE_X   = 52.0            # field-complex chain-link ring
FENCE_Y_S = -36.0
FENCE_Y_N = 121.0
GATE_Y0, GATE_Y1 = 60.2, 63.8           # the field gate (west run)

LOT_X0, LOT_X1 = -80.0, -54.0           # parking lot, west of the fence
LOT_Y0, LOT_Y1 = 64.0, 104.0
STALL_P   = 2.8             # stall pitch; head spot = southernmost
HEAD_Y    = 67.8            # Coach K's spot, closest to the field gate

ROAD_W_X0, ROAD_W_X1 = -88.0, -81.0     # perimeter road, west run
ROAD_E_X0, ROAD_E_X1 = 81.0, 88.0
ROAD_N_Y0, ROAD_N_Y1 = 142.0, 149.0

# ── Palette (Gulf Coast Texas, mid-August; vertex colors only) ────
COL_GROUND    = (0.40, 0.42, 0.24, 1.0)   # dry August ground / rough
COL_SCRUB     = (0.50, 0.47, 0.28, 1.0)   # scorched scrub patches
COL_BERMUDA   = (0.30, 0.44, 0.20, 1.0)   # the playing surface
COL_MOW_LT    = (0.34, 0.48, 0.22, 1.0)   # alternate mowing bands
COL_EZ_GREEN  = (0.24, 0.38, 0.20, 1.0)   # end zones, deeper green
COL_WORN      = (0.47, 0.44, 0.26, 1.0)   # two-a-days cleat wear
COL_PAINT     = (0.93, 0.93, 0.88, 1.0)   # field paint
COL_TRACK     = (0.60, 0.29, 0.24, 1.0)   # synthetic rust-red
COL_ASPHALT   = (0.24, 0.24, 0.25, 1.0)
COL_ASPH_WEAR = (0.20, 0.20, 0.21, 1.0)
COL_CONCRETE  = (0.66, 0.64, 0.58, 1.0)
COL_DITCH     = (0.31, 0.30, 0.19, 1.0)   # damp drainage ditch
COL_TANNIN    = (0.29, 0.25, 0.15, 1.0)   # standing tannin water
COL_ALUM      = (0.72, 0.74, 0.76, 1.0)   # bleacher aluminum
COL_ALUM_DK   = (0.52, 0.54, 0.56, 1.0)
COL_GALV      = (0.56, 0.58, 0.60, 1.0)   # chain-link galvanized
COL_STEEL_DK  = (0.30, 0.31, 0.33, 1.0)
COL_GP_YELLOW = (0.92, 0.76, 0.18, 1.0)   # goalpost safety yellow
COL_GP_PAD    = (0.20, 0.26, 0.42, 1.0)
COL_SCORE_GRN = (0.10, 0.24, 0.15, 1.0)   # scoreboard cabinet
COL_SCORE_FACE= (0.06, 0.07, 0.08, 1.0)
COL_SCORE_LMP = (0.80, 0.56, 0.20, 1.0)   # unlit amber digit fields
COL_BLOCK     = (0.72, 0.70, 0.62, 1.0)   # field-house cinderblock
COL_METAL_RF  = (0.60, 0.62, 0.62, 1.0)
COL_DOOR_STL  = (0.36, 0.42, 0.40, 1.0)
COL_CORK      = (0.55, 0.40, 0.24, 1.0)
COL_PAPER     = (0.92, 0.90, 0.84, 1.0)
COL_BRICK     = (0.55, 0.36, 0.28, 1.0)   # the school, far massing
COL_BRICK_2   = (0.50, 0.33, 0.27, 1.0)
COL_GLASS_DK  = (0.15, 0.17, 0.21, 1.0)
COL_TRUNK     = (0.34, 0.26, 0.19, 1.0)
COL_OAK_A     = (0.26, 0.37, 0.21, 1.0)   # live-oak canopy lobes
COL_OAK_B     = (0.22, 0.32, 0.18, 1.0)
COL_PINE      = (0.19, 0.30, 0.19, 1.0)
COL_CONE_OR   = (0.90, 0.42, 0.10, 1.0)
COL_COOLER_OR = (0.92, 0.44, 0.12, 1.0)
COL_WHITE     = (0.92, 0.92, 0.90, 1.0)
COL_F250      = (0.90, 0.90, 0.88, 1.0)   # Coach K's white F-250
COL_SHELL     = (0.84, 0.84, 0.81, 1.0)   # the camper shell
COL_F150      = (0.10, 0.10, 0.11, 1.0)   # Brent's, immaculate
COL_TACOMA    = (0.42, 0.26, 0.22, 1.0)   # Tucker's
COL_CIVIC     = (0.60, 0.63, 0.67, 1.0)   # Ben's
COL_TIRE      = (0.10, 0.10, 0.10, 1.0)
COL_TAPE      = (0.62, 0.60, 0.55, 1.0)   # the mirror tape job
COL_CHAIR_GRN = (0.20, 0.32, 0.24, 1.0)   # Eileen's folding chair
COL_THERMOS   = (0.68, 0.16, 0.14, 1.0)   # the lemon-water thermos
COL_CANVAS    = (0.48, 0.44, 0.32, 1.0)   # mouthguard bag
COL_ROPE      = (0.72, 0.62, 0.42, 1.0)


# ── Local helpers (arbitrary-orientation tube + arc slab) ─────────
def make_tube(name, p0, p1, radius, color, segments=8):
    """Cylinder between two arbitrary points — the playbook's
    make_tube_segment. Winding mirrors make_cyl (right-handed basis
    e1, e2, axis)."""
    dx, dy, dz = p1[0] - p0[0], p1[1] - p0[1], p1[2] - p0[2]
    L = math.sqrt(dx * dx + dy * dy + dz * dz)
    if L < 1e-9:
        return None
    wx, wy, wz = dx / L, dy / L, dz / L
    # e1 = normalize(w x Z-hat) unless near-parallel, then w x X-hat
    cx_, cy_, cz_ = wy * 1.0 - wz * 0.0, wz * 0.0 - wx * 1.0, wx * 0.0 - wy * 0.0
    m = math.sqrt(cx_ * cx_ + cy_ * cy_ + cz_ * cz_)
    if m < 1e-6:
        cx_, cy_, cz_ = 0.0, wz, -wy      # w x X-hat
        m = math.sqrt(cx_ * cx_ + cy_ * cy_ + cz_ * cz_)
    e1 = (cx_ / m, cy_ / m, cz_ / m)
    e2 = (wy * e1[2] - wz * e1[1], wz * e1[0] - wx * e1[2],
          wx * e1[1] - wy * e1[0])        # w x e1
    verts = []
    for base in (p0, p1):
        for i in range(segments):
            a = 2.0 * math.pi * i / segments
            ca, sa = math.cos(a) * radius, math.sin(a) * radius
            verts.append((base[0] + ca * e1[0] + sa * e2[0],
                          base[1] + ca * e1[1] + sa * e2[1],
                          base[2] + ca * e1[2] + sa * e2[2]))
    faces = []
    for i in range(segments):
        ni = (i + 1) % segments
        faces.append([i, ni, ni + segments, i + segments])
    faces.append(list(reversed(range(segments))))
    faces.append(list(range(segments, segments * 2)))
    return _finalize_mesh(name, verts, faces, color)


def make_arc_slab(name, cx, cy, r_in, r_out, a0, a1, z0, z1, color,
                  segments=20):
    """One solid ring-band mesh between angles a0->a1 (radians,
    increasing = CCW from +Z, so top faces wind CCW seen from above
    — same convention as harmony_terrain's raised sidewalks)."""
    verts = []
    for i in range(segments + 1):
        a = a0 + (a1 - a0) * i / segments
        ca, sa = math.cos(a), math.sin(a)
        verts.append((cx + ca * r_in,  cy + sa * r_in,  z0))   # 4i   in-bot
        verts.append((cx + ca * r_out, cy + sa * r_out, z0))   # 4i+1 out-bot
        verts.append((cx + ca * r_in,  cy + sa * r_in,  z1))   # 4i+2 in-top
        verts.append((cx + ca * r_out, cy + sa * r_out, z1))   # 4i+3 out-top
    faces = []
    for i in range(segments):
        b, n = 4 * i, 4 * (i + 1)
        faces.append([b + 2, b + 3, n + 3, n + 2])   # top (CCW from +Z)
        faces.append([b + 1, b + 0, n + 0, n + 1])   # bottom
        faces.append([b + 0, b + 2, n + 2, n + 0])   # inner wall
        faces.append([b + 3, b + 1, n + 1, n + 3])   # outer wall
    faces.append([0, 1, 3, 2])                                        # end cap a0
    e = 4 * segments
    faces.append([e + 2, e + 3, e + 1, e + 0])                        # end cap a1
    return _finalize_mesh(name, verts, faces, color)


# ══════════════════════════════════════════════════════════════════
# GROUND — one continuous plane under the ENTIRE world (playbook
# 2026-06-14: ground first, or the locale is floating islands).
# Top at z = 0. Dry-August scrub variation outside the track.
# ══════════════════════════════════════════════════════════════════
def build_ground():
    make_box("Ground", (0.0, 55.0, -0.06), (250.0, 240.0, 0.12), COL_GROUND)
    # Scorched scrub patches in the rough (deterministic hand-baked)
    patches = [(-46.0, 8.0, 9.0, 6.0), (47.0, 20.0, 7.0, 5.0),
               (-64.0, 30.0, 10.0, 7.0), (60.0, 86.0, 8.0, 6.0),
               (-46.0, 112.0, 7.0, 5.0), (20.0, 118.0, 9.0, 5.0),
               (66.0, 46.0, 6.0, 8.0), (-70.0, 120.0, 8.0, 6.0)]
    for i, (px, py, pw, pl) in enumerate(patches):
        make_box(f"Scrub_{i}", (px, py, 0.003), (pw, pl, 0.006), COL_SCRUB)


# ══════════════════════════════════════════════════════════════════
# CIRCULATION — the perimeter asphalt road (ch13:28 — the team runs
# three loops of it), the parking lot with striped stalls, driveway
# apron, drainage ditches (bayou-country water table), concrete
# walks. Roads BEFORE features.
# ══════════════════════════════════════════════════════════════════
def build_roads_and_lot():
    rw_cx = (ROAD_W_X0 + ROAD_W_X1) / 2.0
    re_cx = (ROAD_E_X0 + ROAD_E_X1) / 2.0
    rn_cy = (ROAD_N_Y0 + ROAD_N_Y1) / 2.0
    make_box("Road_W", (rw_cx, 55.0, 0.02), (7.0, 190.0, 0.04), COL_ASPHALT)
    make_box("Road_E", (re_cx, 55.0, 0.02), (7.0, 190.0, 0.04), COL_ASPHALT)
    make_box("Road_N", (0.0, rn_cy, 0.02), (176.0, 7.0, 0.04), COL_ASPHALT)
    # Asphalt wear splotches (bayou roads are not pristine)
    wear = [(rw_cx + 1.0, 18.0, 3.0, 5.0), (rw_cx - 1.2, 84.0, 2.5, 4.0),
            (re_cx, 60.0, 3.0, 6.0), (-30.0, rn_cy, 6.0, 3.0)]
    for i, (px, py, pw, pl) in enumerate(wear):
        make_box(f"Road_Wear_{i}", (px, py, 0.045), (pw, pl, 0.006), COL_ASPH_WEAR)
    # Drainage ditches alongside the roads — darker damp strips with
    # patches of standing tannin water (high water table)
    make_box("Ditch_W", (ROAD_W_X1 + 1.2, 30.0, 0.004), (2.0, 130.0, 0.008), COL_DITCH)
    make_box("Ditch_E", (ROAD_E_X0 - 1.2, 55.0, 0.004), (2.0, 170.0, 0.008), COL_DITCH)
    for i, (px, py) in enumerate([(ROAD_W_X1 + 1.2, 12.0), (ROAD_W_X1 + 1.2, 52.0),
                                   (ROAD_E_X0 - 1.2, 78.0)]):
        make_box(f"Ditch_Water_{i}", (px, py, 0.009), (1.4, 5.0, 0.006), COL_TANNIN)
    # THE PARKING LOT (ch13:5-6) west of the field fence
    lot_cx = (LOT_X0 + LOT_X1) / 2.0
    lot_cy = (LOT_Y0 + LOT_Y1) / 2.0
    make_box("Lot_Slab", (lot_cx, lot_cy, 0.02),
             (LOT_X1 - LOT_X0, LOT_Y1 - LOT_Y0, 0.04), COL_ASPHALT)
    make_box("Lot_Apron", (-82.5, 69.0, 0.02), (5.0, 8.0, 0.04), COL_ASPHALT)
    # Stall stripes along the east edge — noses toward the fence /
    # field gate; the head (southernmost) stripe pair is Coach K's
    for k in range(13):
        sy = HEAD_Y - STALL_P / 2.0 + k * STALL_P
        make_box(f"Lot_Stripe_{k}", (-57.0, sy, 0.044), (5.6, 0.10, 0.008), COL_WHITE)
    # Concrete pad: field gate landing + spur to the lot corner
    make_box("Walk_Gate", (-53.4, 62.0, 0.025), (5.2, 3.4, 0.05), COL_CONCRETE)
    make_box("Walk_GateSpur", (-47.6, 62.0, 0.025), (6.4, 1.8, 0.05), COL_CONCRETE)
    # Walk from the lot to the field-house door (corkboard ritual)
    make_box("Walk_FieldHouse", (-65.6, 90.0, 0.025), (2.0, 7.0, 0.05), COL_CONCRETE)


# ══════════════════════════════════════════════════════════════════
# THE SYNTHETIC TRACK (ch19_depthchart:6 — "the back stretch of the
# synthetic track at six oh-eight AM"). Six lanes, rust-red. Two
# straight slabs + two single-mesh chorded arc bands. Lane lines on
# the straights, lifted above the surface.
# ══════════════════════════════════════════════════════════════════
def build_track():
    straight_len = TRK_CY_N - TRK_CY_S
    for sgn, seg in ((-1, "W"), (+1, "E")):
        make_box(f"Track_Straight_{seg}",
                 (sgn * (TRK_R_IN + TRK_W / 2.0), MID_Y, TRACK_TOP / 2.0),
                 (TRK_W, straight_len, TRACK_TOP), COL_TRACK)
    make_arc_slab("Track_Curve_S", 0.0, TRK_CY_S, TRK_R_IN, TRK_R_OUT,
                  math.pi, 2.0 * math.pi, 0.0, TRACK_TOP, COL_TRACK, segments=22)
    make_arc_slab("Track_Curve_N", 0.0, TRK_CY_N, TRK_R_IN, TRK_R_OUT,
                  0.0, math.pi, 0.0, TRACK_TOP, COL_TRACK, segments=22)
    # Lane lines on the straights (5 dividers for 6 lanes)
    for li in range(1, TRK_LANES):
        lx = TRK_R_IN + li * TRK_LANE_W
        for sgn, seg in ((-1, "W"), (+1, "E")):
            make_box(f"Track_Lane_{seg}_{li}", (sgn * lx, MID_Y, TRACK_TOP + 0.005),
                     (0.05, straight_len, 0.010), COL_WHITE)
    # Inner + outer white edge lines on the straights
    for sgn, seg in ((-1, "W"), (+1, "E")):
        make_box(f"Track_Edge_In_{seg}", (sgn * TRK_R_IN, MID_Y, TRACK_TOP + 0.005),
                 (0.06, straight_len, 0.010), COL_WHITE)
        make_box(f"Track_Edge_Out_{seg}", (sgn * TRK_R_OUT, MID_Y, TRACK_TOP + 0.005),
                 (0.06, straight_len, 0.010), COL_WHITE)


# ══════════════════════════════════════════════════════════════════
# THE FIELD — crowned Bermuda slab, mowing bands, end zones, yard
# lines every 5, hash dashes every yard (HS thirds), two-a-days
# wear between the hashes ("Cleat on Bermuda grass"). All markings
# are thin slabs ABOVE the grass top (playbook: lines never buried).
# ══════════════════════════════════════════════════════════════════
def build_field():
    f_len = EL_N - EL_S
    make_box("Field_Grass", (0.0, MID_Y, FIELD_TOP / 2.0),
             (FIELD_HW * 2.0, f_len, FIELD_TOP), COL_BERMUDA)
    # Alternate mowing bands, goal line to goal line, every 10 yd
    for k in range(0, 10, 2):
        by = GL_S + (k + 0.5) * 10 * YD
        make_box(f"Field_Mow_{k}", (0.0, by, FIELD_TOP + 0.002),
                 (FIELD_HW * 2.0, 10 * YD, 0.004), COL_MOW_LT)
    # End zones a deeper green
    make_box("Field_EZ_S", (0.0, (EL_S + GL_S) / 2.0, FIELD_TOP + 0.003),
             (FIELD_HW * 2.0, 10 * YD, 0.005), COL_EZ_GREEN)
    make_box("Field_EZ_N", (0.0, (GL_N + EL_N) / 2.0, FIELD_TOP + 0.003),
             (FIELD_HW * 2.0, 10 * YD, 0.005), COL_EZ_GREEN)
    # Cleat wear between the hashes — three weeks of two-a-days
    worn = [(0.0, 22.0, 13.0, 5.0), (-2.0, 32.0, 11.0, 4.5),
            (1.5, MID_Y, 14.0, 6.0), (-1.0, 50.0, 12.0, 5.0),
            (2.0, 60.0, 10.0, 4.0), (0.0, 70.5, 9.0, 4.0)]
    for i, (px, py, pw, pl) in enumerate(worn):
        make_box(f"Field_Worn_{i}", (px, py, FIELD_TOP + 0.006),
                 (pw, pl, 0.005), COL_WORN)
    # Yard lines every 5 yards, goal line to goal line (21 lines)
    for i in range(21):
        ly = GL_S + i * 5 * YD
        make_box(f"Field_YL_{i}", (0.0, ly, FIELD_TOP + 0.008),
                 (FIELD_HW * 2.0, 0.10, 0.012), COL_PAINT)
    # Sidelines (full length incl. end zones) + end lines
    for sgn, seg in ((-1, "W"), (+1, "E")):
        make_box(f"Field_Sideline_{seg}", (sgn * FIELD_HW, MID_Y, FIELD_TOP + 0.008),
                 (0.30, f_len, 0.012), COL_PAINT)
    make_box("Field_EndLine_S", (0.0, EL_S, FIELD_TOP + 0.008),
             (FIELD_HW * 2.0 + 0.3, 0.30, 0.012), COL_PAINT)
    make_box("Field_EndLine_N", (0.0, EL_N, FIELD_TOP + 0.008),
             (FIELD_HW * 2.0 + 0.3, 0.30, 0.012), COL_PAINT)
    # Hash dashes at every yard between the fives, both hash rows
    for j in range(1, 100):
        if j % 5 == 0:
            continue
        hy = GL_S + j * YD
        for sgn, seg in ((-1, "W"), (+1, "E")):
            make_box(f"Field_Hash_{seg}_{j}", (sgn * HASH_X, hy, FIELD_TOP + 0.008),
                     (0.60, 0.10, 0.012), COL_PAINT)


# ══════════════════════════════════════════════════════════════════
# GOALPOSTS — gooseneck yellow, HS width (23'4"), crossbar 10 ft,
# uprights 20 ft above. Wrapped base pads. One per end line; the
# missed Vinton PAT sailed past the north one (ch22:68).
# ══════════════════════════════════════════════════════════════════
def _goalpost(prefix, el_y, back_sign):
    """back_sign: +1 = base pole sits north of the end line."""
    base_y = el_y + back_sign * 1.32
    make_cyl(f"{prefix}_Base", (0.0, base_y, 1.45), 0.14, 2.9, COL_GP_YELLOW,
             segments=10)
    make_cyl(f"{prefix}_Pad", (0.0, base_y, 0.95), 0.32, 1.9, COL_GP_PAD,
             segments=10)
    make_cyl(f"{prefix}_Arm", (0.0, (base_y + el_y) / 2.0, 2.72), 0.10, 1.32,
             COL_GP_YELLOW, axis='Y')
    make_cyl(f"{prefix}_Riser", (0.0, el_y, 2.85), 0.10, 0.42, COL_GP_YELLOW)
    make_cyl(f"{prefix}_Crossbar", (0.0, el_y, 3.05), 0.09, 7.11, COL_GP_YELLOW,
             axis='X')
    for sgn, seg in ((-1, "W"), (+1, "E")):
        make_cyl(f"{prefix}_Upright_{seg}", (sgn * 3.555, el_y, 6.10), 0.065, 6.10,
                 COL_GP_YELLOW, segments=10)

def build_goalposts():
    _goalpost("GP_N", EL_N, +1)
    _goalpost("GP_S", EL_S, -1)      # behind camera; completeness


# ══════════════════════════════════════════════════════════════════
# BLEACHERS — small-town aluminum. Home stand west (5 rows, seats
# ~150, ch22:55), visitor stand east (3 rows). Eileen's folding
# chair — THE ONLY folding chair — in the third row north of the
# aisle, thermos on the bench at her right (ch22:32/:46).
# ══════════════════════════════════════════════════════════════════
def _bleachers(prefix, front_x, face_sign, y0, y1, rows):
    """face_sign +1 -> stand faces +X (home stand on the west)."""
    yc = (y0 + y1) / 2.0
    length = y1 - y0
    for r in range(rows):
        seat_x = front_x - face_sign * (0.55 + r * 0.80)
        foot_x = front_x - face_sign * (0.10 + r * 0.80)
        make_box(f"{prefix}_Seat_{r}", (seat_x, yc, 0.46 + r * 0.40),
                 (0.28, length, 0.05), COL_ALUM)
        make_box(f"{prefix}_Foot_{r}", (foot_x, yc, 0.155 + r * 0.40),
                 (0.52, length, 0.03), COL_ALUM)
    depth = rows * 0.80 + 0.5
    n_frames = 5 if rows >= 5 else 4
    for fi in range(n_frames):
        fy = y0 + 0.6 + (length - 1.2) * fi / (n_frames - 1)
        make_box(f"{prefix}_Frame_Base_{fi}",
                 (front_x - face_sign * depth / 2.0, fy, 0.06),
                 (depth, 0.09, 0.12), COL_ALUM_DK)
        for r in range(rows):
            px = front_x - face_sign * (0.45 + r * 0.80)
            ph = 0.38 + r * 0.40
            make_box(f"{prefix}_Frame_Post_{fi}_{r}", (px, fy, ph / 2.0),
                     (0.08, 0.08, ph), COL_ALUM_DK)
    # Guard rails: back run + both ends
    back_x = front_x - face_sign * (rows * 0.80 + 0.35)
    top_z = 0.46 + (rows - 1) * 0.40
    make_box(f"{prefix}_Rail_Back", (back_x, yc, top_z + 0.95),
             (0.06, length, 0.07), COL_GALV)
    for pi in range(4):
        py = y0 + length * pi / 3.0
        make_box(f"{prefix}_Rail_BackPost_{pi}", (back_x, py, top_z + 0.50),
                 (0.05, 0.05, 0.95), COL_GALV)
    for sgn, seg in ((-1, "S"), (+1, "N")):
        ey = yc + sgn * (length / 2.0 - 0.03)
        make_box(f"{prefix}_Rail_End_{seg}",
                 (front_x - face_sign * depth / 2.0, ey, top_z + 0.95),
                 (depth, 0.06, 0.07), COL_GALV)
        make_box(f"{prefix}_Rail_EndPost_{seg}",
                 (front_x - face_sign * 0.3, ey, top_z / 2.0 + 0.60),
                 (0.05, 0.05, top_z + 1.2), COL_GALV)

def build_bleachers():
    _bleachers("BlH", -43.0, +1, 26.0, 56.0, 5)     # home, west
    _bleachers("BlV", +43.0, -1, 26.0, 41.0, 3)     # visitors, east
    # Center-aisle handrail on the home stand (sloped: make_tube)
    make_tube("BlH_Aisle_Rail", (-43.2, 41.0, 0.95), (-46.6, 41.0, 2.65),
              0.03, COL_GALV)
    make_cyl("BlH_Aisle_RailPost_0", (-43.2, 41.0, 0.55), 0.03, 0.80, COL_GALV)
    make_cyl("BlH_Aisle_RailPost_1", (-46.6, 41.0, 2.15), 0.03, 1.00, COL_GALV)
    # EILEEN'S FOLDING CHAIR — third row (r=2 deck), the only one
    cxx, cyy = -44.70, 42.6            # on the row-2 footboard, N of aisle
    deck_z = 0.155 + 2 * 0.40 + 0.015  # row-2 footboard top
    for li, (sx, sy) in enumerate([(-1, -1), (+1, -1), (-1, +1), (+1, +1)]):
        make_box(f"Chair_Leg_{li}", (cxx + sx * 0.18, cyy + sy * 0.17, deck_z + 0.21),
                 (0.03, 0.03, 0.42), COL_STEEL_DK)
    make_box("Chair_Seat", (cxx, cyy, deck_z + 0.44), (0.44, 0.42, 0.035), COL_CHAIR_GRN)
    make_box("Chair_Back", (cxx - 0.21, cyy, deck_z + 0.72), (0.035, 0.44, 0.50),
             COL_CHAIR_GRN)
    # The thermos of lemon-water, on the bench at her right (ch22:46)
    # — she faces the field (east), so her right is south (-Y).
    seat2_z = 0.46 + 2 * 0.40 + 0.025  # row-2 seat plank top (1.285)
    make_cyl("Thermos", (-45.15, 41.7, seat2_z + 0.13), 0.055, 0.26,
             COL_THERMOS, segments=10)
    make_cyl("Thermos_Cap", (-45.15, 41.7, seat2_z + 0.285), 0.045, 0.05,
             COL_WHITE, segments=10)


# ══════════════════════════════════════════════════════════════════
# SIDELINE — home + visiting benches on the aprons, the water
# cooler Brent finds Ben at (ch13:115), the cone lines (ch13:88
# "Cones. Three lines."), the equipment cart at the field gate with
# cones / rope ladder / the canvas bag of mouthguards (ch13:8).
# ══════════════════════════════════════════════════════════════════
def _team_bench(prefix, bx, y0, y1):
    yc = (y0 + y1) / 2.0
    make_box(f"{prefix}_Seat", (bx, yc, 0.47), (0.32, y1 - y0, 0.06), COL_ALUM)
    for pi in range(3):
        py = y0 + (y1 - y0) * pi / 2.0
        make_box(f"{prefix}_Leg_{pi}", (bx, py, 0.22), (0.28, 0.08, 0.44), COL_ALUM_DK)

def _cone(prefix, x, y, z0):
    make_cyl(f"{prefix}_Base", (x, y, z0 + 0.02), 0.16, 0.04, COL_CONE_OR, segments=10)
    make_cyl(f"{prefix}_Body", (x, y, z0 + 0.25), 0.075, 0.42, COL_CONE_OR, segments=10)
    make_cyl(f"{prefix}_Band", (x, y, z0 + 0.28), 0.078, 0.07, COL_WHITE, segments=10)

def build_sideline():
    _team_bench("BenchH_0", -29.0, 31.0, 39.0)
    _team_bench("BenchH_1", -29.0, 43.0, 51.0)
    _team_bench("BenchV_0", +29.0, 34.0, 46.0)
    # The cooler on its stand between the home benches
    make_box("Cooler_Stand", (-29.0, 41.0, 0.38), (0.7, 0.7, 0.76), COL_STEEL_DK)
    make_cyl("Cooler_Body", (-29.0, 41.0, 1.05), 0.24, 0.56, COL_COOLER_OR, segments=12)
    make_cyl("Cooler_Lid", (-29.0, 41.0, 1.36), 0.25, 0.07, COL_WHITE, segments=12)
    make_box("Cooler_Spigot", (-28.72, 41.0, 0.84), (0.08, 0.05, 0.06), COL_WHITE)
    make_cyl("Cooler_Cups", (-28.75, 40.78, 0.895), 0.045, 0.26, COL_WHITE, segments=8)
    make_cyl("Cooler_Cup_Dropped", (-28.3, 42.1, 0.115), 0.04, 0.07, COL_WHITE,
             segments=8)
    # Cones. Three lines. (west numbers area, set for the morning)
    for line_i, lx in enumerate((-12.0, -15.0, -18.0)):
        for j in range(4):
            _cone(f"Cone_L{line_i}_{j}", lx, 18.0 + j * 2.5, FIELD_TOP)
    # The equipment cart, parked inside the field gate
    ccx, ccy = -46.5, 58.0
    make_box("Cart_Tray", (ccx, ccy, 0.42), (1.30, 0.80, 0.10), COL_STEEL_DK)
    make_box("Cart_Lip", (ccx, ccy, 0.52), (1.34, 0.84, 0.05), COL_ALUM_DK)
    for wi, (sx, sy) in enumerate([(-1, -1), (+1, -1), (-1, +1), (+1, +1)]):
        make_cyl(f"Cart_Wheel_{wi}", (ccx + sx * 0.52, ccy + sy * 0.30, 0.12),
                 0.12, 0.08, COL_TIRE, axis='Y', segments=10)
    make_cyl("Cart_Handle_Post_0", (ccx - 0.62, ccy - 0.30, 0.80), 0.02, 0.70, COL_GALV)
    make_cyl("Cart_Handle_Post_1", (ccx - 0.62, ccy + 0.30, 0.80), 0.02, 0.70, COL_GALV)
    make_cyl("Cart_Handle_Bar", (ccx - 0.62, ccy, 1.15), 0.02, 0.64, COL_GALV, axis='Y')
    # Cone stack + rope-ladder coil + the canvas mouthguard bag
    for si in range(3):
        make_cyl(f"Cart_ConeStack_{si}", (ccx + 0.35, ccy - 0.15, 0.60 + si * 0.10),
                 0.14 - si * 0.02, 0.10, COL_CONE_OR, segments=10)
    make_box("Cart_RopeLadder", (ccx - 0.20, ccy + 0.15, 0.585), (0.50, 0.40, 0.12),
             COL_ROPE)
    for ri in range(3):
        make_box(f"Cart_Ladder_Rung_{ri}", (ccx - 0.36 + ri * 0.16, ccy + 0.15, 0.65),
                 (0.05, 0.42, 0.02), COL_STEEL_DK)
    make_box("Cart_CanvasBag", (ccx + 0.30, ccy + 0.22, 0.60), (0.45, 0.30, 0.24),
             COL_CANVAS)


# ══════════════════════════════════════════════════════════════════
# CHAIN-LINK — perimeter ring around the field complex plus the
# lot's road-side run. Post-and-rail with EMPTY openings (playbook
# no-transparency). THE FIELD GATE in the west run (ch13:79); the
# gap behind the field house in the lot run (ch13:28).
# ══════════════════════════════════════════════════════════════════
def _fence_run(prefix, axis, fixed, a0, a1, gaps=()):
    """axis 'Y': run along Y at x=fixed. axis 'X': along X at y=fixed.
    gaps: list of (g0, g1) openings subtracted from the run."""
    segs, cur = [], a0
    for g0, g1 in sorted(gaps):
        if g0 > cur:
            segs.append((cur, g0))
        cur = max(cur, g1)
    if cur < a1:
        segs.append((cur, a1))
    pk = 0
    for si, (s0, s1) in enumerate(segs):
        length = s1 - s0
        n = max(2, int(round(length / 5.0)) + 1)
        for i in range(n):
            a = s0 + length * i / (n - 1)
            pos = (fixed, a, 1.20) if axis == 'Y' else (a, fixed, 1.20)
            make_cyl(f"{prefix}_Post_{pk}", pos, 0.045, 2.40, COL_GALV)
            pk += 1
        mid = (s0 + s1) / 2.0
        for rz, rn in ((2.32, "Top"), (0.25, "Bot")):
            pos = (fixed, mid, rz) if axis == 'Y' else (mid, fixed, rz)
            make_cyl(f"{prefix}_Rail{rn}_{si}", pos, 0.028, length, COL_GALV,
                     axis=axis)

def build_fence_and_gates():
    _fence_run("FenceW", 'Y', -FENCE_X, FENCE_Y_S, FENCE_Y_N,
               gaps=[(GATE_Y0, GATE_Y1)])
    _fence_run("FenceE", 'Y', +FENCE_X, FENCE_Y_S, FENCE_Y_N)
    _fence_run("FenceN", 'X', FENCE_Y_N, -FENCE_X, FENCE_X)
    _fence_run("FenceS", 'X', FENCE_Y_S, -FENCE_X, FENCE_X)
    # Lot road-side run with the runners' gap behind the field house
    _fence_run("FenceLot", 'Y', LOT_X0, LOT_Y0, LOT_Y1, gaps=[(92.0, 95.0)])
    # THE FIELD GATE — two closed swing leaves, frame-and-rail
    for li, (l0, l1) in enumerate([(GATE_Y0, (GATE_Y0 + GATE_Y1) / 2.0),
                                   ((GATE_Y0 + GATE_Y1) / 2.0, GATE_Y1)]):
        for pi, py in enumerate((l0 + 0.05, l1 - 0.05)):
            make_cyl(f"Gate_Leaf{li}_Stile_{pi}", (-FENCE_X, py, 1.10),
                     0.032, 2.20, COL_GALV)
        for ri, rz in enumerate((2.12, 1.10, 0.14)):
            make_cyl(f"Gate_Leaf{li}_Rail_{ri}",
                     (-FENCE_X, (l0 + l1) / 2.0, rz), 0.026, l1 - l0 - 0.12,
                     COL_GALV, axis='Y')
    make_box("Gate_Latch", (-FENCE_X, (GATE_Y0 + GATE_Y1) / 2.0, 1.12),
             (0.10, 0.16, 0.10), COL_STEEL_DK)


# ══════════════════════════════════════════════════════════════════
# FIELD-LIGHT TOWERS — four poles behind the stands, fixture banks
# only (real light comes from scene-side Light3D). Evening register:
# the fixtures are the geometry the dusk key rakes across.
# ══════════════════════════════════════════════════════════════════
def build_field_lights():
    for px, py, tag in ((-50.5, 20.0, "SW"), (-50.5, 64.0, "NW"),
                        (+50.5, 20.0, "SE"), (+50.5, 64.0, "NE")):
        face = 1.0 if px < 0 else -1.0          # lamp faces toward field
        make_cyl(f"Light_{tag}_Pole", (px, py, 10.5), 0.26, 21.0, COL_GALV,
                 segments=10)
        make_box(f"Light_{tag}_Crossarm", (px, py, 19.4), (0.30, 4.6, 0.30),
                 COL_STEEL_DK)
        for li in range(5):
            ly = py - 1.8 + li * 0.9
            make_box(f"Light_{tag}_Lamp_A{li}", (px, ly, 19.95), (0.42, 0.42, 0.50),
                     COL_STEEL_DK)
            make_box(f"Light_{tag}_Lens_A{li}", (px + face * 0.23, ly, 19.95),
                     (0.05, 0.34, 0.40), COL_WHITE)
        for li in range(4):
            ly = py - 1.35 + li * 0.9
            make_box(f"Light_{tag}_Lamp_B{li}", (px, ly, 20.65), (0.42, 0.42, 0.50),
                     COL_STEEL_DK)
            make_box(f"Light_{tag}_Lens_B{li}", (px + face * 0.23, ly, 20.65),
                     (0.05, 0.34, 0.40), COL_WHITE)


# ══════════════════════════════════════════════════════════════════
# SCOREBOARD — beyond the north curve, facing the field. Cabinet +
# unlit amber digit fields (no text — Label3D territory if ever
# needed). 0-7 lived here; so did 21-13 final (ch22).
# ══════════════════════════════════════════════════════════════════
def build_scoreboard():
    for sgn, seg in ((-1, "W"), (+1, "E")):
        make_cyl(f"Score_Post_{seg}", (sgn * 2.8, 117.0, 2.5), 0.11, 5.0,
                 COL_STEEL_DK, segments=10)
    make_box("Score_Cabinet", (0.0, 117.0, 6.0), (7.6, 0.35, 2.7), COL_SCORE_GRN)
    # Face + digit fields step proud of the cabinet's south (field-
    # facing) plane at y = 116.825 — overlapping, never floating
    make_box("Score_Face", (0.0, 116.81, 6.0), (7.0, 0.06, 2.2), COL_SCORE_FACE)
    for fx, fn in ((-2.2, "Home"), (0.0, "Clock"), (+2.2, "Guest")):
        make_box(f"Score_Digits_{fn}", (fx, 116.77, 5.75), (1.5, 0.05, 0.8),
                 COL_SCORE_LMP)
    make_box("Score_HeaderStrip", (0.0, 116.77, 6.95), (7.0, 0.05, 0.35), COL_WHITE)


# ══════════════════════════════════════════════════════════════════
# FIELD HOUSE — cinderblock, at the lot's north end. The corkboard
# outside the door with the depth-chart sheet (ch19_depthchart:
# 67-78, noon-Friday ritual). Door faces the lot (kids read it from
# their cars). The fence gap the runners use is right behind it.
# ══════════════════════════════════════════════════════════════════
def build_field_house():
    fx, fy = -64.0, 96.0
    make_box("FH_Walls", (fx, fy, 1.70), (10.0, 6.0, 3.40), COL_BLOCK)
    make_box("FH_Roof", (fx, fy, 3.49), (10.6, 6.6, 0.18), COL_METAL_RF)
    make_box("FH_RoofCap", (fx, fy, 3.62), (3.0, 2.0, 0.28), COL_STEEL_DK)
    # Door on the south face, facing the lot
    make_box("FH_Door", (fx - 1.6, fy - 3.02, 1.05), (0.95, 0.06, 2.10), COL_DOOR_STL)
    make_box("FH_DoorFrame_Head", (fx - 1.6, fy - 3.03, 2.16), (1.15, 0.05, 0.10),
             COL_WHITE)
    for sgn in (-1, +1):
        make_box(f"FH_DoorFrame_Jamb_{'W' if sgn < 0 else 'E'}",
                 (fx - 1.6 + sgn * 0.55, fy - 3.03, 1.08), (0.10, 0.05, 2.16),
                 COL_WHITE)
    make_box("FH_DoorKnob", (fx - 1.25, fy - 3.06, 1.05), (0.05, 0.04, 0.05),
             COL_STEEL_DK)
    # THE CORKBOARD, east of the door — frame, cork, the fresh
    # depth-chart sheet + two older faded ones. (Frame overlaps the
    # wall plane; panel + sheets step proud — playbook: painted /
    # mounted accents on the OUTSIDE face, never buried or floating.)
    make_box("Cork_Frame", (fx + 0.9, fy - 2.98, 1.55), (1.34, 0.09, 0.94), COL_ALUM_DK)
    make_box("Cork_Panel", (fx + 0.9, fy - 3.05, 1.55), (1.22, 0.04, 0.82), COL_CORK)
    make_box("Cork_Sheet_DepthChart", (fx + 0.72, fy - 3.08, 1.58),
             (0.30, 0.02, 0.42), COL_PAPER)
    make_box("Cork_Sheet_Old_0", (fx + 1.18, fy - 3.07, 1.62), (0.26, 0.015, 0.36),
             (0.84, 0.81, 0.72, 1.0))
    make_box("Cork_Sheet_Old_1", (fx + 0.98, fy - 3.065, 1.32), (0.24, 0.012, 0.20),
             (0.80, 0.77, 0.68, 1.0))
    # Wall floodlight over the door + a bench against the wall
    make_box("FH_Floodlight_Stem", (fx - 1.6, fy - 2.97, 2.55), (0.06, 0.12, 0.06),
             COL_STEEL_DK)
    make_box("FH_Floodlight_Head", (fx - 1.6, fy - 3.09, 2.52), (0.22, 0.14, 0.18),
             COL_STEEL_DK)
    make_box("FH_Bench_Seat", (fx + 2.9, fy - 3.35, 0.45), (1.6, 0.35, 0.06),
             (0.55, 0.44, 0.31, 1.0))
    for pi in range(2):
        make_box(f"FH_Bench_Leg_{pi}", (fx + 2.3 + pi * 1.2, fy - 3.35, 0.21),
                 (0.08, 0.30, 0.42), COL_STEEL_DK)


# ══════════════════════════════════════════════════════════════════
# EQUIPMENT SHED — at the back of the school field with the small
# lot behind it (ch19_depthchart:117-119, Coach Dale's shed talk).
# ══════════════════════════════════════════════════════════════════
def build_equipment_shed():
    sx, sy = 34.0, 104.0
    make_box("Shed_Walls", (sx, sy, 1.40), (5.0, 4.0, 2.80), COL_METAL_RF)
    make_box("Shed_Roof", (sx, sy, 2.92), (5.5, 4.5, 0.16), COL_STEEL_DK)
    make_box("Shed_SlideDoor", (sx - 0.6, sy - 1.99, 1.20), (1.90, 0.07, 2.30),
             (0.52, 0.54, 0.52, 1.0))
    make_box("Shed_DoorRail", (sx - 0.3, sy - 2.01, 2.45), (3.4, 0.06, 0.08),
             COL_STEEL_DK)
    make_box("Shed_Pad", (sx, sy + 4.5, 0.02), (7.0, 5.0, 0.04), COL_ASPHALT)


# ══════════════════════════════════════════════════════════════════
# THE SCHOOL — distant two-story brick massing NW beyond the north
# road (Ben "drives back to the school", the locked front). Massing
# only: window bands, entry block, gym volume, rooftop mech.
# ══════════════════════════════════════════════════════════════════
def build_school():
    make_box("School_Main", (-40.0, 132.0, 3.6), (46.0, 15.0, 7.2), COL_BRICK)
    for zi, wz in enumerate((2.2, 5.2)):
        make_box(f"School_WinBand_{zi}", (-40.0, 124.47, wz), (43.0, 0.10, 1.10),
                 COL_GLASS_DK)
    make_box("School_Entry", (-40.0, 123.0, 2.3), (8.0, 3.4, 4.6), COL_BRICK_2)
    make_box("School_EntryGlass", (-40.0, 121.28, 1.7), (4.6, 0.08, 2.6), COL_GLASS_DK)
    for ri, (rx, rw) in enumerate([(-52.0, 3.0), (-40.0, 4.0), (-28.0, 2.5)]):
        make_box(f"School_RoofUnit_{ri}", (rx, 133.0, 7.8), (rw, 2.4, 1.2),
                 COL_METAL_RF)
    make_box("School_Gym", (-10.0, 134.0, 4.5), (20.0, 17.0, 9.0), COL_BRICK_2)
    make_box("School_GymBand", (-10.0, 125.48, 6.8), (17.0, 0.10, 1.0), COL_GLASS_DK)
    make_cyl("School_Flagpole", (-38.0, 119.5, 4.5), 0.05, 9.0, COL_WHITE, segments=8)
    make_cyl("School_Flagpole_Ball", (-38.0, 119.5, 9.08), 0.09, 0.16, COL_GP_YELLOW,
             segments=8)


# ══════════════════════════════════════════════════════════════════
# THE LIVE OAK — the field's namesake, off the east straight.
# Trunk + limb tubes (never boxes for organic shapes) + offset
# canopy lobes; the canopy leans out over lane six.
# ══════════════════════════════════════════════════════════════════
def build_live_oak():
    ox, oy = 45.0, 54.0
    make_cyl("Oak_Trunk", (ox, oy, 1.60), 0.55, 3.20, COL_TRUNK, segments=10)
    for fi, (fdx, fdy) in enumerate([(-0.45, -0.25), (0.42, -0.30), (0.05, 0.50)]):
        make_cyl(f"Oak_RootFlare_{fi}", (ox + fdx, oy + fdy, 0.35), 0.20, 0.70,
                 COL_TRUNK, segments=8)
    crotch = (ox, oy, 2.85)
    limbs = [((41.6, 50.6, 5.2), 0.26), ((48.4, 51.2, 5.6), 0.24),
             ((44.2, 58.2, 5.4), 0.26), ((41.2, 57.2, 4.7), 0.20),
             ((48.2, 57.0, 4.9), 0.20)]
    for li, (tip, lr) in enumerate(limbs):
        make_tube(f"Oak_Limb_{li}", crotch, tip, lr, COL_TRUNK)
    lobes = [((43.0, 51.0, 6.5), 3.4, 2.6, COL_OAK_A),
             ((47.5, 52.0, 6.9), 3.2, 2.4, COL_OAK_B),
             ((44.5, 57.2, 6.7), 3.6, 2.6, COL_OAK_A),
             ((41.4, 55.6, 5.9), 2.8, 2.2, COL_OAK_B),
             ((47.8, 56.8, 6.1), 2.7, 2.2, COL_OAK_A),
             ((45.0, 54.0, 8.6), 2.7, 2.1, COL_OAK_B)]
    for ci, ((lx, ly, lz), lr, lh, col) in enumerate(lobes):
        make_cyl(f"Oak_Canopy_{ci}", (lx, ly, lz), lr, lh, col, segments=10)


# ══════════════════════════════════════════════════════════════════
# BACKGROUND TREES — species diversity (pine / oak / cedar) with
# baked scale variety, behind the north fence + along the east road.
# ══════════════════════════════════════════════════════════════════
def _bg_pine(prefix, x, y, s):
    make_cyl(f"{prefix}_Trunk", (x, y, 2.4 * s), 0.16 * s, 4.8 * s, COL_TRUNK)
    for ti, (tr, tz, th) in enumerate([(1.9, 5.6, 2.2), (1.4, 7.3, 2.0),
                                       (0.8, 8.8, 1.8)]):
        make_cyl(f"{prefix}_Tier_{ti}", (x, y, tz * s), tr * s, th * s, COL_PINE,
                 segments=8)

def _bg_oak(prefix, x, y, s):
    make_cyl(f"{prefix}_Trunk", (x, y, 1.3 * s), 0.24 * s, 2.6 * s, COL_TRUNK)
    for ci, (cdx, cdy, cz, cr, ch, col) in enumerate([
            (0.0, 0.0, 3.4, 2.6, 1.9, COL_OAK_A),
            (-1.1, 0.6, 4.3, 1.9, 1.6, COL_OAK_B),
            (1.2, -0.4, 4.5, 1.7, 1.5, COL_OAK_A)]):
        make_cyl(f"{prefix}_Lobe_{ci}", (x + cdx * s, y + cdy * s, cz * s),
                 cr * s, ch * s, col, segments=8)

def build_background_trees():
    pines = [(-34.0, 128.0, 1.10), (3.0, 127.0, 0.90), (39.0, 129.0, 1.35),
             (70.0, 131.0, 1.20)]
    oaks = [(-16.0, 131.0, 1.30), (20.0, 132.0, 1.20), (56.0, 127.0, 1.00),
            (76.0, 60.0, 0.90), (74.0, 24.0, 1.10)]
    for i, (x, y, s) in enumerate(pines):
        _bg_pine(f"BgPine_{i}", x, y, s)
    for i, (x, y, s) in enumerate(oaks):
        _bg_oak(f"BgOak_{i}", x, y, s)


# ══════════════════════════════════════════════════════════════════
# VEHICLES — slab-tier bodies (playbook: acceptable for cars).
# Coach K's F-250 (white, camper shell, ladder rack, THE TAPED
# DRIVER'S-SIDE MIRROR) at the head of the lot; Brent's black
# F-150; Tucker's Tacoma; Ben's Civic four spaces down (ch13).
# All nose east toward the fence.
# ══════════════════════════════════════════════════════════════════
def _pickup(prefix, cx, cy, body_col, camper=False, rack=False,
            mirror_tape=False):
    z0 = LOT_TOP
    make_box(f"{prefix}_Body", (cx, cy, z0 + 0.82), (5.4, 1.94, 0.50), body_col)
    make_box(f"{prefix}_Cab", (cx + 0.55, cy, z0 + 1.36), (1.65, 1.80, 0.58), body_col)
    make_box(f"{prefix}_Windshield", (cx + 1.40, cy, z0 + 1.38), (0.06, 1.55, 0.46),
             COL_GLASS_DK)
    for sgn, seg in ((-1, "S"), (+1, "N")):
        make_box(f"{prefix}_SideGlass_{seg}", (cx + 0.55, cy + sgn * 0.915, z0 + 1.38),
                 (1.35, 0.05, 0.42), COL_GLASS_DK)
    if camper:
        make_box(f"{prefix}_Shell", (cx - 1.55, cy, z0 + 1.36), (2.45, 1.88, 0.58),
                 COL_SHELL)
        make_box(f"{prefix}_ShellWin", (cx - 2.80, cy, z0 + 1.36), (0.05, 1.30, 0.40),
                 COL_GLASS_DK)
    else:
        for sgn, seg in ((-1, "S"), (+1, "N")):
            make_box(f"{prefix}_BedWall_{seg}", (cx - 1.55, cy + sgn * 0.90, z0 + 1.18),
                     (2.45, 0.08, 0.22), body_col)
        make_box(f"{prefix}_Tailgate", (cx - 2.74, cy, z0 + 1.18), (0.08, 1.86, 0.22),
                 body_col)
    if rack:
        # Rack posts sit ON the camper shell (top z0+1.65), not
        # piercing through it — audit intersections first (playbook)
        for ri, (rdx, rdy) in enumerate([(-2.5, -0.85), (-2.5, 0.85),
                                         (-0.5, -0.85), (-0.5, 0.85)]):
            make_cyl(f"{prefix}_RackPost_{ri}", (cx + rdx, cy + rdy, z0 + 1.79),
                     0.03, 0.30, COL_STEEL_DK, segments=8)
        for sgn, seg in ((-1, "S"), (+1, "N")):
            make_cyl(f"{prefix}_RackRail_{seg}", (cx - 0.9, cy + sgn * 0.85, z0 + 1.94),
                     0.03, 4.4, COL_STEEL_DK, axis='X', segments=8)
    for wi, (wdx, wdy) in enumerate([(1.75, -0.86), (1.75, 0.86),
                                     (-1.75, -0.86), (-1.75, 0.86)]):
        make_cyl(f"{prefix}_Wheel_{wi}", (cx + wdx, cy + wdy, z0 + 0.36), 0.36, 0.26,
                 COL_TIRE, axis='Y', segments=10)
    for sgn, seg in ((-1, "S"), (+1, "N")):
        make_box(f"{prefix}_Mirror_{seg}", (cx + 1.30, cy + sgn * 1.02, z0 + 1.50),
                 (0.10, 0.14, 0.14), body_col)
    if mirror_tape:      # driver's side = north (+Y) when nosing east
        make_box(f"{prefix}_MirrorTape", (cx + 1.30, cy + 1.10, z0 + 1.50),
                 (0.11, 0.03, 0.15), COL_TAPE)
    make_box(f"{prefix}_Bumper_F", (cx + 2.74, cy, z0 + 0.62), (0.10, 1.80, 0.16),
             COL_ALUM)
    make_box(f"{prefix}_Bumper_R", (cx - 2.74, cy, z0 + 0.62), (0.10, 1.80, 0.16),
             COL_ALUM)

def _sedan(prefix, cx, cy, body_col):
    z0 = LOT_TOP
    make_box(f"{prefix}_Body", (cx, cy, z0 + 0.72), (4.5, 1.75, 0.42), body_col)
    make_box(f"{prefix}_Cabin", (cx - 0.15, cy, z0 + 1.16), (2.35, 1.62, 0.46),
             body_col)
    make_box(f"{prefix}_Windshield", (cx + 1.05, cy, z0 + 1.16), (0.06, 1.40, 0.38),
             COL_GLASS_DK)
    make_box(f"{prefix}_RearGlass", (cx - 1.35, cy, z0 + 1.16), (0.06, 1.40, 0.36),
             COL_GLASS_DK)
    for sgn, seg in ((-1, "S"), (+1, "N")):
        make_box(f"{prefix}_SideGlass_{seg}", (cx - 0.15, cy + sgn * 0.825, z0 + 1.16),
                 (1.90, 0.05, 0.34), COL_GLASS_DK)
    for wi, (wdx, wdy) in enumerate([(1.45, -0.78), (1.45, 0.78),
                                     (-1.45, -0.78), (-1.45, 0.78)]):
        make_cyl(f"{prefix}_Wheel_{wi}", (cx + wdx, cy + wdy, z0 + 0.31), 0.31, 0.22,
                 COL_TIRE, axis='Y', segments=10)

def build_vehicles():
    car_x = -57.3
    _pickup("Truck_CoachK", car_x, HEAD_Y, COL_F250, camper=True, rack=True,
            mirror_tape=True)                       # head of the lot (ch13:6)
    _pickup("Truck_Brent", car_x, HEAD_Y + 2 * STALL_P, COL_F150)
    _pickup("Truck_Tucker", car_x, HEAD_Y + 3 * STALL_P, COL_TACOMA)
    _sedan("Car_Ben", car_x, HEAD_Y + 4 * STALL_P, COL_CIVIC)   # four spaces down


def main():
    clear_scene()
    # Exterior discipline: ground → circulation → track → field →
    # features. (Playbook 2026-06-14: ground + roads BEFORE features.)
    build_ground()
    build_roads_and_lot()
    build_track()
    build_field()
    build_goalposts()
    build_bleachers()
    build_sideline()
    build_fence_and_gates()
    build_field_lights()
    build_scoreboard()
    build_field_house()
    build_equipment_shed()
    build_school()
    build_live_oak()
    build_background_trees()
    build_vehicles()
    out = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)),
        "../../../assets/3d/locales/school_field_evening.glb"))
    print(f"\n[build_school_field_evening] exporting to {out}")
    export_glb(out)

if __name__ == "__main__":
    main()
