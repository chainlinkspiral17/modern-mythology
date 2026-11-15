#!/usr/bin/env python3
"""figure_floor_audit.py — a person standing INSIDE the floor under them
(2026-11-15, pass 394).

Pass 376 taught the recorder to see `human_sculpt.human_figure` people (two
legs, a torso, a head), and the overlap gate found the ones inside walls.
Feet in a floor are not an overlap — standing on a floor touches it — so a
person set at the GROUND height where a floor slab lies over the ground
stood with their shoes inside it and no gate said so: Harmony Creek's
shopkeepers and customers 6 - 10 cm down in their shop floors (they were
placed with the terrain height under the shop), the St. Jude couple 10 cm
inside the north sidewalk, two Graustark kids inside a house.

A figure's leg (`*_Leg_L` / `*_Leg_R`) whose bottom is more than 2 cm below
the top of an exact flat box under it (a slab at most 30 cm thick and 0.8 m
across or more), and above that box's bottom, stands in it. Parts no view
shows together are not asked (view_tags).

    python3 godot/tools/audit/figure_floor_audit.py [locale …]
Gate: zero (there is no baseline).
"""
import glob
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import prop_overlap_audit as P
import view_tags as VT

SINK = 0.02
LEG = re.compile(r"_Leg_[LR]$")


def hits_for(path):
    boxes, _err = P.record_builder(path)
    if not boxes:
        return []
    legs = [(n, c, h) for n, c, h in boxes if LEG.search(n) and h[2] > 0.2]
    if not legs:
        return []
    exact = P.A.TRUE_BOXES
    floors = [(n, c, h) for n, c, h in boxes
              if n in exact and h[2] <= 0.15 and h[0] >= 0.4 and h[1] >= 0.4]
    out = {}
    for n, c, h in legs:
        who = n.rsplit("_Leg_", 1)[0]
        if who in out:
            continue
        bot = c[2] - h[2]
        for fn, fc, fh in floors:
            if fn.startswith(who):
                continue
            if abs(c[0] - fc[0]) <= fh[0] and abs(c[1] - fc[1]) <= fh[1]:
                top, fb = fc[2] + fh[2], fc[2] - fh[2]
                if fb - 0.001 < bot < top - SINK and not VT.never_together(n, fn):
                    out[who] = (fn, top - bot)
                    break
    return sorted((w, f, d) for w, (f, d) in out.items())


def main():
    only = [a for a in sys.argv[1:] if not a.startswith("-")]
    if not getattr(P.A, "STUBS_ON", False):
        P.A.install_stubs()
    paths = sorted(glob.glob(os.path.join(P.A.LOCALES, "build_*.py")))
    total, sets = 0, 0
    for path in paths:
        loc = os.path.basename(path)[6:-3]
        if only and loc not in only:
            continue
        hs = hits_for(path)
        if hs:
            sets += 1
            total += len(hs)
            for who, fn, d in hs:
                print("SUNK   %-24s %-34s in %-30s %3.0f mm" % (loc, who[:34], fn[:30], d * 1000))
    print("figure_floor_audit · %d set(s) read · %d person(s) standing inside the floor under them, in %d set(s)"
          % (len(only) if only else len(paths), total, sets))
    return 1 if total else 0


if __name__ == "__main__":
    sys.exit(main())
