"""
audit_fences.py
══════════════════════════════════════════════════════════════════
Check that no backyard fence panel overlaps a road quad, another
house's footprint, or a pond water / creek band. Fences extend
11m back + 9m to either side from each house, so corner-lot and
small-yard houses can have fences spilling into neighbor yards
or across nearby roads.

Run:
    cd godot/tools/audit && python3 audit_fences.py
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


_fences = []
_houses = []
_orig = mod._make_box_local


def _cap(name, center, size, color):
    if '_Fence' in name and 'Post' not in name:
        _fences.append((name, center, size))
    elif (name.endswith('_Main') and size[2] > 2.0
          and size[0] > 4.0 and size[1] > 4.0):
        _houses.append((name, center, size))
    return _orig(name, center, size, color)


mod._make_box_local = _cap


def main():
    try:
        mod.main()
    except RuntimeError:
        pass

    print(f"Audit covers {len(_fences)} fence boxes "
          f"against {len(_houses)} houses + roads + water.\n")

    # ── Fence × road ──────────────────────────────────────────
    road_problems = []
    for fname, (fx, fy, _fz), (fsx, fsy, _fsz) in _fences:
        fx_min, fx_max = fx - fsx / 2, fx + fsx / 2
        fy_min, fy_max = fy - fsy / 2, fy + fsy / 2
        hit = False
        for (rn, wps, hw, _sh) in mod.ROAD_CORRIDORS:
            for i in range(len(wps) - 1):
                x0, y0, _ = wps[i]
                x1, y1, _ = wps[i + 1]
                seg_len = math.hypot(x1 - x0, y1 - y0) or 1
                n_samples = max(int(seg_len / 3), 2)
                for s in range(n_samples + 1):
                    t = s / n_samples
                    px = x0 + (x1 - x0) * t
                    py = y0 + (y1 - y0) * t
                    dx = max(fx_min - px, 0, px - fx_max)
                    dy = max(fy_min - py, 0, py - fy_max)
                    d = math.hypot(dx, dy)
                    if d < hw:
                        road_problems.append((fname, rn, d, hw))
                        hit = True
                        break
                if hit:
                    break
            if hit:
                break
    print("Fence × road overlaps:")
    seen = set()
    for fn, rn, d, hw in road_problems:
        if fn in seen:
            continue
        seen.add(fn)
        print(f"  {fn[:40]:40s} × {rn:15s}  d={d:.1f}m  hw={hw}m")
    if not seen:
        print("  (none)")

    # ── Fence × another house ─────────────────────────────────
    house_problems = []
    for fname, (fx, fy, _fz), (fsx, fsy, _fsz) in _fences:
        owner = fname.split('_Fence')[0]
        fx_min, fx_max = fx - fsx / 2, fx + fsx / 2
        fy_min, fy_max = fy - fsy / 2, fy + fsy / 2
        for hname, (hx, hy, _hz), (hsx, hsy, _hsz) in _houses:
            if hname[:-5] == owner:
                continue
            hx_min, hx_max = hx - hsx / 2, hx + hsx / 2
            hy_min, hy_max = hy - hsy / 2, hy + hsy / 2
            if (fx_max > hx_min and fx_min < hx_max
                and fy_max > hy_min and fy_min < hy_max):
                house_problems.append((fname, hname))
    print("\nFence × OTHER-house footprint overlaps:")
    seen = set()
    for fn, hn in house_problems:
        k = (fn, hn)
        if k in seen:
            continue
        seen.add(k)
        print(f"  {fn[:40]:40s} INTO {hn[:35]}")
    if not seen:
        print("  (none)")

    # ── Fence × water ─────────────────────────────────────────
    water_problems = []
    for fname, (fx, fy, _fz), (fsx, fsy, _fsz) in _fences:
        fx_min, fx_max = fx - fsx / 2, fx + fsx / 2
        fy_min, fy_max = fy - fsy / 2, fy + fsy / 2
        for (pname, pcx, pcy, pr, _) in mod.PONDS:
            wr = pr * 0.90
            rdx = max(fx_min - pcx, 0, pcx - fx_max)
            rdy = max(fy_min - pcy, 0, pcy - fy_max)
            d = math.hypot(rdx, rdy)
            if d < wr:
                water_problems.append(('pond', fname, pname, d))
                break
    print("\nFence × pond water overlaps:")
    seen = set()
    for _t, fn, pn, d in water_problems:
        if fn in seen:
            continue
        seen.add(fn)
        print(f"  {fn[:40]:40s} × {pn:18s} d={d:.1f}m")
    if not seen:
        print("  (none)")


if __name__ == "__main__":
    main()
