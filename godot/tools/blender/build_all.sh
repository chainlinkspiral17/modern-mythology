#!/usr/bin/env bash
# ════════════════════════════════════════════════════════════════
# build_all.sh
# Runs every Blender build script in sequence, producing all the
# GLBs needed for the COMMUNITY PLANNED Cathedral scene.
#
# Uses run_cathedral.sh as the Blender-detection wrapper so the
# Steam Deck / Flatpak / AppImage paths all work.
#
# from this directory:    ./build_all.sh
# ════════════════════════════════════════════════════════════════

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

if [ ! -x "./run_cathedral.sh" ]; then
  chmod +x ./run_cathedral.sh 2>/dev/null || true
fi

SCRIPTS=(
  "build_cathedral_interior.py"
  "build_workbench_props.py"
  "build_agent_figurines.py"
  "build_regional_dioramas.py"
  "build_atmosphere_props.py"
)

total=${#SCRIPTS[@]}
failures=0

echo ""
echo "════════════════════════════════════════════════════════════════"
echo "  COMMUNITY PLANNED · BUILDING ALL 3D ASSETS"
echo "  $total scripts to run"
echo "════════════════════════════════════════════════════════════════"

i=0
for script in "${SCRIPTS[@]}"; do
  i=$((i+1))
  echo ""
  echo "─── [$i/$total] $script ──────────────────────────────────────"
  if ./run_cathedral.sh "$script"; then
    echo "    ✓ ok"
  else
    echo "    ✗ FAILED"
    failures=$((failures+1))
  fi
done

echo ""
echo "════════════════════════════════════════════════════════════════"
if [ $failures -eq 0 ]; then
  echo "  ALL $total ASSETS BUILT"
else
  echo "  $failures of $total scripts failed"
fi
echo "════════════════════════════════════════════════════════════════"

echo ""
echo "Output GLBs:"
OUTPUT_BASE="$SCRIPT_DIR/../../assets/3d"
if [ -d "$OUTPUT_BASE" ]; then
  find "$OUTPUT_BASE" -name "*.glb" -printf "    · %P  (%s bytes)\n" 2>/dev/null || \
    find "$OUTPUT_BASE" -name "*.glb"
fi

exit $failures
