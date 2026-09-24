#!/usr/bin/env python3
"""glb_diag — what did the exporter actually write?

2026-09-24: after a Blender update on the Deck, rebuilt rooms rendered
washed toward white (pale, low-chroma — colours present but lifted).
Two causes fit and need OPPOSITE fixes: the colour layer now storing
our values as linear instead of sRGB, or the exporter no longer
converting sRGB to linear for COLOR_0. This prints, per GLB, the
exporter that wrote it (asset.generator) and the first COLOR_0 value of
a few named meshes, so the numbers can be compared with the colours the
builders asked for.

    python3 godot/tools/audit/glb_diag.py [name …]      # default: a few
Reads the GLB's JSON + BIN chunks; no dependencies.
"""
import glob, json, os, struct, sys

HERE = os.path.dirname(os.path.abspath(__file__))
GLB_DIR = os.path.normpath(os.path.join(HERE, "..", "..", "assets", "3d", "locales"))
PROBES = ("Floor", "Wall", "Counter", "Cooler", "Door", "Desk", "Table", "Bed", "Roof", "Ground")
DEFAULT = ("diner", "kwik_stop", "cedar_tower", "henderson_kitchen", "hans_bakery_back_kitchen",
           "el_rancho_taqueria", "grunion_beach", "vehicle_cab")
FMT = {5126: ("f", 4, None), 5121: ("B", 1, 255.0), 5123: ("H", 2, 65535.0)}
NCOMP = {"VEC3": 3, "VEC4": 4, "SCALAR": 1}


def load(path):
    with open(path, "rb") as f:
        data = f.read()
    off, j, b = 12, None, b""
    while off + 8 <= len(data):
        clen, ctype = struct.unpack_from("<II", data, off)
        chunk = data[off + 8: off + 8 + clen]
        if ctype == 0x4E4F534A:
            j = json.loads(chunk)
        elif ctype == 0x004E4942:
            b = chunk
        off += 8 + clen
    return j, b


def first_value(j, b, acc_i):
    acc = j["accessors"][acc_i]
    bv = j["bufferViews"][acc["bufferView"]]
    code, size, norm = FMT[acc["componentType"]]
    n = NCOMP[acc["type"]]
    start = bv.get("byteOffset", 0) + acc.get("byteOffset", 0)
    vals = struct.unpack_from("<%d%s" % (n, code), b, start)
    if norm:                      # integer colours are normalised by spec
        vals = tuple(v / norm for v in vals)
    return tuple(round(v, 4) for v in vals), acc["componentType"], acc.get("normalized", False)


def main():
    names = sys.argv[1:] or DEFAULT
    for name in names:
        path = os.path.join(GLB_DIR, name + ".glb")
        if not os.path.exists(path):
            print("%-28s (no glb)" % name)
            continue
        j, b = load(path)
        gen = j.get("asset", {}).get("generator", "?")
        print("%-28s mtime %s · %s · materials %d" % (
            name, __import__("time").strftime("%Y-%m-%d %H:%M", __import__("time").localtime(os.path.getmtime(path))),
            gen, len(j.get("materials", []))))
        shown = 0
        for node in j.get("nodes", []):
            if "mesh" not in node or shown >= 4:
                continue
            if not any(p.lower() in node.get("name", "").lower() for p in PROBES):
                continue
            prim = j["meshes"][node["mesh"]]["primitives"][0]
            ci = prim.get("attributes", {}).get("COLOR_0")
            if ci is None:
                print("    %-30s NO COLOR_0" % node["name"][:30])
            else:
                v, ct, nz = first_value(j, b, ci)
                print("    %-30s COLOR_0 %s  (componentType %d%s)" % (node["name"][:30], v, ct, " normalized" if nz else ""))
            shown += 1


if __name__ == "__main__":
    main()
