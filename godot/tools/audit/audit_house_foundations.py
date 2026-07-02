"""
audit_house_foundations.py
══════════════════════════════════════════════════════════════════
Check the height of every house's foundation skirt. The skirt is
sized to bridge the maximum terrain-Z range across the slab
footprint — so a 5 m skirt means the lot has 5 m of vertical
variation across its 14 × 9 m footprint, which reads as a
"house on a cliff." Real suburban lots are graded flat enough
that visible foundations are < 1 m.

A foundation > 2 m almost always indicates the house lot
straddles a settlement boundary, lot pad shoulder, or pond/
creek carve shoulder.

Run:
    cd godot/tools/audit && python3 audit_house_foundations.py
"""
import sys
import os


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

    foundations = [(n, c, s) for (n, c, s) in _boxes
                    if n.endswith('_Foundation') and s[2] > 0.1]
    print(f"Found {len(foundations)} foundation skirts")

    THRESHOLD = 2.0
    tall = sorted(
        [(s[2], n) for (n, c, s) in foundations if s[2] > THRESHOLD],
        reverse=True)
    print(f"\nFoundations > {THRESHOLD} m (likely lot-on-cliff):")
    for h, n in tall:
        print(f"  {h:5.2f}m  {n}")
    if not tall:
        print(f"  (none — all foundations under {THRESHOLD} m)")
    print(f"\nTotal {len(tall)} tall foundations")


if __name__ == "__main__":
    main()
