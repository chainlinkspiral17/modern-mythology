#!/bin/bash
# One command: start the comic inspector and open it in the browser.
#   bash godot/tools/comic/inspect.sh          (from anywhere)
# Stops any copy already running, starts a fresh one in the background,
# waits until it answers, opens the browser, and prints the address.
cd "$(dirname "$0")/../../.." || exit 1
PORT=${PORT:-8765}
URL="http://127.0.0.1:$PORT/"
for p in $(pgrep -f "^python3 .*comic_inspector\.py"); do kill "$p" 2>/dev/null; done
sleep 0.5
nohup python3 godot/tools/comic/comic_inspector.py --port "$PORT" > /tmp/comic_inspector.log 2>&1 &
for i in $(seq 1 20); do
  if curl -s "${URL}api/keys" >/dev/null 2>&1; then break; fi
  sleep 0.5
done
if ! curl -s "${URL}api/keys" >/dev/null 2>&1; then
  echo "✗ the inspector did not start. Log:"; cat /tmp/comic_inspector.log; exit 1
fi
echo
echo "  COMIC INSPECTOR is running:  $URL"
echo "  (log: /tmp/comic_inspector.log · stop it with: bash godot/tools/comic/inspect.sh stop)"
echo
if [ "$1" = "stop" ]; then for p in $(pgrep -f "^python3 .*comic_inspector\.py"); do kill "$p"; done; echo "  stopped."; exit 0; fi
for opener in xdg-open firefox chromium chromium-browser google-chrome; do
  if command -v "$opener" >/dev/null 2>&1; then "$opener" "$URL" >/dev/null 2>&1 && exit 0; fi
done
if command -v flatpak >/dev/null 2>&1; then flatpak run org.mozilla.firefox "$URL" >/dev/null 2>&1 && exit 0; fi
echo "  Could not open a browser myself. Type this in the address bar:  127.0.0.1:$PORT"
