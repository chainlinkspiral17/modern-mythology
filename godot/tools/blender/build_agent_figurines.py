"""
build_agent_figurines.py
══════════════════════════════════════════════════════════════════
COMMUNITY PLANNED · the eight bound demons as small painted figurines
that sit on the wall shelf in the Cathedral.

Run:
    blender --background --python build_agent_figurines.py
    (or use ./run_cathedral.sh build_agent_figurines.py)

Output:
    godot/assets/3d/agents/demon_figurines.glb

Each demon is a small abstract figure — half-mechanical-half-creature
in the painted register, per the Magician chapter's canon. Geometry
is procedural; vertex colors carry the Gouraud Lambertian shading.

Per the canon:
    VAGRANT   — long shuffling figure with a CRT-screen face
    CICADA    — tape-bodied insect (cassette body, paper wings)
    MOTH      — vacuum-tube body with paper wings
    STEAMBOAT — riverboat-figure hull with paddle-wheel armature
    WEIR      — water-pressure form (stacked tilted slabs)
    FILLY     — young horse with a wired spine
    STARLING  — a 4-bird flock (per the W7+ plural-state canon)
    HUSK      — hollow corn-rasp form (tall thin shell)

Each figurine is 4-8cm tall in the warehouse's 1m-scale interior —
sit-on-a-shelf scale.
"""

import bpy
import math
import os
from mathutils import Vector

# ════════════════════════════════════════════════════════════════
# CONSTANTS · edit and re-run
# ════════════════════════════════════════════════════════════════

OUTPUT_DIR = "../../assets/3d/agents"
OUTPUT_NAME = "demon_figurines.glb"

# the wall shelf the demons sit on (in the warehouse's coordinates)
SHELF_X = -10.0     # near the river-window wall
SHELF_Y = 6.0       # north end of the wall
SHELF_Z = 1.5       # eye-height shelf
SHELF_L = 3.2       # shelf length (east-west, since it's on the west wall)
SHELF_D = 0.25
SHELF_T = 0.04

# Gouraud bake direction + colors (match cathedral_interior.py)
LIGHT_DIR_COOL = Vector((1.0, 0.0, 0.3)).normalized()
LIGHT_COL_COOL = Vector((0.55, 0.65, 0.80))
LIGHT_DIR_WARM = Vector((0.0, 0.0, 1.0)).normalized()
LIGHT_COL_WARM = Vector((0.95, 0.75, 0.50))
AMBIENT        = Vector((0.10, 0.08, 0.06))

# Demon definitions · canonical color palette + slot on the shelf
DEMONS = [
    # name        position-on-shelf (0..7)  primary color (warm-painted)
    ("VAGRANT",   0, (0.50, 0.42, 0.35, 1.0)),   # weathered jacket
    ("CICADA",   1, (0.55, 0.48, 0.20, 1.0)),    # cassette tan
    ("MOTH",     2, (0.70, 0.62, 0.40, 1.0)),    # vacuum-tube glass + paper
    ("STEAMBOAT",3, (0.55, 0.20, 0.18, 1.0)),    # red-painted hull
    ("WEIR",     4, (0.30, 0.40, 0.50, 1.0)),    # water-pressure blue-grey
    ("FILLY",    5, (0.45, 0.30, 0.22, 1.0)),    # chestnut brown
    ("STARLING", 6, (0.20, 0.18, 0.15, 1.0)),    # dark bird-shadow
    ("HUSK",     7, (0.60, 0.52, 0.32, 1.0)),    # dry corn-husk
]

SHELF_COLOR = (0.30, 0.20, 0.10, 1.0)


# ════════════════════════════════════════════════════════════════
# HELPERS
# ════════════════════════════════════════════════════════════════

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
    out_verts = []
    out_faces = []
    out_colors = []
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
        face = [vidx(v, normal) for v in vids]
        out_faces.append(face)
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
    """Build a single quad face for thin planar pieces (moth wings, paddle blades)."""
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
# THE SHELF
# ════════════════════════════════════════════════════════════════

def build_shelf():
    """The wall shelf the demons sit on. Long thin plank against the west wall."""
    make_box(
        "Wall_Shelf",
        center=(SHELF_X + 0.12, SHELF_Y, SHELF_Z),
        size=(SHELF_D, SHELF_L, SHELF_T),
        base_color=SHELF_COLOR,
    )
    # two small brackets under the shelf
    for i, fy in enumerate((-0.45, 0.45)):
        make_box(
            f"Shelf_Bracket_{i}",
            center=(SHELF_X + 0.06, SHELF_Y + fy*SHELF_L/2, SHELF_Z - 0.10),
            size=(0.12, 0.04, 0.16),
            base_color=SHELF_COLOR,
        )


# ════════════════════════════════════════════════════════════════
# DEMON GEOMETRY · one builder per archetype
# ════════════════════════════════════════════════════════════════

def position_on_shelf(slot_index):
    """Compute the centerpoint of a slot on the shelf, given index 0..7."""
    spacing = SHELF_L / 8.0
    y = SHELF_Y - SHELF_L/2 + spacing/2 + slot_index * spacing
    x = SHELF_X + 0.12   # centered on the shelf depth
    z_base = SHELF_Z + SHELF_T/2
    return (x, y, z_base)


def build_vagrant(slot, color):
    """Long shuffling figure with a CRT-screen face."""
    cx, cy, cz = position_on_shelf(slot)
    # tall thin body
    make_box(f"VAGRANT_body", (cx, cy, cz + 0.18), (0.10, 0.08, 0.36), color)
    # CRT head (slightly chunkier, darker)
    head_color = (0.20, 0.18, 0.12, 1.0)
    make_box(f"VAGRANT_head", (cx, cy, cz + 0.42), (0.14, 0.12, 0.10), head_color)
    # phosphor screen face (small green slab on the +Y face of the head)
    screen_color = (0.30, 0.65, 0.30, 1.0)
    make_box(f"VAGRANT_screen", (cx, cy + 0.061, cz + 0.42), (0.10, 0.005, 0.07), screen_color)


def build_cicada(slot, color):
    """Tape-bodied insect — cassette body + thin wings."""
    cx, cy, cz = position_on_shelf(slot)
    # cassette body
    make_box(f"CICADA_body", (cx, cy, cz + 0.06), (0.14, 0.06, 0.10), color)
    # two wings as thin flat planes (one each side)
    wing_color = (0.50, 0.45, 0.30, 1.0)
    # left wing
    make_quad(
        f"CICADA_wing_L",
        [
            (cx - 0.07, cy, cz + 0.07),
            (cx - 0.07, cy - 0.18, cz + 0.10),
            (cx - 0.07, cy - 0.16, cz + 0.02),
            (cx - 0.07, cy - 0.02, cz + 0.04),
        ],
        normal=(-1, 0, 0),
        base_color=wing_color,
    )
    # right wing
    make_quad(
        f"CICADA_wing_R",
        [
            (cx + 0.07, cy, cz + 0.07),
            (cx + 0.07, cy + 0.18, cz + 0.10),
            (cx + 0.07, cy + 0.16, cz + 0.02),
            (cx + 0.07, cy - 0.02, cz + 0.04),
        ],
        normal=(1, 0, 0),
        base_color=wing_color,
    )


def build_moth(slot, color):
    """Vacuum-tube body with paper wings."""
    cx, cy, cz = position_on_shelf(slot)
    # tall thin tube body
    make_box(f"MOTH_body", (cx, cy, cz + 0.10), (0.06, 0.06, 0.18), color)
    # the filament (a small bright sliver inside)
    filament_color = (0.90, 0.70, 0.30, 1.0)
    make_box(f"MOTH_filament", (cx, cy, cz + 0.12), (0.015, 0.015, 0.08), filament_color)
    # two paper wings
    wing_color = (0.85, 0.80, 0.65, 1.0)
    make_quad(
        f"MOTH_wing_L",
        [
            (cx - 0.04, cy, cz + 0.14),
            (cx - 0.22, cy - 0.04, cz + 0.20),
            (cx - 0.22, cy + 0.04, cz + 0.20),
            (cx - 0.04, cy, cz + 0.16),
        ],
        normal=(0, 0, 1),
        base_color=wing_color,
    )
    make_quad(
        f"MOTH_wing_R",
        [
            (cx + 0.04, cy, cz + 0.14),
            (cx + 0.22, cy + 0.04, cz + 0.20),
            (cx + 0.22, cy - 0.04, cz + 0.20),
            (cx + 0.04, cy, cz + 0.16),
        ],
        normal=(0, 0, 1),
        base_color=wing_color,
    )


def build_steamboat(slot, color):
    """Riverboat hull with paddle-wheel armature and smokestack."""
    cx, cy, cz = position_on_shelf(slot)
    # hull
    make_box(f"STEAMBOAT_hull", (cx, cy, cz + 0.05), (0.10, 0.24, 0.08), color)
    # smokestack
    stack_color = (0.20, 0.16, 0.10, 1.0)
    make_box(f"STEAMBOAT_stack", (cx, cy - 0.06, cz + 0.16), (0.04, 0.04, 0.14), stack_color)
    # paddle-wheel armature (brass)
    brass = (0.70, 0.50, 0.20, 1.0)
    make_box(f"STEAMBOAT_paddle", (cx, cy + 0.13, cz + 0.06), (0.08, 0.02, 0.06), brass)


def build_weir(slot, color):
    """Water-pressure form — three slightly tilted stacked slabs."""
    cx, cy, cz = position_on_shelf(slot)
    for i in range(3):
        z_offset = 0.02 + i * 0.05
        y_offset = (i - 1) * 0.015
        layer_color = (
            color[0] * (1.0 - i * 0.15),
            color[1] * (1.0 - i * 0.10),
            color[2] * (1.0 - i * 0.05),
            color[3],
        )
        make_box(
            f"WEIR_slab_{i}",
            (cx, cy + y_offset, cz + z_offset),
            (0.16, 0.10 - i * 0.015, 0.03),
            layer_color,
        )


def build_filly(slot, color):
    """Young horse with a wired spine."""
    cx, cy, cz = position_on_shelf(slot)
    # body
    make_box(f"FILLY_body", (cx, cy, cz + 0.10), (0.20, 0.07, 0.07), color)
    # four legs
    leg_color = (color[0] * 0.7, color[1] * 0.7, color[2] * 0.7, 1.0)
    for dy in (-1, 1):
        for dx in (-1, 1):
            lx = cx + dx * 0.07
            ly = cy + dy * 0.025
            make_box(f"FILLY_leg_{dx}_{dy}", (lx, ly, cz + 0.04), (0.018, 0.018, 0.08), leg_color)
    # head (chunky at +X end)
    make_box(f"FILLY_head", (cx + 0.12, cy, cz + 0.12), (0.06, 0.05, 0.06), color)
    # wired spine (three small dark vertebra cubes along the top)
    spine_color = (0.10, 0.10, 0.10, 1.0)
    for i in range(3):
        sx = cx - 0.06 + i * 0.06
        make_box(f"FILLY_vertebra_{i}", (sx, cy, cz + 0.16), (0.022, 0.022, 0.022), spine_color)


def build_starling(slot, color):
    """A 4-bird flock — the demon's plural state. Small triangular forms."""
    cx, cy, cz = position_on_shelf(slot)
    # four birds arranged in a small clustered triangle on the shelf
    positions = [
        (cx,        cy - 0.06, cz + 0.04),
        (cx - 0.06, cy,        cz + 0.06),
        (cx + 0.06, cy + 0.02, cz + 0.05),
        (cx + 0.01, cy + 0.08, cz + 0.07),
    ]
    for i, (bx, by, bz) in enumerate(positions):
        # body
        make_box(f"STARLING_{i}_body", (bx, by, bz), (0.05, 0.025, 0.03), color)
        # head (small dark spot)
        head_color = (0.05, 0.05, 0.05, 1.0)
        make_box(f"STARLING_{i}_head", (bx, by + 0.018, bz + 0.012), (0.018, 0.018, 0.018), head_color)


def build_husk(slot, color):
    """Hollow corn-rasp form. Tall thin shell."""
    cx, cy, cz = position_on_shelf(slot)
    # outer shell - tall thin box
    make_box(f"HUSK_shell", (cx, cy, cz + 0.18), (0.08, 0.05, 0.36), color)
    # slight depression at the top (dark inner shadow)
    inner_color = (0.10, 0.08, 0.05, 1.0)
    make_box(f"HUSK_inner", (cx, cy, cz + 0.34), (0.05, 0.03, 0.04), inner_color)


# Dispatch table
DEMON_BUILDERS = {
    "VAGRANT":   build_vagrant,
    "CICADA":    build_cicada,
    "MOTH":      build_moth,
    "STEAMBOAT": build_steamboat,
    "WEIR":      build_weir,
    "FILLY":     build_filly,
    "STARLING":  build_starling,
    "HUSK":      build_husk,
}


# ════════════════════════════════════════════════════════════════
# EXPORT
# ════════════════════════════════════════════════════════════════

def export_glb():
    out_dir = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), OUTPUT_DIR))
    os.makedirs(out_dir, exist_ok=True)
    out_path = os.path.join(out_dir, OUTPUT_NAME)

    print(f"\n[build_agent_figurines] exporting to {out_path}")
    print(f"[build_agent_figurines] scene objects: {len(bpy.context.scene.objects)}")

    bpy.ops.object.select_all(action='SELECT')

    base_kwargs = {
        'filepath': out_path,
        'export_format': 'GLB',
        'use_selection': False,
        'export_apply': True,
    }
    rna = bpy.ops.export_scene.gltf.get_rna_type()
    legacy = {}
    if 'export_colors' in rna.properties: legacy['export_colors'] = True
    if 'export_normals' in rna.properties: legacy['export_normals'] = True

    try:
        result = bpy.ops.export_scene.gltf(**base_kwargs, **legacy)
        print(f"[build_agent_figurines] export result: {result}")
    except Exception as e:
        print(f"[build_agent_figurines] ✗ EXPORT FAILED: {e}")
        import traceback; traceback.print_exc()
        raise

    if os.path.exists(out_path):
        size = os.path.getsize(out_path)
        print(f"[build_agent_figurines] ✓ wrote {out_path} ({size} bytes)")
    else:
        raise RuntimeError("GLB not written")


# ════════════════════════════════════════════════════════════════
# MAIN
# ════════════════════════════════════════════════════════════════

def main():
    clear_scene()
    build_shelf()
    for name, slot, color in DEMONS:
        builder = DEMON_BUILDERS[name]
        builder(slot, color)
    export_glb()


if __name__ == "__main__":
    main()
