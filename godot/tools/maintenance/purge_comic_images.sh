#!/bin/bash
# Remove the comic images from the comic branch's git HISTORY, after they are
# safely on Google Drive — this is what frees space on GitHub (deleting files in
# a normal commit does not: every older commit still holds them).
#
# Run in a full clone that has every branch fetched (the cloud session does
# this; it is not a Deck command):
#   bash godot/tools/maintenance/purge_comic_images.sh --rehearse   # no Drive check, no push
#   bash godot/tools/maintenance/purge_comic_images.sh              # check + rewrite, no push
#   bash godot/tools/maintenance/purge_comic_images.sh --push       # check + rewrite + force-push
#
# Safety:
#   1. Refuses unless EVERY image in the branch's history is in the branch's
#      godot/tools/comic/drive_manifest.json with the same size and md5 (the
#      comic tool's SAVE writes it as each upload lands).
#   2. Rewrites only the commits that exist on the comic branch alone; history
#      shared with other branches keeps its exact commit ids (checked).
#   3. The tip's text files must come out byte-identical (checked).
#   4. Force-push uses --force-with-lease against the tip it checked, so a
#      push that landed meanwhile is never overwritten.
set -euo pipefail
BR=${BR:-claude/cool-hypatia-3firgv}
MODE=check
for a in "$@"; do case "$a" in --rehearse) MODE=rehearse ;; --push) MODE=push ;; *) echo "unknown option $a"; exit 2 ;; esac; done
export PATH="$HOME/.local/bin:$PATH"
command -v git-filter-repo >/dev/null || { echo "needs git-filter-repo: pip install --user git-filter-repo"; exit 1; }
REPO=$(git rev-parse --show-toplevel)
WORK=$(mktemp -d "${TMPDIR:-/tmp}/purge_comic.XXXX")
IMG_RE='^(godot/assets/comic/|lore/drift_wood/refs/).*\.(png|jpg|jpeg|webp)$'
cd "$REPO"

echo "· fetching every branch…"
git fetch -q origin '+refs/heads/*:refs/remotes/origin/*'
OLD=$(git rev-parse "origin/$BR")
OTHERS=$(git for-each-ref --format='%(refname)' refs/remotes/origin | grep -v -e "/HEAD$" -e "/$BR$")
EXCL=$(for r in $OTHERS; do printf '^%s ' "$r"; done)
echo "  $BR at ${OLD:0:8}; $(echo "$OTHERS" | wc -l) other branches"

# ── 1. every image in history must be on the Drive ─────────────────────────
echo "· listing images in the branch's history…"
git rev-list --objects "origin/$BR" -- godot/assets/comic lore/drift_wood/refs \
  | awk 'NF==2' | grep -E " ${IMG_RE#^}" > "$WORK/hist.txt" || true
NIMG=$(cut -d' ' -f1 "$WORK/hist.txt" | sort -u | wc -l)
echo "  $NIMG distinct image(s) in history"
[ "$NIMG" -gt 0 ] || { echo "  nothing to remove — the history holds no comic images"; exit 0; }
if [ "$MODE" != rehearse ]; then
  git show "origin/$BR:godot/tools/comic/drive_manifest.json" > "$WORK/manifest.json" 2>/dev/null \
    || { echo "✗ no drive_manifest.json on $BR yet — run SAVE in the comic inspector first"; exit 1; }
  python3 - "$WORK/hist.txt" "$WORK/manifest.json" <<'PY'
import hashlib, json, subprocess, sys
hist = [l.split(" ", 1) for l in open(sys.argv[1]).read().splitlines() if l.strip()]
files = json.load(open(sys.argv[2])).get("files", {})
by_md5 = {}
for path, m in files.items():
    by_md5.setdefault(m.get("md5"), set()).add(m.get("size"))
missing, seen = [], set()
for sha, path in hist:
    if sha in seen:
        continue
    seen.add(sha)
    blob = subprocess.run(["git", "cat-file", "blob", sha], capture_output=True, check=True).stdout
    md5 = hashlib.md5(blob).hexdigest()
    if len(blob) not in by_md5.get(md5, set()):
        missing.append(path)
if missing:
    print(f"✗ {len(missing)} image(s) in history are NOT on the Drive (by md5) — SAVE again, then retry:")
    for p in missing[:20]:
        print("   ", p)
    sys.exit(1)
print(f"  ✓ all {len(seen)} image(s) are on the Drive (size + md5 match the manifest)")
PY
else
  echo "  (rehearsal: Drive check skipped)"
fi

# ── 2. rewrite only the comic branch's own commits, in a scratch clone ───────
echo "· rewriting in a scratch clone…"
git clone -q --no-local --bare "$REPO" "$WORK/scratch.git"
cd "$WORK/scratch.git"
git fetch -q "$REPO" "+refs/remotes/origin/*:refs/heads/*"
BOUNDARY=$(git rev-list --boundary "$BR" $(for r in $OTHERS; do printf '^%s ' "${r#refs/remotes/origin/}"; done) | sed -n 's/^-//p')
git filter-repo --force --quiet --refs "$BR" $(for b in $BOUNDARY; do printf '^%s ' "$b"; done) \
  --invert-paths \
  --path-glob 'godot/assets/comic/*.png' --path-glob 'godot/assets/comic/*.jpg' \
  --path-glob 'godot/assets/comic/*.jpeg' --path-glob 'godot/assets/comic/*.webp' \
  --path-glob 'lore/drift_wood/refs/*.png' --path-glob 'lore/drift_wood/refs/*.jpg' \
  --path-glob 'lore/drift_wood/refs/*.jpeg' --path-glob 'lore/drift_wood/refs/*.webp'
NEW=$(git rev-parse "$BR")

# ── 3. checks ────────────────────────────────────────────────────────────────
echo "· checking the result…"
left=$(git rev-list --objects "$BR" | awk 'NF==2' | grep -cE " ${IMG_RE#^}" || true)
[ "$left" = 0 ] || { echo "✗ $left image(s) still reachable — not pushing"; exit 1; }
for b in $BOUNDARY; do git merge-base --is-ancestor "$b" "$BR" || { echo "✗ shared commit ${b:0:8} lost — not pushing"; exit 1; }; done
diff <(cd "$REPO" && git ls-tree -r "$OLD" | grep -vE $'\t'"${IMG_RE#^}") <(git ls-tree -r "$NEW") >/dev/null \
  || { echo "✗ the tip's text files differ — not pushing"; exit 1; }
[ "$(git rev-list --count "$BR")" = "$(cd "$REPO" && git rev-list --count "$OLD")" ] \
  || echo "  note: commit count changed (commits that only added images became empty and were dropped)"
before=$(cd "$REPO" && git rev-list --objects "$OLD" $EXCL | awk '{print $1}' | git cat-file --batch-check='%(objectsize:disk)' | awk '{s+=$1} END {print s}')
after=$(git rev-list --objects "$BR" $(for r in $OTHERS; do printf '^%s ' "${r#refs/remotes/origin/}"; done) | awk '{print $1}' | git cat-file --batch-check='%(objectsize:disk)' | awk '{s+=$1} END {print s}')
printf "  ✓ no images left; shared history intact (%s boundary commit(s)); tip text identical\n" "$(echo "$BOUNDARY" | wc -w)"
printf "  branch-only data: %.0f MB → %.0f MB\n" "$(echo "$before/1048576" | bc -l)" "$(echo "$after/1048576" | bc -l)"
echo "  old tip ${OLD:0:8} → new tip ${NEW:0:8}"

# ── 4. keep the result as refs/purge/<branch>; push it with --push ─────────
cd "$REPO"
git fetch -q "$WORK/scratch.git" "+refs/heads/$BR:refs/purge/$BR"
echo "  rewritten history kept locally as refs/purge/$BR"
if [ "$MODE" = push ]; then
  git push --force-with-lease="refs/heads/$BR:$OLD" origin "refs/purge/$BR:refs/heads/$BR"
  git update-ref -d "refs/purge/$BR"
  echo "  ✓ pushed. GitHub reclaims the space when it next garbage-collects (can take a while;"
  echo "    GitHub Support can run it on request)."
else
  echo "  (not pushed: $MODE)"
fi
rm -rf "$WORK"
