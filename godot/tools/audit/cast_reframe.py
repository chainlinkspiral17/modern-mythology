#!/usr/bin/env python3
import sys, math, re, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import prop_overlap_audit as P, vantage_obstruction_audit as VO, marker_aim_audit as M, marker_reframe as R
P.A.install_stubs()
"""cast_reframe.py — re-pose a CAST closeup that stares into a wall (2026-09-10).

A closeup of a person has no object to aim at, so marker_reframe skips
it and the gate judges it by fill: five stood 0.1–0.4 m from a cubicle
wall or booth back, or framed a bare wall. This treats the marker's
current look-point 1.6 m along its forward as the person's spot, runs
marker_reframe's ring search around it (1.0–2.2 m, ≤ 30° elevation,
eye ≥ 0.35 m) and accepts the first pose the gate's own fill verdict
passes. Position-form markers get a rotation line.

    python3 godot/tools/audit/cast_reframe.py [--dry] <locale>:<marker>…
"""
jobs = [tuple(a.split(":", 1)) for a in sys.argv[1:] if ":" in a]
dry = "--dry" in sys.argv
for locale, name in jobs:
    path = os.path.join(M.LOCALES_TSCN, locale + ".tscn")
    src = open(path).read()
    markers = {m[0]: m for m in M.parse_markers(path)}
    _n, pos, rot = markers[name]
    fovs = M.parse_marker_fovs(path); fov = fovs.get(name, 42.0)
    boxes = VO.boxes_for(locale)
    lo, hi = R.locale_bounds(boxes)
    # the person's spot: 1.6 m along the marker's forward, at chest height
    fwd = (-math.sin(rot[1]) * math.cos(rot[0]), math.sin(rot[0]), -math.cos(rot[1]) * math.cos(rot[0]))
    tgt = (pos[0] + fwd[0] * 1.6, 1.25, pos[2] + fwd[2] * 1.6)
    hits = [("_person", tgt)]
    cands = R.candidates(tgt, 0.6, pos, boxes, set(), lo, hi, hits)
    chosen = None
    for score, npos, d, el in cands:
        if d < 1.0 or d > 2.2 or el > 30.0: continue
        rx, ry = R.aim(npos, tgt)
        st = VO.frame_stats(R.to_b(npos), rx, ry, fov, boxes)
        if VO.verdict(st): continue
        if VO.inside_any(R.to_b(npos), boxes): continue
        chosen = (npos, rx, ry, d, el, st); break
    if not chosen:
        print("STUCK", locale, name); continue
    npos, rx, ry, d, el, st = chosen
    print("%-22s %-24s (%.1f, %.1f, %.1f) → (%.1f, %.1f, %.1f) %.1fm %+.0f° median %.1f distinct %d" % (locale, name, *pos, *npos, d, el, st["median"], st["distinct"]))
    if not dry:
        src2, ok = R.write_marker(src, name, npos, rx, ry)
        if ok: open(path, "w").write(src2)
