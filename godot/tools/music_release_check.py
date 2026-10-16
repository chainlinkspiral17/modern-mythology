#!/usr/bin/env python3
"""Third-party temps before a release: list them, or strip them from the game folder.

The AUDIO DIRECTOR's REMIX can make temp tracks out of imported audio (covers, samples) for sketching. Every take
made from an import that wasn't marked as cleared (yours / public domain / licensed) carries "third_party" in its
meta, its approval record (resources/music/temp_approvals.json) and the approved temp's manifest
(<base>.stems.json). A release build never plays them (AudioMgr._third_party_blocked), but they should not ship:

    python3 godot/tools/music_release_check.py            # list them; exit 1 if any are in the game folder
    python3 godot/tools/music_release_check.py --strip    # remove those temps (.temp.ogg, .stems/, .stems.json, credits)
    python3 godot/tools/music_release_check.py --json     # the list as JSON

Only temp files are ever removed — a real recording at the catalog path is never touched. The approval record
stays (it is the director's file; the AUDIO DIRECTOR then shows the track as missing its temp). Back the music up
first (godot/tools/music_drive.sh push) if you might want the sketches again.
"""
import argparse
import json
import os
import shutil
import sys

GODOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def load_json(rel, default):
    try:
        with open(os.path.join(GODOT, rel), encoding="utf-8") as f:
            return json.load(f)
    except (OSError, ValueError):
        return default


def find(godot=GODOT):
    """Every third-party temp in the game folder: [{id, base, files, third_party, source}]"""
    out, seen = [], set()
    # 1) the manifests on disk — what the game would actually load
    audio = os.path.join(godot, "assets", "audio")
    for root, dirs, files in os.walk(audio):
        dirs[:] = [d for d in dirs if d not in ("review", "library", "projects", "replaced", "imports")]
        for f in files:
            if not f.endswith(".stems.json"):
                continue
            path = os.path.join(root, f)
            try:
                man = json.load(open(path, encoding="utf-8"))
            except (OSError, ValueError):
                continue
            if not isinstance(man, dict) or not man.get("third_party"):
                continue
            base = os.path.relpath(path, godot)[: -len(".stems.json")]
            seen.add(base)
            out.append({"base": base, "third_party": man["third_party"], "source": "manifest", "files": temp_files(godot, base)})
    # 2) approvals that say so, in case a manifest went missing
    ap = load_json(os.path.join("resources", "music", "temp_approvals.json"), {"tracks": {}})
    cat = load_json(os.path.join("resources", "music_catalog.json"), [])
    srcs = {t.get("id"): t.get("src", "") for t in (cat if isinstance(cat, list) else cat.get("tracks", []))}
    for tid, rec in (ap.get("tracks") or {}).items():
        a = (rec or {}).get("approved") or {}
        if not a.get("third_party") or not srcs.get(tid):
            continue
        base = os.path.splitext(srcs[tid])[0]
        if base in seen:
            for e in out:
                if e["base"] == base:
                    e["id"] = tid
            continue
        files = temp_files(godot, base)
        if files:
            out.append({"id": tid, "base": base, "third_party": a["third_party"], "source": "approval", "files": files})
    return out


def temp_files(godot, base):
    """the temp's own files (never the real recording at the catalog path)"""
    cand = [base + ".temp.ogg", base + ".temp.ogg.credits.txt", base + ".stems.json", base + ".stems"]
    return [c for c in cand if os.path.exists(os.path.join(godot, c))]


def strip(entries, godot=GODOT):
    gone = []
    for e in entries:
        for rel in e["files"]:
            p = os.path.join(godot, rel)
            if os.path.isdir(p):
                shutil.rmtree(p)
            elif os.path.exists(p):
                os.remove(p)
            gone.append(rel)
    return gone


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--strip", action="store_true", help="remove the third-party temps from the game folder")
    ap.add_argument("--json", action="store_true", help="print the list as JSON")
    ap.add_argument("--godot", default=GODOT, help=argparse.SUPPRESS)
    a = ap.parse_args(argv)
    entries = find(a.godot)
    if a.json:
        print(json.dumps(entries, indent=1))
    elif not entries:
        print("no third-party temps in the game folder — clear to export.")
    else:
        print("%d third-party temp(s) (covers / samples of imported audio — sketches, not for release):" % len(entries))
        for e in entries:
            tp = e["third_party"] if isinstance(e["third_party"], dict) else {}
            print("  %-40s %-7s from %s" % (e.get("id") or e["base"], tp.get("kind", "?"), tp.get("source", "?")))
    if a.strip and entries:
        gone = strip(entries, a.godot)
        print("stripped %d file(s)/folder(s). The approvals stay; the director shows those tracks as missing a temp." % len(gone))
        return 0
    return 1 if entries and not a.json else 0


if __name__ == "__main__":
    sys.exit(main())
