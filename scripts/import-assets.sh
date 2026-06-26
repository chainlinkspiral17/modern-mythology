#!/usr/bin/env bash
# Copy 3D models into the previz project and trigger a Godot import.
# Usage:   bash scripts/import-assets.sh "/path/to/your/3D model"
# Example: bash scripts/import-assets.sh "$HOME/Downloads/3D model"
set -uo pipefail

REPO="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
DEST="$REPO/godot/assets/models"
SRC="${1:-}"
mkdir -p "$DEST"

if [ -z "$SRC" ]; then
  echo "usage: bash scripts/import-assets.sh <folder-with-your-.glb-files>"
  echo "models go into: $DEST"
  echo "currently there:"; ls -la "$DEST"
  exit 1
fi

echo ">> copying models from: $SRC"
find "$SRC" -type f \( -iname '*.glb' -o -iname '*.gltf' -o -iname '*.bin' \
  -o -iname '*.png' -o -iname '*.jpg' -o -iname '*.jpeg' \) -exec cp -v {} "$DEST/" \;

echo ">> now in $DEST:"; ls -la "$DEST"

# auto-wire the two specially-named models
[ -f "$DEST/barn hanger.glb" ] && echo ">> hangar will auto-load (barn hanger.glb found)"
[ -f "$DEST/helicopter.glb" ] && echo ">> helicopter will auto-load (helicopter.glb found)"

# trigger Godot's importer so the .glb become usable resources
GODOT="${GODOT:-}"
if [ -z "$GODOT" ]; then
  if   command -v godot  >/dev/null 2>&1; then GODOT="godot"
  elif command -v godot4 >/dev/null 2>&1; then GODOT="godot4"
  elif flatpak info org.godotengine.Godot >/dev/null 2>&1; then GODOT="flatpak run org.godotengine.Godot"
  fi
fi
if [ -n "$GODOT" ]; then
  echo ">> importing (headless)…"
  $GODOT --headless --editor --path "$REPO/godot" --quit >/dev/null 2>&1 || true
  echo ">> done."
else
  echo ">> Godot not found — open the project in the editor once to import."
fi

echo ">> Characters: add a model path in godot/scenes/previz/data/characters.json, e.g."
echo '     "model": "res://assets/models/nono.glb"'
