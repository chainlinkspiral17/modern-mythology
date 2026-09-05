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


def _make_box(name, center, size, color=None, *a, **k):
    # `size` is FULL extents — every real make_box (both the _props
    # one and the vendored model-chapter copies) halves internally.
    # Recording it unhalved inflated every box 2x for the audit's
    # whole first life: reach was overstated by up to one prop-size,
    # thickness tests ran against doubled walls, and the camera
    # collision checks were double-conservative.
    BOXES.append((str(name), tuple(float(c) for c in center),
                  tuple(abs(float(s)) / 2.0 for s in size)))
    return _obj_stub(name)


def _make_cyl(name, center, radius=1.0, height=1.0, color=None,
              axis='Z', segments=8, *a, **k):
    r, h = abs(float(radius)), abs(float(height))
    half = {'Z': (r, r, h / 2), 'Y': (r, h / 2, r),
            'X': (h / 2, r, r)}.get(str(axis).upper(), (r, r, h / 2))
    BOXES.append((str(name), tuple(float(c) for c in center), half))
    return _obj_stub(name)


class _StubVal(float):
    """Universal stub: builders do arithmetic on helper returns
    (top_z = make_counter(...) + 0.06), read .name off them, call
    them, len() palette constants (len(P.SNACK_TINTS)), and index
    color tuples. A float subclass that answers everything keeps a
    builder's main() running to completion under the stubs."""
    def __getattr__(self, _k):
        return self

    def __call__(self, *a, **k):
        return self

    def __len__(self):
        return 4

    def __getitem__(self, _i):
        return _StubVal(0.5)

    def __setitem__(self, _i, _v):
        pass

    def __index__(self):
        # Lets builder code use a stub as a list index / range bound
        # (graustark indexes a palette list with a helper return).
        return 0

    def __iter__(self):
        return iter((_StubVal(0.5), _StubVal(0.5),
                     _StubVal(0.5), _StubVal(1.0)))


_noop = _StubVal(0.9)


def _obj_stub(name):
    """Recorded-object stand-in. A bare SimpleNamespace(name=...) dies
    the moment builder code touches .data / .scale / any bpy-ish attr
    on a created object (diner did exactly that). _StubVal answers
    every attribute chain, so returning one — with the real .name
    pinned on top — keeps main() running while the recorders still
    capture the geometry."""
    o = _StubVal(0.9)
    try:
        o.name = str(name)
    except Exception:
        pass
    return o


def install_stubs():
    """Stand in for every _props.* helper and for bpy itself."""
    bpy = types.ModuleType("bpy")
    for attr in ("ops", "data", "context", "types", "utils"):
        # _StubVal answers any attribute chain / call / len / index,
        # so direct bpy usage (bpy.data.meshes.new, bpy.context.object)
        # in the hand-rolled builders no-ops instead of raising.
        setattr(bpy, attr, _StubVal(0.9))
    sys.modules["bpy"] = bpy
    mu = types.ModuleType("mathutils")

    class Vector:
        # Minimal stand-in: diner / graustark / riverfront import
        # mathutils.Vector; without it three builders (including a
        # MODEL CHAPTER) were unmeasurable and the audit could not
        # claim completeness.
        def __init__(self, seq=(0.0, 0.0, 0.0)):
            v = list(seq) + [0.0] * (3 - len(list(seq)))
            self.x, self.y, self.z = (float(v[0]), float(v[1]),
                                      float(v[2]))

        def __iter__(self):
            return iter((self.x, self.y, self.z))

        def __getitem__(self, i):
            return (self.x, self.y, self.z)[i]

        def __add__(self, o):
            return Vector((self.x + o[0], self.y + o[1], self.z + o[2]))

        def __sub__(self, o):
            return Vector((self.x - o[0], self.y - o[1], self.z - o[2]))

        def __mul__(self, k):
            return Vector((self.x * k, self.y * k, self.z * k))

        __rmul__ = __mul__

        @property
        def length(self):
            return (self.x ** 2 + self.y ** 2 + self.z ** 2) ** 0.5

        def normalized(self):
            l = self.length or 1.0
            return Vector((self.x / l, self.y / l, self.z / l))

    mu.Vector = Vector
    sys.modules["mathutils"] = mu

    pkg = types.ModuleType("_props")
    pkg.__path__ = []
    sys.modules["_props"] = pkg

    def _rec_prism(name, center, size, color=None, *a, **k):
        return _make_box(name, center, size)

    def _rec_taper(name, center, r_bottom, r_top=0.0, height=1.0,
                   color=None, segments=10, axis='Z', *a, **k):
        return _make_cyl(name, center, max(r_bottom, r_top), height,
                         color, segments, axis)

    def _rec_round(name, center, radius, color=None, *a, **k):
        r = abs(float(radius))
        BOXES.append((str(name),
                      tuple(float(c) for c in center), (r, r, r)))
        return _obj_stub(name)

    def _rec_lathe(name, center, profile, color=None, segments=12, yaw=0.0, loop=False, *a, **k):
        r = max(abs(float(p[0])) for p in profile)
        zs = [float(p[1]) for p in profile]
        cx, cy, cz = (float(c) for c in center)
        BOXES.append((str(name), (cx, cy, cz + (max(zs) + min(zs)) / 2.0),
                      (r, r, (max(zs) - min(zs)) / 2.0)))
        return _obj_stub(name)

    def _rec_prism_poly(name, center, polygon, length, color=None, axis="Z", yaw=0.0, *a, **k):
        import math as _m
        us = [float(p[0]) for p in polygon]; vs = [float(p[1]) for p in polygon]
        if yaw:
            c_, s_ = _m.cos(float(yaw)), _m.sin(float(yaw))
            pts = [(u * c_ - v * s_, u * s_ + v * c_) for u, v in zip(us, vs)]
            us = [p[0] for p in pts]; vs = [p[1] for p in pts]
        hu = (max(us) - min(us)) / 2.0; hv = (max(vs) - min(vs)) / 2.0
        mu = (max(us) + min(us)) / 2.0; mv = (max(vs) + min(vs)) / 2.0
        hl = abs(float(length)) / 2.0
        cx, cy, cz = (float(c) for c in center)
        ax = str(axis).upper()
        if ax == "Z":
            BOXES.append((str(name), (cx + mu, cy + mv, cz), (hu, hv, hl)))
        elif ax == "X":
            BOXES.append((str(name), (cx, cy + mu, cz + mv), (hl, hu, hv)))
        else:
            BOXES.append((str(name), (cx + mu, cy, cz + mv), (hu, hl, hv)))
        return _obj_stub(name)

    def _rec_tube(name, path, radius, color=None, *a, **k):
        r = abs(float(radius))
        xs = [float(p[0]) for p in path]; ys = [float(p[1]) for p in path]; zs = [float(p[2]) for p in path]
        BOXES.append((str(name), ((max(xs) + min(xs)) / 2.0, (max(ys) + min(ys)) / 2.0, (max(zs) + min(zs)) / 2.0),
                      ((max(xs) - min(xs)) / 2.0 + r, (max(ys) - min(ys)) / 2.0 + r, (max(zs) - min(zs)) / 2.0 + r)))
        return _obj_stub(name)

    def _rec_rot_box(name, center, size, color=None, yaw=0.0, pitch=0.0, roll=0.0, *a, **k):
        import math as _m
        cx, cy, cz = (float(c) for c in center)
        hx, hy, hz = (abs(float(s)) / 2.0 for s in size)
        cy_, sy_ = _m.cos(float(yaw)), _m.sin(float(yaw)); cp, sp = _m.cos(float(pitch)), _m.sin(float(pitch))
        cr, sr = _m.cos(float(roll)), _m.sin(float(roll))
        ex = ey = ez = 0.0
        for i in (-1, 1):
            for j in (-1, 1):
                for kk in (-1, 1):
                    dx, dy, dz = i * hx, j * hy, kk * hz
                    dy, dz = dy * cr - dz * sr, dy * sr + dz * cr
                    dx, dz = dx * cp + dz * sp, -dx * sp + dz * cp
                    dx, dy = dx * cy_ - dy * sy_, dx * sy_ + dy * cy_
                    ex, ey, ez = max(ex, abs(dx)), max(ey, abs(dy)), max(ez, abs(dz))
        BOXES.append((str(name), (cx, cy, cz), (ex, ey, ez)))
        return _obj_stub(name)

    def _rec_heightfield(name, origin, cell, heights, color=None, skirt=0.3, *a, **k):
        rows, cols = len(heights), len(heights[0])
        zs = [float(h) for row in heights for h in row]
        lo, hi = min(zs), max(zs) 
        ox, oy, oz = (float(c) for c in origin)
        cell = float(cell); skirt = float(skirt)
        BOXES.append((str(name), (ox + (cols - 1) * cell / 2.0, oy + (rows - 1) * cell / 2.0, oz + (hi + lo - skirt) / 2.0),
                      ((cols - 1) * cell / 2.0, (rows - 1) * cell / 2.0, (hi - lo + skirt) / 2.0)))
        return _obj_stub(name)

    _RECORDERS = {
        "make_box": _make_box, "make_cyl": _make_cyl,
        "make_chamfer_box": _rec_prism, "make_wedge": _rec_prism,
        "make_gable": _rec_prism, "make_taper_cyl": _rec_taper,
        "make_dome": _rec_round, "make_blob": _rec_round,
        # DETAIL DRAFT 1 primitives (2026-09-05)
        "make_lathe": _rec_lathe, "make_prism": _rec_prism_poly,
        "make_tube": _rec_tube, "make_rot_box": _rec_rot_box,
        "make_heightfield": _rec_heightfield,
    }

    class _Any(types.ModuleType):
        def __getattr__(self, item):
            return _RECORDERS.get(item, _noop)

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

    # _props.detail contains REAL geometry logic (make_far_bands lays
    # out the horizon bands). Stubbing it to noops made the audit
    # blind to exactly the fix it demanded — half the patched locales
    # stayed flagged because their bands were never recorded. Execute
    # the real module with its relative geometry import resolving to
    # the recording stub above.
    # Every COMPOSITE prop module belongs here for the same reason:
    # objects.py (bottles/cans/glassware), drones.py (the vol7
    # Oneironautics units) and creatures.py (the crow) emit their
    # geometry through the recording helpers, but only if the module
    # itself RUNS. Stubbed, `make_crow(...)` is a no-op and the audit
    # cannot see the bird at all — three locales' crows recorded ZERO
    # objects before this line was widened (2026-08-12), which also
    # means their clipping went unchecked.
    for real_mod in ("detail", "trees", "objects", "drones",
                     "creatures", "vehicles", "buildings", "furniture", "structure", "shelving", "decor",
                     "food_service", "cleaning", "coolers_drinks",
                     "signage", "store_fixtures", "safety"):
        mpath = os.path.join(BLENDER, "_props", real_mod + ".py")
        if not os.path.exists(mpath):
            continue
        real = types.ModuleType("_props." + real_mod)
        real.__package__ = "_props"
        real.__file__ = mpath
        sys.modules["_props." + real_mod] = real
        setattr(pkg, real_mod, real)
        exec(compile(open(mpath).read(), mpath, "exec"), real.__dict__)


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
        # Yaw is the rotation's second component — written either as
        # deg_to_rad(N) or as raw radians. Matching only the former
        # defaulted raw-radian presets to yaw 0 and produced a false
        # positive (riverfront_park, which looks NW at 0.49 rad, was
        # measured looking S and reported an 18m stump).
        ym = re.search(r'"camera_rotation":\s*Vector3\([^,]+,\s*'
                       r'deg_to_rad\(([-\d.]+)\)', body)
        if ym:
            yaw = math.radians(float(ym.group(1)))
        else:
            ym = re.search(r'"camera_rotation":\s*Vector3\([^,]+,'
                           r'\s*([-\d.]+)\s*,', body)
            yaw = float(ym.group(1)) if ym else 0.0
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
            # Godot camera forward is -Z rotated by yaw about +Y:
            # forward_godot = (-sin y, 0, -cos y). Blender maps
            # (x, -z): forward_blender = (-sin y, +COS y). The
            # original -cos coincided with the truth only at yaw 180
            # (louisiana) — every other preset was measured looking
            # BACKWARD, which hid cabin_road's Sky wall standing
            # 24m in front of the real view.
            bx, by = gx, -gz
            vx, vy = -math.sin(yaw), math.cos(yaw)
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
                vx, vy = -math.sin(yaw), math.cos(yaw)
                d = (c[0] - bx) * vx + (c[1] - by) * vy
                if d <= 0:
                    continue
                # THE TEST: how much of the locale lies beyond it?
                behind = sum(
                    1 for _n2, c2, _h2 in boxes
                    if (c2[0] - bx) * vx + (c2[1] - by) * vy > d + 1.0)
                # Both cases are faults now. A horizon-named slab
                # with nothing behind it is a painted backdrop; one
                # WITH geometry behind it is an OCCLUDER — it hides
                # the horizon that exists (this is how 11 'fixed'
                # exteriors kept their new far bands invisible: the
                # old Sky wall was still standing in front of them).
                report["backdrops"].append((n, d, span, behind))
                break
    return report


def check_gate_position(path):
    """Code after `if __name__ == "__main__": main()` never exists
    when main() runs — Blender executes the file top-to-bottom and
    the gate CALLS main() mid-file. 14 exteriors shipped their
    entire 2026-08 horizon wave as dead code this way: every one
    NameError'd at build time and kept its stale GLB, silently.
    The gate must be the last statement in every builder."""
    lines = open(path).read().split("\n")
    gate = None
    for i, ln in enumerate(lines):
        if ln.startswith("if __name__"):
            gate = i
            break
    if gate is None:
        return None
    for ln in lines[gate + 1:]:
        if ln.startswith(("def ", "class ")) or re.match(r"^[A-Z_]+\s*=", ln):
            return "code after the __main__ gate (dead at build time)"
    return None


def main():
    show_all = "--all" in sys.argv
    install_stubs()
    cams = camera_presets()
    rows, errs = [], []
    for f in sorted(os.listdir(LOCALES)):
        if not (f.startswith("build_") and f.endswith(".py")):
            continue
        name = f[6:-3]
        gate_err = check_gate_position(os.path.join(LOCALES, f))
        if gate_err:
            errs.append((name, gate_err))
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
            kind_s = "OCCLUDER (hides the horizon behind it)" if bh > 2 \
                else "BACKDROP (painted end of the world)"
            why.append("%s %r %.0fm out, %.0fm wide, %d parts behind"
                       % (kind_s, bn, bd, bs, bh))
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
