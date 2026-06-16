"""
build_cathedral_interior.py
══════════════════════════════════════════════════════════════════
COMMUNITY PLANNED · The Bricoleur's warehouse-cathedral interior.

A rewrite from scratch. The earlier build washed white and had
missing-face issues; this version is intentionally simpler and
strictly closed-shell.

Run:
    blender --background --python build_cathedral_interior.py

Output:
    godot/assets/3d/cathedral/cathedral_interior.glb

Design goals (per user "start the cathedral over"):
  · Closed shell — floor, ceiling, four walls, no holes the player
    can fall into or see through accidentally.
  · DARK base palette. The runtime lighting in cathedral.tscn does
    all the cinematography; vertex colors must NOT pre-bright the
    surfaces or we wash white the moment any practical fires.
  · Two readable apertures: the river window on -X (cool blue
    spill, Bayou Saint Méduse outside) and the bay door on +X
    (open onto a dock leading into the bayou). Both are visible
    as players enter and serve as cardinal landmarks.
  · Vaulted exposed-rafter ceiling (the "warehouse cathedral"
    silhouette).
  · The interior holds the workbench (with BBS terminal), four
    regional diorama plinths, and demon-figurine shelves. The
    plinths + workbench + shelves are loaded as SEPARATE GLBs by
    cathedral.tscn — this script only emits the shell + permanent
    architecture (rafters, windows, doors, brick courses).

Triangles: target ~5-7k.
"""

import bpy
import math
import os

OUTPUT_DIR = "../../assets/3d/cathedral"
OUTPUT_NAME = "cathedral_interior.glb"

# ════════════════════════════════════════════════════════════════
# Dimensions
# ════════════════════════════════════════════════════════════════

WH_W = 24.0    # east-west (+X east → bay door; -X west → river window)
WH_D = 18.0    # north-south
WH_H = 7.0     # eaves height
ROOF_PEAK_H = 9.5   # gable peak height

# River window on the WEST wall (-X)
RIVER_WIN_W   = 7.0
RIVER_WIN_H   = 4.0
RIVER_WIN_Z   = 1.50      # bottom of window above floor

# Bay door on the EAST wall (+X)
BAY_W = 5.0
BAY_H = 4.2
BAY_Z = 0.0               # bottom flush with floor (it's a freight bay)

# Bayou dock that extends outward beyond the bay door
DOCK_LEN = 8.0            # how far the dock juts past the wall in +X
DOCK_W   = 6.0            # plank-deck width (N-S)

# ════════════════════════════════════════════════════════════════
# Palette — DELIBERATELY DARK so runtime lighting builds contrast.
# A common failure mode in this codebase: pre-bright vertex colors
# blow out under any practical light. Keep base ≤ 0.30.
# ════════════════════════════════════════════════════════════════

COL_FLOOR        = (0.14, 0.11, 0.08, 1.0)   # concrete slab — warm gray
COL_FLOOR_SEAM   = (0.06, 0.05, 0.03, 1.0)
COL_FLOOR_STAIN  = (0.08, 0.06, 0.04, 1.0)   # oil / water marks
COL_BRICK_WARM   = (0.22, 0.14, 0.09, 1.0)   # interior brick
COL_BRICK_COURSE = (0.16, 0.10, 0.06, 1.0)   # brick course mortar joints
COL_BRICK_PALE   = (0.24, 0.18, 0.13, 1.0)   # accent brick (lighter)
COL_PILASTER     = (0.18, 0.12, 0.08, 1.0)
COL_CEILING      = (0.10, 0.08, 0.06, 1.0)   # dark wood-plank ceiling
COL_RAFTER       = (0.20, 0.14, 0.09, 1.0)   # warm pine rafters
COL_STEEL        = (0.18, 0.18, 0.18, 1.0)   # painted-black structural steel
COL_GLASS_RIVER  = (0.20, 0.32, 0.42, 1.0)   # cold blue river-window glass
COL_GLASS_MULL   = (0.08, 0.08, 0.06, 1.0)   # window mullion (paint)
COL_BAY_DOOR     = (0.16, 0.13, 0.10, 1.0)   # rolled steel
COL_DOCK_WOOD    = (0.22, 0.16, 0.10, 1.0)   # creosote-soaked plank
COL_DOCK_DARK    = (0.14, 0.10, 0.06, 1.0)   # plank seams
COL_BAYOU_WATER  = (0.10, 0.14, 0.10, 1.0)   # bayou water — green-black
COL_BAYOU_BANK   = (0.12, 0.10, 0.08, 1.0)   # mud bank
COL_TREE_DARK    = (0.08, 0.12, 0.08, 1.0)   # cypress silhouette
COL_FRAME_BRASS  = (0.36, 0.26, 0.12, 1.0)   # window-frame brass (darker than diner)
COL_BRICK_HIGH   = (0.28, 0.20, 0.14, 1.0)   # high brick course where light hits

# ════════════════════════════════════════════════════════════════
# Helpers
# ════════════════════════════════════════════════════════════════

def clear_scene():
    bpy.ops.object.select_all(action='SELECT')
    bpy.ops.object.delete(use_global=False)
    for c in (bpy.data.meshes, bpy.data.materials, bpy.data.images):
        for item in list(c):
            if item.users == 0:
                c.remove(item)


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
        ('-Z', (0,3,2,1)),
        ('+Z', (4,5,6,7)),
        ('-Y', (0,1,5,4)),
        ('+Y', (2,3,7,6)),
        ('-X', (3,0,4,7)),
        ('+X', (1,2,6,5)),
    ]
    mesh = bpy.data.meshes.new(name + "_mesh")
    faces = [tuple(vids) for tag, vids in face_defs if tag not in open_faces]
    mesh.from_pydata(verts, [], faces)
    mesh.update()
    if not mesh.vertex_colors:
        mesh.vertex_colors.new(name="Col")
    layer = mesh.vertex_colors["Col"]
    for poly in mesh.polygons:
        for li in poly.loop_indices:
            layer.data[li].color = base_color
    obj = bpy.data.objects.new(name, mesh)
    bpy.context.collection.objects.link(obj)
    return obj


def make_cyl(name, center, radius, height, color, segments=8, axis='Z'):
    cx, cy, cz = center
    h2 = height / 2.0
    verts = []
    for cap_sgn in (-1, +1):
        for i in range(segments):
            ang = 2 * math.pi * i / segments
            r0 = radius * math.cos(ang)
            r1 = radius * math.sin(ang)
            if axis == 'Z':
                verts.append((cx + r0, cy + r1, cz + cap_sgn * h2))
            elif axis == 'X':
                verts.append((cx + cap_sgn * h2, cy + r0, cz + r1))
            else:
                verts.append((cx + r0, cy + cap_sgn * h2, cz + r1))
    cap_lo = len(verts)
    if axis == 'Z':   verts.append((cx, cy, cz - h2))
    elif axis == 'X': verts.append((cx - h2, cy, cz))
    else:             verts.append((cx, cy - h2, cz))
    cap_hi = len(verts)
    if axis == 'Z':   verts.append((cx, cy, cz + h2))
    elif axis == 'X': verts.append((cx + h2, cy, cz))
    else:             verts.append((cx, cy + h2, cz))
    faces = []
    for i in range(segments):
        j = (i + 1) % segments
        faces.append([i, j, segments + j, segments + i])
        faces.append([cap_lo, j, i])
        faces.append([cap_hi, segments + i, segments + j])
    mesh = bpy.data.meshes.new(f"{name}_mesh")
    mesh.from_pydata(verts, [], faces)
    mesh.update(calc_edges=True)
    if not mesh.vertex_colors:
        mesh.vertex_colors.new(name="Col")
    vc = mesh.vertex_colors[0]
    for poly in mesh.polygons:
        for li in poly.loop_indices:
            vc.data[li].color = color
    obj = bpy.data.objects.new(name, mesh)
    bpy.context.collection.objects.link(obj)
    return obj


def make_prism(name, verts, faces, color):
    """Arbitrary mesh with a single flat vertex color (for the gable
    end-walls and roof slopes)."""
    mesh = bpy.data.meshes.new(f"{name}_mesh")
    mesh.from_pydata(verts, [], faces)
    mesh.update(calc_edges=True)
    if not mesh.vertex_colors:
        mesh.vertex_colors.new(name="Col")
    vc = mesh.vertex_colors[0]
    for poly in mesh.polygons:
        for li in poly.loop_indices:
            vc.data[li].color = color
    obj = bpy.data.objects.new(name, mesh)
    bpy.context.collection.objects.link(obj)
    return obj


# ════════════════════════════════════════════════════════════════
# Build steps
# ════════════════════════════════════════════════════════════════

def build_floor():
    """Concrete slab. Slight dark seams every 4m to read 'industrial
    poured concrete' rather than 'flat plane'. Also a few oil stains
    where the workbench / bay door will sit."""
    make_box("Floor_Slab", (0, 0, -0.06), (WH_W, WH_D, 0.12), COL_FLOOR,
             open_faces={'-Z'})
    # Expansion-joint seams in a 4m × 4m grid
    nx = int(WH_W / 4)
    ny = int(WH_D / 4)
    for i in range(1, nx):
        x = -WH_W/2 + i * 4
        make_box(f"Floor_Seam_NS_{i}", (x, 0, 0.005),
                 (0.04, WH_D - 0.5, 0.005), COL_FLOOR_SEAM)
    for j in range(1, ny):
        y = -WH_D/2 + j * 4
        make_box(f"Floor_Seam_EW_{j}", (0, y, 0.005),
                 (WH_W - 0.5, 0.04, 0.005), COL_FLOOR_SEAM)
    # Oil-stain blots
    for label, (sx, sy, sw, sd) in [
        ("workbench_oil",  (0.0,  3.0, 1.5, 0.8)),
        ("bay_drag_marks", (8.0,  0.0, 2.0, 0.4)),
        ("plinth_wear_E",  (5.0, -3.0, 1.2, 1.2)),
        ("plinth_wear_W",  (-4.0, 4.0, 1.0, 0.9)),
    ]:
        make_box(f"Floor_Stain_{label}", (sx, sy, 0.012),
                 (sw, sd, 0.004), COL_FLOOR_STAIN)


def build_walls():
    """Four interior brick walls. Hollow boxes with open inward face
    so the player only sees the inside surface — keeps tris down and
    lets us insert windows / doors on each wall separately."""
    # NORTH wall (+Y) — solid brick, full height
    make_box("Wall_N", (0, WH_D/2 + 0.05, WH_H/2),
             (WH_W + 0.20, 0.10, WH_H), COL_BRICK_WARM)
    # SOUTH wall (-Y) — solid brick
    make_box("Wall_S", (0, -WH_D/2 - 0.05, WH_H/2),
             (WH_W + 0.20, 0.10, WH_H), COL_BRICK_WARM)

    # WEST wall (-X) — river-window cutout
    win_x = -WH_W/2 - 0.05
    # below window
    make_box("Wall_W_below", (win_x, 0, RIVER_WIN_Z/2),
             (0.10, WH_D, RIVER_WIN_Z), COL_BRICK_WARM)
    # above window
    above_h = WH_H - (RIVER_WIN_Z + RIVER_WIN_H)
    make_box("Wall_W_above", (win_x, 0, RIVER_WIN_Z + RIVER_WIN_H + above_h/2),
             (0.10, WH_D, above_h), COL_BRICK_WARM)
    # north of window
    side_d = (WH_D - RIVER_WIN_W) / 2
    make_box("Wall_W_N_of_win",
             (win_x, WH_D/2 - side_d/2, RIVER_WIN_Z + RIVER_WIN_H/2),
             (0.10, side_d, RIVER_WIN_H), COL_BRICK_WARM)
    make_box("Wall_W_S_of_win",
             (win_x, -WH_D/2 + side_d/2, RIVER_WIN_Z + RIVER_WIN_H/2),
             (0.10, side_d, RIVER_WIN_H), COL_BRICK_WARM)

    # EAST wall (+X) — bay-door cutout (full bottom-flush opening)
    bay_x = WH_W/2 + 0.05
    # north of bay
    bay_side_d = (WH_D - BAY_W) / 2
    make_box("Wall_E_N_of_bay",
             (bay_x, WH_D/2 - bay_side_d/2, WH_H/2),
             (0.10, bay_side_d, WH_H), COL_BRICK_WARM)
    make_box("Wall_E_S_of_bay",
             (bay_x, -WH_D/2 + bay_side_d/2, WH_H/2),
             (0.10, bay_side_d, WH_H), COL_BRICK_WARM)
    # above bay
    above_bay_h = WH_H - BAY_H
    make_box("Wall_E_above_bay",
             (bay_x, 0, BAY_H + above_bay_h/2),
             (0.10, BAY_W, above_bay_h), COL_BRICK_WARM)


def build_brick_courses():
    """Horizontal brick-course detail bands. Three accent strips
    around the inside of the interior walls — gives the eye
    something to rest on when reading wall height. Slightly
    lighter than the base brick for subtle banding."""
    inset = 0.06
    # Course heights (low / mid / high) — emulating real masonry
    # band courses.
    for label, z in [("LowCourse", 0.80),
                     ("MidCourse", 2.40),
                     ("HighCourse", 4.20),
                     ("EavesCourse", WH_H - 0.30)]:
        color = COL_BRICK_HIGH if "Eaves" in label or "High" in label \
                                else COL_BRICK_COURSE
        # North wall band
        make_box(f"Brick_{label}_N", (0, WH_D/2 - 0.10, z),
                 (WH_W - 0.40, 0.04, 0.15), color)
        make_box(f"Brick_{label}_S", (0, -WH_D/2 + 0.10, z),
                 (WH_W - 0.40, 0.04, 0.15), color)
        # West wall band (skip the window opening)
        if not (z > RIVER_WIN_Z - 0.10 and z < RIVER_WIN_Z + RIVER_WIN_H + 0.10):
            make_box(f"Brick_{label}_W", (-WH_W/2 + 0.10, 0, z),
                     (0.04, WH_D - 0.40, 0.15), color)
        else:
            # split the band across the window
            side_d = (WH_D - RIVER_WIN_W) / 2 - 0.20
            for sgn in (-1, +1):
                make_box(f"Brick_{label}_W_{sgn:+d}",
                         (-WH_W/2 + 0.10, sgn * (WH_D/2 - side_d/2), z),
                         (0.04, side_d, 0.15), color)
        # East wall band (skip the bay opening)
        if not (z < BAY_H):
            make_box(f"Brick_{label}_E", (WH_W/2 - 0.10, 0, z),
                     (0.04, WH_D - 0.40, 0.15), color)
        else:
            bay_side_d = (WH_D - BAY_W) / 2 - 0.20
            for sgn in (-1, +1):
                make_box(f"Brick_{label}_E_{sgn:+d}",
                         (WH_W/2 - 0.10, sgn * (WH_D/2 - bay_side_d/2), z),
                         (0.04, bay_side_d, 0.15), color)


def build_pilasters():
    """Brick pilasters down the long walls — visual rhythm that reads
    as load-bearing piers."""
    # Six pilasters per long wall (N and S), spaced every 4m
    for label, (wy, sgn) in [("N", (WH_D/2 - 0.30, -1)),
                              ("S", (-WH_D/2 + 0.30, +1))]:
        for i in range(-2, 3):
            px = i * 4.0
            make_box(f"Pilaster_{label}_{i:+d}",
                     (px, wy, WH_H/2),
                     (0.40, 0.18, WH_H - 0.30), COL_PILASTER)
            # Capital at top
            make_box(f"PilasterCap_{label}_{i:+d}",
                     (px, wy, WH_H - 0.10),
                     (0.55, 0.30, 0.10), COL_BRICK_HIGH)


def build_ceiling_and_roof():
    """A flat-ish lower-chord ceiling plus rafters above. Players
    looking up see exposed wooden rafters under a peaked ceiling.

    The ceiling we present to the player is the flat plane at WH_H
    (so the box of the room is sealed at eaves height); the rafters
    sit BELOW that plane as decoration. The gable peak above the
    flat ceiling is invisible to the player but lets exterior
    silhouettes feel right if the player ever looks out a window."""
    # Sealed ceiling plane (dark wood)
    make_box("Ceiling_Plane", (0, 0, WH_H + 0.05),
             (WH_W, WH_D, 0.10), COL_CEILING, open_faces={'+Z'})

    # Lower-chord rafter beams (the visible "ribs" under the ceiling)
    # — 7 trusses spanning E-W
    for i in range(-3, 4):
        cy = i * 2.5
        # bottom chord
        make_box(f"Rafter_Chord_{i:+d}", (0, cy, WH_H - 0.20),
                 (WH_W - 0.50, 0.20, 0.18), COL_RAFTER)
        # king post (vertical center)
        make_box(f"Rafter_KingPost_{i:+d}", (0, cy, WH_H - 0.60),
                 (0.16, 0.16, 0.70), COL_RAFTER)
        # angled top chords (faked as two flat boxes meeting at apex)
        for sgn in (-1, +1):
            make_box(f"Rafter_TopChord_{sgn:+d}_{i:+d}",
                     (sgn * (WH_W/4), cy, WH_H - 0.36),
                     (WH_W/2 - 0.30, 0.16, 0.12), COL_RAFTER)
        # diagonal strut from king-post base to mid-chord
        for sgn in (-1, +1):
            make_box(f"Rafter_Strut_{sgn:+d}_{i:+d}",
                     (sgn * (WH_W/4), cy, WH_H - 0.50),
                     (WH_W/2 - 0.60, 0.10, 0.08), COL_RAFTER)

    # Steel truss tie-rods (thin horizontal cylinders under each truss)
    for i in range(-3, 4):
        cy = i * 2.5
        make_cyl(f"Truss_TieRod_{i:+d}", (0, cy, WH_H - 0.85),
                 0.020, WH_W - 0.60, COL_STEEL, segments=6, axis='X')

    # Hanging pendant lights — three big enamel-shade fixtures down
    # the long axis, runtime light sources placed in cathedral.tscn
    for label, cx in [("W", -7.0), ("C", 0.0), ("E", 7.0)]:
        # Drop wire
        make_cyl(f"Pendant_{label}_Wire", (cx, 0, WH_H - 1.5),
                 0.015, 1.4, (0.04, 0.04, 0.04, 1.0), segments=4, axis='Z')
        # Canopy at the ceiling
        make_cyl(f"Pendant_{label}_Canopy", (cx, 0, WH_H - 0.15),
                 0.10, 0.06, COL_STEEL, segments=8, axis='Z')
        # Enamel shade — broad shallow cone (use cylinder approximation)
        make_cyl(f"Pendant_{label}_ShadeUpper", (cx, 0, WH_H - 2.10),
                 0.16, 0.04, COL_STEEL, segments=8, axis='Z')
        make_cyl(f"Pendant_{label}_ShadeMid", (cx, 0, WH_H - 2.25),
                 0.32, 0.20, (0.86, 0.84, 0.78, 1.0), segments=8, axis='Z')
        make_cyl(f"Pendant_{label}_ShadeRim", (cx, 0, WH_H - 2.34),
                 0.36, 0.02, COL_STEEL, segments=8, axis='Z')
        # Visible bulb
        make_cyl(f"Pendant_{label}_Bulb", (cx, 0, WH_H - 2.42),
                 0.05, 0.10, (0.96, 0.90, 0.66, 1.0), segments=6, axis='Z')


def build_river_window():
    """River window on the west wall: brass-framed 6-pane window
    with cold blue glass, plus deep sill. Outside the window sits a
    sliver of bayou silhouette (visible through the glass plane)."""
    win_x = -WH_W/2 - 0.06   # just outside the wall plane
    cz = RIVER_WIN_Z + RIVER_WIN_H / 2

    # Glass plane (single dark-blue slab — runtime light brings the
    # cool-blue spill onto interior surfaces)
    make_box("RiverWindow_Glass", (win_x - 0.02, 0, cz),
             (0.02, RIVER_WIN_W, RIVER_WIN_H), COL_GLASS_RIVER)

    # Mullion grid — 3 vertical + 2 horizontal members
    cols = 3
    rows = 2
    for c in range(cols + 1):
        cx_off = -RIVER_WIN_W/2 + c * (RIVER_WIN_W / cols)
        make_box(f"RiverWindow_MullionV_{c}",
                 (win_x - 0.01, cx_off, cz),
                 (0.025, 0.06, RIVER_WIN_H), COL_GLASS_MULL)
    for r in range(rows + 1):
        cz_off = -RIVER_WIN_H/2 + r * (RIVER_WIN_H / rows)
        make_box(f"RiverWindow_MullionH_{r}",
                 (win_x - 0.01, 0, cz + cz_off),
                 (0.025, RIVER_WIN_W, 0.06), COL_GLASS_MULL)

    # Brass outer frame (chunky)
    make_box("RiverWindow_Frame_T",
             (win_x + 0.005, 0, cz + RIVER_WIN_H/2 + 0.10),
             (0.06, RIVER_WIN_W + 0.20, 0.10), COL_FRAME_BRASS)
    make_box("RiverWindow_Frame_B",
             (win_x + 0.005, 0, cz - RIVER_WIN_H/2 - 0.10),
             (0.06, RIVER_WIN_W + 0.20, 0.10), COL_FRAME_BRASS)
    make_box("RiverWindow_Frame_L",
             (win_x + 0.005, -RIVER_WIN_W/2 - 0.10, cz),
             (0.06, 0.10, RIVER_WIN_H + 0.20), COL_FRAME_BRASS)
    make_box("RiverWindow_Frame_R",
             (win_x + 0.005, RIVER_WIN_W/2 + 0.10, cz),
             (0.06, 0.10, RIVER_WIN_H + 0.20), COL_FRAME_BRASS)

    # Stone sill (interior) — deep, doubles as a small shelf
    make_box("RiverWindow_Sill", (win_x + 0.20, 0, RIVER_WIN_Z - 0.05),
             (0.40, RIVER_WIN_W + 0.50, 0.10), COL_BRICK_HIGH)

    # ── Outside silhouettes (visible through the glass plane) ──
    # Far bayou bank — low strip
    make_box("Outside_Bayou_Bank", (win_x - 25, 0, RIVER_WIN_Z + 0.40),
             (5.0, 40.0, 1.20), COL_BAYOU_BANK)
    # Bayou water plane (low, just below sill height)
    make_box("Outside_Bayou_Water",
             (win_x - 12, 0, RIVER_WIN_Z - 0.20),
             (20.0, 40.0, 0.10), COL_BAYOU_WATER)
    # Cypress silhouettes
    for t in range(5):
        ty = -16 + t * 8
        make_box(f"Outside_Cypress_{t}",
                 (win_x - 22, ty, RIVER_WIN_Z + 2.5),
                 (1.6, 1.6, 3.5), COL_TREE_DARK)
        # Tapered crown
        make_box(f"Outside_CypressCrown_{t}",
                 (win_x - 22, ty, RIVER_WIN_Z + 4.7),
                 (1.0, 1.0, 1.2), COL_TREE_DARK)


def build_bay_door_and_dock():
    """The bay door on +X, OPEN, with a wooden dock leading out
    into the bayou. Player can walk OUT onto the dock — the dock is
    real walkable geometry on the same floor plane (Godot collision
    boxes in cathedral.tscn cover the dock too).
    """
    bay_x_outside = WH_W/2

    # Rolled steel header above the door (the rolled-up door itself)
    make_box("BayDoor_Header", (bay_x_outside, 0, BAY_H + 0.20),
             (0.30, BAY_W + 0.40, 0.40), COL_BAY_DOOR)
    # Rolled door body (cylinder) tucked above
    make_cyl("BayDoor_Roll", (bay_x_outside + 0.10, 0, BAY_H + 0.50),
             0.30, BAY_W, COL_BAY_DOOR, segments=8, axis='Y')
    # Door tracks (vertical channels on the sides of the opening)
    for sgn in (-1, +1):
        make_box(f"BayDoor_Track_{sgn:+d}",
                 (bay_x_outside, sgn * (BAY_W/2 + 0.08), BAY_H/2),
                 (0.15, 0.10, BAY_H), COL_STEEL)
    # Door threshold strip (worn steel at the floor crossing)
    make_box("BayDoor_Threshold",
             (bay_x_outside, 0, 0.015),
             (0.40, BAY_W, 0.03), COL_STEEL)

    # ── DOCK (extends from threshold out into the bayou) ──
    dock_z = 0.0
    dock_start_x = WH_W/2
    dock_end_x   = WH_W/2 + DOCK_LEN
    dock_cx = (dock_start_x + dock_end_x) / 2
    make_box("Dock_Deck",
             (dock_cx, 0, dock_z - 0.04),
             (DOCK_LEN, DOCK_W, 0.08), COL_DOCK_WOOD)
    # Plank seams along the deck (every 0.4m perpendicular to walking dir)
    n_planks = int(DOCK_LEN / 0.4)
    for i in range(1, n_planks):
        sx = dock_start_x + i * 0.4
        make_box(f"Dock_PlankSeam_{i}",
                 (sx, 0, dock_z + 0.005),
                 (0.015, DOCK_W - 0.10, 0.005), COL_DOCK_DARK)
    # Pilings at the corners
    for ex in (dock_start_x + 0.4, dock_end_x - 0.4):
        for sy in (-DOCK_W/2 + 0.3, +DOCK_W/2 - 0.3):
            make_cyl(f"Dock_Piling_{ex:.1f}_{sy:+.1f}",
                     (ex, sy, -0.5),
                     0.14, 2.6, COL_DOCK_DARK, segments=6, axis='Z')
            # Cap
            make_box(f"Dock_PilingCap_{ex:.1f}_{sy:+.1f}",
                     (ex, sy, 0.78), (0.34, 0.34, 0.10), COL_DOCK_WOOD)
    # Rope rail strung between cap-posts on the outer (north) side
    rope_z = 0.70
    make_cyl("Dock_Rope_N",
             ((dock_start_x + dock_end_x) / 2, +DOCK_W/2 - 0.30, rope_z),
             0.015, DOCK_LEN - 0.8, (0.30, 0.20, 0.10, 1.0),
             segments=4, axis='X')
    make_cyl("Dock_Rope_S",
             ((dock_start_x + dock_end_x) / 2, -DOCK_W/2 + 0.30, rope_z),
             0.015, DOCK_LEN - 0.8, (0.30, 0.20, 0.10, 1.0),
             segments=4, axis='X')

    # Bayou water around the dock
    make_box("Bayou_Water_Bay",
             (dock_end_x + 12, 0, -0.40),
             (24, 40.0, 0.10), COL_BAYOU_WATER)
    # A small skiff tied up off the dock end
    skiff_cx = dock_end_x + 1.6
    make_box("Skiff_Hull", (skiff_cx, -DOCK_W/2 + 0.6, -0.15),
             (1.8, 0.7, 0.30), (0.30, 0.20, 0.12, 1.0))
    make_box("Skiff_Bench", (skiff_cx, -DOCK_W/2 + 0.6, 0.05),
             (1.4, 0.20, 0.04), (0.42, 0.30, 0.18, 1.0))
    # Distant cypress + bank across the bayou
    make_box("Bayou_FarBank", (dock_end_x + 22, 0, 0.6),
             (3.0, 40.0, 1.6), COL_BAYOU_BANK)
    for t in range(5):
        ty = -16 + t * 8
        make_box(f"Bayou_FarCypress_{t}",
                 (dock_end_x + 22, ty, 2.8),
                 (1.6, 1.6, 3.6), COL_TREE_DARK)
        make_box(f"Bayou_FarCypress_Crown_{t}",
                 (dock_end_x + 22, ty, 5.0),
                 (1.0, 1.0, 1.4), COL_TREE_DARK)


def build_entry_door():
    """Small human-scale entry door on the SOUTH wall — the everyday
    door (the bay is freight-only). Just a recessed wood panel."""
    door_x = +6.0
    door_w = 1.2
    door_h = 2.2
    make_box("EntryDoor_Panel",
             (door_x, -WH_D/2 + 0.06, door_h/2),
             (door_w, 0.04, door_h), (0.22, 0.14, 0.08, 1.0))
    # Frame
    for sgn in (-1, +1):
        make_box(f"EntryDoor_Jamb_{sgn:+d}",
                 (door_x + sgn * (door_w/2 + 0.04), -WH_D/2 + 0.06, door_h/2),
                 (0.06, 0.08, door_h + 0.10), COL_BRICK_HIGH)
    make_box("EntryDoor_Lintel",
             (door_x, -WH_D/2 + 0.06, door_h + 0.06),
             (door_w + 0.20, 0.08, 0.10), COL_BRICK_HIGH)
    # Brass kick-plate at bottom
    make_box("EntryDoor_KickPlate",
             (door_x, -WH_D/2 + 0.04, 0.12),
             (door_w - 0.10, 0.02, 0.20), COL_FRAME_BRASS)
    # Knob
    make_cyl("EntryDoor_Knob",
             (door_x + door_w/2 - 0.12, -WH_D/2 + 0.03, 1.05),
             0.035, 0.06, COL_FRAME_BRASS, segments=8, axis='Y')


def build_plinth_markers():
    """Just the floor-marked outlines where regional dioramas will
    drop in (the diorama GLBs supply the actual platforms). These
    are slightly raised concrete pads showing where they go."""
    plinth_specs = [
        ("graustark", (5.0,  2.0),  4.0, 3.0),
        ("hce",       (-4.0, 4.0),  3.5, 2.5),
        ("smallwood", (5.0, -3.0),  3.5, 2.5),
        ("estuary",   (-5.0, -3.0), 3.0, 2.5),
    ]
    for label, (cx, cy), w, d in plinth_specs:
        make_box(f"PlinthPad_{label}",
                 (cx, cy, 0.06),
                 (w, d, 0.12),
                 (0.18, 0.14, 0.10, 1.0))
        # Stenciled label outline (a darker rectangle on the pad — the
        # demon figurines and diorama models sit on top of these)
        make_box(f"PlinthPad_{label}_Stencil",
                 (cx, cy - d/2 + 0.15, 0.122),
                 (w * 0.4, 0.04, 0.004),
                 (0.08, 0.06, 0.04, 1.0))


# ════════════════════════════════════════════════════════════════
# Workshop palette (extra colors for the lived-in detail pass)
# ════════════════════════════════════════════════════════════════
COL_WORKBENCH    = (0.30, 0.22, 0.14, 1.0)   # heavy wood top
COL_WORKBENCH_DK = (0.18, 0.13, 0.08, 1.0)   # wood-frame underside
COL_PEGBOARD     = (0.36, 0.26, 0.16, 1.0)   # masonite peg board
COL_TOOL_DARK    = (0.16, 0.14, 0.12, 1.0)   # tool handles, dark
COL_TOOL_STEEL   = (0.42, 0.42, 0.44, 1.0)
COL_CRT_CASE     = (0.30, 0.28, 0.22, 1.0)   # beige BBS terminal case
COL_CRT_SCREEN   = (0.10, 0.18, 0.12, 1.0)   # dark green screen (off-glow)
COL_CRT_GLOW     = (0.30, 0.92, 0.50, 1.0)   # phosphor lines
COL_KEYBOARD     = (0.18, 0.16, 0.14, 1.0)
COL_PAPER        = (0.84, 0.76, 0.60, 1.0)
COL_PAPER_DARK   = (0.62, 0.54, 0.36, 1.0)
COL_PAINT_RED    = (0.66, 0.20, 0.14, 1.0)
COL_PAINT_GREEN  = (0.20, 0.38, 0.18, 1.0)
COL_PAINT_BLUE   = (0.16, 0.26, 0.42, 1.0)
COL_RAG          = (0.42, 0.32, 0.22, 1.0)
COL_RUG          = (0.42, 0.22, 0.16, 1.0)
COL_RUG_DARK     = (0.26, 0.14, 0.10, 1.0)
COL_CRATE        = (0.36, 0.26, 0.16, 1.0)
COL_CRATE_DARK   = (0.22, 0.16, 0.10, 1.0)
COL_BARREL       = (0.28, 0.18, 0.10, 1.0)
COL_BARREL_BAND  = (0.10, 0.08, 0.06, 1.0)
COL_SOLDER_TIP   = (0.86, 0.32, 0.14, 1.0)   # glowing soldering iron tip
COL_LEATHER      = (0.22, 0.14, 0.08, 1.0)   # boots, jacket
COL_DENIM        = (0.18, 0.22, 0.32, 1.0)
COL_COFFEE_MUG   = (0.86, 0.82, 0.74, 1.0)
COL_COFFEE       = (0.18, 0.10, 0.06, 1.0)
COL_FIGURINE     = (0.34, 0.26, 0.18, 1.0)   # demon figurines on shelves
COL_FIGURINE_DK  = (0.18, 0.14, 0.10, 1.0)
COL_BRASS_DULL   = (0.50, 0.36, 0.18, 1.0)


def build_workbench():
    """The workbench — the heart of the room. A real heavy carpenter's
    bench with a tool tray, vise, BBS terminal, soldering station,
    parts bins, scattered paper. This stays in cathedral_interior.glb
    so the space is FURNISHED even if workbench_props.glb fails to
    build separately."""
    # Anti-fatigue rubber mat
    make_box("Workbench_Mat", (0, 3.0, 0.025),
             (3.6, 1.8, 0.04), (0.08, 0.06, 0.04, 1.0))
    # Power cable run leading to the wall
    make_box("Workbench_CableRun", (-3.5, 3.0, 0.025),
             (6.0, 0.05, 0.025), (0.10, 0.08, 0.05, 1.0))
    # Heavy bench top (3.0m × 0.9m × 0.06m at z=0.91)
    bench_top_z = 0.91
    make_box("Workbench_Top", (0, 3.0, bench_top_z),
             (3.0, 0.90, 0.06), COL_WORKBENCH)
    # Apron and skirt (suggest thick top)
    make_box("Workbench_Apron_F",
             (0, 3.0 - 0.45, bench_top_z - 0.10),
             (3.0, 0.04, 0.18), COL_WORKBENCH_DK)
    make_box("Workbench_Apron_B",
             (0, 3.0 + 0.45, bench_top_z - 0.10),
             (3.0, 0.04, 0.18), COL_WORKBENCH_DK)
    # 4 chunky legs
    for ex in (-1.35, +1.35):
        for ey in (-0.40, +0.40):
            make_box(f"Workbench_Leg_{ex:+.2f}_{ey:+.2f}",
                     (ex, 3.0 + ey, bench_top_z/2 - 0.04),
                     (0.10, 0.10, bench_top_z - 0.04), COL_WORKBENCH_DK)
    # Lower shelf between the legs (for parts bins)
    make_box("Workbench_LowerShelf",
             (0, 3.0, 0.20),
             (2.50, 0.70, 0.04), COL_WORKBENCH_DK)
    # Bench vise on the south-west corner
    vise_x = -1.10
    vise_y = 3.0 - 0.32
    make_box("Vise_Body", (vise_x, vise_y, bench_top_z + 0.06),
             (0.18, 0.14, 0.12), COL_TOOL_STEEL)
    make_box("Vise_Jaw_Fixed", (vise_x - 0.10, vise_y, bench_top_z + 0.09),
             (0.04, 0.14, 0.10), COL_TOOL_DARK)
    make_box("Vise_Jaw_Slide", (vise_x + 0.05, vise_y, bench_top_z + 0.09),
             (0.04, 0.14, 0.10), COL_TOOL_DARK)
    make_cyl("Vise_Handle", (vise_x + 0.18, vise_y, bench_top_z + 0.06),
             0.012, 0.30, COL_TOOL_STEEL, segments=6, axis='X')
    # BBS terminal — beige case + phosphor green CRT (the canonical
    # "only screen in the room"). Sits on the +Y back of the bench.
    crt_x, crt_y, crt_z = 0.6, 3.0 + 0.20, bench_top_z + 0.18
    make_box("BBS_Case", (crt_x, crt_y, crt_z),
             (0.46, 0.42, 0.36), COL_CRT_CASE)
    # Inset bezel
    make_box("BBS_Bezel", (crt_x, crt_y - 0.22, crt_z + 0.02),
             (0.34, 0.02, 0.28), COL_CRT_SCREEN)
    # Screen (phosphor green) — slightly proud of bezel so glow reads
    make_box("BBS_Screen", (crt_x, crt_y - 0.23, crt_z + 0.02),
             (0.30, 0.005, 0.24), COL_CRT_GLOW)
    # 5 horizontal scanline rows (a touch darker than screen base)
    for i in range(5):
        line_z = crt_z - 0.10 + i * 0.05
        make_box(f"BBS_ScanLine_{i}", (crt_x, crt_y - 0.232, line_z),
                 (0.22, 0.002, 0.012), (0.20, 0.62, 0.32, 1.0))
    # Keyboard in front of the CRT
    make_box("BBS_Keyboard", (crt_x, crt_y - 0.42, bench_top_z + 0.025),
             (0.42, 0.16, 0.025), COL_KEYBOARD)
    # Key cap rows (suggest individual keys without modeling each)
    for r in range(4):
        ky = crt_y - 0.42 - 0.05 + r * 0.03
        make_box(f"BBS_KeyRow_{r}", (crt_x, ky, bench_top_z + 0.041),
                 (0.40, 0.022, 0.010), (0.32, 0.30, 0.26, 1.0))
    # Soldering iron in holder (south-east of the BBS, glowing tip)
    sld_x, sld_y = -0.7, 3.0 - 0.10
    # Holder base
    make_box("Solder_HolderBase", (sld_x, sld_y, bench_top_z + 0.03),
             (0.10, 0.16, 0.06), COL_TOOL_STEEL)
    # Coiled spring rests (vertical posts)
    make_cyl("Solder_HolderPost_L", (sld_x - 0.025, sld_y, bench_top_z + 0.10),
             0.010, 0.14, COL_TOOL_STEEL, segments=4, axis='Z')
    make_cyl("Solder_HolderPost_R", (sld_x + 0.025, sld_y, bench_top_z + 0.10),
             0.010, 0.14, COL_TOOL_STEEL, segments=4, axis='Z')
    # Iron body (a horizontal cylinder slanted across the holder)
    make_cyl("Solder_IronBody", (sld_x, sld_y + 0.05, bench_top_z + 0.14),
             0.018, 0.18, COL_TOOL_DARK, segments=6, axis='Y')
    # Tip (glowing)
    make_cyl("Solder_IronTip", (sld_x, sld_y - 0.07, bench_top_z + 0.14),
             0.008, 0.05, COL_SOLDER_TIP, segments=4, axis='Y')
    # Cord trailing off the back
    make_cyl("Solder_Cord", (sld_x + 0.20, sld_y + 0.20, bench_top_z + 0.06),
             0.005, 0.50, (0.10, 0.10, 0.10, 1.0), segments=4, axis='X')
    # Spool of solder (small cylinder lying on the bench)
    make_cyl("Solder_Spool", (sld_x - 0.20, sld_y, bench_top_z + 0.04),
             0.05, 0.04, COL_BRASS_DULL, segments=8, axis='Z')
    # Magnifying lamp on a swing arm (just over the work area)
    arm_origin_x, arm_origin_y = -0.4, 3.0 + 0.40
    make_cyl("MagLamp_Post",
             (arm_origin_x, arm_origin_y, bench_top_z + 0.20),
             0.018, 0.40, COL_TOOL_STEEL, segments=6, axis='Z')
    make_cyl("MagLamp_Arm1",
             (arm_origin_x + 0.20, arm_origin_y - 0.05, bench_top_z + 0.40),
             0.012, 0.45, COL_TOOL_STEEL, segments=4, axis='X')
    make_cyl("MagLamp_Arm2",
             (arm_origin_x + 0.42, arm_origin_y - 0.20, bench_top_z + 0.30),
             0.012, 0.40, COL_TOOL_STEEL, segments=4, axis='Y')
    # Lens ring (a torus-ish ring drawn as a wide thin cylinder)
    make_cyl("MagLamp_Lens",
             (arm_origin_x + 0.42, arm_origin_y - 0.35, bench_top_z + 0.22),
             0.10, 0.02, (0.78, 0.84, 0.92, 1.0), segments=12, axis='Z')
    # Parts bins on the lower shelf — 5 small open boxes with bright tabs
    for i, color in enumerate([
        (0.42, 0.34, 0.22, 1.0),
        (0.30, 0.42, 0.20, 1.0),
        (0.42, 0.20, 0.16, 1.0),
        (0.20, 0.28, 0.42, 1.0),
        (0.46, 0.30, 0.18, 1.0),
    ]):
        bx = -1.10 + i * 0.45
        make_box(f"PartsBin_{i}", (bx, 3.0 - 0.18, 0.30),
                 (0.28, 0.22, 0.18), color)
        make_box(f"PartsBin_{i}_Label", (bx, 3.0 - 0.28, 0.32),
                 (0.20, 0.005, 0.05), COL_PAPER)
    # Paper drift / scattered work notes on the bench (south-west cluster)
    for i, (px, py) in enumerate([(-0.55, +0.28), (-0.40, +0.18),
                                   (-0.65, +0.10), (-0.30, +0.30)]):
        make_box(f"BenchPaper_{i}",
                 (px, 3.0 + py, bench_top_z + 0.005),
                 (0.18, 0.22, 0.003),
                 COL_PAPER if i % 2 == 0 else COL_PAPER_DARK)
    # Coffee mug (a bit east of the keyboard, half-full)
    mug_x, mug_y = +1.30, 3.0 - 0.15
    make_cyl("CoffeeMug_Body", (mug_x, mug_y, bench_top_z + 0.05),
             0.038, 0.10, COL_COFFEE_MUG, segments=8, axis='Z')
    make_cyl("CoffeeMug_Coffee", (mug_x, mug_y, bench_top_z + 0.094),
             0.034, 0.004, COL_COFFEE, segments=8, axis='Z')
    # Handle (small box on the side)
    make_box("CoffeeMug_Handle", (mug_x + 0.05, mug_y, bench_top_z + 0.06),
             (0.018, 0.015, 0.06), COL_COFFEE_MUG)
    # Ashtray + a stubbed cigarette (Frasier doesn't smoke but the bench
    # belongs to a working space — drop this if canon says no)
    # Skipping per character — no cigarettes.
    # A small partly-built tarot card-station base (foreshadows what
    # the dioramas grow into)
    make_box("WIP_Station_Base", (+1.10, 3.0 + 0.20, bench_top_z + 0.03),
             (0.40, 0.30, 0.04), COL_PILASTER)
    # Wire spools standing on end at the east edge
    for i, col in enumerate([(0.86, 0.20, 0.14, 1.0),
                              (0.20, 0.28, 0.42, 1.0),
                              (0.18, 0.18, 0.18, 1.0)]):
        sx = +1.45 - i * 0.10
        sy = 3.0 + 0.30 - i * 0.05
        make_cyl(f"WireSpool_{i}", (sx, sy, bench_top_z + 0.04),
                 0.05, 0.04, col, segments=8, axis='Z')


def build_workbench_chair():
    """Wooden stool tucked partly under the workbench — implies
    Frasier just stepped away. South of the bench."""
    sx, sy = -0.2, 2.10
    make_box("WorkChair_Seat", (sx, sy, 0.50),
             (0.42, 0.40, 0.06), COL_WORKBENCH)
    # Four splayed legs (just verticals — splay would need rotations
    # we'd rather not introduce here)
    for ex in (-1, +1):
        for ey in (-1, +1):
            make_box(f"WorkChair_Leg_{ex:+d}_{ey:+d}",
                     (sx + ex * 0.18, sy + ey * 0.17, 0.25),
                     (0.04, 0.04, 0.50), COL_WORKBENCH_DK)
    # Cross-stretchers (an X under the seat)
    make_box("WorkChair_Stretcher_X",
             (sx, sy, 0.18), (0.34, 0.04, 0.02), COL_WORKBENCH_DK)
    make_box("WorkChair_Stretcher_Y",
             (sx, sy, 0.18), (0.04, 0.34, 0.02), COL_WORKBENCH_DK)
    # Back rest (low ladder-back)
    make_box("WorkChair_BackPost_L",
             (sx - 0.18, sy + 0.17, 0.78),
             (0.04, 0.04, 0.56), COL_WORKBENCH_DK)
    make_box("WorkChair_BackPost_R",
             (sx + 0.18, sy + 0.17, 0.78),
             (0.04, 0.04, 0.56), COL_WORKBENCH_DK)
    for i in range(3):
        bz = 0.78 + (i - 1) * 0.10
        make_box(f"WorkChair_BackRung_{i}",
                 (sx, sy + 0.17, bz),
                 (0.32, 0.03, 0.02), COL_WORKBENCH_DK)
    # Worn cushion
    make_box("WorkChair_Cushion",
             (sx, sy, 0.54),
             (0.40, 0.38, 0.04), COL_RUG)


def build_pegboard():
    """Pegboard mounted on the wall above the workbench, hung with
    tool silhouettes. Reads as a real shop wall."""
    # Pegboard back panel — on the SOUTH wall behind the bench
    pb_x = 0.0
    pb_y = -WH_D/2 + 0.10
    pb_z = 1.95
    make_box("Pegboard_Back", (pb_x, pb_y, pb_z),
             (3.4, 0.04, 1.50), COL_PEGBOARD)
    # Frame edges
    for x_off, y_off, sx, sy in [
        ( 0,  +0.75, 3.50, 0.06),    # top
        ( 0,  -0.75, 3.50, 0.06),    # bottom
        (-1.7,   0,  0.06, 1.50),    # left
        (+1.7,   0,  0.06, 1.50),    # right
    ]:
        make_box(f"Pegboard_Frame_{x_off}_{y_off}",
                 (pb_x + x_off, pb_y, pb_z + y_off),
                 (sx, 0.05, sy if sx > 0.5 else sy),
                 COL_WORKBENCH_DK)
    # Tool silhouettes mounted with pegs — a few recognizable shapes.
    # All are thin slabs PROUD of the pegboard so they catch the
    # workbench lamp.
    tool_specs = [
        # (offset_x, offset_z, sx, sz, color)  — silhouette
        (-1.30, +0.45, 0.10, 0.55, COL_TOOL_DARK),    # tall screwdriver
        (-1.10, +0.45, 0.10, 0.55, COL_TOOL_DARK),
        (-0.90, +0.45, 0.10, 0.55, COL_TOOL_DARK),
        (-0.40, +0.30, 0.50, 0.16, COL_TOOL_STEEL),   # adjustable wrench
        (-0.40, +0.10, 0.50, 0.16, COL_TOOL_STEEL),
        (+0.30, +0.40, 0.30, 0.45, COL_TOOL_DARK),    # hammer
        (+0.70, +0.40, 0.16, 0.55, COL_TOOL_STEEL),   # pliers handles
        (+1.10, +0.20, 0.45, 0.30, COL_TOOL_STEEL),   # crescent saw outline
        (+1.40, +0.50, 0.10, 0.40, COL_BRASS_DULL),   # small hex key set
        (-0.20, -0.30, 0.50, 0.16, COL_TOOL_DARK),    # tape measure
        (+0.40, -0.30, 0.20, 0.20, COL_TOOL_STEEL),   # small drill outline
    ]
    for i, (ox, oz, sx, sz, col) in enumerate(tool_specs):
        make_box(f"Pegboard_Tool_{i}",
                 (pb_x + ox, pb_y + 0.03, pb_z + oz),
                 (sx, 0.012, sz), col)


def build_shelves_and_figurines():
    """Wooden shelves along the NORTH wall holding the demon
    figurines + collected oddments. Player will populate these with
    unlock collectibles during play."""
    # 3 shelves, 3 cells each (so 9 figurine slots, leaving room for
    # the unlock-during-play arc).
    shelf_x = 0.0
    shelf_y = WH_D/2 - 0.10
    for s, sz in enumerate([1.20, 2.10, 3.00]):
        # Shelf board
        make_box(f"Shelf_{s}_Board",
                 (shelf_x, shelf_y, sz),
                 (5.0, 0.32, 0.04), COL_WORKBENCH_DK)
        # Brackets (3 brackets)
        for bx in (-2.0, 0.0, +2.0):
            make_box(f"Shelf_{s}_Bracket_{bx:+.1f}",
                     (shelf_x + bx, shelf_y + 0.10, sz - 0.10),
                     (0.04, 0.10, 0.10), COL_STEEL)
        # 3 figurines per shelf
        for f_i in range(3):
            fx = shelf_x - 1.8 + f_i * 1.8
            # Body
            make_box(f"Figurine_{s}_{f_i}_Body",
                     (fx, shelf_y, sz + 0.20),
                     (0.20, 0.22, 0.36),
                     COL_FIGURINE if (s + f_i) % 2 == 0 else COL_FIGURINE_DK)
            # Head
            make_box(f"Figurine_{s}_{f_i}_Head",
                     (fx, shelf_y, sz + 0.46),
                     (0.16, 0.16, 0.16), COL_FIGURINE_DK)
            # Tiny brass plaque on the shelf in front of it
            make_box(f"Figurine_{s}_{f_i}_Plaque",
                     (fx, shelf_y - 0.13, sz + 0.022),
                     (0.16, 0.04, 0.006), COL_BRASS_DULL)


def build_storage_crates():
    """Stacks of wooden crates along the long walls. Establishes
    'this is still also a warehouse' silhouette."""
    crate_specs = [
        # Stacked pair at the NW
        (-WH_W/2 + 1.0, -WH_D/2 + 2.0, 0, 2),
        # Single in NE
        (WH_W/2 - 1.0, WH_D/2 - 1.5, 0, 1),
        # Stacked triple, west wall, north of river-window pilaster
        (-WH_W/2 + 1.0, -WH_D/2 + 6.5, 0, 3),
        # Two in front of bay door, off to the side
        (WH_W/2 - 2.5, -WH_D/2 + 3.0, 0, 2),
        # Single in deep north corner west
        (-WH_W/2 + 1.0, WH_D/2 - 1.0, 0, 1),
    ]
    for stack_i, (cx, cy, _, n) in enumerate(crate_specs):
        for layer in range(n):
            cz = 0.30 + layer * 0.60
            make_box(f"Crate_{stack_i}_{layer}", (cx, cy, cz),
                     (0.70, 0.60, 0.58), COL_CRATE)
            # Slat seams (3 horizontal seams)
            for sl in range(3):
                make_box(f"Crate_{stack_i}_{layer}_Slat_{sl}",
                         (cx, cy - 0.31, cz - 0.18 + sl * 0.18),
                         (0.66, 0.005, 0.025), COL_CRATE_DARK)
            # Stamped label
            make_box(f"Crate_{stack_i}_{layer}_Label",
                     (cx, cy - 0.31, cz),
                     (0.20, 0.005, 0.12), COL_PAPER_DARK)
    # A couple of barrels too
    for i, (bx, by) in enumerate([
        (-WH_W/2 + 1.5, +1.5),
        (+WH_W/2 - 1.5, -3.0),
    ]):
        # Barrel body
        make_cyl(f"Barrel_{i}_Body", (bx, by, 0.45),
                 0.32, 0.90, COL_BARREL, segments=10, axis='Z')
        # Bands (two darker rings as flattened cylinders)
        for ring_z in (0.22, 0.68):
            make_cyl(f"Barrel_{i}_Band_{ring_z}",
                     (bx, by, ring_z), 0.33, 0.04,
                     COL_BARREL_BAND, segments=12, axis='Z')
        # Top lid (slightly darker)
        make_cyl(f"Barrel_{i}_Lid", (bx, by, 0.91),
                 0.30, 0.02, COL_BARREL_BAND, segments=10, axis='Z')


def build_hanging_chains_and_cables():
    """Drop chains and conduit hanging from the rafters — power feeds
    for the pendants and a chain hoist sat over the bay-door zone."""
    # Conduit runs along the long axis (south side of rafters)
    make_box("Conduit_Main",
             (0, -WH_D/2 + 1.0, WH_H - 0.45),
             (WH_W - 2.0, 0.05, 0.06), COL_STEEL)
    # Branch conduits dropping to each pendant
    for cx in (-7.0, 0.0, 7.0):
        make_box(f"Conduit_Branch_{cx:+.1f}",
                 (cx, -WH_D/2 + 1.0 + 0.5, WH_H - 0.45),
                 (0.05, 1.0, 0.05), COL_STEEL)
    # Chain hoist (over the bay door) — a steel beam + dangling chain
    make_box("ChainHoist_Beam",
             (WH_W/2 - 3.0, 0, WH_H - 0.50),
             (5.0, 0.16, 0.16), COL_STEEL)
    # Trolley block
    make_box("ChainHoist_Trolley",
             (WH_W/2 - 4.0, 0, WH_H - 0.70),
             (0.30, 0.30, 0.20), COL_STEEL)
    # Chain (a series of small steel cylinders down to ~2.5m)
    for i in range(14):
        cz = WH_H - 0.95 - i * 0.28
        make_box(f"ChainHoist_Link_{i}",
                 (WH_W/2 - 4.0, 0, cz),
                 (0.04, 0.04, 0.08), COL_STEEL)
    # Hook at the bottom
    make_box("ChainHoist_Hook",
             (WH_W/2 - 4.0, 0, WH_H - 4.95),
             (0.10, 0.06, 0.16), COL_STEEL)


def build_floor_clutter():
    """Rugs, broom, paint cans, boots, ladder — the small things
    that say 'someone has been working here for months'."""
    # Worn area rug under the workbench (a different rug from the mat,
    # this one is more decorative — old red kilim)
    make_box("Rug_Workbench",
             (0, 3.0, 0.012),
             (4.6, 2.4, 0.012), COL_RUG)
    # Rug seam border
    for sgn in (-1, +1):
        make_box(f"Rug_Workbench_BorderN_{sgn:+d}",
                 (0, 3.0 + sgn * 1.15, 0.014),
                 (4.6, 0.10, 0.006), COL_RUG_DARK)
        make_box(f"Rug_Workbench_BorderE_{sgn:+d}",
                 (sgn * 2.25, 3.0, 0.014),
                 (0.10, 2.4, 0.006), COL_RUG_DARK)

    # Push broom leaning against the south wall, east of the bench
    broom_x, broom_y = +3.5, -WH_D/2 + 0.30
    # Handle (vertical cylinder, slight tilt fake by offset top)
    make_cyl("Broom_Handle", (broom_x, broom_y, 0.80),
             0.014, 1.50, COL_WORKBENCH, segments=4, axis='Z')
    make_box("Broom_Head", (broom_x, broom_y, 0.06),
             (0.36, 0.10, 0.10), COL_WORKBENCH_DK)
    make_box("Broom_Bristles", (broom_x, broom_y, 0.02),
             (0.34, 0.08, 0.04), COL_RAG)

    # Row of paint cans (small storage line) on the floor west wall
    for i, color in enumerate([COL_PAINT_RED, COL_PAINT_GREEN,
                                COL_PAINT_BLUE, COL_PILASTER]):
        cx = -WH_W/2 + 1.0
        cy = -1.5 + i * 0.45
        make_cyl(f"PaintCan_{i}", (cx, cy, 0.15),
                 0.10, 0.28, COL_STEEL, segments=8, axis='Z')
        # Dripped paint band visible on the rim
        make_cyl(f"PaintCan_{i}_Drip", (cx, cy, 0.28),
                 0.105, 0.012, color, segments=8, axis='Z')
        # Label (paper around the body)
        make_box(f"PaintCan_{i}_Label", (cx, cy - 0.10, 0.16),
                 (0.16, 0.005, 0.12), COL_PAPER)

    # Boots pair near the entry door (south wall, east of door)
    for b, (bx_off, sgn) in enumerate([(-0.20, +1), (-0.05, -1)]):
        bx = +6.0 + bx_off
        by = -WH_D/2 + 0.45
        # Sole
        make_box(f"Boot_{b}_Sole", (bx, by, 0.025),
                 (0.10, 0.26, 0.04), COL_LEATHER)
        # Upper
        make_box(f"Boot_{b}_Upper", (bx, by + 0.04, 0.20),
                 (0.10, 0.16, 0.30), COL_LEATHER)
        # Tongue
        make_box(f"Boot_{b}_Tongue", (bx, by, 0.16),
                 (0.07, 0.04, 0.10), COL_DENIM)

    # Wooden ladder leaning against the west wall (south of river window)
    lad_x = -WH_W/2 + 0.30
    lad_y = -3.0
    for r in range(7):
        lz = 0.20 + r * 0.40
        make_box(f"Ladder_Rung_{r}", (lad_x + r * 0.08, lad_y, lz),
                 (0.04, 0.30, 0.03), COL_WORKBENCH)
    # Side rails (two long boxes)
    make_box("Ladder_Rail_N", (lad_x + 0.24, lad_y + 0.13, 1.50),
             (0.78, 0.04, 0.04), COL_WORKBENCH_DK)
    make_box("Ladder_Rail_S", (lad_x + 0.24, lad_y - 0.13, 1.50),
             (0.78, 0.04, 0.04), COL_WORKBENCH_DK)

    # Spool of cable on the floor near the workbench
    make_cyl("CableSpool_Disc",
             (-1.8, 1.9, 0.22),
             0.32, 0.42, COL_WORKBENCH_DK, segments=10, axis='Z')
    make_cyl("CableSpool_Core",
             (-1.8, 1.9, 0.22),
             0.16, 0.46, (0.10, 0.08, 0.04, 1.0), segments=8, axis='Z')

    # Jacket draped over the chair back
    make_box("Jacket_Draped",
             (-0.10, 2.30, 0.94),
             (0.36, 0.10, 0.46), COL_DENIM)
    # Sleeve falling forward
    make_box("Jacket_Sleeve",
             (-0.12, 2.20, 0.78),
             (0.10, 0.08, 0.34), COL_DENIM)

    # Drift of papers on the floor under the workbench
    for i, (px, py) in enumerate([(-0.4, 2.6), (-0.2, 2.5), (+0.2, 2.7)]):
        make_box(f"FloorPaper_{i}",
                 (px, py, 0.025),
                 (0.22, 0.28, 0.004),
                 COL_PAPER if i % 2 == 0 else COL_PAPER_DARK)

    # Small folded blueprint roll near a crate
    make_cyl("BlueprintRoll",
             (-WH_W/2 + 1.0, +3.5, 0.05),
             0.04, 0.46, COL_PAPER, segments=6, axis='X')


# ════════════════════════════════════════════════════════════════
# Export
# ════════════════════════════════════════════════════════════════

def export_glb():
    out_dir = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), OUTPUT_DIR))
    os.makedirs(out_dir, exist_ok=True)
    out_path = os.path.join(out_dir, OUTPUT_NAME)
    print(f"[build_cathedral] exporting to {out_path}")
    print(f"[build_cathedral] scene objects: {len(bpy.context.scene.objects)}")
    bpy.ops.object.select_all(action='SELECT')
    base = dict(filepath=out_path, export_format='GLB',
                use_selection=False, export_apply=True,
                export_lights=False, export_cameras=False)
    rna = bpy.ops.export_scene.gltf.get_rna_type()
    legacy = {}
    if 'export_colors' in rna.properties:  legacy['export_colors']  = True
    if 'export_normals' in rna.properties: legacy['export_normals'] = True
    bpy.ops.export_scene.gltf(**base, **legacy)
    if os.path.exists(out_path):
        size = os.path.getsize(out_path)
        print(f"[build_cathedral] ✓ wrote {out_path} ({size} bytes)")
    else:
        raise RuntimeError("GLB not written")


def main():
    clear_scene()
    build_floor()
    build_walls()
    build_brick_courses()
    build_pilasters()
    build_ceiling_and_roof()
    build_river_window()
    build_bay_door_and_dock()
    build_entry_door()
    build_plinth_markers()
    build_workbench()
    build_workbench_chair()
    build_pegboard()
    build_shelves_and_figurines()
    build_storage_crates()
    build_hanging_chains_and_cables()
    build_floor_clutter()
    export_glb()


if __name__ == "__main__":
    main()
