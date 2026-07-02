# _props/shelving.py
# ════════════════════════════════════════════════════════════════
# Snack-aisle rows, end-cap displays, pegboard chip racks,
# magazine racks, OTC meds shelves. Reused across convenience
# stores, supermarkets, comic shops.
# ════════════════════════════════════════════════════════════════
from . import palette as P
from .geometry import make_box, make_cyl


def make_snack_aisle(prefix, anchor, *, length=6.0, shelf_count=5,
                     products_per_shelf=12, palette=None,
                     top_signs=None):
    """E-W snack aisle with N shelves on both sides + top signs.
    anchor=(center_x, run_center_y, base_z).
    top_signs: optional (south_label, north_label) tuple."""
    palette = palette or {}
    base = palette.get("base", P.COUNTER_DARK)
    shelf_metal = palette.get("shelf", P.METAL_STEEL)
    tints = palette.get("tints", P.SNACK_TINTS)
    cx, cy, bz = anchor
    # Base support
    make_box(f"{prefix}_Base", (cx, cy, bz + 0.10),
             (length, 0.70, 0.20), base)
    # 5 shelves both sides
    for sh in range(shelf_count):
        shz = bz + 0.34 + sh * 0.40
        for sy_sgn in (-1, +1):
            make_box(f"{prefix}_Shelf_{sh}_y{sy_sgn:+d}",
                     (cx, cy + sy_sgn * 0.32, shz),
                     (length, 0.04, 0.32), shelf_metal)
            make_box(f"{prefix}_PriceTag_{sh}_y{sy_sgn:+d}",
                     (cx, cy + sy_sgn * 0.32, shz - 0.10),
                     (length, 0.001, 0.04), P.PAPER)
            for p in range(products_per_shelf):
                px = -(length / 2.0) + (p + 0.5) * (length / products_per_shelf)
                tint = tints[(sh * 3 + p) % len(tints)]
                base_h_table = [0.18, 0.22, 0.26, 0.30, 0.16, 0.20]
                base_h: float = base_h_table[(sh + p) % len(base_h_table)]
                make_box(f"{prefix}_Snack_{sh}_y{sy_sgn:+d}_{p}",
                         (cx + px, cy + sy_sgn * 0.26,
                          shz + base_h / 2.0 + 0.02),
                         (length / products_per_shelf * 0.6, 0.20, base_h),
                         tint)
    # Optional top signs hanging from ceiling structure
    if top_signs is not None:
        label_text_tint = P.PAPER
        for k, (lbl_y_off, _lbl_text) in enumerate(zip([-0.34, +0.34], top_signs)):
            make_box(f"{prefix}_TopSign_BG_{k}",
                     (cx, cy + lbl_y_off, bz + 2.50),
                     (length * 0.95, 0.06, 0.24), P.BRAND_RED_KWIK)
            make_box(f"{prefix}_TopSign_Text_{k}",
                     (cx, cy + lbl_y_off + (0.001 if k == 0 else -0.001),
                      bz + 2.50),
                     (length * 0.75, 0.005, 0.12), label_text_tint)


def make_endcap(prefix, anchor, *, palette=None, shelves=4):
    """Slanted product end-cap stand. anchor=(center_x, center_y, base_z)."""
    palette = palette or {}
    base = palette.get("base", P.COUNTER_DARK)
    metal = palette.get("metal", P.METAL_STEEL)
    header = palette.get("header", P.BRAND_RED_KWIK)
    tints = palette.get("tints", P.SNACK_TINTS)
    cx, cy, bz = anchor
    make_box(f"{prefix}_Base", (cx, cy, bz + 0.12),
             (0.60, 0.80, 0.24), base)
    for sh in range(shelves):
        shz = bz + 0.40 + sh * 0.34
        make_box(f"{prefix}_Shelf_{sh}", (cx, cy, shz),
                 (0.62, 0.70, 0.02), metal)
        for p in range(4):
            px = -0.20 + p * 0.14
            tint = tints[(sh + p) % len(tints)]
            make_box(f"{prefix}_Product_{sh}_{p}",
                     (cx + px, cy, shz + 0.14),
                     (0.10, 0.50, 0.18), tint)
    make_box(f"{prefix}_Header", (cx, cy, bz + 0.40 + shelves * 0.34),
             (0.62, 0.78, 0.20), header)


def make_pegboard_chip_rack(prefix, anchor, *, palette=None,
                            rows=3, cols=4):
    """Wall-mounted peg-board with bags hanging from hooks.
    anchor=(wall_x, run_center_y, center_z)."""
    palette = palette or {}
    panel = palette.get("panel", (0.86, 0.74, 0.58, 1.0))
    tints = palette.get("tints", P.SNACK_TINTS)
    cx, cy, cz = anchor
    make_box(f"{prefix}_Panel", (cx, cy, cz),
             (0.04, cols * 0.28 + 0.20, rows * 0.24 + 0.30), panel)
    for r in range(rows):
        for c in range(cols):
            hook_y = cy - (cols - 1) / 2.0 * 0.28 + c * 0.28
            hook_z = cz + (rows - 1) / 2.0 * 0.24 - r * 0.24
            make_cyl(f"{prefix}_Hook_{r}_{c}",
                     (cx + 0.02, hook_y, hook_z),
                     0.005, 0.06, P.METAL_STEEL, axis='Y')
            tint = tints[(r * cols + c) % len(tints)]
            make_box(f"{prefix}_Bag_{r}_{c}",
                     (cx + 0.06, hook_y, hook_z - 0.06),
                     (0.005, 0.16, 0.20), tint)


def make_otc_meds_display(prefix, anchor, *, palette=None, tiers=2):
    """Small countertop medicine display with cylindrical bottles.
    anchor=(center_x, center_y, base_z)."""
    palette = palette or {}
    shelf = palette.get("shelf", P.METAL_STEEL)
    bottle_cap = palette.get("cap", P.PAPER)
    bottle_palette = palette.get("bottles", [
        (0.18, 0.32, 0.62, 1.0),
        (0.62, 0.18, 0.18, 1.0),
        (0.42, 0.62, 0.32, 1.0),
        (0.92, 0.78, 0.32, 1.0),
        (0.82, 0.82, 0.82, 1.0),
        (0.62, 0.42, 0.18, 1.0),
    ])
    sx, sy, bz = anchor
    make_box(f"{prefix}_Base", (sx, sy, bz),
             (0.24, 0.20, 0.02), shelf)
    for tier in range(tiers):
        tz = bz + 0.12 + tier * 0.14
        make_box(f"{prefix}_Tier_{tier}", (sx, sy, tz - 0.06),
                 (0.24, 0.20, 0.02), shelf)
        for bi in range(6):
            bx2 = sx - 0.08 + (bi % 3) * 0.08
            by2 = sy - 0.06 + (bi // 3) * 0.12
            bot_color = bottle_palette[bi % len(bottle_palette)]
            make_cyl(f"{prefix}_Bottle_{tier}_{bi}",
                     (bx2, by2, tz),
                     0.020, 0.10, bot_color)
            make_cyl(f"{prefix}_BottleCap_{tier}_{bi}",
                     (bx2, by2, tz + 0.06),
                     0.022, 0.012, bottle_cap)


def make_magazine_rack(prefix, anchor, *, palette=None, count=8):
    """Slanted magazine rack — N magazine fronts visible at an angle."""
    palette = palette or {}
    frame = palette.get("frame", P.METAL_STEEL)
    tints = palette.get("tints", P.SNACK_TINTS)
    cx, cy, bz = anchor
    make_box(f"{prefix}_Back", (cx, cy + 0.10, bz + 0.50),
             (0.04, 0.80, 1.00), frame)
    for mi in range(count):
        my = cy - (count - 1) / 2.0 * 0.18 + mi * 0.18
        mz = bz + 0.40
        tint = tints[mi % len(tints)]
        make_box(f"{prefix}_Mag_{mi}",
                 (cx, my, mz),
                 (0.30, 0.20, 0.005), tint)
