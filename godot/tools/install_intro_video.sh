#!/usr/bin/env bash
# The opening movie (2026-10-01): modernmythology1.mp4 → the game's intro.
#
# Godot plays only Ogg Theora video, so this converts the .mp4 to
# godot/assets/video/intro/modernmythology1.ogv (1280 wide — the Deck's
# screen — Theora video, Vorbis sound), then backs it up to Google Drive
# with Hero Studio's SAVE (videos live on Drive, not in git; another
# machine gets it with `meshy_pipeline.py drive-pull`).
#
#   bash godot/tools/install_intro_video.sh                 # finds the .mp4 itself
#   bash godot/tools/install_intro_video.sh ~/Videos/x.mp4  # or name it
#
# ffmpeg: the system's if it has the Theora encoder; otherwise a static
# build is downloaded once into ~/.local/share/ffmpeg-static (no root).
set -euo pipefail
cd "$(dirname "$0")/../.."
NAME="modernmythology1"
SRC="${1:-}"
if [ -z "$SRC" ]; then
  SRC="$(find "$HOME/Downloads" "$HOME/Videos" "$HOME/Desktop" "$HOME" -maxdepth 3 -iname "$NAME.mp4" 2>/dev/null | head -1 || true)"
fi
if [ -z "$SRC" ] || [ ! -f "$SRC" ]; then
  echo "Could not find $NAME.mp4 on this machine."
  echo "Download it from Google Drive in the browser (it lands in ~/Downloads):"
  echo "  https://drive.google.com/file/d/1xOg7lYAgVgkZ-DB4YBh3vIz4V3B-T8JL/view"
  echo "then run this again."
  exit 1
fi
echo "source: $SRC"

FF="$(bash godot/tools/get_ffmpeg.sh)"
OUT="godot/assets/video/intro/$NAME.ogv"
mkdir -p "$(dirname "$OUT")"
echo "converting (a few minutes for a long video) …"
"$FF" -hide_banner -loglevel error -stats -y -i "$SRC" \
  -vf "scale=1280:-2" -c:v libtheora -q:v 7 -c:a libvorbis -q:a 5 "$OUT"
echo "made $OUT ($(( $(stat -c %s "$OUT") / 1000000 )) MB)"
python3 godot/tools/meshy_pipeline.py save || echo "(the video is in place; the Drive backup did not finish — run: python3 godot/tools/meshy_pipeline.py save)"
echo "INTRO READY — start the game: it opens on the movie; click or any button skips to the menu"
