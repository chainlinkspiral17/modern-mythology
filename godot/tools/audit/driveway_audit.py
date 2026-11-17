#!/usr/bin/env python3
"""driveway_audit.py — driveways that meet their street (pass 421).

The user (2026-11-16): "Curbs and driveways look broken or incomplete."
What the sets had, and what this gate finds in the recorded boxes of every
builder that lays a driveway:

  SUNK      a driveway lower than a walk it overlaps by more than 15 mm —
            it vanishes under the walk (Meadowlark's eight sat 40 mm under
            theirs, starting inside the walk)
  ACROSS    a curb standing more than 20 mm over a driveway's own footprint
  BLOCKED   a curb standing more than 30 mm across the line a driveway
            runs on, within 2.5 m past either end, over most of its width:
            no curb cut, so no car gets in (the drive stopped at the walk
            and the curb ran on across its mouth)

A curb cut built with _props.streets (make_street_edge / make_cut_curb) or
make_view(drives=…) drops the curb to a lip 2 cm over the street, which
none of these flag.

Findings judged acceptable are listed in JUDGED with the reason; anything
else fails. Uses vantage_obstruction_audit's box cache (keyed by the
builder and every shared module), so an unchanged set costs nothing.

    python3 godot/tools/audit/driveway_audit.py [locale ...]
"""
import glob
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import vantage_obstruction_audit as V  # noqa: E402

LOC = os.path.normpath(os.path.join(HERE, "..", "blender", "locales"))
DRIVE = re.compile(r"driveway|(^|_)drive([NSEW]_|_|[NSEW]$|$)|apron", re.I)
DECAL = re.compile(r"wear|stain|crack|seam|oil|car\b|_car_|vehicle|line|puddle|paint|mark|shadow|leaf|leaves|chalk|sheen|grass|lawn|turf", re.I)
WALK = re.compile(r"sidewalk|(^|_)walk(_|$)", re.I)
CURB = re.compile(r"curb", re.I)
CURBSTOP = re.compile(r"curbstop|wheel_?stop|parking_?block", re.I)

# "locale:drive" -> why it stands
_FRONTAGE = ("the frontage aprons: the flat frontage walk crosses each drive 2 cm "
             "proud (a walk across a drive, not a drive sunk under one), and the raised "
             "D'Ambrosio walk ramps down either side of both lot cuts by design "
             "(CurbRamp_*); no used view looks at the frontage road (riverfront_exterior "
             "faces the boat, riverfront_park the park). Draft N+1: the lot's own curbs "
             "(Curb_N / Curb_S) where the two lot aprons enter it")
JUDGED = {"%s:%s" % (loc, d): _FRONTAGE
          for loc in ("riverfront", "graustark")
          for d in ("Drive_Lot_apron_-16", "Drive_Lot_apron_16", "Drive_Gas_apron", "Drive_Mall_apron")}
# whole sets judged, with the reason (a set's every finding)
JUDGED_SETS = {}


def _ov(a0, a1, b0, b1):
    return min(a1, b1) - max(a0, b0)


def findings_for(locale, boxes, imprecise=frozenset()):
    """imprecise: parts whose box is not their shape (vantage_obstruction_
    audit.imprecise_for: a curve, a diagonal strip, a ribbon on sloped
    ground). A pair with one of them is not judged by box."""
    drives = [b for b in boxes if DRIVE.search(b[0]) and not DECAL.search(b[0])]
    walks = [b for b in boxes if WALK.search(b[0]) and not DECAL.search(b[0])]
    curbs = [b for b in boxes if CURB.search(b[0]) and not CURBSTOP.search(b[0]) and not DECAL.search(b[0])]
    out = []
    for n, c, h in drives:
        if h[0] < 0.6 or h[1] < 0.6 or h[2] > 0.15:   # not a drive: a strip, a sign, a screen, a part
            continue
        top = c[2] + h[2]
        probs = []
        loose = n in imprecise
        for wn, wc, wh in walks:
            if loose or wn in imprecise:
                continue
            ox = _ov(c[0] - h[0], c[0] + h[0], wc[0] - wh[0], wc[0] + wh[0])
            oy = _ov(c[1] - h[1], c[1] + h[1], wc[1] - wh[1], wc[1] + wh[1])
            if ox > 0.05 and oy > 0.05 and abs(wc[2] - c[2]) < 0.5:
                wt = wc[2] + wh[2]
                if wt - top > 0.015:
                    probs.append("SUNK %.0f mm under %s" % ((wt - top) * 1000, wn))
        # a curb cut already serves this drive when a curb piece no more
        # than 30 mm over it runs at least 2.4 m (a car's width) across its
        # footprint or its mouth: the rest of that curb may stand (an apron
        # that runs on past its curb, the roadside chapel's)
        near = []
        for cn, cc, ch in curbs:
            if abs(cc[2] - c[2]) > 0.6:
                continue
            ox = _ov(c[0] - h[0] - 2.5, c[0] + h[0] + 2.5, cc[0] - ch[0], cc[0] + ch[0])
            oy = _ov(c[1] - h[1] - 2.5, c[1] + h[1] + 2.5, cc[1] - ch[1], cc[1] + ch[1])
            if ox > 0.0 and oy > 0.0:
                near.append((cn, cc, ch))
        served = any((cc[2] + ch[2]) - top <= 0.03 and 2.0 * max(ch[0], ch[1]) >= 2.4 for cn, cc, ch in near)
        for cn, cc, ch in ([] if served or loose else near):
            if cn in imprecise:
                continue
            ct = cc[2] + ch[2]
            ox = _ov(c[0] - h[0], c[0] + h[0], cc[0] - ch[0], cc[0] + ch[0])
            oy = _ov(c[1] - h[1], c[1] + h[1], cc[1] - ch[1], cc[1] + ch[1])
            if ox > 0.05 and oy > 0.05 and max(ox, oy) > 0.5 and ct - top > 0.02:
                probs.append("ACROSS: %s stands %.0f mm over it" % (cn, (ct - top) * 1000))
                continue
            # BLOCKED: past either end of the drive's long axis
            ax = 0 if h[0] >= h[1] else 1
            cr = 1 - ax
            for sgn in (-1, 1):
                e0 = c[ax] + sgn * h[ax]
                e1 = e0 + sgn * 2.5
                lo, hi = min(e0, e1), max(e0, e1)
                along = _ov(lo, hi, cc[ax] - ch[ax], cc[ax] + ch[ax])
                across = _ov(c[cr] - h[cr], c[cr] + h[cr], cc[cr] - ch[cr], cc[cr] + ch[cr])
                if along > 0.0 and across > 1.2 * h[cr] and ct - top > 0.03:
                    probs.append("BLOCKED: %s stands %.0f mm across its mouth" % (cn, (ct - top) * 1000))
                    break
        if probs:
            out.append((n, probs))
    return out


LOT = re.compile(r"(^|_)lot(_|$)|parking|forecourt", re.I)
ROAD = re.compile(r"road|street|asphalt|highway|avenue|(^|_)lane(_|$)", re.I)
NOT_ROAD = re.compile(r"lot|parking|forecourt|dash|line|stripe|center|centre|crack|patch|seam|mark|puddle|shoulder|median|island", re.I)
# "locale:lot" -> why a lot with no way in from its road stands
JUDGED_LOTS = {}
for _lot in ("Lot_NW_KwikStop", "Lot_NE_GasGo", "Lot_SW_Cosmic", "Lot_SE_Damb"):
    JUDGED_LOTS["harmony_commercial:" + _lot] = (
        "no used view (the set has no preset a chapter plays); draft N+1: "
        "cut the four lots' entrances when the set is next built")


def sealed_lots(boxes, imprecise=frozenset()):
    """SEALED: a parking lot that touches a road (within 6 m) only through
    curb or raised walk — no stretch of 3 m where the barrier is down —
    and has no open frontage to any road. (Gas & Go and the Kwik Stop
    across Gallatin, pass 421: both lots were walled off from the road.)"""
    flat = [(n, c, h) for n, c, h in boxes if h[2] <= 0.08 and n not in imprecise]
    lots = [b for b in flat if LOT.search(b[0]) and not DECAL.search(b[0]) and b[2][0] * b[2][1] * 4.0 >= 40.0]
    roads = [b for b in flat if ROAD.search(b[0]) and not NOT_ROAD.search(b[0]) and max(b[2][0], b[2][1]) >= 7.5]
    # a curb cut's own flares (CurbRamp_*) slope down into it: not a barrier
    bars = [b for b in boxes if (CURB.search(b[0]) or WALK.search(b[0])) and not DECAL.search(b[0])
            and not re.search(r"ramp", b[0], re.I) and b[0] not in imprecise]
    out = []
    for ln, lc, lh in lots:
        ltop = lc[2] + lh[2]
        touching, open_any = 0, False
        for rn, rc, rh in roads:
            if abs(rc[2] - lc[2]) > 0.5:
                continue
            for ax in (0, 1):
                cr = 1 - ax
                # separation along ax: the lot's near edge to the road's near edge
                if lc[ax] + lh[ax] <= rc[ax] - rh[ax] + 0.01:
                    e0, e1 = lc[ax] + lh[ax], rc[ax] - rh[ax]
                elif rc[ax] + rh[ax] <= lc[ax] - lh[ax] + 0.01:
                    e0, e1 = rc[ax] + rh[ax], lc[ax] - lh[ax]
                else:
                    continue
                if e1 - e0 > 6.0:
                    continue
                f0 = max(lc[cr] - lh[cr], rc[cr] - rh[cr])
                f1 = min(lc[cr] + lh[cr], rc[cr] + rh[cr])
                if f1 - f0 < 3.0:
                    continue
                touching += 1
                rtop = rc[2] + rh[2]
                cover = []
                for bn, bc, bh in bars:
                    if bc[2] + bh[2] < max(ltop, rtop) + 0.05:
                        continue
                    if bc[ax] + bh[ax] < e0 - 0.3 or bc[ax] - bh[ax] > e1 + 0.3:
                        continue
                    a, b = max(f0, bc[cr] - bh[cr]), min(f1, bc[cr] + bh[cr])
                    if b > a:
                        cover.append((a, b))
                cover.sort()
                cur, widest = f0, 0.0
                for a, b in cover:
                    widest = max(widest, a - cur)
                    cur = max(cur, b)
                widest = max(widest, f1 - cur)
                if widest >= 3.0:
                    open_any = True
        if touching and not open_any:
            out.append(ln)
    return out


def main():
    want = [a for a in sys.argv[1:] if not a.startswith("-")]
    paths = sorted(glob.glob(os.path.join(LOC, "build_*.py")))
    bad = judged = sets = 0
    for path in paths:
        loc = os.path.basename(path)[6:-3]
        if want and loc not in want:
            continue
        src = open(path, encoding="utf-8", errors="replace").read()
        # (a window view's street, make_view, lays drives of its own)
        if not re.search(r"(?i)drive|apron|(^|_)lot(_|\b)|parking|forecourt|make_view\(", src):
            continue
        boxes = V.boxes_for(loc) or []
        loose = V.imprecise_for(loc)
        sets += 1
        for ln in sealed_lots(boxes, loose):
            key = "%s:%s" % (loc, ln)
            if key in JUDGED_LOTS or loc in JUDGED_SETS:
                judged += 1
                continue
            bad += 1
            print("  %-26s %-36s SEALED: no way in from its road (curb or raised walk the whole frontage)" % (loc, ln[:36]))
        for n, probs in findings_for(loc, boxes, loose):
            key = "%s:%s" % (loc, n)
            if key in JUDGED or loc in JUDGED_SETS:
                judged += 1
                continue
            bad += 1
            print("  %-26s %-36s %s" % (loc, n[:36], "; ".join(probs)[:160]))
    print("driveway_audit: %d set(s) with driveways · %d finding(s) · %d judged" % (sets, bad, judged))
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
