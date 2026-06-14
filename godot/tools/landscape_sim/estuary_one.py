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
class LandscapeParams:
    name: str
    bounds: tuple[float, float, float, float]   # (min_x, max_x, min_y, max_y)
    elevation: Callable[[float, float], float]
    creek: CreekPath
    roads: RoadGrid
    neighbourhoods: list[Neighbourhood] = field(default_factory=list)
    resolution: int = 800           # px on the longer axis
    contour_step: float = 0.5       # metres between contour lines
    seed: int = 1337

# ── HCE example parameters (the topography doc made flesh) ────────
def hce_elevation(x: float, y: float) -> float:
    """Harmony Creek Estates elevation. NW high (country club / golf),
    creek runs diagonal NW→SE through the middle as a flood plain
    dip, SE low (skate park / woods). Slight noise on top so the
    map doesn't look ruler-drawn."""
    # Baseline tilt: high in NW corner, low in SE
    tilt = 4.0 * ((-(x) + y) / 600.0)
    # Country-club rise — gentle bump in the north
    cc_dx = x - 0
    cc_dy = y - 200
    cc_rise = 4.0 * math.exp(-(cc_dx * cc_dx + cc_dy * cc_dy) / (140.0 * 140.0))
    # Subtle texture noise — 30cm peaks for that "manicured but real" feel
    noise = (fbm(x * 0.008, y * 0.008, octaves=3) - 0.5) * 0.6
    # Creek subtracts a flood-plain dip
    creek_dist = HCE_CREEK.distance(x, y)
    dip = -1.2 * math.exp(-creek_dist * creek_dist / (HCE_CREEK.flood_width ** 2))
    return tilt + cc_rise + noise + dip

HCE_CREEK = CreekPath(
    points=[
        (-280,  180),
        (-150,   80),
        ( -40,    0),
        (  80,  -70),
        ( 200, -120),
        ( 290, -180),
    ],
    width=6.0,
    flood_width=22.0,
)

HCE_ROADS = RoadGrid(
    segments=[
        # Frontage road N-S along west side
        ((-280, -200), (-280, 200)),
        # Hilltop road E-W across the north (country club access)
        ((-280, 160), (290, 160)),
        # Central E-W (main residential collector)
        ((-280,   0), (290,   0)),
        # South arterial (skate park / woods edge)
        ((-280, -160), (290, -160)),
        # N-S secondary on the east side
        (( 200, -200), ( 200, 200)),
        # Two cul-de-sac stubs east
        (( 200,  80), (260,  80)),
        (( 200, -80), (260, -80)),
        # Park-loop on the west
        ((-220, -80), (-120, -80)),
        ((-120, -80), (-120,  80)),
        ((-120,  80), (-220,  80)),
    ]
)

HCE_NEIGHBOURHOODS = [
    Neighbourhood("Country Club + Golf", [
        (-280, 100), (290, 100), (290, 200), (-280, 200)
    ], landuse="golf"),
    Neighbourhood("Town Park + Pool", [
        (-120, -60), (60, -60), (60, 60), (-120, 60)
    ], landuse="park"),
    Neighbourhood("West Residential", [
        (-280, -160), (-120, -160), (-120, 60), (-280, 60)
    ], landuse="single_family"),
    Neighbourhood("East Cul-de-sac", [
        (60, -160), (290, -160), (290, 60), (60, 60)
    ], landuse="cul_de_sac"),
    Neighbourhood("Skate Park + Woods", [
        (-280, -200), (290, -200), (290, -160), (-280, -160)
    ], landuse="natural_park"),
    Neighbourhood("Creek Corridor", [
        # Approximate the creek's flood plain
        (-280, 200), (-260, 200), (290, -180), (290, -200),
    ], landuse="creek_corridor"),
]

HCE_PARAMS = LandscapeParams(
    name="Harmony Creek Estates",
    bounds=(-300, 300, -210, 210),
    elevation=hce_elevation,
    creek=HCE_CREEK,
    roads=HCE_ROADS,
    neighbourhoods=HCE_NEIGHBOURHOODS,
    resolution=900,
    contour_step=0.8,
    seed=1337,
)

# ── Rendering: hand-rolled PPM so we don't pull in numpy/PIL ──────
def lerp(a, b, t):
    return a + (b - a) * t

def colour_for_elevation(z: float, z_min: float, z_max: float, landuse: str = "") -> tuple[int, int, int]:
    """Map elevation + landuse → RGB. Greens for parkland, browns for
    high ground, blues for creek, sandy yellow for very low."""
    t = (z - z_min) / max(0.001, z_max - z_min)
    # Land-use overrides
    if landuse == "creek_corridor":
        return (60, 90, 130)
    if landuse == "golf":
        return (int(lerp(30, 80, t)), int(lerp(120, 170, t)), int(lerp(40, 60, t)))
    if landuse == "park":
        return (int(lerp(40, 100, t)), int(lerp(140, 180, t)), int(lerp(40, 80, t)))
    if landuse == "natural_park":
        return (int(lerp(60, 100, t)), int(lerp(100, 140, t)), int(lerp(40, 80, t)))
    if landuse == "single_family":
        return (int(lerp(120, 160, t)), int(lerp(150, 180, t)), int(lerp(100, 140, t)))
    if landuse == "cul_de_sac":
        return (int(lerp(150, 180, t)), int(lerp(160, 190, t)), int(lerp(130, 160, t)))
    # default elevation ramp
    if t < 0.25:
        return (130, 145, 170)
    if t < 0.55:
        return (110, 145, 100)
    if t < 0.85:
        return (140, 150, 110)
    return (150, 140, 110)

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
    print(f"[preview] wrote {summary_path}")


# ── Entry point ──────────────────────────────────────────────────
if __name__ == "__main__":
    out = sys.argv[1] if len(sys.argv) > 1 else "hce_preview.ppm"
    print("[estuary one] slowstick landscape preview · vol 7 prototype")
    render(HCE_PARAMS, out)
