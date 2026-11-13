#!/usr/bin/env python3
"""wrong_room_audit.py — a closeup that cuts to another area (2026-09-12).

One .tscn serves several presets in different AREAS of the same
geometry: salty_tome_interior.tscn is the shop, the kitchenette and the
alley; the diner is the counter and the formal room; lake_palestine is
the shore and the dock. VnDirector resolves `[shot:closeup X]` by
marker NAME from the whole .tscn, so a scene on the dock that cued a
closeup of a person cut to the person/person_b pair authored at the
shore — 15.7 m away, a face in a different picture. Seventy such cuts
across 21 chapters, every one placed by a pass that had been declared
done.

The fix is PER-PRESET MARKERS: `<name>__<preset_id>` belongs to that
preset's area and wins while it is loaded (Background3D.find_shot_
marker / shot_markers_of_type). This audit resolves every closeup cue
the way the engine now does and fails when the frame it lands on is
more than FAR metres (12) from the preset's camera — a closeup is a face at
the conversation spot, and the conversation spot is near the camera.

INSERTS (pass 366, 2026-11-13). "An insert IS a cut to wherever the object
is" held until two rooms of one .tscn had an object of the same name: the
Chaus' bathroom line "razors found behind the mirror" cut to Mrs. Chau's
dresser mirror; the narrator's bedroom cut a floor down to the living
room's television; the Foxhole lot's "cargo van with a logo" cut to the
storm's van on the two-lane, 275 m off; the cedar tower's ground doors cut
to the fourth-floor landing. Nine such cuts, found by distance and read by
render. An `insert` / `wide` cue that resolves to a PLAIN marker (the preset
has none of its own) is reported when the marker
  - stands more than NEAR (8 m) from the preset's camera AND another preset
    of the same .tscn has its camera at less than half that distance — the
    object is in THAT preset's area — or
  - is more than LEVEL (2.2 m) above or below the camera: another storey.
Many such cuts are right (a tower on the hill, the bus across the lot, the
table indoors a porch line remembers). Each is READ BY RENDER and recorded
in KEPT_INSERT with the reason, or fixed: the preset's own marker
(`shot_insert_<id>__<preset>`), another cue, or no cue.

    python3 godot/tools/audit/wrong_room_audit.py
    python3 godot/tools/audit/wrong_room_audit.py --all

Gate at zero.
"""
import os as _os, sys as _sys
_sys.path.insert(0, _os.path.dirname(_os.path.abspath(__file__)))
import bg_resolve
import glob
import json
import math
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
ROOT = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
GODOT = os.path.join(ROOT, "godot")
SCENES = os.path.join(GODOT, "resources", "scenes")
TSCN = os.path.join(GODOT, "scenes", "locales")

import preset_vantage_audit as PV

# 12 m, not 8: the diner's own named closeups sit 8.4–11 m from its
# preset camera (the booth alcove vs the door) and are the same room;
# the formal room's are 21–23 m away and are not.
FAR = 12.0
CUE = re.compile(r"\[shot:closeup ([^\]]+)\]")

# (preset, cue id): reason — read and kept.
DELIBERATE = {}

OBJ = re.compile(r"\[shot:(insert|wide)\s+(\w+)~?\]")
NEAR = 8.0      # an object this near the camera is in the camera's own room
LEVEL = 2.2     # a storey

_DIORAMA = "the Estuary 7 diorama: its parts, from above"
_KESTREL = "Kestrel Mountain is one walk on several terraces"
# (preset, marker): why — each read by render (pass 366) and kept.
KEPT_INSERT = {
    ("graustark_wreck", "shot_insert_notebook"): "Sofia's notebook in Rio — no set of its own; the shotgun house's notebook stands in",
    ("graustark_wreck", "shot_insert_smoke_ring"): "the Frog on the bank over the wreck",
    ("graustark_ruins", "shot_insert_sinkhole"): "the sinkhole, across the ruins",
    ("graustark_chalk_wall", "shot_wide_threshold"): "the shotgun house's threshold, from the wall",
    ("graustark_cottage", "shot_insert_herbs"): "Joanna's herb patch outside",
    ("highway_101", "shot_insert_marker"): "the mile marker up the road",
    ("new_auburn_cedar_route", "shot_insert_cypress"): "the Cypress's sign, passed on the ride",
    ("new_auburn_strip_mall", "shot_insert_sedan"): "the white sedan in the FRONT lot (this camera is the back lot's)",
    ("daily_grind_interior", "shot_insert_tower"): "the tower on the hill, seen from town",
    ("kestrel_mountain", "shot_wide_town"): _KESTREL, ("kestrel_mountain_golden", "shot_wide_town"): _KESTREL,
    ("kestrel_mountain", "shot_insert_hedge"): _KESTREL, ("kestrel_mountain_golden", "shot_insert_hedge"): _KESTREL,
    ("kestrel_mountain", "shot_insert_bowl"): _KESTREL, ("kestrel_mountain_golden", "shot_insert_bowl"): _KESTREL,
    ("meadowlark_circle", "shot_insert_sprinklers"): "the lawns down the circle",
    ("small_wood_roadside", "shot_insert_coop"): "the coop beside the house up the road",
    ("small_wood_roadside", "shot_insert_house"): "the lit house up the road",
    ("small_wood_roadside", "shot_insert_fallen_house"): "the fallen-in house off the road",
    ("small_wood_road", "shot_insert_fallen_house"): "the fallen-in house off the road",
    ("lake_palestine_dock", "shot_insert_cooler"): "the cooler on the shore, from the dock",
    ("accretion_corridor", "shot_insert_door"): "the door at the corridor's far end",
    ("accretion_corridor", "shot_insert_desk"): "the desk past the corridor",
    ("estuary_7_template", "shot_insert_foundation"): _DIORAMA, ("estuary_7_template", "shot_insert_mill"): _DIORAMA,
    ("estuary_7_template", "shot_insert_drone"): _DIORAMA, ("estuary_7_template", "shot_insert_cabin"): _DIORAMA,
    ("estuary_7_template", "shot_insert_tide_pool"): _DIORAMA, ("estuary_7_template", "shot_insert_diner"): _DIORAMA,
    ("estuary_7_template", "shot_insert_cove"): _DIORAMA, ("estuary_7_template", "shot_insert_grove"): _DIORAMA,
    ("estuary_7_template", "shot_insert_tower"): _DIORAMA,
    ("hans_bakery_back_kitchen", "shot_insert_back_light"): "the back door's light, from the lot: 'The bakery's back-kitchen light was on'",
    ("nick_house_front", "shot_insert_minibike"): "the mini-bike outside the house",
    ("cabin_porch", "shot_insert_table"): "the table indoors he had been sitting at",
    ("cabin_porch_day", "shot_insert_bowls"): "the bowls on the table indoors: they go in",
    ("kwik_stop_interior", "shot_insert_coffee"): "the coffee station across the store",
    ("kwik_stop_interior", "shot_insert_window"): "the table by the window",
    ("missing_link_exterior", "shot_insert_bench"): "the shuttle bench outside",
    ("nick_drafting", "shot_insert_tv"): "the muted shopping channel in the next room, on a line about money",
    ("club_street_curb", "shot_insert_judgement_day"): "the car at the curb, the frame shirt on its glass",
    ("county_line_station", "shot_insert_crow"): "the crow up on the sign",
    ("vehicle_cab_side", "shot_insert_sedan"): "Claire's white sedan across the turnout",
    ("vehicle_cab_side", "shot_insert_phone"): "a phone in a dash cradle, tight: the pickup's stands in for hers",
}


def presets():
    src = open(PV.GD).read()
    out = {}
    for m in PV.BLOCK.finditer(src):
        pid, body = m.group(1), m.group(2)
        sm = re.search(r'"scene":\s*"res://scenes/locales/(\w+)\.tscn"', body)
        om = PV.ORIGIN.search(body)
        if sm and om:
            out[pid] = (sm.group(1), tuple(PV._ev(om.group(i)) for i in (1, 2, 3)))
    return out


_MK = {}


def markers(tscn):
    if tscn in _MK:
        return _MK[tscn]
    out = {}
    p = os.path.join(TSCN, tscn + ".tscn")
    if os.path.exists(p):
        src = open(p).read()
        for mm in re.finditer(r'\[node name="(shot_[\w]+)"[^\]]*\](.*?)(?=\n\[|\Z)', src, re.S):
            body = mm.group(2)
            pm = re.search(r"position = Vector3\(([^)]+)\)", body)
            tm = re.search(r"transform = Transform3D\(([^)]+)\)", body)
            if pm:
                v = [float(x) for x in pm.group(1).split(",")]
            elif tm:
                v = [float(x) for x in tm.group(1).split(",")][9:12]
            else:
                continue
            out[mm.group(1)] = tuple(v)
    _MK[tscn] = out
    return out


def resolve(mk, name, preset):
    """The engine's order: the preset's own marker, then the plain one,
    then the preset's generic pair, then the plain pair."""
    for cand in (name + "__" + preset, name,
                 "shot_closeup_person__" + preset, "shot_closeup_person"):
        if cand in mk:
            return cand
    return None


def cast_frame(mk, speaker, preset):
    """The speaker's own face frame for a generic person/person_b cue on a
    line they SAY (VnDirector + Background3D.find_cast_closeup, 2026-10-27):
    the preset's override, else the plain marker when this preset also uses
    the plain pair. None → the generic resolution stands."""
    ch = re.sub(r"_+", "_", re.sub(r"[^a-z0-9]", "_", speaker.lower())).strip("_")
    if not ch:
        return None
    if "shot_closeup_%s__%s" % (ch, preset) in mk:
        return "shot_closeup_%s__%s" % (ch, preset)
    if "shot_closeup_person__" + preset in mk:
        return None
    return "shot_closeup_" + ch if "shot_closeup_" + ch in mk else None


def insert_areas(pre, show_all):
    """Every insert / wide cue on a PLAIN marker that stands in another
    preset's area or on another level. Returns (checked, kept, problems)."""
    by_scene = {}
    for pid, (tscn, cam) in pre.items():
        by_scene.setdefault(tscn, []).append((pid, cam))
    seen, problems = {}, []
    checked = 0
    for f in sorted(glob.glob(os.path.join(SCENES, "**", "*.json"), recursive=True)):
        if os.path.basename(f) == "index.json":
            continue
        j = json.load(open(f, encoding="utf-8"))
        if not isinstance(j, dict):
            continue
        sid = j.get("id", os.path.basename(f)[:-5])
        pid = None
        for i, n in enumerate(j.get("nodes", [])):
            if n.get("t") == "bg":
                pid = bg_resolve.preset_of(n.get("src"), sid)
            if pid not in pre:
                continue
            tscn, cam = pre[pid]
            mk = markers(tscn)
            for typ, oid in OBJ.findall(str(n.get("text") or "")):
                base = "shot_%s_%s" % (typ, oid)
                if base + "__" + pid in mk or base not in mk:
                    continue           # the preset's own frame, or blind (shot_marker_audit's job)
                checked += 1
                if (pid, base) in seen:
                    continue
                pos = mk[base]
                d = math.dist(pos, cam)
                dy = abs(pos[1] - cam[1])
                near = min(((math.dist(pos, c2), q) for q, c2 in by_scene[tscn] if q != pid), default=(1e9, ""))
                why = ""
                if d > NEAR and near[0] * 2.0 < d:
                    why = "%.0f m off, in %s's area (%.0f m from its camera)" % (d, near[1], near[0])
                elif dy > LEVEL:
                    why = "%.1f m above or below the camera (another level)" % dy
                seen[(pid, base)] = why
                if why and (pid, base) not in KEPT_INSERT:
                    problems.append((sid, i, pid, base, why))
                elif why and show_all:
                    print("ok(kept) %-26s %-30s %s" % (pid, base, KEPT_INSERT[(pid, base)]))
    kept = sum(1 for k, w in seen.items() if w and k in KEPT_INSERT)
    stale = sorted(k for k in KEPT_INSERT if not seen.get(k))
    return checked, kept, problems, stale


def main():
    show_all = "--all" in sys.argv
    pre = presets()
    checked, problems = 0, []
    for f in sorted(glob.glob(os.path.join(SCENES, "**", "*.json"), recursive=True)):
        if os.path.basename(f) == "index.json":
            continue
        j = json.load(open(f, encoding="utf-8"))
        sid = j.get("id", os.path.basename(f)[:-5])
        pid = None
        for i, n in enumerate(j.get("nodes", [])):
            if n.get("t") == "bg":
                # the engine's reading: a painting bg_places swaps for a set
                pid = bg_resolve.preset_of(n.get("src"), sid)
                continue
            if pid not in pre:
                continue
            tscn, cam = pre[pid]
            mk = markers(tscn)
            for who in CUE.findall(str(n.get("text") or "")):
                cue = who.strip().split()[0]
                name = None
                if cue in ("person", "person_b") and n.get("t") == "say":
                    name = cast_frame(mk, str(n.get("char") or ""), pid)
                if name is None:
                    name = resolve(mk, "shot_closeup_" + cue, pid)
                if name is None:
                    continue           # blind — shot_marker_audit's job
                checked += 1
                d = math.dist(mk[name], cam)
                if d <= FAR:
                    continue
                if (pid, cue) in DELIBERATE:
                    if show_all:
                        print("ok(kept) %-26s %-14s %s" % (pid, cue, DELIBERATE[(pid, cue)]))
                    continue
                problems.append((sid, i, pid, cue, name, d))
    for sid, i, pid, cue, name, d in problems:
        print("ROOM    %-30s #%-4d closeup %-12s under %-26s lands on %s, %.1f m from the camera"
              % (sid, i, cue, pid, name, d))
    ichecked, ikept, iproblems, stale = insert_areas(pre, show_all)
    for sid, i, pid, base, why in iproblems:
        print("AREA    %-30s #%-4d %-30s under %-26s %s" % (sid, i, base, pid, why))
    for pid, base in stale:
        print("STALE   KEPT_INSERT (%s, %s) no longer applies: remove it" % (pid, base))
    print("\nwrong_room_audit · %d closeup cue(s) resolved · %d land in another area · "
          "%d insert/wide cue(s) on a plain marker · %d in another area or level "
          "(%d read and kept) · %d stale"
          % (checked, len(problems), ichecked, len(iproblems), ikept, len(stale)))
    return 1 if (problems or iproblems or stale) else 0


if __name__ == "__main__":
    sys.exit(main())
