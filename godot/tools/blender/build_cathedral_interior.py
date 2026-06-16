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


def build_workbench_zone():
    """Floor-mounted markers indicating where workbench / BBS will go.
    The workbench mesh itself is provided by workbench_props.glb in
    cathedral.tscn — here we just put the floor cable runs and the
    rubber mat under it."""
    # Rubber anti-fatigue mat under the workbench
    make_box("Workbench_Mat", (0, 3.0, 0.025),
             (3.2, 1.6, 0.04),
             (0.10, 0.08, 0.06, 1.0))
    # Power cable trough running from the workbench toward the wall
    make_box("Workbench_CableRun", (-3.0, 3.0, 0.022),
             (6.0, 0.06, 0.03),
             (0.10, 0.08, 0.05, 1.0))


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
    build_workbench_zone()
    export_glb()


if __name__ == "__main__":
    main()
