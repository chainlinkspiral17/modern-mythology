"""
build_atmosphere_props.py
══════════════════════════════════════════════════════════════════
COMMUNITY PLANNED · the inhabiting atmosphere of the Cathedral.

Run:
    blender --background --python build_atmosphere_props.py
    (or ./run_cathedral.sh build_atmosphere_props.py)

Output:
    godot/assets/3d/atmosphere/atmosphere.glb

Includes:
    · Faith the dog (curled on the back-room rug)
    · the phone on the workbench's edge
    · the back-room partition (bathroom + storage)
    · the freight bay door (the rolling industrial door on +X)
    · a hanging light bulb above the workbench (warm overhead)
    · a few stacked crates against the south wall
"""

import bpy
import math
import os
from mathutils import Vector

OUTPUT_DIR = "../../assets/3d/atmosphere"
OUTPUT_NAME = "atmosphere.glb"

# Warehouse coordinate-frame constants (match cathedral_interior.py)
WH_W = 24.0
WH_D = 18.0
WH_H = 7.0
WB_X = 0.0
WB_Y = -3.0
WB_TOP_Z = 0.94
BAY_W = 4.0
BAY_H = 4.0

LIGHT_DIR_COOL = Vector((1.0, 0.0, 0.3)).normalized()
LIGHT_COL_COOL = Vector((0.55, 0.65, 0.80))
LIGHT_DIR_WARM = Vector((0.0, 0.0, 1.0)).normalized()
LIGHT_COL_WARM = Vector((0.95, 0.75, 0.50))
AMBIENT        = Vector((0.10, 0.08, 0.06))


def clear_scene():
    bpy.ops.object.select_all(action='SELECT')
    bpy.ops.object.delete(use_global=False)
    for c in (bpy.data.meshes, bpy.data.materials, bpy.data.images):
        for item in list(c):
            if item.users == 0:
                c.remove(item)


def gouraud_term(normal, base_rgba):
    n = Vector(normal).normalized()
    cool = max(0.0, n.dot(LIGHT_DIR_COOL))
    warm = max(0.0, n.dot(LIGHT_DIR_WARM))
    light = Vector((
        AMBIENT.x + LIGHT_COL_COOL.x * cool + LIGHT_COL_WARM.x * warm * 0.4,
        AMBIENT.y + LIGHT_COL_COOL.y * cool + LIGHT_COL_WARM.y * warm * 0.4,
        AMBIENT.z + LIGHT_COL_COOL.z * cool + LIGHT_COL_WARM.z * warm * 0.4,
    ))
    return (
        min(1.0, base_rgba[0] * light.x),
        min(1.0, base_rgba[1] * light.y),
        min(1.0, base_rgba[2] * light.z),
        base_rgba[3]
    )


def make_box(name, center, size, base_color, open_faces=None):
    open_faces = open_faces or set()
    cx, cy, cz = center
    sx, sy, sz = size
    hx, hy, hz = sx/2, sy/2, sz/2
    verts = [
        (cx-hx, cy-hy, cz-hz), (cx+hx, cy-hy, cz-hz),
        (cx+hx, cy+hy, cz-hz), (cx-hx, cy+hy, cz-hz),
        (cx-hx, cy-hy, cz+hz), (cx+hx, cy-hy, cz+hz),
        (cx+hx, cy+hy, cz+hz), (cx-hx, cy+hy, cz+hz),
    ]
    face_defs = [
        ('-Z', (0,3,2,1), ( 0, 0,-1)),
        ('+Z', (4,5,6,7), ( 0, 0, 1)),
        ('-Y', (0,1,5,4), ( 0,-1, 0)),
        ('+Y', (2,3,7,6), ( 0, 1, 0)),
        ('-X', (3,0,4,7), (-1, 0, 0)),
        ('+X', (1,2,6,5), ( 1, 0, 0)),
    ]
    mesh = bpy.data.meshes.new(name + "_mesh")
    out_verts, out_faces, out_colors = [], [], []
    vmap = {}
    def vidx(v_orig, normal):
        key = (v_orig, tuple(normal))
        if key in vmap: return vmap[key]
        idx = len(out_verts)
        out_verts.append(verts[v_orig])
        out_colors.append(gouraud_term(normal, base_color))
        vmap[key] = idx
        return idx
    for tag, vids, normal in face_defs:
        if tag in open_faces: continue
        out_faces.append([vidx(v, normal) for v in vids])
    mesh.from_pydata(out_verts, [], out_faces)
    mesh.update()
    if not mesh.vertex_colors:
        mesh.vertex_colors.new(name="Col")
    layer = mesh.vertex_colors["Col"]
    for poly in mesh.polygons:
        for li in poly.loop_indices:
            v = mesh.loops[li].vertex_index
            layer.data[li].color = out_colors[v]
    obj = bpy.data.objects.new(name, mesh)
    bpy.context.collection.objects.link(obj)
    return obj


# ════════════════════════════════════════════════════════════════
# FAITH THE DOG
# ════════════════════════════════════════════════════════════════

def build_faith():
    """Faith — medium mongrel, white with grey patches, curled on a rug in the back."""
    # the rug
    fx, fy = -8.0, -7.5
    rug_color = (0.45, 0.25, 0.18, 1.0)
    make_box("Faith_Rug", (fx, fy, 0.012), (1.4, 0.9, 0.024), rug_color)
    # Faith curled up (low chunky form, more horizontal than tall)
    body_color = (0.78, 0.74, 0.68, 1.0)        # white-ish
    patch_color = (0.55, 0.50, 0.42, 1.0)        # grey patches
    # main curled body
    make_box("Faith_Body", (fx, fy, 0.10), (0.50, 0.32, 0.16), body_color)
    # grey patch on the back
    make_box("Faith_Patch_Back", (fx - 0.05, fy + 0.05, 0.18), (0.16, 0.10, 0.03), patch_color)
    # head tucked at one end
    make_box("Faith_Head", (fx + 0.28, fy + 0.04, 0.10), (0.14, 0.12, 0.12), body_color)
    # one ear up, one down (per canon)
    make_box("Faith_Ear_Up", (fx + 0.31, fy + 0.08, 0.20), (0.04, 0.04, 0.06), body_color)
    make_box("Faith_Ear_Down", (fx + 0.31, fy - 0.04, 0.14), (0.05, 0.04, 0.02), patch_color)
    # tail curled around
    make_box("Faith_Tail", (fx - 0.22, fy + 0.10, 0.12), (0.16, 0.04, 0.03), body_color)


# ════════════════════════════════════════════════════════════════
# THE PHONE
# ════════════════════════════════════════════════════════════════

def build_phone():
    """Beige push-button phone on the workbench's edge. Receiver in cradle."""
    px = WB_X + 1.0
    py = WB_Y + 0.30
    # base (rounded chunky form, faked with two stacked boxes)
    phone_color = (0.78, 0.72, 0.55, 1.0)
    make_box("Phone_Base_lower", (px, py, WB_TOP_Z + 0.018), (0.22, 0.18, 0.036), phone_color)
    make_box("Phone_Base_upper", (px, py, WB_TOP_Z + 0.055), (0.20, 0.16, 0.020), phone_color)
    # the receiver in its cradle (a thinner curved piece — faked as a slightly-wider top slab)
    receiver_color = (0.74, 0.68, 0.52, 1.0)
    make_box("Phone_Receiver", (px, py - 0.04, WB_TOP_Z + 0.085), (0.20, 0.07, 0.030), receiver_color)
    # the receiver's mouthpiece + earpiece bumps
    make_box("Phone_Mouthpiece", (px - 0.07, py - 0.04, WB_TOP_Z + 0.105), (0.04, 0.06, 0.020), receiver_color)
    make_box("Phone_Earpiece",   (px + 0.07, py - 0.04, WB_TOP_Z + 0.105), (0.04, 0.06, 0.020), receiver_color)
    # keypad (a 3x4 grid faked as a single darker slab with subtle button shapes)
    keypad_color = (0.48, 0.42, 0.32, 1.0)
    make_box("Phone_Keypad", (px, py + 0.03, WB_TOP_Z + 0.072), (0.16, 0.10, 0.005), keypad_color)
    # tiny "buttons" as four bumps
    button_color = (0.85, 0.80, 0.62, 1.0)
    for i in range(3):
        for j in range(4):
            bx = px - 0.06 + i * 0.06
            by = py + 0.06 - j * 0.024
            make_box(f"Phone_Btn_{i}_{j}", (bx, by, WB_TOP_Z + 0.077),
                     (0.018, 0.014, 0.006), button_color)
    # the coiled cord trailing off the back (faked as a small chunky helix)
    cord_color = (0.65, 0.60, 0.46, 1.0)
    for i in range(5):
        cz = WB_TOP_Z + 0.06 - i * 0.012
        cy_off = 0.10 + i * 0.018
        make_box(f"Phone_Cord_{i}", (px + 0.10, py + cy_off, cz),
                 (0.012, 0.020, 0.012), cord_color)


# ════════════════════════════════════════════════════════════════
# THE BACK-ROOM PARTITION
# ════════════════════════════════════════════════════════════════

def build_back_partition():
    """A small wall partition in the back creating the bathroom + a storage nook."""
    # the partition wall (runs north-south, 4m long, against the +Y wall at x=-6)
    partition_color = (0.30, 0.24, 0.16, 1.0)
    make_box("BackRoom_Partition",
             (-6.0, 7.0, WH_H / 2),
             (0.15, 4.0, WH_H * 0.55),  # only ~3.85m tall (doesn't reach ceiling)
             partition_color)
    # a doorframe in the partition
    door_color = (0.42, 0.32, 0.22, 1.0)
    make_box("BackRoom_DoorFrame_top",
             (-6.0, 6.0, 2.20),
             (0.16, 1.0, 0.10),
             door_color)
    make_box("BackRoom_DoorFrame_left",
             (-6.0, 5.50, 1.10),
             (0.16, 0.05, 2.20),
             door_color)
    make_box("BackRoom_DoorFrame_right",
             (-6.0, 6.50, 1.10),
             (0.16, 0.05, 2.20),
             door_color)


# ════════════════════════════════════════════════════════════════
# THE FREIGHT BAY DOOR
# ════════════════════════════════════════════════════════════════

def build_freight_door():
    """The rolling industrial door on the east wall — closed, with slats."""
    door_color = (0.42, 0.36, 0.26, 1.0)
    slat_color = (0.30, 0.26, 0.20, 1.0)
    door_x = WH_W / 2 - 0.02
    door_y_center = -WH_D / 2 + BAY_W / 2
    # door panel
    make_box("FreightDoor_Panel",
             (door_x, door_y_center, BAY_H / 2),
             (0.06, BAY_W, BAY_H),
             door_color)
    # horizontal slats (8 across the height)
    for i in range(8):
        slat_z = 0.25 + i * (BAY_H - 0.4) / 7
        make_box(f"FreightDoor_Slat_{i}",
                 (door_x - 0.03, door_y_center, slat_z),
                 (0.02, BAY_W * 0.95, 0.05),
                 slat_color)
    # the bottom rail and the rolling track at top
    make_box("FreightDoor_BottomRail",
             (door_x, door_y_center, 0.05),
             (0.10, BAY_W * 1.05, 0.10),
             slat_color)
    make_box("FreightDoor_TopTrack",
             (door_x, door_y_center, BAY_H + 0.20),
             (0.14, BAY_W * 1.1, 0.14),
             slat_color)


# ════════════════════════════════════════════════════════════════
# HANGING BULB OVER THE WORKBENCH
# ════════════════════════════════════════════════════════════════

def build_hanging_bulb():
    """A bare warm bulb on a wire above the workbench."""
    bx, by = WB_X, WB_Y
    bulb_z = WH_H - 1.5
    # the wire
    wire_color = (0.10, 0.08, 0.06, 1.0)
    make_box("WorkbenchBulb_Wire",
             (bx, by, bulb_z + 0.80),
             (0.012, 0.012, 1.5),
             wire_color)
    # the porcelain socket
    socket_color = (0.85, 0.80, 0.70, 1.0)
    make_box("WorkbenchBulb_Socket",
             (bx, by, bulb_z + 0.05),
             (0.06, 0.06, 0.08),
             socket_color)
    # the bulb itself (a slightly translucent warm slab)
    bulb_color = (0.98, 0.85, 0.55, 1.0)
    make_box("WorkbenchBulb_Bulb",
             (bx, by, bulb_z - 0.04),
             (0.08, 0.08, 0.08),
             bulb_color)


# ════════════════════════════════════════════════════════════════
# CRATES AGAINST THE SOUTH WALL
# ════════════════════════════════════════════════════════════════

def build_crates():
    """A few stacked wooden crates against the south wall (storage)."""
    crate_color = (0.50, 0.36, 0.22, 1.0)
    crate_color_2 = (0.45, 0.32, 0.20, 1.0)
    # three large crates, stacked
    cy = -WH_D / 2 + 0.65
    make_box("Crate_1", (-9.0, cy, 0.40), (0.80, 0.80, 0.80), crate_color)
    make_box("Crate_2", (-8.0, cy, 0.40), (0.80, 0.80, 0.80), crate_color_2)
    make_box("Crate_3", (-9.0, cy, 1.20), (0.80, 0.80, 0.80), crate_color_2)
    # a smaller crate on the right
    make_box("Crate_4", (-7.0, cy, 0.30), (0.55, 0.55, 0.55), crate_color)


# ════════════════════════════════════════════════════════════════
# EXPORT
# ════════════════════════════════════════════════════════════════

def export_glb():
    out_dir = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), OUTPUT_DIR))
    os.makedirs(out_dir, exist_ok=True)
    out_path = os.path.join(out_dir, OUTPUT_NAME)

    print(f"\n[build_atmosphere_props] exporting to {out_path}")
    print(f"[build_atmosphere_props] scene objects: {len(bpy.context.scene.objects)}")

    bpy.ops.object.select_all(action='SELECT')
    base = {
        'filepath': out_path, 'export_format': 'GLB',
        'use_selection': False, 'export_apply': True,
    }
    rna = bpy.ops.export_scene.gltf.get_rna_type()
    legacy = {}
    if 'export_colors' in rna.properties: legacy['export_colors'] = True
    if 'export_normals' in rna.properties: legacy['export_normals'] = True

    try:
        result = bpy.ops.export_scene.gltf(**base, **legacy)
        print(f"[build_atmosphere_props] export result: {result}")
    except Exception as e:
        print(f"[build_atmosphere_props] ✗ EXPORT FAILED: {e}")
        import traceback; traceback.print_exc()
        raise

    if os.path.exists(out_path):
        size = os.path.getsize(out_path)
        print(f"[build_atmosphere_props] ✓ wrote {out_path} ({size} bytes)")
    else:
        raise RuntimeError("GLB not written")


def main():
    clear_scene()
    build_faith()
    build_phone()
    build_back_partition()
    build_freight_door()
    build_hanging_bulb()
    build_crates()
    export_glb()


if __name__ == "__main__":
    main()
