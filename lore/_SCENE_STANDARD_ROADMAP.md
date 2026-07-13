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
