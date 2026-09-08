#!/usr/bin/env python3
"""marker_author.py — give a marker-less locale its first inserts (2026-09-10).

The Hierophant's chapel had no vn_shot markers at all, so every cue in
the chapter held the wide; a repo count found 32 more presets whose
scene carries ZERO markers — every [shot:] there is silent, and
shot_seed.py (which only uses markers that exist) can never cut there.

For each such locale this authors up to N `shot_insert_<prefix>`
markers on its hero objects: named prop assemblies (not walls, floors,
ceilings, glass, decals), 0.25–3 m across, standing below 2.2 m,
preferring the ones the chapters that use this locale actually NAME
in their prose (prose-anchored, the playbook's rule), then the larger
ones. Each marker's position comes from marker_reframe's ring search
(clear of geometry, not occluded, not an empty frame), scored toward
the preset camera so the insert is shot from the room's own side.
Markers are appended as position-form Marker3D nodes.

    python3 godot/tools/audit/marker_author.py --dry [locale…]
    python3 godot/tools/audit/marker_author.py [locale…]
    python3 godot/tools/audit/marker_author.py --cue <locale>:<cue>…   # one marker for a blind cue
    python3 godot/tools/audit/marker_author.py --closeup [locale…]     # a room's one closeup frame
    python3 godot/tools/audit/marker_author.py --closeup-b [locale…]   # its reverse shot, from the far side
"""
import collections
import json
import math
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import prop_overlap_audit as P
import vantage_obstruction_audit as VO
import marker_aim_audit as M
import marker_reframe as R
import shot_marker_audit as SM
import furniture_grammar_audit as G

ROOT = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
BG3D = os.path.join(ROOT, "godot", "scripts", "vn", "Background3D.gd")
N_INSERTS = 4
NOT_SUBJECT = re.compile(r"(wall|floor|ceil|roof|window|win_|glass|door|frame|jamb|sill|trim|baseboard|crown|molding|seam|grout|tile|plank|"
                         r"sky|horizon|far|band|void|ground|lawn|grass|dirt|asphalt|road|curb|sidewalk|path|walk|lot|terrain|"
                         r"light|lamp|fixture|fluor|tube|glow|shadow|stain|wear|decal|label|sticker|line|stripe|mark|"
                         r"^z_|zone|outline|hint|_ac$|beam|joist|rafter|stud|post$|pole|column|pillar|pipe|duct|vent|wire|cable|"
                         r"tree|shrub|hedge|bush|canopy|foliage|leaf|branch|trunk|cloud|moon|sun$|star|fog|haze|"
                         r"^rug|^carpet|^mat$|threshold|^slab|^step|^stair)", re.I)


def preset_cameras():
    """preset → (scene basename, camera_origin godot)."""
    src = open(BG3D).read()
    out = {}
    for m in re.finditer(r'"(\w+)":\s*\{(.*?)\n\t\}', src, re.S):
        preset, body = m.group(1), m.group(2)
        sm = re.search(r'"scene":\s*"res://scenes/locales/(\w+)\.tscn"', body)
        cm = re.search(r'"camera_origin":\s*Vector3\(([^)]+)\)', body)
        if sm and cm:
            vals = [float(v) for v in cm.group(1).split(",")]
            out[preset] = (sm.group(1), tuple(vals))
    return out


def chapter_text_for(scene_names):
    """All prose of every chapter whose bg resolves to one of these scenes."""
    cams = preset_cameras()
    presets = {p for p, (sc, _c) in cams.items() if sc in scene_names}
    blob = []
    for dirpath, _d, files in os.walk(SM.SCENES):
        for fn in files:
            if not fn.endswith(".json"):
                continue
            try:
                j = json.load(open(os.path.join(dirpath, fn)))
            except Exception:
                continue
            nodes = j.get("nodes", [])
            uses = any(n.get("t") == "bg" and str(n.get("src", ""))[3:] in presets for n in nodes)
            if not uses:
                continue
            for n in nodes:
                t = n.get("text")
                if isinstance(t, str):
                    blob.append(t.lower())
    return " ".join(blob)


def subjects_for(boxes, prose):
    groups = collections.defaultdict(list)
    for b in boxes:
        n = b[0]
        if VO.IGNORE.search(n) or NOT_SUBJECT.search(n) or n in P.MESH_NAMES:
            continue
        # group by the assembly's FIRST word: LongBooth_Ch0/Ch1/Ch2 are one
        # booth, Bench_0/Bench_1 one class of bench, Rack_Post/Rack_Hook the rack
        groups[n.split("_")[0]].append(b)
    scored = []
    for pre, parts in groups.items():
        lo = [min(b[1][i] - b[2][i] for b in parts) for i in range(3)]
        hi = [max(b[1][i] + b[2][i] for b in parts) for i in range(3)]
        size = max(hi[0] - lo[0], hi[1] - lo[1], hi[2] - lo[2])
        if size < 0.25 or size > 3.0 or lo[2] > 2.2:
            continue
        words = [w.lower() for w in re.split(r"_", re.sub(r"(?<=[a-z])(?=[A-Z])", "_", pre)) if len(w) >= 4]
        mentions = sum(len(re.findall(r"\b" + re.escape(w) + r"s?\b", prose)) for w in words)
        scored.append((mentions, size, pre, parts))
    scored.sort(key=lambda s: (-min(s[0], 12), -s[1]))
    return scored


def author(locale, tscn_path, glb, cam_g, prose, dry):
    boxes = VO.boxes_for(glb)
    if not boxes or sum(1 for b in boxes if not VO.IGNORE.search(b[0])) < 20:
        return 0
    lo, hi = R.locale_bounds(boxes)
    name_geo = [(b[0], (b[1][0], b[1][2], -b[1][1])) for b in boxes]
    made = []
    for mentions, size, pre, parts in subjects_for(boxes, prose):
        if len(made) >= N_INSERTS:
            break
        # the cue is the CamelCase-split name (StormHeap → storm_heap) so the
        # gates' matches_for resolves it; the subject set is THEIRS, not the
        # first-word group's, so the gate judges the same occlusion we did
        cue = "_".join(w.lower() for w in re.split(r"_", re.sub(r"(?<=[a-z])(?=[A-Z])", "_", pre)) if w)
        cue = re.sub(r"[^a-z0-9_]", "", cue)
        if not cue or any(c == cue for c, *_r in made):
            continue
        hits = M.matches_for(cue, name_geo)
        if not hits:
            print("   skip     %-22s (cue %s resolves to no geometry)" % (pre, cue))
            continue
        subj = {h[0] for h in hits}
        _an, tgt = M.subject_target(hits, cam_g)
        cands = R.candidates(tgt, R.subject_size(hits), cam_g, boxes, subj, lo, hi, hits)
        chosen = None
        for score, npos, d, el in cands[:60]:
            _a2, tgt2 = M.subject_target(hits, npos)
            rx, ry = R.aim(npos, tgt2)
            if VO._occlusion(R.to_b(npos), R.to_b(tgt2), boxes, subj):
                continue
            st = VO.frame_stats(R.to_b(npos), rx, ry, 35.0, boxes)
            if st["escape"] >= VO.EMPTY_FRAC and glb not in VO.NO_EMPTY:
                continue
            chosen = (npos, d, el, rx, ry)
            break
        if chosen is None:
            print("   stuck    %-22s (%d mention(s), %.1f m)" % (pre, mentions, size))
            continue
        npos, d, el, rx, ry = chosen
        made.append((cue, pre, mentions, size, npos, d, el, rx, ry))
        print("   insert   %-22s ← %-22s %2d mention(s) %.1f m  at (%.1f, %.1f, %.1f) %.1fm · %+.0f°" % (
            "shot_insert_" + cue, pre, mentions, size, npos[0], npos[1], npos[2], d, el))
    if made and not dry:
        blk = ["", "; first inserts, authored by marker_author.py (2026-09-10): the locale had no vn_shot markers"]
        for cue, pre, mentions, size, npos, d, el, rx, ry in made:
            blk.append('[node name="shot_insert_%s" type="Marker3D" parent="." groups=["vn_shot"]]' % cue)
            blk.append("position = Vector3(%.3f, %.3f, %.3f)" % npos)
            blk.append("rotation = Vector3(%.4f, %.4f, 0.0)" % (rx, ry))
            blk.append("metadata/fov = 35.0")
            blk.append("")
        with open(tscn_path, "a") as f:
            f.write("\n".join(blk))
    return len(made)


def author_cue(locale, cue, dry):
    """--cue <locale>:<cue>: author ONE shot_insert_<cue> for an authored
    cue that has an object but no marker (shot_marker_audit's blind list)."""
    path = os.path.join(M.LOCALES_TSCN, locale + ".tscn")
    src_txt = open(path).read()
    if ('name="shot_insert_%s"' % cue) in src_txt:
        print("== %s: shot_insert_%s exists" % (locale, cue))
        return 0
    gm = re.search(r'path="res://assets/3d/locales/(\w+)\.glb"', src_txt)
    glb = gm.group(1) if gm else locale
    cams = preset_cameras()
    cam = next((c for _p, (sc, c) in cams.items() if sc == locale), None)
    boxes = VO.boxes_for(glb)
    if cam is None or not boxes:
        print("== %s: no preset camera or boxes" % locale)
        return 0
    lo, hi = R.locale_bounds(boxes)
    name_geo = [(b[0], (b[1][0], b[1][2], -b[1][1])) for b in boxes]
    hits = M.matches_for(cue, name_geo)
    if not hits:
        print("== %s: cue %s resolves to no geometry" % (locale, cue))
        return 0
    subj = {h[0] for h in hits}
    _an, tgt = M.subject_target(hits, cam)
    for score, npos, d, el in R.candidates(tgt, R.subject_size(hits), cam, boxes, subj, lo, hi, hits)[:60]:
        _a2, tgt2 = M.subject_target(hits, npos)
        rx, ry = R.aim(npos, tgt2)
        if VO._occlusion(R.to_b(npos), R.to_b(tgt2), boxes, subj):
            continue
        st = VO.frame_stats(R.to_b(npos), rx, ry, 35.0, boxes)
        if st["escape"] >= VO.EMPTY_FRAC and glb not in VO.NO_EMPTY:
            continue
        print("== %s: shot_insert_%s at (%.1f, %.1f, %.1f) %.1fm · %+.0f°" % (locale, cue, npos[0], npos[1], npos[2], d, el))
        if not dry:
            blk = ["", "; authored by marker_author.py --cue (2026-09-10): the chapter cued it, nothing framed it",
                   '[node name="shot_insert_%s" type="Marker3D" parent="." groups=["vn_shot"]]' % cue,
                   "position = Vector3(%.3f, %.3f, %.3f)" % npos,
                   "rotation = Vector3(%.4f, %.4f, 0.0)" % (rx, ry),
                   "metadata/fov = 35.0", ""]
            with open(path, "a") as f:
                f.write("\n".join(blk))
        return 1
    print("== %s: cue %s — every clear position is occluded or empty" % (locale, cue))
    return 0


def author_closeup(locale, dry, side="a"):
    """--closeup: a room's ONE generic closeup frame — `shot_closeup_person`
    — for scenes whose chapters cue closeups of PEOPLE but carry no
    closeup marker at all (112 presets, 561 cues). VnDirector borrows
    any closeup marker for a missing one, so this single frame is what
    every cast closeup in the room cuts to: a bust-height frame of the
    room's conversation spot (the preset camera's look-point 3 m out),
    1.2–2.2 m off it, ≤ 25° down, passing the gate's fill verdict."""
    path = os.path.join(M.LOCALES_TSCN, locale + ".tscn")
    src_txt = open(path).read()
    mname = "shot_closeup_person" if side == "a" else "shot_closeup_person_b"
    if side == "a" and 'name="shot_closeup_' in src_txt:
        return 0
    if side == "b" and ('name="shot_closeup_person"' not in src_txt or ('name="%s"' % mname) in src_txt):
        return 0                      # the reverse shot only pairs with a generic frame
    a_pos = None
    if side == "b":
        am = re.search(r'name="shot_closeup_person"[^\n]*\nposition = Vector3\(([^)]+)\)', src_txt)
        if am:
            a_pos = tuple(float(v) for v in am.group(1).split(","))
    gm = re.search(r'path="res://assets/3d/locales/(\w+)\.glb"', src_txt)
    glb = gm.group(1) if gm else locale
    cams = preset_cameras()
    cam = None
    rot = None
    csrc = open(BG3D).read()
    for m in re.finditer(r'"(\w+)":\s*\{(.*?)\n\t\}', csrc, re.S):
        body = m.group(2)
        if ('"scene": "res://scenes/locales/%s.tscn"' % locale) in body:
            cm = re.search(r'"camera_origin":\s*Vector3\(([^)]+)\)', body)
            rm = re.search(r'"camera_rotation":\s*Vector3\(((?:[^()]|\([^()]*\))+)\)', body)
            if cm and rm:
                def _num(v):
                    v = v.strip()
                    dm = re.match(r"deg_to_rad\(([-0-9.]+)\)", v)
                    return math.radians(float(dm.group(1))) if dm else float(v)
                try:
                    cam = tuple(_num(v) for v in cm.group(1).split(","))
                    rot = tuple(_num(v) for v in re.split(r",(?![^(]*\))", rm.group(1)))
                except ValueError:
                    cam = rot = None
                break
    boxes = VO.boxes_for(glb)
    if cam is None or not boxes or sum(1 for b in boxes if not VO.IGNORE.search(b[0])) < 20:
        return 0
    lo, hi = R.locale_bounds(boxes)
    fwd = (-math.sin(rot[1]) * math.cos(rot[0]), math.sin(rot[0]), -math.cos(rot[1]) * math.cos(rot[0]))
    tgt = (cam[0] + fwd[0] * 3.0, 1.25, cam[2] + fwd[2] * 3.0)
    hits = [("_room", tgt)]
    # the reverse shot is searched from the far side of the spot: the
    # mirrored camera, so the two frames look at each other across it
    origin = cam if side == "a" else (2.0 * tgt[0] - cam[0], cam[1], 2.0 * tgt[2] - cam[2])
    for score, npos, d, el in R.candidates(tgt, 0.6, origin, boxes, set(), lo, hi, hits):
        if d < 1.2 or d > 2.2 or el > 25.0:
            continue
        if a_pos is not None and math.hypot(npos[0] - a_pos[0], npos[2] - a_pos[2]) < 1.5:
            continue                  # not the same side as the first frame
        rx, ry = R.aim(npos, tgt)
        st = VO.frame_stats(R.to_b(npos), rx, ry, 45.0, boxes)
        if VO.verdict(st) or VO.inside_any(R.to_b(npos), boxes):
            continue
        print("== %-28s %s at (%.1f, %.1f, %.1f) %.1fm · %+.0f° median %.1f distinct %d" % (locale, mname, npos[0], npos[1], npos[2], d, el, st["median"], st["distinct"]))
        if not dry:
            blk = ["", "; the room's %s closeup frame, authored by marker_author.py --closeup (2026-09-10)" % ("one" if side == "a" else "REVERSE"),
                   "; " + ("every closeup of a person cued here cuts to it (the scene had no closeup marker)" if side == "a" else "the far side of the same spot, so two speakers alternate sides"),
                   '[node name="%s" type="Marker3D" parent="." groups=["vn_shot"]]' % mname,
                   "position = Vector3(%.3f, %.3f, %.3f)" % npos,
                   "rotation = Vector3(%.4f, %.4f, 0.0)" % (rx, ry),
                   "metadata/fov = 45.0", ""]
            with open(path, "a") as f:
                f.write("\n".join(blk))
        return 1
    print("== %-28s stuck: no clear closeup frame" % locale)
    return 0


def main():
    dry = "--dry" in sys.argv
    only = [a for a in sys.argv[1:] if not a.startswith("--")]
    P.A.install_stubs()
    if "--closeup" in sys.argv or "--closeup-b" in sys.argv:
        side = "b" if "--closeup-b" in sys.argv else "a"
        n = 0
        for fn in sorted(os.listdir(M.LOCALES_TSCN)):
            if fn.endswith(".tscn") and (not only or fn[:-5] in only):
                n += author_closeup(fn[:-5], dry, side)
        print("\n%d closeup frame(s) %s" % (n, "planned" if dry else "authored"))
        return
    if "--cue" in sys.argv:
        n = 0
        for a in only:
            if ":" in a:
                loc, cue = a.split(":", 1)
                n += author_cue(loc, cue, dry)
        print("\n%d cue marker(s) %s" % (n, "planned" if dry else "authored"))
        return
    cams = preset_cameras()
    scene_cam = {}
    for preset, (sc, cam) in cams.items():
        scene_cam.setdefault(sc, cam)
    total = 0
    for fn in sorted(os.listdir(M.LOCALES_TSCN)):
        if not fn.endswith(".tscn"):
            continue
        locale = fn[:-5]
        if only and locale not in only:
            continue
        path = os.path.join(M.LOCALES_TSCN, fn)
        if M.parse_markers(path):
            continue                    # has markers already — reframe's job, not ours
        if locale not in scene_cam:
            continue                    # no preset looks at it
        src_txt = open(path).read()
        gm = re.search(r'path="res://assets/3d/locales/(\w+)\.glb"', src_txt)
        glb = gm.group(1) if gm else locale
        prose = chapter_text_for({locale})
        print("== %s (glb %s, %d chars of prose)" % (locale, glb, len(prose)))
        total += author(locale, path, glb, scene_cam[locale], prose, dry)
    print("\n%d insert marker(s) %s" % (total, "planned" if dry else "authored"))


if __name__ == "__main__":
    main()
