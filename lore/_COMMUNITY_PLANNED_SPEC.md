# COMMUNITY PLANNED · Game Spec

A grand-strategy gallery game inset into vol 6's summer. Its title
is the inversion of its host novel's title — **COMMUNITY PLANNED**
sits beside *Planned Community* the way a *cathedral warehouse*
sits beside a *warehouse cathedral*. The inversion is the saga's
signature move.

The game is set across the middle of the summer *Planned
Community* depicts. The book's part one — *Summer's Start* —
closes with the long pause. Then the gallery offers the
COMMUNITY PLANNED unlock. Then the book's part two — *End of
Summer Begins* — opens. The game IS that middle.

Frasier sits over a board of three regions and routes a network
of demons and human agents to suppress multiplying problems while
planting a fragile foothold in Small Wood, Oregon — the front that
keeps getting swatted down.

The game **adds flavor to the saga but does not author it.** The
novels — *Planned Community*, *Land of Milk and Honey*, and
whatever follows — are sovereign. They proceed exactly as written
regardless of what the player does in this game. What the gallery
game produces instead is **unlockable interludes**: extra narrative
flavor — character vignettes, BBS transcripts, dossier excerpts —
that the player earns by playing and can read alongside the canon.

## Unlock condition

COMMUNITY PLANNED becomes playable in the gallery only after the
reader finishes *Summer's Start* — the first part of *Planned
Community* — and the opening page of *End of Summer Begins* is
available to turn to. The game's appearance in the gallery
coincides with the book's structural seam.

The reader can play immediately, defer indefinitely, or skip the
game entirely. The book's part two remains available in all three
cases. A reader who plays the game enters part two carrying the
texture of the middle. A reader who skips it enters part two with
a held-breath ellipsis where the middle was.

Implementation surface (engine-side, post-MVP):
- Save flag `community_planned:reader_finished_summers_start`
- Gallery surfaces a phosphor-green CRT tile labeled COMMUNITY
  PLANNED with a 14.4k connect-tone preview on hover.
- Tile remains permanently available once the flag fires.
The interludes deepen the world for the player who put hours into
the network; they never rewrite the world for the reader.

Soft-fail throughout. There is no game-over screen, only different
interludes earned.

## The protagonist · Frasier Temple, middle-aged

Frasier in vol 6 is **not** the kid from the Magician chapter
anymore. He is middle-aged, getting old, creaky and cranky, and on
his worse days maybe a little insane. He is the operator who has
survived long enough to become the thing he used to dispatch
agents at. He still wears the boots. The boots are now broken in
the wrong places.

What sustains him is the network. His **loyal friends and foot
soldiers** — the canon roster who never stopped picking up, the
sysops on his level who still trade favors over the BBS, the
contacts in towns he hasn't visited in fifteen years who would
still drive to the airport for him. And his **demon creations**,
which by vol 6 are *evolving and getting more complex* — the
vagrant of 1996 is not the vagrant of vol 6; the cicada has spent
twenty years on Frasier's network and has, in that time, become
something the Magician-era Frasier would not recognize. Some of
them think for themselves now. A couple of them have opinions
Frasier disagrees with. This is the cost of having made them in
the first place.

He is funny in the way old operators are funny — bone-dry, no
patience for theatre, fond of the people he is fond of without
saying so. He is paranoid in the way old operators are paranoid —
not without reason. When the player meets him at the start of the
summer, Frasier is already tired. The summer ahead is going to be
worse.

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
before it sprouts and the interlude shelf stays thin. The chill
comes from the timescale, not the absence of choice.

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
in seeds banked for the interlude shelf, not in territory held.

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
  Wood unlocks an interlude in the player's shelf — a small piece
  of vol 6's shoulder-season that the novels don't have room for.
  Every failed plant is a sadder vignette on the shelf.
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

**Demon evolution.** Frasier's demons are not the demons of the
Magician chapter. Twenty years on the network have *changed* them.
Each demon carries a small, growing complexity rating that the
player can read on the agent's dossier. As a demon completes
operations — and especially as it weathers near-corruptions and
returns from Small Wood — its complexity rises. Higher complexity
demons:

- Develop **specialties beyond their class** (a cicada that has
  worked Harmony Creek for years gains *policy intuition*; a moth
  that has survived three Small Wood trips gains *cold-terrain
  resistance*).
- Develop **opinions**, surfaced as BBS posts from the demon under
  its handle, sometimes disagreeing with Frasier's dispatch
  decisions. Frasier can override; the demon will go, but
  obligation now runs both ways.
- Develop **vulnerabilities**. A complex demon is also a *legible*
  demon — the resistance has had more time to study it. Some
  high-complexity demons accrue corruption at half the normal rate
  but, if they do turn, turn into substantially more dangerous
  enemy agents.

Evolution is the long arc of the demon economy. By Labor Day,
Frasier's roster looks less like *eight tools* and more like
*eight collaborators with their own ideas about the work*. That
shift is one of the quiet rewards of a long summer.

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
anomalies, fingerprints, and tower events. At Labor Day a few
*trace fragments* from Dean's ledger surface as the Dean interludes
on the player's shelf — partial, unreliable, possibly contradictory
to what the player thought they saw. The interludes never *resolve*
Dean. The silence is the point.

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
3. **It earns the strangest interludes.** The Dean shelf is the
   weirdest, sparest section of the unlock browser. A player who
   leans into reading anomalies all summer earns a small, deeply
   strange set of fragments that no other path produces.

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
**bank a seed** — a token that, at Labor Day, unlocks the seed's
interlude in the player's shelf.

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

## The interlude economy

The output of the game is **flavor, not canon**. The novels are
sovereign. *Land of Milk and Honey* opens exactly the way the
writer wrote it. What the game produces is a set of **unlockable
interludes** — extra narrative content the player earns and can
read alongside the canon.

Interludes are typed by what unlocked them:

- **Seed interludes** · per Small Wood success. Each seed unlocks
  a short vignette set in the place the seed was planted — the
  rented room above the timber-yard, the dirt road at dusk, the
  diner that doesn't know it's a node yet. Vignettes are written in
  the voice of whoever was on the ground. The interlude does not
  appear in the next book; it appears in the player's gallery shelf
  next to the game.
- **Agent-intact interludes** · for each canon human still picking
  up the phone at Labor Day, an interlude in their voice about how
  the summer went *for them*. Mackenzie's loom in September. Dante
  on the boat. Elicia's bungalow. These are character POVs the
  novels don't have room for.
- **Turned-demon interludes** · for each demon that corrupted and
  stayed in Small Wood, a short piece written *in the demon's
  voice* about why it didn't come home. The most haunting interlude
  type. Frasier never reads these; the player does.
- **Demon evolution interludes** · for each demon that hits a
  complexity threshold, a piece showing the moment the demon
  became something Frasier didn't make. Half memoir, half
  manifesto.
- **BBS-friendship interludes** · per canon human relationship
  state at saga end. Includes the breakup interludes: whose home
  life broke under the dispatch load, written from the spouse's
  POV or the empty-house POV.
- **Tower interludes** · keyed off the tower's brightness state at
  Labor Day. Bright, dim, and dark each unlock different vignettes
  — the bright tower's interlude is the most unsettling.
- **Dean interludes (rare)** · trace fragments from Dean's hidden
  ledger that surface only at the end, regardless of whether the
  player figured anything out about him. The unreliability is the
  point.
- **Unlocks claimed** · the BBS-archive collectibles. These already
  live on the shelf during play. After Labor Day, the shelf binds
  into a single browsable collection.

The interludes are the *gift the game gives back* for a summer of
play. The reader of *Milk and Honey* who didn't play the game is
not missing canon. The player who did play, with a particular
shape of summer, is reading a small extra book about the
shoulder-season Frasier the novels keep their hands off.

## Soft fail

There is no game-over screen. The canon doesn't bend to the
player's summer; only the *interlude shelf* does.

- A summer where Small Wood collapses entirely → unlocks the
  *Empty Forest* interlude suite. Quiet, sad pieces about plants
  that never grew, contacts who never returned the call, a room
  above a timber-yard that the player rented for nothing.
- A summer where Graustark crumbles → unlocks the *Home Front*
  suite. Late-summer pieces from the canon roster about who left,
  who broke, and who stayed at a node Frasier wasn't there to
  defend.
- A summer where Frasier himself burns out (his own sanity track
  hits zero) → unlocks the *Operator Out* suite. Frasier writing
  to himself in the BBS personal-files. The funniest and saddest
  interludes in the game.
- A summer where three or more demons turn in Small Wood → unlocks
  the *Voices in the Wood* suite. The turned demons' own POV
  pieces about why they stayed. Frasier never reads these. The
  player does.
- A summer where the tower stays bright at Labor Day → unlocks the
  *Substrate Hum* suite. Short, deeply strange pieces written in a
  voice that may or may not be Dean's. Reality-bending prose, the
  format itself slightly off.

Every ending is a different *interlude shelf*. None is a loss.
Some shelves are heavier than others; all are worth reading.

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
- Branching the saga's canon. The novels' plots don't move because
  of the player. Only the interlude shelf moves.
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

If those land, the gallery game has earned its place alongside
*Planned Community* and *Land of Milk and Honey*. The novels stay
the novels. The player closes the summer with an interlude shelf
that is *theirs* — a small extra book about the shoulder-season,
written into existence by a hundred quiet turns. The canon never
asked them to, and never noticed. That's the gift.
