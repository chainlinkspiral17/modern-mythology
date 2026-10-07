#!/usr/bin/env python3
"""walkway_audit.py — can a person walk between the store fixtures?
(2026-10-07, the user: "Looks like shelves blocking shelves and aisles
too cramped for pedestrians.")

The stocked stores were laid out by footprint arithmetic that never
asked about the space BETWEEN fixtures: the grocery had 0.50 m between
two gondolas and 0.15 m between an aisle and the checkout; the Kwik
Stop's endcaps stood 0.42 m off aisle 0's corners; the fueling
station's endcap was 0.23 m from its coolers. Every gate measured
clipping and support; none measured passage.

For each store locale, every FLOOR-STANDING fixture (gondolas, endcaps,
counters, coolers, displays) is reduced to its plan footprint — every
part that starts within 0.3 m of the floor and is at least 12 cm tall,
so a gondola's 0.70 m base counts and its spine alone does not — and
every pair closer than WALK_MIN that is not touching (an endcap fixed
to its aisle's end, a bank of coolers) is a CRAMPED lane.

    python3 godot/tools/audit/walkway_audit.py            # every store
    python3 godot/tools/audit/walkway_audit.py kwik_stop
"""
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import prop_overlap_audit as P  # noqa: E402

WALK_MIN = 0.90       # m · the narrowest lane a shopper passes another in
TOUCH = 0.05          # m · closer than this the two are ONE fixture (an endcap on its aisle's end)
STORES = ("kwik_stop", "centro_grocery_aisle", "nexcorp_fueling_station", "nexcorp_gas_go")
FIXTURE = re.compile(
    r"^(Aisle_Endcap_Water|Aisle_?\d*|EndCap_[^_]+|Produce|Card_Bale|Checkout|Counter|Register|Cooler_\d+|"
    r"Ice_Merchandiser|ATM|Coffee_Counter|CoffeeCounter|Coffee_Base|SodaPyr|BeerFridge|Slurpee|MagRack|"
    # islands (2026-10-07: the Kwik Stop's ice-cream chest stood 0.70 m in
    # front of the cooler doors and this list did not know its name)
    r"Novelty_Cooler|Freezer|Meat_Case|Deli_Case|Frozen_Bank|Pallet|Break_Bench|Break_Locker|Hot_Case|HotCase|"
    r"Impulse_Rack|Vape_Kiosk|Newspaper)(?=_|$)", re.I)
BANK = re.compile(r"^Cooler_\d+$", re.I)      # reach-in doors in a row along a wall are one bank
# pieces that are ONE assemblage though they do not touch
PAIRS = {frozenset(("Break_Bench", "Break_Locker")),     # the bench in front of its lockers
         frozenset(("Impulse_Rack", "Register"))}        # the rack on the register's face
# staged on purpose: the story puts it in the lane
DELIBERATE = {
    # "Diego parks the hand truck. He starts pulling cases of stewed tomatoes
    # off the pallet and onto the lower shelf" — 3 AM, the store closed
    ("centro_grocery_aisle", "Pallet"),
}


def footprints(boxes):
    fx = {}
    for n, c, h in boxes:
        m = FIXTURE.match(n)
        if not m or c[2] - h[2] > 0.30 or 2 * h[2] < 0.12:
            continue
        k = m.group(1)
        b = fx.setdefault(k, [1e9, 1e9, -1e9, -1e9])
        b[0] = min(b[0], c[0] - h[0]); b[1] = min(b[1], c[1] - h[1])
        b[2] = max(b[2], c[0] + h[0]); b[3] = max(b[3], c[1] + h[1])
    return fx


def audit(locale):
    P.record_builder(os.path.join(P.A.LOCALES, "build_%s.py" % locale))
    fx = footprints(P.A.BOXES)
    out = []
    ks = sorted(fx)
    for i, a in enumerate(ks):
        for b in ks[i + 1:]:
            if BANK.match(a) and BANK.match(b):
                continue
            if frozenset((a, b)) in PAIRS or (locale, a) in DELIBERATE or (locale, b) in DELIBERATE:
                continue
            A, B = fx[a], fx[b]
            gap = max(B[0] - A[2], A[0] - B[2], B[1] - A[3], A[1] - B[3])
            if TOUCH <= gap < WALK_MIN:
                out.append((gap, a, b))
    return out


def main():
    P.A.install_stubs()
    only = [a for a in sys.argv[1:] if not a.startswith("-")] or list(STORES)
    bad = 0
    for loc in only:
        for gap, a, b in audit(loc):
            print("CRAMPED  %-24s %.2f m between %s and %s" % (loc, gap, a, b))
            bad += 1
    print("walkway_audit · %d store(s) · %d cramped lane(s) (min %.2f m)" % (len(only), bad, WALK_MIN))
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
