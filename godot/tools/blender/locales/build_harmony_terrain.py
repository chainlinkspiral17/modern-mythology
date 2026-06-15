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
    # Harmony Creek High School football field + stadium platform
    # — large flat zone east of Phase 2 (between Phase 2 and the
    # East Commercial strip) for the field + bleachers. Expanded
    # to cover the track ring and end zones (total ~80 x 150 m,
    # rather than the field alone).
    ("HighSchoolField", 200, 480, -130, 110, +3.0, 0.88),
    # NexCorp HQ pad on the North Commercial belt — covers
    # plaza, reflecting pool, hedges, parking lot and flagpoles
    # (lot extends to y=264, pool to y=283).
    ("NexCorpHQPad",    -35,  35, 255, 335, +14.0, 0.95),
    # SCRATCH night-club pad on West Commercial Highway 9
    ("NightClubPad",   -530, -490, -22, 20, -2.0, 0.95),
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
        # EMPIRICAL DISC RADIUS · the analytic depression is
        # WEAKENED by settlement flattening (settlement target
        # pulls all elevations toward target_z by `flatness`, so
        # a 6 m-deep pond inside a flatness=0.55 zone yields only
        # a 2.7 m carved depression). A fixed 0.48×radius disc
        # therefore floats above terrain for ponds in flattened
        # zones. Probe outward sampling mesh_z and stop just
        # before terrain rises above water_z so the disc edge
        # sits where the bowl wall meets the water surface.
        wr = radius * 0.20
        for probe_k in range(1, 20):
            test_r = radius * (0.20 + probe_k * 0.04)
            # Sample 4 cardinal points at this radius
            terrain_above = False
            for sample_i in range(4):
                ang = 2.0 * math.pi * sample_i / 4
                tx = cx + math.cos(ang) * test_r
                ty = cy + math.sin(ang) * test_r
                if mesh_z(tx, ty) > water_z - 0.05:
                    terrain_above = True
                    break
            if terrain_above:
                break
            wr = test_r
        # Cap at 0.90 × radius so we never grow beyond the
        # depression's analytic extent.
        wr = min(wr, radius * 0.90)
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


def _fence_along(name, p0, p1, fence_type, sub_len=15.0):
    """Subdivide (p0, p1) into ~sub_len pieces and place a fence
    segment at each, sampling elevation at the midpoint of each
    piece. Per user feedback (2026-06-15): "fences running through
    terrain, no aligned to terrain." With 40 m sub-segments a
    typical district slope of ±1 m per 30 m gave each segment a
    ±0.7 m end-to-end elevation delta — fence floated on the
    high end and was buried on the low end. Dropped sub_len to
    15 m (delta now ±0.25 m, well within the fence's vertical
    extent so segments visibly track terrain).

    Each segment z is sampled at MIDPOINT and the segment is
    built as a straight box at that z. With short segments the
    joints step naturally to follow terrain.

    Also drops a small grass-coloured skirt sphere at each
    segment midpoint to mask any residual gap where the fence
    base meets the terrain mesh.
    """
    x0, y0 = p0; x1, y1 = p1
    length = math.hypot(x1 - x0, y1 - y0)
    if length < 0.001:
        return
    n = max(1, int(length / sub_len))
    for i in range(n):
        t0 = i / n; t1 = (i + 1) / n
        sp0 = (x0 + (x1 - x0) * t0, y0 + (y1 - y0) * t0)
        sp1 = (x0 + (x1 - x0) * t1, y0 + (y1 - y0) * t1)
        # Sample z at BOTH endpoints + midpoint; use the LOWER of
        # the endpoint samples as the segment base so the fence
        # always at least touches the lower terrain side (no
        # floating); the higher side gets buried slightly but
        # the skirt sphere masks it.
        mx = (sp0[0] + sp1[0]) / 2
        my = (sp0[1] + sp1[1]) / 2
        z_mid = mesh_z(mx, my)
        z_p0 = mesh_z(sp0[0], sp0[1])
        z_p1 = mesh_z(sp1[0], sp1[1])
        z = min(z_p0, z_p1, z_mid)
        if fence_type == 'iron':
            iron_lattice_fence(f"{name}_{i}", sp0, sp1, z=z, height=1.4)
            # Skirt to mask the join gap on the high side
            _base_skirt(f"{name}_{i}_Skirt", mx, my, z,
                         color=(0.30, 0.42, 0.20, 1.0), radius=0.40)
        elif fence_type == 'brick':
            brick_wall(f"{name}_{i}", sp0, sp1, z=z, height=1.8)
            _base_skirt(f"{name}_{i}_Skirt", mx, my, z,
                         color=(0.30, 0.42, 0.20, 1.0), radius=0.50)


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
    # Water sits ABOVE the ground (was at pool_ground - 0.30
    # which buried the disc beneath the terrain mesh — the
    # settlement zone is flat at +2.0 with no carved depression
    # at this pool location, so the water was invisible).
    pool_cx = sx
    pool_cy = sy - 22
    pool_r = 6.0
    pool_ground = mesh_z(pool_cx, pool_cy)
    pool_water_z = pool_ground + 0.04
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
    # Concrete pad sits on the ground (top at +0.10) and water
    # sits on TOP of the concrete (was at rill_ground - 0.18,
    # buried under the terrain mesh like the OT pool was).
    _make_box_local("OTPark_Rill_Concrete",
                    (rill_mid_x, rill_mid_y, rill_ground + 0.05),
                    (rill_sx, rill_sy, 0.10),
                    COL_POOL_RIM)
    _make_box_local("OTPark_Rill_Water",
                    (rill_mid_x, rill_mid_y, rill_ground + 0.12),
                    (water_sx, water_sy, 0.04),
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


def _build_parking_lot(name_prefix, lot_cx, lot_cy, lot_w, lot_d,
                        ground_z, building_y_north, car_palette,
                        n_handicap=1):
    """Strip-mall-style parking lot with 2 rows of head-in stalls,
    a drive aisle between them, proper stall stripes (3 sides per
    stall), handicap stalls closest to the building, and cars
    positioned inside stalls (not loose on the asphalt).

    Layout (north → south):
      · access aisle (4 m) flush with the building sidewalk
      · north stall row (5.5 m deep, cars facing north toward
        the building, closest to storefront)
      · centre drive aisle (6 m wide for 2-way navigation)
      · south stall row (5.5 m deep, cars facing south toward
        the road approach)
      · south access aisle (4 m)

    car_palette: list of (r, g, b, a) tuples; one car per element,
    placed in the first N stalls of (north row, then south row),
    SKIPPING the handicap stalls so they read as empty.

    n_handicap: number of HC stalls reserved at the NORTH row's
    most-buildingward end (typically 1-2 per strip-mall lot).
    """
    COL_ASPHALT = (0.22, 0.22, 0.24, 1.0)
    COL_STRIPE = (0.92, 0.90, 0.84, 1.0)
    COL_HC_BLUE = (0.18, 0.38, 0.72, 1.0)
    COL_HC_WHITE = (0.95, 0.95, 0.92, 1.0)
    COL_CURB = (0.78, 0.74, 0.66, 1.0)

    hw = lot_w / 2
    hd = lot_d / 2

    # Asphalt slab — per-corner mesh_z so the lot tracks terrain
    sv = []
    for (lx, ly) in [(lot_cx - hw, lot_cy - hd),
                     (lot_cx + hw, lot_cy - hd),
                     (lot_cx + hw, lot_cy + hd),
                     (lot_cx - hw, lot_cy + hd)]:
        sv.append((lx, ly, mesh_z(lx, ly) + 0.04))
    _finalize_mesh(f"{name_prefix}_Lot", sv, [[0, 1, 2, 3]],
                    COL_ASPHALT)

    # Stall + aisle parameters
    stall_w = 2.7
    stall_d = 5.5
    drive_aisle_w = 6.0
    n_stalls_per_row = int((lot_w - 1.0) / stall_w)  # 1 m margin
    actual_row_w = n_stalls_per_row * stall_w

    # Y positions of stall rows
    # North row: at lot_cy + drive_aisle_w/2 + stall_d/2
    # South row: at lot_cy - drive_aisle_w/2 - stall_d/2
    n_row_cy = lot_cy + drive_aisle_w / 2 + stall_d / 2
    s_row_cy = lot_cy - drive_aisle_w / 2 - stall_d / 2

    # Centre stripe of the drive aisle (yellow dashed line could
    # come later; just a thin white line for now)
    aisle_centre_stripe_l = actual_row_w
    _make_box_local(f"{name_prefix}_AisleDivider",
                    (lot_cx, lot_cy, mesh_z(lot_cx, lot_cy) + 0.055),
                    (aisle_centre_stripe_l, 0.10, 0.01),
                    COL_STRIPE)

    # Iterate stalls in each row
    car_idx = 0
    rows = [
        ('N', n_row_cy, +1, True),    # north row, cars face +Y (toward building)
        ('S', s_row_cy, -1, False),
    ]
    for row_tag, row_cy, face_dir_sgn, is_north_row in rows:
        # Stall end line (one long stripe at the building/road
        # end of the row, parallel to the drive aisle)
        end_line_cy = row_cy + face_dir_sgn * stall_d / 2
        _make_box_local(
            f"{name_prefix}_StallEndLine_{row_tag}",
            (lot_cx, end_line_cy,
             mesh_z(lot_cx, end_line_cy) + 0.055),
            (actual_row_w, 0.12, 0.01), COL_STRIPE)
        # Stall divider stripes (between adjacent stalls)
        for k in range(n_stalls_per_row + 1):
            sx_div = lot_cx - actual_row_w / 2 + k * stall_w
            sv2 = []
            for (lx, ly) in [
                (sx_div - 0.06, row_cy - stall_d / 2),
                (sx_div + 0.06, row_cy - stall_d / 2),
                (sx_div + 0.06, row_cy + stall_d / 2),
                (sx_div - 0.06, row_cy + stall_d / 2),
            ]:
                sv2.append((lx, ly, mesh_z(lx, ly) + 0.055))
            _finalize_mesh(
                f"{name_prefix}_StallDiv_{row_tag}_{k}",
                sv2, [[0, 1, 2, 3]], COL_STRIPE)

        # Handicap stalls (only in the NORTH row, closest to
        # building). Paint the stall floor blue + draw a thin
        # white border. Use the LEFTMOST n_handicap stalls.
        if is_north_row:
            for hck in range(n_handicap):
                hc_cx = lot_cx - actual_row_w / 2 + \
                        (hck + 0.5) * stall_w
                hc_cy = row_cy
                # Blue floor pad
                _make_box_local(
                    f"{name_prefix}_HCStall_{hck}",
                    (hc_cx, hc_cy,
                     mesh_z(hc_cx, hc_cy) + 0.045),
                    (stall_w - 0.20, stall_d - 0.20, 0.02),
                    COL_HC_BLUE)
                # White handicap "diamond" placeholder (small
                # white square at stall centre)
                _make_box_local(
                    f"{name_prefix}_HCSymbol_{hck}",
                    (hc_cx, hc_cy,
                     mesh_z(hc_cx, hc_cy) + 0.060),
                    (0.80, 0.80, 0.01),
                    COL_HC_WHITE)
        # Curb stops at the BACK of each stall (against the
        # building side for north row, against the road buffer
        # for south row)
        for k in range(n_stalls_per_row):
            cs_x = lot_cx - actual_row_w / 2 + (k + 0.5) * stall_w
            cs_y = row_cy + face_dir_sgn * (stall_d / 2 - 0.30)
            cs_z = mesh_z(cs_x, cs_y)
            _make_box_local(
                f"{name_prefix}_CurbStop_{row_tag}_{k}",
                (cs_x, cs_y, cs_z + 0.10),
                (1.5, 0.25, 0.20), COL_CURB)

        # Place cars INSIDE stalls
        first_car_idx_for_row = n_handicap if is_north_row else 0
        for k in range(n_stalls_per_row):
            if is_north_row and k < n_handicap:
                continue       # skip handicap stalls
            if car_idx >= len(car_palette):
                break
            car_x = lot_cx - actual_row_w / 2 + (k + 0.5) * stall_w
            # Car centre is offset back from the stall end by half
            # the car length so the bumper is 0.5 m from the curb
            car_y = row_cy + face_dir_sgn * \
                    (stall_d / 2 - 4.4 / 2 - 0.5)
            car_z = mesh_z(car_x, car_y)
            car_face = '+Y' if face_dir_sgn > 0 else '-Y'
            _build_parked_car(
                f"{name_prefix}_Car_{car_idx}",
                car_x, car_y, car_z,
                car_palette[car_idx], facing=car_face)
            car_idx += 1


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
    # ── Arcade attendant booth at the back wall — a small
    # counter + token display so the attendant has a workstation
    # instead of just standing alone in the middle of the bay.
    booth_x = arc_cx
    booth_y = cy + depth / 2 - 1.4    # in back aisle, south of wall
    _make_box_local("KwikShop_Arc_AttBooth_Counter",
                    (booth_x, booth_y, ground_z + 0.55),
                    (1.8, 0.7, 1.10), (0.42, 0.30, 0.20, 1.0))
    # Token / prize display behind the booth (thin tall shelf
    # mounted to the back wall). Depth shrunk to 0.15 so the
    # attendant has clearance between counter and shelf.
    _make_box_local("KwikShop_Arc_AttBooth_PrizeShelf",
                    (booth_x, cy + depth / 2 - 0.15,
                     ground_z + 1.30),
                    (2.4, 0.15, 1.40), (0.42, 0.42, 0.45, 1.0))
    # A row of small token boxes on top of the counter
    for k in range(3):
        tx = booth_x - 0.6 + k * 0.6
        _make_box_local(f"KwikShop_Arc_AttBooth_TokenBox_{k}",
                        (tx, booth_y, ground_z + 1.18),
                        (0.30, 0.30, 0.12),
                        (0.95, 0.85, 0.30, 1.0))   # gold tokens

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
    # Community bulletin board on the east partition — paper
    # flyers in coloured rectangles.
    bb_x = ldr_cx + bay_w / 2 - 0.06
    _make_box_local("KwikShop_Ldr_BulletinBoard",
                    (bb_x, cy + 0.5, ground_z + 1.50),
                    (0.08, 1.40, 1.20),
                    (0.42, 0.30, 0.20, 1.0))           # cork brown
    # 6 flyers pinned to the board (3x2 grid)
    for kx in range(3):
        for ky in range(2):
            cols = [(0.95, 0.85, 0.30, 1.0),
                    (0.32, 0.55, 0.78, 1.0),
                    (0.85, 0.22, 0.20, 1.0),
                    (0.62, 0.22, 0.78, 1.0),
                    (0.42, 0.62, 0.32, 1.0),
                    (0.98, 0.95, 0.86, 1.0)]
            col = cols[kx * 2 + ky]
            fy = cy + 0.5 - 0.50 + kx * 0.45
            fz = ground_z + 1.50 - 0.30 + ky * 0.50
            _make_box_local(f"KwikShop_Ldr_Flyer_{kx}_{ky}",
                            (bb_x - 0.05, fy, fz),
                            (0.02, 0.30, 0.30), col)


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

    # ── PARKING LOTS in front of each store. Per user feedback
    # (2026-06-15): cars parked INSIDE stalls (not loose on the
    # asphalt); handicap stalls closest to the building (min 1-2
    # per lot); shopping centres have plenty of OPEN concrete for
    # driving + fast-travel lanes — use 2 rows + central 6 m
    # drive aisle for navigation.
    #
    # Each call to _build_parking_lot creates the slab, two rows
    # of head-in stalls, stall stripes (3 sides per stall), curb
    # stops at the back of each stall, handicap stalls + symbol,
    # and CARS positioned INSIDE the stalls in the order of the
    # palette.
    common_palette = [
        (0.82, 0.32, 0.22, 1.0),    # red
        (0.78, 0.74, 0.68, 1.0),    # beige
        (0.32, 0.55, 0.78, 1.0),    # blue
        (0.20, 0.20, 0.22, 1.0),    # black
        (0.42, 0.62, 0.32, 1.0),    # green
        (0.92, 0.85, 0.30, 1.0),    # yellow
        (0.62, 0.42, 0.78, 1.0),    # purple
        (0.92, 0.55, 0.20, 1.0),    # orange
        (0.62, 0.62, 0.64, 1.0),    # silver
        (0.18, 0.32, 0.55, 1.0),    # navy
    ]
    # Kwik Shop — large strip lot directly in front of the strip
    _build_parking_lot("KwikShop", ks_x, ks_y - 18.0,
                        lot_w=30.0, lot_d=22.0,
                        ground_z=mesh_z(ks_x, ks_y - 18.0),
                        building_y_north=ks_y,
                        car_palette=common_palette,
                        n_handicap=2)
    # NexCorp Gas & Go — smaller lot south of the pump canopy
    _build_parking_lot("NexCorpGG", nc_x, nc_y - 25.0,
                        lot_w=18.0, lot_d=20.0,
                        ground_z=mesh_z(nc_x, nc_y - 25.0),
                        building_y_north=nc_y,
                        car_palette=common_palette[:4],
                        n_handicap=1)
    # Diner
    _build_parking_lot("Diner", dn_x, dn_y - 18.0,
                        lot_w=22.0, lot_d=20.0,
                        ground_z=mesh_z(dn_x, dn_y - 18.0),
                        building_y_north=dn_y,
                        car_palette=common_palette[:6],
                        n_handicap=1)
    # Cosmic Comics — smallest lot
    _build_parking_lot("CosmicComics", cc_x, cc_y - 17.0,
                        lot_w=16.0, lot_d=20.0,
                        ground_z=mesh_z(cc_x, cc_y - 17.0),
                        building_y_north=cc_y,
                        car_palette=common_palette[:4],
                        n_handicap=1)

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
        # clerk stands NORTH of counter at cy-1.3 — centred
        # between counter and the south shelf at cy-0.7.
        ("NPC_Comics_Clerk",     cc_x + 3.1, cc_y - 1.3),
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
        ("ComicsClerk", cc_x + 3.1, cc_y - 1.3, 1.0, "bowl",
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

    # (Parked cars now placed INSIDE stalls by _build_parking_lot)

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

    # ── DELIVERY TRUCK parked on the road frontage in front of
    # Kwik Shop — chapter-one truck driver dropping off supplies.
    # Box truck silhouette: cab + cargo box on top of a 6 wheels.
    truck_x = ks_x - 6.0
    truck_y = road_y + 0.5         # in the eastbound lane (north of centre)
    truck_z = mesh_z(truck_x, truck_y)
    COL_TRUCK_BODY = (0.92, 0.92, 0.90, 1.0)
    COL_TRUCK_CAB  = (0.62, 0.62, 0.64, 1.0)
    COL_TRUCK_DARK = (0.18, 0.18, 0.20, 1.0)
    # Cab (front of truck, facing -X = west)
    _make_box_local("Comm_DeliveryTruck_Cab",
                    (truck_x - 2.5, truck_y, truck_z + 0.40 + 1.20 / 2 + 0.4),
                    (2.6, 2.0, 1.80), COL_TRUCK_CAB)
    # Cab windshield
    _make_box_local("Comm_DeliveryTruck_Windshield",
                    (truck_x - 3.55, truck_y, truck_z + 1.70),
                    (0.40, 1.80, 0.60),
                    (0.18, 0.22, 0.30, 1.0))
    # Cargo box (taller, behind cab)
    _make_box_local("Comm_DeliveryTruck_Cargo",
                    (truck_x + 1.5, truck_y, truck_z + 0.40 + 1.20 / 2 + 1.0),
                    (5.0, 2.4, 2.40), COL_TRUCK_BODY)
    # Roller door on the back (east end of cargo)
    _make_box_local("Comm_DeliveryTruck_RollerDoor",
                    (truck_x + 4.05, truck_y, truck_z + 1.6),
                    (0.06, 2.20, 2.00), COL_TRUCK_DARK)
    # Wheels (6 — front pair on cab, 4 on cargo)
    truck_wheel_h = 0.50
    for wx_off in (-3.4, -1.8, 0.4, 1.4, 2.6, 3.6):
        for wy_sgn in (-1, 1):
            _make_box_local(
                f"Comm_DeliveryTruck_Wheel_{int(wx_off*10):+d}_{wy_sgn:+d}",
                (truck_x + wx_off,
                 truck_y + wy_sgn * 1.0,
                 truck_z + truck_wheel_h / 2),
                (0.50, 0.30, truck_wheel_h),
                COL_TRUCK_DARK)
    # Headlights on the cab front
    for sgn_y in (-1, 1):
        _make_box_local(
            f"Comm_DeliveryTruck_Headlight_{sgn_y:+d}",
            (truck_x - 3.78, truck_y + sgn_y * 0.7, truck_z + 1.1),
            (0.06, 0.30, 0.20),
            (0.98, 0.96, 0.86, 1.0))
    # Delivery crates stacked behind the truck's open roller door
    # (the driver is unloading). 3 crates in a small pile on the
    # asphalt, just north of the truck cargo end.
    crate_x0 = truck_x + 4.5
    crate_y0 = truck_y + 1.4
    crate_z0 = truck_z
    COL_CRATE = (0.62, 0.45, 0.30, 1.0)
    crate_specs = [
        (crate_x0, crate_y0, 0,    0.80, 0.60, 0.55),  # base, big
        (crate_x0 + 0.6, crate_y0 + 0.2, 0, 0.55, 0.50, 0.45),
        (crate_x0, crate_y0, 0.55, 0.60, 0.50, 0.45),  # stacked on first
    ]
    for k, (kx, ky, kz_off, sw, sd, sh) in enumerate(crate_specs):
        _make_box_local(f"Comm_DeliveryCrate_{k}",
                        (kx, ky, crate_z0 + kz_off + sh / 2),
                        (sw, sd, sh), COL_CRATE)

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

    # STOP sign at the crosswalk's west side so eastbound traffic
    # yields to pedestrians.
    stop_x = spur_jog_x - 5.0
    stop_y = road_y + hwr + 1.0
    stop_z = mesh_z(stop_x, stop_y)
    _make_cyl_local("CommRoad_StopPole",
                    (stop_x, stop_y, stop_z + 1.1),
                    0.04, 2.2,
                    (0.62, 0.62, 0.64, 1.0), segments=4)
    # Octagonal-ish stop face — thin axis along X so the sign
    # faces WEST (toward eastbound drivers approaching the
    # crosswalk).
    _make_box_local("CommRoad_StopFace",
                    (stop_x, stop_y, stop_z + 2.20),
                    (0.04, 0.50, 0.50),
                    (0.78, 0.18, 0.18, 1.0))

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


def _build_suburban_house(name, cx, cy, ground_z, facing='-Y',
                           palette=None):
    """Mid-sized single-family suburban house — rectangular
    footprint with pitched gable roof, attached garage, front
    door + porch, two front windows and one over the garage.

    facing: which direction the FRONT (porch + front door) points.
            '-Y' = south, '+Y' = north, '-X' = west, '+X' = east.

    palette: dict with keys 'wall', 'trim', 'roof', 'door',
             'garage_door', 'porch_post'. Defaults to a beige/cream
             palette if not supplied.
    """
    if palette is None:
        palette = {}
    col_wall   = palette.get('wall',   (0.82, 0.78, 0.70, 1.0))
    col_trim   = palette.get('trim',   (0.95, 0.92, 0.86, 1.0))
    col_roof   = palette.get('roof',   (0.42, 0.30, 0.22, 1.0))
    col_door   = palette.get('door',   (0.62, 0.32, 0.22, 1.0))
    col_garage = palette.get('garage_door', (0.95, 0.92, 0.86, 1.0))
    col_post   = palette.get('porch_post', (0.95, 0.92, 0.86, 1.0))
    col_window = palette.get('window', (0.32, 0.42, 0.55, 1.0))

    # Footprint: main house 9 m wide x 7 m deep x 4 m tall + garage
    # 5 m wide x 6 m deep x 3.5 m tall attached to one side
    main_w = 9.0
    main_d = 7.0
    main_h = 4.0
    gar_w  = 5.0
    gar_d  = 6.0
    gar_h  = 3.0

    # The "front" of the house is at -fy from center (facing axis).
    fx, fy = _face_axis(facing)
    # Perpendicular vector (right-hand) so we can place the garage
    # on the house's RIGHT side.
    perp_x = -fy
    perp_y = fx

    # Slab — covers main + garage footprint, centred at (cx, cy).
    # For Y-facing buildings the WIDTH axis (main_w + gar_w) is X
    # and the DEPTH axis is Y; for X-facing the axes swap.
    slab_w = main_w + gar_w + 0.4
    slab_d = max(main_d, gar_d) + 0.4
    if abs(fx) > 0.5:
        # Facing E/W → width axis is Y, depth axis is X
        slab_size = (slab_d, slab_w, 0.10)
    else:
        # Facing N/S → width axis is X, depth axis is Y
        slab_size = (slab_w, slab_d, 0.10)
    _make_box_local(f"{name}_Slab",
                    (cx, cy, ground_z + 0.05),
                    slab_size, col_trim)

    # Main house walls — built as a single box with the front
    # face oriented along facing direction.
    main_cx = cx - perp_x * gar_w / 2
    main_cy = cy - perp_y * gar_w / 2
    if abs(fx) > 0.5:
        # Facing E/W: house long axis is Y, house depth is X
        main_size = (main_d, main_w, main_h)
    else:
        # Facing N/S: house long axis is X, house depth is Y
        main_size = (main_w, main_d, main_h)
    _make_box_local(f"{name}_Main",
                    (main_cx, main_cy, ground_z + main_h / 2),
                    main_size, col_wall)

    # Pitched gable roof — two slanted quads meeting at a ridge
    # along the long axis of the house.
    ridge_h = 1.6
    if abs(fx) > 0.5:
        # Ridge runs Y direction (along long axis of house facing E/W)
        # 4 verts of the eave + 2 verts of the ridge
        rverts = [
            (main_cx - main_d / 2 - 0.20, main_cy - main_w / 2 - 0.20,
             ground_z + main_h),
            (main_cx + main_d / 2 + 0.20, main_cy - main_w / 2 - 0.20,
             ground_z + main_h),
            (main_cx + main_d / 2 + 0.20, main_cy + main_w / 2 + 0.20,
             ground_z + main_h),
            (main_cx - main_d / 2 - 0.20, main_cy + main_w / 2 + 0.20,
             ground_z + main_h),
            (main_cx, main_cy - main_w / 2 - 0.20,
             ground_z + main_h + ridge_h),
            (main_cx, main_cy + main_w / 2 + 0.20,
             ground_z + main_h + ridge_h),
        ]
        rfaces = [
            [0, 1, 5, 4],     # west slope (south end gable underneath)
            [4, 5, 2, 3],     # east slope (north end gable underneath)
            [0, 4, 5, 1],     # gable triangle south? quad — keep planar
        ]
        # Cleanup: real gable roof has two slopes + two triangular
        # gable end walls. Simpler 4-quad approximation: two
        # slopes + a placeholder gable.
        rfaces = [[0, 1, 5, 4], [3, 4, 5, 2]]
        # Two triangular gable ends
        rfaces.append([0, 4, 3])
        rfaces.append([1, 2, 5])
    else:
        rverts = [
            (main_cx - main_w / 2 - 0.20, main_cy - main_d / 2 - 0.20,
             ground_z + main_h),
            (main_cx + main_w / 2 + 0.20, main_cy - main_d / 2 - 0.20,
             ground_z + main_h),
            (main_cx + main_w / 2 + 0.20, main_cy + main_d / 2 + 0.20,
             ground_z + main_h),
            (main_cx - main_w / 2 - 0.20, main_cy + main_d / 2 + 0.20,
             ground_z + main_h),
            (main_cx - main_w / 2 - 0.20, main_cy,
             ground_z + main_h + ridge_h),
            (main_cx + main_w / 2 + 0.20, main_cy,
             ground_z + main_h + ridge_h),
        ]
        rfaces = [[0, 1, 5, 4], [3, 4, 5, 2]]
        rfaces.append([0, 4, 3])
        rfaces.append([1, 2, 5])
    _finalize_mesh(f"{name}_Roof", rverts, rfaces, col_roof)

    # Front door at the front face of the main house, offset
    # toward the garage corner. front_off is always main_d/2
    # because main_d is the depth-along-facing in BOTH axes
    # (the main_size ternary already places main_d on the facing
    # axis). Two front windows on the OPPOSITE side of the door
    # from the garage (so the "living-room" half gets the glass).
    front_off = main_d / 2
    door_perp_off = 1.8         # door pushed toward the garage corner
    door_cx = main_cx + fx * front_off + perp_x * door_perp_off
    door_cy = main_cy + fy * front_off + perp_y * door_perp_off
    _make_box_local(f"{name}_FrontDoor",
                    (door_cx, door_cy, ground_z + 1.05),
                    (0.08 if abs(fx) > 0.5 else 0.90,
                     0.90 if abs(fx) > 0.5 else 0.08,
                     2.10), col_door)
    # Two windows on the front face, both on the NON-garage side
    # of the door (perp negative direction). Spaced -1.6 and -3.4
    # from main_cx so they don't overlap each other or the door.
    for sgn, off in ((-1, -1.6), (-2, -3.4)):
        wx_pos = main_cx + fx * front_off + perp_x * off
        wy_pos = main_cy + fy * front_off + perp_y * off
        _make_box_local(f"{name}_Window_F_{sgn:+d}",
                        (wx_pos, wy_pos, ground_z + 1.50),
                        (0.10 if abs(fx) > 0.5 else 1.2,
                         1.2 if abs(fx) > 0.5 else 0.10,
                         1.0), col_window)

    # Porch — small slab + 2 roof posts in front of the door
    porch_d = 1.2
    porch_cx = door_cx + fx * porch_d / 2
    porch_cy = door_cy + fy * porch_d / 2
    _make_box_local(f"{name}_PorchSlab",
                    (porch_cx, porch_cy, ground_z + 0.10),
                    (2.4 if abs(fx) < 0.5 else porch_d,
                     porch_d if abs(fx) < 0.5 else 2.4,
                     0.20),
                    col_trim)
    # Porch posts
    for sgn in (-1, 1):
        post_x = porch_cx + perp_x * sgn * 1.0 + fx * porch_d / 2
        post_y = porch_cy + perp_y * sgn * 1.0 + fy * porch_d / 2
        _make_box_local(f"{name}_PorchPost_{sgn:+d}",
                        (post_x, post_y, ground_z + 1.40),
                        (0.14, 0.14, 2.60), col_post)
    # Porch roof (flat overhang)
    _make_box_local(f"{name}_PorchRoof",
                    (porch_cx, porch_cy, ground_z + 2.70),
                    (2.6 if abs(fx) < 0.5 else porch_d + 0.20,
                     porch_d + 0.20 if abs(fx) < 0.5 else 2.6,
                     0.12),
                    col_roof)

    # Garage — attached on the +perp side of the main house
    gar_cx = cx + perp_x * (main_w / 2 + gar_w / 2 - gar_w / 2) - perp_x * gar_w / 2
    gar_cx = main_cx + perp_x * (main_w / 2 + gar_w / 2)
    gar_cy = main_cy + perp_y * (main_w / 2 + gar_w / 2)
    if abs(fx) > 0.5:
        gar_size = (gar_d, gar_w, gar_h)
    else:
        gar_size = (gar_w, gar_d, gar_h)
    _make_box_local(f"{name}_Garage",
                    (gar_cx, gar_cy, ground_z + gar_h / 2),
                    gar_size, col_wall)
    # Garage roof (flat)
    _make_box_local(f"{name}_GarageRoof",
                    (gar_cx, gar_cy, ground_z + gar_h + 0.10),
                    (gar_size[0] + 0.20, gar_size[1] + 0.20, 0.20),
                    col_roof)
    # Garage door (front face of garage). gar_d/2 is the depth-
    # along-facing in BOTH X- and Y-facing cases (gar_size puts
    # gar_d on the facing axis).
    gdoor_cx = gar_cx + fx * gar_d / 2
    gdoor_cy = gar_cy + fy * gar_d / 2
    if abs(fx) > 0.5:
        gdoor_size = (0.06, 3.8, 2.2)
    else:
        gdoor_size = (3.8, 0.06, 2.2)
    _make_box_local(f"{name}_GarageDoor",
                    (gdoor_cx, gdoor_cy, ground_z + 1.20),
                    gdoor_size, col_garage)
    # Garage-window strip above the door
    if abs(fx) > 0.5:
        gw_size = (0.04, 3.5, 0.30)
    else:
        gw_size = (3.5, 0.04, 0.30)
    _make_box_local(f"{name}_GarageWindow",
                    (gdoor_cx, gdoor_cy, ground_z + 2.50),
                    gw_size, col_window)


def _build_driveway(name, house_cx, house_cy, ground_z, facing,
                     curb_x, curb_y, color=(0.18, 0.18, 0.20, 1.0)):
    """Asphalt driveway from the front of a house (garage front)
    to a point on the curb. Computed as a quad from the garage
    apron to the curb point, sampling mesh_z at each corner."""
    fx, fy = _face_axis(facing)
    perp_x = -fy
    perp_y = fx
    # Driveway starts at the garage apron — at the garage's
    # front face. Garage centre is offset (main_w/2 + gar_w/2)
    # perp from the house centre, and the garage's front face
    # is gar_d/2 along the facing direction from the garage
    # centre. main_d/2 (3.5) was incorrectly used here for the
    # Y axis, putting the apron 0.5 m past the garage face.
    # Garage centre lives at house_centre + perp * main_w/2 (the
    # builder shifts main_centre by -perp*gar_w/2 and the garage
    # sits +(main_w/2 + gar_w/2) further along perp, so net
    # garage offset is main_w/2). Apron front face is gar_d/2
    # along the facing direction past the garage centre.
    main_w = 9.0
    gar_d = 6.0
    apron_cx = house_cx + perp_x * main_w / 2 + fx * gar_d / 2
    apron_cy = house_cy + perp_y * main_w / 2 + fy * gar_d / 2
    # Driveway is a 3.5 m wide quad from apron to curb
    dw_w = 3.5
    perp_hw = dw_w / 2
    # Compute apron→curb direction
    direction_x = curb_x - apron_cx
    direction_y = curb_y - apron_cy
    dist = math.hypot(direction_x, direction_y) or 1.0
    perp_dx = -direction_y / dist
    perp_dy = direction_x / dist
    corners = [
        (apron_cx - perp_dx * perp_hw, apron_cy - perp_dy * perp_hw),
        (curb_x   - perp_dx * perp_hw, curb_y   - perp_dy * perp_hw),
        (curb_x   + perp_dx * perp_hw, curb_y   + perp_dy * perp_hw),
        (apron_cx + perp_dx * perp_hw, apron_cy + perp_dy * perp_hw),
    ]
    verts = [(vx, vy, mesh_z(vx, vy) + 0.04) for (vx, vy) in corners]
    _finalize_mesh(f"{name}_Driveway", verts, [[0, 1, 2, 3]], color)


def _face_axis(facing):
    """Returns (forward_x, forward_y) unit vector for the given
    facing tag — same convention as human_sculpt._face_axis."""
    if facing == '+X':  return (1.0, 0.0)
    if facing == '-X':  return (-1.0, 0.0)
    if facing == '+Y':  return (0.0, 1.0)
    if facing == '-Y':  return (0.0, -1.0)
    return (0.0, -1.0)


def build_east_commercial_box():
    """Big-box-style shopping pad east of the high school in
    EastComm settlement zone (440..540, -340..260). One large
    department-store box with a flat roof, plus a smaller
    drive-thru fast-food pad to the south.
    """
    # ── DEPT STORE — 60 × 24 × 7 m flat-roof box
    cx, cy = 480.0, 60.0
    ground_z = mesh_z(cx, cy)
    col_db_wall = (0.62, 0.55, 0.50, 1.0)     # warm beige
    col_db_trim = (0.85, 0.20, 0.18, 1.0)     # red accent
    col_db_roof = (0.30, 0.28, 0.26, 1.0)
    col_db_door = (0.18, 0.18, 0.20, 1.0)
    col_db_window = (0.32, 0.42, 0.55, 1.0)
    w, d, h = 60.0, 24.0, 7.0
    t = 0.20
    _make_box_local("EC_DB_Slab",
                    (cx, cy, ground_z + 0.05),
                    (w + 0.6, d + 0.6, 0.10),
                    (0.78, 0.74, 0.66, 1.0))
    # Walls (back + sides solid)
    _make_box_local("EC_DB_WallN",
                    (cx, cy + d / 2 - t / 2,
                     ground_z + h / 2),
                    (w, t, h), col_db_wall)
    _make_box_local("EC_DB_WallE",
                    (cx + w / 2 - t / 2, cy,
                     ground_z + h / 2),
                    (t, d, h), col_db_wall)
    _make_box_local("EC_DB_WallW",
                    (cx - w / 2 + t / 2, cy,
                     ground_z + h / 2),
                    (t, d, h), col_db_wall)
    # South wall — central double-door entry + 4 storefront windows
    dw, dh = 4.0, 3.4
    left_w = w / 2 - dw / 2
    _make_box_local("EC_DB_WallS_L",
                    (cx - dw / 2 - left_w / 2,
                     cy - d / 2 + t / 2,
                     ground_z + h / 2),
                    (left_w, t, h), col_db_wall)
    _make_box_local("EC_DB_WallS_R",
                    (cx + dw / 2 + left_w / 2,
                     cy - d / 2 + t / 2,
                     ground_z + h / 2),
                    (left_w, t, h), col_db_wall)
    _make_box_local("EC_DB_WallS_Header",
                    (cx, cy - d / 2 + t / 2,
                     ground_z + dh + (h - dh) / 2),
                    (dw, t, h - dh), col_db_wall)
    # Double entry doors
    for sgn in (-1, 1):
        _make_box_local(f"EC_DB_Door_{sgn:+d}",
                        (cx + sgn * dw / 4, cy - d / 2 + 0.05,
                         ground_z + dh / 2),
                        (dw / 2 - 0.12, 0.06, dh - 0.10),
                        col_db_door)
    # 4 big front windows
    for sgn in (-1, 1):
        for k in range(2):
            wx = cx + sgn * (dw / 2 + (k + 1) * 6.0)
            if abs(wx) < cx + w / 2 - 3.0:
                _make_box_local(f"EC_DB_Window_{sgn:+d}_{k}",
                                (wx, cy - d / 2 + 0.04,
                                 ground_z + 3.0),
                                (4.0, 0.04, 2.4),
                                col_db_window)
    # Roof + red trim band
    _make_box_local("EC_DB_Roof",
                    (cx, cy, ground_z + h + 0.10),
                    (w + 0.4, d + 0.4, 0.20), col_db_roof)
    _make_box_local("EC_DB_TrimBand",
                    (cx, cy - d / 2 - 0.05,
                     ground_z + h - 0.30),
                    (w + 0.4, 0.10, 0.40), col_db_trim)
    # Big rooftop sign panel
    _make_box_local("EC_DB_SignPanel",
                    (cx, cy - d / 2 - 0.20,
                     ground_z + h + 0.80),
                    (16.0, 0.20, 1.6),
                    (0.85, 0.20, 0.18, 1.0))

    # ── DRIVE-THRU FAST FOOD pad — south of the dept store
    ff_cx = cx
    ff_cy = cy - d / 2 - 30.0
    ff_z = mesh_z(ff_cx, ff_cy)
    fw, fd, fh = 14.0, 10.0, 4.0
    _make_box_local("EC_FF_Slab",
                    (ff_cx, ff_cy, ff_z + 0.05),
                    (fw + 0.4, fd + 0.4, 0.10),
                    (0.78, 0.74, 0.66, 1.0))
    _make_box_local("EC_FF_Walls",
                    (ff_cx, ff_cy, ff_z + fh / 2),
                    (fw, fd, fh),
                    (0.95, 0.45, 0.20, 1.0))     # orange
    _make_box_local("EC_FF_Roof",
                    (ff_cx, ff_cy, ff_z + fh + 0.10),
                    (fw + 0.4, fd + 0.4, 0.20),
                    (0.32, 0.30, 0.28, 1.0))
    # Drive-thru ordering kiosk
    _make_box_local("EC_FF_Kiosk",
                    (ff_cx + fw / 2 + 2.0, ff_cy - 2.0,
                     ff_z + 1.40),
                    (0.60, 1.20, 2.80),
                    (0.32, 0.32, 0.36, 1.0))


def build_drive_in_theatre():
    """Drive-in movie theatre in the open SE wild zone south of
    Phase 2. A big asphalt arc of stalls facing a giant screen,
    plus a tiny concession-stand building.
    """
    cx, cy = 150.0, -300.0
    ground_z = mesh_z(cx, cy)

    # ── SCREEN — massive white panel facing south on a tall
    # support frame. Players parked south of the screen look up
    # at it.
    scr_x, scr_y = cx, cy - 80.0   # 80 m south of stalls' centre
    scr_z = mesh_z(scr_x, scr_y)
    col_screen = (0.95, 0.95, 0.92, 1.0)
    col_screen_frame = (0.18, 0.18, 0.20, 1.0)
    scr_w = 32.0; scr_h = 12.0
    # Frame uprights (left + right of the screen)
    for sgn in (-1, 1):
        _make_cyl_local(f"DI_ScreenLeg_{sgn:+d}",
                        (scr_x + sgn * scr_w / 2, scr_y,
                         scr_z + scr_h / 2),
                        0.25, scr_h, col_screen_frame, segments=4)
    # Cross-brace top
    _make_box_local("DI_ScreenTopBar",
                    (scr_x, scr_y, scr_z + scr_h - 0.10),
                    (scr_w + 0.5, 0.20, 0.20), col_screen_frame)
    # Screen face — thin tall panel
    _make_box_local("DI_ScreenFace",
                    (scr_x, scr_y, scr_z + scr_h / 2 + 1.0),
                    (scr_w, 0.20, scr_h - 1.0), col_screen)

    # ── PARKING ARC — 4 concentric rows of stalls facing the
    # screen. Each row holds 12 cars (small for low-poly).
    n_rows = 4
    row_d = 6.0    # depth between rows
    inner_r = 30.0  # closest row to screen
    n_cars_per_row = 12
    car_palette = [
        (0.85, 0.20, 0.18, 1.0), (0.62, 0.62, 0.64, 1.0),
        (0.18, 0.32, 0.55, 1.0), (0.32, 0.55, 0.25, 1.0),
        (0.20, 0.20, 0.22, 1.0), (0.95, 0.85, 0.30, 1.0),
        (0.78, 0.74, 0.66, 1.0), (0.42, 0.62, 0.32, 1.0),
    ]
    car_idx = 0
    for row in range(n_rows):
        r = inner_r + row * row_d
        for k in range(n_cars_per_row):
            # Spread cars in an arc from -60° to +60° relative
            # to the screen
            ang_deg = -60 + k * (120 / (n_cars_per_row - 1))
            ang = math.radians(ang_deg)
            cpx = scr_x + math.sin(ang) * r
            cpy = scr_y + math.cos(ang) * r
            cpz = mesh_z(cpx, cpy)
            # Cars face TOWARD the screen (south)
            col = car_palette[car_idx % len(car_palette)]
            _build_parked_car(f"DI_Car_{row}_{k}",
                              cpx, cpy, cpz, col, facing='-Y')
            car_idx += 1

    # ── CONCESSION STAND — small building at the back (north of
    # stalls)
    cs_x = cx
    cs_y = cy + 20.0
    cs_z = mesh_z(cs_x, cs_y)
    col_cs_wall = (0.85, 0.82, 0.72, 1.0)
    col_cs_roof = (0.85, 0.20, 0.18, 1.0)
    cs_w, cs_d, cs_h = 12.0, 6.0, 3.5
    _make_box_local("DI_Concession_Walls",
                    (cs_x, cs_y, cs_z + cs_h / 2),
                    (cs_w, cs_d, cs_h), col_cs_wall)
    _make_box_local("DI_Concession_Roof",
                    (cs_x, cs_y, cs_z + cs_h + 0.10),
                    (cs_w + 0.4, cs_d + 0.4, 0.20), col_cs_roof)
    # Walk-up window on the south face
    _make_box_local("DI_Concession_Window",
                    (cs_x, cs_y - cs_d / 2 + 0.04,
                     cs_z + 1.6),
                    (4.0, 0.04, 1.4), (0.32, 0.42, 0.55, 1.0))


def build_hospital():
    """Harmony Creek Hospital — civic hospital in NorthComm east
    of NexCorp HQ. 36 × 16 × 11 m three-story building with a
    large red CROSS sign on the south facade and an ambulance
    bay on the east end.
    """
    cx, cy = 180.0, 300.0
    ground_z = mesh_z(cx, cy)
    col_wall = (0.92, 0.92, 0.90, 1.0)
    col_trim = (0.62, 0.62, 0.64, 1.0)
    col_roof = (0.32, 0.32, 0.35, 1.0)
    col_cross = (0.85, 0.20, 0.18, 1.0)
    col_glass = (0.32, 0.42, 0.55, 1.0)
    col_door = (0.18, 0.32, 0.55, 1.0)
    w, d, h = 36.0, 16.0, 11.0
    t = 0.20
    _make_box_local("Hos_Slab",
                    (cx, cy, ground_z + 0.05),
                    (w + 0.4, d + 0.4, 0.10), col_trim)
    _make_box_local("Hos_WallN",
                    (cx, cy + d / 2 - t / 2, ground_z + h / 2),
                    (w, t, h), col_wall)
    _make_box_local("Hos_WallE",
                    (cx + w / 2 - t / 2, cy, ground_z + h / 2),
                    (t, d, h), col_wall)
    _make_box_local("Hos_WallW",
                    (cx - w / 2 + t / 2, cy, ground_z + h / 2),
                    (t, d, h), col_wall)
    # South face split for main entry
    dw, dh = 3.5, 3.4
    left_w = w / 2 - dw / 2
    _make_box_local("Hos_WallS_L",
                    (cx - dw / 2 - left_w / 2,
                     cy - d / 2 + t / 2, ground_z + h / 2),
                    (left_w, t, h), col_wall)
    _make_box_local("Hos_WallS_R",
                    (cx + dw / 2 + left_w / 2,
                     cy - d / 2 + t / 2, ground_z + h / 2),
                    (left_w, t, h), col_wall)
    _make_box_local("Hos_WallS_Header",
                    (cx, cy - d / 2 + t / 2,
                     ground_z + dh + (h - dh) / 2),
                    (dw, t, h - dh), col_wall)
    # Main entrance double-door
    for sgn in (-1, 1):
        _make_box_local(f"Hos_Door_{sgn:+d}",
                        (cx + sgn * dw / 4,
                         cy - d / 2 + 0.05, ground_z + dh / 2),
                        (dw / 2 - 0.12, 0.06, dh - 0.10), col_door)
    # 3 rows of 6 windows on the south face (story heights at
    # 3.7 m apart)
    for story in range(3):
        z_win = ground_z + 1.8 + story * 3.7
        for sgn in (-1, 1):
            for k in range(3):
                wx = cx + sgn * (dw / 2 + (k + 1) * 4.0)
                if abs(wx - cx) < w / 2 - 1.5:
                    _make_box_local(
                        f"Hos_Window_{story}_{sgn:+d}_{k}",
                        (wx, cy - d / 2 + 0.04, z_win),
                        (2.4, 0.04, 1.6), col_glass)
    # Roof + parapet
    _make_box_local("Hos_Roof",
                    (cx, cy, ground_z + h + 0.10),
                    (w + 0.4, d + 0.4, 0.20), col_roof)
    parapet_h = 0.80
    for sgn_y, tag in ((-1, 'S'), (1, 'N')):
        _make_box_local(f"Hos_Parapet_{tag}",
                        (cx, cy + sgn_y * (d + 0.4) / 2,
                         ground_z + h + 0.20 + parapet_h / 2),
                        (w + 0.4, 0.20, parapet_h), col_trim)
    # Big RED CROSS sign on the south facade (above the entry)
    _make_box_local("Hos_CrossBg",
                    (cx, cy - d / 2 - 0.18,
                     ground_z + h - 1.6),
                    (2.6, 0.14, 2.6), (0.95, 0.94, 0.90, 1.0))
    _make_box_local("Hos_Cross_V",
                    (cx, cy - d / 2 - 0.25,
                     ground_z + h - 1.6),
                    (0.50, 0.08, 2.2), col_cross)
    _make_box_local("Hos_Cross_H",
                    (cx, cy - d / 2 - 0.25,
                     ground_z + h - 1.6),
                    (2.2, 0.08, 0.50), col_cross)

    # ── AMBULANCE BAY · covered drive-through on the east end
    bay_cx = cx + w / 2 + 8.0
    bay_cy = cy
    bay_z = mesh_z(bay_cx, bay_cy)
    bay_w = 12.0; bay_d = 8.0; bay_h = 4.5
    for sgn_x in (-1, 1):
        for sgn_y in (-1, 1):
            _make_cyl_local(
                f"Hos_BayCol_{sgn_x:+d}_{sgn_y:+d}",
                (bay_cx + sgn_x * (bay_w / 2 - 0.30),
                 bay_cy + sgn_y * (bay_d / 2 - 0.30),
                 bay_z + bay_h / 2),
                0.20, bay_h, col_trim, segments=6)
    _make_box_local("Hos_BayRoof",
                    (bay_cx, bay_cy, bay_z + bay_h + 0.15),
                    (bay_w + 0.6, bay_d + 0.6, 0.30),
                    col_door)      # blue ambulance-bay roof
    # AMBULANCE — a small box truck parked under the bay
    ambo_x = bay_cx
    ambo_y = bay_cy
    ambo_z = mesh_z(ambo_x, ambo_y)
    _make_box_local("Hos_Ambulance_Cab",
                    (ambo_x - 2.0, ambo_y, ambo_z + 1.2),
                    (2.4, 2.0, 1.8), (0.95, 0.94, 0.90, 1.0))
    _make_box_local("Hos_Ambulance_Box",
                    (ambo_x + 1.5, ambo_y, ambo_z + 1.4),
                    (4.0, 2.2, 2.4), (0.95, 0.94, 0.90, 1.0))
    # Red cross on the ambulance side
    _make_box_local("Hos_Ambulance_RedCross_V",
                    (ambo_x + 1.5, ambo_y - 1.12,
                     ambo_z + 1.4),
                    (0.20, 0.04, 1.0), col_cross)
    _make_box_local("Hos_Ambulance_RedCross_H",
                    (ambo_x + 1.5, ambo_y - 1.12,
                     ambo_z + 1.4),
                    (1.0, 0.04, 0.20), col_cross)


def build_halsey_studios():
    """Halsey Studios — music recording studio referenced in
    lore/_HCE_PROJECT_NOTES.md ("recording booth window probably
    visible"). 18 × 14 × 4.5 m brick + black box with a big
    plate-glass recording-booth window on the south face.
    Positioned in EastComm just south of the high school.
    """
    cx, cy = 480.0, -100.0
    ground_z = mesh_z(cx, cy)
    col_wall = (0.18, 0.18, 0.22, 1.0)        # near-black studio walls
    col_trim = (0.62, 0.42, 0.28, 1.0)         # warm wood trim
    col_window = (0.32, 0.42, 0.55, 1.0)       # tinted control glass
    col_door = (0.85, 0.20, 0.18, 1.0)
    col_roof = (0.12, 0.12, 0.14, 1.0)
    w, d, h = 18.0, 14.0, 4.5
    t = 0.20
    _make_box_local("HS_Studio_Slab",
                    (cx, cy, ground_z + 0.05),
                    (w + 0.4, d + 0.4, 0.10), col_trim)
    _make_box_local("HS_Studio_WallN",
                    (cx, cy + d / 2 - t / 2, ground_z + h / 2),
                    (w, t, h), col_wall)
    _make_box_local("HS_Studio_WallE",
                    (cx + w / 2 - t / 2, cy, ground_z + h / 2),
                    (t, d, h), col_wall)
    _make_box_local("HS_Studio_WallW",
                    (cx - w / 2 + t / 2, cy, ground_z + h / 2),
                    (t, d, h), col_wall)
    # South wall — big recording-booth window on the right,
    # entry door on the left.
    win_w = 7.0; win_h = 2.4
    dr_w = 1.4; dr_h = 2.4
    # The south face has, left-to-right:
    #   side wall L (3 m) | door | side wall mid (3 m) | window |
    #   side wall R (2 m)
    side_l = 3.0
    mid_w = 3.0
    side_r = w - (side_l + dr_w + mid_w + win_w)
    if side_r < 0.5:
        side_r = 0.5
        mid_w = w - (side_l + dr_w + win_w + side_r)
    _make_box_local("HS_Studio_WallS_L",
                    (cx - w / 2 + side_l / 2,
                     cy - d / 2 + t / 2, ground_z + h / 2),
                    (side_l, t, h), col_wall)
    # Door
    _make_box_local("HS_Studio_Door",
                    (cx - w / 2 + side_l + dr_w / 2,
                     cy - d / 2 + 0.05, ground_z + dr_h / 2),
                    (dr_w, 0.06, dr_h - 0.10), col_door)
    # Door header
    _make_box_local("HS_Studio_DoorHeader",
                    (cx - w / 2 + side_l + dr_w / 2,
                     cy - d / 2 + t / 2,
                     ground_z + dr_h + (h - dr_h) / 2),
                    (dr_w, t, h - dr_h), col_wall)
    # Mid wall (between door and window)
    _make_box_local("HS_Studio_WallS_Mid",
                    (cx - w / 2 + side_l + dr_w + mid_w / 2,
                     cy - d / 2 + t / 2, ground_z + h / 2),
                    (mid_w, t, h), col_wall)
    # The big window — wide pane of tinted glass + wood trim
    win_cx = cx - w / 2 + side_l + dr_w + mid_w + win_w / 2
    _make_box_local("HS_Studio_Window",
                    (win_cx, cy - d / 2 + 0.04,
                     ground_z + 1.6),
                    (win_w, 0.04, win_h), col_window)
    # Window header + sill
    _make_box_local("HS_Studio_WindowHeader",
                    (win_cx, cy - d / 2 + t / 2,
                     ground_z + 1.6 + win_h / 2 +
                     (h - 1.6 - win_h / 2) / 2),
                    (win_w, t,
                     h - 1.6 - win_h / 2), col_wall)
    _make_box_local("HS_Studio_WindowSill",
                    (win_cx, cy - d / 2 + t / 2,
                     ground_z + (1.6 - win_h / 2) / 2),
                    (win_w, t, 1.6 - win_h / 2), col_wall)
    # Right side wall (east of window)
    _make_box_local("HS_Studio_WallS_R",
                    (cx + w / 2 - side_r / 2,
                     cy - d / 2 + t / 2, ground_z + h / 2),
                    (side_r, t, h), col_wall)
    # Roof
    _make_box_local("HS_Studio_Roof",
                    (cx, cy, ground_z + h + 0.10),
                    (w + 0.4, d + 0.4, 0.20), col_roof)
    # SIGN above the entry — a sideways wooden plank
    _make_box_local("HS_Studio_Sign",
                    (cx - w / 2 + side_l + dr_w / 2,
                     cy - d / 2 - 0.18,
                     ground_z + h + 0.4),
                    (4.0, 0.14, 0.80), col_trim)

    # ── PARKING LOT in front
    _build_parking_lot("HalseyStudios", cx, cy - 18.0,
                        lot_w=22.0, lot_d=20.0,
                        ground_z=mesh_z(cx, cy - 18.0),
                        building_y_north=cy,
                        car_palette=[(0.85, 0.20, 0.18, 1.0),
                                      (0.20, 0.20, 0.22, 1.0),
                                      (0.62, 0.62, 0.64, 1.0),
                                      (0.32, 0.42, 0.55, 1.0)],
                        n_handicap=1)


def build_water_tower_and_lines():
    """High-visibility infrastructure landmarks:
      · WATER TOWER on the country-club hilltop just east of
        spawn, visible across the district
      · 3 HIGH-VOLTAGE TRANSMISSION TOWERS running west-east
        through the south side of HCE (parallel to but well
        south of Horizon Drive)
    """
    # ── WATER TOWER at (220, 380) — east of spawn on CC hilltop
    wt_x, wt_y = 220.0, 380.0
    wt_z = mesh_z(wt_x, wt_y)
    col_steel = (0.62, 0.62, 0.64, 1.0)
    col_tank = (0.85, 0.85, 0.82, 1.0)
    # Three support legs splayed outward, 22 m tall
    leg_h = 22.0
    leg_r = 5.0
    for k, ang_deg in enumerate((0, 120, 240)):
        ang = math.radians(ang_deg)
        lx = wt_x + math.cos(ang) * leg_r
        ly = wt_y + math.sin(ang) * leg_r
        # Tilt-approximated as a vertical pole at the splayed
        # foot (true tilt would need oriented cyl)
        _make_cyl_local(f"WT_Leg_{k}",
                        (lx, ly, wt_z + leg_h / 2),
                        0.18, leg_h, col_steel, segments=4)
    # Central vertical pole going up to the tank
    _make_cyl_local("WT_CenterPole",
                    (wt_x, wt_y, wt_z + leg_h / 2),
                    0.22, leg_h, col_steel, segments=6)
    # Cross-bracing — 3 horizontal rings at heights 6 m, 12 m,
    # 18 m. Approximated as flat ring boxes around the centre.
    for ring_z in (6.0, 12.0, 18.0):
        _make_box_local(f"WT_BraceRing_{int(ring_z)}",
                        (wt_x, wt_y, wt_z + ring_z),
                        (leg_r * 2 + 0.4, 0.10, 0.10), col_steel)
        _make_box_local(f"WT_BraceRing_{int(ring_z)}_Y",
                        (wt_x, wt_y, wt_z + ring_z),
                        (0.10, leg_r * 2 + 0.4, 0.10), col_steel)
    # The tank itself — squat cylinder atop the central pole
    tank_h = 8.0
    tank_r = 5.5
    _make_cyl_local("WT_Tank",
                    (wt_x, wt_y, wt_z + leg_h + tank_h / 2),
                    tank_r, tank_h, col_tank, segments=12)
    # Conical top approximated as a smaller cylinder
    _make_cyl_local("WT_TankTop",
                    (wt_x, wt_y, wt_z + leg_h + tank_h + 0.5),
                    tank_r * 0.8, 1.0, col_tank, segments=12)
    # Red beacon on top
    _make_box_local("WT_Beacon",
                    (wt_x, wt_y, wt_z + leg_h + tank_h + 1.3),
                    (0.40, 0.40, 0.40),
                    (0.85, 0.20, 0.18, 1.0))

    # ── 3 TRANSMISSION TOWERS — power lines crossing south HCE
    tt_specs = [
        ("PL_TwrW", -350, -290),
        ("PL_TwrM",    0, -300),
        ("PL_TwrE",  350, -290),
    ]
    col_pylon = (0.42, 0.42, 0.45, 1.0)
    pylon_h = 28.0
    pylon_base_w = 7.0
    pylon_top_w = 2.0
    pylon_pts = []
    for tag, tx, ty in tt_specs:
        tz = mesh_z(tx, ty)
        # 4 corner legs going from splayed base to narrow top
        # Approximate the lattice as a single vertical box and
        # decorative crossbars.
        _make_box_local(f"{tag}_Body",
                        (tx, ty, tz + pylon_h / 2),
                        (pylon_top_w, pylon_top_w, pylon_h),
                        col_pylon)
        # Splay legs at base
        for sgn_x in (-1, 1):
            for sgn_y in (-1, 1):
                _make_box_local(
                    f"{tag}_Leg_{sgn_x:+d}_{sgn_y:+d}",
                    (tx + sgn_x * pylon_base_w / 2,
                     ty + sgn_y * pylon_base_w / 2,
                     tz + pylon_h * 0.30 / 2),
                    (0.30, 0.30, pylon_h * 0.30),
                    col_pylon)
        # Crossarm at the TOP carrying 3 wire mounts
        _make_box_local(f"{tag}_Crossarm",
                        (tx, ty, tz + pylon_h - 1.0),
                        (10.0, 0.30, 0.30), col_pylon)
        # 3 insulator stubs hanging from the crossarm
        for k_ins, dx in enumerate((-4.0, 0.0, 4.0)):
            _make_cyl_local(f"{tag}_Insulator_{k_ins}",
                            (tx + dx, ty, tz + pylon_h - 1.6),
                            0.10, 1.0,
                            (0.88, 0.84, 0.72, 1.0), segments=4)
        pylon_pts.append((tx, ty, tz + pylon_h - 2.6))

    # Wires between consecutive towers (3 wires per span, one
    # per insulator position)
    for k in range(len(pylon_pts) - 1):
        x0, y0, z0 = pylon_pts[k]
        x1, y1, z1 = pylon_pts[k + 1]
        for offx in (-4.0, 0.0, 4.0):
            mid_x = (x0 + x1) / 2 + offx
            mid_y = (y0 + y1) / 2
            mid_z = (z0 + z1) / 2 - 2.0     # sag
            _build_oriented_handle(
                f"PL_Wire_{k}_{int(offx)}_A",
                (x0 + offx, y0, z0),
                (mid_x, mid_y, mid_z),
                radius=0.05, color=(0.08, 0.08, 0.08, 1.0))
            _build_oriented_handle(
                f"PL_Wire_{k}_{int(offx)}_B",
                (mid_x, mid_y, mid_z),
                (x1 + offx, y1, z1),
                radius=0.05, color=(0.08, 0.08, 0.08, 1.0))


def build_church_cemetery():
    """Small graveyard beside the church on Harmony Boulevard.
    24 headstones in a regular grid, a wrought-iron fence
    around the perimeter, and one larger family monument."""
    # Cemetery east of the church at (-30, 140)
    cm_cx = -30.0 + 15.0   # east of church
    cm_cy = 140.0
    cm_z = mesh_z(cm_cx, cm_cy)
    cm_w = 22.0
    cm_d = 28.0
    col_ground = (0.30, 0.42, 0.20, 1.0)
    col_path = (0.78, 0.74, 0.66, 1.0)
    col_stone = (0.62, 0.58, 0.52, 1.0)
    col_dark = (0.42, 0.40, 0.38, 1.0)
    # Ground patch (slightly darker grass)
    _make_box_local("Cm_Ground",
                    (cm_cx, cm_cy, cm_z + 0.02),
                    (cm_w, cm_d, 0.04), col_ground)
    # Central path along x = cm_cx
    _make_box_local("Cm_Path",
                    (cm_cx, cm_cy, cm_z + 0.03),
                    (1.4, cm_d - 1.0, 0.02), col_path)
    # 24 headstones in 4 rows × 6 columns, skipping the central
    # path column
    for row in range(4):
        for col in range(6):
            # Path is between cols 2 and 3 — skip
            if col == 2:
                continue
            hx = cm_cx - cm_w / 2 + 2.0 + col * 3.5
            hy = cm_cy - cm_d / 2 + 3.0 + row * 6.0
            hz = mesh_z(hx, hy)
            stone_w = 0.50
            stone_d = 0.18
            stone_h = 0.80
            # Some headstones are SLABS, some are CROSSES — alternate
            if (row + col) % 3 == 0:
                # Cross stone (vertical bar + horizontal bar)
                _make_box_local(f"Cm_Cross_V_{row}_{col}",
                                (hx, hy, hz + stone_h / 2),
                                (0.08, stone_d, stone_h), col_stone)
                _make_box_local(f"Cm_Cross_H_{row}_{col}",
                                (hx, hy, hz + stone_h - 0.20),
                                (0.40, stone_d, 0.08), col_stone)
            else:
                _make_box_local(f"Cm_Stone_{row}_{col}",
                                (hx, hy, hz + stone_h / 2),
                                (stone_w, stone_d, stone_h),
                                col_stone)
                # Engraved name plaque (darker thin box on front)
                _make_box_local(f"Cm_StonePlaque_{row}_{col}",
                                (hx, hy - stone_d / 2 - 0.005,
                                 hz + stone_h * 0.55),
                                (stone_w * 0.7, 0.01, stone_h * 0.4),
                                col_dark)
    # Larger family monument at the back centre
    mm_x = cm_cx
    mm_y = cm_cy + cm_d / 2 - 3.0
    mm_z = mesh_z(mm_x, mm_y)
    _make_box_local("Cm_Monument_Base",
                    (mm_x, mm_y, mm_z + 0.30),
                    (1.6, 1.0, 0.60), col_stone)
    _make_box_local("Cm_Monument_Column",
                    (mm_x, mm_y, mm_z + 1.40),
                    (0.80, 0.80, 1.60), col_stone)
    _make_box_local("Cm_Monument_Cap",
                    (mm_x, mm_y, mm_z + 2.30),
                    (1.0, 1.0, 0.20), col_stone)
    # Iron fence corner posts (4)
    for sgn_x in (-1, 1):
        for sgn_y in (-1, 1):
            fx = cm_cx + sgn_x * (cm_w / 2 + 0.2)
            fy = cm_cy + sgn_y * (cm_d / 2 + 0.2)
            fz = mesh_z(fx, fy)
            _make_box_local(
                f"Cm_FencePost_{sgn_x:+d}_{sgn_y:+d}",
                (fx, fy, fz + 1.0),
                (0.20, 0.20, 2.0), col_dark)
    # Front gate at the south side (cm_cy - cm_d/2)
    for sgn in (-1, 1):
        _make_box_local(f"Cm_GatePost_{sgn:+d}",
                        (cm_cx + sgn * 1.0,
                         cm_cy - cm_d / 2 - 0.20,
                         mesh_z(cm_cx + sgn * 1.0,
                                cm_cy - cm_d / 2 - 0.20) + 1.4),
                        (0.30, 0.30, 2.8), col_dark)
    # Arched top connecting the gate posts (just a flat box)
    _make_box_local("Cm_GateArch",
                    (cm_cx, cm_cy - cm_d / 2 - 0.20,
                     mesh_z(cm_cx, cm_cy - cm_d / 2 - 0.20) + 2.7),
                    (2.5, 0.20, 0.30), col_dark)


def build_arterial_sidewalks():
    """Concrete sidewalks on both sides of Harmony Blvd and
    Horizon Drive. Each sidewalk is a 2.4 m wide concrete band
    1.5 m outside the road edge (between road and the
    streetlamp line at 5 m).
    """
    COL_SIDEWALK = (0.78, 0.76, 0.72, 1.0)
    sw_w = 2.4
    sw_outer_off = 4.0 + 1.2 + sw_w / 2   # ~ 6.4 m from centerline

    def _emit_sidewalk(pts, prefix):
        for sgn in (-1, 1):
            for i in range(len(pts) - 1):
                x0, y0 = pts[i]
                x1, y1 = pts[i + 1]
                dxs = x1 - x0; dys = y1 - y0
                seg_len = math.hypot(dxs, dys) or 1.0
                perp_x = -dys / seg_len
                perp_y =  dxs / seg_len
                pv = []
                for (px, py) in [
                    (x0 + sgn * perp_x * (sw_outer_off - sw_w / 2),
                     y0 + sgn * perp_y * (sw_outer_off - sw_w / 2)),
                    (x1 + sgn * perp_x * (sw_outer_off - sw_w / 2),
                     y1 + sgn * perp_y * (sw_outer_off - sw_w / 2)),
                    (x1 + sgn * perp_x * (sw_outer_off + sw_w / 2),
                     y1 + sgn * perp_y * (sw_outer_off + sw_w / 2)),
                    (x0 + sgn * perp_x * (sw_outer_off + sw_w / 2),
                     y0 + sgn * perp_y * (sw_outer_off + sw_w / 2)),
                ]:
                    pv.append((px, py, mesh_z(px, py) + 0.06))
                _finalize_mesh(f"{prefix}Sidewalk_{i}_{sgn:+d}", pv,
                                [[0, 1, 2, 3]], COL_SIDEWALK)

    harmony_blvd = [
        (0, 340), (10, 260), (30, 200), (60, 130),
        (60, 10), (40, -80), (20, -180), (10, -260), (0, -340),
    ]
    horizon_dr = [
        (-460, -20), (-380, -10), (-280, -10), (-180, -20),
        (-80, -30), (60, -20), (160, -10), (260, -10),
        (380, 0), (440, 0),
    ]
    _emit_sidewalk(harmony_blvd, "HarmonyBlvd_")
    _emit_sidewalk(horizon_dr, "HorizonDr_")


def build_arterial_lighting():
    """Streetlamps along Harmony Blvd and Horizon Drive at ~40 m
    spacing, alternating sides. Tall (6 m) suburban-arterial
    style with a steel pole and a small overhanging luminaire.
    """
    COL_LAMP_POLE = (0.32, 0.32, 0.34, 1.0)
    COL_LAMP_HEAD = (0.95, 0.92, 0.78, 1.0)
    LAMP_H = 6.0

    def _emit_lamps(pts, prefix, spacing=40.0):
        # Walk along the polyline at spacing intervals
        accumulated = 0.0
        next_lamp = spacing / 2     # first lamp at half-spacing in
        side_sgn = 1
        for i in range(len(pts) - 1):
            x0, y0 = pts[i]
            x1, y1 = pts[i + 1]
            seg_len = math.hypot(x1 - x0, y1 - y0) or 1.0
            seg_end = accumulated + seg_len
            while next_lamp < seg_end:
                t = (next_lamp - accumulated) / seg_len
                # Position along the centerline
                mx = x0 + (x1 - x0) * t
                my = y0 + (y1 - y0) * t
                # Move out perpendicular for the lamp pole
                dxs = x1 - x0; dys = y1 - y0
                perp_x = -dys / seg_len
                perp_y =  dxs / seg_len
                lamp_x = mx + side_sgn * perp_x * 5.0
                lamp_y = my + side_sgn * perp_y * 5.0
                lz = mesh_z(lamp_x, lamp_y)
                # Pole
                _make_cyl_local(f"{prefix}Lamp_Pole_{int(next_lamp)}",
                                (lamp_x, lamp_y, lz + LAMP_H / 2),
                                0.08, LAMP_H, COL_LAMP_POLE, segments=6)
                # Curved head (just a horizontal bar + light box)
                _make_box_local(f"{prefix}Lamp_Arm_{int(next_lamp)}",
                                (lamp_x - side_sgn * perp_x * 0.5,
                                 lamp_y - side_sgn * perp_y * 0.5,
                                 lz + LAMP_H + 0.05),
                                (1.2, 0.06, 0.06), COL_LAMP_POLE)
                _make_box_local(f"{prefix}Lamp_Head_{int(next_lamp)}",
                                (lamp_x - side_sgn * perp_x * 1.0,
                                 lamp_y - side_sgn * perp_y * 1.0,
                                 lz + LAMP_H - 0.10),
                                (0.40, 0.18, 0.18), COL_LAMP_HEAD)
                side_sgn = -side_sgn
                next_lamp += spacing
            accumulated = seg_end

    # Use the same arterial polylines (re-listed here for clarity)
    harmony_blvd = [
        (0, 340), (10, 260), (30, 200), (60, 130),
        (60, 10), (40, -80), (20, -180), (10, -260), (0, -340),
    ]
    horizon_dr = [
        (-460, -20), (-380, -10), (-280, -10), (-180, -20),
        (-80, -30), (60, -20), (160, -10), (260, -10),
        (380, 0), (440, 0),
    ]
    _emit_lamps(harmony_blvd, "HarmonyBlvd_")
    _emit_lamps(horizon_dr, "HorizonDr_")


def build_bus_stops():
    """Bus-stop shelters at key arterial intersections. Each:
    4 corner steel posts + slanted roof + back wall + bench.
    """
    bus_specs = [
        # (name, cx, cy)
        ("HarmonyBlvd_HS",   65, 60),       # Harmony Blvd at HS entry
        ("HarmonyBlvd_OT",   30, 130),      # near OT Park
        ("HorizonDr_Mid",    65, -28),      # Harmony/Horizon junction
        ("HorizonDr_WE",   -440, -28),     # West Estates link
        ("HorizonDr_ECDS",   260, -28),     # East CDS link
    ]
    COL_BUS_STEEL = (0.62, 0.62, 0.64, 1.0)
    COL_BUS_ROOF = (0.32, 0.42, 0.55, 1.0)
    COL_BUS_BACK = (0.85, 0.82, 0.74, 1.0)
    for tag, cx, cy in bus_specs:
        gz = mesh_z(cx, cy)
        bus_w, bus_d, bus_h = 4.0, 1.6, 2.40
        for sgn_x in (-1, 1):
            for sgn_y in (-1, 1):
                _make_box_local(
                    f"BusStop_{tag}_Post_{sgn_x:+d}_{sgn_y:+d}",
                    (cx + sgn_x * (bus_w / 2 - 0.05),
                     cy + sgn_y * (bus_d / 2 - 0.05),
                     gz + bus_h / 2),
                    (0.10, 0.10, bus_h), COL_BUS_STEEL)
        # Back wall (north)
        _make_box_local(f"BusStop_{tag}_BackWall",
                        (cx, cy + bus_d / 2 - 0.05,
                         gz + bus_h * 0.55),
                        (bus_w - 0.10, 0.08, bus_h * 0.85),
                        COL_BUS_BACK)
        # Slanted roof
        roof_verts = [
            (cx - bus_w / 2 - 0.10, cy - bus_d / 2,
             gz + bus_h - 0.10),
            (cx + bus_w / 2 + 0.10, cy - bus_d / 2,
             gz + bus_h - 0.10),
            (cx + bus_w / 2 + 0.10, cy + bus_d / 2 + 0.10,
             gz + bus_h + 0.10),
            (cx - bus_w / 2 - 0.10, cy + bus_d / 2 + 0.10,
             gz + bus_h + 0.10),
        ]
        _finalize_mesh(f"BusStop_{tag}_Roof", roof_verts,
                       [[0, 1, 2, 3]], COL_BUS_ROOF)
        # Bench inside
        _make_box_local(f"BusStop_{tag}_Bench",
                        (cx, cy + bus_d / 4, gz + 0.42),
                        (bus_w - 0.30, 0.40, 0.06),
                        (0.42, 0.30, 0.20, 1.0))


def build_truck_stop():
    """Big-rig truck stop east of the chapter-one commercial
    cluster in the SouthComm settlement zone. Large fuelling
    canopy spanning multiple lanes, a repair-shop building, and
    a big asphalt lot with truck-sized stalls (no cars — just
    the asphalt + striping).
    """
    cx, cy = 200.0, -380.0
    ground_z = mesh_z(cx, cy)

    # ── BIG REPAIR GARAGE — 30 × 12 × 6.5 m
    col_g_wall = (0.62, 0.55, 0.45, 1.0)
    col_g_door = (0.85, 0.82, 0.74, 1.0)
    col_g_roof = (0.32, 0.30, 0.28, 1.0)
    col_g_trim = (0.18, 0.18, 0.20, 1.0)
    g_w, g_d, g_h = 30.0, 12.0, 6.5
    g_t = 0.20
    _make_box_local("TS_Garage_Slab",
                    (cx, cy + 14.0, ground_z + 0.05),
                    (g_w + 0.4, g_d + 0.4, 0.10), col_g_trim)
    _make_box_local("TS_Garage_WallN",
                    (cx, cy + 14.0 + g_d / 2 - g_t / 2,
                     ground_z + g_h / 2),
                    (g_w, g_t, g_h), col_g_wall)
    _make_box_local("TS_Garage_WallE",
                    (cx + g_w / 2 - g_t / 2, cy + 14.0,
                     ground_z + g_h / 2),
                    (g_t, g_d, g_h), col_g_wall)
    _make_box_local("TS_Garage_WallW",
                    (cx - g_w / 2 + g_t / 2, cy + 14.0,
                     ground_z + g_h / 2),
                    (g_t, g_d, g_h), col_g_wall)
    # South wall — three BIG roll-up doors
    bay_w = 6.0; bay_h = 5.0
    bay_span = 3 * bay_w + 2 * 0.5
    side_w = (g_w - bay_span) / 2
    _make_box_local("TS_Garage_WallS_L",
                    (cx - bay_span / 2 - side_w / 2,
                     cy + 14.0 - g_d / 2 + g_t / 2,
                     ground_z + g_h / 2),
                    (side_w, g_t, g_h), col_g_wall)
    _make_box_local("TS_Garage_WallS_R",
                    (cx + bay_span / 2 + side_w / 2,
                     cy + 14.0 - g_d / 2 + g_t / 2,
                     ground_z + g_h / 2),
                    (side_w, g_t, g_h), col_g_wall)
    _make_box_local("TS_Garage_WallS_Header",
                    (cx, cy + 14.0 - g_d / 2 + g_t / 2,
                     ground_z + bay_h + (g_h - bay_h) / 2),
                    (bay_span, g_t, g_h - bay_h), col_g_wall)
    # 3 garage doors
    for k in range(3):
        bx = cx - bay_span / 2 + (k + 0.5) * (bay_w + 0.5)
        _make_box_local(f"TS_Garage_BayDoor_{k}",
                        (bx, cy + 14.0 - g_d / 2 + 0.05,
                         ground_z + bay_h / 2),
                        (bay_w, 0.06, bay_h), col_g_door)
    _make_box_local("TS_Garage_Roof",
                    (cx, cy + 14.0, ground_z + g_h + 0.10),
                    (g_w + 0.4, g_d + 0.4, 0.20), col_g_roof)

    # ── FUELLING CANOPY · big steel structure with 6 lanes
    can_cx = cx
    can_cy = cy - 8.0
    can_w = 36.0
    can_d = 14.0
    can_h = 6.5
    COL_CAN_STEEL = (0.92, 0.92, 0.90, 1.0)
    COL_CAN_ROOF = (0.32, 0.42, 0.55, 1.0)
    # 8 columns (2 rows x 4 columns)
    for ix in (-can_w/2 + 0.5, -can_w/4, can_w/4, can_w/2 - 0.5):
        for iy in (-can_d/2 + 0.5, can_d/2 - 0.5):
            _make_cyl_local(
                f"TS_CanopyCol_{int(ix*10)}_{int(iy*10)}",
                (can_cx + ix, can_cy + iy,
                 ground_z + can_h / 2),
                0.22, can_h, COL_CAN_STEEL, segments=6)
    # Canopy slab
    _make_box_local("TS_CanopyRoof",
                    (can_cx, can_cy, ground_z + can_h + 0.20),
                    (can_w + 0.6, can_d + 0.6, 0.40),
                    COL_CAN_ROOF)
    # 3 pump islands under the canopy
    for k, ix in enumerate((-can_w/4, 0, can_w/4)):
        _make_box_local(f"TS_PumpPad_{k}",
                        (can_cx + ix, can_cy, ground_z + 0.10),
                        (1.8, 8.0, 0.20),
                        (0.72, 0.70, 0.66, 1.0))
        # 2 pumps per island
        for sgn_y, tag_y in ((-1, "S"), (1, "N")):
            _make_box_local(f"TS_PumpBody_{k}_{tag_y}",
                            (can_cx + ix, can_cy + sgn_y * 2.0,
                             ground_z + 1.10),
                            (0.80, 0.50, 1.80),
                            (0.95, 0.94, 0.90, 1.0))
            _make_box_local(f"TS_PumpDisplay_{k}_{tag_y}",
                            (can_cx + ix, can_cy + sgn_y * 2.0,
                             ground_z + 2.15),
                            (0.70, 0.42, 0.30),
                            (0.20, 0.22, 0.28, 1.0))

    # ── BIG ASPHALT TRUCK LOT south of the canopy
    lot_cy = cy - 28.0
    lot_w = 50.0
    lot_d = 14.0
    sv = []
    for (lx, ly) in [(cx - lot_w/2, lot_cy - lot_d/2),
                     (cx + lot_w/2, lot_cy - lot_d/2),
                     (cx + lot_w/2, lot_cy + lot_d/2),
                     (cx - lot_w/2, lot_cy + lot_d/2)]:
        sv.append((lx, ly, mesh_z(lx, ly) + 0.04))
    _finalize_mesh("TS_TruckLot", sv, [[0, 1, 2, 3]],
                    (0.22, 0.22, 0.24, 1.0))
    # Truck-size striping (~ 4 m wide each, for 12 stalls)
    for k in range(11):
        sx = cx - lot_w/2 + (k + 1) * (lot_w / 12)
        cv = []
        for (lx, ly) in [(sx - 0.06, lot_cy - lot_d/2 + 0.3),
                          (sx + 0.06, lot_cy - lot_d/2 + 0.3),
                          (sx + 0.06, lot_cy + lot_d/2 - 0.3),
                          (sx - 0.06, lot_cy + lot_d/2 - 0.3)]:
            cv.append((lx, ly, mesh_z(lx, ly) + 0.055))
        _finalize_mesh(f"TS_LotStripe_{k}", cv, [[0, 1, 2, 3]],
                        (0.92, 0.90, 0.84, 1.0))

    # ── PYLON SIGN visible from afar
    pyl_x = cx - lot_w/2 - 6.0
    pyl_y = cy - 8.0
    pyl_z = mesh_z(pyl_x, pyl_y)
    _make_cyl_local("TS_PylonPole",
                    (pyl_x, pyl_y, pyl_z + 5.0),
                    0.30, 10.0, COL_CAN_STEEL, segments=6)
    _make_box_local("TS_PylonSign",
                    (pyl_x, pyl_y, pyl_z + 9.5),
                    (4.0, 0.18, 2.4), COL_CAN_ROOF)


def build_elementary_school():
    """Harmony Creek Elementary — single-story school building
    on the north edge of HarmonyPark settlement zone. 24 × 12 m
    brick + cream with a small flag-bearing entry plaza.
    """
    es_cx, es_cy = -90.0, 160.0
    es_z = mesh_z(es_cx, es_cy)
    col_es_wall = (0.55, 0.32, 0.22, 1.0)
    col_es_trim = (0.95, 0.92, 0.86, 1.0)
    col_es_roof = (0.32, 0.30, 0.28, 1.0)
    col_es_door = (0.20, 0.45, 0.20, 1.0)   # forest green
    es_w, es_d, es_h = 24.0, 12.0, 4.5
    es_t = 0.20
    _make_box_local("ES_Slab",
                    (es_cx, es_cy, es_z + 0.05),
                    (es_w + 0.4, es_d + 0.4, 0.10), col_es_trim)
    _make_box_local("ES_WallN",
                    (es_cx, es_cy + es_d / 2 - es_t / 2,
                     es_z + es_h / 2),
                    (es_w, es_t, es_h), col_es_wall)
    _make_box_local("ES_WallE",
                    (es_cx + es_w / 2 - es_t / 2, es_cy,
                     es_z + es_h / 2),
                    (es_t, es_d, es_h), col_es_wall)
    _make_box_local("ES_WallW",
                    (es_cx - es_w / 2 + es_t / 2, es_cy,
                     es_z + es_h / 2),
                    (es_t, es_d, es_h), col_es_wall)
    # South wall split for entry door
    es_dw, es_dh = 3.0, 3.0
    es_left = es_w / 2 - es_dw / 2
    _make_box_local("ES_WallS_L",
                    (es_cx - es_dw / 2 - es_left / 2,
                     es_cy - es_d / 2 + es_t / 2,
                     es_z + es_h / 2),
                    (es_left, es_t, es_h), col_es_wall)
    _make_box_local("ES_WallS_R",
                    (es_cx + es_dw / 2 + es_left / 2,
                     es_cy - es_d / 2 + es_t / 2,
                     es_z + es_h / 2),
                    (es_left, es_t, es_h), col_es_wall)
    _make_box_local("ES_WallS_Header",
                    (es_cx, es_cy - es_d / 2 + es_t / 2,
                     es_z + es_dh + (es_h - es_dh) / 2),
                    (es_dw, es_t, es_h - es_dh), col_es_wall)
    _make_box_local("ES_Roof",
                    (es_cx, es_cy, es_z + es_h + 0.10),
                    (es_w + 0.4, es_d + 0.4, 0.20), col_es_roof)
    # Door
    for sgn in (-1, 1):
        _make_box_local(f"ES_Door_{sgn:+d}",
                        (es_cx + sgn * es_dw / 4,
                         es_cy - es_d / 2 + 0.05,
                         es_z + es_dh / 2),
                        (es_dw / 2 - 0.10, 0.06, es_dh - 0.10),
                        col_es_door)
    # 6 windows along south face (3 each side)
    for sgn in (-1, 1):
        for k in range(3):
            wx = es_cx + sgn * (es_dw / 2 + (k + 1) * 2.5)
            if abs(wx) < (es_w / 2 - 0.5):
                _make_box_local(f"ES_Window_{sgn:+d}_{k}",
                                (wx, es_cy - es_d / 2 + 0.04,
                                 es_z + 2.5),
                                (1.4, 0.04, 1.4),
                                (0.32, 0.42, 0.55, 1.0))
    # Flagpole flanking the entry
    fp_x = es_cx
    fp_y = es_cy - es_d / 2 - 4.0
    fp_z = mesh_z(fp_x, fp_y)
    _make_cyl_local("ES_FlagPole",
                    (fp_x, fp_y, fp_z + 4.0),
                    0.08, 8.0, (0.62, 0.62, 0.64, 1.0), segments=6)
    _make_box_local("ES_Banner",
                    (fp_x + 0.40, fp_y, fp_z + 6.8),
                    (0.80, 0.02, 0.60),
                    (0.85, 0.20, 0.18, 1.0))


def build_connector_roads():
    """Short link roads connecting each neighborhood to the new
    district arterials (Harmony Blvd N-S, Horizon Dr E-W). Each
    is a thin 5 m collector road sampling mesh_z per corner.
    """
    road_w = 5.0
    curb_w = 0.4
    COL_ROAD = (0.22, 0.22, 0.24, 1.0)
    COL_CURB = (0.78, 0.76, 0.70, 1.0)
    hw = road_w / 2

    def _emit(pts, prefix):
        for i in range(len(pts) - 1):
            x0, y0 = pts[i]; x1, y1 = pts[i + 1]
            dxs = x1 - x0; dys = y1 - y0
            seg_len = math.hypot(dxs, dys) or 1.0
            perp_x = -dys / seg_len
            perp_y =  dxs / seg_len
            rv = []
            for (rx, ry) in [(x0 - perp_x * hw, y0 - perp_y * hw),
                             (x1 - perp_x * hw, y1 - perp_y * hw),
                             (x1 + perp_x * hw, y1 + perp_y * hw),
                             (x0 + perp_x * hw, y0 + perp_y * hw)]:
                rv.append((rx, ry, mesh_z(rx, ry) + 0.04))
            _finalize_mesh(f"{prefix}Road_{i}", rv, [[0, 1, 2, 3]],
                            COL_ROAD)
            for sgn in (-1, 1):
                cv = []
                for (rx, ry) in [(x0 + sgn * perp_x * hw,
                                  y0 + sgn * perp_y * hw),
                                 (x1 + sgn * perp_x * hw,
                                  y1 + sgn * perp_y * hw),
                                 (x1 + sgn * perp_x * (hw + curb_w),
                                  y1 + sgn * perp_y * (hw + curb_w)),
                                 (x0 + sgn * perp_x * (hw + curb_w),
                                  y0 + sgn * perp_y * (hw + curb_w))]:
                    cv.append((rx, ry, mesh_z(rx, ry) + 0.10))
                _finalize_mesh(f"{prefix}Curb_{i}_{sgn:+d}", cv,
                                [[0, 1, 2, 3]], COL_CURB)

    # Phase 2 → Horizon Dr (east end)
    _emit([(240, -150), (260, -80), (260, -10)], "P2Link_")
    # West Estates → Horizon Dr (west end)
    _emit([(-440, -180), (-440, -100), (-440, -25)], "WELink_")
    # North Ranch → Harmony Blvd (south side of NR)
    _emit([(-320, 100), (-200, 100), (-100, 100), (10, 130)],
           "NRLink_")
    # East CDS → Horizon Dr east end
    _emit([(200, 140), (200, 80), (220, 20), (260, -10)],
           "ECDSLink_")
    # Country Club south driveway → Harmony Blvd top
    _emit([(0, 360), (0, 340)], "CCLink_")


def build_community_landmarks():
    """Three civic landmarks scattered across HCE:
      · CHURCH on Harmony Boulevard between HarmonyPark and OT
        Park
      · FIRE STATION on Horizon Drive
      · POST OFFICE south of Horizon Drive near Harmony Boulevard
    """
    # ── CHURCH at (-30, 140) — west of Harmony Blvd
    ch_cx, ch_cy = -30.0, 140.0
    ch_z = mesh_z(ch_cx, ch_cy)
    col_ch_wall = (0.92, 0.90, 0.86, 1.0)   # white clapboard
    col_ch_roof = (0.42, 0.32, 0.22, 1.0)
    col_ch_door = (0.42, 0.20, 0.16, 1.0)
    col_ch_cross = (0.78, 0.62, 0.32, 1.0)  # brass
    ch_w, ch_d, ch_h = 12.0, 18.0, 5.0
    ch_t = 0.20
    # Slab
    _make_box_local("Ch_Slab", (ch_cx, ch_cy, ch_z + 0.05),
                    (ch_w + 0.4, ch_d + 0.4, 0.10), col_ch_wall)
    # Walls (all four solid)
    _make_box_local("Ch_WallN",
                    (ch_cx, ch_cy + ch_d / 2 - ch_t / 2,
                     ch_z + ch_h / 2),
                    (ch_w, ch_t, ch_h), col_ch_wall)
    _make_box_local("Ch_WallE",
                    (ch_cx + ch_w / 2 - ch_t / 2, ch_cy,
                     ch_z + ch_h / 2),
                    (ch_t, ch_d, ch_h), col_ch_wall)
    _make_box_local("Ch_WallW",
                    (ch_cx - ch_w / 2 + ch_t / 2, ch_cy,
                     ch_z + ch_h / 2),
                    (ch_t, ch_d, ch_h), col_ch_wall)
    # South wall split for double door
    d_w = 2.4; d_h = 3.4
    left_w = ch_w / 2 - d_w / 2
    _make_box_local("Ch_WallS_L",
                    (ch_cx - d_w / 2 - left_w / 2,
                     ch_cy - ch_d / 2 + ch_t / 2, ch_z + ch_h / 2),
                    (left_w, ch_t, ch_h), col_ch_wall)
    _make_box_local("Ch_WallS_R",
                    (ch_cx + d_w / 2 + left_w / 2,
                     ch_cy - ch_d / 2 + ch_t / 2, ch_z + ch_h / 2),
                    (left_w, ch_t, ch_h), col_ch_wall)
    _make_box_local("Ch_WallS_Header",
                    (ch_cx, ch_cy - ch_d / 2 + ch_t / 2,
                     ch_z + d_h + (ch_h - d_h) / 2),
                    (d_w, ch_t, ch_h - d_h), col_ch_wall)
    # Pitched gable roof — use the suburban-house roof pattern
    # but bigger
    ridge_h = 3.0
    rverts = [
        (ch_cx - ch_w/2 - 0.30, ch_cy - ch_d/2 - 0.30, ch_z + ch_h),
        (ch_cx + ch_w/2 + 0.30, ch_cy - ch_d/2 - 0.30, ch_z + ch_h),
        (ch_cx + ch_w/2 + 0.30, ch_cy + ch_d/2 + 0.30, ch_z + ch_h),
        (ch_cx - ch_w/2 - 0.30, ch_cy + ch_d/2 + 0.30, ch_z + ch_h),
        (ch_cx, ch_cy - ch_d/2 - 0.30, ch_z + ch_h + ridge_h),
        (ch_cx, ch_cy + ch_d/2 + 0.30, ch_z + ch_h + ridge_h),
    ]
    rfaces = [[0, 1, 5, 4], [3, 4, 5, 2],
              [0, 4, 3], [1, 2, 5]]
    _finalize_mesh("Ch_Roof", rverts, rfaces, col_ch_roof)
    # Door
    for sgn in (-1, 1):
        _make_box_local(f"Ch_Door_{sgn:+d}",
                        (ch_cx + sgn * d_w / 4,
                         ch_cy - ch_d / 2 + 0.05,
                         ch_z + d_h / 2),
                        (d_w / 2 - 0.10, 0.06, d_h - 0.10),
                        col_ch_door)
    # Round stained-glass window above the door
    _make_cyl_local("Ch_RoseWindow",
                    (ch_cx, ch_cy - ch_d / 2 + 0.04,
                     ch_z + ch_h - 0.8),
                    0.70, 0.06,
                    (0.62, 0.18, 0.42, 1.0), segments=10)
    # STEEPLE — square tower atop the south end with a spire
    st_x = ch_cx
    st_y = ch_cy - ch_d / 2 + 1.2
    st_base_z = ch_z + ch_h + ridge_h
    _make_box_local("Ch_SteepleBase",
                    (st_x, st_y, st_base_z + 1.5),
                    (2.4, 2.4, 3.0), col_ch_wall)
    # Belfry openings (4 sides)
    for sgn_x, sgn_y, tag in ((-1, 0, 'W'), (1, 0, 'E'),
                               (0, -1, 'S'), (0, 1, 'N')):
        _make_box_local(f"Ch_BelfryOpen_{tag}",
                        (st_x + sgn_x * 1.0, st_y + sgn_y * 1.0,
                         st_base_z + 2.0),
                        (0.10 if sgn_x else 0.8,
                         0.8 if sgn_x else 0.10, 1.4),
                        (0.18, 0.14, 0.10, 1.0))
    # Spire — narrow pyramid (approximate with a tapered box)
    _make_box_local("Ch_Spire1",
                    (st_x, st_y, st_base_z + 4.0),
                    (1.6, 1.6, 1.0), col_ch_roof)
    _make_box_local("Ch_Spire2",
                    (st_x, st_y, st_base_z + 5.0),
                    (1.0, 1.0, 1.0), col_ch_roof)
    _make_box_local("Ch_Spire3",
                    (st_x, st_y, st_base_z + 5.7),
                    (0.4, 0.4, 0.4), col_ch_roof)
    # Cross at the top
    _make_box_local("Ch_CrossV",
                    (st_x, st_y, st_base_z + 6.4),
                    (0.06, 0.06, 0.80), col_ch_cross)
    _make_box_local("Ch_CrossH",
                    (st_x, st_y, st_base_z + 6.7),
                    (0.40, 0.06, 0.06), col_ch_cross)

    # ── FIRE STATION at (-200, -30) on Horizon Drive
    fs_cx, fs_cy = -200.0, -30.0
    fs_z = mesh_z(fs_cx, fs_cy)
    col_fs_wall = (0.82, 0.32, 0.22, 1.0)   # fire-engine red
    col_fs_door = (0.95, 0.94, 0.90, 1.0)   # white garage door
    col_fs_trim = (0.62, 0.62, 0.64, 1.0)
    fs_w, fs_d, fs_h = 22.0, 14.0, 5.5
    _make_box_local("FS_Slab",
                    (fs_cx, fs_cy, fs_z + 0.05),
                    (fs_w + 0.4, fs_d + 0.4, 0.10), col_fs_trim)
    # Solid walls (back + sides)
    _make_box_local("FS_WallN",
                    (fs_cx, fs_cy + fs_d / 2 - 0.10,
                     fs_z + fs_h / 2),
                    (fs_w, 0.20, fs_h), col_fs_wall)
    _make_box_local("FS_WallE",
                    (fs_cx + fs_w / 2 - 0.10, fs_cy,
                     fs_z + fs_h / 2),
                    (0.20, fs_d, fs_h), col_fs_wall)
    _make_box_local("FS_WallW",
                    (fs_cx - fs_w / 2 + 0.10, fs_cy,
                     fs_z + fs_h / 2),
                    (0.20, fs_d, fs_h), col_fs_wall)
    # South wall — 3 BIG garage doors, each 4 m wide × 4 m tall
    bay_w = 4.5
    n_bays = 3
    bay_span = n_bays * bay_w + (n_bays - 1) * 0.4
    bay_door_h = 4.0
    # Side wall pieces around the bay row
    side_w = (fs_w - bay_span) / 2
    _make_box_local("FS_WallS_L",
                    (fs_cx - bay_span / 2 - side_w / 2,
                     fs_cy - fs_d / 2 + 0.10,
                     fs_z + fs_h / 2),
                    (side_w, 0.20, fs_h), col_fs_wall)
    _make_box_local("FS_WallS_R",
                    (fs_cx + bay_span / 2 + side_w / 2,
                     fs_cy - fs_d / 2 + 0.10,
                     fs_z + fs_h / 2),
                    (side_w, 0.20, fs_h), col_fs_wall)
    # Lintel header over all bays
    _make_box_local("FS_WallS_Header",
                    (fs_cx, fs_cy - fs_d / 2 + 0.10,
                     fs_z + bay_door_h + (fs_h - bay_door_h) / 2),
                    (bay_span, 0.20, fs_h - bay_door_h), col_fs_wall)
    # 3 white garage doors
    for k in range(n_bays):
        bx = fs_cx - bay_span / 2 + (k + 0.5) * (bay_w + 0.4)
        _make_box_local(f"FS_BayDoor_{k}",
                        (bx, fs_cy - fs_d / 2 + 0.05,
                         fs_z + bay_door_h / 2),
                        (bay_w, 0.06, bay_door_h), col_fs_door)
    # Roof + parapet
    _make_box_local("FS_Roof",
                    (fs_cx, fs_cy, fs_z + fs_h + 0.10),
                    (fs_w + 0.4, fs_d + 0.4, 0.20),
                    (0.22, 0.20, 0.22, 1.0))
    # White stripe at top of red walls
    _make_box_local("FS_TopStripe",
                    (fs_cx, fs_cy - fs_d / 2 - 0.05,
                     fs_z + fs_h - 0.40),
                    (fs_w + 0.4, 0.10, 0.40),
                    (0.95, 0.94, 0.90, 1.0))
    # Sign panel above the door header
    _make_box_local("FS_SignPanel",
                    (fs_cx, fs_cy - fs_d / 2 - 0.18,
                     fs_z + fs_h + 0.80),
                    (8.0, 0.14, 1.2),
                    (0.18, 0.14, 0.10, 1.0))
    # Fire hydrant out front
    _make_cyl_local("FS_Hydrant",
                    (fs_cx + fs_w / 2 + 2.0,
                     fs_cy - fs_d / 2 - 2.0, fs_z + 0.40),
                    0.18, 0.80,
                    (0.85, 0.20, 0.18, 1.0), segments=6)

    # ── POST OFFICE at (180, -30) just south of Horizon Drive
    po_cx, po_cy = 180.0, -30.0
    po_z = mesh_z(po_cx, po_cy)
    col_po_wall = (0.42, 0.42, 0.45, 1.0)   # institutional grey
    col_po_trim = (0.62, 0.62, 0.64, 1.0)
    col_po_door = (0.18, 0.32, 0.55, 1.0)   # USPS blue
    col_po_red = (0.85, 0.20, 0.18, 1.0)
    po_w, po_d, po_h = 16.0, 12.0, 4.5
    _make_box_local("PO_Slab",
                    (po_cx, po_cy, po_z + 0.05),
                    (po_w + 0.4, po_d + 0.4, 0.10), col_po_trim)
    _make_box_local("PO_WallN",
                    (po_cx, po_cy + po_d / 2 - 0.10,
                     po_z + po_h / 2),
                    (po_w, 0.20, po_h), col_po_wall)
    _make_box_local("PO_WallE",
                    (po_cx + po_w / 2 - 0.10, po_cy,
                     po_z + po_h / 2),
                    (0.20, po_d, po_h), col_po_wall)
    _make_box_local("PO_WallW",
                    (po_cx - po_w / 2 + 0.10, po_cy,
                     po_z + po_h / 2),
                    (0.20, po_d, po_h), col_po_wall)
    # South wall split for entry door
    po_dw = 2.0; po_dh = 2.6
    po_left_w = po_w / 2 - po_dw / 2
    _make_box_local("PO_WallS_L",
                    (po_cx - po_dw / 2 - po_left_w / 2,
                     po_cy - po_d / 2 + 0.10, po_z + po_h / 2),
                    (po_left_w, 0.20, po_h), col_po_wall)
    _make_box_local("PO_WallS_R",
                    (po_cx + po_dw / 2 + po_left_w / 2,
                     po_cy - po_d / 2 + 0.10, po_z + po_h / 2),
                    (po_left_w, 0.20, po_h), col_po_wall)
    _make_box_local("PO_WallS_Header",
                    (po_cx, po_cy - po_d / 2 + 0.10,
                     po_z + po_dh + (po_h - po_dh) / 2),
                    (po_dw, 0.20, po_h - po_dh), col_po_wall)
    _make_box_local("PO_Door",
                    (po_cx, po_cy - po_d / 2 + 0.05,
                     po_z + po_dh / 2),
                    (po_dw, 0.06, po_dh - 0.10), col_po_door)
    # 2 windows each side of door
    for sgn in (-1, 1):
        for k in range(2):
            wx = po_cx + sgn * (po_dw / 2 + (k + 1) * 2.5)
            if abs(wx) < (po_w / 2 - 0.5):
                _make_box_local(f"PO_Window_{sgn:+d}_{k}",
                                (wx, po_cy - po_d / 2 + 0.04,
                                 po_z + 2.5),
                                (1.4, 0.04, 1.4),
                                (0.32, 0.42, 0.55, 1.0))
    # Roof + flag pole on top
    _make_box_local("PO_Roof",
                    (po_cx, po_cy, po_z + po_h + 0.10),
                    (po_w + 0.4, po_d + 0.4, 0.20),
                    (0.22, 0.20, 0.22, 1.0))
    # Two outdoor blue USPS drop boxes by the door
    for sgn in (-1, 1):
        _make_box_local(f"PO_DropBox_{sgn:+d}",
                        (po_cx + sgn * 3.0,
                         po_cy - po_d / 2 - 1.5, po_z + 0.55),
                        (0.60, 0.50, 1.10), col_po_door)
    # USPS sign panel above the entry — red+white+blue stripes
    _make_box_local("PO_SignBlue",
                    (po_cx, po_cy - po_d / 2 - 0.18,
                     po_z + po_h + 0.60),
                    (6.0, 0.14, 0.50), col_po_door)
    _make_box_local("PO_SignRed",
                    (po_cx, po_cy - po_d / 2 - 0.18,
                     po_z + po_h + 1.20),
                    (6.0, 0.14, 0.50), col_po_red)


def build_district_arterials():
    """Two arterials threading through HCE: HARMONY BOULEVARD
    runs north-south from the country club down to the chapter-
    one commercial cluster; HORIZON DRIVE runs east-west across
    the middle of the district connecting West Estates with the
    East CDS / high-school zone. Both are 4-lane (8 m) asphalt
    with painted yellow centerlines.
    """
    road_w = 8.0
    COL_ROAD = (0.20, 0.20, 0.22, 1.0)
    COL_CL = (0.95, 0.85, 0.30, 1.0)         # yellow centerline
    hw = road_w / 2

    def _emit_arterial(pts, prefix, with_centerline=True):
        for i in range(len(pts) - 1):
            x0, y0 = pts[i]; x1, y1 = pts[i + 1]
            dxs = x1 - x0; dys = y1 - y0
            seg_len = math.hypot(dxs, dys) or 1.0
            perp_x = -dys / seg_len
            perp_y =  dxs / seg_len
            rv = []
            for (rx, ry) in [(x0 - perp_x * hw, y0 - perp_y * hw),
                             (x1 - perp_x * hw, y1 - perp_y * hw),
                             (x1 + perp_x * hw, y1 + perp_y * hw),
                             (x0 + perp_x * hw, y0 + perp_y * hw)]:
                rv.append((rx, ry, mesh_z(rx, ry) + 0.04))
            _finalize_mesh(f"{prefix}Road_{i}", rv, [[0, 1, 2, 3]],
                            COL_ROAD)
            if with_centerline:
                # 3 dashes per segment evenly spaced
                for d in range(3):
                    t = (d + 0.5) / 3
                    mid_x = x0 + dxs * t
                    mid_y = y0 + dys * t
                    dx_len = 2.5
                    ddx = dxs / seg_len * dx_len / 2
                    ddy = dys / seg_len * dx_len / 2
                    dv = []
                    for (rx, ry) in [
                        (mid_x - ddx - perp_x * 0.08,
                         mid_y - ddy - perp_y * 0.08),
                        (mid_x + ddx - perp_x * 0.08,
                         mid_y + ddy - perp_y * 0.08),
                        (mid_x + ddx + perp_x * 0.08,
                         mid_y + ddy + perp_y * 0.08),
                        (mid_x - ddx + perp_x * 0.08,
                         mid_y - ddy + perp_y * 0.08),
                    ]:
                        dv.append((rx, ry, mesh_z(rx, ry) + 0.055))
                    _finalize_mesh(f"{prefix}Dash_{i}_{d}", dv,
                                    [[0, 1, 2, 3]], COL_CL)

    # ── HARMONY BOULEVARD · N-S arterial. Threads east of the
    # Harmony Park community pool to avoid cutting it in half.
    harmony_blvd = [
        (   0, 340),   # at country club south edge
        (  10, 260),
        (  30, 200),   # entering HarmonyPark zone east of pool
        (  60, 130),   # east of community pool
        (  60,  10),
        (  40, -80),
        (  20, -180),
        (  10, -260),
        (   0, -340),  # at chapter-1 commercial zone north edge
    ]
    _emit_arterial(harmony_blvd, "HarmonyBlvd_")

    # ── HORIZON DRIVE · E-W arterial across the middle of HCE.
    # Connects West Estates / WestComm with East CDS / East Comm.
    horizon_dr = [
        (-460,  -20),       # at West Comm boundary
        (-380,  -10),
        (-280,  -10),       # passes south of OT Park
        (-180,  -20),       # crosses Harmony Park south edge
        ( -80,  -30),
        (  60,   -20),      # crosses Harmony Boulevard
        ( 160,   -10),      # entering Phase 2 north edge
        ( 260,   -10),
        ( 380,    0),       # at East CDS
        ( 440,    0),       # at East Comm
    ]
    _emit_arterial(horizon_dr, "HorizonDr_")


def build_harmony_park():
    """HarmonyPark — central manicured community park. Sits in
    HarmonyPark settlement zone (-120..180, -40..200, target_z =
    +1.0, flatness 0.55). HarmonyPond at (30, 60) acts as the
    COMMUNITY POOL — wrap park infrastructure around it.
    """
    # The community pool sits at HarmonyPond. Add a concrete pool
    # deck ring just outside the pond's water disc.
    pool_cx, pool_cy = 30.0, 60.0
    pool_r = 32.0      # matches PONDS entry
    pool_z = mesh_z(pool_cx, pool_cy)
    deck_outer = pool_r * 1.10
    deck_inner = pool_r * 0.95
    segments = 18
    deck_verts = []
    for i in range(segments):
        ang = 2.0 * math.pi * i / segments
        deck_verts.append((pool_cx + math.cos(ang) * deck_inner,
                            pool_cy + math.sin(ang) * deck_inner,
                            pool_z + 0.08))
        deck_verts.append((pool_cx + math.cos(ang) * deck_outer,
                            pool_cy + math.sin(ang) * deck_outer,
                            pool_z + 0.08))
    deck_faces = []
    for i in range(segments):
        j = (i + 1) % segments
        deck_faces.append([i * 2, i * 2 + 1, j * 2 + 1, j * 2])
    _finalize_mesh("HP_PoolDeck", deck_verts, deck_faces,
                    (0.78, 0.74, 0.66, 1.0))

    # CHANGING ROOM building — east of the pool
    cr_cx = pool_cx + deck_outer + 12.0
    cr_cy = pool_cy
    cr_z = mesh_z(cr_cx, cr_cy)
    cr_w, cr_d, cr_h = 18.0, 10.0, 3.6
    cr_t = 0.20
    col_cr_wall = (0.78, 0.74, 0.66, 1.0)
    col_cr_roof = (0.42, 0.30, 0.22, 1.0)
    col_cr_door = (0.32, 0.55, 0.78, 1.0)   # pool blue
    _make_box_local("HP_ChangeRoom_Slab",
                    (cr_cx, cr_cy, cr_z + 0.05),
                    (cr_w + 0.6, cr_d + 0.6, 0.10), col_cr_wall)
    _make_box_local("HP_ChangeRoom_WallN",
                    (cr_cx, cr_cy + cr_d / 2 - cr_t / 2,
                     cr_z + cr_h / 2),
                    (cr_w, cr_t, cr_h), col_cr_wall)
    _make_box_local("HP_ChangeRoom_WallE",
                    (cr_cx + cr_w / 2 - cr_t / 2, cr_cy,
                     cr_z + cr_h / 2),
                    (cr_t, cr_d, cr_h), col_cr_wall)
    _make_box_local("HP_ChangeRoom_WallS",
                    (cr_cx, cr_cy - cr_d / 2 + cr_t / 2,
                     cr_z + cr_h / 2),
                    (cr_w, cr_t, cr_h), col_cr_wall)
    # West wall split — two doors (men + women) facing the pool
    door_h = 2.4
    door_w = 1.2
    # Door positions: at cr_cy ± 2.0 (north door = women, south = men)
    for sgn, label in ((-1, "M"), (+1, "W")):
        # Left side wall piece
        wall_h_above = cr_h - door_h
        d_centre_y = cr_cy + sgn * 2.0
        # West wall is segmented around two door openings; for
        # simplicity, just make the door visually with a colored
        # box covering the wall position (no actual cutout — this
        # is a primitive placeholder per the user's "models still
        # super primitive" note)
        _make_box_local(f"HP_ChangeRoom_Door_{label}",
                        (cr_cx - cr_w / 2 + 0.10, d_centre_y,
                         cr_z + door_h / 2),
                        (0.20, door_w, door_h), col_cr_door)
    # Full west wall behind the doors (so the doors APPEAR set
    # into a wall — primitive)
    _make_box_local("HP_ChangeRoom_WallW",
                    (cr_cx - cr_w / 2 + cr_t / 2 + 0.20, cr_cy,
                     cr_z + cr_h / 2),
                    (cr_t, cr_d, cr_h), col_cr_wall)
    _make_box_local("HP_ChangeRoom_Roof",
                    (cr_cx, cr_cy, cr_z + cr_h + 0.10),
                    (cr_w + 0.4, cr_d + 0.4, 0.20), col_cr_roof)

    # 4 lounge chairs along the pool deck north-side
    for k in range(4):
        ang = math.radians(60 + k * 30)   # NE-ish spread
        lcx = pool_cx + math.cos(ang) * (deck_outer + 1.5)
        lcy = pool_cy + math.sin(ang) * (deck_outer + 1.5)
        lcz = mesh_z(lcx, lcy)
        _make_box_local(f"HP_Lounge_{k}",
                        (lcx, lcy, lcz + 0.15),
                        (1.8, 0.6, 0.15),
                        (0.95, 0.95, 0.92, 1.0))
        # Lounge back angled up (just a tilted box approximated as a vertical box at end)
        _make_box_local(f"HP_LoungeBack_{k}",
                        (lcx, lcy - 0.20, lcz + 0.50),
                        (1.8, 0.10, 0.70),
                        (0.95, 0.95, 0.92, 1.0))

    # Lifeguard chair on the north side of the pool
    lg_x = pool_cx
    lg_y = pool_cy + deck_outer + 2.0
    lg_z = mesh_z(lg_x, lg_y)
    _make_cyl_local("HP_Lifeguard_PoleL",
                    (lg_x - 1.0, lg_y, lg_z + 1.5),
                    0.06, 3.0, (0.78, 0.62, 0.32, 1.0), segments=4)
    _make_cyl_local("HP_Lifeguard_PoleR",
                    (lg_x + 1.0, lg_y, lg_z + 1.5),
                    0.06, 3.0, (0.78, 0.62, 0.32, 1.0), segments=4)
    _make_box_local("HP_Lifeguard_Seat",
                    (lg_x, lg_y, lg_z + 2.5),
                    (2.0, 0.8, 0.10),
                    (0.78, 0.18, 0.18, 1.0))
    _make_box_local("HP_Lifeguard_Back",
                    (lg_x, lg_y + 0.35, lg_z + 3.0),
                    (2.0, 0.08, 0.80),
                    (0.78, 0.18, 0.18, 1.0))

    # ── PLAYGROUND south of the pool · swings + slide + sandbox
    pg_cx = pool_cx
    pg_cy = pool_cy - deck_outer - 25.0
    pg_z = mesh_z(pg_cx, pg_cy)
    # Sandbox
    _make_box_local("HP_Sandbox",
                    (pg_cx, pg_cy, pg_z + 0.05),
                    (10.0, 10.0, 0.10),
                    (0.90, 0.82, 0.62, 1.0))
    # Sandbox edge planks
    for sgn_x, sgn_y in ((-1, 0), (1, 0), (0, -1), (0, 1)):
        if sgn_x != 0:
            _make_box_local(
                f"HP_SandboxEdge_{sgn_x:+d}_{sgn_y:+d}",
                (pg_cx + sgn_x * 5.0, pg_cy, pg_z + 0.18),
                (0.20, 10.4, 0.20),
                (0.42, 0.30, 0.22, 1.0))
        else:
            _make_box_local(
                f"HP_SandboxEdge_{sgn_x:+d}_{sgn_y:+d}",
                (pg_cx, pg_cy + sgn_y * 5.0, pg_z + 0.18),
                (10.4, 0.20, 0.20),
                (0.42, 0.30, 0.22, 1.0))
    # SWING SET — 2 swings on a frame east of sandbox
    sw_x = pg_cx + 10.0
    sw_y = pg_cy
    # Frame uprights
    for sgn in (-1, 1):
        _make_cyl_local(f"HP_SwingPost_{sgn:+d}",
                        (sw_x, sw_y + sgn * 1.6, pg_z + 1.5),
                        0.05, 3.0,
                        (0.62, 0.62, 0.64, 1.0), segments=4)
    _make_box_local("HP_SwingTop",
                    (sw_x, sw_y, pg_z + 3.0),
                    (0.10, 3.6, 0.10), (0.62, 0.62, 0.64, 1.0))
    # 2 swings hanging
    for sgn in (-1, 1):
        _make_box_local(f"HP_SwingSeat_{sgn:+d}",
                        (sw_x, sw_y + sgn * 0.8, pg_z + 0.8),
                        (0.50, 0.30, 0.04),
                        (0.85, 0.20, 0.18, 1.0))
        for cx_off in (-0.20, 0.20):
            _make_box_local(
                f"HP_SwingChain_{sgn:+d}_{int(cx_off*10)}",
                (sw_x + cx_off, sw_y + sgn * 0.8, pg_z + 1.9),
                (0.02, 0.02, 2.2),
                (0.32, 0.32, 0.34, 1.0))
    # SLIDE — west of sandbox
    sl_x = pg_cx - 10.0
    sl_y = pg_cy
    _make_box_local("HP_SlideTower",
                    (sl_x, sl_y, pg_z + 1.5),
                    (1.5, 1.5, 3.0),
                    (0.55, 0.42, 0.30, 1.0))
    # Slide chute — slanted (using a long box as placeholder)
    _make_box_local("HP_SlideChute",
                    (sl_x + 2.0, sl_y, pg_z + 1.2),
                    (3.5, 0.80, 0.10),
                    (0.78, 0.18, 0.18, 1.0))

    # ── PARK BENCHES around the pool deck (4 cardinal points)
    for k, ang_deg in enumerate((0, 90, 180, 270)):
        ang = math.radians(ang_deg)
        bx = pool_cx + math.cos(ang) * (deck_outer + 3.0)
        by = pool_cy + math.sin(ang) * (deck_outer + 3.0)
        bz = mesh_z(bx, by)
        _make_box_local(f"HP_Bench_{k}",
                        (bx, by, bz + 0.42),
                        (1.8, 0.42, 0.06),
                        (0.42, 0.30, 0.20, 1.0))
        _make_box_local(f"HP_BenchBack_{k}",
                        (bx, by + 0.18, bz + 0.65),
                        (1.8, 0.06, 0.40),
                        (0.42, 0.30, 0.20, 1.0))
        for sgn in (-1, 1):
            _make_box_local(f"HP_BenchLeg_{k}_{sgn:+d}",
                            (bx + sgn * 0.75, by, bz + 0.21),
                            (0.06, 0.42, 0.42),
                            (0.18, 0.18, 0.18, 1.0))


def build_country_club():
    """Harmony Creek Country Club — top-of-the-hill prosperous
    zone. Symmetrical brick clubhouse with white columns, plus
    a tennis-court pair and a golf-fairway suggestion. Settlement
    zone (-460..440, 340..420, target_z = +22.0, flatness 0.85).
    """
    cx, cy = 0.0, 370.0
    ground_z = mesh_z(cx, cy)

    # ── CLUBHOUSE — 36 × 14 × 7 m brick + white-column portico
    col_brick = (0.55, 0.32, 0.24, 1.0)
    col_white = (0.95, 0.94, 0.90, 1.0)
    col_roof = (0.22, 0.20, 0.22, 1.0)
    col_door = (0.32, 0.18, 0.16, 1.0)
    col_window = (0.32, 0.42, 0.55, 1.0)

    cb_w = 36.0; cb_d = 14.0; cb_h = 7.0; cb_t = 0.20
    # Slab
    _make_box_local("CC_Slab", (cx, cy, ground_z + 0.05),
                    (cb_w + 0.6, cb_d + 0.6, 0.10), col_white)
    # Solid back + side walls
    _make_box_local("CC_WallN",
                    (cx, cy + cb_d / 2 - cb_t / 2, ground_z + cb_h / 2),
                    (cb_w, cb_t, cb_h), col_brick)
    _make_box_local("CC_WallE",
                    (cx + cb_w / 2 - cb_t / 2, cy, ground_z + cb_h / 2),
                    (cb_t, cb_d, cb_h), col_brick)
    _make_box_local("CC_WallW",
                    (cx - cb_w / 2 + cb_t / 2, cy, ground_z + cb_h / 2),
                    (cb_t, cb_d, cb_h), col_brick)
    # South wall — split for the entry opening
    sd_w = 4.0       # door opening width
    sd_h = 4.0       # door opening height
    left_w = cb_w / 2 - sd_w / 2
    _make_box_local("CC_WallS_L",
                    (cx - sd_w / 2 - left_w / 2,
                     cy - cb_d / 2 + cb_t / 2, ground_z + cb_h / 2),
                    (left_w, cb_t, cb_h), col_brick)
    _make_box_local("CC_WallS_R",
                    (cx + sd_w / 2 + left_w / 2,
                     cy - cb_d / 2 + cb_t / 2, ground_z + cb_h / 2),
                    (left_w, cb_t, cb_h), col_brick)
    _make_box_local("CC_WallS_Header",
                    (cx, cy - cb_d / 2 + cb_t / 2,
                     ground_z + sd_h + (cb_h - sd_h) / 2),
                    (sd_w, cb_t, cb_h - sd_h), col_brick)
    # Roof — flat with parapet trim
    _make_box_local("CC_Roof",
                    (cx, cy, ground_z + cb_h + 0.10),
                    (cb_w + 0.4, cb_d + 0.4, 0.20), col_roof)
    # White trim band along south facade at parapet
    _make_box_local("CC_TrimBand",
                    (cx, cy - cb_d / 2 - 0.05,
                     ground_z + cb_h - 0.10),
                    (cb_w + 0.4, 0.10, 0.30), col_white)
    # PORTICO — 4 white columns in front of the entry, 1.2 m
    # forward of south face, with a triangular pediment-suggestion
    # box on top
    for k, col_off in enumerate((-3.6, -1.2, 1.2, 3.6)):
        _make_cyl_local(f"CC_PorticoCol_{k}",
                        (cx + col_off, cy - cb_d / 2 - 1.6,
                         ground_z + cb_h * 0.40),
                        0.25, cb_h * 0.80, col_white, segments=8)
    # Portico roof (thick white slab)
    _make_box_local("CC_PorticoRoof",
                    (cx, cy - cb_d / 2 - 1.6,
                     ground_z + cb_h * 0.85),
                    (9.0, 1.6, 0.30), col_white)
    # Pediment triangle (placeholder: just a flat box above)
    _make_box_local("CC_Pediment",
                    (cx, cy - cb_d / 2 - 1.6,
                     ground_z + cb_h * 0.85 + 0.45),
                    (8.0, 1.4, 0.60), col_white)

    # Front door (double red leaf)
    glass_y = cy - cb_d / 2 + 0.05
    for sgn in (-1, 1):
        _make_box_local(f"CC_Door_{sgn:+d}",
                        (cx + sgn * sd_w / 4, glass_y,
                         ground_z + sd_h / 2),
                        (sd_w / 2 - 0.12, 0.06, sd_h - 0.10),
                        col_door)
    # 8 windows along the south façade (4 each side of the door)
    for sgn in (-1, 1):
        for k in range(4):
            wx = cx + sgn * (sd_w / 2 + (k + 1) * 3.0)
            if abs(wx) < cb_w / 2 - 1.5:
                _make_box_local(f"CC_Window_S_{sgn:+d}_{k}",
                                (wx, glass_y, ground_z + 3.5),
                                (1.4, 0.04, 1.8), col_window)
    # Welcome mat
    _make_box_local("CC_DoorMat",
                    (cx, glass_y - 0.5, ground_z + 0.07),
                    (sd_w + 0.4, 0.80, 0.02),
                    (0.32, 0.18, 0.16, 1.0))

    # ── TENNIS COURT PAIR — east of clubhouse
    tc_cx = cx + cb_w / 2 + 22.0
    tc_cy = cy
    tc_w = 24.0       # standard tennis court 23.77 m × 10.97 m
    tc_d = 11.0
    COL_TC = (0.45, 0.35, 0.55, 1.0)     # purple-ish court
    COL_TC_LINE = (0.95, 0.95, 0.92, 1.0)
    for k_court in (0, 1):
        ty = tc_cy + (k_court - 0.5) * (tc_d + 2.0)
        _make_box_local(f"CC_TennisCourt_{k_court}",
                        (tc_cx, ty, ground_z + 0.05),
                        (tc_w, tc_d, 0.06), COL_TC)
        # Net at midcourt
        _make_box_local(f"CC_TennisNet_{k_court}",
                        (tc_cx, ty, ground_z + 0.55),
                        (0.10, tc_d - 0.6, 0.90),
                        (0.18, 0.18, 0.18, 1.0))
        # Centre line
        _make_box_local(f"CC_TennisCenterline_{k_court}",
                        (tc_cx, ty, ground_z + 0.09),
                        (tc_w - 1.0, 0.10, 0.01), COL_TC_LINE)
        # Service lines
        for ln_off in (-tc_w / 4, tc_w / 4):
            _make_box_local(
                f"CC_TennisServLine_{k_court}_{int(ln_off)}",
                (tc_cx + ln_off, ty, ground_z + 0.09),
                (0.10, tc_d - 1.0, 0.01), COL_TC_LINE)
    # Chain-link fence around the courts (4 corner posts + suggestion)
    fence_x_min = tc_cx - tc_w / 2 - 1.0
    fence_x_max = tc_cx + tc_w / 2 + 1.0
    fence_y_min = tc_cy - (tc_d + 2.0) - 1.0
    fence_y_max = tc_cy + (tc_d + 2.0) + 1.0
    for fx in (fence_x_min, fence_x_max):
        for fy in (fence_y_min, fence_y_max):
            _make_cyl_local(f"CC_TennisFencePost_{int(fx)}_{int(fy)}",
                            (fx, fy, ground_z + 1.5),
                            0.05, 3.0,
                            (0.62, 0.62, 0.64, 1.0), segments=4)

    # ── GOLF FAIRWAY suggestion — long green stripe running west
    # from the clubhouse, ending at a putting green
    fw_x = cx - cb_w / 2 - 40.0
    fw_w = 60.0
    fw_d = 18.0
    COL_FAIRWAY = (0.30, 0.55, 0.25, 1.0)
    COL_GREEN = (0.20, 0.45, 0.20, 1.0)
    _make_box_local("CC_Fairway",
                    (fw_x, cy, ground_z + 0.03),
                    (fw_w, fw_d, 0.04), COL_FAIRWAY)
    # Putting green at far west end of fairway
    pg_x = fw_x - fw_w / 2 - 8.0
    _make_box_local("CC_PuttingGreen",
                    (pg_x, cy, ground_z + 0.05),
                    (12.0, 12.0, 0.06), COL_GREEN)
    # Flag pin in the centre of the green
    _make_cyl_local("CC_GolfPinPole",
                    (pg_x, cy, ground_z + 1.0),
                    0.02, 2.0, (0.95, 0.95, 0.92, 1.0), segments=4)
    # Flag triangle
    _make_box_local("CC_GolfFlag",
                    (pg_x + 0.30, cy, ground_z + 1.70),
                    (0.50, 0.02, 0.30),
                    (0.85, 0.20, 0.18, 1.0))


def build_phase3_neighborhood():
    """Phase III — Norman Lott's abandoned development. "Gone to
    seed" per the design manual: partial road, half-finished
    houses, construction debris. Settlement zone (-460..-340,
    -260..-180, target_z = -8.0, flatness 0.70).
    """
    road_w = 5.0      # narrower than completed neighborhoods
    curb_w = 0.3
    COL_GRAVEL = (0.55, 0.50, 0.40, 1.0)     # unfinished gravel road
    COL_DIRT = (0.42, 0.32, 0.22, 1.0)
    hw = road_w / 2

    # Short partial road — only one block was paved before the
    # developer went bust
    road_pts = [(-440, -220), (-380, -220), (-360, -230)]
    for i in range(len(road_pts) - 1):
        x0, y0 = road_pts[i]; x1, y1 = road_pts[i + 1]
        dxs = x1 - x0; dys = y1 - y0
        seg_len = math.hypot(dxs, dys) or 1.0
        perp_x = -dys / seg_len
        perp_y =  dxs / seg_len
        rv = []
        for (rx, ry) in [(x0 - perp_x * hw, y0 - perp_y * hw),
                         (x1 - perp_x * hw, y1 - perp_y * hw),
                         (x1 + perp_x * hw, y1 + perp_y * hw),
                         (x0 + perp_x * hw, y0 + perp_y * hw)]:
            rv.append((rx, ry, mesh_z(rx, ry) + 0.03))
        _finalize_mesh(f"P3Gravel_{i}", rv, [[0, 1, 2, 3]], COL_GRAVEL)

    # ── 4 partial houses · 2 framed (slab + 4 wall studs, no
    # roof), 2 finished but dilapidated.
    dilap_palette = [
        {'wall': (0.55, 0.50, 0.42, 1.0), 'roof': (0.32, 0.28, 0.22, 1.0)},
        {'wall': (0.58, 0.52, 0.42, 1.0), 'roof': (0.30, 0.25, 0.20, 1.0)},
    ]
    # 2 finished but dilapidated houses on the partial road
    for k, (hcx_off, hcy_off, facing) in enumerate((
            (-30, -10, '+Y'),     # north of road
            (10, +10, '-Y'),      # south of road
    )):
        hcx = -440 + 50 + hcx_off
        hcy = -220 + hcy_off
        hcz = mesh_z(hcx, hcy)
        _build_suburban_house(f"P3_Dilap_House_{k}", hcx, hcy, hcz,
                              facing=facing,
                              palette=dilap_palette[k % len(dilap_palette)])

    # 2 framed-only houses · just a slab + 4 corner studs + a
    # stack of lumber on top of the slab
    for k, (fcx, fcy) in enumerate(((-410, -240), (-400, -195))):
        fz = mesh_z(fcx, fcy)
        # Slab
        _make_box_local(f"P3_Framed_Slab_{k}",
                        (fcx, fcy, fz + 0.10),
                        (10.0, 8.0, 0.20),
                        (0.62, 0.58, 0.52, 1.0))
        # 4 corner studs
        for sx_off in (-4.5, 4.5):
            for sy_off in (-3.5, 3.5):
                _make_box_local(
                    f"P3_Framed_Stud_{k}_{int(sx_off)}_{int(sy_off)}",
                    (fcx + sx_off, fcy + sy_off, fz + 1.5),
                    (0.10, 0.10, 3.0),
                    (0.55, 0.42, 0.30, 1.0))
        # Lumber pile on the slab
        _make_box_local(f"P3_Framed_Lumber_{k}",
                        (fcx, fcy, fz + 0.45),
                        (2.0, 0.40, 0.40),
                        (0.55, 0.42, 0.30, 1.0))

    # Debris pile at the road's dead-end
    dx, dy = road_pts[-1]
    dz = mesh_z(dx, dy)
    _make_box_local("P3_DebrisPile",
                    (dx + 5, dy - 5, dz + 0.50),
                    (4.0, 4.0, 1.0), COL_DIRT)
    # "STOP CONSTRUCTION" sign on a leaning post
    _make_cyl_local("P3_SignPost",
                    (dx, dy + 6, dz + 1.0),
                    0.06, 2.0, (0.55, 0.42, 0.30, 1.0), segments=4)
    _make_box_local("P3_SignFace",
                    (dx, dy + 6, dz + 2.0),
                    (0.80, 0.04, 0.60),
                    (0.78, 0.62, 0.22, 1.0))


def build_east_cds_neighborhood():
    """East CDS Estates — east-ridge mid-tier neighborhood,
    curving collector road with a cul-de-sac branch heading
    north. Sits in EastCDS settlement zone (180..440, 20..260,
    target_z = +8.0, flatness 0.80).
    """
    road_w = 6.0
    curb_w = 0.5
    COL_ROAD = (0.20, 0.20, 0.22, 1.0)
    COL_CURB = (0.78, 0.76, 0.70, 1.0)
    hw = road_w / 2

    def _emit_road(pts, prefix):
        for i in range(len(pts) - 1):
            x0, y0 = pts[i]; x1, y1 = pts[i + 1]
            dxs = x1 - x0; dys = y1 - y0
            seg_len = math.hypot(dxs, dys) or 1.0
            perp_x = -dys / seg_len
            perp_y =  dxs / seg_len
            rv = []
            for (rx, ry) in [(x0 - perp_x * hw, y0 - perp_y * hw),
                             (x1 - perp_x * hw, y1 - perp_y * hw),
                             (x1 + perp_x * hw, y1 + perp_y * hw),
                             (x0 + perp_x * hw, y0 + perp_y * hw)]:
                rv.append((rx, ry, mesh_z(rx, ry) + 0.04))
            _finalize_mesh(f"{prefix}Road_{i}", rv, [[0, 1, 2, 3]],
                            COL_ROAD)
            for sgn in (-1, 1):
                cv = []
                for (rx, ry) in [(x0 + sgn * perp_x * hw,
                                  y0 + sgn * perp_y * hw),
                                 (x1 + sgn * perp_x * hw,
                                  y1 + sgn * perp_y * hw),
                                 (x1 + sgn * perp_x * (hw + curb_w),
                                  y1 + sgn * perp_y * (hw + curb_w)),
                                 (x0 + sgn * perp_x * (hw + curb_w),
                                  y0 + sgn * perp_y * (hw + curb_w))]:
                    cv.append((rx, ry, mesh_z(rx, ry) + 0.10))
                _finalize_mesh(f"{prefix}Curb_{i}_{sgn:+d}", cv,
                                [[0, 1, 2, 3]], COL_CURB)

    # Curving collector — Ridge Crest Dr
    collector = [(200, 140), (240, 130), (300, 130), (360, 140),
                  (420, 150)]
    _emit_road(collector, "ECDS_Coll_")
    # Cul-de-sac spur north
    spur = [(300, 130), (300, 180), (320, 220)]
    _emit_road(spur, "ECDS_Spur_")
    # Cul-de-sac bulb at (320, 220)
    cul_x, cul_y = 320, 220
    cul_r = 9.0
    segs = 12
    cul_verts = [(cul_x, cul_y, mesh_z(cul_x, cul_y) + 0.04)]
    for i in range(segs):
        ang = 2.0 * math.pi * i / segs
        vx = cul_x + math.cos(ang) * cul_r
        vy = cul_y + math.sin(ang) * cul_r
        cul_verts.append((vx, vy, mesh_z(vx, vy) + 0.04))
    cul_faces = []
    for i in range(segs):
        ni = (i + 1) % segs
        cul_faces.append([0, 1 + i, 1 + ni])
    _finalize_mesh("ECDS_CulDeSac", cul_verts, cul_faces, COL_ROAD)

    # Houses · cookie-cutter palette, varied roof colours
    cds_palette = [
        {'wall': (0.85, 0.82, 0.74, 1.0), 'roof': (0.32, 0.22, 0.18, 1.0)},
        {'wall': (0.80, 0.78, 0.70, 1.0), 'roof': (0.42, 0.30, 0.22, 1.0)},
        {'wall': (0.78, 0.74, 0.66, 1.0), 'roof': (0.45, 0.30, 0.22, 1.0)},
        {'wall': (0.82, 0.78, 0.68, 1.0), 'roof': (0.55, 0.30, 0.22, 1.0)},
    ]
    setback = 14.0
    house_idx = 0
    # Houses along the collector — alternating sides per segment
    for pidx in range(len(collector) - 1):
        x0, y0 = collector[pidx]; x1, y1 = collector[pidx + 1]
        dxs = x1 - x0; dys = y1 - y0
        seg_len = math.hypot(dxs, dys) or 1.0
        perp_x = -dys / seg_len
        perp_y =  dxs / seg_len
        mid_x = (x0 + x1) / 2
        mid_y = (y0 + y1) / 2
        for side_sgn in (-1, +1):
            hcx = mid_x + side_sgn * perp_x * setback
            hcy = mid_y + side_sgn * perp_y * setback
            hcz = mesh_z(hcx, hcy)
            facing = '+Y' if side_sgn == -1 else '-Y'
            palette = cds_palette[house_idx % len(cds_palette)]
            _build_suburban_house(
                f"ECDS_Coll_House_{pidx}_{side_sgn:+d}",
                hcx, hcy, hcz, facing=facing, palette=palette)
            curb_x = mid_x + side_sgn * perp_x * (hw + curb_w + 0.5)
            curb_y = mid_y + side_sgn * perp_y * (hw + curb_w + 0.5)
            _build_driveway(
                f"ECDS_Coll_House_{pidx}_{side_sgn:+d}_Drive",
                hcx, hcy, hcz, facing, curb_x, curb_y)
            house_idx += 1
    # 4 houses around the cul-de-sac bulb at 0°, 90°, 180°, 270° (skip 270° = inlet)
    for k, ang_deg in enumerate((30, 90, 150, 270)):
        ang_r = math.radians(ang_deg)
        hcx = cul_x + math.cos(ang_r) * (cul_r + 12.0)
        hcy = cul_y + math.sin(ang_r) * (cul_r + 12.0)
        hcz = mesh_z(hcx, hcy)
        # Face cardinal-closest direction toward the bulb
        dx = -math.cos(ang_r); dy = -math.sin(ang_r)
        if abs(dx) > abs(dy):
            facing = '+X' if dx > 0 else '-X'
        else:
            facing = '+Y' if dy > 0 else '-Y'
        palette = cds_palette[(house_idx + k) % len(cds_palette)]
        _build_suburban_house(
            f"ECDS_Cul_House_{k}", hcx, hcy, hcz,
            facing=facing, palette=palette)
        curb_x = cul_x + math.cos(ang_r) * (cul_r + 0.5)
        curb_y = cul_y + math.sin(ang_r) * (cul_r + 0.5)
        _build_driveway(f"ECDS_Cul_House_{k}_Drive", hcx, hcy, hcz,
                         facing, curb_x, curb_y)


def build_north_ranch_neighborhood():
    """NorthRanch — second-tier residential, ranch-style. Bigger
    lots, longer setbacks, single-story houses (rough placeholders
    just reuse the suburban-house builder for now). Two parallel
    east-west streets connected by a north-south spur, with houses
    on both sides of each street.

    Settlement zone (-460..-200 x, 20..260 y, target_z = +12.0,
    flatness 0.80).
    """
    road_w = 6.0
    curb_w = 0.5
    COL_ROAD = (0.20, 0.20, 0.22, 1.0)
    COL_CURB = (0.78, 0.76, 0.70, 1.0)
    COL_DASH = (0.95, 0.85, 0.30, 1.0)
    hw = road_w / 2

    def _emit_road_polyline(pts, prefix):
        for i in range(len(pts) - 1):
            x0, y0 = pts[i]
            x1, y1 = pts[i + 1]
            dxs = x1 - x0; dys = y1 - y0
            seg_len = math.hypot(dxs, dys) or 1.0
            perp_x = -dys / seg_len
            perp_y =  dxs / seg_len
            rv = []
            for (rx, ry) in [(x0 - perp_x * hw, y0 - perp_y * hw),
                             (x1 - perp_x * hw, y1 - perp_y * hw),
                             (x1 + perp_x * hw, y1 + perp_y * hw),
                             (x0 + perp_x * hw, y0 + perp_y * hw)]:
                rv.append((rx, ry, mesh_z(rx, ry) + 0.04))
            _finalize_mesh(f"{prefix}Road_{i}", rv, [[0, 1, 2, 3]],
                            COL_ROAD)
            for sgn in (-1, 1):
                cv = []
                for (rx, ry) in [(x0 + sgn * perp_x * hw,
                                  y0 + sgn * perp_y * hw),
                                 (x1 + sgn * perp_x * hw,
                                  y1 + sgn * perp_y * hw),
                                 (x1 + sgn * perp_x * (hw + curb_w),
                                  y1 + sgn * perp_y * (hw + curb_w)),
                                 (x0 + sgn * perp_x * (hw + curb_w),
                                  y0 + sgn * perp_y * (hw + curb_w))]:
                    cv.append((rx, ry, mesh_z(rx, ry) + 0.10))
                _finalize_mesh(f"{prefix}Curb_{i}_{sgn:+d}", cv,
                                [[0, 1, 2, 3]], COL_CURB)

    # Two parallel east-west streets ("Aspen" north + "Birch" south)
    aspen = [(-440, 200), (-380, 200), (-320, 200), (-240, 200)]
    birch = [(-440, 100), (-380, 100), (-320, 100), (-240, 100)]
    # North-south spur connecting them at x=-320 (middle)
    spur = [(-320, 200), (-320, 100)]
    _emit_road_polyline(aspen, "NRAspen_")
    _emit_road_polyline(birch, "NRBirch_")
    _emit_road_polyline(spur, "NRSpur_")

    # 12 houses · 3 per side of each east-west street, spaced
    # ~50 m apart (matches ranch-style spacious lots)
    ranch_palette = [
        {'wall': (0.72, 0.68, 0.55, 1.0), 'roof': (0.45, 0.30, 0.22, 1.0)},
        {'wall': (0.78, 0.74, 0.65, 1.0), 'roof': (0.32, 0.22, 0.18, 1.0)},
        {'wall': (0.82, 0.78, 0.68, 1.0), 'roof': (0.55, 0.30, 0.22, 1.0)},
        {'wall': (0.62, 0.68, 0.72, 1.0), 'roof': (0.42, 0.32, 0.22, 1.0)},
    ]
    setback = 18.0   # bigger than Phase 2's 12 m
    house_idx = 0
    for street_name, street_pts in (("Aspen", aspen), ("Birch", birch)):
        for k in range(3):
            x_mid = (street_pts[k][0] + street_pts[k + 1][0]) / 2
            y_mid = street_pts[k][1]
            for side_sgn, facing_n, facing_s in ((+1, '-Y', '-Y'),
                                                   (-1, '+Y', '+Y')):
                hcx = x_mid
                hcy = y_mid + side_sgn * setback
                if street_name == "Aspen":
                    facing = '-Y' if side_sgn > 0 else '+Y'
                else:
                    facing = '-Y' if side_sgn > 0 else '+Y'
                hcz = mesh_z(hcx, hcy)
                palette = ranch_palette[house_idx % len(ranch_palette)]
                _build_suburban_house(
                    f"NR_{street_name}_House_{k}_{side_sgn:+d}",
                    hcx, hcy, hcz,
                    facing=facing, palette=palette)
                # Driveway to the curb
                curb_x = x_mid
                curb_y = y_mid + side_sgn * (hw + curb_w + 0.5)
                _build_driveway(
                    f"NR_{street_name}_House_{k}_{side_sgn:+d}_Drive",
                    hcx, hcy, hcz, facing, curb_x, curb_y)
                house_idx += 1


def build_west_estates_neighborhood():
    """West Estates neighborhood — straight east-west arterial
    'Magnolia Lane' with a branch loop. Sits in the WestEstates
    settlement zone (-460..-120 x, -340..-40 y, target_z = -3.0,
    flatness 0.78). 6 houses with driveways along the arterial
    + 4 along the loop branch.
    """
    # Arterial waypoints — west to east through the middle of
    # the zone, gentle dip in the centre
    arterial_pts = [
        (-440, -180),
        (-380, -185),
        (-320, -190),
        (-260, -185),
        (-200, -180),
        (-140, -175),
    ]
    # Loop branch — small closed loop north of the arterial.
    # Last waypoint closes back to the first so the loop is a
    # real ring (was open-ended, leaving the road dead-ending in
    # the middle of the neighborhood).
    loop_pts = [
        (-320, -190),
        (-300, -150),
        (-340, -130),
        (-380, -150),
        (-360, -190),
        (-320, -190),   # close back to start
    ]

    road_w = 6.0
    curb_w = 0.5
    COL_ROAD = (0.20, 0.20, 0.22, 1.0)
    COL_CURB = (0.78, 0.76, 0.70, 1.0)
    COL_DASH = (0.95, 0.85, 0.30, 1.0)
    hw = road_w / 2

    def _emit_road_polyline(pts, prefix):
        for i in range(len(pts) - 1):
            x0, y0 = pts[i]
            x1, y1 = pts[i + 1]
            dxs = x1 - x0; dys = y1 - y0
            seg_len = math.hypot(dxs, dys) or 1.0
            perp_x = -dys / seg_len
            perp_y =  dxs / seg_len
            rv = []
            for (rx, ry) in [(x0 - perp_x * hw, y0 - perp_y * hw),
                             (x1 - perp_x * hw, y1 - perp_y * hw),
                             (x1 + perp_x * hw, y1 + perp_y * hw),
                             (x0 + perp_x * hw, y0 + perp_y * hw)]:
                rv.append((rx, ry, mesh_z(rx, ry) + 0.04))
            _finalize_mesh(f"{prefix}Road_{i}", rv, [[0, 1, 2, 3]],
                            COL_ROAD)
            for sgn in (-1, 1):
                cv = []
                for (rx, ry) in [(x0 + sgn * perp_x * hw,
                                  y0 + sgn * perp_y * hw),
                                 (x1 + sgn * perp_x * hw,
                                  y1 + sgn * perp_y * hw),
                                 (x1 + sgn * perp_x * (hw + curb_w),
                                  y1 + sgn * perp_y * (hw + curb_w)),
                                 (x0 + sgn * perp_x * (hw + curb_w),
                                  y0 + sgn * perp_y * (hw + curb_w))]:
                    cv.append((rx, ry, mesh_z(rx, ry) + 0.10))
                _finalize_mesh(f"{prefix}Curb_{i}_{sgn:+d}", cv,
                                [[0, 1, 2, 3]], COL_CURB)
            mid_x = (x0 + x1) / 2
            mid_y = (y0 + y1) / 2
            dx_len = 2.0
            ddx = dxs / seg_len * dx_len / 2
            ddy = dys / seg_len * dx_len / 2
            dv = []
            for (rx, ry) in [(mid_x - ddx - perp_x * 0.08,
                              mid_y - ddy - perp_y * 0.08),
                             (mid_x + ddx - perp_x * 0.08,
                              mid_y + ddy - perp_y * 0.08),
                             (mid_x + ddx + perp_x * 0.08,
                              mid_y + ddy + perp_y * 0.08),
                             (mid_x - ddx + perp_x * 0.08,
                              mid_y - ddy + perp_y * 0.08)]:
                dv.append((rx, ry, mesh_z(rx, ry) + 0.055))
            _finalize_mesh(f"{prefix}Dash_{i}", dv, [[0, 1, 2, 3]],
                            COL_DASH)

    _emit_road_polyline(arterial_pts, "WEArtl_")
    _emit_road_polyline(loop_pts, "WELoop_")

    # ── HOUSES along the arterial · alternating sides
    arterial_houses = [
        ("WE_House_A1", 0, -1, '+Y',
            {'wall': (0.78, 0.72, 0.58, 1.0),
             'roof': (0.42, 0.30, 0.22, 1.0)}),
        ("WE_House_A2", 1, +1, '-Y',
            {'wall': (0.85, 0.78, 0.65, 1.0),
             'roof': (0.32, 0.22, 0.18, 1.0)}),
        ("WE_House_A3", 2, -1, '+Y',
            {'wall': (0.72, 0.78, 0.65, 1.0),
             'roof': (0.55, 0.30, 0.20, 1.0)}),
        ("WE_House_A4", 3, +1, '-Y',
            {'wall': (0.82, 0.75, 0.60, 1.0),
             'roof': (0.32, 0.30, 0.26, 1.0)}),
        ("WE_House_A5", 4, -1, '+Y',
            {'wall': (0.78, 0.68, 0.55, 1.0),
             'roof': (0.42, 0.32, 0.22, 1.0)}),
    ]
    for name, pidx, side_sgn, facing, palette in arterial_houses:
        x0, y0 = arterial_pts[pidx]
        x1, y1 = arterial_pts[pidx + 1]
        dxs = x1 - x0; dys = y1 - y0
        seg_len = math.hypot(dxs, dys) or 1.0
        perp_x = -dys / seg_len
        perp_y =  dxs / seg_len
        mid_x = (x0 + x1) / 2
        mid_y = (y0 + y1) / 2
        hcx = mid_x + side_sgn * perp_x * 18.0
        hcy = mid_y + side_sgn * perp_y * 18.0
        hcz = mesh_z(hcx, hcy)
        _build_suburban_house(name, hcx, hcy, hcz,
                              facing=facing, palette=palette)
        curb_x = mid_x + side_sgn * perp_x * (hw + curb_w + 0.5)
        curb_y = mid_y + side_sgn * perp_y * (hw + curb_w + 0.5)
        _build_driveway(f"{name}_Drive", hcx, hcy, hcz, facing,
                         curb_x, curb_y)

    # ── HOUSES along the loop branch · only one per LONG side
    # of the diamond — placing houses on every segment puts
    # adjacent outer-corner houses too close (the inner diamond
    # is only ~44 m per side and 18 m off-road placement collides
    # adjacent houses around sharp corners).
    # House facings here are toward the road (opposite the perp
    # offset direction from road centre). L1's road is east → L1
    # faces +X. L4's road is west → L4 faces -X.
    loop_houses = [
        ("WE_House_L1", 0, +1, '+X',
            {'wall': (0.82, 0.78, 0.70, 1.0),
             'roof': (0.42, 0.30, 0.22, 1.0)}),
        ("WE_House_L4", 3, +1, '-X',
            {'wall': (0.72, 0.78, 0.68, 1.0),
             'roof': (0.42, 0.30, 0.22, 1.0)}),
    ]
    for name, pidx, side_sgn, facing, palette in loop_houses:
        x0, y0 = loop_pts[pidx]
        x1, y1 = loop_pts[pidx + 1]
        dxs = x1 - x0; dys = y1 - y0
        seg_len = math.hypot(dxs, dys) or 1.0
        perp_x = -dys / seg_len
        perp_y =  dxs / seg_len
        mid_x = (x0 + x1) / 2
        mid_y = (y0 + y1) / 2
        hcx = mid_x + side_sgn * perp_x * 18.0
        hcy = mid_y + side_sgn * perp_y * 18.0
        hcz = mesh_z(hcx, hcy)
        _build_suburban_house(name, hcx, hcy, hcz,
                              facing=facing, palette=palette)
        curb_x = mid_x + side_sgn * perp_x * (hw + curb_w + 0.5)
        curb_y = mid_y + side_sgn * perp_y * (hw + curb_w + 0.5)
        _build_driveway(f"{name}_Drive", hcx, hcy, hcz, facing,
                         curb_x, curb_y)


def build_phase2_neighborhood():
    """Phase II residential neighborhood — winding cul-de-sac
    road through the settlement zone (40..240 x, -260..-100 y,
    target_z = +1.0). 6 houses nestled along a curving asphalt
    road, each with its own driveway connecting to the curb.

    Road layout: enters from the east edge of Phase 2 at
    (240, -150), winds northwest then southwest in a gentle S
    curve, ending in a cul-de-sac at (70, -210). Houses
    alternate sides of the road for varied composition.
    """
    # ── ROAD WAYPOINTS forming a winding cul-de-sac ─────────────
    road_pts = [
        (240, -150),   # east entry from the Phase 2 boundary
        (210, -160),
        (180, -150),
        (150, -160),
        (120, -180),
        (90,  -200),
        (70,  -210),   # cul-de-sac centre
    ]
    road_w = 6.0
    curb_w = 0.5
    COL_ROAD = (0.20, 0.20, 0.22, 1.0)
    COL_CURB = (0.78, 0.76, 0.70, 1.0)
    COL_DASH = (0.95, 0.85, 0.30, 1.0)
    hw = road_w / 2
    for i in range(len(road_pts) - 1):
        x0, y0 = road_pts[i]
        x1, y1 = road_pts[i + 1]
        dxs = x1 - x0; dys = y1 - y0
        seg_len = math.hypot(dxs, dys) or 1.0
        perp_x = -dys / seg_len
        perp_y =  dxs / seg_len
        # Road segment
        rv = []
        for (rx, ry) in [(x0 - perp_x * hw, y0 - perp_y * hw),
                         (x1 - perp_x * hw, y1 - perp_y * hw),
                         (x1 + perp_x * hw, y1 + perp_y * hw),
                         (x0 + perp_x * hw, y0 + perp_y * hw)]:
            rv.append((rx, ry, mesh_z(rx, ry) + 0.04))
        _finalize_mesh(f"P2Road_{i}", rv, [[0, 1, 2, 3]], COL_ROAD)
        # Curb strips on each side · inner edge flush with road
        # edge at hw, outer edge at hw + curb_w. Previous code
        # used (hw + curb_w/2) for the inner edge, leaving a
        # 0.25 m visible gap between road and curb.
        for sgn in (-1, 1):
            cv = []
            for (rx, ry) in [(x0 + sgn * perp_x * hw,
                              y0 + sgn * perp_y * hw),
                             (x1 + sgn * perp_x * hw,
                              y1 + sgn * perp_y * hw),
                             (x1 + sgn * perp_x * (hw + curb_w),
                              y1 + sgn * perp_y * (hw + curb_w)),
                             (x0 + sgn * perp_x * (hw + curb_w),
                              y0 + sgn * perp_y * (hw + curb_w))]:
                cv.append((rx, ry, mesh_z(rx, ry) + 0.10))
            _finalize_mesh(f"P2Curb_{i}_{sgn:+d}", cv, [[0,1,2,3]], COL_CURB)
        # Centerline dash (one per segment, in the middle)
        mid_x = (x0 + x1) / 2
        mid_y = (y0 + y1) / 2
        dx_len = 2.0
        ddx = dxs / seg_len * dx_len / 2
        ddy = dys / seg_len * dx_len / 2
        dv = []
        for (rx, ry) in [(mid_x - ddx - perp_x * 0.08, mid_y - ddy - perp_y * 0.08),
                         (mid_x + ddx - perp_x * 0.08, mid_y + ddy - perp_y * 0.08),
                         (mid_x + ddx + perp_x * 0.08, mid_y + ddy + perp_y * 0.08),
                         (mid_x - ddx + perp_x * 0.08, mid_y - ddy + perp_y * 0.08)]:
            dv.append((rx, ry, mesh_z(rx, ry) + 0.055))
        _finalize_mesh(f"P2RoadDash_{i}", dv, [[0,1,2,3]], COL_DASH)

    # Cul-de-sac circular asphalt at the road end
    cul_x, cul_y = road_pts[-1]
    cul_r = 9.0
    segs = 12
    cul_verts = [(cul_x, cul_y, mesh_z(cul_x, cul_y) + 0.04)]
    for i in range(segs):
        ang = 2.0 * math.pi * i / segs
        vx = cul_x + math.cos(ang) * cul_r
        vy = cul_y + math.sin(ang) * cul_r
        cul_verts.append((vx, vy, mesh_z(vx, vy) + 0.04))
    cul_faces = []
    for i in range(segs):
        ni = (i + 1) % segs
        cul_faces.append([0, 1 + i, 1 + ni])
    _finalize_mesh("P2Road_CulDeSac", cul_verts, cul_faces, COL_ROAD)

    # ── 5 HOUSES around the cul-de-sac BULB · radiating from
    # the bulb centre, each facing toward the bulb. Skip the
    # inlet angle (270°/west, where the access road arrives).
    cul_house_specs = [
        (30,  '-X', {'wall': (0.80, 0.76, 0.68, 1.0), 'roof': (0.42, 0.30, 0.22, 1.0)}),
        (90,  '-Y', {'wall': (0.70, 0.74, 0.62, 1.0), 'roof': (0.55, 0.20, 0.16, 1.0)}),
        (150, '+X', {'wall': (0.82, 0.75, 0.60, 1.0), 'roof': (0.32, 0.30, 0.26, 1.0)}),
        (210, '+X', {'wall': (0.65, 0.68, 0.78, 1.0), 'roof': (0.42, 0.30, 0.22, 1.0)}),
        (330, '-X', {'wall': (0.85, 0.82, 0.72, 1.0), 'roof': (0.32, 0.22, 0.18, 1.0)}),
    ]
    cul_setback = 21.0    # bulb r 9 + setback 12 m
    for k, (ang_deg, facing, palette) in enumerate(cul_house_specs):
        ang_r = math.radians(ang_deg)
        hcx = cul_x + math.cos(ang_r) * cul_setback
        hcy = cul_y + math.sin(ang_r) * cul_setback
        hcz = mesh_z(hcx, hcy)
        _build_suburban_house(f"P2_Cul_House_{k}", hcx, hcy, hcz,
                              facing=facing, palette=palette)
        # Driveway to the cul-de-sac edge
        curb_x = cul_x + math.cos(ang_r) * (cul_r + 0.5)
        curb_y = cul_y + math.sin(ang_r) * (cul_r + 0.5)
        _build_driveway(f"P2_Cul_House_{k}_Drive", hcx, hcy, hcz,
                         facing, curb_x, curb_y)

    # ── HOUSES placed along the arterial · alternating sides,
    # closer to road (12 m off-road, was 18 m) so the
    # neighborhood reads as TIGHT-PACKED suburban per the
    # aerial reference photos.
    house_specs = [
        ("P2_House_A", 0, -1, '-Y',
            {'wall': (0.82, 0.78, 0.70, 1.0), 'roof': (0.45, 0.30, 0.22, 1.0)}),
        ("P2_House_B", 1, +1, '+Y',
            {'wall': (0.78, 0.68, 0.55, 1.0), 'roof': (0.32, 0.22, 0.18, 1.0)}),
        ("P2_House_C", 2, -1, '-Y',
            {'wall': (0.85, 0.82, 0.72, 1.0), 'roof': (0.55, 0.20, 0.16, 1.0)}),
        ("P2_House_D", 3, +1, '+Y',
            {'wall': (0.72, 0.78, 0.68, 1.0), 'roof': (0.42, 0.32, 0.22, 1.0)}),
        ("P2_House_E", 4, -1, '-Y',
            {'wall': (0.82, 0.75, 0.60, 1.0), 'roof': (0.32, 0.30, 0.26, 1.0)}),
        ("P2_House_F", 5, +1, '+Y',
            {'wall': (0.65, 0.68, 0.78, 1.0), 'roof': (0.42, 0.30, 0.22, 1.0)}),
    ]
    arterial_setback = 12.0
    for name, pidx, side_sgn, facing, palette in house_specs:
        # Compute road tangent + normal at this segment
        x0, y0 = road_pts[pidx]
        x1, y1 = road_pts[pidx + 1]
        dxs = x1 - x0; dys = y1 - y0
        seg_len = math.hypot(dxs, dys) or 1.0
        perp_x = -dys / seg_len
        perp_y =  dxs / seg_len
        mid_x = (x0 + x1) / 2
        mid_y = (y0 + y1) / 2
        hcx = mid_x + side_sgn * perp_x * arterial_setback
        hcy = mid_y + side_sgn * perp_y * arterial_setback
        hcz = mesh_z(hcx, hcy)
        _build_suburban_house(name, hcx, hcy, hcz,
                              facing=facing, palette=palette)
        # Driveway from house's garage to a curb point on the road
        curb_x = mid_x + side_sgn * perp_x * (hw + curb_w + 0.5)
        curb_y = mid_y + side_sgn * perp_y * (hw + curb_w + 0.5)
        _build_driveway(f"{name}_Drive", hcx, hcy, hcz, facing,
                         curb_x, curb_y)
        # Small grass lawn box between road and house (visual fill)
        # Skipped — terrain vertex colors handle the green already


def build_nexcorp_hq():
    """NexCorp Corporate HQ public-facing front. The PR-friendly
    face of the megacorp that owns the chapter-one gas station.
    Sits on the North Commercial belt at (0, 300) so the player
    sees it from the spawn approach south through HCE.

    Building: 3-story office-block silhouette with a glass curtain
    wall on the south face, recessed entry, a reflecting pool out
    front, and the corporate logo above the entry.
    """
    cx, cy = 0.0, 300.0
    ground_z = mesh_z(cx, cy)
    name_prefix = "NexCorpHQ"

    # Dimensions — bigger than convenience store, smaller than a
    # real skyscraper. 3 stories.
    width = 32.0      # E-W
    depth = 18.0      # N-S
    story_h = 3.5
    n_stories = 3
    total_h = story_h * n_stories     # 10.5 m
    wall_t = 0.20

    # Materials — corporate
    col_wall  = (0.92, 0.92, 0.90, 1.0)        # off-white tower skin
    col_trim  = (0.42, 0.42, 0.45, 1.0)        # steel band
    col_glass = (0.32, 0.55, 0.78, 0.6)        # tinted curtain wall
    col_floor_slab = (0.78, 0.76, 0.72, 1.0)
    col_roof  = (0.32, 0.32, 0.35, 1.0)
    col_logo_bg = (0.18, 0.32, 0.55, 1.0)
    col_logo_text = (0.95, 0.95, 0.94, 1.0)

    # Footprint slab (asphalt-tone for the surrounding plaza)
    _make_box_local(f"{name_prefix}_PlazaSlab",
                    (cx, cy - 1.0, ground_z + 0.05),
                    (width + 16.0, depth + 12.0, 0.10),
                    (0.85, 0.82, 0.74, 1.0))     # cream plaza pavers

    # Main building shell — solid walls on N/E/W, glass curtain
    # on S (south = facing toward the player approaching from
    # spawn area)
    _make_box_local(f"{name_prefix}_WallN",
                    (cx, cy + depth / 2 - wall_t / 2,
                     ground_z + total_h / 2),
                    (width, wall_t, total_h), col_wall)
    _make_box_local(f"{name_prefix}_WallE",
                    (cx + width / 2 - wall_t / 2, cy,
                     ground_z + total_h / 2),
                    (wall_t, depth, total_h), col_wall)
    _make_box_local(f"{name_prefix}_WallW",
                    (cx - width / 2 + wall_t / 2, cy,
                     ground_z + total_h / 2),
                    (wall_t, depth, total_h), col_wall)

    # Glass curtain wall on south face — 3 vertical bays per
    # story, in a grid of mullions surrounding tinted glass panels
    glass_y = cy - depth / 2 + 0.05
    n_vert_mullions = 7      # 6 bays across the width
    for k in range(n_vert_mullions):
        mx = cx - width / 2 + 0.3 + k * (width - 0.6) / (n_vert_mullions - 1)
        _make_box_local(f"{name_prefix}_GlassMul_V_{k}",
                        (mx, glass_y, ground_z + total_h / 2),
                        (0.20, 0.10, total_h), col_trim)
    # Horizontal mullions at each floor band (3 of them)
    for k in range(n_stories + 1):
        bz = ground_z + k * story_h
        _make_box_local(f"{name_prefix}_GlassMul_H_{k}",
                        (cx, glass_y, bz),
                        (width - 0.3, 0.12, 0.30), col_trim)
    # Glass panels per bay-per-story (visual fill — slightly
    # smaller than the bay so the mullion grid reads)
    bay_w = (width - 0.3) / 6
    for k_x in range(6):
        for k_y in range(n_stories):
            px = cx - width / 2 + 0.3 + (k_x + 0.5) * bay_w
            pz = ground_z + (k_y + 0.5) * story_h
            _make_box_local(f"{name_prefix}_GlassPanel_{k_x}_{k_y}",
                            (px, glass_y - 0.02, pz),
                            (bay_w - 0.20, 0.04, story_h - 0.30),
                            col_glass)

    # Floor slabs at story boundaries (visible through the glass
    # from outside)
    for k in range(1, n_stories):
        sz = ground_z + k * story_h
        _make_box_local(f"{name_prefix}_FloorSlab_{k}",
                        (cx, cy, sz),
                        (width - 0.4, depth - 0.4, 0.30),
                        col_floor_slab)

    # Roof + parapet
    _make_box_local(f"{name_prefix}_Roof",
                    (cx, cy, ground_z + total_h + 0.10),
                    (width + 0.4, depth + 0.4, 0.20), col_roof)
    # Parapet wall — taller than convenience-store version
    parapet_h = 0.80
    pz_centre = ground_z + total_h + 0.20 + parapet_h / 2
    for sgn_y, tag in ((-1, 'S'), (+1, 'N')):
        _make_box_local(f"{name_prefix}_Parapet_{tag}",
                        (cx, cy + sgn_y * (depth + 0.4) / 2,
                         pz_centre),
                        (width + 0.4, 0.20, parapet_h), col_trim)
    for sgn_x, tag in ((-1, 'W'), (+1, 'E')):
        _make_box_local(f"{name_prefix}_Parapet_{tag}",
                        (cx + sgn_x * (width + 0.4) / 2, cy,
                         pz_centre),
                        (0.20, depth + 0.4, parapet_h), col_trim)

    # ── ENTRY — double doors at the centre of the south curtain
    # wall, coplanar with the glass so they read as part of the
    # facade (rather than 1.5 m inside, where the player can't
    # reach them). Door spans 3 m wide × 2.6 m tall.
    entry_y = glass_y
    door_w = 3.0
    door_h = 2.6
    # Door frame
    _make_box_local(f"{name_prefix}_DoorFrame_L",
                    (cx - door_w / 2, entry_y, ground_z + door_h / 2),
                    (0.20, 0.30, door_h), col_trim)
    _make_box_local(f"{name_prefix}_DoorFrame_R",
                    (cx + door_w / 2, entry_y, ground_z + door_h / 2),
                    (0.20, 0.30, door_h), col_trim)
    _make_box_local(f"{name_prefix}_DoorHeader",
                    (cx, entry_y, ground_z + door_h + 0.20),
                    (door_w + 0.6, 0.30, 0.40), col_trim)
    # Two door leaves (dark tinted)
    for sgn in (-1, 1):
        _make_box_local(f"{name_prefix}_Door_{sgn:+d}",
                        (cx + sgn * door_w / 4, entry_y,
                         ground_z + door_h / 2),
                        (door_w / 2 - 0.12, 0.06, door_h - 0.10),
                        (0.10, 0.18, 0.32, 1.0))
    # Welcome mat outside
    _make_box_local(f"{name_prefix}_DoorMat",
                    (cx, entry_y - 1.2, ground_z + 0.07),
                    (door_w + 0.40, 1.20, 0.02),
                    (0.18, 0.32, 0.55, 1.0))

    # ── CORPORATE LOGO PANEL above the entry — large illuminated
    # rectangle with "NEXCORP" text and a small NexCorp diamond
    # graphic.
    logo_y = cy - depth / 2 - 0.20
    logo_z = ground_z + total_h - 1.2
    _make_box_local(f"{name_prefix}_LogoPanel",
                    (cx, logo_y, logo_z),
                    (12.0, 0.14, 1.80), col_logo_bg)
    _make_box_local(f"{name_prefix}_LogoPanelTrim",
                    (cx, logo_y, logo_z + 1.0),
                    (12.2, 0.16, 0.12), col_trim)
    # Small NexCorp diamond ahead of the text (a flat diamond
    # rotated 45° won't render rotated since we use AABBs, so
    # build it as a square white "badge")
    _make_box_local(f"{name_prefix}_LogoDiamond",
                    (cx - 5.6, logo_y, logo_z),
                    (0.80, 0.20, 0.80), col_logo_text)

    # ── REFLECTING POOL out front — stone rim (solid base box)
    # with water disc on TOP of the rim, inset slightly so the
    # rim reads as a border. Previously water was inside the rim
    # box (z 0.13-0.23 with rim z 0..0.40) so the water was
    # invisible.
    pool_cy = cy - depth / 2 - 6.0
    pool_w = 14.0
    pool_d = 4.0
    pool_rim_h = 0.40
    _make_box_local(f"{name_prefix}_PoolRim",
                    (cx, pool_cy, ground_z + pool_rim_h / 2),
                    (pool_w + 0.6, pool_d + 0.6, pool_rim_h),
                    (0.78, 0.74, 0.66, 1.0))
    # Water sits ON TOP of the rim, inset 0.3 m so the rim shows
    # around the perimeter.
    _make_box_local(f"{name_prefix}_PoolWater",
                    (cx, pool_cy, ground_z + pool_rim_h + 0.02),
                    (pool_w - 0.3, pool_d - 0.3, 0.04),
                    (0.32, 0.55, 0.78, 1.0))

    # ── HEDGE BORDERS flanking the entry walkway. Hedge sits in
    # the 4 m gap between the building south face (cy - 9) and
    # the pool north edge (cy - 11): centred at cy - 10 with
    # depth 2.0 m, height 1.1 m. Clear of both building and pool.
    for sgn in (-1, 1):
        hedge_x = cx + sgn * (door_w / 2 + 1.6)
        _make_box_local(f"{name_prefix}_HedgeFront_{sgn:+d}",
                        (hedge_x, cy - depth / 2 - 1.5,
                         ground_z + 0.55),
                        (0.60, 2.0, 1.10),
                        (0.20, 0.42, 0.18, 1.0))

    # ── PARKING LOT to the south of the plaza
    lot_cy = pool_cy - 14.0
    lot_w = 36.0
    lot_d = 14.0
    hw_lot = lot_w / 2; hd_lot = lot_d / 2
    lv = []
    for (lx, ly) in [(cx - hw_lot, lot_cy - hd_lot),
                     (cx + hw_lot, lot_cy - hd_lot),
                     (cx + hw_lot, lot_cy + hd_lot),
                     (cx - hw_lot, lot_cy + hd_lot)]:
        lv.append((lx, ly, mesh_z(lx, ly) + 0.04))
    _finalize_mesh(f"{name_prefix}_Lot", lv, [[0, 1, 2, 3]],
                    (0.22, 0.22, 0.24, 1.0))
    # Stripes
    for k in range(7):
        sx_line = cx - hw_lot + (k + 1) * lot_w / 8
        sv = []
        for (lx, ly) in [(sx_line - 0.05, lot_cy - hd_lot + 0.3),
                          (sx_line + 0.05, lot_cy - hd_lot + 0.3),
                          (sx_line + 0.05, lot_cy + hd_lot - 0.3),
                          (sx_line - 0.05, lot_cy + hd_lot - 0.3)]:
            sv.append((lx, ly, mesh_z(lx, ly) + 0.055))
        _finalize_mesh(f"{name_prefix}_LotStripe_{k}", sv,
                        [[0, 1, 2, 3]], (0.92, 0.90, 0.84, 1.0))
    # 4 cars — corporate fleet (greys + blue)
    for k, (px_off, col) in enumerate(((
            -12, (0.42, 0.42, 0.45, 1.0)),
            (-4, (0.62, 0.62, 0.64, 1.0)),
            (4,  (0.32, 0.42, 0.55, 1.0)),
            (12, (0.20, 0.20, 0.22, 1.0)))):
        cpx = cx + px_off
        cpy = lot_cy + 1.0
        cpz = mesh_z(cpx, cpy)
        _build_parked_car(f"{name_prefix}_Car_{k}", cpx, cpy, cpz,
                           col, facing='+Y')

    # ── FLAGPOLES flanking the plaza — three poles with banners
    # (typical corporate: US flag, state flag, corporate flag)
    for k, (fp_x_off, banner_col) in enumerate((
            (-8, (0.85, 0.20, 0.20, 1.0)),
            (0,  (0.18, 0.32, 0.55, 1.0)),   # NexCorp blue
            (8,  (0.95, 0.95, 0.94, 1.0)))):
        fp_x = cx + fp_x_off
        fp_y = cy - depth / 2 - 11.0
        fp_z = mesh_z(fp_x, fp_y)
        _make_cyl_local(f"{name_prefix}_FlagPole_{k}",
                        (fp_x, fp_y, fp_z + 4.0),
                        0.08, 8.0, col_trim, segments=6)
        # Banner cloth hung from the pole
        _make_box_local(f"{name_prefix}_FlagBanner_{k}",
                        (fp_x + 0.50, fp_y, fp_z + 6.8),
                        (1.0, 0.02, 0.70), banner_col)


def build_strip_mall_nightclub():
    """Strip-mall night club on the West Commercial Highway 9
    frontage. Per user spec ("the strip mall night club"): a
    standalone after-hours venue with a dark windowless facade,
    a neon SCRATCH-style sign, a single recessed entry with a
    velvet rope, two bouncer markers, and a small parking lot.

    Settlement zone: WestComm (-560..-460 x, -340..260 y,
    target_z = -2.0). Building centred at (-510, 0).
    """
    cx, cy = -510.0, 0.0
    ground_z = mesh_z(cx, cy)
    name_prefix = "NightClub"

    # Building dimensions
    width = 22.0      # E-W
    depth = 14.0      # N-S
    height = 5.0      # taller than convenience store — feels imposing
    wall_t = 0.20

    # Materials — moody / dark night-club palette
    col_wall  = (0.18, 0.10, 0.22, 1.0)     # deep purple-black
    col_trim  = (0.95, 0.42, 0.62, 1.0)     # hot pink accent
    col_roof  = (0.10, 0.08, 0.12, 1.0)     # near-black
    col_neon_sign = (0.32, 0.18, 0.42, 1.0)  # base panel
    col_door = (0.10, 0.08, 0.12, 1.0)
    col_velvet = (0.62, 0.10, 0.22, 1.0)
    col_rope_stand = (0.85, 0.62, 0.20, 1.0)  # brass

    # Slab
    _make_box_local(f"{name_prefix}_Slab",
                    (cx, cy, ground_z + 0.05),
                    (width + 0.6, depth + 0.6, 0.10),
                    (0.62, 0.58, 0.50, 1.0))     # asphalt apron

    # Solid walls all four sides — no plate glass, this is a club
    _make_box_local(f"{name_prefix}_WallN",
                    (cx, cy + depth / 2 - wall_t / 2,
                     ground_z + height / 2),
                    (width, wall_t, height), col_wall)
    # South wall split LEFT + RIGHT + HEADER around the alcove
    # opening (alcove walls sit at cx ± 1.10 so the opening is
    # 2.20 m wide).
    alc_half = 1.10
    alc_open_top_z = 3.20      # opening height above ground
    left_w = width / 2 - alc_half
    _make_box_local(f"{name_prefix}_WallS_L",
                    (cx - alc_half - left_w / 2,
                     cy - depth / 2 + wall_t / 2,
                     ground_z + height / 2),
                    (left_w, wall_t, height), col_wall)
    _make_box_local(f"{name_prefix}_WallS_R",
                    (cx + alc_half + left_w / 2,
                     cy - depth / 2 + wall_t / 2,
                     ground_z + height / 2),
                    (left_w, wall_t, height), col_wall)
    # Header lintel over the opening
    _make_box_local(f"{name_prefix}_WallS_Header",
                    (cx, cy - depth / 2 + wall_t / 2,
                     ground_z + alc_open_top_z +
                     (height - alc_open_top_z) / 2),
                    (alc_half * 2, wall_t,
                     height - alc_open_top_z), col_wall)
    _make_box_local(f"{name_prefix}_WallE",
                    (cx + width / 2 - wall_t / 2, cy,
                     ground_z + height / 2),
                    (wall_t, depth, height), col_wall)
    _make_box_local(f"{name_prefix}_WallW",
                    (cx - width / 2 + wall_t / 2, cy,
                     ground_z + height / 2),
                    (wall_t, depth, height), col_wall)

    # Hot-pink accent stripe at mid-height — painted on the
    # EXTERIOR face of each wall (was at depth/2 - 0.10 which
    # placed it inside the wall thickness).
    for sgn_y, tag in ((-1, 'S'), (+1, 'N')):
        _make_box_local(f"{name_prefix}_PinkStripe_{tag}",
                        (cx, cy + sgn_y * (depth / 2 + 0.05),
                         ground_z + height * 0.65),
                        (width, 0.06, 0.22), col_trim)
    for sgn_x, tag in ((-1, 'W'), (+1, 'E')):
        _make_box_local(f"{name_prefix}_PinkStripe_{tag}",
                        (cx + sgn_x * (width / 2 + 0.05), cy,
                         ground_z + height * 0.65),
                        (0.06, depth, 0.22), col_trim)

    # Roof
    _make_box_local(f"{name_prefix}_Roof",
                    (cx, cy, ground_z + height + 0.10),
                    (width + 0.4, depth + 0.4, 0.20), col_roof)
    # Parapet on all four sides
    parapet_h = 0.60
    pz_centre = ground_z + height + 0.20 + parapet_h / 2
    for sgn_y, tag in ((-1, 'S'), (+1, 'N')):
        _make_box_local(f"{name_prefix}_Parapet_{tag}",
                        (cx, cy + sgn_y * (depth + 0.4) / 2,
                         pz_centre),
                        (width + 0.4, 0.18, parapet_h), col_wall)
    for sgn_x, tag in ((-1, 'W'), (+1, 'E')):
        _make_box_local(f"{name_prefix}_Parapet_{tag}",
                        (cx + sgn_x * (width + 0.4) / 2, cy,
                         pz_centre),
                        (0.18, depth + 0.4, parapet_h), col_wall)

    # Recessed entry on the SOUTH face — alcove with door + velvet
    # rope stanchions on each side.
    entry_y = cy - depth / 2 + 0.05
    door_w = 1.6
    door_h = 2.6
    # Entry alcove walls (two side walls forming an inset of
    # 1.0 m). Centered at half-height so the wall bottom is on
    # the ground; previous code (centre at 0.55 * height,
    # size 0.95 * height) had the bottom floating at 0.375 m
    # and the top poking above the building roofline.
    alcove_d = 1.2
    alc_wall_h = height * 0.95
    for sgn in (-1, 1):
        _make_box_local(f"{name_prefix}_AlcoveWall_{sgn:+d}",
                        (cx + sgn * (door_w / 2 + 0.15),
                         entry_y + alcove_d / 2,
                         ground_z + alc_wall_h / 2),
                        (0.30, alcove_d, alc_wall_h),
                        col_wall)
    # Door itself — solid black, slightly inset
    _make_box_local(f"{name_prefix}_EntryDoor",
                    (cx, entry_y + alcove_d, ground_z + door_h / 2),
                    (door_w, 0.06, door_h), col_door)
    # Door handle (small chrome bar)
    _make_cyl_local(f"{name_prefix}_DoorHandle",
                    (cx + door_w / 2 - 0.20,
                     entry_y + alcove_d - 0.06,
                     ground_z + 1.20),
                    0.03, 0.40, col_rope_stand, segments=4)

    # Velvet rope — 4 brass stanchions + red rope segments between
    # them, forming a queue line outside the door.
    rope_pts = [
        (cx - door_w / 2 - 0.30, entry_y - 0.50),
        (cx - door_w / 2 - 0.30, entry_y - 2.00),
        (cx + door_w / 2 + 0.30, entry_y - 2.00),
        (cx + door_w / 2 + 0.30, entry_y - 0.50),
    ]
    for k, (sx, sy) in enumerate(rope_pts):
        # Brass stanchion
        _make_cyl_local(f"{name_prefix}_Stanchion_{k}",
                        (sx, sy, ground_z + 0.50),
                        0.05, 1.00, col_rope_stand, segments=6)
        # Brass ball cap on top
        _make_sphere_low_local(f"{name_prefix}_StanchionCap_{k}",
                                (sx, sy, ground_z + 1.05),
                                0.08, col_rope_stand,
                                rings=3, segments=6)
    # Red rope segments between consecutive stanchions
    for k in range(3):
        p0 = rope_pts[k]
        p1 = rope_pts[k + 1]
        _build_oriented_handle(
            f"{name_prefix}_VelvetRope_{k}",
            (p0[0], p0[1], ground_z + 0.92),
            (p1[0], p1[1], ground_z + 0.92),
            radius=0.04, color=col_velvet)

    # ── BOUNCER POSITIONS — two bouncers flanking the door
    bouncer_specs = [
        (cx - door_w / 2 - 1.0, entry_y - 0.30),
        (cx + door_w / 2 + 1.0, entry_y - 0.30),
    ]
    for k, (bx_, by_) in enumerate(bouncer_specs):
        bz_ = mesh_z(bx_, by_)
        human_figure(
            name=f"NightClub_Bouncer_{k}",
            base_x=bx_, base_y=by_, base_z=bz_,
            scale=1.05,
            facing='-Y',
            skin_color=(0.62, 0.45, 0.36, 1.0),
            hair_style='short',
            hair_color=(0.10, 0.08, 0.10, 1.0),
            jacket_color=(0.10, 0.08, 0.12, 1.0),
            pants_color=(0.10, 0.08, 0.12, 1.0),
            shoe_color=(0.10, 0.08, 0.10, 1.0),
            has_sunglasses=True,
            sunglasses_color=(0.05, 0.05, 0.06, 1.0),
            with_ears=True,
            with_mouth=False,
        )

    # ── NEON SIGN on the south face above the entry — "SCRATCH"
    # in hot pink on a darker purple panel mounted to the parapet.
    sign_y = cy - depth / 2 - 0.18
    sign_h_local = 1.2
    _make_box_local(f"{name_prefix}_SignPanel",
                    (cx, sign_y, ground_z + height + 0.10 + sign_h_local / 2),
                    (10.0, 0.18, sign_h_local), col_neon_sign)
    # Pink neon tube border around the sign
    for sgn_x in (-1, 1):
        _make_box_local(f"{name_prefix}_SignNeon_E_{sgn_x:+d}",
                        (cx + sgn_x * 5.0, sign_y - 0.08,
                         ground_z + height + 0.10 + sign_h_local / 2),
                        (0.04, 0.04, sign_h_local - 0.10),
                        col_trim)
    for sgn_y_tube in (-1, 1):
        _make_box_local(f"{name_prefix}_SignNeon_H_{sgn_y_tube:+d}",
                        (cx, sign_y - 0.08,
                         ground_z + height + 0.10 + sign_h_local / 2 +
                         sgn_y_tube * (sign_h_local / 2 - 0.05)),
                        (10.0, 0.04, 0.04), col_trim)

    # ── PARKING LOT south of the building (entry road from
    # Highway 9 west). Asphalt slab + stripes + 3 cars.
    lot_cy = cy - 14.0
    lot_w = 26.0
    lot_d = 12.0
    hw = lot_w / 2; hd = lot_d / 2
    lv = []
    for (lx, ly) in [(cx - hw, lot_cy - hd),
                     (cx + hw, lot_cy - hd),
                     (cx + hw, lot_cy + hd),
                     (cx - hw, lot_cy + hd)]:
        lv.append((lx, ly, mesh_z(lx, ly) + 0.04))
    _finalize_mesh(f"{name_prefix}_Lot", lv, [[0, 1, 2, 3]],
                    (0.22, 0.22, 0.24, 1.0))
    # Stripes
    for k in range(5):
        sx_line = cx - hw + (k + 1) * lot_w / 6
        sv = []
        for (lx, ly) in [(sx_line - 0.05, lot_cy - hd + 0.3),
                          (sx_line + 0.05, lot_cy - hd + 0.3),
                          (sx_line + 0.05, lot_cy + hd - 0.3),
                          (sx_line - 0.05, lot_cy + hd - 0.3)]:
            sv.append((lx, ly, mesh_z(lx, ly) + 0.055))
        _finalize_mesh(f"{name_prefix}_LotStripe_{k}", sv,
                        [[0, 1, 2, 3]], (0.92, 0.90, 0.84, 1.0))
    # 3 cars
    for k, (px_off, col) in enumerate(((
            -8, (0.18, 0.18, 0.20, 1.0)),
            (0, (0.85, 0.20, 0.20, 1.0)),
            (8, (0.18, 0.22, 0.42, 1.0)))):
        cpx = cx + px_off
        cpy = lot_cy + 1.0
        cpz = mesh_z(cpx, cpy)
        _build_parked_car(f"{name_prefix}_Car_{k}", cpx, cpy, cpz,
                           col, facing='+Y')


def build_high_school_field():
    """Harmony Creek High School football field + stadium. Carved
    out of the new HighSchoolField settlement zone (240..440 x,
    -100..0 y, target +3.0 m, flatness 0.88).

    Layout (centred at (340, -50)):
      · 120 × 53 m green field with 5-yd lateral white stripes
      · 9 m end zones (one north, one south) in school colours
      · 1 m white sideline + end-line stripes
      · Running track ring around field (red oval)
      · Bleachers on EAST side (home) + smaller WEST side (visit)
      · 2 goalposts at each end zone
      · "HARMONY CREEK HIGH" pylon sign at the entrance
    """
    cx, cy = 340.0, -50.0
    ground_z = mesh_z(cx, cy)

    # Materials
    COL_GRASS_FIELD = (0.24, 0.55, 0.22, 1.0)
    COL_GRASS_STRIPE = (0.30, 0.62, 0.26, 1.0)   # alternating mowing
    COL_LINE = (0.95, 0.95, 0.94, 1.0)
    COL_ENDZONE_HOME = (0.20, 0.22, 0.55, 1.0)    # school navy
    COL_ENDZONE_AWAY = (0.85, 0.20, 0.20, 1.0)    # accent red
    COL_TRACK = (0.62, 0.22, 0.20, 1.0)           # rubberized red
    COL_BLEACHER_FRAME = (0.42, 0.42, 0.45, 1.0)
    COL_BLEACHER_BENCH = (0.62, 0.62, 0.64, 1.0)
    COL_GOALPOST = (0.95, 0.95, 0.94, 1.0)

    # ── FIELD slab (green) — 120 × 53 m. Top at ground_z + 0.08
    # so all the painted stripes can sit ABOVE it without being
    # buried inside the slab.
    field_w = 53.0
    field_l = 120.0
    grass_top_z = ground_z + 0.08
    _make_box_local("HSField_Grass",
                    (cx, cy, ground_z + 0.04),
                    (field_w, field_l, 0.08), COL_GRASS_FIELD)
    # Alternating mowing stripes (sit a hair above the grass top)
    n_stripes = 12
    stripe_w = field_l / n_stripes
    for k in range(n_stripes):
        if k % 2 == 0:
            sx_y = cy - field_l / 2 + (k + 0.5) * stripe_w
            _make_box_local(f"HSField_MowStripe_{k}",
                            (cx, sx_y, grass_top_z + 0.01),
                            (field_w - 0.4, stripe_w * 0.95, 0.02),
                            COL_GRASS_STRIPE)
    # 11 lateral 5-yard lines (above mowing stripes)
    n_lines = 11
    for k in range(n_lines):
        ly_pos = cy - field_l / 2 + (k + 1) * field_l / (n_lines + 1)
        _make_box_local(f"HSField_YardLine_{k}",
                        (cx, ly_pos, grass_top_z + 0.03),
                        (field_w - 0.4, 0.20, 0.02), COL_LINE)
    # Sidelines (E + W)
    for sgn in (-1, 1):
        _make_box_local(f"HSField_Sideline_{sgn:+d}",
                        (cx + sgn * (field_w / 2 - 0.15),
                         cy, grass_top_z + 0.03),
                        (0.30, field_l - 0.4, 0.02), COL_LINE)
    # End lines (N + S)
    for sgn in (-1, 1):
        _make_box_local(f"HSField_Endline_{sgn:+d}",
                        (cx, cy + sgn * (field_l / 2 - 0.15),
                         grass_top_z + 0.03),
                        (field_w - 0.4, 0.30, 0.02), COL_LINE)

    # ── END ZONES — 9 m extensions in school colours
    ez_d = 9.0
    for sgn, col, ez_tag in ((-1, COL_ENDZONE_HOME, "Home"),
                              (+1, COL_ENDZONE_AWAY, "Away")):
        _make_box_local(f"HSField_EndZone_{ez_tag}",
                        (cx, cy + sgn * (field_l / 2 + ez_d / 2),
                         ground_z + 0.04),
                        (field_w, ez_d, 0.08), col)

    # ── TRACK — red rubberized ring around the field. Built as a
    # ring of 36 quad segments forming an oval following the
    # rounded-rectangle shape (track typical: ~6m wide).
    track_w = 6.0
    field_half_l = field_l / 2 + ez_d   # outer end of end zones
    field_half_w = field_w / 2
    # Outer rectangle of track footprint:
    # straight sides + semi-circular ends
    segs_curve = 12
    inner_pts = []
    outer_pts = []
    # Top semi-circle (north end)
    for i in range(segs_curve + 1):
        t = i / segs_curve
        ang = math.pi * t              # 0..pi
        ix = math.cos(ang) * field_half_w
        iy = field_half_l + math.sin(ang) * field_half_w
        ox = math.cos(ang) * (field_half_w + track_w)
        oy = field_half_l + math.sin(ang) * (field_half_w + track_w)
        inner_pts.append((cx + ix, cy + iy))
        outer_pts.append((cx + ox, cy + oy))
    # Bottom semi-circle (south end) — angles pi..2pi
    for i in range(segs_curve + 1):
        t = i / segs_curve
        ang = math.pi + math.pi * t
        ix = math.cos(ang) * field_half_w
        iy = -field_half_l + math.sin(ang) * field_half_w
        ox = math.cos(ang) * (field_half_w + track_w)
        oy = -field_half_l + math.sin(ang) * (field_half_w + track_w)
        inner_pts.append((cx + ix, cy + iy))
        outer_pts.append((cx + ox, cy + oy))
    # Build the ring as quads between inner_pts[i] and outer_pts[i]
    track_verts = []
    for (ix, iy), (ox, oy) in zip(inner_pts, outer_pts):
        track_verts.append((ix, iy, grass_top_z))
        track_verts.append((ox, oy, grass_top_z))
    track_faces = []
    npairs = len(inner_pts)
    for i in range(npairs):
        # 4 verts per quad: inner_i, outer_i, outer_i+1, inner_i+1
        # The modulo closes the loop so the east straight side is
        # included (was missing — only 25 of 26 quads rendered).
        j = (i + 1) % npairs
        track_faces.append([i * 2, i * 2 + 1,
                            j * 2 + 1, j * 2])
    _finalize_mesh("HSField_Track", track_verts, track_faces,
                    COL_TRACK)

    # ── BLEACHERS — east side (home, larger) + west side (visit).
    # Each bleacher = stepped seating from front rail back to top.
    def _build_bleacher_block(name, bcx, bcy, n_rows=6, row_d=0.8,
                               row_h=0.40, length=60.0,
                               rise_dir_perp_sgn=1):
        """rise_dir_perp_sgn = +1 means the bleachers RISE toward
        +X (east-facing bleacher block, so home side west of
        field). -1 means rises toward -X."""
        # Frame backing wall — top sits ~1 m above the top bench
        # (so the wall reads as a real backstop, not a tower).
        back_top_z = n_rows * row_h + 1.0
        _make_box_local(f"{name}_BackWall",
                        (bcx + rise_dir_perp_sgn * (n_rows * row_d + 0.5),
                         bcy, ground_z + back_top_z / 2),
                        (0.20, length, back_top_z),
                        COL_BLEACHER_FRAME)
        # 6 stepped rows
        for k in range(n_rows):
            row_x_off = rise_dir_perp_sgn * (k * row_d + row_d / 2)
            row_z = k * row_h
            _make_box_local(f"{name}_Step_{k}",
                            (bcx + row_x_off, bcy,
                             ground_z + row_z + row_h / 2),
                            (row_d, length, row_h),
                            COL_BLEACHER_FRAME)
            # Bench on top of the step
            _make_box_local(f"{name}_Bench_{k}",
                            (bcx + row_x_off, bcy,
                             ground_z + row_z + row_h + 0.04),
                            (row_d * 0.85, length - 0.4, 0.08),
                            COL_BLEACHER_BENCH)
        # Front rail (low metal pipe at first step)
        _make_box_local(f"{name}_FrontRail",
                        (bcx - rise_dir_perp_sgn * 0.10,
                         bcy, ground_z + 0.85),
                        (0.06, length, 0.10),
                        COL_BLEACHER_FRAME)

    # HOME bleachers on the EAST side (rises east-facing toward +X)
    home_bx = cx + field_w / 2 + track_w + 2.0
    _build_bleacher_block("HSField_Home", home_bx, cy,
                          n_rows=8, length=80.0,
                          rise_dir_perp_sgn=+1)
    # VISIT bleachers on the WEST side (smaller)
    visit_bx = cx - field_w / 2 - track_w - 2.0
    _build_bleacher_block("HSField_Visit", visit_bx, cy,
                          n_rows=5, length=50.0,
                          rise_dir_perp_sgn=-1)

    # ── GOAL POSTS at each end zone
    for sgn, ez_tag in ((-1, "Home"), (+1, "Away")):
        gp_y = cy + sgn * (field_l / 2 + ez_d)
        gp_base_z = ground_z + 0.04
        # Vertical pole (single, behind end line)
        _make_cyl_local(f"HSField_GP_{ez_tag}_Base",
                        (cx, gp_y, gp_base_z + 3.0),
                        0.08, 6.0, COL_GOALPOST, segments=6)
        # Crossbar at top of vertical pole, perpendicular
        _make_box_local(f"HSField_GP_{ez_tag}_Crossbar",
                        (cx, gp_y, gp_base_z + 6.0),
                        (5.6, 0.10, 0.10), COL_GOALPOST)
        # Two upright posts on the crossbar
        for sx_off in (-2.6, 2.6):
            _make_cyl_local(f"HSField_GP_{ez_tag}_Upright_{int(sx_off*10):+d}",
                            (cx + sx_off, gp_y,
                             gp_base_z + 8.0),
                            0.06, 4.0, COL_GOALPOST, segments=6)

    # ── SCOREBOARD on the north (away) end behind the end zone.
    # Two poles tall enough that the name banner above the score
    # panel is fully supported.
    sb_y = cy + field_l / 2 + ez_d + 8.0
    sb_z = ground_z
    pole_h = 9.5
    for sgn_x in (-1, 1):
        _make_cyl_local(f"HSField_Scoreboard_Pole_{sgn_x:+d}",
                        (cx + sgn_x * 4.0, sb_y, sb_z + pole_h / 2),
                        0.20, pole_h, COL_BLEACHER_FRAME, segments=6)
    _make_box_local("HSField_Scoreboard_Panel",
                    (cx, sb_y, sb_z + 6.0),
                    (10.0, 0.20, 3.0),
                    (0.20, 0.22, 0.28, 1.0))
    # School name banner above the scoreboard panel
    _make_box_local("HSField_Scoreboard_NameBanner",
                    (cx, sb_y, sb_z + 8.4),
                    (10.0, 0.10, 0.80),
                    (0.20, 0.22, 0.55, 1.0))

    # ── HARMONY CREEK HIGH SCHOOL BUILDING — long brick-fronted
    # building NORTH of the field. The football field is on the
    # school's south lawn; the school sits between the field and
    # the EastCDS neighborhood to the north.
    sch_cx, sch_cy = cx, 50.0
    sch_w = 40.0     # E-W
    sch_d = 14.0     # N-S
    sch_h = 6.0
    sch_t = 0.20
    col_brick   = (0.55, 0.32, 0.22, 1.0)
    col_sch_trim = (0.85, 0.82, 0.74, 1.0)
    col_sch_roof = (0.32, 0.30, 0.28, 1.0)
    col_door_red = (0.78, 0.18, 0.18, 1.0)
    col_glass   = (0.32, 0.42, 0.55, 1.0)
    sch_z = mesh_z(sch_cx, sch_cy)
    # Walls (all four solid)
    _make_box_local("HSBuilding_Slab",
                    (sch_cx, sch_cy, sch_z + 0.05),
                    (sch_w + 0.6, sch_d + 0.6, 0.10), col_sch_trim)
    _make_box_local("HSBuilding_WallN",
                    (sch_cx, sch_cy + sch_d / 2 - sch_t / 2,
                     sch_z + sch_h / 2),
                    (sch_w, sch_t, sch_h), col_brick)
    _make_box_local("HSBuilding_WallE",
                    (sch_cx + sch_w / 2 - sch_t / 2, sch_cy,
                     sch_z + sch_h / 2),
                    (sch_t, sch_d, sch_h), col_brick)
    _make_box_local("HSBuilding_WallW",
                    (sch_cx - sch_w / 2 + sch_t / 2, sch_cy,
                     sch_z + sch_h / 2),
                    (sch_t, sch_d, sch_h), col_brick)
    # South wall — split with central entry opening
    sch_door_w = 4.0
    sch_door_h = 3.0
    sch_left_w = sch_w / 2 - sch_door_w / 2
    _make_box_local("HSBuilding_WallS_L",
                    (sch_cx - sch_door_w / 2 - sch_left_w / 2,
                     sch_cy - sch_d / 2 + sch_t / 2,
                     sch_z + sch_h / 2),
                    (sch_left_w, sch_t, sch_h), col_brick)
    _make_box_local("HSBuilding_WallS_R",
                    (sch_cx + sch_door_w / 2 + sch_left_w / 2,
                     sch_cy - sch_d / 2 + sch_t / 2,
                     sch_z + sch_h / 2),
                    (sch_left_w, sch_t, sch_h), col_brick)
    _make_box_local("HSBuilding_WallS_Header",
                    (sch_cx, sch_cy - sch_d / 2 + sch_t / 2,
                     sch_z + sch_door_h + (sch_h - sch_door_h) / 2),
                    (sch_door_w, sch_t, sch_h - sch_door_h),
                    col_brick)
    # Roof + parapet
    _make_box_local("HSBuilding_Roof",
                    (sch_cx, sch_cy, sch_z + sch_h + 0.10),
                    (sch_w + 0.4, sch_d + 0.4, 0.20), col_sch_roof)
    # Front door (red double leaves)
    sch_glass_y = sch_cy - sch_d / 2 + 0.05
    for sgn in (-1, 1):
        _make_box_local(f"HSBuilding_Door_{sgn:+d}",
                        (sch_cx + sgn * sch_door_w / 4,
                         sch_glass_y,
                         sch_z + sch_door_h / 2),
                        (sch_door_w / 2 - 0.12, 0.06,
                         sch_door_h - 0.10),
                        col_door_red)
    # Welcome mat
    _make_box_local("HSBuilding_DoorMat",
                    (sch_cx, sch_glass_y - 0.5, sch_z + 0.07),
                    (sch_door_w + 0.40, 0.80, 0.02),
                    (0.32, 0.22, 0.18, 1.0))
    # Front windows — rows of classroom windows along the south
    # wall (8 windows on each side of the central door)
    win_z = sch_z + 3.5
    for k in range(8):
        # West-side windows
        wx_pos = sch_cx - sch_door_w / 2 - (k + 1) * 2.0
        if wx_pos > sch_cx - sch_w / 2 + 1.0:
            _make_box_local(f"HSBuilding_WinW_{k}",
                            (wx_pos, sch_glass_y, win_z),
                            (1.2, 0.04, 1.4), col_glass)
        # East-side windows
        wx_pos_e = sch_cx + sch_door_w / 2 + (k + 1) * 2.0
        if wx_pos_e < sch_cx + sch_w / 2 - 1.0:
            _make_box_local(f"HSBuilding_WinE_{k}",
                            (wx_pos_e, sch_glass_y, win_z),
                            (1.2, 0.04, 1.4), col_glass)
    # Brick band trim at the parapet
    _make_box_local("HSBuilding_TrimBand_S",
                    (sch_cx, sch_cy - sch_d / 2 - 0.05,
                     sch_z + sch_h - 0.30),
                    (sch_w + 0.4, 0.10, 0.30),
                    col_sch_trim)
    # School name plaque centered above the entry
    _make_box_local("HSBuilding_NamePlaque",
                    (sch_cx, sch_cy - sch_d / 2 - 0.15,
                     sch_z + sch_h + 0.30),
                    (sch_w * 0.5, 0.14, 1.0),
                    (0.20, 0.22, 0.55, 1.0))
    # Two flagpoles flanking the entry (US + state)
    for sgn, banner_col in ((-1, (0.85, 0.20, 0.20, 1.0)),
                             (+1, (0.20, 0.22, 0.55, 1.0))):
        fp_x = sch_cx + sgn * (sch_door_w / 2 + 3.0)
        fp_y = sch_cy - sch_d / 2 - 4.0
        fp_z = mesh_z(fp_x, fp_y)
        _make_cyl_local(f"HSBuilding_FlagPole_{sgn:+d}",
                        (fp_x, fp_y, fp_z + 3.5),
                        0.08, 7.0, col_sch_trim, segments=6)
        _make_box_local(f"HSBuilding_FlagBanner_{sgn:+d}",
                        (fp_x + 0.40, fp_y, fp_z + 5.9),
                        (0.80, 0.02, 0.60), banner_col)

    # ── PARKING LOT north of the school building (student lot).
    # Lot oriented so cars face south (toward the school) using
    # the existing Y-axis _build_parked_car helper.
    sl_cx = sch_cx
    sl_cy = sch_cy + sch_d / 2 + 13.0      # 6 m gap to school + lot
    sl_w = 28.0    # E-W (along the wider face of the school)
    sl_d = 12.0    # N-S (lot depth)
    hw_sl = sl_w / 2; hd_sl = sl_d / 2
    sl_v = []
    for (lx, ly) in [(sl_cx - hw_sl, sl_cy - hd_sl),
                     (sl_cx + hw_sl, sl_cy - hd_sl),
                     (sl_cx + hw_sl, sl_cy + hd_sl),
                     (sl_cx - hw_sl, sl_cy + hd_sl)]:
        sl_v.append((lx, ly, mesh_z(lx, ly) + 0.04))
    _finalize_mesh("HSBuilding_Lot", sl_v, [[0, 1, 2, 3]],
                    (0.22, 0.22, 0.24, 1.0))
    # 6 painted stripes splitting the lot into 7 bays along x
    for k in range(6):
        sx_line = sl_cx - hw_sl + (k + 1) * sl_w / 7
        sv = []
        for (lx, ly) in [(sx_line - 0.05, sl_cy - hd_sl + 0.3),
                          (sx_line + 0.05, sl_cy - hd_sl + 0.3),
                          (sx_line + 0.05, sl_cy + hd_sl - 0.3),
                          (sx_line - 0.05, sl_cy + hd_sl - 0.3)]:
            sv.append((lx, ly, mesh_z(lx, ly) + 0.055))
        _finalize_mesh(f"HSBuilding_LotStripe_{k}", sv,
                        [[0, 1, 2, 3]], (0.92, 0.90, 0.84, 1.0))
    # 7 student cars facing SOUTH (toward the school)
    student_palette = [
        (0.85, 0.20, 0.20, 1.0),     # red
        (0.62, 0.62, 0.64, 1.0),     # silver
        (0.18, 0.32, 0.55, 1.0),     # blue
        (0.32, 0.55, 0.25, 1.0),     # green
        (0.20, 0.20, 0.22, 1.0),     # black
        (0.95, 0.85, 0.30, 1.0),     # yellow
        (0.62, 0.42, 0.78, 1.0),     # purple
    ]
    for k, col in enumerate(student_palette):
        cpx = sl_cx - hw_sl + (k + 0.5) * sl_w / 7
        cpy = sl_cy + 1.0
        cpz = mesh_z(cpx, cpy)
        _build_parked_car(f"HSBuilding_Car_{k}", cpx, cpy, cpz,
                           col, facing='-Y')


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
    build_phase2_neighborhood()
    build_west_estates_neighborhood()
    build_north_ranch_neighborhood()
    build_east_cds_neighborhood()
    build_phase3_neighborhood()
    build_country_club()
    build_harmony_park()
    build_district_arterials()
    build_community_landmarks()
    build_connector_roads()
    build_elementary_school()
    build_truck_stop()
    build_east_commercial_box()
    build_bus_stops()
    build_arterial_lighting()
    build_church_cemetery()
    build_water_tower_and_lines()
    build_halsey_studios()
    build_hospital()
    build_drive_in_theatre()
    build_arterial_sidewalks()
    build_high_school_field()
    build_strip_mall_nightclub()
    build_nexcorp_hq()
    export_glb()


if __name__ == "__main__":
    main()
