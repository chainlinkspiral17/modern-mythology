#!/usr/bin/env python3
"""meshy_integrity.py — is an installed model in one piece? (2026-11-10)

The user: "riverboat model looks all messed up in the renderer" and, after a
render-side fix that could not have helped, "riverboat model still broken
looking. thought this was fixed." The file itself was broken: the slim step
had cut a 106 MB original to its 10,000-triangle budget with the texture
seams released, on a mesh the glTF importer had split at every seam of a
fragment atlas — 10,000 triangles in 2,884 loose pieces, two edges in three
open. Nothing downstream can draw that as a boat.

    python3 godot/tools/meshy_integrity.py                 # every installed model
    python3 godot/tools/meshy_integrity.py a.glb b.glb     # these files
    python3 godot/tools/meshy_integrity.py --gate          # exit 1 on a shattered one

Reads the GLB directly (no Blender): welds vertices that share a position
(a texture seam is not a tear), then counts the surface's loose pieces and
its open edges. SHATTERED = more than OPEN_MAX of the edges open AND more
than one piece per PIECE_TRIS triangles — a model in shards, not one with a
few open sheets (hair cards, a cape, a single-sided sign).
`measure(path)` is what slim_model's caller uses to refuse a shattered cut.
"""
import json
import struct
import sys
from pathlib import Path

OPEN_MAX = 0.30        # share of welded edges with one face only
PIECE_TRIS = 40        # more than one loose piece per this many triangles

_FMT = {5120: "b", 5121: "B", 5122: "h", 5123: "H", 5125: "I", 5126: "f"}
_N = {"SCALAR": 1, "VEC2": 2, "VEC3": 3, "VEC4": 4}


def _read(path):
    b = Path(path).read_bytes()
    ln = struct.unpack_from("<I", b, 12)[0]
    j = json.loads(b[20:20 + ln])
    return j, b, 20 + ln + 8


def _accessor(j, b, bin_at, idx):
    a = j["accessors"][idx]
    bv = j["bufferViews"][a["bufferView"]]
    n = _N[a["type"]]
    fmt = _FMT[a["componentType"]]
    size = struct.calcsize(fmt) * n
    stride = bv.get("byteStride") or size
    at = bin_at + bv.get("byteOffset", 0) + a.get("byteOffset", 0)
    if stride == size:
        flat = struct.unpack_from("<%d%s" % (a["count"] * n, fmt), b, at)
        return [flat[i:i + n] for i in range(0, len(flat), n)] if n > 1 else list(flat)
    return [struct.unpack_from("<%d%s" % (n, fmt), b, at + i * stride) for i in range(a["count"])]


def measure(path):
    """{tris, pieces, small_pieces, edges, open_edges, open_share, shattered}
    for the whole file, welded by position. None when it cannot be read."""
    try:
        j, b, bin_at = _read(path)
    except (OSError, ValueError, struct.error):
        return None
    weld = {}
    tris = []
    for m in j.get("meshes", []):
        for pr in m.get("primitives", []):
            if pr.get("mode", 4) != 4 or "POSITION" not in pr.get("attributes", {}):
                continue
            pos = _accessor(j, b, bin_at, pr["attributes"]["POSITION"])
            ids = [weld.setdefault((round(p[0], 5), round(p[1], 5), round(p[2], 5)), len(weld)) for p in pos]
            idx = _accessor(j, b, bin_at, pr["indices"]) if "indices" in pr else list(range(len(pos)))
            for i in range(0, len(idx) - 2, 3):
                t = (ids[idx[i]], ids[idx[i + 1]], ids[idx[i + 2]])
                if t[0] != t[1] and t[1] != t[2] and t[0] != t[2]:
                    tris.append(t)
    if not tris:
        return None
    edges = {}
    parent = list(range(len(weld)))

    def find(x):
        while parent[x] != x:
            parent[x] = parent[parent[x]]
            x = parent[x]
        return x

    for a, c, d in tris:
        for u, v in ((a, c), (c, d), (d, a)):
            k = (u, v) if u < v else (v, u)
            edges[k] = edges.get(k, 0) + 1
            ru, rv = find(u), find(v)
            if ru != rv:
                parent[ru] = rv
    sizes = {}
    for a, _, _ in tris:
        r = find(a)
        sizes[r] = sizes.get(r, 0) + 1
    open_edges = sum(1 for n in edges.values() if n == 1)
    share = open_edges / float(len(edges))
    pieces = len(sizes)
    return {
        "tris": len(tris), "pieces": pieces,
        "small_pieces": sum(1 for n in sizes.values() if n <= 8),
        "edges": len(edges), "open_edges": open_edges, "open_share": round(share, 3),
        "shattered": share > OPEN_MAX and pieces * PIECE_TRIS > len(tris),
    }


def main(argv):
    gate = "--gate" in argv
    files = [Path(a) for a in argv if not a.startswith("--")]
    if not files:
        root = Path(__file__).resolve().parents[1] / "assets"
        for d in ("3d/heroes", "3d/demons", "3d/props"):
            files += sorted(p for p in (root / d).glob("*.glb"))
    bad = 0
    for f in files:
        m = measure(f)
        if m is None:
            print(f"  ?  {f.name}: cannot be read")
            continue
        if m["shattered"]:
            bad += 1
            print(f"  ✗  {f.name}: SHATTERED — {m['tris']} triangles in {m['pieces']} loose pieces "
                  f"({m['small_pieces']} of 8 triangles or fewer), {round(100 * m['open_share'])} % of edges open. "
                  f"Re-cut it: python3 godot/tools/meshy_pipeline.py slim {f.stem} --force")
        elif len(argv) and not gate or len(files) <= 12:
            print(f"  ok {f.name}: {m['tris']} triangles, {m['pieces']} piece(s), {round(100 * m['open_share'])} % of edges open")
    print(f"meshy_integrity · {len(files)} model(s) · {bad} shattered")
    return 1 if (gate and bad) else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
