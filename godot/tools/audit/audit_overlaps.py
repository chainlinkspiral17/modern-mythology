"""
audit_overlaps.py
══════════════════════════════════════════════════════════════════
Full-sweep overlap audit. Runs the entire build under a stubbed
bpy, intercepts every _make_box_local emit, filters to building-
sized boxes (≥4m × ≥4m × ≥2m, excluding slabs / roofs / lots /
sidewalks / paths / etc.), and checks each against every road
corridor.

Previously this tool used a hand-curated BUILDINGS list, which
silently missed buildings I forgot to add to the list. The new
approach catches everything that gets emitted, so adding a new
building / NPC structure / asset doesn't require touching this
file.

Run:
    cd godot/tools/audit && python3 audit_overlaps.py

Outputs a list of (building, road, distance, road_hw) tuples
plus a summary count. Zero overlaps = clean map.
"""
import sys
import math
import os


class _Anything:
    """Stub for every bpy attribute / subscript / call."""
    def __getattr__(self, k): return _Anything()
    def __setattr__(self, k, v): pass
    def __getitem__(self, k): return _Anything()
    def __setitem__(self, k, v): pass
    def __call__(self, *a, **k): return _Anything()
    def __iter__(self): return iter([])
    def __contains__(self, k): return True
    def __bool__(self): return True
    def __float__(self): return 0.0
    def __int__(self): return 0
    def __len__(self): return 0


class _Bpy:
    def __getattr__(self, k): return _Anything()


sys.modules['bpy'] = _Bpy()

_HERE = os.path.dirname(os.path.abspath(__file__))
_BUILD = os.path.normpath(os.path.join(
    _HERE, "..", "blender", "locales", "build_harmony_terrain.py"))

import importlib.util
spec = importlib.util.spec_from_file_location('bh', _BUILD)
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)

# ── Intercept every box emit during the build ──────────────────
_boxes = []
_orig_box = mod._make_box_local


def _captured_box(name, center, size, color):
    _boxes.append((name, center, size))
    return _orig_box(name, center, size, color)


mod._make_box_local = _captured_box


def seg_to_box_dist(px, py, x_min, x_max, y_min, y_max):
    dx = max(x_min - px, 0, px - x_max)
    dy = max(y_min - py, 0, py - y_max)
    return math.hypot(dx, dy)


# Substring filters that mark a box as NOT a building (cosmetic,
# ground-plane, signage, etc.). If a box name contains any of
# these, it's skipped from the audit.
NON_BUILDING_KEYWORDS = (
    'Slab', 'Foundation', 'Roof', 'Sidewalk', 'Driveway', 'Lot',
    'Pad', 'Walk', 'Carpet', 'Path', 'Court', 'Field', 'Bench',
    'Sign', 'Mat', 'Crossbar', 'Stripe', 'Curb', 'EdgeLine',
    'DoubleYellow', 'Bar', 'Grass', 'Mulch', 'Berm', 'Trim',
    'Cap', 'Plinth', 'Awning', 'Canopy', 'Sandbox', 'Plate',
    'Banner', 'Plank', 'Pier', 'Deck', 'Quay',
)


def main():
    try:
        mod.main()
    except RuntimeError:
        pass  # expected — stub can't write the GLB

    buildings = []
    for name, (cx, cy, cz), (sx, sy, sz) in _boxes:
        if sx < 4.0 or sy < 4.0 or sz < 2.0:
            continue
        if any(k in name for k in NON_BUILDING_KEYWORDS):
            continue
        buildings.append((name, cx, cy, sx, sy))
    print(f"Captured {len(_boxes)} total boxes; "
          f"{len(buildings)} building-sized.\n")

    problems = []
    for name, cx, cy, w, d in buildings:
        bx_min = cx - w / 2
        bx_max = cx + w / 2
        by_min = cy - d / 2
        by_max = cy + d / 2
        for road_name, waypoints, hw, sh in mod.ROAD_CORRIDORS:
            for i in range(len(waypoints) - 1):
                x0, y0, _ = waypoints[i]
                x1, y1, _ = waypoints[i + 1]
                seg_len = math.hypot(x1 - x0, y1 - y0)
                n_samples = max(int(seg_len / 3), 2)
                for s in range(n_samples + 1):
                    t = s / n_samples
                    px = x0 + (x1 - x0) * t
                    py = y0 + (y1 - y0) * t
                    d_box = seg_to_box_dist(
                        px, py, bx_min, bx_max, by_min, by_max)
                    if d_box < hw:
                        problems.append(
                            (name, road_name, px, py, d_box, hw))

    seen = set()
    print("BUILDING × ROAD OVERLAPS:")
    for name, road_name, px, py, dist, hw in problems:
        key = (name, road_name)
        if key in seen:
            continue
        seen.add(key)
        depth = hw - dist
        print(f"  {name[:35]:35s} × {road_name:15s} "
              f"edge {dist:.1f}m hw {hw}m "
              f"(road quad penetrates by {depth:.1f}m) "
              f"@ ({px:7.1f}, {py:7.1f})")
    if not seen:
        print("  (none — map is clean)")
    print(f"\nTotal {len(seen)} unique building/road overlap pairs")


if __name__ == "__main__":
    main()
