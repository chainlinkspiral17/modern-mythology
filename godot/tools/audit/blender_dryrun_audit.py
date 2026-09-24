#!/usr/bin/env python3
"""blender_dryrun_audit — run every locale builder through its REAL kit
code, outside Blender, against a small stand-in `bpy`.

Why (2026-09-24): every other gate runs builders under the RECORDER,
whose stubs accept any arguments. A builder that dies in Blender — a
comment pasted mid-call that swallowed make_cyl's colour, a renamed
variable — passes every gate and simply leaves its GLB missing on the
Deck. Two did: chillwave_interior and missing_link_exterior had been
failing in Blender since the twelfth support pass.

This runs each builder as __main__ in its own process with
godot/tools/audit/blender_dryrun/ first on sys.path (bpy + mathutils
stand-ins: meshes are built from the kits' real vertex lists; faces are
checked for out-of-range or repeated indices, which crash from_pydata).
A builder must reach export_glb with no exception and no bad mesh.

    python3 godot/tools/audit/blender_dryrun_audit.py            # all
    python3 godot/tools/audit/blender_dryrun_audit.py <name>...  # some
Nonzero exit if any builder fails.
"""
import glob, os, subprocess, sys

HERE = os.path.dirname(os.path.abspath(__file__))
LOCALES = os.path.normpath(os.path.join(HERE, "..", "blender", "locales"))
FAKE = os.path.join(HERE, "blender_dryrun")

RUNNER = r'''
import sys, os, runpy, traceback
sys.path.insert(0, %(fake)r)
import bpy
path = sys.argv[1]
os.chdir(os.path.dirname(path))
sys.argv = [path]
try:
    runpy.run_path(path, run_name="__main__")
    ok = "export" in bpy.STATS
    print("RESULT", "OK" if (ok and not bpy.STATS["bad"]) else ("BAD-MESH" if bpy.STATS["bad"] else "NO-EXPORT"),
          bpy.STATS["meshes"], bpy.STATS["bad"][:2])
except SystemExit as e:
    print("RESULT EXIT", e.code)
except Exception as e:
    tb = traceback.extract_tb(sys.exc_info()[2])[-1]
    print("RESULT ERROR %%s: %%s @ %%s:%%d" %% (type(e).__name__, str(e)[:160], os.path.basename(tb.filename), tb.lineno))
finally:
    t = bpy.STATS.get("touched")
    if t and os.path.exists(t) and os.path.getsize(t) == 0:
        os.remove(t)
'''


def main():
    names = sys.argv[1:] or sorted(os.path.basename(f)[6:-3] for f in glob.glob(os.path.join(LOCALES, "build_*.py")))
    code = RUNNER % {"fake": FAKE}
    bad = []
    for n in names:
        path = os.path.join(LOCALES, "build_%s.py" % n)
        try:
            out = subprocess.run([sys.executable, "-c", code, path], capture_output=True, text=True, timeout=900).stdout
        except subprocess.TimeoutExpired:
            out = "RESULT TIMEOUT"
        res = [l for l in out.splitlines() if l.startswith("RESULT")]
        line = res[-1] if res else "RESULT NO-RESULT"
        if not line.startswith("RESULT OK"):
            bad.append((n, line))
            print("FAIL  %-30s %s" % (n, line[7:]))
    print("\nblender_dryrun_audit · %d builder(s) · %d fail(s)" % (len(names), len(bad)))
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
