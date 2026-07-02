# _props/food_service.py
# ════════════════════════════════════════════════════════════════
# Coffee stations, hot food cases, pizza warmers, donut displays,
# slurpee fountains — fixtures shared across diners, convenience
# stores, and bakeries.
#
# Slurpee fountain lives in coolers_drinks.py since it's a beverage
# dispenser; everything else (food-side serving) lives here.
# ════════════════════════════════════════════════════════════════
import math
from . import palette as P
from .geometry import make_box, make_cyl


def make_hot_food_case(prefix, anchor, *, palette=None,
                       hot_items=3):
    """Heated glass-front display case. anchor=(center_x, center_y, base_z).
    Default 3 hot items inside; pass hot_items=N for more."""
    palette = palette or {}
    body = palette.get("body", (0.94, 0.92, 0.84, 1.0))
    glass = palette.get("glass", P.GLASS)
    lamp = palette.get("lamp", (1.0, 0.78, 0.32, 1.0))
    cx, cy, bz = anchor
    make_box(f"{prefix}_Body", (cx, cy, bz),
             (0.50, 0.70, 0.60), body)
    make_box(f"{prefix}_Glass", (cx - 0.22, cy, bz),
             (0.04, 0.70, 0.58), glass)
    make_box(f"{prefix}_Lamp", (cx, cy, bz + 0.25),
             (0.50, 0.70, 0.04), lamp)
    for i in range(hot_items):
        y_off = -0.24 + i * (0.48 / max(1, hot_items - 1))
        make_box(f"{prefix}_Item_{i}", (cx - 0.08, cy + y_off, bz - 0.12),
                 (0.20, 0.14, 0.08), (0.78, 0.58, 0.40, 1.0))


def make_taquito_roller(prefix, anchor, *, palette=None, count=2):
    """Convenience-store taquito / hot-dog roller rods.
    anchor=(center_x, center_y, base_z)."""
    palette = palette or {}
    col = palette.get("col", (0.42, 0.32, 0.20, 1.0))
    cx, cy, bz = anchor
    for i in range(count):
        make_cyl(f"{prefix}_Rod_{i}",
                 (cx + 0.05, cy + 0.20 - i * 0.10, bz),
                 0.04, 0.50, col, segments=8, axis='X')


def make_pizza_warmer(prefix, anchor, *, palette=None, pans=3):
    """Pizza-warmer case with heat lamp. anchor=(center_x, center_y, base_z)."""
    palette = palette or {}
    body = palette.get("body", P.METAL_STEEL)
    glass = palette.get("glass", P.GLASS)
    heat = palette.get("heat_lamp", (1.0, 0.74, 0.34, 1.0))
    cheese = palette.get("cheese", (0.86, 0.62, 0.32, 1.0))
    cx, cy, bz = anchor
    make_box(f"{prefix}_Body", (cx, cy, bz),
             (0.50, 0.50, 0.42), body)
    make_box(f"{prefix}_Glass", (cx - 0.26, cy, bz),
             (0.04, 0.50, 0.38), glass)
    for pi in range(pans):
        py_off = (pi - (pans - 1) / 2.0) * (0.36 / max(1, pans - 1))
        make_cyl(f"{prefix}_Pan_{pi}", (cx, cy + py_off, bz - 0.10),
                 0.14, 0.02, body)
        make_cyl(f"{prefix}_Cheese_{pi}", (cx, cy + py_off, bz - 0.085),
                 0.13, 0.012, cheese)
        # 4 pepperoni dots
        for di in range(4):
            ang = di * 1.57
            dx = math.cos(ang) * 0.06
            dy = math.sin(ang) * 0.06
            make_cyl(f"{prefix}_Pep_{pi}_{di}",
                     (cx + dx, cy + py_off + dy, bz - 0.07),
                     0.018, 0.005, (0.74, 0.18, 0.16, 1.0))
    make_box(f"{prefix}_HeatLamp", (cx, cy, bz + 0.25),
             (0.46, 0.46, 0.04), heat)


def make_donut_display(prefix, anchor, *, palette=None, tiers=3):
    """Glass-front donut case with N tiers of round donuts.
    anchor=(center_x, center_y, base_z)."""
    palette = palette or {}
    body = palette.get("body", P.METAL_STEEL)
    tray = palette.get("tray", (0.86, 0.86, 0.84, 1.0))
    glaze = palette.get("glaze", (0.92, 0.78, 0.46, 1.0))
    pink = palette.get("pink", (0.96, 0.62, 0.78, 1.0))
    choc = palette.get("choc", (0.32, 0.20, 0.12, 1.0))
    dx, dy, bz = anchor
    make_box(f"{prefix}_CaseBody", (dx, dy, bz + 0.30),
             (0.86, 0.40, 0.60), body)
    make_box(f"{prefix}_CaseGlass", (dx + 0.21, dy, bz + 0.30),
             (0.04, 0.36, 0.56), P.GLASS)
    tier_colors = [glaze, choc, pink]
    for tier in range(tiers):
        tray_z = bz + 0.12 + tier * 0.18
        make_box(f"{prefix}_Tray_{tier}", (dx, dy, tray_z),
                 (0.74, 0.34, 0.02), tray)
        for di in range(4):
            dcol = tier_colors[(tier + di) % len(tier_colors)]
            d_off_y = -0.12 + di * 0.08
            make_cyl(f"{prefix}_Donut_{tier}_{di}",
                     (dx, dy + d_off_y, tray_z + 0.04),
                     0.035, 0.025, dcol)
            make_cyl(f"{prefix}_DonutHole_{tier}_{di}",
                     (dx, dy + d_off_y, tray_z + 0.05),
                     0.012, 0.025, P.METAL_BLACK)


def make_coffee_pots(prefix, anchor, *, palette=None, pots=3):
    """Drip-coffee pots on a backbar. anchor=(center_x, center_y, base_z)."""
    palette = palette or {}
    glass = palette.get("glass", P.GLASS)
    liquids = palette.get("liquids", [
        (0.18, 0.10, 0.06, 1.0),    # dark
        (0.32, 0.18, 0.10, 1.0),    # medium
        (0.42, 0.32, 0.20, 1.0),    # decaf
    ])
    cx, cy, bz = anchor
    for i in range(pots):
        py = cy - 0.50 + i * 0.50
        col = liquids[i % len(liquids)]
        make_cyl(f"{prefix}_Pot_{i}_Body", (cx + 0.05, py, bz + 0.13),
                 0.08, 0.26, glass)
        make_cyl(f"{prefix}_Pot_{i}_Liquid", (cx + 0.05, py, bz + 0.07),
                 0.068, 0.16, col)
        make_cyl(f"{prefix}_Pot_{i}_Burner", (cx + 0.05, py, bz - 0.06),
                 0.10, 0.02, P.METAL_BLACK)
        make_box(f"{prefix}_Pot_{i}_Handle", (cx + 0.16, py, bz + 0.13),
                 (0.06, 0.04, 0.10), P.METAL_BLACK)
        make_box(f"{prefix}_Pot_{i}_Label", (cx + 0.05, py, bz + 0.42),
                 (0.20, 0.18, 0.10), col)


def make_sugar_creamer_caddy(prefix, anchor, *, palette=None):
    """Sugar packets + creamer-cup stack + stirrers on a small tray."""
    palette = palette or {}
    caddy = palette.get("caddy", (0.94, 0.94, 0.88, 1.0))
    cx, cy, bz = anchor
    make_box(f"{prefix}_Tray", (cx, cy, bz),
             (0.40, 0.30, 0.08), caddy)
    packet_colors = [
        (0.96, 0.92, 0.84, 1.0),  # white sugar
        (0.82, 0.58, 0.34, 1.0),  # brown sugar
        (0.42, 0.62, 0.92, 1.0),  # equal blue
    ]
    for di in range(3):
        dx_off = -0.12 + di * 0.12
        make_box(f"{prefix}_Divider_{di}",
                 (cx + dx_off, cy, bz + 0.06),
                 (0.005, 0.26, 0.12), caddy)
        for stack in range(4):
            make_box(f"{prefix}_Sugar_{di}_{stack}",
                     (cx + dx_off + 0.06, cy - 0.10 + stack * 0.06,
                      bz + 0.06),
                     (0.06, 0.05, 0.005), packet_colors[di])
    # Stirrer cup + stirrers
    make_cyl(f"{prefix}_StirrerCup", (cx + 0.16, cy + 0.08, bz + 0.10),
             0.04, 0.16, P.METAL_STEEL)
    for st in range(6):
        ang = st * 1.05
        sx = cx + 0.16 + math.cos(ang) * 0.018
        sy = cy + 0.08 + math.sin(ang) * 0.018
        make_box(f"{prefix}_Stirrer_{st}", (sx, sy, bz + 0.20),
                 (0.003, 0.003, 0.18), P.PAPER)
    for cs in range(4):
        make_cyl(f"{prefix}_CreamerCup_{cs}",
                 (cx - 0.16, cy + 0.04, bz + 0.04 + cs * 0.06),
                 0.025, 0.06, P.PAPER)


def make_paper_cup_stack(prefix, anchor, *, palette=None, count=20):
    """Tall stack of paper hot cups. anchor=(center_x, center_y, base_z)."""
    palette = palette or {}
    col = palette.get("col", P.PAPER)
    cx, cy, bz = anchor
    for ci in range(count):
        make_cyl(f"{prefix}_{ci}", (cx, cy, bz + ci * 0.012),
                 0.045, 0.014, col)
