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
| `K` | add a director camera from the current view, using the pending move |
| `M` | cycle the pending camera move (push in / crane / orbit / …) |
| `Tab` | switch between the fly camera and the active director camera |
| `Space` | play / pause the active camera's keyframed move (loops) |
| `[` `]` | scrub the active camera's timeline |
| `,` `.` | previous / next director camera |
| `\` | save all director cameras to `user://previz_cameras.json` |
| `I` | import a storyboard (`user://storyboard.json`) → build a camera per shot |
| `N` `B` | step to the next / previous storyboard shot |
| `R` | batch-render a start frame for every shot + export camera data |
| `P` | save a frame to `user://frames/` |
| `H` | toggle the on-screen help |

### Camera director (Phase 2)
Fly to a framing, press `M` until the move you want is shown, then `K` to drop a
camera that performs that move from where you're standing (push in, crane up,
orbit, whip pan, rise-to-reveal, etc. — the same vocabulary as the Storyboard
tool). `Tab` to preview it live, `Space` to play, `[` `]` to scrub. Phase 3 will
build one of these automatically per storyboard shot.

## Swapping in real 3D models

Models are authored in Drive at **`one model nation finale/3D model/`**.

**The hangar** (`barn hanger.glb`): drop it at `res://assets/models/barn hanger.glb`
and `Hangar.gd` loads it automatically instead of the procedural barrel-vault
blockout (it checks a few candidate paths — see `MODEL_CANDIDATES`). The
blockout is a corrugated Quonset arch at roughly reference scale (~18 m wide,
~11.5 m tall, 55 m long) so framing reads correctly until the real model is in.

**Characters:** download a `.glb`/`.gltf` into the project (e.g.
`res://assets/models/`), let Godot import it, then add a `"model"` path to that
character in `data/characters.json`:

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
- **Phase 1 ✓** — procedural blockout, 3 stage rigs, moods, fly camera, character stand-ins, screenshot
- **Phase 2 ✓** — multi-camera director with keyframed moves/FOV on a timeline (storyboard move vocabulary), save to JSON
- **Phase 3 ✓** — Storyboard JSON import (shots → camera/mood/stage/time) + batch frame render + per-shot camera export back to the tool
- **Phase 4** — asset-swap UI, lighting-mood interpolation over time, real venue/model geometry once the `.glb`s land

## Storyboard round-trip (Phase 3)
1. In the HTML **Storyboard Pipeline** tool, click *Export project (.json)*.
2. Rename it `storyboard.json` and put it where the running game can read it —
   `user://storyboard.json` (on Linux: `~/.local/share/godot/app_userdata/Modern Mythology/`),
   or drop it at `res://scenes/previz/data/storyboard.json`.
3. In the previz scene press **`I`** — each shot becomes a camera with its
   storyboard move, its set's stage rig, and a mood from its time-of-day
   (`night`→night, `dusk`→dusk, `sfx` beats→disaster). Stage level follows set
   order (1/2/3 = NoNo / One Model Nation / Zonk).
4. **`N`/`B`** to step shot-to-shot; **`Space`** to play a shot's move.
5. **`R`** batch-renders a start frame per shot to `user://frames/shot_NN.png`
   and writes `user://storyboard_previz.json` (per-shot camera pos/target/fov +
   frame name) to fold back into the storyboard tool as start frames.

Framing is auto-derived from each shot's *type* (close/medium/wide/crowd/
overhead/insert…); treat it as a starting block you nudge, then re-save (`\`).
