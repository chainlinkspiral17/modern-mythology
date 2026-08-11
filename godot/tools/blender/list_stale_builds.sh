#!/usr/bin/env bash
# ════════════════════════════════════════════════════════════════
# list_stale_builds.sh — which locales need a Blender rebuild?
#
# For every locales/build_<name>.py, compares the builder's last
# GIT COMMIT time against the mtime of its GLB
# (godot/assets/3d/locales/<name>.glb). A builder newer than its
# GLB — or a missing GLB — means the on-disk mesh is stale: the
# graustark chapters rendered a month-old world for exactly this
# reason ("check ls -l TIMESTAMPS when a rebuild didn't take").
#
# Run on the Deck after a pull:
#   cd godot/tools/blender && ./list_stale_builds.sh
# It prints the ready-to-paste rebuild loop at the end.
# ════════════════════════════════════════════════════════════════
set -e
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

GLB_DIR="$SCRIPT_DIR/../../assets/3d/locales"
stale=()
missing=()

for f in locales/build_*.py; do
    name="$(basename "$f" .py)"
    name="${name#build_}"
    glb="$GLB_DIR/$name.glb"
    # Last commit touching the builder (falls back to file mtime on
    # a tree with uncommitted edits).
    src_t="$(git log -1 --format=%ct -- "$f" 2>/dev/null || true)"
    file_t="$(stat -c %Y "$f" 2>/dev/null || echo 0)"
    [ -z "$src_t" ] && src_t=0
    [ "$file_t" -gt "$src_t" ] && src_t="$file_t"
    if [ ! -f "$glb" ]; then
        missing+=("$name")
    else
        glb_t="$(stat -c %Y "$glb")"
        if [ "$src_t" -gt "$glb_t" ]; then
            stale+=("$name")
        fi
    fi
done

if [ "${#missing[@]}" -gt 0 ]; then
    echo "── NEVER BUILT (${#missing[@]}) ──"
    printf '  %s\n' "${missing[@]}"
fi
if [ "${#stale[@]}" -gt 0 ]; then
    echo "── STALE (${#stale[@]}) — builder newer than GLB ──"
    printf '  %s\n' "${stale[@]}"
fi

all=("${stale[@]}" "${missing[@]}")
if [ "${#all[@]}" -eq 0 ]; then
    echo "✓ every GLB is newer than its builder — nothing to rebuild"
    exit 0
fi

echo ""
echo "── paste to rebuild all of it ──"
echo "cd $SCRIPT_DIR && for n in ${all[*]}; do ./run_cathedral.sh build_\$n.py; done"
