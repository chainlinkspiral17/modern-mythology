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
| `F` | toggle clean full-screen capture view (hides HUD + timeline, native res) |
| `P` | save a frame to `user://frames/` (chrome auto-hidden for the grab) |
| `H` | toggle the on-screen help |
| **Timeline** | |
| `T` | play / pause the timeline (syncs to the music track if one is loaded) |
| `Y` | stop and rewind to 0 |
| `;` `'` | scrub the playhead back / forward |
| `O` | cycle the keyframe target (camera / rig / …) |
| `J` | set a keyframe for the selected target at the playhead |
| `G` | cycle the reference image placement (corners / full / hidden) |
| `L` | load the next reference image (from `user://refs/` or `scenes/previz/refs/`) |
| `U` | drop a reference-image cue at the playhead |
| `/` | save the timeline to `user://timeline.json` |
| **Lighting (LX)** | |
| `4` | cycle the lighting look (warm/cool wash, colour sweep, chase, strobe, follow, blackout) |
| `5` | toggle strobe |
| `6` | toggle blackout |
| `7` `8` | volumetric fog density down / up |
| `F1` `F2` | smoke-machine density down / up (5 emitters around the stage) |
| `-` `=` | master dimmer down / up |
| `9` | aim the follow spot at the lead performer |
| **FX** | |
| `V` | trigger the helicopter flyby + breakaway roof/glass debris (sets disaster mood) |
| `0` | reset the disaster (heli hidden, debris back in place) |

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
- **Phase 4 ✓** — Timeline spine: camera/object/audio/ref-image keyframe tracks on one playhead that syncs to the music; reference overlay (corners/full); drawn timeline strip; save to JSON
- **Phase 5 ◐** — lighting rig (colored wash fixtures + follow spot, visible beams in volumetric fog), chases that play along the music clock, fog density control, hot technician keys. Project flipped to **Forward+**. (Graphical technician console + per-fixture timeline tracks still to come.)
- **Phase 6 ✓** — helicopter flyby + breakaway roof/glass debris (rigid-body physics) + dust bursts on the disaster beat (`V` trigger, `0` reset)
- **Phase 7** — graphical technician console + per-fixture timeline tracks; timeline-cue trigger for the disaster; asset-swap UI + real venue/model geometry once the `.glb`s land

## Disaster FX (Phase 6)
`V` flies the helicopter in on an approach → low-buzz → depart path over the
hangar mouth; at the buzz it breaks off roof panels + glass panes (real
RigidBody3D physics) that fall onto the stage-side crowd, with a dust burst, and
snaps the lighting to the **disaster** mood. `0` resets it (heli hidden, pieces
returned). Drop a `helicopter.glb` at `res://assets/models/` and it's used in
place of the procedural blockout. (Firing it from a timeline cue instead of a
key comes in Phase 7.)

## Renderer: Forward+
The project is now on the **Forward+** renderer (needed for volumetric fog and
visible light beams; the Steam Deck runs it fine). To revert to the 2D-VN's old
`gl_compatibility` renderer:
```bash
sed -i 's/renderer\/rendering_method="forward_plus"/renderer\/rendering_method="gl_compatibility"/; s/"Forward Plus"/"GL Compatibility"/' godot/project.godot
```

## Stage rigs (3, escalating)
`StageRig.gd` builds the truss structure, and each stage **builds on the last**:
1. front truss on two towers; 2. + upstage truss, side booms, backdrop frame;
3. + overhead grid, PA/LED towers, downstage floor truss + thrust. Switch with
`1`/`2`/`3`; the lighting rig rebuilds to match.

## Lighting / fog (Phase 5, cinematic pass)
`LightingRig.gd` hangs **typed, cinematic fixtures** that grow with the stage:
a warm shadow-casting **key**, cool **rim/back** lights for separation, colour
**washes**, sweeping **beam** movers (strong volumetric beams), audience
**blinders**, and floor **up-lights**. The environment runs ACES tonemap, bloom
and SSAO; a **SmokeMachine** adds drifting haze on top of denser volumetric fog
so beams read clearly.

`4` cycles looks (key+rim, warm/cool wash, colour sweep, beam fan, alternating
chase, strobe, follow spot, blackout) — moving looks animate off the **timeline
clock** so they chase in time with the music. `5` strobe, `6` blackout, `7`/`8`
haze (fog+smoke), `-`/`=` master dimmer, `9` follow spot on the lead performer.
(Graphical technician console + per-fixture keyframe tracks still to come.)

## Timeline (Phase 4)
One playhead drives everything. If a music file is found
(`res://assets/audio/song.ogg|smoke_it.ogg` or `user://song.ogg`) it becomes the
master clock so cues "play along with the music". Tracks:
- **Camera** — keyframe the view pose + fov (`O` to select `camera`, fly to a
  framing, `J` to key). Playback drives the camera and disables fly nav.
- **Object** — keyframe any registered Node3D's transform; `rig` is registered
  so you can e.g. rotate the whole lighting/stage rig over time.
- **Audio cues** — one-shot SFX fired as the playhead crosses them.
- **Ref-image cues** — show a storyboard/reference frame (placement) at a time.

`T` play, `;`/`'` scrub, `J` keyframe, `U` ref cue, `/` save to
`user://timeline.json`. The bottom strip shows tracks, keyframe ticks and the
playhead. (Click-to-edit + the technician console arrive in Phase 5.)

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
