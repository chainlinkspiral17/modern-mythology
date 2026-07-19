#!/usr/bin/env bash
## Build the Steam Machine release of Modern Mythology.
##
## Exports the "SteamMachine" preset (single self-contained
## x86_64 binary, PCK embedded) to <repo>/builds/steam_machine/.
## Run from anywhere:
##
##   ./godot/tools/build_steam_machine.sh
##
## Requirements on the build box (Deck or the Steam Machine itself):
##   · Godot 4.6 editor binary (set GODOT_BIN, or have godot4 /
##     godot on PATH, or the Flatpak org.godotengine.Godot)
##   · matching export templates installed once via
##     Editor → Manage Export Templates → Download and Install
##
## Then on the Steam Machine: Steam → Add a Non-Steam Game →
## browse to builds/steam_machine/ModernMythology.x86_64.
## Controller + haptics notes: lore/_CONTROLLER_STEAM_PLAYBOOK.md.

set -euo pipefail

ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
OUT_DIR="$ROOT/builds/steam_machine"

find_godot() {
	if [ -n "${GODOT_BIN:-}" ] && command -v "$GODOT_BIN" >/dev/null 2>&1; then
		echo "$GODOT_BIN"; return
	fi
	for c in godot4 godot godot4.6 godot-4; do
		if command -v "$c" >/dev/null 2>&1; then
			echo "$c"; return
		fi
	done
	if command -v flatpak >/dev/null 2>&1 \
			&& flatpak info org.godotengine.Godot >/dev/null 2>&1; then
		echo "flatpak run org.godotengine.Godot"; return
	fi
	echo ""
}

GODOT="$(find_godot)"
if [ -z "$GODOT" ]; then
	echo "error: no Godot binary found. Set GODOT_BIN=/path/to/godot and retry." >&2
	exit 1
fi

mkdir -p "$OUT_DIR"
echo "· exporting SteamMachine preset with: $GODOT"
# One import pass first so a fresh clone has its .godot cache built
# before the headless export reads it.
$GODOT --headless --path "$ROOT/godot" --import || true
$GODOT --headless --path "$ROOT/godot" --export-release "SteamMachine" \
	"$OUT_DIR/ModernMythology.x86_64"

chmod +x "$OUT_DIR/ModernMythology.x86_64" 2>/dev/null || true
echo ""
echo "· done → $OUT_DIR/ModernMythology.x86_64"
echo "· Steam → Add a Non-Steam Game → browse to that binary."
echo "· First run defaults to fullscreen; window mode lives in SETTINGS."
