#!/usr/bin/env python3
"""orphan_practical_audit.py — a practical is a claim about a fixture
(2026-09-18).

Found twice by hand this week: cabin_interior shipped two fluorescent
practicals in a cabin with no electricity, and lena_apartment lit a
desk lamp that had not stood there since the 08-03 rebuild. Both were
derived from a builder of their day and outlived it. The lighting
playbook names practicals after the geometry they belong to
(`<Fixture>_Practical`, or the older `Practical_<Fixture>`) — so the
name is a claim the builder can be asked about.

For every locale scene, run its builder through the audit recorder
and, for every named practical:
  · ORPHAN  — no object the builder emits matches the fixture name;
  · DRIFTED — the nearest matching object is more than DRIFT metres
    from the light (the fixture moved; the light did not).
Unnamed practicals (a `Sodium_S`, a `DiningRoomGlow`) are not claims
and are not checked.

    python3 godot/tools/audit/orphan_practical_audit.py
    python3 godot/tools/audit/orphan_practical_audit.py --all [locale…]

Gate at zero.
"""
import glob
import math
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import prop_overlap_audit as P
import vantage_obstruction_audit as VO

ROOT = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
SCENES = os.path.join(ROOT, "godot", "scenes", "locales")
DRIFT = 1.5     # m · a fixture this far from its light has moved

LIGHT_RX = re.compile(r'\[node name="([^"]+)" type="(OmniLight3D|SpotLight3D)"[^\]]*\](.*?)(?=\n\[|\Z)', re.S)


# A practical whose stem names a FIXTURE is a claim about geometry. One
# whose stem names a spill or a glow (Overhead, JukeboxGlow, Forecourt,
# StreetlampSpill, CounterWarm) is a lighting decision, not a claim,
# and is not checked — the playbook's own examples (DiningRoomGlow,
# SignSpot) are of that kind.
FIXTURE_WORD = re.compile(r"(lamp|bulb|sconce|pendant|chandelier|lantern|fluor|tube|candle|worklight|shoplight|dome|hood|neon|sign)", re.I)


def practical_stem(name):
    if name.endswith("_Practical"):
        stem = name[:-len("_Practical")]
    elif name.startswith("Practical_"):
        stem = name[len("Practical_"):]
    else:
        return None
    return stem if FIXTURE_WORD.search(stem) else None


def light_pos_blender(body):
    pm = re.search(r"position = Vector3\(([^)]+)\)", body)
    tm = re.search(r"transform = Transform3D\(([^)]+)\)", body)
    if pm:
        p = [float(v) for v in pm.group(1).split(",")]
    elif tm:
        v = [float(x) for x in tm.group(1).split(",")]
        p = v[9:12]
    else:
        return None
    return (p[0], -p[2], p[1])


def norm(s):
    return re.sub(r"[^a-z0-9]", "", s.lower())


def matches(stem, boxes):
    """Objects whose name carries the fixture stem. Exact prefix first
    (Lantern_Glass → Lantern_Glass*), then the squashed substring
    (DeskLamp → Desk_Lamp_Head), then the stem's first word alone
    when it is not a bare generic."""
    exact = [b for b in boxes if b[0] == stem or b[0].startswith(stem + "_")]
    if exact:
        return exact
    ns = norm(stem)
    loose = [b for b in boxes if ns and ns in norm(b[0])]
    if loose:
        return loose
    head = stem.split("_")[0]
    if len(head) >= 5 and head.lower() not in ("light", "lamp", "glow"):
        return [b for b in boxes if b[0].split("_")[0] == head]
    return []


def main():
    show_all = "--all" in sys.argv
    only = [a for a in sys.argv[1:] if not a.startswith("--")]
    P.A.install_stubs()
    problems, checked, scenes = [], 0, 0
    for tscn in sorted(glob.glob(os.path.join(SCENES, "*.tscn"))):
        locale = os.path.basename(tscn)[:-5]
        if only and locale not in only:
            continue
        src = open(tscn, encoding="utf-8").read()
        lights = [(m.group(1), m.group(3)) for m in LIGHT_RX.finditer(src)]
        named = [(n, b) for n, b in lights if practical_stem(n)]
        if not named:
            continue
        gm = re.search(r'path="res://assets/3d/locales/(\w+)\.glb"', src)
        glb = gm.group(1) if gm else locale
        boxes = VO.boxes_for(glb)
        if not boxes:
            continue
        scenes += 1
        for n, body in named:
            checked += 1
            stem = practical_stem(n)
            pos = light_pos_blender(body)
            hits = matches(stem, boxes)
            # The name is how a fixture is FOUND; the question is whether
            # one stands where the light is. A fixture of any name within
            # reach answers it (TubeRow_S over a run of Fluor_* tubes).
            if pos is not None:
                anyfix = [b for b in boxes if FIXTURE_WORD.search(b[0]) and not re.search(r"(cord|switch|outlet|wear|stain|glow|halo|zone|^z_)", b[0], re.I)]
                near_any = min((math.dist(pos, b[1]) for b in anyfix), default=99.0)
            else:
                near_any = 99.0
            if not hits and near_any > DRIFT:
                problems.append(("ORPHAN", locale, n, "no fixture within %.1f m; nothing named like '%s' in build_%s" % (DRIFT, stem, glb)))
                continue
            if pos is None:
                continue
            d = min(math.dist(pos, h[1]) for h in hits) if hits else near_any
            if d > DRIFT and near_any > DRIFT:
                near = min(hits, key=lambda h: math.dist(pos, h[1]))[0]
                problems.append(("DRIFTED", locale, n, "%.1f m from %s; no other fixture nearer" % (d, near)))
            elif show_all:
                print("ok      %-26s %-32s %.1f m" % (locale, n, min(d, near_any)))
    for kind, locale, n, why in problems:
        print("%-8s %-26s %-32s %s" % (kind, locale, n, why))
    print("\norphan_practical_audit · %d named practical(s) in %d scene(s) · %d problem(s)"
          % (checked, scenes, len(problems)))
    return 1 if problems else 0


if __name__ == "__main__":
    sys.exit(main())
