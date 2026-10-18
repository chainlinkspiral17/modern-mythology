#!/usr/bin/env python3
"""voice_id_hunt — find the cast's voice IDs ANYWHERE on this machine
(2026-10-18).

browser_storage_scan.py found no live copy of the voice studio's map in 50
browser storage places. This looks everywhere else, by content instead of by
place: every ElevenLabs voice ID is a distinctive 20-character string, and
the workspace's 116 voices are known (godot/tools/voice_recovery/
workspace_voices.json). Every file under the home folder and any SD card is
searched for those strings (plain, UTF-16, and inside snappy-compressed
browser blocks: Chromium .ldb tables, Firefox data.sqlite values, deleted
rows left in a database's free pages, write-ahead logs), and for any
`"<character key>":"<20-char id>"` pair. Each hit is reported with the
character key written just before it, so a voice map that survives in an
old export, a stale browser profile, a backup or a cache comes back whole.

    python3 godot/tools/voice_id_hunt.py             # search + report
    python3 godot/tools/voice_id_hunt.py --apply     # also write the pairs

Report: godot/tools/voice_recovery/HUNT_REPORT.md (+ hunt.json). --apply
writes every character whose pairs agree (one ID) into voice_map.json —
these are the user's own picks, so they replace recording-match guesses.
Media, games and the repo's own working files are skipped. Stdlib only.
"""
import argparse
import collections
import json
import os
import re
import sqlite3
import sys
import tempfile
import time
import shutil
from pathlib import Path

TOOLS = Path(__file__).resolve().parent
REPO = TOOLS.parent.parent
OUT = TOOLS / "voice_recovery"
sys.path.insert(0, str(TOOLS))
import browser_storage_scan as bss  # noqa: E402  (snappy + leveldb readers)

SKIP_EXT = {".mp3", ".ogg", ".wav", ".flac", ".webm", ".mp4", ".mkv", ".mov", ".avi", ".png", ".jpg", ".jpeg",
            ".webp", ".gif", ".glb", ".gltf", ".blend", ".blend1", ".fbx", ".obj", ".exr", ".hdr", ".ktx",
            ".ctex", ".scn", ".res", ".pck", ".so", ".dll", ".exe", ".a", ".o", ".iso", ".img", ".vpk",
            ".ttf", ".otf", ".woff", ".woff2", ".pdf", ".psd", ".kra", ".zst", ".xz", ".gz", ".bz2", ".7z",
            ".rar", ".deb", ".rpm", ".appimage", ".flatpak", ".wasm", ".pyc", ".jar", ".class"}
SKIP_DIRS = {"steamapps", "Steam", "compatdata", "shadercache", ".cache", "Cache", "Code Cache", "GPUCache",
             "cache2", "node_modules", ".git", "__pycache__", ".godot", ".import", "proc", "sys",
             "flatpak", "ostree", "pw-browsers", "site-packages", "dist-packages"}
MAX_BYTES = 64 << 20


def known_ids():
    try:
        vs = json.loads((OUT / "workspace_voices.json").read_text(encoding="utf-8"))
    except (OSError, ValueError):
        vs = []
    return {v["voice_id"]: (v.get("name") or "").strip() for v in vs if v.get("voice_id")}


def known_keys():
    keys = set()
    try:
        m = json.loads((TOOLS / "voice_map.json").read_text(encoding="utf-8"))
        keys |= set((m.get("characters") or {}).keys())
        keys |= {str(v) for v in (m.get("aliases") or {}).values() if isinstance(v, str)}
    except (OSError, ValueError):
        pass
    try:
        keys |= set(json.loads((OUT / "matches.json").read_text(encoding="utf-8")).get("tiers", {}).keys())
    except (OSError, ValueError):
        pass
    return keys


def roots(extra):
    rs = [Path.home()]
    for media in (Path("/run/media"), Path("/media"), Path("/mnt")):
        if media.exists():
            rs.append(media)
    return rs + [Path(p) for p in extra]


def walk(rs):
    skip_tree = {REPO / "godot", REPO / "lore", REPO / ".git"}
    for r in rs:
        for dirpath, dirnames, filenames in os.walk(r, followlinks=False):
            d = Path(dirpath)
            if d in skip_tree:
                dirnames[:] = []
                continue
            dirnames[:] = [n for n in dirnames if n not in SKIP_DIRS]
            for fn in filenames:
                p = d / fn
                if p.suffix.lower() in SKIP_EXT:
                    continue
                try:
                    st = p.stat()
                except OSError:
                    continue
                if 0 < st.st_size <= MAX_BYTES and p.is_file():
                    yield p


def blobs(p, data):
    """The file's bytes, plus every decompressed browser block it holds."""
    yield "raw", data
    try:
        if p.suffix in (".ldb", ".sst") and data[-8:] == bytes.fromhex("57fb808b247547db"):
            foot = data[-48:]
            _, j = bss._varint(foot, 0)
            _, j = bss._varint(foot, j)
            ioff, j = bss._varint(foot, j)
            isize, j = bss._varint(foot, j)
            for _, handle in bss._block_entries(bss._read_block(data, ioff, isize)):
                boff, k = bss._varint(handle, 0)
                bsize, k = bss._varint(handle, k)
                try:
                    yield "leveldb block", bss._read_block(data, boff, bsize)
                except (ValueError, IndexError):
                    pass
        elif data[:16] == b"SQLite format 3\x00":
            with tempfile.TemporaryDirectory() as tmp:
                con = bss._sqlite_copy(p, tmp)
                tables = [r[0] for r in con.execute("SELECT name FROM sqlite_master WHERE type='table'")]
                for t in tables:
                    cols = [r[1] for r in con.execute(f'PRAGMA table_info("{t}")')]
                    for c in cols:
                        try:
                            for (v,) in con.execute(f'SELECT "{c}" FROM "{t}"'):
                                if isinstance(v, bytes) and len(v) > 8:
                                    try:
                                        yield f"sqlite {t}.{c} (snappy)", bss.snappy(v)
                                    except (ValueError, IndexError):
                                        pass
                        except sqlite3.Error:
                            pass
                con.close()
    except Exception:  # noqa: BLE001 — a file we cannot parse is still searched raw
        return


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--apply", action="store_true", help="write characters whose pairs agree")
    ap.add_argument("--root", action="append", default=[], help="another folder or drive to search")
    args = ap.parse_args()
    ids = known_ids()
    keys = known_keys()
    if not ids:
        print("(no workspace voice list yet: searching by character-key pairs only)")
    id_re = re.compile(b"|".join(re.escape(i.encode()) for i in sorted(ids))) if ids else None
    id16_re = re.compile(b"|".join(re.escape(i.encode("utf-16-le")) for i in sorted(ids))) if ids else None
    pair_re = re.compile(rb'"([a-z][a-z0-9_]{1,40})"\s*:\s*"([A-Za-z0-9]{20})"')
    key_before = re.compile(r'"([a-z_][a-z0-9_]{1,40})"\s*:\s*"?\s*$')

    pairs = collections.defaultdict(lambda: collections.Counter())    # key -> {id: n}
    where = collections.defaultdict(set)                               # (key,id) -> files
    id_hits = collections.Counter()
    files_with = collections.Counter()
    n_files, t0 = 0, time.time()
    for p in walk(roots(args.root)):
        n_files += 1
        if n_files % 5000 == 0:
            print(f"  … {n_files} files searched ({int(time.time() - t0)} s)", flush=True)
        try:
            data = p.read_bytes()
        except OSError:
            continue
        if not (id_re and (id_re.search(data) or id16_re.search(data))) and not pair_re.search(data) \
                and not (p.suffix in (".ldb", ".sst", ".sqlite", ".db") or data[:16] == b"SQLite format 3\x00"):
            continue
        label = str(p).replace(str(Path.home()), "~")
        for how, blob in blobs(p, data):
            texts = [blob]
            if id16_re and id16_re.search(blob):
                texts.append(blob.decode("utf-16-le", "ignore").encode("latin-1", "ignore"))
            for b in texts:
                for m in pair_re.finditer(b):
                    k, v = m.group(1).decode(), m.group(2).decode()
                    if k in keys:
                        pairs[k][v] += 1
                        where[(k, v)].add(f"{label} [{how}]")
                if id_re:
                    for m in id_re.finditer(b):
                        v = m.group(0).decode()
                        id_hits[v] += 1
                        files_with[label] += 1
                        ctx = b[max(0, m.start() - 60):m.start()].decode("latin-1", "replace")
                        km = key_before.search(ctx)
                        if km and km.group(1) in keys:
                            pairs[km.group(1)][v] += 1
                            where[(km.group(1), v)].add(f"{label} [{how}]")
    print(f"searched {n_files} files in {int(time.time() - t0)} s")

    OUT.mkdir(exist_ok=True)
    agreed = {k: c.most_common(1)[0][0] for k, c in pairs.items() if len(c) == 1}
    split = {k: c for k, c in pairs.items() if len(c) > 1}
    L = ["# Voice ID hunt (" + time.strftime("%Y-%m-%d %H:%M") + ")", "",
         f"{n_files} files searched for the workspace's {len(ids)} voice IDs and for character → ID pairs.", "",
         f"- characters found with one ID: **{len(agreed)}**",
         f"- characters found with several IDs (a recast; most-seen listed first): {len(split)}",
         f"- workspace IDs seen anywhere: {len(id_hits)}", ""]
    if agreed or split:
        L += ["## Pairs found", "", "| character | voice | seen | where |", "|---|---|---|---|"]
        for k in sorted(pairs):
            for v, n in pairs[k].most_common():
                w = sorted(where[(k, v)])
                L.append(f"| `{k}` | {ids.get(v, '?')} `{v}` | {n} | {'; '.join(w[:3])}{' …' if len(w) > 3 else ''} |")
    if files_with:
        L += ["", "## Files holding workspace voice IDs", ""]
        for f, n in files_with.most_common(40):
            L.append(f"- {f}: {n}")
    (OUT / "HUNT_REPORT.md").write_text("\n".join(L) + "\n", encoding="utf-8")
    (OUT / "hunt.json").write_text(json.dumps({"pairs": {k: dict(c) for k, c in pairs.items()},
                                               "files": dict(files_with)}, indent=1) + "\n", encoding="utf-8")
    print(f"characters found: {len(agreed)} with one ID, {len(split)} with several · "
          f"files holding workspace IDs: {len(files_with)}")
    print(f"report → {(OUT / 'HUNT_REPORT.md').relative_to(REPO)}")
    if args.apply and pairs:
        import voice_ids
        res = voice_ids.save_ids(agreed, "voice_id_hunt (found on disk)", overwrite=True)
        print(f"written to voice_map.json: {res['set'] + res['added']}")


if __name__ == "__main__":
    main()
