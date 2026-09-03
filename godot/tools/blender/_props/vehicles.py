"""Parked vehicles for exteriors — non-intersecting by construction.

Promoted from build_meadowlark_circle.py (2026-09-03) after the cab,
the lake truck, the vigil sedan and the Henderson curb each
re-derived the same bands: body block, cabin block, glass PLATES
outside the cabin, wheels OUTSIDE the body. Nothing here crosses
anything else, so the overlap audit stays quiet.

    make_car(prefix, cx, cy, length, col, pickup=False, hatch=False,
             light_bar=False, along="X", z0=0.0)

`along` is the axis the car's length runs on ("X" or "Y"); the nose
is toward +axis. `z0` is the ground the wheels stand on. `hatch`
lengthens the cabin to the tail (a Civic); `pickup` adds a cab, bed
sides and a tailgate; `light_bar` a patrol bar.
"""
from .geometry import make_box, make_cyl

GLASS_DK = (0.26, 0.30, 0.36, 1.0)
RUBBER = (0.14, 0.14, 0.15, 1.0)


def make_car(prefix, cx, cy, length, col, pickup=False, hatch=False, light_bar=False, along="X", z0=0.0):
    hw = 0.90
    if along == "X":
        def P(u, v, z): return (cx + u, cy + v, z)
        def S(l, w, h): return (l, w, h)
        wheel_axis = "Y"
    else:
        def P(u, v, z): return (cx + v, cy + u, z)
        def S(l, w, h): return (w, l, h)
        wheel_axis = "X"
    make_box(f"{prefix}_Body", P(0.0, 0.0, z0 + 0.62), S(length, 2 * hw, 0.60), col)
    if pickup:
        make_box(f"{prefix}_Cab", P(0.55, 0.0, z0 + 1.27), S(2.0, 2 * hw, 0.70), col)
        make_box(f"{prefix}_Windshield", P(1.57, 0.0, z0 + 1.30), S(0.02, 1.60, 0.50), GLASS_DK)
        for sgn, nm in ((1, "L"), (-1, "R")):
            make_box(f"{prefix}_Side_Glass_{nm}", P(0.55, sgn * 0.91, z0 + 1.30), S(1.70, 0.02, 0.50), GLASS_DK)
            make_box(f"{prefix}_Bed_Side_{nm}", P(-1.35, sgn * (hw - 0.02), z0 + 1.12), S(1.8, 0.04, 0.40), col)
        make_box(f"{prefix}_Tailgate", P(-length / 2.0 + 0.03, 0.0, z0 + 1.12), S(0.06, 2 * hw - 0.10, 0.40), col)
    else:
        cab_len = 2.60 if hatch else 2.20
        cab_u = -0.40 if hatch else -0.20
        make_box(f"{prefix}_Cabin", P(cab_u, 0.0, z0 + 1.13), S(cab_len, 2 * hw - 0.30, 0.42), col)
        nose = cab_u + cab_len / 2.0
        tail = cab_u - cab_len / 2.0
        # a 3 cm gap between the cabin block and the windshield plate leaves
        # room for a phone on the dash (Jesse's, ch14)
        make_box(f"{prefix}_Windshield", P(nose + 0.04, 0.0, z0 + 1.15), S(0.02, 1.40, 0.30), GLASS_DK)
        make_box(f"{prefix}_Rear_Glass", P(tail - 0.01, 0.0, z0 + 1.15), S(0.02, 1.40, 0.30), GLASS_DK)
        for sgn, nm in ((1, "L"), (-1, "R")):
            make_box(f"{prefix}_Side_Glass_{nm}", P(cab_u, sgn * 0.76, z0 + 1.15), S(cab_len - 0.30, 0.02, 0.30), GLASS_DK)
    if light_bar:
        make_box(f"{prefix}_Light_Bar", P(-0.20, 0.0, z0 + 1.40), S(0.30, 1.10, 0.12), (0.16, 0.16, 0.18, 1.0))
        make_box(f"{prefix}_Light_Bar_Red", P(-0.20, 0.30, z0 + 1.40), S(0.32, 0.30, 0.13), (0.70, 0.12, 0.10, 1.0))
        make_box(f"{prefix}_Light_Bar_Blue", P(-0.20, -0.30, z0 + 1.40), S(0.32, 0.30, 0.13), (0.14, 0.24, 0.72, 1.0))
    for wi, (wu, wv) in enumerate(((-length * 0.32, -1.03), (length * 0.32, -1.03), (-length * 0.32, 1.03), (length * 0.32, 1.03))):
        make_cyl(f"{prefix}_Wheel_{wi}", P(wu, wv, z0 + 0.33), 0.33, 0.25, RUBBER, axis=wheel_axis, segments=10)
