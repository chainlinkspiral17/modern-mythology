#!/usr/bin/env python3
"""Register every slowstick BGM wav in music_catalog.json.

'For the time being, let's just put all the music in the music
player.' Walks assets/audio/bgm/<stick>/*.wav and appends a catalog
entry for each track that isn't already registered, grouped under a
per-stick `section` label (MusicPlayerOverlay renders `section` as
the group header when present, instead of VOL. N).

Entries are always-unlocked (empty unlock clause) and carry vol=99
so unlock_volume(n) never mass-enqueues them. Idempotent: reruns
skip existing ids.

Run from repo root: python3 godot/tools/audio/add_stick_tracks_to_catalog.py
"""
import json, os, glob, re

ROOT = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".."))
CATALOG = os.path.join(ROOT, "resources", "music_catalog.json")

STICKS = [
    ("shelf", "THE CABIN SHELF"),
    ("e1",    "ESTUARY 1"),
    ("e2",    "ESTUARY 2"),
    ("e3",    "ESTUARY 3"),
    ("sss",   "SAM'S SUMMER SHIFTS"),
    ("ksm",   "KWIK STOP MANAGER"),
    ("nh",    "NORTHWIND HARBOR"),
    ("ps",    "PIRATE SUMMER"),
    ("sg",    "SWEETGUM"),
    ("pmg",   "PATIENT MISTER GLASS"),
    ("hnn",   "HANE NO NIWA"),
    ("em",    "EARTHMAN CHRONICLES"),
    ("ff",    "FEY FAIRE"),
    ("sw",    "SISTERS WYRD"),
]


def prettify(basename):
    t = basename.replace("_", " ").strip()
    t = re.sub(r"\bact(\d)\b", r"act \1", t)
    t = re.sub(r"\bmix ([a-z]+)\b", lambda m: "mix " + m.group(1).upper(), t)
    return t.title().replace("Mix ", "Mix ")


def main():
    with open(CATALOG) as f:
        catalog = json.load(f)
    have = {e.get("id") for e in catalog}
    added = 0
    for stick, label in STICKS:
        wavs = sorted(glob.glob(os.path.join(ROOT, "assets", "audio", "bgm", stick, "*.wav")))
        for w in wavs:
            base = os.path.splitext(os.path.basename(w))[0]
            tid = "slow_%s_%s" % (stick, base)
            if tid in have:
                continue
            catalog.append({
                "id": tid,
                "vol": 99,
                "section": "SLOWSTICK · " + label,
                "title": prettify(base),
                "src": "assets/audio/bgm/%s/%s.wav" % (stick, base),
                "composer": "—",
                "desc": "%s — %s." % (label.title(), prettify(base)),
                "unlock": {},
            })
            have.add(tid)
            added += 1
    with open(CATALOG, "w") as f:
        json.dump(catalog, f, indent=1, ensure_ascii=False)
        f.write("\n")
    print("added %d stick tracks · catalog now %d entries" % (added, len(catalog)))


if __name__ == "__main__":
    main()
