"""
build_harmony_terrain.py
══════════════════════════════════════════════════════════════════
VOL 6 · HCE TERRAIN-ONLY · just the land
Per the user's directive (2026-06-14) and the locale design
manual (lore/_LOCALE_DESIGN_MANUAL.md): topography is built FIRST
and verified before anything sits on it.

Builds ONLY:
  · Subdivided ground plane sampled from hce_elevation
  · Harmony Creek water surface
  · Per-polygon vertex colour by landuse_at()
  · NOTHING ELSE — no roads, no buildings, no signs, no trees,
    no civic furniture. The land is the deliverable.

Target vertical range: ~30 m bottom-to-top across the 600 × 420 m
district. Country-club rise (~14 m peak) + secondary east ridge
(~6 m) + NW→SE tilt (±7 m) + creek ravine (−3 m below bank tops)
+ noise (±1.5 m).

Run:
    blender --background --python build_harmony_terrain.py

Output:
    godot/assets/3d/locales/harmony_terrain.glb
"""

import os
import math
import sys
import bpy

_SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, _SCRIPT_DIR)

from infra_library import (
    brick_wall, iron_lattice_fence,
    COL_BRICK_WALL, COL_BRICK_CAP, COL_IRON_FENCE,
)
from human_sculpt import human_figure

OUTPUT_DIR = "../../../assets/3d/locales"
OUTPUT_NAME = "harmony_terrain.glb"

SEASON = 0.35

def lerp_palette(t, lo, hi):
    return tuple(lo[i] + (hi[i] - lo[i]) * t for i in range(4))

# ── DISTRICT BOUNDS (matches estuary_one HCE_PARAMS) ─────────────
# 1200 × 840 m — sized to fit golf + 3 residential phases + creek
# corridor + commercial belts + parks + sports + Halsey Studios
# without crowding. See lore/_LOCALE_DESIGN_MANUAL.md.
DIST_MIN_X = -600.0
DIST_MAX_X =  600.0
DIST_MIN_Y = -420.0
DIST_MAX_Y =  420.0

# Cell size ~15 m so terrain features (the 14 m country-club rise,
# the creek ravine, the secondary east ridge) read clean.
GROUND_NX = 80
GROUND_NY = 56

# ── PALETTE (seasonal lawn + landuse zones) ──────────────────────
COL_LAWN          = lerp_palette(SEASON, (0.22, 0.55, 0.18, 1.0),
                                          (0.68, 0.62, 0.22, 1.0))
COL_NATURAL_GREEN = lerp_palette(SEASON, (0.18, 0.42, 0.18, 1.0),
                                          (0.42, 0.42, 0.18, 1.0))
COL_GOLF_GREEN    = (0.16, 0.48, 0.18, 1.0)
COL_OVERGROWN     = lerp_palette(SEASON, (0.30, 0.48, 0.26, 1.0),
                                          (0.55, 0.55, 0.28, 1.0))
COL_DIRT          = lerp_palette(SEASON, (0.58, 0.55, 0.42, 1.0),
                                          (0.76, 0.72, 0.55, 1.0))
COL_CREEK_BANK    = (0.42, 0.36, 0.26, 1.0)
COL_CREEK_WATER   = (0.32, 0.50, 0.55, 1.0)
COL_COMMERCIAL_DIRT = (0.42, 0.40, 0.36, 1.0)

# ────────────────────────────────────────────────────────────────
# HARMONY CREEK polyline (matches estuary_one HCE_CREEK)
# ────────────────────────────────────────────────────────────────
CREEK_POINTS = [
    (-560,  360),
    (-300,  160),
    ( -80,    0),
    ( 160, -140),
    ( 400, -240),
    ( 580, -360),
]
CREEK_FLOOD_WIDTH = 50.0

def creek_distance(x, y):
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


# ────────────────────────────────────────────────────────────────
# ELEVATION — must stay in sync with estuary_one and
# build_harmony_district. Single source of truth: this docstring.
# Total vertical range across the district: ~30 m peak-to-trough.
# ────────────────────────────────────────────────────────────────

def fbm(x, y, octaves=3, base_freq=1.0, lacunarity=2.0):
    total = 0.0; amp = 0.5; freq = base_freq
    for _ in range(octaves):
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


# ────────────────────────────────────────────────────────────────
# SETTLEMENTS — human-built zones get FLATTENED to a per-zone
# platform elevation. Higher target_z = more prosperous (country
# club > north ranch > east CDS > west estates > Phase III).
# Per the design manual: humans build on relatively flat land;
# the wild zones BETWEEN them keep all the topographic drama.
# ────────────────────────────────────────────────────────────────
# Format: (name, x_min, x_max, y_min, y_max, target_z, flatness)
SETTLEMENTS = [
    # Country club + golf — peak prosperity, top of the hill
    ("CountryClub", -460, 440, 340, 420, +22.0, 0.85),
    # North Ranch Homes — second-highest tier
    ("NorthRanch",  -460, -200, 20, 260, +12.0, 0.80),
    # East CDS Estates — sits on the east ridge
    ("EastCDS",     180, 440, 20, 260, +8.0, 0.80),
    # Phase II construction (under occupancy) — middle tier
    ("Phase2",      40, 240, -260, -100, +1.0, 0.75),
    # West Estates (single-family) — modest lowland
    ("WestEstates", -460, -120, -340, -40, -3.0, 0.78),
    # Phase III construction (Norman Lott) — gone-to-seed low
    ("Phase3",      -460, -260, -340, -180, -8.0, 0.70),
    # North Commercial Belt — between CC and Ranch, sloped
    ("NorthComm",   -460, 440, 260, 340, +14.0, 0.75),
    # East Commercial
    ("EastComm",    440, 540, -340, 260, +5.0, 0.80),
    # West Commercial Strip (Highway 9 lowland)
    ("WestComm",    -560, -460, -340, 260, -2.0, 0.85),
    # South Commercial / Truck Stop (low — truck route)
    ("SouthComm",   -460, 440, -400, -340, -9.0, 0.85),
    # Harmony Park (manicured — flatter than wild, less than housing)
    ("HarmonyPark", -120, 180, -40, 200, +1.0, 0.55),
    # Dedicated platform around the Oliver Tree statue so the
    # walkways + benches + reflecting pool all sit flat
    ("OliverTreeMemPark", -300, -220, 60, 180, +2.0, 0.80),
]
SETTLEMENT_FALLOFF = 35.0   # m of smooth transition outside each rect

# ────────────────────────────────────────────────────────────────
# PONDS, POOLS, MINI-VALLEYS — features in the WILD zones between
# settlements. Add character to the in-between spaces.
# ────────────────────────────────────────────────────────────────
# Format: (name, cx, cy, radius, depth)  depth is positive metres
PONDS = [
    # Wider + deeper than the v1 ponds. Format: (name, cx, cy, radius, depth)
    # WATER_SURFACE_Z is how far below GROUND_Z the water plane sits;
    # depth is the terrain depression amount.
    ("FoundersPond",   -300,  140,  45, 10.0),    # big anchor pond in Founders Grove
    ("HarmonyPond",      30,   60,  32,  6.0),    # community pool placement
    ("WildLotPond",    -340, -240,  38,  8.0),    # gone-to-seed wild pond
    ("SECreekPond",     360, -120,  40,  9.0),    # moved AWAY from the creek so it reads
    ("NWHeadwatersPond",-440,  280,  30,  6.0),
    ("EastWoodsPond",   320,  310,  28,  5.0),
    ("MidValleyPond",     0, -180,  35,  7.0),    # NEW · in the SE-basin wild zone
]


def smoothstep(edge0, edge1, x):
    if x <= edge0: return 0.0
    if x >= edge1: return 1.0
    t = (x - edge0) / (edge1 - edge0)
    return t * t * (3 - 2 * t)


def settlement_blend(x, y, x_min, x_max, y_min, y_max, falloff=SETTLEMENT_FALLOFF):
    """Returns 1.0 fully inside the rectangle, smoothstepping to 0
    over `falloff` meters outside. Used to flatten human-built zones
    toward their platform elevation."""
    dx = max(x_min - x, 0.0, x - x_max)
    dy = max(y_min - y, 0.0, y - y_max)
    d = math.hypot(dx, dy)
    return 1.0 - smoothstep(0, falloff, d)


def pond_depression(x, y, cx, cy, radius, depth):
    """Negative bump at (cx, cy) with smooth circular falloff."""
    d = math.hypot(x - cx, y - cy)
    return -depth * math.exp(-d * d / (radius * radius))


def hce_elevation(x, y):
    """Per the design manual: humans build on relatively flat land;
    wild zones in between keep ALL the topographic drama. Higher
    altitude = more prosperous community.

    Base terrain (~40 m peak-to-trough):
      · NW country-club hill   +22 m   (the most prosperous)
      · East ridge             +10 m   (east CDS estates)
      · NW headwaters knoll     +8 m
      · SE basin               -8 m
      · NW→SE tilt            ±10 m
      · Creek ravine          -7 m
      · Multi-scale fbm noise ±5.5 m

    Then six PONDS / mini-pools punch wild-zone depressions in
    between settlements, and ELEVEN settlement zones flatten the
    base toward their per-zone platform elevation — country club
    +22 m at the top, Phase III construction -8 m at the bottom.
    """
    # ── Base terrain ─────────────────────────────────────────────
    tilt = 10.0 * ((-(x) + y) / 1200.0)
    cc_dx = x - 0
    cc_dy = y - 380
    cc_rise = 22.0 * math.exp(-(cc_dx * cc_dx + cc_dy * cc_dy) / (180.0 * 180.0))
    east_dx = x - 480
    east_dy = y - 80
    east_rise = 10.0 * math.exp(-(east_dx * east_dx + east_dy * east_dy) / (150.0 * 150.0))
    nw_dx = x + 400
    nw_dy = y - 280
    nw_rise = 8.0 * math.exp(-(nw_dx * nw_dx + nw_dy * nw_dy) / (140.0 * 140.0))
    south_dx = x - 80
    south_dy = y + 280
    south_dip = -8.0 * math.exp(-(south_dx * south_dx + south_dy * south_dy) / (180.0 * 180.0))
    noise_low = (fbm(x * 0.003, y * 0.003, octaves=3) - 0.5) * 4.0
    noise_high = (fbm(x * 0.012, y * 0.012, octaves=2) - 0.5) * 1.5
    creek_d = creek_distance(x, y)
    creek_dip = -7.0 * math.exp(-creek_d * creek_d / (CREEK_FLOOD_WIDTH ** 2))
    base = (tilt + cc_rise + east_rise + nw_rise + south_dip
            + noise_low + noise_high + creek_dip)

    # ── Pond depressions (carve into wild zones) ─────────────────
    for (_name, cx, cy, r, d) in PONDS:
        base += pond_depression(x, y, cx, cy, r, d)

    # ── Settlement flattening ────────────────────────────────────
    # Each rectangle pulls the elevation toward its platform z by
    # `flatness`. Multiple overlapping zones blend by max-weight.
    best_blend = 0.0
    best_target = 0.0
    for (_n, x_min, x_max, y_min, y_max, target_z, flatness) in SETTLEMENTS:
        b = settlement_blend(x, y, x_min, x_max, y_min, y_max) * flatness
        if b > best_blend:
            best_blend = b
            best_target = target_z

    if best_blend > 0.001:
        flattened = base * (1 - best_blend) + best_target * best_blend
    else:
        flattened = base

    # ── Suburban BERMS — artificial linear hillocks between
    # settlements and the surrounding world. Per user direction:
    # "suburbs have lots of artificial slopes and hills to obstruct
    # views of homes." Each berm is a Gaussian ridge along a
    # polyline. Stacked on TOP of the flattened residential
    # platforms so the platform stays buildable but the property
    # edge gets a view-blocking rise.
    for (_n, polyline, width, height) in BERMS:
        flattened += berm_ridge(x, y, polyline, width, height)
    return flattened


# ────────────────────────────────────────────────────────────────
# BERMS — artificial linear slopes between settlements and the
# outside world. Each is a polyline + width + height; the elevation
# adds a Gaussian ridge along the line.
# ────────────────────────────────────────────────────────────────
BERMS = [
    # Country club perimeter berm — separates golf from commercial
    ("CC_Buffer",        [(-460, 340), (440, 340)],          14.0, 2.5),
    # North Ranch street-facing berm (blocks views from arterials)
    ("NorthRanch_Front", [(-460, 270), (-200, 270)],         10.0, 1.8),
    ("NorthRanch_South", [(-460, 25), (-200, 25)],           10.0, 1.5),
    # East CDS Estates frontage berm
    ("EastCDS_Front",    [(180, 270), (440, 270)],           10.0, 1.8),
    ("EastCDS_South",    [(180, 25), (440, 25)],             10.0, 1.5),
    # West Estates road berm
    ("WestEstates_E",    [(-120, -340), (-120, -40)],        9.0, 1.4),
    ("WestEstates_N",    [(-460, -30), (-120, -30)],         9.0, 1.4),
    # Phase II buffer berm (visually separates the new construction)
    ("Phase2_N",         [(40, -100), (240, -100)],          8.0, 1.5),
    # Wild Lot perimeter — keeps the gone-to-seed look in
    ("WildLot_Edge",     [(-400, -180), (-260, -180)],       6.0, 1.5),
]


def berm_segment_dist(x, y, polyline):
    """Closest distance from (x, y) to the polyline."""
    best = float("inf")
    for i in range(len(polyline) - 1):
        x0, y0 = polyline[i]
        x1, y1 = polyline[i + 1]
        dx = x1 - x0; dy = y1 - y0
        l2 = dx * dx + dy * dy
        if l2 < 0.001:
            continue
        t = max(0.0, min(1.0, ((x - x0) * dx + (y - y0) * dy) / l2))
        px = x0 + dx * t; py = y0 + dy * t
        d = math.hypot(x - px, y - py)
        if d < best:
            best = d
    return best


def berm_ridge(x, y, polyline, width, height):
    d = berm_segment_dist(x, y, polyline)
    return height * math.exp(-d * d / (width * width))


def landuse_at(x, y):
    """Coarse landuse classifier on the 1200 × 840 m district.
    All polygons 2× the original sketch. No buildings or roads
    yet — the per-zone colour helps verify the design intent."""
    # Country club golf course (irrigated — stays green)
    if -460 < x < 440 and 340 < y < 420:
        return 'golf'
    # Creek bank
    if creek_distance(x, y) < 14.0:
        return 'creek_bank'
    # Commercial belts — DIRT for now (roads come next)
    if -560 <= x <= -460 and -340 <= y <= 260:
        return 'commercial_dirt'
    if x >= 440 and -340 <= y <= 260:
        return 'commercial_dirt'
    if -460 <= x <= 440 and 260 <= y <= 340:
        return 'commercial_dirt'
    if -460 <= x <= 440 and -400 <= y <= -340:
        return 'commercial_dirt'
    # Harmony Park
    if -120 <= x <= 180 and -40 <= y <= 200:
        return 'park'
    # Founders Memorial Grove
    if -400 <= x <= -200 and 100 <= y <= 220:
        return 'natural'
    # Wild lot
    if -400 <= x <= -260 and -300 <= y <= -180:
        return 'overgrown'
    return 'lawn'


def color_for(x, y):
    lu = landuse_at(x, y)
    if lu == 'golf':            return COL_GOLF_GREEN
    if lu == 'creek_bank':      return COL_CREEK_BANK
    if lu == 'commercial_dirt': return COL_COMMERCIAL_DIRT
    if lu == 'park':            return COL_LAWN
    if lu == 'natural':         return COL_NATURAL_GREEN
    if lu == 'overgrown':       return COL_OVERGROWN
    return COL_LAWN


# ────────────────────────────────────────────────────────────────
# PRIMITIVES
# ────────────────────────────────────────────────────────────────

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


def clear_scene():
    bpy.ops.object.select_all(action='SELECT')
    bpy.ops.object.delete(use_global=False)
    for block in bpy.data.meshes:
        bpy.data.meshes.remove(block)


def build_ground():
    """Subdivided heightmap. Per-vertex elevation; per-polygon
    colour from landuse_at() sampled at the polygon centre."""
    verts = []
    nx_plus_1 = GROUND_NX + 1
    for j in range(GROUND_NY + 1):
        wy = DIST_MIN_Y + (DIST_MAX_Y - DIST_MIN_Y) * j / GROUND_NY
        for i in range(nx_plus_1):
            wx = DIST_MIN_X + (DIST_MAX_X - DIST_MIN_X) * i / GROUND_NX
            z = hce_elevation(wx, wy)
            verts.append((wx, wy, z))
    faces = []
    for j in range(GROUND_NY):
        for i in range(GROUND_NX):
            a = j * nx_plus_1 + i
            b = a + 1
            c = b + nx_plus_1
            d = a + nx_plus_1
            faces.append([a, b, c, d])
    mesh = bpy.data.meshes.new("Terrain_mesh")
    mesh.from_pydata(verts, [], faces)
    mesh.update()
    if not mesh.vertex_colors:
        mesh.vertex_colors.new(name="Col")
    layer = mesh.vertex_colors["Col"]
    z_min = min(v[2] for v in verts)
    z_max = max(v[2] for v in verts)
    print(f"[build_harmony_terrain] elevation range: "
          f"{z_min:+.2f} m → {z_max:+.2f} m "
          f"(spread {z_max - z_min:.1f} m)")
    for poly in mesh.polygons:
        cx = sum(verts[v][0] for v in poly.vertices) / len(poly.vertices)
        cy = sum(verts[v][1] for v in poly.vertices) / len(poly.vertices)
        col = color_for(cx, cy)
        for li in poly.loop_indices:
            layer.data[li].color = col
    obj = bpy.data.objects.new("Terrain", mesh)
    bpy.context.collection.objects.link(obj)
    return obj


def build_creek():
    """Water surface quads sitting inside the flood-plain ravine.
    Bank tops at ~0 m; water surface at ~−2.2 m (just below mean
    bank elevation so a real ravine reads on either side)."""
    water_z = -2.2
    width = 6.0
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


# ────────────────────────────────────────────────────────────────
# EXPORT
# ────────────────────────────────────────────────────────────────

def export_glb():
    out_dir = os.path.normpath(os.path.join(_SCRIPT_DIR, OUTPUT_DIR))
    os.makedirs(out_dir, exist_ok=True)
    out_path = os.path.join(out_dir, OUTPUT_NAME)
    print(f"\n[build_harmony_terrain] exporting to {out_path}")
    print(f"[build_harmony_terrain] scene objects: {len(bpy.context.scene.objects)}")
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
        print(f"[build_harmony_terrain] export result: {result}")
    except Exception as e:
        print(f"[build_harmony_terrain] ✗ EXPORT FAILED: {e}")
        import traceback; traceback.print_exc()
        raise
    if os.path.exists(out_path):
        size = os.path.getsize(out_path)
        print(f"[build_harmony_terrain] ✓ wrote {out_path} ({size} bytes)")
    else:
        raise RuntimeError("GLB not written")


def build_feature_beacons():
    """Tall thin colour-coded survey poles at every named terrain
    feature. The user can fly across the district and SEE where
    each pond / settlement / hill peak lives. NOT buildings — these
    are deliberately stick-thin survey markers, removable later
    when full geometry replaces them."""
    BEACON_H = 60.0    # tall enough to clear any berm / hill
    BEACON_R = 0.40
    BEACON_TOP_BOX = 3.0

    # Settlement beacons — colour-coded by prosperity tier
    settlement_beacons = [
        ("Beacon_CountryClub",   0,    380, (0.95, 0.85, 0.30, 1.0)),  # gold
        ("Beacon_NorthRanch",   -330,  140, (0.85, 0.78, 0.62, 1.0)),
        ("Beacon_EastCDS",       310,  140, (0.85, 0.78, 0.62, 1.0)),
        ("Beacon_Phase2",        140, -180, (0.62, 0.55, 0.45, 1.0)),
        ("Beacon_WestEstates", -290, -190, (0.55, 0.50, 0.42, 1.0)),
        ("Beacon_Phase3",      -360, -260, (0.45, 0.35, 0.28, 1.0)),
        ("Beacon_TruckStop",      0, -370, (0.40, 0.32, 0.26, 1.0)),
    ]

    # Red fence-corner beacons — only for the four strategic fence
    # runs we actually emit, so each red dot maps 1:1 to a real fence.
    fence_beacons = [
        ("Beacon_Fence_CC_S_W",      -440, 345, (0.85, 0.18, 0.16, 1.0)),
        ("Beacon_Fence_CC_S_E",       420, 345, (0.85, 0.18, 0.16, 1.0)),
        ("Beacon_Fence_NRanch_NW",   -440, 250, (0.85, 0.18, 0.16, 1.0)),
        ("Beacon_Fence_NRanch_PondS",-220,  80, (0.85, 0.18, 0.16, 1.0)),
        ("Beacon_Fence_Phase2_N_W",   50, -110, (0.85, 0.18, 0.16, 1.0)),
        ("Beacon_Fence_Phase2_N_E",  230, -110, (0.85, 0.18, 0.16, 1.0)),
    ]
    settlement_beacons += fence_beacons
    for (name, x, y, col) in settlement_beacons:
        z = hce_elevation(x, y)
        _cyl(name + "_Pole", (x, y, z + BEACON_H / 2),
             BEACON_R, BEACON_H, (0.10, 0.10, 0.10, 1.0),
             segments=6)
        # Coloured top
        _finalize_mesh(
            name + "_Top",
            [
                (x - BEACON_TOP_BOX, y - BEACON_TOP_BOX, z + BEACON_H - 1),
                (x + BEACON_TOP_BOX, y - BEACON_TOP_BOX, z + BEACON_H - 1),
                (x + BEACON_TOP_BOX, y + BEACON_TOP_BOX, z + BEACON_H - 1),
                (x - BEACON_TOP_BOX, y + BEACON_TOP_BOX, z + BEACON_H - 1),
                (x - BEACON_TOP_BOX, y - BEACON_TOP_BOX, z + BEACON_H + 2),
                (x + BEACON_TOP_BOX, y - BEACON_TOP_BOX, z + BEACON_H + 2),
                (x + BEACON_TOP_BOX, y + BEACON_TOP_BOX, z + BEACON_H + 2),
                (x - BEACON_TOP_BOX, y + BEACON_TOP_BOX, z + BEACON_H + 2),
            ],
            [[4,5,6,7],[0,3,2,1],[0,1,5,4],[2,3,7,6],[0,4,7,3],[1,2,6,5]],
            col,
        )

    # Pond beacons — cyan
    cyan = (0.18, 0.78, 0.92, 1.0)
    for (name, cx, cy, _r, _d) in PONDS:
        z = hce_elevation(cx, cy)
        _cyl(f"PondBeacon_{name}_Pole",
             (cx, cy, z + BEACON_H / 2),
             BEACON_R, BEACON_H, (0.10, 0.10, 0.10, 1.0),
             segments=6)
        _finalize_mesh(
            f"PondBeacon_{name}_Top",
            [
                (cx - 2, cy - 2, z + BEACON_H - 1),
                (cx + 2, cy - 2, z + BEACON_H - 1),
                (cx + 2, cy + 2, z + BEACON_H - 1),
                (cx - 2, cy + 2, z + BEACON_H - 1),
                (cx - 2, cy - 2, z + BEACON_H + 1.5),
                (cx + 2, cy - 2, z + BEACON_H + 1.5),
                (cx + 2, cy + 2, z + BEACON_H + 1.5),
                (cx - 2, cy + 2, z + BEACON_H + 1.5),
            ],
            [[4,5,6,7],[0,3,2,1],[0,1,5,4],[2,3,7,6],[0,4,7,3],[1,2,6,5]],
            cyan,
        )


def _cyl(name, center, radius, height, color, segments=8):
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


def build_pond_water():
    """Blue water disc + sandy beach ring at each pond. Pass 2
    adds: a second darker-blue inner disc for depth read,
    cattail/reed clumps at the perimeter, and lily-pad discs
    floating on the surface."""
    segments = 20
    for (name, cx, cy, radius, _depth) in PONDS:
        bottom_z = hce_elevation(cx, cy)
        water_z = bottom_z + 1.5
        wr = radius * 0.80
        # Outer water disc (lighter — shallow rim)
        verts = [(cx, cy, water_z)]
        for i in range(segments):
            ang = 2.0 * math.pi * i / segments
            verts.append((cx + math.cos(ang) * wr,
                          cy + math.sin(ang) * wr, water_z))
        faces = []
        for i in range(segments):
            ni = (i + 1) % segments
            faces.append([0, 1 + i, 1 + ni])
        _finalize_mesh(f"PondWater_{name}", verts, faces,
                       (0.40, 0.62, 0.68, 1.0))    # lighter teal
        # Inner darker disc — reads as depth
        ir = wr * 0.55
        verts2 = [(cx, cy, water_z + 0.005)]
        for i in range(segments):
            ang = 2.0 * math.pi * i / segments
            verts2.append((cx + math.cos(ang) * ir,
                           cy + math.sin(ang) * ir,
                           water_z + 0.005))
        faces2 = []
        for i in range(segments):
            ni = (i + 1) % segments
            faces2.append([0, 1 + i, 1 + ni])
        _finalize_mesh(f"PondDeep_{name}", verts2, faces2,
                       (0.18, 0.32, 0.42, 1.0))    # deep navy
        # Sandy beach ring outside the water
        outer = radius * 0.95
        beach_z = water_z + 0.15
        bverts = []
        for ring in (0, 1):
            r = wr if ring == 0 else outer
            for i in range(segments):
                ang = 2.0 * math.pi * i / segments
                bverts.append((cx + math.cos(ang) * r,
                               cy + math.sin(ang) * r,
                               beach_z))
        bfaces = []
        for i in range(segments):
            ni = (i + 1) % segments
            bfaces.append([i, ni, ni + segments, i + segments])
        _finalize_mesh(f"PondBeach_{name}", bverts, bfaces,
                       (0.78, 0.72, 0.52, 1.0))

        # ── Lily pads — small green discs scattered on the surface
        # Deterministic placement so each pond gets the same set
        # across rebuilds.
        n_pads = max(3, int(radius / 8))
        for k in range(n_pads):
            t = k / n_pads
            ang = 6.2831 * (t * 1.7 + 0.31)        # spiraled placement
            pr = wr * 0.30 + wr * 0.40 * (t * 0.83 % 1.0)
            lx = cx + math.cos(ang) * pr
            ly = cy + math.sin(ang) * pr
            _disc_low(f"PondLily_{name}_{k}",
                      (lx, ly, water_z + 0.04),
                      0.4 + 0.15 * (k % 3), (0.22, 0.55, 0.28, 1.0),
                      segments=8)

        # ── Reed / cattail clumps at the bank ──
        # Tall thin green-brown stalks ringing the outer edge of
        # the beach.
        n_clumps = max(4, int(radius / 6))
        for k in range(n_clumps):
            ang = 6.2831 * k / n_clumps + 0.13
            rx = cx + math.cos(ang) * outer * 1.04
            ry = cy + math.sin(ang) * outer * 1.04
            _reed_clump(f"PondReeds_{name}_{k}", rx, ry,
                        ground_z=beach_z, count=5)


def _disc_low(name, center, radius, color, segments=8):
    cx, cy, cz = center
    verts = [(cx, cy, cz)]
    for i in range(segments):
        ang = 2.0 * math.pi * i / segments
        verts.append((cx + math.cos(ang) * radius,
                      cy + math.sin(ang) * radius, cz))
    faces = []
    for i in range(segments):
        ni = (i + 1) % segments
        faces.append([0, 1 + i, 1 + ni])
    _finalize_mesh(name, verts, faces, color)


def _reed_clump(name, cx, cy, ground_z, count=5):
    """A small clump of thin tall reeds with brown cattail tops.
    count = number of stalks. Each stalk is a thin vertical box
    with a darker brown cap. Deterministic placement around (cx, cy)."""
    for i in range(count):
        ang = 6.2831 * i / count + 0.21 * (i % 3)
        ox = math.cos(ang) * 0.20
        oy = math.sin(ang) * 0.20
        stalk_h = 0.95 + 0.15 * (i % 3)
        # Green stalk
        _make_box_local(f"{name}_Stalk_{i}",
                        (cx + ox, cy + oy, ground_z + stalk_h / 2),
                        (0.04, 0.04, stalk_h),
                        (0.32, 0.55, 0.22, 1.0))
        # Brown cattail head at the top
        _make_box_local(f"{name}_Head_{i}",
                        (cx + ox, cy + oy, ground_z + stalk_h - 0.10),
                        (0.07, 0.07, 0.20),
                        (0.45, 0.30, 0.18, 1.0))


def _fence_along(name, p0, p1, fence_type, sub_len=40.0):
    """Subdivide (p0, p1) into ~sub_len pieces and place a fence
    segment at each, sampling elevation at the midpoint of each
    piece. sub_len bumped from 10 m to 40 m so a 300 m fence emits
    8 segments instead of 30 — each segment internally still
    contains rails + bars + end posts, but at 1/4 the segment
    count we cut the total MeshInstance3D node count by 4x. Godot's
    import was hanging on the dense version."""
    x0, y0 = p0; x1, y1 = p1
    length = math.hypot(x1 - x0, y1 - y0)
    if length < 0.001:
        return
    n = max(1, int(length / sub_len))
    for i in range(n):
        t0 = i / n; t1 = (i + 1) / n
        sp0 = (x0 + (x1 - x0) * t0, y0 + (y1 - y0) * t0)
        sp1 = (x0 + (x1 - x0) * t1, y0 + (y1 - y0) * t1)
        mx = (sp0[0] + sp1[0]) / 2
        my = (sp0[1] + sp1[1]) / 2
        z = hce_elevation(mx, my)
        if fence_type == 'iron':
            iron_lattice_fence(f"{name}_{i}", sp0, sp1, z=z, height=1.4)
        elif fence_type == 'brick':
            brick_wall(f"{name}_{i}", sp0, sp1, z=z, height=1.8)


def build_district_fences():
    """Place fences STRATEGICALLY per user direction (2026-06-14):
    "use them strategically." Fences are punctuation, not
    paragraphs — four signature runs that read the design intent
    without blanketing every settlement edge.

    The four picks:
      1. Country club golf south perimeter — the iconic boundary
         between wealth and the rest of the district.
      2. North Ranch east edge facing Founders Grove pond — the
         canonical iron-lattice "amenity view preserved" beat.
      3. North Ranch north edge backing onto North Commercial Belt
         — the most prominent residential / arterial brick wall.
      4. Phase II construction north perimeter — under-construction
         privacy wall; signals the in-progress phase.

    All other fence placements (East CDS perimeters, West Estates
    walls, etc.) deferred to each sub-sector's own build_*.py
    script when that sub-sector lands. Keeps polycount low and
    preserves the manual's wall-vs-fence rule as PUNCTUATION."""

    # IRON LATTICE — preserving the amenity view
    _fence_along("CC_GolfPerim_S", (-440, 345), (420, 345), 'iron')
    _fence_along("NorthRanch_PondFence", (-220, 80), (-220, 200), 'iron')

    # BRICK WALLS — privacy along arterials
    _fence_along("NorthRanch_NorthWall", (-440, 250), (-220, 250), 'brick')
    _fence_along("Phase2_NorthWall", (50, -110), (230, -110), 'brick')


def build_oliver_tree_memorial():
    """Public-works statue of Oliver Tree in Founders Memorial Grove
    (-260, +120). Rebuilt on top of human_sculpt.human_figure so
    the silhouette reads as a recognizable person, not abstract
    box-stack. 2× scale (3.6 m tall figure) on a 1.5 m plinth.

    Signature elements wired through human_figure parameters:
      · hair_style='bowl'  — the mushroom bowl-cut + forward bang
      · pants_flare=2.6    — the JNCO wide-leg flare
      · jacket pink body + purple yoke + pink star accent
      · yellow scarf at the collar
      · pink-red sunglasses band across the eye line"""
    sx, sy = -260.0, 120.0
    ground_z = hce_elevation(sx, sy)

    # ── Plinth ──────────────────────────────────────────────────
    COL_PLINTH = (0.78, 0.74, 0.66, 1.0)
    COL_PLAQUE = (0.65, 0.48, 0.20, 1.0)
    plinth_w = 2.6
    plinth_d = 2.2
    plinth_h = 1.5
    plinth_z = ground_z + plinth_h / 2
    _make_box_local("OT_Plinth",
                    (sx, sy, plinth_z),
                    (plinth_w, plinth_d, plinth_h),
                    COL_PLINTH)
    # Brass plaque on the front (south face)
    _make_box_local("OT_Plaque",
                    (sx, sy - plinth_d / 2 - 0.04, plinth_z + 0.10),
                    (1.6, 0.08, 0.60),
                    COL_PLAQUE)

    # ── The figure itself, via the human_sculpt pipeline ────────
    base_z = ground_z + plinth_h   # feet sit on top of the plinth
    human_figure(
        name="OT",
        base_x=sx, base_y=sy, base_z=base_z,
        scale=2.0,                    # 3.6 m statue
        facing='-Y',                  # plaque/face point south
        skin_color=(0.92, 0.75, 0.62, 1.0),
        hair_style='bowl',
        hair_color=(0.32, 0.22, 0.16, 1.0),
        jacket_color=(0.95, 0.42, 0.62, 1.0),     # hot pink
        yoke_color=(0.62, 0.42, 0.78, 1.0),       # purple shoulder yoke
        accent='star',
        accent_color=(0.95, 0.42, 0.62, 1.0),     # pink star on chest
        scarf_color=(0.95, 0.85, 0.35, 1.0),      # yellow scarf
        pants_color=(0.55, 0.68, 0.82, 1.0),      # denim blue
        pants_flare=2.6,                          # JNCO wide-leg
        shoe_color=(0.92, 0.90, 0.84, 1.0),       # white shoes
        has_sunglasses=True,
        sunglasses_color=(0.95, 0.30, 0.45, 1.0), # pink-red lenses
    )

    # Beacon moved to the park's south entry so it doesn't obscure
    # the figure. See build_oliver_tree_memorial_park().


def build_oliver_tree_memorial_park():
    """The Oliver Tree Memorial Park — 80 × 120 m platform around
    the statue inside Founders Memorial Grove. Per user direction
    (2026-06-14): "design a pleasant suburban park, The Oliver
    Tree Memorial Park. With pathways, and terraced hills and nice
    spots to have a picnic or relax under some older growth trees."

    Build:
      · Central walkway ring (12 m inner / 15 m outer concrete)
      · Four radial paths (N/S/E/W) connecting to the perimeter
      · A two-step TERRACED RISE at the north end — the elevated
        view-point overlooking the statue + reflecting pool
      · Reflecting pool 22 m south of statue (the contemplation
        focal point)
      · 8 mature OAKS forming a loose ring outside the walkways
      · 3 picnic tables in shaded spots under the oaks
      · 5 benches around the central ring + on the terrace
      · Brown park sign at the south entry
      · Pink flower planters at each cardinal point of the inner
        ring (pink for Oliver Tree's signature jacket colour)
      · Beacon relocated to the south entry so it doesn't tower
        over the statue
    """
    sx, sy = -260.0, 120.0      # statue centre (sub-platform)
    park_z = hce_elevation(sx, sy)   # platform z after settlement flatten

    COL_PATH        = (0.78, 0.74, 0.66, 1.0)
    COL_TERRACE     = (0.82, 0.78, 0.68, 1.0)
    COL_OAK_TRUNK   = (0.30, 0.22, 0.16, 1.0)
    COL_OAK_CANOPY  = (0.22, 0.42, 0.20, 1.0)
    COL_OAK_CANOPY2 = (0.30, 0.48, 0.22, 1.0)
    COL_POOL_WATER  = (0.30, 0.52, 0.62, 1.0)
    COL_POOL_RIM    = (0.78, 0.74, 0.66, 1.0)
    COL_FLOWER_PINK = (0.95, 0.42, 0.62, 1.0)
    COL_FLOWER_BED  = (0.42, 0.30, 0.20, 1.0)
    COL_BENCH       = (0.42, 0.30, 0.20, 1.0)
    COL_PICNIC      = (0.48, 0.36, 0.24, 1.0)
    COL_SIGN_BROWN  = (0.40, 0.30, 0.20, 1.0)
    COL_SIGN_FACE   = (0.86, 0.82, 0.70, 1.0)

    # ── Central walkway ring (inner 12, outer 15) ─────────────
    segs = 18
    inner_r = 12.0; outer_r = 15.0
    ring_verts = []
    for ring_idx, r in ((0, inner_r), (1, outer_r)):
        for i in range(segs):
            ang = 2.0 * math.pi * i / segs
            ring_verts.append((sx + math.cos(ang) * r,
                                sy + math.sin(ang) * r,
                                park_z + 0.02))
    ring_faces = []
    for i in range(segs):
        ni = (i + 1) % segs
        ring_faces.append([i, ni, ni + segs, i + segs])
    _finalize_mesh("OTPark_RingWalk", ring_verts, ring_faces, COL_PATH)

    # ── 4 radial paths (N/S/E/W from ring to perimeter) ───────
    path_w = 2.4
    radials = [
        ('N', 0,  1, 30),
        ('S', 0, -1, 50),     # south path longest — main entry
        ('E', 1,  0, 25),
        ('W', -1, 0, 25),
    ]
    for tag, dx, dy, length in radials:
        start_x = sx + dx * outer_r
        start_y = sy + dy * outer_r
        end_x = sx + dx * (outer_r + length)
        end_y = sy + dy * (outer_r + length)
        if abs(dx) > abs(dy):
            _make_box_local(f"OTPark_Path_{tag}",
                            ((start_x + end_x) / 2,
                             (start_y + end_y) / 2,
                             park_z + 0.02),
                            (length, path_w, 0.04), COL_PATH)
        else:
            _make_box_local(f"OTPark_Path_{tag}",
                            ((start_x + end_x) / 2,
                             (start_y + end_y) / 2,
                             park_z + 0.02),
                            (path_w, length, 0.04), COL_PATH)

    # ── Terraced rise at the NORTH end — two short steps up ──
    # Step 1: 22 × 8 m at +0.6 m
    _make_box_local("OTPark_Terrace_1",
                    (sx, sy + outer_r + 30 + 6, park_z + 0.30),
                    (22, 12, 0.60), COL_TERRACE)
    # Step 2: 14 × 6 m at +1.2 m on top of step 1
    _make_box_local("OTPark_Terrace_2",
                    (sx, sy + outer_r + 30 + 8, park_z + 0.90),
                    (14, 8, 0.60), COL_TERRACE)
    # Terrace railings — short walls along the front edge of step 2
    _make_box_local("OTPark_Terrace_Rail_L",
                    (sx - 6.5, sy + outer_r + 30 + 4.2, park_z + 1.50),
                    (1.5, 0.20, 0.60), COL_TERRACE)
    _make_box_local("OTPark_Terrace_Rail_R",
                    (sx + 6.5, sy + outer_r + 30 + 4.2, park_z + 1.50),
                    (1.5, 0.20, 0.60), COL_TERRACE)
    # Two stair stubs leading up to step 1
    for ox in (-5, 5):
        _make_box_local(f"OTPark_Stairs_{ox:+d}",
                        (sx + ox, sy + outer_r + 30 - 1.5,
                         park_z + 0.15),
                        (2.0, 1.5, 0.30), COL_TERRACE)

    # ── Reflecting pool 22 m SOUTH of statue ──────────────────
    pool_cx = sx
    pool_cy = sy - 22
    pool_r = 6.0
    # Recessed water disc
    pool_segs = 16
    pverts = [(pool_cx, pool_cy, park_z - 0.30)]
    for i in range(pool_segs):
        ang = 2.0 * math.pi * i / pool_segs
        pverts.append((pool_cx + math.cos(ang) * pool_r,
                       pool_cy + math.sin(ang) * pool_r,
                       park_z - 0.30))
    pfaces = []
    for i in range(pool_segs):
        ni = (i + 1) % pool_segs
        pfaces.append([0, 1 + i, 1 + ni])
    _finalize_mesh("OTPark_Pool", pverts, pfaces, COL_POOL_WATER)
    # Concrete rim
    rverts = []
    for ring_idx, r in ((0, pool_r), (1, pool_r + 0.6)):
        for i in range(pool_segs):
            ang = 2.0 * math.pi * i / pool_segs
            rverts.append((pool_cx + math.cos(ang) * r,
                           pool_cy + math.sin(ang) * r,
                           park_z + 0.05))
    rfaces = []
    for i in range(pool_segs):
        ni = (i + 1) % pool_segs
        rfaces.append([i, ni, ni + pool_segs, i + pool_segs])
    _finalize_mesh("OTPark_Pool_Rim", rverts, rfaces, COL_POOL_RIM)

    # ── 8 mature OAKS — older growth, big canopies ────────────
    oak_positions = [
        (sx - 28, sy - 10), (sx - 28, sy + 12),
        (sx + 28, sy - 10), (sx + 28, sy + 12),
        (sx - 18, sy + 26), (sx + 18, sy + 26),
        (sx - 18, sy - 26), (sx + 18, sy - 26),
    ]
    for i, (ox, oy) in enumerate(oak_positions):
        trunk_h = 5.5     # taller than the wild-zone oaks
        canopy_r = 5.5    # wider canopy = old-growth
        _make_cyl_local(f"OTPark_Oak_{i}_Trunk",
                        (ox, oy, park_z + trunk_h / 2),
                        0.50, trunk_h, COL_OAK_TRUNK, segments=6)
        col = COL_OAK_CANOPY if i % 2 == 0 else COL_OAK_CANOPY2
        _make_sphere_low_local(
            f"OTPark_Oak_{i}_Canopy",
            (ox, oy, park_z + trunk_h + canopy_r * 0.55),
            canopy_r, col, rings=3, segments=8)

    # ── 3 picnic tables under shade trees ─────────────────────
    picnic_spots = [
        (sx - 24, sy + 18),     # NW shade
        (sx + 24, sy + 18),     # NE shade
        (sx - 24, sy - 18),     # SW shade
    ]
    for i, (px, py) in enumerate(picnic_spots):
        _make_box_local(f"OTPark_Picnic_{i}_Top",
                        (px, py, park_z + 0.75),
                        (2.0, 0.90, 0.06), COL_PICNIC)
        for sign in (-1, 1):
            _make_box_local(f"OTPark_Picnic_{i}_Bench_{sign:+d}",
                            (px, py + sign * 0.70, park_z + 0.42),
                            (2.0, 0.36, 0.05), COL_PICNIC)
            # Bench legs (suggested)
            for tx in (-0.85, 0.85):
                _make_box_local(f"OTPark_Picnic_{i}_BLeg_{sign:+d}_{tx:+.1f}",
                                (px + tx, py + sign * 0.70,
                                 park_z + 0.21),
                                (0.06, 0.06, 0.42), COL_PICNIC)

    # ── 5 benches: 4 around the ring + 1 on the terrace ──────
    bench_angles = [45, 135, 225, 315]    # diagonals so they face statue
    for i, ang_deg in enumerate(bench_angles):
        ang = math.radians(ang_deg)
        bx = sx + math.cos(ang) * 13.2
        by = sy + math.sin(ang) * 13.2
        # Seat
        _make_box_local(f"OTPark_Bench_{i}_Seat",
                        (bx, by, park_z + 0.43),
                        (1.6, 0.42, 0.06), COL_BENCH)
        # Back — perpendicular to the radial direction so it faces
        # inward toward the statue.
        back_off_x = math.cos(ang) * 0.18
        back_off_y = math.sin(ang) * 0.18
        if abs(math.cos(ang)) > abs(math.sin(ang)):
            back_sz = (0.06, 1.5, 0.45)
        else:
            back_sz = (1.5, 0.06, 0.45)
        _make_box_local(f"OTPark_Bench_{i}_Back",
                        (bx + back_off_x, by + back_off_y,
                         park_z + 0.85),
                        back_sz, COL_BENCH)
    # Terrace bench at the top step
    _make_box_local("OTPark_TerraceBench_Seat",
                    (sx, sy + outer_r + 30 + 6, park_z + 1.50 + 0.43),
                    (2.4, 0.42, 0.06), COL_BENCH)
    _make_box_local("OTPark_TerraceBench_Back",
                    (sx, sy + outer_r + 30 + 6.20,
                     park_z + 1.50 + 0.85),
                    (2.4, 0.06, 0.45), COL_BENCH)

    # ── Pink flower planters at NSEW of the inner ring ──────
    for tag, fx_off, fy_off in (('N', 0, 11), ('S', 0, -11),
                                  ('E', 11, 0), ('W', -11, 0)):
        # Wooden bed
        _make_box_local(f"OTPark_FlowerBed_{tag}",
                        (sx + fx_off, sy + fy_off, park_z + 0.20),
                        (2.0, 1.0, 0.30), COL_FLOWER_BED)
        # Pink flowers on top — Oliver Tree's signature jacket pink
        _make_box_local(f"OTPark_Flowers_{tag}",
                        (sx + fx_off, sy + fy_off, park_z + 0.50),
                        (1.9, 0.9, 0.18), COL_FLOWER_PINK)

    # ── Park sign at the SOUTH entry ─────────────────────────
    sign_x = sx
    sign_y = sy - outer_r - 48     # near the end of the south path
    # Two posts
    for sign_post_x in (-1.4, 1.4):
        _make_cyl_local(f"OTPark_SignPost_{sign_post_x:+.1f}",
                        (sign_x + sign_post_x, sign_y,
                         park_z + 1.4),
                        0.08, 2.8, COL_SIGN_BROWN, segments=4)
    # Brown panel
    _make_box_local("OTPark_SignPanel",
                    (sign_x, sign_y, park_z + 2.2),
                    (3.4, 0.15, 1.20), COL_SIGN_BROWN)
    # Cream lettering area inset (Label3D will overlay text later)
    _make_box_local("OTPark_SignLetters",
                    (sign_x, sign_y - 0.08, park_z + 2.2),
                    (3.0, 0.06, 0.90), COL_SIGN_FACE)

    # ── Beacon relocated to the park south entry ────────────
    beacon_x = sx
    beacon_y = sy - outer_r - 50
    BEACON_H = 35.0
    _make_cyl_local("OT_Beacon_Pole",
                    (beacon_x, beacon_y, park_z + BEACON_H / 2),
                    0.20, BEACON_H, (0.10, 0.10, 0.10, 1.0),
                    segments=4)
    _make_box_local("OT_Beacon_Top",
                    (beacon_x, beacon_y, park_z + BEACON_H + 1.2),
                    (2.2, 2.2, 2.2), COL_FLOWER_PINK)


def _make_sphere_low_local(name, center, radius, color,
                           rings=3, segments=8):
    cx, cy, cz = center
    verts = [(cx, cy, cz + radius)]
    for r in range(1, rings):
        phi = math.pi * r / rings
        rr = radius * math.sin(phi)
        zh = radius * math.cos(phi)
        for s in range(segments):
            ang = 2.0 * math.pi * s / segments
            verts.append((cx + rr * math.cos(ang),
                          cy + rr * math.sin(ang),
                          cz + zh))
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


def _make_box_local(name, center, size, color):
    """Local box helper — same signature as the module-level make
    helpers but distinct name so we don't import-shadow."""
    cx, cy, cz = center
    sx, sy, sz = size
    hx, hy, hz = sx/2, sy/2, sz/2
    verts = [
        (cx-hx, cy-hy, cz-hz), (cx+hx, cy-hy, cz-hz),
        (cx+hx, cy+hy, cz-hz), (cx-hx, cy+hy, cz-hz),
        (cx-hx, cy-hy, cz+hz), (cx+hx, cy-hy, cz+hz),
        (cx+hx, cy+hy, cz+hz), (cx-hx, cy+hy, cz+hz),
    ]
    faces = [
        [4, 5, 6, 7], [0, 3, 2, 1],
        [0, 1, 5, 4], [2, 3, 7, 6],
        [3, 0, 4, 7], [1, 2, 6, 5],
    ]
    return _finalize_mesh(name, verts, faces, color)


def _make_cyl_local(name, center, radius, height, color, segments=6):
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


def main():
    clear_scene()
    build_ground()
    build_creek()
    build_pond_water()
    build_district_fences()
    build_feature_beacons()
    build_oliver_tree_memorial()
    build_oliver_tree_memorial_park()
    export_glb()


if __name__ == "__main__":
    main()
