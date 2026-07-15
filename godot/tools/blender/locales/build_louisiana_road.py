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
    (+4.2, 2.0, 2.9), (+4.2, 10.0, 2.9),                        # east verge
]


def build_road():
    # Road runs N-S along Y axis. Half-width 2m.
    # Asphalt
    make_box("Asphalt", (0.0, 6.0, 0.0), (4.0, 24.0, 0.04), COL_ASPHALT)
    # Center yellow dashed line
    for di in range(11):
        dy = -5.0 + di*1.40
        make_box(f"CenterLine_{di}", (0.0, dy, 0.022), (0.10, 0.60, 0.005), COL_LANE_LINE)
    # White edge lines
    for sgn in (-1, +1):
        make_box(f"EdgeLine_{sgn:+d}", (sgn*1.85, 6.0, 0.022), (0.06, 24.0, 0.005), (0.92, 0.92, 0.86, 1.0))
    # Dirt shoulders
    for sgn in (-1, +1):
        make_box(f"Shoulder_{sgn:+d}", (sgn*2.50, 6.0, 0.02), (0.80, 24.0, 0.04), COL_DIRT_SHOULDER)


def build_grass_and_swamp():
    # Grass strips west of west shoulder; swamp east of east shoulder
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
        (-8.5, 1.0, 6.5), (-9.0, 4.5, 7.0), (-7.5, 8.0, 5.8),
        (-9.5, 11.5, 6.8), (-8.0, 15.0, 7.2), (-9.0, 18.0, 6.0),
        (+9.0, 2.0, 7.0), (+9.5, 6.0, 6.5), (+9.0, 10.5, 7.5),
        (+9.5, 14.0, 6.0), (+10.5, 17.0, 6.5),
    ]
    for ti, (tx, ty, th) in enumerate(positions):
        # Trunk (buttressed base wider than top)
        make_cyl(f"Cypress_{ti}_TrunkBase", (tx, ty, 0.50), 0.60, 1.00, COL_CYPRESS_TRUNK, segments=10)
        make_cyl(f"Cypress_{ti}_Trunk", (tx, ty, th/2.0 + 1.0), 0.30, th, COL_CYPRESS_TRUNK, segments=10)
        # Foliage clusters (3 stacked)
        for fi in range(3):
            fr = 1.40 - fi*0.30
            fz = th + 1.0 + fi*0.80
            make_cyl(f"Cypress_{ti}_Foliage_{fi}", (tx, ty, fz), fr, 1.20, COL_CYPRESS_FOLIAGE, segments=10)
        # Spanish moss strands hanging
        for mi in range(3):
            mx = tx + (mi - 1) * 0.30
            mz = th + 0.8
            make_box(f"Cypress_{ti}_Moss_{mi}", (mx, ty, mz - 0.80), (0.04, 0.04, 1.20), COL_SPANISH_MOSS)


def build_signs_and_markers():
    # Mile-marker reflectors along edge
    for mi in range(6):
        my = -2.0 + mi*3.5
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
    # Large sky-color plane far behind (north) — at distance acts as horizon backdrop
    make_box("SkyBackdrop", (0.0, 24.0, 6.0), (40.0, 0.04, 12.0), COL_SKY)
    # A few cloud puffs
    for ci, (cx, cz) in enumerate([(-8.0, 8.0), (-2.0, 9.5), (5.0, 8.5), (12.0, 9.0)]):
        make_cyl(f"Cloud_{ci}", (cx, 23.9, cz), 1.40, 0.20, (0.26, 0.28, 0.36, 1.0), axis='Y', segments=10)




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
    pole_ys = [-2.0, 4.0, 10.0, 16.0, 22.0]
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
    # ── Guardrail on the SWAMP (west) side, x=-2.5, dented ──
    for i in range(9):
        gy = -3.0 + i * 3.0
        dent = 0.05 if i == 5 else 0.0   # one bashed post
        make_box(f"Guardrail_Beam_{i}", (-2.5 - dent, gy + 1.5, 0.55),
                 (0.04, 3.0, 0.16), steel)
        make_cyl(f"Guardrail_Post_{i}", (-2.5, gy, 0.28), 0.05, 0.56,
                 steel_dk, segments=5)
    # ── Stalled sedan on the WEST shoulder, nosed north ──
    cxp, cyp = -3.1, 8.0
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
    # ── Cattail reed clumps in the swamp (west of guardrail) ──
    for i, (rx, ry) in enumerate([(-5.5, 2.0), (-6.2, 9.0), (-4.8, 15.0),
                                  (-7.0, 20.0), (-5.0, -4.0)]):
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
                   (16.5, 'two_story', COL_HOUSE_GRY)]
    for i, (hy, style, col) in enumerate(east_houses):
        _make_house(f"HouseE_{i}", 14.5, hy, -1, style, col)
    # ── Driveways (curb-cut apron to each west house) + one parked car ──
    for i, (hy, _s, _c) in enumerate(west_houses):
        make_box(f"DriveW_{i}", (-6.8, hy, 0.032), (6.0, 2.6, 0.05), COL_DRIVEWAY)
        make_box(f"DriveApron_W_{i}", (-3.2, hy, 0.031), (1.6, 2.2, 0.04), COL_DRIVEWAY)
    # parked sedan on the middle west driveway (nosed toward the house)
    cxp, cyp = -8.2, 6.5
    make_box("Parked_Body", (cxp, cyp, 0.5), (2.0, 4.2, 0.6), (0.20, 0.28, 0.40, 1.0))
    make_box("Parked_Cabin", (cxp, cyp - 0.2, 1.05), (1.7, 2.2, 0.5), (0.16, 0.22, 0.32, 1.0))
    make_box("Parked_Windshield", (cxp, cyp + 0.85, 1.06), (1.5, 0.05, 0.42), (0.30, 0.36, 0.42, 1.0))
    for wx in (-0.8, 0.8):
        for wy in (-1.5, 1.5):
            make_cyl(f"Parked_Wheel_{wx:+.0f}_{wy:+.0f}", (cxp + wx, cyp + wy, 0.32),
                     0.34, 0.28, (0.08, 0.08, 0.09, 1.0), segments=8, axis='X')
    # ── Mailboxes on posts at each west driveway mouth ──
    for i, (hy, _s, _c) in enumerate(west_houses):
        make_cyl(f"Mailbox_Post_{i}", (-3.1, hy + 1.4, 0.55), 0.05, 1.1, COL_MAIL_POST, segments=6)
        make_box(f"Mailbox_Box_{i}", (-3.1, hy + 1.4, 1.15), (0.24, 0.42, 0.24), COL_MAILBOX)
        make_box(f"Mailbox_Flag_{i}", (-2.95, hy + 1.2, 1.2), (0.02, 0.04, 0.14), COL_SIGN_RED)
    # ── Sprinklers on the west lawns: heads + faint arcing spray ──
    for i, (sx, sy) in enumerate([(-9.0, 0.0), (-7.5, 8.0), (-10.0, 15.0)]):
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


def main():
    clear_scene()
    build_sky_backdrop()
    build_road()
    build_grass_and_swamp()
    build_cypress_trees()
    build_signs_and_markers()
    build_roadside_detail()
    build_suburban_street()
    out = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "../../../assets/3d/locales/louisiana_road.glb"))
    print(f"\n[build_louisiana_road] exporting to {out}")
    export_glb(out)


if __name__ == "__main__":
    main()
