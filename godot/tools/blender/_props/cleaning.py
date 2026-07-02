# _props/cleaning.py
# ════════════════════════════════════════════════════════════════
# Janitorial / safety props: wet-floor cone, broom + mop, trash
# can, cigarette urn, trashbag. Reusable across all retail
# interiors.
# ════════════════════════════════════════════════════════════════
from . import palette as P
from .geometry import make_box, make_cyl


def make_wet_floor_cone(prefix, anchor, *, palette=None):
    """Yellow A-frame WET FLOOR cone. anchor=(cx, cy, base_z)."""
    palette = palette or {}
    yellow = palette.get("yellow", (0.96, 0.78, 0.18, 1.0))
    cx, cy, bz = anchor
    for sgn in (-1, +1):
        make_box(f"{prefix}_Panel_{sgn:+d}",
                 (cx + sgn * 0.18, cy, bz + 0.30),
                 (0.04, 0.30, 0.60), yellow)
        make_box(f"{prefix}_Text_{sgn:+d}",
                 (cx + sgn * 0.19, cy, bz + 0.40),
                 (0.004, 0.26, 0.10), P.METAL_BLACK)
    make_box(f"{prefix}_Foot", (cx, cy, bz + 0.02),
             (0.30, 0.30, 0.04), P.RUBBER_MAT)


def make_broom_mop(prefix, anchor, *, palette=None):
    """Broom + mop leaning in a corner. anchor=(broom_x, both_y, floor_z)."""
    palette = palette or {}
    broom = palette.get("broom_handle", (0.62, 0.46, 0.30, 1.0))
    brush = palette.get("brush", (0.74, 0.62, 0.42, 1.0))
    mop_metal = palette.get("mop", P.METAL_STEEL)
    mop_head = palette.get("mop_head", (0.82, 0.78, 0.72, 1.0))
    bx, by, bz = anchor
    # Broom
    make_cyl(f"{prefix}_BroomHandle", (bx, by, bz + 0.80),
             0.018, 1.60, broom, axis='Z')
    make_cyl(f"{prefix}_BroomHandleTop", (bx + 0.04, by, bz + 1.46),
             0.018, 0.30, broom, axis='Z')
    make_box(f"{prefix}_BroomBrush", (bx, by, bz + 0.06),
             (0.28, 0.06, 0.10), brush)
    # Mop (next to broom)
    mx = bx - 0.16
    make_cyl(f"{prefix}_MopHandle", (mx, by, bz + 0.80),
             0.018, 1.60, mop_metal, axis='Z')
    make_box(f"{prefix}_MopHead", (mx, by, bz + 0.08),
             (0.18, 0.20, 0.10), mop_head)


def make_trash_can(prefix, anchor, *, palette=None, branded=True):
    """Cylindrical swing-lid trash can. anchor=(cx, cy, base_z)."""
    palette = palette or {}
    body = palette.get("body", P.BRAND_RED_KWIK)
    band = palette.get("band", P.PAPER)
    lid = palette.get("lid", P.METAL_BLACK)
    cx, cy, bz = anchor
    make_cyl(f"{prefix}_Body", (cx, cy, bz + 0.50), 0.30, 1.00, body)
    if branded:
        make_cyl(f"{prefix}_BrandBand", (cx, cy, bz + 0.70),
                 0.31, 0.16, band)
    make_cyl(f"{prefix}_Lid", (cx, cy, bz + 1.04), 0.32, 0.04, lid)
    make_box(f"{prefix}_FlapSlot", (cx, cy, bz + 1.00),
             (0.32, 0.02, 0.04), P.METAL_STEEL)


def make_trashbag(prefix, anchor, *, palette=None):
    """Tied-off black trash bag at a doorway threshold."""
    palette = palette or {}
    col = palette.get("col", (0.10, 0.10, 0.12, 1.0))
    bx, by, bz = anchor
    make_cyl(f"{prefix}_Body", (bx, by, bz + 0.30), 0.20, 0.60, col)
    make_cyl(f"{prefix}_Tie", (bx, by, bz + 0.60), 0.04, 0.06, col)
    make_cyl(f"{prefix}_Crinkle", (bx, by, bz + 0.40), 0.22, 0.20, col)


def make_cigarette_urn(prefix, anchor, *, palette=None):
    """Sand-topped cigarette urn outside a doorway."""
    palette = palette or {}
    body = palette.get("body", P.METAL_STEEL)
    sand = palette.get("sand", (0.72, 0.62, 0.42, 1.0))
    cx, cy, bz = anchor
    make_cyl(f"{prefix}_Body", (cx, cy, bz + 0.40), 0.14, 0.80, body)
    make_cyl(f"{prefix}_Sand", (cx, cy, bz + 0.81), 0.13, 0.04, sand)
    import math
    for bi in range(5):
        ang = bi * 1.25
        bxx = cx + math.cos(ang) * 0.06
        byy = cy + math.sin(ang) * 0.06
        make_box(f"{prefix}_Butt_{bi}",
                 (bxx, byy, bz + 0.84),
                 (0.012, 0.012, 0.04), P.PAPER_AGED)
