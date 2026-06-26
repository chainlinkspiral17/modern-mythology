#!/usr/bin/env bash
# Open the 3D Asset Manager in Chromium, served over localhost so the
# "Write to project" (File System Access API) feature works.
# Usage:  bash scripts/asset-manager.sh
set -uo pipefail

REPO="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
. "$(dirname "${BASH_SOURCE[0]}")/_canon_guard.sh"
PORT="${PORT:-8770}"
URL="http://localhost:${PORT}/project/3D%20Asset%20Manager.html"

# pick a python for the static server
PY=""
command -v python3 >/dev/null 2>&1 && PY="python3"
[ -z "$PY" ] && command -v python >/dev/null 2>&1 && PY="python"
if [ -z "$PY" ]; then
  echo "!! need python3 to serve the page. Install it, or open this in Chromium directly:"
  echo "   file://$REPO/project/3D Asset Manager.html"
  exit 1
fi

# pick a Chromium-family browser (File System Access API needs Chromium, not Firefox)
open_browser() {
  if   command -v chromium         >/dev/null 2>&1; then chromium "$1" &
  elif command -v chromium-browser >/dev/null 2>&1; then chromium-browser "$1" &
  elif command -v google-chrome    >/dev/null 2>&1; then google-chrome "$1" &
  elif flatpak info org.chromium.Chromium >/dev/null 2>&1; then flatpak run org.chromium.Chromium "$1" &
  elif flatpak info com.google.Chrome      >/dev/null 2>&1; then flatpak run com.google.Chrome "$1" &
  elif command -v xdg-open >/dev/null 2>&1; then
    echo "!! No Chromium/Chrome found — opening in your default browser."
    echo "   NOTE: 'Write to project' needs Chromium/Chrome. Install it (Discover store) for that feature."
    xdg-open "$1" &
  else
    echo "!! No browser launcher found. Open this URL yourself: $1"
    return 1
  fi
}

echo ">> serving $REPO on http://localhost:$PORT"
cd "$REPO"
"$PY" -m http.server "$PORT" >/dev/null 2>&1 &
SERVER_PID=$!
trap 'kill $SERVER_PID 2>/dev/null' EXIT
sleep 1

echo ">> opening: $URL"
open_browser "$URL"

echo ">> In the tool: drag your .glb / sky / audio files in, tag them, then"
echo "   'connect repo folder' (pick this modern-mythology folder) and 'Write all to project'."
echo ">> Leave this Konsole tab open while you work; press Ctrl-C here to stop the server."
wait $SERVER_PID
