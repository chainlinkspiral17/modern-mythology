#!/usr/bin/env python3
"""painting_spot_audit.py — the paintings' named spots are real, and used right.

A 2D painting has no markers; resources/vn/painting_spots.json names the
parts of a picture a cue can point at (GameEngine._painting_spot,
2026-11-08): `[shot:insert pool]` on the deep-end painting pushes in on the
pool. An insert whose id the picture does not name falls back to a seeded
glance — fine on a painting that names nothing, a typo on one that does.

Fails on:
  - a spots key that is not a picture on disk
  - a spot that is not [u, v] or [u, v, zoom] with u, v in 0..1, zoom 1..3
  - an insert cue on a painting that HAS spots, naming one it does not have
Reports how many insert cues on paintings are aimed vs seeded.
"""
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
GODOT = os.path.normpath(os.path.join(HERE, "..", ".."))
SCENES = os.path.join(GODOT, "resources", "scenes")
SPOTS = os.path.join(GODOT, "resources", "vn", "painting_spots.json")
sys.path.insert(0, HERE)
import bg_resolve  # noqa: E402

INSERT = re.compile(r"\[shot:insert\s+(\w+)~?\]")


def main():
    spots = json.load(open(SPOTS, encoding="utf-8")) if os.path.exists(SPOTS) else {}
    bad = []
    for key, table in spots.items():
        if key.startswith("_"):
            continue
        if not os.path.exists(os.path.join(GODOT, key)):
            bad.append("SPOTS  %s: no such picture" % key)
            continue
        if not isinstance(table, dict) or not table:
            bad.append("SPOTS  %s: no spots" % key)
            continue
        for sid, v in table.items():
            ok = isinstance(v, list) and len(v) in (2, 3) and all(isinstance(x, (int, float)) for x in v) \
                and 0.0 <= v[0] <= 1.0 and 0.0 <= v[1] <= 1.0 and (len(v) == 2 or 1.0 <= v[2] <= 3.0)
            if not ok:
                bad.append("SPOTS  %s: %s = %r (want [u, v] or [u, v, zoom], u/v 0..1, zoom 1..3)" % (key, sid, v))
    aimed = seeded = 0
    for dirpath, _dirs, files in os.walk(SCENES):
        for fn in sorted(files):
            if not fn.endswith(".json"):
                continue
            try:
                j = json.load(open(os.path.join(dirpath, fn), encoding="utf-8"))
            except Exception:
                continue
            if not isinstance(j, dict):
                continue
            src = ""
            for i, n in enumerate(j.get("nodes", [])):
                if n.get("t") == "bg":
                    raw = n.get("src") or ""
                    src = "" if bg_resolve.preset_of(raw, j.get("id", fn[:-5])) else \
                        bg_resolve.resolve_bg(raw, j.get("id", fn[:-5])).replace("res://", "")
                if not src:
                    continue
                for sid in INSERT.findall(n.get("text") or ""):
                    table = spots.get(src)
                    if isinstance(table, dict) and table:
                        if sid in table:
                            aimed += 1
                        else:
                            bad.append("CUE    %s node %d: insert %s — %s names %s"
                                       % (fn, i, sid, os.path.basename(src), ", ".join(sorted(table))))
                    else:
                        seeded += 1
    for b in bad:
        print(b)
    print("painting_spot_audit · %d painting(s) with spots · %d insert cue(s) aimed · %d seeded · %d problem(s)"
          % (sum(1 for k in spots if not k.startswith("_")), aimed, seeded, len(bad)))
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
