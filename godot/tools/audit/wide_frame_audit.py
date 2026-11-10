#!/usr/bin/env python3
"""wide_frame_audit.py — which views may show MORE on a wide screen (2026-11-09).

On a screen wider than 16:9 a view holds its composed width by default
(Background3D._fit_native): the first wide frames widened the lens instead and
the user saw past the Hendersons' garage to its outer wall and a bare horizon
("it also shows the garage is a side-set, and breaks the illusion"). Holding
costs the top and bottom 13 % of the frame. A view whose set really does run
past the wide frame can have the panorama: this decides which.

For each view (and each shot marker that plays in it) rays are cast through
the 16:9 frame and through the two side BANDS a 21:9 screen adds. A ray that
points below the horizon and meets nothing has run off the set's ground — the
VOID. A ray above the horizon that meets nothing is open SKY. A view may
expand when its bands open no void and no more sky than its composed frame
already has, for the establishing frame and for every marker:

    void(bands) <= void(frame) + 0.02      sky(bands) <= sky(frame) + 0.10

It cannot see a band that HITS something ugly (another room's back wall);
that is still a read on the Deck. Result: resources/vn/wide_views.json
(`expand`: the views that pass), read by Background3D; a preset's own
`"wide"` key wins.

    python3 tools/audit/wide_frame_audit.py                # report
    python3 tools/audit/wide_frame_audit.py --write        # write wide_views.json
    python3 tools/audit/wide_frame_audit.py henderson_garage kwik_stop_interior
    python3 tools/audit/wide_frame_audit.py --check        # the JSON names only real views
    python3 tools/audit/wide_frame_audit.py --gate         # every view the JSON clears still passes (suite)
"""
import json
import math
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import vantage_obstruction_audit as VO  # noqa: E402

GODOT = os.path.normpath(os.path.join(HERE, "..", ".."))
OUT = os.path.join(GODOT, "resources", "vn", "wide_views.json")
SCENES = os.path.join(GODOT, "scenes")
WIDE = 3440.0 / 1440.0
VOID_TOL = 0.02
SKY_TOL = 0.10
FAR = 900.0
MARKER = re.compile(r'\[node name="(shot_[^"]+)" type="Marker3D"[^\n]*\n((?:[^\[][^\n]*\n)*)')


def solids(boxes, view):
    out = []
    for name, c, h in boxes:
        if not VO._in_view(name, view) or not VO._not_stripped(name, view):
            continue
        # a flat slab 16 m2 or more is GROUND whatever it is called: the
        # obstruction audit's PASSABLE list names streets and roads (nothing
        # stands on a lens's way there), and a ray that landed on the street
        # across from a front window was being counted as void (pass 330)
        if VO.PASSABLE.search(name) and not (h[2] <= 0.08 and h[0] * h[1] >= 4.0):
            continue
        out.append((c[0] - h[0], c[1] - h[1], c[2] - h[2], c[0] + h[0], c[1] + h[1], c[2] + h[2]))
    return out


def hit(o, d, sol):
    ox, oy, oz = o
    dx, dy, dz = d
    ix = 1.0 / dx if abs(dx) > 1e-9 else None
    iy = 1.0 / dy if abs(dy) > 1e-9 else None
    iz = 1.0 / dz if abs(dz) > 1e-9 else None
    for x0, y0, z0, x1, y1, z1 in sol:
        tmin, tmax = 0.05, FAR
        if ix is None:
            if ox < x0 or ox > x1:
                continue
        else:
            a, b = (x0 - ox) * ix, (x1 - ox) * ix
            if a > b:
                a, b = b, a
            if a > tmin:
                tmin = a
            if b < tmax:
                tmax = b
            if tmin > tmax:
                continue
        if iy is None:
            if oy < y0 or oy > y1:
                continue
        else:
            a, b = (y0 - oy) * iy, (y1 - oy) * iy
            if a > b:
                a, b = b, a
            if a > tmin:
                tmin = a
            if b < tmax:
                tmax = b
            if tmin > tmax:
                continue
        if iz is None:
            if oz < z0 or oz > z1:
                continue
        else:
            a, b = (z0 - oz) * iz, (z1 - oz) * iz
            if a > b:
                a, b = b, a
            if a > tmin:
                tmin = a
            if b < tmax:
                tmax = b
            if tmin > tmax:
                continue
        return True
    return False


def band_stats(o, pitch, yaw, fov, sol, cols_c, rows, cols_b):
    """(void_frame, sky_frame, void_bands, sky_bands)"""
    tv = math.tan(math.radians(fov) / 2.0)
    t16, tw = tv * 16.0 / 9.0, tv * WIDE
    us_c = [(-t16 + 2.0 * t16 * i / (cols_c - 1)) for i in range(cols_c)]
    us_b = []
    for i in range(cols_b):
        u = t16 * 1.03 + (tw - t16 * 1.03) * (i + 0.5) / cols_b
        us_b += [-u, u]
    vs = [(-tv * 0.92 + 2.0 * tv * 0.92 * j / (rows - 1)) for j in range(rows)]

    def tally(us):
        down = down_miss = up = up_miss = 0
        for u in us:
            for v in vs:
                d = VO.ray_dir(pitch, yaw, math.atan(u), math.atan(v))
                h = hit(o, d, sol)
                if d[2] < -0.02:
                    down += 1
                    down_miss += 0 if h else 1
                else:
                    up += 1
                    up_miss += 0 if h else 1
        return (down_miss / down if down else 0.0, up_miss / up if up else 0.0)

    vc, sc = tally(us_c)
    vb, sb = tally(us_b)
    return vc, sc, vb, sb


def markers_of(locale_scene, view):
    """the shot markers that play in this view: (name, origin_b, pitch, yaw, fov)"""
    out = {}
    for sub in ("locales", ""):
        p = os.path.join(SCENES, sub, locale_scene + ".tscn")
        if os.path.exists(p):
            break
    else:
        return []
    src = open(p, encoding="utf-8").read()
    for m in MARKER.finditer(src):
        name, body = m.group(1), m.group(2)
        base, _, tag = name.partition("__")
        if tag and tag != view:
            continue
        pos = re.search(r"position = Vector3\(([^)]+)\)", body)
        tr = re.search(r"transform = Transform3D\(([^)]+)\)", body)
        rot = re.search(r"rotation = Vector3\(([^)]+)\)", body)
        fv = re.search(r"metadata/fov = ([\d.]+)", body)
        if pos:
            g = [float(x) for x in pos.group(1).split(",")]
        elif tr:
            g = [float(x) for x in tr.group(1).split(",")][9:12]
        else:
            continue
        r = [float(x) for x in rot.group(1).split(",")] if rot else [0.0, 0.0, 0.0]
        rec = (name, (g[0], -g[2], g[1]), r[0], r[1], float(fv.group(1)) if fv else 42.0)
        if tag or base not in out:            # the view's own marker wins over the shared one
            out[base] = rec
    return list(out.values())


def scene_of(pid, src):
    m = re.search(r'"%s":\s*\{.*?"scene":\s*"res://scenes/(?:locales/)?(\w+)\.tscn"' % re.escape(pid), src, re.S)
    return m.group(1) if m else ""


def passes(st):
    vc, sc, vb, sb = st
    return vb <= vc + VOID_TOL and sb <= sc + SKY_TOL


def main():
    want = [a for a in sys.argv[1:] if not a.startswith("--")]
    src = open(VO.V.GD).read()
    VO.PRESET_IDS.update(p[0] for p in VO.presets())
    VO.STRIPS.update(VO._strips())
    if "--check" in sys.argv:
        ids = {p[0] for p in VO.presets()}
        data = json.load(open(OUT, encoding="utf-8")) if os.path.exists(OUT) else {"expand": []}
        bad = [x for x in data.get("expand", []) if x not in ids]
        for x in bad:
            print("UNKNOWN  wide_views.json names a view that does not exist: %s" % x)
        print("wide_frame_audit --check · %d view(s) expand · %d unknown" % (len(data.get("expand", [])), len(bad)))
        return 1 if bad else 0
    gate = "--gate" in sys.argv
    listed = set()
    if gate:
        if os.path.exists(OUT):
            listed = set(json.load(open(OUT, encoding="utf-8")).get("expand", []))
    expand, hold = [], []
    for pid, loc, og, rot, fov in VO.presets():
        if want and pid not in want:
            continue
        if gate and pid not in listed:
            continue                      # the gate re-reads only the views the list clears
        try:
            boxes = VO.boxes_for(loc)
        except Exception:
            boxes = None
        if not boxes:
            hold.append((pid, "no recorded geometry"))
            continue
        sol = solids(boxes, pid)
        o = (og[0], -og[2], og[1])
        st = band_stats(o, rot[0], rot[1], fov, sol, 13, 9, 4)
        why = ""
        if not passes(st):
            why = "the frame: void %.0f%%→%.0f%%, sky %.0f%%→%.0f%%" % (st[0] * 100, st[2] * 100, st[1] * 100, st[3] * 100)
        else:
            for name, mo, mp, my, mf in markers_of(scene_of(pid, src), pid):
                ms = band_stats(mo, mp, my, mf, sol, 11, 9, 4)
                if not passes(ms):
                    why = "%s: void %.0f%%→%.0f%%, sky %.0f%%→%.0f%%" % (name, ms[0] * 100, ms[2] * 100, ms[1] * 100, ms[3] * 100)
                    break
        if why:
            hold.append((pid, why))
            if want:
                print("HOLD    %-34s %s" % (pid, why))
        else:
            expand.append(pid)
            if want:
                print("EXPAND  %-34s void %.0f%%→%.0f%%, sky %.0f%%→%.0f%%" % (pid, st[0] * 100, st[2] * 100, st[1] * 100, st[3] * 100))
    if gate:
        for pid, why in hold:
            print("STALE   %-34s is cleared in wide_views.json and no longer passes — %s" % (pid, why))
        print("wide_frame_audit --gate · %d cleared view(s) re-read · %d no longer pass%s" % (
            len(listed), len(hold), "  (re-run with --write and look at them wide)" if hold else ""))
        return 1 if hold else 0
    print("wide_frame_audit · %d view(s) may expand · %d hold their composed width" % (len(expand), len(hold)))
    if "--write" in sys.argv and not want:
        json.dump({"_comment": "Written by tools/audit/wide_frame_audit.py --write. The views that may show more to either "
                               "side on a screen wider than 16:9 (their side bands open no void and no more sky than the "
                               "composed frame, for the establishing frame and every shot marker). Every other view holds "
                               "its composed width. A preset's own \"wide\" key in Background3D.gd wins.",
                   "expand": sorted(expand),
                   "hold": {p: w for p, w in sorted(hold)}},
                  open(OUT, "w", encoding="utf-8"), indent=1, ensure_ascii=False)
        print("wrote %s" % os.path.relpath(OUT, GODOT))
    return 0


if __name__ == "__main__":
    sys.exit(main())
