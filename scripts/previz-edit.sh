#!/usr/bin/env bash
# Open the Godot EDITOR on the previz project, with the Previz scene loaded.
# The editor imports any new .glb on open, so this also doubles as the import
# step. Inside: press F6 (or the ▶ Play Scene button) to run the level.
# Usage:  bash scripts/previz-edit.sh
# Override Godot:  GODOT=/path/to/godot bash scripts/previz-edit.sh
set -uo pipefail

REPO="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
. "$(dirname "${BASH_SOURCE[0]}")/_canon_guard.sh"
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
echo ">> launching the RUNNING scene (background)…"
$GODOT --path "$REPO/godot" scenes/previz/Previz.tscn &
SCENE_PID=$!
sleep 2
echo ">> opening the EDITOR (foreground; alt-tab to the running scene window)…"
$GODOT --editor --path "$REPO/godot" scenes/previz/Previz.tscn
# when you close the editor, also stop the running scene
kill "$SCENE_PID" 2>/dev/null || true
