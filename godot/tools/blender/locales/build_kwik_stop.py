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
    export_glb()


if __name__ == "__main__":
    main()
