"""voice_ids — where the cast's ElevenLabs voice IDs live (2026-10-18).

The user: "all my voice IDs in the voice studio are gone ... when I ask to
save relevant data, I mean this." The voice studio kept them only in the
browser's localStorage, which belongs to one address and port: when Hero
Studio moved from port 8765 to 8877 (2026-10-13) the page opened at a new
address and found nothing. From now on the IDs live in files the repo keeps:

  * godot/tools/voice_map.json   — `characters.<key>.voice_id`, the file the
    renderer (elevenlabs_render.py) and the studio's import already share;
  * godot/tools/voice_ids_backup.json — a flat {key: voice_id} snapshot with
    the time and source of the last save, so a bad edit to the map can never
    take the IDs with it.

Hero Studio's SAVE commits and pushes both. Stdlib only.
"""
import json
import re
import time
from pathlib import Path

TOOLS = Path(__file__).resolve().parent
MAP_PATH = TOOLS / "voice_map.json"
BACKUP_PATH = TOOLS / "voice_ids_backup.json"
VOICE_ID_RE = re.compile(r"^[A-Za-z0-9]{12,40}$")


def load_ids():
    """{key: voice_id} for every character with a non-empty voice_id, plus
    any the backup holds that the map does not."""
    out = {}
    try:
        m = json.loads(MAP_PATH.read_text(encoding="utf-8"))
        for k, e in (m.get("characters") or {}).items():
            vid = ((e or {}).get("voice_id") or "").strip() if isinstance(e, dict) else ""
            if vid:
                out[k] = vid
    except (OSError, ValueError):
        pass
    try:
        b = json.loads(BACKUP_PATH.read_text(encoding="utf-8"))
        for k, vid in (b.get("ids") or {}).items():
            if vid and k not in out:
                out[k] = vid
    except (OSError, ValueError):
        pass
    return out


def _set_in_text(text, key, vid):
    """Set characters.<key>.voice_id in the map's own text, keeping its
    layout. Returns the new text, or None when the key's block or its
    voice_id field is not found (the caller then adds the key)."""
    m = re.search(r'\n(\s*)' + re.escape(json.dumps(key)) + r'\s*:\s*\{', text)
    if not m:
        return None
    start = m.end()
    depth, i = 1, start
    while i < len(text) and depth:
        c = text[i]
        if c == '"':                      # skip strings (they may hold braces)
            i += 1
            while i < len(text) and text[i] != '"':
                i += 2 if text[i] == "\\" else 1
        elif c == "{":
            depth += 1
        elif c == "}":
            depth -= 1
        i += 1
    block = text[start:i]
    fm = re.search(r'"voice_id"\s*:\s*"[^"]*"', block)
    if not fm:
        return None
    new_block = block[:fm.start()] + '"voice_id": ' + json.dumps(vid) + block[fm.end():]
    return text[:start] + new_block + text[i:]


def save_ids(ids, source="voice studio", overwrite=True):
    """Merge {key: voice_id} into voice_map.json and the backup. Empty values
    never erase a saved ID. With overwrite=False an ID already saved for a
    key is kept (the rescue and recovery tools fill gaps only). Returns
    {"set": n, "added": n, "kept": n, "skipped": [...]}."""
    clean = {}
    skipped = []
    for k, v in (ids or {}).items():
        k, v = str(k).strip(), str(v or "").strip()
        if not k or not v:
            continue
        if not VOICE_ID_RE.match(v):
            skipped.append(k)
            continue
        clean[k] = v
    have = load_ids()
    text = MAP_PATH.read_text(encoding="utf-8")
    m = json.loads(text)
    chars = m.setdefault("characters", {})
    res = {"set": 0, "added": 0, "kept": 0, "skipped": skipped}
    added = {}
    for k, v in sorted(clean.items()):
        if have.get(k) == v:
            continue
        if have.get(k) and not overwrite:
            res["kept"] += 1
            continue
        if k in chars and isinstance(chars[k], dict):
            nt = _set_in_text(text, k, v)
            if nt is not None:
                text = nt
                res["set"] += 1
                continue
        added[k] = v
    if added:
        # a key the map does not carry yet (a walk-on the studio met first):
        # rewrite the map as JSON with the key added
        m = json.loads(text)
        chars = m.setdefault("characters", {})
        for k, v in added.items():
            e = chars.get(k) if isinstance(chars.get(k), dict) else {}
            e["voice_id"] = v
            chars[k] = e
            res["added"] += 1
        text = json.dumps(m, indent=2, ensure_ascii=False) + "\n"
    json.loads(text)                      # never write a broken map
    if res["set"] or res["added"]:
        tmp = MAP_PATH.with_suffix(".json.tmp")
        tmp.write_text(text, encoding="utf-8")
        tmp.replace(MAP_PATH)
    snap = load_ids()
    BACKUP_PATH.write_text(json.dumps({"_comment": "voice_ids.py keeps this: the cast's ElevenLabs voice IDs, "
                                       "a flat copy of voice_map.json's voice_id fields. Do not hand-edit.",
                                       "updated": time.strftime("%Y-%m-%d %H:%M:%S"), "source": source,
                                       "ids": dict(sorted(snap.items()))}, indent=2, ensure_ascii=False) + "\n",
                           encoding="utf-8")
    return res
