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
the overlap grammar); Deck verification of everything above.
DRAFT 4A shipped: six more rooms' tables and chairs through the
furniture kit (henderson, cabin — turned pedestal, seven chairs with
the ring opened toward the partition — centro, roberts, lena, pit
stop), every swap keeping the original prefix. DRAFT 4B shipped:
conifers with five jittered tiers and a leader, broadleaves with
three to five two-green lobes and two tube limbs (seven builders).
STILL QUEUED: the diner's and kwik stop's stools and counters through
lathe + prism (model chapters — Deck-verify the chamfer policy on
them FIRST); riverboat_interior and daily_grind chairs (cylinder
seats — a stool-style variant of make_chair); hospital_room's
metal-armed chair; salty_tome's wing chair (a shaped prism back);
the two unmeasured Harmony builders; heightfield ground. THE PROGRAM'S END STATE: every remaining
blind cue is deliberate — the two road aggregates (re-homing
decision), four cast closeups without char ids, three beats that
happen elsewhere or on a person. NEXT:
cabin_road's 43 and louisiana_road's 18
are fallback-staging aggregates — a re-homing decision (real
locales for those scenes), not a prop wave; verify on Deck first.

**2026-09-07 · THE TRIP · DRAFT 1 — "realism but trippy, at all
times, in lines and backgrounds, synced to the music."** A new
autoload, TripSync, plus one screen-space shader, trip_sync.gdshader.
The autoload reads the BGM bus spectrum analyzer (eight log bands,
adaptive gain so a quiet drone drives as hard as a loud track),
detects beats on the low band, keeps a tempo estimate from the median
inter-beat interval, and pushes the music state to every attached
material each frame. The shader keeps the picture real and rides four
things on it: a rainbow aura along the Sobel edges (hue runs along
the line, brightness follows energy, the beat flares the glow); a
domain-warped noise field breathing the FLAT regions by a few pixels
(suppressed where edge density is high, so outlines and text stay
sharp); a capped YIQ hue drift plus a mid-band saturation lift; and a
beat-launched radial ripple with a short chromatic split. Mounted
two ways: a global layer-60 CanvasLayer ("world_render", F4 leaves
it) over every locale walk, slowstick and menu; and in texture mode
on the VN's background TextureRect and 3D SubViewportContainer while
GameEngine is in "trip_local" (the global layer steps aside so the
dialogue box is never touched). Dial: Settings.trip_amount, the
PSYCHEDELIA slider in the settings overlay (default 0.6; 0 = off).
InGameMusicPlayer moved to the BGM bus so user-dropped tracks feed
the analyzer. NOTHING HAS BEEN SEEN ON THE DECK. DRAFT 2 TARGETS: the
mix itself — is 0.6 too loud for the VN, does the ripple read as a
ripple or a wobble, does the line aura cheapen the model chapters;
per-mood scaling (a `trip_scale` key in the mood presets so linework
and lithograph moods dial it down); per-surface scaling for the main
menu and the slowstick TV (a "trip_soft" group at ×0.45); a beat
detector check against the real catalog (the bass-onset threshold
was set blind — log bpm from status_line() on three known tracks);
a second look for the ripple centre (a vn_shot subject, not a
random drift); the hue drift into the lighting (practicals breathing
with the bar like lightshow_extreme does, at 10% of that); a
kaleidoscope peak state gated to [mood:] cues for the trip chapters.
DRAFT 1B shipped (same day): per-mood scaling — MoodCycler._apply
pushes 0.35 under neon-1.0 / ascii-≥0.5 moods (or the preset's own
`trip_scale`); a "trip_soft" group at ×0.45 (the main menu joins it);
the DebugHUD prints TripSync.status_line() (dial · mood × · surface ×
· bpm · energy · bass · pulse) so the beat detector can be read
against a known track. Still blind until the Deck sees it.
DRAFT 1C shipped (same day, user direction: "slowstick games too ·
Jeff Minter design and visuals · only current hardware · and game
design · Major Arcana swampy + arcade · Planned Community retro
games, zines, stoner sludge meta punk · Milk and Honey SCUMM,
psychedelic wall-of-sound classic rock but sci-fi"): the REGISTER
system — five named dial sets in TripSync.REGISTERS (base · arcana ·
community · milk_honey · slowstick) with per-register palette
(rainbow / swamp phosphor / riso duotone / liquid light / neon
vector), sparks, photocopy grain, cabinet flicker, the Minter thump
and a per-register pulse decay; an owner stack so a host's register
pops when the host leaves the tree; pushes from GameEngine (by
volume), TarotGauntletGame, CommunityPlannedGame and SlowstickLook.
lore/_PSYCHEDELIC_DESIGN_BIBLE.md holds the doctrine and each
pillar's GAME GRAMMAR queue. GAME DESIGN HAS NOT SHIPPED — the
bible's grammar column is the queue: gauntlet attract mode + chain
multipliers + tempo-as-difficulty; CP's BBS as the zine's letters
column + pressure curve as tempo drops; a verb coin on the cabin
chapter; a Minter bonus round in one stick; a feedback-trail
SubViewport for the slowstick register; TripSync raising its layer
above Pirate Summer's layer-90 console.
DRAFT 2 shipped (same day · Deck verdicts "that's mostly nausea
inducing" then "I like it, but it's rough"): THE MOTION RULE — the
image never moves. Every UV displacement (flat warp, beat ripple,
Minter zoom thump, chromatic split) and every whole-frame
brightness change (cabinet flicker) removed; the beat is a ring of
LIGHT on the lines; hue drift capped ±0.35 and the colour clocks
run at a third of draft 1's rates; three-scale soft Sobel so the
aura stops reading the dither as speckle; screen blend instead of
add; a 45 ms attack on the beat envelope; default amount 0.45.
DRAFT 3 TARGETS: Deck taste pass per register on the still
picture; the aura's hue banding width (q·0.08 — wider or narrower);
whether the zine duotone's hard ink step reads as intent or as
aliasing; sparks density in milk_honey; then the GAME GRAMMAR rows.
DRAFT 2B shipped (Deck verdict on 2: "needs to be way more subtle,
3D backgrounds are on the right path, slowsticks are ugly and
strobey"): default amount 0.25; the aura is energy-led with the beat
at a tenth of its weight and the ring of light at half, so a fast
track cannot strobe; hue drift capped ±0.26; sparks are slow sine
fades (no gating, no beat flash); the slowstick register is now the
FAINTEST of the five (lines 0.30, no wash, no sparks) — the Minter
look belongs inside each stick's own rendering (particles, glow), a
per-game render task, not a screen overlay. DRAFT 3 TARGETS: the
3D-background register per volume on the Deck (that is the path
that works); the slowstick overlay may go to zero if it still reads
at 0.30; Minter-in-the-game for one stick (its own particle glow,
its own beat-lit lines) as the first GAME GRAMMAR row.
DRAFT 3 shipped (Deck verdicts on 2B: "lost all the best parts" ·
"didn't tone it down so much as strip it completely" · "still too
muted, find a balance"): the liquid is back as a near-constant,
never-beat-synced drift (6 + 6·energy px, open regions only, a slow
field); draft 1's colour and line weights restored (hue cap ±0.55,
aura 0.30 + 0.62·energy + 0.45·kick + 0.9·ring, wash 0.11); default
dial 0.6; the registers back at their 1C weights (slowstick at a
middle: lines 0.65, no flat motion, no sparks); FOUR MIX SLIDERS in
settings under PSYCHEDELIA — FLOW (0 = still) · LINES · COLOUR ·
BEAT — persisted as Settings.trip_flow/lines/colour/beat. DRAFT 4
TARGETS: read the user's slider positions back from settings.cfg
after a session and bake them as the defaults; per-register FLOW
(the sticks at 0, milk_honey highest); the ring's centre on the shot
subject; Minter-in-the-game for one stick.
DECK VERDICT on draft 3 (2026-09-07): "The cabin in Land of Milk and
Honey is looking great, seeing good work all over with the background
geometry. That's the right path, it's coming along better now." So
the vol 7 register on the cabin set (cabin_interior + cabin_road at
detail draft 4, THE TRIP milk_honey at draft 3) is the current
REFERENCE POINT for the whole program — tune the other registers
toward how that reads, not toward their own numbers.

**2026-09-07 · THE DECK SESSION · "the world is a huge mess."** One
evening of Deck screenshots, in order: the diner's first shot a yellow
field with a door sliver · "what is that weird object in the middle
of the diner bar?" · "cars don't park in the middle of streets. this
keeps happening." · "what are these blue rectangles in front of the
home?" · "lots of clipping on beds and weird pillow designs" · "weird
broken overlapping geometry all over the place. comic shop." · "an
exploded office chair facing the wrong direction away from the desk
… a desk in the center of the room" · "real bad shot direction all
throughout the latter half of major arcana, just poor." · "movement
on pirate summer still totally busted."

ROOT CAUSES FOUND (the tooling had holes, not just the content):
1. 198 of 589 vn_shot markers are written in `position =` form and
   were INVISIBLE to marker_aim_audit and marker_reaim (both read
   only `transform =`). The diner's clock insert faced 180° from the
   clock with a green audit. Both tools now read both forms.
2. The subject matcher split names on "_" only — "clock" never
   matched "WallClock_Face". CamelCase now splits; sixteen insert
   cues had no synonyms at all (deckwall, meatcase, speak_and_spell,
   oneway, setlist, wreck, bed, hotsauce, record_player, ceiling_fan,
   bourbon, longboxes, scoreboard, bleachers, radio, boxes) — added;
   an EXCLUDE table stops "door" landing on a fridge door and
   "photograph" on a door frame; duplicate SYNONYMS keys silently won
   (the dict literal kept the LAST) — deduped.
3. An INSERT whose subject could not be resolved fell through to
   "anything in a wide cone" and PASSED. Unresolved inserts now fail
   (KNOWN_UNRESOLVED prints WARN: cabin_road's crow lives in
   cabin_interior).
4. No tool ever cast rays from a MARKER. vantage_obstruction_audit
   --markers now runs the fan over all 589 with SUBJECT-AWARE
   verdicts: OCCLUDED (five rays lens→subject blocked by a non-
   subject), camera INSIDE, EMPTY (sky/far only ≥ 80%). First run:
   128 real defects — 92 occluded, 16 inside a bookshelf / seat back /
   partition, 12 sky. NEW TOOL marker_reframe.py searches rings
   around the subject (5 distances × 24 yaws × 5 elevations, not
   inside anything, occlusion-free, nearest to the author's original
   position) and rewrites position + aim: 110 reframed over two
   passes, 19 STUCK (no clear position — the prop is behind a wall
   from every side; those need the prop or the cue to move): cabin_road
   drone · cape_perpetua hexagon · cedar_tower credit · centro_stockroom
   smear · cosmic_comics_interior oneway · daily_grind tower ·
   graustark wreck + smoke_ring · henderson basement · jesse phone ·
   lena window · maya board + floorboards + envelope · new_auburn
   cypress · new_orleans_office window · new_orleans_room mirror ·
   riverboat window · school_field scoreboard. Marker gate: 128 → 41
   (a zero-regression ceiling in run_all_audits); aim gate: 0 misaims.
5. prop_overlap_audit exempts same-prefix parts as one assembly, so
   a pillow through its own bed, a chair back floating off its seat,
   and stacked desk papers were never reported. NEW TOOL
   furniture_grammar_audit.py (informational): INTRA (intra-assembly
   penetration), FLOAT (prop hangs above its support), CHAIR (back on
   the desk side), DESK (top touches no wall), LANE (car centre > 2.2 m
   from the road's edge). Draft 1 confirms the user's eye on every
   case it can measure: Jesse's desk off the wall, the white sedan
   4.4 m into the bulb's asphalt, the futon pillow through the
   mattress.

FIXES SHIPPED: the clock insert moved to the dining floor 3 m off the
clock and aimed; the diner's coffee maker is a pour-over brewer (base,
tower, brew head, two warmers with lathed glass pots, coffee in one)
instead of a 0.5 m steel cube; Meadowlark's sprinkler "translucent"
slabs (this pipeline has no alpha — they rendered as opaque blue
rectangles) are five thin water arcs per head and one surgical stream
for the Miller head; the comic-shop back office desk sits against the
north wall west of the service door with every desk prop carried
along (DESK_DX/DY), the chair's back is on the far side from the desk
on two posts; Pirate Summer's idle-bob anchor resets on spawn (it
carried the PREVIOUS zone's resting Y into the new sprite — Sam drew
at the wrong row until his first step, then tweened across the map);
20 markers re-aimed, 96 reframed.

QUEUE (next passes, in order): (a) the 22 STUCK markers — move the
prop or the cue; (b) cars in the lane: White_Sedan (meadowlark bulb),
plus a repo-wide LANE run; then a `curb_park()` helper in vehicles.py
that snaps a car to the nearest road edge; (c) a shared make_bed()
in _props/furniture.py (frame, mattress inset, fitted sheet, folded
blanket prism, two pillows) and the 24 hand-built beds through it;
(d) the grammar audit repo-wide, then a ceiling per class and a gate;
(e) SHOT DIRECTION vol 5 ch11–21: every preset and marker those
chapters cue through the two gates, then a Deck taste pass chapter by
chapter; (f) highway9's six presets read EMPTY because harmony_terrain
records its props in a frame the recorder cannot place — an
UNMEASURED skip, to be root-caused. Deck rebuild: diner,
meadowlark_circle, cosmic_comics_back_office (the marker changes are
tscn-only and need no rebuild).

**2026-09-07 · THE QUEUE, WORKED ("go ahead and get started on all the
work that needs to get done").**
· MARKERS: an EMBED_TOL (18 cm) in the occlusion test — a window's
  glass sits inside its wall slab, a board on its floor — freed 8 of
  the 19 stuck; the marker gate ceiling is now 17 (128 → 41 → 32 → 26 → 17 with
  harmony_terrain's five markers skipped as unmeasured); the eleven stuck
  are resolved (see THE STUCK ELEVEN below); the 17 left are cast closeups
  with a wall 2.4 m behind the person and two sky-heavy exteriors — taste
  calls for the Deck, not defects (cabin_road drone in the Sitka canopy · cape_perpetua
  hexagon in the fog bank · cedar_tower credit · centro_stockroom
  smear · cosmic_comics_interior oneway · daily_grind tower · graustark
  wreck + smoke_ring · henderson basement door · lena window · maya
  board · new_auburn cypress · new_orleans_office window · new_orleans_
  room mirror · riverboat window · school_field scoreboard — each a
  prop behind a wall from every side or a subject that is not built:
  content fixes, one per pass). Aim gate: 0 misaims.
· THE STUCK ELEVEN, resolved (later the same day): a `--why` mode on
  marker_reframe tallies why every candidate position fails. Six of
  the eleven failed ONLY the 2.6 m eye clamp — the drone in the Sitka
  crowns, the credit poster, the stockroom's thermal smear, the watch
  tower, the motel sign, the helm window on the upper deck, the
  scoreboard: the lens may now climb to 1 m below a high subject and
  look up at it, and rings widen to 13 m for subjects over 3 m. Fog
  banks, foliage tiers and blob lobes, shrubs and spray are PASSABLE
  for a lens (the hexagon in Cape Perpetua's fog, the drone in the
  canopy). Two were CONTENT: the Frog King's smoke ring sat inside
  the Minstral hull's bounding box (moved to his mouth, outside it)
  and Henderson's fridge stood square in the basement doorway (moved
  north along the east wall). One was a DUPLICATE marker name in
  henderson_kitchen.tscn — two shot_insert_table nodes, the tools
  editing the first while the gate judged the second; the stale one
  is gone and duplicate names are now something to scan for. Graustark
  and harmony_terrain are NO_EMPTY (heightfield meshes the recorder
  cannot see make "only sky" an artifact). The reframe now accepts a
  position only if the gate would (occlusion AND sky re-tested from
  the final spot), so a marker can no longer oscillate between the two
  tools.
· CARS: `curb_park()` and `bulb_park()` in _props/vehicles.py; the
  white sedan through make_car at the bulb's south curb; Finn's truck
  to the store-side curb of Main Street. The LANE check now excludes
  lots / aprons / frontage strips and measures cul-de-sac bulbs
  radially: LANE 11 → 0 repo-wide (the other nine were cars in
  parking lots).
· BEDS: `make_bed()` in _props/furniture.py — frame / platform /
  captain / futon / hospital, every layer ON the one below, pillows
  on the sheet, a made blanket with a rolled edge or a heap. Seven
  beds through it (graciela, diego, new_orleans_apartment, hospital,
  faust, jesse's futon, sam's captain's bed), then the second wave:
  ben (head to the E wall), coach_k (under the two sleepers), bungalow
  (unmade heap), lena, natalie's nook, new_orleans_room, safehouse,
  maya, hospice (hospital style) — 16 beds through make_bed. Hand-
  fixed in place because their shape is the point: finn's raised
  platform on posts (comforter and pillow lifted onto the mattress),
  kai's floor futon (layers onto the mat), simon's rumpled single,
  the cabin daybed (blanket off the bolster) and east-room bed, the
  lighthouse bunk, the asylum gurney, the nightmare cot, the Roberts
  bedroom peek. LESSON: a bed that hides something UNDER it (Maya's
  loose floorboard, the safehouse floor books) must be the open
  "frame" style — the solid platform occluded three inserts at once.
  make_bed next-pass targets: a raised head section for the hospital
  style, a tall-post platform style for Finn's, quilt patterns.
· CHAIRS: numerically confirmed — the back sat on the TABLE side in
  daigles' meeting ring (11), the daily grind's cafe pairs (4), the
  riverboat's card table (5), Tem's vigil chair, the safehouse desk
  chair. All flipped. The matcher learned: side/end/night/coffee
  tables are not seating targets, a chair is fine if it faces ANY
  table within 0.95 m of its seat, `Z_` zone outlines are not tables.
  CHAIR 36 → 2 (finn's perch, new_orleans_room — to inspect).
· DESKS: the six template bedroom desks (jesse, sam, diego, kai,
  maya, finn) to their walls (13 cm off the N wall for the back-edge
  clutter; Maya's end-on against the E wall because her bed owns the
  N window); pit_stop_office and the Caldwell broadcast desk to the N
  wall; the comic-shop desk (earlier). Freestanding BY DESIGN and
  allow-listed: the judge's bench and clerk's desk, the helm, the
  newsroom island, Miller's dining-table desk at the rain window, the
  New Orleans executive desk, Antonio's desk, the WGUR console,
  Anya's studio table, the riverboat cat desk. DESK 22 → 0.
· Every changed locale passes the overlap gate at 0 clips.
DECK REBUILD: everything — the furniture and vehicle kits changed
under 20+ builders: `cd godot/tools/blender && ./build_scenes.sh`.
INTRA/FLOAT REVIEW (same day): classified by part type on highway_101
/ diner / riverfront. Ninety percent were bounding-box artifacts the
recorder cannot help — conifer tiers stacked as cones, blob lobes,
fronds and reeds; a vehicle's hub inside its wheel inside its body;
road-bend prism segments meeting at joints; dock pilings in their
stringers. All excluded by class (foliage is PASSABLE, one vehicle is
one rigid body, Road_ prefixes are joints, dock/partition members are
structural). highway_101 INTRA 849 → 0; diner 208 → 87 (stool hubs and
tablecloth-over-pedestal tucks remain — real but sub-4 cm); riverfront
684 → 294 (dock construction, boat parts). The tool stays
INFORMATIONAL: a gate needs shape-aware tests (cylinder-in-cylinder,
cone stacks), not more name lists. NEXT: highway9's recorder gap
(harmony_terrain's heightfield drape — the recorder sees no ground, so
the EMPTY test is meaningless there); then the GAME GRAMMAR rows; then
the Deck taste pass on Major Arcana 11–21.

**2026-09-07 · SECOND DECK ROUND ("this interior is a complete mess"
· "ladders turned 90 degrees" · "chairs not fully assembled" · "cars
still in the middle of streets, looks even worse" · "sprinklers still
look ridiculous, consider particles").**
· LENA'S APARTMENT: the bedroom partition's east reach was a 25 cm
  stub beside the door — a door frame standing in the room. It is now
  a wall with a door AND a cased opening to the couch nook (header
  across the opening, mullion, end post, wood casings). The drop-tile
  ceiling GRID — an office ceiling — is off in 25 residential
  interiors (kitchens, bedrooms, apartments, the lighthouse, Wagner's
  home, the Houston studio); `make_ceiling(..., with_grid=False)`.
· CABIN: the loft ladder stood UNDER the deck at y 3.95 climbing into
  its underside; it stands at the loft's front edge (y 3.50) west of
  the round table now. The kit chair's back posts are rooted inside
  the seat with a gentler rake and a lower rail — "not fully
  assembled" was the raked posts leaving the seat edge.
· MEADOWLARK: every street car through curb_park (north curb: Ben's
  truck, the Corolla; south curb: the patrol car), LANE_M 2.2 → 1.4 so
  a car in a lane centre can never pass again. The sprinklers are
  PARTICLES: scripts/SprinklerFX.gd (a Node3D in the tscn) spawns a
  CPUParticles3D fan at every Sprinkler_Head_* and the thin arc at the
  Miller head, firing in sequence east down the block — the prelude's
  own image. No geometry, no tinted slabs, no tubes.
· NOTE FOR THE DECK: exterior/interior geometry fixes need the Blender
  rebuild (`build_scenes.sh`); a pull alone shows the old GLBs — which
  is why the cars "still" stood in the street after the first fix.
DRAFT-NEXT: Lena's establishing preset re-read with the new wall;
particle tuning on the Deck (count, alpha, throw); a wet-sheen
decal under each fan already exists (Sprinkler_Wet_*).

**2026-09-07 · THE TRIP draft 4 · direction.** User: "scenes need
stronger direction with the psychedelic filter in effect. 75 percent
seems about right for me right now as default" · "whiter or brighter
scenes are too plain and humdrum, it really only looks good on darker
scenes, need a different effect maybe" · "tune per scene and mood as
per director notes." Shipped: default 0.75; a `[trip:X]` chapter cue
(GameEngine directive regex, replayed on load, reset per scene) →
TripSync.scene_scale; `trip_scale` on 26 moods by intent (dark and
dreaming hot, plain daylight cool — the table is in the bible); and
the BRIGHT-SCENE PATH in the shader: where the picture is bright the
aura is coloured ink on the lines and the flats take a multiplied
tint, cross-faded by per-pixel luminance, hue drift ×1.7 on white.
NEXT: author `[trip:]` cues into the model chapters' turns (the diner's
3:47, the cabin's night, the Lena interludes) the way `[mood:]` cues
were placed on interlude beats; Deck-check the ink path on day_bright.

**2026-09-07 · "keep going" · direction seed + game grammar row 1.**
190 `[trip:1.2]` cues placed on the first line after every interlude
card in vols 5–7 (163 files; the story audit validates the cue's
range) — the same structural-turn rule the mood cues followed. The
gauntlet's ARCADE ATTRACT MODE shipped (TarotGauntletGame.gd tail):
45 s idle → banner loop + mood strata cycle + trip 1.3; any input
wakes it. NEXT: Deck-check the attract banner does not fight a modal;
score bursts on chained rounds; the BBS-as-letters-column row for
Planned Community; a verb coin on the cabin chapter.

**2026-09-07 · game grammar row 2 · the letters column.** RUST_CODE
gets THE_LETTERS (letter N, public from W1): nine NEWS FROM HARMONY
CREEK letters-to-the-editor threads, W2–W16, in Maya's zine voice with
F.T. in the sysop's chair — JSON only, per the CP playbook (board_list
+ the_letters.json; every CP JSON validates). NEXT: the verb coin on
the cabin chapter (row 3); Minter inside one stick (row 4); Deck-read
the letters at 14400 baud for length.

**2026-09-07 · game grammar row 3 · the verb coin.** GameEngine:
`{"t":"jump","goto":N}` hops within a scene; choice options accept
`hide_if_flag` / `only_if_flag`; a choice's `style: verb_coin` +
`hotspot` renders as verbs over a named object (ChoiceMenu.present
grew two optional params — same buttons, same number keys). First
coin authored in vol7_ch10_cabin (Per's box on the table: LOOK AT ·
ASK PER · LEAVE IT; verbs spend themselves). Story audit green. NEXT:
coins on the diner jukebox and the kwik stop back cooler; Deck-check
the caps verbs against the IM Fell face at 19 px.

**2026-09-07 · game grammar row 4 · Minter inside Spiderdrops.**
SpiderdropsMinterFX.gd (additive child Node2D) fed by SpiderdropsWeb's
own events: drops → sparks, snaps → white-core bursts, every ten
points → a mote to the HUD bar; the beat pulse lifts the light. This
is where the Minter register lives — the screen overlay stays faint.
All four game-grammar rows now have a draft 1 (attract mode · the
letters column · the verb coin · Minter-in-the-stick). NEXT: Deck
taste on all four; Spiderdrops' storm finale as a light-synth bonus.

**2026-09-07 · the highway9 recorder gap, closed.** Highway 9's
ribbons, guardrails and gantries are built through harmony_terrain's
raw-mesh helper `_finalize_mesh`, which the audit recorder never saw
— six Deck-verified presets audited against nothing. The recorder now
records every `_finalize_mesh` call (eight builders define it) as the
verts' bounding box. Two consequences handled the same hour: (1) a
sloped 50 m ribbon's bbox is a wall to a ray and a clip to every box
under it, so the terrain-following ribbons (asphalt / shoulder /
median / berm / embankment) count as FILL in the ray audits and raw-
mesh boxes are excluded from box-vs-box overlap entirely; (2) with
that, all six highway9 presets pass, harmony_terrain leaves the
UNMEASURED set, and the overlap gate stays clean on all eight raw-
mesh builders. The two "unmeasured Harmony builders" from the detail
queue (harmony_district 393, harmony_commercial 193 objects) measure
too. harmony_terrain's five markers pass the ray gate; the marker ceiling stays at 17.

**2026-09-07 · the grammar review, worked.** The repo-wide furniture-
grammar run (INTRA 5051 · FLOAT 1737 · CHAIR 5 · DESK 1 · LANE 13 after
the mesh hook) classified by part: (1) CHAIR BACKS FLOATING ABOVE THEIR
SEATS — 29 across 14 builders (the roadhouse ring 8 cm, the drive-in
porch chairs, the courthouse jury seats, the Missing Link booths, Anya's
studio chair 12 cm, NexCorp's office chair 17 cm …) — every back
lowered onto its seat with a 1 cm tuck; (2) three more chairs facing
away (the Houston studio's five task chairs via their helper, the
pharmacy office chair) flipped; (3) NexCorp's office desk to its N wall;
(4) the Kwik Stop in harmony_commercial stood with its front half IN
the North Belt's asphalt (KWIK_CY 11 with the lot starting at 11.2) —
moved onto its lot (CY 19), its car parked along the storefront;
(5) rules: DRIVING cars (highway traffic, the delivery truck, Tem's
northbound truck) are not parking; medians, ramps and bbox-inflated
diagonal roads are not lanes; designed TUCKS (bullnose in a counter
top, liquid in a pot, book in a shelf, bulb in a shade) are not intra
clips; vehicle parts never float. Every touched builder: 0 clips,
0 misaims, 0 obstructed. Repo-wide counts after: see the next run.

**2026-09-08 · the grammar review, closed out; CHAIR · DESK · LANE
gated at zero.** Repo-wide after the class fixes: CHAIR 0 · DESK 0 ·
LANE 0 (INTRA 4544 · FLOAT 1420 informational). What closed the last
seven: (1) HARMONY DRIVEWAY CARS — `_build_suburban_house()` took a
`road_edge` clearance callable (segment or cul-de-sac bulb) and now
walks the car back toward the garage door until all four corners clear
the road by 0.5 m, or skips the car when the driveway can't hold one
(P2 House C and E lost theirs — 5 m of diagonal driveway is not a
parking space). Every house family passes its road: WE arterial + loop,
P2 arterial + bulb, ECDS collector, the NR streets. (2) The audit could
not measure a DIAGONAL road from its bbox (P2Road_1's box is 15 m tall
for a 7 m road) — roads wider than 10 m across are skipped, honestly.
(3) NexCorp's desk against Wall_N (dy 8.5), chair back 0.50 tall on the
seat, file cabinet moved off the desk's end. (4) Drafting stools face
drafting tables (`draft|drawing` are DESKISH); wheelchairs, tipped
chairs, rockers and porch swings are not "at" a table. Deck rebuild:
harmony_terrain, nexcorp_gas_go. NEXT DRAFT: the INTRA 4544 by part
class (the shelving/ceiling-grid families first), then FLOAT 1420 —
each class either a builder fix or a grammar rule, never a ceiling
bump; the same road-clearance rule for `meadowlark_circle`'s and
`harmony_commercial`'s hand-placed cars (they pass today by hand).

**2026-09-08 (later) · INTRA read as JOINTS; the POKE class; ten real
clips fixed.** The INTRA 4544 grouped by part-class pair was 95 % the
rooting grammar itself — curb over road edge, post rooted in slab,
mullion in rail, door in wall, head on body — so INTRA now treats
penetration ≤ 0.25 m inside ONE named assembly as a joint and laid
paving pairs as laid: 4544 → 174 (massing residue: a church tower
through its nave, quoins in a corner, a beacon top on its pole). What
the Deck actually saw ("chairs not fully assembled", "exploded office
chair") was a MEMBER PASSING CLEAN THROUGH a solid — a new class, POKE:
a post/leg (thin in both plan dims) or a chair BACK whose top stands
proud of a same-assembly solid AND whose bottom runs out below it.
Sheets (back panels through shelves, glass, jambs, door frames) and
ground slabs (a post rooted through a deck) are excluded. First run
198 → real ones fixed in ten builders: the courthouse judge's chair
moved ONTO the dais behind the bench (it stood on the floor in front,
back panel to the ground); the Foxhole folding-chair backs onto the
seat edge; Simon's tipped chair rebuilt lying on its back (it was an
upright chair sunk half into the floor); the Bayou/WGUR desk drawers
between their side panels; the Foxhole hi-hat out of the snare; the
Roberts faucet rising from the counter; Le Roulant's LE ROULANT
letters above the cornice with the neon wheel above them; the Centro
stockroom's door coil ending inside its tracks; the riverboat's spiral
stair rail post out of tread 1's sweep. Deep INTRA
residue fixed too: the bungalow fridge at the END of the counter run,
Cedar Tower footlockers in front of the bunks, the Kwik pylon pole
ending inside its cabinet, the diner pickup given a hood with the cab
ahead of the bed (it sat 1.25 m inside it), the Kwik Stop aisles
shifted east so the endcaps clear the counter (and sit at the aisles'
ends, not between them). POKE gated at 0 with CHAIR · DESK · LANE.
Deck rebuild: courthouse_chamber, foxhole_dressing_room,
foxhole_stage, simon_apartment, bayou_lighthouse,
wgur_transmitter_shack, roberts_kitchen, graustark, bungalow,
cedar_tower, harmony_commercial, diner, harmony_terrain,
centro_stockroom, riverboat_interior. NEXT DRAFT:
the FLOAT 1408 by class the same way (graustark 230, harmony 354
first — expect the same split between real hangs and mounted things
the grammar doesn't know yet); the INTRA 174 massing residue is a
design read, not a defect list — leave it informational.

**2026-09-08 (night) · FLOAT read by class; 82 legless chairs given
legs; the courthouse's props found their table.** FLOAT 1408 grouped by
part class: three grammar gaps (a book EMBEDDED in a one-box shelf
body is held, not floating; terrain locales have no ground box so
"nothing under it" is unmeasurable there; shutters, crenels, coats,
hoses, swings and thirty other mounted/hanging classes) took it to
812 — and the biggest real class was SEAT: 82 chair and bench seats
0.40–0.46 m above the floor with nothing under them. The Deck's
"chairs not fully assembled", named. Legs added in place (four posts
rooted 2 cm into the seat; pedestal + disc base for the two office
chairs; the judge's chair on its dais) in sixteen builders: Kwik Stop
window chairs, Board Lords (Devon), Kai's and Finn's kitchen chairs,
the New Orleans bar's group chairs, Boyd's chair, the witness chair,
El Rancho's booth + six-top chairs, the riverboat's private-dining
and back-room chairs, the Salty Tome kitchen, Daily Grind four-tops,
the New Orleans room, Solenade's east bench, Harmony's skatepark
benches, pond benches and every patio chair, NexCorp + pharmacy office
chairs. The courthouse detail passes had put BOTH counsel tables' props
(caption page, Anna's pen, the folder, the briefcase, the motion, the
coffees) at y 2.5 — the first pew row — while the tables stand at y
5.5; moved onto the tables, the folder insert reframed; Lucien Avant
was seated in mid-air in the centre aisle (0, -1.8) — now on the
second pew's aisle end; the witness-stand front reaches the floor.
Deck rebuild: the sixteen chair builders + courthouse_chamber. NEXT
DRAFT: the FLOAT residue (~700) by class — 'base' (armchair bases 5 cm
over rugs: FLOAT_GAP vs rug thickness), 'leg'/'body'/'face' (figure
parts and sign faces — mounted classes the grammar still lacks),
'tread' (open-riser stairs on stringers the prefix rule now sees),
'manga'/'book'/'deck' (racks whose tier boards are not modelled — add
the boards, not a rule); then per-class gates as each hits zero.

**2026-09-09 · FLOAT classes two through nine; a second phantom
desk.** The next FLOAT classes, each fixed as a class: BACK — seven
bench/chair backs hanging 5–17 cm over their seats (Briar Falls, Roy's
folding chair, every Harmony park/pond/skatepark bench, the riverboat
purser's chair, the Roberts kitchen chairs) lowered onto them; BASE —
the parish cemetery's 48 vaults stood 8 cm off the grass (cap and
cross followed), armchair/couch bases in the cabin, Lena's, Wagner's
and the Daily Grind extended to the floor, the drive-in popcorn
machine given the cart it stood on; BOOK/MANGA — Maya's bookshelf was
one solid block with the paperbacks INSIDE it, now a carcass with
three boards; Cosmic Comics' manga wall and YA shelf got boards; BLOCK
— Christian Ice's freezer was a solid box with the blocks inside it
and the block grid a metre west of it — a shell now, blocks stacked on
its floor; TREAD/STAIR — the four kitchen "stair mouths" were three
slabs at one xy (a ladder of shelves) → solid steps advancing into the
stair; gym, Cedar Tower lobby and Montreal row steps solid to the
ground; the lighthouse spiral's treads are RADIAL planks from the
centre pole (make_rot_box) instead of squares floating mid-radius;
BODY — kerosene heater, backup ice chest, the Henderson Telecaster
down onto their floors/stand. The bayou lighthouse had the courthouse
bug: two detail passes put the desk at (0, 1.1) and (0, -1.2) while it
stands at (RADIUS-0.8, -0.2) — logbook, mug, thermos, laptop bag moved
to the real desk, the closed placeholder logbook removed. Grammar: a
sibling that RUNS PAST a part (post through a sign face, frame side
beside its mullion, body a leg hangs from) holds it. Marker: "fardoor"
resolves to Far_Door (cedar closeup was reading the glass behind the
door as its subject). Deck rebuild: 24 builders. NEXT DRAFT: FLOAT
residue by class again (brochure racks, antlers/portraits (mounted),
ropes/bells (hanging — a HANGING class from a sibling ABOVE), crosses
on spires (cone bbox), carousel horses); the INTRA massing residue
stays informational.

**2026-09-09 (later) · the phantom-surface sweep; FLOAT 353 → 102.**
Searched the FLOAT residue for props hanging at desk/counter height
over a floor — the signature of a detail pass that hard-coded a
surface the builder never put there — and found FOUR more: FROG KNOWS
BEST's three passes ("FOR LILY" cardstock at (0,-1), Aurélie's
notebook + pencil and Ferdinand's Nikon at y -0.2) while the counter
stands at y 2.2 top 0.98; THE MIXING GLASS's last-call pass (Frank's
notebook, pen, stool at a "U-bar mid-section (0,-1)" — open floor at
the south end; the bar's N-cap is at y 7.4) and its tipped highball
at y 5.6 between the arms; BIANCA's coffee grinder 30 cm south of the
counter run and the dishwasher face standing loose off it; the
DARKROOM's notebook at y 2.05 with the dry bench at 3.1. All moved to
the real surfaces. Also: the Kwik Stop pumps had no body between base
and head (a display 5 mm thick held the head up a metre), the propane
tanks hung in their cage, the truck and the customer cars rode 6–8 cm
above the asphalt, the soda-pyramid topper hovered over its caps; the
drive-in's cup tower stood in the gap between the counters; Sam's
shelf was a solid block with the longboxes and figures inside it (a
carcass now); the Cypress Motel's pumps 20 cm off the ground; the
Lacombe jack stands 40 cm short of the truck frame. Grammar: EMBEDDED
check moved above the top-window filter (it never ran for anything
inside a tall body — Lacombe's vending bottles, Centro's bale);
HANGING (a leg from its body, a bar from its rail) and BACKED (a
poster, a deck on its wall board, an AC in its window, a face on its
machine) rules; notices, fences, sky objects mounted. Deck rebuild:
frog_knows_best, mixing_glass, bianca_kitchen_morning, darkroom,
static_drive_in, sam_bedroom, kwik_stop, lacombe_service_garage,
new_auburn_road. NEXT DRAFT: the residue by locale (the earlier
list's brochure racks, ropes, bells, crosses-on-cones), then decide
whether FLOAT gates at its floor or stays a count.

**2026-09-09 (night) · the FLOAT residue worked to its floor.** The
last 102 read one by one: half were hanging/mounted things the
grammar had no word for (towels, blackout curtains, hand dryers, dock
ropes, crane cabs, wall tools, grass tufts, card racks, bells,
silhouettes in windows, wall cabinets, window headers, phone coils,
scoreboard elements, hung shirts, tower obstruction lights, a wind
streak, hint decals, rack accents, pool cues, curb stops) — named as
classes; the other half were small real gaps, fixed in 20 builders:
bungalow and diner toilet tanks down onto their bowls (the diner's
given a trapway), Cedar Tower's pot-belly stove to the floor, the ice
house compressors and counter bell, both Foxholes' PA tops on their
subs, three church crosses onto their spire tips (cone bboxes end at
the tip), the Harmony water-tower beacon, the Graustark statue's head,
Houston's four monitors given stands (they hung 16 cm over the desks),
Kestrel's cliff rocks seated, Maya's bike wheel and the safehouse CRT
down, Missing Link pump toppers, the Montreal task chair a pedestal,
the riverboat's DOWN stair solid and its spiral UP stair radial
planks from the post, the coach's head on his torso, tideline
boulders, the wheelchair footrest, the gym bench uprights, the
Graustark crab traps stacked trap-on-trap. Repo-wide FLOAT 102 → 2
(two palmetto trunks on terrain samples) and GATED at 2. Deck
rebuild: 21 builders. NEXT DRAFT: the INTRA massing
residue is the only informational class left, and the grammar can
turn to what it does NOT yet see: rotated props (make_rot_box bboxes
are inflated — the audit should use rot_box_bbox corners), and
"faces the wall" for desks/TVs/beds (orientation grammar, class 6).

**2026-09-09 (late) · the latter-half arcana shot pass, draft 1.**
User's "real bad shot direction all throughout the latter half of
major arcana": the density scan showed 8–12 cues per 100–137-node
chapter with twenty-line holds. New tool `shot_seed.py` cuts by the
playbook grammar at prose anchors using only the locale's existing
markers (closeups on speaker change, inserts where the object is
named, back to a wide after six nodes, budget nodes/4, authored cues
untouched, mid-chapter bg swaps honoured). vol5 ch10–21: +109 cues,
story gate green, blind cues unchanged. Draft 1 — expect to prune a
third on the Deck. NEXT DRAFT: run it on vol6/vol7 tails (the 0–1
beat chapters the 2026-08-30 pass found), then ch1–9 with a lighter
hand; author [mood:] turns by the fiction's clock in the same
chapters (the tool deliberately does not touch mood); the Deck read
of ch12 (the phone call) and ch16 (the teacup / eviction notice /
camera) first.

**2026-09-09 (late, ii) · the vol6/vol7 tails seeded.** The 23
chapters below one cue per fifteen nodes (Kwik Stop 312 nodes / 12
cues, El Rancho 296 / 11, the Centro night shift, stockroom and
inventory, Cosmic Comics ×2, the Miller kitchen ×2, the vehicle cab,
the cabin's first morning, Lena's mornings and night, the Hans bakery,
the Salty Tome, the field, Bianca's kitchen, Henderson prints, the
Board Lords shop) took +251 cues under the same rules. Two tool
truths from the run: a mid-chapter `bg` must swap the vocabulary
even when the new locale has NO markers (El Rancho and Kai's
apartment have none — the stale vocabulary seeded phone/packet
inserts into rooms without them), and an insert is seedable only
when the builder has the object. Story gate green, blind cues 10.
NEXT DRAFT: Deck read of the Kwik Stop chapter (33 cuts over 312
nodes is the densest) before the early-arcana pass.

**2026-09-10 · OUTSIDE — the class the phantom passes could still
hide in.** A prop with legs to the floor never floats, so a stool
authored outside the building passed every gate. New grammar class
OUTSIDE: in an interior locale (floor boxes under 40 m), a prop whose
footprint touches no floor-class box and is not an exterior view
(thru-window trees, facades, alleys, cars, siding, docks, stairs
leaving the slab). First run found two more phantom passes: DAIGLE'S
"your stool", Lou's glass and towel, the register and the tab were
authored along y -3.5 — the parking lot — while the bar runs along
the north wall at y 7.1 (moved: Lou north of the bar, the stool on
the customer side, the register and tab on the 0.5 m bar instead of
0.48 m past its edge); CHRISTIAN ICE's two counter passes (Couvillon's
ledger at (2, 0), Marcy's notepad and Mrs Aucoin's étouffée at
(0, -1.2)) while the counter stands at (0, 2.4) — moved. Repo-wide
OUTSIDE is now 0 in interiors; informational (exteriors and terrains
skip it). Six locales have now had the phantom-surface bug
(courthouse, lighthouse, Frog, Mixing Glass, Bianca, darkroom,
Daigle's, ice house — eight); every "detail pass" docstring that says
"approx at" is the tell. Deck rebuild: daigles_roadhouse,
christian_ice_co. NEXT DRAFT: grep every builder for "approx" in a
detail-pass and verify each against the builder's own constant —
the last of this class by reading, not by audit.

**2026-09-10 (ii) · the "approx at" sweep — six more phantom passes,
by reading.** Every builder grepped for "approx"; the location claims
checked against the builder's own boxes in one query. Six more were
wrong, all invisible to every gate because the props were thin,
mounted, or legged: ASYLUM WARD C's chart binder and Sister
Beatrice's votive "at roughly (0, 0)" (the station is at (0, 6.6),
top 1.15), its five chart pockets on a "back wall" the mid-corridor
station never had (now on the east wall beside it, turned to face
in), Mrs Hadley's peppermints on "ward 4's window" (ward 4 is a door;
the corridor's windows are the east bays — on the north bay's sill
now); the BUNGALOW's Priestess pass: the pH-tape label on a closet
door at (-3, -0.8) (the door is at (1.4, 1.5)) and the basil's fallen
yellow leaves at (2.6, 1.4) — mid-kitchen floor — now at the pot's
rim under the window; CHRISTIAN ICE's freezer fog, wiped streak and
wiping cloth at (-1.5, 2) (the freezer is at (0, 3.8), glass at 3.4,
top 2.4); the COURTHOUSE's twelve jury seats at (-3, 1) — in front of
the first public pew, outside the rails at x -4..-3 / y 4..7.4 — and
the gavel at (0.4, 4.5, 1.06) over the well (the bench is at y 9.8,
top 1.45); DAIGLE'S "6 STEPS" sign on a front door "at (0, 5.4)" —
mid-room; the front wall is the south wall with an open doorway, the
sign is on the wall beside it; FROG KNOWS BEST's tank name cards along
y 2.0 — the counter — while the tanks stand at y 6.5, and Em's keys
"by the door at (3, -2.5)" — outside the building; the door is at
(0, 0). Fourteen locales have now had the pattern. All gates green.
Deck rebuild: asylum_ward_c, bungalow, christian_ice_co,
courthouse_chamber, daigles_roadhouse, frog_knows_best. NEXT DRAFT:
the same reading pass for detail-pass docstrings that name a surface
WITHOUT "approx" (grep `_z = 0.7[0-9]|_z = 0.9[0-9]|_z = 1.0[0-9]`
hard-coded surface heights) — the pattern's last hiding place.

**2026-09-10 (iii) · phantom_surface_audit — the pattern gets a tool;
eight more passes moved.** New `godot/tools/audit/phantom_surface_audit.py`
reads every builder for a hard-coded `<a>_x` / `<a>_y` pair with a
`<b>_z` / `<b>_top_z` within six lines (stems need not match: rc_x /
counter_z was the shape) and checks the claim against the recorded
boxes — some box under (x, y) must top out within 8 cm of z. Twenty-
nine claims flagged; the vehicle-body and stacking-base ones are
noise; eight were real and are moved: DAIGLE'S racked balls and cue
at a pool table "at (2, 1)" (the felt is at (1.5, 3.2)) and Gil's
buckle on a bar at the SOUTH wall (the second time the roadhouse's
bar was authored at the wrong end); LE ROULANT's wheel scuff at
(2.5, 1.5, 1.06), its cashier slip at (4, -3) and the disassembled-
wheel cloth at y 1.0 — the table is at (0, 4.5) top 0.86 and the cage
counter at (3.5, 8.6); SIMON's static-TV overlay drawn as a second
screen on the south wall (now on the TV's east-facing screen), and
his six banker's boxes and left boot "by the front door at (0, -1.8)"
— 1.2–1.6 m outside the building (the doorway is the gap in the
south wall at y 0); the DRIVE-IN's camcorder, cassettes and flashlight
on a concession counter "at (0, -1.5)" (the counters are at y 3.2);
WGUR's two desk passes at (0, -1.2) and (0, 1.5) (the desk is at
(-0.4, 1.4)) — the terminal case, the tape player and the operator's
chair, whose back then faced the desk and is flipped; Jules's shirt
INSIDE the solid rack body, now on its face; the ASYLUM's Bishop's-
letter pass at y 7.0, the gap between the counter and the desk; the
MIXING GLASS's off-pour glass, Maddie's three clean glasses and her
pour rail on a back bar at y 0.2 — the south wall — while the back
bar is at y 8.2. OUTSIDE grammar: towers, masts, guy wires are
exterior. Eighteen locales have had the pattern now. Deck rebuild:
daigles_roadhouse, le_roulant_casino, simon_apartment,
static_drive_in, wgur_transmitter_shack, asylum_ward_c, mixing_glass.
NEXT DRAFT: the audit's residue is a read list, not a count —
re-run it after every detail pass; make it a suite gate at the
current 21 once the vehicle/stack false positives are excluded by
name.

**2026-09-10 (iv) · phantom-surface GATED at zero; the early arcana
seeded with a light hand.** phantom_surface_audit excludes vehicle
bodies, stacking bases and poles by stem on both sides of the claim;
repo-wide 0 unbacked claims and a suite gate at 0 — a detail pass
that writes a surface from a comment now fails the build. shot_seed
grew `--light` (gaps 5/7, hold 9, budget nodes/6) for chapters that
already carry authored grammar: vol5 ch1–9 took +22 cues (The
Chariot's office phone call as shot/reverse-shot, The Empress's
register insert, The Hermit's chalk and wall). ch1, ch2 and ch2b were
left as authored (dense enough). vn_story 0 problems, blind cues 10.
NEXT DRAFT: the Deck read of the seeded chapters; then [mood:] by the
fiction's clock (the 2026-08-30 lesson) in the same chapters. The
Hierophant's chapel (roadside_chapel.tscn) had NO shot markers — the
chapter's authored closeups were silent no-ops; shot_closeup_paul (on
the church steps) and shot_closeup_maya (on the gravel path) are
authored now, both clear on the marker gates.

**2026-09-10 (v) · marker_author.py — 21 marker-less scenes get their
first inserts.** Counting closeup cues that resolve to no marker
found 561 across 83 presets, and 21 scenes with NO vn_shot markers at
all (Faust's apartment, the pharmacy, the skatepark, Briar Falls, the
cliffside circus, the school newspaper, Little Switzerland, El Rancho,
the gym, Kai's, the equipment shed, Coach K's and Graciela's rooms,
Miller's garage, the Caldwell kitchen, the Foxhole dressing room, the
cemetery, the crumpled barn, Wagner's, the bar exterior, the carnival
lot). VnDirector already substitutes a same-type marker for a missing
one, so a room with ANY insert cuts somewhere real; a room with none
holds the wide for every cue. New tool `marker_author.py`: for each
marker-less scene, up to four `shot_insert_<object>` markers on its
hero assemblies — prose-anchored first (the objects the chapters set
there actually name), then the largest — positioned by
marker_reframe's ring search from the preset camera's side, cue names
CamelCase-split so the gates' matcher resolves them, judged by the
gates' own occlusion and empty-frame tests. 77 markers; 0 misaims, 0
obstructed. shot_seed --light then cut the ten vol1/vol2 chapters set
in those rooms (+10: Faust's mirror and paint table, the pharmacy
office, the Briar Falls pay phone and trail, Little Switzerland's sign
and house, the newspaper's driftwood). NEXT DRAFT: the 535 cues the
seeder would add to the mid-density vol6/vol7 chapters wait on the
Deck read of the first passes; closeup markers for the cast (the 561)
need staged cast positions — gate 2 (character GLBs) — or a
`shot_closeup` generic per room the director prefers over an insert.

**2026-09-10 (vi) · BED — the head of a bed goes to a wall.** New
grammar class (the "bedroom oddities" complaint): a mattress ≥ 1.6 m
whose pillow end is more than 0.45 m from any wall, unless a long
side lies along one (a cot or daybed). Ten beds flagged, all real:
Sam's, Jesse's, the safehouse's, the New Orleans room's, the hospice
and hospital beds stood 0.5–1.5 m off their north walls (the
2026-09-07 make_bed swaps kept the old mid-room origins); the ward
5 bed in the asylum corridor had its pillow at the FOOT; Finn's
platform bed had its pillow along the long side. Heads moved to the
walls, the ward bed's pillow to its head and the frame to the N
wall, Finn's pillow to the west end. The bedside things followed:
the safehouse's chair beside the head, the New Orleans room's
nightstand and water glass to the bed's west side, the hospice's bed
table (prayer book, swab dispenser, bent straw) beside the head and
its closeup of Alice re-posed on the pillow from the bed's west side.
The moves exposed two latent
bugs: the New Orleans room's desk legs and drawer were at absolute
x 0 while the top had moved to x 1.1 (fixed), and the hospice's
closeup of Alice was framed on the old bed position (re-posed on
the pillow). The Vieux Carré four-poster stands free by design (the
kitchenette owns its wall) — exempt by name. BED gated at 0. Deck
rebuild: sam_bedroom, jesse_bedroom, new_orleans_room,
safehouse_bedroom, hospice_room, hospital_room, asylum_ward_c,
finn_apartment. NEXT DRAFT: nightstands and lamps follow the beds
(they were placed for the old positions — run the FLOAT/overlap
classes' eye over each room on the Deck); TV/couch facing (class
7: a screen faces its seating).

**2026-09-10 (vii) · screens face their seating — measured, one
fix.** Class 7 measured as a script rather than a grammar class
(four screens in the whole repo have seating): the Roberts kitchen
CRT's screen faced the south WALL with the kitchen chairs behind it
— flipped to face the room. The safehouse CRT, Simon's TV and
Wagner's TV face their seats. Not worth a gate at four instances;
re-measure when a locale gains a screen.

**2026-09-10 (viii) · cast closeups out of the walls; marker ceiling
15 → 8.** The obstructed-marker list read by hand: five were CAST
closeups no tool could reframe (a person is not an object) — Anna's
lens 0.1 m inside a cubicle wall, the Chillwave stickbox 0.4 m from
a partition, Nicola's and Douglas's against a wall and a booth back,
Philip's on a bare wall; two more (Mackenzie, the boy) in the Roberts
kitchen looked at open sky. New `cast_reframe.py`: the marker's
look-point 1.6 m along its forward is the person's spot; the ring
search around it (1–2.2 m, ≤ 30° elevation) accepts the first pose
the gate's own fill verdict passes. All seven fixed; the eight that
remain are four sky inserts (drone, crow, cypress, myrtle — the
things ARE in the sky), the eviction notice on a window, a porch
wide into its own screen and two 37 %-near frames. Ceiling 8.

**2026-09-10 (ix) · the marker gate at ZERO.** The last eight: the
Kwik Stop customer closeup through cast_reframe; the Centro and
Miller-porch wides re-posed by the same ring search at wide
distances (2.5 m+, ≤ 20°); the eviction notice by marker_reframe
(0.7 m on the tape); and the four sky inserts — a crow on a wire, a
drone, a cypress crown, a crepe myrtle — read by hand and declared
DELIBERATE in vantage_obstruction_audit (the subject IS the sky).
MARKER_CEILING 0: every marker in the repo now sees its subject and
frames a picture. NEXT DRAFT: the audit judges geometry, not taste
— the Deck read of the reframed closeups (they sit 1.4 m from the
person's spot at 15–30°) decides whether the cast grammar wants a
lower, flatter house style; if so, one constant in cast_reframe.

**2026-09-10 (x) · Spiderdrops finale — Minter row draft 2.** The
run's resolve no longer hands the host its register at once: the
web's light plays the ending first (~2 s) — WHOLE/HELD/STAR as light
travelling the web from the hub outward ring by ring with the anchors
flaring white and gold motes climbing to the score; THE STORM as
gray-blue sparks quickening off every anchor. Snap bursts scale with
the gust (26 → 56 sparks). Both GDScript checkers clean. NEXT DRAFT:
a rising sting per register (SFXBank), a Deck read of the storm
ending's length (0.9 s hold after the last light), the same class
under Spiderdrops 2.

**2026-09-10 (xi) · the third verb coin — the three bowls.** vol7
ch14 (the morning of the painting): after the bowls insert, a coin on
"the three bowls" — LOOK AT (the crow's head toward the door, the
young woman with a hand out to the dark, the carved man's eyes on
the lamp and past it the town), TURN A BOWL (she turns Marina's
grandfather's bowl a quarter; the man's eyes stay on the lamp; she
does not do that again), LEAVE THEM; and a FOURTH in ch20 (the
morning at the wall): the four bowls on the milk crate — LOOK AT,
TOUCH ROY'S (a hand held over it, not on it, for a count of four),
STEP BACK. Flags ch14_bowls_looked /
_turned hide a used verb. Story gate green. TOOL LESSON: the coin
was spliced as raw text into the chapter JSON — `json.dump` does not
round-trip these files, and an `open(P, "w").write(json.dumps(...))`
whose dumps raises TRUNCATES THE FILE before failing (it did; git
restored it). Never open for write inside the same expression as the
serializer. NEXT DRAFT: the Deck read of all four coins (ch10 box, vol6 cooler,
ch14 bowls, ch20 crate); ch11 has no stove passage to hang one on.

**2026-09-10 (xii) · OUTSIDE at zero and gated.** The last 89 were
vocabulary: rock jags, surf and headlands on the cliff, flower beds,
a Ciera by name, a kiosk, an aisle-number sign, a no-smoking sign, a
restroom shell — and one bug: the garden's Ground_Grass counted as
foliage (PASSABLE) and was dropped from the floor list, so Pepper
the dog stood on nothing. Ground boxes are floors now whatever their
name says. OUTSIDE joins POKE · CHAIR · DESK · LANE · BED as a
zero-ceiling gate. Every geometry class the grammar knows is now
gated except INTRA (massing, informational) and FLOAT (ceiling 2).

**2026-09-10 (xiii) · FLOAT at zero; blind cues worked.** The two
palmetto trunks are rooted 0.25 m into their sampled ground (a plant
on a lot apron or lawn box showed daylight under it) — FLOAT 0,
gated at 0. Every geometry class the grammar knows is now a zero
gate except INTRA (massing, informational). Blind cues: ch10's
`insert wooden_box` renamed to the cabin's authored `chest` marker;
marker_author grew `--cue <locale>:<cue>` and authored the Houston
design studio's phone and desk inserts (the bakery already had the
box's marker — the cabin section alone needed `chest`). What remains
blind is honest (9): closeups of
Coach Dale and Douglas (cast, substituted at runtime), "hands" ×2
(a person's), a tattoo, a press and a window no builder has.

**2026-09-10 (xiv) · every room gets its closeup frame.** 561 cued
closeups of people resolved to no marker across 112 presets, and
VnDirector's substitution then borrowed an INSERT of a prop for a
line about a face. `marker_author.py --closeup` authored ONE
`shot_closeup_person` per scene that had no closeup marker — a bust-
height frame of the room's conversation spot (the preset camera's
look-point 3 m out), 1.2–2.2 m off it, ≤ 25° down, passing the fill
verdict: 81 rooms, then the last three (the darkroom is 2.6 m across;
Kestrel and the tideline are cliffs) under a relaxed band —
`--relax` widens the house band 1.2–2.2 m / ≤ 25° to 0.9–3.2 m /
≤ 38°. All 84 rooms carry both frames. The director's substitution now
prefers it for every cast closeup in those rooms. Named `person`
because the matcher splits CamelCase and "room" is a word in
CardRoom / CountRoom / ChangeRoom. The REVERSE SHOT followed the same
day: `--closeup-b` searches from the far side of the same spot (the
mirrored preset camera, ≥ 1.5 m from the first frame) — 78 rooms have
both, 0 misaims, 0 obstructed, and VnDirector's hash of the character
id picks one, so two speakers alternate sides. NEXT DRAFT: the seeder
could cut cast closeups in rooms that carry only the generic pair (it
keys closeups by character today); the Deck read of a dialogue chapter
in Lena's apartment or the Miller kitchen decides.

**2026-09-11 · the generic pair put to work: +862 cast cuts.**
shot_seed learned the room's generic closeup pair: when a speaker has
no marker of their own but the room has `shot_closeup_person` and its
reverse, each speaker OWNS a side for the scene (first speaker takes
the frame, second the reverse, alternating from there; a cut to the
frame we are already on is not a cut, so it is skipped). Applied at
--light across every volume: 175 chapters, +862 cues, budget still
one per six nodes. The Miller kitchen's Monday breakfast now plays as
shot/reverse-shot with Bianca at the stove and Sam at the table.
Story gate green, blind object cues unchanged at 9. The pass exposed a
continuity wobble in the same rooms — an AUTHORED cast cue
(`[shot:closeup bianca]`, one of the 561 with no marker) still
resolved by hashing the name onto the pair, so a character could
appear on both sides in one scene. VnDirector now keeps a per-locale
speaker→side map (first-seen order, cleared on every bg change), so
authored and seeded cast closeups agree. Both GDScript checkers clean.

**2026-09-11 (ii) · mood_clock_audit — a mood is a claim about time.**
The 2026-08-30 lesson ("audit the mood against the fiction") became a
tool: each `[mood:]` cue governs until the next, and the OPENING lines
of its passage are read for clock readings and hour words. Only
light-against-dark is reported — morning↔day and dusk↔night are the
same light an hour apart, and pre-dawn is the hinge. Three tool truths
cost a pass each: past-tense narration means a night chapter says
"morning" on every second line (hence opening lines only); a clock
after "since / until / from" is a span the scene remembers, not the
hour it is in; and 4 and 5 AM are DARK — morning light starts at six.
Two real findings out of 321 cues: Diego's Sunday opened `day_bright`
on a blackout-curtained bedroom at 4:08 PM ("the kind of dark that has
no relationship to the hour") — now `night`, with `day_bright`
restored when he goes downstairs; and the Devil walked out into "the
New Orleans morning" under `night` — now `dawn_warm`. Three
disagreements are declared deliberate in the tool (Death's 4:06 AM
under the card's rising sun, the painting cabin's pre-dawn, booth 6 at
3:47 AM). Gated at 0.

**2026-09-11 (iii) · the Minter light reaches Spiderdrops 2.** The
bible's next-draft line for the slowstick register — "the same FX
class under Spiderdrops 2's balloon glide" — shipped: LongWindFlight
loads SpiderdropsMinterFX and feeds it the glide's own events (silk
cast, drop caught, thermal entered, leg crossed, every ten points a
mote). The finale followed the same day: ARRIVED plays the crossing back as
light travelling the wind band left to right with gold going up at the
landing, STILL FLYING is the wind's light leaving to the right and not
coming back, one house sting each, the host reading the register only
after. Both GDScript checkers clean. NEXT DRAFT: the Deck read of both
sticks' light at 75 % trip and of the 0.9 s hold after the last spark.

**2026-09-11 (iv) · blind cues at ZERO — every line gets the frame it
asked for.** 1532 object cues across 123 presets, all resolving. The
last nine were three kinds: a cue naming a character by the wrong id
(`coach_dale` where the scripts say `coachdale`, `douglas` where they
say `doug` — the cast ones the audit could never skip because the id
was in no `char` field anywhere); a cue naming a thing the builder
does not have but a NEIGHBOUR does (the ouroboros tattoo on Douglas's
forearm → the bar's hands insert; the print shop in Bern → the
template's mill); and a cue naming a thing that is not there ON
PURPOSE — Diego's knock "at his window" in a cell that has no window,
now the WALL, which is the better cut and the chapter's own image.
Two hand cues with no hands geometry take the room's face frame.
Gated at 0.

Also measured and closed: the drafting program's "edge-of-set
treatment (no visible world edges)". Every preset camera under a
ceiling was cast for escaped rays: five leak 1–2 rays of 27 (doorways),
and the diner's formal dining room's 40 % is the RIVER through its west
windows, not a hole. The sets are closed; nobody needs to look again.

**2026-09-11 (v) · the gauntlet's three copies of every board.** A
gauntlet space lives in the location JSON (the board), the host's
SPACE_MAP (world positions) and TarotGauntletGame's hand-copied
mirror (used standalone) — and the mirror's own comment, "when you
update a host's SPACE_MAP, copy the change here too", was the only
thing holding them together. It had rotted: the Magician's last five
arcana stations (star, moon, sun, judgement, world) never reached the
mirror, so a standalone Magician board had no vantage for them;
D'AMBROSIO'S BOOTH_1 AND BOOTH_6 WERE SWAPPED against build_diner.py's
south→north numbering (Booth_1 at y −3.75, Booth_6 at +3.75 — the
builder settled it, the host was right, the mirror walked the player
to the wrong end of the alcove row); the hostess stand kept its
pre-playtest position; and precipice_door — a THRESHOLD liminal
station — was missing from the mirror entirely. All fixed, and
`space_map_audit.py` now holds the three copies to each other as a
suite gate (hosts paired to locations by key overlap, since the
diner's host is DinerGauntletHost and its location id is
"dambrosios"; symbolic floor constants resolved from the host).
Three locations are declared KNOWN_DIVERGENT: ember_ash_office,
roberts_house and the_hierophant_circuit have host tables describing
an earlier staging, the game falls back to the mirror for them, and
the audit checks only that the mirror covers the JSON's board.

Also checked and clean: all four liminal-tagged locations bind the
LiminalProximityController, so no liminal tag is inert.

**2026-09-11 (vi) · the sweep for hand-synced duplicates.** After the
space-map find, every comment in the repo admitting a manual copy was
read. Most were shape-mirrors (the stick hosts' studio chrome) with
nothing to check. One was real: CharLayer's EXPR_TINTS (31
expressions, applied as modulate at runtime) against
raster_substrate.py's EXPRESSION_TINTS (6), so the offline baker's
`--all-expressions` emitted six PNGs and every other expression baked
FLAT — the lookup's default is no tint, which cannot be told from a
legitimate one. Brought to parity and gated by `expr_tint_audit.py`.

**2026-09-11 (vii) · the lighting pass the drafting program asked for.**
Model-chapter quality includes "lighting that models the space", and
nothing had measured it. Every locale has the three-light foundation
(median 5 lights, none at zero), but 205 VISIBLE FIXTURES emitted
nothing — the playbook's cardinal rule, broken 205 times. New
`practical_author.py` authors them from the playbook's own tables
(colour by source, range ≈ 2× fixture height, energy in band, shadows
off, `<Fixture>_Practical` naming), capped at the published budget of
ten per locale and prioritised by distance to a preset camera, since
the rule is about what is in frame. 158 authored across 48 locales:
the Mixing Glass's booth candles, the Pit Stop's five pendants, the
Kwik Stop's tubes and heat lamps, Cedar Tower's lobby pendants and
sconces, twenty porch fixtures in the suburbs, the Magician's dock
lamps. NEXT DRAFT: the Deck read — the numbers are the playbook's but
only the screen can say whether any room is now over-lit, and the 47
fixtures beyond the per-locale budget wait on that verdict.

**2026-09-11 (viii) · six volumes were playing vol5's music.** The
lighting pass asked what else ships as a description instead of an
artifact, and the answer was the score. `music_catalog.json` had 207
entries and FIVE audio files; thirty-six of the missing were named by
a chapter, and 234 of 312 scenes had no entry naming them at all — all
of vol6 and vol7 bar a dozen, the whole arcana run ch6-ch21, the vol1
link hub. None of that is silence: `AudioMgr.play_next()` falls
through to the player's unlocked playlist when a chapter's track list
is empty, so every volume has been scored by D'Ambrosio's at dawn and
the cicadas. Shipped: 33 beds authored from the catalog's own prose
through the project synth (`author_vn_beds.py`), six orphan vol5 room
tones adopted into the catalog, ten already-rendered .wav beds
REPOINTED (their entries pointed at .mp3/.ogg that never existed — the
first pass overwrote all ten before `git status` was read),
`normalize_bank` taught to walk `bgm/` itself (it only ever visited
subdirectories, so every VN bed shipped at 0.07-0.25 against every
stick's 0.85), and every non-stub scene assigned by
`assign_chapter_beds.py` — 174 by place, 23 on the volume floor, 0
unscored. New gate `music_coverage_audit.py` at zero. NEXT DRAFT, all
Deck-gated: does 22050 Hz read dull on the hiss-forward beds (rest-stop
wind, the cicada field, Kestrel's thermal)? is the ~40 s loop seam
audible at the top of each bed? are the five remaining `.ogg` tracks
now quieter than the wavs `normalize_bank` can reach? Then the 92
ghosts — character themes, gauntlet B-sides, finale stingers — which
have entries and no files and are played by their own systems.

**2026-09-11 (ix) · the audio the catalog doesn't cover.** The same
question asked one layer out — every `assets/audio/...` path written
into a script or data file — found fifteen that had never existed. The
twelve `gauntlet_*.ogg` in TarotGauntletGame's `_SFX` were dead (an
earlier pass had rerouted every key to an SFXBank preset) but read
exactly like a live bug, so the table is gone and `_audio_sfx` warns
instead of falling through. The other three were real: the Fool's
diner carries TWO JUKEBOX 45s AS USABLE ITEMS — NOON ROOM ROOM and
WHERE THE BAR USED TO BE — that played nothing when used, and the
Music Player's TAPE REEL skin unlocks on having heard
`vol5_elicia_theme_solo`, a file that never existed, so the skin was
unreachable by construction. All three authored (the two 45s are the
only tracks in this wave with a real tune — a jukebox record is
diegetic, the player chose to hear it). Also fixed:
`normalize_bank.py` computes gain per DIRECTORY, so once a directory
is at target a newly-added file stays at the synth's raw level —
three tracks shipped that way inside this session before
`--set <files…>` existed. New gate `audio_reference_audit.py` (588
paths, 12 bank routes, zero). NEXT: the 89 remaining ghosts —
character themes (which unlock on `show` and would give every
principal a signature), the gauntlet's arcana B-sides, and the
Magician/Priestess finale stingers, which are the ones a player
actually reaches at the end of a run.

**2026-09-11 (x) · the gauntlet's scenario beds.** Fifteen catalog
entries described one bed per ARCANA × DIFFICULTY across the first five
arcana and had neither a file nor a caller — every board played the
location drone. Authored all fifteen (12-14 bars, 55-65 s: a run is
minutes, not a page) and wired `_BGM_BY_SCENARIO` keyed
`"<arcana>:<difficulty>"` ahead of `_BGM_BY_LOCATION`. The
descriptions themselves say difficulty is a TIME OF DAY — easy is
afternoon light, medium the working evening, hard the small hours —
which is the same axis `_GAUNTLET_DESIGN_PLAYBOOK.md` names as the
primary difficulty knob, so the score now says what the board says.
The general lesson: a catalog entry with no consumer is invisible to
BOTH audio gates (coverage sees only the chapter relation, reference
sees only paths someone wrote down); the only thing that finds it is
reading the descriptions and asking who would ever hear this. NEXT:
the fifteen still in that state — the Magician's seven finale stingers
and the Priestess's six (the code already maps finale-id → milestone
key at the loss screen; it just never plays anything), plus
gauntlet_win / gauntlet_loss. Then the 22 character themes, which
would give every principal a signature on `show`.

**2026-09-11 (xi) · the description was not the board — a correction
to (x).** Checking the fifteen new scenario beds against
`setup_*.json` found that the catalog descriptions they were written
from had themselves drifted. The EMPEROR's three describe a courthouse
(brass clock, radiator, appellate hearing) and every Emperor scenario
is on the riverboat; the HIEROPHANT's three describe a BBS night and a
ham band and the board is a Sunday circuit — St Jude's after the
service, table 17 at brunch, the bandstand at 3:18 PM. Six beds
re-authored to the board as it is and twelve catalog entries retitled
and re-described through `author_vn_beds.py --retitle` (The Friday
Helm · Nine-Oh-Six · Six Weeks Apart · The Service Has Ended · Table
Seventeen · The Second Phone Call, plus clock fixes on the Magician's
easy, all three Priestess and two Empress). The rule now written into
the audio playbook: **`resources/games/<arcana>/setup_*.json` is the
board of record** — the game reads it, so it is maintained; the
catalog's `desc` is prose nothing checks, so it rots. Read the setup
first. `audio_reference_audit.py` gained a structural half of the
check (a `_BGM_BY_SCENARIO` key whose arcana × difficulty no scenario
defines now fails); nothing automatic can tell you the prose has moved
to another building.

**2026-09-11 (xii) · the endings get their music.** Every gauntlet run
ends on a win screen or a named Finale and neither played anything but
a one-shot SFX. Thirteen stings authored — two shared (THE LEAP (won)
and TWENTY-FOUR HOURS (reversed): the same two chords taken opposite
ways, and the win is the only cadence in the gauntlet's music) plus
the Magician's seven and the four Priestess finales the bungalow board
can actually reach. `_audio_ending()` prefers the named sting and
falls back to the shared one, so all 22 arcana end on music now and a
new named sting is one table entry. Also found and fixed: the
Priestess milestone block matched SIX finale ids from the
recording-booth staging, none of which exist in the bungalow board's
finale.json, so no `milestone:priestess_finale:*` could ever unlock —
rewritten by trigger. New gate `finale_id_audit.py` (27 id references
across 22 arcana, 0 dead; the arcana guard is scoped to the FUNCTION,
or an arcana-agnostic helper like `_loss_cg_path` inherits a guard
that isn't its own). NEXT: the twenty other arcana have 4-5 finales
each and no named stings (they take the shared one); `_loss_cg_path`
names finale CGs that may not exist — an image-reference audit is the
same shape as the audio one; and the 22 character themes remain.

**2026-09-11 (xiii) · THE FEEDBACK — the Minter half of the trip.**
User direction: "the psychedelic visual layer to the visual novel
should include a feedback element that deepens the visual experience
ala Jeff Minter visualizers and games." The bible had carried this as
the one honest gap since draft 1 ("no feedback-trail buffer yet ...
the real thing is a SubViewport with a decay quad"). Shipped for the
VN: two half-resolution ping-pong SubViewports re-project the previous
buffer with a slow zoom/spin/drift, decay it, and screen in new light;
a show rect adds it back over the background. THE DESIGN CALL that
keeps it inside rule 1: **the buffer catches the LAYER'S OWN LIGHT,
not the picture** — the source's highlights plus the register's aura
recomputed from its silhouettes — so the photograph never trails and
a face never smears. The motion rule holds: zoom/spin/decay are
per-second rates × delta, unchanged by the music, and the beat's only
job is to brighten what enters. The source is a TEXTURE (the PNG bg,
or the 3D locale's SubViewport — both registered, the rig takes
whichever is live), never the screen, so type cannot smear by
construction; the rect sits at z_index 10, above the backgrounds and
under the cast. Per-register character: the arcade SINKS (zoom −0.09),
sludge HANGS (decay 2.6, barely travels), the oil projector BLOOMS
(0.90 / +0.17), the slowstick overlay stays faint. Fifth player dial:
TRAILS. NEXT DRAFT, Deck-gated: the wake length and the zoom sign per
register are container guesses; is milk_honey at 0.90 a light show or
a fog; then a screen-sourced rig for the locale walk and the gauntlet
board, which needs a UI-free source first.

**2026-09-11 (xiv) · THREE DECK NOTES.** (1) **"I like the look of the
psychedelic warehouse, it fits."** — the Magician's cathedral interior
under `arcana` plus the new feedback is a KEEP, and the first verdict
THE TRIP has had that was not a complaint. That frame is the reference
now. (2) **A directive rendered on screen**: the title card read
"[mood:arcana_warehouse]Chapter I — The Magician", because
`_directed()` ran on narrate/say/think and not on `interlude`. Putting
the mood on the card is the right instinct, so `interlude` became a
consumer (and joined the resume replay); `vn_story_audit` now fails on
a leading directive in any field the engine does not consume — `sub`
and `caption` are the same trap. (3) **The camera was inside a
building the prose was describing from the road**: ch1 narrated "the
warehouse slumped ... at the industrial edge of Graustark" and
"Outside, kudzu vines throttled the chain-link fence" over an
interior, then turned inside itself one line later. New
`cathedral_exterior` vantage into the graustark megabuild (SW corner
looking NE: the office annex, the south gable, the roof masts; ray
tested clean at 41 m), a `bg` cut back to the interior on the word
"Inside", and an `[shot:establish]` to open the room. THE RULE: when
narration names a place the current locale cannot show, the answer is
a second locale, not a different marker inside the first.

**2026-09-11 (xv) · THE DOMESTIC REGISTER.** "Other chapters aren't as
successful, the lovers should be warm and cozy and domestic, not
garish and weird." The cause was the REGISTER, not the amount: vol 5
pushes `arcana` for the whole volume and phosphor-green lines with
sodium amber are exactly wrong over a kitchen in the morning. A
pillar-wide register is right for a pillar and wrong for a room, so:
a new `domestic` register (palette 5 HEARTH — amber → rose → cream and
nothing on the cold side of the wheel; a low aura, almost no wash or
hue drift, a pulse that never snaps, a wake like afternoon sun on a
wall) and a fourth director dial, `[register:X]`, with the same
lifecycle as `[trip:]`. Applied to THE LOVERS (whose opening also had
a mechanical `[trip:1.2]` fighting a mood that had deliberately dialled
itself to 0.70 — removed) and TEMPERANCE (dust motes in a shaft of
light, a coffee maker, "a cluttered archive of selves"). NOT applied
to the other eight vol 5 chapters with domestic locales: **locale is
not register.** THE STAR is in a cottage and reads "like having your
skin peeled back layer by sensitive layer" — a lookup would have made
it cozy. The remaining candidates, needing an authorial call each:
ch2_priestess + _b (the bungalow), ch8_strength, ch12_hanged,
ch13_death (the hospice vigil — the strongest of the eight),
ch15_devil, ch16_tower, ch18_moon.

**2026-09-11 (xvi) · inside_out_audit — the Magician's class, gated.**
The camera-inside-a-building-the-prose-describes-from-the-road defect
was one instance of a class, so the class got a tool: every narrate
line is read for a STRONG place opener ("From the road", "Across the
street", "The house stood/slumped", "Inside,", "In the kitchen") and
compared with the active background's kind — presets classified by
name first, geometry (a roof-sized box over the camera) as the tie-
break. A window in the two lines before makes an exterior opener a
VIEW, not a camera claim (the Chariot's "Across the street, an older
man ... was leaning against a streetlight" is Antonio at the leaded
window, and the director's `[shot:insert window~]` is right). 7962
narrated lines under a known vantage; ONE more real: the Harmony Creek
prelude walked into the Miller kitchen ("In the kitchen on Meadowlark
Circle, a voice calls up the stairs. / Sam. You up?") with the street
still on screen — cut to `3d:miller_kitchen` on that line. Gated at
zero. NEXT: the openers list is narrow on purpose; widen it only from
Deck reads, never from a thesaurus.

**2026-09-12 · trip_fight_audit — 85 pushes on cool moods.** The
Lovers' "garish" opening had a second cause beside the register: a
mechanical `[trip:1.2]` (the 190-interlude structural-turn pass) on a
mood that had dialled itself to 0.70. Measured across the corpus: 85
such lines, all on moods the bible names as cool (day_bright,
morning_bright, lunch, fluorescent_corridor, kitchen_practical,
studio). All 85 pushes removed so the mood governs; gate at zero. The
dark-mood pushes stay — pushing a dark scene is the bible's own
direction. NEXT: the same product check for `[register:]` once more
chapters carry it.

**2026-09-12 (ii) · THE FEEDBACK, draft 2 — everywhere, still without
the UI.** Draft 1 was the VN only, because the only UI-free source
was the background texture. Draft 2 adds two more without a single
screen read: the GAUNTLET BOARD mounts the rig on its own
`fp_3d_container` (its 3D already renders into a SubViewport; show
rect one z above it and under the board header), and THE MIRROR — a
quarter-res SubViewport sharing the root World3D with its own Camera3D
copying the live camera every frame (transform, fov, near/far,
projection, environment, attributes, cull mask), no shadows, no AA —
serves anything whose 3D renders straight to the root: the locale
walk, the cathedral, a menu visualizer. HUD is never in the buffer by
construction. It stands down when a mounted surface is live or the VN
holds the global layer aside; 2D screens have no camera, so the sticks
stay untouched. NEXT: the mirror's cost in graustark on the Deck; the
same Deck reads as draft 1.

**2026-09-12 (iii) · the uncut runs.** Measured the longest stretch of
text lines between two `[shot:]` cues per chapter. The kwik stop — a
model chapter — had a 43-line three-speaker dialogue with no cut.
Three causes fixed in the tools: `marker_author --closeup` treated a
NAMED closeup (shot_closeup_sam) as satisfying a twelve-speaker room
(it now skips only when the generic person/person_b pair exists); it
took the room's FIRST preset, which for the kwik stop is the god's-eye
diagnostic at `-PI/2` and failed silently (diagnostic presets skipped,
expressions evaluated, next preset tried); and `shot_seed`'s budget
trim kept the EARLIEST cuts, spending the allowance on act one (a
candidate that breaks a run ≥ 2 × HOLD_MAX is kept regardless, and a
hold on the wide rotates to the next establish at 2 × HOLD_MAX).
Kwik stop pair authored (aim clean), then — once a `bg` change was
counted as the cut it is — the courthouse got a SECOND WIDE from the
new `marker_author --establish-b` (far side of the look-point, ≥ 90°
round, fill verdict; `candidates()` only opens its wide rings above
subject size 3.0) and the Pit Stop got its person/person_b pair (it
had three named closeups, all objects). 97 light-mode cues across vols
5–7, all resolving, 839 markers aim-clean. Chapters with a run > 20:
15 → 1; the kwik stop 43 → 10. NEXT: the one left is the painting in
`salty_tome_alley` — three presets share one tscn and a generic pair
lands at the first preset's look-point (the shop), so the alley needs a
per-preset pair (`--preset` on the planner) before the seeder can cut
it.

**2026-09-12 (iv) · PER-PRESET MARKERS — 70 wrong-room closeups.** The
alley problem generalised: one .tscn serves several presets in
different AREAS (26 of them — the shop/kitchenette/alley, the counter/
formal room, shore/dock, cab/cab-side, lobby/studio/quarters/portal,
street/shop…), and a marker resolved by NAME from the whole file does
not know which area the scene is in. The 2026-09-10 closeup-pair pass
therefore sent 70 cast closeups in 21 chapters to a face in another
room — the dock to the shore (15.7 m), the formal room to the counter
(23 m), the World's child 272 m across graustark. Convention shipped:
`<marker>__<preset_id>`; `Background3D.find_shot_marker` and the
borrow pool prefer the loaded preset's own marker; `marker_author
--preset <id>` authors at that preset's look-point; the aim and blind-
cue audits strip the suffix. Pairs authored for lake_palestine_dock,
accretion_basement, vehicle_cab_side, centro_dock, meadowlark_circle_
henderson + _night, new_auburn_strip_mall + _bypass, riverfront_park,
small_wood_roadside + _night, dambrosios_formal, graustark_ruins; the
closeup planner now requires ≥ 3 distinct surfaces in frame (the dock's
first pair looked at open water). Named second-room closeups are clones
of that room's pair (nicola/dean at the formal room, the child at the
ruins). New gate `wrong_room_audit.py` (12 m = the same room; inserts
exempt). The alley got its pair too (`--relax`: an alley is 2.8 m
across) and the painting / wall / leaving / eight chapters re-seeded —
chapters with a run over 20 lines: 15 → 0. NEXT: every multi-preset
room's OTHER presets by demand rather than by audit (main_street ×8 on
board_lords_interior.tscn, cedar_tower's four areas, shuttle_bench ×8)
— they pass the 12 m gate today only because their cues are few.

**2026-09-12 (v) · ONE PAGE AT A TIME.** "Some sections have too much
text on screen at once and it gets too small and cramped." The box was
doing the cramping: DialogueBox auto-fits past 260 visible characters
by stepping the font toward half size, and 2,219 nodes were over the
line (the longest 1,566 characters — 17 px type over the picture). New
`page_split.py`: sentences packed to 230 characters, long sentences
broken at dash / semicolon / comma, then conjunction, then any space;
directives and `voice` stay on the first page; `char` / `expr` / flag
gates copy to every page; choice `goto` / `check` and jump `goto`
re-pointed to first pages; raw spans spliced via raw_decode (211 of
313 files do not round-trip), parsed before writing. 2,155 nodes in
226 files → 3,460 extra pages (redone once: a blank line inside a
node is a hard page boundary — the Moon's opening had eight and the
first pass had packed them by sentence count; a [fade] span is one
unit, not a reason to leave 549 characters whole); every scene gate
green; two audits that
counted in nodes now count in what they meant (four pages, 450
characters). New gate `page_length_audit.py` at zero. Follow-through:
`_advance` stopped the voice on every page (a recording is the whole
passage, on page one) — it now plays on while the next node is an
unvoiced text page; and vols 5–7 re-seeded in page units (450 cues;
chapters with a run over 20 pages 11 → 4). NEXT (Deck): is 230 the
right page at 34 px, or does a page want three lines rather than four?
Does the seeder now cut too often? Two constants (TARGET, HOLD_MAX).

**2026-09-12 (vi) · a `show` enqueued another volume's bed.** Found
while sizing the character-theme wave: `unlock_tracks_for_character`
enqueues every catalog entry naming the character, and BEDS name
characters (Lena → `vol2_ambient`; Nicola/Dante → `vol4_standoff_
strings`; Antonio → `vol3_ambient`). Masked while the files were
missing; live since the 2026-09-11 render — a Lena `show` in vol 7
queued Oregon over the cabin. Enqueue is now volume-scoped; the unlock
is not. Recorded rule: rendering a file activates every consumer the
entry already had — read `chars` and `chapters` first. The 22
character themes stay NEXT, and with this fix they can be added
without surprising the queue.

**2026-09-12 (vii) · THE WORLD HUM.** Every 3D scene has TWO beds and
the loud one is not the catalog's: `enter_locale_ambient` ducks the
Music Player to 14% and raises the locale's bed from
`resources/audio/locale_ambient.json` — which mapped 108 locales to ten
vol-5 files (cicadas on Cape Perpetua, the riverboat drone on Highway
101, D'Ambrosio's dawn in Cosmic Comics) and left 42 presets with no
hum at all. So the 2026-09-11 chapter beds have been playing at 14%
under vol 5. Rebuilt from the same locale→bed table the chapters use
(`rebuild_locale_ambient.py`: place bed, else the author's generic
room tone, else the volume floor): 19 kept, 86 re-pointed, 41 added.
Runtime-looped WAVs now get a loop region (they had none). New gate
`locale_ambient_audit.py` at zero. THIS is the change the Deck will
hear first in vols 6–7. NEXT (Deck): do the hum beds loop; is 14%
under the hum the right Music Player level now that both layers are
the same room; the character themes belong in the ducked layer.

**2026-09-12 (viii) · SIGNATURES.** The catalog's 46 character themes
("Sharp's signature, played whenever Sharp shows up") had one file.
Nineteen authored — every theme whose character is shown or speaks in
its volume (`faust3` → `faust` corrected; the other 27 name keys that
never appear and wait for their scenes). The engine cues a signature
ONCE PER SCENE on the character's first show or first line (four
themed characters never `show`), as a one-shot that hands the bed
back, in both jukebox modes; a resume fast-forward only marks. Under
a world hum the duck inverts: the signature comes to full and the
hum sinks to 20% for its length, then both return. `bed(trim=)`
brings the set within 4 dB before normalization. 304 cues across 184
scenes. SECOND WAVE same day: fifteen more themes name the gauntlet's
visitor cast and cue from the arrival card (`_cue_visitor_signature`,
alias table for board-local ids, volume scope lifted) — 34 of 46 themes
have files; the 12 left name characters no scene or board has. NEXT
(Deck): the once-per-scene rate (three stingers in a vol 6 scene's
first minute), the 0.20 floor, a signature over the gauntlet's own
scenario bed (no hum there — it plays at the Music Player's level).

**2026-09-12 (ix) · THE SEAM.** Every hum bed ended in a second of
digital silence and opened on its attacks, so every 3D room dropped
out for a second every 40-70 s at the loop point — the "~40 s loop
seam" deferred on 09-11, and worse than a seam. The synth now honours
`loop: true`: the boundary notes are held 2 s past the loop bar and the
overrun is equal-power crossfaded into the head (a plain fold still
dipped 11 dB — the voices release inside the note). All 50 looping beds
re-rendered with `--keep-level` (peak-matched to the normalized file, so
nothing moved); the 33 one-shots keep their tails. The 16 beds not
authored here get the runtime half: `_last_audible_frame` puts the WAV
loop end at the last audible frame. NEXT (Deck): the 2 s crossfade on
sparse beds; the 16 legacy compositions re-rendered with `loop` once
heard; the `rain` voice's new envelope on the same pass.

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

## THE VISUAL PROGRAM (2026-09-13 · read `lore/_VISUAL_PROGRAM.md`)

The user's ask: *"Improving backgrounds, models and direction and
design is still a big project. Let's plan that out."* The plan is its
own file. In one line each: ARC 0 is THE LENS — a contact-sheet rig
that renders every preset × marker and every hero GLB × expression to
PNGs Claude can read, because 871 framings are math-verified and zero
have been seen; backgrounds go one locale deep in screen-time order
(cabin_interior 31 · lena_apartment 23 · the vol 6 dozen) through the
primitive upgrade + D2–D6 + light + wear; models have three routes and
the user picks (Mixamo · Meshy-from-image · GNM stopgap); direction's
next draft is cut from the sheet; design gets the VN consequence map,
the model-chapter verb coins, the gauntlet tempo rows, and Salmonberry
on the word. Seven user decisions are listed in §8 of the file.

**2026-09-15 · ARC 0 draft 1 shipped (unseen).** The contact-sheet
rig: `contact_manifest.py` (the shot list, committed), `VnContactSheet
.tscn` (Background3D + Portrait3D, 1,559 frames), `contact_sheet.sh`,
`contact_push.sh` (orphan branch `qa/contact`). One paste on the Deck in
`godot/qa/README.md`. Until it has run once, every framing in the game
is still unseen.

**2026-09-18 · LIGHTING · orphan practicals, gated.** The two hand-
finds (fluorescents in the kerosene cabin, a desk lamp nobody built in
Lena's) were a class: `orphan_practical_audit.py` found nine lights with
no fixture — four bedrooms sharing one template desk-lamp position,
Natalie's floor lamp, two fluorescents off their tubes, the cafe's two
pendants that never existed. Seven moved onto their rooms' real lamps
and tubes; the cafe's pendants built (`make_pendant`). Gate at zero in
the suite. (The cabin's "planned 0" was right: its lamp and lantern had
been lit on 09-11 at the file's tail; the hand copies were duplicates,
now removed, and the audit checks DUPLICATE root names too.)

**2026-09-22 · THE SUPPORT PASS (user: "lots of objects floating in
scenes still, not tethered to walls or tables or floors").** The
furniture gate's FLOAT rule only judged prop-sized parts, let
anything named like a fixture off by name, and counted a part
EMBEDDED in a solid as held. `support_audit.py` asks the plain
question of every recorded box: is it connected, through what it
touches (3 cm), to the floor, a wall or the ceiling? First run: 3,805
floating components in 121 locales. Three causes were systemic:
(1) the recorder's stub turned `catenary` into the constant 0.9, so
every strung wire, fence strand and chain in the game had recorded as
a POINT at (0.5, 0.5, 0.5) since the stubs were written — invisible
to every gate; (2) kit helpers built things in the air: every recessed
fluorescent 9 cm below its ceiling, every floor plant's pot 17 cm up,
every kit car's taillights 10 cm behind the body, the endcap's
shelves on nothing, the coffee station's labels 11 cm over the pots;
(3) rooms dressed by coordinate: Miller's upper cabinets 28 cm off
the wall, outlets 60 cm off theirs, the cabin's pot rack hung on
nothing, Lena's coat hooks in the door gap, the kwik stop's spinner
pole 34 cm above its base, the diner's cords all 5–10 cm short of
the ceiling (`D_H - 0.05` everywhere), its port stools without
posts, its formal table standing on its cloth. After the recorder,
kit and eight-room fixes: 1,181 → the baseline
(`support_baseline.json`, per-locale, zero-regression in the suite);
the six most-seen rooms are at zero, the kwik stop 145 → 49, the
diner 87 → 45. Terrain locales (graustark, harmony, riverfront, the
roads) are skipped: a heightfield floor the recorder cannot see.
SECOND PASS, same day: the kwik stop and the diner to ZERO (1,181 →
913 repo-wide, baseline rewritten). What the last floats were, by
kind — worth knowing because every locale has the same kinds:
(a) DRESSED A PHANTOM: the kwik stop's ATM detail (14 keys, three
slots, an overhead sign) at (-5.4, 2.1) where no machine had stood
since v2 — the real ATM is at (4.8, 1.0), and its screen faced the
south wall 70 cm away while the queue tape lay on the north side;
now it faces the store and wears the detail. The diner's Hierophant
print hung in open air where the centre-floor private dining box
was removed on 07-12 (now on the formal room's partition); its
meeple shelf hung mid-hallway (now on the north wall by the
corkboard); its vestibule payphone hung IN the front door's glass
(now in the NE corner's solid wall); the bathroom mirror + hand
dryer hung on the picture window (now on the north partition).
(b) OFF THE COUNTER'S END: the donut case 0.6 m past the coffee
counter, the cream/sugar unit over both its edges and 4 cm into the
top, the microwave 19 cm up and half past the edge. (c) A HAIR
SHORT: coin slot 4 cm off the jukebox face, LEDs 5 cm off the pump
display, the spray head 5 cm past the arm's end, ropes 6 cm short of
their posts, the sign topper with no posts, the bottle pyramid
starting 25 cm up (a riser now), the hose nozzle with no hose to
the coil. (d) THE AUDIT'S OWN BLIND SPOT: "crown" in the foliage
list dropped the candelabra's crown and the register's crown, so
their candles and finial read as floating whatever the builder did
(`TREE_CROWN` now needs a tree word in the name). The bayou
lighthouse got the same treatment on the way (11 → 1): its calendar,
life ring and octant kit sat OUTSIDE the tower (r 3.2 in a 2.4 m
room), the skiff's lamp over the marsh.
THIRD PASS, same day — the next four by placements to ZERO (913 →
652 repo-wide): the RIVERBOAT (78: the bulletin notices' y was
computed from the board's x, so eight papers hung in the catering
office; the card-room placard hung past the lower deck's south
rooms; the calling card sat beside the desk at the height of the
top's underside; the pass counter touched neither wall on nothing;
chandeliers 30 cm under the ceiling with crystals 20 cm off the
core — a rod and a ring each now; coat hooks were vertical pegs 15
cm out from the pole; the time clock 15 cm off the wall; card
chairs and Table 17's benches without legs or plinths), the SCHOOL
FIELD (58: every player's head 7 cm above the shoulders, the chain
lying 13 cm over the turf, the coolers and transformer boxes 4–10
cm up, the helmet rack's two bars and five helmets in the air, the
car kit's rear bumper 11 cm behind every sedan — kit fix), the
SOLENADE GARDEN (50: Frank's "already built" east bench never was —
thermos, mugs, book, wear patch and plaque all sat on air; 36
blooms 27 cm over grass, soil now; the oak's trunk began 0.5 m
above its base; the diagonal benches' legs stood 0.9 m from their
seats; the salvia bed sat inside a flowerbed over its blooms) and
the CEDAR TOWER (41: the Estuary 7 print hung in the studio's door
gap; monitors 7 cm over desks; twelve dining chairs and five studio
chairs with no legs; the tower's glass bands 20 cm short of each
floor; the mug pegs inside the cabinets; the drone dock's EMPTY
cradle on nothing — kit fix, a rail post to post). Also the diner's
jukebox base sat 10 cm inside the bar counter (moved north; the
insert shot's target had dipped under the bar top when the quarters
came down onto the marquee).
THE AUDIT'S OWN LIES, four more: "canopy" in the foliage list ate
lamp canopies and the gas-station roof; the vantage audit's IGNORE
(`plinth$`, `band`, `far`) ate the sundial's plinth and the tower's
floor bands — the support audit no longer uses it, and `^far` names
(FarTown_E0, FarWood_N1) are sky by their own rule; "shimmer",
"sundisc" are sky. Each regex fix surfaced one or two REAL floats
that had been hiding behind a dropped neighbour (a circus rail 23 cm
outside its posts, a bandstand finial 5 cm short).
FOURTH PASS, same day — nine more rooms to zero (652 → 422): the
CARNIVAL (39: the big top was eight flat slabs touching neither the
pole nor each other — a cone now; six carousel heads hung off the
bodies' sides; the cage door 0.6 m past the wagon; Marv's pickup
with no wheels; the festoon eleven level stubs at eleven heights —
one hanging line), CENTRO (35: shelf-edge tag rails 28 cm out from
the shelves; aisle signs' wires outside the boards and 5 cm short of
the ceiling; the meat trays at the room's other end from the meat
case; the cooler door's LEAF dropped as foliage), the HIEROPHANT
CIRCUIT (29: belfry 40 cm over the facade; paddlewheel blades around
an axle touching nothing — side rims now; pews without ends; the
corridor's clock and coats off the deckhouse; the riverboat's upper
deck 10 cm short of its posts), the COURTHOUSE (27: the chambers
corridor "stub" was never built — placard, robe hook and bench hung
in open air, on the east wall now; the DEPT 3 placard 4 m outside
the room; pews, juror chairs, counsel chairs without legs; rails
without posts; scales' pans without chains), EL RANCHO (festoon
wires on nothing, bulbs 3 cm under them), the BUNGALOW (gauntlet
stencils 6 cm over the floor, string lights' cords level between
sagging bulbs — one sagging tube now; closet tapes past their box;
a tripod hub between three legs), the SALTY TOME (the hero pass
dressed an E-W counter — the real one runs N-S: ledger, terminal
and hold shelf hung beside it; pendants 5 cm short; couch,
radiator 9–12 cm up; a phone cord of four rings on nothing) and
the two NEXCORP stations (impulse rack items with no rack; the
no-smoking placard 0.4 m from its post; tubes 5 cm short; the
PENDING folder 0.6 m off its desk). Two insert markers were re-aimed
on the way (centro's meat case: the trays it framed had been on air
across the room). FIFTH PASS, same day — seven of the long tail to zero (422 → 326):
CHRISTIAN ICE (the ICE letters on a parapet never built — on two
posts and a rail now; a zero-length hot-gas pipe and a brine line
cutting a diagonal that touched neither end; the grandfather's
photo 0.4 m in front of the freezer it was "on"), the PARISH
CEMETERY (every course of the mausoleum's roof 5–20 cm over the one
below; the Menard markers 40 cm up BETWEEN the vaults; the gate's
swung leaf a metre inside the gateway, its y hand-typed as -8 in a
-9 fence), the ROADSIDE CHAPEL (steeple 30 cm over the roof slab;
bell rope 0.9 m short of the ceiling; votive rack on a stand now),
ELICIA'S (three door hinges in a 3 m opening with no door — a leaf
and a sidelight panel now; the light switch in the doorway; ring
light LEDs on a hoop), the MIXING GLASS (both tool stations 0.6 m
south of the bar arms they were "on"; wear patches inside the back
wall; the banquettes on plinths), MONTREAL (the drying rack, bowl,
mug and kettle south of the fridge on air — on the counter; the
bookshelf's sides 20 cm up) and the CLIFFSIDE CIRCUS (bunting: one
sagging tube; string bulbs on drops from their wire). THE USER'S VERDICT AFTER FIVE PASSES: "still getting pillows
floating away from beds … not seeing much difference"; "objects
inside other objects, too." Two things were true at once. The GLBs
are not in git — the Deck paste pulled and rendered the OLD builds
(every report that touches builders must carry the rebuild line
`list_stale_builds.sh` prints). And the gates forgave what the eye
does not: the 3 cm touch tolerance hid 1,644 more gaps of 1–3 cm
(kit helpers again: smoke detectors 2 cm under 22 ceilings, the
register 5 cm over 8 counters, fence boards 2.5 cm up, plant fills,
coffee pots 5 cm over their burners, sugar packets 2 cm over their
tray, the soda pyramid centred on its anchor); the overlap grammar
let a chair back sit 12 cm inside a wall and a box 25 cm inside a
locker. SIXTH PASS: TOUCH → 1.2 cm, embed/tuck/flex/contents →
0.06/0.20/0.15/0.15, the kit helpers fixed, both gates on
per-locale baselines that only come down: support 1,316, overlap
254. SEVENTH PASS: the two model chapters to ZERO at the new tolerances
(support 1,316 → 1,088; overlap 254 → 208). The kwik stop (88 → 0,
16 → 0 clips): the cigarette bands 4 cm in front of their packs,
peg bags 1 cm off their hooks, neon tubes 2 cm off the glass, the
four coolers hung 20 cm up (a plinth each now), the register's
drawer buried in the counter, the hose reel's coil 11 cm off its
bracket AND 8 cm into the wall, three decals inside the wall, the
quarter machines standing in the window tables' chairs (east of the
mat now), the magazine rack 20 cm into the coffee counter, the beer
stack 20 cm into the novelty cooler. The diner (56 → 0, 36 → 6
clips): the counter's top face was 1.08 while every dressing pass
placed from 1.10 — the top and its front raised 2 cm and 67 things
landed at once; the fans' arms and blades to the housing; the expo
counter ran 25 cm through alcove booth 1's bench (it starts east of
the alcove now); the bathroom bin straddled its partition; two
D'Ambrosio tables' chair backs sat inside the west wall; the back
bell inside the galley wall; the fretwork spans its two rails. The
diner's hull slabs are wall-class for the overlap gate (they join
the walls by construction). NEXT: roadside chapel 87 (mostly
CaneLeaf, now foliage) → recount; school field 65, centro stockroom
61, cedar tower 45, missing link 40, harmony commercial 35,
meadowlark 32, bindery 29, hierophant 29, riverboat 29; overlap:
pit stop 26, centro 11, crumpled barn 11, ben's bedroom 10.
EIGHTH PASS (batches 10–11): support 1,088 → 725; overlap 208 → 210
under a TIGHTER grammar (its rules alone would have read 247). Twelve
more rooms to zero at the 1.2 cm tolerance: the school field (the
bleacher benches 2 cm over their risers — 65 things landed; player
heads and helmets; Eileen's chair on the actual bench top; the
football ON its tee), the cedar tower (posters and photos 1–2 cm off
their walls; the mug pegs and folded clothes), the stockroom (every
box tier 1 cm over the tier below; the door coil 7 cm INTO the wall
header; the bale's straps as three faces ON the bale, not a slab
through it), missing link's exterior (dashes, puddles, bollards,
windows, bell, vent, awning, bench — all 1–3 cm short), meadowlark
(Salinas' cabin, Don's glass, the patrol stripe and light bar — kit
fix, on the roof now — the garage vent on its header), caldwell's
porch (the bike's tubes, the log pile, the fan blades, the radio ON
the rail, the blanket ON the rocker, the planter's wire reaching the
pot and its leaves hung from the rim), board lords (the flap, tool
rest, repair board, sanderling, mural patch, awning arms, the wheels
resting ON their bin), harmony commercial (crosswalks, kiosk sign,
cosmic glass; the four STOPLIGHTS hung from nothing 3.4 m over the
lane — a corner pole and an L-arm each, the stub reaching the head;
the far cars had no wheels and hung 15 cm over the lot), the
vehicle cab (climate knobs, the wheel's four diagonal spokes out to
the rim, the key in the column, the pedals' arms), lake palestine
(two reed clumps 12 cm over the water), miller's porch (the mug on
the side table), cosmic comics (the window paint, helm, face and
poster ON the glass in four layers; the statue shelf on the wall;
the register cord down its back face and along the floor — it cut a
diagonal through the counter; the CRT's cord up the wall, not into
the CRT; the manga panel BEHIND the books, which stood 6 cm inside
it). And CENTRO GROCERY, a re-plan: the 2.4 m MEAT CASE sat in the
checkout lane (queue posts, candy rack and card terminal inside it,
its own back 15 cm in the S wall), the DELI CASE sat inside the
BAKERY counter, a fourth gondola (Aisle_2) sat bodily INSIDE
Aisle_0, and the cart was parked through Aisle_0's face — all
unreported, because the overlap gate's contents rule exempted any
pair whose one name held "case" and its assembly key was the first
name segment alone. Now: meat case on the E wall's north end (the
docstring's own placement), deli along the S wall between the
entrance and the queue (the W wall is the dry-goods run and the
produce island), chest freezer under the S window, bakery clear of
the checkout, the cubby on the cashier's side of the counter (it was
18 cm inside the front), Aisle_2 removed, the cart in the corridor
its wheel lines already lead to, both cords ON the top and around
the cubby, the grille on the wall face; the meat-case insert marker
re-aimed. Grammar: contents must be under 1 m and fit; an integer
second segment joins the assembly key (`Aisle_0`), a part name does
not. Three builders had been broken by comment-swallowing edits
(SyntaxError reads as "partial" in a skimmed report) — compile all
before any audit now. NEXT (support 725, by locale): bindery 29,
hierophant 29, riverboat 29, asylum ward 19, new orleans bar 19,
estuary_7_template 18, simon 17, le roulant 16, roberts house 16,
roberts kitchen 16, frog knows best 14, natalie 14, both nexcorp 14,
pharmacy 14; overlap (210): pit stop 26, crumpled barn 11,
courthouse 10, centro break room 10, ben's bedroom 10, riverboat 8,
graustark 8, mixing glass 7.
NINTH PASS (batches 12–13): support 725 → 567, overlap 210 → 209.
Seven more rooms to zero. The BINDERY (the door bell 20 cm over the
door; the open book 14 cm over its stack; the Borges sign in the
open at y 7.8 where the cases end at 6.9 — on shelf 4 now; the
ladder's brass rail on three brackets). HIEROPHANT (the bandstand's
balusters 5 cm over the deck and 2 cm under the rail; the town
car's side glass outside its greenhouse). The RIVERBOAT (the station
plates 1 cm over every deck; the office stair's stringers and rails
3–9 cm outside the treads; the milk crate, mixer head, desk lamp,
glass, books, pencil, time cards, catering papers). The ASYLUM (the
gurney's frame 40 cm over its wheels — posts now; Ward 5's bed with
no legs; the nurse desk a top on nothing; both wheelchairs' seats
floating between their wheels; Emile's cart 15 cm up; the boarded
cupola pane at the room's SOUTH end while the cupola is at the
north — "we approximate"; the bed-rail hand wear 20 cm past the
bed). NEW ORLEANS BAR (the bottle wall 40 cm off the wall, on the
mirror now and short of the TV; pendants 10 cm short of ceiling and
shade; two lamp sets sharing one name; stools, table post). SIMON'S
(the armchair wear 1.5 m from the armchair; the remote on a coffee
table that did not exist — built; the non-renewal form on a counter
at the wrong wall; the coat peg inside the wall, and once it came
out, the boot that had hung THROUGH the wall; banker's boxes, lamp,
faucet, shirt, phone, pull cord). The ROBERTS KITCHEN (the south
wall's halves 40 cm short of the door header with the hinges in the
hole; the VCR stack, sill, stools, magnets, towel). The support
audit counts "streak" as sky (a light streak is not a solid). NEXT
(support 567): estuary_7_template 18, le roulant 16, roberts house
16, frog knows best 14, natalie 14, both nexcorp 14, pharmacy 14,
daigles 13, equipment shed 13, static drive-in 13; overlap (209):
pit stop 26, crumpled barn 11, courthouse 10, centro break room 10,
ben's bedroom 10.
TENTH PASS (batch 14): support 567 → 517, overlap 209 → 209 with
MORE seen. The recorder never rebound a hand-rolled builder's
sphere helpers — every vendored sphere in the game (the diner's 27,
harmony terrain's canopies and globes, the roberts house's bird)
was invisible to every gate. Hooked, and the overlap gate judges a
sphere by its ball, not its cube. The DINER's six booths each had a
table lamp built INSIDE the ceiling pendant (asset pass 3 read the
invisible pendant's light as "floating bare"); gone. Harmony
terrain: a house in the skatepark, a lamp pole in a tree trunk, a
stop sign in a conifer, a globe in a street tree, a flower bed in
the church's stalls. Le roulant, the roberts house and the estuary
7 template (its land plate had been listed as sky) to zero.
ELEVENTH PASS (batch 15): support 517 → 447, overlap 208. Frog knows
best (a 3 m wall opening around a 1 m door — jambs and header now;
the till sheet over the porch; the OPEN sign 2 m out on the porch),
natalie, both nexcorp stations, the pharmacy — all to zero. NEXT
(support 447): daigles 13, equipment shed 13, static drive-in 13,
bayou lighthouse 12, chillwave 12, coach k 12, bungalow 11, daily
grind 11, foxhole bar 11, little switzerland 11, pit stop interior
and office 11, wgur 11; overlap: pit stop 26, crumpled barn 11,
courthouse 10, centro break room 10, ben's bedroom 10.
TWELFTH PASS (batches 16–17): support 447 → 371, overlap 208 → 204.
THE COUNTER KIT BURIED EVERYTHING 2 CM: `make_counter` returned
base+height+0.04 as the top while its top slab ends at +0.06, so in 22
builders every register, bell, pot, pad and paperback dressed from
the return value sat 2 cm INSIDE the counter — and the overlap gate's
"resting on a surface" allowance (10 cm) waved it through. Fixed in
the kit; three hand-tuned items that now hovered were re-seated.
Rooms to zero: DAIGLES (taps, the pool cue ON the rail, the six-steps
sign inside the doorway, Lou's mug by the front door at bar height,
the cigarette burns past the bar's edge), the EQUIPMENT SHED (sled
arms on nothing, the liner's handle, helmets, cones, the bulb, the
roster sheets 6 cm inside the wall), the STATIC DRIVE-IN (a 4.2 m
wall opening around a 1.4 m window — sill and header now; the candy
case in the gap between the counters; Natalie's notebook a second
copy of the sigil notebook, outside the building; the mini-fridge in
the south wall; Ollie's note on a booth door that was never built),
the BAYOU LIGHTHOUSE (the clock past its wall slab's end; the lens 17
cm over its drive with 2 cm gaps between rings), CHILLWAVE (the kit
counter runs N-S but its register and bell were placed for an E-W
one — one off each side; the reading glasses inside the counter
slab; the kick scuff inside the counter front), COACH K (the fan's
blades short of the motor, the photo standing inside the laundry
stack, nightstands 2.5 cm up). The thermostat kit set every
thermostat 1.25 cm off its wall. A counter close-up's subject no
longer includes scuffs, outlets and cords named for the counter.
NEXT (support 371): bungalow 11, daily grind 11, foxhole bar 11,
little switzerland 11, pit stop interior and office 11, wgur 11,
courthouse 10, diego bedroom 10; overlap: pit stop 26, crumpled barn
11, courthouse 10, centro break room 10, ben's bedroom 10.
THIRTEENTH PASS (batches 18–22): eleven more rooms to zero on the
support gate and the two worst overlap rooms to zero clips. The PIT
STOP (26 clips → 0: every booth's back 10 cm inside the west wall
and 13 cm inside its window frames; the lot cars 10 cm into the
same wall from outside — and with no wheels, so moving them off the
wall left them hanging; the LA pickup with no wheels either; the
hood towel through the hood), the COURTHOUSE (10 floats and 10 clips
→ 0: the wainscot built INSIDE the walls; a second, older gavel
sharing the real one's names; the tables' bodies 3 cm up), the
BUNGALOW (door headers short of door and wall; the closet boxes'
bottom row 2.5 cm up; the headboard over the legs; a mirror insert
shot from outside the house at 2.4 m), DAILY GRIND and FOXHOLE BAR
(each declared its counter's top as the slab's CENTRE and dressed
from it, so the register, pots, pitchers, cup stack and taps sat 3
cm inside the counter; the daily grind's register stood past the
counter's end; pendant cords short of ceiling and shade), LITTLE
SWITZERLAND (every chalet window, flower box and brace 2–4 cm proud
of its facade; a snow strip left hanging 16 m out after its ridge
was deleted), the PIT STOP OFFICE, DIEGO (his laptop and letter were
dressed for the desk's old position and hung in mid-air 2.5 m from
it), and WGUR (the kill switch, coffee maker and caution tape at
guessed coordinates — one outside the building; the tower's
obstruction lamps in its middle on nothing). A scan for "slab
centred on the height the dressing uses" found seven builders; in
five the dressing already sat right (placed with the half-thickness
added) and the change was reverted there — a scan is a lead, not a
fix. Audit: the foliage drop list no longer drops curtain RODS and
other hardware; backdrop terrain (hill, ridge, sea) holds what
stands on it; `Part_*` partitions are walls to the overlap grammar.
NEXT: gym weight room 10, new orleans office 10, salty tome 10, cafe
olimpico 9, cosmic back office 9, henderson garage 9, hospital room
9, darkroom 8, houston design studio 8, houston office 8; overlap:
crumpled barn 11, centro break room 10, ben's bedroom 10.
FOURTEENTH PASS (batches 23–28): eleven more rooms to zero. The GYM
(the dumbbell rack's two shelves on no frame; a pulldown seat and
thigh pad on no post; fixtures 5 cm under the ceiling; the depth
chart 7 cm inside its wall), CAFE OLIMPICO (every bentwood chair a
seat at 44 cm with no legs; the booth a seat and back on nothing),
the NEW ORLEANS OFFICE (six shelves with no sides; its street view's
balcony, shutters and gallery rail count now — backdrop buildings
hold what is mounted on them), SALTY TOME (the bookcase helper stood
every book 1.5 cm above every shelf — some 300 books; the kick scuff
through the N-S counter again), the COSMIC BACK OFFICE, the
HENDERSON GARAGE (the bass 20 cm over a stand that had only a foot;
the opener motor hung from nothing; the rack tom over the kick), the
HOSPITAL ROOM and HOSPICE (the bed kit set its side rails 4 cm
outside the deck; the IV bag under its hook; blanket creases 80 cm
off the bed; a clipboard and a door-kick scuff in a doorway with no
door), the DARKROOM (the enlarger head stacked with gaps; prints
under their clips; the timer inside the wall and through the
enlarger), both HOUSTON rooms (chair backs 3 cm over seats; sticky
notes 34 cm in front of the monitor they were stuck to). The
security-camera kit hung every dome 4 cm under its ceiling, and four
rooms mounted it 10 cm into the east wall.
NEXT: the rooms at 7 (finn, graciela, missing link interior, new
orleans room, roadside chapel, sam bedroom, hans bakery); overlap:
crumpled barn 11, centro break room 10, ben's bedroom 10.
FIFTEENTH PASS (batches 29–30; support 176 → 123, overlap 151 → 120):
the seven rooms at 7 to zero. FINN (a crow and its sill marks on a
sill the window never had; bed crates 4 cm off the floor), GRACIELA
(the rosary 3 cm over the spread), MISSING LINK (every booth seat a
cushion at 39 cm on nothing — plinths added; the ticket rail on air
15 cm off the wall, now along the menu board), NEW ORLEANS ROOM (the
letter, pen and envelope at the desk's OLD position over the pillow;
the headboard 2 cm over the platform; the bulb, socket and cord in
three pieces), the ROADSIDE CHAPEL (the altar top over its base; four
of six votives standing off the rack's edges), SAM (two of five fan
blades off the hub — blades rotated now; the model kits stacked with
gaps; the skateboard tipped SIDEWAYS by `pitch`, 10 cm off the wall),
HANS BAKERY (hood, scale, tool rail, calendar, drawers, and two coat
pegs in the air in front of the pass window). And the three worst
overlap rooms to zero: the CENTRO BREAK ROOM's whole kitchenette faced
the wall (counter doors, upper cabinet doors and fridge doors on the
wall side, the run 8 cm inside the W wall, the fridge 16 cm into the
N wall, the bulletin board inside it, the dishwasher half inside the
counter carcass); BEN'S BEDROOM (the headboard, the desk and the depth
chart inside their walls; the "cracked" door was a shut leaf with its
knob 56 cm in front of it and a slot open to the ceiling beside the
opening — the leaf swings in on its hinge now); the CRUMPLED BARN
(the automaton cabinet was one solid block with Jiggles inside the
wood — built hollow now; a post through a fallen roof plane; the
fallen beam through the rubble).
NEXT: the rooms at 6 (bar exterior, briar falls, caldwell radio room
night, foxhole dressing room, miller office) and 5 (christian ice co,
elicia apartment, kowalski backyard, parish cemetery, safehouse
bedroom); overlap: graustark 8, riverboat interior 8, mixing glass 7,
the diner 6 (a model chapter — first), harmony terrain 6.
SIXTEENTH PASS (support 123 → 75, overlap 120 → 81): THE BURIED
WINDOWS. `make_window` built its glass and frame toward −Y/−X from
the anchor, which is into the wall for every SOUTH and WEST wall; and
callers that anchored on the wall's centre line buried theirs on any
wall. A scan for "window glass wholly inside a wall solid" found 43
windows in 34 rooms that could not be seen from the room at all —
the Deck has been rendering those rooms as blank walls. The kit takes
`room_dir` now (default −1, the old behaviour); all 43 are anchored on
the room face and built toward the room (an AST rewrite kept the
builders' symbolic anchors: `ROOM_D - 0.10`). Rooms fixed by hand: the
DINER, a model chapter, to zero (its first alcove booth lay inside the
galley — tile, grout and ticket rail through it; a ticket through the
soda fountain; the soda gun on the customers' side inside a stool
back), MIXING GLASS (booths 1.50 long on a 1.42 pitch; the ice chest
inside booth 0), GRAUSTARK (a hummock in the sinkhole; the flagstone
path under the lighthouse deck), the RIVERFRONT (every E sewer grate
laid across the road 30 cm into the sidewalk), the RIVERBOAT INTERIOR
(stairs down through a main deck with no stairwell — a hole now; the
back bar a solid 2 m block 50 cm off the deck with 60 bottles INSIDE
it behind the mirror, across the side door; corridor walls, carpet,
walk-in and intercom in the hull), and the rooms at 6 and 5: bar
exterior, briar falls, caldwell radio room night (the mic boom four
pieces in the air), foxhole dressing room, miller office (the
chandelier's axis-aligned arms missed four of six cups), christian
ice co, elicia apartment, kowalski backyard. AUDIT: the overlap key's
index rule needed three name segments, so two-segment siblings
(Aisle_0 / Aisle_2) were one assembly and Drum_0 a stranger to its
own Drum_0_band; a bare numbered whole now owns its parts wherever
the number sits (NapkinDispenser_8 / NapkinDispenser_Slot_8). The
suite FAILS on a builder whose main() raises under the recorder — the
riverboat passed as "clean" through a NameError that would have broken
the Deck build. The support gate lets things drawn in flight
(butterfly, moth, firefly) fly. Walls are SOLID in this pipeline, so a
window is a lit panel on the wall, not a view out — except the CABIN
KITCHEN window, whose crow ("seen through the glass… on the outside
sill") had never been in any frame: its wall is built round a real
opening now, with an outside sill for the bird; the lens audit treats
glass as see-through. Four markers re-placed where the new windows
stood in the frame (cabin crow ×2, cabin-bed closeup, natalie desk).
NEXT: parish cemetery 5, safehouse bedroom 5, then the 4s (carnival
lot, cosmic comics, faust apartment, maya bedroom, miller garage);
overlap: the new worst in overlap_baseline.json. Deck-verify the 43
windows (the first frames of those rooms with glass in them).
SEVENTEENTH PASS (support 75 → 45, overlap 81 → 75): THE BURIED
BASEBOARDS. `make_wall` built its baseboard 6 cm thick, centred 6 cm
off the wall's centre line — wholly inside any 20 cm wall, whichever
side was asked for. 398 baseboards in 79 rooms had never been
visible (the scan: a `<wall>_Base` wholly inside `<wall>`). The kit
sets it ON the face now, 1.2 cm proud (under the overlap gate's
1.5 cm abutment tolerance, so furniture set flush to a wall still
reads flush); then 119 walls in 61 builders whose baseboard_face_sign
pointed OUT of the room were flipped (AST rewrite: the kwarg, or the
loop tuple that feeds it). Five hand-copied 0.06/0.06 baseboards
(kwik stop ×3, three spandrels) and the cabin's new N wall fixed by
hand. Rooms to zero: parish cemetery (both lecterns' tops over their
posts; Louis's engraving on the face pressed AGAINST the vault, his
candle inside it — turned to the path, the insert with it), safehouse
bedroom (the cork wall 2.5 cm inside its wall; the IV line a rod in
the air, now bag → bed in two runs clear of two inserts; the duvet
"hands" creases 30 cm off the foot of the bed, left behind when the
bed moved on 09-10; a 0.44 nightstand in a 0.32 gap), carnival lot,
cosmic comics (clock, payphone — the kit's hood hung over nothing —
the purple rack, the long boxes inside the counter), faust apartment,
maya bedroom (desk and vanity into the E wall, the mirror on air, the
notebook and packs at the desk's pre-09-07 position), miller garage
(the shop light's chains hung from no joist; a mower handle plate on
air; bike seat and bars on no posts). marker_reaim.py re-aimed the
vanity insert at a drawer pull — reverted by hand: the reaim tool
picks the nearest named part, not the prose subject.
NEXT: cabin interior 3, grunion beach 3, jesse bedroom 3, kowalski
kitchen 3, school newspaper 3, tideline survey 3; overlap: the new
worst; Deck-verify the windows AND baseboards (the first frames of
most rooms with a baseboard in them).
EIGHTEENTH PASS (support 45 → 27, overlap 75 → 56): the six rooms
at 3 to zero, and the overlap top list. CABIN (the oil lamp's chains
stopped 1.4 cm under the ceiling — the whole lamp hung on nothing;
the ladder stood 13 cm inside the kitchen counter under the loft's
open end — it stands in front of the counter now and hooks over the
loft beam), GRUNION BEACH (a 70 cm strip of nothing between the tide
gleam and the sea, the first surf line floating over it), JESSE
(the bedside lamp and both notebooks left at y 2.95 when the bed and
nightstand moved to the N wall on 09-10 — 1.2 m from their table; the
lamp's practical light moved with them; the guitar case 25 cm into
the S wall and under the stand), KOWALSKI KITCHEN (couch base, oven
bar, mower; the upper cabinets and the hot-sauce cabinet 9.5 cm into
the N wall), SCHOOL NEWSPAPER (pages at stacking heights over nothing),
TIDELINE SURVEY (the kelp floats; and a PRACTICAL LIGHT on a kelp float
— practical_author read "Bulb" as a light bulb: removed, and
practical_author now ignores kelp/seaweed/flower/tulip/onion/garlic).
The KWIK STOP, a model chapter, to zero: TWO Slurpee machines built
into one spot (the fountain kept, set on the counter it hung 27 cm
over; the duplicate barrels removed); the cardboard end-cap pyramid
built on the same spot as the aisle's end-cap shelving (removed — the
shelving is the display); the strip curtain hanging 1.3 m north of the
back door, through a locker and into the N wall (on the back door's
frame now). GRACIELA (crucifix and Guadalupe inside their walls), LENA
(the whole kitchen run 10 cm inside the W wall — shifted, the faucet
clear of the now-visible window, the pan flat on the wall; table
chairs at 1.0 m pulled to 0.78; the lamp cord routed round the shelf).
STILL IN THE KWIK STOP'S NE CORNER: a heap — stockroom boxes, shelf
backboard, products into the N wall, the trash bag, the break bench
and lockers, all in one 1.5 m corner. Re-plan it next pass.
NEXT: the kwik stop NE corner; the rooms at 2 (cliffside circus, el
rancho, ember ash office, henderson porch front, new orleans
apartment, nightmare cell, ramos kitchen, sapo falls); overlap: the
new worst (harmony terrain 6, accretion basement 5, cabin road 5, new
auburn road 5).
NINETEENTH PASS (support 27 → 0 — NO FLOATING COMPONENT IN ANY OF THE
114 MEASURED LOCALES; overlap 56 → 34): the KWIK STOP's NE corner
re-planned (lockers flush on the N wall, the bench on legs, the trash
bag between them and three cartons stacked N of the back door, clear
of its swing; the "seen through the curtain" stockroom shelf and
products removed — there is no stockroom in the model; a broom and mop
that stood through the bench moved to the N wall; three back-door
hinges floating mid-room at an old door position moved onto the
door). The rooms at 2 and 1, eighteen of them, to zero — among them
the NIGHTMARE CELL's only light (fixture, tubes and cage 5.5 cm under
the ceiling), SAPO FALLS (a strip of nothing between shore and pool;
the tepui flank began 5 m up), NEW ORLEANS APARTMENT (the bass on no
stand), EMBER ASH (an office chair whose five feet and post touched
nothing), LACOMBE (the tow boom 50 cm over the bed). Overlap: HARMONY
TERRAIN to zero (ticket booths on the end zone, a valet lot over tennis
court 1, a framed slab under a house, a dumpster in the car wash wall),
ACCRETION BASEMENT (block-course lines through the N wall), NEW AUBURN
ROAD (the far ground sheet lay OVER both roadside ditches — they were
never visible; the sheet is cut round them), CABIN ROAD. AUDIT: the
"closet tools" rule excused a broom or mop against ANYTHING to 20 cm —
tool against tool only now; creek/river/stepping stones may root in the
ground, lawn sprinklers sit flush in the lawn (named narrowly).
NEXT (the support gate now holds every locale at 0 — any float is a
regression): overlap bayou lighthouse 3, finn apartment 3, small wood
road 3, then the 2s (cape perpetua, carnival lot, coach k, hierophant
circuit, pharmacy, solenade garden). Deck-verify the whole run
(windows, baseboards, the rebuilt corners).
TWENTIETH PASS (support 0 → 0, overlap 34 → 0 — BOTH GATES AT ZERO IN
EVERY BUILDER; both baselines are now all-zero, so ANY float or clip
anywhere fails the suite). THE RECORDER HAD BLOBS WRONG: every
make_blob recorded as a round ball of its radius, ignoring `squash`
(default 0.8) and noise — 25% too tall by default, 82% for a flat
duffel. The recorder now builds the kit's own vertex ring (same hash)
and takes its exact extents. That removed false clips (finn's duffel
"13 cm into the floor") and exposed 48 REAL floats the round ball had
hidden: blobs seated at "centre = radius" hang radius x (1 - squash)
over the ground — tideline boulders and pool pebbles, highway 101 rock
rubble, salal and the headland, kestrel cliff rocks and hedges, lake
palestine reeds, meadowlark's black cat, hans's flour sacks — all
seated by their squashed height now; and the crow kit's back toe hung
2.2 cm behind its leg, held only by the over-tall body box. The 34
overlaps: the bayou lighthouse (a SECOND calendar inside a wall segment
— removed; the lens-drive weight hung to the bottom of its drop through
a stair tread — wound up now), carnival festoon cable and bulbs through
the tent pole and the carousel finial, walls (asylum hatch, bungalow
tub, coach k headboard and dresser, the daily grind four-top, foxhole
cymbal, new orleans room dresser, pharmacy file, pit stop monitor,
solenade tap, nexcorp restroom shell), henderson's BASEMENT DOOR dark
inside its wall (never visible), maya's CAVITY and ENVELOPE inside the
floor slab (never visible — on the planks under the lifted board now),
pharmacy's storefront glass inside the S wall, small wood road's
ditches under the far-ground sheet (cut round them), hierophant's curb
inside the wharf deck, skatepark's seam under the stairs, elicia's
camera lens into the wall. The window scan widened (glass inside a
wall's THICKNESS and overlapping it along the run, not only "wholly
inside one segment") and found three more buried windows: cafe olimpico
×2, elicia SE. Grammar: bluff rock roots in ground; driftwood half-
buried in sand; a floor slab set into its earth mound.
THE CONTACT SHEET (2026-09-24, from draft 19's build, 1,529 frames,
141 presets) was read as one establish frame per preset. What the gates
could not see and the frames showed: FLAT SLABS FLOATING IN THE SKY on
the exteriors (vehicle cab side, skatepark, and others) — the far-band
kit (`make_far_bands`, 37 callers) passed half-extents to make_box as
sizes, so every horizon band stood a quarter of its height OFF the
ground and every crown hung over its band; the support audit never saw
it because "far" was in its SKY list. The kit grounds its bands now
(footprints as built — the scenes were composed around them); "far" is
out of the SKY list, and the nine other far pieces that then floated
were fixed (the diner's far storefront signs 10 cm off their facades,
the bar's far block 6 m up, the sapo falls far tepui 4.4 m up, little
switzerland's two "snow caps" 20 m out capping ridges 260 m away —
deleted). The riverfront park's north far-town band stood across the
frontage road and through the real north town; west only now. Also on
the sheet, for the next direction pass: establish frames facing a wall
or near-black (crumpled barn int, nightmare cell, d'ambrosio's formal,
cabin interior bed, chapel exterior), and highway 101 + small wood road
were SKIPPED (their GLBs did not load on the Deck) — rebuild and check.
NEXT: Deck-verify (the whole support pass has not been seen on the
Deck; windows, baseboards, the kwik stop corner, the rebuilt lighthouse
weight, the grounded horizons). Then back to THE DRAFTING PROGRAM's
visual backlog with both gates holding at zero.
TWENTY-FIRST PASS — BUILDS THAT DIE IN BLENDER. Every gate ran
builders under the RECORDER, whose stubs accept any arguments; a builder
that crashes in Blender passed all of them and just left its GLB
missing. NEW GATE blender_dryrun_audit.py runs every builder through its
REAL kit code against a small stand-in bpy (godot/tools/audit/
blender_dryrun/: meshes from the kits' real vertex lists, faces checked
for bad or repeated indices, exported only if main() finishes). It
found TWO builds that had died in Blender since the twelfth support
pass — chillwave_interior and missing_link_exterior — both the
trailing-comment trap (a comment pasted mid-call swallowed make_cyl's
colour). 121/121 pass now, in ~30 s; it runs in the suite. The 09-24
sheet also skipped highway 101 and small wood road: both build cleanly
here, so contact_sheet.sh now runs `godot --headless --import` first —
a run of the project does not import new or changed GLBs. Cameras from
the sheet: D'AMBROSIO'S FORMAL stood OUTSIDE the diner (an 09-03
automatic re-vantage picked x -15.4, past the west wall) — inside the
partition door now; the CRUMPLED BARN's "shaft of daylight" was a solid
pale slab in front of the interior camera (vertex alpha does not render
translucent) — removed, the tscn's OmniLight is the light. Nightmare
cell (the tall dark cell looked up at) and cabin bed (the waking POV)
read as intended.
NEXT: a fresh contact sheet from this build (the grounded horizons, the
two recovered builds, the two roads), then the direction backlog.

**2026-09-19 · DESIGN · the two decorative checks made real, the first
remembered choice.** Nate's basement (ch6) and Tem staying (ch8): the
empathy checks' pass branches land on a line of their own now (a
think beat before the shared continuation) — `vn_skill_audit` reports
0 decorative. The apology (ch8): `vol7_ch7_apology_heard` was set by an
unconditional node at the end of Finn's speech, so no callback could
mean anything; it rides the two options that HEAR the apology now
(listening, and the passed empathy check) and Roy's scene remembers
either way (a when_flag line and its when_not_flag twin — Finn clears
the bowls like a man let back into a kitchen, or carefully, unsure of
his welcome). Loose flags 43 → 42. The splice: nodes inserted by raw
text at the file's own indentation, every goto/pass/fail ≥ the
insertion index bumped, the check's pass re-pointed; json.loads and a
node-by-node text comparison before writing. NEXT: the other loose
choice flags the same way — vol 1's faust_* set (asked_for_joan,
black_lodge, dose, dream_woman_held, elem_favored, met_dickens),
each read once in a later scene of its own volume.
SHIPPED same day: `faust_dose` (2 | 3 — `when_flag` + `is`) in the
pharmacy mirror; `faust_elem_favored` (fire | water | air) in the
painting's second scene, each element claiming its own listener;
`faust_dream_woman_held` in the lullaby (held: her arm's weight; not:
alone in the middle of the bed); `faust_asked_for_joan` in the waking
(Joan: it is tomorrow / you went back to your friends). Loose flags
42 → 38; the rest are `*_complete` progression markers and flags set
on every path (black_lodge, met_dickens) — not memories.
AND TWO BROKEN CHOICES, found on the way: vol1_ch1_s2's second option
and its passed logic check pointed at `jump vol1_end` nodes (the
Stranger's written replies never played; the volume ended), and
vol2_graveyard's "I'll sell it." pointed two nodes BACK at the think
before the choice, re-opening it forever; the other two gotos were two
short and skipped Jo's first reply. Every goto/pass/fail in the game
was a hand-typed index nothing checked. Fixed, and gated:
`vn_target_audit.py` (BACKWARD · OOB · ONTO_END · SELF at zero;
ONTO_JUMP listed as info — "Listen. Say nothing." legitimately jumps).
The graveyard's decision is a memory now (`vol2_house_decision` =
sell | wait | ask, read three ways in vol2_end).
AND THE MODEL-CHAPTER VERB COINS (the bible's queue, §6): the diner's
jukebox in ch0_closing (LOOK AT · PLAY B4 · LEAVE IT — it plays the
booth-six song unfed), the cathedral's workbench right after the
Magician's workbench beat (LOOK AT · SORT PARTS — by feel, not value
— · LEAVE IT), the Henderson stove at the prints chapter's kitchen
door (LOOK AT — one burner cleaner since June — · PUT THE KETTLE ON ·
LEAVE IT). With the kwik stop's cooler, all four model chapters carry
one; seven coins in the game; every verb sets and hides on its own
flag, the exit lands on the beat that followed. No new shot cues (the
diner and the Henderson kitchen have no jukebox / stove markers —
the placing narrate names the object without cueing a lens).
AND THE INVENTORY (draft 1, same day): items are flags named
`item:<name>` (they save with everything else); an option may carry
`item` (picked up — a TAKEN toast), `drop_item` (used up) and
`needs_item` (shown only while held); HudBar shows the held items as
a strip of small caps after the chapter whisper. The first item: the
workbench coin's fourth verb POCKET A PART takes a capacitor; at the
riverboat a `needs_item` option fits it under the river (the hum
changes key, it does not stop), uses it up, and the scene's end
remembers it (`ch1_river_capacitor` read by a when_flag line). NEXT
for the inventory: an item per model chapter (the napkin, the
cooler's bottle, the stove's kettle) and one use each across a
chapter boundary; `drop_item` on a wrong use with a funny line, not a
fatal one.
SHIPPED same day, the kwik stop's: TAKE TWO on the cooler coin puts two
Powerades in the pocket; at the dumpster the handing-over line plays
two ways and the held one uses them up (a narrate may carry
`drop_item` now — a thing handed over is a line, not a choice). The
Henderson kettle is a remembered choice rather than an item: the
sleep chapter's kitchen sees it full on the clean burner, or cold on
the burner nobody uses. The diner's napkin stays prose: John does
not return in vol 5 after ch0, so nothing could use it. The
consequence map lists items now (`item:<name>` set by `item`, read by
`needs_item` / `drop_item`).
AND COMMUNITY PLANNED (§6's row): RUST_CODE's masthead is in the
zine's hand now — lowercase, hand-ruled, "news from harmony creek ·
the letters column lives here · cut · pasted · photocopied · two inks
you can't see from here" — instead of figlet block capitals that read
as any BBS; and RN_010 "to the editor: 6:12" (W4) answers the
prelude's `[trip:]` sprinkler beat: a Meadowlark Circle lawn writes
that the sprinklers come on at 6:12 not 6:15 and that the cracked
head on the Miller lawn is the association's, on the list since
March, and still throws one last arc that catches the light; m.d.
corrects the reprint and draws the head. Data only (json.loads-
validated, the thread shape of RN_001); no engine change.
AND THE GAUNTLET'S TEMPO ROW (draft 1): the reading under every ending
gets a fourth line, THE CARD — this arcana's record across runs (runs,
wins, the best clock: "best 5 of 8 turns · 3 runs, 1 won", "a new
best", "first run · the room will remember the next one"), kept in
`SaveSystem.get_record / set_record` (user://progress/records.json,
beside the unlocks). The score bursts on chained rounds wait for a
Deck look at the board (a burst is feedback, and nothing here has been
seen).

**2026-09-17 · DESIGN · the consequence map, and SKILLS EARN (draft 1).**
The VN's game layer drawn for the first time (`consequence_map.py` →
`lore/_VN_CONSEQUENCE_MAP.md`): 28 choices, 5 skill checks, 58 flags
of which 43 are set and never read. The headline defect: NO NODE EVER
RAISED A SKILL — every labelled check option took its fail branch since
the first build. Now an option trains the skill it exercises (`skill`
on a choice option; once per playthrough per option; plate label, HUD
dots, toast), 70 options tagged, the five checks re-sized to what is
earnable before them, and `vn_skill_audit.py` gates CANNOT_PASS /
NO_EARN / UNKNOWN at zero in the suite. NEXT: the 43 loose flags paid
off one callback line at a time (vol 7 first); the two decorative
checks (pass = fail) given a real pass branch; the verb coins on the
four model chapters.

---

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
| Cosmic Comics shop floor (vol 6, 12 placements) | 4 (DRAFT 4 09-18: U-wire spinner pockets, lathe dome + bell, kit stool + table, lidded longboxes; first WEAR (paths, elbow strip, bin scuffs, stool ring, tape ghosts); D3 switch + register cord + the corner CRT built and glowing; D5 sidewalk/curb/parked car/streetlamp/storefronts) | draft 5: bins as real bins (lip, dividers, comics at a lean); key-wall bag rims; posed statues; pegwall silhouettes; the checkerboard worn through at the door; Deck: ten-AM establish (the Galactus bars), `insert dome` |
| Cosmic Comics back office (vol 6, 11 placements) | 4 (DRAFT 4 09-18: turned desk legs + apron, monitor on a stand, drawer pulls/labels, the bulb as a bulb with chain + pull, carafe + chair seat as profiles; first WEAR (entry paths, caster oval, forearm patch, coffee rings, ink, pin holes); D3 power strip + cords from everything; the two phantom fluorescents removed) | draft 5: longbox tops as comics at a lean; the light table lit from within; corkboard pages drawn; the office door's knob + hand patch; the alley past the service door; Deck: establish + `insert notebook` under the bulb |
| Kowalski kitchen (vol 6, 7 placements) | 4 (DRAFT 4 09-18: gooseneck faucet, burners/knobs/oven bar, pendant as canopy+cord+shade+bulb, fridge pull + photo, shakers; first WEAR incl. Daisy's spot; D3 two switches + three cords; D5 backyard + neighbour's yard; the phantom overhead fluorescent → the pendant's bulb, the under-cabinet light lit) | draft 5: upper cabinet doors with pulls (one ajar); dishes in the rack; stair risers + runner; the TV on a stand; Deck: the ch19 establish under the under-cabinet light |
| Caldwell porch at night (vol 6, 7 placements) | 4 (DRAFT 4 09-18: turned balusters + bottom rail, both rockers on curved runners, caged carriage lamp, side table on turned legs, bike spokes + hubs, kit slow car; first WEAR; D3 switch/conduit/hose bib; D5 hedge, streetlamp, houses across) | draft 5: screen door as mesh on a frame; bark on the logs; the planter's chain; the streetlamp's sodium practical; Deck: night establish + `insert radio` |
| Vehicle cab (vol 6, 7 placements) | 2 (DRAFT 2 09-18: treads + lugs, lathed posts, kit sedan, tapered scrub, planked picnic table with initials; the cab's WEAR — heel mat, bolster shine, dust line, door ding, deeper ruts; D3 charger cord to the 12 V socket, key ring, the pine tree) | draft 3: the 09-03 targets — headlight cones + night dash-glow, a rear-bench preset, rain on the windshield, the Civic hatch; Deck: the cab establish at night |
| Centro Grocery aisle (vol 6, 9 placements) | 4 (DRAFT 4 09-18: wire carts, cone, round fruit, scale with dial/pan/chains, lathed queue posts, hand-truck wheels, cooler-door handle; first WEAR; D3 floor box + cords, EXIT sign + conduit, compressor grille, floor drain; D5 the lot — asphalt, walk, curb, stripes, a car, the corral, a lamp post, the strip across) | draft 5: aisle facings as products with faces; cooler doors with handles + price strips; meat trays' contents; donuts as rings; bag rack; Deck: establish + `insert scanner` |
| School field at dusk (vol 6, 8 placements) | 4 (DRAFT 4 09-18: tapered poles on base plates + conduit + transformer box, hooded lamps, lathed fence posts + mesh, four kit vehicles, folding chair; exterior WEAR — hash band, goal mouths, bench dirt, sideline path, gate tread; D3 field-house door light + practical, scoreboard cable + box, goalpost pads) | draft 5: spectators/players as posed figures (a `_props` class); bleacher underside; press box; scoreboard digits; lot lamp practicals; Deck: dusk establish + `insert corkboard` |
| Maya's bedroom (vol 6, 10 placements) | 4 (DRAFT 4 09-18: turned desk legs, a real desk lamp, pulls, perfume bottles, record + tonearm, lidded hamper, the fairy string strung, HER DOOR with stickers; first WEAR; D3 switch/outlets/5 cords; D5 backyard via make_backyard_view; the fairy string's wash) | draft 5: corkboard photos as photos; paperbacks at a lean; mirror frame as a ring; the duvet's stripe; box fan blades; Deck: night establish + `insert floorboard` |
| Sam's bedroom (vol 6, 9 placements) | 4 (DRAFT 4 09-18: turned desk legs, clip lamp with neck + bulb, kit chair pushed out and turned, one sat-in beanbag, skateboard on trucks, dresser pulls, bedside lamp profiles, fan pull chain; first WEAR incl. stickers + a peeled one; D3 switch/strip/5 cords; D5 backyard) | draft 5: figures posed; lidded longboxes; the CRT's bezel + screen glow; curtain rings; laundry as clothes; Deck: establish + `insert notebook` |
| Miller back porch (vol 6 + 7, 12 placements) | 3 (DRAFT 3 09-18: turned balusters + bottom rail, rocker on curved runners, wicker weave + cushion, globe lamp, pedestal side table, steps with risers + stringers, kit pickup; first WEAR pass (three paths, runner arcs, cup rings, mat scuff, bark litter, patched screen); D3 switch/pull chain/hose bib + coil; D5 fences + treeline; the lit window's spill) | draft 4: the second rocker or the preset comment corrected; screen mesh at the frames; yard as heightfield; myrtle trunks as tapered lathes; the neighbor's house east; Deck: dusk establish + `insert bowls` |
| Hans's bakery back kitchen (vol 7, 8 placements) | 4 (DRAFT 4 09-19: the twelve box chairs at THE TABLE are kit chairs — turned legs, spindled backs, Roy's in the dark wood — and the table has turned legs, an apron and shin rails; the pass window CUT THROUGH the south wall with the closed front of house beyond (display case, a table, the street pane's pre-dawn grey); the hemlock outside Win_W with a second trunk and a far band; the cedar bowls, the mixer bowl + whisk as lathes, oven handles on standoffs, a rolling pin with handles; first WEAR — the flour path, the oven approach, ten seat patches, the table's elbow strips, grip patches under the oven handles, the counter's kick scuff, the proofer's hand patch; D3 door switch, three outlets, three straight cords. LAYOUT FIXES the recorder's threshold hid: the counter's SE corner sat inside the table's north end (counter 2.10, at -1.65), the prep table's edge ran into the west chairs (moved to -1.9), the speed rack shared floor with the window chair (rolled to the east aisle), the plant stood inside the counter (by the pass pier), the scale hung off the prep table's edge) | draft 5: a hollow proofer with trays behind real glass; lathed scored loaves on both racks; a flour-haze slab at the prep table; Greta's drawer half-open with the cloth spilling; crown on the south segments; Deck: shot_establish_b down the table through the door and the pass |
| Hospice room — the Death set (vol 5; 1 VN placement + the board) | 3 (DRAFT 3 09-19: LAYOUT — the north window's frame + glass sat inside the wall, the beach print hung INSIDE the window opening, the spare blanket floated 70 cm south of the bed, a second water glass floated beside it, two slipper pairs shared names, three flower stems stood in the air with no vase while the vase floated on a sill that did not exist inside the rose's votive, the prayer book sat in the lamp base — the wall CUT around a window EAST of the bed (so the head backs a real wall — the BED rule), a sill for the votive, the print on the west wall, the blanket over the foot panel, the vase + flowers on the dresser, the duplicates gone. PRIMITIVES: the visitor chair chamfered with rolled arms + turned legs, the throw draped; the kit bedside lamp; the IV line a tube to the rail; the monitor's collared pole + cable; the control pendant on its cord; a gooseneck at the sink; votive/bloom/glass/vase profiles. WEAR (three weeks of a vigil): the visitor's patch, the table ring, the door kick, the arm's shine; D3 two outlets + the monitor's and lamp's cords; D5 the garden — lawn, path, hedge, a birch, a bench, far trees. Scene: the 'BedsideLamp' light 1.5 m off the lamp → the under-cabinet light's; the rose and chair inserts re-aimed) | draft 4: the raised head in make_bed's hospital style; the sink mirror; gathered curtains; the wall oxygen outlet; Deck: the preset + establish_b |
| Elicia's bungalow — the Priestess set (vol 5; 2 VN placements + the board) | N+1 for the LIVING ROOM + STUDIO (09-19, the shared kit imported into this vendored builder: LAYOUT — two floor lamps shared one set of object names, the closed laptop + coffee cup sat INSIDE Anya's CRT case, a second drive stack hung half off the desk, a box stack stood inside the reading chair, both book bundles sat in the lamp base, Anya's chair faced away from the mic; PRIMITIVES — the reading chair chamfered with rolled arms, the kit side table, both floor lamps as profiles, Anya's kit chair facing the mic (the laptop on its seat), the can light, mic capsule + mesh, pop filter on a gooseneck, headphone cups + band, coffee cup; WEAR — the seat's dent, the arm's shine, the feet patch, Anya's patch, the desk's elbow strip; D3 — the lamp's cord to a south outlet (two straight runs), a power strip under the desk + the reel's cord) | draft N+2: the kitchen + bedroom stations by the same method; wicker as woven lathes; the string lights' cord as one catenary; Deck: the preset + the cast markers' frames |
| Houston office — the Emperor set (vol 5; 2 VN placements + the board) | 3 (DRAFT 3 09-19: LAYOUT — the manager's glass ran along the SOUTH of her office (the credenza stood through it, her chair against it), the cubicle row's west third overlapped the office, the teak drawer faces floated 18 cm off the desk's end, the second monitor hung off the desk, the west outlet sat inside the bookcase, the 'door' was a bar in the glass — the office is the SW corner proper: glass north + east with a glass door, credenza on the real south wall, a two-pedestal desk with the drawers on the east pedestal facing the sitter, the bookcase inside the glass, the cubicle row north. PRIMITIVES: five-star office chairs (manager + three cubicles) with casters/pillars/arms, kit guest chairs, kit lamp, a wedge phone with handset arc + cord, the cooler jug a bottle, cups as profiles. WEAR: the cubicle aisle, three chair mats, the elbow strip, the mug ring, the glass door's hand smudge; D3 a floor box + the lamp's cord, three screen cords down the partitions; D5 the freeway deck twelve floors down + three towers. Scene: the lamp practical onto the kit bulb; shot_closeup_anna south of the moved row) | draft 4: the drop ceiling as tiles; the printer + stand; a coat on the door; cubicle name plates; the hawk past the glass; Deck: the E preset + establish_b |
| New Orleans apartment — the Tower set (vol 5; 2 VN placements + the board) | 3 (DRAFT 3 09-19: LAYOUT — the ENTIRE shuttered-window set (frames, glass, shutters, balcony bars) sat inside the south wall's thickness, invisible from the room; the entry was a 3 m hole with no door; the bed's head posts stood in the kitchenette; the ajar microwave door floated 0.5 m from the microwave; sofa cushions 4 cm into the base, the jacket into the back; takeout in the sink; the bass into the armoire + amp; the console half inside the TV stand — the south wall CUT around both windows (piers/spandrel/lintel), shutters folded on the piers inside, the rail on a gallery deck outside, door jambs + header + leaf, everything else onto what it stands on. PRIMITIVES: turned posts with finials; fan stem/hub/light bowl; the bass with neck, headstock, strings; amp grille + knobs. WEAR personality: the crash dent, the sofa-to-bed path, three ring stains + the ash dust, the can ring; D3 three cords + two outlets; D5 the gallery deck + rail, the street three floors down, the facade across with its galleries. Scene: the fan practical into the light bowl; shot_insert_microwave re-aimed) | draft 4: the sheer as hanging panels; the brick's mortar grid; scroll ironwork; the transom; a fridge; Deck: the SE preset + establish_b |
| New Orleans office — Jimmy's (vol 5; 2 VN placements + the board) | 3 (DRAFT 3 09-19: LAYOUT — the desk's modesty panel faced the SITTER, the filing cabinet stood in front of the back-stair door, the west wainscot sat INSIDE the wall (invisible), the AC was wedged into a south window that had never been built, the entry line ran mid-wall into the chair, the banker's-lamp practical hung 0.85 m off the lamp — panel to the visitor's side, cabinet up the east wall, wainscot proud of the face, Window_S built, the bourbon on the desk beside the chipped glass with its marker re-aimed. PRIMITIVES: kit pendant; banker's lamp as base + stem + rolled green shade with brass caps; executive chair with five-star base, casters, pillar, arms, headroll; rotary phone (dial, cradle, handset arc, coiled cord); inkwell + bottle profiles; leather inlay. WEAR personality: the chair's arc, the second drawer's pull patch, two elbow strips, the door kick; D3 the lamp's cord, the phone line to a jack, the AC's cord; D5 the gallery rail + the neighbour's shuttered brick east, the street + facade + balcony south) | draft 4: the room at canon's twelve-by-ten (four times too big — the full rebuild); the ceiling fan; the transom; the plans as a tube with paper ends; Deck: the SW preset + establish_b |
| Natalie's apartment — the Empress set (vol 5; 3 VN placements + the board) | 3 (DRAFT 3 09-19, the arcana primitive upgrade's first room: LAYOUT — the sofa + coffee table sat in the front door's swing (the entry wear ran through the sofa), the scarf lamp floated 0.6 m up with nothing under it, the twilight quilt floated over nothing in the east half, the record lay INSIDE the plinth, the sleeve stood half off the stand, the deck + dealt cards lay under the sofa and low table, the desk chair ran into the bookshelf, the coffee pots overlapped the phone — the living set moved east + north, rug and low table north, bookshelf up the wall, quilt folded on the arm, lamp on a kit side table. PRIMITIVES: chamfered sofa with rolled arms; kit coffee table, side table, writing chair, two kit lamps; turned desk legs + apron; gooseneck faucet; kettle profile; platter/spindle/pivot/tonearm. WEAR personality: her end of the sofa, the kettle path, the desk edge, the stove drip; D3 three cords + two outlets; D5 the neighbour's brick wall with one lit window + the live oak west, the parish street + facade + globe lamp south-east. Scene: the free-floating Practical_Lamp → the under-cabinet light's; shot_insert_deck re-aimed) | draft 4: the L-counter's corner as one piece; fridge seam + magnets + photo; the blinds' cord; a shelf row of her objects; Deck: the SW preset + establish_b |
| THE MISSING LINK interior (vol 1, 8 placements) | 3 (DRAFT 3 09-19: stools as profiles (flared base, foot ring, rolled seat); booths chamfered with a top rail, flanged table posts, chrome edge bands; the cake dome a bell; jukebox feet + trims; the swing door's push plate + hinge strip. Through the windows: the pumps moved WEST of the door to match the exterior builder (the east one stood in front of the entrance), a hose + nozzle, the depot bench under a real awning, the road + dashes, the pole sign, the cobra lamppost, the treeline. First WEAR (the entry line ON the checker tiles, kick scuff, elbow strip, booth sit shine, the lean patch at the jukebox); D3 switch bank, two outlets, the jukebox's and coffee station's cords) | draft 4: reconcile the two builders' plans (the exterior's door is at the EAST end, the interior's centred; 8 m vs 7 m); chrome napkin dispensers; the pie case lit; Deck: the SW preset + establish_b |
| THE MISSING LINK exterior + THE SHUTTLE BENCH (vol 1, 8 + the exterior's placements — vol 1's highest-traffic background) | 2 (DRAFT 2 09-19: the kit pickup (moved west of the sign pole); the kit's telephone poles with insulators and a transformer, the wires strung between them; two rows of conifers for the treeline (was twelve boxes); the cobra lamppost + sign pole as flanged profiles; pumps chamfered, a hanging hose + nozzle, two bollards; the awning corrugated with its own tube fixture (lit — the spill practical hung outside the awning), the trash can with a domed lid; window mullions, a door pull, a downspout. First WEAR: two tire tracks to the pumps, the oil stain, the awning's drip line, the step's worn centre, the bench's sit shine, the rust streak at the sign's foot) | draft 3: reconcile with the interior; the roofline neon; a second parked car; rain streaks on the plexiglass; puddles as alpha sheets; Deck: the shuttle_bench preset for the wires against the sky |
| Finn's apartment (vol 7, 7 placements) | 3 (DRAFT 3 09-19: kit lamp / desk chair / kitchen chairs / perch chair (rail on the kit back); kettle + pour-over cone + mug as profiles; the ceiling dome a dome; turned bed posts + foot rail; dresser and nightstand pulls; counter door seam + pulls. LAYOUT fixes: the desk 6 cm in the east wall; phone + notebook floating BESIDE the desk; reader + headset hovering over the perch chair (the nightstand had moved with the bed); duffel inside the desk chair; counter in the west wall; dresser in the east wall; both outlets inside furniture; the round rug across the partition; the plant's pot in the bed deck. First WEAR (three seat patches, the step-up scuff, the desk edge, the counter drip, the sill's marks, the corner's wall patch); D3 two outlets + the kettle's and lamp's cords; D5 the neighbour's roof + treeline north, the street, roofline, sea band + sky south. Scene: the desk-lamp practical onto the kit bulb (it had stayed at the desk's OLD spot since 09-07), the dome lit, shot_insert_duffel re-aimed) | draft 4: slatted crates with contents; the dresser's top dressing; the kitchen window's curtain; the entry door leaf + chain; a fridge; Deck: the SE-corner preset + establish_b |
| Board Lords + Main Street (vol 7; the one scene serves both presets, 15 placements) | 3 (DRAFT 3 09-19: kit chair/stool/bench; kettle profile with spout + bail on a coil burner; the work lamp as clamp + two arms + cone; the lathe's tailstock, tool rest, motor, belt cover and shavings; chamfered decks; pegs under the parts; wheels as wheels; a bearings box with its flap open; the door's push bar + kick plate. THE STREET: Finn's truck is the kit pickup in the parking lane (the 09-07 'curb' put it on the sidewalk; the road box now ends at the curbs, -8.0..-2.3, or every parked car reads mid-lane); the far facade runs the block with a corner building each end, the bookstore window, two parked cars, a second streetlamp, three puddles; the near streetlamp on the sidewalk. LAYOUT fixes: repair bench inside the counter, partition through the counter's back, wheel bin in the east wall, bearings boxes in Devon's chair. First WEAR (entry path, roll-in wheel lines, three sit patches, Kai's stand spot, the window smudge, elbow strip, bench scars); D3 switch, two outlets, two cords, the lit EXIT sign; the bench tube lit; shot_insert_crow re-aimed at the moved truck) | draft 4: complete boards (trucks + wheels) on three wall decks; the griptape roll; the register's cord; the bell on its spring; the awning's valance; the laundromat's dusk glow; Deck: the main_street preset + establish_b for the street's depth |
| Cabin road (vol 7, 8 placements) | 3 (DRAFT 3 09-19: the gravel on a continuous GRADE — road prisms whose tops slope, the bend and upper run yawed north-east and joined end to end (four stepped slabs with 20–40 cm risers until now); the culvert at creek level under the fill with a headwall each mouth and a delineator each shoulder; creek stones + moss caps as blobs; the kit's new sword ferns (`make_fern`, ten); the mile marker leaning with a cap; PAVEMENT ENDS on a post; wear that FOLLOWS the slope (parking fan, five washboard strips, the crossing's wet band, the truck's ruts up the gravel as sheets — the old rut boxes lay buried in the fill), puddles in the asphalt's tire lines, a fallen alder branch; SitkaE_7 moved out of the upper run) | draft 4: fill embankments at the crossing; the east ditch (make_ditch_field); ridged bark on the near trunks; a second mile marker; the worker drone's shadow; Deck: establish_b from the bend + the asphalt preset for the grade's read |
| Vol 7 cabin set (cabin_interior + cabin_road) | 5 (DRAFT 5 09-17, the visual program's first background pass: the primitive upgrade — stove/kettle/lamp/lantern/basin/jars as lathe profiles, kit bed + desk + chair, chamfered upholstery, chest straps, kerosene D3; the fluorescent practicals a template gave an off-grid cabin replaced by lamp/lantern/ember, cool key over warm practicals) · was 3 (hero props 08-12: bowls/crow/drones; wear-personality pass 08-19: Olaf's decades vs Tem's weeks — the two-age wear vocabulary) | draft 5: Deck screenshots of wear + through-window reads (Sitka band S, lean-to/creek strip N — D5 shipped 08-19; cabin_road D2 shipped 08-19: centerline fragments, one truck's tire lines, the parking fan + oil shadow, needle drift, moss seam) | next: Deck screenshot loop, then cabin_road D5 horizon check |
| Lena's apartment (vol7) | 4 (DRAFT 4 09-17: the primitive upgrade — kettle/faucet/cone/grinder/knobs/pedestal/post/pull as lathes and tubes, chamfered upholstery with rolled arms, fridge seam+pull+photo; D3 wires — switch, outlets, cords from heater/fairy/fridge/the new floor lamp; her side of the bed; the dorm-era desk-lamp practical replaced by lamp/fairy/sodium window) · was 3 (hero props 08-12/19: easel+canvas, nebula+patches; wear pass 08-19: three-years-alone vocabulary — narrow single path, cone rings, paint constellation in HER palette, 61° props, crowding shown in objects not floor) | draft 4: Deck check of easel/mural/window inserts; D3 cords (easel lamp? none yet — she works in window light, verify that reads); bedroom wear |
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
| **THE TRIP (music-synced psychedelic layer · 2026-09-07 · FEEDBACK 2026-09-11)** | **4** (the liquid drifts slowly and never to the beat; draft-1 colour/line weight; FLOW · LINES · COLOUR · BEAT mix sliders;  TripSync autoload + trip_sync.gdshader; global layer 60 + VN texture mode; PSYCHEDELIA slider; per-mood/per-surface scaling; FIVE REGISTERS arcana/community/milk_honey/slowstick/base pushed by the hosts; **THE FEEDBACK 2026-09-11** — ping-pong half-res SubViewports trailing the LAYER'S light (highlights + the aura), never the picture, sourced from a texture so type cannot smear, per-register zoom sign and wake length, fifth TRAILS dial — see _PSYCHEDELIC_DESIGN_BIBLE.md) | draft 2: the feedback's wake length and zoom sign per register are container guesses (is milk_honey at 0.90 a light show or a fog?); a screen-sourced feedback rig for the locale walk and the gauntlet; Deck look at 0.6 per register (gauntlet, CP screen, a vol 7 chapter, a stick); beat detector vs the real catalog; then the GAME GRAMMAR column one row per pillar |
| **The VN score (2026-09-11)** | **1** (33 beds authored from the catalog's own descriptions; 6 orphan vol5 room tones adopted; 10 already-rendered beds repointed; `normalize_bank` taught to walk `bgm/` itself; every non-stub scene assigned — 174 by place, 23 on the volume floor; `music_coverage_audit` gates SILENT + NOFILE at zero) | draft 2 (2026-09-12): SEAMLESS — every looping bed re-rendered with the synth's new `loop` crossfade at its normalized level; the legacy 16 get a runtime loop-end trim. Deck-gated: 22050 Hz on the hiss-forward beds, the five `.ogg` tracks normalize can't read, the 16 legacy compositions re-rendered with `loop` + the enveloped `rain`. Then the 74 remaining ghosts — the Magician's 7 finale stingers + the Priestess's 6 (the loss screen already picks the finale and unlocks its milestone; it plays nothing), gauntlet_win/loss, and the 22 character themes (a signature per principal on `show`) |
| **Signatures (2026-09-12)** | **2** (34 character themes authored — 19 principals on first show/line, 15 gauntlet visitors on the arrival card — every theme whose character is shown or speaks in its volume; `faust3`→`faust`; cue once per scene on first show OR first line, one-shot that hands the bed back; the duck inverts under a signature — hum to 20%, theme to full; `bed(trim=)` levels the set; 304 cues / 184 scenes) | Deck: the once-per-scene rate, the 0.20 floor, the translations that miss (Rick, Carl, the Superfan's paper bag); the 12 themes left name characters no scene or board has |
| **Gauntlet audio (2026-09-11)** | **1** (15 scenario B-sides authored and wired as `_BGM_BY_SCENARIO`, arcana × difficulty, ahead of the location drone; the 12 dead `gauntlet_*.ogg` fallbacks deleted — every key was already on an SFXBank preset) | the finale stingers at the loss screen; a bed for the other seventeen arcana (they still share four vol5 drones by tonal fit); then Deck: does the hard-mode bed read as "the small hours" against the easy one? |
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
