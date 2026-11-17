#!/usr/bin/env python3
"""hero_prop_standin_audit — every hero model stands on its stand-in (pass 436).

A HeroProp node (`HP_*` in a locale .tscn) loads a Hero Studio model over a
procedural stand-in and hides the stand-in's parts (`hide_prefixes`). The
model does not know whether its stand-in still exists: when a pass removed
the cabin's kitchen-sill crow (435) and Board Lords' cab-roof crow (407), both
models went on loading the crow where the text has none. The same node with
no view tag shows its model in every view of the set, whatever its stand-in's
tags say.

This reads each set's builder (the geometry gates' recorded parts) and fails
when an HP node has no part matching its hide prefixes within 1 m of it.

    python3 godot/tools/audit/hero_prop_standin_audit.py
"""
import glob
import math
import os
import re
import sys

sys.argv = sys.argv[:1]
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import vantage_obstruction_audit as V   # noqa: E402

REACH_M = 1.0


def main():
    bad = []
    n = 0
    for p in sorted(glob.glob(os.path.join(HERE, "..", "..", "scenes", "locales", "*.tscn"))):
        s = open(p).read()
        gm = re.search(r'path="res://assets/3d/locales/(\w+)\.glb"', s)
        if not gm:
            continue
        hps = re.findall(r'\[node name="(HP_[^"]*)"[^\]]*\]\n((?:[^\[\n][^\n]*\n)+)', s)
        if not hps:
            continue
        bx = V.boxes_for(gm.group(1)) or []
        if not bx:
            continue
        for nm, body in hps:
            hp = re.search(r'hide_prefixes = PackedStringArray\(([^)]*)\)', body)
            pre = re.findall(r'"([^"]+)"', hp.group(1)) if hp else []
            pm = re.search(r"position = Vector3\(([^)]*)\)", body) or \
                re.search(r"transform = Transform3D\((?:[^,]*,){9}([^)]*)\)", body)
            if not pm or not pre:
                continue
            n += 1
            g = [float(v) for v in pm.group(1).split(",")]
            b = (g[0], -g[2], g[1])
            best = min((math.dist(b, c) for nm2, c, h in bx if any(nm2.startswith(x) for x in pre)), default=None)
            if best is None or best > REACH_M:
                bad.append("%-28s %-34s hides %s — %s" % (os.path.basename(p), nm, pre,
                           "no such part in the builder" if best is None else "nearest such part %.2f m off" % best))
    print("hero_prop_standin_audit · %d hero prop(s) · %d with no stand-in under them" % (n, len(bad)))
    for line in bad:
        print("   " + line)
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
