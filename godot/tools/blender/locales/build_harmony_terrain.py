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

# Cell size ~10 m. Bumped from 15 m (80×56) to 120×84 in the
# 2026-06-15 infrastructure-alignment grind. Finer cells = smoother
# road-shoulder cut/fill slopes (the visible "terracing" at
# carve-shoulder boundaries was the 15 m grid aliasing the 36 m
# arterial shoulder onto only ~2 cells across). At 10 m cells the
# 36 m shoulder spans ~3.6 cells, giving a smoother batter.
# Cost: ~2.25× more terrain vertices (10080 vs 4480). Still under
# 5s build on the deck.
GROUND_NX = 120
GROUND_NY = 84

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
    # Updated 2026-06-15 to match the new CREEK_CHANNEL re-route
    # around NorthRanch (was slicing through Aspen Street). Used
    # only by creek_distance() for the base-terrain Gaussian dip
    # and the bank-color landuse classifier; the actual carve
    # lives in CREEK_CHANNEL.
    (-560,  360),
    (-500,  340),
    (-440,  310),
    (-340,  300),
    (-260,  280),
    (-180,  240),
    (-160,  200),
    (-160,  140),
    (-120,   80),
    ( -80,    0),
    (  40,  -70),
    ( 160, -140),
    ( 280, -190),
    ( 400, -240),
    ( 500, -310),
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
    # Country club + golf — peak prosperity, top of the hill.
    # Flatness 0.85 -> 0.92 for uniform fairways/greens.
    ("CountryClub", -460, 440, 340, 420, +22.0, 0.92),
    # North Ranch Homes — second-highest tier. Flatness raised
    # 0.80 -> 0.90 (2026-06-15) so houses between streets read at
    # the platform target (+12) instead of 2m below it (the old
    # 0.80 let 20% of base terrain leak through, so the inter-
    # street strips read +9.9 while the streets themselves were
    # carved cleanly to +12).
    ("NorthRanch",  -460, -200, 20, 260, +12.0, 0.90),
    # East CDS Estates — sits on the east ridge. South edge moved
    # from y=20 to y=120 (2026-06-15) so it no longer OVERLAPS the
    # HighSchoolField settlement (-130..110). Flatness 0.80 -> 0.90.
    ("EastCDS",     180, 440, 120, 260, +8.0, 0.90),
    # Phase II construction (under occupancy) — middle tier.
    # Flatness 0.75 -> 0.90.
    ("Phase2",      40, 240, -260, -100, +1.0, 0.90),
    # West Estates (single-family) — modest lowland. 0.78 -> 0.90.
    ("WestEstates", -460, -120, -340, -40, -3.0, 0.90),
    # Phase III construction (Norman Lott) — gone-to-seed low
    ("Phase3",      -460, -260, -340, -180, -8.0, 0.70),
    # North Commercial Belt — between CC and Ranch, sloped.
    # Flatness raised 0.75 -> 0.88 (2026-06-15) so the belt reads
    # uniformly at +14 instead of varying +10..+18 from base terrain
    # leaking through (CC's Gaussian decay was bleeding into the
    # belt's north edge).
    ("NorthComm",   -460, 440, 260, 340, +14.0, 0.88),
    # East Commercial — flatness 0.80 -> 0.90
    ("EastComm",    440, 540, -340, 260, +5.0, 0.90),
    # West Commercial Strip (Highway 9 lowland)
    ("WestComm",    -560, -460, -340, 260, -2.0, 0.90),
    # South Commercial / Truck Stop (low — truck route)
    ("SouthComm",   -460, 440, -400, -340, -9.0, 0.90),
    # Harmony Park (manicured — flatter than wild, less than housing)
    ("HarmonyPark", -120, 180, -40, 200, +1.0, 0.55),
    # Dedicated platform around the Oliver Tree statue so the
    # walkways + benches + reflecting pool all sit flat. Flatness
    # raised 0.80 -> 0.95 (2026-06-15) so OT Park's nested
    # platform wins over its containing NorthRanch (+12) in the
    # softmax blend — without this the park reads at +5 instead
    # of its design +2.
    ("OliverTreeMemPark", -300, -220, 60, 180, +2.0, 0.95),
    # Secluded skatepark — sunken 2.5 m below the memorial park
    # platform so it reads as tucked away. Flatness raised
    # 0.90 -> 0.97 (2026-06-15) so it wins softmax over OT Park
    # (0.95) and NR (0.80) — the doubly-nested settlement.
    ("OTSkatePark",       -300, -260, 65, 100, -0.5, 0.97),
    # Harmony Creek High School football field + stadium platform
    # — large flat zone east of Phase 2 (between Phase 2 and the
    # East Commercial strip) for the field + bleachers. Expanded
    # to cover the track ring and end zones (total ~80 x 150 m,
    # rather than the field alone).
    ("HighSchoolField", 200, 480, -130, 110, +3.0, 0.98),
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
SETTLEMENT_FALLOFF = 20.0   # m of smooth transition outside each rect
# Reduced from 35m to 20m (2026-06-15) so adjacent settlements
# don't pull each other's interiors. With the new weighted-blend
# averaging, a 35m falloff at a settlement boundary made the
# football field's north edge ramp 2m up toward East CDS Estates'
# +8 platform. 20m falloff keeps the field flat at +3 and confines
# the cross-blend to the actual boundary strip.

# ────────────────────────────────────────────────────────────────
# ROAD CORRIDORS — civil-engineering road cuts. Humans don't drape
# asphalt over rolling hills; they EXCAVATE the terrain to follow a
# designed grade, with controlled cross-slope and shoulder gradient.
# Per the user (2026-06-15): "you can carve the terrain to accommodate
# roads, humans do. they level things and have gradual slopes on roads
# where it makes sense. use civil engineering to design this suburb."
#
# Each corridor: polyline of (x, y, target_z) waypoints + full-grade
# half-width + shoulder transition width. Inside the full-grade band
# the terrain is FORCED to road grade (target_z interpolated along
# the polyline between waypoints). Outside the band, over the shoulder
# distance, terrain smoothly grades back to the natural+settlement
# height. Beyond shoulder, terrain unchanged.
#
# target_z values match the adjoining settlement platform heights so
# arterials thread smoothly between zones (e.g. Harmony Blvd descends
# from +20 at the country club entry down to -9 at the south truck
# route, hitting each settlement's deck height on the way).
#
# Format: (name, [(x, y, z), ...], full_half_w, shoulder_w)
# ────────────────────────────────────────────────────────────────
ROAD_CORRIDORS = [
    # ── HARMONY BOULEVARD · N-S arterial. Descends from the country
    # club hill (+22) down to the SouthComm truck route (-9). Each
    # waypoint's z matches the settlement platform it crosses.
    # Subdivided to ≤40 m segments so the carved grade reads smooth
    # across the 15 m mesh grid (longer segments showed visible
    # kinks at each polyline vertex).
    # Targets ALIGNED TO SETTLEMENT PLATFORMS so the road doesn't
    # ride visibly above flat zones. The road only changes
    # elevation in the TRANSITION strips between settlements
    # (which IS where humans place ramps). Inside HarmonyPark
    # (y -40 .. 200, +1) the road stays at +1; the climb to
    # NorthComm happens y=200..260 (60m, +13m -> 22% peak).
    # FLAT through each settlement; only ramps in the transition
    # strips BETWEEN zones. Updated 2026-06-15 to AVOID bisecting
    # Country Club building (y=363..377, x=-18..18) and NexCorp HQ
    # building (y=288..312, x=-15..15) — both used to overlap the
    # road quad. Road now swings EAST around HQ + terminates south
    # of CC building.
    ("HarmonyBlvd", [
        (   0,  350, +22.0),   # well south of CC south face (y=363) — road quad north edge at 358.5 stays clear
        # CC -> NorthComm ramp (y=350..330, +22 -> +14)
        (   5,  343, +20.5),
        (  12,  335, +18.0),
        (  20,  325, +16.0),
        (  27,  315, +14.0),
        # NorthComm zone: swing EAST around NexCorp HQ (x=-15..15)
        # at x=27 the road WEST edge is 18.5 — clear of HQ x=15.
        (  27,  300, +14.0),
        (  27,  280, +14.0),
        (  22,  265, +14.0),
        (  14,  260, +14.0),
        # NorthComm -> HarmonyPark ramp (y=260..200, +14 -> +1, 60m, 22% peak)
        (  15,  245, +12.0),
        (  22,  225,  +8.0),
        (  30,  205,  +2.5),
        # HarmonyPark zone (y=-40..200 +1): flat through
        (  44,  190,  +1.0),
        (  56,  170,  +1.0),
        (  60,  140,  +1.0),
        (  60,  100,  +1.0),
        (  60,   60,  +1.0),
        (  60,   20,  +1.0),
        (  56,  -20,  +1.0),
        (  44,  -38,  +1.0),
        # HarmonyPark -> wild zone -> SouthComm gradual descent
        # (y=-40..-340 +1 -> -9, 300m, 3.3% avg). South end swings
        # EAST to x=14 so HBlvd's road quad (8.5m hw) doesn't reach
        # into the Kwik Shop strip's east edge at x=-1.
        (  36,  -70,  -0.5),
        (  28, -110,  -2.0),
        (  22, -150,  -3.5),
        (  18, -190,  -4.5),
        (  16, -230,  -5.5),
        (  14, -270,  -6.5),
        (  13, -310,  -8.0),
        # SouthComm zone (y=-400..-340 -9): flat through, x=14
        # keeps the road quad clear of Kwik Shop strip (x<=-1)
        # and Diner (x>=25).
        (  13, -340,  -9.0),
        (  14, -370,  -9.0),
        (  14, -385,  -9.0),
        (  14, -392,  -9.0),
    ], 8.5, 22.0),

    # ── HORIZON DRIVE · E-W arterial. From WestComm (-2) east to
    # EastComm (+5), threading through Harmony Park (0) and crossing
    # Harmony Blvd at the central junction (0).
    # FLAT through each settlement; ramps only in transition strips.
    ("HorizonDr", [
        # WestComm zone (x=-560..-460 -2): flat at -2
        (-560,  -20,  -2.0),
        (-510,  -20,  -2.0),
        (-460,  -20,  -2.0),   # WestComm boundary
        # WestComm -> HarmonyPark transition (x=-460..-180, -2 -> +1)
        # 280m for a 3m change = 1.1% grade
        (-420,  -20,  -1.6),
        (-360,  -18,  -1.0),
        (-300,  -15,  -0.3),
        (-240,  -18,  +0.5),
        # HarmonyPark zone (x=-120..180, y=-40..200 +1): flat at +1
        (-180,  -20,  +1.0),   # HarmonyPark south edge
        (-130,  -25,  +1.0),
        ( -80,  -30,  +1.0),
        ( -40,  -30,  +1.0),
        (  10,  -25,  +1.0),
        (  60,  -20,  +1.0),   # junction with Harmony Blvd
        ( 110,  -15,  +1.5),
        ( 160,  -10,  +2.0),   # HarmonyPark east edge transition
        # HSField zone (x=200..480, y=-130..110 +3): flat at +3
        ( 210,  -10,  +3.0),
        ( 260,  -10,  +3.0),
        ( 320,   -5,  +3.0),
        ( 380,    0,  +3.0),
        # HSField -> EastComm transition (x=380..480, +3 -> +5)
        # 100m for 2m = 2% grade
        ( 420,    0,  +4.0),
        ( 460,    0,  +5.0),
        # EastComm zone (x=440..540 +5): flat at +5
        ( 510,    0,  +5.0),
        ( 560,    0,  +5.0),
    ], 8.5, 22.0),

    # ── CONNECTOR ROADS · short 5 m collectors. full-grade half-width
    # smaller because the road is narrower.
    # Phase 2 → Horizon Dr east
    ("P2Link", [
        (240, -150, +1.0),   # Phase2 platform
        (260,  -80,  0.0),
        (260,  -10,  +2.5),  # Horizon Dr east approach
    ], 5.0, 16.0),

    # West Estates → Horizon Dr west. Endpoint at HorizonDr CL
    # y=-17.5 (lerp between (-460,-20) and (-420,-15) at x=-440).
    ("WELink", [
        (-440, -180, -3.0),  # WestEstates
        (-440, -100, -2.5),
        (-440,  -60, -2.2),
        (-440,  -17, -2.0),  # at Horizon Dr WestComm CL
    ], 5.0, 16.0),

    # North Ranch → Harmony Blvd. STARTS at the east edge of NR
    # (x=-200) so it doesn't overlap NRBirch (which runs y=100 from
    # x=-440 to x=-240). The old NRLink started at (-320, 100) and
    # carried target_z +12 -> +10 along the same y=100 line, so
    # both corridors carved the same strip but at different
    # gradients — Birch tilted east where NRLink crossed it.
    # New path exits NR at x=-200, ramps down to HBlvd at +1 over
    # ~270m (3.3% grade) through the wild zone south of NR.
    ("NRLink", [
        (-200, 100, +10.0),  # east edge of NR on Birch line
        (-140, 110,  +7.0),  # wild zone descent
        ( -80, 120,  +4.0),
        (   0, 125,  +2.5),
        (  40, 128,  +1.5),
        (  60, 130,  +1.0),  # at HarmonyBlvd centerline
    ], 5.0, 16.0),

    # East CDS → Horizon Dr east
    ("ECDSLink", [
        (200, 140, +8.0),   # EastCDS
        (200,  80, +6.0),
        (220,  20, +4.0),
        (260, -10, +3.0),   # Horizon Dr
    ], 5.0, 16.0),

    # East Commercial collector — at x=440 (the EastComm west edge)
    # so the buildings centered at x=480 (Halsey, Self-Storage,
    # Auto dealership, Big-Box) sit fully east of the road with
    # ~40 m of parking-lot frontage between road and building. The
    # original collector at x=480 had every EastComm building
    # sitting INSIDE the road quad.
    ("ECommN", [
        (438,   0, +5.0),
        (440,  20, +5.0),
        (440,  60, +5.0),
        (440, 100, +5.0),
    ], 5.0, 16.0),
    ("ECommS", [
        (440,    0, +5.0),
        (440, -100, +5.0),
        (440, -180, +5.0),
        (440, -260, +5.0),
    ], 5.0, 16.0),

    # SCRATCH link (WestComm). Endpoint trimmed to (-490, 0) so
    # the 5m hw road quad sits CLEAR of the SCRATCH building east
    # face (x=-495) by 0m at the face — the road ends AT the
    # building entrance, doesn't push inside.
    ("WCommLink", [
        (-460, -20, -2.0),
        (-475, -10, -2.0),
        (-490,   0, -2.0),
    ], 5.0, 14.0),

    # Truck stop access
    ("TSLink", [
        (100, -392, -9.0),
        (160, -390, -9.0),
        (200, -385, -9.0),
    ], 5.0, 14.0),

    # Drive-in theatre access — gradual climb to drive-in pad (-5).
    # Re-routed 2026-06-15: old path went through the Diner at
    # (35, -360). New path runs EAST along the chapter-1 frontage
    # at y=-385, then turns NORTH between Cosmic Comics and the
    # Taqueria (the gap at x=110-130), then NE to the drive-in.
    ("DILink", [
        (  12, -392, -9.0),    # at HarmonyBlvd south end
        (  50, -388, -9.0),    # along frontage
        (  90, -385, -9.0),
        ( 110, -383, -8.5),    # gap east of Cosmic Comics
        ( 115, -355, -7.0),    # turning north
        ( 130, -320, -6.0),
        ( 150, -290, -5.0),
        ( 150, -280, -5.0),    # at drive-in pad
    ], 5.0, 14.0),

    # Country Club south driveway. Endpoint trimmed from y=360
    # (which put CCLink's 5m road quad 2m inside CC building at
    # y=363) to y=358 — quad north edge at 363, just touching
    # building south face.
    ("CCLink", [
        (   0, 358, +22.0),
        (   0, 348, +21.5),
    ], 5.0, 12.0),

    # OT Park access — from Horizon Dr north to OT Park south entry.
    # Aligned with build_ot_park_access_road actual polyline.
    ("OTLink", [
        (-260, -15, -1.0),   # Horizon Dr (existing emit y)
        (-260,  20,  0.0),
        (-260,  55, +1.5),   # park entry beacon
    ], 4.0, 12.0),

    # Hospital access — Horizon → Hospital lot
    ("HospLink", [
        (180,  -10, +1.5),   # Horizon
        (180,   60, +4.0),
        (180,  140, +8.0),
        (180,  220, +12.0),
        (180,  280, +14.0),  # at Hospital pad
    ], 5.0, 14.0),

    # NexCorp HQ driveway off Harmony Blvd. Per civil-engineering
    # standard the gradient should be at most ~10% so the approach
    # ramp climbs the +3 (at HarmonyBlvd CL y=170) to +14 (at
    # NexCorpHQPad south edge) over ~85m, giving ~13% slope.
    # Start point on HarmonyBlvd centerline at y=170.
    ("NXHQLink", [
        (  44, 170, +3.0),   # on HarmonyBlvd centerline
        (  35, 195, +5.5),
        (  22, 220, +8.5),
        (  12, 240, +11.0),
        (   0, 255, +14.0),  # at NexCorpHQPad south edge
    ], 5.0, 14.0),

    # ── NEIGHBORHOOD STREETS — residential collectors sitting on
    # the settlement platforms. Narrow corridor + narrow shoulder
    # so they don't fight with the parent settlement flattening,
    # just smooth out the local 1-2 m fbm bumps still showing
    # through the settlement's flatness blend.
    # NorthRanch · 3 parallel east-west streets + the spur
    ("NRAspen",  [(-440, 200, +12.0), (-320, 200, +12.0),
                  (-240, 200, +12.0)], 4.0, 10.0),
    # NRBirch ramps DOWN as it enters OliverTreeMemPark (-300..-220
     #x, target +2) so the road follows the park grade instead of
     #carving a +12 plateau through the park's middle.
    ("NRBirch",  [(-440, 100, +12.0), (-320, 100, +12.0),
                  (-305, 100, +10.0),
                  (-285, 100,  +3.0),
                  (-240, 100,  +2.0)], 4.0, 10.0),
    ("NRCedar",  [(-440,  40, +12.0), (-320,  40, +12.0),
                  (-240,  40, +12.0)], 4.0, 10.0),
    ("NRSpur",   [(-320, 200, +12.0), (-320, 100, +12.0),
                  (-320,  40, +12.0)], 4.0, 10.0),

    # WestEstates · Magnolia Lane (gentle north-south curve) +
    # loop branch. Aligned with what build_west_estates_
    # neighborhood actually emits.
    ("WEMag",    [(-440, -180, -3.0), (-380, -185, -3.0),
                  (-320, -190, -3.0), (-260, -185, -3.0),
                  (-200, -180, -3.0), (-140, -175, -3.0)],
                  4.0, 10.0),
    ("WELoop",   [(-320, -190, -3.0), (-300, -150, -3.0),
                  (-340, -130, -3.0), (-380, -150, -3.0),
                  (-360, -190, -3.0), (-320, -190, -3.0)],
                  4.0, 10.0),

    # Phase 2 · winding cul-de-sac arterial (aligned with the
    # polyline that build_phase2_neighborhood actually emits).
    ("P2Main",   [(240, -150, +1.0), (210, -160, +1.0),
                  (180, -150, +1.0), (150, -160, +1.0),
                  (120, -180, +1.0), ( 90, -200, +1.0),
                  ( 70, -210, +1.0)], 4.0, 10.0),

    # East CDS · Ridge Crest Dr (gentle S-curve) + cul-de-sac spur
    # north. Aligned to the polyline that build_east_cds_
    # neighborhood actually emits.
    ("ECDSRidge",[(200, 140, +8.0), (240, 130, +8.0),
                  (300, 130, +8.0), (360, 140, +8.0),
                  (420, 150, +8.0)], 4.0, 10.0),
    ("ECDSCul",  [(300, 130, +8.0), (300, 180, +8.0),
                  (320, 220, +8.0)], 4.0, 10.0),

    # Phase 3 abandoned partial road (one-block paved). Aligned
    # with build_phase3_neighborhood's actual polyline so the
    # carve sits exactly under the gravel.
    ("Ph3Access",[(-440, -220, -8.0), (-380, -220, -8.0),
                  (-360, -230, -8.0)], 4.0, 12.0),

    # ── CHAPTER-1 COMMERCIAL FRONTAGE · the E-W road that runs in
    # front of NexCorp Gas & Go, Kwik Stop, Diner, Cosmic Comics.
    # SouthComm platform (-9.0). Wider corridor (8m road + 1m
    # buffer = 5m half-width) to match the existing emit in
    # build_commercial_cluster.
    ("Ch1Frontage", [
        (-120, -392, -9.0),
        ( -80, -392, -9.0),
        ( -40, -392, -9.0),
        (   0, -392, -9.0),
        (  40, -392, -9.0),
        (  80, -392, -9.0),
        ( 110, -392, -9.0),
    ], 6.0, 16.0),
]


def _seg_proj(px, py, x0, y0, x1, y1):
    """Project (px, py) onto segment (x0,y0)→(x1,y1). Returns (t, d)
    where t in [0,1] is the clamped projection parameter and d is
    perpendicular distance."""
    dx = x1 - x0; dy = y1 - y0
    l2 = dx * dx + dy * dy
    if l2 < 1e-6:
        return 0.0, math.hypot(px - x0, py - y0)
    t = ((px - x0) * dx + (py - y0) * dy) / l2
    t_c = max(0.0, min(1.0, t))
    qx = x0 + dx * t_c
    qy = y0 + dy * t_c
    return t_c, math.hypot(px - qx, py - qy)


def road_carve(x, y):
    """Returns (target_z, weight) for the nearest road corridor.
    Inside the full-grade band: weight = 1.0 (terrain locked to road
    grade). Through the shoulder: smoothstep falloff. Beyond shoulder:
    weight = 0.0. target_z is linearly interpolated along the polyline
    between the two waypoints bracketing the closest projection.

    When multiple corridors overlap (e.g. at an intersection), the
    one with the strongest weight wins; if equal, the one whose
    target_z is closer to the current terrain wins (prevents step
    jumps at junctions because both arterials carry the same target
    at the junction waypoint).
    """
    best_weight = 0.0
    best_target = 0.0
    for (_name, waypoints, full_hw, shoulder) in ROAD_CORRIDORS:
        seg_best_d = float("inf")
        seg_best_target = 0.0
        for i in range(len(waypoints) - 1):
            x0, y0, z0 = waypoints[i]
            x1, y1, z1 = waypoints[i + 1]
            t, d = _seg_proj(x, y, x0, y0, x1, y1)
            if d < seg_best_d:
                seg_best_d = d
                seg_best_target = z0 + (z1 - z0) * t
        if seg_best_d <= full_hw:
            w = 1.0
        elif seg_best_d <= full_hw + shoulder:
            tt = (seg_best_d - full_hw) / shoulder
            # Linear falloff reads as a constant-slope BATTER (cut/
            # fill slope) — civil engineering's standard 3:1 to 4:1
            # slope. Smoothstep was producing visible "terraced"
            # stepping where its mid-band 1.5× peak gradient hit the
            # 15 m grid cells. Linear keeps every shoulder cell at
            # the same slope.
            w = 1.0 - tt
        else:
            w = 0.0
        if w > best_weight:
            best_weight = w
            best_target = seg_best_target
    return best_target, best_weight


# ────────────────────────────────────────────────────────────────
# LOT PADS — flat platforms for parking lots and building pads not
# already covered by a SETTLEMENT rectangle. Each pad pulls the
# terrain to its target_z within the rect, with a smooth shoulder
# falloff so the lot edge grades back to natural terrain.
# Format: (name, x_min, x_max, y_min, y_max, target_z, shoulder_w)
# ────────────────────────────────────────────────────────────────
LOT_PADS = [
    # NexCorp HQ visitor lot south of the HQ building (NexCorpHQPad
    # only covers the building footprint; the southern visitor lot
    # extends to y=235 and was floating above terrain).
    ("NexCorpHQLot",  -40,  40, 220, 256, +14.0, 22.0),

    # Hospital — building + visitor lot
    ("HospitalLot",  160, 200, 255, 305, +14.0, 22.0),

    # Church + cemetery + lot
    ("ChurchPad",    -60,  20, 115, 168,  +1.0, 20.0),

    # Fire station + apron. Building moved south to y=-42 to
    # clear HorizonDr at y=-18.8; pad follows.
    ("FirePad",     -222, -178, -60, -24,  0.0, 18.0),

    # Police station + cruiser lot
    ("PolicePad",   -192, -148, -78, -42,  0.0, 18.0),

    # Post office + drop-box plaza
    ("PostPad",      164, 196,  -42, -18, +1.5, 16.0),

    # Library + bike racks. Library moved (60,80) -> (40,80)
    # 2026-06-15 to clear HarmonyBlvd at x=60; pad follows.
    ("LibraryPad",    20,  60,  62, 102,  +1.0, 16.0),

    # Drive-in theatre — concession + parking arcs + screen.
    # Tightened to (100, 230, -348, -235) with 15m shoulder so the
    # pad doesn't pull Cosmic Comics (at x=70, y=-360) UP toward
    # its -5 target. Old extent reached cosmic with weight 0.8,
    # carving the south wall of the comics shop to -5 instead of
    # SouthComm's -9.
    ("DriveInPad",    100, 230, -348, -235, -5.0, 15.0),

    # Halsey Studios — building 36m + 50m lot. Widened both axes.
    ("HalseyPad",    448, 512, -125, -75, +5.0, 22.0),

    # Auto dealership — 60×28 lot at (480, -260). Widened x.
    ("AutoPad",      440, 520, -290, -230, +5.0, 22.0),

    # Self-storage — 3 rows of orange roll-ups, 50×30 area.
    ("StoragePad",   448, 512, -210, -150, +5.0, 18.0),

    # East big-box — dept store + drive-thru, big lot.
    ("BigBoxPad",    442, 520,   35,  95, +5.0, 22.0),

    # Truck stop — wider east-extent so the rig stalls fit
    ("TruckStopPad", 162, 250, -400, -355, -9.0, 18.0),

    # Mini-mart at (-260, -50) — building + single-pump apron
    ("MiniMartPad", -278, -242, -68, -32, -1.0, 16.0),

    # Horizon Plaza — strip mall + lot (lot south)
    ("HorizonPzPad", -118, -82,  15,  45, +1.0, 16.0),

    # Elementary School — building + adjacent playground + lot
    ("ESPad",       -118, -62, 135, 185, +1.5, 20.0),

    # Little League diamond + dugouts
    ("LLDiamondPad", -178, -122, 175, 225, +1.0, 16.0),

    # Country Club main building pad — the clubhouse + portico
    ("CCMainPad",    -28,  28, 358, 388, +22.0, 18.0),

    # Country Club tennis + putting green + valet lot
    ("CCAuxPad",     -90,  90, 340, 392, +22.0, 22.0),

    # NexCorp Sales Trailer + 3-car visitor lot
    ("SalesPad",    -312, -288, 200, 232, +12.0, 14.0),

    # NexCorp Model Home + driveway pull-up
    ("ModelHomePad",-352, -328, 205, 232, +12.0, 14.0),

    # Taqueria El Rancho — building + drive-thru loop + parking
    ("TaqueriaPad",  275, 308, -385, -355, -9.0, 18.0),

    # D'Ambrosio's bar + patio
    ("DambrosioPad",-165, -135, -375, -345, -9.0, 16.0),

    # NexCorp HQ reflecting pool + plaza north of building
    ("NXHQPlaza",    -30,  30, 295, 335, +14.0, 18.0),
]


def lot_pad_carve(x, y):
    """Returns (target_z, weight) for the nearest LOT_PADS rect.
    Same semantics as road_carve: full inside, smooth shoulder out."""
    best_weight = 0.0
    best_target = 0.0
    for (_n, x_min, x_max, y_min, y_max, target_z, shoulder) in LOT_PADS:
        if x_min <= x <= x_max and y_min <= y <= y_max:
            w = 1.0
        else:
            dx = max(x_min - x, 0.0, x - x_max)
            dy = max(y_min - y, 0.0, y - y_max)
            d = math.hypot(dx, dy)
            if d >= shoulder:
                continue
            t = d / shoulder
            # Linear falloff (see road_carve comment).
            w = 1.0 - t
        if w > best_weight:
            best_weight = w
            best_target = target_z
    return best_target, best_weight


# ────────────────────────────────────────────────────────────────
# PONDS, POOLS, MINI-VALLEYS — features in the WILD zones between
# settlements. Add character to the in-between spaces.
# ────────────────────────────────────────────────────────────────
# Format: (name, cx, cy, radius, depth)  depth is positive metres
PONDS = [
    # Wider + deeper than the v1 ponds. Format: (name, cx, cy, radius, depth)
    # WATER_SURFACE_Z is how far below GROUND_Z the water plane sits;
    # depth is the terrain depression amount.
    # FoundersPond moved 2026-06-15 from (-380, 30) to (-380, -10).
    # Old position was INSIDE NorthRanch (-460..-200, 20..260) and
    # was punching a -4.5m crater across Cedar Street (y=40). New
    # position sits in the wild zone south of NR + west of
    # HarmonyPark / OliverTree Park, where it actually belongs.
    ("FoundersPond",   -380,   -10,  32,  8.0),
    ("HarmonyPond",      30,    60,  32,  6.0),    # community pool placement
    ("WildLotPond",    -340,  -240,  38,  8.0),    # gone-to-seed wild pond
    # SECreekPond moved from (360, -120) to (360, -210). Old
    # position was INSIDE HighSchoolField (-130..110), carving a
    # bowl under the football field.
    ("SECreekPond",     360,  -210,  40,  9.0),
    # NWHeadwatersPond moved (-440, 280) -> (-540, 340). Old was
    # INSIDE NorthComm (260..340 +14), carving a 13m crater. New
    # sits in the NW district corner wild zone near the creek
    # headwaters where the name 'headwaters' actually makes sense.
    ("NWHeadwatersPond",-540,   340,  30,  6.0),
    # EastWoodsPond moved (320, 310) -> (510, 310). Old was INSIDE
    # NorthComm. New sits in the wild zone NE of EastComm.
    ("EastWoodsPond",   510,   310,  28,  5.0),
    ("MidValleyPond",     0,  -180,  35,  7.0),
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


# ────────────────────────────────────────────────────────────────
# WATER CARVES — ponds + creek channel get an explicit floor_z and
# a true carve operation that beats settlement flattening. Per user
# (2026-06-15): "rivers and water also carves through terrain."
# Without this, settlements near the creek (OliverTreeMemPark,
# HarmonyPark, Phase2) flatten the creek dip back up, leaving the
# water plane floating above ground.
#
# Pond format: (name, cx, cy, full_r, shoulder_r, floor_z)
#   - Inside full_r: terrain locked to floor_z (the channel bed)
#   - From full_r to full_r+shoulder_r: smooth ramp back to natural
#   - Water plane sits at floor_z + 0.6 (computed in build_pond_water)
# ────────────────────────────────────────────────────────────────
POND_CARVES = [
    # (name, cx, cy, full_r, shoulder_r, floor_z)
    # floor_z values: targeted from local terrain at pond center
    # minus a reasonable depth. The water surface in build_pond_water
    # is computed as max(rim_z - 0.7, floor_z + 0.6), so leaving the
    # rim a bit higher than floor_z+0.6 keeps the water disc inside
    # the rim.
    ("FoundersPond",     -380,  -10, 24.0, 18.0, -3.0),
    ("HarmonyPond",        30,   60, 22.0, 16.0,  0.2),  # community pool
    ("WildLotPond",      -340, -240, 28.0, 20.0, -7.5),
    ("SECreekPond",       360, -210, 30.0, 22.0, -7.0),
    ("NWHeadwatersPond", -540,  340, 22.0, 16.0, +3.0),
    ("EastWoodsPond",     510,  310, 20.0, 16.0, +2.0),
    ("MidValleyPond",       0, -180, 26.0, 20.0, -4.5),
]

# Creek channel — polyline of (x, y, channel_floor_z) waypoints.
# floor_z decreases monotonically toward the outlet (creek flows
# south-east toward the river). Channel is narrow (3 m full-grade
# half-width) with a wide flood-plain shoulder (25 m) so the
# surrounding terrain grades down into the ravine without a
# vertical step at the channel edge.
CREEK_CHANNEL = [
    # Re-routed 2026-06-15. Old route sliced diagonally through
    # NorthRanch, punching a -1m water trench through Aspen Street.
    # New route: through NorthComm at modest depth (only 3-4m below
    # commercial-belt grade so it reads as a small creek, not a
    # ravine), curves east to wild gap (between NR and HP), then
    # flows SE through wild zones.
    # Each floor_z is no more than ~4m below the local natural
    # platform so the channel stays a small creek, not a canyon.
    (-560,  360,  +2.5),   # NW district corner (wild)
    (-500,  340,  +8.0),   # entering NorthComm (target +14)
    (-440,  310, +12.0),   # NorthComm interior (only 2m cut)
    (-340,  300, +12.0),   # NorthComm interior
    (-260,  280, +10.5),   # at NR/NorthComm boundary
    (-180,  240,  +1.0),   # wild gap east of NR — drops to natural
    (-160,  200,  -1.0),   # wild gap (between OT Park edge & HP)
    (-160,  140,  -1.5),
    (-120,   80,  -1.5),   # HarmonyPark west edge approach
    ( -80,    0,  -3.0),   # wild zone south of HarmonyPark
    (  40,  -70,  -4.5),
    ( 160, -140,  -5.5),
    ( 280, -190,  -6.5),
    ( 400, -240,  -7.5),
    ( 500, -310,  -8.5),
    ( 580, -360,  -9.5),   # SE outlet
]
CREEK_CHANNEL_HW = 3.0       # half-width of the channel bed
CREEK_SHOULDER = 22.0        # flood-plain falloff


def _pond_carve(x, y):
    """Best-weight pond-floor lock. Inside full_r: weight = 1
    (terrain forced to floor_z). Through shoulder: smooth falloff."""
    best_w = 0.0; best_z = 0.0
    for (_n, cx, cy, full_r, sh, floor_z) in POND_CARVES:
        d = math.hypot(x - cx, y - cy)
        if d <= full_r:
            w = 1.0
        elif d <= full_r + sh:
            t = (d - full_r) / sh
            w = 1.0 - smoothstep(0.0, 1.0, t)
        else:
            continue
        if w > best_w:
            best_w = w; best_z = floor_z
    return best_z, best_w


def _creek_carve(x, y):
    """Channel floor lock along the creek polyline. floor_z lerps
    along segments between waypoints (so the creek slopes naturally
    toward the outlet). Inside CREEK_CHANNEL_HW: weight = 1; through
    CREEK_SHOULDER: smooth ramp."""
    best_d = float("inf"); best_z = 0.0
    for i in range(len(CREEK_CHANNEL) - 1):
        x0, y0, z0 = CREEK_CHANNEL[i]
        x1, y1, z1 = CREEK_CHANNEL[i + 1]
        t, d = _seg_proj(x, y, x0, y0, x1, y1)
        if d < best_d:
            best_d = d
            best_z = z0 + (z1 - z0) * t
    if best_d <= CREEK_CHANNEL_HW:
        w = 1.0
    elif best_d <= CREEK_CHANNEL_HW + CREEK_SHOULDER:
        tt = (best_d - CREEK_CHANNEL_HW) / CREEK_SHOULDER
        # Linear ramp inside the shoulder reads as a real BATTER
        # (cut slope) — smoothstep was producing the visible
        # "terrace" stepping in the 15 m mesh cells.
        w = 1.0 - tt
    else:
        w = 0.0
    return best_z, w


def water_carve(x, y):
    """Combine pond + creek carves; return the strongest."""
    pz, pw = _pond_carve(x, y)
    cz, cw = _creek_carve(x, y)
    if pw >= cw:
        return pz, pw
    return cz, cw


_HCE_ELEV_CACHE = {}

def _cached_hce_elevation(x, y):
    """hce_elevation with a dict cache keyed by exact (x, y) so
    repeated calls at the same point return instantly. mesh_z calls
    hce_elevation at 4 cell corners; building emit functions call
    mesh_z dozens of times per object; many of those calls hit the
    same corner. With the new 25-corridor carve pipeline each
    hce_elevation costs ~300 ops, so caching saves significant
    build time. Cleared at the start of build_ground so reproducible."""
    key = (x, y)
    z = _HCE_ELEV_CACHE.get(key)
    if z is None:
        z = hce_elevation(x, y)
        _HCE_ELEV_CACHE[key] = z
    return z


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
    z00 = _cached_hce_elevation(x0, y0)   # bottom-left = a
    z10 = _cached_hce_elevation(x1, y0)   # bottom-right = b
    z11 = _cached_hce_elevation(x1, y1)   # top-right = c
    z01 = _cached_hce_elevation(x0, y1)   # top-left = d
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
    # Base creek dip reduced -7 -> -3 (2026-06-15). The actual
    # creek floor is set by CREEK_CHANNEL carve later; this base
    # dip only needs to bias the area gently so the carve has a
    # natural-looking flood plain. Old -7m was over-deep and
    # leaked through low-flatness settlements (HarmonyPark at
    # 0.55) producing visible creek-bed depressions inside parks.
    creek_dip = -3.0 * math.exp(-creek_d * creek_d / (CREEK_FLOOD_WIDTH ** 2))
    base = (tilt + cc_rise + east_rise + nw_rise + south_dip
            + noise_low + noise_high + creek_dip)

    # ── Pond depressions (carve into wild zones) ─────────────────
    for (_name, cx, cy, r, d) in PONDS:
        base += pond_depression(x, y, cx, cy, r, d)

    # ── Settlement flattening ────────────────────────────────────
    # Per-settlement (blend × flatness) contributions combine via
    # SOFTMAX over targets. With T=0.10 the result behaves like
    # max-weight inside each settlement (so nested ones like OT
    # Park inside NR still read their own target +2) but smooth-
    # transitions at boundaries (so HSField +3 -> EastCDS +8
    # doesn't cliff in one cell).
    softmax_T = 0.10
    blends = []
    for (_n, x_min, x_max, y_min, y_max, target_z, flatness) in SETTLEMENTS:
        b = settlement_blend(x, y, x_min, x_max, y_min, y_max) * flatness
        if b > 0.001:
            blends.append((b, target_z))

    if blends:
        # Softmax over the weights / T, BUT only include settlements
        # whose blend is within 1% of the leader. That way a doubly-
        # nested settlement (e.g. OTSkatePark at b=0.97 inside
        # OliverTreeMemPark at b=0.95 inside NorthRanch at b=0.80)
        # cleanly dominates inside its own rect — the outer parents
        # don't pull the skatepark interior up toward their targets.
        # The 1% threshold still admits competitors at proper
        # SETTLEMENT BOUNDARIES (where two settlements have nearly-
        # equal blend from opposite sides of the boundary), giving
        # the smooth 5-25m transition softmax was added for.
        max_b = max(b for b, _ in blends)
        contenders = [(b, tz) for b, tz in blends if b >= max_b * 0.99]
        exps = [(math.exp((b - max_b) / softmax_T), tz) for b, tz in contenders]
        sum_e = sum(e for e, _ in exps)
        avg_target = sum(e * tz for e, tz in exps) / sum_e
        flattened = base * (1 - max_b) + avg_target * max_b
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

    # ── LOT PADS — flatten parking lots / institutional pads not
    # covered by SETTLEMENTS. Applied AFTER berms so a pad cuts
    # through any incidental berm bump.
    lot_target, lot_w = lot_pad_carve(x, y)
    if lot_w > 0.001:
        flattened = flattened * (1.0 - lot_w) + lot_target * lot_w

    # ── WATER CARVE — ponds + creek channel lock terrain to their
    # respective floor heights, with smooth flood-plain shoulders.
    # Beats settlement flattening so pond rims + creek banks stay
    # below water level even where a settlement overlaps the water.
    water_target, water_w = water_carve(x, y)
    if water_w > 0.001:
        flattened = flattened * (1.0 - water_w) + water_target * water_w

    # ── ROAD CORRIDOR carve. Civil-engineering road cut: humans
    # excavate dirt to set a controlled gradient. Inside the
    # full-grade band terrain is locked to road-grade; through the
    # shoulder it grades smoothly back to surrounding height.
    #
    # YIELD TO WATER: where water_w is at or near full, the road
    # carve yields. The road would otherwise FILL IN the creek
    # channel at every crossing. Where carve yields, we emit
    # explicit BRIDGE DECK geometry instead (see build_bridges).
    road_target, road_w = road_carve(x, y)
    if road_w > 0.001:
        # Scale road weight down by (1 - water_w) so water survives
        # the crossing. Where water_w = 1.0, road weight drops to 0
        # and the channel stays carved. Where water_w = 0, road
        # behaves normally.
        effective_road_w = road_w * (1.0 - water_w)
        if effective_road_w > 0.001:
            flattened = flattened * (1.0 - effective_road_w) + road_target * effective_road_w

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
    # EastCDS_South berm moved y=25 -> y=115 (2026-06-15) so it
    # sits just south of the new EastCDS rect (which was shrunk
    # to y=120..260). Old position was 95m south of the settlement
    # — geometrically meaningless after the rect change.
    ("EastCDS_South",    [(180, 115), (440, 115)],            10.0, 1.5),
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
    _HCE_ELEV_CACHE.clear()
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
    """Water surface quads following the carved creek channel. Each
    segment of CREEK_CHANNEL declares an explicit floor_z; water
    sits 0.6 m above the bed and slopes down toward the outlet
    along with the channel.

    Per the 2026-06-15 water-carve pass: the channel itself is now
    a true carve in hce_elevation (see CREEK_CHANNEL + _creek_carve),
    so mesh_z within the channel returns floor_z. The water disc
    no longer needs to probe mesh_z — it can use floor_z directly,
    giving a stable surface that doesn't tilt with mesh aliasing."""
    width = 3.6
    for i in range(len(CREEK_CHANNEL) - 1):
        x0, y0, z0 = CREEK_CHANNEL[i]
        x1, y1, z1 = CREEK_CHANNEL[i + 1]
        dx = x1 - x0; dy = y1 - y0
        ang = math.atan2(dy, dx)
        perp_x = -math.sin(ang); perp_y = math.cos(ang)
        # Per-corner water z so the surface slopes with the channel
        # gradient instead of stepping at every segment boundary.
        # 0.6 m above the floor (typical small-creek depth).
        wz0 = z0 + 0.6
        wz1 = z1 + 0.6
        verts = [
            (x0 - perp_x * width / 2, y0 - perp_y * width / 2, wz0),
            (x1 - perp_x * width / 2, y1 - perp_y * width / 2, wz1),
            (x1 + perp_x * width / 2, y1 + perp_y * width / 2, wz1),
            (x0 + perp_x * width / 2, y0 + perp_y * width / 2, wz0),
        ]
        _finalize_mesh(f"Creek_Water_{i}", verts, [[0, 1, 2, 3]],
                       COL_CREEK_WATER)


def _seg_intersect(ax, ay, bx, by, cx, cy, dx, dy):
    """Return the (x, y, ts, td) intersection of segments AB and CD,
    or None if they don't cross. ts/td are the parameters along the
    two segments at the crossing point."""
    rx = bx - ax; ry = by - ay
    sx = dx - cx; sy = dy - cy
    denom = rx * sy - ry * sx
    if abs(denom) < 1e-6:
        return None
    ts = ((cx - ax) * sy - (cy - ay) * sx) / denom
    td = ((cx - ax) * ry - (cy - ay) * rx) / denom
    if 0.0 <= ts <= 1.0 and 0.0 <= td <= 1.0:
        return (ax + rx * ts, ay + ry * ts, ts, td)
    return None


def _emit_raised_sidewalk(pts, prefix, sw_w=2.5, sw_h=0.15,
                           color=(0.82, 0.80, 0.76, 1.0),
                           curb_color=(0.55, 0.52, 0.48, 1.0)):
    """Raised concrete sidewalk along polyline `pts`. Per user
    2026-06-15: "raised cement" — emit a 3D box with visible top
    (cement top) + 4 side faces (curb edge), not just a flat quad.

    For each segment between consecutive waypoints:
      · Box w/ top face at mesh_z + sw_h (sampled per-corner), and
        bottom face at mesh_z (the slab embeds into the ground).
      · Slab follows perpendicular to the segment direction, half-
        width sw_w/2 on each side of the centerline.

    Returns nothing; emits two meshes per segment (a top quad +
    side panels). The visible top is cement-colored; the curb
    sides are slightly darker so the slab reads as RAISED.
    """
    hw = sw_w / 2
    for i in range(len(pts) - 1):
        x0, y0 = pts[i]; x1, y1 = pts[i + 1]
        dxs = x1 - x0; dys = y1 - y0
        seg_len = math.hypot(dxs, dys) or 1.0
        perp_x = -dys / seg_len
        perp_y =  dxs / seg_len
        # Four corner xys
        corners = [
            (x0 - perp_x * hw, y0 - perp_y * hw),     # bottom-left
            (x1 - perp_x * hw, y1 - perp_y * hw),     # bottom-right
            (x1 + perp_x * hw, y1 + perp_y * hw),     # top-right
            (x0 + perp_x * hw, y0 + perp_y * hw),     # top-left
        ]
        # Sample mesh_z at each corner for the bottom; top is +sw_h
        ground_zs = [mesh_z(cx, cy) for (cx, cy) in corners]
        top_zs = [gz + sw_h for gz in ground_zs]
        # Slab as a 3D box: 8 verts (4 bottom, 4 top), 6 faces
        verts = []
        for (cx, cy), gz in zip(corners, ground_zs):
            verts.append((cx, cy, gz + 0.01))    # bottom (just above ground)
        for (cx, cy), tz in zip(corners, top_zs):
            verts.append((cx, cy, tz))            # top
        faces = [
            [4, 5, 6, 7],          # top (cement)
            [0, 3, 2, 1],          # bottom (hidden, in ground)
            [0, 4, 5, 1],          # side (south face of perp segment)
            [1, 5, 6, 2],          # side
            [2, 6, 7, 3],          # side (north face)
            [3, 7, 4, 0],          # side
        ]
        # Single mesh with top-cement coloring; the sides inherit
        # the same vertex colors so they read as the slab's edge.
        _finalize_mesh(f"{prefix}_RaisedSW_{i}", verts, faces, color)


def build_chapter1_pedestrian_network():
    """RAISED CONCRETE SIDEWALK network connecting the chapter-1
    commercial cluster. Per user direction 2026-06-15: "sidewalks
    are still a missing part of infrastructure. start at the
    kwikstop complex and design navigatable paths for pedestrians,
    raised cement."

    Existing geometry (build_commercial_cluster) emits a thin
    storefront walk in front of NexCorpGG / Kwik Stop / Diner /
    Cosmic Comics at y = -366.5 (flat quad, no curb). This network
    adds:
      · West extension to D'Ambrosio's Holdover (-150, -360)
      · East extension to Taqueria El Rancho (290, -370)
      · Spur south to Truck Stop (200, -380)
      · Connection up to HarmonyBlvd's south sidewalk via the
        existing crosswalk at (12, -388 .. -396)
      · South side of frontage road (between road and the dirt
        beyond) for two-sided walking

    All sidewalks emit as 2.5 m wide × 0.15 m TALL raised
    concrete boxes so the slab visibly stands above the asphalt
    and grass.
    """
    # Anchor positions (ground z is read from mesh_z at runtime)
    # Storefront walk line is at y = -366.5 (existing)
    storefront_y = -366.5
    # South side of frontage road sits at y = -397 (road CL at
    # -392, road half-width 4, then ~1m grass buffer)
    south_walk_y = -397.0

    # ── A. NORTH SIDE storefront extension WEST to D'Ambrosio's
    # NexCorpGG at x=-60, west edge x=-75ish. D'Ambrosio at x=-150,
    # east face x=-143. Walk runs at y=-366.5 from -75 to -143.
    west_walk = [
        (-143.0, storefront_y),    # D'Ambrosio east face
        (-100.0, storefront_y),
        ( -75.0, storefront_y),    # NexCorpGG west edge
    ]
    _emit_raised_sidewalk(west_walk, "Ch1Walk_W")

    # ── B. NORTH SIDE storefront extension EAST to Taqueria
    # Cosmic Comics at x=70, east edge x=80. Taqueria at x=290,
    # west face x=283. Walk runs y=-366.5 from 80 to 283.
    east_walk = [
        (  80.0, storefront_y),    # Cosmic east edge
        ( 130.0, storefront_y),
        ( 180.0, storefront_y),
        ( 235.0, storefront_y),
        ( 283.0, storefront_y),    # Taqueria west face
    ]
    _emit_raised_sidewalk(east_walk, "Ch1Walk_E")

    # ── C. SPUR south from east walk down to Truck Stop
    # Truck Stop at (200, -380), north entry around y=-368.
    truckstop_spur = [
        ( 200.0, storefront_y),    # off the east walk
        ( 200.0, -373.0),          # truck stop north face
    ]
    _emit_raised_sidewalk(truckstop_spur, "Ch1Walk_TS")

    # ── D. SOUTH SIDE of the frontage road — runs full length so
    # pedestrians can walk on EITHER side
    south_walk = [
        (-150.0, south_walk_y),    # D'Ambrosio south
        ( -75.0, south_walk_y),    # opposite NexCorpGG
        (  -8.0, south_walk_y),    # opposite the HarmonyBlvd crosswalk
        (  35.0, south_walk_y),    # opposite Diner
        (  90.0, south_walk_y),    # opposite Cosmic
        ( 180.0, south_walk_y),
        ( 283.0, south_walk_y),    # opposite Taqueria
    ]
    _emit_raised_sidewalk(south_walk, "Ch1Walk_South")

    # ── E. NORTH-side connector from HarmonyBlvd south sidewalk
    # down to the chapter-1 storefront walk. HarmonyBlvd south
    # sidewalk ends at y=-340. Storefront walk at y=-366.5. Walk
    # bridges this 26m gap on the EAST side of HarmonyBlvd, just
    # east of the road edge.
    # HarmonyBlvd at y=-340 is at x≈0 (waypoint (0, -340, -9)).
    # Sidewalk offset on east side: x = 0 + 6.4 = 6.4.
    blvd_connector = [
        (   6.4, -340.0),          # at HarmonyBlvd south sidewalk
        (   8.0, -350.0),
        (   9.0, -360.0),
        (  12.0, storefront_y),    # joins storefront walk
    ]
    _emit_raised_sidewalk(blvd_connector, "Ch1Walk_BlvdN")

    # ── F. SOUTH-side connector: same idea on the south of road,
    # from HarmonyBlvd's south end down past the road to the
    # south-side frontage walk.
    blvd_connector_s = [
        (   6.4, -388.0),          # at HarmonyBlvd just north of frontage
        (   6.4, south_walk_y),    # at south side walk
    ]
    _emit_raised_sidewalk(blvd_connector_s, "Ch1Walk_BlvdS")

    # ── G. CROSSWALK ZEBRAS across the frontage road, connecting
    # the north and south walks at major crossing points.
    # Already covered by build_intersections at HarmonyBlvd ×
    # Ch1Frontage. Add a mid-block zebra opposite Kwik Stop for
    # easy walking between sides.
    COL_CROSS = (0.92, 0.90, 0.84, 1.0)
    cross_y_mid = (storefront_y + south_walk_y) / 2  # y = -381.75
    for x_center in (-100.0, -15.0, 35.0, 200.0, 260.0):
        cw_n = storefront_y - 2.5
        cw_s = south_walk_y + 2.5
        for k in range(5):
            sx = x_center - 1.2 + k * 0.6
            z_top = mesh_z(sx, (cw_n + cw_s) / 2) + 0.055
            verts = [
                (sx - 0.20, cw_n, z_top),
                (sx + 0.20, cw_n, z_top),
                (sx + 0.20, cw_s, z_top),
                (sx - 0.20, cw_s, z_top),
            ]
            _finalize_mesh(f"Ch1Walk_Zebra_{int(x_center)}_{k}",
                            verts, [[0, 1, 2, 3]], COL_CROSS)

    # ── H. SIDEWALK at chapter-1 to the spawn pad north.
    # Existing spur in build_commercial_cluster covers (0, -340)
    # down to the storefront walk. We can ADD a raised-cement
    # version that runs alongside, for visual consistency with
    # the rest of the chapter-1 network. Use slightly east x so
    # it doesn't z-fight with the existing spur.
    north_spur = [
        (  15.0, -340.0),          # at spawn approach
        (  15.0, -355.0),
        (  15.0, storefront_y),    # joins storefront walk
    ]
    _emit_raised_sidewalk(north_spur, "Ch1Walk_SpawnSpur")


def build_intersections():
    """At every road-road xy crossing, emit an asphalt slab covering
    the intersection footprint so the four-quadrant grass triangles
    between the two crossing road quads are filled. The slab z
    matches whichever corridor target_z is higher at the crossing
    (avoids sagging into the lower road's grade).

    Also emits crosswalks on the major arterial intersections."""
    COL_INTER = (0.18, 0.18, 0.20, 1.0)
    COL_STRIPE = (0.92, 0.90, 0.84, 1.0)

    seen = set()
    for a_idx, (rname_a, wps_a, hw_a, _sh_a) in enumerate(ROAD_CORRIDORS):
        for b_idx, (rname_b, wps_b, hw_b, _sh_b) in enumerate(ROAD_CORRIDORS):
            if b_idx <= a_idx:
                continue
            for i in range(len(wps_a) - 1):
                ax0, ay0, az0 = wps_a[i]
                ax1, ay1, az1 = wps_a[i + 1]
                for j in range(len(wps_b) - 1):
                    bx0, by0, bz0 = wps_b[j]
                    bx1, by1, bz1 = wps_b[j + 1]
                    hit = _seg_intersect(ax0, ay0, ax1, ay1,
                                          bx0, by0, bx1, by1)
                    if not hit:
                        continue
                    hx, hy, ts, td = hit
                    # De-dupe near-duplicates (same intersection at
                    # consecutive corridor entries)
                    key = (round(hx / 4) * 4, round(hy / 4) * 4)
                    if key in seen:
                        continue
                    seen.add(key)
                    # Slab z = the higher of the two corridor zs at
                    # the crossing (so the slab doesn't sag below
                    # either road).
                    za = az0 + (az1 - az0) * ts
                    zb = bz0 + (bz1 - bz0) * td
                    inter_z = max(za, zb)
                    # Slab span = max(hw_a, hw_b) + 0.5 on each side
                    half = max(hw_a, hw_b) + 0.5
                    verts = [
                        (hx - half, hy - half, inter_z + 0.04),
                        (hx + half, hy - half, inter_z + 0.04),
                        (hx + half, hy + half, inter_z + 0.04),
                        (hx - half, hy + half, inter_z + 0.04),
                    ]
                    _finalize_mesh(
                        f"Inter_{rname_a}_{rname_b}_{i}_{j}",
                        verts, [[0, 1, 2, 3]], COL_INTER)
                    # 4 crosswalk zebras on arterial intersections
                    is_arterial = (hw_a >= 7.0 and hw_b >= 7.0)
                    if is_arterial:
                        for side in (-1, +1):
                            for axis in ('x', 'y'):
                                cw_z = inter_z + 0.055
                                if axis == 'x':
                                    # Crosswalk across X (zebra
                                    # stripes running along Y axis)
                                    cwx = hx
                                    cwy = hy + side * (half - 0.7)
                                    for k in range(5):
                                        sx = cwx - half * 0.7 + k * (half * 1.4 / 4)
                                        _finalize_mesh(
                                            f"Inter_{rname_a}_{rname_b}_{i}_{j}_CW_{axis}_{side:+d}_{k}",
                                            [
                                                (sx - 0.3, cwy - 1.0, cw_z),
                                                (sx + 0.3, cwy - 1.0, cw_z),
                                                (sx + 0.3, cwy + 1.0, cw_z),
                                                (sx - 0.3, cwy + 1.0, cw_z),
                                            ],
                                            [[0, 1, 2, 3]], COL_STRIPE)
                                else:
                                    cwx = hx + side * (half - 0.7)
                                    cwy = hy
                                    for k in range(5):
                                        sy = cwy - half * 0.7 + k * (half * 1.4 / 4)
                                        _finalize_mesh(
                                            f"Inter_{rname_a}_{rname_b}_{i}_{j}_CW_{axis}_{side:+d}_{k}",
                                            [
                                                (cwx - 1.0, sy - 0.3, cw_z),
                                                (cwx - 1.0, sy + 0.3, cw_z),
                                                (cwx + 1.0, sy + 0.3, cw_z),
                                                (cwx + 1.0, sy - 0.3, cw_z),
                                            ],
                                            [[0, 1, 2, 3]], COL_STRIPE)


def build_bridges():
    """Where a road corridor crosses the creek channel, emit a
    bridge deck at road grade (not at the dipped creek floor) so
    the player can drive across. Without this the road quads sag
    into the creek bed because road_carve YIELDS to water_carve at
    the channel centerline.

    For each ROAD_CORRIDOR × CREEK_CHANNEL pair of segments, compute
    the analytic xy intersection point. At the crossing, emit:
      · a deck quad 14 m × 8 m at road target_z (road follows the
        corridor direction; deck spans the channel + flood plain)
      · two stone-coloured side parapets (low railings)
      · two stone piers down to the creek floor for read
    """
    COL_DECK = (0.32, 0.32, 0.35, 1.0)           # darker asphalt
    COL_PARAPET = (0.78, 0.74, 0.68, 1.0)        # cast-concrete
    COL_PIER = (0.62, 0.58, 0.52, 1.0)

    for (rname, waypoints, full_hw, _sh) in ROAD_CORRIDORS:
        for i in range(len(waypoints) - 1):
            rx0, ry0, rz0 = waypoints[i]
            rx1, ry1, rz1 = waypoints[i + 1]
            for j in range(len(CREEK_CHANNEL) - 1):
                cx0, cy0, cz0 = CREEK_CHANNEL[j]
                cx1, cy1, cz1 = CREEK_CHANNEL[j + 1]
                hit = _seg_intersect(rx0, ry0, rx1, ry1,
                                     cx0, cy0, cx1, cy1)
                if not hit:
                    continue
                hx, hy, ts, td = hit
                deck_z = rz0 + (rz1 - rz0) * ts
                creek_z = cz0 + (cz1 - cz0) * td
                # Road direction unit vector
                rdx = rx1 - rx0; rdy = ry1 - ry0
                rlen = math.hypot(rdx, rdy) or 1.0
                ux = rdx / rlen; uy = rdy / rlen
                # Road perpendicular (across-road direction)
                px = -uy; py = ux
                # Deck dimensions. The deck should be slightly wider
                # than the actual road quad (the road in
                # build_district_arterials uses road_w=8, so the road
                # quad is 8m wide). With curbs + parapets the deck
                # should span ~11m. Less than 2*full_hw because the
                # full_hw includes shoulder margin not occupied by
                # asphalt.
                deck_along = 18.0
                deck_across = min(2.0 * full_hw + 2.0, 12.0)
                # Deck quad — flat at deck_z
                half_a = deck_along / 2
                half_b = deck_across / 2
                corners = [
                    (hx - ux * half_a - px * half_b,
                     hy - uy * half_a - py * half_b),
                    (hx + ux * half_a - px * half_b,
                     hy + uy * half_a - py * half_b),
                    (hx + ux * half_a + px * half_b,
                     hy + uy * half_a + py * half_b),
                    (hx - ux * half_a + px * half_b,
                     hy - uy * half_a + py * half_b),
                ]
                deck_thick = 0.5
                # Bottom verts (deck underside) for thickness
                verts = []
                for (vx, vy) in corners:
                    verts.append((vx, vy, deck_z + 0.05))
                for (vx, vy) in corners:
                    verts.append((vx, vy, deck_z + 0.05 - deck_thick))
                # Top quad + bottom quad + 4 sides
                faces = [
                    [0, 1, 2, 3],            # top
                    [7, 6, 5, 4],            # bottom (reversed)
                    [0, 4, 5, 1],            # side
                    [1, 5, 6, 2],
                    [2, 6, 7, 3],
                    [3, 7, 4, 0],
                ]
                _finalize_mesh(f"Bridge_{rname}_{i}_{j}_Deck",
                               verts, faces, COL_DECK)
                # Two side parapets (low concrete walls along the
                # bridge edges)
                rail_h = 0.7
                rail_t = 0.20
                for sgn in (-1, +1):
                    cxR = hx + sgn * px * (half_b + rail_t / 2 - 0.05)
                    cyR = hy + sgn * py * (half_b + rail_t / 2 - 0.05)
                    # Build box via 8 corners aligned with road axis
                    rverts = []
                    for ka in (-half_a, half_a):
                        for kb in (-rail_t / 2, rail_t / 2):
                            rverts.append((
                                cxR + ux * ka + px * kb,
                                cyR + uy * ka + py * kb,
                                deck_z + 0.10,
                            ))
                    for ka in (-half_a, half_a):
                        for kb in (-rail_t / 2, rail_t / 2):
                            rverts.append((
                                cxR + ux * ka + px * kb,
                                cyR + uy * ka + py * kb,
                                deck_z + 0.10 + rail_h,
                            ))
                    rfaces = [
                        [0, 1, 3, 2],         # bottom
                        [6, 7, 5, 4],         # top
                        [0, 4, 5, 1],
                        [1, 5, 7, 3],
                        [3, 7, 6, 2],
                        [2, 6, 4, 0],
                    ]
                    _finalize_mesh(
                        f"Bridge_{rname}_{i}_{j}_Parapet_{sgn:+d}",
                        rverts, rfaces, COL_PARAPET)
                # Two stone piers descending from deck to creek floor
                pier_z_top = deck_z - deck_thick + 0.10
                pier_z_bot = creek_z - 0.20
                pier_h = pier_z_top - pier_z_bot
                if pier_h > 0.5:
                    for sgn in (-1, +1):
                        # Place piers across the road axis at ±2 m
                        pcx = hx + sgn * ux * 4.0
                        pcy = hy + sgn * uy * 4.0
                        pverts = []
                        for ka in (-1.0, 1.0):
                            for kb in (-0.8, 0.8):
                                pverts.append((
                                    pcx + ux * ka + px * kb,
                                    pcy + uy * ka + py * kb,
                                    pier_z_bot,
                                ))
                        for ka in (-1.0, 1.0):
                            for kb in (-0.8, 0.8):
                                pverts.append((
                                    pcx + ux * ka + px * kb,
                                    pcy + uy * ka + py * kb,
                                    pier_z_top,
                                ))
                        pfaces = [
                            [0, 1, 3, 2],
                            [6, 7, 5, 4],
                            [0, 4, 5, 1],
                            [1, 5, 7, 3],
                            [3, 7, 6, 2],
                            [2, 6, 4, 0],
                        ]
                        _finalize_mesh(
                            f"Bridge_{rname}_{i}_{j}_Pier_{sgn:+d}",
                            pverts, pfaces, COL_PIER)


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
    # Build a lookup of pond floor + carve radius from POND_CARVES.
    floor_by_name = {n: (full_r, floor_z)
                     for (n, _cx, _cy, full_r, _sh, floor_z) in POND_CARVES}
    for (name, cx, cy, radius, _depth) in PONDS:
        # Per the 2026-06-15 water-carve pass: each pond now declares
        # an explicit floor_z in POND_CARVES. Use that directly for
        # water_z so the surface always sits 0.6 m above the bowl bed
        # regardless of how settlements/lots/roads carved nearby.
        # Sample rim well beyond the carve shoulder so it reads
        # natural terrain, not the carved bowl wall.
        if name in floor_by_name:
            full_r, floor_z = floor_by_name[name]
            water_z = floor_z + 0.6
            bottom_z = floor_z
        else:
            bottom_z = mesh_z(cx, cy)
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
    """KWIK SHOP — 3-bay strip building. Per user direction
    (2026-06-15): the Kwik Stop is the HERO bay; the arcade +
    laundromat are smaller adjacent bays that connect to each
    other. Bay widths reflect that — Kwik Stop 16m, arcade 6m,
    laundromat 6m. Total 28m across.

    Layout west → east:
        [ ARCADE 6m | LAUNDROMAT 6m ][ KWIK STOP 16m ]

    The arcade-laundromat side is the "annex" zone that the
    Kwik Stop's main entry sits across from.
    """
    name_prefix = "KwikShop"
    # Per-bay widths (sum to total_w)
    BAY_W_ARCADE     = 6.0
    BAY_W_LAUNDROMAT = 6.0
    BAY_W_KWIKSTOP   = 16.0
    total_w = BAY_W_ARCADE + BAY_W_LAUNDROMAT + BAY_W_KWIKSTOP
    depth = 10.0
    height = 3.6

    # Bay center xs (relative to strip center cx):
    #   strip west edge at cx - total_w/2 = cx - 14
    #   arcade center:     -14 + 3   = -11  -> cx - 11
    #   laundromat center: -11 + 3 + 3 = -5 -> cx - 5
    #   kwikstop center:   -2  + 8   = +6   -> cx + 6
    ARCADE_OX     = -total_w / 2 + BAY_W_ARCADE / 2                          # -11
    LAUNDROMAT_OX =  ARCADE_OX + BAY_W_ARCADE / 2 + BAY_W_LAUNDROMAT / 2     # -5
    KWIKSTOP_OX   =  LAUNDROMAT_OX + BAY_W_LAUNDROMAT / 2 + BAY_W_KWIKSTOP / 2  # +6
    # Inter-bay partition x positions
    PART_ARC_LAUN = ARCADE_OX + BAY_W_ARCADE / 2                              # -8
    PART_LAUN_KWIK = LAUNDROMAT_OX + BAY_W_LAUNDROMAT / 2                     # -2

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
    # Two interior partition walls between the three bays. The
    # arcade↔laundromat partition runs only 60% of the depth so
    # the two bays read as CONNECTED (per user direction
    # 2026-06-15) — customers can walk between the arcade floor
    # and the laundry floor without leaving the building.
    # The laundromat↔kwikstop partition is FULL height (the kwik
    # stop is a separate retail space).
    _make_box_local(f"{name_prefix}_PartWall_Arc_Laun",
                    (cx + PART_ARC_LAUN,
                     cy + depth * 0.20,            # back 60%
                     ground_z + height / 2),
                    (wall_t, depth * 0.60, height), col_wall)
    _make_box_local(f"{name_prefix}_PartWall_Laun_Kwik",
                    (cx + PART_LAUN_KWIK, cy,
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
    # HVAC units — one per bay (now at proper per-bay positions)
    for k_off, ox in enumerate((ARCADE_OX, LAUNDROMAT_OX, KWIKSTOP_OX)):
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
    # Each tuple now carries its OWN bay_w so per-bay storefront
    # geometry (glass, mullions, door, sign) scales with the
    # actual bay size rather than the old constant.
    bay_specs = [
        ("Arcade",     ARCADE_OX,     BAY_W_ARCADE,     col_arcade_sign,
            "ARCADE",       (0.95, 0.85, 0.30, 1.0)),
        ("Laundromat", LAUNDROMAT_OX, BAY_W_LAUNDROMAT, col_laundromat_sign,
            "LAUNDROMAT",   (0.98, 0.98, 0.96, 1.0)),
        ("KwikStop",   KWIKSTOP_OX,   BAY_W_KWIKSTOP,   col_kwikstop_sign,
            "KWIK STOP",    (0.98, 0.95, 0.86, 1.0)),
    ]
    glass_y = cy - depth / 2 + 0.05
    for bay_tag, bay_ox, bay_w_local, col_sign, sign_text, _txt_col in bay_specs:
        bcx = cx + bay_ox
        # Plate-glass storefront (mullions + rails) per bay.
        # More mullions for wider bays (1 per ~2.5m) so glass
        # reads dense.
        n_mullions = max(3, int(bay_w_local / 2.5))
        for k in range(n_mullions):
            mx = bcx - bay_w_local / 2 + 0.3 + \
                 k * (bay_w_local - 0.6) / (n_mullions - 1)
            _make_box_local(f"{name_prefix}_{bay_tag}_GlassMul_{k}",
                            (mx, glass_y, ground_z + height / 2),
                            (0.10, 0.06, height), col_glass_frame)
        _make_box_local(f"{name_prefix}_{bay_tag}_GlassTopRail",
                        (bcx, glass_y, ground_z + height - 0.08),
                        (bay_w_local - 0.2, 0.08, 0.16), col_glass_frame)
        _make_box_local(f"{name_prefix}_{bay_tag}_GlassBotRail",
                        (bcx, glass_y, ground_z + 0.20),
                        (bay_w_local - 0.2, 0.08, 0.40), col_glass_frame)
        # Entry door — Kwik Stop puts it OFF-CENTER (east) so the
        # SW counter has unobstructed glass frontage and the door
        # leads customers past the counter to the aisles.
        # Arcade + laundromat keep centered doors (small bays).
        if bay_tag == "KwikStop":
            door_off_x = +bay_w_local / 2 - 2.0
            door_w = 1.4
        else:
            door_off_x = 0.0
            door_w = 1.2
        door_x = bcx + door_off_x
        door_h = 2.4
        for sgn in (-1, 1):
            _make_box_local(
                f"{name_prefix}_{bay_tag}_DoorJamb_{sgn:+d}",
                (door_x + sgn * door_w / 2, glass_y,
                 ground_z + door_h / 2),
                (0.12, 0.10, door_h), col_trim)
        _make_box_local(f"{name_prefix}_{bay_tag}_DoorHeader",
                        (door_x, glass_y,
                         ground_z + door_h + 0.08),
                        (door_w + 0.12, 0.10, 0.16), col_trim)
        _make_cyl_local(f"{name_prefix}_{bay_tag}_DoorHandle",
                        (door_x + 0.20, glass_y - 0.06,
                         ground_z + 1.10),
                        0.025, 0.40, col_glass_frame, segments=4)
        _make_box_local(f"{name_prefix}_{bay_tag}_DoorMat",
                        (door_x, glass_y - 0.40,
                         ground_z + 0.07),
                        (door_w + 0.20, 0.80, 0.02),
                        (0.32, 0.22, 0.18, 1.0))
        # Per-bay roof sign
        sign_h_local = 0.8
        sign_y = cy - depth / 2 - 0.36
        _make_box_local(f"{name_prefix}_{bay_tag}_SignPanel",
                        (bcx, sign_y,
                         ground_z + height + 0.20 + sign_h_local / 2),
                        (bay_w_local * 0.85, 0.12, sign_h_local), col_sign)
        _make_box_local(f"{name_prefix}_{bay_tag}_SignTrim",
                        (bcx, sign_y,
                         ground_z + height + 0.20 + sign_h_local + 0.05),
                        (bay_w_local * 0.85 + 0.10, 0.14, 0.10), col_trim)

    # ── BAY-SPECIFIC INTERIORS ─────────────────────────────────
    # ARCADE bay — narrower bay (6m wide) so we drop to 3 arcade
    # cabinets in a row near the back wall.
    arc_cx = cx + ARCADE_OX
    COL_CAB_BODY = (0.18, 0.18, 0.22, 1.0)
    COL_CAB_SCREEN = (0.32, 0.55, 0.78, 1.0)
    COL_CAB_MARQUEE = (0.95, 0.42, 0.30, 1.0)
    for k in range(3):
        kx = arc_cx - 2.0 + k * 2.0
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
                    (arc_cx - BAY_W_ARCADE / 2 + 0.4,
                     cy + 0.5, ground_z + 0.80),
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
    # attendant has clearance between counter and shelf. Width
    # fits within the narrower 6m arcade bay.
    _make_box_local("KwikShop_Arc_AttBooth_PrizeShelf",
                    (booth_x, cy + depth / 2 - 0.15,
                     ground_z + 1.30),
                    (BAY_W_ARCADE - 1.0, 0.15, 1.40),
                    (0.42, 0.42, 0.45, 1.0))
    # A row of small token boxes on top of the counter
    for k in range(3):
        tx = booth_x - 0.6 + k * 0.6
        _make_box_local(f"KwikShop_Arc_AttBooth_TokenBox_{k}",
                        (tx, booth_y, ground_z + 1.18),
                        (0.30, 0.30, 0.12),
                        (0.95, 0.85, 0.30, 1.0))   # gold tokens

    # ── KWIK STOP bay · REFERENCE INTERIOR for the chapter-one
    # cluster. Per user direction (2026-06-15): "do quality,
    # polish sculpting and retail passes at the qwik stop. this
    # will become a reference locale for this zone."
    #
    # Bay layout (south door entry working north):
    #   · ENTRY ZONE  cy-4.95 to cy-3.0: welcome mat + wire-
    #     basket stack + magazine rack + newspaper stand
    #   · AISLE ZONE  cy-3.0 to cy+2.0: two long shelves running
    #     E-W (south = snacks, north = drinks + sundries)
    #   · COOLER WALL cy+3.0 to cy+4.4: 3-door refrigerated
    #     drinks cooler against the back wall
    #   · COUNTER NE  ks_x+2.8, cy+3.45: cash register + scanner
    #     + lottery scratch ticket display + tip jar + ID-check
    #     sign + back-wall cigarette + lotto racks
    #   · WEST FIXTURES cy-2..cy+2 against west partition:
    #     coffee station + roller grill (hot dogs) + slushie
    #     machine
    # Kwik Stop bay center (was cx; now offset to the EAST end of
    # the strip since arcade+laundromat occupy the WEST half).
    kw_cx = cx + KWIKSTOP_OX
    kw_bay_w = BAY_W_KWIKSTOP
    # All the legacy Kwik Stop interior code references `bay_w` as
    # a bare local — alias it to the Kwik Stop width so the
    # canopy, columns, pendant lights, ATM, security camera,
    # pylon, ice freezer, propane cage, news boxes, pay phone,
    # air pump, sandwich board, bike rack, lot lamp, etc.
    # automatically scale to the new 16m bay.
    bay_w = kw_bay_w
    col_shelf      = (0.50, 0.50, 0.52, 1.0)
    col_shelf_dark = (0.32, 0.32, 0.34, 1.0)
    col_counter    = (0.42, 0.32, 0.22, 1.0)
    col_register   = (0.20, 0.20, 0.22, 1.0)
    col_cooler     = (0.78, 0.84, 0.88, 1.0)
    col_cooler_frame = (0.42, 0.42, 0.45, 1.0)
    col_basket     = (0.60, 0.20, 0.18, 1.0)
    col_floor_mat  = (0.30, 0.22, 0.18, 1.0)
    col_chips_orange = (0.95, 0.55, 0.20, 1.0)
    col_chips_red    = (0.85, 0.22, 0.20, 1.0)
    col_chips_blue   = (0.32, 0.55, 0.78, 1.0)
    col_chips_green  = (0.32, 0.55, 0.25, 1.0)
    col_chips_yellow = (0.95, 0.85, 0.30, 1.0)
    col_chips_purple = (0.62, 0.42, 0.78, 1.0)
    col_slushie_a  = (0.62, 0.22, 0.62, 1.0)
    col_slushie_b  = (0.95, 0.62, 0.20, 1.0)
    col_steel      = (0.62, 0.62, 0.64, 1.0)
    col_coffee_pot = (0.20, 0.18, 0.16, 1.0)
    col_grill_dark = (0.32, 0.30, 0.28, 1.0)
    col_grill_hot  = (0.62, 0.18, 0.16, 1.0)

    # ── 2 LONG E-W aisles (snack + drinks) running across most
    # of the bay width. Wider now (12m) to fill the new 16m bay.
    aisle_w = 12.0       # X span (centered on bay)
    aisle_d = 0.40       # shelf thickness (Y axis)
    aisle_h = 1.8
    for k, aisle_y in enumerate((cy - 1.0, cy + 1.5)):
        # Main shelf body
        _make_box_local(f"KwikShop_KwikStop_Aisle_{k}",
                        (kw_cx, aisle_y, ground_z + aisle_h / 2),
                        (aisle_w, aisle_d, aisle_h), col_shelf)
        # Top horizontal "shelf" panel
        _make_box_local(f"KwikShop_KwikStop_AisleTop_{k}",
                        (kw_cx, aisle_y, ground_z + aisle_h),
                        (aisle_w, aisle_d + 0.08, 0.04),
                        col_shelf_dark)
        # Per-side stacked product boxes — alternating colours
        # to read as bags of chips / snack bags.
        product_palettes = [col_chips_orange, col_chips_red,
                             col_chips_blue, col_chips_green,
                             col_chips_yellow, col_chips_purple,
                             col_chips_red, col_chips_orange]
        for sgn in (-1, 1):
            # 14 product bags per side at top (more bags for the
            # wider aisle)
            for j in range(14):
                px = kw_cx - aisle_w / 2 + 0.4 + j * (aisle_w - 0.8) / 13
                _make_box_local(
                    f"KwikShop_KwikStop_Goods_{k}_{sgn:+d}_{j}",
                    (px,
                     aisle_y + sgn * (aisle_d / 2 + 0.04),
                     ground_z + aisle_h - 0.18),
                    (0.50, 0.10, 0.36),
                    product_palettes[(j + k * 3) % len(product_palettes)])
            # Mid-shelf row of products (smaller boxes)
            for j in range(9):
                px = kw_cx - aisle_w / 2 + 0.6 + j * (aisle_w - 1.2) / 8
                _make_box_local(
                    f"KwikShop_KwikStop_GoodsMid_{k}_{sgn:+d}_{j}",
                    (px,
                     aisle_y + sgn * (aisle_d / 2 + 0.03),
                     ground_z + aisle_h - 0.70),
                    (0.40, 0.08, 0.30),
                    product_palettes[(j + k * 2 + 3) % len(product_palettes)])

    # ── COUNTER · FRONT-LEFT position per the design-guide rule
    # in _3D_MODELING_PLAYBOOK.md. Counter long axis runs E-W
    # along the south wall, west of the door. Visually-distinct
    # build: dark wood body + lighter overhanging laminate top +
    # brown front kickplate so it READS as a counter rather than
    # blending into the cigarette wall behind.
    counter_w = 4.0      # long axis along south wall
    counter_d = 1.00     # deeper so register + scanner + pinpad fit
    counter_h = 1.05
    counter_x = kw_cx - kw_bay_w / 2 + counter_w / 2 + 1.0
    counter_y = cy - depth / 2 + counter_d / 2 + 1.4
    # Main counter body (dark wood)
    _make_box_local("KwikShop_KwikStop_Counter",
                    (counter_x, counter_y,
                     ground_z + counter_h / 2),
                    (counter_w, counter_d, counter_h),
                    (0.38, 0.26, 0.18, 1.0))    # darker than back wall
    # Counter top — LIGHTER laminate with a 5cm OVERHANG so the
    # counter has a clear visual top edge from the storefront view
    _make_box_local("KwikShop_KwikStop_CounterTop",
                    (counter_x, counter_y - 0.06,
                     ground_z + counter_h + 0.025),
                    (counter_w + 0.10, counter_d + 0.10, 0.05),
                    (0.85, 0.78, 0.62, 1.0))    # cream laminate
    # Toe-kick at the bottom (darker recess) — adds visual depth
    _make_box_local("KwikShop_KwikStop_CounterToeKick",
                    (counter_x, counter_y - counter_d / 2 + 0.03,
                     ground_z + 0.08),
                    (counter_w, 0.06, 0.16),
                    (0.18, 0.12, 0.08, 1.0))
    # Display-case glass front (knee to counter-top) on the
    # customer-facing south side — shows scratch tickets + candy
    # bars + phone cards inside. Reads as a working retail bar.
    _make_box_local("KwikShop_KwikStop_CounterCase",
                    (counter_x, counter_y - counter_d / 2 - 0.005,
                     ground_z + counter_h * 0.65),
                    (counter_w - 0.10, 0.04, counter_h * 0.55),
                    (0.62, 0.78, 0.85, 1.0))    # tinted glass
    # Inside the case: 4 product rectangles visible through glass
    for k_disp in range(4):
        dx = counter_x - counter_w / 2 + 0.6 + k_disp * (counter_w - 1.2) / 3
        disp_col = [
            (0.95, 0.85, 0.30, 1.0),   # gold scratch tickets
            (0.85, 0.20, 0.18, 1.0),   # red phone cards
            (0.32, 0.55, 0.78, 1.0),   # blue prepaid
            (0.95, 0.94, 0.86, 1.0),   # cream specialty
        ][k_disp]
        _make_box_local(
            f"KwikShop_KwikStop_CounterDisplay_{k_disp}",
            (dx, counter_y - counter_d / 2 + 0.10,
             ground_z + counter_h * 0.50),
            (0.45, 0.30, 0.30), disp_col)
    _make_box_local("KwikShop_KwikStop_Register",
                    (counter_x - 0.6, counter_y,
                     ground_z + counter_h + 0.15),
                    (0.55, 0.40, 0.30), col_register)
    # Scanner / display next to register
    _make_box_local("KwikShop_KwikStop_Scanner",
                    (counter_x - 0.6, counter_y - 0.05,
                     ground_z + counter_h + 0.45),
                    (0.18, 0.10, 0.20),
                    (0.42, 0.42, 0.45, 1.0))
    # Lottery scratch-ticket display (vertical box on counter)
    _make_box_local("KwikShop_KwikStop_LottoCase",
                    (counter_x + 0.5, counter_y,
                     ground_z + counter_h + 0.20),
                    (0.40, 0.30, 0.36),
                    (0.95, 0.85, 0.30, 1.0))
    # Tip jar (small cyl)
    _make_cyl_local("KwikShop_KwikStop_TipJar",
                    (counter_x + 0.1, counter_y - 0.20,
                     ground_z + counter_h + 0.10),
                    0.06, 0.20,
                    (0.42, 0.50, 0.58, 1.0), segments=8)
    # ID-check sign on the counter front
    _make_box_local("KwikShop_KwikStop_IDSign",
                    (counter_x, counter_y - counter_d / 2 - 0.04,
                     ground_z + counter_h * 0.55),
                    (0.50, 0.04, 0.30),
                    (0.85, 0.20, 0.18, 1.0))
    # Cigarette + lottery rack BACKBOARD against back wall.
    # Backboard moved 0.8m NORTH of counter (was 0.10m) so the
    # clerk has a real 0.8m aisle to stand in between counter and
    # backboard. The old 0.10m gap had Sam crushed against the
    # cigarette wall and reading as "in front of the counter" from
    # the storefront-glass view.
    BACKBOARD_OFFSET = 0.80    # clerk aisle width
    _make_box_local("KwikShop_KwikStop_BackBoard",
                    (counter_x,
                     counter_y + counter_d / 2 + BACKBOARD_OFFSET,
                     ground_z + 1.6),
                    (counter_w + 0.4, 0.10, 1.6),
                    col_shelf_dark)
    # Horizontal shelves on the backboard (cigarette cartons)
    for shelf_z in (ground_z + 1.30, ground_z + 1.80, ground_z + 2.30):
        _make_box_local(
            f"KwikShop_KwikStop_BackShelf_{int(shelf_z*10)}",
            (counter_x,
             counter_y + counter_d / 2 + BACKBOARD_OFFSET + 0.06,
             shelf_z),
            (counter_w + 0.3, 0.12, 0.04),
            (0.55, 0.42, 0.30, 1.0))
    # 8 cigarette cartons in a row on the middle shelf
    for k in range(8):
        cx_c = counter_x - counter_w / 2 + 0.15 + k * (counter_w - 0.3) / 7
        _make_box_local(f"KwikShop_KwikStop_Cigs_{k}",
                        (cx_c,
                         counter_y + counter_d / 2 + BACKBOARD_OFFSET + 0.05,
                         ground_z + 1.95),
                        (0.18, 0.08, 0.12),
                        (0.85, 0.85, 0.85, 1.0) if k % 3 != 0
                        else (0.20, 0.45, 0.20, 1.0))

    # ── BIG REFRIGERATED COOLER along the back wall · 3 glass
    # doors with stacked products visible inside. Replaces the
    # old narrow cooler.
    cooler_total_w = 5.0
    cooler_h = 2.4
    cooler_d = 0.40
    cooler_cx = kw_cx - bay_w / 2 + cooler_total_w / 2 + 0.30
    # Body (the metal back/sides of the cooler unit)
    _make_box_local("KwikShop_KwikStop_Cooler",
                    (cooler_cx,
                     cy + depth / 2 - 0.30,
                     ground_z + cooler_h / 2),
                    (cooler_total_w, cooler_d, cooler_h),
                    col_cooler_frame)
    # 3 glass doors with chrome frames
    for k in range(3):
        dx = cooler_cx - cooler_total_w / 2 + (k + 0.5) * (cooler_total_w / 3)
        _make_box_local(
            f"KwikShop_KwikStop_CoolerDoor_{k}",
            (dx, cy + depth / 2 - 0.50,
             ground_z + cooler_h / 2),
            (cooler_total_w / 3 - 0.08, 0.04, cooler_h - 0.20),
            col_cooler)
        # Handle on each door
        _make_box_local(
            f"KwikShop_KwikStop_CoolerHandle_{k}",
            (dx + 0.5, cy + depth / 2 - 0.52,
             ground_z + 1.20),
            (0.04, 0.04, 0.80),
            (0.42, 0.42, 0.45, 1.0))
        # Stacked product silhouettes visible through the glass
        # (each door shows 4 rows of cans/bottles)
        for row in range(4):
            for col_idx in range(4):
                pdx = dx - 0.45 + col_idx * 0.30
                pdz = ground_z + 0.50 + row * 0.40
                # Alternate colors per row/col
                cans_palette = [
                    (0.85, 0.22, 0.20, 1.0),     # red cola
                    (0.32, 0.55, 0.78, 1.0),     # blue energy
                    (0.32, 0.55, 0.25, 1.0),     # green soda
                    (0.95, 0.85, 0.30, 1.0),     # yellow citrus
                ]
                _make_box_local(
                    f"KwikShop_KwikStop_CoolerCan_{k}_{row}_{col_idx}",
                    (pdx,
                     cy + depth / 2 - 0.40,
                     pdz),
                    (0.20, 0.06, 0.30),
                    cans_palette[(row + col_idx + k) % 4])

    # ── BACK COOLER RECURSIVE-REFLECTION HOTSPOT · canonical
    # detail from Maya Daigle's NEWS FROM HARMONY CREEK #11 ("the
    # cooler's reflection contains the back of the cooler's own
    # surface, an infinite recursion of itself"). Rendered as five
    # nested rectangles on the MIDDLE door, each smaller and
    # slightly darker, suggesting an infinite recess. Reads at
    # close range as a "wrong" reflection in the glass.
    mid_dx = cooler_cx   # middle door centerline x
    rec_y = cy + depth / 2 - 0.49   # just in front of the door
    rec_z = ground_z + 1.60
    rec_palette = [
        (0.42, 0.50, 0.55, 1.0),
        (0.32, 0.40, 0.45, 1.0),
        (0.22, 0.30, 0.35, 1.0),
        (0.15, 0.22, 0.27, 1.0),
        (0.08, 0.14, 0.18, 1.0),
    ]
    for k_rec, col_rec in enumerate(rec_palette):
        rs = 0.50 - k_rec * 0.10  # shrinking rectangles
        _make_box_local(
            f"KwikShop_KwikStop_RecursionPanel_{k_rec}",
            (mid_dx, rec_y - k_rec * 0.001,
             rec_z),
            (rs, 0.002, rs * 0.80), col_rec)

    # ── WEST-WALL FIXTURE COLUMN · slushie + coffee + roller
    # grill stacked S→N along the partition wall. Each fixture
    # is shallower in X (~0.55 m) so it sits flush against the
    # west wall, with its FACE (long dimension along Y) toward
    # the bay interior. Previous layout had these against the
    # BACK wall, overlapping the counter at the NE corner.
    wall_x = kw_cx - bay_w / 2 + 0.40   # 0.40 m east of partition

    # ROLLER GRILL — northernmost (closest to counter/staff)
    rg_y = cy + 2.5
    _make_box_local("KwikShop_KwikStop_RollerGrillCounter",
                    (wall_x, rg_y, ground_z + 0.40),
                    (0.55, 0.80, 0.80),
                    (0.62, 0.55, 0.45, 1.0))
    _make_box_local("KwikShop_KwikStop_RollerGrillCase",
                    (wall_x, rg_y, ground_z + 1.00),
                    (0.55, 0.80, 0.60), col_grill_dark)
    # 4 roller bars + hot dogs on top (bars run Y direction since
    # the case is along Y now)
    for k in range(4):
        rry = rg_y - 0.30 + k * 0.20
        _make_box_local(f"KwikShop_KwikStop_Roller_{k}",
                        (wall_x, rry, ground_z + 0.95),
                        (0.40, 0.04, 0.04), col_steel)
        _make_box_local(f"KwikShop_KwikStop_HotDog_{k}",
                        (wall_x, rry, ground_z + 1.05),
                        (0.40, 0.06, 0.06),
                        (0.78, 0.55, 0.30, 1.0))
    _make_box_local("KwikShop_KwikStop_RollerGrillHeat",
                    (wall_x, rg_y, ground_z + 0.92),
                    (0.50, 0.70, 0.02), col_grill_hot)

    # COFFEE STATION — middle
    cof_y = cy + 0.8
    _make_box_local("KwikShop_KwikStop_CoffeeCounter",
                    (wall_x, cof_y, ground_z + 0.40),
                    (0.55, 1.20, 0.80),
                    (0.62, 0.55, 0.45, 1.0))
    _make_box_local("KwikShop_KwikStop_CoffeeBrewer",
                    (wall_x, cof_y, ground_z + 1.10),
                    (0.50, 0.55, 0.60), col_steel)
    for k, oy in enumerate((-0.25, 0.25)):
        _make_cyl_local(f"KwikShop_KwikStop_CoffeePot_{k}",
                        (wall_x, cof_y + oy, ground_z + 0.95),
                        0.08, 0.22, col_coffee_pot, segments=8)
    _make_box_local("KwikShop_KwikStop_CoffeeCaddy",
                    (wall_x, cof_y + 0.45, ground_z + 0.90),
                    (0.30, 0.30, 0.20),
                    (0.42, 0.42, 0.45, 1.0))
    _make_cyl_local("KwikShop_KwikStop_CupStack",
                    (wall_x, cof_y - 0.45, ground_z + 0.85),
                    0.05, 0.40,
                    (0.95, 0.95, 0.92, 1.0), segments=8)

    # SLUSHIE MACHINE — southernmost (closest to entry zone)
    sl_y = cy - 1.5
    _make_box_local("KwikShop_KwikStop_Slushie_Base",
                    (wall_x, sl_y, ground_z + 1.10),
                    (0.55, 0.85, 2.20), col_steel)
    for k, col in enumerate((col_slushie_a, col_slushie_b)):
        _make_box_local(f"KwikShop_KwikStop_Slushie_Tank_{k}",
                        (wall_x, sl_y - 0.25 + k * 0.50,
                         ground_z + 1.85),
                        (0.50, 0.40, 0.50), col)
    for k in range(2):
        _make_cyl_local(f"KwikShop_KwikStop_Slushie_Nozzle_{k}",
                        (wall_x + 0.30,
                         sl_y - 0.25 + k * 0.50, ground_z + 1.55),
                        0.05, 0.20, col_steel, segments=4)

    # ── ENTRY ZONE props (welcome mat already exists outside;
    # add interior entrance fixtures)
    # Wire basket STACK (3 nested) at the entry
    for k in range(3):
        _make_box_local(f"KwikShop_KwikStop_WireBasket_{k}",
                        (kw_cx + 3.0,
                         cy - depth / 2 + 1.0 + k * 0.04,
                         ground_z + 0.10 + k * 0.10),
                        (0.40, 0.30, 0.20), col_basket)
    # Magazine rack (vertical narrow shelf on the west side of
    # the entry zone)
    _make_box_local("KwikShop_KwikStop_MagRack",
                    (kw_cx - 3.0, cy - depth / 2 + 1.0,
                     ground_z + 1.0),
                    (0.40, 0.40, 1.6),
                    col_shelf_dark)
    # 6 magazines visible on the rack (small colored boxes)
    mag_colours = [(0.85, 0.22, 0.20, 1.0), (0.95, 0.85, 0.30, 1.0),
                    (0.32, 0.55, 0.78, 1.0), (0.62, 0.42, 0.78, 1.0),
                    (0.95, 0.55, 0.20, 1.0), (0.42, 0.62, 0.32, 1.0)]
    for k in range(6):
        _make_box_local(f"KwikShop_KwikStop_Mag_{k}",
                        (kw_cx - 3.0, cy - depth / 2 + 0.78,
                         ground_z + 0.30 + k * 0.25),
                        (0.30, 0.04, 0.22),
                        mag_colours[k % len(mag_colours)])
    # Floor entry mat (interior side)
    _make_box_local("KwikShop_KwikStop_FloorMat",
                    (kw_cx, cy - depth / 2 + 0.6,
                     ground_z + 0.06),
                    (2.4, 1.2, 0.02), col_floor_mat)
    # ── CEILING FLUORESCENT FIXTURES — 4 long boxes hanging
    # below the roof (visual only, no Light3D — those go in the
    # scene file)
    for k in range(4):
        fx_l = kw_cx - 3.0 + k * 2.0
        _make_box_local(f"KwikShop_KwikStop_Fluo_{k}",
                        (fx_l, cy, ground_z + 3.4),
                        (1.6, 0.20, 0.10),
                        (0.95, 0.94, 0.90, 1.0))

    # ── SLOPED CANOPY OVER THE STOREFRONT (matches the
    # user-provided Kwik Stop reference photo). A wide canopy
    # extending out from the storefront's parapet, supported by
    # 4 columns at the south sidewalk edge. The canopy reads as
    # a covered walkway — the awnings above each door remain
    # underneath it as smaller signage canopies.
    can_north_y = cy - depth / 2 - 0.10     # at storefront wall
    can_south_y = cy - depth / 2 - 3.0      # 3 m forward of glass
    can_top_z = ground_z + height + 0.05    # base of canopy
    can_drop = 0.30                          # south edge drop
    col_canopy_tan = (0.68, 0.55, 0.45, 1.0)
    col_canopy_trim = (0.42, 0.30, 0.20, 1.0)
    # Canopy slab — a quad sloping slightly down toward the
    # south edge (front)
    can_verts = [
        (kw_cx - bay_w / 2, can_north_y, can_top_z + 0.20),
        (kw_cx + bay_w / 2, can_north_y, can_top_z + 0.20),
        (kw_cx + bay_w / 2, can_south_y, can_top_z + 0.20 - can_drop),
        (kw_cx - bay_w / 2, can_south_y, can_top_z + 0.20 - can_drop),
        # Underside (5 cm thick)
        (kw_cx - bay_w / 2, can_north_y, can_top_z + 0.15),
        (kw_cx + bay_w / 2, can_north_y, can_top_z + 0.15),
        (kw_cx + bay_w / 2, can_south_y, can_top_z + 0.15 - can_drop),
        (kw_cx - bay_w / 2, can_south_y, can_top_z + 0.15 - can_drop),
    ]
    can_faces = [
        [0, 1, 2, 3],          # top
        [4, 7, 6, 5],          # bottom
        [0, 4, 5, 1],          # north (back)
        [1, 5, 6, 2],          # east side
        [2, 6, 7, 3],          # south (front lip)
        [3, 7, 4, 0],          # west side
    ]
    _finalize_mesh("KwikShop_KwikStop_Canopy", can_verts, can_faces,
                    col_canopy_tan)
    # Horizontal trim band on the south face of the canopy
    _make_box_local("KwikShop_KwikStop_CanopyTrim",
                    (kw_cx, can_south_y,
                     can_top_z + 0.18 - can_drop - 0.05),
                    (bay_w, 0.10, 0.20), col_canopy_trim)
    # 4 white-painted steel columns supporting the canopy at
    # the south edge
    for k in range(4):
        col_x = kw_cx - bay_w / 2 + 1.0 + k * (bay_w - 2.0) / 3
        col_z_bottom = ground_z
        col_z_top = can_top_z + 0.15 - can_drop
        _make_cyl_local(f"KwikShop_KwikStop_CanopyCol_{k}",
                        (col_x, can_south_y,
                         (col_z_bottom + col_z_top) / 2),
                        0.12, col_z_top - col_z_bottom,
                        (0.95, 0.92, 0.86, 1.0), segments=6)
    # Ceiling pendant lights mounted to canopy underside (4)
    for k in range(4):
        lt_x = kw_cx - bay_w / 2 + 1.5 + k * (bay_w - 3.0) / 3
        lt_y = (can_north_y + can_south_y) / 2
        _make_box_local(f"KwikShop_KwikStop_CanopyLight_{k}",
                        (lt_x, lt_y,
                         can_top_z + 0.10 - can_drop / 2),
                        (0.30, 0.30, 0.06),
                        (0.95, 0.88, 0.62, 1.0))

    # ── INTERIOR "Harmony Creek Estates" banner above the back
    # wall (district-branding sign visible from the customer
    # area, per the Kwik Stop reference photo). Big blue plaque
    # with cream text, hung above the counter.
    hce_banner_x = kw_cx
    hce_banner_y = cy + depth / 2 - 0.30
    hce_banner_z = ground_z + 2.80
    _make_box_local("KwikShop_KwikStop_HCEBanner",
                    (hce_banner_x, hce_banner_y, hce_banner_z),
                    (5.0, 0.10, 0.60),
                    (0.18, 0.32, 0.55, 1.0))
    _make_box_local("KwikShop_KwikStop_HCEBannerTrim_Top",
                    (hce_banner_x, hce_banner_y, hce_banner_z + 0.34),
                    (5.2, 0.12, 0.08),
                    (0.32, 0.32, 0.34, 1.0))
    _make_box_local("KwikShop_KwikStop_HCEBannerTrim_Bot",
                    (hce_banner_x, hce_banner_y, hce_banner_z - 0.34),
                    (5.2, 0.12, 0.08),
                    (0.32, 0.32, 0.34, 1.0))

    # ── WINDOW THERMOMETER DECAL · small red-and-white
    # thermometer in one of the storefront window bays
    _make_box_local("KwikShop_KwikStop_ThermometerBg",
                    (kw_cx - 3.6, cy - depth / 2 + 0.05 - 0.04,
                     ground_z + 2.6),
                    (0.30, 0.04, 0.80),
                    (0.95, 0.95, 0.92, 1.0))
    # Red mercury column
    _make_box_local("KwikShop_KwikStop_ThermometerCol",
                    (kw_cx - 3.6, cy - depth / 2 + 0.05 - 0.05,
                     ground_z + 2.4),
                    (0.08, 0.02, 0.40),
                    (0.85, 0.20, 0.18, 1.0))
    # Bulb
    _make_cyl_local("KwikShop_KwikStop_ThermometerBulb",
                    (kw_cx - 3.6, cy - depth / 2 + 0.05 - 0.05,
                     ground_z + 2.20),
                    0.06, 0.04,
                    (0.85, 0.20, 0.18, 1.0), segments=8)

    # ── EXTERIOR POLISH for the Kwik Stop bay — window decals,
    # OPEN sign, security camera, ATM, bordering planter
    glass_y_bay = cy - depth / 2 + 0.05
    # OPEN neon sign hung in the right-bay window
    _make_box_local("KwikShop_KwikStop_OpenSign",
                    (kw_cx + 2.5, glass_y_bay - 0.04,
                     ground_z + 2.4),
                    (0.60, 0.04, 0.20),
                    (0.85, 0.20, 0.18, 1.0))
    # Window decals (small color panels suggesting lottery, ATM,
    # ice, etc.) along the bottom of the south face
    decals = [
        (-3.0, (0.95, 0.85, 0.30, 1.0)),   # gold "LOTTERY"
        (-2.0, (0.32, 0.55, 0.78, 1.0)),   # blue "ATM"
        (-1.0, (0.95, 0.94, 0.90, 1.0)),   # cream "ICE"
        ( 3.0, (0.85, 0.22, 0.20, 1.0)),   # red "EBT"
    ]
    for k, (x_off, col_d) in enumerate(decals):
        _make_box_local(f"KwikShop_KwikStop_Decal_{k}",
                        (kw_cx + x_off, glass_y_bay - 0.04,
                         ground_z + 0.85),
                        (0.50, 0.04, 0.35), col_d)
    # Security camera mounted at the SE corner of the storefront
    cam_x = kw_cx + bay_w / 2 - 0.4
    cam_y = glass_y_bay - 0.10
    cam_z = ground_z + height - 0.30
    # Mount bracket
    _make_box_local("KwikShop_KwikStop_CamMount",
                    (cam_x, cam_y - 0.05, cam_z),
                    (0.08, 0.16, 0.08),
                    (0.32, 0.32, 0.34, 1.0))
    # Camera body (cylinder facing down + south)
    _make_cyl_local("KwikShop_KwikStop_CamBody",
                    (cam_x, cam_y - 0.18, cam_z - 0.10),
                    0.08, 0.20,
                    (0.18, 0.18, 0.20, 1.0), segments=8)
    # Tiny red LED on the camera
    _make_box_local("KwikShop_KwikStop_CamLED",
                    (cam_x, cam_y - 0.28, cam_z - 0.08),
                    (0.03, 0.02, 0.03),
                    (0.85, 0.10, 0.10, 1.0))

    # ── ATM kiosk on the sidewalk outside the storefront, just
    # east of the door
    atm_x = kw_cx + 3.5
    atm_y = glass_y_bay - 0.70
    atm_z = mesh_z(atm_x, atm_y)
    # ATM body
    _make_box_local("KwikShop_KwikStop_ATM_Body",
                    (atm_x, atm_y, atm_z + 0.85),
                    (0.70, 0.50, 1.70),
                    (0.42, 0.42, 0.45, 1.0))
    # Screen
    _make_box_local("KwikShop_KwikStop_ATM_Screen",
                    (atm_x, atm_y - 0.26, atm_z + 1.30),
                    (0.50, 0.04, 0.30),
                    (0.18, 0.32, 0.42, 1.0))
    # Card slot strip
    _make_box_local("KwikShop_KwikStop_ATM_Card",
                    (atm_x, atm_y - 0.26, atm_z + 0.90),
                    (0.30, 0.04, 0.04),
                    (0.85, 0.85, 0.85, 1.0))
    # ATM sign on top
    _make_box_local("KwikShop_KwikStop_ATM_Sign",
                    (atm_x, atm_y, atm_z + 1.95),
                    (0.70, 0.50, 0.30),
                    (0.32, 0.55, 0.78, 1.0))

    # ── GUMBALL / STICKER MACHINES outside, west of the door
    gum_y = glass_y_bay - 0.50
    for k, col in enumerate(((0.85, 0.20, 0.18, 1.0),     # red
                              (0.32, 0.55, 0.78, 1.0),     # blue
                              (0.95, 0.85, 0.30, 1.0))):    # yellow
        gx = kw_cx - 3.5 + k * 0.5
        gz = mesh_z(gx, gum_y)
        # Pedestal
        _make_cyl_local(f"KwikShop_KwikStop_Gum_Stand_{k}",
                        (gx, gum_y, gz + 0.40),
                        0.10, 0.80,
                        (0.32, 0.32, 0.34, 1.0), segments=6)
        # Globe / dispenser top
        _make_sphere_low_local(f"KwikShop_KwikStop_Gum_Globe_{k}",
                                (gx, gum_y, gz + 1.10),
                                0.22, col, rings=3, segments=8)
        # Coin mechanism base
        _make_box_local(f"KwikShop_KwikStop_Gum_Base_{k}",
                        (gx, gum_y, gz + 0.85),
                        (0.22, 0.22, 0.16), col_steel)

    # ── HOURS placard on the door jamb · small dark plaque
    _make_box_local("KwikShop_KwikStop_HoursPlaque",
                    (kw_cx + 1.0, glass_y_bay - 0.06,
                     ground_z + 1.95),
                    (0.30, 0.04, 0.40),
                    (0.18, 0.18, 0.20, 1.0))

    # ── PROMO BANNER hung from the awning · long red strip with
    # white text suggested
    _make_box_local("KwikShop_KwikStop_PromoBanner",
                    (kw_cx, glass_y_bay - 1.30,
                     ground_z + 2.55),
                    (4.0, 0.04, 0.50),
                    (0.85, 0.20, 0.18, 1.0))

    # ── PYLON SIGN at the south edge of the parking lot (the
    # tall street-visible Kwik Stop sign from the reference photo)
    pyl_x = kw_cx + bay_w / 2 + 8.0
    pyl_y = cy - depth / 2 - 28.0       # south end of lot
    pyl_z = mesh_z(pyl_x, pyl_y)
    PYLON_H = 8.0
    col_pyl_pole = (0.62, 0.62, 0.64, 1.0)
    col_pyl_blue = (0.18, 0.32, 0.55, 1.0)
    col_pyl_white = (0.95, 0.94, 0.90, 1.0)
    col_pyl_red = (0.85, 0.20, 0.18, 1.0)
    # Pole
    _make_cyl_local("KwikShop_KwikStop_Pylon_Pole",
                    (pyl_x, pyl_y, pyl_z + PYLON_H / 2),
                    0.18, PYLON_H, col_pyl_pole, segments=6)
    # Main top sign (blue background, "KWIK STOP")
    _make_box_local("KwikShop_KwikStop_PylonSign_Top",
                    (pyl_x, pyl_y, pyl_z + PYLON_H + 0.6),
                    (2.4, 0.18, 1.0), col_pyl_blue)
    # Texas star on top corner of the top sign
    _make_box_local("KwikShop_KwikStop_PylonStar",
                    (pyl_x - 0.90, pyl_y - 0.10,
                     pyl_z + PYLON_H + 0.95),
                    (0.40, 0.04, 0.40), col_pyl_red)
    # White price-strip bands below (3 strips for prices /
    # promos / Kwik branding info)
    for k in range(3):
        _make_box_local(f"KwikShop_KwikStop_PylonStrip_{k}",
                        (pyl_x, pyl_y,
                         pyl_z + PYLON_H + 0.0 - k * 0.45),
                        (2.2, 0.18, 0.40), col_pyl_white)
    # Strip border trims
    for k in range(4):
        _make_box_local(f"KwikShop_KwikStop_PylonStripTrim_{k}",
                        (pyl_x, pyl_y,
                         pyl_z + PYLON_H + 0.10 - k * 0.45),
                        (2.4, 0.20, 0.04),
                        (0.42, 0.42, 0.45, 1.0))

    # ── LOTTERY MARQUEE · LED scrolling numbers display below the
    # main pylon. Dark CRT panel with amber dots suggesting current
    # Powerball + Lotto Texas numbers. Highly visible from the
    # road approach.
    lot_z = pyl_z + PYLON_H - 1.40
    _make_box_local("KwikShop_KwikStop_PylonLotto_Bg",
                    (pyl_x, pyl_y, lot_z),
                    (2.4, 0.20, 0.32),
                    (0.18, 0.18, 0.20, 1.0))
    # "TX LOTTO" header label (orange)
    _make_box_local("KwikShop_KwikStop_PylonLotto_Header",
                    (pyl_x - 0.85, pyl_y - 0.11,
                     lot_z + 0.08),
                    (0.55, 0.04, 0.10),
                    (0.92, 0.55, 0.20, 1.0))
    # 6 LED-style number bubbles (amber on dark)
    for k in range(6):
        bx = pyl_x - 0.80 + k * 0.32
        _make_box_local(f"KwikShop_KwikStop_PylonLotto_Num_{k}",
                        (bx, pyl_y - 0.11, lot_z - 0.06),
                        (0.22, 0.04, 0.16),
                        (0.95, 0.78, 0.20, 1.0))

    # ── GAS NEXT DOOR cross-promotion · small green arrow strip
    # at the very bottom of the pylon
    _make_box_local("KwikShop_KwikStop_PylonGasArrow",
                    (pyl_x, pyl_y, pyl_z + PYLON_H - 2.20),
                    (2.4, 0.20, 0.30),
                    (0.32, 0.55, 0.32, 1.0))
    # Arrow shape (suggested by a thin pointing strip)
    _make_box_local("KwikShop_KwikStop_PylonGasArrowHead",
                    (pyl_x - 0.95, pyl_y - 0.11,
                     pyl_z + PYLON_H - 2.20),
                    (0.32, 0.04, 0.16),
                    (0.95, 0.94, 0.90, 1.0))

    # ── PYLON BASE PLINTH · brick-veneer base hiding the pole's
    # ground anchor + utility-meter cabinet
    _make_box_local("KwikShop_KwikStop_PylonPlinth",
                    (pyl_x, pyl_y, pyl_z + 0.40),
                    (1.10, 0.70, 0.80),
                    (0.55, 0.32, 0.22, 1.0))
    # Utility cabinet on the back of the plinth
    _make_box_local("KwikShop_KwikStop_PylonUtilityCab",
                    (pyl_x, pyl_y + 0.40, pyl_z + 0.55),
                    (0.40, 0.10, 0.50),
                    (0.42, 0.42, 0.45, 1.0))

    # ── COUNTER DETAIL · pinpad + receipt printer + cash drawer
    # Pinpad / card reader to the right of the register, facing
    # the customer
    _make_box_local("KwikShop_KwikStop_Pinpad",
                    (counter_x + 0.10,
                     counter_y - 0.15,
                     ground_z + counter_h + 0.10),
                    (0.16, 0.20, 0.12),
                    (0.32, 0.32, 0.34, 1.0))
    # Receipt printer (small box behind register)
    _make_box_local("KwikShop_KwikStop_ReceiptPrinter",
                    (counter_x - 0.6,
                     counter_y + 0.20,
                     ground_z + counter_h + 0.08),
                    (0.22, 0.18, 0.10),
                    (0.62, 0.62, 0.64, 1.0))
    # Receipt paper strip hanging
    _make_box_local("KwikShop_KwikStop_ReceiptPaper",
                    (counter_x - 0.6,
                     counter_y + 0.10,
                     ground_z + counter_h - 0.10),
                    (0.06, 0.02, 0.30),
                    (0.95, 0.95, 0.92, 1.0))
    # Gum/candy impulse display on the customer side of the
    # counter (a low shelf rack)
    _make_box_local("KwikShop_KwikStop_ImpulseRack",
                    (counter_x,
                     counter_y - counter_d / 2 - 0.18,
                     ground_z + 0.5),
                    (counter_w - 0.2, 0.20, 0.90),
                    (0.42, 0.32, 0.22, 1.0))
    # 6 colorful candy boxes on the impulse rack
    candy_palette = [(0.85, 0.22, 0.20, 1.0),
                      (0.32, 0.55, 0.78, 1.0),
                      (0.95, 0.85, 0.30, 1.0),
                      (0.62, 0.42, 0.78, 1.0),
                      (0.42, 0.62, 0.32, 1.0),
                      (0.95, 0.55, 0.20, 1.0)]
    for k in range(6):
        cdx = counter_x - counter_w / 2 + 0.20 + k * (counter_w - 0.40) / 5
        _make_box_local(f"KwikShop_KwikStop_Candy_{k}",
                        (cdx,
                         counter_y - counter_d / 2 - 0.20,
                         ground_z + 0.85),
                        (0.18, 0.12, 0.15),
                        candy_palette[k])
    # Floor mat behind counter (clerk side)
    _make_box_local("KwikShop_KwikStop_ClerkMat",
                    (counter_x,
                     counter_y + counter_d / 2 + 0.35,
                     ground_z + 0.06),
                    (counter_w + 0.2, 0.50, 0.02),
                    (0.30, 0.22, 0.18, 1.0))

    # ── ENTRY FLOOR MAT inside the door · red Kwik Stop-branded
    # mat with cream border. Player walks over this entering.
    _make_box_local("KwikShop_KwikStop_FloorMat",
                    (kw_cx + 0.2,
                     cy - depth / 2 + 1.0,
                     ground_z + 0.04),
                    (1.40, 1.40, 0.02),
                    (0.55, 0.18, 0.16, 1.0))
    # Cream border around the mat (slightly larger square below)
    _make_box_local("KwikShop_KwikStop_FloorMat_Border",
                    (kw_cx + 0.2,
                     cy - depth / 2 + 1.0,
                     ground_z + 0.035),
                    (1.50, 1.50, 0.02),
                    (0.92, 0.88, 0.78, 1.0))

    # ── MAGAZINE / TABLOID RACK · 3-tier wire rack on the customer
    # side of the impulse area, between counter and entry door
    mag_x = counter_x - counter_w / 2 - 0.8
    mag_y = counter_y - counter_d / 2 - 0.50
    mag_z = ground_z + 0.50
    # Frame stand (chrome)
    _make_box_local("KwikStop_Kwik_MagRack_Frame",
                    (mag_x, mag_y, mag_z + 0.50),
                    (0.55, 0.30, 1.00),
                    (0.62, 0.62, 0.64, 1.0))
    # 3 tier shelves with stacked magazines (different cover
    # colors)
    mag_palette = [
        (0.85, 0.20, 0.18, 1.0),    # red tabloid
        (0.18, 0.32, 0.55, 1.0),    # blue glossy
        (0.95, 0.85, 0.30, 1.0),    # yellow tabloid
    ]
    for k, col_mag in enumerate(mag_palette):
        _make_box_local(
            f"KwikStop_Kwik_MagRack_Tier_{k}",
            (mag_x, mag_y - 0.06, mag_z + 0.20 + k * 0.30),
            (0.45, 0.20, 0.04), col_mag)

    # ── OUTDOOR TRASH BIN by the entry door · dark plastic
    # cylindrical liner inside a powder-coated frame
    tb_x = kw_cx - 1.4
    tb_y = sw_y - 0.30
    tb_z = mesh_z(tb_x, tb_y)
    # Outer frame
    _make_cyl_local("KwikStop_TrashBin_Frame",
                    (tb_x, tb_y, tb_z + 0.45),
                    0.22, 0.90,
                    (0.32, 0.32, 0.34, 1.0), segments=6)
    # Inner liner (slightly smaller, darker)
    _make_cyl_local("KwikStop_TrashBin_Liner",
                    (tb_x, tb_y, tb_z + 0.45),
                    0.18, 0.88,
                    (0.10, 0.10, 0.12, 1.0), segments=6)
    # Black liner bag hanging slightly over the rim
    _make_cyl_local("KwikStop_TrashBin_LinerBag",
                    (tb_x, tb_y, tb_z + 0.92),
                    0.18, 0.06,
                    (0.08, 0.08, 0.10, 1.0), segments=6)

    # ── CONVEX SECURITY MIRROR above the door · canon from
    # Sam Miller's POV ("Sam watches him in the convex security
    # mirror above the door"). Wall-mounted half-sphere giving the
    # clerk eyes on the back of the store.
    mirror_x = kw_cx
    mirror_y = cy - depth / 2 + 0.10    # just inside the south wall
    _make_sphere_low_local("KwikShop_KwikStop_SecurityMirror",
                            (mirror_x, mirror_y, ground_z + 2.95),
                            0.22,
                            (0.78, 0.88, 0.92, 1.0),
                            rings=3, segments=8)
    # Bracket mount
    _make_box_local("KwikShop_KwikStop_SecurityMirror_Bracket",
                    (mirror_x, mirror_y - 0.05, ground_z + 3.10),
                    (0.10, 0.10, 0.06),
                    (0.32, 0.32, 0.34, 1.0))

    # ── HOT POCKET on the counter · the foil-wrapped Hot Pocket
    # Sam eats while watching the back-cooler customer (canon from
    # Maya zine #11 panel 3). Small silver-foil rectangle.
    _make_box_local("KwikShop_KwikStop_HotPocket",
                    (counter_x - counter_w / 2 + 0.30,
                     counter_y - counter_d / 2 + 0.22,
                     ground_z + counter_h + 0.04),
                    (0.14, 0.10, 0.04),
                    (0.78, 0.78, 0.82, 1.0))   # foil

    # ── FLUORESCENT CEILING FIXTURES · 4 long horizontal panels
    # below the ceiling at uniform spacing — typical convenience-
    # store overhead lighting visible through the south plate-glass.
    for k in range(4):
        fix_x = kw_cx - bay_w / 2 + 1.0 + k * (bay_w - 2.0) / 3
        # Fixture housing
        _make_box_local(f"KwikShop_KwikStop_FloLight_{k}_Housing",
                        (fix_x, cy, ground_z + height - 0.15),
                        (0.30, 1.20, 0.10),
                        (0.92, 0.92, 0.90, 1.0))
        # Bright glow tube (offset slightly below the housing)
        _make_box_local(f"KwikStop_KwikStop_FloLight_{k}_Tube",
                        (fix_x, cy, ground_z + height - 0.22),
                        (0.24, 1.10, 0.04),
                        (0.95, 0.94, 0.78, 1.0))

    # ── SAM'S PHONE face-up on the counter · canon detail from
    # Sam Miller's _COMMUNITY_PLANNED_LORE.md ("her phone is on the
    # counter face-up"). Small black rectangle with a bright cyan
    # screen, set on the customer-facing edge so it reads as hers
    # rather than the clerk's.
    _make_box_local("KwikShop_KwikStop_SamPhone_Body",
                    (counter_x + counter_w / 2 - 0.45,
                     counter_y - counter_d / 2 + 0.18,
                     ground_z + counter_h + 0.01),
                    (0.08, 0.16, 0.012),
                    (0.10, 0.10, 0.12, 1.0))
    # Screen lit cyan-ish (active call / message screen)
    _make_box_local("KwikShop_KwikStop_SamPhone_Screen",
                    (counter_x + counter_w / 2 - 0.45,
                     counter_y - counter_d / 2 + 0.18,
                     ground_z + counter_h + 0.018),
                    (0.06, 0.14, 0.002),
                    (0.42, 0.68, 0.78, 1.0))

    # ── AISLE ENDCAPS · feature displays at the east + west
    # ends of each aisle (special promotions / impulse stacks)
    endcap_colours = [
        (0.95, 0.55, 0.20, 1.0),   # orange (chips)
        (0.32, 0.55, 0.25, 1.0),   # green (granola)
        (0.18, 0.32, 0.55, 1.0),   # blue (cereal)
        (0.85, 0.22, 0.20, 1.0),   # red (soup)
    ]
    aisle_y_positions = (cy - 1.5, cy + 1.0)
    for ka, ay in enumerate(aisle_y_positions):
        for kx, sgn in enumerate((-1, 1)):
            ec_x = kw_cx + sgn * (aisle_w / 2 + 0.4)
            # Endcap stack (3 layers of varying products)
            for layer in range(3):
                _make_box_local(
                    f"KwikShop_KwikStop_Endcap_{ka}_{sgn:+d}_{layer}",
                    (ec_x, ay, ground_z + 0.20 + layer * 0.45),
                    (0.45, 0.50, 0.40),
                    endcap_colours[(ka * 2 + kx) % 4])

    # ── RESTOCKING BOXES · stack of cardboard delivery boxes
    # near the NW corner of the bay (between the cooler and
    # the west partition)
    rs_x = kw_cx - bay_w / 2 + 0.6
    rs_y = cy + 1.5
    rs_z = ground_z
    # 4 cardboard boxes stacked
    box_specs = [(0, 0, 0, 0.60, 0.45, 0.40),
                  (0.08, 0.04, 0.40, 0.50, 0.40, 0.35),
                  (-0.04, -0.05, 0.75, 0.55, 0.45, 0.32),
                  (0.10, 0.08, 1.07, 0.40, 0.35, 0.30)]
    for k, (dx, dy, dz, sw, sd, sh) in enumerate(box_specs):
        _make_box_local(f"KwikShop_KwikStop_StockBox_{k}",
                        (rs_x + dx, rs_y + dy, rs_z + dz + sh / 2),
                        (sw, sd, sh),
                        (0.62, 0.50, 0.36, 1.0))
    # Tape strip on top box (small dark strip)
    _make_box_local("KwikShop_KwikStop_StockBoxTape",
                    (rs_x + 0.10, rs_y + 0.08,
                     rs_z + 1.07 + 0.30 + 0.005),
                    (0.20, 0.05, 0.01),
                    (0.32, 0.30, 0.28, 1.0))

    # ── "CAUTION WET FLOOR" yellow A-frame sign in the centre
    cau_x = kw_cx
    cau_y = cy - 0.5
    cau_z = mesh_z(cau_x, cau_y)
    # A-frame body (one face) — flat triangle approximated as a
    # tall thin tilted box
    _make_box_local("KwikShop_KwikStop_WetSign_A",
                    (cau_x, cau_y - 0.05,
                     ground_z + 0.40),
                    (0.50, 0.20, 0.80),
                    (0.95, 0.85, 0.30, 1.0))
    # Black text band suggestion
    _make_box_local("KwikShop_KwikStop_WetSign_Text",
                    (cau_x, cau_y - 0.16,
                     ground_z + 0.50),
                    (0.40, 0.04, 0.20),
                    (0.18, 0.18, 0.20, 1.0))

    # ── EMPLOYEES ONLY door on the back wall (between counter
    # backboard and the east wall). Just a flat box with an
    # "EMPLOYEES ONLY" plaque.
    emp_x = kw_cx + bay_w / 2 - 0.6
    emp_y = cy + depth / 2 - 0.15
    _make_box_local("KwikShop_KwikStop_EmpDoor",
                    (emp_x, emp_y, ground_z + 1.05),
                    (0.90, 0.06, 2.10),
                    (0.42, 0.32, 0.22, 1.0))
    _make_box_local("KwikShop_KwikStop_EmpDoorSign",
                    (emp_x, emp_y - 0.04, ground_z + 1.90),
                    (0.60, 0.02, 0.20),
                    (0.85, 0.20, 0.18, 1.0))

    # ── INTERIOR POSTERS taped to the partition walls (above
    # the products) — bright color blocks suggesting branded
    # ad posters
    poster_colors = [
        (0.32, 0.55, 0.78, 1.0),     # blue (Pepsi-style)
        (0.85, 0.22, 0.20, 1.0),     # red (Coke-style)
        (0.95, 0.55, 0.20, 1.0),     # orange
        (0.42, 0.62, 0.32, 1.0),     # green
    ]
    # 2 posters on the west partition interior face
    for k, py in enumerate((cy - 3.0, cy + 3.2)):
        _make_box_local(f"KwikShop_KwikStop_PosterW_{k}",
                        (kw_cx - bay_w / 2 + 0.13, py,
                         ground_z + 2.5),
                        (0.04, 0.80, 0.80),
                        poster_colors[k % 4])
    # 2 posters on the east partition interior face
    for k, py in enumerate((cy - 3.0, cy + 1.5)):
        _make_box_local(f"KwikShop_KwikStop_PosterE_{k}",
                        (kw_cx + bay_w / 2 - 0.13, py,
                         ground_z + 2.5),
                        (0.04, 0.80, 0.80),
                        poster_colors[(k + 2) % 4])
    # 1 poster on the back wall east of cooler (between cooler
    # east edge and counter west edge)
    _make_box_local("KwikShop_KwikStop_PosterB_1",
                    (kw_cx + 1.3, cy + depth / 2 - 0.13,
                     ground_z + 2.5),
                    (0.80, 0.04, 0.80),
                    poster_colors[0])

    # ── DOOR ENTRY BELL on the storefront door interior
    # (small chrome cylinder + clapper)
    glass_y_inside = cy - depth / 2 + 0.12
    door_centre_x = kw_cx
    _make_cyl_local("KwikShop_KwikStop_DoorBell",
                    (door_centre_x, glass_y_inside,
                     ground_z + 2.40),
                    0.04, 0.10, col_steel, segments=8)
    _make_box_local("KwikShop_KwikStop_DoorBellBracket",
                    (door_centre_x, glass_y_inside,
                     ground_z + 2.50),
                    (0.10, 0.04, 0.06),
                    (0.32, 0.32, 0.34, 1.0))

    # LAUNDROMAT bay — row of washing machines + dryers + folding
    # table. Two rows: 5 washers on the south side, 5 dryers on
    # the north side. Folding table down the middle. Bay moved
    # (2026-06-15) from +9 to LAUNDROMAT_OX (-5) so it sits in
    # the smaller 6m bay between Arcade and Kwik Stop.
    ldr_cx = cx + LAUNDROMAT_OX
    COL_WASHER_BODY = (0.92, 0.92, 0.90, 1.0)
    COL_WASHER_PORT = (0.32, 0.32, 0.36, 1.0)
    COL_WASHER_TRIM = (0.62, 0.62, 0.64, 1.0)
    COL_FOLDING = (0.62, 0.55, 0.45, 1.0)
    # 4 front-loaders along the back (north) wall — 1.4m spacing
    # so the row fits within the new 6m laundromat bay.
    for k in range(4):
        wx = ldr_cx - 2.1 + k * 1.4
        wy = cy + depth / 2 - 0.7      # washer back face clears wall
        _make_box_local(f"KwikShop_Ldr_Washer_{k}_Body",
                        (wx, wy, ground_z + 0.55),
                        (1.10, 0.70, 1.10), COL_WASHER_BODY)
        # Round porthole — approximated as a dark square
        _make_box_local(f"KwikShop_Ldr_Washer_{k}_Port",
                        (wx, wy - 0.36, ground_z + 0.65),
                        (0.42, 0.04, 0.42), COL_WASHER_PORT)
        # Trim panel above
        _make_box_local(f"KwikShop_Ldr_Washer_{k}_Trim",
                        (wx, wy - 0.36, ground_z + 1.02),
                        (0.95, 0.04, 0.18), COL_WASHER_TRIM)
    # 2 stacked dryers against the EAST partition (laundry has
    # less floor space in the new 6m bay)
    for k in range(2):
        wx = ldr_cx + BAY_W_LAUNDROMAT / 2 - 0.55
        wy = cy + depth * 0.15 - k * 0.9 + 0.4
        for stack in (0, 1):
            _make_box_local(f"KwikShop_Ldr_Dryer_{k}_{stack}_Body",
                            (wx, wy,
                             ground_z + 0.55 + stack * 1.10),
                            (0.90, 0.70, 1.10), COL_WASHER_BODY)
            _make_box_local(f"KwikShop_Ldr_Dryer_{k}_{stack}_Port",
                            (wx - 0.36, wy,
                             ground_z + 0.65 + stack * 1.10),
                            (0.04, 0.42, 0.42), COL_WASHER_PORT)
    # Folding table in the middle of the bay
    _make_box_local("KwikShop_Ldr_FoldingTable",
                    (ldr_cx, cy - 1.0, ground_z + 0.85),
                    (2.4, 0.75, 0.06), COL_FOLDING)
    for tx in (ldr_cx - 1.05, ldr_cx + 1.05):
        for ty in (cy - 1.35, cy - 0.65):
            _make_box_local(
                f"KwikShop_Ldr_FoldTableLeg_{int(tx*10)}_{int(ty*10)}",
                (tx, ty, ground_z + 0.42),
                (0.06, 0.06, 0.84), COL_WASHER_TRIM)
    # Coin/change machine on west partition
    _make_box_local("KwikShop_Ldr_ChangeMachine",
                    (ldr_cx - BAY_W_LAUNDROMAT / 2 + 0.40, cy + 0.5,
                     ground_z + 0.80),
                    (0.30, 0.40, 1.20),
                    (0.42, 0.42, 0.45, 1.0))
    # Community bulletin board on the east partition — paper
    # flyers in coloured rectangles.
    bb_x = ldr_cx + BAY_W_LAUNDROMAT / 2 - 0.06
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

    # ════════════════════════════════════════════════════════════════
    # KWIK STOP HERO-ASSET POLISH (2026-06-15 / hero pass)
    # The chapter-1 reference locale. Real Texas convenience stores
    # have a specific cluster of EXTERIOR fittings that signals
    # "store" before the player reads the sign. Each item below is
    # one of those fittings, sourced from real Gulf-Coast Kwik
    # references + the canon (Sam Miller's zine names Diego "leaning
    # against the ice freezer outside" — that freezer is below).
    # ════════════════════════════════════════════════════════════════

    # Storefront walk y matches build_commercial_cluster
    # walk_strip_y = ks_y - 6.5 (offset from BUILDING CENTER, not
    # from south wall). For depth=10 building, south wall is at
    # cy - 5; sidewalk at cy - 6.5 sits 1.5m south of the wall.
    sw_y = cy - 6.5
    sw_z_base = mesh_z(kw_cx, sw_y)

    # ── ICE FREEZER · west of the entry door · per Sam Miller's
    # zine, this is where Diego stands. Steel chest cooler with
    # sliding-glass top and "ICE" in red on the white upper band.
    ice_x = kw_cx - 4.4
    ice_y = sw_y + 0.85
    ice_z = mesh_z(ice_x, ice_y)
    COL_ICE_BODY = (0.62, 0.62, 0.64, 1.0)      # steel grey
    COL_ICE_TOP  = (0.95, 0.94, 0.90, 1.0)
    COL_ICE_GLASS = (0.65, 0.78, 0.88, 1.0)     # light blue-glass
    COL_ICE_RED  = (0.85, 0.18, 0.16, 1.0)
    # Lower body — chest height
    _make_box_local("KwikStop_IceFreezer_Body",
                    (ice_x, ice_y, ice_z + 0.45),
                    (1.20, 0.65, 0.90), COL_ICE_BODY)
    # Upper white band with "ICE" decal
    _make_box_local("KwikStop_IceFreezer_TopBand",
                    (ice_x, ice_y, ice_z + 1.00),
                    (1.20, 0.66, 0.18), COL_ICE_TOP)
    # Red ICE letter strip
    _make_box_local("KwikStop_IceFreezer_IceText",
                    (ice_x, ice_y - 0.33, ice_z + 1.00),
                    (0.42, 0.04, 0.12), COL_ICE_RED)
    # Sliding glass top
    _make_box_local("KwikStop_IceFreezer_GlassTop",
                    (ice_x, ice_y, ice_z + 1.13),
                    (1.16, 0.62, 0.04), COL_ICE_GLASS)
    # Side vent grille (east face)
    _make_box_local("KwikStop_IceFreezer_Vent",
                    (ice_x + 0.61, ice_y, ice_z + 0.40),
                    (0.04, 0.40, 0.30),
                    (0.28, 0.28, 0.30, 1.0))
    # Coin slot (west face)
    _make_box_local("KwikStop_IceFreezer_CoinSlot",
                    (ice_x - 0.61, ice_y + 0.10, ice_z + 0.95),
                    (0.04, 0.16, 0.16),
                    (0.18, 0.18, 0.20, 1.0))
    # Price sticker on the front
    _make_box_local("KwikStop_IceFreezer_Price",
                    (ice_x + 0.30, ice_y - 0.33, ice_z + 0.50),
                    (0.20, 0.04, 0.15),
                    (0.95, 0.85, 0.30, 1.0))   # yellow $2.49 sticker

    # ── PROPANE TANK CAGE · east of the ice freezer, between
    # storefront and parking. 6-tank cage with mesh sides.
    pro_x = kw_cx - 3.0
    pro_y = sw_y + 0.95
    pro_z = mesh_z(pro_x, pro_y)
    COL_PROPANE_CAGE = (0.32, 0.32, 0.34, 1.0)
    COL_PROPANE_TANK = (0.78, 0.74, 0.66, 1.0)
    # Cage frame (4 vertical posts + bottom + top rails)
    for sx, sy in ((-0.50, -0.30), (0.50, -0.30),
                   (-0.50,  0.30), (0.50,  0.30)):
        _make_box_local(
            f"KwikStop_Propane_Post_{int(sx*10):+d}_{int(sy*10):+d}",
            (pro_x + sx, pro_y + sy, pro_z + 0.60),
            (0.04, 0.04, 1.20), COL_PROPANE_CAGE)
    # Bottom & top rails
    for rz in (pro_z + 0.05, pro_z + 1.15):
        _make_box_local(f"KwikStop_Propane_Rail_{int(rz*100)}",
                        (pro_x, pro_y, rz),
                        (1.08, 0.68, 0.04), COL_PROPANE_CAGE)
    # Mesh suggestion (cross-bars)
    for kk in range(3):
        rz = pro_z + 0.30 + kk * 0.30
        _make_box_local(f"KwikStop_Propane_Mesh_{kk}",
                        (pro_x, pro_y + 0.32, rz),
                        (1.04, 0.02, 0.02), COL_PROPANE_CAGE)
    # 6 propane tanks in a 3x2 grid
    for tx in range(3):
        for ty in range(2):
            tk_x = pro_x - 0.36 + tx * 0.36
            tk_y = pro_y - 0.15 + ty * 0.30
            _make_cyl_local(
                f"KwikStop_Propane_Tank_{tx}_{ty}",
                (tk_x, tk_y, pro_z + 0.40),
                0.14, 0.65, COL_PROPANE_TANK, segments=6)
    # "PROPANE EXCHANGE" sign on top
    _make_box_local("KwikStop_Propane_Sign",
                    (pro_x, pro_y - 0.33, pro_z + 1.40),
                    (1.10, 0.04, 0.30),
                    (0.85, 0.18, 0.16, 1.0))

    # ── NEWSPAPER BOXES · three coin-op boxes side by side, east
    # of the entry door. Local paper, USA Today, Penny Saver.
    news_y = sw_y + 0.65
    news_z_base = mesh_z(kw_cx, news_y)
    for k, (col_body, tag) in enumerate([
        ((0.18, 0.32, 0.55, 1.0), "Beaumont"),    # Beaumont Enterprise blue
        ((0.85, 0.20, 0.18, 1.0), "USAToday"),
        ((0.42, 0.42, 0.45, 1.0), "PennySaver"),
    ]):
        nx = kw_cx + 2.0 + k * 0.50
        nz = mesh_z(nx, news_y)
        # Stand legs
        for sgn in (-1, 1):
            _make_box_local(
                f"KwikStop_NewsBox_{tag}_Leg_{sgn:+d}",
                (nx + sgn * 0.18, news_y, nz + 0.35),
                (0.04, 0.04, 0.70),
                (0.42, 0.42, 0.45, 1.0))
        # Body
        _make_box_local(f"KwikStop_NewsBox_{tag}_Body",
                        (nx, news_y, nz + 0.95),
                        (0.42, 0.36, 0.50), col_body)
        # Glass window (front)
        _make_box_local(f"KwikStop_NewsBox_{tag}_Window",
                        (nx, news_y - 0.19, nz + 1.00),
                        (0.30, 0.04, 0.30),
                        (0.78, 0.85, 0.92, 1.0))
        # Coin slot
        _make_box_local(f"KwikStop_NewsBox_{tag}_Slot",
                        (nx + 0.15, news_y - 0.19, nz + 0.80),
                        (0.06, 0.04, 0.06),
                        (0.18, 0.18, 0.20, 1.0))
        # Top header strip
        _make_box_local(f"KwikStop_NewsBox_{tag}_Header",
                        (nx, news_y, nz + 1.22),
                        (0.42, 0.36, 0.06),
                        (0.95, 0.92, 0.86, 1.0))

    # ── PAY PHONE · pole-mounted on the sidewalk west of the door
    pp_x = kw_cx - 2.0
    pp_y = sw_y - 0.10    # just south of sidewalk centerline
    pp_z = mesh_z(pp_x, pp_y)
    COL_PHONE_BODY = (0.18, 0.32, 0.55, 1.0)   # bell-system blue
    COL_PHONE_STEEL = (0.62, 0.62, 0.64, 1.0)
    # Pole
    _make_cyl_local("KwikStop_PayPhone_Pole",
                    (pp_x, pp_y, pp_z + 1.10),
                    0.05, 2.20, COL_PHONE_STEEL, segments=6)
    # Phone enclosure (3-sided hood)
    _make_box_local("KwikStop_PayPhone_Hood",
                    (pp_x, pp_y + 0.12, pp_z + 1.85),
                    (0.50, 0.32, 0.50), COL_PHONE_BODY)
    # Coin slot panel
    _make_box_local("KwikStop_PayPhone_Coinpanel",
                    (pp_x, pp_y - 0.05, pp_z + 1.65),
                    (0.36, 0.04, 0.50),
                    (0.42, 0.42, 0.45, 1.0))
    # Handset cradle
    _make_box_local("KwikStop_PayPhone_Cradle",
                    (pp_x - 0.20, pp_y - 0.07, pp_z + 1.40),
                    (0.06, 0.06, 0.20),
                    (0.18, 0.18, 0.20, 1.0))

    # ── COIN-OP AIR/WATER PUMP · east end of the building, on
    # the corner of the lot. Yellow-and-black "AIR/WATER 75¢" box.
    aw_x = kw_cx + bay_w / 2 + 1.5
    aw_y = sw_y - 1.0
    aw_z = mesh_z(aw_x, aw_y)
    # Pedestal box
    _make_box_local("KwikStop_AirWater_Body",
                    (aw_x, aw_y, aw_z + 0.55),
                    (0.45, 0.45, 1.10),
                    (0.95, 0.85, 0.30, 1.0))   # safety yellow
    # Black header band
    _make_box_local("KwikStop_AirWater_Header",
                    (aw_x, aw_y, aw_z + 1.05),
                    (0.45, 0.45, 0.18),
                    (0.18, 0.18, 0.20, 1.0))
    # Air hose coiled
    _make_cyl_local("KwikStop_AirWater_HoseCoil",
                    (aw_x + 0.25, aw_y, aw_z + 0.85),
                    0.10, 0.08,
                    (0.20, 0.20, 0.22, 1.0), segments=8)
    # Brass valve / pressure gauge cluster
    _make_box_local("KwikStop_AirWater_Valve",
                    (aw_x, aw_y - 0.22, aw_z + 0.75),
                    (0.10, 0.06, 0.18),
                    (0.78, 0.62, 0.32, 1.0))

    # ── SANDWICH BOARD A-FRAME SIGN on the sidewalk in front of
    # the door · "OPEN 24 HRS · LOTTO · ICE"
    sb_x = kw_cx + 0.6
    sb_y = sw_y - 0.85
    sb_z = mesh_z(sb_x, sb_y)
    COL_SB_WOOD = (0.62, 0.42, 0.28, 1.0)
    COL_SB_FACE = (0.95, 0.85, 0.30, 1.0)
    # Two A-frame panels (slight V angle suggested by parallel boxes
    # offset slightly)
    for sgn in (-1, 1):
        _make_box_local(f"KwikStop_SandwichBoard_Panel_{sgn:+d}",
                        (sb_x, sb_y + sgn * 0.08, sb_z + 0.40),
                        (0.60, 0.04, 0.78), COL_SB_FACE)
        # Wood frame around the panel
        _make_box_local(f"KwikStop_SandwichBoard_FrameT_{sgn:+d}",
                        (sb_x, sb_y + sgn * 0.08, sb_z + 0.80),
                        (0.66, 0.05, 0.04), COL_SB_WOOD)
        _make_box_local(f"KwikStop_SandwichBoard_FrameB_{sgn:+d}",
                        (sb_x, sb_y + sgn * 0.08, sb_z + 0.02),
                        (0.66, 0.05, 0.04), COL_SB_WOOD)
    # Hinge at top
    _make_box_local("KwikStop_SandwichBoard_Hinge",
                    (sb_x, sb_y, sb_z + 0.82),
                    (0.06, 0.06, 0.04),
                    (0.62, 0.62, 0.64, 1.0))

    # ── CIGARETTE BUTT URN by the door (small dark cylinder with
    # sand top — every real Kwik Stop has one)
    urn_x = kw_cx + 1.2
    urn_y = sw_y - 0.50
    urn_z = mesh_z(urn_x, urn_y)
    _make_cyl_local("KwikStop_CigUrn_Body",
                    (urn_x, urn_y, urn_z + 0.45),
                    0.16, 0.90,
                    (0.32, 0.28, 0.26, 1.0), segments=6)
    # Sand top
    _make_cyl_local("KwikStop_CigUrn_Sand",
                    (urn_x, urn_y, urn_z + 0.91),
                    0.16, 0.02,
                    (0.85, 0.78, 0.62, 1.0), segments=6)

    # ── ROOF FIXTURES on the parapet/roof line · satellite dish
    # for the security DVR + antenna + small alarm bell box.
    roof_z = ground_z + height + 0.30
    # Satellite dish (small white disc)
    _make_cyl_local("KwikStop_RoofSat_Mount",
                    (kw_cx + bay_w / 2 - 1.2,
                     cy + depth * 0.20,
                     roof_z + 0.30),
                    0.04, 0.60,
                    (0.42, 0.42, 0.45, 1.0), segments=4)
    _make_cyl_local("KwikStop_RoofSat_Dish",
                    (kw_cx + bay_w / 2 - 1.2,
                     cy + depth * 0.20 + 0.15,
                     roof_z + 0.55),
                    0.18, 0.05,
                    (0.95, 0.94, 0.90, 1.0), segments=10)
    # Antenna mast on the west end of the parapet
    _make_cyl_local("KwikStop_RoofAntenna_Mast",
                    (kw_cx - bay_w / 2 + 0.4,
                     cy + depth * 0.30,
                     roof_z + 1.50),
                    0.03, 3.00,
                    (0.18, 0.18, 0.20, 1.0), segments=4)
    # 3 antenna crossbars (decreasing in size, top to bottom)
    for k, cb_w in enumerate((0.50, 0.70, 0.90)):
        _make_box_local(
            f"KwikStop_RoofAntenna_Crossbar_{k}",
            (kw_cx - bay_w / 2 + 0.4,
             cy + depth * 0.30,
             roof_z + 2.5 - k * 0.40),
            (cb_w, 0.03, 0.03),
            (0.18, 0.18, 0.20, 1.0))
    # Alarm bell box on south parapet edge
    _make_box_local("KwikStop_RoofAlarmBell",
                    (kw_cx + bay_w / 2 - 0.5,
                     cy - depth / 2 - 0.05,
                     roof_z + 0.10),
                    (0.30, 0.10, 0.30),
                    (0.85, 0.20, 0.18, 1.0))

    # ── WINDOW STICKERS · the dense cluster of cling decals every
    # real US convenience store accumulates: WE CARD age check,
    # credit-card logos, hours decal, Coke Coca-Cola corporate
    # cling. All inside the south-facing storefront glass.
    glass_y = cy - depth / 2 + 0.06
    # "WE CARD" red square at adult eye height, west of the door
    _make_box_local("KwikStop_WeCardDecal",
                    (kw_cx - 3.0, glass_y, ground_z + 1.85),
                    (0.30, 0.02, 0.30),
                    (0.85, 0.20, 0.18, 1.0))
    _make_box_local("KwikStop_WeCardDecal_Text",
                    (kw_cx - 3.0, glass_y - 0.005, ground_z + 1.85),
                    (0.24, 0.01, 0.18),
                    (0.95, 0.94, 0.90, 1.0))
    # Credit-card logos row (4 small rectangles)
    cc_colors = [
        (0.18, 0.32, 0.55, 1.0),  # Visa blue
        (0.85, 0.20, 0.18, 1.0),  # MasterCard red
        (0.32, 0.55, 0.78, 1.0),  # AmEx blue
        (0.95, 0.85, 0.30, 1.0),  # Discover orange
    ]
    for k, col_cc in enumerate(cc_colors):
        _make_box_local(f"KwikStop_CCLogo_{k}",
                        (kw_cx + 1.6 + k * 0.18, glass_y,
                         ground_z + 1.78),
                        (0.14, 0.02, 0.10), col_cc)
    # Hours decal on the door (24/7 small white sticker)
    _make_box_local("KwikStop_HoursDecal",
                    (kw_cx + 0.2, glass_y, ground_z + 2.10),
                    (0.16, 0.02, 0.16),
                    (0.95, 0.95, 0.92, 1.0))
    _make_box_local("KwikStop_HoursDecal_Number",
                    (kw_cx + 0.2, glass_y - 0.005, ground_z + 2.10),
                    (0.12, 0.01, 0.10),
                    (0.85, 0.20, 0.18, 1.0))
    # COCA-COLA corporate door cling (red oval-shaped strip)
    _make_box_local("KwikStop_CokeCling",
                    (kw_cx - 0.6, glass_y, ground_z + 1.40),
                    (0.40, 0.02, 0.18),
                    (0.85, 0.20, 0.18, 1.0))

    # ── TASTE HOME HAMBURGER WINDOW DECAL · canonical Vol 6 Ch 1
    # opening detail ("a cheerful cartoon hamburger holding a sign
    # that reads TASTE HOME. The hamburger has lost one of its
    # eyes. The eye is somewhere in the decal's adhesive layer,
    # drifting"). Brown burger circle + cream sign + ONE eye on
    # the right (the other is missing).
    th_x = kw_cx - 1.6
    th_y = glass_y
    th_z = ground_z + 1.15
    # Burger body (brown circle)
    _make_cyl_local("KwikStop_TasteHome_Burger",
                    (th_x, th_y, th_z),
                    0.18, 0.02,
                    (0.55, 0.32, 0.22, 1.0), segments=10)
    # Burger top bun lighter shade (smaller circle on top)
    _make_cyl_local("KwikStop_TasteHome_BurgerBun",
                    (th_x, th_y - 0.005, th_z + 0.06),
                    0.14, 0.005,
                    (0.78, 0.55, 0.32, 1.0), segments=8)
    # Single remaining eye (right side only)
    _make_box_local("KwikStop_TasteHome_Eye",
                    (th_x + 0.05, th_y - 0.01, th_z + 0.05),
                    (0.03, 0.005, 0.03),
                    (0.18, 0.18, 0.20, 1.0))
    # "TASTE HOME" sign rectangle
    _make_box_local("KwikStop_TasteHome_Sign",
                    (th_x + 0.18, th_y, th_z - 0.05),
                    (0.30, 0.02, 0.12),
                    (0.95, 0.94, 0.86, 1.0))
    _make_box_local("KwikStop_TasteHome_SignText",
                    (th_x + 0.18, th_y - 0.005, th_z - 0.05),
                    (0.24, 0.01, 0.06),
                    (0.55, 0.22, 0.18, 1.0))

    # ── SLUSHIE MACHINE · 3-flavor frosty barrel beside the
    # roller grill. Each barrel a translucent dome with brightly
    # coloured slush visible inside.
    sl_x = counter_x + counter_w / 2 - 0.40
    sl_y = counter_y + counter_d / 2 + 0.50
    sl_z = ground_z + counter_h + 0.10
    # Base unit (white box with chrome trim)
    _make_box_local("KwikStop_Slushie_Base",
                    (sl_x, sl_y, sl_z + 0.15),
                    (0.85, 0.55, 0.30),
                    (0.95, 0.94, 0.90, 1.0))
    # Chrome top band
    _make_box_local("KwikStop_Slushie_TopBand",
                    (sl_x, sl_y, sl_z + 0.32),
                    (0.85, 0.55, 0.04),
                    (0.62, 0.62, 0.64, 1.0))
    # 3 slush barrels (translucent cylinders with coloured slush)
    barrel_palette = [
        (0.85, 0.20, 0.18, 1.0),    # cherry red
        (0.32, 0.55, 0.78, 1.0),    # blue raspberry
        (0.95, 0.85, 0.30, 1.0),    # citrus yellow
    ]
    for k, col_bar in enumerate(barrel_palette):
        slx = sl_x - 0.28 + k * 0.28
        # Translucent barrel (low-poly cylinder)
        _make_cyl_local(
            f"KwikStop_Slushie_Barrel_{k}",
            (slx, sl_y, sl_z + 0.60),
            0.13, 0.50,
            col_bar, segments=8)
        # Top spinner cap (white)
        _make_cyl_local(
            f"KwikStop_Slushie_Cap_{k}",
            (slx, sl_y, sl_z + 0.88),
            0.13, 0.05,
            (0.95, 0.94, 0.90, 1.0), segments=8)
        # Dispenser handle / spout below (chrome)
        _make_box_local(
            f"KwikStop_Slushie_Spout_{k}",
            (slx, sl_y - 0.20, sl_z + 0.40),
            (0.08, 0.10, 0.16),
            (0.62, 0.62, 0.64, 1.0))

    # ── COFFEE STATION · 2-burner drip coffee maker on the back
    # counter, with two glass pots (one regular, one decaf)
    cof_x = counter_x - counter_w / 2 + 0.80
    cof_y = counter_y + counter_d / 2 + 0.50
    cof_z = ground_z + counter_h + 0.10
    # Base unit (black coffee maker housing)
    _make_box_local("KwikStop_CoffeeMaker_Body",
                    (cof_x, cof_y, cof_z + 0.20),
                    (0.55, 0.40, 0.40),
                    (0.20, 0.20, 0.22, 1.0))
    # Warming-plate / control panel
    _make_box_local("KwikStop_CoffeeMaker_Plate",
                    (cof_x, cof_y, cof_z + 0.42),
                    (0.55, 0.40, 0.04),
                    (0.42, 0.42, 0.45, 1.0))
    # Two glass pots (slightly amber from coffee)
    for k, col_pot in enumerate([
        (0.42, 0.22, 0.16, 1.0),   # regular (full)
        (0.85, 0.65, 0.42, 1.0),   # decaf (lighter)
    ]):
        cpx = cof_x - 0.14 + k * 0.28
        # Pot body (glass-amber cylinder)
        _make_cyl_local(
            f"KwikStop_CoffeePot_{k}",
            (cpx, cof_y, cof_z + 0.30),
            0.075, 0.18,
            col_pot, segments=6)
        # Handle (chrome)
        _make_box_local(
            f"KwikStop_CoffeePot_Handle_{k}",
            (cpx + 0.10, cof_y, cof_z + 0.30),
            (0.04, 0.04, 0.16),
            (0.42, 0.42, 0.45, 1.0))
        # Pot lid
        _make_cyl_local(
            f"KwikStop_CoffeePot_Lid_{k}",
            (cpx, cof_y, cof_z + 0.42),
            0.075, 0.02,
            (0.20, 0.20, 0.22, 1.0), segments=6)
    # Coffee cup stack beside the maker (cream paper cups)
    for k in range(3):
        _make_cyl_local(
            f"KwikStop_CoffeeCupStack_{k}",
            (cof_x - 0.40, cof_y, cof_z + 0.20 + k * 0.04),
            0.045, 0.10,
            (0.95, 0.92, 0.86, 1.0), segments=6)
    # Sugar / creamer caddy
    _make_box_local("KwikStop_CoffeeStation_Caddy",
                    (cof_x + 0.35, cof_y, cof_z + 0.16),
                    (0.16, 0.20, 0.18),
                    (0.62, 0.62, 0.64, 1.0))

    # ── ROLLER GRILL · the classic stainless-steel hot-dog roller
    # at the back of the counter. 4 parallel chrome rollers under
    # a heat lamp.
    rg_x = counter_x - counter_w / 2 + 0.30
    rg_y = counter_y + counter_d / 2 + 0.50
    rg_z = ground_z + counter_h + 0.10
    # Base box
    _make_box_local("KwikStop_RollerGrill_Base",
                    (rg_x, rg_y, rg_z + 0.10),
                    (0.65, 0.45, 0.20),
                    (0.62, 0.62, 0.64, 1.0))
    # 4 chrome rollers across
    for k in range(4):
        rgrx = rg_x - 0.22 + k * 0.15
        _make_cyl_local(
            f"KwikStop_RollerGrill_Roller_{k}",
            (rgrx, rg_y, rg_z + 0.22),
            0.045, 0.40,
            (0.85, 0.85, 0.85, 1.0), segments=6)
    # Heat-lamp hood above
    _make_box_local("KwikStop_RollerGrill_Hood",
                    (rg_x, rg_y, rg_z + 0.40),
                    (0.65, 0.45, 0.06),
                    (0.92, 0.55, 0.20, 1.0))
    # Two visible hot dogs on the rollers
    for k in range(2):
        hdx = rg_x - 0.10 + k * 0.20
        _make_cyl_local(
            f"KwikStop_RollerGrill_HotDog_{k}",
            (hdx, rg_y, rg_z + 0.25),
            0.025, 0.18,
            (0.78, 0.42, 0.28, 1.0), segments=6)

    # ── HELP WANTED sign in the west bay window · paper-yellow
    # rectangle with hand-lettered red text suggested
    _make_box_local("KwikStop_HelpWanted",
                    (kw_cx + 2.2, glass_y, ground_z + 1.45),
                    (0.30, 0.02, 0.40),
                    (0.95, 0.85, 0.50, 1.0))
    # Black border to suggest hand-frame
    _make_box_local("KwikStop_HelpWanted_Border",
                    (kw_cx + 2.2, glass_y - 0.005, ground_z + 1.45),
                    (0.32, 0.01, 0.42),
                    (0.32, 0.22, 0.18, 1.0))

    # ── DEDICATED KWIK STOP LIGHT POLE · 7m sodium-vapor lot
    # light at the SW corner of the parking lot (illuminates the
    # forecourt at night). Skinny black pole + double-shoebox head.
    lp_x = kw_cx - bay_w / 2 - 4.0
    lp_y = cy - depth / 2 - 22.0     # south end of lot
    lp_z = mesh_z(lp_x, lp_y)
    _make_cyl_local("KwikStop_LotLamp_Pole",
                    (lp_x, lp_y, lp_z + 3.5),
                    0.08, 7.0,
                    (0.18, 0.18, 0.20, 1.0), segments=6)
    # Crossarm
    _make_box_local("KwikStop_LotLamp_Arm",
                    (lp_x + 0.6, lp_y, lp_z + 6.9),
                    (1.20, 0.06, 0.06),
                    (0.18, 0.18, 0.20, 1.0))
    # Twin shoebox heads (one on each side)
    for sgn in (-1, 1):
        _make_box_local(f"KwikStop_LotLamp_Head_{sgn:+d}",
                        (lp_x + sgn * 0.50, lp_y, lp_z + 6.85),
                        (0.45, 0.30, 0.18),
                        (0.42, 0.42, 0.45, 1.0))
        # Glow plate underneath
        _make_box_local(f"KwikStop_LotLamp_Glow_{sgn:+d}",
                        (lp_x + sgn * 0.50, lp_y, lp_z + 6.72),
                        (0.40, 0.26, 0.02),
                        (0.95, 0.92, 0.62, 1.0))

    # ── WET FLOOR SIGN inside the store (yellow A-frame caution
    # sign), placed mid-aisle near the entry
    wf_x = kw_cx - 0.5
    wf_y = cy - depth / 2 + 1.5     # 1.5m inside the door
    # Two yellow panels in A-frame configuration
    for sgn in (-1, 1):
        _make_box_local(f"KwikStop_WetFloor_Panel_{sgn:+d}",
                        (wf_x, wf_y + sgn * 0.10, ground_z + 0.40),
                        (0.30, 0.04, 0.55),
                        (0.95, 0.85, 0.30, 1.0))
    # Black hinge at top
    _make_box_local("KwikStop_WetFloor_Hinge",
                    (wf_x, wf_y, ground_z + 0.70),
                    (0.06, 0.06, 0.04),
                    (0.18, 0.18, 0.20, 1.0))

    # ── BIKE RACK · 2-loop chrome rack at the west edge of the
    # sidewalk with a single bike chained to it
    br_x = kw_cx - 4.8
    br_y = sw_y - 0.70
    br_z = mesh_z(br_x, br_y)
    COL_BIKE_RACK = (0.62, 0.62, 0.64, 1.0)
    # 2 inverted-U loops + connecting bar
    for sgn in (-1, 1):
        # Upright
        _make_cyl_local(
            f"KwikStop_BikeRack_Up_{sgn:+d}",
            (br_x + sgn * 0.30, br_y, br_z + 0.40),
            0.025, 0.80, COL_BIKE_RACK, segments=6)
    # Top bar
    _make_box_local("KwikStop_BikeRack_Bar",
                    (br_x, br_y, br_z + 0.78),
                    (0.65, 0.04, 0.04), COL_BIKE_RACK)
    # The single bike — sketched: 2 wheel circles + frame triangle
    bike_x = br_x + 0.10
    COL_BIKE_FRAME = (0.85, 0.20, 0.18, 1.0)   # red bike frame
    COL_BIKE_TIRE = (0.18, 0.18, 0.20, 1.0)
    # Two wheels (low-poly cylinders)
    for sgn in (-1, 1):
        _make_cyl_local(
            f"KwikStop_BikeWheel_{sgn:+d}",
            (bike_x + sgn * 0.36, br_y - 0.18, br_z + 0.30),
            0.30, 0.04, COL_BIKE_TIRE, segments=10)
    # Frame top tube
    _make_box_local("KwikStop_BikeFrame_Top",
                    (bike_x, br_y - 0.18, br_z + 0.55),
                    (0.65, 0.04, 0.04), COL_BIKE_FRAME)
    # Seat tube
    _make_box_local("KwikStop_BikeFrame_Seat",
                    (bike_x + 0.10, br_y - 0.18, br_z + 0.45),
                    (0.03, 0.04, 0.30), COL_BIKE_FRAME)
    # Handlebars
    _make_box_local("KwikStop_BikeHandlebars",
                    (bike_x - 0.38, br_y - 0.18, br_z + 0.70),
                    (0.04, 0.30, 0.04), COL_BIKE_FRAME)
    # Seat
    _make_box_local("KwikStop_BikeSeat",
                    (bike_x + 0.12, br_y - 0.18, br_z + 0.65),
                    (0.18, 0.06, 0.04),
                    (0.20, 0.20, 0.22, 1.0))


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

    # ════════════════════════════════════════════════════════════════
    # MAYA DAIGLE CANON DETAILS (2026-06-15 hero pass)
    # Cosmic Comics is Maya's domain on weekends + after school.
    # The following are the canon objects from her character file:
    # ════════════════════════════════════════════════════════════════

    # ── "DO NOT SORT YET" PILE · stack of unsorted comics on the
    # floor between the two shelves. Maya's literal job ("sorting
    # the DO NOT SORT YET pile with the patient indifference of a
    # sixteen-year-old who has been given the kind of task adults
    # use to keep teenagers busy"). 4 stacked piles, each a
    # multi-color column.
    pile_x = cx - 1.0
    pile_y = cy + 0.5
    pile_palette = [
        (0.85, 0.20, 0.18, 1.0),   # red Marvel
        (0.18, 0.32, 0.55, 1.0),   # blue DC
        (0.95, 0.85, 0.30, 1.0),   # yellow indie
        (0.32, 0.55, 0.25, 1.0),   # green sci-fi
        (0.62, 0.22, 0.78, 1.0),   # purple horror
        (0.95, 0.55, 0.20, 1.0),   # orange humor
    ]
    for k_pile, col_p in enumerate(pile_palette):
        # Stack of 8 comics per pile
        for j in range(8):
            _make_box_local(
                f"{name_prefix}_DoNotSortYet_{k_pile}_{j}",
                (pile_x + (k_pile % 2) * 0.30,
                 pile_y + (k_pile // 2) * 0.30,
                 ground_z + 0.08 + j * 0.012),
                (0.25, 0.34, 0.012), col_p)

    # ── "THE FUND" JAR · small glass jar on the back counter
    # labeled with hand-lettered "THE FUND" sign (no explanation,
    # per canon: "Maya labels THE FUND without ever explaining what
    # the fund is for"). Contains visible dollar bills.
    jar_x = cx + width / 2 - 1.4 + 0.50   # on east counter
    jar_y = cy - depth / 2 + 1.5
    jar_z_top = ground_z + 1.10           # on counter top
    # Jar body (translucent cylinder)
    _make_cyl_local(f"{name_prefix}_FundJar_Body",
                    (jar_x, jar_y, jar_z_top + 0.10),
                    0.06, 0.20,
                    (0.85, 0.90, 0.92, 1.0), segments=8)
    # Cash visible inside (cream rectangles stacked)
    for k_cash in range(3):
        _make_box_local(f"{name_prefix}_FundJar_Cash_{k_cash}",
                        (jar_x, jar_y, jar_z_top + 0.08 + k_cash * 0.012),
                        (0.08, 0.04, 0.008),
                        (0.55, 0.62, 0.42, 1.0))
    # Hand-lettered label
    _make_box_local(f"{name_prefix}_FundJar_Label",
                    (jar_x, jar_y - 0.06, jar_z_top + 0.10),
                    (0.10, 0.005, 0.08),
                    (0.95, 0.92, 0.86, 1.0))

    # ── MINI-ZINE DISPLAY RACK · cardboard countertop rack with
    # 4 slots, each holding a small zine. Canon: "Each issue is a
    # single observational piece — sold for one dollar each at
    # the back counter."
    zr_x = cx + width / 2 - 1.4 - 0.40
    zr_y = cy - depth / 2 + 1.5
    zr_z_top = ground_z + 1.10
    # Cardboard base
    _make_box_local(f"{name_prefix}_ZineRack_Base",
                    (zr_x, zr_y, zr_z_top + 0.04),
                    (0.40, 0.32, 0.04),
                    (0.78, 0.62, 0.42, 1.0))
    # 4 zine covers stacked at slight forward angle
    zine_palette = [
        (0.95, 0.94, 0.86, 1.0),   # cream cover #6 "WIDOW AT LOT 14"
        (0.32, 0.55, 0.78, 1.0),   # blue cover #11 "BACK COOLER"
        (0.85, 0.65, 0.42, 1.0),   # tan cover #15 "GRANDMOTHER"
        (0.42, 0.30, 0.20, 1.0),   # dark cover #19 "PHANTOM"
    ]
    for k_z, col_z in enumerate(zine_palette):
        zx_off = -0.12 + k_z * 0.08
        _make_box_local(f"{name_prefix}_ZineRack_Issue_{k_z}",
                        (zr_x + zx_off, zr_y - 0.10, zr_z_top + 0.10),
                        (0.07, 0.005, 0.10), col_z)
    # "$1 · NEWS FROM HARMONY CREEK" hand-lettered card
    _make_box_local(f"{name_prefix}_ZineRack_PriceCard",
                    (zr_x, zr_y - 0.13, zr_z_top + 0.04),
                    (0.40, 0.005, 0.06),
                    (0.95, 0.92, 0.86, 1.0))

    # ── F.T. LETTER on the counter · a partially-visible envelope
    # addressed to "Maya" (small detail from canon: "F.T. has been
    # writing to her for nine months. She has not told anyone").
    # Cream envelope + a stripe of red wax suggested
    letter_x = cx + width / 2 - 1.4 + 0.20
    letter_y = cy - depth / 2 + 1.5 - 0.18
    _make_box_local(f"{name_prefix}_FTLetter_Body",
                    (letter_x, letter_y, ground_z + 1.11),
                    (0.18, 0.13, 0.005),
                    (0.95, 0.92, 0.86, 1.0))
    # Red wax seal dot (right edge of envelope)
    _make_box_local(f"{name_prefix}_FTLetter_WaxSeal",
                    (letter_x + 0.08, letter_y, ground_z + 1.114),
                    (0.022, 0.022, 0.003),
                    (0.55, 0.18, 0.16, 1.0))
    # Postmark stripe (top-right corner)
    _make_box_local(f"{name_prefix}_FTLetter_Stamp",
                    (letter_x + 0.07, letter_y + 0.05, ground_z + 1.113),
                    (0.035, 0.04, 0.002),
                    (0.62, 0.22, 0.20, 1.0))

    # ── BULLETIN BOARD on the west wall · zine community flyers,
    # show announcements, missing-pet posters
    bb_x = cx - width / 2 + 0.12
    bb_y = cy - 1.0
    bb_z = ground_z + 1.80
    _make_box_local(f"{name_prefix}_Bulletin_Frame",
                    (bb_x, bb_y, bb_z),
                    (0.05, 1.60, 1.20),
                    (0.42, 0.30, 0.20, 1.0))
    # Cork backing
    _make_box_local(f"{name_prefix}_Bulletin_Cork",
                    (bb_x + 0.03, bb_y, bb_z),
                    (0.02, 1.50, 1.10),
                    (0.78, 0.55, 0.32, 1.0))
    # 6 flyers (cycling palette so the board reads as a real
    # community noticeboard)
    flyer_palette = [
        (0.95, 0.85, 0.30, 1.0),   # yellow show flyer
        (0.85, 0.20, 0.18, 1.0),   # red zine call-for-submissions
        (0.32, 0.55, 0.78, 1.0),   # blue band poster
        (0.62, 0.22, 0.78, 1.0),   # purple "missing cat"
        (0.95, 0.94, 0.90, 1.0),   # cream
        (0.42, 0.62, 0.32, 1.0),   # green community garden
    ]
    for k_f, col_f in enumerate(flyer_palette):
        fy = bb_y - 0.50 + (k_f % 3) * 0.50
        fz = bb_z + 0.35 - (k_f // 3) * 0.50
        _make_box_local(f"{name_prefix}_Bulletin_Flyer_{k_f}",
                        (bb_x + 0.04, fy, fz),
                        (0.005, 0.32, 0.32), col_f)


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

    # ── CAR WASH BUILDING at the rear of NexCorp Gas & Go ──────
    # Canon: "It also, notably, has a car wash in the rear — the
    # kind of car wash with the full automated tunnel" (Vol 6 Ch 1,
    # the 15:11 transaction scene). Long tunnel building running
    # E-W behind the store + entry sign at the north entrance.
    cw_cx = nc_x + 8.0          # east of the store
    cw_cy = nc_y + 10.0         # north of the store
    cw_w, cw_d, cw_h = 16.0, 6.5, 4.0
    cw_z = nc_z
    COL_CW_WALL = (0.82, 0.80, 0.76, 1.0)
    COL_CW_ROOF = (0.32, 0.42, 0.55, 1.0)   # blue NexCorp roof
    COL_CW_TRIM = (0.32, 0.55, 0.78, 1.0)   # NexCorp blue
    COL_CW_DOOR = (0.42, 0.42, 0.45, 1.0)
    # Walls (N, S solid; tunnel openings on E and W)
    _make_box_local("NexCorpGG_CarWash_WallN",
                    (cw_cx, cw_cy + cw_d / 2 - 0.10, cw_z + cw_h / 2),
                    (cw_w, 0.20, cw_h), COL_CW_WALL)
    _make_box_local("NexCorpGG_CarWash_WallS",
                    (cw_cx, cw_cy - cw_d / 2 + 0.10, cw_z + cw_h / 2),
                    (cw_w, 0.20, cw_h), COL_CW_WALL)
    # End walls partial (tunnel openings 3.6m wide x 3.0m tall)
    open_w = 3.6
    open_h = 3.0
    side_w_remain = (cw_d - open_w) / 2
    for sgn_x, tag in ((-1, "W"), (1, "E")):
        wx = cw_cx + sgn_x * (cw_w / 2 - 0.10)
        # Bottom corners (split around tunnel opening)
        for sgn_y in (-1, 1):
            _make_box_local(
                f"NexCorpGG_CarWash_Wall{tag}_Side_{sgn_y:+d}",
                (wx, cw_cy + sgn_y * (cw_d / 2 - side_w_remain / 2),
                 cw_z + cw_h / 2),
                (0.20, side_w_remain, cw_h), COL_CW_WALL)
        # Top lintel above the opening
        _make_box_local(
            f"NexCorpGG_CarWash_Wall{tag}_Lintel",
            (wx, cw_cy, cw_z + open_h + (cw_h - open_h) / 2),
            (0.20, open_w, cw_h - open_h), COL_CW_WALL)
    # Roof
    _make_box_local("NexCorpGG_CarWash_Roof",
                    (cw_cx, cw_cy, cw_z + cw_h + 0.10),
                    (cw_w + 0.4, cw_d + 0.4, 0.20), COL_CW_ROOF)
    # NexCorp blue trim band at top of walls
    for sgn_y, tag_y in ((-1, "S"), (1, "N")):
        _make_box_local(
            f"NexCorpGG_CarWash_TrimBand_{tag_y}",
            (cw_cx, cw_cy + sgn_y * (cw_d / 2 - 0.05),
             cw_z + cw_h - 0.30),
            (cw_w + 0.4, 0.10, 0.45), COL_CW_TRIM)
    # Entry sign at the WEST opening · "AUTOMATIC CAR WASH $5"
    _make_box_local("NexCorpGG_CarWash_EntrySign",
                    (cw_cx - cw_w / 2 - 0.30, cw_cy, cw_z + cw_h + 0.65),
                    (0.20, 2.40, 0.80), COL_CW_TRIM)
    # Sign text strip (white)
    _make_box_local("NexCorpGG_CarWash_EntrySignText",
                    (cw_cx - cw_w / 2 - 0.32, cw_cy, cw_z + cw_h + 0.65),
                    (0.06, 2.20, 0.40),
                    (0.95, 0.94, 0.90, 1.0))
    # Arrow into the wash on the west wall (yellow arrow)
    _make_box_local("NexCorpGG_CarWash_EntryArrow",
                    (cw_cx - cw_w / 2 + 0.5, cw_cy, cw_z + 1.5),
                    (0.50, 0.04, 0.30),
                    (0.95, 0.85, 0.30, 1.0))
    # Visible interior · rotating brush silhouette suggested by
    # 2 vertical cylinders in the tunnel
    for k, ix in enumerate((-3.5, 3.5)):
        _make_cyl_local(f"NexCorpGG_CarWash_Brush_{k}",
                        (cw_cx + ix, cw_cy, cw_z + cw_h / 2),
                        0.42, cw_h - 0.5,
                        (0.55, 0.32, 0.78, 1.0), segments=8)
    # Concrete drainage pad in front of the WEST entry (curb to
    # catch runoff)
    _make_box_local("NexCorpGG_CarWash_DrainPad",
                    (cw_cx - cw_w / 2 - 2.0, cw_cy, cw_z + 0.04),
                    (3.6, cw_d + 0.6, 0.08),
                    (0.72, 0.70, 0.66, 1.0))
    # Yellow line painted on drain pad (DO NOT ENTER FROM EAST)
    _make_box_local("NexCorpGG_CarWash_DrainLineYellow",
                    (cw_cx - cw_w / 2 - 0.8, cw_cy, cw_z + 0.06),
                    (0.10, cw_d, 0.01),
                    (0.95, 0.85, 0.30, 1.0))

    # ── ADDITIONAL FUEL ISLANDS · canon says NexCorp Gas & Go has
    # 8 PUMPS (4 islands x 2 sides). Original had 2 islands.
    # Adding 2 more islands further south of the canopy.
    for k_extra, ix_extra in enumerate((-2.6, 2.6)):
        ec_x = can_cx + ix_extra
        ec_y = can_cy - can_d - 1.5    # 1.5m south of existing canopy
        # Island pad
        _make_box_local(f"NexCorpGG_PumpPadExtra_{k_extra}",
                        (ec_x, ec_y, nc_z + PAD_H / 2),
                        (1.8, 4.0, PAD_H),
                        (0.72, 0.70, 0.66, 1.0))
        # Pump body
        _make_box_local(f"NexCorpGG_PumpBodyExtra_{k_extra}",
                        (ec_x, ec_y,
                         nc_z + PAD_H + PUMP_H / 2),
                        (0.80, 0.40, PUMP_H),
                        COL_PUMP_BODY)
        # Pump display
        _make_box_local(f"NexCorpGG_PumpDisplayExtra_{k_extra}",
                        (ec_x, ec_y,
                         nc_z + PAD_H + PUMP_H + DISPLAY_H / 2),
                        (0.70, 0.42, DISPLAY_H),
                        (0.20, 0.22, 0.28, 1.0))
        for sgn in (-1, 1):
            _make_cyl_local(
                f"NexCorpGG_PumpHoseExtra_{k_extra}_{sgn:+d}",
                (ec_x, ec_y + sgn * 0.22,
                 nc_z + PAD_H + PUMP_H * 0.55),
                0.04, 0.30, COL_PUMP_HOSE, segments=4)

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
    # Skin-tone palette for character diversity
    SKIN_LIGHT  = (0.92, 0.78, 0.62, 1.0)   # light/peach
    SKIN_MED    = (0.78, 0.58, 0.42, 1.0)   # medium/tan
    SKIN_DARK   = (0.55, 0.38, 0.28, 1.0)   # dark brown
    SKIN_OLIVE  = (0.82, 0.68, 0.48, 1.0)   # olive

    chapter_one_cast = [
        # (name, x, y, scale, hair, jacket, pants, pose, skin, beard)
        ("Skip",     nc_x + 4.0, nc_y + 4.3, 1.0, "cap",
            (0.32, 0.55, 0.78, 1.0), (0.42, 0.42, 0.45, 1.0),
            "hands_on_counter", SKIN_LIGHT, "stubble"),
        ("ArcadeAtt", ks_x - 11.0, ks_y + 4.3, 1.0, "bowl",
            (0.62, 0.22, 0.78, 1.0), (0.20, 0.20, 0.22, 1.0),
            "arms_crossed", SKIN_OLIVE, "none"),
        # Sam — Diego is Hispanic-American per canon (Ramos
        # family), Sam paired with him. Olive tone reads close.
        ("Sam",      ks_x + 1.0, ks_y - 2.25, 1.0, "ponytail",
            (0.42, 0.30, 0.22, 1.0), (0.55, 0.50, 0.42, 1.0),
            "hands_on_counter", SKIN_LIGHT, "none"),
        # Diego Ramos — canon Hispanic-American 19yo drummer
        ("Diego",    ks_x + 1.8, ks_y - 5.0, 1.0, "beanie",
            (0.18, 0.14, 0.12, 1.0), (0.20, 0.20, 0.24, 1.0),
            "one_arm_lean", SKIN_MED, "stubble"),
        # Roy — mid-50s white regular
        ("Roy",      ks_x + 0.5, ks_y + 3.0, 1.05, "cap",
            (0.42, 0.42, 0.45, 1.0), (0.78, 0.74, 0.66, 1.0),
            "hands_pockets", SKIN_LIGHT, "goatee"),
        ("LaundryAtt", ks_x - 5.0, ks_y + 0.5, 1.0, "bowl",
            (0.32, 0.55, 0.78, 1.0), (0.92, 0.92, 0.90, 1.0),
            "hands_on_counter", SKIN_MED, "none"),
        # Diner cook — classic Greek-American short-order, full
        # mustache.
        ("DinerCook", dn_x,        dn_y + 3.4, 1.0, "short",
            (0.98, 0.98, 0.96, 1.0), (0.18, 0.18, 0.22, 1.0),
            "hands_on_counter", SKIN_OLIVE, "full"),
        ("DinerWaiter", dn_x + 4.0, dn_y + 2.5, 1.0, "short",
            (0.85, 0.22, 0.20, 1.0), (0.92, 0.90, 0.84, 1.0),
            "arms_out", SKIN_LIGHT, "none"),
        # Comics shopkeeper Rick · 62yo collector with a full beard
        ("ComicsClerk", cc_x + 3.1, cc_y - 1.3, 1.0, "bowl",
            (0.92, 0.92, 0.86, 1.0), (0.32, 0.18, 0.32, 1.0),
            "arms_crossed", SKIN_LIGHT, "full"),
        # Maya Daigle — 16yo, canon "purple-tipped dark hair"
        ("Maya",     cc_x + 3.0, cc_y + 2.5, 0.92, "bowl",
            (0.40, 0.18, 0.42, 1.0), (0.20, 0.20, 0.24, 1.0),
            "hands_on_counter", SKIN_LIGHT, "none"),
    ]
    for tag, fx, fy, sc, hair, jacket, pants, pose, skin, beard in chapter_one_cast:
        fz = mesh_z(fx, fy)
        human_figure(
            name=f"NPC_{tag}",
            base_x=fx, base_y=fy, base_z=fz,
            scale=sc,
            facing='-Y',                  # face SOUTH (toward player)
            skin_color=skin,
            hair_style=hair,
            hair_color=(0.20, 0.14, 0.10, 1.0),
            jacket_color=jacket,
            pants_color=pants,
            shoe_color=(0.20, 0.16, 0.14, 1.0),
            has_sunglasses=False,
            with_ears=True,
            with_mouth=True,
            mouth_color=(0.55, 0.22, 0.28, 1.0),
            beard=beard,
            pose=pose,
        )

    # ── CUSTOMERS · a few patrons scattered around the block so
    # it reads as ALIVE, not staffed-but-empty. Each faces the
    # action they're engaged with (arcade kid faces cabinet,
    # diner patron faces counter, etc.)
    customers = [
        # (name, x, y, facing, scale, hair, jacket, pants, pose)
        # Arcade kid at the leftmost cabinet. Arcade bay now at
        # cx + ARCADE_OX = ks_x - 11. Cabinets at arc_cx + k*2 - 2.
        # Leftmost cab at arc_cx - 2.0 = ks_x - 13.
        ("ArcadeKid",  ks_x - 13.0, ks_y + 3.0, '+Y', 0.78, "bowl",
            (0.42, 0.65, 0.32, 1.0), (0.32, 0.18, 0.32, 1.0),
            "standing"),
        # Diner patron at a stool.
        ("DinerPatron", dn_x - 2.0, dn_y + 0.6, '+Y', 1.0, "cap",
            (0.62, 0.42, 0.78, 1.0), (0.18, 0.22, 0.30, 1.0),
            "hands_on_counter"),
        # Cosmic Comics browser between the two shelves.
        ("ComicsBrowser", cc_x - 1.5, cc_y + 0.5, '+Y', 0.92, "short",
            (0.95, 0.55, 0.20, 1.0), (0.42, 0.30, 0.20, 1.0),
            "arms_crossed"),
        # Sidewalk pedestrian heading east. Hands in pockets.
        ("Pedestrian", 12.0, walk_strip_y, '+X', 1.0, "beanie",
            (0.32, 0.55, 0.78, 1.0), (0.42, 0.42, 0.45, 1.0),
            "hands_pockets"),
        # Kwik Stop customer at counter paying. Counter is at
        # SW corner now (counter center at kw_cx-5, counter_y).
        # Customer south of counter facing north toward Sam.
        ("KwikStopCust1", ks_x + 1.0, ks_y - 4.3, '+Y', 1.0,
            "ponytail", (0.85, 0.22, 0.20, 1.0), (0.18, 0.18, 0.20, 1.0),
            "hands_on_counter"),
        # Kwik Stop customer browsing the snack aisle (south).
        # South aisle at (kw_cx=ks_x+6, ks_y - 1.0).
        ("KwikStopCust2", ks_x + 4.0, ks_y - 1.8, '+Y', 0.95,
            "short", (0.42, 0.62, 0.32, 1.0), (0.55, 0.32, 0.22, 1.0),
            "arms_crossed"),
        # Kwik Stop customer at the back cooler (north end of bay)
        ("KwikStopCust3", ks_x + 8.0, ks_y + 3.5, '+Y', 1.0,
            "cap", (0.95, 0.85, 0.30, 1.0), (0.32, 0.18, 0.32, 1.0),
            "standing"),
    ]
    for tag, fx, fy, facing, sc, hair, jacket, pants, pose in customers:
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
            pose=pose,
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
    # Moved 2026-06-15: user reported drive-in "too cramped and
    # close to the road". Old cy=-300 put the screen at y=-380,
    # only 12m north of the chapter-1 frontage road at y=-392,
    # AND the screen sat 20m outside the DriveInPad's south edge
    # (pad y range -340..-235). New cy=-270 keeps the entire
    # drive-in installation (screen + 4 parking rows) inside the
    # carved pad and 42m clear of the road.
    cx, cy = 150.0, -270.0
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


def build_dambrosios_holdover():
    """D'Ambrosio's Holdover — chapter-1 era smaller version of
    the canonical riverfront bar. Per lore/_HCE_PROJECT_NOTES.md
    referenced as a chapter-1 location needing an interior on
    the exterior map. Single-story dark wood building with a
    pitched roof and a cursive sign in the D'Ambrosio's red.

    Sits west of the chapter-1 commercial cluster at (-150,
    -360) within the South Commercial belt.
    """
    cx, cy = -150.0, -360.0
    ground_z = mesh_z(cx, cy)
    col_wall = (0.42, 0.30, 0.20, 1.0)         # dark wood
    col_trim = (0.62, 0.42, 0.28, 1.0)          # lighter wood
    col_roof = (0.32, 0.22, 0.18, 1.0)
    col_door = (0.62, 0.18, 0.16, 1.0)
    col_window = (0.95, 0.85, 0.45, 1.0)        # warm-lit window glow
    col_sign = (0.85, 0.20, 0.18, 1.0)
    w, d, h = 14.0, 12.0, 4.2
    t = 0.20
    _make_box_local("DA_Slab",
                    (cx, cy, ground_z + 0.05),
                    (w + 0.4, d + 0.4, 0.10), col_trim)
    # Walls (solid all four sides, just window cutouts via
    # decorative window panels)
    _make_box_local("DA_WallN",
                    (cx, cy + d / 2 - t / 2, ground_z + h / 2),
                    (w, t, h), col_wall)
    _make_box_local("DA_WallE",
                    (cx + w / 2 - t / 2, cy, ground_z + h / 2),
                    (t, d, h), col_wall)
    _make_box_local("DA_WallW",
                    (cx - w / 2 + t / 2, cy, ground_z + h / 2),
                    (t, d, h), col_wall)
    # South wall with central door + flanking windows
    dw, dh = 1.6, 2.6
    left_w = w / 2 - dw / 2
    _make_box_local("DA_WallS_L",
                    (cx - dw / 2 - left_w / 2,
                     cy - d / 2 + t / 2, ground_z + h / 2),
                    (left_w, t, h), col_wall)
    _make_box_local("DA_WallS_R",
                    (cx + dw / 2 + left_w / 2,
                     cy - d / 2 + t / 2, ground_z + h / 2),
                    (left_w, t, h), col_wall)
    _make_box_local("DA_WallS_Header",
                    (cx, cy - d / 2 + t / 2,
                     ground_z + dh + (h - dh) / 2),
                    (dw, t, h - dh), col_wall)
    _make_box_local("DA_Door",
                    (cx, cy - d / 2 + 0.05, ground_z + dh / 2),
                    (dw, 0.06, dh - 0.10), col_door)
    # Two warm-lit windows on the south face flanking the door
    for sgn in (-1, 1):
        _make_box_local(f"DA_Window_{sgn:+d}",
                        (cx + sgn * 3.5, cy - d / 2 + 0.04,
                         ground_z + 2.0),
                        (1.8, 0.04, 1.4), col_window)
    # Pitched gable roof
    ridge_h = 2.0
    rverts = [
        (cx - w / 2 - 0.30, cy - d / 2 - 0.30, ground_z + h),
        (cx + w / 2 + 0.30, cy - d / 2 - 0.30, ground_z + h),
        (cx + w / 2 + 0.30, cy + d / 2 + 0.30, ground_z + h),
        (cx - w / 2 - 0.30, cy + d / 2 + 0.30, ground_z + h),
        (cx, cy - d / 2 - 0.30, ground_z + h + ridge_h),
        (cx, cy + d / 2 + 0.30, ground_z + h + ridge_h),
    ]
    rfaces = [[0, 1, 5, 4], [3, 4, 5, 2],
              [0, 4, 3], [1, 2, 5]]
    _finalize_mesh("DA_Roof", rverts, rfaces, col_roof)
    # Hanging sign on a wrought-iron bracket south of the door
    _make_box_local("DA_SignBracket",
                    (cx, cy - d / 2 - 0.7,
                     ground_z + h - 0.6),
                    (0.06, 1.0, 0.08),
                    (0.18, 0.18, 0.18, 1.0))
    _make_box_local("DA_SignPanel",
                    (cx, cy - d / 2 - 1.0,
                     ground_z + h - 1.4),
                    (2.4, 0.10, 1.2), col_sign)
    # Small front patio (cobblestone-style)
    _make_box_local("DA_Patio",
                    (cx, cy - d / 2 - 1.5,
                     ground_z + 0.05),
                    (8.0, 2.0, 0.10),
                    (0.55, 0.50, 0.45, 1.0))
    # 2 outdoor café tables
    for sgn in (-1, 1):
        tx = cx + sgn * 3.0
        ty = cy - d / 2 - 1.5
        tz = mesh_z(tx, ty)
        _make_cyl_local(f"DA_PatioTable_{sgn:+d}",
                        (tx, ty, tz + 0.75),
                        0.40, 0.06, col_trim, segments=8)
        _make_cyl_local(f"DA_PatioTableStem_{sgn:+d}",
                        (tx, ty, tz + 0.40),
                        0.06, 0.70, col_trim, segments=6)


def build_church_lot_and_school_playground():
    """Church parking lot west of the church + a small fenced
    playground area south of the elementary school.
    """
    # Church parking lot at (-50, 140) — west of the church
    # (church at (-30, 140))
    _build_parking_lot("Church", -55.0, 140.0,
                        lot_w=20.0, lot_d=16.0,
                        ground_z=mesh_z(-55.0, 140.0),
                        building_y_north=140.0,
                        car_palette=[
                            (0.85, 0.20, 0.18, 1.0),
                            (0.62, 0.62, 0.64, 1.0),
                            (0.18, 0.32, 0.55, 1.0),
                            (0.32, 0.55, 0.25, 1.0),
                            (0.78, 0.74, 0.66, 1.0),
                        ],
                        n_handicap=1)

    # ── ELEMENTARY SCHOOL PLAYGROUND south of the school at
    # (-90, 145). School is at (-90, 160).
    pg_cx, pg_cy = -90.0, 142.0
    pg_z = mesh_z(pg_cx, pg_cy)
    col_grass = (0.30, 0.55, 0.25, 1.0)
    col_rubber = (0.42, 0.32, 0.22, 1.0)
    col_red = (0.85, 0.20, 0.18, 1.0)
    col_blue = (0.18, 0.32, 0.55, 1.0)
    col_yellow = (0.95, 0.85, 0.30, 1.0)
    col_steel = (0.62, 0.62, 0.64, 1.0)
    # Rubber play surface
    _make_box_local("ES_Playground_Surface",
                    (pg_cx, pg_cy, pg_z + 0.04),
                    (20.0, 10.0, 0.08), col_rubber)
    # Chain-link fence corner posts
    for sgn_x in (-1, 1):
        for sgn_y in (-1, 1):
            fx = pg_cx + sgn_x * 10.2
            fy = pg_cy + sgn_y * 5.2
            fz = mesh_z(fx, fy)
            _make_cyl_local(
                f"ES_PG_FencePost_{sgn_x:+d}_{sgn_y:+d}",
                (fx, fy, fz + 1.0),
                0.05, 2.0, col_steel, segments=4)
    # Climbing structure (cube with poles)
    cs_x = pg_cx - 5.0
    cs_y = pg_cy
    for sgn_x in (-1, 1):
        for sgn_y in (-1, 1):
            _make_cyl_local(
                f"ES_PG_ClimberPost_{sgn_x:+d}_{sgn_y:+d}",
                (cs_x + sgn_x * 1.5, cs_y + sgn_y * 1.5,
                 pg_z + 1.2),
                0.10, 2.4, col_red, segments=4)
    # Top platform
    _make_box_local("ES_PG_ClimberTop",
                    (cs_x, cs_y, pg_z + 2.30),
                    (3.2, 3.2, 0.10), col_yellow)
    # Slide off the east side
    _make_box_local("ES_PG_Slide",
                    (cs_x + 2.5, cs_y, pg_z + 1.2),
                    (2.5, 0.7, 0.06), col_blue)
    # Monkey bars frame east of the climber
    mb_x = pg_cx + 4.0
    mb_y = pg_cy
    for sgn in (-1, 1):
        _make_cyl_local(f"ES_PG_MonkeyPost_{sgn:+d}",
                        (mb_x + sgn * 2.0, mb_y, pg_z + 1.2),
                        0.08, 2.4, col_steel, segments=4)
    _make_box_local("ES_PG_MonkeyTop",
                    (mb_x, mb_y, pg_z + 2.4),
                    (4.0, 0.10, 0.10), col_steel)
    # 3 swinging bars hanging under
    for k, x_off in enumerate((-1.2, 0, 1.2)):
        _make_cyl_local(f"ES_PG_MonkeyRung_{k}",
                        (mb_x + x_off, mb_y, pg_z + 2.3),
                        0.04, 0.30, col_steel, segments=4)
    # Sand pit south of climber
    _make_box_local("ES_PG_SandPit",
                    (pg_cx, pg_cy - 3.0, pg_z + 0.06),
                    (6.0, 3.0, 0.10),
                    (0.90, 0.82, 0.62, 1.0))


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


def build_police_station():
    """Harmony Creek PD — civic block east of the fire station
    on Horizon Drive. Two-story navy-blue brick building with
    flag pole + small parking lot.
    """
    cx, cy = -170.0, -60.0
    ground_z = mesh_z(cx, cy)
    col_wall = (0.18, 0.22, 0.42, 1.0)        # police navy
    col_trim = (0.85, 0.82, 0.74, 1.0)
    col_roof = (0.32, 0.30, 0.28, 1.0)
    col_door = (0.32, 0.32, 0.34, 1.0)
    col_badge_gold = (0.78, 0.62, 0.32, 1.0)
    w, d, h = 22.0, 14.0, 7.0
    t = 0.20
    _make_box_local("PD_Slab",
                    (cx, cy, ground_z + 0.05),
                    (w + 0.4, d + 0.4, 0.10), col_trim)
    _make_box_local("PD_WallN",
                    (cx, cy + d / 2 - t / 2, ground_z + h / 2),
                    (w, t, h), col_wall)
    _make_box_local("PD_WallE",
                    (cx + w / 2 - t / 2, cy, ground_z + h / 2),
                    (t, d, h), col_wall)
    _make_box_local("PD_WallW",
                    (cx - w / 2 + t / 2, cy, ground_z + h / 2),
                    (t, d, h), col_wall)
    # South wall split for entry
    dw, dh = 2.5, 3.0
    left_w = w / 2 - dw / 2
    _make_box_local("PD_WallS_L",
                    (cx - dw / 2 - left_w / 2,
                     cy - d / 2 + t / 2, ground_z + h / 2),
                    (left_w, t, h), col_wall)
    _make_box_local("PD_WallS_R",
                    (cx + dw / 2 + left_w / 2,
                     cy - d / 2 + t / 2, ground_z + h / 2),
                    (left_w, t, h), col_wall)
    _make_box_local("PD_WallS_Header",
                    (cx, cy - d / 2 + t / 2,
                     ground_z + dh + (h - dh) / 2),
                    (dw, t, h - dh), col_wall)
    _make_box_local("PD_Door",
                    (cx, cy - d / 2 + 0.05, ground_z + dh / 2),
                    (dw, 0.06, dh - 0.10), col_door)
    # 2 stories of windows on south face
    for story in range(2):
        z_win = ground_z + 2.0 + story * 3.0
        for sgn in (-1, 1):
            for k in range(2):
                wx = cx + sgn * (dw / 2 + (k + 1) * 3.5)
                if abs(wx - cx) < w / 2 - 1.0:
                    _make_box_local(f"PD_Window_{story}_{sgn:+d}_{k}",
                                    (wx, cy - d / 2 + 0.04, z_win),
                                    (1.6, 0.04, 1.4),
                                    (0.32, 0.42, 0.55, 1.0))
    _make_box_local("PD_Roof",
                    (cx, cy, ground_z + h + 0.10),
                    (w + 0.4, d + 0.4, 0.20), col_roof)
    # Gold POLICE BADGE on the south facade above the door
    _make_box_local("PD_Badge",
                    (cx, cy - d / 2 - 0.20,
                     ground_z + h - 0.8),
                    (1.4, 0.14, 1.4), col_badge_gold)
    # Flag pole flanking the entry
    fp_x = cx + 7.0
    fp_y = cy - d / 2 - 4.0
    fp_z = mesh_z(fp_x, fp_y)
    _make_cyl_local("PD_FlagPole",
                    (fp_x, fp_y, fp_z + 4.0),
                    0.08, 8.0, col_trim, segments=6)
    _make_box_local("PD_FlagBanner",
                    (fp_x + 0.40, fp_y, fp_z + 6.8),
                    (0.80, 0.02, 0.60),
                    (0.85, 0.20, 0.18, 1.0))
    # Small parking lot south with 2 police cruisers (black + white)
    _build_parking_lot("PoliceStation", cx, cy - 18.0,
                        lot_w=18.0, lot_d=20.0,
                        ground_z=mesh_z(cx, cy - 18.0),
                        building_y_north=cy,
                        car_palette=[(0.20, 0.20, 0.22, 1.0),
                                      (0.92, 0.92, 0.90, 1.0),
                                      (0.20, 0.20, 0.22, 1.0),
                                      (0.92, 0.92, 0.90, 1.0)],
                        n_handicap=1)


def build_phase3_crane():
    """Abandoned construction crane left standing at the
    failed Phase III development. A tall lattice tower with a
    horizontal jib + counter-jib, rusted brown.
    """
    cx, cy = -420.0, -250.0
    ground_z = mesh_z(cx, cy)
    col_rust = (0.55, 0.32, 0.18, 1.0)
    col_cab = (0.85, 0.78, 0.22, 1.0)

    # Tower lattice — 30 m tall single box (approximation)
    tower_h = 30.0
    _make_box_local("P3_Crane_Tower",
                    (cx, cy, ground_z + tower_h / 2),
                    (1.4, 1.4, tower_h), col_rust)
    # Tower base flare (broader at the bottom)
    _make_box_local("P3_Crane_Base",
                    (cx, cy, ground_z + 1.0),
                    (3.0, 3.0, 2.0), col_rust)
    # Operator cab at the top
    _make_box_local("P3_Crane_Cab",
                    (cx, cy, ground_z + tower_h + 0.5),
                    (2.2, 2.2, 1.6), col_cab)
    # Horizontal jib (the long arm)
    jib_l = 24.0
    _make_box_local("P3_Crane_Jib",
                    (cx + jib_l / 2 - 1.0,
                     cy, ground_z + tower_h + 1.6),
                    (jib_l, 0.80, 0.80), col_rust)
    # Counter-jib (shorter arm on the opposite side)
    cjib_l = 8.0
    _make_box_local("P3_Crane_CounterJib",
                    (cx - cjib_l / 2 - 0.5,
                     cy, ground_z + tower_h + 1.6),
                    (cjib_l, 0.80, 0.80), col_rust)
    # Counterweight block at the back end
    _make_box_local("P3_Crane_Counterweight",
                    (cx - cjib_l - 0.5,
                     cy, ground_z + tower_h + 1.0),
                    (1.2, 1.6, 1.6),
                    (0.32, 0.30, 0.28, 1.0))
    # Hook hanging from the jib at half-length
    hook_x = cx + jib_l / 2 - 1.0
    hook_y = cy
    _build_oriented_handle("P3_Crane_HookCable",
                            (hook_x, hook_y, ground_z + tower_h + 1.6),
                            (hook_x, hook_y, ground_z + 12.0),
                            radius=0.04, color=(0.08, 0.08, 0.08, 1.0))
    _make_box_local("P3_Crane_Hook",
                    (hook_x, hook_y, ground_z + 11.5),
                    (0.50, 0.30, 0.80),
                    (0.42, 0.42, 0.45, 1.0))


def build_dumpsters():
    """Trash dumpsters in alley positions behind several
    commercial buildings — chapter-1 back-alley atmosphere.
    """
    COL_DUMP_GREEN = (0.30, 0.45, 0.25, 1.0)
    COL_DUMP_BROWN = (0.42, 0.30, 0.20, 1.0)
    COL_DUMP_LID = (0.20, 0.20, 0.22, 1.0)

    def _dumpster(name, x, y, color):
        z = mesh_z(x, y)
        # Body
        _make_box_local(f"{name}_Body",
                        (x, y, z + 0.65),
                        (2.0, 1.4, 1.30), color)
        # Slanted lid (approximated by a flat box tilted via z offset)
        _make_box_local(f"{name}_Lid",
                        (x, y + 0.10, z + 1.35),
                        (2.0, 1.5, 0.08), COL_DUMP_LID)

    # Behind the Kwik Shop strip
    _dumpster("Dump_KS_Arcade", -15 - 9.0, -360 + 6.0, COL_DUMP_GREEN)
    _dumpster("Dump_KS_Kwik",    -15,       -360 + 6.0, COL_DUMP_BROWN)
    _dumpster("Dump_KS_Laundro", -15 + 9.0, -360 + 6.0, COL_DUMP_GREEN)
    # Behind NexCorp Gas & Go
    _dumpster("Dump_NC", -60, -360 + 6.0, COL_DUMP_GREEN)
    # Behind the Diner
    _dumpster("Dump_Diner", 35, -360 + 5.5, COL_DUMP_BROWN)
    # Behind Cosmic Comics
    _dumpster("Dump_Cosmic", 70, -360 + 5.0, COL_DUMP_GREEN)
    # Behind D'Ambrosio's Holdover
    _dumpster("Dump_DA", -150, -360 + 7.0, COL_DUMP_BROWN)
    # Behind Halsey Studios
    _dumpster("Dump_HS", 480, -100 + 8.0, COL_DUMP_BROWN)
    # Behind the diner / library / dept store
    _dumpster("Dump_Lib", 60, 80 + 8.0, COL_DUMP_GREEN)
    _dumpster("Dump_DB", 480, 60 + 14.0, COL_DUMP_GREEN)
    _dumpster("Dump_FF", 480, -90 + 6.0, COL_DUMP_BROWN)


def build_horizon_plaza():
    """Small 3-bay neighborhood strip plaza on the north side
    of Horizon Drive between the elementary school and OT Park.
    Each bay has its own storefront + sign + lot stall.
    """
    cx, cy = -100.0, 30.0
    ground_z = mesh_z(cx, cy)
    total_w = 36.0   # 3 bays × 12 m
    d, h = 10.0, 4.0
    t = 0.20
    col_wall = (0.85, 0.82, 0.74, 1.0)
    col_roof = (0.32, 0.30, 0.28, 1.0)
    col_glass_frame = (0.62, 0.62, 0.64, 1.0)
    col_trim = (0.62, 0.42, 0.28, 1.0)
    bay_palettes = [
        # (bay tag, sign colour, door colour)
        ("PizzaPlace",  (0.85, 0.20, 0.18, 1.0), (0.32, 0.18, 0.16, 1.0)),
        ("DryClean",    (0.18, 0.32, 0.55, 1.0), (0.18, 0.32, 0.55, 1.0)),
        ("Salon",       (0.95, 0.45, 0.62, 1.0), (0.55, 0.30, 0.42, 1.0)),
    ]
    # Slab + back wall + side walls + roof (one continuous shell)
    _make_box_local("HzPlaza_Slab",
                    (cx, cy, ground_z + 0.05),
                    (total_w + 0.4, d + 0.4, 0.10), col_trim)
    _make_box_local("HzPlaza_WallN",
                    (cx, cy + d / 2 - t / 2, ground_z + h / 2),
                    (total_w, t, h), col_wall)
    _make_box_local("HzPlaza_WallE",
                    (cx + total_w / 2 - t / 2, cy,
                     ground_z + h / 2),
                    (t, d, h), col_wall)
    _make_box_local("HzPlaza_WallW",
                    (cx - total_w / 2 + t / 2, cy,
                     ground_z + h / 2),
                    (t, d, h), col_wall)
    _make_box_local("HzPlaza_Roof",
                    (cx, cy, ground_z + h + 0.10),
                    (total_w + 0.4, d + 0.4, 0.20), col_roof)
    # Per-bay storefront on the south face
    bay_w = total_w / 3
    for k, (bay_tag, col_sign, col_door) in enumerate(bay_palettes):
        bcx = cx - total_w / 2 + (k + 0.5) * bay_w
        glass_y = cy - d / 2 + 0.05
        # Plate glass mullions
        for m in range(4):
            mx = bcx - bay_w / 2 + 0.3 + m * (bay_w - 0.6) / 3
            _make_box_local(f"HzPlaza_{bay_tag}_Mul_{m}",
                            (mx, glass_y, ground_z + h / 2),
                            (0.10, 0.06, h), col_glass_frame)
        _make_box_local(f"HzPlaza_{bay_tag}_TopRail",
                        (bcx, glass_y, ground_z + h - 0.08),
                        (bay_w - 0.2, 0.08, 0.16), col_glass_frame)
        _make_box_local(f"HzPlaza_{bay_tag}_BotRail",
                        (bcx, glass_y, ground_z + 0.20),
                        (bay_w - 0.2, 0.08, 0.40), col_glass_frame)
        # Door (centred in bay)
        dw, dh = 1.2, 2.4
        _make_box_local(f"HzPlaza_{bay_tag}_Door",
                        (bcx, glass_y, ground_z + dh / 2),
                        (dw, 0.06, dh - 0.10), col_door)
        # Sign panel above the bay
        _make_box_local(f"HzPlaza_{bay_tag}_SignPanel",
                        (bcx, cy - d / 2 - 0.30,
                         ground_z + h + 0.30),
                        (bay_w * 0.75, 0.14, 0.80), col_sign)
        # Welcome mat
        _make_box_local(f"HzPlaza_{bay_tag}_Mat",
                        (bcx, glass_y - 0.40, ground_z + 0.07),
                        (dw + 0.20, 0.80, 0.02),
                        (0.32, 0.22, 0.18, 1.0))

    # Parking lot south of the plaza
    _build_parking_lot("HzPlaza", cx, cy - 18.0,
                        lot_w=32.0, lot_d=18.0,
                        ground_z=mesh_z(cx, cy - 18.0),
                        building_y_north=cy,
                        car_palette=[
                            (0.85, 0.20, 0.18, 1.0),
                            (0.62, 0.62, 0.64, 1.0),
                            (0.18, 0.32, 0.55, 1.0),
                            (0.32, 0.55, 0.25, 1.0),
                            (0.20, 0.20, 0.22, 1.0),
                            (0.95, 0.85, 0.30, 1.0),
                        ],
                        n_handicap=1)


def build_midway_minimart():
    """A small mini-mart + single gas pump on the south side of
    Horizon Drive midway between the West Estates link and the
    big central Harmony/Horizon junction. Gives long-distance
    drivers a quick stop.
    """
    cx, cy = -260.0, -50.0
    ground_z = mesh_z(cx, cy)
    col_wall = (0.85, 0.82, 0.74, 1.0)
    col_trim = (0.32, 0.55, 0.78, 1.0)
    col_roof = (0.32, 0.30, 0.28, 1.0)
    col_door = (0.32, 0.55, 0.78, 1.0)
    col_glass = (0.42, 0.50, 0.58, 0.6)
    col_pump = (0.95, 0.94, 0.90, 1.0)
    w, d, h = 10.0, 8.0, 3.6
    t = 0.20
    _make_box_local("MM_Slab",
                    (cx, cy, ground_z + 0.05),
                    (w + 0.4, d + 0.4, 0.10),
                    (0.78, 0.74, 0.66, 1.0))
    _make_box_local("MM_WallN",
                    (cx, cy + d / 2 - t / 2, ground_z + h / 2),
                    (w, t, h), col_wall)
    _make_box_local("MM_WallE",
                    (cx + w / 2 - t / 2, cy, ground_z + h / 2),
                    (t, d, h), col_wall)
    _make_box_local("MM_WallW",
                    (cx - w / 2 + t / 2, cy, ground_z + h / 2),
                    (t, d, h), col_wall)
    # South wall — plate glass storefront with central door
    glass_y = cy - d / 2 + 0.05
    n_mul = 4
    for k in range(n_mul):
        mx = cx - w / 2 + 0.3 + k * (w - 0.6) / (n_mul - 1)
        _make_box_local(f"MM_GlassMul_{k}",
                        (mx, glass_y, ground_z + h / 2),
                        (0.10, 0.06, h), col_trim)
    _make_box_local("MM_GlassTop",
                    (cx, glass_y, ground_z + h - 0.08),
                    (w - 0.2, 0.08, 0.16), col_trim)
    _make_box_local("MM_GlassBot",
                    (cx, glass_y, ground_z + 0.20),
                    (w - 0.2, 0.08, 0.40), col_trim)
    # Door
    dw, dh = 1.0, 2.2
    for sgn in (-1, 1):
        _make_box_local(f"MM_DoorJamb_{sgn:+d}",
                        (cx + sgn * dw / 2, glass_y,
                         ground_z + dh / 2),
                        (0.10, 0.08, dh), col_trim)
    _make_box_local("MM_DoorHeader",
                    (cx, glass_y, ground_z + dh + 0.08),
                    (dw + 0.10, 0.08, 0.16), col_trim)
    _make_box_local("MM_Door",
                    (cx, glass_y, ground_z + dh / 2),
                    (dw - 0.10, 0.06, dh - 0.10), col_door)
    # Welcome mat
    _make_box_local("MM_Mat",
                    (cx, glass_y - 0.40, ground_z + 0.07),
                    (dw + 0.20, 0.80, 0.02),
                    (0.32, 0.22, 0.18, 1.0))
    # Roof
    _make_box_local("MM_Roof",
                    (cx, cy, ground_z + h + 0.10),
                    (w + 0.4, d + 0.4, 0.20), col_roof)
    # Big sign panel on the roof south side
    _make_box_local("MM_SignPanel",
                    (cx, cy - d / 2 - 0.30,
                     ground_z + h + 0.80),
                    (w * 0.75, 0.14, 0.80), col_trim)

    # ── Single fuel pump under a small canopy west of the
    # building
    pmp_x = cx - w / 2 - 7.0
    pmp_y = cy
    pmp_z = mesh_z(pmp_x, pmp_y)
    # 4 small canopy columns
    can_w, can_d, can_h = 6.0, 6.0, 4.0
    for sgn_x in (-1, 1):
        for sgn_y in (-1, 1):
            _make_cyl_local(
                f"MM_CanopyCol_{sgn_x:+d}_{sgn_y:+d}",
                (pmp_x + sgn_x * (can_w / 2 - 0.3),
                 pmp_y + sgn_y * (can_d / 2 - 0.3),
                 pmp_z + can_h / 2),
                0.15, can_h, col_trim, segments=6)
    _make_box_local("MM_CanopyRoof",
                    (pmp_x, pmp_y, pmp_z + can_h + 0.10),
                    (can_w + 0.4, can_d + 0.4, 0.20), col_trim)
    # The pump itself
    _make_box_local("MM_PumpPad",
                    (pmp_x, pmp_y, pmp_z + 0.10),
                    (1.6, 1.6, 0.20),
                    (0.72, 0.70, 0.66, 1.0))
    _make_box_local("MM_PumpBody",
                    (pmp_x, pmp_y, pmp_z + 1.20),
                    (0.70, 0.40, 1.80), col_pump)
    _make_box_local("MM_PumpDisplay",
                    (pmp_x, pmp_y, pmp_z + 2.05),
                    (0.60, 0.42, 0.30),
                    (0.20, 0.22, 0.28, 1.0))


def build_auto_dealership():
    """Big used-car dealership lot in EastComm south of the
    big-box pad. Long row of triangle flag bunting + showroom +
    a fleet of 16 inventory cars in 2 rows.
    """
    cx, cy = 480.0, -260.0
    ground_z = mesh_z(cx, cy)
    # Asphalt slab
    lot_w = 60.0
    lot_d = 28.0
    sv = []
    for (lx, ly) in [(cx - lot_w / 2, cy - lot_d / 2),
                     (cx + lot_w / 2, cy - lot_d / 2),
                     (cx + lot_w / 2, cy + lot_d / 2),
                     (cx - lot_w / 2, cy + lot_d / 2)]:
        sv.append((lx, ly, mesh_z(lx, ly) + 0.04))
    _finalize_mesh("Auto_Lot", sv, [[0, 1, 2, 3]],
                    (0.22, 0.22, 0.24, 1.0))

    # 16 inventory cars · 2 rows of 8
    car_palette = [
        (0.85, 0.20, 0.18, 1.0), (0.62, 0.62, 0.64, 1.0),
        (0.18, 0.32, 0.55, 1.0), (0.32, 0.55, 0.25, 1.0),
        (0.20, 0.20, 0.22, 1.0), (0.95, 0.85, 0.30, 1.0),
        (0.78, 0.74, 0.66, 1.0), (0.92, 0.55, 0.20, 1.0),
        (0.62, 0.42, 0.78, 1.0), (0.42, 0.62, 0.32, 1.0),
        (0.18, 0.18, 0.22, 1.0), (0.95, 0.94, 0.90, 1.0),
        (0.55, 0.32, 0.22, 1.0), (0.32, 0.42, 0.55, 1.0),
        (0.65, 0.68, 0.78, 1.0), (0.85, 0.78, 0.62, 1.0),
    ]
    car_idx = 0
    for row in (-1, 1):
        row_cy = cy + row * 6.0
        for k in range(8):
            cpx = cx - lot_w / 2 + 5.0 + k * 7.0
            cpy = row_cy
            cpz = mesh_z(cpx, cpy)
            face = '+Y' if row < 0 else '-Y'
            _build_parked_car(f"Auto_Car_{car_idx}",
                              cpx, cpy, cpz,
                              car_palette[car_idx], facing=face)
            car_idx += 1

    # Showroom building at the east end
    sh_x = cx + lot_w / 2 + 10.0
    sh_y = cy
    sh_z = mesh_z(sh_x, sh_y)
    sh_w, sh_d, sh_h = 14.0, 22.0, 5.5
    col_sh_wall = (0.32, 0.42, 0.55, 1.0)
    col_sh_glass = (0.48, 0.58, 0.72, 1.0)
    col_sh_roof = (0.32, 0.30, 0.28, 1.0)
    _make_box_local("Auto_Show_Slab",
                    (sh_x, sh_y, sh_z + 0.05),
                    (sh_w + 0.4, sh_d + 0.4, 0.10),
                    (0.78, 0.74, 0.66, 1.0))
    # 3 solid walls
    _make_box_local("Auto_Show_WallN",
                    (sh_x, sh_y + sh_d / 2 - 0.10,
                     sh_z + sh_h / 2),
                    (sh_w, 0.20, sh_h), col_sh_wall)
    _make_box_local("Auto_Show_WallS",
                    (sh_x, sh_y - sh_d / 2 + 0.10,
                     sh_z + sh_h / 2),
                    (sh_w, 0.20, sh_h), col_sh_wall)
    _make_box_local("Auto_Show_WallE",
                    (sh_x + sh_w / 2 - 0.10, sh_y,
                     sh_z + sh_h / 2),
                    (0.20, sh_d, sh_h), col_sh_wall)
    # West face is BIG plate glass (showroom window)
    _make_box_local("Auto_Show_GlassW",
                    (sh_x - sh_w / 2 + 0.05, sh_y,
                     sh_z + sh_h / 2),
                    (0.10, sh_d - 0.4, sh_h * 0.95), col_sh_glass)
    _make_box_local("Auto_Show_Roof",
                    (sh_x, sh_y, sh_z + sh_h + 0.10),
                    (sh_w + 0.4, sh_d + 0.4, 0.20), col_sh_roof)
    # Showroom interior: ONE shiny featured car
    feat_x = sh_x + 0.5
    feat_y = sh_y
    feat_z = mesh_z(feat_x, feat_y)
    _build_parked_car("Auto_FeaturedCar",
                       feat_x, feat_y, feat_z,
                       (0.85, 0.20, 0.18, 1.0), facing='-X')
    # Big SIGN pylon at the SW corner
    py_x = cx - lot_w / 2 - 4.0
    py_y = cy
    py_z = mesh_z(py_x, py_y)
    _make_cyl_local("Auto_PylonPole",
                    (py_x, py_y, py_z + 5.0),
                    0.30, 10.0,
                    (0.62, 0.62, 0.64, 1.0), segments=6)
    _make_box_local("Auto_PylonSign",
                    (py_x, py_y, py_z + 9.5),
                    (4.0, 0.20, 2.4),
                    (0.18, 0.32, 0.55, 1.0))


def build_library_and_bike_racks():
    """HCE Public Library — small civic building on Harmony
    Blvd just south of the elementary school. Plus bike racks
    at the elementary school + library + community pool.
    """
    # ── LIBRARY at (40, 80) — moved west of HarmonyBlvd (x=60)
    # so the road quad doesn't overlap the library. Building is
    # 16m wide so footprint x=32..48; road CL at x=60 leaves a
    # 12m gap which fits the sidewalk + bike racks + a strip of
    # lawn between road and library entrance.
    cx, cy = 40.0, 80.0
    ground_z = mesh_z(cx, cy)
    col_wall = (0.62, 0.42, 0.32, 1.0)         # warm brick
    col_trim = (0.95, 0.92, 0.86, 1.0)
    col_roof = (0.32, 0.30, 0.28, 1.0)
    col_door = (0.32, 0.18, 0.16, 1.0)
    col_glass = (0.32, 0.42, 0.55, 1.0)
    w, d, h = 22.0, 14.0, 5.5
    t = 0.20
    _make_box_local("Lib_Slab",
                    (cx, cy, ground_z + 0.05),
                    (w + 0.4, d + 0.4, 0.10), col_trim)
    _make_box_local("Lib_WallN",
                    (cx, cy + d / 2 - t / 2, ground_z + h / 2),
                    (w, t, h), col_wall)
    _make_box_local("Lib_WallE",
                    (cx + w / 2 - t / 2, cy, ground_z + h / 2),
                    (t, d, h), col_wall)
    _make_box_local("Lib_WallW",
                    (cx - w / 2 + t / 2, cy, ground_z + h / 2),
                    (t, d, h), col_wall)
    dw, dh = 2.6, 2.8
    left_w = w / 2 - dw / 2
    _make_box_local("Lib_WallS_L",
                    (cx - dw / 2 - left_w / 2,
                     cy - d / 2 + t / 2, ground_z + h / 2),
                    (left_w, t, h), col_wall)
    _make_box_local("Lib_WallS_R",
                    (cx + dw / 2 + left_w / 2,
                     cy - d / 2 + t / 2, ground_z + h / 2),
                    (left_w, t, h), col_wall)
    _make_box_local("Lib_WallS_Header",
                    (cx, cy - d / 2 + t / 2,
                     ground_z + dh + (h - dh) / 2),
                    (dw, t, h - dh), col_wall)
    _make_box_local("Lib_Door",
                    (cx, cy - d / 2 + 0.05, ground_z + dh / 2),
                    (dw, 0.06, dh - 0.10), col_door)
    # 4 tall windows on the south face
    for sgn in (-1, 1):
        for k in range(2):
            wx = cx + sgn * (dw / 2 + (k + 1) * 3.5)
            if abs(wx - cx) < w / 2 - 1.0:
                _make_box_local(f"Lib_Window_{sgn:+d}_{k}",
                                (wx, cy - d / 2 + 0.04,
                                 ground_z + 2.7),
                                (1.6, 0.04, 2.4), col_glass)
    _make_box_local("Lib_Roof",
                    (cx, cy, ground_z + h + 0.10),
                    (w + 0.4, d + 0.4, 0.20), col_roof)
    # White trim band south
    _make_box_local("Lib_TrimBand",
                    (cx, cy - d / 2 - 0.05,
                     ground_z + h - 0.30),
                    (w + 0.4, 0.10, 0.30), col_trim)
    # Sign panel above the entry
    _make_box_local("Lib_SignPanel",
                    (cx, cy - d / 2 - 0.20,
                     ground_z + h + 0.30),
                    (8.0, 0.14, 0.80),
                    (0.18, 0.32, 0.55, 1.0))

    # ── BIKE RACKS · short U-shaped steel rails
    def _emit_bike_rack(name_prefix, anchor_x, anchor_y, count=5):
        anc_z = mesh_z(anchor_x, anchor_y)
        for k in range(count):
            rx = anchor_x + (k - count / 2.0 + 0.5) * 0.80
            ry = anchor_y
            # Two vertical posts + one curved top (approximated)
            for sgn in (-1, 1):
                _make_cyl_local(
                    f"{name_prefix}_Post_{k}_{sgn:+d}",
                    (rx + sgn * 0.20, ry, anc_z + 0.40),
                    0.03, 0.80,
                    (0.42, 0.42, 0.45, 1.0), segments=4)
            # Top bar
            _make_box_local(f"{name_prefix}_Bar_{k}",
                            (rx, ry, anc_z + 0.80),
                            (0.46, 0.04, 0.04),
                            (0.42, 0.42, 0.45, 1.0))

    # Bike rack outside the library entry
    _emit_bike_rack("Lib_BikeRack", cx + 6, cy - d / 2 - 1.5, 4)
    # Bike rack outside the elementary school entry
    _emit_bike_rack("ES_BikeRack", -90.0 + 4.0, 160.0 - 7.0 - 1.5,
                     6)
    # Bike rack at the community pool change-room west door
    _emit_bike_rack("HP_BikeRack", 30.0 + 32.0 * 1.10 + 12.0 - 5,
                     60.0 - 5, 4)


def build_little_league_field():
    """Little League baseball diamond west of the elementary
    school. Backstop fence + dirt infield + grass outfield +
    bleachers. Sits on the HarmonyPark / NorthComm boundary.
    """
    cx, cy = -150.0, 200.0
    ground_z = mesh_z(cx, cy)
    col_grass = (0.30, 0.55, 0.25, 1.0)
    col_dirt = (0.72, 0.55, 0.40, 1.0)
    col_line = (0.92, 0.90, 0.84, 1.0)
    col_fence = (0.62, 0.62, 0.64, 1.0)
    col_bench = (0.42, 0.30, 0.20, 1.0)

    # Outfield grass (large rectangle as approximation for the
    # actual fan-shaped outfield)
    _make_box_local("LL_Outfield",
                    (cx, cy + 30.0, ground_z + 0.04),
                    (60.0, 50.0, 0.06), col_grass)
    # Dirt infield (diamond-ish, here a square)
    _make_box_local("LL_Infield",
                    (cx, cy, ground_z + 0.05),
                    (24.0, 24.0, 0.06), col_dirt)
    # Pitcher's mound (small circle of dirt)
    _make_cyl_local("LL_Mound",
                    (cx, cy + 8.0, ground_z + 0.10),
                    1.5, 0.20, col_dirt, segments=10)
    # Base path lines (along diamond perimeter)
    # First-base line (south-east)
    _make_box_local("LL_BaseLine_1B",
                    (cx + 6.0, cy + 6.0, ground_z + 0.08),
                    (12.0, 0.18, 0.02), col_line)
    # Third-base line (south-west)
    _make_box_local("LL_BaseLine_3B",
                    (cx - 6.0, cy + 6.0, ground_z + 0.08),
                    (0.18, 12.0, 0.02), col_line)

    # Backstop fence — 3 panels forming a U behind home plate
    bs_y = cy - 2.0
    for sgn_x, panel_w in ((-1, 4.0), (0, 6.0), (1, 4.0)):
        if sgn_x == 0:
            _make_box_local("LL_Backstop_Mid",
                            (cx, bs_y - 4.0,
                             ground_z + 2.2),
                            (panel_w, 0.20, 4.4), col_fence)
        else:
            _make_box_local(f"LL_Backstop_{sgn_x:+d}",
                            (cx + sgn_x * 4.5, bs_y - 2.0,
                             ground_z + 2.2),
                            (0.20, 4.0, 4.4), col_fence)
    # Home plate
    _make_box_local("LL_HomePlate",
                    (cx, bs_y + 1.0, ground_z + 0.08),
                    (0.50, 0.30, 0.02), col_line)
    # Dugout (3-row bench under a small canopy roof) on the
    # west side
    dug_x = cx - 16.0
    dug_y = cy
    dz = mesh_z(dug_x, dug_y)
    for k_row in range(2):
        _make_box_local(f"LL_Dugout_Bench_{k_row}",
                        (dug_x, dug_y, dz + 0.42 + k_row * 0.50),
                        (10.0, 1.0, 0.10), col_bench)
    # Dugout roof posts + roof
    for sgn in (-1, 1):
        _make_cyl_local(f"LL_Dugout_Post_{sgn:+d}",
                        (dug_x + sgn * 5.0, dug_y, dz + 1.5),
                        0.10, 3.0, col_fence, segments=4)
    _make_box_local("LL_Dugout_Roof",
                    (dug_x, dug_y, dz + 3.0),
                    (10.5, 2.0, 0.20),
                    (0.32, 0.30, 0.28, 1.0))
    # Same on the east side (visitors)
    dug_x2 = cx + 16.0
    for k_row in range(2):
        _make_box_local(f"LL_Dugout2_Bench_{k_row}",
                        (dug_x2, dug_y, dz + 0.42 + k_row * 0.50),
                        (10.0, 1.0, 0.10), col_bench)
    for sgn in (-1, 1):
        _make_cyl_local(f"LL_Dugout2_Post_{sgn:+d}",
                        (dug_x2 + sgn * 5.0, dug_y, dz + 1.5),
                        0.10, 3.0, col_fence, segments=4)
    _make_box_local("LL_Dugout2_Roof",
                    (dug_x2, dug_y, dz + 3.0),
                    (10.5, 2.0, 0.20),
                    (0.32, 0.30, 0.28, 1.0))


def build_self_storage():
    """SafeKeep Self-Storage — long parallel rows of orange
    roll-up units. Sits in EastComm south of the big-box pad.
    """
    cx, cy = 480.0, -180.0
    ground_z = mesh_z(cx, cy)
    col_unit_body = (0.62, 0.58, 0.50, 1.0)
    col_unit_door = (0.85, 0.45, 0.20, 1.0)
    col_roof = (0.32, 0.32, 0.30, 1.0)
    col_office = (0.85, 0.82, 0.74, 1.0)

    # 3 parallel rows of units, each 60 m long × 4 m deep
    row_w = 60.0
    row_d = 4.0
    row_h = 2.8
    door_w = 2.4
    n_doors = int(row_w / (door_w + 0.2))
    for row_idx, row_cy_off in enumerate((-12.0, -4.0, 4.0)):
        rcx = cx
        rcy = cy + row_cy_off
        # Body wall
        _make_box_local(f"SS_Row_{row_idx}_Body",
                        (rcx, rcy, ground_z + row_h / 2),
                        (row_w, row_d, row_h), col_unit_body)
        # Roof
        _make_box_local(f"SS_Row_{row_idx}_Roof",
                        (rcx, rcy, ground_z + row_h + 0.10),
                        (row_w + 0.20, row_d + 0.20, 0.20),
                        col_roof)
        # Orange roll-up doors along the SOUTH face
        for k in range(n_doors):
            dx = rcx - row_w / 2 + (k + 0.5) * (door_w + 0.2)
            _make_box_local(f"SS_Row_{row_idx}_Door_{k}",
                            (dx, rcy - row_d / 2 + 0.05,
                             ground_z + 1.05),
                            (door_w, 0.06, 2.10), col_unit_door)
    # Front gate office at the west end
    of_x = cx - row_w / 2 - 8.0
    of_y = cy
    of_z = mesh_z(of_x, of_y)
    of_w, of_d, of_h = 10.0, 8.0, 3.6
    _make_box_local("SS_Office_Slab",
                    (of_x, of_y, of_z + 0.05),
                    (of_w + 0.4, of_d + 0.4, 0.10), col_office)
    _make_box_local("SS_Office_Walls",
                    (of_x, of_y, of_z + of_h / 2),
                    (of_w, of_d, of_h), col_office)
    _make_box_local("SS_Office_Roof",
                    (of_x, of_y, of_z + of_h + 0.10),
                    (of_w + 0.4, of_d + 0.4, 0.20), col_roof)
    # Front window on south face
    _make_box_local("SS_Office_Window",
                    (of_x, of_y - of_d / 2 + 0.04,
                     of_z + 1.6),
                    (5.0, 0.04, 1.4),
                    (0.32, 0.42, 0.55, 1.0))
    # Front door
    _make_box_local("SS_Office_Door",
                    (of_x + 3.0, of_y - of_d / 2 + 0.05,
                     of_z + 1.05),
                    (1.0, 0.06, 2.10), col_unit_door)


def build_ambient_npcs():
    """Scatter ~15 ambient NPC figures around civic + commercial
    landmarks so the district feels populated. Each samples
    mesh_z at its position so it stands on actual ground.
    """
    ambient = [
        # (name, x, y, facing, hair, jacket, pants)
        # Elementary school front
        ("ES_Teacher", -90, 148, '-Y', 'short',
            (0.42, 0.62, 0.32, 1.0), (0.18, 0.22, 0.30, 1.0)),
        ("ES_Parent",  -85, 145, '-Y', 'bowl',
            (0.62, 0.42, 0.78, 1.0), (0.20, 0.20, 0.22, 1.0)),
        ("ES_Kid",     -95, 142, '+Y', 'bowl',
            (0.95, 0.42, 0.30, 1.0), (0.55, 0.32, 0.22, 1.0)),
        # Library
        ("Lib_Librarian", 60, 75, '-Y', 'short',
            (0.32, 0.18, 0.32, 1.0), (0.42, 0.32, 0.22, 1.0)),
        ("Lib_Patron",    55, 71, '-Y', 'bowl',
            (0.95, 0.85, 0.30, 1.0), (0.32, 0.42, 0.55, 1.0)),
        # Church
        ("Ch_Pastor", -30, 130, '-Y', 'short',
            (0.18, 0.18, 0.22, 1.0), (0.18, 0.18, 0.22, 1.0)),
        # Hospital ambulance bay
        ("Hos_EMT_L", 175, 305, '-Y', 'short',
            (0.85, 0.94, 0.92, 1.0), (0.18, 0.18, 0.22, 1.0)),
        ("Hos_EMT_R", 185, 305, '-Y', 'short',
            (0.85, 0.94, 0.92, 1.0), (0.18, 0.18, 0.22, 1.0)),
        # Truck stop attendant
        ("TS_Att", 200, -370, '-Y', 'bowl',
            (0.55, 0.42, 0.30, 1.0), (0.32, 0.32, 0.36, 1.0)),
        # Country club host
        ("CC_Host", -3, 360, '-Y', 'short',
            (0.18, 0.18, 0.22, 1.0), (0.18, 0.18, 0.22, 1.0)),
        # Police officer outside PD
        ("PD_Officer", -170, -75, '-Y', 'short',
            (0.18, 0.22, 0.42, 1.0), (0.18, 0.22, 0.42, 1.0)),
        # Mini-mart clerk
        ("MM_Clerk", -260, -47, '-Y', 'short',
            (0.32, 0.55, 0.78, 1.0), (0.20, 0.20, 0.22, 1.0)),
        # Plaza pedestrian
        ("Plaza_Walker", -90, 23, '-X', 'bowl',
            (0.95, 0.42, 0.62, 1.0), (0.18, 0.32, 0.55, 1.0)),
        # Bus-stop waiter at Harmony/Horizon junction
        ("Bus_Waiter", 65, 61, '-Y', 'short',
            (0.42, 0.30, 0.20, 1.0), (0.32, 0.32, 0.34, 1.0)),
        # Cemetery visitor
        ("Cm_Mourner", -15, 130, '-Y', 'short',
            (0.18, 0.18, 0.20, 1.0), (0.18, 0.18, 0.20, 1.0)),
    ]
    for tag, fx, fy, facing, hair, jacket, pants in ambient:
        fz = mesh_z(fx, fy)
        human_figure(
            name=f"AmbientNPC_{tag}",
            base_x=fx, base_y=fy, base_z=fz,
            scale=1.0,
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


def build_school_zone_signs():
    """Yellow pentagon SCHOOL CROSSING signs on the approaches
    to the elementary school and high school. Plus speed-limit
    signs reading "SCHOOL ZONE 25".
    """
    COL_POLE = (0.62, 0.62, 0.64, 1.0)
    COL_YELLOW = (0.98, 0.85, 0.20, 1.0)
    COL_WHITE = (0.98, 0.98, 0.96, 1.0)
    COL_BLACK = (0.08, 0.08, 0.10, 1.0)

    def _xing_sign(name, x, y, face_axis):
        z = mesh_z(x, y)
        _make_cyl_local(f"{name}_Pole",
                        (x, y, z + 1.4),
                        0.04, 2.8, COL_POLE, segments=4)
        if face_axis == 'X':
            sign_size = (0.06, 0.60, 0.60)
        else:
            sign_size = (0.60, 0.06, 0.60)
        _make_box_local(f"{name}_Face",
                        (x, y, z + 2.7),
                        sign_size, COL_YELLOW)

    def _speed_sign(name, x, y, face_axis):
        z = mesh_z(x, y)
        _make_cyl_local(f"{name}_Pole",
                        (x, y, z + 1.0),
                        0.04, 2.0, COL_POLE, segments=4)
        if face_axis == 'X':
            sign_size = (0.04, 0.40, 0.55)
        else:
            sign_size = (0.40, 0.04, 0.55)
        _make_box_local(f"{name}_Face",
                        (x, y, z + 2.0),
                        sign_size, COL_WHITE)
        # Black "25" approximated as black box on face
        if face_axis == 'X':
            num_size = (0.05, 0.30, 0.30)
        else:
            num_size = (0.30, 0.05, 0.30)
        _make_box_local(f"{name}_Number",
                        (x, y, z + 1.85),
                        num_size, COL_BLACK)

    # Elementary school (-90, 160) — yellow crossing east + west
    # of school + speed-limit signs on Harmony Blvd approaches
    _xing_sign("ES_Xing_E", -65, 165, 'Y')
    _xing_sign("ES_Xing_W", -115, 165, 'Y')
    _speed_sign("ES_Speed_N", 8, 215, 'X')
    _speed_sign("ES_Speed_S", 12, 175, 'X')

    # High school (340, 50) — yellow crossings + speed signs on
    # Horizon Dr east approaches
    _xing_sign("HS_Xing_E", 380, 5, 'X')
    _xing_sign("HS_Xing_W", 300, -5, 'X')
    _speed_sign("HS_Speed_E", 360, 5, 'X')
    _speed_sign("HS_Speed_W", 280, -10, 'X')


def build_street_name_signs():
    """Green street-name signs at major arterial intersections.
    Each sign = a steel pole with two perpendicular green
    rectangular plaques (one labelling each crossing road).
    """
    COL_POLE = (0.42, 0.42, 0.45, 1.0)
    COL_SIGN_GREEN = (0.20, 0.45, 0.25, 1.0)
    COL_SIGN_TRIM = (0.95, 0.94, 0.90, 1.0)

    def _sign(name, x, y, ns_face, ew_face):
        """ns_face = name of the N-S road for the
        north-pointing plaque. ew_face = E-W road name."""
        z = mesh_z(x, y)
        _make_cyl_local(f"{name}_Pole",
                        (x, y, z + 2.2),
                        0.04, 4.4, COL_POLE, segments=4)
        # N-S road label (faces east/west, thin axis Y)
        _make_box_local(f"{name}_PlaqueNS",
                        (x, y, z + 4.2),
                        (1.6, 0.06, 0.40), COL_SIGN_GREEN)
        # E-W road label (faces north/south, thin axis X)
        _make_box_local(f"{name}_PlaqueEW",
                        (x, y, z + 3.8),
                        (0.06, 1.6, 0.40), COL_SIGN_GREEN)
        # Tiny white border slabs (decorative)
        _make_box_local(f"{name}_PlaqueNS_Trim",
                        (x, y, z + 4.40),
                        (1.6, 0.07, 0.04), COL_SIGN_TRIM)
        _make_box_local(f"{name}_PlaqueEW_Trim",
                        (x, y, z + 4.00),
                        (0.07, 1.6, 0.04), COL_SIGN_TRIM)

    # Major intersections to label
    _sign("Sign_HarmHorz", 60, -20, "HARMONY BLVD", "HORIZON DR")
    _sign("Sign_HarmCC",     0, 340, "HARMONY BLVD", "CC ENTRY")
    _sign("Sign_HarmChap",  12, -392, "HARMONY BLVD", "CHAPTER 1")
    _sign("Sign_HorzWE",  -460, -20, "HORIZON DR",   "WEST COMM")
    _sign("Sign_HorzEC",   440,   0, "HORIZON DR",   "EAST COMM")
    _sign("Sign_HzPlaza", -100,  -50, "HORIZON DR",   "PLAZA")
    _sign("Sign_NRSpur",  -320,  100, "ASPEN-BIRCH",  "NR SPUR")


def build_crosswalks_and_stops():
    """Painted white zebra crosswalks + red stop signs at the
    major intersections — Harmony Blvd × Horizon Dr (the big
    central junction), the elementary-school approach, and the
    high-school field entry on Horizon Dr.
    """
    COL_WHITE = (0.92, 0.90, 0.84, 1.0)
    COL_RED = (0.85, 0.20, 0.18, 1.0)
    COL_POLE = (0.62, 0.62, 0.64, 1.0)

    def _zebra(cx, cy, span_axis, length, prefix):
        """4-stripe zebra centered at (cx, cy). span_axis = 'x'
        means stripes run along Y direction (perpendicular to
        an east-west road, where the pedestrian crosses Y)."""
        n_stripes = 5
        stripe_w = 0.45
        gap = 0.45
        total = n_stripes * stripe_w + (n_stripes - 1) * gap
        for k in range(n_stripes):
            off = -total / 2 + stripe_w / 2 + k * (stripe_w + gap)
            if span_axis == 'x':
                # Stripe centered at cy, off-set in x, runs Y direction
                _make_box_local(f"{prefix}_Stripe_{k}",
                                (cx + off, cy,
                                 mesh_z(cx + off, cy) + 0.055),
                                (stripe_w, length, 0.01), COL_WHITE)
            else:
                _make_box_local(f"{prefix}_Stripe_{k}",
                                (cx, cy + off,
                                 mesh_z(cx, cy + off) + 0.055),
                                (length, stripe_w, 0.01), COL_WHITE)

    def _stop_sign(name, x, y, face_dir):
        z = mesh_z(x, y)
        _make_cyl_local(f"{name}_Pole",
                        (x, y, z + 1.1),
                        0.04, 2.2, COL_POLE, segments=4)
        # face_dir 'X' → thin axis X, faces ±X; 'Y' → thin Y
        if face_dir == 'X':
            sign_size = (0.04, 0.50, 0.50)
        else:
            sign_size = (0.50, 0.04, 0.50)
        _make_box_local(f"{name}_Face",
                        (x, y, z + 2.2),
                        sign_size, COL_RED)

    # Big junction: Harmony Blvd × Horizon Dr around (60, -20)
    # Harmony runs N-S here (vertical road), Horizon E-W
    # Need 2 crosswalks: one across Harmony (pedestrians going E-W)
    # and one across Horizon (pedestrians going N-S)
    _zebra(60, -28, 'y', 8.0, "X_BigJct_AcrossH")    # across Horizon
    _zebra(50, -20, 'x', 8.0, "X_BigJct_AcrossB")    # across Harmony
    # Stop signs at the 4 approaches
    _stop_sign("X_BigJct_S_StopN", 64, -32, 'Y')
    _stop_sign("X_BigJct_S_StopS", 56, -8,  'Y')
    _stop_sign("X_BigJct_S_StopE", 70, -16, 'X')
    _stop_sign("X_BigJct_S_StopW", 50, -24, 'X')

    # Elementary school approach on Harmony Blvd around (30, 200)
    _zebra(30, 195, 'x', 8.0, "X_ESC")
    _stop_sign("X_ESC_StopE", 36, 192, 'X')
    _stop_sign("X_ESC_StopW", 24, 198, 'X')

    # High-school entrance on Horizon Drive near (320, -5)
    _zebra(320, -5, 'y', 8.0, "X_HS")
    _stop_sign("X_HS_StopN", 326, -10, 'Y')
    _stop_sign("X_HS_StopS", 314, 0,   'Y')

    # West Estates approach on Horizon Drive around (-440, -20)
    _zebra(-430, -20, 'x', 8.0, "X_WE")
    _stop_sign("X_WE_StopE", -424, -24, 'X')
    _stop_sign("X_WE_StopW", -436, -16, 'X')


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

    corridor_xys = {name: [(x, y) for (x, y, _z) in wps]
                    for (name, wps, _hw, _sh) in ROAD_CORRIDORS}
    # Arterials at standard 2.4m sidewalk, 6.4m offset
    _emit_sidewalk(_catmull_rom_2d(corridor_xys["HarmonyBlvd"],
                                    samples_per_seg=4),
                   "HarmonyBlvd_")
    _emit_sidewalk(_catmull_rom_2d(corridor_xys["HorizonDr"],
                                    samples_per_seg=4),
                   "HorizonDr_")
    # ── COMMERCIAL FRONTAGE sidewalks · chapter-1 + east comm
    # collectors. Narrower 1.6m sidewalk + tighter offset since
    # connectors are narrower. _emit_sidewalk uses module-scoped
    # constants, so we redo the math inline with narrower values.
    sw_w_link = 1.6
    sw_off_link = 2.5 + 0.6 + sw_w_link / 2
    COL_SIDEWALK_LINK = (0.78, 0.76, 0.72, 1.0)
    def _emit_link_sw(pts, prefix):
        for sgn in (-1, 1):
            for i in range(len(pts) - 1):
                x0, y0 = pts[i]; x1, y1 = pts[i + 1]
                dxs = x1 - x0; dys = y1 - y0
                seg_len = math.hypot(dxs, dys) or 1.0
                perp_x = -dys / seg_len
                perp_y =  dxs / seg_len
                pv = []
                for (px, py) in [
                    (x0 + sgn * perp_x * (sw_off_link - sw_w_link / 2),
                     y0 + sgn * perp_y * (sw_off_link - sw_w_link / 2)),
                    (x1 + sgn * perp_x * (sw_off_link - sw_w_link / 2),
                     y1 + sgn * perp_y * (sw_off_link - sw_w_link / 2)),
                    (x1 + sgn * perp_x * (sw_off_link + sw_w_link / 2),
                     y1 + sgn * perp_y * (sw_off_link + sw_w_link / 2)),
                    (x0 + sgn * perp_x * (sw_off_link + sw_w_link / 2),
                     y0 + sgn * perp_y * (sw_off_link + sw_w_link / 2)),
                ]:
                    pv.append((px, py, mesh_z(px, py) + 0.06))
                _finalize_mesh(f"{prefix}Sidewalk_{i}_{sgn:+d}", pv,
                                [[0, 1, 2, 3]], COL_SIDEWALK_LINK)
    # Ch1Frontage has its own sidewalks emitted inside
    # build_commercial_cluster (the storefront walk at y=-366.5).
    # Don't double up.
    for cname, prefix in [
        ("ECommN",          "ECommN_"),
        ("ECommS",          "ECommS_"),
        ("NRLink",          "NRLink_"),
        ("ECDSLink",        "ECDSLink_"),
    ]:
        if cname in corridor_xys:
            _emit_link_sw(_catmull_rom_2d(corridor_xys[cname],
                                            samples_per_seg=4),
                          prefix)
    # ── RESIDENTIAL STREET sidewalks · narrower 1.2m walks set
    # back ~3.5m from the road CL (matches the residential street
    # geometry: 4m wide road + 0.4m curb + 1.2m grass + 1.2m walk).
    # Emitted on BOTH sides for every residential corridor so each
    # house has frontage walking access.
    sw_w_res = 1.2
    sw_off_res = 2.0 + 0.5 + sw_w_res / 2   # CL-to-sidewalk-centerline
    COL_SIDEWALK_RES = (0.82, 0.80, 0.74, 1.0)
    def _emit_res_sw(pts, prefix):
        for sgn in (-1, 1):
            for i in range(len(pts) - 1):
                x0, y0 = pts[i]; x1, y1 = pts[i + 1]
                dxs = x1 - x0; dys = y1 - y0
                seg_len = math.hypot(dxs, dys) or 1.0
                perp_x = -dys / seg_len
                perp_y =  dxs / seg_len
                pv = []
                for (px, py) in [
                    (x0 + sgn * perp_x * (sw_off_res - sw_w_res / 2),
                     y0 + sgn * perp_y * (sw_off_res - sw_w_res / 2)),
                    (x1 + sgn * perp_x * (sw_off_res - sw_w_res / 2),
                     y1 + sgn * perp_y * (sw_off_res - sw_w_res / 2)),
                    (x1 + sgn * perp_x * (sw_off_res + sw_w_res / 2),
                     y1 + sgn * perp_y * (sw_off_res + sw_w_res / 2)),
                    (x0 + sgn * perp_x * (sw_off_res + sw_w_res / 2),
                     y0 + sgn * perp_y * (sw_off_res + sw_w_res / 2)),
                ]:
                    pv.append((px, py, mesh_z(px, py) + 0.06))
                _finalize_mesh(f"{prefix}Sidewalk_{i}_{sgn:+d}", pv,
                                [[0, 1, 2, 3]], COL_SIDEWALK_RES)
    for cname, prefix in [
        ("NRAspen",     "NRAspen_"),
        ("NRBirch",     "NRBirch_"),
        ("NRCedar",     "NRCedar_"),
        ("NRSpur",      "NRSpur_"),
        ("WEMag",       "WEMag_"),
        ("WELoop",      "WELoop_"),
        ("P2Main",      "P2Main_"),
        ("ECDSRidge",   "ECDSRidge_"),
        ("ECDSCul",     "ECDSCul_"),
    ]:
        if cname in corridor_xys:
            _emit_res_sw(_catmull_rom_2d(corridor_xys[cname],
                                          samples_per_seg=4),
                          prefix)


def build_arterial_trees():
    """Street trees along Harmony Blvd and Horizon Drive at 25 m
    intervals, alternating with the streetlamps so the result is
    a continuous canopy + lamp parade along the arterials.
    """
    COL_TRUNK = (0.30, 0.22, 0.16, 1.0)
    COL_CANOPY = (0.30, 0.55, 0.25, 1.0)
    TREE_OFFSET = 7.8     # 1.4 m outside the sidewalk's outer edge

    def _emit_trees(pts, prefix, spacing=25.0):
        accumulated = 0.0
        next_tree = 12.5     # half a spacing offset from start
        side_sgn = -1        # opposite-side seed from lamps
        idx = 0
        for i in range(len(pts) - 1):
            x0, y0 = pts[i]
            x1, y1 = pts[i + 1]
            seg_len = math.hypot(x1 - x0, y1 - y0) or 1.0
            seg_end = accumulated + seg_len
            while next_tree < seg_end:
                t = (next_tree - accumulated) / seg_len
                mx = x0 + (x1 - x0) * t
                my = y0 + (y1 - y0) * t
                dxs = x1 - x0; dys = y1 - y0
                perp_x = -dys / seg_len
                perp_y =  dxs / seg_len
                tx = mx + side_sgn * perp_x * TREE_OFFSET
                ty = my + side_sgn * perp_y * TREE_OFFSET
                tz = mesh_z(tx, ty)
                trunk_h = 3.6
                canopy_r = 2.4
                _make_cyl_local(f"{prefix}Tree_{idx}_Trunk",
                                (tx, ty, tz + trunk_h / 2),
                                0.20, trunk_h, COL_TRUNK, segments=6)
                _make_sphere_low_local(
                    f"{prefix}Tree_{idx}_Canopy",
                    (tx, ty, tz + trunk_h + canopy_r * 0.55),
                    canopy_r, COL_CANOPY,
                    rings=3, segments=8)
                idx += 1
                side_sgn = -side_sgn
                next_tree += spacing
            accumulated = seg_end

    corridor_xys = {name: [(x, y) for (x, y, _z) in wps]
                    for (name, wps, _hw, _sh) in ROAD_CORRIDORS}
    _emit_trees(_catmull_rom_2d(corridor_xys["HarmonyBlvd"],
                                  samples_per_seg=4),
                 "HarmonyBlvd_")
    _emit_trees(_catmull_rom_2d(corridor_xys["HorizonDr"],
                                  samples_per_seg=4),
                 "HorizonDr_")

    # RESIDENTIAL STREET TREES · narrower offset (5m from CL),
    # closer spacing (18m) to match a typical residential street
    # canopy. Smaller trees too (trunk_h 3.0, canopy 1.8).
    RES_TREE_OFFSET = 5.0
    def _emit_res_trees(pts, prefix, spacing=18.0):
        accumulated = 0.0
        next_tree = 9.0
        side_sgn = -1
        idx = 0
        for i in range(len(pts) - 1):
            x0, y0 = pts[i]
            x1, y1 = pts[i + 1]
            seg_len = math.hypot(x1 - x0, y1 - y0) or 1.0
            seg_end = accumulated + seg_len
            while next_tree < seg_end:
                t = (next_tree - accumulated) / seg_len
                mx = x0 + (x1 - x0) * t
                my = y0 + (y1 - y0) * t
                dxs = x1 - x0; dys = y1 - y0
                perp_x = -dys / seg_len
                perp_y =  dxs / seg_len
                tx = mx + side_sgn * perp_x * RES_TREE_OFFSET
                ty = my + side_sgn * perp_y * RES_TREE_OFFSET
                tz = mesh_z(tx, ty)
                trunk_h = 3.0
                canopy_r = 1.8
                _make_cyl_local(f"{prefix}Tree_{idx}_Trunk",
                                (tx, ty, tz + trunk_h / 2),
                                0.16, trunk_h, COL_TRUNK, segments=6)
                _make_sphere_low_local(
                    f"{prefix}Tree_{idx}_Canopy",
                    (tx, ty, tz + trunk_h + canopy_r * 0.55),
                    canopy_r, COL_CANOPY,
                    rings=3, segments=8)
                idx += 1
                side_sgn = -side_sgn
                next_tree += spacing
            accumulated = seg_end
    for cname, prefix in [
        ("NRAspen",   "NRAspen_RT_"),
        ("NRBirch",   "NRBirch_RT_"),
        ("NRCedar",   "NRCedar_RT_"),
        ("NRSpur",    "NRSpur_RT_"),
        ("WEMag",     "WEMag_RT_"),
        ("WELoop",    "WELoop_RT_"),
        ("P2Main",    "P2Main_RT_"),
        ("ECDSRidge", "ECDSRidge_RT_"),
        ("ECDSCul",   "ECDSCul_RT_"),
    ]:
        if cname in corridor_xys:
            _emit_res_trees(_catmull_rom_2d(corridor_xys[cname],
                                              samples_per_seg=4),
                            prefix)


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

    corridor_xys = {name: [(x, y) for (x, y, _z) in wps]
                    for (name, wps, _hw, _sh) in ROAD_CORRIDORS}
    _emit_lamps(_catmull_rom_2d(corridor_xys["HarmonyBlvd"],
                                  samples_per_seg=4),
                 "HarmonyBlvd_")
    _emit_lamps(_catmull_rom_2d(corridor_xys["HorizonDr"],
                                  samples_per_seg=4),
                 "HorizonDr_")

    # RESIDENTIAL STREET LAMPS · shorter (4m vs 6m arterial),
    # offset 3.5m from CL, spaced 30m. Single-head fixture instead
    # of the arterial's twin-head shoebox.
    def _emit_res_lamps(pts, prefix, spacing=30.0):
        accumulated = 0.0
        next_lamp = 15.0
        side_sgn = 1
        for i in range(len(pts) - 1):
            x0, y0 = pts[i]
            x1, y1 = pts[i + 1]
            seg_len = math.hypot(x1 - x0, y1 - y0) or 1.0
            seg_end = accumulated + seg_len
            while next_lamp < seg_end:
                t = (next_lamp - accumulated) / seg_len
                mx = x0 + (x1 - x0) * t
                my = y0 + (y1 - y0) * t
                dxs = x1 - x0; dys = y1 - y0
                perp_x = -dys / seg_len
                perp_y =  dxs / seg_len
                lamp_x = mx + side_sgn * perp_x * 3.5
                lamp_y = my + side_sgn * perp_y * 3.5
                lz = mesh_z(lamp_x, lamp_y)
                lamp_h_res = 4.0
                _make_cyl_local(f"{prefix}Lamp_{int(next_lamp)}",
                                (lamp_x, lamp_y, lz + lamp_h_res / 2),
                                0.06, lamp_h_res,
                                COL_LAMP_POLE, segments=6)
                # Single shoebox head
                _make_box_local(f"{prefix}Lamp_Head_{int(next_lamp)}",
                                (lamp_x, lamp_y, lz + lamp_h_res - 0.05),
                                (0.30, 0.18, 0.14), COL_LAMP_HEAD)
                side_sgn = -side_sgn
                next_lamp += spacing
            accumulated = seg_end
    for cname, prefix in [
        ("NRAspen",   "NRAspen_LP_"),
        ("NRBirch",   "NRBirch_LP_"),
        ("NRCedar",   "NRCedar_LP_"),
        ("WEMag",     "WEMag_LP_"),
        ("P2Main",    "P2Main_LP_"),
        ("ECDSRidge", "ECDSRidge_LP_"),
    ]:
        if cname in corridor_xys:
            _emit_res_lamps(_catmull_rom_2d(corridor_xys[cname],
                                              samples_per_seg=4),
                            prefix)


def build_residential_mailboxes():
    """Curbside mailboxes along every residential street. One
    mailbox per house spacing (~22m), alternating sides so each
    house has a clear curb-mount. The cul-de-sac roads get
    mailboxes only on the outer curve.
    """
    COL_BOX = (0.32, 0.32, 0.34, 1.0)   # dark grey rural mailbox
    COL_POST = (0.42, 0.30, 0.20, 1.0)  # wood post
    COL_FLAG = (0.85, 0.20, 0.18, 1.0)  # red flag
    mb_offset = 4.5    # m from road CL to mailbox
    mb_spacing = 22.0
    corridor_xys = {name: [(x, y) for (x, y, _z) in wps]
                    for (name, wps, _hw, _sh) in ROAD_CORRIDORS}

    def _emit_mailboxes(pts, prefix):
        accumulated = 0.0
        next_mb = 11.0      # first one at half a spacing in
        side_sgn = 1
        idx = 0
        for i in range(len(pts) - 1):
            x0, y0 = pts[i]; x1, y1 = pts[i + 1]
            seg_len = math.hypot(x1 - x0, y1 - y0) or 1.0
            seg_end = accumulated + seg_len
            while next_mb < seg_end:
                t = (next_mb - accumulated) / seg_len
                mx = x0 + (x1 - x0) * t
                my = y0 + (y1 - y0) * t
                dxs = x1 - x0; dys = y1 - y0
                perp_x = -dys / seg_len
                perp_y =  dxs / seg_len
                bx = mx + side_sgn * perp_x * mb_offset
                by = my + side_sgn * perp_y * mb_offset
                bz = mesh_z(bx, by)
                # Wooden post
                _make_box_local(f"{prefix}MB_{idx}_Post",
                                (bx, by, bz + 0.55),
                                (0.10, 0.10, 1.10), COL_POST)
                # Mailbox body (small horizontal cylinder/box)
                # Box orientation aligned with road (perpendicular
                # to perp): the LONG axis of the mailbox runs
                # parallel to the road direction.
                dx_norm = dxs / seg_len; dy_norm = dys / seg_len
                if abs(dx_norm) > abs(dy_norm):
                    box_sx, box_sy = 0.20, 0.32
                else:
                    box_sx, box_sy = 0.32, 0.20
                _make_box_local(f"{prefix}MB_{idx}_Body",
                                (bx, by, bz + 1.20),
                                (box_sx, box_sy, 0.22), COL_BOX)
                # Red flag on the road-facing side
                flag_x = bx - side_sgn * perp_x * 0.15
                flag_y = by - side_sgn * perp_y * 0.15
                if abs(dx_norm) > abs(dy_norm):
                    flag_sx, flag_sy = 0.04, 0.12
                else:
                    flag_sx, flag_sy = 0.12, 0.04
                _make_box_local(f"{prefix}MB_{idx}_Flag",
                                (flag_x, flag_y, bz + 1.32),
                                (flag_sx, flag_sy, 0.10), COL_FLAG)
                idx += 1
                side_sgn = -side_sgn
                next_mb += mb_spacing
            accumulated = seg_end

    for cname, prefix in [
        ("NRAspen",   "NRAspen_MB_"),
        ("NRBirch",   "NRBirch_MB_"),
        ("NRCedar",   "NRCedar_MB_"),
        ("WEMag",     "WEMag_MB_"),
        ("WELoop",    "WELoop_MB_"),
        ("P2Main",    "P2Main_MB_"),
        ("ECDSRidge", "ECDSRidge_MB_"),
    ]:
        if cname in corridor_xys:
            _emit_mailboxes(_catmull_rom_2d(corridor_xys[cname],
                                              samples_per_seg=4),
                            prefix)


def build_bus_stops():
    """Bus-stop shelters at key arterial intersections. Each:
    4 corner steel posts + slanted roof + back wall + bench.
    """
    # Positions moved to sit clearly ON THE SIDEWALK after the
    # 2026-06-15 arterial geometry update. Each (x, y) is at the
    # arterial sidewalk centerline (offset 6.4m perpendicular
    # from road CL on the east/south side).
    bus_specs = [
        # (name, cx, cy)
        # Harmony Blvd CL at y=60 is x=60 -> east sidewalk x=66.4
        ("HarmonyBlvd_HS",     67, 60),
        # Harmony Blvd CL at y=130 is x=60 -> east sidewalk x=66.4
        ("HarmonyBlvd_OT",     67, 130),
        # Horizon Dr CL at x=65 is y=-20 -> south sidewalk y=-26.4
        ("HorizonDr_Mid",      65, -27),
        # Horizon Dr CL at x=-440 is y=-17.5 -> south sidewalk y=-24
        ("HorizonDr_WE",     -440, -24),
        # Horizon Dr CL at x=260 is y=-10 -> south sidewalk y=-16.4
        ("HorizonDr_ECDS",    260, -17),
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


def build_taqueria_el_rancho():
    """Taqueria El Rancho — Mexican restaurant in the SouthComm
    belt east of the truck stop. Per user reference photo:
    strip-mall-style single-story building with a red
    'TAQUERIA EL RANCHO' sign across the south facade, plate-
    glass front, chest-style outdoor cooler. Per spec: a
    DRIVE-THROUGH window on the east face with a menu board +
    ordering speaker + pickup window and a curving drive-thru
    lane wrapping around the east side.
    """
    cx, cy = 290.0, -370.0
    ground_z = mesh_z(cx, cy)
    name_prefix = "Taqueria"

    # Palette — cream walls, red sign, brown trim
    col_wall = (0.85, 0.82, 0.74, 1.0)
    col_trim = (0.42, 0.32, 0.22, 1.0)
    col_roof = (0.32, 0.30, 0.28, 1.0)
    col_red_sign = (0.78, 0.18, 0.16, 1.0)
    col_door = (0.62, 0.42, 0.28, 1.0)
    col_glass_frame = (0.62, 0.62, 0.64, 1.0)
    col_window_warm = (0.95, 0.78, 0.45, 1.0)    # warm interior glow
    col_steel = (0.62, 0.62, 0.64, 1.0)
    col_chest_white = (0.92, 0.90, 0.86, 1.0)
    col_chest_dark = (0.32, 0.32, 0.34, 1.0)

    w, d, h = 14.0, 10.0, 4.5
    t = 0.20

    # ── SLAB
    _make_box_local(f"{name_prefix}_Slab",
                    (cx, cy, ground_z + 0.05),
                    (w + 0.6, d + 0.6, 0.10), col_trim)

    # ── WALLS: N (solid back), W (solid), E (with drive-thru
    # window), S (plate-glass storefront + door)
    _make_box_local(f"{name_prefix}_WallN",
                    (cx, cy + d / 2 - t / 2,
                     ground_z + h / 2),
                    (w, t, h), col_wall)
    _make_box_local(f"{name_prefix}_WallW",
                    (cx - w / 2 + t / 2, cy,
                     ground_z + h / 2),
                    (t, d, h), col_wall)
    # EAST wall · split for drive-through window opening
    dt_w = 1.6       # window width (along Y)
    dt_h = 1.4       # window height
    dt_centre_z = ground_z + 1.30
    dt_centre_y = cy - 1.0   # window biased toward the front
    # East wall above window
    _make_box_local(f"{name_prefix}_WallE_Above",
                    (cx + w / 2 - t / 2, dt_centre_y,
                     ground_z + dt_centre_z - ground_z + dt_h / 2 +
                     (h - (dt_centre_z - ground_z + dt_h / 2)) / 2),
                    (t, dt_w,
                     h - (dt_centre_z - ground_z + dt_h / 2)),
                    col_wall)
    # East wall below window
    _make_box_local(f"{name_prefix}_WallE_Below",
                    (cx + w / 2 - t / 2, dt_centre_y,
                     ground_z + (dt_centre_z - ground_z - dt_h / 2) / 2),
                    (t, dt_w,
                     dt_centre_z - ground_z - dt_h / 2),
                    col_wall)
    # East wall north of window
    east_n_l = (d / 2 - 1.0) - dt_w / 2     # length north of window
    if east_n_l > 0.1:
        _make_box_local(f"{name_prefix}_WallE_N",
                        (cx + w / 2 - t / 2,
                         dt_centre_y + dt_w / 2 + east_n_l / 2,
                         ground_z + h / 2),
                        (t, east_n_l, h), col_wall)
    # East wall south of window
    east_s_l = (d / 2 + 1.0) - dt_w / 2     # length south of window
    if east_s_l > 0.1:
        _make_box_local(f"{name_prefix}_WallE_S",
                        (cx + w / 2 - t / 2,
                         dt_centre_y - dt_w / 2 - east_s_l / 2,
                         ground_z + h / 2),
                        (t, east_s_l, h), col_wall)
    # Drive-through window pane (chrome frame + warm glow inside)
    _make_box_local(f"{name_prefix}_DT_WindowFrame",
                    (cx + w / 2 - 0.05, dt_centre_y,
                     dt_centre_z),
                    (0.06, dt_w + 0.10, dt_h + 0.10),
                    col_steel)
    _make_box_local(f"{name_prefix}_DT_WindowPane",
                    (cx + w / 2 - 0.10, dt_centre_y,
                     dt_centre_z),
                    (0.04, dt_w, dt_h),
                    col_window_warm)
    # Sliding-window divider line (vertical chrome strip)
    _make_box_local(f"{name_prefix}_DT_WindowDivider",
                    (cx + w / 2 - 0.07, dt_centre_y,
                     dt_centre_z),
                    (0.04, 0.06, dt_h),
                    col_steel)

    # ── PLATE-GLASS STOREFRONT on south face (Sam's-style)
    glass_y = cy - d / 2 + 0.05
    n_mullions = 5
    for k in range(n_mullions):
        mx = cx - w / 2 + 0.3 + k * (w - 0.6) / (n_mullions - 1)
        _make_box_local(f"{name_prefix}_GlassMul_{k}",
                        (mx, glass_y, ground_z + h / 2),
                        (0.10, 0.06, h), col_glass_frame)
    _make_box_local(f"{name_prefix}_GlassTopRail",
                    (cx, glass_y, ground_z + h - 0.08),
                    (w - 0.2, 0.08, 0.16), col_glass_frame)
    _make_box_local(f"{name_prefix}_GlassBotRail",
                    (cx, glass_y, ground_z + 0.30),
                    (w - 0.2, 0.08, 0.60), col_glass_frame)
    # Entry door — leftmost bay
    door_w = 1.4; door_h = 2.4
    door_cx = cx - w / 2 + 2.5
    for sgn in (-1, 1):
        _make_box_local(f"{name_prefix}_DoorJamb_{sgn:+d}",
                        (door_cx + sgn * door_w / 2, glass_y,
                         ground_z + door_h / 2),
                        (0.12, 0.10, door_h), col_trim)
    _make_box_local(f"{name_prefix}_DoorHeader",
                    (door_cx, glass_y, ground_z + door_h + 0.08),
                    (door_w + 0.12, 0.10, 0.16), col_trim)
    _make_box_local(f"{name_prefix}_Door",
                    (door_cx, glass_y, ground_z + door_h / 2),
                    (door_w - 0.10, 0.06, door_h - 0.10),
                    col_door)
    _make_box_local(f"{name_prefix}_DoorMat",
                    (door_cx, glass_y - 0.40, ground_z + 0.07),
                    (door_w + 0.20, 0.80, 0.02),
                    (0.32, 0.22, 0.18, 1.0))
    # Warm-glow window panels behind the mullion grid (suggests
    # interior visible — like in the reference photo)
    for k in range(n_mullions - 1):
        bay_w_ms = (w - 0.6) / (n_mullions - 1)
        gx = cx - w / 2 + 0.3 + (k + 0.5) * bay_w_ms
        # Skip the bay containing the door
        if abs(gx - door_cx) < bay_w_ms / 2:
            continue
        _make_box_local(f"{name_prefix}_GlassGlow_{k}",
                        (gx, glass_y - 0.02,
                         ground_z + h / 2),
                        (bay_w_ms - 0.20, 0.02,
                         h - 1.0), col_window_warm)

    # ── ROOF + parapet
    _make_box_local(f"{name_prefix}_Roof",
                    (cx, cy, ground_z + h + 0.10),
                    (w + 0.4, d + 0.4, 0.20), col_roof)
    parapet_h = 0.40
    _make_box_local(f"{name_prefix}_ParapetN",
                    (cx, cy + (d + 0.4) / 2,
                     ground_z + h + 0.20 + parapet_h / 2),
                    (w + 0.4, 0.18, parapet_h), col_wall)
    for sgn_x, tag in ((-1, 'W'), (1, 'E')):
        _make_box_local(f"{name_prefix}_Parapet_{tag}",
                        (cx + sgn_x * (w + 0.4) / 2, cy,
                         ground_z + h + 0.20 + parapet_h / 2),
                        (0.18, d + 0.4, parapet_h), col_wall)
    # HVAC rooftop unit
    _make_box_local(f"{name_prefix}_HVAC",
                    (cx + 3.0, cy + d * 0.3,
                     ground_z + h + 0.20 + 0.40),
                    (1.4, 1.2, 0.80), col_steel)

    # ── BIG RED SIGN PANEL across the south facade (the
    # TAQUERIA EL RANCHO sign from the reference photo)
    sign_y = cy - d / 2 - 0.20
    sign_h_local = 1.4
    _make_box_local(f"{name_prefix}_SignPanel",
                    (cx, sign_y,
                     ground_z + h + 0.30 + sign_h_local / 2),
                    (w * 0.85, 0.14, sign_h_local), col_red_sign)
    _make_box_local(f"{name_prefix}_SignTrim",
                    (cx, sign_y,
                     ground_z + h + 0.30 + sign_h_local + 0.05),
                    (w * 0.85 + 0.20, 0.16, 0.10), col_trim)
    # Small overhead-light strip below the sign illuminating it
    _make_box_local(f"{name_prefix}_SignLightBar",
                    (cx, sign_y,
                     ground_z + h + 0.10),
                    (w * 0.85, 0.10, 0.10), col_steel)

    # ── ADDRESS NUMBER plaque (from the photo · "300")
    _make_box_local(f"{name_prefix}_AddressPlaque",
                    (cx - w / 2 + 1.0, glass_y - 0.04,
                     ground_z + h - 0.5),
                    (0.40, 0.04, 0.30),
                    (0.18, 0.18, 0.20, 1.0))

    # ── OUTDOOR CHEST COOLER (the white-and-grey ice chest in
    # the reference photo)
    ch_x = cx - w / 2 + 4.5
    ch_y = cy - d / 2 - 1.4
    ch_z = mesh_z(ch_x, ch_y)
    # Lower body (dark grey)
    _make_box_local(f"{name_prefix}_Chest_LowerBody",
                    (ch_x, ch_y, ch_z + 0.35),
                    (1.6, 1.0, 0.70), col_chest_dark)
    # Upper body (white refrigeration unit)
    _make_box_local(f"{name_prefix}_Chest_UpperBody",
                    (ch_x, ch_y, ch_z + 0.95),
                    (1.6, 1.0, 0.50), col_chest_white)
    # Sliding glass top
    _make_box_local(f"{name_prefix}_Chest_Top",
                    (ch_x, ch_y, ch_z + 1.22),
                    (1.6, 1.0, 0.06),
                    (0.62, 0.70, 0.78, 1.0))
    # Side vent
    _make_box_local(f"{name_prefix}_Chest_Vent",
                    (ch_x + 0.78, ch_y, ch_z + 0.30),
                    (0.04, 0.40, 0.20),
                    (0.42, 0.42, 0.45, 1.0))

    # ── DRIVE-THRU LANE: curving asphalt strip wrapping around
    # the east side of the building from the south-east corner
    # to the north of the building.
    COL_DTLANE = (0.20, 0.20, 0.22, 1.0)
    COL_DTSTRIPE = (0.95, 0.85, 0.30, 1.0)
    lane_w = 3.6
    lane_hw = lane_w / 2
    # 5-point curve approaching from the south, wrapping around
    # east, going north past the window
    dt_pts = [
        (cx + w / 2 + 8.0, cy - d / 2 - 6.0),   # entry from south-east
        (cx + w / 2 + 8.0, cy - d / 2 + 2.0),
        (cx + w / 2 + 5.5, cy - d / 2 + 5.0),
        (cx + w / 2 + 3.5, cy - 1.0),            # at the window
        (cx + w / 2 + 3.5, cy + d / 2 + 2.0),    # exit north
        (cx + w / 2 + 6.0, cy + d / 2 + 6.0),
    ]
    for i in range(len(dt_pts) - 1):
        x0, y0 = dt_pts[i]; x1, y1 = dt_pts[i + 1]
        dxs = x1 - x0; dys = y1 - y0
        seg_len = math.hypot(dxs, dys) or 1.0
        perp_x = -dys / seg_len
        perp_y =  dxs / seg_len
        rv = []
        for (rx, ry) in [(x0 - perp_x * lane_hw, y0 - perp_y * lane_hw),
                         (x1 - perp_x * lane_hw, y1 - perp_y * lane_hw),
                         (x1 + perp_x * lane_hw, y1 + perp_y * lane_hw),
                         (x0 + perp_x * lane_hw, y0 + perp_y * lane_hw)]:
            rv.append((rx, ry, mesh_z(rx, ry) + 0.04))
        _finalize_mesh(f"{name_prefix}_DTLane_{i}", rv,
                        [[0, 1, 2, 3]], COL_DTLANE)

    # ── MENU BOARD on a pole on the SE approach to the drive-thru
    mb_x = cx + w / 2 + 5.0
    mb_y = cy - d / 2 - 2.0
    mb_z = mesh_z(mb_x, mb_y)
    # Pole
    _make_cyl_local(f"{name_prefix}_MenuBoard_Pole",
                    (mb_x, mb_y, mb_z + 1.4),
                    0.10, 2.8, col_steel, segments=6)
    # Board face (dark background w/ menu text suggested)
    _make_box_local(f"{name_prefix}_MenuBoard_Face",
                    (mb_x, mb_y, mb_z + 2.5),
                    (1.6, 0.12, 1.4),
                    (0.10, 0.10, 0.12, 1.0))
    # Bright stripe at top with TAQUERIA red banner
    _make_box_local(f"{name_prefix}_MenuBoard_Banner",
                    (mb_x, mb_y, mb_z + 3.10),
                    (1.6, 0.13, 0.30), col_red_sign)
    # ORDER HERE speaker box just below the menu board
    _make_box_local(f"{name_prefix}_MenuBoard_Speaker",
                    (mb_x, mb_y, mb_z + 1.4),
                    (0.40, 0.20, 0.50),
                    (0.42, 0.42, 0.45, 1.0))
    # Speaker grille (dark mesh)
    _make_box_local(f"{name_prefix}_MenuBoard_Grille",
                    (mb_x, mb_y - 0.13, mb_z + 1.4),
                    (0.30, 0.04, 0.30),
                    (0.18, 0.18, 0.20, 1.0))

    # ── ARROW + DRIVE THRU lane markings (white painted strips
    # at the entry of the lane)
    for k in range(3):
        ay = mb_y - 3.0 - k * 2.5
        _make_box_local(f"{name_prefix}_DTArrow_{k}",
                        (cx + w / 2 + 8.0, ay,
                         mesh_z(cx + w / 2 + 8.0, ay) + 0.055),
                        (0.60, 0.12, 0.01), COL_DTSTRIPE)

    # ── CUSTOMER PARKING LOT on the south side of the building
    _build_parking_lot(name_prefix, cx - 3.0, cy - 16.0,
                        lot_w=18.0, lot_d=18.0,
                        ground_z=mesh_z(cx - 3.0, cy - 16.0),
                        building_y_north=cy,
                        car_palette=[
                            (0.85, 0.20, 0.18, 1.0),
                            (0.62, 0.62, 0.64, 1.0),
                            (0.32, 0.55, 0.78, 1.0),
                            (0.32, 0.55, 0.25, 1.0),
                            (0.95, 0.85, 0.30, 1.0),
                        ],
                        n_handicap=1)

    # ── INTERIOR (visible through the south plate glass)
    # Order counter at the rear
    ct_x = cx
    ct_y = cy + d / 2 - 1.8
    ct_w = 6.0; ct_d = 0.9; ct_h = 1.1
    _make_box_local(f"{name_prefix}_Counter",
                    (ct_x, ct_y, ground_z + ct_h / 2),
                    (ct_w, ct_d, ct_h),
                    (0.55, 0.42, 0.30, 1.0))
    # Counter top
    _make_box_local(f"{name_prefix}_CounterTop",
                    (ct_x, ct_y, ground_z + ct_h + 0.02),
                    (ct_w + 0.10, ct_d + 0.10, 0.04),
                    (0.42, 0.32, 0.22, 1.0))
    # Register on the counter
    _make_box_local(f"{name_prefix}_Register",
                    (ct_x - 1.5, ct_y, ground_z + ct_h + 0.20),
                    (0.55, 0.40, 0.30),
                    (0.20, 0.20, 0.22, 1.0))
    # MENU BOARD over the counter (hanging from ceiling, red)
    _make_box_local(f"{name_prefix}_InteriorMenu",
                    (ct_x, ct_y + ct_d / 2 + 0.05,
                     ground_z + h - 0.7),
                    (ct_w, 0.05, 1.0),
                    (0.78, 0.18, 0.16, 1.0))
    # 3 tortilla / chip warmers on the counter
    for k, ox in enumerate((-2.4, -1.5, -0.6)):
        _make_cyl_local(f"{name_prefix}_Warmer_{k}",
                        (ct_x + ox, ct_y, ground_z + ct_h + 0.30),
                        0.20, 0.40, col_steel, segments=8)
        # Glass dome on top
        _make_sphere_low_local(f"{name_prefix}_WarmerDome_{k}",
                                (ct_x + ox, ct_y,
                                 ground_z + ct_h + 0.55),
                                0.22,
                                (0.62, 0.70, 0.78, 1.0),
                                rings=3, segments=6)
    # 4 cafe tables in the dining area + 4 chairs each
    for tk, (tx_off, ty_off) in enumerate(((-3.5, 0.8), (-1.2, 0.8),
                                            (-3.5, -1.6), (-1.2, -1.6))):
        tx = cx + tx_off
        ty = cy + ty_off
        tz = ground_z
        # Round table top
        _make_cyl_local(f"{name_prefix}_TableTop_{tk}",
                        (tx, ty, tz + 0.75),
                        0.50, 0.06,
                        (0.78, 0.74, 0.66, 1.0), segments=8)
        _make_cyl_local(f"{name_prefix}_TableStem_{tk}",
                        (tx, ty, tz + 0.40),
                        0.06, 0.70,
                        (0.62, 0.62, 0.64, 1.0), segments=6)
        # 2 chairs flanking the table
        for sgn_y, side in ((-1, 'S'), (1, 'N')):
            _make_box_local(
                f"{name_prefix}_Chair_{tk}_{side}_Seat",
                (tx, ty + sgn_y * 0.75, tz + 0.45),
                (0.40, 0.40, 0.06),
                (0.42, 0.32, 0.22, 1.0))
            _make_box_local(
                f"{name_prefix}_Chair_{tk}_{side}_Back",
                (tx, ty + sgn_y * 0.95,
                 tz + 0.75),
                (0.40, 0.06, 0.50),
                (0.42, 0.32, 0.22, 1.0))
    # Cook NPC marker (behind the counter)
    cook_x = ct_x + 0.8
    cook_y = ct_y + ct_d / 2 + 0.4
    cook_z = mesh_z(cook_x, cook_y)
    human_figure(
        name=f"NPC_{name_prefix}_Cook",
        base_x=cook_x, base_y=cook_y, base_z=cook_z,
        scale=1.0, facing='-Y',
        skin_color=(0.85, 0.65, 0.48, 1.0),
        hair_style='short',
        hair_color=(0.15, 0.10, 0.06, 1.0),
        jacket_color=(0.95, 0.94, 0.90, 1.0),
        pants_color=(0.18, 0.18, 0.22, 1.0),
        shoe_color=(0.20, 0.16, 0.14, 1.0),
        has_sunglasses=False, with_ears=True,
        with_mouth=True,
        mouth_color=(0.55, 0.22, 0.28, 1.0))
    # Drive-thru order taker NPC (just inside the window)
    dt_npc_x = cx + w / 2 - 0.6
    dt_npc_y = dt_centre_y
    dt_npc_z = mesh_z(dt_npc_x, dt_npc_y)
    human_figure(
        name=f"NPC_{name_prefix}_DTOrder",
        base_x=dt_npc_x, base_y=dt_npc_y, base_z=dt_npc_z,
        scale=1.0, facing='+X',
        skin_color=(0.92, 0.75, 0.62, 1.0),
        hair_style='short',
        hair_color=(0.20, 0.14, 0.10, 1.0),
        jacket_color=(0.78, 0.18, 0.16, 1.0),
        pants_color=(0.32, 0.32, 0.36, 1.0),
        shoe_color=(0.20, 0.16, 0.14, 1.0),
        has_sunglasses=False, with_ears=True,
        with_mouth=True,
        mouth_color=(0.55, 0.22, 0.28, 1.0))


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


def build_hs_stadium_overflow_lot():
    """Game-day overflow lot south of the HS football field. A
    big rectangular asphalt slab + parallel painted stripes —
    intentionally NO cars (it's the overflow lot, empty until
    a Friday-night game). Two ticket-booth shacks at the
    pedestrian entry from the field's south end zone.
    """
    cx, cy = 340.0, -130.0
    ground_z = mesh_z(cx, cy)
    lot_w = 80.0
    lot_d = 20.0
    hw_lot = lot_w / 2; hd_lot = lot_d / 2
    sv = []
    for (lx, ly) in [(cx - hw_lot, cy - hd_lot),
                     (cx + hw_lot, cy - hd_lot),
                     (cx + hw_lot, cy + hd_lot),
                     (cx - hw_lot, cy + hd_lot)]:
        sv.append((lx, ly, mesh_z(lx, ly) + 0.04))
    _finalize_mesh("HS_OverflowLot", sv, [[0, 1, 2, 3]],
                    (0.22, 0.22, 0.24, 1.0))
    # Paint 26 stalls (perpendicular to building) in 2 rows
    n_stalls_total = 26
    for k in range(n_stalls_total - 1):
        sx = cx - hw_lot + (k + 1) * (lot_w / n_stalls_total)
        cv = []
        for (lx, ly) in [(sx - 0.05, cy - hd_lot + 0.3),
                          (sx + 0.05, cy - hd_lot + 0.3),
                          (sx + 0.05, cy + hd_lot - 0.3),
                          (sx - 0.05, cy + hd_lot - 0.3)]:
            cv.append((lx, ly, mesh_z(lx, ly) + 0.055))
        _finalize_mesh(f"HS_OverflowStripe_{k}", cv,
                        [[0, 1, 2, 3]], (0.92, 0.90, 0.84, 1.0))
    # Ticket booths flanking the pedestrian entry (north side
    # of the lot, where the field is just north)
    for sgn, tag in ((-1, 'L'), (1, 'R')):
        tx = cx + sgn * 5.0
        ty = cy + hd_lot + 2.0
        tz = mesh_z(tx, ty)
        # Body
        _make_box_local(f"HS_TicketBooth_{tag}_Body",
                        (tx, ty, tz + 1.4),
                        (2.4, 2.0, 2.8),
                        (0.85, 0.20, 0.18, 1.0))   # red
        # Roof (slightly overhanging)
        _make_box_local(f"HS_TicketBooth_{tag}_Roof",
                        (tx, ty, tz + 2.95),
                        (2.8, 2.4, 0.20),
                        (0.32, 0.30, 0.28, 1.0))
        # Service window on the south face
        _make_box_local(f"HS_TicketBooth_{tag}_Window",
                        (tx, ty - 1.02, tz + 1.5),
                        (1.4, 0.04, 0.80),
                        (0.32, 0.42, 0.55, 1.0))


def build_ot_park_access_road():
    """Short access road from Horizon Drive (at ~ (-260, -15))
    north to the Oliver Tree Memorial Park south entry (around
    (-260, 55) where the beacon stands). Connects the park to
    the main district road network.
    """
    road_w = 6.0
    curb_w = 0.5
    COL_ROAD = (0.22, 0.22, 0.24, 1.0)
    COL_CURB = (0.78, 0.76, 0.70, 1.0)
    hw = road_w / 2
    pts = [(-260, -15), (-260, 20), (-260, 55)]
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
        _finalize_mesh(f"OTLink_Road_{i}", rv, [[0, 1, 2, 3]],
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
            _finalize_mesh(f"OTLink_Curb_{i}_{sgn:+d}", cv,
                            [[0, 1, 2, 3]], COL_CURB)
    # OT Park visitor parking lot at the road's north end, just
    # south of the beacon
    _build_parking_lot("OTParkVisitor", -260, 45,
                        lot_w=22.0, lot_d=16.0,
                        ground_z=mesh_z(-260, 45),
                        building_y_north=70,
                        car_palette=[(0.85, 0.20, 0.18, 1.0),
                                      (0.62, 0.62, 0.64, 1.0),
                                      (0.18, 0.32, 0.55, 1.0),
                                      (0.95, 0.85, 0.30, 1.0),
                                      (0.32, 0.55, 0.25, 1.0)],
                        n_handicap=2)


def build_connector_roads():
    """Short link roads connecting each neighborhood to the new
    district arterials (Harmony Blvd N-S, Horizon Dr E-W). Each
    is a thin 5 m collector road sampling mesh_z per corner.
    """
    road_w = 5.0
    curb_w = 0.4
    COL_ROAD = (0.22, 0.22, 0.24, 1.0)
    COL_CURB = (0.78, 0.76, 0.70, 1.0)
    COL_DASH = (0.95, 0.85, 0.30, 1.0)   # yellow — US convention
    # (yellow stripes separate OPPOSING traffic flows on undivided
    # 2-way roads; white separates same-direction lanes only).
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
            # 2 yellow dash marks per segment — US convention for
            # an undivided 2-way road's centerline.
            if seg_len > 5.0:
                for d_idx in range(2):
                    t = (d_idx + 0.5) / 2
                    mid_x = x0 + dxs * t
                    mid_y = y0 + dys * t
                    dash_l = 2.0
                    ddx = dxs / seg_len * dash_l / 2
                    ddy = dys / seg_len * dash_l / 2
                    dv = []
                    for (rx, ry) in [
                        (mid_x - ddx - perp_x * 0.07,
                         mid_y - ddy - perp_y * 0.07),
                        (mid_x + ddx - perp_x * 0.07,
                         mid_y + ddy - perp_y * 0.07),
                        (mid_x + ddx + perp_x * 0.07,
                         mid_y + ddy + perp_y * 0.07),
                        (mid_x - ddx + perp_x * 0.07,
                         mid_y - ddy + perp_y * 0.07),
                    ]:
                        dv.append((rx, ry, mesh_z(rx, ry) + 0.055))
                    _finalize_mesh(f"{prefix}Dash_{i}_{d_idx}", dv,
                                    [[0, 1, 2, 3]], COL_DASH)

    # Pull polylines from ROAD_CORRIDORS and smooth with Catmull-Rom
    # so connector turns read as curves, not 90° kinks. Each link
    # also extends its endpoints slightly so curbs meet flush with
    # arterial curbs.
    corridor_xys = {name: [(x, y) for (x, y, _z) in wps]
                    for (name, wps, _hw, _sh) in ROAD_CORRIDORS}
    LINK_NAMES = [
        ("P2Link",      "P2Link_"),
        ("WELink",      "WELink_"),
        ("NRLink",      "NRLink_"),
        ("ECDSLink",    "ECDSLink_"),
        ("ECommN",      "ECommN_"),
        ("ECommS",      "ECommS_"),
        ("WCommLink",   "WCommLink_"),
        ("TSLink",      "TSLink_"),
        ("DILink",      "DILink_"),
        ("CCLink",      "CCLink_"),
        # OTLink road quads are emitted by build_ot_park_access_road
        # (existing). The OTLink corridor still carves terrain.
        ("HospLink",    "HospLink_"),
        ("NXHQLink",    "NXHQLink_"),
        # Ch1Frontage road quads are emitted by build_commercial_
        # cluster (existing). The Ch1Frontage corridor still carves
        # terrain so the existing road sits on a flat platform.
    ]
    for (cname, prefix) in LINK_NAMES:
        if cname not in corridor_xys:
            continue
        pts = corridor_xys[cname]
        smoothed = _catmull_rom_2d(pts, samples_per_seg=4)
        _emit(smoothed, prefix)


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
    # Fire station moved (-200, -30) -> (-200, -42) so HorizonDr's
    # road quad (8.5m hw at y=-18.8 in this x range) doesn't reach
    # the building's north face. Old position had ~3.5m of road
    # quad inside the FireStn footprint.
    fs_cx, fs_cy = -200.0, -42.0
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


def _catmull_rom_2d(pts, samples_per_seg=8):
    """Catmull-Rom spline through a list of (x, y) waypoints. Returns
    a denser polyline whose centerline curves smoothly through each
    waypoint instead of kinking at every vertex. Used to make road
    quad emission follow the road-corridor carve as a smooth curve
    rather than a faceted polyline.

    Mirror the endpoints to anchor the spline at the first and last
    waypoint (so the result starts/ends at the same xy as input)."""
    if len(pts) < 2:
        return list(pts)
    ext = [pts[0]] + list(pts) + [pts[-1]]
    out = []
    for i in range(len(pts) - 1):
        p0 = ext[i]; p1 = ext[i + 1]; p2 = ext[i + 2]; p3 = ext[i + 3]
        for s in range(samples_per_seg):
            t = s / samples_per_seg
            t2 = t * t; t3 = t2 * t
            # Standard Catmull-Rom basis
            qx = 0.5 * (
                (2 * p1[0]) +
                (-p0[0] + p2[0]) * t +
                (2 * p0[0] - 5 * p1[0] + 4 * p2[0] - p3[0]) * t2 +
                (-p0[0] + 3 * p1[0] - 3 * p2[0] + p3[0]) * t3
            )
            qy = 0.5 * (
                (2 * p1[1]) +
                (-p0[1] + p2[1]) * t +
                (2 * p0[1] - 5 * p1[1] + 4 * p2[1] - p3[1]) * t2 +
                (-p0[1] + 3 * p1[1] - 3 * p2[1] + p3[1]) * t3
            )
            out.append((qx, qy))
    out.append(pts[-1])
    return out


def build_district_arterials():
    """Two arterials threading through HCE: HARMONY BOULEVARD
    runs north-south from the country club down to the chapter-
    one commercial cluster; HORIZON DRIVE runs east-west across
    the middle of the district connecting West Estates with the
    East CDS / high-school zone. Both are 4-lane (8 m) asphalt
    with painted yellow centerlines. Polylines come from
    ROAD_CORRIDORS so the road quad geometry stays in sync with
    the terrain carve, then are smoothed through a Catmull-Rom
    spline so curves read as curves instead of polyline kinks.
    """
    road_w = 8.0
    COL_ROAD = (0.20, 0.20, 0.22, 1.0)
    COL_CL = (0.95, 0.85, 0.30, 1.0)         # yellow centerline
    hw = road_w / 2

    COL_CURB = (0.78, 0.74, 0.66, 1.0)
    COL_EDGE = (0.95, 0.92, 0.84, 1.0)         # white edge line
    curb_w = 0.5

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
            # Curb-and-gutter on both sides of the arterial. The curb
            # ribbon stretches just outside the road edge by curb_w,
            # rising 10 cm above the asphalt. Civil-engineering
            # standard suburban arterial detail.
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
                # Solid white edge line · 0.10 m wide, just inside
                # the curb. Helps drivers see lane edges at night.
                ev = []
                edge_off = hw - 0.15
                edge_w = 0.10
                for (rx, ry) in [
                    (x0 + sgn * perp_x * (edge_off - edge_w/2),
                     y0 + sgn * perp_y * (edge_off - edge_w/2)),
                    (x1 + sgn * perp_x * (edge_off - edge_w/2),
                     y1 + sgn * perp_y * (edge_off - edge_w/2)),
                    (x1 + sgn * perp_x * (edge_off + edge_w/2),
                     y1 + sgn * perp_y * (edge_off + edge_w/2)),
                    (x0 + sgn * perp_x * (edge_off + edge_w/2),
                     y0 + sgn * perp_y * (edge_off + edge_w/2)),
                ]:
                    ev.append((rx, ry, mesh_z(rx, ry) + 0.045))
                _finalize_mesh(f"{prefix}EdgeLine_{i}_{sgn:+d}", ev,
                                [[0, 1, 2, 3]], COL_EDGE)
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

    # Pull polylines straight from ROAD_CORRIDORS so the road
    # geometry matches the terrain carve waypoints exactly. Then
    # Catmull-Rom smooth so the road curves through each waypoint
    # instead of cornering. Smoothed samples are dense enough
    # (8 per input segment, plus the input is already <=40m
    # segments) that the road reads as continuously curving.
    corridor_xys = {name: [(x, y) for (x, y, _z) in wps]
                    for (name, wps, _hw, _sh) in ROAD_CORRIDORS}
    harmony_blvd = _catmull_rom_2d(corridor_xys["HarmonyBlvd"],
                                    samples_per_seg=4)
    horizon_dr = _catmull_rom_2d(corridor_xys["HorizonDr"],
                                  samples_per_seg=4)
    _emit_arterial(harmony_blvd, "HarmonyBlvd_")
    _emit_arterial(horizon_dr, "HorizonDr_")


def build_wild_zone_trees():
    """Scatter ~40 trees deterministically across the wild zones
    BETWEEN settlements so the district doesn't read as empty
    grass between built areas.
    """
    COL_OAK_TRUNK = (0.30, 0.22, 0.16, 1.0)
    COL_OAK_CANOPY = (0.30, 0.55, 0.25, 1.0)
    COL_PINE_TRUNK = (0.32, 0.22, 0.14, 1.0)
    COL_PINE_CANOPY = (0.18, 0.42, 0.20, 1.0)

    # Deterministic positions scattered in wild zones
    tree_specs = [
        # (x, y, kind)
        # NW wild between NorthRanch and Country Club
        (-380, 320, 'oak'), (-280, 320, 'pine'), (-180, 320, 'oak'),
        (-100, 320, 'pine'),
        # N wild around CC north
        (-360, 420, 'oak'), (-200, 430, 'pine'),
        (150, 430, 'pine'), (300, 420, 'oak'),
        # NE wild between EastCDS and CC
        (380, 290, 'pine'), (380, 320, 'oak'),
        # E wild east of EastCDS
        (480, 200, 'oak'), (480, 140, 'pine'),
        # SE wild between Phase 2 and EastComm
        (300, -80, 'oak'), (380, -80, 'pine'),
        (300, -200, 'oak'), (380, -200, 'oak'),
        # S wild between Phase 2 and SouthComm
        (100, -300, 'pine'), (180, -300, 'oak'),
        (-50, -320, 'pine'), (-180, -310, 'oak'),
        # SW wild west of Phase 3
        (-440, -340, 'pine'), (-360, -340, 'oak'),
        (-260, -340, 'pine'),
        # W wild between WestEstates and WestComm
        (-500, -120, 'oak'), (-500, -240, 'pine'),
        (-490, 0, 'oak'),
        # NW wild between NorthRanch and OliverTree
        (-180, 280, 'pine'), (-100, 240, 'oak'),
        # Between OTPark and HarmonyPark
        (-160, 160, 'pine'), (-200, 100, 'oak'),
        # Between PHs and chapter-1
        (-350, -90, 'oak'), (-250, -90, 'pine'),
        # E between EastCDS and HSField
        (260, 60, 'oak'), (320, 0, 'pine'),
        # Around drive-in
        (60, -250, 'pine'), (240, -260, 'oak'),
        # Random distributed
        (-410, 320, 'oak'), (-90, 110, 'pine'),
        (160, 140, 'oak'), (380, 120, 'pine'),
    ]
    for k, (tx, ty, kind) in enumerate(tree_specs):
        tz = mesh_z(tx, ty)
        seed = (int(tx) * 17 + int(ty) * 31) % 100
        trunk_h = 4.5 + (seed % 4) * 0.6
        canopy_r = 2.4 + ((seed // 5) % 3) * 0.4
        if kind == 'oak':
            _make_cyl_local(f"WildTree_{k}_Trunk",
                            (tx, ty, tz + trunk_h / 2),
                            0.30, trunk_h, COL_OAK_TRUNK, segments=6)
            _make_sphere_low_local(
                f"WildTree_{k}_Canopy",
                (tx, ty, tz + trunk_h + canopy_r * 0.55),
                canopy_r, COL_OAK_CANOPY,
                rings=3, segments=8)
        else:
            # PINE — taller, narrower, more conical
            _make_cyl_local(f"WildTree_{k}_Trunk",
                            (tx, ty, tz + trunk_h / 2),
                            0.24, trunk_h, COL_PINE_TRUNK, segments=6)
            # Conical canopy (approximated as 3 stacked tapered cylinders)
            _make_cyl_local(f"WildTree_{k}_Canopy1",
                            (tx, ty, tz + trunk_h + 0.5),
                            canopy_r, 1.6, COL_PINE_CANOPY, segments=6)
            _make_cyl_local(f"WildTree_{k}_Canopy2",
                            (tx, ty, tz + trunk_h + 2.0),
                            canopy_r * 0.7, 1.4, COL_PINE_CANOPY, segments=6)
            _make_cyl_local(f"WildTree_{k}_Canopy3",
                            (tx, ty, tz + trunk_h + 3.2),
                            canopy_r * 0.4, 1.0, COL_PINE_CANOPY, segments=6)


def build_community_garden():
    """Community garden in HarmonyPark west of the playground.
    8 raised wood-edge beds in a 4×2 grid plus a small tool
    shed and a watering-can stand.
    """
    cx, cy = -60.0, 30.0
    ground_z = mesh_z(cx, cy)
    col_wood = (0.42, 0.30, 0.20, 1.0)
    col_soil = (0.32, 0.22, 0.16, 1.0)
    col_green = (0.30, 0.55, 0.25, 1.0)
    col_red = (0.85, 0.25, 0.22, 1.0)   # tomato red, etc.
    col_path = (0.62, 0.55, 0.45, 1.0)
    bed_w, bed_d = 3.0, 1.6
    # Layout 4 wide x 2 deep with 1 m path between
    for r in range(2):
        for c in range(4):
            bcx = cx - 7.5 + c * (bed_w + 1.0)
            bcy = cy - 2.0 + r * (bed_d + 1.0)
            bcz = mesh_z(bcx, bcy)
            # Bed wood edge (a low box ring)
            _make_box_local(f"CG_BedEdge_{r}_{c}",
                            (bcx, bcy, bcz + 0.20),
                            (bed_w, bed_d, 0.40), col_wood)
            # Soil interior
            _make_box_local(f"CG_BedSoil_{r}_{c}",
                            (bcx, bcy, bcz + 0.35),
                            (bed_w - 0.2, bed_d - 0.2, 0.10),
                            col_soil)
            # Plants — green sprouts (3 rows of small green boxes)
            for pr in range(3):
                for pc in range(5):
                    px = bcx - bed_w / 2 + 0.3 + pc * (bed_w - 0.6) / 4
                    py = bcy - bed_d / 2 + 0.3 + pr * (bed_d - 0.6) / 2
                    # Alternate plant colors
                    pcol = col_red if (pr + pc) % 4 == 0 else col_green
                    _make_box_local(
                        f"CG_Plant_{r}_{c}_{pr}_{pc}",
                        (px, py, bcz + 0.55),
                        (0.20, 0.20, 0.30), pcol)
    # Gravel path between rows
    _make_box_local("CG_PathHoriz",
                    (cx, cy + bed_d / 2 + 0.5, ground_z + 0.05),
                    (4 * bed_w + 3 * 1.0, 1.0, 0.10), col_path)
    # Tool shed at the west end
    sh_x = cx - 16.0
    sh_y = cy
    sh_z = mesh_z(sh_x, sh_y)
    _make_box_local("CG_ToolShed_Walls",
                    (sh_x, sh_y, sh_z + 1.4),
                    (3.6, 3.0, 2.8), col_wood)
    _make_box_local("CG_ToolShed_Roof",
                    (sh_x, sh_y, sh_z + 2.95),
                    (4.0, 3.4, 0.20), (0.32, 0.30, 0.28, 1.0))
    _make_box_local("CG_ToolShed_Door",
                    (sh_x, sh_y - 3.0 / 2 + 0.05, sh_z + 1.1),
                    (0.80, 0.06, 2.0), (0.42, 0.20, 0.16, 1.0))
    # Water spigot post in the middle of the garden
    _make_cyl_local("CG_Spigot_Post",
                    (cx, cy - bed_d / 2 - 0.4, ground_z + 0.6),
                    0.06, 1.2,
                    (0.62, 0.62, 0.64, 1.0), segments=4)
    # Watering can on a small bench
    _make_box_local("CG_Bench",
                    (cx - bed_w * 1.0, cy + bed_d + 1.5,
                     ground_z + 0.42),
                    (1.6, 0.42, 0.06), col_wood)


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


def build_country_club_lot():
    """Country Club valet lot east of the clubhouse + curving
    cobblestone driveway from Harmony Boulevard's north end.
    """
    # ── VALET LOT east of the clubhouse
    cc_lot_cx = 30.0   # clubhouse spans cx-18..+18, lot east of that
    cc_lot_cy = 370.0
    _build_parking_lot("CCValet", cc_lot_cx + 30.0, cc_lot_cy - 4.0,
                        lot_w=22.0, lot_d=18.0,
                        ground_z=mesh_z(cc_lot_cx + 30.0,
                                         cc_lot_cy - 4.0),
                        building_y_north=cc_lot_cy,
                        car_palette=[
                            (0.20, 0.20, 0.22, 1.0),  # black
                            (0.62, 0.62, 0.64, 1.0),  # silver
                            (0.85, 0.20, 0.18, 1.0),  # red (member roadster)
                            (0.18, 0.32, 0.55, 1.0),  # navy
                            (0.92, 0.92, 0.90, 1.0),  # white
                        ],
                        n_handicap=1)

    # ── COBBLESTONE DRIVEWAY from Harmony Blvd (0, 340) to the
    # clubhouse portico front (0, 358 — south of clubhouse)
    COL_COBBLE = (0.62, 0.55, 0.45, 1.0)
    pts = [(0, 340), (0, 350), (5, 358)]
    hw = 4.0
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
            rv.append((rx, ry, mesh_z(rx, ry) + 0.05))
        _finalize_mesh(f"CC_Driveway_{i}", rv, [[0, 1, 2, 3]],
                        COL_COBBLE)
    # Turnaround circle in front of the portico
    tc_x, tc_y = 0.0, 358.0
    tc_r = 8.0
    segs = 12
    tc_verts = [(tc_x, tc_y, mesh_z(tc_x, tc_y) + 0.05)]
    for i in range(segs):
        ang = 2.0 * math.pi * i / segs
        vx = tc_x + math.cos(ang) * tc_r
        vy = tc_y + math.sin(ang) * tc_r
        tc_verts.append((vx, vy, mesh_z(vx, vy) + 0.05))
    tc_faces = []
    for i in range(segs):
        ni = (i + 1) % segs
        tc_faces.append([0, 1 + i, 1 + ni])
    _finalize_mesh("CC_Turnaround", tc_verts, tc_faces, COL_COBBLE)
    # Centre planter (small circular flower bed at the centre of
    # the turnaround)
    _make_cyl_local("CC_TurnPlanter",
                    (tc_x, tc_y, mesh_z(tc_x, tc_y) + 0.15),
                    1.6, 0.30,
                    (0.62, 0.42, 0.28, 1.0), segments=10)
    _make_sphere_low_local("CC_TurnFlowers",
                            (tc_x, tc_y, mesh_z(tc_x, tc_y) + 0.55),
                            1.3, (0.95, 0.42, 0.62, 1.0),
                            rings=3, segments=8)


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


def build_nexcorp_model_home():
    """NexCorp Residential Solutions MODEL HOME — the Sunday-
    open showpiece NexCorp uses to sell HCE lots. Per
    lore/_COMMUNITY_PLANNED_LORE.md:
      · "their first home at Lot 47"
      · "the basil pot at the model home is fake"
      · "model-home open Sunday"
      · "the model-home scheme — the wrong-address mail
        apparatus that funnels HCE deeds toward NexCorp shells"

    Placed at Lot 47 in NorthRanch (the NW prosperous tier) on
    Aspen Street's north side. Larger than the other NR houses,
    in a brick + multi-gable style matching the suburb reference
    photos. Tagged with a MODEL HOME yard sign + NEXCORP banner
    + open front door + visible "fake basil pot" on the porch.
    """
    cx, cy = -340.0, 218.0     # Lot 47 — NR Aspen north side
    ground_z = mesh_z(cx, cy)

    # Two-story silhouette with bigger footprint than the
    # standard suburban house. Brick + front-loaded garage.
    col_brick = (0.55, 0.32, 0.22, 1.0)        # red brick
    col_brick_alt = (0.62, 0.42, 0.28, 1.0)    # lighter brick accent
    col_trim_cream = (0.92, 0.90, 0.84, 1.0)
    col_roof_dark = (0.32, 0.30, 0.28, 1.0)
    col_door_navy = (0.18, 0.32, 0.55, 1.0)
    col_garage_white = (0.92, 0.90, 0.84, 1.0)
    col_window_warm = (0.42, 0.50, 0.62, 1.0)

    main_w = 11.0
    main_d = 9.0
    main_h = 6.0      # 2-story
    gar_w = 6.0
    gar_d = 7.0
    gar_h = 3.5

    # ── SLAB (covers both main house + front-loaded garage)
    slab_w = main_w + 0.4
    slab_d = main_d + gar_d + 0.4
    _make_box_local("ModelHome_Slab",
                    (cx + 0.3, cy + (main_d - gar_d) / 2,
                     ground_z + 0.05),
                    (slab_w + 4.0, slab_d, 0.10), col_trim_cream)

    # ── MAIN HOUSE (north, 2-story) — brick body
    main_cx = cx
    main_cy = cy + 2.0    # main pushed north; garage in front
    _make_box_local("ModelHome_Main",
                    (main_cx, main_cy, ground_z + main_h / 2),
                    (main_w, main_d, main_h), col_brick)
    # Brick-trim band at first-floor / second-floor break
    _make_box_local("ModelHome_BrickBand",
                    (main_cx, main_cy - main_d / 2 - 0.02,
                     ground_z + 3.0),
                    (main_w + 0.10, 0.06, 0.18), col_brick_alt)

    # ── MULTI-GABLE ROOF — front gable peak (over the garage
    # side) + larger main hip-style roof behind. Approximate
    # with two stacked pitched roofs.
    main_ridge_h = 2.6
    main_rverts = [
        (main_cx - main_w / 2 - 0.30,
         main_cy - main_d / 2 - 0.30, ground_z + main_h),
        (main_cx + main_w / 2 + 0.30,
         main_cy - main_d / 2 - 0.30, ground_z + main_h),
        (main_cx + main_w / 2 + 0.30,
         main_cy + main_d / 2 + 0.30, ground_z + main_h),
        (main_cx - main_w / 2 - 0.30,
         main_cy + main_d / 2 + 0.30, ground_z + main_h),
        (main_cx - main_w / 2 - 0.30, main_cy,
         ground_z + main_h + main_ridge_h),
        (main_cx + main_w / 2 + 0.30, main_cy,
         ground_z + main_h + main_ridge_h),
    ]
    main_rfaces = [[0, 1, 5, 4], [3, 4, 5, 2],
                   [0, 4, 3], [1, 2, 5]]
    _finalize_mesh("ModelHome_MainRoof", main_rverts, main_rfaces,
                    col_roof_dark)
    # FRONT GABLE — smaller pitched peak above the garage
    fg_w = 5.5
    fg_d = 3.0
    fg_base_z = ground_z + main_h + 0.5
    fg_ridge_h = 1.8
    fg_cx = main_cx + 2.5    # offset east
    fg_cy = main_cy - main_d / 2 - 0.5
    fg_rverts = [
        (fg_cx - fg_w / 2, fg_cy - fg_d / 2, fg_base_z),
        (fg_cx + fg_w / 2, fg_cy - fg_d / 2, fg_base_z),
        (fg_cx + fg_w / 2, fg_cy + fg_d / 2, fg_base_z),
        (fg_cx - fg_w / 2, fg_cy + fg_d / 2, fg_base_z),
        (fg_cx, fg_cy - fg_d / 2, fg_base_z + fg_ridge_h),
        (fg_cx, fg_cy + fg_d / 2, fg_base_z + fg_ridge_h),
    ]
    fg_rfaces = [[0, 1, 5, 4], [3, 4, 5, 2],
                 [0, 4, 3], [1, 2, 5]]
    _finalize_mesh("ModelHome_FrontGable", fg_rverts, fg_rfaces,
                    col_roof_dark)

    # ── FRONT DOOR (centred on south face of main)
    door_w = 1.2; door_h = 2.4
    door_cx = main_cx - 2.5     # west of front gable
    door_y = main_cy - main_d / 2 + 0.02
    # Door (slightly ajar — open-house impression by NOT closing)
    _make_box_local("ModelHome_Door",
                    (door_cx, door_y - 0.05,
                     ground_z + door_h / 2),
                    (door_w, 0.06, door_h - 0.10),
                    col_door_navy)
    # Door header
    _make_box_local("ModelHome_DoorHeader",
                    (door_cx, door_y, ground_z + door_h + 0.20),
                    (door_w + 0.40, 0.12, 0.40),
                    col_trim_cream)
    # Door frame / surround
    for sgn in (-1, 1):
        _make_box_local(f"ModelHome_DoorFrame_{sgn:+d}",
                        (door_cx + sgn * (door_w / 2 + 0.10),
                         door_y, ground_z + door_h / 2),
                        (0.12, 0.10, door_h + 0.20),
                        col_trim_cream)

    # ── FRONT WINDOWS · 4 windows (2 on first floor, 2 on
    # second floor, west side of front gable)
    for floor in (0, 1):
        z_win = ground_z + 1.6 + floor * 3.0
        for k in range(2):
            wx = main_cx - main_w / 2 + 1.5 + k * 2.5
            if wx > door_cx + 1.0:
                continue   # skip if would be on door area
            _make_box_local(f"ModelHome_Window_{floor}_{k}",
                            (wx, main_cy - main_d / 2 + 0.02,
                             z_win),
                            (1.4, 0.04, 1.4), col_window_warm)
            # Window shutters (decorative)
            for sgn in (-1, 1):
                _make_box_local(
                    f"ModelHome_Shutter_{floor}_{k}_{sgn:+d}",
                    (wx + sgn * 0.85,
                     main_cy - main_d / 2 + 0.04,
                     z_win),
                    (0.16, 0.04, 1.4),
                    col_door_navy)
    # Window on the east side of front gable (above garage)
    _make_box_local("ModelHome_Window_E_upper",
                    (main_cx + 3.0, main_cy - main_d / 2 + 0.02,
                     ground_z + 4.6),
                    (1.2, 0.04, 1.2), col_window_warm)

    # ── PORCH COVER over the front door
    _make_box_local("ModelHome_PorchRoof",
                    (door_cx, main_cy - main_d / 2 - 1.0,
                     ground_z + door_h + 0.55),
                    (door_w + 1.6, 2.0, 0.12), col_trim_cream)
    # Porch posts (2 white columns)
    for sgn in (-1, 1):
        _make_cyl_local(f"ModelHome_PorchPost_{sgn:+d}",
                        (door_cx + sgn * (door_w / 2 + 0.6),
                         main_cy - main_d / 2 - 1.8,
                         ground_z + door_h / 2 + 0.20),
                        0.10, door_h + 0.40,
                        col_trim_cream, segments=6)
    # PORCH SLAB
    _make_box_local("ModelHome_PorchSlab",
                    (door_cx, main_cy - main_d / 2 - 1.0,
                     ground_z + 0.12),
                    (door_w + 1.6, 2.0, 0.10),
                    (0.78, 0.74, 0.66, 1.0))
    # Welcome mat
    _make_box_local("ModelHome_WelcomeMat",
                    (door_cx, main_cy - main_d / 2 - 0.30,
                     ground_z + 0.18),
                    (door_w + 0.40, 0.60, 0.02),
                    (0.32, 0.22, 0.18, 1.0))
    # FAKE BASIL POT (canonical detail) — small terracotta pot
    # with cubic green sprouts on the porch
    _make_cyl_local("ModelHome_BasilPot",
                    (door_cx + 1.0,
                     main_cy - main_d / 2 - 0.50,
                     ground_z + 0.30),
                    0.18, 0.30,
                    (0.78, 0.45, 0.25, 1.0), segments=8)
    _make_sphere_low_local("ModelHome_BasilSprouts",
                            (door_cx + 1.0,
                             main_cy - main_d / 2 - 0.50,
                             ground_z + 0.50),
                            0.22, (0.32, 0.55, 0.25, 1.0),
                            rings=3, segments=6)

    # ── FRONT-LOADED GARAGE (south of main, attached) — single
    # big roll-up door visible to the street
    gar_cx = main_cx + 2.5
    gar_cy = main_cy - main_d / 2 - gar_d / 2 - 0.20
    _make_box_local("ModelHome_Garage",
                    (gar_cx, gar_cy, ground_z + gar_h / 2),
                    (gar_w, gar_d, gar_h), col_brick)
    # Garage flat roof
    _make_box_local("ModelHome_GarageRoof",
                    (gar_cx, gar_cy, ground_z + gar_h + 0.10),
                    (gar_w + 0.30, gar_d + 0.30, 0.20),
                    col_roof_dark)
    # Garage door (south face)
    _make_box_local("ModelHome_GarageDoor",
                    (gar_cx, gar_cy - gar_d / 2 + 0.05,
                     ground_z + (gar_h - 0.4) / 2 + 0.10),
                    (gar_w - 0.6, 0.06, gar_h - 0.5),
                    col_garage_white)
    # Garage window strip above door
    _make_box_local("ModelHome_GarageWindow",
                    (gar_cx, gar_cy - gar_d / 2 + 0.04,
                     ground_z + gar_h - 0.20),
                    (gar_w - 0.8, 0.04, 0.20),
                    col_window_warm)

    # ── DRIVEWAY from garage to the curb (Aspen Street at y=200)
    drive_apron_x = gar_cx
    drive_apron_y = gar_cy - gar_d / 2
    drive_curb_y = 200 + 3.5     # curb edge of Aspen
    drive_w = 5.0
    drive_hw = drive_w / 2
    drive_verts = [
        (drive_apron_x - drive_hw, drive_apron_y,
         mesh_z(drive_apron_x - drive_hw, drive_apron_y) + 0.04),
        (drive_apron_x + drive_hw, drive_apron_y,
         mesh_z(drive_apron_x + drive_hw, drive_apron_y) + 0.04),
        (drive_apron_x + drive_hw, drive_curb_y,
         mesh_z(drive_apron_x + drive_hw, drive_curb_y) + 0.04),
        (drive_apron_x - drive_hw, drive_curb_y,
         mesh_z(drive_apron_x - drive_hw, drive_curb_y) + 0.04),
    ]
    _finalize_mesh("ModelHome_Driveway", drive_verts,
                    [[0, 1, 2, 3]], (0.78, 0.76, 0.72, 1.0))

    # ── "MODEL HOME · TOUR SUNDAY" YARD SIGN at the curb
    sign_x = drive_apron_x - drive_hw - 3.0
    sign_y = drive_curb_y - 0.5
    sign_z = mesh_z(sign_x, sign_y)
    # 2 small posts in the ground
    for sgn in (-1, 1):
        _make_box_local(f"ModelHome_YardSignPost_{sgn:+d}",
                        (sign_x + sgn * 0.55, sign_y,
                         sign_z + 0.85),
                        (0.06, 0.06, 1.70),
                        (0.42, 0.30, 0.20, 1.0))
    # Big sign panel (TOUR SUNDAY)
    _make_box_local("ModelHome_YardSign_Panel",
                    (sign_x, sign_y, sign_z + 1.40),
                    (1.40, 0.05, 0.90),
                    (0.18, 0.32, 0.55, 1.0))
    # Panel border trim
    _make_box_local("ModelHome_YardSign_Trim",
                    (sign_x, sign_y, sign_z + 1.40),
                    (1.46, 0.06, 0.96),
                    (0.95, 0.92, 0.86, 1.0))
    # NexCorp company-logo strip at the bottom of the sign
    _make_box_local("ModelHome_YardSign_NexCorp",
                    (sign_x, sign_y - 0.02, sign_z + 0.95),
                    (1.30, 0.06, 0.30),
                    (0.85, 0.20, 0.18, 1.0))

    # ── NEXCORP BANNER mounted on the front porch railing
    _make_box_local("ModelHome_NexCorpBanner",
                    (door_cx, main_cy - main_d / 2 - 0.10,
                     ground_z + door_h + 1.0),
                    (3.0, 0.06, 0.40),
                    (0.18, 0.32, 0.55, 1.0))

    # ── HEDGE BORDER along the south of the front yard
    _make_box_local("ModelHome_Hedge_S",
                    (cx + 0.3,
                     (main_cy - main_d / 2 + drive_curb_y) / 2 - 5.0,
                     ground_z + 0.40),
                    (slab_w + 4.0, 0.50, 0.80),
                    (0.20, 0.42, 0.18, 1.0))


def build_nexcorp_sales_trailer():
    """NexCorp Residential Solutions sales TRAILER — temporary
    on-site sales office near the model home. Single-wide
    rectangular trailer with NEXCORP branding, accessibility
    ramp, and a small visitor lot. Per the lore: NexCorp is
    aggressively selling HCE lots from this trailer ("NexCorp
    Residential Solutions has been mailing brochures to ...").
    """
    cx, cy = -300.0, 218.0    # west of the model home on Aspen
    ground_z = mesh_z(cx, cy)
    # Trailer body (a single-wide rectangular building on
    # cinder-block stilts)
    trailer_w = 12.0
    trailer_d = 4.0
    trailer_h = 3.0
    floor_z = 0.50    # stilts raise the floor
    col_trailer = (0.85, 0.85, 0.82, 1.0)
    col_trim = (0.18, 0.32, 0.55, 1.0)
    col_roof = (0.42, 0.42, 0.45, 1.0)
    col_door = (0.85, 0.20, 0.18, 1.0)
    # Stilts (cinder-block piers)
    for sgn_x in (-1, 1):
        for sgn_y in (-1, 1):
            _make_box_local(
                f"Sales_Stilt_{sgn_x:+d}_{sgn_y:+d}",
                (cx + sgn_x * (trailer_w / 2 - 0.4),
                 cy + sgn_y * (trailer_d / 2 - 0.4),
                 ground_z + floor_z / 2),
                (0.40, 0.40, floor_z),
                (0.62, 0.62, 0.64, 1.0))
    # Trailer body
    _make_box_local("Sales_Trailer_Body",
                    (cx, cy, ground_z + floor_z + trailer_h / 2),
                    (trailer_w, trailer_d, trailer_h), col_trailer)
    # Blue trim band along south face
    _make_box_local("Sales_Trailer_TrimBand",
                    (cx, cy - trailer_d / 2 - 0.02,
                     ground_z + floor_z + trailer_h - 0.40),
                    (trailer_w, 0.06, 0.30), col_trim)
    # Flat roof (slightly sloped tar paper)
    _make_box_local("Sales_Trailer_Roof",
                    (cx, cy, ground_z + floor_z + trailer_h + 0.05),
                    (trailer_w + 0.20, trailer_d + 0.20, 0.10),
                    col_roof)
    # Front door (south face, west-of-centre)
    dw, dh = 1.0, 2.0
    door_cx = cx - 3.0
    _make_box_local("Sales_Trailer_Door",
                    (door_cx, cy - trailer_d / 2 + 0.04,
                     ground_z + floor_z + dh / 2),
                    (dw, 0.06, dh), col_door)
    # 2 windows east of the door
    for k in range(2):
        wx = cx + 0.5 + k * 2.2
        _make_box_local(f"Sales_Trailer_Window_{k}",
                        (wx, cy - trailer_d / 2 + 0.04,
                         ground_z + floor_z + 1.5),
                        (1.4, 0.04, 1.0),
                        (0.42, 0.50, 0.62, 1.0))
    # ACCESSIBILITY RAMP from ground to floor (south of door)
    ramp_x = door_cx
    ramp_y0 = cy - trailer_d / 2
    ramp_y1 = ramp_y0 - 2.5
    ramp_verts = [
        (ramp_x - 1.0, ramp_y0,
         mesh_z(ramp_x - 1.0, ramp_y0) + 0.04 + floor_z),
        (ramp_x + 1.0, ramp_y0,
         mesh_z(ramp_x + 1.0, ramp_y0) + 0.04 + floor_z),
        (ramp_x + 1.0, ramp_y1,
         mesh_z(ramp_x + 1.0, ramp_y1) + 0.04),
        (ramp_x - 1.0, ramp_y1,
         mesh_z(ramp_x - 1.0, ramp_y1) + 0.04),
    ]
    _finalize_mesh("Sales_Trailer_Ramp", ramp_verts,
                    [[0, 1, 2, 3]],
                    (0.62, 0.55, 0.45, 1.0))
    # RAMP HANDRAIL on both sides
    for sgn in (-1, 1):
        for k in range(2):
            rail_y = ramp_y1 + k * 2.5
            _make_cyl_local(
                f"Sales_Trailer_RailPost_{sgn:+d}_{k}",
                (ramp_x + sgn * 1.0, rail_y,
                 ground_z + floor_z * (k + 0.0) + 0.5),
                0.04, 1.0,
                (0.62, 0.62, 0.64, 1.0), segments=4)

    # ── BIG NEXCORP SIGN on the trailer's roof
    _make_box_local("Sales_Trailer_RooftopSign",
                    (cx, cy - trailer_d / 2 - 0.20,
                     ground_z + floor_z + trailer_h + 1.4),
                    (8.0, 0.14, 1.4), col_trim)

    # ── 4-car visitor lot south of the trailer
    _build_parking_lot("Sales_Trailer", cx, cy - 10.0,
                        lot_w=14.0, lot_d=14.0,
                        ground_z=mesh_z(cx, cy - 10.0),
                        building_y_north=cy,
                        car_palette=[
                            (0.62, 0.62, 0.64, 1.0),
                            (0.85, 0.20, 0.18, 1.0),
                            (0.18, 0.32, 0.55, 1.0),
                        ],
                        n_handicap=1)


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
    cedar = [(-440, 40),  (-380, 40),  (-320, 40),  (-240, 40)]
    # North-south spur connecting Aspen + Birch + Cedar at x=-320
    spur = [(-320, 200), (-320, 100), (-320, 40)]
    _emit_road_polyline(aspen, "NRAspen_")
    _emit_road_polyline(birch, "NRBirch_")
    _emit_road_polyline(cedar, "NRCedar_")
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
    for street_name, street_pts in (("Aspen", aspen),
                                      ("Birch", birch),
                                      ("Cedar", cedar)):
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


def build_west_estates_townhouses():
    """Row of 6 connected townhouses in WestEstates — shared
    walls, 3-color palette, individual front doors + garages.
    Adds residential density to the lowland zone.
    """
    cx_start = -260.0
    cy = -100.0
    ground_z = mesh_z(cx_start, cy)
    unit_w = 7.0
    unit_d = 12.0
    unit_h = 5.0
    palettes = [
        {'wall': (0.78, 0.68, 0.55, 1.0),
         'roof': (0.42, 0.30, 0.22, 1.0),
         'door': (0.42, 0.20, 0.16, 1.0)},
        {'wall': (0.62, 0.68, 0.78, 1.0),
         'roof': (0.32, 0.22, 0.18, 1.0),
         'door': (0.32, 0.18, 0.16, 1.0)},
        {'wall': (0.72, 0.78, 0.68, 1.0),
         'roof': (0.55, 0.30, 0.22, 1.0),
         'door': (0.20, 0.32, 0.18, 1.0)},
    ]
    # Shared slab
    total_w = 6 * unit_w
    _make_box_local("TH_Slab",
                    (cx_start + total_w / 2 - unit_w / 2, cy,
                     ground_z + 0.05),
                    (total_w + 0.4, unit_d + 0.4, 0.10),
                    (0.78, 0.74, 0.66, 1.0))
    # Back wall — single continuous box (saves geometry)
    _make_box_local("TH_BackWall",
                    (cx_start + total_w / 2 - unit_w / 2,
                     cy + unit_d / 2 - 0.10, ground_z + unit_h / 2),
                    (total_w, 0.20, unit_h),
                    (0.78, 0.68, 0.55, 1.0))
    # End walls (left + right)
    _make_box_local("TH_EndWall_L",
                    (cx_start - unit_w / 2 + 0.10, cy,
                     ground_z + unit_h / 2),
                    (0.20, unit_d, unit_h),
                    (0.78, 0.68, 0.55, 1.0))
    _make_box_local("TH_EndWall_R",
                    (cx_start + total_w - unit_w / 2 - 0.10, cy,
                     ground_z + unit_h / 2),
                    (0.20, unit_d, unit_h),
                    (0.78, 0.68, 0.55, 1.0))
    # Per-unit: front wall (south), garage, door, window, roof
    for k in range(6):
        ucx = cx_start + k * unit_w
        pal = palettes[k % len(palettes)]
        # Front wall (split for door + garage door)
        garage_w = 2.6
        ped_w = 1.0     # pedestrian front door
        side_l = (unit_w - garage_w - ped_w) / 2 - 0.20
        # Side L
        _make_box_local(f"TH_{k}_FrontWall_L",
                        (ucx - unit_w / 2 + side_l / 2,
                         cy - unit_d / 2 + 0.10,
                         ground_z + unit_h / 2),
                        (side_l, 0.20, unit_h), pal['wall'])
        # Pedestrian door
        _make_box_local(f"TH_{k}_PedDoor",
                        (ucx - unit_w / 2 + side_l + ped_w / 2,
                         cy - unit_d / 2 + 0.05,
                         ground_z + 1.05),
                        (ped_w - 0.10, 0.06, 2.10), pal['door'])
        _make_box_local(f"TH_{k}_PedDoorHeader",
                        (ucx - unit_w / 2 + side_l + ped_w / 2,
                         cy - unit_d / 2 + 0.10,
                         ground_z + 2.10 + (unit_h - 2.10) / 2),
                        (ped_w, 0.20, unit_h - 2.10), pal['wall'])
        # Side mid (between ped door and garage)
        side_mid_w = 0.6
        _make_box_local(f"TH_{k}_FrontWall_Mid",
                        (ucx - unit_w / 2 + side_l + ped_w +
                         side_mid_w / 2,
                         cy - unit_d / 2 + 0.10,
                         ground_z + unit_h / 2),
                        (side_mid_w, 0.20, unit_h), pal['wall'])
        # Garage door
        garage_h = 2.4
        _make_box_local(f"TH_{k}_GarageDoor",
                        (ucx - unit_w / 2 + side_l + ped_w +
                         side_mid_w + garage_w / 2,
                         cy - unit_d / 2 + 0.05,
                         ground_z + garage_h / 2),
                        (garage_w, 0.06, garage_h),
                        (0.92, 0.92, 0.90, 1.0))
        _make_box_local(f"TH_{k}_GarageHeader",
                        (ucx - unit_w / 2 + side_l + ped_w +
                         side_mid_w + garage_w / 2,
                         cy - unit_d / 2 + 0.10,
                         ground_z + garage_h + (unit_h - garage_h) / 2),
                        (garage_w, 0.20, unit_h - garage_h),
                        pal['wall'])
        # Side R (east edge of unit before next unit's wall)
        side_r = unit_w - side_l - ped_w - side_mid_w - garage_w
        if side_r > 0.05:
            _make_box_local(f"TH_{k}_FrontWall_R",
                            (ucx + unit_w / 2 - side_r / 2 - 0.20,
                             cy - unit_d / 2 + 0.10,
                             ground_z + unit_h / 2),
                            (side_r, 0.20, unit_h), pal['wall'])
        # Window on the side L (above the door height)
        _make_box_local(f"TH_{k}_Window",
                        (ucx - unit_w / 2 + side_l / 2,
                         cy - unit_d / 2 + 0.04,
                         ground_z + 3.4),
                        (side_l * 0.8, 0.04, 1.0),
                        (0.32, 0.42, 0.55, 1.0))
        # Per-unit roof panel
        _make_box_local(f"TH_{k}_Roof",
                        (ucx, cy, ground_z + unit_h + 0.10),
                        (unit_w + 0.10, unit_d + 0.10, 0.20),
                        pal['roof'])
        # Driveway from garage to a curb 12 m south
        drive_apron_x = (ucx - unit_w / 2 + side_l + ped_w +
                          side_mid_w + garage_w / 2)
        drive_apron_y = cy - unit_d / 2
        curb_y = drive_apron_y - 10.0
        verts = [(drive_apron_x - 1.8, drive_apron_y,
                  mesh_z(drive_apron_x - 1.8, drive_apron_y) + 0.04),
                  (drive_apron_x + 1.8, drive_apron_y,
                   mesh_z(drive_apron_x + 1.8, drive_apron_y) + 0.04),
                  (drive_apron_x + 1.8, curb_y,
                   mesh_z(drive_apron_x + 1.8, curb_y) + 0.04),
                  (drive_apron_x - 1.8, curb_y,
                   mesh_z(drive_apron_x - 1.8, curb_y) + 0.04)]
        _finalize_mesh(f"TH_{k}_Drive", verts, [[0, 1, 2, 3]],
                        (0.18, 0.18, 0.20, 1.0))


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
    build_west_estates_townhouses()
    build_north_ranch_neighborhood()
    build_nexcorp_model_home()
    build_nexcorp_sales_trailer()
    build_east_cds_neighborhood()
    build_phase3_neighborhood()
    build_country_club()
    build_country_club_lot()
    build_harmony_park()
    build_community_garden()
    build_wild_zone_trees()
    build_district_arterials()
    build_community_landmarks()
    build_connector_roads()
    build_chapter1_pedestrian_network()
    build_intersections()
    build_bridges()
    build_ot_park_access_road()
    build_hs_stadium_overflow_lot()
    build_elementary_school()
    build_truck_stop()
    build_taqueria_el_rancho()
    build_east_commercial_box()
    build_bus_stops()
    build_residential_mailboxes()
    build_arterial_lighting()
    build_arterial_trees()
    build_church_cemetery()
    build_church_lot_and_school_playground()
    build_dambrosios_holdover()
    build_water_tower_and_lines()
    build_halsey_studios()
    build_hospital()
    build_drive_in_theatre()
    build_arterial_sidewalks()
    build_crosswalks_and_stops()
    build_street_name_signs()
    build_school_zone_signs()
    build_ambient_npcs()
    build_self_storage()
    build_auto_dealership()
    build_midway_minimart()
    build_horizon_plaza()
    build_dumpsters()
    build_little_league_field()
    build_library_and_bike_racks()
    build_phase3_crane()
    build_police_station()
    build_high_school_field()
    build_strip_mall_nightclub()
    build_nexcorp_hq()
    export_glb()


if __name__ == "__main__":
    main()
