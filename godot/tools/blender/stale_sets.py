#!/usr/bin/env python3
"""stale_sets.py — which locale GLBs are older than their builders (2026-10-27).

The Deck: "figures still poking out through glass case. thought this was
fixed" and a back office drawn as floating pictures over a void — the fixes
were in the builders, and the Deck's GLBs had not been rebuilt since. File
times can't tell (a `git pull` touches every builder it changes, and a GLB
copied in looks new), so this compares each GLB's time with the time of the
builder's last COMMIT — and of the shared modules it imports from this
folder (build_small_wood_farmhouse builds the ranch's rooms, so a ranch
change makes the farmhouse stale too).

    python3 godot/tools/blender/stale_sets.py            # the stale sets, one per line
    python3 godot/tools/blender/stale_sets.py --verbose  # with the times

rebuild_all_locales.sh --stale rebuilds exactly these.
"""
import os
import re
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
LOC = os.path.join(HERE, "locales")
GLB = os.path.normpath(os.path.join(HERE, "..", "..", "assets", "3d", "locales"))


def commit_time(path):
    try:
        out = subprocess.run(["git", "log", "-1", "--format=%ct", "--", path], cwd=HERE,
                             capture_output=True, text=True, timeout=30).stdout.strip()
        return int(out) if out else 0
    except Exception:
        return 0


def local_deps(path):
    """The builders this one imports from the locales folder."""
    deps = []
    try:
        src = open(path, encoding="utf-8").read()
    except OSError:
        return deps
    for m in re.finditer(r"^\s*import (build_\w+)|^\s*from (build_\w+) import", src, re.M):
        name = m.group(1) or m.group(2)
        p = os.path.join(LOC, name + ".py")
        if os.path.exists(p):
            deps.append(p)
    return deps


def glb_of(path):
    """The GLB a builder writes (its export path), else build_<name> -> <name>.glb."""
    try:
        src = open(path, encoding="utf-8").read()
    except OSError:
        src = ""
    m = re.search(r"assets/3d/locales/(\w+)\.glb", src)
    name = m.group(1) if m else os.path.basename(path)[6:-3]
    return os.path.join(GLB, name + ".glb")


def main():
    verbose = "--verbose" in sys.argv
    stale = []
    for fn in sorted(os.listdir(LOC)):
        if not (fn.startswith("build_") and fn.endswith(".py")):
            continue
        path = os.path.join(LOC, fn)
        glb = glb_of(path)
        t_src = max([commit_time(path)] + [commit_time(d) for d in local_deps(path)])
        t_glb = os.path.getmtime(glb) if os.path.exists(glb) else 0
        if t_glb < t_src:
            stale.append(fn[6:-3])
            if verbose:
                print("%-36s glb %s · builder committed %s" % (fn[6:-3], int(t_glb) or "missing", t_src))
            else:
                print(fn[6:-3])
    if verbose:
        print("\n%d stale set(s)" % len(stale))


if __name__ == "__main__":
    main()
