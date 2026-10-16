#!/usr/bin/env bash
# ART REVIEW (2026-10-14): hand Claude the hero-art pictures in a form it can
# read — the originals are 1.3 GB on Drive. One run:
#   1. art-optimize  — each picture's import settings (VRAM-compressed,
#                      capped by its surface; `inspect` pictures — meta-texts,
#                      art pieces, what the prose describes — at full size)
#   2. godot --import — Godot applies them (the first time takes a while)
#   3. ArtReviewSheet — every picture as 256 px contact sheets + a report
#                       (aspect vs surface, borders, brightness, alpha)
#   4. contact_sheet  — the rooms with the most art, rendered WITH the art on
#                       their surfaces (Background3D lays it), for judging it
#                       against the 3D sets
#   5. contact_push   — all of it onto the qa/contact review branch
#
#   bash godot/tools/art_review.sh
#   ONLY=kwik_stop,diner bash godot/tools/art_review.sh      # other rooms
set -uo pipefail
cd "$(dirname "$0")/../.."
find_godot() {
	if [ -n "${GODOT_BIN:-}" ] && command -v "$GODOT_BIN" >/dev/null 2>&1; then echo "$GODOT_BIN"; return; fi
	for c in godot4 godot godot4.6 godot-4; do command -v "$c" >/dev/null 2>&1 && { echo "$c"; return; }; done
	if command -v flatpak >/dev/null 2>&1 && flatpak info org.godotengine.Godot >/dev/null 2>&1; then
		echo "flatpak run org.godotengine.Godot"; return; fi
}
GODOT="$(find_godot)"
[ -z "$GODOT" ] && { echo "art_review: no Godot found — set GODOT_BIN=/path/to/godot" >&2; exit 1; }
ROOMS="${ONLY:-graustark,kwik_stop,centro_grocery,daily_grind,new_auburn,riverfront,diner,nexcorp_gas_go,new_orleans_bar,pharmacy,board_lords,missing_link,faust_apartment,roberts_kitchen,salty_tome,lena_apartment,cabin_interior}"

echo "1/5 import settings …"
python3 godot/tools/meshy_pipeline.py art-optimize || exit 1
echo "2/5 Godot import (the first time can take 10-20 minutes) …"
$GODOT --headless --path godot --import 2>&1 | grep -iE "error" | grep -v "custom_samplers" | tail -5 || true
echo "3/5 contact sheets of every picture …"
rm -rf godot/qa/contact/_art
$GODOT --headless --path godot --script res://tools/ArtReviewSheet.gd 2>&1 | grep -E "ArtReviewSheet|ERROR" | grep -v custom_samplers || true
echo "4/5 the rooms with their art ($ROOMS) …"
bash godot/tools/contact_sheet.sh --only="$ROOMS" || echo "(room renders failed — the sheets still go up)"
echo "5/5 pushing to the review branch …"
bash godot/tools/contact_push.sh
