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
TWENTY-SECOND PASS — WHAT THE SHEET SHOWED. The 09-24 sheet's black
frames were not all the night mood: 32 key/sun/moon/overhead
DirectionalLight3Ds in 31 scenes pointed UP (grunion's moon, the kwik
stop's fluorescent key, …) — all flipped down; NEW GATE
light_direction_audit.py (132 key lights, 0 up) runs in the suite, and
contact_frame_screen.py lists near-black / one-flat-colour frames from a
sheet (report only). Flat inserts: ~15 hand-built windows in 14 builders
sat inside their walls (offset from the wall's centre line) — on the
room face now, glass in front of the frame; the New Orleans office's
east window was a solid slab over its glass — four bars now; Faust's
curtain rod got brackets back to the wall. Markers: henderson garage's
map insert looked over the map (pitched down now); graustark's wreck
insert stood inside the wreck (moved off it). THE MARKER-AIM GATE COULD
NOT FAIL: its exit code was grep's; four misaims had ridden through —
cedar tower's two ESTUARY 7 cameras still filmed the door gap the poster
left in the twentieth pass (moved to the E wall), hospital hands and the
riverboat calling card (re-aimed; the card is the helm desk's, per
vol5 ch4). Gate fixed (and orphan_practical's, same bug); 0 misaims.
NEXT (draft 23): a fresh contact sheet — confirm the lit rooms, the
windows, the inserts; run contact_frame_screen.py on it. Still open from
the screener: dark inserts (cedar tower credit, montreal drainpipe,
board lords decks, nightmare cell), markers too close to large subjects
(carnival storm heap, the henderson truck), and the direction backlog.
TWENTY-THIRD PASS — WHAT THE LENS COULD NOT SEE. Read from the old sheet's
screener list (39 flagged frames) with a fan-cast per marker: most dark
frames were LIT wrong, the flat ones were GLASS. Lights: 22 keys sat at
the identity matrix (shining sideways, level with the floor) and 39
back/rim lights shared a matrix aimed 45° UP — all down now;
light_direction_audit gates key < −0.10 and back ≤ +0.05 (222 lights, the
portrait rig's BackRim the one named exception). Glass: the pipeline has
no alpha, so every "glass" slab is an opaque panel — and most glass
cases were SOLID bodies with the product inside. New
_props.structure.make_case_shell (five panels, same extents); the kits'
cooler door, hot-food case, pizza warmer and donut case (15 rooms) and
the kwik stop's own coolers / hot case / donut / pizza / vape kiosk are
open shells with product on real shelves and two glints for the glass;
by hand: the Board Lords deck wall (28 decks behind lavender), the
centro vending machine, the ice freezer front (Emile's photo now on a
centre mullion; the fog decal and wiped streak went with the glass),
Jiggles' cabinet (a broken remnant along the head, not a full pane), the
chip warmer, the proofer (door is a frame now), the Miller file cabinet,
the missing-link pie case, nexcorp's three coolers, the gas-go fridge,
the meat case's sneeze glass. make_window(see_through=True): the cabin's
crow insert filmed a grey pane — the kitchen window has no glass now.
The obstruction audit no longer treats glass as see-through (it
passed that crow). Finn's window: four frame bars, glass set in them,
the crow's beak clear. Markers: henderson truck insert 0.66 m → 2.8 m
off the cab; cedar credit 0.43 → 1.0 m.
NEXT (draft 24): a fresh contact sheet (the relit rooms, the open
cases, the crow through the window). Glass still hiding things: the
frog tanks (water is a slab too), the diner's west glass over
D'Ambrosio's service bar (model chapter — look first), the asylum
window bars, the cosmic comics window display, the missing-link cake
dome, the bakery FOH case. Dark rooms with NO key at all (equipment
shed, nightmare cell, centro stockroom: fill + practicals only) — a
lighting call per room. The carnival storm-heap marker.
TWENTY-FOURTH PASS — THE WHITE ROOMS. The 09-24 sheet (from fa48a810)
came back with ~30 rooms washed near-white (hans, el rancho, the kwik
stop, centro, nexcorp, kowalski, the miller rooms, faust, finn…). Not the
light re-aims — henderson kitchen had kowalski's exact light changes and
did not move — the GEOMETRY lost its vertex colours: every GLB rebuilt on
the Deck that day renders with a white albedo, every GLB not rebuilt is
fine. The export set only the legacy `export_colors`; a newer glTF
exporter (the Deck's Blender evidently updated overnight) replaced it
with `export_vertex_color`, whose default ('MATERIAL') skips meshes with
no material — all of ours. FIX: _props.geometry.gltf_color_kwargs sets
export_vertex_color='ACTIVE' + colours-without-material on any exporter
version (and the colour layer is made the ACTIVE colour attribute); the
16 builders with their own export blocks carry the same lines. GUARDS:
blender_dryrun now models the NEW exporter and fails any builder whose
export would drop colours (NO-COLOUR; negative-tested);
tools/audit/glb_color_check.py reads each built GLB's JSON and fails
colourless ones; contact_sheet.sh warns before rendering;
list_stale_builds.sh counts a GLB stale when it lost its colours OR when
any _props kit its builder imports is newer — it compared the builder
alone, so kit fixes (draft 20's grounded horizon bands, draft 23's open
cases in 15 kit rooms) NEVER rebuilt their callers. The next Deck
rebuild is therefore nearly every locale (geometry.py changed) — long,
once. Also: henderson garage had no key (only a 0.14 fill — Ben's truck
at the curb rendered black, and MoodCycler's sun rotation landed on the
fill): Dusk_Key added.
NEXT (draft 25): the full Deck rebuild + a fresh sheet; confirm colour
on every room (glb_color_check 0), THEN judge the drafts 22–23 light
re-aims on real colour. The draft-24 list carries over (frog tanks,
diner west glass, asylum bars, cosmic window, cake dome, FOH case,
keyless dark rooms, carnival storm heap).
TWENTY-FIFTH PASS — WASHED, NOT WHITE. The sheet from 72bdde67 (after a
full Deck rebuild) still showed the rebuilt rooms pale — 79 rooms far
brighter than draft 19; pixel-identical frames (24 → 25) were rooms that
were ALREADY washed and rebuilt to the same thing. Looking closer: the
kwik stop's product boxes show faint distinct colours — the colours are
PRESENT but lifted toward white. That is a gamma flip, not a missing
attribute: glTF COLOR_0 is linear; the old chain wrote
srgb_to_linear(our colour); the new one writes our colour unconverted
(whether the colour layer now takes linear input or the exporter
stopped converting, the GLB is identical), and 0.5 renders as 0.73. The
draft-24 `export_vertex_color` fix was necessary but not this.
FIX, version-proof by measurement: _props/glb_colorfix.postfix reads
every exported GLB back, compares COLOR_0 of up to 300 objects with the
colour Blender holds for them (the layer returns what the builder
wrote), and ONLY when the values are unconverted rewrites every COLOR_0
through srgb_to_linear; a correct export is untouched (tested: float +
normalised u16, idempotent). Called after export_glb and in all 16
self-contained export blocks; blender_dryrun fails an export that is
not read back (NO-COLOURFIX, negative-tested). DIAGNOSTICS: glb_diag.py
prints each GLB's exporter (asset.generator) + sample COLOR_0 values;
contact_sheet.sh writes it and glb_color_check into
qa/contact/_glb_diag.txt and contact_push now carries .txt.
NEXT (draft 26): the full rebuild again (geometry.py changed) → sheet →
read _glb_diag.txt: expect "converted N colours" in the build log and
linear values in the diag; THEN judge the draft 22–23 light re-aims.
TWENTY-SIXTH PASS — THE FILES WERE RIGHT; GODOT'S DEFAULT WAS NOT. The
Deck's glb_diag output: every GLB written by "Khronos glTF Blender I/O
v5.2.39" (the Blender update, confirmed), COLOR_0 as normalised u16, and
the values CORRECT — cedar tower's desk asks for (0.58, 0.42, 0.28) and
holds (0.296, 0.147, 0.063), exactly srgb_to_linear. The draft-25
"gamma flip" diagnosis was WRONG (its read-back fix measures first, found
nothing to fix, and stays as a harmless guard). The decider: the DINER
was rebuilt on the same exporter (10:39) and stayed in colour — its scene
runs LocaleSetup.gd, which puts a vertex-colour-as-albedo material on
every mesh; the white scenes use the material Godot's importer makes for
a material-less primitive, which with the v5 files no longer reads the
colours. FIX (runtime, no rebuild): scripts/VertexColorGuard.gd, called
from MoodCycler._ready on the locale root (every locale scene, walkable
and VN background alike) — for every surface that HAS a colour array and
an untextured StandardMaterial3D without vertex_color_use_as_albedo (or
no material), a cached copy with the flag on; real materials untouched.
NEXT (draft 27): pull + sheet only (no rebuild needed for this) → every
room in colour? THEN the draft 22–23 light re-aims on real colour, then
the carried list.
TWENTY-SEVENTH PASS — COLOUR BACK; THE DARK ROOMS. Sheet from 7c853dd5:
VertexColorGuard worked — flat frames 135 → 8, glb_color_check 121/121
coloured, every room back in its palette (and the draft-23 open cases
READ: the kwik coolers show product, the Board Lords deck wall shows its
decks). The drafts 22–23 light re-aims look right on real colour. Of the
20 near-black: under-keyed night/dusk rooms — grunion Moon_Key 0.4 → 0.6
+ Fill 0.15 → 0.22 (the playbook's night band is 0.45–0.6), the bar
exterior's moon 0.45 → 0.6, henderson's Dusk_Key 0.45 → 0.8; three
rooms had NO key at all (fill + practicals only, their inserts pure
black) — equipment shed Key_Bulb 0.35, centro stockroom Key_Fluor 0.5,
nightmare cell Key_Tube 0.2 (the cell stays dark). The riverboat bourbon
insert framed Dante's bottle on the helm file cabinet at 3.7 m in a 30°
lens in a dark corner — moved in to 1.4 m. (A scratch-tool lesson: the
frame caster read "rays escape" for self-contained builders because it
queried the recorder before installing its stubs.)
NEXT (draft 28): sheet → the keyed rooms and the night beach; a FIXTURE
+ practical by the helm file cabinet (the bourbon corner is unlit — a
light needs something to come from); the cedar credit (poster wall on
the key's back side); the crumpled barn "lean" insert (one grey wall);
the montreal drainpipe; then the glass list (frog tanks, diner west
glass, asylum bars, cosmic window, cake dome, FOH case) and the
carnival storm heap.
TWENTY-EIGHTH PASS — WHY THE KEYS DID NOTHING. Sheet from 949d283e: the
raised keys barely moved the night frames (grunion 2.3 → ~2). The night
mood changes no light; it posterises to 9 levels with floor() in the
Compatibility renderer's sRGB, so everything under 28/255 goes to 0 —
most of a dark-albedo set. The shader playbook already had the rule
(2026-07-12): dark-albedo night sets want scene ambient 1.0–1.8. Eight
scenes sat at 0.5–0.65 — grunion, bar exterior, caldwell porch night,
equipment shed, nightmare cell, centro stockroom, henderson garage, cedar
tower — all 1.0 now. USER DECISION (not taken): demoscene_post's
quantiser uses floor(); round-to-nearest would stop crushing shadows in
EVERY palette mood but shifts every mood's look by half a step.
Glass: the frog tanks' front pane + SOLID water box hid every fish —
front is glints now, the water a surface at the waterline, the back pane
carries the water's colour, plants rooted in the gravel, the frog's eyes
on its head (support_audit: `minnow` joins the flyers, a shoal hangs in
water); the missing-link cake dome is lifted and set beside the stand
(it was an opaque bell over the pie); the riverboat's bourbon corner got
a real fixture — a brass sconce on the east partition over the file
cabinet — and its practical. Checked and left: the cosmic comics
window statues and the asylum bars stand on the ROOM side of their
glass. Left for the user: the diner's west glass over D'Ambrosio's
service bar (model chapter). The crumpled barn "lean" insert is used by
no cue.
Deck: rebuild frog_knows_best, missing_link_interior, riverboat_interior
(the rest is scene-only).
NEXT (draft 29): sheet → the ambient-lifted night sets, the tanks, the
cake, the sconce; the cedar credit; the montreal drainpipe; the carnival
storm heap; the bakery FOH case.
TWENTY-NINTH PASS — THE DARK END IS THE QUANTISER. Sheet from 9e0d0dbc:
the new fixture reads (the bourbon insert shows the bottle and glass
under the sconce's glow), the equipment shed's cones are lit, the cake
and the tanks built. The night frames did NOT move with ambient 1.0:
grunion's night establish has R and G at 0–2 across the whole frame and
only blue above zero — every value the blue moon puts under the
quantiser's first step (28/255) floors to 0, and most remaining dark
frames read only at 4x. Lights are not the lever; the floor() in
demoscene_post is — a USER decision (asked). Centro's smear insert: the
text puts the smear on the eastern HORIZON above the cedar; the camera
stood 2 m from the slab looking up — it shoots from the dock now
(24.6 m, 12.5° up). Carnival storm heap: no preset, no cue — unused.
Bakery FOH case: an empty shelf — nothing to hide.
The user's answer: lift only the dark moods — demoscene_post
`shadow_lift` (gamma lift before the quantiser, default 0), night 0.6,
3_47_am 0.6, dusk 0.3; every other mood unchanged.
NEXT (draft 30): sheet → do the night frames read (grunion, beach night,
nightmare cell, bar trash, henderson truck at dusk) without looking
washed? tune the three lifts; then the cedar credit, the montreal
drainpipe, the diner west glass (user look).
THIRTIETH PASS — THE NIGHT READS; EVERY CLOCK WAS BLANK. Sheet from
61b0b329: near-black 14 → 4 — the grunion / beach-night frames read as a
dark teal shore with the surf lit, the nightmare cell has shape,
henderson's truck reads at dusk; the lifts look like night, not wash.
The 4 left: the dock's smear insert looked at a near-black background
(centro_stockroom background → pre-dawn 0.12/0.14/0.24; the text says "a
clear morning"); the nightmare cell's wall insert stood OUTSIDE the cell,
0.2 m behind the west wall — now inside, 1.8 m from the dots; the
cedar-tower credit sat at y 0.105, INSIDE the poster's frame (face at
0.135) — on the face now, printed pale.
A new scan (scratch buried_decals.py: a thin object ≤ 6 mm lying wholly
inside a thicker box) found 1351 hits; the biggest family was the WALL
CLOCK KIT: the rim was a solid 20 cm disc IN FRONT of the 18 cm face, so
every kit clock rendered as a blank grey disc — face, ticks and hands
inside the rim. Kit fixed (rim behind the face; ticks on it; hands on
the ticks) and given `facing` ('-Y' default, '+Y', '-X', '+X'): about
twenty clocks on east/west walls faced along their wall, dials inside it.
All 44 call sites snapped onto their host wall's room face and faced
into the room (scratch fix_clocks.py, from the recorded geometry); four
that then overlapped a window or shelf frame moved clear.
Deck: the kits changed (geometry.py in 25, decor.py now) — the next
paste rebuilds nearly every locale, once.
NEXT (draft 31): the other buried-decal families — posters inside W/E
walls (~70), the riverboat's ceiling tiles inside the ceiling slabs
(165), street paint inside roads (crosswalks, sidewalk seams), brick
courses inside walls, rack labels, calendar grids, card-terminal keys;
graduate buried_decals into a gate. Then the montreal drainpipe and the
diner west glass (user look).
THIRTY-FIRST PASS — THE USER'S LIST: "furniture on ceilings, rooms too
cramped, doorways obstructed or misaligned; sprinklers should do the
rotational chug-chug-chug thing, more in a yard, wider arcs."
· CEILINGS: no chair was on a ceiling — the ceiling kit's WATER STAINS
  were three solid 0.8 m squares in a dark tan at fixed metre offsets
  (hitting walls in small rooms), reading as boards stuck overhead in
  80 rooms. make_ceiling: a faint tint of the tile, an irregular
  three-piece blotch at fractions of the ceiling, none under 2.5 m;
  the kwik stop's and lena's hand-built stains the same.
· DOORWAYS: NEW tools/audit/doorway_audit.py (report in the suite) —
  BLOCKED (solid furniture in the 0.9 m clearance each side of a
  leaf) and ADRIFT (a leaf not in a wall). ~25 interior doors cleared
  by moving what stood in them (coffee tables at elicia's and natalie's
  front doors, the bungalow's books / counter / upper cabinet /
  studio chair, the cabin's basin, crates, beanbags, bike, guitar
  case, lockers, counters, the pharmacy gum rack → a countertop rack).
  MISALIGNED: the template bedrooms (sam, maya, jesse), elicia, the
  cabin, board lords, centro break room hung 0.9 m doors in 2–3 m wall
  gaps; the bungalow's front/back doors (1.6 m) in 3.6 m gaps; the
  asylum's five cell doors in 1.6 m openings open to the ceiling —
  all closed to the frame (infill walls, jambs, headers); the
  bungalow closet door (1.4 m, 10 cm proud, 0.2 m into the partition
  both sides) refitted to its 1.0 m opening. DEFERRED (need a
  replan): board lords' alley door vs Devon's desk (corner full: east
  wall + register), lena's bedroom door between the kitchen chairs and
  the bed foot.
· SPRINKLERS: impact heads — each jet steps 6° every 0.16 s across its
  arc (a visible arm kicks per chug), swings back fast, sprays the
  whole time; three heads per lawn (two street corners ~110°, one by
  the house a half circle back to the street), the arc in the head's
  name; lots come on west → east and stay on; the Miller cracked head
  keeps its jammed arc. The single heads had stood a metre off their
  lawns. (Sound: no chug SFX yet — next.)
· CRAMPED: furniture covers 10–30% of floor almost everywhere — the
  rooms are SMALL. Widened the five smallest bedrooms (sam, maya,
  safehouse 4×5 → 4.8×5.6; jesse 4×4.5 → 4.8×5.1; ben 3.6×4 →
  4.4×4.6); absolute-placed props re-anchored to ROOM_W/ROOM_D, 5
  markers re-aimed, one reframed.
· POSTERS: make_faded_poster printed its ink INTO the wall on every
  east/west poster (sign by coordinate) and on south walls at y 0; new
  `into_room`; 46 call sites moved onto their wall's room face (they
  were anchored 5 cm off the wall's centre line — inside it).
NEXT (draft 32): Deck sheet (full rebuild — kits changed): ceilings,
the refilled doorways, the widened bedrooms, the sprinklers moving (a
video capture would help). Then: the deferred two doors; a chug SFX for
the impact heads; more rooms to widen if the bedrooms read better
(lena 5×5, finn, grandmother, cosmic back office, centro break room);
the buried-decal families still open (riverboat ceiling tiles 165,
street paint, brick courses, rack labels, calendar grids, the
courthouse notice behind its wainscot); doorway_audit to a gate once
the façade false positives are tuned.
THIRTY-SECOND PASS. Sheet from 1568b794 reads: the widened bedrooms have
room, the posters show, the ceilings are clean, the refilled doorways
read as doors. (Note: 35ba44db — the 31st pass — was pushed with the
suite FAILING, DESK 1 / BED 1 from the safehouse widening; 1568b794
fixed it. The commit step now refuses to run unless the log ends EXIT 0.)
· SPRINKLER SOUND: tools/audio/sprinkler_chug.py renders a seamless 8 s
  loop (22050 Hz mono): three impact heads out of phase — the arm's
  "tch" (noise burst + 2.2–2.5 kHz ring + thump) stepping the arc, a
  fast ratchet on the return — over the spray's hiss;
  assets/audio/sfx/env/sprinkler_chug_loop.wav; SprinklerFX plays it
  (SFX bus, -13 dB) when the first lot comes on.
· BURIED DETAILS 1351 → 423: the riverboat's 165 tin tiles hung inside
  the ceiling slabs (now under their faces; deck seams on the deck, not
  12 mm above); scratch fix_buried.py brought 366 more out to their
  host's nearest face — a coffee inside its mug, a monitor's glow
  inside its screen, wear marks inside counter tops, notices inside
  walls — only where every object a call emits needs the same move,
  capped at 12 cm. Left for a hand look (moves too big to trust): the
  Civic's and the lot sedan's phone/tablet screens (1.2 m inside the
  car body — placed in the wrong car?), Ben's truck hood sheen (0.56 m
  in), cedar tower rack labels (0.37 m), the kwik stop card-terminal
  keys and sugar dividers, the roulette service-case decal, the cone
  sign, a shirt stain, the asylum votive pool (1.1 m under a wall);
  plus 84 in mixed loops (the nightmare cell's 46 dots among them).
· SKIPPED PRESETS: highway 101 and small wood road have been skipped
  on every sheet; the repo only lacks their GLBs (not in git) — so on
  the Deck the builds or their import fail. Background3D now records
  WHY a location did not load (last_load_error) and the contact sheet
  writes it to _report.json (skip_reasons); glb_diag prints whether
  the two GLBs exist and their size.
· DEFERRED, with the plan: board lords' alley door opens into a back
  office 0.8 m deep (partition at y 6.1, Devon's desk and chair in it)
  — move the partition south (the register must give) or lengthen the
  building; lena's bedroom door sits between the kitchen chairs and
  the bed foot — move the door along its wall or turn the bed.
NEXT (draft 33): the sheet's skip_reasons for the two roads; the big
buried moves by hand; the 84 mixed-loop details; the two deferred
doors; doorway_audit's façade false positives → gate; more small rooms
to widen (lena, finn, grandmother, cosmic back office, centro break).

THIRTY-THIRD PASS. Sheet from 15256b30 (1459 frames; near-black 3,
flat 4 — the same seven as last time).
· THE TWO ROADS, FOUND: skip_reasons said "scene failed to load (GLB
  present)" for highway_101 and small_wood_road, and the GLBs were
  there (4.3 MB, 2.3 MB). The cause was one line in each .tscn:
  `background_color = Color(0.62, 0.66, 0.72)` — three arguments.
  Godot's scene parser wants four, so the whole file failed to parse
  and load() returned null. Every other locale scene writes four.
  Fixed; `tscn_syntax_audit.py` (constructor arity for Color/Vector/
  Transform/…, declared resource ids, ext_resource paths, node
  parents) is a gate, 217 files, zero. The next sheet should carry
  highway_101 (×2 presets) and small_wood_road (×3) for the first
  time — those frames are unscreened.
· THE DOORWAY GATE: 59 BLOCKED / 194 ADRIFT → 0 / 0, and it gates.
  Rules learned: a door set into a solid massing (motel wing, shed,
  house body) is HOSTED — the massing is its wall and the side
  inside it is nobody's room; HouseW_0_Door's host is HouseW_0_Body
  (no prefix skip); roads, curbs, parked cars, hanging robes and
  sheets under 12 mm do not block. Then 30 real ones by hand: the
  Briar Falls bench across door 0, the mausoleum lectern 3 cm inside
  the clearance, Houston's guest chairs at the office door, the
  Cosmic Comics display tower moved east of the entry (north of the
  door it hit the new-arrivals table), the accretion extinguisher case
  ON door 2 and the bulletin board across door 3, the motel office
  door straddling the office/wing seam (and both machines across
  room 1's door), the circus shacks 0.7 m from the pool coping, the
  substation's cars 10 cm inside the doors, Miller's coffee maker
  overhanging into the pantry door, the equipment shed's "open"
  leaves that were flat boxes 0.55 m in front of the wall (rotated
  120° on their jambs now).
· THE TWO DEFERRED DOORS: board lords — the register counter runs
  along X to y 5.93, so the partition could not come south; the
  BUILDING is longer instead (ROOM_D 7.0 → 7.6, everything on the N
  wall relative — clock and cord ends tied to it), the office 1.4 m
  deep, Devon's desk against the E wall south of the door's swing, his
  chair north of it with its back to the alley, the bearings boxes on
  the floor at the counter's east end; lena's bedroom door fills its opening
  (0.86 at -0.30 — it was 0.62 at -0.62, 18 cm into the partition),
  the bed against the W wall, the couch east (0.17..2.07), the hall
  table west of the door, the front door at +0.30 with the wall
  closed either side (55 cm of daylight before), the table south to
  1.26 with its fourth chair at the NE diagonal.
· BIG BURIED DETAILS, ALL 11 BY HAND: the asylum votive's wax runs and
  pool (left at the S wall from a draft that hung the votive in the
  corridor) are on the counter by the jar; cedar's rack labels on the
  racks' fronts (37 cm inside); the centro cone sign a sleeve on the
  cone's face; kwik's PIN pad laid on the terminal's top, its sugar
  caddy off the Slurpee base; the casino service case on the floor at
  the table's front (its back half stood inside the base, in the air)
  with the decal on its front; the WGUR shirt stain on the shirt's
  top; Ben's truck hood sheen PITCHED with the hood (make_rot_box,
  0.027 rad); the Civic phone and the sedan tablet — nothing here is
  transparent, so a lit phone inside a car is invisible — are glow
  patches laid on the windshield rakes (roll -0.57 / -0.65). Plus 18
  second-order ones by tool (OnAir face, diner sign letters, roulette
  scuffs…) and three the tool misread: the bungalow welcome mat lay
  inside the porch deck (raised to it); the cabin bowls' rims were
  solid discs over the hollows (a lathe RING now, the hollow and the
  water inside it); the Roberts sink rim was a plate over the basin
  (a ring of strips, the drip's puddle on the basin's top).
· ROOMS WIDENED: centro break room 5.0×4.0 → 5.6×4.6; finn 4.5×5.0 →
  5.0×5.4; cosmic back office 4.0×5.0 → 4.6×5.2 (its one-way mirror
  frame off the doorway, the safe out of the service door's swing).
  Lena and grandmother (5×5) stay: their partitions are literal.
  Widening fallout, the usual kind: the break room's trash can and
  wall clock were literal and its dishwasher wall-relative (a clip
  and a float) — tied to the walls now; Finn's two insert markers
  re-aimed; Miller's coffee maker, pushed back onto the counter, met
  the microwave (east of it now); Lena's cushion wear stayed at the
  old couch spot. And four insert markers lost their line of sight to
  subjects that moved (the back-office safe, the Cosmic tower, Finn's
  nightstand, Lena's charcoal letters) — marker_reframe moved them.
  And the floats: the accretion bulletin papers pinned where the
  board used to be; the back-office mug keyed to a literal y while
  the desk moved with ROOM_D; Finn's counter, grounded only by
  touching the W wall, lost the wall (the counter and its dressing
  followed it). LESSON, again: everything on or against a wall is
  written against ROOM_W/ROOM_D, never a number.
NEXT (draft 34): screen highway_101 and small_wood_road on their first
sheet; the 65 mixed-loop buried details left (nightmare cell's 46
dots); the seven stable near-black/flat frames (centro dock dusk
smear, stockroom smear, miller office rain window, the two barn lean
inserts, montreal drainpipe + dust) by hand; judge the widened rooms
and the shed's swung leaves on the sheet; a "door narrower than its
opening" check (Lena's front door passed ADRIFT because the header
spanned it).

THIRTY-FOURTH PASS. Sheet from 284d2904: 1559 frames, ALL 122 locales,
no skips — the first complete sheet. highway_101 (dusk) and
small_wood_road read as roads: guardrail, centre line, treewall,
mailboxes; both are draft 1 and dark at dusk. The widened rooms read
as rooms (finn's partition and window, the break room's counter run,
the back office's desk wall); Lena's leaf fills its opening and the
couch nook reads through the cased opening.
· THE SEVEN FRAMES, each a different disease: miller office's window
  insert stood BEYOND the N wall (in the dark outside) — inside now;
  montreal's drainpipe insert looked at the pipe THROUGH the window
  glass (opaque here) — in the alley now, reframed off the brick;
  montreal's dust insert saw only the lit wall (1 cm motes are
  invisible) — low and tilted into the window's light; the barn's
  lean insert was 1 m from a dark plank on a dark wall — 2.3 m off
  with wall and ground; the centro smear was a dark band 24 m off at
  z 7 — a hot band twice as tall, 16 m off. (The two centro presets
  share the marker.) All five pass aim + sight.
· Board Lords' front-door insert had been black on the previous sheet
  too: the door's glass pane is an opaque dark slab 1.4 m from the
  lens — a daylight tint now. Its exit-sign practical followed the N
  wall (it was 0.7 m south of the sign).
· OPENING (report) in doorway_audit: a leaf narrower than the gap
  between its wall ends, nothing filling the difference. Ten found;
  four real interiors filled (board lords alley door 20 + 10 cm and a
  header, foxhole dressing room 1.1 m, natalie's front door 1.3 m,
  safehouse 1.1 m); swung leaves and massing-hosted doors skipped;
  the diner's Precipice_Door (0.98 m) stays as a report line.
· Buried details: kwik's aisle sign text and wet-floor text onto
  their faces, the ice-machine sign onto the machine's front (it
  faced the wall), miller's photographs and pit stop's prints onto
  their tables, the diner ticket out of the dessert dome. 7 loop
  partials left (scuffs under a mat, stains under a fixture, seams
  under a raised walk — hidden, harmless).
NEXT (draft 35): the roads' second draft (they are template + props:
lights, edge-of-set, coverage); the OPENING residue (diner Precipice
door); nightmare cell's 46 dots (they no longer report — verify on
the sheet); the near-black screen should read 0 — if the smear is
still black at dusk, give the ridge a practical.

THIRTY-FIFTH PASS. Sheet from 7580635c: near-black 1 (the stockroom's
default smear — the dock's dusk one reads now), flat 0. The user:
"still seeing a lot of objects just hanging out in the middle of
rooms, not arranged properly, up against walls or on top surfaces.
New door-like polygons in the middle of rooms. A door behind a sign
in the diner. One of the bedrooms looks too cramped, a bed and a
dresser both against a short wall."
· PLACEMENT AUDIT (report): OFF_WALL — a wall-class piece (dresser,
  wardrobe, bookcase, cabinet, locker, fridge, desk, crate, hamper…)
  whose back is > 12 cm from every wall and that leans on nothing;
  FREE_SLAB — a tall thin box reaching no wall at either end; TIGHT —
  storage within 45 cm of a bed on the same wall. First run 38 / 59 /
  2; after the wall regex learned that walls are named Hull, WallSeg,
  Lobby_Wall, Case_Back, Cub_Part: 35 / 1 / 2. Now 13 / 0 / 0, the 13
  deliberate (a nurse station, a reception desk, a milk crate that is
  Sam's seat, a TV on a crate, a wood stove 14 cm off its wall).
· THE KITCHEN TEMPLATE: seven kitchens (henderson, kowalski, ramos,
  grandmother, bianca, caldwell, miller) put the counter run and the
  stove at ROOM_D-1.0 — 0.55 m off the N wall in every one. ROOM_D-
  0.45 puts their backs on the wall face; everything keyed ROOM_D-1.0x
  moved with them (a −0.55 pass over ROOM_D-1.00..1.45), and the
  literal stragglers by name (kettle, skillet, eggs, chorizo, mugs,
  photographs, knife lines, water glass, toaster, grinder, bills
  drawer, two dishwasher faces that stood 0.4–0.7 m in front of their
  counters, Hans's oven and its cord).
· 22 PIECES TO THEIR WALLS: ben's gear crate and footlocker (at the
  bed's foot now), jesse's record crate (mid-floor → beside the amp)
  and dresser (2 cm into one wall, 5 into the other), sam's dresser
  with its drawers and the Wednesday list, safehouse's dresser and
  fridge (its locker stays: the door swing), diego's and graciela's
  nightstands (to the beds' heads / the wall, phone along), the back
  office's mini-fridge, natalie's bookshelf and fridge (SW corner —
  between the stove and the bed it left 30 cm, the NW corner is the
  counters' L; its sink was IN the W counter all along), new
  orleans's armoire, TV stand (screen, cans, console, cord and outlet
  along), the office bookcase, the school's teacher desk, chillwave's
  crate, the gym's fan crate, pit stop's milk crates (onto the
  partition's N face — south of it they blocked the walk-in), the
  drive-in's mini-fridge, wagner's record crate, nexcorp's beer
  fridge, montreal's bookshelf, maya's hamper.
· THE DINER'S DOOR BEHIND A SIGN: the card wall's 3 m corkboard hung
  across the Precipice Door (x 0.875..1.525 on the hall's N wall). It
  is 1.6 m wide now, west of the door, its 15 cards scaled to it.
· "A bed and a dresser both against a short wall": none measured
  tight (the TIGHT rule found natalie's fridge 30 cm off her bed —
  moved); the candidates by eye are ben (4.4 m) and jesse. NEXT: look
  at ben's and jesse's frames for which one the user meant.
THIRTY-SIXTH PASS (the kitchens finished). Sheet from 0cbf8598: 36
frames changed, 30 of them kitchen inserts and closeups — the
counters moved under them. The user: "seeing lots more new issues …
hopefully it's all work in progress and not stuff getting broken."
Frame-by-frame diff against the previous sheet (a scratch PIL
compare) is the tool for that question: every changed frame was a
moved kitchen, a reframed marker, or film grain. What the diff DID
find: (a) Ramos, Bianca and Caldwell wrote their counter as ROOM_D-
1.35, so the −0.55 pass left those three counters 0.30 m off the
wall while their stoves went to it — counters at ROOM_D-0.50 now;
(b) `make_coffee_pots` centres THREE pots on its anchor (py = cy −
0.50 + i·0.50), so a lone pot lands 0.5 m in front of the anchor —
five kitchens had their coffee maker hanging off the counter's front
edge, and had since the kits were placed; anchors are at the wall
plane now, pots at the counter centre; (c) Ramos's pulled-out bills
drawer stood half inside the counter; (d) Miller's phone insert had
the moved counter filling its frame — 1.5 m off the wall phone, level.
THIRTY-SEVENTH PASS. Sheet from 7ccc25ff: `contact_diff.py` is a tool
now (old sheet dir, new sheet dir → every frame whose 160×90 grey
diff ≥ 6, with brightness before/after, NEW and GONE): 20 changed, of
which the memory_warm and dream_blur moods account for 12 (film grain
— those moods are not deterministic frame to frame; a diff report
should say so), the corrected kitchens for 6. What it showed: the
coffee makers sit on their counters; Miller's phone insert, which the
reframe tool had pointed at a bare wall, is hand-placed over the cell
phone on the counter (0.7 m in front, 36° down).
· PLACEMENT IS A GATE. `DELIBERATE` names the pieces that stand free
  on purpose (the asylum's nurse station and its radiator under the
  barred window bay — its wall is the 1.2 m wainscot tile the rule
  cannot see; the cabin's wood stove and its clearance; cedar's
  reception desk; the back office's milk crate that is Sam's seat;
  nexcorp's locker bench; Houston's office L). The two that were NOT
  deliberate moved: the safehouse footlocker to the bed's foot (it
  stood 1.5 m short of it), and Simon's TV — on a crate mid-floor, its
  screen facing east while the armchair faced south — is on the E
  wall under the poster (raised), the chair turned to face it.
NEXT (draft 38): judge Simon's room and the safehouse on the sheet;
the "door-like polygons" — still unlocated (FREE_SLAB and HALF_SLAB
find nothing outside Houston's L); the diner's 0.98 m opening beside
the Precipice Door; the roads' second draft.

THIRTY-EIGHTH PASS. Sheet from fcdb082d (labelled "from
claude/meshy-image-generation-w92vr6@fcdb082d": the Deck's checkout
carries that branch NAME — the user's reset put our commit under it;
the real meshy work, 128 commits of Hero Studio / roster / keys, is
safe on origin). contact_diff: 9 changed, 7 of them film grain; the
safehouse footlocker reads at the bed's foot; Miller's phone insert
is a counter still-life with the phone at the left edge — a draft.
Simon's apartment has no preset on the sheet at all (no vn_shot
frames it) — it can only be judged in the game.
· THE DINER'S OPENING was a false alarm: the Precipice Door stands
  3 cm proud of a continuous wall; the fill test's plane tolerance
  went 2 → 8 cm. OPENING 0.
· HIGHWAY 101, DRAFT 2 (`build_dusk_dressing_2026_09`): amber
  reflectors on every guardrail post's road face over the visible
  stretch (y -40..155), a sedan 190 m up the lane with its taillights
  to the truck, a warm band 600 m out over the sea haze. The builder
  carries its own NEXT (dashboard glow, wet asphalt, the marker lit
  at the turn).
**2026-09-26 · HERO STUDIO · the roster's shortage, and looks.** (On
the `claude/meshy-image-generation-w92vr6` branch, where Hero Studio
lives.) The user: "a big shortage of characters … alternate
models/costumes … one isn't enough for the longer timelines." A scan
of every `say` node's `char` key against the roster's keys: 100
speakers with no entry, 85 of them in vol6 (Eileen 186 lines, BT 103,
Anita 92, Coach K 79 mentions, the Centro night shift, the team).
+36 heroes (each with canon quotes from the scenes, or `notes: SPARSE`
where the text gives a job and a bag and no face), and LOOKS: an entry
with `base` + `look {label, vols, when}` is another age or costume of
the same person, with its own image and GLB — Maya at 7 (vol5 ch5),
Miriam nine years on (vol6's courthouse), Ben in pads and in the TE-1
jersey, Anita in scrubs, Coach K at home. The page files looks under
their hero. Key fixes: `ben`, `mr_henderson`, `anya` (Elicia's
recorded persona) now route. NEXT there: chapter-based routing in
CharLayer for bare keys that cross eras (`miriam`); vol1's chorus
(Helen, Emily, Deborah, Eric) has no description in the text at all;
Lena's prompt says 2050s and vol7's wiki said 2025 — the user
ruled the 2050s (2026-09-26); both wikis are rewritten to it.

**2026-10-01 · DRAFT 44 · the three misses from sheets 40-42.**
· cape_perpetua_overlook: the fog box (lowered in draft 41) still read
  from the overlook as a frozen white lake. Fog is a grey floor low in
  the drop and ~65 flattened grey blobs over it, the Sitka crowns
  rising through.
· cabin_interior_bed: the window over the bed was a dark solid pane
  with nothing behind it — the glass is "the gray-green of cedars" (ch1)
  with a cross of glazing bars; the camera looks down the bed's length
  (yaw −2.55, pitch 0.05) with the window 24° left of centre (square on,
  Wall_E filled 67 % of the frame at 1.8 m).
· bar_exterior: the big lit window sat INSIDE its frame box, which hid
  the glow but an L-shaped sliver; the glow is in front of the frame.
Also seen on sheet 42: the intro video reached Drive from the Deck.
NEXT: sheet 43 for these three; Graustark; Kestrel.

**2026-10-01 · THE OPENING MOVIE (temporary).** The user: "I have a
modernmythology1.mp4 I'd like to make the temp starting title/credits/
opening movie that goes to main menu on click or finish and also play on
the pause/menu screen in the background. It will eventually be replaced
by a much more involved system involving unlocked assets and the media
player." Godot plays only Theora, and the .mp4 (60 MB, in the user's
Drive root, id 1xOg7lYAgVgkZ-DB4YBh3vIz4V3B-T8JL) is out of reach of both
this session's connector (too big) and the Deck's rclone (drive.file
sees only its own files) — so `godot/tools/install_intro_video.sh`
converts ON THE DECK: finds the .mp4 (or prints the Drive link), uses a
Theora-capable ffmpeg (system, else a static build into
~/.local/share/ffmpeg-static), writes
godot/assets/video/intro/modernmythology1.ogv at 1280 wide, and SAVEs
(video joins DRIVE_DIRS; .ogv excluded from git). `IntroMovie.gd` plays
it at boot (Main.gd) with sound; click / key / pad button after a 0.4 s
grace, or the end, → main menu; no file → straight to the menu. The
pause menu loops it silently under its dim. Loaded from the FILE
(VideoStreamTheora.file), so no Godot import is needed. Tested: the
installer end to end against a stand-in Drive; IntroMovie headless
(plays, grace, skip, no-file fallback). REPLACE with the unlockable-
assets + media-player system later (the user's plan).

**2026-10-01 · SHEET 43 · draft 44 judged; portrait sizes re-stepped.**
Landed: the cape's fog reads as a rumpled grey bank below the rail (no
longer a flat sheet); the cabin bedroom shows the window over the bed;
the bar's window glows. The cape bench insert is right (the canvas bag
on the dark wet bench) but dark. MISAIMED: cabin_interior_bed's
`shot_insert_window` was the kitchen's marker copied with the scene —
it framed the dining table; re-aimed at the window over the bed from
inside the east room. Portraits: mcu ≈ cu on every hero → all close
sizes neck-anchored in clear steps + aimed at the measured head (see
_VN_DIRECTION_PLAYBOOK, sheet 43). cathedral_interior still has no GLB
on the Deck (the builder must run there). **Sheet 44 checks:** the
three sizes step visibly; the bedroom window insert; the cape bench
lit enough to read.

**2026-10-01 · VOICE IMPORT · draft 2 — splits recovered.** The Deck's
import: 124 zips, 7,254 lines wired (vol5 1,587 / 2,949 · vol6 5,966 /
8,308), all 7,553 files on the Drive, audio audit 0. 982 skipped:
checked against git history at each zip's date, 480 were SPLIT (one
recorded paragraph, now 2-4 consecutive lines, same words), 29 trimmed,
293 unknown (no git version old enough). The importer now cuts a split
line's recording at its pauses (silencedetect; each cut at the piece's
share of the words, snapped to the nearest pause) — synthetic test on
the prelude's real 08-03 history: 24/24 clips cut in the right gap.
Re-run with --again. **Deck re-run (same day): 922 recordings cut
into 2,646 lines; vol5 2,831 / 2,949 voiced, vol6 7,324 / 8,308; only 17
lines still skipped; audio audit 0 over 20,639 paths.** Not yet heard
by ear. **Draft 3 targets:** the trimmed 29 (audio could
be cut at the pause after the kept words); the vol 7 scenes have no
voice zips yet; a loudness pass across takes from different days.

**2026-10-01 · SAVE survives a long upload.** The Deck's first voice
import worked (audio in place, game plays it) but SAVE's Drive upload
hit its 2-hour limit at 2,836 of 7,553 files (Drive creates ~0.4
files/s on rclone's shared client, whatever their size) and the crash
took the git commit with it — the vol 6 voice keys stayed on the Deck.
Now: git commits + pushes FIRST; the Drive upload goes in chunks (one
per folder: a voice scene, the heroes …) of only the pending files
(--files-from --no-traverse, 8 transfers), each chunk recorded in the
manifest as it lands, no time limit; a stopped upload resumes on the
next SAVE; the manifest is committed after, even when partial.
audio_reference_audit counts gitignored voice/ + drive/ paths as
Drive-held (the keys can be ahead of the manifest). Tested with a
simulated drop mid-upload: 3/9 recorded, the rerun sent the other 6.

**2026-10-02 · THE CH 0 CRASH (hotfix d25eaf11).** "game crashed on
loading up ch 0: _tell_mood_painted: Invalid call. Nonexistent 'float'
constructor." `get_shader_parameter("paint")` is null until something
sets the uniform; the game never did, every test tool had. RULE: never
read a uniform back from a ShaderMaterial for logic — keep the value
in a variable. And a test that mirrors the GAME's call order (load a
locale without set_paint) is now in the loop: `crashtest.gd` pattern —
instantiate Background3D, load_location, 10 frames, no other calls.
THE CATHEDRAL (ch 1): dark under every mood because its materials are
authored dark (concrete 0.14, brick 0.22, dark plank ceiling) with the
workbench lamp the only key at the VN vantage — a model chapter's
look, not a bug. Left for the Deck's verdict once it is built there.

**2026-10-05 · JOANNA'S ANIMALS + THE EMPRESS'S VOTIVES.** The creature
kit had only the crow. `_props/creatures.py` gains `make_dog` (lying
sphinx head-up · curled asleep · sitting; one-eyed option) and
`make_cat` (sitting · loaf). Rumpus lies by Joanna's block at the wall
and the cat sits at the wall's foot — Joanna's closeup now frames "The
cat ... The dog raised its head"; Rumpus sleeps curled by the shotgun
house's steps ("sleeps twitching in a sunbeam"). The Empress's floor:
votives on the four corner tables (only the middle three had them) and
ONE low warm wash at table height for all seven (the diner is far past
the ~12-light guideline — one light, not seven). Deck must REBUILD
graustark and diner. Draft N+1: the cat cleaning its paw (a pose); the
crow on the patched roof; damask as a woven tone, not a flat colour.

**2026-10-05 · THE HIEROPHANT AT HOME (ch 5) — St. Jude's + the park by
the Old Armory, draft 2 of both district landmarks.** §I "Outside St.
Jude's Acadian Church" played on the Lovers' roadside chapel; §IV "the
park near the Old Armory ... the abandoned bandstand" played on the
riverfront's parking lot. Both now play in the district, on two new
presets (`graustark_st_jude`, `graustark_armory_park`):
- ST. JUDE'S FRONT was a solid block: the steeple's 5 m base stood over
  the entrance and swallowed the door, the portico and all three steps.
  Rebuilt: a gable roof; the tower over an open entry (piers + lintel,
  the doors at the back of the recess), belfry louvres, a rose window;
  a portico on two columns; two steps to the front walk. The church
  straddled the riverfront zone's edge (half its steps under 1.2 m of
  field) — a level CIVIC PAD under it, and one under the armory, which
  stood on a 7 m slope.
- SR12 and the other district roads floated ~3 m over the flat zone (a
  berm's declared grade); on the flat zone and the pads they lie on the
  ground now (HWY 90 stays a berm).
- §I dressing: the street, curbs, sidewalks, front walk; "a long black
  car idling by the curb" with its exhaust; two parked cars; the
  fellowship table (cloth, lemonade dispenser, cup stack, cookies); the
  trash can with the cup in it; the parish sign; a live oak with moss;
  four parishioners in Sunday clothes. `closeup paul` frames the door
  he walks out of, `closeup maya` the lemonade table.
- §IV: a small park on the armory's east side — gravel paths, THE
  ABANDONED BANDSTAND (octagonal deck, posts, verdigris roof, two rail
  sections gone and one in the grass, weeds, cans, the crow on the
  rail), three chipped benches (John's with his open notebook and the
  pigeon), two lamps (one globe smashed), a trash can, two live oaks.
  `insert notebook` frames John's notebook on the bench.
Deck must REBUILD graustark.
Draft 3 targets: heat shimmer for §I's `lunch`; the armory's east face
(doors, plaque) and the park's street edge; working lamps as dusk
practicals; check the district priest figure's framing at the door.

**2026-10-04 · MIRIAM'S SUBARU — new locale, draft 1 (ch 18 Moon ·
ch 20 Judgement).** "Miriam's car was a 2009 Subaru wagon, dark green,
immaculate. The back seat had a folded blanket and a thermos of
coffee ... the crow ... settled on the roof." Both chapters borrowed
vol 6's `vehicle_cab` — Ben's crew-cab pickup PARKED at a scrub
turnout, the camera at the front console — for a wagon MOVING through
cane fields with the women in the back seat. `build_miriam_subaru.py`
+ preset `miriam_subaru`: the camera is Natalie, back seat, left of
centre, through the gap between the front seats over the dash at a
two-lane road through cane at dawn (sun through Nicola's passenger-side
window); the blanket and thermos, Nicola's duffel at her feet, Miriam's
canvas bag and travel mug up front, the cash in Natalie's door pocket,
the rearview ("Miriam's eyes met Natalie's in the rearview" now cuts
to it); the crow rides on the roof. 260 m ahead: the county-line sign,
the gas station (canopy, pumps, the store with the ice machine and the
metal bench, the price pylon, the traffic light over the exit with the
crow on it), the same Subaru parked at a pump — `wide station` and
`insert crow` play the county-line beats on the same set — the I-49
overpass, a sugar mill steaming on the horizon. Deck must BUILD
miriam_subaru (new GLB).
Draft 2 targets: the road does not move (a motion shader pass for the
drive); figures are not staged (the frames hold their places); a
Deck look at the dawn key through the passenger glass.

**2026-10-04 · GRAUSTARK'S RUIN QUARTER + THE MINSTRAL'S GREEN
(ch 9 Hermit · 17 Star · 20 Judgement · 21 World) — draft 2.** The
four presets were the last untouched vol 5 backgrounds, and the
establishes showed why: a red-and-white lighthouse on piles over open
water, a grey slab with two pale rectangles, a green box on a flat
field. Root causes, all in `build_graustark.py`:
- THE QUARTER WAS IN THE BAYOU CHANNEL. Every hero prop (chalked wall,
  I-beam, cottage path, desk) stood at z 0 over terrain at −3..−4.5 —
  four metres of air over the water. The prose names the fix: the
  cleanup year's limestone, "left in piles at the edges of the void".
  `graustark_elevation` raises a fill plateau (`RUIN_FILL_*`, plus a
  54 m disc round the void); the 6 m grid's edge cells make a natural
  embankment. District props that land on it at bayou depth (a skiff,
  crab traps, a hydrant, the lighthouse pier) skip.
- THE SINKHOLE WAS A LID. Four solid capped cylinders, widest on top =
  a raised disc. Now the terrain inside the lip drops below the floor
  and `build_sinkhole_bowl_2026_10` lines it with open terraced bands
  (strata faces / rubble ledges, darkening to a black pool), an apron
  over the coarse grid's dip at the lip, pavement sliding in, the
  fence the town gave up on.
- THE RIVERFRONT'S RIVER WAS BURIED. The preservation zone returned
  z 0 everywhere — over the riverfront river at −2.5 — so D'Ambrosio's
  boat stood on dry ground in every district view and the World's
  "down here by the river" had no river. The basin is carved, and the
  Minstral's slough joins it from the south beside the wreck.
- PROPS WERE PLACED ON THE WRONG HEIGHT. `terrain_surface_z(x, y)` is
  the height of the TRIANGULATED mesh (the 6 m cells), not the
  analytic field; the Child, the wildflower, reeds, knees and cypress
  stand on it now.
Built from the chapters' nouns: THE HABERDASHERY ("the gutted shell
of what might have been a haberdashery") round Joanna's wall —
checker floor with tiles gone, broken north wall where the I-beam
crosses (the beam now ten feet up on two pier stubs, "the crow perched
on a section of rusted I-beam ten feet above her"), empty window, the
doorway onto nothing, the fallen west wall, counter + hat block +
spools + crushed hat, her block with satchel/flashlight/chalk/charcoal/
lipstick; the WRITING as lines of words (three chalk verses, the
Star's charcoal verses, washed-out older chalk) with the receipt chip
"to the right of the chalk". JOANNA'S PATCHED SHOTGUN HOUSE replaces
the keeper's stucco box: back half on brick piers, tin gable with a
new sheet and a blue tarp, the torn north end in mismatched plywood,
joists jutting where the front rooms were; inside her desk-door-on-
bricks under the east window (candle, letter, envelope, pen, notebook,
flashlight — the desk stood OUTSIDE on the deck), pinned poems,
mattress on a pallet, crate bookshelf, candle niche by the door, her
D'Ambrosio's apron on a hook, the crow's gifts on the west sill; the
flagstone path, salvaged picket fence + the gate, the herb bed newly
planted, the clothesline, rain barrel, Rumpus asleep by the steps.
THE DEAD LIGHT: the district lighthouse is broken at ten metres, its
lantern room fallen (the Hermit's lantern is a failing flashlight;
the beacon practical is gone, `Practical_Candle` lights the room).
THE MINSTRAL'S GREEN: shaped hull beached on the slough bank, waterline
stain and rust, deck + rails half gone, deckhouse windows, pilothouse,
two stacks abreast (one broken — the old stack stood INSIDE the
deckhouse), the paddlebox cover with boards gone and the wheel (rims,
spokes, buckets) sagged into the water under the Frog's seat; reeds,
cypress knees, a life-ring, cypress on the far bank. The HWY 90 truss
gets real Warren diagonals (they were horizontal bars — a ladder fence
in every frame) and three bents over the fill.
DIRECTION: the Star is staged on the chalk-wall preset (five of its
seven establishes are at the wall); the house beats cut to new
`wide house` / `wide threshold` markers and the Hermit's lip moment to
`wide sinkhole`; the World opens at the river (it opened in the ruin
quarter with the Frog's close-ups pointing at a fence), switches to
the cottage for Joanna's section and back. JUDGEMENT IS A MONTAGE —
staged on the wreck, its ten close-ups all fell to the one closeup in
the pool: the Child. It now cuts through fifteen rooms already built
this month (Houston office, Montreal, the wall, the cab, the riverboat,
Antonio's office, the room over the laundromat, Natalie's, the
hospice, the design studio, the Iron Crow, the Roberts house, Elicia's,
the cab, the wreck) with each vignette's cues re-pointed at what that
room has (Erica's phone, the narwhal mug, the card and the bourbon at
the helm, the record player, the rose, Philip and Mackenzie, Elicia's
camera, the Frog). Deck must REBUILD graustark.
Draft 3 targets: a Deck look at every Graustark frame (the fill's
edges from the cottage establish; the sinkhole wide at night); the
cat, and Rumpus at the wall (no creature kit for them yet); the crow
on the patched roof for the Hermit/World lines (one bird for now);
"Minstral's Green" lettering on the paddlebox (Label3D); the post
office on Elm (Judgement's Joanna beat plays at the wall); the doll
stays gone. (Correction 2026-10-05: the riverboat preset IS the helm —
Dante's office upstairs — so the montage's Dante cut is right.) NEXT IN VOL 5: the Hierophant (ch 5) plays "Outside St.
Jude's Acadian Church" on the Lovers' ROADSIDE chapel and "the park
near the Old Armory ... the abandoned bandstand" on the riverfront —
the district has St. Jude's, the bandstand and the armory, but as
far-LOD box stacks, and the bandstand stands 550 m from the armory.
The ruin-quarter treatment (fill the nouns, presets at the real
buildings) is the next pass.

**2026-10-03 · THE EMPRESS'S FLOOR (ch 3, dambrosios_formal = the
diner's west room).** The Empress plays on "the power plays at Table
4, the whispered betrayals at Table 9 … the crystal at the empty
Table 6 … the speakers in Table 12's section … at Table 14, a man …
watching her", on "damask tablecloths" under "calculated mood
lighting". The west room held one banquet table with ten chairs — a
wedding, not a Friday — with the 2026-08 dressing's four corner
tables (4, 9, 12, 14) round it. The banquet table is gone; Tables 3,
6 and 7 take the middle of the floor (cloths to the floor, a votive,
settings and glasses, a numbered tent each; Table 6 laid and empty
with its crystal); the speakers hang in the far corners; the folded
NOTE lies on Table 14 beside the hundred (it lay on the banquet
table); John's Fool-chapter notebook now exists on Booth 6's table
(its insert had settled on that note across the building, the only
"note" there was). Markers: Nicola at the hostess stand from the
archway, Dean at Table 14, the note, the room's two close-up frames
INSIDE the room (they stood past the port wall). The Empress's own hostess podium stands at this floor's door, in
the corridor east of the partition doorway (the wrong-room gate
caught her close-up resolving to the Fool chapters' vestibule podium,
17.6 m from the camera); `shot_closeup_nicola` and its per-preset
override both frame it. Deck must REBUILD diner. Draft N+1: the
"intimate but not improper" light is the chandelier alone — the
votives want practicals; the cloths are plain cream, not damask.

**2026-10-03 · CAFÉ OLIMPICO — character pass (ch 19).** From the
chapter's nouns and the real café: the soccer on a TV high on the
east wall, tricolour bunting along it, five team photographs round the
poster, the chalk menu over the bar beside the clock, cannoli on a
tray and the biscotti jar, a tip jar, the sugar station, sugar and
napkins on every table, two more marble tables with their bentwood
chairs, the paper rack and a coat stand by the door, a plant in the
north-east corner, nine motes in the back window's shaft of light.
Clean on every gate (the coat on the stand reaches its base — a
jacket "hung above" the base failed the grammar gate; the biscotti
share their jar's name prefix). Deck must REBUILD cafe_olimpico.

**2026-10-03 · NEW ORLEANS ×3 — character passes (ch 7 / 8).** The
Roberts standard on the Chariot and Strength rooms, from their
chapters' nouns. ANTONIO'S OFFICE ("the cramped office above what
would, eventually, be Ember & Ash … hot because it was August"): a
drafting table with the elevation and a T-square, the permits board
under nine pinned papers, the site calendar, three sample boards
(brick, wood, tile) against the west wall, fixture boxes labelled for
the restaurant, a hard hat, a box fan on the floor, the drip pan under
the AC with its ring, the two coffees Jimmy set down, a tape measure,
a water bottle; the leaded window cut through the wall (its frame was
a plate); outside — two oaks dripping Spanish moss, the streetlight on
the corner the watcher leans on, the sidewalk. THE DIVE ("buzzing neon
… the sticky tabletop … the back door"): three taps and a bar mat, a
tip jar, napkin dispensers, ashtrays, a bowl of peanuts, the register,
a glass rack hung over the bar on chains, a COLD BEER neon over the
mirror, string lights along the north wall, Mardi Gras beads on the
mirror and the TV, a dartboard with its chalk scores, the specials
board, a gator head on the wall, the back door with its RESTROOM
sign, the street at night outside (sidewalk, curb, street, the facade
opposite, a lamp, a parked car). THE ROOM OVER THE LAUNDROMAT: the
window moved OVER THE DESK ("the small desk under the window" — it
was over the bed's head), the door hung in its opening with the chain
the chapter rattles, the shade half drawn, the LAUNDROMAT sign glowing
up from the facade below the window, the street three floors down and
the facade across, a towel on its hook, shoes under the bed, a rug,
paperbacks on the dresser, a transistor radio and a mug on the desk,
the key and the cigarettes on the nightstand, a wastebasket, a box of
dryer sheets. Markers re-aimed from the renders: Antonio's close-up
(the street windows behind him — it was the desk top), the office's
window insert (through the LEADED window at the oaks and the
streetlight — it framed the east pane), Douglas's close-up in the bar
(across the room from his booth — it faced the booth's back), the
bar TV (it cut the screen off), the room's letter (it framed the bed)
and mirror (a bare wall). All three clean on every gate. Deck must
REBUILD all three. Draft N+1: the office is still four times canon's twelve by
ten (a full rebuild at scale); the bar's booth wants its own light;
the room's bare bulb is the only practical. (2026-10-05: the booth
has a wall sconce with its own practical over Doug's table; the room's
LAUNDROMAT sign below the window is its second practical.)

**2026-10-05 · THE SUBARU DRIVES; ERICA'S GLASS CLEARS.** MIRIAM'S
SUBARU draft 2: "moving west on a two-lane road through cane fields" —
the road did not move. Nothing can move the car (a preset track moves
only the camera, which would leave the car), so the WORLD moves:
`scripts/RoadScroller.gd` on the scene streams every part named Cane_*,
Pole_* and Road_Delineator_* toward the camera at 24 m/s, each part
wrapping round the 880 m span on its own centre — and only while the
active camera is inside the car, so the county-line station marker
holds still (headless test: 9.7 m of cane in 60 frames inside, 0.0 at
the station). New: white delineator posts with amber reflectors on both
shoulders every 25 m, the motion cue at the side windows. HOUSTON
OFFICE: the preset stands inside Erica's glass office, the east
partition 20 cm off the lens — partitions, window and glass wall at 0.50
/ 0.30 alpha stacked to a white haze over half the establish; 0.16 /
0.20 now, the cubicle row reads through it. Deck must REBUILD
miriam_subaru and houston_office.

**2026-10-05 · THE VOL 5 CONTACT SHEET + THE CATHEDRAL FROM OUTSIDE.**
All 24 vol 5 presets rendered under their chapters' leading moods into
one sheet (the Arc 0 loop, run locally; `qa/contact_manifest.json`
regenerated for the Deck's VnContactSheet). The weakest frame was the
Magician's opening, `cathedral_exterior`: 57 m off on an empty plain
at night, Frasier's warehouse a small dark block — and the prose's
"kudzu vines thick as wrists throttled the chain-link fence" not built.
Draft 2: a level lot under the warehouse (CIVIC_PADS), cracked and
weeded, oil drums; the chain-link fence down the west edge throttled by
kudzu (blobs, drapes, vines); rust weeping down the brick; a sagging run
of roof (it "slumped"); two sodium yard lights with practicals so the
brick and the kudzu read in the purple night; the camera in the lot at
the fence corner with the fence receding down the left and the building
looming right. The district staged Frasier, his apprentice (no model:
the reference mannequin) and a visitor at the door — the prose has him
inside — they stand round the east side now, the apprentice dressed.
Also: the crow on the shotgun house's ridge ("settled on the patched
roof above the door"); the crew's lunch litter in Antonio's warehouse.
THE BUNGALOW (the sheet's next weakest — a sparse blue room): its
preset stood in the kitchen looking into the BEDROOM; and the living
room, the Priestess's main room, was an L round a "storage closet" —
two stub walls cut it in half, and the closet's slatted door was
mounted IN the living room -> studio doorway Elicia "paused in". The
closet's walls and door are gone (the gauntlet's station coordinates
all still hold — `the_storage_closet` stands by the Pomegranate Hour
boxes, which stay put, their tape label moved onto the top box); the
preset stands in the living room by the studio doorway, across the
boxes to the bedroom door. The full floor-plan redraw (kitchen open to
the living room, the windowsill basil in the main frame) is a gauntlet
design call — left for the user. THE WRECK's flat hull side (the
sheet's third): plating strakes in two greens with seams, a wooden rub
rail at the sheer, paint failing to primer and rust in patches, a row
of brass-rimmed portholes, and on the stern the name board with her
name blocked in over the rudder post. Deck must REBUILD graustark,
new_orleans_office and bungalow.

**2026-10-05 · ANTONIO'S OFFICE AT CANON SCALE — draft 4, the rebuild
(ch 7 Chariot · ch 5 §III · ch 20).** "The office was twelve feet by
ten. He could pace it in eight strides." Drafts 1-3 were a 7 x 6 m
period law office (four times the canon, banker's furniture, a drafting
table, a ROTARY phone for a man whose phone screen says Q. PAUL) with
the street at the office's own floor level for a room the prose climbs
a stair to. `build_new_orleans_office.py` rewritten: 3.66 x 3.05 m
under a 2.75 m ceiling; the front door to the iron stair (W), the back
door to the back stair Jimmy comes up (E), Jimmy's AC in one street
sash and the small leaded window (with cames) beside it (S), an interior
LOOKOUT over the warehouse (N). His desk under the lookout facing the
street; the smartphone face-down, the bourbon and the chipped glass,
the rolled plans with paper ends, Jimmy's two coffees, the banker's
lamp, a laptop; the visitor's chair; the file cabinet with the hard hat;
the permits board and sample boards; the worn runner where he paces;
the ceiling fan; the box fan and the drip pan. A storey down: the
street, Creole cottages with iron galleries, two oaks with moss, the
streetlight with the man in the charcoal suit beside it, the dark sedan
by the dumpster. A storey down to the north: the warehouse — brick and
graffiti, trusses, the cypress beam hanging crooked on two chain hoists
over two ladders, salvaged doors and planks, a clawfoot tub, the crew's
radio and cooler on a sawhorse, a work light (its practical lights the
floor the lookout sees). Every marker re-aimed; `establish_b` looks
down through the lookout. Deck must REBUILD new_orleans_office.
Draft 5 targets: the crew's lunch litter; the radio's practical; the
iron stair outside the front door; the man's cigarette ember; a Deck
look at the 12 x 10 room's preset from the front door.

**2026-10-07 · THE SHELVES, EVERYWHERE (the sheet's most repeated
defect).** Every stocked store showed the same "toy blocks": the shared
`make_snack_aisle` (grocery aisle, fueling station) and the Kwik Stop's
vendored copy built each "shelf" as a 32 cm VERTICAL fin, with every
product a floating saturated block beside it. `_props/merch.py` is the
merchandise grammar the Gas & Go pass began — chip bags with a band and
a crimp, candy trays, jerky, nuts, cookies, crisp tubes, motor oil,
washer fluid, and for the grocery: cereal boxes with panels, stacked
cans with labels, bottles with necks, jars with lids, pasta with
windows — plus `stock_gondola` (base, a shelving spine, horizontal plates
both sides, price strips and tags, the stock by PLAN: convenience · chips
· candy · auto · grocery). `make_snack_aisle` and `make_endcap` are
built on it; the Kwik Stop (CHIPS/SNACKS aisle, CANDY/JERKY aisle, both
end-caps) and the Gas & Go use it; the grocery aisle stocks as a
grocery. Fixed on the way: the grocery queue post stood inside aisle 0,
the produce stand 10 cm into its end, its tiers 3 cm over their base and
its scale hanging from nothing (the aisle's fins had been "supporting"
them); the Kwik Stop's stale price strips at the old fin pitch retired.
PERFORMANCE: a stocked store is thousands of packages — `join_stock()`
(`_props.geometry`, called by every export) joins each fixture's
`_Stock_` parts into one mesh (Kwik Stop 3364 parts -> 4 meshes; grocery
6647 -> 5); packages are sharp-edged (the auto-chamfer tripled their
vertices). The gates read builder names, not the GLB, so they are
unchanged. The fueling station's preset stood 2 m up at an aisle end
(a shelf top and an endcap header): at eye height in the open lane now.
Deck must REBUILD kwik_stop, centro_grocery_aisle,
nexcorp_fueling_station, nexcorp_gas_go. Draft N+1: the reach-in
coolers (`make_cooler_row`, the Kwik Stop's beer cooler) still hold
blocks — bottles and cans by the same grammar; the cigarette walls; the
pegboard chip racks hang flat plates.

THE USER, same day: "Looks like shelves blocking shelves and aisles too
cramped for pedestrians." Measured, it was worse than it looked: the
grocery had 0.50 m between two gondolas and 0.15 m from aisle 0 to the
checkout; the Kwik Stop's endcaps stood 0.42 m off aisle 0's corners and
its soda pyramid 0.40 m off the aisle face; the fueling station's aisles
were 0.90 m apart, its endcap 0.23 m from the coolers and its register
0.05 m from the cooler bank; the Gas & Go's ice merchandiser 0.38 m from
the counter. Re-laid: the grocery is two 4 m aisles 1.40 m apart with
the endcaps on aisle 1's ends (Aisle_3 removed), the checkout lane 1.15
m, the bale clear of the produce; the Kwik Stop's endcaps on the WEST
ends of its two aisles and the pyramid in the open entry zone; the
fueling station's aisles 1.20 m apart, its register narrower and west of
the coolers, its coffee counter against the north wall east of the
restroom door, one endcap against the front wall; the Gas & Go's ice
chest OUTSIDE by the door (where gas stations keep it) and its aisle
0.2 m east of the coffee bar. NEW GATE `walkway_audit.py` (in the suite,
ceiling 0): every pair of floor-standing store fixtures at least 0.90 m
apart unless they touch as one fixture — it found four lanes the first
measurement had missed. The grocery GLB is 7.5 MB now (two aisles).
Deck must REBUILD kwik_stop, centro_grocery_aisle,
nexcorp_fueling_station, nexcorp_gas_go. Draft N+1: extend
walkway_audit's STORES to the diner, the cafes and the bars (tables and
chairs: the same question at a different scale).
THE USER, again: "No they don't — the glass case can't be opened by the
island obstructing it." Right: walkway_audit measured the gaps BETWEEN
fixtures and never the floor a door swings into, and it did not know the
islands' names. The Kwik Stop's ice-cream chest (`Novelty_Cooler`, the
island) stood 0.70 m in front of beer-cooler doors 0 and 1. NEW GATE
`case_access_audit.py` (in the suite, ceiling 0): 0.90 m clear in front of
every glass-front case's doors (the door face is the side away from its
wall). Its first run found eleven more blocked doors and walkway's widened
island list found eleven cramped lanes; all fixed: the chest is 0.70 m
deep and centred in the cooler lane (0.98 m to the doors, 0.98 m to aisle
1); the grocery's cooler doors re-spaced off the meat case and the frozen
bank (the propped door, its milk crate, its thermometer and its wear arc
moved with door 0 — the crate stays in the swing ON PURPOSE, named in
DELIBERATE), the soda pyramid and the un-cued pallet jack gone, the deli
case 1.10 m wide (0.91 m to the checkout), the produce stand and the bale
0.9 m off the freezer and the frozen bank, the wet-floor cone out of the
deli's doors; the PALLET is in Aisle Seven's lane against the shelf being
stocked, as the prose has it ("Diego parks the hand truck ... off the
pallet and onto the lower shelf", 3 AM — DELIBERATE in walkway_audit), its
clipboard and phone with it, its three markers re-aimed; the fueling
station's impulse rack moved with its register (it had stayed in front of
a cooler). The Kwik Stop's establish_c went up the cooler lane (it stood
nose-to-nose with the end cap). Deck must REBUILD kwik_stop,
centro_grocery_aisle, nexcorp_fueling_station.

THE USER: "Don't be afraid to make spaces and floorplans bigger.
Backgrounds always felt small and claustrophobic." — now a STANDING RULE
(CLAUDE.md, THE DRAFTING PROGRAM rule 5: size a room from the prose and
the real thing, then err larger; enlarge the room before shaving the
furniture). First application, CENTRO FOODS DRAFT 6: the supermarket was
a 10 x 8 m box with two gondolas for a store whose staff "covers all
twelve aisles and the produce wet wall and the dairy case and the meat
counter". `build_centro_grocery_aisle.py` rewritten at 30 x 22 m under a
5.4 m open-structure ceiling (bar joists, the main duct, a sprinkler main,
fluorescent strips hung on wires): the storefront with sliding doors, two
glass runs, the cart corral; four checkout lanes with lane lights and bag
carousels and the service desk; the produce wet wall (sloped misted
tiers) and three produce islands, the hanging scale; six 9 m gondolas
FRONT-TO-BACK (Aisles 5-9 with numbered blades, 1.9 m lanes, end caps on
the action alley); the dairy wall of twelve reach-in doors with the
propped one (milk crate, Russell's thermometer); receiving's flap doors
and the bale; the meat counter's service case; the deli and its slicer
counter, the bakery, the frozen bank; the bread racks; the lot outside.
The pallet is in Aisle Seven with the clipboard, phone and scanner on
it. `_props/merch.py` grew `axis='Y'` gondolas (a 90-degree turn) and
`lean=True` (front facings only: a 30 m store's back stock is never in
frame); furniture_grammar skips `_Stock_` (merchandise is not furniture:
527 s -> 16 s). Every marker and the preset re-authored; eight
practicals at the strips and runs. Deck must REBUILD
centro_grocery_aisle. Draft 7 targets: the reach-in contents by the
grammar; the manager's office window over the front; WEAR and D3 at the
new scale; shelf talkers; the other half of the twelve aisles past the
frame edge. NEXT BY THE SAME RULE: the Kwik Stop (a model chapter, 12 x
9 m — check it against the prose before enlarging), the vol 6 bedrooms
(4 x 4 m template boxes), the family kitchens (the Miller rebuild).

**2026-10-07 · THE MILLER KITCHEN, BUILT BIG (miller_kitchen draft 9,
bianca_kitchen_morning draft 2).** Two template boxes of one room —
`bianca_kitchen_morning` is Bianca's 4:11 in the same kitchen on
Meadowlark Circle ("the green terrycloth robe is on the hook by the back
door", "Mike's chair, which is on the short side near the window"). One
room now, `_props/miller_kitchen.py`, on `_props/kitchen_kit.py`: a 9 x 7 m
open kitchen (2.75 m ceiling) — the shaker run with the French-door
fridge, the coffee corner, the range under its hood and chimney, the
double sink under a CUT window onto the front yard and the cul-de-sac
(the prose looked through a window that did not exist) with THE LIGHT
OVER THE SINK in its valance; the island and three stools; the
breakfast table east with Sammy's head, Bianca's long side, Mike's short
end by the east window (sheers, the lit garage window beyond); the back
door and the robe; the pantry, the wall phone and its worn patch, the
calendar, the message board; the doorway to the front hall (the stair,
the front door, the coats); a 5 m cased opening onto the family room
(sofa, coffee table, armchair, TV, bookshelf, floor lamp, the backyard
window and its crape myrtle). Across the street the Gellers' house with
Don's porch light (a practical). Dressings: family (Mike's 6:24 coffee
and phone, the French toast, the cinnamon roll, the kolaches, the jar,
the Sentinel, the photographs, the white sedan) and dawn (the kettle,
the grinder, her cup at Mike's end, the cordless, the stationery and the
small drawer, Sammy's cereal; the pendants dark — "she does not turn on
the overhead"; a cool 4 AM ambient). Morning / pre-dawn skies; seven
practicals at real fixtures; 22 markers re-authored; the kitchen kit
gained handle posts that reach the body. The grocery's calendar was
buried in its wall (the helper faces +X): on the face now. Deck must
REBUILD miller_kitchen, bianca_kitchen_morning (and centro_grocery_aisle
for the calendar). Draft N+1: the upstairs landing from the stair's foot;
the family room's evening practicals; Sammy's school things on the
island; the sedan's two silhouettes; the henderson and kowalski kitchens
onto the kit (same template, same build-big pass).

**2026-10-07 · WINDOWS YOU CAN SEE OUT OF (the claustrophobia pass, batch
1).** 25 builders still built their windows as panes on SOLID walls —
nothing outside, the rooms sealed. `_props/views.py` `make_view(prefix,
side, wall_line, center, kind, ground_z)` lays out what is past any wall:
'front' (lawn, walk, curb, street, the houses across with porch lights
and mailboxes, a tree, street lights), 'back' (lawn, patio, fence, a
tree, the neighbours' roofs), 'side' (the neighbour's wall close, its
window, the AC pad), 'street' (walk, curb, two lanes, parked cars, the
facades across, lamp posts); `ground_z` drops it a storey for upstairs
rooms. Batch 1, cut (`make_wall_with_openings`, the window
`see_through`, a sky in the env): sam_bedroom (upstairs at the Millers':
the cul-de-sac and the NexCorp mailbox across — its back-yard view went,
its window insert re-aimed out and down), maya_bedroom and
kowalski_kitchen (their existing back-yard views now seen), jesse and
diego bedrooms (upstairs back yards), henderson_kitchen (the front on
Magnolia), safehouse_bedroom (between the boards, a side yard),
graciela_bedroom (west: the side yard). Skies by each scene's dominant
mood (night rooms get a night sky). Deck must REBUILD those eight.
Batch 2 next: kai, finn, miller_office, hospital_room,
caldwell_kitchen_night, daily_grind, cosmic_comics_interior,
missing_link, salty_tome, caldwell_radio_room; then the loop-built ones
(pit_stop_interior, chillwave, lena_apartment, ember_ash_office).

**2026-10-07 · WINDOWS, batch 2 (ten rooms) + a sky bug.** Cut:
kai_apartment (a side yard, upstairs), finn_apartment (its D5 treeline
now SEEN), miller_office (the back yard in the rain, the neighbour's
house), hospital_room (the street three storeys down),
caldwell_kitchen_night (the back yard, night sky), daily_grind (the
street through both front windows), cosmic_comics, the Missing Link
and the Salty Tome (their D5 streets now seen through the cut glass),
caldwell_radio_room_night (the back yard). Skies by mood (day, dusk,
rain, night). The Missing Link's treeline slab read black through the
cut panes: a field and a low treeline at 34 m now, sky over them.
MoodCycler: scene_default no longer overwrites the scene's sky/fog
with a night one (F11 / leaving lightshow_extreme). Deck must REBUILD
those ten. Draft N+1: the loop-built windows (pit_stop_interior,
chillwave, lena_apartment W, ember_ash_office E, board_lords,
hans_bakery_back_kitchen); window markers for kai, hospital, the
Caldwell rooms and Daily Grind (none look out yet); exterior key light
for the outsides (lit by ambient only, they read dim against the
interior practicals). [CORRECTED 2026-10-07: not so — every interior's
Key/Fill/Back directionals run with shadows OFF, so the outsides take the
same key as the room. What reads dim is dark material (the Missing
Link's treeline) and facades turned from the key; fix by value, not by
adding lights.]

**2026-10-07 · WINDOWS, batch 3 (the loop-built ones).** Pit Stop
(both storefront panes + the two W booth windows + the kitchen's N
window: its W "frames" were SOLID 1.70 x 1.55 slabs — real head, sill
and jambs now; the 4.4 m treelines 8 m out became fields with low
treelines at 31-35 m; a street past the front), Chillwave (its D5
street), Lena's (the kitchen window onto the alley's Starfish Nebula
mural — the mural is finally SEEN; the front window onto Hemlock a
floor down), Board Lords (Main Street), Hans's back kitchen (the
hemlock at 4 AM, a dusk-blue sky). Deck must REBUILD those five.
Still solid: ember_ash_office's CornerAcross — a LIMINAL threshold
(the man in the charcoal suit); cutting it is a liminal-JSON decision,
not a window pass.

**2026-10-07 · window_backing_audit + Kwik Stop's storefront.** A new
gate in the suite (ceiling 0): any pane whose wall is uncut behind it
fails. Its first sweep found Kwik Stop's picture windows on solid
make_box walls — cut now (piers, spandrel, lintel), the warm glass
0.70 → 0.35 so the lot reads; the hose reel moved onto the pier, the
burger decal's sign onto the glass; shot_insert_window ("the south
glass, the lot beyond") re-aimed out of the tables and through it.
Deck must REBUILD kwik_stop and pit_stop_interior.

**2026-10-07 · window inserts.** shot_insert_window added where no
shot looked out (sightline raycast-checked through the pane before
writing, the window's own mullions ignored): kai_apartment (the side
yard), hospital_room (moved off the vitals monitor: the street below),
caldwell_kitchen_night (over the sink, the back yard at night),
caldwell_radio_room_night (the yard; its open S door now shows the
yard too — a booth with an outside door), daily_grind_interior (the
street, the facades across, a parked car). Scene-only; no rebuild.

**2026-10-07 · scale checks (BUILD BIG, measured before enlarging).**
The Kwik Stop against its six chapters: one counter girl, "the back
cooler hums against the far wall", "the table by the window", the Gas &
Go "across the intersection" seen from it — a small store; 12 x 9 m
stands (a 30 m Centro this is not). The vol 6 bedrooms measure 4.0-4.8
x 4.5-5.6 m — larger than real rooms already; what read claustrophobic
was the SEALED windows, cut this pass. Next by the rule: the
Henderson and Kowalski kitchens onto `_props/kitchen_kit.py`.

**2026-10-07 · THE HENDERSON KITCHEN ON THE KIT (draft N).** It was a
store counter (`make_counter`) and a chamfered box for a stove. From
the prose: "He stands at the kitchen sink for a long minute ...
Through the open window, the cicadas are loud" (ch14, ch20) — the sink
faced a SOLID N wall. Now: the N wall cut over the sink, the window
open (frame only), the back yard past it (`make_view` back); a base
run wall to wall on the N face in the Hendersons' oak and gold formica
with brass pulls, almond subway tile, the kit sink under the window, a
dishwasher, the kit range (its own oven face — the pot roast's "on
warm"), uppers either side of the window and clear of the clock; "the
kettle his mother uses and his father does not" on the back burner.
The cream fridge with its magnets stays. `kitchen_kit` gains `rail=`
(the door rails were hard-coded white shaker: cream stripes on oak).
shot_insert_coffee re-aimed onto the pot; shot_insert_window added (the
sink window, ch20's cicadas). Deck must REBUILD henderson_kitchen (and
miller_kitchen, unchanged in look). Draft N+1: the porch build's
lit-window match on the S side; wear on the formica at the sink; the
basement stair void deeper than a 2 cm card.

**2026-10-07 · WINDOWS, batch 4 (the gate's own list).** window_backing_audit
was blind to every make_wall (no install_stubs); fixed, it found 17 more
panes on solid walls and, with its new frame-board test, 20 windows
whose "frame" was one solid board over the opening. All cut / ringed
(`structure.make_frame_ring`): Ben's room (the back yard a floor down),
the cabin (both S windows, both E — its Sitka and station wagon now
seen), Coach K's (the side yard past the curtain), Cosmic Comics (the
street), the courthouse (sky and the square behind the bench), El
Rancho's drive-thru (the lane), Faust's (the street two floors down),
Finn's S window, Kowalski's E window (its neighbour's yard), the
fueling station's storefront (the pumps), the pharmacy (the street),
Wagner's (the back yard at dusk), Asylum Ward C's bays (the grounds),
the bayou lighthouse, Cafe Olimpico's back corner, the hospice
(the garden), the New Orleans apartment (the gallery), the Roberts
kitchen E, Simon's (the fire escape), the drive-in (the screen and
the moon). Skies added by mood. Exteriors keep their dark boards
(bar_exterior, kowalski_backyard: the unlit room the street sees).
The gate now reads 0 across 122 builders. Deck must REBUILD all of
those listed plus henderson_kitchen and miller_kitchen.

**2026-10-07 · THE KOWALSKI KITCHEN ON THE KIT.** A store counter and a
chamfered-box stove, and the upper cabinets ran ACROSS the sink window
(cut in batch 1) — the yard Gracie's dad yells about the weeds in was
half behind a cabinet. Now the kit run in honey maple and butcher-block
laminate with pewter pulls and biscuit tile, the sink under the window,
the range where Bill cooks the eggs, uppers either side of the window
("hot sauce is in the cabinet to the left of the stove": Upper_Mid),
and the under-cabinet light Anita sits by under Upper_Mid — its
practical moved with it. The courthouse seal sat in the wall the
window cut opened; seated on its mount. Deck must REBUILD
kowalski_kitchen and courthouse_chamber. Draft N+1: the upper doors
with one ajar (draft 5's target), the dish rack's dishes. DONE IN THE
SAME PASS: the hot sauce cabinet (the last upper left of the stove) is
open — a shell, its shelf, the red bottle and its neighbours, the door
swung 70 degrees — and shot_insert_hotsauce frames it from the stove
side (it pointed up into the old solid box's underside).

**2026-10-07 · THE DAIRY CASE HOLDS DAIRY (centro_grocery_aisle).** The
twelve-door cooler was the beverage kit — beer six-packs and soda cans
under a DAIRY sign. The merch grammar gains the dairy kinds (gallon
jugs with the cap colour code, gable-top half-gallons, egg cartons,
butter, yogurt cups with foils, shredded-cheese bags) and a "dairy"
plan; `make_cooler_door(stock="dairy")` faces them shelf by shelf under
the `_Stock_` tag so join_stock merges them. Deck must REBUILD
centro_grocery_aisle (an 11-minute build here). Draft N+1: the
manager's office window over the front; the meat case's cuts by the
same grammar; shelf talkers.

**2026-10-07 · THE MANAGER'S OFFICE + THE MEAT CASE (centro_grocery_aisle)
· THE BASEMENT STAIR + SINK WEAR (henderson_kitchen).** Centro: "the
manager's office" is a mezzanine over the front's SE corner above the
service desk — a slab on a column with a green fascia, its front wall cut
for a window over the floor (blinds half down, the desk, monitor and
lamp behind them, a warm `Office_Lamp_Practical`), a corkboard of
schedules, a hatch rail, and a steel ship's stair under the slab along
the south wall (clear of the storefront glass and the desk clerk's side;
the desk's hanging sign moved north out of the office wall);
shot_insert_office frames it from the checkout lanes. The meat case's
twelve red slabs are cuts: steaks with their fat, ground-beef mounds,
chops with bones, chicken, sausage links, tied roasts, each tray with a
price tag on a pick and parsley lines between. Henderson: the basement
door's frame is a ring, the E wall cut behind it, the door CRACKED 25
degrees onto a landing and nine steps falling into the dark (the well's
walls, ceiling, handrail and a black end wall) — it was a 2 cm card;
the formica worn pale at the sink, a runner, the floor's path. Deck must
REBUILD centro_grocery_aisle and henderson_kitchen. Draft N+1: shelf
talkers and price-check signs (Centro); the office's door at the stair
head; a bulb on a pull chain in Henderson's well (lit in ch7?).
SAME PASS: shelf talkers — five a side on every gondola, at eye level,
flags out of the price strips (SALE yellow, NEW red, Centro green).
Remaining Centro N+1: a price-check station; the office door at the
stair head.

**2026-10-07 · THE LAST TOY BLOCKS (Centro checkouts, the Kwik Stop's
tobacco wall and pegboard).** Centro's four checkout candy racks held
solid saturated blocks: now gum tubes, jerky and nuts by the merch
grammar, authored along X and turned onto the racks' Y run with the
`_ROT` pivot (`_LEAN` on). The Kwik Stop's cigarette wall — a model
chapter, behind Sam all summer — was 18 x 16 cm bricks in snack colours
standing 4 cm INSIDE the east wall on a 2 cm rail: now a shelf plate
off the wall face and flip-top packs faced out two high, a brand to a
slot (white under its red band, gold foil, menthol green, blue, black),
joined as stock; the old band-painting pass (`build_cigarette_pack_faces`)
retired. The pegboard chip bags were 5 mm cards: now bags with a body,
a band and a crimp under the hook. Deck must REBUILD kwik_stop and
centro_grocery_aisle. Draft N+1: SNACK_TINTS still colours lottery
tickets, magazines, prepaid cards and gumballs — fine as colour, but
check each reads as its object at the counter shots. And the red
stacked boxes on the yellow mat by the Kwik Stop's door (shot_closeup_
customer) still read as toy blocks — find their builder and give them
a carton's grammar (band, handle cut, the 12-pack print). DONE: they
were `CupStack` (red-cup cases), with `CharcoalStack` and `BeerStack`
the same solid-slab pyramids — now kraft cup cases with their red band
and three loose sleeves of cups by the SALE topper; charcoal bags three,
two, one with red labels and crimped tops; the beer 30-racks as cases,
two courses a layer, banded faces and handle cuts — all joined as
stock.

**2026-10-08 · draft N+2 items.** Henderson: the bare bulb on its long
cord near the well's foot, lit low (`Basement_Bulb_Practical`, 0.55) —
ch7: "His eyes adjust to the kitchen light" — the only light past the
cracked door. The Kwik Stop's magazine rack was a solid black 0.36 x
1.10 x 1.84 box with its shelves and magazines modelled INSIDE it: now a
plinth, sides and a back on the west wall's face, five tiers stepping
back as they rise (ledge, lip, riser), four covers a tier with
mastheads and cover photos. The Centro office "door at the stair head"
was moot — the ship's stair rises through a hatch INSIDE the office.
Deck must REBUILD henderson_kitchen and kwik_stop.

**2026-10-08 · THE VOL 6 CONTACT SHEET, first findings.** Every vol 6
preset rendered in its chapter mood and tiled (`$S/montage.py`). First
nine frames: Sam's and Maya's rooms read as ONE room — the same three
"posters" on the west wall, each a tan sheet with a dark block and bar
(empty frames on the sheet), Maya's third half behind her corkboard.
`decor.make_faded_poster` now draws a DESIGN — band bill, movie
one-sheet, comic page, sports — sun-faded, with a white margin, picked
by `kind=` or by the prefix's hash, so all 38 rooms that hang posters
vary without edits (0 floats, 0 clips across the 38). Sam's three are
chosen (comic, one-sheet, show bill); Maya's west wall is hers now: a
mandala tapestry in lavender and teal on its rod, fringe loose, clear of
the corkboard. Deck must REBUILD every poster room (list_stale_builds
finds them: decor.py changed).

**2026-10-08 · CONTACT SHEET, round two of fixes.** From the sheet:
- **caldwell_radio_room_night was the WRONG ROOM.** Ch5: "the upstairs
  window is lit ... at her shortwave radio ... Morse code ... the cadence
  her husband Thomas had taught her"; Maya "sits on the edge of the bed",
  "helps her into bed". The builder had made a broadcast STATION BOOTH
  (mixing board, boom mic, rack, ON AIR sign, fluorescent tubes) and the
  window pass gave it a ground-floor yard. Rebuilt as Linda Caldwell's
  bedroom: the radio desk on the east wall by the south window (the
  transceiver and its amber dial, the straight key, headphones, the log
  open, QSL cards, Thomas's photo, the coax out the sash), the bed's foot
  toward it, nightstand and lamp, dresser and mirror, the hall door
  closed, the yard a storey down. Seven studio lights out; desk-lamp,
  radio-dial and bedside practicals in; preset and four markers re-aimed.
- **caldwell_porch_night was a room** — walled to the ceiling on three
  sides, the railing inside its south wall. Now open: the house wall and
  the roof on posts and beams, railings south (split at the screen door,
  the frame a ring, the screen see-through), west and east; the carriage
  lamp on a post (its practical moved), the conduit down the corner post,
  a night sky.
- **caldwell_kitchen_night on the kit** in Linda's palette (sage, cream
  laminate, chrome, pink tile): the sink under the window with its sill
  and her radio on it ("The radio, on the windowsill, stays off"), a
  percolator on the back burner, the floating water glass on the counter.
- **centro_dock** looked at sky only: tilted 12 degrees down — the dock
  edge, bumpers and the apron's lanes in the foreground. (Its cone trees
  are draft-1 crude: blobs next pass.)
- **`decor.make_floor_plant`** was ONE plant in 37 rooms (disc leaves
  floating off a pencil stem) in the same south-west corner: now snake
  plant / fern / ficus / monstera by `kind=` or the prefix's hash, soil
  to leaf connected (0 floats, 0 clips across the 37).
Deck must REBUILD the Caldwell porch, kitchen and radio room, and every
plant room (list_stale_builds: decor.py changed).

**2026-10-08 · THE WAITING ROOM IS NOT ROOM 318 (hospital_room).** Ch7:
"Maya is in the waiting room when Ben arrives ... a chair against the back
wall ... coffee from the vending machine". Ch8: Room 318 — the bed, the
IV, "the visitor's chair", Anita "by the window". One 5 x 5 box held both
(the waiting chairs and vending machine against the patient's wall; the
hospital_waiting preset framed a bed). The waiting room is its own room
now, next door in the same GLB: 7.9 x 5 m under four troffers (their
practicals), beam seating on the back wall and back to back, the drink
and snack machines, a water cooler, a TV on its bracket, a magazine
table, a ficus, a window three storeys up with the street below, the
double doors to the corridor. The preset and shot_insert_coffee frame
it; Room 318's headboard is seated on its own deck (it had leaned on the
waiting chairs). Deck must REBUILD hospital_room.

**2026-10-08 · facing seats.** The user: "Chairs facing each other with
no room between seems a big problem." The waiting room's middle rows were
built FACING (seat fronts 14 cm apart); they are back to back now — the
north row faces the back wall's row across 1.29 m, the south row the
doors. New gate `seat_clearance_audit` (0.75 m between facing seat fronts
unless a table stands between; ceiling 0) — its first sweep found only
this room. Same pass: centro_dock's cedars are lumpy junipers (three noise
blobs on a trunk), not cones; Jesse's room has its carpet ("puts the
phone face-down on the carpet") and show bills. Deck must REBUILD
hospital_room, centro_stockroom, jesse_bedroom.

**2026-10-08 · LINDA CALDWELL'S HOUSE, LIVED IN.** The user: "Too bare
and empty, the Caldwell." Forty years in one house, from the prose:
- **Kitchen:** a china hutch (blue and white plates on edge, cups, a
  doily and a vase), the rotary wall phone with its coiled cord and
  notepad, a chair rail and a painted lower wall, the canister set, a
  bread box, a spice shelf, her pill box and magnifier, the soup on the
  front burner ("soup in the kitchen"), a dish towel on the oven handle,
  café curtains tied back so her radio and two violets show on the sill,
  a checked cloth and a fruit bowl on the table, cookbooks and a recipe
  box and two photographs on the east wall, the fridge door's photos and
  magnets, a braided rug at the sink.
- **Her room:** a pieced quilt, her cane against the nightstand, slippers,
  a water glass and a book, her robe on the back of the hall door, the
  family over the bed and three frames on the dresser (Thomas's in brass,
  in the middle) with a runner and a jewelry box, her reading chair with
  an afghan and its lamp table and books, a low bookshelf, curtains at
  the radio's window, a picture rail.
- **The porch:** ch19 — "Linda in the wicker, Maya in the second porch
  chair, two iced teas on the small table, the third pulled out and
  waiting": the two rockers became her wicker chair (woven skirt, fan
  back, floral cushion; the blanket over its arm), Maya's white chair and
  the third pulled out; the house's FRONT DOOR in the house wall (it had
  none — Maya "stands in the doorway"), the house number and mailbox,
  geraniums on the railing, a wind chime.
Also: 14 wall calendars across the game stood 5 cm INSIDE their walls
(the `+0.05` template offset on 20 cm walls) — on the face now; and the
calendar's month grid printed into the wall on every east wall.
Deck must REBUILD the three Caldwell sets and the calendar rooms
(list_stale_builds catches decor.py).

**2026-10-08 · THE BAREST VOL 6 ROOMS, DRESSED.** A bareness probe
(`$S/bareness.py`: dressing groups per m2, eye-level wall coverage) ranked
the game; the vol 6 rooms on it, dressed from their prose:
- **henderson_garage** — "his father's territory", swept "on the first
  Saturday of each month": steel shelving with labelled bins, the
  toolbox, screw cans, gas can and bucket; garden tools on hooks; the
  push broom and dustpan (Jesse swept twice); the camping chairs bagged
  on the bench shelf; Nate's cooler and the Mountain Dew; the mower; an
  overhead rack of boxes; two shop lights on chains.
- **centro_stockroom** (12 % wall coverage) — the workbench with "the
  stockroom drawer" and the canvas gloves, the box cutter and tape gun,
  the receiving clipboard; empty pallets stacked by the dock with the
  stretch wrap; the mop sink and bucket; bollards at the dock door; the
  dock board; the electrical panel; a high wall fan; the extinguisher,
  first aid, eyewash and safety posters.
- **hospital_room** (Room 318) — the headwall (gas outlets, call box, the
  light over the bed), the nurse's whiteboard, a TV on its arm, a clock,
  the sink and towels and sanitizer, get-well cards and flowers on the
  sill Anita stands at, the pitcher and the straw cup and tissues on the
  tray, the call button on the rail, a pillow on the visitor's chair.
- **pit_stop_office** — Rick's father's office: the corkboard of permits
  over the desk, the opening-day photograph, the desk phone and the
  invoice spike, the floor safe, cases of to-go supplies, a shelf with
  the radio, a chair mat, the wastebasket.
Next by the probe: kai_apartment, ben_bedroom, coach_k_bedroom (vol 6);
then the older volumes' barest — lacombe_service_garage, christian_ice_co,
le_roulant_casino, roadside_chapel, houston_design_studio, pharmacy.

SAME DAY, the next three: **ben_bedroom** — the athlete's walls (the
pennant and framed team photograph over the headboard, a trophy shelf
with the game ball over a dresser, a sports print by the door, the
hamper); **coach_k_bedroom** — twenty years in (the wedding photograph and
two frames over the bed, the team picture and a plaque, the cedar chest
with a quilt at the bed's foot, a reading chair with his sweater, the
hamper); **kai_apartment** — the studio had a kitchen table and "the
clock on the kitchen wall" and no kitchen: a kitchenette on the kit west
of the window (sink, two burners, uppers, a mini fridge, the kettle, a
dish rack with one plate and one mug), a rug under the table. Deck must
REBUILD henderson_garage, centro_stockroom, hospital_room,
pit_stop_office, ben_bedroom, coach_k_bedroom, kai_apartment.

**2026-10-10 · overnight run, pass 40: THE DAILY GRIND, DRAFT 3 (build big).**
Lena's café played in a 7 x 6 m box under a 2.8 m ceiling. Vol 7
describes it across many chapters:
- the back door to the alley, the heat-pump compressor that runs "the
  hot-water lines for the espresso bar";
- "the ceramic milk pitchers ... on the bar in the order the morning
  regulars liked their drinks pulled";
- "standing at the bar looking through the front window at the
  slate-gray light over Main";
- the bell over the door, the CLOSED / OPEN sign;
- Wren's hot chocolate with its one hand-cut marshmallow, bought from
  Hans "for a stack of tokens";
- the corner table with "the fourth chair".

`build_daily_grind_interior.py` is rewritten as a corner storefront on
Main, 12 x 10 m under a 3.6 m pressed-tin ceiling, glass on both street
sides:
- **The bar** along the back, facing the front window: the pastry case
  of Hans's bread, the register with its token reader and tip jar, the
  two-group machine with the five ceramic pitchers, the grinder, the
  hand-off with Wren's hot chocolate, the under-counter milk cooler.
- **The back bar** behind it: sink, pour-over station, hot-water
  dispenser, decaf grinder, cups, beans, batch brewer; the mug shelves
  and the chalkboard menu; the copper lines coming down from the heat
  pump.
- **The corner table** where the window walls meet: four chairs, Kai's
  laptop (facing him) and phone, the Frequency paperback, Wren's
  notebook, the duffel by the fourth chair.
- **The rest of the room.** The window bar and stools, the side two-tops,
  five round tables under exposed-bulb pendants, the banquette on the
  brick wall under three of Lena's paintings on a track, the lounge
  (couch, two armchairs, book-swap shelf, floor lamp), the community
  board, the condiment station.
- **The back hall.** The restroom, the hot-water tank, the back door
  under EXIT.
- **Outside.** Main, the cross street, and the tower on the hill.

Scene and preset:
- **Lights.** A new rig of pendant practicals and the overcast window
  light.
- **Markers.** Thirteen, including named closeups: lena (at the bar),
  wren (at the counter), finn and tem (at the corner table). The tower
  insert moved out to the slope below the tower, because inserts stay
  within 40 m.
- **Names.** Several parts are named so they don't match the closeup
  cues: `Painting_*` (not "Lena_Canvas"), `Duffel` (not "Finn_Duffel"),
  `HotWater_Dispenser`.

Deck must REBUILD daily_grind_interior.

Draft 4 targets:
- rain on the glass and the wet street;
- the studio door off the alley, seen through the back door's window;
- the pre-six-oh-four dressing, with chairs up on the tables;
- the dusk look for "Tem and Lena were the only two people".

**2026-10-10 · overnight run, pass 39: THE DRUGSTORE, DRAFT 2 (build big).**
vol1 ch2 "The Drugstore" played in an 8 x 6 m first-generation box. Its
"annex" was gray, and the mirror was bolted to the sales floor. The
prose:
- "whitewalled fortress of solitude ... my kingdom — of cheap
  fluorescents and impulse buys";
- the office has the computer, the coffee and the pills, and Faust
  "stands up and inspects himself in the mirror" before he "exits the
  office";
- "Deborah is helping a customer at the front table ... Faust checks the
  bottle and hands it over";
- Eric puts down lunch: Vietnamese, six eggrolls.

`build_pharmacy.py` is rewritten as a chain drugstore, 26 x 22 m under a
3.6 m drop ceiling of troffers:
- **The front.** The storefront and sliding doors, the lot and the
  street. The storefront is drawn as glints on open mullions (the
  picture-window rule); vertex-alpha glass would also work, since
  `LocaleGlass` makes it transparent at runtime. Two register stands with impulse racks, the baskets, the
  security pedestals, a promo table, the magazine rack, the photo kiosk.
- **The aisles.** Seven gondolas with endcaps and hanging aisle signs,
  wall bays, and five cooler doors.
- **The pharmacy.** It is raised 45 cm, so the pharmacist looks out over
  the shelf tops:
  - the PHARMACY soffit, and the DROP OFF / PICK UP / CONSULTATION
    stations along the counter (the counter is "the front table");
  - the will-call rack of white bags, the work island with its trays and
    screens;
  - THE LUNCH on the island: the bag, three clamshells (one open on its
    eggrolls, with chopsticks), the sauce cups;
  - the back wall of stock bottles.
- **The office.** White walls and one green-white troffer. The desk holds
  the monitor, the coffee, the open bottle with its cap off and three
  tablets beside it. The full-length mirror is on the E wall. Also: the
  reference shelf, the diplomas, the drug-rep samples on the file
  cabinet, the corkboard, his jacket.
- **East of the pharmacy.** The waiting chairs, the BP kiosk, the flu-shot
  sign, the restroom and EMPLOYEES ONLY doors, the fountain.

Scene and presets:
- **Lights.** A new rig of troffer practicals (`Fluor_*_Practical`), a
  key straight down, and the sun through the storefront.
- **Markers.** Five, suffixed per preset. The four stale draft-1 inserts
  (checkout, gum, register, office) are gone, and
  `godot/qa/contact_manifest.json` is regenerated (it was stale for this
  whole night's sets).
- **`pharmacy_floor`.** From the counter's edge on the platform, down the
  lane to the glass.
- **`pharmacy_office`.** From the door corner: the desk and the mirror.

Deck must REBUILD pharmacy.

Draft 3 targets:
- the trickle of customers' traces: a cart left in a lane, a basket at
  the pickup, the queue stanchions;
- seasonal endcaps for the chapter's month;
- privacy glass on the consultation window;
- depth past the restroom door;
- the mirror as a real reflective surface (a ReflectionProbe or a
  planar-mirror trick); it reads as a pale panel now.

**2026-10-10 · overnight run, pass 38: "TWO DOORS DOWN" (from the sweep).**
The prose puts the unit "two doors down at the back of the strip mall"
from the Foxhole's back door. The set had the unit's door right next to
it.
- **The unit.** Its door now stands 3.5 m further along the back wall,
  with a plain service door between.
- **What moved with it.** Its window with the papers taped inside, the
  gap light under the door and its spill, and the `shot_insert_unit` /
  `shot_insert_door` markers.
- **The vantage.** `new_auburn_strip_mall` is re-aimed (yaw −1.215) so
  the frame reads left to right: the Foxhole's lit door, the plain door,
  then the unit's dark door with light under it.

Draft 2 target: a third back door with its own grease bin, so "two doors"
counts from the frame alone.

**2026-10-10 · overnight run, pass 37: THE VOL7 MONTAGE, SPLIT (from the
sweep).** Frequency Interlude II played all its places on the warehouse
cathedral. Four `bg` nodes now give each segment its place:
- **The Speak & Spell** "in the back room of Cosmic Comics" goes to
  `cosmic_comics_back_office`, which carries the prop and its insert.
- **"FINN — Cape Perpetua trail, fog bank approaching"** goes to
  `cape_perpetua_overlook`.
- **The Demon's TX-LA-01 telemetry** stays on the cathedral, its speaker
  "in the warehouse cathedral".
- **"A JETTY, SMOLVUD — fog"** goes to the cape's fog (there is no jetty
  set yet).
- **The phone cue.** Finn's `insert phone` had no anchor on the cape, so
  his phone now rests on the trailhead post with the dropped GPS pin on
  its screen, with a marker.
- **The JSON.** It was rewritten in its own 1-space indent, so the diff
  is the four nodes and nothing else.

Draft 2 target: a Smolvud jetty set for the Frog.

**2026-10-10 · overnight run, pass 36: THE POST OFFICE ON ELM (a new set from
the sweep).** vol5 ch20: "She was at the post office on Elm ... The
envelope had gone into the outgoing bin ... The floor tiles of the post
office cracked in a single precise line from the outgoing bin to
Joanna's feet. The line passed between her shoes. The line continued to
the door. The door ... opened of its own accord." It played on the chalk
wall in the ruins. The new `graustark_post_office` is a small-town
Louisiana lobby, 9 x 7 m under a 4 m ceiling:
- **The room.** Checkerboard tile, two ceiling fans with globes.
- **The counter.** Three windows behind bronze grilles, with the scale
  and the date stamp. The OUTGOING bin behind it with its letters, a
  canvas hamper.
- **The lobby.** A wall of brass PO boxes, the lobby table with its pen
  on a chain, the flag, the clock at 10:44, the wanted board.
- **The S front.** The window, and the door standing open.
- **THE LINE.** One straight crack of jogging segments, with tile chips
  along it, from under the bin's end of the counter to the door.
- **Outside.** Elm Street with its fronts and a live oak.
- **Scene and markers.** The rig is written row-major this time. Four
  markers: the clerk's closeup (oblique, so the counter screen does not
  fill it), Joanna halfway to the door, the crack insert.
- **ch20.** It gains a switch to the post office at node 74 and back to
  the chalk wall at "They walked back toward the ruins".

Draft 2 targets:
- the alley beside it, where the animals wait;
- Elm Street beginning to lift.

**2026-10-10 · overnight run, pass 35: THE SMOLVUD CO-OP (a new set from the
sweep).** The organic co-op is named across nine vol7 chapters: Finn
delivers its boxes by bike; Margaret has run it "since 2041"; there is
"her apartment above the co-op"; it closes for a morning. It had never
had a set, so ch12's visit ("Margaret was at the front ... at the counter
going through the morning's invoices") played on Main Street outside
Board Lords. The new `smolvud_coop` is an old storefront on Main, 12 x 9 m
under a 3.4 m joisted ceiling:
- **The street front.** Big front windows with rain on the glass, the
  green door with its bell.
- **Margaret's counter.** The register tablet, the invoice clipboard and
  her pen, the scale, a tip jar.
- **Hans's bread.** On its rack beside the counter, the seeded loaves.
- **The floor.** Produce in crates on two tiered tables. Two gondolas of
  jars, bags and cans. Seven bulk bins with scoops on the W wall under
  the chalkboard prices. The cooler wall on the N: milk, eggs, the fish
  co-op's smoked salmon.
- **Finn's crates.** Labelled and stacked by the back door; the corkboard
  by the front.
- **Outside.** The awning, Finn's cargo bike, the wet street and the
  facades across.
- **Scene.** Pendant practicals, a cooler glow, a window rain fill; five
  markers.
- **ch12, split by three inserted `bg` nodes.** The walk stays on
  `main_street`. "The co-op opened at six" cuts to the co-op. "The crow
  was on the kitchen table" cuts to `finn_apartment` (the crow, the
  cloth, the hexagon). The drive out returns to `main_street`.

Draft 2 targets:
- the stair to the apartment above;
- Margaret's glasses;
- the morning delivery staged on the crates.

**2026-10-10 · overnight run, pass 34: THE FOXHOLE "DRESSING ROOM" IS A
CLOSET (from the sweep).** vol6 ch22: "a storage closet with two folding
chairs and a clothing rack and a sign on the door that says DRESSING
ROOM in marker. The fluorescent overhead has a slow buzz." Drafts 1-2 had
dressed it up as a green room: a bulb-framed vanity, a couch, a
mini-fridge, a rug.
- **Removed.** The vanity, couch, fridge and rug, and the two scene
  lights that only lit them.
- **Kept.** The folding chairs, the rack, the tube, the door and its
  marker sign, the cases, the setlist.
- **Added: the closet's own things.** N-wall steel shelving of the
  venue's supplies: paper-towel flats, cleaner bottles, glassware
  crates, a merch box with a shirt, toilet paper, a cable coil.
- **Added: the floor.** The mop bucket and its mop, the stack of spare
  folding chairs, and floor left clear along the W wall for Carl.
- **Markers.** A closeup re-aimed off the chair stack.

Draft 4 target: the hallway to the stage door.

**2026-10-10 · overnight run, pass 33: EL RANCHO FROM OUTSIDE (from the
sweep).** vol6 ch16's taqueria segment happens entirely outside, in BT's
car: "TAQUERIA EL RANCHO in red paint on a yellow building, with the small
image of a steer's head on the side of the building under the sign, faded
... The drive-thru is at the back ... He parks in the small lot at the
side of the building, in the spot under the steer's head." It played on
the dining room inside.
- **The building.** `el_rancho_taqueria` grows the yellow skin (named
  `Facade_*` so the corner joins with the walls pass), the roof and
  parapet, and the red TAQUERIA / EL RANCHO sign board over the front.
- **The W side.** The steer's head painted on the wall and faded to
  orange: face, muzzle, horns, eyes, with its painted name above.
- **The side lot.** Stripes and a wheel stop, BT's beige Altima in the
  spot under the head, and the pole light with a sodium practical. The
  drive-thru lane and the broken speaker already stood at the E window.
- **Preset and routing.** New preset `el_rancho_drive_thru`; both ch16
  El Rancho segments route to it. Car closeups are framed from outside
  the doors, pulled back so the solid body does not fill them.

Draft 2 targets:
- the drive-thru window conversation's own framing (Hugo);
- the front's sign at insert scale.

**2026-10-10 · overnight run, pass 32: THE NEW AUBURN COUNTY COURTROOM (a new
set from the sweep) + a transposed-light fix.** vol6 ch8's arraignment is
in the New Auburn County courtroom: "bigger than she had expected. The
wood is darker". Sam is "in the third row"; the man in the charcoal suit
is "in the second row, behind the prosecution table"; there is "the
third row ... directly across the aisle", the clerk "beside the judge"
at her screen, "the side door", "the bailiff at the door of the
gallery". It played on `courthouse_chamber`, Graustark's parish
small-claims room, which stays as the Gauntlet's Justice board. The new
`new_auburn_courtroom` is 16 x 22 m under a 6 m coffered ceiling:
- **The room.** Dark wainscot to 2.4 m with its cap. Tall W windows with
  blinds, brass globe pendants.
- **The gallery.** Two banks of eight pews either side of a carpeted
  centre aisle; the bar rail and its gate.
- **The well.** The prosecution and defense tables with chairs, folders
  and pitchers; the lectern.
- **The bench.** Up on its dais with the judge's chair, nameplate, gavel
  block and the folder. The clerk's station beside it with her screen;
  the witness box.
- **The rest.** The empty two-tier jury box (an arraignment); the Texas
  seal between the flags; the side door by the defense table, moved
  clear of the jury box; the back double doors and the clock.
- **Outside.** The steps down to the curb, with Miriam's dark green
  Subaru wagon (door open, the quilt's outline on the seat), carried
  over from the old set's `insert subaru` and `insert quilt`.
- **Markers.** Ten, covering every cue. The preset sits in the aisle so
  all closeups are within 12 m.
- **The fix.** The light-direction gate caught a real bug in this
  pass's own helper. `.tscn` `Transform3D` lists basis ROWS, and the
  helper wrote columns. Every directional light it made tonight was
  rotation-transposed: aimed down, but from the wrong compass side.
  Erica's sun came from the NE, not the NW. All ten lights in the five
  scenes are transposed back, and the playbook carries the rule.

Draft 2 targets:
- the gallery's people;
- the hallway outside;
- the 15:04 light.

**2026-10-10 · overnight run, pass 31: BIANCA'S OFFICE (the wrong PERSON's
room, from the sweep).** In vol6 ch17 Bianca is "at her desk in the
small office off the master bedroom, paying the August bills ... The
electric bill is ninety-six dollars ... The cable bill is one
seventy-two. The Visa bill ... She closes the laptop." It played in
Mike's converted dining room downstairs (`miller_office`).
- **Her room.** Built into the same set 30 m east, where none of Mike's
  windows see it: a small upstairs room with the white writing desk
  under a morning window over the back yard. On the desk: the open
  laptop, the three statements with their logos and torn envelopes, the
  checkbook, the calculator, her coffee, Sam's school photograph, a desk
  lamp.
- **Around the desk.** The chair, a carcass bookshelf (its first cut was
  a solid box that swallowed the books, the solid-frame lesson again),
  the August calendar, the wastebasket.
- **Through the W doorway.** The master bedroom's carpet, the bed's
  corner, the dresser.
- **Preset and routing.** New preset `miller_office_bianca`; ch17 routes
  to it. Suffixed markers (bills, laptop, Bianca) and lights (window
  fill, desk-lamp practical).

Draft 2 target: the rest of the upstairs (the master bedroom proper).

**2026-10-10 · overnight run, pass 30: CLUB SHARP (a new set from the
sweep).** vol1 ch4: "a club in the heart of nowhere, beating with life ...
Club Sharp has a # for a logo. Dickens Dean seems to have the run of the
place. There is a gigantic arcade downstairs, several dance floors, and a
bowling alley". It played on the Foxhole, vol6's Texas punk black box.
The new `club_sharp`, built big because it is a dream that keeps
opening:
- **The main floor.** 24 x 18 m with 6 m to the deck, light trusses with
  their cans. Two dance floors of lit tiles.
- **The bar.** The long bar with a chrome top and LED strip, nine stools,
  the back bar of absinthe and other bottles, the absinthe fountain.
- **Dickens Dean's booth.** Up three steps on the N dais: velvet, a
  table with three absinthe glasses and the spoon, the # in neon over
  it.
- **The arcade downstairs.** On the W, a railed glass atrium opens onto
  it, 4 m down a stair: 24 cabinets in rows with lit screens and
  marquees, and starry carpet.
- **The bowling alley.** Behind the S glass: six lanes running away 24 m
  to their pin decks and pin-deck lights, scoring screens, ball returns.
- **Scene.** Neon practicals; four markers. The preset camera sits on
  the rail within 12 m of the booth closeups (the `wrong_room` FAR
  rule).
- **Wiring.** vol1 ch4's club_sharp, club_sharp_b and waking route to
  it.

Draft 2 targets:
- the crowd;
- the arcade's glow from the main floor (it reads dim past the rail);
- the car outside.

**2026-10-10 · overnight run, pass 29: THE SMALL WOOD REC CENTER (a new set
from the sweep).** vol2's second interlude is set at "Small Wood Rec
Center — a small, deteriorating one-room building on the main drag ...
that night was a dance instead of the usual casual come-as-you-are games
of foosball, pool, and scattered cartridges popped into an old Nintendo
system". It played on Harmony Creek High's weight room. The new
`small_wood_rec_center` is 12 x 9 m:
- **The shell.** Worn vinyl tile, wood paneling to 1.2 m, a
  water-stained drop ceiling with six troffers (two dead). The glass
  double doors and windows look onto the main drag at night: shopfronts
  and a street lamp.
- **The dance.** At the far wall: Jay Rose's folding table with two
  decks, the mixer and a CD stack, speakers on stands, the party light's
  three colored heads, streamers and balloons.
- **The room shoved to its edges.** The pool table and a leaned cue, the
  foosball, the TV cart with the Nintendo and scattered cartridges.
- **The back.** The chair stack and the two fold-ups pulled out by the
  magazine rack ("Janess and I made for the back").
- **Fixtures.** The bulletin board, the drinking fountain, the restroom
  doors, the snack window's shutter.
- **Scene.** Troffer, party-light and street-lamp practicals; four
  markers.
- **Wiring.** Routed. `gym_weight_room`, now only vol6's, gets its own
  vol6 bed.

Draft 2 targets:
- the eight kids and the shuffling pair;
- the middle school gym's pick-up game.

**2026-10-10 · overnight run, pass 28: THE SMALL WOOD CEMETERY (a new set
from the sweep).** vol2's graveside ("the minister says something about
roots and returns ... Jo stands beside you") is in Small Wood, Oregon. It
played on `parish_cemetery`, Graustark's above-ground tomb city of white
limestone vaults: a Louisiana burial form, for an in-ground funeral on
the Oregon coast. That set stays as the Tarot Gauntlet's Judgement board.
The new `small_wood_cemetery` is a lawn cemetery:
- **The setting.** Douglas firs and red cedars ringing it, the firs
  spaced so no two crowns cross. Granite uprights in rows, the old ones
  mossed, flat bronze markers, a family obelisk.
- **The aunt's grave.** The green carpet and the opening, the lowering
  device with the casket on its straps and a spray on the lid. The dirt
  mound under its tarp. The funeral home's canopy and valance, two rows
  of folding chairs with a program on one, the flower sprays on easels,
  the minister's lectern.
- **Around it.** The gravel lane with the hearse, the hills going grey
  in a fog-heavy overcast.
- **Scene.** An overcast key (daylight) and a sea-side fill; four
  markers.
- **Wiring.** vol2_graveyard routes to the new set; the ambient bed and
  the chapter-bed map gain it.

Draft 2 targets:
- the mourners;
- the hillside's fall;
- the ocean past the firs.

**2026-10-10 · overnight run, pass 27: JESSE'S ROOM, DRAFT 5 (a bed, and the
Telecaster).** The prose says "In his bedroom he sits on the edge of the
bed ... He puts the notebook on the nightstand. He gets in bed", "his back
against his bed". Drafts 1-4 had a futon on the floor, so the room now has
a twin on a frame, with the nightstand, its lamp, the notebooks, the clock
and the lamp practical raised to match. And the guitar the chapters name
every time ("his Telecaster unplugged in his lap") was a round-bodied
cylinder. It is now a Telecaster:
- the single-cut slab body in butterscotch and its horn;
- the black pickguard, the chrome control plate and bridge;
- the maple neck and fretboard, the six-in-line headstock with its
  tuners.

`insert guitar` and `insert telecaster` were framing the guitar case and
the neck; both are re-aimed at the body.

Draft 6 target: the Telecaster in his lap as the ch3 state; the body's
proportions.

**2026-10-10 · overnight run, pass 26: THE SWEEP (a background agent read every
chapter-used preset against its prose) + ANNA LOGUE'S OFFICE.** The sweep
found 17 mismatch classes. Fixed this pass:
- **`houston_design_studio` → Anna Logue's office (draft 3).** It was "an
  open-plan creative studio: drafting tables, brick wall, exposed duct",
  a loft. Justice has "her meticulously greige Houston high-rise office,
  three floors down from a law firm": Erica's firm, in Erica's tower.
  Rebuilt at 7 x 6 m:
  - one glass wall over the SAME city, Erica's `build_city` run through
    `plan.shifted` 10.5 m lower, with its facade and hawk filtered out at
    creation (not by deleting `bpy` objects, which the audits' recording
    stubs would not see);
  - greige walls and carpet;
  - the long white-oak desk with THREE monitors (EMBER & ASH on the
    third), the pen tablet, the cold brew, the glasses, the phone, the
    mesh chair;
  - the pitch deck pinned in a grid with Slide 7 dark, two air purifiers,
    the credenza with the colour printer and swatch books, a low sofa,
    one plant;
  - a sky, a daylight key, downlight practicals, six markers.
- **Routing.**
  - vol6 ch4's storm "across the subdivision" played on the Louisiana
    swamp (`louisiana_road`); it is now on `meadowlark_circle`.
  - vol2's 1902 cannery narration played on a modern Texas grocery dock
    (`centro_dock`); it is now on `grunion_beach`, the Oregon coast.
  - vol1's L. Ron memory montage cut to Graciela Ramos's kitchen
    (`grandmother_kitchen_morning`, picked for the word "grandmother"); it
    now stays on `riverfront_park`, where Faust is telling it.
- **Already shipped this run from the same list.** The safehouse (pass 25)
  and Finn's truck (pass 24).

STILL OPEN from the sweep (each needs a set, not a route):
- vol2's Small Wood Rec Center dance plays on Harmony Creek's weight
  room;
- vol2's Oregon funeral plays on a Louisiana tomb cemetery
  (`parish_cemetery`);
- vol1's Club Sharp (an arcade, dance floors, a bowling alley) plays on
  the Foxhole;
- `courthouse_chamber` is a Louisiana small-claims room where vol6 needs
  a Texas county criminal courtroom;
- vol6 ch17's Bianca at "the small office off the master bedroom" plays
  on Mike Miller's converted dining room;
- vol7 ch12's co-op interior is missing (it plays on the street);
- vol6 ch16's El Rancho drive-thru is shown as the dining room;
- the vol7 interlude montage is on the cathedral;
- vol5 ch20's post office is on the chalk wall;
- the Foxhole dressing room is a "storage closet", not a bulb-mirror
  vanity;
- the D'Ambrosio's dining-floor builds disagree;
- `jesse_bedroom` has a futon, but the prose has a bed and a nightstand.

**2026-10-10 · overnight run, pass 25: THE SAFEHOUSE, DRAFT 3 (the wrong
REGISTER: a sickroom, not a hideout).** Drafts 1-2 of `safehouse_bedroom`
were a spy's den: a red-string corkboard, a CRT (also against the no-retro
rule), a boarded window, a pizza box. The chapters (vol6 ch6, ch7, ch9)
describe a quiet sickroom. "A small frame house on a county road ...
owned, on paper, by ... Linda Caldwell". "Diego is in the back bedroom. A
doctor ... She has set the IV." "She sets the slushie on the bedside
table. She sits in the chair beside the bed." Graciela is on the back
porch on the phone; Doyle is in the kitchen. Rebuilt as the back bedroom
of an old frame house, 5.2 x 4.8 m:
- **The bed.** Head to the W wall. The IV pole with its bag and drip
  chamber, the line down to the bed.
- **The bedside table.** The lamp, the blue-raspberry slushie with its
  taped lid and red spoon, the water glass, his phone, Sam's spiral
  notebook, the pill bottles. The chair beside the bed.
- **The dresser.** A doily, Linda's old framed photographs, and Dr.
  Patel's tray: gauze, saline bags, gloves, tape.
- **The room.** A rag rug, the ceiling fan and its globe, painted walls
  and a picture rail.
- **Through the N window.** The back porch with Graciela's glider and
  mug, then the yard: a clothesline with a sheet, post oaks, a wire fence,
  the field, the treeline.
- **Through the door.** The hall's bulb, and the kitchen at its end with
  Doyle's coffee pot.
- **Scene.** A NE sun key (daylight), sky fill, fan, lamp and hall
  practicals, a kitchen fill. Twelve markers cover every cue in the three
  chapters, including Graciela through the window and the hands on the
  sheet.

Draft 4 targets:
- the front room and the kitchen as presets;
- ch6's night on the porch;
- Deck framing.

**2026-10-10 · overnight run, pass 24: FINN'S TRUCK (the wrong VEHICLE, twice
over).** vol7 ch2's drive, with the crow on the dashboard and "the
shortwave receiver from his grandfather" humming "through the canvas of
the duffel", rendered in Ben's green Texas pickup on a Texas turnout. And
Finn's duffel, with the charred wood, rode on that pickup's passenger seat
through every vol6 scene.
- **The truck.** "An older Toyota that had belonged to Finn's
  grandfather" is now built into `cabin_road`, on a gravel pull-out off
  the approach. It sits behind the road preset's camera, so the eight
  road scenes do not see it.
- **Its cab.** `vehicle_cab`'s cab is run through `plan.shifted` in faded
  red. Inside: the duffel, cloth and charred wood, and the shortwave's
  antenna out of the zip; the crow on the dash; rain on the windshield.
  The pull-out has alders, Sitkas and ferns.
- **Preset and routing.** New preset `cabin_road_truck`; ch2 routes to
  it, with suffixed radio, charred-wood, crow and Finn markers. The
  road's orphan `insert crow` now frames the dash crow through the
  windshield.
- **Ben's truck.** It loses the duffel and its marker. Its hazard button
  moves onto the dash face; it had floated 2 cm off.

Draft 2 targets:
- turn the truck to face downhill (`shifted` does not rotate);
- a single cab, not Ben's crew cab;
- the phone cradle is Ben's.

**2026-10-10 · overnight run, pass 23: ERICA'S OFFICE, DRAFT 4 (the wrong
REGISTER: a cubicle floor).** Drafts 1-3 of `houston_office` built "a
generic corporate office: glass partition, cubicle row, fluorescents", with
Erica in a glass box in its corner under a drop ceiling and the freeway 12
m down. The chapters (Wheel, Justice, Judgement) describe a law partner of
fourteen years "high in her sterile tower": "a temple to control. Glass
walls. Chrome accents. Files indexed with obsessive precision", "the
Italian marble floor", the custom teak desk, "the heat-shimmer rising off
the asphalt twelve stories below", the hawk, and her assistant Marcus at
her door with two coffees. Rebuilt at 9 x 7 m, ceiling 3.0:
- **The corner.** N and W walls are floor-to-ceiling glass on mullions,
  with the city 42 m down: street grid, the elevated freeway with its
  traffic, banded towers, the near one's office window lit. The hawk
  rides its thermal below the sill line.
- **The room.** Marble and a charcoal rug; a smooth ceiling with
  recessed downlights.
- **The desk.** The teak desk mid-room facing the door, her back to the
  glass. On it: two monitors, the phone, the chrome lamp, the eleven-page
  draft, Marcus's two coffees and his card, and "the small framed
  photograph on the corner of the desk, the only personal item" (so no
  diplomas). The third drawer; her ergonomic chair; two chrome-and-leather
  guest chairs; the credenza against the glass.
- **The walls.** A SW seating group by the W glass. The E wall of lateral
  files, every drawer labelled, under the law reporters.
- **The door and the hall.** The door ajar with its frosted sidelight;
  through it, the hall and Marcus's desk facing her door.
- **Scene.** A ProceduralSky (it was a flat grey background); a sun key
  from the NW (daylight metadata), a sky fill, downlight and lamp
  practicals; seven markers, including the closeup from the desk's east
  end with the city behind her. The audit allows the freestanding desk
  (`DESK_FREESTANDING_LOCALES`), and the mullions are named as the
  curtain wall the credenza stands against.

Draft 5 targets:
- the city at dusk as a per-preset variant (lit windows, freeway lights);
- the file labels at insert scale;
- Marcus's jacket on his chair.

**2026-10-09 · overnight run, pass 22: NATALIE'S APARTMENT, DRAFT 4 (the
futon and the things the prose names).** Moon puts Nicola asleep "on the
futon, under the twilight-colored quilt"; drafts 1-3 had a teal sofa. It is
now a futon: a low slatted wood frame, the teal mattress folded into seat
and back, wooden arms, the quilt over one arm. Also built from the
chapters' own sentences:
- **By the door.** The coat hook with her coat on it ("Took off her coat.
  Hung it on the hook"), with her work shoes under it.
- **The closet.** On the E wall.
- **THE SPARE CORNER.** The dead nook between the stove and the bed, with
  ten years of storage: boxes, a rolled rug, a record crate. In Judgement
  she clears it for a crib.
- **From Hanged.** "Discarded dance shoes soft as moth wings" in the
  aisle, "stacks of books leaning at precarious Borgesian angles", the
  "chipped porcelain teacups holding dried herbs" on the sill past the
  Hanged Man, and a second deck fanned on the floor.
- **From Moon.** The candle burning low on the rug, with a practical.

Draft 5 targets:
- the crib corner as a Judgement-morning variant;
- the fridge's magnets and photo;
- the room is 7 x 5.5 with the bed in a nook. Moon reads it as a
  one-bedroom, so a bedroom through a doorway would be the build-big pass.

**2026-10-09 · overnight run, pass 21: THE CAB, DRAFT 3 (the wrong VEHICLE:
BT's Altima).** `vehicle_cab` is "one cab for every vehicle": Ben's green
crew-cab pickup. But ch16, a 10.6k-character chapter set entirely in the
car, is in BT's "2017, beige" Altima ("BT, at the wheel ... The car is the
space BT gets to set the terms of"). Its El Rancho spread (the flauta box,
the cup, the leaking El Diablito, the cradle phone) was dressed into Ben's
pickup.
- **The Altima.** It now parks in the same turnout, east of the truck
  and nose to the road, with the picnic table off its left rear ("Eat in
  the car, eat at the table?"). It has a sedan body: long low hood,
  trunk deck, fascia, wheels.
- **Its cab.** The cab is the truck's cab run through `plan.shifted` 14 cm
  lower and in its own colours. `shifted` gains `dz` (centre-first and path
  parts only; the default 0 leaves every other builder unchanged).
- **The spread.** It moved into the Altima; the truck keeps Finn's duffel
  (vol7).
- **Preset and routing.** New preset `vehicle_cab_altima`; ch16 routes to
  it. Its inserts (cup, flautas, packet, phone) and closeups (BT, Diego)
  are `__vehicle_cab_altima` markers, with the closeups outside the
  fenders the way the truck's are. The truck's El Rancho inserts are
  retired.
- **The rig.** The Altima's dome, phone and radio practicals are
  per-preset.

Draft 4 targets:
- the Civic (ch19/ch20) still renders in the pickup;
- the sedan's raked glass;
- Finn's truck (vol7) is not Ben's green one;
- the night rig;
- ch4's rain.

**2026-10-09 · overnight run, pass 20: THE SCHOOL FIELD, DRAFT 5 (the home
stands are behind the home bench).** In vol6 ch22 Eileen sits "Third row,
behind the home bench". Drafts 1-4 of `school_field_evening` had the only
stands on the west sideline and the home bench (the stopwatch, the helmet
rack, the coolers) on the east, so her chair stood across the field in
what are the visitors' seats.
- **The home stands, now east.** Open aluminium rows (seat plank,
  footboard, posts every 3 m, tie beams, the back guard rail, the aisle
  handrail, the concrete walk) replace the solid stepped block. The
  underside was a draft-5 target. The PRESS BOX sits on top with its
  stair.
- **The visitors.** A five-row visitors' stand west, with Vinton fans.
- **The floodlights.** The poles stand behind both stands, and the scene
  floods and lamp practicals moved with them.
- **Eileen's chair.** Third row, on the footboard behind the home bench.
- **Coach K's truck.** It is now ch13's "white Ford F-250 with the camper
  shell and the ladder rack and the tape job on the driver's-side mirror",
  not a bare red pickup. `insert truck` had framed Coach Dale's truck by
  the shed (both were "truck"). The parts are renamed `CoachK_Truck_*` /
  `Dale_Pickup_*`, and the marker is re-aimed.
- **Re-aimed markers.** `insert bleachers` and `insert folding_chair`.

Draft 6 targets:
- the synthetic track (ch19: "the back stretch of the synthetic track").
  A real one rings the field, so the lot, the gate and the field house
  move south and the stands outward;
- figures with a pose;
- the scoreboard's digits;
- lot lamps at dusk.

**2026-10-09 · overnight run, pass 19: THE IRON CROW, DRAFT 6 (build big +
the chalk table was never a pool table).** `new_orleans_bar` (Strength,
Judgement, and vol1's "A Hip Bar") had grown to a 9 x 6 m box holding a
bar, a pool table, Douglas's booth, a round six-top, a pinball machine and
an arcade cabinet. The pool table was built straight through the booth
table, and the S wall had a 3.6 m hole where the street door should be.
The draft-2 hero pass had also misread vol1's CHALK TABLE as the pool
table, but the crowd SITS at it: "Helen pushes Margaret into the seat next
to Faust ... Emily puts her purse next to Faust ... Cozy corner". It is a
chalkboard-topped bench table, and Faust is "already drawing up some wacky
shit" on it. Rebuilt at 13 x 9 m under a 3.9 m pressed-tin ceiling:
- **The street front.** Two big windows, and a glazed door with its
  transom, push bar and mat. An OPEN neon hangs in the window.
- **The bar.** The long panelled bar has its bullnose, a brass rail on
  standoffs and seven stools. Behind it is a 1.0 m bartender's lane, the
  underbar (ice well, speed rail), the back bar with its doors, bottles
  and register, and a lit beer cooler. Above sit a smoky mirror between
  pilasters, two glass shelves on brackets, and the glass rack on chains.
- **Up on the N wall.** The muted TV with the game on it, where the booth
  looks; an IRON CROW neon (a red crow and the name); the gator; the
  clock.
- **Douglas's corner booth, SW.** The cheap vinyl L (with a tear), the
  table with the empties, the saltshaker over the folded twenty, an
  ashtray, the sticky patches and the sconce. Exactly three beer neons
  sit round it.
- **The rest of the floor.** Pinball, Missile Command, the cigarette
  machine and an ATM along the W wall; the pool table mid-floor under its
  billiard lamp, the cue rack on the pier; a high-top.
- **THE CHALK TABLE, SE.** The cozy corner: the bench L and a loose bench,
  the chalkboard top with Faust's drawing (a face, a star, a rocket), the
  chalk tin, six shots, the ginger beer, Emily's purse on the bench, its
  pendant and the flyers.
- **The E wall and the back hall.** The jukebox, the dartboard with the
  oche tape. Through the E wall: kegs, the restroom door, the delivery
  door with EXIT, and a hand truck.
- **Outside.** Creole cottages across the street with shutters and
  galleries, the street lamp, two parked cars.
- **The rig.** Rebuilt as 19 omnis, each under its fixture; ambient 0.48.
- **Coverage.** Six markers. `shot_insert_chalk` is new. The Douglas
  closeup now looks out from his seat, because a wall 2 m behind him
  filled the frame.

Draft 7 targets:
- the morning variant for Judgement (bourbon, the Times-Picayune
  crossword) as a per-preset prop set;
- the underbar at insert scale;
- the pressed-tin pattern (the ceiling still reads as drop-tile);
- Deck framing.

**2026-10-09 · overnight run, pass 18: DIEGO'S ROOM IS NOT A SHRINE (the wrong
dressing).** Drafts 1-4 made `diego_bedroom` "a shrine to the pitch":
jerseys, a scarf, a Mexico flag, striker posters, trophies, cleats.
Nothing in vol6 has Diego playing anything, and ch0 says the opposite:
"A photograph of Sam ... tucked into the corner of the mirror, which is
the only decoration in the room besides a periodic table he has had since
seventh grade and a calendar he stopped updating in March." Rebuilt from
ch0/16/18/22/23 at 4.4 x 4.8 m:
- **Bed.** The twin with the sheets pushed to one side.
- **"The small desk that has been his desk since he was nine."** The
  laptop, the water glass with a finger of water, the textbook, the blue
  pen, the fourteen-line letter and its envelope on the corner, a lamp.
- **The PERIODIC TABLE**, cell by cell, over the desk, and the calendar
  stopped on March.
- **The dresser by the door.** The clock that says three eleven, and the
  mirror with SAM'S PHOTOGRAPH tucked in its corner.
- **The window's two curtains.** The blackout pair his mother installed,
  pushed aside, and the regular pair, half drawn.
- **The rest.** The ceiling fan; the green duffel with the broken
  front-pocket zipper, half-packed (shirts, the charger's cord, the
  boots); the closet; his door.
- **Coverage.** A desk-lamp practical; 10 markers (letter, envelope,
  photo, duffel, window, bed, glass, establish, the closeup pair).

Draft 6 targets:
- the hall and Graciela's room;
- the blackout curtains drawn as a scene state;
- Deck framing.

**2026-10-09 · overnight run, pass 17: THE CENTRO BREAK ROOM, DRAFT 3.** The
night crew's room (vol6 ch18/ch22) was 5.6 x 4.6 m with TWO tables in one
spot: the hero pass "squared the round table into a card table" by
building a card table over it and never retiring the round one. The dock
door sat in the break room's own wall; the prose has "BT's footsteps
cross the break-room corridor, hit the dock". Now 7.2 x 5.6 m:
- **One crew table for six.** A folding table with mismatched chairs (kit
  chairs and two plastic stackers), Marisol's thermos, Russell's
  Express-News.
- **DOUG'S CHAIR "against the back wall"**, his thermos at its feet and
  the Karamazov on the floor beside it.
- **Kitchenette.** The radio on a bracket shelf, keyed to the microwave.
- **Lockers** on the E wall, and the time clock with its card rack.
- **The doorway BT stands in**, open on the corridor, with the dock door
  at its E end (push bar, wire glass, EXIT sign).
- **Markers.** New `closeup_doug` and `closeup_bt`; the inserts re-aimed.

Draft 4 targets:
- names on the lockers;
- the dock door lit by the sodium lamp through its wire glass;
- Deck framing.

**2026-10-09 · overnight run, pass 16: COSMIC'S BACK OFFICE, ONE SET WITH THE
SHOP.** The office existed twice:
- the 4.6 x 5.2 m `cosmic_comics_back_office` set that five vol6 chapters
  play in;
- a 2.8 m glimpse built behind the shop's cut doorway.

They disagreed: different furniture, and the one-way mirror on opposite
sides of the door. From the office set's doorway there was no shop at
all, yet ch12 has "Maya, at the back-office door, watches Curtis handle
the first hour and a half from her doorway". Now:
- **One builder.** The shop builder runs the office builder's OWN
  functions inside `plan.shifted(vars(BO), 3.6, 8.0, prefix="BO_")`, so
  the office's doorway IS the shop's. A diff confirmed all 242 office
  parts landed shifted by exactly (3.6, 8.0) with nothing unprefixed. The
  glimpse is retired.
- **The office set** gets the shop's 0.95 m doorway with the leaf open on
  the E jamb, and the one-way mirror moves to the WEST of the door,
  where the shop has it.
- **The preset** loads the shop scene. The office set's 17 markers and
  its rig were carried over with a `__cosmic_comics_back_office` suffix;
  its two practicals sit on the BO_ fixtures and are lit from both
  rooms.
- **Audits.** `plan.shifted` gains `prefix=`.
  `vantage_obstruction_audit --markers` and `light_direction_audit` now
  strip a `__preset` suffix before reading a subject or a role: "back"
  in "_back_office" had made a fill light into a back light.

The old office scene is unused now; its builder stays as the office's
source.

Draft targets:
- Rick's couch in the office (the Saturday nap);
- the preset vantage off the open leaf;
- the service door's alley.

**2026-10-09 · overnight run, pass 15: THE KOWALSKI KITCHEN, DRAFT 5 (build big
+ the family room).** A 6 x 5 m room held the kitchen run, the table, the
fridge, a couch a chair-width from the table, a TV on the kitchen wall
and a stair nothing climbs. The prose has more: "Bill is at the kitchen
table with the Sentinel"; "sat with the dog, watched five minutes of the
noon news"; "He goes in through the garage"; his mother asleep behind
"the bedroom door from the hallway". Rebuilt at 10.0 x 6.4 m:
- **Kitchen (E half).** The run is laid out on the new N wall with the
  kitchen kit's own constants: the sink under the back-yard window, the
  hot sauce cabinet left of the stove. The table, pendant, fridge and E
  window moved rigidly with `plan.shifted`, checked against a part
  snapshot.
- **Family room (W half).** The room is turned so the TV stands on the S
  wall. The couch faces it with DAISY lying on her spot (`make_dog`).
  Bill's recliner with the Sentinel on its arm, the area rug, a coffee
  table with the remote, a floor lamp, a W-wall bookcase with a trophy,
  family photos.
- **S wall.** The garage door with Bill's work jacket and the boots, and
  the hall opening with the bedroom door shut.
- **Coverage.** Practicals for the floor lamp, the family-room light and
  the TV's glow. Markers re-aimed; new `shot_insert_daisy`.
- **The kit fact.** A kit function (`kitchen_kit.base_run`) builds in its
  own module, so `plan.shifted` cannot move it: lay a kit run out with
  new constants instead.

Draft 6 targets:
- the open floor between the table and the family room (an island or a
  hutch);
- the upper doors ajar;
- the dish rack's dishes;
- Deck framing.

**2026-10-09 · overnight run, pass 14: SAM'S BEDROOM IS SAM MILLER'S (the
wrong person).** Drafts 1-4 dressed `sam_bedroom` for "Sam (the kid
protagonist; into Cosmic Comics and video games) ... boyish ... his
door": a captain's bed, comic longboxes, a CRT, a console, a skateboard.
Every scene that loads the preset (vol6 ch0/1/3/4/5/6/15) belongs to
SAM MILLER, the chief's daughter, who works the Kwik Stop and drives the
Corolla. Rebuilt as her room:
- **Walls, fan and window.** "Her cornflower blue bedroom" with white
  trim. THE FAN, which "clicks on the third rotation": five blades, the
  light kit, the pull chain. The window on the cul-de-sac with drapes
  and a drawn-aside sheer.
- **Through the window, two floors down.** The front lawn and THE CRACKED
  SPRINKLER throwing its arc onto the sidewalk's grey stripe. The street,
  the houses across, and the mailboxes with the NexCorp logo
  (`make_view` kind=front, logo_mailbox).
- **Furniture.** The bed with the nightstand, lamp and dream notebook.
  The desk with the legal pad, its top sheet the WEDNESDAY LIST, and the
  corkboard over it. The dresser with her phone, the mirror and the Kwik
  Stop name tag. The closet with the red polo hanging on its door for the
  morning. A bookshelf, a laundry basket, her six-panel door.
- **Coverage.** Practicals for the bedside lamp, the desk lamp and the
  fan's light. 12 markers: window, sprinklers, phone, notebook, list,
  legal pad, door, fan, establish b/c, the closeup pair.

Draft 6 targets:
- her parents' room down the hall (ch3's "insert door");
- the fan's blades turning;
- the wet sidewalk at 6:12;
- Deck framing.

**2026-10-09 · overnight run, pass 13: MAYA'S UPSTAIRS (the room across the
hall).** vol6 ch2 stages half of Maya's night in her grandmother's
bedroom. "She crosses the hall. She opens her grandmother's bedroom
door"; then [shot:closeup grandmother], [shot:insert hands], and "Why is
there a radio in your room on 1776 kHz." The set was Maya's room only, so
the closeup fell back to a substitute and the hands insert framed a
stand-in crease on MAYA's duvet. `build_upstairs_2026_10` adds:
- **The hall.** A runner and the hall light; her grandfather's
  black-and-white photographs ("Your grandfather was a photographer");
  the stair going down at the E end.
- **Linda's room**, through her open door. The made bed and the creases
  where they sat, now on HER blanket. The SHORTWAVE on the nightstand,
  dial lit, antenna up. The reading lamp and glasses; the dresser with
  his old camera and a framed print; the armchair and cardigan by the W
  window over the dark yard.
- **Coverage.** Practicals for the dial, the lamp and the hall, a moon at
  the window. Markers: `shot_closeup_grandmother`, a re-aimed
  `shot_insert_hands`, and `shot_insert_radio`.

The builder's docstring had Maya as "Maya Miller (Chief Miller's
daughter)". She is Maya Daigle, and Sam is the chief's daughter: the
wrong-house class again (_SET_DETAIL_PLAYBOOK 2026-10-08).

Draft 6 targets:
- Maya's own N window view at the second floor's height;
- the corkboard photos;
- Deck framing of the grandmother closeup.

**2026-10-09 · overnight run, pass 12: FINN'S APARTMENT, DRAFT 4 (build big +
the prose's kitchen).** Vol7's six Finn scenes played in a 5.0 x 5.4 m
room. The kitchen was a counter, and the bedroom partition stood across
a third of the preset. The prose's kitchen had no home: "He banked the
space heater in the corner. He put the kettle on. He stood at the kitchen
window looking down at the alley." Rebuilt at 8.4 x 7.6 m under 2.7:
- **Kitchen run (W wall).** Fridge, stove with the kettle, the sink under
  THE KITCHEN WINDOW, upper cupboards and a curtain. Two floors down
  across the alley is the bakery's back wall, its door and the
  back-kitchen light (lit), so Finn's window looks at the same light
  Marina stands under in ch15.
- **The table.** The cloth with five charred-wood pieces laid in a shape,
  the hexagon, the stick in its sleeve, the plate Kai made him eat from,
  the paper bag, three chairs.
- **Around the kitchen.** The lit space heater in one corner and the
  nine-month duffel in the other. The desk holds the lamp, phone,
  notebook and carved cedar. A low bookcase; the entry door from the
  stairs with its chain, a canvas coat and boots; the S window's sill
  with the crow's marks.
- **Bedroom (through a real cased doorway).** The raised bed on turned
  posts over slatted crates, the nightstand with the reader and headset,
  and THE CHAIR BESIDE THE BED with the crow on its back. A clothes rail,
  a bench with the folded thermal and jeans, floor books, a dresser with
  the change bowl and keys, and the N window over the neighbour's roof.
- **Markers.** 18, re-authored for every cue the six chapters fire.

Draft 5 targets:
- a bathroom door;
- the dish rack;
- the crates' contents;
- rain under the bakery light;
- Deck framing.

**2026-10-09 · overnight run, pass 11: THE MISSING LINK, DRAFT 4 (one building,
built big, BIGFOOT).** CANON (user, 2026-10-09): **the Missing Link diner
is Bigfoot-themed.** The creature "halfway between a man and an ape" on
the enamel sign is a Sasquatch.

Draft 3's own first target was to reconcile the two builders: the
interior's door was centred, the exterior's at the east end, and the
exterior body was 8 m to the interior's 7. They are one building now:
- **Plan.** The interior is 10 x 7 m. The exterior body runs
  x -6.5..3.5 and 10 m deep, with the kitchen behind. The door is at the
  east end, and interior = exterior + (1.5, -8.0); the interior's
  outside props are placed from the exterior's coordinates.
- **Booths.** Four front booths sit under four windows, which are the
  exterior's four.
- **The corner booth** (vol1 hub; vol7's "back booth") is in the NW,
  under the wall of square photographs, with the polaroid taped among
  them.
- **Counter.** It has five stools; the third points at the kitchen door
  (vol1_link_counter). The laminated menu stands at the third stool, and
  the second mug, a foot to the left, is empty. The back-bar runs either
  side of the door: coffee and register on one side, pie case and shake
  mixer on the other.
- **Jukebox** on the E wall by the door.
- **Bigfoot.** `_props/creatures.make_bigfoot` (shaggy or chainsaw-carved
  cedar) gives:
  - a life-size Sasquatch on the W wall under a SASQUATCH CROSSING sign;
  - plaster footprint casts in a shadow box;
  - the silhouette over the kitchen door;
  - the menu-board logo;
  - a research-fund tip jar;
  - the carved greeter by the door outside, seen from the lot, the
    bench and the booths;
  - the figure on both faces of the pole sign.
- **Surfaces.** Knotty-pine wainscot and a chrome rail; a checker aisle.
- **Coverage.** New inserts: the photo wall, the menu, the window, the
  door, the Sasquatch.

`furniture_grammar` now treats a creature's own overlapping blobs as
anatomy, not a clip.

Draft 5 targets:
- the kitchen glimpse;
- rain on the glass;
- the seven photographs as their subjects;
- the young man at the bench;
- Deck framing.

**2026-10-09 · overnight run, pass 10: HANS'S BAKERY, DRAFT 5 (build big +
the fill).** Vol7's table (8 scenes) had a 13-seat communal table in a
6 x 5 m back kitchen, alongside a deck oven, a proofer, a counter, a prep
table and two racks. Every aisle was a chair-width wide, and the preset's
right third was a grey slab: the cooling rack's solid "frame", which
swallowed its shelves and loaves (the speed rack's frame did the same).
- **9 x 7.6 m under 3.0.** The builder's mixed functions were split by
  area, and each area moved rigidly with `plan.shifted`. A part-by-part
  snapshot diff confirmed that every part moved by its group's shift and
  nothing else changed. The bake line sits on the N wall, the table
  mid-room, the Hemlock-window corner and prep bench on the W wall, and
  the racks on the E wall as open post frames on casters. The S wall
  (door, pass, Per's bench) stayed put.
- **The fill.** The bigger room first read as an empty hall. It now has
  a maple baker's bench in the E aisle (dough mass, rounds, bannetons, a
  scraper, tubs on the shelf), a timber wainscot on the W and S walls,
  aprons on hooks, a hand sink by the door, and a plaster ceiling on four
  beams. Two warm pendants hang over the table (with practicals), and
  the tubes are kept over the bake line only.
- **Light.** The walls were (0.96, 0.84, 0.62) under a 0.95 ambient and
  a 1.1 shadowless key, so every frame was flat yellow. Now: aged-plaster
  walls, ambient 0.58, key 0.62, and the pendants carry the table.

Draft 6 targets:
- the proofer as real glass;
- lathed scored loaves;
- the flour haze;
- Greta's drawer half-open;
- a bread shelf for the front in the E aisle's S end;
- Deck framing.

**2026-10-09 · overnight run, pass 9: THE PIT STOP KITCHEN, DRAFT 2 (build
big).** Ben's side of the pass-through (vol6 ch2/ch4/ch6) was a 3 m galley
holding a grill, a fryer and one prep table, washed out under the dining
room's white key. Its grill insert framed the backsplash. The building now
runs 2 m further north, so the kitchen is 11 x 4.8 m:
- **Cook line (N wall).** Range with a stockpot; flat-top on a chef base
  with the patties, buns, press and spatula; two-well fryer; lowboy with
  the cut veg and the ticket printer. One hood covers it all, with
  filters, lights and the ticket rail on its lip, and the mat runs in
  front.
- **Ben's window and the back lot.** A hand sink sits under the window.
  Out back there is a lot with the dumpster enclosure ("Dumpster at
  two-fifteen"); the window insert frames it.
- **Island and pass.** The plating island holds Ben's phone. The pass
  counter carries an order up under a heat lamp.
- **W end.** The walk-in has its condenser and temperature log. Dry
  storage holds flour sacks and #10 cans, and there is a speed rack.
- **E wall.** The dish pit: three-compartment sink, pre-rinse sprayer,
  rack shelf, bus tub, floor drain.
- **N wall, E end.** Paper-goods shelving.
- **Surfaces and safety.** A K-class extinguisher, a quarry-tile floor,
  and sage FRP to 2 m.

Lighting and coverage:
- Hood-light, pass heat lamp and three tube practicals.
- The `pit_stop_kitchen` preset has a fluorescent `env`.
- New markers: the kitchen's own closeup pair (`__pit_stop_kitchen`: Ben
  at the flat-top, Jesse at the swing door).
- Re-aimed: the grill insert (now looks down at the flat-top), the
  window, the phone, the walk-in and the line wide.
- The Louisiana pickup is black now, as the prose says.

Draft 3 targets:
- steam and smoke over the flat-top;
- grease on the filters;
- the back door to the dumpster;
- the FOH's own pass (the dining room still has draft-1 booths);
- Deck framing.

**2026-10-09 · overnight run, pass 8: FAUST'S STUDIO, DRAFT 3 (build big +
the prose's rooms).** Vol1's most-played interior was a 6 x 5 m box at
2.7 m. It had no bathroom, the mirror cabinet hung over the kitchen sink,
the books sat deep inside a dark case, and one night sky served the
painting morning too. Rebuilt from the prose as an 8 x 6.6 m walk-up
studio under 2.95 m:
- **Bathroom (SE).** Its own walls, the door open on the lit vanity. The
  mirror cabinet is open on the vitamins. Toilet, a tub behind a
  half-drawn curtain, a towel rail. These cover "opens the mirror to get
  his vitamins" and "To the bathroom. Pukes in the toilet."
- **Entry.** The door is chained shut. The hooks carry the blue scrubs
  and the white coat, with shoes and a work bag under them. The bicycle
  leans on the bathroom wall.
- **Kitchenette (W wall).** Fridge, counter, hot plate, sink, cupboards,
  a cafe table with the mail and a pill organizer.
- **Bookcase and reading corner.** A four-bay bookcase CARCASS with books
  at the front edge (some stacks lying flat, rolled canvases), the
  reading chair and its floor lamp.
- **Bed corner.** The bed under his biggest canvas. The nightstand holds
  the alarm, the water glass and the journal. The dresser carries
  drug-rep sample boxes. The clock is stopped at 4:00.
- **Painting corner (E window).** Easel on a drop cloth with the
  elemental canvas, the paint table with palette and brush jar, a stool.
  Canvases are leaned on the wall and laid on the floor. A radiator sits
  under the window, and a desk under a second, N window.
- **Views.** A street view out of the E window, a back view out of the N.

Lighting and coverage:
- `faust_apartment_day` carries a morning `env` (the new per-preset
  environment) and its own sun and skylight. `faust_bedroom` keeps the
  night rig: lamp, moon, sodium street lamp. See _LIGHTING_PLAYBOOK
  2026-10-09.
- 11 markers. The bed has its own closeup pair
  (`__faust_bedroom`: Faust at the headboard, the woman at the foot).
  The mirror insert is inside the bathroom. New inserts: the alarm, the
  coat, establish_b.

Draft 4 targets:
- the hall beyond the entry door (an ajar variant for the morning exit);
- a toilet insert for the waking's last line;
- readable book titles;
- dust and a paint-crusted floor at the easel;
- the day wide's right third is the bathroom wall: re-stage that
  vantage on the Deck.

**2026-10-09 · overnight run, pass 7: CHILLWAVE'S SHELVES + THE SWALLOWED
CONTENTS.** ChillWave (Cale's secondhand stick shop, vol 7 ch3/6) read as
a counter in an empty room. Its cedar wall units' "frames" were SOLID
blocks that swallowed the shelves and every stick, so each wall unit was a
dark slab, and the floor's middle was empty.
- The units are carcasses now (back panel on the wall, sides, top), the
  shelves pulled off the wall; the back room's inventory units likewise.
- A double-sided cedar island of sticks with a new-arrivals card fills
  the front floor.
A scan for visible contents swallowed by a solid body found the same
class elsewhere, now opened up:
- Lena's bookshelf: 24 books inside a solid box. It is a carcass with
  four boards and books of unequal height, one lying flat (its draft-5
  target);
- the Miller office's low shelf (binders);
- the bungalow's bookshelf (the tarot decks, books, the cookie box);
- the Lacombe vending machine: a solid lower half under a glazed
  chamber with spiral shelves;
- Aurelie's notebook lay UNDER the Frog register.
(Card-terminal keys sit flush in their bodies by design.)
The bungalow's walls were solid slabs with the window frames floating
in front of them, so no window opened. `_wall_cut` now builds each
windowed wall (S-W, S-E, N-E, E, W) as piers, a sill and a header
around a real opening, the same way the cabin and Lena's flat do.
Draft N+1: glimpses of the outside through those cuts (the side yard
and the next lot's fence), and the Cosmic back office set unified with
the shop's office glimpse.

**2026-10-09 · overnight run, pass 6: THE BURIED-DECOR SWEEP (new gate).**
Diego's room read bare because its things were INSIDE ITS WALLS: the
jerseys and scarf 4 cm inside the north wall (and across its window),
the flag inside the west wall. A sweep of all 122 builders found the same
error everywhere: decor placed from a wall's CENTRE line (`ROOM_W/2 -
0.06` on a 20 cm wall whose face is at ROOM_W/2 - 0.10).
- Jesse's acoustic foam and lyric sheets; Maya's corkboard, pins and
  fairy lights; the Miller office's plat map and commendations;
  Lena's thermostat and her bed's head (8 cm into the N wall);
- Board Lords' parts pegboard; the Roberts calendar; Faust's and the
  school newspaper's clocks; the pinboard;
- Daigle's neon backings and corkboard; El Rancho's menu board and neon;
  the ice company's services board; the Houston moodboard;
- the Henderson, Frog, Pit Stop office, Miller and Lacombe pegboards;
- the gym's mirror, the Mixing Glass back-bar mirror, Cafe Olimpico's
  pennants, the Foxhole dressing room's set list, Cosmic's one-way
  mirrors and a poster behind its manga wall, the bungalow's foam and
  bathroom mirror, the Ember & Ash crew photo, Wagner's poster, the
  restroom signs, the riverboat calendar.
All are on their wall faces now. Diego's room also re-hangs its jerseys on the
east wall and its posters as sports posters, and is toned down from
washed-out.
- **Doors** inside solid walls are proud of the room face: the Kwik
  Stop restroom, Cosmic's service door, the Daily Grind's back door,
  Kai's bathroom door, the Millers' porch door, the courthouse side
  door, the riverboat's side door and leaded window.
- **The gate:** `buried_decor_audit.py` (in the suite, ceiling 0) fails
  any wall decor fully inside a wall.
STILL OPEN (a different fix, cut openings): the diner's saloon and
pilot-house windows and the bungalow's six windows sit inside SOLID walls
(neither inside nor outside sees them); the riverboat's gangway door;
the pharmacy's door glass sits in a wall pier.

**2026-10-09 · overnight run, pass 5: THE ALLEY BEHIND THE SALTY TOME, A
PLACE.** Vol 7's climax (ch14/16/18/20/21: the painting, the hour at the
wall, the face opening its eyes before thirty-five people) played in a
strip of asphalt between a 3.6 m mural wall and the store's 2.8 m back
wall, with sky over both and nothing past either end.
- the mural wall is a three-storey brick building with windows and a
  cornice;
- the store side has its upper storey (one window lit behind curtains)
  and building corners to the entrance and the laundromat;
- the laundromat is a building closing the far end, blind as the prose
  says (a downspout, no door, no fire escape);
- Petra's back-door light, with its practical;
- rain pools and a drain;
- the takeaway cup on the crate and its `insert coffee __alley` marker
  (four cues cut to the kitchenette's mug before);
- the street across the entrance;
- two establishing alternates: from the entrance down the alley, and
  from the far end back to the street.
Next: the crowd states (ch20/21's thirty-five people); the face itself
is a box stack (a painted figure at a draft's resolution); and THE
COSMIC BACK OFFICE should be ONE set with the shop. The shop's doorway
glimpse (2026-10-09) and `cosmic_comics_back_office` are two different
rooms.

**2026-10-09 · overnight run, pass 4: LENA'S APARTMENT, 7 x 6.6 (draft 5).**
Vol 7's second set (23 placements) was 5 x 5 m. 25 m2 held a kitchen, a
table for four, a couch nook, a window chair, an easel and a bedroom.
The table was jammed against the counter, the fridge stood in front of
the front window, and THE BEDROOM WAS OPEN TO THE COUCH: no wall stood
between them behind the partition, though "the bedroom closes behind its
own door". The slippers "at the foot of the bed" stood outside the
partition.
- **The method:** the bigger-room technique, now shared as
  `_props/plan.py shifted()`, with the audit recorder executing it for
  real.
  - Groups: kitchen and easel (-1, 0); table (-0.3, +0.3); window chair
    (+0.25, +0.3); fridge and radiator (+1, 0) into the SE corner, out
    of the window; bedroom (-1, +1.6) behind the partition, which moves
    to y 3.6 and is closed by a new east wall; couch nook (+0.3, +0.95);
    bookshelf on the E wall.
  - The paths, cords and outlets were re-drawn by hand. The diff
    against the snapshot checks every group.
- **The markers:** 18 moved with their subjects; `establish_b` (now from
  the nook across the main room), the nightstand and the charcoal
  inserts were re-authored inside their rooms; `closeup_person` frames
  the kitchen window and the mural.
Draft 6: the old draft 5's list (real bookshelf shelves, the counter's
doors, the radiator, the blind) plus the bedroom's empty east half and
the main room's new floor.

**2026-10-09 · overnight run, pass 3: THE FOXHOLE IS ONE VENUE (foxhole_bar
draft 1 of the rebuild).** The prose plays one big room: "a hundred and
ten people", the stage at the front with six LED fixtures on two truss
towers at its lip, the DJ booth at its side, "Walk to the back. Stand
against the back wall", "the bar in the back", "a high-top to the left
of the stage", the rail, backstage, the set list taped to the floor. It
was two template rooms: `foxhole_bar`, an 8 x 6 m bar with a stage
crammed on its west wall, and `foxhole_stage`, an auto-generated
8 x 5 m shell.
- **The venue** (`build_foxhole_bar.py`, rewritten) is a 12 x 16 m black
  box under a 4.6 m ceiling:
  - the stage across the north end (deck, skirt, backdrop pleats, drum
    riser and kit, two amps, three mics with their cords, wedges, the
    lyrics flyer and the taped set list);
  - the truss towers with their fixtures, the lighting pipe with six
    cans, the PA on the floor off the stage's corners, the rail;
  - Chess's DJ booth at the stage's east side;
  - the FOH desk on its platform with Ricky's cooler and the snake taped
    to the floor;
  - high-tops down the west wall;
  - the bar across the back's west half (back bar, mirror, three shelves
    of bottles, neon, taps, stools) with a 1.1 m bartender's lane;
  - the entrance doors, the restrooms, the backstage door off the
    stage's wing, the work light in the back corner.
- **Lights:** practicals on the fixtures (neon, the mirror glow, four
  tower fixtures, two cans, the work light, Chess's laptop) and a stage
  wash.
- **Presets:** `foxhole_stage` now points at the same set (the
  cabin-porch pattern) with its own `__foxhole_stage` markers.
  foxhole_stage.tscn and its builder are retired.
Draft 2:
- the gig-night crowd (ch22's 110 people are an empty floor);
- the bar's tap handles told apart;
- flyers layered by date;
- the stage too dark under `night` from the back.

**2026-10-09 · overnight run, pass 2: BOARD LORDS draft 4.** The retail
floor was empty linoleum between the deck wall and the counter.
From vol 7 ch 2/5/9/10/12/16:
- the floor RACK of complete boards ("The board was in the rack. The
  rack was full. The board was on the bottom.") with trucks and wheels,
  the cracked 2034 Tess Mariana at the bottom;
- the NEW DECKS on the wall behind the counter, with Lena's Tide Pool
  Geometries run among them;
- a hoodie rounder on its hangers;
- Devon's chipped Tidewater mug and the wooden token box under the
  counter;
- griptape on the repair bench;
- the bell as a turned bell on a coiled spring;
- across Main, the drone at the laundromat's new downspout;
- the pale puddle discs darkened.
Next: the drop ceiling's grid reads office, not skate shop (an exposed
ceiling or a painted one); stickers on the counter front; the
shoe-and-apparel wall.

**2026-10-09 · overnight run, pass 1: cabin interior draft 9 + COSMIC COMICS draft 5.**
- **Cabin:**
  - the daybed blanket drapes over the room-side edge;
  - the loft has a soft mattress and blanket, a pillow, Marina's
    sweater and the flashlight she came down with;
  - a shelf on the N wall by the stove (tins, two jars of beans, the box
    grinder);
  - coat pegs on the east room's new wall with Tem's wool coat, a cap,
    the rain jacket, and a boot tray under them. The main room's corner
    by the east room's door was bare plaster.
- **Cosmic Comics, from vol 6 ch 1/2/4/12/21:**
  - THE BACK OFFICE WAS A DARK BOX on a solid wall behind a solid
    frame board. The doorway is cut, with a frame ring and the leaf open.
    Through it: the file cabinet with "the shelf above the file cabinet"
    (paperbacks, a pen can, the dust ghost where the Speak & Spell sat),
    the desk with its lamp lit (a practical: "The light is on"), and
    Rick's loveseat for the Saturday nap;
  - the staff side: the stool and its floor ring stood on the CUSTOMER
    side and are behind the counter now; the employee cubby with Wren's
    bag; Rick's small shelf with the Sentinel and a mug; Curtis's thermos
    under the register;
  - the bins have lips and the Tuesday shelf-talkers;
  - THE STOREFRONT'S SECOND WINDOW: the east half of the front was solid
    plaster. It is a display window now (graphic novels on stands, the
    PULL LIST card), and `closeup_person_b`, which framed a bare purple
    corner, frames the window and the street.
Next for Cosmic: the bins' comics at a lean; the key wall's bags with a
rim; the statues posed; the drop ceiling's grid is heavy in every wide.

**2026-10-09 · TEM'S CABIN, interior draft 8.**
- **The counter** was a flat yellow box under lamplight. It now has a
  darker body, three plank doors with their seams and knobs, a drawer
  over each, the toe-kick, and the drip line on the door fronts.
- **The seven chairs** read as gathered over forty years, not a set: one
  carries a wool cushion, one is newer and pale, and one is the odd
  green-painted kitchen chair.
- **The loft's balusters** are turned.
- **A braided oval runner** lies inside the door, in the floor's widened
  middle.
- **THE EAST ROOM IS A ROOM.** It was an alcove open to the main room.
  The partition now runs to a north wall with a door by the partition,
  its plank leaf standing open into the room.
- **The basin's mirror** stood INSIDE the partition, never seen. It now
  hangs on the south wall over the basin.
- **`establish_b`** had moved with the kitchen into the jar row under
  the pot rack. It now stands off the counter, looking across the room to
  the door.
Draft 9 targets:
- the daybed's blanket draped over the edge;
- the crow's sill and the Sitkas seen from inside;
- the loft's mattress and blanket, which are still boxes;
- a shelf of jars and tins on the N wall by the stove;
- the main room's south-east corner by the east room's door is bare;
- Deck framing of the vol 7 rotation (establish b and c) in the bigger
  room.

**2026-10-09 · TEM'S CABIN, 8 x 8 (cabin_interior, interior draft 7).**
The room was 6 x 6 m for what the prose puts in it: a table that seats
seven, the daybed, two armchairs at the stove, a kitchen under a loft and
an east room. CLAUDE.md rule 5 says enlarge the room before shaving the
furniture, so it is now 8 x 8.
- **How:** the hundreds of hand-placed coordinates were not retyped. Each
  furniture group moves RIGIDLY to its corner of the new plan through
  `_shift(dx, dy)`, a context manager that wraps the builder's geometry
  names (and the creature and floor-wear helpers) and hands the group the
  OLD wall constants, so its wall-hugging pieces land on the new walls.
  - kitchen, loft and the crow's window: (-1, +2)
  - stove corner: (+1, +2)
  - the table and everything on it: (0, +1)
  - daybed: (-1, +0.6)
  - east room: the bed wall +1, the desk wall +0.25, the partition from
    1.0 to 1.4, so the east room is 2.4 m wide
  - the door, the basin, the kerosene can and the west south window stay
  - Olaf's and Tem's floor-wear paths are re-drawn by hand.
- **Verification:** every recorded part was diffed against a pre-change
  snapshot; each moved by exactly its group's shift.
- **The scenes:** the 33 interior markers and three practicals moved with
  their subjects' groups, so every framing is preserved. The wagon insert
  now looks out of the east room's south window. The bed preset's camera
  moved with the bed.
- **The outside follows:** the roof pitch drops to 0.80 (ridge ~6.8 m),
  Olaf's shop moves west with the wall, the yard's north edge moves out
  2 m, the truck parks in front of the shop, and the stovepipe follows the
  stove.

**2026-10-08 · TEM'S PORCH IS NOT THE MILLERS' PORCH (cabin_porch, draft
1).** Twelve vol 7 scenes are set on the porch of Tem's off-grid Oregon
cabin ("Tem was on the porch with a coffee in her hand", the cedar with
Eddvard's hand on the rail, "the small tin Tem kept on the porch for the
people who smoked", the crow on the railing, "the small gravel turnaround
in front of the cabin's porch"). All twelve were shot on
`miller_back_porch`, the Millers' TEXAS back porch: a different house in a
different state. The cabin had no outside at all: a box of walls with a
flat lid, standing on nothing, and the two vehicles parked against its
front wall.
- **The cabin got a building's outside** (`build_exterior_2026_10`):
  - a gable roof, the gable ends filled, a vent under the ridge;
  - a stone foundation, so the floor stands 0.40 m over the yard;
  - siding lines broken at the openings;
  - the stovepipe out of the north wall and up past the eave;
  - the yard, with Sitkas round the clearing and a dark forest band past them where the set ends.
- **The porch** (`build_porch_2026_10`):
  - deck, step, four posts and a shed roof on a ledger;
  - railings with a wide cap carrying her mug, the cedar hand (palm-up, fingers curled) and the smokers' tin with a butt in it, plus the crow on the west rail;
  - the bench under the west window with a blanket, one chair, boots by the door, firewood under the east window;
  - the rain barrel at the corner and the chopping block in the yard. No porch lamp: there are no wires.
- **The turnaround** moved south of the porch. Finn's truck and the station wagon are now kit cars parked nose-in, where before they were four boxes each.
- **A 0.40 m slot over the front door** showed the interior thermometer; the door head is closed.
- **The `cabin_porch` preset** shoots from the turnaround. It has ten `__cabin_porch` markers, so the plain interior establish_b/c and closeups never cut a porch scene back inside. `insert bowls` (ch15: "the bowls were on the table") deliberately keeps the interior marker.
- **Wiring:** the twelve chapters point at `3d:cabin_porch`. Vol 6's three Miller-porch uses stay on the Millers' porch, whose ambient bed is now the vol 6 one (it was the cabin woodstove).

SAME DAY, the user: "The cabin looks too small on the outside." It did.
A 6 m front under a 0.6 pitch read as a garden shed, for a house that
seats seven, keeps a sleeping loft and an east room. Two changes:
- The roof is now at a loft's pitch (0.95, ridge ~6.4 m).
- The cabin grew OLAF'S SHOP, a 4 x 5.7 m west wing under its own lower
  gable, set back from the porch wall. Its window shows the carving bench
  with a cedar blank and the gouges. The cabin's west wall has no
  openings, so the room inside is unchanged. The north wall's 10 cm stub
  past the west face is trimmed flush to meet it.
The preset now frames the whole front. Finn's truck parks in front of the
shop on a second lobe of gravel. The interior's `insert truck` stood
outside the west wall, where the shop now is; it is now inside, at the
west south window ("seen from the west south window").
The interior is still the 6 x 6 m room the prose overfills: a table for
seven, a daybed, two armchairs, a stove corner, a kitchen and an east
room. Enlarging it (CLAUDE.md rule 5) is the cabin's next interior draft.
THEN, the user: "Why are the vehicles on a big block that sits above the
bottom of the cabin." They were at foundation level, and the frame made
them look raised:
- The gravel was a pale flat polygon with an inked edge, so it read as a
  plinth.
- The yard was one flat plane out to the forest band, so its far edge met
  the dark band at eye level, like the top of a block with the cabin sunk
  into it.
The fix: the gravel is now a tone off the dirt, and the clearing's edge
RISES 1.8 m into the trees on a ring of berm heightfields, outside
everything that stands in the clearing. The bands stand on the crest.
Lesson: a flat ground plane that ends at a wall reads as a block. Run the
ground UP to the set's edge.
DRAFT 4 (same day):
- The porch has its OWN light: a low east-southeast morning sun with
  shadows plus a cool sky fill, named `__cabin_porch` so Background3D
  drops them for the room's presets. They carry `metadata/daylight`, so
  MoodCycler turns the sun down at dusk and off under night and
  candlelight_low. The night porch is lit by the windows, as the prose
  has it.
- The crowns are greener.
- Sword fern and salal line the berms' foot.
- The front door is board-and-batten. As a flat slab the paint pass
  blotched it into a giant disc.
DRAFT 5 (same day):
- Night window light: two warm spots just inside the south windows,
  aimed down through the glass onto the boards. They are porch-only
  (`__cabin_porch`) and NOT daylight-tagged, since the lamps burn all day.
- The road out: a gravel track with two wheel tracks leaves the
  turnaround south into the trees, through a cut in the bank. The south
  berm is split around it, and a tree and the fern line moved off its
  line.
- Olaf's shop has a board-and-batten door in its south wall, a stone step
  and eight stepping stones round to the porch steps.
- The Sitka crowns are four drooping tiers in two greens. A first try
  flared each tier from a ring and read as stacked bells; a skirt's
  underside RISES to the trunk.
- `insert door` is reframed wider (fov 55): the door, the bench and the
  boots.
PORCH DRAFT 6:
- The night spill is soft on the boards. Give it a crisper square:
  spot_angle_attenuation, or a lit decal on the deck.
- Moss on the roofs.
- Siding as boards with a shadow line.
- Window boxes or a drying line on the porch (lived-in).
- The road's far end into the band (a few trunks in front of it).
- Walk the twelve chapters' framing on the Deck.
Earlier list, superseded:
- the gravel road out of the clearing;
- tiered two-tone crowns (the lit cones still read khaki);
- the window's square of yellow on the boards at night;
- moss on the roof;
- siding as boards;
- the shop's door and its path;
- `insert door` reframed wider (fov 45 frames only the door's middle).
Earlier list, kept:
- an exterior light for the preset (the outside is lit by the interior's rig and reads dusky under morning_bright);
- the gravel road out of the clearing;
- tiered two-tone crowns;
- the window's square of yellow on the boards at night;
- moss on the roof;
- siding as boards with a shadow line.

(DONE 2026-10-07 as miller_kitchen draft 9 — see that builder; this note was stale.) Bianca's kitchen is the Miller kitchen again —
`bianca_kitchen_morning` (ch 22 / 23) and `miller_kitchen` are one room
on Meadowlark Circle (the cul-de-sac through the window, the green robe
on the hook by the back door, Mike's chair at the short side by the
window). `_props/kitchen_kit.py` (shaker base and upper runs, subway
tile, a stainless sink, slide-in range, French-door fridge, dishwasher)
is written for it: rebuild the Miller room on the kit with the sink
window CUT (the prose's front-yard view has no window today) and the
east window and back door cut, keep its eight story passes, and build
Bianca's locale from it with her dressing.

**2026-10-06 · THE DOCK AT PRE-DAWN + GRACIELA'S KITCHEN, ONCE + THE GAS & GO STOCKED + THE BACK LOT (vol 6
contact sheet, its two weakest frames).** CENTRO_DOCK rendered black:
the dawn bands stood 520 m out where the 0.004 fog left 12 % of them,
lit only by ambient. The stockroom's environment is a pre-dawn
ProceduralSky now (navy overhead, a warm horizon to story-east;
`sky_curve` 0.35 so the warmth climbs off the ground line; both
directional lights `sky_mode` light-only so no sun discs), the fog is
the horizon's own tone and thinner (aerial perspective, not mud), the
far treeline bands are cedar-scrub height (4-7 m, were 8-17 m: a wall
over the dawn) and the THERMAL SMEAR is seven thin ragged rust veils —
a sky card 55 m out scaled to the far horizon's angle (an insert's
subject must be inside marker_aim's 40 m). GRACIELA'S KITCHEN was TWO
template locales of one canonical room (`ramos_kitchen_morning` ch 1 /
10, `grandmother_kitchen_morning` ch 16 / 18 / 22 / 23) — a store-kit
counter, a centre table and a grey box each. One room now,
`_props/ramos_kitchen.py`, dressed per locale: "the small round table
under the window" with the radio, the salt box, a veladora and an aloe
on the sill and the side drive outside (his truck in it, or only its
oil stain — "the truck is the bait"); the counter run with canisters,
the molcajete, the limes, the double sink under an open shelf of mugs,
the dish rack, the white enamel range with THE CLOCK ABOVE THE STOVE
(8:15 / 4:38), the fridge papered in forty years; Talavera accents;
the china hutch, the back door standing open on its screen door and
the patio (lemon tree, clothesline, cedar fence, live oak); the hall
with the front door, the console lamp, the foot of the stair; the
Guadalupe with its palm cross, his school pictures climbing the wall,
the Sacred Heart, the baker's rack; Saltillo tile, a serape runner, a
ceiling fan, the pendant over the table. Dressings: the yellow plate
with the chip, her Sentinel, the fruit, the second letter, the caldo,
the comal, the onion and the bay leaf (eggs) · the rosary, the black
coffee, the cordless phone charging, the soup, the chorizo eggs in the
skillet (rosary). Both envs carry a morning ProceduralSky with
`fog_sky_affect = 0` (the fog had tinted the sky through the window
brown). Five practicals at real fixtures (pendant, fan kit, hood lamp,
hall lamp, a window sky fill). Every marker re-authored; the unused
pie insert dropped. AUDIT: `locale_geometry_audit` runs
`_props/ramos_kitchen` for real (a shared ROOM module was invisible to
every gate — 0 objects — until it joined the real-module list). Deck
must REBUILD centro_stockroom, grandmother_kitchen_morning and
ramos_kitchen_morning. Draft 3 targets (kitchen): the half-bath door
off the hall; the cordless charge light as a practical; steam over the
pot (a mood); the clock reads faint at the preset's distance; the
ceiling fan dominates the preset's top third — try a 44" fan. Draft N+1
(dock): the dock lamp's cone on the apron; a parked trailer at the far
bay. THE GAS & GO (the sheet's "toy blocks"): every shelf product was a
solid saturated block. `build_merchandise_2026_10` stocks the aisle the
way a gas station does — chip bags with a band and a crimp up top,
candy trays of bars, jerky and nuts at the hand, motor-oil quarts and
washer-fluid jugs at the shins — with price strips and tags on every
edge, end panels, the water stacked at the counter end; the cigarette
wall is packs by brand; a roller grill by the coffee; six-packs are
carriers with can tops. The two south "windows" were panes on SOLID
walls: cut, mullioned, decaled — and outside them the lot, Gallatin's
four lanes, the median palms and, across the intersection, the Kwik
Stop's red front with Sam's Corolla in its lot (ch 2's night watch). A
day ProceduralSky (`fog_sky_affect = 0`). Skip's side of the counter:
the drop safe with the receipt rolls, his cooler and his energy drink,
the case of bags, the trash, the fatigue mat; his phone and his vape on
the counter, the lottery case, the impulse rack; the east wall's ice
merchandiser, ATM and hiring poster. The preset stood 1.5 m from the
aisle (shelving only): it now looks over Skip's shoulder at the counter,
the door and the pumps. Deck must REBUILD nexcorp_gas_go. Draft N+1: the
car-wash tunnel out back; a back-bar behind the counter (the cigarette
wall belongs there, not on the north wall); the night mood should dim
the sky (ch 2's lot scene is at night). THE STRIP MALL'S BACK LOT (ch 14 /
20 / 22, "a long blank wall"): `build_back_lot_2026_10` puts in what the
prose lists — "three dumpsters and a small parked U-Haul that has been
there for three weeks", "a chain-link fence at the back separating the
lot from a small drainage easement and a stand of cedar" (its gap at the
south end where the Civic comes in) — and the back wall's working life:
a meter and conduit at every unit, door numbers on every door but the
unit's, wall packs over the plain doors (none over the unit's, which "has
no signage"), scupper rust, corner bollards, oil stains, the Foxhole's
pallets. Deck must REBUILD new_auburn_road. Draft N+1: the dark sedan's
empty space by the far dumpster; the sodium head as a cobra head with its
practical; roof-top units on the parapet's skyline.

**2026-10-03 · WINDOWS CUT ACROSS VOL 5 (draft N+1 of the glass
pass).** Every remaining vol 5 window on a solid wall is cut with
`make_wall_with_openings`: Natalie's (W + SE; its W "frame" was a
solid plate — four bars now), the Houston office (the whole north
wall behind the glass wall — the towers show), the design studio,
the cafe (its two street windows were half over the door opening;
centred on their wall pieces now; the back-corner window cut too),
the New Orleans office (S + E), bar (SW + SE) and room (N; its
frame plate four bars). The hospice was already cut. Elicia's west
side gets a skyline plate with lit windows behind the whole wall;
Montreal's bookshelf is runs of varied books with two laid flat per
row. Elicia's skyline: a near-black plate 12 m out with 180 lit
windows (at 3 m it stood in the window practical's light and read
as a grey wall; the practical moved 50 cm off the pane); the four
free-standing towers of the first pass are gone (they stood inside
the plate); `shot_insert_skyline` added for "watching the indifferent
city lights". The cafe's front was a 4 m hole with nothing beyond
(its door insert saw "81 % sky" once the walls were cut): a glazed
front with a door pair now, and a Mile End street outside it —
sidewalk, curb, street, the facade opposite, a lamp post, a parked
car, a street tree. Deck must REBUILD: natalie_apartment, houston_office,
houston_design_studio, cafe_olimpico, new_orleans_office,
new_orleans_bar, new_orleans_room, elicia_apartment,
montreal_apartment. Draft N+1: what is OUTSIDE each cut — the
Houston towers exist, the cafe's street and the bar's street do
not (a hole onto the sky reads as daylight; the night chapters
want a street with a lamp); the diner's glass wall segment and the
bungalow's skylight are their own cases.

**2026-10-03 · THE THREE APARTMENTS — character passes (ch 14 / 15 /
16).** The Roberts standard applied to the rest of vol 5's homes, each
from its chapter's own inventory. MONTREAL (John Frank, "a cluttered
archive of selves"): four Criterion posters, eleven torn journal pages
pinned over the desk, notebook ziggurats on every surface (coffee
table, bistro table, sofa, radiator, two on the floor), the desk lamp
and pen cup and the notebook open mid-line, the kitchen drawer half
out with the private notebook in it, the bookshelf's collection (key
bowl, DVDs, pen jar, photo, plant, camera), the winter coat and boots
by the door. NEW ORLEANS (Jimmy's sublet, "a dumpster fire of a
life"): empties and a can by the sofa, the pizza box open, a shirt and
jeans on the floor, the duffel half unpacked at the bed's foot, shoes
kicked off at the door, the sticky stain, dirty plates, the pan, a
second bottle on its side, the mail, the cigarettes and lighter, the
landlord's calendar, a Saints pennant on the brick, a cracked mirror,
a votive on the TV stand. ELICIA'S (the Tower, "ruins of some
forgotten exposition"): the work table under the west window with two
dead monitors, the keyboard, the drive stacks, a dead plant and the
cable ivy off its edge; the story-map whiteboard under fourteen
post-its and the corkboard of the photographs she stopped taking; her
prints leaning unhung; the low case of binders, film cans and drive
cases; a tripod standing for the camera; ten more pages, four more
slates; Montreal's dusk through the west window (four tower blocks
with their windows lit, the harbour's red and gold afar). All three
clean on overlap, support and both marker audits. Markers re-aimed
from the renders: Montreal's mug (the NARWHAL one, on the desk) and
notebook (the one open on the desk) and the drainpipe (through the
window — which found the window was a pane on a solid wall, see
_SHADER_VISUALS 2026-10-03: `make_wall_with_openings` cuts the hole;
Montreal, Elicia's and the Roberts house are cut, the default glass
thinned); New Orleans' Jimmy (the sofa and the lace window behind
him) and the microwave (face on); Elicia's teacup (0.7 m off). Deck
must REBUILD all three AND roberts_kitchen. Draft N+1: Elicia's dusk
towers stand just outside her west window's sightline (the panes show
the environment's sky) — a wide skyline plate with lit windows behind
the whole west side; cut the windows
of the other locales (`grep -l make_window` — the diner's, the
bungalow's, the hospice's, Natalie's: every one is a pane on a wall); (this
pass was built blind from the prose while the first renders ran);
Montreal's bookshelf still has identical books (vary them with
_book_row); New Orleans wants the bruised-purple window light the
chapter names; Elicia's sofa is a plain slab.

**2026-10-03 · THE ROBERTS HOUSE — foyer · living room · dining room
(the Deck: "mackenzie home still looking wrong. sink on backwards? I
want it to feel cozy, brimming with detail … a foyer, a living room,
a dining room/kitchen, I want to have character").** Interior walls
make a foyer and a living room; the dining room gets a wainscot; each
room its furniture and its collections (_SET_DETAIL_PLAYBOOK
2026-10-03 has the inventory). The sink is a basin cut into the
counter with the faucet at the backsplash. Four practicals added for
the new fixtures; `shot_establish_b` (the living room) and
`shot_establish_dining` added; the Polaroid insert re-aimed at the
hall table's new place. Deck must REBUILD roberts_kitchen. Draft N+1:
the kitchen's west end (the loom's old corner) is bare; the radio's
sill could carry more of Philip's driftwood; the foyer's north
opening is a plain header — a transom or a glazed pair of doors would
read older; the living room's window wants the yard beyond it (a
make_backyard_view south); photos are tinted rectangles — the
HeroImage path could put real pictures in the frames.

**2026-10-02 · THE STILLS LIED — the trail rig over the paint (ch 0).**
The Deck: "still too muddy, can't make out details. neon lines
overwhelming the models … I saw stills that looked to fix this, in
action, still looks terrible. first five chapters unchanged." The
game mounts TripSync's FEEDBACK rig over every background; the test
tool never did. Over a watercolour the rig is a halo, neon edges and
a smear. Fixed in TripSync (`paint_under_3d`: the trail's gain and
edge feed × (1 − 0.85) over a painted 3D bg), the aura's inked
cross-fade reaching 1 under paint, and TripPaintTest mounting the rig
so stills are the game (_SHADER_VISUALS_PLAYBOOK 2026-10-02 (vii)).
No rebuild on the Deck: scripts and shaders only. If ch 0 STILL reads
unchanged after this pull, the next diagnostic is PSYCHEDELIA at 0 in
settings: the painting alone, no trip — it tells whether the painter
runs at all on the Deck.

**2026-10-02 · VOL 5 BACKGROUND PROGRAM · pass 2 — DIRECTION, shot by
shot, and GLASS IS GLASS.** The method now: render every `[shot:]`
marker of a locale through `TripPaintTest --marker shot_x` into one
montage, read the chapter's cue lines beside it, and re-aim each
marker from the prose as a camera point + a target point
(`aim(cam, tgt)` → pitch/yaw, see _VN_DIRECTION_PLAYBOOK 2026-10-02).
Shipped: NATALIE'S APARTMENT (ch 12/18) — six markers; `insert card`
framed a plant and a stool, `closeup natalie` a bare wall, `insert
phone` a counter the phone was INSIDE (the north counter's slab was
centred on top_z, 3 cm above the west counter's — the phone, the mug
and its ring were buried in it; builder fixed). RIVERBOAT INTERIOR
(ch 4) — `insert window` sat at 4.70, in the void between decks,
looking up at a table's underside; now Dante at the leaded pane, 3/4
from beside the chair, the pane re-coloured for Friday NIGHT (the
dining room's candle glow, not daylight) and its lead cames 3.5 cm at
25 cm standing proud of the glass (they were brass hairlines INSIDE the
pane — invisible); `closeup dante` faced a bulkhead port, now his
father's clock behind him; the bourbon closer. HOUSTON OFFICE (ch
10/11) — `insert monitor` looked at the monitor's BACK, `insert
photograph` at the chair's base, `closeup anna` at a wall; all six
re-aimed, and the ESTABLISH re-vantaged into her office (the old
vantage was the open floor from the door — the prose is "the glass
wall of her office"; now the teak desk, the two monitors, the lamp,
and the floor through the north partition's glass). HOUSTON DESIGN
STUDIO (ch 11) — `insert monitor` looked at the third monitor's back,
`insert phone` down an empty desk; both at their object. HOSPICE (ch
13) — `closeup alice` was a top-down pillow (now the bed's head and the
window from its foot), `insert rose` a speck on a bright sill
(closer), `insert chair` the chair's own back from behind (now its
seat). GLASS: the builders write every pane with an alpha below 1
and the GLB carries it, but the importer's default material is opaque
— Erica's "glass-walled office" was a box, the helm's leaded window a
wall. `scripts/LocaleGlass.gd` (preloaded by Background3D, applied to
every instanced locale) turns vertex alpha into real transparency: no
rebuild, no Blender on the Deck. NEXT (pass 3): houston_design_studio
+ hospice_room markers (rendered, judged next), then montreal /
new_orleans / elicia apartments, graustark ×4, vehicle cab, cafe,
chapel, new_orleans office/bar/room, dambrosios_formal,
riverfront_park; Houston `establish_b` still has a cubicle partition
at frame-left (nudge the camera west); the riverboat's dining room
through the leaded pane is a warm glow, not a room (light the dining
floor for the helm's view); roberts_kitchen ceiling hotspot; the
cathedral verdict.

**2026-10-02 · VOL 5 BACKGROUND PROGRAM · pass 1 (the user: "I'm
flagging all of vol 5 for background work. it's all really rough …
work slow and methodical").** The loop that makes this possible: bpy
builds any locale here in seconds; `TripPaintTest --preset X --mood
<the scene's own> [--trip 0 | --energy 0.22]` renders it through the
real stack; judged at 1:1. Worklist = 26 vol 5 presets over ~20 GLBs
(diner ×2, riverfront ×2, graustark ×4, cathedral ×2, bungalow,
roberts_kitchen, natalie/montreal/new_orleans/elicia apartments,
houston office + studio, hospice, vehicle cab, cafe, riverboat
interior, chapel, new_orleans office/bar/room). DONE this pass:
diner (lights, clock, windows), bungalow (the dresser off the bed's
foot, drawers to the aisle), roberts_kitchen (D4 proof of life + the
kitchen's BONES + re-vantaged establish — see _SET_DETAIL_PLAYBOOK
2026-10-02). NEXT, in order: roberts_kitchen's ceiling hotspot and
flat walls (D2); cathedral_interior lighting (renders near-black); the
riverboat interior; Natalie's apartment (vol 5's second-most-used
room); then down the list. The vol 5 DIRECTION pass ("camera and
director attention not where they should be") rides along: each
locale's establish re-vantaged to the chapter's geography, its
[shot:] markers checked against the prose.

**2026-10-02 · THE PAINTED ROOM · draft 5 — the Deck's five notes.**
"getting there, but still too bright and contrasty in the diner, and
too muddy and details lost in the exterior … the neon line border is
coming on a bit strong" / "the warehouse looks terrible … blobby" /
"the same repeating watercolor wash texture stays static" / "the
empress. looks like underwater". Causes and fixes in
_SHADER_VISUALS_PLAYBOOK 2026-10-02 (v): the scene's own [mood:] under
the paint (signal artifacts quieted), gradient-gated layering, lighter
ink, the paper anchored to the view. Verified on the diner and
riverfront under `night`, the warehouse under `arcana_warehouse`.
**STANDING ORDER (the user): "background passes just need much further
work. iterate and iterate."** Open from the same session, NOT the
painter: (a) Elicia's room — the wardrobe/drawers at the foot of the
bed cannot open (set design); (b) the Lovers' domicile (roberts_
kitchen) "needs to feel domestic and lived in, proof of life, not a
sterile empty thing" (a D4 use-states pass, _SET_DETAIL_PLAYBOOK);
(c) "direction still isn't strong at all, vol 5. camera and director
attention not where they should be" (the vol 5 [shot:] coverage and
marker aim — a chapter-by-chapter direction pass).

**2026-10-02 · THE PAINTED ROOM · draft 4 — a real watercolour.** The
Deck on draft 3: "better, but it doesn't look like watercolor at all.
keep working and go ahead and get vol 5 up to snuff." The watercolour
model is now one shared include (wash regions, bleeding, stepped
layers, pigment density, pooled rims, dry paper, pencil) used by the
room pass and the hero look alike — see _SHADER_VISUALS_PLAYBOOK
2026-10-02 (iv). Rendered here on the real diner, riverfront and
cathedral (bpy builds all three now; TripPaintTest `--trip 0` /
`--energy 0.22`) and John over the in-game diner. **Draft 5 targets:**
the Deck verdict in play; the cathedral renders very dark (its lights
need the diner treatment); Graustark + the bayou lighthouse through
the same loop; the layering strength per volume (vol 6 may want it
softer); the Steam Deck's frame time with the 64-tap wash on both
passes.

**2026-10-02 · THE PAINTED ROOM · draft 3 — vol 5's tenor kept, lit.**
The Deck on draft 2: "vol 5 looks bad still … I want the look vol 6
has, but with vol 5's tenor. I didn't want it to go away. It was just
poorly lit" / "Awful looking" (screenshot: green aura + glare). The
tenor is TripSync's arcana aura over the painting; the painter's bed
and the vol-5 hand were the wrong fix and are removed. The aura now
renders in its inked form over the paint (trip_sync `paint_under`
0.85) — tested on the real diner (bpy builds locales here now) with a
held loud beat: green ink on the edges, no glare. The diner's lights
were the "poorly lit": fluorescents 8.0 → 4.5, ambient 1.0 → 0.75,
glow 0.85 → 0.55. THE CLOCK ("still without numbers or hands … hanging
above an expo and not on the wall, where it should probably be to the
left"): every dial part was built on the far side of the face, and the
clock floated at x=0 over the expo line; rebuilt on the galley's east
wall (x 4.91, the framed-photos wall, left of frame from the front
door), dial facing the room, hands/pegs/hub/nail, marker re-aimed —
verified in a local render reading 3:47; then raised ("still hanging
too low, coming down into the doorway") to clear the door under it.
THE WINDOWS at 3:47 AM ("too bright, even with exterior lighting of the
paddleboat"): the west wall's five panes were pie-case glass, near
white — now night glass (0.13, 0.15, 0.21). **Draft 4 targets:** the Deck
verdict in play with music (the inked aura at real energy); the other
vol 5 locales' lighting (cathedral, Graustark) through TripPaintTest;
`paint_under` per register (community/milk_honey may want less ink).

**2026-10-02 · THE PAINTED ROOM · draft 2 — balance.** Deck notes: ch 0
muddy + no detail; the diner washed out, "far too bright"; ch 1 no
interior; vol 5 "real rough … needs a strong direction balance pass";
Planned Community / vol 6 "looks a lot better". Draft 2: the pass keeps
the scene's values (re-key, highlight knee, dark-paper margins,
relative ink, wash radius 3.5 → 2.0), downward-only auto-exposure (the
diner renders near-white before any painting), the PAINTER'S BED (the
locale's stack drops quantization / ASCII / neon / dither under the
painter — the diner's rings were the "raw" mood's palette 32), and a
per-volume hand (vol 5 firmer and lower-keyed; vol 6 unchanged). Ch 1's
missing interior is not the painter: cathedral_interior.glb (and its
four prop GLBs) have never been built on the Deck. **Draft 3 targets:**
the Deck verdict on vol 5 with the bed on; the scenes' [mood:] beats
that WERE the direction (silent film, noir, ink_blue) need painted
equivalents now that the bed turns their effects off; vol 7's hand.

**2026-10-02 · THE PAINTED ROOM · draft 1.** Sheet 45 verdict from the
Deck: "portraits generally work very well, I'm pleased for now.
background clashing with the new art style and models. let's bridge
the gap." Every 3D VN background now ends in a watercolour-and-ink pass
in the heroes' language (painted_scene.gdshader in a layer inside
Background3D's viewport, above the locale's own stack; paper colour by
volume). Tested over sheet-45 frames of the diner, kwik stop, cosmic,
cabin, cape and bar with the heroes' look laid on top, and live in a
Background3D. **Draft 2 targets:** the Deck verdict in play; the locale
style packs underneath (neon edges, rings, ASCII) still show through —
a "painted" style pack per locale that hands the painter clean flat
colour would read cleaner than painting over neon; the 2D PNG /
composition backgrounds are not painted yet; the TripSync aura on top
of a painted room; frame time on the Deck (two full-screen ~70-tap
passes plus the portraits).

**2026-10-02 · PORTRAITS · draft 4 — the painted hero.** The Deck: "more
shaders and post-processing, less plastic, more cartoon sketch, with
watercolor vibe." Matte materials on load + a watercolour-and-ink pass
on the portrait container (washes, cel bands, pooling, granulation,
broken ink, hatching, ragged bleed; static, no boil), steered by mood
and room — see _SHADER_VISUALS_PLAYBOOK 2026-10-02. Rendered here over
the diner (John, Frasier; the local GLBs are older than the Deck's).
**Draft 5 targets:** the Deck verdict on the real heroes; ink weight by
shot size (the ecu's lines run heavy); a paper colour per volume
register (vol 6 milk_honey warm, vol 5 arcana cooler); the sheet
now captures the composited look (`_heroes/<hero>__look_<size>_<mood>.jpg`,
over paper grey) — judge the real heroes there; Deck frame time with three
portraits up.

**2026-10-02 · SHEET 44 · eye anchors judged.** The three close sizes
step visibly on all 51 heroes (chest-up → head and shoulders → brow
to mouth) and the eyes sit near the upper third in nearly every
frame — sheet 43's mcu ≈ cu is gone, and the ecu no longer slides to a
cheek or hairline. The bedroom's `shot_insert_window` now frames the
window over the bed. **Draft 5 targets:** the window glass is an opaque
flat grey-green box, so "the gray-green of cedars" is only a colour:
put cedar silhouettes beyond the east wall and make the pane read as
glass (a lighter centre, the muntins' shadow); the sheet still saves
the raw portrait viewport, so the hero LOOK pass (rim, grade, grain)
needs a composited capture to be judged off-Deck; cathedral_interior
has never been built on the Deck.

**2026-10-01 · GOOGLE DRIVE · your own client id.** The user made their
own Google OAuth client (rclone.org/drive/#making-your-own-client-id).
`bash godot/tools/drive_setup.sh --client` asks for the id + secret
(secret typed hidden), keeps them in `godot/tools/.gdrive_client`
(gitignored, mode 600), moves BOTH connections onto them and signs each
in once. The project connection `gdrive` goes from `drive.file` to
`drive`: drive.file sees only files made by the SAME app, and the 4.5 GB
in ModernMythology was made by rclone's shared app — under the new app
it would look empty and SAVE would start a second copy. `gdrive_ro`
stays drive.readonly. The app must be PUBLISHED (a "Testing" app's
sign-in expires in 7 days); the unverified-app warning is expected.

**2026-10-01 · DECK NOTES · portraits draft 3.** Four notes from play
(details in _VN_DIRECTION_PLAYBOOK): Frasier behind the text → close
sizes eye-anchored from a per-hero eye table read off sheet 43; shaky
/ motion-sick → all portrait motion ×0.3, lens-scaled, tremor = a
decaying startle, CharLayer bob/breath/parallax cut; "lame without
post" → a hero look pass (fringe, grade, bloom, grain, rim glow in the
room's key, vignette) steered by mood and room; a character not in
the scene (vol6 prelude: Henderson stood in Maya's bedroom) → a cut
to a different PLACE (another locale GLB) clears the stage; one show
authored before its cut (vol6_ch3_coda, Rick) moved after it.
**Draft 4 targets:** sheet 44 shows the eye anchors per hero (a
contact sheet that captures the composited look, not the raw
viewport); tune MOOD_LOOK per register (vol 6 milk_honey vs vol 5
arcana); an options toggle for the look + a reduce-motion setting.

**2026-10-01 · VOICE IMPORT · draft 1.** The user: "I have a good
number of zips of voice studio audio in google drive that can be added
to the game project for the visual novel." ~60 `voice_dropin_*.zip`
under Drive "modern mythology voice files" (vol5 major arcana, June;
vol6 planned community, Aug–Sep) + more being uploaded. Each zip carries
the scene JSON AS RECORDED — unzipping would wipe later edits and shift
every NNN after an inserted node. `godot/tools/import_voice_dropins.sh`
(Deck, one paste): read-only Drive connection (`drive_setup.sh --read`,
scope drive.readonly, remote `gdrive_ro`) copies every zip on the Drive
to ~/.cache; `import_voice_dropins.py` aligns recorded lines to today's
text (difflib over directive-stripped words; ≥90 % = "close"; else
SKIPPED + listed), webm/wav → Ogg (`get_ffmpeg.sh`, shared with the
intro installer), writes ONLY the "voice" keys in place (each file's
own layout byte for byte — 37 scenes are hand-formatted), SAVE: audio
→ Drive (DRIVE_DIRS += audio/voice), JSON + report + state → git.
Idempotent by zip md5. Tested on stale git versions of real vol6
scenes: 128 lines placed, 0 misplaced, 16 skipped (split/trimmed since).
`audio_reference_audit` counts drive_manifest paths as present.
**Draft 2 targets:** read the Deck's report — the SKIPPED lines of
split nodes could take the audio on the FIRST piece when the old text
= the concatenation of consecutive new nodes; per-character loudness
pass on the imported lines; vol5 June zips vs the 8 wired scenes
(kept unless --overwrite — confirm the user wants the newer takes).

**2026-10-01 · AUDIO INVENTORY · draft 1.** The user: "sync up all the
music and sound mp3s on the drive to the tool/game as well. I don't want
to bloat it, so let's do an inventory in the tool that can send music
files to the game." Hero Studio → AUDIO (`hero_uploader/audio.html`):
SCAN lists every audio file on the whole Drive (gdrive_ro, rclone
lsjson --hash; cache in ~/.cache, never committed; the project's own
ModernMythology folder excluded; same-bytes duplicates folded); ▶
streams a file through `rclone cat`; SEND copies one file to
godot/assets/audio/drive/{music,sfx,voice_takes}/ (m4a/flac → ogg) and
for music appends a `FROM THE DRIVE` catalog entry (unlock {} — the
player has all tracks open); REMOVE undoes both; git keeps
`tools/audio_sent.json` + the catalog line; the audio rides SAVE to
Drive. Files the game already ships (md5 match) read "in game".
Tested in Chromium against a local stand-in Drive. **Draft 2 targets:**
see the real scan (the Drive mixes songs, ElevenLabs takes, stems and
loose voice folders — tune the kind guess); assign a sent track to
chapters (`chapters`) / characters (`chars`) from the page; a sent
SOUND wired to SFXBank presets.

**2026-10-01 · GOOGLE DRIVE · incoming/.** The user: "start an incoming
folder in the google drive project folder that I can reference in chat
for various things." `ModernMythology/incoming` (Drive folder id
12p3INRnze8yI4JJHYq0VynC9Yy5PePZf), with a README. Any session reads it
through the Google Drive connector (search `parentId = '12p3INRnze8yI4JJHYq0VynC9Yy5PePZf'`,
then read_file_content / download_file_content). Hero Studio's SAVE
never writes or deletes there (rclone copies only its own folders).

**2026-10-01 · SHEET 40 · drafts 40-43 judged; portraits seen.** The
first sheet since draft 39. Landed: the barn insert (a tractor of
wheels, bales), Small Wood's house insert (the house), the lake's far
shore, the skatepark's pool, the chapel whole with its cross, the cedar
tower whole, the comic shop's standee out of the lens, the diner's flat
checker. Still wrong: the cape's fog reads as a flat white sheet below
the rail (a box is not fog — blobs, greyer); the cabin bedroom is still
orange wall (the camera needs the window and the bed in, not the
partition); the bar front is mostly brick. The hero frames (the default
waist-up) read well, but every SAD frame cut the head off — the old
mood tilt was built for the wide; it now fades out as the shot tightens.
The sheet now shoots EVERY hero on disk (it used the manifest's 10) at
mcu / cu / ecu too, so sheet 41 shows whether the close-ups find faces.

**2026-10-01 · PAINT OR PASS · draft 1.** The user: "we'll narrow
individual areas once more hero assets populate them, can you compare
generations built up from raw static scene data and paint or pass on
select parts?" Hero Studio's runner + `hero_uploader/scenes.html`: a
contact-sheet frame (the raw render) goes as the reference image to
Gemini / Runway with a layout-keeping prompt and the locale's builder
docstring; raw and generations compared side by side (A/B hold); boxes
on the frame PAINT from a chosen generation or PASS (keep the raw);
composite + recipe saved under assets/concept/scenes (Drive, not git).
Tested end to end in Chromium with a stand-in generator (painted box
took the generation, a passed box inside it kept the raw, outside
untouched). The real providers are first exercised on the Deck. NEXT:
feathered masks; geometry drift; batch a locale; whether a composite
ever replaces the live render in game (the user's call).

**2026-10-01 · HERO STUDIO · the 54 are home; a name is not a person
across volumes.** The 48 assigned models had been committed by the
meshy branch's SAVE on the Deck (push refused), so switching to this
branch removed them from the folder; `git archive` of that branch put
them back untracked, and SAVE sent them to Drive (2.9 GB; manifest 54
hero GLBs). The user then saw ch0 unchanged — it is John and Frasier,
the two original models, plus two Stranger lines. Checking where the
new models speak found FOUR cross-volume misroutes (vol6 "Sammy" → vol5's
bartender, vol6 "Wren" → vol7's, vol1 "Margaret" → vol7's co-op, vol5
"Ben" → Ben Kowalski): CharLayer now plays a GLB only in the volumes its
roster entry lists (`_vol_ok`, `_glb_vols`), the roster key table holds
every entry per key, and `sammy` / `wren` are keys of sam_miller /
wren_vol6 too. Simulated over every scene: 0 misroutes, 45 heroes, ~2,900
lines in 3D. CORRECTION (the user: "I wouldn't have made new models for ch 0 and
assigned them if I didn't want to use them"): the ch0 leads' recovered
GLBs are NEW models (John 36.7 MB vs 11.4; Elicia, Nicola, Dante,
Antonio, Alberto 33-56 MB vs 0.1 MB placeholders), not refreshes — they
are on the Deck; the game showed Godot's import cache of the old files.
godot/tools/reimport_models.sh runs the headless `--import` (tested:
a replaced GLB re-imports). Best scenes to see them: vol6 ch8 hospital (Linda), ch2
dumpster (Jesse, Ben), ch17 table (Bianca), ch8 lake (Chief Miller), ch12
cosmic / ch4 speak-spell (Curtis, Rick).

**2026-10-01 · SAVES · a picture and the player's notes.** The user:
"The save state should be a thumbnail with a notes section. Players
can input these notes at any time." Each slot now keeps
user://saves/slot_N.png (384x216) — the scene as it stood when the
pause menu opened, captured before the menu draws (autosaves capture
fresh) — and a free-text `notes` field. Notes are typed in the pause
menu's new right-hand column (the slot's picture over the notes box,
saved as you type, ESC still resumes) or on the save/load screen for
any slot, from the main menu too. Overwriting a slot keeps its notes;
notes typed before the first save land on it. Deleting a slot deletes
its picture. Saves from before today show "no picture". Verified in a
Godot 4.6 headless run (17 checks: write, resize, overwrite, pending,
both screens' editing, delete). NEXT: the Deck — the capture runs on
the real renderer there (headless cannot draw); a "notes" glyph on
the slot line when a save has notes; pad typing is Steam's keyboard
(STEAM + X), noted under the box when a pad is connected.

**2026-09-30 (later) · HERO STUDIO · big files on GOOGLE DRIVE.** The
user: "I don't want to crowd up git with large models and files, can we
use google drive?" New GLBs (heroes/demons/props) and all of
concept/meshy are gitignored; SAVE uploads them with rclone (`copy`,
never `sync`) to `gdrive:ModernMythology`, writes
godot/tools/drive_manifest.json (size + md5 per file), and commits only
small text; `drive-pull` restores a checkout. Setup is one script,
godot/tools/drive_setup.sh (rclone into ~/.local/bin, OAuth once in the
browser, scope drive.file). Tested with a folder standing in for the
Drive: models off git, manifest on, a fresh clone pulls byte-identical.
Already-tracked GLBs stay tracked (untracking them would delete them on
every other checkout's pull).

**2026-09-30 · HERO STUDIO → THE GAME BRANCH.** The user: "Heroes
aren't showing up in the game project, despite being in Hero Tool."
Two causes: (1) Hero Studio and its routing lived only on
`claude/meshy-image-generation-w92vr6`, which split from this branch
on 2026-07-01 (141 vs 1231 commits; a full merge conflicts in 69
files, mostly July-era locale builders) — this branch had no roster
and no roster routing in CharLayer, so only the old hard-coded keys
could ever show; (2) the 48 assigned models were never committed
anywhere, so the server's meshy branch still held the original 7.
PORTED here (not merged): CharLayer's three hero commits (a8eaffea's
model table — the game branch had pruned it while the GLBs did not
exist — plus 0ca03690 looks-by-scene and 5bcab83c every-roster-key),
GameEngine's set_scene_context call, meshy_roster.json,
meshy_pipeline.py (with SAVE), meshy_canon.py, meshy_recover.py, the
recovered mapping, hero_uploader/, and the .gitignore rules for the
API keys and concept candidates (without them SAVE here would have
committed every candidate image). RULE from now on: run Hero Studio
from THIS branch, so SAVE lands models where the game reads them. The
meshy branch keeps other sessions' previz/menu work; do not merge it
wholesale.

**2026-09-26 · HERO STUDIO · the recovered batch.** The user's 60
Meshy models of 2026-09-25 never reached the game (the runner's
manifest and stills were lost with the clone); `meshy_recover.py
fetch-all` pulled them into `concept/meshy/recovered/<task_id>`,
and `godot/tools/recovered_mapping_2026-09-26.txt` (on the meshy
branch) names 48 of them from the thumbnails — the batch ran in
roster order — and `assign` moves them to `heroes/<slug>.glb`.
**The five left in `recovered/` are the user's to keep** (four
first-versions of redone characters — Douglas, Jimmy, Rick, Curtis
— and a younger Alice Newsom with a XIII sigil on her skirt): "keep
there for now, I may use them for something." Do NOT clean that
folder up or assign them without the user. NEXT there: the
green-skirt Alice as a look slot if the user wants both; the 8
recovered GLBs without thumbnails, if any, need naming by eye in
the runner's viewer.

NEXT (draft 39): small_wood_road's second draft (it is template +
props: the house's window lit, a porch light, the mailboxes'
reflectors, a car in the drive); the "door-like polygons" — ask the
user for a locale; the 46 nightmare-cell dots, verified on the sheet.

THIRTY-NINTH PASS. small_wood_road, draft 2
(`build_property_dressing_2026_09`): the house's lit window and porch
fixture were already there (the tscn's House_Window and porch
practical); what the frame lacked was anyone home — a pickup up the
gravel by the pole barn, nose to the barn, and reflectors on the three
mailboxes' road faces. The builder carries its NEXT (the gate's chain
and padlock, a dog on the porch, the minister's car on the roadside
preset's gravel, the crick's headwall wet). The nightmare cell's 46
dots: the buried-detail tool finds none left — the tin-tile pass
moved them; verified by tool, not yet by eye on the sheet.
NEXT (draft 40): the roads on the sheet (highway 101's reflectors and
taillights at dusk, the truck in Small Wood's drive); the "door-like
polygons" still need a locale from the user; the seven kitchens by
eye once more; Simon's room in the game (no preset frames it).

FORTIETH PASS (2026-09-27). The 09-26 sheet (from draft 39) against
the 09-25 one: 6 frames changed, all memory_warm grain — the roads'
new props sat outside every frame, so the roads were judged by eye:
· small_wood_road: `shot_insert_house` looked at grass and a tree
  crown (it stood east of the road pitched 25° down, aimed south);
  it stands on the drive now, 1.5 m up, looking west at the house.
  The barn insert's red and orange boxes were `Pole_Barn_Tractor`
  and `Pole_Barn_Hay`: a tractor is its wheels (two tall rear, two
  small front, a narrow hood, a seat, a stack) and hay is bales
  (nine, two courses, offset, two shades).
· highway_101: the fog line (0.92 white) was the brightest thing in
  the dusk establish, a blazing line up the shoulder; worn to 0.66.
· the eleven kitchens by eye: counters on their walls, yes; but every
  one had a RING OF SIX BLACK DOTS on the wall — the kit wall clock's
  off-white face is the colour of a cream wall under a warm
  practical, so only its four ticks and two hands showed. The rim is
  now a dark ring 3.5 cm wide behind the face's front, with a hub.
  One edit in `_props/decor.py`; every kit clock in the game.
· simon_apartment: built in the support pass, six lights, no shot
  markers, no preset, no scene — "Simon's room in the game" meant
  all three. It has a `simon_apartment` preset now (NE corner
  looking SW: the armchair and the TV's crate near, the boot on the
  far wall, the window and fire escape beyond) and four markers (tv,
  boot, two closeups). Pointing XII Hanged Man at it was TRIED and
  UNDONE: the chapter cues the card laid by the reading rug, the
  deck, the phone on the counter and the apartment door (the bell,
  the stairs) — eight cues on four objects Simon's room does not
  have (`shot_marker_audit`: 8 blind, ceiling 0). So there are TWO
  builders of the same apartment: natalie_apartment (7×5.5, the
  rug and the deck, where the chapter plays) and simon_apartment
  (5×7, the boot on its peg, the tipped chair, the TV on its
  crate). USER DECISION: merge the Hanged Man dressing into
  natalie_apartment and retire the other, or move the rug, deck,
  door and phone into simon_apartment and switch the chapter. Until
  then simon_apartment has no scene and the manifest (uses-only)
  leaves it off the sheet; `contact_manifest.py --all` frames it.
· tools: `marker_reframe.py --help` used to RUN the pass (it wrote
  cabin_road's drone insert before it was stopped; reverted); a
  fixer prints its doc and exits on --help now.
NEXT (draft 41): the sheet — the tractor under the tin, the house
insert, the clocks in eleven kitchens; the user's call on the two
apartments (then Simon's five frames for the first time); the "door-like
polygons" still need a locale from the user; the highway's draft 3
list (dashboard glow on the hood preset, wet asphalt after ch22's
rain); Small Wood's (the gate's chain, a dog on the porch).

FORTY-FIRST PASS (2026-09-30). No new sheet since draft 39, so the
pass surveyed all 146 establish frames of the 09-26 sheet by eye
(twenty to a page) and drafted the four worst backgrounds:
· grunion_beach (beach_night + grunion_beach presets), draft 2: both
  frames were a dark sea under three BLACK BARS — the cloud "slabs"
  were 22 × 2.6 m cards 6 cm thick, 24 m out, darker than the fogged
  sky; the beach was 36 m wide, so the tide-edge vantage looking west
  saw the sand, gleam and surf lines END, and the far-dune band on
  side W stood IN the sea. Now: the beach runs 420 m, dunes landward
  only, Ground_Far landward only (under the sea it made a sand strip
  on the horizon); a cloud DECK of nine flattened blobs 140-200 m out
  with a gap where a moon disc sits, the Hidden_Moon light moved up
  into the gap to silver its edges; the narrator's FOOTPRINTS from the
  dune to the wet band ("I walked down to the water's edge"); a wrack
  line; driftwood piled at the dune foot. beach_night reframed down
  the footprints (driftwood left third, the moon gap right third);
  grunion_beach dropped to eye 0.9 on the wet band looking west.
· cape_perpetua_overlook: the white slab under the rail and the crow
  was the FOG BANK — top at +1.0, east edge over the platform, and
  vertex alpha is not transparency here. And the headland ground plus
  Ground_Far ran straight over the bluff drop, burying the trees below
  to their crowns and hiding the sea under a lawn. Fog now 2 m under
  the lip, west of the bluff face; the headland and Ground_Far stop at
  the bluff; the bluff runs 300 m of coast (it was 12 m, and past its
  ends the land just stopped); the sea reaches the bluff foot.
· roadside_chapel (chapel_exterior): the camera stood 4.5 m off a 5 m
  facade — one blank tan wall and a trash can. It stands at the
  apron's road edge now, tilted up (the whole front, the portico, the
  steeple and cross, cane both sides); the front has two lancet
  windows, clapboard shadow lines and corner boards.
· tideline_survey: the pale "rocks" hanging in the sky were the fog
  bank, six blobs with their bottoms 1.2 m over the shelf. Eight wider,
  flatter blobs sunk two thirds into the water: a bank rolling in.
Survey list for later passes (weak establishes, not yet drafted):
graustark_chalk_wall/cottage/ruins (the same red-and-white stack
dominates all three), crumpled_barn_ext/int (grey mush — intended?),
lake_palestine + its dock (empty water), kestrel_mountain (a wall),
skatepark_day (empty lot), cedar_tower_exterior (cropped), bar_
exterior_night (camera against the wall), cosmic_comics_interior
(a purple panel across the lens), cabin_interior_bed (orange walls).
NEXT (draft 42): the sheet for the four drafted here; then the survey
list, worst first; the two-apartment decision (user); the door-like
polygons (user).

FORTY-SECOND PASS (2026-09-30). Still no new sheet; down the survey
list:
· crumpled_barn, draft 2: the exterior was grey on grey on grey — a
  grey board gable square-on against a grey sky over a grey-olive
  field, with six 4.8 x 3.2 m hedge BOXES reading as walls either
  side. The field and far stubble are lifted to dry straw, the hedge
  is twelve seated foliage blobs (the field runs under them now), and
  the camera stands SE three-quarter on the gable so the fallen roof
  behind it reads — "a gray barn that lost its back half". Inside,
  the daylight shaft onto Jiggles' cabinet and the mermaid sign is
  doubled (1.1 → 2.2, range 4 → 5).
· lake_palestine (both presets), draft 2: "looking SOUTH across the
  cove at the far shore" showed dark water to a grey horizon — the
  water ran 200 m to a bank of nothing and the far shore was an 8 m
  box 260 m out, fogged to a sliver. The cove is 158 m across now: a
  clay bank, the far land, two ragged rows of 88 pines, three treeline
  ridges behind for the fog. The side shores stop at the far shore
  (they were coplanar with it past y -158).
· skatepark, draft 2: THE POOL was "suggested without booleans" — a
  darker patch and a coping outline flat on the slab; the establish
  read as an empty lot. It is a real 1.5 m pit now: `holed_box` cuts
  the slab, the grass and Ground_Far round it; four walls, a floor, a
  drain, quarter-round transitions (prisms) along every wall's base,
  the coping flush and full length. The hump moved west out of the
  pool's mouth; the establish tilts down into it.
· graustark (chalk_wall / cottage / ruins): NOT drafted, diagnosed.
  The red-and-white stack in all three frames is the Hermit's 18 m
  bayou lighthouse, and the railing across the upper half is the
  HWY 90 truss bridge (deck at z 5, 11 m of truss) 10-20 m north of
  the ruin quarter. The quarter was built round the lighthouse's
  keeper cottage on purpose (Joanna is IX), so the lighthouse
  belongs; three sets inside 60 m is the problem. Draft 2 needs the
  sheet in hand: either move the bridge's crossing north (a town-map
  change: HWY90's waypoints) or reframe each preset to own one of
  the three (the chalk wall with the lighthouse out of frame, the
  cottage with the lighthouse whole, the ruins wide with the bridge
  as the roof of the frame).
NEXT (draft 43): the sheet for drafts 40-42; Graustark as above;
kestrel_mountain (a wall), cedar_tower_exterior (cropped),
bar_exterior_night (lens on the wall), cosmic_comics_interior (a
purple panel across the lens), cabin_interior_bed (orange walls).

FORTY-THIRD PASS (2026-09-30). Still no new sheet. Four frames that
were camera problems, fixed as camera problems:
· cabin_interior_bed: the 09-03 `--propose` pass had stood it in the
  MAIN room west of the east room's partition, pitched 20° up — the
  "orange walls" were the partition and the ceiling. It is at the
  pillow end inside the east room now (blender 1.2, 2.5, eye 1.05),
  the made bed low, the window over it (ch1: "the window above the
  bed gave her the gray-green of cedars").
· cosmic_comics_interior: the purple slab across a third of the frame
  was the cardboard STANDEE, 0.9 m in front of the lens in the SE
  corner. It stands in the SW corner by the door now, small and far
  on the frame's left.
· bar_exterior_night: on the sidewalk 2.3 m off the facade looking
  WNW, the lit front window filled a third of the frame and the door
  was a sliver. The camera stands across the (3 m) road now looking
  N at the whole frontage: door spill + neon, the window, the sedan,
  the lamp, the dark upper story.
· cedar_tower_exterior: 18 m off a 26 m tower pitched 17° up, with
  five spruce 3 m off the lens. It stands 30 m off now, the whole
  tower top to doors, the Sitka ring's south arc framing the left.
  Two audit findings on the way: the tower's floors were named
  `Tower_Band_*` and the vantage audit reads any "band" as a far
  horizon band — the tower was invisible to it (renamed
  `Tower_Cedar_*`); and the clearing's gravel ended short of the
  camera, so the lower frame was Ground_Far, which the EMPTY test
  also treats as nothing (the gravel runs south under the camera).
  The rename also un-hid the tower from the DOORWAY gate (its IGNORE
  has `band` too): the 2.5 m double doors ran up into the glass band
  over a 2.2 m cedar floor, so the tower could not host them — they
  are 2.1 m now.
kestrel_mountain: NOT drafted — the frame is a dark rock wall left, a
pale slab floating in the sky (the "cloud on the top"?) and a
corridor path; needs the sheet at full size to diagnose.
NEXT (draft 44): the sheet for 40-43; Graustark; Kestrel; then a
second survey of the markers (the establishes are the first frame of
a scene, but most of a scene's frames are its inserts and closeups).

NEXT (draft 36, as written): judge the moved pieces on the sheet (ben, jesse, sam,
safehouse, the seven kitchens); name the 13 deliberate OFF_WALL pieces
(a `free=True` tag or a name class) and gate placement; simon's TV on
a crate mid-room and the back office's milk crate — decide; the
"door-like polygons" — FREE_SLAB found none after the wall names were
learned, so the user's polygons are something else: look at the
frames for tall thin things (the shed's swung leaves? the bedroom
partitions' cased-opening posts? Lena's Part_E post at 0.25 × 0.16?).

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

- **P0 (2026-10-01):** voice zips on the Drive → `import_voice_dropins.sh`
  on the Deck; then the AUDIO page for the Drive's songs/sounds (see
  the dated entries). Read `godot/tools/voice_import_report.md` after.
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
