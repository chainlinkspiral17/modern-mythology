# SLOWSTOCK AUTHORING PLAYBOOK

Patterns for authoring the in-fiction retro slowsticks — Estuary 3
(1993), Manager Mode (Estuary 3 alt), Pirate Summer (1988), Fey
Faire (1990), Earthman Chronicles (1985). All of them ship as text-
forward Control scenes owned by a single Host controller that
routes between child scenes on signal.

Read this before adding a fifth slowstick, before scaffolding a
new host controller, or before writing a beat-sequence chapter
scene.

## Core rules

### The Host / child-scene contract

Every slowstick has ONE host controller (e.g. `FeyFaireHost.gd`)
that owns:
- title screen (built inline as `_title_root: Node`)
- save file at `user://<name>.save.json`
- one `_run_state: Dictionary` that all child scenes share
- one `_child_scene: Node` reference · always one scene at a time
- `_clear_current_scene()` free-and-null before every open

Every child scene:
- extends `Control`, sets `PRESET_FULL_RECT` in `_ready()`
- joins `add_to_group("ui")` so F4 hides it
- accepts a `boot(state: Dictionary)` method called AFTER
  `add_child()` — receives the run_state (or a slice of it)
- emits `quit_to_shelf` (goes back to shelf) OR `quit` (goes back
  one level to Gate/Host) — never both
- emits any scene-specific signal (`negotiate_with_fey`,
  `enter_big_top`, `chapter_complete`, `finished`) that the host
  translates into a routing decision

The host uses `child_scene.has_signal(name)` / `has_method("boot")`
to defensively connect only what exists. This lets a child stub in
a partial signal-set during scaffolding without breaking the host.

### Signals for the boot layer

`SlowstockBoot.gd` calls into every host uniformly, so every host
MUST provide:
- `signal quit_to_shelf`
- `signal finished(canon_vars: Dictionary, lore_tokens: Array)`
- `func start_new_run(manager_mode: bool = false) -> void`

Match this exactly. `manager_mode` is ignored by slowsticks that
don't have an alt mode; keep the parameter.

### `_run_state` shape

Every host initializes `_run_state` twice — once at the field
declaration site (default values on ready if no save) and once at
the top of `start_new_run()` (reset for a fresh run). Keep them in
sync. The dictionary must be JSON-serializable — no `Vector2` or
`Color` values, no scene refs, no Callables.

Keys grow over time. When you add a new mechanic that persists,
add it to BOTH initializers and add a default read in every child
that reads it (`_run_state.get("new_key", default_value)`).

### `_save_state()` writes JSON with indent

```gdscript
f.store_string(JSON.stringify(_run_state, "  "))
```

The two-space indent matters. It makes save files readable during
debugging, which is required for any content that wants to be
inspected during authoring.

### The beat-sequence pattern

For story chapters (Earthman Ch1-6, Fey Faire Big Top, Chapter 5
"Academy" reveal), use a hardcoded `var _beats: Array = [...]` of
dictionaries with `speaker`, `text`, optional `type: "choice"`
with `choices` array. Then:

- `_render_current_beat()` reads `_beats[_beat_idx]` and calls
  `_render_choices()` or `_render_advance_button()`
- `_on_choice_selected(choice)` merges `sets` deltas into
  `_run_state` and advances
- Space / Enter / KP_Enter advance non-choice beats via `_input`

The `_delta` suffix convention in `sets`: any key ending in
`_delta` is applied as an integer add against the base key. This
handles disposition shifts, court alignment, HP/SP changes with a
single line each in JSON-shaped GDScript literals.

Beat scenes should stay in one file each — no fancy inheritance.
Duplicating the frame-drawing code across chapters is fine; a
chapter's tone comes from its palette + wallpaper motifs, and
those are the top ~40 lines of each chapter script.

### The ending scene pattern

Both Earthman Ch6 and Fey Faire's endings scene follow the same
three-phase structure:

1. **gather phase** · 2-3 beats set the tone before choices
2. **choice phase** · walk-out / consent gate · buttons appear
   only if state qualifies for that ending
3. **ending phase** · beat-sequence playback of the chosen ending

`_pick_ending()` (or `_resolve_ending_from_state()`) inspects
run state and returns an ending id. Priority ordering matters —
put the TRUE ending first, then rare gated endings, then default
court endings. The final fallback should never return null; pick
a sensible default so a broken state doesn't hang the run.

### Variable substitution against the questionnaire

Any ending script that references `$PLAYER_NAME`, `$LOST_PERSON`,
`$CITY`, `$FAVORITE_SONG` should route through a single
`_substitute(text)` helper that reads `_run_state.questionnaire`
and does `.replace()` calls. Add new variables to that helper as
needed, not inline in each beat.

### Data-driven scenes for combat / negotiation

Where the same scene structure is repeated across many entities
(feys, campers, workings), the scene should read a JSON catalog
and pick the entry by id passed via `boot({"id": ...})`. Never
switch-statement on ids inside a scene; that's a smell that the
data model isn't right yet.

Fey Faire's `FeyFaireNegotiation` and `FeyFaireCombat` both do
this well — the fey's stats, skills, court, weakness, and
manifestation all come from `feys.json` at boot time.

### F4 must sweep every new HUD

Every new HUD Control MUST either:
- `add_to_group("ui")` — F4 hides all group-`ui` nodes, OR
- live inside a CanvasLayer — F4 sweeps CanvasLayers by default

If a child scene forgets this, the fix is one line in `_ready()`
(the `add_to_group("ui")` call). Add it at scaffold time; don't
wait for someone to press F4 and see leftover UI.

### Escape key behavior

Every scene handles `KEY_ESCAPE` in `_input()` and calls
`get_viewport().set_input_as_handled()`. The host's own `_input`
handler ONLY escapes when the title screen is showing (child
scenes handle their own escape). This prevents double-escape
races and keeps back-navigation predictable.

### Save-then-CONTINUE routing

The host's `_on_continue_pressed()` routes based on saved
`chapter` (Earthman) or `night` (Pirate Summer, Fey Faire) or
`act` (Estuary 3). Match the enum to the game's own progression
unit. If a slowstick has multiple progression axes, pick one
canonical routing axis and store it in `_run_state` explicitly at
each state transition.

## Recent lessons

### 2026-07-09 · four slowsticks end-to-end · what the fourth build taught us

Landed Fey Faire (Gate → Questionnaire → Negotiation → Trailer →
Midway → Big Top → Combat → Endings, 7 endings) and Earthman
Chronicles (all 6 chapters + 6 endings). Both fully playable
start-to-finish. The pattern above is now stable across four
slowsticks.

Lessons:

- **The uniform host signal set (`quit_to_shelf` + `finished`) is
  worth its weight in gold.** SlowstockBoot doesn't need to know
  anything about Fey Faire's specific state — it treats every
  slowstick as a black box that eventually emits `finished` with
  a canon_vars dict + lore_tokens array. New slowstick = drop-in.
  The cost of enforcing this uniformly across four hosts is under
  10 lines of duplicated signal-declaration each; the payoff is
  that the boot layer never grows a switch statement.

- **Beat arrays beat state machines for narrative scenes.** Every
  chapter scene is a flat `_beats: Array` of dicts. The temptation
  to build a proper node-graph story engine was real, but flat
  arrays with `_on_choice_selected` merging `sets` deltas covered
  every case across ~40 chapter scenes. The `_delta` suffix
  convention (any `foo_delta` in `sets` adds to `foo`) collapsed
  ~200 potential switch cases into three lines of runtime code.

- **Ending selection is a priority ladder, not a table lookup.**
  Both Earthman Ch6 and Fey Faire endings use if-elif ladders
  with the TRUE ending first, gated endings next, and defaults
  last. This is easier to read (and easier to reason about
  correctness for) than a scoring table, because the gates ARE
  the state facts you already track — "IX refused AND all six
  corrections AND Rocha recruited AND Sara LIKED+" reads as
  literal English in a single if.

- **Endings scripts belong in the scene, not in endings.json.**
  We authored `endings.json` files first (Earthman, Fey Faire)
  with full script text expecting to load and interpret them at
  runtime. In practice the beats got copied inline into the
  ending scene as `const ENDINGS: Dictionary` because the scene
  wanted to control tint, per-beat animation, and choice injection
  in ways the flat JSON didn't express. The JSON is now the
  design-time document; the scene is the runtime source of truth.
  Keep both in sync manually — this is fine, they don't diverge
  often.

- **`_run_state["_route_to_trailer"]` and friends: transient
  routing flags are load-bearing.** Some transitions need one bit
  of "which scene do we go back to." Fey Faire's midway sets
  `_run_state["_route_to_trailer"] = true` before emitting `quit`;
  host reads it, opens the trailer, and `.erase()`s the flag.
  This is uglier than a proper "return address" parameter but it
  survives save/reload and is one line at each site. Don't over-
  engineer this until you have three or more return-target flags
  simultaneously.

- **Chapter status lines on the title screen are the fastest
  progress signal.** After each chapter lands, update the title
  screen's `status_label.text` to say what's playable. This is a
  30-second edit that lets the player (and the next session's
  claude) know at a glance where the game is. "Chapters 1-5
  playable · Chapter 6 pending" → "all 6 chapters playable · 6
  endings authored".

- **Palette shifts per chapter carry more than dialogue does.**
  Earthman's palette walks from cool-purple (Pasadena) → dust-
  orange (Parsa surface) → warm-cream (Talikan) → basalt-black
  (Mines) → deep-indigo-with-gold-star-motif (Academy) → dark-
  cortex-purple (Finale). Reading the source code with the
  palette blocks visible tells you the emotional arc even before
  you read the beats. Chapter tone is 40% palette / 20%
  wallpaper motif / 40% dialogue.

### 2026-07-09 · the audit pass · readers vs writers

Ran a full feature/wiring audit across both new slowsticks after
they reached end-to-end playable. Five real bugs, all one shape.

- **Audit every gate's readers against its writers.** Every bug the
  audit found was a state key that something READ (ending triggers,
  Codex tabs, THREATEN unlocks) but nothing WROTE — or wrote under a
  different name. `titania_disposition` gated an ending nothing fed;
  `fey_court_<id>` was counted but never cached; the mirror granted
  true name `kelpie_water_horse` while checks looked for `kelpie`;
  the Observatory granted `correction_academy_broadcast`, an id not
  in corrections.json. Grep each gate key for its writer BEFORE
  declaring an ending reachable.
- **Watch for grant-during-the-ending chicken-and-egg gates.** THE
  CORRECTION required 6 corrections, but the 6th was designed to be
  granted BY the ending. Gate on the findable set; grant the
  capstone during playback.
- **Chapter-end "next chapter pending" texts rot the moment the
  next chapter lands.** They're player-facing, and auto-advance
  makes them lies. Replace endcaps with in-fiction transitions at
  the time the next chapter ships, not later.
- **A currency needs three legs or it isn't one: init, income,
  balance check.** Shenin had zero of three — costs existed with no
  wallet. If a design doc mentions "money you earned," the earn
  mechanic must exist before any spend gate ships.

### 2026-07-09 · the systems arc · six sticks, one library

Sam's Summer Shifts became the sixth playable slowstick, the
console inside Pirate Summer boots the real games, and every
authored-but-unconsumed data file got its consumer (workings,
quotes, promises, the manuscript). Lessons:

- **When the data isn't machine-checkable, make the honor system
  the mechanic.** Fey Faire's promises are life-promises ("plant a
  tree") · inventory-matching was impossible and wrong. The fix:
  Ondine reads the ledger back on Night 6 and ASKS. The game takes
  your word, on purpose, on theme. Don't fight the data's nature;
  design around what it actually is.
- **NG+ is a lifetime block the reset preserves.** `start_new_run`
  reads the keys that should survive (endings_seen) BEFORE building
  the fresh dict and seeds them back in. One pattern, two games
  (Fey Faire, Sam's Summer Shifts). Anything not in the lifetime
  block is per-run by definition · no ambiguity.
- **Overlay combat preserves beat position.** Chapter beat-scenes
  don't save mid-chapter, so combat launched by the HOST would
  reset the chapter. Instead the chapter instantiates the combat
  scene as its own child, pauses on it, and resumes `_on_advance()`
  from `combat_complete`. The chapter never knows it stopped.
- **The uniform host contract paid out twice more.** Nesting Fey
  Faire inside Pirate Summer's console was ~50 lines because
  quit_to_shelf/finished are universal; Sam's Summer Shifts slotted
  into SlowstockBoot with one const + one branch + one opener.
- **A completed progression ladder makes a free moveset.** Earthman
  combat lets each finished Working be cast once per fight · the
  nine-rung ritual ladder doubles as the special-move list with
  zero new progression design. Look for systems the player already
  climbed before inventing new ones.
- **Sub-menus need the same cleanup discipline as scenes.** The
  combat action row overlapped its own WORKING/PARTY submenus until
  both were named into the same "BottomMenu" slot. Anything that
  swaps in-place needs a single named anchor to clear.

### 2026-07-10 · Estuary 1 · the smallest full stick

- **A one-screen game wants `_draw`, not a scene graph.** Estuary
  1's whole picture (tide bands, reeds, gate, lever, shimmer,
  air-holes) is one Control `_draw()` plus two real children (the
  notebook Label and the advance Button).  Deterministic scatter
  comes from an integer hash, never `randf()` in `_draw` — a
  redraw must not re-roll the world.
- **Roll randomness once, save it.** The twelve tide-luck values
  are rolled at boot and stored in `_run_state["luck"]`, so a
  continued save replays the same weather.  Any per-run randomness
  belongs in the save, not in the frame.
- **Single-track AudioMgr + stem-mixed score = render the
  combinations.** Ostrom's drone-plus-voices score became 8
  pre-rendered WAVs (`mix_d[f][s][h]`); the loop swaps files
  weekly and the crossfade sells it.  Naming the files by stem
  set keeps the pick logic one string-append per voice.
- **The shelf's BOOT button keys off `manifest.has("acts")`.**
  SSS shipped without an `acts` key and silently showed PEEK
  instead of BOOT.  Every playable manifest needs `acts`, even a
  one-act stick — added to both manifests this session.
- **Emit AND consume in the same commit.** `estuary_1_patience_a`
  ships with its Jules line (E3 Act 2) and `estuary_1_week_13_seen`
  with its grace beat (E3 Act 4), per the readers-vs-writers
  audit lesson: a token nobody reads is a bug deferred.

## TEMPLATE — new lesson entry

```
### YYYY-MM-DD · short session title

- **Punchy lesson, present tense.** Two-to-four sentences.
- **Next lesson.** Same shape.
```
