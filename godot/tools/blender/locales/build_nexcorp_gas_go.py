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

2026-07-02 · reference-quality dressing pass (Kwik-Stop parity).
Design thesis: the CORPORATE mirror of the family-run Kwik Stop.
Same retail vocabulary, but sterile / standardized / surveilled:
  · planogram product placement — uniform tint per shelf run and
    per cooler door (Kwik Stop cycles tints per item; we don't)
  · camera domes over every zone, incl. the breakroom
  · compliance postings, height strip, EAS pedestals, queue rail
  · NO water stains, NO crown molding, minimal scuffs — the
    clean is the brand
  · canon beats: locker #4, slushie machine w/ manila envelope
    tucked behind it, Skip's vape + under-the-till folder at
    reg. 4, single-use camera display, NexCorp Voice rack,
    GOOD NEIGHBORS GOOD GROUND poster, 8 fueling positions
    (4 dispensers), car wash tunnel in the rear + employee lot
    with the black Louisiana pickup and the white NexCorp van
Windows/doors are real OPENINGS + frames/mullions (playbook
2026-06-17: see-through glazing gets NO glass slab).

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

# Product tint cycle — matches _props/palette.py canon warm-sunset
# list (do NOT re-rainbow; franchise-wide visual cohesion).
SNACK_TINTS = [
    (0.92, 0.62, 0.28, 1.0),   # warm amber (dominant)
    (0.78, 0.42, 0.22, 1.0),   # rust orange
    (0.68, 0.32, 0.20, 1.0),   # terracotta
    (0.94, 0.82, 0.52, 1.0),   # cream wheat
    (0.86, 0.66, 0.34, 1.0),   # gold honey
    (0.52, 0.40, 0.26, 1.0),   # warm brown jerky
    (0.42, 0.52, 0.56, 1.0),   # muted teal accent
    (0.56, 0.58, 0.42, 1.0),   # sage olive accent
    (0.34, 0.42, 0.54, 1.0),   # dusty blue accent
]

# 2026-07-02 dressing-pass additions
COL_AMBER_NEX       = (0.84, 0.64, 0.28, 1.0)   # canon NexCorp accent
COL_WHITE_PANEL     = (0.96, 0.96, 0.96, 1.0)
COL_CHROME          = (0.78, 0.80, 0.82, 1.0)
COL_CONCRETE        = (0.62, 0.60, 0.56, 1.0)
COL_ASPHALT         = (0.20, 0.20, 0.22, 1.0)
COL_STRIPE_WHITE    = (0.88, 0.88, 0.86, 1.0)
COL_CAUTION_YEL     = (0.92, 0.78, 0.20, 1.0)
COL_WOOD            = (0.42, 0.30, 0.18, 1.0)
COL_MANILA          = (0.82, 0.72, 0.52, 1.0)
COL_DARK_SCREEN     = (0.10, 0.12, 0.15, 1.0)
COL_SCREEN_BLUE     = (0.42, 0.62, 0.88, 1.0)
COL_CAM_SMOKE       = (0.12, 0.12, 0.14, 1.0)
COL_PLASTIC_GREY    = (0.52, 0.53, 0.55, 1.0)
COL_RUBBER_MAT      = (0.22, 0.20, 0.20, 1.0)
COL_CORK            = (0.72, 0.58, 0.40, 1.0)
COL_SAGE            = (0.56, 0.58, 0.42, 1.0)
COL_DUSTY_BLUE      = (0.34, 0.42, 0.54, 1.0)
COL_TRUCK_BLACK     = (0.10, 0.10, 0.11, 1.0)
COL_VAN_WHITE       = (0.90, 0.90, 0.92, 1.0)
COL_WINDOW_TINT     = (0.14, 0.15, 0.17, 1.0)   # opaque auto glass
COL_RED_ACCENT      = (0.86, 0.42, 0.32, 1.0)

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
    # South wall — REAL openings for the door and the two picture
    # windows (playbook 2026-06-17: see-through glazing gets NO
    # glass slab — the pump canopy must read from inside).
    #   Door opening:   x ∈ [-1.6, +1.6], z ∈ [0, 2.4]
    #   Window openings: x ∈ [±3.1, ±5.3], z ∈ [0.95, 2.35]
    make_box("Wall_S_W", (-5.65, 0.0, CEIL_Z/2.0),
             (0.70, 0.20, CEIL_Z), COL_WALL_NEXCORP)      # west pier
    make_box("Wall_S_E", (+5.65, 0.0, CEIL_Z/2.0),
             (0.70, 0.20, CEIL_Z), COL_WALL_NEXCORP)      # east pier
    for sgn in (-1, +1):
        # Pier between window and door
        make_box(f"Wall_S_Pier_{sgn:+d}", (sgn * 2.35, 0.0, CEIL_Z/2.0),
                 (1.50, 0.20, CEIL_Z), COL_WALL_NEXCORP)
        # Sill wall below window + header above
        make_box(f"Wall_S_Sill_{sgn:+d}", (sgn * 4.20, 0.0, 0.475),
                 (2.20, 0.20, 0.95), COL_WALL_NEXCORP)
        make_box(f"Wall_S_Head_{sgn:+d}", (sgn * 4.20, 0.0, 2.675),
                 (2.20, 0.20, 0.65), COL_WALL_NEXCORP)
    make_box("Wall_S_AboveDoor", (0.0, 0.0, CEIL_Z - 0.30),
             (3.20, 0.20, 0.60), COL_WALL_NEXCORP)
    # Brand sign — NEXCORP letters on white panel, PROUD of the
    # exterior wall face (wall face is y=-0.10; the old y=-0.02
    # placement buried the sign inside the wall).
    make_box("Brand_BG", (0.0, -0.13, 2.50), (3.00, 0.05, 0.36),
             (0.96, 0.96, 0.96, 1.0))
    make_box("Brand_Letters", (0.0, -0.165, 2.50), (2.40, 0.02, 0.20),
             COL_WALL_NEXCORP)
    make_box("Brand_AccentStripe", (0.0, -0.075, 2.27),
             (3.00, 0.05, 0.05), COL_AMBER_NEX)
    # Storefront double door — aluminum frame, OPEN glazing.
    # "Door_Glass" (name kept for collider stability) is now the
    # mid-height push rail spanning the leaves.
    make_box("Door_Frame_T", (0.0, 0.0, 2.10), (3.20, 0.10, 0.08),
             COL_METAL_STEEL)
    make_box("Door_Frame_B", (0.0, 0.0, 0.06), (3.20, 0.10, 0.08),
             COL_METAL_STEEL)
    make_box("Door_Transom", (0.0, 0.0, 2.27), (3.20, 0.10, 0.26),
             COL_WALL_NEXCORP)
    for sgn in (-1, +1):
        make_box(f"Door_Jamb_{sgn:+d}", (sgn * 1.55, 0.0, 1.05),
                 (0.10, 0.10, 2.00), COL_METAL_STEEL)
        make_box(f"Door_Stile_{sgn:+d}", (sgn * 1.38, 0.0, 1.05),
                 (0.08, 0.06, 2.00), COL_METAL_STEEL)
        make_box(f"Door_Kick_{sgn:+d}", (sgn * 0.72, 0.0, 0.28),
                 (1.24, 0.05, 0.36), COL_METAL_STEEL)
        # Exterior vertical pull handles (cylinder — eye-level rule)
        make_cyl(f"Door_Pull_{sgn:+d}", (sgn * 0.28, -0.09, 1.10),
                 0.016, 0.50, COL_METAL_BLACK, segments=8, axis='Z')
    make_box("Door_Stile_Mid", (0.0, 0.0, 1.05),
             (0.16, 0.06, 2.00), COL_METAL_STEEL)
    make_box("Door_Rail_T", (0.0, 0.0, 1.98), (2.80, 0.05, 0.14),
             COL_METAL_STEEL)
    make_box("Door_Glass", (0.0, 0.0, 1.02), (2.80, 0.06, 0.16),
             COL_METAL_STEEL)
    make_box("Door_PushBar", (0.0, 0.09, 1.14), (2.60, 0.03, 0.05),
             COL_CHROME)
    make_box("Door_Closer", (0.70, 0.12, 2.02), (0.50, 0.08, 0.08),
             COL_METAL_BLACK)
    # South picture windows — frame + mullions only, NO glass.
    # "Window_S_-1"/"Window_S_+1" (names kept) are the horizontal
    # center transom bars.
    for sgn, cx in [(-1, -4.20), (+1, +4.20)]:
        make_box(f"Window_S_{sgn:+d}", (cx, 0.0, 1.65),
                 (2.24, 0.06, 0.06), COL_METAL_STEEL)
        make_box(f"Win_S{sgn:+d}_Frame_T", (cx, 0.0, 2.32),
                 (2.28, 0.08, 0.07), COL_METAL_STEEL)
        make_box(f"Win_S{sgn:+d}_SillCap", (cx, 0.0, 0.98),
                 (2.36, 0.16, 0.06), COL_METAL_STEEL)
        for side in (-1, +1):
            make_box(f"Win_S{sgn:+d}_Side_{side:+d}",
                     (cx + side * 1.12, 0.0, 1.65),
                     (0.07, 0.08, 1.44), COL_METAL_STEEL)
        for k in (-1, +1):
            make_box(f"Win_S{sgn:+d}_MullV_{k:+d}",
                     (cx + k * 0.735, 0.0, 1.65),
                     (0.05, 0.06, 1.40), COL_METAL_STEEL)
    # Ceiling
    make_box("Ceiling", (0.0, 4.5, CEIL_Z + 0.05),
             (12.4, 9.4, 0.10), COL_CEILING_TILE)
    # Fluorescent fixtures — uniform corporate grid, 3 rows
    # (Kwik Stop has warm staggered fixtures; NexCorp is regular)
    for j, ypos in enumerate([2.5, 6.0, 7.8]):
        for i in range(-1, 2):
            xp = i * 2.4
            make_box(f"Tube_{j}_{i}", (xp, ypos, CEIL_Z - 0.08),
                     (1.8, 0.40, 0.06), (0.96, 0.96, 0.92, 1.0))


# ════════════════════════════════════════════════════════════════
# SHELL POLISH — baseboards, corporate T-bar ceiling grid, entry
# mat, floor gleam. Deliberately NO water stains / almost no
# scuffs: the corporate clean is the contrast with the Kwik Stop.
# ════════════════════════════════════════════════════════════════
def build_shell_polish():
    # Grey vinyl baseboards (corporate spec, not Kwik Stop's warm
    # wood). West wall skips the restroom door (y 0.95..1.85).
    make_box("Base_W_S", (-5.87, 0.475, 0.06),
             (0.06, 0.95, 0.12), COL_PLASTIC_GREY)
    make_box("Base_W_N", (-5.87, 5.425, 0.06),
             (0.06, 7.15, 0.12), COL_PLASTIC_GREY)
    make_box("Base_E", (+5.87, 4.50, 0.06),
             (0.06, 8.80, 0.12), COL_PLASTIC_GREY)
    make_box("Base_N", (0.0, 8.87, 0.06),
             (12.20, 0.06, 0.12), COL_PLASTIC_GREY)
    for sgn in (-1, +1):
        make_box(f"Base_S_Pier_{sgn:+d}", (sgn * 2.35, 0.13, 0.06),
                 (1.50, 0.06, 0.12), COL_PLASTIC_GREY)
        make_box(f"Base_S_Sill_{sgn:+d}", (sgn * 4.20, 0.13, 0.06),
                 (2.20, 0.06, 0.12), COL_PLASTIC_GREY)
        make_box(f"Base_S_Outer_{sgn:+d}", (sgn * 5.65, 0.13, 0.06),
                 (0.70, 0.06, 0.12), COL_PLASTIC_GREY)
    # Suspended-ceiling T-bar grid — 1.2 m module, dead regular
    for i, gx in enumerate([-4.8 + k * 1.2 for k in range(9)]):
        make_box(f"CeilGridX_{i}", (gx, 4.5, CEIL_Z - 0.005),
                 (0.03, 9.4, 0.008), COL_PLASTIC_GREY)
    for j, gy in enumerate([0.6 + k * 1.2 for k in range(7)]):
        make_box(f"CeilGridY_{j}", (0.0, gy, CEIL_Z - 0.005),
                 (12.4, 0.03, 0.008), COL_PLASTIC_GREY)
    # Branded entry mat just inside the door
    make_box("Entry_Mat", (0.0, 1.0, 0.008),
             (2.20, 0.90, 0.014), COL_RUBBER_MAT)
    make_box("Entry_Mat_Logo", (0.0, 1.0, 0.017),
             (0.90, 0.30, 0.004), COL_WALL_NEXCORP)
    # Exactly two scuffs, at the door — buffed nightly, per SOP
    for i, (sx, sy) in enumerate([(-0.3, 0.6), (0.4, 1.5)]):
        make_box(f"Floor_Scuff_{i}", (sx, sy, 0.009),
                 (0.26, 0.16, 0.001), (0.46, 0.44, 0.40, 1.0))
    # Polished-floor gleam strips near the window light
    for i, (gx, gy) in enumerate([(-4.2, 1.6), (0.0, 2.2), (4.2, 1.6)]):
        make_box(f"Floor_Gleam_{i}", (gx, gy, 0.007),
                 (0.90, 0.10, 0.001), (0.92, 0.92, 0.94, 1.0))


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
    # Stool
    make_cyl("Stool_Seat", (cx, cy + 0.32, 0.66),
             0.16, 0.04, COL_LOCKER_GREY, segments=10)
    make_cyl("Stool_Post", (cx, cy + 0.32, 0.36),
             0.030, 0.56, COL_METAL_BLACK)
    make_cyl("Stool_Base", (cx, cy + 0.32, 0.05),
             0.20, 0.04, COL_METAL_BLACK, segments=8)
    # Backbar island BEHIND the clerk (clerk aisle is y 1.75-2.6;
    # the old cig_y=8.85 placement marooned the shelves inside the
    # manager's office at the north wall — register rule says the
    # cigarette backboard sits within the clerk's reach).
    make_box("Backbar_Base", (4.0, 3.0, 0.50),
             (3.20, 0.50, 1.00), COL_COUNTER_LAMINATE)
    make_box("Backbar_Top", (4.0, 3.0, 1.02),
             (3.30, 0.56, 0.04), COL_METAL_BLACK)
    make_box("Backbar_Panel", (4.0, 3.22, 1.90),
             (3.20, 0.06, 1.76), COL_WALL_NEXCORP)
    # Cigarette shelves — corporate planogram: brand blocks of
    # three, not the Kwik Stop per-item shuffle
    cig_y = 3.10
    for sh in range(3):
        shz = 1.55 + sh * 0.42
        make_box(f"CigShelf_{sh}", (cx + 0.5, cig_y, shz),
                 (3.20, 0.22, 0.02), COL_METAL_STEEL)
        for ci in range(12):
            box_x = cx + 0.5 - 1.45 + ci * 0.26
            make_box(f"CigBox_{sh}_{ci}",
                     (box_x, cig_y - 0.04, shz + 0.13),
                     (0.20, 0.12, 0.22),
                     SNACK_TINTS[(ci // 3 + sh) % len(SNACK_TINTS)])


# ════════════════════════════════════════════════════════════════
# COUNTER ZONE DRESSING — queue rail, terminals, Skip's things.
# Clerk stands NORTH of the counter facing SOUTH (sight of the
# door AND the pumps through the window — forecourt watch).
# ════════════════════════════════════════════════════════════════
def build_counter_zone():
    cx, cy = 3.5, 1.4
    # Bullnose edge strip on the customer (south) face
    make_box("Counter_Bullnose", (cx, cy - 0.36, 1.04),
             (4.10, 0.04, 0.08), COL_METAL_STEEL)
    # Anti-fatigue mat in the clerk aisle
    make_box("Clerk_Mat", (cx, 2.15, 0.006),
             (3.40, 0.60, 0.012), COL_RUBBER_MAT)
    # Queue rail — two stanchions + belt (pure corporate; the
    # Kwik Stop would never)
    for i, px in enumerate([1.9, 3.1]):
        make_cyl(f"Stanchion_Base_{i}", (px, 0.55, 0.02),
                 0.16, 0.04, COL_METAL_BLACK, segments=10)
        make_cyl(f"Stanchion_Post_{i}", (px, 0.55, 0.50),
                 0.024, 0.92, COL_CHROME, segments=8)
        make_cyl(f"Stanchion_Cap_{i}", (px, 0.55, 0.98),
                 0.035, 0.04, COL_WALL_NEXCORP, segments=8)
    make_box("Stanchion_Belt", (2.5, 0.55, 0.88),
             (1.20, 0.04, 0.07), COL_WALL_NEXCORP)
    # WAIT HERE floor decal at the head of the queue
    make_box("Queue_Decal_Bar", (1.5, 0.80, 0.009),
             (0.50, 0.06, 0.001), COL_STRIPE_WHITE)
    make_box("Queue_Decal_Foot", (1.5, 0.62, 0.009),
             (0.06, 0.30, 0.001), COL_STRIPE_WHITE)
    # "REG 4" plate on the counter's customer face — canon: Skip
    # signs his envelope "S.D., reg. 4"
    make_box("Reg4_Plate", (2.5, cy - 0.305, 0.95),
             (0.22, 0.012, 0.07), COL_WHITE_PANEL)
    # Skip's vape lying by the register (eye-level → cylinder)
    make_cyl("Skip_Vape", (2.9, 1.55, 1.085),
             0.012, 0.11, COL_METAL_BLACK, segments=8, axis='X')
    make_box("Skip_VapePodBox", (2.95, 1.42, 1.09),
             (0.06, 0.04, 0.03), COL_DUSTY_BLUE)
    # Skip's phone, face-up (he is reading it, canonically)
    make_box("Skip_Phone", (3.25, 1.45, 1.085),
             (0.075, 0.155, 0.012), COL_METAL_BLACK)
    make_box("Skip_Phone_Screen", (3.25, 1.45, 1.093),
             (0.065, 0.140, 0.002), COL_DARK_SCREEN)
    # The under-the-till manila folder (canon — the documents Skip
    # has chosen not to throw away), poking out under the top
    make_box("Till_Folder", (2.5, 1.70, 0.975),
             (0.30, 0.22, 0.015), COL_MANILA)
    # Credit-card terminal on the customer edge + cord
    make_box("CC_Terminal_Base", (4.6, 1.20, 1.10),
             (0.16, 0.14, 0.05), COL_METAL_BLACK)
    make_box("CC_Terminal_Screen", (4.6, 1.17, 1.16),
             (0.13, 0.02, 0.09), COL_SCREEN_BLUE)
    make_cyl("CC_Terminal_Cord", (4.6, 1.32, 1.06),
             0.008, 0.18, COL_METAL_BLACK, segments=6, axis='Y')
    # Receipt printer + paper curl
    make_box("Receipt_Printer", (2.0, 1.55, 1.12),
             (0.26, 0.22, 0.12), COL_PLASTIC_GREY)
    make_cyl("Receipt_Curl", (2.0, 1.44, 1.20),
             0.025, 0.14, COL_PAPER, segments=8, axis='X')
    # Lottery scratch-ticket case — uniform acrylic steps
    make_box("Scratch_Case_Base", (5.1, 1.40, 1.10),
             (0.44, 0.34, 0.06), COL_METAL_BLACK)
    for step in range(2):
        make_box(f"Scratch_Step_{step}",
                 (5.1, 1.46 - step * 0.14, 1.16 + step * 0.09),
                 (0.40, 0.10, 0.10),
                 (0.98, 0.84, 0.32, 1.0))
        make_box(f"Scratch_Step_Header_{step}",
                 (5.1, 1.46 - step * 0.14, 1.235 + step * 0.09),
                 (0.40, 0.10, 0.03), COL_WALL_NEXCORP)
    # LOTTO cube hanging above the case
    make_cyl("Lotto_Cube_Rod", (5.1, 1.4, 2.74),
             0.008, 0.52, COL_METAL_STEEL, segments=6)
    make_box("Lotto_Cube", (5.1, 1.4, 2.36),
             (0.24, 0.24, 0.24), COL_WALL_NEXCORP)
    make_box("Lotto_Cube_Band", (5.1, 1.4, 2.36),
             (0.25, 0.25, 0.08), (0.98, 0.84, 0.32, 1.0))
    # Impulse rack on the customer face — planogram: one tint per
    # row (the Kwik Stop's is a candy jumble)
    make_box("Impulse_Rack_Back", (3.9, 1.08, 0.62),
             (1.40, 0.04, 0.80), COL_METAL_STEEL)
    for row in range(3):
        rz = 0.34 + row * 0.26
        make_box(f"Impulse_Shelf_{row}", (3.9, 1.00, rz),
                 (1.40, 0.12, 0.02), COL_METAL_STEEL)
        row_tint = SNACK_TINTS[row % len(SNACK_TINTS)]
        for c in range(6):
            make_box(f"Impulse_Item_{row}_{c}",
                     (3.9 - 0.575 + c * 0.23, 1.00, rz + 0.06),
                     (0.18, 0.09, 0.09), row_tint)
    # Air-freshener clip strip — three IDENTICAL navy trees
    make_box("AirTree_Strip", (2.2, 1.09, 0.85),
             (0.04, 0.015, 0.55), COL_METAL_STEEL)
    for i in range(3):
        make_box(f"AirTree_{i}", (2.2, 1.075, 0.95 - i * 0.20),
                 (0.10, 0.008, 0.14), COL_WALL_NEXCORP)


# ════════════════════════════════════════════════════════════════
# BACKBAR EQUIPMENT — CCTV quad monitor, locked vape case, the
# single-use camera display (canon: Skip's Polaroid came from
# here), hanging CAR WASH menu.
# ════════════════════════════════════════════════════════════════
def build_backbar_dressing():
    # CCTV quad monitor angled at the clerk — the store watches
    # itself and makes sure Skip knows it
    make_box("CCTV_Monitor_Body", (5.3, 3.0, 1.25),
             (0.40, 0.14, 0.34), COL_METAL_BLACK)
    for qi in range(2):
        for qj in range(2):
            make_box(f"CCTV_Quad_{qi}_{qj}",
                     (5.3 - 0.085 + qi * 0.17, 2.925,
                      1.175 + qj * 0.15),
                     (0.15, 0.01, 0.13), COL_DARK_SCREEN)
    # Locked vape display case (corporate retail: everything
    # desirable is behind acrylic)
    # (open-front carcass so the stock reads through the pane)
    make_box("Vape_Case_Frame", (2.75, 3.12, 1.26),
             (0.52, 0.08, 0.44), COL_WALL_NEXCORP)
    for tag, vx in [("W", 2.51), ("E", 2.99)]:
        make_box(f"Vape_Case_Cheek_{tag}", (vx, 2.97, 1.26),
                 (0.04, 0.30, 0.44), COL_WALL_NEXCORP)
    make_box("Vape_Case_Top", (2.75, 2.97, 1.46),
             (0.52, 0.30, 0.04), COL_WALL_NEXCORP)
    make_box("Vape_Case_Base", (2.75, 2.97, 1.06),
             (0.52, 0.30, 0.04), COL_WALL_NEXCORP)
    make_box("Vape_Case_Glass", (2.75, 2.83, 1.26),
             (0.44, 0.02, 0.36), (0.46, 0.78, 0.92, 0.55))
    for sh in range(2):
        for c in range(4):
            make_box(f"Vape_Item_{sh}_{c}",
                     (2.75 - 0.15 + c * 0.10, 2.92, 1.14 + sh * 0.17),
                     (0.06, 0.05, 0.11),
                     SNACK_TINTS[(6 + sh) % len(SNACK_TINTS)])
    make_box("Vape_Case_Lock", (2.75, 2.815, 1.09),
             (0.05, 0.02, 0.05), COL_CHROME)
    # Single-use camera display — three identical yellow boxes.
    # Canon: Skip bought one "three years ago for this exact
    # purpose" and developed exactly one exposure.
    make_box("FunShot_Tray", (3.6, 3.0, 1.06),
             (0.40, 0.26, 0.04), COL_WALL_NEXCORP)
    for i in range(3):
        make_box(f"FunShot_Camera_{i}",
                 (3.6 - 0.12 + i * 0.12, 3.0, 1.14),
                 (0.09, 0.14, 0.12), (0.94, 0.82, 0.52, 1.0))
    # CAR WASH menu — three service tiers hung from the ceiling
    # over the backbar (name panels are Label3D anchors)
    for i, rx in enumerate([2.45, 3.25]):
        make_cyl(f"Carwash_Menu_Rod_{i}", (rx, 2.75, 2.79),
                 0.008, 0.42, COL_METAL_STEEL, segments=6)
    make_box("Carwash_Menu_Header", (2.85, 2.75, 2.50),
             (0.96, 0.03, 0.16), COL_WALL_NEXCORP)
    tier_cols = [COL_PLASTIC_GREY, COL_CHROME, COL_AMBER_NEX]
    for i in range(3):
        make_box(f"Carwash_Menu_Tier_{i}",
                 (2.85, 2.75, 2.36 - i * 0.13),
                 (0.96, 0.02, 0.11), COL_WHITE_PANEL)
        make_box(f"Carwash_Menu_Chip_{i}",
                 (2.46, 2.745, 2.36 - i * 0.13),
                 (0.10, 0.025, 0.09), tier_cols[i])
    # WE CARD UNDER 40 compliance panel, high on the backbar panel
    make_box("WeCard_Panel", (4.9, 3.185, 2.52),
             (0.42, 0.012, 0.30), COL_WHITE_PANEL)
    make_box("WeCard_Band", (4.9, 3.175, 2.62),
             (0.42, 0.012, 0.08), COL_RED_ACCENT)


# ════════════════════════════════════════════════════════════════
# ENTRY ZONE — EAS pedestals, ATM, height strip, corporate
# postings. The door checks you in and out; the Kwik Stop's door
# just has a bell.
# ════════════════════════════════════════════════════════════════
def build_entry_zone():
    # EAS anti-theft pedestals flanking the door
    for sgn in (-1, +1):
        make_box(f"EAS_Base_{sgn:+d}", (sgn * 0.95, 0.42, 0.025),
                 (0.22, 0.50, 0.05), COL_METAL_BLACK)
        make_box(f"EAS_Panel_{sgn:+d}", (sgn * 0.95, 0.42, 0.78),
                 (0.05, 0.44, 1.46), COL_PLASTIC_GREY)
        make_box(f"EAS_Cap_{sgn:+d}", (sgn * 0.95, 0.42, 1.54),
                 (0.06, 0.46, 0.06), COL_WALL_NEXCORP)
    # Electronic door chime + status LED above the east jamb
    make_box("Door_Chime", (1.45, 0.13, 2.20),
             (0.14, 0.06, 0.08), COL_WHITE_PANEL)
    make_box("Door_Chime_LED", (1.40, 0.17, 2.20),
             (0.02, 0.02, 0.02), (0.32, 0.86, 0.42, 1.0))
    # Interior illuminated EXIT sign on the transom
    make_box("Exit_Sign_Box", (0.0, 0.095, 2.27),
             (0.46, 0.07, 0.20), COL_METAL_BLACK)
    make_box("Exit_Sign_Face", (0.0, 0.135, 2.27),
             (0.38, 0.01, 0.14), COL_RED_ACCENT)
    # Height strip on the east pier — the door photographs you
    # leaving; ticks every 30 cm
    make_box("Height_Strip", (1.72, 0.115, 1.50),
             (0.12, 0.012, 1.90), COL_WHITE_PANEL)
    for i in range(5):
        make_box(f"Height_Tick_{i}", (1.70, 0.125, 0.90 + i * 0.30),
                 (0.08, 0.012, 0.02), COL_WALL_NEXCORP)
    # CAMERAS IN OPERATION panel over the west window
    make_box("CamNotice_Panel", (-4.2, 0.115, 2.60),
             (0.52, 0.012, 0.26), COL_WHITE_PANEL)
    make_box("CamNotice_Dot", (-4.40, 0.125, 2.60),
             (0.06, 0.012, 0.06), COL_RED_ACCENT)
    # ATM against the south wall, west of the door
    make_box("ATM_Body", (-2.35, 0.42, 0.80),
             (0.60, 0.52, 1.60), (0.24, 0.28, 0.36, 1.0))
    make_box("ATM_Screen", (-2.35, 0.70, 1.18),
             (0.34, 0.02, 0.24), COL_SCREEN_BLUE)
    make_box("ATM_Keypad", (-2.35, 0.70, 0.94),
             (0.28, 0.02, 0.12), COL_PLASTIC_GREY)
    make_box("ATM_CardSlot", (-2.16, 0.70, 1.02),
             (0.10, 0.02, 0.02), COL_AMBER_NEX)
    make_box("ATM_Topper", (-2.35, 0.42, 1.72),
             (0.56, 0.44, 0.22), COL_WALL_NEXCORP)
    make_box("ATM_Topper_Text", (-2.35, 0.655, 1.72),
             (0.40, 0.012, 0.14), COL_WHITE_PANEL)
    # NexCorp Voice newsletter rack (canon: the quarterly internal
    # newsletter — glossy, professionally produced, unread)
    make_box("Voice_Rack_Back", (2.35, 0.13, 1.35),
             (0.50, 0.02, 0.70), COL_WALL_NEXCORP)
    for p in range(3):
        make_box(f"Voice_Rack_Bar_{p}", (2.35, 0.19, 1.10 + p * 0.24),
                 (0.48, 0.04, 0.03), COL_METAL_STEEL)
        make_box(f"Voice_Issue_{p}", (2.35, 0.165, 1.19 + p * 0.24),
                 (0.40, 0.015, 0.16), COL_WHITE_PANEL)
        make_box(f"Voice_Issue_Band_{p}", (2.35, 0.155, 1.25 + p * 0.24),
                 (0.40, 0.012, 0.04), COL_WALL_NEXCORP)
    # GOOD NEIGHBORS GOOD GROUND poster (canon: the community-
    # engagement initiative from the NexCorp Voice spring issue)
    make_box("GoodGround_Poster", (2.35, 0.115, 2.35),
             (0.60, 0.012, 0.66), COL_WALL_NEXCORP)
    make_box("GoodGround_TextBar_0", (2.35, 0.127, 2.52),
             (0.48, 0.012, 0.08), (0.86, 0.84, 0.74, 1.0))
    make_box("GoodGround_TextBar_1", (2.35, 0.127, 2.40),
             (0.48, 0.012, 0.08), (0.86, 0.84, 0.74, 1.0))
    make_box("GoodGround_GroundBar", (2.35, 0.127, 2.14),
             (0.48, 0.012, 0.14), COL_SAGE)
    # Nested hand-basket stack by the west window
    make_box("Basket_Stack_Base", (-3.4, 0.50, 0.10),
             (0.44, 0.30, 0.20), COL_METAL_STEEL)
    for i in range(4):
        make_box(f"Basket_{i}", (-3.4, 0.50, 0.24 + i * 0.09),
                 (0.46, 0.32, 0.07), COL_WALL_NEXCORP)


# ════════════════════════════════════════════════════════════════
# LOCKER ROOM (back-NW · Locker #4 is Skip's, canonical)
# ════════════════════════════════════════════════════════════════
def build_lockers():
    # Lockers along the west wall, back half, Y ∈ [5.5, 8.5]
    lx = -5.70
    for i in range(6):
        ly = 5.7 + i * 0.55
        # Body
        make_box(f"Locker_{i+1}_Body", (lx, ly, 1.00),
                 (0.50, 0.50, 1.80), COL_LOCKER_GREY)
        # Door seam
        make_box(f"Locker_{i+1}_Door", (lx - 0.21, ly, 1.00),
                 (0.02, 0.48, 1.74), COL_LOCKER_DOORSEAM)
        # Handle
        make_box(f"Locker_{i+1}_Handle", (lx - 0.23, ly + 0.16, 1.00),
                 (0.02, 0.06, 0.06), COL_METAL_BLACK)
        # Vent grille
        for j in range(3):
            make_box(f"Locker_{i+1}_Vent_{j}",
                     (lx - 0.22, ly, 1.70 + j * 0.08),
                     (0.005, 0.30, 0.02), COL_METAL_BLACK)
        # Number plate — #4 is Skip's, paint it brass instead of paper
        plate_col = (0.78, 0.62, 0.30, 1.0) if (i + 1) == 4 else COL_PAPER
        make_box(f"Locker_{i+1}_Plate", (lx - 0.22, ly, 1.85),
                 (0.005, 0.18, 0.06), plate_col)
        # The combination lock on #4 (Skip's: ex-wife's birthday backward)
        if (i + 1) == 4:
            make_cyl(f"Locker_{i+1}_Lock", (lx - 0.24, ly - 0.04, 1.30),
                     0.04, 0.04, COL_METAL_BLACK, segments=10, axis='X')

    # Bench in front of lockers
    make_box("Locker_Bench_Seat", (lx + 0.6, 6.8, 0.40),
             (0.32, 2.50, 0.06), (0.42, 0.30, 0.18, 1.0))
    for sy in (-1, +1):
        make_box(f"Locker_Bench_Leg_{sy}",
                 (lx + 0.6, 6.8 + sy * 1.10, 0.20),
                 (0.32, 0.06, 0.40), (0.42, 0.30, 0.18, 1.0))
    # A spare uniform jacket hanging off the bench (NexCorp blue)
    make_box("Spare_Jacket", (lx + 0.42, 5.9, 0.65),
             (0.04, 0.30, 0.50), COL_WALL_NEXCORP)


# ════════════════════════════════════════════════════════════════
# BACK-OF-HOUSE — partition around the locker/break room with an
# OPEN doorway (the locker room stays visible per the design
# note), time clock, compliance postings, vending, breakroom
# table (canon: where the tarot printout was found), rear exit.
# ════════════════════════════════════════════════════════════════
def build_backroom():
    # Partition: wall at y=5.2 from the west wall to x=-3, then a
    # return wall at x=-3 up to the north wall. Doorway opening
    # x ∈ [-4.6, -3.5] — no door panel; corporate keeps the
    # sightline (and the cameras) on the breakroom.
    make_box("BOH_Wall_S_W", (-5.30, 5.2, CEIL_Z/2.0),
             (1.40, 0.12, CEIL_Z), COL_WALL_WHITE)
    make_box("BOH_Wall_S_E", (-3.25, 5.2, CEIL_Z/2.0),
             (0.50, 0.12, CEIL_Z), COL_WALL_WHITE)
    make_box("BOH_Wall_S_Header", (-4.05, 5.2, 2.55),
             (1.10, 0.12, 0.90), COL_WALL_WHITE)
    make_box("BOH_Wall_E", (-3.0, 7.1, CEIL_Z/2.0),
             (0.12, 3.80, CEIL_Z), COL_WALL_WHITE)
    # EMPLOYEES ONLY plaque over the doorway (retail side) +
    # keypad on the jamb — badge-in culture
    make_box("BOH_Plaque", (-4.05, 5.13, 2.25),
             (0.70, 0.012, 0.18), COL_WHITE_PANEL)
    make_box("BOH_Keypad", (-3.42, 5.12, 1.25),
             (0.10, 0.03, 0.16), COL_PLASTIC_GREY)
    for r in range(3):
        for c in range(2):
            make_box(f"BOH_Key_{r}_{c}",
                     (-3.44 + c * 0.045, 5.095, 1.30 - r * 0.045),
                     (0.028, 0.01, 0.028), COL_WHITE_PANEL)
    # Time clock on the partition, BOH side, beside the doorway
    make_box("TimeClock_Body", (-3.25, 5.32, 1.50),
             (0.26, 0.12, 0.32), COL_PLASTIC_GREY)
    make_cyl("TimeClock_Face", (-3.25, 5.395, 1.56),
             0.075, 0.02, COL_WHITE_PANEL, segments=12, axis='Y')
    make_box("TimeClock_Slot", (-3.25, 5.39, 1.38),
             (0.16, 0.02, 0.015), COL_METAL_BLACK)
    # Punch-card rack on the BOH return wall — 8 uniform slots
    make_box("TimeCard_Rack", (-3.08, 5.75, 1.50),
             (0.02, 0.50, 0.42), COL_METAL_STEEL)
    for r in range(2):
        for c in range(4):
            make_box(f"TimeCard_{r}_{c}",
                     (-3.10, 5.56 + c * 0.125, 1.60 - r * 0.20),
                     (0.012, 0.09, 0.14), (0.86, 0.84, 0.74, 1.0))
    # Labor-law / compliance posting board (BOH side of partition)
    # — a dead-regular 2x3 grid, header in brand navy
    make_box("Compliance_Board", (-5.30, 5.275, 1.70),
             (1.20, 0.012, 0.90), COL_WHITE_PANEL)
    make_box("Compliance_Header", (-5.30, 5.285, 2.08),
             (1.20, 0.012, 0.14), COL_WALL_NEXCORP)
    for r in range(2):
        for c in range(3):
            make_box(f"Compliance_Post_{r}_{c}",
                     (-5.64 + c * 0.34, 5.285, 1.82 - r * 0.36),
                     (0.28, 0.012, 0.30),
                     COL_PAPER if (r + c) % 2 == 0 else COL_WHITE_PANEL)
    # Breakroom table (cylinder — eye-level rule) + two chairs
    make_cyl("Break_Table_Top", (-4.15, 6.5, 0.74),
             0.40, 0.04, COL_COUNTER_LAMINATE, segments=12)
    make_cyl("Break_Table_Post", (-4.15, 6.5, 0.38),
             0.035, 0.68, COL_METAL_BLACK, segments=8)
    make_cyl("Break_Table_Foot", (-4.15, 6.5, 0.03),
             0.24, 0.05, COL_METAL_BLACK, segments=10)
    for i, (chx, chy, back_dx, back_dy) in enumerate([
            (-4.15, 5.90, 0.0, -0.21), (-3.50, 6.50, 0.21, 0.0)]):
        make_box(f"Break_Chair_Seat_{i}", (chx, chy, 0.45),
                 (0.42, 0.42, 0.05), COL_PLASTIC_GREY)
        make_box(f"Break_Chair_Back_{i}",
                 (chx + back_dx, chy + back_dy, 0.78),
                 (0.42 if back_dx == 0 else 0.05,
                  0.42 if back_dy == 0 else 0.05, 0.60),
                 COL_PLASTIC_GREY)
        make_cyl(f"Break_Chair_Post_{i}", (chx, chy, 0.22),
                 0.025, 0.42, COL_METAL_BLACK, segments=8)
    # NexCorp Voice spring issue on the table (canon) + a mug
    make_box("Break_Voice_Issue", (-4.25, 6.42, 0.765),
             (0.20, 0.28, 0.01), COL_WHITE_PANEL)
    make_box("Break_Voice_Band", (-4.25, 6.42, 0.772),
             (0.20, 0.08, 0.008), COL_WALL_NEXCORP)
    make_cyl("Break_Mug", (-3.95, 6.68, 0.81),
             0.04, 0.09, COL_WALL_NEXCORP, segments=10)
    # Snack vending machine — the company sells its employees the
    # same planogram it sells the town
    # Open-front carcass: back slab, west cheek, east selection
    # column, fascia + plinth — the product coils must read
    # through the window, not sit inside a solid box
    make_box("Vending_Body", (-3.65, 8.62, 0.915),
             (0.90, 0.45, 1.83), (0.22, 0.30, 0.44, 1.0))
    make_box("Vending_Cheek_W", (-4.07, 8.30, 0.915),
             (0.06, 0.42, 1.83), (0.22, 0.30, 0.44, 1.0))
    make_box("Vending_Column_E", (-3.32, 8.30, 0.915),
             (0.24, 0.42, 1.83), (0.22, 0.30, 0.44, 1.0))
    make_box("Vending_Fascia", (-3.74, 8.30, 1.755),
             (0.60, 0.42, 0.15), (0.22, 0.30, 0.44, 1.0))
    make_box("Vending_Plinth", (-3.74, 8.30, 0.26),
             (0.60, 0.42, 0.52), (0.16, 0.22, 0.34, 1.0))
    make_box("Vending_Window", (-3.74, 8.14, 1.11),
             (0.60, 0.02, 1.16), (0.46, 0.78, 0.92, 0.55))
    for r in range(4):
        make_box(f"Vending_Coil_{r}", (-3.74, 8.28, 0.70 + r * 0.26),
                 (0.52, 0.04, 0.02), COL_METAL_STEEL)
        for c in range(3):
            make_box(f"Vending_Item_{r}_{c}",
                     (-3.94 + c * 0.16, 8.30, 0.78 + r * 0.26),
                     (0.12, 0.08, 0.14),
                     SNACK_TINTS[(r * 3 + c) % len(SNACK_TINTS)])
    make_box("Vending_Keypad", (-3.32, 8.085, 1.30),
             (0.12, 0.02, 0.30), COL_PLASTIC_GREY)
    make_box("Vending_Flap", (-3.74, 8.085, 0.32),
             (0.44, 0.02, 0.18), COL_METAL_BLACK)
    # Mini fridge + microwave stack
    make_box("Break_Fridge", (-3.35, 7.55, 0.43),
             (0.54, 0.54, 0.85), COL_WHITE_PANEL)
    make_box("Break_Fridge_Handle", (-3.35, 7.26, 0.60),
             (0.20, 0.02, 0.03), COL_METAL_STEEL)
    make_box("Break_Microwave", (-3.35, 7.55, 1.02),
             (0.50, 0.38, 0.28), COL_METAL_BLACK)
    make_box("Break_Microwave_Door", (-3.35, 7.35, 1.02),
             (0.36, 0.02, 0.20), COL_DARK_SCREEN)
    # Rear fire exit — steel door + panic bar + EXIT box
    make_box("Back_Door", (-4.90, 8.86, 1.05),
             (0.90, 0.06, 2.10), COL_PLASTIC_GREY)
    make_box("Back_Door_PanicBar", (-4.90, 8.80, 1.05),
             (0.70, 0.05, 0.06), COL_CHROME)
    make_box("Back_Exit_Box", (-4.90, 8.82, 2.30),
             (0.40, 0.06, 0.18), COL_METAL_BLACK)
    make_box("Back_Exit_Face", (-4.90, 8.78, 2.30),
             (0.32, 0.01, 0.12), COL_RED_ACCENT)
    # Janitor corner — mop bucket + standing mop + broom
    make_cyl("Mop_Bucket", (-3.35, 5.75, 0.24),
             0.16, 0.44, COL_CAUTION_YEL, segments=10)
    make_cyl("Mop_Handle", (-3.38, 5.75, 0.95),
             0.014, 1.30, COL_WOOD, segments=6)
    make_cyl("Broom_Handle", (-3.12, 6.15, 0.75),
             0.012, 1.40, COL_WOOD, segments=6)
    make_box("Broom_Head", (-3.12, 6.15, 0.08),
             (0.06, 0.30, 0.14), (0.86, 0.66, 0.34, 1.0))
    # Safety station on the BOH return wall — extinguisher +
    # first-aid box (corporate compliance, mounted level)
    make_box("Extinguisher_Bracket", (-3.08, 6.90, 1.05),
             (0.02, 0.10, 0.16), COL_METAL_BLACK)
    make_cyl("Extinguisher_Tank", (-3.16, 6.90, 1.02),
             0.07, 0.44, COL_RED_ACCENT, segments=10)
    make_cyl("Extinguisher_Neck", (-3.16, 6.90, 1.28),
             0.025, 0.10, COL_METAL_BLACK, segments=8)
    make_box("FirstAid_Box", (-3.08, 7.50, 1.60),
             (0.05, 0.34, 0.28), COL_WHITE_PANEL)
    make_box("FirstAid_Cross_V", (-3.10, 7.50, 1.60),
             (0.012, 0.06, 0.18), COL_RED_ACCENT)
    make_box("FirstAid_Cross_H", (-3.10, 7.50, 1.60),
             (0.012, 0.18, 0.06), COL_RED_ACCENT)
    # BOH gets its own fluorescent + frame
    make_box("Tube_BOH", (-4.5, 7.0, CEIL_Z - 0.08),
             (1.6, 0.40, 0.06), (0.96, 0.96, 0.92, 1.0))
    make_box("Troffer_BOH", (-4.5, 7.0, CEIL_Z - 0.11),
             (1.72, 0.48, 0.02), COL_METAL_STEEL)


# ════════════════════════════════════════════════════════════════
# MANAGER'S OFFICE (Skip's, back-east corner · glass partition)
# ════════════════════════════════════════════════════════════════
def build_office():
    # Glazed partition — stub walls + OPEN glazing frames (no
    # glass slabs; vertex-color "glass" renders opaque). Names
    # Office_PartW/PartN kept: they are now the knee-walls.
    make_box("Office_PartW", (+3.0, 7.975, 0.55),
             (0.10, 2.05, 1.10), COL_WALL_WHITE)
    make_box("Office_PartN", (+4.5, 6.0, 0.55),
             (3.00, 0.10, 1.10), COL_WALL_WHITE)
    # Glazing frame, west run (x=3.0, y 6.95..9.0)
    make_box("Office_Glz_W_Cap", (3.0, 7.975, 1.13),
             (0.08, 2.05, 0.06), COL_METAL_STEEL)
    make_box("Office_Glz_W_Post", (3.0, 8.0, 2.05),
             (0.06, 0.06, 1.90), COL_METAL_STEEL)
    for k, gz in enumerate([2.0, 2.94]):
        make_box(f"Office_Glz_W_Rail_{k}", (3.0, 7.975, gz),
                 (0.06, 2.05, 0.06), COL_METAL_STEEL)
    # Glazing frame, north run (y=6.0, x 3..6)
    make_box("Office_Glz_N_Cap", (4.5, 6.0, 1.13),
             (3.00, 0.08, 0.06), COL_METAL_STEEL)
    make_box("Office_Glz_N_Post", (4.5, 6.0, 2.05),
             (0.06, 0.06, 1.90), COL_METAL_STEEL)
    for k, gz in enumerate([2.0, 2.94]):
        make_box(f"Office_Glz_N_Rail_{k}", (4.5, 6.0, gz),
                 (3.00, 0.06, 0.06), COL_METAL_STEEL)
    make_box("Office_Glz_Corner", (3.0, 6.0, CEIL_Z/2.0),
             (0.10, 0.10, CEIL_Z), COL_METAL_STEEL)
    # Office door in the y 6.0..6.95 opening + header above
    make_box("Office_Door", (+3.04, 6.5, 1.05),
             (0.04, 0.90, 2.10), COL_WOOD)
    make_box("Office_Door_Header", (3.0, 6.475, 2.55),
             (0.10, 0.95, 0.90), COL_WALL_WHITE)
    make_cyl("Office_Door_Knob", (3.08, 6.82, 1.00),
             0.03, 0.05, COL_CHROME, segments=8, axis='X')
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
    make_box("Office_Phone", (dx + 0.50, dy, 0.78),
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
# OFFICE DETAIL — the room where NexCorp lives: time-delay safe,
# uniform binder row, CCTV feed, corkboard of memos.
# ════════════════════════════════════════════════════════════════
def build_office_detail():
    dx, dy = 4.5, 7.5
    # Desk clutter — keyboard, two paper stacks, mug, in/out tray
    make_box("Desk_Keyboard", (dx - 0.15, dy - 0.12, 0.775),
             (0.40, 0.15, 0.02), COL_PLASTIC_GREY)
    make_box("Desk_Papers_0", (dx - 0.52, dy - 0.08, 0.775),
             (0.22, 0.30, 0.02), COL_PAPER)
    make_box("Desk_Papers_1", (dx - 0.54, dy - 0.11, 0.79),
             (0.20, 0.28, 0.008), COL_WHITE_PANEL)
    make_cyl("Desk_Mug", (dx + 0.28, dy - 0.18, 0.81),
             0.04, 0.10, COL_WALL_NEXCORP, segments=10)
    for t in range(2):
        make_box(f"Desk_Tray_{t}", (dx - 0.60, dy + 0.26, 0.79 + t * 0.09),
                 (0.28, 0.36, 0.02), COL_METAL_BLACK)
        make_box(f"Desk_Tray_Paper_{t}",
                 (dx - 0.60, dy + 0.26, 0.805 + t * 0.09),
                 (0.24, 0.32, 0.008), COL_PAPER)
    # Time-delay drop safe under the desk (cash control: the
    # corporate answer to the Kwik Stop's cigar box)
    make_box("Drop_Safe", (4.85, 7.55, 0.24),
             (0.42, 0.42, 0.44), (0.16, 0.18, 0.22, 1.0))
    make_box("Drop_Safe_Keypad", (4.85, 7.32, 0.30),
             (0.10, 0.02, 0.10), COL_PLASTIC_GREY)
    make_box("Drop_Safe_Slot", (4.85, 7.32, 0.42),
             (0.20, 0.02, 0.02), COL_METAL_BLACK)
    # Wall shelf of IDENTICAL navy binders (planogram even here)
    make_box("Binder_Shelf", (4.4, 8.80, 2.02),
             (1.60, 0.26, 0.03), COL_METAL_STEEL)
    for b in range(8):
        make_box(f"Binder_{b}", (3.75 + b * 0.17, 8.82, 2.19),
                 (0.06, 0.22, 0.30),
                 COL_WALL_NEXCORP if b < 6 else COL_WHITE_PANEL)
    # CCTV monitor on the file cabinet — same four quads Skip
    # doesn't look at
    make_box("Office_CCTV_Body", (5.30, 8.40, 1.76),
             (0.38, 0.16, 0.30), COL_METAL_BLACK)
    for qi in range(2):
        for qj in range(2):
            make_box(f"Office_CCTV_Quad_{qi}_{qj}",
                     (5.30 - 0.08 + qi * 0.16, 8.31,
                      1.695 + qj * 0.13),
                     (0.14, 0.01, 0.11), COL_DARK_SCREEN)
    # Corkboard with pinned memos
    make_box("Office_Corkboard", (3.55, 8.895, 1.62),
             (0.80, 0.02, 0.60), COL_CORK)
    for i, (mx, mz) in enumerate([(3.32, 1.72), (3.56, 1.50),
                                  (3.78, 1.75), (3.48, 1.80)]):
        make_box(f"Office_Memo_{i}", (mx, 8.878, mz),
                 (0.14, 0.008, 0.18),
                 COL_WHITE_PANEL if i % 2 == 0 else COL_PAPER)
    # GOOD NEIGHBORS GOOD GROUND poster, office copy (east wall)
    make_box("Office_GG_Poster", (5.88, 7.20, 1.80),
             (0.012, 0.60, 0.85), COL_WALL_NEXCORP)
    make_box("Office_GG_Band", (5.868, 7.20, 2.02),
             (0.012, 0.48, 0.10), (0.86, 0.84, 0.74, 1.0))
    make_box("Office_GG_Ground", (5.868, 7.20, 1.52),
             (0.012, 0.48, 0.14), COL_SAGE)
    # Office fluorescent + frame
    make_box("Tube_Office", (4.5, 7.5, CEIL_Z - 0.08),
             (1.6, 0.40, 0.06), (0.96, 0.96, 0.92, 1.0))
    make_box("Troffer_Office", (4.5, 7.5, CEIL_Z - 0.11),
             (1.72, 0.48, 0.02), COL_METAL_STEEL)


# ════════════════════════════════════════════════════════════════
# AUTO-SUPPLY AISLE (one aisle, free-standing, E-W) + COFFEE
# ════════════════════════════════════════════════════════════════
def build_floor_props():
    # Single short gondola aisle (gas station, not a grocery).
    # Corporate planogram: ONE tint per shelf-side run — the
    # Kwik Stop cycles tints per item; NexCorp does not.
    ax, ay = -1.0, 4.0
    make_box("Aisle_Base", (ax, ay, 0.10),
             (5.0, 0.80, 0.20), COL_COUNTER_LAMINATE)
    make_box("Aisle_Spine", (ax, ay, 1.05),
             (5.0, 0.06, 1.90), COL_WALL_NEXCORP)
    for sh in range(3):
        shz = 0.50 + sh * 0.45
        for sy_sgn in (-1, +1):
            make_box(f"Aisle_Shelf_{sh}_y{sy_sgn:+d}",
                     (ax, ay + sy_sgn * 0.22, shz),
                     (5.0, 0.38, 0.04), COL_METAL_STEEL)
            make_box(f"Aisle_Rail_{sh}_y{sy_sgn:+d}",
                     (ax, ay + sy_sgn * 0.42, shz + 0.015),
                     (5.0, 0.02, 0.06), COL_WHITE_PANEL)
            tint = SNACK_TINTS[(sh * 2 + (0 if sy_sgn < 0 else 1))
                               % len(SNACK_TINTS)]
            for p in range(10):
                px = ax - 2.3 + p * 0.50
                make_box(f"Aisle_Product_{sh}_y{sy_sgn:+d}_{p}",
                         (px, ay + sy_sgn * 0.24, shz + 0.16),
                         (0.16, 0.20, 0.26), tint)
    # Aisle top sign — corporate blue, hung on rods
    make_box("Aisle_Sign", (ax, ay, 2.30),
             (5.0, 0.10, 0.26), COL_WALL_NEXCORP)
    for r, rx in enumerate([ax - 2.2, ax + 2.2]):
        make_cyl(f"Aisle_Sign_Rod_{r}", (rx, ay, 2.715),
                 0.008, 0.57, COL_METAL_STEEL, segments=6)

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

    # Beer fridge (single door, smaller than Kwik Stop's wall of
    # them). Relocated to the north-wall cooler run — the old
    # (-5.5, 8.0) spot interpenetrated lockers 5-6.
    fx, fy = -2.42, 8.50
    # Open-front carcass: back slab + cheeks + plinth/top so the
    # six-packs read through the door glass instead of sitting
    # buried inside a solid body box
    make_box("BeerFridge_Body", (fx, fy + 0.22, 1.20),
             (1.00, 0.36, 2.30), (0.42, 0.42, 0.46, 1.0))
    for tag, chx in [("W", fx - 0.47), ("E", fx + 0.47)]:
        make_box(f"BeerFridge_Cheek_{tag}", (chx, fy - 0.16, 1.20),
                 (0.06, 0.40, 2.30), (0.42, 0.42, 0.46, 1.0))
    make_box("BeerFridge_Plinth", (fx, fy - 0.16, 0.13),
             (1.00, 0.40, 0.16), (0.34, 0.34, 0.38, 1.0))
    make_box("BeerFridge_TopCap", (fx, fy - 0.16, 2.30),
             (1.00, 0.40, 0.10), (0.42, 0.42, 0.46, 1.0))
    make_box("BeerFridge_Glass", (fx, fy - 0.36, 1.20),
             (0.92, 0.04, 2.20), (0.46, 0.78, 0.92, 0.55))
    # Visible six-packs
    for sh in range(4):
        shz = 0.30 + sh * 0.50
        make_box(f"BeerFridge_Shelf_{sh}",
                 (fx, fy - 0.10, shz),
                 (0.86, 0.42, 0.02), COL_METAL_STEEL)
        for b in range(3):
            bx = fx - 0.30 + b * 0.30
            make_box(f"BeerFridge_Sixpack_{sh}_{b}",
                     (bx, fy - 0.12, shz + 0.17),
                     (0.24, 0.24, 0.30), SNACK_TINTS[(sh+b) % len(SNACK_TINTS)])

    # Restroom door — west wall, proud of the inner wall face at
    # x=-5.9 (the old x=-5.96 buried it inside the wall)
    make_box("Restroom_Door", (-5.87, 1.4, 1.05),
             (0.05, 0.90, 2.10), COL_WOOD)
    make_box("Restroom_Sign", (-5.83, 1.4, 2.30),
             (0.02, 0.30, 0.10), (0.96, 0.96, 0.96, 1.0))
    make_cyl("Restroom_Knob", (-5.82, 1.05, 1.00),
             0.03, 0.05, COL_CHROME, segments=8, axis='X')
    # M/W pictogram plates + the corporate key placard
    for i in range(2):
        make_box(f"Restroom_Picto_{i}", (-5.835, 1.28 + i * 0.24, 1.62),
                 (0.015, 0.10, 0.10), COL_WALL_NEXCORP)
    make_box("Restroom_Key_Placard", (-5.87, 2.10, 1.50),
             (0.012, 0.34, 0.22), COL_WHITE_PANEL)
    make_cyl("Restroom_Key_Hook", (-5.85, 2.10, 1.36),
             0.008, 0.05, COL_METAL_STEEL, segments=6, axis='X')


# ════════════════════════════════════════════════════════════════
# RETAIL FLOOR EXTENSION — second gondola, endcaps, auto-supply
# wall rack, hanging signs. Everything squared, everything rowed.
# ════════════════════════════════════════════════════════════════
def build_retail_floor():
    # Second gondola aisle, dead parallel to the first
    ax, ay = -0.3, 5.8
    make_box("Aisle2_Base", (ax, ay, 0.10),
             (3.8, 0.80, 0.20), COL_COUNTER_LAMINATE)
    make_box("Aisle2_Spine", (ax, ay, 1.05),
             (3.8, 0.06, 1.90), COL_WALL_NEXCORP)
    for sh in range(3):
        shz = 0.50 + sh * 0.45
        for sy_sgn in (-1, +1):
            make_box(f"Aisle2_Shelf_{sh}_y{sy_sgn:+d}",
                     (ax, ay + sy_sgn * 0.22, shz),
                     (3.8, 0.38, 0.04), COL_METAL_STEEL)
            make_box(f"Aisle2_Rail_{sh}_y{sy_sgn:+d}",
                     (ax, ay + sy_sgn * 0.42, shz + 0.015),
                     (3.8, 0.02, 0.06), COL_WHITE_PANEL)
            tint = SNACK_TINTS[(3 + sh * 2 + (0 if sy_sgn < 0 else 1))
                               % len(SNACK_TINTS)]
            for p in range(8):
                px = ax - 1.72 + p * 0.49
                make_box(f"Aisle2_Product_{sh}_y{sy_sgn:+d}_{p}",
                         (px, ay + sy_sgn * 0.24, shz + 0.16),
                         (0.16, 0.20, 0.26), tint)
    make_box("Aisle2_Sign", (ax, ay, 2.30),
             (3.8, 0.10, 0.26), COL_WALL_NEXCORP)
    for r, rx in enumerate([ax - 1.6, ax + 1.6]):
        make_cyl(f"Aisle2_Sign_Rod_{r}", (rx, ay, 2.715),
                 0.008, 0.57, COL_METAL_STEEL, segments=6)
    # Endcaps on aisle 2 — single-product promo stacks (uniform)
    for tag, ex, promo_tint in [("W", -2.55, COL_DUSTY_BLUE),
                                ("E", +1.95, SNACK_TINTS[0])]:
        make_box(f"Endcap_{tag}_Base", (ex, ay, 0.10),
                 (0.70, 0.80, 0.20), COL_COUNTER_LAMINATE)
        make_box(f"Endcap_{tag}_Back", (ex, ay, 1.00),
                 (0.06, 0.80, 1.80), COL_WALL_NEXCORP)
        for sh in range(3):
            shz = 0.44 + sh * 0.42
            make_box(f"Endcap_{tag}_Shelf_{sh}", (ex, ay, shz),
                     (0.60, 0.76, 0.04), COL_METAL_STEEL)
            for p in range(3):
                make_box(f"Endcap_{tag}_Item_{sh}_{p}",
                         (ex, ay - 0.25 + p * 0.25, shz + 0.15),
                         (0.30, 0.18, 0.24), promo_tint)
        make_box(f"Endcap_{tag}_Header", (ex, ay, 1.95),
                 (0.66, 0.70, 0.14), COL_AMBER_NEX)
    # Aisle-number discs — navy, hung at the aisle heads
    for ai, (nx, ny) in enumerate([(-3.3, 4.0), (-2.35, 5.8)]):
        make_cyl(f"AisleNum_Rod_{ai}", (nx, ny, CEIL_Z - 0.14),
                 0.008, 0.22, COL_METAL_STEEL, segments=6)
        make_cyl(f"AisleNum_Disc_{ai}", (nx, ny, CEIL_Z - 0.32),
                 0.15, 0.04, COL_WALL_NEXCORP, segments=12, axis='X')
        make_box(f"AisleNum_Band_{ai}", (nx - 0.025, ny, CEIL_Z - 0.32),
                 (0.01, 0.09, 0.09), COL_WHITE_PANEL)
    # Auto-supply rack on the east wall (motor oil in uniform
    # ranks — this is the "gas station first" wall)
    make_box("Oil_Rack_Back", (5.80, 4.6, 1.10),
             (0.06, 1.60, 2.00), COL_WALL_NEXCORP)
    for sh in range(3):
        shz = 0.50 + sh * 0.50
        make_box(f"Oil_Shelf_{sh}", (5.62, 4.6, shz),
                 (0.36, 1.60, 0.04), COL_METAL_STEEL)
        for b in range(6):
            make_box(f"Oil_Bottle_{sh}_{b}",
                     (5.62, 3.93 + b * 0.27, shz + 0.16),
                     (0.14, 0.14, 0.26),
                     (0.16, 0.16, 0.18, 1.0) if sh == 0
                     else SNACK_TINTS[4])
            make_box(f"Oil_Cap_{sh}_{b}",
                     (5.62, 3.93 + b * 0.27, shz + 0.31),
                     (0.06, 0.06, 0.05), COL_RED_ACCENT)
    make_box("Oil_Rack_Sign", (5.76, 4.6, 2.30),
             (0.04, 1.40, 0.24), COL_WALL_NEXCORP)
    # Washer-fluid jugs floor stack, 2x2, dusty-blue uniform
    for jx in range(2):
        for jy in range(2):
            make_box(f"WasherJug_{jx}_{jy}",
                     (5.42 + jx * 0.26, 3.38 + jy * 0.26, 0.19),
                     (0.22, 0.22, 0.38), COL_DUSTY_BLUE)
            make_box(f"WasherJug_Cap_{jx}_{jy}",
                     (5.42 + jx * 0.26, 3.38 + jy * 0.26, 0.41),
                     (0.06, 0.06, 0.06), COL_WHITE_PANEL)
    # Retail fire extinguisher (code) above the jugs
    make_box("Extinguisher2_Bracket", (5.88, 3.30, 1.22),
             (0.04, 0.10, 0.16), COL_METAL_BLACK)
    make_cyl("Extinguisher2_Tank", (5.78, 3.30, 1.20),
             0.07, 0.44, COL_RED_ACCENT, segments=10)
    # Hanging promo banners — corporate print, perfectly level
    for r, rx in enumerate([2.1, 2.9]):
        make_cyl(f"Banner_PayHere_Rod_{r}", (rx, 0.95, 2.79),
                 0.006, 0.42, COL_METAL_STEEL, segments=6)
    make_box("Banner_PayHere", (2.5, 0.95, 2.42),
             (1.10, 0.02, 0.32), COL_WALL_NEXCORP)
    make_box("Banner_PayHere_Text", (2.5, 0.935, 2.42),
             (0.90, 0.012, 0.16), COL_WHITE_PANEL)
    for r, rx in enumerate([-1.5, -0.5]):
        make_cyl(f"Banner_Promo_Rod_{r}", (rx, 6.9, 2.79),
                 0.006, 0.42, COL_METAL_STEEL, segments=6)
    make_box("Banner_Promo", (-1.0, 6.9, 2.42),
             (1.10, 0.02, 0.32), COL_WALL_NEXCORP)
    make_box("Banner_Promo_Text", (-1.0, 6.885, 2.42),
             (0.90, 0.012, 0.16), COL_AMBER_NEX)


# ════════════════════════════════════════════════════════════════
# COFFEE + FOUNTAIN — corporate coffee: two pots, a slushie
# machine, and the manila envelope tucked behind it (canon).
# ════════════════════════════════════════════════════════════════
def build_coffee_fountain():
    cfx = -5.0
    # Corporate menu panel on the wall above the station
    make_box("Coffee_Menu_Panel", (-5.88, 3.5, 2.10),
             (0.02, 1.60, 0.60), COL_WALL_NEXCORP)
    for m in range(3):
        make_box(f"Coffee_Menu_Bar_{m}", (-5.865, 3.5, 2.26 - m * 0.16),
                 (0.012, 1.30, 0.09), COL_WHITE_PANEL)
    # Slushie machine at the counter's north end. Canon (Skip's
    # file): "the manila envelope behind the slushie machine."
    make_box("Slushie_Body", (cfx - 0.05, 4.55, 1.02),
             (0.50, 0.50, 0.28), COL_WALL_NEXCORP)
    for i, s_tint in enumerate([COL_RED_ACCENT, COL_DUSTY_BLUE]):
        by = 4.42 + i * 0.26
        make_cyl(f"Slushie_Bowl_{i}", (cfx - 0.05, by, 1.32),
                 0.105, 0.30, COL_GLASS, segments=10)
        make_cyl(f"Slushie_Mix_{i}", (cfx - 0.05, by, 1.29),
                 0.09, 0.22, s_tint, segments=10)
        make_cyl(f"Slushie_Cap_{i}", (cfx - 0.05, by, 1.49),
                 0.08, 0.04, COL_PLASTIC_GREY, segments=10)
        make_box(f"Slushie_Tap_{i}", (cfx + 0.24, by, 1.05),
                 (0.06, 0.06, 0.10), COL_METAL_BLACK)
    make_box("Slushie_DripTray", (cfx + 0.26, 4.55, 0.90),
             (0.10, 0.40, 0.02), COL_METAL_STEEL)
    # The manila envelope, flat on the counter behind the machine
    make_box("Slushie_Envelope", (cfx - 0.44, 4.78, 0.885),
             (0.16, 0.22, 0.008), COL_MANILA)
    # Cup dispenser tube + lid stack + napkins + condiment caddy
    make_cyl("Coffee_CupTube", (cfx + 0.22, 3.9, 1.12),
             0.055, 0.48, COL_METAL_STEEL, segments=10)
    make_cyl("Coffee_LidStack", (cfx + 0.22, 3.62, 0.94),
             0.052, 0.12, COL_PLASTIC_GREY, segments=10)
    make_box("Coffee_Napkins", (cfx - 0.15, 3.35, 0.96),
             (0.16, 0.12, 0.16), COL_METAL_STEEL)
    make_box("Coffee_Caddy", (cfx - 0.10, 3.05, 0.93),
             (0.34, 0.24, 0.10), COL_PLASTIC_GREY)
    for c in range(3):
        make_box(f"Coffee_Caddy_Cell_{c}",
                 (cfx - 0.20 + c * 0.11, 3.05, 1.00),
                 (0.08, 0.20, 0.05),
                 [COL_WHITE_PANEL, COL_RED_ACCENT,
                  COL_AMBER_NEX][c])
    make_cyl("Coffee_StirCup", (cfx + 0.24, 3.2, 0.94),
             0.035, 0.12, COL_WHITE_PANEL, segments=8)
    # Swing-lid trash can at the station's south end
    make_cyl("Coffee_Trash_Body", (-3.95, 1.55, 0.42),
             0.22, 0.80, COL_PLASTIC_GREY, segments=12)
    make_cyl("Coffee_Trash_Lid", (-3.95, 1.55, 0.86),
             0.23, 0.06, COL_WALL_NEXCORP, segments=12)
    make_box("Coffee_Trash_Flap", (-3.95, 1.55, 0.93),
             (0.26, 0.20, 0.06), COL_WALL_NEXCORP)
    # Wet-floor cone by the machines — corporate compliance
    make_box("WetFloor_Base", (-3.80, 2.70, 0.02),
             (0.34, 0.34, 0.04), COL_CAUTION_YEL)
    for t in range(3):
        make_cyl(f"WetFloor_Tier_{t}", (-3.80, 2.70, 0.14 + t * 0.20),
                 0.13 - t * 0.035, 0.20, COL_CAUTION_YEL, segments=8)
    make_box("WetFloor_Band", (-3.80, 2.70, 0.34),
             (0.20, 0.20, 0.08), COL_WHITE_PANEL)


# ════════════════════════════════════════════════════════════════
# COOLER BANK — north wall, three branded doors. Planogram:
# one product tint per door. Header band is a Label3D anchor.
# ════════════════════════════════════════════════════════════════
def build_cooler_bank():
    # Open-front carcass (back slab + cheeks + fascia + plinth) so
    # the interior shelves READ through the translucent doors —
    # a solid body box would bury the product (invisible geometry)
    make_box("CoolerBank_Body", (0.55, 8.72, 1.25),
             (4.60, 0.35, 2.50), (0.30, 0.32, 0.36, 1.0))
    for tag, chx in [("W", -1.70), ("E", 2.80)]:
        make_box(f"CoolerBank_Cheek_{tag}", (chx, 8.35, 1.25),
                 (0.10, 0.40, 2.50), (0.30, 0.32, 0.36, 1.0))
    for m, mx in enumerate([-0.175, 1.275]):
        make_box(f"CoolerBank_Mullion_{m}", (mx, 8.35, 1.25),
                 (0.12, 0.40, 2.50), (0.30, 0.32, 0.36, 1.0))
    make_box("CoolerBank_Fascia", (0.55, 8.35, 2.45),
             (4.60, 0.40, 0.10), (0.30, 0.32, 0.36, 1.0))
    make_box("CoolerBank_Plinth", (0.55, 8.35, 0.06),
             (4.60, 0.40, 0.12), (0.24, 0.26, 0.30, 1.0))
    make_box("CoolerBank_Grille", (0.55, 8.16, 0.12),
             (4.50, 0.04, 0.20), COL_METAL_BLACK)
    make_box("CoolerBank_Header", (0.55, 8.35, 2.72),
             (4.70, 0.50, 0.36), COL_WALL_NEXCORP)
    make_box("CoolerBank_Header_Text", (0.55, 8.08, 2.72),
             (3.20, 0.02, 0.20), COL_WHITE_PANEL)
    door_tints = [SNACK_TINTS[0], COL_DUSTY_BLUE, COL_SAGE]
    for i, dx in enumerate([-0.90, 0.55, 2.00]):
        make_box(f"Cooler_{i}_Frame", (dx, 8.18, 1.25),
                 (1.36, 0.06, 2.30), COL_WALL_NEXCORP)
        make_box(f"Cooler_{i}_Glass", (dx, 8.16, 1.25),
                 (1.20, 0.04, 2.10), (0.42, 0.66, 0.84, 0.55))
        make_cyl(f"Cooler_{i}_Handle", (dx + 0.56, 8.10, 1.25),
                 0.02, 0.90, COL_CHROME, segments=8, axis='Z')
        make_box(f"Cooler_{i}_PriceStrip", (dx, 8.14, 2.24),
                 (1.20, 0.02, 0.08), COL_WHITE_PANEL)
        for sh in range(4):
            shz = 0.38 + sh * 0.50
            make_box(f"Cooler_{i}_Shelf_{sh}", (dx, 8.39, shz),
                     (1.18, 0.30, 0.02), COL_METAL_STEEL)
            for c in range(5):
                make_box(f"Cooler_{i}_Can_{sh}_{c}",
                         (dx - 0.44 + c * 0.22, 8.37, shz + 0.10),
                         (0.09, 0.09, 0.17), door_tints[i])
    # 21+ compliance chip on the beer fridge next door
    make_box("Beer21_Panel", (-2.42, 8.085, 2.20),
             (0.20, 0.012, 0.14), COL_WHITE_PANEL)
    make_box("Beer21_Band", (-2.42, 8.075, 2.24),
             (0.20, 0.012, 0.05), COL_RED_ACCENT)


# ════════════════════════════════════════════════════════════════
# CEILING SYSTEMS — the surveilled ceiling. Five smoked camera
# domes (one per zone, INCLUDING the breakroom), HVAC, sprinklers,
# PA speakers, conduit. The Kwik Stop has one camera; we have six.
# ════════════════════════════════════════════════════════════════
def build_ceiling_systems():
    # Camera domes — mount ring + smoked dome (cylinder approx)
    for i, (cx, cy) in enumerate([
            (0.0, 1.1),     # entry / door
            (3.5, 2.3),     # register
            (-1.0, 4.9),    # aisles
            (0.5, 7.3),     # cooler lane
            (-4.3, 7.0),    # breakroom — corporate watches staff
    ]):
        make_cyl(f"CamDome_Ring_{i}", (cx, cy, CEIL_Z - 0.02),
                 0.10, 0.03, COL_WHITE_PANEL, segments=12)
        make_cyl(f"CamDome_{i}", (cx, cy, CEIL_Z - 0.075),
                 0.075, 0.09, COL_CAM_SMOKE, segments=12)
    # HVAC supply diffusers + return grille
    for i, (vx, vy) in enumerate([(-2.4, 3.2), (1.8, 6.8)]):
        make_box(f"HVAC_Frame_{i}", (vx, vy, CEIL_Z - 0.02),
                 (0.60, 0.60, 0.04), COL_METAL_STEEL)
        for s in range(3):
            make_box(f"HVAC_Slat_{i}_{s}",
                     (vx, vy - 0.18 + s * 0.18, CEIL_Z - 0.045),
                     (0.52, 0.10, 0.02), COL_PLASTIC_GREY)
    make_box("HVAC_Return", (4.0, 4.8, CEIL_Z - 0.02),
             (0.80, 0.50, 0.04), COL_METAL_STEEL)
    for s in range(4):
        make_box(f"HVAC_Return_Slat_{s}",
                 (4.0, 4.65 + s * 0.10, CEIL_Z - 0.045),
                 (0.72, 0.05, 0.02), COL_METAL_BLACK)
    # Sprinkler pendants (4) + smoke detectors (2)
    for i, (sx, sy) in enumerate([(-3.5, 1.5), (3.0, 4.5),
                                  (-1.5, 7.5), (4.8, 7.8)]):
        make_cyl(f"Sprinkler_Stem_{i}", (sx, sy, CEIL_Z - 0.03),
                 0.012, 0.06, COL_METAL_STEEL, segments=6)
        make_cyl(f"Sprinkler_Head_{i}", (sx, sy, CEIL_Z - 0.07),
                 0.025, 0.03, COL_AMBER_NEX, segments=8)
    for i, (sx, sy) in enumerate([(0.0, 3.0), (-4.5, 6.4)]):
        make_cyl(f"SmokeDet_{i}", (sx, sy, CEIL_Z - 0.025),
                 0.07, 0.05, COL_WHITE_PANEL, segments=10)
    # PA speakers — corporate playlist and announcements
    for i, (sx, sy) in enumerate([(-2.0, 5.0), (3.0, 3.5)]):
        make_cyl(f"Speaker_Ring_{i}", (sx, sy, CEIL_Z - 0.015),
                 0.11, 0.03, COL_WHITE_PANEL, segments=12)
        make_cyl(f"Speaker_Cone_{i}", (sx, sy, CEIL_Z - 0.04),
                 0.08, 0.03, COL_PLASTIC_GREY, segments=12)
    # EMT conduit run: office wall → register camera drop
    make_cyl("Conduit_Run_X", (2.25, 2.2, CEIL_Z - 0.03),
             0.015, 4.50, COL_METAL_STEEL, segments=6, axis='X')
    make_cyl("Conduit_Run_Y", (4.5, 4.85, CEIL_Z - 0.03),
             0.015, 5.30, COL_METAL_STEEL, segments=6, axis='Y')
    make_box("Conduit_JBox_0", (4.5, 2.2, CEIL_Z - 0.05),
             (0.10, 0.10, 0.08), COL_PLASTIC_GREY)
    make_box("Conduit_JBox_1", (4.5, 7.5, CEIL_Z - 0.05),
             (0.10, 0.10, 0.08), COL_PLASTIC_GREY)
    # Troffer frames around every retail tube (uniform grid look)
    for j, ypos in enumerate([2.5, 6.0, 7.8]):
        for i in range(-1, 2):
            make_box(f"Troffer_{j}_{i}", (i * 2.4, ypos, CEIL_Z - 0.11),
                     (1.92, 0.48, 0.02), COL_METAL_STEEL)


# ════════════════════════════════════════════════════════════════
# EXTERIOR — pump canopy + 4 dispensers (8 fueling positions,
# canon) visible through the open south windows
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
    # 4 dispensers = the canonical EIGHT fueling positions
    # ("It has eight pumps" — vol6_ch1_gas_and_go.json). List
    # order keeps Pump_0/Pump_1 at their original stations.
    for i, px in enumerate([-1.5, +1.5, -4.5, +4.5]):
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
# FORECOURT DETAIL — islands, navy bollards, price sign, front
# walk, parking, ice merchandiser, propane cage, canopy branding.
# ════════════════════════════════════════════════════════════════
def build_forecourt_detail():
    cy = -4.0
    # Concrete pump islands + navy corporate bollards (the Kwik
    # Stop's bollards are yellow; NexCorp paints them brand navy)
    for i, px in enumerate([-1.5, +1.5, -4.5, +4.5]):
        make_box(f"Island_{i}", (px, cy, 0.075),
                 (1.10, 3.40, 0.15), COL_CONCRETE)
        for e, ey in enumerate([cy - 1.85, cy + 1.85]):
            make_cyl(f"Bollard_{i}_{e}", (px, ey, 0.45),
                     0.07, 0.90, COL_WALL_NEXCORP, segments=10)
            make_cyl(f"Bollard_Cap_{i}_{e}", (px, ey, 0.92),
                     0.075, 0.04, COL_AMBER_NEX, segments=10)
    # Windshield-service stations on the outer islands
    for i, px in enumerate([-4.5, +4.5]):
        make_cyl(f"Squeegee_Post_{i}", (px + 0.35, cy + 1.2, 0.55),
                 0.03, 1.10, COL_PLASTIC_GREY, segments=8)
        make_box(f"Squeegee_Box_{i}", (px + 0.35, cy + 1.2, 1.12),
                 (0.30, 0.22, 0.28), COL_WALL_NEXCORP)
        make_cyl(f"Squeegee_Bucket_{i}", (px + 0.35, cy + 1.2, 0.66),
                 0.13, 0.22, COL_METAL_BLACK, segments=10)
        make_box(f"Towel_Dispenser_{i}", (px - 0.35, cy + 1.3, 0.95),
                 (0.20, 0.16, 0.30), COL_PLASTIC_GREY)
    # Island trash cans, uniform navy
    for i, px in enumerate([-1.2, +4.8]):
        make_cyl(f"Island_Trash_{i}", (px, cy - 1.3, 0.42),
                 0.16, 0.80, COL_WALL_NEXCORP, segments=10)
        make_cyl(f"Island_Trash_Lid_{i}", (px, cy - 1.3, 0.84),
                 0.17, 0.05, COL_METAL_BLACK, segments=10)
    # Canopy branding — NEXCORP letter blocks + amber accent +
    # recessed light panels + a camera dome UNDER the canopy
    for i in range(7):
        make_box(f"Canopy_Letter_{i}",
                 (-1.26 + i * 0.42, cy - 2.465, 4.30),
                 (0.28, 0.02, 0.22), COL_WHITE_PANEL)
    make_box("Canopy_Accent", (0.0, cy - 2.46, 4.14),
             (10.2, 0.04, 0.06), COL_AMBER_NEX)
    for i, px in enumerate([-4.5, -1.5, 1.5, 4.5]):
        make_box(f"Canopy_Light_{i}", (px, cy, 4.33),
                 (0.90, 0.50, 0.05), (0.96, 0.96, 0.92, 1.0))
    make_cyl("Canopy_CamDome_Ring", (0.0, cy + 1.5, 4.33),
             0.10, 0.03, COL_WHITE_PANEL, segments=12)
    make_cyl("Canopy_CamDome", (0.0, cy + 1.5, 4.275),
             0.075, 0.09, COL_CAM_SMOKE, segments=12)
    # Price pole sign at the lot's south edge — panel meshes are
    # Label3D anchors
    make_cyl("PriceSign_Pole", (-4.0, -7.6, 1.30),
             0.12, 2.60, COL_METAL_STEEL, segments=10)
    make_box("PriceSign_Brand", (-4.0, -7.6, 3.30),
             (1.50, 0.14, 0.50), COL_WALL_NEXCORP)
    make_box("PriceSign_Panel", (-4.0, -7.6, 2.75),
             (1.50, 0.12, 0.60), COL_WHITE_PANEL)
    for r in range(3):
        make_box(f"PriceSign_Row_{r}", (-4.0, -7.67, 2.93 - r * 0.18),
                 (1.30, 0.012, 0.13), COL_DARK_SCREEN)
    make_box("PriceSign_Carwash", (-4.0, -7.6, 2.32),
             (1.50, 0.10, 0.22), COL_AMBER_NEX)
    # Front walk (concrete apron between storefront and lot)
    make_box("Front_Walk", (0.0, -0.75, -0.02),
             (12.40, 1.50, 0.06), COL_CONCRETE)
    for i in range(3):
        make_box(f"Front_Walk_Joint_{i}", (-4.0 + i * 4.0, -0.75, 0.012),
                 (0.03, 1.50, 0.002), (0.48, 0.46, 0.42, 1.0))
    for i, bx in enumerate([-2.0, 2.0]):
        make_cyl(f"Walk_Bollard_{i}", (bx, -1.25, 0.45),
                 0.07, 0.90, COL_WALL_NEXCORP, segments=10)
    # Ice merchandiser + propane cage on the walk (canon retail
    # exterior vocabulary, corporate paint)
    make_box("Ice_Body", (-2.9, -0.85, 0.75),
             (0.85, 0.75, 1.50), COL_WHITE_PANEL)
    make_box("Ice_Band", (-2.9, -1.24, 1.10),
             (0.85, 0.02, 0.36), COL_WALL_NEXCORP)
    make_box("Ice_Lid_Seam", (-2.9, -1.23, 0.62),
             (0.70, 0.012, 0.03), COL_PLASTIC_GREY)
    cage_x, cage_y = 5.35, -0.85
    for px_i, pxs in enumerate([-0.35, 0.35]):
        for py_i, pys in enumerate([-0.3, 0.3]):
            make_box(f"Propane_Post_{px_i}_{py_i}",
                     (cage_x + pxs, cage_y + pys, 0.70),
                     (0.05, 0.05, 1.40), COL_METAL_STEEL)
    for rz_i, rz in enumerate([0.25, 0.75, 1.25]):
        make_box(f"Propane_Rail_F_{rz_i}", (cage_x, cage_y - 0.3, rz),
                 (0.75, 0.03, 0.05), COL_METAL_STEEL)
        make_box(f"Propane_Rail_B_{rz_i}", (cage_x, cage_y + 0.3, rz),
                 (0.75, 0.03, 0.05), COL_METAL_STEEL)
    make_box("Propane_Roof", (cage_x, cage_y, 1.43),
             (0.80, 0.70, 0.05), COL_WALL_NEXCORP)
    for t in range(3):
        make_cyl(f"Propane_Tank_{t}", (cage_x - 0.22 + t * 0.22,
                                       cage_y, 0.30),
                 0.10, 0.50, COL_WHITE_PANEL, segments=10)
    # East parking strip — striped stalls + curb stops
    make_box("Lot_Asphalt_E", (7.0, -3.25, -0.05),
             (4.00, 6.50, 0.10), COL_ASPHALT)
    for i in range(4):
        make_box(f"Park_Stripe_{i}", (5.8 + i * 0.95, -5.2, 0.012),
                 (0.08, 2.40, 0.002), COL_STRIPE_WHITE)
    for i in range(3):
        make_box(f"Curb_Stop_{i}", (6.28 + i * 0.95, -6.1, 0.06),
                 (0.70, 0.16, 0.12), COL_CONCRETE)
    # Storefront placards on the piers (Label3D anchors) +
    # exterior door camera
    make_box("Hours_Placard", (-1.85, -0.115, 1.50),
             (0.24, 0.012, 0.34), COL_WHITE_PANEL)
    make_box("NoLoiter_Placard", (1.85, -0.115, 1.50),
             (0.24, 0.012, 0.34), COL_WHITE_PANEL)
    make_box("Ext_Cam_Arm", (1.9, -0.14, 2.78),
             (0.06, 0.10, 0.06), COL_PLASTIC_GREY)
    make_box("Ext_Cam_Body", (1.9, -0.24, 2.70),
             (0.10, 0.16, 0.10), COL_PLASTIC_GREY)
    make_cyl("Ext_Cam_Lens", (1.9, -0.33, 2.70),
             0.035, 0.03, COL_CAM_SMOKE, segments=8, axis='Y')


# ════════════════════════════════════════════════════════════════
# CAR WASH + EMPLOYEE LOT (rear) — canon: "eight pumps and a car
# wash in the rear," and the lot behind it where the black
# Louisiana pickup meets the white NexCorp van. Not visible from
# the counter window — exactly as written.
# ════════════════════════════════════════════════════════════════
def build_carwash_rear():
    # Tunnel body — entrance faces EAST (off the side drive),
    # exit faces NORTH into the employee lot
    make_box("Carwash_Body", (2.5, 13.0, 1.70),
             (5.00, 6.00, 3.40), COL_CONCRETE)
    make_box("Carwash_RoofBand", (2.5, 13.0, 3.55),
             (5.20, 6.20, 0.30), COL_WALL_NEXCORP)
    make_box("Carwash_Mouth_E", (4.98, 13.0, 1.30),
             (0.10, 3.00, 2.60), (0.05, 0.05, 0.06, 1.0))
    make_box("Carwash_Mouth_Frame_E", (5.02, 13.0, 2.70),
             (0.08, 3.20, 0.20), COL_AMBER_NEX)
    make_box("Carwash_Mouth_N", (2.5, 15.98, 1.30),
             (3.00, 0.10, 2.60), (0.05, 0.05, 0.06, 1.0))
    make_box("Carwash_SignPanel", (5.06, 13.0, 3.05),
             (0.06, 3.40, 0.50), COL_WALL_NEXCORP)
    make_box("Carwash_SignText", (5.10, 13.0, 3.05),
             (0.02, 2.40, 0.26), COL_WHITE_PANEL)
    # Side drive connecting the forecourt to the tunnel entrance
    make_box("Drive_E", (7.5, 4.75, -0.05),
             (3.00, 9.50, 0.10), COL_ASPHALT)
    make_box("Drive_E_Turn", (7.0, 12.0, -0.05),
             (4.00, 5.00, 0.10), COL_ASPHALT)
    # Employee lot behind the car wash
    make_box("EmpLot_Asphalt", (2.0, 18.0, -0.05),
             (12.00, 4.00, 0.10), COL_ASPHALT)
    for i in range(3):
        make_box(f"EmpLot_Stripe_{i}", (-2.0 + i * 2.6, 18.0, 0.012),
                 (0.08, 3.20, 0.002), COL_STRIPE_WHITE)
    # THE BLACK PICKUP, Louisiana plates (canon: parks behind the
    # car wash, engine off; Skip photographed it exactly once)
    make_box("Pickup_Chassis", (-1.0, 18.0, 0.62),
             (5.00, 1.85, 0.55), COL_TRUCK_BLACK)
    make_box("Pickup_Cab", (0.3, 18.0, 1.32),
             (1.70, 1.78, 0.75), COL_TRUCK_BLACK)
    make_box("Pickup_Hood", (1.80, 18.0, 1.00),
             (1.40, 1.75, 0.25), COL_TRUCK_BLACK)
    make_box("Pickup_Windshield", (1.18, 18.0, 1.42),
             (0.06, 1.60, 0.50), COL_WINDOW_TINT)
    make_box("Pickup_Bed_Tailgate", (-3.46, 18.0, 1.02),
             (0.08, 1.80, 0.35), COL_TRUCK_BLACK)
    for sgn in (-1, +1):
        make_box(f"Pickup_Bed_Rail_{sgn:+d}", (-2.0, 18.0 + sgn * 0.86, 1.02),
                 (2.90, 0.08, 0.35), COL_TRUCK_BLACK)
    for wi, wx in enumerate([-2.4, 1.5]):
        for sgn in (-1, +1):
            make_cyl(f"Pickup_Wheel_{wi}_{sgn:+d}",
                     (wx, 18.0 + sgn * 0.95, 0.38),
                     0.38, 0.24, (0.06, 0.06, 0.07, 1.0),
                     segments=10, axis='Y')
    make_box("Pickup_Plate_LA", (-3.52, 18.0, 0.72),
             (0.02, 0.32, 0.16), COL_WHITE_PANEL)
    make_box("Pickup_Plate_Band", (-3.535, 18.0, 0.77),
             (0.012, 0.28, 0.04), COL_AMBER_NEX)
    # THE WHITE NEXCORP VAN, parked next to it (canon)
    make_box("NexVan_Body", (4.5, 18.0, 1.35),
             (4.40, 2.00, 1.70), COL_VAN_WHITE)
    make_box("NexVan_Nose", (6.90, 18.0, 0.95),
             (0.50, 1.90, 0.90), COL_VAN_WHITE)
    make_box("NexVan_Windshield", (6.72, 18.0, 1.72),
             (0.06, 1.70, 0.55), COL_WINDOW_TINT)
    for wi, wx in enumerate([3.3, 6.2]):
        for sgn in (-1, +1):
            make_cyl(f"NexVan_Wheel_{wi}_{sgn:+d}",
                     (wx, 18.0 + sgn * 1.02, 0.36),
                     0.35, 0.22, (0.06, 0.06, 0.07, 1.0),
                     segments=10, axis='Y')
    for sgn in (-1, +1):
        make_box(f"NexVan_Band_{sgn:+d}", (4.5, 18.0 + sgn * 1.02, 1.40),
                 (3.00, 0.03, 0.40), COL_WALL_NEXCORP)
        make_box(f"NexVan_Logo_{sgn:+d}", (4.5, 18.0 + sgn * 1.045, 1.40),
                 (1.60, 0.012, 0.16), COL_WHITE_PANEL)
    make_box("NexVan_RearSeam", (2.28, 18.0, 1.35),
             (0.02, 1.60, 1.40), (0.78, 0.78, 0.80, 1.0))


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


def main():
    clear_scene()
    # Shell + interior zones
    build_shell()
    build_shell_polish()
    build_counter()
    build_counter_zone()
    build_backbar_dressing()
    build_entry_zone()
    build_lockers()
    build_backroom()
    build_office()
    build_office_detail()
    build_floor_props()
    build_retail_floor()
    build_coffee_fountain()
    build_cooler_bank()
    build_ceiling_systems()
    # Exterior zones
    build_pump_canopy()
    build_forecourt_detail()
    build_carwash_rear()
    export_glb()


if __name__ == "__main__":
    main()
