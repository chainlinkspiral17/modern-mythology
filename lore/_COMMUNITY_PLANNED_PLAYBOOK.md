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

## Lesson capture cadence

After every work session that touches Community Planned and
involves more than 3 commits, an aesthetic decision, or specific
user feedback, append a dated entry to **Recent lessons** below
using the template at the bottom. Lessons graduate up to **Core
rules** once they've held across multiple sessions.

---

## Recent lessons

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
