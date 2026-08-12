#!/usr/bin/env python3
"""Shot-cue coverage audit — are the scripts' inserts landing on
anything?

Born 2026-08-12 from the user's note that the vol7 cabin chapters
were "mostly just solid color scenes." The cause was not lazy
direction — those chapters are richly directed — but that a cue
with no matching Marker3D falls back to a BLIND ZOOM: VnDirector
punches the fov to 35 (insert) or 45 (closeup) on the SAME preset
vantage, so the frame fills with whatever flat surface happened to
be in the middle of the wide. Twenty-one [shot:insert bowls] cues
in vol 7 pointed at a table that had no bowls modeled on it.

This audit reads every scene JSON, tracks which 3D background is
in effect at each node, collects the [shot:<type> <id>] cues that
fire against it, and checks the locale's .tscn for the marker
`shot_<type>_<id>` that VnDirector would look for. Missing markers
are reported per locale, ranked by how many cues land blind.

CHARACTER closeups are excluded: `[shot:closeup tem]` is meant to
be answered by the 3D cast (Background3D.CAST_ENABLED), and while
that is off a lens-only punch-in is the intended fallback. What
this hunts is OBJECT cues — inserts, and closeups of things —
which are supposed to frame a specific prop.

Usage:
    python3 godot/tools/audit/shot_marker_audit.py          # summary
    python3 godot/tools/audit/shot_marker_audit.py --all    # every gap
"""
import collections
import json
import os
import re
import sys

ROOT = os.path.normpath(os.path.join(
    os.path.dirname(os.path.abspath(__file__)), "..", ".."))
SCENES = os.path.join(ROOT, "resources", "scenes")
LOCALES_TSCN = os.path.join(ROOT, "scenes", "locales")
BG3D = os.path.join(ROOT, "scripts", "vn", "Background3D.gd")

CUE = re.compile(r"\[shot:([a-z]+)(?:\s+([a-z0-9_]+))?~?\]")

# Cast-answered cues: character closeups. Everything else is an
# object cue and wants a marker.
CAST_TYPES = {"closeup"}
# Known character ids — a closeup of one of these is cast work, not
# a prop frame. Harvested from the say/char fields at runtime.
NEVER_MARKER = {"establish", "wide", "reset"}


def preset_to_scene():
    """preset_id -> the EXACT res:// scene path the preset declares.

    Resolving by basename instead bit once (2026-08-12): the repo
    carries both scenes/cathedral.tscn (the real set, with markers)
    and an orphan scenes/locales/cathedral.tscn (a legacy shell with
    none). A basename search hit the orphan and reported the model
    chapter as having zero coverage. Trust the preset's own path.
    """
    src = open(BG3D).read()
    out = {}
    for m in re.finditer(r'"(\w+)":\s*\{(.*?)\n\t\},', src, re.S):
        pid, body = m.group(1), m.group(2)
        sm = re.search(r'"scene":\s*"res://([\w/]+\.tscn)"', body)
        if sm:
            out[pid] = sm.group(1)
    return out


def markers_in(res_rel_path):
    path = os.path.join(ROOT, res_rel_path)
    if not os.path.exists(path):
        return None
    src = open(path).read()
    return set(re.findall(r'\[node name="(shot_[\w]+)"', src))


def main():
    show_all = "--all" in sys.argv
    p2s = preset_to_scene()
    chars = set()
    # First pass: learn the character ids so closeups of PEOPLE are
    # not reported as missing props.
    for dirpath, _dirs, files in os.walk(SCENES):
        for fn in files:
            if not fn.endswith(".json"):
                continue
            try:
                j = json.load(open(os.path.join(dirpath, fn)))
            except Exception:
                continue
            for n in j.get("nodes", []):
                c = n.get("char")
                if isinstance(c, str) and c:
                    chars.add(c.lower())

    gaps = collections.defaultdict(collections.Counter)
    seen_cues = collections.Counter()
    no_marker_support = collections.Counter()
    for dirpath, _dirs, files in os.walk(SCENES):
        for fn in sorted(files):
            if not fn.endswith(".json"):
                continue
            try:
                j = json.load(open(os.path.join(dirpath, fn)))
            except Exception:
                continue
            cur = ""
            for n in j.get("nodes", []):
                if n.get("t") == "bg":
                    src = str(n.get("src") or "")
                    cur = src[3:] if src.startswith("3d:") else ""
                if not cur:
                    continue
                for typ, sid in CUE.findall(json.dumps(n)):
                    if typ in NEVER_MARKER or not sid:
                        continue
                    if typ in CAST_TYPES and sid in chars:
                        continue
                    seen_cues[(cur, typ, sid)] += 1

    for (preset, typ, sid), n in seen_cues.items():
        tscn = p2s.get(preset)
        if tscn is None:
            no_marker_support[preset] += n
            continue
        have = markers_in(tscn)
        if have is None:
            no_marker_support[preset] += n
            continue
        if ("shot_%s_%s" % (typ, sid)) not in have:
            gaps[preset][(typ, sid)] += n

    total_blind = sum(sum(c.values()) for c in gaps.values())
    print("shot_marker_audit · %d object cues across %d 3D presets"
          % (sum(seen_cues.values()), len({k[0] for k in seen_cues})))
    if no_marker_support:
        print("   (%d cues on presets with no resolvable .tscn — skipped)"
              % sum(no_marker_support.values()))
    ranked = sorted(gaps.items(), key=lambda kv: -sum(kv[1].values()))
    for preset, counter in ranked if show_all else ranked[:14]:
        print("== %-28s %d blind cue(s), %d distinct"
              % (preset, sum(counter.values()), len(counter)))
        for (typ, sid), n in counter.most_common(None if show_all else 6):
            print("     %2dx  shot_%s_%s" % (n, typ, sid))
    if not show_all and len(ranked) > 14:
        print("   … %d more presets (--all)" % (len(ranked) - 14))
    print("\n%d blind object cue(s) across %d preset(s)"
          % (total_blind, len(gaps)))
    return 0


if __name__ == "__main__":
    sys.exit(main())
