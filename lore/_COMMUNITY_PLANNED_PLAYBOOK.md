# COMMUNITY PLANNED · Playbook

Working rules for COMMUNITY PLANNED — Frasier Temple's grand-strategy
inset between parts of the novel *Planned Community*. Read this
before touching `scenes/games/CommunityPlannedGame.gd`,
`scenes/games/CommunityPlannedBBS.gd`, or any
`resources/games/community_planned/**` file.

For the *what we're building* doc, see `_COMMUNITY_PLANNED_SPEC.md`.
For the phase-2 scope contract, see `_COMMUNITY_PLANNED_PHASE2_SCOPE.md`.
For the network's canonical history (1988–2026, board founding
dates, archival-stamp reconciliation, authoring rules for
historical posts), see `_COMMUNITY_PLANNED_BBS_HISTORY.md`.
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

0. **COMMUNITY PLANNED takes place in 2026. Full stop.** Per the
   spec ("a grand-strategy gallery game inset into vol 6's
   summer"; "the canon roster, aged forward into vol 6's
   timeline") and standing user correction, made repeatedly
   across sessions. The 2026-08-14 sweep converted the game's
   entire current-summer grid (337 date stamps, the engine's
   Memorial Day / Labor Day dialogs) from the erroneous 1996 to
   2026 — so any pre-2026 date stamp you find now is
   *deliberate archive texture* (the attic's memorial threads,
   the MAINSTREET '96 welcome sticky, the barn's 1981 binding
   sticky) and must be left alone. The calendar: Day 1 =
   Memorial Day = **Monday, May 25, 2026**; the Labor Day
   cookout finale = **Sunday, September 6, 2026**; a 1996
   summer weekday lands two calendar days earlier in 2026
   (Sun Jun 4 '96 → Tue Jun 2 '26, etc. — verify against the
   real 2026 calendar). The bayou-scene games and BBS-era
   culture (1985–2004, see
   `planned_community/digital_subculture.md`) appear as
   decades-old retro objects — anniversary threads, flea-market
   finds, period iron kept alive — never as new releases. The
   circle running a dial-up BBS in 2026 is the point, not an
   error.
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

## Lesson capture cadence

After every work session that touches Community Planned and
involves more than 3 commits, an aesthetic decision, or specific
user feedback, append a dated entry to **Recent lessons** below
using the template at the bottom. Lessons graduate up to **Core
rules** once they've held across multiple sessions.

---

## Recent lessons

### 2026-08-14 · game-fiction pass · slowstick canon + digital-subculture threads

The session that gave the slowsticks their canon
(`lore/milk_and_honey/slowsticks.md`) and threaded the fictional-
games substrate into four thin CP boards (OH_005, CB_004, BL_006,
TA_005 on the art wall).

- **Reconcile new canon against established numbers before
  writing a word.** The slowstick doc works because the SCUMM
  machine's drawer arithmetic already existed in two places
  (scumm_machine.md: 42 original sticks + ~50 added since 2007;
  digital_subculture.md: ~40 canonical + ~30 studio titles + ~20
  unknown). Designing the slowsticks as *the source of the ~30
  studio sticks* made the new doc land exactly on both existing
  inventories instead of adding a third count to keep in sync.
  Rule: grep the numbers first; author into them.
- **Game-fiction threads read best when the sysop's trade grounds
  the game.** WIRE_MOTHER reviewing SUBSTATION as an electrician
  (the lockout sequence is correct; that is not public
  information) and chainlinkspiral reviewing NIGHT WALK as a
  man who walks fence for a living carry more world-weight than
  any enthusiast post could. Pick the reviewer whose day job the
  game is about; the register does the rest.
- **The setting is 2026 — corrected mid-session by the user,
  now Core rule #0, then enforced by a full sweep.** The first
  draft of these four threads was dated 1996, inferred from
  older-dated posts already in the JSON — and the audit the user
  ordered ("check the actual in game text and code") showed why:
  the drift was in the shipped game itself. 375 of 381 date
  stamps said 1996; the engine hardcoded "Memorial Day · 1996"
  and "Labor Day · September 1, 1996"; whole back-porch threads
  discussed Quake and the N64 as new releases. The spec said
  vol 6's summer all along, and one reply (hasslein calling The
  Frighteners "Peter Jackson before the Rings") was already
  written from the retrospective frame. Self-reinforcing wrong
  dates recruit every future session into the error — audit by
  tallying date fields, not by sampling threads.
- **The 2026 sweep, for the record.** 337 current-summer stamps
  shifted 1996 → 2026 (minus two days keeps the weekday for
  Mar–Dec dates; Memorial Day Mon May 27 '96 lands exactly on
  Memorial Day Mon May 25 '26). Deliberately-archival posts
  kept their dates: the attic's memorial threads (1990–2004),
  the MAINSTREET Jan '96 welcome sticky, the barn's 1981
  binding sticky — the archive is *supposed* to be old; only
  the present moved. Period-culture threads (BP_001 Quake,
  BP_002 Fargo, BP_007 Mario 64, BP_008 movies-of-'96)
  converted to 30th-anniversary retro framing in the same
  voices; arithmetic casualties fixed (Aria's eighteenth
  birthday 2000 → 2030, memorial-fund checks since 1994 →
  2020, the Genetec plate reader, the '94 → '24 wooden box).
  A 2026 circle keeping period iron alive on a dial-up BBS
  needed no invention — it was already the spec's
  characterization of the aged-forward roster.
- **The enemy-arc convergence was assembled, not invented.** Every
  element the hidden boards had seeded (the ratchet moved to Aug
  4, the unlogged seventh camera, Filly's closed docket, the
  Mast watch) now aims at the W14 storm — the week the strategic
  game already made its hard branch. RH_006/TG_006/TG_007 carry
  the turn; MS_015/MS_016 echo it on the public layer in
  double-voiced civic prose (the enemy reads mainstreet — write
  both readings on purpose); TB_007 finally uses Table 14 for
  the glossary's built purpose; TB_BAS_015/016 ready the demon
  roster (the cicada goes on record disagreeing, which the spec
  promised). Rule of thumb that held all session: before
  inventing a new arc beat, inventory what the boards already
  planted — convergence written from existing seeds reads as
  inevitability; invented beats read as plot.
- **Universal DM beats must be checked against branch geography.**
  A storm-night beat written for "the kitchen" collided with the
  send_her_away branch, where Aria is at the bungalow — caught
  only because the append script printed the existing week
  numbers. Rule: before adding an untagged beat to a branched DM
  spine, list where every branch physically puts the characters
  that week. The fix was better than the draft: the bungalow
  variant ("there is no distance that keeps her from the
  schedule") is the sharpest of the three.
- **One rare voice beats five regular ones.** Sammy's single post
  (TB_008, the box scores at the two stones) does more for the
  bar than any number of thelma threads because the board spent
  eight threads establishing his silence first. Spend silence
  like a currency.
- **Retro distance beats contemporaneity anyway.** In 2026 the
  bayou-scene games are thirty-year-old objects (chainlinkspiral
  buys NIGHT WALK plus a working Game Boy at a flea market;
  D-MAGNUS translates his own 1994 poster from memory, the
  floppy long unreadable), and that register — patient,
  memorial, slightly haunted — is the one the deck is best at.
- **The network got its history (user direction: the BBS is old,
  late-'80s, still in use by the friends).**
  `_COMMUNITY_PLANNED_BBS_HISTORY.md` reconciles every archival
  stamp into a 1988–2026 timeline: founding October 1988, the
  November 1991 number change the welcome sticky alludes to, the
  attic's 1990 rules, the 1981 barn-sticky stamp left
  deliberately unexplained, the copper refusal, the 2020 origin
  of the register glossary, the friends' arrival years. Method:
  the archive stamps already in canon were treated as fixed
  points and the history written *through* them — nothing
  existing moved. Surfaced in-game as BP_019 (the origin-stories
  thread), where each regular's first-call story doubles as
  their bio.
- **Second-wave threads let the session's two halves meet.** With
  the 2026 frame settled, the slowstick ecosystem exists *during*
  CP: hasslein orders THE PERIMETER · COLLECTED from Bayou
  Receivers and the interpreter writes him an unasked walk that
  ends in a request (CP_007 — rhyming with Frasier's read of the
  substrate instability); the PDP Riffmaster lands on SNACKS's
  counter via a trucker's freebie (SN_006). New original game
  fiction to balance the crossovers: THE TALLY (TL_006), the
  board's own door game since winter '93 — one counted thing per
  call, annual reading the last Sunday of July — now also in the
  history doc. Rule of thumb held: half cross-canon, half new.
- **The BP_ prefix collision was a live bug, caught by writing
  fiction.** the_pit (BEDROCK) used BP_* ids while the_back_porch
  (RUST_CODE) uses BP_001–019, and
  `_has_read_thread_on_bbs("BEDROCK")` credits any BP_-prefixed
  read — so one back-porch read silently satisfied BEDROCK's leg
  of the BACKCHANNEL breadth unlock. Fixed: pit renamed to BT_*
  (storm thread keeps the _004 slot parallel to OH_004/CP_004),
  engine map updated, backchannel cross-ref updated. Also fixed
  two duplicate thread ids (CP_004 sage → CP_006, pit BP_004 →
  BT_006). Lesson: content sessions should run the id-uniqueness
  check alongside the JSON validity gate — duplicates and prefix
  collisions are invisible until an unlock misfires.
- **Wave three closed the thin-board pass and paid off a planted
  thread.** CK_007 (the hymnal copied for the nursery — "track 31
  is not for the nursery"), DA_006 (LOW TIDE TABLE on the desert
  board: "watch the water go; take only what you can name"),
  OOB_006 (the watching-the-door stranger from OOB_002 wins the
  claw-machine lobster in one drop and doesn't watch the door on
  his way out). Paying off an existing minor-mystery thread beats
  starting a new one — the board reads as a place where things
  continue. The scumm repo's Lore Hub (scumm11.html) was synced
  the same session: slowsticks + network-history concepts,
  documents, and timeline events, JS syntax-checked via node.
- **Wave four: promises kept on the home boards.** BP_020 pays
  off CK_007's "saving my flute opinions for the porch" — the
  full thirty-two-year track-31 argument, closed by a one-line
  reply from a first-time handle ("andrew.": "She was right. I
  couldn't hear it until she moved it."), deniable, unconfirmed,
  exactly the size a canon cameo should be. TW_009 completes the
  slowstick adoption chain (letter → reader build → sticks
  circulating), with Frasier's note that the slot spec predates
  the label — the 2007-box lineage surfacing in-game without
  being explained. Chains > singletons: every wave this session
  planted something a later wave paid off, and the boards read
  as a living place because of it. Check-before-id: the workshop
  listing truncated at 8 of 10 threads and TW_007 was taken —
  always compute the next free id from the full list, never from
  a truncated display.
- **Real-calendar dating discipline.** Check new thread dates
  against the actual 2026 calendar (Jul 5 / Aug 16 / Aug 23 are
  Sundays). Cheap to verify, ugly to get wrong on a board whose
  sysops post tide tables.
- **The Kiva stays sparse on purpose.** Its notes say two posts
  a season is the cadence — a thin board is not automatically an
  under-populated board. Read the board notes for the intended
  cadence before applying the "thinnest boards first" rule.

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
