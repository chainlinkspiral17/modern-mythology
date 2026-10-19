#!/usr/bin/env python3
"""Render voice lines via ElevenLabs and drop them where wire_voicelines.py expects.

For each voiceable node (narrate/say/think) in the targeted scenes:
  - resolve the character to a voice_map.json key (same rules as
    voice_manifest.py, see voice_common.py): normalised name, scene_aliases,
    aliases, _walkons groups; multi-speaker lines ("Faust, Jacob, Wagner")
    -> _chorus, falling back to the first named speaker with a voice_id;
    narrate lines -> _narrator_vol{N} (scene "vol" field) or
    _narrator_whispers for vol5_prelude_arcana_ep*, falling back to _narrator.
    Characters with no voice_map entry at all fall back to the narrator.
  - look up the voice_id + voice_settings
  - POST text → ElevenLabs (PCM 44.1 kHz, eleven_v3 by default)
  - re-encode the PCM to .ogg via local ffmpeg
  - save to assets/audio/voice/<scene_id>/<NNN>.ogg

Then run wire_voicelines.py to inject the "voice" keys into the scene
JSONs. Skips lines whose target file already exists unless --overwrite.

Requirements:
  - ELEVENLABS_API_KEY env var
  - ffmpeg on PATH (PCM → ogg re-encode)
  - urllib (stdlib), no third-party deps

Scenes are every resources/scenes/vol*/*.json with "id" and "nodes"
(meld_* included). With --vol they run in index.json play order (--alpha
to override).

--dry-run needs no API key, no ffmpeg and no network: it prints each line
with its resolved voice key and whether that key has a voice_id yet.

Usage:
  python3 tools/elevenlabs_render.py vol5_ch0_booth6
  python3 tools/elevenlabs_render.py vol5_ch0_* --kind say think
  python3 tools/elevenlabs_render.py --vol 1 --dry-run
  python3 tools/elevenlabs_render.py 'vol5_prelude_arcana_*' --dry-run
  python3 tools/elevenlabs_render.py 'meld_*' --dry-run
  python3 tools/elevenlabs_render.py vol5_ch0_booth6 --node 14 --overwrite
"""

import argparse
import collections
import json
import os
import shutil
import subprocess
import sys
import time
import urllib.error
import urllib.request

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import voice_ages  # noqa: E402 — the age ledger's era voices
from pathlib import Path

import voice_common as vc

REPO = vc.REPO
VOICE_ROOT = vc.VOICE_ROOT
VOICE_KINDS = set(vc.VOICE_KINDS)

ELEVEN_BASE = "https://api.elevenlabs.io/v1/text-to-speech"
OUTPUT_FORMAT = "pcm_44100"  # then re-encoded to ogg
PCM_SAMPLE_RATE = 44100
PCM_CHANNELS = 1
PCM_SAMPLE_FMT = "s16le"


def load_voice_map():
    return vc.load_voice_map()


def get_api_key():
    k = os.environ.get("ELEVENLABS_API_KEY", "").strip()
    kf = Path(__file__).resolve().parent / ".elevenlabs_key"      # voice_recover.py keeps it here (git ignores it)
    if not k and kf.exists():
        k = kf.read_text(encoding="utf-8").strip()
    if not k:
        sys.exit("ELEVENLABS_API_KEY env var not set.\n"
                 "  export ELEVENLABS_API_KEY=sk_...")
    return k


def require_ffmpeg():
    if shutil.which("ffmpeg") is None:
        sys.exit("ffmpeg not found on PATH.\n"
                 "  macOS:    brew install ffmpeg\n"
                 "  Debian:   apt install ffmpeg\n"
                 "  Windows:  https://ffmpeg.org/download.html")


def find_scenes(patterns, vol_filter, index_order=False):
    return vc.find_scenes(patterns, vol_filter, index_order)


def voice_lookup(vmap, char, kind="say", scene_id=None, aliases=None, vol=None):
    """Return (voice_key, voice_id, voice_settings_dict); voice_id/settings are
    None when neither the key nor any of its fallbacks has a voice_id.
    (2026-10-16) A character's voice at the age the scene is set: when the
    age ledger (ages.json, voice_ages.py) puts this scene in one of the
    character's eras and that era's key is cast in voice_map.json, the era's
    voice overrides the base casting; settings layer base-then-era."""
    key, voice_id, settings = vc.voice_for(vmap, char, kind, scene_id, aliases, vol)
    era_key = voice_ages.era_voice_key(key, scene_id) if (key and scene_id) else None
    era = vmap.get("characters", {}).get(era_key) if era_key else None
    if era and era.get("voice_id"):
        merged = dict(settings or {})
        merged.update(era.get("voice_settings", {}) or {})
        return key, era["voice_id"], merged
    return key, voice_id, settings


def synth_line(api_key, model_id, voice_id, settings, text):
    """Call ElevenLabs TTS. Returns raw PCM bytes."""
    url = f"{ELEVEN_BASE}/{voice_id}?output_format={OUTPUT_FORMAT}"
    body = json.dumps({
        "text": text,
        "model_id": model_id,
        "voice_settings": settings,
    }).encode("utf-8")
    req = urllib.request.Request(url, data=body, method="POST", headers={
        "Accept": "audio/pcm",
        "Content-Type": "application/json",
        "xi-api-key": api_key,
    })
    # 5xx and 429 → retry up to 4× with exponential backoff
    delay = 2
    last_err = None
    for attempt in range(4):
        try:
            with urllib.request.urlopen(req, timeout=120) as resp:
                return resp.read()
        except urllib.error.HTTPError as e:
            last_err = e
            if e.code in (429, 500, 502, 503, 504) and attempt < 3:
                time.sleep(delay)
                delay *= 2
                continue
            # surface the API error body for diagnostic clarity
            try:
                detail = e.read().decode("utf-8", "replace")[:500]
            except Exception:
                detail = ""
            raise RuntimeError(f"ElevenLabs HTTP {e.code}: {detail}") from e
        except urllib.error.URLError as e:
            last_err = e
            if attempt < 3:
                time.sleep(delay)
                delay *= 2
                continue
            raise
    raise RuntimeError(f"ElevenLabs failed after retries: {last_err}")


def pcm_to_ogg(pcm: bytes, out_path: Path) -> None:
    out_path.parent.mkdir(parents=True, exist_ok=True)
    cmd = [
        "ffmpeg", "-y", "-loglevel", "error",
        "-f", PCM_SAMPLE_FMT,
        "-ar", str(PCM_SAMPLE_RATE),
        "-ac", str(PCM_CHANNELS),
        "-i", "pipe:0",
        "-c:a", "libvorbis", "-q:a", "5",
        str(out_path),
    ]
    p = subprocess.run(cmd, input=pcm, capture_output=True)
    if p.returncode != 0:
        raise RuntimeError(f"ffmpeg failed: {p.stderr.decode('utf-8', 'replace')[:500]}")


def iter_lines(scene_path, kinds, only_node):
    data = vc.load_scene(scene_path) or {}
    scene_id = data.get("id", scene_path.stem)
    vol = vc.scene_vol_number(data, scene_path)
    for i, node in enumerate(data.get("nodes", [])):
        if only_node is not None and i != only_node:
            continue
        t = node.get("t", "")
        if t not in kinds:
            continue
        char = "" if t == "narrate" else (node.get("char") or "").strip()
        text = (node.get("text") or "").strip()
        if not text:
            continue
        yield scene_id, vol, i, t, char, text


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("patterns", nargs="*",
                    help="Scene id glob(s), e.g. 'vol5_ch0_*'. Empty matches all.")
    ap.add_argument("--vol", type=int,
                    help="Restrict to one volume number (implies --index-order).")
    order = ap.add_mutually_exclusive_group()
    order.add_argument("--index-order", dest="index_order", action="store_true", default=None,
                       help="Process scenes in index.json play order (default with --vol).")
    order.add_argument("--alpha", dest="index_order", action="store_false",
                       help="Process scenes alphabetically, even with --vol.")
    ap.add_argument("--kind", nargs="+", choices=sorted(VOICE_KINDS),
                    default=sorted(VOICE_KINDS),
                    help="Which line kinds to render. Default: all three.")
    ap.add_argument("--node", type=int,
                    help="Only render this node index (within a single scene).")
    ap.add_argument("--overwrite", action="store_true",
                    help="Re-render even if audio for the line already exists.")
    ap.add_argument("--dry-run", action="store_true",
                    help="No network, no API key, no ffmpeg: list every line that "
                         "would be rendered with its resolved voice key, marking "
                         "keys that still have no voice_id.")
    ap.add_argument("--model", help="Override model_id from voice_map.json.")
    ap.add_argument("--limit", type=int,
                    help="Stop after this many successful renders (useful for "
                         "a small test batch).")
    args = ap.parse_args()

    vmap = load_voice_map()
    aliases = vc.alias_table(vmap)
    model_id = args.model or vmap.get("model", "eleven_v3")
    kinds = set(args.kind)

    index_order = args.index_order if args.index_order is not None else args.vol is not None
    scenes = find_scenes(args.patterns, args.vol, index_order)
    if not scenes:
        sys.exit("no scenes matched")
    if args.node is not None and len(scenes) != 1:
        sys.exit(f"--node requires exactly one scene to be matched (got {len(scenes)})")

    if not args.dry_run:
        api_key = get_api_key()
        require_ffmpeg()
    else:
        api_key = ""  # unused

    total = {"queued": 0, "rendered": 0, "skipped": 0,
             "missing_voice": 0, "errors": 0}
    missing_voices = collections.Counter()

    for scene_path in scenes:
        existing = None
        for scene_id, vol, idx, kind, char, text in iter_lines(scene_path, kinds, args.node):
            total["queued"] += 1
            out_path = VOICE_ROOT / scene_id / f"{idx:03d}.ogg"
            if existing is None:
                existing = vc.scan_voice_dir(scene_id)   # any of ogg/mp3/wav

            if idx in existing and not args.overwrite:
                total["skipped"] += 1
                continue

            key, voice_id, settings = voice_lookup(vmap, char, kind, scene_id, aliases, vol)
            preview = text[:60].replace("\n", " ")
            who = char or key
            if vc.char_key(who) != key:
                who = f"{who}->{key}"
            tag = f"{scene_id}/{idx:03d}  {kind:<7} {who:<14}"

            if voice_id is None:
                missing_voices[key] += 1
                total["missing_voice"] += 1
                if args.dry_run:
                    print(f"  [DRY no voice_id] {tag}  {preview!r}")
                continue

            if args.dry_run:
                print(f"  [DRY] {tag}  {preview!r}")
                total["rendered"] += 1
                continue

            try:
                print(f"  → {tag}  {preview!r}", flush=True)
                spoken = vc.speakable_text(text)
                if not spoken:
                    total["skipped"] += 1
                    print(f"  [nothing to speak] {tag}  {preview!r}")
                    continue
                pcm = synth_line(api_key, model_id, voice_id, settings, spoken)
                pcm_to_ogg(pcm, out_path)
                total["rendered"] += 1
            except Exception as e:
                print(f"    ERROR {e}", file=sys.stderr)
                total["errors"] += 1

            if args.limit and total["rendered"] >= args.limit:
                print(f"\nhit --limit {args.limit}, stopping", file=sys.stderr)
                _summary(total, missing_voices, args.dry_run)
                return

    _summary(total, missing_voices, args.dry_run)


def _summary(total, missing_voices, dry_run=False):
    label = "would render" if dry_run else "rendered"
    print(
        f"\nsummary: queued={total['queued']} "
        f"{label}={total['rendered']} skipped(existing audio)={total['skipped']} "
        f"missing_voice={total['missing_voice']} errors={total['errors']}",
        file=sys.stderr,
    )
    if missing_voices:
        print(
            "voice_map keys without a voice_id (lines): "
            + ", ".join(f"{k} {n}" for k, n in missing_voices.most_common()),
            file=sys.stderr,
        )


if __name__ == "__main__":
    main()
