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
Lot, River Window, Precipice Door) with all four of:

1. **Bindle assembled.** You've collected three named commitments
   (the Diner Rag, the Booth-Six Notebook, the Bell) into your
   inventory and played the ASSEMBLE BINDLE action. Without it
   you're escaping; with it you're leaping with what you knew.
2. **Faith adjacent.** The dog is on your space. She is the
   witness to the leap. Without her, you walk out alone and the
   leap doesn't register as a leap.
3. **The recursive card surfaced.** The card-within-the-card on
   the wall has four dormant elements (BINDLE, DOG, SUN, ABYSS).
   At least three must be surfaced — you must have *seen your own
   archetype* before you can act as it.
4. **Inertia below 7.** You haven't bought so deep into the
   routine that the leap is impossible.

Choose your threshold at the moment of LEAP. Each gives a different
ending lore token:

- **Parking Lot** — *the leap into Graustark*, mundane, the world the rest of vol5 maps
- **River Window** — *the leap into the substrate*, the journey of vol6+
- **Precipice Door (II)** — *the leap into Elicia's archive*, you become Priestess-witnessed

### IV.3 Loss condition

The Inertia Track reaches 12. The diner becomes the 24-hour diner
of the soul. The exits disappear from the map. You wake up tomorrow
at 3:47 AM and the run resets at Inertia 6. The losing screen says:

> *He's journey hasn't started; it's always about to.*

### IV.4 The Inertia Track (the Shadow)

Default range 0-12. Starts at 0 (or at 6 on a restart from a prior
loss). The Inertia Track ticks up by:

- **+1 per turn** by default (the gravity of the room)
- **+1** per comfortable action: WIPE COUNTER, ADDRESS THE BELL,
  READ THE CARD (when not at CARD WALL)
- **+1 or +2** per Gravity-deck card resolved (see IV.7)
- **+1** if the Bindle is not assembled by turn 6
- **+1** per Call Faith beyond the second (the dog gets tired)

The Inertia Track ticks down by:

- **−1** per memory addressed (see IV.6)
- **−1** per card-within-card element surfaced
- **−1** per Bindle item picked up (Rag, Notebook, Bell)
- **−1** per Upkeep phase where Faith is adjacent (the witness
  steadies you)
- **−1** from THE STEAMBOAT ECHO (only if you have completed the
  Magician)

The track has named thresholds:

| Level | State |
|---|---|
| 0-3 | *standing at the counter* — neutral |
| 4-6 | *the rag is warm in your hand* — small effects |
| 7-9 | *what time is it again* — Gravity deck +1 card per turn |
| 10-11 | *the door looks farther* — exit spaces cost +1 movement |
| 12 | *the 24-hour diner of the soul* — reversal triggers Finale |

### IV.5 The Bindle (the three commitments)

The Bindle isn't gear; it's three things John has been holding
without naming. Each is picked up at a specific space; picking it
up doesn't just inventory it, it *names it*.

| Item | Location | What it means |
|---|---|---|
| **The Diner Rag** | Counter (always present) | the labor I have done here. Twelve years of formica. Without it you're leaping as if your labor never happened. |
| **The Booth-Six Notebook** | Booth 6 (always present) | the stranger who watched me see them. Booth six is where the stranger sits in the vol5 prose. Without it you're leaping as if you were never witnessed first. |
| **The Bell** | Door (becomes pickup-able only after both of its tones have been heard via ADDRESS THE BELL) | the threshold I knew was a threshold. The bell rings twice in the iconography (open/close); you have to have heard both. Without it you're leaping without ever having known it was a leap. |

With all three picked up, the action card **ASSEMBLE BINDLE** (0
Time) becomes playable. It formally names the bundle. Without that
formal naming, LEAP cannot be played.

### IV.6 Memories (placed on the board, addressable)

The board has six MEMORY tokens at start:

| Space | Memory |
|---|---|
| Booth 6 | *the stranger looking up at you* |
| Kitchen Alcove | *Frasier's first entrance, fifteen years ago* |
| Bell | *the night you almost left, and didn't* |
| Register | *the twelve-year embroidered "12 yr" on your apron* |
| Card Wall | *seeing yourself in the painted card the first time* |
| River Window | *the steamboat in the reflection, that no one else has seen* |

Each memory takes the action card **ADDRESS A MEMORY** (2 Time)
to engage with. The card requires a Threshold Roll:

- ★★ — Memory dissolved, reveal a Lore Token, −2 Inertia
- ★ — Memory dissolved, reveal a Lore Token, −1 Inertia
- ✕ — Memory holds. +1 Inertia. The memory stays on the board.

Memories aren't victims and they aren't enemies. They're things in
John's head that you can choose to face or ignore. Facing them
helps you leave; ignoring them is fine, but they fill the room.

### IV.7 The Gravity Deck (formerly "Reversal," renamed)

Twelve cards. One is drawn at the start of each Shadow phase. These
are *not* attacks. They are the room being the room. The room
generates lore-tokens, hands you coffee, asks if you want anything
else — and each generosity is also a way of keeping you.

| # | Card | Effect |
|---|---|---|
| 1 | **THE CLOCK HOLDS** | Time does not reset to 6 next Planning phase; resets to 5. +1 Inertia. |
| 2 | **WIPE THE SAME SPOT** | If you played WIPE COUNTER this turn, no penalty. If not, +1 Inertia (the routine wanted it and you withheld). |
| 3 | **STILL CHASING SHADOWS, JOHNNY?** | Frasier's voice from the kitchen. The closest unaddressed memory moves to your space. +1 Inertia. |
| 4 | **THE FLUORESCENT TICK** | Every Action card with Time cost ≥ 2 costs +1 this turn. |
| 5 | **THE COUNTER WANTS WIPING** | Discard 2 Action cards or +2 Inertia. |
| 6 | **THE GRAFFITI HAND** | Reveal a Lore Token (FRANKLY/FOOLISH). No Inertia change. The room *gives*; that's also gravity. |
| 7 | **THE BELL RINGS (ONE TONE)** | Hear one of the bell's two tones automatically. After both are heard, the Bell becomes pickup-able regardless of ADDRESS THE BELL plays. |
| 8 | **THE PAINTED POSE** | If you haven't yet surfaced the SUN element of the card-within-the-card, +1 Inertia. If you have, no effect. |
| 9 | **THE STEAMBOAT ECHO** | Reveal Lore Token. If you have completed the Magician arcana, lower Inertia by 1. (Cross-arcana threading.) |
| 10 | **THE FELLOW TRAVELER** | Faith moves to your space, free of action cost. |
| 11 | **TWELVE YEARS** | +2 Inertia. The room reminds you how long you've been here. |
| 12 | **NINE LOCUST SEVENTEEN DOOR** | The Sinkhole's number-sequence whispers from the counter. If you stand on the COUNTER next turn, surface the ABYSS element of the card-within-the-card. +1 Inertia. |

### IV.8 The card-within-the-card (the recognition mechanism)

On the CARD WALL there's a small classic-tarot-style Fool card
pinned. It's the *recursive* Fool — the deck's thesis that every
modern person occupies an ancient archetype. It has four dormant
elements visible only after you've earned them:

| Element | Surfaced by |
|---|---|
| **BINDLE** | playing ASSEMBLE BINDLE |
| **DOG** | first time Faith is named in an event/action (CALL FAITH after she's responded once, or via *THE FELLOW TRAVELER* gravity card) |
| **SUN** | first time Inertia falls back below 4 after having reached 8+ |
| **ABYSS** | first time you stand on a threshold space (Parking Lot / River Window / Precipice Door) |

Three surfaced = LEAP becomes playable (given other conditions).

The point of this mechanism: the leap requires *self-recognition*.
You can't act as the Fool if you don't know you're the Fool. The
elements are the four iconographic notes the card makes about
itself; surfacing them is John learning he's been painted.

### IV.9 The three Finale cards (the named reversal)

The reversed Fool isn't a monster who arrives. It's the named state
*you* enter when Inertia reaches 12. Reveal one of:

| Finale | What it means |
|---|---|
| **WIPE THE SAME SPOT FOREVER** | The counter glows. You cannot leave the COUNTER space. The card is over; you sleep on your feet. |
| **THE 24-HOUR DINER OF THE SOUL** | Every exit space disappears from the map. The Bindle, if assembled, is forgotten. You wake at 3:47 AM. |
| **ANOTHER NIGHT, ANOTHER 3:47** | The clock resets visibly. The run begins again, Inertia 6, all memories restored, but Lore Tokens carry over. (Repeated losses still teach you the card.) |

### IV.10 Fool-unique action cards (joining the tableau)

Final Girl gives you six Zero-Cost starters (Walk, Focus, Search,
Sprint, Weak Attack, Short Rest). The Gauntlet keeps the four
non-violent ones verbatim (Walk, Focus, Search, Short Rest) and
drops the two violent ones (Weak Attack, Furious Strike); the
Fool isn't a fighter. In their place, the Fool starts with:

- **WIPE COUNTER** (0 Time): +1 Time, +1 Inertia. The tempting comfort. Discards to tableau like any other card.
- **ADDRESS THE BELL** (1 Time): If at BELL space, hear the next bell tone. After both tones, BELL is pickup-able. +1 Inertia.

The full Fool tableau adds these to the shared core:

| Card | Time | Effect |
|---|---|---|
| **WIPE COUNTER** | 0 | starter; see above |
| **ADDRESS THE BELL** | 1 | starter; see above |
| **READ THE CARD** | 1 | If at CARD WALL, surface one card-within-the-card element. −1 Inertia. If elsewhere, +1 Inertia (you tried to read it from across the room). |
| **ADDRESS A MEMORY** | 2 | At a memory's space, Threshold Roll. ★★ −2 Inertia; ★ −1 Inertia; ✕ +1 Inertia. Memory dissolved on success. |
| **CALL FAITH** | 1 | Faith moves to your space. Max 2 uses (third is +1 Inertia). |
| **STEP TOWARD** | 1 | Move 1 space toward a threshold of your choice. |
| **PICK UP** | 0 | Take a Bindle item or Item-deck card from your current space. |
| **ASSEMBLE BINDLE** | 0 | Bindle items required (3); formally name the bindle. Unlocks LEAP. |
| **LEAP** | 3 | At a threshold space, win conditions met → game ends victorious. Choose threshold for ending lore token. |

### IV.11 The Hand: John Frank

| stat | value |
|---|---|
| Health | 5 |
| Ultimate ability | *Twelve Years.* Once per game, you may treat any single ADDRESS A MEMORY as an automatic ★★ without rolling. |
| Save-witness rewards | (n/a — there are no witnesses in this scenario) |

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
              [search]              [search]
                                    [memory]
                    │                   │
                    ├──── COUNTER ──────┤      ← John starts here
                    │   (named space)   │      ← Diner Rag here
                    │                   │
                    │   UNDER COUNTER   │
                    │      [Faith]      │
                    │                   │
                    └─── BELL ──────────┘
                       [memory]
                       [bindle: Bell after both tones]
                              │
                          REGISTER
                          [search]
                          [memory]
                              │
                          CARD WALL
                          [memory]
                       (recursive card
                       pinned here)
                              │
                       RIVER WINDOW (threshold)
                              │
                              ⋮
                       PRECIPICE DOOR (threshold)
                       — only visible once
                       PRECIPICE DOOR
                       hotspot is surfaced
```

Adjacencies follow the diagram. The COUNTER is central. CARD WALL
is a named space where standing on it lets READ THE CARD function.
The third threshold, Precipice Door, doesn't appear on the map at
game start — it surfaces only after Inertia has been below 4 for
two consecutive turns, which canonically represents John lucid
enough to see the door he hadn't seen before. Search spaces map to
three item piles (see §IV.13).

### IV.13 D'Ambrosio's item deck

Items live in 3 search-piles (Kitchen Alcove, Booth 6, Register), 4
face-down per pile, top one face-up. Search spaces same as Final
Girl: SEARCH gives you the top card; ★★ lets you peek at the next.

| Item | Hands | Effect |
|---|---|---|
| **Diner Rag** | 1 | Always at Counter (not in piles). One of the three Bindle items. With Rag held, WIPE COUNTER gives +1 Time AND +1 Inertia (unchanged); without Rag, WIPE COUNTER gives 0 Time and still +1 Inertia. The rag IS the labor. |
| **Booth-Six Notebook** | 1 | Always at Booth 6 (not in piles). One of three Bindle items. With Notebook held, ADDRESS A MEMORY at any memory space gets +1 die on the Threshold Roll. |
| **The Bell** | 1 | At Bell space after both tones heard. One of three Bindle items. If carried, you can place it on any space. Memories within 2 of the bell move toward it on Drift phase. |
| **Stale Coffee (cup #4 of the night)** | 1 | Recover 1 health; discard. |
| **The Card Within The Card** (a small printed copy) | hands free | Permanent +1 die on any Threshold Roll made while standing on CARD WALL. |
| **Frasier's Wire-Wrapped Pen** | hands free | Once per game, force-convert one failure die to a success on a Threshold Roll. |
| **The Cassette Spine (JOHN_47AM_3)** | 1 | Unlocks the Priestess archive overlay on the codex. Lore-only; reveals 3 extra Lore Tokens at game end. |
| **The Fluorescent Strip** | hands free | Every PAUSE die rolled (Fool die face 2) lowers Inertia by 1 in addition to its other effect. |
| **AUDI ET TACE Luggage Tag** | hands free | Unlocked only after Hierophant completion. While equipped, you may ignore one Gravity-deck card per game without resolving it. |
| **The Steamboat Echo** | hands free | Unlocked only after Magician completion. While equipped, draw 2 Lore Tokens at game end instead of 1. |
| **The Painted Pose** | hands free | Unlocked only after Magician's painting-acknowledged thread. Lore-only; reveals the "John is in a painting in a room he'll never enter" token at game end. |
| **The Charioteer's Sysop Handle** | 1 | Unlocked only after Chariot completion. Once per game, after a Gravity-deck card resolves, draw and resolve another. (You let the BBS-counted-dead network through; risky.) |

### IV.14 D'Ambrosio's event deck

10 cards. 1 is revealed at game start; subsequent events trigger via
the Gravity deck (THE FELLOW TRAVELER triggers no event, but
WHAT FRASIER WOULD ASK draws one — both cards are functionally
equivalent; pick one based on flavor).

1. **STILL CHASING SHADOWS, JOHNNY?** — Frasier physically enters. He sits at COUNTER. Your next Action costs +1 Time. Persistent until you ADDRESS A MEMORY with him at the table (treated as a memory at his space).
2. **DAWN-NOT-QUITE-DAWN** — All Threshold Rolls +1 die for the rest of the game.
3. **THE DEMONS ARE RESTLESS TONIGHT** — Place 1 additional memory (a digital-sprite memory) at REGISTER.
4. **THE RIVER HAS ITS OWN PROGRAM** — RIVER WINDOW threshold closes for 2 turns.
5. **THE GRAFFITI HAND** — FRANKLY/FOOLISH appears on the wall. Reveal a Lore Token: "graffiti signature seen." No Inertia change.
6. **THE BBS HUMS** — At end of every turn, draw one Item card face-down. Persists until discarded.
7. **3:47 EXACTLY** — Clock will not reset Time at all next Planning phase. Time resets to 3, not 6.
8. **WHO TAUGHT YOU TO BE A FOOL?** — Look at the top 3 cards of the Gravity deck. Put them back in any order.
9. **THE FELLOW TRAVELER** — Faith is now adjacent to you, wherever you are, and stays for 3 turns.
10. **A SECOND COUNTER WIPE** — All WIPE COUNTER cards in your hand now read "+2 Time, +1 Inertia" instead of "+1, +1" for the rest of the game.

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
- ☐ Win with all six memories addressed → unlock *Frasier's Wire-Wrapped Pen* permanently
- ☐ Win with Inertia at 0 → unlock *Bare Feet Fool* hand variant (start with 6 health, no Bindle items required)
- ☐ Win using LEAP with all four card-within-card elements surfaced → unlock the full painted card art as a permanent skin
- ☐ Surface PRECIPICE DOOR threshold and leap through it → unlock the High Priestess as your next available arcana scenario
- ☐ Lose by reaching exactly 12 Inertia three games in a row → unlock the *Reversed Fool* as a playable hand (you embody the slippage)

**FG-style achievement pages:**
- The Fool page: defeat the Fool reversal at 5 locations, write each name (mirrors FG's per-Killer page exactly)
- The D'Ambrosio's page: defeat 5 different arcana reversals at the diner, write each name (mirrors FG's per-Location page)
- Pure completionist; no mechanical reward beyond filling the page.

## V. The play loop in detail

Five phases per turn:

1. **ACTION PHASE.** Play cards from hand. Each card costs Time and may trigger a Threshold Roll (or has a 0-cost / pure-effect resolution). Use Action cards to move, search, address memories, wipe the counter, address the bell, read the card, call Faith, step toward a threshold, pick up items, eventually assemble the bindle and LEAP.
2. **PLANNING PHASE.** Spend remaining Time to buy from the Action tableau. Time resets to 6 unless a Gravity/Event card said otherwise. Played + discarded cards return to the tableau at end of phase.
3. **SHADOW PHASE.** Draw the top Gravity card, resolve top-down. The Inertia Track ticks up per the card and per the per-turn baseline.
4. **DRIFT PHASE.** Memories in spaces affected by the resolved Gravity card move per its instructions. Faith may move toward you per THE FELLOW TRAVELER.
5. **UPKEEP PHASE.** Resolve carried effects (Inertia thresholds crossed, Bindle conditions met). If Faith is adjacent, Inertia −1. Rearrange inventory. Reveal Finale if Inertia ≥ 12.

## VI. The hybrid play surface

Confirmed direction: **location board + card-as-codex.**

The screen has two zones:

**Left/center: the location board.**
A static map of D'Ambrosio's interior (per §IV.12). Player meeple,
Faith's meeple, memory tokens, named spaces highlighted. Three
search piles visible. Inertia + Threshold + Time tracks visible
above the board. Hand below.

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
    bindle.json                       ← three commitment items per §IV.5
    memories.json                     ← six memory specs per §IV.6
    card_within_card.json             ← four elements per §IV.8
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
