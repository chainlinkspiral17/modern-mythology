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
4. The latest commit message on the working branch — recent context.
5. If working on a specific volume, the relevant `lore/_VOL{N}_WIKI.md`.

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

When a new domain accumulates ≥ 5 distinct lessons, spin up a
playbook for it (e.g. `_GAUNTLET_DESIGN_PLAYBOOK.md`).

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
