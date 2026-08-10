#!/usr/bin/env python3
"""Prop-interpenetration audit — find the clipping.

The Gas & Go shipped with a beer fridge buried 0.55m inside the locker
bank and the entire locker row facing INTO the wall (every door,
handle, vent and number plate hidden in the plaster) — "objects
clipping through each other at odd angles." Nothing caught it because
the geometry audit measures reach, not collisions. This does.

For each requested builder it records every emitted box/cyl (both the
shared _props helpers and the vendored make_box copies in the early
hand-rolled builders), then reports pairwise AABB interpenetrations.

Filtering, so intentional contact doesn't drown the real finds:
  · same assembly (shared name prefix up to the last _segment) — a
    drawer inside its dresser is a feature
  · penetration <= EPS (1.5cm) — abutment is not clipping
  · pairs where one name matches WALLISH — doors/windows/signs/trim
    are EMBEDDED in walls on purpose; a prop overlapping a wall by
    more than EMBED_MAX (0.12m = wall thickness) still reports

Usage:
    python3 godot/tools/audit/prop_overlap_audit.py <builder> [...]
    python3 godot/tools/audit/prop_overlap_audit.py --all
"""
import os
import re
import sys
import types

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import locale_geometry_audit as A

EPS = 0.015
EMBED_MAX = 0.12
WALLISH = re.compile(
    r"wall|window|door|sign|brand|partw|partn|part\b|trim|crown|"
    r"baseboard|backsplash|wainscot|frame|sill|floor|ceil|apron|"
    r"turf|road|grass|rug|mat|plumbing|curb|kerb|lawn|drive|sidewalk|path\b|apron|asphalt|edgeline|shoulder|gravel|yard\b|headland|ground", re.I)
CONTAINERISH = re.compile(
    r"cage|case|chest|bin\b|bin_|basket|crate|rack|cooler|fridge|"
    r"freezer|cubby|cart|shelf|shelv|island|hutch|drawer|cab\b|"
    r"cabinet|locker|oven|proofer|tub\b|vase|votive", re.I)
# Objects RESTING on a surface: min-penetration axis is Z and one of
# the pair is a surface. Books sink 2cm into their shelf, a phone
# into its desk — seating, not clipping.
SURFACEISH = re.compile(
    r"shelf|shelv|top\b|_top|desk|table|counter|tray|sill|seat|"
    r"bench|plank|deck\b|worktop|platform|island", re.I)
SEAT_MAX = 0.10
# Structure members joining each other (lattice-tower braces meeting
# legs, railing spindles into rails) — joints, not clipping.
CROWNISH = re.compile(r"crown|canopy|foliage|lobe|frond", re.I)
# Non-solid volumetrics: sprinkler spray arcs, light shafts, steam —
# they interpenetrate everything by design.
NONSOLID = re.compile(r"spray|mist|steam|smoke|shaft|glow|beam\b|dust|fog|surf|foam|wake|"
    r"fall_|veil|cascade|plunge", re.I)
# Infrastructure DESIGNED to be buried — culverts under roads,
# pipes through creek beds, footings in the ground.
BURIEDISH = re.compile(r"culvert|drain|conduit|footing|foundation|piling", re.I)
# Rock against rock — talus piles, jagged outcrops, scree — is
# geology, not clipping.
ROCKISH = re.compile(r"jag|talus|rock|outcrop|boulder|scree|crag|cliff|rim\b|rim_|face\b|face_|gorge|tepui|ledge", re.I)
# Vegetation against vegetation (a shrub against a cypress buttress)
# is undergrowth, not clipping.
PLANTISH = re.compile(r"shrub|bush|hedge|fern|reed|weed|plant|vine|"
                      r"cypress|oak|conifer|tree|myrtle|magnolia|alder|sitka|spruce|"
                      r"cedar|fir\b|pine|birch|willow|green\b|green_|growth|ivy|moss", re.I)
ROOFISH = re.compile(r"eave|ridge|roof|gable|chimney|awning\b", re.I)
STRUCTISH = re.compile(
    r"leg|brace|strut|post|pole|beam|rail|truss|arm\b|_arm|spindle|"
    r"baluster|joist|stud\b|wire|cable|line|rope|cord|string", re.I)


def record_builder(path):
    """Record geometry from a builder, catching BOTH the shared
    _props helpers (via the audit stubs) and vendored local
    make_box/make_cyl definitions (by rebinding build_* globals)."""
    A.BOXES.clear()
    src = open(path).read()
    src = re.sub(r"^if __name__.*$[\s\S]*", "", src, flags=re.M)
    g = {"__name__": "_overlap_probe", "__file__": path}
    mod_dir = os.path.dirname(path)
    if mod_dir not in sys.path:
        sys.path.insert(0, mod_dir)
    try:
        exec(compile(src, path, "exec"), g)
    except Exception as e:
        return None, "%s: %s" % (type(e).__name__, e)

    def rec_box(name, center, size, base_color=None, *a, **k):
        A.BOXES.append((str(name), tuple(float(c) for c in center),
                        tuple(abs(float(s)) / 2.0 for s in size)))
        return types.SimpleNamespace(name=str(name))

    def rec_cyl(name, center, radius, height, base_color=None,
                segments=8, axis='Z', *a, **k):
        r, h = abs(float(radius)), abs(float(height))
        half = {'Z': (r, r, h / 2), 'Y': (r, h / 2, r),
                'X': (h / 2, r, r)}.get(str(axis).upper(), (r, r, h / 2))
        A.BOXES.append((str(name), tuple(float(c) for c in center), half))
        return types.SimpleNamespace(name=str(name))

    if "make_box" in g:
        g["make_box"] = rec_box
    if "make_cyl" in g:
        g["make_cyl"] = rec_cyl
    for noop_name in ("export_glb", "clear_scene"):
        if noop_name in g:
            g[noop_name] = lambda *a, **k: None

    def _rebound(fn):
        return types.FunctionType(fn.__code__, g, fn.__name__,
                                  fn.__defaults__)

    # Run the builder's CANONICAL entrypoint. Calling every build_*
    # alphabetically mis-runs composite builders — kwik_stop's
    # polish passes executed out of order produced 291 phantom
    # pairs. main() is the same sequence Blender runs.
    err = None
    if "main" in g and callable(g.get("main")):
        # main() calls module-level names, which resolve through g —
        # the vendored make_box/export_glb patches above apply.
        try:
            _rebound(g["main"])()
        except Exception as e:
            err = "main(): %s: %s" % (type(e).__name__, e)
    if err or "main" not in g:
        # Fallback sweep: run each build_* individually to recover
        # coverage past the failure point. Name-dedupe (first emit
        # wins) keeps main()'s canonical placements where both ran.
        for fname in sorted(g):
            fn = g[fname]
            if fname.startswith("build_") and callable(fn) and \
                    getattr(fn, "__code__", None) is not None:
                try:
                    _rebound(fn)()
                except Exception:
                    pass
    return list(A.BOXES), err


def overlaps(boxes):
    # Dedupe BY NAME, first emit wins: aggregate build_all()-style
    # functions re-run their children when we call every build_*,
    # and parameterized/seeded placement can re-emit the same name
    # at a shifted position — a phantom copy that pair-checks
    # against the real one. In an actual Blender run duplicate
    # names can't coexist (auto-.001 rename), so name-dedupe is
    # faithful to the real scene.
    seen = set()
    unique = []
    for b in boxes:
        if b[0] not in seen:
            seen.add(b[0])
            unique.append(b)
    boxes = unique
    hits = []
    for i in range(len(boxes)):
        n1, c1, h1 = boxes[i]
        for j in range(i + 1, len(boxes)):
            n2, c2, h2 = boxes[j]
            if n1.rsplit("_", 1)[0] == n2.rsplit("_", 1)[0] or \
                    n1.split("_")[0] == n2.split("_")[0]:
                continue
            if NONSOLID.search(n1) or NONSOLID.search(n2):
                continue
            if BURIEDISH.search(n1) or BURIEDISH.search(n2):
                continue
            if PLANTISH.search(n1) and PLANTISH.search(n2):
                continue
            if ROCKISH.search(n1) and ROCKISH.search(n2):
                continue
            # Vegetation rooted in / draped over rock and walls grows
            # THROUGH them by nature — any depth.
            if (PLANTISH.search(n1) or CROWNISH.search(n1)) and \
                    (WALLISH.search(n2) or ROCKISH.search(n2)):
                continue
            if (PLANTISH.search(n2) or CROWNISH.search(n2)) and \
                    (WALLISH.search(n1) or ROCKISH.search(n1)):
                continue
            # Containment: a small object whose center sits inside a
            # container-named object is contents, not clipping
            # (propane tanks in their cage, sixpacks in the fridge).
            contained = False
            for (na, ca, ha), (nb, cb, hb) in (((n1, c1, h1), (n2, c2, h2)),
                                               ((n2, c2, h2), (n1, c1, h1))):
                if CONTAINERISH.search(na) and all(
                        abs(cb[ax] - ca[ax]) < ha[ax] for ax in range(3)):
                    contained = True
                    break
            if contained:
                continue
            pen = []
            ok = True
            for ax in range(3):
                o = (h1[ax] + h2[ax]) - abs(c1[ax] - c2[ax])
                if o <= EPS:
                    ok = False
                    break
                pen.append(o)
            if not ok:
                continue
            depth = min(pen)
            # Report floor: contact artifacts (books against the case
            # back, a jacket draped on a bench, a phone seated on a
            # desk) all land under 4cm. Every confirmed-real clip so
            # far (gas station, faust, foxhole) was 0.05m+.
            if depth <= 0.04:
                continue
            if (WALLISH.search(n1) or WALLISH.search(n2)) and \
                    depth <= EMBED_MAX:
                continue
            if depth <= SEAT_MAX and pen.index(depth) == 2 and \
                    (SURFACEISH.search(n1) or SURFACEISH.search(n2)):
                continue
            if STRUCTISH.search(n1) and STRUCTISH.search(n2):
                continue
            if depth <= 0.40 and (
                    (STRUCTISH.search(n1) and ROOFISH.search(n2)) or
                    (STRUCTISH.search(n2) and ROOFISH.search(n1))):
                continue
            # A rope/wire/pole ENDPOINT buried a few cm in whatever
            # anchors it is a fastening, not a clip.
            if depth <= 0.12 and (STRUCTISH.search(n1) or STRUCTISH.search(n2)):
                continue
            # Porches, balconies, awnings TUCK INTO their building's
            # facade by construction.
            if depth <= 0.25 and (
                    re.search(r"porch|veranda|stoop|balcony|marquee", n1, re.I) or
                    re.search(r"porch|veranda|stoop|balcony|marquee", n2, re.I)):
                continue
            # A tree crown over a roofline is natural adjacency —
            # canopies hang over eaves everywhere trees stand near
            # buildings. Trunks and buttresses are NOT excused.
            if (CROWNISH.search(n1) and ROOFISH.search(n2)) or \
                    (CROWNISH.search(n2) and ROOFISH.search(n1)):
                continue
            # A crown is an amorphous leaf mass — 35cm of foliage
            # against any surface reads as touching, not clipping.
            # Deeper crown burial still reports.
            if depth <= 0.35 and (CROWNISH.search(n1) or CROWNISH.search(n2)):
                continue
            hits.append((depth, n1, n2, tuple(pen)))
    hits.sort(reverse=True)
    return hits


def main():
    args = sys.argv[1:]
    A.install_stubs()
    if "--all" in args:
        names = sorted(f[6:-3] for f in os.listdir(A.LOCALES)
                       if f.startswith("build_") and f.endswith(".py"))
    else:
        names = [a.replace("build_", "").replace(".py", "") for a in args]
    if not names:
        print(__doc__)
        return 1
    total = 0
    for name in names:
        path = os.path.join(A.LOCALES, "build_%s.py" % name)
        if not os.path.exists(path):
            print("%-32s NO BUILDER" % name)
            continue
        boxes, err = record_builder(path)
        if err and not boxes:
            print("%-32s ERR %s" % (name, err))
            continue
        if err:
            print("%-32s (partial: %s)" % (name, err))
        hits = overlaps(boxes)
        if hits:
            print("== %s · %d objects · %d clips" % (name, len(boxes), len(hits)))
            for depth, n1, n2, pen in hits[:20]:
                print("   CLIP %5.2fm  %-26s x %-26s" % (depth, n1, n2))
            if len(hits) > 20:
                print("   … %d more" % (len(hits) - 20))
            total += len(hits)
        elif "--all" not in args:
            print("%-32s clean (%d objects)" % (name, len(boxes)))
    print("\n%d clip(s) across %d builder(s)" % (total, len(names)))
    return 0


if __name__ == "__main__":
    sys.exit(main())
