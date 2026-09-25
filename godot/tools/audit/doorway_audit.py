#!/usr/bin/env python3
"""doorway_audit — can you walk through the door? (2026-09-24)

The user on the 09-24 sheet: "doorways obstructed or misaligned". For
every door leaf a builder emits (a tall, door-sized, thin box named
*door*), this checks the CLEARANCE ZONE a person needs to use it: the
door's width, floor to 1.9 m, 0.9 m out on EACH side of the leaf.

  BLOCKED  — a solid, walk-blocking object (furniture, fixtures,
             stacks; not rugs, mats, floor decals, light fittings or
             the door's own parts) stands in the zone;
  ADRIFT   — the leaf is not in a wall: no wall-like box within 0.25 m
             of its plane along its full width (a door standing in the
             room, or a wall that moved without its door).

    python3 godot/tools/audit/doorway_audit.py            # all
    python3 godot/tools/audit/doorway_audit.py <locale>…  # some
A GATE since 2026-09-25 (exit 1 on any finding). What it learned on the
way from 59 BLOCKED / 194 ADRIFT to zero: a door set INTO a solid
massing (a motel wing, a shed, a house body) is HOSTED by it — the
massing is its wall, and the side inside the massing is nobody's room;
HouseW_0_Door's host is HouseW_0_Body, so no prefix skip; roads, curbs,
parked cars' pans and wheels, hanging robes, and sheets thinner than
12 mm (paper, posters, decals) do not block a doorway.
"""
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import prop_overlap_audit as P

LOCALES = os.path.normpath(os.path.join(HERE, "..", "blender", "locales"))
DOOR = re.compile(r"(^|_)(door|doorleaf|door_leaf|frontdoor|backdoor)(_|$|[0-9])", re.I)
DOOR_PART = re.compile(r"crack|reach|cage|cab_|cabinet|armoire|wardrobe|dresser|hutch|cupboard|vanity|fridge|freezer|oven|locker|stall|shower|car_|truck|van_|mirror|cooler|safe|garage|knob|handle|hinge|pull|plate|push|kick|sign|number|mat|stop|bell|peep|lock|chain|frame|jamb|trim|glass|window|panel|decal|seam|rail|bar|closer|sweep|header|lintel|casing|arch|sill|threshold|wreath|note|flyer|hook|mail|slot|shadow|wear", re.I)
WALLISH = re.compile(r"wall|part|partition|facade|siding|front|shell|panel|brick|hull|fence|gate", re.I)
IGNORE = re.compile(r"(^|_)(doorframe|deadbolt|stripcurtain|pipe|plumbing|conduit|cord|cable|wire|outlet|switch|plate|body|mass|massing|tile|walltile|wains|wainscot|backsplash|splash|floor|ceil|ceiling|ground|lawn|road|street|sidewalk|curb|rug|mat|carpet|runner|stain|wear|decal|seam|grid|tile|baseboard|base|crown|trim|light|lamp|bulb|practical|pendant|fixture|sconce|fan|vent|smoke|sprinkler|shadow|glow|spill|sky|far|band|horizon|fog|mist|haze|threshold|sill|path|walk|driveway|porch_slab|step|stair|landing|pan|wheel|tire|robe|coat|jacket|towel|scarf|apron|scuff|scratch|smear|drip|puddle)(_|$|[0-9])|stair|step|road|curb|sidewalk|driveway|lawn|grass", re.I)
# a sheet of paper, a poster, a decal: a person walks past it
THIN = 0.012
CLEAR = 0.9


def audit(loc, boxes):
    out = []
    for n, c, h in boxes:
        if not DOOR.search(n) or DOOR_PART.search(n):
            continue
        ax = 0 if h[0] < h[1] else 1            # the leaf's thin axis
        lat = 1 - ax
        width, thick, tall = 2 * h[lat], 2 * h[ax], 2 * h[2]
        if not (0.6 <= width <= 2.2 and tall >= 1.7 and thick <= 0.15):
            continue
        z0 = c[2] - h[2]
        prefix = re.split(r"_(?=[^_]*$)", n)[0]
        # HOSTS (2026-09-25): a door SET INTO a building massing — its
        # leaf flush with, or sunk a few cm into, a box that spans it
        # laterally and stands taller than it — is hosted by that box.
        # A façade massing is the wall; it neither blocks nor sets the
        # door adrift. 59 BLOCKED / 194 ADRIFT on the 09-24 report were
        # motel wings, strip malls and sheds "blocking" their own doors.
        # (no prefix skip here: HouseW_0_Door's host IS HouseW_0_Body;
        # door parts are thin, or match DOOR, and drop out that way)
        hosts = set()
        for n2, c2, h2 in boxes:
            if n2 == n or DOOR.search(n2):
                continue
            if h2[2] + c2[2] < c[2] + h[2] - 0.05 or 2 * h2[ax] < 0.05:
                continue
            if not (c2[lat] - h2[lat] <= c[lat] - h[lat] + 0.05 and c2[lat] + h2[lat] >= c[lat] + h[lat] - 0.05):
                continue
            # the leaf's slab lies within the box's slab, or stands on a face
            lo, hi = c2[ax] - h2[ax], c2[ax] + h2[ax]
            if lo - 0.035 <= c[ax] - h[ax] and c[ax] + h[ax] <= hi + 0.035:
                hosts.add(n2)
            elif abs(c[ax] - h[ax] - hi) <= 0.035 or abs(c[ax] + h[ax] - lo) <= 0.035:
                hosts.add(n2)
        # ADRIFT: a wall-like box in the leaf's plane beside it
        walled = bool(hosts)
        for n2, c2, h2 in boxes:
            if walled:
                break
            if n2 == n or not WALLISH.search(n2) or (DOOR.search(n2) and not n2.lower().startswith(("wall", "part"))):
                continue
            if h2[2] < 0.8 or min(h2[0], h2[1]) > 0.4:
                continue
            if abs(c2[ax] - c[ax]) > h2[ax] + h[ax] + 0.25:
                continue
            # touching the leaf's edge along the wall, or spanning it
            if c2[lat] - h2[lat] <= c[lat] + h[lat] + 0.15 and c2[lat] + h2[lat] >= c[lat] - h[lat] - 0.15:   # a frame's width
                walled = True
                break
        # BLOCKED: solids in the clearance zone on either side
        for side in (-1, 1):
            zlo = [0.0, 0.0, z0 + 0.12]
            zhi = [0.0, 0.0, z0 + 1.9]
            zlo[lat], zhi[lat] = c[lat] - h[lat] + 0.05, c[lat] + h[lat] - 0.05
            face = c[ax] + side * h[ax]
            zlo[ax], zhi[ax] = (face, face + side * CLEAR) if side > 0 else (face - CLEAR, face)
            # a door set into a solid massing: the side INSIDE the massing
            # is the building's interior nobody built — not a zone
            mid = [(zlo[i] + zhi[i]) / 2.0 for i in range(3)]
            if any(all(abs(mid[i] - c2[i]) < h2[i] for i in range(3)) for n2, c2, h2 in boxes if n2 in hosts):
                continue
            for n2, c2, h2 in boxes:
                if n2 == n or n2 in hosts or n2.startswith(prefix) or IGNORE.search(n2) or DOOR.search(n2):
                    continue
                if max(h2) < 0.05 or (min(h2) < THIN and not re.search(r"glass|pane|screen|fence|gate|grille", n2, re.I)):
                    continue                       # small clutter, a sheet on the wall
                if all(c2[i] - h2[i] < zhi[i] - 0.01 and c2[i] + h2[i] > zlo[i] + 0.01 for i in range(3)):
                    if WALLISH.search(n2) and h2[2] > 0.8:
                        continue                   # the wall the door sits in
                    out.append(("BLOCKED", n, n2, side))
                    break
        if not walled:
            out.append(("ADRIFT", n, "", 0))
    return out


def main():
    only = [a for a in sys.argv[1:] if not a.startswith("-")]
    P.A.install_stubs()
    tot = {"BLOCKED": 0, "ADRIFT": 0}
    n_doors = 0
    for fn in sorted(os.listdir(LOCALES)):
        if not (fn.startswith("build_") and fn.endswith(".py")):
            continue
        loc = fn[6:-3]
        if only and loc not in only:
            continue
        boxes, _ = P.record_builder(os.path.join(LOCALES, fn))
        if not boxes:
            continue
        for kind, door, what, side in audit(loc, boxes):
            tot[kind] += 1
            print("%-8s %-28s %-30s %s" % (kind, loc, door, ("%s (side %+d)" % (what, side)) if what else ""))
    print("doorway_audit · BLOCKED %d · ADRIFT %d" % (tot["BLOCKED"], tot["ADRIFT"]))
    return 1 if (tot["BLOCKED"] or tot["ADRIFT"]) else 0     # a gate since 2026-09-25


if __name__ == "__main__":
    sys.exit(main())
