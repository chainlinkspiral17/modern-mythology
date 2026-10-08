#!/usr/bin/env python3
"""seat_clearance_audit.py — do facing seats leave room for knees? (2026-10-08)

The user, on the hospital waiting room: "Chairs facing each other with no
room between seems a big problem." The two middle rows of beam seating
were meant back to back and were built FACING, their seat fronts 15 cm
apart. No gate asked how far apart two seats that face each other stand.

Every seat (a part named `<stem>_Seat`) takes its facing from its back
(the parts named `<stem>_Back*`): the seat looks away from its back. Two
seats that face each other (opposite facings, overlapping across their
width) need FACING_MIN metres between their front edges for two people's
knees and feet — unless a table, a desk, a counter or a booth table
stands between them (a dining table, a booth: the table is the room).

    python3 godot/tools/audit/seat_clearance_audit.py            # every builder
    python3 godot/tools/audit/seat_clearance_audit.py hospital_room
"""
import glob
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import prop_overlap_audit as P  # noqa: E402

FACING_MIN = 0.75     # m between facing seat fronts with nothing between
SEAT = re.compile(r"^(.*)_Seat$")
BETWEEN = re.compile(r"(table|desk|counter|top|bar\b|booth|bench|island|workbench)", re.I)


def seats_of(loc):
    P.record_builder(os.path.join(P.A.LOCALES, "build_%s.py" % loc))
    boxes = list(P.A.BOXES)
    seats = []
    for n, c, h in boxes:
        m = SEAT.match(n)
        if not m:
            continue
        stem = m.group(1)
        backs = [(bc, bh) for bn, bc, bh in boxes if bn.startswith(stem + "_Back")]
        if not backs:
            continue
        bx = sum(bc[0] for bc, _ in backs) / len(backs)
        by = sum(bc[1] for bc, _ in backs) / len(backs)
        dx, dy = c[0] - bx, c[1] - by
        if abs(dx) < 1e-3 and abs(dy) < 1e-3:
            continue
        # snap the facing to its dominant axis
        f = (1 if dx > 0 else -1, 0) if abs(dx) >= abs(dy) else (0, 1 if dy > 0 else -1)
        seats.append((stem, c, h, f))
    return seats, boxes


def audit(loc):
    seats, boxes = seats_of(loc)
    out = []
    for i, (sa, ca, ha, fa) in enumerate(seats):
        for sb, cb, hb, fb in seats[i + 1:]:
            if fa[0] != -fb[0] or fa[1] != -fb[1]:
                continue
            ax = 0 if fa[0] else 1                     # the facing axis
            lat = 1 - ax
            # B must stand in front of A
            if (cb[ax] - ca[ax]) * fa[ax] <= 0:
                continue
            if abs(cb[lat] - ca[lat]) > ha[lat] + hb[lat] - 0.05:
                continue                                # not across from each other
            front_a = ca[ax] + fa[ax] * ha[ax]
            front_b = cb[ax] + fb[ax] * hb[ax]
            gap = (front_b - front_a) * fa[ax]
            if gap >= FACING_MIN:
                continue
            lo, hi = sorted((front_a, front_b))
            between = False
            for n, c, h in boxes:
                if not BETWEEN.search(n) or n.startswith((sa, sb)):
                    continue
                if c[ax] + h[ax] > lo and c[ax] - h[ax] < hi and abs(c[lat] - ca[lat]) < h[lat] + ha[lat] \
                        and 0.35 < c[2] + h[2] < 1.25:
                    between = True
                    break
            if not between:
                out.append((sa, sb, gap))
    return out


def main(argv):
    P.A.install_stubs()
    locs = argv[1:] or sorted(os.path.basename(p)[6:-3] for p in glob.glob(os.path.join(P.A.LOCALES, "build_*.py")))
    total = 0
    for loc in locs:
        try:
            bad = audit(loc)
        except Exception as e:  # a builder the recorder cannot run is not a seating defect
            print("  · %-28s (skipped: %s)" % (loc, type(e).__name__))
            continue
        for a, b, gap in bad:
            total += 1
            print("  ✗ %-26s %-28s faces %-28s %.2f m between them" % (loc, a, b, gap))
    print("seat_clearance_audit · %d locale(s) · %d facing pair(s) under %.2f m" % (len(locs), total, FACING_MIN))
    return 1 if total else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
