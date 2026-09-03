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
DELIBERATE = {"vehicle_cab", "vehicle_cab_rear", "lake_palestine_dock"}
NEAR_M, NEAR_FRAC = 1.0, 0.30
WALL_M, WALL_FRAC = 2.6, 0.45
ASPECT = 16.0 / 9.0
IGNORE = re.compile(r"(ground|sky|horizon|far|band|floor|ceil|void|sea\b|swamp_floor|lake_water|valley_floor|plinth$|template_(land|sea)|road_asphalt|asphalt$)", re.I)


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


def boxes_for(locale):
    if locale in _cache:
        return _cache[locale]
    for cand in (os.path.join(P.A.LOCALES, "build_%s.py" % locale),
                 os.path.join(BLENDER_ALT, "build_%s.py" % locale)):
        if os.path.exists(cand):
            bx, _err = P.record_builder(cand)
            _cache[locale] = bx or []
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


def cast(origin_b, d, boxes):
    """Nearest slab hit along d from origin_b. Returns (t, name)."""
    best, who = None, None
    ox, oy, oz = origin_b
    for name, c, h in boxes:
        if IGNORE.search(name):
            continue
        tmin, tmax = 0.0, 1e9
        ok = True
        for o, dd, cc, hh in ((ox, d[0], c[0], h[0]), (oy, d[1], c[1], h[1]), (oz, d[2], c[2], h[2])):
            lo, hi = cc - hh, cc + hh
            if abs(dd) < 1e-9:
                if o < lo or o > hi:
                    ok = False
                    break
                continue
            t1, t2 = (lo - o) / dd, (hi - o) / dd
            if t1 > t2:
                t1, t2 = t2, t1
            tmin, tmax = max(tmin, t1), min(tmax, t2)
            if tmin > tmax:
                ok = False
                break
        if ok and tmin > 0.02 and (best is None or tmin < best):
            best, who = tmin, name
    return best, who


def inside_any(pt, boxes):
    for name, c, h in boxes:
        if IGNORE.search(name):
            continue
        if all(abs(pt[i] - c[i]) < h[i] for i in range(3)):
            return name
    return None


def frame_stats(origin_b, pitch, yaw, fov, boxes):
    vf = math.radians(fov)
    hf = 2.0 * math.atan(math.tan(vf / 2.0) * ASPECT)
    hits = []
    for r in range(ROWS):
        dv = (r - (ROWS - 1) / 2.0) * (vf / 2.5)
        for c in range(COLS):
            dh = (c - (COLS - 1) / 2.0) * (hf / (COLS - 1))
            t, who = cast(origin_b, ray_dir(pitch, yaw, dh, dv), boxes)
            hits.append((t if t is not None else 200.0, who))
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
                escape=1.0 - len(hit) / n,
                depth_hit=(sum(min(t, 9.0) for t in hit) / (9.0 * len(hit))) if hit else 0.0)


def verdict(st):
    why = []
    if st["near"] >= NEAR_FRAC:
        why.append("%.0f%% of frame within %.1fm" % (st["near"] * 100, NEAR_M))
    if st["wall"] and st["wall_frac"] >= WALL_FRAC and st["wall_med"] < WALL_M:
        why.append("%s fills %.0f%% at %.1fm" % (st["wall"], st["wall_frac"] * 100, st["wall_med"]))
    return why


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
    flagged = []
    n = 0
    for pid, locale, o_g, rot, fov in presets():
        if only and pid not in only and locale not in only:
            continue
        boxes = boxes_for(locale)
        if not boxes:
            continue
        n += 1
        o_b = (o_g[0], -o_g[2], o_g[1])
        inside = inside_any(o_b, boxes)
        st = frame_stats(o_b, rot[0], rot[1], fov, boxes)
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
