# HCE · Performance & Asset-Management Plan

Status: **DEFERRED** until we hit the threshold (see bottom).

Captured 2026-06-15 during the long uninterrupted build session
that produced ~30 buildings + the arterial network + civic
landmarks.

## Current state (what we have today)

- **One monolithic GLB per locale.** `harmony_terrain.glb` ships
  everything: terrain, all buildings, all neighborhoods, all
  signage, all NPCs. The Blender build script
  (`godot/tools/blender/locales/build_harmony_terrain.py`,
  ~6500 lines) emits one giant scene; Godot loads the whole
  thing on enter.
- **`LocaleSetup.gd`** walks every `MeshInstance3D` once at
  `_ready()`, applies a single `StandardMaterial3D` material
  override that reads vertex color as albedo, and adds trimesh
  `StaticBody3D` colliders to any mesh whose name matches a
  hint in `COLLIDER_NAME_HINTS`.
- **One material across everything.** Vertex color + plain
  `StandardMaterial3D`. No per-mesh materials, no textures, no
  texture atlases.
- **Colliders are eager and per-mesh.** Every wall / post /
  slab gets its own trimesh collider sibling at load time.

## What to add when we hit the threshold

In rough order of impact-for-effort:

### 1. MultiMeshInstance3D for repeating geometry
Houses, street trees, lamp posts, parked cars, fence segments,
sidewalk panels — currently each emits a fresh
`MeshInstance3D`. Collapse each palette family (e.g. all
beige-walled houses, all street trees in NorthRanch) into one
`MultiMeshInstance3D` with per-instance transforms. Easily ~10×
node-count reduction.

### 2. Per-locale GLB splits
Break the single `harmony_terrain.glb` into ~6 sub-GLBs:
- `hce_north.glb` (CountryClub + NorthRanch + NorthComm +
  NexCorp HQ + Hospital)
- `hce_central.glb` (HarmonyPark + ES + Church + Cemetery +
  Civic landmarks)
- `hce_south_residential.glb` (Phase 2 + WestEstates + Phase 3
  + Drive-in)
- `hce_south_commercial.glb` (Chapter-1 cluster + Truck Stop)
- `hce_east.glb` (EastCDS + HS field + Halsey Studios + Big-box
  + Self-Storage)
- `hce_west.glb` (SCRATCH nightclub + WestComm)

Then a `chunk_manager.gd` on the scene root parents only the
chunks within ~400 m of the player position. The build script
becomes a wrapper that runs N times, each emitting a subset.

### 3. Visibility ranges on small props
Godot 4.2+ exposes `visibility_range_begin/end` on
`MeshInstance3D`. Cars, NPCs, signs, mailboxes, jukeboxes,
ketchup bottles — all hide past ~150 m. Big buildings stay
visible to ~600 m. Trees / streetlamps to ~300 m. A
post-process pass on the build script's output applies sane
defaults per name pattern.

### 4. Box colliders instead of trimesh for buildings
Currently every wall the hint list matches becomes a per-vertex
trimesh collider. For axis-aligned box geometry that's wasteful.
Replace `_ensure_static_collider` with code that builds an
axis-aligned `BoxShape3D` from the mesh AABB. Trimesh is only
needed for terrain (which is the only sloped surface).

### 5. Async background loading
`ResourceLoader.load_threaded_request()` for the sub-GLBs so
chunks load in worker threads instead of blocking the main
thread on enter.

### 6. LOD swaps
For buildings further than ~200 m, swap to a "low-poly" GLB
(single tagged box per house instead of main + garage + roof +
windows). Build script emits both a `_hi.glb` and `_lo.glb`
per chunk; `chunk_manager.gd` swaps based on distance.

## Threshold to start

Begin work on item 1 when ANY of:
- Frame rate drops below 60 fps on the Steam Deck during a
  fly-through of the full district
- Initial scene load exceeds 5-6 seconds
- The GLB exceeds ~100 MB
- Player reports stutter or hitches when crossing the district

Until then the monolithic build keeps iteration fast — a single
`./run_cathedral.sh build_harmony_terrain.py` invocation
rebuilds the whole world and the build-edit-test loop stays
short. Premature splitting would slow that loop down for no
visible benefit during rough-layout.

## Where to look

- Build script: `godot/tools/blender/locales/build_harmony_terrain.py`
- Locale setup: `godot/scenes/locales/LocaleSetup.gd`
- Scene file: `godot/scenes/locales/harmony_terrain.tscn`
- Lessons & rules: `lore/_3D_MODELING_PLAYBOOK.md`
