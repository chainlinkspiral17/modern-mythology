# _props/kitchen_kit.py
# ════════════════════════════════════════════════════════════════
# A HOUSE KITCHEN'S FIXTURES (2026-10-07). The vol 6 family kitchens
# were all built from the store kit: `make_counter` (a formica shop
# counter), a chamfer-box "stove", a box "fridge", one slab of upper
# cabinet — the sheet's row of identical template kitchens. These are
# the fixtures of a 2010s suburban kitchen, all against a wall that
# runs along X with the room toward -Y (a NORTH wall):
#
#   base_run      toe kick, carcass, door and drawer fronts with bar
#                 pulls, the top with its front edge; `gaps` leave room
#                 for a range or a dishwasher
#   upper_run     wall cabinets with shaker doors and pulls
#   backsplash    subway tile: a field with its courses
#   sink          an undermount double basin, a gooseneck faucet
#   range_        slide-in range: glass top, burners, knobs, oven door
#   fridge        French-door fridge with the freezer drawer
#   dishwasher    the panel and its handle in a base-run gap
#
# y_back is the wall's ROOM face; everything is built toward -Y.
# ════════════════════════════════════════════════════════════════
from .geometry import make_box, make_cyl, make_tube

WHITE_SHAKER = (0.92, 0.91, 0.87, 1.0)
WHITE_SHAKER_DK = (0.84, 0.83, 0.79, 1.0)
QUARTZ = (0.86, 0.85, 0.82, 1.0)
QUARTZ_EDGE = (0.78, 0.77, 0.74, 1.0)
STAINLESS = (0.72, 0.73, 0.74, 1.0)
STAINLESS_DK = (0.52, 0.53, 0.55, 1.0)
BLACK_GLASS = (0.10, 0.10, 0.11, 1.0)
NICKEL = (0.68, 0.68, 0.66, 1.0)


def base_run(prefix, x0, x1, y_back, *, depth=0.62, top_z=0.98, door_w=0.50,
             body=WHITE_SHAKER, top=QUARTZ, edge=QUARTZ_EDGE, pull=NICKEL, gaps=(), rail=WHITE_SHAKER_DK):
    """Base cabinets x0..x1. `gaps` = [(gx0, gx1), ...] left open (no
    carcass, no top) for a range; a dishwasher gap keeps its top."""
    y0 = y_back - depth
    segs, cur = [], x0
    for g0, g1 in sorted(gaps):
        if g0 > cur:
            segs.append((cur, g0))
        cur = max(cur, g1)
    if cur < x1:
        segs.append((cur, x1))
    for si, (a, b) in enumerate(segs):
        w, cx = b - a, (a + b) / 2.0
        make_box(f"{prefix}_{si}_Kick", (cx, (y0 + 0.07 + y_back) / 2.0, 0.05), (w, depth - 0.07, 0.10), (0.20, 0.20, 0.20, 1.0))
        make_box(f"{prefix}_{si}_Carcass", (cx, (y0 + y_back) / 2.0, (0.10 + top_z - 0.04) / 2.0),
                 (w, depth, top_z - 0.04 - 0.10), body)
        make_box(f"{prefix}_{si}_Top", (cx, (y0 - 0.025 + y_back) / 2.0, top_z - 0.02), (w, depth + 0.025, 0.04), top)
        make_box(f"{prefix}_{si}_Top_Edge", (cx, y0 - 0.0265, top_z - 0.02), (w, 0.003, 0.04), edge)
        n = max(1, int(round(w / door_w)))
        dw = w / n
        for k in range(n):
            dx = a + dw * (k + 0.5)
            make_box(f"{prefix}_{si}_Door_{k}", (dx, y0 - 0.009, 0.42), (dw - 0.012, 0.018, 0.58), body)
            make_box(f"{prefix}_{si}_Door_{k}_Rail_T", (dx, y0 - 0.0195, 0.67), (dw - 0.06, 0.003, 0.05), rail)
            make_box(f"{prefix}_{si}_Door_{k}_Rail_B", (dx, y0 - 0.0195, 0.17), (dw - 0.06, 0.003, 0.05), rail)
            make_box(f"{prefix}_{si}_Drawer_{k}", (dx, y0 - 0.009, top_z - 0.135), (dw - 0.012, 0.018, 0.15), body)
            make_box(f"{prefix}_{si}_Drawer_{k}_Pull", (dx, y0 - 0.026, top_z - 0.135), (min(0.16, dw * 0.4), 0.016, 0.012), pull)
            kx = dx + (dw / 2.0 - 0.06) * (1 if k % 2 else -1)
            make_box(f"{prefix}_{si}_Door_{k}_Pull", (kx, y0 - 0.026, 0.55), (0.012, 0.016, 0.12), pull)


def upper_run(prefix, x0, x1, y_back, *, z0=1.46, z1=2.20, depth=0.34, door_w=0.45,
              body=WHITE_SHAKER, pull=NICKEL, rail=WHITE_SHAKER_DK):
    w, cx = x1 - x0, (x0 + x1) / 2.0
    y0 = y_back - depth
    make_box(f"{prefix}_Carcass", (cx, (y0 + y_back) / 2.0, (z0 + z1) / 2.0), (w, depth, z1 - z0), body)
    make_box(f"{prefix}_Crown", (cx, y0 + 0.01, z1 + 0.03), (w + 0.04, 0.05, 0.06), body)
    n = max(1, int(round(w / door_w)))
    dw = w / n
    for k in range(n):
        dx = x0 + dw * (k + 0.5)
        make_box(f"{prefix}_Door_{k}", (dx, y0 - 0.009, (z0 + z1) / 2.0), (dw - 0.012, 0.018, z1 - z0 - 0.02), body)
        make_box(f"{prefix}_Door_{k}_Rail_T", (dx, y0 - 0.0195, z1 - 0.05), (dw - 0.06, 0.003, 0.05), rail)
        make_box(f"{prefix}_Door_{k}_Rail_B", (dx, y0 - 0.0195, z0 + 0.05), (dw - 0.06, 0.003, 0.05), rail)
        kx = dx + (dw / 2.0 - 0.05) * (1 if k % 2 else -1)
        make_box(f"{prefix}_Door_{k}_Pull", (kx, y0 - 0.026, z0 + 0.12), (0.012, 0.016, 0.12), pull)


def backsplash(prefix, x0, x1, y_back, z0, z1, *, tile=(0.94, 0.94, 0.92, 1.0), grout=(0.78, 0.78, 0.76, 1.0),
               course=0.075):
    """Subway tile on the wall face between z0 and z1."""
    w, cx = x1 - x0, (x0 + x1) / 2.0
    make_box(f"{prefix}_Field", (cx, y_back - 0.005, (z0 + z1) / 2.0), (w, 0.010, z1 - z0), tile)
    k, z = 0, z0 + course
    while z < z1 - 0.01:
        make_box(f"{prefix}_Course_{k}", (cx, y_back - 0.0105, z), (w, 0.001, 0.004), grout)
        k += 1
        z += course


def sink(prefix, cx, y_back, top_z, *, width=0.84, depth=0.48):
    yc = y_back - 0.04 - depth / 2.0
    make_box(f"{prefix}_Rim", (cx, yc, top_z + 0.002), (width, depth, 0.004), STAINLESS)
    for sgn, nm in ((-1, "L"), (1, "R")):
        make_box(f"{prefix}_Basin_{nm}", (cx + sgn * width * 0.24, yc, top_z + 0.0045), (width * 0.44, depth - 0.08, 0.002), STAINLESS_DK)
        make_cyl(f"{prefix}_Basin_{nm}_Drain", (cx + sgn * width * 0.24, yc, top_z + 0.006), 0.03, 0.002, (0.30, 0.30, 0.32, 1.0), segments=8)
    fy = y_back - 0.05
    make_cyl(f"{prefix}_Faucet_Base", (cx, fy, top_z + 0.03), 0.028, 0.05, NICKEL, segments=8)
    make_tube(f"{prefix}_Faucet_Spout", [(cx, fy, top_z + 0.05), (cx, fy, top_z + 0.34), (cx, fy - 0.08, top_z + 0.40),
                                         (cx, fy - 0.18, top_z + 0.33)], 0.011, NICKEL)
    make_box(f"{prefix}_Faucet_Lever", (cx + 0.045, fy, top_z + 0.12), (0.06, 0.014, 0.014), NICKEL)


def range_(prefix, cx, y_back, top_z, *, width=0.76, depth=0.66):
    """Slide-in range; its cooktop sits at top_z - 0.04 (flush with
    the counter's top slab underside + a glass top on it)."""
    y0 = y_back - depth
    yc = (y0 + y_back) / 2.0
    make_box(f"{prefix}_Body", (cx, yc, (top_z - 0.04) / 2.0), (width, depth, top_z - 0.04), STAINLESS)
    make_box(f"{prefix}_Cooktop", (cx, yc, top_z - 0.02), (width, depth, 0.04), BLACK_GLASS)
    for bi, (bx, by) in enumerate(((-0.19, -0.14), (0.19, -0.14), (-0.19, 0.16), (0.19, 0.16))):
        make_cyl(f"{prefix}_Burner_{bi}", (cx + bx, yc + by, top_z + 0.001), 0.10 if bi % 3 == 0 else 0.08, 0.002,
                 (0.26, 0.24, 0.24, 1.0), segments=14)
    make_box(f"{prefix}_Oven_Door", (cx, y0 - 0.012, 0.47), (width - 0.02, 0.024, 0.62), STAINLESS)
    make_box(f"{prefix}_Oven_Window", (cx, y0 - 0.0245, 0.50), (width - 0.20, 0.002, 0.30), BLACK_GLASS)
    make_cyl(f"{prefix}_Oven_Handle", (cx, y0 - 0.06, 0.82), 0.012, width - 0.12, NICKEL, axis='X', segments=8)
    for sgn in (-1, 1):
        make_box(f"{prefix}_Oven_Handle_Post_{sgn:+d}", (cx + sgn * (width / 2.0 - 0.08), y0 - 0.025, 0.82), (0.02, 0.05, 0.02), NICKEL)
    for k in range(5):
        make_cyl(f"{prefix}_Knob_{k}", (cx - width / 2.0 + 0.10 + k * (width - 0.20) / 4.0, y0 - 0.02, top_z - 0.10), 0.02, 0.025,
                 STAINLESS_DK, axis='Y', segments=8)
    make_box(f"{prefix}_Drawer", (cx, y0 - 0.012, 0.08), (width - 0.02, 0.024, 0.12), STAINLESS)


def fridge(prefix, cx, y_back, *, width=0.86, depth=0.74, height=1.78):
    y0 = y_back - depth
    make_box(f"{prefix}_Body", (cx, (y0 + y_back) / 2.0, height / 2.0), (width, depth, height), STAINLESS)
    for sgn, nm in ((-1, "L"), (1, "R")):
        dx = cx + sgn * width / 4.0
        make_box(f"{prefix}_Door_{nm}", (dx, y0 - 0.02, 1.20), (width / 2.0 - 0.01, 0.04, 1.14), STAINLESS)
        make_cyl(f"{prefix}_Handle_{nm}", (cx + sgn * 0.04, y0 - 0.07, 1.20), 0.012, 0.70, NICKEL, segments=8)
        for e in (-1, 1):
            make_box(f"{prefix}_Handle_{nm}_Post_{e:+d}", (cx + sgn * 0.04, y0 - 0.055, 1.20 + e * 0.33), (0.02, 0.03, 0.02), NICKEL)
    make_box(f"{prefix}_Freezer", (cx, y0 - 0.02, 0.33), (width - 0.01, 0.04, 0.56), STAINLESS)
    make_cyl(f"{prefix}_Freezer_Handle", (cx, y0 - 0.07, 0.55), 0.012, width - 0.16, NICKEL, axis='X', segments=8)
    for e in (-1, 1):
        make_box(f"{prefix}_Freezer_Handle_Post_{e:+d}", (cx + e * (width / 2.0 - 0.12), y0 - 0.045, 0.55), (0.02, 0.05, 0.02), NICKEL)
    make_box(f"{prefix}_Dispenser", (cx - width / 4.0, y0 - 0.041, 1.30), (0.18, 0.002, 0.28), (0.24, 0.24, 0.26, 1.0))


def dishwasher(prefix, cx, y_front, top_z, *, width=0.60):
    """The panel and handle on a base run's front (y_front)."""
    make_box(f"{prefix}_Panel", (cx, y_front - 0.012, (0.10 + top_z - 0.04) / 2.0), (width - 0.01, 0.024, top_z - 0.14), STAINLESS)
    make_cyl(f"{prefix}_Handle", (cx, y_front - 0.05, top_z - 0.12), 0.011, width - 0.12, NICKEL, axis='X', segments=8)
    for e in (-1, 1):
        make_box(f"{prefix}_Handle_Post_{e:+d}", (cx + e * (width / 2.0 - 0.07), y_front - 0.035, top_z - 0.12), (0.02, 0.03, 0.02), NICKEL)
