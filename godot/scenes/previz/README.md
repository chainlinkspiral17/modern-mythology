# Previz — 3D staging sandbox

A 3D pre-visualisation module living inside the Modern Mythology Godot project
(`res://scenes/previz/`). It blocks out the **giant barn-hangar festival venue**
and the **three escalating stage shows** (NoNo / One Model Nation / Zonk) so you
can stage cameras and lighting moods, then feed start-frames + camera data into
the HTML **Storyboard Pipeline** tool.

> **Phase 1 (this drop):** procedural blockout, three stage rigs, dusk/night/
> disaster moods, fly camera, capsule character stand-ins, frame screenshot.
> Built entirely from primitives so it runs with **zero imported assets**.
> Not yet opened in an editor here (headless env) — if it throws on load, send
> the error and it'll be fixed fast.

## Run it

Open the project in **Godot 4.4+**, then run this scene directly: select
`scenes/previz/Previz.tscn` and press **F6** (Run Current Scene). It does not
touch the visual-novel game (`Main.tscn`).

### Controls
| Key | Action |
|-----|--------|
| `W A S D` / `Q E` | fly (hold `Shift` to move faster) |
| Right mouse (hold) | look around |
| `1` `2` `3` | stage show: NoNo · One Model Nation · Zonk |
| `Z` `X` `C` | mood: dusk · night · disaster |
| `P` | save a frame to `user://frames/` |
| `H` | toggle the on-screen help |

## Swapping in real 3D models

Models are authored in Drive at **`one model nation finale/3D model/`**.
Download a `.glb`/`.gltf` into the project (e.g. `res://assets/models/`), let
Godot import it, then add a `"model"` path to that character in
`data/characters.json`:

```json
{ "id": "nono", "name": "NoNo Von Deutschland", "band": "Nana Avatar",
  "color": "d05a9a", "zone": "stage", "model": "res://assets/models/nono.glb" }
```

The swapper instances the scene if the path exists, otherwise it falls back to a
coloured capsule — so you can drop models in one at a time.

## Files
- `Previz.tscn` / `Previz.gd` — scene root + orchestrator (build, nav, input, moods, screenshot)
- `Hangar.gd` — procedural venue blockout (hangar shell, gable roof, ground, stage riser)
- `StageRig.gd` — the three progressive stage-show rigs (`build(level)`)
- `Moods.gd` — dusk / night / disaster lighting presets
- `data/characters.json` — character roster + per-character model paths

## Renderer note
The host project is set to `gl_compatibility` (for the 2D VN). 3D renders fine
there, but the richer toys — volumetric fog, SDFGI, SSAO — need **Forward+**.
On a Steam Deck (Vulkan/RDNA2) Forward+ runs comfortably; flipping the project
renderer is a one-line change in `project.godot` and is reversible.

## Roadmap
- **Phase 2** — multi-camera director with keyframed moves/FOV on a timeline (matching the storyboard's camera-move vocabulary)
- **Phase 3** — Storyboard JSON import (shots → camera/mood/stage/time) and batch frame + per-shot camera/light export back into the tool
- **Phase 4** — asset-swap UI, lighting-mood interpolation over time, real venue/model geometry
