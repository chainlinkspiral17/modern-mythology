#!/usr/bin/env python3
"""trip_fight_audit.py — a trip push fighting a cool mood (2026-09-12).

The director holds THE TRIP at three levels (bible, "the three dials"):
the mood's `trip_scale` (bright, plain daylight runs COOL — day_bright
0.7, morning_bright 0.7, studio 0.6, lunch 0.75), the `[trip:X]` cue
on a beat, and the register. They multiply. So a `[trip:1.2]` placed on
a line whose mood has just dialled itself to 0.7 is a scene arguing
with itself: the mood says "this is daylight, keep the layer low" and
the cue says "push it" in the same breath, and the Deck's standing
verdict is that light laid on a bright picture "adds nothing … it
really only looks good on darker scenes."

Eighty-five of those existed, all from one mechanical pass (190
interlude beats given `[trip:1.2]` as "the structural turn pushes the
layer" without reading the mood under each). The Lovers' opening was
the one the Deck caught — "warm and cozy and domestic, not garish and
weird" — and it had morning_bright 0.7 × [trip:1.2] on line one.

RULE: a push above 1.0 on a mood scaled under COOL is a contradiction
unless it is in DELIBERATE with a reason. A push on a dark mood is the
bible's own direction and is never flagged.

    python3 godot/tools/audit/trip_fight_audit.py
    python3 godot/tools/audit/trip_fight_audit.py --all

Gate at zero.
"""
import glob
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
GODOT = os.path.join(ROOT, "godot")
SCENES = os.path.join(GODOT, "resources", "scenes")
MOODS = os.path.join(GODOT, "scripts", "MoodCycler.gd")

COOL = 0.85        # a mood scaled under this has dialled itself down
PUSH = 1.0         # a cue above this is a push

CUE_RX = re.compile(r"\[(mood|trip):([^\]]+)\]")

# (scene id, node index): reason — read and kept on purpose.
DELIBERATE = {}


def mood_scales():
    src = open(MOODS, encoding="utf-8").read()
    return {m.group(1): float(m.group(2)) for m in re.finditer(
        r'"name":\s*"(\w+)"[^}]*?"trip_scale":\s*([0-9.]+)', src)}


def main():
    show_all = "--all" in sys.argv
    scale = mood_scales()
    problems, pushes = [], 0
    for f in sorted(glob.glob(os.path.join(SCENES, "**", "*.json"), recursive=True)):
        if os.path.basename(f) == "index.json":
            continue
        j = json.load(open(f, encoding="utf-8"))
        sid = j.get("id", os.path.basename(f)[:-5])
        mood = None
        for i, n in enumerate(j.get("nodes", [])):
            t = str(n.get("text") or "")
            if not t.startswith("["):
                continue
            cues = CUE_RX.findall(t)
            # a [mood:] on the same line governs the [trip:] beside it
            for k, v in cues:
                if k == "mood":
                    mood = v.strip()
            for k, v in cues:
                if k != "trip":
                    continue
                try:
                    tv = float(v)
                except ValueError:
                    continue
                if tv <= PUSH:
                    continue
                pushes += 1
                ms = scale.get(mood)
                if ms is None or ms >= COOL:
                    continue
                if (sid, i) in DELIBERATE:
                    if show_all:
                        print("ok(kept) %-30s #%-4d %s" % (sid, i, DELIBERATE[(sid, i)]))
                    continue
                problems.append((sid, i, mood, ms, tv))
    for sid, i, mood, ms, tv in problems:
        print("FIGHT   %-30s #%-4d [trip:%.1f] on %s (%.2f) — the mood says cool"
              % (sid, i, tv, mood, ms))
    print("\ntrip_fight_audit · %d push(es) · %d fighting a cool mood"
          % (pushes, len(problems)))
    return 1 if problems else 0


if __name__ == "__main__":
    sys.exit(main())
