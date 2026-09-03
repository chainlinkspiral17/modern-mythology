"""VOL 5 · Louisiana Road — outdoor cameo. Two-lane blacktop
through swamp/woodland: cypress trees with Spanish moss, road
shoulder, mile markers, distant gas-station sign.
"""
import os, sys
_BT = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
if _BT not in sys.path: sys.path.insert(0, _BT)
import math
from _props import palette as P
from _props.geometry import clear_scene, make_box, make_cyl, export_glb

COL_ASPHALT = (0.16, 0.16, 0.18, 1.0); COL_LANE_LINE = (0.96, 0.92, 0.62, 1.0)
COL_GRASS = (0.42, 0.46, 0.30, 1.0); COL_DIRT_SHOULDER = (0.42, 0.32, 0.22, 1.0)
COL_CYPRESS_TRUNK = (0.32, 0.22, 0.16, 1.0); COL_CYPRESS_FOLIAGE = (0.32, 0.42, 0.30, 1.0)
COL_SPANISH_MOSS = (0.62, 0.58, 0.42, 1.0)
COL_SWAMP_WATER = (0.18, 0.24, 0.18, 0.65); COL_LILY = (0.32, 0.42, 0.30, 1.0)
COL_MILE_MARKER = (0.78, 0.84, 0.62, 1.0); COL_SIGN_RED = (0.74, 0.28, 0.20, 1.0)
COL_SKY = (0.10, 0.13, 0.22, 1.0)   # night sky backdrop (deep dusk blue)

# ── Suburban dressing palette (Harmony Creek Estates night street) ──
COL_SIDEWALK  = (0.54, 0.54, 0.52, 1.0)   # pale concrete
COL_CURB      = (0.42, 0.42, 0.42, 1.0)
COL_DRIVEWAY  = (0.48, 0.48, 0.50, 1.0)
COL_LAWN      = (0.30, 0.44, 0.24, 1.0)   # mowed front lawn, darker at night
COL_HOUSE_TAN = (0.52, 0.44, 0.34, 1.0)   # tan siding ranch
COL_HOUSE_GRY = (0.42, 0.42, 0.46, 1.0)   # gray two-story
COL_HOUSE_BRK = (0.46, 0.34, 0.30, 1.0)   # brick
COL_ROOF      = (0.18, 0.16, 0.18, 1.0)
COL_ROOF_WARM = (0.24, 0.19, 0.17, 1.0)
COL_TRIM      = (0.72, 0.70, 0.64, 1.0)
COL_WIN_WARM  = (0.98, 0.88, 0.58, 1.0)   # lit window (bright — reads as glowing)
COL_WIN_TV    = (0.56, 0.68, 0.94, 1.0)   # cool TV-glow window
COL_WIN_DARK  = (0.10, 0.12, 0.16, 1.0)   # unlit window
COL_DOOR      = (0.36, 0.24, 0.20, 1.0)
COL_LAMP_POLE = (0.22, 0.22, 0.24, 1.0)
COL_LAMP_HEAD = (1.0, 0.80, 0.42, 1.0)    # sodium fixture glass (bright warm)
COL_MAILBOX   = (0.30, 0.34, 0.40, 1.0)
COL_MAIL_POST = (0.40, 0.30, 0.20, 1.0)
COL_SHRUB     = (0.26, 0.40, 0.24, 1.0)
COL_SPRINK    = (0.30, 0.32, 0.30, 1.0)
COL_SPRAY     = (0.70, 0.80, 0.88, 0.35)  # faint sprinkler arc droplets
COL_STREETSIGN_G = (0.20, 0.46, 0.32, 1.0)

# Streetlamp fixtures. Each entry is (pole_x, y, head_x) in BLENDER frame;
# lamp head sits at z=5.0. The louisiana_road.tscn Sodium_* practicals are
# co-located: godot(x,y,z) = (head_x, 5.0, -y). This outdoor set legitimately
# spans +/-Y (godot +/-Z), so the practicals sit at both +Z and -Z (not a bug).
LAMP_FIXTURES = [
    (-3.7, -2.0, -2.8), (-3.7, 6.0, -2.8), (-3.7, 14.0, -2.8),  # west verge
    (+5.4, 2.0, 3.0), (+5.4, 10.0, 3.0),                        # east verge
]


# The road's far end. Everything that must run to the horizon reads
# this. (2026-08-04: the road was 48m long with a painted sky wall
# 33m ahead of the camera — "the highway is a stump, it does not
# stretch." A highway reads as a highway because its lines converge
# to a vanishing point; you cannot fake that with 33 metres.)
ROAD_FAR = 1200.0
ROAD_NEAR = -1200.0


def build_road():
    # Road runs N-S along Y axis. Half-width 2m.
    span = (ROAD_FAR - ROAD_NEAR) / 2.0
    mid = (ROAD_FAR + ROAD_NEAR) / 2.0
    # Asphalt · one long ribbon to the horizon
    make_box("Asphalt", (0.0, mid, 0.0), (4.0, span, 0.04), COL_ASPHALT)
    # Center yellow dashes · a real 3m-on / 9m-off cadence, run the
    # whole length. The convergence of THESE is the sense of distance.
    di = 0
    dy = ROAD_NEAR
    while dy < ROAD_FAR:
        make_box(f"CenterLine_{di}", (0.0, dy, 0.022), (0.10, 1.50, 0.005),
                 COL_LANE_LINE)
        dy += 12.0
        di += 1
    # White edge lines
    for sgn in (-1, +1):
        make_box(f"EdgeLine_{sgn:+d}", (sgn*1.85, mid, 0.022),
                 (0.06, span, 0.005), (0.92, 0.92, 0.86, 1.0))
    # Dirt shoulders
    for sgn in (-1, +1):
        make_box(f"Shoulder_{sgn:+d}", (sgn*2.50, mid, 0.02),
                 (0.80, span, 0.04), COL_DIRT_SHOULDER)


def build_grass_and_swamp():
    # GROUND (2026-08-09, user: "no ground on any of the roads,
    # outside the road it's a flat expanse of nothing"): the terrain
    # runs the road's full 2400m, out past the treeline bands.
    # West: bottomland floor. East: the swamp proper — floor plus a
    # standing-water sheet (this is the guardrail side).
    make_box("Swamp_Floor_W", (-66.0, 0.0, -0.012), (120.0, 2500.0, 0.02),
             (0.13, 0.17, 0.11, 1.0))
    make_box("Swamp_Floor_E", (+66.0, 0.0, -0.012), (120.0, 2500.0, 0.02),
             (0.12, 0.16, 0.11, 1.0))
    make_box("Swamp_Water_E", (+80.0, 0.0, 0.002), (100.0, 2500.0, 0.008),
             (0.10, 0.15, 0.15, 1.0))
    # Near-road grass strips (the settlement block keeps its lawn)
    make_box("Grass_W", (-5.50, 6.0, 0.02), (4.60, 24.0, 0.04), COL_GRASS)
    make_box("Grass_E", (+5.50, 6.0, 0.02), (4.60, 24.0, 0.04), COL_GRASS)
    # Swamp water patches east
    for wi, (wx, wy) in enumerate([(7.5, 2.0), (8.5, 5.0), (7.5, 9.0), (8.0, 13.0)]):
        make_cyl(f"SwampWater_{wi}", (wx, wy, 0.024), 1.20, 0.006, COL_SWAMP_WATER, segments=12)
        # Lily pads
        for li in range(3):
            ang = li * 2.094
            lx = wx + math.cos(ang) * 0.40
            ly = wy + math.sin(ang) * 0.40
            make_cyl(f"Lily_{wi}_{li}", (lx, ly, 0.030), 0.20, 0.005, COL_LILY, segments=8)


def build_cypress_trees():
    # Cypress trees east + west of road, varying distances + heights
    positions = [
        (-8.5, 0.4, 6.5), (-8.9, 2.4, 7.0), (-7.5, 8.0, 5.8),
        (-8.9, 10.2, 6.8), (-8.0, 15.0, 7.2), (-9.0, 18.0, 6.0),
        (+9.0, 2.0, 7.0), (+9.2, 5.7, 6.5), (+9.0, 10.5, 7.5),
        (+9.7, 13.1, 6.0), (+9.4, 24.4, 6.5),
        # trunks 1/3/10 were through HouseW awnings + the gas canopy
    ]
    # 2026-08-04: crowns were three stacked flat discs (layer-cake).
    # Real cypress now: buttressed taper trunk + one wide squashed
    # blob crown + moss, from _props.trees.
    from _props.trees import make_cypress
    for ti, (tx, ty, th) in enumerate(positions):
        make_cypress(f"Cypress_{ti}", tx, ty, th,
                     COL_CYPRESS_FOLIAGE, COL_CYPRESS_TRUNK,
                     COL_SPANISH_MOSS)


def build_signs_and_markers():
    # Mile-marker reflectors along edge
    # explicit list — the stalled sedan occupies y 6..10 of the
    # shoulder and marker 3 used to stand inside its body
    for mi, my in enumerate([-2.0, 1.5, 5.0, 12.0, 15.5, 19.0]):
        make_box(f"Marker_W_{mi}_Post", (-2.80, my, 0.40), (0.04, 0.04, 0.80), COL_MILE_MARKER)
        make_box(f"Marker_W_{mi}_Reflector", (-2.80, my, 0.70), (0.06, 0.04, 0.10), (0.96, 0.62, 0.20, 1.0))
    # Distant gas-station sign (north end of road)
    sx, sy = +2.0, 20.0
    make_cyl("GasSign_Pole", (sx, sy, 2.50), 0.10, 5.00, P.METAL_STEEL)
    make_box("GasSign_BG", (sx, sy, 5.30), (1.20, 0.10, 0.80), COL_SIGN_RED)
    make_box("GasSign_Letters", (sx-0.06, sy, 5.30), (0.005, 1.00, 0.30), P.PAPER)
    # Stop-ahead sign south
    sx2, sy2 = -2.50, -3.5
    make_cyl("StopSign_Pole", (sx2, sy2, 1.20), 0.04, 2.40, P.METAL_STEEL)
    make_box("StopSign_Face", (sx2, sy2, 2.20), (0.50, 0.04, 0.50), COL_SIGN_RED)


def build_sky_backdrop():
    # The old backdrop was a 56m-wide panel standing 33m in front of
    # the camera: a WALL at the end of the road. It is why the
    # highway read as a stump. The horizon is the environment's job
    # (fog + sky in the .tscn); geometry's job is to run out far
    # enough that fog eats it.
    #
    # What's left here is depth-cueing scenery that lives BEYOND the
    # drivable road: receding treelines either side, stepping back in
    # bands so aerial perspective has something to grade.
    for i, (by, bw, bh, shade) in enumerate([
            (120.0, 70.0, 7.0, 0.90), (240.0, 110.0, 8.5, 0.76),
            (420.0, 170.0, 10.0, 0.62), (700.0, 260.0, 12.0, 0.50),
            (1050.0, 380.0, 15.0, 0.40)]):
        c = (COL_SKY[0] * shade, COL_SKY[1] * shade, COL_SKY[2] * shade, 1.0)
        for sgn in (-1, +1):
            for ns in (-1, +1):
                make_box(f"FarTreeline_{i}_{sgn:+d}_{ns:+d}",
                         (sgn * (12.0 + bw * 0.5), ns * by, bh * 0.5),
                         (bw, 6.0, bh), c)




def build_roadside_detail():
    """Scene-standard deep pass (2026-07-12) for the game's most-seen
    backdrop (67 instances). Adds the iconic two-lane-swamp-highway
    silhouette the flat road was missing: a run of leaning
    utility poles with sagging catenary wires down the east verge, a
    dented guardrail on the swamp side, a stalled sedan on the west
    shoulder (gives the scenes' sedan/truck cuts a real subject),
    cattail reed clumps in the water, a dead cypress snag, a culvert
    pipe under the shoulder, and faded skid marks on the asphalt.
    Road runs N-S along +Y; asphalt half-width 2m; shoulders at
    x=+/-2.2. Uses only make_box/make_cyl (this script's imports)."""
    import math as _m
    pole_wood = (0.34, 0.26, 0.20, 1.0)
    wire_col  = (0.08, 0.08, 0.09, 1.0)
    steel     = (0.52, 0.54, 0.56, 1.0)
    steel_dk  = (0.34, 0.35, 0.37, 1.0)
    # ── Utility poles + sagging wires down the EAST verge (x=+3.4) ──
    pole_x = 3.4
    # Poles march to the horizon at a real 40m spacing — the
    # repeating vertical that tells the eye how far it is seeing.
    pole_ys = [-1080.0 + i * 40.0 for i in range(55)]
    top_z = 5.2
    for i, py in enumerate(pole_ys):
        lean = _m.radians(3 + (i % 3))   # each leans a hair differently
        make_cyl(f"Pole_{i}", (pole_x + i * 0.02, py, top_z / 2), 0.09, top_z,
                 pole_wood, segments=6)
        # crossarm near the top
        make_box(f"Pole_{i}_Arm", (pole_x, py, top_z - 0.4),
                 (0.06, 0.9, 0.08), pole_wood)
        for sgn in (-1, +1):
            make_cyl(f"Pole_{i}_Insul_{sgn:+d}", (pole_x, py + sgn * 0.35, top_z - 0.32),
                     0.04, 0.10, (0.30, 0.44, 0.42, 1.0), segments=5)
        # sagging catenary wire to the next pole (three dip segments)
        if i < len(pole_ys) - 1:
            ny = pole_ys[i + 1]
            span = ny - py
            for seg in range(4):
                t0 = seg / 4.0; t1 = (seg + 1) / 4.0
                tm = (t0 + t1) / 2
                sag = 0.55 * _m.sin(_m.pi * tm)   # dip lowest mid-span
                make_cyl(f"Wire_{i}_{seg}", (pole_x, py + span * tm, top_z - 0.30 - sag),
                         0.012, span / 4.0 + 0.05, wire_col, segments=3, axis='Y')
    # ── Guardrail on the SWAMP (east) side, x=+3.0, dented ──
    for i in range(730):
        gy = -1095.0 + i * 3.0
        dent = 0.05 if i == 5 else 0.0   # one bashed post
        make_box(f"Guardrail_Beam_{i}", (3.0 + dent, gy + 1.5, 0.55),
                 (0.04, 3.0, 0.16), steel)
        make_cyl(f"Guardrail_Post_{i}", (3.0, gy, 0.28), 0.05, 0.56,
                 steel_dk, segments=5)
    # ── Stalled sedan on the WEST shoulder, nosed north ──
    cxp, cyp = -2.55, 8.0
    body = (0.46, 0.16, 0.16, 1.0)
    glass = (0.20, 0.26, 0.30, 1.0)
    make_box("Sedan_LowerBody", (cxp, cyp, 0.44), (1.7, 4.0, 0.5), body)
    make_box("Sedan_Cabin", (cxp, cyp - 0.2, 0.95), (1.55, 2.2, 0.55),
             (0.40, 0.14, 0.14, 1.0))
    make_box("Sedan_Windshield", (cxp, cyp + 0.85, 0.98), (1.4, 0.06, 0.42), glass)
    make_box("Sedan_RearGlass", (cxp, cyp - 1.28, 0.98), (1.4, 0.06, 0.40), glass)
    for sgn in (-1, +1):
        make_box(f"Sedan_SideGlass_{sgn:+d}", (cxp + sgn * 0.76, cyp - 0.2, 0.98),
                 (0.05, 2.0, 0.40), glass)
    for wx in (-0.65, 0.65):
        for wy in (-1.4, 1.4):
            make_cyl(f"Sedan_Wheel_{wx:+.0f}_{wy:+.0f}", (cxp + wx, cyp + wy, 0.30),
                     0.34, 0.30, (0.08, 0.08, 0.09, 1.0), segments=8, axis='X')
    make_box("Sedan_Bumper_F", (cxp, cyp + 2.02, 0.42), (1.6, 0.10, 0.24), steel)
    make_box("Sedan_HoodUp", (cxp, cyp + 1.3, 1.02), (1.4, 1.2, 0.06),
             (0.42, 0.15, 0.15, 1.0))   # hood popped (broken down)
    # ── Cattail reed clumps in the swamp (EAST — where the water
    # actually is; they used to stand on the mowed west lawn) ──
    for i, (rx, ry) in enumerate([(7.6, 2.0), (8.2, 9.0), (6.8, 15.0),
                                  (8.4, 20.0), (7.2, -4.0)]):
        for b in range(5):
            a = b * 1.3
            bx = rx + _m.cos(a) * 0.18; by = ry + _m.sin(a) * 0.18
            h = 0.9 + 0.25 * (b % 3)
            make_cyl(f"Reed_{i}_{b}", (bx, by, h / 2), 0.015, h,
                     (0.44, 0.48, 0.32, 1.0), segments=3)
            make_cyl(f"Reed_{i}_{b}_Head", (bx, by, h + 0.05), 0.03, 0.12,
                     (0.36, 0.24, 0.14, 1.0), segments=4)
    # ── Dead cypress snag (bare, pale) on the east treeline ──
    sx, sy = 6.5, 13.0
    make_cyl("Snag_Trunk", (sx, sy, 3.0), 0.22, 6.0, (0.58, 0.56, 0.50, 1.0), segments=6)
    for i, (dz, ang, ln) in enumerate([(4.2, 0.4, 1.6), (3.4, 3.5, 1.9), (4.8, 1.9, 1.2)]):
        make_cyl(f"Snag_Limb_{i}",
                 (sx + _m.cos(ang) * ln / 2, sy + _m.sin(ang) * ln / 2, dz),
                 0.06, ln, (0.54, 0.52, 0.46, 1.0), segments=4, axis='X')
    # ── Culvert pipe mouth under the west shoulder ──
    make_cyl("Culvert_Pipe", (-2.9, -1.0, 0.30), 0.30, 0.9,
             (0.30, 0.31, 0.33, 1.0), segments=10, axis='Y')
    make_cyl("Culvert_Bore", (-2.9, -1.35, 0.30), 0.22, 0.2,
             (0.06, 0.07, 0.07, 1.0), segments=10, axis='Y')
    # ── Faded skid marks on the asphalt (two parallel streaks) ──
    for sgn in (-1, +1):
        for k in range(3):
            make_box(f"Skid_{sgn:+d}_{k}", (sgn * 0.5, 5.0 + k * 0.9, 0.021),
                     (0.10, 0.8, 0.002), (0.09, 0.09, 0.10, 1.0))


def _make_house(prefix, cx, cy, face, style, wall_col):
    """Suburban house massing set back off the road. `face` = +1 for a
    west-side house (road at +X) or -1 for east (road at -X). `style` is
    'ranch' (low + wide, optional garage wing) or 'two_story'. Compound
    silhouette: body + eave + ridge cap + a row of lit/dark windows on the
    road-facing wall + door + chimney, plus a garage wing for ranches. Lit
    windows use bright emissive-reading vertex colour so the frame isn't a
    black void behind the dialogue."""
    import math as _m
    if style == 'two_story':
        bd, bw, bh, rows = 5.0, 6.0, 5.4, 2
    else:                              # ranch
        bd, bw, bh, rows = 5.2, 7.2, 3.0, 1
    # main body
    make_box(f"{prefix}_Body", (cx, cy, bh / 2.0), (bd, bw, bh), wall_col)
    # wide eave slab + ridge cap (hip-roof massing)
    make_box(f"{prefix}_Eave", (cx, cy, bh + 0.12), (bd + 0.7, bw + 0.7, 0.24), COL_ROOF)
    make_box(f"{prefix}_Ridge", (cx, cy, bh + 0.5), (bd * 0.55, bw * 0.7, 0.6), COL_ROOF_WARM)
    # chimney
    make_box(f"{prefix}_Chimney", (cx - bd * 0.28, cy + bw * 0.3, bh + 0.7),
             (0.4, 0.4, 1.0), COL_HOUSE_BRK)
    # road-facing wall + its windows
    wall_x = cx + face * (bd / 2.0 + 0.02)
    lit_cycle = [COL_WIN_WARM, COL_WIN_DARK, COL_WIN_WARM, COL_WIN_TV, COL_WIN_DARK]
    for r in range(rows):
        wz = 1.5 + r * 2.0
        for c in range(3):
            wy = cy - bw * 0.28 + c * (bw * 0.28)
            wc = lit_cycle[(r * 3 + c + (0 if face > 0 else 2)) % len(lit_cycle)]
            make_box(f"{prefix}_Win_{r}_{c}", (wall_x, wy, wz), (0.05, 1.0, 1.0), wc)
            make_box(f"{prefix}_WinTrim_{r}_{c}", (wall_x - face * 0.02, wy, wz),
                     (0.03, 1.16, 1.16), COL_TRIM)
    # front door
    make_box(f"{prefix}_Door", (wall_x, cy - bw * 0.28, 1.05), (0.06, 0.9, 2.1), COL_DOOR)
    # porch: slab + two posts under an awning
    px = wall_x + face * 0.9
    make_box(f"{prefix}_Porch", (px, cy - bw * 0.28, 0.1), (1.8, 2.2, 0.2), COL_SIDEWALK)
    for ps in (-1, +1):
        make_cyl(f"{prefix}_PorchPost_{ps:+d}", (wall_x + face * 1.7, cy - bw * 0.28 + ps * 1.0, 1.2),
                 0.08, 2.4, COL_TRIM, segments=6)
    make_box(f"{prefix}_Awning", (wall_x + face * 1.0, cy - bw * 0.28, 2.45), (2.0, 2.3, 0.14), COL_ROOF)
    # ranch garage wing
    if style == 'ranch':
        gy = cy + bw * 0.5 + 1.6
        make_box(f"{prefix}_Garage", (cx + face * 0.4, gy, 1.3), (bd * 0.7, 3.0, 2.6), wall_col)
        make_box(f"{prefix}_GarageRoof", (cx + face * 0.4, gy, 2.7), (bd * 0.7 + 0.4, 3.2, 0.2), COL_ROOF)
        make_box(f"{prefix}_GarageDoor", (cx + face * (bd * 0.35 + 0.03), gy, 1.1),
                 (0.05, 2.4, 2.0), COL_TRIM)
    # a couple of foundation shrubs against the facing wall
    for si in range(3):
        make_cyl(f"{prefix}_Shrub_{si}", (wall_x + face * 0.5, cy - bw * 0.3 + si * bw * 0.3, 0.4),
                 0.45, 0.8, COL_SHRUB, segments=8)


def _make_streetlamp(prefix, pole_x, y, head_x):
    """Cobra-head sodium streetlamp: pole + arm reaching over the verge +
    a glowing lamp head at z=5.0. The head is co-located with a Sodium_*
    OmniLight practical in louisiana_road.tscn."""
    make_cyl(f"{prefix}_Pole", (pole_x, y, 2.6), 0.09, 5.2, COL_LAMP_POLE, segments=8)
    # horizontal arm from pole toward the road
    arm_len = abs(head_x - pole_x)
    make_cyl(f"{prefix}_Arm", ((pole_x + head_x) / 2.0, y, 5.05), 0.05, arm_len,
             COL_LAMP_POLE, segments=6, axis='X')
    # cobra-head housing + bright glass lens (reads as the lit fixture)
    make_box(f"{prefix}_Housing", (head_x, y, 5.12), (0.5, 0.28, 0.16), COL_LAMP_POLE)
    make_box(f"{prefix}_Lens", (head_x, y, 4.98), (0.42, 0.22, 0.06), COL_LAMP_HEAD)


def build_suburban_street():
    """Populate the black frame: Harmony Creek Estates comes right up to
    this two-lane road. West side is fully developed (sidewalk, lawns with
    sprinklers, driveways, houses, mailboxes, a parked car); the east side
    backs onto the bayou but still carries set-back houses + a sidewalk, so
    the road reads as a lit suburban street from any angle instead of a
    strip of asphalt in a void. Blender frame; road runs N-S along +Y."""
    import math as _m
    y0, y1 = -6.0, 18.0
    y_mid, y_len = (y0 + y1) / 2.0, (y1 - y0)
    # ── Sidewalks + curbs both sides (public right-of-way) ──
    for sgn, sw_x in ((-1, -4.0), (+1, 4.6)):
        make_box(f"Sidewalk_{sgn:+d}", (sw_x, y_mid, 0.03), (1.2, y_len, 0.06), COL_SIDEWALK)
        make_box(f"Curb_{sgn:+d}", (sw_x - sgn * 0.7, y_mid, 0.05), (0.12, y_len, 0.12), COL_CURB)
    # ── West front lawns (mowed, raised slightly off the street) ──
    make_box("Lawn_W", (-8.0, y_mid, 0.035), (7.0, y_len, 0.05), COL_LAWN)
    # ── Houses set back on BOTH sides, varied silhouettes ──
    west_houses = [(-1.5, 'ranch', COL_HOUSE_TAN), (6.5, 'two_story', COL_HOUSE_GRY),
                   (14.0, 'ranch', COL_HOUSE_BRK)]
    for i, (hy, style, col) in enumerate(west_houses):
        _make_house(f"HouseW_{i}", -12.5, hy, +1, style, col)
    east_houses = [(1.0, 'two_story', COL_HOUSE_BRK), (9.0, 'ranch', COL_HOUSE_TAN),
                   (29.5, 'two_story', COL_HOUSE_GRY)]  # north of the gas station — at 16.5 it stood inside the store
    for i, (hy, style, col) in enumerate(east_houses):
        _make_house(f"HouseE_{i}", 14.5, hy, -1, style, col)
    # ── Driveways (curb-cut apron to each west house) + one parked car ──
    for i, (hy, _s, _c) in enumerate(west_houses):
        make_box(f"DriveW_{i}", (-6.8, hy, 0.032), (6.0, 2.6, 0.05), COL_DRIVEWAY)
        make_box(f"DriveApron_W_{i}", (-3.2, hy, 0.031), (1.6, 2.2, 0.04), COL_DRIVEWAY)
    # parked sedan on the middle west driveway (nosed toward the house)
    # On house 0's driveway, along it (E-W), nosed west at the
    # house. It was authored crosswise on drive 1: nose inside the
    # porch posts, tail across the cypress buttresses, and drive 1's
    # mouth is where the sedan stalled anyway.
    cxp, cyp = -6.0, -1.3
    make_box("Parked_Body", (cxp, cyp, 0.5), (3.8, 2.0, 0.6), (0.20, 0.28, 0.40, 1.0))
    make_box("Parked_Cabin", (cxp + 0.2, cyp, 1.05), (2.0, 1.7, 0.5), (0.16, 0.22, 0.32, 1.0))
    make_box("Parked_Windshield", (cxp - 0.75, cyp, 1.06), (0.05, 1.5, 0.42), (0.30, 0.36, 0.42, 1.0))
    for wx in (-1.35, 1.35):
        for wy in (-0.8, 0.8):
            make_cyl(f"Parked_Wheel_{wx:+.0f}_{wy:+.0f}", (cxp + wx, cyp + wy, 0.32),
                     0.34, 0.28, (0.08, 0.08, 0.09, 1.0), segments=8, axis='Y')
    # ── Mailboxes on posts at each west driveway mouth ──
    for i, (hy, _s, _c) in enumerate(west_houses):
        # house 1's box sits SOUTH of its drive: the stalled sedan
        # stands exactly where hy+1.4 lands
        mb_y = hy - 1.4 if i == 1 else hy + 1.4
        make_cyl(f"Mailbox_Post_{i}", (-3.1, mb_y, 0.55), 0.05, 1.1, COL_MAIL_POST, segments=6)
        make_box(f"Mailbox_Box_{i}", (-3.1, mb_y, 1.15), (0.24, 0.42, 0.24), COL_MAILBOX)
        make_box(f"Mailbox_Flag_{i}", (-2.95, mb_y - 0.2, 1.2), (0.02, 0.04, 0.14), COL_SIGN_RED)
    # ── Sprinklers on the west lawns: heads + faint arcing spray ──
    for i, (sx, sy) in enumerate([(-6.8, 0.5), (-6.4, 7.6), (-9.6, 16.8)]):
        make_cyl(f"Sprinkler_{i}", (sx, sy, 0.08), 0.05, 0.16, COL_SPRINK, segments=6)
        # parabolic arc of droplets rising and falling from the head
        for d in range(6):
            t = d / 5.0
            ax = sx + t * 2.4
            az = 0.15 + _m.sin(_m.pi * t) * 1.1
            make_cyl(f"Spray_{i}_{d}", (ax, sy, az), 0.03, 0.06, COL_SPRAY, segments=5)
    # ── West telephone poles w/ crossarms (overhead lines both sides) ──
    for i, py in enumerate([-4.0, 6.0, 16.0]):
        make_cyl(f"WPole_{i}", (-4.6, py, 2.7), 0.09, 5.4, (0.34, 0.26, 0.20, 1.0), segments=6)
        make_box(f"WPole_{i}_Arm", (-4.6, py, 5.0), (0.06, 0.9, 0.08), (0.34, 0.26, 0.20, 1.0))
        for sgn in (-1, +1):
            make_cyl(f"WPole_{i}_Insul_{sgn:+d}", (-4.6, py + sgn * 0.35, 5.12),
                     0.04, 0.10, (0.30, 0.44, 0.42, 1.0), segments=5)
    # ── Streetlamps (co-located with tscn Sodium_* practicals) ──
    for i, (pole_x, y, head_x) in enumerate(LAMP_FIXTURES):
        _make_streetlamp(f"Streetlamp_{i}", pole_x, y, head_x)
    # ── Street-name blade sign at the south intersection ──
    make_cyl("StreetSign_Pole", (-3.0, -5.0, 1.2), 0.04, 2.4, P.METAL_STEEL, segments=6)
    make_box("StreetSign_Blade", (-3.0, -5.0, 2.3), (0.05, 1.2, 0.28), COL_STREETSIGN_G)
    make_box("StreetSign_Text", (-3.03, -5.0, 2.3), (0.005, 0.9, 0.12), P.PAPER)


def build_vol6_landmarks():
    """2026-08-03 hero-prop pass: the civic reads the vol6 prose
    keeps naming — the Harmony Creek water tower (62 ft), the gas
    station the sign already advertised (canopy + pumps + store),
    the traffic light over its exit, the NAPD SUBSTATION B sign."""
    steel = (0.55, 0.57, 0.58, 1.0)
    # Water tower, SW skyline (62 ft ~ 18.9 m)
    for li, (dx, dy) in enumerate(((-2.2, -2.2), (2.2, -2.2), (-2.2, 2.2), (2.2, 2.2))):
        make_cyl(f"WTower_Leg_{li}", (-18.0 + dx, 21.0 + dy, 7.0), 0.20, 14.0, steel, segments=8)
    make_cyl("WTower_Tank", (-18.0, 21.0, 16.2), 3.0, 4.6, (0.72, 0.74, 0.76, 1.0), segments=14)
    make_cyl("WTower_Cap", (-18.0, 21.0, 18.8), 2.2, 0.8, (0.62, 0.64, 0.66, 1.0), segments=14)
    make_box("WTower_Band", (-18.0, 20.9, 16.2), (6.2, 0.05, 1.0), (0.30, 0.44, 0.62, 1.0))
    # The gas station behind its sign (canopy, two islands, store)
    make_box("Gas_Canopy", (7.5, 20.0, 4.85), (10.0, 8.0, 0.5), (0.90, 0.90, 0.92, 1.0))
    for ci, (cx, cy) in enumerate(((4.0, 17.0), (11.0, 17.0), (4.0, 23.0), (11.0, 23.0))):
        make_cyl(f"Gas_Canopy_Post_{ci}", (cx, cy, 2.3), 0.16, 4.6, steel, segments=8)
    for ii, (ix, iy) in enumerate(((5.8, 18.8), (9.2, 18.8), (5.8, 21.2), (9.2, 21.2))):
        make_box(f"Gas_Pump_{ii}", (ix, iy, 0.85), (0.45, 0.55, 1.40), (0.18, 0.32, 0.50, 1.0))
    make_box("Gas_Store", (13.5, 20.0, 1.8), (6.0, 8.0, 3.6), (0.66, 0.62, 0.55, 1.0))
    make_box("Gas_Store_Glow", (10.55, 20.0, 1.4), (0.06, 5.0, 1.6), (0.98, 0.84, 0.55, 1.0))
    # Traffic light over the gas-station exit (the crow's perch)
    # mast west of the canopy edge, head raised above the slab —
    # the pole used to pass through the canopy, the head hung in it
    make_cyl("Signal_Mast", (1.9, 17.0, 3.3), 0.10, 6.6, steel, segments=8)
    make_box("Signal_Arm", (4.05, 17.0, 6.2), (4.2, 0.09, 0.09), steel)
    make_box("Signal_Head", (6.3, 17.0, 5.75), (0.30, 0.30, 0.90), (0.16, 0.16, 0.18, 1.0))
    for si, (sz, col) in enumerate(((6.02, (0.72, 0.20, 0.16, 1.0)), (5.75, (0.86, 0.64, 0.20, 1.0)),
                                    (5.48, (0.26, 0.62, 0.30, 1.0)))):
        make_cyl(f"Signal_Lamp_{si}", (6.16, 17.0, sz), 0.08, 0.03, col, axis='X', segments=8)
    # NAPD SUBSTATION B — hand-touched-up dark-blue enamel
    make_box("NAPD_Base", (-4.35, 12.0, 0.25), (0.30, 1.9, 0.50), (0.52, 0.50, 0.46, 1.0))
    make_box("NAPD_Sign", (-4.35, 12.0, 0.95), (0.15, 1.8, 0.90), (0.12, 0.18, 0.38, 1.0))
    make_box("NAPD_Text", (-4.26, 12.0, 1.05), (0.02, 1.4, 0.30), (0.86, 0.86, 0.82, 1.0))


def build_foxhole_strip_mall_2026_08():
    """THE FOXHOLE STRIP MALL (--props hunt, 2026-08).

    Jesse's whole vol6 surveillance thread runs through geometry
    that did not exist: "The unit at the back of the Foxhole's
    section of the strip mall is the unit Jesse has been tracking"
    · "the papered-over front window" · "His own band's name, in
    chalk, on the front of a venue, in his town." Five cues across
    three chapters looked at nothing.

    Sited east of the road, north of the gas station, with the
    BACK of the mall toward the road — because that is the view
    the chapters use: Jesse in a parked Civic, looking across the
    lot at a dark unit. The white panel van and the dark sedan are
    NOT modeled; the prose keeps noting their absence.
    """
    stucco = (0.72, 0.68, 0.60, 1.0)
    stucco_dk = (0.62, 0.58, 0.50, 1.0)
    roofline = (0.38, 0.35, 0.30, 1.0)
    door_steel = (0.45, 0.46, 0.48, 1.0)
    paper = (0.86, 0.83, 0.76, 1.0)
    chalk = (0.92, 0.92, 0.88, 1.0)
    board = (0.14, 0.14, 0.15, 1.0)
    # y=33 stood inside HouseE_2 (14.5, 29.5) and clipped the
    # gas store — the east side is full through y~35. North of
    # all of it: the mall anchors the road's far end.
    mx, my = 17.0, 47.0            # mall center
    # The mall block: one long bar, back face toward the road (west).
    make_box("StripMall_Block", (mx, my, 2.1), (10.0, 22.0, 4.2), stucco)
    make_box("StripMall_Parapet", (mx, my, 4.35), (10.4, 22.4, 0.35), roofline)
    # Service lot between road and mall back.
    make_box("StripMall_Lot", (10.0, my, 0.015), (7.6, 22.0, 0.03), (0.24, 0.24, 0.25, 1.0))
    for si, sy in enumerate(range(-8, 9, 4)):
        make_box("StripMall_LotStripe_%d" % si, (8.2, my + sy, 0.032),
                 (2.6, 0.10, 0.004), (0.55, 0.54, 0.50, 1.0))
    # Back doors of the row: four plain units...
    for di, dy in enumerate((-8.0, -3.5, 5.5, 9.0)):
        make_box("StripMall_BackDoor_%d" % di, (mx - 5.02, my + dy, 1.05),
                 (0.06, 0.95, 2.10), door_steel)
    # ...the Foxhole's section (rear door + one caged bulb + kegs).
    make_box("Foxhole_BackDoor", (mx - 5.02, my + 1.5, 1.05), (0.06, 0.95, 2.10),
             (0.30, 0.24, 0.20, 1.0))
    make_box("Foxhole_DoorLamp", (mx - 5.10, my + 1.5, 2.45), (0.10, 0.16, 0.16),
             (0.90, 0.78, 0.50, 1.0))
    for ki, ky in enumerate((2.6, 3.1)):
        make_cyl("Foxhole_Keg_%d" % ki, (mx - 5.55, my + ky, 0.30), 0.20, 0.60,
                 (0.60, 0.62, 0.64, 1.0), segments=10)
    # THE UNIT · the tracked one, between the Foxhole and the rest:
    # a rear window PAPERED OVER (paper sheets slightly askew), the
    # door repainted darker than its neighbors, no lamp.
    ux = mx - 5.02
    make_box("Unit_BackDoor", (ux, my - 1.0, 1.05), (0.06, 0.95, 2.10),
             (0.24, 0.23, 0.24, 1.0))
    make_box("Unit_Window_Frame", (ux, my - 2.3, 1.60), (0.05, 1.30, 1.00), stucco_dk)
    for pi2, (poy, poz, w, h) in enumerate((
            (-0.30, 0.18, 0.62, 0.55), (0.28, -0.12, 0.66, 0.60),
            (0.02, 0.30, 0.55, 0.38))):
        make_box("Unit_Window_Paper_%d" % pi2,
                 (ux - 0.035, my - 2.3 + poy, 1.60 + poz), (0.012, w, h), paper)
    # The lot's one working floodlight aims at the OTHER end — the
    # unit sits in the dark on purpose.
    make_cyl("StripMall_FloodPole", (10.5, my + 9.5, 2.6), 0.09, 5.2, door_steel, segments=8)
    make_box("StripMall_FloodHead", (10.7, my + 9.2, 5.1), (0.35, 0.30, 0.22),
             (0.92, 0.88, 0.72, 1.0))
    # THE MARQUEE · front corner, visible from the road past the
    # mall's south end: a black reader board on two posts, chalk
    # lines where the band name is (the name itself is one long
    # chalk stroke and two short ones — legible as writing, not as
    # letters, which is how chalk reads at distance).
    qx, qy = 11.5, 35.5
    for pi3, py3 in enumerate((qy - 0.8, qy + 0.8)):
        make_cyl("Marquee_Post_%d" % pi3, (qx, py3, 1.4), 0.07, 2.8, door_steel, segments=8)
    make_box("Marquee_Board", (qx, qy, 3.1), (0.14, 2.4, 1.30), board)
    make_box("Marquee_Trim", (qx, qy, 3.80), (0.18, 2.5, 0.10), (0.70, 0.20, 0.16, 1.0))
    make_box("Marquee_Chalk_Line1", (qx - 0.08, qy, 3.38), (0.01, 1.9, 0.16), chalk)
    make_box("Marquee_Chalk_Line2", (qx - 0.08, qy - 0.35, 3.05), (0.01, 1.2, 0.12), chalk)
    make_box("Marquee_Chalk_Line3", (qx - 0.08, qy + 0.42, 3.02), (0.01, 0.9, 0.10), chalk)


def build_live_oak_2026_09():
    """LIVE OAK (vol6 ch14, re-homed 2026-09-03 — the beat that stays on
    this set because this set IS the strip mall). "Tonight the door is
    open. Two inches. A faint light is visible through the gap." Jesse
    "stops the car at the corner of the lot, in the small position
    where the sodium lamp does not directly illuminate the Civic's
    silhouette." "At ten twenty-three, Jesse takes out his phone."
    """
    from _props.vehicles import make_car
    mx, my = 17.0, 47.0
    ux = mx - 5.02
    # the two-inch gap: a blade of light on the latch side of the unit's back door, and its spill on the lot
    make_box("Unit_Door_Gap_Light", (ux - 0.035, my - 1.0 + 0.45, 1.05), (0.01, 0.05, 2.02), (0.98, 0.90, 0.66, 1.0))
    make_box("Unit_Door_Light_Spill", (ux - 0.40, my - 0.55, 0.033), (0.70, 0.60, 0.002), (0.46, 0.40, 0.28, 1.0))
    # Jesse's Civic at the south-west corner of the lot, nose north, lights off
    make_car("Civic", 7.2, 38.0, 4.3, (0.34, 0.36, 0.40, 1.0), hatch=True, along="Y", z0=0.03)
    # the phone, lit, in the gap between the dash and the windshield, driver's side
    make_box("Phone", (6.85, 38.0 - 0.40 + 1.30 + 0.015, 0.03 + 1.08), (0.07, 0.012, 0.14), (0.08, 0.08, 0.09, 1.0))
    make_box("Phone_Screen", (6.85, 38.0 - 0.40 + 1.30 + 0.0225, 0.03 + 1.08), (0.062, 0.001, 0.126), (0.66, 0.80, 0.96, 1.0))


def build_cypress_motel_2026_09():
    """THE CYPRESS (vol6 ch15, Room 7 — re-homed 2026-09-03). "A motel
    from the 1970s, single-story, twelve rooms in a long L around a
    small empty parking lot. There are three cars in the lot." Sam
    drives past it slowly on the way home; she does not stop. West of
    the road, north of the houses: the long wing runs N-S at x -26
    with its doors toward the lot, the short wing closes the north end,
    the office and the pole sign at the south end nearest the road.
    Room 7 has its light on and its AC running.
    """
    from _props.vehicles import make_car
    wall = (0.74, 0.66, 0.52, 1.0)
    wall_dk = (0.62, 0.54, 0.42, 1.0)
    trim = (0.40, 0.24, 0.18, 1.0)
    roof = (0.30, 0.28, 0.26, 1.0)
    door = (0.36, 0.26, 0.18, 1.0)
    glass = (0.22, 0.26, 0.32, 1.0)
    glass_lit = (0.96, 0.84, 0.54, 1.0)
    lot = (0.26, 0.26, 0.27, 1.0)
    walk = (0.58, 0.56, 0.52, 1.0)
    rw = 3.4
    y0 = 60.0
    # long wing: rooms 1-8, x -30..-22, doors on the east face
    make_box("Cypress_Motel_Long_Wing", (-26.0, y0 + 4 * rw, 1.45), (8.0, 8 * rw, 2.90), wall)
    make_box("Cypress_Motel_Long_Roof", (-26.0, y0 + 4 * rw, 3.02), (8.4, 8 * rw + 0.4, 0.24), roof)
    make_box("Cypress_Motel_Long_Fascia", (-21.85, y0 + 4 * rw, 3.02), (0.10, 8 * rw + 0.4, 0.30), trim)
    # short wing: rooms 9-12 along the north end, x -22..-8.4, doors on the south face
    make_box("Cypress_Motel_Short_Wing", (-15.2, y0 + 8 * rw + 4.0, 1.45), (13.6, 8.0, 2.90), wall)
    make_box("Cypress_Motel_Short_Roof", (-15.2, y0 + 8 * rw + 4.0, 3.02), (14.0, 8.4, 0.24), roof)
    make_box("Cypress_Motel_Short_Fascia", (-15.2, y0 + 8 * rw - 0.15, 3.02), (14.0, 0.10, 0.30), trim)
    # the office at the south end, its window lit, the ice machine and the soda machine beside it
    make_box("Cypress_Motel_Office", (-26.0, y0 - 2.5, 1.45), (8.0, 5.0, 2.90), wall_dk)
    make_box("Cypress_Motel_Office_Roof", (-26.0, y0 - 2.5, 3.02), (8.4, 5.4, 0.24), roof)
    make_box("Cypress_Motel_Office_Window", (-21.98, y0 - 2.5, 1.55), (0.04, 2.60, 1.20), glass_lit)
    make_box("Cypress_Motel_Office_Door", (-21.98, y0 - 0.2, 1.05), (0.04, 0.90, 2.10), glass)
    make_box("Motel_Ice_Machine", (-21.5, y0 + 0.6, 0.85), (0.80, 0.70, 1.70), (0.80, 0.80, 0.78, 1.0))
    make_box("Motel_Soda_Machine", (-21.5, y0 + 1.5, 0.90), (0.80, 0.80, 1.80), (0.72, 0.16, 0.14, 1.0))
    make_box("Motel_Soda_Machine_Face", (-21.09, y0 + 1.5, 1.10), (0.01, 0.60, 1.10), (0.96, 0.92, 0.80, 1.0))
    # the walkway under the overhang, the posts
    make_box("Cypress_Motel_Walk_Long", (-21.2, y0 + 4 * rw, 0.05), (1.6, 8 * rw, 0.10), walk)
    make_box("Cypress_Motel_Walk_Short", (-15.2, y0 + 8 * rw - 0.8, 0.05), (13.6, 1.6, 0.10), walk)
    make_box("Cypress_Motel_Overhang_Long", (-20.9, y0 + 4 * rw, 2.86), (2.2, 8 * rw, 0.08), roof)
    make_box("Cypress_Motel_Overhang_Short", (-15.2, y0 + 8 * rw - 1.1, 2.86), (13.6, 2.2, 0.08), roof)
    for pi in range(9):
        make_box("Motel_Post_%d" % pi, (-19.85, y0 + pi * rw, 1.41), (0.10, 0.10, 2.82), trim)
    for pi in range(5):
        make_box("Motel_Post_N_%d" % pi, (-21.5 + pi * rw, y0 + 8 * rw - 2.15, 1.41), (0.10, 0.10, 2.82), trim)
    # rooms 1-8: door, window, AC unit under the window, room number, one wall lamp each
    for ri in range(8):
        ry = y0 + ri * rw + rw / 2.0
        lit = (ri == 6)      # Room 7
        make_box("Motel_Room_%d_Door" % (ri + 1), (-21.98, ry - 0.9, 1.05), (0.04, 0.90, 2.10), door)
        make_box("Motel_Room_%d_Number" % (ri + 1), (-21.955, ry - 0.9, 1.75), (0.01, 0.12, 0.14), (0.86, 0.80, 0.60, 1.0))
        make_box("Motel_Room_%d_Window" % (ri + 1), (-21.98, ry + 0.75, 1.60), (0.04, 1.30, 1.00), glass_lit if lit else glass)
        make_box("Motel_Room_%d_Curtain" % (ri + 1), (-21.955, ry + 0.75, 1.60), (0.01, 1.20, 0.90), (0.76, 0.68, 0.50, 1.0) if not lit else (0.92, 0.82, 0.58, 1.0))
        make_box("Motel_Room_%d_AC" % (ri + 1), (-21.65, ry + 0.75, 0.62), (0.70, 0.70, 0.50), (0.68, 0.66, 0.62, 1.0))
        make_box("Motel_Room_%d_Lamp" % (ri + 1), (-21.93, ry - 0.2, 2.30), (0.06, 0.14, 0.14), (0.92, 0.82, 0.50, 1.0))
    make_box("Motel_Room_7_AC_Drip", (-21.65, y0 + 6 * rw + rw / 2.0 + 0.75, 0.101), (0.30, 0.24, 0.002), (0.30, 0.30, 0.32, 1.0))
    # rooms 9-12 on the short wing, plainer
    for ri in range(4):
        rx = -21.5 + ri * rw + rw / 2.0
        make_box("Motel_Room_%d_Door" % (ri + 9), (rx - 0.9, y0 + 8 * rw + 0.02, 1.05), (0.90, 0.04, 2.10), door)
        make_box("Motel_Room_%d_Window" % (ri + 9), (rx + 0.75, y0 + 8 * rw + 0.02, 1.60), (1.30, 0.04, 1.00), glass)
        make_box("Motel_Room_%d_AC" % (ri + 9), (rx + 0.75, y0 + 8 * rw - 0.35, 0.62), (0.70, 0.70, 0.50), (0.68, 0.66, 0.62, 1.0))
    # the small empty parking lot, three cars in it
    make_box("Cypress_Motel_Lot", (-13.0, y0 + 4 * rw - 1.0, 0.015), (14.0, 8 * rw + 4.0, 0.03), lot)
    for si in range(7):
        make_box("Motel_Lot_Stripe_%d" % si, (-17.0, y0 + 2.0 + si * rw, 0.032), (4.6, 0.10, 0.004), (0.50, 0.50, 0.46, 1.0))
    make_car("Motel_Car_0", -15.5, y0 + 2 * rw + 0.4, 4.4, (0.62, 0.62, 0.60, 1.0), along="Y", z0=0.03)
    make_car("Motel_Car_1", -15.5, y0 + 6 * rw + 0.4, 4.2, (0.40, 0.26, 0.20, 1.0), along="Y", z0=0.03)
    make_car("Motel_Car_2", -9.0, y0 + 7 * rw - 1.6, 4.6, (0.20, 0.22, 0.30, 1.0), along="X", z0=0.03)
    # the pole sign by the road: CYPRESS · MOTEL · VACANCY
    make_cyl("Cypress_Motel_Sign_Pole", (-5.5, y0 - 2.0, 3.5), 0.14, 7.0, (0.36, 0.36, 0.38, 1.0), segments=8)
    make_box("Cypress_Motel_Sign", (-5.5, y0 - 2.0, 7.8), (0.30, 3.2, 1.60), (0.18, 0.40, 0.36, 1.0))
    make_box("Cypress_Motel_Sign_Text", (-5.34, y0 - 2.0, 8.1), (0.02, 2.6, 0.50), (0.96, 0.92, 0.72, 1.0))
    make_box("Cypress_Motel_Sign_Motel", (-5.34, y0 - 2.0, 7.5), (0.02, 1.6, 0.26), (0.92, 0.60, 0.30, 1.0))
    make_box("Cypress_Motel_Vacancy", (-5.5, y0 - 2.0, 6.7), (0.26, 2.0, 0.44), (0.16, 0.16, 0.18, 1.0))
    make_box("Cypress_Motel_Vacancy_Neon", (-5.35, y0 - 2.0, 6.7), (0.02, 1.6, 0.18), (0.94, 0.30, 0.30, 1.0))
    # the access road from the highway into the lot
    make_box("Cypress_Motel_Access", (-4.3, y0 + 4.0, 0.012), (3.0, 6.0, 0.024), lot)
    # a cypress or two behind the wings, for the name
    from _props.trees import make_cypress
    make_cypress("Cypress_Motel_Tree_0", -33.5, y0 + 10.0, 7.5, COL_CYPRESS_FOLIAGE, COL_CYPRESS_TRUNK, COL_SPANISH_MOSS)
    make_cypress("Cypress_Motel_Tree_1", -34.0, y0 + 26.0, 6.8, COL_CYPRESS_FOLIAGE, COL_CYPRESS_TRUNK, COL_SPANISH_MOSS)


def main():
    clear_scene()
    build_sky_backdrop()
    build_road()
    build_grass_and_swamp()
    build_cypress_trees()
    build_signs_and_markers()
    build_roadside_detail()
    build_suburban_street()
    build_vol6_landmarks()
    build_foxhole_strip_mall_2026_08()
    build_live_oak_2026_09()
    build_cypress_motel_2026_09()
    out = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "../../../assets/3d/locales/louisiana_road.glb"))
    print(f"\n[build_louisiana_road] exporting to {out}")
    export_glb(out)


if __name__ == "__main__":
    main()
