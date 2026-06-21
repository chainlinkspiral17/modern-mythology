# _props/coolers_drinks.py
# ════════════════════════════════════════════════════════════════
# Beverage fixtures — beer/soda coolers, slurpee fountains, soda
# bottle pyramids, can rows. Reused across convenience-store,
# diner, and bar locales.
# ════════════════════════════════════════════════════════════════
import math
from . import palette as P
from .geometry import make_box, make_cyl


def make_cooler_door(prefix, anchor, *,
                     shelves=5, cans_per_shelf=6, sixpacks_per_shelf=5,
                     palette=None, include_six_packs=True,
                     include_cans=True):
    """A single glass-front beverage cooler door, wall-recessed.
    anchor=(door_center_x, wall_y, door_center_z).
    Caller chains multiple doors along a wall."""
    palette = palette or {}
    glass = palette.get("glass", P.COOLER_GLASS)
    interior = palette.get("interior", P.COOLER_INTERIOR)
    steel = palette.get("steel", P.METAL_STEEL)
    handle = palette.get("handle", P.METAL_BLACK)
    tints = palette.get("tints", P.SNACK_TINTS)
    cx, wall_y, cz = anchor
    # Interior box
    make_box(f"{prefix}_Interior",
             (cx, wall_y + 0.30, cz),
             (1.30, 0.40, 2.20), interior)
    # Back mirror (recursion canon)
    make_box(f"{prefix}_BackMirror",
             (cx, wall_y + 0.485, cz),
             (1.20, 0.005, 2.10), (0.18, 0.30, 0.42, 0.85))
    # Glass front
    make_box(f"{prefix}_Glass",
             (cx, wall_y + 0.06, cz),
             (1.24, 0.04, 2.10), glass)
    # Frame
    for sgn, label in [(-1, 'L'), (+1, 'R')]:
        make_box(f"{prefix}_Frame_{label}",
                 (cx + sgn * 0.62, wall_y + 0.04, cz),
                 (0.04, 0.08, 2.10), steel)
    make_box(f"{prefix}_Frame_T", (cx, wall_y + 0.04, cz + 1.06),
             (1.30, 0.08, 0.04), steel)
    make_box(f"{prefix}_Frame_B", (cx, wall_y + 0.04, cz - 1.06),
             (1.30, 0.08, 0.04), steel)
    # Handle
    make_box(f"{prefix}_Handle",
             (cx + 0.60, wall_y + 0.02, cz),
             (0.02, 0.06, 0.60), handle)
    # Grab-bar cylinder lower
    make_cyl(f"{prefix}_Grab",
             (cx + 0.62, wall_y + 0.03, cz - 0.70),
             0.014, 0.18, steel, axis='X', segments=8)
    # Rubber-gasket trim
    for sgn in (-1, +1):
        make_cyl(f"{prefix}_Gasket_{sgn}",
                 (cx, wall_y + 0.05, cz + sgn * 1.04),
                 0.008, 1.20, (0.12, 0.12, 0.14, 1.0), axis='X')
    # Shelves + product
    for sh in range(shelves):
        shz = cz - 0.90 + sh * 0.42
        make_box(f"{prefix}_Shelf_{sh}",
                 (cx, wall_y + 0.30, shz),
                 (1.20, 0.30, 0.02), steel)
        if include_six_packs:
            for b in range(sixpacks_per_shelf):
                bx = cx - 0.48 + b * 0.24
                tint = tints[(sh + b) % len(tints)]
                make_box(f"{prefix}_Sixpack_{sh}_{b}",
                         (bx, wall_y + 0.30, shz + 0.20),
                         (0.20, 0.22, 0.30), tint)
        if include_cans:
            for c in range(cans_per_shelf):
                bx = cx - 0.50 + c * 0.20
                tint = tints[(sh + c + 3) % len(tints)]
                make_cyl(f"{prefix}_Can_{sh}_{c}",
                         (bx, wall_y + 0.16, shz + 0.08),
                         0.04, 0.16, tint)
                make_cyl(f"{prefix}_CanLid_{sh}_{c}",
                         (bx, wall_y + 0.16, shz + 0.16),
                         0.04, 0.01, (0.78, 0.80, 0.82, 1.0))


def make_cooler_row(prefix, wall_y, door_centres, cz=1.30, **kwargs):
    """Convenience: build N cooler doors along a north wall.
    door_centres is an iterable of X coords."""
    for i, cx in enumerate(door_centres):
        make_cooler_door(f"{prefix}_{i}", (cx, wall_y, cz), **kwargs)


def make_slurpee_fountain(prefix, anchor, *, flavors=2, palette=None):
    """N-barrel frozen-drink fountain. anchor=(center_x, center_y, counter_z).
    Default 2 flavors (blue raspberry / cherry red); pass flavors=3 for
    a triple-barrel."""
    palette = palette or {}
    case = palette.get("case", (0.92, 0.94, 0.92, 1.0))
    steel = palette.get("steel", P.METAL_STEEL)
    cx, cy, base_z = anchor
    flavor_cols = palette.get("flavor_cols", [
        (0.34, 0.42, 0.58, 1.0),    # dusty blue
        (0.74, 0.28, 0.20, 1.0),    # muted cherry
        (0.46, 0.58, 0.42, 1.0),    # sage (lime)
    ])
    make_box(f"{prefix}_Base", (cx, cy, base_z),
             (0.86, 0.50, 0.30), steel)
    for bi in range(flavors):
        by_off = -0.18 + bi * 0.36
        col = flavor_cols[bi % len(flavor_cols)]
        make_cyl(f"{prefix}_Barrel_{bi}",
                 (cx, cy + by_off, base_z + 0.46),
                 0.16, 0.50, case)
        make_cyl(f"{prefix}_Liquid_{bi}",
                 (cx, cy + by_off, base_z + 0.36),
                 0.14, 0.28, col)
        make_cyl(f"{prefix}_Top_{bi}",
                 (cx, cy + by_off, base_z + 0.74),
                 0.16, 0.06, P.METAL_BLACK)
        make_box(f"{prefix}_Handle_{bi}",
                 (cx + 0.20, cy + by_off, base_z + 0.30),
                 (0.04, 0.06, 0.20), P.METAL_BLACK)
        make_box(f"{prefix}_DripTray_{bi}",
                 (cx + 0.18, cy + by_off, base_z + 0.16),
                 (0.16, 0.20, 0.04), steel)


def make_soda_bottle_pyramid(prefix, anchor, *,
                             tiers=3, base_count=4, bottle_h=0.30,
                             bottle_r=0.07, palette=None):
    """3-tier 2L bottle pyramid. Default Coke/Pepsi/Sprite cycle."""
    palette = palette or {}
    bottles = palette.get("bottles", [
        ((0.74, 0.28, 0.20, 1.0), (0.92, 0.92, 0.88, 1.0)),  # Coke
        ((0.34, 0.42, 0.58, 1.0), (0.92, 0.92, 0.88, 1.0)),  # Pepsi
        ((0.46, 0.58, 0.42, 1.0), (0.92, 0.92, 0.88, 1.0)),  # Sprite
    ])
    bx, by, base_z = anchor
    spacing = bottle_r * 2.2
    for ti in range(tiers):
        count = base_count - ti
        tier_z = base_z + ti * (bottle_h + 0.02)
        offset = -(count - 1) * spacing / 2.0 + ti * (spacing / 2.0)
        for ci in range(count):
            col, cap = bottles[ci % len(bottles)]
            x_off = offset + ci * spacing
            make_cyl(f"{prefix}_T{ti}_{ci}",
                     (bx + x_off, by, tier_z),
                     bottle_r, bottle_h, col)
            make_cyl(f"{prefix}_T{ti}_Cap_{ci}",
                     (bx + x_off, by, tier_z + bottle_h * 0.55),
                     bottle_r * 0.7, bottle_h * 0.2, cap)


def make_ice_machine(prefix, anchor, *, palette=None):
    """Front-loader chest ice maker. anchor=(center_x, center_y, base_z)."""
    palette = palette or {}
    body = palette.get("body", P.METAL_STEEL)
    lid = palette.get("lid", (0.42, 0.74, 0.92, 1.0))
    cx, cy, base_z = anchor
    make_box(f"{prefix}_Body", (cx, cy, base_z + 0.80),
             (1.10, 1.20, 1.60), body)
    make_box(f"{prefix}_Top", (cx, cy, base_z + 1.62),
             (1.14, 1.24, 0.06), P.METAL_BLACK)
    make_box(f"{prefix}_Lid", (cx + 0.10, cy, base_z + 1.66),
             (0.94, 1.04, 0.04), lid)
    make_box(f"{prefix}_Sign", (cx - 0.50, cy, base_z + 1.20),
             (0.02, 0.80, 0.30), lid)
    make_box(f"{prefix}_SignText", (cx - 0.51, cy, base_z + 1.20),
             (0.005, 0.40, 0.16), P.PAPER)
    make_box(f"{prefix}_DrainPan", (cx, cy, base_z + 0.04),
             (1.20, 1.30, 0.04), P.METAL_BLACK)
