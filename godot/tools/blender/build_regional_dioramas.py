"""
build_regional_dioramas.py
══════════════════════════════════════════════════════════════════
COMMUNITY PLANNED · the three regional dioramas as tabletop
miniatures on the Cathedral floor.

Run:
    blender --background --python build_regional_dioramas.py
    (or ./run_cathedral.sh build_regional_dioramas.py)

Output:
    godot/assets/3d/dioramas/regions.glb
    (all three dioramas in one GLB; Godot can split by node name)

Scale: roughly 1:48 tabletop. The miniatures sit on the platforms
defined in build_cathedral_interior.py (Graustark at +5,+2,0; HCE
at +5,-2,0; Small Wood at +5,-5.5,0).

Graustark miniatures:
    · the surviving son's storefront
    · the diner
    · Nicola's house
    · Elicia's bungalow
    · the cathedral (recursive — a tiny warehouse-of-warehouses)
    · the river (a strip of blue)
    · the boat-ghost site (an empty rectangle of pilings)

HCE miniatures:
    · Phase I cul-de-sac (built)
    · Phase II under-occupancy
    · Phase III dirt + surveying flags
    · Lot 47 model home (with the fake basil pot)
    · HOA office
    · community pool

Small Wood miniatures:
    · Wagner's Hardware (corner where Board Lords will be in
      another universe)
    · Petra's mother's bookstore
    · the cannery at the river-mouth (barely operational)
    · God's Thumb (a small bluff)
    · the tower (Dean's, unreachable, in the woods east of town)
      rendered as a tall pylon the player's eye snags on
"""

import bpy
import math
import os
from mathutils import Vector

OUTPUT_DIR = "../../assets/3d/dioramas"
OUTPUT_NAME = "regions.glb"

# Diorama platform centers (must match cathedral_interior.py)
PLAT_GRAU = (5.0,  2.0,  0.30)   # platform top z = 0.30
PLAT_HCE  = (5.0, -2.0,  0.30)
PLAT_SW   = (5.0, -5.5,  0.30)

# Platform dimensions (footprint we have to stay inside)
PLAT_GRAU_SIZE = (4.0, 3.0)
PLAT_HCE_SIZE  = (3.5, 2.5)
PLAT_SW_SIZE   = (3.5, 2.0)

# Lighting (same as everything else)
LIGHT_DIR_COOL = Vector((1.0, 0.0, 0.3)).normalized()
LIGHT_COL_COOL = Vector((0.55, 0.65, 0.80))
LIGHT_DIR_WARM = Vector((0.0, 0.0, 1.0)).normalized()
LIGHT_COL_WARM = Vector((0.95, 0.75, 0.50))
AMBIENT        = Vector((0.10, 0.08, 0.06))


# ── helpers (duplicated for standalone simplicity) ─────────────

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


def make_building(name, center, size, roof_color, wall_color, roof_pitch=0.0):
    """Build a simple two-tone building: walls (box) + flat roof slab."""
    cx, cy, cz = center
    sx, sy, sz = size
    # walls
    make_box(f"{name}_walls", (cx, cy, cz + sz/2), (sx, sy, sz), wall_color)
    # roof slab on top
    roof_h = 0.03 + roof_pitch
    make_box(f"{name}_roof", (cx, cy, cz + sz + roof_h/2), (sx * 1.02, sy * 1.02, roof_h), roof_color)


# ════════════════════════════════════════════════════════════════
# GRAUSTARK · the home region
# ════════════════════════════════════════════════════════════════

def build_graustark():
    gx, gy, gz = PLAT_GRAU
    # the river runs along the west side of the diorama
    make_box("Grau_River",
             (gx - 1.6, gy, gz + 0.01),
             (0.5, 2.8, 0.02),
             base_color=(0.30, 0.42, 0.55, 1.0))

    # the boat-ghost site: a rectangle of small pilings on the river bank
    piling_color = (0.20, 0.15, 0.08, 1.0)
    for i in range(4):
        for j in range(3):
            px = gx - 1.40 + i * 0.10
            py = gy - 0.50 + j * 0.10
            make_box(f"Grau_BoatGhost_piling_{i}_{j}",
                     (px, py, gz + 0.04),
                     (0.018, 0.018, 0.07),
                     base_color=piling_color)
    # a small dock-fragment marker (a low wooden plank floating on the water)
    make_box("Grau_Dock_Fragment",
             (gx - 1.45, gy - 0.45, gz + 0.025),
             (0.20, 0.04, 0.015),
             base_color=(0.45, 0.30, 0.18, 1.0))

    # the surviving son's storefront (replacing the boat — a small clapboard building)
    build_building(
        "Grau_Restaurant",
        center=(gx - 0.9, gy + 0.6, gz),
        size=(0.55, 0.45, 0.30),
        roof_color=(0.32, 0.14, 0.10, 1.0),
        wall_color=(0.78, 0.72, 0.55, 1.0),
    )
    # awning over the front
    make_box("Grau_Restaurant_Awning",
             (gx - 0.9, gy + 0.40, gz + 0.30),
             (0.55, 0.06, 0.02),
             base_color=(0.55, 0.20, 0.18, 1.0))

    # D'Ambrosio's diner (slightly larger, classic-clapboard, brass railings)
    build_building(
        "Grau_Diner",
        center=(gx - 0.3, gy + 0.2, gz),
        size=(0.75, 0.40, 0.28),
        roof_color=(0.25, 0.20, 0.14, 1.0),
        wall_color=(0.82, 0.78, 0.64, 1.0),
    )

    # Nicola's house (residential, smaller, with a porch)
    build_building(
        "Grau_Nicola_House",
        center=(gx + 0.3, gy + 0.7, gz),
        size=(0.45, 0.45, 0.30),
        roof_color=(0.42, 0.22, 0.16, 1.0),
        wall_color=(0.74, 0.66, 0.52, 1.0),
        roof_pitch=0.05,
    )
    # porch
    make_box("Grau_Nicola_Porch",
             (gx + 0.3, gy + 0.50, gz + 0.04),
             (0.45, 0.10, 0.04),
             base_color=(0.50, 0.36, 0.22, 1.0))

    # Elicia's bungalow (small shotgun-style, with a small pomegranate tree)
    build_building(
        "Grau_Elicia_Bungalow",
        center=(gx + 0.9, gy - 0.5, gz),
        size=(0.50, 0.32, 0.22),
        roof_color=(0.32, 0.22, 0.12, 1.0),
        wall_color=(0.80, 0.75, 0.62, 1.0),
    )
    # the pomegranate tree (a small green-red blob)
    make_box("Grau_Pomegranate_Trunk",
             (gx + 0.78, gy - 0.30, gz + 0.04),
             (0.025, 0.025, 0.10),
             base_color=(0.30, 0.20, 0.10, 1.0))
    make_box("Grau_Pomegranate_Canopy",
             (gx + 0.78, gy - 0.30, gz + 0.14),
             (0.10, 0.10, 0.07),
             base_color=(0.32, 0.45, 0.22, 1.0))

    # the Cathedral itself (recursive — a tiny warehouse-of-warehouses)
    build_building(
        "Grau_Cathedral_recursive",
        center=(gx + 1.2, gy + 0.2, gz),
        size=(0.40, 0.30, 0.32),
        roof_color=(0.18, 0.14, 0.09, 1.0),
        wall_color=(0.55, 0.42, 0.28, 1.0),
    )
    # the tall paned river-side window on the cathedral (a small darker rectangle on the wall)
    make_box("Grau_Cathedral_recursive_window",
             (gx + 1.00, gy + 0.20, gz + 0.20),
             (0.005, 0.18, 0.18),
             base_color=(0.20, 0.30, 0.42, 1.0))

    # ground (a thin slab to differentiate from the platform underneath)
    make_box("Grau_Ground",
             (gx + 0.1, gy, gz + 0.005),
             (2.4, 2.8, 0.01),
             base_color=(0.32, 0.26, 0.18, 1.0))


def build_building(name, center, size, roof_color, wall_color, roof_pitch=0.0):
    """Inline-helper that handles building geometry; wraps make_building for one-name use."""
    cx, cy, cz = center
    sx, sy, sz = size
    make_box(f"{name}_walls", (cx, cy, cz + sz/2), (sx, sy, sz), wall_color)
    roof_h = 0.03 + roof_pitch
    make_box(f"{name}_roof", (cx, cy, cz + sz + roof_h/2), (sx * 1.02, sy * 1.02, roof_h), roof_color)


# ════════════════════════════════════════════════════════════════
# HCE · the engineered front
# ════════════════════════════════════════════════════════════════

def build_hce():
    hx, hy, hz = PLAT_HCE
    # ground (the planned-community uniform lawn)
    make_box("HCE_Ground",
             (hx, hy, hz + 0.005),
             (3.4, 2.4, 0.01),
             base_color=(0.45, 0.55, 0.30, 1.0))

    # Phase I (north end, completed — five small uniform houses)
    for i in range(5):
        px = hx - 1.3 + i * 0.30
        build_building(
            f"HCE_PhaseI_house_{i}",
            center=(px, hy + 0.75, hz),
            size=(0.22, 0.20, 0.22),
            roof_color=(0.45, 0.30, 0.20, 1.0),
            wall_color=(0.85, 0.80, 0.70, 1.0),
        )

    # Phase II (middle, partially built — three with one missing)
    for i, present in enumerate([True, True, False, True, True]):
        if not present:
            continue
        px = hx - 1.3 + i * 0.30
        # framing-only (no roof, smaller walls)
        make_box(
            f"HCE_PhaseII_frame_{i}",
            (px, hy + 0.15, hz + 0.12),
            (0.22, 0.20, 0.24),
            base_color=(0.62, 0.50, 0.32, 1.0),
        )

    # Phase III (south end, dirt + surveying flags)
    make_box("HCE_PhaseIII_dirt",
             (hx, hy - 0.55, hz + 0.012),
             (2.6, 0.50, 0.02),
             base_color=(0.42, 0.30, 0.18, 1.0))
    # surveying flags (small orange triangular flags on thin stakes)
    flag_color = (0.92, 0.45, 0.20, 1.0)
    stake_color = (0.20, 0.18, 0.14, 1.0)
    for i in range(7):
        fx = hx - 1.2 + i * 0.35
        fy = hy - 0.55 + (0.15 if i % 2 == 0 else -0.15)
        make_box(f"HCE_Flag_stake_{i}", (fx, fy, hz + 0.07),
                 (0.008, 0.008, 0.10), stake_color)
        make_box(f"HCE_Flag_{i}", (fx + 0.012, fy, hz + 0.12),
                 (0.012, 0.004, 0.030), flag_color)

    # Lot 47 model home (south of Phase III; THE model home)
    build_building(
        "HCE_Lot47_Model",
        center=(hx + 1.0, hy - 0.95, hz),
        size=(0.45, 0.35, 0.30),
        roof_color=(0.32, 0.22, 0.14, 1.0),
        wall_color=(0.92, 0.86, 0.74, 1.0),
    )
    # the (fake) basil pot at the kitchen window — Mackenzie's slow-witness intel
    make_box("HCE_Lot47_FakeBasil_pot",
             (hx + 1.20, hy - 0.85, hz + 0.28),
             (0.022, 0.022, 0.04),
             base_color=(0.62, 0.50, 0.34, 1.0))
    make_box("HCE_Lot47_FakeBasil_leaves",
             (hx + 1.20, hy - 0.85, hz + 0.34),
             (0.040, 0.040, 0.05),
             # slightly too saturated green — that's the tell
             base_color=(0.30, 0.62, 0.25, 1.0))

    # HOA office (small, official, with a stubby clock-tower)
    build_building(
        "HCE_HOA_Office",
        center=(hx - 1.3, hy + 0.05, hz),
        size=(0.45, 0.40, 0.32),
        roof_color=(0.30, 0.22, 0.16, 1.0),
        wall_color=(0.80, 0.74, 0.60, 1.0),
    )
    # the stubby clock-tower
    make_box("HCE_HOA_Tower",
             (hx - 1.3, hy + 0.05, hz + 0.45),
             (0.10, 0.10, 0.16),
             base_color=(0.78, 0.70, 0.55, 1.0))

    # community pool (a small blue rectangle on the ground)
    make_box("HCE_Pool",
             (hx + 0.30, hy + 0.30, hz + 0.013),
             (0.30, 0.20, 0.005),
             base_color=(0.30, 0.55, 0.72, 1.0))


# ════════════════════════════════════════════════════════════════
# SMALL WOOD · the front
# ════════════════════════════════════════════════════════════════

def build_smallwood():
    sx, sy, sz = PLAT_SW
    # ground (cooler, damper — PNW)
    make_box("SW_Ground",
             (sx, sy, sz + 0.005),
             (3.4, 1.9, 0.01),
             base_color=(0.30, 0.32, 0.24, 1.0))

    # Wagner's Hardware (corner store)
    build_building(
        "SW_Wagners",
        center=(sx - 1.1, sy + 0.4, sz),
        size=(0.45, 0.35, 0.28),
        roof_color=(0.30, 0.22, 0.14, 1.0),
        wall_color=(0.62, 0.52, 0.38, 1.0),
    )
    # Wagner's sign (a thin slab over the door)
    make_box("SW_Wagners_sign",
             (sx - 1.10, sy + 0.22, sz + 0.30),
             (0.30, 0.025, 0.06),
             base_color=(0.42, 0.32, 0.20, 1.0))

    # Petra's mother's bookstore (smaller, narrower)
    build_building(
        "SW_Bookstore",
        center=(sx - 0.5, sy + 0.4, sz),
        size=(0.30, 0.32, 0.26),
        roof_color=(0.42, 0.30, 0.20, 1.0),
        wall_color=(0.72, 0.60, 0.40, 1.0),
    )

    # the cannery at the river-mouth (long, low, weather-grey)
    cannery_color = (0.52, 0.50, 0.45, 1.0)
    make_box("SW_Cannery_walls",
             (sx + 0.4, sy + 0.6, sz + 0.10),
             (1.20, 0.30, 0.20),
             cannery_color)
    # corrugated tin roof (slightly darker)
    make_box("SW_Cannery_roof",
             (sx + 0.4, sy + 0.6, sz + 0.21),
             (1.22, 0.31, 0.025),
             base_color=(0.30, 0.32, 0.28, 1.0))
    # small loading dock at the river end
    make_box("SW_Cannery_Dock",
             (sx + 1.05, sy + 0.6, sz + 0.05),
             (0.18, 0.20, 0.05),
             base_color=(0.40, 0.28, 0.18, 1.0))

    # God's Thumb (a small bluff — a rocky bump)
    make_box("SW_GodsThumb_base",
             (sx + 1.20, sy - 0.55, sz + 0.06),
             (0.30, 0.25, 0.12),
             base_color=(0.40, 0.38, 0.32, 1.0))
    make_box("SW_GodsThumb_cap",
             (sx + 1.20, sy - 0.55, sz + 0.16),
             (0.22, 0.20, 0.08),
             base_color=(0.35, 0.34, 0.28, 1.0))

    # ── THE TOWER ── (Dean's, unreachable, in the woods east of town)
    # rendered as a tall narrow pylon the eye snags on — DELIBERATELY
    # taller than anything else on the diorama. ~3x the other heights.
    tower_x = sx + 1.50
    tower_y = sy + 0.10
    # base (chunky concrete plinth)
    make_box("SW_Tower_base",
             (tower_x, tower_y, sz + 0.04),
             (0.12, 0.12, 0.08),
             base_color=(0.30, 0.28, 0.22, 1.0))
    # tower shaft (very tall, slightly tapered — three stacked boxes)
    tower_color = (0.18, 0.16, 0.14, 1.0)
    make_box("SW_Tower_shaft_lower",
             (tower_x, tower_y, sz + 0.30),
             (0.07, 0.07, 0.40),
             tower_color)
    make_box("SW_Tower_shaft_mid",
             (tower_x, tower_y, sz + 0.65),
             (0.055, 0.055, 0.30),
             tower_color)
    make_box("SW_Tower_shaft_upper",
             (tower_x, tower_y, sz + 0.92),
             (0.045, 0.045, 0.22),
             tower_color)
    # tower beacon (a faintly glowing top — the "brightness" the player tracks)
    make_box("SW_Tower_beacon",
             (tower_x, tower_y, sz + 1.05),
             (0.06, 0.06, 0.05),
             base_color=(0.85, 0.65, 0.35, 1.0))   # warm beacon (will be modulated per-week in game)

    # the road from Wagner's into town (a thin strip)
    make_box("SW_Road",
             (sx - 0.3, sy - 0.3, sz + 0.011),
             (1.6, 0.10, 0.01),
             base_color=(0.22, 0.20, 0.18, 1.0))

    # a few scattered fir-tree miniatures (the PNW texture)
    tree_color_a = (0.18, 0.28, 0.16, 1.0)
    tree_color_b = (0.16, 0.24, 0.14, 1.0)
    tree_positions = [
        (sx + 0.95, sy - 0.30, tree_color_a),
        (sx + 0.65, sy - 0.55, tree_color_b),
        (sx + 0.05, sy - 0.55, tree_color_a),
        (sx - 0.65, sy - 0.45, tree_color_b),
        (sx - 1.45, sy - 0.30, tree_color_a),
        (sx + 0.35, sy + 0.10, tree_color_b),
    ]
    for i, (tx, ty, tc) in enumerate(tree_positions):
        # trunk
        make_box(f"SW_Tree_{i}_trunk",
                 (tx, ty, sz + 0.04),
                 (0.012, 0.012, 0.07),
                 base_color=(0.20, 0.14, 0.08, 1.0))
        # canopy (a small conical box stack)
        make_box(f"SW_Tree_{i}_canopy_lower",
                 (tx, ty, sz + 0.13),
                 (0.08, 0.08, 0.07),
                 tc)
        make_box(f"SW_Tree_{i}_canopy_upper",
                 (tx, ty, sz + 0.18),
                 (0.055, 0.055, 0.05),
                 tc)


# ════════════════════════════════════════════════════════════════
# EXPORT
# ════════════════════════════════════════════════════════════════

def export_glb():
    out_dir = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), OUTPUT_DIR))
    os.makedirs(out_dir, exist_ok=True)
    out_path = os.path.join(out_dir, OUTPUT_NAME)

    print(f"\n[build_regional_dioramas] exporting to {out_path}")
    print(f"[build_regional_dioramas] scene objects: {len(bpy.context.scene.objects)}")

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
        print(f"[build_regional_dioramas] export result: {result}")
    except Exception as e:
        print(f"[build_regional_dioramas] ✗ EXPORT FAILED: {e}")
        import traceback; traceback.print_exc()
        raise

    if os.path.exists(out_path):
        size = os.path.getsize(out_path)
        print(f"[build_regional_dioramas] ✓ wrote {out_path} ({size} bytes)")
    else:
        raise RuntimeError("GLB not written")


def main():
    clear_scene()
    build_graustark()
    build_hce()
    build_smallwood()
    export_glb()


if __name__ == "__main__":
    main()
