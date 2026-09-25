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

# Product tints — warm-sunset-aligned palette. Per user "rainbow
# bright doesn't fit the concept art." Was 9 saturated primary +
# secondary colors; pulled to amber/rust/cream-dominant with two
# muted cool accents so the snack-aisle / cooler-can rows stop
# reading as a Skittles bag and start reading as a 1990s gas-
# station coloured by sodium-lamp warmth. Saturations halved.
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


def case_shell(prefix, center, size, color, open_face, wall=0.02):
    """Five panels, one face open — _props.structure.make_case_shell's
    twin for this self-contained builder (2026-09-24: every glass case
    here was a SOLID body with its food inside it, behind a "glass" slab
    that renders opaque — the pipeline has no alpha)."""
    cx, cy, cz = center
    sx, sy, sz = size
    hx, hy, hz = sx / 2.0, sy / 2.0, sz / 2.0
    w, ih = wall, sz - 2.0 * wall
    make_box(f"{prefix}_Top", (cx, cy, cz + hz - w / 2.0), (sx, sy, w), color)
    make_box(f"{prefix}_Bottom", (cx, cy, cz - hz + w / 2.0), (sx, sy, w), color)
    if open_face in ('-Y', '+Y'):
        sg = 1.0 if open_face == '-Y' else -1.0
        make_box(f"{prefix}_Side_L", (cx - hx + w / 2.0, cy, cz), (w, sy, ih), color)
        make_box(f"{prefix}_Side_R", (cx + hx - w / 2.0, cy, cz), (w, sy, ih), color)
        make_box(f"{prefix}_Back", (cx, cy + sg * (hy - w / 2.0), cz), (sx - 2.0 * w, w, ih), color)
    else:
        sg = 1.0 if open_face == '-X' else -1.0
        make_box(f"{prefix}_Side_L", (cx, cy - hy + w / 2.0, cz), (sx, w, ih), color)
        make_box(f"{prefix}_Side_R", (cx, cy + hy - w / 2.0, cz), (sx, w, ih), color)
        make_box(f"{prefix}_Back", (cx + sg * (hx - w / 2.0), cy, cz), (w, sy - 2.0 * w, ih), color)


COL_GLINT = (0.86, 0.90, 0.92, 1.0)   # where a glass pane is: two pale strips


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
        # on the wall face, 1.2 cm proud (2026-09-23: inside the wall —
        # the same 0.06/0.06 pattern that buried 398 kit baseboards)
        make_box(f"Wall_X{sgn:+d}_Base", (xpos - sgn*(WALL_THICK/2.0 + 0.006), 4.5, 0.08),
                 (0.012, 9.4, 0.16), COL_WALL_BASEBOARD)
    # North wall (back, beer cooler runs along it)
    make_box("Wall_N", (0.0, 9.0, CEIL_Z/2.0),
             (12.4, WALL_THICK, CEIL_Z), COL_WALL_CREAM)
    make_box("Wall_N_Base", (0.0, 9.0 - (WALL_THICK/2.0 + 0.006), 0.08),
             (12.4, 0.012, 0.16), COL_WALL_BASEBOARD)
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
    # on the wall's room face, glass in front of the frame (2026-09-24: frame and glass
    # were offset from the wall's CENTRE line — inside the wall, never visible)
        # Glass
        make_box(f"Window_S_{sgn:+d}_Glass", (cx, 0.12, 1.55),
                 (2.40, 0.04, 1.40), COL_GLASS_WARM)
        # Frame T + B
        make_box(f"Window_S_{sgn:+d}_Frame_T", (cx, 0.13, 2.30),
                 (2.50, 0.06, 0.10), COL_METAL_STEEL)
        make_box(f"Window_S_{sgn:+d}_Frame_B", (cx, 0.13, 0.80),
                 (2.50, 0.06, 0.10), COL_METAL_STEEL)
        # Mullion in middle (vertical)
        make_box(f"Window_S_{sgn:+d}_Mull", (cx, 0.165, 1.55),
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
        make_box(f"Ceiling_GridX_{i}", (i*1.0, 4.5, CEIL_Z - 0.010),
                 (0.04, 9.4, 0.012), COL_CEILING_GRID)
    for j in range(0, 10):
        make_box(f"Ceiling_GridY_{j}", (0.0, float(j), CEIL_Z - 0.010),
                 (12.4, 0.04, 0.012), COL_CEILING_GRID)
    # Water stains on ceiling tiles — canonical convenience-store
    # detail. Three darker patches at specific tile centres.
    for stain_i, (sx, sy) in enumerate([
        (-2.0, 2.5), (+1.0, 5.5), (+3.0, 7.5),
    ]):
        # a faint blotch, not a dark 0.8 m board (2026-09-24, the user:
        # "furniture on ceilings" — the stains read as slabs)
        make_box(f"Ceiling_Stain_{stain_i}",
                 (sx, sy, CEIL_Z - 0.004),
                 (0.46, 0.38, 0.004),
                 tuple(COL_CEILING_TILE[k] * 0.72 + COL_CEILING_STAIN[k] * 0.28 for k in range(3)) + (1.0,))

    # ── Fluorescent tube fixtures (3 rows of 2 each) ────────────
    for j, ypos in enumerate([2.5, 5.0, 7.5]):
        for i in range(-1, 2):
            xp = i * 2.4
            make_box(f"FluorTube_{j}_{i}",
                     (xp, ypos, CEIL_Z - 0.05),
                     (1.6, 0.36, 0.06), (0.96, 0.96, 0.92, 1.0))
            # Diffuser frame — flush with the ceiling (2026-09-22)
            make_box(f"FluorFrame_{j}_{i}",
                     (xp, ypos, CEIL_Z - 0.01),
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
    # (2026-09-22: the drawer was buried in the counter, the body 2 cm over it)
    make_box("Register_Drawer",
             (cx, cy - 1.20, 1.12),
             (0.50, 0.40, 0.10), (0.22, 0.20, 0.22, 1.0))
    make_box("Register_Body",
             (cx, cy - 1.20, 1.33),
             (0.42, 0.40, 0.32), (0.22, 0.20, 0.22, 1.0))
    make_box("Register_Display",
             (cx - 0.22, cy - 1.20, 1.50),
             (0.04, 0.34, 0.14), (0.10, 0.32, 0.16, 1.0))
    make_box("Register_Keypad",
             (cx, cy - 1.20, 1.18),
             (0.36, 0.36, 0.02), (0.32, 0.32, 0.34, 1.0))

    # ── Hot food case beside register (Hot Pockets canon) ───────
    hcx, hcy = cx, cy - 0.10
    # open to the customer (-X); the glass is two glints
    case_shell("HotCase_Body", (hcx, hcy, 1.30), (0.50, 0.70, 0.60), (0.94, 0.92, 0.84, 1.0), '-X')
    for gi, (gy, gw) in enumerate(((-0.18, 0.02), (-0.10, 0.01))):
        make_box(f"HotCase_Glint_{gi}", (hcx - 0.22, hcy + gy, 1.30), (0.004, gw, 0.56), COL_GLINT)
    # Warm lamp under the top panel (amber glow over the food)
    make_box("HotCase_Lamp", (hcx, hcy, 1.56),
             (0.46, 0.66, 0.04), (1.0, 0.78, 0.32, 1.0))
    # Hot Pockets on the case floor (3 of them)
    for i in range(3):
        hp_y = hcy - 0.24 + i * 0.24
        make_box(f"HotPocket_{i}", (hcx - 0.08, hp_y, 1.06),
                 (0.20, 0.14, 0.08), (0.78, 0.58, 0.40, 1.0))
    # Taquito roller (canon convenience-store fixture) — rods from the
    # back panel toward the opening (they ran 5 cm out through the back)
    for i in range(2):
        make_cyl(f"TaquitoRoller_{i}",
                 (hcx + 0.015, hcy + 0.20 - i * 0.10, 1.42),
                 0.04, 0.43, (0.42, 0.32, 0.20, 1.0), segments=8, axis='X')

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
    # TAPED TO THE EAST WALL above the cig rack (which tops at 2.22):
    # 2026-09-22 they hung half a metre off the wall, in front of the
    # rack, at nothing.
    notice_x = 6.0 - WALL_THICK / 2.0 - 0.01
    notices_data = [
        # (dy_offset, dz_offset, width, height, tint)
        (-1.4, 2.66, 0.28, 0.36, COL_PAPER),         # employment
        (-1.0, 2.66, 0.30, 0.40, COL_PAPER),         # lottery odds
        (-0.6, 2.66, 0.18, 0.20, COL_PAPER_AGED),    # we card
        (-0.2, 2.66, 0.22, 0.28, (0.96, 0.96, 0.62, 1.0)),  # tallboys yellow
        (+0.2, 2.66, 0.16, 0.22, COL_PAPER_AGED),    # no loitering
        (+0.6, 2.66, 0.20, 0.26, (0.86, 0.46, 0.22, 1.0)),  # security cam orange
        (+1.0, 2.66, 0.30, 0.42, COL_PAPER),         # shift schedule
        (+1.4, 2.66, 0.24, 0.30, COL_PAPER),         # food stamps
        # Lower row
        (-1.0, 2.34, 0.22, 0.18, COL_PAPER_AGED),
        (+0.0, 2.34, 0.18, 0.16, COL_PAPER),
        (+0.8, 2.34, 0.20, 0.20, (0.92, 0.74, 0.42, 1.0)),
    ]
    for i, (dy, dz, w, h, tint) in enumerate(notices_data):
        make_box(f"Notice_{i}_Bg",
                 (notice_x, base_y + dy + 1.4, dz),
                 (0.02, w, h), tint)
        # Tiny dark print band (the actual text, abstracted)
        make_box(f"Notice_{i}_Print",
                 (notice_x - 0.0105, base_y + dy + 1.4, dz - 0.04),
                 (0.001, w * 0.7, h * 0.45), COL_METAL_BLACK)
        # Tape strips at corners (just a couple)
        make_box(f"Notice_{i}_TapeTop",
                 (notice_x - 0.0105, base_y + dy + 1.4, dz + h * 0.5 - 0.01),
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
    # MUST sit against the east wall, NOT floating mid-counter. East
    # wall interior face at X=+5.9 (wall centered at X=+6 with
    # WALL_THICK=0.20). Use X=+5.87 so the rack's 2cm-thick steel
    # shelves clear the wall by a hair and SAM (standing at the
    # clerk band, X≈+5.78) has the cig rack BEHIND her, not in her
    # face. Earlier value cx+0.45=+5.45 floated the rack inside the
    # counter front (X∈[4.5,5.5]) and put the top-shelf row at her
    # eye level — that's what the "red panel filling Sam's view"
    # turned out to be.
    cig_x = 5.87
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
        # The case: five panels open to the room, frame foot to top
        # (2026-09-24: a SOLID interior box with every shelf and six-pack
        # modelled inside it, behind an opaque "glass" door — 95 objects
        # per door the camera could never see)
        case_shell(f"Cooler_{i}_Interior", (cx, cy + 0.30, 1.32),
                   (1.30, 0.40, 2.16), COL_COOLER_INTERIOR, '-Y')
        # The "infinite recursion" inner mirror — on the back panel's
        # face, with a slight tint shift
        make_box(f"Cooler_{i}_BackMirror",
                 (cx, cy + 0.4775 - 0.0806, 1.31),
                 (1.20, 0.005, 2.00), (0.18, 0.30, 0.42, 0.85))
        # Glass door: two glints frame to frame (no glass slab)
        for gi, (gx, gw) in enumerate(((-0.34, 0.03), (-0.26, 0.012))):
            make_box(f"Cooler_{i}_Glint_{gi}", (cx + gx, cy + 0.06, 1.30),
                     (gw, 0.004, 2.08), COL_GLINT)
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
        # the plinth to the floor under the box and its door (2026-09-22:
        # the whole cooler hung 20 cm up)
        make_box(f"Cooler_{i}_Plinth",
                 (cx, cy + 0.25, 0.12),
                 (1.30, 0.50, 0.24), (0.20, 0.20, 0.22, 1.0))
        # Handle
        make_box(f"Cooler_{i}_Handle",
                 (cx + 0.60, cy + 0.02, 1.30),
                 (0.02, 0.06, 0.60), COL_METAL_BLACK)
        # Shelves of beer six-packs visible through the glass
        for sh in range(5):
            shz = 0.40 + sh * 0.42
            make_box(f"Cooler_{i}_Shelf_{sh}",
                     (cx, cy + 0.30, shz),
                     (1.26, 0.36, 0.02), COL_METAL_STEEL)   # side panel to side panel
            for b in range(5):
                bx = cx - 0.48 + b * 0.24
                tint = SNACK_TINTS[(i + sh + b) % len(SNACK_TINTS)]
                make_box(f"Cooler_{i}_Sixpack_{sh}_{b}",
                         (bx, cy + 0.30, shz + 0.01 + 0.13),
                         (0.20, 0.22, 0.26), tint)   # on the shelf (it hung 4 cm over it)

    # ── Price tag strip across the top of all coolers ───────────
    for i, cx in enumerate(door_centres):
        # on the top shelf's front lip (2026-09-24: it was stuck to the
        # door glass, which is gone — the glass never rendered as glass)
        make_box(f"Cooler_PriceTag_{i}",
                 (cx, cy + 0.1175, 2.03),
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
             (cx - 0.58, cy, 1.40),   # on the wall (2026-09-22: 3 cm off it)
             (0.04, 3.20, 1.00), (0.86, 0.84, 0.78, 1.0))

    # ── 3 coffee pots (dark / medium / decaf) ───────────────────
    for i, tint in enumerate([
            (0.18, 0.10, 0.06, 1.0),
            (0.32, 0.18, 0.10, 1.0),
            (0.42, 0.32, 0.20, 1.0)]):
        py = cy - 1.20 + i * 0.50
        # Pot
        # (2026-09-22: the pot ON its burner, the burner on the counter —
        # the pot hung 5 cm over the burner; the label goes on the backsplash)
        make_cyl(f"Coffee_Pot_{i}_Body",
                 (cx + 0.05, py, 1.05),
                 0.08, 0.26, COL_GLASS, segments=8)
        make_cyl(f"Coffee_Pot_{i}_Liquid",
                 (cx + 0.05, py, 0.99),
                 0.068, 0.16, tint, segments=8)
        make_cyl(f"Coffee_Pot_{i}_Burner",
                 (cx + 0.05, py, 0.90),
                 0.10, 0.02, COL_METAL_BLACK, segments=10)
        # Handle (small protrusion)
        make_box(f"Coffee_Pot_{i}_Handle",
                 (cx + 0.16, py, 1.05),
                 (0.06, 0.04, 0.10), COL_METAL_BLACK)
        # Label / brand panel above (matching dark/med/decaf labels)
        label_tint = [(0.32, 0.20, 0.10, 1.0),
                       (0.62, 0.42, 0.20, 1.0),
                       (0.96, 0.96, 0.86, 1.0)][i]
        make_box(f"Coffee_Pot_{i}_Label",
                 (cx - 0.5475, py, 1.42),
                 (0.005, 0.18, 0.10), label_tint)

    # (2026-09-23: the twin Slurpee barrels that stood here were a SECOND
    # machine built into build_slurpee_fountain's — barrels through its
    # base. The fountain is the machine; it sits on this counter.)

    # ── Cup stack (next to coffee pots) ─────────────────────────
    for i in range(8):
        make_cyl(f"Coffee_Cup_{i}",
                 (cx + 0.30, cy - 1.10, 0.90 + i * 0.04),   # between the microwave and the lids (2026-09-22)
                 0.04, 0.04, (0.92, 0.86, 0.74, 1.0), segments=10)

    # ── Lid dispenser ───────────────────────────────────────────
    make_cyl("Coffee_LidDispenser",
             (cx + 0.30, cy - 0.85, 0.92),
             0.07, 0.18, COL_METAL_STEEL, segments=8)

    # ── Cream + sugar caddy ─────────────────────────────────────
    # (2026-09-22: it overhung the counter's north AND east edges and
    # sat 4 cm into the top; the pumps stood beside it on air)
    make_box("Coffee_CSC_Body",
             (cx + 0.44, cy + 1.38, 0.96),
             (0.28, 0.40, 0.16), (0.78, 0.68, 0.52, 1.0))
    for i in range(3):
        col = [(0.94, 0.94, 0.94, 1.0),
               (0.32, 0.22, 0.16, 1.0),
               (0.78, 0.74, 0.60, 1.0)][i]
        make_box(f"Coffee_CSC_{i}",
                 (cx + 0.44, cy + 1.28 + i * 0.10, 1.08),
                 (0.10, 0.08, 0.06), col)

    # ── Squeegee + bucket near the coffee station ──────────────
    make_cyl("Mop_Bucket",
             (cx + 0.60 + 0.550, cy + 1.80, 0.20),
             0.18, 0.40, (0.92, 0.86, 0.36, 1.0), segments=10)
    make_box("Mop_Wringer",
             (cx + 0.60 + 0.550, cy + 1.80, 0.42),
             (0.30, 0.30, 0.06), COL_METAL_BLACK)
    # Squeegee handle
    make_cyl("Squeegee_Handle",
             (cx + 0.60 + 0.550, cy + 1.80, 1.20),
             0.020, 1.60, (0.62, 0.32, 0.20, 1.0), segments=8)
    make_box("Squeegee_Head",
             (cx + 0.60 + 0.550, cy + 1.80, 0.42),
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
            for hi, hx in enumerate((-2.4, 2.4)):   # hangers to the ceiling (2026-09-22)
                make_box(f"Aisle_{j}_TopSign_Hanger_{k}_{hi}",
                         (hx, ay + lbl_y_off, (2.62 + CEIL_Z) / 2.0),
                         (0.01, 0.01, CEIL_Z - 2.62), COL_METAL_STEEL)
            # Letter band (cream)
            make_box(f"Aisle_{j}_TopSign_Text_{k}",
                     (0.0, ay + lbl_y_off + (0.033 if k == 0 else -0.033), 2.50),   # on the sign's face (2026-09-25: at ±1 mm the band lay inside the 6 cm sign)
                     (4.6, 0.005, 0.12), label_text_tint)

    # ── End-caps (the small slanted stands near windows, per ref) ──
    # Two end-caps placed near the south windows for cross-traffic
    for sgn, sx in [(-1, -3.40), (+1, +3.40)]:
        # Body (slightly angled — we fake angle with a thinner base)
        make_box(f"EndCap_{sgn:+d}_Base",
                 (sx, 2.35, 0.12),
                 (0.60, 0.80, 0.24), COL_COUNTER_DARK)
        for ui, uy in enumerate((2.35 - 0.36, 2.35 + 0.36)):   # uprights (2026-09-22)
            make_box(f"EndCap_{sgn:+d}_Upright_{ui}", (sx, uy, (0.24 + 2.02) / 2.0),
                     (0.04, 0.04, 2.02 - 0.24), COL_METAL_STEEL)
        # 4 narrow shelves stacked
        for sh in range(4):
            shz = 0.40 + sh * 0.34
            make_box(f"EndCap_{sgn:+d}_Shelf_{sh}",
                     (sx, 2.35, shz),
                     (0.62, 0.70, 0.02), COL_METAL_STEEL)
            # 4 products per shelf (smaller than aisle products)
            for p in range(4):
                px = sx - 0.20 + p * 0.14
                tint = SNACK_TINTS[(sgn + sh + p) % len(SNACK_TINTS)]
                make_box(f"EndCap_{sgn:+d}_Product_{sh}_{p}",
                         (px, 2.35, shz + 0.10),
                         (0.10, 0.50, 0.18), tint)
        # Top header
        make_box(f"EndCap_{sgn:+d}_Header",
                 (sx, 2.35, 1.92),
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
    mrx, mry = -5.30, 2.35   # clear of the coffee counter's south end (2026-09-22: 20 cm into it)
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
    # screen + keypad on the NORTH face — the machine faces the store
    # (2026-09-22: they faced the south wall 70 cm away, and the queue
    # tape line was always on the north side)
    make_box("ATM_Screen", (atm_x, atm_y + 0.20, 1.16),
             (0.32, 0.04, 0.22), (0.18, 0.32, 0.46, 1.0))
    make_box("ATM_Keypad", (atm_x, atm_y + 0.20, 0.92),
             (0.22, 0.04, 0.16), (0.22, 0.22, 0.24, 1.0))
    make_box("ATM_Slot", (atm_x, atm_y + 0.22, 0.74),
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
    make_box("Entry_Mat_Text", (0.0, 0.85, 0.0236),
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
             (bdx + 0.27, bdy, 2.02),   # on the door's upper panel (2026-09-22)
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
    # on the machine's EAST face — the loader side, toward the room
    # (2026-09-25: the sign sat 4 cm inside the west edge against the W
    # wall, and its text had been pushed into the wall)
    make_box("IceMachine_Sign", (cx + 0.56, cy, 1.20),
             (0.02, 0.80, 0.30), COL_ICE_BLUE)
    make_box("IceMachine_SignText", (cx + 0.5731, cy, 1.20),
             (0.005, 0.40, 0.16), COL_PAPER)
    # Floor drain pan at base
    make_box("IceMachine_DrainPan", (cx, cy, 0.04),
             (1.20, 1.30, 0.04), COL_METAL_BLACK)


def build_lottery_display():
    # Lottery scratch-off / Powerball display behind counter, mounted
    # on the east wall above the cig rack (which tops at ~1.95m).
    cx = 6.0 - WALL_THICK / 2.0 - 0.01  # ON the east wall (2026-09-22: it hung 0.4 m off it)
    cy = 4.50 - 2.10  # south end of counter, opposite the register
    base_z = 2.16
    make_box("Lottery_Box", (cx, cy, base_z),
             (0.02, 0.60, 0.40), COL_METAL_STEEL)
    # Yellow signage banner
    make_box("Lottery_BannerYellow", (cx - 0.005, cy, base_z + 0.16),
             (0.005, 0.56, 0.10), COL_LOTTERY_YEL)
    # Red Powerball stripe
    make_box("Lottery_BannerRed", (cx - 0.005 - 0.0081, cy, base_z + 0.04),
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
    cx, cy = 5.20, 1.72
    make_cyl("Trash_Body", (cx, cy, 0.50), 0.30, 1.00, COL_BRAND_RED)
    # Brand band
    make_cyl("Trash_BrandBand", (cx, cy, 0.70), 0.31, 0.16, COL_PAPER)
    # Lid with swing-flap slot
    make_cyl("Trash_Lid", (cx, cy, 1.04), 0.32, 0.04, COL_METAL_BLACK)
    make_box("Trash_FlapSlot", (cx, cy, 1.00),
             (0.32, 0.02, 0.04), COL_METAL_STEEL)


def build_strip_curtain():
    # Plastic strip curtain hanging in stockroom doorway
    # (2026-09-23: the curtain hung at x 4.88, y 8.28-9.28 — a metre from
    # the E wall, 1.3 m north of the only door in it, through the break
    # nook's locker and on into the N wall. The back door is BackDoor, in
    # the E wall at y 7.05-7.95; the curtain hangs in front of it.)
    door_x = 5.90
    door_y = 7.50
    # The stockroom door is built elsewhere; the strip curtain hangs
    # in FRONT of it as 6 PVC slats.
    # (2026-09-22: the doorway is IN the east wall, so the slats hang
    # along Y across it from a rail on the wall's inside face; they used
    # to be spread across the wall's thickness, in the air)
    make_box("StripCurtain_Rail", (door_x - 0.04, door_y, 2.22), (0.04, 1.00, 0.04), COL_METAL_STEEL)   # on the door frame
    for s in range(6):
        sy = door_y - 0.40 + s * 0.16
        make_box(f"StripCurtain_{s}", (door_x - 0.04, sy, 1.40),
                 (0.005, 0.12, 1.60), COL_STRIP_PVC)


def build_counter_impulse_buys():
    # Small high-margin items lined along the counter top east-of-
    # register, where Sam can reach them but the customer must
    # cross the counter to grab. Canon convenience-store layout.
    base_y = 4.5
    base_z = 1.10   # the counter's top face is 1.07; trays centred here sit on it
    # Mint dispenser
    make_box("Counter_MintsTray", (5.10, base_y + 1.20, base_z),
             (0.36, 0.30, 0.06), COL_METAL_STEEL)
    for m in range(6):
        make_box(f"Counter_MintTube_{m}",
                 (5.05 + (m % 3) * 0.10, base_y + 1.20 + (m // 3) * 0.10,
                  base_z + 0.06),
                 (0.04, 0.04, 0.12), SNACK_TINTS[m % len(SNACK_TINTS)])
    # Gum strip rack
    make_box("Counter_GumStrip", (5.10, base_y + 1.65, base_z + 0.02),   # on the counter
             (0.32, 0.20, 0.10), COL_METAL_BLACK)
    for g in range(4):
        gy = base_y + 1.58 + g * 0.06
        make_box(f"Counter_GumPack_{g}",
                 (5.05, gy, base_z + 0.12),
                 (0.05, 0.05, 0.10), SNACK_TINTS[g % len(SNACK_TINTS)])
    # Slim Jim jar — tall clear cylinder on the counter top, jerky
    # sticks visible inside
    make_cyl("Counter_SlimJimJar", (4.80, base_y - 1.70, base_z + 0.14),   # on the counter
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
    make_cyl("Cam_Dome", (cam_x, cam_y, CEIL_Z - 0.06),   # on the ceiling (2026-09-22: 4 cm under it)
             0.12, 0.12, COL_METAL_BLACK)
    make_cyl("Cam_DomeGlass", (cam_x, cam_y, CEIL_Z - 0.12),
             0.10, 0.04, (0.18, 0.20, 0.22, 0.70))
    # Second cam over door
    make_cyl("Cam_Dome2", (0.0, 1.0, CEIL_Z - 0.05),
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
                 (cx + sgn * 0.2025, cy, 0.40),   # on the panel's outer face (2026-09-25: inside it)
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
             (0.0, canopy_y - 2.11 - 0.0431, canopy_z + 0.05),
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
        make_box(f"Pump_{sgn:+d}_Display", (px, canopy_y - 0.26 - 0.0131, 1.20),   # on the body's face
                 (0.40, 0.005, 0.50), COL_PUMP_FACE)
        # Pump body between base and head (2026-09-09: the head hung
        # 1 m above the base with only the display between them)
        make_box(f"Pump_{sgn:+d}_Body", (px, canopy_y, 1.11),
                 (0.44, 0.54, 1.02), COL_PUMP_BODY)
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
                     (px - 0.15 + d_i * 0.15, canopy_y - 0.265 - 0.0081, 1.40),   # on the display's face
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
                 (wx, wy, 0.26), 0.26, 0.20, COL_METAL_BLACK, axis='Y')   # on the asphalt
    # Headlights
    for ws in (-1, +1):
        make_box(f"Car_Headlight_{ws:+d}",
                 (car_x + 0.9025, car_y + ws * 0.32, 0.55),   # on the nose
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
    # (2026-09-23: the cardboard end-cap pyramid is gone — it was built
    # on the SAME spot as the aisle's end-cap shelving (EndCap_-1), its
    # boxes through the shelves and uprights, its bottom tier hanging
    # 25 cm off the floor; and the floor south of it is the window
    # seating. The shelving end cap is the display.)


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
COL_NEON_RED      = (0.86, 0.42, 0.32, 1.0)   # muted neon
COL_NEON_BLUE     = (0.52, 0.68, 0.82, 1.0)
COL_NEON_PINK     = (0.86, 0.54, 0.66, 1.0)
COL_NEON_GREEN    = (0.58, 0.78, 0.54, 1.0)
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
    open_x, open_y, open_z = -3.0, 0.1125, 2.00   # the border tube against the glass at y 0.10
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
                 (open_x + lx, open_y - 0.007, open_z),
                 (0.16, 0.005, 0.18), COL_NEON_RED)
    # Right window — ICE COLD BEER, two lines
    beer_x, beer_y, beer_z = +3.0, 0.1055, 1.70   # against the glass at y 0.10
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
                 (open_x + lx, open_y - 0.007, open_z + 0.62),
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
                 (clock_x + mx, clock_y - 0.025 - 0.0101, clock_z + mz),
                 (0.02, 0.005, 0.02), COL_METAL_BLACK)
    # Hour + minute hands (frozen at 11:47, vol6's canonical hour)
    make_box("Clock_HourHand",
             (clock_x - 0.025, clock_y - 0.030, clock_z + 0.040),
             (0.05, 0.004, 0.10), COL_METAL_BLACK)
    make_box("Clock_MinuteHand",
             (clock_x + 0.080, clock_y - 0.030, clock_z + 0.020),
             (0.16, 0.004, 0.018), COL_METAL_BLACK)
    # ── Fire extinguisher — west wall corner
    ext_x, ext_y = -5.80, 8.20   # against the wall (2026-09-22: 8 cm into it)
    make_cyl("FireExt_Body", (ext_x, ext_y, 0.86), 0.10, 0.50,
             COL_FIRE_RED)
    make_cyl("FireExt_Top", (ext_x, ext_y, 1.20), 0.08, 0.18,
             COL_METAL_BLACK)
    make_box("FireExt_Bracket", (ext_x - 0.04, ext_y, 0.86),
             (0.04, 0.18, 0.50), COL_METAL_STEEL)
    make_box("FireExt_Sign", (-5.8975, ext_y - 0.40, 1.60),   # on the wall
             (0.005, 0.30, 0.30), COL_FIRE_RED)
    # ── Employees-Must-Wash-Hands sign by stockroom door
    make_box("Sign_HandWash", (5.8975, 8.40, 1.80),   # on the wall
             (0.005, 0.40, 0.20), COL_PAPER)
    # ── Calendar (girl, beach, faded — corner-store classic)
    make_box("Calendar", (-5.88, 5.40, 1.70),
             (0.005, 0.40, 0.50), COL_POSTER_FADED)
    make_box("Calendar_GridTop", (-5.88 + 0.002 + 0.0191, 5.40, 1.55),
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
    base_z = 1.03   # the base ON the coffee counter's top at 0.88 (2026-09-23: 27 cm over it)
    # Stainless base
    make_box("Slurpee_Base", (cx, cy, base_z),
             (0.86, 0.50, 0.30), COL_METAL_STEEL)
    # Two clear barrels
    for bs, by_off in [(-1, -0.18), (+1, +0.18)]:
        make_cyl(f"Slurpee_Barrel_{bs:+d}",
                 (cx, cy + by_off, base_z + 0.40),   # on the base (2026-09-23: 6 cm over it)
                 0.16, 0.50, COL_SLURPEE_CASE)
        # Liquid inside (different colour each barrel)
        col = COL_SLURPEE_BLUE if bs < 0 else COL_SLURPEE_RED
        make_cyl(f"Slurpee_Liquid_{bs:+d}",
                 (cx, cy + by_off, base_z + 0.30),
                 0.14, 0.28, col)
        # Top auger cap
        make_cyl(f"Slurpee_Top_{bs:+d}",
                 (cx, cy + by_off, base_z + 0.68),
                 0.16, 0.06, COL_METAL_BLACK)
        # Dispense handle on the customer side (south)
        make_box(f"Slurpee_Handle_{bs:+d}",
                 (cx + 0.16, cy + by_off, base_z + 0.30),   # on the barrel
                 (0.04, 0.06, 0.20), COL_METAL_BLACK)
        # Drip catch tray
        make_box(f"Slurpee_DripTray_{bs:+d}",
                 (cx + 0.18, cy + by_off, base_z + 0.16),
                 (0.16, 0.20, 0.04), COL_METAL_STEEL)
    # Flavor-label header strip across both barrels
    make_box("Slurpee_LabelHeader", (cx - 0.18, cy, base_z + 0.76),   # meets the top caps (2026-09-22)
             (0.04, 0.50, 0.12), COL_BRAND_NAVY)


def build_price_tag_strips():
    # Edge-of-shelf white price strips on each snack aisle shelf.
    # The aisles are at Y=3.5 and Y=5.5 with 5 shelves each. Strips
    # face south on the south aisle, north on the north aisle.
    for ai, ay in enumerate([3.5, 5.5]):
        face_y = ay + (-0.3425 if ai == 0 else +0.3425)   # on the shelf faces (0.34)
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
             (1.20, 0.60, 0.0236),
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
    make_box("Payphone_Hood", (px - 0.16, py, 1.65),   # on the box's top (2026-09-22: 9 cm over it)
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
    # (2026-09-24 re-plan of the NE corner: this stack was placed to be
    # seen "through the strip curtain" into a stockroom the model does
    # not have — the back door is a closed leaf in the E wall — and with
    # a steel backboard and three products half into the N wall, a
    # locker and the trash bag, it was a heap. Three cartons now, stacked
    # in the corner N of the back door, clear of its swing.)
    for ti, (bx_, by_, bz_) in enumerate(((5.66, 8.35, 0.20), (5.66, 8.68, 0.20), (5.66, 8.35, 0.60))):
        make_box(f"Stockroom_Box_{ti}", (bx_, by_, bz_), (0.36, 0.30, 0.40), COL_BOX_KRAFT)


def build_more_floor_displays():
    # Beer 30-rack pyramid south of the cooler row
    bx, by = -2.65, 7.20   # clear of the novelty cooler (2026-09-22: 20 cm into it)
    for layer_i in range(3):
        layer_w = 1.20 - layer_i * 0.30
        layer_d = 0.60 - layer_i * 0.10
        make_box(f"BeerStack_Layer_{layer_i}",
                 (bx, by, 0.15 + layer_i * 0.30),   # case on case, on the floor
                 (layer_w, layer_d, 0.30), COL_BRAND_NAVY)
        # White label band on each layer
        make_box(f"BeerStack_Band_{layer_i}",
                 (bx, by - layer_d / 2 - 0.005, 0.15 + layer_i * 0.30),
                 (layer_w * 0.80, 0.005, 0.08), COL_PAPER)
    # Charcoal-bag pyramid near west window
    cx, cy = -4.55, 2.30
    for li in range(3):
        lw = 0.96 - li * 0.24
        make_box(f"CharcoalStack_{li}",
                 (cx, cy, 0.14 + li * 0.28),   # bag on bag
                 (lw, 0.50, 0.28), COL_METAL_BLACK)
        make_box(f"CharcoalLabel_{li}",
                 (cx, cy - 0.255, 0.14 + li * 0.28),
                 (lw * 0.7, 0.005, 0.10), COL_LOTTERY_RED)
    # Cardboard pyramid of red-cup 12-packs near east window
    cup_x, cup_y = 3.55, 1.55
    for li in range(2):
        lw = 0.80 - li * 0.24
        make_box(f"CupStack_{li}",
                 (cup_x, cup_y, 0.12 + li * 0.24),   # case on case
                 (lw, 0.40, 0.24), COL_BRAND_RED)
    # SALE topper sign
    make_box("CupStack_SaleSign", (cup_x, cup_y - 0.2, 0.57),   # stands on the top case
             (0.40, 0.005, 0.18), COL_LOTTERY_YEL)


def build_atm_detail():
    # Dresses THE ATM from build_floor_props — (4.80, 1.00), body
    # 0.50 x 0.42 x 1.50, screen + keypad on its north face.
    # 2026-09-22: this pass used to draw a phantom keypad, slots and
    # an overhead sign at (-5.4, 2.1) against the west wall, where
    # no machine has stood since v2 — fourteen keys in mid-air.
    ax, ay = 4.80, 1.00
    face_y = ay + 0.21          # the body's north face
    pad_y = ay + 0.22           # the screen/keypad slabs' north face
    # Display highlight on the screen
    make_box("ATM_DisplayHighlight", (ax, pad_y + 0.0025, 1.18),
             (0.20, 0.005, 0.04), COL_LOTTERY_YEL)
    # 4×3 keypad on the keypad slab (z 0.84..1.00)
    for r in range(4):
        for c in range(3):
            make_box(f"ATM_Key_{r}_{c}",
                     (ax - 0.07 + c * 0.07,
                      pad_y + 0.0025,
                      0.87 + r * 0.04),
                     (0.06, 0.005, 0.03), COL_METAL_BLACK)
    # Card slot + receipt slot on the body face
    make_box("ATM_CardSlot", (ax - 0.12, face_y + 0.0025, 0.66),
             (0.10, 0.005, 0.012), COL_METAL_STEEL)
    make_box("ATM_ReceiptSlot", (ax + 0.12, face_y + 0.0025, 0.66),
             (0.10, 0.005, 0.012), COL_METAL_STEEL)
    # Cash dispense slot
    make_box("ATM_CashSlot", (ax, face_y + 0.0025, 0.50),
             (0.22, 0.005, 0.020), COL_METAL_BLACK)
    # Overhead "ATM" sign on a thin bracket from the body's top (1.50)
    make_box("ATM_OverheadBracket", (ax, ay, 1.87),
             (0.04, 0.04, 0.74), COL_METAL_BLACK)
    make_box("ATM_OverheadSign", (ax, ay, 2.30),
             (0.30, 0.04, 0.12), COL_LOTTERY_YEL)
    make_box("ATM_OverheadSignText", (ax, ay + 0.0225, 2.30),
             (0.22, 0.005, 0.06), COL_METAL_BLACK)


def build_air_freshener_tree():
    # A bundle of pine-tree air fresheners hanging above the
    # register on a small wire — classic gas-station accent.
    base_x, base_y = 5.0, 4.5 - 0.40
    base_z = 1.90
    # Suspension wire
    make_box("AirFresh_Wire",
             (base_x, base_y, (base_z + CEIL_Z) / 2.0),
             (0.005, 0.005, CEIL_Z - base_z), COL_METAL_BLACK)   # to the ceiling (2026-09-22)
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
                 (base_x, ty, base_z - 0.09),   # meets the lowest tier (2026-09-22)
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
# POLISH PASS 3 — finer-grain detail + shop-window depth
# Cigarette pack faces (legible brand stripes), donut display
# behind glass, drip-coffee creamer / sugar caddy, a kid's
# soccer-ball display end-cap, fluorescent-tube diffuser strips
# (visible behind the housings), price-window strips on each
# beer-cooler door, dust on the highest shelves (vertex-colour
# darker stripe), trash-bag tied at the back-room door
# threshold, propane-tank exchange cage outside the south
# windows, a pickup truck silhouette beside the canopy column,
# more pump-island details (squeegee bucket, ice bin), a small
# ICE bin chest cooler near the south door, and a couple of
# in-store posters (cigarette ad, gum gum gum).
# ════════════════════════════════════════════════════════════════
COL_BAG_BLACK     = (0.10, 0.10, 0.12, 1.0)
COL_PROPANE_BLUE  = (0.18, 0.32, 0.50, 1.0)
COL_PROPANE_TANK  = (0.92, 0.92, 0.86, 1.0)
COL_TRUCK_BODY    = (0.36, 0.32, 0.30, 1.0)
COL_TRUCK_BED     = (0.20, 0.18, 0.16, 1.0)
COL_DUST          = (0.62, 0.56, 0.42, 1.0)
COL_DONUT_GLAZE   = (0.92, 0.78, 0.46, 1.0)
COL_DONUT_PINK    = (0.96, 0.62, 0.78, 1.0)
COL_DONUT_CHOC    = (0.32, 0.20, 0.12, 1.0)
COL_DONUT_TRAY    = (0.86, 0.86, 0.84, 1.0)
COL_SUGAR_CADDY   = (0.94, 0.94, 0.88, 1.0)
COL_SOCCER_BLK    = (0.10, 0.10, 0.12, 1.0)
COL_SOCCER_WHT    = (0.96, 0.96, 0.92, 1.0)


def build_cigarette_pack_faces():
    # Existing CigBox boxes (12 per shelf × 3 shelves) get a thin
    # darker stripe along their forward face — reads as a brand band
    # at distance. Cig rack lives at X=5.87 (build_counter) — boxes
    # face WEST, so bands sit slightly west of the rack at 5.83.
    cig_x = 5.87   # the boxes' west faces are at 5.88 (2026-09-22: the bands hung 4 cm in front of them)
    cy = 4.50
    for sh in range(3):
        shz = 1.40 + sh * 0.32 + 0.10  # match CigBox center z
        for c in range(12):
            cy_pos = cy - 1.50 + c * 0.28
            # Brand band — dark stripe across the front of each pack
            make_box(f"CigBand_{sh}_{c}",
                     (cig_x + 0.005, cy_pos, shz - 0.04),
                     (0.005, 0.16, 0.04), COL_METAL_BLACK)
            # Health-warning stripe on the bottom (white)
            make_box(f"CigWarn_{sh}_{c}",
                     (cig_x + 0.007, cy_pos, shz - 0.07),
                     (0.005, 0.14, 0.02), COL_PAPER)


def build_donut_display():
    # Glass-front donut case on the coffee counter, west wall.
    # coffee counter is at cx=-5.30, cy=4.50 (per build_coffee_station).
    # Mid-counter between the lid dispenser and the slurpee trays, long
    # axis along the counter, glass to the east (2026-09-22: it stood
    # 0.6 m past the counter's north end, on air; the north end is
    # the slurpee's cups + the cream/sugar unit)
    dx, dy = -4.92, 4.52
    base_z = 0.88  # ON the coffee counter top
    # Case body (metal/glass front)
    case_shell("Donut_CaseBody", (dx, dy, base_z + 0.30), (0.40, 0.86, 0.60), COL_METAL_STEEL, '+X')
    # Front glass: two glints at the opening
    for gi, (gy, gw) in enumerate(((-0.30, 0.02), (-0.22, 0.01))):
        make_box(f"Donut_CaseGlint_{gi}", (dx + 0.18, dy + gy, base_z + 0.30), (0.004, gw, 0.56), COL_GLINT)
    # 3 tiers of donuts inside
    for tier in range(3):
        tray_z = base_z + 0.12 + tier * 0.18
        # Tray
        make_box(f"Donut_Tray_{tier}", (dx - 0.01, dy, tray_z),
                 (0.34, 0.82, 0.02), COL_DONUT_TRAY)   # wall to wall, on the side panels
        # 4 donuts per tier — vary by tier
        donut_colors = [
            [COL_DONUT_GLAZE, COL_DONUT_GLAZE, COL_DONUT_PINK, COL_DONUT_GLAZE],
            [COL_DONUT_CHOC, COL_DONUT_GLAZE, COL_DONUT_CHOC, COL_DONUT_PINK],
            [COL_DONUT_GLAZE, COL_DONUT_PINK, COL_DONUT_GLAZE, COL_DONUT_CHOC],
        ][tier]
        for di, dcol in enumerate(donut_colors):
            d_off_y = -0.12 + di * 0.08
            make_cyl(f"Donut_{tier}_{di}", (dx, dy + d_off_y, tray_z + 0.0225),
                     0.035, 0.025, dcol)
            # Hole in middle (just a darker small box)
            make_cyl(f"Donut_{tier}_{di}_Hole",
                     (dx, dy + d_off_y, tray_z + 0.0235),
                     0.012, 0.025, COL_METAL_BLACK)
    # DONUTS sign on top of case, reading east
    make_box("Donut_Sign", (dx, dy, base_z + 0.68),
             (0.04, 0.84, 0.16), COL_BRAND_RED)
    make_box("Donut_SignText", (dx + 0.022, dy, base_z + 0.68),
             (0.005, 0.60, 0.08), COL_PAPER)


def build_creamer_sugar_caddy():
    # On the coffee counter — coffee station is at cx=-5.30, cy=4.50.
    cx, cy = -5.30, 5.92  # the coffee counter's north end (2026-09-22: it shared space with pot 1, then the lid dispenser; 2026-09-25: then the Slurpee base)
    base_z = 0.92  # ON the coffee counter top (0.88)
    # Sugar caddy — a tray with sugar packet slots and creamer cups
    make_box("Caddy_Tray", (cx, cy, base_z),
             (0.40, 0.30, 0.08), COL_SUGAR_CADDY)
    # Sugar packet slots — vertical dividers
    for di in range(3):
        dx_off = -0.12 + di * 0.12
        make_box(f"Caddy_SugarDivider_{di}",
                 (cx + dx_off, cy, base_z + 0.06),
                 (0.005, 0.26, 0.12), COL_SUGAR_CADDY)
        # Sugar packets (different colours per slot)
        packet_col = [(0.96, 0.92, 0.84, 1.0),  # white sugar
                      (0.82, 0.58, 0.34, 1.0),  # brown
                      (0.42, 0.62, 0.92, 1.0)][di]  # blue (equal)
        for stack in range(4):
            make_box(f"Caddy_Sugar_{di}_{stack}",   # standing in the slot, on the tray (2026-09-22)
                     (cx + dx_off + 0.06, cy - 0.10 + stack * 0.06,
                      base_z + 0.07),
                     (0.005, 0.05, 0.06), packet_col)
    # Stirrer cup
    make_cyl("Caddy_StirrerCup", (cx + 0.16, cy + 0.08, base_z + 0.10),
             0.04, 0.16, COL_METAL_STEEL)
    # Stirrers visible above cup rim
    for st in range(6):
        ang = st * 1.05
        sx = cx + 0.16 + math.cos(ang) * 0.018
        sy = cy + 0.08 + math.sin(ang) * 0.018
        make_box(f"Caddy_Stirrer_{st}", (sx, sy, base_z + 0.20),
                 (0.003, 0.003, 0.18), COL_PAPER)
    # Creamer cups (a stack)
    for cs in range(4):
        make_cyl(f"Caddy_CreamerCup_{cs}",
                 (cx - 0.16, cy + 0.04, base_z + 0.04 + cs * 0.06),
                 0.025, 0.06, COL_PAPER)


def build_endcap_soccer():
    # A small kid's-merch end-cap near the south door — soccer balls
    # in a wire bin. Convenience-store impulse-buy classic.
    bx, by = -1.40, 1.00
    # Wire bin
    make_box("Soccer_Bin", (bx, by, 0.25),   # on the floor
             (0.60, 0.40, 0.50), COL_METAL_STEEL)
    # Three balls poking out the top
    for bi in range(3):
        bx_off = -0.16 + bi * 0.16
        # Use cylinders as approximate spheres
        make_cyl(f"Soccer_Ball_{bi}_Lower",
                 (bx + bx_off, by, 0.54),
                 0.10, 0.08, COL_SOCCER_WHT)
        # Black pentagon patches — abstracted as a contrasting cap
        make_cyl(f"Soccer_Ball_{bi}_Cap",
                 (bx + bx_off, by, 0.58),
                 0.08, 0.04, COL_SOCCER_BLK)
    # Sign topper on two wire posts from the bin's rim (2026-09-22)
    for sgn in (-1, +1):
        make_box(f"Soccer_SignPost_{sgn:+d}", (bx + sgn * 0.27, by, 0.61),
                 (0.02, 0.02, 0.22), COL_METAL_STEEL)
    make_box("Soccer_Sign", (bx, by, 0.79),
             (0.60, 0.04, 0.14), COL_BRAND_RED)
    make_box("Soccer_SignText", (bx, by - 0.022, 0.79),
             (0.42, 0.005, 0.06), COL_PAPER)


def build_diffuser_strips():
    # Long thin light-emitting strips under each fluorescent tube
    # fixture — reads as "the tube is on." The FluorTube boxes
    # already exist at (i*2.4, ypos, CEIL_Z-0.08); add a brighter,
    # thinner strip directly below them.
    for j, ypos in enumerate([2.5, 5.0, 7.5]):
        for i in range(-1, 2):
            xp = i * 2.4
            make_box(f"DiffuserGlow_{j}_{i}",
                     (xp, ypos, CEIL_Z - 0.095),   # under the tube, which is flush now
                     (1.50, 0.16, 0.02), (1.0, 0.96, 0.86, 1.0))


def build_cooler_price_windows():
    # Small white price-window strip on each beer-cooler door —
    # already exists as Cooler_PriceTag at z=2.18. Add a price-
    # number-band below it so the cooler reads as priced merchandise.
    cy = 8.50
    door_centres = [-2.40, -0.80, +0.80, +2.40]
    for i, cx in enumerate(door_centres):
        make_box(f"Cooler_PriceBand_{i}",
                 (cx, cy + 0.1175, 1.96),   # under the price tag, on the shelf lip
                 (0.32, 0.005, 0.04), COL_BRAND_RED)


def build_dust_stripes():
    # Subtle darker stripes on the TOPS of the highest shelves —
    # reads as dust under the fluorescent overhead glare.
    for j, ay in enumerate([3.5, 5.5]):
        for sy_sgn in (-1, +1):
            shz = 0.34 + 4 * 0.40   # top shelf centre; its top face is +0.16
            make_box(f"DustStripe_Aisle{j}_y{sy_sgn:+d}",
                     (0.0, ay + sy_sgn * 0.32, shz + 0.1605),
                     (6.0, 0.04, 0.001), COL_DUST)


def build_trashbag_at_stockroom():
    # Tied-off black trash bag at the stockroom door threshold —
    # Sam's mid-shift "still need to take this out" prop.
    # between the lockers and the cartons (2026-09-24: it stood in a locker)
    bx, by = 5.20, 8.62
    make_cyl("Trashbag_Body", (bx, by, 0.30), 0.20, 0.60, COL_BAG_BLACK)
    # Tied top
    make_cyl("Trashbag_Tie", (bx, by, 0.60), 0.04, 0.06, COL_BAG_BLACK)
    # Slight crinkle — top tier widens
    make_cyl("Trashbag_Crinkle", (bx, by, 0.40), 0.22, 0.20, COL_BAG_BLACK)


def build_propane_cage_outside():
    # Propane-tank exchange cage outside the south door, visible
    # through the windows. Canon gas-station prop.
    cx, cy = -4.00, -1.10
    # Cage frame
    make_box("PropaneCage_Frame", (cx, cy, 0.70),
             (1.20, 0.80, 1.40), COL_METAL_STEEL)
    # Open front (cage bars — abstracted as gaps with vertical bars)
    for vb in range(5):
        bxp = cx - 0.55 + vb * 0.275
        make_box(f"PropaneCage_Bar_{vb}", (bxp, cy - 0.40, 0.70),
                 (0.03, 0.01, 1.40), COL_METAL_STEEL)
    # 6 propane tanks visible inside
    for ti in range(6):
        tcol = ti % 3
        tx = cx - 0.40 + (ti % 3) * 0.40
        tz = 0.20 + (ti // 3) * 0.40      # on the cage floor, stacked
        make_cyl(f"PropaneTank_{ti}", (tx, cy, tz),
                 0.14, 0.40, COL_PROPANE_TANK)
        # Blue collar / brand band
        make_cyl(f"PropaneCollar_{ti}", (tx, cy, tz + 0.16),
                 0.145, 0.06, COL_PROPANE_BLUE)
    # Cage signage panel
    make_box("PropaneCage_Sign", (cx, cy - 0.41, 1.46),
             (1.20, 0.02, 0.14), COL_PROPANE_BLUE)


def build_pickup_truck_outside():
    # A second vehicle silhouette beside the left canopy column —
    # a small pickup truck. Adds depth to the parking-lot scene
    # visible through the south windows. Position chosen to NOT
    # overlap the existing sedan (which is on the right side).
    tx, ty = -3.05, -2.30
    # Cab
    make_box("Truck_Cab", (tx, ty, 0.80),
             (1.20, 1.00, 0.70), COL_TRUCK_BODY)
    make_box("Truck_Roof", (tx, ty, 1.30),
             (1.06, 0.94, 0.30), COL_TRUCK_BODY)
    # Windows
    make_box("Truck_WindowFront", (tx + 0.55, ty, 1.20),
             (0.04, 0.84, 0.30), COL_CAR_WINDOW)
    for ws in (-1, +1):
        make_box(f"Truck_WindowSide_{ws:+d}",
                 (tx, ty + ws * 0.48, 1.20),
                 (1.00, 0.005, 0.30), COL_CAR_WINDOW)
    # Bed (open box rearward of cab)
    make_box("Truck_Bed", (tx - 1.10, ty, 0.72),
             (1.10, 0.96, 0.50), COL_TRUCK_BED)
    make_box("Truck_BedFloor", (tx - 1.10, ty, 0.42),
             (1.20, 1.00, 0.04), COL_TRUCK_BODY)
    # Wheels
    for wx, wy in [(tx - 0.50, ty - 0.48), (tx + 0.50, ty - 0.48),
                   (tx - 1.40, ty - 0.48), (tx - 0.50, ty + 0.48),
                   (tx + 0.50, ty + 0.48), (tx - 1.40, ty + 0.48)]:
        make_cyl(f"Truck_Wheel_{wx:+.1f}_{wy:+.1f}",
                 (wx, wy, 0.24), 0.24, 0.20, COL_METAL_BLACK, axis='Y')   # on the asphalt
    # Headlights
    for ws in (-1, +1):
        make_box(f"Truck_Headlight_{ws:+d}",
                 (tx + 0.6025, ty + ws * 0.32, 0.80),
                 (0.005, 0.16, 0.12), COL_STREETLAMP_LIT)


def build_squeegee_bucket():
    # Squeegee + bucket beside the right pump — gas-station prop.
    px, py = +2.20, -2.80
    make_cyl("Squeegee_Bucket", (px + 0.550, py, 0.20), 0.18, 0.40, COL_METAL_STEEL)
    # Water-blue inside
    make_cyl("Squeegee_Water", (px + 0.550, py, 0.32), 0.16, 0.10, COL_ICE_BLUE)
    # Two squeegee handles sticking out
    for s_off in (-0.06, +0.06):
        make_box(f"Squeegee_Handle_{s_off:+.2f}",
                 (px + s_off + 0.550, py, 0.55),
                 (0.02, 0.02, 0.50), COL_METAL_BLACK)   # in the bucket (started 5 cm above it)
        # Squeegee head
        make_box(f"Squeegee_Head_{s_off:+.2f}",
                 (px + s_off + 0.550, py, 0.81),
                 (0.06, 0.20, 0.06), COL_METAL_STEEL)


def build_ice_chest_outside():
    # Chest-style ICE cooler beside the south door (Visi-Cool style),
    # visible through the window. Outdoor merchandising.
    cx, cy = +0.85, -0.90
    make_box("IceChest_Body", (cx, cy, 0.40),
             (1.20, 0.80, 0.80), COL_ICE_BLUE)
    make_box("IceChest_Lid", (cx, cy, 0.82),
             (1.22, 0.82, 0.04), COL_METAL_STEEL)
    # ICE label band
    make_box("IceChest_Label", (cx, cy - 0.41, 0.50),
             (0.80, 0.005, 0.30), COL_PAPER)
    make_box("IceChest_LabelText", (cx, cy - 0.415, 0.50),
             (0.50, 0.005, 0.16), COL_BRAND_NAVY)


def build_polish_pass_3():
    build_cigarette_pack_faces()
    build_donut_display()
    build_creamer_sugar_caddy()
    build_endcap_soccer()
    build_diffuser_strips()
    build_cooler_price_windows()
    build_dust_stripes()
    build_trashbag_at_stockroom()
    build_propane_cage_outside()
    build_pickup_truck_outside()
    build_squeegee_bucket()
    build_ice_chest_outside()


# ════════════════════════════════════════════════════════════════
# POLISH PASS 4 — counter-side detail + entry-zone clutter
# Per "more passes on store detail." Focuses on the foreground
# half of the store (where Sam's POV camera spends most of its
# time): credit-card terminal, receipt printer paper curl, cash
# drawer open-slot, pizza warmer, donut box stack, hanging chip
# rack, prepaid-card spinner, smoke/vape display, gumball + toy
# machines at entry, bug zapper, coupon dispenser, baseboard
# power-cord run, cigarette urn outside, entry mat dirt detail.
# ════════════════════════════════════════════════════════════════
COL_TERMINAL_GRAY  = (0.32, 0.34, 0.36, 1.0)
COL_TERMINAL_SCRN  = (0.32, 0.46, 0.40, 1.0)   # muted LCD
COL_CASH_GREEN     = (0.48, 0.58, 0.42, 1.0)
COL_PIZZA_ORANGE   = (0.86, 0.62, 0.32, 1.0)
COL_BLACKLIGHT_BLU = (0.46, 0.56, 0.74, 1.0)
COL_GUMBALL_BODY   = (0.74, 0.32, 0.20, 1.0)   # rust
COL_GUMBALL_GLASS  = (0.86, 0.86, 0.84, 0.55)
COL_BLACK_RUBBER   = (0.10, 0.10, 0.10, 1.0)
COL_VAPE_DARK      = (0.18, 0.16, 0.20, 1.0)
COL_VAPE_NEON      = (0.52, 0.72, 0.52, 1.0)   # muted neon


def build_credit_card_terminal():
    # Sits on counter top east of register, customer-facing
    cx, cy = 5.20, 4.5 - 0.30  # south of mid-counter, customer side
    base_z = 1.08
    make_box("CCTerm_Body", (cx, cy, base_z + 0.06),
             (0.18, 0.26, 0.12), COL_TERMINAL_GRAY)
    # Screen
    make_box("CCTerm_Screen", (cx, cy - 0.131, base_z + 0.10),
             (0.12, 0.005, 0.06), COL_TERMINAL_SCRN)
    # PIN pad — 4 rows × 3 cols, laid on the body's top face
    # (2026-09-25: the keys hung in the body's middle, 13 cm inside it)
    for r in range(4):
        for c in range(3):
            make_box(f"CCTerm_Key_{r}_{c}",
                     (cx - 0.05 + c * 0.05, cy - 0.06 + r * 0.035, base_z + 0.12 + 0.0031),
                     (0.04, 0.012, 0.005), COL_PAPER_AGED)
    # Card swipe slot
    make_box("CCTerm_Slot", (cx, cy + 0.13, base_z + 0.06),
             (0.14, 0.005, 0.012), COL_METAL_BLACK)
    # Coiled cord trailing south
    for ci in range(6):
        make_cyl(f"CCTerm_Cord_{ci}",
                 (cx + 0.05 - ci * 0.005,
                  cy - 0.10 - ci * 0.03,
                  base_z + 0.005),
                 0.005, 0.04, COL_METAL_BLACK)


def build_receipt_paper_curl():
    # Paper curl emerging from the existing Receipt_Printer (at
    # cx=5.0, cy-1.50, 1.18 per build_counter)
    rx, ry = 5.0, 4.5 - 1.50
    rz = 1.2325   # the printer's top (1.23) — 2026-09-22: the strip hung 5 cm above it
    # Strip of paper sticking out south then curling
    make_box("ReceiptCurl_Strip",
             (rx, ry - 0.10, rz),
             (0.04, 0.16, 0.005), COL_PAPER)
    # Curl loop — 3 small boxes simulating spiral
    for ci in range(3):
        angle = ci * 0.4
        offx = math.sin(angle) * 0.04
        offz = -ci * 0.012
        make_box(f"ReceiptCurl_Loop_{ci}",
                 (rx + offx, ry - 0.20, rz + offz),
                 (0.04, 0.02, 0.005), COL_PAPER)


def build_cash_drawer_open():
    # The existing Register_Drawer (cx, cy - 1.20, 0.94 per build_counter)
    # gets a "slightly open" tier with bill slots visible.
    dx, dy = 5.0, 4.5 - 1.20
    dz = 0.92
    # Open drawer tray (sticks out west, customer-facing)
    make_box("CashDrawer_Tray", (dx - 0.30, dy, dz),
             (0.50, 0.40, 0.08), COL_COUNTER_DARK)
    # Bill compartments (4 slots) — green for $1 / $5 / $10 / $20
    for bi, bcol in enumerate([
            (0.42, 0.60, 0.42, 1.0),  # $1
            (0.62, 0.74, 0.58, 1.0),  # $5
            (0.58, 0.68, 0.50, 1.0),  # $10
            (0.46, 0.62, 0.46, 1.0)]):  # $20
        make_box(f"CashDrawer_Bills_{bi}",
                 (dx - 0.40 + bi * 0.10, dy, dz + 0.05),
                 (0.08, 0.30, 0.02), bcol)
    # Coin tray (north end)
    for ci_color, cv in enumerate([
            (0.84, 0.74, 0.32, 1.0),   # pennies/quarters
            (0.74, 0.74, 0.74, 1.0),
            (0.62, 0.58, 0.42, 1.0),
            (0.86, 0.86, 0.86, 1.0)]):
        make_box(f"CashDrawer_Coins_{ci_color}",
                 (dx + 0.18, dy - 0.14 + ci_color * 0.08, dz + 0.05),
                 (0.08, 0.06, 0.015), cv)


def build_pizza_warmer():
    # Counter-mounted pizza warmer beside the existing hot food case
    # (HotCase at cx, cy-0.10, 1.30 in build_counter)
    px, py = 5.0, 4.5 + 0.70
    base_z = 1.20
    case_shell("Pizza_CaseBody", (px, py, base_z), (0.50, 0.50, 0.42), COL_METAL_STEEL, '-X')
    # Glass front: two glints at the opening
    for gi, (gy, gw) in enumerate(((-0.14, 0.02), (-0.07, 0.01))):
        make_box(f"Pizza_Glint_{gi}", (px - 0.24, py + gy, base_z), (0.004, gw, 0.38), COL_GLINT)
    # 3 round pizzas on the case floor, side by side (28 cm pans on
    # 16 cm centres overlapped each other and the case sides)
    for pi, py_off in enumerate([-0.15, 0.0, +0.15]):
        make_cyl(f"Pizza_Pan_{pi}", (px, py + py_off, base_z - 0.18),
                 0.07, 0.02, COL_METAL_STEEL)
        # Pizza (cheese-orange)
        make_cyl(f"Pizza_Cheese_{pi}", (px, py + py_off, base_z - 0.164),
                 0.06, 0.012, COL_PIZZA_ORANGE)
        # 4 pepperoni dots
        for di in range(4):
            ang = di * 1.57
            dx2 = math.cos(ang) * 0.032
            dy2 = math.sin(ang) * 0.032
            make_cyl(f"Pizza_Pep_{pi}_{di}",
                     (px + dx2, py + py_off + dy2, base_z - 0.1555 + 0.0286),
                     0.014, 0.005, (0.74, 0.18, 0.16, 1.0))
    # Heat lamp glow, under the top panel
    make_box("Pizza_HeatLamp", (px, py, base_z + 0.17),
             (0.46, 0.46, 0.04), (1.0, 0.74, 0.34, 1.0))
    # PIZZA label, on the case top
    make_box("Pizza_Sign", (px, py, base_z + 0.23),
             (0.50, 0.50, 0.04), COL_BRAND_RED)


def build_donut_box_stack():
    # Cardboard donut boxes stacked on the coffee counter
    bx, by = -5.20, 5.30
    base_z = 0.92
    for li in range(3):
        make_box(f"DonutBox_{li}", (bx, by, base_z + li * 0.08),
                 (0.36, 0.36, 0.08), COL_BOX_KRAFT)
        # Logo strip
        make_box(f"DonutBox_Label_{li}",
                 (bx, by - 0.181, base_z + li * 0.08),
                 (0.28, 0.005, 0.04), COL_BRAND_RED)


def build_hanging_chip_rack():
    # Wall-mounted peg-board with bags of chips hanging from hooks.
    # Mounts on west wall above the coffee counter (X=-5.85, Y=6.6 north).
    cx = -5.85
    cy = 6.50
    base_z = 1.80
    # Pegboard panel
    make_box("PegBoard_Panel", (cx, cy, base_z),
             (0.04, 1.20, 0.80), (0.86, 0.74, 0.58, 1.0))
    # Hooks + chip bags — 3 rows × 4 columns
    for r in range(3):
        for c in range(4):
            hook_y = cy - 0.42 + c * 0.28
            hook_z = base_z + 0.30 - r * 0.24
            # Hook
            make_cyl(f"PegHook_{r}_{c}",
                     (cx + 0.02, hook_y, hook_z),
                     0.005, 0.06, COL_METAL_STEEL, axis='Y')
            # Chip bag (varies by tint cycle)
            tint = SNACK_TINTS[(r * 4 + c) % len(SNACK_TINTS)]
            make_box(f"PegBag_{r}_{c}",
                     (cx + 0.0275, hook_y, hook_z - 0.06),   # against its hook
                     (0.005, 0.16, 0.20), tint)


def build_prepaid_card_spinner():
    # Rotating wire spinner of prepaid phone / lottery / gift cards
    # near the front door. Common gas-station impulse fixture.
    sx, sy = 1.50, 1.20
    base_z = 0.40
    # Vertical pole
    # (2026-09-22: the pole stands ON its base — it started 34 cm above it)
    make_box("Spinner_Pole", (sx, sy, (base_z - 0.34 + base_z + 1.00) / 2.0),
             (0.04, 0.04, 1.34), COL_METAL_STEEL)
    # Base
    make_box("Spinner_Base", (sx, sy, base_z - 0.36),
             (0.30, 0.30, 0.04), COL_METAL_STEEL)
    # 4 rows of card carriers
    for r in range(4):
        rz = base_z + 0.20 + r * 0.22
        # Wire ring at each level (2026-09-22: it exists now — the cards
        # hung on the idea of one)
        from _props.geometry import make_lathe as _ml
        _ml(f"Spinner_Ring_{r}", (sx, sy, rz + 0.04), [(0.175, 0.0), (0.185, 0.006), (0.175, 0.012)], COL_METAL_STEEL, segments=16, loop=True)
        for ai in range(8):
            ang = ai * (math.pi * 2 / 8)
            cx2 = sx + math.cos(ang) * 0.18
            cy2 = sy + math.sin(ang) * 0.18
            # Card hanging on the wire
            tint = SNACK_TINTS[(r + ai) % len(SNACK_TINTS)]
            make_box(f"Spinner_Card_{r}_{ai}",
                     (cx2, cy2, rz),
                     (0.06, 0.005, 0.10), tint)


def build_quarter_machines():
    # Three quarter-machines (gumball / sticker / temporary tattoo)
    # in a row near the south door, west of the entry mat.
    for mi, mx in enumerate([1.90, 2.30, 2.70]):   # east of the entry mat (2026-09-22: they stood in the window tables' chairs)
        my = 0.30   # clear of the wall's inner face (2026-09-22: 6 cm into it, the coin slot inside the plaster)
        # Body
        make_box(f"Quarter_{mi}_Body", (mx, my, 0.50),
                 (0.36, 0.36, 1.00), COL_GUMBALL_BODY)
        # Glass globe top
        make_cyl(f"Quarter_{mi}_Globe", (mx, my, 1.20),
                 0.20, 0.40, COL_GUMBALL_GLASS, axis='Z')
        # Gumballs inside (varied tints)
        for gi in range(6):
            gx = mx + (gi % 3 - 1) * 0.08
            gy_off = (gi // 3 - 0.5) * 0.10
            gz = 1.10 + (gi % 2) * 0.10
            tint = SNACK_TINTS[(mi + gi) % len(SNACK_TINTS)]
            make_cyl(f"Quarter_{mi}_Ball_{gi}",
                     (gx, my + gy_off, gz),
                     0.06, 0.06, tint, axis='Y')
        # Coin slot
        make_box(f"Quarter_{mi}_Slot", (mx, my - 0.18, 0.60),
                 (0.10, 0.005, 0.02), COL_METAL_BLACK)
        # Crank handle
        make_cyl(f"Quarter_{mi}_Crank", (mx + 0.18, my, 0.50),
                 0.05, 0.04, COL_METAL_BLACK, axis='X')


def build_vape_smoke_kiosk():
    # Small black-glass kiosk behind counter, north of the register,
    # displaying vape pens and rolling papers. East-wall flush.
    kx, ky = 5.84, 5.80
    base_z = 1.20
    # Body
    # a shallow shell open to the west (the pens were INSIDE a solid 6 cm
    # body, behind an opaque glass slab)
    case_shell("Vape_KioskBody", (kx, ky, base_z), (0.06, 0.80, 1.10), COL_VAPE_DARK, '-X', wall=0.015)
    for gi, (gy, gw) in enumerate(((-0.30, 0.02), (-0.22, 0.01))):
        make_box(f"Vape_Glint_{gi}", (kx - 0.028, ky + gy, base_z), (0.004, gw, 1.07), COL_GLINT)
    # Stacked vape pens on 3 shelves
    for sh in range(3):
        shz = base_z - 0.40 + sh * 0.34
        for c in range(5):
            cx2 = ky - 0.32 + c * 0.16
            tint = SNACK_TINTS[(sh + c) % len(SNACK_TINTS)]
            make_box(f"VapePen_{sh}_{c}",
                     (kx + 0.0125, cx2, shz),   # on the back panel
                     (0.005, 0.04, 0.16), tint)
    # Neon green VAPE sign
    make_box("Vape_NeonSign", (kx - 0.02, ky, base_z + 0.60),   # on the kiosk's top
             (0.005, 0.60, 0.10), COL_VAPE_NEON)


def build_bug_zapper():
    # Wall-mounted bug zapper near the beer cooler row — UV blue tubes
    # in a wire cage. Canon convenience-store summer prop.
    bx, by, bz = -4.20, 8.85, 2.20
    # Cage
    make_box("BugZap_Cage", (bx, by, bz),
             (0.50, 0.10, 0.30), COL_METAL_STEEL)
    # Blue tubes inside (2)
    for ti in range(2):
        make_box(f"BugZap_Tube_{ti}",
                 (bx, by - 0.04 - 0.0131, bz + 0.06 - ti * 0.12),
                 (0.46, 0.005, 0.04), COL_BLACKLIGHT_BLU)
    # Wire grille (4 horizontal bars)
    for wi in range(4):
        make_box(f"BugZap_GrilleH_{wi}",
                 (bx, by - 0.05, bz + 0.12 - wi * 0.08),
                 (0.50, 0.005, 0.005), COL_METAL_STEEL)


def build_coupon_dispenser():
    # Small red-LED price-dispenser unit on the counter — blinks like
    # a grocery-aisle in-shelf coupon broadcaster.
    cx, cy = 5.10, 4.5 + 0.40
    base_z = 1.10
    make_box("Coupon_Body", (cx, cy, base_z + 0.06),
             (0.16, 0.18, 0.12), COL_TERMINAL_GRAY)
    # Red LED matrix face
    make_box("Coupon_Screen", (cx, cy - 0.091, base_z + 0.08),
             (0.12, 0.005, 0.08), COL_LOTTERY_RED)
    # Price tear-off pad below
    make_box("Coupon_TearPad", (cx, cy + 0.10, base_z + 0.005),
             (0.14, 0.06, 0.010), COL_PAPER)


def build_baseboard_cord_run():
    # Black power cord running along the baseboard from outlet on
    # west wall (build_electrical_conduit at 4.00 Y) east to the
    # coffee station base.
    cord_z = 0.06
    # West wall vertical run — connects outlet at Y=4.0 to floor
    make_box("Cord_VertW", (-5.88, 4.00, cord_z + 0.08),
             (0.02, 0.02, 0.16), COL_METAL_BLACK)
    # Horizontal run along baseboard, west to coffee
    for ci in range(8):
        x_off = -5.78 + ci * 0.10
        make_box(f"Cord_Horiz_{ci}",
                 (x_off, 4.00 + ci * 0.04, cord_z),
                 (0.10, 0.02, 0.02), COL_METAL_BLACK)


def build_cigarette_urn_outside():
    # Sand-topped cigarette urn outside the front door, south.
    ux, uy = -1.20, -0.40
    make_cyl("CigUrn_Body", (ux, uy, 0.40),
             0.14, 0.80, COL_METAL_STEEL)
    # Sand top
    make_cyl("CigUrn_Sand", (ux, uy, 0.81),
             0.13, 0.04, (0.72, 0.62, 0.42, 1.0))
    # A few cigarette butts in the sand
    for bi in range(5):
        ang = bi * 1.25
        bx = ux + math.cos(ang) * 0.06
        by = uy + math.sin(ang) * 0.06
        make_box(f"CigUrn_Butt_{bi}",
                 (bx, by, 0.84),
                 (0.012, 0.012, 0.04), COL_PAPER_AGED)


def build_entry_mat_grime():
    # Black entry-zone rubber tracking mat with visible dirt streaks.
    # Sits just inside the south door.
    mx, my = 0.0, 1.20
    make_box("EntryMat_Body", (mx, my, 0.012),
             (3.00, 1.20, 0.010), COL_BLACK_RUBBER)
    # WELCOME text band (light tan)
    make_box("EntryMat_Welcome", (mx, my, 0.0231),
             (2.20, 0.20, 0.001), (0.72, 0.62, 0.42, 1.0))
    # Dirt streaks (3 darker patches)
    for di in range(6):
        sx = (di - 2.5) * 0.40
        make_box(f"EntryMat_Dirt_{di}",
                 (sx, my + (di % 2) * 0.20 - 0.10, 0.0236),
                 (0.18, 0.14, 0.002), (0.32, 0.26, 0.18, 1.0))


def build_polish_pass_4():
    build_credit_card_terminal()
    build_receipt_paper_curl()
    build_cash_drawer_open()
    build_pizza_warmer()
    build_donut_box_stack()
    build_hanging_chip_rack()
    build_prepaid_card_spinner()
    build_quarter_machines()
    build_vape_smoke_kiosk()
    build_bug_zapper()
    build_coupon_dispenser()
    build_baseboard_cord_run()
    build_cigarette_urn_outside()
    build_entry_mat_grime()


# ════════════════════════════════════════════════════════════════
# POLISH PASS 5 — break the box silhouette
# Per "still way too boxy." Adds CYLINDRICAL props (bottles, cans,
# pipes, posts), EDGE TRIM to existing flat surfaces (counter
# bullnose, crown molding, baseboard quarter-round), and SMALL
# DENSE variation to repeated-box rows. ~150 new objects, mostly
# cylinders — cuts the everything-is-an-AABB read.
# ════════════════════════════════════════════════════════════════
COL_BOTTLE_COKE     = (0.74, 0.28, 0.20, 1.0)   # muted rust-red
COL_BOTTLE_PEPSI    = (0.34, 0.42, 0.58, 1.0)   # dusty navy
COL_BOTTLE_SPRITE   = (0.46, 0.58, 0.42, 1.0)   # sage green
COL_BOTTLE_CAP      = (0.92, 0.92, 0.88, 1.0)
COL_CAN_BUDLIGHT    = (0.42, 0.52, 0.62, 1.0)   # muted blue-grey
COL_CAN_REDBULL     = (0.36, 0.42, 0.54, 1.0)   # dusty navy
COL_CAN_ENERGY      = (0.48, 0.58, 0.34, 1.0)   # olive
COL_ALUM_LID        = (0.78, 0.80, 0.82, 1.0)
COL_CROWN_MOLD      = (0.74, 0.62, 0.42, 1.0)   # warm wood
COL_BOLLARD_YEL     = (0.84, 0.68, 0.28, 1.0)   # muted amber
COL_PLANT_GREEN     = (0.42, 0.52, 0.36, 1.0)   # sage
COL_PLANT_POT       = (0.46, 0.34, 0.22, 1.0)
COL_BROOM_HANDLE    = (0.62, 0.46, 0.30, 1.0)
COL_BROOM_BRUSH     = (0.74, 0.62, 0.42, 1.0)
COL_PVC_WHITE       = (0.86, 0.84, 0.78, 1.0)   # cream
COL_RUBBER_GASKET   = (0.12, 0.12, 0.14, 1.0)


def build_counter_bullnose():
    # Rounded front edge on the counter top — simulated with a thin
    # cylinder running along the west face of the counter top
    # (Counter_Top spans X∈[4.45, 5.55], Y∈[2.25, 6.75], top Z=1.07).
    # Cylinder axis along Y, hugging the west top edge.
    cx_edge = 4.45
    for seg in range(8):
        seg_y = 2.30 + seg * 0.56
        make_cyl(f"Counter_Bullnose_{seg}",
                 (cx_edge, seg_y, 1.04),
                 0.025, 0.56, COL_COUNTER_TOP, axis='Y', segments=8)


def build_crown_molding():
    # Crown molding strip at the top of all four walls — half-round
    # cylinder along ceiling junction. Reads as warm wood trim.
    # West + East walls
    for sgn, xpos in [(-1, -5.90), (+1, +5.90)]:
        for seg in range(9):
            seg_y = 0.50 + seg * 1.00
            make_cyl(f"Crown_X{sgn:+d}_{seg}",
                     (xpos, seg_y, CEIL_Z - 0.06),
                     0.04, 1.00, COL_CROWN_MOLD, axis='Y', segments=6)
    # North wall
    for seg in range(12):
        seg_x = -5.50 + seg * 1.00
        make_cyl(f"Crown_N_{seg}",
                 (seg_x, 8.90, CEIL_Z - 0.06),
                 0.04, 1.00, COL_CROWN_MOLD, axis='X', segments=6)
    # South wall (skipping centre door span X∈[-1.5, +1.5])
    for seg in range(12):
        seg_x = -5.50 + seg * 1.00
        if -1.7 < seg_x < 1.7:
            continue   # door opening
        make_cyl(f"Crown_S_{seg}",
                 (seg_x, 0.10, CEIL_Z - 0.06),
                 0.04, 1.00, COL_CROWN_MOLD, axis='X', segments=6)


def build_baseboard_quarter_round():
    # Quarter-round shoe-molding strip where the baseboard meets the
    # floor on all four walls. Tiny cylinders running along the
    # baseline. Adds depth to the floor/wall junction.
    for sgn, xpos in [(-1, -5.85), (+1, +5.85)]:
        for seg in range(9):
            seg_y = 0.50 + seg * 1.00
            make_cyl(f"QtrRound_X{sgn:+d}_{seg}",
                     (xpos, seg_y, 0.018),
                     0.018, 1.00, COL_WALL_BASEBOARD, axis='Y', segments=6)
    for seg in range(12):
        seg_x = -5.50 + seg * 1.00
        make_cyl(f"QtrRound_N_{seg}",
                 (seg_x, 8.85, 0.018),
                 0.018, 1.00, COL_WALL_BASEBOARD, axis='X', segments=6)


def build_soda_bottle_pyramid():
    # 2L bottle pyramid on a foreground end-cap — replaces a generic
    # cardboard pyramid with proper cylindrical bottle stack.
    bx, by = -1.40, 2.60
    base_z = 0.40
    # the riser the bottom tier stands on (2026-09-22: the pyramid
    # began 25 cm above the floor)
    make_box("SodaPyr_Riser", (bx, by, 0.125), (0.84, 0.30, 0.25), COL_BOX_KRAFT)
    bottles = [
        (COL_BOTTLE_COKE,   COL_BOTTLE_CAP),
        (COL_BOTTLE_PEPSI,  COL_BOTTLE_CAP),
        (COL_BOTTLE_SPRITE, COL_BOTTLE_CAP),
    ]
    # Tier 0 — 4 bottles
    for i in range(4):
        col, capcol = bottles[i % 3]
        # 2-liter silhouette: body + shoulder-neck + cap (was a fat
        # straight tube - "all the bottles are cubes")
        make_cyl(f"SodaPyr_T0_{i}", (bx - 0.30 + i * 0.20, by, base_z - 0.045),
                 0.048, 0.21, col)
        make_cyl(f"SodaPyr_T0_Neck_{i}", (bx - 0.30 + i * 0.20, by, base_z + 0.095),
                 0.020, 0.07, col)
        make_cyl(f"SodaPyr_T0_Cap_{i}", (bx - 0.30 + i * 0.20, by, base_z + 0.145),
                 0.022, 0.025, capcol)
    # boards the upper tiers stand on (over the caps below; 2026-09-22)
    make_box("SodaPyr_Board_0", (bx - 0.05, by, base_z + 0.16), (0.76, 0.24, 0.02), COL_BOX_KRAFT)
    make_box("SodaPyr_Board_1", (bx, by, base_z + 0.48), (0.56, 0.24, 0.02), COL_BOX_KRAFT)
    # Tier 1 — 3 bottles (offset)
    for i in range(3):
        col, capcol = bottles[(i + 1) % 3]
        # 2-liter silhouette: body + shoulder-neck + cap (was a fat
        # straight tube - "all the bottles are cubes")
        make_cyl(f"SodaPyr_T1_{i}", (bx - 0.20 + i * 0.20, by, base_z + 0.32 - 0.045),
                 0.048, 0.21, col)
        make_cyl(f"SodaPyr_T1_Neck_{i}", (bx - 0.20 + i * 0.20, by, base_z + 0.32 + 0.095),
                 0.020, 0.07, col)
        make_cyl(f"SodaPyr_T1_Cap_{i}", (bx - 0.20 + i * 0.20, by, base_z + 0.32 + 0.145),
                 0.022, 0.025, capcol)
    # Tier 2 — 2 bottles
    for i in range(2):
        col, capcol = bottles[i]
        # 2-liter silhouette: body + shoulder-neck + cap (was a fat
        # straight tube - "all the bottles are cubes")
        make_cyl(f"SodaPyr_T2_{i}", (bx - 0.10 + i * 0.20, by, base_z + 0.64 - 0.045),
                 0.048, 0.21, col)
        make_cyl(f"SodaPyr_T2_Neck_{i}", (bx - 0.10 + i * 0.20, by, base_z + 0.64 + 0.095),
                 0.020, 0.07, col)
        make_cyl(f"SodaPyr_T2_Cap_{i}", (bx - 0.10 + i * 0.20, by, base_z + 0.64 + 0.145),
                 0.022, 0.025, capcol)
    # Topper SALE banner
    make_box("SodaPyr_Topper", (bx, by, base_z + 0.88),      # on the top tier's caps
             (0.50, 0.30, 0.16), COL_LOTTERY_YEL)


def build_can_arrays_on_cooler_shelves():
    # Replace some of the existing six-pack boxes in the cooler with
    # tighter cylindrical can arrays — reads as "12-pack stacked of
    # cans" not "vague box." Layer additional cans IN FRONT of the
    # existing Cooler_Sixpack boxes so the shelves look denser.
    cy = 8.50
    door_centres = [-2.40, -0.80, +0.80, +2.40]
    can_colors = [COL_CAN_BUDLIGHT, COL_CAN_REDBULL, COL_CAN_ENERGY,
                  (0.62, 0.18, 0.16, 1.0), (0.18, 0.62, 0.46, 1.0)]
    for di, cx in enumerate(door_centres):
        for sh in range(5):
            shz = 0.42 + sh * 0.42
            ccol = can_colors[(di + sh) % len(can_colors)]
            for b in range(6):
                bx2 = cx - 0.50 + b * 0.20
                make_cyl(f"CoolerCan_{di}_{sh}_{b}",
                         (bx2, cy + 0.16, shz + 0.08),
                         0.04, 0.16, ccol)
                # Aluminum lid
                make_cyl(f"CoolerCanLid_{di}_{sh}_{b}",
                         (bx2, cy + 0.16, shz + 0.16),
                         0.04, 0.01, COL_ALUM_LID)


def build_register_recess_detail():
    # The register body is a solid block — break its silhouette with
    # a slight recess where the keypad sits, and add small cylindrical
    # bezel details around the screen.
    rx, ry = 5.0, 4.5 - 1.20
    rz = 1.25
    # Screen bezel (rounded corners suggested by small cylinders)
    for sgn_x, sgn_z in [(-1, -1), (+1, -1), (-1, +1), (+1, +1)]:
        make_cyl(f"Register_Bezel_{sgn_x:+d}_{sgn_z:+d}",
                 (rx - 0.22, ry - 0.15 * sgn_x, rz + 0.16 + 0.06 * sgn_z),
                 0.012, 0.024, (0.62, 0.42, 0.18, 1.0))
    # Receipt-feed tube on top of the register
    make_cyl("Register_ReceiptTube", (rx, ry, rz + 0.22),
             0.025, 0.10, COL_METAL_STEEL)


def build_yellow_bollards_outside():
    # Three yellow safety bollards outside the south door — concrete-
    # filled steel posts. Canon convenience-store curb detail.
    for bi, bx in enumerate([-2.40, 0.0, +2.40]):
        by = -0.40
        # Cylinder
        make_cyl(f"Bollard_{bi}", (bx, by, 0.42),
                 0.10, 0.84, COL_BOLLARD_YEL)
        # Concrete base ring
        make_cyl(f"BollardBase_{bi}", (bx, by, 0.04),
                 0.14, 0.06, COL_METAL_STEEL)
        # Black scuff stripe (cars bump these)
        make_cyl(f"BollardScuff_{bi}", (bx, by, 0.30),
                 0.11, 0.06, COL_METAL_BLACK)


def build_drink_fridge_handles():
    # Cylindrical pull handles on each cooler door, replacing the
    # existing boxy Cooler_Handle. Existing handles stay (they're
    # at cx+0.60); add a SECOND grab-rail style horizontal cylinder
    # below them for two-hand-friendly pulls.
    cy = 8.50
    door_centres = [-2.40, -0.80, +0.80, +2.40]
    for i, cx in enumerate(door_centres):
        make_cyl(f"CoolerGrab_{i}", (cx + 0.62, cy + 0.03, 0.60),
                 0.014, 0.18, COL_METAL_STEEL, axis='X', segments=8)
        # Rubber gasket trim along door perimeter (top + bottom)
        for sgn in (-1, +1):
            make_cyl(f"CoolerGasket_{i}_{sgn}",
                     (cx, cy + 0.05, 1.30 + sgn * 1.04),
                     0.008, 1.20, COL_RUBBER_GASKET, axis='X')


def build_floor_plant():
    # Decorative potted plant near the front door — fake green plant
    # in a terracotta pot. Cheap convenience-store dressing.
    px, py = -5.00, 0.45
    # Pot
    for r_layer in range(3):
        make_cyl(f"Plant_Pot_{r_layer}",
                 (px, py, 0.20 + r_layer * 0.06),
                 0.18 - r_layer * 0.02, 0.06, COL_PLANT_POT)
    # Leaves (multiple stacked cylinders)
    leaf_z_levels = [0.42, 0.50, 0.58, 0.64]
    for li, lz in enumerate(leaf_z_levels):
        for ang_i in range(6):
            ang = ang_i * (math.pi * 2.0 / 6.0) + li * 0.3
            ox = math.cos(ang) * 0.16
            oy = math.sin(ang) * 0.16
            make_cyl(f"Plant_Leaf_{li}_{ang_i}",
                     (px + ox, py + oy, lz),
                     0.04, 0.08, COL_PLANT_GREEN)


def build_broom_and_mop():
    # Broom + mop against the N wall between the last cooler and the break
    # bench (2026-09-24: at (4.40, 8.40) both stood through the bench)
    bx, by = 3.70, 8.78
    # Broom
    # out of the door's swing (2026-09-24, the user: doorways obstructed)
    make_cyl("Broom_Handle", (bx + 0.550, by, 0.80),
             0.018, 1.60, COL_BROOM_HANDLE, axis='Z')
    # Slight lean (offset along Y at top — abstracted by a second cylinder)
    make_cyl("Broom_HandleTop", (bx + 0.04 + 0.550, by, 1.46),
             0.018, 0.30, COL_BROOM_HANDLE, axis='Z')
    # Brush head
    make_box("Broom_Brush", (bx + 0.550, by, 0.06),
             (0.28, 0.06, 0.10), COL_BROOM_BRUSH)
    # Mop (next to broom)
    mx = bx - 0.16
    make_cyl("Mop_Handle", (mx + 0.550, by, 0.80),
             0.018, 1.60, COL_METAL_STEEL, axis='Z')
    make_box("Mop_Head", (mx + 0.550, by, 0.08),
             (0.18, 0.20, 0.10), (0.82, 0.78, 0.72, 1.0))


def build_pipes_along_ceiling():
    # White PVC pipes running along the ceiling — water lines for the
    # bathroom + ice machine. Adds linear cylindrical visual interest
    # against the flat ceiling.
    # East-west run at Y=4.5, Z=2.92
    for seg in range(12):
        seg_x = -5.50 + seg * 1.00
        make_cyl(f"Pipe_EW_{seg}",
                 (seg_x, 4.50, CEIL_Z - 0.10),
                 0.03, 1.00, COL_PVC_WHITE, axis='X', segments=6)
    # N-S branch at X=-5.40 (down to ice machine)
    for seg in range(4):
        seg_y = 1.80 + seg * 1.00
        make_cyl(f"Pipe_NS_{seg}",
                 (-5.40, seg_y, CEIL_Z - 0.10),
                 0.03, 1.00, COL_PVC_WHITE, axis='Y', segments=6)
    # Vertical drop from EW pipe to NS branch (elbow joint area)
    make_cyl("Pipe_Elbow_1", (-5.40, 4.50, CEIL_Z - 0.10),
             0.04, 0.06, COL_PVC_WHITE)


def build_otc_meds_display():
    # Small over-the-counter medicine display on a counter-top
    # standalone shelf — cluster of small cylindrical bottles
    # (aspirin / pain relief / antacid). High-margin impulse items.
    sx, sy = 4.85, 4.5 - 1.85
    base_z = 1.10
    # Wire shelf base
    make_box("OTC_ShelfBase", (sx, sy, base_z),
             (0.24, 0.20, 0.02), COL_METAL_STEEL)
    # Two tiers
    for tier in range(2):
        tz = base_z + 0.12 + tier * 0.14
        make_box(f"OTC_ShelfTier_{tier}", (sx, sy, tz - 0.06),
                 (0.24, 0.20, 0.02), COL_METAL_STEEL)
        # 6 small bottles per tier
        for bi in range(6):
            bx2 = sx - 0.08 + (bi % 3) * 0.08
            by2 = sy - 0.06 + (bi // 3) * 0.12
            bot_color = [(0.18, 0.32, 0.62, 1.0),
                         (0.62, 0.18, 0.18, 1.0),
                         (0.42, 0.62, 0.32, 1.0),
                         (0.92, 0.78, 0.32, 1.0),
                         (0.82, 0.82, 0.82, 1.0),
                         (0.62, 0.42, 0.18, 1.0)][bi % 6]
            make_cyl(f"OTC_Bottle_{tier}_{bi}",
                     (bx2, by2, tz),
                     0.020, 0.10, bot_color)
            # White cap
            make_cyl(f"OTC_BottleCap_{tier}_{bi}",
                     (bx2, by2, tz + 0.06),
                     0.022, 0.012, COL_PAPER)


def build_cup_stack_lid_dispenser():
    # Tall stack of paper hot cups beside the coffee pots + a side
    # lid dispenser. Already in v2 builder via build_coffee_station —
    # check if I need this. Adding a SECOND stack near the slurpee
    # fountain so the west wall reads as a serving station.
    sx, sy = -5.20, 5.90
    base_z = 0.887   # on the counter top at 0.88 (2026-09-23: 1.3 cm over it)
    # Cup stack (40 cups tall)
    for ci in range(20):
        make_cyl(f"CupStackSlurp_{ci}", (sx, sy, base_z + ci * 0.012),
                 0.045, 0.014, COL_PAPER)
    # Lid dispenser (cylinder)
    make_cyl("LidDisp_Slurp", (sx + 0.14, sy, base_z + 0.083),
             0.05, 0.18, COL_METAL_BLACK)
    # Single visible lid on top
    make_cyl("LidDisp_Slurp_TopLid", (sx + 0.14, sy, base_z + 0.18),
             0.05, 0.005, COL_PAPER)


def build_window_mullions():
    # Add cross-mullions to the existing south windows — turn the
    # plain glass rectangles into multi-pane windows.
    for sgn in (-1, +1):
        cx = sgn * 3.00
        # Horizontal mid-mullion
        make_box(f"Window_Mull_H_{sgn:+d}",
                 (cx, -0.04, 1.55),
                 (2.20, 0.06, 0.05), COL_METAL_STEEL)
        # Two vertical mullions
        for vm_off in (-0.60, +0.60):
            make_box(f"Window_Mull_V_{sgn:+d}_{vm_off:+.2f}",
                     (cx + vm_off, -0.04, 1.55),
                     (0.05, 0.06, 1.40), COL_METAL_STEEL)


def build_door_hinges():
    # Cylindrical hinge barrels on the front + back doors. Tiny but
    # adds vertical interest to the door-frame seam.
    # Front door (south, X=0, Y=0)
    for sgn_x in (-1, +1):
        for hi in range(3):
            make_cyl(f"FrontDoor_Hinge_{sgn_x:+d}_{hi}",
                     (sgn_x * 1.50, 0.0, 0.30 + hi * 0.70),
                     0.018, 0.10, COL_METAL_BLACK, axis='X')
    # Back door (north-east, near stockroom)
    for hi in range(3):
        # on the back door's N edge (2026-09-24: three hinges stood in
        # mid-air at (4.40, 8.78), where an older back door once was)
        make_cyl(f"BackDoor_Hinge_{hi}",
                 (5.862, 7.94, 0.30 + hi * 0.70),
                 0.018, 0.08, COL_METAL_BLACK, axis='Z')


def build_paper_towel_dispenser():
    # Wall-mounted brown-paper-towel dispenser above the coffee
    # station — beige plastic box with curved cylindrical roll inside.
    px, py = -5.84, 4.20
    base_z = 1.80
    # Plastic body
    make_box("PaperTowel_Body", (px, py, base_z),
             (0.04, 0.30, 0.30), COL_PAPER_AGED)
    # Roll (visible from below)
    make_cyl("PaperTowel_Roll", (px + 0.04, py, base_z - 0.12),
             0.06, 0.26, COL_PAPER, axis='Y')
    # Sheet hanging down
    make_box("PaperTowel_Sheet", (px + 0.05, py, base_z - 0.27),   # from the roll
             (0.005, 0.24, 0.18), COL_PAPER)


def build_outside_hose_reel():
    # Coiled water-hose reel mounted on the south wall outside,
    # west of the door. Concentric cylinders simulate the coil.
    hx, hy = -4.20, -0.30   # (2026-09-22: the coil sat 8 cm into the wall, the bracket 3 cm off it)
    base_z = 1.20
    # Mount bracket, on the wall's outer face (y -0.10)
    make_box("HoseReel_Bracket", (hx, hy + 0.15, base_z),
             (0.04, 0.10, 0.30), COL_METAL_STEEL)
    # Coil — 4 concentric rings simulated as cylinders of increasing
    # radius, same Z. Color: dark green hose.
    for ri in range(4):   # the coil on the bracket's axle (2026-09-22: 11 cm out from it)
        make_cyl(f"HoseReel_Coil_{ri}", (hx + 0.05, hy, base_z),
                 0.04 + ri * 0.04, 0.06, (0.18, 0.32, 0.20, 1.0),
                 axis='X', segments=12)
    # Nozzle dangling on a drop of hose from the coil (2026-09-22)
    make_cyl("HoseReel_Drop", (hx + 0.05, hy, base_z - 0.215),
             0.012, 0.15, (0.18, 0.32, 0.20, 1.0))
    make_cyl("HoseReel_Nozzle", (hx + 0.05, hy, base_z - 0.34),
             0.025, 0.10, COL_METAL_STEEL)


def build_propane_pole_sign():
    # Tall outdoor pole sign with the convenience-store branding
    # at the southwest corner — visible through the south window.
    px, py = -5.80, -3.20
    pole_z = 2.50
    # Pole
    make_cyl("Pole_Body", (px, py, pole_z),
             0.10, 5.00, COL_METAL_STEEL)
    # Top sign panel (KWIK STOP red)
    make_box("Pole_Sign_BG", (px, py, pole_z + 2.40),
             (1.40, 0.10, 0.80), COL_BRAND_RED)
    # White letter band
    make_box("Pole_Sign_Letters", (px - 0.06, py, pole_z + 2.40),
             (0.005, 1.20, 0.30), COL_PAPER)
    # Gas-price LED panel below
    make_box("Pole_PriceBG", (px, py, pole_z + 1.60),
             (1.20, 0.10, 0.50), COL_METAL_BLACK)
    # Three red-LED digit blocks (price)
    for di in range(3):
        make_box(f"Pole_PriceDigit_{di}",
                 (px - 0.05, py, pole_z + 1.60),
                 (0.005, 0.30, 0.20), (0.96, 0.18, 0.10, 1.0))


def build_register_cord_loop():
    # Looped power cord from register to wall outlet — small black
    # cylinder arcs giving organic curve interest.
    rx, ry = 5.0, 4.5 - 1.20
    rz = 0.94
    # Trail south then east along the counter base
    for ci in range(8):
        progress: float = ci / 7.0
        # Arc downward then east
        cx2 = rx + math.sin(progress * math.pi * 0.5) * 0.40
        cy2 = ry - progress * 0.30
        cz2 = rz - progress * 0.84
        make_cyl(f"RegCord_{ci}",
                 (cx2, cy2, cz2),
                 0.012, 0.10, COL_METAL_BLACK)


def build_aisle_label_signs():
    # Cylindrical end-mount aisle-number signs at the head of each
    # aisle — round red disc with white number, suspended from the
    # ceiling at the south end of each aisle.
    for ai, ay in enumerate([3.5, 5.5]):
        sign_x = -2.80
        # Mount rod
        make_cyl(f"AisleNumRod_{ai}", (sign_x, ay, CEIL_Z - 0.20),
                 0.008, 0.40, COL_METAL_STEEL)   # reaches the ceiling
        # Disc
        make_cyl(f"AisleNumDisc_{ai}", (sign_x, ay, CEIL_Z - 0.42),
                 0.16, 0.04, COL_BRAND_RED, axis='X')
        # White number band
        make_box(f"AisleNum_{ai}", (sign_x - 0.03, ay, CEIL_Z - 0.42),
                 (0.005, 0.10, 0.10), COL_PAPER)


def build_polish_pass_5():
    build_counter_bullnose()
    build_crown_molding()
    build_baseboard_quarter_round()
    build_soda_bottle_pyramid()
    build_can_arrays_on_cooler_shelves()
    build_register_recess_detail()
    build_yellow_bollards_outside()
    build_drink_fridge_handles()
    build_floor_plant()
    build_broom_and_mop()
    build_pipes_along_ceiling()
    build_otc_meds_display()
    build_cup_stack_lid_dispenser()
    build_window_mullions()
    build_door_hinges()
    build_paper_towel_dispenser()
    build_outside_hose_reel()
    build_propane_pole_sign()
    build_register_cord_loop()
    build_aisle_label_signs()


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
        print(f"[build_kwik_stop] ✗ EXPORT FAILED: {e}")
        raise
    if os.path.exists(out_path):
        size = os.path.getsize(out_path)
        print(f"[build_kwik_stop] ✓ wrote {out_path} ({size} bytes)")


def build_hero_props_2026_08():
    """2026-08-03 hero-prop pass — vol6's most-repeated fixtures.
    Frame: x -6..6, y 0 storefront .. 9 north wall, counter L at
    east (cx 5.0, cy 4.5, top 1.04)."""
    wood = (0.42, 0.30, 0.18, 1.0)
    steel = (0.60, 0.62, 0.63, 1.0)
    # THE THREE TABLES BY THE WINDOW (the Red Peugeot chapter lives
    # here). One aligned to the existing west outlet.
    for ti, tx in enumerate((-4.5, -3.65, -2.8)):
        make_box(f"WinTable_{ti}_Top", (tx, 1.05, 0.74), (0.70, 0.70, 0.04), wood)
        make_cyl(f"WinTable_{ti}_Post", (tx, 1.05, 0.37), 0.05, 0.70, steel, segments=8)
        make_cyl(f"WinTable_{ti}_Foot", (tx, 1.05, 0.03), 0.24, 0.03, steel, segments=10)
        for ci, cy in enumerate((0.55, 1.55)):
            make_box(f"WinChair_{ti}_{ci}_Seat", (tx, cy, 0.44), (0.38, 0.38, 0.04), (0.62, 0.28, 0.24, 1.0))
            make_box(f"WinChair_{ti}_{ci}_Back", (tx, cy + (0.17 if ci else -0.17), 0.70),
                     (0.38, 0.04, 0.48), (0.55, 0.24, 0.20, 1.0))
            # four legs (2026-09-08: the seats hung 0.42 m above the floor)
            for lx in (-1, 1):
                for ly in (-1, 1):
                    make_box(f"WinChair_{ti}_{ci}_Leg_{lx:+d}_{ly:+d}",
                             (tx + lx * 0.16, cy + ly * 0.16, 0.22),
                             (0.03, 0.03, 0.44), steel)
    # THE MICROWAVE, its clock set nine minutes fast on purpose —
    # green LED face, on the coffee/food counter
    # (2026-09-22: it hung 19 cm above the counter, half past its edge)
    make_box("Microwave", (-5.05, 3.06, 1.03), (0.50, 0.36, 0.30), (0.26, 0.26, 0.28, 1.0))
    make_box("Microwave_Door", (-5.05, 2.87, 1.03), (0.38, 0.02, 0.24), (0.12, 0.12, 0.14, 1.0))
    make_box("Microwave_ClockLED", (-4.87, 2.865, 1.11), (0.10, 0.015, 0.035), (0.30, 0.92, 0.42, 1.0))
    # THE ACTUAL CLOCK — second face by the office door, east wall.
    # The pairing with the fast microwave clock is the point.
    make_cyl("Clock_Office_Face", (5.88, 8.05, 2.10), 0.16, 0.04, (0.92, 0.90, 0.84, 1.0), axis='X', segments=14)
    make_box("Clock_Office_HandH", (5.85, 8.02, 2.12), (0.02, 0.015, 0.08), (0.14, 0.14, 0.15, 1.0))
    make_box("Clock_Office_HandM", (5.85, 8.09, 2.11), (0.02, 0.10, 0.015), (0.14, 0.14, 0.15, 1.0))
    # The back office door (Jen's deposit paperwork) + lit pocket
    make_box("Office_Doorframe", (5.94, 7.2, 1.08), (0.10, 0.98, 2.16), wood)
    make_box("Office_Door_Open", (5.90, 7.2, 1.05), (0.05, 0.85, 2.05), (0.50, 0.40, 0.28, 1.0))
    make_box("Office_Light_Pocket", (5.89, 7.2, 1.30), (0.02, 0.70, 1.70), (0.98, 0.92, 0.72, 1.0))
    # The employee bathroom door, north wall — RESTROOM plaque
    make_box("Restroom_Door", (3.6, 8.94, 1.03), (0.80, 0.06, 2.05), (0.62, 0.60, 0.56, 1.0))
    make_box("Restroom_Plaque", (3.6, 8.90, 1.75), (0.24, 0.02, 0.10), (0.30, 0.34, 0.44, 1.0))
    # The layered window decals on the west picture window: lottery,
    # dead cigarette brand, and the TASTE HOME hamburger missing an
    # eye (ported in from the exterior shell where it was hiding)
    make_box("Decal_Lottery", (-4.1, 0.105, 1.62), (0.55, 0.01, 0.40), (0.90, 0.72, 0.24, 0.85))   # on the panel's inner face (2026-09-22: inside the wall)
    make_box("Decal_Cigs", (-3.4, 0.105, 1.45), (0.50, 0.01, 0.35), (0.70, 0.28, 0.24, 0.85))
    make_box("Decal_Burger", (-2.9, 0.105, 1.30), (0.45, 0.01, 0.45), (0.88, 0.62, 0.30, 0.9))
    make_box("Decal_Burger_Sign", (-2.9, -0.035, 1.10), (0.30, 0.008, 0.12), (0.94, 0.90, 0.80, 0.9))
    make_box("Decal_Burger_Eye", (-2.98, 0.111, 1.40), (0.05, 0.008, 0.05), (0.14, 0.14, 0.15, 1.0))
    # Convex security mirror above the door, angled at the counter
    make_cyl("Convex_Mirror", (0.0, 0.30, 2.55), 0.28, 0.06, (0.62, 0.68, 0.72, 1.0), axis='Y', segments=14)
    make_cyl("Convex_Mirror_Rim", (0.0, 0.27, 2.55), 0.30, 0.02, (0.94, 0.42, 0.20, 1.0), axis='Y', segments=14)
    make_box("Convex_Mirror_Bracket", (0.0, 0.185, 2.55), (0.04, 0.17, 0.04), COL_METAL_BLACK)   # to the wall (2026-09-22)
    # Rubber anti-fatigue mat on the working side of the counter
    make_box("AntiFatigue_Mat", (5.55, 4.5, 0.010), (0.80, 3.60, 0.015), (0.14, 0.14, 0.15, 1.0))
    # Employee break nook, NE corner: bench + two lockers
    # (2026-09-24: lockers flush on the N wall, W of the corner; the bench
    # in front of them, on legs — it was a board at 42 cm on nothing)
    make_box("Break_Bench", (4.45, 8.25, 0.42), (1.00, 0.36, 0.06), wood)
    for bi, (lx, ly) in enumerate(((-0.44, -0.14), (0.44, -0.14), (-0.44, 0.14), (0.44, 0.14))):
        make_box(f"Break_Bench_Leg_{bi}", (4.45 + lx, 8.25 + ly, 0.195), (0.04, 0.04, 0.39), wood)
    for li, lx in enumerate((4.25, 4.65)):
        make_box(f"Break_Locker_{li}", (lx, 8.70, 0.95), (0.38, 0.35, 1.90), (0.44, 0.50, 0.54, 1.0))
    # Indoor ice-cream novelty cooler (the one acting up)
    make_box("Novelty_Cooler", (-1.2, 7.4, 0.45), (1.60, 0.80, 0.90), (0.86, 0.88, 0.90, 1.0))
    make_box("Novelty_Cooler_Lid", (-1.2, 7.4, 0.92), (1.55, 0.75, 0.04), (0.55, 0.62, 0.66, 0.6))
    make_box("Novelty_Cooler_Decal", (-1.2, 6.99, 0.55), (1.20, 0.01, 0.40), (0.92, 0.56, 0.62, 1.0))
    # Tip cup at the register
    make_cyl("Tip_Cup", (4.55, 3.6, 1.12), 0.05, 0.14, (0.80, 0.82, 0.72, 0.7), segments=8)


def build_hero_props_2026_09():
    """HERO PROPS FOR THE BLIND CUES (shot_marker_audit, 2026-09-01).

    The kwik_stop_interior preset fires five distinct cues; the
    window cue aims at the existing south glass. Built here:

    - SAM'S PHONE (x2 — "Sam's phone buzzes" / "At 12:31, her
      phone buzzes"): face-up on the counter west of the impulse
      row. The payphone by the door is NOT her phone; the marker
      sits close so this one wins the nearest-match race.
    - THE SLUSHIE ("Sam drinks the slushie at one of the three
      tables by the window"): cup + lid + straw on WinTable_1,
      with the day-old paper Jen folded there beside it.
    - THE CARD ("MARTINEZ RE-ROOFING & SIDING with a phone
      number"): on the counter by the register where she set it
      before it went into the apron pocket.
    - THE NEXCORP VAN ("The van's engine is running. The van is
      facing her direction."): parked on a Linden street strip
      south of the forecourt, teal livery stripe toward the
      store, visible through the south glass past the pumps.

    Draft note: draft N+1 could idle the van (exhaust as a mood,
    not a mesh) and give the card its phone-number line.
    """
    white = (0.88, 0.88, 0.86, 1.0)
    # ── SAM'S PHONE · counter top (Z=1.07) ──
    make_box("Sams_Phone", (4.90, 4.05, 1.0755), (0.070, 0.140, 0.011),
             (0.13, 0.13, 0.15, 1.0))
    make_box("Sams_Phone_Screen", (4.90, 4.05, 1.0820), (0.058, 0.124, 0.002),
             (0.32, 0.40, 0.48, 1.0))
    # ── THE CARD · by the register ──
    make_box("Roofing_Card", (5.00, 3.75, 1.0705), (0.089, 0.051, 0.001),
             (0.93, 0.91, 0.84, 1.0))
    # ── THE SLUSHIE · WinTable_1 (top 0.76) ──
    make_cyl("Slushie_Cup", (-3.55, 0.98, 0.832), 0.045, 0.140,
             (0.20, 0.35, 0.75, 0.9), segments=10)
    make_cyl("Slushie_Lid", (-3.55, 0.98, 0.912), 0.047, 0.020,
             (0.90, 0.89, 0.86, 1.0), segments=10)
    make_cyl("Slushie_Straw", (-3.54, 0.97, 0.972), 0.006, 0.100,
             (0.86, 0.24, 0.20, 1.0), segments=6)
    make_box("Folded_Paper", (-3.78, 1.12, 0.766), (0.200, 0.140, 0.008),
             (0.86, 0.84, 0.78, 1.0))
    # ── THE NEXCORP VAN · Linden strip past the forecourt ──
    make_box("Street_Linden", (2.0, -7.2, -0.03), (8.0, 3.0, 0.05),
             (0.30, 0.30, 0.31, 1.0))
    make_box("NexCorp_Van_Body", (2.9, -7.2, 1.02), (4.60, 1.90, 1.50), white)
    make_box("NexCorp_Van_Windows", (2.9, -6.235, 1.35), (1.40, 0.030, 0.50),
             (0.28, 0.32, 0.38, 1.0))
    make_box("NexCorp_Van_Stripe", (2.9, -6.235, 0.85), (3.80, 0.030, 0.25),
             (0.20, 0.45, 0.48, 1.0))
    for wi, (wx2, wy2) in enumerate(((1.6, -6.375), (4.2, -6.375),
                                     (1.6, -8.025), (4.2, -8.025))):
        make_cyl(f"NexCorp_Van_Wheel_{wi}", (wx2, wy2, 0.35), 0.35, 0.25,
                 (0.14, 0.14, 0.15, 1.0), axis='Y', segments=10)


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
    build_polish_pass_3()
    build_polish_pass_4()
    build_polish_pass_5()
    build_hero_props_2026_08()
    build_hero_props_2026_09()
    export_glb()


if __name__ == "__main__":
    main()
