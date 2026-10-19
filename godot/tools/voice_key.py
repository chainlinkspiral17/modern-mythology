#!/usr/bin/env python3
"""voice_key — keep the ElevenLabs API key on THIS machine for the voice
studio (2026-10-19).

The user: "I reloaded and it didn't keep the key. seriously, I need these
stored locally." The studio's key box was never saved: every reload asked
again. The key now lives in two gitignored files next to the tools:

  godot/tools/.elevenlabs_key      — the key (elevenlabs_render.py and
                                     voice_recover.py read it too)
  godot/tools/.elevenlabs_key.js   — the same key as a script, which the
                                     voice studio loads even when it is
                                     opened as a file (a file:// page may
                                     load a <script src>, not read a file)

Neither is ever committed (.gitignore: godot/tools/.*_key, .*_key.js).

    python3 godot/tools/voice_key.py           # write the .js from the saved key
    python3 godot/tools/voice_key.py --set     # paste a new key (not shown)

Hero Studio's voice studio page saves a key typed into it the same way.
Stdlib only.
"""
import argparse
import getpass
import json
import os
import sys
from pathlib import Path

TOOLS = Path(__file__).resolve().parent
KEY_FILE = TOOLS / ".elevenlabs_key"
JS_FILE = TOOLS / ".elevenlabs_key.js"


def _private(p):
    try:
        os.chmod(p, 0o600)
    except OSError:
        pass


def load():
    k = os.environ.get("ELEVENLABS_API_KEY", "").strip()
    if not k and KEY_FILE.exists():
        k = KEY_FILE.read_text(encoding="utf-8").strip()
    return k


def save(key):
    """Write the key file and its script twin. Returns the key."""
    k = (key or "").strip()
    if not k.startswith("sk_"):
        raise ValueError("an ElevenLabs API key starts with sk_ (the settings page also lists key IDs, "
                         "which are labels, not keys)")
    KEY_FILE.write_text(k + "\n", encoding="utf-8")
    _private(KEY_FILE)
    write_js(k)
    return k


def write_js(key=None):
    k = (key or load()).strip()
    if not k:
        return False
    JS_FILE.write_text("// The ElevenLabs key for the voice studio. Gitignored: never commit.\n"
                       f"window.MM_ELEVEN_KEY = {json.dumps(k)};\n", encoding="utf-8")
    _private(JS_FILE)
    return True


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--set", action="store_true", help="paste a new key")
    args = ap.parse_args()
    if args.set or not load():
        k = getpass.getpass("ElevenLabs API key (sk_…, not shown): ")
        try:
            save(k)
        except ValueError as ex:
            sys.exit(str(ex))
    else:
        write_js()
    print(f"Key kept in {KEY_FILE.name} and {JS_FILE.name} (godot/tools/, gitignored). "
          f"Reload the voice studio.")


if __name__ == "__main__":
    main()
