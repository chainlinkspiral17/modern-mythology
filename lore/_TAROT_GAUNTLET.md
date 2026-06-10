# THE TAROT GAUNTLET

*A modular solo card-and-dice framework grafted onto the Modern
Mythology arcana. Each Major Arcana becomes a playable scenario; the
player embodies the upright reading and contends against internal
slippage toward the reversed reading. Heavily indebted to Final Girl
(Van Ryder Games, 2020) for action-economy, time-as-currency, and
multi-axis modularity.*

---

## I. Why this exists

The deck has always promised play. The Fool's card chrome literally
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
**Planning** (spend Time to buy cards from the tableau) →
**Reversal** (the reversed arcana acts on the room) → **Panic**
(witnesses in the reversal's space may flee or be lost) →
**Upkeep** (resolve carried effects, rearrange inventory). The player
holds an *Arcana* (the upright reading), occupies a *Location*
(chapter setting board), and starts with a *Hand* (the character
carrying the arcana through this location). Win by completing the
**Setup card's** objective before the Reversal Track maxes out and
the **Finale** state triggers. Lose by reversing — slipping into the
arcana's own dark reading.

## III. Mapping Final Girl onto Modern Mythology

| Final Girl | Tarot Gauntlet |
|---|---|
| Final Girl meeple (you) | Player meeple (the *Hand* carrying the arcana — John for Fool, Maya for Hierophant, etc.) |
| Final Girl card (Laurie / Reiko) | Hand card — character stats + Ultimate Ability |
| Killer | Reversed arcana (same card, broken meaning) |
| Killer board (Bloodlust, Health, Finale, Dark Powers) | Reversal board — **Reversal Track**, Reversal HP (how long until forced reversal), **Finale**, Dark Powers (escalation cards) |
| Horror Track / Roll (1-7, dice from 1-6) | **Threshold Track / Roll** — how close you are to the reversed read this turn |
| Time Track (6 per turn) | Time Track (6 per turn, identical mechanic) |
| 6 custom dice (core) | **Arcana dice** — each arcana has its own 6-face die. The Fool die has faces themed to the Fool's iconography (leap / pause / etc.). Additional dice unlock through play. |
| Action card tableau (~23 cards) | **Action tableau** — shared core (~16 cards: Walk, Focus, Search, Sprint, Short Rest, Long Rest, Distraction, Guard, Retaliate, etc.) + 2-4 arcana-unique cards joined in when that arcana is played |
| Setup cards (5 per location) | Setup cards (3-5 per arcana × location pairing — randomizes starting state + objective + named complications) |
| Item deck (per Location) | Item deck (per Location — diner items at D'Ambrosio's, warehouse items at Frasier's cathedral, etc.) |
| Event cards (10 per Location) | Event cards (ambient location beats) |
| Terror cards (Killer's actions) | **Reversal deck** — what the reversed arcana does during the Reversal phase |
| Finale cards (3 per Killer) | Finale cards (3 per arcana — the worst state of the reversal) |
| Achievements (per Killer + per Location) | Achievements (per Arcana + per Location) |
| Feature Film modularity (any Killer × any Location) | **Arcana × Location** mix-and-match. The Fool runs canonical at D'Ambrosio's; once unlocked you can play "Fool at Frasier's Cathedral" with a different reversal flavor |

## IV. What the Fool box specifically holds

### IV.1 The Fool die (six faces)

| Face | Symbol | Effect during a Threshold Roll |
|---|---|---|
| 1 | LEAP | Success ★★. Spend 1 Time and advance two spaces in your Setup's success direction. |
| 2 | PAUSE | Success ★. The clock holds; the Reversal Track does not tick this turn if the card resolves. |
| 3 | ONE FOOT | Partial. Spend 2 Action cards to convert to ★. |
| 4 | TWO FEET | Partial. Spend 2 Action cards to convert to ★. (Same partial value as ONE FOOT, different flavor on cards that read either-or.) |
| 5 | WIPE | Failure. The counter takes the action; nothing else does. +1 Bindle Token. |
| 6 | DOG | Wild. Counts as ★ if Faith (the dog) is adjacent to you; counts as failure otherwise. |

The Fool die replaces a standard d6 in any roll. Other arcana have
their own die that replaces standard d6s when that arcana is in
play. Final Girl uses 6 custom dice; the Gauntlet uses 1-3 arcana
dice + the rest are standard, with arcana-die slots growing through
unlocks.

### IV.2 The Setup card: BETWEEN ACTS (canonical Fool scenario)

```
SETUP · BETWEEN ACTS
Location: D'Ambrosio's interior
Hand:     John Frank

· You start at the COUNTER. The reversed Fool starts off-board.
· Place 6 WITNESS meeples in the diner (booth six, kitchen alcove,
  the bell, the register, the parking lot, the river window).
  Each witness is a memory John has carried for twelve years.
· Place 1 KNOCK token on each round of the Reversal Track at
  rounds 2, 4, 6. When the round arrives, draw and resolve a
  Reversal card immediately.
· Place the BINDLE on the kitchen alcove, the CARD on the wall,
  FAITH (the dog) under the counter.

OBJECTIVE
  Escort all 6 witnesses to an exit before the Reversal Track
  reaches 8. Each witness saved = 1 Memory token. 4+ Memory tokens
  at game end = victory. 6 Memory tokens = full canon resolution
  (unlocks alt Fool die at completion).

LOSING THE FOOL
  Reversal Track reaches 8 → Finale revealed. The reversed Fool
  walks in; you have 1 turn to defeat it (Threshold Roll vs all
  remaining Reversal Track ticks) before the diner becomes the
  24-hour diner of the soul.

NAMED SPACES
  COUNTER (start) · BOOTH 6 · KITCHEN ALCOVE · BELL · REGISTER ·
  PARKING LOT (exit) · RIVER WINDOW (exit) · CARD WALL · UNDER
  COUNTER (Faith)
```

### IV.3 Fool action cards (joining the shared tableau)

Final Girl gives every player six Zero Cost starters (Walk, Focus,
Search, Sprint, Weak Attack, Short Rest). The Gauntlet keeps those
verbatim — they are the universal verbs of solo horror. Fool adds:

| Card | Time | Effect |
|---|---|---|
| **WIPE COUNTER** | 0 | If you are at the COUNTER, gain +1 Time and add 1 Bindle Token. Discards to the Action Tableau. |
| **ADDRESS THE KNOCK** | 2 | Threshold Roll: ★ = cancel the next Reversal card; ★★ = cancel AND lower Reversal Track by 1. Failure = +1 Reversal Track. |
| **READ THE CARD** | 1 | Move to CARD WALL (or if there, examine 1 hotspot from `puzzle_hooks/fool.json`). Reveals a Lore Token onto the codex — see §VI. |
| **PICK UP BINDLE** | 0 | If at KITCHEN ALCOVE, take the BINDLE into your inventory. With Bindle equipped, witnesses follow you at +1 movement. |
| **CALL FAITH** | 1 | Faith comes to your space. While Faith is adjacent, all 6-DOG rolls succeed. |

### IV.4 The Reversal deck — what slippage does

Twelve cards in the Fool's Reversal deck. Each represents a way the
"24-hour diner of the soul" leaks in. Cards are drawn during the
Reversal phase and apply top-down.

| # | Card | Effect |
|---|---|---|
| 1 | **THE CLOCK HOLDS** | Time marker does not reset to 6 in the next Planning phase; it resets to 5. |
| 2 | **WHO ASKED FOR THIS** | The closest witness to you panics 1 space away from any exit. |
| 3 | **THE COUNTER WANTS WIPING** | If you don't play WIPE COUNTER this Action phase, Reversal Track +1. |
| 4 | **THE FLUORESCENT TICK** | Every Action card with a Time cost ≥ 2 costs +1 this turn. |
| 5 | **THREE-FORTY-SEVEN** | All witnesses move 1 space away from exits. |
| 6 | **WHAT FRASIER WOULD ASK** | Draw an Event card from D'Ambrosio's deck immediately and resolve it. |
| 7 | **NINE LOCUST SEVENTEEN DOOR** | The bell rings. Any witness within 1 space of the bell may not move toward an exit this turn. |
| 8 | **CODE STREAMS** | The card chrome glitches. Discard 2 Action cards; if you can't, +2 Reversal Track. |
| 9 | **OBSERVER'S ARCHIVE** | A new witness appears at the BELL — Elicia has been recording. Place an extra witness meeple. |
| 10 | **THE PAINTING IN DANTE'S OFFICE** | If you have not addressed any knock this game, +2 Reversal Track now. |
| 11 | **AUDI ET TACE** | All witnesses freeze for one turn. They cannot panic; you cannot escort. (You can still wipe the counter, address the knock, etc.) |
| 12 | **TWELVE YEARS** | Final card before Finale. If drawn, the Finale flips face-up next Upkeep. |

### IV.5 Finale cards (the reversed Fool's worst states)

| Finale | Effect when revealed |
|---|---|
| **WIPE THE SAME SPOT** | The COUNTER is now blocked. You can stand on it but cannot use WIPE COUNTER. All Threshold Rolls −1 die for the rest of the game. |
| **THE COUNTER IS THE SINKHOLE** | The COUNTER becomes an *anti-exit*: witnesses move toward it instead of away. The shape of the Sinkhole Nexus's geological signature pressed up into the laminate from below. |
| **JOHN DOESN'T KNOW HIS OWN NAME** | You can no longer take CALL FAITH or PICK UP BINDLE — both cards become blank. Your accumulated Bindle Tokens stay; you just can't author new ones. |

### IV.6 D'Ambrosio's items

Items live in 3 search-piles on the LOCATION board (Kitchen Alcove,
Booth 6, Register). 4 face-down per pile, top one face-up. Search
spaces match Final Girl exactly: top card of pile faceup, Search
gives you the top, ★★ lets you peek at the next.

| Item | Hands | Effect |
|---|---|---|
| **Bindle on a Stick** | 1 | Witnesses following you move +1 space when you do. (Same as the canonical bindle pickup.) |
| **Diner Rag** | 1 | Every WIPE COUNTER you play gives +1 Time instead of 0. |
| **Booth 6 Notebook** | 1 | Once per game, take the top card of the Reversal deck and look at it. |
| **The Card Within The Card** | hands free | Permanently +1 die on any Threshold Roll made while standing on the CARD WALL space. |
| **Frasier's Wire-Wrapped Pen** | hands free | Once per game, force-convert one failure die to a success on a Threshold Roll. |
| **The Cassette Spine (JOHN_47AM_3)** | 1 | Unlocks the Priestess's archive overlay on the codex — see §VI. |
| **Stale Coffee (cup #4 of the night)** | 1 | Recover 1 health; discard. |
| **The Bell** | 1 | If carried, you can place it on any space. Witnesses within 2 spaces of the bell hear it and move 1 space toward you on their next move. (Risky.) |
| **The Fluorescent Strip** | hands free | Every PAUSE die (Fool die face 2) you roll lowers the Threshold Track by 1 in addition to its other effect. |
| **The Steamboat Echo** | hands free | If equipped, draw the Magician's gallery card as your codex instead — full cross-arcana lore unlock. (Itself unlocked only after a Magician completion.) |
| **AUDI ET TACE Luggage Tag** | hands free | Witnesses cannot panic into the Killer's space. (Universal tag — usable in any arcana run once unlocked.) |
| **The Painted Pose** | hands free | Lore-only. Equip to reveal a Memory token at game end — the deck's class-vision payoff. Unlocked through the Magician's painting-acknowledged thread. |

### IV.7 Event cards (D'Ambrosio's deck)

10 ambient story beats. Drawn at game start (1 revealed) + during
Reversal phase via "WHAT FRASIER WOULD ASK".

1. **STILL CHASING SHADOWS, JOHNNY?** — Frasier enters. Next Action card costs +1 Time. Discard at end of turn.
2. **DAWN-NOT-QUITE-DAWN** — All Threshold Rolls +1 die for the rest of the game.
3. **THE DEMONS ARE RESTLESS TONIGHT** — Place 1 additional witness (the_demon, played by a digital sprite) at the REGISTER.
4. **THE RIVER HAS ITS OWN PROGRAM** — RIVER WINDOW exit closes for 2 turns.
5. **THE GRAFFITI HAND** — FRANKLY / FOOLISH appears on the wall. Reveal a Lore Token: "graffiti signature seen."
6. **THE BBS HUMS** — At end of every turn, draw one card from the Item deck of your choice, face-down. Persists until discarded.
7. **3:47 EXACTLY** — The clock will not move. Time does not reset to 6 next Planning phase. It resets to 4.
8. **WHO TAUGHT YOU TO BE A FOOL?** — Look at the top 3 cards of the Reversal deck. Put them back in any order.
9. **THE FELLOW TRAVELER** — Faith is now adjacent to you, wherever you are, and stays there. She does not panic. (Discard when she's removed from play.)
10. **A SECOND COUNTER WIPE** — All WIPE COUNTER cards in your hand now read "+2 Time" instead of "+1 Time" for the rest of the game.

### IV.8 D'Ambrosio's location board

```
                       PARKING LOT (exit)
                              │
                              │
                    ┌─────────┴─────────┐
                    │                   │
            KITCHEN ALCOVE          BOOTH 6
              [search]              [search]
              [bindle]
                    │                   │
                    ├──── COUNTER ──────┤      ← John starts here
                    │   (named space)   │
                    │      [search?]    │
                    │                   │
                    │   UNDER COUNTER   │
                    │      [Faith]      │
                    │                   │
                    └───── BELL ────────┘
                              │
                          REGISTER
                          [search]
                              │
                          CARD WALL
                       (the gallery card
                        is pinned here)
                              │
                       RIVER WINDOW (exit)
```

Adjacencies follow the diagram. The COUNTER is central. CARD WALL is
a named space where standing on it lets READ THE CARD examine
hotspots one at a time. Search spaces map to the three item piles.

### IV.9 Achievements (drives the unlock progression)

**Coarse tier (per arcana):**
- ☐ Win once at D'Ambrosio's → unlock Fool for play at other locations
- ☐ Win at 3 different locations → unlock alt Fool die (REVERSED FACES)
- ☐ Win at all 7 vol5 locations → unlock the 22-die set
- ☐ 10 cumulative Fool wins → unlock the recursive Fool card as a Setup option in other arcana runs

**Fine-grained card unlocks (per achievement):**
- ☐ Save all 6 witnesses → unlock *Frasier's Wire-Wrapped Pen* item permanently
- ☐ Win without playing WIPE COUNTER → unlock alt action card *Counter Is The Sinkhole* (treats COUNTER as an exit space for one game)
- ☐ Defeat the reversed Fool with Faith adjacent → unlock Faith as a Special Victim in any arcana run
- ☐ Read AUDI ET TACE before Frasier enters → unlock the AUDI ET TACE Luggage Tag as a starting item
- ☐ Reveal all 13 dormant hotspots in one game → unlock *The Painted Pose* item
- ☐ Win with only Zero Cost action cards purchased → unlock *Bare Hands Fool* hand variant
- ☐ Win without any Threshold Roll failures → unlock *The Card Within The Card* item
- ☐ Lose the game by reversal at exactly 8 Reversal Track → unlock the *Reversed Fool* as a Setup option (you play the slippage)

**FG-style achievement page** (mirroring the per-Location and per-Killer pages in the FG rulebook): both the Fool page (defeat Fool reversal at 5 locations, write each name) and the D'Ambrosio's page (defeat 5 different arcana reversals at the diner, write each name) persist across runs in `SaveSystem`. These are display achievements with no mechanical reward beyond filling the page — Final Girl's pure completionist signal.

## V. The play loop in detail

Identical to Final Girl with renamed phases. One turn:

1. **ACTION PHASE.** Play cards from hand. Each card costs Time and triggers a Threshold Roll (or has a 0-cost effect). Use Action cards to move, search, address knocks, wipe the counter, escort witnesses.
2. **PLANNING PHASE.** Spend remaining Time to buy from the action tableau. Time resets to 6 (or 4/5 if a Reversal/Event card said so). Played + discarded cards return to the tableau at end of phase.
3. **REVERSAL PHASE.** Draw the top Reversal card, resolve top-down. The reversed Fool does not have a meeple on the board — it acts through the room itself. Reversal Track +1 each turn unless cancelled.
4. **PANIC PHASE.** Any witness in a space that's "panic-target" (Killer space in FG; here, any space the Reversal card flagged) panics in the indicated direction.
5. **UPKEEP PHASE.** Resolve carried effects, rearrange inventory. Reveal Finale if Reversal Track ≥ 8 OR Reversal deck is empty.

## VI. The hybrid play surface

This is the design choice you picked: **location board + card-as-codex.**

The screen has two zones:

**Left/center: the location board.**
A static map of D'Ambrosio's interior (laid out per §IV.8). Player
meeple, witness meeples, named spaces highlighted. Three search
piles visible. Threshold + Reversal + Time tracks visible above the
board. Hand below.

**Right: the gallery card pinned as codex.**
The actual `assets/gallery/fool.png` rendered at ~30% width. The 23
hotspots from `puzzle_hooks/fool.json` are clickable but
*dormant* — the card is read-only during play. Each hotspot has 3
states:

| State | Visual |
|---|---|
| Locked | hotspot invisible |
| Witnessed | hotspot visible, dim, gold ring |
| Surfaced | hotspot visible, fully lit, glyph attached |

Surfacing happens through play: an Action card (READ THE CARD), an
Event (graffiti hand, painting in Dante's office), an Item (the
cassette spine reveals the Anya cross-card), or an achievement
(unlocked dormant hotspots become visible across all future runs).

The codex IS the meta-progression visible to the player. The card
literally fills in over many plays — by the time you've defeated the
Fool at all 7 vol5 locations, the gallery card looks the way it does
in the design files, with all dormant cross-card hotspots
illuminated and the lore reading bound together.

This makes the gallery card not just art but the *save-file made
visible*.

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

## VIII. The first slice — what gets built

Scope is **Fool only, BETWEEN ACTS scenario, D'Ambrosio's
location.** Concretely:

**Data files** (JSON, authored before any engine code):
```
godot/resources/games/
  _README.md                          ← schema doc
  framework/
    action_tableau_core.json          ← Walk, Focus, Search, Sprint,
                                        Short Rest, Long Rest,
                                        Distraction, Guard, Retaliate,
                                        Close Call, Spend It, Improvise
  fool/
    die.json                          ← 6 faces per IV.1
    setup_between_acts.json           ← per IV.2
    action_cards.json                 ← per IV.3
    reversal_deck.json                ← per IV.4
    finale.json                       ← per IV.5
    items.json                        ← per IV.6
    events.json                       ← per IV.7
    achievements.json                 ← per IV.9
  locations/
    dambrosios.json                   ← map per IV.8
  hands/
    john_frank.json                   ← 5 health, ultimate ability,
                                        save-witness rewards
```

**Engine code** (GDScript, after data is locked):
```
godot/scenes/games/
  TarotGauntletGame.gd                ← main controller, 5-phase loop
  PlayerBoard.gd                      ← Time, Threshold, Hand display
  LocationBoard.gd                    ← map renderer + meeples
  ActionTableau.gd                    ← card market
  HandArea.gd                         ← player hand
  ReversalBoard.gd                    ← Reversal Track + Finale display
  Dice.gd                             ← arcana dice + Threshold Roll
  CardCodex.gd                        ← gallery card pinned, hotspot states
  AchievementPanel.gd                 ← FG-style page
  TarotGauntletGame.tscn              ← root scene
godot/autoload/
  GauntletState.gd                    ← persistent meta-progression
                                        (unlocks, achievement progress,
                                        codex hotspot states)
```

**Save system extension:**
The existing `SaveSystem.gd` gets a `mark_gauntlet_progress(arcana,
location, achievement_id)` method. Gauntlet runs do NOT touch the VN
save slots — they live in a separate `gauntlet_state.json` save file
so completing arcana runs doesn't conflict with linear chapter
progress.

**Hookup to the existing menu:**
The Gallery (which shows all 22 arcana cards) gets a new affordance
per card: "▷ PLAY" appears once the arcana has a built scenario.
Clicking enters TarotGauntletGame. For the first slice, only the
Fool card shows the affordance.

## IX. Open questions for after this doc lands

1. **Action card art.** Final Girl's cards have flavor text + double
   success / single success / failure lines. The Gauntlet inherits
   that structure. Authoring: per-arcana card art? Or generic art
   for the universal cards and arcana-specific only for the 2-4
   unique-per-arcana cards?
2. **The codex's gallery card** — should it be the canonical
   `assets/gallery/fool.png`, or a version with all chrome stripped
   so the hotspot states are visually unambiguous?
3. **Hand variants beyond John Frank.** The Fool's canonical hand
   is John. But the AUDI ET TACE thread suggests Maya could also be
   a Fool-Hand at a different location. Reserve for a later slice?
4. **Reversal music.** The Pomegranate Hour, the music strata, the
   tarot_synth — all suggest the Reversal phase has its own
   soundscape. Tag now, build later.

---

*This doc is the framework spec, not the implementation. Implementation
proceeds in two passes: data files (§VIII) reviewed against this doc,
then engine code wired to consume them. Engine code is not begun until
this doc is signed off.*
