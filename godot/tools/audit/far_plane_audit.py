#!/usr/bin/env python3
"""far_plane_audit — open views whose horizon the camera cannot reach (2026-10-31).

The VN camera's far plane is 200 m unless a preset sets "far" (Background3D's
Camera3D; pass 195's lesson). Pass 247 found the Small Wood hills invisible
behind it, and a scan found 78 more views across the volumes whose named far
scenery (hills, tree lines, the sea horizon and cloud decks, mesas, pole and
road runs) stood wholly past their far plane, inside the lens's cone: the
desert mesas, the beach's cloud decks, Briar Falls' woods. Each now sets
`far`; this keeps a new open view from shipping cut.

For every preset a chapter uses: each GLB mesh whose NAME reads as far
scenery (LAND), whose nearest point is beyond the preset's far plane, within
~60 deg of the lens's axis and large enough to see (> 2% of its distance)
is a cut. Any cut fails.

Multi-room sets are skipped: several rooms share one GLB 300 m apart, and
past 200 m from one room is the next room, not a horizon.

    python3 godot/tools/audit/far_plane_audit.py        # report + exit 1 on any cut
"""
import glob
import json
import math
import os
import re
import struct
import sys

ROOT = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".."))
GD = os.path.join(ROOT, "scripts", "vn", "Background3D.gd")
DEFAULT_FAR = 200.0
LAND = re.compile(r"Far|Treeline|Cloud|Sea_Horizon|Mesa|Headland|Ridge|Hill|Wood|Bluff|Windbreak|"
                  r"Pole|Wire|Road|Surf|Canopy|Scrub|Trees", re.I)
MULTI_ROOM = {"vol3_rooms", "vol4_story_rooms", "pasadena_1945"}


def _ev(x):
    x = x.strip()
    m = re.match(r"deg_to_rad\((-?[\d.]+)\)", x)
    if m:
        return math.radians(float(m.group(1)))
    try:
        return float(eval(x.replace("PI", "math.pi").replace("TAU", "2*math.pi"), {"math": math}))
    except Exception:
        return 0.0


def presets():
    src = open(GD, encoding="utf-8").read()
    out = {}
    for m in re.finditer(r'^\t"(\w+)": \{\s*\n(.*?)\n\t\},?$', src, re.M | re.S):
        body = m.group(2)
        sc = re.search(r'"scene": "res://scenes/locales/(\w+)\.tscn"', body)
        co = re.search(r'"camera_origin": Vector3\(([^)]*)\)', body)
        cr = re.search(r'"camera_rotation": Vector3\(([^,]*),\s*([^,]*),', body)
        far = re.search(r'"far": ([\d.]+)', body)
        if not (sc and co and cr):
            continue
        out[m.group(1)] = (sc.group(1), [float(v) for v in co.group(1).split(",")], _ev(cr.group(2)),
                           float(far.group(1)) if far else DEFAULT_FAR)
    return out


def used_presets():
    bp = json.load(open(os.path.join(ROOT, "resources", "vn", "bg_places.json")))
    places = bp.get("places", bp)
    used = set()
    for f in glob.glob(os.path.join(ROOT, "resources", "scenes", "*", "*.json")):
        try:
            nodes = json.load(open(f, encoding="utf-8")).get("nodes", [])
        except Exception:
            continue
        for n in nodes:
            if not isinstance(n, dict) or n.get("t") != "bg":
                continue
            s = str(n.get("src") or "")
            if s.startswith("3d:"):
                used.add(s[3:])
                continue
            e = places.get(os.path.splitext(os.path.basename(s))[0])
            t = (e.get("to") if isinstance(e, dict) else e) or ""
            if isinstance(t, str) and t.startswith("3d:"):
                used.add(t[3:])
    return used


_CACHE = {}


def meshes(scene):
    if scene in _CACHE:
        return _CACHE[scene]
    p = os.path.join(ROOT, "assets", "3d", "locales", scene + ".glb")
    out = []
    if os.path.exists(p):
        b = open(p, "rb").read()
        ln = struct.unpack("<I", b[12:16])[0]
        j = json.loads(b[20:20 + ln])
        for n in j.get("nodes", []):
            if "mesh" in n and not n.get("translation"):
                a = j["accessors"][j["meshes"][n["mesh"]]["primitives"][0]["attributes"]["POSITION"]]
                out.append((n.get("name", ""), a["min"], a["max"]))
    _CACHE[scene] = out
    return out


def main():
    P = presets()
    cuts = []
    missing = set()
    for pre in sorted(used_presets()):
        if pre not in P:
            continue
        sc, (x, y, z), yaw, far = P[pre]
        if sc in MULTI_ROOM:
            continue
        ms = meshes(sc)
        if not ms:
            missing.add(sc)
            continue
        fx, fz = -math.sin(yaw), -math.cos(yaw)
        hit = []
        for nm, mn, mx in ms:
            if not LAND.search(nm):
                continue
            q = [min(max(v, a), b) for v, a, b in zip((x, y, z), mn, mx)]
            d = math.dist(q, (x, y, z))
            if d <= far:
                continue
            c = [(a + b) / 2.0 for a, b in zip(mn, mx)]
            v = [c[0] - x, c[1] - y, c[2] - z]
            L = math.hypot(*v) or 1.0
            if (v[0] * fx + v[2] * fz) / L < 0.5:
                continue
            if max(b - a for a, b in zip(mn, mx)) < d * 0.02:
                continue
            hit.append((round(d), nm))
        if hit:
            hit.sort()
            cuts.append((pre, sc, far, hit))
    for pre, sc, far, hit in cuts:
        print("CUT  %-30s %-26s far %5.0f · %d piece(s) wholly past it, nearest %s at %d m"
              % (pre, sc, far, len(hit), hit[0][1], hit[0][0]))
    if missing:
        print("note: no GLB for %s (build the sets to audit them)" % ", ".join(sorted(missing)))
    print("far_plane_audit · %d view(s) with a horizon past the far plane" % len(cuts))
    return 1 if cuts else 0


if __name__ == "__main__":
    sys.exit(main())
