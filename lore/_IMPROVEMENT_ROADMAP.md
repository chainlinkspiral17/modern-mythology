# IMPROVEMENT ROADMAP · recommended next work

**Updated 2026-07-22.** The living plan for continual improvement
across every pillar. Priorities reflect the user's standing verdicts:
**graphics and presentation are always the sore points; the visual
novel needs the most work.** Update this doc when an item ships or a
blocking decision lands; future sessions should read it alongside
CLAUDE.md's playbook list.

## North star

Every pillar reads as a finished, art-directed work: the VN as a
cinematic literary book, the slowsticks as **alternate reality games
— sophisticated modern games made in an alternate timeline** (user
correction 2026-08-30; see THE CORRECTION in the aesthetic bible —
the old "SVGA bar" framing was our-timeline retro cosplay and is
dead), and all departments delivering in sync (the producer
discipline).

---

**2026-08-12 · SIX LOCALES HAD NEVER BEEN BUILT AT ALL.** The new
list_stale_builds.sh, first run on the Deck, found six builders
with no GLB on disk — and five of them are LIVE VN backgrounds
(ben_bedroom ×2 chapters, henderson_garage ×3, bindery,
centro_stockroom, miller_garage ×1 each = 8 chapters) plus
ember_ash_office, the Chariot gauntlet's board locale. Every one
of them has been rendering the 2D fallback — the same failure
class as the graustark brown, sitting unnoticed because nothing
ever compared builders against artifacts. Rebuild priority is
therefore: (1) the six never-built, (2) graustark + riverfront
(today's fixes), (3) the 38 stale. Lesson recorded in
_GEOMETRY_AUDIT_PLAYBOOK: an artifact that was never produced
looks exactly like an artifact that is merely old — enumerate
both.

**2026-08-12 · THE AUDIT'S EYES OPENED — and what it found.**
Widening the real-module whitelist (composite `_props` helpers had
been stubbed to no-ops) took the repo 18 → 286 clips, then triage
brought it to 39. The systemic finds, all invisible before:
- ELEVEN windows centered at floor level (`make_window`'s anchor is
  a CENTER; callers passed 0) — half-buried, ankle to knee.
- TWELVE counters and SIX windows built 90° ROTATED, because
  `make_counter` takes `depth` as X / `length` as Y and
  `make_window` spans X. Includes the New Orleans bar (7m through
  the north wall, stools in its flank), the Pit Stop lunch counter,
  and the kitchen template replicated in eight houses. Both helpers
  (and the bullnose, poster, calendar) now take `axis=`.
- The centro grocery double-booked store-wide (69 → 1).
Detection that generalizes: **a fixture against a wall must run
PARALLEL to it** — one geometric pass found all twelve rotations
without waiting for a collision.
ALSO: the shot-cue work. 453 blind object cues across 79 presets
(a cue with no marker used to ZOOM INTO A WALL); VnDirector now
substitutes a same-type marker or holds the wide, 374 cues covered.
Two never-modeled hero props built: Olaf's two bowls (21 cues) and
the Henderson pot roast (3 cues, a MODEL CHAPTER). The crow (12+
cues across four locales) now exists as `_props/creatures.py`.
NEXT: the 39-clip tail (crumpled_barn's 11 are the crumple),
26 locales still wanting marker pools, and the remaining --props
art gaps (tide_pool, Lena's canvas, the eviction notice).

**2026-08-19 · THE HERO-OBJECT HUNT, continued.** After the voice
drafts, four more art waves off the --props/marker rankings: the
Miller landline ("the landline never rings") + french toast
mid-making, the Starfish Nebula on Lena's alley wall WITH its four
patches (each differently wrong, one newer), Per's wooden box and
the bench that holds it, the Foxhole strip mall (the tracked
unit's papered window, the chalk marquee — Jesse's whole vol6
surveillance thread finally has geometry). The audit learned char
aliasing (closeup miller = chief_miller). Blind cues 435 → 366.
NEXT in the ranking: board_lords_interior (14 · bread/patch),
sam_bedroom (10), school_field_evening (9), maya_bedroom (8);
cabin_road's remaining 43 are mostly games-Finn-plays and
substitute-fallback territory — verify on Deck before adding more
there.

**2026-09-01 · THE BLIND-CUE HERO-PROP PROGRAM, six waves.** One
method down the ranking: prose anchor → props named for the
matcher → transform-format markers, rotation zero → marker_reaim
→ suite. Shipped: board_lords_interior (sanderling mural + patch,
hexagon + ARIA piece, bread, shop phone), lena_apartment (Estuary
7 stick on the side table, the hexagon + eighth piece, the letter
to Jorgen, phone, bread, bowl, deadbolt), hans_bakery_back_kitchen
(four cedar bowls + the crow on the substrate-bowl's rim, floured
handprints for the Aud/Marit beat, the four-AM back-kitchen
light), graustark star night (crow on the I-beam, the desk-that-
was-a-door-on-bricks, "I am ready.", the candle), miller_kitchen
(worn-patch hands, cinnamon roll, kolaches, jar, the white sedan
at the curb through the sink window), ramos_kitchen_morning
(hands, chorizo eggs in the skillet, the soup). Blind cues 324 →
277; marker_aim 113/113; overlap 0 regressions throughout. Deck
rebuilds queued for all six builders. LESSONS in the geometry
playbook (position-format markers are invisible to the tools —
conversion queued; residue grammar for human-contact cues; shared-
tscn presets clear in batches). CONTINUED same day, eleven more
waves: safehouse, centro, pit stop (+ the diner door and bell),
kwik stop (+ the NexCorp van), daily grind (+ the tower on the
hill), houston office, graustark world-shore (the Child / the
Frog / doohickey / smoke ring), nightmare cell, gas & go (+ the
Louisiana pickup), sam_bedroom, school field (+ the Vinton bus),
miller back porch (+ Finn's truck), henderson garage (+ Ben's
map and truck) → blind 277 → 213, marker_aim 168/168, overlap 0
regressions. Two deliberate blinds stand as precedent
(closeup_douglas; the cell window — explicit "no windows" canon).
THIRD STRETCH same day: natalie, bianca kitchen,
montreal (the dust motes), maya bedroom (the dock photograph),
new orleans bar, centro break room (the Karamazov), kowalski,
jesse bedroom, both salty tome presets (two bells), the bakery's
hidden three (--all lesson), the cathedral (the Speak & Spell +
the waiting crow) -> blind 171. FOURTH STRETCH: cabin_interior (15 cues — the
vol7 heart), henderson kitchen, finn apartment, six 3-cue presets
(riverboat card, Doyle's sedan + badge + cash, the August bills,
the green Subaru + quilt seat, the Speak & Spell under the
register, Rick's notebook), then the whole 2-cue tail in one wave
-> blind 85 across 25 presets, 276 aim-verified markers. FIFTH
STRETCH: all seventeen 1-cue presets -> blind 68 across 9 presets,
293 aim-verified markers. RE-HOMING DRAFT 1 (2026-09-01, user: "let's get real locales"):
25 road-staged segments moved onto real places — the nine alley
scenes (vol7's climax: the painting, the crowd at the wall, the
leaving) onto salty_tome_alley, now dressed with the nebula, the
substrate patch the face is painted into, the crate + brush + cedar
+ notebook, the four bowls, Lena's hand print, the crow, the
laundromat brick closing the far end; NEW cape_perpetua_overlook
(the earthen platform, rail, wet bench, salal, spur trail, the lot
with the Vestergaard truck and the old Subaru, fog in the trees
below, the hexagon on the earth); NEW main_street preset on the
Board Lords set (awning, sign, CLOSED, laundromat + shoe-repair
across, streetlamp, Finn's truck at the curb with the crow on the
cab); and re-points to bakery / cabin / cedar tower exterior /
henderson porch / cosmic front door. cabin_road 43 -> 18 blind.
RE-HOMING DRAFT 2 (2026-09-03, user: "if it will benefit the scene
and emotion of the storytelling, I want it. keep going"): four NEW
locales built from the prose, 34 re-points, blind 45 → 24.
(A) meadowlark_circle — the Harmony Creek cul-de-sac: eight ranch
houses (1402..1428 + the south three), the Miller cracked head and
its etched stripe, the sprinkler fans, Geller's house at the bulb
with Don's lit window, the vigil sedan + thermos, the water tower +
NexCorp fence + van, the black cat; day + night presets; prelude
and the three codas. (B) vehicle_cab — one hollow crew cab stands
for every parked-car conversation (Ben's truck, the El Rancho
lay-by with the flauta box on the console and the leaking El
Diablito, the Civic, Miriam's car, Miller's highway) with Claire's
white sedan + the picnic table at the turnout; cab + side presets;
11 re-points. (C) lake_palestine — the north boat ramp, Miller's
truck with the cooler, sixteen meters of dock to "the same metal
cleat," the cove, the eastern-shore pines the sun comes up over;
dawn key from the EAST. (D) estuary_7_template — the planner's-view
as a museum diorama in a dark room: sea, river, bar, flats, bluff +
Dean's seven-floor tower, Smolvud, the cabin hub with four
substrate-lines as circuit traces, mill + wheel, grove, diner, the
pools, palettes + clocks, Tem's one drone; plus the headset on the
cabin table beside the disc-case (a cabin_interior bg inserted
before Tem takes it off). The strip-mall scenes stay on
louisiana_road — that IS the strip mall. What remains on cabin_road
(8) is honest driving plus the Cape Perpetua tide-pool beat.
RE-HOMING DRAFT 3A (2026-09-03, later): the ch3_coda "three
blinds" were not on the street at all — nodes 7-21 are Rick in the
back office of Cosmic Comics (the interlude line "Outside, the
subdivision hums" was the only street beat). A back-office bg
inserted; the folder with the map / Polaroid / envelope + the
fireproof box under the desk built and marked. "Two Houses Down"
(ch5_garage 14, ch5_miller_drive 0) → NEW preset
meadowlark_circle_henderson (lot 1414 dressed: Ben's truck at the
curb, the Corolla, the light post + Maya's bike, the patrol vehicle,
the lit garage vent). vehicle_cab_rear for the four-up;
lake_palestine_dock for the accounting at the end of the dock.
Blind 24 → 21 (all deliberate). RE-HOMING DRAFT 3B-3D (2026-09-03,
same session): the three vol7 SUBSTRATE chapters that were still
"driving": (B) tideline_survey — ch18's basalt headland, the pools
as HOLES in a cell grid with their creatures under a thin water
skin, the cedar at the bottom of the second, the worn path, the
knee-hollows; two scenes over one glb so the tide_pool marker
frames the right pool (marker_aim now resolves a builder through
the tscn's glb reference). (C) kestrel_mountain — ch11's path as
ramps between flat station segments with a stepped cliff west and
drop wedges east, the hut, the stream + plank + bowl, the bench,
the hedge with berries, the cloud, and the square at the foot with
the three-basin fountain and twenty-two rim figures; two presets.
(D) accretion_basement — ch11 nodes 41-128, the 1990s hallway with
wire-glass doors, the stairs with the green handrail, the stenciled
door, the basement with six racks and the boy's desk; two presets.
Also the diorama's draft 2 (gallery layer sheets, off-frame labels,
the cursor) and Meadowlark's night practicals. Blind 21 → 14, every
one deliberate (hands ×2, cast closeups without ids ×4, the
strip-mall door/phone and the Cypress drive-by on louisiana_road,
the Bern press, the cell window, the tattoo, the charcoal, the
wooden box). RE-HOMING DRAFT 4A-4B (2026-09-03, same session):
the strip-mall back door open two inches with its blade of light
and spill, Jesse's Civic at the lot corner with the phone lit on
its dash (ch14 stays on louisiana_road — it IS the strip mall); the
Cypress motel built onto the same set (twelve rooms in an L, the
office, ice + soda machines, the walkway on posts, three cars, the
pole sign, Room 7 lit with its AC dripping) with preset
cypress_motel for ch15's drive-by; make_car() promoted into
_props/vehicles.py (along X/Y, hatch, pickup, light bar, a dash
gap for a phone); Per's wooden box was a MATCHER MISS (PersBox_*
had stood on the bakery bench since August — synonym + marker);
the interlude-ii LENA slug re-homed to her apartment with the
charcoal S U N as residue on the duvet. Blind 14 → 9. THE BLIND
PROGRAM'S END STATE (9): hands ×2 (kestrel, cab), closeup
coach_dale ×2 and closeup douglas ×2 (cast without char ids), the
Bern press (off the template's frame), the cell window (canon: no
windows), the tattoo (on skin). Nothing left to model for a cue.
NEXT (draft 2 of the nine new locales, per THE DRAFTING PROGRAM):
SCALE + EDGES + COVERAGE on meadowlark, the cab, the lake, the
diorama, the headland, Kestrel, the basement, the motel — second
presets where the chapter moves (the dock end and the square
already have theirs), edge-of-set treatment where the Deck shows
a world edge, Deck-verified framing before any more props. Then:
scree + switchbacks on Kestrel; the boot-wear channel on the
headland; the geometry audit's interior test (a ceiling over the
camera should exempt a locale from the 40 m exterior rule); the
exterior template's upward Sun basis. Check
the exterior template's Sun: its −Z basis points UP (+y) in
kowalski/meadowlark/cape/vehicle_cab — the Sky_Fill does the
modeling; lake_palestine's Sun was authored downward on purpose.

**2026-09-03 (evening) · THREE USER VERDICTS, THREE PROGRAMS.**
(1) "the stretches of highway across all the volumes look identical,
same geometry, same camera. fix this shit." — vol1, vol2 and vol6
had all been playing on the vol5 Louisiana swamp road from one
breakdown-lane vantage, with vol6's whole New Auburn dressing built
among the cypress. Split into one set per region: louisiana_road
(vol5, swamp), NEW new_auburn_road (vol6, Texas: the moved
subdivision / water tower / gas station / strip mall / Live Oak /
Cypress plus the front lot, the cedar route, the open two-lane with
the van and the Chronicle sedan, the NAPD substation off the bypass;
five presets), NEW small_wood_road (vol1-2, Oregon county road: the
property gate, pole barn, tool shed, chicken coop, the crick and
culvert, the fallen-in house, firs; three presets), NEW highway_101
(vol7 ch22: guardrail, the drop to the sea, the cedar wall, the
headland, the chained Old Yachats Road turn; two presets). Every
road preset is a different place, height and lens. 14 re-points.
(2) "another establishing shot that is 90 percent wall/obstructed.
frame scenes to maximize the set/the props/the drama." — NEW
vantage_obstruction_audit.py (ray fan per preset; near-fill, single-
surface fill, camera-inside-a-box; --propose grid-searches a better
camera) found 21 of 153; all re-placed (the cabin wide stood inside
the bed alcove, three kitchens stood inside the fridge, the Foxhole
inside a PA cabinet, Kestrel's square inside a building, the
bungalow behind a closet ...); it is a suite gate now. (3) "movement
in pirate summer is completely broken." — the slowstick input fence
swallowed joypad buttons before the GamepadMgr autoload could
translate them, so the day-intro modal could never be dismissed on
pad; fixed in InputBlocker; the modal's button gets focus for A;
Cabin Beaver's doorway was walled in by a pine (a zone-reachability
BFS over all 17 zones is clean). NEXT: the Deck has not yet seen any
of the nine new locales or the four road sets — build_scenes.sh
then look, before any more props; the exterior template's Sun; a
ceiling test for the geometry audit's exterior rule; the road sets'
draft 2 (a bend or a crest each — every road is still straight).

**2026-09-05 · DETAIL DRAFT 1 — "basic cubes and rectangles."** The
primitive layer was the ceiling: box, cylinder, blob. Five real
primitives (lathe, prism, tube + catenary, rotated box,
heightfield), each registered in the audit recorder; the shared
composites rebuilt on them — make_car draft 2 (profile body, lathed
wheels, seams, lights, mirrors, wipers), NEW buildings.make_ranch_
house / make_shed (gable prism with eaves and shingle courses,
siding, trimmed windows with shutters, paneled door, turned porch
posts, chimney, gutters, downspouts, garage), the roadside kit
(utility poles with insulators and sagging wires, W-beam guardrail,
wire fence with a gate gap, ditch heightfield), bare trees and
shrubs. Applied to new_auburn_road, small_wood_road, highway_101,
meadowlark_circle (all fourteen houses), the Kestrel fountain, the
lake pilings. DETAIL DRAFT 2 TARGETS: the cab interior (wheel as a
lathe loop, cup, knobs, chamfered seats and dash); a furniture kit
(chair with turned legs, table with apron and stretchers, lamp with
shade, stool) for the nine new interiors; Meadowlark's water tower
and streetlamps lathed; road bends as yawed prisms and ground as
heightfields under the road sets; a chamfer pass over every
interior's furniture boxes; then the model chapters themselves (the
diner's 910 boxes) through the same kit. The Deck has still seen
NONE of it — build, look, then continue.

**2026-09-06 · DETAIL DRAFT 3.** The de-blocking POLICY: make_box
auto-chamfers every prop-sized box (≤ 3 m a side, ≥ 2.5 cm thick,
no open faces) with a 2% cut — every builder's furniture, doors,
crates and fixtures get cut edges without a line changed; walls,
floors, roads, decals and glass stay as they were. Plus: Meadowlark's
water tower and streetlamps lathed (catwalk, rails, cobra heads), the
chained turn on 101 hangs a real catenary chain, slate slabs on the
Kestrel hut, the strip mall's parapet cap / cornice / downspouts /
vents, Miller's lake truck through make_car. DRAFT 3B (in progress):
road BENDS — a shared make_road_bend (arc + run of prisms, "Road"-
prefixed so the segments are one assembly) on small_wood, 101 and
new_auburn so no road runs straight to the horizon; a heightfield
ditch beside the Small Wood road. Every GLB changes under the chamfer
policy: the Deck rebuild is build_scenes.sh, not a list.
DRAFT 3B shipped: make_road_bend (arc + run of "Road_"-prefixed
prisms) — Small Wood bends 20° east into the firs at y 150, 101 bends
28° inland at y 250, New Auburn curves 18° west at y 420 past the van;
a heightfield bar ditch beside the Small Wood gate. DRAFT 3C shipped:
the fourteen vendored make_box copies (the diner, the kwik stop, the
cathedral, the bungalow, the riverboat, the riverfront, Roberts,
Harmony commercial, the gas station, five prop builders) delegate to
the shared one, so the MODEL CHAPTERS take the chamfer policy; the
three family kitchens' tables and chairs through the furniture kit
(Ramos's pedestal turned). Side effect: the diner became measurable
by the geometry audit for the first time and failed ("view stops at
69m") — a river-town horizon fixed it. DRAFT 4 TARGETS: the two
unmeasured builders (harmony_district, harmony_terrain record zero
boxes); the remaining hand-built chairs and tables (grep
"Chair_.*_Seat" across locales) through the kit; the kwik stop and
diner counters/stools through lathe + prism; conifers with more
tiers and a crown blob; make_broadleaf with a multi-blob crown;
heightfield ground under the road sets (needs a ground exemption in
the overlap grammar); Deck verification of everything above. THE PROGRAM'S END STATE: every remaining
blind cue is deliberate — the two road aggregates (re-homing
decision), four cast closeups without char ids, three beats that
happen elsewhere or on a person. NEXT:
cabin_road's 43 and louisiana_road's 18
are fallback-staging aggregates — a re-homing decision (real
locales for those scenes), not a prop wave; verify on Deck first.

**2026-08-19 · PER-STICK VOICE SWEEP VERDICT (voice draft 4).**
Ran the leakage grep (TODO/WIP/placeholder/implemented/deferred/
stub) and a string survey across EVERY stick directory: estuary_4,
northwind_harbor, salmonberry, fey_faire, mrs_wus, tideline,
spiderdrops, earthman, pirate_summer, kwik_stop_manager, estuary
1-3. Verdict: the sticks are ALREADY IN REGISTER ("bosun is not
the limit here" · "you are slightly otherwise" · "the estuary does
not grade on effort") — the only remaining "stub" hits are ticket
stubs, which are diegetic. One touch shipped: Estuary 4's season
status line now speaks its own delta dialect ("the crew %d/5 in
good heart"). Do NOT re-sweep; future voice work should come from
playtest complaints, not grep.

## NEXT SESSION QUEUE (written 2026-08-11 night, session close)

The audit era is consolidated: run_all_audits.sh is green end to
end (0 geometry flags · 0 blind vantages · 18 clips = barn crumple
+ diner ticket tucks) and everything is pushed. The user-side step
is the big Deck rebuild — `godot/tools/blender/list_stale_builds.sh`
prints the exact list — then a lookthrough. In-repo, next session
picks from:

1. ~~**Gauntlet FP wiring gaps**~~ — draft 1 SHIPPED 2026-08-19:
   the gaps were mostly a scene-MAPPING bug (roberts_house pointed
   at roberts_kitchen.tscn; ember_ash_office at houston_office.tscn
   — both remapped to their real locales), 21 computed vantages
   authored across the three locations, and the Wheel's loom +
   tapestry built (they existed only as prose). Draft 2 SHIPPED same
   day: the Ember & Ash warehouse level (graffiti brick, salvage,
   kitchen rough-in, front stair, alley, Marigny sidewalk, the
   corner across) and the circuit's seven stations (St Jude's
   nave, the old armory with its plaque nobody cleans, the
   riverfront state line, and D'Ambrosio's RIVERBOAT — brunch
   floor, table 17 at the stern rail, kitchen pass, staff
   corridor with the time clock). All 35 spaces across the three
   boards now carry FP vantages. Draft 3 is Deck-gated: FP
   walkthrough of all three boards, then wear passes on the new
   sets.
2. **Wear PERSONALITY passes** (tail-wave ledger row): whose feet,
   whose spills — anchor each locale's wear in its chapter prose.
   Read _SET_DETAIL_PLAYBOOK first; one locale deep per visit
   beats five shallow.
3. **Post-lookthrough taste work** (blocked on user screenshots):
   VN framing draft 5, kwik_stop/diner model-chapter verification,
   CP stamp legibility, the four graustark chapter opens, the
   lamplit jog path.

**2026-08-19 · THE VOICE PROGRAM opens (user play-test verdict).**
"The game fiction is still rough and disjointed and doesn't feel
cohesive. The voice of community planned is robotic and sterile
and kinda off putting. Game texts need to be well written,
evocative and suggest a living breathing world. literary and
playful and dark and exciting. slowsticks, too." Draft 1 shipped:
CP's engine frame-lines rewritten into Frasier's ledger register
(dispatch/success/partial/failure/status/caps — numbers kept,
telemetry removed), all 40 problem templates now carry resolution
flavor (the County Seat legal cluster was silent), and two
developer-speak leaks re-fictioned (slowstock stub screen's
"follow-up commit", compass "TODO"). Draft 2 shipped same day:
gauntlet art placeholders re-fictioned ("this card is still
unpainted" — the gauntlet is a physical board, an empty slot is an
unpainted card), Earthman ch2's literal scaffold beats replaced
with AUTHORED BRANCHED aftermath (the beat renderer learned
`text_by` — a beat can branch its text on any _run_state key; the
Murg duel now has three written outcomes in the uncanny-translation
register, and the fire scene stops printing its own stage
direction), Estuary 3's resume screen re-fictioned as the cart's
SERVICE CARD. Draft 3 shipped: the
shelf chrome re-fictioned ("authored on the shelf" → "cases on the
shelf"; "UNLOCKED · not yet fully implemented" → "the cart is out
on loan"; PEEK → OPEN CASE; "FINISHED · yours to replay"), the
main menu's empty-state error re-voiced, and the sweep VERDICT
recorded: KwikStopRoom's register-tape voice, Mrs Wu's, Tideline,
and Spiderdrops all read healthy ("The chest holds five. It holds
five."), the BBS command bars are period-correct modem terseness
(diegetic — do not "fix"), and the 177 stage-choice summaries are
info lines under literary labels (leave them). Remaining targets: stage-choice summaries, region-panel
chrome, per-stick slowstick text sweeps (each stick's system text
in ITS studio's register per the aesthetic bible), BBS system
prompts. The leakage grep (commit/TODO/authored/playable/
placeholder/scaffold — minus diegetic scaffolding) runs in every
voice pass.

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
| Tail-wave locales (~40, 2026-08-03) | 2-3 (22 interiors D2-seeded; the SIX ARCANA SETS ran D4 use-states deep 2026-08-09 — mid-vigil hospice, Natalie's 2am reading, Jimmy's stalled week, the Tower's half-packed boxes, the case files out in Houston, Temperance's drying dishes — plus room-layout fixes: the Devil's bed was inside the kitchenette, armoire inside the sofa, Natalie's stove inside her counter) | per-locale wear PERSONALITY (whose feet, whose spills — the generic pass is scaffolding); D5 through-windows; lighting; reframe |
| Vols 1–2 migration locales | 1–2 | same as tail wave |
| Pit Stop diner / ChillWave (re-themes) | 4 (D2-D6 + strata) | Deck reframe loops (strata retuned to the model diner's vocabulary: lunch/kitchen_practical/dawn_warm) |
| Salty Tome back + alley | 4 (D2-D6 authored) | Deck reframe of three presets + six vn_shot setups; then wear deepening vs the model chapters |
| **Highway 9 (planned community)** | **3** | draft 4: Deck screenshot loops on all six framings + the five vn_shot markers |
| Vol 7 cabin set (cabin_interior + cabin_road) | 3 (hero props 08-12: bowls/crow/drones; wear-personality pass 08-19: Olaf's decades vs Tem's weeks — the two-age wear vocabulary) | draft 5: Deck screenshots of wear + through-window reads (Sitka band S, lean-to/creek strip N — D5 shipped 08-19; cabin_road D2 shipped 08-19: centerline fragments, one truck's tire lines, the parking fan + oil shadow, needle drift, moss seam) | next: Deck screenshot loop, then cabin_road D5 horizon check |
| Lena's apartment (vol7) | 3 (hero props 08-12/19: easel+canvas, nebula+patches; wear pass 08-19: three-years-alone vocabulary — narrow single path, cone rings, paint constellation in HER palette, 61° props, crowding shown in objects not floor) | draft 4: Deck check of easel/mural/window inserts; D3 cords (easel lamp? none yet — she works in window light, verify that reads); bedroom wear |
| Miller kitchen (vol6) | 4 (wear 08-19; D3 infra 08-19: door switch, counter duplexes, under-cab + microwave cords, the landline's OLD four-pin jack low on the wall — the wire predates the remodel — floor vent) | draft 5: Deck check ch6/ch11 opens + through-window reads (garage lit window E, cul-de-sac N — D5 shipped 08-19); sink_light insert at 4:32 mood |
| Slowstick painted art (CORRECTED 2026-08-30) | 3 SHIPPED (THE CORRECTION: slowsticks are sophisticated modern games from an alternate timeline — the 320×200/256c era filter was our-timeline retro cosplay and is retired; all ten scenes repainted at native 1280×720 painterly, loaders drop TEXTURE_FILTER_NEAREST, bible/pipeline/design docs corrected) | draft 4: Deck sign-off on the full-res register; AI-painted sources (modern illustration discipline, NOT 'AI does Sierra') through art_studio.html scene by scene; town/store interiors need the most; remaining studios (pirate_summer, tideline, spiderdrops, earthman, basilica, hane_no_niwa) |
| Cedar tower (vol7 ch22) | 4 (D2 wear 08-19: lobby's single line + chairless desk dust, studio chair spots + one desk's coffee rings, quarters' five-of-twelve seats, and the portal landing where wear STOPS at the door) | draft 5: Deck reframe of the five presets + seven vn_shot setups; D3 cords (rack power, desk cables) |
| Graustark ruin quarter / riverfront park | 3 (per-chapter vantages 08-11: chalk wall / cottage / wreck / wide; ~~ruin cameras untuned~~; ~~park lamp practicals~~ shipped in riverfront.tscn) | draft 4: Deck screenshots of the four chapter opens + the lamplit jog path; then ruin-quarter D2 wear |
| CP region banners + agent busts | 2 (plan SHIPPED — verified in code 2026-08-03: banners incl. county_seat, tower variants, roster + dossier busts) | banner art iteration vs the SVGA bar; authored face overrides for marquee agents |
| CP coherency + presentation (2026-08-04) | 1 (timeline→2025, Faith II dog, demons electronic, type 15px, 25 problem stamps, demon sigils, 4 BGM) | Deck check: stamp legibility at row size + clipped rows at new type scale; ~~THE_BASEMENT threads in the electronic register~~ (shipped 08-09); ~~per-class {agent} stage phrasing~~ (shipped 08-09: body_demon on 12 stages + engine dispatch); ~~mission-text vagueness sweep~~ (ran 08-09: the corpus has grown specific since this was written — all 40 flavors carry named places, times, and objects; nothing to fix, verdict recorded); ~~stamp severity tinting~~ (shipped 08-09: parchment→amber→orange→red-heat modulate at all three stamp sites, thresholds 3/5/7); ~~more BBS 2025-era threads~~ (3 shipped 08-09: the gumbo accounted for · the bench by the gate · late August, the boat — the third-plank fix from memorial_dock_rot echoes into the board with no name attached); NEXT CP visit: Deck-check gates only |
| Northwind Harbor playability | 2 (onboarding pass) | Deck-verify the first five minutes actually teach; then mornings 2-6 pacing |
| Slowstick manuals + packaging (NH = model) | 1 | era-voice + walkthrough sweep across ~20 sticks; box art after experiences are good (task #234) |
| VN portrait busts (de-blocking · 2026-08-04) | 2 (EPX×2 + soft finish; hide-ghosts made ephemeral) | screenshot check vs the SVGA bar; if still chunky: raise the 60x64 base canvas itself (more shading ramps, finer features); dialogue-box busts + CP roster inherit automatically |
| Scene direction · coverage rotation (2026-08-04) | 5 (28 locales carry decks — 111 authored setups, 176 markers repo-wide; draft 5 gave TEN ARCANA SETS the exact markers their scripts already cue (round 2: cafe_olimpico, both new_orleans rooms + the office — 42 arcana markers total; graustark deferred to the richer stub) — Alice's rose/chair/closeup, Natalie's turntable/card, Jimmy's sofa, Elicia's desk/laptop/teacup, Erica's office, the Montreal notebook — plus establish_b rotations, ALL euler-form now: the 81 matrix markers were converted after draft 3 found the transpose bug. Draft 4 covered the whole 7-9-use tier incl. kwik_stop B/C and the shared missing_link_exterior/shuttle_bench deck) | Deck screenshots — every framing is math-verified to <0.5° but ZERO have been seen through a lens; taste notes ("finn B too low") drive draft 5. Next tier (5-6 uses: foxhole_bar, henderson_garage, faust_bedroom, jesse_bedroom, centro_break_room, bianca_kitchen_morning, diner_interior variants) only after a taste pass confirms the grammar reads |
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

**2026-08-08 · recorder calibration + wave 4 (hero furniture).**
The audit's box recorder was treating builders' `size` argument
(full extents) as half-extents — every plain box measured 2× for
the audit's whole first life. Fixed; all 101 builders re-measured
at true extents; still 0 flagged (the stump fixes hold under the
honest metric). Then de-Minecraft wave 4: 118 make_box→
make_chamfer_box swaps + 4 blob conversions (finn's duffel, the
bakery flour sacks) across the 14 decked interiors — targeted at
the hero objects the new insert shots frame from ~1m. Ledger
detail in the 3D playbook. Wave 5 candidates: chamfer sweep for
the 5-6-use tier once it earns decks; harmony/riverfront sphere-
helper retirement stays deliberately deferred (zero visual delta).

**2026-08-09 · THE CLIPPING HUNT (user: "gas and go objects are
clipping through each other at odd angles").** New gate:
`godot/tools/audit/prop_overlap_audit.py` — records every emitted
box/cyl (shared _props helpers AND vendored model-chapter copies),
reports pairwise interpenetration with intentional-contact filters
(same assembly, wall embeds ≤0.12m, container contents). Found and
fixed in the Gas & Go: the beer fridge was INSIDE the locker bank
(0.55m), the entire locker row FACED THE WALL (every door/handle/
vent/plate buried in plaster), cig shelves ran through the office
glass, a ceiling tube crossed the partition corner, the stool was in
the counter. nexcorp_fueling_station audits clean. Next pass:
execution-fidelity work so the tool can sweep composite builders
(kwik_stop reports 291 pairs that need triage — its build_* fns
may mis-run when called blind; teach the tool per-builder
entrypoints before believing repo-wide numbers).

**2026-08-09 later · THE SWEEP THAT FOUND THE DEAD CODE.** Teaching
the overlap tool to run each builder's canonical main() (instead of
calling build_* alphabetically) surfaced something much bigger than
clipping: **three whole classes of silently-broken builders.**
(1) All 14 exteriors patched in the 2026-08 horizon wave had
`build_horizon_2026_08()` defined AFTER the `if __name__` gate —
Blender executes top-to-bottom, so main() ran before the def
existed: NameError, no export, stale GLB. THE ENTIRE HORIZON WAVE
NEVER LANDED ON THE DECK for: bar_exterior briar_falls cabin_road
carnival_lot cedar_tower cliffside_circus grunion_beach
little_switzerland missing_link_exterior riverfront roadside_chapel
sapo_falls school_field_evening skatepark. Gates moved to EOF; a
check_gate_position() guard now runs in the geometry audit so the
class can't recur. (2) ben_bedroom used undefined COL_WOOD (crash),
(3) roberts_kitchen used CEIL for its CEIL_Z (crash),
riverboat_interior called a make_sphere_low that never existed
(crash — now vendored). All three fixed + verified headless.
Clipping triage backlog (full-main()-run numbers, trustworthy):
kwik_stop 291 (model chapter - triage w/ screenshots before
believing), new_orleans_office 67, wgur_transmitter_shack 66,
faust_apartment 60, foxhole_bar 46, henderson_porch_front 34,
solenade_garden 34. riverfront/diner/graustark report through the
partial-run fallback - numbers NOT trustworthy for them yet.

**2026-08-09 later still · CLIPPING TRIAGE ROUND 1 — the game's #1
locale had a house inside the gas station.** With the natural-contact
grammar tuned (crown-drape ≤0.35m, non-solid volumetrics, plant-on-
plant, wires-on-poles, wheels-on-ground, seating, joints, 4cm floor),
the trustworthy finds got fixed:
- louisiana_road (37 uses, most-seen bg): HouseE_2 stood INSIDE the
  gas store (3.5m deep) — moved north of the station; the parked car
  was crosswise with its nose in HouseW_1's porch posts — now along
  house 0's driveway; a mile marker + the mailbox stood inside the
  STALLED SEDAN (the shot_insert_sedan hero); three cypress trunks
  ran through awnings and the gas canopy; the signal mast pierced
  the canopy slab; sprinkler heads sat inside a tree butt and a
  house wall. ALL CLEAN NOW (2541 objects, 0 clips).
- faust_apartment: desk stood inside the kitchen counter (same
  west-wall stretch) — moved to the east wall north of the window;
  cupboard clipped the mirror cabinet — narrowed + shifted.
- foxhole_bar: 6m bar ran into the stage zone; DJ booth 0.55m inside
  the PA sub; trusses through the deck edge; westmost stool ON the
  stage; bottles into the neon — bar shortened east, everything
  reseated. CLEAN.
- crumpled_barn's 19 'clips' are the crumple itself (fallen roof
  through posts) — correctly left alone.
Remaining triage: kwik_stop 263 + bungalow/parish/carnival etc. need
the same treatment; model chapters get screenshots first.

**2026-08-09 lookthrough round 2 (user screenshots + notes).** Fixed
this wave: (1) THE FOOTBALL FIELD REBUILT AT TRUE SCALE — was a
20x14m toy with goalposts standing inside the playing surface; now a
real 120yd x 53 1/3yd HS gridiron (yard lines every 5yd, yard-ticks
at the HS inbound lines, abstract numbers, mow stripes, goalposts ON
the end lines at regulation size, 8 corner pylons, 36m stands, six
18m light poles, scoreboard past the north end zone; tscn floods
moved to the new poles; all 4 vn_shot markers re-authored).
(2) GROUND PLANES: louisiana got 2500m of swamp floor + a standing-
water sheet east (the "floating black slabs" were bands with no
terrain under them); cabin_road got an Oregon duff floor + a 66m
asphalt approach (was a 6m stub starting at the lens) — which also
begins the roads-look-identical fix (green swamp floor vs red-brown
duff). Overlap grammar grew: buried infrastructure, conifer species
names, per-name crown/lobe parts.
FIXED SINCE (2026-08-09 continued): the football field grew a
practice scrimmage (players = the scale reference); cliffside got
its tall cliff / anchored bunting / arch / kiosk / bandstand; the
Emperor was the missing riverboat GLB (rebuild fixes it); the
punch-in dolly-into-walls bug was betraying EVERY well-authored
arcana chapter (zoom now, wide restores preset); Sapo Falls is
veils/streamers/foam-mounds/mist-blobs; the store-ceiling flicker
was grid+stains EMBEDDED INSIDE the ceiling slab, z-fighting its
underside — fixed in the SHARED make_ceiling (every interior) and
kwik_stop's vendored copy. Rebuild-on-next-touch applies the
ceiling fix per locale; kwik_stop + centro first.
STILL OPEN (tasks #3-8): gas & go aisle product jumble + punch-in
landing inside shelving; cliffside_circus identity; floating bunting
at the camp main building; ground planes for the REMAINING exteriors;
the Emperor scene black/empty; arcana scenarios 3+ production pass.

**2026-08-11 · FULL-COVERAGE CLIPPING AUDIT (draft 3 of the gate).**
The recorder stubs grew object fidelity (`_obj_stub`: recorded
objects answer .data/.scale/item-assignment/list-indexing) and now
**all 110 builders run their canonical main() to completion — zero
partials** for the first time (graustark/riverfront/diner previously
measured through the crash-fallback path). Cost: riverfront went
141→4639 recorded objects and the O(n²·regex) pair pass sat for
minutes — flags are now hoisted per-name + x-axis sweep-and-prune;
--all completes in ~1 min. Grammar draft 3 (calibrated against the
diner, the model chapter): funnel/stack through decks+ceilings,
tubs-in-sinks, ruins-as-rubble, scrub-as-vegetation, sinkhole-as-
geology, stanchions-as-structure, wall-x-wall joins ≤0.30, seat-
tucked-under-surface ≤0.30. Diner 130→64, graustark 9→2 (benign
hull/paddlebox residual).
TRIAGE ROUND 2 SHIPPED (2026-08-11, same day): repo 1693 → 1155.
Seven locales taken to CLEAN — real finds fixed:
- roadside_chapel: Ground_Far floated 1m ABOVE local grade slicing
  all 80 cane stalks (dropped below the cane field at -1.08); cane
  grew through the asphalt apron (placement skip added).
- parish_cemetery: THREE prop groups (Beatrice lectern + 22 names,
  the tonight-list lectern + missal, the parish register) were all
  buried inside the SOLID mausoleum body — every session furnished
  a "vestibule" that is solid stone. All three now flank the south
  door. Lampposts ±2.0 stood inside the mausoleum walls (→ ±3.6);
  two oaks were 0.35 inside vault caps.
- briar_falls: the picnic shelter overlapped the restroom building
  wholesale (loose table + post INSIDE it — shelter moved west);
  vending machine sunk 0.37 in the wall; brochure rack sunk 0.2
  into the east end; pine through the shelter roof.
- pit_stop_interior: the exterior pickup was parked THROUGH the
  west wall with its bed among the booths (moved 0.7 west).
- cosmic_comics: longboxes 0.14 inside case fronts; statue tower
  in the new-arrivals table; bin row grazing it.
- carnival_lot: the milk truck stood ON Lavelle's sedan at the
  gate (moved down the highway); carousel/wagon parts renamed into
  their assemblies.
- bungalow: bookshelf ran 0.35 THROUGH the mid partition into the
  bedroom (shrunk to the wall's north segment); walls renamed
  Wall_* so the grammar sees them; studio desk decluttered (laptop
  closed at left front, headphones right front — the Priestess CRT
  pair owns the center).
Grammar draft 4: rock-roots-in-ground, flexible-lines/drapes ≤0.25,
offerings ≤0.10, wheels ≤0.30, portico/pediment, steps+caps as
surfaces, win_/outlet/plate as wall furniture, EMBED_MAX 0.14,
falls?_ nonsolid, walk as ground.
REMAINING: riverfront 562 (backdrop-massing decision first),
kwik_stop 139 (screenshots first), diner 56 (candidates: ServiceBar
x Sideboard 0.48, paddlewheel spokes 0.5 under the road, Booth_1 x
Galley_Expo), centro_grocery_aisle 22, skatepark 21,
riverboat_interior 21, houston_office 18, frog_knows_best 18,
crumpled_barn 15 (the crumple — leave). NOTE: these builder fixes
are invisible until each locale is REBUILT on the Deck.
2026-08-11 addendum: hooking harmony_terrain's vendored
_make_box_local/_make_cyl_local made the game's BIGGEST locale
measurable for the first time — 8,863 objects, 110 clips. Also
shipped: a one-shot preset-vantage check (scratchpad
preset_vantage_check.py pattern); graustark was the only
aimed-at-nothing vantage; all six highway9 presets see geometry.
2026-08-11 later · HARMONY TRIAGE SHIPPED: 110 → 0 CLEAN. Real
finds: TWO pole signs planted inside buildings (SelfStorage sign
in the office, BigBox sign in the dept-store shell); ALL rooftop
mech at wrong absolute z (spec ignored terrain — NexCorpHQ's six
units were INSIDE the tower at level 1: now mesh+height, and the
SelfStorage mech line re-aimed onto row 1 clear of the office);
the pool change room built ACROSS Harmony Blvd overlapping the HS
bus stop (now west of the pool); Birch house k2/+1 stood inside
OTPark on the lamp + drinking fountain (skip_slots); the cart
corral occupied parking stall 9 with car 7 parked through it (lot
east margin); P2Main mailbox #3 stood in House C's parked car
(cadence skip); a wild tree through the HSField bleachers; the
cemetery's col-0 stones in the church east wall; a DUPLICATE
fluorescent grid (Fluo pass removed in favor of FloLight);
gum stands in the propane cage line; mag rack in the laundromat
partition; newsboxes in the ATM. Grammar draft 5: Roof_<Bldg>
prefix aliasing, BERMISH ≤0.65, hedge-holds-post ≤0.35,
slab/plaza/endzone as ground. Repo total 1118. NEXT: riverfront
544 (decision), kwik_stop 133 (screenshots), diner 54, then
centro_grocery_aisle 22 / riverboat_interior 21 / houston_office
18 / frog_knows_best 18. Deck rebuild needed: harmony_terrain.
2026-08-11 later still · TRIAGE ROUND 3: twelve more locales CLEAN,
repo 1118 → 843. Real finds: centro's frozen bank stood IN the dry
aisle + its chest freezer was SPLIT (body at y-3.4, lid+kick at
y-2.0); asylum's Bishop's-letter hero prop lay INSIDE the nurse
counter (desk_z 0.90 vs counter top 1.10) and ward 5's bed was
shoved through door 4's leaf; mixing_glass's U-bar arms ran y 4.4-
7.6 swallowing booths 2-3's tables (arms shortened, banquette
packed); cosmic back-office longboxes in the fridge + safe;
little_switzerland pines inside chalet walls (now behind the row);
caldwell's headphone cups sunk in the desk slab + monitors on the
board edges; break-room fridge in the counter run. Grammar draft
6-7: water is nonsolid (aquarium/swamp), shrink-wrap + pallets +
counters contain, forks enter pallets, poured skatepark features
merge (hump/coping/basin), Part[NSEW] walls, stair members through
uncut slabs ≤0.40, mounted fixtures ≤0.20, mirror collage ≤0.10,
soft-foliage nestle ≤0.15, boards/consoles are surfaces.
REMAINING BIG THREE: riverfront 544 (decision), kwik_stop 133
(screenshots), diner 54 — then a long tail of ≤10s. Deck rebuilds
this round: cosmic_comics_back_office asylum_ward_c
centro_grocery_aisle riverboat_interior houston_office
frog_knows_best mixing_glass little_switzerland centro_break_room
caldwell_radio_room_night.
2026-08-11 final round · THE TAIL IS DONE: every non-gated locale
in the game audits CLEAN. Repo 843 → 597, and 592 of those sit in
the four known holdouts (riverfront 450 · kwik_stop 80 · diner 48
· crumpled_barn 14 — the crumple). Best finds: cedar_tower's
folded-clothes story prop was INSIDE the solid bunk frame (now on
top); roberts_house bed 0.35 through the north wall; daigles'
AA-meeting chair ring stood in the bar (ring moved + rotated);
henderson's truck parked overlapping the car by 2.4m (moved to the
curb ahead); the gym's deadlift bar ran under bench 1; montreal's
bookshelf and kitchen double-booked the same wall stretch. Grammar
drafts 8-9: contents press into containers ≤0.25, cushions/
pillows, swing-rope-through-canopy, roof-members-join, cues lean,
ducts run along bands, sand/shore/hills as terrain, knee braces +
pipes as structure, vending/warmers/domes/nightstands contain.
NEXT DRAFT: riverfront backdrop decision → kwik_stop screenshots →
diner candidates; then this gate goes into run_all_audits.sh as a
zero-regression check.
2026-08-11 night · RIVERFRONT 450 → 0 CLEAN + the gate is LIVE.
run_all_audits.sh now ends with the prop-overlap zero-regression
gate (holdouts: kwik_stop 90 / diner 55 / crumpled_barn 15 — never
bump a ceiling; fix the builder or extend the grammar). Riverfront
real finds: BOTH armory/old-church silhouette passes were built
INSIDE the detailed strip mall (Armory_Tower fully within it, the
mass crossing River Road) — whole silhouette layer moved 20m west
behind the frontage, skyline blocks west of that; THE PADDLEWHEEL
WAS ROTATING ABOUT THE WRONG AXIS (blade circle in XZ instead of
YZ — every revolution swung blades 1.1m through the stern into the
dining room; wheel reframed about the X axle + moved 0.6 aft);
roadside tree ty=-28 slipped an exclusive bound into the gas
station store; SpeedLimit_S stood inside bridge pier 0; lobster
trap 2 in a fuel drum. Grammar draft 10: BACKDROP x BACKDROP
(oppo/far/shore/skyline/masses/billboard/far-bank groups), vessel
superstructure joins itself, terrain-water-bank interlock,
grounded-object rule (proud of the ground sheet = standing, not
clipping), pier abutments, plant-strip berms, stilts as structure.
Graustark draft 3 also shipped: Hermit/Star/Judgement/World each
open on their own staging (chalked wall / cottage gate / Minstral
wreck / the wide). REPO TOTAL: 1693 this morning → 132 tonight,
all inside the three model-chapter holdouts. Deck rebuild:
riverfront (the wheel + silhouettes are geometry).
2026-08-11 last · THE HUNT IS COMPLETE: kwik_stop 67 → 0 CLEAN and
diner 48 → 4 (ticket-tuck ≤0.06). REPO TOTAL: 18 — barn's crumple
(14, by design) + the diner tickets. Kwik finds: the mag rack
stood inside the ice machine (west wall double-booked → rack
north), the pickup was parked THROUGH the propane cage (a lane
out — then its cab hit a canopy column: slid east between them),
the ice chest in the blue news rack, the quarter-machine row ran
through window-table 2's chairs (now against the glass), charcoal
pyramid + floor plant + endcaps + cup stack all rearranged out of
each other. Diner: its wheel had a THIRD wheel bug (fore-aft
offset computed and never used — blades stacked in a vertical
column diving under River Road), and the Damb service bar stood
inside the WestFormal sideboard (now a true 0.85m stub between
partition and sideboard). Gate holdouts now: diner 6 +
crumpled_barn 15 only. VERIFY BY SCREENSHOT next Deck session:
kwik_stop front-of-store rearrangement and the diner stub bar are
model-chapter changes made on audit evidence alone.

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

- **THE PROFESSIONAL PASS (2026-08-30, active) · back-to-front per
  the user's direction** ("the start of each volume has the most
  work done already"). Draft 1 shipped: (a) vn_story_audit.py suite
  gate — every directive resolves; ten never-existing bgm files
  found and authored as beds; index.json treated as runtime truth
  (vol5's shipping TEST scene de-indexed; "End of Demo" re-fictioned
  in four closers); (b) VnSweep.gd — headless traversal of all ~270
  indexed scenes, back to front; (c) beat/mood seeding through the
  vol7 epilogues + ch20-22, vol6 ch19-23 (night chapters were graded
  dawn_warm), vol1 ch4 dream suite + vol2 close. Draft 2 SHIPPED
  (2026-08-31): the whole vol6/7 zero-beat list seeded; vols 1-2
  directed end to end (63 scenes, beats + moods + first panels);
  mood-clock audits across vols 6-7 (lunch-at-dusk class, 8 fixed);
  three unwinnable choices + three dead skill checks found by
  VnSweep and fixed; ten silent chapters got authored beds; the
  Fool's eight ending CGs repainted 320x200-era → 1280×720; four
  kinetic-text seeds; panels for the bill note / three
  instructions / Diego's letter; 56k-error portrait-loader guard.
  Draft 3 targets: Deck feel pass on ALL of it (beats, ice /
  lithograph / chillwave grades, the dark river-window CG); other
  arcana boards' end screens are text-only — a CG program like the
  Fool's if wanted; vols 3-4 need locales before direction; stage
  grammar still gated on character GLBs (gate 2); kinetic seeds
  expand only after Deck sign-off.

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
- **P0 · Painted-art retrofit pilot** (gate 1) — CORRECTED direction
  (2026-08-30): full-res modern painted illustration at 1280×720, NO
  era filter (`svga_quantize` retired — it was our-timeline retro
  cosplay). Pilot on Salmonberry (title + 5 endings), then sweep the
  catalog studio by studio. The old flat-vector HeroImage scenes
  remain only as fallbacks.
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

- **THE ENDING-CG PROGRAM — HALTED BY USER VERDICT (2026-08-31):
  "don't waste time doing art. you aren't good at it. game design
  and coding."** This closes ALL Claude-side procedural art
  authoring (scene_painter compositions, CG sets, painted
  backdrops). The four shipped boards stay as placeholders; the
  data-driven cg-path mechanism stays (any art source drops in
  with zero code). Future art comes from the user's tools (gate 1:
  ArtCraft / image-gen) or not at all. Claude's lane: game design,
  systems, engine code, QA, writing. (Original program row kept
  below for the record.)
- **the ending-CG program (2026-08-31, halted · record)** —
  _win_cg_path/_loss_cg_path are data-driven now: art drops in at
  assets/cg/gauntlet_<arcana>_<id>.png, zero code. Scope: 64 win
  thresholds + 97 loss finales across 22 boards. SHIPPED: Fool (8,
  original filenames), Magician (10), Priestess (7), Empress (7) —
  the vol5 opening trio complete. Method: compose from each
  ending's own prose; visually REVIEW every render before shipping
  (three pareidolia strikes and two floating-object catches so far
  — symmetric circles + a vertical WILL become a face; a tabletop
  needs its cloth drop). NEXT: Emperor, then down the arcana order.
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
- **SHIPPED · Screenshot mode** — verified built 2026-08-31
  (GameEngine._toggle_photo_mode: letterbox bars, dialogue/HUD/
  choices/auto-chip dropped with restore, cursor hidden, backlog
  closed, timed-advance fenced). This row was stale.
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
