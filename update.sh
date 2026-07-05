#!/usr/bin/env bash
# ════════════════════════════════════════════════════════════════
# update.sh — one-shot project updater for the Steam Deck.
#
#   Pulls the latest `main`, then rebuilds every locale GLB from its
#   Blender build script. Safe to re-run; continues past any single
#   build failure and prints a summary at the end.
#
# Usage:
#   ./update.sh              # pull main + rebuild ALL locales
#   ./update.sh --pull-only  # just pull, don't build
#   ./update.sh vol5         # pull + rebuild only locales matching "vol5"
#                            # (matches on the build script filename)
#
# Override the repo location or branch with env vars if needed:
#   REPO_DIR=/path/to/modern-mythology BRANCH=main ./update.sh
# ════════════════════════════════════════════════════════════════

set -uo pipefail

REPO_DIR="${REPO_DIR:-$HOME/Downloads/modern-mythology}"
BRANCH="${BRANCH:-main}"
FILTER=""
PULL_ONLY=0

for arg in "$@"; do
  case "$arg" in
    --pull-only) PULL_ONLY=1 ;;
    --*)         echo "unknown flag: $arg"; exit 1 ;;
    *)           FILTER="$arg" ;;
  esac
done

if [ ! -d "$REPO_DIR/.git" ]; then
  echo "✗ no git repo at $REPO_DIR"
  echo "  set REPO_DIR=/path/to/modern-mythology and re-run."
  exit 1
fi
cd "$REPO_DIR"

# ── 1) Stash any local edits so the pull can't be blocked ─────────
if [ -n "$(git status --porcelain)" ]; then
  echo "→ stashing local changes (recover with: git stash pop)"
  git stash push -u -m "update.sh-$(date +%s)" >/dev/null
fi

# ── 2) Pull the branch, retrying on network errors ────────────────
echo "→ pulling $BRANCH ..."
git checkout "$BRANCH" >/dev/null 2>&1 || { echo "✗ can't checkout $BRANCH"; exit 2; }
attempt=1; delay=2
until git pull origin "$BRANCH"; do
  [ $attempt -ge 4 ] && { echo "✗ git pull failed after 4 tries"; exit 2; }
  echo "  retry $attempt in ${delay}s ..."; sleep "$delay"
  attempt=$((attempt + 1)); delay=$((delay * 2))
done
echo ""

[ "$PULL_ONLY" -eq 1 ] && { echo "✓ pulled. (--pull-only, skipping builds)"; exit 0; }

# ── 3) Rebuild the locale GLBs ────────────────────────────────────
cd "$REPO_DIR/godot/tools/blender"
mapfile -t SCRIPTS < <(find locales -maxdepth 1 -name "build_*.py" -type f -printf '%f\n' | sort)
[ -n "$FILTER" ] && mapfile -t SCRIPTS < <(printf '%s\n' "${SCRIPTS[@]}" | grep -i -- "$FILTER")

total=${#SCRIPTS[@]}
[ "$total" -eq 0 ] && { echo "✗ no locale scripts match '$FILTER'"; exit 1; }
echo "→ building $total locale(s)$([ -n "$FILTER" ] && echo " matching '$FILTER'") ..."
echo ""

ok=0; failed=()
i=0
for s in "${SCRIPTS[@]}"; do
  i=$((i + 1))
  printf "[%2d/%2d] %s\n" "$i" "$total" "$s"
  if ./run_cathedral.sh "$s" >/tmp/build_"$s".log 2>&1; then
    ok=$((ok + 1))
  else
    failed+=("$s")
    echo "        ✗ FAILED — see /tmp/build_$s.log"
  fi
done

# ── 4) Summary ────────────────────────────────────────────────────
echo ""
echo "════════════════════════════════════════════════════════════"
echo " built $ok/$total   ·   GLBs in godot/assets/3d/locales/"
if [ ${#failed[@]} -gt 0 ]; then
  echo " ${#failed[@]} failed:"
  printf '   · %s\n' "${failed[@]}"
  echo " (logs at /tmp/build_<name>.log)"
fi
echo " open a scene in Godot · F6 to play · F3 moods · F1 noclip"
echo "════════════════════════════════════════════════════════════"
