#!/usr/bin/env python3
"""support_audit.py — everything stands on something (2026-09-22).

The user, looking at the Deck: "lots of objects floating in scenes
still, not tethered to walls or tables or floors." The furniture
gate's FLOAT rule only looked at prop-sized parts, let anything named
like a fixture off by name, and counted a part EMBEDDED in a larger
solid as held. This audit asks the plain question of every recorded
box: is it connected, through things it touches, to the floor, a
wall, or the ceiling?

  · two boxes TOUCH when their bounding boxes overlap or come within
    TOUCH metres on every axis (a leg on a slab, a cord to a wall, a
    shade round its bulb);
  · a component of touching boxes is GROUNDED when it contains a
    shell piece (floor · wall · ceiling · ground · road · slab) or a
    box whose underside is within TOUCH of z = 0;
  · every other component FLOATS. The report names the component by
    its lowest member and lists the rest.

Skipped: sky, far bands, mist, drones and anything the vantage audit
already treats as not-a-thing (VO.IGNORE), plus foliage lobes and
leaders (PASSABLE) — those hang in their crowns by design.

    python3 godot/tools/audit/support_audit.py [locale …]
    python3 godot/tools/audit/support_audit.py --all      # list members

Gate: zero-regression against HOLDOUT counts (see below).
"""
import glob
import json
import os
import re
import sys
from collections import defaultdict

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import prop_overlap_audit as P
import vantage_obstruction_audit as VO

ROOT = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
BUILDERS = P.A.LOCALES
TOUCH = 0.03
# foliage and vapour hang in their crowns by design — whole name PARTS,
# so "smoke" cannot eat the Smokers_Tin (the vantage audit's PASSABLE did)
FOLIAGE = re.compile(r"(^|_)(foliage|leaf|leaves|frond|lobe|salal|shrub|bush|hedge|needles|fern|grass|reed|vine|ivy|moss|drape|sheer|curtain|spray|stream|fog|haze|mist|steam|cloud|leader)(_|$)|_[CL][0-9]+(_|$)", re.I)
# a tree's crown hangs in its trunk by design; a candelabra's crown, a
# register's crown, crown moulding do not (2026-09-22: "crown" in FOLIAGE
# dropped the diner's candelabra ring, so its candles read as floating)
TREE_CROWN = re.compile(r"(tree|cedar|sitka|hemlock|grove|scrub|conifer|broadleaf|oak|pine|maple|birch|elm|willow|fir|spruce|palm|alder|cottonwood|poplar|aspen|cypress|juniper|shrub|bush|sapling|myrtle|magnolia|dogwood|sycamore|laurel|neardeep|deep|wild|yard|back)[a-z0-9_]*_(crown|canopy)", re.I)
# a door / window / gate / shutter LEAF is a slab, not foliage (2026-09-22:
# "leaf" dropped the centro cooler's door, so its handle floated)
DOOR_LEAF = re.compile(r"(door|window|gate|shutter|hatch|lid)_?leaf", re.I)
TERRAIN = {"graustark", "harmony_terrain", "small_wood_road", "riverfront", "louisiana_road", "new_auburn_road", "harmony_district"}
SHELL = re.compile(r"(^|_)(wall|floor|ceil|ground|road|slab|apron|sidewalk|curb|terrain|lawn|grass|deck|stair|step|porch|platform|roof|beam|joist|foundation|pier|spandrel|lintel|jamb|partition|hull|shell|facade|street|path|gravel|asphalt|track|rail_bed|island|dock|bridge)", re.I)
# (the vantage audit's IGNORE is not used here: its `plinth$` dropped the
# sundial's plinth and its `band` the cedar tower's floor bands, 2026-09-22)
# whole name PARTS only — "ridge" must not eat the Fridge (2026-09-22)
SKY = re.compile(r"(^|_)(sky|far|farband|horizon|mist|cloud|drone|skein|haze|fog|treeline|ridge|hill|glow|clearing|sundisc|moondisc|shimmer|mote|void|sea|swamp_floor|lake_water|valley_floor|template_land|template_sea|ribbon)(_|$)|^far[a-z]|(^|_)out_[a-z]+_(ground|street|facade|wall|sea|sky|roof|treeline|lawn|tower|freeway|brick|gallery)|garden_far", re.I)


def touching(a, b):
    (alo, ahi), (blo, bhi) = a, b
    for i in range(3):
        if blo[i] > ahi[i] + TOUCH or alo[i] > bhi[i] + TOUCH:
            return False
    return True


def audit(locale, boxes, show_all=False):
    keep = []
    for n, c, h in boxes:
        # shells stay whatever the vantage audit ignores (it drops floors
        # and ceilings as not-a-thing; here they are what things stand on)
        if not SHELL.search(n) and not DOOR_LEAF.search(n) and (FOLIAGE.search(n) or TREE_CROWN.search(n)):
            continue
        if SKY.search(n):
            continue
        keep.append((n, tuple(c[i] - h[i] for i in range(3)), tuple(c[i] + h[i] for i in range(3))))
    n = len(keep)
    parent = list(range(n))

    def find(i):
        while parent[i] != i:
            parent[i] = parent[parent[i]]
            i = parent[i]
        return i

    def union(i, j):
        ri, rj = find(i), find(j)
        if ri != rj:
            parent[ri] = rj

    # sweep on x to keep this near-linear for the big builders
    order = sorted(range(n), key=lambda i: keep[i][1][0])
    active = []
    for i in order:
        lo = keep[i][1]
        active = [j for j in active if keep[j][2][0] + TOUCH >= lo[0]]
        for j in active:
            if touching((keep[i][1], keep[i][2]), (keep[j][1], keep[j][2])):
                union(i, j)
        active.append(i)
    grounded = set()
    for i, (nm, lo, hi) in enumerate(keep):
        if SHELL.search(nm) or lo[2] <= TOUCH:
            grounded.add(find(i))
    comps = defaultdict(list)
    for i in range(n):
        r = find(i)
        if r not in grounded:
            comps[r].append(i)
    shells = [(keep[i][1], keep[i][2]) for i in range(n) if SHELL.search(keep[i][0])]
    floats = []
    for r, members in comps.items():
        members.sort(key=lambda i: keep[i][1][2])
        low = keep[members[0]]
        top = max(keep[i][2][2] for i in members)
        # the nearest shell piece to any member: the gap on the axis
        # that separates them (how far short the thing hangs or stands)
        gap = 9.9
        for i in members:
            lo, hi = keep[i][1], keep[i][2]
            for slo, shi in shells:
                g = max(max(slo[k] - hi[k], lo[k] - shi[k]) for k in range(3))
                if g < gap:
                    gap = g
        floats.append((low[0], low[1][2], top, gap, [keep[i][0] for i in members]))
    floats.sort(key=lambda f: f[0])
    return floats


BASELINE = os.path.join(HERE, "support_baseline.json")


def main():
    show_all = "--all" in sys.argv
    write_baseline = "--write-baseline" in sys.argv
    only = [a for a in sys.argv[1:] if not a.startswith("--")]
    P.A.install_stubs()
    total = 0
    per = {}
    base = {}
    if os.path.exists(BASELINE):
        base = json.load(open(BASELINE)).get("counts", {})
    for path in sorted(glob.glob(os.path.join(BUILDERS, "build_*.py"))):
        locale = os.path.basename(path)[6:-3]
        if only and locale not in only:
            continue
        if locale in TERRAIN:
            continue      # a heightfield floor the recorder cannot see: nothing here can be judged by boxes
        boxes = VO.boxes_for(locale)
        if not boxes:
            continue
        floats = audit(locale, boxes, show_all)
        per[locale] = len(floats)
        total += len(floats)
        if floats:
            print("== %s · %d floating component(s)" % (locale, len(floats)))
            for lowname, z, top, gap, members in floats:
                extra = "" if len(members) == 1 else "  +%d: %s" % (len(members) - 1, ", ".join(members[1:5]) + (" …" if len(members) > 5 else ""))
                print("   FLOAT  %-34s z %.2f..%.2f · nearest shell %.2f m%s" % (lowname, z, top, gap, extra))
    print("\nsupport_audit · %d locale(s) · %d floating component(s)" % (len(per), total))
    worst = sorted(per.items(), key=lambda kv: -kv[1])[:20]
    print("worst: " + ", ".join("%s %d" % kv for kv in worst if kv[1]))
    # zero-regression: no locale may float MORE than its baseline line
    regress = [(loc, n, base.get(loc, 0)) for loc, n in per.items() if n > base.get(loc, 0)]
    better = sum(max(base.get(loc, 0) - n, 0) for loc, n in per.items())
    for loc, n, b in regress:
        print("REGRESSION  %-28s %d floating (baseline %d)" % (loc, n, b))
    if better:
        print("%d fewer than the baseline · run with --write-baseline to lower the line" % better)
    if write_baseline and not only:
        doc = json.load(open(BASELINE)) if os.path.exists(BASELINE) else {}
        doc["counts"] = per
        json.dump(doc, open(BASELINE, "w"), indent=1, sort_keys=True)
        print("baseline written")
    return 1 if regress else 0


if __name__ == "__main__":
    sys.exit(main())
