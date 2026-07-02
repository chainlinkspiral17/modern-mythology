#!/usr/bin/env bash
# Pull the previz branch and headlessly validate the Godot scripts.
# Usage:  bash scripts/previz-check.sh        (or ./scripts/previz-check.sh)
# Override Godot:  GODOT=/path/to/godot bash scripts/previz-check.sh
set -uo pipefail

REPO="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
BRANCH="claude/sweet-faraday-f6uvba"
cd "$REPO" || exit 1
echo ">> repo: $REPO"

# get latest (skip if you have local uncommitted edits)
git fetch origin "$BRANCH" && git checkout "$BRANCH" && git pull --ff-only origin "$BRANCH" || \
  echo "!! git update skipped/failed (local changes?) — continuing with what's on disk"

# locate Godot 4 (env override wins)
GODOT="${GODOT:-}"
if [ -z "$GODOT" ]; then
  if   command -v godot  >/dev/null 2>&1; then GODOT="godot"
  elif command -v godot4 >/dev/null 2>&1; then GODOT="godot4"
  elif flatpak info org.godotengine.Godot >/dev/null 2>&1; then GODOT="flatpak run org.godotengine.Godot"
  else echo "!! Godot 4 not found — install it or run: GODOT=/path/to/godot bash scripts/previz-check.sh"; exit 1
  fi
fi
echo ">> using: $GODOT"

# headless editor import: scans the project, resolves class_names, prints script errors
LOG=/tmp/previz_import.log
$GODOT --headless --editor --path "$REPO/godot" --quit >"$LOG" 2>&1 || true

echo "----- script errors (empty = clean) -----"
grep -iE 'SCRIPT ERROR|Parse Error|error at|expected|not declared|Invalid call|Identifier .* not' "$LOG" || echo "  none found"
echo "------------------------------------------"
echo "(full log: $LOG)"
