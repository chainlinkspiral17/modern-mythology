#!/usr/bin/env python3
"""browser_storage_scan — read the tools' saved work straight out of the
browsers' own files on disk (2026-10-18).

The user: "all my voice IDs in the voice studio are gone ... Not good
enough." The voice studio kept the cast's voice IDs in localStorage, and a
browser files localStorage under the page's ADDRESS: when Hero Studio moved
from port 8765 to 8877 the studio opened at a new address, empty. The old
address's copy is still in the browser's profile on disk. This reads it
there, with no page, no port and no browser running:

  * Chrome / Chromium / Brave / Edge / Vivaldi / Opera (native and Flatpak):
    `Local Storage/leveldb` — both the write-ahead .log files and the
    compacted .ldb tables (snappy-compressed blocks), every version of
    every key, newest first;
  * Firefox (native and Flatpak): `storage/default/<origin>/ls/data.sqlite`
    (snappy-compressed values) and the older `webappsstore.sqlite`.

Every address the voice studio was ever opened at is found (127.0.0.1 and
localhost, any port, file://). The voice IDs from the newest copy at each
address are merged — the address holding the most IDs wins a conflict —
and written into godot/tools/voice_map.json and voice_ids_backup.json.
These are the IDs the user picked, so they REPLACE IDs a recovery guessed
(voice_recover.py's matches); --keep leaves every ID already saved alone.
The other tools' work kept in the same storage (FORGE user presets, the DX7
bank, Runway presets and queue, Resolve actions, the FM-1 checkout, the
planned-community studio, the DAW inbox, the Meshy queue) is copied to
godot/tools/browser_rescue/, one file per address. Never a key or token.

    python3 godot/tools/browser_storage_scan.py           # find + write
    python3 godot/tools/browser_storage_scan.py --dry-run # find only
    python3 godot/tools/browser_storage_scan.py --keep    # gaps only

The browser may stay open: its files are copied to a temporary folder and
read there. Stdlib only. Report: godot/tools/browser_rescue/SCAN_REPORT.md
"""
import argparse
import json
import os
import re
import shutil
import sqlite3
import struct
import sys
import tempfile
import time
from pathlib import Path

TOOLS = Path(__file__).resolve().parent
RESCUE = TOOLS / "browser_rescue"
sys.path.insert(0, str(TOOLS))

VOICE_KEY = "mm_voice_map"
META_KEY = "mm_voice_meta"
WORK_KEYS = ["mm_forge_user_presets", "mm_dx7_bank", "mm_runway_presets_v1", "mm_runway_queue_v1",
             "mm_resolve_actions_v1", "mm_fm1_checkout", "community_planned_w1_state", "mm_daw_inbox",
             "mm_meshy_queue"]
WANTED = {VOICE_KEY, META_KEY, *WORK_KEYS}


# ── snappy (raw block format; leveldb and Firefox both use it) ──────────────

def _varint(b, i):
    v = s = 0
    while True:
        c = b[i]
        i += 1
        v |= (c & 0x7F) << s
        if c < 0x80:
            return v, i
        s += 7


def snappy(b):
    n, i = _varint(b, 0)
    out = bytearray()
    while i < len(b):
        tag = b[i]
        i += 1
        t = tag & 3
        if t == 0:
            ln = tag >> 2
            if ln >= 60:
                k = ln - 59
                ln = int.from_bytes(b[i:i + k], "little")
                i += k
            ln += 1
            out += b[i:i + ln]
            i += ln
            continue
        if t == 1:
            ln = ((tag >> 2) & 7) + 4
            off = ((tag >> 5) << 8) | b[i]
            i += 1
        elif t == 2:
            ln = (tag >> 2) + 1
            off = int.from_bytes(b[i:i + 2], "little")
            i += 2
        else:
            ln = (tag >> 2) + 1
            off = int.from_bytes(b[i:i + 4], "little")
            i += 4
        if off <= 0 or off > len(out):
            raise ValueError("bad snappy offset")
        for _ in range(ln):
            out.append(out[-off])
    if len(out) != n:
        raise ValueError("bad snappy length")
    return bytes(out)


# ── leveldb (Chromium's Local Storage) ──────────────────────────────────────

def _block_entries(block):
    """(key, value) pairs of one leveldb block."""
    if len(block) < 4:
        return
    nrest = struct.unpack("<I", block[-4:])[0]
    end = len(block) - 4 - 4 * nrest
    i, last = 0, b""
    while 0 <= i < end:
        shared, i = _varint(block, i)
        nonshared, i = _varint(block, i)
        vlen, i = _varint(block, i)
        key = last[:shared] + block[i:i + nonshared]
        i += nonshared
        yield key, block[i:i + vlen]
        i += vlen
        last = key


def _read_block(data, off, size):
    raw = data[off:off + size]
    kind = data[off + size] if off + size < len(data) else 0
    return snappy(raw) if kind == 1 else raw


def ldb_records(path):
    """(user_key, seq, value) from one .ldb table."""
    data = path.read_bytes()
    if len(data) < 48 or data[-8:] != bytes.fromhex("57fb808b247547db"):
        return
    foot = data[-48:]
    _, j = _varint(foot, 0)
    _, j = _varint(foot, j)
    ioff, j = _varint(foot, j)
    isize, j = _varint(foot, j)
    for _, handle in _block_entries(_read_block(data, ioff, isize)):
        boff, k = _varint(handle, 0)
        bsize, k = _varint(handle, k)
        try:
            blk = _read_block(data, boff, bsize)
        except (ValueError, IndexError):
            continue
        for ikey, val in _block_entries(blk):
            if len(ikey) < 8:
                continue
            tail = struct.unpack("<Q", ikey[-8:])[0]
            if tail & 0xFF == 1:                      # a put (0 = deletion)
                yield ikey[:-8], tail >> 8, val


def log_records(path):
    """(user_key, seq, value) from one leveldb .log (write-ahead) file."""
    data = path.read_bytes()
    recs, buf = [], b""
    for bstart in range(0, len(data), 32768):
        blk = data[bstart:bstart + 32768]
        i = 0
        while i + 7 <= len(blk):
            ln, kind = struct.unpack("<H", blk[i + 4:i + 6])[0], blk[i + 6]
            body = blk[i + 7:i + 7 + ln]
            i += 7 + ln
            if kind == 0 and ln == 0:
                break
            if kind == 1:
                recs.append(body)
            elif kind == 2:
                buf = body
            elif kind == 3:
                buf += body
            elif kind == 4:
                recs.append(buf + body)
                buf = b""
    for rec in recs:
        if len(rec) < 12:
            continue
        seq = struct.unpack("<Q", rec[:8])[0]
        count = struct.unpack("<I", rec[8:12])[0]
        i = 12
        try:
            for n in range(count):
                tag = rec[i]
                i += 1
                kl, i = _varint(rec, i)
                key = rec[i:i + kl]
                i += kl
                if tag == 1:
                    vl, i = _varint(rec, i)
                    yield key, seq + n, rec[i:i + vl]
                    i += vl
        except IndexError:
            continue


def _chrome_str(b):
    if not b:
        return ""
    if b[0] == 0:
        return b[1:].decode("utf-16-le", "replace")
    return b[1:].decode("latin-1")


def scan_leveldb(folder):
    """{(origin, key): [(seq, value), ...]} from one Local Storage/leveldb."""
    out = {}
    with tempfile.TemporaryDirectory() as tmp:
        for f in folder.iterdir():
            if f.suffix in (".ldb", ".log", ".sst"):
                shutil.copy2(f, Path(tmp) / f.name)
        for f in sorted(Path(tmp).iterdir()):
            try:
                rows = list(log_records(f) if f.suffix == ".log" else ldb_records(f))
            except Exception:  # noqa: BLE001 — a damaged file must not stop the rest
                continue
            for ukey, seq, val in rows:
                if not ukey.startswith(b"_") or b"\x00" not in ukey:
                    continue
                origin, name = ukey[1:].split(b"\x00", 1)
                key = _chrome_str(name)
                if key in WANTED:
                    out.setdefault((origin.decode("latin-1"), key), []).append((seq, _chrome_str(val)))
    return out


# ── Firefox ─────────────────────────────────────────────────────────────────

def _ff_value(blob, compressed, conversion):
    b = bytes(blob)
    if compressed:
        b = snappy(b)
    if conversion == 1:
        return b.decode("utf-8", "replace")
    try:
        return b.decode("utf-16-le")
    except UnicodeDecodeError:
        return b.decode("utf-8", "replace")


def _sqlite_copy(db, tmp):
    dst = Path(tmp) / db.name
    shutil.copy2(db, dst)
    for ext in ("-wal", "-shm"):
        side = db.with_name(db.name + ext)
        if side.exists():
            shutil.copy2(side, dst.with_name(dst.name + ext))
    return sqlite3.connect(str(dst))


def _ff_origin(folder_name):
    """'http+++127.0.0.1+8765' -> 'http://127.0.0.1:8765'."""
    s = folder_name.split("^", 1)[0]
    m = re.match(r"^(https?|file)\+\+\+(.*)$", s)
    if not m:
        return s
    rest = m.group(2)
    host, _, port = rest.rpartition("+")
    if host and port.isdigit():
        return f"{m.group(1)}://{host}:{port}"
    return f"{m.group(1)}://{rest}"


def scan_firefox_ls(db):
    out = {}
    origin = _ff_origin(db.parent.parent.name)
    with tempfile.TemporaryDirectory() as tmp:
        try:
            con = _sqlite_copy(db, tmp)
            cols = {r[1] for r in con.execute("PRAGMA table_info(data)")}
            q = "SELECT key, value, {}, {}, {} FROM data".format(
                "compression_type" if "compression_type" in cols else "0",
                "conversion_type" if "conversion_type" in cols else "1",
                "last_access_time" if "last_access_time" in cols else "0")
            for key, val, comp, conv, when in con.execute(q):
                if key in WANTED:
                    out.setdefault((origin, key), []).append((int(when or 0), _ff_value(val, comp, conv)))
            con.close()
        except Exception:  # noqa: BLE001
            pass
    return out


def scan_webappsstore(db):
    out = {}
    with tempfile.TemporaryDirectory() as tmp:
        try:
            con = _sqlite_copy(db, tmp)
            for okey, key, val in con.execute("SELECT originKey, key, value FROM webappsstore2"):
                if key not in WANTED:
                    continue
                # originKey: reversed host + ':' + scheme + ':' + port
                parts = (okey or "").split(":")
                host = parts[0][::-1].lstrip(".") if parts else ""
                origin = f"{parts[1]}://{host}:{parts[2]}" if len(parts) >= 3 else okey
                out.setdefault((origin, key), []).append((0, val))
            con.close()
        except Exception:  # noqa: BLE001
            pass
    return out


# ── where the browsers keep it ──────────────────────────────────────────────

def candidate_roots():
    home = Path.home()
    roots = [home / ".config", home / ".mozilla", home / "snap", home / ".var" / "app",
             home / ".local" / "share"]
    return [r for r in roots if r.exists()]


def find_stores(extra=()):
    found = []
    for root in list(candidate_roots()) + [Path(p) for p in extra]:
        for dirpath, dirnames, filenames in os.walk(root, followlinks=False):
            d = Path(dirpath)
            # skip the big caches that never hold storage
            dirnames[:] = [n for n in dirnames if n not in ("Cache", "Code Cache", "GPUCache", "cache2",
                                                             "Service Worker", "IndexedDB", "blob_storage",
                                                             "node_modules", ".git")]
            if d.name == "leveldb" and d.parent.name == "Local Storage":
                found.append(("chromium", d))
            elif d.name == "ls" and "data.sqlite" in filenames and d.parent.parent.name == "default":
                found.append(("firefox", d / "data.sqlite"))
            elif "webappsstore.sqlite" in filenames:
                found.append(("firefox-old", d / "webappsstore.sqlite"))
    return found


def _profile_label(kind, path):
    s = str(path).replace(str(Path.home()), "~")
    for cut in ("/Local Storage/leveldb", "/storage/default/", "/webappsstore.sqlite"):
        if cut in s:
            s = s.split(cut)[0]
    return f"{kind}: {s}"


def _ids_from(value):
    try:
        d = json.loads(value or "{}")
    except ValueError:
        return {}
    if not isinstance(d, dict):
        return {}
    return {str(k): str(v).strip() for k, v in d.items() if isinstance(v, str) and v.strip()}


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--dry-run", action="store_true", help="find and report; write nothing")
    ap.add_argument("--keep", action="store_true", help="never replace an ID already saved (gaps only)")
    ap.add_argument("--root", action="append", default=[], help="another folder to search (a copied profile)")
    args = ap.parse_args()

    stores = find_stores(args.root)
    print(f"browser storage found: {len(stores)} place(s)")
    hits = []            # (profile, origin, key, [(stamp, value)])
    for kind, path in stores:
        if kind == "chromium":
            got = scan_leveldb(path)
        elif kind == "firefox":
            got = scan_firefox_ls(path)
        else:
            got = scan_webappsstore(path)
        for (origin, key), vals in got.items():
            vals.sort(key=lambda r: r[0], reverse=True)
            hits.append((_profile_label(kind, path), origin, key, vals))

    voice = [h for h in hits if h[2] == VOICE_KEY]
    lines = ["# Browser storage scan (" + time.strftime("%Y-%m-%d %H:%M") + ")", "",
             f"{len(stores)} storage place(s) searched; {len(voice)} address(es) hold voice IDs.", ""]
    best = []            # (n_ids, profile, origin, ids, all_versions_union)
    for prof, origin, _, vals in voice:
        newest = {}
        for _, v in vals:                       # newest first: first non-empty copy wins
            newest = _ids_from(v)
            if newest:
                break
        union = {}
        for _, v in reversed(vals):             # oldest first, newer overwrite
            union.update(_ids_from(v))
        best.append((len(newest), prof, origin, newest, union))
        lines.append(f"- **{origin}** in {prof}: newest copy {len(newest)} IDs; {len(vals)} version(s) on disk; "
                     f"{len(union)} keys across all versions")
        print(f"  {origin}  ({prof}): {len(newest)} voice IDs in the newest copy, {len(vals)} version(s)")
    best.sort(key=lambda r: -r[0])

    merged, conflicts = {}, []
    for _, prof, origin, ids, _ in best:
        for k, v in ids.items():
            if k not in merged:
                merged[k] = v
            elif merged[k] != v:
                conflicts.append((k, merged[k], v, origin))
    # keys that only an OLDER version still holds (the newest copy dropped them)
    older = {}
    for _, prof, origin, ids, union in best:
        for k, v in union.items():
            if k not in merged and k not in older:
                older[k] = (v, origin)

    lines += ["", f"## Voice IDs: {len(merged)} from the newest copies", ""]
    for k in sorted(merged):
        lines.append(f"- `{k}`: `{merged[k]}`")
    if conflicts:
        lines += ["", "## Conflicts (the address with the most IDs won)", ""]
        for k, a, b, origin in conflicts:
            lines.append(f"- `{k}`: kept `{a}`; {origin} has `{b}`")
    if older:
        lines += ["", "## Only in older versions (not written: listed so nothing is lost)", ""]
        for k, (v, origin) in sorted(older.items()):
            lines.append(f"- `{k}`: `{v}` ({origin})")

    work = [h for h in hits if h[2] in WORK_KEYS]
    if work:
        lines += ["", "## Other tools' work found", ""]
    if not args.dry_run:
        RESCUE.mkdir(exist_ok=True)
    for prof, origin, key, vals in work:
        safe = re.sub(r"[^A-Za-z0-9]+", "_", origin).strip("_")
        dst = RESCUE / f"{key}__{safe}.json"
        lines.append(f"- `{key}` at {origin} ({prof}) → `{dst.relative_to(TOOLS.parent.parent)}`")
        if not args.dry_run:
            v = vals[0][1]
            try:
                body = json.dumps(json.loads(v), indent=2, ensure_ascii=False)
            except ValueError:
                body = json.dumps(v)
            dst.write_text(body + "\n", encoding="utf-8")
    print(f"voice IDs found: {len(merged)} ({len(conflicts)} conflict(s), {len(older)} only in older versions)")
    print(f"other tools' work found: {len(work)}")

    if not args.dry_run:
        RESCUE.mkdir(exist_ok=True)
        if merged:
            import voice_ids
            res = voice_ids.save_ids(merged, "browser_storage_scan (the browser's own copy)", overwrite=not args.keep)
            lines += ["", f"Written: {res['set'] + res['added']} · already the same or kept: {res['kept']} · "
                          f"refused (not an ID): {len(res['skipped'])}"]
            print(f"written to voice_map.json: {res['set'] + res['added']} · kept {res['kept']}"
                  + (f" · refused {res['skipped']}" if res["skipped"] else ""))
        (RESCUE / "SCAN_REPORT.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
        print(f"report → {(RESCUE / 'SCAN_REPORT.md').relative_to(TOOLS.parent.parent)}")
    if not voice:
        print("No voice IDs in any browser profile found here. If the studio ran in a browser elsewhere "
              "(another machine, a portable browser), copy that profile folder over and pass it with --root.")


if __name__ == "__main__":
    main()
