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
