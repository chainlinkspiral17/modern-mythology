#!/usr/bin/env python3
"""Render voice lines via ElevenLabs and drop them where wire_voicelines.py expects.

For each voiceable node (narrate/say/think) in the targeted scenes:
  - look up the character's voice_id in voice_map.json
  - POST text → ElevenLabs (PCM 44.1 kHz, eleven_v3 by default)
  - re-encode the PCM to .ogg via local ffmpeg
  - save to assets/audio/voice/<scene_id>/<NNN>.ogg

Then run wire_voicelines.py to inject the "voice" keys into the scene
JSONs. Skips lines whose target file already exists unless --overwrite.

Requirements:
  - ELEVENLABS_API_KEY env var
  - ffmpeg on PATH (PCM → ogg re-encode)
  - urllib (stdlib), no third-party deps

Usage:
  python3 tools/elevenlabs_render.py vol5_ch0_booth6
  python3 tools/elevenlabs_render.py vol5_ch0_* --kind say think
  python3 tools/elevenlabs_render.py --vol 5 --dry-run
  python3 tools/elevenlabs_render.py vol5_ch0_booth6 --node 14 --overwrite
"""

import argparse
import fnmatch
import json
import os
import shutil
import subprocess
import sys
import time
import urllib.error
import urllib.request
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
SCENES_ROOT = REPO / "resources" / "scenes"
VOICE_ROOT = REPO / "assets" / "audio" / "voice"
MAP_PATH = REPO / "tools" / "voice_map.json"
VOICE_KINDS = {"narrate", "say", "think"}

ELEVEN_BASE = "https://api.elevenlabs.io/v1/text-to-speech"
OUTPUT_FORMAT = "pcm_44100"  # then re-encoded to ogg
PCM_SAMPLE_RATE = 44100
PCM_CHANNELS = 1
PCM_SAMPLE_FMT = "s16le"


def load_voice_map():
    if not MAP_PATH.exists():
        sys.exit(f"voice_map.json not found at {MAP_PATH}")
    return json.loads(MAP_PATH.read_text())


def get_api_key():
    k = os.environ.get("ELEVENLABS_API_KEY", "").strip()
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


def find_scenes(patterns, vol_filter):
    out = []
    for vol_dir in sorted(SCENES_ROOT.glob("vol*")):
        if vol_filter is not None and vol_dir.name != f"vol{vol_filter}":
            continue
        for path in sorted(vol_dir.glob("vol*.json")):
            if patterns and not any(fnmatch.fnmatch(path.stem, p) for p in patterns):
                continue
            out.append(path)
    return out


def voice_lookup(vmap, char):
    """Return (voice_id, voice_settings_dict). Falls back to _narrator if
    the character has no entry. Errors out if no _narrator either."""
    chars = vmap.get("characters", {})
    key = char.lower() if char else "_narrator"
    entry = chars.get(key) or chars.get("_narrator")
    if entry is None or not entry.get("voice_id"):
        return None, None
    settings = dict(vmap.get("default_voice_settings", {}))
    settings.update(entry.get("voice_settings", {}) or {})
    return entry["voice_id"], settings


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
    data = json.loads(scene_path.read_text())
    scene_id = data.get("id", scene_path.stem)
    for i, node in enumerate(data.get("nodes", [])):
        if only_node is not None and i != only_node:
            continue
        t = node.get("t", "")
        if t not in kinds:
            continue
        char = (node.get("char") or "").strip() or "_narrator"
        if t == "narrate":
            char = "_narrator"
        text = (node.get("text") or "").strip()
        if not text:
            continue
        yield scene_id, i, t, char, text


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("patterns", nargs="*",
                    help="Scene id glob(s), e.g. 'vol5_ch0_*'. Empty matches all.")
    ap.add_argument("--vol", type=int, help="Restrict to one volume number.")
    ap.add_argument("--kind", nargs="+", choices=sorted(VOICE_KINDS),
                    default=sorted(VOICE_KINDS),
                    help="Which line kinds to render. Default: all three.")
    ap.add_argument("--node", type=int,
                    help="Only render this node index (within a single scene).")
    ap.add_argument("--overwrite", action="store_true",
                    help="Re-render even if the target .ogg already exists.")
    ap.add_argument("--dry-run", action="store_true",
                    help="Print what would be rendered without calling the API.")
    ap.add_argument("--model", help="Override model_id from voice_map.json.")
    ap.add_argument("--limit", type=int,
                    help="Stop after this many successful renders (useful for "
                         "a small test batch).")
    args = ap.parse_args()

    vmap = load_voice_map()
    model_id = args.model or vmap.get("model", "eleven_v3")
    kinds = set(args.kind)

    scenes = find_scenes(args.patterns, args.vol)
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
    missing_voices = set()

    for scene_path in scenes:
        for scene_id, idx, kind, char, text in iter_lines(scene_path, kinds, args.node):
            total["queued"] += 1
            out_path = VOICE_ROOT / scene_id / f"{idx:03d}.ogg"

            if out_path.exists() and not args.overwrite:
                total["skipped"] += 1
                continue

            voice_id, settings = voice_lookup(vmap, char)
            if voice_id is None:
                missing_voices.add(char.lower())
                total["missing_voice"] += 1
                continue

            preview = text[:60].replace("\n", " ")
            tag = f"{scene_id}/{idx:03d}  {kind:<7} {char:<10}"
            if args.dry_run:
                print(f"  [DRY] {tag}  {preview!r}")
                total["rendered"] += 1
                continue

            try:
                print(f"  → {tag}  {preview!r}", flush=True)
                pcm = synth_line(api_key, model_id, voice_id, settings, text)
                pcm_to_ogg(pcm, out_path)
                total["rendered"] += 1
            except Exception as e:
                print(f"    ERROR {e}", file=sys.stderr)
                total["errors"] += 1

            if args.limit and total["rendered"] >= args.limit:
                print(f"\nhit --limit {args.limit}, stopping", file=sys.stderr)
                _summary(total, missing_voices)
                return

    _summary(total, missing_voices)


def _summary(total, missing_voices):
    print(
        f"\nsummary: queued={total['queued']} "
        f"rendered={total['rendered']} skipped={total['skipped']} "
        f"missing_voice={total['missing_voice']} errors={total['errors']}",
        file=sys.stderr,
    )
    if missing_voices:
        print(
            "characters without a voice_id in voice_map.json: "
            + ", ".join(sorted(missing_voices)),
            file=sys.stderr,
        )


if __name__ == "__main__":
    main()
