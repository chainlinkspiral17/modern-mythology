# ESTUARY 3 — cabin slowstock (major gallery game)

Vol 7 · Land of Milk & Honey · the cabin's personal slowstock
library. A playable-from-gallery slowstick in the tradition of
early-2000s Oneironautics Inc. releases. **Full length: ~10–12
hours across four acts.** Sits inside the wider slowstock library
system (see §Library, below), which unlocks more shelf entries as
the player finishes each stick.

This doc is the design brief. Resources live under
`godot/resources/games/vol7/estuary_3/` and
`godot/resources/games/vol7/library/`.

## Scope revision

The first design pass (2026-07-04) scoped Estuary 3 as a 25-minute
mini-game. That's the wrong shape. Slowsticks from the early
Oneironautics era were 8–15 hours; the cult-favorite ones were the
15+ hour ones that kept dilating out into unexpected new genres.
Estuary 3, per its in-fiction reputation, is the pivot-into-
landscape-sim that made Ines Rocha's career. It has to actually
be that.

New scope: four acts, roughly 2–3 hours each. Each act is a
different playstyle. The joins between acts are the whole point of
the game.

## In-fiction premise (unchanged)

Oneironautics Inc. shipped the first *Estuary* stick in 2001. It
was a soft-simulation of an Oregon-coast estuary — you managed a
handful of species, ran the tides, watched the mudflats. It sold
mostly to Pacific Northwest school libraries.

*Estuary 3* (October 2003) is the entry the studio is quietly
embarrassed about and quietly proudest of. The team, that year,
spent six months trying to make a "Sam's Summer Shifts" competitor
— a Kwik Stop manager game meant to compete with the RANCH's
convenience-store-management stick that had been the surprise hit
of Q3 2002. The Oneironautics team's version, three months in,
was not fun. They shelved it. Then Ines Rocha, junior designer,
spent a Labor Day weekend welding the failed Kwik Stop game onto
the front of a new Estuary build. The game boots as a Kwik Stop
shift; the seams eventually give and the game becomes an estuary
planner; the estuary planner eventually gives and the game becomes
something else again. Reviewers in 2003 didn't know what to do
with it. It sold ~40,000 units — huge for the era. It has, in the
Vol 7 present, a cult following.

The player finds *Estuary 3* on the cabin's slowstock shelf in
Chapter 12 or 13 (Per's father's cabin, built '79). The shelf
holds ~30 sticks, mostly from Olaf's era. Tem tells the player,
quietly, to try Estuary 3 first.

## Design pillars

1. **Genre pivots as design.** Each act is a different game. Act
   1 is a SCUMM-descendant. Act 2 is a top-down soft-sim. Act 3
   is a text-forward walkabout. Act 4 is something the player
   discovers. The pivots ARE the game.
2. **Retro-authentic UI.** 640×480 target, 256-color palette,
   chunky pixel font, one chiptune loop per act. Everything in-
   engine — no fake CRT filter overlay. Commit to the era's
   constraints, don't decorate with them.
3. **Every act has a full story shape.** Act 1 is not a tutorial.
   Act 4 is not an epilogue. Each act, on its own, has a
   beginning + middle + end and could stand alone as a short
   Oneironautics release. Together they interlock.
4. **Mechanical echoes across acts.** Actions in Act 1 seed state
   in Act 2. Choices in Act 2 shape Act 3's town. Act 3 reveals
   which of Act 4's endings are available. The player who plays
   the whole thing sees the interlock; the player who stops after
   Act 1 still gets a complete Kwik Stop story.
5. **Cabin-shelf discipline.** All progression persists to
   GauntletState. Finishing a stick unlocks the next. Nothing
   requires the main VN save.

## Structure

### Act 1 · THE SHIFT · ~2 hours · SCUMM-descendant

Twelve nights at the Kwik Stop across the last two weeks of the
summer season. Each night is one 15-turn shift from 2:14 AM to
5:14 AM. One fixed room (the counter). Six interactable objects,
six verbs, six customer types plus specials. Between nights, a
brief interstitial: Sam driving home in the pre-dawn along the
coast highway, one line of narration.

Ongoing threads:
- **Mr. Aandahl's lottery arc.** Every night's scratcher choice
  matters. On night 11 the outcome lands.
- **The kid on the bike.** Speaks for the first time on night 5.
  His arc closes on night 9.
- **The other clerk from up the road.** Trades gossip nights 1–6.
  On night 7 she doesn't come in — the shell station closed at
  midnight. Where she goes on nights 8–12 depends on player
  choices.
- **The tourists.** Four different families across the twelve
  nights. Each is one line of dialogue and a choice.
- **The 2 AM customer.** Sits in the corner booth every night.
  Never orders. On night 12 he stands up and opens the backroom
  door. The door was never locked.
- **The phone.** Rings 3–4 times a night. Jules (manager) on
  nights 1, 5, 9. Wrong-number-Ines on nights 2, 6, 10. Nobody-
  is-there on nights 3, 7, 11. Silence on 4, 8, 12.
- **The radio.** Six stations, each with a per-night rotation.
  105.3's Christian talk carries a background story about the
  town's mill closure. 1150 AM's fishing report predicts the
  next day's tides — matters in Act 2.

Act 1's ending is night 12's backroom door. The tally sheet
prints. The transition begins.

### Interstitial · ~2 minutes

The 2 AM customer walks past the counter, up the two steps, and
opens the backroom door. Inside is not a backroom. Inside is the
estuary at first light, seen from the tide gate looking east
toward the coastal-highway rise. The Kwik Stop is a small yellow
square in the top-right of the frame. Sam is still in it. Sam
does not know Act 2 is happening.

### Act 2 · THE ESTUARY · ~2.5 hours · soft-sim landscape planner

Top-down 640×480 view. A full 52-week year, compressed to ~90
minutes of session time. Four seasons plus a second spring. Three
control axes per season — tide gate (open/partial/closed),
riparian buffer (minimal/moderate/wide), species boost (two of
eight, refreshed each season).

Each Act 1 decision surfaces as a landscape input in Act 2. The
register tape from Act 1 sits as a foldable overlay in the top-
right; the player can pull it up mid-planning to see how the
customer choices seeded species survivability. The Kwik Stop is
at (384, 210) and its receipts show in the map's UI.

Weather events (once per season, rolled at season-start): fog,
king tide, mill outfall accident, wildfire smoke, seiche, algal
bloom, coho fry release. Each has a mechanical effect and a
narrative beat.

Species roster: coho, chum, sturgeon, cutthroat, otter, heron,
sedge-wren, tidewater-goby, plus (unlockable in Act 3) tidewater
lamprey and pygmy owl.

Ending of Act 2: the second spring lands. Sam is on shift tonight.
The screen dims to a single line: "Sam is on shift tonight. Should
Sam keep working here next summer?" The player has three options.
The choice records but does NOT end the game. Instead, the choice
is Act 3's opening frame.

### Act 3 · THE TOWN · ~2.5 hours · text-forward walkabout

The player is Sam. It's the morning of Labor Day. Sam has slept
four hours after the last shift. Sam has decided (per the Act 2
final choice) whether to stay another summer. Now Sam walks the
town — the small coastal-highway town the Kwik Stop sits on the
edge of.

Nine locations, walkable from a hub map:
1. The Kwik Stop (revisit, in daylight, empty).
2. The shell station up the road (closed).
3. The pier.
4. The mill office (closed since '96).
5. The bookstore Ines Rocha's mother owned before she died in
   1998 (Ines herself, still a junior designer in 2003, is
   canonically the mother's daughter in this game — a
   meta-touch the '03 reviewers missed).
6. The Aandahl house.
7. The elementary school (closed for summer).
8. The tide gate itself.
9. The cabin road, which the player cannot walk down (blocked;
   a note on the gate reads BUILT '79 · PRIVATE).

Each location has 3–6 hotspots. Interactions are text-forward,
graphic-adventure verb-lite (LOOK, TALK, USE). NPCs from the
Kwik Stop reappear in daylight: Mr. Aandahl in his yard, the
other clerk at the pier, the kid on the bike outside the school,
the 2 AM customer at the tide gate.

Ongoing thread: Sam is trying to decide whether the choice made
at the end of Act 2 was the right one. Each conversation weighs
into the deciding.

Act 3's endpoint: Sam returns to the Kwik Stop as dusk falls.
Jules is behind the counter. Jules hands Sam the keys or Sam hands
Jules the keys. The framing depends on the walk.

### Act 4 · THE FIFTH SEASON · ~2 hours · discovered playstyle

The player boots Act 4 and is not told what kind of game they're
playing. Reviewers in 2003 spent most of their column inches on
this act. The out-of-fiction author's note here is: **the act is
a slow-drawing rhythm game.** The player, as Sam, produces a
single long-line drawing on the beach with a stick, hour by hour,
as the tide comes in. The line is one continuous mark; the beach
is 4x the visible screen; the tide advances at real-time-40x. The
player's "input" is a rhythmic press — one press per beat, the
line curves according to press timing. Various sea creatures
respond to the shape of the line as it emerges.

The drawing is what remains of the summer. The endings — three,
per player intent — depend on the shape of the line.

### Ending · one line

Sam signs the drawing with a stick. The signature is Sam's initial.
The line and the initial fade. The game prints one line:

    You have finished ESTUARY 3.

And returns to the cabin's slowstock library, with the next
slowstick (or two) unlocked.

## The slowstock library

The cabin's shelf holds ~30 sticks. Only a handful start unlocked.
Finishing a stick unlocks 1–2 more, following a fanout graph
authored per `library/unlock_graph.json`.

Starter set (unlocked from the beginning):
- **Estuary 3** (this game)

Wave 2 unlocks (available after finishing Estuary 3):
- **Estuary 2** (Oneironautics, 2002) · the simpler predecessor.
  Straight top-down soft-sim, no SCUMM section, no genre pivots.
  ~4 hours. Reviewed as "the calm one."
- **Pirate Summer** (Oneironautics, 2002) · a slowstick from the
  same team, unrelated to Estuary. A summer at a coastal Oregon
  camp with a pirate theme. ~6 hours. Wave 2's fun option.

Wave 3 unlocks (available after finishing Estuary 2 OR Pirate
Summer):
- **Mrs. Wu's Garden** (Oneironautics, 2003) · a slower plant-sim
  Oneironautics released the same October as Estuary 3. Sold
  ~8,000 units. In-fiction, a Rocha side-project.
- **Kwik Stop Manager** (RANCH, 2002) · the *competitor* stick
  Oneironautics's failed 2003 attempt was chasing. It is on the
  cabin shelf because Olaf bought a copy of it in 2002 to see
  what the buzz was about. Reads, in the Vol 7 present, as the
  first mainstream success in the manager-game subgenre.
- **Estuary 1** (Oneironautics, 2001) · the original. Rougher,
  shorter (~2 hours), a school-library curio. Reveals what Rocha
  was iterating on.

Wave 4 unlocks (available after finishing 3 sticks total):
- **Estuary 4** (Oneironautics, 2005) · the studio's course-
  correct after Estuary 3's cult reception. Bigger budget, more
  species, a proper narrative campaign. ~14 hours.
- **Sam's Summer Shifts** (RANCH, 2003) · the sequel to Kwik
  Stop Manager. Set at a different convenience store the summer
  after the events of KSM. The in-fiction "official" Sam.
- **The Tideline** (Oneironautics, 2004) · Rocha's first solo
  credit. A 2-hour meditation piece.

Wave 5 unlocks (any 5 sticks total):
- **Tideline Survey** (Oneironautics, 2048) · Brandon's Estuary
  7 template, commercialized. Listed on the shelf because Tem
  buys a copy in Vol 7 present and adds it. Only playable if
  the player is at Vol 7 Chapter 22 or later.

The shelf's other 15+ entries are visible-but-not-playable
Wonderswan-and-N-Gage-era detritus: reference stubs, labels only.
Some carry lore-hint blurbs.

## File layout

```
godot/resources/games/vol7/
  library/
    unlock_graph.json           # which stick unlocks which
    shelf_layout.json           # visual position of each cartridge
    stubs/                      # non-playable label-only entries
      *.json                    # 15+ short manifests
  estuary_3/
    manifest.json               # already scaffolded
    act1_kwik_stop.json         # already scaffolded, needs expansion
    act2_estuary.json           # already scaffolded
    act3_town.json              # NEW · Act 3 script
    act4_fifth_season.json      # NEW · Act 4 script
    ending.json                 # already scaffolded
  estuary_2/  · manifest + acts (deferred)
  pirate_summer/  · manifest + acts (deferred)
  ...
godot/scenes/games/estuary_3/
  Estuary3Host.gd               # single scene · switches between acts
  KwikStopRoom.gd               # act 1 room controller
  EstuaryPlanner.gd             # act 2 map controller
  TownWalkabout.gd              # act 3 hub + locations
  FifthSeasonBeach.gd           # act 4 rhythm-drawing
  Estuary3Ending.gd             # ending screen
godot/scenes/games/slowstock/
  SlowstockShelf.gd             # the cabin shelf UI
  SlowstockManifest.gd          # generic loader for any stick
```

## Development order

1. **~~Commit 1 (done)~~.** Design doc + Estuary 3 manifest + Act
   1 + Act 2 + ending JSON (short-scope). Committed as a374b64.
2. **Commit 2 (this session).** Revised design doc (this file) +
   slowstock library structure + `unlock_graph.json` +
   `shelf_layout.json` + Wave 2/3 stub manifests (Estuary 2,
   Pirate Summer, Mrs. Wu's Garden, Kwik Stop Manager, Estuary 1)
   + shelf/library README.
3. **Commit 3.** Expanded Act 1 (twelve-night structure, per-
   night customer arcs, phone/radio rotations, the 2 AM customer's
   arc). This is the "Act 1 is a full 2-hour game" pass.
4. **Commit 4.** Act 3 town-walkabout JSON.
5. **Commit 5.** Act 4 fifth-season rhythm-drawing JSON.
6. **Commit 6+.** Godot scripts: SlowstockShelf → Estuary3Host →
   KwikStopRoom → boot the first playable slice.

Ship each commit playable-or-authored in isolation.
