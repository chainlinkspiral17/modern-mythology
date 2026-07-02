# COMMUNITY PLANNED · Turn Design

Fourth sibling doc to LORE / SPEC / WEEKLY. This one answers the
specific question: **what does the player actually do, moment to
moment, across the 100 turns of the summer?**

The brief: a thematic, suspenseful strategy game playing 20-40
hours beginning to end depending on engagement. The turn loop has
to carry that range — be quick enough for a casual play, deep
enough for a careful one, and evolve across the summer so the
player who reaches Labor Day is doing things they could not have
done at Memorial Day.

## The play-time budget

20-40 hours over 100 turns means **12-24 minutes per turn
averaged.** The actual distribution is not flat:

| Turn type | Count | Time each (casual) | Time each (deep) |
|---|---|---|---|
| Quiet weekday turn | ~60 | 3-5 min | 10-15 min |
| Active weekday turn (dispatch + event) | ~24 | 8-15 min | 20-30 min |
| BBS night (every 7th) | 14 | 30-60 min | 90-180 min |
| Crisis weekday turn (rare) | ~2 | 15-25 min | 40-60 min |
| **Total** | **100** | **~17 hours** | **~42 hours** |

The 20-hour run is the casual player who reads the surface, makes
clean strategic decisions, doesn't deep-read every BBS thread, and
finishes the summer. The 40-hour run is the patient player who
reads every DM, decodes the sysop circle's vocabulary, deep-dives
the hidden boards, sits with the Cathedral Letters. Both are
intended; both are valid; both reach Labor Day.

## What a turn is

A turn is **one day in Frasier Temple's life**, lived from inside
the Cathedral of Rust and Code. The player is Frasier. The
warehouse is the interface. The world outside is the strategic
map.

A turn has four phases, played in soft order (the player can
move between them freely):

### 1 · MORNING (the opening moment)

The player loads the day. A short cinematic moment lands:

- **The warehouse at the hour.** Light through the river window
  (cool blue at dawn, warm gold at evening), the workbench in
  its state, the BBS terminal humming at idle. Faith asleep
  somewhere in frame. A single ambient cue (cicadas, rain,
  river-bank lap, distant freight horn).
- **One line of narration.** Frasier's internal register —
  *"the brass railing is the wrong brass again. Tuesday."*
  Bone-dry, three to twelve words. Sets the day's tone.
- **The phone (sometimes).** A buzz from a pocket Frasier
  hasn't yet picked up. The player can answer immediately or
  let it sit. (See the Phone Mechanic below.)

The morning takes 5-30 seconds depending on whether anything is
already pulling at the player's attention. Most mornings are
quiet.

### 2 · SURVEY (reading the state)

The player walks through the warehouse — which is the strategic
map, rendered as the Cathedral floor in painted top-down — and
reads the state.

What's visible without action:

- **The strategic map.** Three regions (Graustark, HCE, Small
  Wood) on the warehouse floor as miniature dioramas Frasier
  built. Nodes are physical pieces; problems are small painted
  tokens that have appeared overnight.
- **The agent dock.** A small shelf on the wall where the demon
  icons sit. Active demons are on the map; resting demons are
  on their shelf positions. Human-agent portraits hang in a
  small grid next to it.
- **The tower brightness chart.** A small ANSI-style readout in
  the corner of the map, week by week. The current week's cell
  is updated overnight; the player learns to glance at it
  first.
- **The unread badge.** A small number next to the BBS terminal
  showing unread DMs and threads since last log-in. Does not
  press the player to read; just shows.
- **The wall calendar.** Days crossed off. Marked events for
  the week (the surviving son's restaurant's Friday dinner,
  Maya's letter expected, etc.).

What requires action to learn:

- **Hover over a problem** — its escalation clock and current
  resolution profile.
- **Hover over an agent** — current state, burn/obligation,
  recent post register (if a demon).
- **Click a control node** — open a small inspection panel.
- **Inspect an entity's tilt** — requires the player to deliberately
  highlight them. The tilt rating itself is never numeric; it
  shows as a register descriptor (*nominal* / *drift visible* /
  *concerning* / *committed*).

Survey takes 1-10 minutes depending on depth. A quiet day's
survey is "nothing new, end day." A loud day's survey is "two
new problems, one tilt rise, one demon reporting in odd
register."

### 3 · ACTIONS (doing the day)

The player does some subset of the day's available actions. None
are required. A day with zero actions is *valid* and sometimes
correct.

Action set:

- **Dispatch an agent** to a problem or a region. Costs the
  agent some travel/execution days, costs Frasier the agent's
  use, costs the agent burn/obligation/life-cost.
- **Recall an agent.** Sometimes you change your mind. Recall
  costs the agent +1 burn or +1 obligation depending on class.
- **Read an unread DM.** Reading is free; the DM may surface a
  tilt change, a refusal, a personal beat.
- **Reply to a DM.** A single-sentence reply. Has consequence
  next turn.
- **Make a phone call.** Outbound — to a sysop, to the
  surviving son, to Otis Vandermeer in Small Wood. Costs time;
  surfaces information faster than DM.
- **Take a phone call.** A buzz earlier in the morning is
  pending; the player picks up now, or doesn't.
- **Work at the workbench.** Spend the day at the bench. No
  strategic action; accumulates a Cathedral Letter day (the
  workbench-presence-as-currency mechanic from W10 onward).
- **Walk to a Cathedral station.** Diegetic action: Frasier
  walks to the EMPRESS station, the EMPEROR station, the
  HIEROPHANT station, etc. Each station has its own small
  state — letters Nicola has sent, photos Antonio left, the
  cypress beam fragment under the CHARIOT marker. Walking the
  Cathedral is contemplation; sometimes a fact surfaces.
- **Visit a region in person.** Frasier himself dispatches. Big
  cost — Frasier offline for 2-3 days; the warehouse is empty;
  any BBS night during the absence is unattended. Big payoff
  — Frasier can do things agents can't.
- **End day.** Close the turn. Time advances.

Most days the player does 1-3 actions and ends. Some days the
player does 5-7 actions and ends. Some days the player just
sits at the workbench and ends.

### 4 · END-OF-DAY (the world moves)

When the player ends the day, a short animated transition lands:

- **The warehouse dims** (or brightens, depending on hour).
- **The map updates.** Active dispatches advance one day along
  their travel arcs. Problems with expired clocks escalate.
  New problems may spawn (Sundays).
- **Event banners** show the day's resolved events: an agent
  returned, a tilt shifted, a problem escalated, a sighting
  occurred, an unread thread expired.
- **One line of closing narration.** *"Tuesday closes. The
  cicadas at dusk-frequency."*
- **The morning of the next day loads.**

End-of-day takes 10-30 seconds. The animation is short enough
that it doesn't bottleneck a quick player; long enough that a
deep player has the breath between turns the design wants.

## The diegetic interface · the warehouse as UI

Everything the player clicks on lives **inside the Cathedral**.
There is no menu screen, no spreadsheet view, no system panel.

- **The strategic map** = the Cathedral floor's dioramas.
- **The agent dock** = the shelf on the wall.
- **The BBS terminal** = the phosphor-green CRT in the corner.
  The player walks Frasier to it, sits down, dials in.
- **The workbench** = the workbench. Frasier sits at it to work
  on Cathedral Letter days. The bench has a state visible to
  the player — what tool is out, what model is half-built, what
  notebook is open.
- **The phone** = on the workbench's edge. Buzzes when there's
  an incoming call. Has a small unread-message indicator.
- **The river window** = the tall paned window onto the river.
  Sometimes the player notices something through it. The
  bird-watcher's view of the osprey nest in the iron struts;
  the rare Aria sighting in W13.
- **The wall calendar** = a wall calendar.
- **Faith the dog** = sometimes underfoot. Sometimes in the
  back room. A small ambient presence.

The player's mouse moves Frasier through the room. Click on a
location, he walks there. Click on an object, he interacts with
it. The room is the UI. The UI is the room.

This is a **point-and-click strategy game** as much as a turn-
based one. The diegetic interface is half the game's pleasure.

## Making it suspenseful · the moment-to-moment mechanics

Strategy games tend to be cerebral. COMMUNITY PLANNED has to also
be **thematic and suspenseful**, which means the player needs to
feel the day in their stomach, not just their head. Six mechanics
do this work:

### 1 · The phone

The phone on the workbench buzzes at unpredictable moments during
the morning or the survey. Sometimes during the actions phase.

When it buzzes, a small icon pulses in the player's HUD. The
player can:
- Pick up immediately (interrupts whatever else they were doing)
- Let it ring through (the buzz stops after 4-5 seconds; the
  call is voicemail)
- Pick up later in the turn (voicemail is queued)
- Never pick up (the missed call becomes a small ledger entry,
  occasionally consequential)

Most calls are not strategically critical. Some are. The player
learns, by W4 or so, which numbers to glance at and which to
ignore. The phone is the chief vector of suspense — *what if this
one's the one I shouldn't have let ring?*

### 2 · The unread thread

Unread DMs and BBS threads accumulate. The player can let them
sit. Some, after sitting too long, **expire** — Nicola's letter
arrives the day after she expected Frasier to read her DM, and
the letter's text reads slightly differently than the version
that would have arrived if he'd replied. The change is small.
The change is real.

The Refused Pile (W6 onward) and the Cathedral Letters suite
(W10 onward) both have analogs of this — unread expiration as a
quiet pressure that does not loudly punish but does softly
shape the shelf at Labor Day.

### 3 · The tower glance

The tower brightness chart in the corner is the player's
**weather report**. The player learns, by W7, to glance at it
first thing every morning. The chart fills in left to right
across the summer; a single dim cell amid bright weeks is the
visual register of substrate weather.

The chart's *prediction layer* (faint shading for what next
week's brightness might be) is a derived signal from the sysop
circle's posts. Reading carefully enough to update the prediction
layer is one of the patient player's rewards.

### 4 · The half-degree

Tilt ratings on tracked entities surface as **register
descriptors**, never numbers:

- *nominal* (tilt 0-2) — entity reads as themselves
- *drift visible* (tilt 3-5) — entity's posts have a subtle
  off-ness the patient reader catches
- *concerning* (tilt 6-7) — the BBS sysops have started
  cross-referencing this entity's posts
- *committed* (tilt 8-9) — the player has lost them but doesn't
  know it yet
- *converted* (tilt 10) — gone

The player cannot see the register descriptor without inspecting
the entity's most recent post. **Inspection is an action.** The
turn budget therefore forces the player to choose which entities
to read for tilt and which to read for content. The
mis-prioritized inspection becomes a small private regret.

### 5 · The workbench-vs-strategy trade-off

A day at the workbench is a day not dispatched. Cathedral Letter
days bank toward the final suite; dispatched days move strategic
pieces. The trade-off is constant and visible: the bench has its
own day-count, displayed next to the model Frasier is currently
working on.

The Cathedral Letters mechanic (W10 onward) makes this trade
explicit; before W10 the player can still work at the bench but
without the Letter accumulation, so it's "free" days the player
can spend on contemplation. After W10 the bench has weight.

### 6 · The cathedral hum

A faint **audio cue** plays at unpredictable moments during a
turn — usually morning, sometimes mid-action. Three pitches:

- A low warm hum. Means a Cathedral station has gained a small
  state change (Nicola sent a new letter to the EMPRESS wall;
  Mackenzie's loom has updated in MACKENZIE's diorama; Antonio's
  desk in the EMPEROR station has a different paper on it).
- A high cool ring. Means something off-stage moved — the tower
  brightness chart updated mid-day, an Aria sighting registered
  somewhere in the network, a sysop posted unexpectedly.
- A faint static rasp. Means a tilt rating changed somewhere on
  the map.

The hum is non-prescriptive. The player can ignore it. The hum
will land on something the player is looking at within 30
seconds, or not. The player learns, by W4 or so, to *listen* in
addition to *look*.

## Making it interactive

What the player physically does, beyond clicking:

- **The point-and-click warehouse.** Move Frasier around the
  Cathedral floor. Walk to nodes. Pick up objects. The pace is
  deliberately slow; Frasier is middle-aged.
- **The BBS terminal.** Keyboard-driven, period-correct.
  Single-letter board navigation. Type slash-commands. The
  terminal feels like a terminal. The player can use the mouse
  but the keyboard is faster.
- **The phone.** Two-button decision: answer or don't. The
  voicemail playback is text-on-screen with a typed-line
  animation; the player reads at their own pace.
- **The DM reply.** Free text input, limited to one short
  sentence. The player types. Frasier sends.
- **The workbench.** A small mini-game per Cathedral Letter day:
  a short typed letter, a small model-assembly action, a
  station-refinement gesture. Each is 30-90 seconds of small
  interaction.
- **The dial-up directory.** Five public numbers, plus SNACKS
  once admitted. The player dials by clicking digits or typing
  the number. The connect tone plays. The 14.4k handshake.
- **The map dispatch.** Click an agent, click a destination,
  click confirm. Or drag-and-drop.
- **The inspection panel.** Hover for tooltip, click for the
  full panel (which costs an action point in the late game).

The mix of point-and-click, keyboard, free text, and small
mini-games keeps the player physically engaged. The pacing is
slow but the **input variety** is wide.

## Making it evolve · the 14-week curve

The turn loop changes shape across the summer. Each week's
mechanic introduction (per WEEKLY doc) layers in new turn-time
costs:

| Wk | New element | Effect on turn time |
|---|---|---|
| W1 | basic dispatch | turns are simple, fast |
| W2 | DMs | + 1-3 min per turn (reading replies) |
| W3 | hidden boards | + 5-10 min per BBS night |
| W4 | tilt detection | + 3-8 min per turn (inspection cost) |
| W5 | slow witness | dispatch decisions branch wider |
| W6 | agent refusal | sometimes a multi-minute decision moment |
| W7 | substrate flicker | first crisis turn (15-25 min) |
| W8 | migrant branching | named-decision turns (10-20 min) |
| W9 | demon turning | a high-emotion turn (15-25 min) |
| W10 | Cathedral Letters | bench-day decisions add weight |
| W11 | vocabulary glossary | re-reading prior weeks (the patient player spends a whole BBS night) |
| W12 | endgame push | turns compress, decisions accelerate |
| W13 | the sighting | one quarter-second of animation; player will replay |
| W14 | binding | BBS night doubles in length |

The arc:
- **W1-3** · learning. Turns are quick. The player builds habit.
- **W4-6** · deepening. The first complex turns. Tilt and
  refusal force harder reading.
- **W7-9** · crisis era. The summer's worst turns are here.
- **W10-11** · spiritual layer. Turns slow down. The Cathedral
  Letters and the glossary reward patience.
- **W12-13** · endgame. Turns get short again, but the stakes
  are highest.
- **W14** · binding. The final BBS night is, in itself, the
  experience the whole summer was for.

A player who finishes the casual run does ~17 hours and feels
the shape. A player who finishes the patient run does ~40 hours
and has read every thread, decoded every register, written every
Cathedral Letter, sat with every refusal. Both end the same way:
the seven chords of the suite-binding play, the BBS goes dark,
the tile stays lit on the gallery.

## Three concrete turn examples

To make the design tangible, here are three exemplary turns at
three points in the summer.

### W1 · Day 3 (Tuesday morning, late May)

**Morning.** The warehouse at 7:14 AM. Light cool through the
river window. Faith is at her food bowl in the back. The
workbench has the cypress beam fragment under the CHARIOT marker
visible. The narration: *"the brass railing is the wrong brass
again. Tuesday."*

**Survey.** Three control nodes in Graustark held and stable.
HCE has two contested nodes (model home, HOA office). Small
Wood has the room above Wagner's Hardware as Frasier's only
foothold. No new problems overnight. Two unread DMs (Elicia's
tape thread; the surviving son's first DM).

**Actions.** The player reads Elicia's DM (45 seconds). It's
about the tape. No reply needed. The player reads the surviving
son's DM (60 seconds). It's about Sammy. The player composes a
single-sentence reply: *"I'll come by Friday for dinner."*
Frasier sends. The player dispatches the vagrant to the
riverfront for routine recon (one click). The player ends day.

**End-of-day.** Vagrant departs. Map updates. *"Tuesday closes.
The cicadas at dusk-frequency."* Wednesday morning loads.

**Time elapsed:** 4-7 minutes casual, 10-15 deep.

### W7 · Day 47 (Wednesday, mid-July, substrate dim)

**Morning.** The warehouse at 8:14 AM. Light wrong — the
overhead fluorescents are flickering at a frequency they should
not be. Faith is in the back room, agitated. The narration:
*"the tower has been dim three days running. the apartments at
HCE Phase II have not, this morning, all turned on their
sprinklers."*

**Survey.** The tower brightness chart in the corner shows three
dim cells in a row. The strategic map looks different — three
problems on it that were not there yesterday, two of which are
flagged as "uncertain origin" (the substrate effect: problems
mis-classified). One demon's dispatch reported in last night
from a region it was not sent to. Unread badge shows seven
threads.

**Actions.** The player reads the demon's misdirected dispatch
report. The post-register is OFF — tilt visible. The player
inspects the demon: *concerning* (tilt 6). The player composes
an urgent message to the demon-rest board THE_BASEMENT to pull
the demon home. The player dispatches the moth to one of the
new HCE problems. The player phones Otis Vandermeer in Small
Wood about the surveying flag — the call goes 4 minutes; Otis
has news. The player checks DRY_BLOOM.BBS to see if PALOMINO has
posted (she has not; week 1 of her silence). The player ends
day late and tired.

**End-of-day.** Two dispatches in flight. One demon being
pulled home. The flicker continues. *"Wednesday closes. The
warehouse fluorescents at the wrong frequency."*

**Time elapsed:** 15-22 minutes casual, 35-50 deep.

### W13 · Day 87 (the sighting day, mid-August)

**Morning.** The warehouse at 6:42 AM. Cool blue light through
the river window. Faith asleep on the back-room rug. The
workbench has the *Cathedral Letter* notebook open to a blank
page. The narration: *"the iron struts catch the morning the
way they used to."*

**Survey.** The tower brightness chart shows two bright weeks
followed by yesterday's dim cell. Most regions stable. The
endgame push is on — three migrant arcs simultaneously in flight
(Mae Halsey-Knight, the unnamed young woman from W11, the
Vargas-Quintana family). Unread badge low — Frasier has been
keeping up.

**Actions.** The player walks Frasier toward the BBS terminal,
intending to dial in early. Mid-walk — *quarter-second* — the
player sees a figure through the river window between the iron
struts where the bird-watcher used to stand. Yellow rainslicker.
Blue curls. Purple-rimmed glasses. The figure is not there.

(The animation is short enough that some players will miss it.
A small subtitle line at the bottom of the screen confirms the
sighting for the player who blinked: *"a quarter-second."* The
patient player will replay the day to catch it again.)

The player has Frasier sit at the BBS terminal. Dials RUST_CODE.
Reads STEEPLE's morning post on OVERPASS. The player does NOT
post about what Frasier just saw. Frasier walks to the workbench
and composes a Cathedral Letter entry — the day's gravitational
center, the player will see at Labor Day. The letter is short.
The player ends day quietly.

**End-of-day.** Migrant arcs advance. The sighting is logged
internally; the count is now 12. *"Saturday closes. The river
window the way it used to be."*

**Time elapsed:** 8-12 minutes casual, 25-40 deep. The patient
player will replay the morning at least once.

## UI / UX notes

A small set of cross-cutting design rules:

- **No timer ever.** The player takes a turn at the speed they
  want. Long pauses mid-action are welcome.
- **Diegetic indicators only.** No floating health bars. No
  numeric counters except the wall calendar's date. The tower
  brightness chart is the most "system-looking" element and it
  is rendered as ANSI inside the strategic map.
- **No auto-play.** End-of-day is the only mode-shift. There is
  no fast-forward, no skip-week, no autopilot. The player plays
  every day.
- **Save-on-end-of-day.** The save state writes when the day
  closes. The player can quit mid-turn and resume; the in-
  progress turn rolls back to the morning state.
- **The deep-read toggle.** A gallery setting (introduced in
  SPEC) lets the player switch between surface-read and
  deep-read BBS modes. Both write the same save state; the
  difference is what the player sees during BBS nights.
- **The replay sigil.** Days the player wants to revisit can be
  marked with a small sigil. The gallery's day-log lets the
  player jump back to a marked day after Labor Day — read-only,
  no rewriting. (Save-state-untouched.)
- **Accessibility.** The player can adjust the typewriter speed
  for typed narration, the volume balance for the audio cues,
  and the contrast for the ANSI elements. The Cathedral hum can
  be disabled for the player who finds it intrusive.

## What this design enables

By Labor Day the player has lived a hundred days. Each day was
small. Each day was specific. Each day's small specifics
accumulated into a summer that:

- The player can describe by Tuesday.
- The player can grieve by August.
- The player can close by Labor Day.
- The player can return to, marked-sigil by marked-sigil, after
  the summer is over.

The turn loop is the **diegetic vehicle** for the saga's larger
work: the conversion that creeps through ordinary attention, the
migration that delivers people one specific day at a time, the
faith that builds across a hundred small mornings without ever
naming itself.

The strategy isn't the game. The strategy is *the medium of the
game.* The game is what the strategy is for.

## Open questions for the next pass

Held for when the implementation phase opens:

- **Save slot architecture.** Should the player be able to save
  multiple summers? The "branching playthroughs" implication is
  attractive but the interlude shelf is meant to be a single
  player's record.
- **NG+ behavior.** Should a second playthrough alter anything?
  (Recommendation: no. The summer is what it is.)
- **Multiplayer.** Out of scope; held to the spec's no-multiplayer
  rule.
- **Accessibility for the audio cues.** Cathedral hum must have
  full visual equivalents.
- **Mobile play.** Out of scope for first build; the diegetic
  warehouse interface assumes desktop.

The turn is the day. The day is the room. The room is the
warehouse. The warehouse is the cathedral. The cathedral is
the thing Frasier is building, one day at a time, that Aria will
eventually move into.
