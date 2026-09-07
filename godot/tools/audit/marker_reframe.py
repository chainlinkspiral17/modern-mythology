#!/usr/bin/env python3
"""Re-FRAME vn_shot markers whose subject the lens cannot see.

The third tool of the marker discipline (2026-09-07):
  marker_aim_audit   · does the marker FACE its subject?      (gate)
  marker_reaim       · turn it until it does                  (fix)
  vantage_obstruction --markers · can the lens SEE it?        (gate)
  marker_reframe     · MOVE it until it can                   (fix · this)

The Deck verdict that forced it: "real bad shot direction all
throughout the latter half of Major Arcana" — and the --markers pass
had 128 answers: 92 subjects occluded by a counter, a wall or a
chair back; 16 cameras standing inside a bookshelf, a seat back or
a partition; 12 frames that saw only sky.

Method: for every flagged marker that names a subject, search
positions on rings around the subject cluster — five distances
(scaled to the subject's size), 24 yaws, five elevations — keep the
ones that are not inside any box, inside the locale's bounds, and
from which the five-ray occlusion test passes; score by nearness to
the author's original position (their intent about WHERE the shot
comes from is kept as far as geometry allows), a preferred distance
for the subject's size, and a mild penalty on steep elevations. The
winner's position and aim are written into the .tscn — both marker
forms (`transform = Transform3D` origin and `position = Vector3`).

Usage:
    python3 godot/tools/audit/marker_reframe.py            # all flagged
    python3 godot/tools/audit/marker_reframe.py <locale>…  # some
    python3 godot/tools/audit/marker_reframe.py --dry      # report only
"""
import math
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import prop_overlap_audit as P
import vantage_obstruction_audit as VO
import marker_aim_audit as M

DISTS = (0.7, 1.0, 1.4, 2.0, 2.8)
YAWS = 24
ELEVS = (-10.0, 0.0, 15.0, 30.0, 45.0)      # degrees above the subject
MIN_EYE = 0.35                                # m · never lower than a kneeling lens
MAX_EYE = 2.6


def subject_size(hits):
    xs = [h[1][0] for h in hits]; ys = [h[1][1] for h in hits]; zs = [h[1][2] for h in hits]
    return max(max(xs) - min(xs), max(ys) - min(ys), max(zs) - min(zs), 0.1)


def preferred_dist(size):
    # a mug wants ~0.8 m, a bed ~2.4 m
    return min(3.0, max(0.7, 0.7 + size * 1.2))


def locale_bounds(boxes):
    real = [b for b in boxes if not VO.IGNORE.search(b[0])]
    lo = [min(b[1][i] - b[2][i] for b in real) for i in range(3)]
    hi = [max(b[1][i] + b[2][i] for b in real) for i in range(3)]
    return lo, hi


def aim(pos_g, tgt_g):
    dx, dy, dz = (tgt_g[i] - pos_g[i] for i in range(3))
    ry = math.atan2(-dx, -dz)
    rx = math.atan2(dy, math.hypot(dx, dz))
    return rx, ry


def to_b(g):
    return (g[0], -g[2], g[1])


WHY = None      # set to a dict by --why to tally rejection reasons


def candidates(tgt_g, size, orig_g, boxes, subj, lo, hi, hits):
    pref = preferred_dist(size)
    out = []
    # Big subjects (a wreck, a tower, a scoreboard) need bigger rings;
    # a HIGH subject (a sign on a pole, a drone in the crowns, a poster
    # near a ceiling, a window on an upper deck) lets the lens climb —
    # up to 1 m below the subject — and look UP at it (2026-09-07: six
    # of eleven stuck markers were only the 2.6 m eye clamp).
    dists = DISTS + ((4.0, 6.0, 9.0, 13.0) if size > 3.0 else ())
    elevs = ELEVS + ((-25.0, -40.0) if tgt_g[1] > 2.0 else ())
    max_eye = max(MAX_EYE, tgt_g[1] - 1.0)
    for d in dists:
        for yi in range(YAWS):
            a = yi * (2.0 * math.pi / YAWS)
            for el in elevs:
                e = math.radians(el)
                pos = (tgt_g[0] + math.cos(a) * d * math.cos(e),
                       tgt_g[1] + d * math.sin(e),
                       tgt_g[2] + math.sin(a) * d * math.cos(e))
                if pos[1] < MIN_EYE or pos[1] > max_eye:
                    if WHY is not None: WHY["eye"] = WHY.get("eye", 0) + 1
                    continue
                pb = to_b(pos)
                if not (lo[0] - 0.2 <= pb[0] <= hi[0] + 0.2 and lo[1] - 0.2 <= pb[1] <= hi[1] + 0.2):
                    if WHY is not None: WHY["bounds"] = WHY.get("bounds", 0) + 1
                    continue
                ins = VO.inside_any(pb, boxes)
                if ins:
                    if WHY is not None: WHY["inside " + ins] = WHY.get("inside " + ins, 0) + 1
                    continue
                # the subject as seen FROM THIS candidate (nearest part,
                # cluster widened by distance) — the same target the gates use
                _an, tgt_here = M.subject_target(hits, pos)
                occ = VO._occlusion(pb, to_b(tgt_here), boxes, subj)
                if occ:
                    if WHY is not None: WHY["occluded by " + occ] = WHY.get("occluded by " + occ, 0) + 1
                    continue
                dist_orig = math.sqrt(sum((pos[i] - orig_g[i]) ** 2 for i in range(3)))
                score = dist_orig + 1.6 * abs(d - pref) + 0.012 * abs(el - 15.0)
                out.append((score, pos, d, el))
    out.sort(key=lambda c: c[0])
    return out


def write_marker(src, name, pos, rx, ry):
    blk = re.search(r'\[node name="%s"[^\]]*\](.*?)(?=\n\[|\Z)' % re.escape(name), src, re.S)
    if not blk:
        return src, False
    body = blk.group(1)
    b0 = blk.start(1)
    tm = re.search(r'transform = Transform3D\(([^)]+)\)', body)
    pm = re.search(r'position = Vector3\(([^)]+)\)', body)
    if tm:
        vals = [v.strip() for v in tm.group(1).split(",")]
        vals[9:12] = ["%.3f" % pos[0], "%.3f" % pos[1], "%.3f" % pos[2]]
        body = body[:tm.start(1)] + ", ".join(vals) + body[tm.end(1):]
    elif pm:
        body = body[:pm.start(1)] + "%.3f, %.3f, %.3f" % pos + body[pm.end(1):]
    else:
        return src, False
    rot_m = re.search(r'rotation = Vector3\(([^)]+)\)', body)
    new_rot = "%.4f, %.4f, 0.0" % (rx, ry)
    if rot_m:
        body = body[:rot_m.start(1)] + new_rot + body[rot_m.end(1):]
    else:
        anchor = re.search(r'(transform = Transform3D\([^)]+\)|position = Vector3\([^)]+\))', body)
        body = body[:anchor.end()] + "\nrotation = Vector3(%s)" % new_rot + body[anchor.end():]
    return src[:b0] + body + src[blk.end(1):], True


def explain(locale, marker):
    """--why <locale> <marker>: tally why every candidate was rejected."""
    global WHY
    WHY = {}
    P.A.install_stubs()
    path = os.path.join(M.LOCALES_TSCN, locale + ".tscn")
    src_txt = open(path).read()
    glb = locale
    gm = re.search(r'path="res://assets/3d/locales/(\w+)\.glb"', src_txt)
    if gm:
        glb = gm.group(1)
    boxes = VO.boxes_for(glb)
    name_geo = [(b[0], (b[1][0], b[1][2], -b[1][1])) for b in boxes]
    lo, hi = locale_bounds(boxes)
    for name, pos, rot in M.parse_markers(path):
        if name != marker:
            continue
        cm = re.match(r"shot_(insert|closeup)_(\w+)$", name)
        hits = M.matches_for(cm.group(2), name_geo)
        anchor_name, tgt = M.subject_target(hits, pos)
        print("subject %s at godot (%.2f, %.2f, %.2f) · %d parts · marker at (%.2f, %.2f, %.2f)" % (anchor_name, tgt[0], tgt[1], tgt[2], len(hits), pos[0], pos[1], pos[2]))
        print("bounds x %.1f..%.1f  y %.1f..%.1f (blender)" % (lo[0], hi[0], lo[1], hi[1]))
        cands = candidates(tgt, subject_size(hits), pos, boxes, {h[0] for h in hits}, lo, hi, hits)
        print("clear candidates:", len(cands))
        for k, v in sorted(WHY.items(), key=lambda kv: -kv[1])[:12]:
            print("  %4d  %s" % (v, k))


def main():
    if "--why" in sys.argv:
        i = sys.argv.index("--why")
        return explain(sys.argv[i + 1], sys.argv[i + 2])
    dry = "--dry" in sys.argv
    only = [a for a in sys.argv[1:] if not a.startswith("--")]
    P.A.install_stubs()
    moved = 0
    stuck = []
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
        src_txt = open(path).read()
        glb = locale
        gm = re.search(r'path="res://assets/3d/locales/(\w+)\.glb"', src_txt)
        if gm:
            glb = gm.group(1)
        boxes = VO.boxes_for(glb)
        if not boxes or sum(1 for b in boxes if not VO.IGNORE.search(b[0])) < 20:
            continue
        name_geo = [(b[0], (b[1][0], b[1][2], -b[1][1])) for b in boxes]
        lo, hi = locale_bounds(boxes)
        fovs = M.parse_marker_fovs(path)
        changed = False
        for name, pos, rot in markers:
            cm = re.match(r"shot_(insert|closeup)_(\w+)$", name)
            if not cm:
                continue
            hits = M.matches_for(cm.group(2), name_geo)
            if not hits:
                continue
            subj = {h[0] for h in hits}
            pb = to_b(pos)
            anchor_name, tgt = M.subject_target(hits, pos)
            nearest = (anchor_name, tgt)
            inside = VO.inside_any(pb, boxes)
            occl = VO._occlusion(pb, to_b(tgt), boxes, subj)
            st = VO.frame_stats(pb, rot[0], rot[1], fovs.get(name, 42.0), boxes)
            if not inside and not occl and (st["escape"] < VO.EMPTY_FRAC or glb in VO.NO_EMPTY):
                continue
            size = subject_size(hits)
            cands = candidates(tgt, size, pos, boxes, subj, lo, hi, hits)
            if not cands:
                stuck.append((locale, name, "no clear position found"))
                continue
            # Accept only a candidate the GATE will also accept: aimed at
            # the subject as seen from there, not occluded, and not an
            # EMPTY frame (an egg on open ground can be 80% sky from
            # every ring position — then the marker is STUCK, honestly,
            # not "reframed" to the same spot every run).
            chosen = None
            for score, npos, d, el in cands[:60]:
                _an, tgt_new = M.subject_target(hits, npos)
                rx, ry = aim(npos, tgt_new)
                if VO._occlusion(to_b(npos), to_b(tgt_new), boxes, subj):
                    continue
                st2 = VO.frame_stats(to_b(npos), rx, ry, fovs.get(name, 42.0), boxes)
                if st2["escape"] >= VO.EMPTY_FRAC and glb not in VO.NO_EMPTY:
                    continue
                chosen = (npos, d, el, rx, ry)
                break
            if chosen is None:
                stuck.append((locale, name, "every clear position is an empty or occluded frame"))
                continue
            npos, d, el, rx, ry = chosen
            print("reframed  %-24s %-28s → %s  from (%.1f, %.1f, %.1f) to (%.1f, %.1f, %.1f)  %.1fm · %+.0f°" % (
                locale, name, nearest[0], pos[0], pos[1], pos[2], npos[0], npos[1], npos[2], d, el))
            if not dry:
                src_txt, ok = write_marker(src_txt, name, npos, rx, ry)
                changed = changed or ok
            moved += 1
        if changed and not dry:
            open(path, "w").write(src_txt)
    for locale, name, why in stuck:
        print("STUCK     %-24s %-28s %s" % (locale, name, why))
    print("%d marker(s) reframed · %d stuck" % (moved, len(stuck)))


if __name__ == "__main__":
    main()
