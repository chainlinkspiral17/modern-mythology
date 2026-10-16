"""Shared helpers for the voice pipeline (stdlib only).

Used by voice_manifest.py, wire_voicelines.py and elevenlabs_render.py so
all three agree on:

  * which files are scenes  - every resources/scenes/vol*/*.json that is a
    dict with "id" and "nodes" (this picks up meld_* scenes; index.json and
    any non-scene JSON are skipped)
  * scene ordering          - alphabetical, or index.json play order
  * character keys          - char_key(), mirrored by charKey() in
                              voice_studio.html.  Keep the two in sync.
  * voice_map.json lookups  - aliases, _walkons groups, scene_aliases,
                              and the _chorus key for multi-speaker lines
  * narrator ids            - narrate lines (and char-less lines) resolve to
                              _narrator_vol{N} from the scene's "vol" field,
                              or _narrator_whispers for vol5_prelude_arcana_ep*;
                              fallback _narrator_vol{N} -> _narrator.
                              (_narrator_vol5 is aliased to _narrator.)

The audio path convention is assets/audio/voice/<scene_id>/<NNN>.<ext>.
"""

import fnmatch
import json
import re
import unicodedata
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent          # godot/
SCENES_ROOT = REPO / "resources" / "scenes"
INDEX_PATH = SCENES_ROOT / "index.json"
VOICE_ROOT = REPO / "assets" / "audio" / "voice"
MAP_PATH = REPO / "tools" / "voice_map.json"
VOICE_KINDS = ("narrate", "say", "think")
AUDIO_EXTS = (".ogg", ".mp3", ".wav")

NARRATOR = "_narrator"
CHORUS = "_chorus"

# ── character keys ──────────────────────────────────────────────────────────

_PAREN_SUFFIX = re.compile(r"\s*\([^()]*\)\s*$")
_MULTI_SPLIT = re.compile(r"\s*(?:,|&|/|\+|\band\b)\s*", re.IGNORECASE)


def char_key(name):
    """Normalise a scene "char" value to a voice_map key.

    lowercase; strip trailing parenthetical suffixes ("Olivia (alternate)");
    drop accents and apostrophes ("Jacob's Son" -> jacobs_son); every other
    non-alphanumeric run -> "_"; collapse/trim underscores.  Empty -> _narrator.
    A leading underscore is preserved so "_narrator"/"_chorus" survive.

    voice_studio.html charKey() implements the same steps - keep them in sync.
    """
    s = (name or "").strip()
    while _PAREN_SUFFIX.search(s):
        s = _PAREN_SUFFIX.sub("", s)
    lead = "_" if s.startswith("_") else ""
    s = unicodedata.normalize("NFKD", s)
    s = "".join(c for c in s if not unicodedata.combining(c)).lower()
    s = re.sub(r"['’]", "", s)
    s = re.sub(r"[^a-z0-9]+", "_", s).strip("_")
    return (lead + s) if s else NARRATOR


def split_speakers(name):
    """'Faust, Jacob, Wagner' -> ['Faust', 'Jacob', 'Wagner'].  One name -> [name]."""
    s = (name or "").strip()
    while _PAREN_SUFFIX.search(s):
        s = _PAREN_SUFFIX.sub("", s)
    parts = [p for p in _MULTI_SPLIT.split(s) if p.strip()]
    return parts or [s]


# ── voice_map.json ──────────────────────────────────────────────────────────

def load_voice_map(path=MAP_PATH):
    if not Path(path).exists():
        raise SystemExit(f"voice_map.json not found at {path}")
    return json.loads(Path(path).read_text())


def alias_table(vmap):
    """Flatten "aliases" + "_walkons" into {normalised name: target key}."""
    out = {}
    for group_key, members in (vmap.get("_walkons") or {}).items():
        if isinstance(members, list):
            for m in members:
                out[char_key(m)] = group_key
    for src, dst in (vmap.get("aliases") or {}).items():
        if isinstance(dst, str):
            out[char_key(src)] = char_key(dst)
    return out


WHISPERS_PREFIX = "vol5_prelude_arcana_ep"   # Whispers from the Liminal episodes
NARRATOR_WHISPERS = "_narrator_whispers"


def narrator_key(scene_id=None, vol=None):
    """Per-volume narrator id: _narrator_whispers for the Whispers episodes,
    else _narrator_vol{N} from the scene's "vol" field, else _narrator.
    voice_studio.html narratorKey() mirrors this."""
    if scene_id and scene_id.startswith(WHISPERS_PREFIX):
        return NARRATOR_WHISPERS
    try:
        return f"{NARRATOR}_vol{int(vol)}"
    except (TypeError, ValueError):
        return NARRATOR


def resolve_char(vmap, char, kind="say", scene_id=None, _aliases=None, vol=None):
    """Map a scene's raw char to a voice_map key.

    Returns (key, fallbacks): fallbacks is an ordered list of other keys to
    try if `key` has no voice_id (_chorus -> named speakers; narrator ids ->
    _narrator_vol{N} -> _narrator).
    Order: narrate / empty char -> narrator_key(); scene_aliases[scene];
    aliases/_walkons; multi-speaker -> _chorus; else the normalised name.
    """
    aliases = _aliases if _aliases is not None else alias_table(vmap)
    if kind == "narrate" or not (char or "").strip():
        nk = narrator_key(scene_id, vol)
        chain = [nk]
        if nk == NARRATOR_WHISPERS and vol is not None:
            chain.append(narrator_key(None, vol))
        chain.append(NARRATOR)
        chain = [aliases.get(k, k) for k in chain]
        dedup = []
        for k in chain:
            if k not in dedup:
                dedup.append(k)
        return dedup[0], dedup[1:]
    k = char_key(char)
    scoped = (vmap.get("scene_aliases") or {}).get(scene_id or "", {})
    scoped = {char_key(a): char_key(b) for a, b in scoped.items()}
    if k in scoped:
        return scoped[k], []
    if k in aliases:
        return aliases[k], []
    speakers = split_speakers(char)
    if len(speakers) > 1:
        fb = []
        for sp in speakers:
            sk = char_key(sp)
            sk = scoped.get(sk, aliases.get(sk, sk))
            if sk not in fb:
                fb.append(sk)
        return CHORUS, fb
    return k, []


def voice_for(vmap, char, kind="say", scene_id=None, _aliases=None, vol=None):
    """Return (resolved_key, voice_id or None, voice_settings or None).

    Tries the resolved key, then its fallbacks (_chorus -> named speakers;
    narrator ids -> _narrator).  A character with NO voice_map entry at all
    falls back to the volume narrator (the old behaviour); a character that
    has an entry with an empty voice_id does not, so nobody gets silently
    rendered in the narrator's voice.
    """
    chars = vmap.get("characters", {})
    aliases = _aliases if _aliases is not None else alias_table(vmap)
    key, fallbacks = resolve_char(vmap, char, kind, scene_id, aliases, vol)
    chain = [key] + fallbacks
    if key not in chars and not fallbacks:
        nk, nfb = resolve_char(vmap, "", "narrate", scene_id, aliases, vol)
        chain += [nk] + nfb
    for k in chain:
        entry = chars.get(k)
        if entry and (entry.get("voice_id") or "").strip():
            settings = dict(vmap.get("default_voice_settings", {}))
            settings.update(entry.get("voice_settings", {}) or {})
            return key, entry["voice_id"].strip(), settings
    return key, None, None


def has_own_voice(vmap, key):
    entry = vmap.get("characters", {}).get(key) or {}
    return bool((entry.get("voice_id") or "").strip())


# ── scene discovery ─────────────────────────────────────────────────────────

def load_scene(path):
    """Return the scene dict, or None if the file isn't a scene."""
    try:
        data = json.loads(Path(path).read_text())
    except (ValueError, OSError):
        return None
    if not isinstance(data, dict) or "id" not in data or not isinstance(data.get("nodes"), list):
        return None
    return data


def load_index():
    try:
        data = json.loads(INDEX_PATH.read_text())
    except (ValueError, OSError):
        return {}
    return data if isinstance(data, dict) else {}


def find_scenes(patterns=None, vol_filter=None, index_order=False):
    """Return [Path] of scene JSONs under resources/scenes/vol*/.

    patterns     - fnmatch globs against the scene id (file stem); empty = all
    vol_filter   - int volume number, or None for every volume
    index_order  - order each volume by index.json play order; scenes not
                   listed in index.json follow, alphabetically
    """
    index = load_index() if index_order else {}
    out = []
    vol_dirs = sorted(SCENES_ROOT.glob("vol*"),
                      key=lambda p: (int(re.sub(r"\D", "", p.name) or 0), p.name))
    for vol_dir in vol_dirs:
        if not vol_dir.is_dir():
            continue
        if vol_filter is not None and vol_dir.name != f"vol{vol_filter}":
            continue
        paths = []
        for path in sorted(vol_dir.glob("*.json")):
            if path.name == "index.json":
                continue
            if patterns and not any(fnmatch.fnmatch(path.stem, p) for p in patterns):
                continue
            if load_scene(path) is None:
                continue
            paths.append(path)
        if index_order:
            order = {sid: i for i, sid in enumerate(index.get(vol_dir.name[3:], []))}
            paths.sort(key=lambda p: (order.get(p.stem, len(order)), p.stem))
        out.extend(paths)
    return out


def scene_vol(path):
    """Folder name, e.g. 'vol4' - used for grouping reports."""
    return Path(path).parent.name


def scene_vol_number(data, path=None):
    """The scene's own "vol" field (meld scenes carry theirs), else the folder."""
    v = (data or {}).get("vol")
    try:
        return int(v)
    except (TypeError, ValueError):
        pass
    if path is not None:
        digits = re.sub(r"\D", "", Path(path).parent.name)
        if digits:
            return int(digits)
    return None


# ── audio on disk ───────────────────────────────────────────────────────────

def voice_path(scene_id, node_index, ext=".ogg"):
    return f"assets/audio/voice/{scene_id}/{node_index:03d}{ext}"


def scan_voice_dir(scene_id):
    """Return {node_index: repo-relative path} for NNN.<ogg|mp3|wav> files.
    When several extensions exist for one index, ogg > mp3 > wav."""
    d = VOICE_ROOT / scene_id
    out = {}
    if not d.is_dir():
        return out
    for f in d.iterdir():
        ext = f.suffix.lower()
        if ext not in AUDIO_EXTS or not f.stem.isdigit():
            continue
        idx = int(f.stem)
        existing = out.get(idx)
        if existing and AUDIO_EXTS.index(ext) > AUDIO_EXTS.index(Path(existing).suffix.lower()):
            continue
        out[idx] = f.relative_to(REPO).as_posix()
    return out
