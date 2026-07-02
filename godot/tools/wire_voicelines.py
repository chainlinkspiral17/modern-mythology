#!/usr/bin/env python3
"""Inject "voice" keys into scene JSONs based on files present on disk.

For each scene under resources/scenes/, scan
    assets/audio/voice/<scene_id>/<NNN>.<ext>
where NNN is the zero-padded node index and ext is one of ogg/mp3/wav.
For every match where the target node is narrate/say/think, add a
"voice" key pointing at that file. Existing "voice" keys are
preserved unless --overwrite is passed.

Usage:
    python3 tools/wire_voicelines.py                       # all scenes
    python3 tools/wire_voicelines.py vol5_ch0_*            # glob
    python3 tools/wire_voicelines.py --vol 5
    python3 tools/wire_voicelines.py --dry-run             # show diff, write nothing
    python3 tools/wire_voicelines.py --overwrite           # replace existing voice keys

Reports per-scene how many lines got wired, how many recordings on
disk had no matching voiceable node (warnings), and how many existing
"voice" keys were left untouched / overwritten.
"""

import argparse
import fnmatch
import json
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
SCENES_ROOT = REPO / "resources" / "scenes"
VOICE_ROOT = REPO / "assets" / "audio" / "voice"
VOICE_KINDS = {"narrate", "say", "think"}
EXTS = (".ogg", ".mp3", ".wav")


def find_scene_paths(patterns, vol_filter):
    out = []
    for vol_dir in sorted(SCENES_ROOT.glob("vol*")):
        if vol_filter is not None and vol_dir.name != f"vol{vol_filter}":
            continue
        for path in sorted(vol_dir.glob("vol*.json")):
            if patterns and not any(fnmatch.fnmatch(path.stem, p) for p in patterns):
                continue
            out.append(path)
    return out


def scan_voice_dir(scene_id):
    """Return {node_index: rel_src_path} for files matching NNN.<ext>."""
    d = VOICE_ROOT / scene_id
    out = {}
    if not d.exists():
        return out
    for f in d.iterdir():
        if f.suffix.lower() not in EXTS:
            continue
        stem = f.stem
        if not stem.isdigit():
            continue
        idx = int(stem)
        # Stable preference order: keep the first ext we see per index
        # (ogg > mp3 > wav so authoring overrides defaults).
        existing = out.get(idx)
        if existing and EXTS.index(f.suffix.lower()) > EXTS.index(Path(existing).suffix.lower()):
            continue
        out[idx] = f.relative_to(REPO).as_posix()
    return out


def wire_scene(path, dry_run, overwrite):
    data = json.loads(path.read_text())
    scene_id = data.get("id", path.stem)
    nodes = data.get("nodes", [])
    files = scan_voice_dir(scene_id)
    stats = {"added": 0, "kept": 0, "replaced": 0, "skipped_kind": 0,
             "missing_node": [], "files_seen": len(files)}

    for idx, src in sorted(files.items()):
        if idx >= len(nodes):
            stats["missing_node"].append((idx, src))
            continue
        node = nodes[idx]
        if node.get("t") not in VOICE_KINDS:
            stats["skipped_kind"] += 1
            continue
        if "voice" in node and not overwrite:
            stats["kept"] += 1
            continue
        if "voice" in node:
            stats["replaced"] += 1
        else:
            stats["added"] += 1
        node["voice"] = src

    if not dry_run and (stats["added"] or stats["replaced"]):
        path.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n")
    return stats


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("patterns", nargs="*",
                    help="Scene id glob(s), e.g. 'vol5_ch0_*'. Empty matches all.")
    ap.add_argument("--vol", type=int, help="Restrict to one volume number.")
    ap.add_argument("--dry-run", action="store_true",
                    help="Report planned changes without writing.")
    ap.add_argument("--overwrite", action="store_true",
                    help="Replace existing voice keys instead of keeping them.")
    args = ap.parse_args()

    scenes = find_scene_paths(args.patterns, args.vol)
    if not scenes:
        print("no scenes matched", file=sys.stderr)
        sys.exit(1)

    total = {"added": 0, "kept": 0, "replaced": 0, "skipped_kind": 0,
             "files_seen": 0, "scenes_touched": 0, "warnings": 0}

    for path in scenes:
        s = wire_scene(path, args.dry_run, args.overwrite)
        if s["files_seen"] == 0 and s["kept"] == 0:
            continue
        total["files_seen"] += s["files_seen"]
        total["scenes_touched"] += 1
        for k in ("added", "kept", "replaced", "skipped_kind"):
            total[k] += s[k]
        action = "would write" if args.dry_run else "wrote"
        verb = action if (s["added"] or s["replaced"]) else "unchanged"
        print(f"{path.stem:<32}  files={s['files_seen']:>3}  "
              f"added={s['added']:>3}  kept={s['kept']:>3}  "
              f"replaced={s['replaced']:>3}  skipped_kind={s['skipped_kind']:>2}  "
              f"[{verb}]")
        for idx, src in s["missing_node"]:
            print(f"  WARN: {src} -> node index {idx} doesn't exist in scene "
                  f"(scene has {len(json.loads(path.read_text()).get('nodes', []))} nodes)")
            total["warnings"] += 1

    print(file=sys.stderr)
    print(f"summary: {total['files_seen']} files, "
          f"{total['scenes_touched']} scenes touched, "
          f"added={total['added']} kept={total['kept']} "
          f"replaced={total['replaced']} skipped_kind={total['skipped_kind']} "
          f"warnings={total['warnings']}",
          file=sys.stderr)


if __name__ == "__main__":
    main()
