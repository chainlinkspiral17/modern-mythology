# Pirate Summer · Design Doc

> Oneironautics Inc. · 2002 · Oneironautics Slowstick Rev 3
> Design lead: Marc Ostrom · Party dialogue on four campers +
> Wilson Ashe: Ines Rocha (her first credit)
> Player time: ~12-14 hours base · +4-6 hours Counselor Mode
> Cabin roster: 14 campers · 3 counselors · 4-member party
> Setting: Camp Sweetgum, on the Oregon coast, July 1994
>
> **Vibe**:  *Goonies* meets *Earthbound* meets *Ultima 7*.
> Kids on the Oregon coast, treasure map that isn't a
> metaphor, ghost pirate whose reveal is a real dungeon, and
> a summer camp overworld where every object has a use.

## Scope

Pirate Summer is the **Wave 2** slowstock unlock alongside
Estuary 2. It is a full-scale pixelart JRPG/CRPG hybrid ·
the *big* game on the shelf. Roughly the same authoring
weight as Estuary 3.

The player is **Sam** (same Sam as Estuary 3 — this is Sam
at age eleven, in July 1994), one of fourteen campers at
Camp Sweetgum. Sam explores the camp overworld, befriends
cabin-mates, forms a party, solves puzzles, uncovers
buried secrets, and — if the player plays attentively —
discovers that Wilson Ashe, the tall quiet counselor, is
a pirate.

Not a light-sim. A real game with real systems.

## In-fiction premise

Camp Sweetgum has run for forty-two summers in 1994. Head
counselor **Jenny Copeland** has been coming here since she
was ten. Archery instructor **Bear Roland** catches fish
before breakfast. New this summer: **Wilson Ashe**, thirty-
one, tall, quiet, a canvas bag he does not let out of his
sight.

The buried treasure map is real. It is under **The Old
Man**, a downed spruce at the north end of camp. It was
placed there by Wilson Ashe in 1988. Wilson has known this
for six years. He has, until this summer, never brought a
camp session close enough to matter.

Something is different this summer. The player will
discover, if they investigate, what.

## Design pillars

1. **Goonies energy, not Encyclopedia Brown energy.** Real
   stakes, real danger (not lethal — this is a summer camp
   for children — but real *loss* possible), real
   consequences to poking the wrong nest.

2. **Party is the point.** Sam does not do this alone. Sam
   makes friends, brings friends along, and the party's
   composition determines which puzzles are solvable. A
   solo run is possible and legibly harder.

3. **Ultima 7 depth of systems.** Every visible object is
   interactable. Take, drop, use, combine, cook, eat, wear,
   read, tune, throw. The map is walkable to any coordinate.
   The cave system has real geography that can be lost in.

4. **Earthbound's tonal register.** Small-town Americana
   sincerity, weird-but-earnest oddball encounters, a
   soundtrack that respects the summer instead of
   soundtracking it. Cousin to *A Boy and His Blob* and
   *Chrono Trigger*, not *Final Fantasy 6*.

5. **No calendar walkouts.** Missing an activity doesn't
   fail anything. Time advances when Sam sleeps. Sleeping
   is optional up to a fatigue ceiling. The camp week runs
   long if the player wants it to; the ending unlocks on
   Saturday regardless of how you got there.

6. **Cross-Oneironautics lore is a scavenger hunt.** Hidden
   throughout the camp, obscure enough that only players
   who own the full Slowstock library will notice. See
   §Cross-Oneironautics lore.

## Structure · six days, plus an open ending

Days advance when Sam sleeps in the cabin. There are
scripted anchor events per day (opening campfire Sunday,
homesick night Tuesday, treasure map appears Thursday,
etc.), but the player is free to explore the whole
overworld between anchors.

| Day | Anchor event(s) | Windows opened |
|-----|-----------------|----------------|
| Sun | Arrival · name game · opening campfire | Cabin Sturgeon, mess hall, activity board |
| Mon | Swimming class · archery · Reptile Skit | Alder Pond dock, archery range, target shed |
| Tue | Canoes · tie-dye · Homesick Night | Boathouse (locked · Wilson has key), tie-dye tables |
| Wed | Hike to north bluff · scavenger hunt · Ghost Pirate Play | The Old Man is now walkable-to · scavenger unlocks caves entrance |
| Thu | Free swim · **the map appears** · Talent Show | The map · Ollie-Fisk-nearly-drowns beat · Nika sneaks out |
| Fri | Archery finals · closing bonfire · **free time (mystery window)** | The caves are open · the ghost ship visible from the north bluff after dusk |
| Sat | Departure · endings resolve | (all locations close) |

Sat's departure is soft. The player can walk out early on
any day (there's a bus stop half a mile down the road that
leads to Depoe Bay); doing so ends the run with the *left
camp early* variant of the current-friendship ending.

## Party system

Sam always leads. Up to 3 additional party members join
Sam in the field. Composition can be changed at the mess
hall, at Sam's cabin, or by asking a party member to head
back on the field ("Priya, go back to the cabin, I need to
swap for Nika").

### Friendship meter

Each of the fourteen campers has a friendship meter (0-5).
Friendship rises through:

- Doing an activity together (+1 per shared activity, cap
  at 3 from activities alone)
- Giving a preferred item as a gift (+1 · each camper has a
  small preferred-items list · e.g. Bea Hallowell loves
  smooth river stones · Elias Wren loves used lens caps)
- Making a specific choice at a per-camper story beat
  (+1 · these are the moments the writing was written
  around · e.g. sitting with Danny during Homesick Night)
- Solving a puzzle together (+1, once per camper)

At friendship 3, the camper joins Sam's party on request.
At friendship 5, the camper teaches Sam their party skill
(Sam can still use it if the camper isn't in the party ·
this is what makes late-game solo runs feel earned rather
than punished).

### Party skills · each camper has one

Only six of the fourteen campers have per-camper endings
(Tessa · Wu Kai · Nika · Elias · Danny · Wilson · see
§Endings). But **all fourteen** have a party skill that
opens or clarifies content:

| # | Camper            | Party skill                                | Opens |
|---|-------------------|--------------------------------------------|-------|
| 1 | Tessa Ansen       | PLAN AHEAD · shows counselor patrol paths  | Sneaking past Jenny · timing the Old Man dig |
| 2 | Wu Kai            | READ THE SIGN · decodes archaic script     | The Portuguese shanty · the coordinates in the Ghost Pirate script |
| 3 | Marisol Cortez    | LEAD THE PARTY · +2 to any social check    | Convincing counselors to allow late-night swim · getting kicked-out unstuck |
| 4 | Danny Broz        | CRY ON CUE · counselors lower guard        | Getting out of trouble · getting Bear to let you use the good canoe |
| 5 | Reggie Vandermeer | DAD'S BOAT KEYS · unlocks boathouse door   | The boathouse dungeon on Tuesday · a shortcut for the caves |
| 6 | Sylvie Nakagawa   | SING TO THE HERON · lures animals close    | The Alder Pond heron scene · the raccoon in the mess hall |
| 7 | Ollie Fisk        | HOLD YOUR BREATH · long-swim stretches     | The underwater passage in the caves · retrieving items from the pond floor |
| 8 | Bea Hallowell     | ROCKS FOR CLIMBING · scale short cliffs    | The north bluff shortcut · reaching the roof of the mess hall |
| 9 | Amelie Rocha      | GRAY IS HONEST · sees through disguises    | Recognizing Wilson's tattoos · reading the ledger in Wilson's bag |
|10 | Xavier Lund       | THE JOKE · distracts NPCs for a full turn  | Stealing back a confiscated item · getting past Bear |
|11 | Priya Sundar      | ALLERGY WARNING · notices trace substances | Detecting the pond-scum residue on Wilson's boots · finding the buried bottle |
|12 | Elias Wren        | BIRD IS THE WORD · spots hidden objects    | Finding the bottle on the beach · nests with items · caves markings |
|13 | Nika Voss         | SNEAK LIKE A CAT · bypasses lockable doors | Anywhere Sam shouldn't be · Wilson's cabin at 2 AM |
|14 | Ford Mears        | MARINE LOGIC · reads tide charts + wrecks  | The ghost ship's approach window · the shipwreck in the caves |

**Design note:** Any of the fourteen can be in the party
regardless of ending eligibility. Sam can befriend Reggie
Vandermeer (no per-camper ending) and still finish with the
Wilson ending. But Reggie's DAD'S BOAT KEYS opens the
Tuesday boathouse three days early — a genuinely different
run. Every camper has a niche.

## Combat / encounter system

No violence. Kids at camp. Instead, five encounter types:

### 1 · Skill checks

Climb, swim, aim, run, hold breath, listen. Rolled against
a difficulty. Party members can help via their skills or
by having a matching stat (see §Character stats). Failure
never bricks a run · retry after a beat, or route around.

### 2 · Social encounters

Convince a counselor, calm a homesick camper, defuse a
fight, get information from a townie at the bus stop.
Turn-based dialogue tree. Party members contribute lines.

### 3 · Puzzle rooms

Real dungeon-crawl puzzles in the caves, boathouse,
counselor-cabin-at-night, and the ghost ship. Ultima-7-
depth: pressure plates, moved rocks, tide-timing, lantern
oil, code-locked doors that read Wilson's Portuguese.

### 4 · Chase sequences

Run from something. A raccoon in the mess hall. Bear
Roland after curfew. The tide coming in on the caves.
Speed-based · Xavier's distraction can end a chase
prematurely.

### 5 · Nature encounters

The heron at Alder Pond. The raccoon family in the east
forest. The seals off the ghost ship. Each has a memory
of what you did the last time (Ultima 7 memory · rare but
felt). Give the raccoon a snack once and it will follow
Sam thereafter.

## Character stats · six of them

Every camper (Sam included) has six stats, 1-5:

- **BODY** · climbing, swimming, holding breath
- **HEART** · social checks, calming, gift-giving
- **MIND** · reading, decoding, planning
- **LUCK** · rolls at Wilson's Ghost Pirate Play · finding hidden things
- **SNEAK** · being where you shouldn't be
- **KNACK** · the character's specialty skill

Party checks sum the party's best in that stat (not
average · one competent person can carry a whole party
for a specific check).

Sam starts with a balanced 2/2/2/2/2/2 and increases one
stat per day by picking a morning activity aligned with it:
- Swimming → BODY
- Nature journal → MIND
- Cabin chat → HEART
- Scavenger hunt → LUCK
- Free time → SNEAK
- Camp play rehearsal → KNACK

So the player shapes Sam over six days. Not a class system
· a personality-formation system.

## Inventory / survival

### The duffel bag

Sam's inventory is a duffel bag (16 slots). Items in the
world can be picked up. Items can be:

- **Used** (flashlight, canteen, insect repellent, sunscreen)
- **Combined** (rope + hook = grappling hook · lantern +
  oil = lit lantern · notebook + pencil = journal entry
  possible)
- **Cooked** on the campfire (raw fish + campfire = grilled
  fish · marshmallow + campfire + graham cracker + chocolate
  = a s'more, which raises the eating-camper's HEART by 1
  for the day)
- **Gifted** to a camper (their preferred-item list has
  ~4 items each · plus wildcards like the Portuguese
  postcard that raise anyone's meter by 1)
- **Read** (the buried treasure map, Wilson's Ghost Pirate
  script, the pages of Sam's own journal, Estuary 1's
  manual page from the bottled letter)

### Survival meters

Two meters, both soft:

- **Fatigue** · rises with skill checks and long walks.
  Sleep in a bed to reset. If fatigue hits max (10), Sam
  falls asleep wherever they are · time skips to morning.
- **Hunger** · rises with time. Reset by eating at the
  mess hall (free, 3× a day) or eating a snack from the
  duffel. If hunger hits max, all stats drop by 1 until
  Sam eats.

Neither meter can kill Sam. Both change the tempo · the
Goonies pacing where the kids get hungry halfway through
the caves and share a Twinkie.

### The Slowstock in Sam's duffel

Sam has an **Oneironautics Slowstick Rev 2** in the duffel
bag. Sam brought it from home. It can be booted at any
bench in the camp, and it plays a **mini-slowstick called
*NORTHWIND HARBOR*** · a small 15-minute game-within-a-
game that hints at Estuary 1's world. Only the first
chapter of Northwind Harbor is on the cartridge; the rest
is "damaged" and shows a static screen. Northwind Harbor
does not appear anywhere else in the game library. Its
existence is a lore hint.

## Locations · the overworld map

Camp Sweetgum spans roughly the same area as Estuary 3's
town walkabout. Twelve zones, all walkable:

1. **Cabin Sturgeon** (Sam's cabin) · six bunks · duffel
   inspection · sleep to advance day.
2. **Cabin Beaver / Osprey / Kestrel** · the other three
   cabins · scene-of-events for cabin-mate arcs.
3. **The mess hall** · three meals a day · bulletin board
   with lore fliers · the raccoon family lives under the
   porch.
4. **The activity board** (outside the mess hall) · daily
   activity sign-ups · a place to loiter and overhear.
5. **Alder Pond** · dock, canoes, the heron scene, the
   underwater passage (needs Ollie).
6. **The archery range** · Bear's domain · a set of five
   ranges · a ridge behind the fifth range that's climbable
   (needs Bea).
7. **Sweetgum Creek** · shortcut between mess hall and
   caves · a wading section, a small waterfall.
8. **The boathouse** · locked · needs Reggie's key or Nika.
   Inside: canoes, life jackets, a locked chest that
   requires further reveal.
9. **The Old Man** · downed spruce at the north bluff ·
   the treasure map is under it · walkable-to from
   Wednesday's hike onward.
10. **The caves** · the big dungeon · three levels ·
    tide-timed passages · the real pirate treasure is
    here.
11. **The east forest** · off-limits to campers · a
    hunter's cabin (reappears in Estuary 4) · a
    Portuguese sailor's grave from 1873 · needs SNEAK 3
    to enter without a chase.
12. **The bus stop / camp road** · exit to Depoe Bay ·
    the "leave camp early" branch resolves here.

Each zone has its own pixelart tileset. The world is
walked with 4-way movement (like Chrono Trigger); the
camera follows Sam. Zones connect via edge-of-screen
transitions.

## Dungeons · four of them

### 1 · The Old Man (small · ~30 min)

Not a dungeon per se · a puzzle spot. Under the log:
the treasure map, buried in a coffee tin. Needs Bea
Hallowell OR a shovel from the mess hall shed OR three
party members to lever the log.

### 2 · The Boathouse (small · ~45 min)

Locked chest at the back. Inside the chest: Wilson's
1988 logbook. Reading it reveals two of the six Wilson
clues plus a coordinate list of caves passages. The
door requires Reggie's key OR Nika.

### 3 · The Caves (large · ~3-4 hours · the main dungeon)

Three levels. Tide-timed · Ford Mears reads the tide
chart so you know when passages are safe. Puzzles
include:

- **Level 1** · The Chamber of Barrels · Portuguese
  ship-name graffiti · a barrel that opens if you know
  the shanty's second verse (Wu Kai reads it)
- **Level 2** · The Underwater Passage · Ollie must be
  in the party OR the party must find the second
  entrance via the east forest
- **Level 3** · The Treasure Room · not gold. A leather
  satchel containing: (a) a captain's silver whistle
  from a 1873 wreck; (b) a signed letter from the last
  captain who mattered; (c) a folded chart showing that
  there is *another treasure*, at a coordinate that
  reads 44° 45' N, 124° 03' W · which is Camp Sweetgum
  itself · the treasure was already at the camp

Boss: the caves themselves. If the party spends too long,
the tide comes in. Chase back to level 1.

### 4 · The Ghost Ship (medium · ~1.5 hours · Thursday–Friday only)

Visible offshore on Thursday night. Reachable by canoe
if Ford is in the party (he reads the approach window).
On board: a real 1780s brig, ghost-inhabited but not
hostile. Wilson's ancestor was one of the crew.

Puzzles here are talky · convincing the ghost captain
(who is Wilson's great-great-great-grandfather) to
grant Wilson absolution. Requires Sam to be carrying
the leather satchel from the caves.

Solving the ghost ship is the prerequisite for the
Wilson ending.

## Cast · fourteen campers · six-line vignettes

Written by Marc Ostrom unless noted (I.R. = Ines Rocha).

| # | Name              | Age | Stat spike | KNACK |
|---|-------------------|-----|------------|-------|
| 1 | Tessa Ansen       | 11  | MIND       | PLAN AHEAD |
| 2 | Wu Kai (I.R.)     | 10  | MIND       | READ THE SIGN |
| 3 | Marisol Cortez    | 12  | HEART      | LEAD THE PARTY |
| 4 | Danny Broz        |  9  | HEART      | CRY ON CUE |
| 5 | Reggie Vandermeer | 11  | LUCK       | DAD'S BOAT KEYS |
| 6 | Sylvie Nakagawa   | 10  | HEART      | SING TO THE HERON |
| 7 | Ollie Fisk        | 12  | BODY       | HOLD YOUR BREATH |
| 8 | Bea Hallowell     | 11  | BODY       | ROCKS FOR CLIMBING |
| 9 | Amelie Rocha (I.R.)| 10 | MIND       | GRAY IS HONEST |
|10 | Xavier Lund       | 12  | LUCK       | THE JOKE |
|11 | Priya Sundar (I.R.)| 11 | MIND       | ALLERGY WARNING |
|12 | Elias Wren (I.R.) |  9  | LUCK       | BIRD IS THE WORD |
|13 | Nika Voss         | 12  | SNEAK      | SNEAK LIKE A CAT |
|14 | Ford Mears        | 10  | MIND       | MARINE LOGIC |

Each has: a preferred-items list (~4), a per-camper story
beat (one moment where a specific dialogue choice grants
+1 friendship), a party dialogue register (they will
comment on locations, other party members, Wilson's
suspicious behavior).

## The Wilson Ashe mystery · six clues, plus the reveal dungeon

### Six optional clues

Same six as the earlier design — noticing four raises
Wilson's meter enough that he can be recruited to the
party on Friday. The clues:

1. Monday · anchor decal on his water bottle
2. Tuesday · Homesick-Night 20-minute absence, wet jacket
3. Wednesday · Ghost Pirate script coordinates = the camp
4. Thursday · buried map signed 'W.A. — 1987'
5. Friday · Portuguese shanty · Amelie's grandmother's word
6. Friday free-time · under the Old Man, ask him directly

### The reveal · the ghost ship dungeon

Solving clues 1-6 unlocks Wilson as a party candidate on
Friday afternoon. If Sam brings Wilson AND the leather
satchel from the caves out to the ghost ship at low tide
Friday night, Wilson confronts his ancestor and asks for
his own name back. The ancestor grants it. Wilson stays
at Camp Sweetgum.

If Sam does NOT bring Wilson (or does not have the
satchel), Wilson resigns Saturday morning and takes the
bus to Depoe Bay.

## Endings · six per-camper + shared + the ghost-ship reveal

Determined by Sam's highest-friendship camper AND whether
Sam completed the caves + ghost ship. Composited on
Saturday morning at 6:14 AM (matching Estuary 3's
morning-of-departure timing).

| Camper       | Ending title             | Blurb-in-brief |
|--------------|--------------------------|----------------|
| Tessa Ansen  | The Plotter              | Sam grows into a person with plans |
| Wu Kai       | The Reader               | Sam becomes a librarian |
| Nika Voss    | The Wanderer             | Sam becomes a person who walks at night |
| Elias Wren   | The Birder               | Sam becomes an ornithologist |
| Danny Broz   | The Homesick Kid         | Sam becomes a teacher who watches for it |
| Wilson Ashe  | The Pirate               | Wilson gives Sam the satchel |
| (shared)     | Good friends             | Sam remembers the summer for a long time |
| (early exit) | Left camp early          | Sam takes the Friday bus · what was lost |

Each ending has: an `epilogue_base` (five paragraphs, Sam
in the future) + `line_shape_riders` keyed to Sam's final
personality shape (a MIND-heavy Sam vs a HEART-heavy Sam
lands differently in every ending).

## Cross-Oneironautics lore · the scavenger hunt

Hidden throughout the camp, sized so a full-library player
catches ~half on a first playthrough:

- **The bottle on the beach** · south of the Alder Pond
  dock. Inside: page 17 of Estuary 1's manual. Only Elias
  spots the bottle. The manual page describes the sedge
  wren (which recurs in Estuary 3).
- **The bulletin board flier** · in the mess hall. Reads
  "Corvallis · Mrs. Wu's Garden · Fall Open House · June
  15, 1995." Mrs. Wu's Garden is another slowstick.
- **The 1600 AM radio** · in the counselors' cabin. Same
  static-voice station as Estuary 3's night 5. On
  Thursday night at 3:14 AM it says a specific word:
  *volta.* Sam-players-of-Estuary-3 hear this word again
  later.
- **The hunter's cabin in the east forest** · reappears
  in Estuary 4. The hunter is not there in 1994 · a note
  on the door reads "back in the spring" and is signed
  with a date of 2016.
- **Nika's postcard** · pinned to Cabin Kestrel's wall ·
  from her older sister, who works "at a studio in
  Portland." The studio is Oneironautics Inc. Nika's
  sister designed the box art for Mrs. Wu's Garden.
- **Wilson's Portuguese shanty** · the same melody the
  Estuary 3 player hears on 1600 AM in the final act.
  Written by Ines Rocha specifically to bridge the two
  games. In Pirate Summer (1994) it's the original.
- **The Northwind Harbor mini-cart** · Sam's duffel bag.
  Chapter 1 playable · rest damaged. Northwind Harbor
  exists as a lore reference only · never shipped as its
  own slowstock in the library.
- **Ford Mears's uncle's shipwreck book** · in the mess
  hall bookshelf. Includes a passage referencing "the
  Tideline" (a slowstick further up the unlock graph).
- **The Camp Sweetgum yearbook** · in Jenny's cabin.
  Signed in 1980 by a camper named "Jules." Jules · the
  same Jules who runs the Kwik Stop in Estuary 3.

## Sprite / visual language

Six visual tiers, one per system.

### Overworld · 16×16 pixelart tiles

Camp Sweetgum tileset · grass, sand, boardwalk, cabin
wall, pine-tree tops, boulder, dock, tide-pool. All
authored as `SlowstockSprite` palette-indexed sprites at
16×16, upscaled 3× for on-screen 48×48.

### Character sprites · 16×24 with 4-frame walk cycles

Fourteen campers + three counselors + Sam = 18 character
sprites. Each has: idle-down, idle-up, idle-left, walk
cycles for each direction (4 frames each). ~120 total
frames of authored pixelart.

### Character portraits · 48×64 for dialogue

Higher-res portrait when a character speaks. Emotional
variants: neutral / smiling / worried / determined / tired
· ~5 portraits × 18 characters = 90 portraits total.

### Location hero images · HeroImage

For special-attention scenes (the ghost ship reveal, the
treasure room, the closing bonfire), a full-screen
HeroImage backdrop overrides the tile view. Similar to
Estuary 3's town walkabout hero images.

### The Night View overlay

Same as before · warm dim palette for mystery reveals.
Kelvin ~2800K lantern lighting. Only the object in Sam's
hand is fully lit. Everything else silhouette. This
overlay reads over the pixelart layer without replacing
it · a color-shift plus a vignette.

### Journal / cross-stick lore items

Sam's nightly journal, the buried treasure map, Wilson's
logbook, the Estuary 1 manual page all render as
`HeroImage`-scale documents with an authored 5×7 pixel
handwritten font. Distinct from in-world dialogue text.

## Music / audio

Following the audio playbook · compositions authored via
`slowstick_synth`. Estuary 3's engine ships as-is · same
saw+saw+sub-triangle voice palette. Approximate track
list (deferred to a future audio wave):

- Camp Sweetgum theme (overworld daytime)
- Cabin lantern-light (indoors evening)
- Alder Pond (morning water)
- The archery range
- Sweetgum Creek (walking)
- The Old Man (bluff atmosphere · sparse)
- The Caves (three variations, one per level)
- The Ghost Ship (Portuguese shanty · Wilson's melody)
- Homesick Night (a slow HEART-focus piece)
- The closing bonfire
- Six ending pieces (one per per-camper ending, matched to
  the emotional register of each ending)
- The Wilson-resigns bus ride (Counselor Mode)

## Counselor Mode

By analogy with Estuary 3's Manager Mode. After finishing
Pirate Summer once, the shelf card exposes a **COUNSELOR
MODE** toggle. Selecting it starts a new run in which
Sam is Jenny Copeland.

### What Counselor Mode changes

- The daily loop is head-counselor tasks (rosters, cabin
  checks, medical logbook, evening event coordination),
  not camper activities.
- Sam-the-camper is one of the fourteen NPCs Jenny watches.
  So are the others. Jenny sees what each camper does but
  cannot go on the caves adventure herself (there's a
  gentle constraint: Jenny cannot leave camp perimeter).
- Wilson Ashe is a colleague, not a mystery. Jenny knows.
  Wilson knows Jenny knows. They do not speak of it
  during camp week — unless the player-as-Jenny asks the
  right question at the right time.
- **Additional ending: 'Wilson leaves on Friday.'** If
  Jenny lets Sam-the-camper find the map (which the
  base-mode player would want!), Wilson resigns Friday
  morning and does not return. Jenny drives him to the
  bus. He nods. He gets on the bus.
- **Second additional ending: 'The conversation.'** If
  Jenny asks Wilson on Thursday night about the 1988
  logbook, Wilson opens up. This ending is Jenny's own ·
  Wilson stays another summer, they become friends, and
  the epilogue is about Jenny's next four summers running
  the camp with Wilson as her right hand.

Counselor Mode adds ~4-6 hours over the base 12-14.

### Counselor-Mode-only scrapbook tokens

Additional discoveries a Jenny playthrough can surface:
`jenny_kept_the_medical_log_perfect` ·
`jenny_noticed_ollie_couldnt_swim_before_thursday` ·
`jenny_and_wilson_had_the_conversation` ·
`jenny_saw_the_ghost_ship_from_the_dock`.

## File layout · deferred until acts are authored

```
godot/
  scenes/games/pirate_summer/
    PirateSummerHost.gd            · run controller
    CampOverworld.gd               · 4-way movement + zone transitions
    CampZone.gd                    · per-zone tilemap + interactables
    PartyManager.gd                · roster, meters, active party
    Encounter.gd                   · skill checks · social · puzzle · chase
    Inventory.gd                   · duffel bag · combine · cook
    NPCDialogue.gd                 · portrait + dialogue tree
    NightViewOverlay.gd            · mystery reveal filter
    CavesDungeon.gd                · three-level tide-timed dungeon
    GhostShipDungeon.gd            · Thursday-Friday-only
    NorthwindHarborMini.gd         · game-within-a-game
    PirateSummerEnding.gd          · eight-ending epilogue screen
  resources/games/vol7/pirate_summer/
    manifest.json                  · exists (stub)
    campers.json                   · fourteen defs with skills + preferred items
    counselors.json                · three defs
    zones/                         · twelve zone JSONs
    days/                          · seven day JSONs (Sun-Sat)
    activities.json                · twelve activities
    skits.json                     · six evening events
    wilson_clues.json              · six clue reveals + reveal dungeon
    dungeons/
      old_man.json                 · small puzzle
      boathouse.json               · small dungeon
      caves.json                   · three-level main dungeon
      ghost_ship.json              · Wilson reveal dungeon
    endings.json                   · eight endings
    scrapbook.json                 · discovery catalog
    lore_hints.json                · cross-Oneironautics hint catalog
    northwind_harbor.json          · the mini-slowstick
    sprites/
      tiles/*.json                 · 16×16 overworld tiles
      chars/*.json                 · 16×24 character sprites × 18
      portraits/*.json             · 48×64 dialogue portraits × ~90
      scenes/*.json                · HeroImage backgrounds for reveal moments
      docs/*.json                  · journal · map · logbook · manual page
```

## Development order · fifteen waves

Pirate Summer is a **large second stick** · roughly the
same authoring weight as Estuary 3. Realistic wave plan
for when we come back to build it:

1. **Wave A · scaffold** (this commit) · design doc,
   expanded manifest, empty resource folders.
2. **Wave B · zone tileset + overworld movement** · one
   walkable zone (Cabin Sturgeon → mess hall), Sam sprite
   4-frame walk cycle, edge transitions.
3. **Wave C · fourteen camper data + party manager** ·
   campers.json full · friendship meters · roster UI at
   the mess hall.
4. **Wave D · daily loop scaffold** · six days advance on
   sleep · anchor events fire at scripted times · no
   activities interactive yet, just narration.
5. **Wave E · one activity fully playable** · pick one
   (probably swimming) · encounter mechanic + BODY stat
   grant.
6. **Wave F · remaining eleven activities** · each with
   its friendship-increment and stat-grant.
7. **Wave G · overworld filled in** · remaining eleven
   zones authored with tilesets.
8. **Wave H · inventory + survival meters** · duffel bag ·
   combine · cook · fatigue · hunger.
9. **Wave I · six evening skits** · plus the Ghost Pirate
   script as a reveal moment.
10. **Wave J · the Old Man + Boathouse mini-dungeons** ·
    puzzle sceneswith clear win conditions.
11. **Wave K · the Caves · main dungeon** · three levels ·
    tide timing · treasure room.
12. **Wave L · the Ghost Ship** · Wilson reveal dungeon.
13. **Wave M · six per-camper endings + shared + early exit**.
14. **Wave N · scrapbook + cross-Oneironautics lore
    scavenger hunt items** · bulletin board flier · bottle
    on beach · Northwind Harbor mini-cart · yearbook signed
    by Jules.
15. **Wave O · Counselor Mode** · Jenny run · two
    additional endings · Counselor-Mode scrapbook.

Each wave ships independently testable · the shelf's PEEK
button reaches whatever's been built so far.

## Lore tokens awarded on completion

Base completion writes three tokens:

- `pirate_summer_finished`
- `camp_sweetgum_visited`
- `wilson_ashe_recognized` (only when Wilson ending
  reached; other endings get the other two)

Per-camper endings each carry their own token:
`sam_and_tessa_stayed_friends`,
`sam_and_wu_kai_stayed_friends`,
`sam_and_nika_stayed_friends`,
`sam_and_elias_stayed_friends`,
`sam_and_danny_stayed_friends`,
`sam_and_wilson_have_the_map`.

Cross-Oneironautics discoveries each carry their own
token · `sam_read_the_estuary_1_manual_page`,
`sam_recognized_the_1600_am_word`,
`sam_played_northwind_harbor_chapter_one`,
`sam_found_the_hunters_cabin_note_signed_2016`,
`sam_read_the_yearbook_signed_by_jules`.

Counselor Mode's Wilson-leaves ending writes
`wilson_ashe_resigned_on_friday`. Counselor Mode's
conversation ending writes `jenny_and_wilson_had_the_
conversation`.

## Cross-references · what plays back where

- Sam from Estuary 3 is the same Sam. Chapter 21 of Vol
  7 references Sam being at Camp Sweetgum in July 1994 ·
  playing Pirate Summer after Estuary 3 retroactively
  colors that reference.
- Head counselor Jenny Copeland reappears in **Mrs. Wu's
  Garden** as an adult, unnamed at first · playing both
  sticks lands the reappearance.
- The Portuguese word *volta* is also the 1600 AM word
  from Estuary 3 night 5 · the Amelie Rocha translation
  scene in Pirate Summer explains it in retrospect.
- The hunter's cabin note signed 2016 is a plant · that
  hunter reappears in **Estuary 4**.
- Jules · signs the 1980 Camp Sweetgum yearbook · runs
  the Kwik Stop in Estuary 3.
- Wilson Ashe's Portuguese shanty melody · played on 1600
  AM in Estuary 3, sung by Wilson in Pirate Summer.
- **Northwind Harbor** · the mini-cart in Sam's duffel ·
  a slowstick that never shipped standalone · exists only
  in Pirate Summer's inventory · a lore ghost.

## Design notes · in-fiction dev commentary

Marc Ostrom, in the 2019 podcast, said: "Pirate Summer is
the game where I figured out you can build a whole feeling
by giving one character a bag they don't put down. Wilson
Ashe's whole arc is inside the bag. The player never has
to open it. If the player opens it — well, the player
opens it by asking one question on Friday, or by playing
Counselor Mode. And Wilson answers."

Ines Rocha, same podcast, said: "The four campers I wrote —
Amelie, Wu Kai, Priya, Elias — I wrote as if I was writing
a poem about summer camp. I did not know that was
different from what Marc was doing. Marc was writing an
adventure. So the game has both, and the campers who
overlap are the ones the player remembers most, because
they hear both registers in the same room."

She added: "The Portuguese shanty is my grandmother's.
She sang it in Coimbra in the 1950s. I did not know, in
2002, that I was writing my grandmother into a game.
I know now."

## What has shipped · Waves B through N

Snapshot at the close of the current build:

| Wave       | Delivered                                          |
|------------|----------------------------------------------------|
| B          | Overworld scaffold · 4-way movement · 2 zones · Sam sprite |
| C          | 14 campers data + 5 Sturgeon bunkmates as NPCs + dialogue box |
| C-tail     | Party manager · TAB roster · friendship meters     |
| D          | Six-day loop · sleep · anchor-event intro modals   |
| E          | Dialogue web · facts + character reactions         |
| F          | Party chatter · self-stories + gossip + moods      |
| G          | Camp schedule · mess hall + Alder Pond             |
| G-tail     | Schedule-driven NPC placement · party members hide from world |
| G-tail-2   | Counselors (Jenny · Bear · Wilson) as visible NPCs |
| G-tail-3   | Archery range zone                                 |
| G-tail-4   | Free-time scatter · campers wander to varied zones |
| G-tail-5   | Beaver cabin · Tessa · Marisol · Danny · Reggie    |
| G-tail-6   | Osprey + Kestrel cabins · Sylvie · Ollie · Nika · Priya · Amelie |
| H          | Duffel · pickups · gifting mechanic                |
| H-tail     | Journal panel (key J)                              |
| I          | Campfire ring zone · evening events · Wilson clues 2 + 3 |
| I+J-tail   | Wilson clues 5 + 6 · closing bonfire + Old Man reveal |
| J-partial  | North bluff · Old Man log · treasure map (clue 4)  |
| N-partial  | Bulletin board · cross-Oneironautics fliers        |
| M          | Saturday endings screen · 8 endings                |
| N          | Scrapbook · 25-entry catalog                       |
| F+         | Chatter growth · 101 total lines across 14 speakers|

Content totals at snapshot:
- **9 walkable zones** (cabin_sturgeon, cabin_beaver, cabin_osprey,
  cabin_kestrel, camp_path, mess_hall, alder_pond, north_bluff,
  archery_range, campfire_ring)
- **17 speaking NPCs** (14 campers + 3 counselors) with
  schedules that place them by (day, time block)
- **34 facts, 118 authored reactions** across all 17 speakers
- **101 party chatter lines** with mood tinting and gossip
  auto-gating
- **8 endings** with authored five-paragraph epilogues
- **25 scrapbook entries** in five tiers, picked up by the
  existing SlowstockScrapbook UI automatically

Still deferred (Wave O and beyond):
- Counselor Mode (Jenny playthrough · adds 2 endings)
- Ghost Ship dungeon (Wave L)
- Caves main dungeon (Wave K)
- Story-beat +1 friendship moments (data authored in
  campers.json, not yet wired to specific day/place triggers)
- BGM per zone (audio playbook applies)
- Portraits (48×64 emotional variants per character)
- Walk-cycle frames for character sprites (currently down-facing
  idle only, all NPCs are palette variants of Sam's silhouette)

## Recent lessons

### 2026-07-08 · the dialogue web IS the game

The dialogue-as-discovery-graph (Wave E) turned out to be
the mechanical core Pirate Summer needed. Every other system
plugs into it: chatter references discovered facts, world
objects grant facts, character reactions unlock further
facts, the ending reads the fact set to pick which epilogue
plays. Authoring reactions per (character × fact) means each
discovery lands differently in every conversation it touches.

The lesson: **the game's tone is set by what a character
chooses to say about a piece of information**, not by the
information itself. Xavier's take on Wilson's anchor decal
("so Wilson IS a pirate. I called it. Sam · I called it.")
and Jenny's take on the same fact ("you noticed the anchor?
Yeah. Wilson used to work at sea. He told me his first day.
He didn't say more than that. I didn't ask.") are the same
fact filtered through two different registers. The game
lives in the difference.

### 2026-07-08 · palette-variant sprites work at 16×24

All 17 character sprites ship as palette variations of Sam's
16×24 pose data. This is a shortcut, and the shortcut works:
color separation is enough at that resolution for a player to
tell Bea from Wu Kai at a glance (red hair vs black hair,
brown vs green shirt). Walk cycles + unique silhouettes are
Wave B-tail and beyond; not shipping them yet doesn't hurt
the readability of the room.

The lesson: **at 16×24 with hard palette contrast, silhouette
variety is not blocking**. It becomes blocking when characters
need distinct actions (Bear casting a fishing line, Wilson
carrying his bag, Sylvie mid-song) · then a unique pose data
per character is warranted.

### 2026-07-08 · schedule-driven NPC placement makes the world

The `sched.mess_hall_seat` / `sched.activity_positions` /
`sched.free_time_zone` triple lets the whole camp respond to
the clock without any per-NPC scripting. When Sam sleeps on
Monday, everyone teleports to their Tuesday-morning positions.
The world visibly rearranges. This was ~40 lines of resolver
code and one JSON block per character.

The lesson: **place-by-schedule is cheaper than script-by-
event**. A future project should default to schedule tables
and only reach for scripts when a character needs a
non-schedulable behavior (Wilson disappearing to the
saltmarsh for exactly 20 minutes on Tuesday · that one's
scripted, and rightly so).

### 2026-07-08 · playable front-to-end · every camper matters at every dungeon

The party-KNACK-gate design landed with real teeth once the
dungeons all shipped.  A player who runs solo through Pirate
Summer can complete the main path (six clues, Wilson ending)
· but a player who forms a party of Bea + Ollie + Ford can
reach content solo-Sam can't:

  · Bea's ROCKS FOR CLIMBING opens the Old Man dig
  · Ollie's HOLD YOUR BREATH swims the caves-level-2 passage
    (Ford's MARINE LOGIC does it too, differently)
  · Ford's MARINE LOGIC tide-times the ghost ship approach
  · Nika's SNEAK LIKE A CAT opens the boathouse door (or
    east forest gate) · Reggie's DAD'S BOAT KEYS does the
    boathouse the other way
  · Wu Kai's READ THE SIGN opens the caves-level-1 barrel
  · Priya's ALLERGY WARNING opens the boathouse chest
    (or Nika's SNEAK does)
  · Amelie's context translates Wilson's shanty (Wave clue 5)

Every one of the seven ending-eligible campers plus five of
the non-ending-eligible campers has a moment the player would
plausibly bring them along for.  The game rewards party
composition without punishing solo play · both paths reach the
Wilson ending.

Lesson: **KNACK design is architectural, not decorative**.
Author each character's KNACK to open a specific piece of
content (a dungeon door, a passage, a chest, a translation).
When a player picks a party, they are picking which pieces of
the world they will get to see this run.  Different party →
different game.  This is what makes replay feel different, not
same.

### 2026-07-08 · gossip auto-gates on party composition

The party chatter system's `subject` field auto-gates gossip:
a line about Reggie won't fire when Reggie is in Sam's party.
This felt fussy to implement (~15 lines of filter logic) but
paid for itself the first playthrough · running with just Bea
in the party surfaces different chatter than running with
Reggie, because the Reggie-related gossip Bea would have
delivered stays locked. Party composition changes what you
hear about who you *don't* have with you.

The lesson: **auto-gating gossip on party membership is a
tiny system that generates a lot of felt variance**. Combine
it with kind:self_story and kind:surroundings (which don't
gate on party) and every party composition produces a
different soundtrack of chatter over the same walk.

