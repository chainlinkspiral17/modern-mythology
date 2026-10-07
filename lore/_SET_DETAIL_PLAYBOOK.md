# SET DETAIL PLAYBOOK — how a draft-1 set becomes a location

Created 2026-08-03, the same day as THE DRAFTING PROGRAM (see
CLAUDE.md + `lore/_IMPROVEMENT_ROADMAP.md`). This is the METHOD for
the "dozens and dozens" of passes: what each detail pass actually
adds, in what order, within the honest constraints (no textures —
vertex color + geometry + real lights only).

## Why sets read as primitive

A draft-1 build is: flat single-color walls, a flat single-color
floor, template furniture, and prose props floating in clean space.
Real rooms read differently because every surface carries HISTORY
(wear), every object carries INFRASTRUCTURE (cords, outlets,
fasteners), and every cluster carries USE (asymmetry, mid-task
states). The model chapters (diner, kwik stop, cathedral,
henderson) got there by accumulating exactly these layers.

## The five detail passes (run in order, one per visit)

### D2 · SURFACE BREAKUP — no surface is one color
- Walls: wainscot line or color band; slightly darker band at the
  top 30 cm (ceiling shadow gather); per-wall ±0.02 tint variance.
- Floors: traffic-path darkening (a slightly darker ribbon from
  door to counter/table — where feet actually go), 2-3 stains near
  work zones, thresholds at doorways.
- Ceilings: slightly darker than walls, never the same tone.
- Big furniture: top surfaces lighter (dust/light), kick zones
  darker (scuff), edges a contrasting worn strip.
- Tool: `_props/detail.py` (`make_traffic_wear`, `make_floor_stain`,
  `make_scuff_band`, `make_wall_tint_band`).

### D3 · INFRASTRUCTURE — rooms are plugged in
- Outlets + switch plates at real heights (outlet 0.30, switch 1.20,
  by the door).
- Cords: everything electric gets a cord to a wall (lamp → outlet,
  register → floor, neon → junction). Sagging cord = two-segment run.
- Fasteners/joins where two materials meet: door hinges, corner
  guards, counter edge strips.
- HVAC: registers low on walls in old buildings, ceiling vents in
  commercial; a thermostat.
- Tool: `make_wall_outlet`, `make_light_switch`, `make_cord_run`,
  `make_thermostat`.

### D4 · USE STATES — mid-task, not showroom
- Every work surface gets one task IN PROGRESS (a half-wiped
  counter with the rag still on it; an open ledger with a pen).
- Asymmetric multiples: chairs at angles ≠ 90°, one stack leaning,
  papers fanned not squared. (Rotation isn't available from
  make_box — fake it with offset stacking and off-grid anchors.)
- Containers open: one drawer ajar, one cabinet door open, a lid off.
- The trash tells the truth: crumples near the bin, not in it.

### D5 · DEPTH BANDS + EDGES — the set never ends at the walls
- Interiors: something THROUGH every window (a wall, a car shape, a
  tree band, a lit window across the street) at believable distance.
- Exteriors: three bands — playable detail (0-30 m), silhouette
  band (30-150 m: massed simple shapes), horizon band (150 m+:
  berms/treelines/rooflines + fog). The Highway 9 rule: geometry
  runs PAST the frame in every direction a camera looks.
- No raw world edge may be visible from any vn_shot or preset
  camera. Check every camera, not just the default.

### D6 · COVERAGE + LIGHT (the cinematography pass)
- Per the lighting playbook: practicals tied to the fixtures the
  detail passes added (that task lamp now casts).
- vn_shot still setups for every place a scene lingers; camera
  motion where action moves (see the Highway 9 workstream).
- Deck screenshots → reframe. This pass repeats forever.

## Rules

1. **One pass per visit.** Don't smear D2-D6 thin in one session;
   run one deep and record the next.
2. **Helpers over one-offs.** Any detail used twice goes into
   `_props/detail.py` so it costs nothing the third time.
3. **The wear must agree with the fiction.** The diner's wear is
   30 years of boots; Cale's shop is tidy-worn; NexCorp spaces are
   unnervingly wearless (that IS their detail).
4. **Budget**: a detail pass should roughly double a build's
   mesh-object count, not 10x it. Silhouette bands are cheap quads,
   not modeled buildings.
5. Update the DRAFTING PROGRAM ledger row after every pass.

## Recent lessons

### 2026-10-07 · stock reads by PACKAGING; a kit defect is fixed in the kit

- Solid saturated blocks on a shelf read as toys at any count. A shelf
  reads by its packaging grammar — a bag's band and crimp, a tray of
  bars, a can's label, a bottle's neck, a box's panel — in brand tints
  with one band colour, faced in rows of one product per section the
  way stores face them. `_props/merch.py` holds it; use `stock_gondola`
  for any aisle and `merch_section` for any single shelf.
- The same defect lived in a shared kit AND a vendored copy (the Kwik
  Stop's). Fix it in the kit, then grep the builders for the copy —
  `SNACK_TINTS[` finds every block-stocking loop left.
- Fixing a support can unmask a FLOAT: the aisle's fins had been the
  "support" under a produce stand's tiers and scale. When an old
  fixture changes shape, re-run support_audit on its neighbours.
- Thousands of packages are thousands of draw calls: join each
  fixture's stock into one mesh at export (`join_stock`) and keep the
  packages sharp-edged.
- A STORE IS WALKED. Lay fixtures out by the lanes between them, not
  by their footprints: ≥ 0.90 m between any two fixtures that are not one
  piece (1.1-1.4 m between gondolas reads as a real aisle), an endcap ON
  its aisle's end or in open floor with a metre round it, never a
  diagonal half-metre off a corner. `walkway_audit.py` measures it; the
  user saw "shelves blocking shelves" the first time the stock read as
  real — dense, legible stock exposes a cramped plan that blocks hid.

### 2026-10-03 · a home is ROOMS, not a box with furniture in it (the Roberts house)

- The Deck, on the Lovers' domicile after a bones pass AND a proof-of-
  life pass: "still looking wrong … I want it to feel cozy, brimming
  with detail. Photos, and collections and comfy furniture and book
  shelves and lived in spaces, not antiseptic and sterile … a foyer, a
  living room, a dining room/kitchen, I want to have character." Two
  passes of props on an 8×6 box were still a box. Character comes from
  PLAN first: interior walls that make a foyer (walls either side of
  the front door, a cased opening north), a living room with its own
  paint, a dining room with a wainscot — and THEN each room's furniture
  and its collections. build_house_rooms_2026_10 is the model.
- What each room needs to read as itself: FOYER — the mat and the boots,
  the hall table, a bench with coats on hooks, a mirror, a ceiling
  fixture. LIVING — a window over the sofa, the sofa with a quilt and
  a throw pillow, an armchair with a throw, a coffee table with a book
  stack and a mug and the reading glasses, a rug with a border, a
  BOOKCASE with books of fourteen thicknesses and a collection among
  them (shells, sea glass, pinecones, a framed photo), a gallery wall
  of five mismatched frames, a floor lamp, a side table with a lamp.
  DINING — a table for four with chairs that do not match, a pendant
  over it, a rug, a HUTCH with the plates standing and the preserves in
  three colours, a sideboard under the window with standing frames and
  the garden's flowers in a jar and a bowl of fruit, cookbooks on a
  shelf, a wainscot and a chair rail. Every one of these is a box, a
  cylinder or a lathe; `_wall_frame`, `_book_row`, `_bookcase` make
  them cheap.
- Each fixture gets its practical in the tscn (the floor lamp, the side
  lamp, the pendant, the foyer's fixture) — a lamp with no light is a
  prop, a lamp with a light is a room.
- A sink is a basin CUT INTO the counter: four strips of counter round
  a hole, a steel floor and four walls 18 cm down, the base cabinet
  stopping under the floor. A white block standing on the counter with
  the faucet on its room side read as "sink on backwards".
- The same pass on three apartments the same day (Montreal, New
  Orleans, Elicia's): read the chapter for its NOUNS first, then build
  every one of them — a "cluttered archive of selves" is posters AND
  torn pages AND ziggurats on every surface; a "dumpster fire" is
  empties AND the pizza box AND clothes on the floor AND the duffel; a
  "ruined command center" is dead monitors AND the story-map
  whiteboard AND the prints she never hung. Twenty to thirty objects a
  room, each named in the prose or following from it.
- `make_tube` polylines are boxed WHOLE by the overlap audit: a cable
  that runs along a table and drops to the floor "hits" the stretcher
  under the table. Split it where it leaves the table.
- The audits catch what the eye forgives at montage size: frames
  standing 3–4 cm off their shelf, a switch floating off a thinner
  interior wall, a faucet handle not reaching its pipe, a soap bottle
  left over the new hole. Run support_audit after every density pass.

### 2026-10-02 · the Roberts kitchen · bones before props, and the lane of the camera

- The Deck: "the lovers domicile needs to feel domestic and lived in,
  proof of life, not a sterile empty thing." The D4 pass went in first
  (Philip under the sink mid-repair, two of everything drying, the
  returned casserole, breakfast interrupted, boots and gloves and the
  trowel at the door, the basil on the sill, her loom, the laundry, the
  crumple by the bin, the lane door → island → sink, TWO mug rings) —
  and the room still read as a cream box. The BONES were missing: a
  sink, a stove and a fridge standing apart on bare wall, no counters
  between them, no uppers, no backsplash, no window over the sink. A
  kitchen is its RUNS. Props cannot carry a room whose architecture
  says nobody built it. Run D3-bones before D4 on any locale that
  was placed from a template.
- WALL FACE ≠ WALL LINE. make_wall builds 20 cm thick on the line; the
  first backsplash and window sat inside the wall, invisible. Anchor
  wall-mounted things at ROOM_D − 0.10 (and check the locale's own
  earlier fixes: this file had learned it twice already, per window).
- A locale's establishing camera is PART of its set dressing. The old
  vantage (SE corner, across the island) put every bit of life out of
  frame; from inside the front door looking north, the chapter's
  geography — island, sink, window, loom — is one wide. Re-vantage
  BEFORE judging a props pass, or you will add props the camera never
  sees.
- The doorway (D5): the front door was a 2.2 m hole onto the void —
  `shot_insert_door` stared at nothing. The prose had the whole
  exterior: the screen door (a lattice of fine bars — it casts the
  grid of light), the porch under its eave, three steps, the gravel
  drive, the wagon at the curb, trees past it. The gates then taught
  two rules: a solid door LEAF anywhere near a doorway must have both
  sides of its swing clear (hall table, boots and even a window frame
  count), and a locale's background colour is the sky behind every
  window and open door — a dark interior brown reads as night outside.
- `TripPaintTest --marker <name>` shoots from a [shot:] marker through
  the real stack: judge inserts there, not from the sheet alone.
- Elicia's bungalow: the dresser hugged the bed's foot with its drawers
  14 cm from the mid-wall ("the wardrobe/drawer at the foot of the bed
  can't open"). Every container must have its open side on open floor;
  check this with the room's walls, not the furniture alone.

### 2026-08-19 · WEAR HAS AN AGE — the cabin's two inhabitants

- First full wear-personality pass (cabin_interior, the "land of
  milk and honey" heart). The finding that generalizes: **wear is
  not one layer, it is a TIMELINE, and the difference between two
  ages of wear is itself story.** Olaf lived here from '79: his
  wear is decades — the door→table→kitchen→stove path cut dark
  and wide, the Sunday carving spot scraped PALE by chair legs
  with a shaving crescent no broom ever fully got, the kettle's
  ring on the stove top, the flame-mark iron's scorch where it
  was always set down, the latch-hand patch, three ladder rungs
  worn at the grab line, the reader's un-faded rectangle on a
  shelf otherwise darkened since '46. Tem's vigil is WEEKS: a
  faint NARROW path to the chair beside the daybed and one mug
  ring. New wear is narrower and closer to the floor's own tone;
  old wear is wide, dark, or scraped pale. A visitor should be
  able to date the household from the floor alone.
- **The Lovers wear IN PAIRS** (pass 8, closing the arcana set):
  two knee-dents close together on the front kneeler, a narrow
  aisle walked slow and in step, rice ground into the threshold
  seams that no broom ever beats the next wedding to, the bell
  rope hand-dark at one height (rung once after each vow), the
  statue's foot rubbed bright by thumbs, and TWO wax colors at
  the altar's candle stations — two households' candles, burned
  down together. The eight-personality wear vocabulary is now:
  age (decades/weeks on one floor), width (family/alone), the
  material inversions (wood darkens, dust clears, wax dulls),
  both-ages-one-spot, the absence, appetite, the architect, and
  the pair. New locales should pick their personality FIRST and
  let it choose the marks.
- **Appetite vs. measure, and the architect's wear** (passes 6-7):
  Daigle's is the anti-Mixing-Glass — RINGS ON RINGS on the bar
  top, cigarette scallops, the dance patch worn to pale wood with
  a dark watchers' rim, and the belly lane running the bar's WHOLE
  length because at the Devil's everybody bellies up. The casino
  inverted the question a different way: its carpet lanes are the
  ARCHITECT'S wear — the house routes you, door → wheel → slots →
  cage, planned before any foot took it — with the users' tells on
  top (the rail bright only at the wheel end; the lucky third
  slot's floor worn double, and it is never lucky; the cage sill
  pale mid-span where forty years of chips slide under the bars).
  Ask WHO designed the traffic before asking whose feet took it.
- **Sometimes the absence is the wear** (Mixing Glass, pass 5):
  a bar kept in Temperance's measure has NO spill rings — copper
  that polishes bright in the nightly wipe-arcs, pale reach-wear
  under only the five working bottles, dust intact on the top
  shelf — and exactly ONE water-glass ring at the south end of
  the west arm, hers, because the one glass she doesn't measure
  is her own. Wear passes should ask what the keeper REFUSES to
  let happen, then break the refusal exactly once, meaningfully.
- **Waxed floors dull, they don't darken** (asylum ward, wear
  pass 4): institutional linoleum's traffic lane reads PALER and
  flatter than the sheen around it — the third material inversion
  (wood darkens underfoot, dust clears pale, wax dulls pale). The
  ward also carried the game's deepest single lane — nurses walk
  miles, station to every bay — with the gurney's two rubber
  wheel-lines over it and one swerve where it always misses the
  radiator. Vigil wear is OBJECT-anchored: four chair-foot marks
  that stay when the chair is carried back each morning, the
  hand patch on the bed rail near the head.
- **A renovation floor wears BACKWARDS** (ember warehouse D2):
  concrete dust settles everywhere, so the traffic lanes are the
  PALE-CLEAN part — boots clear the dust where the work moves,
  and the corners nobody works go gray. Plus the vocabulary that
  came with it: sawdust halo around the lumber, mortar dust
  around the brick pallet, the roll gate's rain band with two
  finger stains reaching in, damp-rise on old brick bases, and
  the GHOST WALL — a pale stripe across the slab where a
  demolished partition stood for decades. Ask what the surface
  was DOING before the story arrived.
- The triptych completed same day (Lena's three-years-alone, the
  Millers' family kitchen): a family walks WIDE where one person
  walks narrow; crowding too new to mark a floor shows in OBJECTS
  (a flattened cushion, a folded floor bed); and the strongest
  single wear mark so far is Mike's chair at the Miller table —
  his years worn PALE, and inside that patch one small NEW dark
  crescent, because "since June she has been sitting in Mike's
  chair." Both ages, one spot, no words. ALSO: read the builder's
  own docstrings before placing — the first draft of the chair
  stains used tx=0.0 against a table at tx=0.5 and missed every
  chair by half a meter.
- Vocabulary that carried the pass: worn-PALE for chair-scrape
  (wear lightens wood), worn-DARK for foot traffic (grime
  darkens), scorch rings as habit (one kettle ring from decades,
  one mug ring from weeks), and the negative-space wear of an
  object that never moves (the reader's shadow).
- Mechanical: the detail helpers import at FUNCTION scope in this
  file — a module-scope replace landed a column-0 import inside
  another function's body and broke the build until parsed. Match
  the file's import style before inserting.



### 2026-08-12 · HERO PROPS: build the thing the prose points at

- **`shot_marker_audit.py --props` measures the gap nothing else
  could see**: a chapter cues `[shot:insert x]`, and no builder in
  that locale emits anything named like `x`. 242 such cues across
  191 locale/object pairs on the first run.
- **Not every one is an art gap** — read the prose before modeling.
  vol7's `insert tide_pool` fires on cabin_road because Finn is
  playing a GAME with a tide pool in it; "douglas" and "coach_dale"
  are people; "prints" and "smear" are marks, not objects. The
  director's substitute/hold-wide fallback is the right answer for
  those. Model the ones that belong in the SET.
- **Built this pass, all from what the prose actually says:**
  Olaf's two carved bowls (21 cues — the volume's central image,
  same grain, same spiral, the flame-mark on the base); the
  Henderson pot roast (a MODEL CHAPTER — the dutch oven with its
  lid OFF, leaning, because that is what "she made it tonight"
  looks like); Lena's easel and half-finished board (she is the
  volume's artist and her apartment held none of her work — paint
  tubes stacked on the floor where a working painter keeps them,
  not in a tidy box); the eviction notice taped to Elicia's door
  (the detail that carries it is the SECOND strip of tape and the
  pale ghost where the lease renewal used to hang).
- **The test for a hero prop: name the one detail that proves the
  sentence.** Lid off, not lid on. Two strips of tape, not one.
  Paint on the floor, not in a box. Without that detail it is set
  dressing; with it, it is the shot the chapter asked for.



### 2026-08-03 · founding · first D2+D3 passes
Applied to pit_stop_interior + chillwave_interior (the freshest
re-themes) as proof of method, alongside Highway 9 draft 2 (action
dressing). What worked / broke goes here after Deck review.

### TEMPLATE for next session
### YYYY-MM-DD · <area> · <pass run>
- What was added, what read well on Deck, what to do differently.
