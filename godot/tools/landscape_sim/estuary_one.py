#!/usr/bin/env python3
"""
estuary_one.py
══════════════════════════════════════════════════════════════════
ESTUARY ONE · generative landscape preview harness.

In-fiction: a prototype landscape simulator from the slowstick game
studios of volume 7 — an early build of the tool that designs the
worlds the characters live inside. Out-of-fiction: a parametric
topography previewer we use BEFORE committing to a Blender / glTF
build cycle.

The point: iterate landscape parameters in seconds, in 2-D, without
baking geometry. Tweak the parameters at the bottom; the script
writes a PPM showing the elevation contours, creek path, road grid,
neighbourhood boundaries, and parcel coverage proposed by those
parameters. Decide whether the shape is right; then transcribe the
locked parameters into the locale's build_*.py.

Workflow:
    1. Open this file. Edit the *_PARAMS block(s) at the bottom.
    2. Run: `python3 estuary_one.py [out.ppm]`
    3. Open the PPM in any viewer (or convert to PNG). Adjust
       parameters. Repeat until the topography reads correct.
    4. Once locked, copy the params into the locale's build script
       and start placing geometry.

Dependencies: stdlib only (no matplotlib, no numpy). Writes a
hand-rolled PPM that any viewer reads. Portable to the Steam Deck
container without `pip install`.

Coordinate frame: matches the build scripts — Blender Z-up, units
in metres, (x, y) is the top-down floor plane.
══════════════════════════════════════════════════════════════════
"""
from __future__ import annotations
import math
import struct
import sys
import os
from dataclasses import dataclass, field
from typing import Callable

# ── Deterministic small hash (no random.seed dance) ───────────────
def hash2d(x: float, y: float, seed: int = 1337) -> float:
    """Deterministic 0..1 hash from (x, y) and a seed. Used as the
    primitive under value-noise and the road-grid jitter."""
    n = math.sin(x * 12.9898 + y * 78.233 + seed * 0.0001) * 43758.5453
    return n - math.floor(n)

def value_noise(x: float, y: float, seed: int = 1337) -> float:
    """2-D value noise with bilinear smoothing."""
    xi, yi = math.floor(x), math.floor(y)
    fx, fy = x - xi, y - yi
    # smoothstep
    sx = fx * fx * (3.0 - 2.0 * fx)
    sy = fy * fy * (3.0 - 2.0 * fy)
    a = hash2d(xi,     yi,     seed)
    b = hash2d(xi + 1, yi,     seed)
    c = hash2d(xi,     yi + 1, seed)
    d = hash2d(xi + 1, yi + 1, seed)
    return (a * (1 - sx) + b * sx) * (1 - sy) + (c * (1 - sx) + d * sx) * sy

def fbm(x: float, y: float, octaves: int = 4, seed: int = 1337) -> float:
    v = 0.0
    amp = 0.5
    freq = 1.0
    norm = 0.0
    for _ in range(octaves):
        v += amp * value_noise(x * freq, y * freq, seed)
        norm += amp
        amp *= 0.5
        freq *= 2.0
    return v / norm

# ── Parametric building blocks ────────────────────────────────────
@dataclass
class CreekPath:
    """A meandering line defined by a small set of control points and
    a sinuous wave perturbation. The creek's width varies along its
    length. Used by the elevation function as a flood-plain dip."""
    points: list[tuple[float, float]]  # control points in world coords
    width: float = 6.0                  # nominal water width (m)
    flood_width: float = 22.0           # flood-plain dip width

    def distance(self, x: float, y: float) -> float:
        """Approximate distance from (x, y) to the creek polyline."""
        best = float("inf")
        for i in range(len(self.points) - 1):
            ax, ay = self.points[i]
            bx, by = self.points[i + 1]
            # Segment-distance
            dx, dy = bx - ax, by - ay
            seg_len_sq = dx * dx + dy * dy
            if seg_len_sq < 1e-6:
                d = math.hypot(x - ax, y - ay)
            else:
                t = max(0.0, min(1.0, ((x - ax) * dx + (y - ay) * dy) / seg_len_sq))
                px, py = ax + t * dx, ay + t * dy
                d = math.hypot(x - px, y - py)
            if d < best:
                best = d
        return best

@dataclass
class RoadGrid:
    """Rough road network — N-S frontage + E-W arterial + smaller
    residential loops. Stored as polyline pairs so they render cleanly
    over the elevation map."""
    segments: list[tuple[tuple[float, float], tuple[float, float]]]

@dataclass
class Neighbourhood:
    """A named district boundary polygon + intended landuse code."""
    name: str
    points: list[tuple[float, float]]
    landuse: str   # e.g. "single_family", "park", "golf", "creek_corridor"

@dataclass
class Landmark:
    """A named narrative hot spot — a specific building or address
    that matters to the volume's story. Rendered as a coloured dot
    over the neighbourhood map. category drives the dot colour:
      'commercial' · convenience, gas station, retail (warm yellow)
      'civic'      · HOA office, community pool, school (cyan)
      'narrative'  · a specific story-load address (magenta)
      'media'      · zine shop, recording studio (orange)
      'transit'    · arterial intersections, bus stops (white)
    """
    name: str
    x: float
    y: float
    category: str = "narrative"
    note: str = ""

@dataclass
class LandscapeParams:
    name: str
    bounds: tuple[float, float, float, float]   # (min_x, max_x, min_y, max_y)
    elevation: Callable[[float, float], float]
    creek: CreekPath
    roads: RoadGrid
    neighbourhoods: list[Neighbourhood] = field(default_factory=list)
    landmarks: list[Landmark] = field(default_factory=list)
    resolution: int = 800           # px on the longer axis
    contour_step: float = 0.5       # metres between contour lines
    seed: int = 1337

# ── HCE example parameters (the topography doc made flesh) ────────
def hce_elevation(x: float, y: float) -> float:
    """Real terrain — ~40 m peak-to-trough across the 1200 × 840 m
    district. Tuned after the 30 m spread still read flat. Now:
      · NW country-club hill  +22 m
      · East-side ridge       +10 m
      · NW headwaters knoll    +8 m
      · SE basin              -8 m
      · NW→SE tilt           ±10 m
      · Creek ravine           -7 m
      · Multi-scale noise     ±5.5 m
    Must stay in sync with build_harmony_terrain.py hce_elevation()."""
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
    creek_dist = HCE_CREEK.distance(x, y)
    dip = -7.0 * math.exp(-creek_dist * creek_dist / (50.0 ** 2))
    return (tilt + cc_rise + east_rise + nw_rise + south_dip
            + noise_low + noise_high + dip)

HCE_CREEK = CreekPath(
    points=[
        (-560,  360),
        (-300,  160),
        ( -80,    0),
        ( 160, -140),
        ( 400, -240),
        ( 580, -360),
    ],
    width=6.0,
    flood_width=22.0,
)

HCE_ROADS = RoadGrid(
    # Sparser, more rural road grid — gone back to seed. Commercial
    # belts ride the PERIMETER (N + W + S + E arterials); the interior
    # has a few residential collectors and short stubs but otherwise
    # large unbroken lots and wild patches between roads.
    # District is now 1200 × 840 m so the suburban features have
    # room to breathe — coords below are 2× the original sketch.
    segments=[
        # ── Perimeter commercial arterials (the "bordering roads") ──
        ((-560, -400), (-560, 400)),    # West frontage (Highway 9)
        ((-560, 260),  (580, 260)),     # North arterial (south of golf)
        ((540,  -400), (540, 400)),     # East arterial
        ((-560, -340), (580, -340)),    # South arterial (truck route)

        # ── Sparse residential collectors (interior) ──
        ((-560,  20),  (540, 20)),      # Central E-W
        ((40, -340),   (40, 260)),      # Lone N-S interior

        # ── Short residential stubs ──
        ((-360,  20),  (-360, 200)),    # north stub off central
        ((200, -340),  (200, -120)),    # south stub
        ((-400, -200), (-220, -200)),   # east-west residential
        ((240,  120),  (440,  120)),    # eastern cul-de-sac feeder

        # ── Country club access spur ──
        ((120, 260),   (120, 360)),
    ]
)

HCE_NEIGHBOURHOODS = [
    # ── Commercial belts along the PERIMETER ROADS ──
    Neighbourhood("West Commercial Strip", [
        (-560, -340), (-460, -340), (-460, 260), (-560, 260)
    ], landuse="commercial"),
    Neighbourhood("North Commercial Belt", [
        (-460, 260), (440, 260), (440, 340), (-460, 340)
    ], landuse="commercial"),
    Neighbourhood("South Commercial / Truck Stop", [
        (-460, -400), (440, -400), (440, -340), (-460, -340)
    ], landuse="commercial"),
    Neighbourhood("East Commercial", [
        (440, -340), (540, -340), (540, 260), (440, 260)
    ], landuse="commercial"),

    # ── Country club on the north high ground ──
    Neighbourhood("Country Club + Golf", [
        (-460, 340), (440, 340), (440, 420), (-460, 420)
    ], landuse="golf"),

    # ── MULTIPLE distinct PARKS per grid quadrant ──
    Neighbourhood("Harmony Park (community / pool)", [
        (-120, -40), (180, -40), (180, 200), (-120, 200)
    ], landuse="park"),
    Neighbourhood("Founders Memorial Grove", [
        (-400, 100), (-200, 100), (-200, 220), (-400, 220)
    ], landuse="park_natural"),
    Neighbourhood("South Sports Fields", [
        (260, -320), (440, -320), (440, -100), (260, -100)
    ], landuse="park_sports"),
    Neighbourhood("Creek Trail Park (natural)", [
        (180, -320), (260, -320), (260, -40), (180, -40)
    ], landuse="park_natural"),
    Neighbourhood("Wild Lot (gone to seed)", [
        (-400, -300), (-260, -300), (-260, -180), (-400, -180)
    ], landuse="overgrown"),

    # ── Spread-out residential — single-family, low density ──
    Neighbourhood("West Estates (single-family)", [
        (-460, -340), (-120, -340), (-120, -40), (-460, -40)
    ], landuse="single_family"),
    Neighbourhood("North Ranch Homes", [
        (-460, 20), (-200, 20), (-200, 260), (-460, 260)
    ], landuse="single_family"),
    Neighbourhood("East Cul-de-sac Estates", [
        (180, 20), (440, 20), (440, 260), (180, 260)
    ], landuse="cul_de_sac"),

    Neighbourhood("Creek Corridor", [
        (-560, 420), (-440, 420), (580, -360), (580, -400),
    ], landuse="creek_corridor"),
]

# ── vol6 narrative hot spots ─────────────────────────────────────
# Per _VOL6_WIKI.md "Locations" + "Adjacent infrastructure" sections.
# The CHAPTER-ONE BASELINE QUADRANT: the intersection where Kwik Stop
# and NexCorp Gas & Go sit across from each other (West Commercial
# Strip × North Commercial Belt corner). Everything else is placed
# narratively from there.
HCE_LANDMARKS = [
    # ── THE COMMERCIAL CHAPTER-ONE CLUSTER ──────────────────────
    # Kwik Stop and NexCorp Gas & Go ACROSS THE INTERSECTION per
    # _VOL6_WIKI.md. NW corner of the West Commercial Strip ×
    # North Commercial Belt junction.
    Landmark("Kwik Stop", -500, 290, "commercial",
             "Sam's register · wire basket · back-cooler recursion"),
    Landmark("NexCorp Gas & Go", -420, 290, "commercial",
             "Skip's shift · locker #4"),
    Landmark("Cosmic Comics", -500, 200, "media",
             "Rick · the photocopier · DO NOT SORT YET pile"),

    # ── OTHER COMMERCIAL HOT SPOTS ──────────────────────────────
    Landmark("D'Ambrosio's (vol5 holdover)", -390, 180, "narrative",
             "John's column corner · Maya's mail-drop to F.T."),
    Landmark("Halsey Studios", 500, 200, "media",
             "Gallatin Band · the unreleased fourth-record track"),
    Landmark("Truck Stop Diner", 0, -370, "commercial",
             "south arterial · long-haul corner"),

    # ── CIVIC ──────────────────────────────────────────────────
    Landmark("HOA Welcome / Office", -20, 120, "civic",
             "Carl Reno's breakfasts · the welcome table"),
    Landmark("Community Pool + Bandshell", 30, 80, "civic",
             "the watch-tower lifeguard chair"),
    Landmark("Country Club Clubhouse", -40, 380, "civic",
             "high ground · sightlines into both subdivisions"),

    # ── SPECIFIC NARRATIVE ADDRESSES ────────────────────────────
    Landmark("Lot 7 · Connie Daigle", -340, -120, "narrative",
             "Phase I · the most settled"),
    Landmark("Lot 14 · Mrs. Pimentel", -300, -180, "narrative",
             "Phase I · the wrong-address scheme"),
    Landmark("Lot 47 · model home", 260, 100, "narrative",
             "the fake basil pot · Carla Vega three doors down"),
    Landmark("892 Ashberry Drive", 330, 150, "narrative",
             "Maya's empty house · zine #19"),

    # ── PHASE BOUNDARIES (rough indicators) ────────────────────
    Landmark("Phase II construction office", 100, -260, "civic",
             "new buyers from Graustark and Beaumont"),
    Landmark("Phase III · Norman Lott's trailer", -320, -270, "narrative",
             "dirt and surveying flags · NexCorp's substrate language"),
]

HCE_PARAMS = LandscapeParams(
    name="Harmony Creek Estates",
    bounds=(-600, 600, -420, 420),
    elevation=hce_elevation,
    creek=HCE_CREEK,
    roads=HCE_ROADS,
    neighbourhoods=HCE_NEIGHBOURHOODS,
    landmarks=HCE_LANDMARKS,
    resolution=900,
    contour_step=0.8,
    seed=1337,
)

# ── Rendering: hand-rolled PPM so we don't pull in numpy/PIL ──────
def lerp(a, b, t):
    return a + (b - a) * t

def colour_for_elevation(z: float, z_min: float, z_max: float, landuse: str = "") -> tuple[int, int, int]:
    """Map elevation + landuse → RGB per the HCE colour grammar:
      DARK GREEN  → natural vegetation AND public/community space
      WHITE / DRY → single-family residential AND people (parched)
      BLUE        → creek + water
      GREY-TAN    → commercial belts (asphalt + buildings)
      SAGE        → overgrown / gone-to-seed lots
    """
    t = (z - z_min) / max(0.001, z_max - z_min)
    # ── Water / creek ──
    if landuse == "creek_corridor":
        return (60, 90, 130)
    # ── DARK GREEN family: natural + community public space ──
    if landuse == "golf":
        return (int(lerp(30, 70, t)), int(lerp(110, 150, t)), int(lerp(35, 55, t)))
    if landuse == "park":
        return (int(lerp(40, 90, t)), int(lerp(130, 170, t)), int(lerp(40, 75, t)))
    if landuse == "park_natural":
        return (int(lerp(30, 75, t)), int(lerp(105, 145, t)), int(lerp(35, 65, t)))
    if landuse == "park_sports":
        return (int(lerp(60, 110, t)), int(lerp(140, 180, t)), int(lerp(50, 80, t)))
    if landuse == "natural_park":
        return (int(lerp(50, 95, t)), int(lerp(120, 160, t)), int(lerp(45, 75, t)))
    # ── WHITE / DRY family: single-family homes + parched people ──
    if landuse == "single_family":
        return (int(lerp(195, 225, t)), int(lerp(195, 220, t)), int(lerp(170, 195, t)))
    if landuse == "cul_de_sac":
        return (int(lerp(205, 235, t)), int(lerp(200, 225, t)), int(lerp(180, 205, t)))
    # ── Commercial belts: asphalt-grey with warm hint ──
    if landuse == "commercial":
        return (int(lerp(110, 140, t)), int(lerp(105, 130, t)), int(lerp(95, 115, t)))
    # ── Overgrown / gone-to-seed: dull sage with brown undertone ──
    if landuse == "overgrown":
        return (int(lerp(120, 150, t)), int(lerp(130, 155, t)), int(lerp(85, 110, t)))
    # default elevation ramp — same dry palette so unzoned land
    # blends with the residential field
    if t < 0.25:
        return (170, 175, 165)
    if t < 0.55:
        return (190, 190, 170)
    if t < 0.85:
        return (210, 200, 170)
    return (220, 205, 165)

def point_in_polygon(x: float, y: float, polygon: list[tuple[float, float]]) -> bool:
    """Even-odd-rule polygon-point test."""
    inside = False
    n = len(polygon)
    j = n - 1
    for i in range(n):
        xi, yi = polygon[i]
        xj, yj = polygon[j]
        if ((yi > y) != (yj > y)) and (x < (xj - xi) * (y - yi) / (yj - yi + 1e-12) + xi):
            inside = not inside
        j = i
    return inside

def render(params: LandscapeParams, out_path: str) -> None:
    min_x, max_x, min_y, max_y = params.bounds
    width_world = max_x - min_x
    height_world = max_y - min_y
    aspect = width_world / height_world
    if aspect >= 1:
        W = params.resolution
        H = int(round(params.resolution / aspect))
    else:
        H = params.resolution
        W = int(round(params.resolution * aspect))

    print(f"[preview] rendering {params.name}: {W} × {H} px over {width_world:.0f} × {height_world:.0f} m")

    # Pass 1: compute elevation grid, find min/max
    elev = [[0.0] * W for _ in range(H)]
    z_min = float("inf")
    z_max = float("-inf")
    for j in range(H):
        wy = min_y + (max_y - min_y) * (1.0 - (j + 0.5) / H)
        for i in range(W):
            wx = min_x + (max_x - min_x) * ((i + 0.5) / W)
            z = params.elevation(wx, wy)
            elev[j][i] = z
            if z < z_min:
                z_min = z
            if z > z_max:
                z_max = z
    print(f"[preview] elevation range: {z_min:+.2f} m → {z_max:+.2f} m")

    # Pass 2: colour buffer
    buf = bytearray(W * H * 3)
    for j in range(H):
        for i in range(W):
            wx = min_x + (max_x - min_x) * ((i + 0.5) / W)
            wy = min_y + (max_y - min_y) * (1.0 - (j + 0.5) / H)
            z = elev[j][i]
            landuse = ""
            for n in params.neighbourhoods:
                if point_in_polygon(wx, wy, n.points):
                    landuse = n.landuse
                    break
            r, g, b = colour_for_elevation(z, z_min, z_max, landuse)
            # Contour line: darken pixels where elevation crosses
            # an N × contour_step boundary
            cs = params.contour_step
            band = math.floor(z / cs)
            band_neighbour = math.floor(elev[j][i - 1] / cs) if i > 0 else band
            band_neighbour2 = math.floor(elev[j - 1][i] / cs) if j > 0 else band
            if band != band_neighbour or band != band_neighbour2:
                r = int(r * 0.55)
                g = int(g * 0.55)
                b = int(b * 0.55)
            idx = (j * W + i) * 3
            buf[idx] = max(0, min(255, r))
            buf[idx + 1] = max(0, min(255, g))
            buf[idx + 2] = max(0, min(255, b))

    # Pass 3: overlay creek (blue line)
    def world_to_px(wx: float, wy: float) -> tuple[int, int]:
        i = int(round((wx - min_x) / (max_x - min_x) * W))
        j = int(round((1.0 - (wy - min_y) / (max_y - min_y)) * H))
        return i, j

    def stroke_line(p0: tuple[int, int], p1: tuple[int, int], colour: tuple[int, int, int], thick: int = 2) -> None:
        x0, y0 = p0
        x1, y1 = p1
        dx = x1 - x0
        dy = y1 - y0
        steps = max(abs(dx), abs(dy)) + 1
        for s in range(steps + 1):
            t = s / steps if steps else 0
            px = int(round(x0 + dx * t))
            py = int(round(y0 + dy * t))
            for ox in range(-thick, thick + 1):
                for oy in range(-thick, thick + 1):
                    if ox * ox + oy * oy <= thick * thick:
                        xi = px + ox
                        yi = py + oy
                        if 0 <= xi < W and 0 <= yi < H:
                            idx = (yi * W + xi) * 3
                            buf[idx]     = colour[0]
                            buf[idx + 1] = colour[1]
                            buf[idx + 2] = colour[2]

    # Creek (water)
    for i in range(len(params.creek.points) - 1):
        stroke_line(world_to_px(*params.creek.points[i]),
                    world_to_px(*params.creek.points[i + 1]),
                    (60, 110, 170), thick=3)

    # Roads (dark gray)
    for (a, b) in params.roads.segments:
        stroke_line(world_to_px(*a), world_to_px(*b), (40, 40, 40), thick=2)

    # Neighbourhood labels — simple dot at polygon centroid
    for n in params.neighbourhoods:
        cx = sum(p[0] for p in n.points) / len(n.points)
        cy = sum(p[1] for p in n.points) / len(n.points)
        ci, cj = world_to_px(cx, cy)
        for ox in range(-3, 4):
            for oy in range(-3, 4):
                xi = ci + ox
                yi = cj + oy
                if 0 <= xi < W and 0 <= yi < H:
                    idx = (yi * W + xi) * 3
                    buf[idx] = 240
                    buf[idx + 1] = 200
                    buf[idx + 2] = 60

    # Landmark dots — narrative hot spots get a chunkier coloured
    # marker on top of the elevation map. Category drives the hue
    # so you can read commercial / civic / narrative / media at a
    # glance.
    landmark_palette = {
        "commercial": (255, 215, 50),    # warm yellow
        "civic":      (80, 200, 230),    # cyan
        "narrative":  (235, 90, 200),    # magenta
        "media":      (255, 140, 40),    # orange
        "transit":    (245, 245, 245),   # near-white
    }
    for lm in params.landmarks:
        ci, cj = world_to_px(lm.x, lm.y)
        col = landmark_palette.get(lm.category, (235, 90, 200))
        # Outer halo (dark) for legibility on the lawn green
        for ox in range(-6, 7):
            for oy in range(-6, 7):
                d2 = ox * ox + oy * oy
                if 30 <= d2 <= 42:
                    xi = ci + ox; yi = cj + oy
                    if 0 <= xi < W and 0 <= yi < H:
                        idx = (yi * W + xi) * 3
                        buf[idx]     = 20
                        buf[idx + 1] = 20
                        buf[idx + 2] = 20
        # Inner solid dot
        for ox in range(-5, 6):
            for oy in range(-5, 6):
                if ox * ox + oy * oy <= 25:
                    xi = ci + ox; yi = cj + oy
                    if 0 <= xi < W and 0 <= yi < H:
                        idx = (yi * W + xi) * 3
                        buf[idx]     = col[0]
                        buf[idx + 1] = col[1]
                        buf[idx + 2] = col[2]

    # Write PPM (P6 — binary RGB, universally readable)
    with open(out_path, "wb") as f:
        f.write(f"P6\n{W} {H}\n255\n".encode("ascii"))
        f.write(buf)
    print(f"[preview] wrote {out_path} ({W * H * 3:,} bytes)")
    # Also write a small text summary
    summary_path = os.path.splitext(out_path)[0] + ".txt"
    with open(summary_path, "w") as f:
        f.write(f"{params.name}\n")
        f.write(f"  bounds:    {params.bounds}\n")
        f.write(f"  size:      {width_world:.0f} m × {height_world:.0f} m\n")
        f.write(f"  pixels:    {W} × {H}\n")
        f.write(f"  elevation: {z_min:+.2f} m → {z_max:+.2f} m\n")
        f.write(f"  neighbourhoods:\n")
        for n in params.neighbourhoods:
            f.write(f"    · {n.name:30s} ({n.landuse})\n")
        f.write(f"  road segments: {len(params.roads.segments)}\n")
        f.write(f"  creek control points: {len(params.creek.points)}\n")
        if params.landmarks:
            f.write(f"  narrative hot spots ({len(params.landmarks)}):\n")
            by_cat: dict[str, list[Landmark]] = {}
            for lm in params.landmarks:
                by_cat.setdefault(lm.category, []).append(lm)
            for cat in sorted(by_cat.keys()):
                f.write(f"    ── {cat} ──\n")
                for lm in by_cat[cat]:
                    coord = f"({lm.x:+5.0f}, {lm.y:+5.0f})"
                    f.write(f"    · {lm.name:36s} {coord}")
                    if lm.note:
                        f.write(f"  // {lm.note}")
                    f.write("\n")
    print(f"[preview] wrote {summary_path}")


# ── Zoom views — render any subset of an existing LandscapeParams
# at higher resolution. The chapter-one quadrant is the canonical
# example: Kwik Stop ↔ NexCorp Gas & Go intersection plus Cosmic
# Comics and D'Ambrosio's directly south. ~130 m × 110 m.
def zoom(params: LandscapeParams, bounds: tuple[float, float, float, float],
         resolution: int = 1200, name_suffix: str = "") -> LandscapeParams:
    """Return a new LandscapeParams reading the same elevation /
    creek / roads / neighbourhoods / landmarks but cropped to a
    tighter (min_x, max_x, min_y, max_y) and rendered higher-res.
    Useful for picking out a specific quadrant to lock its layout
    before transcribing to a build script."""
    return LandscapeParams(
        name=params.name + (" · " + name_suffix if name_suffix else ""),
        bounds=bounds,
        elevation=params.elevation,
        creek=params.creek,
        roads=params.roads,
        neighbourhoods=params.neighbourhoods,
        landmarks=params.landmarks,
        resolution=resolution,
        contour_step=max(0.2, params.contour_step * 0.5),  # finer contours when zoomed
        seed=params.seed,
    )

# Chapter-one commercial cluster zoom: the NW corner of HCE.
# Bounds capture Kwik Stop (-250,+145), Gas & Go (-210,+145),
# Cosmic Comics (-250,+100), D'Ambrosio's holdover (-195,+90),
# plus surrounding road frontage + a buffer on each side.
HCE_CHAPTER_ONE = zoom(
    HCE_PARAMS,
    bounds=(-590, -300, 100, 360),
    resolution=1400,
    name_suffix="chapter one quadrant",
)


# ── Entry point ──────────────────────────────────────────────────
if __name__ == "__main__":
    # Usage:
    #   python3 estuary_one.py [out.ppm] [view]
    #     view ∈ {"full", "chapter_one"}, default "full"
    out = sys.argv[1] if len(sys.argv) > 1 else "hce_preview.ppm"
    view = sys.argv[2] if len(sys.argv) > 2 else "full"
    print("[estuary one] slowstick landscape preview · vol 7 prototype")
    if view == "chapter_one":
        render(HCE_CHAPTER_ONE, out)
    else:
        render(HCE_PARAMS, out)
