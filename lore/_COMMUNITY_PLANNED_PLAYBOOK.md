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
   across sessions — this supersedes the earlier 2025 ruling the
   Deck line worked from (2026-08-04; reconciled at the
   2026-10-16 merge, when every live 2025 stamp was shifted onto
   the 2026 grid). The calendar: Day 1 = Memorial Day =
   **Monday, May 25, 2026**; the Labor Day cookout finale =
   **Sunday, September 6, 2026**. Any pre-2026 date stamp you
   find now is *deliberate archive texture* (the attic's
   memorial threads, the MAINSTREET '96 welcome sticky, the
   barn's 1981 binding sticky) and must be left alone. The
   boards themselves are old — RUST_CODE since 1991, SNACKS
   since 1992, BEDROCK since 1993, CALICHE's binding sticky
   since 1981 — and the dial-up anachronism is DIEGETIC:
   Frasier's circle keeps the old network alive on purpose.
   Fixed points (year-anchored, present-independent): Sinkhole +
   Dante · October 2004. Pop dies · November 2023 (funeral,
   inspection roster, JF's box for Aria, transitions sit in
   2022-2023). Boathouse fire · 2022. First Faith (the dog) dies
   2013; Cicada arrives 2016. Aria is fourteen in the game
   summer (b. ~2012, eighteenth birthday 2030 — the
   D'Ambrosio Aria; never merge her with Aria Dean, see
   `_MASTER_TIMELINE.md`). The back-porch regulars have been the
   same found family since the mid-nineties — their '96 talk is
   memory with receipts, never present tense. Real-world facts
   land as-is (Lynch died January 2025; Elliott Smith 2003; the
   BayBears left Mobile 2019). The bayou-scene games and BBS-era
   culture (1985-2004, see
   `planned_community/digital_subculture.md`) appear as
   decades-old retro objects — never as new releases. NEVER
   author a new post that treats the nineties (or 2025) as the
   present.

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
4a. **Staged templates must pass the effort audit.** Sum of each
   stage's maximum ungated effort_applied must be ≥ 0.95 ×
   effort_to_resolve, or the template is unwinnable for a blind
   player (and if even the gated max falls short, unwinnable for
   everyone). The 2026-08-14 audit found 10 of 22 staged
   templates impossible — including the relay, by 0.1. Audit
   one-liner: sum stage maxes vs the threshold before commit.
   Sanctioned exception: the_august_event, where ungated max
   deliberately fails a single attempt (the enemy beats the
   unprepared) but gated max passes and staged progress now
   persists across dispatches, so blind players can brute-force
   a second dispatch at double agent-cost.
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

## Design note · ENDLESS V2 · THE APPRENTICE — 2026-08-31, BUILT same day

m7 ("somebody asks to learn the board") and m11 ("the successor
question") narrated succession; this mechanizes it.

**THE ARIA RULE (user correction, 2026-08-31 · canon-wide):** Aria
is a messiah-like, trans-dimensional figure — fourteen in CP's
2025, Nicola's daughter, the wooden box, the W11 thread, the crow
in vol 7. She is the thing the board orbits, never its staff.
NEVER cast Aria in a mundane role (apprentice, employee, errand
runner) anywhere in the catalog; her cameos stay uncanny (the
dial-up vignette is her LISTENING to the substrate, not a career
interest). The first draft of this mechanic miscast her; recast
same day.

The apprentice is **MAYA DAIGLE** (user casting) — vol6's
comic-shop kid from the Estates, Linda Caldwell's granddaughter,
the one F.T. brought in directly the summer everything ran
through four teenagers and a corkboard, who asked Rick the
question that was always going to become this mechanic: "can we
help him. sometime. after this." It's after this. She knocks at
endless week 10:

- **The offer** (ConfirmationDialog, Sunday): hand her the pencil,
  or "not yet" — declining re-offers every 8 weeks. Some questions
  keep Sunday hours.
- **Training (4 weeks):** lesson lines in register, and a 25% weekly
  chance of a MIS-ROUTE — one random problem +1 severity. Teaching
  costs the board something; that is the mechanic saying so.
- **Graduated:** every Sunday she takes the board's smallest
  problem (severity ≤ 3, nobody dispatched on it) — resolved with
  her own resolution lines, counted in the ledger like any other.
  The ≤3 ceiling is calibrated: the probe proved a 2.0 bar meant
  she never found work (everything ticks past 2 by Sunday).
- **THE HANDOFF:** retire with ≥16 apprentice-weeks and the ending
  changes — "You set the pencil down. She picks it up before it
  stops rolling." Third ending alongside THE BOARD RETIRES and THE
  TOWER FINISHES; ledger reason "handoff", apprentice-weeks lined.

Data in endless_milestones.json under "apprentice". Probe:
tools/qa/ApprenticeProbe.tscn (pins the tower dim to watch the
mechanic; seeds one honest small problem on the full board).

**Two balance findings the probe forced:** (1) severity was
UNCAPPED — a neglected endless board carried problems at severity
65-190, since regions cap at 4 actives, spawns stop, and the
ancient four tick forever. Severity now caps at 9 (highest
authored threshold is 6; nine reads as "as bad as it gets").
(2) A full board starves the apprentice honestly — she needs
fresh spawns to have small ones to take, which rewards the player
keeping regions unclogged. That's the mechanic teaching the mode's
own lesson.

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

## Design note · THE COUNTY SEAT — 2026-07-19, BUILT same day

The LLC-golf-course thread (buyout_letters → the_charter_review →
the_census_stranger's rental lot) pointed at one place from three
directions; this makes it a place. A FOURTH REGION whose problems
are the COUNTERPARTIES — the palette is offense, not defense.

- **Region** `county_seat` · role "offense" · the only region
  where we hold almost nothing at start (one node: the public
  records reading room — the beachhead). Target nodes are the
  law office, the review committee room, the LLC registry desk,
  and the county paper's morgue. Modest yields; escalation clock
  slower (bureaucracy escalates by calendar, not mood); a small
  demon corruption tick (paper is its own binding — demons hate
  certified mail).
- **Palette** · five new problem types, all offense-shaped:
  `records_request` (FOIA the LLC's paper trail) ·
  `filing_deadline` (their motion, our response clock) ·
  `countersuit` (the sev-5 chain-starter · lose it and it
  escalates Graustark from a distance) · `public_comment_period`
  (pack the room, politely) · `registry_pull` (who actually owns
  Fairway Meadows LLC · the answer is a matryoshka).
- **Reveal** · day 66, `region_opens` + `enable_problem_type`,
  seeded with `the_records_request`. Late campaign by design —
  the player has spent nine weeks defending; the doors open right
  when they've learned enough to attack. Endless mode force-opens
  it (`SEPTEMBER AND AFTER` includes the courthouse).
- **Engine** · one save-compat backfill (region_state entries for
  regions added after a save was written) — the agents.json
  lesson, applied to regions. Banner added to the pass-10
  generator (limestone courthouse at dusk, one office lit late).

## Lesson capture cadence

After every work session that touches Community Planned and
involves more than 3 commits, an aesthetic decision, or specific
user feedback, append a dated entry to **Recent lessons** below
using the template at the bottom. Lessons graduate up to **Core
rules** once they've held across multiple sessions.

---

## Recent lessons

### 2026-10-16 · the deck merge · two presents, one grid, union by id

- **The Deck line and the fiction line disagreed on the game's
  present (2025 vs 2026).** Ruling: 2026 (user, repeatedly). All 82
  live 2025 stamps in Deck-authored threads/DMs shifted -1 day,
  year→2026, preserving the named weekday; the Deck's fixed-point
  lattice (Sinkhole 2004, Pop d. Nov 2023, boathouse fire 2022) is
  year-anchored and survived intact. See Content discipline rule 0.
- **Merging two board JSONs is a union by thread id, never a
  pick-a-side.** Ours wins on a shared id both sides changed (the
  2026 sweep + enemy arc); theirs is adopted when new or when ours
  matched base; a theirs-id that equals base but is gone from ours
  was our deliberate rename — skip it, or the rename comes back as
  a duplicate (the pit's BP_/BT_ pair did exactly this).
- **Prefix collisions ride in with adopted boards.** The Deck's new
  THE_ART_WALL took TA_ while the attic already had it; the attic is
  now AT_. Before adopting any board, check its prefix against the
  global id set AND the engine's `_has_read_thread_on_bbs` map.
- **The Deck's 19 staged templates are multi-dispatch problems under
  the staged-persistence fix** (stage_index resets per dispatch, so a
  re-dispatch re-applies the stage while effort_remaining persists).
  Best-pass effort 1.2-2.0 against needs of 1.9-6.65 means 2-4
  dispatches per problem — winnable now, mathematically dead on the
  old per-dispatch accumulator. Audit new staged templates as
  ceil(need / best-pass) dispatches, not one.

### 2026-08-19 · the FRAME LINES are the voice (user: "robotic and sterile")

- **User verdict from play testing: the voice of Community Planned
  is "robotic and sterile and kinda off putting."** The diagnosis:
  the flavor pools were literary but the FRAME lines around them —
  the strings the player reads every single turn — spoke strategy-
  game telemetry. "Day 34 · Ruth resolved Well Contamination in
  Harmony Creek." "ON DISPATCH · returns day 41." "Dispatches
  today: 2/3." A hundred good flavor paragraphs cannot outweigh a
  thousand telemetry lines; the frame IS the voice.
- **The register is Frasier's pencil.** He is an old man keeping a
  summer in a ledger. Rules that held: declarative sentences;
  concrete objects over abstractions (roads, the porch, the
  pencil, a line through it); the numbers STAY (they are gameplay
  information) but they arrive inside a sentence a person would
  write; dry-dark understatement over exclamation ("It will
  keep."). Examples now in the engine: dispatch = "takes the road
  out to X. The pencil says back by day N." · success = "came
  home. X is settled — a line through it in the ledger." ·
  failure = "came back without it. X stands." · resting = "ON THE
  PORCH · day 2 of 3" · cap = "The day carries 3 roads and they
  are all taken. Tomorrow is a day too."
- **All 40 problem templates now carry resolution_flavor_success /
  _failure.** The eight that were silent were the County Seat
  legal cluster — the paperwork problems, which turn out to be the
  best register in the game (clerks, stamps, footnotes, the
  matryoshka LLC). Legal process is a VOICE, not a spreadsheet:
  "Sympathy is not jurisdiction." "Everything is discoverable.
  Everything was always discoverable."
- **Developer-speak inside the fiction is a defect class.** The
  slowstock stub screen said "Playable acts are a follow-up
  commit" — repo vocabulary inside Olaf's television. Now the
  cart is "out on loan" and the case faces the room "so the shelf
  remembers the shape of the game." Grep for it: commit, TODO,
  authored, playable, placeholder, implemented — none of these
  words belong in any player-facing string, ever.
- **The day loop must never go silent.** All 65 daily vignettes
  were one_shot — the pool drained around day 80 and NOTHING fired
  after, which is exactly late summer (peak pressure) and all of
  endless. The fix is canon: the Memorial Day preamble says "Read
  the quiet too. The boiler hums two semitones flat." A RHYTHM
  POOL (vg_rhythm_*, one_shot:false) now carries the pulse — the
  same bell, the same rounds, the same boiler — because a rhythm
  is the thing that repeats. Events outrank the pulse 3-in-4 while
  they last; the _last_vignette_id guard stops back-to-back
  repeats. Rule: any flavor pool that fires on a clock needs a
  never-exhausted floor under its one-shots.
- **The exhaustion audit generalized (2026-08-19).** Applying the
  vignette lesson to every clock-fired pool found two more holes:
  the weekly regional flavor exhausted into ONE static line
  ("the region held its shape this week") repeated verbatim every
  remaining Sunday — harmony_creek's 11 one-shots die before
  Labor Day, and endless mode got the same sentence forever. And
  COUNTY_SEAT had ZERO regional events: every Sunday since the
  region opens, the fallback. Fixed with per-region RHYTHM pools
  in regional_events.json (the engine avoids repeating last
  week's line) and eight county_seat one-shots in the legal
  register ("Clerks are the last neutral country"). The rule,
  now firm: EVERY pool that fires on a clock gets a
  never-exhausted floor, checked at authoring time.
- NEXT voice draft: the stage-choice `summary` strings (still
  "+1.0 effort · slow, attentive · no cost" — the numbers should
  stay but the framing can breathe), region-panel chrome, the
  gauntlet's system strings, and a per-stick sweep of slowstick
  system text against the same leakage grep.



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
- **The first-run difficulty audit: verify the math, not the
  vibe.** The user's playthrough feel ("nothing sticks") was
  confirmed by arithmetic: staged resolution summed only stage
  effort vs 0.95×target with no persistence, making 10 of 22
  staged templates unwinnable. Fixes: staged success now keys
  off the problem's effort_remaining (progress persists across
  dispatches); 11 templates retuned to the ungated-max
  principle; the stage modal now shows "effort X of ~Y needed"
  so failure is legible. Rule graduated to Content discipline 4a.
- **The Filly ruling (author): one Filly, both envelopes.** The
  roster courier and the grove's un-binding specialist are the
  same demon — a freelancer who "goes where the contract is,"
  the office included, and the circle has always known.
  Mechanics: she leaves the roster for the W14 storm window on
  both branches (return_day extended, never shortened). Canon
  surfaces: agents.json flavor, the lintel stage body, and
  TB_BAS_017 — her after-the-week basement quiet ("I billed for
  the night either way") with Frasier's reply: "The drawer is
  still yours. It always was." A mercenary the player relies on
  and the enemy hires is more interesting than two names.
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

### 2026-08-09 · the electronic register reaches the stages + the basement

- **The demon quiets in THE_BASEMENT were still embodied** — walking
  patrol lines, sitting under dock planks, warming on porch steps.
  Rewrote all six in the electronic register while keeping every
  beat and the "X was X / the rest is the rest" cadence: the_vagrant
  rides the copper and rings a doorbell soft to say evening;
  sideways-current holds in the depth sounder; the_moth lives in
  the bulb's circuit and knows the wattage FROM THE DRAW;
  coat-inside watches the desk camera; fresh-second-suitcase gets
  Elicia's newsletters scanned to it page by page on the office
  fax. Frasier's own posts keep their physical idiom — he is human,
  and "the room" is what anyone calls a board.
- **Stage bodies are per-class now.** `body_demon` (schema:
  `body_<class>`, additive, base `body` is always the fallback)
  overrides the modal body when the dispatched agent's class
  matches. Twelve stages whose base bodies parked, sat, and walked
  {agent} now have demon variants that ride cameras, hold in
  fluorescents and PAs, and — the honest limit — CANNOT lift a
  staple or carry flowers past the cemetery gate, which the
  variants say out loud. The class's limits are content, not bugs.

### 2026-08-04 · the 2025 re-anchor + Faith II + electronic demons + presentation

- **The game's present is 2025; check every new line against the
  fixed-point table in Content rule 0.** The BBS shipped an entire
  coherent summer of 1996 — 377 dates, Quake-as-new, Aria's
  birthday in 2000 — against a strategic layer that said Cicada
  2016 and Faith dead in '13. Cross-layer date drift is invisible
  from inside either layer; only the fixed-point table catches it.
- **Re-anchoring content the user loves means aging it, not
  replacing it.** The back-porch threads kept every beloved beat
  (the Tomb of Horrors line, the teleport-counter, 'the window for
  this trip is the window') by becoming the same room 29 years on:
  anniversary rewatches, receipts held since '96, elegies. Time
  passing IS material — chainlinkspiral's dad in past tense does
  more work than the original present tense did.
- **A species is a register.** Faith II drifted human because
  'runs the register' is the path of least resistance for a named
  character at a counter. The fix that keeps the charm is dog-verb
  substitution (guards the pad, catfish skin under the table, in
  charge of the closed register), not deletion. Same rule now
  applies to demons: electronic, on their plane, touching the
  parish only through powered infrastructure — never in chairs,
  cars, or diners (agents.json notes carries the rule).
- **When canon changes what a class IS, the art must follow.**
  Demons became electronic; their VnBustPortrait faces became
  lies. Procedural sigils (per-id glyphs in the class violet)
  replaced them the same day. Prose canon and render canon drift
  independently — patch both in one commit.
- **Every problem type now carries a stamp.** 96x54 HeroImages
  from gen_cp_problem_stamps.py, shown in rows, dossiers, and the
  dispatch picker. Same discipline as banners: deterministic
  generator, missing-file null cache, render-only.
- **Type floor at couch distance is ~15, not 12.** The 12 floor
  from 2026-07-10 was still 'far too small for the screen real
  estate.' 104 sites rescaled +25% (15/16/17/20/22).
- **CP music is four tracks deep now** (drafting table / phosphor
  night / tower watch / labor day dusk) rotating weekly with the
  vol5 beds; the tower gets its own unresolving piece and the
  finale gets the only track allowed to end.

### 2026-07-19 · County Seat + pair dispatches + Dean's Ledger

- **Ride the primary's record, don't duplicate the machinery.**
  Pair dispatches could have meant a parallel _dispatch_pair copy
  of stages/undo/revoke/resolve. Instead the partner is a RIDER
  on the primary's dispatch record (pair_agent_id + extended undo
  snapshot), with three small patches where the record is
  consumed (revoke, resolve, breather). New feature, near-zero
  new surface area for bugs.
- **A refusal is content.** Ruth appears in the partner picker
  specifically so she can decline — the 'Ask anyway' button
  exists to deliver one line. The cheapest characterization on
  the board is a NO with a voice.
- **Deepen an existing earn-ladder instead of a new system.**
  Dean's Ledger is the fingerprints-≥5 rung above the existing
  napkin at ≥3 — one match arm, one seed, and the counter the
  player was already accumulating suddenly has a payoff curve.
- **Hand-formatted JSON stays hand-formatted.** dean.json,
  reveals.json, regions.json, endings.json, PS scrapbook — none
  round-trip through json.dump. The surgical-append pattern
  (render entry, indent to match, insert before the array close,
  re-parse to verify) is now the house method; diffs stay
  append-only and reviewable.

### 2026-07-19 · between-spike events + roster growth · one machine, two features

- **Choice events and recruitment are the same machine.** The
  between-spike event engine (windowed one-shot choice modals,
  effects interpreted against existing verbs) shipped for
  mid-summer texture — then roster growth cost only ONE new
  effect verb (`agent_arrives`) and three authored events. When
  adding a system, spend an extra hour making its effects
  vocabulary data-driven; the second feature rides free.
- **Effects ride existing verbs ONLY.** Escalation deltas,
  _seed_problem into real templates, queued burns, log lines,
  reveal-style agent arrival. No new mechanics entered the game;
  six events + three recruits are pure data. Cross-validate every
  id (region, template, agent, trait) in the same commit.
- **New agents must backfill _agent_state.** Saves written before
  a roster addition restore an agent_state dict without the new
  ids; the arrival verb creates the state dict inline (same shape
  as the boot init). Any future roster addition needs the same
  guard or old saves crash at the dossier.
- **Tradeoffs live entirely in the existing schema.** Brilliant-
  but-brittle is competence 1.8 + obligation 2 + cap 3. Reliable-
  but-slow is 0.9 + cap 7 + travel 2.0. Fast-but-public is speed
  1.4 + burn 2 + low resistance + press failure_effects. If a
  tradeoff needs a new field, simplify it until it doesn't.

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

### 2026-09-19 · the masthead in the zine's hand; a letter that answers a beat

- **A masthead is a register claim.** Figlet block capitals say "a
  BBS, 1991, anyone's". RUST_CODE hosts the zine's letters column,
  so its masthead is the zine's: lowercase, letterspaced, two ruled
  lines, a subtitle in m.d.'s voice, and the risograph joke (two
  inks you can't see from here — the terminal is green). The other
  five boards keep their own hands; only the zine's board changed.
- **A reader letter can answer the book.** The VN's `[trip:]` beats
  are the community's dawn as prose; a letter that disputes one
  (6:12, not 6:15; the cracked head is the association's) makes the
  zine and the chapter the same town. Author it to the pressure curve
  (W4: long, a grievance with a grace note), and let the editor's
  reply be the correction printed — the zine's only verb.
- **Thread shape:** copy RN_001's keys exactly (id · subject ·
  available_from_week · sysop_tagged · op{handle, canonical_character_id,
  date, body} · replies[]); splice the object after its neighbour in
  the file by raw text and validate with json.loads. Ids need not be
  in file order; the week is what the board sorts by.

### 2026-09-07 · the letters column (game grammar row 2)

- **A zine's letters column IS a board.** THE_LETTERS on RUST_CODE:
  the reader's letter is the OP, the editor's lowercase reply is the
  first reply, the sysop drops in when the board's history is the
  point. Nine threads authored to the pressure curve — long by W6,
  three lines in the W13–14 storm window, easing by W16 — so the
  summer's tempo is legible in the letters' LENGTH before it is
  legible in their content.
- **Prefix `RN_`.** RUST_CODE threads are not in the breadth-check
  prefix map (breadth counts the OTHER five BBSes), so a new local
  board needs no engine change. Any new EXTERNAL board does.
