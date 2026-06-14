#!/usr/bin/env bash
# ════════════════════════════════════════════════════════════════
# pull_and_build.sh
# Single-shot script for the Steam Deck. Pulls the latest from the
# working branch, rebuilds the riverfront GLB, prints the next steps.
#
# Run from anywhere:
#   ~/Downloads/modern-mythology/pull_and_build.sh
# Or from inside the repo:
#   ./pull_and_build.sh
#
# Pass a script name to build something other than the riverfront:
#   ./pull_and_build.sh build_diner.py
#   ./pull_and_build.sh build_cathedral_interior.py
# ════════════════════════════════════════════════════════════════

set -e

REPO_DIR="${REPO_DIR:-$HOME/Downloads/modern-mythology}"
BRANCH="${BRANCH:-claude/3d-locales}"
TARGET="${1:-build_riverfront.py}"

if [ ! -d "$REPO_DIR" ]; then
  echo "✗ repo not found at $REPO_DIR"
  echo "  set REPO_DIR=/path/to/modern-mythology and re-run, or clone there."
  exit 1
fi

echo "→ repo: $REPO_DIR"
echo "→ branch: $BRANCH"
echo "→ build target: $TARGET"
echo ""

cd "$REPO_DIR"

# 1) Pull latest. Retry up to 4 times with exponential backoff on
#    network errors (matches the project's git pull guidance).
echo "→ pulling latest..."
attempt=1
delay=2
until git pull origin "$BRANCH"; do
  if [ $attempt -ge 4 ]; then
    echo "✗ git pull failed after 4 attempts. fix conflicts / network and retry."
    exit 2
  fi
  echo "  attempt $attempt failed, waiting ${delay}s..."
  sleep "$delay"
  attempt=$((attempt + 1))
  delay=$((delay * 2))
done
echo ""

# 2) Build the GLB via the existing runner (auto-detects Blender,
#    handles Flatpak / Steam / AppImage / PATH).
echo "→ running blender build..."
cd "$REPO_DIR/godot/tools/blender"
./run_cathedral.sh "$TARGET"
echo ""

# 3) Tell the user where the output lives and what to open.
GLB_DIR="$REPO_DIR/godot/assets/3d/locales"
case "$TARGET" in
  build_riverfront.py)   SCENE="scenes/locales/riverfront.tscn" ;;
  build_diner.py)        SCENE="scenes/locales/diner.tscn" ;;
  build_cathedral_interior.py) SCENE="scenes/warehouse.tscn" ;;
  *) SCENE="(scene unknown — pick from godot/scenes/)" ;;
esac

echo "════════════════════════════════════════════════════════════"
echo " done."
echo "  GLBs in:        $GLB_DIR"
echo "  open in Godot:  $SCENE"
echo "  F6 to play · F3 to cycle moods · F1 toggles noclip"
echo "════════════════════════════════════════════════════════════"
