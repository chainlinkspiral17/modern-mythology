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
from .geometry import make_box, make_cyl, make_chamfer_box, make_prism, make_lathe

GLASS_DK = (0.26, 0.30, 0.36, 1.0)
RUBBER = (0.12, 0.12, 0.13, 1.0)
RIM = (0.66, 0.68, 0.70, 1.0)
CHROME = (0.74, 0.76, 0.78, 1.0)
DARK = (0.10, 0.10, 0.11, 1.0)


def _frame(cx, cy, along):
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
    # prism polygon plane for axis across the car: along X → extrude on Y, polygon (u=x, v=z)
    make_prism(f"{prefix}_Body", P(0.0, 0.0, 0.0), prof_abs, 2 * hw - 0.04, col, axis=side_axis)
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
    make_box(f"{prefix}_Windshield", P(ws_u + 0.02, 0.0, ws_z), S(0.03, 2 * hw - 0.40, ws_h), glass)
    if not pickup:
        rg_u = tail + 0.60 if hatch else tail + 0.85
        make_box(f"{prefix}_Rear_Glass", P(rg_u, 0.0, ws_z - 0.02), S(0.03, 2 * hw - 0.44, ws_h - 0.06), glass)
    else:
        make_box(f"{prefix}_Rear_Glass", P(nose - 3.44, 0.0, z0 + 1.36), S(0.03, 2 * hw - 0.44, 0.44), glass)
    for sgn, nm in ((1, "L"), (-1, "R")):
        make_box(f"{prefix}_Side_Glass_{nm}", P((cab_u0 + cab_u1) / 2.0, sgn * (hw - 0.005), z0 + 1.25),
                 S(cab_u1 - cab_u0 - 0.30, 0.02, 0.36), glass)
        make_box(f"{prefix}_Pillar_B_{nm}", P((cab_u0 + cab_u1) / 2.0, sgn * (hw + 0.006), z0 + 1.25), S(0.06, 0.012, 0.36), trim)
        # door seams + handles + rocker
        for si, du in enumerate((0.0, -1.05)):
            make_box(f"{prefix}_Door_Seam_{nm}_{si}", P(cab_u1 - 0.25 + du, sgn * (hw + 0.003), z0 + 0.72), S(0.012, 0.006, 0.56), DARK)
            make_box(f"{prefix}_Door_Handle_{nm}_{si}", P(cab_u1 - 0.45 + du, sgn * (hw + 0.012), z0 + 0.92), S(0.14, 0.02, 0.03), CHROME)
        make_box(f"{prefix}_Rocker_{nm}", P(0.0, sgn * (hw - 0.02 + 0.005), z0 + 0.45), S(L - 1.2, 0.02, 0.08), DARK)
        # mirror on its arm
        make_box(f"{prefix}_Mirror_Arm_{nm}", P(ws_u - 0.15, sgn * (hw + 0.08), z0 + 1.08), S(0.05, 0.16, 0.03), trim)
        make_chamfer_box(f"{prefix}_Mirror_{nm}", P(ws_u - 0.15, sgn * (hw + 0.20), z0 + 1.10), S(0.10, 0.10, 0.14), col, chamfer=0.02)
        # lights
        make_box(f"{prefix}_Headlight_{nm}", P(nose + 0.006, sgn * 0.55, z0 + 0.72), S(0.012, 0.36, 0.16), (0.90, 0.90, 0.82, 1.0))
        make_box(f"{prefix}_Taillight_{nm}", P(tail - 0.006, sgn * 0.62, z0 + 0.82), S(0.012, 0.28, 0.14), (0.78, 0.14, 0.10, 1.0))
    # ── nose: grille slats, plate, bumpers
    for gi in range(4):
        make_box(f"{prefix}_Grille_{gi}", P(nose + 0.004, 0.0, z0 + 0.60 + gi * 0.06), S(0.008, 0.90, 0.025), DARK)
    make_box(f"{prefix}_Plate", P(nose + 0.008, 0.0, z0 + 0.50), S(0.008, 0.30, 0.15), (0.90, 0.88, 0.82, 1.0))
    make_chamfer_box(f"{prefix}_Bumper_F", P(nose + 0.08, 0.0, z0 + 0.44), S(0.14, 2 * hw - 0.02, 0.16), CHROME, chamfer=0.03)
    make_chamfer_box(f"{prefix}_Bumper_R", P(tail - 0.08, 0.0, z0 + 0.44), S(0.14, 2 * hw - 0.02, 0.16), CHROME, chamfer=0.03)
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
        make_chamfer_box(f"{prefix}_Light_Bar", P(ws_u - 0.55, 0.0, z0 + 1.55), S(0.28, 1.10, 0.10), DARK, chamfer=0.02)
        make_box(f"{prefix}_Light_Bar_Red", P(ws_u - 0.55, 0.32, z0 + 1.55), S(0.30, 0.30, 0.11), (0.72, 0.12, 0.10, 1.0))
        make_box(f"{prefix}_Light_Bar_Blue", P(ws_u - 0.55, -0.32, z0 + 1.55), S(0.30, 0.30, 0.11), (0.14, 0.24, 0.74, 1.0))
    # ── wheels: outside the body's width
    for wi, (wu, wv) in enumerate(((-L * 0.32, -(hw + 0.14)), (L * 0.32, -(hw + 0.14)), (-L * 0.32, hw + 0.14), (L * 0.32, hw + 0.14))):
        _wheel(f"{prefix}_Wheel_{wi}", P, cx, cy, wu, wv, z0, along)
