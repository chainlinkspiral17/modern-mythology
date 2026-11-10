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
  2. every mesh over its share of --tris gets a COLLAPSE decimate with its
     texture seams LOCKED (UVs and the normal map carry the surface detail;
     the silhouette keeps its shape at ~120k for a full figure);
  2b. A MODEL THAT WILL NOT CUT KEEPS ITS SHAPE (2026-11-10). When the
     locked cut misses the budget the model stays as the locked cut left
     it — whole, heavier than its class — and "over_budget" says so. From
     2026-10-27 the fallback released the seams and collapsed anyway; on a
     model whose atlas is thousands of tiny islands that tore every island
     from its neighbours: the riverboat went from a working 12 MB model to
     10,000 triangles in 2,884 loose pieces (the user: "It used to be a
     functional model." / "Still looks exploded"). A model is worth more
     than its budget line.
  2c. THE REBUILD, only when asked (--lock 0, `slim --rebuild`) or when a
     cut comes out in shards: welded, fused into one skin when it is a pile
     of small parts, cut to the budget, NEW texture coordinates, colour /
     metal-roughness / a normal map BAKED from the untouched original. It
     does not look like the original up close — the user, of a first try:
     "That wasnt what the model looked like." — so it is never the default;
  3. images: the base colour and the normal map at most --tex px, every
     other map (metal-roughness, emission) at most --tex-small;
  4. export GLB with JPEG images at --quality.
Prints one JSON line: {"tris_in", "tris_out", "bytes_in", "bytes_out",
"rebuilt", "integrity": {...}} — `integrity` is meshy_integrity.measure()
of the file written; the caller refuses a shattered one.
Works in Blender 4.2 (tested as the bpy module) and the Deck's 5.x.
"""
import json
import math
import os
import sys

import bpy

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
try:
    import meshy_integrity
except ImportError:          # run from a copy outside the tools folder
    meshy_integrity = None


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


def _pieces(me):
    """Loose pieces and the open-edge share of a mesh datablock."""
    import bmesh
    bm = bmesh.new()
    bm.from_mesh(me)
    seen = set()
    pieces = 0
    for v in bm.verts:
        if v.index in seen:
            continue
        pieces += 1
        stack = [v]
        seen.add(v.index)
        while stack:
            x = stack.pop()
            for e in x.link_edges:
                y = e.other_vert(x)
                if y.index not in seen:
                    seen.add(y.index)
                    stack.append(y)
    n_edges = max(len(bm.edges), 1)
    open_share = sum(1 for e in bm.edges if len(e.link_faces) == 1) / float(n_edges)
    bm.free()
    return pieces, open_share


def _shattered(meshes):
    """The cut came out in shards (meshy_integrity's rule, on welded data)."""
    import bmesh
    for ob in meshes:
        me = ob.data.copy()
        bm = bmesh.new()
        bm.from_mesh(me)
        bmesh.ops.remove_doubles(bm, verts=bm.verts, dist=max(max(ob.dimensions), 1e-6) * 1e-5)
        bm.to_mesh(me)
        bm.free()
        pieces, open_share = _pieces(me)
        tris = sum(len(p.vertices) - 2 for p in me.polygons)
        bpy.data.meshes.remove(me)
        if open_share > 0.30 and pieces * 40 > tris:
            return True
    return False


def _apply_modifier(ob, mod_name):
    dg = bpy.context.evaluated_depsgraph_get()
    dg.update()
    new = bpy.data.meshes.new_from_object(ob.evaluated_get(dg))
    old = ob.data
    ob.modifiers.clear()
    ob.data = new
    if old.users == 0:
        bpy.data.meshes.remove(old)


def _only(ob):
    for x in bpy.context.scene.objects:
        x.select_set(False)
    ob.select_set(True)
    bpy.context.view_layer.objects.active = ob


def _surface_source(mat, channel):
    """What a material shows on `channel`: ("socket", output socket) when a
    texture / node drives it, else ("value", colour). channel: base | rough |
    metal | emit."""
    bsdf = next((n for n in mat.node_tree.nodes if n.type == "BSDF_PRINCIPLED"), None)
    if bsdf is None:
        return ("value", (0.8, 0.8, 0.8, 1.0) if channel == "base" else (0.5, 0.5, 0.5, 1.0))
    names = {"base": ("Base Color",), "rough": ("Roughness",), "metal": ("Metallic",),
             "emit": ("Emission Color", "Emission")}[channel]
    inp = next((bsdf.inputs[n] for n in names if n in bsdf.inputs), None)
    if inp is None:
        return ("value", (0.0, 0.0, 0.0, 1.0))
    if inp.is_linked:
        return ("socket", inp.links[0].from_socket)
    v = inp.default_value
    try:
        return ("value", (v[0], v[1], v[2], 1.0))
    except TypeError:
        return ("value", (float(v), float(v), float(v), 1.0))


def _has_texture(high, channel):
    return any(m is not None and m.use_nodes and _surface_source(m, channel)[0] == "socket"
               for m in high.data.materials)


def _bake_emit(high, low, node, what):
    """Bake one surface channel of `high` into the image of `node` on `low`,
    as plain emitted colour (no lighting). what: base | orm | emit."""
    undo = []
    for mat in high.data.materials:
        if mat is None or not mat.use_nodes:
            continue
        nt = mat.node_tree
        out = next((n for n in nt.nodes if n.type == "OUTPUT_MATERIAL" and n.is_active_output), None)
        if out is None:
            continue
        was = out.inputs["Surface"].links[0].from_socket if out.inputs["Surface"].is_linked else None
        em = nt.nodes.new("ShaderNodeEmission")
        made = [em]
        if what == "orm":
            comb = nt.nodes.new("ShaderNodeCombineColor")
            made.append(comb)
            comb.inputs[0].default_value = 1.0            # R: occlusion, none
            for slot, ch in ((1, "rough"), (2, "metal")):
                kind, src = _surface_source(mat, ch)
                if kind == "socket":
                    nt.links.new(src, comb.inputs[slot])
                else:
                    comb.inputs[slot].default_value = src[0]
            nt.links.new(comb.outputs[0], em.inputs["Color"])
        else:
            kind, src = _surface_source(mat, "base" if what == "base" else "emit")
            if kind == "socket":
                nt.links.new(src, em.inputs["Color"])
            else:
                em.inputs["Color"].default_value = src
        nt.links.new(em.outputs[0], out.inputs["Surface"])
        undo.append((nt, out, was, made))
    low.data.materials[0].node_tree.nodes.active = node
    for x in bpy.context.scene.objects:
        x.select_set(False)
    high.select_set(True)
    low.select_set(True)
    bpy.context.view_layer.objects.active = low
    bpy.ops.object.bake(type="EMIT")
    for nt, out, was, made in undo:
        if was is not None:
            nt.links.new(was, out.inputs["Surface"])
        for n in made:
            nt.nodes.remove(n)


def _see_through(ob):
    """A mesh with glass in it (spectacle lenses, a bottle): a bake would
    paint it solid, so the rebuild leaves it as the locked cut made it."""
    for mat in ob.data.materials:
        if mat is None or not mat.use_nodes:
            continue
        bsdf = next((n for n in mat.node_tree.nodes if n.type == "BSDF_PRINCIPLED"), None)
        if bsdf is None or "Alpha" not in bsdf.inputs:
            continue
        a = bsdf.inputs["Alpha"]
        if a.is_linked or a.default_value < 0.999:
            return True
    return False


def _fill_unbaked(img, flat):
    """Texels no bake ray reached (a face the unwrap gave no area, a ray
    that found nothing) stay black, and a black speck on a silver spoon is
    what the eye goes to. They take `flat`, or the mean of what was baked.
    Returns the share of the image that was baked."""
    import numpy as np
    w, h = img.size
    px = np.empty(w * h * 4, dtype=np.float32)
    img.pixels.foreach_get(px)
    px = px.reshape(-1, 4)
    done = px[:, 3] > 0.5
    share = float(done.mean())
    if 0.0 < share < 1.0:
        fill = np.array(flat, dtype=np.float32) if flat is not None else px[done, :3].mean(axis=0)
        px[~done, :3] = fill
    px[:, 3] = 1.0
    img.pixels.foreach_set(px.ravel())
    img.update()
    return round(share, 3)


def _rebuild(meshes, o):
    """Welded, fused if it is a pile of parts, cut to the budget, unwrapped
    afresh and baked from the original. Returns (low object, notes)."""
    import bmesh
    sc = bpy.context.scene
    for ob in meshes:
        _only(ob)
        if ob.parent is not None:
            bpy.ops.object.parent_clear(type="CLEAR_KEEP_TRANSFORM")
    for x in sc.objects:
        x.select_set(False)
    for ob in meshes:
        ob.select_set(True)
    bpy.context.view_layer.objects.active = meshes[0]
    if len(meshes) > 1:
        bpy.ops.object.join()
    high = bpy.context.view_layer.objects.active
    bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)
    dim = max(max(high.dimensions), 1e-6)
    bm = bmesh.new()
    bm.from_mesh(high.data)
    bmesh.ops.remove_doubles(bm, verts=bm.verts, dist=dim * 1e-5)     # a texture seam is not a tear
    bm.to_mesh(high.data)
    bm.free()
    pieces, open_share = _pieces(high.data)
    notes = {"pieces_in": pieces, "open_in": round(open_share, 3)}

    low = high.copy()
    low.data = high.data.copy()
    low.name = high.name + "_slim"
    sc.collection.objects.link(low)
    low.data.materials.clear()
    for vg in list(low.vertex_groups):
        low.vertex_groups.remove(vg)
    # A pile of small parts (a sculpture of spoons) cut piece by piece leaves
    # each one a sliver: fuse it into one skin first. One or a few solid
    # bodies are cut as they are — their thin sheets and open edges survive.
    fuse = pieces * 40 > o["tris"] or open_share > 0.30
    notes["fused"] = fuse
    if fuse:
        mod = low.modifiers.new("Fuse", "REMESH")
        mod.mode = "VOXEL"
        mod.voxel_size = dim / 190.0
        mod.adaptivity = 0.0
        mod.use_smooth_shade = True
        _apply_modifier(low, "Fuse")
    n = _tris(low)
    if n > o["tris"]:
        mod = low.modifiers.new("Slim", "DECIMATE")
        mod.decimate_type = "COLLAPSE"
        mod.ratio = o["tris"] / float(n)
        mod.use_collapse_triangulate = True
        _apply_modifier(low, "Slim")
    for p in low.data.polygons:
        p.use_smooth = True
    while low.data.uv_layers:
        low.data.uv_layers.remove(low.data.uv_layers[0])
    low.data.uv_layers.new(name="UVMap")
    _only(low)
    bpy.ops.object.mode_set(mode="EDIT")
    bpy.ops.mesh.select_all(action="SELECT")
    bpy.ops.uv.smart_project(angle_limit=math.radians(66.0), island_margin=0.012)
    bpy.ops.object.mode_set(mode="OBJECT")

    mat = bpy.data.materials.new("Slim")
    mat.use_nodes = True
    nt = mat.node_tree
    bsdf = next(n for n in nt.nodes if n.type == "BSDF_PRINCIPLED")
    low.data.materials.append(mat)

    def image_node(name, side, data):
        # alpha marks what the bake reached (see _fill_unbaked)
        img = bpy.data.images.new(name, side, side, alpha=True)
        img.generated_color = (0.0, 0.0, 0.0, 0.0)
        if data:
            img.colorspace_settings.name = "Non-Color"
        node = nt.nodes.new("ShaderNodeTexImage")
        node.image = img
        return node

    sc.render.engine = "CYCLES"
    sc.cycles.device = "CPU"
    sc.cycles.samples = 4
    bk = sc.render.bake
    bk.use_selected_to_active = True
    bk.use_cage = False
    bk.cage_extrusion = dim * 0.02
    bk.max_ray_distance = dim * 0.06
    bk.margin = 8
    bk.use_clear = True

    base = image_node("Slim_Base", o["tex"], False)
    _bake_emit(high, low, base, "base")
    notes["baked_share"] = _fill_unbaked(base.image, None)
    nt.links.new(base.outputs["Color"], bsdf.inputs["Base Color"])
    baked = ["base"]
    if _has_texture(high, "rough") or _has_texture(high, "metal"):
        orm = image_node("Slim_ORM", o["tex_small"], True)
        _bake_emit(high, low, orm, "orm")
        _fill_unbaked(orm.image, None)
        sep = nt.nodes.new("ShaderNodeSeparateColor")
        nt.links.new(orm.outputs["Color"], sep.inputs[0])
        nt.links.new(sep.outputs[1], bsdf.inputs["Roughness"])
        nt.links.new(sep.outputs[2], bsdf.inputs["Metallic"])
        baked.append("orm")
    else:
        for ch, name in (("rough", "Roughness"), ("metal", "Metallic")):
            src = next((_surface_source(m, ch) for m in high.data.materials if m is not None and m.use_nodes), None)
            if src is not None and src[0] == "value":
                bsdf.inputs[name].default_value = src[1][0]
    # the normal map carries what the cut took out of the surface
    nrm = image_node("Slim_Normal", o["tex"], True)
    nt.nodes.active = nrm
    for x in sc.objects:
        x.select_set(False)
    high.select_set(True)
    low.select_set(True)
    bpy.context.view_layer.objects.active = low
    bpy.ops.object.bake(type="NORMAL", normal_space="TANGENT")
    _fill_unbaked(nrm.image, (0.5, 0.5, 1.0))
    nmap = nt.nodes.new("ShaderNodeNormalMap")
    nt.links.new(nrm.outputs["Color"], nmap.inputs["Color"])
    nt.links.new(nmap.outputs["Normal"], bsdf.inputs["Normal"])
    baked.append("normal")
    notes["baked"] = baked

    old_mats = [m for m in high.data.materials if m is not None]
    hd = high.data
    bpy.data.objects.remove(high)
    if hd.users == 0:
        bpy.data.meshes.remove(hd)
    for m in old_mats:
        if m.users == 0:
            bpy.data.materials.remove(m)
    for img in list(bpy.data.images):
        if img.users == 0:
            bpy.data.images.remove(img)
    return low, notes


def main():
    src, dst, o = _args()
    bpy.ops.wm.read_factory_settings(use_empty=True)
    bpy.ops.import_scene.gltf(filepath=src)
    meshes = [ob for ob in bpy.context.scene.objects if ob.type == "MESH"]
    tris_in = sum(_tris(ob) for ob in meshes)
    passes = []
    rebuilt = None
    over_budget = False
    if tris_in > o["tris"]:
        # (2026-10-27) the seam lock gives way when it must: a Meshy model cut
        # into thousands of tiny UV islands is mostly seam vertices, and with
        # every one locked the decimate barely runs — the riverboat installed
        # at 12 MB, ~24x its budget; a test hero asked for 30k came out at 56k.
        # Pass 1 locks the seams (a face keeps them whenever the budget can
        # afford it). When that misses the budget by more than 10 % — or the
        # cut comes out in shards — THE REBUILD starts again from the
        # ORIGINAL mesh (see the docstring). (2026-10-27 → 2026-11-10: the
        # fallback used to be the same collapse with the seams free; it
        # always landed on the target and tore fragment-atlas models apart.)
        originals = {ob.name: ob.data.copy() for ob in meshes}
        dg = bpy.context.evaluated_depsgraph_get()
        # --lock 0 (`meshy_pipeline.py slim --rebuild`): straight to the
        # rebuild — for a model the locked cut distorted
        for factor in ((1000.0,) if o["lock"] else ()):
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
        in_budget = bool(passes) and passes[-1][1] <= o["tris"] * 1.10
        shards = bool(passes) and _shattered(meshes)
        if passes and not in_budget and not shards:
            # it keeps its shape; a fragment atlas shrunk to a prop's map
            # size is a smear, so its maps keep a size that holds the islands
            over_budget = True
            o["tex"] = max(o["tex"], 2048)
            o["tex_small"] = max(o["tex_small"], 1024)
        if not passes or shards:
            glass = [ob for ob in meshes if _see_through(ob)]
            solid = [ob for ob in meshes if ob not in glass]
            if solid:
                for ob in solid:       # back to the untouched original
                    old = ob.data
                    ob.data = originals[ob.name].copy()
                    if old.users == 0:
                        bpy.data.meshes.remove(old)
                share = dict(o)
                share["tris"] = max(o["tris"] - sum(_tris(ob) for ob in glass), o["tris"] // 2)
                low, rebuilt = _rebuild(solid, share)
                rebuilt["kept_as_cut"] = [ob.name for ob in glass]
                meshes = [low] + glass
                passes.append(["rebuild", sum(_tris(ob) for ob in meshes)])
        for ob in meshes:
            for vg in list(ob.vertex_groups):
                ob.vertex_groups.remove(vg)
        for me in originals.values():
            if me.users == 0:
                bpy.data.meshes.remove(me)
        if rebuilt is not None:
            # the original's materials and 4096 px maps are done with: gone
            # before the resize pass below spends its time on them
            for m in list(bpy.data.materials):
                if m.users == 0:
                    bpy.data.materials.remove(m)
            for img in list(bpy.data.images):
                if img.users == 0:
                    bpy.data.images.remove(img)
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
    integrity = meshy_integrity.measure(dst) if meshy_integrity is not None else None
    print("SLIM " + json.dumps({
        "tris_in": tris_in, "tris_out": tris_out,
        "bytes_in": os.path.getsize(src), "bytes_out": os.path.getsize(dst),
        "images": scaled, "passes": passes,
        "rebuilt": rebuilt, "integrity": integrity, "over_budget": over_budget, "budget": o["tris"],
        "seams_released": False}), flush=True)


main()
# a clean exit now: the bpy module (used to test this outside Blender)
# segfaults in its own teardown after the file is written
sys.stdout.flush()
os._exit(0)
