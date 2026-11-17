#!/usr/bin/env python3
"""Vantage-obstruction audit — is a wall in the camera's face?

Born 2026-09-03 from two Deck screenshots in a row: the cabin's
opening wide (the camera stood inside the bed alcove, the partition
filled 75% of frame) and Elicia's apartment (a wall across the right
60%). preset_vantage_audit could not see either — it asks whether
geometry lies INSIDE the cone, and a wall is geometry. This audit
asks the cinematographer's question: how far does the frame see, and
how much of it is one surface?

Method: for every Background3D preset with a recordable builder,
cast a fan of rays across the frame (9 columns across the horizontal
fov × 3 rows) against the builder's recorded boxes (axis-aligned
slabs, blender frame) and take the nearest hit per ray. A preset is
flagged when
  · NEAR:  ≥ NEAR_FRAC of rays hit within NEAR_M (something is in
           the lens), or
  · WALL:  one object owns ≥ WALL_FRAC of the rays and its median
           distance is under WALL_M (a surface fills the frame).
Ground / sky / horizon plates are ignored as hits (they are meant to
fill), so an open exterior looking at its own far bands passes.

--propose  for each flagged preset, grid-search camera positions
           (0.5 m step across the locale, eye height kept, not inside
           any box) × 24 yaws and print the best candidate by a score
           that rewards depth, distinct named objects in frame, and
           staying near the author's original position/yaw.

Usage:
    python3 godot/tools/audit/vantage_obstruction_audit.py
    python3 godot/tools/audit/vantage_obstruction_audit.py --propose
    python3 godot/tools/audit/vantage_obstruction_audit.py --all
"""
import math
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import prop_overlap_audit as P
import preset_vantage_audit as V

ROOT = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".."))
BLENDER_ALT = os.path.join(ROOT, "tools", "blender")

COLS, ROWS = 9, 3
# Vantages where the near geometry IS the shot: the cab presets frame
# the dash / the seat backs on purpose; the dock-end preset sits with
# its feet over the water and the planks fill the bottom of frame.
# (2026-10-04: miriam_subaru — vol 5's back-seat camera looks through
# the gap between the front seats; the seatbacks frame it on purpose.)
# (2026-10-17: amanda_fort_close — vol 3's "look at the billowing fort":
# the sheet lit blue by the TV fills the frame on purpose; copy_shop_copier
# — the melds' 4 a.m. copier, close on its lid and its pink scan light.)
# korean_bbq_table (2026-10-18) is seated at the booth over the grill: the
# table, the dishes and the hood are the picture.
DELIBERATE = {"amanda_fort_close", "copy_shop_copier", "korean_bbq_table", "vehicle_cab", "vehicle_cab_rear", "vehicle_cab_altima", "vehicle_cab_night", "vehicle_cab_rear_night", "vehicle_cab_altima_night", "miriam_subaru_night", "vehicle_cab_corolla", "vehicle_cab_corolla_night", "vehicle_cab_judgement_day", "cabin_road_truck", "lake_palestine_dock", "miriam_subaru", "nexcorp_van_cargo"}
NEAR_M, NEAR_FRAC = 1.0, 0.30
WALL_M, WALL_FRAC = 2.6, 0.45
# EMPTY (2026-09-07 · the diner's first shot was a yellow field with a
# door sliver): when this share of the fan hits nothing but fill —
# sky, ceiling, floor, far bands — the frame has no subject.
EMPTY_FRAC = 0.80
EMBED_TOL = 0.18
# Markers where an empty-ish frame is the shot (sky inserts, horizons).
# Subjects that ARE in the sky: a crow on a wire, a drone, the crown of a
# cypress, a crepe myrtle in bloom. An insert of them reads EMPTY by the
# sky rule and is right to (2026-09-10; each read by hand).
DELIBERATE_MARKERS = {
    ("cabin_road", "shot_insert_drone"), ("cabin_road", "shot_insert_crow"),
    # (pass 434) read by render when the gate began judging the aim gate's subject
    # (the part nearest the AXIS, not the lens): vol6 ch20 n106 the stage reads past
    # the rail, which clips the deck's front edge only; vol7 ch14_figure n39 the
    # laundromat's brick wall at the alley's end, framed between the alley's walls;
    # vol7 ch21_leaving n22 Per's mother sits on the crate Lena brought (the text's
    # staging: the figure IS on the subject); vol6 ch15 n38 the red Peugeot reads
    # through the window under its neon signs (a clearer pane is a next-draft aim)
    ("foxhole_bar", "shot_insert_stage__foxhole_bar"),
    ("salty_tome_interior", "shot_insert_laundromat__salty_tome_alley"),
    ("salty_tome_interior", "shot_insert_crate__salty_tome_leaving"),
    ("kwik_stop", "shot_insert_lot"),
    # (2026-11-04) "standing by the meat counter": the lens looks at the meat
    # case's cuts under the glass; the back counter behind it is the audit's
    # name match, and the case in front of it IS the view
    ("centro_grocery_aisle", "shot_insert_counter__centro_grocery_aisle"),
    # (2026-11-04) "He pulls into his driveway": the driveway WITH the sedan and
    # Jim's truck on it, from the lawn; the slab's centre is under the sedan
    ("henderson_porch_front", "shot_insert_driveway__henderson_porch_front"),
    # (2026-11-04) "The substation is a flat-roofed beige building ... off the
    # Bypass": the building from the south of its lot, the Miller truck and the
    # lot's cars at its door are the frame
    ("new_auburn_road", "shot_insert_substation__new_auburn_bypass"),
    ("miller_back_porch", "shot_insert_myrtle"), ("new_auburn_road", "shot_insert_cypress"),
    # (2026-10-04) inside Miriam's Subaru the back-seat close-ups are at
    # arm's length by design: the gap between the front seats Nicola
    # reaches through, and Miriam's eyes in the rearview.
    ("miriam_subaru", "shot_closeup_person"), ("miriam_subaru", "shot_closeup_person_b"),
    # (2026-10-06) the dock's smear insert is a SKY shot by design: "Above
    # the cedar, on the far horizon, the rust-colored thermal smear" — the
    # smear is a sky card, the cedars are passable, the ground is ignored.
    ("centro_stockroom", "shot_insert_smear"),
    # (2026-10-30) vol 3 ch7's rolls of quarters ride inside the Voyager, which
    # has no interior: the insert frames the van from close behind (marker_aim
    # KNOWN_UNRESOLVED); the only geometry named "roll" is Room 4's bedroll at
    # the motel 400 m off, which is not its subject.
    ("desert_route", "shot_insert_roll__utah_highway_day"),
    # (2026-10-31) curtain call's RUTA 77 board stands in the windshield's
    # corner above the hood, inside the car body's BOX (the cast is AABBs; the
    # body is a raked prism). The render reads the lettering clear.
    ("writers_desk", "shot_insert_sign__writers_desk_dawn"),
    # (2026-11-02) the pool insert stands on the S deck looking down across
    # the pool at its marked far wall: the near wall (the subject cluster's
    # centroid, nearest the lens) is under the slab's lip by construction
    ("skatepark", "shot_insert_pool__skatepark_day"),
    # (2026-11-03) Aaron's car in 2003 (vol3 ch8): the windshield and the
    # squeegee on the hood lie inside the car body's BOX (the cast is AABBs;
    # the body is a raked prism), as the writers_desk car's sign does
    ("nexcorp_fueling_station", "shot_insert_windshield__gas_station_2003_night"),
    ("nexcorp_fueling_station", "shot_insert_squeegee__gas_station_2003_night"),
    # (2026-11-03) "Faust takes the wheel": Judgement Day's raked windshield,
    # inside its body's BOX (the cast is AABBs)
    ("houston_bayou", "shot_insert_windshield__jd_river_turn"),
    # (2026-11-03) "The tires make the noise of oars": Judgement Day drives on
    # the river, its tires under the water's skin by design
    ("houston_bayou", "shot_insert_tires__jd_river"),
    # (2026-10-10) inside the van at the NexCorp pump the cargo bay is 1.96 m
    # wide: its close-ups are at arm's length by design, like the Subaru's.
    ("nexcorp_fueling_station", "shot_closeup_diego__nexcorp_van_cargo"),
    ("nexcorp_fueling_station", "shot_closeup_person__nexcorp_van_cargo"),
    ("nexcorp_fueling_station", "shot_closeup_person_b__nexcorp_van_cargo"),
    # (2026-10-10) the truck's bench seat: driver and passenger a cab-width apart
    ("cabin_road", "shot_closeup_person__cabin_road_truck"),
    ("cabin_road", "shot_closeup_person_b__cabin_road_truck"),
    # (2026-10-10) the crow on the traffic light at the county line: a bird against the sky
    ("county_line_station", "shot_insert_crow"),
    # (2026-10-10) vol7 ch2 over the jetty: "the sky over Smolvud was empty" — the insert IS the sky
    ("smolvud_jetty", "shot_insert_drone"),
    # (2026-10-10) the Altima's dash from the driver's eye: an abstract cue, the dash IS the frame
    ("vehicle_cab", "shot_insert_five__vehicle_cab_altima"),
    ("salty_tome_interior", "shot_closeup_lena__salty_tome_office"),   # Lena asleep on the couch: the couch is the frame
    ("salty_tome_interior", "shot_closeup_face__salty_tome_vigil"),    # "the face on the wall opened its eyes": the face painted on the mural wall is the frame
    ("board_lords_interior", "shot_closeup_kai__board_lords_office"),   # a 1.5 m nook: the desk and the chair are the frame
    ("board_lords_interior", "shot_closeup_person_b__board_lords_office"),
    ("hans_bakery_back_kitchen", "shot_closeup_finn__hans_bakery_back_door"),   # Finn beside his pickup: the truck is the frame
    ("miller_kitchen", "shot_closeup_bianca"),   # a seat framed across a dressed table: the runner and the bag are the frame
    ("miller_kitchen", "shot_closeup_sammy"),
    ("small_wood_police", "shot_closeup_julie"),   # the interview across the table (vol 2 ch9): the table is the frame
    ("small_wood_police", "shot_closeup_james"),
    ("cabin_interior", "shot_closeup_marina"),   # Marina under the blanket in the loft: the blanket is the frame
    ("vehicle_cab", "shot_insert_map"),   # the glove box from the driver's eye: the dash is the frame
    ("nate_garage", "shot_closeup_walt__nate_driveway"),   # Walt at the side door: the house is the frame
    ("vehicle_cab", "shot_insert_five__vehicle_cab_altima_night"),
}
# Builders whose recorded boxes do not sit where the runtime puts them
# (harmony_terrain drapes its props over a heightfield the recorder
# cannot follow: every highway9 preset read EMPTY at 100% while the
# Deck shows the stage). Skipped until the recorder learns the drape.
UNMEASURED = set()   # harmony_terrain measured since the _finalize_mesh hook (2026-09-07)
# Locales whose ground is a heightfield MESH the recorder does not see
# (graustark's 200×140 elevation grid): rays past a prop hit nothing,
# so "sees only sky" is an artifact there, not a verdict.
NO_EMPTY = {"graustark", "harmony_terrain"}
ASPECT = 16.0 / 9.0
# far(?!_door): "Far_Door" is the cedar tower's exit, not a backdrop band
# (2026-09-23: its closeup read as 100% sky once glass stopped blocking)
IGNORE = re.compile(r"(ground|sky|horizon|far(?!_door)|band|floor|ceil|void|sea\b|swamp_floor|lake_water|valley_floor|plinth$|template_(land|sea)|road_asphalt|asphalt$|hwy9_(asphalt|shoulder|median|emb|berm|paint|lane|fill)|_ribbon_|terrain)", re.I)
# What counts as NOTHING for the EMPTY test: sky, haze, far bands. Ground,
# floor, ceiling and road anchor a frame and are not empty (a highway
# preset looking down its own road is a picture; the diner's clock
# insert looking at a lit ceiling is caught by WALL, not EMPTY).
SKY = re.compile(r"(sky|horizon|far(?!_door)|band|void|haze)", re.I)
# Not solid for a LENS: fog, smoke, foliage tiers and lobes, shrubs,
# water spray. A camera may stand in a canopy or a fog bank and see
# through it (2026-09-07 · the drone insert in the Sitka crowns, the
# hexagon in Cape Perpetua's fog).
_PASSABLE_RE = re.compile(r"(fog|haze|mist|smoke|steam|cloud|canopy|foliage|_C[0-9]|_L[0-9]|salal|shrub|bush|leaf|leaves|spray|stream|"
                          r"crown|needles|fern|grass|reed|hedge|vine|ivy|moss|drape|sheer|curtain|frond|palm|leader|"
                          r"pine|fir|spruce|cedar|cypress|oak|alder|willow|maple|tree)", re.I)
# NOT glass (2026-09-24, reverting 09-23's "glass|_warm$"): the pipeline
# has no alpha, so a glass slab and its warm tint pane render OPAQUE.
# Calling them passable made the cabin's crow insert pass while the
# frame showed a grey pane and no crow. A lens sees through a window
# only when the window has no glass (make_window(see_through=True)).
# GLASS AGAIN (2026-10-03): scripts/LocaleGlass.gd turns the builders'
# vertex alpha into real transparency at load, so a pane IS seen
# through now (Montreal's drainpipe insert looks out through the north
# window). A pane the builder made opaque on purpose (the diner's
# night glass, alpha 1.0) will pass here and show a slab in the render
# — the montage is the gate for those.
# (2026-11-08) a windshield is glass too: the cab's Cab_Windshield is
# alpha 0.35, and the night drive's road frame looks out through it
_GLASS_RE = re.compile(r"(glass|_pane\b|pane_|_warm\b|windshield|windscreen)", re.I)   # make_window's warm sun pane too
_SOLID_RE = re.compile(r"(trunk|stump|log|pole|post|butt)", re.I)


class _Passable:
    """regex-like: .search(name) is truthy for foliage / fog / spray
    parts a lens may stand in and see through — never for a trunk."""
    def search(self, name):
        if _GLASS_RE.search(name):
            return True
        return bool(_PASSABLE_RE.search(name)) and not _SOLID_RE.search(name)


PASSABLE = _Passable()


def presets():
    src = open(V.GD).read()
    out = []
    for m in V.BLOCK.finditer(src):
        pid, body = m.group(1), m.group(2)
        om, rm, gm = V.ORIGIN.search(body), V.ROT.search(body), V.GLB.search(body)
        if not (om and rm and gm):
            continue
        fm = re.search(r'"fov":\s*([\d.]+)', body)
        fov = float(fm.group(1)) if fm else 60.0
        out.append((pid, gm.group(1),
                    tuple(V._ev(om.group(i)) for i in (1, 2, 3)),
                    tuple(V._ev(rm.group(i)) for i in (1, 2, 3)), fov))
    return out


_cache = {}
# (2026-10-28) A DISK CACHE of every builder's recorded boxes. Replaying a
# builder costs 10-60 s and every marker tool replays all ~260 of them, so a
# whole-game pass spent most of its hour re-learning geometry that had not
# changed (the Deck: "not getting much done"). The key is the builder's bytes
# + every shared _props module + the builders it imports + the recorder
# itself; any change to any of them re-records. Gitignored.
DISK_CACHE = os.path.join(os.path.dirname(os.path.abspath(__file__)), ".box_cache")
_shared_sig = None


def _sig_files(paths):
    import hashlib
    h = hashlib.sha1()
    for fp in sorted(paths):
        try:
            h.update(fp.encode())
            h.update(open(fp, "rb").read())
        except OSError:
            pass
    return h.hexdigest()


def _builder_sig(path):
    global _shared_sig
    import glob as _g
    if _shared_sig is None:
        here = os.path.dirname(os.path.abspath(__file__))
        shared = _g.glob(os.path.join(P.A.LOCALES, "_props", "**", "*.py"), recursive=True)
        shared += _g.glob(os.path.join(BLENDER_ALT, "_props", "**", "*.py"), recursive=True)
        shared += [os.path.join(here, f) for f in ("prop_overlap_audit.py", "locale_geometry_audit.py")]
        _shared_sig = _sig_files(shared)
    deps = [path]
    src = open(path, encoding="utf-8", errors="replace").read()
    for m in re.finditer(r"^\s*(?:import|from) (build_\w+)", src, re.M):
        d = os.path.join(os.path.dirname(path), m.group(1) + ".py")
        if os.path.exists(d):
            deps.append(d)
    return _shared_sig + _sig_files(deps)


_imprecise = {}


def imprecise_for(locale):
    """The recorded parts of `locale` whose box is not their shape — the
    clipping and contact gates should not judge them by box. Re-records a
    set whose cache predates the list."""
    if locale in _imprecise:
        return _imprecise[locale]
    import json as _j
    import hashlib
    for cand in (os.path.join(P.A.LOCALES, "build_%s.py" % locale),
                 os.path.join(BLENDER_ALT, "build_%s.py" % locale)):
        if os.path.exists(cand):
            sig = hashlib.sha1(_builder_sig(cand).encode()).hexdigest()
            cf = os.path.join(DISK_CACHE, "%s.%s.json" % (locale, sig[:16]))
            rf = cf[:-5] + ".raw.json"
            if os.path.exists(rf):
                try:
                    _imprecise[locale] = set(_j.load(open(rf)))
                    return _imprecise[locale]
                except Exception:
                    pass
            if os.path.exists(cf):
                os.remove(cf)
            _cache.pop(locale, None)
            boxes_for(locale)
            return _imprecise.get(locale, set())
    return set()


def boxes_for(locale):
    if locale in _cache:
        return _cache[locale]
    for cand in (os.path.join(P.A.LOCALES, "build_%s.py" % locale),
                 os.path.join(BLENDER_ALT, "build_%s.py" % locale)):
        if os.path.exists(cand):
            import json as _j
            import hashlib
            sig = hashlib.sha1(_builder_sig(cand).encode()).hexdigest()
            cf = os.path.join(DISK_CACHE, "%s.%s.json" % (locale, sig[:16]))
            if os.path.exists(cf):
                try:
                    _cache[locale] = [(n, tuple(c), tuple(h)) for n, c, h in _j.load(open(cf))]
                    return _cache[locale]
                except Exception:
                    pass
            # a caller that skipped install_stubs() records the builder
            # without any _props part (no walls, tables, figures) and that
            # record would go to the disk cache every audit shares
            # (2026-10-30: a probe script did, and the police station read
            # 23 floating parts instead of 6)
            if not getattr(P.A, "STUBS_ON", False):
                P.A.install_stubs()
            bx, _err = P.record_builder(cand)
            _cache[locale] = bx or []
            names = {n for n, _c, _h in (bx or [])}
            _imprecise[locale] = set(P.A.RAW_IMPRECISE) & names
            if bx:
                try:
                    os.makedirs(DISK_CACHE, exist_ok=True)
                    for old_f in os.listdir(DISK_CACHE):
                        if old_f.startswith(locale + ".") and (old_f.count(".") == 2 or old_f.endswith(".raw.json")):
                            os.remove(os.path.join(DISK_CACHE, old_f))
                    tmp = cf + ".tmp"
                    _j.dump([[n, list(c), list(h)] for n, c, h in bx], open(tmp, "w"))
                    os.replace(tmp, cf)
                    # (pass 422) the parts whose box is not their shape (a
                    # curve, a diagonal strip, a ribbon on sloped ground)
                    _j.dump(sorted(_imprecise[locale]), open(cf[:-5] + ".raw.json", "w"))
                except OSError:
                    pass
            return _cache[locale]
    _cache[locale] = None
    return None


def ray_dir(pitch, yaw, dh, dv):
    """Godot camera: forward is -Z rotated by YXZ euler; offset the
    forward by dh (horizontal, radians) and dv (vertical). Returns
    the direction in the BLENDER frame (x, y, z-up)."""
    y = yaw + dh
    p = pitch + dv
    fg = (-math.sin(y) * math.cos(p), math.sin(p), -math.cos(y) * math.cos(p))
    return (fg[0], -fg[2], fg[1])


_SOLID = {}


def _solid(boxes, ignore):
    """The boxes a ray can hit, with their bounds worked out once (pass 381).
    cast() ran two pattern matches on every box for every ray — 200 rays a
    marker, 3,000 boxes in a crowded set, 4,000 markers: most of the gate's
    forty minutes was re.search. Same boxes, same order, same answers."""
    key = (id(boxes), ignore.pattern)
    hit = _SOLID.get(key)
    if hit is not None and hit[0] is boxes and hit[1] == len(boxes):
        return hit[2]
    if len(_SOLID) > 48:
        _SOLID.clear()
    out = [(name, c[0] - h[0], c[0] + h[0], c[1] - h[1], c[1] + h[1], c[2] - h[2], c[2] + h[2])
           for name, c, h in boxes if not (ignore.search(name) or PASSABLE.search(name))]
    _SOLID[key] = (boxes, len(boxes), out)
    return out


def cast(origin_b, d, boxes, ignore=None):
    """Nearest slab hit along d from origin_b. Returns (t, name)."""
    best, who = None, None
    ox, oy, oz = origin_b
    if ignore is None:
        ignore = IGNORE
    dx, dy, dz = d
    ax, ay, az = abs(dx) < 1e-9, abs(dy) < 1e-9, abs(dz) < 1e-9
    for name, x0, x1, y0, y1, z0, z1 in _solid(boxes, ignore):
        tmin, tmax = 0.0, 1e9
        if ax:
            if ox < x0 or ox > x1:
                continue
        else:
            t1, t2 = (x0 - ox) / dx, (x1 - ox) / dx
            if t1 > t2:
                t1, t2 = t2, t1
            if t1 > tmin:
                tmin = t1
            if t2 < tmax:
                tmax = t2
            if tmin > tmax:
                continue
        if ay:
            if oy < y0 or oy > y1:
                continue
        else:
            t1, t2 = (y0 - oy) / dy, (y1 - oy) / dy
            if t1 > t2:
                t1, t2 = t2, t1
            if t1 > tmin:
                tmin = t1
            if t2 < tmax:
                tmax = t2
            if tmin > tmax:
                continue
        if az:
            if oz < z0 or oz > z1:
                continue
        else:
            t1, t2 = (z0 - oz) / dz, (z1 - oz) / dz
            if t1 > t2:
                t1, t2 = t2, t1
            if t1 > tmin:
                tmin = t1
            if t2 < tmax:
                tmax = t2
            if tmin > tmax:
                continue
        if tmin > 0.02 and (best is None or tmin < best):
            best, who = tmin, name
    return best, who


def inside_any(pt, boxes):
    for name, c, h in boxes:
        if IGNORE.search(name) or PASSABLE.search(name):
            continue
        if all(abs(pt[i] - c[i]) < h[i] for i in range(3)):
            return name
    return None


def frame_stats(origin_b, pitch, yaw, fov, boxes):
    vf = math.radians(fov)
    hf = 2.0 * math.atan(math.tan(vf / 2.0) * ASPECT)
    hits = []
    anchored = []
    for r in range(ROWS):
        dv = (r - (ROWS - 1) / 2.0) * (vf / 2.5)
        for c in range(COLS):
            dh = (c - (COLS - 1) / 2.0) * (hf / (COLS - 1))
            d = ray_dir(pitch, yaw, dh, dv)
            t, who = cast(origin_b, d, boxes)
            hits.append((t if t is not None else 200.0, who))
            anchored.append(cast(origin_b, d, boxes, SKY)[0] is not None)
    n = float(len(hits))
    near = sum(1 for t, _ in hits if t < NEAR_M) / n
    # the WALL test reads the middle row only: floor and ceiling hits
    # in the outer rows are ignored fill and would dilute a wall that
    # spans the whole horizon of the frame (the cabin partition case).
    mid = hits[(ROWS // 2) * COLS:(ROWS // 2) * COLS + COLS]
    owners = {}
    for t, who in mid:
        if who:
            owners.setdefault(who, []).append(t)
    wall_name, wall_frac, wall_med = None, 0.0, 0.0
    for who, ts in owners.items():
        frac = len(ts) / float(len(mid))
        if frac > wall_frac:
            ts.sort()
            wall_name, wall_frac, wall_med = who, frac, ts[len(ts) // 2]
    dists = sorted(t for t, _ in hits)
    med = dists[len(dists) // 2]
    distinct = len({who.split("_")[0] for _, who in hits if who})
    hit = [t for t, _ in hits if t < 199.0]
    return dict(near=near, wall=wall_name, wall_frac=wall_frac, wall_med=wall_med,
                median=med, distinct=distinct, mean_depth=sum(min(t, 12.0) for t, _ in hits) / n,
                escape=1.0 - sum(1 for a in anchored if a) / n,
                owners=sorted({who for _, who in hits if who}),
                depth_hit=(sum(min(t, 9.0) for t in hit) / (9.0 * len(hit))) if hit else 0.0)


def verdict(st):
    why = []
    if st["near"] >= NEAR_FRAC:
        why.append("%.0f%% of frame within %.1fm" % (st["near"] * 100, NEAR_M))
    if st["wall"] and st["wall_frac"] >= WALL_FRAC and st["wall_med"] < WALL_M:
        why.append("%s fills %.0f%% at %.1fm" % (st["wall"], st["wall_frac"] * 100, st["wall_med"]))
    if st["escape"] >= EMPTY_FRAC and not st.get("no_empty", False):
        why.append("EMPTY: %.0f%% of the frame sees only fill/sky" % (st["escape"] * 100))
    return why


_CAMEL = re.compile(r"(?<=[a-z])(?=[A-Z])")
_SUPPORT = {"pole", "poles", "post", "posts", "pylon", "bracket", "brackets", "pedestal", "footing"}


def _holds(who, subj):
    """(2026-11-09) a subject's own pole, post or bracket HOLDS it, it does
    not hide it: the Cypress Motel's vacancy sign is mounted on its pole
    (any ray to the sign's centre meets the pole's box first), the
    carnival's faded banner hangs between its posts"""
    parts = [p.lower() for p in _CAMEL.sub("_", who).split("_") if p]
    if not any(p in _SUPPORT for p in parts):
        return False
    stems = {p.lower() for s in subj for p in _CAMEL.sub("_", s).split("_")[:2] if len(p) >= 4}
    return any(p in stems for p in parts if p not in _SUPPORT)


def _rests_on(b, subj_boxes):
    """(2026-11-09) a thing standing ON the subject is what the insert
    shows, not what hides it: the substrate's bowl on the cabin's table"""
    if b is None:
        return False
    c, h = b[1], b[2]
    for sb in subj_boxes:
        sc, sh = sb[1], sb[2]
        top = sc[2] + sh[2]
        if abs((c[2] - h[2]) - top) <= 0.05 and abs(c[0] - sc[0]) <= sh[0] and abs(c[1] - sc[1]) <= sh[1]:
            return True
    return False


def _occlusion(origin_b, target_b, boxes, subj):
    """Five rays from the lens toward the subject (centre + 6 cm
    offsets). Returns the name of the first non-subject object that
    blocks a majority of them before they reach the subject, or None."""
    dx, dy, dz = (target_b[i] - origin_b[i] for i in range(3))
    dist = math.sqrt(dx * dx + dy * dy + dz * dz) or 1e-6
    d0 = (dx / dist, dy / dist, dz / dist)
    # a perpendicular pair for the offsets
    up = (0.0, 0.0, 1.0) if abs(d0[2]) < 0.9 else (1.0, 0.0, 0.0)
    side = (d0[1] * up[2] - d0[2] * up[1], d0[2] * up[0] - d0[0] * up[2], d0[0] * up[1] - d0[1] * up[0])
    sl = math.sqrt(sum(v * v for v in side)) or 1e-6
    side = tuple(v / sl for v in side)
    up2 = (d0[1] * side[2] - d0[2] * side[1], d0[2] * side[0] - d0[0] * side[2], d0[0] * side[1] - d0[1] * side[0])
    blockers = {}
    byname = {b[0]: b for b in boxes}
    for ox, oy in ((0, 0), (0.06, 0), (-0.06, 0), (0, 0.06), (0, -0.06)):
        tgt = tuple(target_b[i] + side[i] * ox + up2[i] * oy for i in range(3))
        v = tuple(tgt[i] - origin_b[i] for i in range(3))
        vl = math.sqrt(sum(a * a for a in v)) or 1e-6
        d = tuple(a / vl for a in v)
        t, who = cast(origin_b, d, boxes)
        # EMBED_TOL: a subject set INTO another surface — glass in a wall
        # slab, a board on a floor, an envelope lying in a desk top's
        # box — is hit through that surface from every angle. A blocker
        # that stops within EMBED_TOL of the subject is the subject's
        # mount, not an occluder (2026-09-07: this alone freed most of
        # the 19 STUCK markers — every window, mirror and board).
        if t is not None and who not in subj and t < vl - EMBED_TOL and not _holds(who, subj) \
                and not _rests_on(byname.get(who), [byname[x] for x in subj if x in byname]):
            blockers[who] = blockers.get(who, 0) + 1
    for who, k in blockers.items():
        if k >= 3:
            return who
    return None


HALF_HIDDEN = 0.40
_HALF_KNOWN = None


def _half_known():
    """half_hidden_baseline.json: the frames the reading flagged on the day
    it was written (pass 387), each still to be READ by render: fixed, or
    judged and noted. A list to read down, not a number to hold: a frame
    leaves it when it is fixed, and nothing is ever added to it."""
    global _HALF_KNOWN
    if _HALF_KNOWN is None:
        import json as _j
        fp = os.path.join(os.path.dirname(os.path.abspath(__file__)), "half_hidden_baseline.json")
        try:
            _d = _j.load(open(fp))
            _HALF_KNOWN = set(_d.get("to_read", [])) | set(_d.get("judged", {}))
        except (OSError, ValueError):
            _HALF_KNOWN = set()
    return _HALF_KNOWN


def _hidden_share(origin_b, pos_g, hits, boxes, subj, anchor=None):
    """(pass 387) How much of the subject can the lens SEE? `_occlusion`
    asks five rays at the cluster's centre, 6 cm apart, and passes when
    three arrive. Nate's set order (vol 6 ch14) is a sheet taped to an
    amp's grille with a second amp standing 0.7 m in front of it: the
    rays at the tape cleared that amp's top and the gate passed, with the
    lower half of the sheet behind the amp in the frame. Here every part
    of the subject cluster is sampled across its own face (centre and
    four points 70% of the way to its edges); returns (blocked, asked,
    the commonest blocker)."""
    import marker_aim_audit as M
    byname = {b[0]: b for b in boxes}
    def gd(a, b):
        return sum((x - y) ** 2 for x, y in zip(a, b)) ** 0.5
    # (pass 434) sample the cluster the gate judged (`anchor`, from best_subject),
    # not the matching part nearest the lens — they differ when the frame looks
    # past a near one (the cabin's dawn crow frame and the loft newel's crow)
    named = [h for h in hits if h[0] == anchor]
    nearest = named[0] if named else min(hits, key=lambda h: gd(h[1], pos_g))
    r = M.cluster_radius(gd(nearest[1], pos_g))
    parts = [h[0] for h in hits if gd(h[1], nearest[1]) < r]
    subj_boxes = [byname[x] for x in subj if x in byname]
    asked, blocked, who_n = 0, 0, {}
    for nm in parts:
        b = byname.get(nm)
        if b is None:
            continue
        c, h = b[1], b[2]
        ax = sorted(range(3), key=lambda i: -h[i])[:2]
        pts = [tuple(c)]
        for sa in (-0.7, 0.7):
            for sb in (-0.7, 0.7):
                q = list(c)
                q[ax[0]] += sa * h[ax[0]]
                q[ax[1]] += sb * h[ax[1]]
                pts.append(tuple(q))
        for q in pts:
            v = tuple(q[i] - origin_b[i] for i in range(3))
            vl = math.sqrt(sum(a * a for a in v)) or 1e-6
            t, who = cast(origin_b, tuple(a / vl for a in v), boxes)
            asked += 1
            if t is not None and who not in subj and t < vl - EMBED_TOL and not _holds(who, subj) \
                    and not _rests_on(byname.get(who), subj_boxes):
                blocked += 1
                who_n[who] = who_n.get(who, 0) + 1
    top = max(who_n, key=who_n.get) if who_n else None
    return blocked, asked, top


def _near_fraction_owned(origin_b, pitch, yaw, fov, boxes, subj):
    vf = math.radians(fov)
    hf = 2.0 * math.atan(math.tan(vf / 2.0) * ASPECT)
    owned = 0
    for r in range(ROWS):
        dv = (r - (ROWS - 1) / 2.0) * (vf / 2.5)
        for c in range(COLS):
            dh = (c - (COLS - 1) / 2.0) * (hf / (COLS - 1))
            t, who = cast(origin_b, ray_dir(pitch, yaw, dh, dv), boxes)
            if t is not None and t < NEAR_M and who in subj:
                owned += 1
    return owned / float(ROWS * COLS)


def _in_view(name, view):
    # (pass 374) the one rule, shared with the engine: tags and VIEW GROUPS
    import view_tags
    own = view_tags.owners(name)
    return own is None or view in own


PRESET_IDS = set()
STRIPS = {}


def _strips():
    """(2026-10-30) each preset's `strip` prefixes (Background3D removes those
    nodes for that view). The marker pass honoured `__<preset>` tags but not
    strips, so the batting team on the dugout bench (Game_Bat_*, stripped by
    the field views) "blocked" ballfield_home_plate's seat insert."""
    src = open(V.GD).read()
    out = {}
    for m in V.BLOCK.finditer(src):
        sm = re.search(r'"strip":\s*\[([^\]]*)\]', m.group(2))
        if sm:
            out[m.group(1)] = re.findall(r'"([^"]+)"', sm.group(1))
    return out


def _not_stripped(name, view):
    return not any(name.startswith(p) for p in STRIPS.get(view, ()))


def markers_pass(only, show_all):
    """Every vn_shot marker through the same fan (2026-09-07). The
    marker is a camera pose; fov from metadata/fov (default 42)."""
    import marker_aim_audit as M
    PRESET_IDS.update(p[0] for p in presets())
    STRIPS.update(_strips())
    flagged = []
    known = []
    n = 0
    for fn in sorted(os.listdir(M.LOCALES_TSCN)):
        if not fn.endswith(".tscn"):
            continue
        locale = fn[:-5]
        if only and locale not in only:
            continue
        path = os.path.join(M.LOCALES_TSCN, fn)
        markers = M.parse_markers(path)
        if not markers:
            continue
        glb = locale
        gm = re.search(r'path="res://assets/3d/locales/(\w+)\.glb"', open(path).read())
        if gm:
            glb = gm.group(1)
        boxes = boxes_for(glb)
        if not boxes:
            continue
        fovs = M.parse_marker_fovs(path)
        real = sum(1 for b in boxes if not IGNORE.search(b[0]))
        if real < 20 or glb in UNMEASURED:
            continue      # unmeasured builder (harmony_terrain's drape — see UNMEASURED)
        all_boxes = boxes
        for name, pos, rot in markers:
            # (2026-10-18) a box named `<Name>__<preset>…` exists only in
            # those presets (Background3D strips it elsewhere). Judge a marker
            # against what its own view loads: the marker's suffix if it has
            # one, else the locale's own preset (wagner_house_steps' open
            # front door is not in wagner_home's skateboard insert).
            view = name.split("__")[1] if "__" in name else locale
            boxes = [b for b in all_boxes if _in_view(b[0], view) and _not_stripped(b[0], view)] if view in PRESET_IDS else all_boxes
            name_geo = [(b[0], (b[1][0], b[1][2], -b[1][1])) for b in boxes]
            n += 1
            if name.startswith("shot_closeup_"):
                # judged as the game shows it: VnDirector levels a face frame
                # (CLOSEUP_PITCH_MIN/MAX, 2026-10-27)
                rot = (max(-0.07, min(0.035, rot[0])),) + tuple(rot[1:])
            o_b = (pos[0], -pos[2], pos[1])
            fov = fovs.get(name, 42.0)
            inside = inside_any(o_b, boxes)
            st = frame_stats(o_b, rot[0], rot[1], fov, boxes)
            why = []
            # a __preset suffix is not the subject (2026-10-09) — stripped for
            # INSERTS only: a suffixed closeup frames a person ("joanna"),
            # and her cat's tail is not her
            base = name.split("__")[0] if name.startswith("shot_insert_") else name
            cm = re.match(r"shot_(insert|closeup)_(\w+)$", base)
            hits = M.matches_for(cm.group(2), name_geo) if cm else []
            if hits:
                # A SUBJECT marker is judged by the cinematographer's
                # question — can the lens see the thing? — not by how
                # much of the frame the thing (or its table) fills.
                subj = {h[0] for h in hits}
                # (pass 434) the aim gate's subject (best_subject: nearest the lens,
                # unless another same-cue cluster sits closer to the axis), not the
                # part nearest the lens alone: the cabin's dawn crow frame looks out
                # at the truck's crow and was judged on the loft newel's carved crow
                # behind the camera's shoulder once the rail crow was stripped
                anchor_name, tgt_g, _a, _d = M.best_subject(hits, pos, M.yxz_forward(*rot))
                occl = _occlusion(o_b, (tgt_g[0], -tgt_g[2], tgt_g[1]), boxes, subj)
                if occl:
                    why.append("OCCLUDED: %s stands between the lens and %s" % (occl, anchor_name))
                elif name.startswith("shot_insert_"):
                    hb, ha, hw = _hidden_share(o_b, pos, hits, boxes, subj, anchor_name)
                    # three points at least: two corners of a one-part subject
                    # (a water tower's leg behind a fence rail) is a foreground
                    if ha >= 5 and hb >= 3 and hb >= HALF_HIDDEN * ha:
                        if "%s:%s" % (locale, name) in _half_known():
                            known.append((locale, name, hw, hb, ha, anchor_name))
                        else:
                            why.append("HALF HIDDEN: %s covers %d of %d points of %s" % (hw, hb, ha, anchor_name))
                if st["escape"] >= EMPTY_FRAC and glb not in NO_EMPTY:
                    why.append("EMPTY: %.0f%% of the frame sees only sky" % (st["escape"] * 100))
            else:
                why = verdict(st)
            if (locale, name) in DELIBERATE_MARKERS and not inside:
                why = []
            if inside:
                why.insert(0, "camera INSIDE %s" % inside)
            if why or show_all:
                flagged.append((locale, name, why, st))
    print("vantage_obstruction_audit --markers · %d marker(s) cast" % n)
    for locale, name, hw, hb, ha, an in known:
        print("to read    %-22s %-30s HALF HIDDEN (listed): %s covers %d of %d points of %s" % (locale, name, hw, hb, ha, an))
    bad = 0
    for locale, name, why, st in flagged:
        if why:
            bad += 1
        print("%s %-22s %-30s median %.1fm · %2d distinct · %s" % (
            "OBSTRUCTED" if why else "ok        ", locale, name, st["median"], st["distinct"], "; ".join(why)))
    print("\n%d obstructed marker(s)" % bad)
    return 1 if bad else 0


def score(st, origin_b, yaw, o0, yaw0):
    dpos = math.hypot(origin_b[0] - o0[0], origin_b[1] - o0[1])
    dyaw = abs((yaw - yaw0 + math.pi) % (2 * math.pi) - math.pi)
    # depth counts only where the frame lands on SOMETHING: an escaped
    # ray (open sky, a doorway into the void) is not a view of the set.
    # 20 proposals in the first run picked "median 200 m, 0 distinct".
    return st["depth_hit"] * 0.45 + min(st["distinct"], 16) / 16.0 * 0.40 \
        - st["near"] * 1.5 - st["escape"] * 0.6 \
        - (0.4 if st["wall"] and st["wall_frac"] >= WALL_FRAC and st["wall_med"] < WALL_M else 0.0) \
        - 0.02 * dpos - 0.06 * dyaw


def frame_stats_coarse(origin_b, pitch, yaw, fov, boxes):
    global COLS, ROWS
    c0, r0 = COLS, ROWS
    COLS, ROWS = 5, 1
    try:
        return frame_stats(origin_b, pitch, yaw, fov, boxes)
    finally:
        COLS, ROWS = c0, r0


def propose(pid, boxes, o_b, rot, fov):
    pitch, yaw0 = rot[0], rot[1]
    boxes = [b for b in boxes if abs(b[1][0] - o_b[0]) < 30.0 and abs(b[1][1] - o_b[1]) < 30.0]
    xs = [c[0] - h[0] for _, c, h in boxes if not IGNORE.search(_)] + [c[0] + h[0] for _, c, h in boxes if not IGNORE.search(_)]
    ys = [c[1] - h[1] for _, c, h in boxes if not IGNORE.search(_)] + [c[1] + h[1] for _, c, h in boxes if not IGNORE.search(_)]
    if not xs:
        return None
    x0, x1 = max(min(xs), o_b[0] - 8.0), min(max(xs), o_b[0] + 8.0)
    y0, y1 = max(min(ys), o_b[1] - 8.0), min(max(ys), o_b[1] + 8.0)
    best = None
    x = x0
    while x <= x1:
        y = y0
        while y <= y1:
            pt = (x, y, o_b[2])
            if inside_any(pt, boxes) is None:
                for k in range(16):
                    yaw = k * math.pi / 8.0
                    st = frame_stats_coarse(pt, pitch, yaw, fov, boxes)
                    sc = score(st, pt, yaw, o_b, yaw0)
                    if best is None or sc > best[0]:
                        best = (sc, pt, yaw, st)
            y += 0.75
        x += 0.75
    if best:
        sc, pt, yaw, _ = best
        # refine the winner's yaw at 7.5° and rescore with the full fan
        fine = None
        for k in range(-2, 3):
            y2 = yaw + k * math.pi / 24.0
            st = frame_stats(pt, pitch, y2, fov, boxes)
            sc2 = score(st, pt, y2, o_b, yaw0)
            if fine is None or sc2 > fine[0]:
                fine = (sc2, pt, y2, st)
        best = fine
    return best


def main():
    show_all = "--all" in sys.argv
    do_propose = "--propose" in sys.argv
    only = [a for a in sys.argv[1:] if not a.startswith("--")]
    P.A.install_stubs()
    if "--markers" in sys.argv:
        return markers_pass(only, show_all)
    flagged = []
    n = 0
    for pid, locale, o_g, rot, fov in presets():
        if only and pid not in only and locale not in only:
            continue
        boxes = boxes_for(locale)
        if not boxes or sum(1 for b in boxes if not IGNORE.search(b[0])) < 20:
            continue      # unmeasured builder (records only fill) — not a verdict
        if locale in UNMEASURED:
            continue
        n += 1
        o_b = (o_g[0], -o_g[2], o_g[1])
        inside = inside_any(o_b, boxes)
        st = frame_stats(o_b, rot[0], rot[1], fov, boxes)
        st["no_empty"] = locale in NO_EMPTY
        why = verdict(st)
        if pid in DELIBERATE and not inside:
            why = []
        if inside:
            why.insert(0, "camera INSIDE %s" % inside)
        if why or show_all:
            flagged.append((pid, locale, why, st, o_b, rot, fov, boxes))
    flagged.sort(key=lambda f: -(f[3]["near"] + f[3]["wall_frac"]))
    print("vantage_obstruction_audit · %d preset(s) cast" % n)
    bad = 0
    for pid, locale, why, st, o_b, rot, fov, boxes in flagged:
        if why:
            bad += 1
        print("%s %-28s median %.1fm · %2d distinct · %s" % (
            "OBSTRUCTED" if why else "ok        ", pid, st["median"], st["distinct"], "; ".join(why) if why else ""))
        if do_propose and why:
            b = propose(pid, boxes, o_b, rot, fov)
            if b:
                sc, pt, yaw, s2 = b
                print("     → propose origin Vector3(%.2f, %.2f, %.2f) yaw %.3f  (median %.1fm, %d distinct, near %.0f%%)" % (
                    pt[0], pt[2], -pt[1], yaw, s2["median"], s2["distinct"], s2["near"] * 100))
    print("\n%d obstructed vantage(s)" % bad)
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
