#!/usr/bin/env bash
# Print the path of an ffmpeg that can write Ogg (Theora video + Vorbis
# audio) — the only formats Godot plays without plugins. The system's if
# it has both encoders; otherwise a static build is downloaded once into
# ~/.local/share/ffmpeg-static (no root; SteamOS's system stays as it is).
#
#   FF="$(bash godot/tools/get_ffmpeg.sh)"
#
# Shared by install_intro_video.sh (the opening movie) and
# import_voice_dropins.sh (Voice Studio's browser recordings are webm).
set -euo pipefail
# (read the whole list: `grep -q` quits early, ffmpeg dies on the closed
# pipe, and under pipefail the check would fail with the encoder present)
has_ogg() {
  local enc; enc="$("$1" -hide_banner -encoders 2>/dev/null || true)"
  [[ "$enc" == *libtheora* && "$enc" == *libvorbis* ]]
}
if command -v ffmpeg >/dev/null 2>&1 && has_ogg ffmpeg; then command -v ffmpeg; exit 0; fi
STATIC="$HOME/.local/share/ffmpeg-static"
if [ -x "$STATIC/ffmpeg" ] && has_ogg "$STATIC/ffmpeg"; then echo "$STATIC/ffmpeg"; exit 0; fi
echo "getting a static ffmpeg (one time) …" >&2
mkdir -p "$STATIC"; TMP="$(mktemp -d)"
if curl -fsSL -o "$TMP/ff.tar.xz" https://johnvansickle.com/ffmpeg/releases/ffmpeg-release-amd64-static.tar.xz \
   || curl -fsSL -o "$TMP/ff.tar.xz" https://github.com/BtbN/FFmpeg-Builds/releases/download/latest/ffmpeg-master-latest-linux64-gpl.tar.xz; then
  tar -xJf "$TMP/ff.tar.xz" -C "$TMP"
  cp "$(find "$TMP" -type f -name ffmpeg | head -1)" "$STATIC/ffmpeg"
  chmod +x "$STATIC/ffmpeg"
fi
rm -rf "$TMP"
has_ogg "$STATIC/ffmpeg" || { echo "the downloaded ffmpeg cannot write Ogg — tell Claude" >&2; exit 1; }
echo "$STATIC/ffmpeg"
