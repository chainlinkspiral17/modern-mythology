# Wave 3 · Cards That Remember, Decks That Change Shape

Wave 2 made the **world** persistent — runs leave marks on each
other, doctrine bleeds across arcana, companions ride along. Wave 3
makes the **deck** persistent in the same way. Cards remember being
played. Hands change shape between runs. Verbs gain counterspells.
The card itself becomes a story object, not just a token.

If Wave 1 was *here are the rooms* and Wave 2 is *the rooms know
about each other*, Wave 3 is **the cards in your hand are no longer
the same cards as last week**.

## What changes for the player

### The Living Hand

Your starting hand is no longer a static list. Each card carries a
small invisible state — *played-count, last-space, last-visitor,
last-mood* — that persists between runs in the same arcana. The hand
panel before a run shows the deck the same way, but a card that's
been played eight times across the saga reads slightly different.

The first time a card "levels" (rules below), the player sees a
small wax-seal flash on the picker. The level-up is permanent for
that hand. If you reset the chapter, you reset the hand back to
freshman.

### Verb Counterspells

In Wave 1/2, when you play a card on a visitor, it lands. In Wave 3,
some visitors refuse. A visitor in *intense* mood at high doubt can
**refuse a deliver** — the card resolves, but with the deliver step
not advancing. The verb cooldown still consumes. This is the first
time the room can say no.

The refusal is narrated, not punished — it's a beat, not a fail.
Sammy at the well refusing a TELL HIM card while Dante is on the
stair feels like Sammy. The card returns to the discard pile carrying
a `was_refused_at` flag that some later cards read off.

### Refusal as a Played Card

Parallel to the above, the player gains the inverse: cards that
**don't do** the verb on purpose. The Chariot cameo's
`dont_say_what_youre_thinking` proved the shape; Wave 3 makes it
universal. Each hand gets one refusal card whose flavor is hand-
specific:

- Frasier · LET THE BENCH STAY EMPTY (skip a build verb, gain fuel)
- Elicia · DON'T HIT RECORD (skip a record verb, gain insight)
- Antonio · DON'T TAKE THE EXIT (skip a leap, sit one more turn)
- Mackenzie · DON'T PICK UP THE THREAD (skip a focus, lose stagnation)
- John · CLOSE THE NOTEBOOK (skip a search, gain sanity)
- Nicola · DON'T POUR THE WATER (skip a pour, gain authority)
- Dante · DON'T COME DOWN THE STAIR (skip a walk, hold the room)
- Quentin/Paul · DON'T MAKE THE CALL (skip a phone, gain doctrine)

These cards are the verb of restraint. They're free-cost. They
ledger differently — a run where you played three refusal cards
writes a `held_back` doctrine token.

### The Witness Slot

A *second* hand sits on the right edge of the play area through your
run. Not playable in the normal sense — they're the witness. Once
per run you can spend a TURN to give them a verb; what they say is a
card from their deck, played in their voice, at your space.

This is single-controller, asynchronous co-play. You pick the
witness on the picker (canon hands only). The witness's presence
changes the ambient pool — Elicia as a witness on a Frasier run adds
cassette-deck ambients. The witness's own ledger gets one tick per
run they witness, separate from playing.

### The Drift Zone

Some spaces in some scenarios are now **drift attractors** with
teeth. Standing on one for two turns causes a card in your hand to
**mutate** — the engine picks a card and rewrites one of its effects
to a thematically-adjacent variant. The mutation persists for the
run. (For example: WALK at the back corridor mutates into SHORT
WALK — same cost, different effect. WALK at the church mutates into
PILGRIMAGE.)

The mutated card is the same card with a new face for the rest of
the run. The Living Hand state remembers it mutated; future runs
draw a small chance of starting with the mutated form.

### The Composted Deck

Cards you BURN, EXHAUST, or REFUSE in any run land in a per-arcana
**compost pile**. The pile is visible on the gallery as a small ash
pile next to the chapter. It's not just a graveyard — at certain
ledger milestones (5 burns, 10 burns, 22 burns), the compost yields
a new card you can draft into the hand. The flavor: the things you
discarded come back changed.

## Evolving card mechanics

This is the spine — the cards themselves evolving. Twelve mechanics,
each one a play-test target.

### 1. Card Levels

A card played `N` times across runs in the same hand gains a level.
Each level adds one effect line, never replaces. Three levels max.
The effect-line additions are hand-specific:

```
WALK · L1 → +1 effect: lose 1 stagnation if you walked through a threshold last turn
WALK · L2 → +1 effect: while in motion, refuse cost penalty is -1
WALK · L3 → +1 effect: walking past a connected visitor advances them 1 step
```

Implementation: `_card_level_state[hand][card_id]` persisted via
SaveSystem; effect-line table per (hand, card_id, level).

### 2. Card Erosion

A card played in the *wrong* mood/space too many times loses an
effect line. Cards have a list of "bad-pairings" — RECORD at the
warehouse, BUILD in the cathedral, POUR on the iron stair. Five
bad-pair plays drops the card's primary effect for the rest of the
saga (until composted and rebought).

Erosion is the price of overplaying a deck out of context.

### 3. Mood-Coupled Cards

Card effects shift by the target visitor's mood at the moment of
play. Same card, different outcome:

```
LISTEN · target talkative → +2 patience to target, gain 1 insight
LISTEN · target preoccupied → +1 patience, gain 2 insight
LISTEN · target intense → +0 patience, gain 3 insight, +1 doubt
LISTEN · target lonely → +3 patience, target's accent color saturates
```

Encourages reading the room before playing the verb.

### 4. State-Carrying Cards

A card "remembers" the last space it was successfully played at. A
played card carries `last_space` on it. Some cards trigger different
effects if played at the same space twice or at a different space.

WIPE THE COUNTER, played at the counter twice in a row, mutates into
WIPE THE SECOND TIME — slightly cheaper, slightly stranger.

### 5. Two-Handed Cards (Companion Required)

New card class that REQUIRES a companion (Wave 2's Companion Slot)
to be present. Two-handed cards multiply the companion's connection
progress by 2 for one verb and consume the companion's `help_with`
charge. Big swing — rare to play.

Examples:
- WORK IT OUT TOGETHER · Frasier + Antonio companion
- HOLD THE FRAME · Mackenzie + Elicia companion
- SAY IT AGAIN, SLOWER · John + Nicola companion

### 6. One-Saga Cards

True one-shots. If played in any run in any chapter, removed from
every future run across the saga. These are loud, decisive cards
attached to canon moments. Each hand gets exactly one:

- Frasier · BURN THE WORKBENCH (clears all stagnation, ends the run)
- Antonio · TELL DAD THE NUMBERS (writes a saga flag, locks the ch20
  emperor scenario into "the conversation happened" branch)
- Elicia · ERASE THE TAPE (loses the run, but removes one ledger
  token of player's choice)
- Mackenzie · CUT THE LAST THREAD (skips ahead to the leap)
- John · WRITE THE STORY (publishes — locks Paul's next scenario)
- Quentin/Paul · BURY THE ENVELOPE (locks Antonio's wreck-day flag)

These are saga-altering. They're the only cards the ledger marks
red.

### 7. Card-as-Visitor

A class of card that, when played, spawns a visitor at the player's
space that follows them. The visitor has its own four verbs and is
treated as a normal visitor for connection-completion. The played
card becomes the visitor, leaves the hand permanently for the run,
returns to the deck at run end (or, if completed, composts).

Examples:
- THE FOLDED LETTER (Empress) — visitor: the letter you've been
  carrying; verbs: read / sign / fold / send
- THE TAPE IN MY BAG (Priestess) — visitor: the tape; verbs: hold /
  rewind / cue / play
- THE PHONE NUMBER ON THE NAPKIN (Lovers) — visitor: the number;
  verbs: copy / call / lose / keep

### 8. Threshold-Cards

A card that, when discarded, **becomes a threshold space** on the
board for the rest of the run. Lets the player improvise a leap
point. Once placed, the threshold has its own ending lore token.

OPEN A SIDE DOOR · costs 2 time · places a SIDE DOOR threshold at
your current position adjacent to your last walked-through space.

### 9. Compound Verbs

Playing two cards in the same turn on the same visitor triggers a
combo effect. The combo is keyed by the VERB tags, not the card
IDs — so any LISTEN + DELIVER on the same visitor in the same turn
fires the "told them what you heard" combo.

Twelve combos, one per pair, each with a small effect:
```
LISTEN + DELIVER → +1 step to the visitor, +1 insight
GREET + DELIVER → connection bonus +1
SIT + LISTEN → sanity +1, the visitor's mood softens one tier
SEARCH + GREET → reveals a hidden visitor at your space
... (eight more)
```

### 10. Inverted Cards

Each card carries an *upright* face (the normal effect) and a
*reversed* face (a darker variant) hidden until a doubt threshold
trips. Above doubt 5, the player's card icons flip; the same card
plays its reversed effect.

WALK upright: lose 1 stagnation.
WALK reversed: lose 1 stagnation, gain 1 doubt, advance one
threatening visitor by 1 step.

This is the first system that makes high-doubt runs feel *worse* in
a way the cards themselves register, not just the room's flavor
text.

### 11. The Verb Cooldown Web

Each verb tag (WALK / FOCUS / SEARCH / DELIVER / LISTEN / etc.) is
on its own per-turn cooldown. Playing two LISTENs in one turn is
allowed but the second is +1 cost. The cooldown graph creates
preferred sequences — the player learns the rhythm.

Engine: a `_verb_uses_this_turn` Dictionary, consulted by cost
resolver.

### 12. Card Echo

When a card resolves, its title is added to a small "echo" list
visible at the bottom of the play area, last 5 plays. Some cards
(rare, drafted) read the echo and trigger only if a specific card
was played 2/3 turns ago. EXAMPLE: WAIT FOR IT triggers if LISTEN
was the previous play.

The echo makes the card text into a poem the player slowly composes
across a run.

## Sequencing for Wave 3

Five phases. Each is independently shippable.

1. **The Living Hand + Card Levels.** The smallest persistent change
   with the loudest player feedback. The wax-seal level-up flash is
   the moment the system clicks.
2. **Mood-Coupled + State-Carrying cards.** Pure card-rule additions,
   no new cards needed.
3. **Refusal cards + Verb Counterspells.** The first "no" both ways.
4. **Card-as-Visitor + Threshold-Cards + Compound Verbs.** The
   structural additions — cards that change the board.
5. **One-Saga Cards + Inverted Cards + Verb Cooldown Web + Echo.** The
   saga-level polish layer.

## Out of scope for Wave 3 (held for Wave 4)

- Minor arcana scenarios (held).
- Multi-hand convergent scenarios.
- The Procession endgame.
- The Witness Replay (the watch-the-replay-back system, separate
  from the Witness Slot).
- Procedural visitor / card generation.

## Wave 3 success criteria

- The player sees a card level up at least once in their first hour.
- The player encounters a refusal (their card refused by a visitor)
  at least once per arcana.
- The player plays a refusal card in at least one run and feels
  rewarded for it (ledger entry, narrative beat).
- The player notices the same card behaving differently in two
  different runs (mood-coupling).
- At least one One-Saga Card is played by the median playthrough,
  and the player feels the weight of it.

If those five land, the deck stops being a tool and becomes a
character.
