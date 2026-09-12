#!/usr/bin/env python3
"""page_length_audit.py — a page the box would have to shrink (2026-09-12).

DialogueBox keeps its full 34 px body up to 260 visible characters and
then auto-fits, stepping the font toward HALF SIZE so the passage fits
the box. Past ~300 the result is the Deck read: "too much text on
screen at once and it gets too small and cramped." page_split.py
turned 2,147 such nodes into pages at sentence boundaries; this keeps
it that way.

A narrate / say / think node whose visible text (directives and inline
markup stripped) exceeds LIMIT fails. Inline [fade …] passages are
never split (2 of them) and are excused by name.

    python3 godot/tools/audit/page_length_audit.py
    python3 godot/tools/audit/page_length_audit.py --all

Gate at zero. The fix is `page_split.py <scene.json>`, not a bigger
limit.
"""
import glob
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
SCENES = os.path.join(ROOT, "godot", "resources", "scenes")

LIMIT = 300
TEXT_TYPES = ("narrate", "say", "think")
DIRECT = re.compile(r"^(\[[a-z]+:[^\]]*\]\s*)+")
MARKUP = re.compile(r"\[/?[a-z]+[^\]]*\]")

# (scene id, node index): why it stays long.
DELIBERATE = {}


def visible(text):
    return MARKUP.sub("", DIRECT.sub("", text)).strip()


def main():
    show_all = "--all" in sys.argv
    checked, problems = 0, []
    for f in sorted(glob.glob(os.path.join(SCENES, "**", "*.json"), recursive=True)):
        if os.path.basename(f) == "index.json":
            continue
        j = json.load(open(f, encoding="utf-8"))
        sid = j.get("id", os.path.basename(f)[:-5])
        for i, n in enumerate(j.get("nodes", [])):
            if n.get("t") not in TEXT_TYPES or not isinstance(n.get("text"), str):
                continue
            checked += 1
            body = n["text"]
            v = visible(body)
            if len(v) <= LIMIT:
                continue
            if "[fade" in body:
                if show_all:
                    print("ok(fade) %-30s #%-4d %d chars" % (sid, i, len(v)))
                continue
            if (sid, i) in DELIBERATE:
                if show_all:
                    print("ok(kept) %-30s #%-4d %s" % (sid, i, DELIBERATE[(sid, i)]))
                continue
            problems.append((sid, i, len(v), v[:70]))
    for sid, i, ln, head in problems:
        print("LONG    %-30s #%-4d %4d chars · %s…" % (sid, i, ln, head))
    print("\npage_length_audit · %d page(s) · %d over %d characters"
          % (checked, len(problems), LIMIT))
    return 1 if problems else 0


if __name__ == "__main__":
    sys.exit(main())
