#!/usr/bin/env bash
## Play the game in its OWN window, straight from the checkout (2026-11-08).
##
## (2026-11-09, the user: "give me a copy paste that opens a game that
## works.") With no argument it opens FULLSCREEN, the story filling a wide
## screen: the window mode is passed to the game itself (`-- --screen …`,
## read by Settings), so the launch does not depend on what was saved or on
## the Godot editor.
##
##   bash godot/tools/play.sh                # fullscreen, the screen's own size
##   bash godot/tools/play.sh ultrawide      # 3440x1440 (fullscreen on a 3440x1440 screen)
##   bash godot/tools/play.sh 1080p          # 720p | 900p | 1080p | 1440p: a window
##   bash godot/tools/play.sh saved          # whatever Settings last saved
##
## Finds Godot: GODOT_BIN, the Godot editor that is running now, godot4 /
## godot on PATH, the Steam install, a Godot_v4* download in the usual
## folders, or the Flatpak org.godotengine.Godot.
set -uo pipefail
ROOT="$(cd "$(dirname "$0")/../.." && pwd)"

GODOT=()
find_godot() {
	if [ -n "${GODOT_BIN:-}" ] && { [ -x "$GODOT_BIN" ] || command -v "$GODOT_BIN" >/dev/null 2>&1; }; then
		GODOT=("$GODOT_BIN"); return
	fi
	# the editor that is open right now knows where Godot lives
	local pid exe
	for pid in $(pgrep -i godot 2>/dev/null); do
		exe="$(readlink -f "/proc/$pid/exe" 2>/dev/null || true)"
		case "$(basename "${exe:-}")" in
			[Gg]odot*) [ -x "$exe" ] && { GODOT=("$exe"); return; } ;;
		esac
	done
	local c
	for c in godot4 godot godot4.7 godot4.6 godot-4; do
		if command -v "$c" >/dev/null 2>&1; then GODOT=("$c"); return; fi
	done
	local f
	for f in \
		"$HOME/.local/share/Steam/steamapps/common/Godot Engine/godot.x11.opt.tools.64" \
		"$HOME/.steam/steam/steamapps/common/Godot Engine/godot.x11.opt.tools.64" \
		"$HOME"/.local/share/Steam/steamapps/common/Godot*/[Gg]odot*64* \
		"$HOME"/Downloads/Godot_v4*x86_64 "$HOME"/Downloads/*/Godot_v4*x86_64 \
		"$HOME"/Applications/Godot_v4*x86_64 "$HOME"/Applications/Godot*.AppImage \
		"$HOME"/Desktop/Godot_v4*x86_64 "$HOME"/.local/bin/Godot_v4*x86_64 "$HOME"/Godot_v4*x86_64; do
		if [ -f "$f" ] && [ -x "$f" ]; then GODOT=("$f"); return; fi
	done
	if command -v flatpak >/dev/null 2>&1 && flatpak info org.godotengine.Godot >/dev/null 2>&1; then
		GODOT=(flatpak run org.godotengine.Godot); return
	fi
}

find_godot
if [ "${#GODOT[@]}" -eq 0 ]; then
	echo "error: no Godot found. Open the Godot editor once and run this again (it uses the running editor's Godot)," >&2
	echo "       or: GODOT_BIN=/path/to/godot bash godot/tools/play.sh" >&2
	exit 1
fi

MODE="${1:-fullscreen}"
GAME_ARGS=()
case "$MODE" in
	fullscreen|wide)                    GAME_ARGS=(--screen fullscreen) ;;
	ultrawide|720p|900p|1080p|1440p)    GAME_ARGS=(--screen "$MODE") ;;
	saved)                              ;;
	*) echo "usage: play.sh [fullscreen | ultrawide | 1440p | 1080p | 900p | 720p | saved]" >&2; exit 1 ;;
esac

echo "· Godot: ${GODOT[*]}"
echo "· screen: $MODE   (lines starting [ScreenMgr] below say what the window is doing)"
if [ "${#GAME_ARGS[@]}" -gt 0 ]; then
	exec "${GODOT[@]}" --path "$ROOT/godot" -- "${GAME_ARGS[@]}"
fi
exec "${GODOT[@]}" --path "$ROOT/godot"
