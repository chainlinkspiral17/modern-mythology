# CLAUDE.md

Project guidance for Claude (any session) working on Modern Mythology.

## Always read before starting work

When picking up a session in this repo, **read these first** before
touching code:

1. `lore/_3D_MODELING_PLAYBOOK.md` — hard-won rules for the Blender
   → glTF → Godot pipeline. Read the Core rules and the latest two
   entries under "Recent lessons."
2. The latest commit message on the working branch — recent context.
3. If working on a specific volume, the relevant `lore/_VOL{N}_WIKI.md`.

## Lesson-capture cadence (durable rule)

After every significant work session — meaning anything that
involved more than ~3 commits OR an aesthetic decision OR a piece of
specific user feedback — append a dated entry to the "Recent lessons"
section of the relevant playbook. Use the TEMPLATE block at the
bottom of each playbook file. Graduate stable lessons up to "Core
rules" once they've held across multiple sessions.

Playbooks currently maintained:
- `lore/_3D_MODELING_PLAYBOOK.md` — Blender → Godot 3D pipeline.

When a new domain accumulates ≥ 5 distinct lessons, spin up a
playbook for it (e.g. `_GAUNTLET_DESIGN_PLAYBOOK.md`,
`_SHADER_PLAYBOOK.md`).

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
