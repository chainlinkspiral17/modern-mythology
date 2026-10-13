#!/usr/bin/env bash
# HERO STUDIO in one command (2026-10-13): ends any Studio still running
# (an old copy holds the port and serves stale code), starts a fresh one and
# opens it in the browser. Ctrl-C, or the page's QUIT button, stops it.
#
#   bash godot/tools/hero_studio.sh
set -uo pipefail
cd "$(dirname "$0")/../.."
python3 godot/tools/meshy_pipeline.py stop
exec python3 godot/tools/meshy_pipeline.py serve "$@"
