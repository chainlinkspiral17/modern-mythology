"""
build_kwik_stop.py
══════════════════════════════════════════════════════════════════
VOL 6 · The Kwik Stop · Sam Miller's register.

Single-room convenience store at the intersection across from
NexCorp Gas & Go. Hot Pockets, the wire basket of left-behind
objects on the counter, the back cooler whose reflection contains
an infinite recursion of its own surface (per _VOL6_WIKI.md).

Footprint: 14m W (X) × 11m D (Y), single floor, ~3.2m ceiling.
Entrance at south (Y=0, automatic glass doors). Counter + register
at north-east (Sam's post). Beer cooler along the north wall.
Three snack aisles running E-W in the middle. Coffee + slurpee
station against the west wall.

COORDINATE FRAME (Blender → Godot):
    +X east  → +X
    +Y north → -Z
    +Z up    → +Y
1 unit = 1 m. Interior X ∈ [-7, +7], Y ∈ [0, +11].

Run:
    blender --background --python build_kwik_stop.py
    (or ./run_cathedral.sh build_kwik_stop.py)

Output:
    godot/assets/3d/locales/kwik_stop.glb
"""

import bpy
import math
import os
import sys

_SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
if _SCRIPT_DIR not in sys.path:
    sys.path.insert(0, _SCRIPT_DIR)

OUTPUT_DIR  = "../../../assets/3d/locales"
OUTPUT_NAME = "kwik_stop.glb"


# ── Palette ──────────────────────────────────────────────────────
# Convenience-store fluorescent: cold whites, primary-color brand
# accents, beer-cooler blue, linoleum-floor tan.
COL_FLOOR_VINYL     = (0.82, 0.78, 0.68, 1.0)   # off-white linoleum
COL_FLOOR_TILE_DARK = (0.32, 0.30, 0.28, 1.0)   # the dark grout strips
COL_WALL_WHITE      = (0.92, 0.94, 0.94, 1.0)   # cold-white painted wall
COL_WALL_BRAND_RED  = (0.78, 0.18, 0.16, 1.0)   # Kwik Stop brand red
COL_CEILING_TILE    = (0.88, 0.90, 0.88, 1.0)   # acoustic ceiling tile
COL_GLASS           = (0.62, 0.78, 0.82, 0.55)  # automatic-door glass
COL_GLASS_FROST     = (0.86, 0.92, 0.94, 0.75)
COL_METAL_STEEL     = (0.66, 0.68, 0.70, 1.0)
COL_METAL_BLACK     = (0.18, 0.16, 0.14, 1.0)
COL_PLASTIC_RED     = (0.86, 0.22, 0.18, 1.0)
COL_PLASTIC_BLUE    = (0.18, 0.42, 0.78, 1.0)
COL_PLASTIC_YELLOW  = (0.96, 0.86, 0.28, 1.0)
COL_PLASTIC_GREEN   = (0.32, 0.72, 0.42, 1.0)
COL_PLASTIC_ORANGE  = (0.96, 0.62, 0.22, 1.0)

# Brand color blocks for snack packaging
SNACK_TINTS = [
    (0.96, 0.32, 0.18, 1.0),   # red
    (0.18, 0.62, 0.92, 1.0),   # blue
    (0.96, 0.86, 0.28, 1.0),   # yellow
    (0.32, 0.78, 0.42, 1.0),   # green
    (0.96, 0.46, 0.22, 1.0),   # orange
    (0.66, 0.32, 0.78, 1.0),   # purple
    (0.88, 0.88, 0.88, 1.0),   # silver
]

COL_COOLER_GLASS    = (0.46, 0.78, 0.92, 0.55)  # beer-cooler tint
COL_COOLER_INTERIOR = (0.10, 0.18, 0.26, 1.0)   # cold-cooler glow base
COL_COFFEE_BROWN    = (0.32, 0.18, 0.10, 1.0)
COL_PAPER           = (0.92, 0.88, 0.78, 1.0)
COL_WIRE_BASKET     = (0.42, 0.40, 0.38, 1.0)

CEIL_Z = 3.20


# ── Geometry helpers (vendored from build_riverfront.py) ─────────
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
        (cx - hx, cy - hy, cz - hz), (cx + hx, cy - hy, cz - hz),
        (cx + hx, cy + hy, cz - hz), (cx - hx, cy + hy, cz - hz),
        (cx - hx, cy - hy, cz + hz), (cx + hx, cy - hy, cz + hz),
        (cx + hx, cy + hy, cz + hz), (cx - hx, cy + hy, cz + hz),
    ]
    face_defs = [
        ('-Z', (0, 3, 2, 1)), ('+Z', (4, 5, 6, 7)),
        ('-Y', (0, 1, 5, 4)), ('+Y', (2, 3, 7, 6)),
        ('-X', (3, 0, 4, 7)), ('+X', (1, 2, 6, 5)),
    ]
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
# SHELL — walls, floor, ceiling, glass front
# ════════════════════════════════════════════════════════════════
def build_shell():
    # Floor — linoleum
    make_box("Floor",
             (0.0, 5.5, -0.05),
             (14.4, 11.4, 0.10), COL_FLOOR_VINYL)
    # Floor grid pattern — dark grout strips every 1m (subtle)
    for i in range(-6, 7):
        make_box(f"Floor_Grid_X_{i}",
                 (i * 1.0, 5.5, 0.005),
                 (0.02, 11.4, 0.001), COL_FLOOR_TILE_DARK)
    for j in range(0, 12):
        make_box(f"Floor_Grid_Y_{j}",
                 (0.0, float(j), 0.005),
                 (14.4, 0.02, 0.001), COL_FLOOR_TILE_DARK)

    # East + West walls
    for sgn, xpos in [(-1, -7.0), (+1, +7.0)]:
        make_box(f"Wall_X{sgn:+d}",
                 (xpos, 5.5, CEIL_Z / 2.0),
                 (0.20, 11.4, CEIL_Z), COL_WALL_WHITE)
    # North wall (back, beer cooler runs along it)
    make_box("Wall_N",
             (0.0, 11.0, CEIL_Z / 2.0),
             (14.4, 0.20, CEIL_Z), COL_WALL_WHITE)
    # South wall — has the automatic glass doors cut out at center
    # Doors span X ∈ [-1.6, +1.6], rest is brick / branded panel
    make_box("Wall_S_W",
             (-4.40, 0.0, CEIL_Z / 2.0),
             (5.20, 0.20, CEIL_Z), COL_WALL_BRAND_RED)
    make_box("Wall_S_E",
             (+4.40, 0.0, CEIL_Z / 2.0),
             (5.20, 0.20, CEIL_Z), COL_WALL_BRAND_RED)
    # Above-door header
    make_box("Wall_S_AboveDoor",
             (0.0, 0.0, CEIL_Z - 0.30),
             (3.40, 0.20, 0.60), COL_WALL_BRAND_RED)
    # KWIK STOP sign on the south brand panel exterior
    make_box("Brand_Sign_Bg",
             (0.0, -0.02, 2.45),
             (3.20, 0.04, 0.40), (0.95, 0.92, 0.86, 1.0))
    # The "KWIK" half (red letters on white)
    make_box("Brand_Sign_KWIK",
             (-0.78, -0.04, 2.45),
             (1.32, 0.005, 0.24), COL_WALL_BRAND_RED)
    # The "STOP" half (red letters)
    make_box("Brand_Sign_STOP",
             (+0.78, -0.04, 2.45),
             (1.32, 0.005, 0.24), COL_WALL_BRAND_RED)

    # Glass double doors — frame + glass
    make_box("Door_Frame_T",
             (0.0, 0.0, 2.10),
             (3.20, 0.10, 0.08), COL_METAL_STEEL)
    make_box("Door_Frame_B",
             (0.0, 0.0, 0.06),
             (3.20, 0.10, 0.08), COL_METAL_STEEL)
    make_box("Door_Frame_DividerMid",
             (0.0, 0.0, 1.05),
             (0.06, 0.10, 2.00), COL_METAL_STEEL)
    # Left door glass + right door glass
    make_box("Door_Glass_L",
             (-0.80, 0.0, 1.05),
             (1.40, 0.04, 2.00), COL_GLASS)
    make_box("Door_Glass_R",
             (+0.80, 0.0, 1.05),
             (1.40, 0.04, 2.00), COL_GLASS)
    # Door handles (horizontal pulls)
    for sx in (-1, +1):
        make_cyl(f"Door_Handle_{sx}",
                 (sx * 0.20, -0.05, 1.10),
                 0.018, 0.30, COL_METAL_BLACK,
                 segments=8, axis='Y')

    # Picture windows on either side of the doors (south wall)
    for sgn, cx in [(-1, -3.50), (+1, +3.50)]:
        # Cut out the brand-red wall behind by drawing a glass
        # rect on top
        make_box(f"Window_S_{sgn:+d}",
                 (cx, -0.02, 1.55),
                 (2.40, 0.04, 1.50), COL_GLASS)
        # Mullion in the middle
        make_box(f"Window_S_{sgn:+d}_Mull",
                 (cx, -0.04, 1.55),
                 (0.05, 0.05, 1.50), COL_METAL_STEEL)

    # Ceiling — acoustic tile grid
    make_box("Ceiling",
             (0.0, 5.5, CEIL_Z + 0.05),
             (14.4, 11.4, 0.10), COL_CEILING_TILE)
    # Tile-grid divider strips
    for i in range(-6, 7):
        make_box(f"Ceiling_Grid_X_{i}",
                 (i * 1.0, 5.5, CEIL_Z + 0.02),
                 (0.04, 11.4, 0.005), (0.62, 0.62, 0.60, 1.0))
    for j in range(0, 12):
        make_box(f"Ceiling_Grid_Y_{j}",
                 (0.0, float(j), CEIL_Z + 0.02),
                 (14.4, 0.04, 0.005), (0.62, 0.62, 0.60, 1.0))

    # Fluorescent tube fixtures — 6 strips, two rows
    for j, ypos in enumerate([3.0, 8.0]):
        for i in range(-2, 3):
            xp = i * 2.4
            make_box(f"FluorescentTube_{j}_{i}",
                     (xp, ypos, CEIL_Z - 0.08),
                     (1.8, 0.40, 0.06), (0.96, 0.96, 0.92, 1.0))
            # Diffuser frame
            make_box(f"FluorescentFrame_{j}_{i}",
                     (xp, ypos, CEIL_Z - 0.10),
                     (1.85, 0.46, 0.02), COL_METAL_STEEL)


# ════════════════════════════════════════════════════════════════
# COUNTER + REGISTER (Sam's post)
# ════════════════════════════════════════════════════════════════
def build_counter():
    # Counter L-shaped against north-east of front area.
    # Main run: X ∈ [+2.5, +6.5], Y = +1.5 (front-facing customer side)
    cx, cy, cz = 4.5, 1.5, 0.50
    # Front counter
    make_box("Counter_Front",
             (cx, cy, cz),
             (4.0, 0.60, 1.00), (0.32, 0.30, 0.28, 1.0))
    # Counter top
    make_box("Counter_Top",
             (cx, cy, 1.04),
             (4.10, 0.70, 0.06), (0.12, 0.12, 0.14, 1.0))
    # Front kick panel
    make_box("Counter_FrontPanel",
             (cx, cy - 0.32, 0.50),
             (4.0, 0.02, 0.95), (0.18, 0.16, 0.14, 1.0))

    # Cash register
    make_box("Register_Body",
             (cx - 1.0, cy + 0.10, 1.25),
             (0.36, 0.40, 0.32), (0.20, 0.20, 0.22, 1.0))
    make_box("Register_Display",
             (cx - 1.0, cy + 0.32, 1.42),
             (0.30, 0.04, 0.10), (0.10, 0.32, 0.16, 1.0))
    make_box("Register_Keypad",
             (cx - 1.0, cy + 0.10, 1.10),
             (0.32, 0.36, 0.02), (0.32, 0.32, 0.34, 1.0))
    make_box("Register_Drawer",
             (cx - 1.0, cy, 0.94),
             (0.40, 0.50, 0.10), (0.20, 0.20, 0.22, 1.0))

    # Lottery scratch-off display (vertical multi-color rack)
    for i in range(5):
        ly = cy + 0.20
        lx = cx + 0.20 + i * 0.18
        col = SNACK_TINTS[i % len(SNACK_TINTS)]
        make_box(f"Lottery_Ticket_{i}",
                 (lx, ly, 1.28),
                 (0.14, 0.04, 0.24), col)
    # Lottery rack frame
    make_box("Lottery_Rack",
             (cx + 0.55, cy + 0.22, 1.28),
             (1.10, 0.06, 0.30), COL_METAL_BLACK)

    # The WIRE BASKET — canonical motif (left-behind objects)
    # Sits on the counter near the register, customer-side
    make_cyl("WireBasket",
             (cx - 0.30, cy - 0.10, 1.12),
             0.16, 0.10, COL_WIRE_BASKET, segments=10)
    # A receipt sticking out
    make_box("WireBasket_Receipt",
             (cx - 0.30, cy - 0.10, 1.18),
             (0.10, 0.06, 0.004), COL_PAPER)
    # A keyring (small ring)
    make_cyl("WireBasket_Keys",
             (cx - 0.34, cy - 0.06, 1.20),
             0.022, 0.005, COL_METAL_STEEL, segments=8, axis='Y')

    # Hot food / Hot Pockets case — behind counter, server-side
    make_box("HotCase",
             (cx, cy + 0.50, 1.30),
             (1.40, 0.40, 0.50), (0.96, 0.94, 0.88, 1.0))
    make_box("HotCase_Glass",
             (cx, cy + 0.32, 1.30),
             (1.40, 0.04, 0.48), COL_GLASS)
    make_box("HotCase_Lamp",
             (cx, cy + 0.50, 1.52),
             (1.40, 0.40, 0.06), (1.0, 0.85, 0.38, 1.0))
    # 3 Hot Pockets visible inside
    for i in range(3):
        hp_x = cx - 0.35 + i * 0.35
        make_box(f"HotPocket_{i}",
                 (hp_x, cy + 0.42, 1.18),
                 (0.20, 0.14, 0.08),
                 (0.78, 0.62, 0.42, 1.0))

    # Cigarette / tobacco shelves on north wall behind counter
    cig_y = 10.85
    for sh in range(4):
        shz = 1.40 + sh * 0.40
        make_box(f"CigShelf_{sh}_Plank",
                 (cx + 0.5, cig_y, shz),
                 (3.40, 0.22, 0.02), (0.72, 0.60, 0.46, 1.0))
        # Cigarette boxes (cartons)
        for ci in range(14):
            box_x = cx + 0.5 - 1.55 + ci * 0.24
            box_col = SNACK_TINTS[(sh + ci) % len(SNACK_TINTS)]
            make_box(f"CigBox_{sh}_{ci}",
                     (box_x, cig_y - 0.04, shz + 0.12),
                     (0.20, 0.12, 0.22), box_col)

    # Coin-trough on customer side
    make_cyl("CoinTrough",
             (cx + 0.40, cy - 0.10, 1.10),
             0.06, 0.10, COL_METAL_BLACK, segments=8, axis='Y')

    # Stool on the server side (Sam sits on the long shifts)
    make_cyl("Stool_Seat",
             (cx, cy + 0.32, 0.66),
             0.16, 0.04, COL_PLASTIC_BLUE, segments=10)
    make_cyl("Stool_Post",
             (cx, cy + 0.32, 0.36),
             0.030, 0.56, COL_METAL_BLACK)
    make_cyl("Stool_Base",
             (cx, cy + 0.32, 0.05),
             0.20, 0.04, COL_METAL_BLACK, segments=8)


# ════════════════════════════════════════════════════════════════
# COFFEE + SLURPEE STATION (west wall)
# ════════════════════════════════════════════════════════════════
def build_coffee_station():
    cx = -6.20
    # Counter run along west wall, Y ∈ [+2, +6]
    make_box("Coffee_Counter",
             (cx, 4.0, 0.86),
             (1.60, 4.00, 0.04), (0.32, 0.30, 0.28, 1.0))
    make_box("Coffee_CounterBase",
             (cx, 4.0, 0.42),
             (1.60, 4.00, 0.84), (0.18, 0.16, 0.14, 1.0))

    # Coffee pots (3 different blends, dark/medium/decaf)
    for i, tint in enumerate([
            (0.18, 0.10, 0.06, 1.0),  # dark
            (0.32, 0.18, 0.10, 1.0),  # medium
            (0.42, 0.32, 0.20, 1.0)]):  # decaf
        pot_y = 2.4 + i * 0.50
        # Pot body
        make_cyl(f"Coffee_Pot_{i}_Body",
                 (cx - 0.20, pot_y, 1.10),
                 0.10, 0.30, COL_GLASS, segments=8)
        # Coffee inside
        make_cyl(f"Coffee_Pot_{i}_Liquid",
                 (cx - 0.20, pot_y, 1.04),
                 0.085, 0.20, tint, segments=8)
        # Burner plate underneath
        make_cyl(f"Coffee_Pot_{i}_Burner",
                 (cx - 0.20, pot_y, 0.91),
                 0.13, 0.02, COL_METAL_BLACK, segments=8)

    # Slurpee machine — twin-barrel
    for i, tint in enumerate([
            (0.62, 0.18, 0.78, 1.0),  # blue raspberry / purple
            (0.96, 0.32, 0.18, 1.0)]):  # cherry
        sl_y = 4.40 + i * 0.50
        make_cyl(f"Slurpee_{i}_Barrel",
                 (cx - 0.20, sl_y, 1.30),
                 0.16, 0.48, tint, segments=10)
        # Drum top (motor housing)
        make_cyl(f"Slurpee_{i}_TopCap",
                 (cx - 0.20, sl_y, 1.58),
                 0.18, 0.10, COL_METAL_STEEL, segments=10)
        # Dispense spout
        make_cyl(f"Slurpee_{i}_Spout",
                 (cx - 0.20, sl_y - 0.16, 1.16),
                 0.025, 0.10, COL_METAL_BLACK, segments=6, axis='Z')

    # Cup stack
    for i in range(6):
        make_cyl(f"Coffee_Cup_{i}",
                 (cx + 0.30, 2.40, 0.90 + i * 0.04),
                 0.04, 0.04, (0.92, 0.86, 0.74, 1.0), segments=10)

    # Lid dispenser
    make_box("Coffee_LidDispenser",
             (cx + 0.30, 2.80, 0.95),
             (0.20, 0.20, 0.18), COL_METAL_STEEL)

    # Cream + sugar caddy
    make_box("Coffee_CreamSugar_Caddy",
             (cx + 0.30, 5.30, 0.92),
             (0.50, 0.30, 0.12), (0.78, 0.68, 0.52, 1.0))
    for i in range(3):
        col = [(0.96, 0.96, 0.96, 1.0),
               (0.32, 0.22, 0.16, 1.0),
               (0.78, 0.74, 0.60, 1.0)][i]
        make_box(f"Coffee_CreamSugar_{i}",
                 (cx + 0.30 - 0.16 + i * 0.16, 5.30, 1.02),
                 (0.10, 0.10, 0.08), col)


# ════════════════════════════════════════════════════════════════
# BEER COOLER (north wall, glass doors with cold blue glow)
# ════════════════════════════════════════════════════════════════
def build_beer_cooler():
    # 4 glass-door panels along the back wall, Y=10.5
    # Sam canonically watches the back-cooler customer through these
    cy = 10.50
    for i, sx in enumerate(range(-3, 4)):
        cx = sx * 1.0
        if abs(cx) > 6.0:
            continue
        # Inset cooler box (recessed into the wall)
        make_box(f"Cooler_Body_{i}",
                 (cx, cy + 0.30, 1.40),
                 (0.92, 0.40, 2.10), COL_COOLER_INTERIOR)
        # Glass door
        make_box(f"Cooler_Glass_{i}",
                 (cx, cy + 0.08, 1.40),
                 (0.88, 0.04, 2.00), COL_COOLER_GLASS)
        # Door frame
        for sgn, sz in [(-1, 'L'), (+1, 'R')]:
            make_box(f"Cooler_Frame_{i}_{sz}",
                     (cx + sgn * 0.44, cy + 0.06, 1.40),
                     (0.04, 0.08, 2.00), COL_METAL_STEEL)
        make_box(f"Cooler_Frame_{i}_T",
                 (cx, cy + 0.06, 2.40),
                 (0.92, 0.08, 0.04), COL_METAL_STEEL)
        make_box(f"Cooler_Frame_{i}_B",
                 (cx, cy + 0.06, 0.40),
                 (0.92, 0.08, 0.04), COL_METAL_STEEL)
        # Handle
        make_box(f"Cooler_Handle_{i}",
                 (cx + 0.42, cy + 0.04, 1.40),
                 (0.02, 0.06, 0.60), COL_METAL_BLACK)
        # Shelves visible through glass — 4 rows of beer cans / 6-packs
        for sh in range(4):
            shz = 0.55 + sh * 0.45
            make_box(f"Cooler_Shelf_{i}_{sh}",
                     (cx, cy + 0.30, shz),
                     (0.84, 0.30, 0.02), COL_METAL_STEEL)
            # 4 six-packs per shelf (rough)
            for b in range(4):
                bx = cx - 0.32 + b * 0.22
                tint = SNACK_TINTS[(i + sh + b) % len(SNACK_TINTS)]
                make_box(f"Cooler_Sixpack_{i}_{sh}_{b}",
                         (bx, cy + 0.30, shz + 0.20),
                         (0.18, 0.22, 0.30), tint)


# ════════════════════════════════════════════════════════════════
# SNACK AISLES (3 aisles, free-standing, running E-W)
# ════════════════════════════════════════════════════════════════
def build_snack_aisles():
    # 3 aisles, each running E-W, at Y=4, 6, 8
    for j, ay in enumerate([4.0, 6.0, 8.0]):
        # Aisle support base
        make_box(f"Aisle_{j}_Base",
                 (0.0, ay, 0.10),
                 (8.0, 0.80, 0.20), (0.32, 0.30, 0.28, 1.0))
        # 4 shelves stacked
        for sh in range(4):
            shz = 0.40 + sh * 0.50
            # Two-sided shelf — facing north (+Y side) and south (-Y side)
            for sy_sgn in (-1, +1):
                # Shelf plank
                make_box(f"Aisle_{j}_Shelf_{sh}_y{sy_sgn:+d}",
                         (0.0, ay + sy_sgn * 0.38, shz),
                         (8.0, 0.04, 0.30), COL_METAL_STEEL)
                # Products on the shelf — random mix of snack tints
                for p in range(16):
                    px = -3.8 + p * 0.48
                    tint = SNACK_TINTS[(j * 7 + sh * 3 + p) % len(SNACK_TINTS)]
                    h = 0.20 if (p % 3 != 0) else 0.28
                    make_box(f"Aisle_{j}_Snack_{sh}_y{sy_sgn:+d}_{p}",
                             (px, ay + sy_sgn * 0.30, shz + h / 2.0 + 0.02),
                             (0.16, 0.20, h), tint)
        # Top sign panel (the aisle label)
        make_box(f"Aisle_{j}_TopSign",
                 (0.0, ay, 2.50),
                 (8.0, 0.10, 0.30), COL_WALL_BRAND_RED)


# ════════════════════════════════════════════════════════════════
# MAGAZINE RACK (between the aisles and the windows, south)
# ════════════════════════════════════════════════════════════════
def build_magazine_rack():
    # Slanted-shelf magazine rack against west side, near windows
    mr_x, mr_y = -6.0, 2.0
    make_box("MagRack_Body",
             (mr_x, mr_y, 0.90),
             (0.40, 1.20, 1.80), COL_METAL_BLACK)
    # 4 slanted shelves with magazines
    for i in range(4):
        sy = mr_y - 0.50 + i * 0.34
        make_box(f"MagRack_Shelf_{i}",
                 (mr_x, sy, 0.50 + i * 0.34),
                 (0.40, 0.30, 0.02), COL_METAL_STEEL)
        # 2-3 magazines per shelf
        for m in range(3):
            mx = mr_x + 0.06 - m * 0.04
            col = SNACK_TINTS[(i + m) % len(SNACK_TINTS)]
            make_box(f"MagRack_Mag_{i}_{m}",
                     (mx, sy, 0.62 + i * 0.34),
                     (0.10, 0.20, 0.26), col)


# ════════════════════════════════════════════════════════════════
# FLOOR DETAILS — ATM, trash, mop bucket
# ════════════════════════════════════════════════════════════════
def build_floor_props():
    # ATM near south door, east side
    atm_x, atm_y = 5.0, 0.80
    make_box("ATM_Body",
             (atm_x, atm_y, 0.75),
             (0.50, 0.40, 1.50), (0.42, 0.42, 0.46, 1.0))
    make_box("ATM_Screen",
             (atm_x, atm_y - 0.18, 1.15),
             (0.30, 0.04, 0.20), (0.18, 0.32, 0.46, 1.0))
    make_box("ATM_Keypad",
             (atm_x, atm_y - 0.18, 0.92),
             (0.20, 0.04, 0.16), (0.22, 0.22, 0.24, 1.0))
    # Slot
    make_box("ATM_Slot",
             (atm_x, atm_y - 0.20, 0.75),
             (0.20, 0.01, 0.02), COL_METAL_BLACK)

    # Trash can near door
    make_cyl("Trash_Body",
             (5.80, 0.70, 0.42),
             0.22, 0.80, (0.42, 0.30, 0.18, 1.0), segments=10)
    make_cyl("Trash_Rim",
             (5.80, 0.70, 0.82),
             0.24, 0.04, COL_METAL_BLACK, segments=10)
    # Trash bag visible
    make_box("Trash_Bag",
             (5.80, 0.70, 0.55),
             (0.36, 0.36, 0.20), (0.18, 0.18, 0.18, 1.0))

    # WIRE BASKET on the floor near the door — the canonical
    # left-behind-objects basket (second one besides the counter one)
    make_cyl("FloorBasket_Body",
             (-5.50, 0.85, 0.20),
             0.22, 0.40, COL_WIRE_BASKET, segments=10)
    # An umbrella sticking out (left-behind)
    make_cyl("FloorBasket_Umbrella_Shaft",
             (-5.50, 0.85, 0.65),
             0.012, 0.50, COL_METAL_BLACK)
    make_box("FloorBasket_Umbrella_Top",
             (-5.50, 0.85, 0.85),
             (0.16, 0.16, 0.08), (0.16, 0.42, 0.18, 1.0))

    # Floor mat at entrance
    make_box("Entry_Mat",
             (0.0, 0.65, 0.012),
             (3.0, 1.20, 0.02), (0.18, 0.18, 0.20, 1.0))
    # WELCOME text on mat (decorative dark band)
    make_box("Entry_Mat_Text",
             (0.0, 0.65, 0.014),
             (1.80, 0.20, 0.002), (0.32, 0.32, 0.34, 1.0))


# ════════════════════════════════════════════════════════════════
# EXPORT
# ════════════════════════════════════════════════════════════════
def export_glb():
    out_dir = os.path.normpath(
        os.path.join(os.path.dirname(os.path.abspath(__file__)), OUTPUT_DIR))
    os.makedirs(out_dir, exist_ok=True)
    out_path = os.path.join(out_dir, OUTPUT_NAME)
    print(f"\n[build_kwik_stop] exporting to {out_path}")
    print(f"[build_kwik_stop] scene objects: {len(bpy.context.scene.objects)}")
    bpy.ops.object.select_all(action='SELECT')
    base = {
        'filepath': out_path, 'export_format': 'GLB',
        'use_selection': False, 'export_apply': True,
        'export_lights': False, 'export_cameras': False,
    }
    rna = bpy.ops.export_scene.gltf.get_rna_type()
    legacy = {}
    if 'export_colors' in rna.properties:
        legacy['export_colors'] = True
    if 'export_normals' in rna.properties:
        legacy['export_normals'] = True
    try:
        result = bpy.ops.export_scene.gltf(**base, **legacy)
        print(f"[build_kwik_stop] export result: {result}")
    except Exception as e:
        print(f"[build_kwik_stop] ✗ EXPORT FAILED: {e}")
        import traceback
        traceback.print_exc()
        raise
    if os.path.exists(out_path):
        size = os.path.getsize(out_path)
        print(f"[build_kwik_stop] ✓ wrote {out_path} ({size} bytes)")


def main():
    clear_scene()
    build_shell()
    build_counter()
    build_coffee_station()
    build_beer_cooler()
    build_snack_aisles()
    build_magazine_rack()
    build_floor_props()
    export_glb()


if __name__ == "__main__":
    main()
