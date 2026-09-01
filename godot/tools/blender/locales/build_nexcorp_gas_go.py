"""
build_nexcorp_gas_go.py
══════════════════════════════════════════════════════════════════
VOL 6 · NexCorp Gas & Go · Skip Donnelly's shift.

Across the intersection from the Kwik Stop. Per _VOL6_WIKI.md:
'Skip's shift. Across the intersection from the Kwik Stop. The
locker (#4, combination is Skip's ex-wife's birthday backward).'

Distinguishing notes from the Kwik Stop:
  · Smaller convenience footprint, BIGGER pump-canopy presence
    (visible through windows)
  · Employee locker room visible at back (#4 prominent)
  · NexCorp corporate-blue brand vs Kwik Stop's brand red
  · Skip's manager office at back-left
  · Less stocked, more transactional (gas station-first)

Footprint: 12m W × 9m D, single floor, ~3.0m ceiling.
Pumps + canopy outside visible through south window.

Run:
    blender --background --python build_nexcorp_gas_go.py

Output:
    godot/assets/3d/locales/nexcorp_gas_go.glb
"""

import bpy
import math
import os
import sys

_SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
if _SCRIPT_DIR not in sys.path:
    sys.path.insert(0, _SCRIPT_DIR)

OUTPUT_DIR  = "../../../assets/3d/locales"
OUTPUT_NAME = "nexcorp_gas_go.glb"


# ── Palette ──────────────────────────────────────────────────────
# NexCorp brand: corporate blue + white + dark grey institutional
COL_FLOOR_TILE      = (0.78, 0.74, 0.70, 1.0)
COL_FLOOR_GROUT     = (0.32, 0.30, 0.28, 1.0)
COL_WALL_WHITE      = (0.90, 0.92, 0.94, 1.0)
COL_WALL_NEXCORP    = (0.16, 0.32, 0.56, 1.0)   # NexCorp corporate blue
COL_CEILING_TILE    = (0.86, 0.88, 0.86, 1.0)
COL_GLASS           = (0.62, 0.78, 0.82, 0.55)
COL_METAL_STEEL     = (0.66, 0.68, 0.70, 1.0)
COL_METAL_BLACK     = (0.18, 0.16, 0.14, 1.0)
COL_LOCKER_GREY     = (0.42, 0.44, 0.48, 1.0)
COL_LOCKER_DOORSEAM = (0.32, 0.34, 0.38, 1.0)
COL_COUNTER_LAMINATE= (0.42, 0.40, 0.38, 1.0)
COL_COFFEE_BROWN    = (0.32, 0.18, 0.10, 1.0)
COL_PAPER           = (0.92, 0.88, 0.78, 1.0)

SNACK_TINTS = [
    (0.96, 0.32, 0.18, 1.0), (0.18, 0.62, 0.92, 1.0),
    (0.96, 0.86, 0.28, 1.0), (0.32, 0.78, 0.42, 1.0),
    (0.96, 0.46, 0.22, 1.0), (0.66, 0.32, 0.78, 1.0),
    (0.88, 0.88, 0.88, 1.0),
]

CEIL_Z = 3.00


def clear_scene():
    for obj in list(bpy.data.objects):
        bpy.data.objects.remove(obj, do_unlink=True)
    for mesh in list(bpy.data.meshes):
        bpy.data.meshes.remove(mesh, do_unlink=True)


def _finalize_mesh(name, verts, faces, base_color):
    mesh = bpy.data.meshes.new(name + "_mesh")
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


def make_box(name, center, size, base_color, open_faces=None):
    open_faces = open_faces or set()
    cx, cy, cz = center
    sx, sy, sz = size
    hx, hy, hz = sx / 2, sy / 2, sz / 2
    verts = [
        (cx-hx, cy-hy, cz-hz), (cx+hx, cy-hy, cz-hz),
        (cx+hx, cy+hy, cz-hz), (cx-hx, cy+hy, cz-hz),
        (cx-hx, cy-hy, cz+hz), (cx+hx, cy-hy, cz+hz),
        (cx+hx, cy+hy, cz+hz), (cx-hx, cy+hy, cz+hz),
    ]
    face_defs = [('-Z',(0,3,2,1)),('+Z',(4,5,6,7)),
                 ('-Y',(0,1,5,4)),('+Y',(2,3,7,6)),
                 ('-X',(3,0,4,7)),('+X',(1,2,6,5))]
    out_faces = [vids for tag, vids in face_defs if tag not in open_faces]
    return _finalize_mesh(name, verts, out_faces, base_color)


def make_cyl(name, center, radius, height, base_color, segments=8, axis='Z'):
    cx, cy, cz = center
    h2 = height / 2.0
    verts = []
    for ring in (0, 1):
        z_off = -h2 if ring == 0 else h2
        for i in range(segments):
            ang = 2.0 * math.pi * i / segments
            a = math.cos(ang) * radius
            b = math.sin(ang) * radius
            if axis == 'Z':
                verts.append((cx + a, cy + b, cz + z_off))
            elif axis == 'Y':
                verts.append((cx + a, cy + z_off, cz + b))
            else:
                verts.append((cx + z_off, cy + a, cz + b))
    faces = []
    for i in range(segments):
        ni = (i + 1) % segments
        faces.append([i, ni, ni + segments, i + segments])
    faces.append(list(reversed(range(segments))))
    faces.append(list(range(segments, segments * 2)))
    return _finalize_mesh(name, verts, faces, base_color)


# ════════════════════════════════════════════════════════════════
# SHELL
# ════════════════════════════════════════════════════════════════
def build_shell():
    make_box("Floor", (0.0, 4.5, -0.05), (12.4, 9.4, 0.10), COL_FLOOR_TILE)
    # Grout grid
    for i in range(-5, 6):
        make_box(f"Floor_GroutX_{i}", (i*1.0, 4.5, 0.005),
                 (0.02, 9.4, 0.001), COL_FLOOR_GROUT)
    for j in range(0, 10):
        make_box(f"Floor_GroutY_{j}", (0.0, float(j), 0.005),
                 (12.4, 0.02, 0.001), COL_FLOOR_GROUT)
    # Walls
    for sgn, xpos in [(-1, -6.0), (+1, +6.0)]:
        make_box(f"Wall_X{sgn:+d}", (xpos, 4.5, CEIL_Z/2.0),
                 (0.20, 9.4, CEIL_Z), COL_WALL_WHITE)
    make_box("Wall_N", (0.0, 9.0, CEIL_Z/2.0),
             (12.4, 0.20, CEIL_Z), COL_WALL_WHITE)
    # South wall — door at center, brand-blue panel
    make_box("Wall_S_W", (-3.80, 0.0, CEIL_Z/2.0),
             (4.40, 0.20, CEIL_Z), COL_WALL_NEXCORP)
    make_box("Wall_S_E", (+3.80, 0.0, CEIL_Z/2.0),
             (4.40, 0.20, CEIL_Z), COL_WALL_NEXCORP)
    make_box("Wall_S_AboveDoor", (0.0, 0.0, CEIL_Z - 0.30),
             (3.20, 0.20, 0.60), COL_WALL_NEXCORP)
    # Brand sign — NEXCORP letters on white panel on the south wall
    make_box("Brand_BG", (0.0, -0.02, 2.50), (3.00, 0.04, 0.36),
             (0.96, 0.96, 0.96, 1.0))
    make_box("Brand_Letters", (0.0, -0.04, 2.50), (2.40, 0.005, 0.20),
             COL_WALL_NEXCORP)
    # Glass door + frame
    make_box("Door_Frame_T", (0.0, 0.0, 2.10), (3.00, 0.10, 0.08),
             COL_METAL_STEEL)
    make_box("Door_Frame_B", (0.0, 0.0, 0.06), (3.00, 0.10, 0.08),
             COL_METAL_STEEL)
    make_box("Door_Glass", (0.0, 0.0, 1.05), (2.80, 0.04, 2.00), COL_GLASS)
    # South-side picture windows showing the canopy + pumps
    for sgn, cx in [(-1, -4.20), (+1, +4.20)]:
        make_box(f"Window_S_{sgn:+d}", (cx, -0.02, 1.65),
                 (2.20, 0.04, 1.40), COL_GLASS)
    # Ceiling
    make_box("Ceiling", (0.0, 4.5, CEIL_Z + 0.05),
             (12.4, 9.4, 0.10), COL_CEILING_TILE)
    # Fluorescent fixtures (less than Kwik Stop — fewer aisles).
    # Back row at 5.3, not 6.0 — at 6.0 the east tube crossed the
    # office's glass partition corner.
    for j, ypos in enumerate([2.5, 5.3]):
        for i in range(-1, 2):
            xp = i * 2.4
            make_box(f"Tube_{j}_{i}", (xp, ypos, CEIL_Z - 0.08),
                     (1.8, 0.40, 0.06), (0.96, 0.96, 0.92, 1.0))


# ════════════════════════════════════════════════════════════════
# COUNTER + REGISTER (Skip's post · NE)
# ════════════════════════════════════════════════════════════════
def build_counter():
    cx, cy = 3.5, 1.4
    make_box("Counter", (cx, cy, 0.50), (4.0, 0.60, 1.00), COL_COUNTER_LAMINATE)
    make_box("Counter_Top", (cx, cy, 1.04),
             (4.10, 0.70, 0.06), COL_METAL_BLACK)
    # Register
    make_box("Register_Body", (cx - 1.0, cy + 0.10, 1.25),
             (0.36, 0.40, 0.32), (0.20, 0.20, 0.22, 1.0))
    make_box("Register_Display", (cx - 1.0, cy + 0.32, 1.42),
             (0.30, 0.04, 0.10), (0.10, 0.32, 0.16, 1.0))
    # Fuel-pump controller (NexCorp distinctive — Kwik Stop doesn't have)
    make_box("PumpController", (cx + 0.5, cy + 0.10, 1.30),
             (0.80, 0.40, 0.40), (0.32, 0.34, 0.38, 1.0))
    make_box("PumpController_Screen", (cx + 0.5, cy + 0.32, 1.42),
             (0.74, 0.04, 0.20), (0.42, 0.62, 0.88, 1.0))
    # 8 pump-station status LEDs (a row, mostly green, one red)
    for i in range(8):
        led_col = (0.96, 0.18, 0.16, 1.0) if i == 3 else (0.32, 0.86, 0.42, 1.0)
        make_box(f"Pump_LED_{i}",
                 (cx + 0.5 - 0.30 + i * 0.08, cy + 0.34, 1.20),
                 (0.04, 0.005, 0.04), led_col)
    # Stool — BEHIND the counter (Skip's side). At cy+0.32 the seat
    # was buried 0.14m in the counter body.
    make_cyl("Stool_Seat", (cx, cy + 0.62, 0.66),
             0.16, 0.04, COL_LOCKER_GREY, segments=10)
    make_cyl("Stool_Post", (cx, cy + 0.62, 0.36),
             0.030, 0.56, COL_METAL_BLACK)
    make_cyl("Stool_Base", (cx, cy + 0.62, 0.05),
             0.20, 0.04, COL_METAL_BLACK, segments=8)
    # Back-wall cigarette + stock shelves — north wall, west of the
    # office. They used to sit at x≈4.0, y=8.85, which ran them
    # straight THROUGH the office's west glass partition.
    cig_x = 0.6
    cig_y = 8.78
    for sh in range(3):
        shz = 1.40 + sh * 0.42
        make_box(f"CigShelf_{sh}", (cig_x, cig_y, shz),
                 (3.20, 0.22, 0.02), (0.72, 0.60, 0.46, 1.0))
        for ci in range(12):
            box_x = cig_x - 1.45 + ci * 0.26
            make_box(f"CigBox_{sh}_{ci}",
                     (box_x, cig_y - 0.04, shz + 0.13),
                     (0.20, 0.12, 0.22),
                     SNACK_TINTS[(sh+ci) % len(SNACK_TINTS)])


# ════════════════════════════════════════════════════════════════
# LOCKER ROOM (back-NW · Locker #4 is Skip's, canonical)
# ════════════════════════════════════════════════════════════════
def build_lockers():
    # Lockers along the west wall, back half, Y ∈ [5.5, 8.5].
    # Doors/handles/vents/plates sit at lx + offset (EAST face,
    # toward the room). They were authored at lx - offset — the
    # entire bank presented its back to the room with every front
    # detail buried inside the west wall.
    lx = -5.62
    for i in range(6):
        ly = 5.7 + i * 0.55
        # Body
        make_box(f"Locker_{i+1}_Body", (lx, ly, 1.00),
                 (0.50, 0.50, 1.80), COL_LOCKER_GREY)
        # Door seam
        make_box(f"Locker_{i+1}_Door", (lx + 0.21, ly, 1.00),
                 (0.02, 0.48, 1.74), COL_LOCKER_DOORSEAM)
        # Handle
        make_box(f"Locker_{i+1}_Handle", (lx + 0.23, ly + 0.16, 1.00),
                 (0.02, 0.06, 0.06), COL_METAL_BLACK)
        # Vent grille
        for j in range(3):
            make_box(f"Locker_{i+1}_Vent_{j}",
                     (lx + 0.22, ly, 1.70 + j * 0.08),
                     (0.005, 0.30, 0.02), COL_METAL_BLACK)
        # Number plate — #4 is Skip's, paint it brass instead of paper
        plate_col = (0.78, 0.62, 0.30, 1.0) if (i + 1) == 4 else COL_PAPER
        make_box(f"Locker_{i+1}_Plate", (lx + 0.22, ly, 1.85),
                 (0.005, 0.18, 0.06), plate_col)
        # The combination lock on #4 (Skip's: ex-wife's birthday backward)
        if (i + 1) == 4:
            make_cyl(f"Locker_{i+1}_Lock", (lx + 0.24, ly - 0.04, 1.30),
                     0.04, 0.04, COL_METAL_BLACK, segments=10, axis='X')

    # Bench in front of lockers
    make_box("Locker_Bench_Seat", (lx + 0.6, 6.8, 0.40),
             (0.32, 2.50, 0.06), (0.42, 0.30, 0.18, 1.0))
    for sy in (-1, +1):
        make_box(f"Locker_Bench_Leg_{sy}",
                 (lx + 0.6, 6.8 + sy * 1.10, 0.20),
                 (0.32, 0.06, 0.40), (0.42, 0.30, 0.18, 1.0))
    # A spare uniform jacket hanging off the bench (NexCorp blue)
    make_box("Spare_Jacket", (lx + 0.48, 5.9, 0.65),
             (0.04, 0.30, 0.50), COL_WALL_NEXCORP)


# ════════════════════════════════════════════════════════════════
# MANAGER'S OFFICE (Skip's, back-east corner · glass partition)
# ════════════════════════════════════════════════════════════════
def build_office():
    # Glass partition wall — splits a small office at NE corner
    make_box("Office_PartW", (+3.0, 7.5, CEIL_Z/2.0),
             (0.10, 3.0, CEIL_Z), COL_GLASS)
    make_box("Office_PartN", (+4.5, 6.0, CEIL_Z/2.0),
             (3.0, 0.10, CEIL_Z), COL_GLASS)
    # Door cut at S of partition
    make_box("Office_Door", (+3.04, 6.5, 1.05),
             (0.04, 0.90, 2.10), (0.42, 0.30, 0.18, 1.0))
    # Desk
    dx, dy = 4.5, 7.5
    make_box("Desk_Top", (dx, dy, 0.74),
             (1.40, 0.70, 0.04), (0.36, 0.26, 0.18, 1.0))
    for sx in (-1, +1):
        for sy in (-1, +1):
            make_cyl(f"Desk_Leg_{sx}_{sy}",
                     (dx + sx * 0.62, dy + sy * 0.30, 0.37),
                     0.020, 0.74, (0.24, 0.18, 0.12, 1.0))
    # Computer monitor (the schedule + the dispatch log live here)
    make_box("Monitor_Body", (dx, dy + 0.16, 1.00),
             (0.50, 0.04, 0.36), (0.18, 0.18, 0.20, 1.0))
    make_box("Monitor_Screen", (dx, dy + 0.135, 1.00),
             (0.46, 0.001, 0.32), (0.16, 0.32, 0.56, 1.0))
    # Phone (Skip takes the dispatch calls here)
    make_box("Office_Phone", (dx + 0.50, dy, 0.81),
             (0.20, 0.30, 0.10), (0.32, 0.30, 0.28, 1.0))
    # Office chair
    make_box("OfficeChair_Seat", (dx, dy - 0.40, 0.46),
             (0.46, 0.46, 0.08), (0.18, 0.16, 0.16, 1.0))
    make_box("OfficeChair_Back", (dx, dy - 0.62, 1.00),
             (0.46, 0.06, 0.66), (0.18, 0.16, 0.16, 1.0))
    # 4-drawer file cabinet (Skip's dispatch records)
    make_box("FileCab", (+5.30, 8.50, 0.80),
             (0.50, 0.60, 1.60), COL_METAL_BLACK)
    for i in range(4):
        dz = 0.30 + i * 0.36
        make_box(f"FileCab_Drawer_{i}", (+5.30, 8.20, dz),
                 (0.46, 0.02, 0.30), COL_LOCKER_GREY)
        make_box(f"FileCab_Handle_{i}", (+5.30, 8.18, dz),
                 (0.16, 0.04, 0.04), COL_METAL_BLACK)


# ════════════════════════════════════════════════════════════════
# AUTO-SUPPLY AISLE (one aisle, free-standing, E-W) + COFFEE
# ════════════════════════════════════════════════════════════════
def build_floor_props():
    # Single short aisle (gas station, not a grocery)
    ax, ay = -1.0, 4.0
    make_box("Aisle_Base", (ax, ay, 0.10),
             (5.0, 0.80, 0.20), COL_COUNTER_LAMINATE)
    # Center spine panel the two shelf sides hang off (a real
    # gondola). The old "shelves" were built (5.0, 0.04, 0.30) —
    # thin VERTICAL walls, not shelf plates — so every product
    # floated, half-buried in a 30cm steel fin ("clipping through
    # each other at odd angles").
    make_box("Aisle_Spine", (ax, ay, 0.95), (5.0, 0.06, 1.50), COL_METAL_STEEL)
    for sh in range(3):
        shz = 0.50 + sh * 0.45
        for sy_sgn in (-1, +1):
            # Horizontal shelf plate, cantilevered off the spine
            make_box(f"Aisle_Shelf_{sh}_y{sy_sgn:+d}",
                     (ax, ay + sy_sgn * 0.21, shz),
                     (5.0, 0.36, 0.04), COL_METAL_STEEL)
            for p in range(10):
                px = ax - 2.25 + p * 0.50
                tint = SNACK_TINTS[(sh + p) % len(SNACK_TINTS)]
                ph = 0.20 + ((sh + p) % 3) * 0.05
                make_box(f"Aisle_Product_{sh}_y{sy_sgn:+d}_{p}",
                         (px, ay + sy_sgn * 0.23, shz + 0.02 + ph / 2.0),
                         (0.16, 0.20, ph), tint)
    # Aisle top sign — corporate blue
    make_box("Aisle_Sign", (ax, ay, 2.30),
             (5.0, 0.10, 0.26), COL_WALL_NEXCORP)

    # Coffee station, simpler than Kwik Stop (gas-station coffee)
    cfx = -5.0
    make_box("Coffee_Counter", (cfx, 3.5, 0.86),
             (1.20, 3.00, 0.04), COL_COUNTER_LAMINATE)
    make_box("Coffee_Base", (cfx, 3.5, 0.42),
             (1.20, 3.00, 0.84), COL_METAL_BLACK)
    # Two pots, no slurpees
    for i, tint in enumerate([(0.18, 0.10, 0.06, 1.0),
                              (0.42, 0.32, 0.20, 1.0)]):
        pot_y = 2.5 + i * 1.50
        make_cyl(f"Coffee_Pot_{i}", (cfx - 0.10, pot_y, 1.10),
                 0.10, 0.30, COL_GLASS, segments=8)
        make_cyl(f"Coffee_Liquid_{i}", (cfx - 0.10, pot_y, 1.04),
                 0.085, 0.20, tint, segments=8)
        make_cyl(f"Coffee_Burner_{i}", (cfx - 0.10, pot_y, 0.91),
                 0.13, 0.02, COL_METAL_BLACK, segments=8)
    # Cup stack
    for i in range(5):
        make_cyl(f"Coffee_Cup_{i}", (cfx + 0.25, 2.5, 0.90 + i * 0.04),
                 0.04, 0.04, (0.92, 0.86, 0.74, 1.0), segments=10)

    # Beer fridge (single door, smaller than Kwik Stop's wall of them).
    # North wall, between the locker room and Skip's office — it was
    # at (-5.5, 8.0), which is INSIDE the locker bank: lockers 5-6,
    # the bench end and the west wall all ran through its body.
    fx, fy = -3.6, 8.35
    make_box("BeerFridge_Body", (fx, fy, 1.20),
             (1.00, 0.80, 2.30), (0.42, 0.42, 0.46, 1.0))
    make_box("BeerFridge_Glass", (fx, fy - 0.36, 1.20),
             (0.92, 0.04, 2.20), (0.46, 0.78, 0.92, 0.55))
    # Visible six-packs
    for sh in range(4):
        shz = 0.30 + sh * 0.50
        make_box(f"BeerFridge_Shelf_{sh}",
                 (fx, fy, shz),
                 (0.94, 0.70, 0.02), COL_METAL_STEEL)
        for b in range(3):
            bx = fx - 0.30 + b * 0.30
            make_box(f"BeerFridge_Sixpack_{sh}_{b}",
                     (bx, fy, shz + 0.20),
                     (0.24, 0.24, 0.30), SNACK_TINTS[(sh+b) % len(SNACK_TINTS)])

    # Restroom door — west wall, marked with M/W signs
    make_box("Restroom_Door", (-5.96, 1.4, 1.05),
             (0.04, 0.90, 2.10), (0.42, 0.30, 0.18, 1.0))
    make_box("Restroom_Sign", (-5.94, 1.4, 2.30),
             (0.02, 0.30, 0.10), (0.96, 0.96, 0.96, 1.0))


# ════════════════════════════════════════════════════════════════
# EXTERIOR HINT — pump canopy + 2 pumps visible through south window
# ════════════════════════════════════════════════════════════════
def build_pump_canopy():
    # The canopy is OUTSIDE (south of the building) — show through window
    cy = -4.0
    # Canopy slab
    make_box("Canopy_Roof", (0.0, cy, 4.50),
             (10.0, 5.0, 0.30), (0.42, 0.44, 0.48, 1.0))
    # NexCorp brand band on canopy edge (visible through window)
    make_box("Canopy_Band", (0.0, cy - 2.40, 4.30),
             (10.2, 0.10, 0.40), COL_WALL_NEXCORP)
    # 4 support columns
    for sx in (-3.5, +3.5):
        for sy in (cy - 2.0, cy + 2.0):
            make_cyl(f"Canopy_Post_{sx}_{sy}", (sx, sy, 2.20),
                     0.20, 4.40, (0.62, 0.62, 0.60, 1.0))
    # 2 fuel pumps (between the columns)
    for i, px in enumerate([-1.5, +1.5]):
        # Body
        make_box(f"Pump_{i}_Body", (px, cy, 1.00),
                 (0.60, 0.50, 2.00), (0.32, 0.34, 0.38, 1.0))
        # Display
        make_box(f"Pump_{i}_Display", (px, cy - 0.26, 1.40),
                 (0.50, 0.04, 0.30), (0.42, 0.62, 0.88, 1.0))
        # Hose holster
        make_cyl(f"Pump_{i}_Hose", (px - 0.20, cy - 0.16, 0.80),
                 0.04, 0.40, COL_METAL_BLACK)
        # Nozzle
        make_box(f"Pump_{i}_Nozzle", (px - 0.20, cy - 0.20, 0.50),
                 (0.06, 0.18, 0.14), COL_METAL_BLACK)
    # Asphalt slab visible through window (the lot in front)
    make_box("Lot_Asphalt", (0.0, cy, -0.05),
             (10.0, 5.0, 0.10), (0.20, 0.20, 0.22, 1.0))


# ════════════════════════════════════════════════════════════════
# EXPORT
# ════════════════════════════════════════════════════════════════
def export_glb():
    out_dir = os.path.normpath(
        os.path.join(os.path.dirname(os.path.abspath(__file__)), OUTPUT_DIR))
    os.makedirs(out_dir, exist_ok=True)
    out_path = os.path.join(out_dir, OUTPUT_NAME)
    print(f"\n[build_nexcorp_gas_go] exporting to {out_path}")
    bpy.ops.object.select_all(action='SELECT')
    base = {'filepath': out_path, 'export_format': 'GLB',
            'use_selection': False, 'export_apply': True,
            'export_lights': False, 'export_cameras': False}
    rna = bpy.ops.export_scene.gltf.get_rna_type()
    legacy = {}
    if 'export_colors' in rna.properties: legacy['export_colors'] = True
    if 'export_normals' in rna.properties: legacy['export_normals'] = True
    try:
        bpy.ops.export_scene.gltf(**base, **legacy)
    except Exception as e:
        print(f"[build_nexcorp_gas_go] ✗ EXPORT FAILED: {e}")
        raise
    if os.path.exists(out_path):
        print(f"[build_nexcorp_gas_go] ✓ wrote {out_path} ({os.path.getsize(out_path)} bytes)")


def build_hero_props_2026_09():
    """HERO PROPS FOR THE BLIND CUES (shot_marker_audit, 2026-09-01).

    Five distinct cues; the phone cue aims at the existing
    Office_Phone (Skip's dispatch line). Built:

    - THE BLACK PICKUP ("a black pickup truck with Louisiana
      plates ... pulls around to the lot behind the car wash,
      which is ... not visible from the street or from the
      counter window"): on a back-lot pad north-east of the
      building — body, cab, tailgate, Louisiana plate, four
      wheels.
    - THE ENVELOPE ("a small manila envelope ... not sealed"):
      flat in the pickup's bed — the hand-off's residue.
    - THE THERMOMETER (stuck at 97 for three summers): a round
      dial + needle on the nearest canopy post.
    - THE FOLDER ("a folder on his workstation labeled
      PENDING — R"): manila folder + tab on the office desk.
    """
    black = (0.10, 0.10, 0.11, 1.0)
    manila = (0.82, 0.72, 0.50, 1.0)
    # ── THE BLACK PICKUP · back lot, NE of the building ──
    make_box("Backlot_Pad", (8.6, 1.5, -0.03), (4.5, 7.0, 0.05),
             (0.40, 0.40, 0.41, 1.0))
    make_box("Pickup_Body", (8.6, 1.6, 0.78), (1.90, 4.60, 0.60), black)
    make_box("Pickup_Cab", (8.6, 2.35, 1.38), (1.75, 1.55, 0.60),
             (0.13, 0.13, 0.15, 1.0))
    make_box("Pickup_Tailgate", (8.6, -0.73, 0.83), (1.80, 0.06, 0.55), black)
    make_box("Louisiana_Plate", (8.6, -0.767, 0.62), (0.30, 0.008, 0.15),
             (0.86, 0.84, 0.76, 1.0))
    for wi, (wx2, wy2) in enumerate(((7.525, 2.6), (9.675, 2.6),
                                     (7.525, 0.0), (9.675, 0.0))):
        make_cyl(f"Pickup_Wheel_{wi}", (wx2, wy2, 0.36), 0.36, 0.25,
                 (0.16, 0.16, 0.17, 1.0), axis='X', segments=10)
    # ── THE ENVELOPE · flat in the bed ──
    make_box("Manila_Envelope", (8.6, 0.10, 1.0815), (0.24, 0.16, 0.003), manila)
    # ── THE THERMOMETER · on the SW canopy post ──
    make_cyl("Lot_Thermometer", (-3.5, -1.78, 1.70), 0.09, 0.030,
             (0.92, 0.90, 0.85, 1.0), axis='Y', segments=10)
    make_box("Thermometer_Needle_97", (-3.53, -1.760, 1.72), (0.050, 0.006, 0.008),
             (0.80, 0.22, 0.18, 1.0))
    # ── THE FOLDER · PENDING — R, on the office desk (top 0.76) ──
    make_box("Pending_Folder", (4.05, 7.35, 0.766), (0.24, 0.32, 0.010), manila)
    make_box("Pending_Folder_Tab", (3.92, 7.54, 0.7725), (0.060, 0.090, 0.003),
             (0.76, 0.64, 0.42, 1.0))


def main():
    clear_scene()
    build_shell()
    build_counter()
    build_lockers()
    build_office()
    build_floor_props()
    build_pump_canopy()
    build_hero_props_2026_09()
    export_glb()


if __name__ == "__main__":
    main()
