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

# (2026-10-06) packaging, not primaries: a gas station's shelves read by
# their BRAND grammar — a bag with a band and a crimp, a tray of bars, a
# quart of oil with its cap — never by a solid saturated block
BRAND_TINTS = [
    (0.80, 0.18, 0.14, 1.0), (0.16, 0.30, 0.62, 1.0), (0.94, 0.74, 0.16, 1.0),
    (0.24, 0.50, 0.26, 1.0), (0.44, 0.20, 0.46, 1.0), (0.90, 0.46, 0.14, 1.0),
    (0.12, 0.12, 0.14, 1.0), (0.86, 0.84, 0.80, 1.0),
]
BAND_TINTS = [(0.96, 0.86, 0.30, 1.0), (0.96, 0.96, 0.94, 1.0), (0.82, 0.16, 0.14, 1.0), (0.14, 0.14, 0.16, 1.0)]


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


def _make_box_vendored(name, center, size, base_color, open_faces=None):
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


def make_box(name, center, size, base_color, open_faces=None):
    """DETAIL DRAFT 3 (2026-09-06): delegates to the shared
    _props.geometry.make_box so this set gets the auto-chamfer policy
    (prop-sized boxes get cut edges; walls, floors, plates stay as
    they were). The vendored flat-color box remains as the fallback
    when _props is not importable."""
    try:
        import sys as _sys, os as _os
        _bt = _os.path.dirname(_os.path.abspath(__file__))
        for _c in (_bt, _os.path.dirname(_bt)):
            if _os.path.isdir(_os.path.join(_c, "_props")) and _c not in _sys.path:
                _sys.path.insert(0, _c)
        from _props.geometry import make_box as _shared
    except Exception:
        return _make_box_vendored(name, center, size, base_color, open_faces)
    return _shared(name, center, size, base_color, open_faces)


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
    # (2026-10-06: the two picture windows were glass panes on SOLID
    # walls — the store could not see its own pumps. Cut.)
    from _props.structure import make_wall_with_openings
    make_wall_with_openings("Wall_S_W", (-3.80, 0.0, 0), length=4.40, height=CEIL_Z, axis='X',
                            palette={"wall": COL_WALL_NEXCORP, "baseboard": COL_METAL_BLACK},
                            baseboard_face_sign=+1, openings=[(-4.20, 1.65, 2.20, 1.40)])
    make_wall_with_openings("Wall_S_E", (+3.80, 0.0, 0), length=4.40, height=CEIL_Z, axis='X',
                            palette={"wall": COL_WALL_NEXCORP, "baseboard": COL_METAL_BLACK},
                            baseboard_face_sign=+1, openings=[(+4.20, 1.65, 2.20, 1.40)])
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
    make_box("Door_Frame_B", (0.0, 0.0, 0.04), (3.00, 0.10, 0.08),   # on the floor
             COL_METAL_STEEL)
    make_box("Door_Glass", (0.0, 0.0, 1.05), (2.80, 0.04, 2.00), COL_GLASS)
    # South-side picture windows showing the canopy + pumps
    for sgn, cx in [(-1, -4.20), (+1, +4.20)]:
        make_box(f"Window_S_{sgn:+d}", (cx, 0.0, 1.65),
                 (2.20, 0.012, 1.40), (0.70, 0.82, 0.86, 0.22))
        for k, (dx, w) in enumerate(((-1.06, 0.08), (1.06, 0.08), (0.0, 0.05))):
            make_box(f"Window_S_{sgn:+d}_Mullion_{k}", (cx + dx, 0.0, 1.65), (w, 0.10, 1.40), COL_METAL_STEEL)
        for k, z in enumerate((0.97, 2.33)):
            make_box(f"Window_S_{sgn:+d}_Rail_{k}", (cx, 0.0, z), (2.20, 0.10, 0.06), COL_METAL_STEEL)
        # the window decals: hours, the rewards card, a hiring sign
        make_box(f"Window_S_{sgn:+d}_Decal", (cx - 0.55 * sgn, 0.012, 1.20), (0.40, 0.003, 0.28),
                 (0.96, 0.96, 0.94, 1.0) if sgn < 0 else (0.94, 0.80, 0.20, 1.0))
    # Ceiling
    make_box("Ceiling", (0.0, 4.5, CEIL_Z + 0.05),
             (12.4, 9.4, 0.10), COL_CEILING_TILE)
    # Fluorescent fixtures (less than Kwik Stop — fewer aisles).
    # Back row at 5.3, not 6.0 — at 6.0 the east tube crossed the
    # office's glass partition corner.
    for j, ypos in enumerate([2.5, 5.3]):
        for i in range(-1, 2):
            xp = i * 2.4
            make_box(f"Tube_{j}_{i}", (xp, ypos, CEIL_Z - 0.03),   # against the ceiling (2026-09-22: 5 cm short)
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
    make_box("Register_Body", (cx - 1.0, cy + 0.10, 1.23),   # on the top
             (0.36, 0.40, 0.32), (0.20, 0.20, 0.22, 1.0))
    make_box("Register_Display", (cx - 1.0, cy + 0.32, 1.40),
             (0.30, 0.04, 0.10), (0.10, 0.32, 0.16, 1.0))
    # Fuel-pump controller (NexCorp distinctive — Kwik Stop doesn't have)
    make_box("PumpController", (cx + 0.5, cy + 0.10, 1.27),   # on the top (2026-09-23: 3 cm over it)
             (0.80, 0.40, 0.40), (0.32, 0.34, 0.38, 1.0))
    make_box("PumpController_Screen", (cx + 0.5, cy + 0.32, 1.39),
             (0.74, 0.04, 0.20), (0.42, 0.62, 0.88, 1.0))
    # 8 pump-station status LEDs (a row, mostly green, one red)
    for i in range(8):
        led_col = (0.96, 0.18, 0.16, 1.0) if i == 3 else (0.32, 0.86, 0.42, 1.0)
        make_box(f"Pump_LED_{i}",
                 (cx + 0.5 - 0.30 + i * 0.08, cy + 0.3025, 1.17),   # on the controller's face (2026-09-22: 4 cm off it)
                 (0.04, 0.005, 0.04), led_col)
    # Stool — BEHIND the counter (Skip's side). At cy+0.32 the seat
    # was buried 0.14m in the counter body.
    make_cyl("Stool_Seat", (cx, cy + 0.62, 0.66),
             0.16, 0.04, COL_LOCKER_GREY, segments=10)
    make_cyl("Stool_Post", (cx, cy + 0.62, 0.34),
             0.030, 0.60, COL_METAL_BLACK)
    make_cyl("Stool_Base", (cx, cy + 0.62, 0.02),   # on the floor
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
        make_box(f"Locker_{i+1}_Kick", (lx, ly, 0.05), (0.46, 0.46, 0.10), COL_METAL_BLACK)   # (2026-09-23: the bank stood 10 cm up on nothing)
        # Door seam
        make_box(f"Locker_{i+1}_Door", (lx + 0.21, ly, 1.00),
                 (0.02, 0.48, 1.74), COL_LOCKER_DOORSEAM)
        # Handle
        make_box(f"Locker_{i+1}_Handle", (lx + 0.23, ly + 0.16, 1.00),
                 (0.02, 0.06, 0.06), COL_METAL_BLACK)
        # Vent grille
        for j in range(3):
            make_box(f"Locker_{i+1}_Vent_{j}",
                     (lx + 0.22 + 0.0331, ly, 1.70 + j * 0.08),
                     (0.005, 0.30, 0.02), COL_METAL_BLACK)
        # Number plate — #4 is Skip's, paint it brass instead of paper
        plate_col = (0.78, 0.62, 0.30, 1.0) if (i + 1) == 4 else COL_PAPER
        make_box(f"Locker_{i+1}_Plate", (lx + 0.22 + 0.0331, ly, 1.85),
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
    dx, dy = 4.5, 8.5     # against Wall_N (y 9.0, inner face 8.9)
    make_box("Desk_Top", (dx, dy, 0.74),
             (1.40, 0.70, 0.04), (0.36, 0.26, 0.18, 1.0))
    for sx in (-1, +1):
        for sy in (-1, +1):
            make_cyl(f"Desk_Leg_{sx}_{sy}",
                     (dx + sx * 0.62, dy + sy * 0.30, 0.37),
                     0.020, 0.74, (0.24, 0.18, 0.12, 1.0))
    # Computer monitor (the schedule + the dispatch log live here)
    make_box("Monitor_Stand", (dx, dy + 0.16, 0.79), (0.16, 0.12, 0.06), (0.18, 0.18, 0.20, 1.0))   # (2026-09-22: the monitor hung 6 cm over the desk)
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
    # pedestal + base (2026-09-08: the seat hung in the air)
    make_cyl("OfficeChair_Post", (dx, dy - 0.40, 0.22), 0.03, 0.44, COL_METAL_BLACK, segments=8)
    make_cyl("OfficeChair_Base", (dx, dy - 0.40, 0.02), 0.28, 0.04, COL_METAL_BLACK, segments=12)
    make_box("OfficeChair_Back", (dx, dy - 0.62, 0.760),
             (0.46, 0.06, 0.50), (0.18, 0.16, 0.16, 1.0))
    # 4-drawer file cabinet (Skip's dispatch records)
    make_box("FileCab", (+5.62, 8.50, 0.80),
             (0.50, 0.60, 1.60), COL_METAL_BLACK)
    for i in range(4):
        dz = 0.30 + i * 0.36
        make_box(f"FileCab_Drawer_{i}", (+5.62, 8.20, dz),
                 (0.46, 0.02, 0.30), COL_LOCKER_GREY)
        make_box(f"FileCab_Handle_{i}", (+5.62, 8.18, dz),
                 (0.16, 0.04, 0.04), COL_METAL_BLACK)


# ════════════════════════════════════════════════════════════════
# AUTO-SUPPLY AISLE (one aisle, free-standing, E-W) + COFFEE
# ════════════════════════════════════════════════════════════════
def build_floor_props():
    # Single short aisle (gas station, not a grocery)
    ax, ay = -0.8, 4.0      # (2026-10-07: 0.86 m to the coffee bar at -1.0)
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
    # Aisle top sign — corporate blue
    make_box("Aisle_Sign", (ax, ay, 2.30),
             (5.0, 0.10, 0.26), COL_WALL_NEXCORP)
    for e in (-1, 1):   # hung from the ceiling (2026-09-22: it hung on nothing)
        make_cyl(f"Aisle_Sign_Wire_{e:+d}", (ax + e * 2.0, ay, (2.43 + CEIL_Z) / 2.0), 0.006, CEIL_Z - 2.43, COL_METAL_STEEL, segments=4)

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
        make_cyl(f"Coffee_Pot_{i}", (cfx - 0.10, pot_y, 1.05),   # on its burner
                 0.10, 0.30, COL_GLASS, segments=8)
        make_cyl(f"Coffee_Liquid_{i}", (cfx - 0.10, pot_y, 1.00),
                 0.085, 0.20, tint, segments=8)
        make_cyl(f"Coffee_Burner_{i}", (cfx - 0.10, pot_y, 0.89),   # on the counter (2026-09-23: 2 cm over it)
                 0.13, 0.02, COL_METAL_BLACK, segments=8)
    # Cup stack
    for i in range(5):
        make_cyl(f"Coffee_Cup_{i}", (cfx + 0.25, 2.5, 0.90 + i * 0.04),
                 0.04, 0.04, (0.92, 0.86, 0.74, 1.0), segments=10)

    # Beer fridge (single door, smaller than Kwik Stop's wall of them).
    # North wall, between the locker room and Skip's office — it was
    # at (-5.5, 8.0), which is INSIDE the locker bank: lockers 5-6,
    # the bench end and the west wall all ran through its body.
    fx, fy = -3.6, 8.50   # its back on the N wall's face (2026-09-25: 15 cm off it)
    from _props.structure import make_case_shell   # make_box's delegate has put _props on the path
    # an open shell (2026-09-24: a solid body with the shelves and
    # six-packs inside it, behind a glass slab that renders opaque)
    make_case_shell("BeerFridge_Body", (fx, fy, 1.15),   # on the floor (2026-09-22: 5 cm up)
                    (1.00, 0.80, 2.30), (0.42, 0.42, 0.46, 1.0), open_face='-Y')
    for gi, (gx, gw) in enumerate(((-0.26, 0.03), (-0.19, 0.012))):
        make_box(f"BeerFridge_Glint_{gi}", (fx + gx, fy - 0.385, 1.15), (gw, 0.004, 2.26), (0.86, 0.90, 0.92, 1.0))
    # Visible six-packs
    for sh in range(4):
        shz = 0.30 + sh * 0.50
        make_box(f"BeerFridge_Shelf_{sh}",
                 (fx, fy + 0.005, shz),
                 (0.96, 0.75, 0.02), COL_METAL_STEEL)   # side to side, to the back panel
        for b in range(3):
            bx = fx - 0.30 + b * 0.30
            carton = BRAND_TINTS[(sh * 3 + b) % len(BRAND_TINTS)]
            make_box(f"BeerFridge_Sixpack_{sh}_{b}",
                     (bx, fy, shz + 0.01 + 0.065),   # a carrier of six cans (2026-10-06: was a 30 cm block)
                     (0.24, 0.16, 0.13), carton)
            make_box(f"BeerFridge_Sixpack_{sh}_{b}_Band", (bx, fy - 0.081, shz + 0.01 + 0.08), (0.24, 0.003, 0.04), (0.94, 0.92, 0.86, 1.0))
            for ci in range(6):
                make_cyl(f"BeerFridge_Sixpack_{sh}_{b}_Can_{ci}", (bx - 0.075 + (ci % 3) * 0.075, fy - 0.035 + (ci // 3) * 0.07, shz + 0.01 + 0.14),
                         0.032, 0.02, (0.76, 0.78, 0.80, 1.0), segments=8)

    # Restroom door — west wall, marked with M/W signs
    make_box("Restroom_Door", (-5.96, 1.4, 1.05),
             (0.04, 0.90, 2.10), (0.42, 0.30, 0.18, 1.0))
    make_box("Restroom_Sign", (-5.94, 1.4, 2.30),
             (0.02, 0.30, 0.10), (0.96, 0.96, 0.96, 1.0))


# ════════════════════════════════════════════════════════════════
# MERCHANDISE (2026-10-06 · vol 6 contact sheet: "toy blocks")
# ════════════════════════════════════════════════════════════════
def _merch_section(tag, kind, x0, front_y, sgn, z0, k):
    """One 0.48 m facing — the grammar lives in _props/merch.py now (it
    began here, 2026-10-06, and the shelving kit and the Kwik Stop share
    it). make_box's delegate has put _props on the path by this call."""
    from _props.merch import merch_section
    merch_section(tag, kind, x0, front_y, sgn, z0, k, width=0.48)


def build_merchandise_2026_10():
    """The aisle stocked as a gas station stocks it — snacks up top,
    candy and jerky at the hand, auto supply at the shins; price strips
    on every shelf edge; end caps; the water stacked at the counter end.
    Skip's counter: the lottery case, the impulse rack, his phone and
    his vape; the cigarette wall as packs; a roller grill by the coffee."""
    ax, ay = -0.8, 4.0      # (2026-10-07: 0.86 m to the coffee bar at -1.0)
    plan = {0: ("oil", "jug", "oil", "jug", "oil", "jug", "oil", "jug", "oil", "jug"),
            1: ("candy", "jerky", "candy", "nuts", "candy", "jerky", "candy", "nuts", "candy", "jerky"),
            2: ("chips", "chips", "tubes", "cookies", "chips", "chips", "tubes", "cookies", "chips", "chips")}
    for sh in range(3):
        shz = 0.50 + sh * 0.45
        top = shz + 0.02
        for sgn in (-1, +1):
            front_y = ay + sgn * 0.39
            for p, kind in enumerate(plan[sh] if sgn < 0 else tuple(reversed(plan[sh]))):
                x0 = ax - 2.48 + p * 0.50
                _merch_section(f"Aisle_Stock_{sh}_y{sgn:+d}_{p}", kind, x0, front_y, sgn, top, sh * 7 + p + (3 if sgn > 0 else 0))
            make_box(f"Aisle_Price_Strip_{sh}_y{sgn:+d}", (ax, front_y + sgn * 0.003, shz - 0.002), (5.0, 0.006, 0.04),
                     (0.94, 0.94, 0.92, 1.0))
            for p in range(10):
                make_box(f"Aisle_Price_Strip_{sh}_y{sgn:+d}_Tag_{p}", (ax - 2.30 + p * 0.50, front_y + sgn * 0.0065, shz - 0.002),
                         (0.05, 0.002, 0.028), (0.96, 0.84, 0.20, 1.0) if (p + sh) % 4 == 0 else (0.98, 0.98, 0.96, 1.0))
    # end panels and the water at the counter end
    for e in (-1, 1):
        make_box(f"Aisle_End_Panel_{e:+d}", (ax + e * 2.52, ay, 0.95), (0.04, 0.80, 1.70), COL_METAL_STEEL)
    for k in range(3):
        for j in range(2):
            make_box(f"Aisle_Endcap_Water_{k}_{j}", (ax + 2.78, ay - 0.15 + j * 0.30, 0.11 + k * 0.22), (0.40, 0.28, 0.22),
                     (0.70, 0.82, 0.92, 1.0))
            make_box(f"Aisle_Endcap_Water_{k}_{j}_Label", (ax + 2.981, ay - 0.15 + j * 0.30, 0.11 + k * 0.22), (0.003, 0.20, 0.08),
                     (0.16, 0.30, 0.62, 1.0))
    make_box("Aisle_Endcap_Water_Sign", (ax + 2.78, ay, 0.75), (0.36, 0.02, 0.18), (0.96, 0.86, 0.20, 1.0))

    # Skip's counter (top at 1.07): the lottery case, the impulse rack on the
    # customer face, and on his side his phone and his vape
    cx, cy = 3.5, 1.4
    top = 1.07
    make_box("Lottery_Case", (cx + 1.45, cy - 0.05, top + 0.18), (0.56, 0.24, 0.36), (0.80, 0.86, 0.90, 1.0))
    for k in range(6):
        make_box(f"Lottery_Case_Roll_{k}", (cx + 1.24 + k * 0.085, cy - 0.17, top + 0.18), (0.07, 0.004, 0.30),
                 BRAND_TINTS[(k * 3) % len(BRAND_TINTS)])
    make_box("Impulse_Rack", (cx - 0.20, cy - 0.33, 0.60), (1.10, 0.06, 0.70), COL_METAL_BLACK)
    for r in range(3):
        for k in range(8):
            make_box(f"Impulse_Rack_Gum_{r}_{k}", (cx - 0.68 + k * 0.135, cy - 0.366, 0.38 + r * 0.22), (0.11, 0.012, 0.16),
                     BRAND_TINTS[(r * 5 + k) % len(BRAND_TINTS)])
    make_box("Skip_Phone", (cx - 0.35, cy + 0.22, top + 0.004), (0.075, 0.15, 0.008), (0.10, 0.10, 0.12, 1.0))
    make_box("Skip_Phone_Screen", (cx - 0.35, cy + 0.22, top + 0.0085), (0.065, 0.13, 0.001), (0.36, 0.52, 0.70, 1.0))
    make_cyl("Skip_Vape", (cx - 0.20, cy + 0.20, top + 0.009), 0.009, 0.11, (0.22, 0.24, 0.30, 1.0), axis='X', segments=6)
    make_cyl("Skip_Vape_Tip", (cx - 0.14, cy + 0.20, top + 0.009), 0.006, 0.02, (0.70, 0.72, 0.74, 1.0), axis='X', segments=6)
    make_cyl("Tip_Jar", (cx - 1.55, cy - 0.10, top + 0.08), 0.06, 0.16, (0.80, 0.86, 0.90, 1.0), segments=10)
    make_box("Tip_Jar_Label", (cx - 1.55, cy - 0.161, top + 0.08), (0.06, 0.002, 0.04), (0.94, 0.92, 0.86, 1.0))

    # the cigarette wall as PACKS, by brand, and the vape row under it
    cig_x, cig_y = 0.6, 8.78
    brands = ((0.96, 0.96, 0.94, 1.0), (0.82, 0.16, 0.14, 1.0), (0.86, 0.72, 0.36, 1.0), (0.22, 0.52, 0.32, 1.0),
              (0.16, 0.30, 0.62, 1.0), (0.12, 0.12, 0.14, 1.0))
    for sh in range(3):
        shz = 1.40 + sh * 0.42
        for k in range(26):
            px = cig_x - 1.50 + k * 0.12
            col = brands[(k // 4 + sh) % len(brands)]
            for r in range(2):
                make_box(f"CigShelf_{sh}_Pack_{k}_{r}", (px + r * 0.055, cig_y - 0.05, shz + 0.055), (0.05, 0.025, 0.09), col)
            make_box(f"CigShelf_{sh}_Pack_{k}_Cap", (px + 0.0275, cig_y - 0.0635, shz + 0.085), (0.105, 0.002, 0.03),
                     (0.94, 0.94, 0.92, 1.0) if col != (0.96, 0.96, 0.94, 1.0) else (0.82, 0.16, 0.14, 1.0))
    make_box("CigShelf_Header", (cig_x, cig_y + 0.11, 2.72), (3.20, 0.02, 0.18), COL_WALL_NEXCORP)

    # a roller grill by the coffee: eight rollers, five dogs
    gx, gy = -5.0, 4.55
    make_box("Roller_Grill_Base", (gx, gy, 0.94), (0.46, 0.40, 0.12), COL_METAL_STEEL)
    for k in range(8):
        make_cyl(f"Roller_Grill_Roller_{k}", (gx, gy - 0.16 + k * 0.045, 1.012), 0.014, 0.40, (0.78, 0.78, 0.76, 1.0),
                 axis='X', segments=6)
    for k in (1, 2, 4, 5, 7):
        make_cyl(f"Roller_Grill_Dog_{k}", (gx, gy - 0.16 + k * 0.045, 1.036), 0.012, 0.16, (0.70, 0.30, 0.20, 1.0),
                 axis='X', segments=6)
    make_box("Roller_Grill_Sneeze_Guard", (gx, gy, 1.16), (0.46, 0.40, 0.006), (0.80, 0.86, 0.90, 0.6))
    for e in (-1, 1):
        make_box(f"Roller_Grill_Sneeze_Guard_Post_{e:+d}", (gx + e * 0.22, gy + 0.18, 1.08), (0.015, 0.015, 0.16), COL_METAL_STEEL)


def build_skips_side_2026_10():
    """Skip's side of the counter and the east wall (2026-10-06: the
    preset looks over his shoulder and saw a bare black slab and a
    blank wall). Under the counter: open shelves with the bag rolls, the
    drop safe, the receipt rolls, his little cooler, the trash can; the
    fatigue mat he stands on. The east wall: the ice merchandiser, the
    ATM, the hiring poster."""
    cx, cy = 3.5, 1.4
    back = cy + 0.30                            # the counter body's north face
    # on the floor against the body's back face (it is a solid box): the
    # case of bags, the drop safe with the receipt rolls on it
    make_box("Counter_Back_Bags_Case", (cx - 1.30, back + 0.10, 0.065), (0.50, 0.20, 0.13), (0.94, 0.94, 0.92, 1.0))
    make_box("Counter_Back_Bags_Case_Logo", (cx - 1.30, back + 0.201, 0.065), (0.20, 0.003, 0.08), COL_WALL_NEXCORP)
    make_box("Counter_Back_Safe", (cx + 0.60, back + 0.14, 0.21), (0.46, 0.28, 0.42), (0.20, 0.20, 0.22, 1.0))
    make_cyl("Counter_Back_Safe_Dial", (cx + 0.60, back + 0.285, 0.26), 0.035, 0.012, (0.70, 0.70, 0.68, 1.0), axis='Y', segments=10)
    make_box("Counter_Back_Safe_Slot", (cx + 0.60, back + 0.282, 0.38), (0.24, 0.004, 0.02), (0.08, 0.08, 0.09, 1.0))
    for k in range(4):
        make_cyl(f"Counter_Back_Safe_Receipt_Roll_{k}", (cx + 0.47 + k * 0.09, back + 0.14, 0.46), 0.04, 0.08, (0.96, 0.96, 0.94, 1.0),
                 axis='Y', segments=10)
    make_box("Skip_Cooler", (cx + 1.25, back + 0.24, 0.20), (0.46, 0.32, 0.40), (0.86, 0.22, 0.18, 1.0))
    make_box("Skip_Cooler_Lid", (cx + 1.25, back + 0.24, 0.415), (0.48, 0.34, 0.03), (0.94, 0.94, 0.92, 1.0))
    make_cyl("Skip_Cooler_Energy_Can", (cx + 1.18, back + 0.24, 0.49), 0.03, 0.12, (0.16, 0.16, 0.18, 1.0), segments=8)
    make_box("Skip_Fatigue_Mat", (cx, back + 0.55, 0.008), (2.40, 0.70, 0.016), (0.12, 0.12, 0.13, 1.0))
    make_cyl("Counter_Back_Trash", (cx - 1.75, back + 0.30, 0.28), 0.17, 0.56, (0.26, 0.28, 0.30, 1.0), segments=12)
    make_cyl("Counter_Back_Trash_Liner", (cx - 1.75, back + 0.30, 0.565), 0.175, 0.03, (0.10, 0.10, 0.10, 1.0), segments=12)
    # the east wall: the ice merchandiser by the door, the ATM, the poster
    # the ice merchandiser stands OUTSIDE by the door, as gas stations keep
    # it (2026-10-07: inside it left 0.38 m to the counter and 0.90 m to
    # the ATM); seen through the east picture window
    ix, iy = 2.45, -0.62
    make_box("Ice_Merchandiser", (ix, iy, 0.95), (1.30, 0.76, 1.90), (0.96, 0.96, 0.96, 1.0))
    make_box("Ice_Merchandiser_Band", (ix, iy - 0.381, 1.62), (1.30, 0.004, 0.34), (0.16, 0.40, 0.72, 1.0))
    make_box("Ice_Merchandiser_Lettering", (ix, iy - 0.384, 1.62), (0.70, 0.002, 0.20), (0.96, 0.96, 0.96, 1.0))
    for k in range(2):
        make_box(f"Ice_Merchandiser_Door_{k}", (ix - 0.32 + k * 0.64, iy - 0.381, 0.80), (0.60, 0.004, 1.10), (0.84, 0.88, 0.92, 1.0))
        make_box(f"Ice_Merchandiser_Handle_{k}", (ix - 0.08 + k * 0.16, iy - 0.40, 0.95), (0.03, 0.03, 0.30), COL_METAL_STEEL)
    make_box("ATM_Body", (5.66, 5.05, 0.80), (0.48, 0.60, 1.60), (0.30, 0.32, 0.36, 1.0))
    make_box("ATM_Screen", (5.418, 5.05, 1.30), (0.004, 0.34, 0.24), (0.36, 0.56, 0.78, 1.0))
    make_box("ATM_Keypad", (5.38, 5.05, 1.05), (0.08, 0.30, 0.03), (0.60, 0.60, 0.62, 1.0))
    make_box("ATM_Topper", (5.66, 5.05, 1.70), (0.48, 0.60, 0.20), COL_WALL_NEXCORP)
    make_box("Hiring_Poster", (5.895, 1.40, 1.55), (0.006, 0.46, 0.62), (0.96, 0.92, 0.36, 1.0))
    make_box("Hiring_Poster_Header", (5.891, 1.40, 1.78), (0.002, 0.40, 0.10), COL_WALL_NEXCORP)


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
    build_street_2026_10()


def build_street_2026_10():
    """What the south glass looks at (2026-10-06): the lot running out
    to Gallatin, the curb and the sidewalk, four lanes, the median with
    its palms, and across the intersection the Kwik Stop's red front —
    "Sam ... has been parked in the Kwik Stop lot for eleven minutes,
    watching the Gas & Go through her windshield"."""
    asphalt, line = (0.24, 0.24, 0.26, 1.0), (0.92, 0.90, 0.80, 1.0)
    make_box("Lot_Apron", (0.0, -10.0, -0.05), (34.0, 7.0, 0.10), asphalt)
    for k in range(6):
        make_box(f"Lot_Apron_Stripe_{k}", (-12.0 + k * 2.6, -9.0, 0.002), (0.10, 4.0, 0.004), line)
    make_box("Lot_Curb", (0.0, -13.6, 0.06), (34.0, 0.30, 0.22), (0.70, 0.70, 0.68, 1.0))
    make_box("Lot_Sidewalk", (0.0, -14.6, 0.05), (34.0, 1.8, 0.10), (0.74, 0.72, 0.68, 1.0))
    make_box("Gallatin_Road", (0.0, -22.0, -0.05), (80.0, 13.0, 0.10), asphalt)
    for k in range(10):
        make_box(f"Gallatin_Road_Dash_{k}", (-36.0 + k * 8.0, -18.8, 0.002), (3.0, 0.12, 0.004), line)
        make_box(f"Gallatin_Road_Dash_B_{k}", (-36.0 + k * 8.0, -25.2, 0.002), (3.0, 0.12, 0.004), line)
    make_box("Gallatin_Median", (0.0, -22.0, 0.10), (80.0, 2.2, 0.20), (0.40, 0.50, 0.28, 1.0))
    for k in range(6):
        px = -25.0 + k * 10.0
        make_cyl(f"Gallatin_Median_Palm_{k}_Trunk", (px, -22.0, 3.6), 0.20, 7.0, (0.52, 0.44, 0.36, 1.0), segments=8)
        for f in range(8):
            ang = f * math.pi / 4.0
            make_box(f"Gallatin_Median_Palm_{k}_Frond_{f}", (px + 0.9 * math.cos(ang), -22.0 + 0.9 * math.sin(ang), 7.2 - 0.2 * (f % 2)),
                     (1.6 if f % 2 == 0 else 0.6, 0.6 if f % 2 == 0 else 1.6, 0.05), (0.30, 0.46, 0.28, 1.0))
    make_box("Gallatin_Far_Sidewalk", (0.0, -29.6, 0.05), (80.0, 2.2, 0.10), (0.74, 0.72, 0.68, 1.0))
    # the Kwik Stop across the intersection: its lot, its red front, its canopy
    make_box("KwikStop_Lot", (6.0, -38.0, -0.05), (30.0, 14.0, 0.10), asphalt)
    make_box("KwikStop_Front_Wall", (6.0, -46.0, 2.0), (18.0, 0.4, 4.1), (0.90, 0.88, 0.84, 1.0))
    make_box("KwikStop_Front_Band", (6.0, -45.75, 3.55), (18.0, 0.1, 0.70), (0.78, 0.14, 0.12, 1.0))
    make_box("KwikStop_Front_Glass", (6.0, -45.79, 1.35), (12.0, 0.04, 1.90), (0.26, 0.32, 0.36, 1.0))
    make_box("KwikStop_Canopy_Roof", (6.0, -38.0, 4.6), (12.0, 6.0, 0.4), (0.92, 0.90, 0.86, 1.0))
    make_box("KwikStop_Canopy_Band", (6.0, -35.0, 4.4), (12.2, 0.12, 0.45), (0.78, 0.14, 0.12, 1.0))
    for sx in (1.0, 11.0):
        make_cyl(f"KwikStop_Canopy_Post_{sx:.0f}", (sx, -38.0, 2.2), 0.18, 4.4, (0.78, 0.78, 0.76, 1.0), segments=8)
    make_box("KwikStop_Sign_Pole", (-7.0, -33.0, 3.5), (0.3, 0.3, 7.0), (0.50, 0.50, 0.50, 1.0))
    make_box("KwikStop_Sign", (-7.0, -33.0, 6.6), (2.4, 0.3, 1.4), (0.78, 0.14, 0.12, 1.0))
    # Sam's Corolla in the Kwik Stop lot, nose to the street
    make_box("Corolla_Body", (-1.0, -36.0, 0.62), (1.76, 4.40, 0.70), (0.62, 0.64, 0.66, 1.0))
    make_box("Corolla_Cabin", (-1.0, -36.2, 1.20), (1.60, 2.20, 0.50), (0.24, 0.28, 0.30, 1.0))
    for k, (wx, wy) in enumerate(((-1.85, -34.6), (-0.15, -34.6), (-1.85, -37.4), (-0.15, -37.4))):
        make_cyl(f"Corolla_Wheel_{k}", (wx, wy, 0.32), 0.32, 0.22, (0.14, 0.14, 0.15, 1.0), axis='X', segments=10)
    # the houses past it, the sky line
    for k in range(5):
        make_box(f"Far_House_{k}", (-24.0 + k * 12.0, -60.0, 2.4), (9.0, 7.0, 4.8), (0.92, 0.88, 0.80, 1.0))
        make_box(f"Far_House_{k}_Roof", (-24.0 + k * 12.0, -60.0, 5.2), (9.6, 7.6, 0.8), (0.64, 0.34, 0.24, 1.0))
    for k in range(3):
        make_cyl(f"Street_Light_{k}_Pole", (-12.0 + k * 14.0, -15.2, 4.0), 0.10, 8.0, (0.50, 0.50, 0.52, 1.0), segments=6)
        make_box(f"Street_Light_{k}_Arm", (-12.0 + k * 14.0, -16.2, 7.9), (0.12, 2.0, 0.12), (0.50, 0.50, 0.52, 1.0))
        make_box(f"Street_Light_{k}_Head", (-12.0 + k * 14.0, -17.1, 7.8), (0.30, 0.60, 0.15), (0.40, 0.40, 0.42, 1.0))


# ════════════════════════════════════════════════════════════════
# EXPORT
# ════════════════════════════════════════════════════════════════
def export_glb():
    out_dir = os.path.normpath(
        os.path.join(os.path.dirname(os.path.abspath(__file__)), OUTPUT_DIR))
    os.makedirs(out_dir, exist_ok=True)
    out_path = os.path.join(out_dir, OUTPUT_NAME)
    print(f"\n[build_nexcorp_gas_go] exporting to {out_path}")
    try:    # one mesh per stocked fixture (2026-10-07, _props.geometry.join_stock)
        from _props.geometry import join_stock
        join_stock()
    except Exception as _e:
        print("[join_stock] skipped:", _e)
    bpy.ops.object.select_all(action='SELECT')
    base = {'filepath': out_path, 'export_format': 'GLB',
            'use_selection': False, 'export_apply': True,
            'export_lights': False, 'export_cameras': False}
    rna = bpy.ops.export_scene.gltf.get_rna_type()
    legacy = {}
    if 'export_colors' in rna.properties: legacy['export_colors'] = True
    # vertex colours on EVERY exporter version (2026-09-24: newer glTF
    # exporters dropped `export_colors`; their default exports colours only
    # for meshes whose material reads them, and ours have no material —
    # the 09-24 sheet rendered 30 rebuilt rooms white). Mirrors
    # _props.geometry.gltf_color_kwargs.
    try:
        if 'ACTIVE' in [e.identifier for e in rna.properties['export_vertex_color'].enum_items]:
            legacy['export_vertex_color'] = 'ACTIVE'
    except Exception:
        pass
    if 'export_active_vertex_color_when_no_material' in rna.properties:
        legacy['export_active_vertex_color_when_no_material'] = True
    if 'export_normals' in rna.properties: legacy['export_normals'] = True
    try:
        bpy.ops.export_scene.gltf(**base, **legacy)
        try:   # COLOR_0 read-back + correction (2026-09-24 · the washed-white rooms)
            import sys as _s, os as _o
            _d = _o.path.dirname(_o.path.abspath(__file__))
            for _c in (_d, _o.path.dirname(_d)):
                if _o.path.isdir(_o.path.join(_c, "_props")) and _c not in _s.path:
                    _s.path.insert(0, _c)
            from _props.glb_colorfix import postfix as _colorfix
            _colorfix(base["filepath"], bpy)
        except Exception as _e:
            print("[glb_colorfix] skipped:", _e)
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
    make_box("Pending_Folder", (4.05, 8.30, 0.766), (0.24, 0.32, 0.010), manila)   # ON the desk (2026-09-22: 0.6 m south of it)
    make_box("Pending_Folder_Tab", (3.92, 8.49, 0.7725), (0.060, 0.090, 0.003),
             (0.76, 0.64, 0.42, 1.0))


def main():
    clear_scene()
    build_shell()
    build_counter()
    build_lockers()
    build_office()
    build_floor_props()
    build_merchandise_2026_10()
    build_skips_side_2026_10()
    build_pump_canopy()
    build_hero_props_2026_09()
    export_glb()


if __name__ == "__main__":
    main()
