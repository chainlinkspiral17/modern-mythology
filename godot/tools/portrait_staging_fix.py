#!/usr/bin/env python3
"""portrait_staging_fix.py — retire the hide-and-reshow flickers (2026-11-09).

The user: "portraits still just cutting out and not transitioning smoothly
between shots". Some chapters stage a two-person exchange ONE portrait at a
time — show Kai, hide Finn, a line, show Finn, hide Kai, a line … — so the
portraits flick in and out on every line (vol7_ch7_night swaps eight times
in twelve lines). The speaker highlight (CharLayer.activate_speaker) is the
tool for "who is talking"; the stage should hold both.

Two narrow rules, simulated over each chapter's nodes:

  A. a HIDE whose character is shown again AT THE SAME SLOT within
     REAPPEAR_LINES text lines, with no room change between: the hide and
     that re-show are both retired — the character simply stays.
  B. a SHOW that is hidden again before any line plays (never seen): both
     are retired.

A retired node keeps its place ({"t": "retired", "was": {...}}; GameEngine
runs straight on), so every node index — voice lines, saves, trip beats,
painting cues — still holds. A file is rewritten only if it round-trips
byte-for-byte unchanged at its own indent.

    python3 tools/portrait_staging_fix.py --dry      # what would change
    python3 tools/portrait_staging_fix.py            # write
"""
import glob
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
SCENES = os.path.normpath(os.path.join(HERE, "..", "resources", "scenes"))
REAPPEAR_LINES = 6
TEXT = ("narrate", "say", "think")


def _key(c):
    return re.sub(r"[^a-z0-9]+", "_", str(c).lower()).strip("_")


def plan(nodes):
    """the node indices to retire"""
    retire = set()
    stage = {}            # pos -> (char, show_index, line_at_show)
    line = 0
    for i, n in enumerate(nodes):
        if not isinstance(n, dict):
            continue
        t = n.get("t")
        if t in TEXT:
            line += 1
        elif t == "bg":
            stage.clear()
        elif t == "show":
            pos = n.get("pos", "center")
            stage[pos] = (_key(n.get("char", "")), i, line)
        elif t == "hide":
            pos = n.get("pos", "")
            targets = [p for p in stage if pos == "" or p == pos]
            if pos == "" or len(targets) != 1:
                for p in targets:
                    del stage[p]
                continue
            who, si, sl = stage[pos]
            # B: shown and hidden with no line between — never seen
            if sl == line and si not in retire:
                retire.update((si, i))
                del stage[pos]
                continue
            # A: the same character back at the same slot soon, same room
            back = None
            lines_ahead = 0
            for k in range(i + 1, len(nodes)):
                m = nodes[k]
                if not isinstance(m, dict):
                    continue
                mt = m.get("t")
                if mt == "bg" or mt == "jump" or mt == "end" or mt == "choice":
                    break
                if mt in TEXT:
                    lines_ahead += 1
                    if lines_ahead > REAPPEAR_LINES:
                        break
                if mt == "hide" and (m.get("pos", "") in ("", pos)):
                    break
                if mt == "show" and m.get("pos", "center") == pos:
                    if _key(m.get("char", "")) == who:
                        back = k
                    break
            if back is not None:
                retire.update((i, back))
                continue        # the character stays on stage
            del stage[pos]
    return retire


def main():
    dry = "--dry" in sys.argv
    total = files = 0
    for f in sorted(glob.glob(os.path.join(SCENES, "**", "*.json"), recursive=True)):
        raw = open(f, encoding="utf-8").read()
        try:
            j = json.loads(raw)
        except Exception:
            continue
        if not isinstance(j, dict) or not isinstance(j.get("nodes"), list):
            continue
        r = plan(j["nodes"])
        if not r:
            continue
        lines = raw.split("\n")
        ind = len(lines[1]) - len(lines[1].lstrip(" ")) if len(lines) > 1 else 2
        fmt = None
        for ea in (False, True):
            for nl in ("\n", ""):
                if fmt is None and json.dumps(j, indent=ind, ensure_ascii=ea) + nl == raw:
                    fmt = (ea, nl)
        if fmt is None:
            print("SKIP (does not round-trip) %s" % os.path.relpath(f, SCENES))
            continue
        for i in sorted(r):
            n = j["nodes"][i]
            j["nodes"][i] = {"t": "retired", "was": n}
        total += len(r)
        files += 1
        print("%-44s retired %2d staging node(s): %s" % (j.get("id"), len(r), sorted(r)[:12]))
        if not dry:
            with open(f, "w", encoding="utf-8") as fh:
                fh.write(json.dumps(j, indent=ind, ensure_ascii=fmt[0]) + fmt[1])
    print("\nportrait_staging_fix · %d node(s) in %d chapter(s) %s" % (total, files, "would retire" if dry else "retired"))
    return 0


if __name__ == "__main__":
    sys.exit(main())
