# IMPROVEMENT ROADMAP · recommended next work

**Updated 2026-07-22.** The living plan for continual improvement
across every pillar. Priorities reflect the user's standing verdicts:
**graphics and presentation are always the sore points; the visual
novel needs the most work.** Update this doc when an item ships or a
blocking decision lands; future sessions should read it alongside
CLAUDE.md's playbook list.

## North star

Every pillar reads as a finished, art-directed work: the VN as a
cinematic literary book, the slowsticks as "modern games through an
alt-reality prism" at a minimum early-90s 256-color SVGA bar
(Sierra/LucasArts), and all departments delivering in sync (the
producer discipline).

---

## THE DRAFTING PROGRAM (standing · 2026-08-03 · read first)

The user's verdict on the whole 2026-08 wave: **"first pass of all
the new stuff, it's still very primitive… It all reads like first
draft. Keep drafting into the dozens and dozens."** So: no area is
"done." Every area carries a draft number and a next-pass target
list. Sessions pick an area, run ONE more pass against the model
chapters (diner / kwik stop / cathedral / henderson — the spaces
with many sessions of iteration in them), record what the pass
after that should do, and repeat. Report "draft N shipped," never
"complete."

Current ledger (draft counts are honest, not aspirational):

| Area | Draft | Next-pass targets |
|---|---|---|
| Tail-wave locales (~40, 2026-08-03) | 2 (22 interiors D2-seeded) | per-locale wear PERSONALITY (whose feet, whose spills — the generic pass is scaffolding); D5 through-windows; lighting; reframe |
| Vols 1–2 migration locales | 1–2 | same as tail wave |
| Pit Stop diner / ChillWave (re-themes) | 4 (D2-D6 + strata) | Deck reframe loops (strata retuned to the model diner's vocabulary: lunch/kitchen_practical/dawn_warm) |
| Salty Tome back + alley | 4 (D2-D6 authored) | Deck reframe of three presets + six vn_shot setups; then wear deepening vs the model chapters |
| **Highway 9 (planned community)** | **3** | draft 4: Deck screenshot loops on all six framings + the five vn_shot markers |
| Cedar tower (vol7 ch22) | 3 (coverage authored) | draft 4: D2 wear pass, Deck reframe of the five presets + seven vn_shot setups |
| Graustark ruin quarter / riverfront park | 2 (skyline + mid-ground) | draft 3: Deck reframe; graustark ruin cameras still untuned; park lamp practicals in tscn |
| CP region banners + agent busts | 2 (plan SHIPPED — verified in code 2026-08-03: banners incl. county_seat, tower variants, roster + dossier busts) | banner art iteration vs the SVGA bar; authored face overrides for marquee agents |
| CP coherency + presentation (2026-08-04) | 1 (timeline→2025, Faith II dog, demons electronic, type 15px, 25 problem stamps, demon sigils, 4 BGM) | Deck check: stamp legibility at row size + clipped rows at new type scale; THE_BASEMENT threads in the electronic register; per-class {agent} stage phrasing; mission-text vagueness sweep; stamp severity tinting; more BBS 2025-era threads in the regulars' aged voices |
| Northwind Harbor playability | 2 (onboarding pass) | Deck-verify the first five minutes actually teach; then mornings 2-6 pacing |
| Slowstick manuals + packaging (NH = model) | 1 | era-voice + walkthrough sweep across ~20 sticks; box art after experiences are good (task #234) |
| VN portrait busts (de-blocking · 2026-08-04) | 2 (EPX×2 + soft finish; hide-ghosts made ephemeral) | screenshot check vs the SVGA bar; if still chunky: raise the 60x64 base canvas itself (more shading ramps, finer features); dialogue-box busts + CP roster inherit automatically |
| Scene direction · coverage rotation (2026-08-04) | 4 (rotation live; 22 locales carry decks — 86 authored setups, 151 markers repo-wide, ALL euler-form now: the 81 matrix markers were converted after draft 3 found the transpose bug. Draft 4 covered the whole 7-9-use tier incl. kwik_stop B/C and the shared missing_link_exterior/shuttle_bench deck) | Deck screenshots — every framing is math-verified to <0.5° but ZERO have been seen through a lens; taste notes ("finn B too low") drive draft 5. Next tier (5-6 uses: foxhole_bar, henderson_garage, faust_bedroom, jesse_bedroom, centro_break_room, bianca_kitchen_morning, diner_interior variants) only after a taste pass confirms the grammar reads |
| Model chapters (diner, kwik stop, cathedral, henderson) | many | the BAR — mine them for what a finished space has |

### Workstream · THE STUMP HUNT (2026-08-04)

*"The highway is a stump. It does not stretch."* — and it was: the
game's most-seen backdrop (louisiana_road, 67 instances) was 48m of
road with a painted sky panel standing 33m in front of the camera.
Nothing caught it for months, so the fix is a gate, not a patch:

**`godot/tools/audit/locale_geometry_audit.py`** runs all 99 locale
builders with bpy stubbed out, records every make_box/make_cyl, and
measures — per camera preset — how far the world extends along the
VIEW DIRECTION, plus any large thin upright slab with nothing behind
it. Two calibrations that matter: there is deliberately NO interior
depth test (a 4m kitchen is correct, and flagging it buries the real
finds), and a wall with nothing behind it is only a fault if it is
standing in for the horizon (a 22m `House_Wall` behind a porch is
architecture; a 104m slab named `Sky` is a painted backdrop).

**Status 2026-08-04 · ALL CLEAR IN MEASUREMENT — every fix awaits a
Deck rebuild to be visible.** The audit now runs all 101 builders
(mathutils.Vector stubbed; real `_props.detail` executed against the
recording geometry stub so `make_far_bands` output is measured; yaw
parser handles raw-radian rotations — that last bug produced a false
positive on riverfront_park and mis-measured every raw-radian
preset). Fixed this wave:

- **Painted horizons (3)**: louisiana_road (48m + sky wall → 1200m),
  crumpled_barn (`Sky` slab → windbreaks to 760m), parish_cemetery
  (4 sky panels → treelines to 520m).
- **Shallow exteriors (14)** via `make_far_bands` in
  `_props/detail.py` (D5 edge treatment, per-locale palette +
  profile): cabin_road Sitka ridgelines · sapo_falls gorge shoulders
  + canopy · roadside_chapel cane hedgerows · skatepark suburb
  rooflines · cedar_tower town-then-woods · school_field_evening
  evening treelines · carnival_lot hedge ring + limestone town ·
  cliffside_circus sea to a true horizon + two headlands ·
  little_switzerland conifers then blue-grey ridges to 820m ·
  bar_exterior block rooflines + water tower · grunion_beach night
  sea + dune ridges · briar_falls stone ridges · missing_link
  receding hills + the road's pole line · riverfront park NW town
  edge behind the armory (bespoke).
- **Fog retuned in all 17 scenes** — density capped at 0.0045,
  aerial perspective + sky-affect on. cabin_road was DOUBLE-stumped:
  22m of geometry inside fog dense enough (0.014) to end the world
  at ~70m regardless.

The exterior threshold is 120m — below that an outdoor space reads
as a diorama. Order of attack: the two painted-sky walls first (they
are the louisiana_road failure exactly), then the shallowest views.
`diner`, `graustark` and `riverfront` import `mathutils.Vector` and
need a richer stub before they can be measured at all.

### Workstream · SLOWSTICK PRODUCTION PASS (user-directed · 2026-08-03)

*"Visual logic, detail and sophistication."* Per-stick direction +
production audit against the PRODUCTION RULES in the slowstock
authoring playbook (first-screen test: camera, visual logic, exits,
read-size art, UI coherence, scale-to-fiction).

- **Pass 1 (shipped 2026-08-03) · Pirate Summer bones**: zone-fit
  zoom (small interiors fill the frame at up to 2.75x), the
  door_wood tile (doors rendered as WALLS — every exit invisible),
  Cabin Sturgeon redrawn 14x10 and dressed, dedicated title cover
  replacing the tally-text moment image.
- **Pass 2 (shipped 2026-08-04) · PS zones + HUD + the audit that
  finds this class of bug**:
  - `godot/tools/audit/ps_zone_audit.py` — NEW gate. Checks exits
    with no tile art, dangling exit targets/spawn keys, spawns on
    non-walkable tiles, stranded scheduled NPC positions, ragged
    grids, undeclared tiles. It found 17 real bugs on first run.
  - **The boathouse was unenterable** — its wet decking was
    non-walkable, so every tile reachable from the door was water
    or deck: you walked in and could only walk back out, with the
    1988 logbook / shortwave / chest thread sealed behind it.
  - Sam spawned INSIDE the alder-pond boathouse building and ON the
    camp-path bulletin board; caves level 2's climb-out named a
    spawn that didn't exist; east_forest_deep's grid was ragged
    (22/23/24-wide rows against a declared 22) so its right column
    was silently clipped.
  - **58 tile kinds had no art** and rendered as flat ColorRects —
    EIGHT WERE EXITS (all four camp-path cabin doors, the mess
    door, the four trailheads, the cave mouth, the forest
    back-trail). This is the general form of the invisible cabin
    door. 18 new procgen tiles authored (fence, log bench, hay
    bale, target, canoe, barrel, pinned paper, carved mark,
    console, sail, rope coil, item glint, cave mouth + the five
    cabin-dressing tiles) and every kind mapped; only deliberate
    multi-tile silhouettes (the Old Man, the watched island, the
    heron) stay flat.
  - **All four cabins rebuilt to the size their roster needs**
    (`tools/sprites/build_ps_cabins.py`): 18x10 warehouses with
    ~120 open tiles → 11x9–14x10 with 55–80, ONE REAL BUNK PER
    CAMPER (Sturgeon had 3 bunks for 5 kids), a footlocker at each
    foot, cubby / clothesline / oil lamp / rug dressing, and
    campers.json `bunk_pos` rewritten to land on the actual bunk.
  - **HUD bands**: the control hints were ~790px of text in a 400px
    top-right box, running through the BACK button and off-screen.
    Three reserved bands now (top-left where/when · top-right BACK
    only · bottom two-line hover + controls), everything clipped
    with ellipsis, dialogue panels lifted clear of the band.
- **Pass 3 (shipped 2026-08-04) · the three most-seen zones**:
  - **The mess hall's tables AND benches both mapped to
    `wood_floor`** — the room the player eats in three times a day
    rendered as an empty box with invisible furniture. Same bug
    class as the doors. `ps_zone_audit` grew **check 7**: a SOLID
    tile drawn with the same sprite as the ground it stands on is
    invisible. It immediately caught a second instance (the ghost
    ship's deckhouse drawn with the deck sprite).
  - **The camp path's four cabins + the mess hall were five flat
    rectangles of one wall tile each.** Every structure now has a
    roof course, a face with lit windows on a regular architectural
    cadence (wall·window·wall·window·SIGN·DOOR·…), and a name board
    beside its door — `tools/sprites/dress_ps_zones.py`, which
    asserts the walkability mask and every exit are byte-identical
    before/after, and is idempotent.
  - Mess hall got a serving line and hanging lamps; the campfire
    ring got the woodpile, the counselor's stump, and two lanterns
    on the approach. 8 more procgen tiles (table, bench, serving
    counter, roof, face, sign, woodpile, stump).
- **Pass 4 (shipped 2026-08-04) · silhouettes, buildings, and the
  bug the composition fix exposed**:
  - **Every prop was a full-bleed opaque 16x16 box** — a tree was a
    green BOX ("too blocky, this isn't Minecraft"). The renderer now
    lays the zone's ground tile under anything that isn't itself
    ground, the generator grew a `-1 = transparent` sentinel plus
    blob/blob_edge helpers, and 24 props were redrawn as shapes
    (canopies with gaps, rounded boulders, a lens-shaped canoe, a
    lamp that is mostly empty cell). Props now run 40-80%
    transparent with contact shadows; ground/architecture stays
    full-bleed.
  - **Buildings were "doors and windows placed in roofs."** The face
    row was picked as the FIRST row containing the door — which for
    the cabins is the row AWAY from the path, so openings landed in
    the upper band with shingles beneath them. The face is now
    always the structure's LOWEST row (the side the player walks up
    to): ridge course on top, slope course with an eave shadow, then
    the front wall carrying windows/door/sign. The eave band is what
    gives a flat top-down tile the slight-isometric depth. A door
    tile stranded in a roof row becomes a doorway recess — dark past
    the screen — instead of a hole in the shingles.
  - **CABIN BEAVER WAS UNREACHABLE.** Its door tile existed only on
    the upper row, with a tree above and solid wall below: no
    walkable tile touched it, so Tessa's cabin could never be
    entered. Found by flood-filling the hub while checking the
    composition fix. Repaired (two-tall door column, as Sturgeon and
    Osprey have) and the audit grew **check 8 · reachability**:
    every exit must stand in the reachable set of some spawn.
  - The dressing script's walkability/exit snapshot assert earned
    its keep — it caught a shared doorway-recess tile that would
    have given all four cabins Sturgeon's exit.
- **Next (draft 5)**: Deck screenshots — do the 16x16 tiles read at
  24px, and does the roof-below-face ordering read correctly in the
  top-down projection (the door faces north, so the roof mass sits
  south of it)? Then alder pond / archery range / north bluff to the
  same standard, then the sweep per stick: Estuary 3 → NH tableaux
  detail → the rest.

### Workstream · HIGHWAY 9 ACTION STAGE (user-directed)

The user: *"the highway stretch feels like a small set, it cuts
off… there will be an action scene of sorts here, it needs to be
staged like that, using still camera set-ups and camera motion."*

- **Draft 1 (shipped 2026-08-03)** — `build_highway9_2026_08()` in
  build_harmony_terrain.py: 4-lane divided highway at x=-510
  running y ±1400 (3.4× the world), median/shoulders/guardrails/
  paint, near overpass (y=+300) + far silhouette overpass (y=-800),
  two sign gantries, embankment + berm silhouettes past the world
  edge, terminal treelines, sparse traffic. Fog carries the fade.
- **Draft 2 (shipped 2026-08-03)** — build_highway9_draft2_2026_08():
  reflector posts, lane grime bands, THE SCAR (skid marks curving
  into a deformed guardrail + debris fan + glass at y=+210 — the
  road's own history mark), exit ramp + gore paint at y=-60,
  gravel rest turnout + semi stand-in at y=-330.
- **Draft 3 (shipped 2026-08-03)** — the camera_track capability
  in Background3D ({to, secs, rot_to, loop} on any preset; sine
  dolly, ping-pong, killed by manual vantage overrides), six
  highway presets (long / shoulder / overpass / scar / turnout
  stills + highway9_drive, the first MOVING background), and five
  vn_shot Marker3D setups in harmony_terrain.tscn for VnDirector
  in-scene cutting. All framings derived from build coords.
- **Draft 4+** — Deck screenshot loops: frame, re-stage, re-light
  until it reads like a location, not a set. Dozens of passes is
  the expectation, not the exception.

---

## The three gates (user-side; everything flows faster once these land)

1. **ART ROUTE** — the standing decision: hybrid (AI-painted sources +
   procedural), but no image key exists and no ArtCraft exports have
   landed. Options: (a) you drive ArtCraft/any generator and drop
   exports through `godot/tools/art/art_studio.html`; (b) drop a
   direct-API key (Flux/BFL, OpenAI images, or Gemini) at
   `godot/tools/art/.image_key` and Claude wires `scene_render.py`
   for batch generation; (c) both. **This gates the biggest visual
   wins in the whole project** (painted VN backgrounds/plates, the
   SVGA retrofit of all ~21 slowsticks, CP banners).
2. **MIXAMO SESSIONS** — `godot/HANDOFF_CHARACTER_MODELS.md` is a
   paint-by-numbers list of the 15 missing vol 6–7 character models.
   Engine side is done; each GLB dropped in upgrades a character from
   a 60×64 pixel bust to a lit 3D portrait, zero code. Lena first.
3. **DECK FEEL PASS** — one playthrough of a vol 5 chapter start-to-
   finish to tune the new presentation grammar (fade/hold/settle
   durations, typewriter pacing multipliers, portrait rise, choice
   plate look, reading-surface scrim 0.34, chapter whisper). Plus the
   standing slowstick verify list: Tideline parallax, diorama demo,
   per-studio shader modes, Spiderdrops/Long Wind/Salmonberry feel.

---

## Pillar backlogs (P0 = do next · P1 = soon · P2 = when reached)

### Visual novel (vols 5–7) — top priority

- **P0 · Character models wire-in + lighting tune** — as GLBs land
  from gate 2, tune `Portrait3D.CHARACTER_LIGHTING` per model.
  (Claude, same-day per model.)
- **P0 · Painted backgrounds/plates** (gate 1) — full-res painted VN
  art (the VN is the modern frame — NO era filter): chapter-card
  backing plates, CG art, locale PNG fallbacks for unbuilt GLB
  locales. Extend `art_studio.html`'s catalog with VN slots; hook
  plate display through the producer clock. **Constraint (2026-08-03
  verdict): VN scene BACKGROUNDS are 3D scenes — painted art is for
  cards/CGs/plates, never a scene bg.**
- **SHIPPED 2026-08-03 · Vols 1-2 → 3D migration, COMPLETE** —
  "visual novel backgrounds are 3d scenes": every vol1/vol2 bg is
  now a `3d:` preset; migration debt ZERO; the 2D plate generator
  retired. Two waves: (1) 47 placements rewired — 17 set-reuse,
  carnival_lot wired, three new multi-vantage builds
  (missing_link_exterior + shuttle_bench · briar_falls ×5 ·
  faust_apartment ×2); (2) nine more builds for the last 12 refs
  (pharmacy ×2 · grunion_beach ×2 · bar_exterior · skatepark ·
  wagner_home · school_newspaper · sapo_falls · little_switzerland
  · crumpled_barn) + parish_cemetery wired for vol2_graveyard + six
  link_* diner sub-scenes homed. USER STEP: run the TWELVE new
  builders on the Deck (single chained command in the session log)
  or the new sets render the black fallback until then.
- **SHIPPED 2026-07 · Locale coverage report** —
  `python3 godot/tools/locale_coverage.py` (run on the Deck):
  cross-references the 78 GLB-requiring camera presets against the
  `3d:` story directives and the files on disk, prints the missing
  list in build-priority order with the exact `run_cathedral.sh`
  command per locale. Born from a real boot error
  (riverboat_interior.glb unbuilt).
- **P1 · Dialogue-surface iteration** — after the Deck look: scrim
  number, and the parked taste call on any further chrome.
- **SHIPPED 2026-07 · Kinetic text** — grammar documented in the
  direction playbook; first seeds in vol5_ch0. Ongoing: seed
  sparingly at the lines that turn.
- **P2 · Speaker-biased text columns** (`DialogueBox._anchor_to` dead
  intent) · letterbox on `establish~` shots · CharLayer
  resolution-relative positions. All taste/robustness, low urgency.

### Slowsticks (the shelf)

- **P0 · DEPTH FLOOR sweep (2026-07-27 user verdict: "far too
  basic... I want depth of play")** — the authoring playbook now
  carries a six-point depth floor (three interlocking systems, ≥30
  decisions/run, visible checks, expiring scarcity, a build,
  textured failure). Audit result: roughly half the shelf is under
  it. Rebuild queue, worst-first by user impact:
  1. **SHIPPED 2026-07 · Salmonberry v2** — the week loop: 4 weeks
     per month (40 decisions), energy budget, deterministic weather
     + one-week forecast, board owed monthly, shown skill checks
     with strong/fair/rough tiers, the general store (5 gear items
     that change play), 9 one-week-only calendar events incl. a
     stakes rescue off the bar, bond decay. Deck-verify pending.
  2. **SHIPPED 2026-07 · Northwind Harbor full game** — 26
     optional kindness/errand chains (52 steps), each gated behind
     its own overheard hint; more morning than the 73 minutes
     allow; Bosun fetch at trust ≥3; horn summary + THE GOOD WEEK.
     All canon steps verbatim. Deck-verify pending.
  3. **SHIPPED 2026-07 · Estuary 4 · THE WORKING SEASON** — 13
     field weeks between the calls and the king tide: budget, crew
     morale, seeded tide windows, forecast storms with prep-or-pay,
     grant deadline, storm damage/repair; the king tide reads built
     quality per project. Deck-verify pending.
  4. **SHIPPED 2026-07 · Tideline / Spiderdrops 2 / Mrs Wu second
     systems** — Tideline: THE TIDE CLOCK (walking/recording/
     watching cost minutes; nine observations live in tide windows
     with authored gone/early ghost lines; the report reads your
     pace). SD2: airborne drops hang low near the churn (+silk,
     risk/reward) + gold thermal columns with free lift, each
     scrolling past exactly once. Mrs Wu: weather rewrites the
     evening's needs (wind = tie up TONIGHT, rain = slugs + free
     watering), the linen chest (frost sheets EARNED by spending
     drying-weather actions washing), the pumpkin boy covers a bed
     on frost night if you tended his twice. Deck-verify pending.
  5. Vignette tier, corrected and in progress:
     - **EXEMPT · Sweetgum** — the audit mislabeled it (truncated
       listing): SweetgumNight.gd (458 lines) delivers its design
       doc 1:1 — rounds, the typed palimpsest log, NOT A STATION,
       the 3 AM sounds, 06:00 QUIET, the NAMES field. Its design
       explicitly forbids expansion ("there is no third
       variation"); deliberate single-scene art objects are judged
       by their own doc, and this one passes.
     - **SHIPPED 2026-07 · Sam's Summer Shifts · THE SHIFT** — the
       "one scripted beat per week" pattern (the exact Salmonberry
       sin) fixed: every week opens at the register with a seeded
       customer queue — ring the right total from three (register
       craft feeds TILL; ≥80% right pays the drawer, <50% costs
       it), handle authored counter moments (Gus's dime, the
       out-of-county check, the unfinished mustache), Heritage
       week rings a longer line with tighter totals, the solo week
       doubles till swings, and week 6's third customer is not a
       customer. ~100 decisions per summer. Deck-verify pending.
     - **RE-AUDITED COMPLETE · Patient Mister Glass** — the deck
       is fully authored (39 rotation variants, trust/cooking/rain
       gates) and all nine ledger findings are wired to real
       variant pairs with unlock chains and three verdicts. The
       slow-detective design is implemented 1:1.
     - **RE-AUDITED COMPLETE · Riffrocker Melody Club** — twelve
       meetings × ~3 call-and-response phrases on the live 3-osc
       PD Riffrocker voice; meeting 12's open mic records YOUR
       take as the cartridge's title music forever. An instrument
       with a club around it, per its design.
     - **RE-AUDITED COMPLETE · Hane no Niwa** — 4 seasons × 9
       visits, four verbs with visible maintenance memory, a
       20-item offering economy, the letters system, fox
       expressions reading unshown upkeep. Passes on its own doc.
     THE DEPTH SWEEP IS CLOSED. Lesson captured in the authoring
     playbook: audit sticks by READING THEIR DATA, not by wc -l —
     the line-count audit mislabeled four of five in this tier.
- **SHIPPED 2026-07 · Sisters Wyrd readability triage** (user: "an
  eyesore") — focus dimming by distance from the drifter (the soup
  fix), label plates, position ring, styled choice buttons lifted
  clear of the log, log opacity/edge. Depth machinery was already
  in (task #175); re-verify feel on Deck after the readability pass.
- **SHIPPED 2026-07 · Earthman palette soften** (user: "hard on the
  eyes") — neon green/pure red/hot amber/stark white desaturated to
  sage/brick/soft amber/warm paper across all 10 scenes; ch2 rust
  glare dimmed.
- **P0 · SVGA retrofit pilot** (gate 1) — the approved direction:
  painted source → `svga_quantize` era filter → per-studio slots via
  `art_studio.html`. Pilot on Salmonberry (title + 5 endings), then
  sweep the catalog studio by studio. The old flat-vector HeroImage
  scenes remain only as fallbacks.
- **P1 · Estuary 4 thinness pass** — the last thinness-cluster stick
  still bare (art through the new pipeline + a BGM pass).
- **SHIPPED 2026-07 · Salmonberry Wave A: the town overworld (v1)**
  — walkable Salmonberry as the month interface (see the design doc).
  **SHIPPED 2026-07-28 · Wave C: THE NIGHT, PLAYED** — the March
  wave is a real-time crisis in the walkable town: 18s slack while
  the bay drains, then the flood climbs from the water up; rescues
  root you in place (progress ring) while it rises; the dock
  drowns first; the bicycle is speed; ineligibility explains
  itself in fiction; multi-rescue with good routing; same reward
  paths as the old menu (registers/codas/tokens unchanged).
  Next: Wave D (full roster/errands);
  town v2 candidates: NPC figures at their places, month-gated
  weather/light, interior beats.
- **P1 · Mrs Wu BGM sign-off** — two composition scores are written
  and awaiting your ear before render/wire.
- **P2 · Spiderdrops 2-player pass-the-stick** (the box promised it)
  · wire the 3D diorama behind Basilica (pending z-order verify) ·
  roll HeroImage-2.0/parallax/diorama to more sticks (superseded in
  part by the SVGA retrofit — decide per stick).

### Community Planned (vol 6 inset)

- **P1 · Visual upgrade, re-planned for the new art bar** — the old
  pass-10 plan (region banner vignettes + agent busts) was authored
  for flat-vector; keep its structure (Small Wood's banner tracking
  tower-brightness is a great idea) but generate banners through the
  painted pipeline (gate 1). The `VnBustPortrait` agent-roster halves
  can proceed anytime (engine-side).

### Tarot Gauntlet (vol 5 inset)

- **P2 · Painted visitor/card plates** (gate 1) — the procedural
  bust fallback works; painted marquee-visitor plates would lift the
  most-seen screens. Low urgency after the recent look-table pass.

### Audio

- Healthy (96-slot audit green, every stick scored). **P2:**
  Salmonberry per-season bed variants · VN ambient choreography as a
  producer client · a Long Wind `silk_cast`-family ambient set.

### Cross-cutting / systems

- **SHIPPED 2026-07 · Producer beats + kinetic text** — `[beat:
  still|hit|chill|lift]` directive (sting + haptic + camera breath +
  letterbox pulse in one call, VnDirector-executed, locale-parked,
  drift-safe) and the native BBCode kinetic-text grammar documented;
  first seeds in vol5_ch0 (the bell · "the walls are thin"). Next:
  seed beats across vols 5-7's emphatic reveals as chapters are
  reread.
- **P2 · Screenshot mode** — F4 already hides HUD; a deliberate
  photo mode (letterbox + pause + no cursor) is ~30 lines and serves
  the user's clean-pictures habit.
- **Discipline reminders** — lesson-capture cadence per playbook;
  emit-and-consume tokens in the same commit; gdparse + JSON sweep
  before every push; scope commits (revert normalize_bank's unrelated
  WAV touches).

---

## Recommended sequence (next five arcs)

1. **Unblock gate 1** (your single highest-leverage act: a key or a
   first ArtCraft export) → Claude pilots painted VN plates + the
   Salmonberry SVGA set in one arc, both through the same tools.
2. **First Mixamo session** — Lena + Mrs. Gable + Petra (vol 7 core).
   Claude wires lighting per model as they land.
3. **Salmonberry town overworld** (Wave A) — the flagship gameplay
   build; no external dependencies, starts on your word.
4. **Producer beats + kinetic text** — one authoring-power arc that
   makes vols 5–7 more cinematic with zero new art.
5. **Estuary 4 thinness pass + CP visual upgrade** — sweep the two
   remaining thin spots with the by-then-proven art pipeline.

Items 3 and 4 are fully Claude-side and can proceed in any gap while
gates 1–2 wait.

---

## 2026-07-28 · FULL AUDIT + FIX WAVE (shipped same day)

Four pillar audits (VN, slowsticks, CP, gauntlet) → 48 ranked
findings → five fix waves, all landed. Highlights: the vol 7
index no longer hard-ends the book and its 19-scene expanded
ch6/ch7 rewrite is live · VN resume rebuilds the full scene state
and saves land on the line being read · the in-game menu closes on
ESC and autosaves on exit · gauntlet fullscreen no longer feeds
clicks to invisible controls, the authored inertia_max /
visitors_claimed_max difficulty knobs are honored at last, help
and goal lines are arcana-correct, DRIFT/UPKEEP auto-advance ·
CP enforces rest, explains every ineligibility, and fits 1280
with four regions · seven slowstick resume exploits closed ·
23 procedural floor plates under the gauntlet board (default ON
at 0.42 — pure material, nothing to misalign). Deck-verify the
lot on the next session.
