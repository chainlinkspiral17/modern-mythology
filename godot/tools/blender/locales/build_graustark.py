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


def build_district_water_layer():
    """PHASE 2 — bayou main channel beyond the riverfront's local
    river patch + man-made drainage canals + tidal flats.

    TODO:
      - Catmull-Rom-smoothed bayou polyline N→S threading the map
      - Drainage canals at 45° to the bayou meander
      - Tidal mud flats at Z = -1, broken by cypress hummocks
    """
    print("[graustark] PHASE 2 water layer — STUB")


def build_district_roads():
    """PHASE 3 — the road network beyond the riverfront's local
    streets. Raised arterial berms vs bayou-side gravel lanes.

    TODO:
      - HWY 90 berm crossing the bayou via the south-end truss bridge
      - State Route 12 N-S commercial spine through downtown
      - River Road continuation north + south of the riverfront stub
      - Wharf St cross-axis
      - Levee-crown lane on top of the high ridge
    """
    print("[graustark] PHASE 3 roads — STUB")


def build_district_buildings():
    """PHASE 4 — buildings outside the riverfront's SE quadrant.

    TODO:
      - Lafayette-style raised cottages on cypress stilts
      - Levee-crown bungalows on the high ground
      - Compact French Quarter block (4-6 buildings, wrought iron)
      - Cathedral / town square anchor on a horizon ridge
      - Above-ground cemetery as outlying narrative locale
      - Boatyard quonsets at south-end industrial pad
      - Strip-mall arteries with faded chain signs
      - Cane-field edge plots
    """
    print("[graustark] PHASE 4 buildings — STUB")


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
