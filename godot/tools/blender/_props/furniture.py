"""Furniture with silhouettes — DETAIL DRAFT 2 kit (2026-09-05).

Every chair in the project was a seat box on four stick cylinders;
every table a slab on posts. These read as furniture at a glance:
turned legs (lathed), aprons and stretchers, a chair back with
spindles, a chamfered seat, a lamp with a shade, a stool with a
footring. All parts share the prefix so the overlap gate treats
each piece as one assembly.

    make_chair(prefix, x, y, yaw=0.0, wood=..., seat_col=None)
    make_table(prefix, x, y, w=1.2, d=0.8, h=0.75, wood=...)
    make_stool(prefix, x, y, h=0.70, wood=...)
    make_lamp(prefix, x, y, base_z=0.0, h=0.55, shade_col=...)
    make_bench(prefix, x, y, length=1.6, yaw=0.0, wood=...)
"""
import math
from .geometry import make_box, make_cyl, make_chamfer_box, make_lathe, make_rot_box, make_tube

WOOD = (0.50, 0.40, 0.28, 1.0)
WOOD_DK = (0.40, 0.31, 0.22, 1.0)
BRASS = (0.72, 0.60, 0.32, 1.0)


def _leg(name, x, y, z0, h, r=0.025, wood=WOOD):
    """A turned leg: foot, a swell, a neck, the block under the seat."""
    make_lathe(name, (x, y, z0), [(r * 0.8, 0.0), (r * 1.15, 0.05), (r * 0.7, 0.10), (r, 0.30 * h), (r * 1.25, 0.42 * h),
                                  (r * 0.85, 0.58 * h), (r * 0.85, 0.90 * h), (r * 1.1, 0.94 * h), (r * 1.1, h)], wood, segments=8)


def make_chair(prefix, x, y, yaw=0.0, wood=WOOD, seat_col=None, seat_h=0.45, w=0.42, z0=0.0):
    seat_col = seat_col or wood
    c, s = math.cos(yaw), math.sin(yaw)
    def P(u, v, z):
        return (x + u * c - v * s, y + u * s + v * c, z0 + z)
    hw = w / 2.0
    for li, (u, v) in enumerate(((-hw + 0.03, -hw + 0.03), (hw - 0.03, -hw + 0.03), (-hw + 0.03, hw - 0.03), (hw - 0.03, hw - 0.03))):
        _leg(f"{prefix}_Leg_{li}", *P(u, v, 0.0)[:2], z0, seat_h - 0.04, wood=wood)
    # stretchers between the legs
    for si, (a, b) in enumerate((((-hw + 0.03, -hw + 0.03), (hw - 0.03, -hw + 0.03)), ((-hw + 0.03, hw - 0.03), (hw - 0.03, hw - 0.03)),
                                 ((-hw + 0.03, -hw + 0.03), (-hw + 0.03, hw - 0.03)), ((hw - 0.03, -hw + 0.03), (hw - 0.03, hw - 0.03)))):
        make_tube(f"{prefix}_Stretcher_{si}", [P(a[0], a[1], 0.18), P(b[0], b[1], 0.18)], 0.012, wood, segments=5)
    make_chamfer_box(f"{prefix}_Seat", P(0.0, 0.0, seat_h - 0.02), (w, w, 0.04), seat_col, chamfer=0.012, yaw=yaw)
    # the back: two posts, a top rail, spindles
    for sgn in (-1, 1):
        make_rot_box(f"{prefix}_Back_Post_{sgn:+d}", P(sgn * (hw - 0.03), -hw + 0.03, seat_h + 0.22), (0.035, 0.035, 0.48), wood, yaw=yaw, roll=-0.10)
    make_rot_box(f"{prefix}_Back_Rail", P(0.0, -hw + 0.03 - 0.05, seat_h + 0.44), (w, 0.03, 0.07), wood, yaw=yaw, roll=-0.10)
    for si, u in enumerate((-0.12, -0.04, 0.04, 0.12)):
        make_rot_box(f"{prefix}_Spindle_{si}", P(u, -hw + 0.03 - 0.03, seat_h + 0.21), (0.016, 0.016, 0.38), wood, yaw=yaw, roll=-0.10)


def make_table(prefix, x, y, w=1.2, d=0.8, h=0.75, wood=WOOD, top_col=None, z0=0.0):
    top_col = top_col or wood
    x, y, h0 = x, y, h
    h = z0 + h
    make_chamfer_box(f"{prefix}_Top", (x, y, h - 0.02), (w, d, 0.04), top_col, chamfer=0.01)
    make_box(f"{prefix}_Apron_F", (x, y - d / 2.0 + 0.06, h - 0.09), (w - 0.16, 0.025, 0.10), WOOD_DK)
    make_box(f"{prefix}_Apron_B", (x, y + d / 2.0 - 0.06, h - 0.09), (w - 0.16, 0.025, 0.10), WOOD_DK)
    make_box(f"{prefix}_Apron_L", (x - w / 2.0 + 0.06, y, h - 0.09), (0.025, d - 0.16, 0.10), WOOD_DK)
    make_box(f"{prefix}_Apron_R", (x + w / 2.0 - 0.06, y, h - 0.09), (0.025, d - 0.16, 0.10), WOOD_DK)
    for li, (u, v) in enumerate(((-w / 2.0 + 0.06, -d / 2.0 + 0.06), (w / 2.0 - 0.06, -d / 2.0 + 0.06), (-w / 2.0 + 0.06, d / 2.0 - 0.06), (w / 2.0 - 0.06, d / 2.0 - 0.06))):
        _leg(f"{prefix}_Leg_{li}", x + u, y + v, z0, h0 - 0.14, r=0.032, wood=wood)
    make_tube(f"{prefix}_Stretcher", [(x - w / 2.0 + 0.06, y, z0 + 0.16), (x + w / 2.0 - 0.06, y, z0 + 0.16)], 0.014, wood, segments=5)


def make_stool(prefix, x, y, h=0.70, wood=WOOD):
    make_lathe(f"{prefix}_Seat", (x, y, h - 0.04), [(0.0, 0.0), (0.17, 0.0), (0.18, 0.02), (0.16, 0.04), (0.0, 0.045)], wood, segments=12)
    for li in range(3):
        a = li * 2.0 * math.pi / 3.0 + 0.5
        _leg(f"{prefix}_Leg_{li}", x + 0.13 * math.cos(a), y + 0.13 * math.sin(a), 0.0, h - 0.045, r=0.02, wood=wood)
    make_lathe(f"{prefix}_Footring", (x, y, 0.22), [(0.15, 0.0), (0.16, 0.01), (0.15, 0.02)], WOOD_DK, segments=12, loop=True)


def make_lamp(prefix, x, y, base_z=0.0, h=0.55, shade_col=(0.92, 0.86, 0.68, 1.0), body_col=BRASS):
    make_lathe(f"{prefix}_Base", (x, y, base_z), [(0.0, 0.0), (0.09, 0.0), (0.08, 0.02), (0.05, 0.03), (0.03, 0.05), (0.014, 0.06), (0.014, h * 0.55),
                                                  (0.025, h * 0.58), (0.014, h * 0.61), (0.014, h * 0.72), (0.0, h * 0.72)], body_col, segments=10)
    make_lathe(f"{prefix}_Shade", (x, y, base_z + h * 0.62), [(0.11, 0.0), (0.16, h * 0.30), (0.0, h * 0.30)], shade_col, segments=12)
    make_lathe(f"{prefix}_Bulb", (x, y, base_z + h * 0.72), [(0.0, 0.0), (0.025, 0.01), (0.03, 0.04), (0.0, 0.07)], (0.98, 0.94, 0.80, 1.0), segments=8)


def make_bench(prefix, x, y, length=1.6, yaw=0.0, wood=WOOD, h=0.45):
    c, s = math.cos(yaw), math.sin(yaw)
    def P(u, v, z):
        return (x + u * c - v * s, y + u * s + v * c, z)
    make_chamfer_box(f"{prefix}_Seat", P(0.0, 0.0, h - 0.025), (length, 0.36, 0.05), wood, chamfer=0.012, yaw=yaw)
    for sgn in (-1, 1):
        make_rot_box(f"{prefix}_Leg_{sgn:+d}", P(sgn * (length / 2.0 - 0.18), 0.0, (h - 0.05) / 2.0), (0.06, 0.30, h - 0.05), WOOD_DK, yaw=yaw)
    make_rot_box(f"{prefix}_Stretcher", P(0.0, 0.0, 0.14), (length - 0.42, 0.05, 0.06), WOOD_DK, yaw=yaw)
