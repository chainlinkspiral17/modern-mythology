# FEY FAIRE — the Trailer

The player's home base for the six nights.  Party management,
keepsake collection, compendium, map, hearth.  Persistent
across deaths.  The one place on the Faire's grounds where the
fey do not have jurisdiction.

Sister docs:
- `_FEY_FAIRE_DESIGN.md` · master overview
- `_FEY_FAIRE_MECHANICS.md` · combat, death, checkpoints
- `_FEY_FAIRE_FACTIONS.md` · Court hierarchies
- `_FEY_FAIRE_ROUTES.md` · midway map, mirrors, endings

## Premise

At the edge of the Parking Lot, past the last row of cars and the
generator shack, is a **1970s Airstream trailer** on cinderblocks.
It hasn't moved in a while.  The door is unlocked.  The lights
inside are on.  Someone has been living here recently · they still
might be.

The trailer belonged to **PROSPERO**.  The one from The Tempest.
Caliban's former master.  Prospero, having drowned his books, no
longer needs it.  Whether he is dead, retired, or simply
elsewhere is up to Rocha's private interpretation — the player
never meets him.  His **cat** is still there and doesn't leave.

Unlocking the trailer is the first substantial choice the player
makes.  It requires: walk past the Gate on Night 1, keep walking
south past the Parking Lot's last row, and open the door.  The
game does not tell you this is possible.  A Bookstall paperback
("Prospero's Notes") hints at it.  Some players will find the
trailer on Night 1.  Some never find it.

## What the trailer contains

Layout (a first-person interior, 6-8 cells):

```
      ┌──────────────────────────────────────────────┐
      │                                              │
      │  BEDROOM AREA                     KITCHENETTE│
      │  (four cots, one bunk-tier)       (hearth ·  │
      │  (recruited feys sleep here)      (HP heal · │
      │                                    no night  │
      │                                    advance)  │
      │                                              │
      │  BOOKCASE                         WRITING DESK
      │  (keepsakes · trinkets ·          (journal ·  │
      │   lore fragments · one per         compendium ·│
      │   shelf slot)                      map)       │
      │                                              │
      │  MIRROR (six · one per memory)  ┌──────────┐ │
      │                                 │ THE      │ │
      │                                 │ CAT      │ │
      │                                 │ (sleeps  │ │
      │  WINDOW (looks out on            │  on the  │ │
      │  current mirror-alignment)       │  table)  │ │
      │                                 └──────────┘ │
      │                                              │
      │                    DOOR                      │
      └──────────────────────────────────────────────┘
```

### The cots · party roster

Four cots along the north wall.  Each cot represents a party slot.

- **Cot 1 — protagonist** · always taken.
- **Cots 2/3/4 — recruited feys** · rotate freely.

At the cot the player can:
- **DISMISS** a recruited fey (they return to their manifestation).
- **INVITE** a recruited fey who is currently at their manifestation.
- Reorder the party (front row / back row).

A dismissed fey does not FORGET the player.  They remember the
recruit and greet them at their booth · they simply aren't in the
active party.  Recruits can be re-invited at any time.

**Party count is unlimited on the roster.**  Only 3 can be ACTIVE
in the party at once (protagonist + 3).  This means the player
builds a stable of dozens of allies and rotates for each
challenge.  This is the SMT-Compendium hook · you collect them,
you choose whom to bring.

### The hearth · HP restore

Kitchen nook.  Small stove, teakettle.  Making tea heals the
protagonist to full HP without advancing the night.  Costs one
LEAF from a specific Wildfey (Peaseblossom, Green Man, or any
Hob).  If none available, hearth is cold.

Tea does NOT restore SP.  For SP you must REST at a fey booth,
which advances the night.

### The bookcase · keepsake collection

The trailer's central mechanic and the one that most rewards
completionists.  ~40-50 keepsakes across the game.

Each keepsake:
- **Occupies one shelf slot** on the bookcase (the bookcase has 20
  slots; the rest are stored in a footlocker).
- **Has a lore text** — a short passage explaining what it is and
  where the player found it.
- **Provides a passive effect while ACTIVE** (on a shelf).
- **Can be swapped in and out** freely at the bookcase.
- **20 active** at any time.  The other 20+ are locked in the
  footlocker.

Keepsake categories:
- **Trinkets** · found or gifted (17 keepsakes) · combat and
  negotiation buffs
- **Lore fragments** · reading them fills the compendium
  (12 keepsakes) · pure information, no mechanical effect
- **Playbill pages** · from Big Top shows (6) · each grants +1 to
  the RECITE cap for a specific play
- **Cat gifts** · the cat brings you things once she trusts you
  (6) · unusual effects
- **Prospero's remnants** · items belonging to the previous
  tenant (6) · unlock hidden content

See `keepsakes.json` for the full catalog.

### The writing desk · compendium + map + journal

Three interconnected panels:

- **Compendium**: 100+ fey entries, unlocked as the player meets
  them.  A met fey is a portrait + one line (`YOU MET THEM at
  the wheel of fortune, night 3`).  A recruited fey is portrait +
  full page (stats, court, prize, name, request, quote).  A
  defeated-not-recruited fey is portrait + partial page (missing
  the prize and true name).
- **Map**: the Faire midway.  Fills in as the player explores.
  Colored dots mark: recruited feys (gold), defeated feys (red),
  met-only (grey), unexplored (blank).  Fairyland sub-realms
  appear on the map ONLY after the player enters each mirror.
- **Journal**: a running diary of the run.  Auto-generated from
  significant events (fact-discoveries, in Pirate Summer's
  parlance).  Editable by the player (rare in games · a quiet
  choice) · adding a note gives you the option to inflect a
  future ending.

### The six mirrors · memory tracking

Along the wall opposite the cots.  Six small circular mirrors,
each faintly reflecting a different room · matching the six
memories from the boot questionnaire.

- On boot, each mirror shows a slightly-blurred still image of
  the memory.
- When a memory is lost to death, that mirror **cracks**.  The
  image remains but the crack persists.
- Six cracked mirrors = the trailer's door will not open on the
  next death.  You are locked out.  That's the YOU_FORGET_WHY_YOU
  _CAME bad ending.

The mirror system is entirely diegetic · nowhere in the UI does
the game say "you have lost 3 memories."  It's the mirrors.

### The window · alignment reflection

North-facing window that never shows the actual Parking Lot.
Instead, it shows a specific view based on the player's current
strongest Court standing:

- **Seelie primary** · a rose garden in bloom, cream and pink.
- **Unseelie primary** · a hunt-hall at dusk with antler chandeliers.
- **Wildfey primary** · a forest floor with mushrooms and moss.
- **No court dominant** · the actual Parking Lot, rendered lovingly.

The window is diegetic feedback on the player's alignment.  The
UI does not show court scores; the window shows their meaning.

### The cat · disposition indicator

Prospero's cat.  Always in the trailer.  Sleeps on the writing
desk unless disturbed.  Named **HELIA** (Prospero named her; she
never answers to it).

The cat has one function: she indicates how each recruited fey is
feeling about the player.  Approach a cot with a sleeping fey and
Helia's tail flicks a specific direction:

- **Tail slow left-to-right** · fey LOVED
- **Tail still** · fey LIKED / NEUTRAL
- **Tail twitching** · fey WARY
- **Cat hisses** · fey HATED

Helia does not indicate court standing · only per-fey personal
disposition.  She's silent about the ones you haven't recruited.

Helia never leaves the trailer.  She never lets herself be
petted.  On specific rare nights (after specific keepsake
milestones) she brings you a gift left on the writing desk.
This is one way to earn the "cat gift" keepsakes.

## Unlocking the trailer

The trailer is not unlocked automatically.  Three ways to find it:

1. **Wander south past the Parking Lot** on any night.  The player
   who explores every cell of the map will find the trailer by
   Night 2.
2. **Read "Prospero's Notes"** at the Bookstall (available Night 1
   for 2 gold).  The paperback describes the trailer's location.
3. **Ask any tier-3 fey where Prospero went**.  Caliban, Ariel,
   and Titania each have specific dialogue about it.  Ariel is
   the most helpful; Caliban is the most bitter.

Once found, the trailer is your home base for the rest of the
run.  It carries across deaths.  It is your ONLY stable point in
the fiction.

## The trailer as anti-Faire

Thematic point: the Faire is a threshold.  The Trailer is a
threshold that goes the OTHER WAY — back toward the mundane.
Prospero unwound his magic here.  His books are in the writing-
desk drawer, waterlogged.  His broken staff is in the umbrella
stand.  The Trailer is where fey magic doesn't quite work.

Practically: **no fey can enter the trailer uninvited.**  This
means the player can:
- Rest safely
- Dismiss and re-invite party members without a fey overhearing
- Read Prospero's compendium (which is critical of specific
  feys · reading Titania's entry aloud in Titania's presence
  would insult her; reading it in the trailer is fine)
- Cry, if it comes to that.

## Keepsakes — the twenty active slots

The bookcase has **20 active slots** and a footlocker for the
overflow.  Each active keepsake provides its passive effect.
Some effects stack (three "small Wildfey keepsake" trinkets each
give +1 to Wildfey standing gain per event) and some don't
(only one "Titania's rose petal" can be active).

**Rearranging keepsakes is a free action inside the trailer** ·
doesn't advance the night, doesn't cost anything.  The
strategic depth is: which 20 do you carry into a specific
challenge?

Example keepsake load-outs (see keepsakes.json for the full list):

**"The negotiation build"** · +30% negotiation success
- Ondine's Postcard from the Coast
- Prospero's Book of Diplomacy
- The Silver Whistle
- Peaseblossom's Handkerchief
- Any Salt Sister's Recipe Card
- 15 more...

**"The Unseelie build"** · +Unseelie standing gain, +Bone resist
- Erlking's Antler Comb
- A Redcap Feather
- Baobhan Sìth's Kissing-Booth Receipt
- The Sluagh's Wind-Chime (broken)
- 16 more...

**"The pacifist build"** · buffs to non-combat only
- Ariel's Air-Song Notation
- The Green Man's Dried Oak Leaf
- Cricket's Retired Ticket
- Prospero's Waterlogged Book
- 16 more...

## Trailer scrapbook (cross-Oneironautics)

The keepsake collection doubles as **the game's scrapbook**.  When
Andy Link (Pirate Summer's protagonist, who is playing Fey Faire
in the outer game) sees the Trailer's keepsake collection, it
reads as Rocha's actual scrapbook — filled with items from her
life she processed into the game.

Specific keepsakes are cross-Oneironautics lore tokens:
- **A silver whistle** · found in Caliban's booth (Undertide
  mirror completion) · IS the whistle from Pirate Summer's
  leather satchel.  Unlocks a specific Pirate Summer scrapbook
  chain fact.
- **A folded music-box tune (Portuguese)** · earned by playing
  Wilson's tune at the Carousel · IS the melody Wilson
  hums in Pirate Summer.
- **A photograph, cream-bordered** · earned by asking the Green
  Man about the 1976 incident directly (specific dialogue
  option available only if Wildfey ≥ 8) · IS the photograph
  in Pirate Summer's east-forest cache.

Every scrapbook keepsake that's cross-Oneironautics unlocks a
matching Pirate Summer scrapbook entry when the player next
returns to the SlowstockShelf.

## Implementation notes

- **Trailer scene**: a first-person interior with 6-8 cells.
  Cell backdrops are HeroImage-scale, painted in a warmer,
  more-mundane palette than the Faire (dust, sunlight through
  yellowed curtains, a bare bulb).
- **Roster storage**: JSON-serializable list of recruited fey
  IDs + their personal disposition state + their status
  (in-party / dismissed).  Persisted per save slot.
- **Compendium storage**: dict `fey_id → encounter_state`
  where state is one of `unmet | met | fought | defeated |
  recruited | dismissed | dead`.
- **Keepsake storage**: two arrays — `active[20]` and
  `footlocker[]`.  Effects computed by iterating `active`.
- **Cat state**: nothing to persist; her tail-flick is a
  view-only function of the currently-selected cot's fey.
- **Map storage**: dict `cell_id → explored: bool`.
- **Journal storage**: array of timestamped auto-notes + array
  of player edits.  Both feed into the ending script.

## The trailer's endings-adjacent role

- **REFUSE_THE_FAIRE ending**: if the player never enters the
  trailer, this ending's epilogue is DIFFERENT than if they did.
  Having entered but chosen to walk away is a knowing refusal.
  Never having found it is ignorance.  Both endings play; the
  latter is sadder.
- **BECOME_THE_FAIRE ending**: the player takes Cricket's stool
  at the Gate.  The trailer stays where it is.  Someone else
  (maybe you-plus-seventeen-years) will find it.  Prospero's cat
  now lives with them.
- **BRING_BACK_THE_LOST ending**: the trailer's writing desk
  drawer, after the ending, holds a NEW photograph.  Of the
  person you brought back.  Sitting where they should have been
  all along.  This is diegetic feedback the player finds by
  reopening the save after the credits.
