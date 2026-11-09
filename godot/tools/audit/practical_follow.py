#!/usr/bin/env python3
"""practical_follow.py — a ceiling fixture's light moves with it (2026-11-09).

The ceiling fixtures now snap onto their tile grids (safety.on_ceiling_grid,
ceiling_grid_audit). A practical light (`<Fixture>_Practical`) placed at the
old spot would hang beside its fixture. For every set with a tile grid, each
named practical whose fixture is a CEILING fixture under that grid takes the
fixture's centre across the ceiling (x / y); its height is kept. Matching is
orphan_practical_audit's (the fixture the name claims, nearest first).

    python3 tools/audit/practical_follow.py          # what would move
    python3 tools/audit/practical_follow.py --write  # move them
"""
import glob
import math
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import vantage_obstruction_audit as VO  # noqa: E402
import orphan_practical_audit as O  # noqa: E402
import ceiling_grid_audit as C  # noqa: E402

SCENES = os.path.normpath(os.path.join(HERE, "..", "..", "scenes", "locales"))
MOVE_MIN = 0.02
MOVE_MAX = 1.2


def main():
    write = "--write" in sys.argv
    moved = 0
    for path in sorted(glob.glob(os.path.join(SCENES, "*.tscn"))):
        loc = os.path.basename(path)[:-5]
        try:
            boxes = VO.boxes_for(loc)
        except Exception:
            continue
        g = C.grid_of(boxes or [])
        if g is None:
            continue
        src = open(path, encoding="utf-8").read()
        out = src
        for m in re.finditer(r'\[node name="([^"]+)" type="(?:Omni|Spot)Light3D"[^\]]*\]\n((?:[^\[][^\n]*\n)*)', src):
            name, body = m.group(1), m.group(2)
            stem = O.practical_stem(name)
            if not stem:
                continue
            pos = O.light_pos_blender(body)
            if pos is None:
                continue
            cands = [b for b in O.matches(stem, boxes) if abs((b[1][2] + b[2][2]) - g["z"]) <= 0.12]
            if not cands:
                continue
            fx = min(cands, key=lambda b: math.dist(b[1][:2], pos[:2]))
            dx, dy = fx[1][0] - pos[0], fx[1][1] - pos[1]
            d = math.hypot(dx, dy)
            if d < MOVE_MIN or d > MOVE_MAX:
                continue
            # godot (x, y, z) = blender (x, z, -y)
            nx, nz = fx[1][0], -fx[1][1]
            new_body = body
            pm = re.search(r"position = Vector3\(([^)]+)\)", body)
            tm = re.search(r"transform = Transform3D\(([^)]+)\)", body)
            if pm:
                v = [x.strip() for x in pm.group(1).split(",")]
                new_body = body.replace(pm.group(0), "position = Vector3(%.3f, %s, %.3f)" % (nx, v[1], nz))
            elif tm:
                v = [x.strip() for x in tm.group(1).split(",")]
                v[9], v[11] = "%.3f" % nx, "%.3f" % nz
                new_body = body.replace(tm.group(0), "transform = Transform3D(%s)" % ", ".join(v))
            if new_body != body:
                out = out.replace(m.group(0), m.group(0).replace(body, new_body), 1)
                print("MOVE  %-24s %-34s %.2f m → its fixture %s" % (loc, name, d, fx[0]))
                moved += 1
        if write and out != src:
            open(path, "w", encoding="utf-8").write(out)
    print("practical_follow · %d light(s) %s" % (moved, "moved" if write else "would move"))
    return 0


if __name__ == "__main__":
    sys.exit(main())
