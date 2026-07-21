# Meshy → Godot hero-asset pipeline

Turn a reference image into a low-poly, **untextured** hero object (a boat, an
altar, a machine — the statement piece a locale can't reach with procedural
cubes) and land it in the game's vertex-color / Light3D / screen-space-shader
pipeline. Two halves, deliberately split:

```
 reference.png ──▶ meshy_render.py ──▶ assets/3d/meshy/<tag>/<slug>.glb (raw)
                    (network, any host)          │
                                                 ▼
                         build_meshy_import.py (Blender, on the Deck)
                                                 │
                                                 ▼
                              assets/3d/locales/<slug>.glb (scene-ready)
```

## 0 · Queue builder — `meshy_studio.html` (optional)

Open it in a browser to assemble jobs visually: set tag/slug, point at a
reference image (a repo-relative path, or pick a file to embed), tune the
params (T2 `ai_model`, `target_polycount`, topology, `should_texture`), reorder
the queue, then **Export queue JSON** → save as `godot/tools/meshy_queue.json`.
Round-trips the same schema the runner reads; queue persists in localStorage.
Self-contained, no build step. (Same role `runway_studio.html` plays for video.)

## 1 · Runner — `meshy_render.py` (no Blender needed)

Calls Meshy's `POST /openapi/v1/image-to-3d`, polls, downloads `model_urls.glb`.
Stdlib only. Every request field passes through the queue's `params`, so the new
**T2 model** id and any future Meshy fields are set from JSON, not code.

```bash
export MESHY_API_KEY=msy_...              # or: echo msy_... > godot/tools/.meshy_key
cp godot/tools/meshy_queue.example.json godot/tools/meshy_queue.json   # edit it
python3 godot/tools/meshy_render.py godot/tools/meshy_queue.json --dry-run
python3 godot/tools/meshy_render.py godot/tools/meshy_queue.json
```

Flags: `--dry-run` (no API calls / no credits), `--only 'hero_*'`, `--limit N`,
`--overwrite`. Progress + a manifest land in `assets/3d/meshy/manifest.json`.

Defaults target the untextured low-poly workflow: `should_texture:false`,
`target_polycount:6000`, `topology:"triangle"`. Set `params.ai_model` to the
T2 model id you're using. The key file and raw `*.glb` under `assets/3d/meshy/`
are gitignored (raw downloads are regenerable; the manifest is tracked).

## 2 · Normalizer — `build_meshy_import.py` (Blender, on the Deck)

Raw Meshy GLBs arrive in Meshy's frame/scale with no game-readable material.
This pass fixes that to the project's conventions:

- join meshes, apply transforms
- recenter (XY centroid → origin, min Z → 0, stands on the ground plane)
- **scale to a real height in metres** (1 unit = 1 m — scale to a sane size,
  never to compensate for a bad number; see the coordinate-frame rule)
- optional decimate for extra low-poly
- **bake a flat vertex-color layer + a minimal material** — the pipeline's
  flat-identifier convention, applied to the otherwise-untextured T2 output so
  Light3D + the screen-space stack render it like every other locale mesh
- re-export GLB (Blender Z-up → Godot Y-up handled by the exporter)

```bash
cp godot/tools/blender/meshy_import.example.json godot/tools/blender/meshy_import.json  # edit
cd godot/tools/blender && ./run_cathedral.sh build_meshy_import.py
# one-off, no config:
#   blender --background --python build_meshy_import.py -- \
#     --in ../../assets/3d/meshy/hero/boat.glb --out ../../assets/3d/locales/boat.glb \
#     --height 3.2 --color 8a8878 --decimate 0.6
```

Then place the finished GLB in the scene (`.tscn` or via `LocaleSetup`) like any
other locale mesh, and light it with real `Light3D` nodes.

## Honest constraints (unchanged)

The T2 output is untextured on purpose: it inherits the project's flat
vertex-color look, not photoreal texturing. Hero objects raise the ceiling on
*silhouette and form* past procedural cubes; they do not change the "no texture
assets, screen-space shaders only" rule for the world around them.
