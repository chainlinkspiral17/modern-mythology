#!/usr/bin/env python3
"""glb_color_check — did the vertex colours make it into the GLB?

2026-09-24: the 09-24 contact sheet rendered ~30 rooms WHITE. Every GLB
rebuilt that day had lost its vertex colours: the glTF exporter on the
Deck no longer had `export_colors`, and its replacement's default
('MATERIAL') exports colours only for meshes whose material reads them —
ours have no material. Godot then drew every mesh with a white albedo.
The builders now set export_vertex_color='ACTIVE'
(_props.geometry.gltf_color_kwargs); this reads the built files to prove
it.

A GLB FAILS when fewer than half of its mesh primitives carry a COLOR_0
attribute and it has no materials (a builder that colours through real
materials — roberts_house — is fine without COLOR_0).

    python3 godot/tools/audit/glb_color_check.py            # every locale GLB
    python3 godot/tools/audit/glb_color_check.py --names    # just the failing names
Nonzero exit when any GLB fails. Reads only the GLB's JSON chunk.
"""
import glob, json, os, struct, sys

HERE = os.path.dirname(os.path.abspath(__file__))
GLB_DIR = os.path.normpath(os.path.join(HERE, "..", "..", "assets", "3d", "locales"))


def gltf_json(path):
    with open(path, "rb") as f:
        head = f.read(12)
        if len(head) < 12 or head[:4] != b"glTF":
            return None
        clen, ctype = struct.unpack("<II", f.read(8))
        if ctype != 0x4E4F534A:      # 'JSON'
            return None
        return json.loads(f.read(clen))


def check(path):
    j = gltf_json(path)
    if j is None:
        return "unreadable", 0, 0
    prims = [p for m in j.get("meshes", []) for p in m.get("primitives", [])]
    colored = sum(1 for p in prims if "COLOR_0" in p.get("attributes", {}))
    if not prims:
        return "no meshes", 0, 0
    if colored * 2 < len(prims) and not j.get("materials"):
        return "NO COLOUR", colored, len(prims)
    return "ok", colored, len(prims)


def main():
    names_only = "--names" in sys.argv
    bad = []
    files = sorted(glob.glob(os.path.join(GLB_DIR, "*.glb")))
    for f in files:
        verdict, c, n = check(f)
        name = os.path.basename(f)[:-4]
        if verdict not in ("ok",):
            bad.append(name)
            if not names_only:
                print("%-10s %-34s %d/%d primitives coloured" % (verdict, name, c, n))
    if names_only:
        for n in bad:
            print(n)
        return 1 if bad else 0
    print("glb_color_check · %d GLB(s) · %d without vertex colours" % (len(files), len(bad)))
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
