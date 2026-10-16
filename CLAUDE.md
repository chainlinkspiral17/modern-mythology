# CLAUDE.md

Project guidance for Claude (any session) working on Modern Mythology.

## Always read before starting work

When picking up a session in this repo, **read these first** before
touching code:

0. `lore/_IMPROVEMENT_ROADMAP.md` — the living prioritized plan
   (per-pillar backlogs, the user-side gates, recommended sequence).
   Update it when items ship or a blocking decision lands.
   AND `lore/_VISUAL_PROGRAM.md` — the 2026-09-13 plan for the four
   big pillars (backgrounds · models · direction · design): the
   arc sequence, the contact-sheet loop (Arc 0), and the decisions
   the user owns. Update it when an arc ships.

1. `lore/_3D_MODELING_PLAYBOOK.md` — hard-won rules for the Blender
   → glTF → Godot pipeline. Read the Core rules (especially the
   "Coordinate frame" section) and the latest two entries under
   "Recent lessons."
2. `lore/_SHADER_VISUALS_PLAYBOOK.md` — screen-space shaders, mood
   presets, post-process stack order, Label3D vs procedural text,
   active shader + mood inventory. Read before touching any visuals.
2b. `lore/_PSYCHEDELIC_DESIGN_BIBLE.md` — THE TRIP: the project-
   wide music-synced psychedelic layer (TripSync autoload +
   trip_sync.gdshader) and the four pillar REGISTERS (arcana ·
   community · milk_honey · slowstick/Minter) with each pillar's
   sound, visual register and GAME grammar. Read before touching
   TripSync, the trip shader, or any pillar's look-and-feel or
   game-design direction. Current hardware only — no retro cosplay
   anywhere in the game.
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
7. `lore/_MASTER_TIMELINE.md` — the RATIFIED chronology spine for
   all volumes (vol5 ~2019 · vol6 2025–26 · vol7 Aug–Sep 2052).
   Read before dating ANYTHING. When prose and the timeline
   disagree, flag it there as a knot — never silently fix either
   side, and never re-derive a volume's present from stray dates
   in older lore files.
8. `lore/_CONTROLLER_STEAM_PLAYBOOK.md` — pad input translation
   layer (GamepadMgr), one-path-per-input rule, haptics grammar
   (SFXBank RUMBLE_MAP), Steam Machine build. Read before touching
   ANY input handling, adding a UI surface, or authoring rumble.
9. The latest commit message on the working branch — recent context.
10. If working on a specific volume, the relevant `lore/_VOL{N}_WIKI.md`
   and, for vol 7, the scene JSONs at `godot/resources/scenes/vol7/`
   (the prose is the authority; the wiki is downstream).
11. If planning NEW slowsticks or building the deferred early
   ones, `lore/_SLOWSTICK_CATALOG_ROADMAP.md` — full plans for
   Estuary 1 + 2 and six imagined sticks, plus the canon lattice
   (studios, people, dates) that must not be contradicted.
   AND `lore/_SLOWSTICK_AESTHETIC_BIBLE.md` — the alternate-
   universe tech premise: slowsticks render MODERN through
   `SlowstickLook.apply()` per-studio presets (demoscene_post);
   no our-timeline retro cosplay (scanline loops, phosphor
   fiction), font floor 12. Read before touching ANY slowstick
   visuals or writing a LOOK section.
12. If touching a slowstock, its per-stick design doc:
   - `lore/_ESTUARY_3_DESIGN.md` (four-act + Manager Mode)
   - `lore/_PIRATE_SUMMER_DESIGN.md` (six-day + Counselor Mode)
   - `lore/_FEY_FAIRE_DESIGN.md` · `lore/_EARTHMAN_CHRONICLES_DESIGN.md`
   - The eight planned sticks each have full docs too:
     _ESTUARY_1_, _ESTUARY_2_, _NORTHWIND_HARBOR_,
     _BASILICA_OF_WIRES_, _SWEETGUM_, _RIFFROCKER_MELODY_CLUB_,
     _HANE_NO_NIWA_, _PATIENT_MISTER_GLASS_ (all `_DESIGN.md`)
   - `lore/_MRS_WUS_GARDEN_DESIGN.md` — stick #16 (built 2026-07)
   - `lore/_THE_TIDELINE_DESIGN.md` — stick #17 + 2048 remake (built 2026-07)
   - `lore/_ESTUARY_4_DESIGN.md` — stick #18, the course-correction (built 2026-07)
   - `lore/_SPIDERDROPS_DESIGN.md` — stick #19, Pretty Dreams physics
     puzzle · the one live Verlet renderer (built 2026-07)
   - `lore/_SPIDERDROPS_2_DESIGN.md` — stick #20, THE LONG WIND ·
     post-game sequel · balloon-glide, carries the register in
     (built 2026-07)
   - `lore/_SALMONBERRY_DESIGN.md` — stick #21, Oneironautics 1992
     (Amelie Rocha) · part-RPG part-adventure, a year in a 1960s
     coastal Oregon town · v1 = the month/aptitude/bond loop; town
     overworld + arc waved (built 2026-07). ART: full-res modern
     painted illustration (see THE CORRECTION in the aesthetic
     bible — no SVGA/era-filter retro cosplay).
   These carry the multi-hour authoring context that
   won't fit in a commit-message header.

## NOTHING IS DONE — THE DRAFTING PROGRAM (hard rule)

The user's standing verdict (2026-08-03): *"It all reads like first
draft. Keep drafting into the dozens and dozens."* Every build,
scene, system, and art pass in this project is a NUMBERED DRAFT,
not a deliverable. The quality bar is the **model chapters** — the
handful of spaces that have absorbed many sessions of iteration
(the diner, the kwik stop, the cathedral, the henderson house).
Everything else is below the bar by definition until repeated
passes bring it up.

Rules:
1. **Never report work as "done", "complete", or "closing the
   arc".** Report it as *"draft N shipped; draft N+1 targets: …"*
   and record the next-pass targets in
   `lore/_IMPROVEMENT_ROADMAP.md` under THE DRAFTING PROGRAM.
2. **Anticipate the next pass while making this one.** Leave the
   next session a concrete list of what draft N+1 should do — in
   the builder's docstring and in the roadmap — the way
   build_highway9_2026_08() does.
3. **A first-generation build (template + props) is draft 1**, no
   matter how many props it has. Model-chapter quality means:
   staged sightlines, camera coverage, lighting that models the
   space, prose-anchored hero objects, edge-of-set treatment (no
   visible world edges), and Deck-verified framing. Most locales
   have only the props.
4. When the user says a space "feels like a set", the fix is
   usually SCALE + EDGES + COVERAGE (run the geometry past the
   frame, hide the world edge, add camera setups), not more props.
5. **Build BIG (user, 2026-10-07): "Don't be afraid to make spaces
   and floorplans bigger. Backgrounds always felt small and
   claustrophobic."** Size a room from what the prose says happens in
   it and what such a place really measures — a supermarket with
   twelve aisles is not a 10 x 8 m box — and then err LARGER: generous
   lanes (1.4 m+ between store fixtures, 0.9 m in front of every case
   door), real ceiling heights, rooms that open onto other rooms. When
   a pass finds a cramped plan, enlarge the room before shaving the
   furniture. `walkway_audit` and `case_access_audit` are floors, not
   targets.

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
5. **A full-screen surface that IS a game is not HUD.** Any
   root that carries a playable screen — the Slowstock TV wrap,
   a slowstick host/stub, the planned-community screen and its
   BBS, the gauntlet board — joins `"game_surface"` as well as
   `"ui"`, and the F4 sweep skips those. Getting this wrong
   shipped a real bug (2026-08-12): F4 mid-slowstick hid the
   whole television while its invisible InputBlocker kept eating
   keys, so clicks fell through to the menu underneath and
   randomly opened SCENE EDITOR (two nav rows below SLOWSTOCK
   LIBRARY). HUD *inside* a game surface still toggles normally,
   because the sweep visits `"ui"` members directly.
6. Test by pressing F4 at SCENE START before any dynamic HUD
   members (music player, mood label) have had time to spawn,
   then waiting for them to spawn — they must NOT pop up.

## Verify GDScript with BOTH checkers (hard rule)

`gdparse <file>` checks GRAMMAR only. Godot **also** runs type
inference and rejects `:=` when the right-hand side has no static
type — syntactically perfect code the linter waves through. This
shipped a broken build on 2026-07-28 (`var x := {...}[key]` in
Estuary 4's working season: "Cannot infer the type").

So every GDScript change is verified twice:

```bash
gdparse <file> && python3 godot/tools/gdinfer_check.py <file>
```

`gdinfer_check.py` flags the Variant-returning right-hand sides
(`{...}[k]`, `.get()`, `.call()`, `get_meta()`, `JSON.parse_string`,
untyped container indexes) and is tuned to report **zero** on the
working tree — if it ever prints something, it is real. Fix by
naming the value and typing it explicitly:

```gdscript
var lines: Dictionary = {...}
var line: String = String(lines.get(key, ""))
```

## Google Drive: every write goes through drive_guard (hard rule, 2026-10-13)

The user: "I want nothing more going to a public shared folder. Very
serious." Twice the project's files landed on the One Model Nation shared
drive (a re-sign-in pointed rclone at it; then a Hero Studio running old
code re-created the folder there). Now:

- **The only writer is `godot/tools/drive_guard.py`** (`rclone_write`,
  `make_root`). It fails closed: rclone env overrides, any remote but
  `gdrive`, any path outside `gdrive:ModernMythology`, a `team_drive` or
  `root_folder_id`, a folder Google reports with no owner (a shared drive),
  or an owner different from the recorded one → nothing is written.
  Shortcuts are never followed.
- **Never** call rclone with a write verb anywhere else, and never use the
  Drive connector tools (create/copy/update/trash) on the user's files.
  Reads into the machine are tagged `drive-read`.
- `drive_write_audit.py` and `drive_guard_test.py` run first in every
  suite (full and scoped). They must stay at zero.
- Hero Studio refuses SAVE when its code changed on disk since it started
  — after a pull the user restarts it (`bash godot/tools/hero_studio.sh`).
- Say a Drive fix is in effect only once it is pushed AND the user has
  pulled and restarted; until then tell them not to press SAVE.

## Run the SCOPED suite before a commit (2026-10-13)

The user: "audit taking over an hour for simple fixes." Before a commit run

```bash
bash godot/tools/audit/run_changed_audits.sh
```

It reads what changed against `origin/claude/3d-locales-clean` (plus the
working tree). Tools, the Hero Studio roster, portrait / hero-art runtime,
Drive scripts and docs get their own checks in seconds (py compile, JSON,
gdparse + gdinfer_check, `bash -n`, .tscn syntax, the roster loader).
Anything that can move the world — a builder, a locale .tscn, chapter
JSON, Background3D / the director, audio, the audits — runs the full
`run_all_audits.sh` exactly as before (`FULL=1` forces it). Widen the
LIGHT list in the script only for files no gate reads.

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
- `lore/_CONTROLLER_STEAM_PLAYBOOK.md` — GamepadMgr translation
  layer, one-path-per-input rule (double-fire guards), haptics
  grammar in SFXBank.RUMBLE_MAP, Steam Machine export + build
  script, per-stick pad-audit inventory.
- `lore/_SET_DETAIL_PLAYBOOK.md` — the detail-pass method for THE
  DRAFTING PROGRAM: D2 surface breakup, D3 infrastructure, D4 use
  states, D5 depth bands + edges, D6 coverage + light. Read before
  running ANY detail pass on a locale.
- `lore/_GEOMETRY_AUDIT_PLAYBOOK.md` — the headless geometry gates
  (stump hunt, clipping hunt, preset vantages): stub fidelity,
  natural-contact grammar discipline, the zero-regression
  ceilings, the wheel/double-booking defect classes. Read before
  touching godot/tools/audit/ or dismissing an audit report.

When a new domain accumulates ≥ 5 distinct lessons, spin up a
playbook for it.

## Working branches

- `claude/mythology-game-fiction-ji1t2g` — the CURRENT unified
  working branch (2026-10-16): the Deck's `claude/3d-locales-clean`
  line (locales, slowsticks, Hero Studio, controller work) merged
  with the game-fiction line (master timeline, 2026 sweep, enemy
  arc, staged-effort fix). All work lands here until promotion.
  The standard Deck pull is:

  ```bash
  cd /home/deck/Downloads/modern-mythology && git checkout -- godot/project.godot && git fetch origin claude/mythology-game-fiction-ji1t2g && git checkout claude/mythology-game-fiction-ji1t2g && git pull origin claude/mythology-game-fiction-ji1t2g
  ```

- `main` — the promoted mainline (July 2026): 3D locale pipeline,
  VN engine, TAROT GAUNTLET, COMMUNITY PLANNED. The riverfront
  scene is at `godot/scenes/locales/riverfront.tscn`, built from
  `godot/tools/blender/locales/build_riverfront.py`. Session
  branches merge back to `main` when promoted; the old
  `claude/3d-locales` / `claude/3d-locales-clean` lines are
  historical.

## Build commands

On the user's Steam Deck (Blender locale builds only):

```bash
cd /home/deck/Downloads/modern-mythology
git pull origin claude/mythology-game-fiction-ji1t2g
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
cd /home/deck/Downloads/modern-mythology && git checkout -- godot/project.godot && git pull origin claude/mythology-game-fiction-ji1t2g && cd godot/tools/blender && ./run_cathedral.sh build_riverfront.py
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
