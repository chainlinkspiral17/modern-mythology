#!/usr/bin/env python3
"""locale_ambient_audit.py — the world hum belongs to the room (2026-09-12).

`resources/audio/locale_ambient.json` is the audible layer of every 3D
scene: on locale load the Music Player track ducks to 14% and the
locale's bed rises on the Ambient bus. It mapped 108 locales to ten
vol-5 files — cicadas on Cape Perpetua, the riverboat drone on
Highway 101 — and 42 presets chapters use had no entry at all (BGM at
full there, hum elsewhere: rooms at different loudness for no reason).

Three checks, per preset a scene uses:
  · COVERED  — the map has an entry and the bed file exists;
  · ITS OWN  — the bed is that volume's (vol<N>_ …), or one of the six
    generic room tones, or a same-place cross-volume bed that
    assign_chapter_beds.PLACES declares (the Foxhole is the Foxhole).
    Anything else is another volume's music in the room.

    python3 godot/tools/audit/locale_ambient_audit.py
    python3 godot/tools/audit/locale_ambient_audit.py --all

Gate at zero.
"""
import glob
import json
import os
import re
import sys
from collections import Counter, defaultdict

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
GODOT = os.path.join(ROOT, "godot")
CFG = os.path.join(GODOT, "resources", "audio", "locale_ambient.json")
CATALOG = os.path.join(GODOT, "resources", "music_catalog.json")
SCENES = os.path.join(GODOT, "resources", "scenes")
sys.path.insert(0, os.path.join(ROOT, "godot", "tools", "audio"))

GENERIC = re.compile(r"vol5_(domestic_roomtone|store_ambient|venue_ambient|cafe_ambient|diner_roomtone|cathedral_drone)\.")
VOL_RX = re.compile(r"/vol(\d+)_")


def main():
    show_all = "--all" in sys.argv
    import assign_chapter_beds as A
    cat = {e["id"]: e for e in json.load(open(CATALOG, encoding="utf-8"))}
    loc = json.load(open(CFG, encoding="utf-8")).get("locales", {})
    use = defaultdict(Counter)
    for f in glob.glob(os.path.join(SCENES, "vol*", "*.json")):
        vol = int(os.path.basename(os.path.dirname(f))[3:])
        for n in json.load(open(f, encoding="utf-8")).get("nodes", []):
            if n.get("t") == "bg":
                s = str(n.get("src") or "")
                if s.startswith("3d:"):
                    use[s[3:]][vol] += 1
    problems, checked = [], 0
    for preset, vc in sorted(use.items()):
        vol = vc.most_common(1)[0][0]
        checked += 1
        e = loc.get(preset)
        bed = e.get("bed") if isinstance(e, dict) else None
        if not bed:
            problems.append(("NOHUM", preset, vol, "no entry — this room plays the Music Player at full"))
            continue
        if not os.path.exists(os.path.join(GODOT, bed)):
            problems.append(("NOFILE", preset, vol, bed))
            continue
        m = VOL_RX.search("/" + bed)
        bed_vol = int(m.group(1)) if m else None
        allowed = cat.get(A.PLACES.get(vol, {}).get(preset, ""), {}).get("src")
        if bed_vol == vol or GENERIC.search(bed) or bed == allowed:
            if show_all:
                print("ok      %-28s vol%d %s" % (preset, vol, bed.split("/")[-1]))
            continue
        problems.append(("OTHER", preset, vol, "hum is %s" % bed.split("/")[-1]))
    for kind, preset, vol, why in problems:
        print("%-7s %-28s vol%d  %s" % (kind, preset, vol, why))
    print("\nlocale_ambient_audit · %d preset(s) a chapter uses · %d problem(s)"
          % (checked, len(problems)))
    return 1 if problems else 0


if __name__ == "__main__":
    sys.exit(main())
