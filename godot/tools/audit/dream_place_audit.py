#!/usr/bin/env python3
"""dream_place_audit.py — a dream is a place: the room changes when it starts
(pass 449, 2026-11-22).

Diego dreams of the loading dock twice (vol 6 ch10, ch16), of the stockroom
(ch18), of his grandmother's kitchen (ch22) and of the Gas & Go at night
(ch9) — fifty-odd lines of "In the dream the dock is the dock ..." — and all
five played over the room he was asleep in. No gate objected: no line carried
a cue the bedroom lacked.

A dream STARTS on a narrated line in the present tense — "he dreams of the
dock", "She dreams, at 03:03, of ...", "In one of the sleeps, he dreams." —
and from there the prose is somewhere else. The gate: within that line and
the two after it the room changes (a bg node, or `[view:preset]` on the line
— tools/audit/inline_view.py), or the dream is JUDGED below with the reason
it has no place to cut to.

Recounted dreams ("Nate told me he had had a dream", "In the dream she had
been standing ...") are past tense and are not starts; a negated one ("He
does not dream of the dock") is not a dream.

    python3 godot/tools/audit/dream_place_audit.py [--all]
"""
import glob
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
GODOT = os.path.normpath(os.path.join(HERE, "..", ".."))
SCENES = os.path.join(GODOT, "resources", "scenes")
sys.path.insert(0, HERE)
import inline_view as IV   # noqa: E402

# present tense, a person as subject: "he dreams", "Diego dreams", "she
# dreams, for the first time", "In the dream he is"
# ("The dreams had not been ..." is a noun: a determiner is not a dreamer)
_DET = r"(?!(?:The|These|Those|His|Her|Their|My|Our|Your|Such|What|Bad|Most|All|No|Some)\b)"
START = re.compile(r"\b(?:[Hh]e|[Ss]he|" + _DET + r"[A-Z][a-z]+) dreams\b"
                   r"|\b[Ii]n the dream (?:he|she|" + _DET + r"[A-Z][a-z]+) is\b")
NOT = re.compile(r"\b(?:does not|doesn't|did not|never|no longer) dream", re.I)
REACH = 2          # the cut lands on the line, or within the two after it
RUN_GAP = 6        # lines of the same dream: one start, not one per sentence

# (scene id, node) -> why this dream has no room to cut to
JUDGED = {
    ("vol6_ch3_sam_bedroom", 21): "she dreams of her father in a photograph she has never seen — "
                                  "a picture, not a place (a panel, when the photograph exists)",
}


def main():
    show_all = "--all" in sys.argv
    problems, starts = [], 0
    for f in sorted(glob.glob(os.path.join(SCENES, "**", "*.json"), recursive=True)):
        if os.path.basename(f) == "index.json":
            continue
        try:
            j = json.load(open(f, encoding="utf-8"))
        except Exception:
            continue
        if not isinstance(j, dict):
            continue
        sid = j.get("id", os.path.basename(f)[:-5])
        nodes = j.get("nodes", [])
        # node index -> True where the room changes (a bg node, or a line that cuts)
        cut_at = set()
        room = {}
        cur = None
        for i, n in IV.walk(nodes):
            if isinstance(n, dict) and n.get("t") == "bg":
                cut_at.add(i)
                cur = str(n.get("src") or "")
            room[i] = cur
        last_start = -99
        for i, n in enumerate(nodes):
            if not isinstance(n, dict) or n.get("t") != "narrate":
                continue
            text = re.sub(r"\[[^\]]*\]", "", str(n.get("text") or ""))
            if not START.search(text) or NOT.search(text):
                continue
            # a 3D set is where a cut is possible (vols 1-4 play over paintings)
            if not str(room.get(i) or "").startswith("3d:"):
                continue
            if i - last_start <= RUN_GAP:
                last_start = i
                continue
            last_start = i
            starts += 1
            # the cut may stand just before the line (a bg node), on it, or
            # within REACH lines after it
            lines_after, k, ok = 0, i, False
            back = i - 1
            while back >= 0 and isinstance(nodes[back], dict) and nodes[back].get("t") not in IV.TEXT:
                if back in cut_at:
                    ok = True
                back -= 1
            while not ok and k < len(nodes) and lines_after <= REACH:
                if k in cut_at:
                    ok = True
                    break
                k += 1
                if k < len(nodes) and isinstance(nodes[k], dict) and nodes[k].get("t") in IV.TEXT:
                    lines_after += 1
            if ok:
                if show_all:
                    print("ok        %-30s #%-4d %s" % (sid, i, text[:70]))
                continue
            if (sid, i) in JUDGED:
                if show_all:
                    print("ok(kept)  %-30s #%-4d %s" % (sid, i, JUDGED[(sid, i)][:70]))
                continue
            problems.append((sid, i, room.get(i), text))
    for sid, i, rm, text in problems:
        print("DREAM   %-30s #%-4d plays on in %s\n        %s" % (sid, i, rm, text[:120]))
    print("\ndream_place_audit · %d dream(s) start in a 3D set · %d with no change of room"
          % (starts, len(problems)))
    return 1 if problems else 0


if __name__ == "__main__":
    sys.exit(main())
