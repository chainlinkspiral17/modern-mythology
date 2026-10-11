#!/usr/bin/env bash
# music_drive.sh — the game's audio lives in Google Drive, not git.
#
# Mirrors  godot/assets/audio/  ⇄  My Drive/ModernMythology/godot/assets/audio/
# (same layout as the repo, so a catalog src like assets/audio/bgm/vol1_title.ogg
#  is ModernMythology/godot/assets/audio/bgm/vol1_title.ogg in Drive).
#
#   godot/tools/music_drive.sh setup    once: installs rclone in ~/.local/bin and links your
#                                       Google account (a browser tab opens — sign in, allow)
#   godot/tools/music_drive.sh pull     Drive → game folder  (new / newer files only)
#   godot/tools/music_drive.sh push     game folder → Drive  (new / newer files only)
#   godot/tools/music_drive.sh status   what differs, nothing copied
#
# Only audio and its sidecars move (.ogg .mp3 .wav .flac, .stems/ folders, .stems.json,
# .credits.txt). Nothing is ever deleted on either side — remove files by hand.
# Env overrides: MM_DRIVE_REMOTE (default gdrive), MM_DRIVE_DIR.
set -euo pipefail

REMOTE="${MM_DRIVE_REMOTE:-gdrive}"
DRIVE_DIR="${MM_DRIVE_DIR:-ModernMythology/godot/assets/audio}"
HERE="$(cd "$(dirname "$0")" && pwd)"
LOCAL="$(cd "$HERE/../assets" && pwd)/audio"
FILTERS=(--include "*.ogg" --include "*.mp3" --include "*.wav" --include "*.flac"
         --include "*.stems.json" --include "*.credits.txt")

find_rclone() {
  if command -v rclone >/dev/null 2>&1; then command -v rclone
  elif [ -x "$HOME/.local/bin/rclone" ]; then echo "$HOME/.local/bin/rclone"
  else echo ""; fi
}

install_rclone() {
  echo "· installing rclone into ~/.local/bin (no sudo needed)…"
  local tmp; tmp="$(mktemp -d)"
  # rclone's own site first, then the same build from its GitHub releases
  if ! curl -fsSL -o "$tmp/rclone.zip" https://downloads.rclone.org/rclone-current-linux-amd64.zip &&
     ! curl -fsSL -o "$tmp/rclone.zip" https://github.com/rclone/rclone/releases/download/v1.68.2/rclone-v1.68.2-linux-amd64.zip; then
    echo "could not download rclone — check the network, or install it yourself (flatpak / AUR / rclone.org)" >&2; rm -rf "$tmp"; return 1
  fi
  python3 -c "import zipfile,sys; zipfile.ZipFile(sys.argv[1]).extractall(sys.argv[2])" "$tmp/rclone.zip" "$tmp" || { rm -rf "$tmp"; return 1; }
  mkdir -p "$HOME/.local/bin"
  cp "$tmp"/rclone-*-linux-amd64/rclone "$HOME/.local/bin/rclone" && chmod +x "$HOME/.local/bin/rclone" || { rm -rf "$tmp"; return 1; }
  rm -rf "$tmp"
}

RCLONE="$(find_rclone)"
need() {
  if [ -z "$RCLONE" ]; then echo "rclone isn't set up yet — run: $0 setup" >&2; exit 1; fi
  if ! "$RCLONE" listremotes | grep -qx "$REMOTE:"; then echo "no '$REMOTE' remote — run: $0 setup" >&2; exit 1; fi
}

case "${1:-}" in
  setup)
    if [ -z "$RCLONE" ]; then install_rclone || exit 1; RCLONE="$HOME/.local/bin/rclone"; fi
    if ! "$RCLONE" listremotes | grep -qx "$REMOTE:"; then
      echo "· linking Google Drive as '$REMOTE' — a browser tab opens; sign in and allow access."
      "$RCLONE" config create "$REMOTE" drive scope=drive
    fi
    "$RCLONE" mkdir "$REMOTE:$DRIVE_DIR"
    echo "✓ ready: $LOCAL  ⇄  $REMOTE:$DRIVE_DIR"
    echo "  now:  $0 pull   (or push)"
    ;;
  pull)
    need
    mkdir -p "$LOCAL"
    "$RCLONE" copy "$REMOTE:$DRIVE_DIR" "$LOCAL" "${FILTERS[@]}" --update --progress
    echo "✓ pulled into $LOCAL"
    ;;
  push)
    need
    "$RCLONE" copy "$LOCAL" "$REMOTE:$DRIVE_DIR" "${FILTERS[@]}" --update --progress
    echo "✓ pushed to $REMOTE:$DRIVE_DIR"
    ;;
  status)
    need
    "$RCLONE" check "$LOCAL" "$REMOTE:$DRIVE_DIR" "${FILTERS[@]}" --size-only 2>&1 | tail -n 25 || true
    ;;
  *)
    sed -n '2,18p' "$0" | sed 's/^# \{0,1\}//'
    exit 1
    ;;
esac
