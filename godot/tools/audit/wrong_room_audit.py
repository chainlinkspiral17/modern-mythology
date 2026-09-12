#!/usr/bin/env python3
"""wrong_room_audit.py — a closeup that cuts to another area (2026-09-12).

One .tscn serves several presets in different AREAS of the same
geometry: salty_tome_interior.tscn is the shop, the kitchenette and the
alley; the diner is the counter and the formal room; lake_palestine is
the shore and the dock. VnDirector resolves `[shot:closeup X]` by
marker NAME from the whole .tscn, so a scene on the dock that cued a
closeup of a person cut to the person/person_b pair authored at the
shore — 15.7 m away, a face in a different picture. Seventy such cuts
across 21 chapters, every one placed by a pass that had been declared
done.

The fix is PER-PRESET MARKERS: `<name>__<preset_id>` belongs to that
preset's area and wins while it is loaded (Background3D.find_shot_
marker / shot_markers_of_type). This audit resolves every closeup cue
the way the engine now does and fails when the frame it lands on is
more than FAR metres (12) from the preset's camera — a closeup is a face at
the conversation spot, and the conversation spot is near the camera.

Inserts are not checked: an insert IS a cut to wherever the object is.

    python3 godot/tools/audit/wrong_room_audit.py
    python3 godot/tools/audit/wrong_room_audit.py --all

Gate at zero.
"""
import glob
import json
import math
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
ROOT = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
GODOT = os.path.join(ROOT, "godot")
SCENES = os.path.join(GODOT, "resources", "scenes")
TSCN = os.path.join(GODOT, "scenes", "locales")

import preset_vantage_audit as PV

# 12 m, not 8: the diner's own named closeups sit 8.4–11 m from its
# preset camera (the booth alcove vs the door) and are the same room;
# the formal room's are 21–23 m away and are not.
FAR = 12.0
CUE = re.compile(r"\[shot:closeup ([^\]]+)\]")

# (preset, cue id): reason — read and kept.
DELIBERATE = {}


def presets():
    src = open(PV.GD).read()
    out = {}
    for m in PV.BLOCK.finditer(src):
        pid, body = m.group(1), m.group(2)
        sm = re.search(r'"scene":\s*"res://scenes/locales/(\w+)\.tscn"', body)
        om = PV.ORIGIN.search(body)
        if sm and om:
            out[pid] = (sm.group(1), tuple(PV._ev(om.group(i)) for i in (1, 2, 3)))
    return out


_MK = {}


def markers(tscn):
    if tscn in _MK:
        return _MK[tscn]
    out = {}
    p = os.path.join(TSCN, tscn + ".tscn")
    if os.path.exists(p):
        src = open(p).read()
        for mm in re.finditer(r'\[node name="(shot_[\w]+)"[^\]]*\](.*?)(?=\n\[|\Z)', src, re.S):
            body = mm.group(2)
            pm = re.search(r"position = Vector3\(([^)]+)\)", body)
            tm = re.search(r"transform = Transform3D\(([^)]+)\)", body)
            if pm:
                v = [float(x) for x in pm.group(1).split(",")]
            elif tm:
                v = [float(x) for x in tm.group(1).split(",")][9:12]
            else:
                continue
            out[mm.group(1)] = tuple(v)
    _MK[tscn] = out
    return out


def resolve(mk, name, preset):
    """The engine's order: the preset's own marker, then the plain one,
    then the preset's generic pair, then the plain pair."""
    for cand in (name + "__" + preset, name,
                 "shot_closeup_person__" + preset, "shot_closeup_person"):
        if cand in mk:
            return cand
    return None


def main():
    show_all = "--all" in sys.argv
    pre = presets()
    checked, problems = 0, []
    for f in sorted(glob.glob(os.path.join(SCENES, "**", "*.json"), recursive=True)):
        if os.path.basename(f) == "index.json":
            continue
        j = json.load(open(f, encoding="utf-8"))
        sid = j.get("id", os.path.basename(f)[:-5])
        pid = None
        for i, n in enumerate(j.get("nodes", [])):
            if n.get("t") == "bg":
                s = str(n.get("src") or "")
                pid = s[3:] if s.startswith("3d:") else None
                continue
            if pid not in pre:
                continue
            tscn, cam = pre[pid]
            mk = markers(tscn)
            for who in CUE.findall(str(n.get("text") or "")):
                cue = who.strip().split()[0]
                name = resolve(mk, "shot_closeup_" + cue, pid)
                if name is None:
                    continue           # blind — shot_marker_audit's job
                checked += 1
                d = math.dist(mk[name], cam)
                if d <= FAR:
                    continue
                if (pid, cue) in DELIBERATE:
                    if show_all:
                        print("ok(kept) %-26s %-14s %s" % (pid, cue, DELIBERATE[(pid, cue)]))
                    continue
                problems.append((sid, i, pid, cue, name, d))
    for sid, i, pid, cue, name, d in problems:
        print("ROOM    %-30s #%-4d closeup %-12s under %-26s lands on %s, %.1f m from the camera"
              % (sid, i, cue, pid, name, d))
    print("\nwrong_room_audit · %d closeup cue(s) resolved · %d land in another area"
          % (checked, len(problems)))
    return 1 if problems else 0


if __name__ == "__main__":
    sys.exit(main())
