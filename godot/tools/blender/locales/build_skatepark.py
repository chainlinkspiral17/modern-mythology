"""Skatepark — vol1 ch2's afternoon ("fun just to imagine how the
world could be"). Municipal concrete park, day.

Hero features: the big concrete slab with two half-buried pipe
humps, a grind ledge pair, a flat rail on posts, a three-stair set
with handrail, chain-link fence along the back, a bench, tagged
utility box, and trees over the fence line.

Coordinate frame: Blender Z-up. y=0 is the entry side (camera);
+Y runs north across the slab to the fence. glTF export remaps to
Godot (x, z, -y).

Vantage wired in Background3D.CAMERA_PRESETS:
  skatepark_day — at the slab's south edge looking N across the
  features.
"""
import os, sys, math
_BT = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
if _BT not in sys.path: sys.path.insert(0, _BT)
from _props.geometry import clear_scene, make_box, make_cyl, make_prism, export_glb

COL_SLAB = (0.56, 0.56, 0.54, 1.0)
COL_SLAB_DK = (0.46, 0.46, 0.45, 1.0)
COL_LEDGE = (0.50, 0.50, 0.48, 1.0)
COL_COPING = (0.66, 0.62, 0.52, 1.0)     # steel coping edge
COL_RAIL = (0.40, 0.42, 0.46, 1.0)
COL_GRASS = (0.42, 0.50, 0.30, 1.0)
COL_FENCE = (0.48, 0.50, 0.52, 1.0)
COL_TRUNK = (0.32, 0.24, 0.16, 1.0)
COL_LEAF = (0.30, 0.44, 0.24, 1.0)
COL_LEAF_LT = (0.38, 0.52, 0.28, 1.0)
COL_BENCH = (0.44, 0.32, 0.22, 1.0)
COL_TAG_A = (0.62, 0.30, 0.44, 1.0)      # spray tags on the utility box
COL_TAG_B = (0.30, 0.44, 0.60, 1.0)
COL_BOX = (0.42, 0.46, 0.42, 1.0)
COL_SKY = (0.68, 0.76, 0.82, 1.0)
COL_POOL = (0.50, 0.50, 0.49, 1.0)       # the bowl's skin, a shade under the slab
COL_POOL_FLOOR = (0.44, 0.44, 0.43, 1.0)

# THE POOL is a real hole (2026-09-30, draft 2): x -2.23..3.23, y 5.27..9.13,
# flush with the coping's inner edges, 1.5 m deep.
POOL_PX, POOL_PY, POOL_HX, POOL_HY, POOL_DEPTH = 0.5, 7.2, 2.73, 1.93, 1.5
POOL_X0, POOL_X1 = POOL_PX - POOL_HX, POOL_PX + POOL_HX
POOL_Y0, POOL_Y1 = POOL_PY - POOL_HY, POOL_PY + POOL_HY


def holed_box(name, cx, cy, sx, sy, cz, th, col):
    """A ground layer with the pool's hole through it: four boxes
    (S and N full width, W and E between them)."""
    x0, x1, y0, y1 = cx - sx / 2.0, cx + sx / 2.0, cy - sy / 2.0, cy + sy / 2.0
    make_box(f"{name}_S", (cx, (y0 + POOL_Y0) / 2.0, cz), (sx, POOL_Y0 - y0, th), col)
    make_box(f"{name}_N", (cx, (POOL_Y1 + y1) / 2.0, cz), (sx, y1 - POOL_Y1, th), col)
    make_box(f"{name}_W", ((x0 + POOL_X0) / 2.0, POOL_PY, cz), (POOL_X0 - x0, POOL_Y1 - POOL_Y0, th), col)
    make_box(f"{name}_E", ((POOL_X1 + x1) / 2.0, POOL_PY, cz), (x1 - POOL_X1, POOL_Y1 - POOL_Y0, th), col)


def build_ground():
    holed_box("Grass_Base", 0.0, 7.0, 30.0, 20.0, 0.0, 0.05, COL_GRASS)
    holed_box("Slab", -1.0, 6.0, 16.0, 12.0, 0.02, 0.06, COL_SLAB)
    # Expansion seams
    for i in range(4):
        if i == 0:
            # split round the stair set (2026-09-24: it ran under the stairs)
            make_box("Seam_X_0", (-7.0, 8.425 / 2.0, 0.055), (0.06, 8.425, 0.01), COL_SLAB_DK)
            make_box("Seam_X_0_N", (-7.0, (9.475 + 12.0) / 2.0, 0.055), (0.06, 12.0 - 9.475, 0.01), COL_SLAB_DK)
            continue
        sx_ = -7.0 + i * 4.0
        if POOL_X0 < sx_ < POOL_X1:   # round the pool (2026-09-30)
            make_box(f"Seam_X_{i}", (sx_, POOL_Y0 / 2.0, 0.055), (0.06, POOL_Y0, 0.01), COL_SLAB_DK)
            make_box(f"Seam_X_{i}_N", (sx_, (POOL_Y1 + 12.0) / 2.0, 0.055), (0.06, 12.0 - POOL_Y1, 0.01), COL_SLAB_DK)
            continue
        make_box(f"Seam_X_{i}", (sx_, 6.0, 0.055), (0.06, 12.0, 0.01), COL_SLAB_DK)
    make_box("Seam_Y", ((-9.0 + POOL_X0) / 2.0, 6.0, 0.055), (POOL_X0 + 9.0, 0.06, 0.01), COL_SLAB_DK)
    make_box("Seam_Y_E", ((POOL_X1 + 7.0) / 2.0, 6.0, 0.055), (7.0 - POOL_X1, 0.06, 0.01), COL_SLAB_DK)


def build_features():
    build_pool_2026_09()
    # One half-buried pipe hump keeps the flow line west (2026-09-30:
    # half a metre further west — its east end poked into the pool's mouth)
    make_cyl("Hump_W", (-5.0, 5.0, -0.25), 1.15, 5.0, COL_SLAB_DK, segments=18, axis='X')
    # Grind ledge pair
    make_box("Ledge_Lo", (1.5, 4.0, 0.20), (2.6, 0.65, 0.40), COL_LEDGE)
    make_box("Ledge_Lo_Coping", (1.5, 4.0, 0.415), (2.6, 0.65, 0.035), COL_COPING)
    make_box("Ledge_Hi", (4.2, 4.4, 0.30), (2.0, 0.65, 0.60), COL_LEDGE)
    make_box("Ledge_Hi_Coping", (4.2, 4.4, 0.615), (2.0, 0.65, 0.035), COL_COPING)
    # Flat rail on posts
    for py in (2.6, 4.4):
        make_box(f"Rail_Post_{py:.1f}", (-2.0, py, 0.22), (0.07, 0.07, 0.44), COL_RAIL)
    make_cyl("Rail", (-2.0, 3.5, 0.46), 0.045, 2.2, COL_RAIL, segments=8, axis='Y')
    # Three-stair set into a lower pad, with handrail
    for s in range(3):
        make_box(f"Stair_{s}", (-6.5, 8.6 + s * 0.35, 0.30 - s * 0.10),
                 (2.4, 0.35, 0.60 - s * 0.20), COL_LEDGE)
    make_box("Stair_Pad", (-6.5, 10.4, 0.02), (2.8, 1.6, 0.06), COL_SLAB_DK)
    make_box("HandRail_Post_S", (-5.5, 8.5, 0.45), (0.06, 0.06, 0.9), COL_RAIL)
    make_box("HandRail_Post_N", (-5.5, 10.3, 0.25), (0.06, 0.06, 0.5), COL_RAIL)
    make_cyl("HandRail", (-5.5, 9.4, 0.72), 0.04, 2.0, COL_RAIL, segments=8, axis='Y')


def build_pool_2026_09():
    """THE POOL, draft 2 (2026-09-30) — canon: "waiting to push off
    into the pool". Draft 1 suggested it "without booleans": a darker
    patch and a coping ring flat on the slab, and the 09-26 sheet's
    establish read as an empty lot with an outline painted on it. Now
    a hole through the slab, the grass and the far ground (holed_box),
    1.5 m deep: four walls whose inner faces are the pool's sides, a
    floor, quarter-round transitions at the base of every wall (the
    curve a skater rides from the floor up the wall), a drain, and
    the steel coping flush with the hole's edge, full length.
    NEXT (draft 3): rounded corners (the transitions stop short of
    them, so each corner is a vertical seam); a deep end (one half
    stepped down); tags and wheel marks on the walls; a skater
    mid-carve at the far wall for the establish."""
    px, py, hx, hy, dep = POOL_PX, POOL_PY, POOL_HX, POOL_HY, POOL_DEPTH
    top = 0.05
    wtop = -0.045                        # under every ground layer (slab, grass, far ground end at the hole's edge themselves)
    wall_h = wtop - (top - dep)
    wz = wtop - wall_h / 2.0
    t = 0.20
    make_box("Pool_Wall_W", (POOL_X0 - t / 2.0, py, wz), (t, 2 * hy, wall_h), COL_POOL)
    make_box("Pool_Wall_E", (POOL_X1 + t / 2.0, py, wz), (t, 2 * hy, wall_h), COL_POOL)
    make_box("Pool_Wall_S", (px, POOL_Y0 - t / 2.0, wz), (2 * hx + 2 * t, t, wall_h), COL_POOL)
    make_box("Pool_Wall_N", (px, POOL_Y1 + t / 2.0, wz), (2 * hx + 2 * t, t, wall_h), COL_POOL)
    fz = top - dep                       # the floor's top
    make_box("Pool_Floor", (px, py, fz - 0.05), (2 * hx, 2 * hy, 0.10), COL_POOL_FLOOR)
    make_cyl("Pool_Drain", (px, py, fz + 0.004), 0.12, 0.008, (0.20, 0.20, 0.21, 1.0), segments=12)
    # transitions: a quarter-round fillet along each wall's base, stopping
    # R short of each corner (the fillets never cross)
    R = 0.9
    n = 7
    arc = [(R - R * math.sin(k * math.pi / 2 / n), R - R * math.cos(k * math.pi / 2 / n)) for k in range(n + 1)]
    poly = [(0.0, 0.0)] + arc          # corner, along the floor to R, up the curve to the wall at R
    # u runs away from the wall along the floor, v up the wall
    import math as _m
    runs = (("W", POOL_X0, "+X", 2 * hy - 2 * R), ("E", POOL_X1, "-X", 2 * hy - 2 * R),
            ("S", POOL_Y0, "+Y", 2 * hx - 2 * R), ("N", POOL_Y1, "-Y", 2 * hx - 2 * R))
    for side, pos, into, ln in runs:
        if side in "WE":
            sgn = 1.0 if into == "+X" else -1.0
            # prism along Y: (u, v) -> (x, z)
            pts = [(sgn * u, v) for (u, v) in poly]
            if sgn < 0:
                pts = list(reversed(pts))
            make_prism(f"Pool_Transition_{side}", (pos, py, fz), pts, ln, COL_POOL, axis="Y")
        else:
            sgn = 1.0 if into == "+Y" else -1.0
            # prism along X: (u, v) -> (y, z)
            pts = [(sgn * u, v) for (u, v) in poly]
            if sgn < 0:
                pts = list(reversed(pts))
            make_prism(f"Pool_Transition_{side}", (px, pos, fz), pts, ln, COL_POOL, axis="X")
    # the coping, flush with the hole's edge, full length, meeting at the corners
    ct = 0.14
    make_box("Pool_Coping_W", (POOL_X0 - ct / 2.0, py, top + 0.025), (ct, 2 * hy + 2 * ct, 0.05), COL_COPING)
    make_box("Pool_Coping_E", (POOL_X1 + ct / 2.0, py, top + 0.025), (ct, 2 * hy + 2 * ct, 0.05), COL_COPING)
    make_box("Pool_Coping_S", (px, POOL_Y0 - ct / 2.0, top + 0.025), (2 * hx, ct, 0.05), COL_COPING)
    make_box("Pool_Coping_N", (px, POOL_Y1 + ct / 2.0, top + 0.025), (2 * hx, ct, 0.05), COL_COPING)


def build_perimeter():
    # Chain-link fence: posts + top rail + a faint mesh plane
    for i in range(9):
        fx = -12.0 + i * 3.0
        make_cyl(f"Fence_Post_{i}", (fx, 12.5, 0.9), 0.05, 1.8, COL_FENCE, segments=6)
    make_cyl("Fence_TopRail", (0.0, 12.5, 1.78), 0.035, 24.5, COL_FENCE, segments=6, axis='X')
    make_box("Fence_Mesh", (0.0, 12.5, 0.9), (24.5, 0.02, 1.7), (0.55, 0.57, 0.58, 0.35))
    # Bench + tagged utility box near the entry
    make_box("Bench_Seat", (5.5, 1.5, 0.42), (1.8, 0.45, 0.06), COL_BENCH)
    for bx in (4.8, 6.2):
        make_box(f"Bench_Leg_{bx:.1f}", (bx, 1.5, 0.20), (0.08, 0.4, 0.40), COL_RAIL)
    make_box("Utility_Box", (-8.6, 2.0, 0.55), (0.8, 0.6, 1.10), COL_BOX)
    make_box("Tag_A", (-8.6, 1.68, 0.62), (0.5, 0.02, 0.28), COL_TAG_A)
    make_box("Tag_B", (-8.45, 1.68, 0.92), (0.34, 0.02, 0.18), COL_TAG_B)


def build_backdrop():
    # Trees over the fence line
    spots = [(-10.0, 14.5), (-5.0, 15.5), (0.5, 14.8), (6.0, 15.2), (10.5, 14.3)]
    for i, (px, py) in enumerate(spots):
        h = 4.2 + 1.0 * ((i * 3) % 3)
        # 2026-08-04: crown was a BOX. Real broadleaf silhouette now.
        from _props.trees import make_broadleaf
        col = COL_LEAF if i % 2 == 0 else COL_LEAF_LT
        make_broadleaf(f"Tree_{i}", px, py, h, col, COL_TRUNK)
    # (occluder slab deleted 2026-08-04 — a paper-thin wall 20m out
    # hiding the real receding bands built behind it)


def main():
    clear_scene()
    build_ground()
    build_features()
    build_perimeter()
    build_backdrop()
    out = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)),
        "../../../assets/3d/locales/skatepark.glb"))
    print(f"\n[build_skatepark] exporting to {out}")
    build_horizon_2026_08()
    export_glb(out)



def build_horizon_2026_08():
    """STUMP HUNT: view stopped at 31m. The park sits in a real
    suburb: house rooflines one street over, then treelines."""
    # GROUND under everything out past the last band (2026-08-09,
    # user: "no ground on any of the roads — a flat expanse of
    # nothing"). Locale-colored so exteriors stop sharing a void.
    holed_box("Ground_Far", 0.0, 0.0, 1000.0, 1000.0, -0.03, 0.02, (0.22, 0.28, 0.17, 1.0))
    from _props.detail import make_far_bands
    make_far_bands("FarRoofline", (0.36, 0.33, 0.30),
                   [(55.0, 60.0, 6.0, 0.92), (120.0, 100.0, 7.0, 0.74)],
                   profile="roofline")
    make_far_bands("FarTrees", (0.24, 0.32, 0.19),
                   [(220.0, 180.0, 10.0, 0.60), (420.0, 300.0, 13.0, 0.45)],
                   profile="treeline")


if __name__ == "__main__":
    main()
