# FEY FAIRE — routes, mirrors, checkpoints, endings

How the player chooses their own path through the game.  The map
of the Faire midway and the six Fairyland sub-realms.  Every
puzzle-gate and every ending mapped concretely.

Sister docs:
- `_FEY_FAIRE_DESIGN.md` · master overview
- `_FEY_FAIRE_MECHANICS.md` · combat + death + checkpoints
- `_FEY_FAIRE_FACTIONS.md` · Court standing gates content

## The Faire midway map (first-person grid)

```
                                                     N
                                                     ↑
    ┌─────────────────────────────────────────────────────────────┐
    │                                                             │
    │                    THE BIG TOP                              │
    │                    (backstage locked                        │
    │                     until Night 4)                          │
    │                                                             │
    │                       │                                     │
    │                       │                                     │
    │  BAKERY               │              BOOKSTALL              │
    │  (Salt Sisters)       │              (Puck's info-desk)     │
    │                       │                                     │
    │                       │                                     │
    │  FUNHOUSE ─ CAROUSEL ─┴─ COTTON CANDY ─ POPCORN             │
    │  (Pooka)   (music box)  (Green Man)     (Hob)               │
    │                                                             │
    │                       │                                     │
    │                       │                                     │
    │  KISSING BOOTH        │              MILK BOTTLES           │
    │  (Baobhan Sìth)       │              (Redcap)               │
    │                       │                                     │
    │  DUNK TANK ─ STRONGMAN │ COIN-IN-GLASS ─ TEST-YOUR-STRENGTH │
    │  (Nuckelavee) (Caliban) (Puck)          (Cobweb)           │
    │                       │                                     │
    │                       │                                     │
    │  POETRY STALL         │              FORTUNE TELLER         │
    │  (Leanan Sídhe)       │              (Sluagh proxy)         │
    │                       │                                     │
    │  FLOWER STALL         │              PEPPER MILL            │
    │  (Peaseblossom)       │              (Mustardseed)          │
    │                       │                                     │
    │  MOTH'S QUIET (10pm+) │              WHEEL OF FORTUNE       │
    │  (Moth)               │              (Erlking)              │
    │                       │                                     │
    │                       │                                     │
    │  FISHBOWL ─ FOUNTAIN─ RING TOSS ─ SLEEP TENT ─ HALL OF      │
    │  (Selkie)  JUMP (Nixie) (Ondine) (Queen Mab · night 4+)     │
    │            (Kelpie · fountain)                              │
    │                       │                                     │
    │                       │                                     │
    │              LOST & FOUND                                   │
    │              (Boggart)                                      │
    │                                                             │
    │                       │                                     │
    │                       │                                     │
    │              THE GATE  (Cricket)                            │
    │                       │                                     │
    │                       ↓                                     │
    │              THE PARKING LOT (exit)                         │
    │                                                             │
    └─────────────────────────────────────────────────────────────┘
```

**Reading the map**: the Gate is south, the Big Top is north, the
midway is the central promenade, booths line either side.  The
Hall of Mirrors sits at the eastern edge (six mirror-doors into
Fairyland).  The Parking Lot is south of the Gate · leaving the
Faire is done through it.

**~48 first-person cells total** on the midway.  Each cell has a
paired backdrop (one 320×180 HeroImage per cell, hand-painted).
Not every cell has a fey · most are transitional (a path with
strung Edison lights, a lamp post, a puddle where a Nixie might
appear once).

## Access rules

- **Nights 1-3**: The Big Top backstage is locked.  Mirror 4 (The
  Green) requires a leaf from outside · you must leave via the
  Gate and return.  Mirror 3 (Court Beneath) requires an Unseelie
  promise-fulfilled.  Mirror 5 (Undertide) is open.  Mirror 2
  (Storm-Wracked Coast) is open.  Mirror 1 (Rose Garden) needs
  Peaseblossom's bouquet puzzle.  Mirror 6 (Dream) opens only
  by sleeping in the Sleep Tent — Sleep Tent doesn't exist until
  night 4.
- **Nights 4-6**: Sleep Tent appears.  Backstage unlocks.
- **Night 6 only**: Morgan le Fey appears at the Big Top IF the
  player is Unseelie ≥ 10.  If not, she watches from the wings.

## The six mirrors (Fairyland sub-realms)

Each mirror is a self-contained first-person grid dungeon
(~15-25 cells).  Corridor backdrops are the sub-realm's palette
overriding the base cream/mauve.  Each ends in a tier-3 boss OR
a peaceful negotiation depending on the player's approach.

### Mirror 1 · The Rose Garden (Seelie)

- **Palette**: cream, rose, deep-green, gold-highlight
- **Gate puzzle**: assemble a bouquet at Peaseblossom's booth of
  six specific rose varieties in the correct order (a diegetic
  logic puzzle — Peaseblossom drops hints about which roses like
  each other).
- **Boss**: Titania.  Recruitable if you win the puzzle without
  cheating AND have Ariel or one of the retinue recruited.
- **Terrain**: rose hedges (bramble walls · take damage brushing
  past), a fountain (heals SP), a garden maze that changes each
  visit (procedural path with fixed rules · not random).
- **Unique fey encounter**: three Nixies swimming in the
  fountain, they may join.
- **Key reward**: a `SEELIE ROSE` (locks alignment if worn).

### Mirror 2 · The Storm-Wracked Coast (Seelie / Tempest)

- **Palette**: storm-blue, foam-white, cream (accent), amber
  lightning
- **Gate puzzle**: recite a specific Tempest line to Ariel while
  the Ferris wheel is at its peak.  The line: "We are such stuff
  as dreams are made on" · quote-tag `tempest-ariel`.
- **Boss**: Ariel.  Recruitable ALWAYS if you speak with him
  before combat.  Ariel wants freedom · offering to release him
  from Titania's service wins him.
- **Terrain**: a beach that shifts under the player's feet, a
  wrecked galleon, a cave with a magical creature (Caliban
  cameo · does not fight yet).
- **Unique fey encounter**: a floating Will-o'-the-Wisp trail
  that leads to a treasure OR a bad end depending on choice.
- **Key reward**: `AIRSPEAK` skill (protagonist can converse
  with Wildfey wind-riders).

### Mirror 3 · The Court Beneath (Unseelie)

- **Palette**: black-plum, deep-purple, bronze accents, cream
  fabric
- **Gate puzzle**: PROMISE a specific service to an Unseelie fey
  (Redcap, Baobhan Sìth, or Sluagh) AND fulfill it before
  crossing.  The fulfilled promise becomes the key.
- **Boss**: Oberon.  Recruitable requires the player to
  successfully play Oberon and Titania against each other · a
  branching dialogue that resolves at the closing scene.
- **Terrain**: a candlelit throne room, a hunt-hall with real
  antlers on the walls, a treasury the player can steal from
  (with consequences).
- **Unique fey encounter**: the Redcap and Baobhan Sìth are
  BOTH here as retainers, if you didn't recruit them at the midway.
- **Key reward**: `TRUENAME` skill (learn the true name of one
  named fey per playthrough, once).

### Mirror 4 · The Green (Wildfey · Green Man)

- **Palette**: forest-green, moss-brown, cream (accent), ochre
- **Gate puzzle**: bring a REAL leaf from outside the Faire.
  This means leaving through the Gate/Parking Lot and returning.
  Doing so consumes an in-game night (advances time).
- **Boss**: The Green Man.  Recruitable ALWAYS if the leaf was
  freshly picked, not bought.
- **Terrain**: a forest floor that reshapes each step, a hollow
  tree that speaks, a clearing where the Green Man holds court
  (silently).
- **Unique fey encounter**: an Ossory Wolf who is completing his
  seven-year term here (year 5).
- **Key reward**: `SEASONAL_SHIFT` (protagonist's damage type
  cycles by round).

### Mirror 5 · The Undertide (Wildfey / Tempest · Caliban)

- **Palette**: teal, salt-crust, cream (surface light), black
  depths
- **Gate puzzle**: win the strongman challenge at Caliban's booth
  fairly · this requires either high `strike`, an iron item, or
  passing a `wit` check (talk him down through PLEAD).
- **Boss**: Caliban.  Recruitable ALWAYS if the strongman was
  won cleanly (no cheating).  Caliban wants a master OR wants
  none.  The negotiation is: convince him he needs neither.
- **Terrain**: an island beach, a specific cave (Sycorax's · his
  mother's · where he was born), sea caves that go down.
- **Unique fey encounter**: Selkie in her seal-form, sitting on
  a rock, telling stories.
- **Key reward**: `MOUNTAIN_STRIKE` (a heavy Bone attack that
  ignores resistance).

### Mirror 6 · The Dream (Wildfey · Queen Mab)

- **Palette**: exactly the palette the player described their
  bedroom as during the boot questionnaire, deepened into
  dream-lighting (mauve edges, gold pools)
- **Gate puzzle**: sleep in the Sleep Tent (available Night 4+).
  The player is transported.  There is no other way in.
- **Boss**: Queen Mab.  Recruitable requires the player to have
  ONE specific dream from their past to tell her (which the game
  extracts from the boot questionnaire's "argument with a parent"
  or "first kiss" fields).
- **Terrain**: the protagonist's bedroom, hallway, and specific
  rooms of childhood.  Every door leads somewhere in the
  player's own history (paraphrased from boot data).  Some doors
  are locked · Mab holds the keys and asks for dreams in trade.
- **Unique fey encounter**: no other feys here.  Mab hunts alone.
- **Key reward**: `DREAM_RIDE` (target moves to your side for
  one round in combat) · plus one recovered memory if the player
  has lost any.

## Checkpoint system (recap from mechanics doc)

**Every recruited fey creates a checkpoint at their manifestation
location.**  On death, the player wakes up at the checkpoint
deepest into their route.  "Deepest" = shortest-path from the Gate
along the midway graph.

### Initial checkpoints
- **The Gate** (always) — if no fey recruited.

### Midway checkpoints (from recruiting a midway fey)
- Ring Toss (Ondine)
- Ferris Wheel (Ariel)
- Poetry Stall (Leanan Sídhe)
- Fortune Teller (Sluagh proxy)
- Test-your-Strength (Cobweb)
- Milk Bottles (Redcap)
- Kissing Booth (Baobhan Sìth)
- Dunk Tank (Nuckelavee)
- Strongman (Caliban)
- Coin-in-Glass (Puck)
- Cotton Candy (Green Man)
- Wheel of Fortune (Erlking)
- Sleep Tent (Queen Mab) [night 4+]
- Big Top (Titania) [after Rose Garden mirror + Titania recruit]
- Backstage Big Top (Oberon) [after Court Beneath mirror + Oberon recruit]
- Flower Stall (Peaseblossom)
- Pepper Mill (Mustardseed)
- Moth's Quiet (Moth)
- Fishbowl (Selkie)
- Fountain (Nixie)
- Popcorn (Hob)
- Lost & Found (Boggart)
- Bakery (Salt Sisters)
- Funhouse (Pooka)
- Bookstall (Cricket · she runs it after-hours) OR (Puck)
- Shooting Gallery (Ossory Wolf)
- Big Top itself (any recruited Big Top NPC)

### Fairyland checkpoints
- Only ONE checkpoint per Fairyland sub-realm, at the boss's
  location.  Recruiting Titania checkpoints in the Rose Garden;
  Ariel in the Storm-Wracked Coast; etc.
- If you die in a sub-realm and don't have that realm's
  checkpoint yet, you wake at the deepest midway checkpoint.

## The seven endings

Ranked from most-common to most-hidden:

### 1. SEELIE ENDING — "A Rose"
Court alignment: Seelie ≥ 10.

You leave the Faire with a rose in your buttonhole.  The rose
does not wilt.  You keep your name, your face, and every friend
you had.  You NO LONGER REMEMBER THE SEASON your specific loss
(from boot questionnaire) happened in.  You catch yourself
humming a Midsummer song at odd moments.  Titania keeps her
promise to you.  Ondine watches you leave through the Gate.
The rose blooms in your buttonhole for exactly one year.

### 2. UNSEELIE ENDING — "A Red Cap"
Court alignment: Unseelie ≥ 10.

You leave the Faire wearing a knitted red cap.  It fits well.
You keep the seasons.  You keep every friend you had.  Your
NAME is different now, and everyone who calls you the old name
gets confused for a moment before you correct them.  You have
to relearn to answer to a name you did not choose.  Oberon
keeps his promise to you (whatever it was).  The Erlking passes
your house at night and does not stop.

### 3. WILDFEY ENDING — "A Stag's Antler"
Court alignment: Wildfey ≥ 10.

You leave the Faire holding a stag's antler wrapped in oiled
paper.  You do not know how to explain it.  You keep everything.
But: you do not really leave.  You are AT the Faire when it
packs up at dawn, and you are on one of the trucks, and you
are there when it unpacks in another town seventeen years
later.  You come back home older, and the town has changed,
and everyone you loved has grown up or died.  You are 32 now.

### 4. REFUSE THE FAIRE — "You walked away"
Player left through the Gate before Night 3 without engaging
substantively.  Requires: fewer than 3 fey recruited, no mirror
crossed, no boss engaged.

Short ending.  Melancholic.  You walk home under a streetlight
that flickers behind you.  You never know what you missed.
Someone at school asks the next Monday if you went to that
carnival that was there over the weekend, and you say no.  You
say no honestly.  You do not remember it.

### 5. BECOME THE FAIRE — "You take Cricket's seat"
Requires: Cricket personal disposition LOVED + all three Court
standings below +3.

Cricket has been at the Gate a very long time.  She would like
to retire.  You accept.  You take the ticket-taker's stool.
You bite the corner off tickets.  Seventeen years pass in one
night.  A new teenager walks up.  You say the same six words
Ondine said to you: "You get six nights."  You mean it.

### 6. BRING BACK THE LOST — "Andrew comes home"
(Or whichever loss the player named at boot.)
Requires: Wildfey ≥ 8, Green Man LOVED, at least one specific
promise fulfilled that matches the named loss, and full
completion of Mirror 4 (The Green).

The Green Man does not speak often.  He speaks now.  He says:
"There is one exchange I will make."  If the lost person was
Andrew, the Green Man asks for **your most-recruited fey**
in trade.  You lose them permanently to Fairyland.  Andrew
comes home in 1976, in the past you cannot revisit, in the
history of a camp you weren't at, and the ripple travels
forward.  On the drive home from the Faire your father tells
you a story about a summer camp he went to as a teen where
they lost a boy · except he didn't · because you gave a fey
back.

(This ending's specific ripple depends on the boot loss.  If
the player named "a friend who moved away" — that friend
writes back to the letter you sent months ago and you didn't
know you'd sent one.  If they named "my father who hits" —
your father dies of a heart attack in the summer of 1988, a
year the player has to look up to know.)

### 7. YOU FORGET WHY YOU CAME — "The Faire keeps you"
Requires: six deaths without any fey recruit.

Bad ending.  Losing all six memories to death.  You are still
at the Faire on Night 7.  The Faire has left already.  You are
alone in an empty lot.  You do not know why you came.  You do
not know your name (the game's boot-questionnaire name still
displays, but the character in the epilogue does not use it).
The screen fades to black.  A cricket chirps.  You (the player,
not the character) know what that means now.

### Hidden variant · QUEEN MAB KEEPS YOU
Requires: Complete Mirror 6 but do not return before Closing Night.

Mab does not release you.  She is very sorry about it.  You are
now a dreamer she visits nightly.  The credits play in a script
you cannot read while she reads them aloud in your voice.

## The player-choice map (early → late)

```
NIGHT 1:  Enter Faire → meet Ondine → wander midway
          ↓
        Choose: recruit a low-tier fey?  which one?
          ↓
NIGHT 2:  6 booths available, 4 mirrors accessible
          ↓
        Choose: which mirror first?  (Rose Garden puzzle · or
        Storm-Wracked Coast if you already learned Tempest)
          ↓
NIGHT 3:  Reveal · Ondine tells you the Faire is a threshold.
          Backstage locked.  Third mirror puzzle plays out.
          ↓
        Choose: which Court to gain standing with?
          ↓
NIGHT 4:  Backstage unlocks.  Sleep Tent appears.  Mirror 6
          becomes accessible.  Now you can meet Oberon.
          ↓
        Choose: attempt Titania+Oberon reconciliation, or pick a side?
          ↓
NIGHT 5:  The Faire feels different · at 3am the ticket-taker
          asks you a question.  Your answer shifts factions.
          ↓
        Choose: pursue the seventh hidden ending (Bring Back the
        Lost) if you have the requirements?
          ↓
NIGHT 6:  Big Top show is YOU.  All unfulfilled promises come
          due one by one.  Alignment locks.  Ending fires.
```

## Design invariants

- **No wrong choice at boot.**  Every boot-questionnaire response
  has authored content.  No matter what the player says, the
  Faire has an angle on them.
- **Every fey on the roster CAN be met.**  Even the most-hidden
  fey (Morgan le Fey, Nuckelavee if you don't visit the dunk tank)
  can be encountered somewhere.  A comprehensive run finds all 29.
- **Every ending is REACHABLE from a fresh start.**  No ending
  requires NG+ knowledge (though NG+ makes some easier).
- **The Faire is not a puzzle to be SOLVED.**  It's a threshold
  to be crossed.  Every ending is valid.  Every ending is Rocha
  saying something specific about surviving.

## Implementation checklist

- [ ] Midway map file (`midway.json`) · 48 cells with backdrop
      references + fey placements + adjacency graph
- [ ] Six mirror map files (`mirror_1_rose_garden.json`, etc.) ·
      ~15-25 cells each with backdrops + boss placement + unique
      fey encounters
- [ ] Checkpoint list (`checkpoints.json`) · cell IDs and their
      unlock conditions (which fey recruited)
- [ ] Boot questionnaire (`questionnaire.json`) · question tree +
      how answers slot into game state
- [ ] Ending scripts (`endings/`) · seven ending screenplays with
      variable substitution for boot-questionnaire answers
- [ ] Standing / disposition tracker (`factions_state.gd`)
- [ ] Diegetic time-of-night indicator (a paper crescent moon
      hanging above the midway that fills as the night advances)
