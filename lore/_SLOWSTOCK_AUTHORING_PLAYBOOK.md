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

### 2026-07-22 · SALMONBERRY · an RPG-of-a-life on the Estuary-1 loop

Stick #21 — a part-RPG part-adventure about a year in a 1960s coastal
Oregon town, the studio's biggest genre. Built v1 as the SMALLEST
complete version (the Estuary-1 discipline), not the full overworld.

- **An RPG's growth doesn't need combat — it needs a verb and a
  ledger.** Six aptitudes raised by DOING (hands/sea/word/heart/wild/
  grit), a bond web, and a journal, all moved by one data-driven
  "spend the month" choice. It's Estuary 1's one-lever loop grown two
  more axes (bonds + collection), and it reads as an RPG because the
  numbers go up and the town's response changes. Ship the loop first;
  the walkable town is a wave, not the MVP.
- **Data-driven activities make the town a JSON file.** activities.json
  (season gate + require + apts/bond/money/journal deltas + outcome)
  and npcs.json (bond_lines that surface at thresholds 2/4/6) mean new
  content is data, never code — the same lesson as Fey Faire's feys and
  the gauntlet visitors. The register resolves from the ledger (the
  Tideline pattern), no win flag.
- **Real history as tentpoles, handled with the Sweetgum restraint.**
  The year is framed by two events everyone from that coast remembers
  (a November afternoon, a Good Friday night); both are felt through
  the town, never staged. The March tsunami is the one scripted month —
  a climactic choice gated by what you built (SEA/bonds), so the RPG
  systems PAY OFF as a rescue. When a real tragedy anchors a stick,
  make it a consequence of the player's year, not a cutscene.
- **The meta-hook lives in provenance + the true ending, not the UI.**
  The grandmother's songs ARE the catalog's recurring melodies; the
  game is their origin. Said once (THE SONG ending, the manifest),
  never on the HUD. The deepest canon payoff is the quietest.

### 2026-07-22 · SPIDERDROPS 2 · a post-game sequel that inverts the verb

Stick #20, THE LONG WIND — the sequel to #19, built the next session.

- **A sequel is the host shape reused + one new physics mode + carry
  the ending in.** SpiderdropsTwoHost is Spiderdrops' host verbatim
  (title/run/ending-register/save); only the boot reads
  `OneironauticsTokens.canon("spiderdrops_result")` and
  `.has("spiderdrops_star")` to set starting silk and the true-ending
  gate. "Carry the ending as the opening" (the Year-Two rule) works
  across two different GENRES, not just two summers of the same one.
- **Invert the verb, don't escalate it.** Game 1 is defense (hold the
  web); the sequel is traversal (balloon on the wind). The hazard
  becomes the vehicle — the same gust system, re-signed from threat to
  tailwind. A sequel that's "the first game but harder" wastes the
  chance; a sequel that completes the first game's SENTENCE (nothing
  holds → so you move on) is worth building.
- **Post-game unlock = the Sweetgum gate.** `starts_unlocked` +
  `hidden_until_token: <prequel>_finished` in shelf_layout: the slot
  literally does not exist until you finish the first, then it is
  immediately bootable. Cleaner than a wave for "you can't own the
  sequel before the original."
- **One forgiving fail path beats many.** The glide's only loss is
  running out of silk (STILL FLYING — reframed as peace, not defeat);
  reaching all legs ARRIVES. All the tension lives in one resource
  (silk) vs one distance, per leg. A physics toy wants a single legible
  stake, not a punish grid.

### 2026-07-21 · SPIDERDROPS · a live physics stick on the same frame

Stick #19 (PDP Toys, 1993) — a real-time Verlet web sim, the first
action/physics stick. It slotted into the exact same host contract as
the text-forward sticks. Lessons:

- **A real-time stick is still host + one scene + data.** The web sim
  is one child (`SpiderdropsWeb`) emitting the uniform `quit` +
  scene-specific `run_over(result)`; the host title/ending/save is the
  Estuary-1 shape verbatim. New GENRE did not mean new frame — the
  boot contract carried an arcade toy as cleanly as it carries a beat
  scene. The one thing that earned new code was the renderer (the
  "core mechanic deserves the renderer" rule): a ~50-line Verlet loop
  (`_integrate` → N× `_solve_constraints` → `_snap_and_cull`) in
  `_physics_process`, all drawing in `_draw` (sky first, web, spider,
  rain), HUD as child Labels so the font floor + F4 still hold.
- **Draw the WORLD in `_draw`, keep only HUD as children.** A Control
  paints its own `_draw` BEFORE its children, so a child sky ColorRect
  would cover the web. Everything world-space goes in `_draw` in order;
  Labels (crisp font, floor 12) ride on top as children. Same split
  any live `_draw` stick will want.
- **One-path-per-input still bites in real time.** Movement polls the
  built-in `ui_*` actions each physics tick; PLUCK is `ui_accept`;
  BRACE is a held raw `KEY_SHIFT`; SPIN is raw `KEY_S`. Before picking
  a raw key, grep the `[input]` map — here only advance/menu_back/
  menu_select/skip are custom and WASD is unbound, so `KEY_S` is free.
  A raw key that collides with a movement action double-fires.
- **The MM twist can be structural, not a cameo.** The "standard game
  experience" is honest arcade physics; the twist is that the storm
  ALWAYS wins and the run grades the web's SHAPE (the Tideline-register
  pattern), and that an orb web stripped to its 8 spokes IS the Order's
  eight-pointed star — a THIRD publisher the star leaks into,
  uncommented. Emit `spiderdrops_star` now for a future Order consumer
  (readers-vs-writers: emit before the reader exists).
- **Tuning is Deck-work; ship reasonable starts and say so.** Break
  ratio, rain rate, gust strength, verb cooldowns, resource regen — all
  physics feel that can't be proofed in CI. Author sane constants,
  gdparse-clean, and flag the numbers for a Deck pass rather than
  claiming they're balanced.

### 2026-07-20 · slowstick depth pass · spine + de-domination + a second axis

- **The shelf is a system, cheaply.** The catalog already had a dense
  cross-stick token web but no COLLECTOR spine — nothing responded to
  how much of the whole shelf you had read. Fix rode existing state:
  `SlowstockBoot._fire_collector_milestones` crosses first/half/whole
  thresholds (counted over the 18 CORE sticks, remake excluded) and
  fires durable tokens the Almanac lights. Centralize the repeated
  `/root/GauntletState` → `canon_vars`/`slowsticks_finished` reads into
  `OneironauticsTokens.canon()/finished_sticks()/is_stick_finished()`
  once, refactor the copies onto it.
- **De-dominate by scaling the REWARD, not adding rebuffs.** Fey Faire
  OFFER was a universal solvent because every branch that succeeded
  granted the same disposition. Give each fey a single WANT (derived
  from data it already carries — favorite_play → RECITE, else court;
  curated-override hatch, empty by default) and scale disposition on
  the match (+3 delighted, +1 cool). OFFER is never a want, so gold
  stops being optimal. No new rebuffs = no soft-locks, no dead content;
  only warmth and flavor change. Surface a legible "tell" so it is a
  READ, not trial-and-error. Same derive+override shape as the gauntlet
  visitor look table.
- **A neglected stat needs a HARD-OVERRIDE ending to matter.** KSM
  tracked landlord but folded it into the single score, where cash
  outweighed it — so it gated nothing. Adding an `evicted` ending that
  OVERRIDES the score when landlord ≤ 1 makes it a real second axis:
  "win the score" and "keep the store" pull apart. Telegraph the danger
  band in the weekly report so the loss is warned, never a gotcha.
- **Promote one boss's good idea to a shared idiom.** Earthman built a
  telegraph -> DEFEND -> counter rhythm for exactly one boss (Thar), and
  DEFEND was near-dead (+5 HP) in every other fight, in both combat
  sticks. Generalizing the pattern — a readable wind-up every third
  enemy turn, DEFEND on that turn fully SLIPS the heavy blow and opens a
  x1.5 counter, DEFEND still halves ordinary hits — makes DEFEND
  load-bearing everywhere with no new engine. Reuse the boss's own state
  flags (`_bind_incoming` -> `_counter_open`); port the same three
  branches into the sibling stick (Fey Faire `_fey_turn`). When one
  encounter proves a mechanic, the cheapest depth is making it the rule,
  not leaving it a one-off.
- **Turn a hazard stat into a spendable one for a route economy.**
  Basilica's coherence was purely a thing you protected. Letting the
  player BURN it to force a "B" wall (a corridor at another pitch)
  instead of tuning to its band creates a real shortcut-vs-detour
  choice: fast but thins your buffer for the next interference room.
  Guard the spend so a force can never itself zero you (the risk is
  being thin AFTER), and print the option on the wall you can't pass so
  it is discovered, not hidden.
- **Scarcity makes a witnessing loop a decision.** Tideline reset its
  2 ruled lines EVERY station, so recording was free and "record
  everything" was optimal — no choice. Re-scoping the counter to a
  SEASON-WIDE budget (8 lines for 11 stations) makes WHAT you choose to
  notice the game, and the ending register (living/lost/line/whole)
  emerges from that allocation: go broad for "the whole beach" or spend
  deep in one category. Persist the budget in run_state; gate the
  per-station cap to `min(2, budget_left)`; show the season number, not
  just the station one. Fits the stick's own restraint theme rather
  than fighting it — the same re-scope is the smallest real-choice add
  for any "attention is the verb" loop (Estuary 2's LOOK is next).

### 2026-07-20 · the meta-layer trilogy · one work, not four

Built three cross-pillar systems in one arc — the Oneironaut's
Almanac (hub), the Major Arcana campaign, the collector's Catalog —
all on the SAME read-only spine. Lessons for wrapping finished
pillars into one work:

- **A tiny predicate engine unifies everything.** `AlmanacState.
  predicate_met({token / token_prefix / arcana_won / all_arcana /
  canon-eq / any / all})` is ~40 lines, and all three systems reuse
  it: Almanac entries light, Catalog carts show played, Catalog
  achievements resolve, campaign tokens surface. One matcher over
  the tokens the pillars ALREADY write beats bespoke checks per
  screen. Build the matcher first; pour JSON into it.
- **Read-only over the existing spine = zero migration risk.** The
  whole trilogy adds no save format (GauntletState gained one
  additive `campaign` block, guarded for old saves). It lights up on
  an existing save because it reads tokens/canon that already fire.
  When connecting shipped systems, READ, don't re-plumb.
- **The campaign is a launcher + bookend, not a second engine.**
  MajorArcanaCampaign reuses SpreadHost's exact launch contract
  (`start_scenario` + `game_ended`); it sequences and frames the 22,
  carries a thin thread, and never touches the board/combat code.
  Free play stays. A "campaign" over existing content is mostly a
  selection screen + an interstitial + a progress dict.
- **Menu overlays: one proven scaffold, three screens.** All three
  are ProfilePanel-pattern (`static build(parent)`, ui group, Esc,
  fresh each open). Copying the known-good overlay skeleton made each
  new screen a content problem, not a lifecycle one.
- **Lattice canon lives in docs; structure it once for the UI.** The
  studio/year/credits lattice was prose in the roadmap + aesthetic
  bible. catalog.json is that canon structured — authored ONCE,
  cross-checked against the source (every cart's studio ∈ the studio
  table) so it can't silently contradict the fiction.
- **Commit messages: no backticks, and prefer double quotes.** Twice
  a backticked word ran as a shell command and an apostrophe in a
  single-quoted message broke out. House rule now: plain words in
  commit bodies, double-quoted.

### 2026-07-20 · Fey Faire · closing the economy loop (C2-tail arc)

Finished the whole C2-tail in one arc: Warren, death economy, booth
puzzles, royal exclusivity, gold sinks. The connective lesson:

- **Every source needs a sink; every sink needs a reason.** Adding
  the puzzle-win gold SOURCE (+3) meant the loop needed more sinks,
  so provisions + the strongbox followed. And each sink pays a
  system that already exists: provisions feed combat survival (which
  feeds the death economy — fewer deaths, fewer spent memories); the
  strongbox protects against the exact half-gold-on-death rule wired
  the same day. Don't add a sink the player has no reason to use.
- **A choice is only a choice if it costs.** Titania/Oberon were both
  freely recruitable, so "which royal" wasn't a decision. Barring one
  on recruit turned an inert pair into the run's defining fork — and
  the endings that already keyed on their dispositions suddenly
  meant something. Look for pairs/options the player can currently
  take ALL of; that's usually a missing exclusivity.
- **The hidden third way rewards mastery without cheapening the
  choice.** Reconciling the royals needs BOTH a walked mirror AND an
  NG+ keepsake (Prospero's Word) whose flavor text already described
  this exact use. First-run players feel the hard fork; deep players
  find the door. Gate the "have it all" path behind proof of depth,
  not behind grinding.
- **Three puzzles, three verbs.** Cobweb/Puck/Erlking could all have
  been the same timing game. Making them timing / memory / deduction
  respectively meant one scene taught three skills. When authoring a
  set of minigames, vary the VERB, not just the theme.

### 2026-07-20 · Fey Faire · wiring a specified-but-dead economy

The death/checkpoint economy was fully written in the mechanics doc
and half-scaffolded in code (checkpoints APPENDED on every recruit/
vanquish, `memories_lost` incremented, gold halved) — but nothing
consumed any of it: loss silently routed to the Gate. Wiring it up:

- **Grep for the half-built scaffold before designing from scratch.**
  The checkpoints array, the loss outcome, `memories_lost`, and
  `midway_cell`-restore-on-boot all already existed. The feature was
  90% latent state that no code read. The build was mostly "make the
  existing writes have a reader," not new systems.
- **Respawn = set the restore key, reopen the scene.** The midway
  already restored `_run_state["midway_cell"]` on boot. So
  "respawn at checkpoint X" is one line — set midway_cell, call
  _open_midway — not a new navigation path. Look for the scene's
  existing boot-restore before writing a teleport.
- **Read another scene's const graph via preload, don't duplicate.**
  Checkpoint depth needed the midway adjacency, which lives as a
  `const MIDWAY` in the midway SCENE script. `preload(".../Midway.gd")
  .MIDWAY` reads it with zero instantiation — BFS from the Gate in
  the Host, no copy of the graph, no drift.
- **Keep two views of one counter in lockstep, in a comment.** The
  Trailer's mirror wall cracks memories by `i < memories_lost`; the
  death screen names the memory at slot `memories_lost - 1`. Both
  index the SAME ordered list — so the list lives once conceptually,
  with a comment in each file pointing at the other. A drifting
  second copy would crack mirror 3 while the death screen mourned
  memory 4.
- **A cost the player can't see didn't happen.** Halving gold in
  silence taught nothing. The interstitial that NAMES each loss (and
  what survived) is the actual feature — the numbers were already
  moving. "Every death teaches a specific lesson" is a UI rule as
  much as a balance one.

### 2026-07-20 · Fey Faire · THE WARREN · giving 101 authored feys a purpose

User: "use all the fey, find a purpose... reasons for having them in
a party." The survey found the party did four small things and 61 of
101 feys were authored-but-unreachable. One loop answered both:

- **Split the roster by REACH, not by rarity.** 40 feys are the
  on-map booth cast (you walk to them); the other 61 live "beyond
  the fence" and are reached ONLY through a party fey vouching for
  its kin. Don't build 61 more booth cells — that's a chore, not a
  game. The unreached majority became a side-quest layer (errands)
  that the party UNLOCKS, so a broad roster is the key.
- **"Boons ride existing machinery" is the modes rule at feature
  scale.** Four passive party benefits (seelie OFFER discount,
  unseelie THREATEN-vouch, wildfey booth-pass, song RECITE-retry)
  are each a `_party_has_court()/_party_has_song()` scan + a
  once-per-night guard flag on run_state (`*_night == night`). No
  new scene, no save-format change — the existing negotiation/
  midway scenes just branch on party composition. Holding a fey now
  CHANGES what you can do, which is the whole point of a party.
- **Compose side-quest cards from the target's OWN authored
  fields.** 61 errands read specific and true because each card is
  built at runtime from the target fey's name/manifestation/
  `request`, wrapped in ONE authored hook line in errands.json.
  Generated against feys.json so coverage is total and every `needs`
  (damage_type == weakness, or court_not for weakness "none") is
  satisfiable from the roster. Total bespoke prose written: 61
  lines, not 61 pages.
- **A boon must be a SENTENCE in the roster, not a stat.** Each boon
  shows in the COTS readout as plain language ("Moth · SONG · she'll
  hum you a second try at a line") so party composition is a visible,
  legible choice — not a hidden modifier the player has to infer.

### 2026-07-19 · the expansion pass · A5 depth expansions + two new sticks

Closed the whole expansion backlog (A1-A5, B1-B4, C1-C2) across
one long arc. What the five A5 depth expansions taught, together:

- **"Modes ride existing machinery" held every time.** Counselor
  Mode, Off Season, Second Reading, Second Deck, Subfloor, Year
  Two - none needed a new scene. Each was a flag on the existing
  run state that the existing scene reads: `counselor`, `off_season`,
  `second_reading`, `b_side`, `year_two`. The cheapest depth on
  the shelf is a boolean the host sets before add_child and the
  child branches on.
- **Cross-stick CANON reads, not just tokens.** Estuary 4 reads
  The Tideline's filed register (`canon_vars.tideline_report`)
  from GauntletState; Year Two reads `estuary_3_ending`. Tokens
  answer "did X happen"; canon vars answer "which way" - and
  reading the latter is what makes a sequel feel like it
  remembers YOUR run, not just that a run occurred.
- **Pre-scaffolded slots are a gift; grep for them first.** Mrs.
  Wu, both Tidelines, Estuary 4 all had shelf slots + unlock
  waves already in the library JSONs from earlier sessions. The
  Mrs. Wu build nearly re-created one. ALWAYS grep shelf_layout +
  unlock_graph for the stick id before authoring registration.
- **Hand-formatted JSON: surgical-append or lose the file.** Bit
  twice this arc - once an `open(w)` truncated ending.json before
  json.dump threw on a None format probe. The rule now: probe
  format; if it round-trips, dump; if it DOESN'T (hand-authored),
  read the file, find the array close bracket by brace-depth
  scan, splice the new entry rendered at the detected indent, and
  re-parse to verify BEFORE writing. Never `open(w)` a
  hand-formatted file you haven't already built the full new
  string for.
- **Carry the ending as the OPENING.** Year Two's whole feeling
  comes from the year-one ending becoming the starting cooler
  stock, opening till, and first-night card. A sequel's best
  starting condition is the previous ending, stated in mechanics
  the player already reads (stock, cash) not just prose.

### 2026-07-19 · depth passes · Sisters Wyrd + Fey Faire · giving decisions teeth

User called Sisters Wyrd underdeveloped and Fey Faire's gameplay
thin. Both were right, and the failure mode was the same in both
sticks: systems that LOOK like decisions but always say yes.

- **Audit for "always yes" before adding content.** Fey Faire had
  101 authored feys, 331 skills, 51 quotes — and a negotiation
  where every branch recruited on the first click. Content was
  never the problem; consequence was. Survey the loop for
  decisions with no failure shape before authoring another line.
- **Give every branch a DIFFERENT price and a DIFFERENT failure.**
  Interchangeable branches are one button wearing four labels.
  FF now: OFFER spends gold, PROMISE is refused at three
  outstanding, THREATEN starts fights at the top tier, RECITE
  needs the actually-matching play. Failure locks the booth for
  the night — when in doubt, charge TIME; every stick has a
  clock and it's always the realest currency.
- **Aftermath beats punishment.** Sisters Wyrd's verbs now write
  on the whole territory (widow-weather, calm quadrants, prices
  that land mechanically: the hat means sunstroke, the question
  means no more lore from asking). The choice matters because
  the WORLD is different after, not because a number went down.
- **Grep the data before designing thresholds.** The THREATEN→
  combat trigger was authored at tier 4; the entire roster is
  tier 1–3, so the door would never have opened. Same lesson as
  the HeroImage schema: the data file is the truth, check it
  first (also: two state-key mismatches had made THREATEN dead
  code and RECITE gating fictional for a whole build — grep the
  writer of every key you read).
- **Economies need a loop, not a pile.** SW silver was dead
  because nothing consumed it and nothing renewed it. The bounty
  board fixed both AND produced destinations — a resource loop
  that also generates rides is worth two systems.

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

### 2026-07-10 · Northwind Harbor · listening as the mechanic

- **Passive steps fire on arrival; active steps wait for the
  button.** The town talks AT you: `heard`/`look` steps auto-fire
  when you enter their screen (listening is not an action), while
  pickup/give/use need the deliberate `· pick up ·` press.  This
  split IS the design — walking around is enough to learn
  everything; helping still costs a choice.
- **Carryover chains need a data slot, not code.** Each chain's
  final step carries a `carryover_line`; on later mornings, an
  unfinished chain's location shows that line instead of ambient
  ("still got my glove, then").  The town noticing is one string
  per chain in the JSON.
- **Fog = relabel navigation, change nothing else.** Chapter 6
  swaps nav-button labels from location names to each location's
  `sound_cue` and dims the tableau modulate.  The graph, steps,
  and code path are untouched · the LISTENING mechanic graduates
  to literal purely through data.
- **Canon that predates the game constrains the build — collect
  it FIRST.** Pirate Summer had already canonized the title theme
  (soft pad, F major, 14 s), Chapter 1's opening line (the boy
  asks the dog), Sam's save (mid-pocket, holding the glove), and
  the camp cart's blacked-out Delisle chart.  Grep every existing
  reference to a stick before authoring its data · all four
  landed as authored beats, not retcons.
- **Cross-check data with a script before first boot.** A
  20-line validator (step locs exist · requires resolve ·
  adjacency symmetric · a hero image per location) catches the
  class of bug the engine reports as silent nothing.

### 2026-07-10 · the catalog run · eight sticks in one arc

- **The uniform host contract scaled to sixteen sticks without a
  crack.** Every build this arc (Riffmaster, Glass, Sweetgum,
  E2, Hane no Niwa, Basilica) was host + one core scene +
  data JSONs, wired identically into SlowstockBoot/Shelf.  Cost
  per stick kept falling because nothing about the frame was
  ever re-decided.
- **The core mechanic deserves the new renderer; everything else
  is data.** Basilica got the catalog's one new renderer
  (WireframeView · trapezoid depths + prop line-lists) and even
  that is ~150 lines because the grid, bands, and props are
  JSON.  When tempted to write engine code, check whether it's
  actually a data file wearing a trenchcoat.
- **Real audio beats simulated audio.** Basilica's interference
  is two live sine voices in one AudioStreamGenerator — actual
  acoustic beating, free, instead of a rendered 'dissonance
  WAV'.  When the fiction says two tones fight, let two tones
  fight.
- **Absence is contentable.** Sweetgum's shelf slot doesn't
  exist until a fact is known (hidden_until_token); Basilica IS
  an empty sleeve until an auction beat fills it.  Both gates
  live in shelf/boot data + ~20 lines, and both are the single
  strongest lore delivery in their sticks.
- **Validate reachability in CI-of-one.** The Basilica level
  flood-fill (entry → S/U/M) and the HNN tag-coverage check each
  caught a real authoring bug (green tag clauseless; grids fine
  but only because checked).  Every graph-shaped data file gets
  a 20-line python validator before first boot, no exceptions.

### 2026-07-10 · the Deck compile pass · gdparse is not Godot

- **gdparse checks syntax; Godot 4.6 checks semantics.**  A clean
  gdparse sweep let through: `var x := arr[i]` (cannot infer from
  untyped container · HARD error), `:= max(/clamp(/lerp(/abs(`
  (untyped builtins), `:= loop_var` captures, duplicate `var` in
  nested blocks, and a `func _set(x,y,idx)` colliding with
  Object._set.  **Rule:** never use `:=` when the right side is a
  container index, an untyped builtin, or an untyped loop var ·
  write the type.  Use maxi/maxf/clampi/clampf/lerpf/absi/absf,
  never the Variant versions.
- **Never name a method _set/_get/_ready-anything on a helper.**
  Object's virtuals will collide with a different signature and
  the whole file (and everything depending on it) fails to load.
  HeroImage's painter is now `_put`.
- **Scripts compile on LOAD, not at startup.**  The boot log only
  shows errors for autoloads + the main-menu dependency tree; a
  slowstick that parses today can still explode when first
  booted.  After any typing fix, sweep ALL game scenes for the
  same pattern, not just the ones in the error log.

### 2026-07-19 · the per-stick improvement waves · one paid-off variable each

- **The cheapest depth is one variable, tracked, paid off.** Six
  waves, one mechanic each: bosun pets → chapter-7 line tiers;
  absence gaps in the mudflat journal; water words from the
  pre-rolled luck; Court statuses in Fey combat; NG+ deja-vu in
  Pirate Summer; a repave/solo week in KSM/SSS.  Every one is a
  var in the existing `_run_state`/`_state` (free persistence),
  one seed site, one payoff site.  If a feature needs a new save
  shape, it's the wrong feature for a wave.
- **`<stick>_finished` in OneironauticsTokens is the crossover
  bus.** Estuary 1 and Pirate Summer already emit it; KSM's heron
  and SSS's slushie guest consume it.  When writing an ending
  scene, ALWAYS add the `<id>_finished` token even with no
  consumer yet — a later stick will want the gate, and retrofitting
  the emitter means touching a shipped ending.
- **NG+ = boot-time token check → one seed fact → gated lines.**
  Pirate Summer's whole NG+ is: OneironauticsTokens check in the
  fresh-run boot branch, a `ng_*` fact in the dialogue web, and
  `conditions.requires_fact` lines in the chatter pools.  No new
  systems; idle chatter just learned the same `requires_fact` key
  party chatter had.  Check which pools actually honor the gate
  before authoring gated lines — one grep saved four dead lines.
- **Scripted boss = branch the boss TURN, not the scaffold.** The
  Thar-Krai-Tam arena is one `_boss_turn_thar()` dispatched by
  boss id; the player verbs, HP labels, and outcome flow are
  untouched, so other bosses stay generic until each earns its
  own pattern.  Telegraph-then-punish plus a defend-to-counter
  window is enough to make DEFEND (previously dead) load-bearing.

## TEMPLATE — new lesson entry

```
### YYYY-MM-DD · short session title

- **Punchy lesson, present tense.** Two-to-four sentences.
- **Next lesson.** Same shape.
```
