# Vol 6 · Network Game Spec · "The Summer Before Milk and Honey"

A grand-strategy gallery game for vol 6, set across a single summer
of an older Frasier Temple's life. Frasier sits over a board of
three regions and routes a network of demons and human agents to
suppress multiplying problems while planting a fragile foothold in
Small Wood, Oregon — the front that keeps getting swatted down.

The game fills the story *Planned Community* doesn't cover. Its
output is the starting state of *Land of Milk and Honey*. Soft-fail
throughout — there is no game-over screen, only worse openings for
the next book.

## Core loop

A turn is a day. ~100 turns = Memorial Day (late May) to Labor Day
(early September), the canonical American summer. Each day has two
layers, run in sequence:

**Day layer · the map**
- Frasier surveys the board, reads incoming reports, and dispatches
  0-3 agents to handle ongoing or new problems.
- Agents travel and execute over a span of days (faster within their
  home region, slower across regions). They return tired, hurt,
  changed, or not at all.
- Problems compound if untreated past a per-region escalation clock.

**Night layer · the BBS**
- Weekly cadence. Six "quiet" days where Frasier just runs the
  board, then one BBS night where everything decompresses.
- Frasier dials in from the office. Reads threads. Answers DMs from
  the canon roster. Makes one or two choices that propagate back up
  into next week's map (an ally goes silent, a demon gets a tip-off,
  a new BBS board reveals itself).
- The BBS night is also the **unlock layer** — neat things to find:
  hidden boards, archive files, character POV documents, demon
  dossiers, easter-egg dial-up numbers.

The whole game is paced for chill. No timer. Long turns are fine.
The BBS is meant to be a place to sit, not a puzzle to solve.

## The map · control nodes and resource flow

The map isn't free-form territory. Each region is a small constellation
of **control nodes** — discrete locations Frasier has to maintain to
keep the network functional in that region. A node held generates
resources for the network (insight, cover, courier capacity, demon
rest, safe-house space). A node lost dries up its output and becomes
a *problem in itself* — a hostile node generates threats outward into
neighbors until reclaimed.

Nodes are not territory in the wargame sense. They are *people's
homes, businesses, and infrastructure that already exist in the canon*.
The boat is a node. The diner is a node. The Roberts house is a node.
Elicia's bungalow is a node. The Harmony Creek model home is a node.
A specific dirt road outside Small Wood is a node.

### The resource trade-off

The strategic spine: **pushing Small Wood costs resources from the
other two regions**. Frasier's network has finite output. To plant
in Small Wood — to even reach Small Wood, given the distance — he
has to *withdraw* a demon-month or a human-week from Graustark or
Harmony Creek. That withdrawal weakens the source node. Weakened
source nodes spawn problems faster. The game's central question
every week is: *how much can I afford to bleed the home soil to
keep trying in Small Wood?*

Push too hard and Graustark starts failing in the slow grief-and-
infrastructure way. Push too little and Small Wood swats every plant
before it sprouts and the seed count for *Milk and Honey* stays at
zero. The chill comes from the timescale, not the absence of choice.

### Graustark · home soil · established network

The TX/LA river country that vol 5 lived in. Nicola's house. The
boat. The diner. The bungalow. The cathedral. Frasier's network
here is *mature* — six to eight control nodes, most of them
self-maintaining as long as the canon roster is in place. Frasier
can run Graustark on autopilot for weeks if he has to. He pays for
that by having drawn down its slack to push elsewhere.

- **Control nodes (sample):** Dante's boat, the diner, Nicola's
  house, Elicia's bungalow, the cathedral, the riverfront. Most
  start the summer held and stable.
- **Native agents:** the canon roster aged forward — Nicola, Dante,
  John Frank, Elicia. They run their nodes by *being there*.
- **Problem palette:** memorial-grief, family-succession, the boat
  closing, the cathedral, the diner's lease, infrastructure failing.
- **Strategic role:** supply. Graustark generates the *insight* and
  *cover* and *courier capacity* Frasier spends elsewhere. Every
  unit pulled to Small Wood is a unit Graustark doesn't have when
  it needs it.

### Harmony Creek Estate · engineered community · medium resistance

The planned-community thread *Planned Community* lives in. A new
build on the edge of nothing, all surveillance-soft and HOA-hard.
Frasier has a thin foothold here — two or three plants — and the
community's leadership is hostile in the polite way.

- **Control nodes (sample):** the model home, the HOA office, a
  specific cul-de-sac that gets a lot of new mail, the community
  pool, a half-finished phase-three lot. Three to four nodes total,
  most contested at game start.
- **Native agents:** Mackenzie at the loom (relocated? visiting?
  the writer can decide). A demon or two embedded as residents (the
  *cicada*, the *starling* — long-watch types).
- **Problem palette:** surveillance, HOA actions, missing kids, a
  community meeting that goes wrong, a model home that has the
  wrong feel.
- **Strategic role:** containment. Harmony Creek is where the
  enemy's policy work happens. Failures here are *legible* — they
  show up in newsletters and ordinances.

### Small Wood, OR · the front · highest resistance

A small Oregon timber town where Frasier is trying to plant
something. Every plant gets swatted. The locals are not on his
side. The terrain is bad for demons (cold, watched, networked
weirdly). This is the *planting* region — where success is measured
in seeds banked for the next book, not in territory held.

- **Control nodes (sample):** one rented room above the timber-yard
  office, one dirt road, one diner that doesn't know it's a node yet,
  one tower site (see below). One or two start the summer held;
  most start as targets to *try for*, not nodes Frasier already has.
- **Native agents:** thin. One or two contacts Frasier has cultivated
  over years; both expensive to dispatch.
- **Problem palette:** local-press exposure, contact going dark, a
  seed dying before sprouting, demon corruption (see below), the
  ground itself refusing the plant.
- **Strategic role:** investment. Every successful plant in Small
  Wood becomes a seed that *Milk and Honey* harvests in its opening
  chapters. Every failed plant is a setback Frasier carries forward.
- **The asymmetry:** Small Wood's escalation clock is twice as fast
  as the other two regions, Frasier loses agents here at a much
  higher rate, and **demons sent to Small Wood risk corruption**
  (see below). The point is not to win Small Wood. The point is to
  *keep trying* in Small Wood while holding the rest.

## Agents

Two classes, each with its own economy.

### Demons · loud, fast, burnable

The Magician chapter's roster, repurposed as dispatchable units.
Each demon has a specialty, a signature problem-type it handles
well, and a signature way of failing:

- **Vagrant** — long-distance reconnaissance. Failure mode: gets
  arrested or "found" by a local press hook.
- **Cicada** — long-watch surveillance. Failure mode: surfaces too
  loudly, blows cover for adjacent operations.
- **Moth** — light demolitions, distraction. Failure mode: starts a
  fire that has consequences in the wrong region.
- **Steamboat** — heavy infrastructure. Failure mode: leaves a wake.
- **Weir** — water work, river-bound, regional to Graustark. Failure
  mode: takes a piece of the river with it when it goes.
- **Filly** — fast courier, message-carrying. Failure mode: gets
  intercepted; whatever was carried is now also in the enemy's
  hand.
- **Starling** — flock surveillance, embedded in places like Harmony
  Creek. Failure mode: scatters; future starling work in the region
  costs double.
- **Husk** — last-resort blunt instrument, very expensive. Failure
  mode: catastrophic; the husk does the job but leaves a body or
  equivalent.

Demons accrue **burn** with each use. At 5 burn, a demon goes dark
for 14 days. At 10, gone for the saga. Burn doesn't recover on its
own — Frasier has to *spend a BBS night on it* (a specific board
where demons rest).

**Corruption in Small Wood.** A demon dispatched to Small Wood
accrues *corruption* alongside burn, at a much faster rate. At a
threshold (5 corruption for most demons, lower for the lighter
classes like cicada and moth), the demon **turns** — it doesn't go
dark, it doesn't come home, it stays in Small Wood as an *enemy
agent on the resistance's side*. The turned demon appears on the
map as a problem source under its original name. Future operations
in Small Wood now also have to plan around a demon Frasier
*trained*.

Corruption is the single largest reason demons aren't the answer to
Small Wood. Every demon-week spent in Small Wood is a coin flip
toward making the region harder for next week. The player learns
this the hard way the first time it happens. After that, demons in
Small Wood become a deliberate trade-off — sometimes the only
option, always the dangerous one.

### Humans · slow, quiet, indebted

The canon roster, aged forward into vol 6's timeline. **Each one is
a person with a home and a life.** They are not units that live on
the map waiting to be moved. Sending Mackenzie to Harmony Creek
means she leaves her loom, leaves Philip, drives or flies, sleeps in
a strange bed, and comes back tired with the work at home backed up.
Sending Dante to Small Wood means the boat doesn't have its captain
for the four days he's gone, and the boat's other problems escalate
unsupervised.

The dispatch cost for a human agent is therefore at least three
overlapping things:

- **Obligation** — they did Frasier a favor; the favor is on the
  books. The third favor is harder than the second. The fifth, they
  stop answering.
- **Time at home** — the node they normally maintain runs without
  them while they're away. Long dispatches mean their home node
  takes on a small-problem of its own (Philip alone with the basil
  pot dying; the boat's Friday dinner crew without Dante on the
  iron stair).
- **Life cost** — some dispatches cost things the BBS layer
  surfaces afterward. Mackenzie sent to Harmony Creek too often
  starts posting about leaving Philip. Dante sent to Small Wood
  starts posting about closing the boat.

The DMs on the BBS are not strategic communications. They are
*people's lives* in response to the strategic communications. Read
them and you'll know who's about to stop picking up.

Humans never "go dark" the way demons do. They just stop picking
up. And the things they stopped picking up about are still in their
homes and lives, getting worse.

The three economies (demon burn / demon corruption / human
obligation-plus-life) are the strategic spine. A run that leans on
demons risks Small Wood eating them. A run that leans on humans
risks the canon roster falling apart in their own homes by Labor
Day. Most summers will be a mix, and the BBS will tell Frasier
which mix is breaking.

## Dean's network · the third faction

Frasier is not the only operator on this map.

Mr. D. Dean — the long-game watcher from vol 5, the lapels-smoothing
gentleman at Table 14, the man who leaves notes under hundred-dollar
bills — has his own network. By vol 6 his operation is larger than
Frasier's, older than Frasier's, and **the big silent unknown of the
strategic layer**. Dean is not Frasier's ally. He is not Frasier's
enemy. He is using his network for *his own reasons*, which Frasier
does not fully understand and the player learns only obliquely.

### What Dean controls

- **The substrate.** A reality-manipulation infrastructure layered
  underneath the map. The substrate is not a place; it is a *medium*
  Dean's network operates through. When the substrate is active in
  a region, the rules of that region soften — escalation clocks
  drift, problems mis-classify, agents arrive late or arrive
  somewhere they weren't dispatched to. Frasier sees the *effects*
  of the substrate as anomalies; he does not see the substrate
  itself.
- **The tower.** A single physical structure in Small Wood, near
  but not on Frasier's seed-planting nodes. The tower is Dean's
  primary focusing point for substrate manipulation. It is on
  Frasier's map but he cannot reach it; agents dispatched to the
  tower do not return. Some weeks the tower is *bright* (active);
  some weeks it is *dim*. The brightness state is the player's only
  legible reading of what Dean is doing.

### How Dean shows up in play

Dean has no boards on the BBS that Frasier can read. He has no DMs.
He is never a dispatchable agent on Frasier's side. He shows up
*only* as:

- **Anomalies on the map.** A Small Wood plant that should have
  been swatted is somehow still there. A Harmony Creek problem
  resolves itself overnight. A demon Frasier sent to corrupt-and-
  die in Small Wood comes home untouched and slightly *different*.
- **Fingerprints in other people's threads.** A canon human posts
  about meeting a "plain-faced man" at a diner. A BBS handle
  Frasier doesn't recognize appears in MAINSTREET once and never
  again. A photograph attached to a thread on THE_LIBRARY shows,
  in the background, lapels being smoothed.
- **Tower-brightness events.** When the tower is bright, the
  strategic layer's rules shift for one in-game week. The shifts
  are *not random*; they are Dean's interventions. Sometimes they
  help Frasier (a Small Wood plant lands cleanly). Sometimes they
  hurt (a Graustark node Frasier was certain was held shows up
  contested on Monday morning). The player learns to read
  brightness as a forecast.

### The Dean ledger

A second hidden ledger runs parallel to Frasier's. The player
cannot read it directly. They can infer its contents from
anomalies, fingerprints, and tower events. *Milk and Honey* opens
with both ledgers as inherited state — Frasier's seeds **and**
Dean's. The protagonist of the next book may discover, late, that
half of what they thought was their own work was Dean's all along.
Or none of it was. The game does not tell the player which.

### Why Dean is the right design choice

Three reasons the third faction earns its place:

1. **It models the universe Frasier actually lives in.** Frasier
   has never been the only one operating. Vol 5 already established
   that. The strategic layer would feel naive without it.
2. **It deepens every decision the player makes.** A Small Wood
   plant that lands clean might be Frasier's work or might be
   Dean's substrate. A demon that should have corrupted but didn't
   might be lucky or might be borrowed. The player can never be
   certain which, and that uncertainty is a *feature*.
3. **It is the engine for the next book.** *Milk and Honey* has to
   open with something the protagonist doesn't know. Dean's parallel
   ledger is that something.

Dean is a design constraint as much as a faction: the writer
authoring anomalies and fingerprints has to decide, scenario by
scenario, what Dean is *doing* — but never has to explain it to
the player. The silence is the point.

## Problems

Problems spawn weekly, on Sunday nights, before the BBS opens.
Each region generates 1-3 problems depending on how exposed it
currently is. Problems have:

- A **type** (from the region's palette).
- A **clock** — how long before it escalates. Small Wood problems
  default to 5 days; Harmony Creek to 10; Graustark to 14.
- A **resolution profile** — which agent classes suppress it
  cleanly, which suppress it noisily, and which make it worse.
- An **escalation child** — what the problem becomes if untreated.
  Some problems escalate into multiple children; a single ignored
  Small Wood thread by week 6 can be three threads by week 10.

Successful resolution returns the agent (with cost) and writes a
small ledger entry. Some resolutions in Small Wood specifically
**bank a seed** — a token *Milk and Honey* reads off Frasier's
ledger at the start of its run.

## The BBS layer

Weekly, on the seventh day of every game-week. The interface is
period-correct: 14.4k connect tone, ANSI color, board navigation by
single-letter commands, a list of boards on the left, a thread
view on the right.

### Boards

Six visible boards from the start, more discoverable through play:

- **MAINSTREET** · the public square. Frasier reads, sometimes
  posts. Choices here are *visible*; the enemy reads MAINSTREET too.
- **THE_BAR** · Graustark regulars. Dante posts. Sammy posts.
  Reading enough threads here unlocks character POV documents.
- **THE_LIBRARY** · archive board. Where Elicia posts. Files to
  download — audio recordings, photos, scans of vol 5 era documents.
- **THE_WORKSHOP** · Frasier's own board. Tech threads. Hidden
  technical unlocks for the player.
- **THE_RECTORY** · religious / municipal cross-talk. Paul's aide
  lurks here under a handle.
- **THE_BACKCHANNEL** · sysop-only. Other operators of Frasier's
  level. The board where strategic policy actually gets discussed.

Hidden boards, discovered through clues in posts:

- **THE_ATTIC** · old grief, the dead. A memorial board, mostly
  read-only. Reading here unlocks character POV documents about
  characters lost in vol 5 and earlier.
- **THE_GROVE** · a Small Wood board. Discoverable around week 5
  by following dial-up clues in MAINSTREET threads. The enemy
  reads here.
- **THE_RIVER_HOUSE** · a board run by someone Frasier knows but
  doesn't trust. Reading it costs cover but reveals the enemy's
  plans for next week.
- **THE_BASEMENT** · the demon roster's resting board. Spending a
  BBS night here reduces all active demon burn by 1.
- (others hidden — let the writer decide how many. 12-15 boards
  total feels right.)

### DMs

Each canon human agent has a private DM thread that updates weekly
based on what Frasier dispatched them to do. The DM thread is the
*character POV* layer — Mackenzie's grief-as-a-thread, Elicia's
archive frustrations, Dante's slow goodbye to the boat, John
Frank's column drafts, Nicola's letters to her sister.

DMs are mostly read. Occasionally Frasier replies; the reply is a
choice with a strategic consequence next turn. The replies are
short — single sentences, sometimes a single word. The point is
the *quiet*, not the verbosity.

### Unlocks

The collectible layer. Found by:
- Reading enough of a thread (POV documents).
- Downloading archive files from THE_LIBRARY (audio, scans,
  transcripts).
- Discovering hidden boards.
- Sending demons / humans to specific regions enough times (demon
  dossiers, agent backstories).
- Completing region milestones (a region's signature easter-egg
  unlock).
- Finding dial-up numbers tucked into BBS posts that connect to
  hidden boards.

Unlocks are tracked in a small "shelf" on Frasier's office that the
player can browse outside of the BBS night. They're the slow-burn
reward layer. None of them are required. All of them deepen the
saga.

## The seed economy

The output of the game. What *Milk and Honey* inherits.

- **Seeds planted** · per Small Wood success. Each seed is a named
  thing (a contact's name, a plot of land, a phrase posted on the
  right board). *Milk and Honey* opens with that many seeds
  available to its protagonist.
- **Agents intact** · which demons are still on Frasier's roster at
  Labor Day. Which humans are still picking up the phone.
- **Demons turned** · the negative inheritance. Demons that
  corrupted in Small Wood and stayed there. *Milk and Honey* opens
  with each turned demon listed as an active enemy agent — Frasier's
  former tools, working for the resistance, knowing his methods.
- **Cover remaining** · the network's deniability score. Low cover
  means *Milk and Honey* opens with Frasier already under watch.
- **BBS friendships** · per-canon-human relationship state at saga
  end. Frasier's call list going into vol 7. Includes whose home
  lives broke under the dispatch load.
- **Tower-state** · the tower's final brightness reading at Labor
  Day. *Milk and Honey* opens with the tower bright, dim, or dark
  depending on what Dean was doing in the last week of the summer.
- **Dean's ledger (hidden)** · the parallel ledger the player never
  sees. *Milk and Honey* may read off this to make the protagonist's
  opening world feel like it has been written without them.
- **Unlocks claimed** · the player's collection state. Carries to
  the saga shelf, not the in-game ledger.

The save file handed to the next book is short — maybe a dozen
fields — but the strategic decisions that wrote it are the whole
summer.

## Soft fail

There is no game-over screen.

- A summer where Small Wood collapses entirely → *Milk and Honey*
  opens with zero seeds, hostile terrain, and the protagonist
  having to start the work from scratch. Different game, not a
  failed game.
- A summer where Graustark crumbles → the canon roster opens vol 7
  reduced. Some characters Frasier knew are gone. The protagonist
  inherits a smaller home.
- A summer where Frasier himself burns out (his own sanity track
  hits zero) → he's still there in *Milk and Honey*, but quieter,
  smaller, no longer the operator. The protagonist has to coordinate
  without him.
- A summer where three or more demons turn in Small Wood → *Milk
  and Honey* opens with a *hostile former Magician roster* working
  against the protagonist. The villains know Frasier's signatures
  because they used to *be* Frasier's signatures.
- A summer where the tower stays bright at Labor Day → Dean has
  finished whatever he was doing. *Milk and Honey* opens with the
  substrate active across all three regions, the rules already
  bending before the protagonist takes their first action.

Every ending is a starting state. None is a loss. Some starting
states are harder than others; none are inaccessible.

## Tone · the chill unwind

The strategic layer is fast in *decisions* but slow in *time*. A
turn is a day; a day takes as long as the player wants. No timer,
no penalty for thinking. The map is beautiful — three hand-drawn
regions, period-correct cartography, the agents drifting between
locations as small line-segments.

The BBS night is the rest. Frasier in the office at dusk. The
modem's connect tone. The cursor blink. A cup of coffee on the
desk. Six boards to wander, threads to read, the slow accumulation
of who's still in the story and who isn't. No fail state on the
BBS. Just presence.

The player should be able to play this game for an hour and feel
like they spent a quiet evening. They should be able to play it
for ten hours across a summer's worth of sittings and feel like
they've been somewhere.

## Sequencing for build

A three-phase build, white-box first.

1. **The map and the day loop.** Three regions on a static
   background. Dispatch as a list of buttons. Problems as JSON.
   Agents as JSON. No art yet. The strategic layer playable as a
   spreadsheet game. Goal: prove the burn-vs-obligation economy.
2. **The BBS shell.** Six visible boards, period-correct UI, threads
   and DMs as authored JSON. No procedural generation. Goal: prove
   the weekly cadence and the unlock layer.
3. **The hookup.** BBS choices write strategic flags read by the
   next day's map. Strategic events write into BBS threads as posts
   from canon characters. Goal: prove the loop closes — what
   happens at night changes what happens tomorrow.

After those three, polish: hand-drawn map, period-correct BBS
ANSI/handles, voice work for DM voices, demon dossier illustrations,
the office shelf for collected unlocks.

## Out of scope

- Real-time play. The game is turn-based on demand.
- Multiplayer / online. The BBS is faked; no other players are real.
- Procedural problem / dialogue generation. Every problem and every
  BBS post is authored.
- Branching endings beyond the inherited save state. The endings
  are *Milk and Honey*'s problem.
- A combat layer. Agents resolve problems by being-dispatched-and-
  returning, not by playable combat.

## Success criteria

- A first playthrough takes 8-12 hours across the summer's hundred
  turns, paced however the player wants.
- The BBS night is the part the player looks forward to.
- The player finishes the summer with at least three Small Wood
  seeds banked and at least one canon-human friendship that
  *changed* during the game.
- The unlock shelf has at least eight items on it.
- The player feels like they spent a summer with an older Frasier
  Temple — not like they played a strategy game with a chat
  interface bolted on.

If those land, the gallery game has earned its place between
*Planned Community* and *Land of Milk and Honey*. And the next
book opens from a starting state the player can point at and say:
*I made that.*
