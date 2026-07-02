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
5. **Visitor roster + unique meeples** — the people and animals
   who haunt this room. They're attached to the LOCATION, not to
   any specific hand. Faith is D'Ambrosio's dog; she's there
   whether John or Frasier or Elicia is playing. She does NOT
   follow a hand across locations. Each room has its regulars.
6. **Item piles** at search spaces — half the items are universal
   to that location, half unlock from completed runs
7. **Scenario cards** — three variants per location

If a HAND's character is ALSO a regular at that location (e.g.
Frasier as hand playing at D'Ambrosio's, where Frasier is also
a usual visitor), the location's visitor slot for that character
gets replaced — typically by another diner regular pulled from
the unlocked-visitor pool (Anya, an extra cook, etc.). You can't
sit with yourself.

### A HAND provides:

1. **Character meeple + portrait** (their player-piece travels
   with them across locations)
2. **Action card set** (~10 cards) themed by the UPRIGHT arcana —
   UNIVERSAL by default, travels with the hand from location to
   location. Cards that need a specific space (WIPE COUNTER needs
   a "counter") self-gate via `requires`. Cards that depend on a
   LOCATION-scoped visitor or item (CALL FAITH calls Faith, who
   only exists at D'Ambrosio's) opt-in to location-locking via
   `available_in_locations: [...]` and are simply NOT loaded
   when the hand plays elsewhere. The pattern: if a card's
   referent (space, visitor, item) is location-scoped, the card
   gets locked to that location. Most cards are universal.
3. An **Ultimate** — one-shot powerful card, name + flavor
4. A **starting hand** drawn from framework + their arcana-unique cards
5. **Carryover unlocks** — cross-arcana items their previous
   completions made available

A hand does NOT bring its own visitors. The visitor roster is
location-scoped (see above). What John brings to the diner is
HIMSELF + his action cards + Faith's name in his memory — but
Faith herself lives at the diner. John playing the warehouse
won't have Faith there; the warehouse has its own creatures
(the warehouse demons).

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
  - Note: Faith stays at the diner. She's the room's dog,
    not John's. John plays the Warehouse without her —
    that's part of the cost of leaving the room he knows.
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
- **INVOKE A DEMON** — summon a warehouse demon to a SPACE
  on the board (not as a visitor — as a *wiring*). The
  demon takes residence in that space and IMPRINTS a flavor
  onto it for the rest of the run:
    · TEXTURE demons add atmosphere — that space now reduces
      Inertia/tension by 1 when ended on
    · CONNECTION demons act as bridge — a space they're
      wired into becomes ADJACENT to any other demon-wired
      space (Frasier lays parallel circuits across the
      board)
    · POWER demons feed actions — at a power-wired space,
      one card play this turn is free
  You owe each demon one Inertia/tension when invoked. They
  remain until end of run or until ABJURED (a card that
  costs 2 tension to unwire them). Frasier carries six
  demon types in his hand; only some are appropriate for
  any given location (no warehouse demon works in a church).
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

> *Archivist, recorder, editor. The laptop comes with her;
> the camera lives in the bag at her hip; the lapel mic is
> always clipped, batteries fresh. She is not just an
> archivist — she is the DIRECTOR who has been recording
> THE POMEGRANATE HOUR episodes through this entire gauntlet,
> one per arcana, twenty-two of them. Each room she visits,
> she is filming. Each visitor she meets is unwitting cast.
> Her shadow (Priestess reversed) is the urge to speak in
> the cut — to interrupt the recording with her own voice.*

#### The kit (carries to every location)

Elicia starts every run with these THREE items already in
her inventory. They're the equivalent of John's bindle —
but unlike the bindle, they're the TOOLS for her win, not
the win itself:

- **THE LAPTOP** — her editing station. Movable. Whenever she
  ends an ACTION phase standing on a space, the laptop's
  "post" pile fills 1 tick toward EDIT. (Each space she
  edits at becomes part of the episode's "rhythm.")
- **THE CAMERA** — captures FOOTAGE at any space. One charge
  per location-space-per-run; the camera "remembers" what's
  there.
- **THE LAPEL MIC** — captures AUDIO at any space. Different
  pile than footage. Audio from where visitors are speaking
  is worth 2x.

#### The bindle equivalent: AN EPISODE

She wins by assembling a complete POMEGRANATE HOUR episode
about the location. The episode requires:

- **FOOTAGE** from at least 3 different spaces (recorded
  with the CAMERA action card)
- **AUDIO** from at least 2 visitor interactions (recorded
  with the MIC card while they're present and speaking)
- **EDIT** completed at the laptop — a final-cut action she
  plays during PLANNING that consumes all gathered FOOTAGE +
  AUDIO and emits a finished episode card

The episode itself is themed by the LOCATION'S reversed
arcana — Elicia at the Diner makes EPISODE 0 · THE FOOL
(reversed reading). Elicia at the Warehouse makes EPISODE
I · THE MAGICIAN. Same gauntlet, different episode each
location. Over 22 runs at 22 locations, the full Pomegranate
Hour gets assembled.

#### Action card set

- **ROLL CAMERA** — at any space, record FOOTAGE of it. One
  per space per run. Free if you're alone here, +1 PRESSURE
  if a visitor is watching.
- **HOT MIC** — at any space with a visitor, capture AUDIO
  of their voice. The visitor must be SPEAKING — i.e. they
  just arrived this turn OR they're at a connection-relevant
  space. Without that, you get room tone instead (worth less).
- **CUTAWAY** — drop the laptop here for one turn; future
  ROLL CAMERA shots at adjacent spaces get a +1 bonus
- **ROUGH CUT** — at the laptop, assemble a 1-minute pass.
  Counts as 1 partial visitor connection if you have enough
  raw material. Doesn't fully connect, but tilts the
  visitor toward yes.
- **B-ROLL** — passive: every move logs an environmental
  detail to the FOOTAGE pile automatically (lightweight,
  for connecting the cuts)
- **PLAYBACK** — at the laptop, play a recorded tape AT
  a visitor; if it's relevant to them, they connect
  immediately (this is how she avoids speaking)
- **THE THIRD EAR** — passive: at any threshold space, peek
  the next Gravity card
- **REWIND** — once per run, undo the last move (Priestess
  time-fold; expensive — costs the laptop's current edit
  progress)
- **CATALOG** — record one Lore Token without claiming it
  (the archive remembers without you committing — same as
  before)
- **CUT TO BLACK** *(win card)* — at the laptop, play this
  with FOOTAGE ≥ 3 + AUDIO ≥ 2 + the laptop in EDIT-ready
  state. Episode is finished. Run ends in win.

#### Ultimate · THE FIRST RECORDING

Once per run. She plays back a tape she made BEFORE this
run started — a tape from her archive that's relevant to
the current location. Effect: reveal one currently-hidden
visitor's connect_via requirement in full, in plain English,
displayed as a tooltip on their meeple for the rest of the
run. (Lore: she's been recording everyone for years; she
knows the secret of how to reach them.)

#### Carryover unlocks

- Cleared L2 (Archive): a tape from THIS run's location
  joins her archive. On the next run at the same location,
  she starts with that tape playable (counts as one
  pre-filled audio slot).
- Cleared L0 (Diner): unlocks DINER ROOM TONE — passive
  +1 audio per turn in any subsequent Diner-shaped space
- Across all 22 locations: each completed episode unlocks
  the NEXT episode's location for free playback in the
  meta-gallery (Pomegranate Hour becomes diegetically
  available as a finished show).

#### Mix-and-match: Elicia reshading each location

| @ Location | What changes | Why |
|---|---|---|
| **L0 Diner** (Fool reversed) | The diner becomes a film set. Inertia doesn't tick when she's standing on a space she's already recorded (the room is being remembered correctly). But she has to GET the recordings before the room slips — visitors who get consumed before HOT MIC captures them are gone from the episode forever. Her win is EPISODE 0 — the Fool reversed reading rendered as a half-hour radio drama. | Her presence transforms the Diner from a place into a subject. The 3:47 AM dread becomes documentary footage of 3:47 AM. |
| **L1 Warehouse** (Magician reversed) | She and Frasier exist in the same room at the same time often — Pomegranate Hour Episode I is largely about him. ROLL CAMERA on Frasier (the visitor here) is worth +2 FOOTAGE. But the warehouse demons jam her audio — HOT MIC has a 30% chance to capture nothing per try. | The Magician's reality-hack interferes with documentation; she has to outwait the interference. |
| **L2 Archive** *(home)* | Default tuning. The laptop already has previous episodes loaded. PLAYBACK costs 0. She knows where every tape is — search is free here. | Home location: lowest friction. |
| **L3 Church** (Hierophant reversed) | HOT MIC during a rite is blasphemous and powerful — captures audio worth 3x but raises DOCTRINE WEAR by 2. The bishop's voice on tape is the episode's centerpiece if you can get it. | The Priestess records what the Hierophant transmits — the act of recording the rite IS the heresy. |
| **L4 Road** (Chariot reversed) | The laptop drains its battery while moving — must EDIT at a stop. Visitors are passing truckers (CB calls = HOT MIC opportunities). The episode is a road movie. | Chariot's motion conflicts with her stationary editing process; she has to plan stops. |

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
- **Elicia (Priestess ↑)** reshades by *turning every room
  into a subject*. She arrives with a laptop, a camera, and
  a lapel mic. Her win at any location is to film + record
  + edit a half-hour Pomegranate Hour episode about that
  location's reversed arcana. The Diner becomes EPISODE 0
  · THE FOOL; the Warehouse becomes EPISODE I · THE
  MAGICIAN; etc. Across 22 runs at 22 locations, the full
  show gets assembled. Her cost: every audio captures the
  room's bad ambient; her shadow is the urge to narrate
  over what was already true.
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

## The setup screen (when content multiplies)

Once there's more than one scenario per location, more than one
hand, and unlocks gating content — the launch flow needs its own
screen. Sketched:

**Three-column picker**, left-to-right is the choice order:

| LOCATION (pick) | HAND (pick) | SCENARIO (pick) |
|---|---|---|
| L0 D'Ambrosio's Diner | H0 John Frank | S1 THE LEAP |
| L1 Frasier's Warehouse 🔒 | H1 Frasier Temple 🔒 | S2 THE SHIFT CHANGE 🔒 |
| L2 Elicia's Archive 🔒 | H2 Elicia 🔒 | S3 THE BLACKOUT 🔒 |
| ... | ... | ... |

Each card shows ONLY what the player should know at the picker.

**LOCATION card preview:**
- Name + reversed-arcana subtitle ("D'Ambrosio's Diner · Fool reversed")
- The location's tension stat NAME (Inertia / Disorder / Pressure-to-Speak)
- Scene description (the opening prose)
- **A list of the DESTINY DECK's card TITLES** — but NO effects
  ("THE CLOCK HOLDS, WIPE THE SAME SPOT, STILL CHASING SHADOWS, ...")
  The titles tell the mood; what each card does is for discovery.
- Number of visitors, number of search piles, threshold count
- Unlock status: locked / unlock condition

**HAND card preview:**
- Portrait + arcana name ("John Frank · Fool upright")
- Character flavor (2-3 sentences)
- **Action card list — only UNLOCKED cards visible**
- Locked action cards show as 🔒 with the unlock condition
  ("LONG REST — Beat THE LEAP without using Short Rest")
- Ultimate card name + flavor (always visible — it's the
  signature ability)
- Carryover unlocks already earned (small chip-list)

**SCENARIO card preview:**
- Title + subtitle ("THE LEAP · Between Acts · 3:47 AM")
- Setting prose
- Starting state summary (Time / Inertia / Health)
- Visitor schedule preview (anonymized — "3 on board at start,
  3 scheduled, 1 conditional")
- Win condition in plain English (no spoilers about HOW)
- Unlock chain: which scenarios become available after this one

**The reveal contract:**
- Destiny-deck card TITLES visible, EFFECTS hidden — drives discovery
- Player's own action-card EFFECTS fully visible — you should know
  your tools
- Visitor connect_via and order_item HIDDEN — in-game discovery
- Per-location tension stat NAME visible — you should know what
  you're playing against
- Win/loss conditions visible in plain English

Implementation note: each LOCATION + HAND + SCENARIO file gets a
`preview` block summarizing what shows at the picker, so the data
file owns its own presentation. Engine reads the previews and
builds the picker columns.


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


## D'Ambrosio's scenario ladder (Fool location)

The diner has three SCENARIO setup files now — same location, same
hand (John Frank), different time of day + tuning. The room
escalates around the same engine.

### THE LEAP · easy · 3:47 AM (Between Acts)
`setup_the_leap.json`

The off-shift. Almost nobody. The room presses on you because
nothing else is. Win = assemble the Bindle, gather three
visitors, walk to a threshold. Inertia +1/turn.

This is the canonical introduction — the rules of the engine
revealed gently. The painted-bg / FP-view / threats / sanity
all show up here but the cost of doing it slowly is low.

### THE RUSH · medium · 12:18 PM (Lunch Service)
`setup_lunch_rush.json`

Lunch service. The room is loud, full, sunlit. Two helper
meeples on the board: the Bus Kid (jovial) and the Line Cook
(gruff). Inertia +2/turn. Win = serve 4 orders + connect 3
visitors + reach a threshold under Inertia 9.

The Bindle isn't the win. The orders are. The tension is
keeping up, not unsticking yourself.

### FULL HOUSE · hard · 8:42 PM (Evening Service)
`setup_evening_service.json`

Evening service. The bar is OPEN — visitor spawns include the
bar half of the room (BAR, BAR STOOLS, JUKEBOX, BOOTH 1/4).
Both helpers still on the board. Inertia +2 at the low end, +3
once you cross 7. Starts at Inertia 1 / Sanity 4 instead of
0/6 — the night is already underway when you clock on.

Win = serve 6 orders + connect 4 visitors + reach a threshold
under Inertia 10.

### Helper visitors
Two staff meeples added with the medium+hard setups:

- **The Bus Kid** (`bus_kid`) — starts at the dish station.
  Helper flag means: cannot be claimed; cannot be dispersed
  by COMING THROUGH; doesn't count toward visitor totals.
  (Engine support for "threats decay faster near a helper"
  is pending.)
- **The Line Cook** (`line_cook`) — starts at the grill.
  Helper flag, same protections. (Engine support for "auto-
  rings the bell each Upkeep" pending.)

### New action card: COMING THROUGH
1 Time, stock 2, non-starter. Disperses every non-helper,
non-Faith visitor at the player's current space to a random
adjacent space. Useful when the counter clogs at lunch or
the bar swarms at evening.

### 1st-person view mode
The default view in the gauntlet panel is a 1st-person painted
shot of the player's current space, with a navigation bar at
the bottom listing adjacent spaces. The fullscreen toggle (⛶)
opens the top-down map.

Per-space FP art lives at:
  `assets/gallery/locations/<location>_fp_<space_id>.png`
Studio entries (gauntlet_studio.html) carry one prompt per
space — defaults to the dambrosios spaces; reusable per
location.
