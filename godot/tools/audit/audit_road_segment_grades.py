"""
audit_road_segment_grades.py
══════════════════════════════════════════════════════════════════
Check every road polyline segment for sane grade. Per civil-
engineering convention, residential street max grade is ~8%,
arterial max is ~6%, and a driveway max is ~12-15%. Anything
above 20% reads as a cliff at gameplay distance.

This tool only flags the CONTROL POLYLINE grade between two
declared waypoints. The road emit functions (_emit_arterial)
apply Catmull-Rom smoothing with samples_per_seg=4, so the
visible road surface has a gentler effective slope than what
this audit reports. Use the audit to spot truly excessive
declarations and as a sanity check after waypoint edits.

Run:
    cd godot/tools/audit && python3 audit_road_segment_grades.py
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


THRESHOLD_PCT = 15.0


def main():
    problems = []
    for (name, wps, hw, _sh) in mod.ROAD_CORRIDORS:
        for i in range(len(wps) - 1):
            x0, y0, z0 = wps[i]
            x1, y1, z1 = wps[i + 1]
            seg_len = math.hypot(x1 - x0, y1 - y0)
            if seg_len < 1:
                continue
            dz = z1 - z0
            grade_pct = (abs(dz) / seg_len) * 100
            if grade_pct > THRESHOLD_PCT:
                problems.append((name, i, seg_len, dz, grade_pct))

    print(f"Road segments with declared grade > {THRESHOLD_PCT}%:")
    for n, i, sl, dz, g in problems:
        print(f"  {n:12s} seg{i:>2}  len={sl:5.1f}m  "
              f"dz={dz:+5.1f}m  grade={g:.1f}%")
    if not problems:
        print("  (none — every segment is under threshold)")
    print(f"\nTotal {len(problems)} steep segments")


if __name__ == "__main__":
    main()
