#!/usr/bin/env python3
"""scene_open_bg_audit.py — no chapter opens on a bare stage (pass 442).

vol7 ch8 Roy's first five lines come before its first bg node: in play a
jump from finn_speaks leaves the supper on the stage, but a load or chapter
select into them showed black. Such a scene names the room its opening
lines play in as a top-level "bg_in" (GameEngine shows it when the stage is
empty). This fails any playable scene whose first line (narrate/say/think)
precedes its first bg node and has no "bg_in" — and any "bg_in" that names
a 3D preset Background3D does not have.

Stubs, tests, trailers, interludes and _demo scenes are skipped.

    python3 godot/tools/audit/scene_open_bg_audit.py
"""
import glob
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
GODOT = os.path.normpath(os.path.join(HERE, "..", ".."))
SKIP = re.compile(r"stub|test|trailer|interlude|/_demo/")


def presets():
    src = open(os.path.join(GODOT, "scripts", "vn", "Background3D.gd"), encoding="utf-8").read()
    return set(re.findall(r'^\t"([a-z0-9_]+)": \{', src, re.M))


def main():
    known = presets()
    bad = []
    n = 0
    for f in sorted(glob.glob(os.path.join(GODOT, "resources", "scenes", "*", "*.json"))):
        if SKIP.search(f.replace(os.sep, "/")):
            continue
        try:
            d = json.load(open(f, encoding="utf-8"))
        except Exception:
            continue
        nodes = d.get("nodes") if isinstance(d, dict) else None
        if not nodes:
            continue
        n += 1
        first_line = first_bg = None
        for i, nd in enumerate(nodes):
            t = nd.get("t") if isinstance(nd, dict) else None
            if t == "bg" and first_bg is None:
                first_bg = i
            if t in ("say", "narrate", "think") and first_line is None:
                first_line = i
        rel = os.path.relpath(f, GODOT)
        bg_in = d.get("bg_in", "")
        if bg_in:
            if bg_in.startswith("3d:") and bg_in[3:] not in known:
                bad.append("%s: bg_in %s names no Background3D preset" % (rel, bg_in))
            continue
        if first_line is not None and (first_bg is None or first_bg > first_line):
            bad.append("%s: line %d plays before the first bg (node %s) and the scene has no bg_in"
                       % (rel, first_line, first_bg))
    for b in bad:
        print("BARE  " + b)
    print("scene_open_bg_audit · %d scene(s) · %d open on a bare stage" % (n, len(bad)))
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
