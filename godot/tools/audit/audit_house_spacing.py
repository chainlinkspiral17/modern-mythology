"""
audit_house_spacing.py
══════════════════════════════════════════════════════════════════
Check pairwise distance between every suburban-house main-wall
box. Houses placed by different neighborhood builders sometimes
end up clustered too tightly when their lot regions overlap
(e.g., a residential street's k-th house position falls inside
a model-home lot, or a cul-de-sac's furthest house drifts into
the adjacent arterial's backyard zone).

Threshold: any pair whose bounding rects come within 3 m of
each other is flagged. Real US suburban lots have ≥ 5 m side
setbacks between neighboring houses.

Run:
    cd godot/tools/audit && python3 audit_house_spacing.py

Outputs: list of (house1, house2, edge_distance) pairs.
"""
import sys
import os
import math


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

_boxes = []
_orig = mod._make_box_local


def _cap(name, center, size, color):
    _boxes.append((name, center, size))
    return _orig(name, center, size, color)


mod._make_box_local = _cap


def main():
    try:
        mod.main()
    except RuntimeError:
        pass

    houses = [(n, c, s) for (n, c, s) in _boxes
              if n.endswith('_Main')
              and s[2] > 2.0 and s[0] > 4.0 and s[1] > 4.0]
    print(f"Found {len(houses)} suburban-house main-wall boxes")

    BUFFER = 3.0
    problems = []
    for i in range(len(houses)):
        n1, (x1, y1, _z1), (sx1, sy1, _sz1) = houses[i]
        for j in range(i + 1, len(houses)):
            n2, (x2, y2, _z2), (sx2, sy2, _sz2) = houses[j]
            dx = max(x1 - sx1 / 2 - (x2 + sx2 / 2),
                     x2 - sx2 / 2 - (x1 + sx1 / 2), 0)
            dy = max(y1 - sy1 / 2 - (y2 + sy2 / 2),
                     y2 - sy2 / 2 - (y1 + sy1 / 2), 0)
            d = math.hypot(dx, dy)
            if d < BUFFER:
                problems.append((n1, n2, d))

    print(f"\nHouse×house pairs within {BUFFER} m of each other:")
    for n1, n2, d in problems:
        print(f"  {n1[:38]:38s} ↔ {n2[:38]:38s} d={d:.2f}m")
    if not problems:
        print("  (none — spacing clean)")
    print(f"\nTotal {len(problems)} tight pairs")


if __name__ == "__main__":
    main()
