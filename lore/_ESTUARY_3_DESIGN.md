# ESTUARY 3 — gallery game / cabin slowstock

Vol 7 · Land of Milk & Honey · the cabin's personal slowstock
library. A playable-from-gallery mini-game standing in for the
in-fiction early Oneironautics catalog. This doc is the design
brief; the resources live under
`godot/resources/games/vol7/estuary_3/`.

## In-fiction premise

Oneironautics Inc. shipped the first *Estuary* stick in 2001. It
was a soft-simulation of an Oregon-coast estuary — you managed a
handful of species, ran the tides, watched the mudflats. It sold
mostly to Pacific Northwest school libraries.

*Estuary 3* (2003) is the entry the studio is quietly embarrassed
about and quietly proudest of. The team, that year, spent six
months trying to make a "Sam's Summer Shifts" competitor — a
Kwik Stop manager game meant to compete with the RANCH's
convenience-store-management stick that had been the surprise hit
of Q3 2002. The Oneironautics team's version, three months in,
was not fun. They shelved it. Then one of the junior designers —
Ines Rocha, whose *Estuary 7* landscape-template Brandon would
submit in 2046 (see `vol7_epilogue_gallery.json`) — spent a
weekend welding the failed Kwik Stop game onto the front of a
new Estuary build. The game boots as a Kwik Stop shift; a third
of the way through, the counter dissolves into an estuary planner.
The convenience store the player has been running was, all along,
the town the player is now shaping. Reviewers didn't know what to
do with it. It sold ~40,000 units. It has, in the Vol 7 present,
a cult following.

The player finds *Estuary 3* on the cabin's slowstock shelf in
Chapter 12 or 13 (Per's father's cabin, built '79). The shelf
holds ~30 sticks, mostly from Olaf's era. Estuary 3 is the one
Tem tells the player, quietly, to try.

## Design pillars

1. **The genre pivot is the whole point.** Act 1 must feel like
   a competent 2003 SCUMM-descendant. Act 2 must feel like a
   competent 2003 soft-sim landscape planner. The join in the
   middle must feel like a deliberate design choice that the
   in-fiction studio was proud of, not a bug.
2. **Retro-authentic UI.** 640×480 target resolution, 256-color
   palette, chunky pixel font, one-tone chiptune-adjacent
   background loop. Everything in-engine — no fake CRT filter
   over the top. The user asked for the *early 2000s* feel; that
   means we commit to the constraints of the era, not decorate
   with them.
3. **Short session.** The gallery game is 15-25 minutes end to
   end. Modeled on the *Kentucky Route Zero* freeware precursor
   *Limits & Demonstrations* (30 min) and *The Entertainer* (20
   min), both of which succeeded at "short in-fiction game that
   deepens a longer parent work."
4. **The Kwik Stop is the estuary.** Every mechanical action in
   Act 1 has a landscape-scale echo in Act 2. Restocking the
   cooler → the salmon run. Sweeping the parking lot → the
   Sunday tide-drag. Handling the 2 AM customer who won't leave
   → a stalled weather system.
5. **Cabin-shelf discipline.** The player boots this from the
   gallery. It doesn't need to hook into the main VN save. It
   doesn't need to persist much. It only needs to record: "the
   player finished Estuary 3" as a lore-token-shaped fact, so
   later Vol 7 dialogue can reference it.

## Structure

### Act 1 · Kwik Stop shift · ~10 minutes

Point-and-click at a single fixed screen: the interior of a
Kwik Stop at 2:14 AM, one week before Labor Day. Behind the
counter is the player-character, Sam (the joke on Sam's Summer
Shifts is explicit in-fiction). Six interactable objects:

- **Register** (verb: OPERATE) — process customers as they arrive
- **Cooler** (verb: OPEN, verb: RESTOCK) — three shelves of drinks
- **Broom** (verb: TAKE, verb: SWEEP) — the parking lot needs it
- **Phone** (verb: ANSWER) — rings four times over the shift
- **Radio** (verb: TUNE) — six stations, some meaningful
- **Backroom door** (verb: LOOK, verb: OPEN) — locked until turn ~30

Six customer types cycle in:
1. **The regular** — buys the same three items every night
2. **The tourist** — asks for directions, doesn't buy
3. **The trucker** — buys black coffee + one lottery ticket
4. **The kid on a bike** — never buys, always looks at the beef
   jerky, always leaves
5. **The other clerk from up the road** — visits on their break,
   trades gossip
6. **The 2 AM customer who won't leave** — sits in the corner
   booth, buys nothing, stays. Reappears every night.

Shift runs 15 turns (each turn = ~40 seconds of real time). The
player who processes cleanly ends the shift at 5:14 AM with a
tally sheet. The player who doesn't gets the "you'll have to
close up anyway" transition.

### Interstitial · ~30 seconds

The 2 AM customer stands up. Walks to the backroom door. Opens
it — the door was never locked. Inside is not a backroom. Inside
is the estuary at first light, seen from above.

### Act 2 · Estuary planner · ~10 minutes

Top-down view of the estuary the town sits on. Seasons pass in
compressed time. The player has three axes of control:

- **Tide gate** (open / partial / closed)
- **Riparian buffer** (which strips of shore stay wild)
- **Species set** (which of the eight local species get the
  seasonal boost — coho, chum, sturgeon, cutthroat, otter,
  heron, sedge-wren, tidewater goby)

The mechanical actions from Act 1 are visible as landscape
inputs. The player can pull up "the register tape from last
night" as an overlay and see how the customer decisions have
seeded species survivability. The Kwik Stop is at coordinate
(384, 210) — a small pixel-square in the top-right of the map,
still there.

The Act 2 objective is to survive one full year — spring,
summer, fall, winter, spring. If the tide gate is closed at the
wrong month the salmon run collapses. If the riparian buffer is
too aggressive the tourism drops (and the Kwik Stop, still there
in the top-right, quietly starts losing customers, which the
player sees as small numbers in the corner).

### Ending · ~1 minute

The seasons finish. The player is asked, once, whether Sam
should keep working at the Kwik Stop next summer. There are
three options, all valid. The game records the choice, prints a
one-paragraph epilogue, and returns the player to the gallery.

## The tie-in

The choice the player makes at the end of Estuary 3 lands as a
lore token that Tem, Lena, or Per can reference in a later Vol 7
chapter. Not gated — the game plays fine without it — but the
player who does play it gets a small "you actually finished
Estuary 3?" beat somewhere in Chapter 15 or 16.

## Out of scope for the first pass

- Sound. Ship silent. Retro chiptune loop is a follow-up.
- Full customer roster. Ship four of the six customer types.
- Full Act 2. Ship spring + summer; fall + winter are follow-up.
- Save between acts. Ship as one 20-minute sitting.
- Native pixel-perfect rendering. Ship with Godot's stretch mode
  and a chunky font; commit to the era in a follow-up polish
  pass.

## File layout

```
godot/resources/games/vol7/estuary_3/
  manifest.json                 # cover art label, era, cover blurb
  act1_kwik_stop.json           # SCUMM-style room + verbs + customers
  act2_estuary.json             # landscape-sim node list
  ending.json                   # three-option branching epilogue
  README.md                     # in-fiction manual text
godot/scenes/games/estuary_3/
  Estuary3Host.gd               # single scene · switches between acts
  KwikStopRoom.gd               # act 1 room controller
  EstuaryPlanner.gd             # act 2 map controller
  Estuary3Ending.gd             # ending screen
```

## Development order

1. **This commit.** Design doc + manifest + Act 1 script (JSON)
   + Act 2 script (JSON) + ending JSON. No Godot scripts yet.
2. **Second commit.** Estuary3Host + KwikStopRoom minimal — one
   verb (LOOK), one customer, prints text. Boot-from-gallery.
3. **Third commit.** All six verbs + four customer types + the
   backroom-door transition beat.
4. **Fourth commit.** EstuaryPlanner minimal — spring + summer
   seasons render.
5. **Fifth commit.** Ending screen + gallery integration + Tem's
   Chapter 15 callback line.

Ship each commit playable in isolation.
