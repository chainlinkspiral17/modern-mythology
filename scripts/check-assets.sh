#!/usr/bin/env bash
# Diagnose why imported assets aren't showing in the previz.
# Usage:  bash scripts/check-assets.sh
set -uo pipefail
REPO="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
G="$REPO/godot"

echo "== repo: $REPO"
echo

echo "== models  ($G/assets/models)"
shopt -s nullglob
found_model=0
for f in "$G/assets/models/"*.glb "$G/assets/models/"*.gltf; do
  found_model=1
  base="$(basename "$f")"
  if [ -f "$f.import" ]; then imp="imported ✓"; else imp="NOT imported ✗ (run previz-run.sh)"; fi
  echo "   $base    [$imp]"
done
[ "$found_model" = 0 ] && echo "   (no .glb/.gltf here — the tool didn't write models to this folder)"
echo

echo "== skyboxes  ($G/assets/sky)"
found_sky=0
for f in "$G/assets/sky/"*.{hdr,exr,png,jpg,jpeg,webp}; do
  found_sky=1; echo "   $(basename "$f")"
done
[ "$found_sky" = 0 ] && echo "   (none — moods use the procedural sky)"
echo

echo "== show tracks  ($G/assets/audio/previz)"
found_aud=0
for f in "$G/assets/audio/previz/"*.{ogg,wav,mp3}; do
  found_aud=1; echo "   $(basename "$f")"
done
[ "$found_aud" = 0 ] && echo "   (none — no music loaded)"
echo

echo "== characters.json model paths"
CJ="$G/scenes/previz/data/characters.json"
if [ -f "$CJ" ]; then
  python3 - "$CJ" "$G" <<'PY'
import json,sys,os
cj,g=sys.argv[1],sys.argv[2]
d=json.load(open(cj))
any_model=False
for c in d.get("characters",[]):
    m=c.get("model")
    if not m: continue
    any_model=True
    rel=m.replace("res://","")
    ok="exists ✓" if os.path.isfile(os.path.join(g,rel)) else "FILE MISSING ✗"
    print(f"   {c.get('id','?'):10} -> {m}   [{ok}]")
if not any_model:
    print("   (no character has a 'model:' path — the tool's merge didn't assign one;")
    print("    re-write with a model tagged 'character' and a matching roster id)")
PY
else
  echo "   characters.json not found at $CJ"
fi
echo

# stray nested folder = the tool was pointed at the godot/ folder, not the repo root
if [ -d "$G/godot/assets" ]; then
  echo "!! Found $G/godot/assets — you connected the 'godot' folder in the tool, not the"
  echo "   repo root. Move those files up to $G/assets/, or reconnect to the repo root."
fi
echo "== done. If models say NOT imported, relaunch with: bash scripts/previz-run.sh"
