#!/usr/bin/env python3
"""Marker-aim audit — does each shot marker actually SEE its object?

Born 2026-08-19, the day a hand-authored wave of insert markers
shipped with INVERTED YAW: the miller_kitchen phone marker faced
+Z while the phone hung at −Z — the "phone insert" framed the
opposite wall. VnDirector applies `cam.global_transform =
marker.global_transform` and a Godot camera looks down its −Z, so
a marker's pose is a camera pose, and aim errors are invisible
until someone renders the shot on the Deck.

For every locale tscn with vn_shot markers, this audit:
  1. records the builder's geometry (same recorder as the overlap
     audit) and converts blender → godot (gx, gy, gz = bx, bz, −by);
  2. parses each marker's position + rotation (YXZ euler, Godot's
     order) and computes its forward = R @ (0, 0, −1);
  3. for shot_insert_<id> / shot_closeup_<id>, finds geometry whose
     name matches the id (shot_marker_audit's SYNONYMS) and checks
     the NEAREST match sits inside the camera's forward cone;
  4. for markers with no nameable object (establish variants,
     abstract ids), checks that ANY geometry is in the cone — the
     preset-vantage rule at marker scale.

A marker whose named object exists but sits OUTSIDE the cone is a
MISAIM and fails the suite. Nonzero exit on any misaim.

Usage:
    python3 godot/tools/audit/marker_aim_audit.py            # all
    python3 godot/tools/audit/marker_aim_audit.py <locale>…  # some
"""
import math
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import prop_overlap_audit as P  # record_builder + audit stubs
from shot_marker_audit import SYNONYMS

ROOT = os.path.normpath(os.path.join(HERE, "..", ".."))
LOCALES_TSCN = os.path.join(ROOT, "scenes", "locales")
BUILDERS = os.path.join(ROOT, "tools", "blender", "locales")

CONE_DEG = 38.0        # half-angle · insert lenses are tight but a
                       # named object should be near frame center
NEAR_MAX = 40.0        # an insert subject more than 40m out is a miss
ANY_CONE_DEG = 55.0    # abstract markers: anything in a wide cone

MARKER_RE = re.compile(
    r'\[node name="(shot_[\w]+)"[^\]]*groups=\["vn_shot"\][^\]]*\]'
    r'(.*?)(?=\n\[|\Z)', re.S)
TR_RE = re.compile(r'transform = Transform3D\(([^)]+)\)')
ROT_RE = re.compile(r'rotation = Vector3\(([^)]+)\)')


def yxz_forward(rx, ry, rz):
    """Godot YXZ euler → the camera's forward (-Z) in world space."""
    cx, sx = math.cos(rx), math.sin(rx)
    cy, sy = math.cos(ry), math.sin(ry)
    cz, sz = math.cos(rz), math.sin(rz)
    # R = Ry @ Rx @ Rz ; forward = R @ (0, 0, -1)
    # Column-major expansion of R applied to (0,0,-1):
    fx = -(sy * cx)
    fy = sx
    fz = -(cy * cx)
    return (fx, fy, fz)


def parse_markers(tscn_path):
    src = open(tscn_path).read()
    out = []
    for m in MARKER_RE.finditer(src):
        name, body = m.group(1), m.group(2)
        tm = TR_RE.search(body)
        if not tm:
            continue
        vals = [float(v) for v in tm.group(1).split(",")]
        pos = tuple(vals[9:12])
        rot = (0.0, 0.0, 0.0)
        rm = ROT_RE.search(body)
        if rm:
            rot = tuple(float(v) for v in rm.group(1).split(","))
        out.append((name, pos, rot))
    return out


_STUBS_READY = False


def geometry_godot(locale):
    # record_builder alone leaves the composite _props modules
    # un-stubbed — install_stubs() is what executes the whitelist
    # for real. Skipping it silently records ~nothing but the
    # builder's own make_box calls (this audit's first run saw 71
    # of cabin_road's objects and zero drones).
    global _STUBS_READY
    if not _STUBS_READY:
        P.A.install_stubs()
        _STUBS_READY = True
    path = os.path.join(BUILDERS, "build_%s.py" % locale)
    if not os.path.exists(path):
        return None
    boxes, err = P.record_builder(path)
    if boxes is None:
        return None
    out = []
    # BOXES rows are (name, CENTER, half_sizes) — not (lo, hi).
    # Averaging center with half_sizes halved every coordinate and
    # this audit's first verdicts were computed against a world at
    # 50% scale. Blender center → godot: (x, z, −y).
    for name, center, _half in boxes:
        out.append((name, (center[0], center[2], -center[1])))
    return out


def matches_for(cue_id, geo):
    stems = [s for s in SYNONYMS.get(cue_id, []) + [cue_id, cue_id.rstrip("s")]
             if len(s) >= 3]
    # Single words match name PARTS exactly ("crow" must not match
    # "Crown"); multi-word stems (pot_roast) match the flattened name.
    words = {s for s in stems if "_" not in s}
    flats = {s.replace("_", "") for s in stems if "_" in s}
    hits = []
    for name, pos in geo:
        parts = name.lower().split("_")
        flat = name.lower().replace("_", "")
        if any(p == w or p == w + "s" for p in parts for w in words) or \
                any(f in flat for f in flats):
            hits.append((name, pos))
    return hits


def angle_to(pos, fwd, target):
    dx = target[0] - pos[0]
    dy = target[1] - pos[1]
    dz = target[2] - pos[2]
    d = math.sqrt(dx * dx + dy * dy + dz * dz)
    if d < 1e-6:
        return 0.0, 0.0
    dot = (dx * fwd[0] + dy * fwd[1] + dz * fwd[2]) / d
    dot = max(-1.0, min(1.0, dot))
    return math.degrees(math.acos(dot)), d


def main():
    only = [a for a in sys.argv[1:] if not a.startswith("-")]
    misaims = []
    checked = 0
    for fn in sorted(os.listdir(LOCALES_TSCN)):
        if not fn.endswith(".tscn"):
            continue
        locale = fn[:-5]
        if only and locale not in only:
            continue
        markers = parse_markers(os.path.join(LOCALES_TSCN, fn))
        if not markers:
            continue
        geo = geometry_godot(locale)
        if not geo:
            continue
        for name, pos, rot in markers:
            fwd = yxz_forward(*rot)
            m = re.match(r"shot_(insert|closeup)_(\w+)$", name)
            checked += 1
            if m:
                cue_id = m.group(2)
                hits = matches_for(cue_id, geo)
                if hits:
                    # The SUBJECT is the nearest matching object —
                    # min-by-angle once matched a same-named object
                    # 200m away that happened to sit near the axis
                    # and made a bad marker look aimed.
                    best = min(hits, key=lambda h: angle_to(pos, fwd, h[1])[1])
                    ang, dist = angle_to(pos, fwd, best[1])
                    if ang > CONE_DEG or dist > NEAR_MAX:
                        misaims.append((locale, name, best[0], ang, dist))
                    continue
            # No nameable object — anything in a wide cone counts.
            in_cone = 0
            for _gn, gp in geo:
                ang, dist = angle_to(pos, fwd, gp)
                if ang <= ANY_CONE_DEG and dist <= 150.0:
                    in_cone += 1
            if in_cone < 3:
                misaims.append((locale, name, "(anything)", 999.0, 0.0))

    print("marker_aim_audit · %d marker(s) checked" % checked)
    if misaims:
        for locale, name, target, ang, dist in misaims:
            if ang >= 999.0:
                print("MISAIM  %-26s %-28s sees nothing at all" % (locale, name))
            else:
                print("MISAIM  %-26s %-28s → %s is %.0f° off axis (%.1fm)" %
                      (locale, name, target, ang, dist))
        print("%d misaimed marker(s)" % len(misaims))
        sys.exit(1)
    print("0 misaims: every marker sees its subject")


if __name__ == "__main__":
    main()
