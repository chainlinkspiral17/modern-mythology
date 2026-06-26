#!/usr/bin/env bash
# Copy 3D models into the previz project and trigger a Godot import.
# Usage:   bash scripts/import-assets.sh "/path/to/your/3D model"
# Example: bash scripts/import-assets.sh "$HOME/Downloads/3D model"
set -uo pipefail

REPO="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
DEST="$REPO/godot/assets/models"
SKY="$REPO/godot/assets/sky"
AUDIO="$REPO/godot/assets/audio/previz"
SRC="${1:-}"
mkdir -p "$DEST" "$SKY" "$AUDIO"

if [ -z "$SRC" ]; then
  echo "usage: bash scripts/import-assets.sh <folder-with-your-assets>"
  echo "  models  -> $DEST"
  echo "  skies   -> $SKY   (.hdr/.exr, or images named dusk/night/disaster)"
  echo "  tracks  -> $AUDIO (.ogg/.wav/.mp3)"
  echo "currently in models:"; ls -la "$DEST"
  exit 1
fi
if [ ! -d "$SRC" ]; then echo "!! not a folder: $SRC"; exit 1; fi

echo ">> models + textures from: $SRC"
find "$SRC" -type f \( -iname '*.glb' -o -iname '*.gltf' -o -iname '*.bin' \
  -o -iname '*.png' -o -iname '*.jpg' -o -iname '*.jpeg' \) -exec cp -v {} "$DEST/" \;

echo ">> audio tracks -> $AUDIO"
find "$SRC" -type f \( -iname '*.ogg' -o -iname '*.wav' -o -iname '*.mp3' \) -exec cp -v {} "$AUDIO/" \;

echo ">> HDR/EXR skyboxes -> $SKY"
find "$SRC" -type f \( -iname '*.hdr' -o -iname '*.exr' \) -exec cp -v {} "$SKY/" \;

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
