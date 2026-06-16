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
import build_harmony_terrain as ht

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


# ── ARCANA LOCALE REGISTRY  ─────────────────────────────────────
# Coordinates for every Major Arcana exterior. See
# lore/_GRAUSTARK_ARCANA_LOCALES.md for the canon + style spec.
# Each entry: arcana name → (x, y, status). Status is one of:
#   'preserved'  — already in build_riverfront, no new build needed
#   'placed'     — placeholder geometry exists from earlier phases
#   'todo'       — coordinates locked, geometry not yet built
ARCANA_LOCALES = {
    'Fool_Diner':        ((    0.0,    0.0), 'preserved'),
    'Empress_BoatDeck':  ((    0.0,    4.0), 'preserved'),
    'Emperor_HelmCabin': ((    0.0,    9.0), 'preserved'),
    'HighPriestess_Curio': ((-320.0, +66.0), 'placed'),    # FQ row N end
    'HangedMan_Apartment': ((-320.0, +98.0), 'placed'),    # FQ row S end
    'Temperance_Lounge':  ((-310.0, +130.0), 'placed'),
    'Magician_Cathedral': ((+300.0, +380.0), 'placed'),
    'Hierophant_Church':  ((-200.0, +200.0), 'placed'),
    'Hierophant_Bandstand': ((-150.0, +120.0), 'placed'),
    'Hierophant_Armory':  ((+200.0, -340.0), 'placed'),
    'Lovers_Chapel':      ((-560.0, -120.0), 'placed'),
    'Chariot_Garage':     ((-180.0, -160.0), 'placed'),
    'Strength_Carnival':  ((-460.0, +400.0), 'placed'),
    'Hermit_Lighthouse':  (( +50.0, -380.0), 'placed'),
    'Wheel_Casino':       ((-200.0, +300.0), 'placed'),
    'Justice_Courthouse': ((-130.0, +250.0), 'placed'),
    'Death_Hospital':     ((-460.0, -340.0), 'placed'),
    'Devil_Roadhouse':    ((+260.0, -380.0), 'placed'),
    'Tower_Broadcast':    ((+400.0, +380.0), 'placed'),
    'Star_IceCo':         ((+180.0, -300.0), 'placed'),
    'Moon_DriveIn':       ((-500.0, +200.0), 'placed'),
    'Sun_Garden':         ((-120.0, +120.0), 'placed'),
    'Judgement_Cemetery': ((-360.0, -200.0), 'placed'),
    'World_FrogShop':     ((+150.0, +300.0), 'placed'),
}


def report_arcana_status():
    """Diagnostic — count locales by status for the build log."""
    by_status = {}
    for name, (_, status) in ARCANA_LOCALES.items():
        by_status[status] = by_status.get(status, 0) + 1
    print(f"[graustark] arcana locales: "
          + ", ".join(f"{k}={v}" for k, v in sorted(by_status.items())))





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


# ── ARCANA EXTERIORS (priority-1 build order) ───────────────────
# Each builder lays one canonical narrative-locale building at
# its ARCANA_LOCALES coordinates. All use ht._make_*_local
# primitives so the geometry ships in the same vertex-colour
# pipeline as everything else.

COL_BRICK_RED       = (0.50, 0.32, 0.26, 1.0)
COL_BRICK_DARK      = (0.36, 0.24, 0.20, 1.0)
COL_TIN_RUSTED      = (0.42, 0.36, 0.28, 1.0)
COL_TIN_FRESH       = (0.60, 0.62, 0.64, 1.0)
COL_SHEET_METAL     = (0.46, 0.46, 0.44, 1.0)
COL_LIMESTONE       = (0.78, 0.74, 0.66, 1.0)
COL_STUCCO_WHITE    = (0.88, 0.84, 0.78, 1.0)
COL_STUCCO_CREAM    = (0.92, 0.86, 0.74, 1.0)
COL_CONCRETE        = (0.68, 0.66, 0.62, 1.0)
COL_GLASS_DARK      = (0.18, 0.22, 0.30, 1.0)
COL_NEON_RED        = (0.92, 0.20, 0.18, 1.0)
COL_NEON_PINK       = (0.95, 0.42, 0.62, 1.0)
COL_DOOR_DARK       = (0.32, 0.22, 0.18, 1.0)
COL_BLACK_IRON      = (0.10, 0.08, 0.08, 1.0)


def _build_magician_cathedral():
    """The Cathedral of Rust and Code — Frasier's converted 1920s
    warehouse. Brick body with buttresses + pitched corrugated tin
    roof, boarded arched windows on the long sides, antenna farm +
    satellite dish on the roof + roof-line vent stacks. Must read
    from anywhere in town as a silhouette anchor for the NE."""
    print("[graustark]   Magician — Cathedral of Rust and Code")
    cx, cy = ARCANA_LOCALES['Magician_Cathedral'][0]
    gz = graustark_elevation(cx, cy)
    W, D, H = 22.0, 42.0, 11.0
    # Main warehouse body
    ht._make_box_local("Magician_Cath_Body",
                       (cx, cy, gz + H / 2),
                       (W, D, H), COL_BRICK_RED)
    # Brick course bands — 3 narrow horizontal stripes (darker brick)
    for i, bz in enumerate([3.5, 6.5, 9.5]):
        ht._make_box_local(
            f"Magician_Cath_Band_{i}",
            (cx, cy, gz + bz),
            (W + 0.05, D + 0.05, 0.20), COL_BRICK_DARK)
    # Buttresses — 5 on each long side, project 0.6m
    for side_sgn in (-1, +1):
        for b in range(5):
            t = -1 + 2 * b / 4
            bx = cx + t * (W / 2 - 1.8)
            by_ = cy + side_sgn * (D / 2 + 0.35)
            # Tapered buttress (two stacked boxes — wider base)
            ht._make_box_local(
                f"Magician_Cath_Buttress_Lo_{side_sgn:+d}_{b}",
                (bx, by_, gz + 4.5),
                (1.6, 1.0, 9.0), COL_BRICK_DARK)
            ht._make_box_local(
                f"Magician_Cath_Buttress_Hi_{side_sgn:+d}_{b}",
                (bx, by_ - side_sgn * 0.25, gz + 10.0),
                (1.2, 0.6, 2.5), COL_BRICK_DARK)
    # Pitched roof — flat ridge box + sloped overhanging eaves
    ridge_z = gz + H + 2.5
    ht._make_box_local("Magician_Cath_Roof_Ridge",
                       (cx, cy, ridge_z),
                       (W * 0.30, D * 0.96, 0.40), COL_TIN_RUSTED)
    ht._make_box_local("Magician_Cath_Roof_Plate",
                       (cx, cy, gz + H + 0.6),
                       (W + 1.2, D + 0.4, 1.2), COL_TIN_RUSTED)
    # Arched windows boarded with sheet metal — 6 on each long side,
    # offset between buttresses
    for side_sgn in (-1, +1):
        side_y = cy + side_sgn * (D / 2 + 0.05)
        for w in range(6):
            # Slot between buttresses
            t = -1 + (2 * w + 1) / 12
            wx = cx + t * (W * 0.80)
            ht._make_box_local(
                f"Magician_Cath_Window_{side_sgn:+d}_{w}",
                (wx, side_y, gz + 5.5),
                (2.4, 0.10, 5.0), COL_SHEET_METAL)
            # Window frame (lighter brick around it)
            ht._make_box_local(
                f"Magician_Cath_WinFrame_{side_sgn:+d}_{w}",
                (wx, side_y, gz + 5.5),
                (2.8, 0.12, 5.4), (0.62, 0.42, 0.34, 1.0))
            ht._make_box_local(
                f"Magician_Cath_Window_{side_sgn:+d}_{w}_inner",
                (wx, side_y + side_sgn * 0.02, gz + 5.5),
                (2.4, 0.10, 5.0), COL_SHEET_METAL)
    # Tall arched window front + back (gable end)
    for end_sgn in (-1, +1):
        ht._make_box_local(
            f"Magician_Cath_GableWindow_{end_sgn:+d}",
            (cx + end_sgn * (W / 2 + 0.05), cy, gz + 7.0),
            (0.10, 5.0, 7.0), COL_SHEET_METAL)
    # Office addition on the front (W gable)
    off_W, off_D, off_H = 8.0, 6.0, 3.5
    off_cx = cx - W / 2 - off_W / 2
    off_cy = cy + 6.0
    ht._make_box_local("Magician_Cath_Office",
                       (off_cx, off_cy, gz + off_H / 2),
                       (off_W, off_D, off_H), COL_BRICK_DARK)
    ht._make_box_local("Magician_Cath_Office_Roof",
                       (off_cx, off_cy, gz + off_H + 0.10),
                       (off_W + 0.3, off_D + 0.3, 0.20),
                       COL_TIN_RUSTED)
    # Office door
    ht._make_box_local("Magician_Cath_Office_Door",
                       (off_cx, off_cy - off_D / 2 - 0.05, gz + 1.0),
                       (1.0, 0.10, 2.0), COL_DOOR_DARK)
    # Antenna farm on the main roof — 4 tall poles
    for i in range(4):
        ax = cx + (-1.5 + i) * 3.5
        ay = cy + (D / 2 - 4.0)
        ht._make_cyl_local(
            f"Magician_Cath_Antenna_{i}",
            (ax, ay, ridge_z + 4.0), 0.06, 8.0,
            COL_BLACK_IRON, segments=4)
    # Cross-bracing struts between antennas (just suggestion of structure)
    for i in range(3):
        ax0 = cx + (-1.5 + i) * 3.5
        ax1 = cx + (-1.5 + i + 1) * 3.5
        ht._make_box_local(
            f"Magician_Cath_AntStrut_{i}",
            ((ax0 + ax1) / 2, cy + (D / 2 - 4.0), ridge_z + 6.0),
            (3.5, 0.06, 0.06), COL_BLACK_IRON)
    # Satellite dish — large disc tilted skyward
    ht._make_sphere_low_local(
        "Magician_Cath_SatDish_Bowl",
        (cx + 5.0, cy - D / 2 + 4.0, ridge_z + 1.8),
        1.6, COL_SHEET_METAL, rings=2, segments=8)
    ht._make_cyl_local(
        "Magician_Cath_SatDish_Mast",
        (cx + 5.0, cy - D / 2 + 4.0, ridge_z + 0.9),
        0.08, 1.8, COL_BLACK_IRON, segments=4)
    # Three small dish receivers for the antenna farm
    for i, (ox, oy) in enumerate([(-4.0, -3.0), (-2.0, +2.0), (+3.0, +1.0)]):
        ht._make_sphere_low_local(
            f"Magician_Cath_SmallDish_{i}",
            (cx + ox, cy + oy, ridge_z + 1.6),
            0.6, COL_SHEET_METAL, rings=2, segments=6)
    # Chimney — masonry stack
    ht._make_box_local("Magician_Cath_Chimney",
                       (cx - W / 2 + 2.0, cy + D / 2 - 3.0,
                        ridge_z + 1.5),
                       (1.2, 1.2, 5.0), COL_BRICK_DARK)
    # Chimney cap
    ht._make_box_local("Magician_Cath_ChimneyCap",
                       (cx - W / 2 + 2.0, cy + D / 2 - 3.0,
                        ridge_z + 4.1),
                       (1.5, 1.5, 0.25), (0.30, 0.28, 0.24, 1.0))
    # Two roof vent stacks
    for i, ox in enumerate([-5.0, +5.0]):
        ht._make_cyl_local(
            f"Magician_Cath_Vent_{i}",
            (cx + ox, cy, ridge_z + 1.2),
            0.30, 2.4, COL_BLACK_IRON, segments=6)


def _build_hierophant_church():
    """St Jude's Catholic Church — Lafayette parish church, stucco
    + single steeple + hipped tin roof + rectory beside. Centerpiece
    of the Sunday-circuit narrative."""
    print("[graustark]   Hierophant — St Jude's")
    cx, cy = ARCANA_LOCALES['Hierophant_Church'][0]
    gz = graustark_elevation(cx, cy)
    # Stepped base
    ht._make_box_local("Hier_Church_Base",
                       (cx, cy, gz + 0.25),
                       (17.0, 29.0, 0.50), COL_LIMESTONE)
    # Nave
    W, D, H = 16.0, 28.0, 8.5
    ht._make_box_local("Hier_Church_Nave",
                       (cx, cy, gz + H / 2 + 0.50),
                       (W, D, H), COL_STUCCO_WHITE)
    # Hipped roof — flat plate + small ridge
    ht._make_box_local("Hier_Church_Roof",
                       (cx, cy, gz + H + 0.30),
                       (W + 0.6, D + 0.6, 0.60), COL_TIN_FRESH)
    ht._make_box_local("Hier_Church_Ridge",
                       (cx, cy, gz + H + 0.90),
                       (W * 0.20, D - 1.5, 0.40), COL_TIN_FRESH)
    # Front gable + steeple on the south end (facing the riverfront)
    steeple_cy = cy - D / 2 - 2.0
    # Steeple base
    ht._make_box_local("Hier_Church_SteepleBase",
                       (cx, steeple_cy, gz + 6.0 / 2),
                       (5.0, 5.0, 6.0), COL_STUCCO_WHITE)
    # Steeple tower (3 stacked tapering boxes)
    ht._make_box_local("Hier_Church_Steeple_Mid",
                       (cx, steeple_cy, gz + 9.0),
                       (4.0, 4.0, 6.0), COL_STUCCO_WHITE)
    ht._make_box_local("Hier_Church_Steeple_Belfry",
                       (cx, steeple_cy, gz + 13.0),
                       (3.4, 3.4, 2.0), COL_STUCCO_CREAM)
    # Pointed spire (small pyramid box stack)
    for i, h in enumerate([1.5, 1.2, 0.8]):
        ht._make_box_local(
            f"Hier_Church_Spire_{i}",
            (cx, steeple_cy, gz + 14.5 + sum([1.5,1.2,0.8][:i]) + h/2),
            (2.4 - i*0.6, 2.4 - i*0.6, h), COL_TIN_FRESH)
    # Cross on top
    ht._make_box_local("Hier_Church_Cross_V",
                       (cx, steeple_cy, gz + 19.0),
                       (0.12, 0.12, 1.4), COL_BLACK_IRON)
    ht._make_box_local("Hier_Church_Cross_H",
                       (cx, steeple_cy, gz + 18.6),
                       (0.80, 0.12, 0.12), COL_BLACK_IRON)
    # Stained-glass arched window panels — 4 each long side
    for side_sgn in (-1, +1):
        side_x = cx + side_sgn * (W / 2 + 0.05)
        for w in range(4):
            t = -1 + 2 * w / 3
            wy = cy + t * (D / 2 - 2.5)
            ht._make_box_local(
                f"Hier_Church_Window_{side_sgn:+d}_{w}",
                (side_x, wy, gz + 5.5),
                (0.10, 1.4, 3.6),
                (0.20, 0.34, 0.52, 1.0))   # blue stained glass
    # Front door
    ht._make_box_local("Hier_Church_Door",
                       (cx, cy - D / 2 - 0.05, gz + 1.5),
                       (1.6, 0.10, 3.0), COL_DOOR_DARK)
    # Front portico — small overhang above the door supported by
    # two limestone columns
    pcy = cy - D / 2 - 1.4
    ht._make_box_local("Hier_Church_Portico_Roof",
                       (cx, pcy, gz + 4.6),
                       (5.0, 2.8, 0.40), COL_LIMESTONE)
    for s in (-1, +1):
        ht._make_cyl_local(
            f"Hier_Church_Portico_Col_{s:+d}",
            (cx + s * 2.0, pcy, gz + 4.6 / 2),
            0.30, 4.4, COL_LIMESTONE, segments=8)
    # Front steps
    for s in range(3):
        ht._make_box_local(
            f"Hier_Church_Step_{s}",
            (cx, pcy - 1.4 - s * 0.4, gz + 0.18 + s * 0.18),
            (5.6 + s * 0.8, 0.4, 0.18), COL_LIMESTONE)
    # Buttresses along the nave — 4 per side
    for side_sgn in (-1, +1):
        for b in range(4):
            t = -1 + 2 * b / 3
            bx = cx + side_sgn * (W / 2 + 0.30)
            by_ = cy + t * (D / 2 - 3.0)
            ht._make_box_local(
                f"Hier_Church_Buttress_{side_sgn:+d}_{b}",
                (bx, by_, gz + 4.5),
                (0.80, 1.4, 8.0), COL_STUCCO_CREAM)
    # Rectory — small adjacent residence
    rcx, rcy = cx + W / 2 + 5.0, cy - 4.0
    ht._make_box_local("Hier_Rectory_Body",
                       (rcx, rcy, gz + 3.5 / 2),
                       (8.0, 8.0, 3.5), COL_STUCCO_CREAM)
    ht._make_box_local("Hier_Rectory_Roof",
                       (rcx, rcy, gz + 3.5 + 0.30),
                       (8.6, 8.6, 0.60), COL_TIN_FRESH)
    # Rectory door + window
    ht._make_box_local("Hier_Rectory_Door",
                       (rcx, rcy - 8.0 / 2 - 0.05, gz + 1.05),
                       (0.95, 0.10, 2.10), COL_DOOR_DARK)
    ht._make_box_local("Hier_Rectory_Window",
                       (rcx - 2.5, rcy - 8.0 / 2 - 0.05, gz + 1.7),
                       (1.2, 0.05, 1.0), COL_GLASS_DARK)


def _build_hierophant_bandstand():
    """Park bandstand — octagonal gazebo, cypress posts, hexagonal
    copper-green roof."""
    print("[graustark]   Hierophant — park bandstand")
    cx, cy = ARCANA_LOCALES['Hierophant_Bandstand'][0]
    gz = graustark_elevation(cx, cy)
    R = 4.5     # gazebo radius
    deck_z = gz + 0.4
    # Deck (octagonal — approximate with a square + 4 corner clips
    # would be 8 polys; cheaper to ship as a box ±sin/cos verts.)
    ht._make_box_local("Hier_Bandstand_Deck",
                       (cx, cy, deck_z),
                       (R * 2 + 0.4, R * 2 + 0.4, 0.20),
                       (0.55, 0.42, 0.30, 1.0))
    # 8 cypress posts at octagonal corners
    POST_H = 3.6
    for i in range(8):
        ang = 2 * 3.14159 * i / 8
        px = cx + R * math.cos(ang)
        py = cy + R * math.sin(ang)
        ht._make_box_local(
            f"Hier_Bandstand_Post_{i}",
            (px, py, deck_z + POST_H / 2),
            (0.18, 0.18, POST_H), COL_PILING)
    # Roof — large flat octagonal cap + a small finial spike
    ht._make_box_local("Hier_Bandstand_Roof",
                       (cx, cy, deck_z + POST_H + 0.30),
                       (R * 2 + 0.8, R * 2 + 0.8, 0.55),
                       (0.30, 0.46, 0.36, 1.0))   # copper-green
    ht._make_box_local("Hier_Bandstand_Roof_Cap",
                       (cx, cy, deck_z + POST_H + 0.95),
                       (R * 1.4, R * 1.4, 0.40),
                       (0.30, 0.46, 0.36, 1.0))
    ht._make_box_local("Hier_Bandstand_Finial",
                       (cx, cy, deck_z + POST_H + 1.7),
                       (0.15, 0.15, 0.9), COL_BLACK_IRON)


def _build_hierophant_armory():
    """The Old Armory — brick + arched windows + crenellated tin
    roof, southern Lafayette National Guard style."""
    print("[graustark]   Hierophant — Old Armory")
    cx, cy = ARCANA_LOCALES['Hierophant_Armory'][0]
    gz = graustark_elevation(cx, cy)
    W, D, H = 24.0, 32.0, 9.5
    ht._make_box_local("Hier_Armory_Body",
                       (cx, cy, gz + H / 2),
                       (W, D, H), COL_BRICK_RED)
    # Crenellated parapet — 8 small notches per long side
    PARAPET_H = 0.9
    par_z = gz + H + PARAPET_H / 2
    ht._make_box_local("Hier_Armory_Parapet_Front",
                       (cx, cy - D / 2 + 0.3, par_z),
                       (W + 0.6, 0.4, PARAPET_H), COL_BRICK_DARK)
    ht._make_box_local("Hier_Armory_Parapet_Back",
                       (cx, cy + D / 2 - 0.3, par_z),
                       (W + 0.6, 0.4, PARAPET_H), COL_BRICK_DARK)
    # Crenellation teeth on the long sides
    for side_sgn in (-1, +1):
        for c in range(7):
            t = -1 + 2 * c / 6
            tx = cx + t * (W / 2 - 1.0)
            ht._make_box_local(
                f"Hier_Armory_Crenel_{side_sgn:+d}_{c}",
                (tx, cy + side_sgn * D / 2,
                 par_z + PARAPET_H * 0.4),
                (1.4, 0.5, 0.6), COL_BRICK_DARK)
    # Tall arched windows — 5 each long side
    for side_sgn in (-1, +1):
        sx_ = cx + side_sgn * (W / 2 + 0.05)
        for w in range(5):
            t = -1 + 2 * w / 4
            wy = cy + t * (D / 2 - 2.5)
            ht._make_box_local(
                f"Hier_Armory_Win_{side_sgn:+d}_{w}",
                (sx_, wy, gz + 5.0),
                (0.10, 1.6, 5.0), COL_GLASS_DARK)
    # Massive double-door entrance on the front
    ht._make_box_local("Hier_Armory_Door",
                       (cx, cy - D / 2 - 0.05, gz + 2.5),
                       (3.5, 0.10, 5.0), COL_DOOR_DARK)


def _build_devil_roadhouse():
    """Daigle's Roadhouse — Gumbo Limbo cycle gravitas. Cinderblock
    one-storey bar with peeling sign, broken neon, dumpster, two
    ratty pickups out front, beer cans scattered in the dirt."""
    print("[graustark]   Devil — Daigle's Roadhouse")
    cx, cy = ARCANA_LOCALES['Devil_Roadhouse'][0]
    gz = graustark_elevation(cx, cy)
    W, D, H = 14.0, 9.0, 3.6
    ht._make_box_local("Devil_Daigle_Body",
                       (cx, cy, gz + H / 2),
                       (W, D, H), (0.62, 0.58, 0.52, 1.0))
    # Weathering streaks on the wall (3 darker vertical stripes)
    for i in range(3):
        t = -1 + 2 * (i + 1) / 4
        ht._make_box_local(
            f"Devil_Daigle_Streak_{i}",
            (cx + t * (W / 2 - 1.0), cy - D / 2 - 0.04, gz + H / 2),
            (0.40, 0.05, H * 0.9), (0.42, 0.40, 0.36, 1.0))
    # Flat tar roof
    ht._make_box_local("Devil_Daigle_Roof",
                       (cx, cy, gz + H + 0.15),
                       (W + 0.4, D + 0.4, 0.30),
                       (0.14, 0.12, 0.12, 1.0))
    # AC unit on the roof (rusted box)
    ht._make_box_local("Devil_Daigle_AC",
                       (cx + W / 4, cy, gz + H + 0.80),
                       (1.4, 1.2, 1.0),
                       (0.46, 0.40, 0.32, 1.0))
    # Faded peeling "DAIGLE'S" sign over the door (with darker
    # patches showing the peeling)
    ht._make_box_local("Devil_Daigle_Sign",
                       (cx, cy - D / 2 - 0.05, gz + 3.0),
                       (5.0, 0.15, 0.9), (0.78, 0.20, 0.18, 1.0))
    # Peeling chunks (3 darker patches on the sign)
    for i, t in enumerate([-0.5, +0.1, +0.7]):
        ht._make_box_local(
            f"Devil_Daigle_SignPeel_{i}",
            (cx + t * 2.0, cy - D / 2 - 0.08,
             gz + 3.0 + (i % 2) * 0.2),
            (0.6, 0.05, 0.30), (0.32, 0.16, 0.12, 1.0))
    # Schlitz neon — small horizontal box hanging off the side
    ht._make_box_local("Devil_Daigle_Neon",
                       (cx + W / 2 + 0.1, cy, gz + 2.6),
                       (0.10, 1.6, 0.45), (0.85, 0.35, 0.20, 1.0))
    # Half-broken neon "OPEN" (one half lit, one dark)
    ht._make_box_local("Devil_Daigle_NeonOpen_Lit",
                       (cx - W / 2 - 0.1, cy + 1.0, gz + 2.6),
                       (0.10, 0.7, 0.35), COL_NEON_PINK)
    ht._make_box_local("Devil_Daigle_NeonOpen_Dead",
                       (cx - W / 2 - 0.1, cy + 0.1, gz + 2.6),
                       (0.10, 0.7, 0.35),
                       (0.36, 0.18, 0.18, 1.0))
    # Single front door
    ht._make_box_local("Devil_Daigle_Door",
                       (cx, cy - D / 2 - 0.05, gz + 1.0),
                       (1.0, 0.10, 2.0), COL_DOOR_DARK)
    # Two front windows (one with a board over half — broken)
    ht._make_box_local("Devil_Daigle_Window_Left",
                       (cx - 3.5, cy - D / 2 - 0.05, gz + 1.8),
                       (1.4, 0.05, 1.0), COL_GLASS_DARK)
    # Right window has a board across the bottom half
    ht._make_box_local("Devil_Daigle_Window_Right",
                       (cx + 3.5, cy - D / 2 - 0.05, gz + 2.1),
                       (1.4, 0.05, 0.50), COL_GLASS_DARK)
    ht._make_box_local("Devil_Daigle_Window_RightBoard",
                       (cx + 3.5, cy - D / 2 - 0.08, gz + 1.6),
                       (1.4, 0.05, 0.55),
                       (0.46, 0.30, 0.20, 1.0))
    # Two ratty pickups parked out front
    for i, ox in enumerate([-4.5, +4.5]):
        tx = cx + ox
        ty = cy - D / 2 - 3.5
        col = (0.42, 0.30, 0.22, 1.0) if i == 0 else (0.36, 0.32, 0.26, 1.0)
        ht._make_box_local(f"Devil_Daigle_Truck_{i}_Body",
                           (tx, ty, gz + 0.85), (2.0, 5.0, 1.2), col)
        ht._make_box_local(f"Devil_Daigle_Truck_{i}_Cab",
                           (tx, ty - 0.8, gz + 1.9),
                           (1.9, 2.2, 0.7), col)
        for wx, wy_ in [(-0.8, -1.6), (+0.8, -1.6),
                        (-0.8, +1.6), (+0.8, +1.6)]:
            ht._make_box_local(
                f"Devil_Daigle_Truck_{i}_Wheel_{wx:+.1f}_{wy_:+.1f}",
                (tx + wx, ty + wy_, gz + 0.30),
                (0.32, 0.64, 0.64), COL_BLACK_IRON)
    # Dumpster around the back (NW corner)
    dxd = cx - W / 2 - 2.0
    dyd = cy + D / 2 + 1.5
    ht._make_box_local("Devil_Daigle_Dumpster",
                       (dxd, dyd, gz + 0.8),
                       (2.2, 1.6, 1.6),
                       (0.16, 0.32, 0.20, 1.0))
    ht._make_box_local("Devil_Daigle_DumpsterLid",
                       (dxd, dyd, gz + 1.65),
                       (2.3, 1.7, 0.10),
                       (0.10, 0.20, 0.14, 1.0))
    # Scattered beer cans / debris (small low boxes) around the lot
    for i, (ox, oy) in enumerate([(-2.0, -8.0), (+1.5, -9.0),
                                    (-6.0, -7.0), (+5.0, -8.5),
                                    (+3.0, -10.0), (-4.5, -9.5)]):
        ht._make_box_local(
            f"Devil_Daigle_Can_{i}",
            (cx + ox, cy + oy, gz + 0.08),
            (0.10, 0.10, 0.18), (0.52, 0.42, 0.32, 1.0))
    # Gravel parking lot
    ht._make_box_local("Devil_Daigle_Lot",
                       (cx, cy - D - 2.0, gz + 0.03),
                       (W + 8.0, 8.0, 0.05),
                       (0.50, 0.46, 0.40, 1.0))
    # Two ratty pickups parked out front
    for i, ox in enumerate([-4.5, +4.5]):
        tx = cx + ox
        ty = cy - D / 2 - 3.5
        col = (0.42, 0.30, 0.22, 1.0) if i == 0 else (0.36, 0.32, 0.26, 1.0)
        # Truck body
        ht._make_box_local(f"Devil_Daigle_Truck_{i}_Body",
                           (tx, ty, gz + 0.85), (2.0, 5.0, 1.2), col)
        # Cab roof
        ht._make_box_local(f"Devil_Daigle_Truck_{i}_Cab",
                           (tx, ty - 0.8, gz + 1.9),
                           (1.9, 2.2, 0.7), col)
        # Wheels (4)
        for wx, wy_ in [(-0.8, -1.6), (+0.8, -1.6),
                        (-0.8, +1.6), (+0.8, +1.6)]:
            ht._make_box_local(
                f"Devil_Daigle_Truck_{i}_Wheel_{wx:+.1f}_{wy_:+.1f}",
                (tx + wx, ty + wy_, gz + 0.30),
                (0.32, 0.64, 0.64), COL_BLACK_IRON)


def _build_justice_courthouse():
    """Graustark Parish Courthouse — Italianate brick block + clock
    tower + four-column portico facing the town square. The town's
    visual anchor; everything else organises around it."""
    print("[graustark]   Justice — Parish Courthouse")
    cx, cy = ARCANA_LOCALES['Justice_Courthouse'][0]
    gz = graustark_elevation(cx, cy)
    W, D, H = 18.0, 22.0, 10.5
    # Rusticated stone base (darker, slightly wider, 2m tall)
    ht._make_box_local("Justice_Court_Base",
                       (cx, cy, gz + 1.0),
                       (W + 0.4, D + 0.4, 2.0), COL_LIMESTONE)
    # Main brick body
    ht._make_box_local("Justice_Court_Body",
                       (cx, cy, gz + H / 2 + 0.5),
                       (W, D, H - 1.0), COL_BRICK_RED)
    # Belt course between floors
    for i, bz in enumerate([4.2, 7.2]):
        ht._make_box_local(
            f"Justice_Court_Belt_{i}",
            (cx, cy, gz + bz),
            (W + 0.20, D + 0.20, 0.20), COL_LIMESTONE)
    # Window pattern — 2 rows × 5 cols on each long side, arched
    # limestone frames around dark glass
    for side_sgn in (-1, +1):
        side_y = cy + side_sgn * (D / 2 + 0.05)
        for r in range(2):
            for c in range(5):
                t = -1 + 2 * c / 4
                wx = cx + t * (W / 2 - 1.5)
                wz = gz + 3.0 + r * 3.0
                # Limestone frame
                ht._make_box_local(
                    f"Justice_Court_WinFrame_{side_sgn:+d}_R{r}C{c}",
                    (wx, side_y, wz),
                    (1.4, 0.04, 2.0), COL_LIMESTONE)
                # Dark glass inset
                ht._make_box_local(
                    f"Justice_Court_Win_{side_sgn:+d}_R{r}C{c}",
                    (wx, side_y + side_sgn * 0.03, wz),
                    (1.0, 0.05, 1.6), COL_GLASS_DARK)
    # Cornice plate (multi-layer for Italianate read)
    for i, h in enumerate([0.20, 0.30, 0.20]):
        ht._make_box_local(
            f"Justice_Court_Cornice_{i}",
            (cx, cy, gz + H + sum([0.20,0.30,0.20][:i]) + h/2),
            (W + 0.6 - i * 0.1, D + 0.6 - i * 0.1, h),
            COL_LIMESTONE)
    # Hipped roof
    ht._make_box_local("Justice_Court_Roof",
                       (cx, cy, gz + H + 0.95),
                       (W, D, 0.6), (0.28, 0.24, 0.24, 1.0))
    # Clock tower at the NE corner — 18m tall, with stone trim
    tcx = cx + W / 2 - 3.0
    tcy = cy + D / 2 - 3.0
    TOW_H = 18.0
    ht._make_box_local("Justice_Court_Tower",
                       (tcx, tcy, gz + TOW_H / 2),
                       (4.5, 4.5, TOW_H), COL_BRICK_RED)
    # Stone quoins on tower corners (vertical strips)
    for sx_sgn in (-1, +1):
        for sy_sgn in (-1, +1):
            ht._make_box_local(
                f"Justice_Court_TowerQuoin_{sx_sgn:+d}_{sy_sgn:+d}",
                (tcx + sx_sgn * 2.0, tcy + sy_sgn * 2.0,
                 gz + TOW_H / 2),
                (0.6, 0.6, TOW_H), COL_LIMESTONE)
    # Tower belt course right at the clock-face level
    ht._make_box_local("Justice_Court_TowerBelt",
                       (tcx, tcy, gz + 13.0),
                       (4.7, 4.7, 0.30), COL_LIMESTONE)
    # Clock faces (4 sides)
    for ang_i, (dx, dy) in enumerate(
            [(+1, 0), (-1, 0), (0, +1), (0, -1)]):
        # Cream backing
        ht._make_box_local(
            f"Justice_Court_Clock_{ang_i}",
            (tcx + dx * 2.3, tcy + dy * 2.3, gz + 14.0),
            (0.10 if abs(dx) > 0 else 1.4,
             1.4 if abs(dx) > 0 else 0.10, 1.4),
            COL_STUCCO_CREAM)
        # Dark hands suggestion (single short hour mark)
        ht._make_box_local(
            f"Justice_Court_ClockHand_{ang_i}",
            (tcx + dx * 2.35, tcy + dy * 2.35, gz + 14.0),
            (0.06 if abs(dx) > 0 else 0.6,
             0.6 if abs(dx) > 0 else 0.06, 0.10),
            COL_BLACK_IRON)
    # Tower cornice
    ht._make_box_local("Justice_Court_TowerCornice",
                       (tcx, tcy, gz + TOW_H + 0.20),
                       (5.2, 5.2, 0.40), COL_LIMESTONE)
    # Tower roof — pyramid stack with stone trim per step
    for i, h in enumerate([1.4, 1.0, 0.6]):
        ht._make_box_local(
            f"Justice_Court_TowerRoof_{i}",
            (tcx, tcy, gz + TOW_H + 0.40 +
             sum([1.4,1.0,0.6][:i]) + h/2),
            (3.6 - i * 0.8, 3.6 - i * 0.8, h),
            (0.28, 0.24, 0.24, 1.0))
    # Flag finial on top
    ht._make_box_local("Justice_Court_Finial",
                       (tcx, tcy, gz + TOW_H + 4.0),
                       (0.12, 0.12, 2.0), COL_BLACK_IRON)
    # Four-column portico on the front (S facing)
    pcy = cy - D / 2 - 1.5
    # Portico pediment (triangle approximated as 2 stacked boxes)
    ht._make_box_local("Justice_Court_Pediment_Lo",
                       (cx, pcy, gz + 6.0),
                       (10.4, 0.6, 1.0), COL_LIMESTONE)
    ht._make_box_local("Justice_Court_Pediment_Hi",
                       (cx, pcy, gz + 7.0),
                       (7.5, 0.6, 0.8), COL_LIMESTONE)
    # Portico roof / entablature
    ht._make_box_local("Justice_Court_Portico_Roof",
                       (cx, pcy, gz + 5.6),
                       (10.0, 3.0, 0.6), COL_LIMESTONE)
    # 4 columns with bases + capitals
    for i, t in enumerate([-1, -0.33, 0.33, 1]):
        col_cx = cx + t * 4.0
        # Base
        ht._make_box_local(
            f"Justice_Court_ColBase_{i}",
            (col_cx, pcy, gz + 0.25),
            (1.0, 1.0, 0.5), COL_LIMESTONE)
        # Column shaft
        ht._make_cyl_local(
            f"Justice_Court_Column_{i}",
            (col_cx, pcy, gz + 5.0 / 2 + 0.5),
            0.42, 5.0, COL_LIMESTONE, segments=8)
        # Capital
        ht._make_box_local(
            f"Justice_Court_ColCap_{i}",
            (col_cx, pcy, gz + 5.5),
            (1.0, 1.0, 0.30), COL_LIMESTONE)
    # Front steps — wider, more layered
    for s in range(5):
        ht._make_box_local(
            f"Justice_Court_Step_{s}",
            (cx, pcy - 1.5 - s * 0.4, gz + 0.18 + s * 0.18),
            (9.0 + s * 1.0, 0.4, 0.18), COL_LIMESTONE)
    # Front double doors at the back of the portico
    ht._make_box_local("Justice_Court_Doors",
                       (cx, cy - D / 2 - 0.05, gz + 2.6),
                       (3.0, 0.10, 5.0), COL_DOOR_DARK)
    # Lampposts flanking the front steps
    for s in (-1, +1):
        lx = cx + s * 7.0
        ly = pcy - 2.4
        ht._make_box_local(
            f"Justice_Court_Lamp_Post_{s:+d}",
            (lx, ly, gz + 2.0),
            (0.18, 0.18, 4.0), COL_BLACK_IRON)
        ht._make_sphere_low_local(
            f"Justice_Court_Lamp_Globe_{s:+d}",
            (lx, ly, gz + 4.2), 0.32,
            (0.96, 0.92, 0.76, 1.0), rings=2, segments=6)


def _build_death_hospital():
    """Graustark Parish Hospital + Asylum (Ward C wing) —
    institutional brick block with the older Ward C in faded
    green tile + broken-paned cupola."""
    print("[graustark]   Death — Parish Hospital + Ward C")
    cx, cy = ARCANA_LOCALES['Death_Hospital'][0]
    gz = graustark_elevation(cx, cy)
    # Main hospital block
    W, D, H = 30.0, 14.0, 12.0
    ht._make_box_local("Death_Hosp_Body",
                       (cx, cy, gz + H / 2),
                       (W, D, H), COL_BRICK_RED)
    # Flat roof + parapet
    ht._make_box_local("Death_Hosp_Roof",
                       (cx, cy, gz + H + 0.20),
                       (W + 0.4, D + 0.4, 0.40),
                       (0.36, 0.30, 0.26, 1.0))
    # Window grid — 3 rows × 7 cols per long side. Long axis is X
    # (W=30), so windows sit on the +Y and -Y faces.
    for side_sgn in (-1, +1):
        side_y = cy + side_sgn * (D / 2 + 0.05)
        for r in range(3):
            for c in range(7):
                tt = -1 + 2 * c / 6
                wx_ = cx + tt * (W / 2 - 2.0)
                ht._make_box_local(
                    f"Death_Hosp_Win_{side_sgn:+d}_R{r}C{c}",
                    (wx_, side_y, gz + 2.0 + r * 3.0),
                    (1.0, 0.05, 1.6), COL_GLASS_DARK)
                # Window frame (limestone trim)
                ht._make_box_local(
                    f"Death_Hosp_WinFrame_{side_sgn:+d}_R{r}C{c}",
                    (wx_, side_y, gz + 2.0 + r * 3.0),
                    (1.2, 0.04, 1.8), COL_LIMESTONE)
                ht._make_box_local(
                    f"Death_Hosp_Win_inner_{side_sgn:+d}_R{r}C{c}",
                    (wx_, side_y + side_sgn * 0.02,
                     gz + 2.0 + r * 3.0),
                    (1.0, 0.05, 1.6), COL_GLASS_DARK)
    # Belt course between floors (3 horizontal limestone bands)
    for i, bz in enumerate([3.7, 6.7, 9.7]):
        ht._make_box_local(
            f"Death_Hosp_Belt_{i}",
            (cx, cy, gz + bz),
            (W + 0.05, D + 0.05, 0.16), COL_LIMESTONE)
    # Cornerstones at the four corners (darker brick blocks)
    for sx_sgn in (-1, +1):
        for sy_sgn in (-1, +1):
            ht._make_box_local(
                f"Death_Hosp_Corner_{sx_sgn:+d}_{sy_sgn:+d}",
                (cx + sx_sgn * (W / 2 - 0.4),
                 cy + sy_sgn * (D / 2 - 0.4),
                 gz + 5.0),
                (0.8, 0.8, 9.5), (0.40, 0.30, 0.24, 1.0))
    # Front entrance — recessed portico
    ent_cy = cy - D / 2 - 1.2
    ht._make_box_local("Death_Hosp_Entrance_Awning",
                       (cx, ent_cy, gz + 4.0),
                       (6.0, 2.4, 0.4), COL_CONCRETE)
    ht._make_box_local("Death_Hosp_Doors",
                       (cx, cy - D / 2 - 0.05, gz + 1.5),
                       (3.5, 0.10, 3.0), COL_GLASS_DARK)
    # Ward C — older wing attached to the EAST, faded green tile
    wcx, wcy = cx + W / 2 + 7.0, cy - 2.0
    WC_W, WC_D, WC_H = 12.0, 10.0, 7.5
    ht._make_box_local("Death_WardC_Body",
                       (wcx, wcy, gz + WC_H / 2),
                       (WC_W, WC_D, WC_H), (0.46, 0.58, 0.48, 1.0))
    ht._make_box_local("Death_WardC_Roof",
                       (wcx, wcy, gz + WC_H + 0.15),
                       (WC_W + 0.3, WC_D + 0.3, 0.30),
                       (0.32, 0.28, 0.26, 1.0))
    # Cupola — broken-paned, sits on the Ward C roof
    ht._make_box_local("Death_WardC_Cupola",
                       (wcx, wcy, gz + WC_H + 1.5),
                       (2.8, 2.8, 2.4), (0.46, 0.58, 0.48, 1.0))
    # Pointed cap
    ht._make_box_local("Death_WardC_CupolaCap",
                       (wcx, wcy, gz + WC_H + 3.4),
                       (2.0, 2.0, 0.8), (0.30, 0.26, 0.24, 1.0))
    # Smaller windows on Ward C — sparser, some boarded
    for side_sgn in (-1, +1):
        for w in range(3):
            t = -1 + 2 * w / 2
            wx_ = wcx + t * (WC_W / 2 - 1.5)
            col = COL_GLASS_DARK if (w + abs(side_sgn)) % 2 == 0 \
                  else COL_SHEET_METAL
            ht._make_box_local(
                f"Death_WardC_Win_{side_sgn:+d}_{w}",
                (wx_, wcy + side_sgn * (WC_D / 2 + 0.05),
                 gz + 4.0),
                (1.0, 0.05, 1.4), col)


def _build_judgement_cemetery():
    """Above-ground tomb city — 40-60 raised cement vaults +
    central mausoleum, all bleached white. The signature
    Louisiana delta cemetery."""
    print("[graustark]   Judgement — above-ground cemetery")
    cx, cy = ARCANA_LOCALES['Judgement_Cemetery'][0]
    gz = graustark_elevation(cx, cy)
    # Cemetery footprint: ~40m × 40m grid of tombs
    tomb_count = 0
    grid_x_range = list(range(-18, 19, 4))
    grid_y_range = list(range(-18, 19, 5))
    for gxi, ox in enumerate(grid_x_range):
        for gyi, oy in enumerate(grid_y_range):
            # Skip the central 5×3 area (reserved for mausoleum)
            if abs(ox) < 6 and abs(oy) < 4:
                continue
            tx = cx + ox
            ty = cy + oy
            tz = graustark_elevation(tx, ty)
            # Per-tomb variety: height + width slight jitter
            seed = (abs(gxi * 13 + gyi * 17)) % 100
            t_h = 1.6 + (seed % 7) * 0.10
            t_w = 1.2 + ((seed // 7) % 5) * 0.08
            t_d = 1.6
            ht._make_box_local(
                f"Judgement_Tomb_{gxi}_{gyi}",
                (tx, ty, tz + t_h / 2),
                (t_w, t_d, t_h),
                (0.94, 0.92, 0.86, 1.0))
            # Capstone
            ht._make_box_local(
                f"Judgement_TombCap_{gxi}_{gyi}",
                (tx, ty, tz + t_h + 0.08),
                (t_w + 0.10, t_d + 0.10, 0.15),
                (0.86, 0.84, 0.78, 1.0))
            # Small cross on ~30% of tombs
            if seed % 100 < 30:
                ht._make_box_local(
                    f"Judgement_TombCross_V_{gxi}_{gyi}",
                    (tx, ty, tz + t_h + 0.50),
                    (0.08, 0.08, 0.60), (0.46, 0.42, 0.36, 1.0))
                ht._make_box_local(
                    f"Judgement_TombCross_H_{gxi}_{gyi}",
                    (tx, ty, tz + t_h + 0.65),
                    (0.36, 0.08, 0.08), (0.46, 0.42, 0.36, 1.0))
            tomb_count += 1
    # Central mausoleum — larger boxy structure
    mauz = gz + 3.5 / 2
    ht._make_box_local("Judgement_Mausoleum_Body",
                       (cx, cy, mauz),
                       (8.0, 6.0, 3.5),
                       (0.94, 0.92, 0.86, 1.0))
    ht._make_box_local("Judgement_Mausoleum_Roof",
                       (cx, cy, gz + 3.5 + 0.4),
                       (8.6, 6.6, 0.4),
                       (0.78, 0.76, 0.70, 1.0))
    # Mausoleum door (sealed)
    ht._make_box_local("Judgement_Mausoleum_Door",
                       (cx, cy - 6.0 / 2 - 0.05, gz + 1.5),
                       (1.6, 0.10, 2.6), COL_BLACK_IRON)
    # Iron fence — perimeter posts
    for i in range(11):
        t = -1 + 2 * i / 10
        for side_sgn in (-1, +1):
            # N + S sides
            fx = cx + t * 22.0
            fy = cy + side_sgn * 22.0
            ht._make_box_local(
                f"Judgement_FencePost_NS_{i}_{side_sgn:+d}",
                (fx, fy, gz + 0.8), (0.14, 0.14, 1.6),
                COL_BLACK_IRON)
            # E + W sides
            fx2 = cx + side_sgn * 22.0
            fy2 = cy + t * 22.0
            ht._make_box_local(
                f"Judgement_FencePost_EW_{i}_{side_sgn:+d}",
                (fx2, fy2, gz + 0.8), (0.14, 0.14, 1.6),
                COL_BLACK_IRON)
    print(f"[graustark]     {tomb_count} tombs + 1 mausoleum")


def _build_tower_broadcast():
    """WGUR — 90m guyed red-and-white radio tower on a small
    concrete pad, single-storey transmitter shack alongside."""
    print("[graustark]   Tower — WGUR Broadcast")
    cx, cy = ARCANA_LOCALES['Tower_Broadcast'][0]
    gz = graustark_elevation(cx, cy)
    # Concrete pad
    ht._make_box_local("Tower_Pad",
                       (cx, cy, gz + 0.10),
                       (8.0, 8.0, 0.20), COL_CONCRETE)
    # Tower — 12 stacked alternating red/white boxes
    BAND_H = 7.5
    for i in range(12):
        col = (0.86, 0.30, 0.22, 1.0) if i % 2 == 0 \
              else (0.96, 0.94, 0.92, 1.0)
        ht._make_box_local(
            f"Tower_Band_{i}",
            (cx, cy, gz + 0.30 + BAND_H * i + BAND_H / 2),
            (1.2 - i * 0.05, 1.2 - i * 0.05, BAND_H), col)
    # Antenna spike at top
    ht._make_box_local("Tower_Spike",
                       (cx, cy, gz + 0.30 + 12 * BAND_H + 1.5),
                       (0.10, 0.10, 3.0), COL_BLACK_IRON)
    # Three guy-wire anchor blocks
    for i in range(3):
        ang = 2 * 3.14159 * i / 3
        ax = cx + 18.0 * math.cos(ang)
        ay = cy + 18.0 * math.sin(ang)
        ht._make_box_local(
            f"Tower_GuyAnchor_{i}",
            (ax, ay, gz + 0.5), (0.8, 0.8, 1.0), COL_CONCRETE)
    # Transmitter shack
    sx_ = cx + 12.0
    sy_ = cy
    ht._make_box_local("Tower_Shack",
                       (sx_, sy_, gz + 2.4 / 2),
                       (6.0, 5.0, 2.4), COL_BRICK_RED)
    ht._make_box_local("Tower_Shack_Roof",
                       (sx_, sy_, gz + 2.4 + 0.10),
                       (6.3, 5.3, 0.20),
                       (0.20, 0.18, 0.18, 1.0))


def _build_moon_drivein():
    """The Static Drive-In — single screen + parking lot + neon
    marquee + snack bar."""
    print("[graustark]   Moon — Static Drive-In")
    cx, cy = ARCANA_LOCALES['Moon_DriveIn'][0]
    gz = graustark_elevation(cx, cy)
    # Massive blank white screen facing south (toward parking)
    SCR_W, SCR_H = 24.0, 14.0
    ht._make_box_local("Moon_DriveIn_Screen",
                       (cx, cy + 12.0, gz + SCR_H / 2 + 2.0),
                       (SCR_W, 0.40, SCR_H),
                       (0.94, 0.92, 0.86, 1.0))
    # Screen support structure (two flanking towers)
    for s in (-1, +1):
        ht._make_box_local(
            f"Moon_DriveIn_Tower_{s:+d}",
            (cx + s * (SCR_W / 2 - 0.3), cy + 12.0,
             gz + (SCR_H + 2.0) / 2),
            (0.8, 0.6, SCR_H + 2.0),
            (0.42, 0.40, 0.38, 1.0))
    # Parking lot (dark asphalt, 30m × 24m, south of screen)
    ht._make_box_local("Moon_DriveIn_Lot",
                       (cx, cy - 8.0, gz + 0.03),
                       (32.0, 26.0, 0.06), (0.16, 0.16, 0.16, 1.0))
    # Speaker posts in the lot (2 rows × 6)
    for r in range(2):
        for c in range(6):
            spx = cx + (-1 + 2 * c / 5) * 12.0
            spy = cy - 4.0 - r * 8.0
            ht._make_box_local(
                f"Moon_DriveIn_Speaker_{r}_{c}",
                (spx, spy, gz + 0.8), (0.10, 0.10, 1.6),
                (0.36, 0.32, 0.28, 1.0))
    # Snack bar (small box) at the south edge
    ht._make_box_local("Moon_DriveIn_Snack",
                       (cx, cy - 22.0, gz + 3.0 / 2),
                       (8.0, 5.0, 3.0), (0.72, 0.62, 0.48, 1.0))
    ht._make_box_local("Moon_DriveIn_Snack_Roof",
                       (cx, cy - 22.0, gz + 3.0 + 0.10),
                       (8.4, 5.4, 0.20),
                       (0.34, 0.28, 0.24, 1.0))
    # Neon-red marquee at entrance
    ht._make_box_local("Moon_DriveIn_Marquee",
                       (cx, cy - 27.0, gz + 3.5),
                       (4.0, 0.30, 2.0), COL_NEON_RED)
    ht._make_box_local("Moon_DriveIn_MarqueePost",
                       (cx, cy - 27.0, gz + 1.5),
                       (0.30, 0.30, 3.0), COL_BLACK_IRON)


def _build_star_iceco():
    """Christian Ice Co — 1950s ice plant, concrete brick + ICE
    parapet letters + glass storefront + truck dock."""
    print("[graustark]   Star — Christian Ice Co.")
    cx, cy = ARCANA_LOCALES['Star_IceCo'][0]
    gz = graustark_elevation(cx, cy)
    W, D, H = 18.0, 12.0, 5.5
    ht._make_box_local("Star_IceCo_Body",
                       (cx, cy, gz + H / 2),
                       (W, D, H), COL_CONCRETE)
    # Tall ICE parapet
    ht._make_box_local("Star_IceCo_Parapet",
                       (cx, cy - D / 2 + 0.05, gz + H + 1.4),
                       (W * 0.9, 0.4, 2.8), COL_CONCRETE)
    # Big "ICE" letters — 3 dark blocks on the parapet
    for i, t in enumerate([-1, 0, 1]):
        ht._make_box_local(
            f"Star_IceCo_Letter_{i}",
            (cx + t * 3.5, cy - D / 2 + 0.10, gz + H + 1.4),
            (2.5, 0.20, 2.0), (0.20, 0.40, 0.62, 1.0))
    # Glass retail storefront on the front
    ht._make_box_local("Star_IceCo_Storefront",
                       (cx - W / 4, cy - D / 2 - 0.05, gz + 1.6),
                       (5.0, 0.05, 3.0), COL_GLASS_DARK)
    # Truck dock — raised concrete platform
    ht._make_box_local("Star_IceCo_Dock",
                       (cx + W / 4, cy - D / 2 - 2.0, gz + 0.6),
                       (6.0, 3.0, 1.2), COL_CONCRETE)
    # Two roll-up doors on the dock side
    for s in (-1, +1):
        ht._make_box_local(
            f"Star_IceCo_RollUp_{s:+d}",
            (cx + W / 4 + s * 1.6, cy - D / 2 - 0.05, gz + 2.0),
            (1.8, 0.05, 3.6), (0.32, 0.30, 0.28, 1.0))


def _build_lovers_chapel():
    """Roadside chapel on Cursed Ground — tiny limestone chapel,
    single bell tower, walled garden — out in the cane fields."""
    print("[graustark]   Lovers — roadside chapel")
    cx, cy = ARCANA_LOCALES['Lovers_Chapel'][0]
    gz = graustark_elevation(cx, cy)
    # Small chapel body
    ht._make_box_local("Lovers_Chapel_Body",
                       (cx, cy, gz + 4.0 / 2),
                       (6.0, 8.0, 4.0), COL_LIMESTONE)
    # Pitched roof
    ht._make_box_local("Lovers_Chapel_Roof",
                       (cx, cy, gz + 4.0 + 0.30),
                       (6.4, 8.4, 0.60), (0.32, 0.28, 0.22, 1.0))
    ht._make_box_local("Lovers_Chapel_Ridge",
                       (cx, cy, gz + 4.0 + 0.95),
                       (0.6, 7.0, 0.40), (0.32, 0.28, 0.22, 1.0))
    # Bell tower on the front
    bcy = cy - 8.0 / 2 - 1.2
    ht._make_box_local("Lovers_Bell_Base",
                       (cx, bcy, gz + 5.0 / 2),
                       (2.4, 2.4, 5.0), COL_LIMESTONE)
    ht._make_box_local("Lovers_Bell_Belfry",
                       (cx, bcy, gz + 5.0 + 1.0),
                       (2.0, 2.0, 1.8), COL_LIMESTONE)
    # Bell (sphere)
    ht._make_sphere_low_local("Lovers_Bell",
                              (cx, bcy, gz + 5.0 + 1.4),
                              0.55, COL_BLACK_IRON,
                              rings=2, segments=6)
    # Cap
    ht._make_box_local("Lovers_Bell_Cap",
                       (cx, bcy, gz + 5.0 + 2.4),
                       (1.4, 1.4, 0.6), (0.32, 0.28, 0.22, 1.0))
    # Cross
    ht._make_box_local("Lovers_Cross_V",
                       (cx, bcy, gz + 5.0 + 3.5),
                       (0.10, 0.10, 1.0), COL_BLACK_IRON)
    ht._make_box_local("Lovers_Cross_H",
                       (cx, bcy, gz + 5.0 + 3.4),
                       (0.50, 0.10, 0.10), COL_BLACK_IRON)
    # Front door (sealed)
    ht._make_box_local("Lovers_Chapel_Door",
                       (cx, cy - 8.0 / 2 - 0.05, gz + 1.4),
                       (1.2, 0.10, 2.4), COL_DOOR_DARK)
    # Walled garden — 4 wall segments around a 14×14 square
    wall_h = 1.4
    for s, w_size, ox, oy in [
            (-1, (14.0, 0.40, wall_h),  0.0, -8.0),
            (+1, (14.0, 0.40, wall_h),  0.0, +8.0),
            (-1, (0.40, 14.0, wall_h), -8.0,  0.0),
            (+1, (0.40, 14.0, wall_h), +8.0,  0.0),
    ]:
        ht._make_box_local(
            f"Lovers_Garden_Wall_{ox:+.0f}_{oy:+.0f}",
            (cx + ox, cy + oy + 8.0, gz + wall_h / 2),
            w_size, COL_LIMESTONE)


def _build_hermit_lighthouse():
    """18m whitewashed lighthouse on a cypress-pile platform at
    the south end of the bayou. A keeper's dwelling at the base."""
    print("[graustark]   Hermit — Bayou Lighthouse")
    cx, cy = ARCANA_LOCALES['Hermit_Lighthouse'][0]
    gz = graustark_elevation(cx, cy)
    # Platform (concrete pad on cypress piles)
    base_z = max(gz, 0.0) + 0.5     # at least at sea level
    # 8 cypress piles
    for i in range(8):
        ang = 2 * math.pi * i / 8
        px = cx + 4.0 * math.cos(ang)
        py = cy + 4.0 * math.sin(ang)
        ht._make_box_local(
            f"Hermit_Pile_{i}", (px, py, base_z - 1.5),
            (0.40, 0.40, 3.0), COL_PILING)
    # Platform deck
    ht._make_box_local("Hermit_Deck",
                       (cx, cy, base_z),
                       (9.0, 9.0, 0.40), COL_CONCRETE)
    # Keeper's cottage at base
    kx = cx + 1.5
    ky = cy + 1.5
    ht._make_box_local("Hermit_Cottage",
                       (kx, ky, base_z + 2.6 / 2 + 0.2),
                       (4.0, 4.0, 2.6), COL_STUCCO_WHITE)
    ht._make_box_local("Hermit_Cottage_Roof",
                       (kx, ky, base_z + 2.6 + 0.30),
                       (4.4, 4.4, 0.40), COL_TIN_FRESH)
    # Lighthouse tower — 3 tapering banded boxes
    LH_H = 18.0
    for i in range(6):
        seg_h = LH_H / 6
        seg_z = base_z + 0.4 + i * seg_h + seg_h / 2
        col = COL_STUCCO_WHITE if i % 2 == 0 \
              else (0.86, 0.30, 0.22, 1.0)
        r = 1.8 - i * 0.10
        ht._make_box_local(
            f"Hermit_Lighthouse_{i}",
            (cx - 2.0, cy - 2.0, seg_z),
            (r * 2, r * 2, seg_h), col)
    # Lantern room at top
    ht._make_box_local("Hermit_Lantern",
                       (cx - 2.0, cy - 2.0, base_z + 0.4 + LH_H + 0.8),
                       (2.4, 2.4, 1.6),
                       (0.96, 0.92, 0.78, 1.0))
    # Cap
    ht._make_box_local("Hermit_LanternCap",
                       (cx - 2.0, cy - 2.0, base_z + 0.4 + LH_H + 2.0),
                       (2.6, 2.6, 0.6), (0.20, 0.18, 0.18, 1.0))
    # Lantern light (bright sphere)
    ht._make_sphere_low_local(
        "Hermit_Lantern_Light",
        (cx - 2.0, cy - 2.0, base_z + 0.4 + LH_H + 1.2),
        0.5, (1.0, 0.94, 0.74, 1.0), rings=2, segments=6)


def _build_strength_carnival():
    """Abandoned Carnival Lot — sun-bleached merry-go-round + big
    top tent + striped ticket booth + empty lion-cage wagon."""
    print("[graustark]   Strength — Abandoned Carnival")
    cx, cy = ARCANA_LOCALES['Strength_Carnival'][0]
    gz = graustark_elevation(cx, cy)
    # Big top tent — central pole + flat conical fabric (approximated)
    ht._make_box_local("Strength_BigTop_Body",
                       (cx, cy, gz + 4.0 / 2),
                       (16.0, 16.0, 4.0),
                       (0.86, 0.78, 0.66, 1.0))   # bleached canvas
    ht._make_box_local("Strength_BigTop_Roof",
                       (cx, cy, gz + 4.0 + 2.0),
                       (12.0, 12.0, 4.0),
                       (0.78, 0.42, 0.36, 1.0))   # faded red stripe
    ht._make_box_local("Strength_BigTop_Cap",
                       (cx, cy, gz + 8.0 + 1.0),
                       (4.0, 4.0, 2.0),
                       (0.86, 0.78, 0.66, 1.0))
    ht._make_box_local("Strength_BigTop_Flag",
                       (cx, cy, gz + 11.0),
                       (0.10, 0.10, 2.0), COL_BLACK_IRON)
    # Merry-go-round — circular platform + 8 vertical poles
    mx = cx + 22.0
    my = cy + 4.0
    ht._make_box_local("Strength_Carousel_Deck",
                       (mx, my, gz + 0.40 / 2),
                       (8.0, 8.0, 0.40), (0.62, 0.52, 0.42, 1.0))
    for i in range(8):
        ang = 2 * math.pi * i / 8
        hx = mx + 3.0 * math.cos(ang)
        hy = my + 3.0 * math.sin(ang)
        ht._make_box_local(
            f"Strength_Carousel_Pole_{i}",
            (hx, hy, gz + 2.0), (0.10, 0.10, 3.5),
            (0.86, 0.74, 0.58, 1.0))
    ht._make_box_local("Strength_Carousel_Roof",
                       (mx, my, gz + 4.0),
                       (8.6, 8.6, 0.4),
                       (0.78, 0.42, 0.36, 1.0))
    # Ticket booth — striped vertical box
    bx = cx - 14.0
    by = cy
    ht._make_box_local("Strength_TicketBooth_Body",
                       (bx, by, gz + 2.4 / 2),
                       (1.8, 1.8, 2.4), (0.96, 0.92, 0.86, 1.0))
    # Stripes (4 horizontal red bands)
    for i in range(4):
        ht._make_box_local(
            f"Strength_TicketBooth_Stripe_{i}",
            (bx, by, gz + 0.4 + i * 0.5),
            (1.85, 1.85, 0.20), (0.78, 0.42, 0.36, 1.0))
    ht._make_box_local("Strength_TicketBooth_Roof",
                       (bx, by, gz + 2.4 + 0.3),
                       (2.4, 2.4, 0.4),
                       (0.32, 0.28, 0.24, 1.0))
    # Empty lion cage wagon
    lx = cx + 4.0
    ly = cy - 12.0
    ht._make_box_local("Strength_LionWagon_Bed",
                       (lx, ly, gz + 0.6),
                       (5.0, 2.8, 0.4), (0.62, 0.42, 0.30, 1.0))
    # Cage bars — 8 vertical posts
    for i in range(8):
        t = -1 + 2 * i / 7
        ht._make_box_local(
            f"Strength_LionWagon_Bar_{i}",
            (lx + t * 2.2, ly + 1.2, gz + 1.8),
            (0.08, 0.08, 2.0), COL_BLACK_IRON)
        ht._make_box_local(
            f"Strength_LionWagon_Bar_back_{i}",
            (lx + t * 2.2, ly - 1.2, gz + 1.8),
            (0.08, 0.08, 2.0), COL_BLACK_IRON)
    ht._make_box_local("Strength_LionWagon_Top",
                       (lx, ly, gz + 2.9),
                       (5.0, 2.8, 0.3),
                       (0.32, 0.28, 0.24, 1.0))
    # Wagon wheels (4)
    for ox, oy in [(-2.0, -1.6), (+2.0, -1.6),
                   (-2.0, +1.6), (+2.0, +1.6)]:
        ht._make_box_local(
            f"Strength_LionWagon_Wheel_{ox:+.0f}_{oy:+.0f}",
            (lx + ox, ly + oy, gz + 0.35),
            (0.16, 0.7, 0.7), COL_BLACK_IRON)


def _build_chariot_garage():
    """Old Lacombe Service Garage — 2-bay yellow-brick gas station
    + repair garage + vintage pump island + parked tow truck."""
    print("[graustark]   Chariot — Lacombe Service Garage")
    cx, cy = ARCANA_LOCALES['Chariot_Garage'][0]
    gz = graustark_elevation(cx, cy)
    # Main garage body
    W, D, H = 14.0, 9.0, 4.5
    ht._make_box_local("Chariot_Garage_Body",
                       (cx, cy, gz + H / 2),
                       (W, D, H), (0.94, 0.86, 0.42, 1.0))
    # Flat roof + overhang
    ht._make_box_local("Chariot_Garage_Roof",
                       (cx, cy, gz + H + 0.15),
                       (W + 1.2, D + 0.4, 0.30),
                       (0.32, 0.28, 0.24, 1.0))
    # Two roll-up garage doors on the front
    for s in (-1, +1):
        ht._make_box_local(
            f"Chariot_Garage_Door_{s:+d}",
            (cx + s * 3.5, cy - D / 2 - 0.05, gz + 3.5 / 2 + 0.10),
            (3.0, 0.05, 3.5), (0.32, 0.30, 0.28, 1.0))
    # Pump island canopy out front
    pcy = cy - D / 2 - 6.0
    # Canopy
    ht._make_box_local("Chariot_Pump_Canopy",
                       (cx, pcy, gz + 4.5),
                       (8.0, 4.0, 0.50), (0.94, 0.92, 0.86, 1.0))
    # 4 canopy posts
    for i, (ox, oy) in enumerate(
            [(-3.5, -1.6), (+3.5, -1.6),
             (-3.5, +1.6), (+3.5, +1.6)]):
        ht._make_box_local(
            f"Chariot_Pump_CanopyPost_{i}",
            (cx + ox, pcy + oy, gz + 4.5 / 2),
            (0.30, 0.30, 4.5), (0.42, 0.38, 0.32, 1.0))
    # Two vintage pumps under the canopy
    for s in (-1, +1):
        ht._make_box_local(
            f"Chariot_Pump_{s:+d}",
            (cx + s * 1.6, pcy, gz + 1.0),
            (0.7, 0.5, 2.0), (0.78, 0.20, 0.18, 1.0))
        # Hose
        ht._make_box_local(
            f"Chariot_Pump_{s:+d}_Top",
            (cx + s * 1.6, pcy, gz + 2.3),
            (0.5, 0.4, 0.6), (0.96, 0.94, 0.86, 1.0))
    # Parked tow truck on the east side of the lot
    tx, ty = cx + W / 2 + 5.0, cy - 2.0
    ht._make_box_local("Chariot_TowTruck_Body",
                       (tx, ty, gz + 1.4),
                       (2.4, 6.0, 1.8),
                       (0.20, 0.30, 0.42, 1.0))
    ht._make_box_local("Chariot_TowTruck_Cab",
                       (tx, ty + 1.8, gz + 2.6),
                       (2.3, 2.2, 1.2),
                       (0.20, 0.30, 0.42, 1.0))
    ht._make_box_local("Chariot_TowTruck_Boom",
                       (tx, ty - 2.0, gz + 3.0),
                       (0.20, 4.0, 0.20), COL_BLACK_IRON)
    # Wheels
    for ox, oy in [(-1.0, -2.0), (+1.0, -2.0),
                   (-1.0, +2.0), (+1.0, +2.0)]:
        ht._make_box_local(
            f"Chariot_TowTruck_Wheel_{ox:+.0f}_{oy:+.0f}",
            (tx + ox, ty + oy, gz + 0.45),
            (0.34, 0.80, 0.80), COL_BLACK_IRON)


def _build_wheel_casino():
    """Le Roulant — ex-bank with limestone columns + ornate cornice,
    glassed-in neon wheel on the parapet. The seedy interior is
    behind a still-respectable bank facade."""
    print("[graustark]   Wheel — Le Roulant casino")
    cx, cy = ARCANA_LOCALES['Wheel_Casino'][0]
    gz = graustark_elevation(cx, cy)
    W, D, H = 16.0, 14.0, 9.0
    # Rusticated stone base
    ht._make_box_local("Wheel_Casino_Base",
                       (cx, cy, gz + 1.5 / 2),
                       (W + 0.30, D + 0.30, 1.5),
                       (0.62, 0.58, 0.52, 1.0))
    # Body
    ht._make_box_local("Wheel_Casino_Body",
                       (cx, cy, gz + H / 2 + 0.5),
                       (W, D, H - 1.0), COL_LIMESTONE)
    # Side window pattern — 4 tall narrow windows per long side
    for side_sgn in (-1, +1):
        side_x = cx + side_sgn * (W / 2 + 0.05)
        for w in range(4):
            t = -1 + 2 * w / 3
            wy_ = cy + t * (D / 2 - 1.5)
            ht._make_box_local(
                f"Wheel_Casino_Win_{side_sgn:+d}_{w}",
                (side_x, wy_, gz + 5.5),
                (0.10, 1.2, 4.0), COL_GLASS_DARK)
            # Limestone arched cap
            ht._make_box_local(
                f"Wheel_Casino_WinCap_{side_sgn:+d}_{w}",
                (side_x, wy_, gz + 7.7),
                (0.20, 1.4, 0.40), COL_LIMESTONE)
    # Ornate cornice (multiple stacked plates)
    for i, h in enumerate([0.20, 0.30, 0.18]):
        ht._make_box_local(
            f"Wheel_Casino_Cornice_{i}",
            (cx, cy, gz + H + sum([0.20,0.30,0.18][:i]) + h/2),
            (W + 0.4 - i * 0.1, D + 0.4 - i * 0.1, h),
            (0.86, 0.82, 0.74, 1.0))
    # Parapet sign back-board
    ht._make_box_local("Wheel_Casino_ParapetBack",
                       (cx, cy - D / 2 + 0.10, gz + H + 2.0),
                       (W * 0.85, 0.30, 3.6),
                       (0.32, 0.30, 0.30, 1.0))
    # Neon wheel on the parapet (red disc)
    ht._make_box_local("Wheel_Casino_NeonDisc",
                       (cx, cy - D / 2 - 0.05, gz + H + 2.2),
                       (3.0, 0.20, 3.0), COL_NEON_RED)
    # 8 spokes (small dark slivers)
    for i in range(8):
        ang = 2 * math.pi * i / 8
        sox = math.cos(ang) * 1.3
        soz = math.sin(ang) * 1.3
        ht._make_box_local(
            f"Wheel_Casino_Spoke_{i}",
            (cx + sox, cy - D / 2 - 0.10, gz + H + 2.2 + soz),
            (0.10, 0.05, 0.10), (0.32, 0.30, 0.30, 1.0))
    ht._make_sphere_low_local("Wheel_Casino_NeonHub",
                              (cx, cy - D / 2 - 0.10, gz + H + 2.2),
                              0.40, COL_NEON_PINK, rings=2, segments=6)
    # "LE ROULANT" letters on the parapet (3 dark blocks)
    for i, t in enumerate([-1, 0, 1]):
        ht._make_box_local(
            f"Wheel_Casino_Letter_{i}",
            (cx + t * 4.0, cy - D / 2 - 0.10, gz + H + 0.6),
            (2.6, 0.10, 0.7), (0.18, 0.16, 0.16, 1.0))
    # 4 limestone columns at the front (former bank facade)
    for i in range(4):
        t = -1 + 2 * i / 3
        cx_c = cx + t * (W / 2 - 1.5)
        # Pedestal under each column
        ht._make_box_local(
            f"Wheel_Casino_ColPed_{i}",
            (cx_c, cy - D / 2 - 0.6, gz + 0.40),
            (1.1, 1.1, 0.80), COL_LIMESTONE)
        # Shaft
        ht._make_cyl_local(
            f"Wheel_Casino_Column_{i}",
            (cx_c, cy - D / 2 - 0.6, gz + H / 2 + 0.4),
            0.50, H - 0.8, COL_LIMESTONE, segments=8)
        # Capital
        ht._make_box_local(
            f"Wheel_Casino_ColCap_{i}",
            (cx_c, cy - D / 2 - 0.6, gz + H + 0.0),
            (1.2, 1.2, 0.30), COL_LIMESTONE)
    # Glass entry doors between the middle columns
    ht._make_box_local("Wheel_Casino_Doors",
                       (cx, cy - D / 2 - 0.05, gz + 3.0 / 2 + 0.30),
                       (3.5, 0.05, 3.0), COL_GLASS_DARK)
    # Wide front steps
    for s in range(3):
        ht._make_box_local(
            f"Wheel_Casino_Step_{s}",
            (cx, cy - D / 2 - 1.2 - s * 0.4, gz + 0.15 + s * 0.20),
            (W + 1.0 + s * 0.8, 0.4, 0.20), COL_LIMESTONE)
    # Velvet rope stanchions either side of the door (subtle "casino")
    for s in (-1, +1):
        ht._make_box_local(
            f"Wheel_Casino_Stanchion_{s:+d}",
            (cx + s * 2.5, cy - D / 2 - 1.0, gz + 1.0),
            (0.15, 0.15, 1.2), COL_BLACK_IRON)
        ht._make_sphere_low_local(
            f"Wheel_Casino_StanchionBall_{s:+d}",
            (cx + s * 2.5, cy - D / 2 - 1.0, gz + 1.7),
            0.16, (0.82, 0.72, 0.36, 1.0), rings=2, segments=6)


def _build_temperance_lounge():
    """The Mixing Glass — windowless 2-storey cocktail lounge with
    hidden side-alley entrance + single neon sign."""
    print("[graustark]   Temperance — The Mixing Glass")
    cx, cy = ARCANA_LOCALES['Temperance_Lounge'][0]
    gz = graustark_elevation(cx, cy)
    W, D, H = 7.0, 14.0, 7.0
    # Body: no street-facing windows
    ht._make_box_local("Temperance_Lounge_Body",
                       (cx, cy, gz + H / 2),
                       (W, D, H), (0.34, 0.30, 0.28, 1.0))
    # Flat roof
    ht._make_box_local("Temperance_Lounge_Roof",
                       (cx, cy, gz + H + 0.15),
                       (W + 0.3, D + 0.3, 0.30),
                       (0.16, 0.14, 0.14, 1.0))
    # Single neon "THE MIXING GLASS" sign on the front (vertical)
    ht._make_box_local("Temperance_Lounge_Sign",
                       (cx - W / 2 - 0.05, cy + D / 4, gz + 4.0),
                       (0.20, 0.6, 4.0), COL_NEON_PINK)
    # Hidden side-alley entrance — small door on the S short side
    ht._make_box_local("Temperance_Lounge_Door",
                       (cx, cy - D / 2 - 0.05, gz + 1.1),
                       (1.0, 0.10, 2.2), COL_DOOR_DARK)
    # Single small "look-through" glass slot beside the door
    ht._make_box_local("Temperance_Lounge_Peephole",
                       (cx - 0.8, cy - D / 2 - 0.05, gz + 1.7),
                       (0.30, 0.05, 0.30), (0.96, 0.84, 0.42, 1.0))


def _build_sun_garden():
    """Solenade Memorial Garden — walled, with an oak in the
    center, brick paths, a bronze sundial, a low limestone bench."""
    print("[graustark]   Sun — Solenade Memorial Garden")
    cx, cy = ARCANA_LOCALES['Sun_Garden'][0]
    gz = graustark_elevation(cx, cy)
    # Wall — 4 limestone segments around a 16×16 square
    wall_h = 1.2
    for s, w_size, ox, oy in [
            (1, (16.0, 0.40, wall_h),  0.0, -8.0),
            (2, (16.0, 0.40, wall_h),  0.0, +8.0),
            (3, (0.40, 16.0, wall_h), -8.0,  0.0),
            (4, (0.40, 16.0, wall_h), +8.0,  0.0),
    ]:
        ht._make_box_local(
            f"Sun_Garden_Wall_{s}",
            (cx + ox, cy + oy, gz + wall_h / 2),
            w_size, COL_LIMESTONE)
    # Central oak — chunky trunk + broad canopy
    ht._make_cyl_local("Sun_Garden_OakTrunk",
                       (cx, cy, gz + 3.0),
                       0.50, 6.0, (0.38, 0.28, 0.20, 1.0), segments=6)
    ht._make_sphere_low_local("Sun_Garden_OakCanopy",
                              (cx, cy, gz + 6.5),
                              3.5, (0.40, 0.50, 0.32, 1.0),
                              rings=3, segments=8)
    # Brick path — narrow strip from S entrance to oak
    ht._make_box_local("Sun_Garden_Path_N",
                       (cx, cy - 4.0, gz + 0.04),
                       (1.2, 8.0, 0.08), COL_BRICK_RED)
    # Low bench at N end
    ht._make_box_local("Sun_Garden_Bench",
                       (cx, cy + 5.5, gz + 0.5 / 2 + 0.10),
                       (3.6, 0.6, 0.50), COL_LIMESTONE)
    # Bronze sundial — tilted box on a small column
    ht._make_box_local("Sun_Garden_Sundial_Base",
                       (cx + 4.0, cy, gz + 0.5),
                       (0.6, 0.6, 1.0), COL_LIMESTONE)
    ht._make_box_local("Sun_Garden_Sundial_Disc",
                       (cx + 4.0, cy, gz + 1.06),
                       (0.7, 0.7, 0.04),
                       (0.62, 0.46, 0.20, 1.0))
    ht._make_box_local("Sun_Garden_Sundial_Gnomon",
                       (cx + 4.0, cy, gz + 1.25),
                       (0.05, 0.4, 0.40),
                       (0.62, 0.46, 0.20, 1.0))
    # Iron gate at the S entrance
    ht._make_box_local("Sun_Garden_Gate",
                       (cx, cy - 8.0, gz + 1.0),
                       (1.8, 0.10, 2.0), COL_BLACK_IRON)


def _build_world_frogshop():
    """Frog Knows Best — wooden roadside aquarium / bait shop with
    a painted frog above the door, tin roof, screened porch."""
    print("[graustark]   World — Frog Knows Best")
    cx, cy = ARCANA_LOCALES['World_FrogShop'][0]
    gz = graustark_elevation(cx, cy)
    # Tiny shotgun-style shop on stilts (delta cottage style)
    W, D, H = 5.0, 9.0, 3.6
    crawl = 0.8
    # 4 pilings
    for ox, oy in [(-W/2+0.4, -D/2+0.4), (+W/2-0.4, -D/2+0.4),
                   (-W/2+0.4, +D/2-0.4), (+W/2-0.4, +D/2-0.4)]:
        ht._make_box_local(
            f"World_FrogShop_Pile_{ox:+.1f}_{oy:+.1f}",
            (cx + ox, cy + oy, gz + crawl / 2),
            (0.24, 0.24, crawl), COL_PILING)
    body_z = gz + crawl
    ht._make_box_local("World_FrogShop_Body",
                       (cx, cy, body_z + H / 2),
                       (W, D, H), (0.42, 0.58, 0.36, 1.0))
    # Tin roof — pitched
    ht._make_box_local("World_FrogShop_Roof",
                       (cx, cy, body_z + H + 0.30),
                       (W + 0.4, D + 0.4, 0.60), COL_TIN_RUSTED)
    ht._make_box_local("World_FrogShop_Ridge",
                       (cx, cy, body_z + H + 0.90),
                       (W * 0.20, D * 0.80, 0.40), COL_TIN_RUSTED)
    # Screened porch on the front
    porch_d = 1.6
    pcy = cy - D / 2 - porch_d / 2
    ht._make_box_local("World_FrogShop_Porch_Deck",
                       (cx, pcy, body_z + 0.05),
                       (W, porch_d, 0.10), COL_PORCH_FLOOR)
    # Two porch posts
    for s in (-1, +1):
        ht._make_box_local(
            f"World_FrogShop_PorchPost_{s:+d}",
            (cx + s * (W / 2 - 0.3), pcy, body_z + 1.5),
            (0.14, 0.14, 3.0), (0.42, 0.58, 0.36, 1.0))
    # Painted frog above the door (small green box with eyes)
    ht._make_box_local("World_FrogShop_FrogSign",
                       (cx, cy - D / 2 - 0.05, body_z + 2.8),
                       (1.8, 0.10, 0.9), (0.30, 0.62, 0.30, 1.0))
    # Two frog eyes (small white blocks)
    for s in (-1, +1):
        ht._make_box_local(
            f"World_FrogShop_FrogEye_{s:+d}",
            (cx + s * 0.4, cy - D / 2 - 0.10, body_z + 3.1),
            (0.20, 0.05, 0.20), (0.96, 0.94, 0.86, 1.0))
    # Front door
    ht._make_box_local("World_FrogShop_Door",
                       (cx, cy - D / 2 - 0.05, body_z + 1.1),
                       (1.0, 0.10, 2.2), COL_DOOR_DARK)
    # Side window with aquarium-blue glow
    ht._make_box_local("World_FrogShop_AquariumWin",
                       (cx + W / 2 + 0.05, cy + 1.0, body_z + 1.6),
                       (0.05, 2.4, 1.6), (0.30, 0.68, 0.78, 1.0))


# ── STRIP MALL  (the canonical Lafayette outskirts vernacular) ─

def _build_sr12_strip_mall():
    """Faded strip mall on SR12 — 5 connected storefronts under
    one continuous flat roof, half-empty parking lot in front.
    Drive-thru daiquiri stand at the south end."""
    print("[graustark]   SR12 strip mall")
    block_cx = -140.0
    block_cy = -100.0      # south of Wharf St, north of garage
    # Continuous body — 40m wide × 12m deep × 4m tall
    BLOCK_W, BLOCK_D, BLOCK_H = 40.0, 12.0, 4.0
    gz = graustark_elevation(block_cx, block_cy)
    ht._make_box_local("Graustark_StripMall_Body",
                       (block_cx, block_cy, gz + BLOCK_H / 2),
                       (BLOCK_W, BLOCK_D, BLOCK_H), COL_CONCRETE)
    # Flat roof overhang
    ht._make_box_local("Graustark_StripMall_Roof",
                       (block_cx, block_cy - BLOCK_D / 2 + 1.5,
                        gz + BLOCK_H + 0.10),
                       (BLOCK_W + 1.0, 3.5, 0.20),
                       (0.32, 0.30, 0.28, 1.0))
    # 5 storefronts: faded chain signs in different colors
    sign_colors = [
        (0.78, 0.32, 0.20, 1.0),    # faded red (PIZZA HUT-ish)
        (0.86, 0.66, 0.22, 1.0),    # mustard yellow (POPEYES-ish)
        (0.20, 0.46, 0.62, 1.0),    # blue (laundromat)
        (0.78, 0.22, 0.34, 1.0),    # pink (dollar store)
        (0.38, 0.40, 0.42, 1.0),    # grey (vacant)
    ]
    for i, sign_col in enumerate(sign_colors):
        store_cx = block_cx + (i - 2) * 8.0
        front_cy = block_cy - BLOCK_D / 2 - 0.05
        # Glass storefront window
        ht._make_box_local(
            f"Graustark_StripMall_Window_{i}",
            (store_cx, front_cy, gz + 1.6),
            (6.0, 0.05, 2.4), COL_GLASS_DARK)
        # Door (narrow box in middle of each storefront)
        ht._make_box_local(
            f"Graustark_StripMall_Door_{i}",
            (store_cx + 2.5, front_cy, gz + 1.2),
            (0.90, 0.05, 2.4), COL_DOOR_DARK)
        # Sign band above the storefront
        ht._make_box_local(
            f"Graustark_StripMall_Sign_{i}",
            (store_cx, front_cy - 0.05, gz + 3.4),
            (7.0, 0.20, 0.80), sign_col)
    # Parking lot in front (asphalt strip)
    ht._make_box_local("Graustark_StripMall_Lot",
                       (block_cx, block_cy - BLOCK_D / 2 - 12.0,
                        gz + 0.03),
                       (BLOCK_W + 4.0, 20.0, 0.06),
                       (0.16, 0.16, 0.16, 1.0))
    # White parking-line stripes (8 spots)
    for sp in range(8):
        t = -1 + 2 * sp / 7
        ht._make_box_local(
            f"Graustark_StripMall_LotLine_{sp}",
            (block_cx + t * (BLOCK_W / 2 - 2.0),
             block_cy - BLOCK_D / 2 - 12.0,
             gz + 0.07),
            (0.12, 5.0, 0.02), COL_LANE_WHITE)
    # 2 parked cars in the lot for life
    for c_i, (ox, oy) in enumerate([(-12.0, -10.0), (+8.0, -10.0)]):
        seed = (abs(int(ox * 13) + int(oy * 17))) % len(_CAR_PALETTES)
        _emit_parked_car(
            f"Graustark_StripMall_Car_{c_i}",
            block_cx + ox, block_cy + oy, '-Y',
            _CAR_PALETTES[seed])
    # Drive-thru daiquiri stand at south end — small detached
    # box with a service window + a sign
    dx = block_cx + BLOCK_W / 2 + 8.0
    dy = block_cy + 4.0
    dz = graustark_elevation(dx, dy)
    ht._make_box_local("Graustark_DaiquiriStand_Body",
                       (dx, dy, dz + 1.8),
                       (4.0, 4.0, 3.6), (0.94, 0.86, 0.42, 1.0))
    ht._make_box_local("Graustark_DaiquiriStand_Roof",
                       (dx, dy, dz + 3.7),
                       (4.6, 4.6, 0.30),
                       (0.32, 0.30, 0.28, 1.0))
    ht._make_box_local("Graustark_DaiquiriStand_Window",
                       (dx - 2.05, dy, dz + 1.6),
                       (0.10, 1.6, 1.0), COL_GLASS_DARK)
    # Hot pink "DAIQUIRIS" sign on the roof
    ht._make_box_local("Graustark_DaiquiriStand_Sign",
                       (dx, dy - 2.05, dz + 4.6),
                       (3.0, 0.20, 1.0),
                       (0.95, 0.32, 0.62, 1.0))


# ── SIDEWALKS  (concrete strips along the arterials) ───────────

def _build_sidewalks():
    """Concrete sidewalks alongside HWY 90 + SR12 + River Rd
    (where they exist in the district outside the RF zone)."""
    print("[graustark]   sidewalks")
    # SR12 — both sides
    sr12 = next(r for r in GRAUSTARK_ROADS if r[0] == 'SR12')
    sm = _smooth_polyline([(w[0], w[1]) for w in sr12[1]],
                          samples_per_seg=4)
    for side_sgn in (-1, +1):
        for i in range(len(sm) - 1):
            sx0, sy0 = sm[i]; sx1, sy1 = sm[i + 1]
            mx = (sx0 + sx1) / 2
            my = (sy0 + sy1) / 2
            # Skip in RF zone band
            if -150 <= my <= +150:
                continue
            dx, dy = sx1 - sx0, sy1 - sy0
            seg_len = math.hypot(dx, dy)
            ht._make_box_local(
                f"Graustark_SW_SR12_{side_sgn:+d}_{i}",
                (mx + side_sgn * 8.0, my, 2.7),
                (1.6, seg_len * 0.95, 0.10), COL_CONCRETE)
    print("[graustark]     sidewalks placed (SR12 both sides)")


# ── BUS STOP  (at the church / SR12 corner) ─────────────────────

def _build_bus_stop():
    """Single bus shelter at SR12 + Wharf street corner."""
    print("[graustark]   bus stop")
    cx, cy = -172.0, +50.0
    gz = graustark_elevation(cx, cy)
    # Bench
    ht._make_box_local("Graustark_BusStop_Bench",
                       (cx, cy, gz + 0.55),
                       (2.4, 0.50, 0.40),
                       (0.40, 0.30, 0.22, 1.0))
    # 4 vertical posts holding up the roof
    for ox, oy in [(-1.1, -0.3), (+1.1, -0.3),
                   (-1.1, +0.3), (+1.1, +0.3)]:
        ht._make_box_local(
            f"Graustark_BusStop_Post_{ox:+.1f}_{oy:+.1f}",
            (cx + ox, cy + oy, gz + 1.4),
            (0.10, 0.10, 2.8), COL_BLACK_IRON)
    # Plexiglass back panel
    ht._make_box_local("Graustark_BusStop_Back",
                       (cx, cy + 0.4, gz + 1.6),
                       (2.4, 0.05, 2.0), COL_GLASS_DARK)
    # Roof
    ht._make_box_local("Graustark_BusStop_Roof",
                       (cx, cy, gz + 2.85),
                       (2.8, 1.4, 0.15),
                       (0.32, 0.30, 0.28, 1.0))
    # GRAUSTARK TRANSIT sign on the back panel
    ht._make_box_local("Graustark_BusStop_Sign",
                       (cx, cy + 0.43, gz + 2.3),
                       (1.6, 0.06, 0.40),
                       (0.28, 0.46, 0.42, 1.0))


# ── BOARDWALKS  (raised plank paths over tidal flats) ──────────
COL_PLANK = (0.55, 0.42, 0.30, 1.0)


def _build_boardwalks():
    """Wooden plank paths connecting levee cottages to bayou-edge
    decks. Visible from any street view in town, signature
    delta-cottage detail."""
    print("[graustark]   bayou boardwalks")
    # Pick the same levee road we used for cottage placement
    levee_road = next(r for r in GRAUSTARK_ROADS if r[0] == 'LeveeCrest_W')
    sm = _smooth_polyline([(w[0], w[1]) for w in levee_road[1]],
                          samples_per_seg=8)
    count = 0
    for i in range(0, len(sm), 3):
        sx, sy = sm[i]
        if (RF_ZONE_X[0] - 30 <= sx <= RF_ZONE_X[1] + 30
                and RF_ZONE_Y[0] - 30 <= sy <= RF_ZONE_Y[1] + 30):
            continue
        # Cottage end (start of boardwalk)
        if i + 1 < len(sm):
            x1, y1 = sm[i + 1]
        else:
            x1, y1 = sm[i - 1]
        dx, dy = x1 - sx, y1 - sy
        seg = math.hypot(dx, dy) or 1
        nx, ny = -dy / seg, dx / seg
        cottage_x = sx + nx * 22
        cottage_y = sy + ny * 22
        if graustark_elevation(cottage_x, cottage_y) < 1.0:
            continue
        # Boardwalk goes east toward the bayou (negative levee
        # crest side = east). Boardwalk endpoint ~10m east into
        # the tidal band.
        end_x = cottage_x + nx * 12
        end_y = cottage_y + ny * 12
        seg_len = math.hypot(end_x - cottage_x, end_y - cottage_y)
        seg_dir_x = (end_x - cottage_x) / seg_len
        seg_dir_y = (end_y - cottage_y) / seg_len
        perp_x = -seg_dir_y
        perp_y = seg_dir_x
        # Plank deck (slightly raised at sea level)
        mid_x = (cottage_x + end_x) / 2
        mid_y = (cottage_y + end_y) / 2
        if abs(seg_dir_x) > abs(seg_dir_y):
            plank_size = (seg_len, 1.2, 0.10)
        else:
            plank_size = (1.2, seg_len, 0.10)
        ht._make_box_local(
            f"Graustark_Boardwalk_{count}_Deck",
            (mid_x, mid_y, 0.40),
            plank_size, COL_PLANK)
        # 4 pilings under the deck
        for p in range(4):
            t = -0.4 + 0.8 * p / 3
            px = cottage_x + (end_x - cottage_x) * (0.5 + t)
            py = cottage_y + (end_y - cottage_y) * (0.5 + t)
            ht._make_box_local(
                f"Graustark_Boardwalk_{count}_Pile_{p}",
                (px, py, -0.50),
                (0.20, 0.20, 2.0), COL_PILING)
        # Small floating deck at the bayou end
        ht._make_box_local(
            f"Graustark_Boardwalk_{count}_EndDeck",
            (end_x, end_y, BAYOU_WATER_Z + 0.30),
            (2.4, 2.4, 0.12), COL_PLANK)
        count += 1
    print(f"[graustark]     placed {count} boardwalks")


# ── FQ AWNINGS  (Bourbon Quarter ground-floor shop awnings) ────
COL_AWNING_RED   = (0.66, 0.20, 0.18, 1.0)
COL_AWNING_GREEN = (0.20, 0.36, 0.28, 1.0)
COL_AWNING_BLUE  = (0.20, 0.30, 0.48, 1.0)
COL_AWNING_GOLD  = (0.78, 0.62, 0.22, 1.0)
COL_AWNING_PURP  = (0.42, 0.22, 0.46, 1.0)


def _build_fq_awnings():
    """Awnings extending out over the storefront of each FQ row
    building. Five different colors, period New Orleans look."""
    print("[graustark]   FQ awnings")
    block_cx = -320.0
    block_cy = +90.0
    spacing_y = 8.0
    colors = [COL_AWNING_RED, COL_AWNING_GREEN, COL_AWNING_GOLD,
              COL_AWNING_BLUE, COL_AWNING_PURP]
    for i in range(5):
        by = block_cy + (i - 2) * spacing_y
        # Awning hangs off the front (street side, west = -X)
        # at ground-floor height
        ax = block_cx - 5.5      # 1m forward of building front
        ay = by
        gz = graustark_elevation(ax, ay)
        ht._make_box_local(
            f"Graustark_FQ_Awning_{i}",
            (ax, ay, gz + 3.20),
            (2.0, 6.0, 0.06), colors[i])
        # 2 small support brackets (iron rods to the building)
        for s in (-1, +1):
            ht._make_box_local(
                f"Graustark_FQ_Awning_{i}_Bracket_{s:+d}",
                (block_cx - 4.0, by + s * 2.5, gz + 3.0),
                (3.0, 0.06, 0.06), COL_BLACK_IRON)
    print(f"[graustark]     placed 5 FQ awnings")


# ── LEVEE COTTAGE MAILBOXES ─────────────────────────────────────

def _build_cottage_mailboxes():
    """Mailbox at the curb of each levee-crest cottage."""
    print("[graustark]   levee cottage mailboxes")
    levee_road = next(r for r in GRAUSTARK_ROADS if r[0] == 'LeveeCrest_W')
    sm = _smooth_polyline([(w[0], w[1]) for w in levee_road[1]],
                          samples_per_seg=8)
    count = 0
    for i in range(0, len(sm), 3):
        sx, sy = sm[i]
        if (RF_ZONE_X[0] - 30 <= sx <= RF_ZONE_X[1] + 30
                and RF_ZONE_Y[0] - 30 <= sy <= RF_ZONE_Y[1] + 30):
            continue
        if i + 1 < len(sm):
            x1, y1 = sm[i + 1]
        else:
            x1, y1 = sm[i - 1]
        dx, dy = x1 - sx, y1 - sy
        seg = math.hypot(dx, dy) or 1
        nx, ny = -dy / seg, dx / seg
        # Mailbox at the cottage-WEST side (toward levee road)
        mx = sx + nx * 4 * (-1)
        my = sy + ny * 4 * (-1)
        # Skip if the cottage was skipped earlier
        cottage_x = sx + nx * 22
        cottage_y = sy + ny * 22
        if graustark_elevation(cottage_x, cottage_y) < 1.0:
            continue
        gz = graustark_elevation(mx, my)
        ht._make_box_local(
            f"Graustark_LeveeMailbox_Post_{count}",
            (mx, my, gz + 0.6),
            (0.10, 0.10, 1.2), COL_DOOR_DARK)
        ht._make_box_local(
            f"Graustark_LeveeMailbox_Box_{count}",
            (mx, my, gz + 1.30),
            (0.45, 0.30, 0.25),
            (0.62, 0.36, 0.20, 1.0))
        count += 1
    print(f"[graustark]     placed {count} cottage mailboxes")


# ── LIGHTHOUSE DOCK  (Hermit Bayou Lighthouse pier) ─────────────

def _build_lighthouse_dock():
    """Wooden pier from the lighthouse platform out to deeper
    water + small mooring posts."""
    print("[graustark]   lighthouse dock")
    lx, ly = ARCANA_LOCALES['Hermit_Lighthouse'][0]
    # Pier extends 12m to the north (toward the bayou main channel)
    pier_dir_x, pier_dir_y = 0.0, 1.0
    pier_len = 12.0
    pier_w = 1.6
    for s in range(6):
        seg_y = ly + 5.0 + s * 2.0
        deck_z = 0.50
        ht._make_box_local(
            f"Graustark_LighthousePier_Deck_{s}",
            (lx, seg_y, deck_z),
            (pier_w, 2.0, 0.10), COL_PLANK)
        # Pilings under each segment
        for sx_sgn in (-1, +1):
            ht._make_box_local(
                f"Graustark_LighthousePier_Pile_{s}_{sx_sgn:+d}",
                (lx + sx_sgn * (pier_w / 2 - 0.10), seg_y, -0.60),
                (0.18, 0.18, 2.2), COL_PILING)
    # End mooring posts
    for ang_i in (0, 1):
        mx = lx + (-1 if ang_i == 0 else +1) * 1.0
        my = ly + 5.0 + 12.0 - 0.5
        ht._make_box_local(
            f"Graustark_LighthousePier_Bollard_{ang_i}",
            (mx, my, 0.95),
            (0.18, 0.18, 0.9), COL_BLACK_IRON)


# ── ROAD MARKINGS  (lane stripes + crosswalks) ──────────────────
COL_LANE_YELLOW = (0.92, 0.78, 0.20, 1.0)
COL_LANE_WHITE  = (0.94, 0.94, 0.90, 1.0)


def _build_road_markings():
    """Yellow centerline on HWY 90 + SR12; white edge stripes on
    HWY 90; crosswalks at the bigger intersections."""
    print("[graustark]   road markings")
    count = 0
    # Yellow centerline on HWY 90 (dashed: ~2m stripes every 4m)
    hwy90 = next(r for r in GRAUSTARK_ROADS if r[0] == 'HWY90')
    sm = _smooth_polyline([(w[0], w[1]) for w in hwy90[1]],
                          samples_per_seg=8)
    for i in range(0, len(sm), 2):
        sx, sy = sm[i]
        gz_road = 3.5 if abs(sx) > 80 else 5.0  # bridge crown
        ht._make_box_local(
            f"Graustark_HWY90_Stripe_{i}",
            (sx, sy, gz_road + 0.02),
            (2.5, 0.15, 0.02), COL_LANE_YELLOW)
        count += 1
    # Yellow centerline on SR12 (continuous double-yellow)
    sr12 = next(r for r in GRAUSTARK_ROADS if r[0] == 'SR12')
    sm = _smooth_polyline([(w[0], w[1]) for w in sr12[1]],
                          samples_per_seg=6)
    for i in range(len(sm) - 1):
        sx0, sy0 = sm[i]; sx1, sy1 = sm[i + 1]
        mx, my = (sx0 + sx1) / 2, (sy0 + sy1) / 2
        seg_len = math.hypot(sx1 - sx0, sy1 - sy0)
        gz_road = 2.8     # average SR12 deck
        # Two parallel yellow stripes 0.4m apart
        for s_off in (-0.20, +0.20):
            ht._make_box_local(
                f"Graustark_SR12_Stripe_{i}_{int(s_off*10):+d}",
                (mx + s_off, my, gz_road + 0.02),
                (0.15, seg_len * 0.92, 0.02), COL_LANE_YELLOW)
            count += 1
    # Crosswalks at HWY90 × SR12 intersection + 2 more
    crosswalks = [
        (-180, -360),     # HWY90 × SR12
        ( -55, -200),     # River Rd S × HWY90 approach
        (-180, +200),     # SR12 × church / RF approach
    ]
    for ci, (cx, cy) in enumerate(crosswalks):
        gz_cw = graustark_elevation(cx, cy) + 0.06
        # 6 white stripes forming a crosswalk
        for s in range(6):
            t = -1 + 2 * s / 5
            ht._make_box_local(
                f"Graustark_Crosswalk_{ci}_{s}",
                (cx + t * 3.0, cy, gz_cw),
                (0.6, 4.0, 0.02), COL_LANE_WHITE)
            count += 1
    print(f"[graustark]     placed {count} road-marking pieces")


# ── STOP SIGNS  (at intersections) ──────────────────────────────
COL_SIGN_RED = (0.78, 0.18, 0.16, 1.0)
COL_SIGN_POLE = (0.42, 0.42, 0.44, 1.0)


def _emit_stop_sign(name, cx, cy, facing='-Y'):
    """Octagonal-ish red sign on a steel pole."""
    gz = graustark_elevation(cx, cy)
    POLE_H = 2.6
    ht._make_box_local(f"{name}_Pole",
                       (cx, cy, gz + POLE_H / 2),
                       (0.12, 0.12, POLE_H), COL_SIGN_POLE)
    # Sign face (a box flat against the facing direction)
    fy = -1 if facing == '-Y' else (+1 if facing == '+Y' else 0)
    fx = -1 if facing == '-X' else (+1 if facing == '+X' else 0)
    sign_offset = 0.10
    sx_ = cx + fx * sign_offset
    sy_ = cy + fy * sign_offset
    if abs(fy) > 0.5:
        sign_size = (0.55, 0.05, 0.55)
    else:
        sign_size = (0.05, 0.55, 0.55)
    ht._make_box_local(f"{name}_Face",
                       (sx_, sy_, gz + POLE_H - 0.20),
                       sign_size, COL_SIGN_RED)


def _build_stop_signs():
    """One stop sign per side road approaching the major arterials."""
    print("[graustark]   stop signs")
    spots = [
        # Side streets entering SR12 (4)
        (-178, +260, '+X'), (-178, +50,  '+X'),
        (-178, -260, '+X'), (-178, -350, '+X'),
        # River Rd N + S entering RF zone (2)
        (-58,  +198, '+Y'), (-58,  -198, '-Y'),
        # Wharf St entering SR12 (1)
        (-176, +50,  '+X'),
        # Levee crest lane entering HWY 90 (1)
        (-66,  -340, '-Y'),
        # Approaches to the truss bridge (2)
        (-25,  -360, '+X'), (+85,  -360, '-X'),
    ]
    for i, (cx, cy, facing) in enumerate(spots):
        _emit_stop_sign(f"Graustark_StopSign_{i}", cx, cy, facing)
    print(f"[graustark]     placed {len(spots)} stop signs")


# ── FIRE HYDRANTS  (period small-town detail) ───────────────────
COL_HYDRANT_RED = (0.78, 0.18, 0.16, 1.0)
COL_HYDRANT_YEL = (0.86, 0.72, 0.30, 1.0)


def _emit_hydrant(name, cx, cy):
    """Red fire hydrant: short stout post + yellow cap."""
    gz = graustark_elevation(cx, cy)
    ht._make_box_local(f"{name}_Body",
                       (cx, cy, gz + 0.45),
                       (0.32, 0.32, 0.90), COL_HYDRANT_RED)
    ht._make_box_local(f"{name}_Cap",
                       (cx, cy, gz + 1.00),
                       (0.34, 0.34, 0.12), COL_HYDRANT_YEL)
    # Two horizontal valve nubs
    for s in (-1, +1):
        ht._make_box_local(
            f"{name}_Valve_{s:+d}",
            (cx + s * 0.22, cy, gz + 0.60),
            (0.10, 0.10, 0.20), COL_HYDRANT_YEL)


def _build_fire_hydrants():
    """One hydrant every ~100m along the major arterials + a few
    at downtown corners."""
    print("[graustark]   fire hydrants")
    # Along SR12 — 8 hydrants (skip middle / riverfront band)
    spots = []
    for j in range(-4, 5):
        if abs(j) < 2:
            continue
        spots.append((-188, j * 100.0))
    # Along HWY 90 (3 each end + 1 on each side of bridge)
    for i in (-5, -3, -1, 1, 3, 5):
        spots.append((i * 100.0, -354.0))
    # Downtown corners (4)
    spots += [(-300, +60), (-300, +100),
              (-185, +260), (-130, +220)]
    # Plus 2 near the lighthouse + Daigle's
    spots += [(+44, -370), (+250, -370)]
    for i, (cx, cy) in enumerate(spots):
        _emit_hydrant(f"Graustark_Hydrant_{i}", cx, cy)
    print(f"[graustark]     placed {len(spots)} fire hydrants")


# ── CYPRESS HUMMOCKS  (tidal flat bumps) ────────────────────────
COL_HUMMOCK_DIRT = (0.42, 0.34, 0.22, 1.0)


def _build_cypress_hummocks():
    """Small raised mounds in the bayou tidal band, each with a
    cluster of 2-4 cypress trees. The signature delta wet-zone
    look — cypress knees rising from the water."""
    print("[graustark]   cypress hummocks (bayou tidal flats)")
    # Hummock spots along the bayou: offset from centerline by
    # 15-25m alternating sides, every 60m of bayou polyline
    sm = _smooth_polyline(BAYOU_CENTERLINE, samples_per_seg=4)
    count = 0
    for i in range(0, len(sm), 4):
        sx, sy = sm[i]
        if i + 1 < len(sm):
            x1, y1 = sm[i + 1]
        else:
            x1, y1 = sm[i - 1]
        dx, dy = x1 - sx, y1 - sy
        seg = math.hypot(dx, dy) or 1
        nx, ny = -dy / seg, dx / seg
        side_sgn = +1 if (i // 4) % 2 == 0 else -1
        hx = sx + nx * 22 * side_sgn
        hy = sy + ny * 22 * side_sgn
        # Skip if inside RF zone (riverfront has its own bayou)
        if (RF_ZONE_X[0] <= hx <= RF_ZONE_X[1]
                and RF_ZONE_Y[0] <= hy <= RF_ZONE_Y[1]):
            continue
        # Skip if landed on dry ground (must be in the tidal band)
        hz = graustark_elevation(hx, hy)
        if hz > 0.0 or hz < -1.6:
            continue
        # Mound — flat-topped low cylinder raised 0.4m above local
        ht._make_cyl_local(
            f"Graustark_Hummock_{count}_Mound",
            (hx, hy, hz + 0.20), 2.0, 0.40,
            COL_HUMMOCK_DIRT, segments=6)
        # 2-3 cypress on the hummock
        cypress_n = 2 + (count % 2)
        for c in range(cypress_n):
            ang = 2 * math.pi * c / cypress_n
            cx = hx + math.cos(ang) * 0.8
            cy = hy + math.sin(ang) * 0.8
            cz = hz + 0.40
            _emit_cypress(f"Graustark_Hummock_{count}_Cypress_{c}",
                           cx, cy, cz)
        count += 1
    print(f"[graustark]     placed {count} cypress hummocks")


# ── FISHING BOATS  (ambient bayou population) ──────────────────
COL_BOAT_HULL_WOOD = (0.40, 0.30, 0.20, 1.0)
COL_BOAT_PAINT_RED = (0.62, 0.22, 0.18, 1.0)
COL_BOAT_PAINT_WHITE = (0.92, 0.90, 0.84, 1.0)


def _emit_fishing_boat(name, cx, cy, facing, hull_color):
    """Small flat-bottom fishing skiff — hull + outboard motor."""
    gz = BAYOU_WATER_Z
    fy = -1 if facing == '-Y' else (+1 if facing == '+Y' else 0)
    fx = -1 if facing == '-X' else (+1 if facing == '+X' else 0)
    if abs(fy) > 0.5:
        hull_size = (2.2, 5.0, 0.55)
    else:
        hull_size = (5.0, 2.2, 0.55)
    # Hull (sitting in the water)
    ht._make_box_local(f"{name}_Hull",
                       (cx, cy, gz + 0.30),
                       hull_size, hull_color)
    # Outboard motor at the stern (opposite facing direction)
    motor_x = cx - fx * 2.6
    motor_y = cy - fy * 2.6
    ht._make_box_local(f"{name}_Motor",
                       (motor_x, motor_y, gz + 0.85),
                       (0.4, 0.4, 0.6), COL_BLACK_IRON)
    # Bench seat
    bench_x = cx + fx * 0.3
    bench_y = cy + fy * 0.3
    if abs(fy) > 0.5:
        bench_size = (1.6, 0.30, 0.20)
    else:
        bench_size = (0.30, 1.6, 0.20)
    ht._make_box_local(f"{name}_Bench",
                       (bench_x, bench_y, gz + 0.85),
                       bench_size, COL_BOAT_HULL_WOOD)


def _build_fishing_boats():
    """Scatter 4-5 small skiffs along the bayou away from the RF
    zone (the riverfront has its own boats)."""
    print("[graustark]   fishing boats on bayou")
    sm = _smooth_polyline(BAYOU_CENTERLINE, samples_per_seg=6)
    count = 0
    target_indices = [4, 9, 16, 28, 34]
    for ti in target_indices:
        if ti >= len(sm):
            continue
        sx, sy = sm[ti]
        if (RF_ZONE_X[0] <= sx <= RF_ZONE_X[1]
                and RF_ZONE_Y[0] <= sy <= RF_ZONE_Y[1]):
            continue
        # Offset slightly from centerline so it's in the water
        # but not centered on the navigable channel
        if ti + 1 < len(sm):
            x1, y1 = sm[ti + 1]
        else:
            x1, y1 = sm[ti - 1]
        dx, dy = x1 - sx, y1 - sy
        seg = math.hypot(dx, dy) or 1
        nx, ny = -dy / seg, dx / seg
        side_sgn = +1 if count % 2 == 0 else -1
        bx = sx + nx * 8 * side_sgn
        by = sy + ny * 8 * side_sgn
        # Pick palette + facing
        color = [COL_BOAT_HULL_WOOD, COL_BOAT_PAINT_RED,
                 COL_BOAT_PAINT_WHITE][count % 3]
        facing = '+Y' if dy >= 0 else '-Y'
        _emit_fishing_boat(f"Graustark_FishingBoat_{count}",
                            bx, by, facing, color)
        count += 1
    print(f"[graustark]     placed {count} fishing boats")


# ── SUBURBAN FRONT-YARD PICKET FENCES ───────────────────────────
COL_PICKET = (0.92, 0.90, 0.84, 1.0)


def _build_suburban_picket_fences():
    """Short white picket fence along the street edge of each
    western residential lot — the classic suburban marker."""
    print("[graustark]   suburban picket fences")
    LOT_GRID_X = [-540, -480, -420, -360, -300]
    LOT_GRID_Y = [+360, +290, +220, +150, +80, +10]
    count = 0
    for ri, gy in enumerate(LOT_GRID_Y):
        for ci, gx in enumerate(LOT_GRID_X):
            if (ri == 2 and ci == 2) or (ri == 4 and ci == 4):
                continue
            # Fence along the +Y edge (street side) of the lot,
            # ~16m wide, leaving a 4m gap for the driveway
            fence_y = gy + 22.0
            gz = graustark_elevation(gx, fence_y)
            # Two segments left + right of a centered driveway gap
            for s, side in [(-1, 'L'), (+1, 'R')]:
                fence_cx = gx + s * 6.0
                ht._make_box_local(
                    f"Graustark_Picket_R{ri}C{ci}_{side}",
                    (fence_cx, fence_y, gz + 0.55),
                    (8.0, 0.08, 1.10), COL_PICKET)
                # Picket tooth-line on top (suggests individual
                # stakes via a darker stripe just below the cap)
                ht._make_box_local(
                    f"Graustark_Picket_Cap_R{ri}C{ci}_{side}",
                    (fence_cx, fence_y, gz + 1.16),
                    (8.0, 0.10, 0.06), COL_PICKET)
                count += 1
    print(f"[graustark]     placed {count} picket fence segments")


# ── PARKED CARS  (lot fillers) ──────────────────────────────────
_CAR_PALETTES = [
    (0.46, 0.46, 0.50, 1.0),   # silver-grey
    (0.32, 0.32, 0.36, 1.0),   # dark grey
    (0.18, 0.18, 0.20, 1.0),   # black
    (0.74, 0.20, 0.22, 1.0),   # red
    (0.36, 0.42, 0.56, 1.0),   # navy
    (0.92, 0.88, 0.78, 1.0),   # cream
    (0.34, 0.52, 0.42, 1.0),   # forest green
]


def _emit_parked_car(name, cx, cy, facing, color):
    """A simple parked sedan — body + cab + 4 wheel boxes."""
    gz = graustark_elevation(cx, cy)
    fy = -1 if facing == '-Y' else (+1 if facing == '+Y' else 0)
    fx = -1 if facing == '-X' else (+1 if facing == '+X' else 0)
    # Orient body to facing direction
    if abs(fy) > 0.5:
        body_size = (1.8, 4.6, 1.2)
        cab_size = (1.7, 2.4, 0.7)
    else:
        body_size = (4.6, 1.8, 1.2)
        cab_size = (2.4, 1.7, 0.7)
    ht._make_box_local(f"{name}_Body",
                       (cx, cy, gz + 0.85),
                       body_size, color)
    ht._make_box_local(f"{name}_Cab",
                       (cx, cy + (-fy * 0.30 if abs(fy) > 0.5 else 0),
                        gz + 1.85),
                       cab_size,
                       (color[0] * 0.85, color[1] * 0.85,
                        color[2] * 0.85, 1.0))
    # 4 wheel boxes
    if abs(fy) > 0.5:
        wheel_positions = [
            (-0.9, -1.6), (+0.9, -1.6),
            (-0.9, +1.6), (+0.9, +1.6)]
    else:
        wheel_positions = [
            (-1.6, -0.9), (-1.6, +0.9),
            (+1.6, -0.9), (+1.6, +0.9)]
    for i, (ox, oy) in enumerate(wheel_positions):
        ht._make_box_local(
            f"{name}_Wheel_{i}",
            (cx + ox, cy + oy, gz + 0.34),
            (0.34, 0.68, 0.68) if abs(fy) > 0.5
            else (0.68, 0.34, 0.68),
            COL_BLACK_IRON)


def _build_parked_cars():
    """Scatter parked cars at the high-traffic commercial /
    cemetery / hospital / cathedral parking spots."""
    print("[graustark]   parked cars")
    # (cx, cy, facing) per car
    spots = [
        # Courthouse town square (4)
        (-148, +266, '-Y'), (-142, +266, '-Y'),
        (-118, +266, '-Y'), (-112, +266, '-Y'),
        # Casino front lot (3)
        (-208, +286, '+Y'), (-198, +286, '+Y'), (-188, +286, '+Y'),
        # Hospital lot (4)
        (-484, -328, '-X'), (-484, -334, '-X'),
        (-484, -340, '-X'), (-484, -346, '-X'),
        # Cemetery gate (2)
        (-396, -180, '+Y'), (-390, -180, '+Y'),
        # Cathedral approach (2)
        (+272, +362, '-Y'), (+278, +362, '-Y'),
        # Ice Co dock side (1)
        (+204, -296, '+X'),
        # Drive-in lot (3 already-parked patron cars in the rows)
        (-510, +192, '+Y'), (-496, +192, '+Y'), (-484, +192, '+Y'),
        # Lacombe garage repair bay (1 customer car)
        (-170, -150, '-Y'),
        # Frog shop lot (1)
        (+142, +296, '+Y'),
    ]
    count = 0
    for i, (cx, cy, facing) in enumerate(spots):
        seed = (abs(int(cx * 7) + int(cy * 11))) % len(_CAR_PALETTES)
        _emit_parked_car(f"Graustark_Car_{i}", cx, cy, facing,
                          _CAR_PALETTES[seed])
        count += 1
    print(f"[graustark]     placed {count} parked cars")


# ── POWER POLES + LINES  (period small-town detail) ─────────────
COL_POWER_POLE = (0.38, 0.30, 0.22, 1.0)
COL_POWER_LINE = (0.16, 0.14, 0.12, 1.0)


def _emit_power_pole(name, cx, cy):
    """Wooden power pole + crossbar."""
    gz = graustark_elevation(cx, cy)
    POLE_H = 9.0
    ht._make_box_local(f"{name}_Pole",
                       (cx, cy, gz + POLE_H / 2),
                       (0.30, 0.30, POLE_H), COL_POWER_POLE)
    # Crossbar at the top
    ht._make_box_local(f"{name}_Crossbar",
                       (cx, cy, gz + POLE_H - 0.40),
                       (2.4, 0.20, 0.20), COL_POWER_POLE)
    # 3 insulator caps (tiny dark blocks on the crossbar)
    for t in (-0.9, 0.0, +0.9):
        ht._make_box_local(
            f"{name}_Insulator_{int(t*10):+d}",
            (cx + t, cy, gz + POLE_H - 0.10),
            (0.18, 0.18, 0.30), COL_GLASS_DARK)


def _build_power_poles():
    """Power poles spaced ~40 m along the major arterials."""
    print("[graustark]   power poles")
    count = 0
    # Along HWY 90 (south end), spaced 40 m
    for i in range(-7, 8):
        px = i * 40.0
        py = -362.0          # 2m south of the road centerline
        _emit_power_pole(f"Graustark_PowerPole_HWY90_{i}", px, py)
        count += 1
    # Along SR12 (north-south spine)
    for j in range(-9, 10):
        if abs(j) < 3:
            continue   # skip the middle (riverfront zone)
        px = -178.0          # 2m east of the road centerline
        py = j * 40.0
        _emit_power_pole(f"Graustark_PowerPole_SR12_{j}", px, py)
        count += 1
    # Along the levee crest lane (just a few)
    for j in (-360, -260, +260, +360):
        _emit_power_pole(f"Graustark_PowerPole_Levee_{j}", -78, j)
        count += 1
    print(f"[graustark]     placed {count} power poles")


# ── DRAINAGE CANALS  (delta authenticity) ──────────────────────
COL_DRAINAGE_WATER = (0.16, 0.20, 0.22, 1.0)


def _build_drainage_canals():
    """Two man-made drainage canals branching off the bayou at
    45° angles, terminating before they hit any building zone."""
    print("[graustark]   drainage canals")
    # Each canal: start point on bayou bank, end point inland,
    # canal width 4 m, surface Z = bayou level + 0.2
    canals = [
        # North canal: from bayou near (+25, +200) heading NW
        ((+25, +200), (-100, +320)),
        # South canal: from bayou near (+60, -200) heading SW
        ((+60, -200), (-100, -300)),
    ]
    for ci, ((x0, y0), (x1, y1)) in enumerate(canals):
        dx, dy = x1 - x0, y1 - y0
        seg = math.hypot(dx, dy) or 1
        nx, ny = -dy / seg, dx / seg
        canal_w = 4.0
        # Single quad strip from start to end
        verts = [
            (x0 + nx * canal_w, y0 + ny * canal_w, BAYOU_WATER_Z + 0.2),
            (x0 - nx * canal_w, y0 - ny * canal_w, BAYOU_WATER_Z + 0.2),
            (x1 - nx * canal_w, y1 - ny * canal_w, BAYOU_WATER_Z + 0.2),
            (x1 + nx * canal_w, y1 + ny * canal_w, BAYOU_WATER_Z + 0.2),
        ]
        faces = [[0, 1, 2], [0, 2, 3]]
        mesh = bpy.data.meshes.new(
            f"Graustark_DrainageCanal_{ci}_mesh")
        mesh.from_pydata(verts, [], faces)
        mesh.update()
        if not mesh.vertex_colors:
            mesh.vertex_colors.new(name="Col")
        layer = mesh.vertex_colors["Col"]
        for poly in mesh.polygons:
            for li in poly.loop_indices:
                layer.data[li].color = COL_DRAINAGE_WATER
        obj = bpy.data.objects.new(
            f"Graustark_DrainageCanal_{ci}", mesh)
        bpy.context.collection.objects.link(obj)
    print(f"[graustark]     placed {len(canals)} drainage canals")


# ── CANE FIELDS  (Lafayette horizon feel) ───────────────────────
# Sugarcane plots at the W + E edges of the district. Each plot
# is a low rectangular ground patch with a vegetation block on
# top (tall green-yellow rows reading as cane). Visible from
# anywhere in town as a horizon-line texture.

COL_CANE_FIELD_GROUND = (0.44, 0.36, 0.22, 1.0)   # exposed soil
COL_CANE_GREEN        = (0.46, 0.56, 0.28, 1.0)   # cane stalks
COL_CANE_YELLOW       = (0.66, 0.62, 0.32, 1.0)   # ripening edge
COL_CANE_CANAL        = (0.20, 0.24, 0.20, 1.0)   # drainage ditch


def _build_cane_field(name, cx, cy, plot_w, plot_d):
    """One cane-field plot + drainage perimeter."""
    gz = graustark_elevation(cx, cy)
    # Soil base (slightly recessed for the dug-out look)
    ht._make_box_local(f"{name}_Soil",
                       (cx, cy, gz + 0.02),
                       (plot_w, plot_d, 0.04),
                       COL_CANE_FIELD_GROUND)
    # Cane vegetation — a single tall block per plot reads from
    # distance. Mix green main + yellow ripe edge stripe for
    # variation.
    ht._make_box_local(f"{name}_Cane",
                       (cx, cy, gz + 1.8 / 2 + 0.05),
                       (plot_w * 0.92, plot_d * 0.92, 1.8),
                       COL_CANE_GREEN)
    ht._make_box_local(f"{name}_Cane_Ripe",
                       (cx, cy + plot_d * 0.42, gz + 1.8 / 2 + 0.05),
                       (plot_w * 0.85, plot_d * 0.10, 1.7),
                       COL_CANE_YELLOW)
    # Drainage ditches on the 4 sides
    for side, ox, oy, sw, sd in [
            ('N',   0,  plot_d / 2 + 0.6, plot_w + 1.2, 0.6),
            ('S',   0, -plot_d / 2 - 0.6, plot_w + 1.2, 0.6),
            ('E',  plot_w / 2 + 0.6, 0, 0.6, plot_d + 1.2),
            ('W', -plot_w / 2 - 0.6, 0, 0.6, plot_d + 1.2),
    ]:
        ht._make_box_local(f"{name}_Ditch_{side}",
                           (cx + ox, cy + oy, gz - 0.10),
                           (sw, sd, 0.30), COL_CANE_CANAL)


def _build_cane_fields():
    """Place a few plot squares at the district edges."""
    print("[graustark]   cane fields (W + E edges)")
    PLOT_W, PLOT_D = 50.0, 80.0
    # West side (X ≈ -570)
    west = [(-570, +280), (-570, +120), (-570, -100), (-570, -260)]
    # East side (across HWY 90)
    east = [(+575, +280), (+575, +120), (+575, -120), (+575, -260)]
    count = 0
    for i, (cx, cy) in enumerate(west + east):
        _build_cane_field(f"Graustark_CaneField_{i}", cx, cy,
                           PLOT_W, PLOT_D)
        count += 1
    print(f"[graustark]     placed {count} cane plots")


# ── TRUSS BRIDGE  (HWY 90 over the bayou) ───────────────────────
# Where HWY 90 crosses the bayou at Y=-360, build a steel truss
# structure flanking + spanning the road. The truss is the
# canonical horizon-anchor in the riverfront's "look downriver"
# axis (see build_riverfront BRIDGE_Y constant).

COL_TRUSS_STEEL = (0.42, 0.42, 0.46, 1.0)
COL_BRIDGE_DECK = (0.20, 0.18, 0.18, 1.0)


def _build_truss_bridge():
    """The HWY 90 truss-bridge crown spanning the bayou."""
    print("[graustark]   truss bridge (HWY 90 over bayou)")
    bridge_cy = -360.0
    bridge_cx = +30.0       # bayou centerline at this Y
    span = 80.0             # E-W span
    deck_z = +5.0           # matches HWY 90 declared Z at bridge crown
    # Deck box (the road plate)
    ht._make_box_local("Graustark_TrussBridge_Deck",
                       (bridge_cx, bridge_cy, deck_z),
                       (span, 18.0, 0.40), COL_BRIDGE_DECK)
    # Side rails (low concrete kerbs)
    for side_sgn in (-1, +1):
        ht._make_box_local(
            f"Graustark_TrussBridge_Kerb_{side_sgn:+d}",
            (bridge_cx, bridge_cy + side_sgn * 8.5, deck_z + 0.40),
            (span, 0.40, 0.80), COL_CONCRETE)
    # Two truss frames — one each side of the deck
    TRUSS_H = 6.0
    for side_sgn in (-1, +1):
        truss_y = bridge_cy + side_sgn * 9.0
        # Top chord
        ht._make_box_local(
            f"Graustark_TrussBridge_TopChord_{side_sgn:+d}",
            (bridge_cx, truss_y, deck_z + TRUSS_H),
            (span, 0.40, 0.40), COL_TRUSS_STEEL)
        # Bottom chord
        ht._make_box_local(
            f"Graustark_TrussBridge_BotChord_{side_sgn:+d}",
            (bridge_cx, truss_y, deck_z + 0.20),
            (span, 0.40, 0.40), COL_TRUSS_STEEL)
        # Vertical members — 9 along the span
        for v in range(9):
            t = -1 + 2 * v / 8
            vx = bridge_cx + t * (span / 2 - 0.5)
            ht._make_box_local(
                f"Graustark_TrussBridge_Vert_{side_sgn:+d}_{v}",
                (vx, truss_y, deck_z + TRUSS_H / 2),
                (0.30, 0.30, TRUSS_H), COL_TRUSS_STEEL)
        # Diagonal members — V pattern (8 panels)
        for v in range(8):
            t = -1 + (2 * v + 1) / 8
            vx = bridge_cx + t * (span / 2)
            # Single tilted diagonal per panel (box approximation)
            ht._make_box_local(
                f"Graustark_TrussBridge_Diag_{side_sgn:+d}_{v}",
                (vx, truss_y, deck_z + TRUSS_H / 2),
                (span / 8 * 1.05, 0.20, 0.30), COL_TRUSS_STEEL)
    # Bridge pylons — concrete supports at each end where the
    # road comes off the berm down to the bayou
    for end_sgn in (-1, +1):
        ht._make_box_local(
            f"Graustark_TrussBridge_Pylon_{end_sgn:+d}",
            (bridge_cx + end_sgn * (span / 2 + 1.0),
             bridge_cy, deck_z / 2),
            (2.0, 18.0, deck_z), COL_CONCRETE)


# ── STREET TREES  (oaks in suburbs, palms downtown) ─────────────
COL_OAK_TRUNK   = (0.42, 0.32, 0.22, 1.0)
COL_OAK_CANOPY  = (0.36, 0.46, 0.26, 1.0)
COL_PALM_TRUNK  = (0.62, 0.52, 0.38, 1.0)
COL_PALM_FROND  = (0.42, 0.56, 0.28, 1.0)


def _emit_oak(name, cx, cy, cz):
    """Suburban oak — chunky trunk + wide rounded canopy."""
    trunk_h = 4.5
    ht._make_cyl_local(f"{name}_Trunk",
                       (cx, cy, cz + trunk_h / 2),
                       0.30, trunk_h, COL_OAK_TRUNK, segments=6)
    ht._make_sphere_low_local(
        f"{name}_Canopy",
        (cx, cy, cz + trunk_h + 1.6),
        2.6, COL_OAK_CANOPY, rings=3, segments=8)


def _emit_palm(name, cx, cy, cz):
    """Downtown palm — tall slim trunk + a few wide flat fronds."""
    trunk_h = 6.0
    ht._make_cyl_local(f"{name}_Trunk",
                       (cx, cy, cz + trunk_h / 2),
                       0.18, trunk_h, COL_PALM_TRUNK, segments=6)
    # 4 frond slabs angled out from the crown
    crown_z = cz + trunk_h + 0.20
    for i in range(4):
        ang = i * math.pi / 2 + math.pi / 4
        fx = math.cos(ang) * 0.6
        fy = math.sin(ang) * 0.6
        ht._make_box_local(
            f"{name}_Frond_{i}",
            (cx + fx, cy + fy, crown_z),
            (2.4 if i % 2 == 0 else 0.30,
             0.30 if i % 2 == 0 else 2.4,
             0.10), COL_PALM_FROND)


def _build_street_trees():
    """Trees along the residential + downtown corridors."""
    print("[graustark]   street trees")
    count = 0
    # Suburban oaks — between each lot and the street (one per lot)
    LOT_GRID_X = [-540, -480, -420, -360, -300]
    LOT_GRID_Y = [+360, +290, +220, +150, +80, +10]
    for ri, gy in enumerate(LOT_GRID_Y):
        for ci, gx in enumerate(LOT_GRID_X):
            if (ri == 2 and ci == 2) or (ri == 4 and ci == 4):
                continue
            # Tree at +Y edge of lot (street side)
            tx = gx + 8.0       # offset east
            ty = gy + 28.0      # at the street curb
            tz = graustark_elevation(tx, ty)
            _emit_oak(f"Graustark_OakSuburb_R{ri}C{ci}",
                      tx, ty, tz)
            count += 1
    # Downtown palms along the FQ + Wharf street
    palm_positions = [
        (-330, +60), (-330, +84), (-330, +108), (-330, +132),
        (-180, +20), (-180, +80), (-180, +140),
        (-130, +210), (-130, +240),
    ]
    for i, (px, py) in enumerate(palm_positions):
        pz = graustark_elevation(px, py)
        _emit_palm(f"Graustark_PalmDowntown_{i}", px, py, pz)
        count += 1
    # Oaks ringing the town square (around the courthouse)
    cs_cx, cs_cy = ARCANA_LOCALES['Justice_Courthouse'][0]
    for i in range(8):
        ang = 2 * math.pi * i / 8 + math.pi / 16
        ox = cs_cx + math.cos(ang) * 28
        oy = cs_cy + math.sin(ang) * 28
        oz = graustark_elevation(ox, oy)
        _emit_oak(f"Graustark_OakSquare_{i}", ox, oy, oz)
        count += 1
    print(f"[graustark]     placed {count} street trees")


def build_district_buildings():
    """PHASE 4 — buildings outside the riverfront's SE quadrant."""
    _hook_hce_mesh_z()
    _build_western_residential()
    _build_bayou_cypress_groves()
    _build_levee_cottages()
    _build_french_quarter_block()
    _build_montreal_block()
    _build_magician_cathedral()
    _build_hierophant_church()
    _build_hierophant_bandstand()
    _build_hierophant_armory()
    _build_devil_roadhouse()
    _build_justice_courthouse()
    _build_death_hospital()
    _build_judgement_cemetery()
    _build_tower_broadcast()
    _build_moon_drivein()
    _build_star_iceco()
    _build_lovers_chapel()
    _build_hermit_lighthouse()
    _build_strength_carnival()
    _build_chariot_garage()
    _build_wheel_casino()
    _build_temperance_lounge()
    _build_sun_garden()
    _build_world_frogshop()
    _build_cane_fields()
    _build_truss_bridge()
    _build_street_trees()
    _build_parked_cars()
    _build_power_poles()
    _build_drainage_canals()
    _build_cypress_hummocks()
    _build_fishing_boats()
    _build_suburban_picket_fences()
    _build_road_markings()
    _build_stop_signs()
    _build_fire_hydrants()
    _build_boardwalks()
    _build_fq_awnings()
    _build_cottage_mailboxes()
    _build_lighthouse_dock()
    _build_sr12_strip_mall()
    _build_sidewalks()
    _build_bus_stop()


# ── PHASE 5  CHARACTERS  ────────────────────────────────────────
# Use HCE's parametric human_figure (in human_sculpt.py) for the
# Graustark population pass. The planar-base GLBs are the canonical
# baseline for FUTURE sculpt variants; for in-town population we
# need fast deterministic placement at scale, which is what
# human_figure already does. Each spawn entry below pins:
#   (label, x, y, facing, body_type, palette_idx)
# Palette index drives the costume colours so we don't have to
# author every NPC's outfit individually.

# Clothing palettes — 8 variants. Index modulo 8 per spawn.
_NPC_PALETTES = [
    {'jacket': (0.40, 0.32, 0.28, 1.0), 'pants': (0.20, 0.20, 0.22, 1.0),
     'hair':   (0.32, 0.22, 0.16, 1.0), 'skin': (0.92, 0.78, 0.62, 1.0)},
    {'jacket': (0.66, 0.30, 0.26, 1.0), 'pants': (0.30, 0.28, 0.26, 1.0),
     'hair':   (0.18, 0.12, 0.08, 1.0), 'skin': (0.84, 0.66, 0.50, 1.0)},
    {'jacket': (0.20, 0.36, 0.50, 1.0), 'pants': (0.16, 0.18, 0.22, 1.0),
     'hair':   (0.42, 0.30, 0.20, 1.0), 'skin': (0.94, 0.80, 0.66, 1.0)},
    {'jacket': (0.96, 0.92, 0.86, 1.0), 'pants': (0.42, 0.32, 0.22, 1.0),
     'hair':   (0.86, 0.78, 0.62, 1.0), 'skin': (0.96, 0.84, 0.70, 1.0)},
    {'jacket': (0.42, 0.46, 0.32, 1.0), 'pants': (0.32, 0.30, 0.26, 1.0),
     'hair':   (0.22, 0.16, 0.12, 1.0), 'skin': (0.72, 0.54, 0.40, 1.0)},
    {'jacket': (0.78, 0.42, 0.22, 1.0), 'pants': (0.36, 0.36, 0.40, 1.0),
     'hair':   (0.52, 0.36, 0.24, 1.0), 'skin': (0.90, 0.74, 0.58, 1.0)},
    {'jacket': (0.28, 0.40, 0.30, 1.0), 'pants': (0.42, 0.30, 0.20, 1.0),
     'hair':   (0.16, 0.12, 0.10, 1.0), 'skin': (0.82, 0.62, 0.48, 1.0)},
    {'jacket': (0.62, 0.52, 0.32, 1.0), 'pants': (0.30, 0.30, 0.30, 1.0),
     'hair':   (0.94, 0.92, 0.86, 1.0), 'skin': (0.96, 0.88, 0.76, 1.0)},
]


# Tier-1 NPCs use the planar base mesh (dacancino's reference,
# ~3,600 tris/figure). Tier-2 NPCs use HCE's primitive human_figure
# (~200 tris/figure). The split limits the planar cost to ~43k tris
# for the 12 narrative-anchored characters while keeping the
# 35 background extras cheap.
TIER_1_LABELS = {
    'Cath_Frasier',           # Magician — Frasier Temple
    'Cath_apprentice',        # Maya (Frasier's apprentice)
    'Church_priest',          # Hierophant — Father Amato
    'Hermit_keeper',          # Hermit
    'Cemetery_mourner1',      # Judgement — ensemble anchor
    'Cemetery_mourner2',
    'FQ_restaurant_door',     # Bourbon Quarter restaurant
    'Casino_doorman',         # Wheel — Le Roulant
    'Frog_owner',             # World — Frog Knows Best
    'Sun_Garden_old',         # Sun — Frank Tuesday observation
    'Cane_field_1',           # Strength — cane-field labour
    'Carnival_caretaker',     # Strength — abandoned carnival
}


# Spawn list — every entry is (label, x, y, facing, body_type).
# Palette is picked from position seed so the layout is
# deterministic. Total ~28 humans distributed across town zones.
NPC_SPAWNS = [
    # ── Town square (courthouse + bandstand + sun garden) ──
    ("TS_visitor_1",     -130.0, +230.0, '-Y', 'male_avg'),
    ("TS_visitor_2",     -136.0, +233.0, '-Y', 'female_avg'),
    ("TS_visitor_3",     -120.0, +240.0, '+X', 'male_tall'),
    ("Bandstand_listener", -150.0, +127.0, '+Y', 'female_avg'),
    ("Bandstand_kid",    -145.0, +124.0, '+Y', 'child'),
    ("Sun_Garden_old",   -118.0, +120.0, '-Y', 'elderly'),
    # ── Bourbon Quarter row ──
    ("FQ_cafe_1",        -311.0, +84.0,  '-X', 'female_slim'),
    ("FQ_cafe_2",        -312.0, +86.0,  '-X', 'male_avg'),
    ("FQ_passerby",      -310.0, +98.0,  '+Y', 'teen'),
    ("FQ_restaurant_door", -312.0, +90.0, '-X', 'male_heavy'),
    # ── D'Ambrosio's parking lot (RF zone — visitors) ──
    ("RF_lot_1",         -38.0,  +18.0,  '+X', 'male_avg'),
    ("RF_lot_2",         -42.0,  +14.0,  '+X', 'female_avg'),
    ("RF_lot_3",         -40.0,  +30.0,  '-Y', 'elderly'),
    # ── Levee cottage porches ──
    ("Levee_porch_N",    -38.0,  +418.0, '+X', 'male_heavy'),
    ("Levee_porch_S",    -86.0,  -424.0, '+X', 'female_avg'),
    # ── Cemetery mourners ──
    ("Cemetery_mourner1", -360.0, -184.0, '-Y', 'elderly'),
    ("Cemetery_mourner2", -358.0, -187.0, '-Y', 'female_avg'),
    # ── Lighthouse keeper ──
    ("Hermit_keeper",    +52.0, -378.0,  '-X', 'elderly'),
    # ── Daigle's roadhouse patrons (outside) ──
    ("Daigle_patron1",   +256.0, -384.0, '+Y', 'male_heavy'),
    ("Daigle_patron2",   +264.0, -384.0, '+Y', 'male_tall'),
    # ── Drive-in lot ──
    ("DriveIn_couple_1", -500.0, +192.0, '+Y', 'male_avg'),
    ("DriveIn_couple_2", -498.0, +192.0, '+Y', 'female_avg'),
    # ── Carnival caretaker ──
    ("Carnival_caretaker", -474.0, +400.0, '+X', 'elderly'),
    # ── Magician cathedral approach ──
    ("Cath_visitor",      +290.0, +366.0, '+Y', 'male_avg'),
    # ── Church entrance ──
    ("Church_priest",    -200.0, +185.0, '-Y', 'elderly'),
    ("Church_attendee",  -196.0, +183.0, '-Y', 'female_avg'),
    # ── Frog shop owner ──
    ("Frog_owner",       +152.0, +296.0, '-Y', 'male_heavy'),
    # ── Gas station attendant + customer ──
    ("Garage_attendant", -180.0, -158.0, '+Y', 'male_avg'),
    ("Garage_customer",  -178.0, -166.0, '-Y', 'female_slim'),
    # ── More bandstand musicians (3-piece in front of the bandstand) ──
    ("Band_horn",        -148.0, +118.0, '-Y', 'male_avg'),
    ("Band_bass",        -150.0, +116.0, '-Y', 'male_heavy'),
    ("Band_drums",       -152.0, +118.0, '-Y', 'male_avg'),
    # ── Casino patrons + doorman ──
    ("Casino_doorman",   -200.0, +290.0, '-Y', 'male_heavy'),
    ("Casino_gambler1",  -204.0, +287.0, '-Y', 'male_tall'),
    ("Casino_gambler2",  -196.0, +287.0, '-Y', 'female_avg'),
    # ── Cathedral approach (Frasier territory) ──
    ("Cath_Frasier",     +296.0, +362.0, '+Y', 'male_tall'),
    ("Cath_apprentice",  +302.0, +360.0, '+Y', 'teen'),
    # ── Suburban kids playing on the SW residential road ──
    ("Suburb_kid_1",     -480.0, +220.0, '+X', 'child'),
    ("Suburb_kid_2",     -478.0, +220.0, '-X', 'child'),
    ("Suburb_parent",    -474.0, +218.0, '+Y', 'female_avg'),
    # ── Cane field worker ──
    ("Cane_field_1",     -580.0, -160.0, '-Y', 'male_heavy'),
    # ── Montreal block residents ──
    ("Montreal_walker1", +480.0, +320.0, '-Y', 'female_slim'),
    ("Montreal_walker2", +486.0, +318.0, '-Y', 'elderly'),
    # ── Ice plant worker on the dock ──
    ("Star_IceCo_worker", +186.0, -304.0, '-X', 'male_avg'),
    # ── Old Armory steps ──
    ("Armory_visitor",   +200.0, -322.0, '+Y', 'male_avg'),
    # ── Boat dock / RF parking lot (extras for atmosphere) ──
    ("RF_couple_1",      -36.0,  +60.0,  '+X', 'female_slim'),
    ("RF_couple_2",      -34.0,  +58.0,  '+X', 'male_avg'),
]


def _build_street_furniture():
    """Town-square and Bourbon Quarter props: park benches, iron
    lampposts, mailboxes, a Mardi Gras banner across the FQ
    street, oyster-shell piles by the dock — the small reads that
    suggest a town being lived in."""
    print("[graustark]   street furniture")

    # Town-square park benches around the bandstand
    bs_cx, bs_cy = ARCANA_LOCALES['Hierophant_Bandstand'][0]
    for i, ang_deg in enumerate([0, 90, 180, 270]):
        ang = math.radians(ang_deg)
        bx = bs_cx + math.cos(ang) * 9.0
        by = bs_cy + math.sin(ang) * 9.0
        bz = graustark_elevation(bx, by)
        # Bench seat
        if ang_deg in (0, 180):
            size = (3.0, 0.5, 0.10)
        else:
            size = (0.5, 3.0, 0.10)
        ht._make_box_local(f"Bandstand_Bench_{i}_Seat",
                           (bx, by, bz + 0.45), size,
                           (0.40, 0.30, 0.22, 1.0))
        # Bench back
        if ang_deg in (0, 180):
            back_size = (3.0, 0.10, 0.6)
            back_y_offset = -math.copysign(0.20, math.sin(ang) or 0.5)
            ht._make_box_local(f"Bandstand_Bench_{i}_Back",
                               (bx, by + (0.20 if ang_deg == 0 else -0.20),
                                bz + 0.75), back_size,
                               (0.40, 0.30, 0.22, 1.0))
        else:
            ht._make_box_local(f"Bandstand_Bench_{i}_Back",
                               (bx + (0.20 if ang_deg == 90 else -0.20),
                                by, bz + 0.75), (0.10, 3.0, 0.6),
                               (0.40, 0.30, 0.22, 1.0))
        # Iron legs (just 2 visible boxes per bench)
        for s in (-1, +1):
            if ang_deg in (0, 180):
                ht._make_box_local(
                    f"Bandstand_Bench_{i}_Leg_{s:+d}",
                    (bx + s * 1.2, by, bz + 0.20),
                    (0.10, 0.5, 0.40), COL_BLACK_IRON)
            else:
                ht._make_box_local(
                    f"Bandstand_Bench_{i}_Leg_{s:+d}",
                    (bx, by + s * 1.2, bz + 0.20),
                    (0.5, 0.10, 0.40), COL_BLACK_IRON)

    # Iron lampposts around the town square (8 in a ring)
    cs_cx, cs_cy = ARCANA_LOCALES['Justice_Courthouse'][0]
    for i in range(8):
        ang = 2 * math.pi * i / 8
        lx = cs_cx + math.cos(ang) * 22.0
        ly = cs_cy + math.sin(ang) * 22.0
        lz = graustark_elevation(lx, ly)
        ht._make_box_local(f"TS_Lamp_Post_{i}",
                           (lx, ly, lz + 2.5),
                           (0.18, 0.18, 5.0), COL_BLACK_IRON)
        ht._make_box_local(f"TS_Lamp_Crossbar_{i}",
                           (lx, ly, lz + 4.9),
                           (0.50, 0.10, 0.10), COL_BLACK_IRON)
        ht._make_sphere_low_local(
            f"TS_Lamp_Globe_{i}",
            (lx, ly, lz + 4.7), 0.30,
            (0.96, 0.94, 0.78, 1.0), rings=2, segments=6)

    # Mardi Gras banner across the Bourbon Quarter street
    # (a horizontal strip between two posts at -325 and -315)
    bq_y = +75.0
    ht._make_box_local("FQ_Banner_PostL",
                       (-328.0, bq_y, graustark_elevation(-328, bq_y) + 3.0),
                       (0.20, 0.20, 6.0), COL_BLACK_IRON)
    ht._make_box_local("FQ_Banner_PostR",
                       (-312.0, bq_y, graustark_elevation(-312, bq_y) + 3.0),
                       (0.20, 0.20, 6.0), COL_BLACK_IRON)
    # Banner (cycling colors — 3 segments)
    banner_z = graustark_elevation(-320, bq_y) + 5.5
    for i, col in enumerate([(0.85, 0.78, 0.20, 1.0),   # gold
                              (0.62, 0.20, 0.50, 1.0),   # purple
                              (0.32, 0.62, 0.32, 1.0)]):  # green
        seg_w = 5.0
        seg_cx = -328.0 + (i + 0.5) * seg_w + 0.5
        ht._make_box_local(f"FQ_Banner_{i}",
                           (seg_cx, bq_y, banner_z),
                           (seg_w, 0.05, 0.8), col)

    # Mailbox posts at the western residential — one per lot
    for ri, gy in enumerate([+360, +290, +220, +150, +80, +10]):
        for ci, gx in enumerate([-540, -480, -420, -360, -300]):
            if (ri == 2 and ci == 2) or (ri == 4 and ci == 4):
                continue
            # Mailbox is at the street edge (toward SR12 at X=-180)
            mx = gx + 18.0
            my = gy
            mz = graustark_elevation(mx, my)
            ht._make_box_local(
                f"Suburb_Mailbox_Post_R{ri}C{ci}",
                (mx, my, mz + 0.6),
                (0.10, 0.10, 1.2), COL_DOOR_DARK)
            ht._make_box_local(
                f"Suburb_Mailbox_Box_R{ri}C{ci}",
                (mx, my, mz + 1.30),
                (0.45, 0.30, 0.25),
                (0.62, 0.36, 0.20, 1.0))

    # Oyster shell piles near the riverfront approach
    for i in range(4):
        ang = 2 * math.pi * i / 4
        ox = +180.0 + math.cos(ang) * 8.0
        oy = -310.0 + math.sin(ang) * 8.0
        oz = graustark_elevation(ox, oy)
        ht._make_box_local(
            f"Oyster_Pile_{i}",
            (ox, oy, oz + 0.40),
            (1.6, 1.6, 0.80),
            (0.78, 0.74, 0.66, 1.0))


def _resolve_planar_gender(body_type):
    """Pick male vs female reference mesh for a given body_type."""
    if body_type.startswith('female'):
        return 'female'
    return 'male'


def _facing_to_z_rotation(facing):
    """The planar reference's natural foot direction is -Y after
    glTF Y-up import. Convert our facing string to Z-rotation."""
    table = {
        '-Y': 0.0,
        '+Y': math.pi,
        '+X': -math.pi / 2,
        '-X': +math.pi / 2,
    }
    return table.get(facing, 0.0)


_REF_GLTF_PATH = os.path.normpath(os.path.join(
    _SCRIPT_DIR, "..", "..", "..", "..", "lore", "refs", "humans",
    "planar_human_base_rigs", "scene.gltf"))

# Module-level cache for the source mesh+armature pairs.
_PLANAR_SOURCES = {'male': None, 'female': None}


def _import_planar_sources():
    """Import dacancino's reference once and cache the male/female
    source objects. Returns False (and prints a clear warning) if
    the reference isn't on disk — the build falls back to primitive
    figures for everyone in that case."""
    if not os.path.exists(_REF_GLTF_PATH):
        print(f"[graustark]   ⚠ planar reference missing at "
              f"{_REF_GLTF_PATH} — falling back to primitives for "
              f"tier-1 NPCs")
        return False
    bpy.ops.import_scene.gltf(filepath=_REF_GLTF_PATH)
    # Classify imported meshes by centroid X
    for o in bpy.data.objects:
        if o.type != 'MESH' or len(o.data.vertices) < 100:
            continue
        # Skip already-named project meshes (e.g. anything not
        # from this import)
        if o.name.startswith('Graustark_'):
            continue
        # Skip if it's the unrelated 4-vert "test light" plane
        if len(o.data.vertices) < 1000:
            continue
        verts_world = [o.matrix_world @ v.co for v in o.data.vertices]
        xs = [v.x for v in verts_world]
        cx = sum(xs) / len(xs)
        if cx < 1.5 and _PLANAR_SOURCES['male'] is None:
            _PLANAR_SOURCES['male'] = o
        elif cx >= 1.5 and _PLANAR_SOURCES['female'] is None:
            _PLANAR_SOURCES['female'] = o
    if not _PLANAR_SOURCES['male'] or not _PLANAR_SOURCES['female']:
        print(f"[graustark]   ⚠ couldn't classify both planar "
              f"sources from reference — got "
              f"{list(k for k,v in _PLANAR_SOURCES.items() if v)}")
        return False
    # Hide the sources themselves; we only want their duplicates.
    for src in _PLANAR_SOURCES.values():
        src.hide_set(True)
        if src.parent and src.parent.type == 'ARMATURE':
            src.parent.hide_set(True)
    print(f"[graustark]   planar reference loaded: "
          f"male={_PLANAR_SOURCES['male'].name}, "
          f"female={_PLANAR_SOURCES['female'].name}")
    return True


def _instance_planar_npc(label, x, y, z, facing, body_type):
    """Duplicate the planar source mesh (and its armature parent),
    move/rotate/scale into spawn position. Reference is ~3.6 units
    tall in source coords; scale 0.5 → 1.8 m human."""
    gender = _resolve_planar_gender(body_type)
    src = _PLANAR_SOURCES[gender]
    if src is None:
        return False
    # Duplicate the armature + skinned mesh together
    bpy.ops.object.select_all(action='DESELECT')
    targets = [src]
    if src.parent and src.parent.type == 'ARMATURE':
        targets.append(src.parent)
    for o in targets:
        o.hide_set(False)
        o.select_set(True)
    bpy.context.view_layer.objects.active = targets[-1]
    bpy.ops.object.duplicate()
    # The duplicates are now the active selection
    dups = list(bpy.context.selected_objects)
    # Re-hide originals
    for o in targets:
        o.hide_set(True)
    # Find the top of the duplicated chain (armature, if present)
    root = next((o for o in dups if o.type == 'ARMATURE'), dups[0])
    # Apply transforms
    root.location = (x, y, z)
    root.rotation_euler = (0.0, 0.0, _facing_to_z_rotation(facing))
    root.scale = (0.5, 0.5, 0.5)
    # Rename to label
    root.name = f"Graustark_NPC_{label}"
    for o in dups:
        if o is not root:
            o.name = f"Graustark_NPC_{label}_{o.type.lower()}"
    return True


# ── HERO GLB OVERRIDES  (Mixamo / Ready Player Me imports) ─────
# Spawn labels in NPC_SPAWNS that have a dedicated hero GLB on
# disk get instanced from that GLB instead of the generic planar
# reference. See godot/assets/3d/characters/heroes/README.md for
# the workflow + filename convention. Missing files fall back to
# the planar reference — never breaks the build.
HERO_GLB_PATHS = {
    'Cath_Frasier':       'frasier_temple.glb',
    'Cath_apprentice':    'maya_apprentice.glb',
    'Church_priest':      'father_amato.glb',
    'Hermit_keeper':      'hermit_keeper.glb',
    'Frog_owner':         'frog_shop_owner.glb',
    'Sun_Garden_old':     'frank_sun.glb',
    'Carnival_caretaker': 'carnival_caretaker.glb',
    'Cane_field_1':       'cane_worker.glb',
    'Cemetery_mourner1':  'cemetery_mourner_1.glb',
    'Cemetery_mourner2':  'cemetery_mourner_2.glb',
    'FQ_restaurant_door': 'fq_restaurant_patron.glb',
    'Casino_doorman':     'casino_doorman.glb',
}

_HERO_GLB_DIR = os.path.normpath(os.path.join(
    _SCRIPT_DIR, "..", "..", "..", "assets", "3d", "characters", "heroes"))


def _instance_hero_glb(label, x, y, z, facing):
    """Import a hero-specific GLB and place it at the spawn. Returns
    True if a file was found and instanced, False to signal the
    caller should fall back to the planar reference."""
    fname = HERO_GLB_PATHS.get(label)
    if not fname:
        return False
    path = os.path.join(_HERO_GLB_DIR, fname)
    if not os.path.exists(path):
        return False
    # Track objects that exist before import so we can identify
    # what came in.
    before = set(o.name for o in bpy.data.objects)
    bpy.ops.import_scene.gltf(filepath=path)
    after = set(o.name for o in bpy.data.objects)
    new_objs = [bpy.data.objects[n] for n in (after - before)]
    if not new_objs:
        return False
    # Find the top-level root of the imported hierarchy (the
    # armature or the first mesh-bearing object with no parent
    # that's in our new set).
    root = next((o for o in new_objs
                 if o.parent is None or o.parent.name not in after),
                new_objs[0])
    root.location = (x, y, z)
    rot_z = {
        '-Y': 0.0, '+Y': math.pi,
        '+X': -math.pi / 2, '-X': +math.pi / 2,
    }.get(facing, 0.0)
    root.rotation_euler = (0.0, 0.0, rot_z)
    # Rename so we can find them later
    for o in new_objs:
        o.name = f"Graustark_NPC_{label}_{o.type.lower()}"
    return True


def build_district_characters_and_props():
    """PHASE 5 — drop humans through the town in a tiered mix.

    Priority per spawn:
      1. Hero GLB (if file exists in
         godot/assets/3d/characters/heroes/) — used for the 12
         named tier-1 spawns when their hero file is on disk
      2. Planar reference instance (dacancino, CC-BY-4.0) — used
         for tier-1 spawns whose hero GLB is missing
      3. Primitive human_figure — used for the 35 background extras
    """
    print(f"[graustark] PHASE 5 characters — {len(NPC_SPAWNS)} figures")
    planar_ready = _import_planar_sources()
    from human_sculpt import human_figure
    placed_hero = placed_planar = placed_prim = failed = 0
    for label, x, y, facing, body_type in NPC_SPAWNS:
        z = graustark_elevation(x, y)
        try:
            # 1. Hero GLB
            if label in HERO_GLB_PATHS:
                if _instance_hero_glb(label, x, y, z, facing):
                    placed_hero += 1
                    continue
            # 2. Planar reference for tier-1 spawns missing a hero
            if planar_ready and label in TIER_1_LABELS:
                if _instance_planar_npc(label, x, y, z, facing,
                                         body_type):
                    placed_planar += 1
                    continue
            # 3. Primitive figure for background extras (and any
            # tier-1 fallback)
            seed = (abs(int(x * 7) + int(y * 11))) \
                   % len(_NPC_PALETTES)
            pal = _NPC_PALETTES[seed]
            human_figure(
                f"Graustark_NPC_{label}",
                base_x=x, base_y=y, base_z=z,
                scale=1.0, facing=facing, body_type=body_type,
                skin_color=pal['skin'],
                hair_color=pal['hair'],
                jacket_color=pal['jacket'],
                pants_color=pal['pants'])
            placed_prim += 1
        except Exception as e:
            failed += 1
            print(f"[graustark]   ✗ failed {label}: {e}")
    print(f"[graustark]   placed: {placed_hero} hero GLB "
          f"+ {placed_planar} planar + {placed_prim} primitive  "
          f"(failed {failed})")
    _build_street_furniture()


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
    report_arcana_status()

    export_glb()


if __name__ == "__main__":
    main()
