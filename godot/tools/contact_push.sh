#!/usr/bin/env bash
# ════════════════════════════════════════════════════════════════
# contact_push.sh — hand the contact sheet to Claude.
#
# The frames are a few hundred MB per run and would sink the working
# branch, so they travel on their OWN orphan branch, `qa/contact`,
# re-created and force-pushed every time: no history, one snapshot,
# the working branch untouched (godot/qa/contact/ is gitignored there).
# Claude fetches origin/qa/contact and reads the JPEGs.
#
#   ./godot/tools/contact_push.sh            # push what contact_sheet.sh produced
#
# Decision 4 of lore/_VISUAL_PROGRAM.md §8: if you would rather the
# frames live on the working branch, say so — this script is the
# alternative, not the verdict.
# ════════════════════════════════════════════════════════════════
set -euo pipefail
HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO="$(cd "$HERE/../.." && pwd)"
FRAMES="$REPO/godot/qa/contact"
BRANCH="qa/contact"

if [ ! -d "$FRAMES" ] || [ -z "$(ls -A "$FRAMES" 2>/dev/null)" ]; then
	echo "contact_push: nothing in $FRAMES — run contact_sheet.sh first" >&2
	exit 1
fi
CUR="$(git -C "$REPO" rev-parse --abbrev-ref HEAD)"
SRC="$(git -C "$REPO" rev-parse --short HEAD)"
TMP="$(mktemp -d)"
trap 'rm -rf "$TMP"' EXIT
# A throwaway index + orphan commit, without touching the checkout.
export GIT_INDEX_FILE="$TMP/index"
( cd "$FRAMES" && find . -type f \( -name '*.jpg' -o -name '*.png' -o -name '*.json' \) -print0 \
	| sed -z 's|^\./|godot/qa/contact/|' \
	| xargs -0 git -C "$REPO" update-index --add -- )
TREE="$(git -C "$REPO" write-tree)"
N="$(git -C "$REPO" ls-tree -r --name-only "$TREE" | wc -l)"
COMMIT="$(printf 'contact sheet · %s · from %s@%s · %s files\n' "$(date -u +%Y-%m-%dT%H:%MZ)" "$CUR" "$SRC" "$N" \
	| git -C "$REPO" commit-tree "$TREE")"
unset GIT_INDEX_FILE
git -C "$REPO" update-ref "refs/heads/$BRANCH" "$COMMIT"
git -C "$REPO" push --force origin "refs/heads/$BRANCH:refs/heads/$BRANCH"
echo "contact_push: $N file(s) on origin/$BRANCH ($COMMIT) — tell Claude the sheet is up"
