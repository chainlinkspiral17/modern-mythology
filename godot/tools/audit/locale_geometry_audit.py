#!/usr/bin/env python3
"""Locale geometry audit — find the stumps.

louisiana_road, the game's most-seen backdrop (67 instances), turned
out to be 48 metres of road with a flat "sky backdrop" panel standing
33 metres in front of the camera. It read as a stump because it WAS a
stump, and nothing caught it for months. This finds the rest.

It runs every Blender locale builder with the bpy layer stubbed out,
records every make_box / make_cyl call, and reports per locale:

  · the geometry's bounding box
  · HOW FAR IT EXTENDS ALONG THE CAMERA'S VIEW DIRECTION — the number
    that decides whether a space reads as deep or as a diorama
  · BACKDROP WALLS: a large, thin, upright slab standing near the
    camera. Painting the horizon onto a panel a few metres out is
    what makes a view stop dead.

Blender build frame per _3D_MODELING_PLAYBOOK: Z-up, +Y into the
room. glTF->Godot remaps (x, z, -y), so a preset's camera_origin
(gx, gy, gz) sits at Blender (gx, -gz, gy) and looks down Blender
-Y rotated by the preset's yaw.

    python3 godot/tools/audit/locale_geometry_audit.py [--all]

Without --all only the flagged locales print.
"""
import math
import os
import re
import runpy
import sys
import types

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
BLENDER = os.path.join(ROOT, "tools", "blender")
LOCALES = os.path.join(BLENDER, "locales")
BG3D = os.path.join(ROOT, "scripts", "vn", "Background3D.gd")

# An EXTERIOR whose view stops closer than this is a diorama. There
# is deliberately no interior depth test — a kitchen is 4m deep and
# that is correct; flagging it would bury the real finds.
SHALLOW_EXTERIOR_M = 120.0
EXTERIOR_BBOX_M = 40.0
# A backdrop wall is a large thin upright slab with NOTHING BEHIND
# IT — the painted end of the world. A big thin slab with geometry
# past it is just a wall, which is fine and normal.
BACKDROP_MIN_SPAN = 18.0
BACKDROP_MAX_THICK = 0.6
BACKDROP_MIN_HEIGHT = 3.0
BACKDROP_BEHIND_FRAC = 0.04
BACKDROP_HORIZON_SPAN = 60.0
NAME_HINT = re.compile(r"sky|backdrop|horizon|cyclo", re.I)

BOXES = []


def _make_box(name, center, half, color=None, *a, **k):
    BOXES.append((str(name), tuple(float(c) for c in center),
                  tuple(abs(float(h)) for h in half)))
    return types.SimpleNamespace(name=str(name))


def _make_cyl(name, center, radius=1.0, height=1.0, color=None,
              axis='Z', segments=8, *a, **k):
    r, h = abs(float(radius)), abs(float(height))
    half = {'Z': (r, r, h / 2), 'Y': (r, h / 2, r),
            'X': (h / 2, r, r)}.get(str(axis).upper(), (r, r, h / 2))
    BOXES.append((str(name), tuple(float(c) for c in center), half))
    return types.SimpleNamespace(name=str(name))


def _noop(*a, **k):
    return types.SimpleNamespace(name="stub")


def install_stubs():
    """Stand in for every _props.* helper and for bpy itself."""
    bpy = types.ModuleType("bpy")
    for attr in ("ops", "data", "context", "types", "utils"):
        setattr(bpy, attr, types.SimpleNamespace())
    sys.modules["bpy"] = bpy
    sys.modules["mathutils"] = types.ModuleType("mathutils")

    pkg = types.ModuleType("_props")
    pkg.__path__ = []
    sys.modules["_props"] = pkg

    class _Any(types.ModuleType):
        def __getattr__(self, item):
            if item == "make_box":
                return _make_box
            if item == "make_cyl":
                return _make_cyl
            return _noop

    # Discover the real _props.* module names instead of guessing —
    # a hardcoded list silently skipped 66 of 81 builders on the
    # first run, which would have hidden every stump but one.
    names = set()
    props_dir = os.path.join(BLENDER, "_props")
    if os.path.isdir(props_dir):
        names |= {f[:-3] for f in os.listdir(props_dir)
                  if f.endswith(".py") and not f.startswith("__")}
    for f in os.listdir(LOCALES):
        if f.endswith(".py"):
            src = open(os.path.join(LOCALES, f)).read()
            names |= set(re.findall(r"from _props\.([a-z_0-9]+) import", src))
            names |= set(re.findall(r"from _props import ([a-z_0-9]+)", src))
    for sub in sorted(names):
        m = _Any("_props." + sub)
        sys.modules["_props." + sub] = m
        setattr(pkg, sub, m)


def camera_presets():
    """preset id -> (origin Vector3 tuple, yaw radians, scene path)."""
    src = open(BG3D).read()
    out = {}
    for m in re.finditer(
            r'"([a-z0-9_]+)":\s*\{(.*?)\n\t\},', src, re.S):
        pid, body = m.group(1), m.group(2)
        sm = re.search(r'"scene":\s*"res://scenes/locales/([a-z0-9_]+)\.tscn"',
                       body)
        om = re.search(r'"camera_origin":\s*Vector3\(([-\d.]+),\s*([-\d.]+),'
                       r'\s*([-\d.]+)\)', body)
        if not (sm and om):
            continue
        ym = re.search(r'"camera_rotation":\s*Vector3\([^,]+,\s*'
                       r'deg_to_rad\(([-\d.]+)\)', body)
        yaw = math.radians(float(ym.group(1))) if ym else 0.0
        out.setdefault(sm.group(1), []).append(
            (pid, tuple(float(om.group(i)) for i in (1, 2, 3)), yaw))
    return out


def run_builder(path):
    BOXES.clear()
    mod_dir = os.path.dirname(path)
    if mod_dir not in sys.path:
        sys.path.insert(0, mod_dir)
    try:
        g = runpy.run_path(path, run_name="_audit")
    except Exception as e:
        return None, "%s: %s" % (type(e).__name__, e)
    # builders gate their work behind main(); call every build_* fn
    fns = [v for k, v in g.items()
           if k.startswith("build_") and callable(v)]
    for fn in fns:
        try:
            fn()
        except TypeError:
            pass          # takes args — part of a larger composition
        except Exception:
            pass
    return list(BOXES), None


def analyse(boxes, cams):
    xs0 = min(c[0] - h[0] for _, c, h in boxes)
    xs1 = max(c[0] + h[0] for _, c, h in boxes)
    ys0 = min(c[1] - h[1] for _, c, h in boxes)
    ys1 = max(c[1] + h[1] for _, c, h in boxes)
    zs1 = max(c[2] + h[2] for _, c, h in boxes)
    report = {"bbox": (xs1 - xs0, ys1 - ys0, zs1), "reach": None,
              "backdrops": []}
    if cams:
        best = 0.0
        for _pid, (gx, gy, gz), yaw in cams:
            # Godot (x,y,z) -> Blender (x, -z, y); view is Blender -Y
            # turned by the preset yaw (yaw 180 looks up +Y).
            bx, by = gx, -gz
            vx, vy = -math.sin(yaw), -math.cos(yaw)
            far = 0.0
            for _n, c, h in boxes:
                d = (c[0] - bx) * vx + (c[1] - by) * vy
                far = max(far, d + max(h[0], h[1]))
            best = max(best, far)
        report["reach"] = best
        for n, c, h in boxes:
            span = max(h[0], h[1]) * 2
            thick = min(h[0], h[1]) * 2
            if thick > BACKDROP_MAX_THICK or h[2] * 2 < BACKDROP_MIN_HEIGHT:
                continue
            # A wall with nothing behind it is only a FAULT if it is
            # standing in for the horizon. A 22m 'House_Wall' behind a
            # porch is architecture and correctly ends the view; a
            # 104m slab named 'Sky' is a painted backdrop.
            if not (NAME_HINT.search(n) or span >= BACKDROP_HORIZON_SPAN):
                continue
            for _pid, (gx, gy, gz), yaw in cams:
                bx, by = gx, -gz
                vx, vy = -math.sin(yaw), -math.cos(yaw)
                d = (c[0] - bx) * vx + (c[1] - by) * vy
                if d <= 0:
                    continue
                # THE TEST: how much of the locale lies beyond it?
                behind = sum(
                    1 for _n2, c2, _h2 in boxes
                    if (c2[0] - bx) * vx + (c2[1] - by) * vy > d + 1.0)
                if behind <= max(2, int(len(boxes) * BACKDROP_BEHIND_FRAC)):
                    report["backdrops"].append((n, d, span, behind))
                break
    return report


def main():
    show_all = "--all" in sys.argv
    install_stubs()
    cams = camera_presets()
    rows, errs = [], []
    for f in sorted(os.listdir(LOCALES)):
        if not (f.startswith("build_") and f.endswith(".py")):
            continue
        name = f[6:-3]
        boxes, err = run_builder(os.path.join(LOCALES, f))
        if err:
            errs.append((name, err))
            continue
        if not boxes:
            continue
        rows.append((name, analyse(boxes, cams.get(name, [])), len(boxes)))

    flagged = []
    for name, r, n in rows:
        why = []
        if r["backdrops"]:
            bn, bd, bs, bh = r["backdrops"][0]
            why.append("BACKDROP %r %.0fm out, %.0fm wide, %d parts behind it"
                       % (bn, bd, bs, bh))
        outdoor = max(r["bbox"][0], r["bbox"][1]) > EXTERIOR_BBOX_M
        if r["reach"] is not None and outdoor and r["reach"] < SHALLOW_EXTERIOR_M:
            why.append("exterior view stops at %.0fm" % r["reach"])
        if why:
            flagged.append((name, why, r, n))

    print("locale_geometry_audit · %d builders, %d with camera presets"
          % (len(rows), sum(1 for n, _, _ in rows if cams.get(n))))
    if show_all:
        for name, r, n in rows:
            print("  %-30s %5d parts  bbox %5.0fx%-5.0f reach %s"
                  % (name, n, r["bbox"][0], r["bbox"][1],
                     "%.0fm" % r["reach"] if r["reach"] is not None else "-"))
    print("\n%d flagged:" % len(flagged))
    for name, why, r, n in flagged:
        print("  · %-28s %s" % (name, "; ".join(why)))
    if errs:
        print("\n%d builder(s) would not run headless:" % len(errs))
        for name, e in errs[:8]:
            print("    %-28s %s" % (name, e[:70]))
    return 0


if __name__ == "__main__":
    sys.exit(main())
