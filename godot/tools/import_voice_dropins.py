#!/usr/bin/env python3
"""Voice Studio drop-in zips → the game (2026-10-01).

The user: "I have a good number of zips of voice studio audio in google
drive that can be added to the game project for the visual novel."

Each zip is what tools/voice_studio.html exports:

    assets/audio/voice/<scene_id>/NNN.<mp3|ogg|wav|webm>
    resources/scenes/vol<N>/<scene_id>.json   ← the scene AS IT WAS that day,
                                                 "voice" keys patched in
    README.txt                                 ← "Generated <iso date>"

The zips were recorded June–September; the scenes have been rewritten
since ([shot:] directives, new beats, inserted nodes). Unzipping one over
godot/ would throw those edits away and every NNN after the first
inserted node would point at the wrong line. So this does NOT unzip:

  1. For each voiced node in the zip's own JSON it takes the line's text,
     with directives ([shot:…], [mood:…], …) and punctuation stripped.
  2. It aligns that sequence against the CURRENT scene's voiceable lines
     in order (difflib, exact lines first; then, inside a gap, a rewritten
     line still counts if it is ≥ 90 % the same — reported as "close").
  3. The audio lands at assets/audio/voice/<scene_id>/<current NNN>.<ext>
     and the current JSON gets the "voice" key. webm (browser mic
     recordings — Godot cannot play them) and wav are converted to Ogg
     Vorbis with ffmpeg; mp3 and ogg are copied as they are.
  4. A line SPLIT since recording (its words are exactly 2+ consecutive
     current lines — 480 of the first import's 982 skips) keeps its
     audio: the recording is cut into one Ogg clip per piece, each cut
     where that piece's share of the words ends, snapped to the nearest
     pause. Run with --again to recover splits from zips already imported.
  5. Lines rewritten past recognition (or trimmed) are SKIPPED and listed:
     the audio says words the game no longer shows.

A line that already has a "voice" key keeps it unless --overwrite (the
eight vol5 scenes wired in June). Zips are taken oldest first by their
README date, so when a scene was exported twice the later take wins.
godot/tools/voice_import_state.json remembers every zip already imported
(by md5): re-running after uploading more zips only does the new ones.

    python3 godot/tools/import_voice_dropins.py ZIP_OR_DIR [...]
        --dry-run       show what would happen, write nothing
        --overwrite     replace existing "voice" keys too
        --again         re-import zips already in the state file
        --ffmpeg PATH   (import_voice_dropins.sh passes get_ffmpeg.sh's)

Normally run through godot/tools/import_voice_dropins.sh, which fetches
the zips from Google Drive first and saves the result afterwards.
"""

import argparse
import difflib
import hashlib
import json
import re
import shutil
import subprocess
import sys
import tempfile
import unicodedata
import zipfile
from datetime import datetime, timezone
from pathlib import Path

GODOT = Path(__file__).resolve().parent.parent
SCENES_ROOT = GODOT / "resources" / "scenes"
VOICE_ROOT = GODOT / "assets" / "audio" / "voice"
STATE = GODOT / "tools" / "voice_import_state.json"
REPORT = GODOT / "tools" / "voice_import_report.md"
VOICE_KINDS = {"narrate", "say", "think"}
KEEP_EXTS = {".mp3", ".ogg"}
CONVERT_EXTS = {".webm", ".wav", ".m4a", ".opus", ".flac"}
CLOSE = 0.90

_DIRECTIVE = re.compile(r"\[[a-z_0-9]+(?::[^\]]*)?\]", re.I)
_PUNCT = re.compile(r"[^\w\s]", re.U)


def norm(text):
    """The words of a line: no directives, no punctuation, no case."""
    t = _DIRECTIVE.sub(" ", str(text or ""))
    t = unicodedata.normalize("NFKC", t).replace("’", "'").replace("‘", "'")
    t = t.replace("'", "")
    t = _PUNCT.sub(" ", t.lower())
    return " ".join(t.split())


def voiceable(nodes):
    """[(index, normalized text)] for the narrate/say/think nodes."""
    out = []
    for i, n in enumerate(nodes):
        if isinstance(n, dict) and n.get("t") in VOICE_KINDS:
            out.append((i, norm(n.get("text", ""))))
    return out


def align(old_nodes, new_nodes, wanted):
    """Map each old node index in `wanted` to a current node index.
    Returns ({old: (new, how)}, [old indices with no home])."""
    old = voiceable(old_nodes)
    new = voiceable(new_nodes)
    a = [t for _, t in old]
    b = [t for _, t in new]
    sm = difflib.SequenceMatcher(None, a, b, autojunk=False)
    mapping = {}
    for tag, i1, i2, j1, j2 in sm.get_opcodes():
        if tag == "equal":
            for k in range(i2 - i1):
                mapping[old[i1 + k][0]] = (new[j1 + k][0], "exact")
        elif tag == "replace":
            # rewritten lines inside the gap: best monotonic close match
            j = j1
            for i in range(i1, i2):
                best, best_r = None, CLOSE
                for jj in range(j, j2):
                    r = difflib.SequenceMatcher(None, a[i], b[jj], autojunk=False).ratio()
                    if r >= best_r:
                        best, best_r = jj, r
                if best is not None:
                    mapping[old[i][0]] = (new[best][0], f"close {int(best_r * 100)}%")
                    j = best + 1
    found = {o: mapping[o] for o in wanted if o in mapping}
    lost = [o for o in wanted if o not in mapping]
    return found, lost


def find_splits(old_nodes, new_nodes, lost, taken):
    """Lines SPLIT since recording (2026-10-01: 480 of the first import's
    982 skips): an old line whose words are exactly a run of 2+
    consecutive current lines. Returns {old: [new indices]}; a run that
    touches a line already mapped this zip (`taken`) does not count."""
    old_t = {i: t for i, t in voiceable(old_nodes)}
    new = voiceable(new_nodes)
    out = {}
    for o in lost:
        ot = old_t.get(o, "")
        if not ot:
            continue
        hits = []
        for p in range(len(new)):
            if not ot.startswith(new[p][1]) or not new[p][1]:
                continue
            acc, q = new[p][1], p
            while len(acc) < len(ot) and q + 1 < len(new):
                q += 1
                acc = acc + " " + new[q][1]
            if acc == ot and q > p:
                run = [new[k][0] for k in range(p, q + 1)]
                if not any(r in taken for r in run):
                    hits.append(run)
        if len(hits) == 1:
            out[o] = hits[0]
    return out


def _silences(ff, wav):
    """[(start, end)] of the pauses in a wav, and its duration."""
    r = subprocess.run([ff, "-hide_banner", "-i", str(wav), "-af",
                        "silencedetect=noise=-35dB:d=0.15", "-f", "null", "-"],
                       capture_output=True, text=True)
    err = r.stderr or ""
    starts = [float(x) for x in re.findall(r"silence_start: ([\d.]+)", err)]
    ends = [float(x) for x in re.findall(r"silence_end: ([\d.]+)", err)]
    m = re.findall(r"time=(\d+):(\d+):([\d.]+)", err)
    dur = 0.0
    if m:
        h, mi, se = m[-1]
        dur = int(h) * 3600 + int(mi) * 60 + float(se)
    return list(zip(starts, ends)), dur


def split_audio(ff, src_bytes, src_ext, texts, dsts):
    """Cut one recording into len(texts) Ogg clips, one per piece of a
    split line: each cut where that piece's share of the words ends,
    snapped to the nearest pause (silencedetect) close enough to it."""
    with tempfile.TemporaryDirectory() as td:
        src = Path(td) / ("src" + src_ext)
        src.write_bytes(src_bytes)
        wav = Path(td) / "full.wav"
        r = subprocess.run([ff, "-hide_banner", "-loglevel", "error", "-y", "-i", str(src),
                            "-vn", "-ac", "1", "-ar", "44100", str(wav)], capture_output=True, text=True)
        if r.returncode or not wav.exists():
            raise RuntimeError((r.stderr or "decode failed").strip()[-200:])
        pauses, dur = _silences(ff, wav)
        if dur <= 0.0:
            raise RuntimeError("could not read the recording's length")
        weights = [max(1, len(t)) for t in texts]
        total = float(sum(weights))
        cuts, acc, prev = [], 0.0, 0.0
        for w in weights[:-1]:
            acc += w
            target = dur * acc / total
            window = max(0.8, 0.30 * dur * w / total)
            best = None
            for a, b in pauses:
                mid = (a + b) * 0.5
                if mid <= prev + 0.3 or mid >= dur - 0.3:
                    continue
                if abs(mid - target) <= window and (best is None or abs(mid - target) < abs(best - target)):
                    best = mid
            cut = best if best is not None else target
            cut = max(cut, prev + 0.3)
            cuts.append(cut)
            prev = cut
        bounds = [0.0] + cuts + [dur]
        for k, dst in enumerate(dsts):
            dst.parent.mkdir(parents=True, exist_ok=True)
            r = subprocess.run([ff, "-hide_banner", "-loglevel", "error", "-y", "-i", str(wav),
                                "-ss", "%.3f" % bounds[k], "-to", "%.3f" % bounds[k + 1],
                                "-c:a", "libvorbis", "-q:a", "5", str(dst)], capture_output=True, text=True)
            if r.returncode or not dst.exists() or dst.stat().st_size == 0:
                raise RuntimeError((r.stderr or "cut failed").strip()[-200:])
        return cuts


def md5(path):
    h = hashlib.md5()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def load_state():
    try:
        return json.loads(STATE.read_text())
    except (OSError, ValueError):
        return {"zips": {}}


def dump_like(orig, data):
    """data as JSON in the original file's own style (indent, escaping,
    final newline) — the scenes were written by several tools, and a
    voice key should not reformat a whole file."""
    import itertools
    old = json.loads(orig)
    for ind, ea, nl in itertools.product((2, 1, 4, "\t"), (False, True), ("\n", "")):
        if json.dumps(old, indent=ind, ensure_ascii=ea) + nl == orig:
            return json.dumps(data, indent=ind, ensure_ascii=ea) + nl
    lines = orig.splitlines()
    second = lines[1] if len(lines) > 1 else "  "
    ind = len(second) - len(second.lstrip(" ")) or 2
    return json.dumps(data, indent=ind, ensure_ascii="\\u" in orig) + ("\n" if orig.endswith("\n") else "")


_VOICE_VAL = re.compile(r'("voice"\s*:\s*)"(?:[^"\\]|\\.)*"')


def patch_text(orig, data):
    """The scene file with ONLY its "voice" keys touched: each changed node's
    key is set or inserted in place, in that node's own layout, and the
    rest of the file is left byte for byte. Falls back to dump_like when
    the file cannot be walked (the result must parse back to `data`)."""
    try:
        old = json.loads(orig)
        dec = json.JSONDecoder()
        m = re.search(r'"nodes"\s*:\s*\[', orig)
        if not m:
            raise ValueError("no nodes array")
        spans, pos = [], m.end()
        while True:
            while pos < len(orig) and orig[pos] in " \t\r\n,":
                pos += 1
            if orig[pos] == "]":
                break
            obj, end = dec.raw_decode(orig, pos)
            spans.append((pos, end, obj))
            pos = end
        if [o for _, _, o in spans] != old.get("nodes"):
            raise ValueError("nodes walk does not match the file")
        out = orig
        for i in range(len(spans) - 1, -1, -1):
            s0, e0, o = spans[i]
            want = data["nodes"][i].get("voice") if isinstance(data["nodes"][i], dict) else None
            if not want or (isinstance(o, dict) and o.get("voice") == want):
                continue
            t = out[s0:e0]
            val = json.dumps(want, ensure_ascii=False)
            if "voice" in o:
                t = _VOICE_VAL.sub(lambda mm: mm.group(1) + val, t, count=1)
            else:
                close = t.rstrip().rfind("}")
                p = len(t[:close].rstrip())
                if "\n" in t[:close]:
                    line = t[:p].rsplit("\n", 1)[-1]
                    indent = line[:len(line) - len(line.lstrip())]
                    t = t[:p] + ",\n" + indent + '"voice": ' + val + t[p:]
                else:
                    t = t[:p] + ', "voice": ' + val + t[p:]
            out = out[:s0] + t + out[e0:]
        if json.loads(out) != data:
            raise ValueError("patched text does not parse back to the scene")
        return out
    except (ValueError, IndexError, KeyError, TypeError):
        return dump_like(orig, data)


def scene_path(scene_id):
    hits = sorted(SCENES_ROOT.glob(f"vol*/{scene_id}.json"))
    return hits[0] if hits else None


def read_zip(path):
    """{scene_id, json (dict | None), audio {old_idx: (member, ext)}, generated}"""
    z = zipfile.ZipFile(path)
    audio, scene_json, generated, scene_id = {}, None, "", None
    for m in z.namelist():
        mm = re.match(r"(?:.*/)?assets/audio/voice/([^/]+)/(\d+)\.([A-Za-z0-9]+)$", m)
        if mm:
            scene_id = mm.group(1)
            audio[int(mm.group(2))] = (m, "." + mm.group(3).lower())
        elif re.match(r"(?:.*/)?resources/scenes/[^/]+/[^/]+\.json$", m):
            try:
                scene_json = json.loads(z.read(m).decode("utf-8"))
            except ValueError:
                scene_json = None
        elif m.endswith("README.txt"):
            g = re.search(r"Generated (\S+)", z.read(m).decode("utf-8", "replace"))
            generated = g.group(1) if g else ""
    if scene_json and not scene_id:
        scene_id = scene_json.get("id")
    if scene_json and scene_json.get("id"):
        scene_id = scene_json["id"]
    return {"zip": z, "scene_id": scene_id, "json": scene_json, "audio": audio, "generated": generated}


def convert(ff, src_bytes, src_ext, dst):
    with tempfile.NamedTemporaryFile(suffix=src_ext, delete=False) as tf:
        tf.write(src_bytes)
        tmp = tf.name
    try:
        r = subprocess.run([ff, "-hide_banner", "-loglevel", "error", "-y", "-i", tmp,
                            "-vn", "-c:a", "libvorbis", "-q:a", "5", str(dst)],
                           capture_output=True, text=True)
        if r.returncode or not dst.exists() or dst.stat().st_size == 0:
            raise RuntimeError((r.stderr or "ffmpeg failed").strip()[-200:])
    finally:
        Path(tmp).unlink(missing_ok=True)


def collect(args_paths):
    zips = []
    for a in args_paths:
        p = Path(a).expanduser()
        if p.is_dir():
            zips += [z for z in p.rglob("*.zip") if z.name.startswith("voice_dropin_")]
        elif p.is_file():
            zips.append(p)
    return sorted(set(zips))


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("paths", nargs="+", help="zips, or folders holding voice_dropin_*.zip")
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--overwrite", action="store_true")
    ap.add_argument("--again", action="store_true")
    ap.add_argument("--ffmpeg", default=shutil.which("ffmpeg") or "")
    args = ap.parse_args(argv)

    state = load_state()
    done = state.setdefault("zips", {})
    zips = collect(args.paths)
    if not zips:
        print("no voice_dropin_*.zip found in: " + " ".join(args.paths))
        return 1

    # read every zip, skip the ones already imported (same bytes), oldest first
    todo, seen_md5, skipped_known = [], set(), 0
    for zp in zips:
        h = md5(zp)
        if h in seen_md5:
            continue                       # the same zip twice in the Drive
        seen_md5.add(h)
        if h in done and not args.again:
            skipped_known += 1
            continue
        try:
            info = read_zip(zp)
        except zipfile.BadZipFile:
            print(f"  ! {zp.name}: not a readable zip — skipped")
            continue
        info["path"], info["md5"] = zp, h
        todo.append(info)
    todo.sort(key=lambda x: (x["generated"] or "", x["path"].name))

    report = [f"# Voice import — {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M UTC')}", ""]
    if skipped_known:
        print(f"{skipped_known} zip(s) already imported earlier — skipped (--again redoes them)")
    scenes_changed = {}                   # path → current scene dict
    originals = {}                        # path → the file's text as read
    set_this_run = set()                  # (scene, new idx) wired earlier in this run
    totals = {"wired": 0, "close": 0, "kept": 0, "lost": 0, "zips": 0, "noscene": 0}
    for info in todo:
        sid = info["scene_id"]
        name = info["path"].name
        if not sid or not info["audio"]:
            print(f"  ! {name}: no voice audio inside — skipped")
            report.append(f"- **{name}**: no voice audio inside — skipped")
            continue
        sp = scene_path(sid)
        if sp is None:
            totals["noscene"] += 1
            print(f"  ! {name}: scene {sid} is not in the game any more — skipped")
            report.append(f"- **{name}**: scene `{sid}` not found in resources/scenes — skipped")
            continue
        if sp not in originals:
            originals[sp] = sp.read_text(encoding="utf-8")
        cur = scenes_changed.get(sp) or json.loads(originals[sp])
        nodes = cur.get("nodes", [])
        wanted = sorted(info["audio"])
        if info["json"] and isinstance(info["json"].get("nodes"), list):
            found, lost = align(info["json"]["nodes"], nodes, wanted)
            taken = {n for n, _ in found.values()}
            splits = find_splits(info["json"]["nodes"], nodes, lost, taken)
            lost = [o for o in lost if o not in splits]
        else:
            # an export without its scene snapshot: trust the indices only
            # where the node there is still a voiceable line
            found = {o: (o, "index (zip has no scene JSON)") for o in wanted
                     if o < len(nodes) and isinstance(nodes[o], dict) and nodes[o].get("t") in VOICE_KINDS}
            lost = [o for o in wanted if o not in found]
            splits = {}
        wired = kept = close = nsplit = 0
        lines = []
        for old_i, (new_i, how) in sorted(found.items()):
            member, ext = info["audio"][old_i]
            node = nodes[new_i]
            has = str(node.get("voice", ""))
            if has and not args.overwrite and (sid, new_i) not in set_this_run \
                    and (GODOT / has).exists():
                kept += 1
                continue
            out_ext = ext if ext in KEEP_EXTS else ".ogg"
            if ext not in KEEP_EXTS and ext not in CONVERT_EXTS:
                lines.append(f"  - {old_i:03d}: unknown audio type {ext} — skipped")
                continue
            rel = f"assets/audio/voice/{sid}/{new_i:03d}{out_ext}"
            if not args.dry_run:
                dst = GODOT / rel
                dst.parent.mkdir(parents=True, exist_ok=True)
                data = info["zip"].read(member)
                if out_ext == ext:
                    dst.write_bytes(data)
                else:
                    if not args.ffmpeg:
                        print("  ! ffmpeg is needed for webm/wav — run through import_voice_dropins.sh")
                        return 1
                    try:
                        convert(args.ffmpeg, data, ext, dst)
                    except RuntimeError as ex:
                        lines.append(f"  - {old_i:03d}: could not convert ({ex}) — skipped")
                        continue
                # a sibling NNN.<other ext> from an older take is now stale
                for sib in dst.parent.glob(f"{new_i:03d}.*"):
                    if sib != dst and sib.suffix.lower() in KEEP_EXTS | CONVERT_EXTS:
                        sib.unlink()
            node["voice"] = rel
            set_this_run.add((sid, new_i))
            wired += 1
            if how != "exact":
                close += 1
                lines.append(f"  - {old_i:03d} → {new_i:03d} ({how}): “{str(node.get('text', ''))[:70]}”")
            elif old_i != new_i:
                pass                       # moved but identical: not worth a line
        for old_i, run in sorted(splits.items()):
            member, ext = info["audio"][old_i]
            if not args.overwrite and any(str(nodes[n].get("voice", "")) and (sid, n) not in set_this_run
                                          and (GODOT / str(nodes[n]["voice"])).exists() for n in run):
                kept += 1
                continue
            rels = [f"assets/audio/voice/{sid}/{n:03d}.ogg" for n in run]
            if not args.dry_run:
                if not args.ffmpeg:
                    print("  ! ffmpeg is needed to split a recording — run through import_voice_dropins.sh")
                    return 1
                try:
                    split_audio(args.ffmpeg, info["zip"].read(member), ext,
                                [norm(nodes[n].get("text", "")) for n in run], [GODOT / r for r in rels])
                except RuntimeError as ex:
                    lines.append(f"  - {old_i:03d}: split into {len(run)} lines but could not cut the audio ({ex}) — skipped")
                    continue
                for n, r in zip(run, rels):
                    for sib in (GODOT / r).parent.glob(f"{n:03d}.*"):
                        if sib.name != Path(r).name and sib.suffix.lower() in KEEP_EXTS | CONVERT_EXTS:
                            sib.unlink()
            for n, r in zip(run, rels):
                nodes[n]["voice"] = r
                set_this_run.add((sid, n))
            wired += len(run)
            nsplit += 1
            lines.append(f"  - {old_i:03d} → {', '.join('%03d' % n for n in run)} (one recording cut at its pauses: the line was split)")
        old_nodes = (info["json"] or {}).get("nodes", [])
        for o in lost:
            t = old_nodes[o].get("text", "") if o < len(old_nodes) and isinstance(old_nodes[o], dict) else ""
            lines.append(f"  - {o:03d} SKIPPED, line rewritten since recording: “{str(t)[:70]}”")
        if wired:
            scenes_changed[sp] = cur
        totals["wired"] += wired; totals["close"] += close; totals["kept"] += kept
        totals["lost"] += len(lost); totals["zips"] += 1
        msg = f"{sid}: {wired} line(s) wired"
        if close:
            msg += f" ({close} to a lightly rewritten line)"
        if nsplit:
            msg += f" ({nsplit} recording(s) cut to fit lines split since)"
        if kept:
            msg += f", {kept} already voiced (kept)"
        if lost:
            msg += f", {len(lost)} SKIPPED (line rewritten since recording)"
        print("  " + msg)
        report.append(f"- **{name}** ({info['generated'][:10] or 'undated'}) — {msg}")
        report += lines
        if not args.dry_run:
            done[info["md5"]] = {"zip": name, "scene": sid, "wired": wired, "kept": kept,
                                 "skipped": len(lost), "at": datetime.now(timezone.utc).strftime("%Y-%m-%d")}

    if args.dry_run:
        print("(dry run — nothing written)")
    else:
        for sp, cur in scenes_changed.items():
            sp.write_text(patch_text(originals[sp], cur), encoding="utf-8")
        STATE.write_text(json.dumps(state, indent=1, sort_keys=True) + "\n")
        report += ["", f"**Totals:** {totals['zips']} zip(s), {totals['wired']} line(s) wired "
                   f"({totals['close']} close), {totals['kept']} kept, {totals['lost']} skipped, "
                   f"{totals['noscene']} zip(s) for scenes no longer in the game."]
        REPORT.write_text("\n".join(report) + "\n")
    print(f"VOICE: {totals['wired']} line(s) wired across {len(scenes_changed)} scene(s) from "
          f"{totals['zips']} zip(s); {totals['lost']} skipped (rewritten lines), "
          f"{totals['noscene']} zip(s) for scenes no longer in the game")
    return 0


if __name__ == "__main__":
    sys.exit(main())
