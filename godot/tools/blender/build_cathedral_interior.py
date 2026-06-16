"""
build_cathedral_interior.py
══════════════════════════════════════════════════════════════════
COMMUNITY PLANNED · the warehouse cathedral interior
Procedural low-poly mesh for the first-person 3D walkthrough.

Run:
    blender --background --python build_cathedral_interior.py

Output:
    godot/assets/3d/cathedral/cathedral_interior.glb

Edit the CONSTANTS section to vary the build. Re-run, get the new
mesh. Deterministic.

Aesthetic lock:
    · ~5k triangles total
    · Vertex colors carry the Gouraud lighting term
    · One main directional light (river-window cool blue from -X)
    · One warm fill (workbench lamp from +Y, low intensity)
    · No real-time shadows; per-vertex Lambertian only

Constants are in MM-canon project units (1 unit = 1 meter).
The warehouse is ~24m × 18m × 7m — roughly true to a 1920s
single-story river-bank warehouse.
"""

import bpy
import bmesh
import math
import os
from mathutils import Vector

# ════════════════════════════════════════════════════════════════
# CONSTANTS · edit these to vary the build
# ════════════════════════════════════════════════════════════════

OUTPUT_DIR = "../../assets/3d/cathedral"   # relative to this script's dir
OUTPUT_NAME = "cathedral_interior.glb"

# warehouse dimensions (meters)
WH_W = 24.0   # width  (east-west, +X is east, river is -X)
WH_D = 18.0   # depth  (north-south)
WH_H = 7.0    # ceiling height

# the river window
WIN_W = 6.0   # width of the tall paned window on the river-side wall (-X)
WIN_H = 4.5   # window height
WIN_BASE = 1.0  # height of the window bottom from the floor

# the freight bay door (+X side)
BAY_W = 4.0
BAY_H = 4.0

# workbench
WB_W = 2.4
WB_D = 0.9
WB_H = 0.9
WB_POS = (0.0, -3.0, 0.0)    # near the river-window side, slightly south

# BBS terminal desk
BBS_W = 1.2
BBS_D = 0.7
BBS_H = 0.75
BBS_POS = (-WH_W/2 + 1.5, 5.0, 0.0)   # corner near the river-window wall

# diorama bases (low platforms on the floor)
DIO_BASES = [
    ("graustark",   (5.0,  2.0, 0.0), 4.0, 3.0, 0.15),
    ("hce",         (5.0, -2.0, 0.0), 3.5, 2.5, 0.15),
    ("smallwood",   (5.0, -5.5, 0.0), 3.5, 2.0, 0.15),
]

# colors (rgba 0-1) — match the project palette
COL_FLOOR    = (0.16, 0.13, 0.08, 1.0)   # warm concrete
COL_FLOOR_DARK = (0.10, 0.08, 0.05, 1.0) # darker stain stripes
COL_FLOOR_SEAM = (0.06, 0.05, 0.03, 1.0) # joint between slabs
COL_WALL     = (0.20, 0.16, 0.10, 1.0)   # warm brick interior
COL_WALL_DARK = (0.14, 0.10, 0.07, 1.0)  # darker brick courses
COL_PILASTER = (0.22, 0.18, 0.12, 1.0)   # raised brick column accent
COL_CEILING  = (0.10, 0.07, 0.04, 1.0)   # dark corrugated tin
COL_TRUSS    = (0.30, 0.27, 0.22, 1.0)   # steel roof truss
COL_RAFTER   = (0.18, 0.14, 0.10, 1.0)   # dark wood / steel cross-tie
COL_BEAM_LIT = (0.42, 0.36, 0.28, 1.0)   # catches the sun
COL_WB_TOP   = (0.45, 0.30, 0.16, 1.0)   # warm wood
COL_WB_LEG   = (0.18, 0.12, 0.06, 1.0)   # dark wood
COL_BBS_DESK = (0.30, 0.20, 0.10, 1.0)
COL_DIORAMA  = (0.50, 0.42, 0.28, 1.0)   # paper-toned platform

# lighting term direction (used to bake Gouraud vertex colors)
# the cool light comes from the river side (-X), the warm fill from above (+Z)
LIGHT_DIR_COOL = Vector((1.0, 0.0, 0.3)).normalized()    # vector AT lit normals
LIGHT_COL_COOL = Vector((0.55, 0.65, 0.80))              # cool blue
LIGHT_DIR_WARM = Vector((0.0, 0.0, 1.0)).normalized()
LIGHT_COL_WARM = Vector((0.95, 0.75, 0.50))              # warm bulb
AMBIENT        = Vector((0.10, 0.08, 0.06))              # warehouse ambient


# ════════════════════════════════════════════════════════════════
# HELPERS
# ════════════════════════════════════════════════════════════════

def clear_scene():
    """Remove all default objects so the script is deterministic."""
    bpy.ops.object.select_all(action='SELECT')
    bpy.ops.object.delete(use_global=False)
    # Also clear orphan data
    for collection in (bpy.data.meshes, bpy.data.materials, bpy.data.images):
        for item in list(collection):
            if item.users == 0:
                collection.remove(item)


def gouraud_term(normal, base_rgba):
    """
    Bake the Gouraud Lambertian lighting term into a vertex color.
    Returns (r, g, b, a).
    """
    n = Vector(normal).normalized()
    cool = max(0.0, n.dot(LIGHT_DIR_COOL))
    warm = max(0.0, n.dot(LIGHT_DIR_WARM))
    light = Vector((
        AMBIENT.x + LIGHT_COL_COOL.x * cool + LIGHT_COL_WARM.x * warm * 0.4,
        AMBIENT.y + LIGHT_COL_COOL.y * cool + LIGHT_COL_WARM.y * warm * 0.4,
        AMBIENT.z + LIGHT_COL_COOL.z * cool + LIGHT_COL_WARM.z * warm * 0.4,
    ))
    r = min(1.0, base_rgba[0] * light.x)
    g = min(1.0, base_rgba[1] * light.y)
    b = min(1.0, base_rgba[2] * light.z)
    return (r, g, b, base_rgba[3])


def make_box(name, center, size, base_color, open_faces=None):
    """
    Build a box mesh with per-vertex Gouraud colors baked in.
    open_faces is a set of {'+X','-X','+Y','-Y','+Z','-Z'} faces to omit.
    Returns the created object.
    """
    open_faces = open_faces or set()
    cx, cy, cz = center
    sx, sy, sz = size
    hx, hy, hz = sx/2, sy/2, sz/2

    # 8 corner vertices
    verts = [
        (cx - hx, cy - hy, cz - hz),  # 0  -X -Y -Z
        (cx + hx, cy - hy, cz - hz),  # 1  +X -Y -Z
        (cx + hx, cy + hy, cz - hz),  # 2  +X +Y -Z
        (cx - hx, cy + hy, cz - hz),  # 3  -X +Y -Z
        (cx - hx, cy - hy, cz + hz),  # 4  -X -Y +Z
        (cx + hx, cy - hy, cz + hz),  # 5  +X -Y +Z
        (cx + hx, cy + hy, cz + hz),  # 6  +X +Y +Z
        (cx - hx, cy + hy, cz + hz),  # 7  -X +Y +Z
    ]

    # 6 faces, each with its outward normal
    face_defs = [
        ('-Z', (0,3,2,1), ( 0, 0,-1)),  # bottom
        ('+Z', (4,5,6,7), ( 0, 0, 1)),  # top
        ('-Y', (0,1,5,4), ( 0,-1, 0)),  # south
        ('+Y', (2,3,7,6), ( 0, 1, 0)),  # north
        ('-X', (3,0,4,7), (-1, 0, 0)),  # west (river side)
        ('+X', (1,2,6,5), ( 1, 0, 0)),  # east (bay door side)
    ]

    mesh = bpy.data.meshes.new(name + "_mesh")

    out_verts = []
    out_faces = []
    out_colors = []
    vmap = {}

    def vidx(v_orig, normal):
        # Per-face vertices so Gouraud can vary by face-normal (flat-ish smoothing).
        # For true Gouraud smoothing across edges, merge by position and average normals.
        # Here we keep it flat-per-face for the slightly chunkier mid-90s look.
        key = (v_orig, tuple(normal))
        if key in vmap:
            return vmap[key]
        idx = len(out_verts)
        out_verts.append(verts[v_orig])
        out_colors.append(gouraud_term(normal, base_color))
        vmap[key] = idx
        return idx

    for tag, vids, normal in face_defs:
        if tag in open_faces:
            continue
        face = [vidx(v, normal) for v in vids]
        out_faces.append(face)

    mesh.from_pydata(out_verts, [], out_faces)
    mesh.update()

    # Apply vertex colors
    if not mesh.vertex_colors:
        mesh.vertex_colors.new(name="Col")
    color_layer = mesh.vertex_colors["Col"]
    li = 0
    for poly in mesh.polygons:
        for loop_index in poly.loop_indices:
            v = mesh.loops[loop_index].vertex_index
            color_layer.data[loop_index].color = out_colors[v]
            li += 1

    obj = bpy.data.objects.new(name, mesh)
    bpy.context.collection.objects.link(obj)
    return obj


def make_window_cutout(wall_obj, x, y_base, w, h, depth_normal):
    """
    Boolean-cutout a rectangular window from a wall.
    For a procedural low-poly look we'll instead reshape: the wall
    becomes 8 small quads around the opening. Simpler and cheaper.
    Skipped in v1 — the river window is created as a separate
    geometry hint (a thin "window frame" prop) and the wall stays
    closed. Visual fidelity for the prototype is sufficient.
    """
    pass


# ════════════════════════════════════════════════════════════════
# BUILD STEPS
# ════════════════════════════════════════════════════════════════

def build_warehouse_shell():
    """The outer box: floor, ceiling, four walls. Built as one open box."""
    # Floor (one flat box at z=0, very thin slab)
    make_box(
        "Floor",
        center=(0, 0, -0.05),
        size=(WH_W, WH_D, 0.1),
        base_color=COL_FLOOR,
        open_faces={'-Z'},  # don't see the underside
    )

    # Ceiling
    make_box(
        "Ceiling",
        center=(0, 0, WH_H + 0.05),
        size=(WH_W, WH_D, 0.1),
        base_color=COL_CEILING,
        open_faces={'+Z'},
    )

    # Four walls — built as four thin boxes
    wall_thickness = 0.2
    # West wall (river side, -X) — has the river window cutout (faked by smaller wall)
    make_box(
        "Wall_W_lower",
        center=(-WH_W/2 - wall_thickness/2, 0, WIN_BASE/2),
        size=(wall_thickness, WH_D, WIN_BASE),
        base_color=COL_WALL,
    )
    make_box(
        "Wall_W_upper",
        center=(-WH_W/2 - wall_thickness/2, 0, (WH_H + WIN_BASE + WIN_H)/2),
        size=(wall_thickness, WH_D, WH_H - (WIN_BASE + WIN_H)),
        base_color=COL_WALL,
    )
    # West wall: north and south of the window
    side_d = (WH_D - WIN_W) / 2
    make_box(
        "Wall_W_south_of_window",
        center=(-WH_W/2 - wall_thickness/2, -WH_D/2 + side_d/2, (WIN_BASE + WIN_H/2)),
        size=(wall_thickness, side_d, WIN_H),
        base_color=COL_WALL,
    )
    make_box(
        "Wall_W_north_of_window",
        center=(-WH_W/2 - wall_thickness/2, WH_D/2 - side_d/2, (WIN_BASE + WIN_H/2)),
        size=(wall_thickness, side_d, WIN_H),
        base_color=COL_WALL,
    )

    # East wall (+X) — has the freight bay door (left open in mesh; door is a separate prop)
    bay_d_offset = WH_D/2 - BAY_W/2  # bay door positioned at south end
    make_box(
        "Wall_E_north_of_bay",
        center=(WH_W/2 + wall_thickness/2, BAY_W/2, WH_H/2),
        size=(wall_thickness, WH_D - BAY_W, WH_H),
        base_color=COL_WALL,
    )
    make_box(
        "Wall_E_above_bay",
        center=(WH_W/2 + wall_thickness/2, -WH_D/2 + BAY_W/2, BAY_H + (WH_H - BAY_H)/2),
        size=(wall_thickness, BAY_W, WH_H - BAY_H),
        base_color=COL_WALL,
    )

    # South wall (-Y) — solid
    make_box(
        "Wall_S",
        center=(0, -WH_D/2 - wall_thickness/2, WH_H/2),
        size=(WH_W, wall_thickness, WH_H),
        base_color=COL_WALL,
    )

    # North wall (+Y) — solid
    make_box(
        "Wall_N",
        center=(0, WH_D/2 + wall_thickness/2, WH_H/2),
        size=(WH_W, wall_thickness, WH_H),
        base_color=COL_WALL,
    )


def build_floor_seams():
    """Concrete-slab seams + a darker stain stripe band running
    east-west. Gives the floor a 'this is a real warehouse' read
    rather than one flat plane."""
    # 5 long seam lines running N-S across the floor (slab joints)
    seam_w = 0.05
    seam_z = 0.02   # just above the floor box
    for i in range(5):
        x = -WH_W/2 + (i + 1) * (WH_W / 6.0)
        make_box(
            f"Floor_Seam_NS_{i}",
            center=(x, 0, seam_z),
            size=(seam_w, WH_D - 0.4, 0.04),
            base_color=COL_FLOOR_SEAM,
        )
    # 3 cross seams running E-W
    for j in range(3):
        y = -WH_D/2 + (j + 1) * (WH_D / 4.0)
        make_box(
            f"Floor_Seam_EW_{j}",
            center=(0, y, seam_z),
            size=(WH_W - 0.4, seam_w, 0.04),
            base_color=COL_FLOOR_SEAM,
        )
    # Two darker stain stripes (where machinery dragged) running
    # E-W under the central workbench area + the BBS desk
    for label, sy in [("WB_stripe", -3.0), ("BBS_stripe", 5.0)]:
        make_box(
            f"Floor_Stain_{label}",
            center=(0, sy, 0.015),
            size=(WH_W - 1.0, 0.30, 0.03),
            base_color=COL_FLOOR_DARK,
        )


def build_brick_courses():
    """Horizontal stripes on the long walls — every 1m a slightly
    darker brick course. Gives the wall surface texture without
    actual brick-by-brick geometry."""
    course_t = 0.06
    n_courses = int(WH_H / 1.0)
    for ci in range(1, n_courses):
        cz = ci * 1.0
        # On the south wall (-Y) — inside face at -WH_D/2
        make_box(
            f"Course_S_{ci}",
            center=(0, -WH_D/2 + 0.05, cz),
            size=(WH_W - 0.2, 0.05, course_t),
            base_color=COL_WALL_DARK,
        )
        # On the north wall (+Y) — inside face at +WH_D/2
        make_box(
            f"Course_N_{ci}",
            center=(0, WH_D/2 - 0.05, cz),
            size=(WH_W - 0.2, 0.05, course_t),
            base_color=COL_WALL_DARK,
        )
        # On the east wall (+X) — skip the bay door region
        make_box(
            f"Course_E_{ci}",
            center=(WH_W/2 - 0.05, BAY_W/2 + 0.5, cz),
            size=(0.05, (WH_D - BAY_W) - 1.0, course_t),
            base_color=COL_WALL_DARK,
        )


def build_pilasters():
    """Vertical brick column accents on the long walls — gives the
    wall surface depth + suggests structural support inside the
    warehouse shell."""
    pilaster_thick = 0.24
    pilaster_depth = 0.18   # how far it projects from the wall
    pilaster_h = WH_H - 0.4
    # 5 pilasters along the south wall
    for i in range(5):
        x = -WH_W/2 + (i + 1) * (WH_W / 6.0)
        make_box(
            f"Pilaster_S_{i}",
            center=(x, -WH_D/2 + pilaster_depth/2 + 0.05, pilaster_h/2 + 0.1),
            size=(pilaster_thick, pilaster_depth, pilaster_h),
            base_color=COL_PILASTER,
        )
        # Capital block on top
        make_box(
            f"Pilaster_S_Cap_{i}",
            center=(x, -WH_D/2 + pilaster_depth/2 + 0.05,
                    pilaster_h + 0.20),
            size=(pilaster_thick + 0.10, pilaster_depth + 0.10, 0.20),
            base_color=COL_WALL_DARK,
        )
    # 5 on the north wall
    for i in range(5):
        x = -WH_W/2 + (i + 1) * (WH_W / 6.0)
        make_box(
            f"Pilaster_N_{i}",
            center=(x, WH_D/2 - pilaster_depth/2 - 0.05, pilaster_h/2 + 0.1),
            size=(pilaster_thick, pilaster_depth, pilaster_h),
            base_color=COL_PILASTER,
        )
        make_box(
            f"Pilaster_N_Cap_{i}",
            center=(x, WH_D/2 - pilaster_depth/2 - 0.05,
                    pilaster_h + 0.20),
            size=(pilaster_thick + 0.10, pilaster_depth + 0.10, 0.20),
            base_color=COL_WALL_DARK,
        )


def build_roof_trusses():
    """Steel roof trusses spanning the warehouse north-south at
    each pilaster pair. Top chord + bottom chord + 4 verticals +
    2 diagonals per truss. Defines the 'cathedral' feel."""
    truss_top_z = WH_H - 0.15
    truss_bot_z = WH_H - 1.2
    chord_t = 0.10
    # 5 trusses, one each pilaster pair
    for i in range(5):
        x = -WH_W/2 + (i + 1) * (WH_W / 6.0)
        # Top chord (against the ceiling)
        make_box(
            f"Truss_{i}_TopChord",
            center=(x, 0, truss_top_z),
            size=(chord_t, WH_D - 0.5, chord_t),
            base_color=COL_TRUSS,
        )
        # Bottom chord (hanging in space)
        make_box(
            f"Truss_{i}_BotChord",
            center=(x, 0, truss_bot_z),
            size=(chord_t, WH_D - 0.5, chord_t),
            base_color=COL_TRUSS,
        )
        # 5 verticals between chords
        for v in range(5):
            t = -1 + 2 * v / 4
            vy = t * (WH_D / 2 - 0.6)
            make_box(
                f"Truss_{i}_Vert_{v}",
                center=(x, vy, (truss_top_z + truss_bot_z) / 2),
                size=(chord_t, chord_t,
                      truss_top_z - truss_bot_z),
                base_color=COL_TRUSS,
            )
        # 4 diagonals (alternating direction)
        for v in range(4):
            t = -1 + (2 * v + 1) / 4
            vy = t * (WH_D / 2 - 0.6)
            make_box(
                f"Truss_{i}_Diag_{v}",
                center=(x, vy, (truss_top_z + truss_bot_z) / 2),
                size=(chord_t, (WH_D - 0.5) / 4 * 1.05, chord_t),
                base_color=COL_TRUSS,
            )


def build_hanging_fixtures():
    """Two industrial work-lamp pendants hanging from the trusses.
    Cone shade + bulb sphere + chain. The lamp shine is provided
    by Light3D nodes in the .tscn; this is just the visible
    fixture geometry."""
    # 2 lamps hanging at the workbench area and the BBS desk
    for label, (lx, ly, drop_h) in [
        ("WB_Lamp",  (0.0, -3.0, 2.4)),
        ("BBS_Lamp", (-WH_W/2 + 1.5, 5.0, 2.6)),
    ]:
        # Chain (single thin box)
        chain_top_z = WH_H - 0.4
        chain_bot_z = WH_H - drop_h
        make_box(
            f"{label}_Chain",
            center=(lx, ly, (chain_top_z + chain_bot_z) / 2),
            size=(0.04, 0.04, chain_top_z - chain_bot_z),
            base_color=COL_TRUSS,
        )
        # Cone shade
        make_box(
            f"{label}_Shade",
            center=(lx, ly, chain_bot_z - 0.15),
            size=(0.45, 0.45, 0.30),
            base_color=COL_RAFTER,
        )
        # Bulb (small yellow box hanging below the shade)
        make_box(
            f"{label}_Bulb",
            center=(lx, ly, chain_bot_z - 0.42),
            size=(0.12, 0.12, 0.15),
            base_color=(0.92, 0.84, 0.42, 1.0),
        )


def build_river_window_frame():
    """Iron-strut frame on the outside of the river window. Thin black slats."""
    strut_w = 0.08
    strut_d = 0.08
    # vertical struts (3 of them dividing the window into 2 panels)
    for i in range(1, 3):
        x = -WH_W/2 - 0.05
        y = -WIN_W/2 + (WIN_W / 3) * i
        make_box(
            f"Strut_V_{i}",
            center=(x, y, WIN_BASE + WIN_H/2),
            size=(strut_d, strut_w, WIN_H),
            base_color=(0.04, 0.03, 0.02, 1.0),
        )
    # horizontal struts (2 of them dividing the window vertically)
    for i in range(1, 3):
        x = -WH_W/2 - 0.05
        z = WIN_BASE + (WIN_H / 3) * i
        make_box(
            f"Strut_H_{i}",
            center=(x, 0, z),
            size=(strut_d, WIN_W, strut_w),
            base_color=(0.04, 0.03, 0.02, 1.0),
        )


def build_workbench():
    """Frasier's workbench. Tabletop + four legs."""
    x, y, z = WB_POS
    # Tabletop
    make_box(
        "Workbench_Top",
        center=(x, y, WB_H + 0.04),
        size=(WB_W, WB_D, 0.08),
        base_color=COL_WB_TOP,
    )
    # Four legs
    leg_w = 0.08
    for dx in (-1, 1):
        for dy in (-1, 1):
            lx = x + dx * (WB_W/2 - leg_w)
            ly = y + dy * (WB_D/2 - leg_w)
            make_box(
                f"Workbench_Leg_{dx}_{dy}",
                center=(lx, ly, WB_H/2),
                size=(leg_w, leg_w, WB_H),
                base_color=COL_WB_LEG,
            )


def build_bbs_terminal():
    """The phosphor-green CRT desk in the corner."""
    x, y, z = BBS_POS
    # Desk surface
    make_box(
        "BBS_Desk_Top",
        center=(x, y, BBS_H + 0.04),
        size=(BBS_W, BBS_D, 0.08),
        base_color=COL_BBS_DESK,
    )
    # Desk legs
    leg_w = 0.07
    for dx in (-1, 1):
        for dy in (-1, 1):
            lx = x + dx * (BBS_W/2 - leg_w)
            ly = y + dy * (BBS_D/2 - leg_w)
            make_box(
                f"BBS_Desk_Leg_{dx}_{dy}",
                center=(lx, ly, BBS_H/2),
                size=(leg_w, leg_w, BBS_H),
                base_color=COL_WB_LEG,
            )
    # CRT monitor body (chunky beige box)
    crt_w, crt_d, crt_h = 0.45, 0.42, 0.40
    make_box(
        "BBS_CRT",
        center=(x, y, BBS_H + crt_h/2 + 0.08),
        size=(crt_w, crt_d, crt_h),
        base_color=(0.55, 0.50, 0.40, 1.0),    # period-correct beige
    )
    # The screen itself — a thin phosphor-green slab in front of the CRT
    make_box(
        "BBS_Screen",
        center=(x, y - crt_d/2 - 0.01, BBS_H + crt_h/2 + 0.08),
        size=(0.34, 0.02, 0.27),
        base_color=(0.18, 0.40, 0.18, 1.0),    # darkened phosphor (the shader can self-emit)
    )
    # The keyboard — a chunky flat box in front of the CRT on the desk
    make_box(
        "BBS_Keyboard",
        center=(x, y - 0.20, BBS_H + 0.10),
        size=(0.45, 0.18, 0.04),
        base_color=(0.45, 0.40, 0.32, 1.0),
    )


def build_diorama_bases():
    """Low platforms for the three regional strategic-map dioramas."""
    for name, pos, w, d, h in DIO_BASES:
        x, y, z = pos
        make_box(
            f"Diorama_{name}",
            center=(x, y, z + h/2),
            size=(w, d, h),
            base_color=COL_DIORAMA,
        )


def add_lights():
    """Place the actual scene lights (in addition to baked vertex Gouraud)."""
    # River-window directional light (cool blue)
    light_data = bpy.data.lights.new(name="RiverLight", type='SUN')
    light_data.energy = 1.6
    light_data.color = (0.55, 0.70, 0.95)
    light_data.angle = math.radians(20)
    light = bpy.data.objects.new(name="RiverLight", object_data=light_data)
    light.location = (-WH_W, 0, WH_H * 1.5)
    light.rotation_euler = (math.radians(60), math.radians(-30), 0)
    bpy.context.collection.objects.link(light)

    # Workbench lamp (warm point light)
    light_data2 = bpy.data.lights.new(name="WorkbenchLamp", type='POINT')
    light_data2.energy = 60.0
    light_data2.color = (0.98, 0.78, 0.55)
    light_data2.shadow_soft_size = 0.5
    light2 = bpy.data.objects.new(name="WorkbenchLamp", object_data=light_data2)
    light2.location = (WB_POS[0], WB_POS[1], WB_POS[2] + 1.6)
    bpy.context.collection.objects.link(light2)

    # BBS phosphor glow (small green point light at the screen)
    light_data3 = bpy.data.lights.new(name="BBSGlow", type='POINT')
    light_data3.energy = 8.0
    light_data3.color = (0.40, 0.85, 0.45)
    light_data3.shadow_soft_size = 0.2
    light3 = bpy.data.objects.new(name="BBSGlow", object_data=light_data3)
    light3.location = (BBS_POS[0], BBS_POS[1] - 0.40, BBS_POS[2] + 1.10)
    bpy.context.collection.objects.link(light3)


def setup_camera_hint():
    """Spawn-point hint: a camera at Frasier's eye height near the door."""
    cam_data = bpy.data.cameras.new(name="FrasierEye")
    cam_data.lens = 35
    cam = bpy.data.objects.new("FrasierEye", cam_data)
    cam.location = (WH_W/2 - 2.0, -WH_D/2 + 2.0, 1.65)  # roughly inside the bay door
    cam.rotation_euler = (math.radians(85), 0, math.radians(135))  # facing inward
    bpy.context.collection.objects.link(cam)


def export_glb():
    out_dir = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), OUTPUT_DIR))
    os.makedirs(out_dir, exist_ok=True)
    out_path = os.path.join(out_dir, OUTPUT_NAME)

    print(f"\n[build_cathedral_interior] exporting to {out_path}")
    print(f"[build_cathedral_interior] scene objects: {len(bpy.context.scene.objects)}")

    bpy.ops.object.select_all(action='SELECT')

    # Build kwargs that work across Blender 3.6 and Blender 4.x.
    # Blender 4.0 removed `export_colors` and `export_normals`; both are
    # now defaults. Vertex colors export automatically when present.
    base_kwargs = {
        'filepath': out_path,
        'export_format': 'GLB',
        'use_selection': False,
        'export_apply': True,
        'export_lights': True,
        'export_cameras': False,   # was True; cameras hijack Godot's active camera
    }

    # Probe the operator's available properties so we add legacy flags
    # only on Blender 3.x.
    rna = bpy.ops.export_scene.gltf.get_rna_type()
    legacy_kwargs = {}
    if 'export_colors' in rna.properties:
        legacy_kwargs['export_colors'] = True
    if 'export_normals' in rna.properties:
        legacy_kwargs['export_normals'] = True

    try:
        result = bpy.ops.export_scene.gltf(**base_kwargs, **legacy_kwargs)
        print(f"[build_cathedral_interior] export result: {result}")
    except Exception as e:
        print(f"[build_cathedral_interior] ✗ EXPORT FAILED: {e}")
        import traceback
        traceback.print_exc()
        raise

    # Verify the file was actually written
    if os.path.exists(out_path):
        size = os.path.getsize(out_path)
        print(f"[build_cathedral_interior] ✓ wrote {out_path} ({size} bytes)")
    else:
        print(f"[build_cathedral_interior] ✗ {out_path} was NOT created — check the export logs above")
        raise RuntimeError("GLB not written")


# ════════════════════════════════════════════════════════════════
# MAIN
# ════════════════════════════════════════════════════════════════

def main():
    clear_scene()
    build_warehouse_shell()
    build_floor_seams()
    build_brick_courses()
    build_pilasters()
    build_roof_trusses()
    build_hanging_fixtures()
    build_river_window_frame()
    build_workbench()
    build_bbs_terminal()
    build_diorama_bases()
    add_lights()
    # Camera intentionally NOT exported. Earlier the embedded
    # FrasierEye camera was hijacking Godot's active camera and
    # the player's view never updated. The FPC's make_current()
    # call defends against this anyway, but stripping the camera
    # at the source is cleaner. We can re-add named camera
    # markers later when we wire up cinematic framing.
    # setup_camera_hint()  # DISABLED
    export_glb()


if __name__ == "__main__":
    main()
