#!/usr/bin/env bash
# ════════════════════════════════════════════════════════════════
# run_sound_studio.sh — start the Sound Studio (or sound_gen.py)
# with its Python dependencies in a private venv, so nothing is
# installed system-wide (SteamOS keeps / read-only).
#
#   ./run_sound_studio.sh                 # open the studio in the browser
#   ./run_sound_studio.sh --status        # outstanding-audio report
#   ./run_sound_studio.sh gen providers   # any sound_gen.py command
#   ./run_sound_studio.sh gen render ../../audio_library/scores/<id>/<file>.score.json
#
# numpy powers the builtin MIDI renderer; anthropic powers the Claude
# composer hook. Both are optional: the studio still runs without them.
# ════════════════════════════════════════════════════════════════
set -uo pipefail

HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
VENV="${MM_SOUND_VENV:-$HOME/.cache/modern-mythology/sound-venv}"
PY="python3"

has() { "$1" -c "import $2" >/dev/null 2>&1; }

if ! command -v python3 >/dev/null 2>&1; then
  echo "✗ python3 not found"; exit 1
fi

if ! { has python3 numpy && has python3 anthropic; }; then
  if [ ! -x "$VENV/bin/python" ]; then
    echo "→ creating a private Python environment at $VENV (first run only)"
    python3 -m venv "$VENV" 2>/dev/null || echo "  (venv unavailable; continuing with system python)"
  fi
  if [ -x "$VENV/bin/python" ]; then
    PY="$VENV/bin/python"
    for pkg in numpy anthropic; do
      if ! has "$PY" "$pkg"; then
        echo "→ installing $pkg"
        "$PY" -m pip install --quiet --disable-pip-version-check "$pkg" \
          || echo "  ($pkg did not install; the hook that needs it stays disabled)"
      fi
    done
  fi
fi

command -v ffmpeg >/dev/null 2>&1 || echo "! ffmpeg not found: rendering and format conversion are disabled until it is installed"

if [ "${1:-}" = "gen" ]; then
  shift
  exec "$PY" "$HERE/sound_gen.py" "$@"
fi
exec "$PY" "$HERE/sound_studio.py" "$@"
