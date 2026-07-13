# SCENE STANDARD ROADMAP · bringing every locale up to bar

The goal (user, 2026-07-12): "bring all the scenes up to standard —
it may be a long process." This is the tracking doc. 60 distinct 3D
locales are referenced across 380 background instances in vols 5–7.
As of this doc, **12 are at standard, 48 remain.**

## What "standard" means (the checklist)

A locale is AT STANDARD when every box below is checked. Verify with
the headless tools, not by eye: `godot/tools/blender/survey.py`
(geometry AABBs, occupancy maps) + scratchpad `check_shots.py`
(ray-marches every camera).

1. **Opens clean.** Its `default_style_pack` is a naturalistic pack
   (`raw` mood = palette-quantize only; NO edge/ascii/neon/scanline
   distortion on the establishing shot). Stylized moods are beats,
   reached mid-scene via `[mood:]`, never the baseline.
2. **Lit to diner-class.** Warm ambient ≥ ~0.5, three-light
   foundation present, practicals at visible fixtures
   (_LIGHTING_PLAYBOOK). No cold 0.15 ambient, no all-black chapter.
3. **Establish frames the room.** The preset vantage is ray-verified:
   camera not inside geometry, ≥ several metres of clear sightline to
   the subject, the chapter's actual space in frame (not a corner or
   a wall). No wrong-room presets.
4. **No box props on featured surfaces.** Every insert-shot subject
   is a compound-silhouette prop (the clock bar: 4–10 primitives,
   silhouette variety, per-part colour, prose detail). Flat 1–3 box
   stacks on a hero surface are placeholders, not set dressing.
5. **Detail density.** The room carries dressing appropriate to the
   space, not bare walls + furniture. (Depth varies by tier — see
   below.)
6. **All cameras ray-check clean.** Markers AND preset, no
   camera-inside-object, no blocked hero shot.
7. **GLB builds.** `./run_cathedral.sh build_<name>.py` exports
   without a Python error (a failed bake blanks the chapter — the
   cathedral lesson).

## Two quality bars (so this finishes this decade)

The ch0–2 treatment (five asset passes each) is too heavy to run 51×.
Split the bar:

- **BASELINE** — items 1,2,3,6,7 + a box-audit of only the
  *featured* props (item 4 on insert subjects). Fast per locale
  (mostly preset + lighting + pack + a few prop swaps). This alone
  removes the "weird / broken / boxy / too-dark" feeling everywhere.
  EVERY locale gets baseline.
- **HERO** — baseline + full items 4 & 5: deep detail passes,
  compound props throughout, multiple authored shots, staging-ready
  markers. Reserved for story-critical + high-screen-time locales.

## Tiers (by screen time = background-instance count)

**Tier A — hero treatment (4 locales, 153 bg instances):**
`louisiana_road` (67), `cosmic_comics_back_office` (43),
`cabin_interior` (27), `miller_back_porch` (16).

**Tier B — baseline now, hero if story-critical (13 remaining):**
lena_apartment, miller_kitchen, cosmic_comics_interior,
school_field_evening, sam_bedroom, maya_bedroom, centro_grocery_aisle,
kowalski_kitchen, nexcorp_fueling_station, board_lords_interior,
hans_bakery_back_kitchen, grandmother_kitchen_morning,
henderson_kitchen.

**Tier C — baseline (34 remaining):** the long tail of 1–5-instance
locales (bedrooms, kitchens, offices, bars). Batchable ~5–8 per pass.

## Done (9)

diner_interior ·  cathedral_interior · bungalow_interior ·
riverboat_interior · roberts_kitchen · kwik_stop_interior ·
chapel_exterior · dambrosios_formal · riverfront_exterior ·
louisiana_road · cosmic_comics_back_office · cabin_interior
(all Tier A/B/C already carried by the ch0–6 direction + asset work).

· miller_back_porch (2026-07-12) — night porch was under-lit (key
  0.5) + sparse (imported make_floor_plant but never used). Boosted
  ambient 0.55→0.72, key→1.1, fill→0.55, added a warm OmniLight
  practical tied to the visible porch-lamp bulb. Asset pass: rockers
  gained spindles + armrests; added a side table (mug + folded paper),
  doormat, potted plant, cordwood stack, hanging planter — compound
  silhouettes, lived-in density. Opens clean via strata[0]=raw.
· lena_apartment (2026-07-12) — key 0.55 → 1.05 (+fill/back), warm
  OmniLight practical at the desk lamp head. Asset pass: bed gained
  headboard + pillow + duvet; desk gained four legs, a gooseneck lamp
  (base/column/head), laptop, book stack, mug, and a four-leg chair;
  added a nightstand + clock, a packed bookshelf, a floor plant, and
  warm string lights on the north wall. (make_floor_plant was imported
  and unused — same copy-paste template gap as the porch.)
· miller_kitchen (2026-07-12) — already dense (compound counter/stove/
  fridge/pedestal-table). Lighter pass: key 0.75→1.0, added a warm
  overhead OmniLight practical for the fluorescents. Chairs gained
  legs; added a fruit-bowl centrepiece, a drip coffee maker
  (make_coffee_pots, was unused), dish rack, paper-towel stand, and a
  wall calendar (make_calendar, was unused).
· cosmic_comics_interior (2026-07-12) — key 0.65→1.0 + broad cool
  overhead OmniLight (comic shops are bright). The "ComicRack" flat
  wall slab became an iconic revolving spinner (base/pole/3 tiers × 6
  wire pockets with comics). Added a glass display case of graded
  slabs by the register, an action-figure pegwall, a cardboard
  standee, and a stool. Bins already good.
· school_field_evening (2026-07-12) — WAS the generic room template:
  four walls, a ceiling, fluorescent tubes, a porch railing — an
  indoor box labelled "field evening." Full rebuild as an exterior
  dusk field: striped turf + yard/side lines, stepped bleachers, two
  goalposts, four floodlight poles with lamp banks, a chain-link fence.
  tscn: dusk-blue sky colour, warm low-sun key 0.5→1.3, ambient→0.72,
  four cool-white stadium-flood OmniLights over the turf. (Watch for
  other locales still on the room template — grep build_*.py for
  make_fluorescent_tube_fixture in exterior-named scenes.)
  Exterior audit run: only the field had a wrong ceiling; the flagged
  porches (caldwell/miller) are legitimately covered.
· sam_bedroom (2026-07-12) — same bare bedroom template as lena.
  Key 0.55→1.0 + desk-lamp practical. Bed gained headboard/pillow/
  comforter; desk gained legs, clip lamp, chunky CRT monitor +
  keyboard, game console + controller, and a chair. Teen dressing:
  nightstand + clock + globe, low colour-blocked game shelf, beanbag,
  skateboard against the wall, laundry pile.
· maya_bedroom (2026-07-12) — further along than sam's (pillow, throw,
  desk legs, books already). Key 0.55→1.0 + desk-lamp practical. Bed
  gained headboard + comforter + two plush toys; added a nightstand +
  clock, a vanity dresser (body, 3 drawers, framed mirror, trinket
  bottles), a floor plant (make_floor_plant, was unused), and warm
  fairy lights on the north wall.
· centro_grocery_aisle (2026-07-12) — already bright + real aisles/
  endcaps (lighting fine). Added two overhead fluorescent light-pool
  OmniLights, plus grocery dressing: a shopping cart (wire basket +
  frame + wheels), a chest freezer, a hanging aisle-number sign, a
  stack of hand baskets, and a wet-floor cone.
· kowalski_kitchen (2026-07-12) — leaner miller_kitchen (seat-only
  chairs, no fridge). Key 0.75→1.0 + overhead practical. Chairs gained
  backrests + legs; added a fridge, drip coffee maker, dish rack, wall
  calendar, table napkin/salt/pepper centrepiece, floor plant.
· nexcorp_fueling_station (2026-07-12) — was a near-empty store box
  (register + 2 endcaps only), no sign it fuels anything. Built into a
  gas-station mart: reach-in cooler bank (east), two snack aisles, a
  coffee station, a roller-grill hot case, an impulse rack, a backlit
  brand sign behind the register, and a west storefront window with a
  fuel-pump island + canopy beyond it. tscn: dusk exterior colour +
  overhead light pools + cooler glow + warm forecourt canopy light.
· board_lords_interior (2026-07-12) — board-game shop with two EMPTY
  flat bin base boxes and dim key (0.65). Bins became double-sided
  gondolas stocked with spine-out board-game boxes; added an open-play
  demo table (board mid-play + tokens + two chairs) and a glass dice/
  mini case by the register. Key→1.0 + violet-white overhead pool.
· hans_bakery_back_kitchen (2026-07-12) — well-lit already but sparse
  (a single stove box). Stove → commercial deck oven (glass doors with
  warm interiors + handles + hood); added a rolling speed rack of
  sheet trays + loaves, a flour-dusted prep table (dough balls +
  rolling pin), stacked flour sacks, and a wall shelf of mixing bowls.
  Added a warm oven-glow OmniLight.
· grandmother_kitchen_morning (2026-07-12) — well-lit, counter/stove/
  pedestal-table present but no homey dressing. Added a china hutch
  (stacked plates behind glass), a braided oval rug under the table, a
  tea kettle on the stove, a pie + fruit bowl on the table, potted
  herbs on the counter, a corner floor plant, and a soft warm overhead
  pool.
· henderson_kitchen (2026-07-12) — seat-only chairs; fridge already
  present. Key 0.75→1.0 + overhead practical. Chairs gained backrests
  + legs; added coffee maker, dish rack, wall calendar, table
  napkin/salt/pepper centrepiece, floor plant. This completes Tier B.

### Tier C (2026-07-12, in progress)
· diego_bedroom — bare bedroom template. Key 0.55→1.0 + desk-lamp
  practical, ambient→0.78. Bed gained headboard + comforter; added a
  nightstand + clock, a dresser, a soccer ball, a desk chair, and a
  floor plant (make_floor_plant was unused).
· jesse_bedroom — identical bare template. Same pass: ambient→0.78,
  key→1.0 + desk-lamp practical; bed headboard + comforter; nightstand
  + clock, dresser, desk chair, floor plant.
· pit_stop_office — garage back office, dim (key 0.55) + floating
  monitor + plain filing boxes. Ambient→0.8, key→1.0, +overhead
  practical. Desk gained sides, CRT + keyboard + work-order papers +
  mug + gooseneck lamp + a swivel chair; filing cabinets gained drawer
  faces + pulls; added a pegboard of work orders, a wall calendar, a
  parts shelf of boxed parts, a coffee maker, and a stack of tyres.
· cafe_olimpico — already hand-authored to hero density (espresso
  machine w/ group heads + steam wand, pastry case, marble bentwood
  tables, vinyl booth, soccer pennants). Lighting-only pass: key
  0.65→1.0, fill→0.5, + two warm amber pendant pools (over the bar and
  the seating). No build change needed.
· new_orleans_apartment — hand-authored hero build (four-poster canopy
  bed, shuttered French windows + wrought-iron balcony, exposed brick,
  armoire, ceiling fan). Lighting-only: key 0.65→1.0, fill→0.45, + a
  warm ceiling-fan-light OmniLight. No build change.
· new_orleans_office — hand-authored period office (oak desk, leather
  chair, wood paneling, bookcase) but dark (key 0.4). Lighting-only:
  ambient→0.78, key→0.55, fill→0.7, + a warm overhead pool and a
  green banker's-lamp glow on the desk. No build change.
· Tier-C lighting batch — hand-authored rooms already at prop-density,
  lifted lighting only (tscn, live on pull):
  - new_orleans_room: dim (key 0.45) → ambient 0.5→0.7, key→0.85, +
    bare-bulb overhead practical.
  - montreal_apartment: key 0.65→0.9, fill→0.4, + warm lamp practical.
  - natalie_apartment: key 0.7→0.95, fill→0.5, + warm table-lamp
    practical.
  - roberts_house: crushed ambient 0.28→0.45 (had strong fill 1.4;
    otherwise its considered moody rig is left intact).
· daigles_roadhouse, lacombe_service_garage — reviewed: hand-authored
  with intentional high-fill rigs (fill 1.1–1.4, low ambient for bar/
  work-light contrast). Left as-is; at standard.
· caldwell_kitchen_night — template kitchen missing sink/stove/chairs.
  Added sink + faucet + stove to the counter, chairs (backs + legs) to
  the table, a fridge, coffee maker, wall calendar, table centrepiece,
  floor plant, + a warm overhead night-pendant practical.
· caldwell_porch_night (2026-07-12) — night porch with seat-only
  rockers + a bare bulb, under-lit (key 0.5, ambient 0.55). Rockers
  became compound (back + spindles + armrests + legs + curved runners);
  porch lamp became a real carriage fixture (bracket + glass housing +
  bulb). Added a side table (mug + folded paper), doormat, cordwood
  pyramid, corner floor plant (make_floor_plant was imported/unused),
  and a hanging planter over the railing. Lighting: ambient 0.55→0.65,
  key 0.5→1.0, fill 0.35→0.55, + a warm OmniLight practical at the
  porch-lamp bulb (energy 2.2, range 4.2).
· el_rancho_taqueria (2026-07-12) — near-empty: a register counter and
  ONE legless cyl table top. Already bright/warm (lighting fine), so
  this was an asset build-out. Added a chip warmer on the counter, a
  north-wall menu board (frame + colour-coded price rows), a salsa/
  condiment station (metal insert pans + squeeze bottles + napkins), a
  proper dining set (3 pedestal tables, each with 2 backed chairs), an
  east-wall neon sign (magenta border + cyan/amber text tubes), and two
  ceiling festoon strands of warm bulbs. Lighting: added two warm
  overhead dining pools, a counter pool, and a magenta neon-accent omni.
· foxhole_stage (2026-07-12) — labelled a live-music stage but was an
  empty box with three wall flyers. Built the whole stage: raised deck
  with a warm lip + skirt, a compound drum kit (kick + snare-on-stand +
  two rack toms + floor tom + two cymbals + hi-hat), two 4x12 amp
  stacks (cab cones + head + knobs + power LED), two boom mic stands,
  two monitor wedges facing the band, and two flanking PA stacks
  (sub + top + woofer/horn). Kept the flyers. Lighting stays
  intentionally dark/dramatic: key 0.5→0.6, ambient left at 0.55, +
  a stage rig of four coloured practicals (warm front wash, magenta +
  cyan side accents, a low red backlight kicker) so the stage reads
  without flattening the mood.
· hospital_room (2026-07-12) — was mislabelled break-room template (a
  microwave on a counter), not clinical at all. Rebuilt as a patient
  room: adjustable bed (frame + legs + mattress + inclined head +
  pillow + teal blanket + head/footboards + side rails), a vitals
  monitor on a rolling stand (ECG waveform + colour readouts), an IV
  pole (5-star base + hook + bag + drip chamber + line), a privacy
  curtain on a ceiling rail, a bedside armchair, an overbed tray table
  with a cup, and a north-wall window (make_window was imported/unused).
  Lighting shifted warm→clinical cool-white: ambient recoloured cool at
  0.62, key/fill/back cooled, + two cool-white overhead fluorescent
  practicals and a small cyan-green glow at the monitor screen.
· foxhole_bar (2026-07-12) — labelled the bar side of the Foxhole venue
  but was the generic room template (a lone 2.4m counter + fluorescents).
  Full rebuild as a music-venue bar consistent with foxhole_stage: a 6m
  bar counter with brass foot rail + rail posts, a three-tier back-bar
  bottle wall (48 bottles) + long back mirror, a four-handle draft-tap
  tower, five bar stools (seat + pillar + foot ring + base), two high-tops
  each with two stools, three neon beer signs (magenta/cyan/amber tube
  rectangles), two warm hanging pendants, and band flyers on the west +
  door walls. Lighting stays moody-warm like the stage: key 0.5→0.62,
  ambient left 0.55, + two warm pendant practicals, a back-bar glow, and
  saturated magenta + cyan neon-accent omnis at the signs.
· foxhole_dressing_room (2026-07-12) — was the generic room template
  (a desk top + one lamp-head cylinder + posters). Full rebuild as
  backstage: a bulb-framed vanity mirror (table + framed mirror + 11
  warm bulbs + clutter + stool), a clothing rack with five garments,
  a beat-up couch (base + back + arms + cushions + tossed jacket), two
  guitar cases on the floor, a taped-up setlist with tape tabs + a
  sticker cluster, and a mini-fridge with cans on top. Kept the accent
  rug. Lighting warm dressing-room: key 0.55→0.7, ambient left 0.65, +
  a warm bulb-frame practical at the mirror and a soft couch-nook glow.
· daily_grind_interior (2026-07-12) — coffee shop that was the generic
  template (register counter + ONE legless table top). Built out to the
  cafe_olimpico idiom: a 5.6m espresso bar (2-group machine + steam wand
  + cup stack, drip coffee pots [make_coffee_pots was imported/unused],
  pastry case, register, sugar/creamer caddy), a chalkboard menu with
  price rows, three round café tables each w/ two legged chairs + a cup,
  a lounge nook (couch + armchair + low table + magazine), a corner floor
  plant, and three warm hanging pendants. Lighting: key 0.7→1.0, ambient
  0.75→0.78, + three warm pendant practicals over counter + seating.
· new_orleans_bar (2026-07-12) — already hand-authored to good density
  (7m mahogany bar + brass foot rail, three-tier bottle wall + back
  mirror, 5 stools, Wurlitzer jukebox, three pendant lamps). Mostly a
  lighting pass: added the one missing asset the brief called for — a
  compound ceiling fan (downrod + brass motor + four blades + a warm
  light kit). Lighting: key 0.55→0.7, ambient left 0.75, + practicals
  at every visible fixture — three amber bar pendants, the fan light,
  a bottle-wall backlight, and a warm jukebox glow.
· le_roulant_casino (2026-07-12) — extremely dense hand-authored build
  already (roulette table + wheel, five slot machines, cashier cage,
  marble columns, neon wheel sign, chandeliers, + two waves of scenario
  props). Lighting-only, but the OLD rig was broken: its WheelHotspot +
  FillBack omnis sat at +Z, i.e. OUTSIDE the room, which lies at -Z (the
  Blender→godot -Y flip). Rebuilt the practical rig over the real
  geometry: two warm chandelier pendants + a warm felt hotspot over the
  roulette table, a jewel pink-red neon-sign glow, two cool purple slot-
  bank glows on the W wall, and a warm cashier-cage glow. Ambient
  0.32→0.5 and key 0.78→0.9 so the glitz reads without flattening the
  smoky/dramatic mood (fog kept). tscn-only; live on pull.
· bianca_kitchen_morning (2026-07-13) — template rebuild (identical bare
  kitchen template to pre-fix caldwell: counter with no sink/stove, table
  with no chairs, single-box fridge). Added sink + faucet + spout, stove
  with four burners, coffee maker (make_coffee_pots was imported/unused),
  chairs (backs + legs), a breakfast centerpiece (napkin holder + salt/
  pepper + fruit bowl), fridge doors + handle, a wall calendar
  (make_calendar unused), a corner floor plant (make_floor_plant unused),
  and a wall clock (make_wall_clock unused, 7:45). Lighting: key 0.75→1.0
  (warmed to morning), fill 0.45→0.5, + a warm overhead pendant practical
  (energy 1.1, range 4.5) at godot (0, 2.5, -2.5). Geometry rebuilds on
  Deck; lighting is live on pull.
· ramos_kitchen_morning (2026-07-13) — template rebuild (bare kitchen:
  cyl pedestal table with seat-only chairs, single-box stove, no sink/
  fridge/dressing). Chairs gained backs + legs; the pedestal gained
  splayed feet; added sink + faucet + spout + coffee maker on the counter
  (make_coffee_pots was imported/unused), a stove top with four burners +
  oven door + handle + backsplash + knobs, a fridge (doors + handle), a
  table centerpiece (napkin holder + salt/pepper + fruit bowl), a wall
  calendar (make_calendar unused), a corner floor plant (make_floor_plant
  unused), and a wall clock (make_wall_clock unused, 7:30). Lighting: key
  kept at 1.1, fill 0.45→0.5, + a warm overhead pendant practical (energy
  1.1, range 4.5). Geometry rebuilds on Deck; lighting live on pull.
· roberts_kitchen (2026-07-13) — hand-authored to hero density already
  (kitchen island + stools + coffee/caddy, north-wall sink+stove+fridge
  with burners/knobs/magnets, breakfast table + chairs, CRT+VCR corner,
  clock/calendar/poster/plant, crown molding, two windows). Lighting-only.
  FIXED a stray-light bug: the existing Practical_Overhead sat at godot
  z=+3.5, i.e. OUTSIDE the room (which lies at -Z per the blender→godot
  -Y flip) — moved to z=-3.5 over the real geometry. Also key 0.65→0.95,
  fill 0.45→0.55, ambient left 0.85, + a cool back-yard spill omni at the
  E window and a cool CRT-glow omni in the SE TV corner. tscn-only; live
  on pull.
· elicia_apartment (2026-07-13) — hand-authored (compound sofa, coffee
  table, vinyl shelf + records, studio nook with mic/ring-light/laptop,
  plants, poster, clock, two windows, crown). Lighting-only. FIXED a
  stray-light bug: the existing Practical_Ring sat at godot (2.4,1.2,+4.5)
  — the +Z put it OUTSIDE the room (which lies at -Z) and x was off from
  the nook; moved to (3.2,1.2,-4.5) at the real ring-light. Also ambient
  0.7→0.76, key 0.55→0.95, fill 0.4→0.5, + a cool daylight-spill omni at
  the W window. tscn-only; live on pull.
· finn_apartment (2026-07-13) — template rebuild (bare bedroom: 2-box
  bed, desk top + a lone lamp-head cyl, rug; only Key/Fill/Back, no
  practical). Applied the diego_bedroom recipe: bed gained pillow +
  throw + headboard + comforter; desk gained legs + a real lamp (base +
  arm + head) + books; added a nightstand + clock, a dresser (with drawer
  faces), a desk chair, crown molding, a north window (make_window was
  imported/unused), wall art (make_faded_poster unused), and a corner
  floor plant (make_floor_plant unused). Lighting: key 0.55→1.0, fill
  0.35→0.4, + a warm desk-lamp practical omni (energy 1.1, range 2.8) at
  the lamp head. Geometry rebuilds on Deck; lighting live on pull.
· kai_apartment (2026-07-13) — template rebuild (identical bare bedroom
  template to finn, cool-blue accent). Same diego recipe: bed gained
  pillow + throw + headboard + comforter; desk gained legs + a real lamp
  (base + arm + head) + books; added a nightstand + clock, a dresser
  (with drawer faces), a desk chair, crown molding, a north window
  (make_window imported/unused), and a corner floor plant
  (make_floor_plant unused); kept the three wall posters. Lighting: key
  0.55→1.0, fill 0.35→0.4, + a cool desk-lamp practical omni (energy 1.1,
  range 2.8). Geometry rebuilds on Deck; lighting live on pull.
· simon_apartment (2026-07-13) — extremely dense hand-authored Hanged-Man
  build (bed + crate lamp, kitchenette, armchair + static TV, tipped
  chair, hanging boot, banker's boxes, hanging phone — three waves of
  scenario props). Deliberately moody (ambient 0.32, one bare bulb +
  kitchen fluor). Lighting-only, mood preserved. FIXED two stray-light
  bugs: both BareBulb and KitchenFluor omnis sat at +Z (outside the room,
  which lies at -Z per the blender→godot -Y flip) — moved over the real
  fixtures (BareBulb→(0,2.14,-3.5), KitchenFluor→(-1.9,2.8,-2.4)). Only a
  single directional (WindowBlueKey) existed, so added a low warm Fill
  (0.18) + a cool cyan Back rim (0.22) to complete the three-light
  foundation without flattening the dark mood. Also ambient 0.32→0.42,
  key 0.42→0.5, BareBulb 0.85→1.15 (range→4.5), fluor 0.55→0.75, + a warm
  bedside crate-lamp glow omni. Fog kept. tscn-only; live on pull. This
  closes the seven-locale batch.
· courthouse_chamber (2026-07-13) — hand-authored to hero density
  already (judge's bench + dais, gavel + scales, witness stand, jury
  box + railing, two counsel tables + chairs, three public pews + bar,
  flags + court seal, arched window; plus three waves of scenario
  props). Lighting-only. FIXED two stray-practical bugs: BenchKey and
  AudienceFill both had y/z swapped AND sat at +Z (outside the room,
  which lies at -Z per the blender→godot -Y flip) — BenchKey (0,9.8,
  +3.4)→(0,4.2,-9.8) over the bench, AudienceFill (0,2.5,+3.4)→(0,4.2,
  -2.5) over the pews. Only one directional (KeyLight) existed, so
  added a warm Fill (0.4) + cool cyan Back rim (0.3) for the three-
  light foundation; key 0.85→0.9. Added a cool fluorescent pool over
  the well (MidFluor) and a cool daylight WindowSpill behind the bench.
  Ambient 0.38→0.52 (daytime courtroom, not a moody set). tscn-only;
  live on pull.
· parish_cemetery (2026-07-13) — OUTDOOR tomb-city, hand-authored to
  hero density (40+ vaults, central mausoleum, iron lampposts, fence +
  half-open gate, oaks, votive array; three waves of scenario plots +
  markers). Deliberately moody All Souls' dusk. Lighting-only. FIXED
  two buried-practical bugs: LampGlow_Center (0,0,+3.0) and
  MausoleumBounce (0,0,1.2) both had y/z swapped, so they sat at
  ground level (godot y=0) instead of at fixture height — moved
  LampGlow_Center to a real spine lamp (1.2,2.9,-2.0) and added two
  more lamp glows (N/S) along the spine; MausoleumBounce → (0,1.8,0)
  on the mausoleum body. Added a warm VotiveGlow at the lit vault.
  Only one directional (OvercastKey) existed → added a low warm Fill
  (0.22) + cool cyan Back rim (0.3) without flattening the dusk mood.
  Ambient 0.48→0.54 (modest lift for a mood set). tscn-only; live on
  pull. (Outdoor set centered on origin: godot z straddles 0, so both
  z signs are legitimate here — the bug was the y=0 ground burial.)
· roadside_chapel (2026-07-13) — hand-authored (altar + candles +
  crucifix, votive rack, two kneeler pews, statue niche, bell pull,
  stained-glass N window, brass pendant, plus a full cane-field
  exterior with mound + gravel path). Votive-warm sanctuary mood.
  Lighting-only. FIXED two stray-practical bugs: VotiveLight
  (0,5.8,+1.4) and FillBack (0,1.2,+1.8) both sat at +Z (outside the
  room, which lies at -Z) — VotiveLight → (0,1.3,-5.8) at the altar,
  FillBack → (0,1.5,-2.8) over the pews. Only one directional
  (KeyLight) existed → added a low warm Fill (0.24) + cool cyan Back
  rim (0.28). Added a warm AltarPendant over the altar. Ambient
  0.28→0.44 (was crushingly dark even for a mood set). tscn-only;
  live on pull.
· static_drive_in (2026-07-13) — the MOON snack-bar concession,
  hand-authored to hero density (L-counter + register, popcorn
  machine, soda fountain, candy case, marquee banner; big picture
  window onto the blank drive-in screen + moon + speaker posts +
  pickup + a maroon Cutlass Ciera; two waves of scenario props).
  Deliberately moonlit-static night mood. Lighting-only. FIXED two
  stray-practical bugs: SnackbarPracticalWarm (0,2.5,+2.3) and
  MarqueePulse (0,1.2,+2.5) both sat at +Z (outside the room, which
  lies at -Z) — moved to (0,2.6,-2.5) and (0,2.6,-1.2) over the real
  fixtures. Only one directional (MoonKey) existed → added a low warm
  Fill (0.2) + cool moonlit Back rim (0.28). Added a cool
  ScreenMoonSpill flooding in through the N picture window. Ambient
  0.3→0.4 (modest lift, contrast kept). tscn-only; live on pull.
· wgur_transmitter_shack (2026-07-13) — the TOWER transmitter shack,
  hand-authored to hero density (three-bay 19" rack w/ VU meters +
  LEDs, patch panel + jumpered cables, operator desk + Bakelite mic +
  log binder + headphones + chair; N window onto the 90m guyed tower
  w/ pulsing obstruction lights; two waves of scenario props). Night
  mood. Lighting-only. FIXED two stray-practical bugs: VUMeterAmber
  (-2.0,2.5,+1.5) had y/z swapped + sat at +Z (outside room) → moved
  to (-2.2,1.3,-2.0) at the rack; ObstructionPulseRed (2.0,14.0,+9.0)
  had y/z swapped so it hung 14m up on the wrong side → moved to
  (2.0,6.0,-14.0) on the actual tower beyond the window (legit
  exterior spill, range→10 to reach through the glass). Only one
  directional (WindowMoonKey) → added low warm Fill (0.2) + cool cyan
  Back rim (0.28). Added a cool Fluorescent overhead pool and a red
  ObstructionFloorPulse for the reflections on the floor by the N
  window. Ambient 0.28→0.4. tscn-only; live on pull.
· caldwell_radio_room_night (2026-07-13) — TEMPLATE rebuild. The .py
  was the bare auto-generated placement script (imported store_fixtures
  / shelving / food_service helpers it never called, and shipped only a
  desk-top + a monitor box + two filing boxes — a room-box mislabelled
  as a radio room). Full asset build-out as a station booth: a
  broadcast desk + mixing board (8 channel strips w/ faders + knobs +
  channel LEDs, two amber VU meters), a CRT monitor + keyboard + a
  second queue monitor, an on-air mic on a boom arm w/ pop filter,
  headphones on the desk edge, a W-wall equipment rack (reel-to-reel
  deck w/ two reels + heads, three cart machines w/ slots + status
  LEDs, an EQ w/ faders + amber readout), a lit ON AIR sign over the
  door, a coffee mug + a side table w/ a coffee maker (make_coffee_pots
  was imported/unused), a gooseneck desk lamp, crown molding, a night
  window (make_window unused), an HVAC vent (make_hvac_vent unused),
  and decor (wall clock 2:14, calendar, station-license poster, floor
  plant — make_calendar/make_faded_poster/make_floor_plant unused).
  Kept the bare-bulb pendant + fluorescent fixtures. Lighting: the
  tscn already had a warm night three-light foundation (ambient 0.65);
  added four practicals at the new fixtures — BareBulb pendant,
  ConsoleGlow (amber VU/board), DeskLamp, and a red OnAirGlow — all at
  negative godot Z (room sits at -Z; +Z audit clean). Geometry rebuilds
  on Deck; lighting live on pull. py_compile + stubbed-bpy main() smoke
  test pass.
· houston_office (2026-07-13) — Emperor corporate office, authored but
  sparse/boxy (cubicle row + manager glass office) with NO practicals.
  Enriched props: cubicle monitors gained inset glow screens + foot +
  keyboard + mug + papers; manager desk gained a glow screen, foot,
  rotary desk phone, blotter + papers. Added a whole exec suite —
  bookcase w/ four shelves of spine-out books, two filing cabinets w/
  drawer faces + pulls, a low credenza (doors + pulls + top w/ photo +
  trophy), two guest chairs (backs + legs) facing the manager desk, a
  framed diploma. Replaced the make_box N window with make_window
  (imported/unused) + added venetian blinds. Lighting: pitched Key_Fluor
  downward (0.65→0.85) + added five practicals — three fluorescent
  ceiling pools, a warm manager desk-lamp glow, and a cool window
  spill, all at negative godot Z (room at -Z; no +Z stray to fix, no
  practicals existed). Geometry rebuilds on Deck; lighting live on pull.
· houston_design_studio (2026-07-13) — Emperor cameo, authored to good
  density (drafting tables w/ tilted tops + anglepoise lamps, dual-
  monitor workstations, plotter, mood board, brick wall, exposed duct)
  but MISSING seating and NO practicals. Added five task chairs (seat +
  back + 5-star post/base on casters) at the drafting + workstation
  desks, a materials/samples shelf w/ colour-blocked sample bins, and a
  corner floor plant; wired make_window (imported/unused) for a proper
  mullioned N window. Lighting: added six fluorescent ceiling pools + a
  warm anglepoise-lamp glow at the drafting row + a warm brick-wall
  bounce, all at negative godot Z (room at -Z; no practicals existed).
  Geometry rebuilds on Deck; lighting live on pull.
· ember_ash_office (2026-07-13) — VII Chariot, already hero-dense hand-
  authored (Antonio's desk w/ bourbon/rotary phone/voicemail/ashtray/
  rolodex, office chair w/ 5-star base, window AC, corner-across window +
  radiator, cypress beam, back-stair opening w/ radio + milk crate, crew
  photo, pendant). LIGHTING was already +Z-corrected in a prior audit
  (VotiveLight/FillBack over the desk at negative Z) — left positions
  untouched. PROPS-focus pass: added a two-guest-chair set for visitors
  (Jimmy/the older man) and a lateral filing cabinet w/ drawer faces +
  pulls + a stack of folders + a desk fan to round out the office.
  Lighting left entirely intact (the existing warm VotiveLight already
  reads as the desk-pendant pool; moody warm ambient 0.28 kept — reads
  well). Geometry rebuilds on Deck (tscn unchanged this pass).
· centro_break_room (2026-07-13) — vol6 break room, SPARSE template-ish
  (imported make_counter/coffee_pots/wall_clock/floor_plant/calendar/
  register etc. but called almost none; only a pedestal table w/ legless
  chairs, a vending machine, a microwave box, a bulletin board). Full
  build-out: a real galley counter w/ stainless sink + faucet + gooseneck
  spout, a compound microwave (door + window + panel + handle) + a drip
  coffee maker (make_coffee_pots, was unused) + upper cabinets; a fridge
  (doors + handles + kick), chairs gained legs, added a wall clock
  (make_wall_clock unused), a corner floor plant (make_floor_plant
  unused), a wall calendar (make_calendar unused), and a swing-lid trash
  bin. Lighting: added two fluorescent ceiling pools + a warm vending-
  machine glow, all at negative godot Z (room at -Z; no practicals
  existed). Geometry rebuilds on Deck; lighting live on pull.
· hospice_room (2026-07-13) — end-of-life palliative room, authored like
  the hospital_room rebuild (adjustable bed, IV pole, vitals cart,
  visitor chair, bedside table, curtained window) but too clinical/cool.
  Warmed it home-like per the hospice brief: recoloured the palette warm
  (oak floor, cream walls, warm linen), added a soft sage blanket folded
  over the bed, a warm bedside table LAMP (base + column + shade), a vase
  of flowers + the existing water cup/photo, a small dresser (body + 3
  drawer faces + pulls + a runner cloth), a wall crucifix, and a knit
  throw over the visitor chair (now a comfier armchair w/ arms). Lighting
  shifted clinical→warm: ambient recoloured warm, Fill_FluorOverhead
  softened + warmed, + a warm bedside-lamp practical and a soft warm
  window glow, all at negative godot Z (room at -Z; no practicals
  existed). Geometry rebuilds on Deck; lighting live on pull.
· asylum_ward_c (2026-07-13) — XIII Death, already hero-dense hand-
  authored corridor (5 patient-room doors, 2 window bays, nurses'
  station w/ chart binder/votive/file cab/chart pockets, gurney,
  wheelchair, broken cupola, + two waves of scenario dressing). LIGHTING
  was already +Z-corrected in a prior audit (CorridorFluor/CupolaBlue at
  negative Z) — left positions untouched. PROPS-focus pass leaning into
  the stark/institutional brief: added reinforced security bars over both
  E window bays, a cast-iron radiator (body + fins) under the south
  window bay, and a single hard institutional chair by the nurses'
  station. Deliberately dim green-tile dread ambient (0.34) kept — reads
  well. Geometry rebuilds on Deck; lighting live on pull.

## Execution plan (LOCKED 2026-07-12)

User decision: **deep (hero) treatment on EVERY locale, in
screen-time order.** No baseline-only tier — every one of the 51
gets the full 7-item standard including deep detail (items 4 & 5).
Sequence strictly by background-instance count, highest first, so
the most-seen sets improve first. One commit per locale; every
commit: survey → audit → fix → ray-check → note the builder to
rebuild → move the locale into Done here.

Worklist (screen-time order, remaining):
1. louisiana_road (67)  ✓ DONE
2. cosmic_comics_back_office (43)  ✓ DONE
3. cabin_interior (27)  ✓ DONE
4. miller_back_porch (16)  ✓ DONE
5. lena_apartment (14)  ✓ DONE
6. miller_kitchen (11)  ✓ DONE
7. cosmic_comics_interior (11)  ✓ DONE
8. school_field_evening (10)  ✓ DONE
9. sam_bedroom (9)  ✓ DONE
10. maya_bedroom (9)  ✓ DONE
11. centro_grocery_aisle (8)  ✓ DONE
12. kowalski_kitchen (7)  ✓ DONE
13. nexcorp_fueling_station (7)  ✓ DONE
14. board_lords_interior (7)  ✓ DONE
15. hans_bakery_back_kitchen (7)  ✓ DONE
16. grandmother_kitchen_morning (6)  ✓ DONE
17. henderson_kitchen (6)  ✓ DONE  ← Tier B complete
18-51. Tier C tail (5→1 instances) — see tier list above.  ← NEXT

Progress is tracked by moving locales into the Done list above and
checking them against the 7-item standard.

## Recent lessons feed the standard

Every fix that reveals a new failure mode updates item-list above and
the relevant playbook (_3D_MODELING / _LIGHTING / _SHADER_VISUALS /
_VN_DIRECTION). The tools are the contract: if survey/check_shots
pass, the locale ships.

## Queued follow-ups (2026-07-12, from live playtest)

- **Earthman choice-box overflow — propagate the Ch2 fix (HIGH, quick).**
  Ch2 (EarthmanChapter2Approach.gd) FIXED: choice beats' options
  overflowed the panel bottom because the (usually empty) body label
  reserved the middle while options were crammed into a 140px bottom
  strip. Fix pattern: pull _content_lbl into a slim top band
  (offset_top -160 / bottom -70), move _choices_root into the vacated
  middle (offset_top -55 / bottom 215), bump fonts (speaker 20, body 18,
  option button 19, note 15 + autowrap), and add an amber bezel ring +
  corner ticks around the panel ("art rings the bounds"). SAME literal
  100/240 offsets exist in EarthmanChapter1Intro, 3Talikan, 4Mines,
  5Academy, and EarthmanChroniclesHost — apply the identical fix to
  each (best: factor a shared _render_choice_panel helper).
- **Slowstick "shine" art pass (Earthman) — CREATIVE, meaty.** User:
  the abstract/early-computer-art baseline works, but make some corners
  really shine — HD computer art "from a more advanced technology, but
  divergent artistically" (per _SLOWSTICK_AESTHETIC_BIBLE: render MODERN
  through SlowstickLook demoscene_post, NOT retro cosplay). Use the
  director tool for hero moments (the Two-Moons desert vista, the Parsa
  approach, Working reveals). Pick 3–5 hero beats per chapter, author
  high-effort HeroImages/backdrops in the divergent-HD register, leave
  the rest in the clean abstract baseline. Reference the aesthetic
  bible's per-studio LOOK presets first.

- **ch1 Magician · full direction pass (DONE 2026-07-12).** Whole
  chapter now cuts through the arcana lens family: model-city districts
  (motherboard plazas / LED tenements / holo-casino) each get a
  [shot:insert model_city] under alternating neon↔green filters; the
  Frankenstein phone → arcana_ink inserts; the god's-eye GumboNet
  overlay → arcana_green (phosphor); the silver-spoon riverboat dread
  beats → arcana_ink; the soldering iron → arcana_neon workbench
  inserts; Frasier's skull-grin → arcana_ink; opens + closes on
  arcana_warehouse. Replaced the old cathedral_devil/cathedral_workbench
  moods with arcana equivalents so the chapter reads as one coherent
  cyberpunk-magickal identity. (Prev "STARTED" note superseded.) Established the
  "arcana" cyberpunk-magickal look: new MOOD `arcana` (violet edges +
  light-green fill floor + deep purple-black, saturated red/white scene
  bits bleed through = the flashes; GPU-safe neon-only), LIGHTING
  `arcana_magick` (violet dir tint, warm-magenta ambient, practicals
  boosted), and STYLE_PACKS `arcana_warehouse` (baseline), `arcana_green`
  (kudzu/LEDs/screens), `arcana_neon` (hot-violet spell glow),
  `arcana_ink` (black/red/white high-contrast). Opening + 4 beats of
  vol5_ch1_magician.json retagged. TODO: finish the chapter — a
  [shot:insert <prop>] on EVERY described bit (the jury-rigged phone,
  solder iron, the model-city districts, the fluorescent seraphim, the
  patched bomber jacket) each through a fitting arcana lens; vary the
  filter beat-to-beat so it reads as "cool views through a variety of
  lenses." Reference the arcana family + the [shot:]/[mood:]/[stage:]
  grammar in _VN_DIRECTION_PLAYBOOK.
- **Per-locale ambient audio layer (NEW, subsystem).** Each locale
  should carry its own ambient bed that, on scene-enter, DUCKS the
  dominant BGM track in the music player way down and raises its own
  layer — effectively an "inverted ambient soundtrack" second player.
  Design: a locale ambient-bed field (per-locale JSON or Background3D
  preset) → an AmbientBed autoload/second AudioStreamPlayer that
  cross-fades against the main BGM bus (main bus volume ducked via a
  tween, ambient bus raised), restoring on scene-exit. Read
  _AUDIO_PLAYBOOK (SFXBank pool discipline) + the music-player code
  first. Ambient beds themselves author via slowstick_synth. For ch1:
  warehouse drone + ozone hum + sputtering-fluorescent bed under the
  arcana look.

- **Diner wall bar (from live shots, HIGH).** A brown/dark-red thin
  horizontal box runs the full length of a diner wall at ~chair-rail
  height (~0.9–1.3 m), passing THROUGH the door frame + wall clock +
  Mondrian panel — reads as an errant bar "running through
  everything." Seen in the Frasier/John (vol5 ch1 Magician) diner
  establishing + insert shots. NOT the counter/back-bar (those are at
  cy=-3.5). Suspect a perimeter chair-rail/wainscot or a cornice band
  added by build_shell / build_interior_partitions / _annex_wall_with_
  door / build_annex_hallway. FIX METHOD: run survey.py --box against
  build_diner.py to find the named box at that Y/Z spanning the wall,
  then trim/remove/reposition; rebuild on Deck to verify (don't blind-
  delete — risk of hitting the legit counter/cornice). Also: general
  "more hero prop passes" on diner insert subjects (condiment caddy,
  napkin holders still read boxy in top-down shots).


- **Diner relocate (CONFIRMED, big).** Move the entry sequence to
  portside (west extension), sequenced: front door → hostess stand
  → hall to formal dining, with the PRIVATE dining room opening off
  the hall (doors to both the hall and the entryway). Clears the
  private-dining island out of the main floor's center so the
  counter reads. Blast radius: build_diner.py (build_interior_
  partitions / build_formal_dining_room / build_private_dining_room
  / build_entry_props relocate west; bar currently at west-ext must
  co-exist or move), diner.tscn lights for those rooms, DinerGauntlet
  Host.SPACE_MAP (hostess_stand/bathroom/etc.) + TarotGauntletGame
  standalone diner vantages, collision walls. Do as its own careful
  pass; re-ray-check every gauntlet space after.
- **Gauntlet space vantages need rework.** e.g. booth_6 vantage
  [-7.95,+3.75,0°] faces EAST (yaw 0) away from the booth — "booth 6
  doesn't even look at booth 6." Audit all SPACE_MAP entries: the
  vantage should FRAME its named subject, not sit on it facing out.
- **Gauntlet cards → pictographs (DONE 2026-07-12).** GauntletCardFace
  now draws representational icons (walk=striding legs, focus=eye,
  search=magnifier, guard=shield, spend=coin, listen=ear, ...) keyed
  on card id + keyword fallback; abstract hash shape only for
  unmapped ids.
