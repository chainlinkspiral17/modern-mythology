#!/usr/bin/env python3
"""Prop-interpenetration audit — find the clipping.

The Gas & Go shipped with a beer fridge buried 0.55m inside the locker
bank and the entire locker row facing INTO the wall (every door,
handle, vent and number plate hidden in the plaster) — "objects
clipping through each other at odd angles." Nothing caught it because
the geometry audit measures reach, not collisions. This does.

For each requested builder it records every emitted box/cyl (both the
shared _props helpers and the vendored make_box copies in the early
hand-rolled builders), then reports pairwise AABB interpenetrations.

Filtering, so intentional contact doesn't drown the real finds:
  · same assembly (shared name prefix up to the last _segment) — a
    drawer inside its dresser is a feature
  · penetration <= EPS (1.5cm) — abutment is not clipping
  · pairs where one name matches WALLISH — doors/windows/signs/trim
    are EMBEDDED in walls on purpose; a prop overlapping a wall by
    more than EMBED_MAX (0.12m = wall thickness) still reports

Usage:
    python3 godot/tools/audit/prop_overlap_audit.py <builder> [...]
    python3 godot/tools/audit/prop_overlap_audit.py --all
"""
import os
import re
import sys
import types

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import locale_geometry_audit as A

EPS = 0.015
EMBED_MAX = 0.14   # wall thickness + proud trim/frame
WALLISH = re.compile(
    r"wall|window|door|sign|brand|part[nsew]?\b|trim|crown|"
    r"baseboard|backsplash|wainscot|frame|sill|floor|ceil|apron|"
    r"turf|road|grass|rug|mat|plumbing|curb|kerb|lawn|drive|sidewalk|path\b|path_|apron|asphalt|edgeline|shoulder|gravel|yard\b|headland|ground|walk\b|walkway|win\b|win_|outlet|socket|plate\b|numeral|slab|plaza|endzone|seam|shore|sand|dune", re.I)
CONTAINERISH = re.compile(
    r"cage|case|chest|bin\b|bin_|basket|crate|rack|cooler|fridge|"
    r"freezer|cubby|cart|shelf|shelv|island|hutch|drawer|cab\b|"
    r"cabinet|locker|oven|proofer|tub\b|vase|votive|sink|basin|"
    r"wrap|pallet\b|counter|vend|warmer|nightstand|dome", re.I)
# Objects RESTING on a surface: min-penetration axis is Z and one of
# the pair is a surface. Books sink 2cm into their shelf, a phone
# into its desk — seating, not clipping.
SURFACEISH = re.compile(
    r"shelf|shelv|top\b|_top|desk|table|counter|tray|sill|seat|"
    r"bench|plank|deck\b|worktop|platform|island|expo|step|cap\b|board|stand\b", re.I)
SEAT_MAX = 0.10
# Structure members joining each other (lattice-tower braces meeting
# legs, railing spindles into rails) — joints, not clipping.
CROWNISH = re.compile(r"crown|canopy|foliage|lobe|frond", re.I)
# Non-solid volumetrics: sprinkler spray arcs, light shafts, steam —
# they interpenetrate everything by design.
NONSOLID = re.compile(r"spray|mist|steam|smoke|shaft|glow|beam\b|dust|fog|surf|foam|wake|"
    r"falls?_|veil|cascade|plunge|water|thread|pool", re.I)
# Infrastructure DESIGNED to be buried — culverts under roads,
# pipes through creek beds, footings in the ground.
BURIEDISH = re.compile(r"culvert|drain|conduit|footing|foundation|piling", re.I)
# Rock against rock — talus piles, jagged outcrops, scree — is
# geology, not clipping.
ROCKISH = re.compile(r"jag|talus|rock|outcrop|boulder|scree|crag|cliff|rim\b|rim_|face\b|face_|gorge|tepui|ledge|"
                     # Collapsed masonry IS rubble — graustark's ruins
                     # interpenetrate each other and their sinkhole by
                     # design, and vegetation grows through them.
                     r"ruin|sinkhole|hump|coping|basin\b", re.I)
# Vegetation against vegetation (a shrub against a cypress buttress)
# is undergrowth, not clipping.
PLANTISH = re.compile(r"shrub|bush|hedge|fern|reed|weed|plant|vine|"
                      r"cypress|oak|conifer|tree|myrtle|magnolia|alder|sitka|spruce|"
                      r"cedar|fir\b|pine|birch|willow|green\b|green_|growth|ivy|moss|"
                      r"scrub|bramble", re.I)
ROOFISH = re.compile(r"eave|ridge|roof|gable|chimney|awning\b", re.I)
STRUCTISH = re.compile(
    r"leg|brace|strut|post|pole|beam|rail|truss|arm\b|_arm|spindle|"
    r"baluster|joist|stud\b|stud_|wire|cable|line|rope|cord|string|"
    r"knee\b|knee_|pipe|"
    r"stanchion", re.I)
# Seats TUCK under their work surface by use — a stool under a desk,
# a booth bench meeting the expo counter. Bounded so a chair buried
# waist-deep in a table still reports.
SEATISH = re.compile(r"stool|chair|bench|seat", re.I)
TUCK_MAX = 0.30
PORCHISH = re.compile(r"porch|veranda|stoop|balcony|marquee|portico|"
                      r"pediment", re.I)
PORCH_MAX = 0.30
# Wheels seat INTO wheel wells (car bodies) and into ground ruts.
WHEELISH = re.compile(r"wheel|tire|tyre", re.I)
WHEEL_MAX = 0.30
# Offerings LEAN on what they honor — a wreath hung on a marker, a
# posy laid against a vault base. Shallow contact only.
OFFERINGISH = re.compile(r"wreath|posy|bouquet|garland|flower|petal", re.I)
OFFERING_MAX = 0.10
# Flexible lines (cords, ropes, chains) and draped fabric CONFORM to
# whatever they cross or lie on — shallow interpenetration is the
# proxy geometry's way of touching.
FLEXISH = re.compile(r"wire|cable|cord|cord_|rope|chain|towel|rag|"
                     r"rag_|cloth|blanket|quilt|drape|linen|banner|"
                     r"pennant|festoon|valance|curtain|sock|laundry|shirt|jacket|"
                     r"strap|beanbag|paper\b", re.I)
FLEX_MAX = 0.25
# Landscaping features are mounded soft dirt — poles, hydrants,
# signs and wheels sink into berms and beds by planting/parking.
BERMISH = re.compile(r"berm|mulch|planter|flower_bed|_bed\b|hill", re.I)
BERM_MAX = 0.65
# A steamboat funnel passes THROUGH every deck and roof above it by
# construction (the diner's riverboat superstructure). Only excused
# when paired with a deck/roof — a soda-stack pyramid never is.
STACKISH = re.compile(r"\bstack|funnel|flue", re.I)
DECKISH = re.compile(r"deck|slab|ceil", re.I)
# Stair members rise THROUGH the floor/ceiling plane at the
# stairwell (the audit sees solid slabs, not the opening).
STAIRISH = re.compile(r"baluster|newel|handrail|stringer", re.I)
# Mounted light fixtures hang FROM / clamp ONTO their support.
LAMPISH = re.compile(r"lamp|shade\b|sconce", re.I)
LAMP_MAX = 0.20


def record_builder(path):
    """Record geometry from a builder, catching BOTH the shared
    _props helpers (via the audit stubs) and vendored local
    make_box/make_cyl definitions (by rebinding build_* globals)."""
    A.BOXES.clear()
    src = open(path).read()
    src = re.sub(r"^if __name__.*$[\s\S]*", "", src, flags=re.M)
    g = {"__name__": "_overlap_probe", "__file__": path}
    mod_dir = os.path.dirname(path)
    if mod_dir not in sys.path:
        sys.path.insert(0, mod_dir)
    try:
        exec(compile(src, path, "exec"), g)
    except Exception as e:
        return None, "%s: %s" % (type(e).__name__, e)

    def rec_box(name, center, size, base_color=None, *a, **k):
        A.BOXES.append((str(name), tuple(float(c) for c in center),
                        tuple(abs(float(s)) / 2.0 for s in size)))
        return A._obj_stub(name)

    def rec_cyl(name, center, radius, height, base_color=None,
                segments=8, axis='Z', *a, **k):
        r, h = abs(float(radius)), abs(float(height))
        half = {'Z': (r, r, h / 2), 'Y': (r, h / 2, r),
                'X': (h / 2, r, r)}.get(str(axis).upper(), (r, r, h / 2))
        A.BOXES.append((str(name), tuple(float(c) for c in center), half))
        return A._obj_stub(name)

    if "make_box" in g:
        g["make_box"] = rec_box
    if "make_cyl" in g:
        g["make_cyl"] = rec_cyl
    # harmony_terrain vendors same-signature local helpers under
    # distinct names — without these hooks its 6 highway9 presets
    # audited against ZERO recorded geometry.
    if "_make_box_local" in g:
        g["_make_box_local"] = rec_box
    if "_make_cyl_local" in g:
        g["_make_cyl_local"] = rec_cyl
    for noop_name in ("export_glb", "clear_scene"):
        if noop_name in g:
            g[noop_name] = lambda *a, **k: None

    def _rebound(fn):
        return types.FunctionType(fn.__code__, g, fn.__name__,
                                  fn.__defaults__)

    # Run the builder's CANONICAL entrypoint. Calling every build_*
    # alphabetically mis-runs composite builders — kwik_stop's
    # polish passes executed out of order produced 291 phantom
    # pairs. main() is the same sequence Blender runs.
    err = None
    if "main" in g and callable(g.get("main")):
        # main() calls module-level names, which resolve through g —
        # the vendored make_box/export_glb patches above apply.
        try:
            _rebound(g["main"])()
        except Exception as e:
            err = "main(): %s: %s" % (type(e).__name__, e)
    if err or "main" not in g:
        # Fallback sweep: run each build_* individually to recover
        # coverage past the failure point. Name-dedupe (first emit
        # wins) keeps main()'s canonical placements where both ran.
        for fname in sorted(g):
            fn = g[fname]
            if fname.startswith("build_") and callable(fn) and \
                    getattr(fn, "__code__", None) is not None:
                try:
                    _rebound(fn)()
                except Exception:
                    pass
    return list(A.BOXES), err


def overlaps(boxes):
    # Dedupe BY NAME, first emit wins: aggregate build_all()-style
    # functions re-run their children when we call every build_*,
    # and parameterized/seeded placement can re-emit the same name
    # at a shifted position — a phantom copy that pair-checks
    # against the real one. In an actual Blender run duplicate
    # names can't coexist (auto-.001 rename), so name-dedupe is
    # faithful to the real scene.
    seen = set()
    unique = []
    for b in boxes:
        if b[0] not in seen:
            seen.add(b[0])
            unique.append(b)
    boxes = unique
    # Classify each NAME once. The original pass re-ran the whole
    # regex battery per PAIR — fine at a few hundred objects, but
    # once the recorder stubs let riverfront's main() run to
    # completion it emits 4.6k boxes (~10M pairs) and the audit sat
    # for minutes. Flags are per-object properties; hoist them.
    ann = []
    for n, c, h in boxes:
        # Rooftop fixtures are named Roof_<Building>_... — strip the
        # Roof_ prefix for the assembly token so a building's own
        # HVAC/vents/ducts pair with it as same-assembly.
        first = n.split("_")[0]
        if first.lower() == "roof" and n.count("_") >= 2:
            first = n.split("_")[1]
        ann.append((
            n, c, h,
            n.rsplit("_", 1)[0], first,
            bool(NONSOLID.search(n)), bool(BURIEDISH.search(n)),
            bool(PLANTISH.search(n)), bool(ROCKISH.search(n)),
            bool(CROWNISH.search(n)), bool(WALLISH.search(n)),
            bool(CONTAINERISH.search(n)), bool(SURFACEISH.search(n)),
            bool(STRUCTISH.search(n)), bool(ROOFISH.search(n)),
            bool(PORCHISH.search(n)),
            bool(STACKISH.search(n)), bool(DECKISH.search(n)),
            bool(SEATISH.search(n)), bool(WHEELISH.search(n)),
            bool(OFFERINGISH.search(n)), bool(FLEXISH.search(n)),
            bool(BERMISH.search(n)), bool(STAIRISH.search(n)),
            bool(LAMPISH.search(n)),
        ))
    # Sweep-and-prune on x: sorted by min-x, the inner scan breaks at
    # the first box that starts past this one's max-x — every later
    # box starts even further right, so no x-overlap is possible.
    ann.sort(key=lambda b: b[1][0] - b[2][0])
    hits = []
    for i in range(len(ann)):
        (n1, c1, h1, p1l, p1f, ns1, bu1, pl1, rk1, cr1, wa1,
         co1, su1, st1, rf1, po1, sk1, dk1, se1, wh1, of1, fx1, bm1,
         sr1, lp1) = ann[i]
        xmax1 = c1[0] + h1[0]
        for j in range(i + 1, len(ann)):
            (n2, c2, h2, p2l, p2f, ns2, bu2, pl2, rk2, cr2, wa2,
             co2, su2, st2, rf2, po2, sk2, dk2, se2, wh2, of2, fx2, bm2,
             sr2, lp2) = ann[j]
            if c2[0] - h2[0] > xmax1:
                break
            if p1l == p2l or p1f == p2f:
                continue
            if ns1 or ns2:
                continue
            if bu1 or bu2:
                continue
            if pl1 and pl2:
                continue
            if rk1 and rk2:
                continue
            # Vegetation rooted in / draped over rock and walls grows
            # THROUGH them by nature — any depth.
            if (pl1 or cr1) and (wa2 or rk2):
                continue
            if (pl2 or cr2) and (wa1 or rk1):
                continue
            # Rock formations root INTO the ground plane; gorge and
            # cliff walls descend below grade through terrain sheets.
            if (rk1 and wa2) or (rk2 and wa1):
                continue
            # Containment: a small object whose center sits inside a
            # container-named object is contents, not clipping
            # (propane tanks in their cage, sixpacks in the fridge).
            if co1 and all(abs(c2[ax] - c1[ax]) < h1[ax]
                           for ax in range(3)):
                continue
            if co2 and all(abs(c1[ax] - c2[ax]) < h2[ax]
                           for ax in range(3)):
                continue
            # Pallet-jack forks ENTER pallets — that is their job.
            l1, l2 = n1.lower(), n2.lower()
            if ("fork" in l1 and "pallet" in l2) or \
                    ("fork" in l2 and "pallet" in l1):
                continue
            pen = []
            ok = True
            for ax in range(3):
                o = (h1[ax] + h2[ax]) - abs(c1[ax] - c2[ax])
                if o <= EPS:
                    ok = False
                    break
                pen.append(o)
            if not ok:
                continue
            depth = min(pen)
            # Report floor: contact artifacts (books against the case
            # back, a jacket draped on a bench, a phone seated on a
            # desk) all land under 4cm. Every confirmed-real clip so
            # far (gas station, faust, foxhole) was 0.05m+.
            if depth <= 0.04:
                continue
            if (wa1 or wa2) and depth <= EMBED_MAX:
                continue
            # Contents PRESS into their container's walls even when
            # their centers sit outside it (ice blocks proud of the
            # freezer, gum boxes on the checkout rack lip).
            if depth <= 0.25 and (co1 or co2):
                continue
            # TWO wall-class surfaces joining (partition into stall
            # wall, floor meeting wall, trim into facade) overlap by
            # a full member thickness at every corner and T-join.
            if wa1 and wa2 and depth <= 0.30:
                continue
            # Seat tucked under its work surface.
            if depth <= TUCK_MAX and ((se1 and su2) or (se2 and su1)):
                continue
            if depth <= SEAT_MAX and pen.index(depth) == 2 and \
                    (su1 or su2):
                continue
            if st1 and st2:
                continue
            if depth <= 0.40 and ((st1 and rf2) or (st2 and rf1)):
                continue
            # A rope/wire/pole ENDPOINT buried a few cm in whatever
            # anchors it is a fastening, not a clip (0.15 = one
            # gate-pier face; fence balusters land at 0.13).
            if depth <= 0.15 and (st1 or st2):
                continue
            # Porches, balconies, porticos TUCK INTO their building's
            # facade by construction.
            if depth <= PORCH_MAX and (po1 or po2):
                continue
            # Wheels seat into wheel wells and ground ruts.
            if depth <= WHEEL_MAX and (wh1 or wh2):
                continue
            # Offerings lean on what they honor.
            if depth <= OFFERING_MAX and (of1 or of2):
                continue
            # Flexible lines + draped fabric conform to what they touch.
            if depth <= FLEX_MAX and (fx1 or fx2):
                continue
            # Planted/parked into landscaping mounds.
            if depth <= BERM_MAX and (bm1 or bm2):
                continue
            # A post standing in a hedge/planting is planted, not
            # clipping (mailboxes in hedges, stakes in beds).
            if depth <= 0.35 and ((pl1 and st2) or (pl2 and st1)):
                continue
            # A tree crown over a roofline is natural adjacency —
            # canopies hang over eaves everywhere trees stand near
            # buildings. Trunks and buttresses are NOT excused.
            if (cr1 and rf2) or (cr2 and rf1):
                continue
            # Roof members JOIN each other — gables rise from roof
            # planes, eaves meet at hips and valleys.
            if rf1 and rf2:
                continue
            # Pillows and cushions nestle into sleepers and sofas.
            if depth <= 0.12 and ("pillow" in n1.lower() or
                                  "pillow" in n2.lower() or
                                  "cushion" in n1.lower() or
                                  "cushion" in n2.lower()):
                continue
            # A swing rope hangs THROUGH the canopy from its branch.
            if (cr1 and fx2) or (cr2 and fx1):
                continue
            # Cues lean against whatever is behind them.
            if depth <= 0.10 and ("cue" in n1.lower() or
                                  "cue" in n2.lower()):
                continue
            # Ducts run pressed along bands/soffits.
            if depth <= 0.15 and ("duct" in n1.lower() or
                                  "duct" in n2.lower()):
                continue
            # Funnel/stack through the decks and roofs above it.
            if (sk1 and (rf2 or dk2)) or (sk2 and (rf1 or dk1)):
                continue
            # Stair balustrade through the floor/ceiling plane at
            # the (uncut) stairwell opening.
            if depth <= 0.40 and ((sr1 and (wa2 or dk2)) or
                                  (sr2 and (wa1 or dk1))):
                continue
            # Mounted fixtures clamp onto their support.
            if depth <= LAMP_MAX and (lp1 or lp2):
                continue
            # Tickets/cards/neon tucked into or mounted on a mirror
            # frame — the classic backbar collage.
            if depth <= 0.10 and ("mirror" in n1.lower() or
                                  "mirror" in n2.lower()):
                continue
            # Objects stored on/against a shelf press into its
            # boards and neighbors.
            if depth <= 0.10 and ("shelf" in n1.lower() or
                                  "shelf" in n2.lower()):
                continue
            # A pew's contents (briefs, folders, cups) lean against
            # its back and seat.
            if depth <= 0.20 and ("pew" in n1.lower() or
                                  "pew" in n2.lower()):
                continue
            # Built-ins meet the ceiling.
            if depth <= 0.25 and ("ceil" in n1.lower() or
                                  "ceil" in n2.lower()):
                continue
            # A crown is an amorphous leaf mass — 35cm of foliage
            # against any surface reads as touching, not clipping.
            # Deeper crown burial still reports.
            if depth <= 0.35 and (cr1 or cr2):
                continue
            # Soft foliage nestles around whatever sits in it
            # (aquarium plants against the frog's log).
            if depth <= 0.15 and (pl1 or pl2):
                continue
            hits.append((depth, n1, n2, tuple(pen)))
    hits.sort(reverse=True)
    return hits


def main():
    args = sys.argv[1:]
    A.install_stubs()
    if "--all" in args:
        names = sorted(f[6:-3] for f in os.listdir(A.LOCALES)
                       if f.startswith("build_") and f.endswith(".py"))
    else:
        names = [a.replace("build_", "").replace(".py", "") for a in args]
    if not names:
        print(__doc__)
        return 1
    total = 0
    for name in names:
        path = os.path.join(A.LOCALES, "build_%s.py" % name)
        if not os.path.exists(path):
            print("%-32s NO BUILDER" % name)
            continue
        boxes, err = record_builder(path)
        if err and not boxes:
            print("%-32s ERR %s" % (name, err))
            continue
        if err:
            print("%-32s (partial: %s)" % (name, err))
        hits = overlaps(boxes)
        if hits:
            print("== %s · %d objects · %d clips" % (name, len(boxes), len(hits)))
            for depth, n1, n2, pen in hits[:20]:
                print("   CLIP %5.2fm  %-26s x %-26s" % (depth, n1, n2))
            if len(hits) > 20:
                print("   … %d more" % (len(hits) - 20))
            total += len(hits)
        elif "--all" not in args:
            print("%-32s clean (%d objects)" % (name, len(boxes)))
    print("\n%d clip(s) across %d builder(s)" % (total, len(names)))
    return 0


if __name__ == "__main__":
    sys.exit(main())
