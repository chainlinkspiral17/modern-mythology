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
    # Chapter-one commercial block pads — nested inside the
    # broader SouthComm belt so each building footprint is locally
    # flat regardless of the parent zone's residual wild-zone
    # bumps. Each pad covers building + sidewalk + parking-lot
    # apron, at the same target_z (-9.0) as SouthComm with higher
    # flatness (0.95) so they win the blend. Repositioned to the
    # closed-block layout: NexCorp -60, Kwik Shop -15 (28 m wide),
    # Diner 35, Cosmic Comics 70.
    ("KwikShopPad",  -30,    1,  -385, -345, -9.0, 0.95),
    ("NexCorpGGPad", -80,  -42,  -395, -345, -9.0, 0.95),
    ("DinerPad",      22,   50,  -380, -345, -9.0, 0.95),
    ("CosmicCPad",    62,   80,  -380, -345, -9.0, 0.95),
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
    # FoundersPond moved south of the OT Park settlement zone — was
    # at (-300, 140) with radius 45, but the OT Park rect (-300 to
    # -220, 60 to 180) flattened the western half of the pond so
    # the water disc hung out across the hillside next to the
    # gazebo. Now at (-380, 30) with radius 32, fully in the wild
    # zone south of the park where the depression carves naturally.
    ("FoundersPond",   -380,   30,  32,  8.0),
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
    """Steep-walled circular bowl with a flat-ish bottom and a
    clear caldera lip at the rim. Per user feedback: "there is no
    lip from the caldera it sits in." Replaced the gentle Gaussian
    with a smoothstep ramp that's full-depth for d < 0.5×radius
    and ramps up to 0 over the remaining 0.5×radius. Reads as a
    real sunken pond, not a vague dip."""
    d = math.hypot(x - cx, y - cy)
    if d >= radius:
        return 0.0
    if d <= radius * 0.5:
        return -depth
    # Smoothstep ramp from depth at r=0.5R to 0 at r=R
    t = (d - radius * 0.5) / (radius * 0.5)
    s = 1.0 - t * t * (3 - 2 * t)
    return -depth * s


def mesh_z(px, py):
    """Returns the z that the ground mesh ACTUALLY renders at
    (px, py). Matches Godot's triangle rasterisation, not analytic
    bilinear interpolation. Quads are triangulated diagonal
    bottom-left → top-right (see build_ground), so:
      tx ≥ ty → lower triangle (a, b, c) = BL, BR, TR
      tx < ty → upper triangle (a, c, d) = BL, TR, TL
    The earlier bilinear version was off by up to 1 m on a sloped
    quad — that was the visible "post hovering above the ground"
    issue the user kept flagging."""
    cell_w = (DIST_MAX_X - DIST_MIN_X) / GROUND_NX
    cell_h = (DIST_MAX_Y - DIST_MIN_Y) / GROUND_NY
    fi = (px - DIST_MIN_X) / cell_w
    fj = (py - DIST_MIN_Y) / cell_h
    i = int(math.floor(fi))
    j = int(math.floor(fj))
    tx = fi - i
    ty = fj - j
    i = max(0, min(GROUND_NX - 1, i))
    j = max(0, min(GROUND_NY - 1, j))
    x0 = DIST_MIN_X + cell_w * i
    x1 = DIST_MIN_X + cell_w * (i + 1)
    y0 = DIST_MIN_Y + cell_h * j
    y1 = DIST_MIN_Y + cell_h * (j + 1)
    z00 = hce_elevation(x0, y0)   # bottom-left = a
    z10 = hce_elevation(x1, y0)   # bottom-right = b
    z11 = hce_elevation(x1, y1)   # top-right = c
    z01 = hce_elevation(x0, y1)   # top-left = d
    if tx >= ty:
        return z00 * (1.0 - tx) + z10 * (tx - ty) + z11 * ty
    return z00 * (1.0 - ty) + z11 * tx + z01 * (ty - tx)


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
    # Taller + wider than the first pass so the park reads ACTUALLY
    # HILLY instead of "subtle ridges way at the edges." Walkway
    # alignment now handled by per-vertex mesh_z sampling, so we
    # can let the central walkway curve up over a gentle statue
    # mound instead of insisting on a perfectly flat plaza.
    # West perimeter embankment — taller hill flanking the park
    ("OTPark_WestEmb",     [(-296, 70),  (-296, 168)],   8.0, 3.2),
    ("OTPark_EastEmb",     [(-224, 70),  (-224, 168)],   8.0, 3.2),
    # North perimeter ridge behind the terrace overlook
    ("OTPark_NorthEmb",    [(-296, 175), (-224, 175)],   6.0, 2.4),
    # Viewing knoll in the NE corner
    ("OTPark_NEKnoll",     [(-238, 165), (-225, 168)],  14.0, 3.6),
    # (SWKnoll removed — was sitting directly on top of the
    #  OTSkatePark zone and burying it under +2.5 m of berm.
    #  Skatepark needs the SW corner to stay sunken.)
    # CENTRAL STATUE MOUND · the statue sits on a gentle rise of
    # ~1 m at peak, dying off over a 14 m radius so the walkway ring
    # has a barely-perceptible slope and the plinth is the highest
    # point of the plaza. Memorial parks almost always elevate the
    # honoured subject like this.
    ("OTPark_StatueMound", [(-260, 120), (-260, 120)],  14.0, 1.0),
    # Sloped berm between the south path and the reflecting pool —
    # the path approach gains a slight rise before descending
    # toward the pool.
    ("OTPark_SouthRise",   [(-265, 98),  (-255, 98)],   6.0, 0.8),
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
            z = mesh_z(wx, wy)
            verts.append((wx, wy, z))
    faces = []
    # Explicit triangulation matching mesh_z (diagonal BL→TR).
    # Quads can be split either way and Godot's behaviour varies;
    # by emitting triangles ourselves we guarantee alignment.
    for j in range(GROUND_NY):
        for i in range(GROUND_NX):
            a = j * nx_plus_1 + i           # bottom-left
            b = a + 1                       # bottom-right
            c = b + nx_plus_1               # top-right
            d = a + nx_plus_1               # top-left
            faces.append([a, b, c])         # lower triangle
            faces.append([a, c, d])         # upper triangle
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
    Each segment samples mesh_z at its four corners and places the
    water plane 0.6 m below the CHANNEL FLOOR at each point — so
    the water follows the carved ravine instead of using a single
    hardcoded z that floats above the channel in some places and
    sinks below ground in others. Width also shrunk to 60% of the
    flood-plain width so the water disc stays well inside the
    carved walls (per the user's "water floating above the hole"
    feedback)."""
    width = 3.6           # was 6.0; shrunk so the disc stays inside
    for i in range(len(CREEK_POINTS) - 1):
        x0, y0 = CREEK_POINTS[i]
        x1, y1 = CREEK_POINTS[i + 1]
        dx = x1 - x0; dy = y1 - y0
        ang = math.atan2(dy, dx)
        perp_x = -math.sin(ang); perp_y = math.cos(ang)
        # Water surface is FLAT within each segment (real water
        # doesn't tilt). Sample mesh_z at all four corners then
        # use the MAXIMUM as the segment's water plane z — that
        # way the surface stays above the channel floor at every
        # corner (no z-fighting) without dipping below the floor
        # at the highest corner. Per-corner sampling would tilt
        # the quad with the channel slope, which looks wrong.
        corners = [
            (x0 - perp_x * width / 2, y0 - perp_y * width / 2),
            (x1 - perp_x * width / 2, y1 - perp_y * width / 2),
            (x1 + perp_x * width / 2, y1 + perp_y * width / 2),
            (x0 + perp_x * width / 2, y0 + perp_y * width / 2),
        ]
        seg_z = max(mesh_z(vx, vy) for (vx, vy) in corners) + 0.05
        verts = [(vx, vy, seg_z) for (vx, vy) in corners]
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
        z = mesh_z(x, y)
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
        z = mesh_z(cx, cy)
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
        bottom_z = mesh_z(cx, cy)
        # Water sits ~0.7 m below the SURROUNDING RIM elevation.
        rim_samples = []
        for sample_i in range(8):
            ang = 2.0 * math.pi * sample_i / 8
            sx_pt = cx + math.cos(ang) * radius * 1.05
            sy_pt = cy + math.sin(ang) * radius * 1.05
            rim_samples.append(hce_elevation(sx_pt, sy_pt))
        rim_z = sum(rim_samples) / len(rim_samples)
        water_z = min(bottom_z + 1.5, rim_z - 0.7)
        # CRITICAL: shrink the water disc so it stays INSIDE the
        # bowl. The user's complaint: "pond reads as polygon of
        # water floating above the ground." Root cause: water disc
        # extended to 0.80 × radius but the analytic depression is
        # only deeper than water_z within ~0.4 × radius. Beyond
        # that, the flat disc sat above the rising bowl wall.
        # Sample the actual terrain at candidate radii and find
        # the largest radius where mesh terrain is still BELOW
        # water level — that's the water's true extent.
        # Water disc · shrunk to 0.48 × radius so the entire disc
        # sits inside the depression's flat-bottom plateau (which
        # extends to d = 0.50 × radius before the rim ramp begins).
        # Earlier 0.70 × radius extended into the rising rim and
        # the user could see water "hanging out" past the carved
        # hole. Now the disc terminates 2% inside the plateau and
        # the carved channel walls visibly rise on all sides.
        wr = radius * 0.48
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
                    vz = max(mesh_z(vx, vy), inner_z + 0.05)
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
            rz = max(mesh_z(rx, ry), water_z + 0.05)
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
            bz = mesh_z(bx, by)
            _make_sphere_low_local(f"PondBush_{name}_{k}",
                                   (bx, by, bz + 0.45),
                                   0.6 + 0.15 * (k % 2),
                                   (0.32, 0.55, 0.28, 1.0),
                                   rings=3, segments=6)

        # ── PER-POND INFRASTRUCTURE per user feedback ──
        # "there is no infrastructure around it." Each pond now
        # gets a circular GRAVEL WALKING PATH on the rim + 2
        # FACING BENCHES + a brown PARK SIGN.
        path_r = radius * 1.18    # walk at the outer rim
        path_w = 2.0
        n_path = 24
        path_verts = []
        for ring_idx, ring_r in ((0, path_r - path_w / 2),
                                 (1, path_r + path_w / 2)):
            for i in range(n_path):
                a = 2.0 * math.pi * i / n_path
                vx = cx + math.cos(a) * ring_r
                vy = cy + math.sin(a) * ring_r
                vz = mesh_z(vx, vy) + 0.025
                path_verts.append((vx, vy, vz))
        path_faces = []
        for i in range(n_path):
            ni = (i + 1) % n_path
            path_faces.append([i, ni, ni + n_path, i + n_path])
        _finalize_mesh(f"PondPath_{name}", path_verts, path_faces,
                       (0.62, 0.55, 0.42, 1.0))   # gravel tan

        # 2 benches facing the pond, ~120° apart on the path
        for bi, bang in enumerate((0.85, 4.0)):
            bx = cx + math.cos(bang) * path_r * 1.04
            by = cy + math.sin(bang) * path_r * 1.04
            bz = mesh_z(bx, by)
            # Seat orientation by which axis is longer in the
            # radial direction (so seat parallels the pond rim)
            radial_x = math.cos(bang); radial_y = math.sin(bang)
            if abs(radial_y) > abs(radial_x):
                seat_sz = (1.4, 0.38, 0.06)
                back_off = (0, 0.18 * (1 if radial_y > 0 else -1), 0)
                back_sz = (1.4, 0.06, 0.42)
            else:
                seat_sz = (0.38, 1.4, 0.06)
                back_off = (0.18 * (1 if radial_x > 0 else -1), 0, 0)
                back_sz = (0.06, 1.4, 0.42)
            _make_box_local(f"PondBench_{name}_{bi}_Seat",
                            (bx, by, bz + 0.43), seat_sz,
                            (0.42, 0.30, 0.20, 1.0))
            _make_box_local(f"PondBench_{name}_{bi}_Back",
                            (bx + back_off[0], by + back_off[1],
                             bz + 0.82),
                            back_sz, (0.42, 0.30, 0.20, 1.0))

        # Brown park sign on the south-side of the path
        sgn_x = cx
        sgn_y = cy - path_r * 1.12
        sgn_z = mesh_z(sgn_x, sgn_y)
        for sgn_post_x in (-0.6, 0.6):
            _make_cyl_local(f"PondSign_{name}_Post_{sgn_post_x:+.1f}",
                            (sgn_x + sgn_post_x, sgn_y, sgn_z + 1.1),
                            0.06, 2.2, (0.40, 0.30, 0.20, 1.0),
                            segments=4)
        _make_box_local(f"PondSign_{name}_Panel",
                        (sgn_x, sgn_y, sgn_z + 1.9),
                        (1.8, 0.10, 0.70),
                        (0.40, 0.30, 0.20, 1.0))
        _make_box_local(f"PondSign_{name}_Face",
                        (sgn_x, sgn_y - 0.07, sgn_z + 1.9),
                        (1.6, 0.04, 0.55),
                        (0.86, 0.82, 0.70, 1.0))


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
        z = mesh_z(mx, my)
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
    ground_z = mesh_z(sx, sy)

    # ── Plinth · three tiers (base + tapered shaft + cap) ──────
    COL_PLINTH_BASE = (0.68, 0.64, 0.56, 1.0)    # darker base stone
    COL_PLINTH_SHAFT = (0.78, 0.74, 0.66, 1.0)   # cream main
    COL_PLINTH_CAP = (0.85, 0.80, 0.70, 1.0)     # lighter cap
    COL_PLAQUE = (0.65, 0.48, 0.20, 1.0)
    # Wider + TALLER plinth so the 4.5 m figure doesn't dwarf its
    # base. Total height 2.8 m, base footprint 4.4 × 3.8 m.
    base_w, base_d, base_h = 4.4, 3.8, 0.7
    base_z = ground_z + base_h / 2
    _make_box_local("OT_Plinth_Base",
                    (sx, sy, base_z),
                    (base_w, base_d, base_h),
                    COL_PLINTH_BASE)
    # Tapered shaft — middle tier (taller, slightly wider)
    shaft_w, shaft_d, shaft_h = 3.4, 2.9, 1.8
    shaft_z = ground_z + base_h + shaft_h / 2
    _make_box_local("OT_Plinth",
                    (sx, sy, shaft_z),
                    (shaft_w, shaft_d, shaft_h),
                    COL_PLINTH_SHAFT)
    # Cap overhang — light stone moulding
    cap_w, cap_d, cap_h = 3.8, 3.3, 0.30
    cap_z = ground_z + base_h + shaft_h + cap_h / 2
    _make_box_local("OT_Plinth_Cap",
                    (sx, sy, cap_z),
                    (cap_w, cap_d, cap_h),
                    COL_PLINTH_CAP)
    # Brass plaque on the shaft front (south face) · scales with
    # the larger shaft.
    _make_box_local("OT_Plaque",
                    (sx, sy - shaft_d / 2 - 0.04, shaft_z),
                    (2.4, 0.08, 1.10),
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

    # ── PROP: microphone in the RIGHT HAND, foam ball at MOUTH.
    # Math: hand at shoulder + 0.20 (chin plane for scale 2.5);
    # mouth at shoulder + 0.29. Need foam ball at +0.29, so mic
    # angles UP only 6 cm from the hand, mostly FORWARD toward
    # the face. Previous 30 cm upward offset put the ball at
    # shoulder + 0.53 — 24 cm above the mouth, near forehead.
    hx, hy, hz = figure_meta["hands"]["R"]
    mic_top_x = hx + 0.0
    mic_top_y = hy - 0.22        # 22 cm forward of hand toward face
    mic_top_z = hz + 0.06         # only 6 cm up · brings ball to mouth
    _build_oriented_handle(
        "OT_MicHandle", (hx, hy, hz),
        (mic_top_x, mic_top_y, mic_top_z),
        radius=0.05, color=(0.12, 0.12, 0.12, 1.0))
    # Foam ball overlapping the handle top (4 cm beyond)
    _make_sphere_low_local("OT_MicHead",
                           (mic_top_x, mic_top_y - 0.04,
                            mic_top_z + 0.02),
                           0.09, (0.18, 0.18, 0.18, 1.0),
                           rings=3, segments=8)

    # ── PROP: scooter leaning against the SE corner of the plinth.
    # User feedback: "weird placed scooter" — was too far from
    # plinth (2.6 m east). Now sits flush against the east face,
    # 1.5 m from the plinth centerline.
    sc_x, sc_y = sx + 1.5, sy - 0.4
    sc_ground = mesh_z(sc_x, sc_y)
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
        tz = mesh_z(tx, ty)
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
        cd_z = mesh_z(cd_x, cd_y)
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
    ph_z = mesh_z(ph_x, ph_y)
    _make_box_local("OT_Tribute_Photo",
                    (ph_x, ph_y, ph_z + 0.30),
                    (0.30, 0.04, 0.40),
                    (0.95, 0.92, 0.84, 1.0))
    # Scooter wheel
    wh_x, wh_y = sx + 1.6, tribute_y - 0.20
    wh_z = mesh_z(wh_x, wh_y)
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
    park_z = mesh_z(sx, sy)   # platform z after settlement flatten

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

    # ── Central walkway ring · per-vertex mesh_z ──────────────
    segs = 18
    inner_r = 12.0; outer_r = 15.0
    ring_verts = []
    for ring_idx, r in ((0, inner_r), (1, outer_r)):
        for i in range(segs):
            ang = 2.0 * math.pi * i / segs
            vx = sx + math.cos(ang) * r
            vy = sy + math.sin(ang) * r
            ring_verts.append((vx, vy, mesh_z(vx, vy) + 0.02))
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
    # Radial paths · build as 4-vert quads with per-vertex mesh_z
    # so they follow the slope of the platform rather than hanging
    # at the analytic park_z.
    for tag, dx, dy, length in radials:
        start_x = sx + dx * outer_r
        start_y = sy + dy * outer_r
        end_x = sx + dx * (outer_r + length)
        end_y = sy + dy * (outer_r + length)
        # Perpendicular for path width
        if abs(dx) > abs(dy):
            perp_x, perp_y = 0.0, 1.0
        else:
            perp_x, perp_y = 1.0, 0.0
        hw = path_w / 2
        pv = []
        for (px, py) in [(start_x - perp_x * hw, start_y - perp_y * hw),
                         (end_x - perp_x * hw, end_y - perp_y * hw),
                         (end_x + perp_x * hw, end_y + perp_y * hw),
                         (start_x + perp_x * hw, start_y + perp_y * hw)]:
            pv.append((px, py, mesh_z(px, py) + 0.025))
        _finalize_mesh(f"OTPark_Path_{tag}", pv, [[0, 1, 2, 3]], COL_PATH)

    # ── Terraced rise at the NORTH end — sample terrain at the
    # terrace centre so the steps stack on the ACTUAL ground, not
    # the analytic park_z. With the new park-interior berms the
    # ground here sits ~40 cm higher than park_z.
    terr_cx = sx
    terr_cy = sy + outer_r + 30 + 6
    terr_ground = mesh_z(terr_cx, terr_cy)
    # Step 1: 22 × 12 m, lifts 0.60 m above the actual ground
    _make_box_local("OTPark_Terrace_1",
                    (terr_cx, terr_cy, terr_ground + 0.30),
                    (22, 12, 0.60), COL_TERRACE)
    terr1_top = terr_ground + 0.60
    # Step 2: 14 × 8 m, sits on top of step 1
    _make_box_local("OTPark_Terrace_2",
                    (terr_cx, terr_cy + 2, terr1_top + 0.30),
                    (14, 8, 0.60), COL_TERRACE)
    terr2_top = terr1_top + 0.60
    # Terrace balustrade — proper full-width railing along the
    # front edge of step 2 (was two wing-walls covering only 3 m
    # of the 14 m front). 13 stone balusters spaced every 1 m
    # connected by top + bottom rails. A 2 m centre opening lines
    # up with the main descent path.
    bal_y = terr_cy - 2 + 0.10
    bal_h = 0.80
    bal_top_z = terr2_top + bal_h
    n_bal = 13
    centre_gap_idx = 6     # the central baluster is omitted for gap
    for k in range(n_bal):
        bx = terr_cx - 6.0 + k * 1.0
        if k == centre_gap_idx:
            continue
        _make_box_local(f"OTPark_Terrace_Bal_{k}",
                        (bx, bal_y, terr2_top + bal_h / 2),
                        (0.18, 0.18, bal_h), COL_TERRACE)
    # Top + bottom rails on each side of the central opening
    for side_tag, x_start, x_end in (
        ("L", terr_cx - 6.5, terr_cx - 0.6),
        ("R", terr_cx + 0.6, terr_cx + 6.5)):
        rail_mid = (x_start + x_end) / 2
        rail_w = x_end - x_start
        _make_box_local(f"OTPark_Terrace_TopRail_{side_tag}",
                        (rail_mid, bal_y, bal_top_z - 0.06),
                        (rail_w, 0.22, 0.12), COL_TERRACE)
        _make_box_local(f"OTPark_Terrace_BotRail_{side_tag}",
                        (rail_mid, bal_y, terr2_top + 0.12),
                        (rail_w, 0.22, 0.10), COL_TERRACE)
    # Anchor end-posts at the two corners
    for sgn in (-1, 1):
        _make_box_local(f"OTPark_Terrace_EndPost_{sgn:+d}",
                        (terr_cx + sgn * 6.6, bal_y,
                         terr2_top + (bal_h + 0.15) / 2),
                        (0.30, 0.30, bal_h + 0.15), COL_TERRACE)
    # Two stair stubs leading up to step 1
    for ox in (-5, 5):
        stair_x = sx + ox
        stair_y = sy + outer_r + 30 - 1.5
        stair_ground = mesh_z(stair_x, stair_y)
        _make_box_local(f"OTPark_Stairs_{ox:+d}",
                        (stair_x, stair_y, stair_ground + 0.15),
                        (2.0, 1.5, 0.30), COL_TERRACE)
    terrace_top_z = terr2_top    # used by gazebo below

    # ── Reflecting pool 22 m SOUTH of statue · pool z derived
    # from mesh_z at the pool centre, NOT park_z. The statue
    # mound makes ground at pool location slightly lower than
    # park_z.
    pool_cx = sx
    pool_cy = sy - 22
    pool_r = 6.0
    pool_ground = mesh_z(pool_cx, pool_cy)
    pool_water_z = pool_ground - 0.30
    pool_segs = 16
    pverts = [(pool_cx, pool_cy, pool_water_z)]
    for i in range(pool_segs):
        ang = 2.0 * math.pi * i / pool_segs
        pverts.append((pool_cx + math.cos(ang) * pool_r,
                       pool_cy + math.sin(ang) * pool_r,
                       pool_water_z))
    pfaces = []
    for i in range(pool_segs):
        ni = (i + 1) % pool_segs
        pfaces.append([0, 1 + i, 1 + ni])
    _finalize_mesh("OTPark_Pool", pverts, pfaces, COL_POOL_WATER)
    # Concrete rim · sits at pool_ground + 0.05 m
    rverts = []
    for ring_idx, r in ((0, pool_r), (1, pool_r + 0.6)):
        for i in range(pool_segs):
            ang = 2.0 * math.pi * i / pool_segs
            rverts.append((pool_cx + math.cos(ang) * r,
                           pool_cy + math.sin(ang) * r,
                           pool_ground + 0.05))
    rfaces = []
    for i in range(pool_segs):
        ni = (i + 1) % pool_segs
        rfaces.append([i, ni, ni + pool_segs, i + pool_segs])
    _finalize_mesh("OTPark_Pool_Rim", rverts, rfaces, COL_POOL_RIM)

    # ── FOUNTAIN JET in the reflecting pool · anchored to pool z
    fountain_cx = pool_cx
    fountain_cy = pool_cy
    _make_cyl_local("OTPark_FountainBase",
                    (fountain_cx, fountain_cy, pool_ground - 0.15),
                    0.45, 0.5, COL_POOL_RIM, segments=8)
    _make_cyl_local("OTPark_FountainJet",
                    (fountain_cx, fountain_cy, pool_ground + 1.20),
                    0.10, 2.4, (0.55, 0.78, 0.85, 1.0), segments=6)
    _make_sphere_low_local("OTPark_FountainCrown",
                            (fountain_cx, fountain_cy, pool_ground + 2.50),
                            0.50, (0.78, 0.92, 0.95, 1.0),
                            rings=3, segments=8)
    for k in range(6):
        ang_k = 2.0 * math.pi * k / 6
        sx_off = math.cos(ang_k) * 0.5
        sy_off = math.sin(ang_k) * 0.5
        _make_sphere_low_local(f"OTPark_FountainSpray_{k}",
                                (fountain_cx + sx_off,
                                 fountain_cy + sy_off,
                                 pool_ground + 0.35),
                                0.18, (0.62, 0.82, 0.88, 1.0),
                                rings=3, segments=6)

    # ── FLAG POLE at half-mast · samples its OWN ground per the
    # alignment golden rule. Previous position (sx+18, sy-20) =
    # (-242, 100) was clipping through the SE oak canopy at
    # (-242, 94) (canopy r up to 5.8 m, pole only 6 m away).
    # Moved south + east to (sx+8, sy-45) = (-252, 75) on the
    # south path approach. Clear of every oak by ≥ 21 m and gives
    # the player a sight line back to the statue. Stays at
    # half-mast per US flag code: flag centre at 50% of pole height.
    fp_x = sx + 8
    fp_y = sy - 45
    fp_z = mesh_z(fp_x, fp_y)
    FLAGPOLE_H = 8.0
    _make_cyl_local("OTPark_FlagPole",
                    (fp_x, fp_y, fp_z + FLAGPOLE_H / 2),
                    0.10, FLAGPOLE_H, (0.82, 0.80, 0.76, 1.0),
                    segments=8)
    _make_box_local("OTPark_FlagPole_Base",
                    (fp_x, fp_y, fp_z + 0.15),
                    (0.80, 0.80, 0.30), COL_POOL_RIM)
    _base_skirt("OTPark_FlagPole_Skirt", fp_x, fp_y, fp_z,
                 color=(0.30, 0.46, 0.20, 1.0), radius=1.10)
    flag_z = fp_z + FLAGPOLE_H * 0.50
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
    # Gold finial · uses fp_z (matches the rest of the pole)
    _make_sphere_low_local("OTPark_FlagPole_Finial",
                            (fp_x, fp_y, fp_z + FLAGPOLE_H + 0.10),
                            0.10, (0.78, 0.62, 0.28, 1.0),
                            rings=3, segments=6)
    # Small brass plaque at the foot of the pole giving in-world
    # explanation for the half-mast position (the user found the
    # half-mast "curious" with no context — this answers why).
    _make_box_local("OTPark_FlagPlaque",
                    (fp_x, fp_y - 0.55, fp_z + 0.65),
                    (0.50, 0.04, 0.30), (0.55, 0.42, 0.20, 1.0))

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
        seed = (i * 17 + int(ox) * 7 + int(oy) * 13) % 100
        trunk_h = 4.5 + (seed % 5) * 0.7
        canopy_r = 4.0 + ((seed // 7) % 4) * 0.6
        lean_x = (((seed * 31) % 7) - 3) * 0.12
        lean_y = (((seed * 53) % 7) - 3) * 0.12
        trunk_col = COL_OAK_TRUNK if (seed % 3) else (0.36, 0.26, 0.18, 1.0)
        # Per-tree elevation · golden rule
        oz = mesh_z(ox, oy)
        _make_cyl_local(f"OTPark_Oak_{i}_Trunk",
                        (ox, oy, oz + trunk_h / 2),
                        0.40 + (seed % 3) * 0.10, trunk_h,
                        trunk_col, segments=6)
        col = COL_OAK_CANOPY if i % 2 == 0 else COL_OAK_CANOPY2
        _make_sphere_low_local(
            f"OTPark_Oak_{i}_CanopyCore",
            (ox + lean_x, oy + lean_y,
             oz + trunk_h + canopy_r * 0.45),
            canopy_r * 0.7, COL_OAK_TRUNK, rings=3, segments=6)
        _make_sphere_low_local(
            f"OTPark_Oak_{i}_Canopy",
            (ox + lean_x, oy + lean_y,
             oz + trunk_h + canopy_r * 0.55),
            canopy_r, col, rings=3, segments=8)

    # ── 3 picnic tables under shade trees ─────────────────────
    picnic_spots = [
        (sx - 24, sy + 18),     # NW shade
        (sx + 24, sy + 18),     # NE shade
        (sx - 24, sy - 18),     # SW shade
    ]
    for i, (px, py) in enumerate(picnic_spots):
        pz_local = mesh_z(px, py)
        _make_box_local(f"OTPark_Picnic_{i}_Top",
                        (px, py, pz_local + 0.75),
                        (2.0, 0.90, 0.06), COL_PICNIC)
        for sign in (-1, 1):
            _make_box_local(f"OTPark_Picnic_{i}_Bench_{sign:+d}",
                            (px, py + sign * 0.70, pz_local + 0.42),
                            (2.0, 0.36, 0.05), COL_PICNIC)
            for tx in (-0.85, 0.85):
                _make_box_local(f"OTPark_Picnic_{i}_BLeg_{sign:+d}_{tx:+.1f}",
                                (px + tx, py + sign * 0.70,
                                 pz_local + 0.21),
                                (0.06, 0.06, 0.42), COL_PICNIC)

    # ── 5 benches: 4 around the ring + 1 on the terrace ──────
    bench_angles = [45, 135, 225, 315]    # diagonals so they face statue
    for i, ang_deg in enumerate(bench_angles):
        ang = math.radians(ang_deg)
        bx = sx + math.cos(ang) * 13.2
        by = sy + math.sin(ang) * 13.2
        bz = mesh_z(bx, by)
        _make_box_local(f"OTPark_Bench_{i}_Seat",
                        (bx, by, bz + 0.43),
                        (1.6, 0.42, 0.06), COL_BENCH)
        back_off_x = math.cos(ang) * 0.18
        back_off_y = math.sin(ang) * 0.18
        if abs(math.cos(ang)) > abs(math.sin(ang)):
            back_sz = (0.06, 1.5, 0.45)
        else:
            back_sz = (1.5, 0.06, 0.45)
        _make_box_local(f"OTPark_Bench_{i}_Back",
                        (bx + back_off_x, by + back_off_y,
                         bz + 0.85),
                        back_sz, COL_BENCH)
    # Gazebo on the top terrace step · floor matches the REAL
    # terrace_top_z (computed from mesh_z, not the analytic park_z)
    # so the gazebo floor sits flush on top of step 2 instead of
    # floating 30-40 cm above it.
    _build_gazebo("OTPark_Gazebo",
                  terr_cx, terr_cy + 2,
                  terrace_top_z,
                  radius=3.6, height=3.2)

    # ── Pink flower planters at four diagonals · per-bed z ────
    for tag, ang_deg in (('NE', 45), ('NW', 135),
                          ('SW', 225), ('SE', 315)):
        ang = math.radians(ang_deg)
        fx = sx + math.cos(ang) * 10.0
        fy = sy + math.sin(ang) * 10.0
        fz = mesh_z(fx, fy)
        if abs(math.cos(ang)) > abs(math.sin(ang)):
            sx_bed, sy_bed = 1.0, 2.0
        else:
            sx_bed, sy_bed = 2.0, 1.0
        _make_box_local(f"OTPark_FlowerBed_{tag}",
                        (fx, fy, fz + 0.20),
                        (sx_bed, sy_bed, 0.30), COL_FLOWER_BED)
        _make_box_local(f"OTPark_Flowers_{tag}",
                        (fx, fy, fz + 0.50),
                        (sx_bed - 0.10, sy_bed - 0.10, 0.18),
                        COL_FLOWER_PINK)

    # ── PARK ENTRY ARCHWAY · stone arch over the south entry ─
    # Local plinth colour constants (the statue build's constants
    # aren't visible from this function).
    COL_PLINTH_BASE = (0.68, 0.64, 0.56, 1.0)
    COL_PLINTH_SHAFT = (0.78, 0.74, 0.66, 1.0)
    COL_PLINTH_CAP = (0.85, 0.80, 0.70, 1.0)
    arch_y = sy - outer_r - 30
    arch_w = 7.0
    arch_post_w = 1.0
    arch_post_h = 4.5
    arch_post_d = 1.2
    for sign in (-1, 1):
        post_x = sx + sign * (arch_w / 2 + arch_post_w / 2)
        post_ground = mesh_z(post_x, arch_y)
        _make_box_local(f"OTPark_ArchPost_{sign:+d}",
                        (post_x, arch_y, post_ground + arch_post_h / 2),
                        (arch_post_w, arch_post_d, arch_post_h),
                        COL_PLINTH_BASE)
        _make_box_local(f"OTPark_ArchPostCap_{sign:+d}",
                        (post_x, arch_y, post_ground + arch_post_h + 0.15),
                        (arch_post_w + 0.30, arch_post_d + 0.30, 0.25),
                        COL_PLINTH_CAP)
        # Grass skirt at the foot of each post
        _base_skirt(f"OTPark_ArchPost_{sign:+d}_Skirt",
                     post_x, arch_y, post_ground,
                     color=(0.30, 0.46, 0.20, 1.0), radius=0.85)
    # Beam + inscription anchored to the LOWER of the two posts so
    # the lintel doesn't tilt
    arch_ground = mesh_z(sx, arch_y)
    _make_box_local("OTPark_ArchBeam",
                    (sx, arch_y, arch_ground + arch_post_h + 0.65),
                    (arch_w + 2 * arch_post_w + 0.6, arch_post_d + 0.3, 0.55),
                    COL_PLINTH_SHAFT)
    _make_box_local("OTPark_ArchInscription",
                    (sx, arch_y - arch_post_d / 2 - 0.04,
                     arch_ground + arch_post_h + 0.65),
                    (arch_w + 1.5, 0.06, 0.40),
                    (0.45, 0.40, 0.32, 1.0))

    # ── Park sign at the SOUTH entry · mesh_z at sign position ─
    sign_x = sx
    sign_y = sy - outer_r - 48
    sign_ground = mesh_z(sign_x, sign_y)
    for sign_post_x in (-1.4, 1.4):
        sp_x = sign_x + sign_post_x
        _make_cyl_local(f"OTPark_SignPost_{sign_post_x:+.1f}",
                        (sp_x, sign_y, sign_ground + 1.4),
                        0.08, 2.8, COL_SIGN_BROWN, segments=4)
        _base_skirt(f"OTPark_SignPost_{sign_post_x:+.1f}_Skirt",
                     sp_x, sign_y, sign_ground,
                     color=(0.30, 0.46, 0.20, 1.0), radius=0.35)
    _make_box_local("OTPark_SignPanel",
                    (sign_x, sign_y, sign_ground + 2.2),
                    (3.4, 0.15, 1.20), COL_SIGN_BROWN)
    _make_box_local("OTPark_SignLetters",
                    (sign_x, sign_y - 0.08, sign_ground + 2.2),
                    (3.0, 0.06, 0.90), COL_SIGN_FACE)

    # ── 6 LAMPPOSTS along the radial paths · per-position z ──
    for tag, dx, dy, length in radials:
        for t in (0.45, 0.95):
            lx = sx + dx * (outer_r + length * t)
            ly = sy + dy * (outer_r + length * t)
            _build_lamppost(f"OTPark_Lamp_{tag}_{int(t*100)}",
                            lx, ly, mesh_z(lx, ly))

    # ── 2 TRASHCANS + 1 DRINKING FOUNTAIN · per-position z ──
    for tx, ty, tag in [(sx - 2.5, sy - outer_r - 40, 'W'),
                          (sx + 2.5, sy - outer_r - 40, 'E')]:
        _build_trashcan(f"OTPark_Trash_{tag}",
                         tx, ty, mesh_z(tx, ty))
    fnt_x, fnt_y = sx - 20, sy - 5
    _build_drinking_fountain("OTPark_Fountain",
                              fnt_x, fnt_y, mesh_z(fnt_x, fnt_y))

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
        seed = (i * 23) % 100
        sw = 0.40 + (seed % 4) * 0.06
        sh = 0.22 + (seed % 3) * 0.05
        col = stone_palette[seed % len(stone_palette)]
        # Per-stone elevation sample · golden rule
        ez = mesh_z(ex, ey)
        _make_box_local(f"OTPark_EdgeStone_{i}",
                        (ex, ey, ez + sh / 2 + 0.02),
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
        bz = mesh_z(bx, by)
        _make_sphere_low_local(f"OTPark_Boulder_{i}",
                               (bx, by, bz + br * 0.45),
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
        # Small green tuft · per-tuft elevation
        tz = mesh_z(tx, ty)
        _make_box_local(f"OTPark_Tuft_{k}",
                        (tx, ty, tz + 0.18),
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
        fz = mesh_z(fx, fy)
        _make_box_local(f"OTPark_ExtraBed_{int(fx)}_{int(fy)}",
                        (fx, fy, fz + 0.16),
                        (1.4, 0.7, 0.22), COL_FLOWER_BED)
        _make_box_local(f"OTPark_ExtraFlowers_{int(fx)}_{int(fy)}",
                        (fx, fy, fz + 0.36),
                        (1.30, 0.65, 0.14), fcol)

    # ── NPCs · each samples ITS OWN terrain elevation per the
    # golden rule, so they stand on the actual ground (which now
    # varies across the park due to interior berms).
    npc_walker = (sx + 1.5, sy - outer_r - 14)
    human_figure(
        name="OTPark_NPC_Walker",
        base_x=npc_walker[0], base_y=npc_walker[1],
        base_z=mesh_z(*npc_walker),
        scale=1.0, facing='+Y',
        hair_style='short', hair_color=(0.42, 0.28, 0.20, 1.0),
        jacket_color=(0.38, 0.55, 0.68, 1.0),
        pants_color=(0.32, 0.32, 0.36, 1.0),
        shoe_color=(0.18, 0.18, 0.22, 1.0),
        with_ears=True, pose='arms_out',
    )
    npc_visitor1 = (sx - 11, sy + 9)
    human_figure(
        name="OTPark_NPC_Visitor1",
        base_x=npc_visitor1[0], base_y=npc_visitor1[1],
        base_z=mesh_z(*npc_visitor1),
        scale=1.0, facing='+X',
        hair_style='bowl', hair_color=(0.62, 0.42, 0.18, 1.0),
        jacket_color=(0.78, 0.32, 0.42, 1.0),
        pants_color=(0.30, 0.28, 0.32, 1.0),
        scarf_color=(0.86, 0.78, 0.55, 1.0),
        with_ears=True,
    )
    # Photographer on the TERRACE TOP — sits on terrace_top_z
    # (the real terrace top from mesh_z + 2 steps × 0.60 m).
    human_figure(
        name="OTPark_NPC_OnTerrace",
        base_x=sx - 2, base_y=sy + outer_r + 30 + 9,
        base_z=terrace_top_z,
        scale=1.0, facing='-Y',
        hair_style='short', hair_color=(0.18, 0.18, 0.22, 1.0),
        jacket_color=(0.32, 0.42, 0.32, 1.0),
        pants_color=(0.50, 0.45, 0.32, 1.0),
        shoe_color=(0.42, 0.30, 0.22, 1.0),
        has_sunglasses=True,
        sunglasses_color=(0.12, 0.12, 0.12, 1.0),
        with_ears=True,
    )
    npc_kid = (sx + 5, sy - 18)
    human_figure(
        name="OTPark_NPC_Kid",
        base_x=npc_kid[0], base_y=npc_kid[1],
        base_z=mesh_z(*npc_kid),
        scale=0.65,
        facing='+X',
        hair_style='short', hair_color=(0.72, 0.55, 0.22, 1.0),
        jacket_color=(0.95, 0.68, 0.30, 1.0),
        pants_color=(0.32, 0.42, 0.62, 1.0),
        shoe_color=(0.85, 0.20, 0.18, 1.0),
        with_ears=True,
    )

    # ════════════════════════════════════════════════════════
    # PARK BROCHURE PASS · refuge from the Texas heat.
    # Per user direction (2026-06-15): "make it comfortable and
    # lovely and human friendly, like it could go on the cover of
    # a promotional booklet for the planned community."
    # ════════════════════════════════════════════════════════

    # ── ROSE GARDEN · formal arrangement in the SE corner of
    # the park. Brick edging frames a grid of coloured bedding.
    rose_cx, rose_cy = sx + 18, sy - 14
    rose_ground = mesh_z(rose_cx, rose_cy)
    rose_w, rose_d = 12.0, 8.0
    # Brick edging — four narrow walls around the bed
    edge_brick = (0.55, 0.32, 0.26, 1.0)
    edge_t = 0.40
    edge_h = 0.40
    for (cx_off, cy_off, sx_e, sy_e) in [
        (0,             -rose_d / 2,  rose_w + edge_t, edge_t),  # south
        (0,              rose_d / 2,  rose_w + edge_t, edge_t),  # north
        (-rose_w / 2,    0,           edge_t,          rose_d),  # west
        ( rose_w / 2,    0,           edge_t,          rose_d),  # east
    ]:
        _make_box_local(f"OTPark_Rose_Edge_{cx_off:+.1f}_{cy_off:+.1f}",
                        (rose_cx + cx_off, rose_cy + cy_off,
                         rose_ground + edge_h / 2),
                        (sx_e, sy_e, edge_h), edge_brick)
    # Soil layer inside the edging — slightly darker brown
    _make_box_local("OTPark_Rose_Soil",
                    (rose_cx, rose_cy, rose_ground + 0.10),
                    (rose_w - 0.10, rose_d - 0.10, 0.20),
                    (0.32, 0.22, 0.16, 1.0))
    # Grid of rose bushes — 3 rows × 4 cols of small coloured spheres
    rose_colors = [
        (0.92, 0.20, 0.32, 1.0),    # crimson
        (0.95, 0.42, 0.62, 1.0),    # pink
        (0.92, 0.85, 0.30, 1.0),    # yellow
        (0.95, 0.70, 0.30, 1.0),    # apricot
        (0.94, 0.92, 0.86, 1.0),    # white
        (0.78, 0.50, 0.78, 1.0),    # lavender
    ]
    for row in range(3):
        for col in range(4):
            bx = rose_cx - rose_w / 2 + (rose_w / 5) * (col + 1)
            by = rose_cy - rose_d / 2 + (rose_d / 4) * (row + 1)
            cidx = (row * 4 + col) % len(rose_colors)
            # Stem
            _make_box_local(f"OTPark_Rose_Stem_{row}_{col}",
                            (bx, by, rose_ground + 0.40),
                            (0.05, 0.05, 0.40),
                            (0.32, 0.45, 0.22, 1.0))
            # Bloom
            _make_sphere_low_local(f"OTPark_Rose_Bloom_{row}_{col}",
                                    (bx, by, rose_ground + 0.70),
                                    0.18, rose_colors[cidx],
                                    rings=3, segments=6)
    # Brown wooden trellis sign at the rose garden's south entry
    _make_box_local("OTPark_Rose_Sign",
                    (rose_cx, rose_cy - rose_d / 2 - 1.2,
                     rose_ground + 1.0),
                    (1.4, 0.08, 0.60),
                    (0.40, 0.30, 0.20, 1.0))

    # ── TRELLIS ARCH over the south radial path · 3 arches at
    # 10 / 20 / 30 m along the path, vines suggested by green
    # bumps on the crossbar.
    for i, dist in enumerate((10.0, 20.0, 30.0)):
        trellis_y = sy - (outer_r + dist)
        trellis_ground = mesh_z(sx, trellis_y)
        post_h = 3.2
        # Two vertical posts flanking the 2.4 m wide path
        for tps in (-1.6, 1.6):
            _make_cyl_local(f"OTPark_Trellis_{i}_Post_{tps:+.1f}",
                            (sx + tps, trellis_y,
                             trellis_ground + post_h / 2),
                            0.06, post_h,
                            (0.42, 0.30, 0.20, 1.0), segments=4)
        # Horizontal beam
        _make_box_local(f"OTPark_Trellis_{i}_Beam",
                        (sx, trellis_y, trellis_ground + post_h + 0.06),
                        (3.6, 0.12, 0.12),
                        (0.42, 0.30, 0.20, 1.0))
        # Cross slats above
        for slat_off in (-0.4, 0, 0.4):
            _make_box_local(f"OTPark_Trellis_{i}_Slat_{slat_off:+.1f}",
                            (sx, trellis_y + slat_off,
                             trellis_ground + post_h + 0.18),
                            (3.6, 0.06, 0.06),
                            (0.42, 0.30, 0.20, 1.0))
        # Vine bumps · 5 small green spheres along the beam
        for v in range(5):
            vox = -1.4 + v * 0.7
            _make_sphere_low_local(f"OTPark_Trellis_{i}_Vine_{v}",
                                    (sx + vox, trellis_y - 0.05,
                                     trellis_ground + post_h + 0.10),
                                    0.18 + (v % 2) * 0.05,
                                    (0.32, 0.55, 0.22, 1.0),
                                    rings=3, segments=6)
        # A pink flower clump per arch
        _make_sphere_low_local(f"OTPark_Trellis_{i}_Flower",
                                (sx + 0.3, trellis_y - 0.05,
                                 trellis_ground + post_h + 0.10),
                                0.14, (0.95, 0.42, 0.62, 1.0),
                                rings=3, segments=6)

    # ── WATER RILL · linear water channel running from the
    # reflecting pool south-east to the rose garden. The
    # rectangular channel is concrete with a thin blue water
    # strip in the middle. Acoustic refuge feature — moving
    # water + cool surface.
    rill_start_x = pool_cx + pool_r + 0.5
    rill_start_y = pool_cy + 0.5
    rill_end_x = rose_cx - rose_w / 2 - 1.0
    rill_end_y = rose_cy + rose_d / 4
    rill_w = 0.8
    rill_concrete_w = 1.4
    # Concrete bed
    rill_mid_x = (rill_start_x + rill_end_x) / 2
    rill_mid_y = (rill_start_y + rill_end_y) / 2
    rill_ground = mesh_z(rill_mid_x, rill_mid_y)
    rill_len_x = abs(rill_end_x - rill_start_x)
    rill_len_y = abs(rill_end_y - rill_start_y)
    if rill_len_x > rill_len_y:
        rill_sx, rill_sy = rill_len_x + 1.0, rill_concrete_w
        water_sx, water_sy = rill_len_x + 0.2, rill_w
    else:
        rill_sx, rill_sy = rill_concrete_w, rill_len_y + 1.0
        water_sx, water_sy = rill_w, rill_len_y + 0.2
    _make_box_local("OTPark_Rill_Concrete",
                    (rill_mid_x, rill_mid_y, rill_ground - 0.10),
                    (rill_sx, rill_sy, 0.30),
                    COL_POOL_RIM)
    _make_box_local("OTPark_Rill_Water",
                    (rill_mid_x, rill_mid_y, rill_ground - 0.18),
                    (water_sx, water_sy, 0.10),
                    (0.30, 0.52, 0.62, 1.0))

    # ── PERGOLA · over the north radial path approaching the
    # terrace. Four wooden posts + cross beams + climbing-vine
    # accents. The "shaded approach to the contemplation gazebo."
    pergola_y = sy + outer_r + 10
    pergola_ground = mesh_z(sx, pergola_y)
    perg_post_h = 3.0
    for px_off in (-2.0, 2.0):
        for py_off in (-2.0, 2.0):
            _make_cyl_local(f"OTPark_Perg_Post_{px_off:+.1f}_{py_off:+.1f}",
                            (sx + px_off, pergola_y + py_off,
                             pergola_ground + perg_post_h / 2),
                            0.10, perg_post_h,
                            (0.42, 0.30, 0.20, 1.0), segments=6)
    # Top frame beams (2 long beams along E-W)
    for py_off in (-2.0, 2.0):
        _make_box_local(f"OTPark_Perg_Beam_{py_off:+.1f}",
                        (sx, pergola_y + py_off,
                         pergola_ground + perg_post_h + 0.08),
                        (4.4, 0.18, 0.16),
                        (0.42, 0.30, 0.20, 1.0))
    # Cross slats above — 7 thin runners
    for k in range(7):
        slat_x = sx - 1.6 + k * 0.53
        _make_box_local(f"OTPark_Perg_Slat_{k}",
                        (slat_x, pergola_y,
                         pergola_ground + perg_post_h + 0.22),
                        (0.08, 4.4, 0.08),
                        (0.42, 0.30, 0.20, 1.0))
    # Climbing vine clumps on the beam corners
    for vx in (-2.0, 2.0):
        for vy in (-2.0, 2.0):
            _make_sphere_low_local(f"OTPark_Perg_Vine_{vx:+.1f}_{vy:+.1f}",
                                    (sx + vx, pergola_y + vy,
                                     pergola_ground + perg_post_h + 0.15),
                                    0.30, (0.32, 0.55, 0.22, 1.0),
                                    rings=3, segments=6)

    # ── CONNECTOR WALKWAY · W radial end → Skatepark NE entry
    # The skatepark sits in the SW corner of the park with no marked
    # path leading to it. This adds a gravel walkway curving south
    # from the end of the West radial path to the skatepark plaza
    # edge, plus a small wooden direction signpost at the fork.
    # Each segment is a per-vertex mesh_z quad so it follows terrain.
    COL_GRAVEL = (0.62, 0.58, 0.50, 1.0)
    conn_w = 1.8
    conn_pts = [
        (sx - outer_r - 25, sy,           ),   # A · end of W radial
        (sx - outer_r - 30, sy - 15,      ),   # B · turn south
        (sx - outer_r - 32, sy - 25,      ),   # C · approach
        (sx - 20,           sy - 26,      ),   # D · NE skatepark entry (-280+...
    ]
    # NB: skatepark plaza is centred at (-280, 82); D above resolves
    # to roughly (-280, 94) — the NE edge of the plaza.
    hw = conn_w / 2
    for i in range(len(conn_pts) - 1):
        x0, y0 = conn_pts[i]
        x1, y1 = conn_pts[i + 1]
        # Perpendicular to segment direction in XY plane
        dxs = x1 - x0; dys = y1 - y0
        seg_len = math.hypot(dxs, dys) or 1.0
        perp_x = -dys / seg_len
        perp_y =  dxs / seg_len
        pv = []
        for (px, py) in [(x0 - perp_x * hw, y0 - perp_y * hw),
                         (x1 - perp_x * hw, y1 - perp_y * hw),
                         (x1 + perp_x * hw, y1 + perp_y * hw),
                         (x0 + perp_x * hw, y0 + perp_y * hw)]:
            pv.append((px, py, mesh_z(px, py) + 0.025))
        _finalize_mesh(f"OTPark_Skp_Connector_{i}", pv, [[0, 1, 2, 3]],
                       COL_GRAVEL)

    # Wooden signpost at the fork (point A) — short post + arrow plank
    sign_x, sign_y = conn_pts[0]
    sign_ground = mesh_z(sign_x, sign_y)
    COL_WOOD_POST = (0.42, 0.30, 0.20, 1.0)
    COL_WOOD_PLANK = (0.58, 0.42, 0.28, 1.0)
    _make_cyl_local("OTPark_Skp_SignPost",
                    (sign_x, sign_y, sign_ground + 1.2),
                    0.06, 2.4, COL_WOOD_POST, segments=6)
    # Arrow plank pointing SW toward the skatepark
    _make_box_local("OTPark_Skp_SignPlank",
                    (sign_x - 0.35, sign_y - 0.20, sign_ground + 2.1),
                    (1.0, 0.18, 0.04), COL_WOOD_PLANK)

    # ── Beacon at the park south entry · samples its own mesh_z
    beacon_x = sx
    beacon_y = sy - outer_r - 50
    beacon_ground = mesh_z(beacon_x, beacon_y)
    BEACON_H = 35.0
    _make_cyl_local("OT_Beacon_Pole",
                    (beacon_x, beacon_y, beacon_ground + BEACON_H / 2),
                    0.20, BEACON_H, (0.10, 0.10, 0.10, 1.0),
                    segments=4)
    _make_box_local("OT_Beacon_Top",
                    (beacon_x, beacon_y, beacon_ground + BEACON_H + 1.2),
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
    """Octagonal gazebo — 8 wooden posts holding up a peaked roof.
    Bumped from 6 to 8 sides per user feedback: "gazebo weirdness,
    looks like polygons." 8 sides + a lower-pitched pyramid reads
    smoother."""
    n_posts = 8
    # Floor — SOLID OCTAGONAL PRISM (foundation slab) so the gazebo
    # plinths visibly sit on the terrace instead of being a paper-
    # thin disc with daylight under it. Top at z_floor + 0.10, bottom
    # at z_floor - 0.20 → 30 cm thick stone foundation.
    foundation_color = (0.70, 0.66, 0.60, 1.0)   # stone, slightly darker than terrace
    foundation_top_z = z_floor + 0.10
    foundation_bot_z = z_floor - 0.20
    fverts = []
    # Top ring (indices 0..7)
    for i in range(n_posts):
        ang = 2.0 * math.pi * i / n_posts
        fverts.append((cx + math.cos(ang) * radius,
                       cy + math.sin(ang) * radius,
                       foundation_top_z))
    # Bottom ring (indices 8..15)
    for i in range(n_posts):
        ang = 2.0 * math.pi * i / n_posts
        fverts.append((cx + math.cos(ang) * radius,
                       cy + math.sin(ang) * radius,
                       foundation_bot_z))
    # Top centre (index 16) and bottom centre (index 17)
    fverts.append((cx, cy, foundation_top_z))
    fverts.append((cx, cy, foundation_bot_z))
    ffaces = []
    top_c = 16
    bot_c = 17
    for i in range(n_posts):
        ni = (i + 1) % n_posts
        # Top fan
        ffaces.append([top_c, i, ni])
        # Side quad
        ffaces.append([i, n_posts + i, n_posts + ni, ni])
        # Bottom fan (reversed winding)
        ffaces.append([bot_c, n_posts + ni, n_posts + i])
    _finalize_mesh(f"{name}_Foundation", fverts, ffaces, foundation_color)

    # Wooden floor surface on top of the foundation (decorative
    # plank layer just visible above the stone).
    verts = [(cx, cy, foundation_top_z + 0.02)]
    for i in range(n_posts):
        ang = 2.0 * math.pi * i / n_posts
        verts.append((cx + math.cos(ang) * (radius - 0.10),
                      cy + math.sin(ang) * (radius - 0.10),
                      foundation_top_z + 0.02))
    faces = []
    for i in range(n_posts):
        ni = (i + 1) % n_posts
        faces.append([0, 1 + i, 1 + ni])
    _finalize_mesh(f"{name}_Floor", verts, faces, floor_color)

    # Posts — bottom flush with the wooden floor surface (sit on
    # top of foundation), not floating.
    post_base_z = foundation_top_z + 0.02
    for i in range(n_posts):
        ang = 2.0 * math.pi * i / n_posts
        px = cx + math.cos(ang) * radius * 0.85
        py = cy + math.sin(ang) * radius * 0.85
        _make_box_local(f"{name}_Post_{i}",
                        (px, py, post_base_z + height / 2),
                        (0.20, 0.20, height), post_color)
    # Header beam ring connecting post tops — closes the visible
    # gap between the posts and the underside of the eave. Eight
    # horizontal beams, one between each pair of consecutive posts.
    beam_r = radius * 0.85
    beam_z = post_base_z + height - 0.10
    for i in range(n_posts):
        ang_a = 2.0 * math.pi * i / n_posts
        ang_b = 2.0 * math.pi * ((i + 1) % n_posts) / n_posts
        ax = cx + math.cos(ang_a) * beam_r
        ay = cy + math.sin(ang_a) * beam_r
        bx = cx + math.cos(ang_b) * beam_r
        by = cy + math.sin(ang_b) * beam_r
        mx = (ax + bx) / 2
        my = (ay + by) / 2
        beam_len = math.hypot(bx - ax, by - ay)
        beam_angle = math.atan2(by - ay, bx - ax)
        # Box rotated isn't trivial with _make_box_local; instead
        # build as a four-vert thin prism aligned with the segment.
        bw = 0.16   # beam thickness (perpendicular to span)
        bh = 0.25   # beam height
        perp_x = -math.sin(beam_angle) * bw / 2
        perp_y =  math.cos(beam_angle) * bw / 2
        bverts = []
        for sgn_top in (-1, 1):
            for (px, py) in [(ax - perp_x, ay - perp_y),
                              (bx - perp_x, by - perp_y),
                              (bx + perp_x, by + perp_y),
                              (ax + perp_x, ay + perp_y)]:
                bverts.append((px, py, beam_z + sgn_top * bh / 2))
        bfaces = [
            [0, 1, 2, 3],          # bottom
            [4, 7, 6, 5],          # top
            [0, 4, 5, 1],          # side
            [1, 5, 6, 2],          # side
            [2, 6, 7, 3],          # side
            [3, 7, 4, 0],          # side
        ]
        _finalize_mesh(f"{name}_HeaderBeam_{i}", bverts, bfaces, post_color)
    # Roof — TIERED dome anchored at the TOP of the header beams
    # (post_base_z + height) so the roof rests cleanly on the
    # structure instead of floating above it.
    roof_base_z = post_base_z + height
    overhang = 0.3
    lower_h = 0.5
    upper_h = 0.7
    mid_r = radius * 0.55
    apex_z = roof_base_z + lower_h + upper_h
    rverts = []
    for i in range(n_posts):
        ang = 2.0 * math.pi * i / n_posts
        rverts.append((cx + math.cos(ang) * (radius + overhang),
                       cy + math.sin(ang) * (radius + overhang),
                       roof_base_z))
    for i in range(n_posts):
        ang = 2.0 * math.pi * i / n_posts
        rverts.append((cx + math.cos(ang) * mid_r,
                       cy + math.sin(ang) * mid_r,
                       roof_base_z + lower_h))
    rverts.append((cx, cy, apex_z))
    apex_idx = len(rverts) - 1
    rfaces = []
    for i in range(n_posts):
        ni = (i + 1) % n_posts
        rfaces.append([i, ni, n_posts + ni, n_posts + i])
    for i in range(n_posts):
        ni = (i + 1) % n_posts
        rfaces.append([n_posts + i, n_posts + ni, apex_idx])
    _finalize_mesh(f"{name}_Roof", rverts, rfaces, roof_color)

    # SOFFIT · seals the gap between the post/header ring (radius)
    # and the roof's outer eave ring (radius + overhang) at
    # z = roof_base_z. Without this you can see daylight between
    # the post tops and the underside of the roof from outside.
    sverts = []
    for i in range(n_posts):
        ang = 2.0 * math.pi * i / n_posts
        sverts.append((cx + math.cos(ang) * radius,
                       cy + math.sin(ang) * radius,
                       roof_base_z - 0.01))
    for i in range(n_posts):
        ang = 2.0 * math.pi * i / n_posts
        sverts.append((cx + math.cos(ang) * (radius + overhang),
                       cy + math.sin(ang) * (radius + overhang),
                       roof_base_z - 0.01))
    sfaces = []
    for i in range(n_posts):
        ni = (i + 1) % n_posts
        sfaces.append([i, ni, n_posts + ni, n_posts + i])
    _finalize_mesh(f"{name}_Soffit", sverts, sfaces, post_color)


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
    pz = mesh_z(cx, cy)          # = ~-0.5 from settlement flat

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


def _build_convenience_store(name_prefix, cx, cy, ground_z,
                              brand="kwikstop"):
    """Box-shaped convenience store with a plate-glass STOREFRONT
    (the south wall is omitted so the interior is visible from
    outside) plus a modeled interior at world scale: aisles,
    counter, back cooler. Per _HCE_PROJECT_NOTES.md the convenience
    stores need plate-glass front walls with the interior visible
    from the public sidewalk.

    brand:
      "kwikstop" — red + cream palette, 'Kwik Stop' interior beats
      "nexcorp"  — blue + grey palette, 'NexCorp Gas & Go' beats
    """
    width = 12.0     # E-W
    depth = 10.0     # N-S (south face is plate glass)
    height = 3.6
    if brand == "nexcorp":
        col_wall   = (0.32, 0.42, 0.55, 1.0)
        col_trim   = (0.92, 0.92, 0.90, 1.0)
        col_roof   = (0.20, 0.22, 0.28, 1.0)
        col_sign   = (0.32, 0.55, 0.78, 1.0)
        col_floor  = (0.78, 0.76, 0.72, 1.0)
    else:
        col_wall   = (0.82, 0.78, 0.72, 1.0)
        col_trim   = (0.85, 0.22, 0.20, 1.0)
        col_roof   = (0.32, 0.18, 0.16, 1.0)
        col_sign   = (0.85, 0.22, 0.20, 1.0)
        col_floor  = (0.74, 0.72, 0.68, 1.0)
    col_glass_frame = (0.62, 0.62, 0.64, 1.0)
    col_shelf      = (0.50, 0.50, 0.52, 1.0)
    col_counter    = (0.42, 0.32, 0.22, 1.0)
    col_register   = (0.20, 0.20, 0.22, 1.0)
    col_cooler     = (0.78, 0.84, 0.88, 1.0)
    col_basket     = (0.60, 0.20, 0.18, 1.0)

    # Slab / floor — extends slightly past walls for a curb
    _make_box_local(f"{name_prefix}_Slab",
                    (cx, cy, ground_z + 0.05),
                    (width + 0.6, depth + 0.6, 0.10), col_floor)

    # Walls — north, east, west. NO south wall (plate glass).
    wall_t = 0.20
    # North (back wall, solid)
    _make_box_local(f"{name_prefix}_WallN",
                    (cx, cy + depth / 2 - wall_t / 2,
                     ground_z + height / 2),
                    (width, wall_t, height), col_wall)
    # East
    _make_box_local(f"{name_prefix}_WallE",
                    (cx + width / 2 - wall_t / 2, cy,
                     ground_z + height / 2),
                    (wall_t, depth, height), col_wall)
    # West
    _make_box_local(f"{name_prefix}_WallW",
                    (cx - width / 2 + wall_t / 2, cy,
                     ground_z + height / 2),
                    (wall_t, depth, height), col_wall)

    # Plate-glass storefront frame (south side) — vertical mullions
    # only; the panels themselves are open so the interior is
    # visible from outside, per project notes.
    glass_y = cy - depth / 2 + 0.05
    n_mullions = 5
    for k in range(n_mullions):
        mx = cx - width / 2 + 0.3 + k * (width - 0.6) / (n_mullions - 1)
        _make_box_local(f"{name_prefix}_GlassMullion_{k}",
                        (mx, glass_y, ground_z + height / 2),
                        (0.10, 0.06, height), col_glass_frame)
    # Top + bottom rails of the storefront
    _make_box_local(f"{name_prefix}_GlassTopRail",
                    (cx, glass_y, ground_z + height - 0.08),
                    (width - 0.2, 0.08, 0.16), col_glass_frame)
    _make_box_local(f"{name_prefix}_GlassBotRail",
                    (cx, glass_y, ground_z + 0.20),
                    (width - 0.2, 0.08, 0.40), col_glass_frame)

    # Entry door — frame outline on the right-most bay of the
    # storefront. Just the frame; the door itself is the gap in
    # the bottom rail. Gives the player a clear "I walk in here."
    door_w = 1.4
    door_h = 2.4
    door_cx = cx + width / 2 - 1.8
    # Vertical door jambs (slightly thicker than the mullions)
    for sgn in (-1, 1):
        _make_box_local(f"{name_prefix}_DoorJamb_{sgn:+d}",
                        (door_cx + sgn * door_w / 2, glass_y,
                         ground_z + door_h / 2),
                        (0.12, 0.10, door_h), col_trim)
    # Door header (above the door)
    _make_box_local(f"{name_prefix}_DoorHeader",
                    (door_cx, glass_y, ground_z + door_h + 0.08),
                    (door_w + 0.12, 0.10, 0.16), col_trim)
    # Push handle (vertical bar on the right jamb side)
    _make_cyl_local(f"{name_prefix}_DoorHandle",
                    (door_cx + 0.20, glass_y - 0.06,
                     ground_z + 1.10),
                    0.025, 0.40, col_glass_frame, segments=4)
    # Welcome mat just outside the door
    _make_box_local(f"{name_prefix}_DoorMat",
                    (door_cx, glass_y - 0.40,
                     ground_z + 0.07),
                    (door_w + 0.20, 0.80, 0.02),
                    (0.32, 0.22, 0.18, 1.0))

    # Roof
    _make_box_local(f"{name_prefix}_Roof",
                    (cx, cy, ground_z + height + 0.10),
                    (width + 0.4, depth + 0.4, 0.20), col_roof)
    # Parapet wall around the back & sides (front carries the sign)
    parapet_h = 0.45
    parapet_t = 0.18
    pz_top = ground_z + height + 0.20      # top of roof slab
    pz_centre = pz_top + parapet_h / 2
    # Back wall
    _make_box_local(f"{name_prefix}_ParapetN",
                    (cx, cy + (depth + 0.4) / 2 - parapet_t / 2,
                     pz_centre),
                    (width + 0.4, parapet_t, parapet_h),
                    col_wall)
    # Side walls
    for sgn in (-1, 1):
        _make_box_local(f"{name_prefix}_ParapetE_{sgn:+d}",
                        (cx + sgn * ((width + 0.4) / 2 - parapet_t / 2),
                         cy, pz_centre),
                        (parapet_t, depth + 0.4, parapet_h),
                        col_wall)
    # Two HVAC condenser units on the roof (offset toward the back)
    for k, ox in enumerate((-2.5, 2.5)):
        _make_box_local(f"{name_prefix}_HVAC_{k}",
                        (cx + ox, cy + depth * 0.20,
                         pz_top + 0.40),
                        (1.4, 1.2, 0.80),
                        (0.62, 0.62, 0.64, 1.0))
        # Fan grille on top (darker)
        _make_box_local(f"{name_prefix}_HVAC_{k}_Grille",
                        (cx + ox, cy + depth * 0.20,
                         pz_top + 0.83),
                        (1.0, 0.9, 0.06),
                        (0.28, 0.28, 0.30, 1.0))

    # Roof-mounted illuminated sign panel (faces south).
    # Pushed 30 cm south of the roof's south edge so the sign
    # sits clear of the roof slab (was straddling it, half buried
    # in the roof). Bottom of the sign rests level with the roof
    # top so the sign reads as "mounted on the roof's south edge."
    sign_w = width * 0.7
    sign_h = 0.9
    sign_y = cy - depth / 2 - 0.36
    _make_box_local(f"{name_prefix}_SignPanel",
                    (cx, sign_y,
                     ground_z + height + 0.20 + sign_h / 2),
                    (sign_w, 0.12, sign_h), col_sign)
    _make_box_local(f"{name_prefix}_SignTrim",
                    (cx, sign_y,
                     ground_z + height + 0.20 + sign_h + 0.05),
                    (sign_w + 0.10, 0.14, 0.10), col_trim)

    # ── INTERIOR ────────────────────────────────────────────────
    # Three aisles of shelving running N-S, set toward the back.
    # Length + position chosen so north end clears the new counter
    # at cy + 3.45 with 0.35 m of breathing room.
    aisle_h = 1.8
    aisle_l = 3.5
    aisle_y_centre = cy + 0.5
    for k, ax_off in enumerate((-3.0, 0.0, 3.0)):
        _make_box_local(f"{name_prefix}_Aisle_{k}",
                        (cx + ax_off, aisle_y_centre,
                         ground_z + aisle_h / 2),
                        (0.40, aisle_l, aisle_h), col_shelf)
        # Suggest products on top: thin coloured strip on each side
        for sgn in (-1, 1):
            _make_box_local(f"{name_prefix}_AisleGoods_{k}_{sgn:+d}",
                            (cx + ax_off + sgn * 0.24,
                             aisle_y_centre,
                             ground_z + aisle_h - 0.20),
                            (0.04, aisle_l - 0.4, 0.30),
                            (0.42, 0.65, 0.38, 1.0))

    # Counter at the BACK-LEFT (player walks in, counter on right)
    # Sized so there's a real walkable aisle (~1.2 m) between the
    # counter's NORTH edge and the back wall — clerk needs room.
    counter_w = 2.4
    counter_d = 0.7
    counter_h = 1.1
    counter_x = cx + width / 2 - counter_w / 2 - 0.5
    counter_y = cy + depth / 2 - counter_d / 2 - 1.2
    _make_box_local(f"{name_prefix}_Counter",
                    (counter_x, counter_y,
                     ground_z + counter_h / 2),
                    (counter_w, counter_d, counter_h), col_counter)
    # Cash register on counter — bottom flush with counter top.
    # Center z = counter_top + half register height.
    _make_box_local(f"{name_prefix}_Register",
                    (counter_x - 0.7, counter_y,
                     ground_z + counter_h + 0.15),
                    (0.55, 0.40, 0.30), col_register)
    # Cigarette/lotto rack behind the counter (vertical board)
    _make_box_local(f"{name_prefix}_BackBoard",
                    (counter_x, counter_y + counter_d / 2 + 0.05,
                     ground_z + 1.6),
                    (counter_w, 0.05, 1.4),
                    (0.32, 0.30, 0.28, 1.0))

    # Back cooler door (west wall, north end) — big glass-fronted cooler
    cooler_w = 2.4
    cooler_h = 2.4
    _make_box_local(f"{name_prefix}_Cooler",
                    (cx - width / 2 + cooler_w / 2 + 0.30,
                     cy + depth / 2 - 0.18,
                     ground_z + cooler_h / 2),
                    (cooler_w, 0.20, cooler_h), col_cooler)
    # Cooler shelf hint — a thin dark strip across the middle
    _make_box_local(f"{name_prefix}_CoolerShelf",
                    (cx - width / 2 + cooler_w / 2 + 0.30,
                     cy + depth / 2 - 0.10,
                     ground_z + cooler_h * 0.55),
                    (cooler_w - 0.10, 0.04, 0.05),
                    (0.32, 0.32, 0.32, 1.0))

    # Wire basket sitting near the entry (south-east of the
    # plate glass, just inside)
    _make_box_local(f"{name_prefix}_WireBasket",
                    (cx + 4.5, cy - depth / 2 + 1.2,
                     ground_z + 0.30),
                    (0.40, 0.30, 0.50), col_basket)


def _build_parked_car(name, cx, cy, ground_z, body_color,
                       facing='+Y'):
    """Low-poly parked car · body + cabin + four wheels. Facing
    parameter ('+Y' or '-Y') flips the cab forward end so cars
    parked nose-in look right.
    """
    car_l = 4.4
    car_w = 1.8
    body_h = 0.55
    cab_h = 0.70
    wheel_r = 0.32
    col_window = (0.18, 0.22, 0.30, 1.0)
    col_wheel  = (0.10, 0.10, 0.12, 1.0)
    # Body (lower box)
    _make_box_local(f"{name}_Body",
                    (cx, cy, ground_z + wheel_r + body_h / 2),
                    (car_w, car_l, body_h), body_color)
    # Cabin (smaller box on top, slightly toward "rear")
    cab_off = -0.35 if facing == '+Y' else 0.35
    _make_box_local(f"{name}_Cabin",
                    (cx, cy + cab_off,
                     ground_z + wheel_r + body_h + cab_h / 2),
                    (car_w - 0.16, car_l * 0.55, cab_h), body_color)
    # Window strip around the cabin (slightly inset, dark)
    _make_box_local(f"{name}_Windows",
                    (cx, cy + cab_off,
                     ground_z + wheel_r + body_h + cab_h * 0.65),
                    (car_w - 0.10, car_l * 0.55 - 0.10, cab_h * 0.45),
                    col_window)
    # Four wheels — boxes shaped like tires (thin along x, tall +
    # long enough to read as a wheel from the side). The cylinder
    # helper only does vertical-axis cylinders so a flat tire-
    # silhouette box is the cleanest substitute.
    tire_w = 0.22
    tire_d = wheel_r * 1.9         # diameter-ish along car length
    tire_h = wheel_r * 1.9
    for wx_sgn in (-1, 1):
        for wy_sgn, wy_off in ((-1, -car_l * 0.32), (1, car_l * 0.32)):
            _make_box_local(f"{name}_Wheel_{wx_sgn:+d}_{wy_sgn:+d}",
                            (cx + wx_sgn * (car_w / 2 - tire_w / 2 + 0.02),
                             cy + wy_off,
                             ground_z + tire_h / 2),
                            (tire_w, tire_d, tire_h),
                            col_wheel)
    # Headlights / taillights — small coloured boxes at the ends
    front_end = car_l / 2 if facing == '+Y' else -car_l / 2
    rear_end  = -car_l / 2 if facing == '+Y' else car_l / 2
    for sgn_x in (-1, 1):
        _make_box_local(f"{name}_Headlight_{sgn_x:+d}",
                        (cx + sgn_x * (car_w / 2 - 0.30),
                         cy + front_end,
                         ground_z + wheel_r + body_h * 0.6),
                        (0.30, 0.06, 0.20),
                        (0.98, 0.96, 0.86, 1.0))
        _make_box_local(f"{name}_Taillight_{sgn_x:+d}",
                        (cx + sgn_x * (car_w / 2 - 0.30),
                         cy + rear_end,
                         ground_z + wheel_r + body_h * 0.6),
                        (0.30, 0.06, 0.20),
                        (0.78, 0.18, 0.18, 1.0))


def _build_kwik_shop_strip(cx, cy, ground_z):
    """KWIK SHOP — 3-bay strip building combining the convenience
    store with an ARCADE and a LAUNDROMAT. Per user spec: "the qwik
    shop has an arcade and laundromat area, in addition to the
    convenience store."

    Layout: ARCADE (left, x-9) · KWIK STOP (centre) · LAUNDROMAT
    (right, x+9). 28 × 10 m total, single continuous roof, each
    bay has its own plate-glass front + entry door + interior.
    """
    name_prefix = "KwikShop"
    bay_w = 9.0
    total_w = 28.0
    depth = 10.0
    height = 3.6

    # Shared shell colours (red/cream Kwik palette throughout)
    col_wall  = (0.82, 0.78, 0.72, 1.0)
    col_trim  = (0.85, 0.22, 0.20, 1.0)
    col_roof  = (0.32, 0.18, 0.16, 1.0)
    col_floor = (0.74, 0.72, 0.68, 1.0)
    col_glass_frame = (0.62, 0.62, 0.64, 1.0)
    col_arcade_sign     = (0.62, 0.22, 0.78, 1.0)   # purple
    col_kwikstop_sign   = (0.85, 0.22, 0.20, 1.0)   # red
    col_laundromat_sign = (0.32, 0.55, 0.78, 1.0)   # blue

    # ── SHARED SHELL ────────────────────────────────────────────
    # Slab spanning full strip
    _make_box_local(f"{name_prefix}_Slab",
                    (cx, cy, ground_z + 0.05),
                    (total_w + 0.6, depth + 0.6, 0.10), col_floor)
    wall_t = 0.20
    # North (back) wall — solid across whole strip
    _make_box_local(f"{name_prefix}_WallN",
                    (cx, cy + depth / 2 - wall_t / 2,
                     ground_z + height / 2),
                    (total_w, wall_t, height), col_wall)
    # East + west exterior walls
    _make_box_local(f"{name_prefix}_WallE",
                    (cx + total_w / 2 - wall_t / 2, cy,
                     ground_z + height / 2),
                    (wall_t, depth, height), col_wall)
    _make_box_local(f"{name_prefix}_WallW",
                    (cx - total_w / 2 + wall_t / 2, cy,
                     ground_z + height / 2),
                    (wall_t, depth, height), col_wall)
    # Two interior partition walls between the three bays
    for sgn, tag_int in ((-1, "Arc_Kwik"), (1, "Kwik_Laun")):
        _make_box_local(f"{name_prefix}_PartWall_{tag_int}",
                        (cx + sgn * bay_w / 2, cy,
                         ground_z + height / 2),
                        (wall_t, depth, height), col_wall)
    # Single continuous roof + parapets
    _make_box_local(f"{name_prefix}_Roof",
                    (cx, cy, ground_z + height + 0.10),
                    (total_w + 0.4, depth + 0.4, 0.20), col_roof)
    parapet_h = 0.45
    parapet_t = 0.18
    pz_top = ground_z + height + 0.20
    pz_centre = pz_top + parapet_h / 2
    _make_box_local(f"{name_prefix}_ParapetN",
                    (cx, cy + (depth + 0.4) / 2 - parapet_t / 2,
                     pz_centre),
                    (total_w + 0.4, parapet_t, parapet_h), col_wall)
    for sgn in (-1, 1):
        _make_box_local(f"{name_prefix}_ParapetE_{sgn:+d}",
                        (cx + sgn * ((total_w + 0.4) / 2 - parapet_t / 2),
                         cy, pz_centre),
                        (parapet_t, depth + 0.4, parapet_h), col_wall)
    # HVAC units — one per bay
    for k_off, ox in enumerate((-9.0, 0.0, 9.0)):
        _make_box_local(f"{name_prefix}_HVAC_{k_off}",
                        (cx + ox, cy + depth * 0.20,
                         pz_top + 0.40),
                        (1.4, 1.2, 0.80),
                        (0.62, 0.62, 0.64, 1.0))
        _make_box_local(f"{name_prefix}_HVAC_{k_off}_Grille",
                        (cx + ox, cy + depth * 0.20,
                         pz_top + 0.83),
                        (1.0, 0.9, 0.06),
                        (0.28, 0.28, 0.30, 1.0))

    # ── PER-BAY STOREFRONT + INTERIOR ──────────────────────────
    bay_specs = [
        ("Arcade",      -9.0, col_arcade_sign,
            "ARCADE",       (0.95, 0.85, 0.30, 1.0)),
        ("KwikStop",     0.0, col_kwikstop_sign,
            "KWIK STOP",    (0.98, 0.95, 0.86, 1.0)),
        ("Laundromat",   9.0, col_laundromat_sign,
            "LAUNDROMAT",   (0.98, 0.98, 0.96, 1.0)),
    ]
    glass_y = cy - depth / 2 + 0.05
    for bay_tag, bay_ox, col_sign, sign_text, _txt_col in bay_specs:
        bcx = cx + bay_ox
        # Plate-glass storefront (mullions + rails) per bay
        n_mullions = 4
        for k in range(n_mullions):
            mx = bcx - bay_w / 2 + 0.3 + \
                 k * (bay_w - 0.6) / (n_mullions - 1)
            _make_box_local(f"{name_prefix}_{bay_tag}_GlassMul_{k}",
                            (mx, glass_y, ground_z + height / 2),
                            (0.10, 0.06, height), col_glass_frame)
        _make_box_local(f"{name_prefix}_{bay_tag}_GlassTopRail",
                        (bcx, glass_y, ground_z + height - 0.08),
                        (bay_w - 0.2, 0.08, 0.16), col_glass_frame)
        _make_box_local(f"{name_prefix}_{bay_tag}_GlassBotRail",
                        (bcx, glass_y, ground_z + 0.20),
                        (bay_w - 0.2, 0.08, 0.40), col_glass_frame)
        # Entry door (centred in each bay)
        door_w = 1.2; door_h = 2.4
        for sgn in (-1, 1):
            _make_box_local(
                f"{name_prefix}_{bay_tag}_DoorJamb_{sgn:+d}",
                (bcx + sgn * door_w / 2, glass_y,
                 ground_z + door_h / 2),
                (0.12, 0.10, door_h), col_trim)
        _make_box_local(f"{name_prefix}_{bay_tag}_DoorHeader",
                        (bcx, glass_y,
                         ground_z + door_h + 0.08),
                        (door_w + 0.12, 0.10, 0.16), col_trim)
        _make_cyl_local(f"{name_prefix}_{bay_tag}_DoorHandle",
                        (bcx + 0.20, glass_y - 0.06,
                         ground_z + 1.10),
                        0.025, 0.40, col_glass_frame, segments=4)
        _make_box_local(f"{name_prefix}_{bay_tag}_DoorMat",
                        (bcx, glass_y - 0.40,
                         ground_z + 0.07),
                        (door_w + 0.20, 0.80, 0.02),
                        (0.32, 0.22, 0.18, 1.0))
        # Per-bay roof sign
        sign_h_local = 0.8
        sign_y = cy - depth / 2 - 0.36
        _make_box_local(f"{name_prefix}_{bay_tag}_SignPanel",
                        (bcx, sign_y,
                         ground_z + height + 0.20 + sign_h_local / 2),
                        (bay_w * 0.85, 0.12, sign_h_local), col_sign)
        _make_box_local(f"{name_prefix}_{bay_tag}_SignTrim",
                        (bcx, sign_y,
                         ground_z + height + 0.20 + sign_h_local + 0.05),
                        (bay_w * 0.85 + 0.10, 0.14, 0.10), col_trim)

    # ── BAY-SPECIFIC INTERIORS ─────────────────────────────────
    # ARCADE bay — 4 standing arcade cabinets in a row near back
    arc_cx = cx - 9.0
    COL_CAB_BODY = (0.18, 0.18, 0.22, 1.0)
    COL_CAB_SCREEN = (0.32, 0.55, 0.78, 1.0)
    COL_CAB_MARQUEE = (0.95, 0.42, 0.30, 1.0)
    for k in range(4):
        kx = arc_cx - 3.0 + k * 2.0
        ky = cy + depth * 0.20
        # Cabinet body
        _make_box_local(f"KwikShop_Arc_Cab_{k}",
                        (kx, ky, ground_z + 0.85),
                        (0.80, 0.70, 1.70), COL_CAB_BODY)
        # Screen
        _make_box_local(f"KwikShop_Arc_Screen_{k}",
                        (kx, ky - 0.36, ground_z + 1.30),
                        (0.55, 0.04, 0.40), COL_CAB_SCREEN)
        # Marquee
        _make_box_local(f"KwikShop_Arc_Marquee_{k}",
                        (kx, ky - 0.36, ground_z + 1.85),
                        (0.70, 0.04, 0.20), COL_CAB_MARQUEE)
        # Control panel slab
        _make_box_local(f"KwikShop_Arc_Panel_{k}",
                        (kx, ky - 0.42, ground_z + 0.95),
                        (0.55, 0.18, 0.06), COL_CAB_BODY)
    # Change machine on west wall
    _make_box_local("KwikShop_Arc_ChangeMachine",
                    (arc_cx - 4.1, cy + 0.5, ground_z + 0.80),
                    (0.30, 0.40, 1.20),
                    (0.42, 0.42, 0.45, 1.0))

    # KWIK STOP bay — aisles + counter + cooler + basket (matches
    # the previous convenience-store interior)
    kw_cx = cx
    col_shelf      = (0.50, 0.50, 0.52, 1.0)
    col_counter    = (0.42, 0.32, 0.22, 1.0)
    col_register   = (0.20, 0.20, 0.22, 1.0)
    col_cooler     = (0.78, 0.84, 0.88, 1.0)
    col_basket     = (0.60, 0.20, 0.18, 1.0)
    # Aisle length shortened so the north end clears the counter
    # (counter sits at cy + 3.45 ± 0.35 = cy + 3.1 to cy + 3.8;
    # aisles now end at cy + 2.75 with 0.35 m of breathing room).
    aisle_h = 1.8
    aisle_l = 3.5
    aisle_y_centre = cy + 0.5
    for k, ax_off in enumerate((-2.0, 0.0, 2.0)):
        _make_box_local(f"KwikShop_KwikStop_Aisle_{k}",
                        (kw_cx + ax_off, aisle_y_centre,
                         ground_z + aisle_h / 2),
                        (0.40, aisle_l, aisle_h), col_shelf)
        for sgn in (-1, 1):
            _make_box_local(
                f"KwikShop_KwikStop_AisleGoods_{k}_{sgn:+d}",
                (kw_cx + ax_off + sgn * 0.24,
                 aisle_y_centre,
                 ground_z + aisle_h - 0.20),
                (0.04, aisle_l - 0.4, 0.30),
                (0.42, 0.65, 0.38, 1.0))
    # Counter sized + positioned so there's a real walkable
    # aisle (~1.0 m) between its NORTH edge and the back wall —
    # the clerk needs to stand somewhere.
    counter_w = 1.8; counter_d = 0.7; counter_h = 1.1
    counter_x = kw_cx + bay_w / 2 - counter_w / 2 - 0.5
    counter_y = cy + depth / 2 - counter_d / 2 - 1.2
    _make_box_local("KwikShop_KwikStop_Counter",
                    (counter_x, counter_y,
                     ground_z + counter_h / 2),
                    (counter_w, counter_d, counter_h), col_counter)
    _make_box_local("KwikShop_KwikStop_Register",
                    (counter_x - 0.6, counter_y,
                     ground_z + counter_h + 0.15),
                    (0.55, 0.40, 0.30), col_register)
    _make_box_local("KwikShop_KwikStop_BackBoard",
                    (counter_x, counter_y + counter_d / 2 + 0.05,
                     ground_z + 1.6),
                    (counter_w, 0.05, 1.4),
                    (0.32, 0.30, 0.28, 1.0))
    # Cooler against the partition wall to the west (next to arcade)
    cooler_w = 2.0; cooler_h = 2.4
    _make_box_local("KwikShop_KwikStop_Cooler",
                    (kw_cx - bay_w / 2 + cooler_w / 2 + 0.30,
                     cy + depth / 2 - 0.18,
                     ground_z + cooler_h / 2),
                    (cooler_w, 0.20, cooler_h), col_cooler)
    _make_box_local("KwikShop_KwikStop_CoolerShelf",
                    (kw_cx - bay_w / 2 + cooler_w / 2 + 0.30,
                     cy + depth / 2 - 0.10,
                     ground_z + cooler_h * 0.55),
                    (cooler_w - 0.10, 0.04, 0.05),
                    (0.32, 0.32, 0.32, 1.0))
    _make_box_local("KwikShop_KwikStop_WireBasket",
                    (kw_cx + 3.0, cy - depth / 2 + 1.2,
                     ground_z + 0.30),
                    (0.40, 0.30, 0.50), col_basket)

    # LAUNDROMAT bay — row of washing machines + dryers + folding
    # table. Two rows: 5 washers on the south side, 5 dryers on
    # the north side. Folding table down the middle.
    ldr_cx = cx + 9.0
    COL_WASHER_BODY = (0.92, 0.92, 0.90, 1.0)
    COL_WASHER_PORT = (0.32, 0.32, 0.36, 1.0)
    COL_WASHER_TRIM = (0.62, 0.62, 0.64, 1.0)
    COL_FOLDING = (0.62, 0.55, 0.45, 1.0)
    # 5 front-loaders along the back (north) wall — wy chosen so
    # the washer's NORTH face (wy + 0.35) clears the back wall
    # interior at cy + 4.8 by 0.15 m.
    for k in range(5):
        wx = ldr_cx - 3.2 + k * 1.6
        wy = cy + depth / 2 - 0.7      # was -0.5, washer clipped wall
        _make_box_local(f"KwikShop_Ldr_Washer_{k}_Body",
                        (wx, wy, ground_z + 0.55),
                        (1.20, 0.70, 1.10), COL_WASHER_BODY)
        # Round porthole — approximated as a dark square
        _make_box_local(f"KwikShop_Ldr_Washer_{k}_Port",
                        (wx, wy - 0.36, ground_z + 0.65),
                        (0.45, 0.04, 0.45), COL_WASHER_PORT)
        # Trim panel above
        _make_box_local(f"KwikShop_Ldr_Washer_{k}_Trim",
                        (wx, wy - 0.36, ground_z + 1.02),
                        (1.0, 0.04, 0.18), COL_WASHER_TRIM)
    # 4 stacked dryers against the EAST partition (back-to-back)
    for k in range(4):
        dy_pos = cy - 0.5 + k * 0.5     # not used, replaced below
        wx = ldr_cx + bay_w / 2 - 0.55
        wy = cy + depth * 0.15 - k * 0.9 + 1.5
        for stack in (0, 1):
            _make_box_local(f"KwikShop_Ldr_Dryer_{k}_{stack}_Body",
                            (wx, wy,
                             ground_z + 0.55 + stack * 1.10),
                            (0.90, 0.70, 1.10), COL_WASHER_BODY)
            _make_box_local(f"KwikShop_Ldr_Dryer_{k}_{stack}_Port",
                            (wx - 0.36, wy,
                             ground_z + 0.65 + stack * 1.10),
                            (0.04, 0.45, 0.45), COL_WASHER_PORT)
    # Folding table in the middle of the bay
    _make_box_local("KwikShop_Ldr_FoldingTable",
                    (ldr_cx - 1.0, cy - 0.5, ground_z + 0.85),
                    (3.0, 0.80, 0.06), COL_FOLDING)
    for tx in (ldr_cx - 2.3, ldr_cx + 0.3):
        for ty in (cy - 0.9, cy - 0.1):
            _make_box_local(
                f"KwikShop_Ldr_FoldTableLeg_{int(tx)}_{int(ty)}",
                (tx, ty, ground_z + 0.42),
                (0.06, 0.06, 0.84), COL_WASHER_TRIM)
    # Coin/change machine on west partition
    _make_box_local("KwikShop_Ldr_ChangeMachine",
                    (ldr_cx - bay_w / 2 + 0.40, cy + 0.5,
                     ground_z + 0.80),
                    (0.30, 0.40, 1.20),
                    (0.42, 0.42, 0.45, 1.0))


def _build_diner(cx, cy, ground_z):
    """Chapter-one DINER — classic chrome+red roadside diner. Long
    thin building with a curved-corner silhouette suggested by a
    central rectangle plus side caps. Plate-glass front facing
    south, neon-style sign panel above.
    """
    name_prefix = "Diner"
    width = 18.0
    depth = 9.0
    height = 3.4
    col_wall   = (0.92, 0.90, 0.88, 1.0)         # cream / cream-aluminium
    col_red_band = (0.85, 0.22, 0.20, 1.0)
    col_roof   = (0.22, 0.20, 0.22, 1.0)
    col_trim   = (0.62, 0.62, 0.64, 1.0)         # chrome
    col_floor  = (0.55, 0.50, 0.46, 1.0)         # checker-ish
    col_glass_frame = (0.62, 0.62, 0.64, 1.0)
    col_sign   = (0.95, 0.42, 0.30, 1.0)
    col_counter = (0.62, 0.55, 0.45, 1.0)
    col_stool  = (0.85, 0.22, 0.20, 1.0)
    col_booth  = (0.85, 0.22, 0.20, 1.0)
    col_table  = (0.78, 0.74, 0.66, 1.0)

    # Slab
    _make_box_local(f"{name_prefix}_Slab",
                    (cx, cy, ground_z + 0.05),
                    (width + 0.6, depth + 0.6, 0.10), col_floor)
    wall_t = 0.20
    # Back wall
    _make_box_local(f"{name_prefix}_WallN",
                    (cx, cy + depth / 2 - wall_t / 2,
                     ground_z + height / 2),
                    (width, wall_t, height), col_wall)
    # Side walls
    _make_box_local(f"{name_prefix}_WallE",
                    (cx + width / 2 - wall_t / 2, cy,
                     ground_z + height / 2),
                    (wall_t, depth, height), col_wall)
    _make_box_local(f"{name_prefix}_WallW",
                    (cx - width / 2 + wall_t / 2, cy,
                     ground_z + height / 2),
                    (wall_t, depth, height), col_wall)
    # Plate-glass front spanning full width
    glass_y = cy - depth / 2 + 0.05
    n_mullions = 7
    for k in range(n_mullions):
        mx = cx - width / 2 + 0.4 + k * (width - 0.8) / (n_mullions - 1)
        _make_box_local(f"{name_prefix}_GlassMul_{k}",
                        (mx, glass_y, ground_z + height / 2),
                        (0.10, 0.06, height), col_glass_frame)
    _make_box_local(f"{name_prefix}_GlassTopRail",
                    (cx, glass_y, ground_z + height - 0.08),
                    (width - 0.2, 0.08, 0.16), col_glass_frame)
    _make_box_local(f"{name_prefix}_GlassBotRail",
                    (cx, glass_y, ground_z + 0.20),
                    (width - 0.2, 0.08, 0.40), col_glass_frame)
    # Red horizontal band at mid-wall height — diner signature
    _make_box_local(f"{name_prefix}_RedBand_N",
                    (cx, cy + depth / 2 - wall_t / 2 - 0.05,
                     ground_z + height * 0.55),
                    (width, 0.10, 0.30), col_red_band)
    # Entry door (centred)
    door_w = 1.4; door_h = 2.4
    for sgn in (-1, 1):
        _make_box_local(f"{name_prefix}_DoorJamb_{sgn:+d}",
                        (cx + sgn * door_w / 2, glass_y,
                         ground_z + door_h / 2),
                        (0.12, 0.10, door_h), col_trim)
    _make_box_local(f"{name_prefix}_DoorHeader",
                    (cx, glass_y, ground_z + door_h + 0.08),
                    (door_w + 0.12, 0.10, 0.16), col_trim)
    _make_box_local(f"{name_prefix}_DoorMat",
                    (cx, glass_y - 0.40, ground_z + 0.07),
                    (door_w + 0.20, 0.80, 0.02),
                    (0.32, 0.22, 0.18, 1.0))
    # Roof — slightly curved suggestion with a thicker band on top
    _make_box_local(f"{name_prefix}_Roof",
                    (cx, cy, ground_z + height + 0.12),
                    (width + 0.4, depth + 0.4, 0.24), col_roof)
    # Sign panel ON the front parapet — diner signs are typically
    # neon mounted ABOVE the door.
    sign_h_local = 1.0
    sign_y = cy - depth / 2 - 0.36
    _make_box_local(f"{name_prefix}_SignPanel",
                    (cx, sign_y,
                     ground_z + height + 0.24 + sign_h_local / 2),
                    (width * 0.6, 0.14, sign_h_local), col_sign)
    _make_box_local(f"{name_prefix}_SignTrim",
                    (cx, sign_y,
                     ground_z + height + 0.24 + sign_h_local + 0.05),
                    (width * 0.6 + 0.20, 0.16, 0.10), col_trim)

    # ── INTERIOR · counter with stools + 4 booths along the
    # storefront + kitchen at the back
    counter_w = 10.0; counter_d = 0.9; counter_h = 1.05
    _make_box_local(f"{name_prefix}_Counter",
                    (cx, cy + depth * 0.18,
                     ground_z + counter_h / 2),
                    (counter_w, counter_d, counter_h), col_counter)
    # Countertop dressings — alternating plates, ketchup bottle,
    # salt + pepper shakers, coffee mug, napkin holder. Spaced
    # along the counter so each stool gets some clutter in front
    # of it.
    counter_top_z = ground_z + counter_h + 0.04
    counter_top_y = cy + depth * 0.18 - 0.20      # toward customer side
    for k in range(5):
        px = cx - counter_w * 0.4 + k * counter_w * 0.2
        if k % 2 == 0:
            # Plate + ketchup bottle pair
            _make_cyl_local(f"{name_prefix}_Top_Plate_{k}",
                            (px, counter_top_y, counter_top_z),
                            0.13, 0.02,
                            (0.95, 0.95, 0.92, 1.0), segments=8)
            _make_cyl_local(f"{name_prefix}_Top_Ketchup_{k}",
                            (px + 0.18, counter_top_y, counter_top_z + 0.10),
                            0.04, 0.20,
                            (0.78, 0.18, 0.18, 1.0), segments=8)
        else:
            # Coffee mug + salt + pepper pair
            _make_cyl_local(f"{name_prefix}_Top_Mug_{k}",
                            (px, counter_top_y, counter_top_z + 0.04),
                            0.05, 0.08,
                            (0.92, 0.90, 0.84, 1.0), segments=8)
            for sgn, col in ((-1, (0.95, 0.95, 0.92, 1.0)),
                              (1, (0.30, 0.28, 0.26, 1.0))):
                _make_cyl_local(
                    f"{name_prefix}_Top_Shaker_{k}_{sgn:+d}",
                    (px + 0.20 + sgn * 0.05, counter_top_y, counter_top_z + 0.05),
                    0.025, 0.10, col, segments=6)
    # Napkin holder at the centre (between stools)
    _make_box_local(f"{name_prefix}_Top_NapkinHolder",
                    (cx, counter_top_y - 0.10, counter_top_z + 0.06),
                    (0.10, 0.12, 0.12),
                    (0.62, 0.62, 0.64, 1.0))

    # 5 stools in front of the counter
    for k in range(5):
        sx = cx - counter_w * 0.4 + k * counter_w * 0.2
        sy = cy + depth * 0.18 - counter_d / 2 - 0.6
        _make_cyl_local(f"{name_prefix}_Stool_{k}_Seat",
                        (sx, sy, ground_z + 0.65),
                        0.20, 0.08, col_stool, segments=8)
        _make_cyl_local(f"{name_prefix}_Stool_{k}_Stem",
                        (sx, sy, ground_z + 0.30),
                        0.04, 0.55,
                        (0.62, 0.62, 0.64, 1.0), segments=4)
    # 4 booths along the south (window) wall
    for k in range(4):
        bx = cx - width * 0.32 + k * width * 0.22
        by = cy - depth / 2 + 1.4
        # Bench seat
        _make_box_local(f"{name_prefix}_BoothSeat_{k}_L",
                        (bx, by - 0.6, ground_z + 0.40),
                        (1.0, 0.40, 0.10), col_booth)
        _make_box_local(f"{name_prefix}_BoothSeat_{k}_R",
                        (bx, by + 0.6, ground_z + 0.40),
                        (1.0, 0.40, 0.10), col_booth)
        # Bench backs
        _make_box_local(f"{name_prefix}_BoothBack_{k}_L",
                        (bx, by - 0.78, ground_z + 0.80),
                        (1.0, 0.06, 0.70), col_booth)
        _make_box_local(f"{name_prefix}_BoothBack_{k}_R",
                        (bx, by + 0.78, ground_z + 0.80),
                        (1.0, 0.06, 0.70), col_booth)
        # Table
        _make_box_local(f"{name_prefix}_BoothTable_{k}",
                        (bx, by, ground_z + 0.55),
                        (0.80, 0.80, 0.06), col_table)
        _make_box_local(f"{name_prefix}_BoothTable_{k}_Leg",
                        (bx, by, ground_z + 0.27),
                        (0.10, 0.10, 0.54),
                        (0.62, 0.62, 0.64, 1.0))
    # Kitchen pass-through / half-wall — pushed south to cy + 3.0
    # so the kitchen aisle between this wall and the prep counter
    # (at cy + 3.70 south edge) is a real 0.7 m wide aisle, room
    # for the cook to stand.
    _make_box_local(f"{name_prefix}_KitchenWall",
                    (cx, cy + 3.0, ground_z + 1.30),
                    (12.0, 0.20, 0.60), col_trim)
    # Prep counter running along the back, behind (north of) the
    # pass-through half-wall. Counter centre at cy + 4.0 so its
    # 0.60 m depth spans cy + 3.70 to cy + 4.30 — north edge
    # touches the back wall interior at cy + 4.30 (no clip).
    kitchen_y = cy + 3.6     # pass-through wall sits a bit south
    _make_box_local(f"{name_prefix}_Kitchen_PrepCounter",
                    (cx - 3.0, kitchen_y + 0.40,
                     ground_z + 0.50),
                    (4.0, 0.60, 1.00),
                    (0.78, 0.78, 0.80, 1.0))           # steel
    # Flat-top grill (raised dark surface, sits on the prep counter)
    _make_box_local(f"{name_prefix}_Kitchen_Grill",
                    (cx - 3.0, kitchen_y + 0.40,
                     ground_z + 1.06),
                    (3.6, 0.50, 0.12),
                    (0.18, 0.18, 0.20, 1.0))
    # Burner ticks on the grill (small darker rectangles)
    for k in range(3):
        gx = cx - 3.0 - 1.0 + k * 1.0
        _make_box_local(f"{name_prefix}_Kitchen_Burner_{k}",
                        (gx, kitchen_y + 0.40, ground_z + 1.13),
                        (0.40, 0.10, 0.02),
                        (0.62, 0.18, 0.16, 1.0))      # warm red glow
    # Extractor hood overhead — depth matched to the prep counter
    # so it doesn't clip through the back wall.
    _make_box_local(f"{name_prefix}_Kitchen_Hood",
                    (cx - 3.0, kitchen_y + 0.40,
                     ground_z + 2.50),
                    (4.2, 0.60, 0.50),
                    (0.32, 0.32, 0.34, 1.0))
    # Drink/fridge unit on the east side of the kitchen
    _make_box_local(f"{name_prefix}_Kitchen_Fridge",
                    (cx + 3.0, kitchen_y + 0.20,
                     ground_z + 0.95),
                    (1.20, 0.70, 1.90),
                    (0.85, 0.85, 0.82, 1.0))
    # Hanging shelf / utensil bar above the prep counter
    _make_box_local(f"{name_prefix}_Kitchen_Utensil_Bar",
                    (cx - 3.0, kitchen_y - 0.05,
                     ground_z + 2.10),
                    (3.0, 0.04, 0.06),
                    (0.62, 0.62, 0.64, 1.0))
    # JUKEBOX in the SE corner — colourful arc-top body so it
    # reads as a Wurlitzer-style 50s jukebox from the sidewalk.
    juke_x = cx + width / 2 - 0.8
    juke_y = cy + depth * 0.05
    _make_box_local(f"{name_prefix}_Jukebox_Body",
                    (juke_x, juke_y, ground_z + 0.70),
                    (0.70, 0.55, 1.40),
                    (0.62, 0.18, 0.62, 1.0))           # magenta body
    _make_box_local(f"{name_prefix}_Jukebox_Dome",
                    (juke_x, juke_y, ground_z + 1.55),
                    (0.70, 0.55, 0.30),
                    (0.95, 0.85, 0.30, 1.0))           # gold dome cap
    _make_box_local(f"{name_prefix}_Jukebox_Window",
                    (juke_x, juke_y - 0.28, ground_z + 1.10),
                    (0.50, 0.04, 0.50),
                    (0.18, 0.22, 0.30, 1.0))           # dark display
    # COFFEE STATION on the back counter / staff aisle. Two
    # carafes + a brewer body. Tells the player coffee's a thing
    # here even from outside.
    coffee_x = cx - width / 2 + 1.4
    coffee_y = cy + depth * 0.25
    _make_box_local(f"{name_prefix}_Coffee_Brewer",
                    (coffee_x, coffee_y, ground_z + 1.40),
                    (0.45, 0.40, 0.50),
                    (0.42, 0.42, 0.45, 1.0))           # steel brewer
    for k, (col_pot, ox) in enumerate((((0.20, 0.18, 0.16, 1.0), -0.20),
                                         ((0.80, 0.32, 0.22, 1.0), 0.20))):
        _make_cyl_local(f"{name_prefix}_Coffee_Pot_{k}",
                        (coffee_x + ox, coffee_y,
                         ground_z + 1.15),
                        0.07, 0.20, col_pot, segments=8)
    # CLOCK on the back wall — round wall clock
    _make_cyl_local(f"{name_prefix}_Clock",
                    (cx, cy + depth / 2 - 0.21, ground_z + 2.50),
                    0.30, 0.05,
                    (0.92, 0.90, 0.88, 1.0), segments=12)
    _make_box_local(f"{name_prefix}_Clock_HandH",
                    (cx, cy + depth / 2 - 0.18, ground_z + 2.55),
                    (0.02, 0.02, 0.18),
                    (0.10, 0.10, 0.10, 1.0))
    _make_box_local(f"{name_prefix}_Clock_HandM",
                    (cx + 0.10, cy + depth / 2 - 0.18, ground_z + 2.45),
                    (0.22, 0.02, 0.02),
                    (0.10, 0.10, 0.10, 1.0))


def _build_cosmic_comics(cx, cy, ground_z):
    """Cosmic Comics — chapter-one comic shop with a plate-glass
    front and a CANONICALLY visible photocopier inside (per
    _HCE_PROJECT_NOTES.md). Smaller than the convenience stores
    (9 × 8 m); tighter, more shop-like."""
    name_prefix = "CosmicComics"
    width = 9.0
    depth = 8.0
    height = 3.2
    col_wall  = (0.32, 0.18, 0.32, 1.0)        # plum/purple
    col_roof  = (0.18, 0.10, 0.18, 1.0)
    col_trim  = (0.95, 0.85, 0.30, 1.0)        # gold
    col_sign  = (0.32, 0.18, 0.32, 1.0)
    col_floor = (0.55, 0.32, 0.22, 1.0)        # warm wood floor
    col_glass_frame = (0.62, 0.62, 0.64, 1.0)
    col_shelf = (0.42, 0.30, 0.20, 1.0)
    col_counter = (0.42, 0.30, 0.20, 1.0)
    col_xerox_body = (0.86, 0.86, 0.88, 1.0)   # iconic copier beige
    col_xerox_top  = (0.32, 0.32, 0.32, 1.0)
    col_xerox_panel = (0.18, 0.18, 0.22, 1.0)
    col_books = (0.95, 0.62, 0.20, 1.0)

    # Slab
    _make_box_local(f"{name_prefix}_Slab",
                    (cx, cy, ground_z + 0.05),
                    (width + 0.6, depth + 0.6, 0.10), col_floor)
    wall_t = 0.20
    _make_box_local(f"{name_prefix}_WallN",
                    (cx, cy + depth / 2 - wall_t / 2,
                     ground_z + height / 2),
                    (width, wall_t, height), col_wall)
    _make_box_local(f"{name_prefix}_WallE",
                    (cx + width / 2 - wall_t / 2, cy,
                     ground_z + height / 2),
                    (wall_t, depth, height), col_wall)
    _make_box_local(f"{name_prefix}_WallW",
                    (cx - width / 2 + wall_t / 2, cy,
                     ground_z + height / 2),
                    (wall_t, depth, height), col_wall)
    # Plate-glass front (south)
    glass_y = cy - depth / 2 + 0.05
    n_mullions = 4
    for k in range(n_mullions):
        mx = cx - width / 2 + 0.3 + k * (width - 0.6) / (n_mullions - 1)
        _make_box_local(f"{name_prefix}_GlassMullion_{k}",
                        (mx, glass_y, ground_z + height / 2),
                        (0.10, 0.06, height), col_glass_frame)
    _make_box_local(f"{name_prefix}_GlassTopRail",
                    (cx, glass_y, ground_z + height - 0.08),
                    (width - 0.2, 0.08, 0.16), col_glass_frame)
    _make_box_local(f"{name_prefix}_GlassBotRail",
                    (cx, glass_y, ground_z + 0.20),
                    (width - 0.2, 0.08, 0.40), col_glass_frame)
    # Entry door (centred)
    door_w = 1.2
    door_h = 2.2
    door_cx = cx
    for sgn in (-1, 1):
        _make_box_local(f"{name_prefix}_DoorJamb_{sgn:+d}",
                        (door_cx + sgn * door_w / 2, glass_y,
                         ground_z + door_h / 2),
                        (0.12, 0.10, door_h), col_trim)
    _make_box_local(f"{name_prefix}_DoorHeader",
                    (door_cx, glass_y, ground_z + door_h + 0.08),
                    (door_w + 0.12, 0.10, 0.16), col_trim)
    _make_cyl_local(f"{name_prefix}_DoorHandle",
                    (door_cx + 0.18, glass_y - 0.06,
                     ground_z + 1.10),
                    0.025, 0.40, col_glass_frame, segments=4)
    _make_box_local(f"{name_prefix}_DoorMat",
                    (door_cx, glass_y - 0.40,
                     ground_z + 0.07),
                    (door_w + 0.20, 0.80, 0.02),
                    (0.32, 0.22, 0.18, 1.0))
    # Roof
    _make_box_local(f"{name_prefix}_Roof",
                    (cx, cy, ground_z + height + 0.10),
                    (width + 0.4, depth + 0.4, 0.20), col_roof)
    # Parapet on back + sides
    parapet_h = 0.45
    parapet_t = 0.18
    pz_top = ground_z + height + 0.20
    pz_centre = pz_top + parapet_h / 2
    _make_box_local(f"{name_prefix}_ParapetN",
                    (cx, cy + (depth + 0.4) / 2 - parapet_t / 2,
                     pz_centre),
                    (width + 0.4, parapet_t, parapet_h),
                    col_wall)
    for sgn in (-1, 1):
        _make_box_local(f"{name_prefix}_ParapetE_{sgn:+d}",
                        (cx + sgn * ((width + 0.4) / 2 - parapet_t / 2),
                         cy, pz_centre),
                        (parapet_t, depth + 0.4, parapet_h),
                        col_wall)
    # Single HVAC condenser on the roof
    _make_box_local(f"{name_prefix}_HVAC",
                    (cx + 1.5, cy + depth * 0.25,
                     pz_top + 0.40),
                    (1.4, 1.2, 0.80),
                    (0.62, 0.62, 0.64, 1.0))
    _make_box_local(f"{name_prefix}_HVAC_Grille",
                    (cx + 1.5, cy + depth * 0.25,
                     pz_top + 0.83),
                    (1.0, 0.9, 0.06),
                    (0.28, 0.28, 0.30, 1.0))
    # Gold roof trim (signature look)
    _make_box_local(f"{name_prefix}_RoofTrim",
                    (cx, cy - depth / 2 - 0.08, ground_z + height - 0.05),
                    (width + 0.4, 0.10, 0.18), col_trim)
    # Signage panel — pushed clear of the roof south edge so it
    # doesn't straddle the roof slab.
    sign_h_local = 0.8
    sign_y = cy - depth / 2 - 0.36
    _make_box_local(f"{name_prefix}_SignPanel",
                    (cx, sign_y,
                     ground_z + height + 0.20 + sign_h_local / 2),
                    (width * 0.7, 0.12, sign_h_local), col_sign)
    _make_box_local(f"{name_prefix}_SignTrim",
                    (cx, sign_y,
                     ground_z + height + 0.20 + sign_h_local + 0.05),
                    (width * 0.7 + 0.10, 0.14, 0.10), col_trim)

    # ── INTERIOR · two big comic-rack shelves running E-W and the
    # iconic photocopier in the north-east corner near the counter
    for k, shelf_y in enumerate((cy - 0.5, cy + 1.5)):
        _make_box_local(f"{name_prefix}_Shelf_{k}",
                        (cx, shelf_y, ground_z + 1.0),
                        (width - 1.5, 0.40, 2.0), col_shelf)
        # Colourful comics on top
        for j in range(5):
            jx = cx - (width - 2) / 2 + j * (width - 2) / 4
            _make_box_local(f"{name_prefix}_Shelf_{k}_Books_{j}",
                            (jx, shelf_y, ground_z + 1.85),
                            (0.50, 0.30, 0.30), col_books)
    # Counter at south-east (player's right on entry)
    _make_box_local(f"{name_prefix}_Counter",
                    (cx + width / 2 - 1.4, cy - depth / 2 + 1.5,
                     ground_z + 0.55),
                    (1.8, 0.7, 1.1), col_counter)
    # Photocopier in NE corner — beige body + dark top + side panel
    px = cx + width / 2 - 1.1
    py = cy + depth / 2 - 1.1
    _make_box_local(f"{name_prefix}_Xerox_Body",
                    (px, py, ground_z + 0.55),
                    (0.85, 0.70, 1.10), col_xerox_body)
    _make_box_local(f"{name_prefix}_Xerox_TopLid",
                    (px, py, ground_z + 1.16),
                    (0.85, 0.70, 0.08), col_xerox_top)
    _make_box_local(f"{name_prefix}_Xerox_Panel",
                    (px - 0.30, py + 0.10, ground_z + 1.05),
                    (0.18, 0.20, 0.06), col_xerox_panel)
    # Output tray sticking out the west side
    _make_box_local(f"{name_prefix}_Xerox_Tray",
                    (px - 0.55, py, ground_z + 0.75),
                    (0.30, 0.50, 0.04), col_xerox_body)


def build_commercial_cluster():
    """Chapter-one commercial cluster · Kwik Stop + NexCorp Gas & Go
    + Cosmic Comics. Per _HCE_PROJECT_NOTES.md (2026-06-14) the
    convenience stores need plate-glass storefronts with the
    interior visible from the public sidewalk; Cosmic Comics
    canonically has a photocopier visible inside. Positioned in the
    South Commercial settlement belt (target z = -9.0) within
    walking distance of the country-club spawn point at
    (0, 30, -380).
    """
    # ── Chapter-one block layout · 4 storefronts in sight-line
    # range of each other, all sharing the same y = -360 line so
    # characters at their respective counters can see across the
    # block via plate-glass fronts.
    #
    #   west │ NexCorp   Kwik Shop strip      Diner    Cosmic │ east
    #        │   -60      -15 (28 m wide)       35       70   │
    #
    # Each gap between adjacent storefronts is sized so the
    # sidewalk + utility props fit between them.
    ks_x, ks_y = -15.0, -360.0
    ks_z = mesh_z(ks_x, ks_y)
    _build_kwik_shop_strip(ks_x, ks_y, ks_z)

    nc_x, nc_y = -60.0, -360.0
    nc_z = mesh_z(nc_x, nc_y)
    _build_convenience_store("NexCorpGG", nc_x, nc_y, nc_z,
                              brand="nexcorp")

    dn_x, dn_y = 35.0, -360.0
    dn_z = mesh_z(dn_x, dn_y)
    _build_diner(dn_x, dn_y, dn_z)

    cc_x, cc_y = 70.0, -360.0
    cc_z = mesh_z(cc_x, cc_y)
    _build_cosmic_comics(cc_x, cc_y, cc_z)
    # ── FUEL PUMP CANOPY out front (south of NexCorp building)
    # The canopy is a big flat roof on four steel columns, with two
    # fuel-pump islands underneath. The canopy faces the sidewalk
    # so the player walks past pumps to reach the storefront.
    can_cx, can_cy = nc_x, nc_y - 12.0
    can_w, can_d = 12.0, 8.0
    can_h = 4.4
    COL_CAN_STEEL = (0.92, 0.92, 0.90, 1.0)
    COL_CAN_ROOF  = (0.32, 0.42, 0.55, 1.0)
    COL_PUMP_BODY = (0.85, 0.85, 0.82, 1.0)
    COL_PUMP_HOSE = (0.18, 0.18, 0.20, 1.0)
    for ox in (-can_w / 2 + 0.3, can_w / 2 - 0.3):
        for oy in (-can_d / 2 + 0.3, can_d / 2 - 0.3):
            _make_cyl_local(
                f"NexCorpGG_CanopyCol_{ox:+.1f}_{oy:+.1f}",
                (can_cx + ox, can_cy + oy, nc_z + can_h / 2),
                0.18, can_h, COL_CAN_STEEL, segments=6)
    # Canopy slab
    _make_box_local("NexCorpGG_CanopyRoof",
                    (can_cx, can_cy, nc_z + can_h + 0.15),
                    (can_w + 0.6, can_d + 0.6, 0.30),
                    COL_CAN_ROOF)
    # Two pump islands — pump body rests ON TOP of the island pad
    # (was embedded 10 cm into the pad). All offsets now keyed to
    # pad_top so the stack reads as: pad → pump body → display.
    PAD_H = 0.20
    PUMP_H = 1.80
    DISPLAY_H = 0.30
    for k, ix in enumerate((-2.6, 2.6)):
        pad_top = nc_z + PAD_H
        # Island concrete pad
        _make_box_local(f"NexCorpGG_PumpPad_{k}",
                        (can_cx + ix, can_cy, nc_z + PAD_H / 2),
                        (1.8, 4.0, PAD_H),
                        (0.72, 0.70, 0.66, 1.0))
        # Pump body (bottom flush with pad top)
        _make_box_local(f"NexCorpGG_PumpBody_{k}",
                        (can_cx + ix, can_cy,
                         pad_top + PUMP_H / 2),
                        (0.80, 0.40, PUMP_H),
                        COL_PUMP_BODY)
        # Pump top display (bottom flush with pump body top)
        _make_box_local(f"NexCorpGG_PumpDisplay_{k}",
                        (can_cx + ix, can_cy,
                         pad_top + PUMP_H + DISPLAY_H / 2),
                        (0.70, 0.42, DISPLAY_H),
                        (0.20, 0.22, 0.28, 1.0))
        # Hose stubs on each end of the pump (mid-body height)
        for sgn in (-1, 1):
            _make_cyl_local(f"NexCorpGG_PumpHose_{k}_{sgn:+d}",
                            (can_cx + ix,
                             can_cy + sgn * 0.22,
                             pad_top + PUMP_H * 0.55),
                            0.04, 0.30, COL_PUMP_HOSE, segments=4)

    # ── PYLON SIGN on a pole · NexCorp brand visible from highway
    # 6m-tall pole + big square sign at the top with the NexCorp
    # blue square + price reader below.
    pyl_x = nc_x - 12.0
    pyl_y = nc_y - 18.0
    pyl_z = mesh_z(pyl_x, pyl_y)
    PYLON_H = 6.5
    _make_cyl_local("NexCorpGG_PylonPole",
                    (pyl_x, pyl_y, pyl_z + PYLON_H / 2),
                    0.20, PYLON_H, COL_CAN_STEEL, segments=6)
    _make_box_local("NexCorpGG_PylonSign",
                    (pyl_x, pyl_y, pyl_z + PYLON_H + 0.6),
                    (2.2, 0.15, 1.2),
                    (0.32, 0.55, 0.78, 1.0))
    _make_box_local("NexCorpGG_PylonPriceBoard",
                    (pyl_x, pyl_y, pyl_z + PYLON_H - 0.5),
                    (1.6, 0.15, 0.6),
                    (0.18, 0.18, 0.22, 1.0))

    # ── PARKING LOTS in front of each store · asphalt slab with
    # painted parking-space stripes. Each slab is sized to fit
    # 6 spaces and follows mesh_z corners so it doesn't float
    # over the South Commercial slope.
    COL_ASPHALT = (0.22, 0.22, 0.24, 1.0)
    COL_STRIPE  = (0.92, 0.90, 0.84, 1.0)
    for tag, store_x, store_y in (
        ("KwikShop", ks_x, ks_y),
        ("NexCorpGG", nc_x, nc_y),
        ("Diner", dn_x, dn_y),
        ("CosmicComics", cc_x, cc_y),
    ):
        lot_cx = store_x
        lot_w = 22.0
        lot_d = 14.0
        if tag == "NexCorpGG":
            # NexCorp's lot wraps AROUND the pump canopy, so push
            # the lot further south of the canopy footprint.
            lot_cy = store_y - 24.0
            lot_d = 10.0
        elif tag == "CosmicComics":
            # Cosmic Comics is a smaller shop — smaller lot too.
            lot_cy = store_y - 15.0
            lot_w = 14.0
            lot_d = 12.0
        elif tag == "Diner":
            lot_cy = store_y - 16.0
            lot_w = 20.0
            lot_d = 12.0
        else:
            # Kwik Shop — wider lot to match the 28 m strip.
            lot_cy = store_y - 17.0
            lot_w = 30.0
        # Four-vert slab so corners track terrain
        hw = lot_w / 2; hd = lot_d / 2
        lv = []
        for (lx, ly) in [(lot_cx - hw, lot_cy - hd),
                          (lot_cx + hw, lot_cy - hd),
                          (lot_cx + hw, lot_cy + hd),
                          (lot_cx - hw, lot_cy + hd)]:
            lv.append((lx, ly, mesh_z(lx, ly) + 0.04))
        _finalize_mesh(f"{tag}_Lot", lv, [[0, 1, 2, 3]], COL_ASPHALT)
        # 6 parking stripes (5 lines defining 6 bays) running N-S
        n_lines = 5
        for k in range(n_lines):
            sx_line = lot_cx - lot_w / 2 + (k + 1) * (lot_w / 6)
            sv = []
            for (lx, ly) in [(sx_line - 0.05, lot_cy - hd + 0.3),
                              (sx_line + 0.05, lot_cy - hd + 0.3),
                              (sx_line + 0.05, lot_cy + hd - 0.3),
                              (sx_line - 0.05, lot_cy + hd - 0.3)]:
                sv.append((lx, ly, mesh_z(lx, ly) + 0.055))
            _finalize_mesh(f"{tag}_LotStripe_{k}", sv, [[0, 1, 2, 3]],
                           COL_STRIPE)
        # Curb stop blocks at the north edge (between lot + sidewalk)
        for k in range(6):
            cs_x = lot_cx - lot_w / 2 + (k + 0.5) * (lot_w / 6)
            cs_y = lot_cy + hd - 0.5
            cs_z = mesh_z(cs_x, cs_y)
            _make_box_local(f"{tag}_CurbStop_{k}",
                            (cs_x, cs_y, cs_z + 0.10),
                            (1.5, 0.25, 0.20),
                            (0.78, 0.74, 0.66, 1.0))

    # ── SIDEWALK in FRONT of the storefronts (south side).
    # Player spawns at (0, 30, -380) facing south; the spawn-side
    # spur drops south to meet the strip sidewalk in front of all
    # three stores so the player walks past actual storefronts on
    # approach, not behind buildings.
    COL_SIDEWALK = (0.78, 0.76, 0.72, 1.0)
    walk_w = 2.5
    walk_strip_y = ks_y - 6.5     # all three stores share ks_y = nc_y = cc_y
    walk_pts = [
        (nc_x,  walk_strip_y),                # NexCorp (west-most)
        ((ks_x + nc_x) / 2, walk_strip_y),    # between NexCorp & Kwik Shop
        (ks_x - 14, walk_strip_y),            # Kwik Shop arcade bay front
        (ks_x,      walk_strip_y),            # Kwik Shop centre (Kwik Stop)
        (ks_x + 14, walk_strip_y),            # Kwik Shop laundromat bay
        ((ks_x + dn_x) / 2, walk_strip_y),    # between Kwik Shop & Diner
        (dn_x,  walk_strip_y),                # Diner
        ((dn_x + cc_x) / 2, walk_strip_y),    # between Diner & Cosmic
        (cc_x,  walk_strip_y),                # Cosmic Comics
    ]
    # Spawn-side spur drops from spawn approach south to the strip
    # sidewalk, then bends EAST through the natural gap between
    # the Kwik Shop strip and the Diner (x = 0 to 25) to reach
    # the road crosswalk. Avoids cutting through parking lots.
    spur_jog_x = 12.0
    # Spur curves gently east as it drops south so it doesn't sit
    # on the Kwik Shop lot's east edge (x = 0). By y = -348 the
    # spur has migrated to x = 4, clearing the lot fully.
    spur_pts = [
        (0.0, -340.0),                          # spawn-side start
        (4.0, -348.0),                          # gentle east curve
        (spur_jog_x, walk_strip_y),             # arrive at sidewalk
        (spur_jog_x, walk_strip_y - 3.0),       # drop south
        (spur_jog_x, ks_y - 32.0 + 4.0 + 0.5),  # at road north edge
    ]
    hw = walk_w / 2
    for i in range(len(walk_pts) - 1):
        x0, y0 = walk_pts[i]
        x1, y1 = walk_pts[i + 1]
        dxs = x1 - x0; dys = y1 - y0
        seg_len = math.hypot(dxs, dys) or 1.0
        perp_x = -dys / seg_len
        perp_y =  dxs / seg_len
        pv = []
        for (px, py) in [(x0 - perp_x * hw, y0 - perp_y * hw),
                         (x1 - perp_x * hw, y1 - perp_y * hw),
                         (x1 + perp_x * hw, y1 + perp_y * hw),
                         (x0 + perp_x * hw, y0 + perp_y * hw)]:
            pv.append((px, py, mesh_z(px, py) + 0.05))
        _finalize_mesh(f"CommSidewalk_{i}", pv, [[0, 1, 2, 3]],
                       COL_SIDEWALK)
    # ── ROAD running E-W in front of the strip · two-lane asphalt
    # with a centerline. Skirts the south edge of the parking lots
    # so the cluster reads as a real frontage.
    COL_ROAD = (0.18, 0.18, 0.20, 1.0)
    COL_CENTERLINE = (0.95, 0.85, 0.30, 1.0)   # yellow
    road_y = ks_y - 32.0
    road_w = 8.0
    road_x_min = cc_x + 30.0          # east end (past Cosmic Comics)
    road_x_max = nc_x - 35.0          # west end (past NexCorp pylon)
    # Sort so x_min < x_max
    if road_x_min > road_x_max:
        road_x_min, road_x_max = road_x_max, road_x_min
    n_segments = 6
    seg_dx = (road_x_max - road_x_min) / n_segments
    hwr = road_w / 2
    for k in range(n_segments):
        x0 = road_x_min + k * seg_dx
        x1 = road_x_min + (k + 1) * seg_dx
        rv = []
        for (rx, ry) in [(x0, road_y - hwr),
                         (x1, road_y - hwr),
                         (x1, road_y + hwr),
                         (x0, road_y + hwr)]:
            rv.append((rx, ry, mesh_z(rx, ry) + 0.04))
        _finalize_mesh(f"CommRoad_{k}", rv, [[0, 1, 2, 3]], COL_ROAD)
    # Dashed yellow centerline (one dash per segment)
    dash_l = 4.0
    dash_w = 0.18
    for k in range(n_segments):
        cx_dash = road_x_min + (k + 0.5) * seg_dx
        dv = []
        for (rx, ry) in [(cx_dash - dash_l / 2, road_y - dash_w / 2),
                         (cx_dash + dash_l / 2, road_y - dash_w / 2),
                         (cx_dash + dash_l / 2, road_y + dash_w / 2),
                         (cx_dash - dash_l / 2, road_y + dash_w / 2)]:
            dv.append((rx, ry, mesh_z(rx, ry) + 0.055))
        _finalize_mesh(f"CommRoad_Dash_{k}", dv, [[0, 1, 2, 3]],
                       COL_CENTERLINE)
    # ── ICE MACHINE + PROPANE CAGE outside Kwik Stop (against the
    # west wall on the sidewalk side). Standard chapter-1 strip
    # mall details: white ICE box with red script panel, plus a
    # caged box of propane tanks beside it.
    # Anchored to the Kwik Stop centre bay (kw_cx = ks_x). The
    # ice machine sits just south of the bay's south wall on the
    # sidewalk's north edge, west of the entry door.
    ic_x = ks_x - 2.8
    ic_y = ks_y - 5.5         # just south of the building south wall
    ic_z = mesh_z(ic_x, ic_y)
    COL_ICE_WHITE = (0.95, 0.95, 0.92, 1.0)
    COL_ICE_RED   = (0.78, 0.18, 0.18, 1.0)
    COL_CAGE      = (0.62, 0.62, 0.64, 1.0)
    COL_PROPANE   = (0.86, 0.84, 0.72, 1.0)
    # ICE machine body
    _make_box_local("KwikStop_IceMachine_Body",
                    (ic_x, ic_y, ic_z + 0.90),
                    (1.20, 0.80, 1.80), COL_ICE_WHITE)
    # Red logo panel near top
    _make_box_local("KwikStop_IceMachine_Logo",
                    (ic_x, ic_y - 0.41, ic_z + 1.40),
                    (1.0, 0.04, 0.40), COL_ICE_RED)
    # Door split visible on front (vertical seam)
    _make_box_local("KwikStop_IceMachine_DoorSeam",
                    (ic_x, ic_y - 0.41, ic_z + 0.60),
                    (0.03, 0.03, 0.80),
                    (0.62, 0.62, 0.64, 1.0))
    # ── Propane tank cage just east of the ice machine
    pc_x = ic_x + 1.35
    pc_y = ic_y
    pc_z = ic_z
    # Cage frame — 4 corner posts + grid suggestion via thin top rails
    cage_w, cage_d, cage_h = 1.10, 0.80, 1.20
    for sgn_x in (-1, 1):
        for sgn_y in (-1, 1):
            _make_box_local(
                f"KwikStop_Propane_Cage_Post_{sgn_x:+d}_{sgn_y:+d}",
                (pc_x + sgn_x * (cage_w / 2 - 0.04),
                 pc_y + sgn_y * (cage_d / 2 - 0.04),
                 pc_z + cage_h / 2),
                (0.06, 0.06, cage_h), COL_CAGE)
    # Top frame
    _make_box_local("KwikStop_Propane_Cage_Top",
                    (pc_x, pc_y, pc_z + cage_h + 0.04),
                    (cage_w, cage_d, 0.08), COL_CAGE)
    # 4 propane tanks visible inside (2x2 grid)
    for kx, ox in enumerate((-0.22, 0.22)):
        for ky, oy in enumerate((-0.18, 0.18)):
            _make_cyl_local(
                f"KwikStop_Propane_Tank_{kx}_{ky}",
                (pc_x + ox, pc_y + oy, pc_z + 0.50),
                0.16, 0.90, COL_PROPANE, segments=6)
            # Valve cap
            _make_cyl_local(
                f"KwikStop_Propane_Valve_{kx}_{ky}",
                (pc_x + ox, pc_y + oy, pc_z + 1.00),
                0.06, 0.10,
                (0.42, 0.42, 0.45, 1.0), segments=4)

    # ── SHOPPING CART CORRAL in the Kwik Stop lot — a steel
    # rectangle of low rails with 3 nested carts inside. Sits at
    # the SE corner of the lot so cars approach it on their way
    # to the road.
    # Cart corral near the EAST end of the Kwik Stop centre bay's
    # parking allocation. Inside the Kwik Shop strip's wider lot.
    co_x = ks_x + 12.0
    co_y = ks_y - 17.0 + 5.0   # north end of the lot at lot_y + lot_d/2
    co_z = mesh_z(co_x, co_y)
    COL_CORRAL = (0.62, 0.62, 0.64, 1.0)
    COL_CART_FRAME = (0.62, 0.62, 0.64, 1.0)
    COL_CART_BASKET = (0.85, 0.85, 0.82, 1.0)
    # Four corner posts + two side rails (E and W)
    for sgn_x in (-1, 1):
        _make_box_local(f"KwikStop_Corral_Post_F_{sgn_x:+d}",
                        (co_x + sgn_x * 0.55, co_y - 1.4,
                         co_z + 0.50),
                        (0.06, 0.06, 1.00), COL_CORRAL)
        _make_box_local(f"KwikStop_Corral_Post_B_{sgn_x:+d}",
                        (co_x + sgn_x * 0.55, co_y + 1.4,
                         co_z + 0.50),
                        (0.06, 0.06, 1.00), COL_CORRAL)
        _make_box_local(f"KwikStop_Corral_Rail_{sgn_x:+d}",
                        (co_x + sgn_x * 0.55, co_y,
                         co_z + 0.85),
                        (0.06, 2.8, 0.06), COL_CORRAL)
    # 3 carts inside, nested front-to-back
    for k in range(3):
        cx_c = co_x
        cy_c = co_y - 0.9 + k * 0.4
        # Basket — open box on top
        _make_box_local(f"KwikStop_Cart_{k}_Basket",
                        (cx_c, cy_c, co_z + 0.55),
                        (0.50, 0.70, 0.30), COL_CART_BASKET)
        # Handle bar at the back
        _make_box_local(f"KwikStop_Cart_{k}_Handle",
                        (cx_c, cy_c + 0.40, co_z + 0.90),
                        (0.50, 0.04, 0.06), COL_CART_FRAME)
        # Front wheel pair (small dark boxes)
        for sgn_w in (-1, 1):
            _make_box_local(
                f"KwikStop_Cart_{k}_Wheel_F_{sgn_w:+d}",
                (cx_c + sgn_w * 0.20, cy_c - 0.30,
                 co_z + 0.08),
                (0.08, 0.10, 0.16),
                (0.10, 0.10, 0.12, 1.0))
            _make_box_local(
                f"KwikStop_Cart_{k}_Wheel_B_{sgn_w:+d}",
                (cx_c + sgn_w * 0.20, cy_c + 0.30,
                 co_z + 0.08),
                (0.08, 0.10, 0.16),
                (0.10, 0.10, 0.12, 1.0))

    # ── UTILITY POLES with horizontal crossbar + dropped power
    # lines spanning between them. Five poles along the south edge
    # of the road (across from the storefronts), with thin black
    # lines between adjacent pole crossbars.
    COL_POLE_WOOD = (0.42, 0.32, 0.22, 1.0)
    COL_POLE_BAR  = (0.32, 0.28, 0.20, 1.0)
    COL_POWER_LINE = (0.08, 0.08, 0.08, 1.0)
    UTIL_POLE_H = 9.0
    # Utility poles distributed across the block frontage — one
    # past each block end, plus two intermediate between buildings.
    pole_xs = [nc_x - 22, (nc_x + ks_x) / 2, ks_x,
               (ks_x + dn_x) / 2, dn_x, cc_x + 18]
    pole_y = road_y - hwr - 4.0     # south of the road
    pole_positions = []
    for k, ux in enumerate(pole_xs):
        uz = mesh_z(ux, pole_y)
        _make_cyl_local(f"CommUtilPole_{k}",
                        (ux, pole_y, uz + UTIL_POLE_H / 2),
                        0.18, UTIL_POLE_H,
                        COL_POLE_WOOD, segments=6)
        # Horizontal crossbar
        _make_box_local(f"CommUtilPoleBar_{k}",
                        (ux, pole_y, uz + UTIL_POLE_H - 0.30),
                        (2.2, 0.16, 0.16), COL_POLE_BAR)
        # Three insulator stubs on top of the bar
        for sgn_off in (-0.9, 0.0, 0.9):
            _make_cyl_local(f"CommUtilIns_{k}_{int(sgn_off*10):+d}",
                            (ux + sgn_off, pole_y,
                             uz + UTIL_POLE_H - 0.10),
                            0.05, 0.20,
                            (0.88, 0.84, 0.72, 1.0), segments=4)
        pole_positions.append((ux, pole_y, uz + UTIL_POLE_H - 0.05))
    # Power lines between adjacent poles — one line per insulator
    # stub offset (-0.9, 0.0, 0.9). Each line approximated by a
    # very thin long box drooping slightly at the midpoint.
    for k in range(len(pole_positions) - 1):
        x0, y0, z0 = pole_positions[k]
        x1, y1, z1 = pole_positions[k + 1]
        for off in (-0.9, 0.0, 0.9):
            span = math.hypot(x1 - x0, y1 - y0)
            mid_x = (x0 + x1) / 2
            mid_y = (y0 + y1) / 2 + off / 1.0    # tiny stagger? skip
            mid_z = (z0 + z1) / 2 - 0.50         # sag
            # Use _build_oriented_handle to make a line from (x0,
            # y0+off, z0) sagging to mid and on to (x1, y1+off, z1)
            _build_oriented_handle(
                f"CommPowerLine_{k}_{int(off*10):+d}_A",
                (x0 + off, y0, z0),
                (mid_x + off, mid_y, mid_z),
                radius=0.025, color=COL_POWER_LINE)
            _build_oriented_handle(
                f"CommPowerLine_{k}_{int(off*10):+d}_B",
                (mid_x + off, mid_y, mid_z),
                (x1 + off, y1, z1),
                radius=0.025, color=COL_POWER_LINE)

    # ── STREET TREES planted in sidewalk cutouts between the
    # stores. Five mid-sized oaks at locations that don't collide
    # with benches, lampposts, phone booth, or the news rack.
    COL_OAK_TRUNK = (0.30, 0.22, 0.16, 1.0)
    COL_OAK_CANOPY = (0.30, 0.55, 0.25, 1.0)
    # Trees BETWEEN buildings so they don't block storefronts.
    # Block stores at x = -60, -15, 35, 70 with widths 14/28/18/9.
    # Building east edges: NexCorp -53, Kwik Shop -1, Diner 44.
    # Building west edges: Kwik Shop -29, Diner 26, Cosmic 65.5.
    street_tree_xs = [
        nc_x - 12,                      # west of NexCorp (open end)
        (nc_x + ks_x) / 2,              # between NexCorp & Kwik Shop (-37.5)
        (ks_x + dn_x) / 2,              # between Kwik Shop & Diner (10)
        (dn_x + cc_x) / 2,              # between Diner & Cosmic (52.5)
        cc_x + 8,                       # east of Cosmic (open end)
    ]
    for k, stx in enumerate(street_tree_xs):
        sty = walk_strip_y - 2.5      # south of the sidewalk, planted
                                      # between sidewalk and parking lot
        stz = mesh_z(stx, sty)
        trunk_h = 3.6
        canopy_r = 2.6
        _make_cyl_local(f"CommStreetTree_{k}_Trunk",
                        (stx, sty, stz + trunk_h / 2),
                        0.28, trunk_h, COL_OAK_TRUNK, segments=6)
        _make_sphere_low_local(f"CommStreetTree_{k}_Canopy",
                               (stx, sty,
                                stz + trunk_h + canopy_r * 0.55),
                               canopy_r, COL_OAK_CANOPY,
                               rings=3, segments=8)
        # Sidewalk cutout — a small brown square at the base of
        # the tree marking the planting bed
        _make_box_local(f"CommStreetTree_{k}_Bed",
                        (stx, sty, stz + 0.04),
                        (1.2, 1.2, 0.08),
                        (0.32, 0.22, 0.16, 1.0))

    # ── NEWSPAPER RACK outside Cosmic Comics. Two coin-op boxes
    # side by side on the sidewalk. Classic chapter-one street
    # furniture.
    for k, col in enumerate([(0.78, 0.18, 0.18, 1.0),   # red box
                              (0.18, 0.42, 0.62, 1.0)]):  # blue box
        nrx = cc_x - 3.0 + k * 0.65
        nry = walk_strip_y + 0.2       # on the sidewalk
        nrz = mesh_z(nrx, nry)
        # Body
        _make_box_local(f"CommNewsRack_{k}_Body",
                        (nrx, nry, nrz + 0.50),
                        (0.55, 0.35, 1.00), col)
        # Sloped top window (just a thin tilted box approximated as
        # a darker rectangle inset on top)
        _make_box_local(f"CommNewsRack_{k}_Window",
                        (nrx, nry - 0.02, nrz + 1.05),
                        (0.50, 0.28, 0.10),
                        (0.20, 0.22, 0.28, 1.0))
        # Coin slot
        _make_box_local(f"CommNewsRack_{k}_CoinSlot",
                        (nrx, nry - 0.18, nrz + 0.80),
                        (0.18, 0.04, 0.04),
                        (0.18, 0.18, 0.18, 1.0))

    # ── RECYCLING + TRASH PAIR at the east end of the strip
    # (between the Cosmic Comics lot and the road). Blue recycling +
    # green compost + the existing trash bin pattern, on a thin
    # concrete pad.
    rp_x = cc_x + 12.0
    rp_y = walk_strip_y       # on the sidewalk east of Cosmic
    rp_z = mesh_z(rp_x, rp_y)
    _make_box_local("CommRecycPad",
                    (rp_x, rp_y, rp_z + 0.04),
                    (2.4, 1.0, 0.08), (0.78, 0.76, 0.72, 1.0))
    for k, (col, tag) in enumerate(((
            (0.32, 0.42, 0.78, 1.0), "Recycling"),
            ((0.30, 0.55, 0.25, 1.0), "Compost"),
            ((0.32, 0.32, 0.32, 1.0), "Trash"))):
        bx = rp_x - 0.8 + k * 0.8
        _make_cyl_local(f"CommRecycBin_{tag}",
                        (bx, rp_y, rp_z + 0.55),
                        0.30, 1.0, col, segments=8)
        # Lid
        _make_cyl_local(f"CommRecycBinLid_{tag}",
                        (bx, rp_y, rp_z + 1.07),
                        0.32, 0.06,
                        (0.20, 0.20, 0.22, 1.0), segments=8)

    # ── SCOOTERS parked outside the arcade and diner — chapter-
    # one kids-on-scooters atmosphere. The scooters lean against
    # imaginary walls on the sidewalk; here they just sit upright
    # since the build script doesn't tilt props.
    arcade_door_x = ks_x - 9.0
    for k, (sc_x_off, deck_col, metal_col) in enumerate((
        (-1.0, (0.30, 0.55, 0.25, 1.0), (0.78, 0.78, 0.80, 1.0)),
        (0.5,  (0.85, 0.22, 0.20, 1.0), (0.62, 0.62, 0.64, 1.0)),
    )):
        sx_pos = arcade_door_x + sc_x_off
        sy_pos = walk_strip_y + 0.6   # just north of sidewalk centre
        sz_pos = mesh_z(sx_pos, sy_pos)
        _build_scooter(f"ArcadeScooter_{k}", sx_pos, sy_pos, sz_pos,
                       color_deck=deck_col, color_metal=metal_col)
    # One more scooter outside the diner
    _build_scooter("DinerScooter",
                   dn_x - 4.0, walk_strip_y + 0.5,
                   mesh_z(dn_x - 4.0, walk_strip_y + 0.5),
                   color_deck=(0.32, 0.55, 0.78, 1.0),
                   color_metal=(0.78, 0.78, 0.80, 1.0))

    # ── STRIPED CANVAS AWNINGS over each storefront door so the
    # block reads as a real chapter-one strip mall instead of
    # bare plate-glass. Each awning is a slanted slab in alternating
    # colour stripes hanging out 1.2 m from the storefront wall.
    awning_storefronts = [
        # (door_cx, store_cy, store_depth, primary_col, stripe_col)
        # NexCorp door is on the right side of its bay
        (nc_x + 14/2 - 1.8, nc_y, 10.0,
            (0.32, 0.42, 0.55, 1.0), (0.92, 0.92, 0.90, 1.0)),
        # Kwik Shop has 3 doors — one per bay
        (ks_x - 9.0, ks_y, 10.0,
            (0.62, 0.22, 0.78, 1.0), (0.95, 0.85, 0.30, 1.0)),
        (ks_x + 0.0, ks_y, 10.0,
            (0.85, 0.22, 0.20, 1.0), (0.98, 0.95, 0.86, 1.0)),
        (ks_x + 9.0, ks_y, 10.0,
            (0.32, 0.55, 0.78, 1.0), (0.98, 0.98, 0.96, 1.0)),
        # Diner door is centred
        (dn_x, dn_y, 9.0,
            (0.85, 0.22, 0.20, 1.0), (0.92, 0.90, 0.88, 1.0)),
        # Cosmic Comics door is centred
        (cc_x, cc_y, 8.0,
            (0.32, 0.18, 0.32, 1.0), (0.95, 0.85, 0.30, 1.0)),
    ]
    for k, (a_cx, a_cy, a_depth, col_primary, col_stripe) in enumerate(awning_storefronts):
        a_z = mesh_z(a_cx, a_cy - a_depth / 2 - 0.6) + 2.80
        # Wall side (north corner) up at the storefront top
        # Hang side (south corner) 0.4 m down + 1.2 m out
        glass_y = a_cy - a_depth / 2 + 0.05
        n_stripes = 5
        stripe_w = 2.0 / n_stripes
        for s in range(n_stripes):
            col = col_primary if s % 2 == 0 else col_stripe
            # 4-vert quad: stripe runs E-W with slight slope
            sx_off = -1.0 + s * stripe_w
            sw = stripe_w
            verts = [
                (a_cx + sx_off, glass_y, a_z),
                (a_cx + sx_off + sw, glass_y, a_z),
                (a_cx + sx_off + sw, glass_y - 1.2, a_z - 0.40),
                (a_cx + sx_off, glass_y - 1.2, a_z - 0.40),
            ]
            _finalize_mesh(f"Awning_{k}_{s}", verts, [[0,1,2,3]], col)
        # Awning support brackets (thin diagonal bars)
        for sgn in (-1, 1):
            bxx = a_cx + sgn * 1.0
            _make_box_local(f"Awning_{k}_Bracket_{sgn:+d}",
                            (bxx, glass_y - 0.6, a_z - 0.20),
                            (0.04, 1.10, 0.04),
                            (0.32, 0.32, 0.34, 1.0))

    # ── OUTDOOR PATIO TABLE in front of the diner — a small round
    # table with 2 chairs on the sidewalk, just east of the
    # diner's main entry door. Classic chapter-one diner-spillover.
    pat_x = dn_x + 5.5
    pat_y = walk_strip_y + 0.2
    pat_z = mesh_z(pat_x, pat_y)
    COL_PAT_TOP = (0.92, 0.90, 0.88, 1.0)
    COL_PAT_LEG = (0.62, 0.62, 0.64, 1.0)
    # Round-ish table top (octagonal cylinder)
    _make_cyl_local("Diner_PatioTable_Top",
                    (pat_x, pat_y, pat_z + 0.72),
                    0.45, 0.05, COL_PAT_TOP, segments=8)
    _make_cyl_local("Diner_PatioTable_Stem",
                    (pat_x, pat_y, pat_z + 0.35),
                    0.06, 0.70, COL_PAT_LEG, segments=6)
    # 2 chairs flanking the table
    for sgn, dy in ((-1, -0.65), (1, 0.65)):
        chair_y = pat_y + dy
        # Seat
        _make_box_local(f"Diner_PatioChair_{sgn:+d}_Seat",
                        (pat_x, chair_y, pat_z + 0.46),
                        (0.40, 0.40, 0.06), COL_PAT_TOP)
        # Back
        _make_box_local(f"Diner_PatioChair_{sgn:+d}_Back",
                        (pat_x, chair_y + sgn * 0.18, pat_z + 0.75),
                        (0.40, 0.04, 0.50), COL_PAT_TOP)
        # 4 legs
        for lx, ly in ((-0.16, -0.16), (-0.16, 0.16),
                        (0.16, -0.16), (0.16, 0.16)):
            _make_box_local(
                f"Diner_PatioChair_{sgn:+d}_Leg_{int(lx*10)}_{int(ly*10)}",
                (pat_x + lx, chair_y + ly, pat_z + 0.23),
                (0.04, 0.04, 0.46), COL_PAT_LEG)

    # ── PHONE BOOTH on the sidewalk between Kwik Stop & NexCorp.
    # Classic glass-paneled booth with a red top cap. The hooked
    # handset is suggested by a thin dark box on the inside wall.
    ph_x = (ks_x + nc_x) / 2.0
    ph_y = walk_strip_y + 0.2     # on the sidewalk, slightly north
    ph_z = mesh_z(ph_x, ph_y)
    COL_BOOTH_FRAME = (0.18, 0.18, 0.18, 1.0)
    COL_BOOTH_GLASS = (0.42, 0.50, 0.58, 0.6)   # tinted glass-ish
    COL_BOOTH_CAP   = (0.82, 0.18, 0.18, 1.0)
    COL_HANDSET     = (0.22, 0.20, 0.20, 1.0)
    BOOTH_W = 0.95; BOOTH_D = 0.95; BOOTH_H = 2.30
    # Four corner posts
    for sgn_x in (-1, 1):
        for sgn_y in (-1, 1):
            _make_box_local(
                f"Comm_PhoneBooth_Post_{sgn_x:+d}_{sgn_y:+d}",
                (ph_x + sgn_x * (BOOTH_W / 2 - 0.04),
                 ph_y + sgn_y * (BOOTH_D / 2 - 0.04),
                 ph_z + BOOTH_H / 2),
                (0.08, 0.08, BOOTH_H), COL_BOOTH_FRAME)
    # Side glass panels (back + two sides; front is open for entry)
    _make_box_local("Comm_PhoneBooth_BackGlass",
                    (ph_x, ph_y + BOOTH_D / 2 - 0.02,
                     ph_z + BOOTH_H / 2 - 0.15),
                    (BOOTH_W - 0.16, 0.04, BOOTH_H - 0.30),
                    COL_BOOTH_GLASS)
    for sgn_x in (-1, 1):
        _make_box_local(
            f"Comm_PhoneBooth_SideGlass_{sgn_x:+d}",
            (ph_x + sgn_x * (BOOTH_W / 2 - 0.02), ph_y,
             ph_z + BOOTH_H / 2 - 0.15),
            (0.04, BOOTH_D - 0.16, BOOTH_H - 0.30),
            COL_BOOTH_GLASS)
    # Red cap on top
    _make_box_local("Comm_PhoneBooth_Cap",
                    (ph_x, ph_y, ph_z + BOOTH_H + 0.10),
                    (BOOTH_W + 0.06, BOOTH_D + 0.06, 0.20),
                    COL_BOOTH_CAP)
    # Handset suggestion: thin dark box on back inside wall
    _make_box_local("Comm_PhoneBooth_Handset",
                    (ph_x, ph_y + BOOTH_D / 2 - 0.10,
                     ph_z + 1.25),
                    (0.08, 0.10, 0.32), COL_HANDSET)
    # Phone body / coin box
    _make_box_local("Comm_PhoneBooth_PhoneBody",
                    (ph_x, ph_y + BOOTH_D / 2 - 0.08,
                     ph_z + 1.00),
                    (0.28, 0.10, 0.40),
                    (0.32, 0.32, 0.32, 1.0))

    # ── NPC SPAWN MARKERS · invisible-ish low-profile pucks
    # marking the canonical chapter-one positions. These are
    # small flat cylinders just barely above ground so an NPC
    # spawn script can read their world position. They keep
    # their distinct mesh names so the game can target them
    # individually.
    # Markers sit at each counter on the back-wall side a clerk
    # would stand. Spawn scripts should nudge slightly toward the
    # back wall when actually instantiating a figure.
    # Per user spec: "characters can see each other at their
    # jobs." All markers are within sight-line range across the
    # block's plate-glass storefronts.
    # Each NPC stands in a CLEAR aisle behind their counter, not
    # embedded inside it. Convenience-store back wall interior at
    # cy + 4.8; counter NORTH edge at cy + 3.8; NPC at cy + 4.3
    # gives ~0.25 m clearance on both sides of a 0.5 m body.
    npc_markers = [
        ("NPC_Skip_Locker",      nc_x + 4.0, nc_y + 4.3),
        ("NPC_Arcade_Attendant", ks_x - 9.0, ks_y + 4.3),
        ("NPC_Sam_Register",     ks_x + 2.8, ks_y + 4.3),
        # Laundromat has no counter; clerk stands near the change
        # machine at the bay's west partition.
        ("NPC_Laundromat_Clerk", ks_x + 9.0 - 3.0, ks_y + 0.5),
        # Diner customer counter spans cy+1.17 to cy+2.07. Pass-
        # wall at cy+3.0. Prep counter spans cy+3.70 to cy+4.30
        # against the back wall. Waiter stands in the customer-
        # side staff aisle (between counter and pass-wall); cook
        # stands in the kitchen-side aisle (between pass-wall and
        # prep counter).
        ("NPC_Diner_Cook",       dn_x,        dn_y + 3.4),
        ("NPC_Diner_Waiter",     dn_x + 4.0, dn_y + 2.5),
        # Cosmic Comics counter at south wall (cy-2.85 to cy-2.15);
        # clerk stands NORTH of counter, deeper into the shop.
        ("NPC_Comics_Clerk",     cc_x + 3.1, cc_y - 1.0),
    ]
    for name, mx_, my_ in npc_markers:
        mz = mesh_z(mx_, my_)
        _make_cyl_local(name,
                        (mx_, my_, mz + 0.01),
                        0.30, 0.02,
                        (0.95, 0.85, 0.30, 0.4), segments=8)

    # ── ACTUAL FIGURES at each NPC marker · so the player can SEE
    # the chapter-one cast through the plate-glass storefronts.
    # Each figure faces SOUTH (toward the storefront / player) so
    # the silhouette reads cleanly from the sidewalk. Outfit /
    # palette varies per character so the cast is distinguishable
    # at a glance.
    chapter_one_cast = [
        # (name, x, y, scale, hair, jacket, pants)
        ("Skip",     nc_x + 4.0, nc_y + 4.3, 1.0, "short",
            (0.32, 0.55, 0.78, 1.0),   # blue NexCorp uniform
            (0.42, 0.42, 0.45, 1.0)),
        ("ArcadeAtt", ks_x - 9.0, ks_y + 4.3, 1.0, "bowl",
            (0.62, 0.22, 0.78, 1.0),
            (0.20, 0.20, 0.22, 1.0)),
        ("Sam",      ks_x + 2.8, ks_y + 4.3, 1.0, "short",
            (0.85, 0.22, 0.20, 1.0),
            (0.55, 0.50, 0.42, 1.0)),
        ("LaundryAtt", ks_x + 9.0 - 3.0, ks_y + 0.5, 1.0, "bowl",
            (0.32, 0.55, 0.78, 1.0),
            (0.92, 0.92, 0.90, 1.0)),
        ("DinerCook", dn_x,        dn_y + 3.4, 1.0, "short",
            (0.98, 0.98, 0.96, 1.0),
            (0.18, 0.18, 0.22, 1.0)),
        ("DinerWaiter", dn_x + 4.0, dn_y + 2.5, 1.0, "short",
            (0.85, 0.22, 0.20, 1.0),
            (0.92, 0.90, 0.84, 1.0)),
        ("ComicsClerk", cc_x + 3.1, cc_y - 1.0, 1.0, "bowl",
            (0.95, 0.85, 0.30, 1.0),
            (0.32, 0.18, 0.32, 1.0)),
    ]
    for tag, fx, fy, sc, hair, jacket, pants in chapter_one_cast:
        fz = mesh_z(fx, fy)
        human_figure(
            name=f"NPC_{tag}",
            base_x=fx, base_y=fy, base_z=fz,
            scale=sc,
            facing='-Y',                  # face SOUTH (toward player)
            skin_color=(0.92, 0.75, 0.62, 1.0),
            hair_style=hair,
            hair_color=(0.20, 0.14, 0.10, 1.0),
            jacket_color=jacket,
            pants_color=pants,
            shoe_color=(0.20, 0.16, 0.14, 1.0),
            has_sunglasses=False,
            with_ears=True,
            with_mouth=True,
            mouth_color=(0.55, 0.22, 0.28, 1.0),
        )

    # ── CUSTOMERS · a few patrons scattered around the block so
    # it reads as ALIVE, not staffed-but-empty. Each faces the
    # action they're engaged with (arcade kid faces cabinet,
    # diner patron faces counter, etc.)
    customers = [
        # (name, x, y, facing, scale, hair, jacket, pants)
        # Arcade kid at the leftmost cabinet (cabinet at ks_x-12,
        # cy + 2.0). Kid stands just south of cabinet facing it.
        ("ArcadeKid",  ks_x - 12.0, ks_y + 1.0, '+Y', 0.78, "bowl",
            (0.42, 0.65, 0.32, 1.0), (0.32, 0.18, 0.32, 1.0)),
        # Diner patron standing next to a stool. Stools at
        # cy + 0.57 (NORTH of cy, not south). Patron facing
        # north toward the counter.
        ("DinerPatron", dn_x - 2.0, dn_y + 0.6, '+Y', 1.0, "short",
            (0.62, 0.42, 0.78, 1.0), (0.18, 0.22, 0.30, 1.0)),
        # Cosmic Comics browser between the two shelves (cy + 0.5).
        ("ComicsBrowser", cc_x - 1.5, cc_y + 0.5, '+Y', 0.92, "bowl",
            (0.95, 0.55, 0.20, 1.0), (0.42, 0.30, 0.20, 1.0)),
        # Sidewalk pedestrian heading east, between Kwik Shop and
        # Diner. Faces +X (east).
        ("Pedestrian", 12.0, walk_strip_y, '+X', 1.0, "short",
            (0.32, 0.55, 0.78, 1.0), (0.42, 0.42, 0.45, 1.0)),
    ]
    for tag, fx, fy, facing, sc, hair, jacket, pants in customers:
        fz = mesh_z(fx, fy)
        human_figure(
            name=f"NPC_{tag}",
            base_x=fx, base_y=fy, base_z=fz,
            scale=sc,
            facing=facing,
            skin_color=(0.92, 0.75, 0.62, 1.0),
            hair_style=hair,
            hair_color=(0.20, 0.14, 0.10, 1.0),
            jacket_color=jacket,
            pants_color=pants,
            shoe_color=(0.20, 0.16, 0.14, 1.0),
            has_sunglasses=False,
            with_ears=True,
            with_mouth=True,
            mouth_color=(0.55, 0.22, 0.28, 1.0),
        )

    # ── KWIK SHOP LOT DIVIDER ISLAND · the strip is wide enough
    # (30 m lot) that a single uninterrupted parking row reads as
    # a sea of asphalt. One planted island in the middle of the
    # lot breaks it up: brown curb perimeter + low grass + small
    # tree. Splits the lot visually into ARCADE-side and
    # LAUNDROMAT-side approaches.
    # Divider sits BETWEEN the middle car (at ks_x) and the east
    # car (at ks_x + 11) so it doesn't collide with either.
    div_x = ks_x + 5.5
    div_y = ks_y - 17.0 + 1.0
    div_z = mesh_z(div_x, div_y)
    COL_DIV_CURB = (0.62, 0.58, 0.50, 1.0)
    COL_DIV_GRASS = (0.30, 0.55, 0.25, 1.0)
    # Curb perimeter (thin box ring)
    div_w = 4.0; div_d = 2.4
    _make_box_local("KwikShop_LotDivider_Curb",
                    (div_x, div_y, div_z + 0.08),
                    (div_w, div_d, 0.16), COL_DIV_CURB)
    # Grass infill (slightly smaller)
    _make_box_local("KwikShop_LotDivider_Grass",
                    (div_x, div_y, div_z + 0.13),
                    (div_w - 0.30, div_d - 0.30, 0.06),
                    COL_DIV_GRASS)
    # Small ornamental tree in the middle
    _make_cyl_local("KwikShop_LotDivider_TreeTrunk",
                    (div_x, div_y, div_z + 1.20),
                    0.16, 2.4,
                    (0.30, 0.22, 0.16, 1.0), segments=6)
    _make_sphere_low_local("KwikShop_LotDivider_TreeCanopy",
                           (div_x, div_y, div_z + 2.80),
                           1.10, COL_DIV_GRASS, rings=3, segments=8)

    # ── PARKED CARS · two per lot, nose-in toward the storefront.
    # Distinct paint colours so the strip reads as populated rather
    # than uniform.
    parked_specs = [
        ("KwikShop", ks_x - 11, ks_y - 14, (0.82, 0.32, 0.22, 1.0)),  # red
        ("KwikShop", ks_x,      ks_y - 14, (0.78, 0.74, 0.68, 1.0)),  # beige
        ("KwikShop", ks_x + 11, ks_y - 14, (0.32, 0.55, 0.78, 1.0)),  # blue (laundromat)
        # Pumped inward 1 m so the cars clear the canopy columns
        # (columns at can_cx ± 5.7 m; cars 1.8 m wide so they
        # overlapped the columns at ±5 m).
        ("NexCorpGG", nc_x - 4, nc_y - 22, (0.20, 0.20, 0.22, 1.0)),  # black
        ("NexCorpGG", nc_x + 4, nc_y - 22, (0.42, 0.42, 0.45, 1.0)),  # grey
        ("Diner",     dn_x - 6, dn_y - 13, (0.95, 0.85, 0.30, 1.0)),  # yellow
        ("Diner",     dn_x + 6, dn_y - 13, (0.42, 0.62, 0.32, 1.0)),  # green
        ("CosmicComics", cc_x - 3, cc_y - 12, (0.62, 0.42, 0.78, 1.0)), # purple
        ("CosmicComics", cc_x + 3, cc_y - 12, (0.92, 0.55, 0.20, 1.0)), # orange
    ]
    for k, (tag, px, py, col) in enumerate(parked_specs):
        pz = mesh_z(px, py)
        _build_parked_car(f"{tag}_Car_{k}", px, py, pz, col,
                           facing='+Y')

    # Crosswalk where the spawn-side spur meets the road. The
    # spur jogs east to spur_jog_x to thread through the lot gap,
    # so the crosswalk matches that x.
    cross_x = spur_jog_x
    cross_w_total = 4.0
    cross_n_stripes = 6
    cross_stripe_w = (cross_w_total / (2 * cross_n_stripes - 1)) * 0.9
    for k in range(cross_n_stripes):
        sx_stripe = cross_x - cross_w_total / 2 + \
                    k * (cross_w_total / (cross_n_stripes - 1))
        cv = []
        for (px, py) in [(sx_stripe - cross_stripe_w / 2, road_y - hwr + 0.4),
                         (sx_stripe + cross_stripe_w / 2, road_y - hwr + 0.4),
                         (sx_stripe + cross_stripe_w / 2, road_y + hwr - 0.4),
                         (sx_stripe - cross_stripe_w / 2, road_y + hwr - 0.4)]:
            cv.append((px, py, mesh_z(px, py) + 0.055))
        _finalize_mesh(f"CommRoad_Crosswalk_{k}", cv, [[0, 1, 2, 3]],
                       (0.92, 0.90, 0.84, 1.0))

    # ── BUS-STOP SHELTER on the road frontage between the Diner
    # and Cosmic Comics lots. Four steel posts + slanted roof +
    # back wall + side panel + bench inside. Players can stand
    # under it; in chapter one the school bus runs this route.
    bus_x = (dn_x + cc_x) / 2 + 8.0
    bus_y = road_y + hwr + 4.0     # just north of the road
    bus_z = mesh_z(bus_x, bus_y)
    COL_BUS_STEEL = (0.62, 0.62, 0.64, 1.0)
    COL_BUS_ROOF = (0.32, 0.42, 0.55, 1.0)
    COL_BUS_BACK = (0.85, 0.82, 0.74, 1.0)
    bus_w = 4.0; bus_d = 1.6; bus_h = 2.40
    # Four corner posts
    for sgn_x in (-1, 1):
        for sgn_y in (-1, 1):
            _make_box_local(
                f"BusStop_Post_{sgn_x:+d}_{sgn_y:+d}",
                (bus_x + sgn_x * (bus_w / 2 - 0.05),
                 bus_y + sgn_y * (bus_d / 2 - 0.05),
                 bus_z + bus_h / 2),
                (0.10, 0.10, bus_h), COL_BUS_STEEL)
    # Back wall (north side) — translucent-suggestion via cream
    # panel
    _make_box_local("BusStop_BackWall",
                    (bus_x, bus_y + bus_d / 2 - 0.05,
                     bus_z + bus_h * 0.55),
                    (bus_w - 0.10, 0.08, bus_h * 0.85),
                    COL_BUS_BACK)
    # One side wall (east) — keeps wind off
    _make_box_local("BusStop_SideWall_E",
                    (bus_x + bus_w / 2 - 0.05, bus_y,
                     bus_z + bus_h * 0.55),
                    (0.08, bus_d - 0.10, bus_h * 0.85),
                    COL_BUS_BACK)
    # Slanted roof — slight tilt to south for water shedding
    roof_verts = [
        (bus_x - bus_w / 2 - 0.10, bus_y - bus_d / 2,
         bus_z + bus_h - 0.10),
        (bus_x + bus_w / 2 + 0.10, bus_y - bus_d / 2,
         bus_z + bus_h - 0.10),
        (bus_x + bus_w / 2 + 0.10, bus_y + bus_d / 2 + 0.10,
         bus_z + bus_h + 0.10),
        (bus_x - bus_w / 2 - 0.10, bus_y + bus_d / 2 + 0.10,
         bus_z + bus_h + 0.10),
    ]
    _finalize_mesh("BusStop_Roof", roof_verts, [[0, 1, 2, 3]],
                   COL_BUS_ROOF)
    # Bench inside the shelter (against the back wall)
    _make_box_local("BusStop_Bench",
                    (bus_x, bus_y + bus_d / 4, bus_z + 0.42),
                    (bus_w - 0.30, 0.40, 0.06),
                    (0.42, 0.30, 0.20, 1.0))
    # Bench legs
    for lx in (-1.4, 1.4):
        _make_box_local(f"BusStop_BenchLeg_{int(lx*10)}",
                        (bus_x + lx, bus_y + bus_d / 4,
                         bus_z + 0.21),
                        (0.06, 0.40, 0.42),
                        (0.18, 0.18, 0.18, 1.0))
    # Bus stop POLE + flag sign out front
    pole_x = bus_x - bus_w / 2 - 0.6
    _make_cyl_local("BusStop_FlagPole",
                    (pole_x, bus_y, bus_z + 1.6),
                    0.05, 3.2, COL_BUS_STEEL, segments=6)
    _make_box_local("BusStop_FlagSign",
                    (pole_x, bus_y, bus_z + 3.0),
                    (0.40, 0.04, 0.40),
                    (0.32, 0.42, 0.55, 1.0))

    # Speed-limit sign on a 2 m pole just east of the crosswalk
    sl_x = spur_jog_x + 8.0
    sl_y = road_y + hwr + 1.2
    sl_z = mesh_z(sl_x, sl_y)
    _make_cyl_local("CommRoad_SpeedLimit_Pole",
                    (sl_x, sl_y, sl_z + 1.0),
                    0.04, 2.0, (0.62, 0.62, 0.64, 1.0), segments=4)
    _make_box_local("CommRoad_SpeedLimit_Sign",
                    (sl_x, sl_y, sl_z + 2.1),
                    (0.45, 0.04, 0.55), (0.98, 0.98, 0.96, 1.0))

    # Driveway aprons connecting each parking lot down to the road
    for tag, lot_x, lot_y, lot_w_drv in (
        ("KwikShop", ks_x, ks_y - 17, 8.0),
        ("NexCorpGG", nc_x, nc_y - 24, 8.0),
        ("Diner",     dn_x, dn_y - 16, 6.0),
        ("CosmicComics", cc_x, cc_y - 15, 6.0),
    ):
        # Apron from south edge of lot down to north edge of road
        apron_y0 = lot_y - 7.0       # bottom of lot
        apron_y1 = road_y + hwr      # north edge of road
        apron_hw = lot_w_drv / 2
        av = []
        for (ax, ay) in [(lot_x - apron_hw, apron_y0),
                          (lot_x + apron_hw, apron_y0),
                          (lot_x + apron_hw, apron_y1),
                          (lot_x - apron_hw, apron_y1)]:
            av.append((ax, ay, mesh_z(ax, ay) + 0.045))
        _finalize_mesh(f"{tag}_Apron", av, [[0, 1, 2, 3]], COL_ROAD)

    # ── STREETLIGHTS + BENCHES along the strip sidewalk
    # Six 4 m lamp posts on the south curb of the sidewalk (i.e.
    # 1 m further south of the sidewalk centerline).
    streetlight_xs = [nc_x - 8, nc_x + 8,
                       ks_x - 14, ks_x + 14,
                       dn_x - 8, dn_x + 8,
                       cc_x + 6]
    for k, slx in enumerate(streetlight_xs):
        sly = walk_strip_y - 1.5       # south of the sidewalk
        slz = mesh_z(slx, sly)
        _build_lamppost(f"Comm_Lamp_{k}", slx, sly, slz, pole_h=4.0)
    # One bench in front of each store. Bench Y is at the sidewalk
    # centerline; backrest faces NORTH (toward the storefront) so
    # someone sitting on the bench is looking into the shop window.
    COL_BENCH_WOOD = (0.42, 0.30, 0.20, 1.0)
    COL_BENCH_LEG  = (0.18, 0.18, 0.18, 1.0)
    for tag, store_x, store_y in (("KwikShop", ks_x, ks_y),
                                    ("NexCorpGG", nc_x, nc_y),
                                    ("Diner", dn_x, dn_y),
                                    ("CosmicComics", cc_x, cc_y)):
        bench_y = walk_strip_y - 0.20      # very slightly south of centerline
        bz = mesh_z(store_x, bench_y)
        _make_box_local(f"{tag}_Bench_Seat",
                        (store_x, bench_y, bz + 0.42),
                        (1.8, 0.42, 0.06), COL_BENCH_WOOD)
        # Backrest at REAR edge of seat (south side of seat) so
        # someone sitting on it faces NORTH toward the store.
        _make_box_local(f"{tag}_Bench_Back",
                        (store_x, bench_y - 0.18, bz + 0.65),
                        (1.8, 0.06, 0.40), COL_BENCH_WOOD)
        for sgn in (-1, 1):
            _make_box_local(f"{tag}_Bench_Leg_{sgn:+d}",
                            (store_x + sgn * 0.75, bench_y,
                             bz + 0.21),
                            (0.06, 0.42, 0.42), COL_BENCH_LEG)
        # Trash bin a step east of the bench (also on sidewalk)
        _make_cyl_local(f"{tag}_Bin",
                        (store_x + 1.6, bench_y, bz + 0.55),
                        0.28, 1.0, (0.32, 0.32, 0.32, 1.0),
                        segments=8)
    # ── HARMONY CREEK ESTATES community sign on a stone plinth
    # at the north end of the spawn spur. The first thing the
    # player sees as they walk south from the country-club
    # spawn point.
    # North of the spur start so the spur doesn't pass through
    # the plinth's 5.6 m footprint.
    hce_x = 0.0
    hce_y = -335.0
    hce_z = mesh_z(hce_x, hce_y)
    COL_HCE_STONE = (0.78, 0.74, 0.66, 1.0)
    COL_HCE_TRIM = (0.42, 0.30, 0.20, 1.0)
    COL_HCE_FACE = (0.86, 0.82, 0.70, 1.0)
    # Stone plinth base
    _make_box_local("HCE_Welcome_Plinth",
                    (hce_x, hce_y, hce_z + 0.50),
                    (5.6, 1.20, 1.00), COL_HCE_STONE)
    # Cap layer on the plinth
    _make_box_local("HCE_Welcome_PlinthCap",
                    (hce_x, hce_y, hce_z + 1.10),
                    (5.8, 1.30, 0.20), COL_HCE_TRIM)
    # Sign face on top (the Label3D target)
    _make_box_local("HCE_Welcome_SignFace",
                    (hce_x, hce_y, hce_z + 2.00),
                    (5.0, 0.15, 1.40), COL_HCE_FACE)
    # Sign top moulding
    _make_box_local("HCE_Welcome_SignTopMould",
                    (hce_x, hce_y, hce_z + 2.78),
                    (5.4, 0.20, 0.16), COL_HCE_TRIM)
    # Two flanking lanterns
    for sgn in (-1, 1):
        _make_cyl_local(f"HCE_Welcome_Lantern_{sgn:+d}_Pole",
                        (hce_x + sgn * 2.4, hce_y,
                         hce_z + 1.80),
                        0.06, 1.40, COL_HCE_TRIM, segments=6)
        _make_box_local(f"HCE_Welcome_Lantern_{sgn:+d}_Box",
                        (hce_x + sgn * 2.4, hce_y,
                         hce_z + 2.65),
                        (0.30, 0.30, 0.40),
                        (0.95, 0.85, 0.30, 1.0))     # warm glass

    # Spur from spawn approach to the strip sidewalk
    for i in range(len(spur_pts) - 1):
        x0, y0 = spur_pts[i]
        x1, y1 = spur_pts[i + 1]
        dxs = x1 - x0; dys = y1 - y0
        seg_len = math.hypot(dxs, dys) or 1.0
        perp_x = -dys / seg_len
        perp_y =  dxs / seg_len
        pv = []
        for (px, py) in [(x0 - perp_x * hw, y0 - perp_y * hw),
                         (x1 - perp_x * hw, y1 - perp_y * hw),
                         (x1 + perp_x * hw, y1 + perp_y * hw),
                         (x0 + perp_x * hw, y0 + perp_y * hw)]:
            pv.append((px, py, mesh_z(px, py) + 0.05))
        _finalize_mesh(f"CommSidewalk_Spur_{i}", pv, [[0, 1, 2, 3]],
                       COL_SIDEWALK)


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

def _base_skirt(name, x, y, ground_z, color=(0.30, 0.42, 0.20, 1.0),
                radius=0.45):
    """Small irregular grass/dirt mound at the base of a vertical
    prop. Masks any small alignment mismatch where the prop foot
    meets the ground triangle. Per user direction (2026-06-15):
    "fill in the gaps naturally with ways to fill in the space
    with appropriate props." """
    _make_sphere_low_local(f"{name}_Skirt",
                            (x, y, ground_z + 0.10),
                            radius, color, rings=3, segments=6)




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
    build_commercial_cluster()
    export_glb()


if __name__ == "__main__":
    main()
