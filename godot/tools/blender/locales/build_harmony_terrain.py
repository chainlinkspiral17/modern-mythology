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
    # Secluded skatepark — sunken 2.5 m below the memorial park
    # platform so it reads as tucked away. Higher flatness so it
    # wins the overlap blend with the parent OT Park zone.
    ("OTSkatePark",       -300, -260, 65, 100, -0.5, 0.90),
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
    # ── OT MEMORIAL PARK · interior terrain features ──
    # Per user direction (2026-06-14): "Texas suburb parks are
    # almost never flat and boring. There are terraced embankments
    # and hills." These narrow ridges sit at the park's edges so
    # they add visual variation WITHOUT intruding on the central
    # walkway ring (which would break alignment of paths, benches,
    # the reflecting pool, etc).
    # West-edge embankment ridge — width 5 → bump dies off ~15 m
    # away from the centerline; walkway ring at x=-275 is clear.
    ("OTPark_WestEmb",     [(-298, 75),  (-298, 165)],   5.0, 1.6),
    ("OTPark_EastEmb",     [(-222, 75),  (-222, 165)],   5.0, 1.6),
    # North-edge embankment ridge (behind the terrace overlook)
    ("OTPark_NorthEmb",    [(-296, 175), (-224, 175)],   4.0, 1.2),
    # Viewing knoll in the NE corner — taller bump with a wider
    # falloff so it reads as a small hill
    ("OTPark_NEKnoll",     [(-232, 168), (-220, 168)],  10.0, 2.2),
    # Viewing knoll in the SW corner — secluded reading spot
    ("OTPark_SWKnoll",     [(-294, 76),  (-282, 76)],   10.0, 1.8),
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
        # Water sits ~0.7 m below the SURROUNDING RIM elevation per
        # the golden rule ("ponds are seldom overflowing"). Sample
        # the terrain at the outer edge of the depression and place
        # water just below that.
        rim_samples = []
        for sample_i in range(8):
            ang = 2.0 * math.pi * sample_i / 8
            sx_pt = cx + math.cos(ang) * radius * 1.05
            sy_pt = cy + math.sin(ang) * radius * 1.05
            rim_samples.append(hce_elevation(sx_pt, sy_pt))
        rim_z = sum(rim_samples) / len(rim_samples)
        water_z = min(bottom_z + 1.5, rim_z - 0.7)
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
        # Sandy beach ring · ALIGNED TO TERRAIN per the golden rule.
        # Inner edge sits just above water; outer edge samples the
        # actual ground elevation at each vertex so the beach slopes
        # naturally up the surrounding hill. No more floating ring.
        outer = radius * 0.95
        inner_z = water_z + 0.10   # 10 cm above water at inner edge
        bverts = []
        for ring in (0, 1):
            r_base = wr if ring == 0 else outer
            for i in range(segments):
                ang = 2.0 * math.pi * i / segments
                # Outer ring wobble for natural edge
                if ring == 1:
                    seed_h = hash((name, i)) & 0xFFFF
                    wobble = (seed_h % 100 - 50) / 50.0   # -1..+1
                    r = r_base + wobble * radius * 0.10
                else:
                    r = r_base
                vx = cx + math.cos(ang) * r
                vy = cy + math.sin(ang) * r
                if ring == 0:
                    # Inner ring sits at the water-edge bank height
                    vz = inner_z
                else:
                    # Outer ring follows the actual terrain elevation
                    # at that vertex's world position. The bank rises
                    # with the slope of the depression.
                    vz = max(hce_elevation(vx, vy), inner_z + 0.05)
                bverts.append((vx, vy, vz))
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

        # ── Reed / cattail clumps at the bank ── golden rule:
        # each clump samples ITS OWN ground elevation, capped at
        # water + 0.05 m so reeds can't sink below the surface.
        n_clumps = max(4, int(radius / 6))
        for k in range(n_clumps):
            ang = 6.2831 * k / n_clumps + 0.13
            rx = cx + math.cos(ang) * outer * 1.04
            ry = cy + math.sin(ang) * outer * 1.04
            rz = max(hce_elevation(rx, ry), water_z + 0.05)
            _reed_clump(f"PondReeds_{name}_{k}", rx, ry,
                        ground_z=rz, count=5)

        # ── Ducks ── two per pond, drifting in deterministic spots
        for d_idx, (dr, da, dfacing) in enumerate([
            (wr * 0.45, 0.7, '+X'),
            (wr * 0.55, 3.6, '-Y'),
        ]):
            dx = cx + math.cos(da) * dr
            dy = cy + math.sin(da) * dr
            _build_duck(f"PondDuck_{name}_{d_idx}",
                        dx, dy, water_z, facing=dfacing)

        # ── Wooden dock ── FoundersPond (the biggest) gets a small
        # public dock extending in from the south bank.
        if name == "FoundersPond":
            dock_w = 2.0
            dock_l = 8.0
            dock_z = water_z + 0.40
            _make_box_local(f"PondDock_{name}_Deck",
                            (cx, cy - outer + dock_l / 2 - 1.0,
                             dock_z),
                            (dock_w, dock_l, 0.12),
                            (0.55, 0.40, 0.26, 1.0))
            # Two posts at the water end
            for dx_off in (-dock_w / 2 + 0.10, dock_w / 2 - 0.10):
                _make_box_local(f"PondDock_{name}_Post_{dx_off:+.1f}",
                                (cx + dx_off,
                                 cy - outer + dock_l - 1.5,
                                 dock_z - 0.30),
                                (0.18, 0.18, 1.0),
                                (0.42, 0.30, 0.20, 1.0))

        # ── Small green bushes ringing the outer beach ─ each
        # bush samples ITS OWN ground (golden rule).
        n_bushes = max(3, int(radius / 12))
        for k in range(n_bushes):
            ang = 6.2831 * k / n_bushes + 0.55
            bx = cx + math.cos(ang) * outer * 1.12
            by = cy + math.sin(ang) * outer * 1.12
            bz = hce_elevation(bx, by)
            _make_sphere_low_local(f"PondBush_{name}_{k}",
                                   (bx, by, bz + 0.45),
                                   0.6 + 0.15 * (k % 2),
                                   (0.32, 0.55, 0.28, 1.0),
                                   rings=3, segments=6)


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

    # ── Plinth · three tiers (base + tapered shaft + cap) ──────
    COL_PLINTH_BASE = (0.68, 0.64, 0.56, 1.0)    # darker base stone
    COL_PLINTH_SHAFT = (0.78, 0.74, 0.66, 1.0)   # cream main
    COL_PLINTH_CAP = (0.85, 0.80, 0.70, 1.0)     # lighter cap
    COL_PLAQUE = (0.65, 0.48, 0.20, 1.0)
    # Wider stepped base
    base_w, base_d, base_h = 3.4, 3.0, 0.5
    base_z = ground_z + base_h / 2
    _make_box_local("OT_Plinth_Base",
                    (sx, sy, base_z),
                    (base_w, base_d, base_h),
                    COL_PLINTH_BASE)
    # Tapered shaft — middle tier
    shaft_w, shaft_d, shaft_h = 2.6, 2.2, 1.2
    shaft_z = ground_z + base_h + shaft_h / 2
    _make_box_local("OT_Plinth",
                    (sx, sy, shaft_z),
                    (shaft_w, shaft_d, shaft_h),
                    COL_PLINTH_SHAFT)
    # Cap overhang — light stone moulding
    cap_w, cap_d, cap_h = 2.9, 2.5, 0.20
    cap_z = ground_z + base_h + shaft_h + cap_h / 2
    _make_box_local("OT_Plinth_Cap",
                    (sx, sy, cap_z),
                    (cap_w, cap_d, cap_h),
                    COL_PLINTH_CAP)
    # Brass plaque on the shaft front (south face)
    _make_box_local("OT_Plaque",
                    (sx, sy - shaft_d / 2 - 0.04, shaft_z),
                    (1.8, 0.08, 0.80),
                    COL_PLAQUE)
    # Plinth corner detail — small column stubs at each base corner
    for (cx_off, cy_off) in [(-base_w / 2 + 0.25, -base_d / 2 + 0.25),
                              (base_w / 2 - 0.25, -base_d / 2 + 0.25),
                              (base_w / 2 - 0.25, base_d / 2 - 0.25),
                              (-base_w / 2 + 0.25, base_d / 2 - 0.25)]:
        _make_cyl_local(f"OT_Plinth_Corner_{cx_off:+.1f}_{cy_off:+.1f}",
                        (sx + cx_off, sy + cy_off,
                         ground_z + base_h + 0.10),
                        0.10, 0.20, COL_PLINTH_CAP, segments=6)
    plinth_h = base_h + shaft_h + cap_h    # total stack height

    # ── The figure itself, via the human_sculpt pipeline ────────
    base_z = ground_z + plinth_h   # feet sit on top of the plinth
    figure_meta = human_figure(
        name="OT",
        base_x=sx, base_y=sy, base_z=base_z,
        scale=2.5,                    # 4.5 m statue
        facing='-Y',                  # plaque/face point south
        skin_color=(0.92, 0.75, 0.62, 1.0),
        hair_style='bowl',
        hair_color=(0.32, 0.22, 0.16, 1.0),
        jacket_color=(0.95, 0.42, 0.62, 1.0),     # hot pink
        yoke_color=(0.62, 0.42, 0.78, 1.0),       # purple shoulder yoke
        accent='star',
        accent_color=(0.95, 0.42, 0.62, 1.0),
        scarf_color=(0.95, 0.85, 0.35, 1.0),      # yellow scarf
        pants_color=(0.55, 0.68, 0.82, 1.0),      # denim blue
        pants_flare=3.4,                          # JNCO drama
        shoe_color=(0.92, 0.90, 0.84, 1.0),       # white shoes
        has_sunglasses=True,
        sunglasses_color=(0.95, 0.30, 0.45, 1.0), # pink-red lenses
        with_ears=True,
        with_mouth=True,
        mouth_color=(0.55, 0.22, 0.28, 1.0),
        jacket_puffy=True,                        # PUFFER silhouette
        pose='right_mic',                         # right arm raised
        lean_x=0.25,                              # contrapposto hip shift
    )

    # ── PROP: microphone attached to the RIGHT HAND ───────────
    # human_figure returns the actual hand-tip world position for
    # whichever pose it built, so the mic anchors to the wrist.
    hx, hy, hz = figure_meta["hands"]["R"]
    # Handle from hand → mouth height
    _build_oriented_handle(
        "OT_MicHandle", (hx, hy, hz), (hx + 0.0, hy - 0.18, hz + 0.55),
        radius=0.05, color=(0.12, 0.12, 0.12, 1.0))
    # Foam-ball head at the top of the handle
    _make_sphere_low_local("OT_MicHead",
                           (hx + 0.0, hy - 0.20, hz + 0.65),
                           0.13, (0.18, 0.18, 0.18, 1.0),
                           rings=3, segments=8)

    # ── PROP: green Razor scooter at ground level beside plinth ─
    # Per the alignment golden rule: sample terrain AT THE PROP'S
    # OWN position, not at the statue center. The new park berms
    # mean the ground varies across the plaza.
    sc_x, sc_y = sx + 2.6, sy - 0.4
    sc_ground = hce_elevation(sc_x, sc_y)
    _build_scooter("OT_Scooter", sc_x, sc_y, sc_ground,
                   color_deck=(0.30, 0.55, 0.25, 1.0),
                   color_metal=(0.78, 0.78, 0.80, 1.0))

    # ── MEMORIAL TRIBUTES at the south face of the plinth ─────
    # Each tribute samples its own ground elevation per the golden
    # rule, so no piece floats above or buries into the terrain.
    tribute_y = sy - shaft_d / 2 - 0.5
    tribute_specs = [
        (sx - 0.9, tribute_y + 0.05, (0.95, 0.42, 0.62, 1.0)),  # pink
        (sx - 0.4, tribute_y + 0.0,  (0.95, 0.88, 0.30, 1.0)),  # yellow
        (sx + 0.0, tribute_y - 0.05, (0.92, 0.90, 0.84, 1.0)),  # white
        (sx + 0.5, tribute_y + 0.05, (0.85, 0.20, 0.20, 1.0)),  # red
        (sx + 1.0, tribute_y + 0.0,  (0.68, 0.42, 0.85, 1.0)),  # purple
    ]
    for i, (tx, ty, tcol) in enumerate(tribute_specs):
        tz = hce_elevation(tx, ty)
        _make_box_local(f"OT_Tribute_Stem_{i}",
                        (tx, ty, tz + 0.10),
                        (0.18, 0.18, 0.20),
                        (0.72, 0.62, 0.45, 1.0))
        _make_sphere_low_local(f"OT_Tribute_Bouquet_{i}",
                               (tx, ty, tz + 0.32),
                               0.18, tcol, rings=3, segments=6)
    # Two lit-candle tributes
    for cdx in (-1.4, 1.4):
        cd_x, cd_y = sx + cdx, tribute_y
        cd_z = hce_elevation(cd_x, cd_y)
        _make_cyl_local(f"OT_Tribute_Candle_{cdx:+.1f}",
                        (cd_x, cd_y, cd_z + 0.12),
                        0.06, 0.22, (0.92, 0.90, 0.84, 1.0),
                        segments=6)
        _make_sphere_low_local(f"OT_Tribute_Flame_{cdx:+.1f}",
                               (cd_x, cd_y, cd_z + 0.30),
                               0.06, (0.98, 0.78, 0.20, 1.0),
                               rings=3, segments=6)
    # Photo in a frame
    ph_x, ph_y = sx - 1.5, tribute_y - 0.10
    ph_z = hce_elevation(ph_x, ph_y)
    _make_box_local("OT_Tribute_Photo",
                    (ph_x, ph_y, ph_z + 0.30),
                    (0.30, 0.04, 0.40),
                    (0.95, 0.92, 0.84, 1.0))
    # Scooter wheel
    wh_x, wh_y = sx + 1.6, tribute_y - 0.20
    wh_z = hce_elevation(wh_x, wh_y)
    _make_cyl_local("OT_Tribute_Wheel",
                    (wh_x, wh_y, wh_z + 0.08),
                    0.10, 0.06, (0.12, 0.12, 0.12, 1.0), segments=8)


def _build_oriented_handle(name, p0, p1, radius, color, segments=6):
    """Tapered-cylinder helper used by props that need to point at
    arbitrary angles (mic handle from hand → mouth, etc.). Wraps
    the human_sculpt._oriented_cyl logic so the build script
    doesn't need to import it."""
    px = p1[0] - p0[0]; py = p1[1] - p0[1]; pz = p1[2] - p0[2]
    length = math.sqrt(px * px + py * py + pz * pz)
    if length < 0.001:
        return
    dx, dy, dz = px / length, py / length, pz / length
    if abs(dz) < 0.9:
        ux, uy, uz = 0.0, 0.0, 1.0
    else:
        ux, uy, uz = 1.0, 0.0, 0.0
    p1x = dy * uz - dz * uy
    p1y = dz * ux - dx * uz
    p1z = dx * uy - dy * ux
    l1 = math.sqrt(p1x * p1x + p1y * p1y + p1z * p1z)
    p1x, p1y, p1z = p1x / l1, p1y / l1, p1z / l1
    p2x = dy * p1z - dz * p1y
    p2y = dz * p1x - dx * p1z
    p2z = dx * p1y - dy * p1x
    verts = []
    for ring in (0, 1):
        c = p0 if ring == 0 else p1
        for i in range(segments):
            ang = 2.0 * math.pi * i / segments
            ca, sa = math.cos(ang), math.sin(ang)
            verts.append((
                c[0] + ca * radius * p1x + sa * radius * p2x,
                c[1] + ca * radius * p1y + sa * radius * p2y,
                c[2] + ca * radius * p1z + sa * radius * p2z,
            ))
    faces = []
    for i in range(segments):
        ni = (i + 1) % segments
        faces.append([i, ni, ni + segments, i + segments])
    faces.append(list(reversed(range(segments))))
    faces.append(list(range(segments, segments * 2)))
    _finalize_mesh(name, verts, faces, color)

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

    # ── FOUNTAIN JET in the reflecting pool · vertical water column
    # plus a small spray ring. Reads as a real water feature, not
    # just a still puddle.
    fountain_cx = pool_cx
    fountain_cy = pool_cy
    # Stone plinth in the pool centre
    _make_cyl_local("OTPark_FountainBase",
                    (fountain_cx, fountain_cy, park_z - 0.15),
                    0.45, 0.5, COL_POOL_RIM, segments=8)
    # Vertical water column (a thin tall cylinder representing the jet)
    _make_cyl_local("OTPark_FountainJet",
                    (fountain_cx, fountain_cy, park_z + 1.20),
                    0.10, 2.4, (0.55, 0.78, 0.85, 1.0), segments=6)
    # Spray crown — small sphere at the top representing breaking water
    _make_sphere_low_local("OTPark_FountainCrown",
                            (fountain_cx, fountain_cy, park_z + 2.50),
                            0.50, (0.78, 0.92, 0.95, 1.0),
                            rings=3, segments=8)
    # Lower spray ring — 6 small spheres around the base
    for k in range(6):
        ang_k = 2.0 * math.pi * k / 6
        sx_off = math.cos(ang_k) * 0.5
        sy_off = math.sin(ang_k) * 0.5
        _make_sphere_low_local(f"OTPark_FountainSpray_{k}",
                                (fountain_cx + sx_off,
                                 fountain_cy + sy_off,
                                 park_z + 0.35),
                                0.18, (0.62, 0.82, 0.88, 1.0),
                                rings=3, segments=6)

    # ── FLAG POLE at half-mast · the "one detail wrong" beat per
    # the modeling playbook. US flag in honour of the deceased.
    fp_x = sx + outer_r + 14
    fp_y = sy + 8
    FLAGPOLE_H = 8.0
    _make_cyl_local("OTPark_FlagPole",
                    (fp_x, fp_y, park_z + FLAGPOLE_H / 2),
                    0.10, FLAGPOLE_H, (0.82, 0.80, 0.76, 1.0),
                    segments=8)
    # Concrete base
    _make_box_local("OTPark_FlagPole_Base",
                    (fp_x, fp_y, park_z + 0.15),
                    (0.80, 0.80, 0.30), COL_POOL_RIM)
    # Flag at HALF mast — alternating red/white stripes + canton
    flag_z = park_z + FLAGPOLE_H * 0.50
    flag_w = 1.6
    flag_h = 0.95
    n_stripes = 7
    stripe_h = flag_h / n_stripes
    for s_idx in range(n_stripes):
        col = (0.78, 0.18, 0.18, 1.0) if s_idx % 2 == 0 else (0.92, 0.90, 0.84, 1.0)
        sz_pos = flag_z - flag_h / 2 + stripe_h * (s_idx + 0.5)
        _make_box_local(f"OTPark_Flag_Stripe_{s_idx}",
                        (fp_x + flag_w / 2 + 0.10, fp_y, sz_pos),
                        (flag_w, 0.02, stripe_h * 0.95), col)
    # Canton (upper-left, blue)
    canton_w = flag_w * 0.40
    canton_h = stripe_h * 4
    canton_z = flag_z + flag_h / 2 - canton_h / 2
    _make_box_local("OTPark_Flag_Canton",
                    (fp_x + 0.10 + canton_w / 2, fp_y, canton_z),
                    (canton_w, 0.025, canton_h),
                    (0.18, 0.22, 0.45, 1.0))
    # Gold finial
    _make_sphere_low_local("OTPark_FlagPole_Finial",
                            (fp_x, fp_y, park_z + FLAGPOLE_H + 0.10),
                            0.10, (0.78, 0.62, 0.28, 1.0),
                            rings=3, segments=6)

    # ── 8 mature OAKS — natural height variation per pass-5 ───
    # Each oak picks a height + canopy + tilt offset deterministically
    # from its position hash so successive rebuilds stay identical.
    oak_positions = [
        (sx - 28, sy - 10), (sx - 28, sy + 12),
        (sx + 28, sy - 10), (sx + 28, sy + 12),
        (sx - 18, sy + 26), (sx + 18, sy + 26),
        (sx - 18, sy - 26), (sx + 18, sy - 26),
    ]
    for i, (ox, oy) in enumerate(oak_positions):
        # Deterministic variation
        seed = (i * 17 + int(ox) * 7 + int(oy) * 13) % 100
        trunk_h = 4.5 + (seed % 5) * 0.7        # 4.5 → 7.3 m
        canopy_r = 4.0 + ((seed // 7) % 4) * 0.6   # 4.0 → 5.8 m
        # Lean offset — slight tilt of the canopy on top of the trunk
        lean_x = (((seed * 31) % 7) - 3) * 0.12      # ±0.36 m
        lean_y = (((seed * 53) % 7) - 3) * 0.12
        # Trunk colour variation
        trunk_col = COL_OAK_TRUNK if (seed % 3) else (0.36, 0.26, 0.18, 1.0)
        _make_cyl_local(f"OTPark_Oak_{i}_Trunk",
                        (ox, oy, park_z + trunk_h / 2),
                        0.40 + (seed % 3) * 0.10, trunk_h,
                        trunk_col, segments=6)
        col = COL_OAK_CANOPY if i % 2 == 0 else COL_OAK_CANOPY2
        # Inner darker canopy core (suggests volume)
        _make_sphere_low_local(
            f"OTPark_Oak_{i}_CanopyCore",
            (ox + lean_x, oy + lean_y,
             park_z + trunk_h + canopy_r * 0.45),
            canopy_r * 0.7, COL_OAK_TRUNK, rings=3, segments=6)
        _make_sphere_low_local(
            f"OTPark_Oak_{i}_Canopy",
            (ox + lean_x, oy + lean_y,
             park_z + trunk_h + canopy_r * 0.55),
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
    # Gazebo on the top terrace step replaces the bare bench — the
    # contemplation pavilion. Hexagonal wooden posts + peaked roof.
    _build_gazebo("OTPark_Gazebo",
                  sx, sy + outer_r + 30 + 6,
                  park_z + 1.50,
                  radius=3.6, height=3.2)

    # ── Pink flower planters at the FOUR DIAGONAL positions of
    # the inner ring — NE / NW / SE / SW, so they don't overlap
    # with the radial paths AND don't clash with the south
    # reflecting pool axis. Each planter is angled inward.
    for tag, ang_deg in (('NE', 45), ('NW', 135),
                          ('SW', 225), ('SE', 315)):
        ang = math.radians(ang_deg)
        fx = sx + math.cos(ang) * 10.0
        fy = sy + math.sin(ang) * 10.0
        # Approximate box rotation by orienting the bed via its
        # larger axis along the tangent
        if abs(math.cos(ang)) > abs(math.sin(ang)):
            sx_bed, sy_bed = 1.0, 2.0
        else:
            sx_bed, sy_bed = 2.0, 1.0
        _make_box_local(f"OTPark_FlowerBed_{tag}",
                        (fx, fy, park_z + 0.20),
                        (sx_bed, sy_bed, 0.30), COL_FLOWER_BED)
        _make_box_local(f"OTPark_Flowers_{tag}",
                        (fx, fy, park_z + 0.50),
                        (sx_bed - 0.10, sy_bed - 0.10, 0.18),
                        COL_FLOWER_PINK)

    # ── PARK ENTRY ARCHWAY · stone arch over the south entry ─
    arch_y = sy - outer_r - 30      # ~30 m south of the ring
    arch_w = 7.0     # gap width
    arch_post_w = 1.0
    arch_post_h = 4.5
    arch_post_d = 1.2
    # Two stone posts flanking the path
    for sign in (-1, 1):
        _make_box_local(f"OTPark_ArchPost_{sign:+d}",
                        (sx + sign * (arch_w / 2 + arch_post_w / 2),
                         arch_y, park_z + arch_post_h / 2),
                        (arch_post_w, arch_post_d, arch_post_h),
                        COL_PLINTH_BASE)
        # Cap stone on top of each post
        _make_box_local(f"OTPark_ArchPostCap_{sign:+d}",
                        (sx + sign * (arch_w / 2 + arch_post_w / 2),
                         arch_y, park_z + arch_post_h + 0.15),
                        (arch_post_w + 0.30, arch_post_d + 0.30, 0.25),
                        COL_PLINTH_CAP)
    # Horizontal arch beam — heavy stone lintel
    _make_box_local("OTPark_ArchBeam",
                    (sx, arch_y, park_z + arch_post_h + 0.65),
                    (arch_w + 2 * arch_post_w + 0.6, arch_post_d + 0.3, 0.55),
                    COL_PLINTH_SHAFT)
    # Decorative inscribed panel on the beam (will get Label3D
    # via LocaleSetup recognising "OTPark_ArchInscription")
    _make_box_local("OTPark_ArchInscription",
                    (sx, arch_y - arch_post_d / 2 - 0.04,
                     park_z + arch_post_h + 0.65),
                    (arch_w + 1.5, 0.06, 0.40),
                    (0.45, 0.40, 0.32, 1.0))

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

    # ── 6 LAMPPOSTS along the radial paths ──────────────────
    # Two per main path (mid + far end of the longer paths) so the
    # walkways read as cared-for at night.
    for tag, dx, dy, length in radials:
        # one at the ring exit, one half-way along, one at the end
        for t in (0.45, 0.95):
            lx = sx + dx * (outer_r + length * t)
            ly = sy + dy * (outer_r + length * t)
            _build_lamppost(f"OTPark_Lamp_{tag}_{int(t*100)}",
                            lx, ly, park_z)

    # ── 2 TRASHCANS at the south entry, 1 DRINKING FOUNTAIN ─
    _build_trashcan("OTPark_Trash_W",
                    sx - 2.5, sy - outer_r - 40, park_z)
    _build_trashcan("OTPark_Trash_E",
                    sx + 2.5, sy - outer_r - 40, park_z)
    _build_drinking_fountain("OTPark_Fountain",
                              sx - 20, sy - 5, park_z)

    # ── Path-edging stones along the ring (decorative) ──────
    # 16 stones around the outer ring. Each gets a slight size +
    # colour wobble so the line of stones reads as cut-and-placed
    # natural pieces, not extruded duplicates.
    edge_count = 16
    stone_palette = [
        (0.82, 0.78, 0.66, 1.0),
        (0.74, 0.70, 0.60, 1.0),
        (0.86, 0.80, 0.66, 1.0),
        (0.68, 0.62, 0.52, 1.0),
        (0.78, 0.72, 0.62, 1.0),
    ]
    for i in range(edge_count):
        ang = 2.0 * math.pi * i / edge_count
        ex = sx + math.cos(ang) * (outer_r + 0.4)
        ey = sy + math.sin(ang) * (outer_r + 0.4)
        # Deterministic variation
        seed = (i * 23) % 100
        sw = 0.40 + (seed % 4) * 0.06    # 0.40 – 0.58 m
        sh = 0.22 + (seed % 3) * 0.05    # 0.22 – 0.32 m
        col = stone_palette[seed % len(stone_palette)]
        _make_box_local(f"OTPark_EdgeStone_{i}",
                        (ex, ey, park_z + sh / 2 + 0.02),
                        (sw, sw, sh), col)

    # ── BOULDERS · natural-feature accents scattered in the lawn ─
    # Six low boulders in deterministic positions outside the
    # walkway ring. Reads as "the park has rocks the landscapers
    # left in place" instead of perfectly mowed lawn everywhere.
    boulder_positions = [
        (sx - 32,  sy + 2,  1.6, (0.55, 0.52, 0.48, 1.0)),
        (sx + 32,  sy + 3,  1.4, (0.50, 0.46, 0.42, 1.0)),
        (sx - 12,  sy + 40, 1.2, (0.58, 0.54, 0.50, 1.0)),
        (sx + 13,  sy + 38, 1.8, (0.52, 0.48, 0.44, 1.0)),
        (sx - 10,  sy - 38, 1.0, (0.55, 0.52, 0.48, 1.0)),
        (sx + 14,  sy - 36, 1.3, (0.50, 0.46, 0.42, 1.0)),
    ]
    for i, (bx, by, br, bcol) in enumerate(boulder_positions):
        _make_sphere_low_local(f"OTPark_Boulder_{i}",
                               (bx, by, park_z + br * 0.45),
                               br, bcol, rings=3, segments=6)

    # ── GRASS TUFTS · small darker-green clumps scattered ──────
    # Reads as longer ornamental grass — breaks the manicured lawn.
    tuft_count = 28
    for k in range(tuft_count):
        # Spiral placement around the park
        ang = 6.2831 * k * 0.413
        radial = 18 + (k * 1.7) % 18
        tx = sx + math.cos(ang) * radial
        ty = sy + math.sin(ang) * radial
        # Skip if too close to a walkway (within 2 m of ring)
        d_to_ring = abs(math.hypot(tx - sx, ty - sy) - (inner_r + outer_r) / 2)
        if d_to_ring < 2.5:
            continue
        # Small green tuft
        _make_box_local(f"OTPark_Tuft_{k}",
                        (tx, ty, park_z + 0.18),
                        (0.30, 0.30, 0.35),
                        (0.28, 0.46, 0.20, 1.0))

    # ── EXTRA FLOWER COLOURS in mid-distance plantings ─────────
    # White + yellow + purple beds spotted around the lawn — adds
    # the "actually maintained" feel to a memorial park.
    extra_flower_specs = [
        (sx - 36, sy + 8,  (0.95, 0.92, 0.84, 1.0)),  # white
        (sx + 36, sy + 8,  (0.95, 0.88, 0.30, 1.0)),  # yellow
        (sx - 36, sy - 8,  (0.68, 0.42, 0.85, 1.0)),  # purple
        (sx + 36, sy - 8,  (0.95, 0.45, 0.25, 1.0)),  # orange
    ]
    for fx, fy, fcol in extra_flower_specs:
        _make_box_local(f"OTPark_ExtraBed_{int(fx)}_{int(fy)}",
                        (fx, fy, park_z + 0.16),
                        (1.4, 0.7, 0.22), COL_FLOWER_BED)
        _make_box_local(f"OTPark_ExtraFlowers_{int(fx)}_{int(fy)}",
                        (fx, fy, park_z + 0.36),
                        (1.30, 0.65, 0.14), fcol)

    # ── NPCs · a few human figures populate the park so it reads
    # as a lived-in place. All use human_sculpt.human_figure at
    # real scale (1.0). Outfits are deliberately varied so the
    # park doesn't feel like a uniformed group.
    # Visitor walking along the south path (toward the statue)
    human_figure(
        name="OTPark_NPC_Walker",
        base_x=sx + 1.5, base_y=sy - outer_r - 14, base_z=park_z,
        scale=1.0, facing='+Y',
        hair_style='short', hair_color=(0.42, 0.28, 0.20, 1.0),
        jacket_color=(0.38, 0.55, 0.68, 1.0),         # blue windbreaker
        pants_color=(0.32, 0.32, 0.36, 1.0),
        shoe_color=(0.18, 0.18, 0.22, 1.0),
        with_ears=True, pose='arms_out',
    )
    # Sitting-near-bench visitor (just standing next to a bench
    # facing the statue — sitting pose isn't in the pipeline yet)
    human_figure(
        name="OTPark_NPC_Visitor1",
        base_x=sx - 11, base_y=sy + 9, base_z=park_z,
        scale=1.0, facing='+X',
        hair_style='bowl', hair_color=(0.62, 0.42, 0.18, 1.0),
        jacket_color=(0.78, 0.32, 0.42, 1.0),         # red coat
        pants_color=(0.30, 0.28, 0.32, 1.0),
        scarf_color=(0.86, 0.78, 0.55, 1.0),
        with_ears=True,
    )
    # Photographer / fan on the terrace overlook
    human_figure(
        name="OTPark_NPC_OnTerrace",
        base_x=sx - 2, base_y=sy + outer_r + 30 + 9,
        base_z=park_z + 1.50,
        scale=1.0, facing='-Y',
        hair_style='short', hair_color=(0.18, 0.18, 0.22, 1.0),
        jacket_color=(0.32, 0.42, 0.32, 1.0),         # green field jacket
        pants_color=(0.50, 0.45, 0.32, 1.0),          # khaki
        shoe_color=(0.42, 0.30, 0.22, 1.0),
        has_sunglasses=True,
        sunglasses_color=(0.12, 0.12, 0.12, 1.0),
        with_ears=True,
    )
    # Kid by the reflecting pool
    human_figure(
        name="OTPark_NPC_Kid",
        base_x=sx + 5, base_y=sy - 18, base_z=park_z,
        scale=0.65,                                    # child-sized
        facing='+X',
        hair_style='short', hair_color=(0.72, 0.55, 0.22, 1.0),
        jacket_color=(0.95, 0.68, 0.30, 1.0),         # yellow raincoat
        pants_color=(0.32, 0.42, 0.62, 1.0),
        shoe_color=(0.85, 0.20, 0.18, 1.0),            # red shoes
        with_ears=True,
    )

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


def _build_scooter(name, x, y, z, color_deck, color_metal):
    """Low-poly Razor-style scooter. Deck + stem + handlebars +
    two wheels. Stands upright on its kickstand at (x, y, z)."""
    # Deck (footboard)
    _make_box_local(f"{name}_Deck",
                    (x, y, z + 0.10),
                    (0.95, 0.20, 0.05), color_deck)
    # Stem (vertical post at front)
    stem_x = x - 0.45
    _make_cyl_local(f"{name}_Stem",
                    (stem_x, y, z + 0.55),
                    0.025, 1.0, color_metal, segments=6)
    # T-bar handlebars
    _make_box_local(f"{name}_Handlebar",
                    (stem_x, y, z + 1.05),
                    (0.05, 0.55, 0.04), color_metal)
    # Two grip caps
    for sgn in (-1, 1):
        _make_cyl_local(f"{name}_Grip_{sgn:+d}",
                        (stem_x, y + sgn * 0.25, z + 1.05),
                        0.04, 0.10, (0.12, 0.12, 0.12, 1.0),
                        segments=6)
    # Wheels
    for sgn, wx in ((1, x - 0.45), (-1, x + 0.45)):
        _make_cyl_local(f"{name}_Wheel_{sgn:+d}",
                        (wx, y, z + 0.04),
                        0.10, 0.06,
                        (0.10, 0.10, 0.10, 1.0), segments=8)


def _build_lamppost(name, x, y, z_ground, pole_h=3.5,
                    pole_color=(0.18, 0.18, 0.18, 1.0),
                    globe_color=(0.94, 0.92, 0.78, 1.0)):
    """Decorative park lamppost — black wrought-iron pole with a
    cream globe lantern at the top."""
    _make_cyl_local(f"{name}_Pole",
                    (x, y, z_ground + pole_h / 2),
                    0.06, pole_h, pole_color, segments=6)
    # Base flare
    _make_box_local(f"{name}_Base",
                    (x, y, z_ground + 0.15),
                    (0.25, 0.25, 0.30), pole_color)
    # Globe lantern
    _make_sphere_low_local(f"{name}_Globe",
                           (x, y, z_ground + pole_h + 0.20),
                           0.22, globe_color, rings=3, segments=8)


def _build_gazebo(name, cx, cy, z_floor, radius=4.0, height=3.5,
                  post_color=(0.42, 0.30, 0.20, 1.0),
                  roof_color=(0.62, 0.18, 0.16, 1.0),
                  floor_color=(0.55, 0.40, 0.26, 1.0)):
    """Hexagonal gazebo — 6 wooden posts holding up a peaked roof.
    Used on the terrace top of the memorial park."""
    n_posts = 6
    # Floor (hexagonal disc)
    verts = [(cx, cy, z_floor + 0.05)]
    for i in range(n_posts):
        ang = 2.0 * math.pi * i / n_posts
        verts.append((cx + math.cos(ang) * radius,
                      cy + math.sin(ang) * radius,
                      z_floor + 0.05))
    faces = []
    for i in range(n_posts):
        ni = (i + 1) % n_posts
        faces.append([0, 1 + i, 1 + ni])
    _finalize_mesh(f"{name}_Floor", verts, faces, floor_color)
    # Posts
    for i in range(n_posts):
        ang = 2.0 * math.pi * i / n_posts
        px = cx + math.cos(ang) * radius * 0.95
        py = cy + math.sin(ang) * radius * 0.95
        _make_box_local(f"{name}_Post_{i}",
                        (px, py, z_floor + height / 2),
                        (0.20, 0.20, height), post_color)
    # Roof — a low pyramid (hexagonal pyramid)
    apex = (cx, cy, z_floor + height + 1.6)
    rverts = [apex]
    for i in range(n_posts):
        ang = 2.0 * math.pi * i / n_posts
        rverts.append((cx + math.cos(ang) * (radius + 0.3),
                       cy + math.sin(ang) * (radius + 0.3),
                       z_floor + height))
    rfaces = []
    for i in range(n_posts):
        ni = (i + 1) % n_posts
        rfaces.append([0, 1 + i, 1 + ni])
    _finalize_mesh(f"{name}_Roof", rverts, rfaces, roof_color)


def _build_drinking_fountain(name, x, y, z_ground):
    """Small white pillar drinking fountain — the kind in every
    public park."""
    _make_box_local(f"{name}_Pillar",
                    (x, y, z_ground + 0.50),
                    (0.35, 0.30, 1.00), (0.88, 0.86, 0.82, 1.0))
    # Basin on top (slight overhang)
    _make_box_local(f"{name}_Basin",
                    (x, y, z_ground + 1.05),
                    (0.45, 0.40, 0.10), (0.88, 0.86, 0.82, 1.0))
    # Spout
    _make_box_local(f"{name}_Spout",
                    (x, y - 0.10, z_ground + 1.15),
                    (0.08, 0.10, 0.10), (0.55, 0.55, 0.58, 1.0))


def _build_trashcan(name, x, y, z_ground):
    _make_cyl_local(f"{name}_Body",
                    (x, y, z_ground + 0.55),
                    0.28, 1.05, (0.32, 0.30, 0.28, 1.0),
                    segments=8)
    _make_cyl_local(f"{name}_Lid",
                    (x, y, z_ground + 1.12),
                    0.30, 0.08, (0.25, 0.23, 0.22, 1.0),
                    segments=8)


def _build_duck(name, x, y, z_water, facing='+X'):
    """Small lowpoly duck — white body + orange beak + black eye dot.
    Sits on the water surface."""
    # Body (squashed sphere)
    _make_sphere_low_local(f"{name}_Body",
                           (x, y, z_water + 0.10),
                           0.18, (0.92, 0.90, 0.84, 1.0),
                           rings=3, segments=8)
    # Head (smaller sphere offset forward)
    if facing == '+X':
        hx, hy = x + 0.18, y
    elif facing == '-X':
        hx, hy = x - 0.18, y
    elif facing == '+Y':
        hx, hy = x, y + 0.18
    else:
        hx, hy = x, y - 0.18
    _make_sphere_low_local(f"{name}_Head",
                           (hx, hy, z_water + 0.25),
                           0.10, (0.92, 0.90, 0.84, 1.0),
                           rings=3, segments=6)
    # Beak
    if facing == '+X':
        bx, by = hx + 0.08, hy
    elif facing == '-X':
        bx, by = hx - 0.08, hy
    elif facing == '+Y':
        bx, by = hx, hy + 0.08
    else:
        bx, by = hx, hy - 0.08
    _make_box_local(f"{name}_Beak",
                    (bx, by, z_water + 0.22),
                    (0.06, 0.06, 0.05),
                    (0.92, 0.55, 0.20, 1.0))


def build_oliver_tree_skatepark():
    """The secluded skatepark inside the Oliver Tree Memorial Park.
    Per user direction (2026-06-14): "a secluded skatepark, more
    elaborate than you might think, a place to find oneself.
    Designed for gentle cruising, high speed navigation and cool
    tricks to attempt."

    Three modes baked in:
      CRUISING   · big flat plaza + gentle banked turn
      SPEED      · pump-track waves + snake-run channel
      TRICKS     · quarter-pipe + mini half-pipe + bowl + grind
                   rail + manual pad + hubba ledge + 3-stair set
    Plus: graffiti art walls, three spectator benches, a small
    concrete pyramid for sitting + memorial reflection, and a
    ring of older-growth trees on the perimeter for seclusion.

    Sits in the SW corner of the OT Park inside the OTSkatePark
    settlement zone which sinks the platform to z = -0.5 (vs the
    park's +2.0). Total drop of 2.5 m + the bowl carves another
    2.5 m below that, so the deepest point sits ~5 m below the
    statue's plinth-top reference."""
    cx, cy = -280.0, 82.0
    pz = hce_elevation(cx, cy)          # = ~-0.5 from settlement flat

    # Materials
    COL_SK_CONCRETE = (0.72, 0.70, 0.66, 1.0)
    COL_SK_PAINT    = (0.62, 0.58, 0.54, 1.0)     # painted lines
    COL_SK_DARK     = (0.40, 0.38, 0.36, 1.0)     # contrast concrete
    COL_SK_RAIL     = (0.62, 0.62, 0.65, 1.0)     # steel
    COL_GRAF_PINK   = (0.95, 0.42, 0.62, 1.0)     # OT pink callback
    COL_GRAF_BLUE   = (0.32, 0.55, 0.78, 1.0)
    COL_GRAF_YELLOW = (0.95, 0.85, 0.30, 1.0)
    COL_GRAF_PURPLE = (0.62, 0.42, 0.78, 1.0)
    COL_GRAF_GREEN  = (0.30, 0.55, 0.25, 1.0)

    # ── MAIN PLAZA · CRUISING MODE ─────────────────────────────
    # Big flat slab of skating concrete. The base of every line
    # connects here.
    plaza_w, plaza_d = 28.0, 24.0
    _make_box_local("Skp_Plaza",
                    (cx, cy, pz - 0.05),
                    (plaza_w, plaza_d, 0.10),
                    COL_SK_CONCRETE)
    # Painted lines on the plaza — suggests "bowl entry" + "drop in"
    for line_x in (-8.0, 0.0, 8.0):
        _make_box_local(f"Skp_PlazaLine_{int(line_x)}",
                        (cx + line_x, cy, pz + 0.005),
                        (0.10, plaza_d - 1, 0.01), COL_SK_PAINT)

    # ────────────────────────────────────────────────────────────
    # SOLID CONCRETE CONSTRUCTION · pool ↔ half-pipe ↔ half-sphere
    # All three features connected as a continuous flow line per
    # user spec. Concrete colour stays uniform across all of them.
    # Sunk into the terrain (settlement zone pulls platform to -0.5
    # already; pool deepens another 3 m, half-sphere another 2.5 m).
    # ────────────────────────────────────────────────────────────

    # ── FULL POOL · 10 × 7 m kidney with 3 m depth ─────────────
    # Carved as 3 stacked elliptical rings: top rim at pz, mid wall
    # at -1.6 m, bottom floor at -3.0 m. Wall taper gives a real
    # bowl/pool slope on the inside.
    pool_cx, pool_cy = cx - 8, cy - 4
    pool_a_top, pool_b_top = 6.0, 4.5         # outer rim ellipse
    pool_a_mid, pool_b_mid = 4.8, 3.4         # mid-wall ellipse
    pool_a_bot, pool_b_bot = 3.6, 2.4         # floor ellipse
    pool_top_z = pz - 0.05
    pool_mid_z = pz - 1.6
    pool_bot_z = pz - 3.0
    segs = 16
    # Outer rim ring (the deck around the pool — keeps level at pz)
    # is just the surrounding plaza, no separate mesh needed.
    # Slope band 1: top rim → mid wall
    v1 = []
    for ring_idx, (ra, rb, rz) in enumerate([
        (pool_a_top, pool_b_top, pool_top_z),
        (pool_a_mid, pool_b_mid, pool_mid_z),
    ]):
        for i in range(segs):
            ang = 2.0 * math.pi * i / segs
            v1.append((pool_cx + math.cos(ang) * ra,
                       pool_cy + math.sin(ang) * rb, rz))
    f1 = []
    for i in range(segs):
        ni = (i + 1) % segs
        f1.append([i, ni, ni + segs, i + segs])
    _finalize_mesh("Skp_Pool_Wall_Upper", v1, f1, COL_SK_CONCRETE)
    # Slope band 2: mid → floor
    v2 = []
    for ra, rb, rz in [(pool_a_mid, pool_b_mid, pool_mid_z),
                        (pool_a_bot, pool_b_bot, pool_bot_z)]:
        for i in range(segs):
            ang = 2.0 * math.pi * i / segs
            v2.append((pool_cx + math.cos(ang) * ra,
                       pool_cy + math.sin(ang) * rb, rz))
    f2 = []
    for i in range(segs):
        ni = (i + 1) % segs
        f2.append([i, ni, ni + segs, i + segs])
    _finalize_mesh("Skp_Pool_Wall_Lower", v2, f2, COL_SK_CONCRETE)
    # Pool floor disc (ellipse fan)
    vfp = [(pool_cx, pool_cy, pool_bot_z)]
    for i in range(segs):
        ang = 2.0 * math.pi * i / segs
        vfp.append((pool_cx + math.cos(ang) * pool_a_bot,
                    pool_cy + math.sin(ang) * pool_b_bot,
                    pool_bot_z))
    ffp = []
    for i in range(segs):
        ni = (i + 1) % segs
        ffp.append([0, 1 + i, 1 + ni])
    _finalize_mesh("Skp_Pool_Floor", vfp, ffp, COL_SK_CONCRETE)
    # Coping rail around the pool rim — steel
    vcope = []
    for ra, rb, rz in [(pool_a_top + 0.05, pool_b_top + 0.05, pool_top_z + 0.02),
                        (pool_a_top - 0.05, pool_b_top - 0.05, pool_top_z + 0.02),
                        (pool_a_top + 0.05, pool_b_top + 0.05, pool_top_z + 0.10),
                        (pool_a_top - 0.05, pool_b_top - 0.05, pool_top_z + 0.10)]:
        for i in range(segs):
            ang = 2.0 * math.pi * i / segs
            vcope.append((pool_cx + math.cos(ang) * ra,
                          pool_cy + math.sin(ang) * rb, rz))
    # (skipping full coping mesh — just place a few suggestion segments)
    for k in range(0, segs, 2):
        ang = 2.0 * math.pi * k / segs
        cope_x = pool_cx + math.cos(ang) * pool_a_top
        cope_y = pool_cy + math.sin(ang) * pool_b_top
        _make_box_local(f"Skp_Pool_Coping_{k}",
                        (cope_x, cope_y, pool_top_z + 0.05),
                        (0.30, 0.30, 0.06), COL_SK_RAIL)

    # ── CONNECTING HALF-PIPE · runs from pool → loop ───────────
    # Channel from the east edge of the pool to the west edge of
    # the half-sphere loop. The flat trough sits at the same depth
    # as the pool floor so a skater can flow continuously through.
    hp_floor_z = pool_bot_z + 0.20    # slight rise from pool to ramp
    hp_west_x = pool_cx + pool_a_top
    hp_east_x = hp_west_x + 7.5
    hp_cy_local = pool_cy
    hp_d = 4.0
    hp_h = 2.4
    # Trough floor (concrete)
    _make_box_local("Skp_HP_Trough",
                    ((hp_west_x + hp_east_x) / 2, hp_cy_local, hp_floor_z),
                    (hp_east_x - hp_west_x, hp_d, 0.20),
                    COL_SK_CONCRETE)
    # Two side ramps — left + right walls curve up to lip height
    # Approximate as wedge-prism boxes with a sloped face.
    for side, sign in (('S', -1), ('N', 1)):
        wall_inner_y = hp_cy_local + sign * (hp_d / 2)
        wall_outer_y = hp_cy_local + sign * (hp_d / 2 + 2.0)
        wall_verts = [
            (hp_west_x, wall_inner_y, hp_floor_z),
            (hp_east_x, wall_inner_y, hp_floor_z),
            (hp_east_x, wall_outer_y, hp_floor_z),
            (hp_west_x, wall_outer_y, hp_floor_z),
            (hp_east_x, wall_outer_y, hp_floor_z + hp_h),
            (hp_west_x, wall_outer_y, hp_floor_z + hp_h),
        ]
        wall_faces = [
            [0, 1, 2, 3],          # bottom
            [4, 1, 0, 5],          # outer back (vertical wall)
            [5, 0, 3],             # west cap (vertical triangle)
            [4, 2, 1],             # east cap (vertical triangle)
            [3, 2, 4, 5],          # inner — the sloped skating face
        ]
        _finalize_mesh(f"Skp_HP_Wall_{side}", wall_verts, wall_faces,
                       COL_SK_CONCRETE)
        # Coping along the top of each wall
        _make_box_local(f"Skp_HP_Coping_{side}",
                        ((hp_west_x + hp_east_x) / 2, wall_outer_y,
                         hp_floor_z + hp_h + 0.02),
                        (hp_east_x - hp_west_x, 0.10, 0.07),
                        COL_SK_RAIL)

    # ── HALF-SPHERE DEEP LOOP · the trick centrepiece ──────────
    # Hemispherical bowl carved into the platform, ~5 m diameter,
    # ~2.5 m deep. Skater drops in from the half-pipe, carves the
    # vertical wall, loops back out. Built from stacked rings of
    # decreasing radius forming the dome shape.
    loop_cx, loop_cy = hp_east_x + 2.5, hp_cy_local
    loop_top_r = 2.8
    loop_top_z = pz - 0.05
    loop_bot_z = loop_top_z - 2.6
    loop_rings = 5
    loop_segs = 16
    # Build dome verts: each ring at a different (r, z) following
    # a quarter-sphere profile (sin / cos parameterised)
    dome_verts = []
    for r_idx in range(loop_rings + 1):
        t = r_idx / loop_rings        # 0 → 1
        # Quarter-sphere: radius = top_r * cos(π/2 * t),
        # z descends from top_z to bot_z following sin(π/2 * t)
        ring_r = loop_top_r * math.cos(math.pi / 2 * t)
        ring_z = loop_top_z + (loop_bot_z - loop_top_z) * math.sin(math.pi / 2 * t)
        for s in range(loop_segs):
            ang = 2.0 * math.pi * s / loop_segs
            dome_verts.append((loop_cx + math.cos(ang) * ring_r,
                                loop_cy + math.sin(ang) * ring_r,
                                ring_z))
    dome_faces = []
    for r_idx in range(loop_rings):
        for s in range(loop_segs):
            ns = (s + 1) % loop_segs
            a = r_idx * loop_segs + s
            b = r_idx * loop_segs + ns
            c = (r_idx + 1) * loop_segs + ns
            d = (r_idx + 1) * loop_segs + s
            dome_faces.append([a, b, c, d])
    _finalize_mesh("Skp_HalfSphere_Loop", dome_verts, dome_faces,
                   COL_SK_CONCRETE)
    # Bottom cap (small disc at the deepest point)
    cap_verts = [(loop_cx, loop_cy, loop_bot_z)]
    cap_top_r = loop_top_r * math.cos(math.pi / 2 * 1.0)
    # cap_top_r is essentially 0; emit a tiny floor anyway
    for s in range(loop_segs):
        ang = 2.0 * math.pi * s / loop_segs
        cap_verts.append((loop_cx + math.cos(ang) * 0.1,
                          loop_cy + math.sin(ang) * 0.1,
                          loop_bot_z))
    cap_faces = []
    for s in range(loop_segs):
        ns = (s + 1) % loop_segs
        cap_faces.append([0, 1 + s, 1 + ns])
    _finalize_mesh("Skp_HalfSphere_Floor", cap_verts, cap_faces,
                   COL_SK_CONCRETE)
    # Coping ring around the loop top
    for k in range(0, loop_segs, 2):
        ang = 2.0 * math.pi * k / loop_segs
        cope_x = loop_cx + math.cos(ang) * loop_top_r
        cope_y = loop_cy + math.sin(ang) * loop_top_r
        _make_box_local(f"Skp_Loop_Coping_{k}",
                        (cope_x, cope_y, loop_top_z + 0.04),
                        (0.20, 0.20, 0.05), COL_SK_RAIL)

    # ── PUMP TRACK · SPEED MODE ────────────────────────────────
    # A winding undulating asphalt path along the south + east
    # edges. Built from a sequence of low domes (each a squashed
    # sphere) with flats between, so the rider can pump speed.
    pump_path = [
        (cx - 12, cy + 9), (cx - 7, cy + 11), (cx - 2, cy + 9),
        (cx + 3, cy + 11), (cx + 8, cy + 9), (cx + 12, cy + 7),
        (cx + 13, cy + 2), (cx + 11, cy - 3),
    ]
    for k, (px, py) in enumerate(pump_path):
        if k % 2 == 0:
            _make_sphere_low_local(f"Skp_Pump_Wave_{k}",
                                    (px, py, pz - 0.20),
                                    1.4, COL_SK_CONCRETE,
                                    rings=3, segments=8)
        else:
            _make_box_local(f"Skp_Pump_Flat_{k}",
                            (px, py, pz),
                            (2.4, 1.4, 0.10), COL_SK_CONCRETE)

    # ── GRIND RAIL · TRICKS MODE ───────────────────────────────
    rail_cx, rail_cy = cx, cy + 6
    rail_len = 5.0
    rail_h = 0.5
    # Two end posts
    for sign in (-1, 1):
        _make_box_local(f"Skp_RailPost_{sign:+d}",
                        (rail_cx + sign * rail_len / 2, rail_cy,
                         pz + rail_h / 2),
                        (0.10, 0.10, rail_h), COL_SK_RAIL)
    # Rail beam — a horizontal box (cylinder would be more accurate
    # but box keeps polycount low)
    _make_box_local("Skp_RailBeam",
                    (rail_cx, rail_cy, pz + rail_h),
                    (rail_len, 0.07, 0.07), COL_SK_RAIL)

    # ── MANUAL PAD · TRICKS MODE ───────────────────────────────
    _make_box_local("Skp_ManualPad",
                    (cx, cy - 5, pz + 0.20),
                    (4.0, 1.2, 0.40), COL_SK_CONCRETE)

    # ── HUBBA LEDGE · TRICKS MODE ──────────────────────────────
    # Stepped concrete ledge along a 3-stair set
    hubba_cx, hubba_cy = cx - 14, cy + 4
    for i, step_h in enumerate((0.20, 0.40, 0.60)):
        _make_box_local(f"Skp_Hubba_Step_{i}",
                        (hubba_cx + i * 0.8, hubba_cy, pz + step_h / 2),
                        (0.80, 2.0, step_h), COL_SK_CONCRETE)
    # The ledge itself — a long box on the side of the stairs
    _make_box_local("Skp_HubbaLedge",
                    (hubba_cx + 1.0, hubba_cy - 1.5, pz + 0.55),
                    (2.6, 0.30, 0.40), COL_SK_DARK)

    # ── BANKED TURN · SPEED + CRUISING ─────────────────────────
    # A curved low ramp at the NE edge connecting plaza to pump
    # track. Approximated by three stepped sloped boxes.
    for k in range(4):
        bank_x = cx + 12 + k * 0.8
        bank_h = 0.10 + k * 0.18
        _make_box_local(f"Skp_Bank_{k}",
                        (bank_x, cy + 4, pz + bank_h / 2),
                        (0.80, 6.0, bank_h), COL_SK_CONCRETE)

    # ── SMALL CONCRETE PYRAMID · sitting + "find oneself" beat ─
    # In the centre of the plaza. Skaters use the apex for tricks
    # but the user spec called for a place to FIND ONESELF, so
    # it's also the obvious meditation perch.
    pyr_cx, pyr_cy = cx + 0, cy + 0
    pyr_verts = [
        (pyr_cx - 1.6, pyr_cy - 1.6, pz),
        (pyr_cx + 1.6, pyr_cy - 1.6, pz),
        (pyr_cx + 1.6, pyr_cy + 1.6, pz),
        (pyr_cx - 1.6, pyr_cy + 1.6, pz),
        (pyr_cx, pyr_cy, pz + 1.1),
    ]
    pyr_faces = [
        [0, 1, 2, 3],
        [0, 4, 1],
        [1, 4, 2],
        [2, 4, 3],
        [3, 4, 0],
    ]
    _finalize_mesh("Skp_Pyramid", pyr_verts, pyr_faces, COL_SK_DARK)

    # ── GRAFFITI ART WALLS · 3 panels on the south edge ────────
    # Each wall: cream concrete back with coloured spray-paint
    # accent blocks suggesting tag art. Pink (OT colour), blue,
    # yellow, purple. Reads as a memorial / fan-art zone.
    wall_y = cy - 12
    wall_h = 2.4
    graf_palettes = [
        (cx - 8, [COL_GRAF_PINK, COL_GRAF_YELLOW, COL_GRAF_BLUE]),
        (cx,     [COL_GRAF_BLUE, COL_GRAF_PINK, COL_GRAF_PURPLE]),
        (cx + 8, [COL_GRAF_GREEN, COL_GRAF_YELLOW, COL_GRAF_PINK]),
    ]
    for wcx, colours in graf_palettes:
        _make_box_local(f"Skp_Wall_{int(wcx)}",
                        (wcx, wall_y, pz + wall_h / 2),
                        (4.5, 0.30, wall_h), COL_SK_CONCRETE)
        # Three coloured accent boxes per wall
        for j, gc in enumerate(colours):
            ox = -1.5 + j * 1.5
            oz = 0.4 + (j * 0.3) % 1.5
            _make_box_local(f"Skp_Wall_{int(wcx)}_Accent_{j}",
                            (wcx + ox, wall_y - 0.16,
                             pz + oz + 0.3),
                            (1.0, 0.04, 0.6), gc)

    # ── 3 SPECTATOR BENCHES around the edges ───────────────────
    bench_specs = [
        (cx - 13, cy + 7, '+X'),   # west side facing east into plaza
        (cx + 13, cy - 5, '-X'),   # east side facing west
        (cx + 2,  cy - 11, '+Y'),  # south side facing north
    ]
    for i, (bx, by, facing) in enumerate(bench_specs):
        # Seat
        if facing in ('+X', '-X'):
            seat_sz = (0.42, 1.6, 0.06)
            back_sz = (0.06, 1.6, 0.45)
            bx_back = 0.18 * (1 if facing == '-X' else -1)
            by_back = 0
        else:
            seat_sz = (1.6, 0.42, 0.06)
            back_sz = (1.6, 0.06, 0.45)
            bx_back = 0
            by_back = 0.18 * (1 if facing == '-Y' else -1)
        _make_box_local(f"Skp_Bench_{i}_Seat",
                        (bx, by, pz + 0.43), seat_sz,
                        (0.42, 0.30, 0.20, 1.0))
        _make_box_local(f"Skp_Bench_{i}_Back",
                        (bx + bx_back, by + by_back, pz + 0.85),
                        back_sz, (0.42, 0.30, 0.20, 1.0))

    # ── PERIMETER TREES · 10 old-growth oaks ringing the park ──
    perimeter = [
        (cx - 16, cy + 12), (cx - 8, cy + 13),
        (cx + 8, cy + 14), (cx + 16, cy + 8),
        (cx + 18, cy - 2), (cx + 14, cy - 13),
        (cx + 2, cy - 16), (cx - 10, cy - 14),
        (cx - 18, cy - 6), (cx - 19, cy + 6),
    ]
    for i, (tx, ty) in enumerate(perimeter):
        # Slight variation
        seed = (i * 31 + int(tx) * 11) % 100
        trunk_h = 4.5 + (seed % 5) * 0.5
        canopy_r = 3.5 + ((seed // 7) % 3) * 0.6
        _make_cyl_local(f"Skp_Tree_{i}_Trunk",
                        (tx, ty, pz + trunk_h / 2),
                        0.35, trunk_h,
                        (0.30, 0.22, 0.16, 1.0), segments=6)
        col = (0.22, 0.42, 0.20, 1.0) if i % 2 == 0 else (0.30, 0.48, 0.22, 1.0)
        _make_sphere_low_local(f"Skp_Tree_{i}_Canopy",
                                (tx, ty,
                                 pz + trunk_h + canopy_r * 0.5),
                                canopy_r, col, rings=3, segments=8)

    # ── MAIN ENTRY STAIRS + RAMP · drop-in from OT Park grade ─
    # The skatepark sits ~2.5 m below the OT Park platform. The
    # entry combo: a 4-step concrete staircase for walkers + a
    # parallel sloped concrete ramp (DROP-IN for skaters) +
    # GRIND RAIL handrail along the stairs.
    entry_y = cy + 16   # north edge of skatepark
    # 4 stair steps descending from pz+2.5 (OT Park level) to pz
    n_stairs = 4
    step_h = 2.5 / n_stairs
    step_d = 0.6
    step_w = 2.6
    for k in range(n_stairs):
        # Step k goes down — top at pz + (n_stairs - k - 0.5) * step_h
        sz = pz + (n_stairs - k - 0.5) * step_h
        sy_step = entry_y - k * step_d
        _make_box_local(f"Skp_EntryStair_{k}",
                        (cx - 2.0, sy_step, sz),
                        (step_w, step_d, step_h),
                        COL_SK_CONCRETE)
    # Concrete drop-in ramp parallel to the stairs (skater's line)
    ramp_w = 3.0
    ramp_l = n_stairs * step_d
    ramp_top_z = pz + 2.5
    ramp_bot_z = pz
    ramp_verts = [
        (cx + 2.0, entry_y - ramp_l, ramp_bot_z),
        (cx + 2.0 + ramp_w, entry_y - ramp_l, ramp_bot_z),
        (cx + 2.0 + ramp_w, entry_y, ramp_top_z),
        (cx + 2.0, entry_y, ramp_top_z),
        (cx + 2.0, entry_y - ramp_l, ramp_bot_z - 0.30),
        (cx + 2.0 + ramp_w, entry_y - ramp_l, ramp_bot_z - 0.30),
    ]
    ramp_faces = [
        [0, 1, 2, 3],          # top sloped surface
        [4, 5, 1, 0],          # bottom face
        [0, 3, 4],             # west cap
        [5, 2, 1],             # east cap
    ]
    _finalize_mesh("Skp_EntryRamp", ramp_verts, ramp_faces,
                   COL_SK_CONCRETE)
    # Handrail grind rail along the stairs — slopes down with steps
    # Each rail segment connects adjacent step tops.
    rail_h_above = 0.95
    for k in range(n_stairs):
        sz0 = pz + (n_stairs - k - 0.5) * step_h + rail_h_above
        sy0 = entry_y - k * step_d - step_d / 2
        sz1 = pz + (n_stairs - k - 1.5) * step_h + rail_h_above
        sy1 = entry_y - (k + 1) * step_d - step_d / 2
        # Suggest with a horizontal box at the midpoint
        midz = (sz0 + sz1) / 2
        midy = (sy0 + sy1) / 2
        _make_box_local(f"Skp_EntryHandrail_{k}",
                        (cx - 2.0 - step_w / 2 + 0.08, midy, midz),
                        (0.07, step_d * 1.4, 0.07), COL_SK_RAIL)
    # Rail posts at each step edge
    for k in range(n_stairs + 1):
        sz = pz + (n_stairs - k) * step_h + rail_h_above / 2
        sy_post = entry_y - k * step_d
        _make_box_local(f"Skp_EntryRailPost_{k}",
                        (cx - 2.0 - step_w / 2 + 0.08, sy_post, sz),
                        (0.07, 0.07, rail_h_above), COL_SK_RAIL)

    # ── 2 ADDITIONAL BENCHES near the entry stairs ────────────
    for i, (bx, by) in enumerate([(cx - 12, cy + 13), (cx + 12, cy + 13)]):
        _make_box_local(f"Skp_EntryBench_{i}_Seat",
                        (bx, by, pz + 0.43),
                        (1.6, 0.42, 0.06), (0.42, 0.30, 0.20, 1.0))
        _make_box_local(f"Skp_EntryBench_{i}_Back",
                        (bx, by + 0.18, pz + 0.85),
                        (1.6, 0.06, 0.45), (0.42, 0.30, 0.20, 1.0))

    # ── ENTRY MARKER · small post with cyan beacon top so the
    # skatepark can be found from the air ──
    BEACON_H = 25.0
    _make_cyl_local("Skp_BeaconPole",
                    (cx + 18, cy, pz + BEACON_H / 2),
                    0.18, BEACON_H, (0.10, 0.10, 0.10, 1.0),
                    segments=4)
    _make_box_local("Skp_BeaconTop",
                    (cx + 18, cy, pz + BEACON_H + 1.0),
                    (2.0, 2.0, 1.4), (0.32, 0.55, 0.78, 1.0))


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
    build_oliver_tree_skatepark()
    export_glb()


if __name__ == "__main__":
    main()
