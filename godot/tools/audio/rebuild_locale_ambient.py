#!/usr/bin/env python3
"""rebuild_locale_ambient.py — the world hum, per place (2026-09-12).

`resources/audio/locale_ambient.json` is THE AUDIBLE LAYER of a 3D
scene: when a locale loads, AudioMgr ducks the Music Player track to
14% and crossfades the locale's bed up on the Ambient bus — "an
inverted ambient soundtrack". The chapter beds assigned on 2026-09-11
therefore play at 14% under whatever this map says.

And what it said was vol 5, everywhere: 108 locales on ten vol-5
files — the cicadas on Cape Perpetua and every New Auburn porch, the
riverboat drone on Highway 101 and the tide pools, D'Ambrosio's dawn
on Meadowlark Circle and in Cosmic Comics, the cathedral drone on
Kestrel. Its own `_doc` says why: "beds reuse the shipped drones + four
bespoke room-tones … any locale can get a bespoke bed later." Forty-
one bespoke beds exist now.

THE RULE, per preset a scene uses:
  1. the PLACE bed from assign_chapter_beds.PLACES (the same table
     the chapters use — a room's hum and a room's music agree);
  2. else keep the map's existing bed IF it is one of the six generic
     room tones (domestic / store / venue / cafe / diner / cathedral)
     — the original author's KIND classification of a room without a
     bespoke bed is worth more than a volume floor;
  3. else the volume floor, `vol<N>_ambient`.
Gains are kept; a new entry takes the map's median gain.

    python3 godot/tools/audio/rebuild_locale_ambient.py --dry
    python3 godot/tools/audio/rebuild_locale_ambient.py
"""
import glob
import json
import os
import statistics
import sys
from collections import Counter, defaultdict

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
ROOT = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
GODOT = os.path.join(ROOT, "godot")
CFG = os.path.join(GODOT, "resources", "audio", "locale_ambient.json")
CATALOG = os.path.join(GODOT, "resources", "music_catalog.json")
SCENES = os.path.join(GODOT, "resources", "scenes")

import assign_chapter_beds as A

GENERIC = {
    "assets/audio/bgm/vol5_domestic_roomtone.wav",
    "assets/audio/bgm/vol5_store_ambient.wav",
    "assets/audio/bgm/vol5_venue_ambient.wav",
    "assets/audio/bgm/vol5_cafe_ambient.wav",
    "assets/audio/bgm/vol5_diner_roomtone.wav",
    "assets/audio/bgm/vol5_cathedral_drone.wav",
}


def preset_volumes():
    use = defaultdict(Counter)
    for f in glob.glob(os.path.join(SCENES, "vol*", "*.json")):
        vol = int(os.path.basename(os.path.dirname(f))[3:])
        for n in json.load(open(f, encoding="utf-8")).get("nodes", []):
            if n.get("t") == "bg":
                s = str(n.get("src") or "")
                if s.startswith("3d:"):
                    use[s[3:]][vol] += 1
    return {p: c.most_common(1)[0][0] for p, c in use.items()}


def main():
    dry = "--dry" in sys.argv
    cfg = json.load(open(CFG, encoding="utf-8"))
    loc = cfg["locales"]
    cat = {e["id"]: e for e in json.load(open(CATALOG, encoding="utf-8"))}
    gains = [float(v.get("gain", 0.9)) for v in loc.values() if isinstance(v, dict)]
    default_gain = round(statistics.median(gains), 2) if gains else 0.9

    def src_of(tid):
        e = cat.get(tid)
        if e and os.path.exists(os.path.join(GODOT, e.get("src", ""))):
            return e["src"]
        return None

    kept = repointed = added = 0
    for preset, vol in sorted(preset_volumes().items()):
        cur = loc.get(preset) if isinstance(loc.get(preset), dict) else None
        cur_bed = cur.get("bed") if cur else None
        want = src_of(A.PLACES.get(vol, {}).get(preset, ""))
        why = "place"
        if want is None and cur_bed in GENERIC:
            want, why = cur_bed, "kind"
        if want is None:
            want, why = src_of("vol%d_ambient" % vol), "floor"
        if want is None:
            continue
        if cur_bed == want:
            kept += 1
            continue
        if cur is None:
            added += 1
            loc[preset] = {"bed": want, "gain": default_gain}
        else:
            repointed += 1
            cur["bed"] = want
        print("  %-6s vol%d %-28s %s → %s"
              % (why, vol, preset, (cur_bed or "(none)").split("/")[-1], want.split("/")[-1]))
    print("\nlocale_ambient · %d kept · %d re-pointed · %d added%s"
          % (kept, repointed, added, " (dry)" if dry else ""))
    if not dry:
        cfg["_doc"] = cfg["_doc"].rstrip() + (
            " REBUILT 2026-09-12 by tools/audio/rebuild_locale_ambient.py: "
            "a locale takes its PLACE bed (assign_chapter_beds.PLACES), else "
            "its existing generic room tone, else its volume floor.")
        out = json.dumps(cfg, indent=2, ensure_ascii=False) + "\n"
        json.loads(out)
        with open(CFG, "w", encoding="utf-8") as f:
            f.write(out)


if __name__ == "__main__":
    main()
