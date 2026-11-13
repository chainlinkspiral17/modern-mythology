#!/usr/bin/env python3
"""orphan_marker_audit.py — insert frames no line ever cuts to (pass 367, 2026-11-13).

An insert marker is half a shot. The other half is the `[shot:insert <id>]`
on the line that names the object. Pass 366 found the motel pool ("Red silt
settles on the skin of the water"), the motel television and the gas
station's ice chest each framed, read, committed — and cued by nothing,
while a wrong line elsewhere borrowed the pool. A scan then found 223 such
markers in 86 scenes: frames authored for a line (many quote it in their
comment) that the player never sees.

For every `shot_insert_*` marker of every locale .tscn this resolves the
chapters' cues the way the engine does (`<name>__<preset>` first, then the
plain name) and lists the markers nothing reaches. A plain marker whose
preset-suffixed twin IS reached is not an orphan (it is the fallback).

    python3 godot/tools/audit/orphan_marker_audit.py            # the list, by scene
    python3 godot/tools/audit/orphan_marker_audit.py --lines    # + the uncued lines that name each
    python3 godot/tools/audit/orphan_marker_audit.py --gate     # exit 1 above CEILING

The fix is a cue on the line the frame was made for — then READ THE FRAME
(a cue the gates pass can still be the wrong object: the crow "on the roof"
of a moving car is not the crow on the traffic light). A marker with no
line left (a copied scene's leftovers, a cut passage) is deleted.

CEILING is a ratchet: lower it when a pass cues or deletes; never raise it
(a new marker ships with its cue).
"""
import collections
import glob
import json
import math
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import bg_resolve  # noqa: E402
import wrong_room_audit as W  # noqa: E402

GODOT = os.path.normpath(os.path.join(HERE, "..", ".."))
SCENES = os.path.join(GODOT, "resources", "scenes")
CUE = re.compile(r"\[shot:(\w+)\s+(\w+)~?\]")
CEILING = 133       # 2026-11-13, pass 368 (223 at the first count; 367: 39 cued; 368: 12 cued, 42 dead ones deleted)


def survey():
    """(orphans by tscn, lines by tscn, presets, cameras by tscn)."""
    pre = W.presets()
    by_scene = collections.defaultdict(list)
    for pid, (tscn, cam) in pre.items():
        by_scene[tscn].append((pid, cam))
    used = collections.defaultdict(set)
    lines = collections.defaultdict(list)
    for f in sorted(glob.glob(os.path.join(SCENES, "**", "*.json"), recursive=True)):
        if os.path.basename(f) == "index.json":
            continue
        try:
            j = json.load(open(f, encoding="utf-8"))
        except Exception:
            continue
        if not isinstance(j, dict):
            continue
        ch = os.path.basename(f)[:-5]
        pid = None
        for i, n in enumerate(j.get("nodes", [])):
            if n.get("t") == "bg":
                pid = bg_resolve.preset_of(n.get("src"), j.get("id", ch))
            if pid not in pre:
                continue
            tscn = pre[pid][0]
            mk = W.markers(tscn)
            t = str(n.get("text") or "")
            for typ, sid in CUE.findall(t):
                base = "shot_%s_%s" % (typ, sid)
                for cand in (base + "__" + pid, base):
                    if cand in mk:
                        used[tscn].add(cand)
                        break
            if t and n.get("t") in ("narrate", "say", "think"):
                lines[tscn].append((ch, i, pid, t))
    orphans = {}
    for tscn in sorted(by_scene):
        mk = W.markers(tscn)
        reached = set(u.split("__")[0] for u in used[tscn])
        un = sorted(m for m in mk if m.startswith("shot_insert_") and m.split("__")[0] not in reached)
        if un:
            orphans[tscn] = un
    return orphans, lines, pre, by_scene


def naming_lines(tscn, marker, lines, pre, by_scene):
    """Uncued lines, on a preset this marker serves, that name its object."""
    mk = W.markers(tscn)
    base, _, suf = marker.partition("__")
    words = [w for w in base[len("shot_insert_"):].split("_") if len(w) > 2]
    if not words:
        return []
    pat = re.compile(r"\b(" + "|".join(re.escape(w) + r"(?:s|es)?" for w in words) + r")\b", re.I)
    out = []
    for ch, i, pid, t in lines[tscn]:
        if "[shot:" in t:
            continue
        if suf and pid != suf:
            continue
        if not suf:
            cam = pre[pid][1]
            d = math.dist(mk[marker], cam)
            near = min((math.dist(mk[marker], c2) for q, c2 in by_scene[tscn] if q != pid), default=1e9)
            if d > W.NEAR and near * 2.0 < d:
                continue           # another preset's area: wrong_room_audit would refuse the cue
        if pat.search(re.sub(r"\[[^\]]*\]", "", t)):
            out.append((ch, i, pid, t))
    return out


def main():
    show_lines = "--lines" in sys.argv
    gate = "--gate" in sys.argv
    orphans, lines, pre, by_scene = survey()
    total = sum(len(v) for v in orphans.values())
    if not gate:
        for tscn, un in orphans.items():
            if not show_lines:
                print("%-28s %s" % (tscn, " ".join(u[len("shot_insert_"):] for u in un)))
                continue
            for m in un:
                hits = naming_lines(tscn, m, lines, pre, by_scene)
                print("\n%s  %s" % (tscn, m))
                for ch, i, pid, t in hits[:5]:
                    print("    %s:%d (%s) %s" % (ch, i, pid, re.sub(r"\[[^\]]*\]", "", t)[:150]))
    print("\norphan_marker_audit · %d insert marker(s) no cue reaches, in %d scene(s) (ceiling %d)"
          % (total, len(orphans), CEILING))
    if gate and total > CEILING:
        print("REGRESSION  %d orphan insert marker(s) (ceiling %d): a new marker ships with its cue" % (total, CEILING))
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
