#!/usr/bin/env bash
## Play the game in its OWN window, straight from the checkout (2026-11-08).
##
## Run from the Godot editor, the game plays embedded in the Game tab, and
## window sizes / fullscreen can't change there. This starts it on its own,
## so SCREEN SIZE (720p … ULTRAWIDE, FULLSCREEN) works as in a release.
##
##   bash godot/tools/play.sh                     # the game, its saved window size
##   bash godot/tools/play.sh 3440x1440           # start at a given size
##   bash godot/tools/play.sh fullscreen          # start fullscreen
##
## Finds Godot like build_steam_machine.sh: GODOT_BIN, godot4 / godot on
## PATH, or the Flatpak org.godotengine.Godot.
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/../.." && pwd)"

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
	echo "error: no Godot found. Set GODOT_BIN=/path/to/godot and retry." >&2
	exit 1
fi

ARGS=()
case "${1:-}" in
	"") ;;
	fullscreen) ARGS+=(--fullscreen) ;;
	*x*) ARGS+=(--resolution "$1") ;;
	*) echo "usage: play.sh [WIDTHxHEIGHT | fullscreen]" >&2; exit 1 ;;
esac

echo "· playing with: $GODOT ${ARGS[*]:-}"
# shellcheck disable=SC2086
exec $GODOT --path "$ROOT/godot" "${ARGS[@]}"
