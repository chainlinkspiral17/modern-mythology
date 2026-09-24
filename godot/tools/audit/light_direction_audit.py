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
has Y > +0.05 fails. Fills may come from low on purpose (the
playbook's FILL is "opposite side, low angle" — a warm ground bounce)
and are not judged.

2026-09-24 (twenty-third pass): the first version only asked "is it
UP?". 22 keys sat at the identity matrix — Godot's default pose, which
shines SIDEWAYS along −Z — and passed, and 39 back/rim lights shared
one copied matrix aimed 45° UP (the playbook's BACK is "behind subject,
down 25°"). Now:
  · a key must travel DOWN: direction Y < −0.10 (golden hour is −0.14);
  · a back / rim must not travel up: Y ≤ +0.05.
The portrait rig's BackRim (scenes/vn/Portrait3D.tscn) is tuned by eye
across every character portrait and is listed as a known exception.

    python3 godot/tools/audit/light_direction_audit.py
Nonzero exit on any key that is not aimed down or back aimed up.
"""
import glob, math, os, re, sys

HERE = os.path.dirname(os.path.abspath(__file__))
SCENES = os.path.normpath(os.path.join(HERE, "..", "..", "scenes"))
KEYLIKE = re.compile(r"key|sun|moon|overcast|overhead", re.I)
BACKLIKE = re.compile(r"back|rim", re.I)
KNOWN = {("vn/Portrait3D.tscn", "BackRim"): "the portrait rig — a look call across every character; Deck first"}
NODE = re.compile(r'\[node name="([^"]+)" type="DirectionalLight3D"[^\]]*\]\n((?:[^\[\n][^\n]*\n?)*)')


def main():
    bad = []
    total = 0
    for f in sorted(glob.glob(os.path.join(SCENES, "**", "*.tscn"), recursive=True)):
        for m in NODE.finditer(open(f).read()):
            name, body = m.group(1), m.group(2)
            role = "key" if KEYLIKE.search(name) else "back" if BACKLIKE.search(name) else None
            if role is None:
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
            rel = os.path.relpath(f, SCENES)
            if (rel, name) in KNOWN:
                continue
            if role == "key" and dy > 0.05:
                bad.append(("UPWARD", rel, name, dy))
            elif role == "key" and dy > -0.10:
                bad.append(("LEVEL", rel, name, dy))
            elif role == "back" and dy > 0.05:
                bad.append(("UPWARD", rel, name, dy))
    for why, f, name, dy in bad:
        print("%-7s %-44s %-26s dir.y %+.2f" % (why, f, name, dy))
    print("light_direction_audit · %d key/back light(s) · %d mis-aimed (%d known exception)" % (
        total, len(bad), len(KNOWN)))
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
