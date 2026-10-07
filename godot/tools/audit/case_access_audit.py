#!/usr/bin/env python3
"""case_access_audit.py — can the glass case be OPENED? (2026-10-07)

The user, after the walkway pass: "No they don't — the glass case can't
be opened by the island obstructing it." walkway_audit measured the
gaps BETWEEN fixtures; a reach-in cooler, a freezer, a display case
also needs the floor IN FRONT of its doors: the door's swing and the
person standing in it. No gate asked.

Every glass-front case (coolers, freezers, beer fridges, display and
merchandiser cases — by name) gets an ACCESS ZONE: ACCESS m deep in
front of its door face, across its width. The door face is the side
away from the nearest wall (a case stands with its back to a wall).
Any floor-standing part of another fixture inside that zone is a
BLOCKED case.

    python3 godot/tools/audit/case_access_audit.py            # the stores
    python3 godot/tools/audit/case_access_audit.py kwik_stop
"""
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import prop_overlap_audit as P  # noqa: E402

ACCESS = 0.90       # m · a reach-in door swings ~0.6 m; you stand in it
STORES = ("kwik_stop", "centro_grocery_aisle", "nexcorp_fueling_station", "nexcorp_gas_go")
# the case's own parts are grouped under the stem before these words
CASE = re.compile(r"^((?:Cooler|Frozen|Freezer|BeerFridge|Beer_Fridge|Pizza_Case|Donut_Case|Ice_Merchandiser|Vape_Kiosk|Deli_Case|Bakery_Case)"
                  r"[A-Za-z]*(?:_\d+)?)", re.I)
WALL = re.compile(r"(^|_)(wall|partition|pier|spandrel|lintel)(_|$)", re.I)
# props that stand in a case's doors ON PURPOSE (the story stages them)
DELIBERATE = {
    # "the propped cooler door + milk crate" — the sticking lock since July
    ("centro_grocery_aisle", "Milk_Crate_Prop"),
}
SKIP = re.compile(r"(floor|ground|rug|mat\b|mat_|runner|stain|wear|scuff|decal|grout|tile|threshold|slab|lot_|stripe|ceil)", re.I)


def boxes_of(loc):
    P.record_builder(os.path.join(P.A.LOCALES, "build_%s.py" % loc))
    return list(P.A.BOXES)


def union(parts):
    return [min(c[0] - h[0] for _, c, h in parts), min(c[1] - h[1] for _, c, h in parts),
            max(c[0] + h[0] for _, c, h in parts), max(c[1] + h[1] for _, c, h in parts)]


def audit(loc):
    boxes = boxes_of(loc)
    cases = {}
    for n, c, h in boxes:
        m = CASE.match(n)
        if m and c[2] - h[2] < 0.35:
            cases.setdefault(m.group(1), []).append((n, c, h))
    walls = [(n, c, h) for n, c, h in boxes if WALL.search(n) and 2 * h[2] > 1.5]
    out = []
    for stem, parts in cases.items():
        x0, y0, x1, y1 = union(parts)
        if x1 - x0 < 0.25 and y1 - y0 < 0.25:
            continue
        # the side nearest a wall is the back
        best = None
        for side, coord in (("-X", x0), ("+X", x1), ("-Y", y0), ("+Y", y1)):
            for n, c, h in walls:
                if side[1] == "X":
                    if not (c[1] - h[1] < y1 and c[1] + h[1] > y0):
                        continue
                    d = abs((c[0] + h[0] if side == "-X" else c[0] - h[0]) - coord)
                else:
                    if not (c[0] - h[0] < x1 and c[0] + h[0] > x0):
                        continue
                    d = abs((c[1] + h[1] if side == "-Y" else c[1] - h[1]) - coord)
                if best is None or d < best[0]:
                    best = (d, side)
        if best is None or best[0] > 0.6:
            continue                       # free-standing: no single door face to judge
        back = best[1]
        if back == "-X":
            zone = (x1, y0, x1 + ACCESS, y1)
        elif back == "+X":
            zone = (x0 - ACCESS, y0, x0, y1)
        elif back == "-Y":
            zone = (x0, y1, x1, y1 + ACCESS)
        else:
            zone = (x0, y0 - ACCESS, x1, y0)
        hit = None
        for n, c, h in boxes:
            if n.startswith(stem) or WALL.search(n) or SKIP.search(n) or CASE.match(n) or (loc, n) in DELIBERATE:
                continue
            if c[2] - h[2] > 0.30 or 2 * h[2] < 0.25:
                continue
            ox = min(zone[2], c[0] + h[0]) - max(zone[0], c[0] - h[0])
            oy = min(zone[3], c[1] + h[1]) - max(zone[1], c[1] - h[1])
            if ox > 0.02 and oy > 0.02 and (hit is None or ox * oy > hit[1]):
                hit = (n, ox * oy)
        if hit:
            out.append((stem, back, hit[0]))
    return out


def main():
    P.A.install_stubs()
    only = [a for a in sys.argv[1:] if not a.startswith("-")] or list(STORES)
    bad = 0
    for loc in only:
        for stem, back, who in audit(loc):
            print("BLOCKED  %-24s %-22s (back %s) — %s stands in front of its doors" % (loc, stem, back, who))
            bad += 1
    print("case_access_audit · %d locale(s) · %d blocked case(s) (%.2f m in front)" % (len(only), bad, ACCESS))
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
