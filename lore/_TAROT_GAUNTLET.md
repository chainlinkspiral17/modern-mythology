# THE TAROT GAUNTLET

*A modular solo card-and-dice framework where each Major Arcana is a
playable scenario. The Final Girl board-game (Van Ryder Games, 2020)
provides the shared chrome — turn phases, action-card tableau,
time-as-currency, custom dice, modular boxes, achievement-driven
unlocks. The framework's animating idea departs from Final Girl
here: **each arcana's play loop comes from its tarot meaning, not
from a transposed killer-vs-victims structure.** The Fool isn't a
horror movie. The Fool is the moment before commitment, and the
game is the test of whether the moment can resolve.*

---

## I. Why this exists

The deck has always promised play. The Fool card's chrome literally
draws a UI:

> NOTEBOOK · INVENTORY · RESTART · weapon (empty) · shield (empty)

with "VN DESIGN NOTES" rendered *inside* the card as a fourth-wall
break. The Priestess names the same meta-system the NARRATIVE
STRUCTURE COMPASS / RUST_CODE.BBS. Every card has hotspots, ciphers,
dormant cross-references, an oracle reading split into UPRIGHT and
REVERSED. The deck has been authoring a game one card at a time.
This doc names the game.

## II. The framework, in one paragraph

A turn has five phases: **Action** (play cards from hand) →
**Planning** (spend Time to buy cards from the tableau) → **Shadow**
(the reversed reading acts on the room — what FG calls the Killer
phase) → **Drift** (witnesses or objects in the shadow's
neighborhood move per the arcana's rules — what FG calls Panic) →
**Upkeep** (resolve carried effects, rearrange inventory). The
player holds an *Arcana* (the upright reading they're trying to
embody), occupies a *Location* (chapter setting board), and carries
a *Hand* (the character carrying the arcana through this location).
Win by satisfying the arcana's specific win condition before the
**Shadow Track** maxes out and the **Finale** triggers. Lose by
slipping into the reversed reading — the arcana's own dark mirror.

**Critical departure from Final Girl:** the win condition and the
shadow's flavor are not transposed from horror-movie tropes. They
are derived from the arcana's tarot meaning. The Fool is about *the
leap*. The Magician is about *assembly*. The Priestess is about
*the archive*. The Hierophant is about *inheritance*. The framework
provides shared mechanics; the arcana provides the scenario's
*shape*.

## III. Mapping Final Girl → Tarot Gauntlet

| Final Girl | Tarot Gauntlet |
|---|---|
| Final Girl meeple (you) | Player meeple (the *Hand* carrying the arcana — John Frank for Fool, Maya for Hierophant, etc.) |
| Final Girl card (Laurie / Reiko) | Hand card — character stats + Ultimate Ability |
| Killer | **Shadow** — the reversed reading of this arcana, manifesting as a track that fills and a Finale that resolves. NOT an external monster. NOT something you attack. The Fool's shadow is *inertia*; the Magician's is *failed assembly*; the Priestess's is *the urge to speak*. |
| Killer board (Bloodlust, Health, Finale, Dark Powers) | **Shadow board** — Shadow Track (fills toward reversal), Finale (the named reversed state), Dark Powers (escalation flavor cards) |
| Horror Track / Horror Roll | **Threshold Roll** — how steadily you embody the upright reading this turn |
| Time Track (6 per turn) | Time Track (6 per turn, identical mechanic) |
| 6 custom dice (core box) | **Arcana dice** — each arcana has its own 6-face die. Fool's die has LEAP/PAUSE/ONE-FOOT/TWO-FEET/WIPE/DOG. Additional dice unlock through play. |
| Action card tableau (~23 cards) | **Action tableau** — shared core (~16 cards: Walk, Focus, Search, Sprint, Short Rest, Long Rest, Distraction, Guard, Retaliate, Close Call, Spend It, Improvise) + 4-6 arcana-unique cards joined in when that arcana is played |
| Setup cards (5 per location) | Setup cards (3-5 per arcana × location pairing — randomizes starting state + specific complications) |
| Item deck (per Location) | Item deck (per Location — diner items at D'Ambrosio's, warehouse items at Frasier's cathedral, etc.) |
| Event cards (10 per Location) | Event cards (ambient location beats — Frasier walks in, the river runs, the BBS hums) |
| Terror cards (the Killer's actions) | **Gravity deck** — what the *room* does each turn. The diner being a diner. The cathedral being a cathedral. Not attacks; weather. |
| Finale cards (3 per Killer) | Finale cards (3 per arcana — the named reversed state, e.g. "wipe the same spot forever," "the model city has no rivers in it") |
| Achievements (per Killer + per Location) | Achievements (per Arcana + per Location) |
| Feature Film modularity (any Killer × any Location) | **Arcana × Location** mix-and-match. Fool runs canonical at D'Ambrosio's; once unlocked, "Fool at Frasier's Cathedral" plays with a different gravity-deck flavor and a different threshold geometry. |

## IV. The Fool box: THE LEAP

### IV.1 What this scenario is

The Fool's card oracle reads:

> UPRIGHT: Beginnings, naivete, free spirit, innocence, leap of
> faith, infinite potential, the witness who hasn't yet committed.
>
> REVERSED: Recklessness, foolishness, paralysis disguised as
> openness, the 24-hour diner of the soul where you never actually
> leave.

The chapter's whole register is suspension. The clock above the
door reads 3:47 AM and does not move. John Frank has been wiping
this counter for twelve years. The chapter ends without resolution
because the chapter IS the moment before resolution.

The game is the test of whether the moment can resolve.

There is **no killer.** The antagonist is **the room itself, being
indifferent.** Indifference is the threat. The diner doesn't hate
John; it just doesn't notice him, and being unnoticed by a room
you've been standing in for twelve years is what's slowly making
you not exist.

Walking out of the diner is trivial. Three thresholds are visible
in the iconography: the parking lot door, the river window, the
precipice door labeled "II — THE PRECIPICE DOOR." You can reach any
of them in three turns.

But the leap *as the Fool* isn't walking out. The leap *as the
Fool* requires that you take the room with you — that you've named
what you're carrying, that you have a witness, that you've seen
your own archetype. The game is the difference between escaping and
*leaping*.

### IV.2 Win condition

Play the **LEAP** action card from any threshold space (Parking
Lot, River Window, Precipice Door) with all three of:

1. **Bindle assembled.** You have a STICK, a CLOTH, and a CONTENTS
   in your inventory, and have played BUNDLE to tie them together.
   See §IV.5 — these are real physical things, not metaphors.
2. **Faith adjacent.** The dog is on your space, the witness to
   the leap.
3. **Three Visitors connected.** You have made contact with three
   of the people / presences passing through the diner. See §IV.6
   — Frasier, the Booth-Six Stranger, Faith herself, the Dawn
   Cook, the BBS Caller, Anya's Recording.

Choose your threshold at the moment of LEAP. Each gives a different
ending lore token:

- **Parking Lot** — *the leap into Graustark*, the world the rest of vol5 maps
- **River Window** — *the leap into the substrate*, the journey of vol6+
- **Precipice Door (II)** — *the leap into Elicia's archive*, you become Priestess-witnessed

The Precipice Door is not on the map at game start. It appears
when four or more Visitors are simultaneously present (not
claimed, not dismissed) — canonically the diner has a full
register of presence, and the threshold to the archive opens.

### IV.3 Loss conditions

Two paths into the reversed state. Both reveal a Finale (§IV.9);
which Finale fires depends on which loss path triggered it.

**Inertia 12.** The shadow has filled the room. Exits disappear.
You wake at 3:47 AM tomorrow. (Finale: *Wipe The Same Spot Forever*
or *24-Hour Diner Of The Soul*.)

**Three Visitors Claimed.** The shadow has taken the people who
might have been a beginning. Frasier never sits, the stranger
gets up, Faith sleeps under a different counter. (Finale: *The
Empty Room*.)

Either loss yields the same shape — the named state of *you*,
here, in stasis. The card resolves to the reversed reading.

### IV.4 The Inertia Track (the Shadow)

A force that undoes player progress. Default range 0-12. Starts at
0 (or at 6 on a restart from a prior loss).

**Ticks up by:**
- **+1 per turn** by default — the gravity of the room
- **+1** per comfortable action: WIPE COUNTER, ADDRESS THE BELL
  when not picking up a Bindle component
- **+1 or +2** per Gravity-deck card resolved (see §IV.7)
- **+1** if the Bindle is not assembled by turn 6
- **+1** per CALL FAITH beyond the second (the dog gets tired)

**Ticks down by:**
- **−1** per Visitor connected (see §IV.6) — the shadow loses ground
  every time a real presence is met
- **−1** per Bindle component picked up (Stick, Cloth, Contents)
- **−1** per Upkeep phase where Faith is adjacent
- **−1** from THE STEAMBOAT ECHO (only if you've completed the
  Magician — cross-arcana threading)

**Inertia thresholds:**

| Level | State | Active effect |
|---|---|---|
| 0-3 | *standing at the counter* | neutral |
| 4-6 | *the rag is warm in your hand* | small flavor effects from Gravity cards |
| 7 | *what time is it again* | Gravity deck draws +1 card per turn |
| 8 | *the room is listening too closely* | the Shadow places a CLAIM on the closest unconnected Visitor on the board |
| 9-10 | *the door looks farther* | exit spaces cost +1 movement |
| 10 | *the room has decided* | the Shadow places a CLAIM on the next-closest unclaimed Visitor |
| 11 | *the counter knows your name* | every Action card costs +1 Time |
| 12 | *24-hour diner of the soul* | Inertia-loss Finale revealed |

A CLAIMED Visitor has a black marker placed on their meeple. You
have **2 turns** to CONNECT with that Visitor or the Shadow
consumes them — see §IV.6.

### IV.5 The Bindle — stick, cloth, contents

The Fool's iconography is literal: a stick over the shoulder, a
cloth knotted at its end, something carried within. The mechanic
mirrors the picture. You need three real things.

| Component | Where it is | What it is |
|---|---|---|
| **The Stick** | KITCHEN ALCOVE search pile | a broken broom handle propped against the freezer for eleven years. Nobody has thrown it away. Nobody has used it. |
| **The Cloth** | BOOTH 6 search pile | a cloth napkin folded for the next customer. It's been folded the same way for so long the creases are permanent. Take it. |
| **The Contents** | drawn from REGISTER search pile (5 possible) | what you choose to put inside. See below — the meaningful pick. |

The **Contents** is the meaningful authoring decision: what do you
take from the diner with you? When you SEARCH the Register pile,
you see the top card faceup and may keep it OR put it back and
search again next turn. The five Contents options:

| Contents | Ending lore token at LEAP | Cross-arcana unlock |
|---|---|---|
| **Pocket money from the till** | *"leaving with what was owed"* — twelve years of unpaid hours, finally taken | unlocks the *Twelve Years Cashed Out* item, usable in any arcana run as +1 starting Time |
| **The cassette spine JOHN_47AM_3** | *"leaving with the record of being seen"* — Elicia archived you while you slept on your feet | unlocks the Priestess archive overlay in any arcana — every run reveals an extra Lore Token at end |
| **A scratched penny from your apron** | *"leaving with the smallest weight that's still mine"* — the smallest thing the diner doesn't own | unlocks the *Apron Penny* die-modifier — once per game you may flip a single die's result |
| **A note from booth 6** | *"leaving with the message that was meant for me"* — the stranger left a note; you finally read it | unlocks the *Booth Six Note* hand-card — playable in any arcana, lets you peek at any Visitor's lore token in advance |
| **The graffiti tag from the table** | *"leaving with proof I was here once"* — FRANKLY/FOOLISH, scratched twenty years ago, taken back | unlocks the *Graffiti Hand* item — once per game, place any Lore Token on a Bindle component without the Search |

With STICK + CLOTH + CONTENTS held, the action card **BUNDLE** (0
Time) becomes playable. It ties cloth around stick with contents
inside. Without playing BUNDLE, LEAP cannot be played.

### IV.6 Visitors and Connections

The diner is the held breath of a 24-hour place. People walk
through it. Six potential Visitors. Each is a meeple. They are not
memories or abstractions — they are real presences in the room,
arriving on specific turns or at specific triggers.

**The Visitor roster:**

| # | Visitor | Arrives | Connects via | Lore token at connection |
|---|---|---|---|---|
| 1 | **Frasier Temple** | turn 3, walks in from the kitchen alcove and sits at COUNTER | play SIT WITH at the counter for 1 full turn (no other action this turn) while Frasier is adjacent | *"still chasing shadows"* — Frasier sees you, you see Frasier |
| 2 | **The Booth-Six Stranger** | already at booth 6 at game start | pick up the CLOTH from booth 6 AND stand on CARD WALL once during the game (the stranger and the painted Fool are paired witnesses) | *"you were seen first"* — there was an observer before the deck |
| 3 | **Faith** | already under the counter at game start | play CALL FAITH twice (she responds; you've named her) | *"the dog's name is Faith"* — she is also the mandatory leap witness |
| 4 | **The Dawn Cook** | turn 5, walks in from the parking lot to the kitchen alcove | be at KITCHEN ALCOVE during his arrival turn and play SHORT REST (accept the coffee he hands you) | *"shift change"* — the next person who'll wipe this counter |
| 5 | **The BBS Caller** | turn 6, the BBS terminal flickers at REGISTER | move to REGISTER and play ADDRESS THE BBS BANNER | *"sysop ember.ash.rest.bbs"* — the network has been counting the dead all night |
| 6 | **Anya's Recording** | auto-arrives if CONTENTS = cassette spine; otherwise, never | auto-connected the moment BUNDLE is played with the cassette spine | *"the Priestess is older than the chapter"* — Elicia has been recording you for years |

You only need **three** Visitors connected to play LEAP. The more
you connect, the richer the leap and the more Lore Tokens reveal at
the end.

**The Shadow claims Visitors — stasis is what's left when
indifference wins:**

When Inertia hits 8, the closest unconnected Visitor on the board
gets a CLAIM marker (a black token on their meeple). When Inertia
hits 10, a second CLAIM is laid on the next-closest unclaimed
Visitor.

If you do not CONNECT with a Claimed Visitor within **2 turns** of
the claim, the Visitor is consumed: their meeple moves to a
board-edge area labeled CLAIMED. That Visitor is unavailable for
the rest of the game. They've been absorbed by the indifference;
the moment passed.

**If three Visitors end up Claimed (consumed), you lose** — see
§IV.3. The Empty Room finale triggers. The diner is full of an
absence. There's nobody left to be a beginning for.

This is the thematic crux: the Fool's leap requires that you've
been *with people*. If the diner consumes them faster than you can
be with them, the leap stops meaning anything. The diner of the
soul isn't lonely. It's surrounded by half-real people you never
quite met.

### IV.7 The Gravity Deck

Twelve cards. One drawn at the start of each Shadow phase. These
are *not* attacks. They are the room being the room. The room
generates lore-tokens, hands you coffee, asks if you want anything
else — and each generosity is also a way of keeping you.

| # | Card | Effect |
|---|---|---|
| 1 | **THE CLOCK HOLDS** | Time does not reset to 6 next Planning phase; resets to 5. +1 Inertia. |
| 2 | **WIPE THE SAME SPOT** | If you played WIPE COUNTER this turn, no penalty. If not, +1 Inertia. |
| 3 | **STILL CHASING SHADOWS, JOHNNY?** | If Frasier has not yet arrived, his arrival turn drops by 1 (he comes early). +1 Inertia. |
| 4 | **THE FLUORESCENT TICK** | Every Action card with Time cost ≥ 2 costs +1 this turn. |
| 5 | **THE COUNTER WANTS WIPING** | Discard 2 Action cards or +2 Inertia. |
| 6 | **THE GRAFFITI HAND** | Reveal a Lore Token (FRANKLY/FOOLISH). No Inertia change. The room *gives*; that's also gravity. |
| 7 | **THE BELL RINGS (ONE TONE)** | One of the bell's two tones plays automatically. After both have rung, the next Visitor's arrival turn drops by 1. |
| 8 | **THE PAINTED POSE** | If you have not connected with the Booth-Six Stranger, +1 Inertia. |
| 9 | **THE STEAMBOAT ECHO** | Reveal a Lore Token. If you have completed the Magician arcana, lower Inertia by 1. (Cross-arcana threading.) |
| 10 | **THE FELLOW TRAVELER** | Faith moves to your space, free of action cost. |
| 11 | **TWELVE YEARS** | +2 Inertia. The room reminds you how long you've been here. |
| 12 | **NINE LOCUST SEVENTEEN DOOR** | The Sinkhole's number-sequence whispers from the counter. Reveal the Precipice Door threshold regardless of Visitor count, but every subsequent turn standing on COUNTER adds +1 Inertia (the depression in the laminate is calling). |

### IV.8 [removed — folded into the codex]

A previous draft tracked a "card-within-the-card" recognition track
as a separate progression bar. Dropped — it was a third self-aware
mechanic on top of the Bindle and Visitors and the codex itself was
already visualizing recognition. Recognition happens through play
(connecting with Visitors, assembling the Bindle, leaping through
specific thresholds); the codex (§VI) shows it; no separate
in-game track needed.

### IV.9 The three Finale cards

The reversed Fool isn't a monster who arrives. It's the named state
*you* enter when a loss condition fires. Reveal a Finale based on
which loss path triggered:

| Finale | Triggered by | What it means |
|---|---|---|
| **WIPE THE SAME SPOT FOREVER** | Inertia 12 | The counter glows. You cannot leave the COUNTER space. The card is over; you sleep on your feet. |
| **THE 24-HOUR DINER OF THE SOUL** | Inertia 12 | Every exit space disappears from the map. The Bindle, if assembled, is forgotten. You wake at 3:47 AM. |
| **THE EMPTY ROOM** | Three Visitors Claimed | Frasier doesn't come. The cook doesn't come. The stranger has gone. Faith is curled in the corner, alone. The counter is wiped to a polish. There is no one left to be a beginning *for*. |

Repeated losses don't erase progress — Lore Tokens already revealed
carry over to subsequent runs, achievement progress accrues, and
the codex's surfaced hotspots stay illuminated. Stasis is real but
it isn't permanent. The card is still learnable.

### IV.10 Fool-unique action cards (joining the tableau)

Final Girl gives you six Zero-Cost starters (Walk, Focus, Search,
Sprint, Weak Attack, Short Rest). The Gauntlet keeps the four
non-violent ones (Walk, Focus, Search, Short Rest) and drops the
two violent ones (Weak Attack, Furious Strike) — the Fool isn't a
fighter. In their place:

| Card | Time | Effect |
|---|---|---|
| **WIPE COUNTER** | 0 | starter. +1 Time, +1 Inertia. The tempting comfort. |
| **ADDRESS THE BELL** | 1 | starter. At BELL, ring next tone. After both tones, the next Visitor arrives 1 turn early. +1 Inertia. |
| **CALL FAITH** | 1 | Faith moves to your space. Max 2 uses (third is +1 Inertia). Connection action for Visitor #3 (Faith). |
| **SIT WITH** | 0 | Pass the turn — no other actions this turn. Connection action for Visitor #1 (Frasier) when he's adjacent at the COUNTER. |
| **SHORT REST** | 1 | Recover 1 health. Also the connection action for Visitor #4 (the Dawn Cook) when played at KITCHEN ALCOVE on his arrival turn. |
| **ADDRESS THE BBS BANNER** | 1 | At REGISTER, the connection action for Visitor #5 (the BBS Caller). Otherwise no effect. |
| **STEP TOWARD** | 1 | Move 1 space toward a threshold of your choice. |
| **PICK UP** | 0 | Take a Bindle component or Item-deck card from your current space. |
| **BUNDLE** | 0 | Requires STICK + CLOTH + CONTENTS in inventory. Ties them. Unlocks LEAP. |
| **LEAP** | 3 | At a threshold, all win conditions met → game ends victorious. Choose threshold for ending lore token. |

Connection-to-Visitor #2 (the Booth-Six Stranger) is not a single
card play; it's a sequence — pick up the CLOTH at booth 6 AND
stand on CARD WALL once during the game. The composite act *is*
the connection.

### IV.11 The Hand: John Frank

| stat | value |
|---|---|
| Health | 5 |
| Ultimate ability | *Twelve Years.* Once per game, when you would draw a Gravity card, you may instead choose the top card of the Gravity discard pile and resolve that. (You force the room to repeat itself — twelve years of doing this means you know its moves.) |
| Save-witness rewards | (n/a — there are no rescuable witnesses; the equivalent is Visitor connection, which has its own per-Visitor reward shown on §IV.6's table) |

John is the canonical Fool-Hand at D'Ambrosio's. Alternate hands
unlock later — Maya as a Fool at the Hierophant's chapel, etc.

### IV.12 D'Ambrosio's location board

```
                       PARKING LOT (threshold)
                              │
                              │
                    ┌─────────┴─────────┐
                    │                   │
            KITCHEN ALCOVE          BOOTH 6
              [search/Stick]        [search/Cloth]
              [Dawn Cook t.5]       [Stranger from t.0]
                    │                   │
                    ├──── COUNTER ──────┤      ← John starts here
                    │   (named space)   │      ← Frasier arrives t.3
                    │                   │
                    │   UNDER COUNTER   │
                    │      [Faith]      │
                    │                   │
                    └─── BELL ──────────┘
                       (bell tones gate
                        next Visitor arrival)
                              │
                          REGISTER
                          [search/Contents]
                          [BBS Caller t.6]
                              │
                          CARD WALL
                       (the recursive Fool
                        card pinned here —
                        Stranger connect
                        requires standing
                        here once)
                              │
                       RIVER WINDOW (threshold)
                              │
                              ⋮
                       PRECIPICE DOOR (threshold)
                       — only visible once
                       4+ Visitors present
                       on the board
```

Adjacencies follow the diagram. The COUNTER is central. The
Precipice Door threshold appears when four or more Visitors are
simultaneously present on the board (per §IV.2). The CARD WALL is
a named space where standing on it counts as part of the
Booth-Six Stranger's connection sequence (per §IV.6).

Visitor arrival spaces (per §IV.6): Frasier at COUNTER turn 3, the
Dawn Cook at KITCHEN ALCOVE turn 5, the BBS Caller signaled at
REGISTER turn 6. The Booth-Six Stranger is at booth 6 from the
start. Faith is under the counter from the start.

### IV.13 D'Ambrosio's item deck

Items live in 3 search-piles (Kitchen Alcove, Booth 6, Register).
The Stick is the top item in the Kitchen Alcove pile. The Cloth is
the top item in the Booth 6 pile. The Register pile is the
Contents pile — see §IV.5 for the five Contents options. Beneath
those, 3 face-down per pile, top one face-up. Search per Final
Girl: SEARCH draws the top; ★★ peeks the next.

Additional item cards (non-Bindle):

| Item | Hands | Effect |
|---|---|---|
| **Stale Coffee (cup #4 of the night)** | 1 | Recover 1 health; discard. |
| **Frasier's Wire-Wrapped Pen** | hands free | Once per game, force-convert one failure die to a success on a Threshold Roll. Frasier might give it to you if you connect; might leave it behind. |
| **The Fluorescent Strip** | hands free | Every PAUSE die rolled (Fool die face 2) lowers Inertia by 1 in addition to its other effect. |
| **AUDI ET TACE Luggage Tag** | hands free | Unlocked only after Hierophant completion. Once per game you may ignore one Gravity-deck card without resolving it. |
| **The Steamboat Echo** | hands free | Unlocked only after Magician completion. While equipped, draw 2 Lore Tokens at game end instead of 1. |
| **The Painted Pose** | hands free | Unlocked only after Magician's painting-acknowledged thread. Lore-only; reveals "John is in a painting in a room he'll never enter" at game end. |
| **The Charioteer's Sysop Handle** | 1 | Unlocked only after Chariot completion. Once per game, after a Gravity-deck card resolves, immediately draw and resolve another. (You let the BBS-counted-dead network through; risky.) |
| **A Number-of-the-Counter Slip** | 1 | A receipt with a four-digit hand-written number on it. Once per game, you may discard this to reduce a CLAIM marker's countdown by 1 — buying yourself an extra turn to connect with that Visitor. |

### IV.14 D'Ambrosio's event deck

10 cards. 1 is revealed at game start; subsequent events trigger
via Gravity deck card #6 (THE GRAFFITI HAND) and Hand ultimate
*Twelve Years* (when it re-resolves a discard).

1. **DAWN-NOT-QUITE-DAWN** — All Threshold Rolls +1 die for the rest of the game. The light is on your side.
2. **THE DEMONS ARE RESTLESS TONIGHT** — A digital-sprite Visitor (#7) appears at REGISTER alongside the BBS Caller. Same connect mechanic (ADDRESS THE BBS BANNER), separate Lore Token. Not counted toward the four-Visitor Precipice Door threshold.
3. **THE RIVER HAS ITS OWN PROGRAM** — RIVER WINDOW threshold closes for 2 turns.
4. **THE GRAFFITI HAND** — FRANKLY/FOOLISH appears on the wall. Reveal a Lore Token; no Inertia change.
5. **THE BBS HUMS** — At end of every turn, draw one face-down Item card from a search pile of your choice without spending Time. Persists until 3 items drawn this way.
6. **3:47 EXACTLY** — Time does not reset next Planning phase. Time resets to 3, not 6.
7. **WHO TAUGHT YOU TO BE A FOOL?** — Look at the top 3 cards of the Gravity deck. Put them back in any order.
8. **A SECOND COUNTER WIPE** — All WIPE COUNTER cards in your hand now read "+2 Time, +1 Inertia" instead of "+1, +1" for the rest of the game.
9. **NO ONE'S DRIVEN BY IN AN HOUR** — The Dawn Cook (Visitor #4) does not arrive this game. If already arrived, he leaves immediately. (If you needed him for your three connections, you need to find another.)
10. **THE BELL HAS A THIRD TONE** — Reveal one extra Visitor: **The Late Patron** (any character; rerolled at start of each game from the unaddressed list). Connects via ADDRESS THE BELL at the BELL while they're there. Adds Lore Token *"the chapter wasn't full at first."*

### IV.15 Achievements (three layers)

**Coarse arcana-tier:**
- ☐ Win once at D'Ambrosio's → unlock Fool for play at other locations
- ☐ Win at 3 different locations → unlock alt Fool die (REVERSED FACES)
- ☐ Win at all 7 vol5 locations → unlock the 22-die set framework
- ☐ 10 cumulative Fool wins → unlock the recursive Fool card as a Setup option in other arcana runs

**Fine-grained card unlocks:**
- ☐ Leap through the Parking Lot threshold → unlock Graustark-bound items
- ☐ Leap through the River Window threshold → unlock substrate-bound items
- ☐ Leap through the Precipice Door threshold → unlock Priestess archive items
- ☐ Win without playing WIPE COUNTER → unlock alt action card *Counter Is The Sinkhole* (treats COUNTER as a threshold space for one game)
- ☐ Win with all six Visitors connected → unlock *Frasier's Wire-Wrapped Pen* permanently in the item pool
- ☐ Win with Inertia 0 at the moment of LEAP → unlock *Bare Feet Fool* hand variant (start with 6 health; Bindle requires only Stick + Cloth)
- ☐ Win with every CONTENTS option played across separate games (all 5) → unlock the *Complete Bindle* achievement and a Codex glyph
- ☐ Surface PRECIPICE DOOR and leap through it → unlock the High Priestess as your next available arcana scenario
- ☐ Save a Claimed Visitor on the last turn of the claim → unlock the *Last-Minute Witness* item permanently
- ☐ Lose by reaching exactly 12 Inertia three games in a row → unlock the *Reversed Fool* as a playable hand (you embody the slippage)
- ☐ Lose by Three Visitors Claimed → unlock *The Empty Room* as a Setup variant (start with 2 Visitors already Claimed; harder)

**FG-style achievement pages:**
- The Fool page: defeat the Fool reversal at 5 locations, write each name (mirrors FG's per-Killer page exactly)
- The D'Ambrosio's page: defeat 5 different arcana reversals at the diner, write each name (mirrors FG's per-Location page)
- Pure completionist; no mechanical reward beyond filling the page.

## V. The play loop in detail

Five phases per turn:

1. **ACTION PHASE.** Play cards from hand. Each card costs Time and may trigger a Threshold Roll (or has a 0-cost / pure-effect resolution). Use Action cards to move, search for Bindle components, connect with Visitors (SIT WITH, SHORT REST, CALL FAITH, ADDRESS THE BBS BANNER, etc.), wipe the counter, address the bell, pick up items, eventually BUNDLE and LEAP.
2. **PLANNING PHASE.** Spend remaining Time to buy from the Action tableau. Time resets to 6 unless a Gravity/Event card said otherwise. Played + discarded cards return to the tableau at end of phase.
3. **SHADOW PHASE.** Draw the top Gravity card, resolve top-down. The Inertia Track ticks up per the card and per the per-turn baseline. If Inertia crossed 8 or 10 this phase, place CLAIM markers per §IV.4.
4. **DRIFT PHASE.** Claimed Visitors check their countdown — if they've been claimed for 2 full turns without a connection, they're consumed (meeple to CLAIMED area). Visitors scheduled to arrive this turn arrive. Faith moves toward you per THE FELLOW TRAVELER.
5. **UPKEEP PHASE.** Resolve carried effects (Inertia thresholds crossed, Bindle conditions met, Visitor connections completed). If Faith is adjacent, Inertia −1. Rearrange inventory. Reveal Finale if Inertia ≥ 12 OR three Visitors are Claimed.

## VI. The hybrid play surface

Confirmed direction: **location board + card-as-codex.**

The screen has two zones:

**Left/center: the location board.**
A static map of D'Ambrosio's interior (per §IV.12). Player meeple,
Faith's meeple, Visitor meeples (Frasier, Stranger, Cook, BBS
Caller, Anya, plus event-spawned), Claim markers on Visitor
meeples when the Shadow has reached for them, Bindle pickup
indicators on search piles, named spaces highlighted. Three search
piles visible. Inertia + Threshold + Time tracks visible above the
board. Hand below.

**Right: the gallery card pinned as codex.**
The actual `assets/gallery/fool.png` rendered at ~30% width. The 23
hotspots from `puzzle_hooks/fool.json` are clickable but *dormant*
— the card is read-only during play. Each hotspot has three states:

| State | Visual |
|---|---|
| Locked | hotspot invisible |
| Witnessed | hotspot visible, dim, gold ring |
| Surfaced | hotspot visible, fully lit, glyph attached |

Surfacing happens through play: an Action card (READ THE CARD), an
Event (graffiti hand, painting in Dante's office), an Item (the
cassette spine reveals the Anya cross-card), or an Achievement
(unlocked dormant hotspots become visible across all future runs).

The codex IS the meta-progression visible to the player. The card
literally fills in over many plays — by the time you've defeated the
Fool reversal at all 7 vol5 locations, the gallery card looks the
way it does in the design files, with all dormant cross-card
hotspots illuminated and the lore reading bound together.

This makes the gallery card not just art but **the save file made
visible.**

## VII. Cross-arcana threading

The dormant hotspots in `puzzle_hooks/fool.json` already encode
cross-card unlocks via `gated_by` fields. These map directly onto
the Gauntlet's cross-game unlocks:

| Hotspot | Gated by | Gauntlet unlock |
|---|---|---|
| `fool_steamboat_echo` | `vol5_magician_emperor_link` | Magician completion at Frasier's Cathedral |
| `fool_anya_tape_label` | `vol5_anya_introduced` | High Priestess completion |
| `fool_lovers_face_down` | `vol5_lovers_card_attempted` | Lovers attempted (even loss counts) |
| `fool_audi_et_tace_tag` | `vol5_audi_et_tace_known` | Hierophant completion |
| `fool_charioteer_scroll` | `vol5_charioteer_handle` | Chariot completion |
| `fool_faith_iris_match` | `vol5_strength_faith_lineage` | Strength completion |
| `fool_dawn_pre_echo` | `vol5_world_fool_return_seen` | World completion (end of vol5) |
| `fool_pomegranate_hour` | `vol5_priestess_pomegranate_hour_shelf` | Priestess Pomegranate Hour episode unlocked |
| `fool_counter_sinkhole` | `vol5_emperor_unmarked_photo_seen` | Emperor completion |
| `fool_painted_cosmic` | `vol5_magician_painting_acknowledged` | Magician completion (a different thread) |
| `fool_long_employment` | `vol5_emperor_two_sons_acknowledged` | Emperor completion (a different thread) |

The "more I play, the more there is" feeling comes from this:
**every other arcana you complete writes ink onto the Fool's card.**
You do not play the Fool in isolation; you play him *into* a deck
that is also being played.

## VIII. Each arcana's play loop, sketched

To prove the framework's modularity isn't FG-transposed in disguise,
here's a one-line shape for each arcana's win/loss derived from
its tarot meaning. **Not specced yet — sketches only.**

| # | Arcana | Verb | Win | Shadow (loss state) |
|---|---|---|---|---|
| 0 | Fool | leap | Leap from a threshold with bindle + witness + recognition | Inertia 12 (24-hour diner of the soul) |
| I | Magician | assemble | All four elemental components placed in the model city | Components scatter — the diorama collapses |
| II | High Priestess | observe | Archive filled (N lore tokens recorded without speaking) | The silence is broken |
| III | Empress | cultivate | The garden / studio / family flourishes to threshold N | Rot threshold reached |
| IV | Emperor | hold | The empire holds against entropy for N turns | The structure fragments |
| V | Hierophant | transmit | The rite reaches the next generation intact | The doctrine breaks under you (the player) |
| VI | Lovers | choose | A binding choice rendered and survived | The card refuses to flip — you walk away with nothing chosen |
| VII | Chariot | drive | The journey completes with mastery | The Charioteer arrives D.O.A. |
| VIII | Strength | endure | Hold the lion for N turns without breaking | You strike — and break what you were holding |
| IX | Hermit | withdraw | Find the lantern's revelation alone | Loneliness becomes the room |
| X | Wheel | ride | Survive a cycle of fortune-shifts without breaking | The wheel breaks you |
| XI | Justice | weigh | The scales rendered to a defensible verdict | The verdict shatters under appeal |
| XII | Hanged Man | suspend | Surrender to receive the revelation | You climb down too soon |
| XIII | Death | release | Let the named ending end | You hold on past the ending |
| XIV | Temperance | combine | The opposites mixed without spillage | The mixture goes wrong |
| XV | Devil | recognize | Name the bond you hadn't named | The bond names you instead |
| XVI | Tower | survive | Outlast the collapse | The collapse takes you with it |
| XVII | Star | offer | The annual offering rendered to its witness | The witness never arrives |
| XVIII | Moon | navigate | Move by indirect light, reach a hidden destination | The illusion takes you to the wrong place |
| XIX | Sun | clarify | Look directly at the thing you've been avoiding | You glance away |
| XX | Judgement | answer | Stand before the call and speak | You stay silent |
| XXI | World | return | The circuit closes — back to the diner with everything seen | The circuit doesn't close |

Some of these will turn out to want different turn-phase structures
(the High Priestess might use a 4-phase loop with an additional
RECORD phase; the Hanged Man might invert the loop so YOU don't
take actions, the room does, and your win is best-stillness). The
framework's chrome (Time, action cards, dice, codex) should hold;
the loops are arcana-specific.

## IX. The first slice — what gets built

Scope is **Fool only, THE LEAP scenario, D'Ambrosio's location.**

**Data files** (JSON, authored before any engine code):
```
godot/resources/games/
  _README.md                          ← schema doc
  framework/
    action_tableau_core.json          ← shared core verbs
  fool/
    die.json                          ← 6 faces per IV.1's die description
    setup_the_leap.json               ← per §IV (win, loss, starting state)
    action_cards.json                 ← Fool-unique cards per §IV.10
    gravity_deck.json                 ← Gravity cards per §IV.7
    finale.json                       ← three reversal states per §IV.9
    bindle.json                       ← stick + cloth + 5 contents per §IV.5
    visitors.json                     ← six Visitor specs (arrival + connect
                                        + lore token + claim rules) per §IV.6
    achievements.json                 ← three-layer per §IV.15
  locations/
    dambrosios.json                   ← map per §IV.12 + items §IV.13 + events §IV.14
  hands/
    john_frank.json                   ← stats + ultimate per §IV.11
```

**Engine code** (GDScript, after data is locked):
```
godot/scenes/games/
  TarotGauntletGame.gd                ← main controller, 5-phase loop
  PlayerBoard.gd                      ← Time, Threshold, Inertia, Hand display
  LocationBoard.gd                    ← map renderer + meeples
  ActionTableau.gd                    ← card market
  HandArea.gd                         ← player hand
  ShadowBoard.gd                      ← Inertia Track + Finale display
  Dice.gd                             ← arcana dice + Threshold Roll
  CardCodex.gd                        ← gallery card pinned, hotspot states
  AchievementPanel.gd                 ← FG-style page
  TarotGauntletGame.tscn              ← root scene
godot/autoload/
  GauntletState.gd                    ← persistent meta-progression
```

**Save system extension:**
`SaveSystem.gd` gets a `mark_gauntlet_progress(arcana, location,
achievement_id)` method. Gauntlet runs do NOT touch the VN save
slots — they live in a separate `gauntlet_state.json` save file so
arcana runs don't conflict with linear chapter progress.

**Hookup to the existing menu:**
The Gallery (which shows all 22 arcana cards) gets a new affordance
per card: "▷ PLAY" appears once the arcana has a built scenario.
Clicking enters TarotGauntletGame. For the first slice, only the
Fool card shows the affordance.

## X. Open questions for after this doc lands

1. **Card art for action cards.** Final Girl's cards have flavor
   text + success/partial/failure lines. The Gauntlet inherits the
   structure. Per-arcana card art for the unique cards, or generic
   chrome with arcana-tinted accents?
2. **The codex's gallery card** — canonical `assets/gallery/fool.png`,
   or a stripped version so hotspot states are visually unambiguous
   without competing with the artwork?
3. **Hand variants beyond John.** Maya as a Fool-Hand at the
   Hierophant's chapel — reserve for a later slice or scope now?
4. **Reversal music.** The Pomegranate Hour, the music strata, the
   tarot_synth — all suggest the Shadow phase has its own
   soundscape. Tag now, build later.

---

*This doc is the framework spec, not the implementation.
Implementation proceeds in two passes: data files (§IX) reviewed
against this doc, then engine code wired to consume them. Engine
code is not begun until this doc is signed off.*
