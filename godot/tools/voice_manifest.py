#!/usr/bin/env python3
"""Generate a recording manifest (or a coverage report) for scenes.

For each voiceable line (narrate, say, think), prints a row showing:
  - the expected audio file path
  - the character as written in the scene, and the voice_map.json key it
    resolves to (aliases, _walkons, scene_aliases, _chorus applied)
  - the line text

The expected path follows the convention
    assets/audio/voice/<scene_id>/<NNN>.ogg
where NNN is the zero-padded node index in the scene JSON. Drop your
recordings into that path with that exact name and run wire_voicelines.py
to inject "voice" keys into the scene JSON.

Scenes are every resources/scenes/vol*/*.json that has "id" and "nodes"
(so meld_* scenes are included; index.json is skipped). With --vol, scenes
are listed in index.json play order (best for a recording session); pass
--alpha for alphabetical. Without --vol the order is alphabetical per volume
unless --index-order is given.

Usage:
    python3 tools/voice_manifest.py vol5_ch0_booth6
    python3 tools/voice_manifest.py 'vol5_prelude_arcana_*'   # Vol 5 prelude
    python3 tools/voice_manifest.py --vol 1                   # play order
    python3 tools/voice_manifest.py --vol 4 --format csv > vol4.csv
    python3 tools/voice_manifest.py 'meld_*'                  # all meld scenes
    python3 tools/voice_manifest.py vol5_ch0_booth6 --kind say think
    python3 tools/voice_manifest.py --coverage                # every volume
    python3 tools/voice_manifest.py --coverage --vol 1

Manifest format (default: human-readable):
    [vol5_ch0_booth6]
    014  say     Stranger     "Watch yourself tonight, brother. The walls are thin."
         file:   assets/audio/voice/vol5_ch0_booth6/014.ogg

    When the voice_map key differs from the written name it is shown as
    "Name -> key" (e.g. "Faust, Jacob, Wagner -> _chorus").

CSV format:
    scene_id,node_index,kind,char,file,text,voice_key

Coverage (--coverage): per volume, total voiceable lines, lines already
wired (node has a "voice" key), lines with an audio file on disk, and the
voice_map keys that still have no voice_id, sorted by line count
("*" = no entry in voice_map.json at all).
"""

import argparse
import collections
import csv
import json
import sys
import textwrap

import voice_common as vc


def iter_lines(scene_path, kinds, vmap=None, aliases=None):
    data = vc.load_scene(scene_path)
    if data is None:
        return
    scene_id = data.get("id", scene_path.stem)
    vol = vc.scene_vol_number(data, scene_path)
    for i, node in enumerate(data.get("nodes", [])):
        t = node.get("t", "")
        if t not in kinds:
            continue
        text = (node.get("text", "") or "").replace("\n", " ").strip()
        if not text:
            continue
        raw = (node.get("char") or "").strip()
        key = vc.resolve_char(vmap or {}, raw, t, scene_id, aliases, vol)[0]
        char = key if (t == "narrate" or not raw) else raw
        yield {
            "scene_id": scene_id,
            "node_index": i,
            "kind": t,
            "char": char,
            "voice_key": key,
            "file": vc.voice_path(scene_id, i),
            "wired": "voice" in node,
            "text": text,
        }


def emit_human(scene_path, rows):
    print(f"\n[{scene_path.stem}]  ({len(rows)} lines)")
    for r in rows:
        char_col = r["char"]
        if vc.char_key(r["char"]) != r["voice_key"]:
            char_col = f"{r['char']} -> {r['voice_key']}"
        text = r["text"]
        if len(text) > 70:
            text = text[:67] + "..."
        print(f"  {r['node_index']:>3}  {r['kind']:<7} {char_col:<14} {text}")
        print(f"       file:   {r['file']}")


def coverage(scenes, kinds, vmap, aliases):
    """Return {vol: stats} plus an "ALL" roll-up."""
    vols = collections.OrderedDict()
    for path in scenes:
        vol = vc.scene_vol(path)
        st = vols.setdefault(vol, {"scenes": 0, "lines": 0, "wired": 0, "audio": 0,
                                   "chars": collections.Counter()})
        st["scenes"] += 1
        rows = list(iter_lines(path, kinds, vmap, aliases))
        if not rows:
            continue
        on_disk = vc.scan_voice_dir(rows[0]["scene_id"])
        for r in rows:
            st["lines"] += 1
            st["wired"] += r["wired"]
            st["audio"] += r["node_index"] in on_disk
            if not vc.has_own_voice(vmap, r["voice_key"]):
                st["chars"][r["voice_key"]] += 1
    total = {"scenes": 0, "lines": 0, "wired": 0, "audio": 0, "chars": collections.Counter()}
    for st in vols.values():
        for k in ("scenes", "lines", "wired", "audio"):
            total[k] += st[k]
        total["chars"].update(st["chars"])
    if len(vols) > 1:
        vols["ALL"] = total
    return vols


def emit_coverage(vols, vmap, out=sys.stdout):
    known = set(vmap.get("characters", {}))
    hdr = f"{'vol':<6} {'scenes':>6} {'lines':>7} {'wired':>7} {'audio':>7} {'no-voice':>9} {'chars w/o voice':>16}"
    print(hdr, file=out)
    print("-" * len(hdr), file=out)
    for vol, st in vols.items():
        nv = sum(st["chars"].values())
        print(f"{vol:<6} {st['scenes']:>6} {st['lines']:>7} {st['wired']:>7} "
              f"{st['audio']:>7} {nv:>9} {len(st['chars']):>16}", file=out)
    print("\nlines = voiceable narrate/say/think; wired = node has a \"voice\" key; "
          "audio = file on disk;\nno-voice = lines whose voice_map key has no voice_id "
          "(* = key missing from voice_map.json)", file=out)
    for vol, st in vols.items():
        if vol == "ALL" or not st["chars"]:
            continue
        items = [f"{k}{'' if k in known else '*'} {n}" for k, n in st["chars"].most_common()]
        print(f"\n{vol} - characters without a voice_id, by line count:", file=out)
        print(textwrap.fill(", ".join(items), width=96,
                            initial_indent="  ", subsequent_indent="  "), file=out)


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("patterns", nargs="*",
                    help="Scene id glob(s), e.g. 'vol5_ch0_*' or 'meld_*'. Empty matches all.")
    ap.add_argument("--vol", type=int,
                    help="Restrict to a single volume number (implies --index-order).")
    order = ap.add_mutually_exclusive_group()
    order.add_argument("--index-order", dest="index_order", action="store_true", default=None,
                       help="List scenes in index.json play order (default when --vol is given).")
    order.add_argument("--alpha", dest="index_order", action="store_false",
                       help="List scenes alphabetically, even with --vol.")
    ap.add_argument("--kind", nargs="+", choices=vc.VOICE_KINDS, default=list(vc.VOICE_KINDS),
                    help="Which line kinds to include. Default: all three.")
    ap.add_argument("--format", choices=("human", "csv", "json"), default="human")
    ap.add_argument("--coverage", action="store_true",
                    help="Print a per-volume coverage report instead of the manifest.")
    args = ap.parse_args()

    index_order = args.index_order if args.index_order is not None else args.vol is not None
    scenes = vc.find_scenes(args.patterns, args.vol, index_order)
    if not scenes:
        print("no scenes matched", file=sys.stderr)
        sys.exit(1)

    vmap = vc.load_voice_map()
    aliases = vc.alias_table(vmap)
    kinds = set(args.kind)

    if args.coverage:
        vols = coverage(scenes, kinds, vmap, aliases)
        if args.format == "json":
            json.dump({v: dict(st, chars=dict(st["chars"].most_common()))
                       for v, st in vols.items()}, sys.stdout, indent=2)
            sys.stdout.write("\n")
        else:
            emit_coverage(vols, vmap)
        return

    if args.format == "csv":
        writer = csv.writer(sys.stdout)
        writer.writerow(["scene_id", "node_index", "kind", "char", "file", "text", "voice_key"])
        for s in scenes:
            for r in iter_lines(s, kinds, vmap, aliases):
                writer.writerow([r["scene_id"], r["node_index"], r["kind"], r["char"],
                                 r["file"], r["text"], r["voice_key"]])
    elif args.format == "json":
        all_rows = []
        for s in scenes:
            all_rows.extend(iter_lines(s, kinds, vmap, aliases))
        json.dump(all_rows, sys.stdout, indent=2, ensure_ascii=False)
        sys.stdout.write("\n")
    else:
        total = 0
        for s in scenes:
            rows = list(iter_lines(s, kinds, vmap, aliases))
            if not rows:
                continue
            emit_human(s, rows)
            total += len(rows)
        print(f"\n{total} lines across {len(scenes)} scene(s)", file=sys.stderr)


if __name__ == "__main__":
    try:
        main()
    except BrokenPipeError:          # e.g. piped into `head`
        sys.stderr.close()
