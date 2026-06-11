# TAROT GAUNTLET · SCENARIO CARDS

*Rough scenario sketches for the first run of arcana boxes, each
keeping the shared framework chrome (5-phase loop, action tableau,
Threshold dice, Gravity deck, Inertia track) but reshaping the
location mechanics + win loop to match the arcana's tarot meaning.*

*Parent doc: [`_TAROT_GAUNTLET.md`](_TAROT_GAUNTLET.md)
(§VIII has the one-liners; this doc fleshes out the first ones).*

---

## Design template

Every scenario card is a JSON setup file like
`fool/setup_the_leap.json`, plus its own deck of action cards,
gravity cards, finale cards, items, and (optionally) a unique
location file. The framework provides:

- 5-phase turn loop: **Action → Planning → Shadow → Drift → Upkeep**
- Threshold dice (6 faces: SS / S / S / fail / fail / wild)
- 11 framework action cards (Walk, Sprint, Focus, Search, Short
  Rest, Long Rest, Distraction, Guard, Close Call, Spend It,
  Improvise)
- Time as per-turn action budget, carries over
- Modal infrastructure (card view, pane modals, finale CG, etc.)

**What each scenario card must specify:**

1. **Setting + atmosphere prose** — the scene the player walks into
2. **Tension stat** — by default this is Inertia, but each arcana
   can rename / reshape it (the Magician's is *Disorder*, the
   Priestess's is *Pressure-to-Speak*, etc.)
3. **Win condition** — derived from the arcana's verb
4. **Loss conditions** — typically a Shadow-Track max + a per-arcana
   reversal state, plus the universal Health = 0
5. **Visitor concept + roster** — who comes through, what their
   connection requires
6. **The "Bindle" equivalent** — the three-things-that-must-come-
   together pattern, named for the arcana
7. **Arcana-unique action cards** — 8-10 verbs only this arcana can
   play, layered on top of the framework 11
8. **Gravity deck** — 12 cards including 3 endgame
9. **Finale cards** — 3 reversal states

---

## 0 · THE FOOL — additional variants

The canonical Fool scenario is **THE LEAP** at D'Ambrosio's. The
Fool is "the moment before commitment" — every Fool variant should
preserve that core but change the room.

### 0a — THE LEAP (canonical, already built)

- Location: D'Ambrosio's diner, 3:47 AM
- Hand: John Frank
- Bindle: stick + cloth + contents
- Tension: Inertia (0–12, "the 24-hour diner of the soul")
- Win: BUNDLE assembled + 3 connections + Faith adjacent +
  Inertia < 7 + at threshold → play LEAP
- Loss: Inertia 12 OR 3 patrons consumed OR Health 0

### 0b — THE STAIRWELL  *(alternate scenario)*

> 18 flights down the side of a tall building, hot summer night.
> The fire alarm has been going for an hour. The elevator stopped
> working at the 14th floor. You came in for the 17th-floor
> tenant who isn't answering their phone. Now you're walking
> down with someone else's dog.

- **Location**: Stairwell, 11 landings (one per floor 17 down to
  street level + roof). The board is a vertical column.
  - Each landing is a space; up/down are the only adjacencies
  - Landings 4-7 have apartments that opened during the alarm
    (the visitors come from these)
  - Landing 1 (Street) and Landing 11 (Roof) are thresholds
- **Bindle**: a NAME (whose dog), an ADDRESS (where to take them),
  WATER (the dog is panting)
- **Tension**: Inertia *("the alarm sound is still in your teeth")*
- **Win**: get the dog to STREET LEVEL with the right name +
  address, OR get to the ROOF and prove the alarm was nothing
- **Loss**: alarm escalates past Inertia 12 (the building's actually
  on fire) / dog dies of dehydration (you lose track of Water) /
  three neighbors get separated from their kids (3 patrons consumed)
- **Unique mechanic**: every space change costs +1 Time per landing
  you DESCEND past your starting floor (going down is harder than
  going up — the framing inverts the usual "exit threshold" logic)
- **Visitors**: a kid with no shoes, a building super on a walkie,
  a tenant in slippers, a paramedic on a stretchered call, the
  dog itself (FAITH equivalent), a phantom-elevator caller

### 0c — THE LAST CALL  *(alternate scenario)*

> The pirate radio station is going off the air at midnight. You
> have 40 minutes until the broadcaster reads the sign-off
> announcement. There are still calls coming in, and one of them
> is for you.

- Location: small radio station booth + four lit-up phone-call
  hotspots representing the four lines
- Hand: a young John Frank (pre-D'Ambrosio's, working an overnight
  switchboard)
- Bindle: the right CALLER, the right SONG, the right SIGN-OFF
- Tension: SHOW TIME (counts down from 40)
- Win: route the right caller into the right song into the right
  sign-off in the last minute of the show
- Loss: dead air for 3+ rounds / sign-off goes wrong / your line
  rings out (Health 0)

---

## I · THE MAGICIAN — primary scenarios

The Magician's verb is **ASSEMBLE**. They take the four elements
on the table (Cups / Pentacles / Swords / Wands) and combine them
into something that wasn't there before. The shadow is **FAILED
ASSEMBLY** — components scatter, the diorama collapses.

The Magician hand: **Maya Lin / Frasier Temple** (the painter
character with the diorama studio).

### I.a — THE STEAMBOAT ECHO  *(primary)*

> Frasier's studio. The model city is half-assembled on the
> table. Four elements are missing: a piece of WATER (the river),
> a piece of EARTH (the bluffs), a piece of FIRE (the diner's
> light), a piece of AIR (the steamboat whistle). Each is hidden
> in a different room of the apartment. The painting is due
> tomorrow morning at the gallery.

- **Location**: Frasier's apartment-studio. Five rooms (Kitchen,
  Hall, Studio, Bathroom, Window). The model city sits in Studio.
- **Hand**: Frasier Temple
- **Bindle (the four elements)**: WATER + EARTH + FIRE + AIR
- **Tension**: DISORDER (0–10) *("the studio is half-finished
  and the studio is going to stay that way")*
- **Win**: All four elements PLACED on the model city in the
  studio + 3 PATRONS witnessed your placement
- **Loss**: Disorder 10 (everything scatters) / two elements
  refuse to fit / a critic arrives before the model is done
- **Unique mechanic — THE TABLE**: the model city in Studio is
  the win location. Each element placed locks it in (can't be
  removed). But every PLANNING phase, one already-placed element
  has a 1-in-4 chance of falling off if you weren't in Studio
  last turn (the table holds nothing without your hand on it).
- **Unique action cards** (~8 ideas):
  - **PLACE WATER / EARTH / FIRE / AIR** — only playable while
    holding the matching element, only in Studio. Locks it on.
  - **STEADY THE TABLE** — at Studio, prevents next Drift-fall
  - **SKETCH** — at any room, draw +1 Item card from this room's
    pile, but burn 1 Time
  - **GLAZE** — at Studio, polish a placed element so the next
    fall-off doesn't dislodge it
  - **WHISPER** — talk to a patron without breaking your focus
    (alternate connection method)
- **Visitors**: a buyer from the gallery, a critic from the
  newspaper, Frasier's ex-wife, a model the diorama is based on,
  an old painting teacher, Faith (the dog, again — she's the
  fellow traveler across runs)
- **Gravity deck themes**: THE LIGHT GOES OFF (a brush dries), THE
  TABLE LURCHES (one element falls), THE CRITIC ARRIVES EARLY,
  YOUR HAND SHAKES (next placement has +1 cost), etc.

### I.b — THE FOUR ON THE TABLE  *(alternate scenario)*

> A back-room poker game. Four other players. You have a quarter
> of the pot in front of you, and you came in tonight to LEAVE
> with what you brought. The game has 12 hands left before dawn.

- Location: round poker table, 5 seats. Spaces are SEATS — you
  can shift to read different players.
- Hand: a card-mechanic-savvy John Frank
- Bindle (the four pots): CASH + WATCH + RING + PHOTOGRAPH —
  these are what each opponent has on the table
- Tension: TILT (0–10)
- Win: leave with what you arrived with (Cash intact) + at least
  one of the other three pots taken (you talked someone out of
  their watch / ring / photograph in conversation, not by
  winning a hand)
- Loss: TILT 10 / you bet your own item / 3 hands without speaking
- **Unique mechanic — HANDS-PER-TURN**: each turn is a single
  poker hand. The ACTION phase = your hand. The SHADOW phase =
  the opposing player's hand (which the engine plays on rails).
  DRIFT = the river / showdown. UPKEEP = the table re-shuffles.

### I.c — THE BROADCAST  *(alternate scenario)*

> Pirate radio station. 30 minutes to broadcast. You have to
> assemble a 30-minute show from four reels: INTRO / NEWS /
> MUSIC / INTERVIEW. The reels are scattered through the building.

- Location: 5 rooms of the radio building (booth, archive, news
  desk, music library, lobby)
- Bindle: the four reels, in the right order, in the booth
- Tension: AIR TIME (countdown)
- Win: broadcast goes out at 30:00 with all four reels and the
  sign-off
- Loss: dead air / wrong reel cued / sign-off forgotten / the
  raid happens before broadcast (loss CG: the FCC at the door)

---

## II · THE HIGH PRIESTESS — primary scenarios

Verb: **OBSERVE**. The Priestess archives. She does not speak.
The shadow is **THE URGE TO SPEAK** — the silence breaks and the
archive corrupts.

Hand: **Elicia** (the archivist from vol5 — already a character
in the codebase).

### II.a — THE ARCHIVE  *(primary)*

> The basement tape archive. Wall-to-wall reels. Tonight someone
> is coming to find a specific recording, and you have to find
> it FIRST and place it in the listening room without saying a
> word. Three voices will arrive between now and dawn. You will
> hear them. You will not speak.

- **Location**: 4 archive rooms + 1 listening room + 1 stairs
  (the entry threshold from upstairs).
- **Hand**: Elicia
- **Bindle (the three index keys)**: CATALOG NUMBER + SIDE LABEL
  + DECK ASSIGNMENT — three layers of identification that
  pinpoint the right tape from thousands.
- **Tension**: PRESSURE-TO-SPEAK (0–10) *("the urge to answer
  is rising — every time you don't answer, it rises more")*
- **Win**: the right tape, queued in the listening room, when
  the third voice arrives + you haven't spoken yet
- **Loss**: Pressure-to-Speak 10 (you answer; everything heard
  this run wipes) / you take the wrong tape into listening (it
  IS heard, it ISN'T the truth, you lose) / a voice waits 3
  turns without being heard (they leave with nothing — you
  failed to receive)
- **Unique mechanic — NO SPEAK**: regular action cards that
  involve SPEECH (CALL FAITH, ADDRESS THE BELL, SIT WITH) raise
  Pressure-to-Speak by their cost. Most cards are RE-WRITTEN
  for the Priestess box to be physical / observational.
- **Unique action cards**:
  - **LISTEN** — at any archive room, peek the top 3 items of
    its pile without taking any
  - **CATALOG** — record one Lore Token without claiming it
    (the archive remembers without you committing)
  - **REWIND** — return last turn's actions to "as if not done"
    (once per run) — Priestess time-fold
  - **THE THIRD EAR** — at listening room, peek at next Gravity
    card
  - **AUDI ET TACE** — passive in hand: −1 Pressure-to-Speak per turn
- **Visitors**: each visitor has a Question they want answered.
  Connection = playing the RIGHT tape (item) in their presence.
  Wrong tape = pressure to speak rises. No tape played = they
  leave with nothing.

### II.b — THE LISTENING ROOM  *(alternate scenario)*

> A medium's parlor. Three sitters arrive over the night, each
> paying in coin. You give them something true — but it has to
> come through you without you saying it. They have to LEAVE
> believing the dead spoke.

- Location: parlor (table + 3 chairs + curtained alcove) + a
  back room with a few props
- Bindle: the three sitters' True Things (one each, drawn from
  their own bring-along objects)
- Tension: DOUBT (rises if you fake, falls if you reveal)
- Win: three true readings before dawn (one per sitter), all
  without saying anything that wasn't already in the room

---

## V · THE HIEROPHANT — primary scenarios

Verb: **TRANSMIT**. The Hierophant passes doctrine to the next
generation. The shadow is **THE DOCTRINE BREAKS** — the
transmission corrupts; the next generation receives a lie.

The motto from existing references: **AUDI ET TACE** (Listen
and be silent — what the Priestess does as a verb is what the
Hierophant inherits as a sacrament).

Hand: **Maya** (a young inheritor — the next-generation
character).

### V.a — THE VESTRY  *(primary)*

> Behind the altar of a small church between services. The
> visiting bishop arrives in the morning. Three rites need to
> be in order: COMMUNION (the wafers + wine), CONFESSION (the
> screen + the seal), BLESSING (the oil + the script). Each
> rite has a precise protocol. Speaking out of turn breaks
> the chain.

- **Location**: 5 spaces — Sanctuary, Vestry, Confessional,
  Sacristy, Bell Tower. The Bell Tower is the threshold
  (where the bishop's car approaches).
- **Hand**: Maya, novice
- **Bindle (the three rites)**: COMMUNION SET + CONFESSION SEAL
  + BLESSING OIL — each is in a specific room, each has its own
  protocol
- **Tension**: DOCTRINE WEAR (0–10) *("the words begin to mean
  something else")*
- **Win**: all three rites set up correctly + bishop arrives +
  you bless him (Communion in Sanctuary, Confession in Vestry,
  Blessing in Sacristy) without breaking the seal of any
- **Loss**: Doctrine Wear 10 (the rite means something else
  now) / you bless the wrong person (a visitor at the wrong
  rite) / the bishop arrives before you're ready
- **Unique mechanic — PROTOCOL ORDER**: each rite has 3
  sub-steps that must be done in a specific order. You can do
  them in any order across the night but BREAKING the order
  within a single rite costs Doctrine Wear.
- **Unique action cards**:
  - **GENUFLECT** — at any altar, +1 Time + lose 1 Pressure
  - **SAY THE WORDS** — at Sanctuary, advance the Communion step
  - **SEAL THE CONFESSION** — at Vestry, lock a visitor's
    Confession step (next rite step requires this)
  - **POUR OIL** — at Sacristy, advance the Blessing step
  - **RING THE BELL** — at Bell Tower, summon the next visitor
    forward (advance arrival)
- **Visitors**: the parish secretary (arrives with bishop's
  schedule), the verger (gives you the keys), an old parishioner
  who confesses something genuinely heavy, a young couple
  wanting a blessing they aren't ready for, a stranger who
  arrives wrong (HIEROPHANT-shadow tempter — must be turned
  away cleanly)

### V.b — THE GENERATION TABLE  *(alternate)*

> The night the patriarch dies. The family is gathered in the
> dining room. You are the inheritor. By morning, you must have
> passed on three things to the next generation already at the
> table: a STORY, an OBJECT, a NAME. Get any of them wrong and
> the line breaks.

- Location: dining room (5 chairs around a table) + kitchen +
  porch
- Bindle: the right STORY for one child + the right OBJECT for
  another + the right NAME for a third
- Tension: GRIEF (rises if the room cries, falls if you laugh
  together)

---

## VII · THE CHARIOT — primary scenarios

Verb: **DRIVE**. The Chariot controls direction by mastery of
contradiction (the two sphinxes). The shadow is **D.O.A.** —
the journey ends but the driver arrives dead. The existing
references hint at a sysop named DOA in the BBS network.

Hand: **a long-haul trucker / a sysop / a courier** — three
possible inheritors of the Chariot's verb.

### VII.a — THE LONG HAUL  *(primary)*

> Overnight haul, Graustark to Houston. The truck has 11 stops
> on the route. You're behind schedule by an hour. The cargo
> in back is something the company won't tell you about. By
> dawn you have to be unloaded at the dock, your hours-of-
> service legal, and the cargo intact.

- **Location**: the highway as a linear board (11 stops, each
  a space), plus your TRUCK (which you can step into/out of at
  any stop). Stops include: gas stations, weigh stations, a
  rest area, a closed diner, the dock at the end.
- **Hand**: a trucker character (Maya's brother? — open
  question, but a Chariot hand should be one of the named
  characters)
- **Bindle (the three legalities)**: HOURS LOG (must be filled),
  WEIGHT TICKET (must be valid), CARGO MANIFEST (must be
  signed)
- **Tension**: FATIGUE (0–10) *("you have not slept in 22
  hours")*
- **Win**: reach DOCK (last stop) by dawn + all three documents
  in order + cargo unbroken (no Sprint failures on rough roads)
- **Loss**: Fatigue 10 (you fall asleep at the wheel) / weight
  ticket fails at a weigh station / DOA cargo (sealed crate
  opens during a Sprint failure — and you can't un-see it)
- **Unique mechanic — DRIVING ROLLS**: instead of Threshold
  rolls, the Chariot rolls DRIVING dice — same 6 faces but a
  failure increments FATIGUE *and* damages the cargo. Every
  third turn must include at least one DRIVING roll or the
  truck stops.
- **Unique action cards**:
  - **SHIFT** — change which stop you're at (free for 1 hop,
    2 Time for 2 hops, requires a DRIVING roll)
  - **CHECK MIRRORS** — peek the next 2 Gravity cards
  - **CB CALL** — connect with another trucker visitor
  - **REST** — at a rest area, lose 2 Fatigue + lose 1 Time
  - **SIGN THE BILL** — at the dock, finalize the cargo manifest
  - **THE SECOND HAND** — once per run, override a Fatigue tick

### VII.b — THE SYSOP'S LAST LOG  *(alternate)*

> A BBS sysop's terminal. The system goes dark at 6 AM. You
> have to migrate the archives + answer three users + log out
> clean. Doors are virtual; spaces are screens.

- Location: a TUI of 5 screens (HOME / USERS / ARCHIVE /
  MAILBOX / TERM)
- Bindle: ARCHIVE EXPORTED + USERS NOTIFIED + LOG ROTATED
- Tension: SYSTEM LOAD (rises with every command)
- Win: clean shutdown at 6:00:00, all three columns green

---

## Cross-arcana threading (carry-over)

Each scenario's `cross_arcana_unlock` field on its items names
a hook the NEXT run reads. Examples:

- Fool's CASSETTE SPINE → unlocks PRIESTESS ARCHIVE OVERLAY in
  the Priestess box (some tapes are already pre-indexed when
  you arrive)
- Magician's PLACED WATER → unlocks RIVER WINDOW threshold in
  any Fool replay (the river already runs through Frasier's
  diorama; the next Fool run sees that diorama in his
  apartment if you visit there)
- Hierophant's SEALED CONFESSION → adds a CONFESSED visitor
  to the next Priestess run (they arrive carrying the secret
  you sealed)
- Chariot's HOURS LOG → if completed clean, the next Fool's
  Dawn Cook visitor arrives ONE turn earlier (the trucker
  drops them off)

These threads are why the GauntletState autoload exists —
it persists across scenarios. Each scenario only has to NAME
the threads it produces; the consuming scenario reads them
on setup.

---

## Implementation priority (after THE LEAP polish lands)

1. **MAGICIAN: THE STEAMBOAT ECHO** — the next full arcana
   build. Reuses the location-board pattern, introduces the
   "four-element assembly" mechanic, gives the cross-arcana
   threading a real first test.
2. **PRIESTESS: THE ARCHIVE** — second full build. Introduces
   the "speech is dangerous" inversion of the framework cards
   and the "no-take peek" Listen mechanic.
3. **HIEROPHANT: THE VESTRY** — third. Introduces
   protocol-order (do these N steps in this order).
4. **CHARIOT: THE LONG HAUL** — fourth. Introduces the linear-
   board variant.

After these four, the framework has been stretched in four
directions (assembly, observation, ordered ritual, linear
journey) and can comfortably absorb the remaining 18 arcana.

---

## Open questions

- **Hand-character cross-pollination**: should John appear as a
  visitor in someone else's arcana run? Yes — the existing item
  `painted_pose_item` already implies this (John in a painting
  in a room he'll never enter — Magician's diorama).

- **Threshold dice swap**: should each arcana have its own die
  faces? Fool uses 6-face SS/S/S/fail/fail/wild. Chariot maybe
  uses DRIVING dice with different distribution (more failures
  if Fatigue is high). The framework allows this via
  `die.json` per-arcana.

- **Inertia/tension stat rename**: is showing the player
  "PRESSURE-TO-SPEAK 7 / 10" cleaner than just generically
  "TENSION 7 / 10"? The literal label sells the arcana; keep
  per-arcana names.

- **Win-condition triggers**: each arcana's win condition is
  the equivalent of LEAP. Should the win card always be named
  the verb (LEAP, ASSEMBLE, OBSERVE, TRANSMIT, DRIVE)? Yes —
  consistent visual language across runs.

- **Loss CG variants**: same three-finale pattern across all
  arcana? Each arcana could have its own three reversal states
  (each tied to one loss path). The Fool already has this:
  WIPE THE SAME SPOT FOREVER / 24-HOUR DINER / THE EMPTY ROOM.
