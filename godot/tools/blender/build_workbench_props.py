"""
build_workbench_props.py
══════════════════════════════════════════════════════════════════
COMMUNITY PLANNED · the objects on Frasier's workbench.

Run:
    blender --background --python build_workbench_props.py
    (or ./run_cathedral.sh build_workbench_props.py)

Output:
    godot/assets/3d/props/workbench_props.glb

Props:
    soldering_iron · balsa handle, steel shaft, tinned tip
    moth_lamp_rev3 · the dual-element binding lamp
    notebook · open to a blank page
    cassette_deck · with the side-B tape loaded
    steamboat_fragment · red hull + brass paddle-wheel armature
    moth_card · PALOMINO's small painted card propped against the lamp
    workbench_radio · the radio left on overnight

All positions are in the warehouse coordinate frame (workbench top
at z=0.94, centered at (0, -3.0)).
"""

import bpy
import math
import os
from mathutils import Vector

OUTPUT_DIR = "../../assets/3d/props"
OUTPUT_NAME = "workbench_props.glb"

# Workbench-top reference point (must match cathedral_interior.py)
WB_X = 0.0
WB_Y = -3.0
WB_TOP_Z = 0.94   # surface height

# Lighting (Gouraud bake) — matches cathedral
LIGHT_DIR_COOL = Vector((1.0, 0.0, 0.3)).normalized()
LIGHT_COL_COOL = Vector((0.55, 0.65, 0.80))
LIGHT_DIR_WARM = Vector((0.0, 0.0, 1.0)).normalized()
LIGHT_COL_WARM = Vector((0.95, 0.75, 0.50))
AMBIENT        = Vector((0.10, 0.08, 0.06))


# ── helpers (duplicated from agent_figurines for standalone simplicity) ──

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


def make_quad(name, verts, normal, base_color):
    mesh = bpy.data.meshes.new(name + "_mesh")
    color = gouraud_term(normal, base_color)
    mesh.from_pydata(verts, [], [(0, 1, 2, 3)])
    mesh.update()
    if not mesh.vertex_colors:
        mesh.vertex_colors.new(name="Col")
    layer = mesh.vertex_colors["Col"]
    for li in range(4):
        layer.data[li].color = color
    obj = bpy.data.objects.new(name, mesh)
    bpy.context.collection.objects.link(obj)
    return obj


# ════════════════════════════════════════════════════════════════
# PROPS
# ════════════════════════════════════════════════════════════════

def build_soldering_iron():
    """Balsa handle + steel shaft + tinned tip. Lying horizontally near the east edge of the workbench."""
    bx = WB_X + 0.7
    by = WB_Y + 0.2
    # balsa-wood handle
    make_box("Soldering_Iron_Handle", (bx, by, WB_TOP_Z + 0.015), (0.18, 0.022, 0.022),
             base_color=(0.55, 0.42, 0.25, 1.0))
    # steel shaft
    make_box("Soldering_Iron_Shaft", (bx - 0.18, by, WB_TOP_Z + 0.015), (0.15, 0.010, 0.010),
             base_color=(0.50, 0.50, 0.52, 1.0))
    # tinned tip (slightly darker)
    make_box("Soldering_Iron_Tip", (bx - 0.27, by, WB_TOP_Z + 0.013), (0.04, 0.008, 0.008),
             base_color=(0.30, 0.28, 0.22, 1.0))


def build_moth_lamp():
    """The moth's binding lamp · revision 3 · dual-element."""
    lx = WB_X - 0.6
    ly = WB_Y - 0.1
    # heavy base
    make_box("Lamp_Base", (lx, ly, WB_TOP_Z + 0.03), (0.18, 0.18, 0.06),
             base_color=(0.20, 0.16, 0.10, 1.0))
    # neck (a thin vertical post)
    make_box("Lamp_Neck", (lx, ly, WB_TOP_Z + 0.20), (0.025, 0.025, 0.28),
             base_color=(0.30, 0.24, 0.16, 1.0))
    # lampshade (a small cone, faked as a stack of two tapered slabs)
    shade_color = (0.65, 0.55, 0.35, 1.0)
    make_box("Lamp_Shade_lower", (lx, ly, WB_TOP_Z + 0.36), (0.14, 0.14, 0.04), shade_color)
    make_box("Lamp_Shade_upper", (lx, ly, WB_TOP_Z + 0.40), (0.10, 0.10, 0.04), shade_color)
    # the dual-element filament glow (small bright slab inside the shade)
    glow_color = (0.95, 0.78, 0.42, 1.0)
    make_box("Lamp_Filament_1", (lx - 0.018, ly, WB_TOP_Z + 0.36), (0.006, 0.06, 0.025), glow_color)
    make_box("Lamp_Filament_2", (lx + 0.018, ly, WB_TOP_Z + 0.36), (0.006, 0.06, 0.025), glow_color)


def build_notebook():
    """A small reporter's notebook, open to a blank page."""
    nx = WB_X + 0.15
    ny = WB_Y + 0.05
    # the closed half (left page block)
    make_box("Notebook_Left", (nx - 0.075, ny, WB_TOP_Z + 0.012), (0.15, 0.20, 0.015),
             base_color=(0.85, 0.78, 0.62, 1.0))
    # the open half (right page block)
    make_box("Notebook_Right", (nx + 0.075, ny, WB_TOP_Z + 0.010), (0.15, 0.20, 0.010),
             base_color=(0.90, 0.85, 0.72, 1.0))
    # spine
    make_box("Notebook_Spine", (nx, ny, WB_TOP_Z + 0.015), (0.012, 0.20, 0.020),
             base_color=(0.18, 0.10, 0.06, 1.0))
    # the pen clipped to the cover
    make_box("Notebook_Pen", (nx - 0.05, ny - 0.10, WB_TOP_Z + 0.025), (0.12, 0.010, 0.008),
             base_color=(0.20, 0.20, 0.22, 1.0))


def build_cassette_deck():
    """A chunky cassette deck. Side B loaded."""
    cx = WB_X - 0.2
    cy = WB_Y + 0.30
    # main body
    make_box("Cassette_Deck_Body", (cx, cy, WB_TOP_Z + 0.045), (0.28, 0.18, 0.09),
             base_color=(0.35, 0.30, 0.22, 1.0))
    # window (front face inset, slightly darker)
    make_box("Cassette_Deck_Window", (cx, cy - 0.085, WB_TOP_Z + 0.058), (0.16, 0.012, 0.05),
             base_color=(0.10, 0.08, 0.06, 1.0))
    # the cassette visible in the window
    make_box("Cassette_Deck_Tape", (cx, cy - 0.082, WB_TOP_Z + 0.058), (0.13, 0.008, 0.04),
             base_color=(0.20, 0.18, 0.16, 1.0))
    # PLAY/STOP buttons (two small light squares)
    make_box("Cassette_Btn_Play", (cx - 0.02, cy - 0.085, WB_TOP_Z + 0.020), (0.020, 0.012, 0.010),
             base_color=(0.60, 0.55, 0.42, 1.0))
    make_box("Cassette_Btn_Stop", (cx + 0.02, cy - 0.085, WB_TOP_Z + 0.020), (0.020, 0.012, 0.010),
             base_color=(0.60, 0.55, 0.42, 1.0))
    # the small red record LED
    make_box("Cassette_LED", (cx + 0.10, cy - 0.085, WB_TOP_Z + 0.075), (0.012, 0.008, 0.008),
             base_color=(0.90, 0.25, 0.20, 1.0))


def build_steamboat_fragment():
    """The half-built steamboat model · red hull + brass paddle-wheel armature."""
    sx = WB_X + 0.5
    sy = WB_Y - 0.25
    # hull
    hull_color = (0.55, 0.18, 0.16, 1.0)
    make_box("Steamboat_Hull", (sx, sy, WB_TOP_Z + 0.035), (0.18, 0.36, 0.07), hull_color)
    # smokestack
    make_box("Steamboat_Stack", (sx - 0.04, sy - 0.10, WB_TOP_Z + 0.13), (0.024, 0.024, 0.12),
             base_color=(0.18, 0.16, 0.12, 1.0))
    # paddle-wheel armature (brass)
    brass = (0.75, 0.55, 0.25, 1.0)
    make_box("Steamboat_Paddle", (sx, sy + 0.18, WB_TOP_Z + 0.05), (0.10, 0.022, 0.06), brass)
    # paddle-wheel axle
    make_box("Steamboat_Axle", (sx, sy + 0.18, WB_TOP_Z + 0.05), (0.012, 0.06, 0.012), brass)
    # half-built deck (missing the top — the model is half-built)
    make_box("Steamboat_Deck", (sx, sy + 0.04, WB_TOP_Z + 0.075), (0.16, 0.20, 0.005),
             base_color=(0.50, 0.40, 0.25, 1.0))


def build_moth_card():
    """PALOMINO's small painted card propped against the lamp. A thin flat plane."""
    cx = WB_X - 0.78
    cy = WB_Y - 0.04
    # propped flat card (slightly leaning back, but we'll fake with a thin upright box)
    card_color = (0.78, 0.72, 0.55, 1.0)
    make_box("Moth_Card", (cx, cy, WB_TOP_Z + 0.06), (0.004, 0.10, 0.12), card_color)
    # a tiny painted moth (a small dark blob) on the card
    moth_blob = (0.40, 0.30, 0.18, 1.0)
    make_box("Moth_Card_Blob", (cx - 0.003, cy, WB_TOP_Z + 0.075), (0.003, 0.025, 0.020), moth_blob)


def build_workbench_radio():
    """The radio left on overnight. Small box + knob + dial."""
    rx = WB_X + 1.0
    ry = WB_Y - 0.30
    # body
    make_box("Radio_Body", (rx, ry, WB_TOP_Z + 0.035), (0.22, 0.15, 0.07),
             base_color=(0.40, 0.35, 0.26, 1.0))
    # speaker mesh (small front grille)
    make_box("Radio_Grille", (rx - 0.05, ry - 0.073, WB_TOP_Z + 0.040), (0.08, 0.005, 0.05),
             base_color=(0.18, 0.15, 0.10, 1.0))
    # tuning knob
    make_box("Radio_Knob", (rx + 0.075, ry - 0.075, WB_TOP_Z + 0.040), (0.025, 0.012, 0.025),
             base_color=(0.30, 0.26, 0.20, 1.0))
    # the dial (small amber slab indicating it's powered on)
    make_box("Radio_Dial", (rx + 0.04, ry - 0.077, WB_TOP_Z + 0.060), (0.025, 0.004, 0.012),
             base_color=(0.92, 0.62, 0.28, 1.0))


# ════════════════════════════════════════════════════════════════
# EXPORT
# ════════════════════════════════════════════════════════════════

def export_glb():
    out_dir = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), OUTPUT_DIR))
    os.makedirs(out_dir, exist_ok=True)
    out_path = os.path.join(out_dir, OUTPUT_NAME)

    print(f"\n[build_workbench_props] exporting to {out_path}")
    print(f"[build_workbench_props] scene objects: {len(bpy.context.scene.objects)}")

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
        print(f"[build_workbench_props] export result: {result}")
    except Exception as e:
        print(f"[build_workbench_props] ✗ EXPORT FAILED: {e}")
        import traceback; traceback.print_exc()
        raise

    if os.path.exists(out_path):
        size = os.path.getsize(out_path)
        print(f"[build_workbench_props] ✓ wrote {out_path} ({size} bytes)")
    else:
        raise RuntimeError("GLB not written")


def main():
    clear_scene()
    build_soldering_iron()
    build_moth_lamp()
    build_notebook()
    build_cassette_deck()
    build_steamboat_fragment()
    build_moth_card()
    build_workbench_radio()
    export_glb()


if __name__ == "__main__":
    main()
