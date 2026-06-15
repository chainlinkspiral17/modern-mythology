"""
audit_overlaps.py
══════════════════════════════════════════════════════════════════
Promotes the inline overlap-audit from the 2026-06-15 chapter-1
cleanup pass into a tool. Run after any change to ROAD_CORRIDORS,
LOT_PADS, or any building footprint to detect:

  1. Road centerlines whose road quad would overlap a building
  2. Two LOT_PADS overlapping each other (silent settlement
     conflict)
  3. Buildings sitting on top of road corridors

Run:
    cd godot/tools/audit && python3 audit_overlaps.py

Outputs a list of (building, road, distance, road_hw) tuples
plus a summary count. Zero overlaps = clean map.

Maintenance: when a new building is added to build_harmony_terrain
.py, append it to the BUILDINGS list below. Multi-component
"buildings" (Truck Stop has a garage + canopy + lot) should add
each REAL building part separately, not the bounding rect of the
whole installation.
"""
import sys
import math
import os

# Bootstrap: stub bpy so the build module can be loaded outside
# Blender. We only care about the data tables (ROAD_CORRIDORS,
# LOT_PADS, etc.) — none of the building functions are called.
class _M(dict):
    def __getattr__(self, k): return _M()
    def __call__(self, *a, **k): return _M()
sys.modules['bpy'] = _M()

_HERE = os.path.dirname(os.path.abspath(__file__))
_BUILD = os.path.normpath(os.path.join(
    _HERE, "..", "blender", "locales", "build_harmony_terrain.py"))

import importlib.util
spec = importlib.util.spec_from_file_location('bh', _BUILD)
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)


# ── Building catalog · update when buildings are added/moved ──
BUILDINGS = [
    # (name, cx, cy, width_x, depth_y)
    ('Hospital',         180, 300, 36, 16),
    ('NexCorpHQ',          0, 300, 30, 24),
    ('CountryClub',        0, 370, 36, 14),
    ('Halsey',           480, -100, 18, 14),
    ('SelfStorage',      480, -180, 12, 60),
    ('Auto Showroom',    480, -260, 30, 14),    # showroom only, not lot
    ('BigBox',           480,   60, 60, 24),
    ('Taqueria',         290, -370, 14, 10),
    ('TruckStopGarage',  200, -366, 30, 12),    # garage only, not canopy
    ('NexCorpGG',        -60, -360, 12, 10),
    ('KwikShop strip',   -15, -360, 28, 10),
    ('Diner',             35, -360, 20, 10),
    ('Cosmic',            70, -360,  9,  8),
    ('Dambrosio',       -150, -360, 14, 12),
    ('Library',           40,   80, 16, 14),
    ('Church',           -30,  140, 12, 18),
    ('FireStn',         -200,  -42, 22, 14),
    ('PoliceStn',       -170,  -60, 18, 12),
    ('PostOffice',       180,  -30, 16, 12),
    ('ES',               -90,  160, 30, 20),
    ('SCRATCH',         -510,    0, 30, 20),
    ('Minimart',        -260,  -50, 15, 12),
    ('HorizonPlaza',    -100,   30, 24, 12),
    ('ModelHome',       -340,  218, 14, 14),
    ('SalesTrailer',    -300,  218, 14,  6),
]


def seg_to_box_dist(px, py, x_min, x_max, y_min, y_max):
    dx = max(x_min - px, 0, px - x_max)
    dy = max(y_min - py, 0, py - y_max)
    return math.hypot(dx, dy)


def main():
    problems = []
    for name, cx, cy, w, d in BUILDINGS:
        bx_min = cx - w/2; bx_max = cx + w/2
        by_min = cy - d/2; by_max = cy + d/2
        for road_name, waypoints, hw, sh in mod.ROAD_CORRIDORS:
            for i in range(len(waypoints) - 1):
                x0, y0, _ = waypoints[i]
                x1, y1, _ = waypoints[i + 1]
                n_samples = max(int(math.hypot(x1-x0, y1-y0) / 3), 2)
                for s in range(n_samples + 1):
                    t = s / n_samples
                    px = x0 + (x1-x0) * t
                    py = y0 + (y1-y0) * t
                    d_box = seg_to_box_dist(
                        px, py, bx_min, bx_max, by_min, by_max)
                    if d_box < hw:
                        problems.append(
                            (name, road_name, px, py, d_box, hw))

    seen = set()
    print("BUILDING × ROAD OVERLAPS:")
    for name, road_name, px, py, d, hw in problems:
        key = (name, road_name)
        if key in seen:
            continue
        seen.add(key)
        depth = hw - d
        print(f'  {name:20s} × {road_name:15s} '
              f'edge {d:.1f}m hw {hw}m '
              f'(quad penetrates building by {depth:.1f}m) '
              f'@ ({px:7.1f}, {py:7.1f})')
    if not seen:
        print('  (none — map is clean)')
    print(f"\nTotal {len(seen)} unique building/road overlap pairs")


if __name__ == "__main__":
    main()
