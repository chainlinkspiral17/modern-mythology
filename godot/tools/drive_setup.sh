#!/usr/bin/env bash
# Google Drive for Hero Studio's big files (2026-09-30).
#
# Installs rclone into ~/.local/bin if it is missing (no root, no
# package manager — SteamOS's system partition stays untouched), then
# connects a remote named "gdrive" to your Google account. A browser
# window opens once: sign in and allow access. The scope is
# drive.file, so rclone can see ONLY the files it creates itself — not
# the rest of your Drive. Models and pictures then go to the Drive
# folder "ModernMythology"; git keeps only a small manifest.
#
#   bash godot/tools/drive_setup.sh
set -euo pipefail
BIN="$HOME/.local/bin"
mkdir -p "$BIN"
RC="$(command -v rclone || true)"
if [ -z "$RC" ] && [ -x "$BIN/rclone" ]; then RC="$BIN/rclone"; fi
if [ -z "$RC" ]; then
  echo "installing rclone into $BIN ..."
  TMP="$(mktemp -d)"
  URL="https://downloads.rclone.org/rclone-current-linux-amd64.zip"
  curl -fsSL -o "$TMP/rclone.zip" "$URL" \
    || curl -fsSL -o "$TMP/rclone.zip" "https://github.com/rclone/rclone/releases/download/v1.68.2/rclone-v1.68.2-linux-amd64.zip"
  python3 -m zipfile -e "$TMP/rclone.zip" "$TMP"
  cp "$TMP"/rclone-*-linux-amd64/rclone "$BIN/rclone"
  chmod +x "$BIN/rclone"
  rm -rf "$TMP"
  RC="$BIN/rclone"
fi
echo "rclone: $("$RC" version | head -1)"
if ! "$RC" listremotes | grep -qx 'gdrive:'; then
  echo
  echo "A browser window will open. Sign in to Google and click Allow."
  echo "(rclone will only ever see the files it creates.)"
  echo
  "$RC" config create gdrive drive scope=drive.file
fi
# A "gdrive" remote can exist without a working sign-in (an earlier
# setup that never finished: "empty token found"). Test it; if it does
# not answer, sign in again. Press Enter at any question rclone asks.
if ! "$RC" lsd gdrive: >/dev/null 2>&1; then
  echo
  echo "The gdrive connection has no working sign-in. A browser window will open:"
  echo "sign in to Google and click Allow. Press Enter at any question here."
  echo
  "$RC" config reconnect gdrive:
fi
"$RC" mkdir gdrive:ModernMythology
"$RC" lsd gdrive: | grep -q ModernMythology && echo "DRIVE READY — Hero Studio's SAVE now puts models and pictures on Google Drive"
