# _props/store_fixtures.py
# ════════════════════════════════════════════════════════════════
# Counter-and-register fixtures shared across convenience stores,
# diners, comic shops, bakeries — anywhere a clerk faces a
# customer across formica.
#
# Each function takes a `prefix` (so multiple instances don't
# collide), an `anchor` tuple in Blender coords, and an optional
# `palette` dict to override the canon defaults from palette.py.
#
# DESIGN NOTE — orientation is up to the caller. All anchors assume
# customer-facing-west (counter face at lower X than anchor.x).
# If a different locale needs a customer-facing-north counter, mirror
# X<->Y in the caller. Library doesn't bake an orientation choice.
# ════════════════════════════════════════════════════════════════
from . import palette as P
from .geometry import make_box, make_cyl


def make_counter(prefix, anchor, *, length=4.40, depth=1.00,
                 height=1.00, top_overhang=0.10, palette=None):
    """L-shape standalone counter. anchor=(center_x, center_y, base_z).
    Returns the (counter_top_z) so chained fixtures can sit on it."""
    palette = palette or {}
    formica = palette.get("formica",   P.COUNTER_FORMICA)
    top_col = palette.get("top",       P.COUNTER_TOP)
    dark    = palette.get("kick",      P.COUNTER_DARK)
    cx, cy, base_z = anchor
    counter_top_z = base_z + height + 0.04
    # Front counter (customer-facing west face)
    make_box(f"{prefix}_Front",
             (cx, cy, base_z + height / 2.0),
             (depth, length, height), formica)
    # Counter top (slight overhang)
    make_box(f"{prefix}_Top",
             (cx, cy, base_z + height + 0.03),
             (depth + top_overhang, length + top_overhang, 0.06), top_col)
    # Kick panel
    make_box(f"{prefix}_Kick",
             (cx - depth / 2.0 - 0.01, cy, base_z + 0.10),
             (0.02, length, 0.20), dark)
    return counter_top_z


def make_counter_bullnose(prefix, anchor, *, length=4.40,
                          segments=8, palette=None):
    """Rounded front-edge bullnose along the counter top's west face.
    Cuts the boxy AABB silhouette. anchor=(west_edge_x, center_y, top_z)."""
    palette = palette or {}
    col = palette.get("top", P.COUNTER_TOP)
    cx, cy, top_z = anchor
    seg_len = length / segments
    for s in range(segments):
        sy = (cy - length / 2.0) + (s + 0.5) * seg_len
        make_cyl(f"{prefix}_Bullnose_{s}",
                 (cx, sy, top_z - 0.03),
                 0.025, seg_len, col, axis='Y', segments=8)


def make_register(prefix, anchor, *, palette=None):
    """1990s point-of-sale terminal sitting on a counter top.
    anchor=(center_x, center_y, counter_top_z)."""
    palette = palette or {}
    body = palette.get("body", (0.22, 0.20, 0.22, 1.0))
    keys = palette.get("keys", (0.32, 0.32, 0.34, 1.0))
    screen = palette.get("screen", (0.10, 0.32, 0.16, 1.0))
    cx, cy, top_z = anchor
    make_box(f"{prefix}_Body",   (cx, cy, top_z + 0.21),
             (0.42, 0.40, 0.32), body)
    make_box(f"{prefix}_Display",(cx - 0.22, cy, top_z + 0.38),
             (0.04, 0.34, 0.14), screen)
    make_box(f"{prefix}_Keypad", (cx, cy, top_z + 0.06),
             (0.36, 0.36, 0.02), keys)
    make_box(f"{prefix}_Drawer", (cx, cy, top_z - 0.10),
             (0.50, 0.40, 0.10), body)


def make_cigarette_rack(prefix, anchor, *, shelves=3, columns=12,
                        col_span=0.28, shelf_step=0.32,
                        palette=None):
    """Wall-mounted tobacco rack — N shelves of color-cycled packs.
    Caller positions it FLUSH against a wall (anchor.x ~= wall face).
    anchor=(rack_x, run_center_y, first_shelf_z)."""
    palette = palette or {}
    shelf_metal = palette.get("shelf", P.METAL_STEEL)
    tints = palette.get("tints", P.SNACK_TINTS)
    rx, ry, base_z = anchor
    for sh in range(shelves):
        shz = base_z + sh * shelf_step
        # Shelf plate
        make_box(f"{prefix}_Shelf_{sh}",
                 (rx, ry, shz),
                 (0.02, columns * col_span, 0.04), shelf_metal)
        # Boxes along the shelf
        for c in range(columns):
            cy_pos = ry - (columns / 2.0 - 0.5) * col_span + c * col_span
            tint = tints[(sh + c) % len(tints)]
            make_box(f"{prefix}_Box_{sh}_{c}",
                     (rx + 0.04, cy_pos, shz + 0.10),
                     (0.06, 0.18, 0.16), tint)
            # Brand band on front face
            make_box(f"{prefix}_Band_{sh}_{c}",
                     (rx + 0.075, cy_pos, shz + 0.06),
                     (0.005, 0.16, 0.04), P.METAL_BLACK)


def make_lottery_display(prefix, anchor, *, palette=None):
    """Powerball / scratch-off vertical display panel. Mounted on
    east wall behind counter typically. anchor=(panel_x, center_y, base_z)."""
    palette = palette or {}
    yel = palette.get("yellow", P.LOTTERY_YEL)
    red = palette.get("red", P.LOTTERY_RED)
    panel = palette.get("panel", P.METAL_STEEL)
    cx, cy, base_z = anchor
    make_box(f"{prefix}_Box", (cx, cy, base_z),
             (0.02, 0.60, 0.40), panel)
    make_box(f"{prefix}_BannerY",
             (cx - 0.005, cy, base_z + 0.16),
             (0.005, 0.56, 0.10), yel)
    make_box(f"{prefix}_BannerR",
             (cx - 0.005, cy, base_z + 0.04),
             (0.005, 0.56, 0.10), red)
    for t in range(5):
        ty = cy - 0.20 + t * 0.10
        make_box(f"{prefix}_Ticket_{t}",
                 (cx - 0.010, ty, base_z - 0.16),
                 (0.005, 0.08, 0.10), P.SNACK_TINTS[t % len(P.SNACK_TINTS)])


def make_credit_card_terminal(prefix, anchor, *, palette=None):
    """PIN-pad / card terminal on counter, customer-facing.
    anchor=(center_x, center_y, counter_top_z)."""
    palette = palette or {}
    body = palette.get("body", (0.32, 0.34, 0.36, 1.0))
    screen = palette.get("screen", (0.32, 0.46, 0.40, 1.0))
    cx, cy, top_z = anchor
    make_box(f"{prefix}_Body", (cx, cy, top_z + 0.06),
             (0.18, 0.26, 0.12), body)
    make_box(f"{prefix}_Screen",
             (cx, cy - 0.131, top_z + 0.10),
             (0.12, 0.005, 0.06), screen)
    for r in range(4):
        for c in range(3):
            make_box(f"{prefix}_Key_{r}_{c}",
                     (cx - 0.05 + c * 0.05,
                      cy,
                      top_z + 0.04 - r * 0.018),
                     (0.04, 0.005, 0.012), P.PAPER_AGED)
    make_box(f"{prefix}_Slot", (cx, cy + 0.13, top_z + 0.06),
             (0.14, 0.005, 0.012), P.METAL_BLACK)
