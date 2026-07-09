# CLAUDE.md

Project guidance for Claude (any session) working on Modern Mythology.

## Always read before starting work

When picking up a session in this repo, **read these first** before
touching code:

1. `lore/_3D_MODELING_PLAYBOOK.md` — hard-won rules for the Blender
   → glTF → Godot pipeline. Read the Core rules (especially the
   "Coordinate frame" section) and the latest two entries under
   "Recent lessons."
2. `lore/_SHADER_VISUALS_PLAYBOOK.md` — screen-space shaders, mood
   presets, post-process stack order, Label3D vs procedural text,
   active shader + mood inventory. Read before touching any visuals.
3. `lore/_LIGHTING_PLAYBOOK.md` — cinematography rules: three-light
   foundation, practicals tied to visible fixtures, color gels by
   Kelvin, when Spot vs Omni. Read before touching any `Light3D`
   nodes in a scene.
4. `lore/_LIMINAL_PLAYBOOK.md` — how "the walls are thin here" is
   rendered (the show / imagination / threshold subtype system).
   Read before tagging a station as liminal OR adding a new
   locale scene. JSON is the single source of truth; the
   drift-checker will warn at scene-open if anything desyncs.
5. `lore/_GAUNTLET_DESIGN_PLAYBOOK.md` — scenario-level design for
   TAROT GAUNTLET: the setup JSON, the visitor casts, win/loss
   condition shape, the bookend pattern per arcana, time-of-day as
   difficulty axis. Read before authoring any new gauntlet
   `setup_*.json` file OR adding scenario_visitors[] inline.
6. `lore/_COMMUNITY_PLANNED_PLAYBOOK.md` — mission stages, BBS
   thread gating, pressure curve, three-slot save. Read before
   editing problems.json, agents.json, or CommunityPlannedGame.gd.
7. The latest commit message on the working branch — recent context.
8. If working on a specific volume, the relevant `lore/_VOL{N}_WIKI.md`.
9. If planning NEW slowsticks or building the deferred early
   ones, `lore/_SLOWSTICK_CATALOG_ROADMAP.md` — full plans for
   Estuary 1 + 2 and six imagined sticks, plus the canon lattice
   (studios, people, dates) that must not be contradicted.
   AND `lore/_SLOWSTICK_AESTHETIC_BIBLE.md` — the alternate-
   universe tech premise: slowsticks render MODERN through
   `SlowstickLook.apply()` per-studio presets (demoscene_post);
   no our-timeline retro cosplay (scanline loops, phosphor
   fiction), font floor 12. Read before touching ANY slowstick
   visuals or writing a LOOK section.
10. If touching a slowstock, its per-stick design doc:
   - `lore/_ESTUARY_3_DESIGN.md` (four-act + Manager Mode)
   - `lore/_PIRATE_SUMMER_DESIGN.md` (six-day + Counselor Mode)
   - `lore/_FEY_FAIRE_DESIGN.md` · `lore/_EARTHMAN_CHRONICLES_DESIGN.md`
   - The eight planned sticks each have full docs too:
     _ESTUARY_1_, _ESTUARY_2_, _NORTHWIND_HARBOR_,
     _BASILICA_OF_WIRES_, _SWEETGUM_, _RIFFMASTER_MELODY_CLUB_,
     _HANE_NO_NIWA_, _PATIENT_MISTER_GLASS_ (all `_DESIGN.md`)
   These carry the multi-hour authoring context that
   won't fit in a commit-message header.

## DEBUG HUD — F4 IS THE MASTER TOGGLE (hard rule)

**Every new HUD overlay MUST honor F4.** The player wants clean
pictures of gameplay; debug text appearing in screenshots is a
recurring complaint. The rules:

1. F4 toggles `FirstPersonController.hud_visible` (a static var)
   and walks the scene tree hiding every `CanvasLayer` plus every
   `"ui"`-group member.
2. Any NEW HUD layer (CanvasLayer, top-level Control) you add
   MUST:
   - Set `visible = FirstPersonController.hud_visible` on spawn
     so it inherits the current toggle state.
   - Either join the `"ui"` group OR live inside a CanvasLayer
     (which F4 already catches).
3. NEVER add a Label or other UI element directly under the
   scene root (it bypasses the F4 sweep). Put it inside a
   CanvasLayer.
4. World-rendering CanvasLayers (PostProcess shaders) should NOT
   be hidden by F4 — those aren't HUD. F4 only sweeps the scene
   tree from root, but the PostProcess CanvasLayer is hidden by
   the same call. If a PostProcess CanvasLayer ever needs to
   survive F4, add it to a `"world_render"` group and skip in
   the F4 sweep. For now: HUD only.
5. Test by pressing F4 at SCENE START before any dynamic HUD
   members (music player, mood label) have had time to spawn,
   then waiting for them to spawn — they must NOT pop up.

## Lesson-capture cadence (durable rule)

After every significant work session — meaning anything that
involved more than ~3 commits OR an aesthetic decision OR a piece of
specific user feedback — append a dated entry to the "Recent lessons"
section of the relevant playbook. Use the TEMPLATE block at the
bottom of each playbook file. Graduate stable lessons up to "Core
rules" once they've held across multiple sessions.

Playbooks currently maintained:
- `lore/_3D_MODELING_PLAYBOOK.md` — Blender → Godot 3D pipeline.
- `lore/_SHADER_VISUALS_PLAYBOOK.md` — screen-space shaders, mood
  system, post-process ordering, Label3D vs procedural text,
  particles checklist, active shader/mood inventory.
- `lore/_LIGHTING_PLAYBOOK.md` — three-light foundation,
  practicals, color gels by Kelvin, Spot vs Omni decisions.
- `lore/_LIMINAL_PLAYBOOK.md` — liminal-station rendering
  (show / imagination / threshold subtypes), JSON-as-source-of-
  truth discipline, runtime drift-checker contract, current
  liminal roster across all locations.
- `lore/_GAUNTLET_DESIGN_PLAYBOOK.md` — scenario-level authoring for
  TAROT GAUNTLET: setup JSON schema, scenario_visitors inline
  pattern, bookend easy/hard difficulty shape, time-of-day as
  primary difficulty axis, named loss conditions as pedagogy.
- `lore/_COMMUNITY_PLANNED_PLAYBOOK.md` — mission stages, BBS-lookup
  gating, mid-summer pressure curve (W6/W12/W18), three-slot save.
- `lore/_AUDIO_PLAYBOOK.md` — audio authoring pipeline
  (`slowstick_synth.py`), SFXBank pool discipline, audit-driven
  wave-authoring, HTML importer parity, formant-synth ceiling.
- `lore/_SPRITE_PLAYBOOK.md` — two-tier sprite system
  (SlowstockSprite palette-indexed + HeroImage primitive-language),
  PNG-override escape hatch, fallback discipline across every
  render path, 3×5 font conventions.
- `lore/_SLOWSTOCK_AUTHORING_PLAYBOOK.md` — host/child-scene
  contract, uniform SlowstockBoot signal set (quit_to_shelf +
  finished), `_run_state` shape, the beat-sequence pattern for
  chapter scenes, the three-phase ending scene pattern (gather →
  choice → ending playback), data-driven scenes for negotiation
  and combat, `_delta` sets convention.

When a new domain accumulates ≥ 5 distinct lessons, spin up a
playbook for it.

## Working branches

- `claude/3d-locales` — current 3D pipeline work. The riverfront
  scene is at `godot/scenes/locales/riverfront.tscn`, built from
  `godot/tools/blender/locales/build_riverfront.py`.

## Build commands

On the user's Steam Deck:

```bash
cd /home/deck/Downloads/modern-mythology
git pull origin claude/3d-locales
cd godot/tools/blender
./run_cathedral.sh build_riverfront.py     # or any build_*.py script
```

The runner auto-detects Blender (Steam / Flatpak / AppImage / PATH)
and writes the GLB to `godot/assets/3d/locales/<name>.glb`.

## Always give the user copy-paste commands

When the user needs to run anything on their machine (pull, build,
git, restart Godot, etc.), provide the **exact command in a fenced
code block** they can paste in one go. Never describe the steps in
prose and make them assemble the command themselves. Multi-step
flows go in a single chained `&&` line when possible — the user runs
on a Steam Deck terminal and every extra paste is friction.

Example — wrong:
> First, cd into the repo. Then pull the latest. Then go to the
> blender tools folder and run the build script.

Example — right:

```bash
cd /home/deck/Downloads/modern-mythology && git pull origin claude/3d-locales && cd godot/tools/blender && ./run_cathedral.sh build_riverfront.py
```

## Honest constraints

- **No texture assets.** All locale geometry uses vertex colors as
  flat material identifiers; lighting comes from real `Light3D`
  nodes. We cannot reach MGS2 / hand-painted-texture quality from
  this pipeline. Be honest about that ceiling instead of promising
  it.
- **Screen-space shaders only.** Locale meshes render through
  `StandardMaterial3D`; visual effects come from the post-process
  stack (`ascii_render` → `demoscene_post`). Do not write per-mesh
  shaders for locales.
