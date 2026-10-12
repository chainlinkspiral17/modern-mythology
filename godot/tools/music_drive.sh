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
#   godot/tools/music_drive.sh tidy     delete from Drive what the tools replaced here (older WAV temps
#                                       shrunk to Ogg, .wav files APPROVE moved to replaced/) — lists
#                                       them first and asks; anything else only in Drive is left alone
#
# Only audio and its sidecars move (.ogg .mp3 .wav .flac, .stems/ folders, .stems.json,
# .credits.txt). push / pull never delete; `tidy` is the only command that removes anything (in Drive).
# Env overrides: MM_DRIVE_REMOTE (default gdrive), MM_DRIVE_DIR.
set -euo pipefail

REMOTE="${MM_DRIVE_REMOTE:-gdrive}"
DRIVE_DIR="${MM_DRIVE_DIR:-ModernMythology/godot/assets/audio}"
HERE="$(cd "$(dirname "$0")" && pwd)"
LOCAL="$(cd "$HERE/../assets" && pwd)/audio"
# assets/audio/review/ is the AUDIO DIRECTOR's local staging (candidate takes): approved takes are copied
# out of it to their game paths and travel from there; the staging itself stays on this machine
# (--filter rules apply in order; mixing --include with --exclude would leave the order to rclone)
FILTERS=(--filter "- /review/**" --filter "+ *.ogg" --filter "+ *.mp3" --filter "+ *.wav" --filter "+ *.flac"
         --filter "+ *.stems.json" --filter "+ *.credits.txt" --filter "- **")

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
  tidy)
    need
    yes=""; [ "${2:-}" = "--yes" ] && yes=1
    # a Drive file this machine no longer has is "replaced" when the tools put something in its place here:
    #   <base>.wav / <base>.wav.credits.txt   → <base>.temp.ogg here (SHRINK / APPROVE), or the .wav was moved
    #                                           to replaced/<name>.<stamp>.wav by APPROVE
    #   <base>.stems/<part>.wav                → <base>.temp.ogg or <base>.stems.json here (the Ogg stems)
    # anything else that is only in Drive (new on another machine) is listed and left alone — pull brings it here
    gone=(); other=()
    while IFS= read -r f; do
      [ -n "$f" ] || continue
      [ -e "$LOCAL/$f" ] && continue
      b=""
      case "$f" in
        replaced/*) continue ;;
        *.stems/*.wav) b="${f%%.stems/*}"; if [ -e "$LOCAL/$b.temp.ogg" ] || [ -e "$LOCAL/$b.stems.json" ]; then gone+=("$f"); else other+=("$f"); fi; continue ;;
        *.wav.credits.txt) b="${f%.wav.credits.txt}" ;;
        *.wav) b="${f%.wav}" ;;
      esac
      if [ -n "$b" ] && { [ -e "$LOCAL/$b.temp.ogg" ] || compgen -G "$LOCAL/replaced/$(basename "$b").*.wav" >/dev/null; }; then gone+=("$f"); else other+=("$f"); fi
    done < <("$RCLONE" lsf -R --files-only "$REMOTE:$DRIVE_DIR" "${FILTERS[@]}")
    if [ ${#other[@]} -gt 0 ]; then
      echo "· only in Drive, left alone (\`$0 pull\` brings these here):"; printf '    %s\n' "${other[@]}"
    fi
    if [ ${#gone[@]} -eq 0 ]; then echo "✓ nothing to tidy: Drive has no replaced temps"; exit 0; fi
    echo "· replaced here — these would come back on the next pull and play instead of the new Ogg temps:"
    printf '    %s\n' "${gone[@]}"
    if [ -z "$yes" ]; then read -r -p "delete these ${#gone[@]} file(s) from Drive? [y/N] " a; case "$a" in y|Y|yes) ;; *) echo "nothing deleted"; exit 0 ;; esac; fi
    for f in "${gone[@]}"; do "$RCLONE" deletefile "$REMOTE:$DRIVE_DIR/$f" && echo "  deleted $f"; done
    echo "✓ tidied ${#gone[@]} file(s) from $REMOTE:$DRIVE_DIR"
    ;;
  *)
    sed -n '2,21p' "$0" | sed 's/^# \{0,1\}//'
    exit 1
    ;;
esac
