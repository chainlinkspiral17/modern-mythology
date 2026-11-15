#!/usr/bin/env python3
"""overhang_audit.py — a thing resting on a surface, mostly off its edge
(2026-11-15, pass 384).

The user, reading a frame of booth six: "What's the thing sticking out from
the end of the table, hovering in the air?" The napkin dispenser. Its group
was laid out for a long table and the booth tables are 0.70 m square: 11 of
its 16 cm stood past the aisle edge on all six booths. support_audit passed
it — it TOUCHES the table, so it is "held" — and prop_overlap had nothing to
say: it clips nothing. What no gate asked: is the thing ON what it rests on?

A small box RESTS on a surface when its underside is within REST of the
surface's top and their footprints overlap; the surface is something clearly
bigger than it (a table top, a counter, a shelf, a deck). It OVERHANGS when
its centre lies past the surface's edge — more than half of it is in the air
— and nothing else it rests on is under its centre.

    python3 godot/tools/audit/overhang_audit.py [locale …]
    python3 godot/tools/audit/overhang_audit.py --all     # every hit, listed
Gate: zero-regression against overhang_baseline.json (lower only).
"""
import glob
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import prop_overlap_audit as P
import vantage_obstruction_audit as VO
try:
    import view_tags as VT
except Exception:                       # pragma: no cover
    VT = None

BASELINE = os.path.join(HERE, "overhang_baseline.json")
REST = 0.025          # underside within 2.5 cm of the surface's top
SMALL = 0.80          # the thing: no side longer than this …
TALL = 0.80           # … and no taller
PAST = 0.012          # centre this far past the edge, at least
BIGGER = 2.0          # the surface's top is at least this many times its footprint
MIN_SIDE = 0.30       # … and at least this long both ways
# not things that rest: vapour, foliage, light, cords and anything hung
SKIP = re.compile(r"(mist|fog|haze|smoke|steam|glow|beam|ray|light_?cone|shadow|puddle|stain|spill|"
                  r"cord|cable|wire|rope|chain|string|strap|hose|pipe|"
                  r"leaf|leaves|frond|fern|vine|ivy|moss|grass|branch|crown|foliage|"
                  r"curtain|drape|cloth|towel|blanket|quilt|sheet|runner|rug|mat\b|"
                  r"sign|banner|flag|awning|canopy|eave|roof|gutter|trim|mould|crown|lip|edge|rim|"
                  r"nosing|overhang|apron|skirt|band|bullnose|"
                  r"arm|leg|foot|feet|head|hand|torso|body|hair|tail|wing|beak)", re.I)


# A PART of a made thing is held by the thing, not by resting: a seat's back
# on its base, a chest's lid, a copier's sorter bin, a ladder's bracket over
# the case it leans on, one book on the next in a stocked row. Judged by the
# name's last word (numbers and signs aside).
PART = re.compile(r"^(back|lid|flap|door|bracket|frame|tank|bin|top|slab|seam|tube|head|face|cushion|cush|pan|"
                  r"panel|shelf|drawer|rail|bar|post|end|pewend|wheel|stock|slumped|seatback|juryseatback|"
                  r"thigh|shin|knee|lap|hinge|handle|knob|base|plinth|cap|cover|housing|body|counterslab)$", re.I)
# A surface that is a covering, not a support: what lies on a rug lies on the
# floor, what lies on a blanket lies on the bed under it.
COVERING = re.compile(r"(rug|carpet|mat$|strip|plaza|curb|reach|blanket|sheet|quilt|duvet|cloth|runner|"
                      r"cushion|pillow|seam)", re.I)


def _last_word(name):
    # numbers, signs and a bare side letter (Thigh_R, Rail_N) are not the word
    words = [w for w in re.split(r"[_\s]+", name.split("__")[0])
             if w and not re.fullmatch(r"[-+]?\d+(\.\d+)?|[LRNSEW]", w)]
    return words[-1] if words else ""


def hits_for(locale):
    boxes = [b for b in VO.boxes_for(locale) if not VO.IGNORE.search(b[0])]
    if len(boxes) < 20:
        return []
    tops = []           # candidate surfaces: (name, x0, x1, y0, y1, top, area)
    for n, c, h in boxes:
        w, d = 2 * h[0], 2 * h[1]
        if w >= MIN_SIDE and d >= MIN_SIDE:
            tops.append((n, c[0] - h[0], c[0] + h[0], c[1] - h[1], c[1] + h[1], c[2] + h[2], w * d))
    out = []
    for n, c, h in boxes:
        w, d, t = 2 * h[0], 2 * h[1], 2 * h[2]
        if max(w, d) > SMALL or t > TALL or min(w, d) < 0.02 or t < 0.01:
            continue
        if SKIP.search(n) or PART.match(_last_word(n)):
            continue
        bot = c[2] - h[2]
        if bot < 0.05:
            continue                    # on the ground: nothing to fall off
        x0, x1, y0, y1 = c[0] - h[0], c[0] + h[0], c[1] - h[1], c[1] + h[1]
        rest = []
        for s in tops:
            if s[0] == n or abs(bot - s[5]) > REST:
                continue
            if s[6] < BIGGER * w * d or COVERING.search(s[0]):
                continue
            ox = min(x1, s[2]) - max(x0, s[1])
            oy = min(y1, s[4]) - max(y0, s[3])
            if ox <= 0 or oy <= 0 or ox * oy < 0.02 * w * d:
                continue                # footprints do not overlap (a shared edge is not resting)
            if VT is not None:
                try:
                    if VT.never_together(n, s[0]):
                        continue
                except Exception:
                    pass
            rest.append(s)
        if not rest:
            continue
        under = [s for s in rest if s[1] - PAST <= c[0] <= s[2] + PAST and s[3] - PAST <= c[1] <= s[4] + PAST]
        if under:
            continue
        s = max(rest, key=lambda s: (min(x1, s[2]) - max(x0, s[1])) * (min(y1, s[4]) - max(y0, s[3])))
        on = max(0.0, min(x1, s[2]) - max(x0, s[1])) * max(0.0, min(y1, s[4]) - max(y0, s[3]))
        out.append((n, s[0], 1.0 - on / (w * d)))
    return out


def main():
    args = sys.argv[1:]
    show = "--all" in args
    only = [a for a in args if not a.startswith("-")]
    locales = sorted(os.path.basename(p)[6:-3] for p in glob.glob(os.path.join(P.A.LOCALES, "build_*.py")))
    counts, listed = {}, {}
    for loc in locales:
        if only and loc not in only:
            continue
        try:
            hs = hits_for(loc)
        except Exception as e:          # a builder the recorder cannot run
            print("partial: %s (%s)" % (loc, e))
            continue
        if hs:
            counts[loc] = len(hs)
            listed[loc] = hs
    if "--write-baseline" in args:
        json.dump({"_doc": "overhang_audit.py: things resting mostly off their surface, per set; lower only",
                   "counts": dict(sorted(counts.items()))}, open(BASELINE, "w"), indent=1)
        print("baseline written: %d overhang(s) in %d set(s)" % (sum(counts.values()), len(counts)))
        return 0
    base = json.load(open(BASELINE)).get("counts", {}) if os.path.exists(BASELINE) else {}
    bad = 0
    for loc in sorted(listed):
        over = counts[loc] > base.get(loc, 0)
        if over:
            bad += 1
        if show or over or only:
            for n, s, frac in sorted(listed[loc], key=lambda r: -r[2]):
                print("%s %-26s %-34s %3.0f%% off  %s" % ("OVERHANG" if over else "known   ", loc, n, frac * 100, s))
    print("overhang_audit · %d set(s) read · %d thing(s) resting mostly off their surface in %d set(s) · %d set(s) over baseline"
          % (len(locales) if not only else len(only), sum(counts.values()), len(counts), bad))
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
