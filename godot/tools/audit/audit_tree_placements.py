"""
audit_tree_placements.py
══════════════════════════════════════════════════════════════════
Check every wild-zone tree against ROAD_CORRIDORS to catch any
placement that lands inside a road quad or its 2m safety buffer.

Tree positions are emitted by build_wild_zone_trees as a static
list (no per-cell procedural generation), so we can parse them
from the source. This complements audit_overlaps.py which only
checks BUILDING-sized boxes.

Run:
    cd godot/tools/audit && python3 audit_tree_placements.py

Outputs: list of (x, y, kind, road, distance) for any tree within
hw + 2m of a road centerline. Zero overlaps = clean placement.
"""
import sys
import os
import math
import re


class _Anything:
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


def main():
    src = open(_BUILD).read()
    m = re.search(
        r"def build_wild_zone_trees.*?tree_specs = \[(.*?)\]\s*for k",
        src, re.S)
    if not m:
        print("Couldn't locate tree_specs block.")
        return
    block = m.group(1)
    tree_pts = re.findall(
        r"\(\s*(-?\d+)\s*,\s*(-?\d+)\s*,\s*'(oak|pine)'\s*\)", block)
    print(f"Parsed {len(tree_pts)} tree positions")

    problems = []
    BUFFER = 2.0
    for tx, ty, kind in tree_pts:
        tx = int(tx); ty = int(ty)
        for road_name, waypoints, hw, _sh in mod.ROAD_CORRIDORS:
            for i in range(len(waypoints) - 1):
                x0, y0, _ = waypoints[i]
                x1, y1, _ = waypoints[i + 1]
                seg_len = math.hypot(x1 - x0, y1 - y0)
                n_samples = max(int(seg_len / 3), 2)
                hit = False
                for s in range(n_samples + 1):
                    t = s / n_samples
                    px = x0 + (x1 - x0) * t
                    py = y0 + (y1 - y0) * t
                    d = math.hypot(px - tx, py - ty)
                    if d < hw + BUFFER:
                        problems.append((tx, ty, kind, road_name, d, hw))
                        hit = True
                        break
                if hit:
                    break

    seen = set()
    print(f"\nTREE × ROAD overlaps (within hw + {BUFFER}m of road CL):")
    for tx, ty, kind, rn, d, hw in problems:
        key = (tx, ty, rn)
        if key in seen:
            continue
        seen.add(key)
        print(f"  ({tx:+5}, {ty:+5}) {kind:5s} × {rn:15s}  "
              f"d={d:.1f}m  hw={hw}m")
    if not seen:
        print("  (none — placement clean)")
    print(f"\nTotal {len(seen)} unique tree/road overlaps")


if __name__ == "__main__":
    main()
