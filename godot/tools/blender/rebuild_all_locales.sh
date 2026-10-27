#!/usr/bin/env bash
# ════════════════════════════════════════════════════════════════
# rebuild_all_locales.sh — every locale GLB rebuilt from its builder
# (2026-10-27, the user: "give me a full rebuild of assets if it's off
# on my end"). list_stale_builds.sh trusts file times, and a GLB
# pulled from the Drive or copied in looks fresh whatever it holds;
# this rebuilds them all, so the sets on the Deck are exactly what the
# builders say. A failure is logged and the next set built — it never
# stops half way. Then Godot re-imports the models.
#
#   cd godot/tools/blender && ./rebuild_all_locales.sh          # all 160-odd sets (an hour or two)
#   ./rebuild_all_locales.sh cabin kwik_stop cosmic_comics      # only these (names or build_<name>.py)
#   ./rebuild_all_locales.sh --stale                            # only the sets older than their builders
#
# The log of every set is ~/.cache/modern-mythology/rebuild_all.log.
# ════════════════════════════════════════════════════════════════
set -u
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"
chmod +x ./run_cathedral.sh 2>/dev/null || true
LOG="$HOME/.cache/modern-mythology/rebuild_all.log"
mkdir -p "$(dirname "$LOG")"
: > "$LOG"

builders=()
# (2026-10-27) --stale: only the sets whose GLB is older than its builder's last
# commit (stale_sets.py) — the Deck's "thought this was fixed" was a set never rebuilt
if [ "${1:-}" = "--stale" ]; then
  mapfile -t names < <(python3 "$SCRIPT_DIR/stale_sets.py")
  echo "${#names[@]} stale set(s): ${names[*]}"
  set -- "${names[@]}"
  [ "$#" -eq 0 ] && { echo "nothing to rebuild"; exit 0; }
fi
if [ "$#" -gt 0 ]; then
  for a in "$@"; do
    b="${a%.py}"; b="${b#build_}"
    [ -f "locales/build_$b.py" ] && builders+=("build_$b.py") || echo "no builder for $a"
  done
else
  for f in locales/build_*.py; do builders+=("$(basename "$f")"); done
fi

total=${#builders[@]}
ok=0; failed=()
start=$(date +%s)
i=0
for b in "${builders[@]}"; do
  i=$((i + 1))
  printf '[%3d/%3d] %-44s ' "$i" "$total" "$b"
  if ./run_cathedral.sh "$b" >>"$LOG" 2>&1; then
    ok=$((ok + 1)); echo "ok"
  else
    failed+=("$b"); echo "FAILED (see $LOG)"
  fi
done
mins=$(( ($(date +%s) - start) / 60 ))
echo ""
echo "rebuilt $ok of $total set(s) in ${mins} min"
if [ "${#failed[@]}" -gt 0 ]; then
  echo "FAILED: ${failed[*]}"
  echo "(the log: $LOG — send it over)"
fi
echo "re-importing the models in Godot …"
bash "$SCRIPT_DIR/../reimport_models.sh" || echo "re-import did not run — open the project in Godot once"
