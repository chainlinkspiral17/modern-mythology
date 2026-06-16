"""
audit_road_grades.py
══════════════════════════════════════════════════════════════════
Check that every connector / residential road endpoint that
terminates at an ARTERIAL (HarmonyBlvd or HorizonDr) declares a
Z value matching the arterial's Z at that point. A mismatch >
1.5m creates a visible step where the connector meets the
arterial — the player sees a 2m bump in the road.

Run:
    cd godot/tools/audit && python3 audit_road_grades.py
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


ARTERIALS = ('HarmonyBlvd', 'HorizonDr')
DZ_THRESHOLD = 1.5
PROXIMITY = 30.0    # m — only check endpoints within this distance


def main():
    arterial_segs = []
    for (name, wps, hw, _sh) in mod.ROAD_CORRIDORS:
        if name not in ARTERIALS:
            continue
        for i in range(len(wps) - 1):
            arterial_segs.append((name, wps[i], wps[i + 1]))

    def arterial_z_at(x, y):
        best_d = float('inf')
        best_z = 0.0
        best_name = ''
        for (name, (x0, y0, z0), (x1, y1, z1)) in arterial_segs:
            dx = x1 - x0
            dy = y1 - y0
            seg_len2 = dx * dx + dy * dy
            if seg_len2 < 1e-3:
                continue
            t = ((x - x0) * dx + (y - y0) * dy) / seg_len2
            t = max(0.0, min(1.0, t))
            px = x0 + dx * t
            py = y0 + dy * t
            d = math.hypot(px - x, py - y)
            if d < best_d:
                best_d = d
                best_z = z0 + (z1 - z0) * t
                best_name = name
        return best_name, best_z, best_d

    problems = []
    for (name, wps, hw, _sh) in mod.ROAD_CORRIDORS:
        if name in ARTERIALS:
            continue
        for idx, (x, y, z) in [(0, wps[0]), (len(wps) - 1, wps[-1])]:
            art_name, art_z, art_d = arterial_z_at(x, y)
            if art_d < PROXIMITY:
                dz = z - art_z
                if abs(dz) > DZ_THRESHOLD:
                    problems.append((name, idx, x, y, z, art_name,
                                      art_z, art_d, dz))

    print("Connector endpoint Z vs nearest arterial Z "
          f"(mismatches > {DZ_THRESHOLD}m within {PROXIMITY}m):")
    for c_name, idx, x, y, z, a_name, a_z, a_d, dz in problems:
        end = 'start' if idx == 0 else 'end  '
        print(f"  {c_name:12s} {end} ({x:+5},{y:+5}) z={z:+5.1f}  "
              f"vs {a_name:11s} z={a_z:+5.1f}  "
              f"d={a_d:4.1f}m  Δz={dz:+5.2f}m")
    if not problems:
        print("  (none — grades match)")
    print(f"\nTotal {len(problems)} mismatches")


if __name__ == "__main__":
    main()
