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
import math
from _props.geometry import clear_scene, make_box, make_cyl, make_prism, make_rot_box, export_glb
from _props.geometry import _gen_prism, _fix_winding, _finalize_mesh


def make_sheared_prism(name, center, polygon, length, base_color, slope, axis="X"):
    """(2026-11-04) make_prism, with the solid's far end raised by `slope`
    per metre along the extrusion axis: a wall-base curve that follows a
    floor sloping toward the deep end. (_finalize_mesh is imported at module
    level so the audits' recorder can rebind it and see the solid.)"""
    try:
        verts, faces = _gen_prism(center, polygon, length, axis.upper())
    except (TypeError, ValueError):
        # under the audits' stubs _gen_prism is a stand-in: record the
        # unsheared prism's box instead (the shear is a few cm of height)
        return make_prism(name, center, polygon, length, base_color, axis=axis)
    ax = 0 if axis.upper() == "X" else 1
    verts = [(v[0], v[1], v[2] + (v[ax] - center[ax]) * slope) for v in verts]
    n = float(len(verts))
    c = (sum(v[0] for v in verts) / n, sum(v[1] for v in verts) / n, sum(v[2] for v in verts) / n)
    return _finalize_mesh(name, verts, _fix_winding(verts, faces, c), base_color)

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
# (2026-11-02, draft 3) a skate pool's size: 6.6 x 4.6 m and 1.8 m deep (it was
# 5.5 x 3.9 x 1.5, a hot tub's footprint); the pipe hump moved west for it
POOL_PX, POOL_PY, POOL_HX, POOL_HY, POOL_DEPTH = 0.5, 7.2, 3.3, 2.3, 1.8
# (2026-11-04, draft 4) a deep end: the W end 1.3 m, the E end 2.3 m, the
# floor sloping between (x from POOL_SLOPE_X0 to POOL_SLOPE_X1)
POOL_SHALLOW, POOL_DEEP = 1.3, 2.3
POOL_SLOPE_X0, POOL_SLOPE_X1 = POOL_PX - POOL_HX + 2.2, POOL_PX - POOL_HX + 4.0
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
    make_cyl("Hump_W", (-5.6, 5.0, -0.25), 1.15, 5.0, COL_SLAB_DK, segments=18, axis='X')
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
    make_box("Hand_Rail_Post_S", (-5.5, 8.5, 0.45), (0.06, 0.06, 0.9), COL_RAIL)
    make_box("Hand_Rail_Post_N", (-5.5, 10.3, 0.25), (0.06, 0.06, 0.5), COL_RAIL)
    make_cyl("Hand_Rail", (-5.5, 9.4, 0.72), 0.04, 2.0, COL_RAIL, segments=8, axis='Y')


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
    DRAFT 3 (2026-11-02): sized as a skate pool (6.6 x 4.6 x 1.8 m),
    the corners rounded, wheel marks and two tags on the far wall.
    DRAFT 4 (2026-11-04): a deep end. The W end is 1.3 m, the E end 2.3 m,
    the floor slopes between over 1.8 m; the wall-base curves follow the
    slope (sheared prisms), each corner's fill reaches its own floor, the
    drain sits in the deep end. The N/S walls run to the deep floor; the
    shallow floor hides their lower part.
    DRAFT 5 (2026-11-04): the coping rounded at the corners; the corner
    fills reach the slab's top.
    NEXT (draft 6): the hip where the slope meets the deep end as a proper
    bump; the boards and the boys are the VN's (Faust, Wagner and Jacob
    are portraits, never stand-ins)."""
    px, py, hx, hy = POOL_PX, POOL_PY, POOL_HX, POOL_HY
    top = 0.05
    wtop = -0.045                        # under every ground layer (slab, grass, far ground end at the hole's edge themselves)
    fz_s, fz_d = top - POOL_SHALLOW, top - POOL_DEEP    # the shallow and deep floors' tops
    sx0, sx1 = POOL_SLOPE_X0, POOL_SLOPE_X1
    slope = (fz_d - fz_s) / (sx1 - sx0)                 # negative: down toward +X
    t = 0.20

    def wall_box(name, cx, cy, sx, sy, floor):
        h = wtop - floor
        make_box(name, (cx, cy, wtop - h / 2.0), (sx, sy, h), COL_POOL)
    wall_box("Pool_Wall_W", POOL_X0 - t / 2.0, py, t, 2 * hy, fz_s)
    wall_box("Pool_Wall_E", POOL_X1 + t / 2.0, py, t, 2 * hy, fz_d)
    wall_box("Pool_Wall_S", px, POOL_Y0 - t / 2.0, 2 * hx + 2 * t, t, fz_d)
    wall_box("Pool_Wall_N", px, POOL_Y1 + t / 2.0, 2 * hx + 2 * t, t, fz_d)
    # the floor in three: the shallow end, the slope, the deep end
    make_box("Pool_Floor_Shallow", ((POOL_X0 + sx0) / 2.0, py, fz_s - 0.05), (sx0 - POOL_X0, 2 * hy, 0.10), COL_POOL_FLOOR)
    make_box("Pool_Floor_Deep", ((sx1 + POOL_X1) / 2.0, py, fz_d - 0.05), (POOL_X1 - sx1, 2 * hy, 0.10), COL_POOL_FLOOR)
    make_sheared_prism("Pool_Floor_Slope", ((sx0 + sx1) / 2.0, py, (fz_s + fz_d) / 2.0 - 0.05),
                       [(-hy, -0.05), (hy, -0.05), (hy, 0.05), (-hy, 0.05)], sx1 - sx0, COL_POOL_FLOOR, slope, axis="X")
    make_cyl("Pool_Drain", (sx1 + (POOL_X1 - sx1) / 2.0, py, fz_d + 0.004), 0.12, 0.008, (0.20, 0.20, 0.21, 1.0), segments=12)
    # transitions: a quarter-round fillet along each wall's base, stopping
    # R short of each corner (the fillets never cross)
    R = 0.9
    n = 7
    arc = [(R - R * math.sin(k * math.pi / 2 / n), R - R * math.cos(k * math.pi / 2 / n)) for k in range(n + 1)]
    poly = [(0.0, 0.0)] + arc          # corner, along the floor to R, up the curve to the wall at R
    # u runs away from the wall along the floor, v up the wall
    import math as _m
    # (draft 3) convex wedges from the corner: one concave prism wound about
    # its vertex centroid, which lay outside it (S drew inside out)
    # (draft 4) the W run sits on the shallow floor, the E run on the deep;
    # the N and S runs come in three: shallow, sloped (sheared), deep
    for side, pos, sgn in (("W", POOL_X0, 1.0), ("E", POOL_X1, -1.0)):
        fz = fz_s if side == "W" else fz_d
        for k in range(1, len(arc)):
            make_prism(f"Pool_Transition_{side}_{k}", (pos, py, fz), [(0.0, 0.0), (sgn * arc[k - 1][0], arc[k - 1][1]),
                       (sgn * arc[k][0], arc[k][1])], 2 * hy - 2 * R, COL_POOL, axis="Y")
    segs = (("Sh", POOL_X0 + R, sx0, fz_s, 0.0), ("Sl", sx0, sx1, (fz_s + fz_d) / 2.0, slope), ("Dp", sx1, POOL_X1 - R, fz_d, 0.0))
    for side, pos, sgn in (("S", POOL_Y0, 1.0), ("N", POOL_Y1, -1.0)):
        for tag, xa, xb, fz, sl in segs:
            for k in range(1, len(arc)):
                poly_k = [(0.0, 0.0), (sgn * arc[k - 1][0], arc[k - 1][1]), (sgn * arc[k][0], arc[k][1])]
                if sl == 0.0:
                    make_prism(f"Pool_Transition_{side}_{tag}_{k}", ((xa + xb) / 2.0, pos, fz), poly_k, xb - xa, COL_POOL, axis="X")
                else:
                    make_sheared_prism(f"Pool_Transition_{side}_{tag}_{k}", ((xa + xb) / 2.0, pos, fz), poly_k, xb - xa, COL_POOL, sl, axis="X")
    # (draft 3) the corners rounded: a quarter-round fill up each corner, so
    # the walls turn into each other (each corner was a vertical seam)
    Rc = 1.0
    arcq = [(Rc + Rc * math.cos(math.radians(a)), Rc + Rc * math.sin(math.radians(a))) for a in range(-90, -181, -15)]
    for tag, cxx, cyy, sx_, sy_, fz in (("SW", POOL_X0, POOL_Y0, 1, 1, fz_s), ("SE", POOL_X1, POOL_Y0, -1, 1, fz_d),
                                        ("NW", POOL_X0, POOL_Y1, 1, -1, fz_s), ("NE", POOL_X1, POOL_Y1, -1, -1, fz_d)):
        # convex wedges from the corner (the whole fill is concave, and a
        # prism winds about its vertex centroid, which lay outside it)
        pts = [(sx_ * u, sy_ * v) for (u, v) in arcq]
        for k in range(len(pts) - 1):
            make_prism(f"Pool_Corner_{tag}_{k}", (cxx, cyy, (fz + wtop) / 2.0), [(0.0, 0.0), pts[k], pts[k + 1]], wtop - fz,
                       COL_POOL, axis="Z")
            # (draft 5) a thin cap band over each fill up to the slab's top, so
            # the deck's inside corner is flush under the rounded coping (one
            # tall fill tripped the grammar gate's joint allowance)
            make_prism(f"Pool_Corner_{tag}_Cap_{k}", (cxx, cyy, (wtop + top) / 2.0), [(0.0, 0.0), pts[k], pts[k + 1]], top - wtop,
                       COL_SLAB, axis="Z")
    # the far (N) wall the lens looks down at: wheel marks where the boards
    # carve it, two tags
    mark = (0.30, 0.30, 0.30, 1.0)
    for k, (mx, mz, a) in enumerate(((-1.6, -0.55, 0.20), (-0.6, -0.40, -0.10), (0.4, -0.62, 0.15), (1.3, -0.48, -0.25),
                                       (2.2, -0.70, 0.30), (-0.1, -0.78, 0.05))):
        make_rot_box(f"Pool_Wheel_Mark_{k}", (px + mx, POOL_Y1 - 0.006, mz), (0.95, 0.01, 0.045), mark, pitch=a)
    make_box("Pool_Tag_A", (px - 1.1, POOL_Y1 - 0.007, -0.30), (0.85, 0.01, 0.32), COL_TAG_A)
    make_box("Pool_Tag_B", (px + 1.9, POOL_Y1 - 0.007, -0.36), (0.60, 0.01, 0.28), COL_TAG_B)
    # the coping, flush with the hole's edge; (2026-11-04, draft 5) ROUNDED at
    # the corners: each run stops Rc short and six short pieces follow the
    # corner's quarter circle (the steel coping of a skate pool bends with
    # the bowl; it met square over a rounded corner)
    ct = 0.14
    make_box("Pool_Coping_W", (POOL_X0 - ct / 2.0, py, top + 0.025), (ct, 2 * hy - 2 * Rc, 0.05), COL_COPING)
    make_box("Pool_Coping_E", (POOL_X1 + ct / 2.0, py, top + 0.025), (ct, 2 * hy - 2 * Rc, 0.05), COL_COPING)
    make_box("Pool_Coping_S", (px, POOL_Y0 - ct / 2.0, top + 0.025), (2 * hx - 2 * Rc, ct, 0.05), COL_COPING)
    make_box("Pool_Coping_N", (px, POOL_Y1 + ct / 2.0, top + 0.025), (2 * hx - 2 * Rc, ct, 0.05), COL_COPING)
    rr = Rc + ct / 2.0
    nseg = 6
    for tag, cxx, cyy, sx_, sy_, a0 in (("SW", POOL_X0, POOL_Y0, 1, 1, 180.0), ("SE", POOL_X1, POOL_Y0, -1, 1, 270.0),
                                        ("NW", POOL_X0, POOL_Y1, 1, -1, 90.0), ("NE", POOL_X1, POOL_Y1, -1, -1, 0.0)):
        ox, oy = cxx + sx_ * Rc, cyy + sy_ * Rc          # the corner arc's centre
        da = 90.0 / nseg
        seg = 2.0 * rr * math.sin(math.radians(da) / 2.0) + 0.02
        for k in range(nseg):
            a = math.radians(a0 + da * (k + 0.5))
            make_rot_box(f"Pool_Coping_{tag}_{k}", (ox + rr * math.cos(a), oy + rr * math.sin(a), top + 0.025), (seg, ct, 0.05),
                         COL_COPING, yaw=a + math.pi / 2.0)


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
