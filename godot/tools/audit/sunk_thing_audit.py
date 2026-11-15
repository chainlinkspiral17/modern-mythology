#!/usr/bin/env python3
"""sunk_thing_audit.py — a thing standing partly INSIDE the furniture it
stands on (2026-11-15, pass 388).

buried_flat_audit (pass 386) asks after FLAT things — a sheet, a coaster, a
mat — lying inside the slab they were set on. Its own NEXT note: a thick
thing sunk into a slab is not flat and is not asked. Pass 388 found one in
a frame: the Kwik Stop's hot case stood with its floor at 1.00, seven
centimetres inside the 1.07 counter top (centred at 1.30 when the top had
moved), and the phone "beside the register" lay through its side wall; the
pizza warmer beside it was sunk eight. Nothing failed: the case touches the
counter (held), and a case 0.6 m tall standing 7 cm into a 6 cm top is not
a clip prop_overlap reads (it asks named dressing, strictly inside).

Read only where the planes are exact: both the thing and its host are a
plain box or an upright cylinder (the recorder's TRUE_BOXES / Z_CYLS). The
host is a FURNITURE SURFACE — a top, counter, desk, table, bench, shelf —
raised off the floor (its top at 0.30 m or more) and a slab (at most 10 cm
thick). The thing is a loose object on it: thicker than 3 cm (thinner is
buried_flat's), at most 0.8 m tall, not built into it (legs, posts, panels,
rails, clamps, a lip). It is SUNK when its underside is more than 1.5 cm
below the host's top and still within the host's height, and its top is
above the host's top:

    python3 godot/tools/audit/sunk_thing_audit.py [locale …]
    python3 godot/tools/audit/sunk_thing_audit.py --all            # list every one
    python3 godot/tools/audit/sunk_thing_audit.py --write-baseline
Gate: zero-regression against sunk_thing_baseline.json (lower only).
"""
import glob
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import prop_overlap_audit as P
import view_tags as VT
import buried_flat_audit as B

BASELINE = os.path.join(HERE, "sunk_thing_baseline.json")
SINK = 0.015            # deeper than this below the host's top is sunk
EPS = 0.0004
SURF = re.compile(r"top|counter|desk|table|bench|shelf|sideboard|dresser|nightstand|cabinet|bar\b|_bar|stand|"
                  r"tray|ledge|sill|mantel|island|vanity|credenza|console|cart", re.I)
# a seat, a rim, a rack, a basket, a stage, a floor: not a surface things are set on
NOTSURF = re.compile(r"stool|seat|cushion|base\b|_base|lip\b|rim|rack|basket|wringer|trim|floor|slab|deck|porch|"
                     r"patio|lot\b|stage|roof|ground|step|stair|tread|riser", re.I)
# the furniture's own members, and things MADE to sit into a surface
BUILT = re.compile(r"leg|post|pedestal|column|rod|wall|mullion|pier|spandrel|back\b|_back|support|bracket|brace|"
                   r"strut|frame|panel|apron|skirt|kick|plinth|footing|stile|rail|clamp|hinge|bolt|screw|mount|"
                   r"stem|spine|lip\b|_lip|sink|hob\b|_hob|cooktop|drop_?in|undermount", re.I)


def hits_for(path):
    boxes, _err = P.record_builder(path)
    if not boxes or len(boxes) < 20:
        return []
    exact = P.A.TRUE_BOXES | P.A.Z_CYLS
    hosts = []
    for n, c, h in boxes:
        if n not in exact or B.HOSTNOT.search(n) or not SURF.search(n) or NOTSURF.search(n):
            continue
        w, d, t = 2 * h[0], 2 * h[1], 2 * h[2]
        if w < 0.25 or d < 0.25 or t < 0.015 or t > 0.10 or c[2] + h[2] < 0.30:
            continue
        hosts.append((n, c, h))
    out = []
    for n, c, h in boxes:
        if n not in exact or B.RECESSED.search(n) or BUILT.search(n):
            continue
        t = 2 * h[2]
        if t <= 0.03 or t > 0.8 or min(h[0], h[1]) < 0.01:
            continue
        top, bot, a = c[2] + h[2], c[2] - h[2], 4 * h[0] * h[1]
        for sn, sc, sh in hosts:
            if sn == n:
                continue
            stop, sbot = sc[2] + sh[2], sc[2] - sh[2]
            if not (sbot - EPS < bot < stop - SINK) or top < stop + 0.01:
                continue
            ox = min(c[0] + h[0], sc[0] + sh[0]) - max(c[0] - h[0], sc[0] - sh[0])
            oy = min(c[1] + h[1], sc[1] + sh[1]) - max(c[1] - h[1], sc[1] - sh[1])
            if ox <= 0 or oy <= 0 or ox * oy < 0.6 * a or 4 * sh[0] * sh[1] < 1.5 * a:
                continue
            if VT.never_together(n, sn):
                continue
            out.append((n, sn, stop - bot, t))
            break
    return out


def main():
    args = sys.argv[1:]
    show = "--all" in args
    only = [a for a in args if not a.startswith("-")]
    if not getattr(P.A, "STUBS_ON", False):
        P.A.install_stubs()
    counts, listed = {}, {}
    paths = sorted(glob.glob(os.path.join(P.A.LOCALES, "build_*.py")))
    for path in paths:
        loc = os.path.basename(path)[6:-3]
        if only and loc not in only:
            continue
        hs = hits_for(path)
        if hs:
            counts[loc] = len(hs)
            listed[loc] = hs
    if "--write-baseline" in args:
        json.dump({"_doc": "sunk_thing_audit.py: loose things standing partly inside the furniture top they stand on, per set; lower only",
                   "counts": dict(sorted(counts.items()))}, open(BASELINE, "w"), indent=1)
        print("baseline written: %d sunk in %d set(s)" % (sum(counts.values()), len(counts)))
        return 0
    base = json.load(open(BASELINE)).get("counts", {}) if os.path.exists(BASELINE) else {}
    bad = 0
    for loc in sorted(listed):
        over = counts[loc] > base.get(loc, 0)
        bad += 1 if over else 0
        if show or over or only:
            for n, s, depth, t in sorted(listed[loc]):
                print("%s %-24s %-36s in %-28s %3.0f mm deep (%3.0f mm tall)"
                      % ("SUNK  " if over else "known ", loc, n[:36], s[:28], depth * 1000, t * 1000))
    print("sunk_thing_audit · %d set(s) read · %d thing(s) standing inside the top they stand on, in %d set(s) · %d set(s) over baseline"
          % (len(paths) if not only else len(only), sum(counts.values()), len(counts), bad))
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
