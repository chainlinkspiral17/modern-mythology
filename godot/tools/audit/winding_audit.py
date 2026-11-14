#!/usr/bin/env python3
"""winding_audit — closed meshes wound inside out (2026-11-01, pass 254).

The geometry gates read the builders' boxes; none of them sees a FACE. Pass
244's roofless car (a prism wound about a centre outside it), the wheels of
every car parked along X (make_cyl's Y axis wound inward) and half of every
sagging wire (make_tube's centroid guess) were all inside out: drawn by their
far inner faces and lit from behind. This reads every GLB and, for each
CLOSED mesh (every edge shared by exactly two triangles, positions welded),
takes its signed volume: inside out is negative.

Pass 254 fixed the helpers (4,309 -> 994). Pass 379 turned the rest outward
at the export (_props.geometry.turn_closed_meshes_outward) and made this read
per shell, with a second count for shells whose faces disagree. Each set is
held at or under winding_baseline.json; lower it with --write-baseline after
a pass removes some, and never raise a count to pass. A new inward part means
a builder exports without that step, or a GLB that was not rebuilt.

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


def scan(path):
    """(inside_out, mixed) for one GLB: the nodes with a closed shell wound
    INWARD, and the nodes with a closed shell whose faces DISAGREE (some
    wound inward: a turned leg with every other ring missing from outside).

    (pass 379) Read per SHELL, not per mesh: positions are welded, faces
    that share a welded vertex are one shell, and a shell is closed when
    every edge of it is shared by exactly two triangles. Before this the
    whole mesh had to be closed and its total volume negative, which missed
    an inward shell joined to a larger outward one, any shell joined to an
    open sheet, every cone (its collapsed tip left degenerate triangles
    that read as open edges) and every shell with only SOME faces inward."""
    b = open(path, "rb").read()
    ln = struct.unpack("<I", b[12:16])[0]
    j = json.loads(b[20:20 + ln])
    bo = 20 + ln + 8
    inward, mixed = [], []
    for n in j.get("nodes", []):
        if "mesh" not in n:
            continue
        n_in = n_mix = False
        for pr in j["meshes"][n["mesh"]]["primitives"]:
            if "indices" not in pr or "POSITION" not in pr.get("attributes", {}):
                continue
            P = _acc(j, b, bo, pr["attributes"]["POSITION"])
            I = [x[0] for x in _acc(j, b, bo, pr["indices"])]
            key, co = {}, []
            idx = []
            for i in I:
                k = tuple(round(c, 4) for c in P[i])
                w = key.get(k)
                if w is None:
                    w = key[k] = len(co)
                    co.append(P[i])
                idx.append(w)
            parent = list(range(len(co)))

            def find(x):
                while parent[x] != x:
                    parent[x] = parent[parent[x]]
                    x = parent[x]
                return x
            tris = []
            for t in range(0, len(idx) - 2, 3):
                a, c, d = idx[t:t + 3]
                if a == c or c == d or d == a:
                    continue            # a collapsed corner: no face
                tris.append((a, c, d))
                ra, rc, rd = find(a), find(c), find(d)
                parent[rc] = ra
                parent[rd] = ra
            shells = {}
            for tr in tris:
                shells.setdefault(find(tr[0]), []).append(tr)
            for sh in shells.values():
                if len(sh) < 4:
                    continue
                und = collections.Counter()
                dirs = collections.Counter()
                for a, c, d in sh:
                    for u, v in ((a, c), (c, d), (d, a)):
                        und[(u, v) if u < v else (v, u)] += 1
                        dirs[(u, v)] += 1
                if any(v != 2 for v in und.values()):
                    continue            # open, or three faces on an edge
                if any(v != 1 for v in dirs.values()):
                    n_mix = True
                    continue
                v = 0.0
                for a, c, d in sh:
                    p, q, r = co[a], co[c], co[d]
                    v += (p[0] * (q[1] * r[2] - q[2] * r[1]) - p[1] * (q[0] * r[2] - q[2] * r[0])
                          + p[2] * (q[0] * r[1] - q[1] * r[0])) / 6.0
                if v < -1e-8:
                    n_in = True
        if n_in:
            inward.append(n.get("name", ""))
        if n_mix:
            mixed.append(n.get("name", ""))
    return inward, mixed


def inside_out(path):
    return scan(path)[0]


def main():
    args = sys.argv[1:]
    if "--list" in args:
        name = args[args.index("--list") + 1]
        inward, mixed = scan(os.path.join(GLB, name + ".glb"))
        for m in inward:
            print(m)
        for m in mixed:
            print(m + "   (some faces inward)")
        return 0
    counts, mixed = {}, {}
    for p in sorted(glob.glob(os.path.join(GLB, "*.glb"))):
        a, m = scan(p)
        counts[os.path.basename(p)[:-4]] = len(a)
        mixed[os.path.basename(p)[:-4]] = len(m)
    if "--write-baseline" in args:
        json.dump({"_doc": "winding_audit.py: per set, closed shells wound inward (counts) and closed "
                           "shells with some faces inward (mixed); lower only",
                   "counts": {k: v for k, v in sorted(counts.items()) if v},
                   "mixed": {k: v for k, v in sorted(mixed.items()) if v}}, open(BASELINE, "w"), indent=1)
        print("baseline written: %d inside-out, %d mixed across %d set(s)"
              % (sum(counts.values()), sum(mixed.values()), len(counts)))
        return 0
    doc = json.load(open(BASELINE)) if os.path.exists(BASELINE) else {}
    base, mbase = doc.get("counts", {}), doc.get("mixed", {})
    bad = [(k, v, base.get(k, 0), "inside-out") for k, v in counts.items() if v > base.get(k, 0)]
    bad += [(k, v, mbase.get(k, 0), "with some faces inward") for k, v in mixed.items() if v > mbase.get(k, 0)]
    for k, v, b, what in bad:
        print("REGRESSION  %-30s %d %s (baseline %d) · --list %s" % (k, v, what, b, k))
    print("winding_audit · %d set(s) · %d inside-out closed shell(s) · %d with some faces inward · %d regression(s)"
          % (len(counts), sum(counts.values()), sum(mixed.values()), len(bad)))
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
