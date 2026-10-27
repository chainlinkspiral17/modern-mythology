"""slim_model.py — a Meshy / Hero Studio GLB cut to a game budget (2026-10-16).

The user: "do a quick assessment how well game is handling graphical load …
how much it can be optimized/expanded", then "Go ahead". tools/PerfProbe.gd
found the hero models are the install-size and memory risk: the ten on hand
median 40 MB and 643k triangles (elicia_temple 1.13M), each with two 4096²
and two 2048² JPEGs — ~180 more at that rate is ~7 GB.

    blender -b --python godot/tools/blender/slim_model.py -- IN.glb OUT.glb \
        [--tris 120000] [--tex 2048] [--tex-small 1024] [--quality 88]

Run by `meshy_pipeline.py slim` (which keeps the untouched original under
heroes/_full/). Steps:
  1. import the GLB;
  2. every mesh over its share of --tris gets a COLLAPSE decimate (UVs and
     the normal map carry the surface detail; the silhouette keeps its
     shape at ~120k for a full figure). Texture seams are locked, less and
     less until the budget fits (2026-10-27: a fully locked seam set let the
     riverboat through at ~24x its budget);
  3. images: the base colour and the normal map at most --tex px, every
     other map (metal-roughness, emission) at most --tex-small;
  4. export GLB with JPEG images at --quality.
Prints one JSON line: {"tris_in", "tris_out", "bytes_in", "bytes_out", ...}.
Works in Blender 4.2 (tested as the bpy module) and the Deck's 5.x.
"""
import json
import os
import sys

import bpy


def _args():
    argv = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else sys.argv[1:]
    opts = {"tris": 120000, "tex": 2048, "tex_small": 1024, "quality": 88, "lock": 1}
    pos = []
    i = 0
    while i < len(argv):
        a = argv[i]
        if a.startswith("--"):
            opts[a[2:].replace("-", "_")] = int(argv[i + 1])
            i += 2
        else:
            pos.append(a)
            i += 1
    if len(pos) != 2:
        sys.exit("usage: slim_model.py -- IN.glb OUT.glb [--tris N] [--tex PX] [--tex-small PX] [--quality Q]")
    return pos[0], pos[1], opts


def _tris(obj):
    return sum(len(p.vertices) - 2 for p in obj.data.polygons)


def _seam_group(ob):
    """Put every texture-seam vertex of `ob` in vertex group SlimSeams.
    Returns how many."""
    import bmesh
    me = ob.data
    bm = bmesh.new()
    bm.from_mesh(me)
    uv = bm.loops.layers.uv.active
    seam = set()
    for e in bm.edges:
        loops = list(e.link_loops)
        if len(loops) != 2:
            seam.update(v.index for v in e.verts)
            continue
        if uv is None:
            continue
        l1, l2 = loops
        # the two faces run the shared edge in opposite directions
        if ((l1[uv].uv - l2.link_loop_next[uv].uv).length > 1e-5
                or (l1.link_loop_next[uv].uv - l2[uv].uv).length > 1e-5):
            seam.update(v.index for v in e.verts)
    bm.free()
    if not seam:
        return 0
    vg = ob.vertex_groups.new(name="SlimSeams")
    vg.add(sorted(seam), 1.0, "REPLACE")
    return len(seam)


def _image_roles():
    """image name → 'big' (base colour, normal map) or 'small' (the rest)."""
    roles = {}
    for mat in bpy.data.materials:
        if not mat.use_nodes:
            continue
        for node in mat.node_tree.nodes:
            if node.type != "TEX_IMAGE" or node.image is None:
                continue
            big = False
            for out in node.outputs:
                for link in out.links:
                    to = link.to_node
                    if to.type == "NORMAL_MAP":
                        big = True
                    elif to.type == "BSDF_PRINCIPLED" and link.to_socket.name == "Base Color":
                        big = True
            if big or roles.get(node.image.name) != "big":
                roles[node.image.name] = "big" if big else "small"
    return roles


def main():
    src, dst, o = _args()
    bpy.ops.wm.read_factory_settings(use_empty=True)
    bpy.ops.import_scene.gltf(filepath=src)
    meshes = [ob for ob in bpy.context.scene.objects if ob.type == "MESH"]
    tris_in = sum(_tris(ob) for ob in meshes)
    passes = []
    if tris_in > o["tris"]:
        # (2026-10-27) the seam lock gives way when it must: a Meshy model cut
        # into thousands of tiny UV islands is mostly seam vertices, and with
        # every one locked the decimate barely runs — the riverboat installed
        # at 12 MB, ~24x its budget; a test hero asked for 30k came out at 56k.
        # Pass 1 locks the seams (a face keeps them whenever the budget can
        # afford it); when that misses the budget by more than 10 %, pass 2
        # starts again from the ORIGINAL mesh with the seams free and always
        # lands on the target. (Weights between 1000 and 1 made no difference,
        # tested: the lock is all or nothing.) "seams_released" in the SLIM
        # line names the models to look over for dark specks at UV seams.
        originals = {ob.name: ob.data.copy() for ob in meshes}
        dg = bpy.context.evaluated_depsgraph_get()
        # --lock 0 (`meshy_pipeline.py slim --free-seams`): straight to the free
        # cut — to compare a model the locked cut may have distorted
        for factor in ((1000.0, 0.0) if o["lock"] else (0.0,)):
            ratio = o["tris"] / float(tris_in)
            for ob in meshes:
                old = ob.data
                ob.data = originals[ob.name].copy()
                if old.users == 0:
                    bpy.data.meshes.remove(old)
                for vg in list(ob.vertex_groups):
                    ob.vertex_groups.remove(vg)
                n_seam = _seam_group(ob) if factor > 0 else 0
                mod = ob.modifiers.new("Slim", "DECIMATE")
                mod.decimate_type = "COLLAPSE"
                mod.ratio = ratio
                mod.use_collapse_triangulate = True
                if n_seam:
                    mod.vertex_group = "SlimSeams"
                    mod.invert_vertex_group = True
                    mod.vertex_group_factor = factor
                dg.update()
                ev = ob.evaluated_get(dg)
                new = bpy.data.meshes.new_from_object(ev)
                old = ob.data
                ob.modifiers.clear()
                ob.data = new
                if old.users == 0:
                    bpy.data.meshes.remove(old)
            got = sum(_tris(ob) for ob in meshes)
            passes.append([factor, got])
            if got <= o["tris"] * 1.10:
                break
        for ob in meshes:
            for vg in list(ob.vertex_groups):
                ob.vertex_groups.remove(vg)
    tris_out = sum(_tris(ob) for ob in meshes)
    roles = _image_roles()
    scaled = []
    for img in bpy.data.images:
        if img.size[0] == 0:
            continue
        cap = o["tex"] if roles.get(img.name, "small") == "big" else o["tex_small"]
        w, h = img.size
        if max(w, h) > cap:
            s = cap / float(max(w, h))
            img.scale(max(1, int(w * s)), max(1, int(h * s)))
            scaled.append([img.name, [w, h], list(img.size)])
    os.makedirs(os.path.dirname(os.path.abspath(dst)), exist_ok=True)
    bpy.ops.export_scene.gltf(filepath=dst, export_format="GLB", export_image_format="JPEG",
                              export_jpeg_quality=o["quality"], export_apply=True,
                              export_animations=False, export_yup=True)
    print("SLIM " + json.dumps({
        "tris_in": tris_in, "tris_out": tris_out,
        "bytes_in": os.path.getsize(src), "bytes_out": os.path.getsize(dst),
        "images": scaled, "passes": passes,
        "seams_released": bool(passes and passes[-1][0] == 0.0)}), flush=True)


main()
# a clean exit now: the bpy module (used to test this outside Blender)
# segfaults in its own teardown after the file is written
sys.stdout.flush()
os._exit(0)
