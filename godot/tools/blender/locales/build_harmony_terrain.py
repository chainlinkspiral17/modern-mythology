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
import bpy

_SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))

OUTPUT_DIR = "../../../assets/3d/locales"
OUTPUT_NAME = "harmony_terrain.glb"

SEASON = 0.35

def lerp_palette(t, lo, hi):
    return tuple(lo[i] + (hi[i] - lo[i]) * t for i in range(4))

# ── DISTRICT BOUNDS (matches estuary_one HCE_PARAMS) ─────────────
DIST_MIN_X = -300.0
DIST_MAX_X =  300.0
DIST_MIN_Y = -210.0
DIST_MAX_Y =  210.0

# Tighter tessellation than the district build (40×28 = ~15 m cells)
# so the terrain reads clean without buildings on top to hide
# undersampling artefacts.
GROUND_NX = 40
GROUND_NY = 28

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
    (-280,  180),
    (-150,   80),
    ( -40,    0),
    (  80,  -70),
    ( 200, -120),
    ( 290, -180),
]
CREEK_FLOOD_WIDTH = 28.0

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


def hce_elevation(x, y):
    """~30 m vertical range. NW country-club rise, east ridge,
    creek ravine, NW→SE tilt, noise."""
    tilt = 7.0 * ((-(x) + y) / 600.0)
    cc_dx = x - 0
    cc_dy = y - 200
    cc_rise = 14.0 * math.exp(-(cc_dx * cc_dx + cc_dy * cc_dy) / (140.0 * 140.0))
    east_dx = x - 240
    east_dy = y - 40
    east_rise = 6.0 * math.exp(-(east_dx * east_dx + east_dy * east_dy) / (110.0 * 110.0))
    noise = (fbm(x * 0.008, y * 0.008, octaves=3) - 0.5) * 3.0
    creek_d = creek_distance(x, y)
    dip = -3.0 * math.exp(-creek_d * creek_d / (CREEK_FLOOD_WIDTH ** 2))
    return tilt + cc_rise + east_rise + noise + dip


def landuse_at(x, y):
    """Coarse landuse classifier — drives the per-polygon ground
    colour. No buildings or roads exist yet, but the seasonal
    palette per zone helps verify the design intent reads visually:
    natural green for the wild + forested zones, manicured green
    for the country club + parks, sage for the overgrown lot,
    dirt for the commercial belts (where roads will go later)."""
    # Country club golf course (irrigated — stays green even in August)
    if -230 < x < 220 and 170 < y < 210:
        return 'golf'
    # Creek bank (where the water cuts through)
    if creek_distance(x, y) < 8.0:
        return 'creek_bank'
    # Commercial belts — DIRT for now (roads laid against terrain later)
    if -280 <= x <= -230 and -170 <= y <= 130:
        return 'commercial_dirt'
    if x >= 220 and -170 <= y <= 130:
        return 'commercial_dirt'
    if -230 <= x <= 220 and 130 <= y <= 170:
        return 'commercial_dirt'
    if -230 <= x <= 220 and -200 <= y <= -170:
        return 'commercial_dirt'
    # Harmony Park
    if -60 <= x <= 90 and -20 <= y <= 100:
        return 'park'
    # Founders Memorial Grove (natural forest)
    if -200 <= x <= -100 and 50 <= y <= 110:
        return 'natural'
    # Wild lot — gone to seed
    if -200 <= x <= -130 and -150 <= y <= -90:
        return 'overgrown'
    # Default: residential / open lawn
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


def main():
    clear_scene()
    build_ground()
    build_creek()
    export_glb()


if __name__ == "__main__":
    main()
