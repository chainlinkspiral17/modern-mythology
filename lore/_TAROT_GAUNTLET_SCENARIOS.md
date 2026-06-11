# TAROT GAUNTLET · SCENARIO + HAND + LOCATION SYSTEM

*Final Girl-style mix-and-match. Pick a HAND (upright arcana,
action card set), a LOCATION (reversed arcana, destiny deck), and
a SCENARIO CARD (one of three plays for that location). Each
combination is its own play. Win-streaks unlock new items per
location and new action cards per hand.*

*Parent doc: [`_TAROT_GAUNTLET.md`](_TAROT_GAUNTLET.md).*

---

## The model, in one breath

Final Girl ships boxes of (Final Girl × Killer × Location). The
Tarot Gauntlet ships boxes of:

| Component | What it is | Tarot side |
|---|---|---|
| **HAND** | a playable character with an action-card set + ultimate | UPRIGHT arcana |
| **LOCATION** | a board + destiny deck (gravity cards + finales) | REVERSED arcana |
| **SCENARIO** | one of three setup cards per location — different starting state, schedule, win twist | per-location variant |

A run is **HAND × LOCATION × SCENARIO**. The hand's upright
arcana and the location's reversed arcana don't have to match;
that's the point. John Frank (Fool upright) can play in Frasier's
warehouse (Magician reversed) and the run becomes "the Fool
testing himself against the Magician's failed assembly." Frasier
(Magician upright) can play in D'Ambrosio's diner (Fool reversed)
and the run becomes "the Magician arranging things in a room
that wants nothing arranged."

Most arcana are FIRST encountered as a location (the box you
buy, the destiny deck you play against). They become PLAYABLE as
a hand only after you've cleared their location at least once —
you can't carry the Magician until you've understood his shadow.

---

## Component anatomy

### A LOCATION provides:

1. The **board** — spaces, adjacency, attractors, threshold spaces
2. The **destiny deck** = Gravity deck + Finale cards, themed by
   the REVERSED arcana
3. The **Inertia / tension stat** rename (each location's stat
   has a flavor name)
4. The **win condition** the scenario card pins to
5. **Visitor roster** that arrives during play (some on board at
   start, some scheduled, some conditional)
6. **Item piles** at search spaces — half the items are universal
   to that location, half unlock from completed runs
7. **Scenario cards** — three variants per location

### A HAND provides:

1. **Character meeple + portrait**
2. **Action card set** (~10 cards) themed by the UPRIGHT arcana
3. An **Ultimate** — one-shot powerful card, name + flavor
4. A **starting hand** that draws from the framework 11 plus
   their unique cards
5. **Carryover unlocks** — cross-arcana items their previous
   completions made available

### A SCENARIO CARD provides:

1. **Title + subtitle** (the specific play, e.g. "THE LEAP /
   Between Acts · 3:47 AM")
2. **Setup variant**:
   - Player starting space
   - Starting Time / Inertia
   - Which visitors are on board at start vs. scheduled vs.
     conditional
   - Which thresholds are visible from the start
   - Any items pre-placed in inventory (e.g. "you start carrying
     the cassette spine — but the till is already empty")
3. **A scenario-specific twist** — a flag the engine reads. E.g.
   "the bar is OPEN tonight" toggles a normally-closed space
   to active

---

## LOCATIONS · sketched (10 listed, 3 in detail)

### L0 — D'AMBROSIO'S DINER  (Fool Reversed)

> *3:47 AM. The 24-hour diner of the soul. Inertia is the
> shadow — the urge to wipe the same spot of formica for another
> twelve years.*

- **Destiny deck**: the existing 12-card Gravity deck (THE
  CLOCK HOLDS, WIPE THE SAME SPOT, etc.) with 3 endgame at
  the bottom
- **Tension stat**: INERTIA (0-12)
- **Finales** (three reversal states): WIPE THE SAME SPOT
  FOREVER / 24-HOUR DINER OF THE SOUL / THE EMPTY ROOM
- **Board**: 23 spaces, three thresholds (Parking Lot / River
  Window / Precipice Door)
- **Search piles**: Kitchen Alcove / Booth 6 / Under Counter /
  Pay Phone / Card Wall / Register / Jukebox (reusable tracks)

#### Scenarios at this location

##### L0.S1 — THE LEAP  *(canonical, built)*

> 3:47 AM. Cloth in hand. Bindle to assemble. Leap by dawn.

- Starting state: counter, Time 6, Inertia 0, Health 5
- Hand starting deck: walk / focus / search / short_rest /
  wipe_counter / address_the_bell
- Visitors on board at start: stranger (Booth 6), Faith (Under
  Counter)
- Visitors scheduled: Frasier (T3 → Counter), Dawn Cook (T5 →
  Kitchen Alcove), BBS Caller (T6 → Register)
- Win: BUNDLE assembled + 3 connections + Faith adjacent +
  Inertia < 7 + at threshold → play LEAP

##### L0.S2 — THE SHIFT CHANGE  *(new — alternate setup)*

> 5:42 AM. The cook is here already. Dawn is bleeding into the
> windows. You've already wiped the counter eight times. The
> stranger is gone but the booth is still warm. Frasier is
> outside, undecided about coming in.

- Starting state: counter, Time 4 (less budget — the night's
  half-over), Inertia 4, Health 4
- Hand starting deck: same as Leap but +1 starter copy of
  WIPE COUNTER (the muscle memory is deep)
- Visitors on board at start: dawn_cook (Kitchen Alcove —
  arrived BEFORE you got the chance), Faith (Under Counter)
- Visitors scheduled: Frasier (T2 → Parking Lot — he might
  not come in), BBS Caller (T4 → Register)
- Conditional: stranger (already left — their cloth is on the
  table at Booth 6, untouched, no warmth)
- Twist: PARKING LOT threshold starts CLOSED (Frasier's car
  is blocking the door); opens when Frasier connects or
  leaves
- Win: same shape but you can't connect with the stranger
  through SIT WITH (already gone) — must take the cloth
  from Booth 6 + visit Card Wall (composite connect)
- Flavor: a softer, more wistful run. You're not racing
  toward the leap; you're realizing it's still possible at
  the end of the shift.

##### L0.S3 — THE BLACKOUT  *(new — alternate setup)*

> The power's been out for forty minutes. Lights run on the
> jukebox's battery and one fluorescent over the booth at the
> back. The phone doesn't work. Visitors are coming in for the
> warmth and the candles you didn't know were under the
> counter.

- Starting state: counter, Time 5, Inertia 6 (started high —
  the dark makes the room feel heavier)
- Hand starting deck: walk / focus / short_rest / wipe_counter
  / address_the_bell (no SEARCH — you can't see)
- Visitors on board at start: stranger (Booth 6), Faith (Under
  Counter), dawn_cook (Bar Stools — came in for the warmth)
- Visitors scheduled: bbs_caller (T2 → Pay Phone — line is
  dead, they came in person), Frasier (T4 → Hostess Stand)
- Twist: most spaces start UNREVEALED; only the candle-lit
  spaces (Counter, Bar Stools, Booth 4, Booth 6) are visible
  at start. Revealing a space costs 1 Time.
- Special item: under_counter pile has a flashlight added at
  the top — picking it up REVEALS all spaces
- Win: bindle assembled + 3 connections + leap at a revealed
  threshold (PARKING LOT, RIVER WINDOW). Precipice Door cannot
  be revealed this scenario.

---

### L1 — FRASIER'S WAREHOUSE  (Magician Reversed)

> *The diorama studio. Tables of half-assembled model cities.
> Failed assembly is the shadow — components scatter, what you
> placed yesterday is on the floor today. The Magician
> reversed: a craftsman in the middle of unmaking.*

- **Destiny deck**: 12 gravity cards themed on collapse +
  scatter + the table going wrong (THE TABLE LURCHES, THE
  GLUE DRIES, THE LIGHT BURNS OUT, etc.)
- **Tension stat**: DISORDER (0-10)
- **Finales**: SCATTERED FOREVER (everything falls) /
  COLLABORATIVE COLLAPSE (a visitor finishes it for you, wrong)
  / THE LAST PIECE (you place the wrong final element and it
  locks)
- **Board**: 5 rooms (Kitchen / Hallway / Studio / Bathroom /
  Window), plus the Studio's TABLE is itself a sub-board of
  4 element slots
- **Search piles**: drawer (Kitchen) / bookshelf (Hallway) /
  scrap-pile (Studio corner) / medicine cabinet (Bathroom)

#### Scenarios at this location

##### L1.S1 — THE STEAMBOAT ECHO  *(canonical for the Warehouse)*

> The model city has four elements missing. The buyer comes
> tomorrow morning. You haven't slept.

- Starting state: Studio, Time 5, Disorder 2, Health 5
- Bindle equivalent: WATER + EARTH + FIRE + AIR placed on the
  TABLE sub-board (each room has one of them hidden)
- Twist: every PLANNING phase, if you weren't in the Studio
  last turn, one already-placed element has a 25% chance of
  falling off
- Win: all four elements placed + 3 patrons witnessed + you
  finish in the Studio
- Loss: Disorder 10 / two elements simultaneously fall (the
  table's foundation cracks) / the buyer arrives early (a
  fixed-turn threat)

##### L1.S2 — THE FIRE INSPECTION  *(alternate)*

> The fire inspector is in the building. The studio is a fire
> hazard — solvents on shelves, no clear exit, the model city
> takes up most of the floor. You need to make this look like
> a workplace by the time they come up the stairs.

- Starting state: Studio (cluttered), Time 6, Disorder 8 (yes,
  starting HIGH — the room is a mess), Health 5
- Twist: DISORDER must be brought DOWN below 3 by the time the
  inspector visitor arrives (T4). Inspector is a one-turn
  visit; if Disorder > 3 when they arrive, automatic loss.
- Action cards re-weighted toward CLEAN / TIDY / HIDE
- Win: pass inspection (Disorder < 3 at T4) + 3 patrons
  testifying for you + your tools still where you can use them
  (don't tidy everything into oblivion)

##### L1.S3 — THE COMMISSION  *(alternate)*

> A wealthy patron commissioned the centerpiece. They visit
> at 8 PM to approve. You have between now and then to finish
> something they'll recognize as theirs.

- Starting state: Studio, Time 6, Disorder 4
- Twist: the patron's "thing" is one of FIVE candidates (drawn
  randomly each run — a house, a boat, a portrait, a memory,
  a name). You learn which one through visitor interactions
  before they arrive.
- Win: the right element placed + 3 visitors confirming you
  read the patron right + patron approves on arrival
- Cross-arcana hook: if the patron's "thing" is a CASSETTE,
  this run unlocks Elicia's archive overlay

---

### L2 — ELICIA'S ARCHIVE  (Priestess Reversed)

> *Basement tape archive. The shadow is THE URGE TO SPEAK —
> every time you don't answer, the urge rises. Speech corrupts
> the recordings. The Priestess reversed: knowing the truth and
> being forced to say it.*

- **Tension stat**: PRESSURE-TO-SPEAK (0-10)
- **Finales**: SPOKE / WIPED THE TAPE / NEVER FOUND IT
- **Board**: 4 archive rooms + listening room + stairs (threshold)
- **Destiny deck**: cards about voices rising, calls from
  upstairs, an unrecorded sound, etc.

#### Scenarios at this location

##### L2.S1 — THE TAPE  *(canonical)*

> A voice arrives at midnight wanting a specific recording.
> Find it and play it without speaking.

##### L2.S2 — THE OPENING  *(alternate)*

> The archive is being opened to the public tomorrow. You
> have one night to decide which tapes go on display and which
> stay sealed. Three visitors arrive with strong opinions.

##### L2.S3 — THE WIPE  *(alternate)*

> A bag-man arrived with a list of tapes to be destroyed
> tonight. You can refuse, hide, or comply. Each tape has
> a name on its spine you recognize.

---

### L3 — MAYA'S CHURCH  (Hierophant Reversed)

> *Doctrine wears. The shadow is the rite breaking under the
> celebrant. AUDI ET TACE inverted: silence is no longer
> sacred; it's complicit.*

- **Tension stat**: DOCTRINE WEAR (0-10)
- **Finales**: THE WORD BROKE / THE NEXT GENERATION REFUSED /
  THE OLD PRIEST RETURNED
- Scenarios: THE VESTRY / THE WEDDING / THE FUNERAL

### L4 — THE LONG ROAD  (Chariot Reversed)

> *Linear board. The shadow is DOA — the journey ends with
> the driver dead.*

- **Tension stat**: FATIGUE (0-10), uses DRIVING dice variant
- **Finales**: DEAD AT THE WHEEL / WRONG CARGO / NEVER ARRIVED
- Scenarios: THE LONG HAUL / THE SYSOP'S LAST LOG / RUN-AWAY
  CAB

### L5–L9 — sketched only

| L | Location | Reversed arcana | Tension | One-line shadow |
|---|---|---|---|---|
| L5 | The Greenhouse | Empress reversed | ROT | The garden rots faster than you can tend |
| L6 | The Precinct | Emperor reversed | LEDGER | Cases stack faster than you can close them |
| L7 | The Bedroom | Lovers reversed | INDECISION | Two visitors won't align on three choices |
| L8 | The Vault | Strength reversed | STRAIN | Hold what you can't hold |
| L9 | The Cabin | Hermit reversed | LONELINESS | The room empties of meaning around you |

---

## HANDS · sketched (5 listed, 4 in detail)

Each hand carries an UPRIGHT arcana and the action card set
that arcana implies. Hands are unlocked by clearing their
matching LOCATION at least once.

### H0 — JOHN FRANK  (Fool upright)

> *The witness who hasn't yet committed. The cloth in his
> hand has been warm for eleven years. He carries the LEAP
> because nobody else in any of these rooms has been holding
> still long enough to.*

- **Action card set**: WIPE COUNTER, ADDRESS THE BELL, CALL
  FAITH, SIT WITH, SHORT REST, ADDRESS THE BBS BANNER, STEP
  TOWARD, PICK UP, BUNDLE (milestone), LEAP (win card)
- **Ultimate**: TWELVE YEARS — once per run, ignore the next
  Inertia tick AND drop one already-claimed visitor's claim
  marker (the room remembers your tenure)
- **Starting cards drawn**: WIPE COUNTER + SIT WITH +
  ADDRESS THE BELL + plus 3 framework starters
- **Carryover unlocks**:
  - Cleared L0 (Diner) once → unlocks BAR (closed) → BAR
    becomes a search space in subsequent Diner runs
  - Cleared L1 (Warehouse) once → John can carry one already-
    placed element as a starting inventory item
- **Mix-and-match notes**:
  - John @ L1 Warehouse: the Fool's slowness vs. the Magician's
    scattering. SIT WITH becomes a stabilizing action — when
    John sits with someone in the Studio, the table doesn't
    fall that turn.
  - John @ L2 Archive: SIT WITH at the listening room
    bypasses the no-speak constraint (he doesn't talk; he just
    waits with the visitor)
  - John @ L3 Church: WIPE COUNTER becomes a sacrilege action
    if used on the altar — a Fool in a Hierophant's room
    misunderstands what gets cleaned.

### H1 — FRASIER TEMPLE  (Magician upright)

> *Tinkerer. Painter. Sysop. He's traced the lemniscate so
> many times in the air over the workbench that he's done it
> without noticing for a decade. The warehouse demons keep
> the soldering iron warm; he keeps them busy enough to leave
> the rest of the building alone. The Magician upright isn't
> placement — it's the act of HOLDING four contradictory
> things together by a small repeated gesture. Frasier is
> what reality hacking looks like when it's quiet and
> domesticated.*

#### Action card set (the toolkit)

- **SOLDER** — mend any broken thing here (a busted bulb, a
  silent phone, a stuck door); costs 1 Time + 1 Inertia/tension
- **TRACE THE LEMNISCATE** — the infinity loop in the air.
  Once played, the NEXT framework dice fail can be re-read
  as a single success (the gesture re-routes outcome)
- **INVOKE A DEMON** — summon a warehouse demon as a
  temporary visitor. They count as a connection for one
  turn, then DEPART back to the warehouse. You owe them
  one Inertia/tension for use.
- **BIND** — lock a placed item / a visitor / a threshold
  in its current state. Bound things can't be moved by
  Drift, Gravity, or Inertia for 3 turns. (Magician's
  signature: hold the contradictions.)
- **READ THE BBS** — at any terminal-shaped space (REGISTER
  in Diner, MAILBOX in Warehouse, TERMINAL in Archive,
  etc.), peek the next 2 destiny cards
- **HACK THE THRESHOLD** — turn one non-threshold space
  into a threshold for this turn only. The "leap card"
  becomes playable from that space if all other conditions
  are met. One-shot per run.
- **SCATTER** — sacrifice ANY 2 placed/held items to undo
  the last Inertia/tension tick. The disassembly is itself
  a gesture.
- **SKETCH** — at any space, log a lore-token-style note of
  what's here; later runs in this location will reference it
- **GLAZE** — protect one already-placed/bound object from
  the next Drift/Gravity hit (cheaper than BIND, single-use)
- **INVOKE** *(win card)* — the four-element / four-suit
  assembly. Variant per location (in L1 it's the model city;
  in L0 it's arranging the booths into a constellation; in
  L2 it's queuing four tapes; in L3 it's stacking four
  rites)

#### Ultimate · THE FIRST PAINTING

Once per run. Frasier paints what's in front of him —
the painting BECOMES the thing for one turn. Effect:
duplicate any one currently-placed/held element so it
counts as TWO for the win condition. The duplicate
disappears at end of turn but its effect persists.

#### Carryover unlocks

- Cleared L1 (Warehouse): the lemniscate is now in your
  muscle memory — TRACE THE LEMNISCATE gains a second
  charge per run
- Cleared L0 (Diner): unlocks DIORAMA OF THE DINER as a
  table-sub-board variant in L1 — the model city you've
  been working on becomes D'Ambrosio's
- Cleared L2 (Archive): the tape archive is now indexed
  for Frasier — READ THE BBS at any terminal also reveals
  one inventory item visitors are carrying
- Cleared L3 (Church): the rites are partially recorded in
  his hand — INVOKE costs 1 less Time

#### Mix-and-match: Frasier reshading each location

| @ Location | What changes | Why |
|---|---|---|
| **L0 Diner** (Fool reversed) | Inertia falls 1 every time Frasier BINDS a booth or pre-placed item. The Diner is a room he's MENTALLY MODELED for years — fixing things in place runs against the Diner's "wipe forever" shadow. Hosting a visitor at a BOUND space prevents them from drifting. INVOKE win-card becomes "arrange the booths into a constellation that maps the model city" — different geometry, same gesture. | The Magician's verb (hold together) is the natural counter to the Fool's shadow (slip away). Frasier's tools were almost designed for this room. |
| **L2 Archive** (Priestess reversed) | INVOKE A DEMON breaks the no-speak rule loudly — costs +3 PRESSURE-TO-SPEAK. But READ THE BBS replaces LISTEN entirely; Frasier doesn't observe, he queries. SOLDER mends a broken tape on the spot (the Archive has shelved tapes that crackle — Frasier can fix one per run, which Elicia herself never does). | Magician's reality-hacking is incompatible with Priestess's discipline of silence. The friction IS the play. Frasier brings the wrong toolkit on purpose. |
| **L3 Church** (Hierophant reversed) | INVOKE A DEMON is sacrilege — costs +3 DOCTRINE WEAR. But BIND, used on a sacred object, treats it AS the rite (you can shortcut a rite step by binding instead of performing). The bishop will sense it. | The Magician's gestures are pre-religious; they predate doctrine and contradict it. Frasier in a church is a heresy in slow motion. |
| **L1 Warehouse** *(home location)* | Default tuning. Frasier is at home here. INVOKE A DEMON costs 0 Tension (the warehouse demons are his roommates). HACK THE THRESHOLD applies to any of the studio's four walls (a leap THROUGH the painting is possible — and the leap CG is uniquely his). | Each hand has one location where their toolkit costs the least to use. Frasier's is the Warehouse. |
| **L4 The Long Road** (Chariot reversed) | INVOKE A DEMON summons a passenger who will drive a shift for him (skip a Fatigue tick). BIND locks the cargo against damage from rough roads. SOLDER fixes a broken engine on the side of the highway, no shop needed. | The Magician's tools turn a Chariot run into a series of small magical hacks: he doesn't drive efficiently, he makes the drive impossible-to-fail by binding it together. |

#### The Frasier pattern (broader)

His presence in any location *makes the location more
literal*. The Diner's wipe-the-same-spot loop becomes a
literal placement puzzle; the Archive's silence becomes a
debugging problem; the Church's doctrine becomes machine
state to bind/unbind. Frasier doesn't enter rooms — he
*reduces them to gestures he can repeat*. The cost is that
every demon he invokes is one he later has to feed; carry-
over Inertia/tension flows back to L1 Warehouse on his next
visit there. The warehouse is a balance sheet.

### H2 — ELICIA  (Priestess upright)

> *Archivist. She doesn't speak unless she has to. The
> archives speak through her hands instead. She has been
> recording everyone in this gauntlet, and most of them don't
> know it.*

- **Action card set**: LISTEN, CATALOG, REWIND, THE THIRD
  EAR, AUDI ET TACE (passive), TAPE-LOG, FIRST PLAY, SEAL
  THE INDEX, BEAR WITNESS, OBSERVE (win card)
- **Ultimate**: THE FIRST RECORDING — once per run, peek
  the entire remaining destiny deck without revealing it to
  the room
- **Mix-and-match notes**:
  - Elicia @ L0 Diner: LISTEN at search piles peeks the top 2
    items without taking either; CATALOG records the tile
    contents as a lore token without picking them up. The
    Diner's inertia is harder for her because she doesn't
    physically act — she records.

### H3 — MAYA  (Hierophant upright)

> *Novice. Maybe still in training. Carries the rites for
> the next generation. She CAN speak — must speak — and her
> shadow is the wrong sermon, not silence.*

- **Action card set**: GENUFLECT, SAY THE WORDS, SEAL THE
  CONFESSION, POUR OIL, RING THE BELL, BLESSING, KEEPER OF
  THE BOOK, AT THE PULPIT, INHERIT, TRANSMIT (win card)
- **Ultimate**: THE PRAYER YOU MEMORIZED AT NINE — once per
  run, freeze Doctrine Wear / equivalent tension for one
  full turn

### H4 — (unspecified Chariot character)  (Chariot upright)

> *Driver, sysop, courier, or runner. Open name. Carries
> mastery of contradiction (the two sphinxes pulling in
> opposite directions). Drives.*

- Action card set themed on movement + control + cargo
- Ultimate: THE SECOND HAND — once per run, override a
  Fatigue tick

---

## The reshade principle

The Frasier table above is the model for every hand. Each
hand's toolkit reshades every location it visits in a
specific, principled way — not just "the player uses
different cards." The hand's UPRIGHT arcana frames how
their tools INTERPRET the location's REVERSED arcana shadow:

- **John Frank (Fool ↑)** reshades by *staying still in a
  room that wants you to commit*. His tools are slow, his
  cost is patience. In other locations: he's the watcher
  who knows the place from the outside. Frasier's warehouse
  through John's eyes is *eleven years of someone else's
  obsession*.
- **Frasier (Magician ↑)** reshades by *making everything
  literal and bindable*. Reduces rooms to gestures. Costs
  in demons-owed.
- **Elicia (Priestess ↑)** reshades by *receiving rather
  than acting*. Her presence in the Diner means the room
  is being RECORDED for the first time; the Diner's
  Inertia doesn't tick when she's present at a space (she
  takes the tick into her tape instead, where it becomes
  lore). Her cost: every recording fills the archive, and
  the archive eventually weighs.
- **Maya (Hierophant ↑)** reshades by *imposing protocol
  on places that have none*. In the Diner, she makes
  WIPE COUNTER into a ritual — the cloth becomes a vestment.
  Inertia rises faster when she's present (the room
  resists ritual), but each ritual completion is a 2x
  connection.
- **(Chariot ↑)** reshades by *being in motion in static
  rooms*. Their presence keeps any space from going
  "stuck" (drift attractors weaken).

The design rule: **every hand×location pair should produce
a sentence that explains how the run feels.** Not "John
plays the Diner" but "John plays the Diner = staying still
in the room that wants him to leave." Not "Frasier plays
the Archive" but "Frasier plays the Archive = trying to
fix tapes Elicia would have just left." Each combination
is a small thesis.

---

## UNLOCK SYSTEM (cross-arcana progression)

Per Final Girl's "play streaks unlock content" model:

### Unlocked by LOCATION clears

When a hand clears a location for the first time, the LOCATION
itself unlocks:
- A new ITEM is added to one of its search piles for future runs
  (e.g. clearing the Diner once adds a BAR KEY to the Under
  Counter pile)
- A new SPACE becomes accessible (the BAR opens for the rest of
  the campaign, etc.)
- A new DESTINY CARD is added to the location's deck

### Unlocked by HAND clears

When a hand clears any location, they unlock one of their own:
- A new ACTION CARD added to their starting deck
- Their ULTIMATE gets a +1 charge (used twice per run instead of
  once)
- A new VISITOR variant becomes available

### Unlocked by HAND × LOCATION combos

Specific pairings unlock special items:
- John @ L1 cleared → John can carry CASSETTE SPINE from the
  warehouse into L2 (Archive), where it's already pre-indexed
- Frasier @ L0 cleared → Frasier unlocks PAINTED DINER, a
  variant element he can place during his L1 runs
- Elicia @ L0 cleared → her archive now contains a tape of
  John's run; in her L2 runs, listening to that tape gives
  +1 visitor pre-arrival hint
- Maya @ L0 cleared → the church inherits a sermon about
  D'Ambrosio's; her L3 runs gain +1 GENUFLECT starter

### Unlocked by SCENARIO clears

Each scenario, when first beaten, unlocks the NEXT scenario for
that location. Each location ships with all three scenarios
buildable, but locked in sequence:
- S1 (canonical) is unlocked from the start
- S2 unlocks after S1 is beaten
- S3 unlocks after S2 is beaten

S3 of each location is the "hard mode" / "true ending" variant —
the run that tests whether you've actually mastered the room.

---

## IMPLEMENTATION PRIORITY

Given the current state (THE LEAP is built, ready-ish for play):

1. **Author all three Fool/Diner scenario cards** as separate
   JSON files (currently we only have `setup_the_leap.json`;
   need `setup_the_shift_change.json` and `setup_the_blackout.json`).
   This proves the per-location scenario-variant system works
   without touching new arcana yet.

2. **Refactor the gallery launch UI** to show a 3-step picker:
   pick LOCATION → pick HAND → pick SCENARIO. Currently the
   gallery launches straight into "the_leap." Need a setup
   chooser that resolves into the right setup_*.json + hand
   + scenario combination.

3. **Build LOCATION L1 (Frasier's Warehouse)** as the first
   non-Fool location, with its own Gravity deck themed on
   Magician-reversed (the table going wrong). Three scenarios
   for it. Frasier becomes an UNLOCKED hand after his location
   clears.

4. **Wire HAND H1 (Frasier)** as a playable mix-and-match —
   Frasier can play L0 (Diner) AND L1 (Warehouse).

5. **Iterate** — L2 / L3 / etc. each follow the same pattern:
   location first (sketches new destiny deck + finale set),
   hand follows.

After L0/L1 are both playable with both H0/H1 (4 combinations
× 3 scenarios = 12 distinct runs), the engine's modularity is
proven and the remaining arcana boxes are content work.

---

## Open questions

- **Where does the gallery picker live?** Suggestion: replace
  the current "▷ PLAY THE LEAP" hotspot in the Fool gallery card
  with a "▷ ENTER THE GAUNTLET" hotspot that opens the 3-step
  picker as a modal.

- **Do hands have separate dice?** Probably yes — John's die
  is the existing 6-face SS/S/S/fail/fail/wild. Frasier's
  might have a STEADY face instead of a wild. Each hand JSON
  declares its die.

- **Cross-arcana unlocks: persistent or session-local?**
  Persistent via GauntletState autoload, already in place. Each
  run reads the state on setup to determine which unlocks
  apply.

- **Difficulty curve**: should some location × hand combos be
  marked "expert" — i.e. you can pick them but they're tuned
  hard? Or should we just trust the player to pick what
  interests them? Suggest: no difficulty rating. The mismatch
  IS the interest.
