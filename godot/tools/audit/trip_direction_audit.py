#!/usr/bin/env python3
"""trip_direction_audit.py — resources/vn/trip_direction.json holds to the chapters.

The trip is directed per scene (tools/trip_direction.py, GameEngine.
_trip_scene_start, 2026-11-08). Fails on: a scene id that is no chapter,
a level outside 0..1.5, a register TripSync does not have, a beat on a
node the scene does not have or outside 0..1.5. Reports how many scenes
are directed and how many chapters have no direction (a new chapter:
rebuild with `python3 tools/trip_direction.py`).
"""
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
GODOT = os.path.normpath(os.path.join(HERE, "..", ".."))
SCENES = os.path.join(GODOT, "resources", "scenes")
PLAN = os.path.join(GODOT, "resources", "vn", "trip_direction.json")
TRIPSYNC = os.path.join(GODOT, "autoload", "TripSync.gd")


def registers():
    s = open(TRIPSYNC, encoding="utf-8").read()
    i = s.index("const REGISTERS")
    j = s.index("\n}\n", i)
    return set(re.findall(r'^\t"(\w+)": \{', s[i:j], re.M))


def chapters():
    out = {}
    for dirpath, _dirs, files in os.walk(SCENES):
        for fn in files:
            if not fn.endswith(".json"):
                continue
            try:
                j = json.load(open(os.path.join(dirpath, fn), encoding="utf-8"))
            except Exception:
                continue
            if isinstance(j, dict) and isinstance(j.get("nodes"), list):
                out[j.get("id") or fn[:-5]] = len(j["nodes"])
    return out


def main():
    if not os.path.exists(PLAN):
        print("trip_direction_audit · no plan (python3 tools/trip_direction.py) · 1 problem(s)")
        return 1
    plan = json.load(open(PLAN, encoding="utf-8")).get("scenes", {})
    regs = registers()
    chs = chapters()
    bad = []
    for sid, e in plan.items():
        if sid not in chs:
            bad.append("SCENE  %s: no such chapter" % sid)
            continue
        lv = e.get("level")
        if not isinstance(lv, (int, float)) or not 0.0 <= lv <= 1.5:
            bad.append("LEVEL  %s: %r (0..1.5)" % (sid, lv))
        reg = e.get("register")
        if reg is not None and reg not in regs:
            bad.append("REG    %s: register %r is not one of TripSync's" % (sid, reg))
        for b in e.get("beats", []) or []:
            nd, tr = b.get("node"), b.get("trip")
            if not isinstance(nd, int) or not 0 <= nd < chs[sid]:
                bad.append("BEAT   %s: node %r outside the scene (%d nodes)" % (sid, nd, chs[sid]))
            if not isinstance(tr, (int, float)) or not 0.0 <= tr <= 1.5:
                bad.append("BEAT   %s: trip %r (0..1.5)" % (sid, tr))
    for b in bad:
        print(b)
    missing = sorted(set(chs) - set(plan))
    print("trip_direction_audit · %d scene(s) directed · %d chapter(s) undirected · %d problem(s)"
          % (len(plan), len(missing), len(bad)))
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
