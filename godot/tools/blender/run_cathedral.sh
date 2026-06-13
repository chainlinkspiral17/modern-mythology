#!/usr/bin/env bash
# ════════════════════════════════════════════════════════════════
# run_cathedral.sh
# auto-detects Blender (Steam · Flatpak · AppImage · PATH) and
# runs build_cathedral_interior.py against it.
#
# from this directory:    ./run_cathedral.sh
# from anywhere:          /home/deck/Downloads/godot/tools/blender/run_cathedral.sh
#
# this script is self-contained. no dependencies beyond bash and
# whichever Blender you've installed.
# ════════════════════════════════════════════════════════════════

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

# pick whichever script the user asked for, default to cathedral_interior
TARGET="${1:-build_cathedral_interior.py}"

if [ ! -f "$TARGET" ]; then
  echo "✗ couldn't find $TARGET in $SCRIPT_DIR"
  echo "  available scripts:"
  ls -1 build_*.py 2>/dev/null || echo "    (none yet)"
  exit 1
fi

# ── try to find Blender in common Steam Deck locations ──────────
BLENDER=""

# 1) Blender via Steam (most common on Deck)
for path in \
  "$HOME/.local/share/Steam/steamapps/common/Blender/blender" \
  "$HOME/.steam/steam/steamapps/common/Blender/blender" \
  "/run/media/mmcblk0p1/steamapps/common/Blender/blender" \
  "/run/media/deck/SDCARD/steamapps/common/Blender/blender"
do
  if [ -x "$path" ]; then
    BLENDER="$path"
    echo "→ found Blender via Steam: $BLENDER"
    break
  fi
done

# 2) Blender via Flatpak
if [ -z "$BLENDER" ]; then
  if command -v flatpak >/dev/null 2>&1; then
    if flatpak list --app 2>/dev/null | grep -q "org.blender.Blender"; then
      BLENDER="flatpak run org.blender.Blender"
      echo "→ found Blender via Flatpak: org.blender.Blender"
    fi
  fi
fi

# 3) Blender AppImage in Downloads
if [ -z "$BLENDER" ]; then
  for appimage in "$HOME/Downloads/"blender-*.AppImage "$HOME/Downloads/"Blender-*.AppImage; do
    if [ -x "$appimage" ]; then
      BLENDER="$appimage"
      echo "→ found Blender AppImage: $BLENDER"
      break
    fi
  done
fi

# 4) Blender on PATH
if [ -z "$BLENDER" ]; then
  if command -v blender >/dev/null 2>&1; then
    BLENDER="$(command -v blender)"
    echo "→ found Blender on PATH: $BLENDER"
  fi
fi

# ── no Blender found ───────────────────────────────────────────
if [ -z "$BLENDER" ]; then
  cat <<EOF
✗ couldn't find Blender anywhere standard.

three sane options to install it on Steam Deck:

  A) Steam (recommended on Deck):
       open Steam → search "Blender" in the store → install.
       this script will find it automatically next run.

  B) Flatpak (clean, sandboxed; needs filesystem grant):
       flatpak install flathub org.blender.Blender
       then: flatpak override --user --filesystem=home org.blender.Blender
       (the filesystem grant lets it write the GLB output)

  C) AppImage (no install, just a binary):
       grab the Linux 64-bit AppImage from https://www.blender.org/download/
       save it to ~/Downloads/
       chmod +x ~/Downloads/blender-*.AppImage
       this script will find it automatically next run.

EOF
  exit 2
fi

# ── run it ────────────────────────────────────────────────────
echo "→ running: $TARGET"
echo ""

# Flatpak case needs the command to be parsed
if [[ "$BLENDER" == flatpak* ]]; then
  $BLENDER --background --python "$TARGET"
else
  "$BLENDER" --background --python "$TARGET"
fi

# ── show output ───────────────────────────────────────────────
echo ""
echo "→ done."
OUTPUT_DIR="$SCRIPT_DIR/../../assets/3d"
if [ -d "$OUTPUT_DIR" ]; then
  echo "→ output GLBs in: $OUTPUT_DIR"
  find "$OUTPUT_DIR" -name "*.glb" -printf "    · %P  (%s bytes)\n" 2>/dev/null || \
    find "$OUTPUT_DIR" -name "*.glb" -exec ls -la {} \; 2>/dev/null
fi
