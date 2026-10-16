#!/usr/bin/env python3
"""music_coverage_audit.py — the chapter that scores itself by accident
(2026-09-11).

Two failures, both silent by construction:

  1. A CHAPTER WITH NO BED. GameEngine._apply_chapter_music_context()
     hands AudioMgr every catalog entry whose `chapters` names the
     scene. When that comes back empty, AudioMgr.play_next() falls
     through to "the unlocked playlist" — whatever the player has
     heard — so the chapter is scored by whatever came before it.
     234 of 312 scenes were in that state: all of vol6 and vol7 bar a
     dozen, the whole Louisiana arcana run, the vol1 link hub.

  2. A BED THAT IS A FILENAME. The entry exists, the chapter names it,
     and the file was never rendered — which resolves to the same empty
     list and the same fallback. Thirty-six were like this; only vol5's
     four beds and the title theme existed on disk, so every other
     volume played vol5's music.

Both gate at ZERO. A third count — catalog entries no chapter names
and no file backs — stays informational: character themes, gauntlet
B-sides and finale stingers are unlocked and played by their own
systems, not by chapter context.

    python3 godot/tools/audit/music_coverage_audit.py
    python3 godot/tools/audit/music_coverage_audit.py --all
"""
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
GODOT = os.path.join(ROOT, "godot")
CATALOG = os.path.join(GODOT, "resources", "music_catalog.json")
SCENES = os.path.join(GODOT, "resources", "scenes")

# Scene ids that are placeholders, not chapters — two nodes and a jump.
def is_stub(sid, nodes):
    return sid.endswith("_stub") or nodes <= 2


def scene_ids():
    out = {}
    for vol in sorted(os.listdir(SCENES)):
        vd = os.path.join(SCENES, vol)
        if not os.path.isdir(vd):
            continue
        for fn in sorted(os.listdir(vd)):
            if not fn.endswith(".json") or fn == "index.json":
                continue
            j = json.load(open(os.path.join(vd, fn), encoding="utf-8"))
            out[j.get("id", fn[:-5])] = len(j.get("nodes", []))
    return out


def main():
    show_all = "--all" in sys.argv
    cat = json.loads(open(CATALOG, encoding="utf-8").read())
    scenes = scene_ids()
    named = {}
    for e in cat:
        ids = set(e.get("chapters", []))
        if e.get("chapter_id"):
            ids.add(e["chapter_id"])
        for i in ids:
            named.setdefault(i, []).append(e)

    problems = 0

    # 1 · a chapter with no bed
    for sid in sorted(scenes):
        if is_stub(sid, scenes[sid]) or sid in named:
            continue
        problems += 1
        print("SILENT  %-34s %4d node(s) · no catalog entry names it"
              % (sid, scenes[sid]))

    # 2 · a bed a chapter names that is not on disk
    for e in cat:
        ids = set(e.get("chapters", [])) | (
            {e["chapter_id"]} if e.get("chapter_id") else set())
        hits = sorted(ids & set(scenes))
        if not hits:
            continue
        src = e.get("src", "")
        if src and os.path.exists(os.path.join(GODOT, src)):
            continue
        problems += 1
        print("NOFILE  %-34s %-44s named by %d chapter(s): %s"
              % (e["id"], src or "(no src)", len(hits), ", ".join(hits[:3])))

    # informational
    ghosts = [e for e in cat
              if not (set(e.get("chapters", [])) & set(scenes))
              and not os.path.exists(os.path.join(GODOT, e.get("src", "")))]
    if show_all:
        for e in ghosts:
            print("ghost   %-34s %s" % (e["id"], e.get("src", "")))
    print("\nmusic_coverage_audit · %d scene(s) · %d catalog entr(ies) · "
          "%d unplayed ghost(s) · %d problem(s)"
          % (len(scenes), len(cat), len(ghosts), problems))
    return 1 if problems else 0


if __name__ == "__main__":
    sys.exit(main())
