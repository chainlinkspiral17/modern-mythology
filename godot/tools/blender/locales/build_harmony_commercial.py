"""
build_harmony_commercial.py
══════════════════════════════════════════════════════════════════
VOL 6 · CHAPTER ONE BASELINE · HCE Commercial Cluster

The chapter-one playable block per _VOL6_WIKI.md "Adjacent
infrastructure" + the estuary_one HCE_CHAPTER_ONE quadrant.
Four buildings around one four-way intersection:

  · Kwik Stop          NW corner   (-250, +145) → local (-25, +8)
      Sam's register · wire basket of left-behind objects · the
      back cooler whose reflection contains an infinite recursion
      of its own surface.
  · NexCorp Gas & Go   NE corner   (-210, +145) → local (+25, +8)
      Skip's shift · locker #4 · ACROSS THE INTERSECTION from
      Kwik Stop per wiki.
  · Cosmic Comics      SW          (-250, +100) → local (-25, -37)
      Rick · the photocopier where NEWS FROM HARMONY CREEK gets
      run · the DO NOT SORT YET pile · Henderson Donation boxes.
  · D'Ambrosio's       SE          (-195, +90)  → local (+30, -47)
      The vol5 holdover. John's column corner. Maya's mail-drop
      to F.T. Same building family as the vol5 diner.

The scene local origin (0, 0, 0) is the INTERSECTION CENTER so
the player spawning at origin sees Kwik Stop to the west and
Gas & Go to the east.

The "one detail wrong" — the watch-detail per topography doc and
modeling playbook — is the FLYER stapled to the utility pole
outside Cosmic Comics. Maya's zine #19 cover. Read by the
player only if they look closely.

Per _3D_MODELING_PLAYBOOK.md vertex-colour zoning:
  RED is reserved for the Kwik Stop signage band and the NexCorp
  pump-island branding so the lithograph red_only bleed gate
  fires on the commercial-anchor signs (mirrors riverfront's
  D'Ambrosio's red).

COORDINATE FRAME (consistent with riverfront, diner, park):
    Blender (this script)  →  Godot world (runtime after glTF import)
      +X east              →    +X east
      +Y north / forward   →    -Z
      +Z up                →    +Y up
    1 unit = 1 metre.

Run:
    blender --background --python build_harmony_commercial.py
    (or ./run_cathedral.sh build_harmony_commercial.py)

Output:
    godot/assets/3d/locales/harmony_commercial.glb
"""

import os
import math
import bpy

_SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))

OUTPUT_DIR = "../../../assets/3d/locales"
OUTPUT_NAME = "harmony_commercial.glb"

# ── SEASON ────────────────────────────────────────────────────────
SEASON = 0.35    # mid-July baseline — see _HCE_TOPOGRAPHY.md

def lerp_palette(t, lo, hi):
    return tuple(lo[i] + (hi[i] - lo[i]) * t for i in range(4))

# ── DIMENSIONS ────────────────────────────────────────────────────
# Scene origin = intersection center.
# +X = east (toward Gas & Go), +Y = north (away from sidewalk),
# -Y = south (down the West Commercial Strip).

GROUND_Z = 0.0

# Streets (the right-of-way)
STREET_WIDTH_NS = 14.0    # N-S running street (the West Commercial)
STREET_WIDTH_EW = 16.0    # E-W arterial (busier — the North Belt)
SIDEWALK_W = 2.4
CURB_H = 0.15
BUFFER_W = 0.8           # planted strip between sidewalk and lot

# Building heights bumped up after first playthrough — user feedback
# "tops of buildings below waist high" was partly distance + partly
# the buildings being scaled for old commercial-strip realism.
# Real Kwik Stop is ~4 m tall but the in-game silhouette reads better
# with 7-8 m anchors plus tall signage pylons. Per modeling playbook:
# silhouette over real-world dimension when they conflict.

# Kwik Stop (NW corner)
KWIK_W = 16.0     # building width
KWIK_L = 11.0     # building depth (along Y)
KWIK_H = 7.0
KWIK_CX = -22.0   # building center east-west — pulled in toward intersection
KWIK_CY =  11.0   # set back 11 m north of intersection center

# NexCorp Gas & Go (NE corner)
GAS_KIOSK_W = 10.0   # the kiosk behind the pumps
GAS_KIOSK_L = 7.0
GAS_KIOSK_H = 5.5
GAS_KIOSK_CX = 40.0
GAS_KIOSK_CY = 16.0
GAS_CANOPY_W = 18.0  # the gas-pump canopy
GAS_CANOPY_L = 12.0
GAS_CANOPY_H = 6.5
GAS_CANOPY_CX = 23.0
GAS_CANOPY_CY = 14.0
GAS_PUMP_SPACING = 4.5     # spacing between pumps

# Cosmic Comics (SW)
COSMIC_W = 13.0
COSMIC_L = 9.0
COSMIC_H = 5.5
COSMIC_CX = -22.0
COSMIC_CY = -40.0

# D'Ambrosio's holdover (SE)
DAMB_W = 16.0
DAMB_L = 11.5
DAMB_H = 6.0
DAMB_CX = 28.0
DAMB_CY = -48.0

# Tall signage pylon heights (added after scale feedback)
PYLON_H = 12.0     # the freestanding pole + sign cabinet at each corner


# ── PALETTE ───────────────────────────────────────────────────────
# Seasonal (lawn / grass interpolates June green → August gold)
COL_LAWN = lerp_palette(SEASON, (0.22, 0.55, 0.18, 1.0),
                                (0.68, 0.62, 0.22, 1.0))
COL_BUFFER = lerp_palette(SEASON, (0.30, 0.50, 0.20, 1.0),
                                  (0.55, 0.48, 0.20, 1.0))
COL_SIDEWALK = lerp_palette(SEASON, (0.72, 0.70, 0.66, 1.0),
                                    (0.72, 0.68, 0.58, 1.0))

# Hard
COL_ASPHALT       = (0.22, 0.22, 0.22, 1.0)
COL_PAINT_YELLOW  = (0.78, 0.66, 0.18, 1.0)    # double-yellow centerline
COL_PAINT_WHITE   = (0.86, 0.84, 0.78, 1.0)    # crosswalk + lane lines
COL_CURB          = (0.55, 0.55, 0.54, 1.0)

# Kwik Stop — cream cinderblock + RED branding band
COL_KWIK_WALL     = (0.92, 0.86, 0.70, 1.0)    # cream block
COL_KWIK_ROOF     = (0.32, 0.30, 0.26, 1.0)    # tar-and-gravel flat roof
COL_KWIK_SIGN_RED = (0.85, 0.18, 0.16, 1.0)    # the RED accent band
COL_KWIK_GLASS    = (0.20, 0.32, 0.42, 1.0)    # storefront glass
COL_KWIK_DOOR     = (0.30, 0.22, 0.18, 1.0)    # service door
COL_TRIM_WHITE    = (0.90, 0.88, 0.82, 1.0)

# NexCorp Gas & Go — blue corporate canopy + red accent on pumps
COL_NEX_KIOSK     = (0.86, 0.82, 0.74, 1.0)
COL_NEX_KIOSK_ROOF= (0.30, 0.28, 0.24, 1.0)
COL_NEX_CANOPY    = (0.94, 0.92, 0.84, 1.0)    # white-painted canopy
COL_NEX_BRAND_BLUE = (0.18, 0.32, 0.62, 1.0)   # NexCorp blue
COL_NEX_BRAND_RED  = (0.82, 0.18, 0.16, 1.0)   # NexCorp red accent on pumps
COL_NEX_POST      = (0.32, 0.30, 0.28, 1.0)    # canopy support columns
COL_PUMP_BODY     = (0.88, 0.86, 0.80, 1.0)
COL_PUMP_BASE     = (0.30, 0.28, 0.26, 1.0)
COL_PUMP_NOZZLE   = (0.20, 0.18, 0.16, 1.0)
COL_CONCRETE_PAD  = (0.78, 0.76, 0.70, 1.0)    # the concrete under the pumps

# Cosmic Comics — purple awning + tan brick storefront
COL_COSMIC_WALL   = (0.62, 0.50, 0.42, 1.0)    # tan brick
COL_COSMIC_ROOF   = (0.32, 0.30, 0.26, 1.0)
COL_COSMIC_AWNING = (0.38, 0.20, 0.45, 1.0)    # purple comix awning
COL_COSMIC_GLASS  = (0.22, 0.30, 0.36, 1.0)
COL_COSMIC_DOOR   = (0.25, 0.20, 0.18, 1.0)
COL_COSMIC_SIGN   = (0.95, 0.90, 0.55, 1.0)    # cream sign face above awning

# D'Ambrosio's holdover — vol5 white clapboard + red trim
COL_DAMB_WALL     = (0.82, 0.78, 0.66, 1.0)    # white clapboard (same as vol5)
COL_DAMB_BAND     = (0.55, 0.20, 0.18, 1.0)    # red trim band (same as vol5)
COL_DAMB_ROOF     = (0.30, 0.24, 0.18, 1.0)
COL_DAMB_DOOR     = (0.30, 0.22, 0.18, 1.0)
COL_DAMB_WINDOW   = (0.50, 0.40, 0.32, 1.0)

# Site furniture
COL_UTIL_POLE     = (0.32, 0.26, 0.20, 1.0)    # creosote pole
COL_UTIL_WIRE     = (0.18, 0.18, 0.18, 1.0)
COL_TRANSFORMER   = (0.45, 0.45, 0.42, 1.0)
COL_STOPLIGHT_BOX = (0.18, 0.18, 0.18, 1.0)
COL_STOPLIGHT_RED   = (0.90, 0.16, 0.14, 1.0)
COL_STOPLIGHT_GREEN = (0.30, 0.78, 0.34, 1.0)
COL_STOPLIGHT_AMBER = (0.95, 0.65, 0.18, 1.0)
COL_STREETLIGHT_POLE = (0.28, 0.26, 0.22, 1.0)
COL_STREETLIGHT_HEAD = (0.92, 0.62, 0.30, 1.0)    # sodium head — fixture
COL_DUMPSTER       = (0.32, 0.46, 0.42, 1.0)      # dark teal dumpster
COL_TRASH          = (0.25, 0.25, 0.26, 1.0)
COL_FLYER          = (0.92, 0.90, 0.78, 1.0)      # the WATCH-DETAIL flyer

# Vehicles (a couple parked)
COL_CAR_GREY      = (0.36, 0.36, 0.38, 1.0)
COL_CAR_RED       = (0.55, 0.20, 0.18, 1.0)
COL_CAR_GLASS     = (0.18, 0.22, 0.26, 1.0)


# ════════════════════════════════════════════════════════════════
# PRIMITIVES (recycled from riverfront / park)
# ════════════════════════════════════════════════════════════════

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
    hx, hy, hz = sx/2, sy/2, sz/2
    verts = [
        (cx-hx, cy-hy, cz-hz), (cx+hx, cy-hy, cz-hz),
        (cx+hx, cy+hy, cz-hz), (cx-hx, cy+hy, cz-hz),
        (cx-hx, cy-hy, cz+hz), (cx+hx, cy-hy, cz+hz),
        (cx+hx, cy+hy, cz+hz), (cx-hx, cy+hy, cz+hz),
    ]
    face_defs = [
        ('-Z', (0,3,2,1)), ('+Z', (4,5,6,7)),
        ('-Y', (0,1,5,4)), ('+Y', (2,3,7,6)),
        ('-X', (3,0,4,7)), ('+X', (1,2,6,5)),
    ]
    faces = [list(vids) for (tag, vids) in face_defs if tag not in open_faces]
    return _finalize_mesh(name, verts, faces, base_color)


def make_cyl(name, center, radius, height, base_color, segments=10, axis='Z'):
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


def make_plane(name, x_min, y_min, x_max, y_max, z, base_color):
    verts = [(x_min, y_min, z), (x_max, y_min, z),
             (x_max, y_max, z), (x_min, y_max, z)]
    faces = [[0, 1, 2, 3]]
    return _finalize_mesh(name, verts, faces, base_color)


# ════════════════════════════════════════════════════════════════
# SCENE CLEAR
# ════════════════════════════════════════════════════════════════

def clear_scene():
    bpy.ops.object.select_all(action='SELECT')
    bpy.ops.object.delete(use_global=False)
    for block in bpy.data.meshes:
        bpy.data.meshes.remove(block)


# ════════════════════════════════════════════════════════════════
# THE INTERSECTION (asphalt, crosswalks, lane paint)
# ════════════════════════════════════════════════════════════════

def build_intersection_and_streets():
    """The 4-way intersection at scene origin, plus the two street
    runs that extend out to the lot edges. North arterial = E-W
    street (wider, busier — the North Commercial Belt). The
    intersecting N-S street is the West Commercial Strip arterial."""
    extent = 70.0   # how far each street run extends from intersection center

    # N-S asphalt strip (the West Commercial frontage)
    make_plane("Street_NS_Asphalt",
               -STREET_WIDTH_NS / 2, -extent,
               STREET_WIDTH_NS / 2, extent,
               GROUND_Z, COL_ASPHALT)
    # E-W asphalt strip (the North Belt arterial)
    make_plane("Street_EW_Asphalt",
               -extent, -STREET_WIDTH_EW / 2,
               extent, STREET_WIDTH_EW / 2,
               GROUND_Z + 0.001, COL_ASPHALT)
    # Intersection center is the union; that's fine — overlap reads
    # as one asphalt patch.

    # Double-yellow centerline on E-W arterial (skip the intersection itself)
    for sign in (-1, 1):
        x0 = sign * (STREET_WIDTH_NS / 2 + 1.5)
        x1 = sign * extent
        for off_y in (-0.18, 0.18):
            x_lo = min(x0, x1); x_hi = max(x0, x1)
            make_plane(f"Yellow_EW_{sign}_{off_y:+.1f}",
                       x_lo, off_y - 0.06, x_hi, off_y + 0.06,
                       GROUND_Z + 0.02, COL_PAINT_YELLOW)
    # Double-yellow on N-S
    for sign in (-1, 1):
        y0 = sign * (STREET_WIDTH_EW / 2 + 1.5)
        y1 = sign * extent
        for off_x in (-0.18, 0.18):
            y_lo = min(y0, y1); y_hi = max(y0, y1)
            make_plane(f"Yellow_NS_{sign}_{off_x:+.1f}",
                       off_x - 0.06, y_lo, off_x + 0.06, y_hi,
                       GROUND_Z + 0.02, COL_PAINT_YELLOW)

    # Crosswalks — 4 of them, one per leg of the intersection.
    # Six parallel white stripes per crosswalk.
    def crosswalk_strips(axis: str, leg_sign: int):
        if axis == 'EW':
            # crosswalk runs E-W across the N-S street
            base_y = leg_sign * (STREET_WIDTH_EW / 2 + 0.5)
            for i in range(6):
                x = -STREET_WIDTH_NS / 2 + 0.5 + i * (STREET_WIDTH_NS - 1.0) / 5
                make_plane(f"Crosswalk_EW_{leg_sign}_{i}",
                           x - 0.30, base_y - 0.05,
                           x + 0.30, base_y + 0.05,
                           GROUND_Z + 0.025, COL_PAINT_WHITE)
        else:
            base_x = leg_sign * (STREET_WIDTH_NS / 2 + 0.5)
            for i in range(6):
                y = -STREET_WIDTH_EW / 2 + 0.5 + i * (STREET_WIDTH_EW - 1.0) / 5
                make_plane(f"Crosswalk_NS_{leg_sign}_{i}",
                           base_x - 0.05, y - 0.30,
                           base_x + 0.05, y + 0.30,
                           GROUND_Z + 0.025, COL_PAINT_WHITE)
    crosswalk_strips('EW', +1)   # north side
    crosswalk_strips('EW', -1)   # south side
    crosswalk_strips('NS', +1)   # east side
    crosswalk_strips('NS', -1)   # west side


# ════════════════════════════════════════════════════════════════
# CURBS + SIDEWALKS + BUFFER STRIPS (per-corner)
# ════════════════════════════════════════════════════════════════

def build_curbs_and_sidewalks():
    """For each of the four corners, drop a curb step, a sidewalk
    plane, and a buffer strip leading into the lawn (or commercial
    lot, depending on the corner)."""
    half_ns = STREET_WIDTH_NS / 2
    half_ew = STREET_WIDTH_EW / 2
    extent = 70.0

    # NW corner sidewalk wraps under Kwik Stop
    # NE corner sidewalk wraps under Gas & Go
    # SW corner sidewalk wraps under Cosmic Comics
    # SE corner sidewalk wraps under D'Ambrosio's
    corners = [
        ('NW', -1, +1),
        ('NE', +1, +1),
        ('SW', -1, -1),
        ('SE', +1, -1),
    ]
    for (tag, sx, sy) in corners:
        # Curb along the inside edges of this corner. Curbs are thin
        # raised slabs of concrete (CURB_H tall).
        # East-west edge of this corner (along the EW street side)
        x_edge_lo = sx * half_ns
        x_edge_hi = sx * extent
        y_edge_inner = sy * half_ew
        # Curb (just inside the sidewalk on the road side)
        x_lo = min(x_edge_lo, x_edge_hi); x_hi = max(x_edge_lo, x_edge_hi)
        make_box(f"Curb_{tag}_EW",
                 ((x_lo + x_hi) / 2, y_edge_inner + sy * 0.12,
                  GROUND_Z + CURB_H / 2),
                 (x_hi - x_lo, 0.24, CURB_H),
                 COL_CURB)
        # Sidewalk inland of that curb
        y_side_lo = y_edge_inner + sy * 0.24
        y_side_hi = y_side_lo + sy * SIDEWALK_W
        y_lo = min(y_side_lo, y_side_hi); y_hi = max(y_side_lo, y_side_hi)
        make_plane(f"Sidewalk_{tag}_EW",
                   x_lo, y_lo, x_hi, y_hi,
                   GROUND_Z + CURB_H + 0.001, COL_SIDEWALK)
        # Buffer strip between sidewalk and lot
        y_buf_lo = y_side_hi
        y_buf_hi = y_side_hi + sy * BUFFER_W
        y_lo = min(y_buf_lo, y_buf_hi); y_hi = max(y_buf_lo, y_buf_hi)
        make_plane(f"Buffer_{tag}_EW",
                   x_lo, y_lo, x_hi, y_hi,
                   GROUND_Z + CURB_H + 0.002, COL_BUFFER)

        # NS-side curb+sidewalk
        y_edge_lo2 = sy * half_ew
        y_edge_hi2 = sy * extent
        x_edge_inner = sx * half_ns
        y_lo2 = min(y_edge_lo2, y_edge_hi2); y_hi2 = max(y_edge_lo2, y_edge_hi2)
        make_box(f"Curb_{tag}_NS",
                 (x_edge_inner + sx * 0.12, (y_lo2 + y_hi2) / 2,
                  GROUND_Z + CURB_H / 2),
                 (0.24, y_hi2 - y_lo2, CURB_H),
                 COL_CURB)
        x_side_lo = x_edge_inner + sx * 0.24
        x_side_hi = x_side_lo + sx * SIDEWALK_W
        x_lo2 = min(x_side_lo, x_side_hi); x_hi2 = max(x_side_lo, x_side_hi)
        make_plane(f"Sidewalk_{tag}_NS",
                   x_lo2, y_lo2, x_hi2, y_hi2,
                   GROUND_Z + CURB_H + 0.001, COL_SIDEWALK)
        x_buf_lo = x_side_hi
        x_buf_hi = x_side_hi + sx * BUFFER_W
        x_lo2 = min(x_buf_lo, x_buf_hi); x_hi2 = max(x_buf_lo, x_buf_hi)
        make_plane(f"Buffer_{tag}_NS",
                   x_lo2, y_lo2, x_hi2, y_hi2,
                   GROUND_Z + CURB_H + 0.002, COL_BUFFER)


# ════════════════════════════════════════════════════════════════
# THE LOTS (commercial parcels behind the sidewalks)
# ════════════════════════════════════════════════════════════════

def build_commercial_lots():
    """Asphalt parking lot pads behind each sidewalk. Each
    storefront has a small parking apron in front."""
    # NW lot — Kwik Stop
    make_plane("Lot_NW_KwikStop",
               -extent_lot_x_nw_min(), STREET_WIDTH_EW / 2 + 3.2,
               -STREET_WIDTH_NS / 2 - 3.2, 38.0,
               GROUND_Z + 0.02, COL_ASPHALT)
    # NE lot — Gas & Go
    make_plane("Lot_NE_GasGo",
               STREET_WIDTH_NS / 2 + 3.2, STREET_WIDTH_EW / 2 + 3.2,
               55.0, 38.0,
               GROUND_Z + 0.02, COL_ASPHALT)
    # SW lot — Cosmic Comics
    make_plane("Lot_SW_Cosmic",
               -50.0, -55.0,
               -STREET_WIDTH_NS / 2 - 3.2, -STREET_WIDTH_EW / 2 - 3.2,
               GROUND_Z + 0.02, COL_ASPHALT)
    # SE lot — D'Ambrosio's
    make_plane("Lot_SE_Damb",
               STREET_WIDTH_NS / 2 + 3.2, -65.0,
               55.0, -STREET_WIDTH_EW / 2 - 3.2,
               GROUND_Z + 0.02, COL_ASPHALT)


def extent_lot_x_nw_min():
    return 50.0


# ════════════════════════════════════════════════════════════════
# KWIK STOP
# ════════════════════════════════════════════════════════════════

def build_kwik_stop():
    """Convenience store — cream cinderblock, flat tar roof, RED
    branding band wrapping the parapet, big storefront glass on
    the street-facing side (south), service door on the west.
    The wire basket and back cooler are interior details we'll
    suggest via interior glow + a Label3D in the .tscn."""
    # Walls
    make_box("Kwik_Walls",
             (KWIK_CX, KWIK_CY, GROUND_Z + KWIK_H / 2),
             (KWIK_W, KWIK_L, KWIK_H),
             COL_KWIK_WALL, open_faces={'-Z'})
    # Flat roof (slightly bigger so it overhangs)
    make_box("Kwik_Roof",
             (KWIK_CX, KWIK_CY, GROUND_Z + KWIK_H + 0.15),
             (KWIK_W + 0.40, KWIK_L + 0.40, 0.30),
             COL_KWIK_ROOF)
    # RED signage band wrapping the parapet — the red bleed accent
    band_h = 0.85
    band_z = GROUND_Z + KWIK_H - band_h / 2 - 0.15
    # Front (south) face — full width
    make_box("Kwik_Band_S",
             (KWIK_CX, KWIK_CY - KWIK_L / 2 - 0.05,
              band_z),
             (KWIK_W + 0.10, 0.10, band_h),
             COL_KWIK_SIGN_RED)
    # East face
    make_box("Kwik_Band_E",
             (KWIK_CX + KWIK_W / 2 + 0.05, KWIK_CY,
              band_z),
             (0.10, KWIK_L + 0.10, band_h),
             COL_KWIK_SIGN_RED)
    # West face
    make_box("Kwik_Band_W",
             (KWIK_CX - KWIK_W / 2 - 0.05, KWIK_CY,
              band_z),
             (0.10, KWIK_L + 0.10, band_h),
             COL_KWIK_SIGN_RED)
    # Storefront glass — wide south-facing window
    glass_w = KWIK_W - 3.0
    glass_h = 2.2
    glass_z = GROUND_Z + 1.0 + glass_h / 2
    make_box("Kwik_Glass",
             (KWIK_CX + 1.0, KWIK_CY - KWIK_L / 2 - 0.05, glass_z),
             (glass_w, 0.10, glass_h),
             COL_KWIK_GLASS)
    # Cream window frame around the glass (trim)
    for (tag, ox, oy, sx, sy) in [
        ('top',    1.0,        0, glass_w + 0.40, 0.20),
        ('bottom', 1.0,        0, glass_w + 0.40, 0.20),
    ]:
        if tag == 'top':
            zf = glass_z + glass_h / 2 + 0.10
        else:
            zf = glass_z - glass_h / 2 - 0.10
        make_box(f"Kwik_GlassTrim_{tag}",
                 (KWIK_CX + ox, KWIK_CY - KWIK_L / 2 - 0.07, zf),
                 (sx, 0.12, 0.20),
                 COL_TRIM_WHITE)
    # Front door (left of the glass)
    door_w = 1.8
    door_h = 2.4
    make_box("Kwik_Door",
             (KWIK_CX - KWIK_W / 2 + 1.6,
              KWIK_CY - KWIK_L / 2 - 0.04,
              GROUND_Z + door_h / 2),
             (door_w, 0.12, door_h),
             COL_KWIK_DOOR)
    # Door frame trim
    make_box("Kwik_Door_Frame",
             (KWIK_CX - KWIK_W / 2 + 1.6,
              KWIK_CY - KWIK_L / 2 - 0.05,
              GROUND_Z + door_h + 0.10),
             (door_w + 0.30, 0.12, 0.18),
             COL_TRIM_WHITE)
    # Service door on the west wall (the back-cooler delivery)
    sd_h = 2.1
    make_box("Kwik_ServiceDoor",
             (KWIK_CX - KWIK_W / 2 - 0.05,
              KWIK_CY + KWIK_L / 2 - 1.4,
              GROUND_Z + sd_h / 2),
             (0.12, 1.0, sd_h),
             COL_KWIK_DOOR)
    # Dumpster behind (north side)
    make_box("Kwik_Dumpster",
             (KWIK_CX - KWIK_W / 2 + 2.0,
              KWIK_CY + KWIK_L / 2 + 1.8,
              GROUND_Z + 0.65),
             (2.6, 1.4, 1.30),
             COL_DUMPSTER, open_faces={'+Z'})


# ════════════════════════════════════════════════════════════════
# NEXCORP GAS & GO
# ════════════════════════════════════════════════════════════════

def build_gas_and_go():
    """NexCorp Gas & Go — 4 fuel pumps under a white canopy with a
    blue NexCorp brand band; small kiosk building behind. Skip's
    locker #4 is interior — a metallic-grey locker bank on the
    north wall, hinted via wall geometry."""
    # Concrete pad under the canopy
    make_plane("Gas_ConcretePad",
               GAS_CANOPY_CX - GAS_CANOPY_W / 2 - 1.5,
               GAS_CANOPY_CY - GAS_CANOPY_L / 2 - 1.5,
               GAS_CANOPY_CX + GAS_CANOPY_W / 2 + 1.5,
               GAS_CANOPY_CY + GAS_CANOPY_L / 2 + 1.5,
               GROUND_Z + 0.05, COL_CONCRETE_PAD)

    # Canopy — flat slab + blue brand band underneath the edge
    make_box("Gas_Canopy",
             (GAS_CANOPY_CX, GAS_CANOPY_CY, GROUND_Z + GAS_CANOPY_H + 0.25),
             (GAS_CANOPY_W, GAS_CANOPY_L, 0.50),
             COL_NEX_CANOPY)
    # Blue NexCorp brand band on the canopy edge — south-facing
    make_box("Gas_BrandBand_S",
             (GAS_CANOPY_CX, GAS_CANOPY_CY - GAS_CANOPY_L / 2 - 0.06,
              GROUND_Z + GAS_CANOPY_H + 0.05),
             (GAS_CANOPY_W + 0.10, 0.10, 0.50),
             COL_NEX_BRAND_BLUE)
    make_box("Gas_BrandBand_N",
             (GAS_CANOPY_CX, GAS_CANOPY_CY + GAS_CANOPY_L / 2 + 0.06,
              GROUND_Z + GAS_CANOPY_H + 0.05),
             (GAS_CANOPY_W + 0.10, 0.10, 0.50),
             COL_NEX_BRAND_BLUE)
    # Canopy support posts (4 corners)
    for (sx, sy) in [(-1, -1), (1, -1), (1, 1), (-1, 1)]:
        post_cx = GAS_CANOPY_CX + sx * (GAS_CANOPY_W / 2 - 0.5)
        post_cy = GAS_CANOPY_CY + sy * (GAS_CANOPY_L / 2 - 0.5)
        make_box(f"Gas_CanopyPost_{sx:+d}_{sy:+d}",
                 (post_cx, post_cy, GROUND_Z + GAS_CANOPY_H / 2),
                 (0.40, 0.40, GAS_CANOPY_H),
                 COL_NEX_POST)

    # 4 Fuel pumps — two islands of 2 pumps each, under the canopy
    # Pump islands are concrete bases with the pump body on top.
    for island in (-1, 1):
        island_x = GAS_CANOPY_CX + island * GAS_PUMP_SPACING
        # Island base
        make_box(f"Gas_Island_{island:+d}",
                 (island_x, GAS_CANOPY_CY, GROUND_Z + 0.20),
                 (1.4, 4.0, 0.30),
                 COL_PUMP_BASE)
        # Two pumps per island, facing opposite directions
        for side in (-1, 1):
            pump_cy = GAS_CANOPY_CY + side * 1.4
            # Pump body
            make_box(f"Gas_PumpBody_{island:+d}_{side:+d}",
                     (island_x, pump_cy, GROUND_Z + 0.30 + 0.80),
                     (0.80, 0.50, 1.60),
                     COL_PUMP_BODY)
            # Red NexCorp brand stripe on the pump face
            make_box(f"Gas_PumpStripe_{island:+d}_{side:+d}",
                     (island_x, pump_cy + side * 0.27,
                      GROUND_Z + 0.30 + 1.40),
                     (0.84, 0.06, 0.30),
                     COL_NEX_BRAND_RED)
            # Pump screen
            make_box(f"Gas_PumpScreen_{island:+d}_{side:+d}",
                     (island_x, pump_cy + side * 0.27,
                      GROUND_Z + 0.30 + 1.05),
                     (0.50, 0.06, 0.36),
                     (0.18, 0.22, 0.20, 1.0))
            # Nozzle holster (suggest with a small dark box)
            make_box(f"Gas_PumpHolster_{island:+d}_{side:+d}",
                     (island_x + 0.30, pump_cy + side * 0.27,
                      GROUND_Z + 0.30 + 0.60),
                     (0.18, 0.10, 0.20),
                     COL_PUMP_NOZZLE)

    # Kiosk building behind the canopy
    make_box("Gas_Kiosk_Walls",
             (GAS_KIOSK_CX, GAS_KIOSK_CY, GROUND_Z + GAS_KIOSK_H / 2),
             (GAS_KIOSK_W, GAS_KIOSK_L, GAS_KIOSK_H),
             COL_NEX_KIOSK, open_faces={'-Z'})
    # Roof
    make_box("Gas_Kiosk_Roof",
             (GAS_KIOSK_CX, GAS_KIOSK_CY, GROUND_Z + GAS_KIOSK_H + 0.15),
             (GAS_KIOSK_W + 0.30, GAS_KIOSK_L + 0.30, 0.30),
             COL_NEX_KIOSK_ROOF)
    # Front glass (south face — facing the pumps)
    make_box("Gas_Kiosk_Glass",
             (GAS_KIOSK_CX, GAS_KIOSK_CY - GAS_KIOSK_L / 2 - 0.05,
              GROUND_Z + 1.7),
             (GAS_KIOSK_W - 2.5, 0.10, 1.8),
             COL_KWIK_GLASS)
    # Door
    make_box("Gas_Kiosk_Door",
             (GAS_KIOSK_CX - 2.5, GAS_KIOSK_CY - GAS_KIOSK_L / 2 - 0.04,
              GROUND_Z + 1.20),
             (1.0, 0.12, 2.40),
             COL_KWIK_DOOR)
    # Brand sign on kiosk roof (NexCorp blue panel)
    make_box("Gas_Kiosk_SignBack",
             (GAS_KIOSK_CX, GAS_KIOSK_CY - GAS_KIOSK_L / 2 - 0.10,
              GROUND_Z + GAS_KIOSK_H + 0.85),
             (GAS_KIOSK_W * 0.70, 0.10, 0.95),
             COL_NEX_BRAND_BLUE)


# ════════════════════════════════════════════════════════════════
# COSMIC COMICS
# ════════════════════════════════════════════════════════════════

def build_cosmic_comics():
    """Smaller storefront. Tan brick walls, flat roof, PURPLE
    awning over the front door + storefront window. Sign panel
    above the awning. Rick's photocopier and the DO NOT SORT YET
    pile are interior — implied through a warm-lit interior."""
    make_box("Cosmic_Walls",
             (COSMIC_CX, COSMIC_CY, GROUND_Z + COSMIC_H / 2),
             (COSMIC_W, COSMIC_L, COSMIC_H),
             COL_COSMIC_WALL, open_faces={'-Z'})
    make_box("Cosmic_Roof",
             (COSMIC_CX, COSMIC_CY, GROUND_Z + COSMIC_H + 0.10),
             (COSMIC_W + 0.30, COSMIC_L + 0.30, 0.25),
             COL_COSMIC_ROOF)
    # Cream sign panel above the awning
    make_box("Cosmic_SignPanel",
             (COSMIC_CX, COSMIC_CY + COSMIC_L / 2 + 0.05,
              GROUND_Z + COSMIC_H - 0.65),
             (COSMIC_W - 1.0, 0.10, 0.80),
             COL_COSMIC_SIGN)
    # Purple awning — slopes down/out from the storefront
    awning_w = COSMIC_W - 1.5
    awning_d = 1.6
    awning_z = GROUND_Z + COSMIC_H - 1.95
    make_box("Cosmic_Awning",
             (COSMIC_CX, COSMIC_CY + COSMIC_L / 2 + awning_d / 2,
              awning_z),
             (awning_w, awning_d, 0.20),
             COL_COSMIC_AWNING)
    # Awning support brackets
    for sx in (-awning_w / 2 + 0.3, awning_w / 2 - 0.3):
        make_box(f"Cosmic_Awning_Bracket_{sx:+.1f}",
                 (COSMIC_CX + sx,
                  COSMIC_CY + COSMIC_L / 2 + 0.05,
                  awning_z + 0.30),
                 (0.10, 0.20, 0.60),
                 COL_COSMIC_AWNING)
    # Storefront glass (under the awning)
    make_box("Cosmic_Glass",
             (COSMIC_CX + 0.6, COSMIC_CY + COSMIC_L / 2 + 0.06,
              GROUND_Z + 1.3),
             (awning_w - 2.5, 0.08, 2.0),
             COL_COSMIC_GLASS)
    # Front door
    make_box("Cosmic_Door",
             (COSMIC_CX - awning_w / 2 + 0.9,
              COSMIC_CY + COSMIC_L / 2 + 0.05,
              GROUND_Z + 1.10),
             (1.0, 0.10, 2.20),
             COL_COSMIC_DOOR)


# ════════════════════════════════════════════════════════════════
# D'AMBROSIO'S HOLDOVER
# ════════════════════════════════════════════════════════════════

def build_dambrosios_holdover():
    """A smaller D'Ambrosio's outpost — vol5 holdover. Same family
    look as the vol5 riverfront diner: white clapboard walls, the
    signature red trim band, dark roof. NOT the boat — this is a
    fixed inland location. John's column corner is the south-east
    corner table area; Maya's letters to F.T. land in the mail-
    drop slot beside the front door."""
    make_box("Damb_Walls",
             (DAMB_CX, DAMB_CY, GROUND_Z + DAMB_H / 2),
             (DAMB_W, DAMB_L, DAMB_H),
             COL_DAMB_WALL, open_faces={'-Z'})
    # Red trim band wraps the building between window-height and roof
    band_z = GROUND_Z + DAMB_H - 0.45
    for (tag, cx, cy, sx, sy) in [
        ('S', DAMB_CX, DAMB_CY - DAMB_L/2 - 0.05, DAMB_W + 0.10, 0.10),
        ('N', DAMB_CX, DAMB_CY + DAMB_L/2 + 0.05, DAMB_W + 0.10, 0.10),
        ('E', DAMB_CX + DAMB_W/2 + 0.05, DAMB_CY, 0.10, DAMB_L + 0.10),
        ('W', DAMB_CX - DAMB_W/2 - 0.05, DAMB_CY, 0.10, DAMB_L + 0.10),
    ]:
        make_box(f"Damb_Band_{tag}",
                 (cx, cy, band_z),
                 (sx, sy, 0.35),
                 COL_DAMB_BAND)
    # Pitched roof (low slope)
    make_box("Damb_Roof",
             (DAMB_CX, DAMB_CY, GROUND_Z + DAMB_H + 0.20),
             (DAMB_W + 0.40, DAMB_L + 0.40, 0.40),
             COL_DAMB_ROOF)
    # Storefront — counter windows along the north face (faces the
    # intersection across the lot)
    for i in range(3):
        wx = DAMB_CX - DAMB_W / 2 + 2.0 + i * 3.8
        make_box(f"Damb_Window_{i}",
                 (wx, DAMB_CY - DAMB_L / 2 - 0.05,
                  GROUND_Z + 1.7),
                 (2.4, 0.10, 1.5),
                 COL_DAMB_WINDOW)
    # Front door (NW-facing entry)
    make_box("Damb_Door",
             (DAMB_CX - DAMB_W / 2 + 0.9,
              DAMB_CY - DAMB_L / 2 - 0.04,
              GROUND_Z + 1.15),
             (1.0, 0.12, 2.30),
             COL_DAMB_DOOR)
    # Mail-drop slot (the F.T. letter beat) — small cream box next to door
    make_box("Damb_MailDrop",
             (DAMB_CX - DAMB_W / 2 + 2.2,
              DAMB_CY - DAMB_L / 2 - 0.06,
              GROUND_Z + 1.10),
             (0.40, 0.08, 0.40),
             COL_TRIM_WHITE)


# ════════════════════════════════════════════════════════════════
# UTILITY POLES + STREETLIGHTS + STOP LIGHTS
# ════════════════════════════════════════════════════════════════

def build_site_furniture():
    # 4 streetlights — one at each corner of the intersection
    pole_h = 7.5
    arm_l = 2.5
    corner_offsets = [
        (-1, -1, +1, +1),    # SW pole, head reaches NE into intersection
        (+1, -1, -1, +1),
        (+1, +1, -1, -1),
        (-1, +1, +1, -1),
    ]
    for i, (sx, sy, head_sx, head_sy) in enumerate(corner_offsets):
        cx = sx * (STREET_WIDTH_NS / 2 + SIDEWALK_W + 0.6)
        cy = sy * (STREET_WIDTH_EW / 2 + SIDEWALK_W + 0.6)
        # Pole
        make_cyl(f"Streetlight_Pole_{i}",
                 (cx, cy, GROUND_Z + pole_h / 2),
                 0.12, pole_h, COL_STREETLIGHT_POLE, segments=8)
        # Arm reaching out over the intersection
        make_box(f"Streetlight_Arm_{i}",
                 (cx + head_sx * arm_l / 2 * 0.6,
                  cy + head_sy * arm_l / 2 * 0.6,
                  GROUND_Z + pole_h - 0.30),
                 (arm_l * 0.6, arm_l * 0.6, 0.10),
                 COL_STREETLIGHT_POLE)
        # Sodium head
        make_box(f"Streetlight_Head_{i}",
                 (cx + head_sx * arm_l * 0.6,
                  cy + head_sy * arm_l * 0.6,
                  GROUND_Z + pole_h - 0.50),
                 (0.70, 0.50, 0.30),
                 COL_STREETLIGHT_HEAD)

    # 4 stoplights at the intersection — suspended on cables from the
    # streetlight arms. Simplified as a stack of three coloured boxes
    # per stoplight, hung on a thin pole.
    for i in range(4):
        # Place each stoplight just inside the intersection from
        # one of the four arrival directions.
        ang = math.pi * 0.5 * i + math.pi * 0.25
        sx_dir = math.cos(ang)
        sy_dir = math.sin(ang)
        cx = sx_dir * 8.0
        cy = sy_dir * 8.0
        # Hanging pole stub
        make_cyl(f"Stoplight_Stub_{i}",
                 (cx, cy, GROUND_Z + 6.8),
                 0.06, 0.6, COL_STOPLIGHT_BOX, segments=6)
        # Stoplight box (3-light vertical)
        for j, col in enumerate([COL_STOPLIGHT_RED,
                                  COL_STOPLIGHT_AMBER,
                                  COL_STOPLIGHT_GREEN]):
            make_box(f"Stoplight_{i}_lens_{j}",
                     (cx, cy, GROUND_Z + 6.3 - j * 0.30),
                     (0.32, 0.30, 0.28),
                     col)
        # Housing strip
        make_box(f"Stoplight_{i}_Housing",
                 (cx - 0.20, cy, GROUND_Z + 5.85),
                 (0.10, 0.34, 0.95),
                 COL_STOPLIGHT_BOX)

    # 6 utility poles — wood creosote with crossbars + wires
    util_positions = [
        (-50, +20), (-50, -20),
        (+50, +20), (+50, -20),
        (-20, -65), (+20, -65),
    ]
    for i, (ux, uy) in enumerate(util_positions):
        pole_uh = 9.0
        make_cyl(f"UtilPole_{i}",
                 (ux, uy, GROUND_Z + pole_uh / 2),
                 0.20, pole_uh, COL_UTIL_POLE, segments=6)
        # Crossbar
        make_box(f"UtilPole_{i}_Crossbar",
                 (ux, uy, GROUND_Z + pole_uh - 0.3),
                 (2.2, 0.16, 0.16),
                 COL_UTIL_POLE)
        # Transformer can on one of the poles (pole 1)
        if i == 1:
            make_cyl(f"UtilPole_{i}_Transformer",
                     (ux + 0.40, uy, GROUND_Z + pole_uh - 1.4),
                     0.30, 0.90, COL_TRANSFORMER, segments=8)
    # Wires connecting adjacent poles — thin boxes (suggested)
    wires = [
        ((-50, +20), (-50, -20)),
        ((+50, +20), (+50, -20)),
        ((-50, +20), (+50, +20)),
        ((-50, -20), (+50, -20)),
        ((-20, -65), (+20, -65)),
    ]
    for i, (a, b) in enumerate(wires):
        ax, ay = a; bx, by = b
        mx = (ax + bx) / 2; my = (ay + by) / 2
        length = math.hypot(bx - ax, by - ay)
        # Just a thin long box at pole-top height; rotation skipped
        # for low-poly speed (good enough as a suggestion)
        if abs(bx - ax) > abs(by - ay):
            make_box(f"UtilWire_{i}",
                     (mx, my, GROUND_Z + 8.4),
                     (length, 0.04, 0.04), COL_UTIL_WIRE)
        else:
            make_box(f"UtilWire_{i}",
                     (mx, my, GROUND_Z + 8.4),
                     (0.04, length, 0.04), COL_UTIL_WIRE)


# ════════════════════════════════════════════════════════════════
# THE WATCH-DETAIL: flyer on the utility pole outside Cosmic Comics
# ════════════════════════════════════════════════════════════════

def build_watch_detail():
    """The 'one detail wrong' per the topography doc — Maya's zine
    #19 cover stapled to the utility pole outside Cosmic Comics.
    Cream paper, hand-printed, slightly off-rectangular. The player
    notices it only on a second look. The flyer being staple-square
    on the pole, with NO other flyers, makes it pop quietly."""
    pole_x = -20.0
    pole_y = -65.0
    # Cream rectangle on the pole's south face, hand-printed feel
    make_box("WatchDetail_Flyer",
             (pole_x, pole_y - 0.22, GROUND_Z + 2.10),
             (0.40, 0.04, 0.55),
             COL_FLYER)


# ════════════════════════════════════════════════════════════════
# PARKED CARS
# ════════════════════════════════════════════════════════════════

def _make_car(name, cx, cy, body_color, facing='+Y'):
    """Lowpoly car suggestion — two boxes stacked (body + cabin)
    plus four small wheel-blobs. PS2-grade silhouette."""
    body_l = 4.2
    body_w = 1.8
    body_h = 1.20
    cabin_l = 2.5
    cabin_w = 1.6
    cabin_h = 0.80

    if facing in ('+X', '-X'):
        body_l, body_w = body_w, body_l
        cabin_l, cabin_w = cabin_w, cabin_l

    # Body
    make_box(f"{name}_Body",
             (cx, cy, GROUND_Z + body_h / 2 + 0.15),
             (body_l, body_w, body_h),
             body_color)
    # Cabin (slightly back-shifted along the facing axis)
    if facing == '+Y':
        cabin_off = (0, -0.30, 0)
    elif facing == '-Y':
        cabin_off = (0, 0.30, 0)
    elif facing == '+X':
        cabin_off = (-0.30, 0, 0)
    else:
        cabin_off = (0.30, 0, 0)
    make_box(f"{name}_Cabin",
             (cx + cabin_off[0], cy + cabin_off[1],
              GROUND_Z + body_h + 0.15 + cabin_h / 2),
             (cabin_l, cabin_w, cabin_h),
             body_color)
    # Glass (just a darker rectangle on the cabin)
    make_box(f"{name}_Glass",
             (cx + cabin_off[0], cy + cabin_off[1],
              GROUND_Z + body_h + 0.15 + cabin_h * 0.65),
             (cabin_l - 0.30, cabin_w - 0.20, cabin_h * 0.55),
             COL_CAR_GLASS)


def build_parked_cars():
    # One car parked in front of Kwik Stop
    _make_car("Car_Kwik", KWIK_CX + 4.0,
              KWIK_CY - KWIK_L / 2 - 3.5, COL_CAR_GREY, facing='+Y')
    # One car at a Gas & Go pump
    _make_car("Car_Pump", GAS_CANOPY_CX - GAS_PUMP_SPACING + 2.8,
              GAS_CANOPY_CY - 1.4, COL_CAR_RED, facing='+X')
    # One parked in front of D'Ambrosio's
    _make_car("Car_Damb", DAMB_CX - 4.5,
              DAMB_CY - DAMB_L / 2 - 3.5, COL_CAR_GREY, facing='+Y')


# ════════════════════════════════════════════════════════════════
# OUT-OF-SCENE GROUND (so the world doesn't end at the lots)
# ════════════════════════════════════════════════════════════════

def build_far_ground():
    """A big lawn/buffer plane around everything so the lots don't
    float on void. Reads as 'somewhere in HCE'."""
    make_plane("Far_Lawn",
               -200, -120, 200, 100,
               GROUND_Z - 0.02, COL_LAWN)


# ════════════════════════════════════════════════════════════════
# EXPORT
# ════════════════════════════════════════════════════════════════

def export_glb():
    out_dir = os.path.normpath(os.path.join(_SCRIPT_DIR, OUTPUT_DIR))
    os.makedirs(out_dir, exist_ok=True)
    out_path = os.path.join(out_dir, OUTPUT_NAME)
    print(f"\n[build_harmony_commercial] exporting to {out_path}")
    print(f"[build_harmony_commercial] scene objects: {len(bpy.context.scene.objects)}")
    bpy.ops.object.select_all(action='SELECT')
    base = {
        'filepath': out_path, 'export_format': 'GLB',
        'use_selection': False, 'export_apply': True,
        'export_lights': False, 'export_cameras': False,
    }
    rna = bpy.ops.export_scene.gltf.get_rna_type()
    legacy = {}
    if 'export_colors' in rna.properties: legacy['export_colors'] = True
    if 'export_normals' in rna.properties: legacy['export_normals'] = True
    try:
        result = bpy.ops.export_scene.gltf(**base, **legacy)
        print(f"[build_harmony_commercial] export result: {result}")
    except Exception as e:
        print(f"[build_harmony_commercial] ✗ EXPORT FAILED: {e}")
        import traceback; traceback.print_exc()
        raise
    if os.path.exists(out_path):
        size = os.path.getsize(out_path)
        print(f"[build_harmony_commercial] ✓ wrote {out_path} ({size} bytes)")
    else:
        raise RuntimeError("GLB not written")


def build_signage_pylons():
    """Tall freestanding signage poles at each commercial corner —
    the silhouette anchors that read at a distance. Each has a pole
    and a rectangular sign cabinet at the top, brand-coloured."""
    # Kwik Stop pylon — RED sign cabinet at top (the lithograph
    # red bleed gate fires on this from across the intersection)
    px, py = KWIK_CX + KWIK_W / 2 + 3.0, KWIK_CY - KWIK_L / 2 - 4.5
    make_cyl("KwikPylon_Pole", (px, py, GROUND_Z + PYLON_H / 2),
             0.18, PYLON_H, COL_UTIL_POLE, segments=8)
    make_box("KwikPylon_Cabinet",
             (px, py, GROUND_Z + PYLON_H - 1.5),
             (3.5, 0.40, 2.8), COL_KWIK_SIGN_RED)
    make_box("KwikPylon_CabinetBorder",
             (px, py, GROUND_Z + PYLON_H - 1.5),
             (3.7, 0.30, 0.20), COL_TRIM_WHITE)

    # NexCorp pylon — BLUE sign cabinet (corporate)
    px, py = GAS_KIOSK_CX + GAS_KIOSK_W / 2 + 3.0, GAS_KIOSK_CY - GAS_KIOSK_L / 2 - 6.0
    make_cyl("NexPylon_Pole", (px, py, GROUND_Z + PYLON_H / 2),
             0.18, PYLON_H, COL_UTIL_POLE, segments=8)
    make_box("NexPylon_Cabinet",
             (px, py, GROUND_Z + PYLON_H - 1.5),
             (3.5, 0.40, 3.0), COL_NEX_BRAND_BLUE)
    # Red NexCorp accent stripe across the bottom of the cabinet
    make_box("NexPylon_AccentStripe",
             (px, py, GROUND_Z + PYLON_H - 2.6),
             (3.6, 0.42, 0.25), COL_NEX_BRAND_RED)

    # Cosmic Comics smaller pylon — purple
    px, py = COSMIC_CX - COSMIC_W / 2 - 3.0, COSMIC_CY + COSMIC_L / 2 + 4.0
    make_cyl("CosmicPylon_Pole", (px, py, GROUND_Z + (PYLON_H - 3) / 2),
             0.15, PYLON_H - 3, COL_UTIL_POLE, segments=6)
    make_box("CosmicPylon_Cabinet",
             (px, py, GROUND_Z + PYLON_H - 4.0),
             (2.8, 0.30, 2.2), COL_COSMIC_AWNING)


def main():
    clear_scene()
    build_far_ground()
    build_intersection_and_streets()
    build_curbs_and_sidewalks()
    build_commercial_lots()
    build_kwik_stop()
    build_gas_and_go()
    build_cosmic_comics()
    build_dambrosios_holdover()
    build_signage_pylons()
    build_site_furniture()
    build_watch_detail()
    build_parked_cars()
    export_glb()


if __name__ == "__main__":
    main()
