#!/usr/bin/env python3
"""narrated_object_audit.py — the narrator names it, the camera ignores it
(2026-10-12). A report, not a gate.

The user, on Diego's room: "The director should be focusing on the items
in Diego's room as they are being called out by the narrator." The
director cuts only on explicit `[shot:...]` cues; a narrated line that
names the duffel, the clock or the lamp with no cue leaves the camera on
whatever it last held. This walks every chapter the way the engine does —
the current `3d:<preset>` background, the locale's `shot_insert_<x>`
markers (plain and `__<preset>`-suffixed) — and lists each narrate line
that has NO shot cue but names an object the room already has an insert
for. Each row is a cue to add: `[shot:insert <x>]` on that line.

    python3 godot/tools/audit/narrated_object_audit.py              # every chapter
    python3 godot/tools/audit/narrated_object_audit.py diego_bedroom # one locale

Words match whole words (plural and singular), so `glass` does not fire on
`glasses` reading-glasses lines unless the room's cue is `glasses`.
Common words that are also cues (`door`, `window`, `table`) are listed but
marked `common` — read the line before cutting on them.
"""
import glob
import json
import os
import re
import sys
from collections import defaultdict

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
GODOT = os.path.join(ROOT, "godot")
SCENES = os.path.join(GODOT, "resources", "scenes")
TSCN = os.path.join(GODOT, "scenes", "locales")
BG3D = os.path.join(GODOT, "scripts", "vn", "Background3D.gd")
COMMON = {"door", "window", "table", "floor", "wall", "room", "light", "hand", "hands", "face", "chair"}


def presets():
    src = open(BG3D).read()
    out = {}
    for m in re.finditer(r'\t"([a-z0-9_]+)": \{\n(?:\t\t[^\n]*\n)*?\t\t"scene": "res://scenes/locales/([a-z0-9_]+)\.tscn"', src):
        out[m.group(1)] = m.group(2)
    return out


def inserts(locale, preset):
    path = os.path.join(TSCN, locale + ".tscn")
    if not os.path.exists(path):
        return set()
    names = set()
    for m in re.finditer(r'\[node name="shot_insert_([a-z0-9_]+?)(?:__([a-z0-9_]+))?" type="Marker3D"', open(path).read()):
        if m.group(2) in (None, preset):
            names.add(m.group(1))
    return names


def nodes_of(path):
    try:
        d = json.load(open(path))
    except (OSError, ValueError):
        return []
    n = d.get("nodes") if isinstance(d, dict) else d
    return n if isinstance(n, list) else []


def main():
    import signal
    signal.signal(signal.SIGPIPE, signal.SIG_DFL)   # piping into head is fine
    only = sys.argv[1] if len(sys.argv) > 1 else None
    pre = presets()
    rows = defaultdict(list)
    for f in sorted(glob.glob(os.path.join(SCENES, "vol*", "*.json"))):
        cur = None
        recent = []          # the inserts cut to in the last few lines: no re-cut on a repeat mention
        for i, n in enumerate(nodes_of(f)):
            if not isinstance(n, dict):
                continue
            if n.get("t") == "bg":
                src = str(n.get("src", ""))
                cur = src[3:] if src.startswith("3d:") else None
                recent = []
                continue
            text = n.get("text") or ""
            m = re.search(r"\[shot:insert ([a-z0-9_]+)~?\]", text)
            recent = (recent + [m.group(1) if m else ""])[-3:]
            if cur is None or n.get("t") != "narrate" or not text:
                continue
            locale = pre.get(cur)
            if locale is None or (only and only not in (locale, cur)):
                continue
            if "[shot:" in text:
                continue
            body = re.sub(r"\[[^\]]*\]", "", text).lower()
            words = set(re.findall(r"[a-z][a-z'_-]*", body))
            for cue in sorted(inserts(locale, cur)):
                stems = {cue, cue.replace("_", " "), cue.rstrip("s"), cue + "s"}
                hit = any(s in words for s in stems if " " not in s) or any(s in body for s in stems if " " in s)
                if hit and cue in recent:
                    break
                if hit:
                    rows[(locale, cur)].append((os.path.basename(f)[:-5], i, cue, "common" if cue in COMMON else "", body[:90]))
                    break
    total = 0
    for (locale, cur), rr in sorted(rows.items(), key=lambda kv: -len(kv[1])):
        print("== %s (preset %s) · %d line(s)" % (locale, cur, len(rr)))
        for ch, i, cue, tag, body in rr:
            print("   %-30s #%-4d insert %-14s %-6s %s" % (ch, i, cue, tag, body))
        total += len(rr)
    print("narrated_object_audit · %d uncued line(s) name an object the room has an insert for" % total)


if __name__ == "__main__":
    main()
