#!/usr/bin/env python3
"""winding_audit — closed meshes wound inside out (2026-11-01, pass 254).

The geometry gates read the builders' boxes; none of them sees a FACE. Pass
244's roofless car (a prism wound about a centre outside it), the wheels of
every car parked along X (make_cyl's Y axis wound inward) and half of every
sagging wire (make_tube's centroid guess) were all inside out: drawn by their
far inner faces and lit from behind. This reads every GLB and, for each
CLOSED mesh (every edge shared by exactly two triangles, positions welded),
takes its signed volume: inside out is negative.

Pass 254 fixed the helpers (4,309 -> 994); what is left is single faces in
non-convex shapes that _fix_winding's centre test misjudges. Each set is held
at or under winding_baseline.json; lower it with --write-baseline after a
pass removes some, and never raise a count to pass.

    python3 godot/tools/audit/winding_audit.py                    # gate
    python3 godot/tools/audit/winding_audit.py --list <set>       # the meshes
    python3 godot/tools/audit/winding_audit.py --write-baseline   # record
"""
import collections
import glob
import json
import os
import struct
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
GLB = os.path.normpath(os.path.join(HERE, "..", "..", "assets", "3d", "locales"))
BASELINE = os.path.join(HERE, "winding_baseline.json")


def _acc(j, b, bin_off, i):
    a = j["accessors"][i]
    bv = j["bufferViews"][a["bufferView"]]
    o = bin_off + bv.get("byteOffset", 0) + a.get("byteOffset", 0)
    n = {"SCALAR": 1, "VEC2": 2, "VEC3": 3, "VEC4": 4}[a["type"]]
    fmt = {5126: "f", 5123: "H", 5125: "I", 5121: "B"}[a["componentType"]]
    sz = struct.calcsize(fmt)
    st = bv.get("byteStride", sz * n)
    return [struct.unpack_from("<" + fmt * n, b, o + k * st) for k in range(a["count"])]


def inside_out(path):
    b = open(path, "rb").read()
    ln = struct.unpack("<I", b[12:16])[0]
    j = json.loads(b[20:20 + ln])
    bo = 20 + ln + 8
    out = []
    for n in j.get("nodes", []):
        if "mesh" not in n:
            continue
        for pr in j["meshes"][n["mesh"]]["primitives"]:
            if "indices" not in pr or "POSITION" not in pr.get("attributes", {}):
                continue
            P = _acc(j, b, bo, pr["attributes"]["POSITION"])
            I = [x[0] for x in _acc(j, b, bo, pr["indices"])]
            key = {}
            idx = [key.setdefault(tuple(round(c, 4) for c in P[i]), len(key)) for i in I]
            edges = collections.Counter()
            for t in range(0, len(idx) - 2, 3):
                a, c, d = idx[t:t + 3]
                edges[(a, c) if a < c else (c, a)] += 1
                edges[(c, d) if c < d else (d, c)] += 1
                edges[(d, a) if d < a else (a, d)] += 1
            if not edges or any(v != 2 for v in edges.values()):
                continue
            v = 0.0
            for t in range(0, len(I) - 2, 3):
                p, q, r = P[I[t]], P[I[t + 1]], P[I[t + 2]]
                v += (p[0] * (q[1] * r[2] - q[2] * r[1]) - p[1] * (q[0] * r[2] - q[2] * r[0])
                      + p[2] * (q[0] * r[1] - q[1] * r[0])) / 6.0
            if v < -1e-6:
                out.append(n.get("name", ""))
    return out


def main():
    args = sys.argv[1:]
    if "--list" in args:
        name = args[args.index("--list") + 1]
        for m in inside_out(os.path.join(GLB, name + ".glb")):
            print(m)
        return 0
    counts = {}
    for p in sorted(glob.glob(os.path.join(GLB, "*.glb"))):
        counts[os.path.basename(p)[:-4]] = len(inside_out(p))
    if "--write-baseline" in args:
        json.dump({"_doc": "winding_audit.py: inside-out closed meshes per set; lower only",
                   "counts": {k: v for k, v in sorted(counts.items()) if v}}, open(BASELINE, "w"), indent=1)
        print("baseline written: %d inside-out across %d set(s)" % (sum(counts.values()), len(counts)))
        return 0
    base = json.load(open(BASELINE)).get("counts", {}) if os.path.exists(BASELINE) else {}
    bad = [(k, v, base.get(k, 0)) for k, v in counts.items() if v > base.get(k, 0)]
    for k, v, b in bad:
        print("REGRESSION  %-30s %d inside-out (baseline %d) · --list %s" % (k, v, b, k))
    print("winding_audit · %d set(s) · %d inside-out closed mesh(es) · %d regression(s)" % (len(counts), sum(counts.values()), len(bad)))
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
