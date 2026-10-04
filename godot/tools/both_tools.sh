#!/bin/bash
# Run Hero Studio and the comic inspector at the same time.
#
#   Hero Studio      http://127.0.0.1:8766/hero_uploader/   main folder, game branch
#   Comic inspector  http://127.0.0.1:8765/                 second folder, comic branch
#
# The two tools live on different branches, and one folder can only have one
# branch checked out. So the comic tool gets its own folder next to the main
# one (a git worktree: same repo, same history, no second clone). Hero Studio
# stays in the main folder because that is where the game reads its models.
#
# Run from inside the main modern-mythology folder:
#   bash both_tools.sh          start (or restart) both, open both in the browser
#   bash both_tools.sh stop     stop both
#
# Safe by design: it only fast-forwards (never merges, rebases or resets), only
# copies leftover comic files (never moves or overwrites), and stops with a
# plain message instead of guessing when the folders are in an unusual state.

set -u
COMIC_BR=${COMIC_BR:-claude/cool-hypatia-3firgv}
GAME_BR_HINT=claude/3d-locales-clean
HERO_PORT=${HERO_PORT:-8766}
COMIC_PORT=${COMIC_PORT:-8765}
NEED_KB=3500000   # the comic branch checks out at about 2.5 GB

common=$(git rev-parse --git-common-dir 2>/dev/null) || { echo "✗ Run this from inside the modern-mythology folder."; exit 1; }
MAIN=$(cd "$common/.." && pwd)
COMIC="${MAIN}-comic"
cd "$MAIN" || exit 1

# Only real python processes running the two servers (a shell whose command
# line merely mentions them must never match).
PY='^[^ ]*python[0-9.]* +([^ ]+ +)*'
stop_all() {
  for p in $(pgrep -f "${PY}[^ ]*meshy_pipeline\.py +serve"); do kill "$p" 2>/dev/null; done
  for p in $(pgrep -f "${PY}[^ ]*comic_inspector\.py"); do kill "$p" 2>/dev/null; done
}

open_url() {
  for opener in xdg-open firefox chromium chromium-browser google-chrome; do
    if command -v "$opener" >/dev/null 2>&1; then "$opener" "$1" >/dev/null 2>&1 && return 0; fi
  done
  if command -v flatpak >/dev/null 2>&1; then flatpak run org.mozilla.firefox "$1" >/dev/null 2>&1 && return 0; fi
  return 1
}

answers() { curl -s -o /dev/null --max-time 2 "$1"; }

# The comic images were purged from the comic branch's history on GitHub
# (2026-10-04, they live on Google Drive). An older comic folder cannot
# fast-forward onto the slimmed history; this lines it up without touching a
# single file on disk: find the slimmed twin of this folder's commit, move
# HEAD there with reset --mixed (index only), then fast-forward. A backup ref
# keeps the old history locally. Returns 1 when the divergence is something
# else (left to the plain warning).
IMG_PATHS=(godot/assets/comic lore/drift_wood/refs)
IMG_RX='\.(png|jpg|jpeg|webp)$'
resync_comic() {
  local remote="origin/$COMIC_BR" n want c match=""
  n=$(git -C "$COMIC" rev-list --objects "$remote..HEAD" -- "${IMG_PATHS[@]}" 2>/dev/null | grep -cE "$IMG_RX" || true)
  [ "${n:-0}" -gt 0 ] || return 1
  if ! git -C "$COMIC" diff --quiet || ! git -C "$COMIC" diff --cached --quiet; then
    echo "  ! GitHub's comic history was slimmed, and this folder has edits not yet saved. Left as is."
    echo "    Do not press SAVE in the comic tool until this is sorted; ask Claude to re-sync it."
    return 0
  fi
  want=$(git -C "$COMIC" ls-tree -r HEAD | grep -vE $'\t'"(godot/assets/comic/|lore/drift_wood/refs/).*$IMG_RX" | md5sum | cut -c1-32)
  for c in $(git -C "$COMIC" rev-list -n 400 "$remote"); do
    if [ "$(git -C "$COMIC" ls-tree -r "$c" | md5sum | cut -c1-32)" = "$want" ]; then match=$c; break; fi
  done
  if [ -z "$match" ]; then
    echo "  ! GitHub's comic history was slimmed, and this folder has commits GitHub does not. Left as is."
    echo "    Do not press SAVE in the comic tool until this is sorted; ask Claude to re-sync it."
    return 0
  fi
  git -C "$COMIC" update-ref "refs/backup/comic-before-slim-$(date +%Y%m%d-%H%M%S)" HEAD
  if git -C "$COMIC" reset -q --mixed "$match" && git -C "$COMIC" merge -q --ff-only "$remote"; then
    echo "  re-synced onto the slimmed comic history (images left GitHub; yours stay on disk)"
  else
    echo "  ! re-sync stopped part-way; nothing on disk changed. Ask Claude."
  fi
  return 0
}

if [ "${1:-}" = "stop" ]; then stop_all; echo "  Stopped Hero Studio and the comic inspector."; exit 0; fi

cur=$(git symbolic-ref --short -q HEAD || echo "(no branch)")
echo "main folder:  $MAIN   [$cur]"

if [ "$cur" = "$COMIC_BR" ]; then
  echo
  echo "✗ The main folder is on the comic branch right now."
  echo "  Hero Studio and the game live on the game branch, and the comic tool will get"
  echo "  its own folder. Save or commit your comic work, switch back, and run this again:"
  echo
  echo "    cd $MAIN && git checkout $GAME_BR_HINT"
  exit 1
fi
if [ ! -f godot/tools/meshy_pipeline.py ]; then
  echo
  echo "✗ The branch in the main folder ($cur) has no Hero Studio. Switch to the game branch:"
  echo
  echo "    cd $MAIN && git checkout $GAME_BR_HINT"
  exit 1
fi

# Hero Studio moved to the game branch on 2026-09-30 and gained Google Drive
# there; an older copy (e.g. the meshy branch) has no Drive support.
if ! grep -q "def drive_push" godot/tools/meshy_pipeline.py; then
  git fetch -q origin "+refs/heads/$GAME_BR_HINT:refs/remotes/origin/$GAME_BR_HINT" 2>/dev/null
  echo
  echo "✗ The Hero Studio on this branch ($cur) is an older copy without Google Drive."
  echo "  The current one is on the game branch. Your models and other uncommitted"
  echo "  files stay in the folder when you switch. Switch, then run this again:"
  echo
  echo "    cd $MAIN && git checkout $GAME_BR_HINT"
  exit 1
fi

# ── 1. Main folder: update only if it is a plain fast-forward ──────────────
echo "· updating the main folder…"
if git pull -q --ff-only origin "$cur" 2>/tmp/both_tools_pull.log; then
  echo "  ok"
else
  # Both sides moved: GitHub has new commits and this folder has its own (a
  # Hero Studio SAVE that did not push, say). Do what Hero Studio's SAVE does
  # on this branch: replay this folder's commits on top of GitHub's
  # (--autostash keeps unsaved edits). A conflict is undone on the spot and
  # nothing changes. A backup ref keeps the folder's previous state.
  git fetch -q origin "+refs/heads/$cur:refs/remotes/origin/$cur" 2>/dev/null || true
  ahead=$(git rev-list --count "origin/$cur..HEAD" 2>/dev/null || echo "?")
  behind=$(git rev-list --count "HEAD..origin/$cur" 2>/dev/null || echo "?")
  echo "  your copy has $ahead commit(s) GitHub lacks; GitHub has $behind you lack — replaying yours on top…"
  git update-ref "refs/backup/main-before-sync-$(date +%Y%m%d-%H%M%S)" HEAD
  if git -c user.name="${GIT_AUTHOR_NAME:-$(git config user.name || echo deck)}" \
        -c user.email="${GIT_AUTHOR_EMAIL:-$(git config user.email || echo deck@localhost)}" \
        pull -q --rebase --autostash origin "$cur" >/tmp/both_tools_pull.log 2>&1; then
    echo "  ok — up to date, your $ahead commit(s) kept on top (SAVE in Hero Studio pushes them)"
  else
    git rebase --abort >/dev/null 2>&1 || true
    echo "  ! could not combine them without a conflict; undone, nothing changed. Starting with what you have."
    grep -iE "conflict|error" /tmp/both_tools_pull.log | head -3 | sed 's/^/    /'
  fi
fi
if grep -q "def openai_generate" godot/tools/meshy_pipeline.py; then
  echo "  Hero Studio $(git log -1 --format=%h) · image providers: Google, Runway, OpenAI (ChatGPT)"
else
  echo "  ! Hero Studio $(git log -1 --format=%h) has no OpenAI yet (it is on GitHub's $GAME_BR_HINT)."
  echo "    Paste this whole output to Claude to sort out the update."
fi

# ── 2. Comic folder: create once, then update like the main one ────────────
git fetch -q origin "+refs/heads/$COMIC_BR:refs/remotes/origin/$COMIC_BR" 2>/dev/null \
  || echo "  ! could not reach GitHub for $COMIC_BR (offline?) — using what is on disk"

if [ -e "$COMIC/.git" ]; then
  echo "· updating the comic folder…"
  if git -C "$COMIC" pull -q --ff-only origin "$COMIC_BR" 2>/tmp/both_tools_pull.log; then
    echo "  ok"
  elif ! resync_comic; then
    echo "  ! not updated: your copy and GitHub have both changed. Starting with what you have."
  fi
else
  if [ -e "$COMIC" ]; then
    echo "✗ $COMIC already exists but is not a git folder. Rename or remove it, then run this again."
    exit 1
  fi
  avail=$(df -Pk "$(dirname "$MAIN")" | awk 'NR==2 {print $4}')
  if [ "${avail:-0}" -lt "$NEED_KB" ]; then
    echo "✗ The comic folder needs about 3.5 GB free next to $MAIN; only $((avail / 1024)) MB is free."
    exit 1
  fi
  if ! git rev-parse -q --verify "refs/remotes/origin/$COMIC_BR" >/dev/null \
     && ! git rev-parse -q --verify "refs/heads/$COMIC_BR" >/dev/null; then
    echo "✗ Cannot find the comic branch $COMIC_BR locally or on GitHub."
    exit 1
  fi
  echo "· creating the comic folder (one time, about 2.5 GB): $COMIC"
  if git rev-parse -q --verify "refs/heads/$COMIC_BR" >/dev/null; then
    git worktree add -q "$COMIC" "$COMIC_BR" || { echo "✗ Could not create the comic folder."; exit 1; }
    git -C "$COMIC" pull -q --ff-only origin "$COMIC_BR" 2>/dev/null \
      || echo "  ! your local comic branch has its own commits; left as it is."
  else
    git worktree add -q --track -b "$COMIC_BR" "$COMIC" "origin/$COMIC_BR" \
      || { echo "✗ Could not create the comic folder."; exit 1; }
  fi
  COMIC_CREATED=1
  # Comic work made in the main folder earlier and never committed (renders,
  # queues in out/): copy it across. Copy only, never overwrite.
  for d in godot/assets/comic godot/tools/comic/out; do
    if [ -d "$MAIN/$d" ]; then
      mkdir -p "$COMIC/$d"
      cp -rn "$MAIN/$d/." "$COMIC/$d/" 2>/dev/null
      echo "  copied leftover comic files from the main folder: $d"
    fi
  done
fi

# ── 3. One set of API keys for both folders ─────────────────────────────────
# The main folder holds the real files; the comic folder links to them. A key
# saved only in the comic folder (e.g. OpenAI from the comic inspector) moves
# to the main folder first, so Hero Studio sees it too.
for k in .runway_key .google_key .openai_key .meshy_key; do
  src="$MAIN/godot/tools/$k"; dst="$COMIC/godot/tools/$k"
  if [ ! -e "$src" ] && [ -f "$dst" ] && [ ! -L "$dst" ]; then
    mv "$dst" "$src" && chmod 600 "$src" && echo "  $k moved to the main folder so both tools share it"
  fi
  if [ -f "$src" ] && [ ! -e "$dst" ] && [ ! -L "$dst" ]; then
    ln -s "$src" "$dst" && echo "  comic folder uses the main folder's $k"
  fi
done

# ── 3b. A new comic folder lacks the images that live only on Google Drive ───
if [ "${COMIC_CREATED:-0}" = 1 ] && [ -f "$COMIC/godot/tools/comic/comic_drive.py" ]; then
  echo "· fetching comic images from Google Drive (only what the new folder lacks)…"
  if ( cd "$COMIC" && python3 godot/tools/comic/comic_drive.py pull ) > /tmp/both_tools_drive.log 2>&1; then
    echo "  ok"
  else
    echo "  ! not fetched — $(tail -1 /tmp/both_tools_drive.log)"
  fi
fi

# ── 4. Start both ───────────────────────────────────────────────────────────
stop_all
sleep 0.5

HERO_URL="http://127.0.0.1:$HERO_PORT/hero_uploader/"
COMIC_URL="http://127.0.0.1:$COMIC_PORT/"

echo "· starting Hero Studio on port $HERO_PORT…"
# exec: the server replaces the subshell, so no extra bash lingers holding this
# terminal's output open.
( cd "$MAIN" && exec nohup python3 godot/tools/meshy_pipeline.py serve --port "$HERO_PORT" \
    > /tmp/hero_studio.log 2>&1 < /dev/null ) &
for _ in $(seq 1 30); do answers "$HERO_URL" && break; sleep 0.5; done
hero_ok=0; answers "$HERO_URL" && hero_ok=1
[ $hero_ok = 1 ] || { echo "✗ Hero Studio did not start. Last lines of its log:"; tail -15 /tmp/hero_studio.log; }

echo "· starting the comic inspector on port $COMIC_PORT…"
PORT="$COMIC_PORT" bash "$COMIC/godot/tools/comic/inspect.sh" >/tmp/both_tools_comic.log 2>&1
comic_ok=0; answers "$COMIC_URL" && comic_ok=1
[ $comic_ok = 1 ] || { echo "✗ The comic inspector did not start:"; cat /tmp/both_tools_comic.log; }

[ $hero_ok = 1 ] && open_url "$HERO_URL"

echo
[ $hero_ok = 1 ]  && echo "  HERO STUDIO      $HERO_URL"
[ $hero_ok = 1 ]  && echo "                   folder $MAIN  [$cur]"
[ $comic_ok = 1 ] && echo "  COMIC INSPECTOR  $COMIC_URL"
[ $comic_ok = 1 ] && echo "                   folder $COMIC  [$COMIC_BR]"
echo
echo "  SAVE in either page: text to git, models and pictures to Google Drive."
echo "  Both keep running after you close this terminal."
echo "  Logs: /tmp/hero_studio.log  /tmp/comic_inspector.log"
echo "  Stop both: run the same command with  stop  at the end."
echo
echo "  Comic copy-paste commands from its README say  cd $MAIN ;"
echo "  run them in  $COMIC  instead, or they act on the game branch."
[ $hero_ok = 1 ] && [ $comic_ok = 1 ]
