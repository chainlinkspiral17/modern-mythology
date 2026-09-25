#!/usr/bin/env python3
"""placement_audit — is the furniture ARRANGED, or dropped? (2026-09-25)

The user on the 09-25 sheet: "a lot of objects just hanging out in the
middle of rooms, not arranged properly, up against walls or on top
surfaces. New door-like polygons in the middle of rooms." Three
classes, per interior builder (a floor + a ceiling over it):

  OFF_WALL   a WALL-CLASS piece (dresser · wardrobe · bookcase · shelf
             unit · cabinet · locker · fridge · desk · sideboard ·
             hutch · crate · hamper · amp · radiator) whose back is
             more than 0.12 m from every wall or partition and that
             touches no other wall-class piece — it stands in the room.
  FREE_SLAB  a tall thin box (≥ 1.7 m, ≤ 0.25 m thick) that is not a
             door, window, glass, poster, mirror, curtain or screen,
             and whose two lateral ends both stop short of a wall by
             more than 0.10 m — a partition that reaches nothing, a
             door-shaped polygon standing in the room.
  TIGHT      a wall-class piece and a bed on the SAME wall with less
             than 0.45 m between them — no way to make the bed or open
             the drawers.

    python3 godot/tools/audit/placement_audit.py            # all
    python3 godot/tools/audit/placement_audit.py <locale>…  # some
Report only; the counts ride into the roadmap. Exit 0.
"""
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import prop_overlap_audit as P

LOCALES = os.path.normpath(os.path.join(HERE, "..", "blender", "locales"))
WALL = re.compile(r"wall|partition|(^|_)part(_|$)|wallseg|closet_[nsew](_|$)|_back$|backdrop|facade|siding|shell|hull", re.I)
WALL_CLASS = re.compile(r"dresser|wardrobe|armoire|bookcase|bookshelf|shelf_body|shelves|shelf_unit|cabinet_body|cabinet$|locker|fridge_body|fridge$|refrigerator|desk_body|desk$|sideboard|hutch|credenza|bureau|footlocker|crate$|_crate|hamper|amp_cab|radiator|filing|file_cab|tv_stand|dryer|washer|stove_body|range_body|oven_body|water_heater", re.I)
NOT_SLAB = re.compile(r"door|window|win_|glass|poster|mirror|curtain|blind|shutter|screen|panel|sign|board|banner|flag|sheet|cloth|drape|shade|ladder|pipe|post|column|pillar|stud|jamb|casing|header|trim|frame|rail|fence|gate|tree|trunk|pole|lamp|light|hose|cord|cable|conduit|duct|vent|chimney|flue|stack|silhouette|cutout|figure|person|body|bar$|counter|partition_glass|rack|case|shelf|shelv|cabinet|locker|fridge|cooler|vending|machine|booth|stall|divider|hedge|bush|shrub|awning|canopy|roof|eave|gutter|face|side|end|top|lid|hood|bed|mattress|pew|bench|altar|organ|piano|kiosk|column|tower|silo|tank|drum|barrel|crate|pallet|stack", re.I)
BED = re.compile(r"(^|_)(bed|cot|bunk)(_mattress|_frame|_platform)?$", re.I)
IGN = re.compile(r"(^|_)(floor|ceil|ceiling|rug|mat|carpet|slab|base|kick|toe|seam|stain|wear|decal|shadow)(_|$)", re.I)


def interior(boxes):
    floors = [(n, c, h) for n, c, h in boxes if re.match(r"(floor|.*_floor$|floor_slab|.*floor_slab)", n, re.I) and h[0] > 1.0 and h[1] > 1.0 and abs(c[2] + h[2]) < 0.12]
    if not floors:
        return None
    fn, fc, fh = max(floors, key=lambda b: b[2][0] * b[2][1])
    if not any(re.search(r"ceil", n, re.I) and abs(c[0] - fc[0]) < fh[0] and abs(c[1] - fc[1]) < fh[1] for n, c, h in boxes):
        return None
    return fc, fh


def nearest_wall(c, h, walls):
    best = None
    for wn, wc, wh in walls:
        ax = 0 if wh[0] < wh[1] else 1
        lat = 1 - ax
        if c[lat] - h[lat] > wc[lat] + wh[lat] + 0.05 or c[lat] + h[lat] < wc[lat] - wh[lat] - 0.05:
            continue
        gap = abs(c[ax] - wc[ax]) - wh[ax] - h[ax]
        if best is None or gap < best[1]:
            best = (wn, gap, ax)
    return best


def touches(a, b, tol=0.03):
    (ca, ha), (cb, hb) = a, b
    return all(abs(ca[i] - cb[i]) <= ha[i] + hb[i] + tol for i in range(3))


def audit(loc, boxes):
    out = []
    room = interior(boxes)
    if room is None:
        return out
    fc, fh = room
    inside = [(n, c, h) for n, c, h in boxes if abs(c[0] - fc[0]) < fh[0] + 0.3 and abs(c[1] - fc[1]) < fh[1] + 0.3]
    walls = [(n, c, h) for n, c, h in inside if WALL.search(n) and h[2] > 0.8 and min(h[0], h[1]) < 0.3 and "Base" not in n]
    # group multi-part pieces by their stem
    pieces = {}
    for n, c, h in inside:
        if IGN.search(n) or c[2] - h[2] > 0.35 or h[2] < 0.15 or max(h[0], h[1]) < 0.15:
            continue
        if WALL_CLASS.search(n):
            stem = re.split(r"_(Body|Top|Back|Side|Frame|Base|Door|Drawer|Shelf|Leg|Panel|Face)(_|$)", n)[0]
            pieces.setdefault(stem, []).append((n, c, h))
    beds = [(n, c, h) for n, c, h in inside if BED.search(n) and max(h[0], h[1]) > 0.6]
    def union(parts):
        lo = [min(c[i] - h[i] for n, c, h in parts) for i in range(3)]
        hi = [max(c[i] + h[i] for n, c, h in parts) for i in range(3)]
        return [(lo[i] + hi[i]) / 2.0 for i in range(3)], [(hi[i] - lo[i]) / 2.0 for i in range(3)]
    for stem, parts in pieces.items():
        n = max(parts, key=lambda b: b[2][0] * b[2][1] * b[2][2])[0]
        c, h = union(parts)                        # the whole piece, not its biggest part
        if min(h[0], h[1]) < 0.05:
            continue                               # a face panel or a handle on something else (a dishwasher front in a counter run)
        w = nearest_wall(c, h, walls)
        if w and w[1] <= 0.12:
            continue
        # leaning on another wall-class piece that IS on a wall is fine
        anchored = False
        for stem2, parts2 in pieces.items():
            if stem2 == stem:
                continue
            n2, c2, h2 = max(parts2, key=lambda b: b[2][0] * b[2][1] * b[2][2])
            w2 = nearest_wall(c2, h2, walls)
            if w2 and w2[1] <= 0.12 and touches((c, h), (c2, h2), 0.06):
                anchored = True
                break
        if not anchored and any(touches((c, h), (bc, bh), 0.06) for bn, bc, bh in beds):
            anchored = True                       # the footlocker at the bed's foot
        if not anchored:
            out.append(("OFF_WALL", n, "%.2f m off %s" % (w[1], w[0]) if w else "no wall in line"))
    for n, c, h in inside:
        if 2 * h[2] < 1.7 or min(h[0], h[1]) > 0.125 or max(h[0], h[1]) < 0.3 or WALL.search(n) or NOT_SLAB.search(n) or c[2] - h[2] > 0.3:
            continue
        ax = 0 if h[0] < h[1] else 1
        lat = 1 - ax
        ends_free = 0
        for sgn in (-1, 1):
            end = c[lat] + sgn * h[lat]
            reach = False
            for wn, wc, wh in walls:
                wax = 0 if wh[0] < wh[1] else 1
                if wax == lat:                     # a wall perpendicular to the slab
                    if abs(wc[lat] - sgn * wh[lat] - end) <= 0.10 and abs(c[ax] - wc[ax]) <= wh[ax] + h[ax] + 0.3:
                        reach = True
                else:                              # a wall in the slab's own plane, end to end
                    if abs(wc[ax] - c[ax]) <= wh[ax] + h[ax] + 0.05 and (wc[lat] - wh[lat] <= end + 0.10 and wc[lat] + wh[lat] >= end - 0.10):
                        reach = True
            if not reach:
                ends_free += 1
        if ends_free == 2:
            out.append(("FREE_SLAB", n, "%.2f × %.2f m, reaches no wall at either end" % (2 * h[lat], 2 * h[2])))
        elif ends_free == 1 and 2 * h[lat] < 3.0:
            # a partition that starts in the room and stops in the room's
            # middle (finn's 1.9 m bedroom slab, 1 m short of the W wall)
            out.append(("HALF_SLAB", n, "%.2f × %.2f m, one end reaches no wall" % (2 * h[lat], 2 * h[2])))
    for bn, bc, bh in beds:
        bw = nearest_wall(bc, bh, walls)
        if not bw or bw[1] > 0.30:
            continue
        for stem, parts in pieces.items():
            n, c, h = max(parts, key=lambda b: b[2][0] * b[2][1] * b[2][2])
            w = nearest_wall(c, h, walls)
            if not w or w[0] != bw[0] or w[1] > 0.12:
                continue
            lat = 1 - bw[2]
            gap = max(c[lat] - h[lat] - (bc[lat] + bh[lat]), bc[lat] - bh[lat] - (c[lat] + h[lat]))
            if 0.0 < gap < 0.45 and not re.search(r"nightstand|bedside", n, re.I):
                out.append(("TIGHT", n, "%.2f m from %s on %s" % (gap, bn, bw[0])))
    return out


def main():
    only = [a for a in sys.argv[1:] if not a.startswith("-")]
    P.A.install_stubs()
    tot = {"OFF_WALL": 0, "FREE_SLAB": 0, "HALF_SLAB": 0, "TIGHT": 0}
    for fn in sorted(os.listdir(LOCALES)):
        if not (fn.startswith("build_") and fn.endswith(".py")):
            continue
        loc = fn[6:-3]
        if only and loc not in only:
            continue
        boxes, _ = P.record_builder(os.path.join(LOCALES, fn))
        if not boxes:
            continue
        for kind, name, what in audit(loc, boxes):
            tot[kind] += 1
            print("%-9s %-28s %-28s %s" % (kind, loc, name, what))
    print("placement_audit · OFF_WALL %d · FREE_SLAB %d · HALF_SLAB %d · TIGHT %d" % (tot["OFF_WALL"], tot["FREE_SLAB"], tot["HALF_SLAB"], tot["TIGHT"]))
    return 0


if __name__ == "__main__":
    sys.exit(main())
