# COMMUNITY PLANNED · Phase 3 Scope · The Dramatic Spine

Phase 1 shipped the strategic map + day loop. Phase 2 shipped the
BBS layer — six BBSes, four hidden boards, DMs, the glossary
unlock, the artifact shelf, the queued-burn delivery. The bones
are in. The game is playable end-to-end mechanically.

What it doesn't yet have: a **dramatic spine**. The summer runs
its 100 days and then ends. There's no W11 Aria moment, no W14
storm coordination, no Labor Day finale that binds what the
player carried in their hands all summer.

Phase 3 is that spine.

## What phase 3 ships (the contract)

Once phase 3 lands, a complete playthrough Memorial Day → Labor
Day delivers:

1. **The W11 moment.** Around day 73-77, the sysop circle's coded
   vocabulary stops being coding and becomes an explicit ask.
   Nicola, through one of her standing surrogates, surfaces what
   has been quiet protective work all summer: Aria is fourteen,
   the third visits more often now, and the family needs to
   decide whether the binding from 1981 still holds. The player
   makes a multi-choice decision with consequences that ripple
   through the last three weeks. This is the only DM choice in
   the summer that gates an interlude shelf section by itself.
2. **The W14 storm.** Around day 91-95, a tropical system south
   of the keys becomes the storm. STEEPLE posts the tide table on
   Wednesday. The other sysops play their established roles per
   `the_backchannel/TC_005`. The cathedral basement becomes the
   inland relay. The player coordinates: a small flurry of cross-
   BBS posts, a real cover/burn tradeoff if the storm comes
   north, JF on the boiler, T. running the storefront alone. If
   the player has been doing the work all summer, this is the
   payoff turn.
3. **The Labor Day finale.** Day 100. The shelf binds. The tower's
   final state is read. The cookout at the storefront actually
   happens (MS_008 from sprint 2 was a save-the-date; now it's a
   beat). Each canon human delivers a closing line. The player
   sees the run's earned interludes laid out in chronological-of-
   when-earned order. Then the credits-style epilogue per the
   final-state branch the player landed in (bright tower / dim /
   dark / white).
4. **Small Wood and Harmony Creek as real regions.** Currently
   they exist in `_regions` but the strategic map doesn't render
   them with the texture Graustark has. Phase 3 ships at least
   one weekly cadence and one named human in each so the regions
   feel like places, not labels.
5. **The post-summer outro.** A short transition screen that
   names what the player carried out of the summer (the artifacts,
   the canon facts, the friendships changed) — the through-line
   to whatever vol6-era content reads this state.

## Work units (sized vs phase 2's 12)

- **U1 · The W11 Aria DM thread.** New canonical DM thread:
  `dms/aria_through_nicola.json`. Available from W11, eight beats
  pre-decision, the decision itself as a 3-way choice, two beats
  post-decision per branch. The choice writes
  `_canon_vars["aria_w11_choice"]` and sets a section flag on the
  interlude shelf.
- **U2 · W11 supporting threads.** On RUST_CODE / SNACKS / CALICHE
  the W11 question gets reflected — at least 2 new threads per
  board that name the moment in the appropriate register without
  spoiling the choice. `MS_009`, `SN_005`, `CB_003`, etc.
- **U3 · Aria interlude shelf section.** New section
  `aria_summer_w11_interludes`: 6 interludes, two per choice
  branch. Earn predicates key off `_canon_vars["aria_w11_choice"]`
  + downstream flags.
- **U4 · The W14 storm engine event.** New event kind:
  `weather_event`. Storm rolls (deterministic by day 91 every run,
  not random — this is a beat, not a chance). The event:
  spawns a `cathedral_basement_relay` problem requiring the
  player's full attention; affects cover/burn budget for the
  week; surfaces a new BBS night with cross-BBS coordination
  threads pinned at the top.
- **U5 · W14 storm content.** Cross-BBS coordination threads — one
  per BBS, all dated within the storm window, all keyed off the
  W14 backchannel post (TC_005). Plus storm-watch DMs from JF
  (boiler), T. (storefront), Elicia (bungalow line down),
  Mackenzie (asking if she can help, finally).
- **U6 · Labor Day finale state computation.** Determine which
  ending branch the player earned: tower brightness, shelf
  composition, Graustark cover status, queued-burns remaining,
  W11 choice. Encode as a deterministic branch id.
- **U7 · Labor Day finale screen.** A real closing screen
  (Control, not just log). The cookout illustrated in flat
  vertex-color geometry per the locale pipeline; named lines from
  each canon human; the artifact shelf laid out; the earned
  interlude titles in order; the credits-style epilogue text per
  branch.
- **U8 · The Aria glossary annotation, deeper pass.** Currently the
  glossary view shows term=canonical mapping. Phase 3 adds inline
  annotation: when reading a thread post-unlock, terms from the
  glossary get rendered in amber with their canonical meaning in
  a footnote at the bottom. Hover/key-toggle.
- **U9 · Small Wood as a real region.** One weekly cadence event
  (the cypress dying schedule, already implied in `the_grove`),
  one named human (the groundskeeper's actual position vs
  Frasier — currently he's a non-canonical enemy poster), three
  to five problem templates that are Small Wood-specific.
- **U10 · Harmony Creek as a real region.** Same shape as U9 but
  for the other quiet region. At least one threadline that uses
  STEAMBOAT_72 as a regular.
- **U11 · Post-summer outro screen.** The Labor Day finale's
  short successor — what the player carried out of the summer,
  rendered as a punch list before returning to the gallery.
- **U12 · Polish + bugfix pass.** Whatever's surfaced during the
  end-to-end playthrough we'll do as the playtest gate before
  Phase 3 declares done. Reserve a sprint slot.

## Sprints (4 sprints, ~3 work units each)

- **Sprint 1 · The W11 spine.** U1, U2, U3. The Aria moment ships
  as the centerpiece. End-of-sprint test: a player who has read
  6+ SNACKS threads by W11 sees the glossary unlock fire,
  receives the Aria DM the same week, picks one of three
  branches, and earns at least one Aria interlude in the next
  three weeks.
- **Sprint 2 · The W14 storm.** U4, U5. The storm-watch becomes a
  real event with cross-BBS content. End-of-sprint test: the
  player reads coordinated threads across all five public BBSes
  in W14 and the cathedral basement relay problem appears on the
  strategic map.
- **Sprint 3 · Labor Day + outro.** U6, U7, U11. The summer ends
  with a real screen. End-of-sprint test: hitting day 100
  triggers the finale; the player can read every interlude they
  earned; the outro screen names the through-line.
- **Sprint 4 · Regions + polish.** U8, U9, U10, U12. Small Wood
  and Harmony Creek become real, the glossary annotation gets a
  second pass, polish whatever the playtest pass surfaced.

## Pre-work checklist (before Sprint 1)

- [ ] Decide the three Aria W11 choices in narrative terms. (My
  proposal: *re-bind* — explicit, costs cover, the family
  reconvenes; *let her hold it* — trust Aria's interior work,
  costs nothing now but escalates the third's presence; *send her
  away* — to the bungalow with Elicia, costs continuity with
  Nicola but isolates the third.) User to confirm or redirect.
- [ ] Decide whether the W14 storm has a "soft" version (it goes
  east, the keel-keeper called it right) and a "hard" version
  (north of the keys, the cathedral basement relay actually
  fires) — and what gates which. My proposal: deterministic
  hard if the player has been reading THE_BACKCHANNEL, soft
  otherwise. Inverts the usual reward → harder is the reward
  here.
- [ ] Decide whether the Labor Day finale is purely declarative
  (read the run's record) or has one last choice (e.g. what
  Frasier writes in the parish ledger on his way out the
  cathedral office for the summer). My proposal: purely
  declarative. The summer was the choice-making.

## Out of scope for phase 3 (deferred)

- A vol6-side reader of the run state. Phase 3 ships the data
  (`save.json` carries everything); a future phase reads it from
  the novel side.
- Localized voice acting / music. The post-process audio
  (DialupToneSynth) covers the BBS night; the strategic side stays
  on the existing music track.
- The interlude-to-prose pipeline (turning unlocked artifacts into
  readable text in the gallery). Listed in the phase 2 scope doc
  as also deferred; remains so.

## Success criteria

Phase 3 declares done when:

1. A clean playthrough Memorial Day → Labor Day takes the player
   through W11 (Aria choice), W14 (storm), and Labor Day (finale).
2. The shelf at Labor Day has at least 10 entries and at least one
   from each section.
3. Small Wood and Harmony Creek each show at least one weekly
   event and one named human across the summer.
4. The W14 storm's hard branch is reachable.
5. F4 still hides every HUD layer including the finale screen's
   debug overlay.
6. Save load is forward-compatible from phase 2 save schema.
