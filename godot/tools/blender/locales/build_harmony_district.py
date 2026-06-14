"""
build_harmony_district.py
══════════════════════════════════════════════════════════════════
VOL 6 · HCE FULL DISTRICT — topography + creek + road grid
The whole 600 m × 420 m suburban district per _HCE_TOPOGRAPHY.md
and the estuary_one HCE_PARAMS map. Low-poly massing only at this
scale; detailed sub-sectors (Kwik Stop intersection, Harmony Park,
country club) get their own build_*.py scripts that compose into
the same world.

Builds:
  · Hilly ground plane (subdivided heightmap from hce_elevation —
    NW high country-club rise, SE low, creek flood-plain dip)
  · Harmony Creek (NW → SE meandering blue ribbon with edge bank)
  · Road grid (4 commercial perimeter belts + interior connectors)
  · Bridges where roads cross the creek
  · Massing blocks for each NEIGHBOURHOOD region — clusters of
    rough rectangular roofs indicating residential / commercial
    density without per-building detail
  · Sub-sector anchor markers (small coloured posts) at every
    named landmark from the estuary_one map — chapter-one Kwik
    Stop / Gas & Go / Cosmic Comics / D'Ambrosio's, plus civic
    (HOA, Pool, Country Club), media (Halsey Studios), narrative
    (Lot 7, Lot 14, Lot 47, 892 Ashberry, Phase III trailer)

This is the WORLD-SCALE backdrop. Detailed sub-sector .glb files
sit alongside it in Godot — the same scene can load both. The
district provides the surrounding context the player sees walking
between sub-sectors.

COORDINATE FRAME (consistent with other build scripts):
    Blender Z-up, +X east, +Y north, 1 unit = 1 metre.

Run:
    blender --background --python build_harmony_district.py

Output:
    godot/assets/3d/locales/harmony_district.glb
"""

import os
import math
import sys
import bpy

_SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, _SCRIPT_DIR)

from infra_library import (
    suburban_drive, highway_segment, four_way_intersection,
    roundabout, cul_de_sac, bridge,
    streetlight_pole, stop_sign, utility_pole, utility_wire,
    fire_hydrant, mailbox_cluster, bus_stop,
    school_zone_sign, library_sign, park_sign, public_walkway,
    bench, picnic_table,
    COL_ASPHALT, COL_SIDEWALK, COL_MEDIAN_GRASS, COL_CONCRETE,
    COL_POLE_DARK, COL_SHELTER_ROOF,
)

OUTPUT_DIR = "../../../assets/3d/locales"
OUTPUT_NAME = "harmony_district.glb"

# ── SEASON ────────────────────────────────────────────────────────
SEASON = 0.35

def lerp_palette(t, lo, hi):
    return tuple(lo[i] + (hi[i] - lo[i]) * t for i in range(4))

# ── DISTRICT BOUNDS (matches estuary_one HCE_PARAMS) ─────────────
DIST_MIN_X = -300.0
DIST_MAX_X =  300.0
DIST_MIN_Y = -210.0
DIST_MAX_Y =  210.0

# Ground tessellation — 30×21 cells = 20 m per cell, finer than
# the elevation noise so the hills read but not so fine the GLB
# blows up.
GROUND_NX = 30
GROUND_NY = 21

# ── PALETTE ───────────────────────────────────────────────────────
COL_LAWN  = lerp_palette(SEASON, (0.22, 0.55, 0.18, 1.0),
                                 (0.68, 0.62, 0.22, 1.0))
COL_NATURAL_GREEN = lerp_palette(SEASON, (0.18, 0.42, 0.18, 1.0),
                                         (0.42, 0.42, 0.18, 1.0))
COL_GOLF_GREEN = (0.16, 0.48, 0.18, 1.0)   # irrigated — stays green
COL_OVERGROWN = lerp_palette(SEASON, (0.30, 0.48, 0.26, 1.0),
                                     (0.55, 0.55, 0.28, 1.0))
COL_DRY_LOT   = lerp_palette(SEASON, (0.58, 0.55, 0.42, 1.0),
                                     (0.76, 0.72, 0.55, 1.0))
COL_CREEK_WATER = (0.32, 0.50, 0.55, 1.0)
COL_CREEK_BANK  = (0.42, 0.36, 0.26, 1.0)
COL_HOUSE_BODY_A = (0.86, 0.82, 0.72, 1.0)    # cream
COL_HOUSE_BODY_B = (0.72, 0.66, 0.56, 1.0)    # tan
COL_HOUSE_BODY_C = (0.62, 0.58, 0.62, 1.0)    # grey-blue
COL_HOUSE_BODY_D = (0.78, 0.62, 0.52, 1.0)    # peach
COL_HOUSE_ROOF_A = (0.32, 0.26, 0.22, 1.0)    # dark shingle
COL_HOUSE_ROOF_B = (0.50, 0.32, 0.24, 1.0)    # red shingle
COL_HOUSE_ROOF_C = (0.28, 0.30, 0.32, 1.0)    # slate
COL_COMMERCIAL_WALL = (0.78, 0.74, 0.66, 1.0)
COL_COMMERCIAL_ROOF = (0.30, 0.28, 0.24, 1.0)
COL_MONUMENT_BLUE   = (0.18, 0.32, 0.62, 1.0)
COL_MONUMENT_RED    = (0.78, 0.18, 0.16, 1.0)
COL_MONUMENT_PURPLE = (0.38, 0.20, 0.45, 1.0)
COL_MONUMENT_CYAN   = (0.18, 0.62, 0.78, 1.0)
COL_MONUMENT_ORANGE = (0.95, 0.55, 0.20, 1.0)
COL_TREE_TRUNK = (0.22, 0.16, 0.10, 1.0)


# ════════════════════════════════════════════════════════════════
# PRIMITIVES (lean — most heavy lifting comes from infra_library)
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


def _box(name, center, size, color, open_faces=None):
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
    return _finalize_mesh(name, verts, faces, color)


def _cyl(name, center, radius, height, color, segments=6):
    cx, cy, cz = center
    h2 = height / 2.0
    verts = []
    for ring in (0, 1):
        z_off = -h2 if ring == 0 else h2
        for i in range(segments):
            ang = 2.0 * math.pi * i / segments
            verts.append((cx + math.cos(ang) * radius,
                          cy + math.sin(ang) * radius,
                          cz + z_off))
    faces = []
    for i in range(segments):
        ni = (i + 1) % segments
        faces.append([i, ni, ni + segments, i + segments])
    faces.append(list(reversed(range(segments))))
    faces.append(list(range(segments, segments * 2)))
    return _finalize_mesh(name, verts, faces, color)


def _make_sphere_low(name, center, radius, color, rings=3, segments=6):
    cx, cy, cz = center
    verts = [(cx, cy, cz + radius)]
    for r in range(1, rings):
        phi = math.pi * r / rings
        rr = radius * math.sin(phi)
        rz = radius * math.cos(phi)
        for s in range(segments):
            a = 2.0 * math.pi * s / segments
            verts.append((cx + rr * math.cos(a),
                          cy + rr * math.sin(a),
                          cz + rz))
    verts.append((cx, cy, cz - radius))
    faces = []
    for s in range(segments):
        faces.append([0, 1 + s, 1 + (s + 1) % segments])
    for r in range(rings - 2):
        base = 1 + r * segments
        nxt = 1 + (r + 1) * segments
        for s in range(segments):
            faces.append([base + s, nxt + s,
                          nxt + (s + 1) % segments,
                          base + (s + 1) % segments])
    last = len(verts) - 1
    base = 1 + (rings - 2) * segments
    for s in range(segments):
        faces.append([last, base + (s + 1) % segments, base + s])
    return _finalize_mesh(name, verts, faces, color)


# ════════════════════════════════════════════════════════════════
# TOPOGRAPHY — heightmap from the estuary_one HCE elevation function
# ════════════════════════════════════════════════════════════════
# Re-implemented here so the build script stays standalone (the
# landscape_sim folder isn't on the Blender sys.path). Identical
# parameters to estuary_one.hce_elevation.

def fbm(x, y, octaves=3, base_freq=1.0, lacunarity=2.0):
    total = 0.0; amp = 0.5; freq = base_freq
    for _ in range(octaves):
        # Tiny value-noise (deterministic hash)
        ix = math.floor(x * freq); iy = math.floor(y * freq)
        fx = x * freq - ix; fy = y * freq - iy
        n00 = _hash2d(ix,     iy)
        n10 = _hash2d(ix + 1, iy)
        n01 = _hash2d(ix,     iy + 1)
        n11 = _hash2d(ix + 1, iy + 1)
        sx = fx * fx * (3 - 2 * fx)
        sy = fy * fy * (3 - 2 * fy)
        nx0 = n00 + sx * (n10 - n00)
        nx1 = n01 + sx * (n11 - n01)
        total += amp * (nx0 + sy * (nx1 - nx0))
        amp *= 0.5; freq *= lacunarity
    return total

def _hash2d(x, y, seed=1337):
    n = math.sin(x * 12.9898 + y * 78.233 + seed * 0.0001) * 43758.5453
    return n - math.floor(n)

# Harmony Creek polyline — copied from estuary_one's HCE_CREEK
CREEK_POINTS = [
    (-280,  180),
    (-150,   80),
    ( -40,    0),
    (  80,  -70),
    ( 200, -120),
    ( 290, -180),
]
CREEK_FLOOD_WIDTH = 28.0

def creek_distance(x, y):
    """Closest distance from (x, y) to the polyline."""
    best = float("inf")
    for i in range(len(CREEK_POINTS) - 1):
        x0, y0 = CREEK_POINTS[i]
        x1, y1 = CREEK_POINTS[i + 1]
        dx = x1 - x0; dy = y1 - y0
        length2 = dx * dx + dy * dy
        if length2 < 0.001:
            d = math.hypot(x - x0, y - y0)
        else:
            t = ((x - x0) * dx + (y - y0) * dy) / length2
            t = max(0.0, min(1.0, t))
            px = x0 + dx * t; py = y0 + dy * t
            d = math.hypot(x - px, y - py)
        if d < best:
            best = d
    return best


def hce_elevation(x, y):
    tilt = 4.0 * ((-(x) + y) / 600.0)
    cc_dx = x - 0
    cc_dy = y - 200
    cc_rise = 4.0 * math.exp(-(cc_dx * cc_dx + cc_dy * cc_dy) / (140.0 * 140.0))
    noise = (fbm(x * 0.008, y * 0.008, octaves=3) - 0.5) * 0.6
    creek_d = creek_distance(x, y)
    dip = -1.2 * math.exp(-creek_d * creek_d / (CREEK_FLOOD_WIDTH ** 2))
    return tilt + cc_rise + noise + dip


def landuse_at(x, y):
    """Classify a point for ground colouring. Approximates the
    estuary_one HCE_NEIGHBOURHOODS polygons without re-importing
    them — coarse but matches the visual breakdown."""
    # Country club + golf (NW high ground)
    if -230 < x < 220 and 170 < y < 210:
        return 'golf'
    # Creek corridor
    if creek_distance(x, y) < 8.0:
        return 'creek'
    # Commercial belts
    if -280 <= x <= -230 and -170 <= y <= 130:
        return 'commercial'
    if x >= 220 and -170 <= y <= 130:
        return 'commercial'
    if -230 <= x <= 220 and 130 <= y <= 170:
        return 'commercial'
    if -230 <= x <= 220 and -200 <= y <= -170:
        return 'commercial'
    # Harmony Park
    if -60 <= x <= 90 and -20 <= y <= 100:
        return 'park'
    # Founders Memorial Grove
    if -200 <= x <= -100 and 50 <= y <= 110:
        return 'park_natural'
    # South Sports Fields
    if 130 <= x <= 220 and -160 <= y <= -50:
        return 'park_sports'
    # Wild lot
    if -200 <= x <= -130 and -150 <= y <= -90:
        return 'overgrown'
    # Default: residential lawn
    return 'lawn'


def color_for(x, y):
    lu = landuse_at(x, y)
    if lu == 'golf':
        return COL_GOLF_GREEN
    if lu == 'creek':
        return COL_CREEK_BANK
    if lu == 'commercial':
        return (0.42, 0.40, 0.36, 1.0)
    if lu == 'park':
        return COL_LAWN
    if lu == 'park_natural':
        return COL_NATURAL_GREEN
    if lu == 'park_sports':
        return COL_LAWN
    if lu == 'overgrown':
        return COL_OVERGROWN
    return COL_LAWN


# ════════════════════════════════════════════════════════════════
# CLEAR SCENE
# ════════════════════════════════════════════════════════════════

def clear_scene():
    bpy.ops.object.select_all(action='SELECT')
    bpy.ops.object.delete(use_global=False)
    for block in bpy.data.meshes:
        bpy.data.meshes.remove(block)


# ════════════════════════════════════════════════════════════════
# GROUND — subdivided heightmap with per-vertex colour
# ════════════════════════════════════════════════════════════════

def build_ground():
    """One big subdivided plane. Per-vertex elevation from
    hce_elevation; per-loop colour from landuse_at."""
    verts = []
    # nx × ny vertices laid out in a regular grid
    for j in range(GROUND_NY + 1):
        wy = DIST_MIN_Y + (DIST_MAX_Y - DIST_MIN_Y) * j / GROUND_NY
        for i in range(GROUND_NX + 1):
            wx = DIST_MIN_X + (DIST_MAX_X - DIST_MIN_X) * i / GROUND_NX
            z = hce_elevation(wx, wy)
            verts.append((wx, wy, z))
    # Quad faces
    faces = []
    nx = GROUND_NX + 1
    for j in range(GROUND_NY):
        for i in range(GROUND_NX):
            a = j * nx + i
            b = a + 1
            c = b + nx
            d = a + nx
            faces.append([a, b, c, d])
    mesh = bpy.data.meshes.new("Ground_mesh")
    mesh.from_pydata(verts, [], faces)
    mesh.update()
    if not mesh.vertex_colors:
        mesh.vertex_colors.new(name="Col")
    layer = mesh.vertex_colors["Col"]
    # Colour each polygon loop based on the face centre's landuse
    for poly in mesh.polygons:
        # Compute face centre in world coords
        cx = sum(verts[v][0] for v in poly.vertices) / len(poly.vertices)
        cy = sum(verts[v][1] for v in poly.vertices) / len(poly.vertices)
        col = color_for(cx, cy)
        for li in poly.loop_indices:
            layer.data[li].color = col
    obj = bpy.data.objects.new("Ground", mesh)
    bpy.context.collection.objects.link(obj)
    return obj


# ════════════════════════════════════════════════════════════════
# CREEK — Harmony Creek as a polyline of submerged water-strip quads
# ════════════════════════════════════════════════════════════════

def build_creek():
    """Water surface inside the creek's flood-plain dip. Sits just
    above the dipped ground (ground at dip bottom is ~−1.2 m; the
    water plane is at ~−0.8 m so a bank shows). Built segment by
    segment along the polyline so it bends with the creek."""
    water_z = -0.8
    width = 5.0
    for i in range(len(CREEK_POINTS) - 1):
        x0, y0 = CREEK_POINTS[i]
        x1, y1 = CREEK_POINTS[i + 1]
        dx = x1 - x0; dy = y1 - y0
        ang = math.atan2(dy, dx)
        perp_x = -math.sin(ang); perp_y = math.cos(ang)
        verts = [
            (x0 - perp_x * width / 2, y0 - perp_y * width / 2, water_z),
            (x1 - perp_x * width / 2, y1 - perp_y * width / 2, water_z),
            (x1 + perp_x * width / 2, y1 + perp_y * width / 2, water_z),
            (x0 + perp_x * width / 2, y0 + perp_y * width / 2, water_z),
        ]
        _finalize_mesh(f"Creek_Water_{i}", verts, [[0, 1, 2, 3]],
                       COL_CREEK_WATER)


# ════════════════════════════════════════════════════════════════
# ROAD NETWORK — major arterials + a few interior connectors
# ════════════════════════════════════════════════════════════════

def build_roads():
    """The four perimeter arterials + two interior collector roads
    using the infra_library. Bridges drop in where roads cross the
    creek polyline."""
    # West arterial (N-S, x ≈ -255)
    suburban_drive("Road_West", (-255, -200), (-255, 200),
                   width=14.0, paint='double_yellow', z=0.0)
    # East arterial
    suburban_drive("Road_East", (245, -200), (245, 200),
                   width=14.0, paint='double_yellow', z=0.0)
    # North arterial (E-W, y ≈ +150)
    suburban_drive("Road_North", (-280, 150), (270, 150),
                   width=14.0, paint='double_yellow', z=0.0)
    # South arterial
    suburban_drive("Road_South", (-280, -185), (270, -185),
                   width=14.0, paint='double_yellow', z=0.0)
    # Interior collectors
    suburban_drive("Road_Mid_NS", (-30, -180), (-30, 145),
                   width=11.0, paint='single_yellow', z=0.0)
    suburban_drive("Road_Mid_EW", (-250, 0), (240, 0),
                   width=11.0, paint='single_yellow', z=0.0)
    suburban_drive("Road_Inner_NE", (100, -180), (100, 145),
                   width=11.0, paint='single_yellow', z=0.0)
    # Hilltop road into the country club
    suburban_drive("Road_Hilltop", (-30, 145), (-30, 200),
                   width=8.0, paint='single_yellow', z=0.0,
                   with_sidewalk=False)
    # Roundabout where Mid_NS meets Mid_EW
    roundabout("Roundabout_Mid", (-30, 0), outer_r=18.0,
               inner_r=9.0, n_legs=4)
    # Cul-de-sac in the east cul-de-sac neighborhood
    cul_de_sac("CDS_East1", (170, 80), radius=14.0, entry_dir='-Y')
    cul_de_sac("CDS_East2", (170, 50), radius=12.0, entry_dir='-Y')

    # Four-way intersection at Kwik Stop / Gas & Go corner
    # (matches build_harmony_commercial.py local origin which is at
    # world coords (-230, 145) per landmark placement).
    four_way_intersection("X_ChapterOne", (-230, 145),
                          ns_width=14.0, ew_width=16.0)
    # Truck stop / south arterial intersection
    four_way_intersection("X_TruckStop", (0, -185),
                          ns_width=11.0, ew_width=14.0)
    # Country club entrance intersection
    four_way_intersection("X_Hilltop", (-30, 145),
                          ns_width=8.0, ew_width=14.0)


# ════════════════════════════════════════════════════════════════
# BRIDGES — where roads cross the creek
# ════════════════════════════════════════════════════════════════

def build_bridges():
    """Each major road crossing the creek polyline gets a bridge.
    Walks the polyline + finds intersections with road segments
    that cross it within tolerance."""
    # Manually identify crossings — the creek goes from
    # (-280,180) → (-150,80) → (-40,0) → (80,-70) → (200,-120) → (290,-180)
    # Crossings (approximate, eyeballed against the road grid):
    crossings = [
        ((-30, 13), 'EW', 12.0, "Bridge_MidEW"),   # Mid_EW crosses creek near (-30, 13)?
        ((100, -55), 'NS', 12.0, "Bridge_InnerNE"),  # Inner_NE crosses creek
    ]
    for (cx, cy), axis, w, name in crossings:
        if axis == 'EW':
            bridge(name, (cx - 12, cy), (cx + 12, cy), width=w,
                   deck_h=1.6, z=0.0, with_rails=True)
        else:
            bridge(name, (cx, cy - 12), (cx, cy + 12), width=w,
                   deck_h=1.6, z=0.0, with_rails=True)


# ════════════════════════════════════════════════════════════════
# MASSING — rough rectangular building blocks for each district
# ════════════════════════════════════════════════════════════════

def build_neighborhoods_massing():
    """Drop low-poly massing into each residential / commercial
    block so the district has visual mass without per-building
    detail. Each neighbourhood gets a grid of houses or commercial
    blocks placed at z=ground(x,y) so they sit on the heightmap."""

    # West Estates (single-family residential, west of central)
    place_house_grid(-220, -160, -80, -30, spacing=24,
                     seed_offset=11, tag="WestEstates")
    # North Ranch Homes
    place_house_grid(-220, 20, -110, 130, spacing=22,
                     seed_offset=22, tag="NorthRanch")
    # East Cul-de-sac Estates
    place_house_grid(110, 20, 220, 130, spacing=22,
                     seed_offset=33, tag="EastCDS")
    # Phase III construction (dirt — west of central, south of creek)
    place_construction(-180, -135, 18, "Phase3_Trailer")

    # Country club clubhouse on the high ground
    _box("CountryClub_Main",
         (-30, 195, hce_elevation(-30, 195) + 5),
         (36, 18, 8.0), COL_COMMERCIAL_WALL, open_faces={'-Z'})
    _box("CountryClub_Roof",
         (-30, 195, hce_elevation(-30, 195) + 9.2),
         (38, 20, 0.6), (0.50, 0.32, 0.24, 1.0))
    # Two annexes (locker rooms / pro shop)
    _box("CountryClub_Annex_W",
         (-65, 192, hce_elevation(-65, 192) + 3),
         (16, 12, 5.5), COL_COMMERCIAL_WALL, open_faces={'-Z'})
    _box("CountryClub_Annex_E",
         (15, 192, hce_elevation(15, 192) + 3),
         (16, 12, 5.5), COL_COMMERCIAL_WALL, open_faces={'-Z'})
    # Circle drive in front of the clubhouse
    from infra_library import circle_drive
    circle_drive("CountryClub_Drive", (-30, 178), radius=14.0,
                 drive_w=5.0, entry_dirs=('-Y',))

    # Harmony Park / pool — placeholder boxes
    _box("HarmonyPark_Bandshell",
         (28, 32, hce_elevation(28, 32) + 2.8),
         (12, 8, 5.5), (0.94, 0.92, 0.86, 1.0))
    _box("HarmonyPark_Pool",
         (-22, 40, hce_elevation(-22, 40) + 0.2),
         (22, 12, 0.4), (0.32, 0.65, 0.78, 1.0))
    _box("HarmonyPark_Shack",
         (5, 70, hce_elevation(5, 70) + 1.5),
         (6, 4, 3.0), (0.86, 0.78, 0.52, 1.0))

    # Halsey Studios (east edge, on the East Commercial)
    _box("HalseyStudios_Body",
         (250, 100, hce_elevation(250, 100) + 4),
         (22, 14, 8), (0.62, 0.50, 0.42, 1.0))
    _box("HalseyStudios_Roof",
         (250, 100, hce_elevation(250, 100) + 8.4),
         (24, 16, 0.6), (0.30, 0.28, 0.24, 1.0))

    # South sports field complex
    _box("SportsField_Bleachers",
         (175, -100, hce_elevation(175, -100) + 1.5),
         (24, 3, 3.0), COL_COMMERCIAL_ROOF)

    # Truck stop diner
    _box("TruckStop_Diner",
         (0, -200, hce_elevation(0, -200) + 2.5),
         (20, 10, 5.0), (0.92, 0.86, 0.70, 1.0))
    _box("TruckStop_Roof",
         (0, -200, hce_elevation(0, -200) + 5.2),
         (22, 11, 0.4), (0.30, 0.28, 0.24, 1.0))


def place_house_grid(x_min, y_min, x_max, y_max, spacing=22,
                     seed_offset=0, tag=""):
    """Drop a grid of single-family-house massing blocks. Each
    house gets a pseudo-random body colour + roof colour + slight
    rotation suggestion (by alternating dimensions). Heights sit
    on the heightmap so houses follow the topography."""
    body_palette = [COL_HOUSE_BODY_A, COL_HOUSE_BODY_B,
                    COL_HOUSE_BODY_C, COL_HOUSE_BODY_D]
    roof_palette = [COL_HOUSE_ROOF_A, COL_HOUSE_ROOF_B,
                    COL_HOUSE_ROOF_C]
    nx = max(1, int((x_max - x_min) / spacing))
    ny = max(1, int((y_max - y_min) / spacing))
    for i in range(nx):
        for j in range(ny):
            cx = x_min + spacing * (i + 0.5)
            cy = y_min + spacing * (j + 0.5)
            # Skip if too close to creek
            if creek_distance(cx, cy) < 10:
                continue
            # Skip if on a road (rough — don't place on the major arterials)
            if abs(abs(cx) - 250) < 8 or abs(abs(cy) - 167) < 8:
                continue
            if abs(cx + 30) < 7:
                continue
            seed = (i * 17 + j * 31 + seed_offset) % 1000
            body_color = body_palette[seed % len(body_palette)]
            roof_color = roof_palette[(seed // 7) % len(roof_palette)]
            # Vary footprint
            footprint_w = 8.0 + (seed % 5) * 0.4
            footprint_l = 10.0 + ((seed // 11) % 5) * 0.4
            if seed % 2:
                footprint_w, footprint_l = footprint_l, footprint_w
            z_ground = hce_elevation(cx, cy)
            house_h = 4.5 + (seed % 3) * 0.4
            _box(f"H_{tag}_{i}_{j}_Body",
                 (cx, cy, z_ground + house_h / 2),
                 (footprint_w, footprint_l, house_h),
                 body_color, open_faces={'-Z'})
            # Pitched roof — flat box for simplicity
            _box(f"H_{tag}_{i}_{j}_Roof",
                 (cx, cy, z_ground + house_h + 0.6),
                 (footprint_w + 0.4, footprint_l + 0.4, 1.2),
                 roof_color)
            # Driveway stub
            _box(f"H_{tag}_{i}_{j}_Drive",
                 (cx, cy - footprint_l / 2 - 3.0, z_ground + 0.02),
                 (3.5, 6.0, 0.04),
                 (0.30, 0.30, 0.30, 1.0))
            # Mailbox at the road edge
            from infra_library import mailbox
            mailbox(f"H_{tag}_{i}_{j}_Mailbox",
                    (cx + footprint_w / 2 + 1.0, cy - footprint_l / 2 - 5.5),
                    facing='+Y', z=z_ground)


def place_construction(cx, cy, n_lots, tag):
    """Phase III construction site — dirt, surveying flags, a
    modular trailer. Per _VOL6_WIKI.md: 'Norman Lott's modular
    trailer · NexCorp Voice's vague phrase about honoring the
    historic significance of the ground'."""
    z_ground = hce_elevation(cx, cy)
    # Bare dirt rectangle
    _box(f"{tag}_DirtPad",
         (cx, cy, z_ground + 0.02),
         (60, 40, 0.05),
         (0.55, 0.42, 0.32, 1.0))
    # Norman Lott's trailer
    _box(f"{tag}_Trailer_Body",
         (cx - 10, cy - 8, z_ground + 1.5),
         (12, 4, 3.0),
         (0.78, 0.74, 0.66, 1.0))
    _box(f"{tag}_Trailer_Roof",
         (cx - 10, cy - 8, z_ground + 3.05),
         (12.4, 4.4, 0.20),
         (0.32, 0.30, 0.26, 1.0))
    # Survey flag markers — small red dots on poles
    for i, (lx, ly) in enumerate([(8, 8), (14, -5), (-2, 10), (5, -12)]):
        _cyl(f"{tag}_SurveyFlag_{i}_Pole",
             (cx + lx, cy + ly, z_ground + 0.6),
             0.02, 1.2, COL_POLE_DARK, segments=4)
        _box(f"{tag}_SurveyFlag_{i}_Flag",
             (cx + lx + 0.15, cy + ly, z_ground + 1.05),
             (0.30, 0.04, 0.18),
             (0.78, 0.18, 0.16, 1.0))


# ════════════════════════════════════════════════════════════════
# LANDMARK ANCHOR MARKERS
# Coloured monument posts at each named hot spot so the district
# reads the same as the estuary_one map. Replaceable by full
# building geometry as each sub-sector gets a build_*.py.
# ════════════════════════════════════════════════════════════════

def build_landmark_anchors():
    """Drop a tall colour-coded monument at each named landmark.
    Categories mirror the estuary_one Landmark colours so the
    district reads as the 3D version of the planning map."""
    landmarks = [
        # commercial · yellow
        ("Kwik_Anchor",           -250, 145, COL_MONUMENT_RED,    "commercial"),
        ("NexGasGo_Anchor",       -210, 145, COL_MONUMENT_BLUE,   "commercial"),
        ("TruckStopDiner_Anchor",    0,-185, (0.95, 0.85, 0.30, 1.0), "commercial"),
        # media · orange
        ("CosmicComics_Anchor",   -250, 100, COL_MONUMENT_PURPLE, "media"),
        ("HalseyStudios_Anchor",   250, 100, COL_MONUMENT_ORANGE, "media"),
        # civic · cyan
        ("HOA_Anchor",             -10,  60, COL_MONUMENT_CYAN,   "civic"),
        ("Pool_Anchor",             15,  40, COL_MONUMENT_CYAN,   "civic"),
        ("CountryClub_Anchor",     -20, 190, COL_MONUMENT_CYAN,   "civic"),
        ("Phase2Office_Anchor",     50,-130, COL_MONUMENT_CYAN,   "civic"),
        # narrative · magenta
        ("Dambrosios_Anchor",     -195,  90, COL_MONUMENT_RED,    "narrative"),
        ("Lot7_Anchor",           -170, -60, (0.62, 0.40, 0.70, 1.0), "narrative"),
        ("Lot14_Anchor",          -150, -90, (0.62, 0.40, 0.70, 1.0), "narrative"),
        ("Lot47_Anchor",           130,  50, (0.62, 0.40, 0.70, 1.0), "narrative"),
        ("Ashberry892_Anchor",     165,  75, (0.62, 0.40, 0.70, 1.0), "narrative"),
        ("Phase3_Anchor",         -160,-135, (0.62, 0.40, 0.70, 1.0), "narrative"),
    ]
    for (name, x, y, col, _cat) in landmarks:
        z_ground = hce_elevation(x, y)
        # Tall thin pole
        _cyl(f"{name}_Pole", (x, y, z_ground + 3.0),
             0.10, 6.0, COL_POLE_DARK, segments=6)
        # Small coloured cube at the top — visible from a distance
        _box(f"{name}_Marker",
             (x, y, z_ground + 6.2),
             (1.2, 1.2, 0.8), col)


# ════════════════════════════════════════════════════════════════
# CIVIC FURNITURE — school zones, library signs, walkways, parks
# ════════════════════════════════════════════════════════════════

def build_civic_furniture():
    """Public-realm dressing per the latest user direction:
    crosswalks (already in road grid via four_way_intersection),
    school zone signs, a library sign, bus stops, public walkways
    with park benches + picnic tables."""

    # School zone signs along the south arterial (assume an
    # elementary school sits south of the South Sports Fields).
    school_zone_sign("SchoolZone_W", (150, -167), facing='+Y')
    school_zone_sign("SchoolZone_E", (220, -167), facing='-Y')

    # Library sign at the corner of Hilltop & North arterial
    # (small branch library at the country club road entrance).
    library_sign("Library_Sign", (-15, 142), facing='-Y')

    # Park signs at HCE-1 Harmony Park entries
    park_sign("HarmonyPark_SignW", (-58, 50), facing='-X')
    park_sign("HarmonyPark_SignE", (90, 60), facing='+X')

    # Public walkways through Harmony Park
    public_walkway("ParkWalk_Main", (-50, 30), (85, 30),
                   width=2.5, with_lampposts=True, lamp_spacing=20)
    public_walkway("ParkWalk_NS", (15, -10), (15, 95),
                   width=2.5, with_lampposts=True, lamp_spacing=18)
    # Founders Memorial Grove walkway
    public_walkway("FoundersWalk", (-185, 80), (-110, 80),
                   width=2.0, with_lampposts=False)
    # Creek trail (along the south side of the creek)
    public_walkway("CreekTrail_1", (-100, 50), (50, -30),
                   width=2.0)
    public_walkway("CreekTrail_2", (50, -30), (180, -130),
                   width=2.0)

    # Benches along the park walkway
    bench("ParkBench_1", (-20, 27), facing='+Y')
    bench("ParkBench_2", (40, 27), facing='+Y')
    bench("ParkBench_3", (15, 65), facing='+X')

    # Picnic tables
    picnic_table("Picnic_1", (-25, 80))
    picnic_table("Picnic_2", (60, 80))

    # Bus stops at major commercial corners
    bus_stop("BusStop_NW", (-250, 130), facing='+X', with_shelter=True)
    bus_stop("BusStop_NE", (235, 130), facing='-X', with_shelter=True)
    bus_stop("BusStop_S", (0, -170), facing='+Y', with_shelter=True)

    # Mailbox cluster at the Phase II entry
    mailbox_cluster("Phase2_Mailboxes", (50, -120), count=6)
    mailbox_cluster("EastCDS_Mailboxes", (130, 35), count=4)

    # Fire hydrants at irregular spacing along the arterials
    for (hx, hy) in [(-250, 80), (-250, -50), (245, 80), (245, -50),
                      (-30, 100), (-30, -100), (100, 80), (100, -90)]:
        fire_hydrant(f"Hydrant_{hx:+d}_{hy:+d}", (hx, hy),
                     z=hce_elevation(hx, hy))


# ════════════════════════════════════════════════════════════════
# OAK TREES SCATTERED ALONG CREEK + STREETS
# ════════════════════════════════════════════════════════════════

def build_trees():
    """Scatter mature canopy trees along the creek (~10 m back from
    the water) and along the residential streets at irregular
    spacing. Trees follow the heightmap so they sit on the ground."""
    # Creek-side cypress / oak
    for i in range(len(CREEK_POINTS) - 1):
        x0, y0 = CREEK_POINTS[i]
        x1, y1 = CREEK_POINTS[i + 1]
        n = 6
        for k in range(n):
            t = k / max(1, n - 1)
            cx = x0 + (x1 - x0) * t
            cy = y0 + (y1 - y0) * t
            dx, dy = (x1 - x0), (y1 - y0)
            length = math.hypot(dx, dy)
            if length < 0.001:
                continue
            perp_x = -dy / length; perp_y = dx / length
            for sign in (-1, 1):
                tx = cx + perp_x * 12 * sign
                ty = cy + perp_y * 12 * sign
                if creek_distance(tx, ty) < 6:
                    continue
                _make_tree(f"TreeCreek_{i}_{k}_{sign:+d}", tx, ty)

    # Country club shade trees (NW high ground)
    for (tx, ty) in [(-100, 195), (-60, 175), (40, 185), (80, 195)]:
        _make_tree(f"TreeCC_{tx:+d}_{ty:+d}", tx, ty)


def _make_tree(name, x, y):
    z = hce_elevation(x, y)
    _cyl(f"{name}_Trunk", (x, y, z + 1.75), 0.35, 3.5,
         COL_TREE_TRUNK, segments=6)
    canopy_r = 3.5 + ((int(x) * 17 + int(y) * 23) % 5) * 0.3
    _make_sphere_low(f"{name}_Canopy",
                     (x, y, z + 3.5 + canopy_r * 0.5),
                     canopy_r, COL_NATURAL_GREEN,
                     rings=3, segments=6)


# ════════════════════════════════════════════════════════════════
# EXPORT
# ════════════════════════════════════════════════════════════════

def export_glb():
    out_dir = os.path.normpath(os.path.join(_SCRIPT_DIR, OUTPUT_DIR))
    os.makedirs(out_dir, exist_ok=True)
    out_path = os.path.join(out_dir, OUTPUT_NAME)
    print(f"\n[build_harmony_district] exporting to {out_path}")
    print(f"[build_harmony_district] scene objects: {len(bpy.context.scene.objects)}")
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
        print(f"[build_harmony_district] export result: {result}")
    except Exception as e:
        print(f"[build_harmony_district] ✗ EXPORT FAILED: {e}")
        import traceback; traceback.print_exc()
        raise
    if os.path.exists(out_path):
        size = os.path.getsize(out_path)
        print(f"[build_harmony_district] ✓ wrote {out_path} ({size} bytes)")
    else:
        raise RuntimeError("GLB not written")


def main():
    clear_scene()
    build_ground()
    build_creek()
    build_roads()
    build_bridges()
    build_neighborhoods_massing()
    build_landmark_anchors()
    build_civic_furniture()
    build_trees()
    export_glb()


if __name__ == "__main__":
    main()
