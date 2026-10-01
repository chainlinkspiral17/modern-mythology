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
find_godot() {
	if [ -n "${GODOT_BIN:-}" ] && command -v "$GODOT_BIN" >/dev/null 2>&1; then
		echo "$GODOT_BIN"; return
	fi
	for c in godot4 godot godot4.6 godot-4; do
		if command -v "$c" >/dev/null 2>&1; then echo "$c"; return; fi
	done
	if command -v flatpak >/dev/null 2>&1 \
			&& flatpak info org.godotengine.Godot >/dev/null 2>&1; then
		echo "flatpak run org.godotengine.Godot"; return
	fi
}
GODOT="$(find_godot)"
if [ -z "$GODOT" ]; then
	echo "reimport_models: no Godot found — open the project in the Godot editor once instead (it rescans on open)" >&2
	exit 1
fi
echo "hero models on disk:"
for f in godot/assets/3d/characters/heroes/{john_frank,frasier_temple,elicia_temple,nicola,dante_dambrosio,antonio,alberto}.glb; do
	[ -f "$f" ] && printf "  %-18s %s MB\n" "$(basename "$f" .glb)" "$(( $(stat -c %s "$f") / 1000000 ))"
done
echo "re-importing (this can take a few minutes for big models) …"
$GODOT --headless --path godot --import 2>&1 | grep -iE "error|import|reimport" | tail -20 || true
echo "REIMPORT DONE — run the game; the new models play"
