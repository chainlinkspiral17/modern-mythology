"""
build_kwik_stop.py · v2
══════════════════════════════════════════════════════════════════
VOL 6 · The Kwik Stop interior · Sam Miller's register.

Second-pass build. Tighter footprint (12m × 9m, was 14 × 11) so
the room reads intimate rather than warehouse-y. Counter relocated
to EAST wall facing the camera (matches the canon vantage looking
in from the south door). Layered prop density per the reference
art the user provided and the canonical motifs from
lore/_VOL6_WIKI.md:

  · Outdoor thermometer mounted high on the south wall, visible
    through the front window — the 97°F Texas-summer cue
  · "Harmony Creek Estates" navy-blue banner above the back
    cooler — NexCorp's brand spillover into the corner store
  · Wall of paper notices above the counter (employment, lottery
    odds, security camera, "we card under 30", $1.29 tallboys,
    no loitering, hand-drawn shift schedule, food-stamp accept)
  · Stack of newspapers bound with twine in the foreground centre
    (Sam's responsibility to put out / pull at end of week)
  · Ceiling tiles with water stains (3-4 darker patches)
  · Mounted wall thermometer + clock near coffee station
  · Wire basket on counter with: receipt, keyring, child's
    drawing (folded paper), single glove, sunglasses, gum packet
  · Slanted magazine rack near front window
  · Floor mat in cursive WELCOME at the entry
  · Mop + bucket in the corner near the back room door
  · ATM, trash bin near south door
  · Single back-cooler with the "infinite recursion" canon (a
    second mirror surface behind it that catches its own
    reflection — implemented as a tinted glass behind the
    cooler's back panel)

Footprint:
  Interior X ∈ [-6, +6], Y ∈ [0, +9], ceiling Z=3.0
  Door at south centre (X ∈ [-1.5, +1.5])
  Counter on east wall (X = +5.0, Y ∈ [3, 7])
  Beer cooler row across north wall (Y = +8.5)
  Two snack aisles running E-W in middle (Y = 3.5, Y = 5.5)
  Coffee + slurpee station on west wall (X = -5.5, Y ∈ [3, 6])

Run:
    blender --background --python build_kwik_stop.py

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
# Per the reference: warm sunset light + tan linoleum + cream
# walls + navy-blue brand banner + warm food-case glow. Saturated
# enough to read on the post-processed render but not gaudy.
COL_FLOOR_VINYL     = (0.84, 0.78, 0.66, 1.0)
COL_FLOOR_SEAM      = (0.62, 0.55, 0.44, 1.0)
COL_FLOOR_SCUFF     = (0.46, 0.40, 0.32, 1.0)
COL_WALL_CREAM      = (0.92, 0.86, 0.74, 1.0)
COL_WALL_BASEBOARD  = (0.62, 0.52, 0.40, 1.0)
COL_CEILING_TILE    = (0.94, 0.92, 0.84, 1.0)
COL_CEILING_GRID    = (0.58, 0.54, 0.46, 1.0)
COL_CEILING_STAIN   = (0.72, 0.62, 0.42, 1.0)
COL_GLASS           = (0.78, 0.84, 0.86, 0.45)
COL_GLASS_WARM      = (0.96, 0.84, 0.62, 0.70)   # sunset-through-window
COL_METAL_STEEL     = (0.66, 0.68, 0.70, 1.0)
COL_METAL_BLACK     = (0.18, 0.16, 0.14, 1.0)
COL_BRAND_NAVY      = (0.18, 0.32, 0.50, 1.0)    # Harmony Creek Estates banner
COL_BRAND_NAVY_TXT  = (0.86, 0.84, 0.74, 1.0)    # the lettering
COL_BRAND_RED       = (0.78, 0.18, 0.16, 1.0)    # KWIK STOP signage
COL_COUNTER_FORMICA = (0.74, 0.64, 0.42, 1.0)
COL_COUNTER_DARK    = (0.30, 0.22, 0.14, 1.0)
COL_COUNTER_TOP     = (0.18, 0.14, 0.12, 1.0)
COL_PAPER           = (0.96, 0.92, 0.82, 1.0)
COL_PAPER_AGED      = (0.86, 0.78, 0.62, 1.0)
COL_NEWSPRINT       = (0.78, 0.74, 0.66, 1.0)
COL_TWINE           = (0.62, 0.46, 0.30, 1.0)
COL_RUBBER_MAT      = (0.22, 0.20, 0.20, 1.0)
COL_RUBBER_MAT_TXT  = (0.42, 0.40, 0.38, 1.0)

# Cool back-cooler interior tones
COL_COOLER_GLASS    = (0.42, 0.66, 0.84, 0.55)
COL_COOLER_INTERIOR = (0.08, 0.16, 0.26, 1.0)

# Brand colours for chip bags / soda cans / beer six-packs.
# Picked to read as a candy-aisle without going clown-y.
SNACK_TINTS = [
    (0.92, 0.32, 0.20, 1.0),   # cool red (chips)
    (0.18, 0.58, 0.86, 1.0),   # blue (corn chips)
    (0.96, 0.84, 0.30, 1.0),   # yellow (cheese pull)
    (0.30, 0.72, 0.42, 1.0),   # green (sour)
    (0.92, 0.50, 0.22, 1.0),   # orange (BBQ)
    (0.62, 0.32, 0.74, 1.0),   # purple (sweet)
    (0.86, 0.86, 0.86, 1.0),   # silver (light / diet)
    (0.32, 0.22, 0.16, 1.0),   # brown (jerky / coffee)
    (0.96, 0.62, 0.78, 1.0),   # pink (candy)
]


# ── Geometry helpers (vendored) ──────────────────────────────────
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


CEIL_Z   = 3.00
WALL_THICK = 0.20


# ════════════════════════════════════════════════════════════════
# SHELL — floor, walls, ceiling, windows, doors
# ════════════════════════════════════════════════════════════════
def build_shell():
    # ── Floor ────────────────────────────────────────────────────
    make_box("Floor", (0.0, 4.5, -0.05),
             (12.4, 9.4, 0.10), COL_FLOOR_VINYL)
    # Plank-style floor seams (running N-S)
    for i in range(-5, 6):
        make_box(f"Floor_SeamX_{i}", (i*1.0, 4.5, 0.005),
                 (0.02, 9.4, 0.001), COL_FLOOR_SEAM)
    # Scuff marks in high-traffic areas (entry + counter side)
    for i, (sx, sy) in enumerate([
        (0.0, 0.8), (-0.4, 1.2), (+0.4, 1.4),
        (+3.6, 4.0), (+3.8, 4.6), (+3.5, 5.2),
        (-3.6, 4.0), (-2.0, 5.0), (-1.0, 6.5),
    ]):
        make_box(f"Floor_Scuff_{i}", (sx, sy, 0.008),
                 (0.30, 0.20, 0.001), COL_FLOOR_SCUFF)

    # ── Walls ────────────────────────────────────────────────────
    # West + East walls
    for sgn, xpos in [(-1, -6.0), (+1, +6.0)]:
        make_box(f"Wall_X{sgn:+d}", (xpos, 4.5, CEIL_Z/2.0),
                 (WALL_THICK, 9.4, CEIL_Z), COL_WALL_CREAM)
        # Baseboard run
        make_box(f"Wall_X{sgn:+d}_Base", (xpos - sgn*0.06, 4.5, 0.08),
                 (0.06, 9.4, 0.16), COL_WALL_BASEBOARD)
    # North wall (back, beer cooler runs along it)
    make_box("Wall_N", (0.0, 9.0, CEIL_Z/2.0),
             (12.4, WALL_THICK, CEIL_Z), COL_WALL_CREAM)
    make_box("Wall_N_Base", (0.0, 9.0 - 0.06, 0.08),
             (12.4, 0.06, 0.16), COL_WALL_BASEBOARD)
    # South wall — door at centre, brand-red panel either side
    make_box("Wall_S_W", (-3.75, 0.0, CEIL_Z/2.0),
             (4.50, WALL_THICK, CEIL_Z), COL_BRAND_RED)
    make_box("Wall_S_E", (+3.75, 0.0, CEIL_Z/2.0),
             (4.50, WALL_THICK, CEIL_Z), COL_BRAND_RED)
    make_box("Wall_S_AboveDoor", (0.0, 0.0, CEIL_Z - 0.30),
             (3.20, WALL_THICK, 0.60), COL_BRAND_RED)

    # KWIK STOP sign on the south brand panel (interior side)
    make_box("Brand_Sign_BG", (0.0, 0.02, 2.50),
             (3.20, 0.02, 0.40), (0.96, 0.94, 0.86, 1.0))
    # K W I K (block letters as 4 small boxes)
    for i, letter_offset in enumerate([-1.20, -0.80, -0.40, 0.0]):
        make_box(f"Brand_KWIK_{i}", (letter_offset, 0.03, 2.50),
                 (0.28, 0.005, 0.24), COL_BRAND_RED)
    # S T O P
    for i, letter_offset in enumerate([0.45, 0.85, 1.25, 1.65]):
        if letter_offset > 1.50:  # last letter clipped by panel edge
            continue
        make_box(f"Brand_STOP_{i}", (letter_offset, 0.03, 2.50),
                 (0.28, 0.005, 0.24), COL_BRAND_RED)

    # ── Glass double doors ──────────────────────────────────────
    make_box("Door_Frame_T", (0.0, 0.0, 2.10), (3.20, 0.10, 0.08),
             COL_METAL_STEEL)
    make_box("Door_Frame_B", (0.0, 0.0, 0.06), (3.20, 0.10, 0.08),
             COL_METAL_STEEL)
    make_box("Door_Frame_DivMid", (0.0, 0.0, 1.05),
             (0.06, 0.10, 2.00), COL_METAL_STEEL)
    make_box("Door_Glass_L", (-0.80, 0.0, 1.05),
             (1.40, 0.04, 2.00), COL_GLASS)
    make_box("Door_Glass_R", (+0.80, 0.0, 1.05),
             (1.40, 0.04, 2.00), COL_GLASS)
    for sx in (-1, +1):
        make_cyl(f"Door_Handle_{sx}", (sx * 0.20, -0.05, 1.10),
                 0.018, 0.30, COL_METAL_BLACK, segments=8, axis='Y')

    # ── Picture windows flanking the doors ──────────────────────
    # Larger windows than v1 — these are the visual openings to
    # the parking lot + NexCorp across the intersection. Warm
    # sunset-through-glass colour.
    for sgn, cx in [(-1, -3.50), (+1, +3.50)]:
        # Glass
        make_box(f"Window_S_{sgn:+d}_Glass", (cx, -0.02, 1.55),
                 (2.40, 0.04, 1.40), COL_GLASS_WARM)
        # Frame T + B
        make_box(f"Window_S_{sgn:+d}_Frame_T", (cx, -0.04, 2.30),
                 (2.50, 0.06, 0.10), COL_METAL_STEEL)
        make_box(f"Window_S_{sgn:+d}_Frame_B", (cx, -0.04, 0.80),
                 (2.50, 0.06, 0.10), COL_METAL_STEEL)
        # Mullion in middle (vertical)
        make_box(f"Window_S_{sgn:+d}_Mull", (cx, -0.06, 1.55),
                 (0.05, 0.05, 1.40), COL_METAL_STEEL)

    # ── Outdoor thermometer (canon — Texas heat cue) ────────────
    # Mounted west side of left window, visible from inside
    # through the glass. Shows ~97°F red column.
    therm_x, therm_y = -5.20, -0.10
    make_box("Therm_BG", (therm_x, therm_y, 1.70),
             (0.30, 0.02, 0.90), COL_PAPER_AGED)
    # Tube
    make_cyl("Therm_Tube", (therm_x, therm_y - 0.02, 1.70),
             0.02, 0.80, COL_GLASS, segments=8, axis='Z')
    # Mercury column (mostly full — 97 degrees)
    make_cyl("Therm_Mercury", (therm_x, therm_y - 0.03, 1.55),
             0.012, 0.55, COL_BRAND_RED, segments=8, axis='Z')
    # Bulb at bottom
    make_cyl("Therm_Bulb", (therm_x, therm_y - 0.03, 1.30),
             0.030, 0.04, COL_BRAND_RED, segments=10, axis='Z')
    # Scale (just a few darker tick marks for read)
    for tick_i in range(5):
        make_box(f"Therm_Tick_{tick_i}",
                 (therm_x + 0.06, therm_y - 0.03, 1.40 + tick_i * 0.15),
                 (0.06, 0.005, 0.012), COL_METAL_BLACK)

    # ── Ceiling ─────────────────────────────────────────────────
    make_box("Ceiling", (0.0, 4.5, CEIL_Z + 0.05),
             (12.4, 9.4, 0.10), COL_CEILING_TILE)
    # Tile grid divider strips
    for i in range(-5, 6):
        make_box(f"Ceiling_GridX_{i}", (i*1.0, 4.5, CEIL_Z + 0.02),
                 (0.04, 9.4, 0.005), COL_CEILING_GRID)
    for j in range(0, 10):
        make_box(f"Ceiling_GridY_{j}", (0.0, float(j), CEIL_Z + 0.02),
                 (12.4, 0.04, 0.005), COL_CEILING_GRID)
    # Water stains on ceiling tiles — canonical convenience-store
    # detail. Three darker patches at specific tile centres.
    for stain_i, (sx, sy) in enumerate([
        (-2.0, 2.5), (+1.0, 5.5), (+3.0, 7.5),
    ]):
        make_box(f"Ceiling_Stain_{stain_i}",
                 (sx, sy, CEIL_Z + 0.025),
                 (0.80, 0.80, 0.003), COL_CEILING_STAIN)

    # ── Fluorescent tube fixtures (3 rows of 2 each) ────────────
    for j, ypos in enumerate([2.5, 5.0, 7.5]):
        for i in range(-1, 2):
            xp = i * 2.4
            make_box(f"FluorTube_{j}_{i}",
                     (xp, ypos, CEIL_Z - 0.08),
                     (1.6, 0.36, 0.06), (0.96, 0.96, 0.92, 1.0))
            # Diffuser frame
            make_box(f"FluorFrame_{j}_{i}",
                     (xp, ypos, CEIL_Z - 0.10),
                     (1.70, 0.44, 0.02), COL_METAL_STEEL)


# ════════════════════════════════════════════════════════════════
# COUNTER — east wall, facing west (toward customer)
# Sam's post.
# ════════════════════════════════════════════════════════════════
def build_counter():
    cx, cy = 5.0, 4.5
    # L-shape: long run N-S along east wall + short return at south
    # Front counter (customer-facing — west face)
    make_box("Counter_Front",
             (cx, cy, 0.50),
             (1.00, 4.40, 1.00), COL_COUNTER_FORMICA)
    # Counter top (dark laminate)
    make_box("Counter_Top",
             (cx, cy, 1.04),
             (1.10, 4.50, 0.06), COL_COUNTER_TOP)
    # Front kick panel (darker base)
    make_box("Counter_Kick",
             (cx - 0.51, cy, 0.10),
             (0.02, 4.40, 0.20), COL_COUNTER_DARK)

    # ── Register on counter top, southern half ──────────────────
    make_box("Register_Body",
             (cx, cy - 1.20, 1.25),
             (0.42, 0.40, 0.32), (0.22, 0.20, 0.22, 1.0))
    make_box("Register_Display",
             (cx - 0.22, cy - 1.20, 1.42),
             (0.04, 0.34, 0.14), (0.10, 0.32, 0.16, 1.0))
    make_box("Register_Keypad",
             (cx, cy - 1.20, 1.10),
             (0.36, 0.36, 0.02), (0.32, 0.32, 0.34, 1.0))
    make_box("Register_Drawer",
             (cx, cy - 1.20, 0.94),
             (0.50, 0.40, 0.10), (0.22, 0.20, 0.22, 1.0))

    # ── Hot food case beside register (Hot Pockets canon) ───────
    hcx, hcy = cx, cy - 0.10
    make_box("HotCase_Body", (hcx, hcy, 1.30),
             (0.50, 0.70, 0.60), (0.94, 0.92, 0.84, 1.0))
    make_box("HotCase_Glass", (hcx - 0.22, hcy, 1.30),
             (0.04, 0.70, 0.58), COL_GLASS)
    # Warm lamp inside (amber glow visible through glass)
    make_box("HotCase_Lamp", (hcx, hcy, 1.55),
             (0.50, 0.70, 0.04), (1.0, 0.78, 0.32, 1.0))
    # Hot Pockets visible (3 of them at different angles)
    for i in range(3):
        hp_y = hcy - 0.24 + i * 0.24
        make_box(f"HotPocket_{i}", (hcx - 0.08, hp_y, 1.18),
                 (0.20, 0.14, 0.08), (0.78, 0.58, 0.40, 1.0))
    # Taquito roller (canon convenience-store fixture)
    for i in range(2):
        make_cyl(f"TaquitoRoller_{i}",
                 (hcx + 0.05, hcy + 0.20 - i * 0.10, 1.42),
                 0.04, 0.50, (0.42, 0.32, 0.20, 1.0), segments=8, axis='X')

    # ── Wire basket on counter (left-behind objects) ────────────
    # The canon motif. Small steel basket with miscellaneous items
    # — a receipt, keys, a folded child's drawing, a single glove,
    # sunglasses, gum.
    wbx, wby = cx, cy + 1.30
    make_cyl("WireBasket_Body", (wbx, wby, 1.12),
             0.18, 0.10, (0.42, 0.40, 0.38, 1.0), segments=12)
    # Receipt sticking out (white paper rectangle)
    make_box("WB_Receipt", (wbx - 0.04, wby - 0.05, 1.18),
             (0.10, 0.06, 0.004), COL_PAPER)
    # Keyring (small metal ring with keys)
    make_cyl("WB_Keyring", (wbx + 0.04, wby - 0.02, 1.19),
             0.025, 0.005, COL_METAL_STEEL, segments=8, axis='Y')
    make_box("WB_Key1", (wbx + 0.04, wby - 0.04, 1.16),
             (0.020, 0.010, 0.06), COL_METAL_STEEL)
    make_box("WB_Key2", (wbx + 0.06, wby - 0.04, 1.16),
             (0.020, 0.010, 0.06), (0.62, 0.46, 0.22, 1.0))
    # Folded child's drawing (small folded paper)
    make_box("WB_Drawing", (wbx - 0.08, wby + 0.03, 1.16),
             (0.06, 0.08, 0.012), COL_PAPER_AGED)
    # Single glove (left, brown wool)
    make_box("WB_Glove", (wbx + 0.07, wby + 0.06, 1.16),
             (0.08, 0.04, 0.06), (0.42, 0.28, 0.18, 1.0))
    # Sunglasses (folded, sticking out)
    make_box("WB_Sunglasses", (wbx - 0.06, wby + 0.08, 1.17),
             (0.08, 0.05, 0.015), COL_METAL_BLACK)
    # Pack of gum (foil)
    make_box("WB_Gum", (wbx + 0.10, wby - 0.05, 1.16),
             (0.04, 0.06, 0.015), (0.86, 0.86, 0.86, 1.0))

    # ── Lottery scratch-off rack (vertical pegboard) ────────────
    lcx, lcy = cx - 0.12, cy + 0.80
    make_box("Lottery_Rack", (lcx, lcy, 1.30),
             (0.06, 0.50, 0.34), COL_METAL_BLACK)
    for i in range(6):
        col = SNACK_TINTS[i % len(SNACK_TINTS)]
        lx_off = (i % 3) * 0.16 - 0.16
        lz_off = (i // 3) * 0.16
        make_box(f"Lottery_Ticket_{i}",
                 (lcx - 0.04, lcy + lx_off, 1.24 + lz_off),
                 (0.04, 0.14, 0.14), col)

    # ── Stool on the server side ────────────────────────────────
    stx, sty = cx + 0.30, cy
    make_cyl("Stool_Seat", (stx, sty, 0.66),
             0.16, 0.04, (0.32, 0.42, 0.62, 1.0), segments=10)
    make_cyl("Stool_Post", (stx, sty, 0.36),
             0.028, 0.56, COL_METAL_BLACK)
    make_cyl("Stool_Base", (stx, sty, 0.04),
             0.20, 0.04, COL_METAL_BLACK, segments=10)

    # ── Paper notices wall (above counter on east wall) ─────────
    # Canon: a wall of taped-up paper signs above the register.
    # Employment notices, lottery odds, security camera warning,
    # we card under 30, $1.29 tallboys, no loitering, shift sched,
    # food stamps accepted.
    base_y = cy - 1.4
    notices_data = [
        # (dy_offset, dz_offset, width, height, tint)
        (-1.4, 2.00, 0.28, 0.36, COL_PAPER),         # employment
        (-1.0, 2.00, 0.30, 0.40, COL_PAPER),         # lottery odds
        (-0.6, 2.00, 0.18, 0.20, COL_PAPER_AGED),    # we card
        (-0.2, 2.00, 0.22, 0.28, (0.96, 0.96, 0.62, 1.0)),  # tallboys yellow
        (+0.2, 2.00, 0.16, 0.22, COL_PAPER_AGED),    # no loitering
        (+0.6, 2.00, 0.20, 0.26, (0.86, 0.46, 0.22, 1.0)),  # security cam orange
        (+1.0, 2.00, 0.30, 0.42, COL_PAPER),         # shift schedule
        (+1.4, 2.00, 0.24, 0.30, COL_PAPER),         # food stamps
        # Lower row
        (-1.0, 1.60, 0.22, 0.18, COL_PAPER_AGED),
        (+0.0, 1.60, 0.18, 0.16, COL_PAPER),
        (+0.8, 1.60, 0.20, 0.20, (0.92, 0.74, 0.42, 1.0)),
    ]
    for i, (dy, dz, w, h, tint) in enumerate(notices_data):
        make_box(f"Notice_{i}_Bg",
                 (cx + 0.40, base_y + dy + 1.4, dz),
                 (0.02, w, h), tint)
        # Tiny dark print band (the actual text, abstracted)
        make_box(f"Notice_{i}_Print",
                 (cx + 0.40 - 0.005, base_y + dy + 1.4, dz - 0.04),
                 (0.001, w * 0.7, h * 0.45), COL_METAL_BLACK)
        # Tape strips at corners (just a couple)
        make_box(f"Notice_{i}_TapeTop",
                 (cx + 0.40 - 0.001, base_y + dy + 1.4, dz + h * 0.5 - 0.01),
                 (0.001, 0.06, 0.02), (0.86, 0.84, 0.78, 0.7))

    # ── Receipt paper / printer at register edge ────────────────
    make_box("Receipt_Printer",
             (cx, cy - 1.50, 1.18),
             (0.20, 0.16, 0.10), (0.30, 0.30, 0.32, 1.0))
    # Receipt curl
    make_box("Receipt_Curl",
             (cx - 0.04, cy - 1.50, 1.10),
             (0.08, 0.04, 0.16), COL_PAPER)

    # ── Cigarette / tobacco rack behind counter (on east wall) ──
    # Lower priority — render as a back-mounted set of small boxes
    cig_x = cx + 0.45
    for sh in range(3):
        shz = 1.40 + sh * 0.32
        make_box(f"CigShelf_{sh}",
                 (cig_x, cy, shz),
                 (0.02, 3.20, 0.04), COL_METAL_STEEL)
        for c in range(12):
            cy_pos = cy - 1.50 + c * 0.28
            tint = SNACK_TINTS[(sh + c) % len(SNACK_TINTS)]
            make_box(f"CigBox_{sh}_{c}",
                     (cig_x + 0.04, cy_pos, shz + 0.10),
                     (0.06, 0.18, 0.16), tint)


# ════════════════════════════════════════════════════════════════
# HARMONY CREEK ESTATES banner (back wall, above coolers)
# NexCorp brand-spill into the corner store. Canonical vol6 motif.
# ════════════════════════════════════════════════════════════════
def build_harmony_banner():
    # Banner panel mounted high on north wall, centred above cooler row
    bcy = 8.89  # just in front of N wall (Y=9)
    bcz = 2.55  # high above coolers (which top at ~2.40)
    # Navy-blue mounting panel
    make_box("Banner_BG", (0.0, bcy, bcz),
             (4.80, 0.02, 0.42), COL_BRAND_NAVY)
    # White frame line around the panel
    for sgn_x in (-1, +1):
        make_box(f"Banner_Frame_X{sgn_x:+d}",
                 (sgn_x * 2.41, bcy - 0.005, bcz),
                 (0.02, 0.02, 0.42), COL_BRAND_NAVY_TXT)
    for sgn_z in (-1, +1):
        make_box(f"Banner_Frame_Z{sgn_z:+d}",
                 (0.0, bcy - 0.005, bcz + sgn_z * 0.21),
                 (4.80, 0.02, 0.02), COL_BRAND_NAVY_TXT)
    # "Harmony Creek Estates" lettering (abstracted as a thick stripe
    # of cream / off-white horizontal text band)
    make_box("Banner_LetterBand", (0.0, bcy - 0.012, bcz),
             (4.40, 0.005, 0.18), COL_BRAND_NAVY_TXT)
    # Tagline below the main letters (smaller)
    make_box("Banner_Tagline", (0.0, bcy - 0.014, bcz - 0.14),
             (3.20, 0.005, 0.06), (0.62, 0.58, 0.48, 1.0))


# ════════════════════════════════════════════════════════════════
# BEER COOLER row (north wall, 4 glass doors)
# Plus the "infinite recursion" canon — a tinted glass behind the
# back panel that catches the cooler's own reflection.
# ════════════════════════════════════════════════════════════════
def build_beer_cooler():
    cy = 8.50
    # 4 cooler doors evenly spaced
    door_centres = [-2.40, -0.80, +0.80, +2.40]
    for i, cx in enumerate(door_centres):
        # Interior box (recessed into the wall area)
        make_box(f"Cooler_{i}_Interior",
                 (cx, cy + 0.30, 1.30),
                 (1.30, 0.40, 2.20), COL_COOLER_INTERIOR)
        # The "infinite recursion" inner mirror — placed at the
        # back of the interior with a slight tint shift
        make_box(f"Cooler_{i}_BackMirror",
                 (cx, cy + 0.485, 1.30),
                 (1.20, 0.005, 2.10), (0.18, 0.30, 0.42, 0.85))
        # Glass door (front)
        make_box(f"Cooler_{i}_Glass",
                 (cx, cy + 0.06, 1.30),
                 (1.24, 0.04, 2.10), COL_COOLER_GLASS)
        # Door frame
        for sgn, sz in [(-1, 'L'), (+1, 'R')]:
            make_box(f"Cooler_{i}_Frame_{sz}",
                     (cx + sgn * 0.62, cy + 0.04, 1.30),
                     (0.04, 0.08, 2.10), COL_METAL_STEEL)
        make_box(f"Cooler_{i}_Frame_T",
                 (cx, cy + 0.04, 2.36),
                 (1.30, 0.08, 0.04), COL_METAL_STEEL)
        make_box(f"Cooler_{i}_Frame_B",
                 (cx, cy + 0.04, 0.24),
                 (1.30, 0.08, 0.04), COL_METAL_STEEL)
        # Handle
        make_box(f"Cooler_{i}_Handle",
                 (cx + 0.60, cy + 0.02, 1.30),
                 (0.02, 0.06, 0.60), COL_METAL_BLACK)
        # Shelves of beer six-packs visible through the glass
        for sh in range(5):
            shz = 0.40 + sh * 0.42
            make_box(f"Cooler_{i}_Shelf_{sh}",
                     (cx, cy + 0.30, shz),
                     (1.20, 0.30, 0.02), COL_METAL_STEEL)
            for b in range(5):
                bx = cx - 0.48 + b * 0.24
                tint = SNACK_TINTS[(i + sh + b) % len(SNACK_TINTS)]
                make_box(f"Cooler_{i}_Sixpack_{sh}_{b}",
                         (bx, cy + 0.30, shz + 0.20),
                         (0.20, 0.22, 0.30), tint)

    # ── Price tag strip across the top of all coolers ───────────
    for i, cx in enumerate(door_centres):
        make_box(f"Cooler_PriceTag_{i}",
                 (cx, cy + 0.03, 2.18),
                 (0.36, 0.005, 0.10), COL_PAPER)


# ════════════════════════════════════════════════════════════════
# COFFEE + SLURPEE station (west wall)
# ════════════════════════════════════════════════════════════════
def build_coffee_station():
    cx = -5.30
    cy = 4.50
    # Counter run along W wall, narrower than v1
    make_box("Coffee_Counter",
             (cx, cy, 0.86),
             (1.20, 3.20, 0.04), COL_COUNTER_FORMICA)
    make_box("Coffee_Base",
             (cx, cy, 0.42),
             (1.20, 3.20, 0.84), COL_COUNTER_DARK)
    # Backsplash
    make_box("Coffee_Backsplash",
             (cx - 0.55, cy, 1.40),
             (0.04, 3.20, 1.00), (0.86, 0.84, 0.78, 1.0))

    # ── 3 coffee pots (dark / medium / decaf) ───────────────────
    for i, tint in enumerate([
            (0.18, 0.10, 0.06, 1.0),
            (0.32, 0.18, 0.10, 1.0),
            (0.42, 0.32, 0.20, 1.0)]):
        py = cy - 1.20 + i * 0.50
        # Pot
        make_cyl(f"Coffee_Pot_{i}_Body",
                 (cx + 0.05, py, 1.10),
                 0.08, 0.26, COL_GLASS, segments=8)
        make_cyl(f"Coffee_Pot_{i}_Liquid",
                 (cx + 0.05, py, 1.04),
                 0.068, 0.16, tint, segments=8)
        make_cyl(f"Coffee_Pot_{i}_Burner",
                 (cx + 0.05, py, 0.91),
                 0.10, 0.02, COL_METAL_BLACK, segments=10)
        # Handle (small protrusion)
        make_box(f"Coffee_Pot_{i}_Handle",
                 (cx + 0.16, py, 1.10),
                 (0.06, 0.04, 0.10), COL_METAL_BLACK)
        # Label / brand panel above (matching dark/med/decaf labels)
        label_tint = [(0.32, 0.20, 0.10, 1.0),
                       (0.62, 0.42, 0.20, 1.0),
                       (0.96, 0.96, 0.86, 1.0)][i]
        make_box(f"Coffee_Pot_{i}_Label",
                 (cx + 0.05, py, 1.42),
                 (0.20, 0.18, 0.10), label_tint)

    # ── Slurpee twin barrels ────────────────────────────────────
    for i, tint in enumerate([
            (0.62, 0.20, 0.78, 1.0),   # blue raspberry
            (0.92, 0.30, 0.18, 1.0)]):  # cherry
        sy = cy + 0.80 + i * 0.50
        make_cyl(f"Slurpee_{i}_Barrel",
                 (cx + 0.05, sy, 1.32),
                 0.14, 0.44, tint, segments=10)
        make_cyl(f"Slurpee_{i}_TopCap",
                 (cx + 0.05, sy, 1.58),
                 0.16, 0.10, COL_METAL_STEEL, segments=10)
        make_cyl(f"Slurpee_{i}_Spout",
                 (cx + 0.05, sy - 0.14, 1.16),
                 0.020, 0.10, COL_METAL_BLACK, segments=6, axis='Z')
        # Drip tray below
        make_box(f"Slurpee_{i}_Tray",
                 (cx + 0.10, sy - 0.20, 0.95),
                 (0.20, 0.30, 0.04), COL_METAL_STEEL)

    # ── Cup stack (next to coffee pots) ─────────────────────────
    for i in range(8):
        make_cyl(f"Coffee_Cup_{i}",
                 (cx + 0.30, cy - 1.45, 0.90 + i * 0.04),
                 0.04, 0.04, (0.92, 0.86, 0.74, 1.0), segments=10)

    # ── Lid dispenser ───────────────────────────────────────────
    make_cyl("Coffee_LidDispenser",
             (cx + 0.30, cy - 0.85, 0.92),
             0.07, 0.18, COL_METAL_STEEL, segments=8)

    # ── Cream + sugar caddy ─────────────────────────────────────
    make_box("Coffee_CSC_Body",
             (cx + 0.30, cy + 1.40, 0.92),
             (0.36, 0.40, 0.16), (0.78, 0.68, 0.52, 1.0))
    for i in range(3):
        col = [(0.94, 0.94, 0.94, 1.0),
               (0.32, 0.22, 0.16, 1.0),
               (0.78, 0.74, 0.60, 1.0)][i]
        make_box(f"Coffee_CSC_{i}",
                 (cx + 0.30, cy + 1.30 + i * 0.10, 1.04),
                 (0.10, 0.08, 0.06), col)

    # ── Squeegee + bucket near the coffee station ──────────────
    make_cyl("Mop_Bucket",
             (cx + 0.60, cy + 1.80, 0.20),
             0.18, 0.40, (0.92, 0.86, 0.36, 1.0), segments=10)
    make_box("Mop_Wringer",
             (cx + 0.60, cy + 1.80, 0.42),
             (0.30, 0.30, 0.06), COL_METAL_BLACK)
    # Squeegee handle
    make_cyl("Squeegee_Handle",
             (cx + 0.60, cy + 1.80, 1.20),
             0.020, 1.60, (0.62, 0.32, 0.20, 1.0), segments=8)
    make_box("Squeegee_Head",
             (cx + 0.60, cy + 1.80, 0.42),
             (0.08, 0.30, 0.06), (0.18, 0.18, 0.20, 1.0))


# ════════════════════════════════════════════════════════════════
# SNACK AISLES — two free-standing rows + end caps
# ════════════════════════════════════════════════════════════════
def build_snack_aisles():
    # Two aisles E-W, at Y=3.5 and Y=5.5. Narrower than v1, with
    # end-caps that lean forward (slanted feel from the reference).
    for j, ay in enumerate([3.5, 5.5]):
        # Base support
        make_box(f"Aisle_{j}_Base", (0.0, ay, 0.10),
                 (6.0, 0.70, 0.20), COL_COUNTER_DARK)
        # 5 product shelves
        for sh in range(5):
            shz = 0.34 + sh * 0.40
            for sy_sgn in (-1, +1):
                # Shelf plank
                make_box(f"Aisle_{j}_Shelf_{sh}_y{sy_sgn:+d}",
                         (0.0, ay + sy_sgn * 0.32, shz),
                         (6.0, 0.04, 0.32), COL_METAL_STEEL)
                # Price-tag strip
                make_box(f"Aisle_{j}_PriceTag_{sh}_y{sy_sgn:+d}",
                         (0.0, ay + sy_sgn * 0.32, shz - 0.10),
                         (6.0, 0.001, 0.04), COL_PAPER)
                # Products — vary height for visual interest
                for p in range(12):
                    px = -2.75 + p * 0.50
                    tint = SNACK_TINTS[(j * 11 + sh * 3 + p) % len(SNACK_TINTS)]
                    # Vary heights: tall bottles, short bags, etc.
                    base_h = [0.18, 0.22, 0.26, 0.30, 0.16, 0.20][(j + sh + p) % 6]
                    make_box(f"Aisle_{j}_Snack_{sh}_y{sy_sgn:+d}_{p}",
                             (px, ay + sy_sgn * 0.26, shz + base_h / 2.0 + 0.02),
                             (0.20, 0.20, base_h), tint)
        # Top aisle-label sign (CHIPS / SNACKS / etc.)
        # Two different brand-coloured labels per aisle, hung from
        # the ceiling structure (NS faces)
        label_text_tint = COL_PAPER
        label_y_offsets = [-0.34, +0.34]
        labels = [("CHIPS", "SNACKS"), ("CANDY", "JERKY")][j]
        for k, (lbl_y_off, lbl_text) in enumerate(zip(label_y_offsets, labels)):
            make_box(f"Aisle_{j}_TopSign_BG_{k}",
                     (0.0, ay + lbl_y_off, 2.50),
                     (5.6, 0.06, 0.24), COL_BRAND_RED)
            # Letter band (cream)
            make_box(f"Aisle_{j}_TopSign_Text_{k}",
                     (0.0, ay + lbl_y_off + (0.001 if k == 0 else -0.001), 2.50),
                     (4.6, 0.005, 0.12), label_text_tint)

    # ── End-caps (the small slanted stands near windows, per ref) ──
    # Two end-caps placed near the south windows for cross-traffic
    for sgn, sx in [(-1, -3.40), (+1, +3.40)]:
        # Body (slightly angled — we fake angle with a thinner base)
        make_box(f"EndCap_{sgn:+d}_Base",
                 (sx, 1.70, 0.12),
                 (0.60, 0.80, 0.24), COL_COUNTER_DARK)
        # 4 narrow shelves stacked
        for sh in range(4):
            shz = 0.40 + sh * 0.34
            make_box(f"EndCap_{sgn:+d}_Shelf_{sh}",
                     (sx, 1.70, shz),
                     (0.62, 0.70, 0.02), COL_METAL_STEEL)
            # 4 products per shelf (smaller than aisle products)
            for p in range(4):
                px = sx - 0.20 + p * 0.14
                tint = SNACK_TINTS[(sgn + sh + p) % len(SNACK_TINTS)]
                make_box(f"EndCap_{sgn:+d}_Product_{sh}_{p}",
                         (px, 1.70, shz + 0.14),
                         (0.10, 0.50, 0.18), tint)
        # Top header
        make_box(f"EndCap_{sgn:+d}_Header",
                 (sx, 1.70, 1.92),
                 (0.62, 0.78, 0.20), COL_BRAND_RED)


# ════════════════════════════════════════════════════════════════
# NEWSPAPER STACK + MAGAZINE RACK (foreground centre)
# Canon: bound newspapers in the entry zone. Sam's responsibility
# to put them out / pull them at end of week.
# ════════════════════════════════════════════════════════════════
def build_newspaper_stack():
    # Stack of newspapers bound with twine, sitting on the floor
    # in the middle-front of the store
    sx, sy = 0.0, 2.20
    # 12 papers stacked, slight horizontal jitter
    for i in range(12):
        jitter_x = ((i * 31) % 7 - 3) * 0.012
        jitter_y = ((i * 17) % 5 - 2) * 0.012
        # Alternate slight rotation by varying width
        w = 0.46 + (i % 2) * 0.02
        d = 0.30 + (i % 2) * 0.02
        make_box(f"Newspaper_{i}",
                 (sx + jitter_x, sy + jitter_y, 0.06 + i * 0.012),
                 (w, d, 0.012),
                 COL_NEWSPRINT if (i % 3 != 0) else COL_PAPER_AGED)
    # Twine wrap (two crossing strips — N-S and E-W)
    stack_top_z = 0.06 + 12 * 0.012 + 0.001
    make_box("Twine_NS",
             (sx, sy, stack_top_z * 0.5),
             (0.02, 0.30, stack_top_z), COL_TWINE)
    make_box("Twine_EW",
             (sx, sy, stack_top_z * 0.5),
             (0.46, 0.02, stack_top_z), COL_TWINE)
    # Twine knot at top
    make_cyl("Twine_Knot",
             (sx, sy, stack_top_z + 0.01),
             0.018, 0.02, COL_TWINE, segments=6, axis='Z')


def build_magazine_rack():
    # Slanted magazine rack against the west wall, near windows
    mrx, mry = -5.30, 1.80
    # Body
    make_box("MagRack_Body", (mrx, mry, 0.92),
             (0.36, 1.10, 1.84), COL_METAL_BLACK)
    # 5 slanted shelves with magazines
    for i in range(5):
        sy = mry - 0.46 + i * 0.24
        # Shelf
        make_box(f"MagRack_Shelf_{i}",
                 (mrx, sy, 0.46 + i * 0.24),
                 (0.36, 0.24, 0.02), COL_METAL_STEEL)
        # Magazines (slanted so we see the cover)
        for m in range(2):
            mx = mrx + 0.04 - m * 0.04
            col = SNACK_TINTS[(i + m * 2) % len(SNACK_TINTS)]
            make_box(f"MagRack_Mag_{i}_{m}",
                     (mx, sy + 0.02, 0.62 + i * 0.24),
                     (0.10, 0.18, 0.26), col)


# ════════════════════════════════════════════════════════════════
# ATM, TRASH, BACK-ROOM DOOR, FLOOR MAT
# ════════════════════════════════════════════════════════════════
def build_floor_props():
    # ── ATM near south door, east side ──────────────────────────
    atm_x, atm_y = 4.80, 1.00
    make_box("ATM_Body", (atm_x, atm_y, 0.75),
             (0.50, 0.42, 1.50), (0.42, 0.42, 0.46, 1.0))
    make_box("ATM_Screen", (atm_x, atm_y - 0.20, 1.16),
             (0.32, 0.04, 0.22), (0.18, 0.32, 0.46, 1.0))
    make_box("ATM_Keypad", (atm_x, atm_y - 0.20, 0.92),
             (0.22, 0.04, 0.16), (0.22, 0.22, 0.24, 1.0))
    make_box("ATM_Slot", (atm_x, atm_y - 0.22, 0.74),
             (0.20, 0.02, 0.02), COL_METAL_BLACK)
    # Tape line under the ATM (don't stand here)
    make_box("ATM_Line", (atm_x, atm_y + 0.30, 0.012),
             (0.50, 0.04, 0.002), (0.86, 0.86, 0.42, 1.0))

    # ── Trash can ───────────────────────────────────────────────
    make_cyl("Trash_Body", (-4.20, 1.20, 0.42),
             0.20, 0.80, (0.42, 0.30, 0.18, 1.0), segments=10)
    make_cyl("Trash_Rim", (-4.20, 1.20, 0.82),
             0.22, 0.04, COL_METAL_BLACK, segments=10)
    make_box("Trash_Bag", (-4.20, 1.20, 0.58),
             (0.32, 0.32, 0.18), (0.18, 0.18, 0.18, 1.0))

    # ── Floor entry mat (WELCOME) ───────────────────────────────
    make_box("Entry_Mat", (0.0, 0.85, 0.012),
             (3.20, 1.30, 0.02), COL_RUBBER_MAT)
    # WELCOME letter band (lighter rectangle)
    make_box("Entry_Mat_Text", (0.0, 0.85, 0.014),
             (1.80, 0.20, 0.002), COL_RUBBER_MAT_TXT)
    # Mat edge — slightly darker line around the perimeter
    for sgn, ax in [('+X', +1.60), ('-X', -1.60)]:
        make_box(f"Mat_Edge_{ax}", (ax, 0.85, 0.013),
                 (0.04, 1.30, 0.003), COL_METAL_BLACK)
    for sgn, ay in [('-Y', 0.20), ('+Y', 1.50)]:
        make_box(f"Mat_Edge_{ay}", (0.0, ay, 0.013),
                 (3.20, 0.04, 0.003), COL_METAL_BLACK)

    # ── Back-room door (north-east corner) ──────────────────────
    # Stockroom door, behind counter at end of east wall
    bdx, bdy = 5.60, 7.50
    make_box("BackDoor",
             (bdx + 0.30, bdy, 1.05),
             (0.04, 0.90, 2.10), (0.42, 0.30, 0.18, 1.0))
    make_box("BackDoor_Frame",
             (bdx + 0.30, bdy, 2.16),
             (0.04, 0.96, 0.10), COL_COUNTER_DARK)
    # STOCK ROOM sign (small paper above)
    make_box("BackDoor_Sign",
             (bdx + 0.25, bdy, 2.30),
             (0.02, 0.30, 0.10), COL_PAPER)
    # Door handle
    make_box("BackDoor_Knob",
             (bdx + 0.28, bdy + 0.36, 1.05),
             (0.02, 0.04, 0.04), COL_METAL_BLACK)


# ════════════════════════════════════════════════════════════════
# DUST + LIGHT-SHAFT HINTS (low-poly placeholders for particles)
# Actual GPU particles are wired in the .tscn — these geometry
# placeholders mark where the sunlight shaft hits the floor so
# the post-process catches it consistently.
# ════════════════════════════════════════════════════════════════
def build_light_shafts():
    # Slanted bright floor patches under each south window
    for sgn, sx in [(-1, -3.0), (+1, +3.0)]:
        # Bright warm patch on the floor where sunlight hits
        make_box(f"LightShaft_Floor_{sgn:+d}",
                 (sx, 1.40, 0.012),
                 (2.60, 2.00, 0.002), (0.96, 0.82, 0.52, 0.8))


# ════════════════════════════════════════════════════════════════
# POLISH PASS — second-iteration density
# Pushes the build past "primitive boxes" toward the reference
# stylized-convenience-store read. Adds:
#   · Square-tile floor grid (E-W seams to cross the N-S planks)
#   · Yellow caution stripe along counter base
#   · Door decals (HOURS, MC/VISA, ATM, OPEN sign)
#   · Ice machine on west wall
#   · Lottery / scratch-off display behind counter
#   · Newspaper vending rack at entry
#   · KWIK STOP trash can
#   · Strip curtain on stockroom door
#   · Counter impulse-buy: mints, gum, candy bars, Slim Jim jar
#   · Security camera, smoke detector, sprinklers, HVAC vent
#   · Electrical conduit running up west wall to ceiling
#   · Wet-floor cone
#   · Pump canopy silhouette + two pumps + streetlamp + parked
#     car visible through the south windows (the world outside)
# ════════════════════════════════════════════════════════════════
COL_PUMP_BODY     = (0.86, 0.62, 0.30, 1.0)   # warm-sunset orange
COL_PUMP_FACE     = (0.18, 0.18, 0.18, 1.0)
COL_CANOPY        = (0.74, 0.66, 0.54, 1.0)
COL_CANOPY_TRIM   = (0.18, 0.32, 0.50, 1.0)
COL_CAR_BODY      = (0.32, 0.30, 0.36, 1.0)   # silhouetted dark sedan
COL_CAR_WINDOW    = (0.42, 0.50, 0.62, 0.85)
COL_ASPHALT       = (0.16, 0.16, 0.18, 1.0)
COL_STREETLAMP    = (0.42, 0.40, 0.36, 1.0)
COL_STREETLAMP_LIT= (0.98, 0.78, 0.42, 1.0)
COL_CAUTION_YEL   = (0.96, 0.78, 0.18, 1.0)
COL_ICE_BLUE      = (0.42, 0.74, 0.92, 1.0)
COL_LOTTERY_YEL   = (0.98, 0.84, 0.32, 1.0)
COL_LOTTERY_RED   = (0.86, 0.22, 0.20, 1.0)
COL_STRIP_PVC     = (0.72, 0.78, 0.82, 0.65)


def build_polish_floor():
    # Cross the existing N-S plank seams with E-W tile seams so the
    # floor reads as a checkerboard of ~1m squares — a canon
    # convenience-store look.
    for j in range(0, 10):
        make_box(f"Floor_SeamY_{j}", (0.0, float(j), 0.005),
                 (12.4, 0.02, 0.001), COL_FLOOR_SEAM)
    # Yellow caution stripe at the foot of the counter front (south-
    # facing strip along Blender X∈[4.45, 5.55] is the counter top
    # footprint; stripe sits just west of the counter front face).
    make_box("Floor_CautionStripe",
             (4.40, 4.5, 0.010),
             (0.08, 4.40, 0.001), COL_CAUTION_YEL)
    # Faded yellow safety stripe in front of cooler row too
    make_box("Floor_CoolerCautionStripe",
             (0.0, 8.10, 0.010),
             (10.0, 0.06, 0.001), COL_CAUTION_YEL)


def build_door_decals():
    # Hours / payment / ATM / OPEN — small high-contrast rectangles
    # taped to the inside of the south glass door at human-eye level.
    decals = [
        # (cx_offset, cz, w, h, color, name)
        (-1.20, 1.40, 0.28, 0.20, COL_PAPER,        "Decal_Hours"),
        (-1.20, 1.18, 0.28, 0.10, COL_BRAND_NAVY,   "Decal_VisaMC"),
        (+1.20, 1.40, 0.28, 0.18, COL_LOTTERY_RED,  "Decal_OPEN"),
        (+1.20, 1.18, 0.28, 0.10, COL_BRAND_NAVY,   "Decal_ATM"),
        # KWIK STOP delivery hours sticker (lower)
        (0.00, 0.40, 0.36, 0.14, COL_PAPER_AGED,    "Decal_Delivery"),
    ]
    for (xo, zo, w, h, col, nm) in decals:
        make_box(nm, (xo, 0.02, zo), (w, 0.005, h), col)


def build_ice_machine():
    # West wall ice machine — front-loader, glass-top freezer feel
    cx, cy = -5.40, 1.20
    make_box("IceMachine_Body", (cx, cy, 0.80),
             (1.10, 1.20, 1.60), COL_METAL_STEEL)
    make_box("IceMachine_Top",  (cx, cy, 1.62),
             (1.14, 1.24, 0.06), COL_METAL_BLACK)
    make_box("IceMachine_Lid",  (cx + 0.10, cy, 1.66),
             (0.94, 1.04, 0.04), COL_ICE_BLUE)
    # ICE label
    make_box("IceMachine_Sign", (cx - 0.50, cy, 1.20),
             (0.02, 0.80, 0.30), COL_ICE_BLUE)
    make_box("IceMachine_SignText", (cx - 0.51, cy, 1.20),
             (0.005, 0.40, 0.16), COL_PAPER)
    # Floor drain pan at base
    make_box("IceMachine_DrainPan", (cx, cy, 0.04),
             (1.20, 1.30, 0.04), COL_METAL_BLACK)


def build_lottery_display():
    # Lottery scratch-off / Powerball display behind counter, mounted
    # on the east wall above the cig rack (which tops at ~1.95m).
    cx = 5.45 + 0.04  # just in front of east wall
    cy = 4.50 - 2.10  # south end of counter, opposite the register
    base_z = 2.16
    make_box("Lottery_Box", (cx, cy, base_z),
             (0.02, 0.60, 0.40), COL_METAL_STEEL)
    # Yellow signage banner
    make_box("Lottery_BannerYellow", (cx - 0.005, cy, base_z + 0.16),
             (0.005, 0.56, 0.10), COL_LOTTERY_YEL)
    # Red Powerball stripe
    make_box("Lottery_BannerRed", (cx - 0.005, cy, base_z + 0.04),
             (0.005, 0.56, 0.10), COL_LOTTERY_RED)
    # Five scratch-off tickets in a row, dispensed from below
    for t in range(5):
        ty = cy - 0.20 + t * 0.10
        make_box(f"Lottery_Ticket_{t}",
                 (cx - 0.010, ty, base_z - 0.16),
                 (0.005, 0.08, 0.10),
                 SNACK_TINTS[t % len(SNACK_TINTS)])


def build_newspaper_rack_exterior():
    # Coin-op newspaper vending rack outside the front doors, visible
    # through the bottom of the south windows.
    for sgn, xpos in [(-1, -1.80), (+1, +1.80)]:
        rack_y = -0.80
        make_box(f"NewsRack_{sgn:+d}_Body", (xpos, rack_y, 0.55),
                 (0.60, 0.40, 1.10), (0.62, 0.18, 0.16, 1.0)
                                       if sgn < 0 else
                                       (0.18, 0.32, 0.62, 1.0))
        make_box(f"NewsRack_{sgn:+d}_Window", (xpos, rack_y - 0.21, 0.80),
                 (0.46, 0.005, 0.40), COL_GLASS)
        # Visible paper inside
        make_box(f"NewsRack_{sgn:+d}_Paper", (xpos, rack_y - 0.20, 0.78),
                 (0.40, 0.01, 0.30), COL_NEWSPRINT)
        # Coin slot
        make_box(f"NewsRack_{sgn:+d}_Coin", (xpos, rack_y - 0.21, 0.30),
                 (0.04, 0.005, 0.04), COL_METAL_BLACK)
        # Legs
        for ls in (-1, +1):
            make_box(f"NewsRack_{sgn:+d}_Leg_{ls}",
                     (xpos + ls*0.22, rack_y, 0.05),
                     (0.04, 0.04, 0.10), COL_METAL_BLACK)


def build_trash_can():
    # KWIK-branded trash bin between counter and east window
    cx, cy = 5.20, 1.40
    make_cyl("Trash_Body", (cx, cy, 0.50), 0.30, 1.00, COL_BRAND_RED)
    # Brand band
    make_cyl("Trash_BrandBand", (cx, cy, 0.70), 0.31, 0.16, COL_PAPER)
    # Lid with swing-flap slot
    make_cyl("Trash_Lid", (cx, cy, 1.04), 0.32, 0.04, COL_METAL_BLACK)
    make_box("Trash_FlapSlot", (cx, cy, 1.00),
             (0.32, 0.02, 0.04), COL_METAL_STEEL)


def build_strip_curtain():
    # Plastic strip curtain hanging in stockroom doorway
    door_x = 5.0
    door_y = 8.78  # at back-room door near north end of east wall
    # The stockroom door is built elsewhere; the strip curtain hangs
    # in FRONT of it as 6 PVC slats.
    for s in range(6):
        sx = door_x - 0.40 + s * 0.16
        make_box(f"StripCurtain_{s}", (sx, door_y, 1.40),
                 (0.12, 0.005, 1.60), COL_STRIP_PVC)


def build_counter_impulse_buys():
    # Small high-margin items lined along the counter top east-of-
    # register, where Sam can reach them but the customer must
    # cross the counter to grab. Canon convenience-store layout.
    base_y = 4.5
    base_z = 1.10
    # Mint dispenser
    make_box("Counter_MintsTray", (5.10, base_y + 1.20, base_z),
             (0.36, 0.30, 0.06), COL_METAL_STEEL)
    for m in range(6):
        make_box(f"Counter_MintTube_{m}",
                 (5.05 + (m % 3) * 0.10, base_y + 1.20 + (m // 3) * 0.10,
                  base_z + 0.06),
                 (0.04, 0.04, 0.12), SNACK_TINTS[m % len(SNACK_TINTS)])
    # Gum strip rack
    make_box("Counter_GumStrip", (5.10, base_y + 1.65, base_z + 0.06),
             (0.32, 0.20, 0.10), COL_METAL_BLACK)
    for g in range(4):
        gy = base_y + 1.58 + g * 0.06
        make_box(f"Counter_GumPack_{g}",
                 (5.05, gy, base_z + 0.12),
                 (0.05, 0.05, 0.10), SNACK_TINTS[g % len(SNACK_TINTS)])
    # Slim Jim jar — tall clear cylinder on the counter top, jerky
    # sticks visible inside
    make_cyl("Counter_SlimJimJar", (4.80, base_y - 1.70, base_z + 0.18),
             0.07, 0.34, COL_GLASS)
    for s in range(8):
        ang = s * 0.78
        sx = 4.80 + math.cos(ang) * 0.03
        sy = base_y - 1.70 + math.sin(ang) * 0.03
        make_box(f"Counter_SlimJim_{s}", (sx, sy, base_z + 0.18),
                 (0.012, 0.012, 0.28), (0.42, 0.18, 0.10, 1.0))
    # Counter pen-on-a-chain
    make_cyl("Counter_PenBody", (4.95, base_y - 1.85, base_z + 0.04),
             0.008, 0.14, (0.18, 0.18, 0.18, 1.0), axis='Y')


def build_ceiling_infrastructure():
    # Security camera dome (over register, looking down-and-west)
    cam_x, cam_y = 4.0, 4.0
    make_cyl("Cam_Dome", (cam_x, cam_y, CEIL_Z - 0.10),
             0.12, 0.12, COL_METAL_BLACK)
    make_cyl("Cam_DomeGlass", (cam_x, cam_y, CEIL_Z - 0.16),
             0.10, 0.04, (0.18, 0.20, 0.22, 0.70))
    # Second cam over door
    make_cyl("Cam_Dome2", (0.0, 1.0, CEIL_Z - 0.10),
             0.10, 0.10, COL_METAL_BLACK)
    # Smoke detectors (two, distributed)
    for d_i, (dx, dy) in enumerate([(-2.5, 6.0), (+2.5, 2.5)]):
        make_cyl(f"SmokeDetect_{d_i}", (dx, dy, CEIL_Z - 0.04),
                 0.10, 0.04, COL_PAPER)
        make_box(f"SmokeDetect_{d_i}_LED", (dx + 0.04, dy, CEIL_Z - 0.06),
                 (0.012, 0.012, 0.012), COL_LOTTERY_RED)
    # Sprinkler heads at tile-grid intersections
    for sx, sy in [(-2.0, 3.5), (+2.0, 3.5), (-2.0, 6.5), (+2.0, 6.5)]:
        make_cyl(f"Sprinkler_{sx:+.0f}_{sy:+.0f}",
                 (sx, sy, CEIL_Z - 0.04),
                 0.025, 0.08, COL_METAL_STEEL)
        make_box(f"SprinklerCap_{sx:+.0f}_{sy:+.0f}",
                 (sx, sy, CEIL_Z - 0.10),
                 (0.06, 0.06, 0.02), COL_METAL_BLACK)
    # HVAC vent grille (rectangular, north-center)
    make_box("HVAC_Vent", (-1.0, 7.5, CEIL_Z - 0.02),
             (1.20, 0.60, 0.04), COL_METAL_STEEL)
    # Vent slats
    for vs in range(6):
        make_box(f"HVAC_VentSlat_{vs}",
                 (-1.0 + (vs - 2.5) * 0.16, 7.5, CEIL_Z - 0.05),
                 (0.06, 0.50, 0.01), COL_METAL_BLACK)
    # Speaker dome (Muzak — corporate-spillover canon)
    make_cyl("CeilingSpeaker", (1.5, 5.5, CEIL_Z - 0.08),
             0.16, 0.08, COL_PAPER)


def build_electrical_conduit():
    # White EMT conduit running up the west wall to the ceiling,
    # tapping into the fluorescent fixture row.
    cx = -5.92  # just inside west wall (wall west face at -5.9)
    # Vertical run from outlet height (0.30) up to ceiling (2.95)
    make_box("Conduit_VertWest",
             (cx, 7.20, 1.62),
             (0.04, 0.04, 2.64), COL_PAPER)
    # 90° elbow to horizontal run along ceiling
    make_box("Conduit_HorizWest",
             (cx, 7.20, CEIL_Z - 0.06),
             (0.04, 4.40, 0.04), COL_PAPER)
    # Wall outlet at base
    make_box("Outlet_West",
             (cx + 0.02, 4.00, 0.30),
             (0.02, 0.16, 0.10), COL_PAPER)
    # Light switch beside register
    make_box("Switch_East",
             (5.88, 2.50, 1.30),
             (0.02, 0.10, 0.16), COL_PAPER)


def build_wet_floor_cone():
    # Yellow A-frame cone near coffee station — canonical clerk
    # gesture, suggests Sam mopped recently and the floor is drying.
    cx, cy = -4.40, 4.00
    # Body — two triangular panels facing E and W
    for sgn in (-1, +1):
        make_box(f"WetFloor_Panel_{sgn:+d}",
                 (cx + sgn * 0.18, cy, 0.30),
                 (0.04, 0.30, 0.60), COL_CAUTION_YEL)
    # Text band ("WET FLOOR")
    for sgn in (-1, +1):
        make_box(f"WetFloor_Text_{sgn:+d}",
                 (cx + sgn * 0.19, cy, 0.40),
                 (0.004, 0.26, 0.10), COL_METAL_BLACK)
    # Foot
    make_box("WetFloor_Foot", (cx, cy, 0.02),
             (0.30, 0.30, 0.04), COL_RUBBER_MAT)


def build_exterior_through_windows():
    # World outside the south windows. Builds at Blender Y∈[-3, -0.4]
    # (south of building) so it reads through the windows. Pump
    # canopy spans both windows; two pumps below it; one parked car
    # silhouette; streetlamp at the southwest corner.
    # ── Asphalt apron (visible through bottom of windows) ───────
    make_box("Asphalt", (0.0, -2.0, -0.04),
             (16.0, 4.0, 0.04), COL_ASPHALT)
    # Parking lines (3 stripes)
    for ps in (-1, 0, +1):
        make_box(f"ParkLine_{ps:+d}",
                 (ps * 2.8, -1.6, -0.018),
                 (0.06, 1.60, 0.004), (0.84, 0.78, 0.20, 1.0))
    # ── Canopy ───────────────────────────────────────────────────
    canopy_y, canopy_z = -2.20, 3.40
    make_box("Canopy_Top", (0.0, canopy_y, canopy_z),
             (10.0, 4.40, 0.20), COL_CANOPY)
    make_box("Canopy_Skirt", (0.0, canopy_y - 2.10, canopy_z - 0.05),
             (10.0, 0.10, 0.40), COL_CANOPY_TRIM)
    make_box("Canopy_Skirt_Branding",
             (0.0, canopy_y - 2.11, canopy_z + 0.05),
             (3.20, 0.005, 0.18), COL_PAPER)
    # Canopy support columns (2)
    for sgn, sx in [(-1, -3.6), (+1, +3.6)]:
        make_box(f"Canopy_Col_{sgn:+d}",
                 (sx, canopy_y, canopy_z / 2.0),
                 (0.30, 0.30, canopy_z), COL_CANOPY_TRIM)
    # ── Two gas pumps under canopy ──────────────────────────────
    for sgn, px in [(-1, -2.20), (+1, +2.20)]:
        # Pump base / body
        make_box(f"Pump_{sgn:+d}_Base", (px, canopy_y, 0.30),
                 (0.50, 0.60, 0.60), COL_PUMP_BODY)
        # Pump screen + buttons
        make_box(f"Pump_{sgn:+d}_Display", (px, canopy_y - 0.31, 1.20),
                 (0.40, 0.005, 0.50), COL_PUMP_FACE)
        # Pump head (handle housing)
        make_box(f"Pump_{sgn:+d}_Head", (px, canopy_y, 1.80),
                 (0.50, 0.60, 0.36), COL_PUMP_BODY)
        # Pump hose nozzle
        make_box(f"Pump_{sgn:+d}_Nozzle",
                 (px + 0.18, canopy_y - 0.20, 1.20),
                 (0.10, 0.04, 0.30), COL_METAL_BLACK)
        # Price-display LEDs (three digits)
        for d_i in range(3):
            make_box(f"Pump_{sgn:+d}_LED_{d_i}",
                     (px - 0.15 + d_i * 0.15, canopy_y - 0.32, 1.40),
                     (0.10, 0.005, 0.14), (0.94, 0.18, 0.08, 1.0))
    # ── Parked sedan silhouette beside the right pump ───────────
    car_x, car_y = +3.20, -1.40
    make_box("Car_Body", (car_x, car_y, 0.55),
             (1.80, 1.00, 0.50), COL_CAR_BODY)
    make_box("Car_Roof", (car_x, car_y, 1.10),
             (1.30, 0.94, 0.40), COL_CAR_BODY)
    make_box("Car_WindowFront", (car_x + 0.65, car_y, 1.10),
             (0.04, 0.86, 0.40), COL_CAR_WINDOW)
    make_box("Car_WindowRear",  (car_x - 0.65, car_y, 1.10),
             (0.04, 0.86, 0.40), COL_CAR_WINDOW)
    for ws in (-1, +1):
        make_box(f"Car_WindowSide_{ws:+d}",
                 (car_x, car_y + ws * 0.48, 1.10),
                 (1.16, 0.005, 0.40), COL_CAR_WINDOW)
    # Wheel arches (4)
    for wx, wy in [(car_x - 0.60, car_y - 0.48),
                   (car_x + 0.60, car_y - 0.48),
                   (car_x - 0.60, car_y + 0.48),
                   (car_x + 0.60, car_y + 0.48)]:
        make_cyl(f"Car_Wheel_{wx:+.1f}_{wy:+.1f}",
                 (wx, wy, 0.30), 0.26, 0.20, COL_METAL_BLACK, axis='Y')
    # Headlights
    for ws in (-1, +1):
        make_box(f"Car_Headlight_{ws:+d}",
                 (car_x + 0.92, car_y + ws * 0.32, 0.55),
                 (0.005, 0.18, 0.14), COL_STREETLAMP_LIT)
    # ── Streetlamp at southwest corner ──────────────────────────
    lp_x, lp_y = -5.40, -2.80
    make_box("Streetlamp_Base", (lp_x, lp_y, 0.20),
             (0.20, 0.20, 0.40), COL_STREETLAMP)
    make_box("Streetlamp_Pole", (lp_x, lp_y, 2.40),
             (0.10, 0.10, 4.40), COL_STREETLAMP)
    # Arm
    make_box("Streetlamp_Arm", (lp_x + 0.60, lp_y, 4.60),
             (1.40, 0.08, 0.10), COL_STREETLAMP)
    # Lamp head (sodium-warm)
    make_box("Streetlamp_Head", (lp_x + 1.30, lp_y, 4.50),
             (0.50, 0.20, 0.20), COL_STREETLAMP_LIT)
    # ── End-cap product display facing the south windows ────────
    # A cardboard end-cap pyramid of stacked product cases — adds
    # density between the registers and the windows.
    ec_x, ec_y = -3.20, 2.60
    for ec_tier in range(3):
        tier_w = 1.20 - ec_tier * 0.30
        tier_y = ec_y + ec_tier * 0.20
        tier_z = 0.40 + ec_tier * 0.30
        make_box(f"EndCap_Box_{ec_tier}",
                 (ec_x, tier_y, tier_z),
                 (tier_w, 0.60, 0.30), (0.84, 0.62, 0.30, 1.0))
    # End-cap signage
    make_box("EndCap_Sign", (ec_x, ec_y - 0.42, 1.40),
             (1.20, 0.005, 0.22), COL_LOTTERY_RED)
    # Stacked products visible on top of the smallest tier
    for p_i in range(4):
        make_box(f"EndCap_Product_{p_i}",
                 (ec_x - 0.30 + p_i * 0.20, ec_y + 0.40, 1.32),
                 (0.14, 0.14, 0.20),
                 SNACK_TINTS[(p_i + 3) % len(SNACK_TINTS)])


def build_polish_pass():
    build_polish_floor()
    build_door_decals()
    build_ice_machine()
    build_lottery_display()
    build_newspaper_rack_exterior()
    build_trash_can()
    build_strip_curtain()
    build_counter_impulse_buys()
    build_ceiling_infrastructure()
    build_electrical_conduit()
    build_wet_floor_cone()
    build_exterior_through_windows()


# ════════════════════════════════════════════════════════════════
# POLISH PASS 2 — atmosphere + life
# Pushes density past "lots of furniture" toward "this room is
# lived in." Hanging promo banners, neon in the windows, wall
# clock + fire extinguisher + employees-must-wash sign, a proper
# Slurpee fountain, edge-of-shelf price strips, customer
# detritus (cup on the counter, magazine open on a stool, candy
# wrapper on the floor), a wall payphone (canon vol6 detail),
# visible stockroom shelving through the strip curtain, more
# floor-display pyramids, a sun-faded poster.
# ════════════════════════════════════════════════════════════════
COL_NEON_RED      = (0.98, 0.32, 0.32, 1.0)
COL_NEON_BLUE     = (0.42, 0.72, 0.96, 1.0)
COL_NEON_PINK     = (0.96, 0.46, 0.72, 1.0)
COL_NEON_GREEN    = (0.42, 0.96, 0.52, 1.0)
COL_CLOCK_FACE    = (0.94, 0.92, 0.86, 1.0)
COL_CLOCK_RIM     = (0.42, 0.40, 0.36, 1.0)
COL_FIRE_RED      = (0.74, 0.16, 0.14, 1.0)
COL_PAYPHONE      = (0.32, 0.30, 0.30, 1.0)
COL_PAYPHONE_TRIM = (0.20, 0.18, 0.18, 1.0)
COL_SLURPEE_CASE  = (0.92, 0.94, 0.92, 1.0)
COL_SLURPEE_BLUE  = (0.18, 0.42, 0.86, 1.0)
COL_SLURPEE_RED   = (0.92, 0.22, 0.20, 1.0)
COL_PRICE_TAG     = (0.96, 0.94, 0.84, 1.0)
COL_POSTER_FADED  = (0.78, 0.62, 0.46, 1.0)
COL_POSTER_INK    = (0.32, 0.24, 0.20, 1.0)
COL_BOX_KRAFT     = (0.74, 0.56, 0.34, 1.0)


def build_hanging_banners():
    # Hanging promo banners along the ceiling — three of them,
    # mounted on thin steel cables a foot below the ceiling tiles.
    banners = [
        # (name, x, y, text_color, bg_color, w, h)
        ("Banner_BeerColdest",  -3.0, 6.0, COL_PAPER, COL_BRAND_NAVY,  1.80, 0.36),
        ("Banner_Slurpee99",     0.0, 4.5, COL_PAPER, COL_BRAND_RED,   1.60, 0.36),
        ("Banner_ATMHere",      +3.0, 3.0, COL_PAPER, COL_LOTTERY_YEL, 1.40, 0.30),
    ]
    for (nm, bx, by, fg, bg, w, h) in banners:
        # Two thin cables suspending the banner
        for cs in (-1, +1):
            make_box(f"{nm}_Cable_{cs}",
                     (bx + cs * (w * 0.40), by, CEIL_Z - 0.20),
                     (0.01, 0.01, 0.40), COL_METAL_STEEL)
        # Banner panel
        make_box(f"{nm}_BG",
                 (bx, by, CEIL_Z - 0.42),
                 (w, 0.02, h), bg)
        # Lettering strip (abstracted, contrast colour)
        make_box(f"{nm}_TextStrip",
                 (bx, by + 0.012, CEIL_Z - 0.42),
                 (w * 0.80, 0.005, h * 0.50), fg)


def build_window_neon():
    # Two neon signs in the south windows — OPEN (red) on the left,
    # ICE COLD BEER (blue, multi-line) on the right. Tiny tubes —
    # geometry only; the shader stack does the bloom-on-edges.
    # Left window (Blender X≈-3 center). OPEN sign.
    open_x, open_y, open_z = -3.0, 0.30, 2.00
    # Outer "OPEN" rectangle
    for stroke in [
        # (cx_off, cz_off, w, h)
        (0.0, 0.30, 0.86, 0.04),   # top
        (0.0, -0.30, 0.86, 0.04),  # bottom
        (-0.42, 0.0, 0.04, 0.60),  # left
        (+0.42, 0.0, 0.04, 0.60),  # right
    ]:
        make_box(f"Neon_OPEN_Border_{stroke[0]:+.2f}_{stroke[1]:+.2f}",
                 (open_x + stroke[0], open_y, open_z + stroke[1]),
                 (stroke[2], 0.02, stroke[3]), COL_NEON_RED)
    # Inner OPEN text (4 letters as small boxes)
    for li, lx in enumerate([-0.32, -0.10, +0.10, +0.32]):
        make_box(f"Neon_OPEN_Letter_{li}",
                 (open_x + lx, open_y, open_z),
                 (0.16, 0.005, 0.18), COL_NEON_RED)
    # Right window — ICE COLD BEER, two lines
    beer_x, beer_y, beer_z = +3.0, 0.30, 1.70
    # "ICE COLD" line — blue
    for li, lx in enumerate([-0.40, -0.20, 0.0, +0.20, +0.40]):
        make_box(f"Neon_ICECOLD_{li}",
                 (beer_x + lx, beer_y, beer_z + 0.18),
                 (0.16, 0.005, 0.14), COL_NEON_BLUE)
    # "BEER" line — pink
    for li, lx in enumerate([-0.30, -0.10, +0.10, +0.30]):
        make_box(f"Neon_BEER_{li}",
                 (beer_x + lx, beer_y, beer_z - 0.10),
                 (0.16, 0.005, 0.18), COL_NEON_PINK)
    # ATM sign in left window above OPEN — green neon
    for li, lx in enumerate([-0.20, 0.0, +0.20]):
        make_box(f"Neon_ATM_{li}",
                 (open_x + lx, open_y, open_z + 0.62),
                 (0.16, 0.005, 0.14), COL_NEON_GREEN)


def build_wall_ornaments():
    # ── Wall clock — north wall above coolers, just left of banner
    clock_x, clock_y, clock_z = -3.20, 8.88, 2.20
    make_cyl("Clock_Face", (clock_x, clock_y, clock_z),
             0.18, 0.04, COL_CLOCK_FACE, axis='Y')
    make_cyl("Clock_Rim", (clock_x, clock_y - 0.022, clock_z),
             0.20, 0.02, COL_CLOCK_RIM, axis='Y')
    # Hour markers (12, 3, 6, 9)
    for ang_i, (mx, mz) in enumerate([(0.0, +0.13), (+0.13, 0.0),
                                       (0.0, -0.13), (-0.13, 0.0)]):
        make_box(f"Clock_Tick_{ang_i}",
                 (clock_x + mx, clock_y - 0.025, clock_z + mz),
                 (0.02, 0.005, 0.02), COL_METAL_BLACK)
    # Hour + minute hands (frozen at 11:47, vol6's canonical hour)
    make_box("Clock_HourHand",
             (clock_x - 0.025, clock_y - 0.030, clock_z + 0.040),
             (0.05, 0.004, 0.10), COL_METAL_BLACK)
    make_box("Clock_MinuteHand",
             (clock_x + 0.080, clock_y - 0.030, clock_z + 0.020),
             (0.16, 0.004, 0.018), COL_METAL_BLACK)
    # ── Fire extinguisher — west wall corner
    ext_x, ext_y = -5.88, 8.20
    make_cyl("FireExt_Body", (ext_x, ext_y, 0.86), 0.10, 0.50,
             COL_FIRE_RED)
    make_cyl("FireExt_Top", (ext_x, ext_y, 1.20), 0.08, 0.18,
             COL_METAL_BLACK)
    make_box("FireExt_Bracket", (ext_x - 0.04, ext_y, 0.86),
             (0.04, 0.18, 0.50), COL_METAL_STEEL)
    make_box("FireExt_Sign", (ext_x - 0.02, ext_y - 0.40, 1.60),
             (0.005, 0.30, 0.30), COL_FIRE_RED)
    # ── Employees-Must-Wash-Hands sign by stockroom door
    make_box("Sign_HandWash", (5.88, 8.40, 1.80),
             (0.005, 0.40, 0.20), COL_PAPER)
    # ── Calendar (girl, beach, faded — corner-store classic)
    make_box("Calendar", (-5.88, 5.40, 1.70),
             (0.005, 0.40, 0.50), COL_POSTER_FADED)
    make_box("Calendar_GridTop", (-5.88 + 0.002, 5.40, 1.55),
             (0.001, 0.34, 0.20), COL_PAPER)
    # ── Sun-faded vintage movie poster, east wall above HotCase
    make_box("Poster_Faded", (5.88, 3.20, 2.00),
             (0.005, 0.60, 0.80), COL_POSTER_FADED)
    make_box("Poster_Faded_Title", (5.875, 3.20, 1.70),
             (0.002, 0.50, 0.10), COL_POSTER_INK)
    make_box("Poster_Faded_Figure", (5.875, 3.20, 2.20),
             (0.002, 0.36, 0.40), COL_POSTER_INK)


def build_slurpee_fountain():
    # Two-flavor Slurpee machine on the west-side coffee counter.
    # Blue cherry + red cola. Sits next to the existing coffee
    # station; reads as the "drinks" pole of the west wall.
    cx, cy = -5.30, 5.40
    base_z = 1.30
    # Stainless base
    make_box("Slurpee_Base", (cx, cy, base_z),
             (0.86, 0.50, 0.30), COL_METAL_STEEL)
    # Two clear barrels
    for bs, by_off in [(-1, -0.18), (+1, +0.18)]:
        make_cyl(f"Slurpee_Barrel_{bs:+d}",
                 (cx, cy + by_off, base_z + 0.46),
                 0.16, 0.50, COL_SLURPEE_CASE)
        # Liquid inside (different colour each barrel)
        col = COL_SLURPEE_BLUE if bs < 0 else COL_SLURPEE_RED
        make_cyl(f"Slurpee_Liquid_{bs:+d}",
                 (cx, cy + by_off, base_z + 0.36),
                 0.14, 0.28, col)
        # Top auger cap
        make_cyl(f"Slurpee_Top_{bs:+d}",
                 (cx, cy + by_off, base_z + 0.74),
                 0.16, 0.06, COL_METAL_BLACK)
        # Dispense handle on the customer side (south)
        make_box(f"Slurpee_Handle_{bs:+d}",
                 (cx + 0.20, cy + by_off, base_z + 0.30),
                 (0.04, 0.06, 0.20), COL_METAL_BLACK)
        # Drip catch tray
        make_box(f"Slurpee_DripTray_{bs:+d}",
                 (cx + 0.18, cy + by_off, base_z + 0.16),
                 (0.16, 0.20, 0.04), COL_METAL_STEEL)
    # Flavor-label header strip across both barrels
    make_box("Slurpee_LabelHeader", (cx - 0.18, cy, base_z + 0.86),
             (0.04, 0.50, 0.12), COL_BRAND_NAVY)


def build_price_tag_strips():
    # Edge-of-shelf white price strips on each snack aisle shelf.
    # The aisles are at Y=3.5 and Y=5.5 with 5 shelves each. Strips
    # face south on the south aisle, north on the north aisle.
    for ai, ay in enumerate([3.5, 5.5]):
        face_y = ay + (-0.36 if ai == 0 else +0.36)
        for sh in range(5):
            shz = 0.30 + sh * 0.36
            make_box(f"PriceStrip_Aisle{ai}_S{sh}",
                     (0.0, face_y, shz),
                     (5.0, 0.005, 0.04), COL_PRICE_TAG)
            # Small dollar-amount marks (3 visible per shelf)
            for d_i, dx in enumerate([-1.6, 0.0, +1.6]):
                make_box(f"PriceMark_Aisle{ai}_S{sh}_T{d_i}",
                         (dx, face_y + 0.003 * (1 if ai == 0 else -1),
                          shz),
                         (0.16, 0.001, 0.02), COL_METAL_BLACK)


def build_customer_detritus():
    # Evidence that THIS room has been used recently.
    # Half-finished coffee on the counter beside the register
    make_cyl("Detritus_CoffeeCup",
             (5.10, 4.5 - 0.40, 1.20),
             0.04, 0.16, COL_PAPER)
    make_cyl("Detritus_CoffeeLid",
             (5.10, 4.5 - 0.40, 1.30),
             0.045, 0.02, COL_METAL_BLACK)
    # An open magazine on the counter (south end)
    make_box("Detritus_MagOpen",
             (4.85, 4.5 - 1.95, 1.08),
             (0.30, 0.22, 0.005), COL_PAPER)
    make_box("Detritus_MagOpen_Crease",
             (4.85, 4.5 - 1.95, 1.082),
             (0.005, 0.22, 0.002), COL_NEWSPRINT)
    # Candy wrapper on the floor near the south door
    make_box("Detritus_CandyWrap",
             (1.20, 0.60, 0.014),
             (0.10, 0.06, 0.002), (0.92, 0.32, 0.20, 1.0))
    # Crumpled receipt under the magazine rack (existing rack at south)
    make_box("Detritus_Receipt",
             (-2.40, 1.20, 0.014),
             (0.06, 0.04, 0.002), COL_PAPER)
    # Empty Slurpee cup tipped over near the wet floor cone
    make_cyl("Detritus_SlurpeeCup",
             (-4.20, 4.20, 0.06),
             0.05, 0.12, COL_SLURPEE_CASE, axis='Y')


def build_payphone():
    # Wall payphone — east wall, near the south window. Canon vol6
    # period detail; even after cell phones, the kwik stop kept it.
    px, py = 5.88, 1.40
    make_box("Payphone_Box", (px, py, 1.30),
             (0.06, 0.34, 0.60), COL_PAYPHONE)
    # Privacy hood
    make_box("Payphone_Hood", (px - 0.16, py, 1.74),
             (0.30, 0.36, 0.10), COL_PAYPHONE_TRIM)
    # Receiver (handset) hanging on left side
    make_box("Payphone_Handset", (px - 0.06, py - 0.20, 1.30),
             (0.04, 0.04, 0.24), COL_PAYPHONE_TRIM)
    # Coin slot
    make_box("Payphone_CoinSlot", (px - 0.04, py + 0.08, 1.46),
             (0.02, 0.10, 0.02), COL_METAL_BLACK)
    # Number-pad face
    make_box("Payphone_Keypad", (px - 0.04, py, 1.18),
             (0.02, 0.16, 0.20), COL_METAL_BLACK)
    # 3×4 number-pad buttons
    for r in range(4):
        for c in range(3):
            make_box(f"Payphone_Key_{r}_{c}",
                     (px - 0.05,
                      py - 0.06 + c * 0.06,
                      1.10 + r * 0.045),
                     (0.005, 0.04, 0.034), COL_PAPER_AGED)
    # Phone-card / dialing-instructions decal
    make_box("Payphone_Decal", (px - 0.04, py, 1.62),
             (0.005, 0.26, 0.08), COL_PAPER)


def build_stockroom_through_curtain():
    # Stack of cardboard boxes visible THROUGH the strip curtain.
    # Sits just inside the stockroom door — the door opens at
    # (5.0, 8.78) per build_floor_props; we put the boxes a bit
    # past it (Blender Y=9.2 — outside the interior wall but the
    # SubViewport renders the open world, no occlusion check).
    # Actually safer: keep them inside the building, on the inner
    # face of the stockroom-door cutout — visible because the door
    # is implied (no actual closed door geometry, just the strip
    # curtain). Place at Y≈8.8 just behind the curtain.
    box_x = 5.0
    box_y = 8.95  # slightly past the strip curtain
    # Stack of three cardboard cartons
    for ti in range(3):
        make_box(f"Stockroom_Box_{ti}",
                 (box_x - 0.20 + (ti % 2) * 0.40,
                  box_y,
                  0.25 + (ti // 2) * 0.50),
                 (0.36, 0.30, 0.40), COL_BOX_KRAFT)
    # A shelving unit visible behind the boxes
    make_box("Stockroom_Shelf",
             (box_x, box_y + 0.20, 1.40),
             (1.20, 0.04, 1.60), COL_METAL_STEEL)
    # Three loose products on the shelf
    for pi in range(3):
        make_box(f"Stockroom_Product_{pi}",
                 (box_x - 0.40 + pi * 0.40,
                  box_y + 0.22,
                  1.20),
                 (0.30, 0.20, 0.30),
                 SNACK_TINTS[pi % len(SNACK_TINTS)])


def build_more_floor_displays():
    # Beer 30-rack pyramid south of the cooler row
    bx, by = -2.40, 7.20
    for layer_i in range(3):
        layer_w = 1.20 - layer_i * 0.30
        layer_d = 0.60 - layer_i * 0.10
        make_box(f"BeerStack_Layer_{layer_i}",
                 (bx, by, 0.30 + layer_i * 0.32),
                 (layer_w, layer_d, 0.30), COL_BRAND_NAVY)
        # White label band on each layer
        make_box(f"BeerStack_Band_{layer_i}",
                 (bx, by - layer_d / 2 - 0.005, 0.30 + layer_i * 0.32),
                 (layer_w * 0.80, 0.005, 0.08), COL_PAPER)
    # Charcoal-bag pyramid near west window
    cx, cy = -3.40, 1.80
    for li in range(3):
        lw = 0.96 - li * 0.24
        make_box(f"CharcoalStack_{li}",
                 (cx, cy, 0.20 + li * 0.30),
                 (lw, 0.50, 0.28), COL_METAL_BLACK)
        make_box(f"CharcoalLabel_{li}",
                 (cx, cy - 0.255, 0.20 + li * 0.30),
                 (lw * 0.7, 0.005, 0.10), COL_LOTTERY_RED)
    # Cardboard pyramid of red-cup 12-packs near east window
    cup_x, cup_y = 3.20, 1.80
    for li in range(2):
        lw = 0.80 - li * 0.24
        make_box(f"CupStack_{li}",
                 (cup_x, cup_y, 0.18 + li * 0.26),
                 (lw, 0.40, 0.24), COL_BRAND_RED)
    # SALE topper sign
    make_box("CupStack_SaleSign", (cup_x, cup_y, 0.94),
             (0.40, 0.005, 0.18), COL_LOTTERY_YEL)


def build_atm_detail():
    # The ATM lives in build_floor_props elsewhere — augment it
    # with a keypad, slot detail, and a small overhead sign. We
    # place these by absolute coords because the existing ATM is
    # at roughly (cx=-5.0, cy=2.10, cz_top=1.40) per the v2 build.
    ax, ay = -5.40, 2.10
    # Keypad and display
    make_box("ATM_Display", (ax + 0.32, ay, 1.40),
             (0.005, 0.32, 0.18), (0.18, 0.32, 0.42, 1.0))
    make_box("ATM_DisplayHighlight", (ax + 0.322, ay, 1.42),
             (0.001, 0.20, 0.04), COL_LOTTERY_YEL)
    # 4×3 keypad
    for r in range(4):
        for c in range(3):
            make_box(f"ATM_Key_{r}_{c}",
                     (ax + 0.32,
                      ay - 0.12 + c * 0.08,
                      1.16 + r * 0.06),
                     (0.005, 0.06, 0.05), COL_METAL_BLACK)
    # Card slot + receipt slot
    make_box("ATM_CardSlot", (ax + 0.32, ay - 0.12, 1.06),
             (0.005, 0.10, 0.012), COL_METAL_STEEL)
    make_box("ATM_ReceiptSlot", (ax + 0.32, ay + 0.12, 1.06),
             (0.005, 0.10, 0.012), COL_METAL_STEEL)
    # Cash dispense slot
    make_box("ATM_CashSlot", (ax + 0.32, ay, 0.86),
             (0.005, 0.22, 0.020), COL_METAL_BLACK)
    # Overhead "ATM" sign on a thin bracket
    make_box("ATM_OverheadBracket", (ax, ay, 2.10),
             (0.04, 0.04, 0.40), COL_METAL_BLACK)
    make_box("ATM_OverheadSign", (ax + 0.02, ay, 2.30),
             (0.20, 0.30, 0.12), COL_LOTTERY_YEL)
    make_box("ATM_OverheadSignText", (ax + 0.025, ay, 2.30),
             (0.005, 0.22, 0.06), COL_METAL_BLACK)


def build_air_freshener_tree():
    # A bundle of pine-tree air fresheners hanging above the
    # register on a small wire — classic gas-station accent.
    base_x, base_y = 5.0, 4.5 - 0.40
    base_z = 1.90
    # Suspension wire
    make_box("AirFresh_Wire",
             (base_x, base_y, base_z + 0.18),
             (0.005, 0.005, 0.36), COL_METAL_BLACK)
    # Three tree-shaped fresheners at different rotations
    tree_colors = [
        (0.40, 0.72, 0.42, 1.0),    # pine green
        (0.92, 0.34, 0.40, 1.0),    # cherry red
        (0.42, 0.62, 0.92, 1.0),    # new-car blue
    ]
    for ti, col in enumerate(tree_colors):
        ty = base_y + (ti - 1) * 0.06
        # Pine-tree silhouette as three stacked triangles → 3 boxes
        for tier in range(3):
            scale = 0.10 - tier * 0.025
            make_box(f"AirFresh_{ti}_Tier_{tier}",
                     (base_x, ty, base_z - 0.04 + tier * 0.04),
                     (0.005, scale, 0.04), col)
        # Trunk
        make_box(f"AirFresh_{ti}_Trunk",
                 (base_x, ty, base_z - 0.18),
                 (0.005, 0.02, 0.06), (0.42, 0.30, 0.20, 1.0))


def build_polish_pass_2():
    build_hanging_banners()
    build_window_neon()
    build_wall_ornaments()
    build_slurpee_fountain()
    build_price_tag_strips()
    build_customer_detritus()
    build_payphone()
    build_stockroom_through_curtain()
    build_more_floor_displays()
    build_atm_detail()
    build_air_freshener_tree()


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
        print(f"[build_kwik_stop] ✗ EXPORT FAILED: {e}")
        raise
    if os.path.exists(out_path):
        size = os.path.getsize(out_path)
        print(f"[build_kwik_stop] ✓ wrote {out_path} ({size} bytes)")


def main():
    clear_scene()
    build_shell()
    build_counter()
    build_harmony_banner()
    build_beer_cooler()
    build_coffee_station()
    build_snack_aisles()
    build_newspaper_stack()
    build_magazine_rack()
    build_floor_props()
    build_light_shafts()
    build_polish_pass()
    build_polish_pass_2()
    export_glb()


if __name__ == "__main__":
    main()
