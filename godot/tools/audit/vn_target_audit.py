#!/usr/bin/env python3
"""vn_target_audit.py — where a choice's branches actually land
(design pillar, 2026-09-19).

Found by hand while paying off loose flags: vol1_ch1_s2's second option
and its passed logic check pointed at `jump vol1_end` nodes, ending the
volume before the Stranger's written replies played; vol2_graveyard's
"I'll sell it." pointed two nodes BACK, at the think before the choice,
so the choice re-opened forever. Every goto/pass/fail in the game was
an index typed by hand, and nothing checked the indices.

For every choice option target (goto, check.pass, check.fail):
  · BACKWARD — the target is at or before the choice (a loop);
  · OOB      — the target is past the scene's last node;
  · ONTO_END — the target is an `end` node (the reply is silence and
    the game stops);
  · SELF     — the target is another choice (a choice landing on a
    choice with no line between);
  · ONTO_JUMP (info) — the target is a `jump`: legitimate when the
    option is a silence ("Listen. Say nothing."), listed so a typo
    that skips a written reply is visible.

    python3 godot/tools/audit/vn_target_audit.py
    python3 godot/tools/audit/vn_target_audit.py --all

Gate at zero on the first four.
"""
import glob
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
SCENES = os.path.join(ROOT, "godot", "resources", "scenes")


def main():
    show_all = "--all" in sys.argv
    problems, info, seen = [], [], 0
    for p in sorted(glob.glob(os.path.join(SCENES, "vol*", "*.json"))):
        sid = os.path.basename(p)[:-5]
        try:
            d = json.load(open(p, encoding="utf-8"))
        except Exception as e:
            problems.append(("BAD_JSON", sid, str(e)))
            continue
        ns = d.get("nodes", []) if isinstance(d, dict) else []
        for i, n in enumerate(ns):
            if not isinstance(n, dict) or n.get("t") != "choice":
                continue
            for oi, o in enumerate(n.get("opts", [])):
                targets = []
                if "goto" in o:
                    targets.append(("goto", o["goto"]))
                c = o.get("check")
                if isinstance(c, dict):
                    for k in ("pass", "fail"):
                        if k in c:
                            targets.append((k, c[k]))
                for k, v in targets:
                    seen += 1
                    where = "%s#%d opt %d %s→%s" % (sid, i, oi, k, v)
                    if not isinstance(v, int):
                        continue
                    if v >= len(ns):
                        problems.append(("OOB", where, "scene has %d nodes" % len(ns)))
                    elif v <= i:
                        problems.append(("BACKWARD", where, "lands on %s at/before the choice" % ns[v].get("t")))
                    else:
                        tt = ns[v].get("t")
                        if tt == "end":
                            problems.append(("ONTO_END", where, "the reply is silence and the game stops"))
                        elif tt == "choice":
                            problems.append(("SELF", where, "a choice landing on a choice"))
                        elif tt == "jump":
                            info.append(("ONTO_JUMP", where, "→ %s" % ns[v].get("scene")))
    for kind, where, why in problems:
        print("%-9s %-44s %s" % (kind, where, why))
    if show_all:
        for kind, where, why in info:
            print("%-9s %-44s %s  (info)" % (kind, where, why))
    print("\nvn_target_audit · %d target(s) · %d problem(s) · %d onto a jump" % (seen, len(problems), len(info)))
    return 1 if problems else 0


if __name__ == "__main__":
    sys.exit(main())
