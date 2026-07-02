#!/usr/bin/env python3
"""Generate a recording manifest for a scene (or set of scenes).

For each voiceable line (narrate, say, think), prints a row showing:
  - the expected audio file path
  - which character (or "_narrator" for narration)
  - the line text

The expected path follows the convention
    assets/audio/voice/<scene_id>/<NNN>.ogg
where NNN is the zero-padded node index in the scene JSON. Drop your
recordings into that path with that exact name and run wire_voicelines.py
to inject "voice" keys into the scene JSON.

Usage:
    python3 tools/voice_manifest.py vol5_ch0_booth6
    python3 tools/voice_manifest.py vol5_ch0_*   # all ch0 scenes
    python3 tools/voice_manifest.py --vol 5 --format csv > vol5.csv
    python3 tools/voice_manifest.py vol5_ch0_booth6 --kind say think

Manifest format (default: human-readable):
    [vol5_ch0_booth6]
    014  say     Stranger    "Watch yourself tonight, brother. The walls are thin."
         file:   assets/audio/voice/vol5_ch0_booth6/014.ogg

CSV format:
    scene_id,node_index,kind,char,file,text
"""

import argparse
import csv
import fnmatch
import json
import sys
from pathlib import Path

SCENES_ROOT = Path(__file__).resolve().parent.parent / "resources" / "scenes"
VOICE_KINDS = ("narrate", "say", "think")


def find_scenes(patterns, vol_filter):
    out = []
    for vol_dir in sorted(SCENES_ROOT.glob("vol*")):
        if vol_filter is not None:
            if vol_dir.name != f"vol{vol_filter}":
                continue
        for path in sorted(vol_dir.glob("vol*.json")):
            scene_id = path.stem
            if patterns and not any(fnmatch.fnmatch(scene_id, p) for p in patterns):
                continue
            out.append(path)
    return out


def voice_path(scene_id, node_index):
    return f"assets/audio/voice/{scene_id}/{node_index:03d}.ogg"


def iter_lines(scene_path, kinds):
    data = json.loads(scene_path.read_text())
    scene_id = data.get("id", scene_path.stem)
    for i, node in enumerate(data.get("nodes", [])):
        t = node.get("t", "")
        if t not in kinds:
            continue
        char = node.get("char", "") or ("_narrator" if t == "narrate" else "")
        text = (node.get("text", "") or "").replace("\n", " ").strip()
        yield {
            "scene_id": scene_id,
            "node_index": i,
            "kind": t,
            "char": char,
            "file": voice_path(scene_id, i),
            "text": text,
        }


def emit_human(scene_path, rows):
    print(f"\n[{scene_path.stem}]  ({len(rows)} lines)")
    for r in rows:
        char_col = r["char"] or "-"
        text = r["text"]
        if len(text) > 70:
            text = text[:67] + "..."
        print(f"  {r['node_index']:>3}  {r['kind']:<7} {char_col:<12} {text}")
        print(f"       file:   {r['file']}")


def emit_csv(writer, rows):
    for r in rows:
        writer.writerow([r["scene_id"], r["node_index"], r["kind"],
                         r["char"], r["file"], r["text"]])


def emit_json(rows, out):
    json.dump(rows, out, indent=2, ensure_ascii=False)
    out.write("\n")


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("patterns", nargs="*",
                    help="Scene id glob(s), e.g. 'vol5_ch0_*'. Empty matches all.")
    ap.add_argument("--vol", type=int,
                    help="Restrict to a single volume number.")
    ap.add_argument("--kind", nargs="+", choices=VOICE_KINDS, default=list(VOICE_KINDS),
                    help="Which line kinds to include. Default: all three.")
    ap.add_argument("--format", choices=("human", "csv", "json"), default="human")
    args = ap.parse_args()

    scenes = find_scenes(args.patterns, args.vol)
    if not scenes:
        print("no scenes matched", file=sys.stderr)
        sys.exit(1)

    if args.format == "csv":
        writer = csv.writer(sys.stdout)
        writer.writerow(["scene_id", "node_index", "kind", "char", "file", "text"])
        for s in scenes:
            emit_csv(writer, list(iter_lines(s, set(args.kind))))
    elif args.format == "json":
        all_rows = []
        for s in scenes:
            all_rows.extend(iter_lines(s, set(args.kind)))
        emit_json(all_rows, sys.stdout)
    else:
        total = 0
        for s in scenes:
            rows = list(iter_lines(s, set(args.kind)))
            if not rows:
                continue
            emit_human(s, rows)
            total += len(rows)
        print(f"\n{total} lines across {len(scenes)} scene(s)", file=sys.stderr)


if __name__ == "__main__":
    main()
