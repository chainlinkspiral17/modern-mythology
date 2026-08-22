#!/usr/bin/env python3
"""Re-aim vn_shot markers at their named subjects.

The companion tool to marker_aim_audit.py, and the second half of
the 2026-08-19 discipline: **author the camera POSITION; let the
tool compute the aim.** Hand-derived yaw shipped a whole wave of
markers facing 180° from their subjects.

For every shot_insert_<id> / shot_closeup_<id> marker whose subject
sits outside the audit's forward cone, this rewrites the marker's
`rotation` in the .tscn so the camera faces the CLUSTER of matching
geometry around the nearest matching part (the crow, not the beak).
Markers already passing the audit are untouched, so authoring flow
is: write the marker with `rotation = Vector3(0, 0, 0)`, run this,
run the audit.

Usage:
    python3 godot/tools/audit/marker_reaim.py            # all
    python3 godot/tools/audit/marker_reaim.py <locale>…  # some
"""
import math
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import marker_aim_audit as M


def cluster_centroid(hits, anchor):
    near = [p for _n, p in hits
            if sum((a - b) ** 2 for a, b in zip(p, anchor)) ** 0.5 < 1.6]
    if not near:
        near = [anchor]
    n = len(near)
    return tuple(sum(p[i] for p in near) / n for i in range(3))


def main():
    only = [a for a in sys.argv[1:] if not a.startswith("-")]
    fixed = 0
    for fn in sorted(os.listdir(M.LOCALES_TSCN)):
        if not fn.endswith(".tscn"):
            continue
        locale = fn[:-5]
        if only and locale not in only:
            continue
        path = os.path.join(M.LOCALES_TSCN, fn)
        markers = M.parse_markers(path)
        if not markers:
            continue
        geo = M.geometry_godot(locale)
        if not geo:
            continue
        src = open(path).read()
        changed = False
        for name, pos, rot in markers:
            m = re.match(r"shot_(insert|closeup)_(\w+)$", name)
            if not m:
                continue
            hits = M.matches_for(m.group(2), geo)
            if not hits:
                continue
            fwd = M.yxz_forward(*rot)
            nearest = min(hits, key=lambda h: sum(
                (a - b) ** 2 for a, b in zip(h[1], pos)))
            ang, dist = M.angle_to(pos, fwd, nearest[1])
            if ang <= M.CONE_DEG and dist <= M.NEAR_MAX:
                continue
            tgt = cluster_centroid(hits, nearest[1])
            dx, dy, dz = (tgt[i] - pos[i] for i in range(3))
            ry = math.atan2(-dx, -dz)
            rx = math.atan2(dy, math.hypot(dx, dz))
            block_re = re.compile(
                r'(\[node name="%s"[^\]]*\].*?rotation = Vector3\()([^)]+)(\))'
                % re.escape(name), re.S)
            mm = block_re.search(src)
            if not mm:
                continue
            src = src[:mm.start(2)] + "%.4f, %.4f, 0.0" % (rx, ry) + \
                src[mm.end(2):]
            changed = True
            fixed += 1
            print("re-aimed  %-24s %-28s → %s" % (locale, name, nearest[0]))
        if changed:
            open(path, "w").write(src)
    print("%d marker(s) re-aimed" % fixed)


if __name__ == "__main__":
    main()
