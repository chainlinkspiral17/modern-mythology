import math
"""Parked vehicles for exteriors — non-intersecting by construction.

DRAFT 2 (2026-09-05, user: "basic cubes and rectangles when the
objects and environments need far more detail"): the car is no
longer two boxes. The body is a SIDE-PROFILE PRISM (hood slope,
windshield rake, roofline, rear glass, trunk lid, rocker) extruded
across the width, sitting on a chamfered pan; the wheels are LATHED
(tire with a shoulder, a dished rim, a hub); bumpers are chamfered;
there are door seams, handles, mirrors on arms, head- and
taillights, a grille with slats, a plate, wipers, a roof antenna.
Pickups get a cab profile, a bed with sides, a tailgate, a rear
bumper step; hatches a fastback profile; the light bar stays.

    make_car(prefix, cx, cy, length, col, pickup=False, hatch=False,
             light_bar=False, along="X", z0=0.0, glass_col=None)

`along` is the axis the car's length runs on ("X" or "Y"); the nose
is toward +axis. `z0` is the ground the wheels stand on. Names keep
the DRAFT 1 parts (Body, Cabin→now part of the Body profile but a
"Cabin" glass band remains, Windshield, Rear_Glass, Side_Glass_L/R,
Wheel_0..3) so every existing marker and synonym still lands.
"""
from .geometry import make_box, make_cyl, make_chamfer_box, make_prism, make_lathe, make_rot_box, make_tube

GLASS_DK = (0.26, 0.30, 0.36, 1.0)
RUBBER = (0.12, 0.12, 0.13, 1.0)
RIM = (0.66, 0.68, 0.70, 1.0)
CHROME = (0.74, 0.76, 0.78, 1.0)
DARK = (0.10, 0.10, 0.11, 1.0)


def _frame(cx, cy, along):
    # (2026-10-27) "-Y": along Y with the nose toward -y (vol 1's Judgement Day
    # heading south on the turn of the river)
    if along == "-Y":
        def P(u, v, z): return (cx - v, cy - u, z)
        def S(l, w, h): return (w, l, h)
        return P, S, "X", "X"
    if along == "X":
        def P(u, v, z): return (cx + u, cy + v, z)
        def S(l, w, h): return (l, w, h)
        return P, S, "Y", "Y"
    def P(u, v, z): return (cx + v, cy + u, z)
    def S(l, w, h): return (w, l, h)
    return P, S, "X", "X"


def _wheel(prefix, P, cx, cy, u, v, z0, along, r=0.33, w=0.24):
    """Lathed tire + rim + hub, axis across the car."""
    # the lathe revolves about Z; a wheel needs its axis across the
    # car, so it is built as a short cylinder stack instead: tire
    # (rubber), a slightly narrower shoulder, the dished rim, the hub.
    axis = "Y" if along == "X" else "X"
    make_cyl(f"{prefix}_Tire", P(u, v, z0 + r), r, w, RUBBER, axis=axis, segments=14)
    off = (w / 2.0 + 0.004) * (1 if v > 0 else -1)
    make_cyl(f"{prefix}_Rim", P(u, v + off, z0 + r), r * 0.62, 0.008, RIM, axis=axis, segments=10)
    make_cyl(f"{prefix}_Hub", P(u, v + off * 1.06, z0 + r), r * 0.18, 0.012, DARK, axis=axis, segments=8)


CAR_HALF_W = 0.88


def curb_park(road_c, road_half_w, along, side, u, gap=0.12):
    """Where a car's centre goes to sit AT THE CURB of a straight road
    (2026-09-07 · "cars don't park in the middle of streets. this keeps
    happening"). road_c: the road's centreline coordinate ACROSS the
    road (y for an along-X road, x for along-Y); road_half_w: half the
    asphalt width; side: +1 / -1 (which curb); u: position ALONG the
    road; gap: clearance between the tire and the curb face. Returns
    (cx, cy) for make_car(..., along=along). Feed the result to
    make_car so the LANE check in furniture_grammar_audit stays quiet."""
    across = road_c + side * (road_half_w - gap - CAR_HALF_W)
    if along == "X":
        return (u, across)
    return (across, u)


def bulb_park(bulb_cx, bulb_cy, bulb_r, angle_deg, along, gap=0.12):
    """The curb of a cul-de-sac bulb: the car centre CAR_HALF_W + gap
    inside the radius at `angle_deg`. The car still runs along X or Y
    (this pipeline's cars are axis-aligned), so pick an angle near a
    cardinal direction for a believable parallel park."""
    a = math.radians(angle_deg)
    rr = bulb_r - gap - CAR_HALF_W
    return (bulb_cx + math.cos(a) * rr, bulb_cy + math.sin(a) * rr)


def _audit_body(prefix, P, S, nose, tail, hw, z0, cab_u0, cab_u1, roof, deck):
    """THE AUDITS READ A PRISM AS ITS BOUNDING BOX (pass 372). Over a pickup's
    bed or a sedan's hood that box is air up to the roof line: anything lying
    there read as "inside the body", and a camera above the bed as inside the
    truck (pass 364 took a phone off a hood for it; the Gas & Go's envelope
    "flat in the pickup's bed" could not be framed). Under the audit stubs
    the body is recorded as it stands — a low box the whole length (pan to
    deck) and a tall one over the cab. In Blender this does nothing."""
    import sys
    A = sys.modules.get("locale_geometry_audit")
    boxes = getattr(A, "BOXES", None) if A is not None else None
    if boxes is None:
        return
    name = f"{prefix}_Body"
    for k in range(len(boxes) - 1, -1, -1):
        if boxes[k][0] == name:
            del boxes[k]
            break
    else:
        return
    half = lambda t: tuple(abs(float(x)) for x in t)
    # the profile's own length (tail + 0.10 .. nose): the bumper, grille and
    # lamps sit ON the nose face and must still touch it
    boxes.append((name, P((nose + tail) / 2.0 + 0.05, 0.0, z0 + (0.42 + deck) / 2.0),
                  half(S((nose - tail - 0.10) / 2.0, hw - 0.02, (deck - 0.42) / 2.0))))
    boxes.append((name + "_Cab", P((cab_u0 + cab_u1) / 2.0, 0.0, z0 + (deck + roof) / 2.0),
                  half(S(abs(cab_u1 - cab_u0) / 2.0, hw - 0.02, (roof - deck) / 2.0))))


def make_car(prefix, cx, cy, length, col, pickup=False, hatch=False, light_bar=False, along="X", z0=0.0, glass_col=None):
    glass = glass_col or GLASS_DK
    P, S, side_axis, wheel_axis = _frame(cx, cy, along)
    L = length
    hw = 0.88
    trim = (max(0.08, col[0] * 0.55), max(0.08, col[1] * 0.55), max(0.08, col[2] * 0.55), 1.0)
    # ── the body: a side profile (u along the length, w up) extruded across the width
    #    z values are relative to z0; the pan sits at 0.30..0.42
    nose, tail = L / 2.0, -L / 2.0
    if pickup:
        # hood to a cab, then the bed
        prof = [(tail + 0.10, 0.42), (nose - 0.05, 0.42), (nose, 0.62), (nose - 0.08, 0.98),
                (nose - 1.55, 1.02), (nose - 1.85, 1.10), (nose - 2.25, 1.62), (nose - 2.40, 1.70),
                (nose - 3.35, 1.70), (nose - 3.45, 1.62), (nose - 3.45, 1.02), (tail + 0.10, 0.98)]
    elif hatch:
        prof = [(tail + 0.10, 0.42), (nose - 0.05, 0.42), (nose, 0.60), (nose - 0.10, 0.92),
                (nose - 1.10, 0.96), (nose - 1.85, 1.44), (nose - 2.10, 1.48), (tail + 0.90, 1.44),
                (tail + 0.20, 1.10), (tail + 0.10, 0.96)]
    else:
        prof = [(tail + 0.10, 0.42), (nose - 0.05, 0.42), (nose, 0.60), (nose - 0.10, 0.92),
                (nose - 1.10, 0.96), (nose - 1.70, 1.42), (nose - 1.95, 1.46), (tail + 1.35, 1.46),
                (tail + 1.15, 1.42), (tail + 0.55, 1.02), (tail + 0.10, 0.98)]
    prof_abs = [(u, z0 + z) for (u, z) in prof]
    if along == "-Y":
        # the prism lays its profile along +y whatever P does: mirror it so the
        # hood is at the nose (2026-10-30: Judgement Day on the turn had its
        # body facing north and its grille and headlights hanging off the tail)
        prof_abs = [(-u, z) for (u, z) in prof_abs]
    # prism polygon plane for axis across the car: along X → extrude on Y, polygon (u=x, v=z)
    # the winding reference (the prism's centre) must sit INSIDE the body: at
    # z 0 it was above the roof of a car set below the origin (2026-10-31, the
    # curtain call's por puesto at z0 -3.2 under a second-floor window drew
    # roofless from above: the roof faces wound inward and culled)
    zr = z0 + 0.70
    make_prism(f"{prefix}_Body", P(0.0, 0.0, zr), [(u, z - zr) for (u, z) in prof_abs], 2 * hw - 0.04, col, axis=side_axis)
    make_chamfer_box(f"{prefix}_Pan", P(0.0, 0.0, z0 + 0.36), S(L - 0.40, 2 * hw - 0.20, 0.12), DARK, chamfer=0.03)
    # ── glass: plates just outside the body's glass band
    if pickup:
        ws_u, ws_z, ws_h = nose - 2.05, z0 + 1.36, 0.52
        cab_u0, cab_u1 = nose - 3.40, nose - 2.30
    elif hatch:
        ws_u, ws_z, ws_h = nose - 1.48, z0 + 1.20, 0.48
        cab_u0, cab_u1 = tail + 0.95, nose - 1.10
    else:
        ws_u, ws_z, ws_h = nose - 1.40, z0 + 1.19, 0.46
        cab_u0, cab_u1 = tail + 1.30, nose - 1.10
    # the greenhouse BETWEEN the glass: the roof's span, reaching 6 cm under each
    # pane's top edge so the panes touch it. Pillar foot to pillar foot (the
    # first cut) put a brick's face in front of the raked windshield — the cab's
    # own window insert read as hidden behind the car.
    gh0, gh1 = (nose - 3.44, nose - 2.19) if pickup else ((tail + 0.84, nose - 1.79) if hatch else (tail + 1.09, nose - 1.64))
    _audit_body(prefix, P, S, nose, tail, hw, z0, gh0, gh1,
                1.70 if pickup else (1.48 if hatch else 1.46), 1.04 if pickup else 1.00)
    # (2026-11-01) the glass LIES ON the body's rake: a vertical plate half
    # buried in the slope read, from above and in front, as a board stood
    # up on the hood (the curtain call's por puesto, every parked sedan).
    # Each pane follows its profile segment (u, z rel. z0), 2.5 cm proud.
    yaw_u = {"X": 0.0, "Y": math.pi / 2.0, "-Y": -math.pi / 2.0}.get(along, math.pi / 2.0)
    def raked(nm, a, b, width, keep=0.86):
        (ua, za), (ub, zb) = a, b
        slope = (zb - za) / (ub - ua)
        ln = math.hypot(ub - ua, zb - za)
        nrm = 1.0 / math.sqrt(1.0 + slope * slope)
        cu = (ua + ub) / 2.0 - slope * nrm * 0.025
        cz = (za + zb) / 2.0 + nrm * 0.025
        make_rot_box(nm, P(cu, 0.0, z0 + cz), (ln * keep, width, 0.02), glass, yaw=yaw_u, pitch=-math.atan(slope))
    if pickup:
        raked(f"{prefix}_Windshield", (nose - 1.85, 1.10), (nose - 2.25, 1.62), 2 * hw - 0.40)
        make_box(f"{prefix}_Rear_Glass", P(nose - 3.44, 0.0, z0 + 1.36), S(0.03, 2 * hw - 0.44, 0.44), glass)   # the cab's back is upright
    elif hatch:
        raked(f"{prefix}_Windshield", (nose - 1.10, 0.96), (nose - 1.85, 1.44), 2 * hw - 0.40)
        raked(f"{prefix}_Rear_Glass", (tail + 0.20, 1.10), (tail + 0.90, 1.44), 2 * hw - 0.44)
    else:
        raked(f"{prefix}_Windshield", (nose - 1.10, 0.96), (nose - 1.70, 1.42), 2 * hw - 0.40)
        raked(f"{prefix}_Rear_Glass", (tail + 0.55, 1.02), (tail + 1.15, 1.42), 2 * hw - 0.44)
    for sgn, nm in ((1, "L"), (-1, "R")):
        # the body's side is at hw - 0.02: everything on the flank starts
        # there (2026-09-22: handles, pillars and mirrors sat 2 cm off it)
        side = hw - 0.02
        make_box(f"{prefix}_Side_Glass_{nm}", P((cab_u0 + cab_u1) / 2.0, sgn * (side - 0.005), z0 + 1.25),
                 S(cab_u1 - cab_u0 - 0.30, 0.02, 0.36), glass)
        make_box(f"{prefix}_Pillar_B_{nm}", P((cab_u0 + cab_u1) / 2.0, sgn * (side + 0.006), z0 + 1.25), S(0.06, 0.012, 0.36), trim)
        # door seams + handles + rocker
        for si, du in enumerate((0.0, -1.05)):
            make_box(f"{prefix}_Door_Seam_{nm}_{si}", P(cab_u1 - 0.25 + du, sgn * (side + 0.003), z0 + 0.72), S(0.012, 0.006, 0.56), DARK)
            make_box(f"{prefix}_Door_Handle_{nm}_{si}", P(cab_u1 - 0.45 + du, sgn * (side + 0.01), z0 + 0.92), S(0.14, 0.02, 0.03), CHROME)
        make_box(f"{prefix}_Rocker_{nm}", P(0.0, sgn * (side + 0.005), z0 + 0.45), S(L - 1.2, 0.02, 0.08), DARK)
        # mirror on its arm, the arm from the flank
        make_box(f"{prefix}_Mirror_Arm_{nm}", P(ws_u - 0.15, sgn * (side + 0.08), z0 + 1.08), S(0.05, 0.16, 0.03), trim)
        make_chamfer_box(f"{prefix}_Mirror_{nm}", P(ws_u - 0.15, sgn * (side + 0.20), z0 + 1.10), S(0.10, 0.10, 0.14), col, chamfer=0.02)
        # lights
        make_box(f"{prefix}_Headlight_{nm}", P(nose + 0.006, sgn * 0.55, z0 + 0.72), S(0.012, 0.36, 0.16), (0.90, 0.90, 0.82, 1.0))
        # on the body's rear face (the profiles end at tail + 0.10; the
        # lights used to sit 10 cm behind it, in the air)
        make_box(f"{prefix}_Taillight_{nm}", P(tail + 0.10 - 0.006, sgn * 0.62, z0 + 0.82), S(0.012, 0.28, 0.14), (0.78, 0.14, 0.10, 1.0))
    # ── nose: grille slats, plate, bumpers
    for gi in range(4):
        make_box(f"{prefix}_Grille_{gi}", P(nose + 0.004, 0.0, z0 + 0.60 + gi * 0.06), S(0.008, 0.90, 0.025), DARK)
    make_box(f"{prefix}_Plate", P(nose + 0.008, 0.0, z0 + 0.50), S(0.008, 0.30, 0.15), (0.90, 0.88, 0.82, 1.0))
    make_chamfer_box(f"{prefix}_Bumper_F", P(nose + 0.08, 0.0, z0 + 0.44), S(0.14, 2 * hw - 0.02, 0.16), CHROME, chamfer=0.03)
    # on the body's rear face (tail + 0.10); it hung 11 cm behind it (2026-09-22)
    make_chamfer_box(f"{prefix}_Bumper_R", P(tail + 0.035, 0.0, z0 + 0.44), S(0.14, 2 * hw - 0.02, 0.16), CHROME, chamfer=0.03)
    # wipers, antenna
    for wi, dv in enumerate((-0.30, 0.20)):
        make_box(f"{prefix}_Wiper_{wi}", P(ws_u + 0.05, dv, ws_z - ws_h / 2.0 + 0.03), S(0.01, 0.40, 0.012), DARK)
    if not pickup:
        make_cyl(f"{prefix}_Antenna", P(tail + 1.30, hw - 0.30, z0 + 1.46 + 0.16), 0.006, 0.32, DARK, segments=5)
    # ── pickup bed
    if pickup:
        bed_u0, bed_u1 = tail + 0.10, nose - 3.45
        for sgn, nm in ((1, "L"), (-1, "R")):
            make_box(f"{prefix}_Bed_Side_{nm}", P((bed_u0 + bed_u1) / 2.0, sgn * (hw - 0.02 - 0.03), z0 + 1.22),
                     S(bed_u1 - bed_u0, 0.05, 0.44), col)
            make_box(f"{prefix}_Bed_Rail_{nm}", P((bed_u0 + bed_u1) / 2.0, sgn * (hw - 0.05), z0 + 1.46), S(bed_u1 - bed_u0, 0.08, 0.04), trim)
        make_box(f"{prefix}_Tailgate", P(bed_u0 + 0.03, 0.0, z0 + 1.22), S(0.06, 2 * hw - 0.20, 0.44), col)
        make_box(f"{prefix}_Bed_Step", P(tail - 0.04, 0.0, z0 + 0.36), S(0.06, 0.6, 0.06), CHROME)
    if light_bar:
        make_chamfer_box(f"{prefix}_Light_Bar", P(ws_u - 0.55, 0.0, z0 + 1.51), S(0.28, 1.10, 0.10), DARK, chamfer=0.02)   # on the roof (2026-09-22: 4 cm over it)
        make_box(f"{prefix}_Light_Bar_Red", P(ws_u - 0.55, 0.32, z0 + 1.51), S(0.30, 0.30, 0.11), (0.72, 0.12, 0.10, 1.0))
        make_box(f"{prefix}_Light_Bar_Blue", P(ws_u - 0.55, -0.32, z0 + 1.51), S(0.30, 0.30, 0.11), (0.14, 0.24, 0.74, 1.0))
    # ── wheels: outside the body's width
    # (2026-09-22: at hw + 0.14 the tires cleared the body by 4 cm and every kit car floated)
    for wi, (wu, wv) in enumerate(((-L * 0.32, -(hw + 0.08)), (L * 0.32, -(hw + 0.08)), (-L * 0.32, hw + 0.08), (L * 0.32, hw + 0.08))):
        _wheel(f"{prefix}_Wheel_{wi}", P, cx, cy, wu, wv, z0, along)


def make_fishing_boat(prefix, x, y, heading=0.0, *, L=9.0, B=3.0, z0=0.0, hull=(0.84, 0.82, 0.76, 1.0),
                      house=(0.88, 0.88, 0.84, 1.0), trim=(0.20, 0.22, 0.24, 1.0), pots=0, poles=True):
    """(2026-11-02) A West Coast crab / salmon boat, bow toward `heading`
    (radians, 0 = +X), the waterline at z0: a hull in plan (square transom,
    the bow drawn to a point) with its sheer at z0 + 1.0, a dark boot-top at
    the waterline, the wheelhouse forward with its window band and roof, a
    mast with two trolling poles and a boom aft, crab pots stacked on the
    afterdeck. Names stay <prefix>_Hull / _Cabin / _Mast (markers and cues
    that named the old box boats still land)."""
    c, s = math.cos(heading), math.sin(heading)

    def at(u, v, z):
        return (x + u * c - v * s, y + u * s + v * c, z)
    hb, bow = B / 2.0, L * 0.26
    plan = [(-L / 2.0, -hb), (L / 2.0 - bow, -hb), (L / 2.0, 0.0), (L / 2.0 - bow, hb), (-L / 2.0, hb)]
    top, bot = z0 + 1.0, z0 - 0.40
    make_prism(f"{prefix}_Hull", (x, y, (top + bot) / 2.0), plan, top - bot, hull, axis="Z", yaw=heading)
    # the boot-top: a dark band round the hull at the waterline, 3 cm proud
    grow = [(u * (1.0 + 0.06 / L), v * (1.0 + 0.06 / B)) for (u, v) in plan]
    make_prism(f"{prefix}_Boot_Top", (x, y, z0 + 0.08), grow, 0.16, trim, axis="Z", yaw=heading)
    # the rub rail at the sheer
    rail = [(u * (1.0 + 0.05 / L), v * (1.0 + 0.05 / B)) for (u, v) in plan]
    make_prism(f"{prefix}_Rub_Rail", (x, y, top - 0.05), rail, 0.10, trim, axis="Z", yaw=heading)
    # the wheelhouse forward of midships
    wu, wl, ww, wh = L * 0.08, L * 0.30, B * 0.72, 1.55
    make_rot_box(f"{prefix}_Cabin", at(wu, 0.0, top + wh / 2.0), (wl, ww, wh), house, yaw=heading)
    make_rot_box(f"{prefix}_Cabin_Windows", at(wu, 0.0, top + wh * 0.66), (wl + 0.02, ww + 0.02, wh * 0.30), (0.22, 0.28, 0.32, 1.0), yaw=heading)
    make_rot_box(f"{prefix}_Cabin_Roof", at(wu, 0.0, top + wh + 0.04), (wl + 0.30, ww + 0.20, 0.08), trim, yaw=heading)
    # the mast on the wheelhouse roof's aft edge, the boom over the afterdeck
    mu = wu - wl / 2.0 + 0.15
    mz0 = top + wh + 0.08
    make_cyl(f"{prefix}_Mast", at(mu, 0.0, mz0 + 2.2), 0.07, 4.4, trim, segments=6)
    make_tube(f"{prefix}_Boom", [at(mu, 0.0, mz0 + 0.9), at(-L / 2.0 + 0.8, 0.0, top + 1.2)], 0.05, trim, segments=6)
    if poles:
        # the trolling poles, stowed up beside the mast
        for side in (-1, 1):
            make_tube(f"{prefix}_Pole_{'L' if side > 0 else 'R'}", [at(mu + 0.1, side * 0.35, mz0), at(mu - 0.6, side * 1.4, mz0 + 5.6)],
                      0.04, trim, segments=6)
    for k in range(pots):
        pu = -L / 2.0 + 1.2 + (k // 2) * 0.95
        pv = (-0.5 + (k % 2)) * 0.95
        make_rot_box(f"{prefix}_Pot_{k}", at(pu, pv, top + 0.35), (0.85, 0.85, 0.70), (0.30, 0.34, 0.32, 1.0), yaw=heading)
