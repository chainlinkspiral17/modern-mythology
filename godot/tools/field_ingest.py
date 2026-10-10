#!/usr/bin/env python3
"""
field_ingest.py — bring field recordings into the game.

Works with WAVs from a hardware recorder's SD card (Zoom, Tascam,
Sound Devices… — BWF/iXML metadata is read), and with the WAV + JSON
pairs FIELD RECORDER / TAPE STUDIO download when no game folder is
linked. No third-party packages; ffmpeg is used only if you ask for
--convert and it is installed.

  python3 godot/tools/field_ingest.py wanted              # catalog tracks with no audio yet
  python3 godot/tools/field_ingest.py scan /run/media/deck/ZOOM/
  python3 godot/tools/field_ingest.py ingest /run/media/deck/ZOOM/ --locale riverfront --tag water
  python3 godot/tools/field_ingest.py ingest ~/Downloads             # browser downloads (+ .json sidecars)
  python3 godot/tools/field_ingest.py fill vol7_marina_morning take.wav

What lands where:
  ingest → godot/assets/audio/field/<locale>/<name>.wav (+ .json sidecar)
           and a row in godot/resources/field_recordings.json
  fill   → the catalog track's own path with a .wav extension, e.g.
           assets/audio/bgm/vol7_marina_morning.wav — AudioMgr plays it
           in place of the missing .ogg / .mp3 (see _load_audio).
           --convert writes the real .ogg / .mp3 with ffmpeg instead.

Copies are 16-bit PCM by default (32-bit float and 24-bit recorder
files are converted with TPDF dither) — smaller, and every Godot
build loads them. --keep-bits keeps the original.
"""

import argparse
import array
import hashlib
import json
import random
import re
import shutil
import struct
import subprocess
import sys
from datetime import datetime
from pathlib import Path

GODOT = Path(__file__).resolve().parent.parent
CATALOG = GODOT / "resources" / "music_catalog.json"
FIELD_CATALOG = GODOT / "resources" / "field_recordings.json"
FIELD_DIR = GODOT / "assets" / "audio" / "field"

FIELD_YES = ["rain", "wind", "cicada", "storm", "thunder", "halyard", "gull", "creak", "hum", "room", "stove", "woodstove",
             "traffic", "crowd", "kitchen", "dock", "tide", "water", "insect", "bird", "fan", "fridge", "static", "radio", "marina",
             "rest stop", "diner", "bar", "night shift", "porch", "field", "substation", "interior", "ambient", "drone", "wash", "surf",
             "frog", "crickets", "bell", "clock", "tap", "faucet", "engine", "boat", "train", "hospital", "office", "warehouse", "shop"]
FIELD_NO = ["theme", "credits", "hymn", "strings", "chord", "band", "song", "stinger", "melody", "piano", "guitar", "choir", "title"]


# ── WAV reading ──────────────────────────────────────────────────────
class Wav:
    """Minimal RIFF/WAVE reader: fmt, data, bext, iXML, LIST/INFO, smpl, mmjs."""

    def __init__(self, path: Path):
        self.path = path
        b = path.read_bytes()
        if len(b) < 12 or b[:4] not in (b"RIFF", b"RF64") or b[8:12] != b"WAVE":
            raise ValueError("not a WAV file")
        if b[:4] == b"RF64":
            raise ValueError("RF64 (>4 GB) files are not supported — split the take on the recorder")
        self.raw = b
        self.chunks = {}
        o = 12
        while o + 8 <= len(b):
            cid = b[o:o + 4].decode("latin-1")
            size = struct.unpack_from("<I", b, o + 4)[0]
            self.chunks.setdefault(cid, (o + 8, min(len(b), o + 8 + size)))
            o += 8 + size + (size & 1)
        if "fmt " not in self.chunks or "data" not in self.chunks:
            raise ValueError("missing fmt or data chunk")
        a, _ = self.chunks["fmt "]
        fmt, ch, sr, _, block, bits = struct.unpack_from("<HHIIHH", b, a)
        if fmt == 0xFFFE:  # WAVE_FORMAT_EXTENSIBLE: real format in the sub-format GUID
            fmt = struct.unpack_from("<H", b, a + 24)[0]
        if fmt not in (1, 3):
            raise ValueError(f"unsupported WAV format tag {fmt} (PCM and float only)")
        self.float = fmt == 3
        self.channels, self.rate, self.bits, self.block = ch, sr, bits, block
        da, db = self.chunks["data"]
        self.data_off, self.data_end = da, db
        self.frames = (db - da) // block if block else 0

    def body(self, cid):
        if cid not in self.chunks:
            return None
        a, b = self.chunks[cid]
        return self.raw[a:b]

    def meta(self):
        m = {}
        bx = self.body("bext")
        if bx and len(bx) >= 346:
            s = lambda a, b: bx[a:b].split(b"\0")[0].decode("latin-1", "replace").strip()
            m["bext"] = {"description": s(0, 256), "originator": s(256, 288), "date": s(320, 330), "time": s(330, 338)}
        ix = self.body("iXML")
        if ix:
            t = ix.decode("utf-8", "replace")
            for tag in ("PROJECT", "SCENE", "TAKE", "NOTE", "TAPE"):
                mm = re.search(rf"<{tag}>(.*?)</{tag}>", t, re.S)
                if mm and mm.group(1).strip():
                    m.setdefault("ixml", {})[tag.lower()] = mm.group(1).strip()
        li = self.body("LIST")
        if li and li[:4] == b"INFO":
            p = 4
            while p + 8 <= len(li):
                sid = li[p:p + 4].decode("latin-1")
                sz = struct.unpack_from("<I", li, p + 4)[0]
                m.setdefault("info", {})[sid] = li[p + 8:p + 8 + sz].split(b"\0")[0].decode("utf-8", "replace")
                p += 8 + sz + (sz & 1)
        sm = self.body("smpl")
        if sm and len(sm) >= 60 and struct.unpack_from("<I", sm, 28)[0] > 0:
            m["loop"] = {"start": struct.unpack_from("<I", sm, 44)[0], "end": struct.unpack_from("<I", sm, 48)[0]}
        mj = self.body("mmjs")
        if mj:
            try:
                m["mmjs"] = json.loads(mj.decode("utf-8"))
            except ValueError:
                pass
        return m

    def samples(self):
        """Interleaved samples as floats in [-1, 1] (array('f'))."""
        raw = self.raw[self.data_off:self.data_end]
        n = len(raw) // (self.bits // 8)
        out = array.array("f")
        if self.float and self.bits == 32:
            out.frombytes(raw[:n * 4])
            if sys.byteorder != "little":
                out.byteswap()
        elif self.float and self.bits == 64:
            d = array.array("d"); d.frombytes(raw[:n * 8])
            if sys.byteorder != "little":
                d.byteswap()
            out = array.array("f", d)
        elif self.bits == 16:
            s = array.array("h"); s.frombytes(raw[:n * 2])
            if sys.byteorder != "little":
                s.byteswap()
            out = array.array("f", (v / 32768.0 for v in s))
        elif self.bits == 24:
            # pad each 3-byte sample to 4 bytes (low byte 0) → int32 >> 8
            padded = bytearray(n * 4)
            padded[1::4] = raw[0:n * 3:3]
            padded[2::4] = raw[1:n * 3:3]
            padded[3::4] = raw[2:n * 3:3]
            s = array.array("i"); s.frombytes(bytes(padded))
            if sys.byteorder != "little":
                s.byteswap()
            out = array.array("f", (v / 2147483648.0 for v in s))
        elif self.bits == 32:
            s = array.array("i"); s.frombytes(raw[:n * 4])
            if sys.byteorder != "little":
                s.byteswap()
            out = array.array("f", (v / 2147483648.0 for v in s))
        elif self.bits == 8:
            out = array.array("f", ((v - 128) / 128.0 for v in raw[:n]))
        else:
            raise ValueError(f"unsupported bit depth {self.bits}")
        return out


def write_wav16(path: Path, samples, channels, rate, extra_chunks=()):
    """16-bit PCM WAV with TPDF dither; extra_chunks: (id, bytes) kept verbatim (bext, LIST, smpl, iXML, mmjs)."""
    rnd = random.random
    pcm = array.array("h", (max(-32768, min(32767, int(round(v * 32767.0 + (rnd() - rnd()))))) for v in samples))
    if sys.byteorder != "little":
        pcm.byteswap()
    data = pcm.tobytes()
    chunks = [(b"fmt ", struct.pack("<HHIIHH", 1, channels, rate, rate * channels * 2, channels * 2, 16))]
    chunks += [(cid.encode("latin-1") if isinstance(cid, str) else cid, body) for cid, body in extra_chunks]
    chunks.append((b"data", data))
    blob = bytearray(b"RIFF\0\0\0\0WAVE")
    for cid, body in chunks:
        blob += cid + struct.pack("<I", len(body)) + body + (b"\0" if len(body) & 1 else b"")
    struct.pack_into("<I", blob, 4, len(blob) - 8)
    path.write_bytes(bytes(blob))


def copy_for_game(src: Wav, dest: Path, keep_bits: bool):
    dest.parent.mkdir(parents=True, exist_ok=True)
    if keep_bits or (src.bits == 16 and not src.float):
        shutil.copyfile(src.path, dest)
        return "copied as is"
    keep = [(cid, src.body(cid)) for cid in ("bext", "LIST", "smpl", "cue ", "iXML", "mmjs") if src.body(cid)]
    write_wav16(dest, src.samples(), src.channels, src.rate, keep)
    return f"converted {src.bits}-bit{' float' if src.float else ''} → 16-bit"


def peak_db(samples):
    p = max((abs(v) for v in samples), default=0.0)
    return -180.0 if p <= 1e-9 else 20 * __import__("math").log10(p)


# ── catalog helpers ──────────────────────────────────────────────────
def field_score(t):
    s = f"{t.get('title', '')} {t.get('desc', '')} {t.get('id', '')}".lower()
    return sum(1 for w in FIELD_YES if w in s) - 2 * sum(1 for w in FIELD_NO if w in s)


def load_catalog():
    return json.loads(CATALOG.read_text(encoding="utf-8"))


def wanted(all_tracks=False):
    out = []
    for t in load_catalog():
        src = t.get("src")
        if not src:
            continue
        p = GODOT / src
        if p.exists() or p.with_suffix(".wav").exists():
            continue
        t = dict(t, field_score=field_score(t), wav_src=str(Path(src).with_suffix(".wav")))
        if all_tracks or t["field_score"] > 0:
            out.append(t)
    return sorted(out, key=lambda t: (-t["field_score"], t.get("vol", 0)))


def load_field_catalog():
    if FIELD_CATALOG.exists():
        return json.loads(FIELD_CATALOG.read_text(encoding="utf-8"))
    return []


def save_field_catalog(rows):
    FIELD_CATALOG.write_text(json.dumps(rows, indent=1, ensure_ascii=False) + "\n", encoding="utf-8")


def slug(s):
    return re.sub(r"[^a-z0-9]+", "_", str(s or "").lower()).strip("_")[:60] or "take"


def sha1(path):
    h = hashlib.sha1()
    with open(path, "rb") as f:
        for blk in iter(lambda: f.read(1 << 20), b""):
            h.update(blk)
    return h.hexdigest()


def wavs_in(paths):
    for p in paths:
        p = Path(p).expanduser()
        if p.is_dir():
            yield from sorted(x for x in p.rglob("*") if x.suffix.lower() == ".wav" and not x.name.startswith("._"))
        elif p.suffix.lower() == ".wav":
            yield p


def describe(w: Wav):
    m = w.meta()
    mj = m.get("mmjs", {})
    ix = m.get("ixml", {})
    # recorder notes beat the BWF description (often a technical string like "zTRK1=…")
    title = (mj.get("title") or m.get("info", {}).get("INAM") or ix.get("note")
             or " ".join(x for x in (ix.get("scene"), ix.get("take") and "take " + ix["take"]) if x)
             or m.get("bext", {}).get("description") or w.path.stem)
    date = mj.get("recordedAt") or mj.get("date") or (m.get("bext", {}).get("date", "") + "T" + m.get("bext", {}).get("time", "")).strip("T")
    return m, mj, title, date


# ── commands ─────────────────────────────────────────────────────────
def cmd_wanted(a):
    rows = wanted(a.all)
    if not rows:
        print("nothing missing" + ("" if a.all else " that reads like a field recording (try --all)") + ".")
        return 0
    for t in rows:
        dots = "●" * max(0, min(5, t["field_score"]))
        print(f"{dots:<5} v{t.get('vol', '?'):<2} {t['id']:<36} {t.get('title', '')}")
        if a.verbose and t.get("desc"):
            print(f"      {t['desc'][:110]}")
            print(f"      → fill writes {t['wav_src']}")
    print(f"\n{len(rows)} track(s). Fill one:  python3 godot/tools/field_ingest.py fill <id> <take.wav>")
    return 0


def cmd_scan(a):
    n = 0
    for p in wavs_in(a.paths):
        try:
            w = Wav(p)
        except (ValueError, OSError) as e:
            print(f"✗ {p}: {e}")
            continue
        m, mj, title, date = describe(w)
        dur = w.frames / w.rate if w.rate else 0
        fmt = f"{w.rate // 1000 if w.rate % 1000 == 0 else w.rate / 1000} kHz {w.bits}-bit{' float' if w.float else ''} {'mono' if w.channels == 1 else str(w.channels) + 'ch'}"
        extra = []
        if "loop" in m: extra.append("∞ loop points")
        if mj.get("forTrack"): extra.append("for " + mj["forTrack"])
        if mj.get("locale"): extra.append("@ " + mj["locale"])
        if m.get("ixml"): extra.append("iXML " + " ".join(f"{k}={v}" for k, v in m["ixml"].items()))
        print(f"· {p.name:<34} {dur:7.1f}s  {fmt:<26} {title[:40]}  {date[:19]}  {' · '.join(extra)}")
        n += 1
    print(f"\n{n} WAV file(s).")
    return 0


def cmd_ingest(a):
    rows = load_field_catalog()
    known = {r.get("sha1") for r in rows}
    done = skipped = 0
    for p in wavs_in(a.paths):
        try:
            w = Wav(p)
        except (ValueError, OSError) as e:
            print(f"✗ {p.name}: {e}")
            continue
        h = sha1(p)
        if h in known:
            skipped += 1
            continue
        m, mj, title, date = describe(w)
        side = p.with_suffix(".json")
        if side.exists():
            try:
                mj = dict(json.loads(side.read_text(encoding="utf-8")), **mj)
                title = mj.get("title") or title
            except ValueError:
                pass
        locale = slug(a.locale or mj.get("locale") or "unsorted")
        stamp = (re.sub(r"[^0-9]", "", date)[:14] or datetime.now().strftime("%Y%m%d%H%M%S"))
        name = f"{slug(title)}_{stamp}.wav"
        dest = FIELD_DIR / locale / name
        rel = dest.relative_to(GODOT).as_posix()
        tags = sorted(set((mj.get("tags") or []) + (a.tag or [])))
        row = {
            "id": f"field_{locale}_{slug(title)}_{stamp}", "path": rel, "title": title, "locale": locale, "tags": tags,
            "notes": mj.get("notes") or m.get("ixml", {}).get("note", ""), "duration": round(w.frames / w.rate, 2),
            "rate": w.rate, "channels": w.channels, "loop": m.get("loop") or mj.get("loop"), "recorded": date,
            "source": str(p), "sha1": h, "gps": mj.get("gps"), "forTrack": mj.get("forTrack") or "",
        }
        if a.dry_run:
            print(f"would ingest {p.name} → {rel}" + (f"  (for {row['forTrack']})" if row["forTrack"] else ""))
            continue
        how = copy_for_game(w, dest, a.keep_bits)
        dest.with_suffix(".json").write_text(json.dumps(row, indent=1, ensure_ascii=False) + "\n", encoding="utf-8")
        rows.append(row); known.add(h); done += 1
        print(f"✓ {p.name} → {rel}  ({how})")
        if row["forTrack"] and a.apply_tracks:
            fill_track(row["forTrack"], dest, convert=False, force=a.force)
    if not a.dry_run:
        save_field_catalog(rows)
    print(f"\n{done} ingested, {skipped} already known. Catalog: {FIELD_CATALOG.relative_to(GODOT)}")
    return 0


def fill_track(track_id, wav_path: Path, convert=False, force=False, keep_bits=False):
    cat = {t["id"]: t for t in load_catalog()}
    t = cat.get(track_id)
    if not t or not t.get("src"):
        print(f"✗ no catalog track '{track_id}'. List them: field_ingest.py wanted --all")
        return 1
    src = GODOT / t["src"]
    if convert:
        if not shutil.which("ffmpeg"):
            print("✗ --convert needs ffmpeg on PATH; without it the .wav fill works the same in-game.")
            return 1
        if src.exists() and not force:
            print(f"✗ {t['src']} exists — add --force to replace it.")
            return 1
        src.parent.mkdir(parents=True, exist_ok=True)
        codec = ["-c:a", "libvorbis", "-q:a", "5"] if src.suffix == ".ogg" else ["-c:a", "libmp3lame", "-q:a", "2"]
        r = subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", str(wav_path), *codec, str(src)])
        if r.returncode:
            print("✗ ffmpeg failed.")
            return 1
        print(f"✓ {track_id}: wrote {t['src']} (ffmpeg). Loop it in Godot's import settings if it's a bed.")
        return 0
    dest = src.with_suffix(".wav")
    if dest.exists() and not force:
        print(f"✗ {dest.relative_to(GODOT)} exists — add --force to replace it.")
        return 1
    w = Wav(wav_path)
    how = copy_for_game(w, dest, keep_bits)
    loop = "with loop points" if w.meta().get("loop") else "no loop points (make a seamless loop in FIELD RECORDER for beds)"
    print(f"✓ {track_id}: {dest.relative_to(GODOT)}  ({how}; {loop}). AudioMgr plays it in place of {Path(t['src']).name}.")
    return 0


def cmd_fill(a):
    return fill_track(a.track, Path(a.wav).expanduser(), convert=a.convert, force=a.force, keep_bits=a.keep_bits)


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)
    w = sub.add_parser("wanted", help="catalog tracks that have no audio file yet")
    w.add_argument("--all", action="store_true", help="include tracks that read like composed music")
    w.add_argument("-v", "--verbose", action="store_true")
    w.set_defaults(fn=cmd_wanted)
    s = sub.add_parser("scan", help="list WAVs with their metadata (nothing is copied)")
    s.add_argument("paths", nargs="+")
    s.set_defaults(fn=cmd_scan)
    i = sub.add_parser("ingest", help="copy WAVs into assets/audio/field and catalog them")
    i.add_argument("paths", nargs="+")
    i.add_argument("--locale", help="game locale (default: from the take's metadata, else 'unsorted')")
    i.add_argument("--tag", action="append", help="add a tag (repeatable)")
    i.add_argument("--keep-bits", action="store_true", help="copy without converting to 16-bit")
    i.add_argument("--apply-tracks", action="store_true", help="also fill catalog tracks named in FIELD RECORDER sidecars")
    i.add_argument("--force", action="store_true", help="with --apply-tracks: replace existing fills")
    i.add_argument("--dry-run", action="store_true")
    i.set_defaults(fn=cmd_ingest)
    f = sub.add_parser("fill", help="give a catalog track its audio")
    f.add_argument("track")
    f.add_argument("wav")
    f.add_argument("--convert", action="store_true", help="encode to the track's .ogg / .mp3 with ffmpeg")
    f.add_argument("--keep-bits", action="store_true")
    f.add_argument("--force", action="store_true")
    f.set_defaults(fn=cmd_fill)
    a = ap.parse_args(argv)
    return a.fn(a)


if __name__ == "__main__":
    sys.exit(main())
