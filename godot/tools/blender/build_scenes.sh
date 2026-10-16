#!/usr/bin/env bash
# ════════════════════════════════════════════════════════════════
# build_scenes.sh  —  rebuild EVERY scene GLB the game uses.
#
# WHY THIS EXISTS: build_all.sh only builds the Cathedral scene's
# 5-script asset set. It does NOT touch the ~70 locale builds
# (diner, bungalow, riverfront, cabin, ...). So a change to
# build_diner.py stayed invisible after build_all.sh — the diner
# GLB was never rebuilt. This script builds the cathedral set AND
# every locales/build_*.py in one pass, so `git pull` + this =
# every scene current.
#
# Usage (Steam Deck):
#   cd /home/deck/Downloads/modern-mythology/godot/tools/blender
#   ./build_scenes.sh              # everything
#   ./build_scenes.sh diner        # just scripts matching 'diner'
#
# Uses run_cathedral.sh for Blender detection. Continues past a
# failing script and prints a summary of OK / FAILED at the end so
# one bad build never hides the rest.
# ════════════════════════════════════════════════════════════════
set -u
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"
chmod +x ./run_cathedral.sh 2>/dev/null || true

FILTER="${1:-}"

# Cathedral-scene asset set (same list as build_all.sh) + every
# locale build script. De-duplicated, order: cathedral set first.
CATHEDRAL_SET=(
  build_cathedral_interior.py
  build_workbench_props.py
  build_agent_figurines.py
  build_regional_dioramas.py
  build_atmosphere_props.py
)

mapfile -t LOCALE_SET < <(find locales -maxdepth 1 -name 'build_*.py' -type f -printf '%f\n' 2>/dev/null | sort)

ALL=("${CATHEDRAL_SET[@]}" "${LOCALE_SET[@]}")

OK=()
FAILED=()
for script in "${ALL[@]}"; do
  if [ -n "$FILTER" ] && [[ "$script" != *"$FILTER"* ]]; then
    continue
  fi
  echo ""
  echo "═══ $script ═══"
  if ./run_cathedral.sh "$script" >/tmp/build_scenes_last.log 2>&1; then
    # surface the export line so the user sees the GLB written
    grep -E 'exporting to|\.glb' /tmp/build_scenes_last.log | tail -1
    OK+=("$script")
  else
    echo "✗ FAILED — last lines:"
    tail -6 /tmp/build_scenes_last.log | sed 's/^/    /'
    FAILED+=("$script")
  fi
done

echo ""
echo "════════════════════════════════════════════════"
echo "  built OK : ${#OK[@]}"
echo "  FAILED   : ${#FAILED[@]}"
if [ "${#FAILED[@]}" -gt 0 ]; then
  printf '    ✗ %s\n' "${FAILED[@]}"
  echo "  (full log of the last build: /tmp/build_scenes_last.log)"
fi
echo "════════════════════════════════════════════════"
