# _props/decor.py
# ════════════════════════════════════════════════════════════════
# Wall + ceiling + counter ornamentation — the things that fill
# the room but aren't transactional fixtures. Wall clock, faded
# poster, payphone, calendar, hanging air freshener tree, etc.
# Reusable across any indoor locale.
# ════════════════════════════════════════════════════════════════
import math
from . import palette as P
from .geometry import make_box, make_cyl


def make_wall_clock(prefix, anchor, *, frozen_hour=11, frozen_min=47,
                    palette=None):
    """Wall-mounted analog clock. anchor=(wall_x, wall_y, center_z).
    Wall_y is the wall's nearest face — clock barrel extends 4cm.
    Frozen time defaults to 11:47 (canon vol6 Sam-shift hour);
    pass (frozen_hour, frozen_min) to override for other locales."""
    palette = palette or {}
    face = palette.get("face", (0.94, 0.92, 0.86, 1.0))
    rim = palette.get("rim", (0.42, 0.40, 0.36, 1.0))
    cx, cy, cz = anchor
    make_cyl(f"{prefix}_Face", (cx, cy, cz), 0.18, 0.04, face, axis='Y')
    make_cyl(f"{prefix}_Rim", (cx, cy - 0.022, cz),
             0.20, 0.02, rim, axis='Y')
    for ang_i, (mx, mz) in enumerate([(0.0, +0.13), (+0.13, 0.0),
                                       (0.0, -0.13), (-0.13, 0.0)]):
        make_box(f"{prefix}_Tick_{ang_i}",
                 (cx + mx, cy - 0.025, cz + mz),
                 (0.02, 0.005, 0.02), P.METAL_BLACK)
    # Hands — point to frozen_hour / frozen_min on a 12-hour clock face
    hour_ang = ((frozen_hour % 12) + frozen_min / 60.0) * (math.pi * 2 / 12) - math.pi / 2
    min_ang = (frozen_min / 60.0) * (math.pi * 2) - math.pi / 2
    h_len = 0.10
    m_len = 0.16
    make_box(f"{prefix}_HourHand",
             (cx + math.cos(hour_ang) * h_len * 0.5,
              cy - 0.030,
              cz + math.sin(hour_ang) * h_len * 0.5),
             (0.05, 0.004, 0.05), P.METAL_BLACK)
    make_box(f"{prefix}_MinuteHand",
             (cx + math.cos(min_ang) * m_len * 0.5,
              cy - 0.030,
              cz + math.sin(min_ang) * m_len * 0.5),
             (0.08, 0.004, 0.05), P.METAL_BLACK)


def make_fire_extinguisher(prefix, anchor, *, palette=None):
    """Wall-bracketed red fire extinguisher. anchor=(wall_x, wall_y, base_z)."""
    palette = palette or {}
    red = palette.get("red", (0.74, 0.16, 0.14, 1.0))
    ex, ey, ez = anchor
    make_cyl(f"{prefix}_Body", (ex, ey, ez + 0.86), 0.10, 0.50, red)
    make_cyl(f"{prefix}_Top", (ex, ey, ez + 1.20), 0.08, 0.18,
             P.METAL_BLACK)
    make_box(f"{prefix}_Bracket", (ex - 0.04, ey, ez + 0.86),
             (0.04, 0.18, 0.50), P.METAL_STEEL)
    make_box(f"{prefix}_Sign", (ex - 0.02, ey - 0.40, ez + 1.60),
             (0.005, 0.30, 0.30), red)


def make_payphone(prefix, anchor, *, palette=None):
    """Wall-mounted period payphone. anchor=(wall_x, wall_y, center_z)."""
    palette = palette or {}
    body = palette.get("body", (0.32, 0.30, 0.30, 1.0))
    trim = palette.get("trim", (0.20, 0.18, 0.18, 1.0))
    px, py, pz = anchor
    make_box(f"{prefix}_Box", (px, py, pz), (0.06, 0.34, 0.60), body)
    make_box(f"{prefix}_Hood", (px - 0.16, py, pz + 0.44),
             (0.30, 0.36, 0.10), trim)
    make_box(f"{prefix}_Handset",
             (px - 0.06, py - 0.20, pz),
             (0.04, 0.04, 0.24), trim)
    make_box(f"{prefix}_CoinSlot",
             (px - 0.04, py + 0.08, pz + 0.16),
             (0.02, 0.10, 0.02), P.METAL_BLACK)
    make_box(f"{prefix}_Keypad",
             (px - 0.04, py, pz - 0.12),
             (0.02, 0.16, 0.20), P.METAL_BLACK)
    for r in range(4):
        for c in range(3):
            make_box(f"{prefix}_Key_{r}_{c}",
                     (px - 0.05,
                      py - 0.06 + c * 0.06,
                      pz - 0.20 + r * 0.045),
                     (0.005, 0.04, 0.034), P.PAPER_AGED)


def make_calendar(prefix, anchor, *, palette=None):
    """Wall calendar with a faded photograph + month grid."""
    palette = palette or {}
    paper = palette.get("paper", (0.78, 0.62, 0.46, 1.0))
    cx, cy, cz = anchor
    make_box(f"{prefix}_Body", (cx, cy, cz),
             (0.005, 0.40, 0.50), paper)
    make_box(f"{prefix}_Grid", (cx + 0.002, cy, cz - 0.15),
             (0.001, 0.34, 0.20), P.PAPER)


def make_faded_poster(prefix, anchor, *, palette=None):
    """Sun-faded vintage poster on a wall. anchor=(wall_x, wall_y, center_z)."""
    palette = palette or {}
    body = palette.get("body", (0.78, 0.62, 0.46, 1.0))
    ink = palette.get("ink", (0.32, 0.24, 0.20, 1.0))
    cx, cy, cz = anchor
    make_box(f"{prefix}_Body", (cx, cy, cz),
             (0.005, 0.60, 0.80), body)
    make_box(f"{prefix}_Title", (cx + 0.005 * (1 if cx >= 0 else -1),
                                 cy, cz - 0.30),
             (0.002, 0.50, 0.10), ink)
    make_box(f"{prefix}_Figure", (cx + 0.005 * (1 if cx >= 0 else -1),
                                  cy, cz + 0.20),
             (0.002, 0.36, 0.40), ink)


def make_air_freshener_tree(prefix, anchor, *, count=3, palette=None):
    """Pine-tree air-fresheners hanging on a wire above the register."""
    palette = palette or {}
    colors = palette.get("colors", [
        (0.42, 0.52, 0.36, 1.0),    # pine green
        (0.74, 0.32, 0.20, 1.0),    # cherry rust
        (0.42, 0.52, 0.62, 1.0),    # dusty blue
    ])
    bx, by, base_z = anchor
    make_box(f"{prefix}_Wire", (bx, by, base_z + 0.18),
             (0.005, 0.005, 0.36), P.METAL_BLACK)
    for ti in range(count):
        ty = by + (ti - (count - 1) / 2.0) * 0.06
        col = colors[ti % len(colors)]
        for tier in range(3):
            scale = 0.10 - tier * 0.025
            make_box(f"{prefix}_{ti}_Tier_{tier}",
                     (bx, ty, base_z - 0.04 + tier * 0.04),
                     (0.005, scale, 0.04), col)
        make_box(f"{prefix}_{ti}_Trunk",
                 (bx, ty, base_z - 0.18),
                 (0.005, 0.02, 0.06), (0.42, 0.30, 0.20, 1.0))


def make_floor_plant(prefix, anchor, *, palette=None):
    """Decorative leafy potted plant on the floor."""
    palette = palette or {}
    leaf = palette.get("leaf", (0.42, 0.52, 0.36, 1.0))
    pot = palette.get("pot", (0.46, 0.34, 0.22, 1.0))
    px, py, base_z = anchor
    for r in range(3):
        make_cyl(f"{prefix}_Pot_{r}",
                 (px, py, base_z + 0.20 + r * 0.06),
                 0.18 - r * 0.02, 0.06, pot)
    for li, lz in enumerate([0.42, 0.50, 0.58, 0.64]):
        for ang_i in range(6):
            ang = ang_i * (math.pi * 2.0 / 6.0) + li * 0.3
            ox = math.cos(ang) * 0.16
            oy = math.sin(ang) * 0.16
            make_cyl(f"{prefix}_Leaf_{li}_{ang_i}",
                     (px + ox, py + oy, base_z + lz),
                     0.04, 0.08, leaf)
