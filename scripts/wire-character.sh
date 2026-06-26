#!/usr/bin/env bash
# Assign a .glb model to a character roster slot in characters.json.
# (This is the part the browser tool's "merge" was supposed to do.)
#
# Usage:   bash scripts/wire-character.sh <roster-id> <model-filename>
# Example: bash scripts/wire-character.sh nono nono.glb
#
# Run with no args to list the roster ids you can target.
set -uo pipefail
REPO="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
CJ="$REPO/godot/scenes/previz/data/characters.json"
MODELS="$REPO/godot/assets/models"

if [ ! -f "$CJ" ]; then echo "!! characters.json not found at $CJ"; exit 1; fi

if [ -z "${1:-}" ]; then
  echo "roster ids you can target (band — id):"
  python3 - "$CJ" <<'PY'
import json,sys
d=json.load(open(sys.argv[1]))
for c in d.get("characters",[]):
    if c.get("zone")=="stage":
        tag=" <- has model" if c.get("model") else ""
        print(f"   {c.get('band','?'):20} {c.get('id','?')}{tag}")
PY
  echo
  echo "usage: bash scripts/wire-character.sh <roster-id> <model-filename-in-assets/models>"
  exit 0
fi

ID="$1"; FILE="${2:-}"
if [ -z "$FILE" ]; then echo "!! give a model filename, e.g. nono.glb"; exit 1; fi
if [ ! -f "$MODELS/$FILE" ]; then
  echo "!! $MODELS/$FILE not found. Copy it in first:  bash scripts/import-assets.sh <folder>"
  exit 1
fi

python3 - "$CJ" "$ID" "$FILE" <<'PY'
import json,sys
cj,cid,fn=sys.argv[1],sys.argv[2],sys.argv[3]
d=json.load(open(cj))
hit=None
for c in d.get("characters",[]):
    if c.get("id")==cid: hit=c; break
if not hit:
    print(f"!! no character with id '{cid}'. Run with no args to list ids."); sys.exit(1)
hit["model"]=f"res://assets/models/{fn}"
json.dump(d,open(cj,"w"),indent=2)
print(f">> {cid} now uses res://assets/models/{fn}")
PY

echo ">> done. Launch:  bash scripts/previz-run.sh   (imports + opens the scene)"
