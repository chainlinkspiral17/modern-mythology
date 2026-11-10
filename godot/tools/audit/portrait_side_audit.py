#!/usr/bin/env python3
"""portrait_side_audit.py — which flank a lone figure takes, read off the set (2026-11-10).

The user: "Text box still obstructing art, so maybe direct and move Frasier to
the left." A lone figure over a 3D set stood RIGHT in every view, so the text
(opposite it, in the lower third) sat on the picture's lower LEFT whatever was
there. `resources/vn/portrait_sides.json` directs it per view, by hand. This
tool is ADVICE for that hand: it reads the set's boxes and says where a lone
figure would cover less. It writes nothing — its reading could not be checked
against pictures for most of the cast (their models are not in a checkout),
and four hundred unverified re-stagings are not direction.

For each view — its establishing frame and every shot marker that is not an
insert (on an insert the cast steps back) — rays are cast through the two
places the text can sit and the two places the figure can stand:

    text  left   x  4 – 57 % of the 16:9 frame, y 68 – 97 %
    text  right  x 43 – 96 %,                   y 68 – 97 %
    figure left  x  5 – 39 %,                   y 22 – 100 %
    figure right x 61 – 95 %,                   y 22 – 100 %

A ray is BUSY when the first thing it meets is not the room itself (floor,
wall, ceiling, door, sky). A picture the roster hangs there (an art row) or a
hero prop standing there counts on top. The cost of an arrangement is what
the text covers plus FIGURE_W of what the figure covers; the figure stands
LEFT only when that is cheaper than standing right by more than MARGIN (right
is the default the scenes were staged with).

    python3 tools/audit/portrait_side_audit.py cathedral_interior # these views, with the numbers (~15 s a view)
    python3 tools/audit/portrait_side_audit.py                    # every view (over an hour)
    python3 tools/audit/portrait_side_audit.py --check            # the JSON names only real views

It reads boxes, not pictures: it cannot tell a dull crate from a model city.
The hand-written "presets" are for what it gets wrong.
"""
import json
import math
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import vantage_obstruction_audit as VO  # noqa: E402
import wide_frame_audit as WF  # noqa: E402

GODOT = os.path.normpath(os.path.join(HERE, "..", ".."))
OUT = os.path.join(GODOT, "resources", "vn", "portrait_sides.json")
ROSTER = os.path.join(GODOT, "tools", "meshy_roster.json")
ASPECT = 16.0 / 9.0
TEXT_L = (-0.92, 0.14, 0.36, 0.94)      # nx0, nx1, ny0, ny1 (x right, y DOWN, the frame is -1..1)
TEXT_R = (-0.14, 0.92, 0.36, 0.94)
FIG_L = (-0.90, -0.22, -0.56, 1.0)
FIG_R = (0.22, 0.90, -0.56, 1.0)
FIGURE_W = 0.6
ART_W = 0.5
MARGIN = 0.10
ROOM = re.compile(r"(wall|floor|ceil|ground|baseboard|skirting|cornice|trim|beam|column|pillar|shell|partition|"
                  r"backdrop|door|jamb|sill|threshold|stair|step|slab|roof|soffit|fascia|siding|road|asphalt|"
                  r"sidewalk|curb|lawn|grass|terrain|sky|horizon|void|template_)", re.I)


def _basis(pitch, yaw):
    f = VO.ray_dir(pitch, yaw, 0.0, 0.0)
    r = (math.cos(yaw), math.sin(yaw), 0.0)
    u = (r[1] * f[2] - r[2] * f[1], r[2] * f[0] - r[0] * f[2], r[0] * f[1] - r[1] * f[0])
    return f, r, u


def _dir(f, r, u, x, y):
    d = (f[0] + r[0] * x + u[0] * y, f[1] + r[1] * x + u[1] * y, f[2] + r[2] * x + u[2] * y)
    n = math.sqrt(d[0] ** 2 + d[1] ** 2 + d[2] ** 2)
    return (d[0] / n, d[1] / n, d[2] / n)


def zone_busy(o, pitch, yaw, fov, boxes, zone, cols=8, rows=5):
    tv = math.tan(math.radians(fov) / 2.0)
    th = tv * ASPECT
    f, r, u = _basis(pitch, yaw)
    busy = n = 0
    x0, x1, y0, y1 = zone
    for i in range(cols):
        for j in range(rows):
            nx = x0 + (x1 - x0) * (i + 0.5) / cols
            ny = y0 + (y1 - y0) * (j + 0.5) / rows
            t, who = VO.cast(o, _dir(f, r, u, nx * th, -ny * tv), boxes, ignore=VO.SKY)
            n += 1
            if who and not ROOM.search(who):
                busy += 1
    return busy / float(n)


def screen_of(o, pitch, yaw, fov, pt):
    """(nx, ny) of a point of the set in this view, or None when behind the camera."""
    tv = math.tan(math.radians(fov) / 2.0)
    th = tv * ASPECT
    f, r, u = _basis(pitch, yaw)
    v = (pt[0] - o[0], pt[1] - o[1], pt[2] - o[2])
    z = v[0] * f[0] + v[1] * f[1] + v[2] * f[2]
    if z < 0.3:
        return None
    return ((v[0] * r[0] + v[1] * r[1] + v[2] * r[2]) / z / th, -(v[0] * u[0] + v[1] * u[1] + v[2] * u[2]) / z / tv)


def _in(zone, p):
    return p is not None and zone[0] <= p[0] <= zone[1] and zone[2] <= p[1] <= zone[3]


def art_points(scene_name, view, roster):
    """What the picture is ABOUT, as points in the set: the roster's art rows
    for this set and the hero props its scene places (blender frame)."""
    pts = []
    for e in roster.get("entries", []):
        if e.get("kind") != "art":
            continue
        for row in e.get("apply", []) or []:
            if row.get("locale") == scene_name and isinstance(row.get("center"), list) and len(row["center"]) == 3:
                pts.append(tuple(float(x) for x in row["center"]))
    for sub in ("locales", ""):
        p = os.path.join(WF.SCENES, sub, scene_name + ".tscn")
        if os.path.exists(p):
            src = open(p, encoding="utf-8").read()
            for m in re.finditer(r'\[node name="([^"]+)"[^\n]*\n((?:[^\[][^\n]*\n)*)', src):
                name, body = m.group(1), m.group(2)
                if "assets/3d/props/" not in body:
                    continue
                tag = name.partition("__")[2]
                if tag and view not in tag.split("__"):
                    continue
                pm = re.search(r"position = Vector3\(([^)]+)\)", body)
                tm = re.search(r"transform = Transform3D\(([^)]+)\)", body)
                g = None
                if pm:
                    g = [float(x) for x in pm.group(1).split(",")]
                elif tm:
                    g = [float(x) for x in tm.group(1).split(",")][9:12]
                if g:
                    pts.append((g[0], -g[2], g[1]))
            break
    return pts


def costs(o, pitch, yaw, fov, boxes, pts):
    """(cost with the figure LEFT, cost with the figure RIGHT)"""
    tl = zone_busy(o, pitch, yaw, fov, boxes, TEXT_L)
    tr = zone_busy(o, pitch, yaw, fov, boxes, TEXT_R)
    fl = zone_busy(o, pitch, yaw, fov, boxes, FIG_L, 5, 7)
    fr = zone_busy(o, pitch, yaw, fov, boxes, FIG_R, 5, 7)
    for pt in pts:
        s = screen_of(o, pitch, yaw, fov, pt)
        if s is None or abs(s[0]) > 1.0 or abs(s[1]) > 1.0:
            continue
        tl += ART_W if _in(TEXT_L, s) else 0.0
        tr += ART_W if _in(TEXT_R, s) else 0.0
        fl += ART_W if _in(FIG_L, s) else 0.0
        fr += ART_W if _in(FIG_R, s) else 0.0
    return tr + FIGURE_W * fl, tl + FIGURE_W * fr


def read_view(pid, loc, og, rot, fov, src, roster):
    try:
        boxes = VO.boxes_for(loc)
    except Exception:
        boxes = None
    if not boxes:
        return None
    sol = [(n, c, h) for n, c, h in boxes if VO._in_view(n, pid) and VO._not_stripped(n, pid) and not VO.PASSABLE.search(n)]
    scene_name = WF.scene_of(pid, src)
    pts = art_points(scene_name, pid, roster)
    o = (og[0], -og[2], og[1])
    cl, cr = costs(o, rot[0], rot[1], fov, sol, pts)
    tot_l, tot_r, w = cl * 2.0, cr * 2.0, 2.0
    for name, mo, mp, my, mf in WF.markers_of(scene_name, pid):
        if "insert" in name:
            continue
        ml, mr = costs(mo, mp, my, mf, sol, pts)
        tot_l += ml
        tot_r += mr
        w += 1.0
    return tot_l / w, tot_r / w


def main():
    want = [a for a in sys.argv[1:] if not a.startswith("--")]
    src = open(VO.V.GD).read()
    VO.PRESET_IDS.update(p[0] for p in VO.presets())
    VO.STRIPS.update(VO._strips())
    data = json.load(open(OUT, encoding="utf-8")) if os.path.exists(OUT) else {}
    if "--check" in sys.argv:
        ids = {p[0] for p in VO.presets()}
        hand = data.get("presets") or {}
        bad = [k for k in hand if k not in ids] + [k for k, v in hand.items() if v not in ("left", "right")]
        if data.get("default", "right") not in ("left", "right"):
            bad.append("default")
        for k in bad:
            print("UNKNOWN  portrait_sides.json: %s is not a view (or its side is not left / right)" % k)
        print("portrait_side_audit --check · %d view(s) directed by hand · %d unknown" % (len(hand), len(bad)))
        return 1 if bad else 0
    roster = json.load(open(ROSTER, encoding="utf-8"))
    left, n = {}, 0
    for pid, loc, og, rot, fov in VO.presets():
        if want and pid not in want:
            continue
        got = read_view(pid, loc, og, rot, fov, src, roster)
        if got is None:
            continue
        n += 1
        cl, cr = got
        side = "left" if cl + MARGIN < cr else "right"
        if side == "left":
            left[pid] = "left"
        if want:
            print("%-5s  %-34s figure left costs %.2f · figure right costs %.2f" % (side.upper(), pid, cl, cr))
    hand = data.get("presets") or {}
    for pid in sorted(left):
        if not want and pid not in hand:
            print("ADVICE  %-34s a lone figure would cover less standing LEFT" % pid)
    print("portrait_side_audit · %d view(s) read · LEFT advised in %d · %d directed by hand" % (n, len(left), len(hand)))
    return 0


if __name__ == "__main__":
    sys.exit(main())
