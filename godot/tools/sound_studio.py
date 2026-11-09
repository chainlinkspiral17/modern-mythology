#!/usr/bin/env python3
"""sound_studio.py — dialogue, sound design and music production studio.

One board for everything in the game that still needs audio — voice lines, SFX
slots, music tracks — next to a library of takes, effects and tracks you can
audition and assign. Assigning copies (or transcodes) the file to the path the
game loads and wires it in; nothing is left to unzip or run by hand.

  ./tools/run_sound_studio.sh            # recommended: sets up numpy + anthropic, opens the browser
  python3 tools/sound_studio.py          # same, with whatever Python you have
  python3 tools/sound_studio.py --status # print the outstanding-audio report and exit

Where things live:
  ../audio_library/            the library (git-ignored except scores/)
      takes/<scene_id>/NNN_*   dialogue takes; the NNN prefix links a take to its line
      sfx/<slot_id>/*          candidates for an SFX slot (anything else under sfx/ is general)
      music/<track_id>/*       candidates for a music track
      scores/<track_id>/*      .score.json + .mid (tracked in git; render them any time)
  godot/assets/audio/...       what the game plays (written by Assign)
  godot/resources/scenes/      "voice" keys are patched here
  godot/resources/sfx_catalog.json, music_catalog.json   the slot lists

The server binds to 127.0.0.1 only. Generation hooks are in sound_gen.py and
configured in sound_providers.json.
"""

import argparse
import hashlib
import json
import mimetypes
import os
import re
import shutil
import subprocess
import sys
import threading
import time
import urllib.parse
import webbrowser
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import sound_gen as gen  # noqa: E402

REPO = gen.REPO                      # godot/
ROOT = gen.ROOT
TOOLS = gen.TOOLS
SCENES_ROOT = gen.SCENES_ROOT
VOICE_ROOT = REPO / "assets" / "audio" / "voice"
VOICE_KINDS = {"narrate", "say", "think"}
GAME_EXTS = (".ogg", ".mp3", ".wav")            # what Godot imports
AUDIO_EXTS = GAME_EXTS + (".flac", ".m4a", ".aac", ".webm", ".opus", ".aif", ".aiff")
SCORE_EXTS = (".mid", ".midi", ".json")
MAX_UPLOAD = 400 * 1024 * 1024


class StudioError(Exception):
    pass


def char_key(name):
    return (name or "_narrator").strip().lower().replace(" ", "_") or "_narrator"


def sha1(path):
    h = hashlib.sha1()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def safe_name(name):
    name = re.sub(r"[^A-Za-z0-9._-]+", "_", Path(name).name).strip("._") or "file"
    return name[:120]


def dump_like(original_text, data):
    """Serialize `data` the way `original_text` was written, so diffs stay minimal."""
    nl = "\n" if original_text.endswith("\n") else ""
    try:
        parsed = json.loads(original_text)
    except json.JSONDecodeError:
        parsed = None
    for indent in (2, 1):
        for ascii_ in (False, True):
            if parsed is not None and json.dumps(parsed, indent=indent, ensure_ascii=ascii_) + nl == original_text:
                return json.dumps(data, indent=indent, ensure_ascii=ascii_) + nl
    return json.dumps(data, indent=2, ensure_ascii=False) + nl


class Studio:
    def __init__(self, library):
        self.library = Path(library).resolve()
        self.lock = threading.RLock()
        self.scene_cache = {}        # path -> (mtime, summary, lines)
        self.meta_path = self.library / "library.json"
        self.meta = {"items": {}, "ledger": {}, "durations": {}}
        self.jobs = {}
        self.job_seq = 0
        self._refs = None
        self.ensure_library()
        self.load_meta()

    # ── library bookkeeping ──────────────────────────────────────────────
    def ensure_library(self):
        for d in ("takes", "sfx", "music", "scores"):
            (self.library / d).mkdir(parents=True, exist_ok=True)

    def load_meta(self):
        try:
            data = json.loads(self.meta_path.read_text(encoding="utf-8"))
            for k in self.meta:
                if isinstance(data.get(k), dict):
                    self.meta[k] = data[k]
        except (OSError, json.JSONDecodeError):
            pass

    def save_meta(self):
        tmp = self.meta_path.with_suffix(".json.tmp")
        tmp.write_text(json.dumps(self.meta, indent=1, ensure_ascii=False), encoding="utf-8")
        os.replace(tmp, self.meta_path)

    # ── scenes / voice slots ─────────────────────────────────────────────
    def scene_paths(self):
        return sorted(SCENES_ROOT.glob("vol*/vol*.json"))

    def load_scene(self, path):
        mtime = path.stat().st_mtime
        hit = self.scene_cache.get(path)
        if hit and hit[0] == mtime:
            return hit[1], hit[2]
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            return None, []
        if not isinstance(data, dict) or not isinstance(data.get("nodes"), list):
            return None, []
        sid = data.get("id", path.stem)
        vdir = VOICE_ROOT / sid
        on_disk = {}
        if vdir.is_dir():
            for f in vdir.iterdir():
                if f.suffix.lower() in GAME_EXTS and f.stem.isdigit():
                    on_disk.setdefault(int(f.stem), []).append(f.name)
        lines, chars = [], {}
        for i, node in enumerate(data["nodes"]):
            if not isinstance(node, dict) or node.get("t") not in VOICE_KINDS:
                continue
            text = (node.get("text") or "").strip()
            if not text:
                continue
            char = "_narrator" if node["t"] == "narrate" else (node.get("char") or "_narrator")
            ck = char_key(char)
            voice = node.get("voice") or ""
            if voice:
                status = "assigned" if (REPO / voice).is_file() else "missing"
                current = voice
            elif i in on_disk:
                status = "unwired"
                current = f"assets/audio/voice/{sid}/{sorted(on_disk[i])[0]}"
            else:
                status, current = "outstanding", ""
            lines.append({"slot": f"voice:{sid}:{i}", "kind": "voice", "scene": sid, "index": i,
                          "t": node["t"], "char": char, "ck": ck, "text": text,
                          "status": status, "current": current, "vol": data.get("vol", 0)})
            c = chars.setdefault(ck, [0, 0])
            c[0] += 1
            c[1] += status == "assigned"
        summary = {"id": sid, "vol": data.get("vol", 0), "chapter": str(data.get("chapter", "")),
                   "title": data.get("title") or "", "type": data.get("type", ""),
                   "total": len(lines), "done": sum(1 for l in lines if l["status"] == "assigned"),
                   "attn": sum(1 for l in lines if l["status"] in ("missing", "unwired")),
                   "chars": chars}
        self.scene_cache[path] = (mtime, summary, lines)
        return summary, lines

    def scenes(self):
        order = {}
        try:
            idx = json.loads((SCENES_ROOT / "index.json").read_text(encoding="utf-8"))
            n = 0
            for vol in sorted(idx, key=lambda v: int(v) if str(v).isdigit() else 99):
                for sid in idx[vol]:
                    order[sid] = n
                    n += 1
        except (OSError, json.JSONDecodeError, AttributeError):
            pass
        out = []
        for p in self.scene_paths():
            s, _ = self.load_scene(p)
            if s and s["total"]:
                out.append(s)
        out.sort(key=lambda s: (s["vol"], order.get(s["id"], 10 ** 6), s["id"]))
        return out

    def scene_path(self, scene_id):
        for p in SCENES_ROOT.glob(f"vol*/{scene_id}.json"):
            return p
        raise StudioError(f"no scene {scene_id!r}")

    def lines(self, scene=None, char=None, vol=None, status=None, q=None, offset=0, limit=400):
        out = []
        if scene:
            _, out = self.load_scene(self.scene_path(scene))
            out = list(out)
        else:
            for p in self.scene_paths():
                s, ls = self.load_scene(p)
                if not s or (vol is not None and s["vol"] != vol):
                    continue
                if char and char not in s["chars"]:
                    continue
                out.extend(ls)
        if char:
            out = [l for l in out if l["ck"] == char]
        if status == "outstanding":
            out = [l for l in out if l["status"] != "assigned"]
        elif status:
            out = [l for l in out if l["status"] == status]
        if q:
            ql = q.lower()
            out = [l for l in out if ql in l["text"].lower() or ql in l["char"].lower()]
        return {"total": len(out), "offset": offset, "lines": out[offset:offset + limit]}

    # ── music / sfx slots ────────────────────────────────────────────────
    def code_refs(self):
        """Text of every script / scene / data file that could reference an audio path."""
        if self._refs is None:
            chunks = []
            for pat in ("**/*.gd", "**/*.tscn"):
                for f in REPO.glob(pat):
                    if "tools" in f.relative_to(REPO).parts[:1] or ".godot" in f.parts:
                        continue
                    try:
                        chunks.append(f.read_text(encoding="utf-8", errors="replace"))
                    except OSError:
                        pass
            for f in SCENES_ROOT.glob("vol*/*.json"):
                try:
                    txt = f.read_text(encoding="utf-8", errors="replace")
                except OSError:
                    continue
                if "audio/sfx/" in txt:
                    chunks.append(txt)
            self._refs = "\n".join(chunks)
        return self._refs

    def music_slots(self):
        try:
            cat = json.loads(gen.MUSIC_CATALOG.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            return []
        out = []
        for t in cat:
            src = t.get("src", "")
            exists = bool(src) and (REPO / src).is_file()
            out.append({"slot": f"music:{t.get('id')}", "kind": "music", "id": t.get("id"),
                        # a few KB of "music" is a placeholder stub, not a track
                        "tiny": exists and (REPO / src).stat().st_size < 48 * 1024,
                        "vol": t.get("vol", 0), "title": t.get("title", ""), "desc": t.get("desc", ""),
                        "target": src, "chapters": t.get("chapters", []), "chars": t.get("chars", []),
                        "status": "assigned" if src and (REPO / src).is_file() else "outstanding",
                        "current": src if src and (REPO / src).is_file() else ""})
        return out

    def sfx_slots(self):
        try:
            cat = json.loads(gen.SFX_CATALOG.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            return []
        refs = self.code_refs()
        out = []
        for s in cat:
            src = s.get("src", "")
            out.append({"slot": f"sfx:{s.get('id')}", "kind": "sfx", "id": s.get("id"),
                        "group": s.get("group", ""), "title": s.get("label", s.get("id")),
                        "desc": s.get("brief", ""), "target": src,
                        "wired": bool(src) and src in refs,
                        "status": "assigned" if src and (REPO / src).is_file() else "outstanding",
                        "current": src if src and (REPO / src).is_file() else ""})
        return out

    def add_sfx_slot(self, sid, label, brief, group):
        sid = re.sub(r"[^a-z0-9_]+", "_", (sid or "").lower()).strip("_")
        if not sid:
            raise StudioError("slot id needed (letters, digits, underscores)")
        cat = json.loads(gen.SFX_CATALOG.read_text(encoding="utf-8"))
        if any(s.get("id") == sid for s in cat):
            raise StudioError(f"an SFX slot named {sid} already exists")
        cat.append({"id": sid, "group": group or "scene", "label": label or sid,
                    "src": f"assets/audio/sfx/{sid}.ogg", "brief": brief or ""})
        gen.SFX_CATALOG.write_text(json.dumps(cat, indent=1, ensure_ascii=False), encoding="utf-8")
        return f"sfx:{sid}"

    def slot(self, slot_id):
        kind, _, rest = slot_id.partition(":")
        if kind == "voice":
            scene, _, idx = rest.rpartition(":")
            _, lines = self.load_scene(self.scene_path(scene))
            for l in lines:
                if l["index"] == int(idx):
                    return dict(l, target_dir=f"assets/audio/voice/{scene}")
        elif kind in ("music", "sfx"):
            for s in (self.music_slots() if kind == "music" else self.sfx_slots()):
                if s["id"] == rest:
                    return s
        raise StudioError(f"no slot {slot_id!r}")

    # ── library ──────────────────────────────────────────────────────────
    def infer_link(self, rel, known):
        parts = rel.split("/")
        top = parts[0]
        if top == "takes" and len(parts) >= 3:
            m = re.match(r"(\d{1,5})", parts[-1])
            if m:
                return f"voice:{parts[1]}:{int(m.group(1))}"
        elif top in ("music", "sfx", "scores"):
            kind = "music" if top in ("music", "scores") else "sfx"
            cands = [parts[1]] if len(parts) >= 3 else []
            cands.append(parts[-1].split("__")[0].split(".")[0])
            for c in cands:
                if f"{kind}:{c}" in known:
                    return f"{kind}:{c}"
        return ""

    def library_items(self, known_slots):
        items, budget, dirty = [], 300, False
        live = {}
        for slot_id, led in self.meta["ledger"].items():
            live.setdefault(led.get("item", ""), []).append(slot_id)
        seen = set()
        for base, prefix in ((self.library, ""), (REPO / "assets" / "audio", "game:")):
            if not base.is_dir():
                continue
            for dirpath, dirnames, filenames in os.walk(base):
                dirnames[:] = sorted(d for d in dirnames if not d.startswith("."))
                for fn in sorted(filenames):
                    ext = os.path.splitext(fn)[1].lower()
                    full = Path(dirpath) / fn
                    rel = full.relative_to(base).as_posix()
                    is_score = ext in (".mid", ".midi") or fn.endswith(".score.json")
                    if prefix and (ext not in GAME_EXTS or rel.startswith("voice/")):
                        continue
                    if not prefix and not (ext in AUDIO_EXTS or is_score):
                        continue
                    try:
                        st = full.stat()
                    except OSError:
                        continue
                    iid = prefix + rel
                    seen.add(iid)
                    top = rel.split("/")[0]
                    if prefix:
                        kind = {"bgm": "music", "sfx": "sfx"}.get(top, "other")
                    elif is_score:
                        kind = "score"
                    else:
                        kind = {"takes": "voice", "sfx": "sfx", "music": "music"}.get(top, "other")
                    dur = None
                    if not is_score:
                        key = f"{int(st.st_mtime)}:{st.st_size}"
                        cached = self.meta["durations"].get(iid)
                        if cached and cached[0] == key:
                            dur = cached[1]
                        elif budget > 0:
                            budget -= 1
                            dur = gen.probe_duration(full)
                            self.meta["durations"][iid] = [key, dur]
                            dirty = True
                    m = self.meta["items"].get(iid, {})
                    link = m.get("link") or ("" if prefix else self.infer_link(rel, known_slots))
                    items.append({"id": iid, "name": fn, "dir": os.path.dirname(rel), "kind": kind,
                                  "ext": ext.lstrip("."), "size": st.st_size, "mtime": int(st.st_mtime),
                                  "dur": dur, "link": link, "game": bool(prefix),
                                  "rating": m.get("rating", 0), "tags": m.get("tags", []),
                                  "note": m.get("note", ""), "live": live.get(iid, [])})
        stale = [k for k in self.meta["durations"] if k not in seen]
        for k in stale:
            del self.meta["durations"][k]
        if dirty or stale:
            self.save_meta()
        items.sort(key=lambda it: -it["mtime"])
        return items

    def item_path(self, item_id):
        if item_id.startswith("game:"):
            base, rel = (REPO / "assets" / "audio").resolve(), item_id[5:]
        else:
            base, rel = self.library, item_id
        p = (base / rel).resolve()
        if base not in p.parents or not p.is_file():
            raise StudioError(f"no library item {item_id!r}")
        return p

    def set_meta(self, item_id, patch):
        self.item_path(item_id)
        m = self.meta["items"].setdefault(item_id, {})
        if "rating" in patch:
            m["rating"] = max(0, min(5, int(patch["rating"])))
        if "tags" in patch:
            m["tags"] = [str(t).strip()[:40] for t in patch["tags"] if str(t).strip()][:12]
        if "note" in patch:
            m["note"] = str(patch["note"])[:500]
        if "link" in patch:
            m["link"] = str(patch["link"])
        self.save_meta()

    def unique(self, path):
        path = Path(path)
        n, out = 2, path
        while out.exists():
            out = path.with_name(f"{path.stem}_{n}{path.suffix}")
            n += 1
        return out

    def library_dir_for(self, slot):
        if slot["kind"] == "voice":
            return self.library / "takes" / slot["scene"]
        return self.library / slot["kind"] / slot["id"]

    def save_upload(self, name, data, kind, slot_id):
        name = safe_name(name)
        ext = os.path.splitext(name)[1].lower()
        is_score = ext in (".mid", ".midi") or name.endswith(".score.json")
        if not (ext in AUDIO_EXTS or is_score):
            raise StudioError(f"{name}: not an audio, MIDI or score file")
        slot = self.slot(slot_id) if slot_id else None
        if is_score:
            dest = self.library / "scores" / (slot["id"] if slot and slot["kind"] == "music" else "inbox")
        elif slot:
            dest = self.library_dir_for(slot)
            if slot["kind"] == "voice" and not re.match(r"\d{3}", name):
                name = f"{slot['index']:03d}_{name}"
        else:
            dest = self.library / {"voice": "takes", "sfx": "sfx", "music": "music"}.get(kind, "music") / "inbox"
        dest.mkdir(parents=True, exist_ok=True)
        out = self.unique(dest / name)
        out.write_bytes(data)
        return out.relative_to(self.library).as_posix()

    def trash(self, item_id):
        if item_id.startswith("game:"):
            raise StudioError("in-game files are removed with Unassign, not from the library")
        p = self.item_path(item_id)
        dest = self.unique(self.library / ".trash" / p.name)
        dest.parent.mkdir(parents=True, exist_ok=True)
        shutil.move(str(p), dest)
        self.meta["items"].pop(item_id, None)
        self.save_meta()

    # ── assign / unassign ────────────────────────────────────────────────
    def displace(self, slot, files):
        """Move files out of the game's way. A file that is byte-identical to the
        library item it came from is simply removed; anything else is kept as a
        candidate so no take is ever lost."""
        led = self.meta["ledger"].get(slot["slot"], {})
        kept = []
        for f in files:
            if not f.is_file():
                continue
            src_ok = False
            if led.get("sha") and led.get("item"):
                try:
                    self.item_path(led["item"])
                    src_ok = sha1(f) == led["sha"]
                except StudioError:
                    src_ok = False
            if src_ok:
                f.unlink()
            else:
                d = self.library_dir_for(slot)
                d.mkdir(parents=True, exist_ok=True)
                stem = f"{slot['index']:03d}" if slot["kind"] == "voice" else slot["id"] + "_"
                dest = self.unique(d / f"{stem}_prev_{gen.stamp()}{f.suffix.lower()}")
                shutil.move(str(f), dest)
                kept.append(dest.relative_to(self.library).as_posix())
            imp = Path(str(f) + ".import")
            if imp.exists():
                imp.unlink()
        return kept

    def patch_voice_key(self, slot, value):
        path = self.scene_path(slot["scene"])
        text = path.read_text(encoding="utf-8")
        data = json.loads(text)
        node = data["nodes"][slot["index"]]
        if node.get("t") not in VOICE_KINDS:
            raise StudioError("scene changed on disk: that node is no longer a voice line")
        if value:
            node["voice"] = value
        else:
            node.pop("voice", None)
        path.write_text(dump_like(text, data), encoding="utf-8")

    def assign(self, slot_id, item_id):
        with self.lock:
            slot = self.slot(slot_id)
            src = self.item_path(item_id)
            ext = src.suffix.lower()
            if ext not in AUDIO_EXTS:
                raise StudioError("that item is a score; render it first, then assign the audio")
            if slot["kind"] == "voice":
                tdir = REPO / slot["target_dir"]
                out_ext = ext if ext in GAME_EXTS else ".ogg"
                target = tdir / f"{slot['index']:03d}{out_ext}"
                old = [tdir / f"{slot['index']:03d}{e}" for e in GAME_EXTS]
                if slot.get("current"):
                    old.append(REPO / slot["current"])
            else:
                if not slot["target"]:
                    raise StudioError("this slot has no target path in its catalog")
                target = REPO / slot["target"]
                out_ext = target.suffix.lower()
                old = [target]
            if src.resolve() == target.resolve():
                raise StudioError("that file is already what this slot plays")
            target.parent.mkdir(parents=True, exist_ok=True)
            tmp = target.with_name(f".{target.stem}.incoming{out_ext}")
            if ext == out_ext:
                shutil.copyfile(src, tmp)
            else:
                if not gen.have("ffmpeg"):
                    raise StudioError(f"this slot needs a {out_ext} file and ffmpeg isn't installed to convert {ext}")
                try:
                    gen.transcode(src, tmp, mono=slot["kind"] == "voice")
                except gen.GenError as e:
                    raise StudioError(str(e))
            seen, uniq = set(), []
            for f in old:
                if f.resolve() not in seen and f.is_file():
                    seen.add(f.resolve())
                    uniq.append(f)
            kept = self.displace(slot, uniq)
            os.replace(tmp, target)
            rel = target.relative_to(REPO).as_posix()
            if slot["kind"] == "voice":
                self.patch_voice_key(slot, rel)
            self.meta["ledger"][slot_id] = {"item": item_id, "sha": sha1(target), "at": int(time.time())}
            self.save_meta()
            return {"target": rel, "kept": kept, "converted": ext != out_ext}

    def unassign(self, slot_id):
        with self.lock:
            slot = self.slot(slot_id)
            files = []
            if slot["kind"] == "voice":
                tdir = REPO / slot["target_dir"]
                files = [tdir / f"{slot['index']:03d}{e}" for e in GAME_EXTS]
                if slot.get("current"):
                    files.append(REPO / slot["current"])
            elif slot.get("target"):
                files = [REPO / slot["target"]]
            seen, uniq = set(), []
            for f in files:
                if f.resolve() not in seen and f.is_file():
                    seen.add(f.resolve())
                    uniq.append(f)
            kept = self.displace(slot, uniq)
            if slot["kind"] == "voice":
                self.patch_voice_key(slot, "")
                try:
                    (REPO / slot["target_dir"]).rmdir()      # only succeeds when it is empty
                except OSError:
                    pass
            self.meta["ledger"].pop(slot_id, None)
            self.save_meta()
            return {"kept": kept}

    def wire(self, slot_id):
        """A recording already sits at the conventional path; just add the voice key."""
        with self.lock:
            slot = self.slot(slot_id)
            if slot["kind"] != "voice" or slot["status"] != "unwired":
                raise StudioError("nothing to wire for this slot")
            self.patch_voice_key(slot, slot["current"])
            return {"target": slot["current"]}

    # ── generation jobs ──────────────────────────────────────────────────
    def start_job(self, label, fn):
        with self.lock:
            self.job_seq += 1
            jid = self.job_seq
            job = {"id": jid, "label": label, "state": "running", "progress": 0.0, "message": "starting",
                   "started": time.time(), "files": [], "detail": ""}
            self.jobs[jid] = job

        def progress(frac, msg):
            job["progress"], job["message"] = round(float(frac), 3), msg

        def work():
            try:
                res = fn(progress)
                files = [Path(res[k]) for k in ("audio", "out", "score", "midi") if res.get(k)]
                job["files"] = [f.relative_to(self.library).as_posix() for f in files
                                if self.library in f.resolve().parents]
                bits = []
                if res.get("intent"):
                    bits.append(res["intent"])
                if res.get("levels"):
                    bits.append("mix: " + ", ".join(f"{l['name']} {l['db']:+.0f}dB" for l in res["levels"]))
                bits += res.get("warnings", [])
                job.update(state="done", progress=1.0, message="done", detail="  ·  ".join(bits))
            except (gen.GenError, StudioError) as e:
                job.update(state="error", message=str(e))
            except Exception as e:  # a hook can fail in ways we can't enumerate; show it, don't die
                job.update(state="error", message=f"{type(e).__name__}: {e}")
            job["ended"] = time.time()

        threading.Thread(target=work, daemon=True).start()
        return jid

    def generate(self, slot_id, provider, seconds, direction, renderer):
        slot = self.slot(slot_id)
        label = f"{provider} → {slot.get('title') or slot.get('char') or slot_id}"
        return self.start_job(label, lambda p: gen.run_job(slot_id, provider, self.library, seconds or None,
                                                           direction or "", renderer or "builtin", "mp3", p))

    def render_item(self, item_id, renderer):
        src = self.item_path(item_id)
        if item_id.startswith("game:") or not (src.suffix.lower() in (".mid", ".midi") or src.name.endswith(".score.json")):
            raise StudioError("only .score.json and .mid library items can be rendered")
        score = gen.load_score_file(src)
        stem = re.sub(r"\.score$", "", src.stem)
        rel = src.relative_to(self.library).parts
        sid = score.get("id") or (rel[1] if len(rel) >= 3 and rel[0] == "scores" else stem.split("__")[0])
        out = self.unique(self.library / "music" / sid / f"{stem}__{renderer}.mp3")

        def run(progress):
            res = gen.render(src, out, renderer, progress=progress)
            if src.suffix.lower() == ".json" and Path(res["midi"]) != src:
                mid = src.with_name(src.name.replace(".score.json", ".mid"))
                shutil.move(str(res["midi"]), mid)
                res["midi"] = mid
            return res
        return self.start_job(f"render {src.name} ({renderer})", run)

    # ── state ────────────────────────────────────────────────────────────
    def git_changes(self):
        try:
            p = subprocess.run(["git", "-C", str(ROOT), "status", "--porcelain", "--", "godot/assets/audio",
                                "godot/resources/scenes", "godot/resources/music_catalog.json",
                                "godot/resources/sfx_catalog.json", "audio_library/scores"],
                               capture_output=True, text=True, timeout=20)
            return len([l for l in p.stdout.splitlines() if l.strip()]) if p.returncode == 0 else None
        except (OSError, subprocess.SubprocessError):
            return None

    def state(self):
        with self.lock:
            scenes = self.scenes()
            music, sfx = self.music_slots(), self.sfx_slots()
            known = {s["slot"] for s in music} | {s["slot"] for s in sfx}
            chars = {}
            for s in scenes:
                for ck, (tot, done) in s["chars"].items():
                    c = chars.setdefault(ck, {"total": 0, "done": 0, "vols": {}})
                    c["total"] += tot
                    c["done"] += done
                    v = c["vols"].setdefault(str(s["vol"]), [0, 0])
                    v[0] += tot
                    v[1] += done
            try:
                provs, rends, cfg_err = gen.providers(), gen.renderers(), ""
            except gen.GenError as e:
                provs, rends, cfg_err = {}, {}, str(e)
            return {
                "scenes": [{k: v for k, v in s.items() if k != "chars"} for s in scenes],
                "chars": chars, "music": music, "sfx": sfx,
                "library": self.library_items(known),
                "providers": provs, "renderers": rends, "config_error": cfg_err,
                "env": {"ffmpeg": gen.have("ffmpeg"), "library": str(self.library),
                        "repo": str(ROOT), "git_changes": self.git_changes()},
                "jobs": self.job_list(),
            }

    def job_list(self):
        now = time.time()
        return [dict(j, age=round(now - j["started"]), ended_ago=round(now - j.get("ended", now))) for j in sorted(self.jobs.values(), key=lambda j: -j["id"])[:12]]

    def status_report(self):
        scenes = self.scenes()
        music, sfx = self.music_slots(), self.sfx_slots()
        out = ["OUTSTANDING AUDIO", ""]
        by_vol = {}
        for s in scenes:
            v = by_vol.setdefault(s["vol"], [0, 0])
            v[0] += s["total"]
            v[1] += s["done"]
        out.append("Dialogue (voiced / lines)")
        for vol in sorted(by_vol):
            tot, done = by_vol[vol]
            out.append(f"  vol {vol}:  {done:>5} / {tot:<6} {100 * done / tot:5.1f}%")
        tot = sum(v[0] for v in by_vol.values())
        done = sum(v[1] for v in by_vol.values())
        out.append(f"  all:    {done:>5} / {tot:<6} {100 * done / max(1, tot):5.1f}%")
        out.append("")
        out.append(f"Music: {sum(1 for m in music if m['status'] == 'assigned')} / {len(music)} tracks have a file")
        for vol in sorted({m["vol"] for m in music}):
            missing = [m["id"] for m in music if m["vol"] == vol and m["status"] != "assigned"]
            if missing:
                out.append(f"  vol {vol}: {len(missing)} outstanding")
        out.append("")
        out.append(f"SFX: {sum(1 for s in sfx if s['status'] == 'assigned')} / {len(sfx)} slots have a file")
        for s in sfx:
            if s["status"] != "assigned":
                out.append(f"  {s['id']:<26} {'played by game code' if s['wired'] else 'not referenced by code yet'}")
        return "\n".join(out)


# ── HTTP ─────────────────────────────────────────────────────────────────

class Handler(BaseHTTPRequestHandler):
    studio = None
    server_version = "MMSoundStudio/1"

    def log_message(self, fmt, *args):
        if os.environ.get("MM_STUDIO_LOG"):
            super().log_message(fmt, *args)

    def send_json(self, obj, code=200):
        body = json.dumps(obj, ensure_ascii=False).encode("utf-8")
        self.send_response(code)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        self.wfile.write(body)

    def send_file(self, path, ctype=None):
        size = path.stat().st_size
        start, end = 0, size - 1
        rng = self.headers.get("Range", "")
        m = re.match(r"bytes=(\d*)-(\d*)$", rng)
        partial = False
        if m and (m.group(1) or m.group(2)):
            if m.group(1):
                start = int(m.group(1))
                end = min(int(m.group(2)), size - 1) if m.group(2) else size - 1
            else:
                start = max(0, size - int(m.group(2)))
            if start > end or start >= size:
                self.send_response(416)
                self.send_header("Content-Range", f"bytes */{size}")
                self.end_headers()
                return
            partial = True
        self.send_response(206 if partial else 200)
        self.send_header("Content-Type", ctype or mimetypes.guess_type(path.name)[0] or "application/octet-stream")
        self.send_header("Accept-Ranges", "bytes")
        self.send_header("Content-Length", str(end - start + 1))
        self.send_header("Cache-Control", "no-store")
        if partial:
            self.send_header("Content-Range", f"bytes {start}-{end}/{size}")
        self.end_headers()
        with open(path, "rb") as f:
            f.seek(start)
            left = end - start + 1
            try:
                while left > 0:
                    chunk = f.read(min(1 << 16, left))
                    if not chunk:
                        break
                    self.wfile.write(chunk)
                    left -= len(chunk)
            except (BrokenPipeError, ConnectionResetError):
                pass

    def local_only(self):
        host = (self.headers.get("Host") or "").split(":")[0]
        return host in ("127.0.0.1", "localhost", "[::1]")

    def do_GET(self):
        st = self.studio
        url = urllib.parse.urlparse(self.path)
        q = {k: v[0] for k, v in urllib.parse.parse_qs(url.query).items()}
        try:
            if not self.local_only():
                return self.send_json({"error": "local only"}, 403)
            if url.path in ("/", "/index.html"):
                return self.send_file(TOOLS / "sound_studio.html", "text/html; charset=utf-8")
            if url.path == "/api/state":
                return self.send_json(st.state())
            if url.path == "/api/jobs":
                return self.send_json({"jobs": st.job_list()})
            if url.path == "/api/lines":
                return self.send_json(st.lines(q.get("scene"), q.get("char"),
                                               int(q["vol"]) if q.get("vol", "").lstrip("-").isdigit() else None,
                                               q.get("status"), q.get("q"), int(q.get("offset", 0)),
                                               min(1000, int(q.get("limit", 400)))))
            if url.path == "/api/brief":
                slot = gen.load_slot(q.get("slot", ""))
                secs = float(q.get("seconds") or 120)
                return self.send_json({"composer": gen.composer_brief(slot, secs) if slot["kind"] == "music" else "",
                                       "audio": gen.audio_prompt(slot, secs)})
            if url.path == "/audio":
                if q.get("item"):
                    return self.send_file(st.item_path(q["item"]))
                p = (REPO / q.get("game", "")).resolve()
                if (REPO / "assets" / "audio").resolve() not in p.parents or not p.is_file():
                    raise StudioError("no such audio file")
                return self.send_file(p)
            self.send_json({"error": "not found"}, 404)
        except (StudioError, gen.GenError) as e:
            self.send_json({"error": str(e)}, 400)
        except (ValueError, KeyError, IndexError) as e:
            self.send_json({"error": f"bad request: {e}"}, 400)

    def do_POST(self):
        st = self.studio
        url = urllib.parse.urlparse(self.path)
        q = {k: v[0] for k, v in urllib.parse.parse_qs(url.query).items()}
        try:
            # A custom header can't be sent cross-origin without a CORS preflight we never
            # answer, so a web page open in another tab can't drive this server.
            if not self.local_only() or self.headers.get("X-MM-Studio") != "1":
                return self.send_json({"error": "forbidden"}, 403)
            length = int(self.headers.get("Content-Length") or 0)
            if length > MAX_UPLOAD:
                return self.send_json({"error": "file too large"}, 413)
            raw = self.rfile.read(length) if length else b""
            if url.path == "/api/upload":
                with st.lock:
                    rel = st.save_upload(q.get("name", "upload"), raw, q.get("kind", ""), q.get("slot", ""))
                return self.send_json({"item": rel})
            body = json.loads(raw.decode("utf-8") or "{}")
            if url.path == "/api/assign":
                return self.send_json(st.assign(body["slot"], body["item"]))
            if url.path == "/api/unassign":
                return self.send_json(st.unassign(body["slot"]))
            if url.path == "/api/wire":
                return self.send_json(st.wire(body["slot"]))
            if url.path == "/api/meta":
                with st.lock:
                    st.set_meta(body["item"], body)
                return self.send_json({"ok": True})
            if url.path == "/api/trash":
                with st.lock:
                    st.trash(body["item"])
                return self.send_json({"ok": True})
            if url.path == "/api/sfx_slot":
                with st.lock:
                    return self.send_json({"slot": st.add_sfx_slot(body.get("id"), body.get("label"),
                                                                   body.get("brief"), body.get("group"))})
            if url.path == "/api/generate":
                return self.send_json({"job": st.generate(body["slot"], body["provider"], body.get("seconds"),
                                                          body.get("direction"), body.get("renderer"))})
            if url.path == "/api/render":
                return self.send_json({"job": st.render_item(body["item"], body.get("renderer") or "builtin")})
            self.send_json({"error": "not found"}, 404)
        except (StudioError, gen.GenError) as e:
            self.send_json({"error": str(e)}, 400)
        except (ValueError, KeyError, IndexError) as e:
            self.send_json({"error": f"bad request: {e}"}, 400)


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--library", default=os.environ.get("MM_AUDIO_LIBRARY", str(gen.LIB_DEFAULT)),
                    help="library folder (default: <repo>/audio_library, or $MM_AUDIO_LIBRARY)")
    ap.add_argument("--port", type=int, default=8787)
    ap.add_argument("--no-browser", action="store_true")
    ap.add_argument("--status", action="store_true", help="print the outstanding-audio report and exit")
    args = ap.parse_args()
    studio = Studio(args.library)
    if args.status:
        print(studio.status_report())
        return
    Handler.studio = studio
    server = None
    for port in range(args.port, args.port + 20):
        try:
            server = ThreadingHTTPServer(("127.0.0.1", port), Handler)
            break
        except OSError:
            continue
    if server is None:
        sys.exit(f"no free port in {args.port}-{args.port + 19}")
    url = f"http://127.0.0.1:{server.server_address[1]}/"
    print(f"Sound Studio  {url}\nlibrary       {studio.library}\nCtrl+C to stop.")
    if not args.no_browser:
        threading.Timer(0.6, lambda: webbrowser.open(url)).start()
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nstopped.")


if __name__ == "__main__":
    main()
