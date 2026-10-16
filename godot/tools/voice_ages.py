#!/usr/bin/env python3
"""voice_ages.py — a character's voice at the age the scene is set (2026-10-16).

The user: "characters need new looks and voices as they age." The age ledger
godot/tools/ages.json lists, for every character who appears in more than
one era, each era's volumes (and scenes, when an era is narrower than a
volume), year, age, look (the roster slug of that age's model) and voice:
{"key": "<base>__<era id>", "casting": "…"}.

era_voice_key(char, scene_id, vol) → the era's voice key, or None when the
character has no ledger entry or no era covers the scene. The renderer
(elevenlabs_render.py) uses that key's voice_id from voice_map.json when one
is cast, and otherwise the character's own voice — so an era with no voice
yet still renders, with the voice it always had.

    python3 godot/tools/voice_ages.py              # every era voice and whether it is cast
    python3 godot/tools/voice_ages.py dickens_dean vol1_ch5_office
"""
import json
import re
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
AGES_PATH = HERE / "ages.json"
MAP_PATH = HERE / "voice_map.json"
_cache = {}


def load_ages():
    if "ages" not in _cache:
        try:
            _cache["ages"] = json.loads(AGES_PATH.read_text())
        except (OSError, ValueError):
            _cache["ages"] = {"characters": {}}
        by_key = {}
        for base, c in (_cache["ages"].get("characters") or {}).items():
            for k in [base] + list(c.get("keys") or []):
                by_key[str(k).lower()] = base
        _cache["by_key"] = by_key
    return _cache["ages"]


def vol_of(scene_id, vol=None):
    if vol is not None:
        return int(vol)
    m = re.match(r"vol(\d+)_", scene_id or "")
    return int(m.group(1)) if m else None


def era_for(char, scene_id, vol=None):
    """The ledger era that covers this character in this scene, or None.
    An era whose `scenes` list names the scene wins. Otherwise the volume
    decides — when exactly one era claims it (an era's scene list says where
    the person appears, it does not fence the era in). Two eras in one
    volume and the scene listed by neither: None, and the renderer keeps the
    character's own voice rather than guess an age."""
    ages = load_ages()
    base = _cache["by_key"].get((char or "").lower())
    if not base:
        return None
    eras = (ages["characters"][base].get("eras") or [])
    for e in eras:
        if scene_id and scene_id in (e.get("scenes") or []):
            return e
    v = vol_of(scene_id, vol)
    if v is None:
        return None
    hits = [e for e in eras if v in (e.get("vols") or [])]
    return hits[0] if len(hits) == 1 else None


def era_voice_key(char, scene_id, vol=None):
    e = era_for(char, scene_id, vol)
    v = (e or {}).get("voice") or {}
    return v.get("key") or None


def main():
    load_ages()
    if len(sys.argv) == 3:
        e = era_for(sys.argv[1], sys.argv[2])
        print(json.dumps(e, indent=1) if e else "no era")
        return 0
    vmap = json.loads(MAP_PATH.read_text()) if MAP_PATH.exists() else {}
    chars = vmap.get("characters", {})
    n = cast = same = 0
    for base, c in sorted(_cache["ages"].get("characters", {}).items()):
        for e in c.get("eras") or []:
            key = ((e.get("voice") or {}).get("key")) or ""
            if not key:
                continue
            v = e.get("voice") or {}
            if key.endswith("__only") or v.get("shares"):
                same += 1                   # keeps the character's own voice (or shares an existing one)
                continue
            n += 1
            ok = bool((chars.get(key) or {}).get("voice_id"))
            cast += ok
            print(f"{'cast ' if ok else 'OPEN '} {key:34s} {e.get('year', '?')!s:>6}  age {e.get('age', '?')!s:<8} "
                  f"{(e.get('voice') or {}).get('casting', '')[:70]}")
    print(f"\n{n} new era voice(s), {cast} cast; {same} era(s) keep an existing voice. Cast one: add \"<key>\": {{\"voice_id\": \"…\"}} under "
          f"\"characters\" in voice_map.json.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
