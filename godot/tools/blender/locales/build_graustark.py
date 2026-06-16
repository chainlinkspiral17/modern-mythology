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


# ── PHASE STUBS ─────────────────────────────────────────────────
# Filled in across subsequent commits as we work through the
# five-phase deep-build. Each stub prints what it WOULD do so
# a build log reads as a checklist of remaining work.

def build_district_elevation_field():
    """PHASE 1 — strata + natural erosion across the whole 1200×840.
    Builds the subdivided ground plane that ENVELOPS the riverfront
    (riverfront keeps its own ground patches at the canonical
    coordinates; this layer fills in everything outside those).

    TODO:
      - Sample HCE-style elevation function with 5 visible strata
      - Carve crevasse splays + cypress hummocks + cordgrass rib lines
      - Subdivision: ~6 m cells over 1200×840 → 200×140 grid
    """
    print("[graustark] PHASE 1 elevation field — STUB (no geometry yet)")


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
