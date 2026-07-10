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

## Sprite techniques · one visual language per act

The four acts already have distinct playstyles, and the sprite
system commits to distinct visual languages to match. Nothing
about the loader is act-specific — the same `SlowstockSprite.gd`
reads all four — but the authoring conventions per act are.

### Act 1 · THE SHIFT · hand-authored SCUMM-era

- **Room background** · single 640×480 palette-indexed image per
  lighting state (normal / late-shift / night-12-still). Hand
  authored is worth it here; the counter is where the whole
  act lives.
- **Character sprites** · 32×48, palette-indexed, walk cycle +
  one idle + one action pose per customer. Placeholder JSONs
  authored per shape; final art expected as hand-drawn PNG
  overrides at the same dimensions.
- **Portraits** · 96×96 for dialogue close-ups on the six
  recurring customers.
- **Style reference** · *Day of the Tentacle*, *Sam & Max Hit
  the Road*. Chunky, high-contrast, warm palette.

### Act 2 · THE ESTUARY · procedural + tiny palette-indexed icons

- **Map background** · generated at runtime · value-noise
  elevation + hand-authored color ramp (mudflat / marsh /
  deepwater channel). Same technique as
  `godot/tools/landscape_sim/estuary_one.py`.
- **Species icons** · 8×8 to 12×12, palette-indexed JSON,
  deliberately abstract. Heron a tall slate blob with a lemon
  beak; otter a horizontal brown line; coho a red-orange dash
  with an eye pixel. Rendered at 4× scale (32×32 to 48×48) in
  the species-boost panel.
- **UI** · 1990s soft-sim chrome — thin bevels, olive/grey
  palette. *Sim City 2000*, *Sim Earth*-adjacent.

### Act 3 · THE TOWN · vector-style hero images

- **One hero image per location** · nine 640×360 letterboxed
  images. Flat-color line art. Six-color palette per image.
  Chunky lines. Everything readable at a glance.
- **No character sprites on-screen.** Act 3 is text-forward;
  the location image is the frame, dialogue is the content.
- **Authoring** · procedural SVG → raster gives clean line art
  quickly and can be hand-overridden per location. The bookstore
  interior and the tide gate are the two most likely to want a
  hand pass.
- **Style reference** · *Kentucky Route Zero*'s static
  compositions but simpler. Early 2000s indie flash-adventure.

### Act 4 · THE FIFTH SEASON · canvas-native procedural

- **Beach** · procedural. Sand-grain value-noise layer; waterline
  a single pixel row that advances up-canvas per the authored
  `tide_advance_curve`; tide pools authored ellipses in the
  wet-sand layer. All code.
- **The line** · real-time stroke buffer, a persistent `Image2D`
  the game paints into as the player presses.
- **Sea creatures** · 6×6 to 10×10 single-color silhouettes.
  Heron black-grey; crab red-blue; otter brown; fry white
  flicker. These are the smallest sprites in the game and the
  most abstract.
- **UI** · almost none. The rhythm cue is a single blinking
  pixel at Sam's stick position.
- **Style reference** · the act should look like nothing else
  in the game. The player is inside a canvas the game is
  helping them fill.

### Common infrastructure

- `godot/scenes/games/estuary_3/SlowstockSprite.gd` · palette-
  indexed JSON loader. `{palette, w, h, data, origin?, hotspots?}`
  → `Image` → `ImageTexture`.
- Sprites live under `godot/resources/games/vol7/estuary_3/sprites/act{n}/`.
- **PNG escape hatch** · a `.png` at the same path with the
  same stem overrides the JSON. Loader tries PNG first, falls
  back to JSON. No code change to swap.

Full schema, palette rules, and authoring guide in
`godot/resources/games/vol7/estuary_3/sprites/README.md`.

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

---

## Manager Mode · the failed 2003 Kwik Stop project, revealed

### Premise

In-fiction: the Kwik Stop half of Estuary 3 was a failed
"Sam's Summer Shifts" competitor. Ines Rocha welded it onto
the front of the estuary sim over a Labor Day weekend, dropping
the manager-sim mechanics in favor of a scripted twelve-night
narrative arc. But she didn't delete the code — she just hid
it behind a flag.

Out-of-fiction: Manager Mode is an optional depth layer that
unlocks after the player finishes Estuary 3 at least once
(`GauntletState.state.slowsticks_finished` contains
`"estuary_3"`). On the shelf, a small **MANAGER MODE** toggle
appears above the BOOT button when Estuary 3 is selected. Toggle
on before starting the run.

### What Manager Mode changes

**Act 1 · The Shift** gains real management-sim depth:

- **Opening till** · $200 in cash at the start of each shift.
- **Inventory** · three cooler shelves (top: sodas, middle:
  energy drinks, bottom: OJ + milk). Each shelf has 12 stock at
  night 1. Depletes as customers buy. Restock actions (from the
  existing cooler sub-menu · currently authored, not yet UI-
  exposed) refill by 4 per action.
- **Ring-up mechanic** · when a customer arrives, their want
  list is displayed. Click the cooler → pick the requested
  items → walk to the register → click OPERATE. Each item rings
  at its authored price. Miss the item (not in stock, or wrong
  item) and you lose the sale.
- **Customer patience** · each customer has a patience timer
  (12-40 seconds depending on type). Miss it and they walk out.
  A walkout is not a fail state · it's a data point.
- **Tip jar** · fulfilling an order without missing the patience
  window adds 20-50¢. Cumulative across the shift.
- **Nightly summary** · real totals: cash rung, tips, walkouts,
  inventory shortages. Fed into the register tape that Act 2
  reads.

**Act 2 · The Estuary** reads the manager-mode register tape:

- Nights with high walkouts (>= 3) tint the Kwik Stop marker
  yellow on the map — the store is stressed. Species-boost
  choices in stressed seasons cost 1 extra effort.
- Nights with high tips (>= $8 total) tint the marker green —
  the store is confident. The player gets +1 species-boost slot
  per season (3 instead of 2).
- Cash flow ends up as the "kwik stop's cash drawer" numbers in
  the season-end narration (currently authored as fixed
  strings: "44% more energy drinks in July than in June" · in
  Manager Mode this becomes the actual delta from the player's
  run).

**Act 4 · The Fifth Season** stays mechanically the same, but
the ending narration references the manager-mode summary if it
was run.

### The Manager-Mode-only endings (three total)

Manager Mode unlocks up to three additional final-choice options
alongside the three canonical ones. Each has its own unlock
condition, each writes a distinct `estuary_3_ending` canon_var,
and each carries its own lore token to the scrapbook:

> **Buy out Jules.**   —   `total_rung + total_tips ≥ $4,200`

Sam takes over the Kwik Stop from Jules. Five-year time-jump
epilogue · the store is still there, Sam is behind the counter
with a name-tag that reads MANAGER instead of CLERK.

> **The clean ledger.**   —   `0 walkouts across all 12 nights`

A quiet-mastery ending. The summer where Sam let no one down,
at some cost Sam does not admit to Jules. The wren is heard
later.

> **Close the store.  Walk out.**   —   `≥3 walkouts on 3+ consecutive nights`

Not a bad ending · a legible one. Sam ends the shift at 3:47 AM,
writes Jules a note, walks to the estuary boardwalk, comes back
the next night. The redemption is honest.

Each ending is on the same footing as the three canonical ones ·
none is "the right one." Together they turn Manager Mode from
a scoreboard into a moral shape-recognizer.

### Shift modifiers · seven weather / event conditions

Each Manager Mode night 1-11 (night 12 is canonical) rolls a
seeded modifier from:

> `clear · rain · county_fair · shipment_delay · full_moon ·
> sheriff_check · counterfeit_bill`

Mechanical effects · rain ×1.5 patience, county_fair ×0.75
patience, full_moon ×2 tip, shipment_delay opens cooler at
8-8-8. Rest are flavor with narrative payoff.

The seed lives on `_run_state.run_seed` and is set at
`start_new_run()`. Two identical runs of the same seed roll the
same summer · the door for structured replay.

### Rare guest customers · five in the pool

30% chance per non-rain night (night 12 excluded). One guest
per night, walks in at rolled turn 4-11:

> `the_regional_manager · the_high_schoolers · the_couple_lost ·
> the_biker · the_church_lady`

Each carries a distinct order/price/tip/patience. Clean ring-up
grants a lore token. Missing them still earns "guest expected /
missed" in the shift summary. Meeting all five across a run
grants a compound token.

### Scrapbook · 20 catalog entries

`resources/games/vol7/estuary_3/manager_scrapbook.json` catalogs
the twenty Manager-Mode-only lore tokens in five tiers:

  · **guests (5)** — met each rare visitor once
  · **modifiers (6)** — survived each unusual shift condition
  · **nights (3)** — hit a per-night threshold (clean night,
    $100 rung, $5 tips)
  · **summers (2)** — accumulated across a whole run (three or
    all-five guests met; five modifiers survived)
  · **endings (3)** — reached one of the Manager-only endings

A future scrapbook UI enumerates this file and cross-references
`GauntletState.state.lore_tokens_revealed` to distinguish
discovered entries from undiscovered ones. Undiscovered entries
render as silhouettes so the shape of what's not-yet-found is
part of the fiction.

### Save state changes

Add these fields to `Estuary3Host._run_state`:

```
manager_mode:            bool     · true when the toggle is on
manager_cash_by_night:   Array    · [ {night: 1, opening: 200,
                                       rung: X, tips: Y, walkouts: Z}, ... ]
manager_inventory:       Dictionary · shelf key → int stock
manager_night_events:    Array    · [ {night, modifier, guest, guest_served}, ... ]
run_seed:                int      · RNG seed for per-night modifier + guest rolls
```

All persist to `user://estuary_3.save.json` alongside the
existing fields. Manager Mode lore tokens flow through
`lore_tokens_pending[]` and land in `GauntletState.state.
lore_tokens_revealed` via the standard finish path.

### Shelf toggle

`SlowstockShelf` gets a per-cartridge toggle strip on cards
where the stick is FINISHED. For Estuary 3 the toggle reads
**"MANAGER MODE"**. Clicking toggles a state on `_run_state`
that survives the boot into Estuary3Host.

### Development order

1. **Commit N (this)** · design doc + save-state fields +
   shelf toggle UI. No engine mechanics yet.
2. **Commit N+1** · inventory + cash-flow engine in
   KwikStopRoom. Ring-up mechanic. Patience timers.
   Nightly summary.
3. **Commit N+2** · customer want-lists · specific item
   requirements per customer type. Satisfaction / walkout.
4. **Commit N+3** · Act 2 marker tinting + species-boost slot
   modifier + season-end narration rendering from real
   register tape.
5. **Commit N+4** · fourth ending · "buy out Jules" ·
   epilogue authoring · $4,200 threshold check.
6. **Commit N+5** · playtest + tuning.

Ship each commit with the mechanic testable in isolation and
Manager Mode still-optional throughout.
