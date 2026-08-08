# VN SCENE DIRECTION · the 3D comic

How the visual novel gets a camera. The target is NOT film — it is
a COMIC read in 3D space: hard cuts between held frames, the way a
page moves panel to panel. Motion is the exception, not the rule.

## The grammar · four shot types

1. **ESTABLISH** — the locale wide. Where the reader learns the
   room. Default shot; every scene opens here.
2. **CLOSEUP** — a speaker or a face. The bust/portrait moment.
3. **INSERT** — a prop, held close: the register, the tape, the
   note on the counter. The comic's "detail panel."
4. **PANEL** — a 2D info card OVER the scene: a receipt, a page,
   a diagram. Rendered flat (HeroImage JSON or text card) inside
   a comic border, on a CanvasLayer in the "ui" group (F4 rule).

Cuts by default. A shot may DRIFT (slow push-in, ~2%/sec) when the
text lingers — mark it explicitly. Never ease between shots like a
camera operator walked there; a comic does not pan between panels.

## Beats · [beat:x] · synchronized emphasis (2026-07)

The producer discipline at line level: one directive fires a sting
(haptic included, via SFXBank.RUMBLE_MAP), a camera breath, and a
letterbox pulse TOGETHER. Four house beats — keep the vocabulary
small; a beat that appears twice a chapter stays an event:

| beat | reads as | sting | camera |
|---|---|---|---|
| `[beat:still]` | a held hush | none | gentlest push (0.94) |
| `[beat:hit]`   | the hard beat | loss_thud | sharp push (0.88) |
| `[beat:chill]` | the uncanny | tier_crossing_close | slow push, longest hold |
| `[beat:lift]`  | wonder / relief | interlude_earned | pulls BACK (1.06) |

Rules: beats chain with other directives (`[beat:chill][shot:closeup
x]` fires both); they park until the locale loads like mood/stage; a
beat borrows the letterbox and returns it unless a shot claims the
bars during the hold; a beat cancels drift (the next shot restores
it). Camera breath eases home on its own — never author a beat as a
persistent state; that is what [mood:] is for.

First seeds: vol5_ch0_booth6 node 12 (`[beat:still]` on the bell) and
node 17 (`[beat:chill]` on "the walls are thin").

## Kinetic text (native BBCode · 2026-07)

`bbcode_enabled` is on in every dialogue variant and the typewriter's
tag-skipper passes bracketed runs through whole — so RichTextLabel's
effect tags work TODAY in narrate/say/think text:

- `[wave amp=8 freq=3]...[/wave]` — the words go soft/unstable (first
  seed: the stranger's "The walls are thin.")
- `[shake rate=12 level=4]...[/shake]` — fear, cold, interference
- `[fade start=4 length=14]...[/fade]` — trailing off

Restraint rules: one effect per line at most; amp/level low (the 34px
serif carries scale already); never on a whole passage — mark the
three or four words that turn. Pairs naturally with a beat on the
same line.

## Script syntax (parsed + stripped at line display)

Directives lead a VN script line, square-bracketed:

    [shot:establish]           cut to the locale wide
    [shot:closeup sam]         cut to marker shot_closeup_sam
    [shot:insert register~]    cut to shot_insert_register, drifting
    [panel:receipt_47]         overlay panels/receipt_47.json
    [panel:off]                dismiss the panel
    [stage:john counter_post]  place John's hero GLB at cast_counter_post
    [stage:john off]           remove John from the set
    [mood:dambrosios_3am]      apply a MoodCycler STYLE_PACK (or bare
                               mood) by name — lighting + post as one look

`~` suffix = drift. Unknown marker/panel/spot/model/mood = silent
no-op (fallback discipline — a script must never crash the reader).

## Cast staging (v3)

- **Anchors**: `Marker3D` named `cast_<spot>` (group `"vn_cast"`) at
  FLOOR level; the marker's yaw is the direction the model faces.
- **Models**: `assets/3d/characters/heroes/*.glb` — STATIC standing
  meshes, no skeleton. They are blocking for wide/establish panels;
  FACES stay on the 2D portrait layer (CharLayer/Portrait3D). Never
  expect a seated pose — block "seated" characters standing beside
  the furniture or pick a beat where they'd stand.
- **Alignment table**: `Background3D.CAST_MODEL_ALIGN`. Audited
  2026-07-11: only john_frank + frasier_temple are Y-up; alberto,
  antonio, dante (1.08 m raw → scale 1.6), elicia, nicola are Z-up
  exports that need the rot_x -90° fix at stage time.
- Staged cast persists across scene jumps that keep the same locale
  preset (D'Ambrosio's chapter chains) and dies with the locale on
  a preset change. Re-stage idempotently at each scene top.
- Locales with a hidden `Hero<FirstName>` node (diner, bungalow,
  riverboat): stage_character reuses it instead of double-loading
  the GLB, and overwrites its transform (the hidden nodes' authored
  transforms predate the Z-up audit — do not trust them).

## The machinery

- **Markers in the locale**: every shot is a `Marker3D` in the
  locale scene, named `shot_<type>_<id>` (or `shot_establish`),
  in group `"vn_shot"`. The marker's transform IS the framing —
  authored in the editor, where framing belongs. Optional metadata
  `fov` (default 50; inserts want ~35).
- **VnDirector** (`godot/scripts/vn/VnDirector.gd`, built): owns
  the cut. `cut_to("closeup_sam", drift)` finds the marker, snaps
  the active Camera3D, starts the drift tween if asked. Also owns
  the **letterbox** — thin bars that appear on closeup/insert
  (comic panel crop) and leave on establish. `panel(id)` /
  `panel_off()` for info cards.
- **Restore**: the director remembers the camera's original
  transform; `release()` puts it back (scene end, ESC menu).

## Wiring (BUILT — v1)

1. `GameEngine.gd` — `_dispatch` routes narrate/say/think through
   `_directed(n)`: regex `^\[(shot|panel):([^\]\r\n]+)\]\s*` strips
   stacked directives off the text front and dispatches each to
   `_director` before display. Zero directives = old behavior; the
   scene-data dict is never mutated (SceneDataDB caches it).
2. `VnDirector` (`godot/scripts/vn/VnDirector.gd`) is created once
   in `_build_layers` and drives the Background3D SubViewport
   camera via new hooks on `Background3D.gd`: `get_camera()`,
   `find_shot_marker(name)`, `has_locale_loaded()`,
   `restore_preset_vantage()`. A shot arriving before the deferred
   `load_location` finishes parks and retries up to 60 frames.
3. `[shot:establish]` falls back to the locale's CAMERA_PRESETS
   vantage when no `shot_establish` marker exists — every existing
   locale supports it with zero markup. closeup/insert with no
   marker = silent no-op (hold the current frame).
4. Letterbox: two ColorRects (z 95) inside GameEngine's own tree —
   NOT a CanvasLayer, so the F4 HUD sweep can't hide the picture.
   On for closeup/insert, off for establish. Panels are a bordered
   card (z 101) in the upper field; dialog owns the bottom.
5. Drift = FOV tighten at 2%/sec, floored at 86% of the shot's
   starting FOV. Cuts snap; nothing eases.
6. First directed locale: `kwik_stop.tscn` — five markers
   (insert_register / insert_door / insert_coffee / closeup_sam /
   closeup_customer). First directed scene:
   `vol6_ch1_shift_change.json` (five directives).
7. MoodCycler untouched — lights are the mood's job; the camera
   is the page's.
8. Panels dir: `godot/resources/vn/panels/*.json` (HeroImage
   schema). Missing file → bordered text card with the id.

## Voice rules for directing scripts

- Establish once per location change; do not re-establish on
  every beat.
- Insert BEFORE the text names the prop, not after — the comic
  shows, then the caption speaks.
- Closeups for decisions and reveals; hold them across the whole
  exchange, don't ping-pong between speakers.
- Drift is for dread and patience only. If everything drifts,
  nothing does.

## Recent lessons

### 2026-08-08 · tscn Transform3D is ROW-major · every matrix marker was transposed

- **THE BUG: 49 markers across three sessions serialized the basis
  column-major; Godot's tscn format is ROW-major.** The stored matrix
  was the transpose of the intent: mirrored aim, inverted pitch, and
  a dutch roll. Every matrix-form vn_shot marker ever authored
  (harmony_terrain and the four shop interiors from the original
  shot-grammar session, the 8 road setups of pass 1, the 12 interior
  setups of pass 2) carried it. Fixed by transposing the 9 basis
  floats in place — stored = intendedᵀ, so the transpose restores the
  intent exactly.
- **The proof is structural and worth memorizing: row1 of
  Ry(yaw)·Rx(pitch) is (0, cos p, −sin p) — the serialized zero sits
  at FLOAT INDEX 3.** Editor-authored matrices (the classic default
  light `Transform3D(0.707107, -0.5, 0.5, 0, 0.707107, ...)`, the
  salty_tome Key) all have f3 = 0. The broken markers had f1 = 0.
  Correct serialization: `(cy, sy·sp, sy·cp, 0, cp, −sp, −sy, cy·sp,
  cy·cp, ox, oy, oz)`.
- **A validation against your own earlier output is not a
  validation.** The 08-04 lesson claimed the column convention was
  "validated against harmony_terrain's hand-tuned markers" — but those
  came from the same generator lineage. The independent referent that
  broke the loop was an editor-authored matrix. Always test
  serialization conventions against something the ENGINE wrote.
- **Orthonormality checks can't catch a transpose** — the transpose
  of a rotation is a rotation. The checks that do: f3 == 0 (no roll),
  f4 > 0 (never upside down), and re-deriving forward = −(f2, f5, f8)
  and confirming it points camera→target (< 0.5°). All three are now
  in the pass-3 validator and should run on any future marker wave.
- **The model chapters were immune because they use `position` +
  `rotation` euler properties, not matrices.** That form has no
  convention trap and reads better in diffs — prefer it for
  hand-authored markers; keep matrices only for generator output
  (where the validator runs).

### 2026-08-08 · directing pass 3 · the next eight get their decks

- miller_kitchen, cosmic_comics ×2, missing_link_interior, maya/sam
  bedrooms, school_field_evening, centro_grocery_aisle: 4 setups each
  (B/C rotation + two inserts), 32 markers, all aimed at
  builder-extracted landmarks (the loose floorboard, the one-way
  mirror, the pie case, the scoreboard). 13 locales now carry
  rotation decks — 52 authored setups total.
- **Give the inserts to the PLOT objects, not the pretty ones.**
  maya_bedroom's insert is the loose floorboard cavity;
  cosmic_comics' is the one-way mirror. When a scene cue says
  [shot:insert x] the director already falls back gracefully, so an
  insert marker is only worth authoring where the object carries
  story weight.

### 2026-08-04 · coverage rotation + the roads get real setups

- **A locale used 37 times through one photograph is not directed.**
  The usage/coverage table (scene bg refs vs presets) found
  louisiana_road at 37 uses / 1 angle and cabin_road at 36 / 1 —
  73 appearances from two frames. Track this ratio; it is the
  production number that matters.
- **Coverage rotation**: when a locale authors shot_establish_b/_c
  (…_e) markers, VnDirector picks ONE per chapter (hash of the
  scene id set by GameEngine._load_scene). A chapter holds its
  angle; across a volume the same road is seen from different
  setups. Zero scene-JSON edits — locales opt in by carrying
  markers. Variant 0 is always the default view (authored
  shot_establish, else the preset vantage): alternates extend the
  deck, never evict the original.
- **Compute framings from the builder's coordinates, not by eye.**
  Camera positions/targets in blender frame; yaw = atan2(-dx, dy),
  pitch = atan2(dz, ground distance); blender→godot origin is
  (x, z, -y). (CORRECTION 2026-08-08: this pass serialized the basis
  column-major; tscn is ROW-major — see the lesson above. The
  framings' intent was right; the serialization was transposed.)
- **The setups are drafts until screenshotted.** Eight markers
  authored blind from geometry (verge, long-lens approach, sedan
  insert, swamp wide; the bend reverse, creekside, mile-marker and
  creek-stone inserts). The framing MATH is verified; the framing
  TASTE needs the Deck.



### 2026-07-22 · choice plates · the turning points get the register

- **Eight choices across vols 5-7 — each one a chapter-grade moment
  that looked like a debug menu** (stock 13px buttons at the top of a
  near-opaque 70%x80% slab). Rebuilt ChoiceMenu in the plate register:
  translucent scrim (the scene stays visible, dimmed, alpha capped
  0.78), centered column with rule-diamond-rule ornaments, IM Fell
  italic 22 prompt, centered chrome-less option lines (StyleBoxEmpty at
  rest, thin gold underline + gold text on hover/focus), skill checks
  as "· logic 3 ·" annotations. Font floor for options raised to 19
  while keeping each volume's skin font. Hover tick + select SFX from
  the shared bank. Public API (setup/present/visible), pad focus,
  number keys, staggered entrance all preserved.
- **Options are TEXT, the way the dialogue is.** The chrome-less
  July-12 philosophy extends to choices: rest state is pure type;
  interaction state is an underline, not a box.

### 2026-07-22 · the PRODUCER · departments on one clock

User: the project has a director module; it needs a producer to bring
the departments together and get the work in sync. Built
`scripts/vn/VnProducer.gd`, owned by GameEngine beside the VnDirector.

- **Director stages shots; producer runs the clock.** Three desyncs
  existed the moment scene fades were added: the first line typed away
  UNDER the chapter card (typewriter moment spent before the curtain
  was up), BGM hard-cut while the picture faded, and the camera
  released (snap) while the old scene was still visible.
- **The curtain gate.** `_load_scene` dispatches its first node through
  `producer.when_curtain_up()`. Across a real transition the node
  waits; mid-story jumps (choice targets, gotos) never hold the curtain
  and pass straight through. The veil's own lifecycle holds/raises the
  curtain — no second state machine.
- **Audio rides existing machinery.** scene_out_begin = AudioMgr.duck()
  (music dips with the 0.3s fade); scene_out_black = stop_scene_bgm +
  director release at full black; reveal_begin = unduck (the NEW
  scene's bed, requested under duck while the veil was up, rises with
  the light). The chapter plate sits in hush; music and the first line
  arrive together as it clears. No new audio paths.
- **The settle beat.** curtain_up waits 0.25s before flushing the held
  node — the establishing shot lands as a picture before it becomes a
  page.
- **Ordering is what makes one duck flag safe.** Dialogue ducking and
  transition ducking share AudioMgr's single flag; the curtain gate
  guarantees no say-node can duck until after reveal_begin's unduck.
  Sequencing beats flags.
- LightController is CP-only (appears in zero VN locale scenes) — the
  producer deliberately does NOT bridge mood→lights; VN mood authority
  stays VnDirector→MoodCycler. Bridging would have driven nothing.
- Future departments hook the producer: painted art plates, portrait
  relighting on mood, per-scene ambience choreography.

### 2026-07-27 · Deck playtest batch · five live bugs from one chapter

- **Speaker-blip ≠ speaker-pop.** show_narrate deliberately clears
  `_last_speaker` so the visual name-pop re-fires after narration —
  but the SFX tick was keyed on the same variable, so alternating
  narration/dialogue beeped constantly ("hearing a beeping through
  ch0"). Sound now gates on `_last_named_speaker` (survives
  narration): the tick fires only on genuine character→character
  handoff. When one variable serves a visual and an audio behavior,
  split it the moment their reset rules differ.
- **Panel cards must live UNDER the dialogue z.** The `[panel:]`
  image band (was z 101, rows 40–480) sat over the text zone; prose
  is the product — art yields. Now capped 700×300 in a 36–370 band
  at z 99 with a 0.25s fade-in.
- **Never mirror composition portraits.** Facing flip (`flip_x`
  meta) mirrored THE DEMON's ASCII art — baked banner text rendered
  backwards. Gate at the single read site in CharLayer._process:
  `kind == "composition"` → flip 1.0. Compositions bake TEXT; text
  has a correct orientation, facing doesn't.
- **`as Object` on a freed instance IS the error.** The ch2→3 crash:
  `_bust_blinkers[i] as Control` threw "Trying to cast a freed
  object" BEFORE the `is_instance_valid` guard on the next line
  could run. Validity-check the raw Variant first, cast second —
  now applied to the blinker list AND the slot table in _process.
- **A shot directive is a prop contract.** `[shot:insert phone]`
  fired in the diner for two ch0 scenes but Frasier's phone mesh
  existed only in the cathedral build (ch1). The insert marker was
  even aimed at empty formica. When authoring `[shot:insert X]`,
  grep the locale's build_*.py for X before shipping the line. The
  diner phone now sits exactly where the existing marker's
  center-ray meets the counter (ray-trace the marker: pos, pitch,
  yaw → surface point; place the prop there, zero marker edits).

### 2026-07-22 · presentation wave 1 · the book finally has chapter breaks

- **The scene JSON carried `title` for 177 scenes and nobody displayed
  it.** GameEngine now presents a ChapterCard (InterludePanel register:
  ornaments, Cinzel kicker VOLUME N · CHAPTER X, IM Fell title) at every
  (vol, chapter) boundary — 71 boundaries across vols 5-7 — plus on
  fresh session start. Data that ships unread is a presentation bug.
- **Every scene change now breathes.** A fade veil (z UI+40) carries
  scene→scene: 0.3s to black, build the next scene under it, then the
  chapter plate or a 0.45s reveal. `_transition_lock` gates
  GameEngine._input so a click mid-fade cannot advance the story
  underneath; the ChapterCard handles its own advance and releases the
  lock in its dismiss callback. Same-frame hard cuts are gone.
- **The typewriter now reads with the prose.** Punctuation-aware pacing
  in DialogueBox._process: sentence stops hold 7x the char delay,
  em-dash/ellipsis 5x, colon/semicolon 4x, comma 2.6x — all scaled off
  the user's char-delay setting, so faster settings stay faster.
- **Tween against the writer, not the property.** CharLayer._process
  writes wrapper.position absolutely every frame (idle bob), so the new
  portrait entrance rise rides an `entrance_y` meta the bob math
  composes in — never tween a property something else owns per-frame.
- **CgPanel fades (0.5s in with a 1.03→1.0 settle-zoom, 0.35s out) and
  DEBUG_BG_OVERLAY is finally false.** A debug label had been shipping
  in the corner of every scene.
- Deck-verify: card typography, fade durations, pacing multipliers, the
  entrance rise amount — all feel numbers.


### 2026-07-13 · v5 · game-wide render fixes + the ~220-scene direction sweep

A long playtest surfaced three CLASSES of bug that read as "black"
or "flat/unreal," plus a full mood-direction sweep of vol5/6/7.

- **"Black scene" almost always = the mood, not a missing GLB.**
  MoodCycler booted to `current_index` = the edges-only `linework`
  mood; any scene without an explicit `[mood:]` AND a locale with an
  empty `default_style_pack` (69 of 80 shipped empty) rendered as a
  wireframe on black. Fix: boot to a CLEAN grade (`raw`). Rule: a
  no-direction scene must fall back to a color grade, never an
  edge/ascii mood. (MoodCycler.gd `_ready`.)
- **"Flat / no geometry / just a fill + character" = the camera is
  aimed OUT of the room.** 48 CAMERA_PRESETS shipped a placeholder
  camera — origin `(0, 2.3, +0.5)` (or a `-0.5` variant) yawed 180°,
  i.e. standing at/behind the door wall facing +Z into the void,
  while interior rooms sit at NEGATIVE godot Z (door/S wall at z=0,
  room extends to z=−ROOM_D). The character (a Portrait3D overlay)
  still drew, so it read as "flat fill + person." Fix + method for a
  real establishing camera from geometry:
  - Read the build script for ROOM_W/ROOM_D + the hero prop; convert
    blender→godot `(bx, bz, −by)`.
  - Camera INSIDE the room, eye height (godot y 1.55–1.8; ~2.0 for
    big retail/venue rooms), aimed on a 3/4 DIAGONAL at the hero prop
    (bar/bed/desk/counter) — head-on wall stares read flat.
  - `yaw = atan2(cam_x − target_x, cam_z − target_z)` (Godot −Z
    forward). VERIFY the sign against a known-good preset
    (roberts_kitchen, new_orleans_bar) before trusting it.
  - Pitch −0.04…−0.12, fov 50–66. Keep the camera WITHIN the walls.
  - Outdoor sets (porches, road, field, the +Z riverboat/cathedral)
    do NOT follow the −Z convention — read each one's real geometry
    sign; some legitimately keep yaw 180 (riverboat helm faces the
    +Z desk; louisiana_road looks down the N–S road).
- **"Wireframe nightmare" = a neon-1.0 mood used as direction.** Any
  MOOD with `neon` 1.0 runs the neon-edge shader (outlines every
  edge). `noir`, `bar_pendant_amber`, `chillwave`, `lithograph`,
  `ink_*`, `sunset`, `blueprint*`, `cel_shaded`, `linework*`,
  `substrate*`, `ice`, `debug_purple`, `anime_motion`, and ascii
  moods are ALL banned as scene direction — AND so is any STYLE_PACK
  that resolves to one (`bungalow_late`→`noir` bit us). Author only
  from the neon-0/ascii-0 grade set (raw, day_bright, morning_bright,
  dawn_warm, dusk, night, lunch, studio, macro_haze, dream_blur,
  candlelight_low, kitchen_practical, fluorescent_corridor,
  tv_glow_blue, silent_film_*, liminal_interior, rain_interior, and
  the rebuilt subtle arcana/arcana_cool/arcana_warm). Mechanical
  check: `[mood:X]` is safe iff MOODS[X] (or its pack's mood) has
  neon<1 AND ascii<0.5. Full list in `_SHADER_VISUALS_PLAYBOOK.md`.
- **Warm-dim beats: use `candlelight_low` (a MOOD), never
  `memory_warm` / `bar_pendant_amber` (STYLE_PACKs).** The packs swap
  in the `candlelight` LIGHTING preset (dir_mult 0.15) which BLACKS
  OUT dim sets. `candlelight_low` only grades colour — no Light3D
  change, no black.
- **Direction discipline the sweep converged on:** one established
  base mood on the FIRST text node; only add another `[mood:]` on a
  line that ALSO cuts the camera (`[shot:insert]`/`[shot:closeup]`)
  AND when the grade genuinely changes; plain narration carries NO
  mood (it inherits). ~2–6 mood tokens per chapter, not one per
  click. Shared locales must differ by time-of-day/beat (e.g. one
  apartment across 9 scenes; graustark across Hermit/Judgement/
  World/Star). Text time-stamps ("3:47 AM", "Sunday morning") are
  the truth for the grade, not the parent guess.

### 2026-07-11 · v0 · grammar + director core

- **A comic, not a film.** The user's brief: "almost a 3D comic
  moving between close-ups, establishing shots, insert shots and
  prop/info/panels." Cuts are the default; that single decision
  removes all camera-path authoring and makes every shot an
  editor-placed Marker3D.
- **Framing lives in the editor, not in code.** Markers carry the
  whole shot. Code only cuts, drifts, letterboxes, restores.

### 2026-07-11 · v1 · director built + Kwik Stop pilot

- **Markers in .tscn are just position + rotation lines.** No
  hand-computed Transform3D basis: `position = Vector3(...)` and
  `rotation = Vector3(pitch, yaw, 0)` are valid tscn properties
  and read like a shot list. Yaw cheat-sheet for locale space
  (Blender→Godot: gx=bx, gy=bz, gz=-by): look WEST(-X) = +π/2,
  EAST(+X) = -π/2, SOUTH(+Z, toward the y=0 wall) = π.
- **Establish-with-no-marker must restore the preset.** The
  Background3D CAMERA_PRESETS vantage IS the authored wide; the
  director treats it as the implicit shot_establish so directing
  can roll out scene-by-scene with zero locale edits.
- **Deferred locale loads race the first directive.** GameEngine
  defers `load_location`; a `[shot:]` on the scene's first line
  lands before the locale instance exists. The director parks the
  spec and retries per-frame (60-frame cap) instead of dropping it.
- **The letterbox must not be a CanvasLayer.** F4's clean-screen
  sweep hides every CanvasLayer; the comic crop is part of the
  PICTURE, not HUD. Plain ColorRects in GameEngine's control tree
  at z 95 (under portraits/dialog at z 100).
- **Hold the closeup across the exchange.** In the pilot scene the
  camera cuts to Jen once at "Diego come by today?" and stays
  through Sam's answers — the no-ping-pong rule immediately felt
  right in markup; re-cutting per speaker read as noise.

### 2026-07-11 · v2 · full-catalog sweep — every 3d scene directed

- **The whole VN is directed.** All 194 scenes with 3D backgrounds
  across vols 5-7 carry direction: vol5 26 scenes/264 shots, vol6
  96/714, vol7 72/554 — 1532 directives total, ~2.5 drifts per
  scene (the dread budget held). Scenes with 2D backgrounds have
  no camera and were correctly left untouched.
- **Marker-free punch-in unlocked the sweep.** closeup/insert with
  no authored Marker3D now cut to a punch derived from the locale's
  CAMERA_PRESETS vantage (forward 1.2/1.8m, FOV 44/34, always from
  the PRESET so repeats can't compound into a wall). Direction no
  longer waits on hand-placed markers; markers refine framing when
  a locale earns them. Only kwik_stop has real markers so far.
- **Direct from a condensed dump, tag by node index.** Workflow
  that held for ~135 hand-directed scenes: `peek.py` prints
  `idx type speaker first-120-chars` per text node plus bg/choice
  markers; decide the shot list from that; `tag.py file idx:spec`
  prefixes the text and validates node type + grammar + JSON in
  one shot. Index-tagging beats prefix-matching (no quoting bugs);
  the validator caught the one mis-aimed tag (a `show` node) before
  it could write.
- **Montage pages break the density budget on purpose.** Ensemble
  scenes (vol5 Judgement, vol6 prelude/ch23) read as one panel per
  character — 13-16 cuts is correct there where 12 would be too
  many in a two-hander. The budget is per-beat, not per-node-count.
- **Repeat-insert = motif.** Cutting back to the same prop id
  (Devil's microwave reflection, Strength's bar TV, the bowls at
  the cabin) builds a refrain across a scene; the second cut lands
  differently because the first one taught the reader the image.

### 2026-07-11 · v3 · set audit + cast staging + per-scene looks (ch0 pilot)

- **The user's brief escalated from framing to set-truth.** "Understand
  what is in the scene, where objects go, where character models go,
  what props need to be there." The answer is an AUDIT loop per
  chapter: read the prose → read the locale build script (the GLB's
  source of truth — locale GLBs aren't in the repo) → place cast
  anchors + shot markers at REAL prop coordinates → retag the scene.
- **build_*.py is the coordinate oracle.** The Fool's diner props all
  had authored Blender coords (booth 6 by=+3.75, register x=-3.6,
  clock north wall, jukebox (-10.5,+5), mug (-1.15,-3.68)); markers
  are placed by conversion (gz=-by), not by eyeballing renders.
- **Five of seven hero GLBs were lying on their backs.** The character
  uploads are Z-up exports; only john/frasier are Y-up. Nobody noticed
  because they'd only ever been used by Portrait3D. CAST_MODEL_ALIGN
  fixes them at stage time. Rule: bbox-audit any new GLB before
  trusting it (python struct read of the glb JSON chunk, 10 lines).
- **The establish should contain the cast.** The diner wide moved from
  John's POV (behind the counter) to a third-person NE dining-floor
  vantage once [stage:] existed — a comic panel SHOWS the protagonist
  in the room. POV vantages belong to the gauntlet's FP mode, not the
  VN's establish.
- **[mood:] rides the existing STYLE_PACKS.** Lighting + post-process
  per scene is one directive (apply_style_or_mood); no new lighting
  machinery. Locale default_style_pack still sets the opening look;
  [mood:] is for mid-chapter shifts (dawn arriving, a threat beat).
- **Floor heights come from the build script, never a vantage table.**
  The riverboat's decks are 0.00/2.50/5.10 (RiverboatGauntletHost
  constants match the builder) but the gauntlet's standalone vantage
  table carried stale 3.2/0.0/-2.8 — every camera keyed to it sat in
  the inter-deck void (Dante's black chapter). Both fixed; when a
  chapter renders black, suspect (1) requires_glb path vs builder
  OUTPUT_DIR, (2) camera below/inside the floor slab.
- **A scene's establish must be in the chapter's ROOM, not just its
  building.** The Empress works Friday-night service in the formal
  annex + vestibule; the diner_interior preset frames the lunch
  counter. One building, two presets (diner_interior /
  dambrosios_formal) — same .tscn, different camera + different
  cast anchors.

### 2026-07-11 · v4 · first staged playtest — five lessons from live frames

- **survey.py is the layout oracle.** Scratchpad tool: runs any
  build_*.py with a stubbed bpy, captures every mesh AABB, prints a
  top-down occupancy map (--map --crop) or spatial queries (--box,
  --find). It caught: the bungalow establish staring into the
  storage closet's south wall from 0.5m, cast_living placing Elicia
  INSIDE the closet, two shot markers embedded in walls, and the
  cathedral chair semicircle. Never place a marker without a survey.
- **Release an authored insert within ~2 nodes.** The marker-free
  punch-ins were mild; real markers pitch down 0.5 rad at a counter
  top, and holding one through a dialogue exchange reads as "why is
  this focused down here." Rule: after [shot:insert x], the next
  beat that isn't ABOUT the prop gets [shot:establish] (or a
  closeup).
- **Edge-only moods render an establish as black.** linework /
  substrate_press show silhouette edges only — great as strata,
  fatal as a chapter's default look. VN chapters get legible packs:
  warehouse_nave + bungalow_packing (naturalistic mood + the
  practical rig). The diner's raw+midnight is the reference recipe.
- **Portraits flank when the bg is 3D.** The center slot (x 490,
  300px wide) parks a card exactly over what the camera is framing.
  CharLayer.bg_is_3d (set by GameEngine on every bg change) remaps
  "center" to a free corner slot; flat 2D bgs keep center.
- **Stale GLBs lie.** The tscn markers ship by git pull; the GLBs
  do NOT (Deck-built artifacts). A shot aimed with current
  build-script coordinates against a months-old GLB frames the OLD
  building (the diner "wall" report). After any marker pass tell
  the user which builders to re-run.

## TEMPLATE — new lesson entry

```
### YYYY-MM-DD · short session title

- **Punchy lesson, present tense.** Two-to-four sentences.
- **Next lesson.** Same shape.
```

### 2026-07-28 · reading furniture · the backlog + photo mode

- **A VN without a backlog loses lines forever.** DialogueBox now
  records every say/think/narrate (cap 300); H or wheel-up opens
  the overlay — speaker names in their portrait accents, thoughts
  italicized, opened at the freshest line, wheel-down past the
  bottom rolls back to the story. The overlay joins
  `vn_input_blocker` so reading history can never advance the
  story underneath.
- **Photo mode is F6, and it is deliberately NOT F4.** F4 hides
  HUD; F6 composes: dialogue + HUD + choices off, cinematic bars
  on, cursor gone, and every other input swallowed so framing a
  shot can't advance the page. The bars intentionally bypass the
  F4 sweep — in photo mode the bars ARE the picture.
- Verified-non-gaps this pass: portrait exits already fade with an
  ASCII ghost; letterbox grammar is already correct (bars on tight
  shots, clear on establishes) — the roadmap's "letterbox on
  establish~" idea is superseded by that reading.

### 2026-07-28 · the chapter card gets a sheet · endpaper plates

- **The most-seen page deserved more than a black field.** 71
  chapter boundaries across vols 5-7 rendered ornaments + type on
  flat near-black. Now each volume has a dyed ENDPAPER behind the
  type — laid paper (wire lines + chain lines), a marbler's comb
  raked in the volume's own ink, sparse foxing, and a deckle
  vignette. Vol 5 warm brass, vol 6 slate blue, vol 7 deep green;
  three variants per volume keyed off chapter number so
  consecutive cards never repeat the sheet.
- **Procedural texture beats painted illustration for backdrops
  behind type.** Same lesson as the gauntlet floor plates: art
  with no depicted SUBJECT can't misalign, can't date, and can't
  fight the words. Reserve the painted-art gate for art that is
  the subject.
- **Two render bugs worth remembering:** ellipse OUTLINES at
  increasing alpha draw RINGS, not a radial gradient (build the
  falloff as a real distance ramp at low res and scale it up);
  and per-channel color jitter reads as rainbow noise — jitter
  LUMINANCE with one shared delta so a material stays one
  substance.
- The plate fades in over 1.0s against the type's 0.7s so the page
  reads as laid down, not switched on.

### 2026-07-28 · the dialogue box is SILENT on advance (hard rule)

- **A per-line tick cannot be saved by gating it.** A speaker-change
  blip was added, then gated to genuine character→character handoffs
  after the first "beeping as I progress" report — and was reported
  again as "super annoying." The reason is structural: in
  back-and-forth dialogue EVERY line IS a speaker change, so any
  handoff-gated sound fires on nearly every advance. There is no
  gate that fixes this; the sound itself was the mistake.
- **The handoff is carried visually and that is enough** — the
  nameplate pops from 1.14 scale and the accent underline wipes in
  from the left. That was always the design intent; the tick was
  redundant reinforcement.
- The rule now lives as a comment block at the top of DialogueBox so
  a later pass doesn't helpfully re-add it. Sound in the VN belongs
  to BEATS (authored, a few per chapter) and to scene `sfx` nodes —
  never to the act of turning a page.
