#!/usr/bin/env bash
# THE SCOPED SUITE (2026-10-13). The user: "audit taking over an hour for
# simple fixes." run_all_audits.sh records every locale builder several
# times over (the marker sightline gate alone is ~40 min) — and a prompt
# edit in the Hero Studio roster, a portrait shader, a Drive script or a
# playbook cannot move a single box in any locale.
#
# This looks at what changed (commits not yet on the remote branch, plus
# the working tree) and:
#   · if EVERYTHING is in the light set below → runs the checks those files
#     can fail (Python compiles, JSON parses, GDScript passes gdparse +
#     gdinfer_check, shell scripts parse, .tscn syntax) — seconds;
#   · if ANYTHING else changed (a builder, a locale .tscn, chapter JSON,
#     Background3D / the director, audio, the audits themselves) → runs the
#     full run_all_audits.sh, unchanged.
#
#   bash godot/tools/audit/run_changed_audits.sh            # vs origin/claude/3d-locales-clean
#   bash godot/tools/audit/run_changed_audits.sh <base>     # vs another ref
#   FULL=1 bash godot/tools/audit/run_changed_audits.sh     # always the whole suite
set -uo pipefail
cd "$(dirname "${BASH_SOURCE[0]}")/../../.."
BASE="${1:-origin/claude/3d-locales-clean}"

# Files no audit in run_all_audits.sh reads to judge the world's geometry,
# cameras, story wiring or audio: tools, the portrait + hero-art runtime,
# docs. Anything not matched here sends the run to the full suite.
LIGHT='^(godot/tools/meshy_[^/]*|godot/tools/meshy_roster\.json|godot/tools/hero_uploader/.*|godot/tools/drive_[^/]*|godot/tools/audit/drive_(write_audit|guard_test)\.py|godot/tools/[^/]*\.sh|godot/tools/Portrait[^/]*|godot/tools/(VN|Vn)[^/]*|godot/tools/ArtReview[^/]*|godot/tools/portraits/.*|godot/scripts/vn/(Portrait3D|HeroArt)\.gd|godot/scripts/HeroProp\.gd|godot/assets/shaders/portrait_[^/]*|godot/assets/art/hero/README\.md|godot/tools/audit/run_changed_audits\.sh|.*\.md|\.gitignore)$'

# the Drive gates run on EVERY change, light or not (2026-10-13)
python3 godot/tools/audit/drive_write_audit.py || { echo "EXIT 1"; exit 1; }
python3 godot/tools/audit/drive_guard_test.py | tail -1
python3 godot/tools/audit/drive_guard_test.py >/dev/null || { echo "EXIT 1"; exit 1; }

CHANGED="$( { git diff --name-only "$BASE"...HEAD 2>/dev/null; git diff --name-only; git diff --name-only --cached;
              git ls-files --others --exclude-standard; } | sort -u | grep -v '^$' )"
if [ -z "$CHANGED" ]; then
    echo "nothing changed against $BASE"; echo "EXIT 0"; exit 0
fi
HEAVY="$(echo "$CHANGED" | grep -Ev "$LIGHT" || true)"
if [ -n "${FULL:-}" ] || [ -n "$HEAVY" ]; then
    [ -n "$HEAVY" ] && { echo "full suite — these can move the world:"; echo "$HEAVY" | head -20 | sed 's/^/   /'; }
    bash godot/tools/audit/run_all_audits.sh
    exit $?
fi

echo "scoped checks — $(echo "$CHANGED" | wc -l | tr -d ' ') changed file(s), none of them geometry, cameras, story or audio:"
FAIL=0
while IFS= read -r f; do
    [ -f "$f" ] || continue                       # deleted
    case "$f" in
        *.py)   python3 -m py_compile "$f" 2>&1 && echo "   ok  py   $f" || { echo "   FAIL py   $f"; FAIL=1; } ;;
        *.json) python3 -c "import json,sys; json.load(open(sys.argv[1]))" "$f" 2>&1 && echo "   ok  json $f" || { echo "   FAIL json $f"; FAIL=1; } ;;
        *.sh)   bash -n "$f" 2>&1 && echo "   ok  sh   $f" || { echo "   FAIL sh   $f"; FAIL=1; } ;;
        *.gd)   { gdparse "$f" >/dev/null && python3 godot/tools/gdinfer_check.py "$f" | grep -q " 0 suspect"; } \
                    && echo "   ok  gd   $f" || { echo "   FAIL gd   $f (gdparse / gdinfer_check)"; FAIL=1; } ;;
        *.tscn) python3 godot/tools/audit/tscn_syntax_audit.py >/dev/null 2>&1 \
                    && echo "   ok  tscn $f" || { echo "   FAIL tscn $f (tscn_syntax_audit)"; FAIL=1; } ;;
        *)      echo "   --  $f" ;;
    esac
done <<< "$CHANGED"
# the roster must still load through the pipeline's own validator
if echo "$CHANGED" | grep -q "meshy_roster.json\|meshy_pipeline.py"; then
    python3 -c "import sys; sys.path.insert(0,'godot/tools'); import meshy_pipeline as M; M.load_roster()" \
        && echo "   ok  roster loads (meshy_pipeline.load_roster)" || { echo "   FAIL roster"; FAIL=1; }
fi
echo "EXIT $FAIL"
exit $FAIL
