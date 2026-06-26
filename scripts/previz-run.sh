#!/usr/bin/env bash
# Launch the previz scene in a window.
# Usage:  bash scripts/previz-run.sh
# Override Godot:  GODOT=/path/to/godot bash scripts/previz-run.sh
set -uo pipefail

REPO="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
GODOT="${GODOT:-}"
if [ -z "$GODOT" ]; then
  if   command -v godot  >/dev/null 2>&1; then GODOT="godot"
  elif command -v godot4 >/dev/null 2>&1; then GODOT="godot4"
  elif flatpak info org.godotengine.Godot >/dev/null 2>&1; then GODOT="flatpak run org.godotengine.Godot"
  else echo "!! Godot 4 not found — run: GODOT=/path/to/godot bash scripts/previz-run.sh"; exit 1
  fi
fi
echo ">> using: $GODOT"
echo ">> importing project (this can take a bit for .glb — letting it finish)…"
# --quit exits after ONE frame, often BEFORE .glb import finishes (→ models load
# as nothing). --quit-after gives the importer time to complete.
$GODOT --headless --editor --path "$REPO/godot" --quit-after 600 >/dev/null 2>&1 || true
echo ">> launching scene…"
$GODOT --path "$REPO/godot" scenes/previz/Previz.tscn
