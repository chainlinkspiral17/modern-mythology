#!/usr/bin/env python3
"""vn_skill_audit.py — a skill check the reader cannot pass is a lie
(design pillar, 2026-09-17).

Found by consequence_map.py: no node ever raised a skill, so every
labelled "[LOGIC] …" option in the game took its fail branch. Now that
options can train a skill (`"skill": "<name>"` on a choice option,
GameEngine._do_choice), this gates the arithmetic:

  · CANNOT_PASS — a check whose `diff` exceeds what its skill can have
    been earned before that scene in index.json reading order;
  · UNKNOWN     — a `skill` or check names something not in the five;
  · NO_EARN     — a volume checks a skill it never lets the reader
    train (the check is a wall, not a door);
  · DECORATIVE  — a check whose pass and fail land on the same node
    (informational: the label promises a difference it does not make).

    python3 godot/tools/audit/vn_skill_audit.py
    python3 godot/tools/audit/vn_skill_audit.py --all

Gate at zero on the first three.
"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import consequence_map as CM


def main():
    show_all = "--all" in sys.argv
    vols = CM.load_volumes()
    problems, info = [], []
    checks = 0
    for vol, v in vols.items():
        earned_in_vol = set(o["skill"] for ch in v["choices"] for o in ch["opts"] if o["skill"])
        for ch in v["choices"]:
            for o in ch["opts"]:
                if o["skill"] and o["skill"] not in CM.SKILLS:
                    problems.append(("UNKNOWN", "%s#%d" % (ch["scene"], ch["node"]), "option trains '%s'" % o["skill"]))
        for c in v["checks"]:
            checks += 1
            where = "%s#%d" % (c["scene"], c["node"])
            if c["skill"] not in CM.SKILLS:
                problems.append(("UNKNOWN", where, "check on '%s'" % c["skill"]))
                continue
            if c["skill"] not in earned_in_vol:
                problems.append(("NO_EARN", where, "vol %d never trains %s" % (vol, c["skill"])))
            elif c["diff"] > c["earnable"]:
                problems.append(("CANNOT_PASS", where, "%s ≥ %d but only %d earnable before this scene"
                                 % (c["skill"], c["diff"], c["earnable"])))
            if c["pass"] == c["fail"]:
                info.append(("DECORATIVE", where, "%s check lands on #%s either way" % (c["skill"], c["pass"])))
            elif show_all:
                print("ok      %-28s %s ≥ %d (earnable %d)" % (where, c["skill"], c["diff"], c["earnable"]))
    for kind, where, why in problems:
        print("%-12s %-28s %s" % (kind, where, why))
    for kind, where, why in info:
        print("%-12s %-28s %s  (info)" % (kind, where, why))
    print("\nvn_skill_audit · %d check(s) · %d problem(s) · %d decorative"
          % (checks, len(problems), len(info)))
    return 1 if problems else 0


if __name__ == "__main__":
    sys.exit(main())
