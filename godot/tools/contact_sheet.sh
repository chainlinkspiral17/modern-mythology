#!/usr/bin/env bash
# ════════════════════════════════════════════════════════════════
# contact_sheet.sh — THE LENS. Render every VN framing to a file.
#
# Runs tools/VnContactSheet.tscn: one frame per preset × mood, one per
# marker, one per hero GLB × expression, into godot/qa/contact/. Needs
# a display and the locale GLBs built (list_stale_builds.sh first).
#
#   ./godot/tools/contact_sheet.sh                # everything (~1,600 frames)
#   ./godot/tools/contact_sheet.sh --only=cabin   # presets starting with "cabin"
#   ./godot/tools/contact_sheet.sh --png          # lossless frames
#
# Then ./godot/tools/contact_push.sh to hand the frames to Claude.
# ════════════════════════════════════════════════════════════════
set -euo pipefail
HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT="$HERE/.."

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
	echo ""
}

GODOT="$(find_godot)"
if [ -z "$GODOT" ]; then
	echo "contact_sheet: no Godot binary found (set GODOT_BIN, or install godot4 / the Flatpak)" >&2
	exit 1
fi
if [ ! -f "$PROJECT/qa/contact_manifest.json" ]; then
	echo "contact_sheet: qa/contact_manifest.json missing — pull, or run tools/audit/contact_manifest.py" >&2
	exit 1
fi
echo "contact_sheet: $GODOT · $(python3 -c "import json;print(json.load(open('$PROJECT/qa/contact_manifest.json'))['frames'])" 2>/dev/null || echo '?') frame(s) planned"
cd "$PROJECT"
# Import first (2026-09-24): running the project does NOT import new or
# changed GLBs — only the editor or --import does — so a locale built
# since the editor last opened is "not built" to the sheet (highway 101
# and small wood road were skipped on the 09-24 sheet). --import brings
# every GLB in, then quits.
# shellcheck disable=SC2086
$GODOT --headless --path . --import >/dev/null 2>&1 || echo "contact_sheet: --import step failed (continuing with what is imported)" >&2
# shellcheck disable=SC2086
$GODOT --path . res://tools/VnContactSheet.tscn -- "$@"
echo
echo "frames: $PROJECT/qa/contact  ·  report: $PROJECT/qa/contact/_report.json"
[ -f "$PROJECT/qa/contact/_report.json" ] && python3 - "$PROJECT/qa/contact/_report.json" <<'EOF'
import json, sys
r = json.load(open(sys.argv[1]))
print("captured %d · presets %d · heroes %d · skipped GLB %d · skipped marker %d · %.0f s"
      % (r.get("captured", 0), r.get("presets", 0), r.get("heroes", 0),
         len(r.get("skipped_glb", [])), len(r.get("skipped_marker", [])), r.get("seconds", 0)))
if r.get("skipped_glb"):
    print("  not built:", ", ".join(r["skipped_glb"][:20]), "…" if len(r["skipped_glb"]) > 20 else "")
EOF
