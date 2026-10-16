"""Houses and small buildings with real silhouettes.

DETAIL DRAFT 1 (2026-09-05). Every subdivision house in the project
was a box with a slab on top and a row of window boxes. This module
builds a house the way a house reads at a distance: a gable roof
with EAVES that overhang the walls (a prism with the roof profile,
plus a ridge cap and shingle courses), siding COURSES on the walls
(thin strips that catch the light), window TRIM with a sill, a
mullion and shutters, a paneled door with a knob under a porch on
turned posts, a chimney with a cap, gutters with downspouts, a
foundation line, a garage with a paneled door and its apron, and
foundation shrubs.

    make_ranch_house(prefix, cx, cy, front, wall_col, roof_col,
                     w=11.0, d=8.0, h=2.9, garage=True,
                     lit=(False, True, False), porch=True,
                     two_story=False, shrubs=True)

`front` is the side the door is on: "+Y", "-Y", "+X" or "-X". `w`
runs along the front, `d` is the depth. Names carry the prefix so
cues find them (Door, Window, Garage, Porch, Chimney, Shrub).
"""
from .geometry import make_box, make_cyl, make_chamfer_box, make_prism, make_lathe, make_tube

TRIM = (0.92, 0.90, 0.86, 1.0)
GLASS = (0.55, 0.62, 0.70, 0.55)
GLASS_LIT = (0.98, 0.86, 0.58, 0.9)
GUTTER = (0.80, 0.80, 0.78, 1.0)
CONCRETE = (0.62, 0.61, 0.58, 1.0)
SHRUB = (0.26, 0.40, 0.24, 1.0)
DOOR_COL = (0.40, 0.28, 0.20, 1.0)


def _frame(cx, cy, front):
    """Local (u along the front, v toward the front, z) → world."""
    if front == "+Y":
        return (lambda u, v, z: (cx + u, cy + v, z)), (lambda a, b, h: (a, b, h)), "X", 1
    if front == "-Y":
        return (lambda u, v, z: (cx - u, cy - v, z)), (lambda a, b, h: (a, b, h)), "X", -1
    if front == "+X":
        return (lambda u, v, z: (cx + v, cy - u, z)), (lambda a, b, h: (b, a, h)), "Y", 1
    return (lambda u, v, z: (cx - v, cy + u, z)), (lambda a, b, h: (b, a, h)), "Y", -1


def make_ranch_house(prefix, cx, cy, front, wall_col, roof_col, w=11.0, d=8.0, h=2.9,
                     garage=True, lit=(False, True, False), porch=True, two_story=False, shrubs=True):
    P, S, ridge_axis, sign = _frame(cx, cy, front)
    if two_story:
        h = h * 1.9
    fv = d / 2.0                       # the front face, in v
    dark = (wall_col[0] * 0.72, wall_col[1] * 0.72, wall_col[2] * 0.72, 1.0)
    roof_dk = (roof_col[0] * 0.8, roof_col[1] * 0.8, roof_col[2] * 0.8, 1.0)
    roof_lt = (min(1.0, roof_col[0] * 1.15), min(1.0, roof_col[1] * 1.15), min(1.0, roof_col[2] * 1.15), 1.0)
    # ── body + foundation
    make_box(f"{prefix}_Slab", P(0.0, 0.0, 0.06), S(w + 0.4, d + 0.4, 0.12), CONCRETE)
    make_box(f"{prefix}_Body", P(0.0, 0.0, 0.12 + h / 2.0), S(w, d, h), wall_col)
    make_box(f"{prefix}_Foundation_Line", P(0.0, fv + 0.003, 0.30), S(w + 0.01, 0.006, 0.36), dark)
    # ── siding courses: front, and every other course on the ends
    for k in range(int(h / 0.24)):
        z = 0.14 + 0.24 * k
        make_box(f"{prefix}_Siding_F_{k}", P(0.0, fv + 0.008, z), S(w - 0.02, 0.012, 0.03), dark)
    for sgn, nm in ((1, "A"), (-1, "B")):
        for k in range(0, int(h / 0.24), 2):
            z = 0.14 + 0.24 * k
            make_box(f"{prefix}_Siding_{nm}_{k}", P(sgn * (w / 2.0 + 0.008), 0.0, z), S(0.012, d - 0.02, 0.03), dark)
    # ── roof: a gable profile across the depth, ridge along the front, with eaves
    eave = 0.55
    rise = d * 0.28
    z_e = 0.12 + h
    prof_v = [(-fv - eave, z_e - 0.10), (fv + eave, z_e - 0.10), (fv + eave, z_e + 0.02), (0.0, z_e + rise), (-fv - eave, z_e + 0.02)]
    # the prism polygon lives in the plane perpendicular to the ridge:
    #   ridge X → polygon (y, z); ridge Y → polygon (x, z). v maps to
    #   world y (±) for X-ridges and world x (±) for Y-ridges.
    vsign = sign if ridge_axis == "X" else sign
    poly = [(vsign * v, z) for (v, z) in prof_v]
    make_prism(f"{prefix}_Roof", (cx, cy, 0.0), poly, w + 0.9, roof_col, axis=ridge_axis)
    make_box(f"{prefix}_Ridge_Cap", P(0.0, 0.0, z_e + rise + 0.03), S(w + 0.94, 0.30, 0.06), roof_dk)
    n_courses = 6
    for k in range(1, n_courses):
        t = k / float(n_courses)
        vk = (fv + eave) - t * (fv + eave)
        zk = z_e + 0.02 + t * (rise - 0.02) + 0.012
        make_box(f"{prefix}_Shingle_Course_{k}", P(0.0, vk, zk), S(w + 0.9, 0.05, 0.012), roof_lt)
    for sgn, nm in ((1, "A"), (-1, "B")):
        make_box(f"{prefix}_Gable_Trim_{nm}", P(sgn * (w / 2.0 + 0.46), 0.0, z_e + rise / 2.0), S(0.04, d + 2 * eave, 0.16), TRIM)
    # gutters + downspouts
    make_box(f"{prefix}_Gutter_F", P(0.0, fv + eave + 0.03, z_e - 0.12), S(w + 0.9, 0.08, 0.08), GUTTER)
    make_box(f"{prefix}_Gutter_B", P(0.0, -(fv + eave + 0.03), z_e - 0.12), S(w + 0.9, 0.08, 0.08), GUTTER)
    for sgn, nm in ((1, "A"), (-1, "B")):
        make_tube(f"{prefix}_Downspout_{nm}", [P(sgn * (w / 2.0 + 0.40), fv + eave + 0.03, z_e - 0.16),
                                               P(sgn * (w / 2.0 + 0.40), fv + 0.10, z_e - 0.30),
                                               P(sgn * (w / 2.0 + 0.40), fv + 0.10, 0.25)], 0.035, GUTTER, segments=6)
    # ── chimney
    make_box(f"{prefix}_Chimney", P(-w * 0.30, -d * 0.15, z_e + rise * 0.55 + 0.6), S(0.7, 0.7, rise + 1.2), (0.46, 0.32, 0.26, 1.0))
    make_box(f"{prefix}_Chimney_Cap", P(-w * 0.30, -d * 0.15, z_e + rise * 0.55 + 1.24), S(0.9, 0.9, 0.08), (0.36, 0.26, 0.22, 1.0))
    # ── windows on the front
    wins = [0.8, 3.6] if garage else [-3.2, 0.8, 3.6]
    for wi, wu in enumerate(wins):
        on = lit[wi % len(lit)]
        wz = 1.55
        make_box(f"{prefix}_Window_{wi}_Trim", P(wu, fv + 0.02, wz), S(1.60, 0.04, 1.30), TRIM)
        make_box(f"{prefix}_Window_{wi}_Glass", P(wu, fv + 0.045, wz), S(1.42, 0.01, 1.12), GLASS_LIT if on else GLASS)
        make_box(f"{prefix}_Window_{wi}_Mullion_V", P(wu, fv + 0.052, wz), S(0.04, 0.004, 1.12), TRIM)
        make_box(f"{prefix}_Window_{wi}_Mullion_H", P(wu, fv + 0.052, wz), S(1.42, 0.004, 0.04), TRIM)
        make_box(f"{prefix}_Window_{wi}_Sill", P(wu, fv + 0.06, wz - 0.68), S(1.72, 0.10, 0.06), TRIM)
        for sgn in (-1, 1):
            make_box(f"{prefix}_Window_{wi}_Shutter_{sgn:+d}", P(wu + sgn * 1.02, fv + 0.03, wz), S(0.36, 0.05, 1.30), dark)
    # ── the door, the porch
    du = -2.0 if garage else 0.0
    make_box(f"{prefix}_Door_Trim", P(du, fv + 0.02, 1.10), S(1.10, 0.04, 2.20), TRIM)
    make_box(f"{prefix}_Door", P(du, fv + 0.05, 1.05), S(0.95, 0.04, 2.10), DOOR_COL)
    for pi, pz in enumerate((0.55, 1.30)):
        make_box(f"{prefix}_Door_Panel_{pi}", P(du, fv + 0.075, pz), S(0.60, 0.01, 0.55), (DOOR_COL[0] * 0.8, DOOR_COL[1] * 0.8, DOOR_COL[2] * 0.8, 1.0))
    make_box(f"{prefix}_Door_Knob", P(du + 0.36, fv + 0.095, 1.02), S(0.05, 0.05, 0.05), (0.78, 0.68, 0.36, 1.0))
    make_box(f"{prefix}_Porch_Fixture", P(du + 0.75, fv + 0.10, 2.25), S(0.14, 0.14, 0.24), (0.86, 0.84, 0.78, 1.0))
    if porch:
        make_box(f"{prefix}_Porch_Slab", P(du, fv + 0.95, 0.12), S(2.6, 1.8, 0.24), CONCRETE)
        make_box(f"{prefix}_Porch_Step", P(du, fv + 2.0, 0.06), S(1.4, 0.4, 0.12), CONCRETE)
        make_box(f"{prefix}_Porch_Roof", P(du, fv + 1.0, z_e - 0.30), S(3.0, 2.2, 0.12), roof_col)
        post_h = z_e - 0.36 - 0.24
        for sgn in (-1, 1):
            make_lathe(f"{prefix}_Porch_Post_{sgn:+d}", P(du + sgn * 1.25, fv + 1.75, 0.24),
                       [(0.07, 0.0), (0.07, 0.12), (0.05, 0.16), (0.05, post_h - 0.06), (0.07, post_h - 0.02), (0.07, post_h)],
                       TRIM, segments=8)
    # ── garage
    if garage:
        gu = -w * 0.5 + 1.9
        make_box(f"{prefix}_Garage_Header", P(gu, fv + 0.03, 2.35), S(3.0, 0.06, 0.20), TRIM)
        make_box(f"{prefix}_Garage_Door", P(gu, fv + 0.03, 1.12), S(2.7, 0.05, 2.24), (0.88, 0.86, 0.82, 1.0))
        for gi in range(4):
            make_box(f"{prefix}_Garage_Panel_{gi}", P(gu, fv + 0.062, 0.32 + gi * 0.55), S(2.5, 0.01, 0.40), (0.80, 0.78, 0.74, 1.0))
        make_box(f"{prefix}_Garage_Apron", P(gu, fv + 1.6, 0.015), S(3.2, 3.0, 0.03), CONCRETE)
    # ── foundation shrubs
    if shrubs:
        for si, su in enumerate((1.9, 2.5, 4.6)):
            make_lathe(f"{prefix}_Shrub_{si}", P(su, fv + 0.55, 0.12),
                       [(0.0, 0.0), (0.38, 0.12), (0.46, 0.40), (0.34, 0.70), (0.0, 0.84)], SHRUB, segments=8)


def make_shed(prefix, cx, cy, front="+X", w=3.0, d=2.4, h=2.3, wall_col=(0.50, 0.46, 0.40, 1.0), roof_col=(0.56, 0.58, 0.58, 1.0)):
    """A small outbuilding: body, gable with eaves, a door with a hasp,
    corner boards, board courses."""
    P, S, ridge_axis, sign = _frame(cx, cy, front)
    fv = d / 2.0
    dark = (wall_col[0] * 0.7, wall_col[1] * 0.7, wall_col[2] * 0.7, 1.0)
    make_box(f"{prefix}_Body", P(0.0, 0.0, h / 2.0), S(w, d, h), wall_col)
    for k in range(int(h / 0.22)):
        make_box(f"{prefix}_Course_{k}", P(0.0, fv + 0.006, 0.12 + 0.22 * k), S(w - 0.02, 0.01, 0.025), dark)
    prof_v = [(-fv - 0.3, h - 0.06), (fv + 0.3, h - 0.06), (fv + 0.3, h + 0.02), (0.0, h + d * 0.32), (-fv - 0.3, h + 0.02)]
    poly = [(sign * v, z) for (v, z) in prof_v]
    make_prism(f"{prefix}_Roof", (cx, cy, 0.0), poly, w + 0.5, roof_col, axis=ridge_axis)
    make_box(f"{prefix}_Door", P(0.0, fv + 0.02, 1.0), S(0.9, 0.04, 2.0), (0.34, 0.30, 0.26, 1.0))
    make_box(f"{prefix}_Hasp", P(0.38, fv + 0.045, 1.05), S(0.08, 0.01, 0.04), (0.50, 0.50, 0.52, 1.0))
    for sgn in (-1, 1):
        make_box(f"{prefix}_Corner_{sgn:+d}", P(sgn * (w / 2.0 - 0.05), fv + 0.008, h / 2.0), S(0.10, 0.012, h - 0.04), (0.60, 0.56, 0.50, 1.0))
