# COMMUNITY PLANNED · Playbook

Working rules for COMMUNITY PLANNED — Frasier Temple's grand-strategy
inset between parts of the novel *Planned Community*. Read this
before touching `scenes/games/CommunityPlannedGame.gd`,
`scenes/games/CommunityPlannedBBS.gd`, or any
`resources/games/community_planned/**` file.

For the *what we're building* doc, see `_COMMUNITY_PLANNED_SPEC.md`.
For the phase-2 scope contract, see `_COMMUNITY_PLANNED_PHASE2_SCOPE.md`.
This playbook is the *how we work on it* doc.

---

## Core rules (stable across sessions)

### Data discipline

1. **JSON is the source of truth.** Every BBS, board, thread, DM,
   reveal, interlude, hidden-board, glossary entry lives in
   `resources/games/community_planned/**.json`. The scripts read.
   The scripts do not invent. Adding content = editing JSON.
2. **Per-BBS layout.** Each external BBS lives in its own folder:
   `bbs/<bbs_id_lower>/board_list.json` + one
   `bbs/<bbs_id_lower>/<board_id_lower>.json` per board. The
   dial_directory.json points to each BBS's board_list.
3. **Hidden boards are listed in the parent BBS's board_list.json**
   with `"visibility": "hidden"` and a `discoverable_from_week`
   field. They appear in the player's board list only after
   discovery. Their actual content file lives next to the public
   boards in the same directory.
4. **Thread ids are BBS-prefixed.** `MS_*` = MAINSTREET, `TB_*` =
   THE_BAR, `OH_*` = OVERPASS / the_harbor, etc. The breadth-unlock
   checker in `CommunityPlannedBBS.gd` keys off these prefixes —
   keep them stable.
5. **Validate before commit.** Run
   `python3 -c "import json,os; [json.load(open(os.path.join(r,f))) for r,_,fs in os.walk('godot/resources/games/community_planned') for f in fs if f.endswith('.json')]"`
   before committing JSON. A single malformed file breaks every
   board-list load.

### Engine discipline

1. **Save-version migration is additive.** Every new persistent
   field defaults to its empty value in `_apply_state`. Existing
   saves load without complaint. Never break an old save.
2. **Effect interpreter is the choke point.** All consequences —
   from DMs, from hidden-board visits, from anomalies, from reveals
   — route through `_exec_effect(eff, ctx)`. New effect kinds get a
   branch in the match; the catch-all `push_warning`s an unknown
   kind. Don't bypass.
3. **Strategic state buckets exist; use them.** `_flags` (bool),
   `_counters` (int), `_queued_burns` (deferred consequences),
   `_canon_vars` (canonized facts), `_unlocked_artifacts` (shelf
   ids). DM and choice effects write into these via the named
   effect kinds (`set_flag`, `increment_counter`, `queue_burn`,
   `set_canon_var`, `unlock_artifact`).
4. **BBS overlay is a child Control, not a separate scene.** The
   strategic engine instantiates it on Sunday nights, `await`s
   `hung_up`, merges the session dict, frees the overlay. No state
   pickling.
5. **Session deltas flow one way.** The BBS receives a snapshot of
   what it needs in `open(week, readmitted, dm_read_to_week,
   discovered_hidden_boards, unlocked_artifacts, glossary_unlocked)`.
   The BBS returns a fresh delta dict via the `hung_up` signal. The
   engine merges. The BBS doesn't reach back into engine state.

### Content discipline

1. **Every thread / DM / reveal carries `available_from_week`.**
   Authoring is staggered. The BBS engine filters on `<= _current_week`.
2. **Canon humans use canonical_character_id everywhere.** Posts,
   DMs, replies, anomalies. The cross-system registry at
   `resources/characters/_index.json` is the authority. Free-form
   handles (`STEEPLE`, `chainlinkspiral`, etc.) are non-canonical
   regulars — no canonical id, post bodies must work without one.
3. **Voice is per-sysop.** RUST_CODE / OVERPASS / CALICHE /
   DRY_BLOOM / BEDROCK / SNACKS each have a register documented in
   `aria_glossary.json`. Posts on a sysop's board match the
   sysop's register. The W11 glossary unlock surfaces the cross-
   register translations; don't undermine it by mixing voices.
4. **Dial-up clue numbers must appear in a post body.** If the
   hidden board has `"dial_number": "5550107"`, then somewhere in
   a public-board thread the string `5550107` must appear, planted
   plausibly in flavor text. Otherwise the player can't discover
   the board.

### UI discipline

1. **Phosphor-green CRT palette only inside the BBS.** Greens
   stratified by intensity (C_FG_BRIGHT / C_FG / C_FG_DIM /
   C_BORDER). Amber (C_HIGHLIGHT) is reserved for "new thing
   discovered / artifact unlocked / glossary hint." Orange
   (C_WARN) for cover loss / queued burn lands.
2. **Single-letter navigation is the player's vocabulary.**
   `M` = mail (DMs). `G` = glossary. `N` = dial new number.
   `D` = dial again. `B` = back. `Q` = hang up. Don't repurpose.
3. **HUD honors F4.** Per CLAUDE.md the BBS overlay is a Control
   under the strategic scene; F4 sweeps it via the usual
   CanvasLayer / "ui" group machinery. New HUD widgets must join
   one of those groups OR live inside a CanvasLayer that's already
   swept.

---

## Design note · POST-CAMPAIGN ENDLESS MODE — 2026-07-19, BUILT same day

Implementation deviations from the note below: entry lives on the
SLOT PICKER (a "↳ SEPTEMBER AND AFTER" row under any finale-done
slot) rather than a separate continue screen — the picker already
is the continue screen. Retire is a button on that row and works
without loading (ledger computed straight off the endless save
file). The ratchet reads `base_severity` (the actual template
field): sev-4+ templates double their draw weight from the 8th
endless week. Brightness curve is logged daily (capped 400) in
`_flags.endless_brightness_log` and rendered as a text sparkline
(. · : █) on the end screen. Ledger file:
`user://saves/community_planned_endless_ledger.json`.

The backlog's replayability item, designed against the engine as
it is (CommunityPlannedGame.gd, TURNS_TOTAL = 100, Labor Day
finale gated on `labor_day_finale_shown`). Implementation is its
own arc.

**Entry.** After the Labor Day finale has been SHOWN on a save,
that save's continue screen gains "SEPTEMBER AND AFTER" — reopen
the same board, same roster, same regional state, seasonless.
Campaign saves untouched: endless writes to a sibling save key
(`slot_N_endless`), never over the campaign slot, so the finale
state stays replayable. The three campaign slots stay three.

**The loop.** Days keep counting past 100. No new anchor events;
instead a scaling pressure curve:
- Weekly spawn keeps firing (the existing `_run_weekly_spawn`),
  but the spawn budget ratchets: +1 problem per week every 4
  weeks, severity floor rising every 8 (reuses the severity-6
  chain templates from the 29-template lattice — endless is where
  those chains get to run long).
- Tower brightness becomes the run's live health bar: endless has
  no finale to absorb a WHITE tower, so WHITE = the run ends
  (a named ending screen, "THE TOWER FINISHES", plus the run
  ledger below). This is the mode's loss condition and its whole
  dramatic argument.
- Demons keep evolving on their existing clocks; humans keep
  their obligation streaks. No new agent mechanics in v1.

**Run ledger (the P3 item rides along).** On endless end (tower
white, or player retires the board voluntarily): weeks survived,
problems resolved per region, tower brightness curve
(sparkline from a per-week brightness log the mode records),
demons evolved. Stored per endless run; the compare screen lists
past runs. This gives replays a target without touching campaign
scoring.

**Protected, restated.** BBS thread-gating and the diegetic
terminal stay as designed. Endless does not add BBS content;
threads already read stay read.

**Non-goals v1.** No new problem templates required (the 29 +
severity chains suffice at ratcheted volume); no new specialists;
no difficulty selector — the ratchet IS the difficulty.

---

## Lesson capture cadence

After every work session that touches Community Planned and
involves more than 3 commits, an aesthetic decision, or specific
user feedback, append a dated entry to **Recent lessons** below
using the template at the bottom. Lessons graduate up to **Core
rules** once they've held across multiple sessions.

---

## Recent lessons

### 2026-07-10 · visual upgrade · region banners + agent busts

Second half of the art pass: imagery, not chrome.

- **Every region folder now opens with a picture.** 160×36
  HeroImage banners from `tools/sprites/gen_cp_region_banners.py`
  (deterministic): Graustark's dusk rooflines + the riverboat
  memory, Harmony Creek's seven IDENTICAL gables (the repetition
  is the region), Small Wood's night treeline with the tower.
- **The tower banner is state.** Four variants (dim / warming /
  bright / white) keyed exactly to `_tower_brightness`;
  `_render_tower_strip` swaps the Small Wood banner texture per
  render. The game's central dread is now a picture that
  brightens, not a word that changes. When a strategic value has
  exactly N states, N authored variants beat any dynamic tinting.
- **Agents have faces.** VnBustPortrait (the VN's procedural
  tier) renders roster icons + dossier portraits from the agent
  id. Demons share one sickly-violet accent so the class reads
  at a glance; humans get stable hash hues. On-dispatch agents'
  busts dim — presence reads without parsing text.
- **Banner render-only, save untouched.** Banners live in
  `banners/` next to the data JSON but are loaded only by the
  render path with the standard missing-file fallback (cache the
  null so the warning fires once).

### 2026-07-10 · strategic-layer art pass · font floor, folder tabs, severity colors

Part of the game-wide graphics sweep. The BBS was untouched — its
phosphor terminal is diegetic and already authored. The strategic
layer got:

- **Font floor 12.** Sixty sub-floor labels (36×10pt, 12×9pt,
  12×11pt) swept to 12pt in one sed pass. The strategic screen is
  played at couch distance; 9pt "send to tower" was invisible.
- **Region panels are file folders now.** A 4px left accent stripe
  per region, hue hashed from the region id — stable forever, and
  the eye learns which folder is which without reading titles.
- **Problem severity is a color, not just a dot count.** Titles
  render calm tan (sev ≤3), amber (4-6), alarm red (≥7). The dots
  stay; the color is what you see from across the room.
- **Advance Day is filled amber; everything else is flat.** The
  game has one primary verb per day — it should be the one filled
  button on screen. New/Back/Shelf are flat steel-bordered.
- **Drafting-table backdrop.** The flat Background ColorRect now
  sits under a once-at-boot procedural texture: corner shade,
  paper grain, a barely-there survey grid. Frasier's planning
  document sits on a desk, not on a color fill.
- **Beware editing a file with sed mid-session.** The Edit tool
  tracks file state; a sed sweep invalidates it and later Edits
  fail until re-read. Do the sed FIRST, then the surgical edits.

### 2026-07-04 · human depth + scrapbook + turned demon + interlude batches (16 interludes added)

The follow-through session. Six commits · human-obligation
helper + voice lines · quiet-week recovery + human pair table +
scrapbook body-scan · turned demon integration (markers +
regional events + THE_BASEMENT threads) · two interlude batches
totalling 16 new interludes with matching predicates and fire
counters.

Lessons:

- **Latch flags for end-of-summer predicates, don't scan history.**
  End-of-summer interludes want to gate on "was this ever true
  this summer" — e.g. "no demon ever hungry" or "b6_fundraiser
  marker ever set." Scanning historical events at Labor Day
  would need retained events; instead latch a flag at the
  moment the state first crosses (`_flags["any_demon_ever_hungry"]
  = true` in the tier helper; `_ever_set_markers` appended in
  the marker effect). The flag is O(1) to check and cheap to
  persist. General rule: any predicate of the shape "ever
  happened this summer" should be a latched flag or an
  ever-array, populated at the crossing site, NOT a scan.
- **Counters for interlude thresholds live at their fire sites.**
  `_demon_pair_fires`, `_human_pair_fires`, `_basement_rite_fires`,
  `_quiet_week_fires` all increment inside the function that
  did the thing. Interlude predicates read them at Labor Day.
  This is the SAME pattern as the "route mutations through a
  helper" rule from the demon-depth arc — the helper owns both
  the state change AND the observability increment.
- **Marker-set effect is one of the biggest cross-file
  concentrations of leverage in the engine.** A single stage
  choice sets a marker · the marker gates a positive regional
  event that fires only while it's active · the marker being
  ever-set gates a Labor Day interlude. One authoring surface
  (`set_regional_marker` in problems.json), three consumption
  surfaces (regional_events.json requires_marker, engine
  ever-set flag, interlude predicate). This is where new
  content shortlists live: every marker deserves at least one
  requires_marker event AND at least one 'ever_set' interlude.
- **BBS handles are the character bible.** The turned demon's
  BBS handle (fresh-second-suitcase) was authored in the
  BASEMENT thread FIRST · once the handle existed, the
  rule-breaking beat, pair interactions, and interlude flavor
  all had a canonical name to hang off. Same lesson as the
  demon handles pass: put the character in the BBS before you
  put them in the mechanics. The handle is the artifact that
  travels.
- **Interlude authoring works best in batches of 8.** Each
  batch takes about one commit. A batch of 4 feels thin next
  to the existing 30; a batch of 12 stretches the predicate
  surface too wide and starts requiring engine plumbing. 8 is
  the number that fits comfortably in one commit's diff and
  makes a visible shelf bump for the player.

### 2026-07-02 · demon-depth batch · corruption tiers, THE_BASEMENT rite, demon pairs, dispatch-time pair preview

The five-commit demon arc. Named corruption tiers (steady /
hungry / restless / close_to_turning / turned) with per-tier
spillover-roll on successful dispatch; tier-crossing warnings +
per-demon voice lines routed through a single helper;
THE_BASEMENT expanded 4 → 14 threads with each demon getting a
distinct handle (brown-water / sideways-current / 17-year-hum /
long-road-twice / line-counter / coat-inside) and Frasier's three
pinned admin rules; a 20-entry demon-pair interaction table with
warm / loud / cold tones and cover/attention deltas; dispatch-
picker preview surfacing the pair before commit; roster-is-loud
interlude when 3+ demons are hungry+ simultaneously.

Lessons:

- **The tier helper is the choke point.** All corruption
  increments route through `_apply_corruption_to_demon(id, amt)`.
  Every path that touched `st["corruption"] = ...` directly had
  to be updated. The upside: adding new consequences (auto-turn
  at 9, tier-crossing warning, per-demon voice line,
  rule-breaking beat, auto-seed of turned_demon_active) all
  happen in ONE place. Same lesson generalizes: any state that
  has meaningful thresholds should be mutated through a helper
  that owns the threshold checks. Direct writes are a footgun.
- **The dispatch preview is where friction lives.** Adding the
  pair preview inline in `_make_dispatch_preview_row` (right
  after the detail line, before the button) surfaces the
  consequence of the choice at the moment of decision. This is
  more valuable than a post-hoc log line — the player weighs
  cover-negative against the value of the pair before committing.
  Codified for future mechanics: if a decision has a scripted
  consequence, surface it in the picker, not just in the log.
- **Named tiers beat raw numbers.** "Corruption 4" is invisible.
  "Hungry · 15% signature-spillover chance on dispatch: 15%" is
  a decision. Same principle as the human life_cost_thresholds
  (obligation 3 = "wife stops answering the phone at night"):
  put the mechanical bucket into words the player carries around
  in their head between sessions.
- **The BBS is the character bible.** Adding THE_BASEMENT
  threads gave the demons voices before anyone tried to author
  demon-facing gameplay. When the tier-crossing rule-break beat
  needed a handle, `_DEMON_BBS_HANDLES` already existed as a
  const dict — because the BBS threads had used those handles.
  If a character is going to appear in mechanics, they should
  have posted at least once first.
- **Pair tables should be alphabetical-key.** `moth+starling`
  and `starling+moth` are the same pair. Storing under a single
  alphabetical key + doing `.get(k1, .get(k2, {}))` at read time
  cuts the table in half AND removes the "did I author this in
  both orders" question. Applies to any commutative relation.
- **Interlude counters need a reset condition.** The
  roster-is-loud beat only fires the FIRST day the roster
  crosses 3 loud demons. The flag has to CLEAR when the roster
  drops back to zero-hungry, else the beat is a one-shot per
  save. General rule: any "one-shot for this state" needs the
  inverse condition to clear the latch, so a second wave can
  fire the beat again.

### 2026-07-02 · BBS + locale polish arc · 33 new threads + 14 Wave-2 locale detail-passes

The long BBS-and-locales pass. Went from 118 threads → 151 across
15 boards, and from 4 Wave-2 locales with detail-passes → 14 (all
of them). ~5,000 lines of Blender geometry code + ~1,000 lines of
BBS content across ~10 commits.

Lessons:

- **Cross-arcana threads are the glue.** Every new BBS thread that
  references a Wave-2 gauntlet character (Marcelle Bernard, Ollie
  the projectionist, Delphine at Christian Ice, the Broussards,
  Cypriane at the lighthouse) makes both games richer at once.
  The rule of thumb: half of new threads should be cross-arcana
  callbacks; half should be new original content. The mix keeps
  the world both connected and fresh.
- **Sysop voice is the load-bearing constraint.** WIRE_MOTHER's
  foal-register, STEEPLE's keel-keeper terseness, THE_QUARRY's
  question-form-only, PALOMINO's second-light lyricism · once
  those are established, every new thread on that board must obey
  them. Threads that break voice read as untrustworthy · the
  player learns to filter them out. Never author a thread on a
  board without re-reading the top comment's `notes` field first.
- **The four-regular found-family is the parish's actual heart.**
  hasslein / uzhekwurm / jlowe / chainlinkspiral on the_back_porch.
  Every board benefits from at least one of them dropping in as a
  reply. Not because they're the plot · they aren't · but because
  their voices are the parish's texture at rest. When in doubt
  about who to reply, ask which of the four fits, and put them in.
- **Under-populated boards have the highest per-thread value.**
  Adding the 3rd thread to a 2-thread board (CK, OT, DA, the
  layers, etc) gives more world-density-per-word than adding the
  16th thread to mainstreet. Prioritize the thinnest boards when
  doing depth passes.

Locale-polish lessons:

- **_wave2_props() as a discipline for Wave-2 locales.** Every
  Wave-2 build script got a dedicated function surfacing the
  named props from the two new bookend scenarios. Additive to the
  canonical _dressing(); never rewrites; kept per-locale in the
  200-500 line total budget. Names in prop-IDs reference the
  scenario's canonical-character-name so an animator/lighter can
  find them by grep later.
- **Placeholder pos_xy [0,0] for scenario-additions is fine but
  needs a follow-up pass.** The 46 scenario_spaces_additions
  entries all currently sit at [0,0]. They resolve at load-time
  (no crashes) but the strategic-map visualization will pile
  them on top of each other until someone moves them. Note in
  the playbook: the visual-polish pass is a separate deliverable.

### 2026-06-26 · all 21 problem templates carry stages[] now

Closed the long arc on mission-stages content. The 4-template
prototype set (memorial_grief / family_succession / infrastructure_failing
/ cathedral_visitor) was carrying the whole demonstration. Today's
work extended `stages[]` to every remaining template — 17 more
templates across four commits — so the clicker-without-choice
feeling is gone from every dispatch path the player can hit, not
just the showcase ones.

Lessons:

- **The "stages[] for every template" floor matters more than the
  ceiling.** A few elaborately-staged scenarios with 3-stage arcs
  (cathedral_basement_relay's boiler/desk/coast) is great, but the
  player feels the absence of choice on the 14th unstaged dispatch
  more than they feel the presence on the 1st staged one. Coverage
  beats depth at this layer of the game; the high-craft moments
  live in the staged paths that branch widely on BBS gates.
- **BBS-thread gates are the connective tissue between the two
  game modes.** Twelve of the 21 templates now include at least one
  choice gated on `requires_bbs_thread`. The threads picked are
  diegetic — `MS_00B_LEVEE` gates the wake-problem gauge cross-
  reference, `MS_010` gates pulling a civilian into the cathedral
  basement relay during the W14 storm, `BP_015` gates the Booth-6
  pattern-match against "the girl at the back of the parish."
  Reading the BBSes is now load-bearing for the strategic game,
  not flavor.
- **Single-stage templates are valid when the choice is the room,
  not the sequence.** Not every dispatch wants two stages; some
  benefit from concentrating the decision into one moment.
  `town_meeting_pushback` (the fifty-year Small Wood room),
  `ground_refuses_plant` (the locals who walk the dirt road) —
  these are one-stage with three branching choices. The shape of
  the problem dictates the shape of the staging; don't pad to a
  template count.
- **The same effect verbs cover staggered narrative consequences
  fine.** `set_canon_var`, `set_flag`, `spend_cover`, `lose_contact`,
  `decrement_region_state`, `increment_counter` — the existing
  effect dictionary verbs handled every stage authored today
  without adding a single new verb. The interpreter is doing its
  job; pile content onto the existing primitives rather than
  growing the engine.
- **Resolution flavor success/failure pairs ship with every staged
  template now.** Two-three lines each. They get sampled when the
  dispatch resolves and they make the moment land harder than
  "dispatch resolved successfully." Cost: ~5 minutes of authoring
  per template; benefit: the post-resolution beat doesn't read as
  game-system text. Worth it every time.

### 2026-06-26 · mission stages + visual-detail passes across 7 locales

Long arc: from the playtest feedback ("feels like a clicker · no
real choice when the best choices are outlined") through the
mission-stages system to scene-description detail passes across
every Wave-1 arcana locale. Twenty-plus commits. Most durable
lessons:

- **Build playtest feedback into the next sprint, not the next
  release.** The user's "feels like a clicker" reply led directly
  to the multi-stage dispatch system (`5ac064b`), which addressed
  the design root cause not the surface complaint. Surfacing the
  feedback in 2-3 sentences (clicker-feel, no real choice, would
  be better if it had X) is more valuable than a long retrospective.
- **A staged dispatch shouldn't auto-resolve.** When a problem
  template declares `stages[]`, the dispatch's `return_day` is
  pushed to `_day + 999` so the existing `_resolve_dispatch` auto-
  resolve path never fires; resolution happens only after the
  last stage choice, deterministically (success keyed off
  `effort_accumulated >= 0.95 * effort_to_resolve`). Don't try to
  graft the random-roll resolution onto a system that's already
  made deterministic narrative choices.
- **The scene_description is the build script's contract.** Each
  Wave-1 arcana setup_*.json names half a dozen specific props
  ("Faith the dog under the counter" / "the cypress beam is the
  cypress beam" / "the wall clock reads 3:47"). The detail pass
  was: read every scene_description, list every named prop,
  check if it exists in the locale's build script, add what's
  missing. Cathedral cake-in-the-fridge, diner Faith, bungalow
  Anya's monitor + John's email window, riverboat Table 14
  plaque, Roberts house Polaroid + drip faucet + bird, helm wrong-
  brass railing, hierophant long-black-car-at-the-curb — all of
  these existed as JSON strings the player would read at gauntlet
  start with no visual anchor before today's passes.
- **One detail per beat is the right density.** Each scene_description
  has 4-8 named beats. Don't over-build (geometry that isn't
  named won't be read; the player's attention is already spoken
  for). Don't under-build (skipping a named beat undercuts the
  scenario's voice). The pass-per-locale ran ~140-440 lines of
  Blender code — that's the right size.
- **The "wrong brass / right brass" trick is the visual hook.** The
  helm's deliberately-tarnished brass railing reads as wrong only
  when you see the right brass on the SIDE DOOR knob next to it.
  Visual contrast carries flavor that's hard to read from text
  alone. The same trick: Booth 6 is the canonical booth because
  it has a distinct fluorescent the others don't.
- **Compositional locale GLBs unlock multi-stop scenarios.** The
  Hierophant circuit spans church → brunch → bandstand. Built as
  a single GLB with two physical stops (church at south, bandstand
  at north) plus a connecting tree-lined path; brunch uses the
  existing riverboat GLB and the host can swap. This avoided
  three separate locale builds for one arcana.
- **Bulk-generate .tscn files with sed.** Three new locale .tscns
  generated in one shell loop substituting uid, GLB path, and
  top-level Node3D name from a template (`roadside_chapel.tscn`).
  Saved ~30 minutes vs hand-authoring each.
- **Host scripts are attach-points, not loaders.** The `.tscn`
  doesn't reference the GauntletHost script in `ext_resource`;
  the script is attached to a Node3D in-editor. So scaffolding a
  host script + a .tscn gives the user a 5-click finalization in
  Godot editor — neither file needs to know about the other at
  scaffold time.

### 2026-06-22 · holistic audit + Tier 1 fix pass

After phase 3 shipped, ran a holistic audit (parallel subagents on
Gauntlet and the non-BBS layer of Community Planned). Surfaced six
real bugs and one structural finding across both games. Tier 1
fixes shipped this commit:

- **F4 HUD compliance was zero on both games.** Adding `groups=["ui"]`
  to the root Control of `CommunityPlannedGame.tscn`,
  `CommunityPlannedBBS.tscn`, and `TarotGauntletGame.tscn` brings
  them under the F4 sweep in `FirstPersonController._apply_hud_visibility`.
  Lesson graduates to Core: **every new game scene MUST add
  `groups=["ui"]` on its root Control at the .tscn level.** Doing
  it at runtime is too easy to forget.
- **Dynamically-spawned modals need `add_to_group("ui")` too.**
  AcceptDialogs added via `add_child(dlg)` are Window nodes — the
  F4 recursive tree-walk only finds CanvasLayers and "ui"-group
  members. Without the explicit add-to-group, popups float over
  cleanly-toggled HUD. Patched all 7 call sites in CP; future
  modal-creating code needs the same `dlg.add_to_group("ui")`
  before `popup_centered()`.
- **`wipe_corruption_on_demon_in_small_wood` had a name/scope
  mismatch.** The handler iterated every demon, not just demons
  on dispatch to Small Wood. Audit caught it; fix walks
  `_active_dispatches` for the region filter.
- **`resolve_random_problem` anomaly could break an active
  dispatch's `problem_index`.** Removing an array element shifts
  later indices; any dispatch bound to a higher index suddenly
  points at the wrong problem. Fix: skip bound indices when
  picking, and shift later-than-removed dispatches' indices down 1.
- **JSON-declared knobs that the engine hardcodes are a smell.**
  `cross_region_dispatch_cost_modifier` was specified per region
  in `regions.json` but the dispatch math hardcoded 1.5. Either
  read the JSON or remove the JSON key. Rule going forward: a
  JSON field with no engine read is dead — delete or wire it.
- **Migration functions should seed every new field for
  legibility,** even if `_apply_state` would default the rest.
  `_migrate_save_v1_to_v2` now lists each v2 field explicitly so
  the migration reads as a record of the schema, not a hint at it.

### 2026-06-22 · phase 3 ships (sprints 1-4)

- **Branch-tagged DM beats are the right shape.** The Aria DM needed
  branch-specific post-decision beats (rebind/let_her_hold_it/
  send_her_away). Tagging beats with `if_branch` + `branch_key`
  and filtering in `_render_dm_view` + `_dm_unread_count` keeps a
  single DM file as the source of truth. The engine ships
  `_canon_vars` into BBS.open() so the filter has the choice
  available. Cleaner than three separate files per branch.
- **Inverting the "reward = easier" reflex for the storm.** The W14
  storm hard branch — the cathedral basement relay actually fires
  as a problem — is the *reward* for reading the BACKCHANNEL all
  summer, not the punishment. The soft branch (storm turns east,
  keel-keeper called it right) is what you get if you weren't
  paying attention. Players who do the work get to do the work.
  Note for future events.
- **The interlude shelf section model scales.** Adding
  `aria_summer_w11_interludes` was: append to the JSON, add to
  the two arrays in `_check_interlude_earnings` /
  `_all_earned_interludes`, add the new predicates, add a
  per-section color in the modal. Five touchpoints, none of them
  branching. The shelf section pattern is the right abstraction.
- **Inline glossary annotation needs longest-first matching.** A
  naive substring scan for register terms broke when a short
  term ("the third") was a prefix of a longer term ("the third
  bell"). Sorting the terms by descending length and scanning in
  that order — plus a lookback to skip wraps that would land
  inside an existing BBCode tag — gave clean inline highlighting.
  See `_annotate_body_with_glossary` in CommunityPlannedBBS.gd.
- **Modal finales beat scene transitions for declarative closers.**
  The Labor Day finale is an AcceptDialog modal built
  programmatically — same pattern as the interlude shelf. No new
  scene file. Closing the modal chains to the post-summer outro,
  also a modal. For closing screens that are read-only and don't
  need camera work or animation, two AcceptDialogs in series is
  cheap and reads right.
- **A region's weekly cadence makes it a place.** Small Wood and
  Harmony Creek were "labels with mechanics" until the Sunday
  loop started firing one flavor line per region per week. The
  lines are 5 per region rotated by week number — five strings
  total, total auth time < 10 minutes — and the regions feel like
  places now. The same pattern probably scales to more regions in
  vol7.

### 2026-06-22 · phase 2 sprint 4 closes (a-d)

- **The hidden-board dial recognizer wants its own input mode.** I
  originally tried to overload digit-keys in the dialer with a
  "type a 7-digit number" affordance and it conflicted with the
  1-9 pick-by-index keys. Splitting it into an explicit `N` →
  `_in_dial_input = true` mode with ENTER / ESC / BACKSPACE made
  it tractable. The mode flag also let me piggyback the NO CARRIER
  "press any key to dismiss" state on the same machinery.
- **Earned-through-breadth unlocks need a prefix convention to be
  cheap.** THE_BACKCHANNEL unlocks when the player has read one
  thread on each external sysop BBS + SNACKS. The check walks
  `_read_thread_ids` looking for known prefixes (`OH_`, `CP_`,
  `DA_`, `BP_`, `SN_`). Required keeping thread ids consistently
  prefixed by their parent BBS / board — codified above as a core
  rule.
- **Queued burns need a delivery tick.** DMs scheduled burns into
  `_queued_burns` from sprint 2 but nothing in the day loop
  consumed the queue. Burns silently accumulated. Added a
  `_tick_queued_burns()` after the other economy ticks in
  `_on_advance_day` that fires every entry whose `trigger_day` has
  arrived, then drops them. Lesson: every persistent state bucket
  needs a corresponding tick or it's just a graveyard.
- **The same effect interpreter handles BBS-session effects.** DM
  replies, hidden-board visits (RIVER_HOUSE cover cost, BASEMENT
  burn -1), and reveals all flow through `_exec_effect(eff, ctx)`.
  Adding new effect kinds — `demon_burn_reduction`,
  `the_grove_intel`, `spend_cover`, `unlock_artifact` — is the
  cheap path. Don't add ad-hoc handlers; extend the match.
- **JSON validation as a pre-commit gate.** A 14-thread JSON edit
  with one trailing-comma typo silently broke six board loads
  before I caught it. The one-liner `python3 -c "import json,os;
  [json.load(open(...)) for ...]"` runs in ~50ms and catches all
  of it. Worth running before every BBS-content commit.
- **The glossary unlock works because the substitutions were
  authored from the start.** The five sysops have been writing in
  their respective registers since sprint 1 (STEEPLE / WIRE_MOTHER
  / PALOMINO / THE_QUARRY) and sprint 2 fleshed it out. When the
  W11 unlock fires and the player reads any past post with the
  glossary visible, the prior weeks of seemingly-flavor-only
  posts retroactively become legible. The lesson: bake the secret
  into the content from day one, then the late-game unlock is
  free interpretation rather than late-game retcon.

---

## TEMPLATE — new lesson entry

```
### YYYY-MM-DD · short session title

- **Punchy lesson, present tense.** Two-to-four sentences. What
  the situation was, what surprised us, what the rule is going
  forward. Reference the file and function if it's anchored to
  code.
- **Next lesson.** Same shape.
```

### 2026-07-19 · +8 templates (21 → 29) · the escalation lattice

- **New templates chain INTO existing ones, both directions.** The
  eight new problems spawn established templates when neglected
  (dock rot → memorial_grief, buyout letters → surveillance, well
  taste → seed_dying, band bleed → town_meeting_pushback), so the
  mid-summer board stops repeating and starts COMPOUNDING. When
  adding problems, wire the severity-6 spawn to a template the
  player already fears — the dread does double duty.
- **Reuse existing problem_type values; new ids, old types.** Agent
  specialty matching keys off problem_type — a novel type string
  matches no specialist and quietly plays worse. All eight ship on
  established types (infrastructure_failing, hoa_action,
  surveillance, ground_refuses_plant, local_press_exposure,
  lease_and_licensing, model_home_feel).
- **Validate ideal_handlers against agents.json ids.** The field is
  advisory, but "the_quiet_one" (invented) and
  "the_small_wood_contact_jules" (real) look equally plausible in
  prose. A cross-reference script caught it; eyeballs did not.
- **BBS gates only on thread ids that exist.** Wanted a CALICHE
  gate; no CA_* thread ids exist yet — the authoring script
  auto-remapped to BP_014 rather than shipping a dead gate. Gate
  fallback beats gate faith.
- **Late-summer weight class = severity 4 + multi-household
  stakes.** buyout_letters (sev 4, six households, the 4%% detail)
  is the escalation shape W12+ wants: not bigger numbers, more
  people at one kitchen table.
