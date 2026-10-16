#!/usr/bin/env bash
# Render every hero's close-up portrait into one folder, for tuning the
# per-character shading (2026-10-13).
#
#   bash godot/tools/portrait_review.sh                 # → ~/hero_review/<hero>.png
#   bash godot/tools/portrait_review.sh --lift 0.7      # try a shading value on the whole cast
#   bash godot/tools/portrait_review.sh --pairs         # the cast two at a time, as the VN
#                                                       #   shows them (mcu + cu, warm/night/day),
#                                                       #   eye lines and the box top drawn in
#
# Values that suit one hero go into Portrait3D.gd's CHARACTER_SHADING
# (lift, lift_knee, normal_scale, sat, tint, look overrides).
# Tuning flags: --lift --knee --normal --sat. Output folder: OUT=... to change.
set -euo pipefail
cd "$(dirname "$0")/../.."
OUT="${OUT:-$HOME/hero_review}"
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
	echo "portrait_review: no Godot found. Set GODOT_BIN=/path/to/godot and run again." >&2
	exit 1
fi
mkdir -p "$OUT"
BG=""
for c in godot/qa/contact/diner_interior/*.jpg godot/qa/contact/diner_interior/*.png; do
	[ -f "$c" ] && BG="$(realpath "$c")" && break
done
if [ "${1:-}" = "--pairs" ]; then
	shift
	echo "rendering the cast in pairs into $OUT (about 10 s a pair) …"
	$GODOT --path godot --rendering-driver opengl3 --resolution 1280x720 res://tools/PortraitCastSheet.tscn -- \
		--out "$OUT" --shots mcu,cu --lights warm,night,day --guides ${BG:+--bg "$BG"} "$@" 2>&1 \
		| grep -E "PortraitCastSheet|eyes at|model changed|ERROR" || true
	echo "done: $(ls "$OUT"/pair_*.png 2>/dev/null | wc -l) frames in $OUT (eye lines: $OUT/_eyes.json)"
	exit 0
fi
echo "rendering every hero into $OUT (about 15 s a hero) …"
$GODOT --path godot --rendering-driver opengl3 res://tools/PortraitLookTest.tscn -- \
	--all --out "$OUT" ${BG:+--bg "$BG"} "$@" 2>&1 | grep -E "PortraitLookTest|ERROR" || true
echo "done: $(ls "$OUT"/*.png 2>/dev/null | wc -l) portraits in $OUT"
