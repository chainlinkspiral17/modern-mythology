#!/usr/bin/env python3
"""buried_flat_audit.py — a flat thing lying INSIDE what it lies on
(2026-11-15, pass 386).

Found re-seating the diner's napkin dispensers (pass 384): `TABLE_TOP_Z` is
the top's centre, so every saucer on every booth table lay wholly inside the
formica. Asked of every set: Dean's hundred and his note are 3 cm inside the
riverboat's dining table; the hospice's envelope is inside the dresser top;
Board Lords' phone, bread board and knife are inside the counter; the Kwik
Stop's pizza, the bungalow's living-room rug, eight car floor mats, wear
marks, paper stacks, a checkbook, a map. None of them can be seen from any
camera, and every gate passed them: a part inside a slab touches it (held),
and prop_overlap's `buried` asks only named wall dressing, strictly inside on
all six sides — a thing set on the slab's BOTTOM face, as these mostly are,
shares a face and is let off as "mounted".

Read only where the planes are exact: both the thing and its host are a
plain box or an upright cylinder (the recorder's TRUE_BOXES / Z_CYLS). The
host is a flat slab — a table top, a counter, a shelf, a floor. The thing is
at most 3 cm thick and lies within the host's height:

  INSIDE  its top is below the host's top: it is not drawn at all;
  FLUSH   its top is IN the host's top plane: both are drawn there (flicker).

    python3 godot/tools/audit/buried_flat_audit.py [locale …]
    python3 godot/tools/audit/buried_flat_audit.py --all            # list every one
    python3 godot/tools/audit/buried_flat_audit.py --write-baseline
Gate: zero-regression against buried_flat_baseline.json (lower only).
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

BASELINE = os.path.join(HERE, "buried_flat_baseline.json")
THIN = 0.03           # the thing: at most this thick
EPS = 0.0004
# hosts that are not a surface to lie on: see-through, soft, a volume
HOSTNOT = re.compile(r"glass|pane|window|water|liquid|mist|fog|haze|glow|light|beam|shaft|ray|sky|cloud|ceil|"
                     r"(^|_)wear_|stock|terrain|hill|ridge|berm|mound|foliage|crown|canopy|leaf|tree|bush|hedge|"
                     r"zone|volume|interior|opening|cavity|recess", re.I)
# things MADE to be below a surface: a sink's bowl, a drain, a well, a slot
RECESSED = re.compile(r"bowl|basin|drain|well\b|_well|slot|groove|channel|chan\b|recess|inset|inlay|"
                      r"opening|hole|pit\b|socket|grout|seam$|joint", re.I)


COVER = re.compile(r"(^|_)(mat|rug|carpet|runner|blanket|sheet|quilt|cloth|tarp|stair|step|tread|riser|"
                   r"platform|plinth|frame|fixture)(_|$)", re.I)
MARK = re.compile(r"scuff|stain|wear|mark|spill|seam|tile|plank|crack|patch|ring|star|dash|line|halo|shadow|tuft|button", re.I)


def hits_for(path):
    boxes, _err = P.record_builder(path)
    if not boxes or len(boxes) < 20:
        return []
    exact = P.A.TRUE_BOXES | P.A.Z_CYLS
    hosts = []
    for n, c, h in boxes:
        if n not in exact or HOSTNOT.search(n):
            continue
        w, d, t = 2 * h[0], 2 * h[1], 2 * h[2]
        if w < 0.25 or d < 0.25 or t < 0.015:
            continue
        if t <= 0.08 or (t <= 0.30 and w * d >= 1.5):
            hosts.append((n, c, h))
    out = []
    for n, c, h in boxes:
        if n not in exact or RECESSED.search(n):
            continue
        t = 2 * h[2]
        if t > THIN or t <= 0 or min(h[0], h[1]) < 0.01 or max(h[0], h[1]) > 2.5:
            continue
        top, bot, a = c[2] + h[2], c[2] - h[2], 4 * h[0] * h[1]
        for sn, sc, sh in hosts:
            if sn == n or 2 * sh[2] <= t:
                continue
            stop, sbot = sc[2] + sh[2], sc[2] - sh[2]
            if top > stop + EPS or bot < sbot - EPS:
                continue
            ox = min(c[0] + h[0], sc[0] + sh[0]) - max(c[0] - h[0], sc[0] - sh[0])
            oy = min(c[1] + h[1], sc[1] + sh[1]) - max(c[1] - h[1], sc[1] - sh[1])
            if ox <= 0 or oy <= 0 or ox * oy < 0.8 * a or 4 * sh[0] * sh[1] < 1.5 * a:
                continue
            if VT.never_together(n, sn):
                continue
            # a covering hides what is under it, as it should: a scuff on
            # the floor under the door mat, a stain under a rug
            if COVER.search(sn) and MARK.search(n):
                continue
            # a MARK on the plane its host stands on is UNDER the host, not
            # in a surface: a floor stain under the bed's platform, a coffee
            # ring under the console, a carpet star under the stair
            if MARK.search(n) and (bot - sbot < 0.012 or stop - top > 0.05):
                continue                # … or deep under a thick thing built over it
            out.append((n, sn, "FLUSH" if abs(top - stop) <= EPS else "INSIDE", stop - top))
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
        json.dump({"_doc": "buried_flat_audit.py: flat things lying inside (or flush with) the slab they lie on, per set; lower only",
                   "counts": dict(sorted(counts.items()))}, open(BASELINE, "w"), indent=1)
        print("baseline written: %d buried in %d set(s)" % (sum(counts.values()), len(counts)))
        return 0
    base = json.load(open(BASELINE)).get("counts", {}) if os.path.exists(BASELINE) else {}
    bad = 0
    for loc in sorted(listed):
        over = counts[loc] > base.get(loc, 0)
        bad += 1 if over else 0
        if show or over or only:
            for n, s, kind, depth in sorted(listed[loc]):
                print("%s %-24s %-6s %-36s in %-28s %4.1f mm under its top"
                      % ("BURIED" if over else "known ", loc, kind, n[:36], s[:28], depth * 1000))
    print("buried_flat_audit · %d set(s) read · %d flat thing(s) inside the slab they lie on, in %d set(s) · %d set(s) over baseline"
          % (len(paths) if not only else len(only), sum(counts.values()), len(counts), bad))
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
