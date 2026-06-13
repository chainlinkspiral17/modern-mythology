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

## The three regions

### Graustark · home soil · low resistance

The TX/LA river country that vol 5 lived in. Nicola's house. The
boat (Dante's, now winding down). The diner. Frasier's network here
is dense, the locals are loyal, the problems are the *slow* kind —
old grief surfacing, succession arguments, infrastructure failing.

- **Native agents:** the canon hands aged forward — Nicola, Dante,
  the diner network (John Frank), Elicia from the bungalow.
- **Problem palette:** memorial-grief, family-succession, the boat
  closing, the cathedral, the diner's lease.
- **Strategic role:** supply. Graustark generates the
  *insight* and *cover* Frasier spends elsewhere.

### Harmony Creek Estate · engineered community · medium resistance

The planned-community thread *Planned Community* lives in. A new
build on the edge of nothing, all surveillance-soft and HOA-hard.
Frasier has a thin foothold here — two or three plants — and the
community's leadership is hostile in the polite way.

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

- **Native agents:** thin. One or two contacts Frasier has cultivated
  over years; both expensive to dispatch.
- **Problem palette:** local-press exposure, demon burn-out, a
  contact going dark, a seed dying before sprouting.
- **Strategic role:** investment. Every successful plant in Small
  Wood becomes a seed that *Milk and Honey* harvests in its opening
  chapters. Every failed plant is a setback Frasier carries forward.
- **The asymmetry:** Small Wood's escalation clock is twice as fast
  as the other two regions, and Frasier loses agents here at a much
  higher rate. The point is not to win Small Wood. The point is to
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

### Humans · slow, quiet, indebted

The canon roster, doing what they would actually do in vol 6's
timeline. Aged forward, sometimes tired, sometimes elsewhere.

- They accrue **obligation** rather than burn. Sending Mackenzie to
  Harmony Creek to look in on the model home is something she does
  because Frasier asked. The third time he asks, she asks something
  back. The fifth time, she stops answering.
- Each human agent has a private DM thread on the BBS. Their
  willingness to be dispatched is what's in the thread.
- Humans never "go dark" the way demons do. They just stop picking
  up.

The two economies (burn / obligation) are the strategic spine. A
run where Frasier leans on demons looks different from a run where
he leans on the canon roster, and the BBS layer reads each
differently.

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
  right board). *Milk and Honey* opens with that many seeds available
  to its protagonist.
- **Agents intact** · which demons are still on Frasier's roster at
  Labor Day. Which humans are still picking up the phone.
- **Cover remaining** · the network's deniability score. Low cover
  means *Milk and Honey* opens with Frasier already under watch.
- **BBS friendships** · per-canon-human relationship state at saga
  end. Frasier's call list going into vol 7.
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

Every ending is a starting state. None is a loss.

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
