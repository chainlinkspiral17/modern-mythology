#!/usr/bin/env bash
# Open the Godot EDITOR on the previz project, with the Previz scene loaded.
# The editor imports any new .glb on open, so this also doubles as the import
# step. Inside: press F6 (or the ▶ Play Scene button) to run the level.
# Usage:  bash scripts/previz-edit.sh
# Override Godot:  GODOT=/path/to/godot bash scripts/previz-edit.sh
set -uo pipefail

REPO="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
GODOT="${GODOT:-}"
if [ -z "$GODOT" ]; then
  if   command -v godot  >/dev/null 2>&1; then GODOT="godot"
  elif command -v godot4 >/dev/null 2>&1; then GODOT="godot4"
  elif flatpak info org.godotengine.Godot >/dev/null 2>&1; then GODOT="flatpak run org.godotengine.Godot"
  else echo "!! Godot 4 not found — run: GODOT=/path/to/godot bash scripts/previz-edit.sh"; exit 1
  fi
fi

echo ">> importing…"
$GODOT --headless --editor --path "$REPO/godot" --quit-after 600 >/dev/null 2>&1 || true
echo ">> opening the EDITOR (hand-edit nodes/scripts) and a RUNNING scene window…"
$GODOT --editor --path "$REPO/godot" scenes/previz/Previz.tscn &
sleep 2
$GODOT --path "$REPO/godot" scenes/previz/Previz.tscn
