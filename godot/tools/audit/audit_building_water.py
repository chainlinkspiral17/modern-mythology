"""
audit_building_water.py
══════════════════════════════════════════════════════════════════
Check that no building sits within a pond water disc OR within
the creek channel band. Complements audit_overlaps.py (which
catches building × road) with the WATER FEATURE side of the
"building in the wrong place" detection.

Run:
    cd godot/tools/audit && python3 audit_building_water.py
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

    buildings = [(n, c, s) for (n, c, s) in _boxes
                  if n.endswith('_Main')
                  and s[2] > 2.0 and s[0] > 4.0 and s[1] > 4.0]
    print(f"Audit covers {len(buildings)} building main walls")

    # ── Pond water disc check ─────────────────────────────────
    pond_problems = []
    for (pname, pcx, pcy, pr, _depth) in mod.PONDS:
        water_r = pr * 0.90
        for bname, (bx, by, bz), (sx, sy, sz) in buildings:
            rdx = max(bx - sx/2 - pcx, 0,
                      pcx - (bx + sx/2))
            rdy = max(by - sy/2 - pcy, 0,
                      pcy - (by + sy/2))
            d = math.hypot(rdx, rdy)
            if d < water_r:
                pond_problems.append((bname, pname, d, water_r))

    print("\nPond water × building overlaps:")
    seen = set()
    for bn, pn, d, wr in pond_problems:
        k = (bn, pn)
        if k in seen:
            continue
        seen.add(k)
        print(f"  {bn[:35]:35s} × {pn:18s} "
              f"d={d:.1f}m  water_r={wr:.1f}m")
    if not seen:
        print("  (none — no building inside any pond water disc)")

    # ── Creek channel check ───────────────────────────────────
    creek_problems = []
    creek_hw = mod.CREEK_CHANNEL_HW
    for bname, (bx, by, bz), (sx, sy, sz) in buildings:
        bx_min, bx_max = bx - sx / 2, bx + sx / 2
        by_min, by_max = by - sy / 2, by + sy / 2
        for i in range(len(mod.CREEK_CHANNEL) - 1):
            x0, y0, _ = mod.CREEK_CHANNEL[i]
            x1, y1, _ = mod.CREEK_CHANNEL[i + 1]
            seg_len = math.hypot(x1 - x0, y1 - y0) or 1
            n_samples = max(int(seg_len / 3), 2)
            hit = False
            for s in range(n_samples + 1):
                t = s / n_samples
                px = x0 + (x1 - x0) * t
                py = y0 + (y1 - y0) * t
                dx = max(bx_min - px, 0, px - bx_max)
                dy = max(by_min - py, 0, py - by_max)
                d = math.hypot(dx, dy)
                if d < creek_hw + 2:
                    creek_problems.append(
                        (bname, px, py, d))
                    hit = True
                    break
            if hit:
                break

    print("\nCreek channel × building overlaps:")
    seen = set()
    for bn, px, py, d in creek_problems:
        if bn in seen:
            continue
        seen.add(bn)
        print(f"  {bn[:35]:35s} d={d:.1f}m to creek "
              f"at ({px:+5.1f},{py:+5.1f})")
    if not seen:
        print("  (none — no building inside the creek channel + 2m)")


if __name__ == "__main__":
    main()
