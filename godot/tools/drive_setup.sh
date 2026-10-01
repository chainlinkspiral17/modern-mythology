#!/usr/bin/env bash
# Google Drive for Hero Studio's big files (2026-09-30).
#
# Installs rclone into ~/.local/bin if it is missing (no root, no
# package manager — SteamOS's system partition stays untouched), then
# connects a remote named "gdrive" to your Google account. A browser
# window opens once: sign in and allow access. Models, pictures, video
# and voice then go to the Drive folder "ModernMythology"; git keeps
# only a small manifest.
#
#   bash godot/tools/drive_setup.sh            # set up, or check
#   bash godot/tools/drive_setup.sh --fresh    # start the sign-in over
#   bash godot/tools/drive_setup.sh --read     # + a read-only view of the whole Drive
#   bash godot/tools/drive_setup.sh --client   # use YOUR OWN Google client id (asks for it)
#
# YOUR OWN CLIENT ID (2026-10-01; https://rclone.org/drive/#making-your-own-client-id).
# rclone's shared client id is rate-limited and is being retired; with
# your own, both connections sign in through YOUR Google app. --client
# asks for the client id and secret (the secret is typed hidden), keeps
# them in godot/tools/.gdrive_client (gitignored, readable only by you),
# moves both connections onto them and signs each in once.
#   · "gdrive" then uses scope `drive`, not `drive.file`: drive.file only
#     sees files made by the SAME app, and the ModernMythology folder was
#     made by rclone's shared app — under your app it would look empty and
#     SAVE would start a second copy. The tool still only ever copies; it
#     never deletes anything on the Drive.
#   · "gdrive_ro" stays read-only (drive.readonly).
#   · In Google Cloud's OAuth consent screen, PUBLISH the app ("In
#     production"): a "Testing" app's sign-in expires every 7 days. The
#     sign-in then warns "Google hasn't verified this app" — it is your
#     own app: Advanced → Go to … → Continue.
set -euo pipefail
HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
CLIENT_FILE="$HERE/.gdrive_client"
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

ARGS=("$@")
has_flag() { local a; for a in "${ARGS[@]}"; do [ "$a" = "$1" ] && return 0; done; return 1; }
has_remote() { "$RC" listremotes | grep -qx "$1:"; }

# ── your own client id ──────────────────────────────────────────────
CLIENT_ID=""
CLIENT_SECRET=""
if has_flag --client; then
  echo
  echo "Your Google OAuth client (Google Cloud → APIs & Services → Credentials)."
  read -r -p "client id (….apps.googleusercontent.com): " CLIENT_ID
  read -r -s -p "client secret (hidden as you type): " CLIENT_SECRET
  echo
  CLIENT_ID="$(echo "$CLIENT_ID" | tr -d '[:space:]')"
  CLIENT_SECRET="$(echo "$CLIENT_SECRET" | tr -d '[:space:]')"
  case "$CLIENT_ID" in
    *.apps.googleusercontent.com) ;;
    *) echo "that client id does not end in .apps.googleusercontent.com — nothing changed"; exit 1 ;;
  esac
  [ -n "$CLIENT_SECRET" ] || { echo "no secret entered — nothing changed"; exit 1; }
  ( umask 077; printf 'CLIENT_ID=%s\nCLIENT_SECRET=%s\n' "$CLIENT_ID" "$CLIENT_SECRET" > "$CLIENT_FILE" )
  echo "saved to $CLIENT_FILE (gitignored, only you can read it)"
elif [ -f "$CLIENT_FILE" ]; then
  CLIENT_ID="$(sed -n 's/^CLIENT_ID=//p' "$CLIENT_FILE")"
  CLIENT_SECRET="$(sed -n 's/^CLIENT_SECRET=//p' "$CLIENT_FILE")"
fi
OWN=0
[ -n "$CLIENT_ID" ] && [ -n "$CLIENT_SECRET" ] && OWN=1
# the project connection: full scope under your own app (see the header)
MAIN_SCOPE="drive.file"
[ "$OWN" = 1 ] && MAIN_SCOPE="drive"

# make (or move) a remote onto the right app + scope, then sign it in
connect() {   # name scope what-it-is
  local name="$1" scope="$2" what="$3"
  local cargs=()
  [ "$OWN" = 1 ] && cargs=("client_id=$CLIENT_ID" "client_secret=$CLIENT_SECRET")
  local signin=0
  if ! has_remote "$name"; then
    "$RC" config create "$name" drive scope="$scope" "${cargs[@]}" config_refresh_token=false --non-interactive >/dev/null
    signin=1
  elif has_flag --client; then
    "$RC" config update "$name" scope="$scope" "${cargs[@]}" config_refresh_token=false --non-interactive >/dev/null
    signin=1   # a sign-in made through another app does not carry over
  fi
  if [ "$signin" = 0 ] && ! "$RC" lsd "$name:" >/dev/null 2>&1; then
    signin=1   # exists without a working sign-in ("empty token found")
  fi
  if [ "$signin" = 1 ]; then
    echo
    echo "── sign in: $what ──"
    echo "A browser window will open. Sign in to Google and click Allow."
    [ "$OWN" = 1 ] && echo "(your own app: if Google says it is unverified — Advanced → Go to … → Continue)"
    echo "Press Enter at any question rclone asks here."
    echo
    "$RC" config reconnect "$name:"
  fi
}

# --fresh: throw away the connection(s) and sign in from scratch (an
# "Auth state doesn't match" from a stale browser tab, a broken token)
if has_flag --fresh; then
  if has_flag --read; then "$RC" config delete gdrive_ro 2>/dev/null || true
  else "$RC" config delete gdrive 2>/dev/null || true; fi
  echo "old connection removed — close any old sign-in tabs; use only the one that opens now"
fi

# --read: a SECOND, read-only connection, "gdrive_ro" (2026-10-01). The
# Voice Studio zips, the songs, anything in incoming/ — files YOU put on
# the Drive — are read through it; it can change nothing (drive.readonly).
# The voice importer and Hero Studio's AUDIO page use it.
if has_flag --read; then
  connect gdrive_ro drive.readonly "the read-only view of your whole Drive"
  "$RC" lsd gdrive_ro: >/dev/null 2>&1 && echo "DRIVE READ READY — the voice importer and the AUDIO page can see your Drive"
  has_flag --client || exit 0
fi

connect gdrive "$MAIN_SCOPE" "the project folder (Hero Studio's SAVE)"
# --client moves the read-only connection too, if there is one
if has_flag --client && has_remote gdrive_ro && ! has_flag --read; then
  connect gdrive_ro drive.readonly "the read-only view of your whole Drive"
fi
"$RC" mkdir gdrive:ModernMythology
if "$RC" lsd gdrive: | grep -q ModernMythology; then
  [ "$OWN" = 1 ] && echo "using your own Google client id"
  echo "DRIVE READY — Hero Studio's SAVE now puts models and pictures on Google Drive"
fi
