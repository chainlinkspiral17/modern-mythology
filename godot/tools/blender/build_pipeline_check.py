"""
build_pipeline_check.py
══════════════════════════════════════════════════════════════════
MINIMAL Blender→Godot pipeline test.

Goal: prove the basic Blender-export → Godot-import → render flow
works end-to-end with the simplest possible asset. No vertex
colors (which I think tripped up the cathedral build). Uses
Blender's standard PBR material system — exports as glTF
materials, imports in Godot as StandardMaterial3D automatically.

If this scene renders correctly in Godot, the pipeline works and
we can add complexity. If it doesn't, we know it's a fundamental
Blender/Godot setup issue.

Run:
    blender --background --python build_pipeline_check.py
    (or ./run_cathedral.sh build_pipeline_check.py)

Output:
    godot/assets/3d/test/pipeline_check.glb

The scene:
    · floor (10x10m, brown)
    · ceiling (10x10m, slightly darker brown)
    · four walls (warm beige)
    · one freestanding cube in the center (rust-red, marker object)
    · NO lights or cameras (Godot scene will add those)

The center cube is a visual reference so you can tell which way
you're facing once in Godot.
"""

import bpy
import os

OUTPUT_DIR = "../../assets/3d/test"
OUTPUT_NAME = "pipeline_check.glb"

ROOM_W = 10.0
ROOM_D = 10.0
ROOM_H = 4.0


def clear_scene():
    bpy.ops.object.select_all(action='SELECT')
    bpy.ops.object.delete(use_global=False)
    for c in (bpy.data.meshes, bpy.data.materials, bpy.data.images):
        for item in list(c):
            if item.users == 0:
                c.remove(item)


def make_material(name, base_color):
    """Create a basic Blender PBR material with a diffuse color.
    The glTF exporter writes this as a standard material that
    Godot imports as StandardMaterial3D — no custom-shader path,
    no vertex-color tricks."""
    mat = bpy.data.materials.new(name=name)
    mat.use_nodes = True
    bsdf = mat.node_tree.nodes.get("Principled BSDF")
    if bsdf:
        bsdf.inputs["Base Color"].default_value = base_color
        bsdf.inputs["Roughness"].default_value = 1.0
        # Some Blender versions name this "Specular" or "Specular IOR Level"
        for key in ("Specular", "Specular IOR Level"):
            if key in bsdf.inputs:
                bsdf.inputs[key].default_value = 0.0
                break
    return mat


def make_box(name, location, size, material):
    """Add a box primitive at location, scale to size, apply material."""
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=location)
    obj = bpy.context.active_object
    obj.name = name
    obj.scale = (size[0]/2, size[1]/2, size[2]/2)
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    obj.data.materials.clear()
    obj.data.materials.append(material)
    return obj


def build_room():
    mat_floor   = make_material("Mat_Floor",   (0.42, 0.32, 0.20, 1.0))
    mat_ceiling = make_material("Mat_Ceiling", (0.32, 0.24, 0.16, 1.0))
    mat_wall    = make_material("Mat_Wall",    (0.65, 0.55, 0.40, 1.0))
    mat_cube    = make_material("Mat_Cube",    (0.78, 0.32, 0.18, 1.0))

    make_box("Floor",   (0, 0, -0.05),         (ROOM_W,  ROOM_D, 0.10), mat_floor)
    make_box("Ceiling", (0, 0, ROOM_H + 0.05), (ROOM_W,  ROOM_D, 0.10), mat_ceiling)
    make_box("Wall_N",  (0, ROOM_D/2 + 0.05, ROOM_H/2),  (ROOM_W, 0.10, ROOM_H), mat_wall)
    make_box("Wall_S",  (0, -ROOM_D/2 - 0.05, ROOM_H/2), (ROOM_W, 0.10, ROOM_H), mat_wall)
    make_box("Wall_E",  (ROOM_W/2 + 0.05, 0, ROOM_H/2),  (0.10, ROOM_D, ROOM_H), mat_wall)
    make_box("Wall_W",  (-ROOM_W/2 - 0.05, 0, ROOM_H/2), (0.10, ROOM_D, ROOM_H), mat_wall)

    # Center reference cube — so you know which way you're facing in Godot
    make_box("CenterMarker_Cube", (0, 2, 0.5), (0.6, 0.6, 1.0), mat_cube)


def export_glb():
    out_dir = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), OUTPUT_DIR))
    os.makedirs(out_dir, exist_ok=True)
    out_path = os.path.join(out_dir, OUTPUT_NAME)

    print(f"\n[build_pipeline_check] exporting to {out_path}")
    print(f"[build_pipeline_check] scene objects: {len(bpy.context.scene.objects)}")

    bpy.ops.object.select_all(action='SELECT')

    # Simplest possible export — just glTF defaults. No vertex
    # colors, no light export, no camera export. Just meshes +
    # materials.
    try:
        result = bpy.ops.export_scene.gltf(
            filepath=out_path,
            export_format='GLB',
            use_selection=False,
            export_apply=True,
        )
        print(f"[build_pipeline_check] export result: {result}")
    except Exception as e:
        print(f"[build_pipeline_check] ✗ EXPORT FAILED: {e}")
        import traceback; traceback.print_exc()
        raise

    if os.path.exists(out_path):
        size = os.path.getsize(out_path)
        print(f"[build_pipeline_check] ✓ wrote {out_path} ({size} bytes)")
    else:
        raise RuntimeError("GLB not written")


def main():
    clear_scene()
    build_room()
    export_glb()


if __name__ == "__main__":
    main()
