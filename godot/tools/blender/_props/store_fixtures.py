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
    # the top box spans base+height .. base+height+0.06; this returned
    # +0.04, so everything dressed from it sat 2 cm INSIDE the top in
    # 22 builders (2026-09-23 — the overlap gate's resting allowance hid it)
    counter_top_z = base_z + height + 0.06
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
                          segments=8, palette=None, axis='Y'):
    """Rounded front-edge bullnose along a counter top's customer
    face. Cuts the boxy AABB silhouette.

    axis='Y' (default, unchanged): the counter runs north-south and
    the bullnose lays along its west face — anchor=(west_edge_x,
    center_y, top_z).
    axis='X': the counter runs east-west and the bullnose lays along
    its south face — anchor=(center_x, south_edge_y, top_z). Added
    2026-08-12 for the New Orleans bar, whose 7m counter runs along
    X; without it the trim ran across the room and through a wall.
    """
    palette = palette or {}
    col = palette.get("top", P.COUNTER_TOP)
    cx, cy, top_z = anchor
    seg_len = length / segments
    for s in range(segments):
        off = (-length / 2.0) + (s + 0.5) * seg_len
        if str(axis).upper() == 'X':
            make_cyl(f"{prefix}_Bullnose_{s}",
                     (cx + off, cy, top_z - 0.03),
                     0.025, seg_len, col, axis='X', segments=8)
        else:
            make_cyl(f"{prefix}_Bullnose_{s}",
                     (cx, cy + off, top_z - 0.03),
                     0.025, seg_len, col, axis='Y', segments=8)


def make_register(prefix, anchor, *, palette=None, operator='+X'):
    """A cash register on a counter top. anchor=(center_x, center_y,
    counter_top_z). `operator` is the side the cashier stands on ('+X'
    default, '-X', '+Y', '-Y'): the keys and the drawer face it, the
    customer display the other way.

    (pass 453, 2026-11-25) The user, of the comic shop's till close-up:
    "That doesn't read as a register." It was four near-black boxes — a
    drawer, a body, a plate between them and a display — in nine rooms, and
    from the cashier's side a dark block. A register is its KEYS: so, in a
    putty case, the cash drawer with its face and pull; a low key deck
    toward the operator with a grid of pale keycaps and a column of
    coloured function keys; the taller back half with the operator's
    read-out on its face; a receipt printer with its paper standing out of
    the slot; the customer display on the -X edge (its place and size
    unchanged: a roster picture is laid on it).

    Draft N+1: the drawer OPEN with its bill wells for the lines that count
    the till (a per-view part); the key deck sloped rather than stepped.
    """
    palette = palette or {}
    body = palette.get("body", (0.72, 0.70, 0.64, 1.0))
    keys = palette.get("keys", (0.32, 0.32, 0.34, 1.0))
    screen = palette.get("screen", (0.10, 0.32, 0.16, 1.0))
    dark = (0.16, 0.16, 0.17, 1.0)
    drawer = (body[0] * 0.84, body[1] * 0.84, body[2] * 0.84, 1.0)
    cap = (0.93, 0.92, 0.87, 1.0)
    cx, cy, top_z = anchor
    op = str(operator).upper()
    assert op in ('+X', '-X', '+Y', '-Y'), operator
    _mb = globals()["make_box"]         # the module's; the name is shadowed below

    def make_box(name, c, sz, col):          # local frame: +x is the operator's side
        lx, ly = c[0] - cx, c[1] - cy
        if op == '+X':
            dx, dy, s2 = lx, ly, (sz[0], sz[1], sz[2])
        elif op == '-X':
            dx, dy, s2 = -lx, -ly, (sz[0], sz[1], sz[2])
        elif op == '+Y':
            dx, dy, s2 = -ly, lx, (sz[1], sz[0], sz[2])
        else:
            dx, dy, s2 = ly, -lx, (sz[1], sz[0], sz[2])
        return _mb(name, (cx + dx, cy + dy, c[2]), s2, col)
    # the cash drawer ON the counter, the body on the drawer (2026-09-22:
    # the drawer was buried 15 cm in the counter and the body hung 5 cm
    # over it, in eight rooms)
    make_box(f"{prefix}_Drawer", (cx, cy, top_z + 0.05), (0.50, 0.40, 0.10), drawer)
    make_box(f"{prefix}_Drawer_Face", (cx + 0.252, cy, top_z + 0.05), (0.006, 0.36, 0.07), body)
    make_box(f"{prefix}_Drawer_Pull", (cx + 0.258, cy, top_z + 0.074), (0.008, 0.16, 0.012), dark)
    make_box(f"{prefix}_Drawer_Lock", (cx + 0.256, cy + 0.14, top_z + 0.045), (0.004, 0.018, 0.018), dark)
    # the back half: the taller case
    make_box(f"{prefix}_Body", (cx - 0.095, cy, top_z + 0.265), (0.23, 0.40, 0.31), body)
    # the key deck, toward the operator
    make_box(f"{prefix}_Deck", (cx + 0.125, cy, top_z + 0.155), (0.21, 0.40, 0.09), body)
    make_box(f"{prefix}_Keypad", (cx + 0.125, cy, top_z + 0.202), (0.19, 0.36, 0.004), keys)
    fn = ((0.80, 0.22, 0.18, 1.0), (0.92, 0.78, 0.22, 1.0), (0.26, 0.62, 0.34, 1.0), (0.24, 0.42, 0.74, 1.0))
    for r in range(4):                      # rows, away from the operator
        kx = cx + 0.20 - r * 0.046
        for c in range(4):                  # the number block
            make_box(f"{prefix}_Key_{r}_{c}", (kx, cy - 0.15 + c * 0.062, top_z + 0.210), (0.032, 0.046, 0.012), cap)
        make_box(f"{prefix}_Key_{r}_Fn", (kx, cy + 0.135, top_z + 0.210), (0.032, 0.058, 0.012), fn[r])
    # the operator's read-out on the back half's face
    make_box(f"{prefix}_Readout", (cx + 0.023, cy - 0.04, top_z + 0.33), (0.006, 0.24, 0.06), screen)
    make_box(f"{prefix}_Readout_Digits", (cx + 0.027, cy - 0.01, top_z + 0.33), (0.002, 0.13, 0.026),
             (min(1.0, screen[0] + 0.5), min(1.0, screen[1] + 0.5), min(1.0, screen[2] + 0.5), 1.0))
    # the receipt printer, its paper out of the slot
    make_box(f"{prefix}_Printer", (cx - 0.07, cy + 0.12, top_z + 0.425), (0.12, 0.10, 0.01), dark)
    make_box(f"{prefix}_Receipt", (cx - 0.05, cy + 0.12, top_z + 0.465), (0.003, 0.076, 0.07), (0.96, 0.95, 0.92, 1.0))
    # the customer display (unchanged)
    make_box(f"{prefix}_Display",(cx - 0.22, cy, top_z + 0.43),
             (0.04, 0.34, 0.14), screen)


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
