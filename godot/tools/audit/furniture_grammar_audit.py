#!/usr/bin/env python3
"""Furniture-grammar audit — the room reads wrong before it reads primitive.

Born 2026-09-07 from one Deck session's worth of screenshots:
  · "lots of clipping on beds and weird pillow designs" — parts of ONE
    assembly overlapping each other. prop_overlap_audit treats every
    same-prefix part as one object and never reports these.
  · "an exploded office chair facing the wrong direction away from the
    desk it is seated at" — a chair back between the seat and the desk,
    hovering 2 cm above the seat with nothing holding it.
  · "a desk in the center of the room, not against a wall like desks
    normally are."
  · "cars don't park in the middle of streets. this keeps happening."
  · "weird broken overlapping geometry all over the place" on a desk
    of stacked papers.

Five report-only checks over every recordable builder (informational
in run_all_audits — a count to drive down, not a gate yet):

  INTRA     two parts of the same assembly (shared name prefix) whose
            boxes interpenetrate by more than INTRA_MIN on every axis,
            where the smaller part is not a designed tuck (thin sheets
            and decals under 6 mm are skipped; a part fully CONTAINED
            in another is skipped — drawers in pedestals, fill in pots).
  FLOAT     a prop-sized part (all sides < 1.6 m, not wall/ceiling-
            mounted by name) whose underside sits more than FLOAT_GAP
            above the highest surface under its footprint.
  CHAIR     a chair assembly (Chair / Stool / Seat with a Back part)
            within CHAIR_REACH of a Desk/Table/Counter top whose BACK
            is on the desk side of the seat — facing away.
  DESK      a Desk top none of whose long edges lies within WALL_GAP of
            a wall-class box (Wall / Partition / Hull).
  LANE      a car-class assembly whose footprint centre sits on a
            Road/Asphalt/Street box more than LANE_M from the road's
            nearest long edge — parked in the travel lane.

Usage:
    python3 godot/tools/audit/furniture_grammar_audit.py            # all
    python3 godot/tools/audit/furniture_grammar_audit.py <locale>…  # some
"""
import os
import re
import sys
from collections import defaultdict

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import prop_overlap_audit as P
import vantage_obstruction_audit as VO

INTRA_MIN = 0.03        # m · penetration on every axis to count
INTRA_THIN = 0.006      # m · sheets/decals thinner than this are tucks
INTRA_JOINT = 0.25      # m · within ONE named assembly, penetration up to this is a
                        # JOINT (rooted posts, mullions in rails, a head on a body,
                        # a door in its wall) — the rooting grammar says parts
                        # overlap on purpose. Deeper is a clip.
# locales whose ground is a heightfield MESH (no box the recorder can
# see): "nothing under it" is unmeasurable there, not a float
TERRAIN_LOCALES = {"graustark", "harmony_terrain", "small_wood_road"}
POKE_THIN = 0.12        # m · a member this thin in plan is a post / pole / leg
POKE_TOL = 0.03         # m · proud of the top AND below the bottom by this each way
# solids a member may pass through: a post is ROOTED through the slab
# or deck it stands on into the ground beneath
POKE_GROUND = re.compile(r"^(slab|foundation|floor|ground|footing|pad|dais|deck|platform|terrain|lot|apron|walk|sidewalk|stoop|porch|landing|boardwalk|pier|dock|wharf)$", re.I)
# members that pass through solids by design: a pole through a sign
# cabinet, a wire through a crossarm, a stem through a shade, a rope
# through a deck, a mast through a hull, a stack through a roof
POKE_OK = re.compile(r"^(wire|cable|rope|chain|line|string|stem|stalk|straw|antenna|aerial|mast|stack|flue|pipe|conduit|drain|downspout|gutter|vent|chimney|spire|finial|rod|bar|bolt|pin|nail|screw|needle|wick|candle|hi|lo|trans|cord|hose|tube|axle|shaft|spindle|hub|trunk|limb|twig|branch|leader|cane|reed|rebar|stake|wick|pole|pile|piling|column|col|pillar|post)$", re.I)
PAVING = re.compile(r"^(road|curb|sidewalk|walk|dash|driveway|apron|loop|path|ditch|ballast|tie|lot|strip|shore|quay|fender|mulch|gravel|paint|stripe|line|crosswalk|median|shoulder)$", re.I)
FLOAT_GAP = 0.045       # m (a seat 4 cm over its beam is on it)
FLOAT_MAX_SIDE = 1.6
CHAIR_REACH = 1.10     # m · seat centre to the table's nearest edge
WALL_GAP = 0.35
LANE_M = 1.4            # m · a parked car's centre sits ~1.0 m off the curb; a lane centre ~1.75

# Pairs whose bounding boxes MUST overlap because the recorder sees cones,
# cylinders and foliage as boxes: conifer tiers, blob lobes, fronds;
# the parts of one vehicle (a hub inside a wheel inside a body); the
# joints of a road bend's prism segments. Skipped in INTRA (2026-09-07
# classification of highway_101 / diner / riverfront: these three
# classes were 90% of the count).
VEHICLE_PART = re.compile(r"^(wheel|hub|spoke|tire|rim|body|cabin|cab|window|windows|windshield|winshld|rearwin|headlight|taillight|bumper|pillar|hood|lid|mirror|lightbar|pan|seat|grille|tailgate|wiper|door|handle|plate|glass|cushion|back|arm|shoulder)$", re.I)
ROAD_SEG = re.compile(r"^(road|hwy|highway|street|lane|asphalt|curb|shoulder)", re.I)
STRUCTURAL = re.compile(r"(wall|crown|molding|roof|chimney|eave|gable|ridge|joist|beam|truss|frame|jamb|header|sill|"
                        r"trim|baseboard|skirt|seam|stud|rafter|hull|deck|pillar|post|leg|rail|spray|stream|tube|wire|cable|rope|chain|port|porthole|strip|band|piling|stringer|girder|brace|lintel|partition|pedestal)", re.I)
MOUNTED = re.compile(r"(lamp|pendant|fan|shelf|sign|poster|frame|clock|board|wall|ceil|window|win_|curtain|light|fixture|cord|wire|"
                     r"pin|bolt|knob|lyric|page|plate|handle|pull|latch|seam|tab|pillar|mailbox|glass|badge|decal|sticker|label|logo|drawer|door|header|thermostat|rung|"
                     r"swing|hammock|shutter|crenel|dormer|chimney|socket|insulator|warn|digit|pennant|roster|paper|ephoto|plaque|tag|led|dish|strap|hose|cable|garment|coat|robe|hinge|border|marker|nozzle|spout|mural|patch|counterslab|weight|ladle|"
                     r"number|letter|text|line|stripe|trim|cap|lid|rim|handset|dial|button|switch|outlet|plug|vent|grille|key|"
                     r"pipe|vent|duct|hood|cabinet|cab_|upper|hang|rail|awning|banner|flag|bulb|chain|hook|mirror|calendar|"
                     r"crown|molding|beam|joist|truss|roof|eave|gutter|antenna|pole|mast|neon|bracket|sconce|smoke|hvac|"
                     r"drone|bird|crow|moss|leaf|branch|limb|canopy|cloud|fog|haze|sky|far|band|horizon|water|swell|foam|"
                     r"spray|stream|arc|balloon|kite|tarp|screen|monitor|tv|speaker|cam|ring|halo|glow|beam)", re.I)
WALLISH = re.compile(r"(^|_)(wall|partition|part_|hull|shell|facade)", re.I)
ROADISH = re.compile(r"(road|asphalt|street|lane|highway|hwy|drive$|_drive_|blvd|avenue)", re.I)
# Places a car is SUPPOSED to stand: lots, aprons, driveways, garages,
# frontage strips in front of stores. Not travel lanes.
PARKINGISH = re.compile(r"(lot|parking|apron|driveway|garage|frontage|carport|pad|bay|stall|pump)", re.I)
# Cars that are DRIVING (highway traffic, the delivery truck in its lane,
# Tem's northbound truck under the hood preset) — not parked anywhere.
MOVING = re.compile(r"(hwy9_car|traffic|deliverytruck|tem_truck|_moving|northbound|southbound)", re.I)
# Designed tucks between parts of one assembly: a bullnose into a
# counter top, liquid in a pot, a book in a shelf, a bulb in a shade.
TUCK = re.compile(r"^(bullnose|liquid|fill|water|coffee|foam|sixpack|interior|stock|marker|riser|laundry|shade|bulb|plate|book|manga|cushion|label|decal|band|stripe|trim|edge|lip|rim|cap|glass|screen)$", re.I)
CARISH = re.compile(r"(car|truck|sedan|van|pickup|cruiser|patrol|corolla|civic|wagon|jeep|suv|ambulance)", re.I)
CAR_PART = re.compile(r"(body|cab|cabin|hood|bed|roof)$", re.I)
DESKISH = re.compile(r"(desk|table|counter|bar_top|workbench|vanity|dining|fourtop|twotop|sixtop|draft|drawing)", re.I)
# seats that are not AT a table by design: wheelchairs, a chair on its
# side, rockers and porch swings
NOT_AT_TABLE = re.compile(r"(wheelchair|tipped|rocker|rocking|swing|porch)", re.I)
# Tables nobody sits AT: side, end, night, console, hall.
# (a coffee table stays IN: the roadhouse's meeting ring sits around one)
NOT_SEATING = re.compile(r"(side|end|night|console|hall|lamp|plant|tv|outline|zone|^z_|plate)", re.I)
# Desks that are freestanding BY DESIGN: a judge's bench, a clerk's
# desk in a courtroom, a ship's helm, a newsroom island.
# Whole locales whose desk is freestanding on purpose: Miller's former
# dining table set at the N window "so he sits with the rain behind
# him"; the New Orleans executive desk centred on the door; Antonio's
# desk turned to watch the AC; the WGUR operator console facing the rack.
DESK_FREESTANDING_LOCALES = {"miller_office", "new_orleans_office", "ember_ash_office", "wgur_transmitter_shack"}
DESK_FREESTANDING = re.compile(r"(judge|clerk|helm|newspaper|desk_[0-9]_top|reception|teller|island|kiosk|studio|cat_desk|drafting|drawing)", re.I)
TOPISH = re.compile(r"(top|surface|slab)(_[0-9]+)?$", re.I)


def part_class(name):
    """The last non-numeric word of a part name: Car_0_Wheel_FL → wheel."""
    parts = re.split(r"_", re.sub(r"(?<=[a-z])(?=[A-Z])", "_", name))
    parts = [p for p in parts if not re.fullmatch(r"[+\-]?\d+|[+\-]?\d|[A-Z]{1,2}", p)]
    return parts[-1].lower() if parts else name.lower()


def family(name):
    """The first two words of a name — the ASSEMBLY (Car_0_Wheel_0_Hub → Car_0)."""
    parts = name.split("_")
    return "_".join(parts[:2]) if len(parts) > 2 else parts[0]


def prefix_of(name):
    parts = name.split("_")
    if len(parts) == 1:
        return name
    # numeric / sign suffixes and generic part words belong to the parent
    while len(parts) > 1 and re.fullmatch(r"[+\-]?\d+|[+\-]\d|[A-Z]{1,2}", parts[-1]):
        parts.pop()      # numbers, signs and L/R/N/S/FL tags belong to the parent
    return parts[0] if len(parts) == 1 else "_".join(parts[:-1]) if len(parts) > 2 else parts[0]


def box_lohi(b):
    _n, c, h = b
    return tuple(c[i] - h[i] for i in range(3)), tuple(c[i] + h[i] for i in range(3))


def penetration(a, b):
    la, ha = box_lohi(a)
    lb, hb = box_lohi(b)
    pen = []
    for i in range(3):
        d = min(ha[i], hb[i]) - max(la[i], lb[i])
        if d <= 0:
            return None
        pen.append(d)
    return pen


def contained(a, b):
    la, ha = box_lohi(a)
    lb, hb = box_lohi(b)
    return all(lb[i] - 0.005 <= la[i] and ha[i] <= hb[i] + 0.005 for i in range(3))


def check_intra(boxes):
    groups = defaultdict(list)
    for b in boxes:
        if VO.IGNORE.search(b[0]):
            continue
        groups[prefix_of(b[0])].append(b)
    out = []
    for pre, parts in groups.items():
        if len(parts) < 2 or len(parts) > 400:
            continue
        for i in range(len(parts)):
            a = parts[i]
            if min(a[2]) * 2 < INTRA_THIN:
                continue
            for j in range(i + 1, len(parts)):
                b = parts[j]
                if min(b[2]) * 2 < INTRA_THIN:
                    continue
                pen = penetration(a, b)
                if pen is None or min(pen) < INTRA_MIN:
                    continue
                if contained(a, b) or contained(b, a):
                    continue
                if min(pen) <= INTRA_JOINT:
                    continue      # a joint, not a clip (2026-09-08: 4544 → the deep ones)
                if PAVING.search(part_class(a[0])) and PAVING.search(part_class(b[0])):
                    continue      # laid strips: curb over road edge, apron flare over driveway
                if STRUCTURAL.search(a[0]) and STRUCTURAL.search(b[0]):
                    continue      # joints: wall corners, crown mitres, roof/chimney, frame members
                if VO.PASSABLE.search(a[0]) or VO.PASSABLE.search(b[0]):
                    continue      # foliage tiers / lobes / fronds — cones and blobs as boxes
                if TUCK.search(part_class(a[0])) or TUCK.search(part_class(b[0])):
                    continue      # designed tucks: bullnose in a top, liquid in a pot, a book in its shelf
                if VEHICLE_PART.search(part_class(a[0])) and VEHICLE_PART.search(part_class(b[0])):
                    continue      # one rigid vehicle
                if ROAD_SEG.search(pre):
                    continue      # bend segments meet at their joints
                out.append((pre, a[0], b[0], min(pen)))
    return out


def check_poke(boxes):
    """POKE-THROUGH: a thin member of an assembly (a post, a pole, a leg,
    a spindle — min xy side ≤ POKE_THIN) that passes CLEAN THROUGH a solid
    part of the same assembly — its top above the part's top AND its
    bottom below the part's bottom, by more than POKE_TOL each way. A
    post rooted 4 cm into a seat is a joint; a post whose top stands
    proud of the seat it should stop under is the Deck's "exploded
    chair" (2026-09-08). Both-thin pairs (mullion × rail, a window grid)
    are excluded."""
    groups = defaultdict(list)
    for b in boxes:
        if VO.IGNORE.search(b[0]):
            continue
        groups[prefix_of(b[0])].append(b)
    out = []
    for pre, parts in groups.items():
        if len(parts) < 2 or len(parts) > 400:
            continue
        # a MEMBER is thin in BOTH plan dims (a post, a leg, a stem); a
        # sheet thin in one (a back panel, glass, a jamb, a door frame)
        # passes through shelves and slabs by design — except a chair
        # BACK through its SEAT, which is the exploded chair itself
        thin = [p for p in parts if p[2][2] * 2 >= 0.10
                and (max(p[2][0], p[2][1]) * 2 <= POKE_THIN * 1.7
                     or (part_class(p[0]) == "back" and min(p[2][0], p[2][1]) * 2 <= POKE_THIN))]
        solid = [p for p in parts if min(p[2][0], p[2][1]) * 2 > POKE_THIN * 2.5 and p[2][2] * 2 >= 0.03]
        for a in thin:
            if VO.PASSABLE.search(a[0]) or POKE_OK.search(part_class(a[0])):
                continue
            alo, ahi = box_lohi(a)
            for b in solid:
                if b is a or VO.PASSABLE.search(b[0]) or POKE_OK.search(part_class(b[0])) or POKE_GROUND.search(part_class(b[0])):
                    continue
                blo, bhi = box_lohi(b)
                # xy: the member's footprint must lie inside the part's
                if not (blo[0] <= a[1][0] <= bhi[0] and blo[1] <= a[1][1] <= bhi[1]):
                    continue
                if part_class(a[0]) == "back" and not re.search(r"(seat|cushion)$", b[0], re.I):
                    continue
                if ahi[2] > bhi[2] + POKE_TOL and alo[2] < blo[2] - POKE_TOL:
                    out.append((pre, a[0], b[0], ahi[2] - bhi[2]))
    return out


def check_float(boxes, terrain=False):
    real = [b for b in boxes]
    out = []
    for b in real:
        n, c, h = b
        if VO.IGNORE.search(n) or MOUNTED.search(n) or VO.PASSABLE.search(n):
            continue      # foliage leaders / lobes are not props that "float"
        if VEHICLE_PART.search(part_class(n)) and CARISH.search(n):
            continue      # a hub inside a tire, a cab on a chassis — the assembly holds it
        if max(h) * 2 > FLOAT_MAX_SIDE or min(h) * 2 < 0.01:
            continue
        bottom = c[2] - h[2]
        if bottom < 0.03:
            continue
        # highest support whose footprint overlaps ours (any overlap —
        # a mailbox on a thin post, a knob on a door face)
        best = None
        blo, bhi = box_lohi(b)
        pre = prefix_of(n)
        for o in real:
            if o is b:
                continue
            lo, hi = box_lohi(o)
            top = hi[2]
            # a support may penetrate us a little (a column into a seat,
            # a post into a mailbox) — anything topping out within 0.25 m
            # above our underside still holds us up
            if top > bottom + 0.25 or top < bottom - 3.0:
                continue
            if top > bottom:
                top = bottom
            # embedded in a sibling (a hub inside its wheel's box, a leader
            # in its crown): the sibling spans our underside → supported
            if family(o[0]) == family(n) and lo[2] - 0.02 <= bottom <= hi[2] + 0.02 and not (hi[0] < blo[0] or lo[0] > bhi[0] or hi[1] < blo[1] or lo[1] > bhi[1]):
                best = (bottom, o[0])
                break
            # EMBEDDED in a larger solid of another assembly — a book in
            # a one-box bookshelf body, a comic in a rack, a deck on a
            # wall board: the solid spans our underside and most of our
            # footprint → held (whether the embedding is ugly is the
            # overlap audit's question, not a float)
            if (lo[2] - 0.02 <= bottom <= hi[2] + 0.02
                    and o[2][0] * o[2][1] * o[2][2] > h[0] * h[1] * h[2]
                    and min(hi[0], bhi[0]) - max(lo[0], blo[0]) >= h[0]
                    and min(hi[1], bhi[1]) - max(lo[1], blo[1]) >= h[1]):
                best = (bottom, o[0])
                break
            if hi[0] < blo[0] or lo[0] > bhi[0] or hi[1] < blo[1] or lo[1] > bhi[1]:
                # a sibling part of the same assembly that touches us in
                # xy but sits beside (a back on posts, a knob on a face)
                if prefix_of(o[0]) == pre and top >= bottom - FLOAT_GAP:
                    best = (bottom, o[0])
                    break
                continue
            if best is None or top > best[0]:
                best = (top, o[0])
        if best is None:
            if bottom > FLOAT_GAP and not terrain:
                out.append((n, bottom, "(nothing under it)", bottom))
        elif bottom - best[0] > FLOAT_GAP:
            out.append((n, bottom, best[1], bottom - best[0]))
    return out


def check_chairs(boxes):
    groups = defaultdict(list)
    for b in boxes:
        groups[prefix_of(b[0])].append(b)
    # a top: named *_Top, or a FLAT slab (h < 0.12, > 0.3 m across) named
    # for a table — round cafe tables are often just "Group_Table"
    tops = [b for b in boxes if DESKISH.search(b[0]) and not NOT_SEATING.search(b[0])
            and (TOPISH.search(b[0]) or (b[2][2] * 2 < 0.12 and max(b[2][0], b[2][1]) * 2 > 0.3 and not re.search(r"(leg|post|pedestal|base|stem|foot|apron|stretcher)", b[0], re.I)))]
    out = []
    for pre, parts in groups.items():
        if not re.search(r"(chair|stool|seat)", pre, re.I) or NOT_AT_TABLE.search(pre):
            continue
        seat = [p for p in parts if re.search(r"seat", p[0], re.I) and not re.search(r"back", p[0], re.I)]
        back = [p for p in parts if re.search(r"back", p[0], re.I) and not re.search(r"post|leg", p[0], re.I)]
        if not seat or not back:
            continue
        sc = seat[0][1]
        bc = back[0][1]
        # the table this chair is AT: the top whose footprint comes
        # nearest the seat centre (a bar 1.5 m behind a ring of chairs
        # is not their table; the ring's own small table is)
        # every table within reach of the seat; the chair is fine if it
        # faces ANY of them (a meeting ring in front of a bar faces the
        # ring's table, not the bar)
        cands = []
        for t in tops:
            px = min(max(sc[0], t[1][0] - t[2][0]), t[1][0] + t[2][0])
            py = min(max(sc[1], t[1][1] - t[2][1]), t[1][1] + t[2][1])
            d = ((px - sc[0]) ** 2 + (py - sc[1]) ** 2) ** 0.5
            if d <= CHAIR_REACH:
                cands.append((d, t, (px - sc[0], py - sc[1])))
        if not cands:
            continue
        to_back = (bc[0] - sc[0], bc[1] - sc[1])
        faces_one = any(td[0] * to_back[0] + td[1] * to_back[1] <= 0.02 for _d, _t, td in cands)
        if not faces_one:
            cands.sort(key=lambda c: c[0])
            out.append((pre, cands[0][1][0]))
    return out


def check_desks(boxes):
    walls = [b for b in boxes if WALLISH.search(b[0]) and max(b[2]) * 2 > 1.5 and b[2][2] * 2 > 1.5]
    out = []
    for b in boxes:
        if not re.search(r"desk", b[0], re.I) or not TOPISH.search(b[0]) or DESK_FREESTANDING.search(b[0]):
            continue
        n, c, h = b
        if not walls:
            continue
        ok = False
        edges = ((c[0] - h[0], None), (c[0] + h[0], None), (None, c[1] - h[1]), (None, c[1] + h[1]))
        for w in walls:
            lo, hi = box_lohi(w)
            for ex, ey in edges:
                if ex is not None and (abs(ex - lo[0]) <= WALL_GAP or abs(ex - hi[0]) <= WALL_GAP) and lo[1] - 0.3 <= c[1] <= hi[1] + 0.3:
                    ok = True
                if ey is not None and (abs(ey - lo[1]) <= WALL_GAP or abs(ey - hi[1]) <= WALL_GAP) and lo[0] - 0.3 <= c[0] <= hi[0] + 0.3:
                    ok = True
        if not ok:
            out.append((n, c))
    return out


def check_lanes(boxes):
    roads = [b for b in boxes if ROADISH.search(b[0]) and not PARKINGISH.search(b[0])
             and not re.search(r"(line|stripe|mark|edge|shoulder|curb|sign|bend|post|median|ramp)", b[0], re.I)
             and max(b[2][0], b[2][1]) * 2 > 12.0 and b[2][2] * 2 < 0.6
             # a diagonal road recorded as one bounding box is wide in BOTH
             # dims — nothing can be measured against it. A two-lane
             # road with curbs is ≤ 9 m across; anything wider is either
             # a diagonal segment's inflated bbox or a boulevard, and
             # both fooled the audit (2026-09-08: two Phase II cars
             # parked 0.5 m clear of a diagonal road read as "2.2 m in
             # the lane" because the road's bbox was 15 m tall)
             and min(b[2][0], b[2][1]) * 2 < 10.0]
    cars = [b for b in boxes if CARISH.search(b[0]) and CAR_PART.search(b[0]) and max(b[2]) * 2 > 1.5
            and not MOVING.search(b[0])]
    out = []
    seen = set()
    for car in cars:
        pre = prefix_of(car[0])
        if pre in seen:
            continue
        cx, cy = car[1][0], car[1][1]
        for r in roads:
            lo, hi = box_lohi(r)
            if not (lo[0] <= cx <= hi[0] and lo[1] <= cy <= hi[1]):
                continue
            # distance to the nearest LONG edge; a square-ish road box is
            # a cul-de-sac bulb (a cylinder's bbox) — measure radially
            w, d = hi[0] - lo[0], hi[1] - lo[1]
            if 0.8 <= w / max(d, 1e-6) <= 1.25:
                rad = min(w, d) / 2.0
                d_edge = rad - ((cx - r[1][0]) ** 2 + (cy - r[1][1]) ** 2) ** 0.5
            elif w >= d:
                d_edge = min(cy - lo[1], hi[1] - cy)
            else:
                d_edge = min(cx - lo[0], hi[0] - cx)
            if d_edge > LANE_M:
                seen.add(pre)
                out.append((pre, r[0], d_edge))
                break
    return out


def main():
    only = [a for a in sys.argv[1:] if not a.startswith("--")]
    P.A.install_stubs()
    totals = defaultdict(int)
    names = sorted(fn[6:-3] for fn in os.listdir(P.A.LOCALES) if fn.startswith("build_") and fn.endswith(".py"))
    for locale in names:
        if only and locale not in only:
            continue
        boxes = VO.boxes_for(locale)
        if not boxes or len(boxes) < 20:
            continue
        intra = check_intra(boxes)
        poke = check_poke(boxes)
        flt = check_float(boxes, terrain=locale in TERRAIN_LOCALES)
        chairs = check_chairs(boxes)
        desks = [] if locale in DESK_FREESTANDING_LOCALES else check_desks(boxes)
        lanes = check_lanes(boxes)
        n = len(intra) + len(poke) + len(flt) + len(chairs) + len(desks) + len(lanes)
        if not n:
            continue
        print("== %s · INTRA %d · POKE %d · FLOAT %d · CHAIR %d · DESK %d · LANE %d" % (locale, len(intra), len(poke), len(flt), len(chairs), len(desks), len(lanes)))
        for pre, a, b, pen in sorted(intra, key=lambda r: -r[3])[:12]:
            print("   INTRA %.2fm  %-28s x %-28s" % (pen, a, b))
        for pre, a, b, proud in sorted(poke, key=lambda r: -r[3])[:12]:
            print("   POKE  %.2fm  %-28s through %-28s" % (proud, a, b))
        for nme, bottom, under, gap in sorted(flt, key=lambda r: -r[3])[:10]:
            print("   FLOAT %.2fm  %-28s hangs above %s" % (gap, nme, under))
        for pre, top in chairs:
            print("   CHAIR        %-28s back faces %s" % (pre, top))
        for nme, c in desks:
            print("   DESK         %-28s at (%.1f, %.1f) touches no wall" % (nme, c[0], c[1]))
        for pre, road, d in lanes:
            print("   LANE  %.1fm  %-28s in the travel lane of %s" % (d, pre, road))
        for k, v in (("INTRA", len(intra)), ("POKE", len(poke)), ("FLOAT", len(flt)), ("CHAIR", len(chairs)), ("DESK", len(desks)), ("LANE", len(lanes))):
            totals[k] += v
    print("\nfurniture_grammar_audit · INTRA %d · POKE %d · FLOAT %d · CHAIR %d · DESK %d · LANE %d" % (
        totals["INTRA"], totals["POKE"], totals["FLOAT"], totals["CHAIR"], totals["DESK"], totals["LANE"]))


if __name__ == "__main__":
    main()
