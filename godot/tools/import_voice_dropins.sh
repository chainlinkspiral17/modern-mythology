#!/usr/bin/env bash
# Voice Studio zips on Google Drive → voiced lines in the game (2026-10-01).
#
#   bash godot/tools/import_voice_dropins.sh            # from the Drive
#   bash godot/tools/import_voice_dropins.sh ~/Downloads # zips already here
#
# 1. reads the Drive through the read-only connection (sets it up the
#    first time: one browser sign-in) and copies every voice_dropin_*.zip
#    — wherever on the Drive it sits — into ~/.cache/modern-mythology/
#    voice_dropins (only new or changed zips download)
# 2. import_voice_dropins.py: lines matched to today's scene text, webm
#    → ogg, "voice" keys written (zips already imported are skipped, so
#    run it again whenever more zips are up)
# 3. Hero Studio's SAVE: the audio goes to the project's Drive folder
#    (not git), the scene JSONs + the report are committed and pushed
#
# The report of every line (wired, close, skipped) is
# godot/tools/voice_import_report.md.
set -euo pipefail
cd "$(dirname "$0")/../.."
RC="$(command -v rclone || true)"
[ -z "$RC" ] && [ -x "$HOME/.local/bin/rclone" ] && RC="$HOME/.local/bin/rclone"
SRC="${1:-}"
if [ -z "$SRC" ]; then
  if [ -z "$RC" ] || ! "$RC" listremotes | grep -qx 'gdrive_ro:'; then
    bash godot/tools/drive_setup.sh --read
    RC="$(command -v rclone || echo "$HOME/.local/bin/rclone")"
  fi
  SRC="$HOME/.cache/modern-mythology/voice_dropins"
  mkdir -p "$SRC"
  echo "looking for voice_dropin_*.zip on the Drive (a minute for a big Drive) …"
  "$RC" copy gdrive_ro: "$SRC" --include "voice_dropin_*.zip" --fast-list \
    --drive-skip-shortcuts --transfers 4 --progress --stats-one-line
fi
FF="$(bash godot/tools/get_ffmpeg.sh)"
python3 godot/tools/import_voice_dropins.py "$SRC" --ffmpeg "$FF"
python3 godot/tools/meshy_pipeline.py save \
  || echo "(the voice is in place; the save did not finish — run: python3 godot/tools/meshy_pipeline.py save)"
echo "VOICE READY — restart Godot (or press F5) and play a voiced scene"
