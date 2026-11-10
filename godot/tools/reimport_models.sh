#!/usr/bin/env bash
# Make Godot pick up changed model files (2026-10-01).
#
# Godot plays a model from its import cache (godot/.godot/imported), not
# from the .glb itself. When a hero GLB is replaced on disk — a Hero
# Studio save, a drive-pull, a recovered model given its name — the game
# keeps showing the OLD model until the editor rescans the project. This
# runs that scan headless, so the next run shows the new models.
#
#   bash godot/tools/reimport_models.sh
set -euo pipefail
cd "$(dirname "$0")/../.."
# the same search tools/play.sh makes: GODOT_BIN, the editor that is running
# now, a Godot on PATH, the Steam install, a download, the Flatpak
GODOT=()
find_godot() {
	if [ -n "${GODOT_BIN:-}" ] && { [ -x "$GODOT_BIN" ] || command -v "$GODOT_BIN" >/dev/null 2>&1; }; then
		GODOT=("$GODOT_BIN"); return
	fi
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
	echo "reimport_models: no Godot found — open the project in the Godot editor once instead (it rescans on open)" >&2
	exit 1
fi
echo "hero models on disk:"
for f in godot/assets/3d/characters/heroes/{john_frank,frasier_temple,elicia_temple,nicola,dante_dambrosio,antonio,alberto}.glb; do
	[ -f "$f" ] && printf "  %-18s %s MB\n" "$(basename "$f" .glb)" "$(( $(stat -c %s "$f") / 1000000 ))"
done
echo "re-importing (this can take a few minutes for big models) …"
"${GODOT[@]}" --headless --path godot --import 2>&1 | grep -iE "error|import|reimport" | tail -20 || true
rm -f godot/.godot/models_changed
echo "REIMPORT DONE — run the game; the new models play"
