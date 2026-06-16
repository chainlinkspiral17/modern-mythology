"""
build_graustark.py
══════════════════════════════════════════════════════════════════
VOL 5 / 6 · GRAUSTARK FULL DISTRICT
The bayou-edge Texas/Louisiana delta town that contains
D'Ambrosio's. Theme-park-sized like HCE (1200 × 840 m envelope),
60-70% Lafayette LA aesthetic + 30-40% New Orleans flavour.

This is the DEEP-BUILD master, sitting one tier ABOVE
build_riverfront.py. The riverfront content is preserved verbatim
— this script imports and calls those builders for the southeast
quadrant — and adds the surrounding district as a five-phase
build:

   0. EXISTING RIVERFRONT  (preserved from build_riverfront.py)
   1. ELEVATION FIELD       (delta strata + erosion + carving)
   2. WATER LAYER           (bayou main channel + drainage canals)
   3. ROAD CORRIDORS        (HWY 90, SR 12, River Rd, side lanes)
   4. BUILDINGS             (raised cottages, French Quarter,
                              cathedral anchor, cane-field edge)
   5. CHARACTERS + PROPS    (placement using planar_human bases)

See `lore/_GRAUSTARK_DEEP_BUILD_PLAN.md` for the full five-phase
narrative and visual reference (Lafayette + NOLA framing).

Coordinate frame (matches HCE + riverfront — see
_3D_MODELING_PLAYBOOK.md):
   Blender +X east → Godot +X east
   Blender +Y north / forward → Godot -Z
   Blender +Z up → Godot +Y up
   1 unit = 1 metre.

Run:
    blender --background --python build_graustark.py
    (or via run_cathedral.sh build_graustark.py)

Output:
    godot/assets/3d/locales/graustark.glb
"""
import os
import math
import sys
import bpy

_SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, _SCRIPT_DIR)

# ── DISTRICT ENVELOPE  (HCE-comparable scale) ───────────────────
# Centred on the existing riverfront origin so the boat, parking,
# bayou, and opposite shore keep their canonical X/Y coords.
DIST_MIN_X = -600.0
DIST_MAX_X =  600.0
DIST_MIN_Y = -420.0
DIST_MAX_Y =  420.0
DIST_W = DIST_MAX_X - DIST_MIN_X   # 1200 m
DIST_H = DIST_MAX_Y - DIST_MIN_Y   #  840 m

# ── ELEVATION STRATA  (per lore/_GRAUSTARK_DEEP_BUILD_PLAN.md) ──
# The five-band Z stack of the delta:
LEVEE_RIDGE_Z = +8.0    # high natural levee / oak ridge
RAISED_BANK_Z = +3.0    # upper bayou bank / road shoulders
SEA_LEVEL_Z   =  0.0    # mean sea level / canonical floor
TIDAL_FLAT_Z  = -1.0    # alga-stained mud, intertidal
BAYOU_SHALLOW = -2.0    # cypress-knee shallow channel
CHANNEL_BED   = -4.0    # navigable channel floor

# ── RIVERFRONT INTEGRATION ─────────────────────────────────────
# Import the riverfront's builders. Each call below has the same
# observable effect as today's build_riverfront output, since
# we're calling the same functions in the same order they
# already use.
import build_riverfront as rf

# Override the riverfront's export path so its main() doesn't
# stomp our graustark.glb if someone calls it accidentally.
OUTPUT_DIR = "../../../assets/3d/locales"
OUTPUT_NAME = "graustark.glb"

# Ground mesh resolution — 6 m cells across 1200×840 envelope.
GROUND_NX = 200
GROUND_NY = 140

# ── BAYOU CENTERLINE  (shared between PHASE 1 carving + PHASE 2 water) ──
# 6-waypoint N→S route. Enters from the north at X≈+50, meanders
# with two broad oxbow bends, passes through the riverfront's
# canonical river lane (X = +20..+100 at Y near 0), continues
# south to the truss-bridge crossing at Y = -380.
BAYOU_CENTERLINE = [
    ( +50.0, +420.0),
    ( +35.0, +260.0),
    ( +95.0, +130.0),
    ( +40.0,    0.0),   # passes near canonical riverfront river
    ( +75.0, -130.0),
    ( +30.0, -270.0),
    ( +55.0, -420.0),
]
# Riverfront preservation zone — inside this rectangle, the
# elevation field returns LAND_Z so the existing riverfront
# geometry sits on top without z-fighting.
RF_ZONE_X = (-200.0, +220.0)
RF_ZONE_Y = (-200.0, +200.0)


def _seg_dist(px, py, x0, y0, x1, y1):
    """Perpendicular distance from (px,py) to segment ((x0,y0),(x1,y1)).
    Returns distance plus t in [0,1] along the segment."""
    dx, dy = x1 - x0, y1 - y0
    seg2 = dx * dx + dy * dy
    if seg2 < 1e-9:
        return math.hypot(px - x0, py - y0), 0.0
    t = ((px - x0) * dx + (py - y0) * dy) / seg2
    t = max(0.0, min(1.0, t))
    cx, cy = x0 + dx * t, y0 + dy * t
    return math.hypot(px - cx, py - cy), t


def bayou_distance(x, y):
    """Closest perpendicular distance from (x,y) to the bayou
    centerline polyline."""
    best = 1e9
    for i in range(len(BAYOU_CENTERLINE) - 1):
        x0, y0 = BAYOU_CENTERLINE[i]
        x1, y1 = BAYOU_CENTERLINE[i + 1]
        d, _ = _seg_dist(x, y, x0, y0, x1, y1)
        if d < best:
            best = d
    return best


def graustark_elevation(x, y):
    """Per-vertex Z for the district ground field.

    Five-band strata profile per lore/_GRAUSTARK_DEEP_BUILD_PLAN.md:
      +8 m  levee ridge crown (oak / loam, 30-50m back from bayou)
      +3 m  upper bayou bank (raised street fill)
       0 m  mean sea level / canonical floor
      -1 m  tidal mud flat
      -2 m  shallow bayou (cypress knees)
      -4 m  navigable channel bed

    Returns LAND_Z = 0 inside the riverfront preservation zone so
    the existing build_riverfront geometry sits ON TOP of a flat
    field rather than fighting carved bayou geometry.
    """
    # Riverfront preservation
    if (RF_ZONE_X[0] <= x <= RF_ZONE_X[1]
            and RF_ZONE_Y[0] <= y <= RF_ZONE_Y[1]):
        return SEA_LEVEL_Z

    d = bayou_distance(x, y)

    # Bayou + channel: the closer you are to centerline, the
    # deeper.   d=0    → CHANNEL_BED (-4)
    #           d=10   → BAYOU_SHALLOW (-2)
    #           d=25   → TIDAL_FLAT (-1)
    #           d=40   → SEA_LEVEL (0)
    if d < 10:
        z = CHANNEL_BED + (BAYOU_SHALLOW - CHANNEL_BED) * (d / 10.0)
    elif d < 25:
        z = BAYOU_SHALLOW + (TIDAL_FLAT_Z - BAYOU_SHALLOW) \
            * ((d - 10) / 15.0)
    elif d < 40:
        z = TIDAL_FLAT_Z + (SEA_LEVEL_Z - TIDAL_FLAT_Z) \
            * ((d - 25) / 15.0)
    else:
        # Above sea level: levee ridge + raised bank + gentle plain
        #   d=40   → SEA_LEVEL (0)
        #   d=70   → RAISED_BANK (+3) — fill / road shoulders
        #   d=110  → LEVEE_RIDGE (+8) — oak ridge crown
        #   d=180+ → gentle plain settling back toward +1 m
        if d < 70:
            z = SEA_LEVEL_Z + (RAISED_BANK_Z - SEA_LEVEL_Z) \
                * ((d - 40) / 30.0)
        elif d < 110:
            z = RAISED_BANK_Z + (LEVEE_RIDGE_Z - RAISED_BANK_Z) \
                * ((d - 70) / 40.0)
        elif d < 180:
            # Falling back off the levee crest
            z = LEVEE_RIDGE_Z + (1.0 - LEVEE_RIDGE_Z) \
                * ((d - 110) / 70.0)
        else:
            z = 1.0

    # Gentle southward delta tilt (the gulf is to the south) —
    # subtract ~1.5 m as Y goes from +420 to -420.
    z += (y / DIST_MAX_Y) * 0.75 - 0.0
    # Micro-noise (deterministic, position-seeded so the same
    # build always produces the same field — no random.seed games).
    z += (math.sin(x * 0.13) + math.cos(y * 0.11)) * 0.25
    z += math.sin(x * 0.07 + y * 0.09) * 0.40
    return z


# ── STRATUM PALETTE ────────────────────────────────────────────
# Each stratum has its own vertex colour so the player reads the
# Z bands as distinct material zones from any angle.
COL_LEVEE     = (0.42, 0.46, 0.28, 1.0)   # oak ridge crown, dry loam
COL_RAISED    = (0.55, 0.48, 0.36, 1.0)   # fill / shoulders
COL_PLAIN     = (0.32, 0.40, 0.24, 1.0)   # mean-sea grass plain
COL_TIDAL     = (0.36, 0.38, 0.26, 1.0)   # alga-stained mud
COL_BAYOU_BED = (0.20, 0.22, 0.16, 1.0)   # tannic shallow
COL_CHANNEL   = (0.14, 0.14, 0.12, 1.0)   # silt floor
COL_RF_ZONE   = (0.34, 0.32, 0.24, 1.0)   # riverfront zone neutral


def graustark_color(x, y, z):
    """Stratum colour at (x,y,z)."""
    if (RF_ZONE_X[0] <= x <= RF_ZONE_X[1]
            and RF_ZONE_Y[0] <= y <= RF_ZONE_Y[1]):
        return COL_RF_ZONE
    if z < -3.0:
        return COL_CHANNEL
    if z < -1.5:
        return COL_BAYOU_BED
    if z < -0.5:
        return COL_TIDAL
    if z < +2.0:
        return COL_PLAIN
    if z < +5.5:
        return COL_RAISED
    return COL_LEVEE


def build_district_elevation_field():
    """PHASE 1 — strata + natural erosion across the 1200×840
    envelope. Returns LAND_Z inside the riverfront preservation
    zone so the existing build_riverfront geometry sits cleanly
    on top."""
    print("[graustark] PHASE 1 elevation field — building "
          f"{GROUND_NX}×{GROUND_NY} grid ({GROUND_NX*GROUND_NY} cells)")
    verts = []
    nx_plus_1 = GROUND_NX + 1
    for j in range(GROUND_NY + 1):
        wy = DIST_MIN_Y + (DIST_MAX_Y - DIST_MIN_Y) * j / GROUND_NY
        for i in range(nx_plus_1):
            wx = DIST_MIN_X + (DIST_MAX_X - DIST_MIN_X) * i / GROUND_NX
            verts.append((wx, wy, graustark_elevation(wx, wy)))
    faces = []
    for j in range(GROUND_NY):
        for i in range(GROUND_NX):
            a = j * nx_plus_1 + i
            b = a + 1
            c = b + nx_plus_1
            d = a + nx_plus_1
            faces.append([a, b, c])
            faces.append([a, c, d])
    mesh = bpy.data.meshes.new("Graustark_Terrain_mesh")
    mesh.from_pydata(verts, [], faces)
    mesh.update()
    if not mesh.vertex_colors:
        mesh.vertex_colors.new(name="Col")
    layer = mesh.vertex_colors["Col"]
    z_min = min(v[2] for v in verts)
    z_max = max(v[2] for v in verts)
    print(f"[graustark] elevation range: {z_min:+.2f} m → "
          f"{z_max:+.2f} m  (spread {z_max - z_min:.1f} m)")
    for poly in mesh.polygons:
        cx = sum(verts[v][0] for v in poly.vertices) / len(poly.vertices)
        cy = sum(verts[v][1] for v in poly.vertices) / len(poly.vertices)
        cz = sum(verts[v][2] for v in poly.vertices) / len(poly.vertices)
        col = graustark_color(cx, cy, cz)
        for li in poly.loop_indices:
            layer.data[li].color = col
    obj = bpy.data.objects.new("Graustark_Terrain", mesh)
    bpy.context.collection.objects.link(obj)
    return obj


# Bayou water surface Z — matches the riverfront's RIVER_LEVEL_Z
# so the two systems are flush. At this surface height the channel
# bed (-4) and shallow band (-2) are submerged, while tidal mud
# flats (-1) are EXPOSED (low-tide reading, alga-stained mud).
BAYOU_WATER_Z = -2.5

# Color for bayou water — tannic dark brown, partly transparent
# in real watercolour but vertex-colour means we render the
# surface flat. Slightly bluish for navigability reading.
COL_BAYOU_WATER = (0.12, 0.18, 0.22, 1.0)


def _catmull_rom(p0, p1, p2, p3, t):
    """Standard centripetal Catmull-Rom at parameter t ∈ [0,1]."""
    t2 = t * t
    t3 = t2 * t
    return (
        0.5 * ((2 * p1[0]) +
               (-p0[0] + p2[0]) * t +
               (2*p0[0] - 5*p1[0] + 4*p2[0] - p3[0]) * t2 +
               (-p0[0] + 3*p1[0] - 3*p2[0] + p3[0]) * t3),
        0.5 * ((2 * p1[1]) +
               (-p0[1] + p2[1]) * t +
               (2*p0[1] - 5*p1[1] + 4*p2[1] - p3[1]) * t2 +
               (-p0[1] + 3*p1[1] - 3*p2[1] + p3[1]) * t3),
    )


def _smooth_polyline(pts, samples_per_seg=6):
    """Catmull-Rom smoothing through the waypoints. Mirror the
    first/last point as virtual endpoints so the curve passes
    through the endpoints cleanly."""
    if len(pts) < 2:
        return list(pts)
    ext = [(2*pts[0][0] - pts[1][0], 2*pts[0][1] - pts[1][1])] \
          + list(pts) \
          + [(2*pts[-1][0] - pts[-2][0], 2*pts[-1][1] - pts[-2][1])]
    out = []
    for i in range(1, len(ext) - 2):
        p0, p1, p2, p3 = ext[i-1], ext[i], ext[i+1], ext[i+2]
        for s in range(samples_per_seg):
            t = s / samples_per_seg
            out.append(_catmull_rom(p0, p1, p2, p3, t))
    out.append(pts[-1])
    return out


def build_district_water_layer():
    """PHASE 2 — bayou main channel water surface.
    Catmull-Rom-smoothed strip following BAYOU_CENTERLINE at
    Z=BAYOU_WATER_Z. Skipped inside the riverfront preservation
    zone (the riverfront's own water mesh handles that band)."""
    smooth = _smooth_polyline(BAYOU_CENTERLINE, samples_per_seg=6)
    print(f"[graustark] PHASE 2 water — smoothed centerline: "
          f"{len(smooth)} samples")

    # For each pair of consecutive samples, emit a quad
    # ±BAYOU_HALF_W along the perpendicular at the midpoint.
    BAYOU_HALF_W = 22.0   # 44 m wide water surface
    verts, faces = [], []
    skipped_in_rf = 0
    for i in range(len(smooth) - 1):
        x0, y0 = smooth[i]
        x1, y1 = smooth[i + 1]
        mx, my = (x0 + x1) / 2, (y0 + y1) / 2
        # Skip segments whose midpoint sits inside the RF zone —
        # riverfront's own water handles that band.
        if (RF_ZONE_X[0] <= mx <= RF_ZONE_X[1]
                and RF_ZONE_Y[0] <= my <= RF_ZONE_Y[1]):
            skipped_in_rf += 1
            continue
        dx, dy = x1 - x0, y1 - y0
        seg = math.hypot(dx, dy) or 1.0
        # Perpendicular (left-hand)
        nx, ny = -dy / seg, dx / seg
        # Four corners of the quad
        ax, ay = x0 + nx * BAYOU_HALF_W, y0 + ny * BAYOU_HALF_W
        bx, by = x0 - nx * BAYOU_HALF_W, y0 - ny * BAYOU_HALF_W
        cx, cy = x1 - nx * BAYOU_HALF_W, y1 - ny * BAYOU_HALF_W
        dx_, dy_ = x1 + nx * BAYOU_HALF_W, y1 + ny * BAYOU_HALF_W
        base = len(verts)
        for vx, vy in [(ax, ay), (bx, by), (cx, cy), (dx_, dy_)]:
            verts.append((vx, vy, BAYOU_WATER_Z))
        faces.append([base + 0, base + 1, base + 2])
        faces.append([base + 0, base + 2, base + 3])

    print(f"[graustark]   {skipped_in_rf} segments skipped (in RF zone)")
    if not faces:
        print("[graustark]   no bayou water emitted")
        return None
    mesh = bpy.data.meshes.new("Graustark_BayouWater_mesh")
    mesh.from_pydata(verts, [], faces)
    mesh.update()
    if not mesh.vertex_colors:
        mesh.vertex_colors.new(name="Col")
    layer = mesh.vertex_colors["Col"]
    for poly in mesh.polygons:
        for li in poly.loop_indices:
            layer.data[li].color = COL_BAYOU_WATER
    obj = bpy.data.objects.new("Graustark_BayouWater", mesh)
    bpy.context.collection.objects.link(obj)
    print(f"[graustark]   bayou water mesh: {len(verts)} verts, "
          f"{len(faces)} tris")
    return obj


# ── ROAD NETWORK ────────────────────────────────────────────────
# Each corridor is (name, waypoints [(x,y,z) raised-berm height],
# half-width m, surface colour). All declared Z values are AT
# ROAD GRADE — the visible berm appears wherever local terrain
# falls below the road Z.
COL_ASPHALT = (0.16, 0.16, 0.18, 1.0)
COL_GRAVEL  = (0.50, 0.48, 0.42, 1.0)
COL_LEVEE_LANE = (0.55, 0.52, 0.42, 1.0)
COL_SHOULDER = (0.30, 0.28, 0.22, 1.0)

# Roads stay BACK from the bayou's outer levee ridges (which peak
# at d≈110 from bayou) so the berm doesn't fight the levee crest.

GRAUSTARK_ROADS = [
    # HWY 90 — east-west interstate, raised berm, crosses bayou
    # via truss bridge at Y=-360 (visible from the riverfront in
    # the far distance).
    ("HWY90", [
        (-600.0, -360.0, +3.5),
        (-400.0, -360.0, +3.5),
        (-200.0, -362.0, +3.6),
        (   0.0, -360.0, +5.0),   # truss bridge crown over bayou
        (+200.0, -358.0, +3.6),
        (+400.0, -360.0, +3.5),
        (+600.0, -360.0, +3.5),
    ], 7.5, COL_ASPHALT),
    # State Route 12 — N-S commercial spine, WEST of the bayou
    # levee ridge so it runs along the dry side of the high ground.
    ("SR12",  [
        (-180.0, +420.0, +3.0),
        (-180.0, +260.0, +3.0),
        (-180.0,    0.0, +2.5),
        (-180.0, -260.0, +3.0),
        (-180.0, -420.0, +3.0),
    ], 6.5, COL_ASPHALT),
    # River Road NORTH extension — north of the riverfront zone,
    # parallel to the bayou's west bank.
    ("RiverRd_N", [
        ( -55.0, +200.0, +1.0),    # joins riverfront's River Rd at zone edge
        ( -55.0, +280.0, +1.2),
        ( -70.0, +360.0, +1.5),
        ( -90.0, +420.0, +1.8),
    ], 4.5, COL_ASPHALT),
    # River Road SOUTH extension — south of the riverfront zone.
    ("RiverRd_S", [
        ( -55.0, -200.0, +1.0),
        ( -55.0, -280.0, +1.5),
        ( -70.0, -340.0, +2.5),
        ( -85.0, -360.0, +3.5),    # meets HWY 90 berm at truss-bridge approach
    ], 4.5, COL_ASPHALT),
    # Wharf St — east-west cross-axis from SR12 to the riverfront.
    ("WharfSt", [
        (-180.0, +50.0, +2.4),
        (-120.0, +52.0, +2.0),
        ( -55.0, +55.0, +1.0),     # ties into River Road inside RF zone edge
    ], 4.0, COL_ASPHALT),
    # Levee-crown lane — gravel road on top of the WEST levee
    # crest. Follows the bayou's natural levee at d≈+110 m WEST.
    ("LeveeCrest_W", [
        ( -60.0, +420.0, +8.0),
        ( -70.0, +260.0, +8.2),
        ( -50.0, +130.0, +8.5),
        ( -85.0,    0.0, +7.8),
        ( -60.0, -130.0, +8.2),
        ( -90.0, -270.0, +8.0),
        ( -65.0, -420.0, +7.8),
    ], 2.5, COL_LEVEE_LANE),
]


def _emit_road_strip(name, waypoints, half_w, color):
    """Build a continuous asphalt strip from a waypoint list with
    declared Z grade. Each segment is a quad ±half_w perpendicular
    to the segment direction."""
    sm = _smooth_polyline([(x, y) for x, y, _ in waypoints],
                           samples_per_seg=4)
    # Interpolate Z along the smoothed line by mapping each sample
    # back to its parametric position along the original polyline.
    def interp_z(sample_idx):
        # Each original segment contributes 4 samples; round to
        # find which segment we're on.
        seg_i = min(len(waypoints) - 2,
                    sample_idx // 4)
        t = (sample_idx - seg_i * 4) / 4.0
        z0 = waypoints[seg_i][2]
        z1 = waypoints[seg_i + 1][2]
        return z0 + (z1 - z0) * t

    verts, faces = [], []
    for i in range(len(sm) - 1):
        x0, y0 = sm[i]; x1, y1 = sm[i + 1]
        z0 = interp_z(i); z1 = interp_z(i + 1)
        dx, dy = x1 - x0, y1 - y0
        seg = math.hypot(dx, dy) or 1.0
        nx, ny = -dy / seg, dx / seg
        base = len(verts)
        verts.append((x0 + nx * half_w, y0 + ny * half_w, z0))
        verts.append((x0 - nx * half_w, y0 - ny * half_w, z0))
        verts.append((x1 - nx * half_w, y1 - ny * half_w, z1))
        verts.append((x1 + nx * half_w, y1 + ny * half_w, z1))
        faces.append([base + 0, base + 1, base + 2])
        faces.append([base + 0, base + 2, base + 3])
    if not faces:
        return None
    mesh = bpy.data.meshes.new(f"Graustark_Road_{name}_mesh")
    mesh.from_pydata(verts, [], faces)
    mesh.update()
    if not mesh.vertex_colors:
        mesh.vertex_colors.new(name="Col")
    layer = mesh.vertex_colors["Col"]
    for poly in mesh.polygons:
        for li in poly.loop_indices:
            layer.data[li].color = color
    obj = bpy.data.objects.new(f"Graustark_Road_{name}", mesh)
    bpy.context.collection.objects.link(obj)
    return obj


def build_district_roads():
    """PHASE 3 — major road arterials. Each road is a raised
    berm (declared Z at each waypoint) that reads as paved
    surface ABOVE local terrain. River Rd N/S join the
    riverfront's existing River Road at the preservation-zone
    edge; HWY 90 has its truss-bridge crown over the bayou."""
    print(f"[graustark] PHASE 3 roads — {len(GRAUSTARK_ROADS)} corridors")
    for name, waypoints, half_w, color in GRAUSTARK_ROADS:
        _emit_road_strip(name, waypoints, half_w, color)
        print(f"[graustark]   road {name}: "
              f"{len(waypoints)} waypoints, half_w={half_w}m")


# HCE builders we borrow. The module-level mesh_z lookup is
# redirected so HCE's _build_suburban_house samples OUR elevation
# field instead of HCE's.
import build_harmony_terrain as ht


def _hook_hce_mesh_z():
    """Redirect HCE's mesh_z to graustark_elevation so reused HCE
    builders read our terrain rather than HCE's."""
    ht.mesh_z = lambda x, y: graustark_elevation(x, y)


# ── WESTERN SUBURBAN GRID  (Lafayette-style residential) ────────
# Houses arranged west of SR12, north of the truss-bridge HWY 90.
# Six rows × five lots = 30 lots, 40m grid spacing. Position-seeded
# palette so the neighbourhood reads as mixed era.

_LAF_PALETTES = [
    {'wall': (0.92, 0.84, 0.62, 1.0), 'roof': (0.32, 0.18, 0.14, 1.0)},  # yellow + brown
    {'wall': (0.86, 0.78, 0.74, 1.0), 'roof': (0.42, 0.30, 0.22, 1.0)},  # cream + chocolate
    {'wall': (0.72, 0.84, 0.74, 1.0), 'roof': (0.32, 0.30, 0.26, 1.0)},  # sage + slate
    {'wall': (0.96, 0.92, 0.84, 1.0), 'roof': (0.18, 0.18, 0.22, 1.0)},  # white + black tin
    {'wall': (0.80, 0.66, 0.52, 1.0), 'roof': (0.46, 0.32, 0.20, 1.0)},  # tan + dark brown
    {'wall': (0.66, 0.72, 0.84, 1.0), 'roof': (0.38, 0.28, 0.22, 1.0)},  # pale blue + brown
]


def _build_western_residential():
    """30-lot Lafayette suburban grid west of SR12, on the dry
    side of the west levee ridge. Uses HCE's _build_suburban_house
    with Louisiana palettes."""
    print("[graustark]   western residential — 30 lots")
    LOT_GRID_X = [-540, -480, -420, -360, -300]   # 5 cols, 60m
    LOT_GRID_Y = [+360, +290, +220, +150, +80, +10]  # 6 rows, 70m apart
    count = 0
    for ri, gy in enumerate(LOT_GRID_Y):
        for ci, gx in enumerate(LOT_GRID_X):
            # Skip a few lots for parks / empty space
            if (ri == 2 and ci == 2) or (ri == 4 and ci == 4):
                continue
            seed = (abs(int(gx * 7) + int(gy * 11))) % 100
            pal_i = seed % len(_LAF_PALETTES)
            facing = '-Y' if ri % 2 == 0 else '+Y'
            gz = graustark_elevation(gx, gy)
            ht._build_suburban_house(
                f"Graustark_West_House_R{ri}_C{ci}",
                gx, gy, gz, facing=facing,
                palette=_LAF_PALETTES[pal_i])
            count += 1
    print(f"[graustark]     placed {count} western houses")


# ── CYPRESS TREES along the bayou ──────────────────────────────
COL_CYPRESS_TRUNK = (0.30, 0.22, 0.16, 1.0)
COL_CYPRESS_CANOPY = (0.30, 0.42, 0.28, 1.0)
COL_SPANISH_MOSS  = (0.52, 0.56, 0.46, 1.0)


def _emit_cypress(name, cx, cy, cz):
    """Single cypress: stubby trunk, broad layered canopy, hint
    of Spanish moss draped underneath. Reuses HCE's low-poly
    primitives so the tri-count stays comparable to HCE trees."""
    trunk_h = 5.5
    canopy_r = 3.2
    ht._make_cyl_local(f"{name}_Trunk",
                       (cx, cy, cz + trunk_h / 2),
                       0.35, trunk_h, COL_CYPRESS_TRUNK, segments=6)
    # Two stacked canopy spheres for the wider cypress profile
    ht._make_sphere_low_local(
        f"{name}_Canopy_Lo",
        (cx, cy, cz + trunk_h + canopy_r * 0.4),
        canopy_r, COL_CYPRESS_CANOPY, rings=3, segments=8)
    ht._make_sphere_low_local(
        f"{name}_Canopy_Hi",
        (cx, cy, cz + trunk_h + canopy_r * 1.1),
        canopy_r * 0.78, COL_CYPRESS_CANOPY, rings=3, segments=8)
    # Spanish moss — small dangling sphere under the canopy
    ht._make_sphere_low_local(
        f"{name}_Moss",
        (cx + 0.6, cy, cz + trunk_h + canopy_r * 0.2),
        0.5, COL_SPANISH_MOSS, rings=2, segments=6)


def _build_bayou_cypress_groves():
    """Cypress trees scattered along the bayou centerline, planted
    in the tidal mud-flat band (d=10..30m from bayou) where they
    grow in real delta wetlands. Skipped inside the RF zone."""
    sm = _smooth_polyline(BAYOU_CENTERLINE, samples_per_seg=4)
    count = 0
    for i, (sx, sy) in enumerate(sm):
        # Plant ON the tidal flat — d ≈ 18m perpendicular to centerline.
        # Compute perpendicular at this sample.
        if i + 1 < len(sm):
            x1, y1 = sm[i + 1]
        else:
            x1, y1 = sm[i - 1]
        dx, dy = x1 - sx, y1 - sy
        seg = math.hypot(dx, dy) or 1
        nx, ny = -dy / seg, dx / seg
        for side_sgn in (-1, +1):
            tx = sx + nx * 18 * side_sgn
            ty = sy + ny * 18 * side_sgn
            # Skip if inside RF zone (riverfront has its own cypress
            # already in build_bayou)
            if (RF_ZONE_X[0] <= tx <= RF_ZONE_X[1]
                    and RF_ZONE_Y[0] <= ty <= RF_ZONE_Y[1]):
                continue
            # Plant on the tidal flat — Z is local terrain
            tz = graustark_elevation(tx, ty)
            # Skip if we landed in deep water
            if tz < -1.5:
                continue
            # Position-seeded skip so the groves aren't perfectly
            # regular (only place a tree at ~70% of candidate spots)
            seed = (abs(int(tx * 13) + int(ty * 17))) % 100
            if seed > 70:
                continue
            _emit_cypress(f"Graustark_Cypress_{i}_{side_sgn:+d}",
                          tx, ty, tz)
            count += 1
    print(f"[graustark]   cypress trees along bayou: {count} placed")


# ── RAISED COTTAGE  (Lafayette signature on cypress stilts) ─────
# Distinctive delta-town building type. Single-story shotgun
# proportions, ~6m wide × 12m deep, sitting on 6-8 visible cypress
# pilings with 1.8-2.5m crawl space, full-width front porch,
# low-pitch hipped or gabled roof in standing-seam tin.

# Pastel weathered wall colours — the Lafayette look.
_COTTAGE_PALETTES = [
    {'wall': (0.96, 0.92, 0.74, 1.0), 'trim': (0.94, 0.94, 0.92, 1.0),
     'roof': (0.62, 0.64, 0.66, 1.0)},  # pale yellow + tin
    {'wall': (0.92, 0.74, 0.76, 1.0), 'trim': (0.96, 0.94, 0.92, 1.0),
     'roof': (0.58, 0.60, 0.60, 1.0)},  # soft pink + tin
    {'wall': (0.68, 0.78, 0.84, 1.0), 'trim': (0.96, 0.94, 0.92, 1.0),
     'roof': (0.56, 0.58, 0.58, 1.0)},  # pale blue-grey + tin
    {'wall': (0.78, 0.88, 0.78, 1.0), 'trim': (0.94, 0.92, 0.88, 1.0),
     'roof': (0.60, 0.62, 0.62, 1.0)},  # mint + tin
    {'wall': (0.90, 0.86, 0.78, 1.0), 'trim': (0.92, 0.74, 0.42, 1.0),
     'roof': (0.46, 0.42, 0.38, 1.0)},  # cream + ochre trim + dark tin
]
COL_PILING = (0.30, 0.22, 0.16, 1.0)        # cypress wood
COL_PORCH_FLOOR = (0.55, 0.42, 0.30, 1.0)


def _build_raised_cottage(name, cx, cy, ground_z, facing='-Y',
                           palette_idx=0):
    """Shotgun-style Lafayette cottage on stilts. The body floats
    1.8-2.5m above grade on visible cypress pilings."""
    pal = _COTTAGE_PALETTES[palette_idx % len(_COTTAGE_PALETTES)]
    col_wall = pal['wall']
    col_trim = pal['trim']
    col_roof = pal['roof']

    # Facing axis
    fx, fy = 0, 0
    if   facing == '-Y': fy = -1
    elif facing == '+Y': fy = +1
    elif facing == '-X': fx = -1
    elif facing == '+X': fx = +1
    px, py = -fy, fx     # perpendicular (right hand)

    # Footprint
    body_w = 6.0           # narrow (perpendicular to facing)
    body_d = 12.0          # deep (along facing axis, shotgun length)
    body_h = 2.8
    crawl_h = 2.1          # piling height (visible crawl)
    porch_d = 1.6
    roof_h = 1.4
    eave_overhang = 0.50

    # Body orientation: if facing is along Y, body_d runs along Y;
    # if facing is along X, body_d runs along X.
    if abs(fx) > 0.5:
        size_xy = (body_d, body_w)
    else:
        size_xy = (body_w, body_d)
    body_cx, body_cy = cx, cy
    body_z = ground_z + crawl_h + body_h / 2

    # ── Pilings (6 cypress posts, 3 each side along facing axis) ──
    n_piles = 3
    for i in range(n_piles):
        # Distribute along facing axis from -body_d/2+0.6 to +body_d/2-0.6
        t = -1 + 2 * i / (n_piles - 1) if n_piles > 1 else 0
        along = t * (body_d / 2 - 0.6)
        for side in (-1, +1):
            perp = side * (body_w / 2 - 0.3)
            if abs(fx) > 0.5:
                pcx = cx + along
                pcy = cy + perp
            else:
                pcx = cx + perp
                pcy = cy + along
            ht._make_box_local(
                f"{name}_Piling_{i}_{side:+d}",
                (pcx, pcy, ground_z + crawl_h / 2),
                (0.28, 0.28, crawl_h), COL_PILING)

    # ── Body ───────────────────────────────────────────────────
    ht._make_box_local(
        f"{name}_Body",
        (body_cx, body_cy, body_z),
        (size_xy[0], size_xy[1], body_h), col_wall)

    # Floor underside (visible from below, planks)
    floor_z = ground_z + crawl_h
    ht._make_box_local(
        f"{name}_Floor",
        (body_cx, body_cy, floor_z - 0.04),
        (size_xy[0] + 0.08, size_xy[1] + 0.08, 0.08), col_trim)

    # ── Porch ──────────────────────────────────────────────────
    # Front face is at -fx, -fy direction from center
    porch_along = -(body_d / 2 + porch_d / 2)
    if abs(fx) > 0.5:
        porch_cx = cx + porch_along * fx
        porch_cy = cy
        porch_size = (porch_d, body_w, 0.10)
    else:
        porch_cx = cx
        porch_cy = cy + porch_along * fy
        porch_size = (body_w, porch_d, 0.10)
    ht._make_box_local(
        f"{name}_Porch_Deck",
        (porch_cx, porch_cy, floor_z + 0.05),
        porch_size, COL_PORCH_FLOOR)

    # Porch railing posts — 4 along the front edge
    front_edge_along = -(body_d / 2 + porch_d)
    for j in range(4):
        t = -1 + 2 * j / 3
        side = t * (body_w / 2 - 0.2)
        if abs(fx) > 0.5:
            rx = cx + front_edge_along * fx
            ry = cy + side
        else:
            rx = cx + side
            ry = cy + front_edge_along * fy
        ht._make_box_local(
            f"{name}_Porch_Post_{j}",
            (rx, ry, floor_z + 0.10 + 1.10 / 2),
            (0.14, 0.14, 1.10), col_trim)

    # ── Roof — low-pitch hipped (4-sided wedge) ────────────────
    # Built as two prism halves so it reads as hipped from any
    # angle. For simplicity, use a stretched pyramid: top box at
    # half-size, sloping faces baked in.
    eave_z = body_z + body_h / 2
    roof_apex_z = eave_z + roof_h
    # Top ridge box (small, oriented along body_d)
    if abs(fx) > 0.5:
        ridge_size = (body_d * 0.50, 0.4, 0.20)
    else:
        ridge_size = (0.4, body_d * 0.50, 0.20)
    ht._make_box_local(
        f"{name}_Roof_Ridge",
        (cx, cy, roof_apex_z),
        ridge_size, col_roof)
    # Eaves on the four sides — flat skirt
    ht._make_box_local(
        f"{name}_Roof_Eaves",
        (cx, cy, eave_z + roof_h * 0.35),
        (size_xy[0] + eave_overhang * 2,
         size_xy[1] + eave_overhang * 2, roof_h * 0.30),
        col_roof)

    # Front door
    door_z = floor_z + 1.0
    door_along = -(body_d / 2 - 0.05)
    if abs(fx) > 0.5:
        dcx = cx + door_along * fx
        dcy = cy
        dsize = (0.10, 0.95, 2.10)
    else:
        dcx = cx
        dcy = cy + door_along * fy
        dsize = (0.95, 0.10, 2.10)
    ht._make_box_local(
        f"{name}_Door",
        (dcx, dcy, door_z),
        dsize, (0.46, 0.30, 0.22, 1.0))


def _build_levee_cottages():
    """Cottages on stilts along the WEST levee crest lane. The
    high ground gives them dry feet; the bayou view defines the
    front porch direction."""
    print("[graustark]   levee-crest raised cottages")
    # Place along the LeveeCrest_W road's smoothed polyline,
    # alternating sides (porch facing the bayou ≈ east).
    levee_road = next(r for r in GRAUSTARK_ROADS if r[0] == 'LeveeCrest_W')
    sm = _smooth_polyline([(w[0], w[1]) for w in levee_road[1]],
                          samples_per_seg=8)
    count = 0
    for i in range(0, len(sm), 3):       # roughly every 3rd sample
        sx, sy = sm[i]
        # Skip if too close to riverfront zone
        if (RF_ZONE_X[0] - 30 <= sx <= RF_ZONE_X[1] + 30
                and RF_ZONE_Y[0] - 30 <= sy <= RF_ZONE_Y[1] + 30):
            continue
        # Place 18m east of the road (toward the bayou)
        # Find perpendicular at this sample
        if i + 1 < len(sm):
            x1, y1 = sm[i + 1]
        else:
            x1, y1 = sm[i - 1]
        dx, dy = x1 - sx, y1 - sy
        seg = math.hypot(dx, dy) or 1
        nx, ny = -dy / seg, dx / seg
        # East side
        cx = sx + nx * 22
        cy = sy + ny * 22
        gz = graustark_elevation(cx, cy)
        # Skip if we'd land in wet/below-sea-level ground
        if gz < +1.0:
            continue
        seed = (abs(int(cx * 19) + int(cy * 23))) % 100
        _build_raised_cottage(
            f"Graustark_LeveeCottage_{i}",
            cx, cy, gz, facing='+X',     # porch toward bayou
            palette_idx=seed % len(_COTTAGE_PALETTES))
        count += 1
    print(f"[graustark]     placed {count} levee-crest cottages")


# ── FACADE BLOCKS  (film-set theory — fronts detailed, backs cheated) ──
# Each "block" is a short row of facade-detailed buildings. The
# back walls and roofs are simplified because the player only
# ever walks the front. Two blocks: French Quarter (NOLA flavour)
# anchoring the restaurant, and a Montreal block tucked into the
# NE corner.

_FQ_PALETTES = [
    {'wall': (0.94, 0.78, 0.66, 1.0), 'trim': (0.96, 0.94, 0.86, 1.0),
     'iron': (0.10, 0.08, 0.08, 1.0)},  # peach + cream
    {'wall': (0.96, 0.88, 0.62, 1.0), 'trim': (0.92, 0.90, 0.84, 1.0),
     'iron': (0.10, 0.08, 0.08, 1.0)},  # yellow ochre
    {'wall': (0.86, 0.66, 0.62, 1.0), 'trim': (0.96, 0.92, 0.86, 1.0),
     'iron': (0.10, 0.08, 0.08, 1.0)},  # faded rose
    {'wall': (0.76, 0.78, 0.66, 1.0), 'trim': (0.94, 0.92, 0.84, 1.0),
     'iron': (0.10, 0.08, 0.08, 1.0)},  # sage
    {'wall': (0.94, 0.86, 0.74, 1.0), 'trim': (0.86, 0.70, 0.42, 1.0),
     'iron': (0.10, 0.08, 0.08, 1.0)},  # cream + ochre trim
]
_MONTREAL_PALETTES = [
    {'wall': (0.62, 0.36, 0.28, 1.0), 'trim': (0.94, 0.92, 0.86, 1.0),
     'roof': (0.22, 0.20, 0.20, 1.0)},  # red brick + cream + slate
    {'wall': (0.74, 0.70, 0.62, 1.0), 'trim': (0.96, 0.94, 0.88, 1.0),
     'roof': (0.18, 0.18, 0.20, 1.0)},  # limestone grey
    {'wall': (0.52, 0.40, 0.32, 1.0), 'trim': (0.94, 0.92, 0.84, 1.0),
     'roof': (0.20, 0.18, 0.22, 1.0)},  # darker brick
    {'wall': (0.66, 0.62, 0.54, 1.0), 'trim': (0.96, 0.92, 0.84, 1.0),
     'roof': (0.18, 0.16, 0.16, 1.0)},  # warm limestone
]

COL_FQ_BALCONY_FLOOR = (0.18, 0.14, 0.10, 1.0)
COL_FQ_WINDOW = (0.18, 0.22, 0.30, 1.0)
COL_RESTAURANT_SIGN = (0.82, 0.32, 0.28, 1.0)
COL_RESTAURANT_TEXT = (0.96, 0.92, 0.74, 1.0)


def _build_fq_rowhouse(name, cx, cy, ground_z, facing, palette,
                       has_restaurant=False, idx=0):
    """One French Quarter row house. 2-storey, pastel stucco, full-
    width wrought-iron balcony, tall arched window pattern. Faces
    the street; back wall is flat to save tris (film-set cheat)."""
    fx, fy = 0, 0
    if facing == '-Y': fy = -1
    elif facing == '+Y': fy = +1
    elif facing == '-X': fx = -1
    elif facing == '+X': fx = +1
    px, py = -fy, fx
    W, D, H = 7.0, 10.0, 7.8

    if abs(fx) > 0.5:
        size = (D, W, H)
    else:
        size = (W, D, H)
    body_z = ground_z + H / 2
    # Body block
    ht._make_box_local(f"{name}_Body",
                       (cx, cy, body_z),
                       size, palette['wall'])
    # Lower trim band (between ground floor and balcony)
    band_z = ground_z + 3.8
    if abs(fx) > 0.5:
        band_size = (D + 0.05, W + 0.30, 0.20)
    else:
        band_size = (W + 0.30, D + 0.05, 0.20)
    ht._make_box_local(f"{name}_Band",
                       (cx, cy, band_z), band_size, palette['trim'])
    # Roofline cornice
    cornice_z = ground_z + H - 0.10
    ht._make_box_local(f"{name}_Cornice",
                       (cx, cy, cornice_z),
                       (size[0] + 0.30, size[1] + 0.30, 0.20),
                       palette['trim'])

    # ── BALCONY  (wrought iron, full street-facing width) ─────
    front_along = -(D / 2 + 0.5)
    if abs(fx) > 0.5:
        bcx = cx + front_along * fx
        bcy = cy
        bsize_floor = (1.0, W, 0.12)
    else:
        bcx = cx
        bcy = cy + front_along * fy
        bsize_floor = (W, 1.0, 0.12)
    ht._make_box_local(f"{name}_BalconyFloor",
                       (bcx, bcy, band_z + 0.20),
                       bsize_floor, COL_FQ_BALCONY_FLOOR)
    # Iron railing — thin top rail + posts
    rail_z = band_z + 0.20 + 0.55
    ht._make_box_local(f"{name}_BalconyRail",
                       (bcx, bcy, rail_z),
                       (bsize_floor[0] * 0.98,
                        bsize_floor[1] * 0.98, 0.05),
                       palette['iron'])
    # Iron support brackets dropping from underside (pure decor)
    for s in range(3):
        t = -1 + 2 * s / 2
        if abs(fx) > 0.5:
            bx = bcx; by_ = bcy + t * (W / 2 - 0.5)
        else:
            bx = bcx + t * (W / 2 - 0.5); by_ = bcy
        ht._make_box_local(f"{name}_BalconyBracket_{s}",
                           (bx, by_, band_z + 0.08),
                           (0.10, 0.10, 0.30), palette['iron'])

    # ── WINDOWS  (tall narrow on the upper floor) ─────────────
    win_h = 1.80
    win_w = 0.55
    win_z = band_z + 0.20 + win_h / 2 + 0.30
    # Three windows on the upper floor street face
    front_face_along = -(D / 2 + 0.02)
    for w in range(3):
        t = -1 + 2 * w / 2
        if abs(fx) > 0.5:
            wx = cx + front_face_along * fx
            wy = cy + t * (W / 2 - 0.7)
            wsize = (0.05, win_w, win_h)
        else:
            wx = cx + t * (W / 2 - 0.7)
            wy = cy + front_face_along * fy
            wsize = (win_w, 0.05, win_h)
        ht._make_box_local(f"{name}_Window_Up_{w}",
                           (wx, wy, win_z), wsize, COL_FQ_WINDOW)

    # Ground-floor storefront / door
    if abs(fx) > 0.5:
        dwx = cx + front_face_along * fx
        dwy = cy
        dwsize = (0.05, W * 0.65, 2.40)
    else:
        dwx = cx
        dwy = cy + front_face_along * fy
        dwsize = (W * 0.65, 0.05, 2.40)
    ht._make_box_local(f"{name}_Storefront",
                       (dwx, dwy, ground_z + 1.20),
                       dwsize, COL_FQ_WINDOW)

    # ── RESTAURANT SIGN  (only on the marked building) ────────
    if has_restaurant:
        sign_z = ground_z + 3.20
        sign_h = 0.6
        sign_w = W * 0.55
        if abs(fx) > 0.5:
            scx = cx + front_face_along * 1.05 * fx
            scy = cy
            ss = (0.20, sign_w, sign_h)
        else:
            scx = cx
            scy = cy + front_face_along * 1.05 * fy
            ss = (sign_w, 0.20, sign_h)
        ht._make_box_local(f"{name}_RestaurantSign",
                           (scx, scy, sign_z), ss,
                           COL_RESTAURANT_SIGN)


def _build_french_quarter_block():
    """Compact 5-building French Quarter row on a side street off
    of Wharf St. The restaurant occupies the middle building."""
    print("[graustark]   french quarter block")
    block_cx = -320.0
    block_cy = +90.0      # north of Wharf St
    # 5 buildings in a row along Y, all facing -X (street to the west)
    spacing_y = 8.0       # adjacent buildings touch
    for i in range(5):
        bx = block_cx + 0.0
        by = block_cy + (i - 2) * spacing_y
        gz = graustark_elevation(bx, by)
        pal = _FQ_PALETTES[i % len(_FQ_PALETTES)]
        _build_fq_rowhouse(
            f"Graustark_FQ_Row_{i}", bx, by, gz,
            facing='-X',                # street is to the west
            palette=pal,
            has_restaurant=(i == 2),    # middle = restaurant
            idx=i)
    # Street strip in front (cobblestone hint)
    street_cx = block_cx - 10.0
    street_cy = block_cy
    ht._make_box_local("Graustark_FQ_Street",
                       (street_cx, street_cy,
                        graustark_elevation(street_cx, street_cy) + 0.02),
                       (8.0, 5 * spacing_y + 4.0, 0.04),
                       (0.32, 0.30, 0.30, 1.0))
    print(f"[graustark]     placed 5 FQ row buildings "
          f"(restaurant at i=2)")


def _build_montreal_rowhouse(name, cx, cy, ground_z, facing, palette):
    """Montreal-style row house: limestone/brick body + mansard
    roof + dormer windows + outdoor staircase."""
    fx, fy = 0, 0
    if facing == '-Y': fy = -1
    elif facing == '+Y': fy = +1
    elif facing == '-X': fx = -1
    elif facing == '+X': fx = +1
    W, D, body_H = 8.0, 11.0, 6.5
    mansard_H = 2.5

    if abs(fx) > 0.5:
        body_size = (D, W, body_H)
    else:
        body_size = (W, D, body_H)
    body_z = ground_z + body_H / 2
    ht._make_box_local(f"{name}_Body",
                       (cx, cy, body_z), body_size, palette['wall'])
    # Mansard roof — taller wedge on top, slightly inset on sides
    mansard_z = ground_z + body_H + mansard_H / 2
    if abs(fx) > 0.5:
        mansard_size = (D * 0.98, W * 0.85, mansard_H)
    else:
        mansard_size = (W * 0.85, D * 0.98, mansard_H)
    ht._make_box_local(f"{name}_Mansard",
                       (cx, cy, mansard_z), mansard_size,
                       palette['roof'])
    # Dormer — small box on the mansard front
    front_along = -(D / 2 + 0.01)
    dormer_z = ground_z + body_H + 1.4
    if abs(fx) > 0.5:
        dox = cx + front_along * fx
        doy = cy
        dosize = (0.40, 1.20, 1.40)
    else:
        dox = cx
        doy = cy + front_along * fy
        dosize = (1.20, 0.40, 1.40)
    ht._make_box_local(f"{name}_Dormer",
                       (dox, doy, dormer_z),
                       dosize, palette['roof'])
    # Tall narrow windows — 4 on upper floor
    win_z = ground_z + body_H * 0.75
    for w in range(4):
        t = -1 + 2 * w / 3
        if abs(fx) > 0.5:
            wx = cx + front_along * fx
            wy = cy + t * (W / 2 - 0.6)
            ws = (0.05, 0.50, 1.30)
        else:
            wx = cx + t * (W / 2 - 0.6)
            wy = cy + front_along * fy
            ws = (0.50, 0.05, 1.30)
        ht._make_box_local(f"{name}_Win_Up_{w}",
                           (wx, wy, win_z), ws, COL_FQ_WINDOW)
    # External staircase up to second-floor entrance (Montreal trademark)
    stair_along = -(D / 2 + 0.8)
    for s in range(4):
        st_z = ground_z + 0.5 + s * 0.5
        if abs(fx) > 0.5:
            sx = cx + stair_along * fx
            sy = cy + (W / 2 - 1.0)
            ss = (1.2 - s * 0.2, 0.8, 0.30)
        else:
            sx = cx + (W / 2 - 1.0)
            sy = cy + stair_along * fy
            ss = (0.8, 1.2 - s * 0.2, 0.30)
        ht._make_box_local(f"{name}_Stair_{s}",
                           (sx, sy, st_z), ss, palette['trim'])


def _build_montreal_block():
    """Montreal block tucked into the NE corner — limestone +
    brick row houses with mansard roofs + outdoor staircases."""
    print("[graustark]   montreal block (NE corner)")
    block_cx = +480.0
    block_cy = +330.0
    spacing_x = 9.5
    for i in range(4):
        bx = block_cx + (i - 1.5) * spacing_x
        by = block_cy
        gz = graustark_elevation(bx, by)
        pal = _MONTREAL_PALETTES[i % len(_MONTREAL_PALETTES)]
        _build_montreal_rowhouse(
            f"Graustark_Montreal_Row_{i}", bx, by, gz,
            facing='-Y', palette=pal)
    # Cobblestone street strip in front
    street_cy = block_cy - 11.0
    ht._make_box_local("Graustark_Montreal_Street",
                       (block_cx, street_cy,
                        graustark_elevation(block_cx, street_cy) + 0.02),
                       (4 * spacing_x + 2.0, 5.0, 0.04),
                       (0.34, 0.32, 0.30, 1.0))
    print(f"[graustark]     placed 4 Montreal row buildings")


def build_district_buildings():
    """PHASE 4 — buildings outside the riverfront's SE quadrant.
    Pass 4a: western suburban + cypress groves.
    Pass 4b: raised cottages on cypress stilts (levee crest).
    Pass 4c: French Quarter block (with restaurant) + Montreal
             block in NE corner. Both done film-set style —
             fronts detailed, backs cheated."""
    _hook_hce_mesh_z()
    _build_western_residential()
    _build_bayou_cypress_groves()
    _build_levee_cottages()
    _build_french_quarter_block()
    _build_montreal_block()


def build_district_characters_and_props():
    """PHASE 5 — NPCs + propscape.

    Pulls from:
      godot/assets/3d/characters/human_male_base.glb
      godot/assets/3d/characters/human_female_base.glb
    as the two canonical baselines (confirmed 2026-06-16). Body-
    type variants ride on top via shape-key deformation, not new
    base sculpts.

    TODO:
      - Spawn anchors on porches, town square, dock, cemetery
      - Variant displacement params per NPC seed
      - Prop pass: cypress trees, palms, oyster-shell piles,
        fishing gear, kid bikes, beads on balconies, Mardi Gras
        banner across one downtown block
    """
    print("[graustark] PHASE 5 characters + props — STUB")


# ── EXPORT (own copy so we write graustark.glb, not riverfront.glb) ──

def export_glb():
    out_dir = os.path.normpath(os.path.join(_SCRIPT_DIR, OUTPUT_DIR))
    os.makedirs(out_dir, exist_ok=True)
    out_path = os.path.join(out_dir, OUTPUT_NAME)
    print(f"\n[graustark] exporting to {out_path}")
    print(f"[graustark] scene objects: {len(bpy.context.scene.objects)}")
    bpy.ops.object.select_all(action='SELECT')
    base = {
        'filepath': out_path, 'export_format': 'GLB',
        'use_selection': False, 'export_apply': True,
        'export_lights': False, 'export_cameras': False,
    }
    rna = bpy.ops.export_scene.gltf.get_rna_type()
    legacy = {}
    if 'export_colors' in rna.properties:
        legacy['export_colors'] = True
    if 'export_normals' in rna.properties:
        legacy['export_normals'] = True
    bpy.ops.export_scene.gltf(**base, **legacy)
    if os.path.exists(out_path):
        size = os.path.getsize(out_path)
        print(f"[graustark] ✓ wrote {out_path} ({size} bytes)")
    else:
        raise RuntimeError("GLB not written")


# ── MAIN ────────────────────────────────────────────────────────

def main():
    # Phase 0 — riverfront. Each rf.build_* writes into the scene.
    # We mirror riverfront's main() build order verbatim so the
    # SE-quadrant content matches the canonical riverfront.glb.
    rf.clear_scene()
    rf.build_ground()
    rf.build_road_network()
    rf.build_riverboat()
    rf.build_parking_lot()
    rf.build_dock()
    rf.build_river()
    rf.build_near_shore()
    rf.build_westbrook_residential()
    rf.build_opposite_shore()
    rf.build_other_boats()
    rf.build_bayou()
    rf.build_far_horizons()
    rf.build_distant_atmosphere()

    # Phases 1-5 — district expansion (currently stubs).
    build_district_elevation_field()
    build_district_water_layer()
    build_district_roads()
    build_district_buildings()
    build_district_characters_and_props()

    export_glb()


if __name__ == "__main__":
    main()
