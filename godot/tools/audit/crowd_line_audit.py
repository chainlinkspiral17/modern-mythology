#!/usr/bin/env python3
"""crowd_line_audit.py — the text names a crowd; is anyone in the room? (pass 375, 2026-11-14)

vol 7 ch20 filled an alley with "perhaps thirty-five people" and vol 6 ch22 a
venue with "about a hundred and ten", and both played on empty sets for
months: nothing compared the words with the figures. This does. For every
line that names a crowd it counts the stand-in people (_props.figures: a
prefix with a head and a torso) in THAT LINE'S VIEW — tags, view groups and
strips applied (view_tags) — and lists the views by fewest figures.

    python3 godot/tools/audit/crowd_line_audit.py            # views with 0 or 1 figure
    python3 godot/tools/audit/crowd_line_audit.py --all      # every view a crowd line plays in
    python3 godot/tools/audit/crowd_line_audit.py --lines    # + each line

It counts what the audit stubs RECORD. Figures made by `human_sculpt`
(Graustark's street people, the four parishioners at St. Jude) are not
recorded by the stubs, so a view dressed with them reads low — read the
builder before building a crowd there.

A REPORT, not a gate: the word list is a net, and a hit is read before it
is built ("the crowd out of sight", "her audience had adored it" and a
metaphor are not people in the room). The fix for a real one is a view of
the set by the clock, with its own frames (the VN direction playbook,
passes 373-375).
"""
import collections
import glob
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import bg_resolve  # noqa: E402
import view_tags as VT  # noqa: E402
import vantage_obstruction_audit as VO  # noqa: E402

SCENES = os.path.normpath(os.path.join(HERE, "..", "..", "resources", "scenes"))
NUM = r"(?:a dozen|two dozen|dozens of|twenty|thirty|forty|fifty|sixty|seventy|eighty|ninety|a hundred|hundreds of|\d{2,3})"
CROWD = re.compile(
    r"\b(the crowd|a crowd|crowd of|small crowd|large crowd|the audience|an audience of|congregation|mourners|onlookers|"
    r"spectators|standing room|full house|packed (?:house|room|hall|bar|church|gym)|the whole town (?:was|is|had|came)|"
    r"everyone in the (?:room|bar|diner|church|gym|hall|alley|lot)|line of (?:people|customers)|"
    + NUM + r"(?: or so| and \w+| odd)? (?:people|kids|students|men|women|guests|customers|fans|townspeople|mourners))\b", re.I)
_FIGS = {}


def figures(loc, view):
    key = (loc, view)
    if key not in _FIGS:
        try:
            boxes = VO.boxes_for(loc) or []
        except Exception:
            boxes = []
        base = [b[0].split("__")[0] for b in boxes if VT.in_view(b[0], view)]
        heads = {n[:-5] for n in base if n.endswith("_Head")}
        torsos = {n[:-6] for n in base if n.endswith("_Torso")}
        _FIGS[key] = len(heads & torsos)
    return _FIGS[key]


def main():
    show_all = "--all" in sys.argv
    show_lines = "--lines" in sys.argv
    scenes = VT.scenes()
    hits = collections.defaultdict(list)
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
            if pid not in scenes or n.get("t") not in ("narrate", "say", "think"):
                continue
            t = re.sub(r"\[[^\]]*\]", "", str(n.get("text") or ""))
            if CROWD.search(t):
                hits[(scenes[pid], pid)].append((ch, i, t))
    rows = sorted((figures(loc, pid), -len(ls), loc, pid, ls) for (loc, pid), ls in hits.items())
    shown = 0
    for nf, nl, loc, pid, ls in rows:
        if nf > 1 and not show_all:
            continue
        shown += 1
        print("%3d figure(s) %3d line(s)  %-26s %-28s %s:%d %s" % (nf, -nl, loc, pid, ls[0][0], ls[0][1], ls[0][2][:96]))
        if show_lines:
            for ch, i, t in ls[1:6]:
                print("%45s %s:%d %s" % ("", ch, i, t[:110]))
    empty = sum(1 for r in rows if r[0] == 0)
    print("\ncrowd_line_audit · %d view(s) a crowd line plays in · %d with no figure at all · %d listed"
          % (len(rows), empty, shown))
    return 0


if __name__ == "__main__":
    sys.exit(main())
