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

# A builder is stale when its GLB is older than the builder OR than any
# _props kit it imports (2026-09-24: this compared the builder alone, so
# a KIT fix — the grounded horizon bands, the open glass cases — never
# rebuilt a caller whose own file did not change), or when the GLB has
# no vertex colours (2026-09-24: the white rooms — see
# tools/audit/glb_color_check.py). Last GIT COMMIT time per file, or the
# file's mtime when it has uncommitted edits.
while IFS=' ' read -r kind name; do
    case "$kind" in
        MISSING) missing+=("$name") ;;
        STALE)   stale+=("$name") ;;
    esac
done < <(python3 - "$GLB_DIR" <<'PY'
import glob, os, re, subprocess, sys
glb_dir = sys.argv[1]
sys.path.insert(0, os.path.join("..", "audit"))
try:
    import glb_color_check as G
except Exception:
    G = None
_t = {}
def src_time(path):
    if path not in _t:
        out = subprocess.run(["git", "log", "-1", "--format=%ct", "--", path],
                             capture_output=True, text=True).stdout.strip()
        t = int(out) if out else 0
        try:
            t = max(t, int(os.stat(path).st_mtime))
        except OSError:
            pass
        _t[path] = t
    return _t[path]
IMP = re.compile(r"from _props(?:\.([a-z_0-9]+))? import ([a-zA-Z_0-9, ()\n]+)")
REL = re.compile(r"from \.([a-z_0-9]+) import")
def kit_deps(src):
    mods = set()
    for m in IMP.finditer(src):
        if m.group(1):
            mods.add(m.group(1))
        else:
            mods |= {w.strip().split(" ")[0] for w in m.group(2).replace("(", "").replace(")", "").split(",")}
    if mods:
        mods.add("geometry")          # export_glb lives there
    for mod in list(mods):            # one level of kit-to-kit imports
        mp = os.path.join("_props", mod + ".py")
        if os.path.exists(mp):
            mods |= set(REL.findall(open(mp).read()))
    return [os.path.join("_props", m + ".py") for m in mods if os.path.exists(os.path.join("_props", m + ".py"))]
for f in sorted(glob.glob("locales/build_*.py")):
    name = os.path.basename(f)[6:-3]
    glb = os.path.join(glb_dir, name + ".glb")
    if not os.path.isfile(glb):
        print("MISSING", name); continue
    t = max([src_time(f)] + [src_time(k) for k in kit_deps(open(f).read())])
    if t > int(os.stat(glb).st_mtime) or (G and G.check(glb)[0] != "ok"):
        print("STALE", name)
PY
)

if [ "${#missing[@]}" -gt 0 ]; then
    echo "── NEVER BUILT (${#missing[@]}) ──"
    printf '  %s\n' "${missing[@]}"
fi
if [ "${#stale[@]}" -gt 0 ]; then
    echo "── STALE (${#stale[@]}) — builder or a kit it imports newer than the GLB, or the GLB lost its colours ──"
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
