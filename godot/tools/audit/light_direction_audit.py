#!/usr/bin/env python3
"""light_direction_audit — a key light must shine DOWN.

2026-09-24: 32 DirectionalLight3D key / sun / moon / overcast / overhead
lights across the locale scenes pointed UP (one copied Rx(+45) matrix,
a sign slip): they lit ceilings and undersides and never a floor, a
table or the ground. The grunion beach's Moon_Key pointed at the sky
and the whole beach rendered black under the night mood; the kwik
stop's Key_FluorescentOverhead shone straight at the ceiling.

A directional light shines along its local -Z. The .tscn Transform3D
lists the basis ROW by row, so -Z = -(m02, m12, m22); its Y component
is -m12. Any light named key|sun|moon|overcast|overhead whose direction
has Y > +0.05 fails. Fills and rims may come from low on purpose
(the portrait rig's "fill from camera-right low") and are not judged.

    python3 godot/tools/audit/light_direction_audit.py
Nonzero exit on any upward key light.
"""
import glob, math, os, re, sys

HERE = os.path.dirname(os.path.abspath(__file__))
SCENES = os.path.normpath(os.path.join(HERE, "..", "..", "scenes"))
KEYLIKE = re.compile(r"key|sun|moon|overcast|overhead", re.I)
NODE = re.compile(r'\[node name="([^"]+)" type="DirectionalLight3D"[^\]]*\]\n((?:[^\[\n][^\n]*\n?)*)')


def main():
    bad = []
    total = 0
    for f in sorted(glob.glob(os.path.join(SCENES, "**", "*.tscn"), recursive=True)):
        for m in NODE.finditer(open(f).read()):
            name, body = m.group(1), m.group(2)
            if not KEYLIKE.search(name):
                continue
            total += 1
            t = re.search(r"transform = Transform3D\(([^)]*)\)", body)
            r = re.search(r"rotation = Vector3\(([^)]*)\)", body)
            if t:
                v = [float(x) for x in t.group(1).split(",")]
                dy = -v[5]
            elif r:
                rx = float(r.group(1).split(",")[0])
                dy = math.sin(rx)
            else:
                dy = 0.0
            if dy > 0.05:
                bad.append((os.path.relpath(f, SCENES), name, dy))
    for f, name, dy in bad:
        print("UPWARD  %-44s %-26s dir.y %+.2f" % (f, name, dy))
    print("light_direction_audit · %d key light(s) · %d pointing up" % (total, len(bad)))
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
