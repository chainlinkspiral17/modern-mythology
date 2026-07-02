"""
import_planar_human_base.py
══════════════════════════════════════════════════════════════════
Bring dacancino's PLANAR HUMAN BASE RIGS (CC-BY-4.0) into the
project as our canonical character base. This is the first step
of the "use the reference as starting sculpt" pipeline (decided
2026-06-16, see lore/_CHARACTER_MODELING_NOTES.md).

What this does:
  1. Imports lore/refs/humans/planar_human_base_rigs/scene.gltf.
  2. Splits the male and female meshes into separate exports.
  3. Renames objects + materials to project-consistent names.
  4. Re-exports each figure as its own GLB into the character
     asset folder.
  5. Saves the .blend workspace file for sculpt-mode iteration.

What this does NOT do:
  · No sculpt edits — we ship the reference topology unchanged
    in this first pass. Body-type variants come in a separate
    script (build_human_variants.py — future work).
  · No retargeting — the reference's 34-bone skeleton already
    matches the skeleton we designed for our pipeline.

Attribution:
    "PLANAR HUMAN BASE RIGS" by dacancino on Sketchfab,
    CC-BY-4.0. See lore/refs/CREDITS.md.

Run (on the Deck):
    cd godot/tools/blender && ./run_cathedral.sh import_planar_human_base.py

Outputs:
    godot/assets/3d/characters/human_male_base.glb
    godot/assets/3d/characters/human_female_base.glb
    godot/assets/3d/characters/human_base_workspace.blend
"""
import os
import sys
import bpy

_HERE = os.path.dirname(os.path.abspath(__file__))
_REPO_ROOT = os.path.normpath(os.path.join(_HERE, "..", "..", "..", ".."))

REF_GLTF = os.path.join(_REPO_ROOT, "lore", "refs", "humans",
                         "planar_human_base_rigs", "scene.gltf")
OUTPUT_DIR = os.path.normpath(
    os.path.join(_HERE, "..", "..", "..", "assets", "3d", "characters"))
WORKSPACE_BLEND = os.path.join(OUTPUT_DIR, "human_base_workspace.blend")


def _clear_scene():
    bpy.ops.object.select_all(action='SELECT')
    bpy.ops.object.delete()
    for block in list(bpy.data.meshes):
        bpy.data.meshes.remove(block)
    for block in list(bpy.data.armatures):
        bpy.data.armatures.remove(block)
    for block in list(bpy.data.materials):
        bpy.data.materials.remove(block)


def _import_reference():
    print(f"[import_planar_human_base] loading {REF_GLTF}")
    if not os.path.exists(REF_GLTF):
        raise RuntimeError(
            f"Reference glTF missing: {REF_GLTF}\n"
            "Expected at lore/refs/humans/planar_human_base_rigs/scene.gltf")
    bpy.ops.import_scene.gltf(filepath=REF_GLTF)
    # After import the scene contains nested empties + 2 skinned
    # meshes + 1 light. Promote what we care about.
    print(f"[import_planar_human_base] scene now has "
          f"{len(bpy.data.objects)} objects")


def _classify_figures():
    """The reference has the male figure around X=0 and the female
    around X=3 (in reference units). Identify them by mesh bbox X.
    Returns dict {'male': mesh_obj, 'female': mesh_obj}."""
    mesh_objs = [o for o in bpy.data.objects
                 if o.type == 'MESH' and len(o.data.vertices) > 100]
    classified = {}
    for o in mesh_objs:
        # Compute centroid X in world space
        verts_world = [o.matrix_world @ v.co for v in o.data.vertices]
        xs = [v.x for v in verts_world]
        centroid_x = sum(xs) / len(xs)
        if centroid_x < 1.5:
            classified['male'] = o
        else:
            classified['female'] = o
    print(f"[import_planar_human_base] classified: "
          f"{list(classified.keys())}")
    return classified


def _normalize_names(figures):
    """Rename meshes + materials + armatures to project-consistent
    names so downstream scripts can find them deterministically."""
    for gender, mesh_obj in figures.items():
        mesh_obj.name = f"human_{gender}_mesh"
        if mesh_obj.data:
            mesh_obj.data.name = f"human_{gender}_mesh_data"
        # Find the armature this mesh is parented to
        if mesh_obj.parent and mesh_obj.parent.type == 'ARMATURE':
            arm = mesh_obj.parent
            arm.name = f"human_{gender}_armature"
            if arm.data:
                arm.data.name = f"human_{gender}_skeleton"
        # Rename materials
        for slot in mesh_obj.material_slots:
            if slot.material:
                slot.material.name = f"human_{gender}_skin"


def _export_figure(gender, mesh_obj, out_glb):
    """Select the mesh + its armature parent and export as GLB."""
    bpy.ops.object.select_all(action='DESELECT')
    mesh_obj.select_set(True)
    arm = mesh_obj.parent
    if arm and arm.type == 'ARMATURE':
        arm.select_set(True)
        bpy.context.view_layer.objects.active = arm
    else:
        bpy.context.view_layer.objects.active = mesh_obj
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    bpy.ops.export_scene.gltf(
        filepath=out_glb,
        export_format='GLB',
        use_selection=True,
        export_apply=False,
        export_yup=True,
        export_animations=False,
    )
    print(f"[import_planar_human_base] exported {out_glb}")


def main():
    _clear_scene()
    _import_reference()
    figures = _classify_figures()

    if 'male' not in figures or 'female' not in figures:
        raise RuntimeError(
            f"Couldn't find both male + female meshes — got "
            f"{list(figures.keys())}. Inspect the imported scene "
            f"by opening the .blend that this script writes.")

    _normalize_names(figures)

    os.makedirs(OUTPUT_DIR, exist_ok=True)
    _export_figure('male', figures['male'],
                   os.path.join(OUTPUT_DIR, "human_male_base.glb"))
    _export_figure('female', figures['female'],
                   os.path.join(OUTPUT_DIR, "human_female_base.glb"))

    bpy.ops.wm.save_as_mainfile(filepath=WORKSPACE_BLEND)
    print(f"[import_planar_human_base] saved {WORKSPACE_BLEND}")
    print("[import_planar_human_base] Open this .blend in Blender, "
          "switch to Sculpt mode, refine on top of the reference "
          "topology. Save body-type variants as separate scenes / "
          "shape keys for build_human_variants.py to pick up next.")


if __name__ == "__main__":
    main()
