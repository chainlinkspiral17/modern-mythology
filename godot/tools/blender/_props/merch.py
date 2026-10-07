# _props/merch.py
# ════════════════════════════════════════════════════════════════
# MERCHANDISE GRAMMAR (2026-10-06/07). Every store in the game stocked
# its shelves with solid saturated blocks — the vol 6 contact sheet's
# "toy blocks" in the Kwik Stop, the grocery aisle, both NexCorp
# stores. A shelf reads by its PACKAGING: a bag with a band and a
# crimp, a tray of bars, a quart of oil with its cap, a cereal box
# with its panel, a row of cans with lids, a bottle with a shoulder.
# And a gondola is a spine with HORIZONTAL shelf plates cantilevered
# off it — the kit's old "shelves" were 32 cm vertical fins with the
# products floating beside them.
#
#   merch_section(tag, kind, x0, front_y, sgn, z0, k, width)
#       one facing of one product across `width` metres of shelf
#   stock_gondola(prefix, (cx, cy, bz), length, levels, plan, ...)
#       base, spine, shelf plates both sides, price strips and tags,
#       end panels, and the stock from `plan`
# ════════════════════════════════════════════════════════════════
from .geometry import make_box as _make_box, make_cyl as _make_cyl

# A gondola is authored running along X; `_ROT` (a pivot) turns everything
# built while it is set 90 degrees counter-clockwise about that pivot, so
# a run can go front-to-back (along Y) — supermarket aisles do (2026-10-07).
_ROT = None
# LEAN: front facings only — no second rows, no back stock (a 30 m store's
# shelves are seen from the lane; the depth behind the front row costs
# thousands of parts and is never in frame)
_LEAN = False


def _xf(c):
    if _ROT is None:
        return tuple(c)
    px, py = _ROT
    return (px - (c[1] - py), py + (c[0] - px), c[2])


def make_box(name, center, size, color, chamfer=0.0):
    """Packages stay sharp-edged: the auto-chamfer's cut is invisible at
    package scale and tripled the vertex count of a stocked store."""
    if _ROT is not None:
        size = (size[1], size[0], size[2])
    return _make_box(name, _xf(center), size, color, chamfer=chamfer)


def make_cyl(name, center, radius, height, color, segments=8, axis='Z'):
    if _ROT is not None and str(axis).upper() in ('X', 'Y'):
        axis = 'Y' if str(axis).upper() == 'X' else 'X'
    return _make_cyl(name, _xf(center), radius, height, color, segments=segments, axis=axis)

BRAND_TINTS = [
    (0.80, 0.18, 0.14, 1.0), (0.16, 0.30, 0.62, 1.0), (0.94, 0.74, 0.16, 1.0),
    (0.24, 0.50, 0.26, 1.0), (0.44, 0.20, 0.46, 1.0), (0.90, 0.46, 0.14, 1.0),
    (0.12, 0.12, 0.14, 1.0), (0.86, 0.84, 0.80, 1.0),
]
BAND_TINTS = [(0.96, 0.86, 0.30, 1.0), (0.96, 0.96, 0.94, 1.0), (0.82, 0.16, 0.14, 1.0), (0.14, 0.14, 0.16, 1.0)]
CARDBOARD = (0.86, 0.78, 0.64, 1.0)
WHITE = (0.94, 0.92, 0.86, 1.0)
STEEL = (0.66, 0.68, 0.70, 1.0)

# per-store shelf plans, bottom level first — a section per entry,
# cycled along the run
PLANS = {
    "convenience": (("cookies", "nuts", "cookies", "jerky"),
                    ("candy", "jerky", "candy", "nuts"),
                    ("candy", "nuts", "candy", "cookies"),
                    ("chips", "tubes", "chips", "chips"),
                    ("chips", "chips", "tubes", "chips")),
    "chips": (("cookies", "cookies", "nuts"), ("tubes", "chips"), ("chips", "chips", "tubes"),
              ("chips", "chips"), ("chips", "tubes", "chips")),
    "candy": (("nuts", "cookies"), ("jerky", "jerky", "nuts"), ("candy", "candy", "jerky"),
              ("candy", "candy"), ("candy", "jerky", "candy")),
    "auto": (("jug", "oil"), ("oil", "jug", "oil"), ("candy", "jerky"), ("chips", "tubes")),
    "bread": (("cookies", "cookies"), ("chips", "chips"), ("chips", "cookies"), ("chips", "chips"), ("cookies", "chips")),
    # the dairy case, bottom shelf first (make_cooler_door stock="dairy")
    "dairy": (("gallon", "gallon"), ("gallon", "gallon", "gallon"), ("halfgal", "halfgal", "halfgal"),
              ("eggs", "butter", "eggs"), ("yogurt", "cheese", "yogurt")),
    "grocery": (("cans", "cans", "jars"), ("cans", "pasta", "cans"), ("cereal", "pasta", "cereal"),
                ("cereal", "cereal", "pasta"), ("bottles", "jars", "bottles")),
}


def merch_section(tag, kind, x0, front_y, sgn, z0, k, width=0.48):
    """Fill `width` metres of shelf from x0 with a FACING of one product.
    front_y = the shelf's front edge; sgn = the side the shelf faces
    (-1 toward -Y, +1 toward +Y); z0 = the shelf's top; k = a seed."""
    body = BRAND_TINTS[k % len(BRAND_TINTS)]
    band = BAND_TINTS[k % len(BAND_TINTS)]

    def Y(d):                                   # d metres back from the front edge
        return front_y - sgn * d

    def fit(pitch):
        n = max(1, int((width + 0.001) / pitch))
        return n, x0 + (width - n * pitch) / 2.0 + pitch / 2.0

    if kind == "chips":
        n, xs = fit(0.16)
        for i in range(n):
            x = xs + i * 0.16
            h = 0.28 + 0.02 * ((i + k) % 2)
            make_box(f"{tag}_Chips_{i}", (x, Y(0.07), z0 + h / 2.0), (0.15, 0.10, h), body)
            make_box(f"{tag}_Chips_{i}_Band", (x, Y(0.019), z0 + h * 0.62), (0.15, 0.004, 0.07), band)
            make_box(f"{tag}_Chips_{i}_Crimp", (x, Y(0.07), z0 + h + 0.008), (0.15, 0.02, 0.016), body)
            if not _LEAN: make_box(f"{tag}_Chips_{i}_Back", (x, Y(0.20), z0 + h / 2.0 - 0.01), (0.15, 0.10, h - 0.02), body)
    elif kind == "candy":
        n, xs = fit(0.24)
        for t in range(n):
            x = xs + t * 0.24
            make_box(f"{tag}_Candy_Tray_{t}", (x, Y(0.09), z0 + 0.025), (0.22, 0.16, 0.05), CARDBOARD)
            make_box(f"{tag}_Candy_Tray_{t}_Header", (x, Y(0.165), z0 + 0.10), (0.22, 0.01, 0.10), BRAND_TINTS[(k + t) % len(BRAND_TINTS)])
            for b in range(6):
                make_box(f"{tag}_Candy_Tray_{t}_Bar_{b}", (x - 0.09 + b * 0.036, Y(0.06), z0 + 0.09),
                         (0.03, 0.016, 0.08), BRAND_TINTS[(k + t + 2) % len(BRAND_TINTS)])
    elif kind == "oil":
        cols = ((0.12, 0.12, 0.14, 1.0), (0.16, 0.30, 0.62, 1.0), (0.94, 0.74, 0.16, 1.0))
        n, xs = fit(0.12)
        for i in range(n):
            x = xs + i * 0.12
            c = cols[(i // 2 + k) % 3]
            for r in range(1 if _LEAN else 2):
                make_box(f"{tag}_Oil_{i}_{r}", (x, Y(0.05 + r * 0.11), z0 + 0.095), (0.09, 0.06, 0.19), c)
            make_cyl(f"{tag}_Oil_{i}_0_Cap", (x + 0.02, Y(0.05), z0 + 0.205), 0.016, 0.03, WHITE, segments=6)
            make_box(f"{tag}_Oil_{i}_0_Label", (x, Y(0.019), z0 + 0.09), (0.08, 0.003, 0.08), WHITE)
    elif kind == "jug":
        n, xs = fit(0.24)
        for i in range(n):
            x = xs + i * 0.24
            make_box(f"{tag}_Jug_{i}", (x, Y(0.08), z0 + 0.14), (0.18, 0.12, 0.28), (0.34, 0.60, 0.88, 1.0))
            make_cyl(f"{tag}_Jug_{i}_Cap", (x + 0.05, Y(0.08), z0 + 0.295), 0.022, 0.03, WHITE, segments=6)
            make_box(f"{tag}_Jug_{i}_Label", (x, Y(0.019), z0 + 0.12), (0.14, 0.003, 0.10), WHITE)
            if not _LEAN: make_box(f"{tag}_Jug_{i}_Back", (x, Y(0.22), z0 + 0.14), (0.18, 0.12, 0.28), (0.30, 0.54, 0.80, 1.0))
    elif kind == "tubes":
        n, xs = fit(0.095)
        for i in range(n):
            x = xs + i * 0.095
            make_cyl(f"{tag}_Tube_{i}", (x, Y(0.05), z0 + 0.115), 0.038, 0.23, body, segments=6)
            make_cyl(f"{tag}_Tube_{i}_Lid", (x, Y(0.05), z0 + 0.2375), 0.040, 0.015, band, segments=6)
            if not _LEAN: make_cyl(f"{tag}_Tube_{i}_Back", (x, Y(0.14), z0 + 0.115), 0.038, 0.23, body, segments=6)
    elif kind == "jerky":
        n, xs = fit(0.12)
        for i in range(n):
            x = xs + i * 0.12
            for r in range(1 if _LEAN else 3):
                make_box(f"{tag}_Jerky_{i}_{r}", (x, Y(0.03 + r * 0.06), z0 + 0.10), (0.11, 0.025, 0.20),
                         ((0.26, 0.16, 0.10, 1.0), (0.12, 0.12, 0.14, 1.0))[(i + k) % 2])
            make_box(f"{tag}_Jerky_{i}_Label", (x, Y(0.016), z0 + 0.13), (0.09, 0.002, 0.05), (0.80, 0.18, 0.14, 1.0))
    elif kind == "cookies":
        n, xs = fit(0.24)
        for i in range(n):
            x = xs + i * 0.24
            for st in range(3):
                make_box(f"{tag}_Cookies_{i}_{st}", (x, Y(0.08), z0 + 0.025 + st * 0.05), (0.20, 0.13, 0.048),
                         BRAND_TINTS[(k + i + st) % len(BRAND_TINTS)] if st == 2 else body)
    elif kind == "nuts":
        n, xs = fit(0.12)
        for i in range(n):
            x = xs + i * 0.12
            for r in range(1 if _LEAN else 2):
                make_cyl(f"{tag}_Nuts_{i}_{r}", (x, Y(0.05 + r * 0.10), z0 + 0.06), 0.045, 0.12, body, segments=6)
            make_cyl(f"{tag}_Nuts_{i}_0_Lid", (x, Y(0.05), z0 + 0.125), 0.046, 0.012, band, segments=6)
    elif kind == "cereal":
        n, xs = fit(0.21)
        for i in range(n):
            x = xs + i * 0.21
            h = 0.30 - 0.03 * ((i + k) % 2)
            make_box(f"{tag}_Cereal_{i}", (x, Y(0.04), z0 + h / 2.0), (0.19, 0.07, h), body)
            make_box(f"{tag}_Cereal_{i}_Panel", (x, Y(0.0035), z0 + h * 0.45), (0.14, 0.002, h * 0.42), band)
            make_box(f"{tag}_Cereal_{i}_Logo", (x, Y(0.0025), z0 + h * 0.82), (0.15, 0.002, 0.05), WHITE)
            if not _LEAN: make_box(f"{tag}_Cereal_{i}_Back", (x, Y(0.13), z0 + h / 2.0), (0.19, 0.07, h), body)
    elif kind == "cans":
        n, xs = fit(0.085)
        for i in range(n):
            x = xs + i * 0.085
            col = BRAND_TINTS[(k + i // 3) % len(BRAND_TINTS)]
            for st in range(2):
                for r in range(1 if _LEAN else 2):
                    make_cyl(f"{tag}_Can_{i}_{st}_{r}", (x, Y(0.045 + r * 0.09), z0 + 0.06 + st * 0.12), 0.038, 0.115,
                             col, segments=6)
                make_cyl(f"{tag}_Can_{i}_{st}_0_Label", (x, Y(0.045), z0 + 0.06 + st * 0.12), 0.0385, 0.05, band, segments=6)
    elif kind == "bottles":
        n, xs = fit(0.10)
        for i in range(n):
            x = xs + i * 0.10
            col = ((0.62, 0.20, 0.12, 1.0), (0.86, 0.66, 0.20, 1.0), (0.30, 0.42, 0.20, 1.0))[(k + i // 2) % 3]
            for r in range(1 if _LEAN else 2):
                make_cyl(f"{tag}_Bottle_{i}_{r}", (x, Y(0.045 + r * 0.10), z0 + 0.09), 0.035, 0.18, col, segments=6)
                make_cyl(f"{tag}_Bottle_{i}_{r}_Neck", (x, Y(0.045 + r * 0.10), z0 + 0.21), 0.014, 0.06, col, segments=6)
            make_cyl(f"{tag}_Bottle_{i}_0_Cap", (x, Y(0.045), z0 + 0.25), 0.016, 0.02, WHITE, segments=6)
            make_cyl(f"{tag}_Bottle_{i}_0_Label", (x, Y(0.045), z0 + 0.08), 0.0355, 0.07, band, segments=6)
    elif kind == "jars":
        n, xs = fit(0.10)
        for i in range(n):
            x = xs + i * 0.10
            for r in range(1 if _LEAN else 2):
                make_cyl(f"{tag}_Jar_{i}_{r}", (x, Y(0.045 + r * 0.10), z0 + 0.065), 0.042, 0.13,
                         ((0.70, 0.22, 0.14, 1.0), (0.88, 0.70, 0.40, 1.0), (0.40, 0.48, 0.20, 1.0))[(k + i) % 3], segments=6)
            make_cyl(f"{tag}_Jar_{i}_0_Lid", (x, Y(0.045), z0 + 0.14), 0.043, 0.02, BAND_TINTS[(k + i) % 4], segments=6)
            make_cyl(f"{tag}_Jar_{i}_0_Label", (x, Y(0.045), z0 + 0.06), 0.0425, 0.06, WHITE, segments=6)
    # ── the dairy case (2026-10-07): the grocery's twelve-door cooler held
    # beer six-packs and soda cans. Milk reads by its jug and cap colour
    # (red whole, blue 2 %, cyan 1 %, pink skim), a half-gallon by its
    # gable, eggs by the grey pulp carton, yogurt by the cup and foil.
    elif kind == "gallon":
        caps = ((0.82, 0.16, 0.14, 1.0), (0.18, 0.34, 0.72, 1.0), (0.36, 0.70, 0.86, 1.0), (0.90, 0.52, 0.64, 1.0))
        n, xs = fit(0.17)
        for i in range(n):
            x = xs + i * 0.17
            cap = caps[(k + i // 2) % len(caps)]
            for r in range(1 if _LEAN else 2):
                make_box(f"{tag}_Gallon_{i}_{r}", (x, Y(0.08 + r * 0.16), z0 + 0.12), (0.15, 0.15, 0.24), (0.95, 0.95, 0.92, 1.0))
            make_box(f"{tag}_Gallon_{i}_0_Shoulder", (x, Y(0.08), z0 + 0.255), (0.10, 0.10, 0.03), (0.95, 0.95, 0.92, 1.0))
            make_cyl(f"{tag}_Gallon_{i}_0_Cap", (x, Y(0.08), z0 + 0.28), 0.022, 0.02, cap, segments=6)
            make_box(f"{tag}_Gallon_{i}_0_Label", (x, Y(0.004), z0 + 0.12), (0.12, 0.002, 0.08), cap)
    elif kind == "halfgal":
        n, xs = fit(0.11)
        for i in range(n):
            x = xs + i * 0.11
            col = ((0.92, 0.92, 0.88, 1.0), (0.94, 0.86, 0.40, 1.0), (0.96, 0.62, 0.20, 1.0))[(k + i // 3) % 3]
            for r in range(1 if _LEAN else 2):
                make_box(f"{tag}_Carton_{i}_{r}", (x, Y(0.05 + r * 0.10), z0 + 0.10), (0.095, 0.095, 0.20), col)
                make_box(f"{tag}_Carton_{i}_{r}_Gable", (x, Y(0.05 + r * 0.10), z0 + 0.215), (0.095, 0.03, 0.03), col)
            make_box(f"{tag}_Carton_{i}_0_Band", (x, Y(0.0015), z0 + 0.14), (0.095, 0.003, 0.05), BRAND_TINTS[(k + 1) % len(BRAND_TINTS)])
    elif kind == "eggs":
        n, xs = fit(0.32)
        for i in range(n):
            x = xs + i * 0.32
            for st in range(3):
                make_box(f"{tag}_Eggs_{i}_{st}", (x, Y(0.07), z0 + 0.035 + st * 0.07), (0.30, 0.12, 0.068),
                         (0.70, 0.70, 0.68, 1.0) if (i + st + k) % 3 else (0.92, 0.88, 0.80, 1.0))
            make_box(f"{tag}_Eggs_{i}_Label", (x, Y(0.009), z0 + 0.175), (0.12, 0.002, 0.04), (0.20, 0.42, 0.24, 1.0))
    elif kind == "butter":
        n, xs = fit(0.14)
        for i in range(n):
            x = xs + i * 0.14
            for st in range(2):
                make_box(f"{tag}_Butter_{i}_{st}", (x, Y(0.04), z0 + 0.035 + st * 0.07), (0.12, 0.065, 0.068),
                         (0.96, 0.88, 0.48, 1.0) if (i + k) % 2 else (0.92, 0.92, 0.88, 1.0))
            make_box(f"{tag}_Butter_{i}_Band", (x, Y(0.0065), z0 + 0.105), (0.12, 0.002, 0.02), (0.20, 0.32, 0.62, 1.0))
    elif kind == "yogurt":
        n, xs = fit(0.08)
        for i in range(n):
            x = xs + i * 0.08
            col = BRAND_TINTS[(k + i // 4) % len(BRAND_TINTS)]
            for st in range(2):
                make_cyl(f"{tag}_Yogurt_{i}_{st}", (x, Y(0.04), z0 + 0.045 + st * 0.09), 0.034, 0.088, (0.94, 0.94, 0.90, 1.0), segments=6)
                make_cyl(f"{tag}_Yogurt_{i}_{st}_Foil", (x, Y(0.04), z0 + 0.0905 + st * 0.09), 0.035, 0.003, col, segments=6)
    elif kind == "cheese":
        n, xs = fit(0.17)
        for i in range(n):
            x = xs + i * 0.17
            make_box(f"{tag}_Cheese_{i}", (x, Y(0.03), z0 + 0.11), (0.15, 0.03, 0.22),
                     ((0.94, 0.62, 0.18, 1.0), (0.96, 0.86, 0.50, 1.0))[(i + k) % 2])
            make_box(f"{tag}_Cheese_{i}_Seal", (x, Y(0.03), z0 + 0.225), (0.15, 0.03, 0.01), (0.94, 0.94, 0.92, 1.0))
            make_box(f"{tag}_Cheese_{i}_Window", (x, Y(0.0145), z0 + 0.08), (0.08, 0.002, 0.07), (0.98, 0.80, 0.40, 1.0))
    elif kind == "pasta":
        n, xs = fit(0.14)
        for i in range(n):
            x = xs + i * 0.14
            for st in range(2):
                make_box(f"{tag}_Pasta_{i}_{st}", (x, Y(0.10), z0 + 0.04 + st * 0.08), (0.12, 0.18, 0.075),
                         (0.18, 0.30, 0.62, 1.0) if (i + k) % 2 else (0.80, 0.18, 0.14, 1.0))
                make_box(f"{tag}_Pasta_{i}_{st}_Window", (x, Y(0.0085), z0 + 0.04 + st * 0.08), (0.07, 0.002, 0.035),
                         (0.92, 0.80, 0.50, 1.0))


def stock_gondola(prefix, anchor, *, length, levels, plan="convenience", sides=(-1, 1),
                  depth=0.70, seed=0, base_col=(0.22, 0.22, 0.24, 1.0), metal=STEEL,
                  tag_col=(0.94, 0.94, 0.92, 1.0), end_panels=True, axis='X', lean=False):
    """A gondola run centred on anchor=(cx, cy, bz), `length` along `axis`
    (X: an E-W run faced north and south; Y: a N-S run faced east and
    west): a base, a spine, shelf plates at `levels` (z of each plate's
    centre) on each side in `sides`, stocked from PLANS[plan]."""
    global _ROT, _LEAN
    if lean and not _LEAN:
        _LEAN = True
        try:
            return stock_gondola(prefix, anchor, length=length, levels=levels, plan=plan, sides=sides,
                                 depth=depth, seed=seed, base_col=base_col, metal=metal, tag_col=tag_col,
                                 end_panels=end_panels, axis=axis)
        finally:
            _LEAN = False
    if str(axis).upper() == 'Y':
        _ROT = (anchor[0], anchor[1])
        try:
            return stock_gondola(prefix, anchor, length=length, levels=levels, plan=plan, sides=sides,
                                 depth=depth, seed=seed, base_col=base_col, metal=metal, tag_col=tag_col,
                                 end_panels=end_panels, axis='X')
        finally:
            _ROT = None
    cx, cy, bz = anchor
    half = depth / 2.0
    top = max(levels) + 0.38
    make_box(f"{prefix}_Base", (cx, cy, bz + 0.10), (length, depth, 0.20), base_col)
    make_box(f"{prefix}_Shelving_Spine", (cx, cy, (bz + 0.20 + top) / 2.0), (length, 0.06, top - bz - 0.20), metal)
    rows = PLANS.get(plan, PLANS["convenience"])
    nsec = max(1, int(round(length / 0.50)))
    w = length / nsec
    for sh, z in enumerate(levels):
        row = rows[min(sh, len(rows) - 1)]
        for sgn in sides:
            front = cy + sgn * half
            make_box(f"{prefix}_Shelf_{sh}_y{sgn:+d}", (cx, cy + sgn * (half + 0.03) / 2.0, z), (length, half - 0.03, 0.03), metal)
            make_box(f"{prefix}_PriceStrip_{sh}_y{sgn:+d}", (cx, front + sgn * 0.003, z), (length, 0.006, 0.04), tag_col)
            for p in range(nsec):
                x0 = cx - length / 2.0 + p * w
                kind = row[(p + (2 if sgn > 0 else 0) + seed) % len(row)]
                merch_section(f"{prefix}_Stock_{sh}_y{sgn:+d}_{p}", kind, x0 + 0.01, front, sgn, z + 0.015,
                              seed * 13 + sh * 7 + p + (3 if sgn > 0 else 0), width=w - 0.02)
                make_box(f"{prefix}_PriceStrip_{sh}_y{sgn:+d}_Tag_{p}", (x0 + w * 0.25, front + sgn * 0.0065, z),
                         (0.05, 0.002, 0.028), (0.96, 0.84, 0.20, 1.0) if (p + sh + seed) % 4 == 0 else (0.98, 0.98, 0.96, 1.0))
    if end_panels:
        for e in (-1, 1):
            make_box(f"{prefix}_End_Panel_{e:+d}", (cx + e * (length / 2.0 + 0.02), cy, (bz + top) / 2.0), (0.04, depth, top - bz), metal)
    return top
