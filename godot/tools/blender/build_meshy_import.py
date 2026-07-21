#!/usr/bin/env python3
"""Normalize raw Meshy GLBs into the project's 3D pipeline conventions.

The runner (godot/tools/meshy_render.py) downloads raw GLBs to
assets/3d/meshy/<tag>/<slug>.glb. Those come in Meshy's own frame/scale and,
with the untextured T2 workflow, carry no material the game can read. This
Blender pass fixes that:

  - import the raw GLB
  - join its meshes, apply transforms
  - recenter: XY centroid to origin, min Z to 0 (stands on the ground plane)
  - scale to a target real-world height in metres (1 unit = 1 m, per the
    coordinate-frame rule — we scale to a sane size, never to compensate)
  - optional decimate for extra low-poly
  - bake a flat vertex-colour layer (the pipeline uses vertex colours as flat
    material identifiers; the T2 output is untextured, so we give it one) and a
    minimal material that reads it
  - re-export GLB (Blender Z-up -> Godot Y-up handled by the exporter) into the
    real assets/3d/<category>/ dir

Run on the Deck like the other build scripts:
    ./run_cathedral.sh build_meshy_import.py
which processes every entry in tools/blender/meshy_import.json. Or a one-off:
    blender --background --python build_meshy_import.py -- \
        --in ../../assets/3d/meshy/props/stool.glb \
        --out ../../assets/3d/props/stool.glb --height 0.6 --color 8a8878

Config (tools/blender/meshy_import.json): {"jobs": [{in,out,height,color,decimate}]}
Paths in the config are relative to this script's directory.
"""

import json
import math
import os
import sys

import bpy


HERE = os.path.dirname(os.path.abspath(__file__))
CONFIG = os.path.join(HERE, "meshy_import.json")


# ── scene helpers ────────────────────────────────────────────────────────────

def clear_scene():
    bpy.ops.object.select_all(action='SELECT')
    bpy.ops.object.delete(use_global=False)
    for block in (bpy.data.meshes, bpy.data.materials):
        for datablock in list(block):
            if datablock.users == 0:
                block.remove(datablock)


def import_glb(path):
    before = set(bpy.data.objects)
    bpy.ops.import_scene.gltf(filepath=path)
    return [o for o in bpy.data.objects if o not in before]


def mesh_objects(objs):
    return [o for o in objs if o.type == 'MESH']


def join_meshes(meshes):
    """Join all mesh objects into one; return it. Empty -> None."""
    if not meshes:
        return None
    bpy.ops.object.select_all(action='DESELECT')
    for m in meshes:
        m.select_set(True)
    bpy.context.view_layer.objects.active = meshes[0]
    if len(meshes) > 1:
        bpy.ops.object.join()
    obj = bpy.context.view_layer.objects.active
    bpy.ops.object.transform_apply(location=False, rotation=True, scale=True)
    return obj


def bounds(obj):
    """World-space (min, max) Vector3 tuples over the object's bounding box."""
    corners = [obj.matrix_world @ __import__("mathutils").Vector(c)
               for c in obj.bound_box]
    mn = [min(c[i] for c in corners) for i in range(3)]
    mx = [max(c[i] for c in corners) for i in range(3)]
    return mn, mx


def recenter_and_scale(obj, target_height):
    """XY centroid to origin, min Z to 0, then scale to target_height (Z) if > 0."""
    mn, mx = bounds(obj)
    cx = (mn[0] + mx[0]) / 2.0
    cy = (mn[1] + mx[1]) / 2.0
    obj.location.x -= cx
    obj.location.y -= cy
    obj.location.z -= mn[2]
    bpy.context.view_layer.update()
    if target_height and target_height > 0:
        mn, mx = bounds(obj)
        h = mx[2] - mn[2]
        if h > 1e-6:
            s = target_height / h
            obj.scale = (obj.scale[0] * s, obj.scale[1] * s, obj.scale[2] * s)
            bpy.context.view_layer.update()
            # re-ground after scaling
            mn, mx = bounds(obj)
            obj.location.z -= mn[2]
    bpy.ops.object.select_all(action='DESELECT')
    obj.select_set(True)
    bpy.context.view_layer.objects.active = obj
    bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)


def decimate(obj, ratio):
    if not ratio or ratio >= 1.0:
        return
    mod = obj.modifiers.new(name="meshy_decimate", type='DECIMATE')
    mod.ratio = max(0.02, float(ratio))
    bpy.ops.object.select_all(action='DESELECT')
    obj.select_set(True)
    bpy.context.view_layer.objects.active = obj
    bpy.ops.object.modifier_apply(modifier=mod.name)


def hex_to_rgb(h):
    h = (h or "8a8878").lstrip("#")
    if len(h) != 6:
        h = "8a8878"
    r, g, b = (int(h[i:i + 2], 16) / 255.0 for i in (0, 2, 4))
    return (r, g, b, 1.0)


def bake_flat_vertex_color(obj, rgba):
    """Fill a Color Attribute with one flat colour and give the object a single
    material that uses vertex colour as albedo — the pipeline's flat-identifier
    convention, applied to the otherwise-untextured T2 mesh."""
    mesh = obj.data
    # Remove any imported materials; we author one flat one.
    mesh.materials.clear()
    # Color attribute on the corner domain (what the glTF exporter reads).
    attr = mesh.color_attributes.new(name="Col", type='BYTE_COLOR', domain='CORNER')
    for i in range(len(attr.data)):
        attr.data[i].color = rgba
    mesh.color_attributes.active_color = attr

    mat = bpy.data.materials.new(name=f"{obj.name}_flat")
    mat.use_nodes = True
    bsdf = mat.node_tree.nodes.get("Principled BSDF")
    if bsdf is not None:
        bsdf.inputs["Base Color"].default_value = rgba
        if "Roughness" in bsdf.inputs:
            bsdf.inputs["Roughness"].default_value = 0.85
    mesh.materials.append(mat)


def export_glb(out_path):
    out_dir = os.path.dirname(os.path.abspath(out_path))
    os.makedirs(out_dir, exist_ok=True)
    bpy.ops.object.select_all(action='SELECT')
    base = {'filepath': out_path, 'export_format': 'GLB',
            'use_selection': False, 'export_apply': True}
    rna = bpy.ops.export_scene.gltf.get_rna_type()
    if 'export_colors' in rna.properties:
        base['export_colors'] = True
    if 'export_normals' in rna.properties:
        base['export_normals'] = True
    bpy.ops.export_scene.gltf(**base)
    if not os.path.exists(out_path):
        raise RuntimeError(f"GLB not written: {out_path}")
    print(f"[build_meshy_import] ✓ wrote {out_path} "
          f"({os.path.getsize(out_path)} bytes)")


# ── one job ──────────────────────────────────────────────────────────────────

def process(job):
    in_path = job["in"] if os.path.isabs(job["in"]) else os.path.join(HERE, job["in"])
    out_path = job["out"] if os.path.isabs(job["out"]) else os.path.join(HERE, job["out"])
    height = float(job.get("height", 0) or 0)
    ratio = float(job.get("decimate", 0) or 0)
    rgba = hex_to_rgb(job.get("color"))

    if not os.path.exists(in_path):
        print(f"[build_meshy_import] ✗ missing input: {in_path}")
        return False
    print(f"[build_meshy_import] {in_path}  ->  {out_path}  "
          f"(height={height or 'keep'} decimate={ratio or 'none'})")

    clear_scene()
    imported = import_glb(in_path)
    obj = join_meshes(mesh_objects(imported))
    if obj is None:
        print(f"[build_meshy_import] ✗ no meshes in {in_path}")
        return False
    recenter_and_scale(obj, height)
    decimate(obj, ratio)
    bake_flat_vertex_color(obj, rgba)
    export_glb(out_path)
    return True


def parse_argv():
    """One-off job from CLI args after '--', or None to use the config file."""
    argv = sys.argv
    if "--" not in argv:
        return None
    rest = argv[argv.index("--") + 1:]
    if not rest:
        return None
    job = {}
    it = iter(rest)
    for tok in it:
        if tok.startswith("--"):
            job[tok[2:]] = next(it, "")
    return job if job.get("in") and job.get("out") else None


def load_jobs():
    one = parse_argv()
    if one is not None:
        return [one]
    if os.path.exists(CONFIG):
        data = json.load(open(CONFIG))
        return data.get("jobs", []) if isinstance(data, dict) else data
    print(f"[build_meshy_import] no CLI job and no config at {CONFIG}")
    return []


def main():
    jobs = load_jobs()
    if not jobs:
        print("[build_meshy_import] nothing to do")
        return
    ok = 0
    for job in jobs:
        if process(job):
            ok += 1
    print(f"[build_meshy_import] done: {ok}/{len(jobs)} normalized")


if __name__ == "__main__":
    main()
