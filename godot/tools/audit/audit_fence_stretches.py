"""
audit_fence_stretches.py
══════════════════════════════════════════════════════════════════
Detect "broken column" fence patterns — multiple fence panels
aligned on the same X (or Y) line within ±1 m, with adjacent
panels far enough apart that the line reads as fragmented
neighbor fencing rather than one intended property-line.

A clean result here means each lot's fence looks like its own,
not part of an accidental 100-metre row of mismatched fragments.

Threshold: streak of ≥ 3 panels in the same bin AND max
edge-gap < 30 m. Pure isolated panels (max gap > 30 m) are NOT
flagged — those read as discrete fences even if they happen to
share an axis.

Run:
    cd godot/tools/audit && python3 audit_fence_stretches.py
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
_orig = mod._make_box_local


def _cap(name, center, size, color):
    if '_Fence' in name and 'Post' not in name:
        _fences.append((name, center, size))
    return _orig(name, center, size, color)


mod._make_box_local = _cap


def main():
    try:
        mod.main()
    except RuntimeError:
        pass

    # Classify each fence panel as "X-aligned" (long axis X, thin
    # axis Y — back fence on a +/-Y-facing house) or "Y-aligned"
    # (long axis Y — side fence on a +/-Y-facing house).
    x_aligned = []   # back fences, runs E-W, classified by Y
    y_aligned = []   # side fences, runs N-S, classified by X
    for name, (cx, cy, cz), (sx, sy, sz) in _fences:
        if sx > sy * 2:
            x_aligned.append((name, cx, cy, sx))
        elif sy > sx * 2:
            y_aligned.append((name, cx, cy, sy))

    print(f"Fence panels: {len(x_aligned)} X-aligned (run E-W) + "
          f"{len(y_aligned)} Y-aligned (run N-S)")

    # Bin by their CL axis (Y for x-aligned, X for y-aligned), to
    # the nearest meter.
    def find_streaks(panels, axis_idx, span_idx, axis_name):
        bins = {}
        for (name, cx, cy, length) in panels:
            axis_val = round((cy if axis_idx == 1 else cx) / 1.0) * 1
            bins.setdefault(axis_val, []).append(
                (name, cx, cy, length))
        long_streaks = []
        for axis_val, plist in bins.items():
            if len(plist) < 3:
                continue
            if span_idx == 0:
                plist.sort(key=lambda p: p[1])
            else:
                plist.sort(key=lambda p: p[2])
            span_vals = [p[1] if span_idx == 0 else p[2]
                          for p in plist]
            total_span = max(span_vals) - min(span_vals)
            gaps = []
            for i in range(len(plist) - 1):
                p1 = plist[i]
                p2 = plist[i + 1]
                c1 = p1[1] if span_idx == 0 else p1[2]
                c2 = p2[1] if span_idx == 0 else p2[2]
                edge_gap = (c2 - c1) - (p1[3] / 2 + p2[3] / 2)
                gaps.append(edge_gap)
            max_gap = max(gaps) if gaps else 0
            # Only flag "broken column" patterns. Panels with
            # max edge-gap > 30m read as isolated fences and are
            # not a visual problem even when they share an axis.
            if max_gap >= 30:
                continue
            long_streaks.append(
                (axis_name, axis_val, plist, total_span, max_gap))
        return long_streaks

    x_streaks = find_streaks(x_aligned, 1, 0, 'Y')
    y_streaks = find_streaks(y_aligned, 0, 1, 'X')

    print("\n── X-aligned BACK fence streaks (E-W rows) ──")
    for (axis, val, plist, span, gap) in sorted(
            x_streaks, key=lambda s: -s[3]):
        print(f"  Y={val:+5}: {len(plist)} panels, span={span:.0f}m, "
              f"max edge-gap={gap:+5.0f}m")
        for (n, cx, cy, length) in plist:
            print(f"      {n[:38]:38s}  cx={cx:+6.1f}  len={length:.1f}m")

    print("\n── Y-aligned SIDE fence streaks (N-S columns) ──")
    for (axis, val, plist, span, gap) in sorted(
            y_streaks, key=lambda s: -s[3]):
        print(f"  X={val:+5}: {len(plist)} panels, span={span:.0f}m, "
              f"max edge-gap={gap:+5.0f}m")
        for (n, cx, cy, length) in plist:
            print(f"      {n[:38]:38s}  cy={cy:+6.1f}  len={length:.1f}m")


if __name__ == "__main__":
    main()
