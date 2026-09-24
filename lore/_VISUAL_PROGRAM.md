# THE VISUAL PROGRAM — backgrounds · models · direction · design

Written 2026-09-13 at the user's ask: *"Improving backgrounds, models
and direction and design is still a big project. Let's plan that
out."* This is the plan. It sits under THE DRAFTING PROGRAM
(CLAUDE.md, `_IMPROVEMENT_ROADMAP.md`): every arc below ships a
numbered draft, never a finish. Read this before picking up any of
the four pillars; update it when an arc ships or a decision lands.

---

## 0 · Where it stands (honest numbers, 2026-09-13; tally 2026-09-19 below)

**Tally, 2026-09-19 (one session):** backgrounds — 24 rooms through a
numbered draft in screen-time order (vol 7's first and second tier,
vol 6's dozen, vol 1's two, the six arcana sets), every one Deck-unseen;
two kit helpers (`make_fern`, `make_pendant`), one kit defect fixed at
the helper (`make_cord_run` drew slabs), one new gate (orphan
practicals). Design — the consequence map drawn, SKILLS EARN, the two
decorative checks made real, seven remembered choices (vol 7's apology,
vol 1's four, vol 2's house, the Henderson kettle), two broken choices
found and gated (`vn_target_audit`), verb coins on all four model
chapters, THE INVENTORY (two items that cross a chapter), Community
Planned's masthead and reader letter, the gauntlet's per-arcana card.
Still zero frames seen: the contact sheet has not run.

| Pillar | State |
|---|---|
| **Backgrounds** | 146 3D presets carry the VN's 478 background placements; 121 Blender builders behind them. The top 20 presets are 47% of everything the reader sees; 71 presets appear once. Four MODEL CHAPTERS (diner, kwik stop, cathedral, henderson) set the bar; ~40 tail-wave locales sit at draft 2–3; vols 1–2's migration sets at 1–2. Every set is vertex-colour geometry under real lights — no textures, by constraint. The 2026-09-05 lesson stands: *the primitive layer was the ceiling*; five new primitives (lathe, prism, tube, rot-box, heightfield) and the first composites (car, ranch house) exist, and most sets have not been rebuilt through them. |
| **Models** | Seven vol 5 principals have hero GLBs (John, Frasier, Elicia, Nicola, Dante, Antonio, Alberto). The fifteen vol 6–7 characters are 60×64 pixel busts BY DECISION until real models exist; `Portrait3D` will light and frame any GLB dropped in with zero code. Three routes exist and none is running: Mixamo/Ready Player Me (the user's keyboard), GNM heads on lofted bodies (offline, shelved after one look at Sam), Meshy image-to-3D (runner + Blender import built, no key ever entered). |
| **Direction** | The grammar is built (establish / closeup / insert / panel, beats, kinetic text, cast staging, registers, THE TRIP, the feedback). 871 markers across 153 presets, every one aim- and obstruction-audited to <0.5°; 19,208 pages, none over 300 characters; 0 story problems. **ZERO framings have been seen through a lens** since the per-preset marker wave; the two Deck reads that exist (the title-card directive, the warehouse exterior) each found a real defect in minutes. |
| **Design** | One game-grammar row per pillar has shipped (attract mode, the letters column, one verb coin, Minter in the stick). The VN's own game layer — five skills, choice plates, flags — has never had a design pass; VnSweep found dead checks and unwinnable choices, which means nobody has drawn the consequence map. The Salmonberry overworld (the flagship gameplay build) is written and waiting on the word. |

---

## 1 · The ceiling, and the three levers that raise it

Without textures the sets top out at "dense, lit, well-dressed
geometry" — the model chapters. That is a real ceiling, and it is
where most of the game should get to before anything else matters.
Three levers go above it, and all three are user-side keys or hours:

1. **An image key or ArtCraft exports** (gate 1) — painted chapter
   cards, CG art, endpaper plates, and REFERENCE IMAGES for lever 2.
   Never a scene background (the 2026-08-03 verdict: VN backgrounds
   are 3D scenes).
2. **A Meshy key** — image-to-3D for HERO OBJECTS: the things whose
   silhouette carries a chapter and that a lathe cannot make (the
   SCUMM machine, the riverboat, Olaf's woodstove, Lena's easel, the
   Cathedral's rack). The pipeline exists end to end
   (`meshy_render.py` → `build_meshy_import.py`); output is
   untextured low-poly with a flat vertex colour, so it slots into the
   same look. Also a CHARACTER route: a reference image → a mesh →
   `Portrait3D`.
3. **Character sessions** (gate 2) — Mixamo/RPM, ~30 minutes each,
   fifteen characters, Lena first. Or lever 2 with a reference
   image, which moves the user's part from thirty minutes to
   approving one picture.

Everything else in this plan is Claude-side and starts now.

---

## 2 · ARC 0 · THE LENS (the loop that makes the rest verifiable)

The single blocking fact in every pillar is the same: the work is
verified by math and never by eye. The user pastes screenshots by
hand; each one has found a defect. The fix is a rig, not more
discipline.

**Build `godot/tools/VnContactSheet.tscn` (Claude, one session):**
boot the VN engine headless-of-story, and for every 3D preset in
`Background3D.CAMERA_PRESETS` (and every `shot_*` marker the preset
owns), load the locale, apply the preset's default mood at its
scene's clock, wait for lights and the post stack, and save a
1280×720 PNG to `godot/qa/contact/<preset>/<marker>.png`. Also one
frame per hero GLB through `Portrait3D` at each expression. ~1,000
frames; a few minutes on the Deck.

**The loop, standing:**
1. Claude ships a draft, gives ONE paste: pull → `list_stale_builds`
   rebuild loop → contact sheet.
2. The user runs it and pushes `godot/qa/contact/` (a second paste).
3. Claude READS the PNGs — the frames are the taste pass — and cuts
   the next draft from what is actually on screen: the stump, the
   wall the closeup is pointing at, the room lit from nowhere.
4. The user's own screenshots and verdicts still outrank the sheet;
   the sheet is for the 900 frames nobody was ever going to paste.

**Why this is Arc 0 and not a nice-to-have:** it converts every
"Deck-gated" line in the ledger (there are dozens) into work Claude
can do between the user's sessions, and it makes the STOP RULE
(`_3D_MODELING_PLAYBOOK.md`) cheap to obey: a stale GLB is visible
in the sheet's timestamps before anyone says "I don't see changes."

**Status (2026-09-15) · draft 1 SHIPPED, unseen.** `tools/audit/
contact_manifest.py` → `qa/contact_manifest.json` (146 presets, 1,266
markers, 10 hero GLBs × 7 expressions = 1,559 frames); `tools/
VnContactSheet.tscn` shoots it through Background3D + Portrait3D;
`tools/contact_sheet.sh` runs it, `tools/contact_push.sh` puts the
frames on the orphan branch `qa/contact` (decision 4 defaulted to the
branch that costs the working branch nothing). `godot/qa/README.md` is
the one-paste. Draft 2 targets: the first Deck run will find the
settle counts wrong somewhere (a shader compiling on frame 31); a
per-frame sidecar with the camera pose so a note can be turned into a
marker edit without opening the .tscn; THE TRIP as an optional second
pass at 75 %.

---

## 3 · Pillar A · BACKGROUNDS

**Principle:** one locale deep beats five shallow, and the order is
screen time. The reader lives in twenty rooms.

**The method per locale (each visit = one draft):**
- **The primitive upgrade** — rebuild the set's furniture and fixtures
  through the five primitives and the composites (`_props`): turned
  legs, aprons, lathed lamps, a car with a profile, a roof with eaves.
  When an object class appears in three locales it goes into
  `_props` and the pass multiplies (the car helper upgraded eleven
  vehicles in one commit).
- **D2–D6** (`_SET_DETAIL_PLAYBOOK.md`): surface breakup →
  infrastructure → use states → depth bands and edges (geometry runs
  PAST the frame in every direction a camera looks) → coverage and
  light.
- **Wear PERSONALITY** — whose feet, whose spills; anchored in the
  chapter prose (Olaf's decades vs Tem's weeks is the vocabulary).
- **Lighting per the lighting playbook** — three-light foundation,
  practicals tied to visible fixtures, gels by Kelvin. Most sets have
  the props and not the light; this is the cheapest jump in
  perceived quality left.
- **Hero objects** — from prose first (the bowls, the pot roast, the
  crow exist this way); from Meshy when the key lands.
- **Verified by the contact sheet** before the next visit.

**Status (2026-09-17) · cabin_interior draft 5 shipped, unseen.** The
primitive upgrade (ten lathe profiles for twenty-two stacked shapes,
kit bed/desk/chair, chamfered upholstery, chest straps), kerosene D3,
and the lighting fix the audit could never see: two fluorescent
practicals in a cabin with no electricity, replaced by the lamp, the
lantern and the stove door's ember under a cool window key. Clip hunt
0, marker obstruction 0 (the kit bed's headboard blocked `insert
chest` and was caught), aim 0. Draft 6 targets are in the builder's
docstring; Lena's apartment is next.

**Status (2026-09-17, later) · lena_apartment draft 4 shipped, unseen.**
Same method: lathes and tubes for the kitchen's fixtures and the
seventies pedestal, chamfered upholstery, the fridge's face; D3 wires
(switch, outlets, four cords, the floor lamp the dressing pass had
named); her side of the bed. The dorm-era desk-lamp practical floated
in air by the window chair — gone; floor lamp, fairy string and the
alley's sodium through the sink window carry the room. Clip 0,
obstruction 0, FLOAT 0. Next: miller_back_porch, then the vol 6 dozen.

**Status (2026-09-18) · the lights-from-nowhere class, gated.** What the
cabin and the apartment found by hand, `orphan_practical_audit.py` now
finds everywhere: nine practicals with no fixture, fixed (seven moved
onto real lamps and tubes, the cafe's pendants built). Every room's
named light stands on a fixture from here on.

**Status (2026-09-18, later) · miller_back_porch draft 3 shipped, unseen.**
The third room in screen-time order (12 placements, shared by vols 6
and 7): the primitive upgrade plus the wear, D3 and D5 passes it had
never had. Clip 0, obstruction 0, FLOAT 0. Next: the vol 6 dozen,
cosmic_comics_interior first.

**Status (2026-09-18, later) · cosmic_comics_interior draft 4 shipped,
unseen.** The fourth room: the primitive upgrade where it counted, the
shop's first wear pass, its wires (and the CRT a fill light had been
pretending was there), and a street outside the window. Next: the
back office, then the bedrooms.

**Status (2026-09-18, later) · cosmic_comics_back_office draft 4 shipped,
unseen.** The fifth room: the bulb's room with its wear and its wires;
the two fluorescent practicals the prose never had are gone (the gate
now matches fixture families). Next: maya_bedroom, sam_bedroom.

**Status (2026-09-18, later) · maya_bedroom and sam_bedroom draft 4
shipped, unseen.** Seven rooms deep now, in screen-time order; the vol 6
bedrooms share one backyard helper. The cue-word rule generalized to
every secondary object. Next: kwik_stop_interior (a model chapter —
verify, not rebuild), centro_grocery_aisle, school_field_evening.

**Status (2026-09-19) · centro_grocery_aisle and school_field_evening
draft 4 shipped, unseen.** Nine rooms deep. The kwik stop, a model
chapter, was verified rather than rebuilt (every gate clean). Next by
uses: kowalski_kitchen, vehicle_cab, henderson_kitchen (model — verify),
caldwell_porch_night, then the vol 7 second tier (hans_bakery,
cabin_road, main_street).

**Status (2026-09-19, later) · kowalski_kitchen, caldwell_porch_night and
vehicle_cab shipped, unseen.** Twelve rooms deep in screen-time order
(the two model chapters in the list verified, not rebuilt). Next: the
vol 7 second tier — hans_bakery_back_kitchen, cabin_road, main_street,
finn_apartment, board_lords_interior — then vol 1's missing_link and
shuttle_bench.

**Status (2026-09-19, later) · hans_bakery_back_kitchen draft 4 shipped,
unseen.** Thirteen rooms deep. THE TABLE's twelve chairs are kit
chairs, the pass window is cut through with the front of house behind
it, the hemlock stands outside the window. Five layout clips the
overlap recorder's threshold never reported were fixed by hand (the
counter inside the table's end, the prep table into the chairs, the
rack under the window chair, the plant in the counter). And a kit
defect found on the way: `make_cord_run` emitted its diagonal segments
as axis-aligned SLABS — every cord in the eleven rooms before this one
was a plank; it emits straight tubes now, all rooms at once. Next:
cabin_road, main_street, finn_apartment, board_lords_interior, then
vol 1's missing_link and shuttle_bench.

**Status (2026-09-19, later) · cabin_road draft 3 shipped, unseen.**
Fourteen rooms deep. The road was four stepped slabs; it climbs on
sloped prisms now, the bend and the upper run laid end to end on the
heading, and every wear sheet on the gravel follows the grade. The
tree kit gained `make_fern`. Next: board_lords_interior (its scene
also serves the `main_street` preset — 15 placements together),
finn_apartment, then vol 1's missing_link and shuttle_bench.

**Status (2026-09-19, later) · board_lords_interior draft 3 shipped,
unseen.** Fifteen rooms deep; this one carries two presets (the shop
and `main_street`). Four layout clips fixed by hand, Finn's truck off
the sidewalk into the parking lane (the road box now ends at the
curbs, which is what the LANE rule measures from), the block given
its corners. Next: finn_apartment, then vol 1's missing_link_interior
and shuttle_bench, then the arcana sets' primitive upgrade.

**Status (2026-09-19, later) · finn_apartment draft 3 shipped, unseen.**
Sixteen rooms deep — the vol 7 second tier is through (bakery, road,
Board Lords + Main, Finn's). The room's own lesson: three hero props
were placed against furniture that had since moved (the desk on
09-07, the bed on 09-10) and floated where the furniture used to
be; the practical stayed behind too. Next: vol 1's
missing_link_interior and shuttle_bench, then the arcana sets'
primitive upgrade (vol 5), then the single-use presets in batches.

**Status (2026-09-19, later) · vol 1's two rooms shipped, unseen:
missing_link_interior draft 3, missing_link_exterior (the shuttle
bench) draft 2.** Eighteen rooms deep. The pair disagree about the
diner itself (the exterior's door is at the east end and its body a
metre wider than the room inside) — a draft-4 reconciliation, noted
in both builders. Next: the vol 5 arcana sets' primitive upgrade
(six rooms plus the cathedral exterior), then the 71 single-use
presets in batches, D2 + light only, from the contact sheet's worst
frames once one exists.

**Status (2026-09-19, later) · natalie_apartment draft 3 shipped, unseen
— the arcana primitive upgrade opens.** Nineteen rooms deep. The Empress
set had nine layout faults no gate reports (a sofa in the door's
swing, a lamp and a quilt in the air, a record inside its plinth);
the footprint walk found them in ten minutes. Next: new_orleans_office,
new_orleans_apartment, houston_office, bungalow_interior, hospice_room,
then the cathedral exterior.

**Status (2026-09-19, later) · new_orleans_office draft 3 shipped,
unseen.** Twenty rooms deep. Six layout faults again (a modesty panel
at the sitter's knees, a cabinet across a door, wainscot inside the
wall). The pattern of the day, for the playbook: the template rooms
were dressed by coordinate and never walked. Next: new_orleans_
apartment, houston_office, bungalow_interior, hospice_room, the
cathedral exterior.

**Status (2026-09-19, later) · new_orleans_apartment draft 3 shipped,
unseen.** Twenty-one rooms deep. The Tower set's whole window wall was
inside the wall. Next: houston_office, bungalow_interior, hospice_room,
the cathedral exterior; then the single-use presets.

**Status (2026-09-19, later) · houston_office draft 3 shipped, unseen.**
Twenty-two rooms deep. The Emperor set's glass office was drawn
inside out. Next: bungalow_interior, hospice_room, the cathedral
exterior; then the single-use presets.

**Status (2026-09-19, later) · bungalow living room + studio shipped,
unseen.** Twenty-three rooms. The Priestess set is a vendored builder
(its own make_box for the recorder); the kit imports into it fine.
Next: hospice_room, the cathedral exterior; then the single-use
presets in batches.

**Status (2026-09-19, later) · hospice_room draft 3 shipped, unseen —
the six arcana sets are through the primitive upgrade.** Twenty-four
rooms. Next: the cathedral exterior the Magician cuts to; then the
single-use presets in batches (D2 + light), then the model chapters'
verification sweeps.

**Status (2026-09-19, later) · DESIGN · the two decorative checks are
real, the apology is a remembered choice.** The backgrounds pass is at
the Deck-gated boundary (single-use presets from the sheet's worst
frames), so the design row runs: next the vol 1 faust_* flags paid off
one callback each.

**Status (2026-09-19, later) · DESIGN · vol 1's four choice-flags paid
off.** Every choice in vol 1 that sets a flag is now remembered by a
line later in the volume (`when_flag` with `is` for valued flags).
Next: vol 2's Delores pair (ghost / lost) if they are choice-set.

**Status (2026-09-19, later) · DESIGN · two broken choices fixed, the
choice-target gate added, vol 2's house remembered.** vol 1's opening
ended the volume on two of three options; vol 2's graveyard looped.
`vn_target_audit.py` gates every goto/pass/fail from here on.

**Status (2026-09-19, later) · DESIGN · the four model chapters carry a
verb coin each.** Seven coins in the game. Next on the design row:
the inventory the coins feed; the gauntlet's tempo rows; Community
Planned's masthead. Backgrounds resume when the contact sheet lands.

**Status (2026-09-19, later) · DESIGN · the inventory, draft 1.** Items
ride in the flags; the HUD carries them; the workbench's capacitor is
the first thing picked up and used. Next on the design row: an item
per model chapter with a use across a chapter boundary; then the
gauntlet's tempo rows.

**Status (2026-09-19, later) · DESIGN · the second item crosses a
chapter.** Two Powerades from the cooler reach the dumpster; the
kettle is remembered on Sunday. Two model chapters carry an item that
matters; the diner's cannot (John leaves the volume at ch0). Next on
the design row: Community Planned's masthead and the reader letter;
then the gauntlet's tempo rows.

**Status (2026-09-19, later) · DESIGN · Community Planned's row.** The
masthead reads as the zine; a reader letter answers the prelude's
sprinklers. Left on the design row: the gauntlet's tempo rows, and
Salmonberry on the word.

**Status (2026-09-19, later) · DESIGN · the gauntlet's per-arcana card.**
Every ending's reading now carries the arcana's record. The design
row's Claude-side items are through; what remains on it is Deck-
gated (the bursts) or user-gated (Salmonberry).

**Status (2026-09-22) · THE SUPPORT PASS.** The user saw the frames: objects
floating everywhere. A new gate (`support_audit.py`: everything must
be connected to floor, wall or ceiling through what it touches)
found 3,805; a recorder bug (strung wires recorded as a point), five
kit helpers and eight rooms brought it to 1,181 with a per-locale
zero-regression baseline; the second pass took the kwik stop and
the diner to ZERO and the repo to 913 (the two model chapters set
the four kinds of float — see the geometry audit playbook); the
third took the riverboat, the school field, the solenade garden and
the cedar tower to zero and the repo to 652; the fourth took nine
more (carnival, centro, hierophant circuit, courthouse, el rancho,
bungalow, salty tome, both nexcorp stations) to zero and the repo
to 422; the fifth took seven of the long tail (christian ice, parish
cemetery, roadside chapel, elicia, mixing glass, montreal, cliffside
circus) to zero and the repo to 326. THEN THE USER'S VERDICT ("still
getting pillows floating away from beds … objects inside other
objects, too"): the GLBs are not in git (the Deck renders old builds
until the rebuild paste runs) and the gates were forgiving — the
touch tolerance went 3 cm → 1.2 cm, the overlap grammar tightened,
both gates on per-locale baselines that only come down. The sixth and
seventh passes took the kwik stop and the diner to zero at the new
tolerance (support 1,088, overlap 208); the eighth took twelve more
rooms to zero and re-planned the centro grocery aisle, whose meat
case stood in the checkout lane and whose deli stood inside the
bakery — hidden by the gate's "contents" rule, now a size test
(support 725, overlap 210 under the tighter grammar); the ninth took seven more (bindery, hierophant, riverboat, asylum, new orleans bar, simon, roberts kitchen) to zero (support 567, overlap 209). This pass runs
ahead of every other background item: a room that floats is not a
draft of anything. The tenth pass taught the recorder spheres —
every vendored sphere had been invisible to every gate, and the
diner (a model chapter) had six table lamps built inside six booth
pendants because of it (support 517); the eleventh took five more rooms to zero (support 447); the twelfth found the counter kit burying all its dressing 2 cm deep in 22 builders and took six more rooms to zero (support 371); the thirteenth took eleven more, including the two worst overlap rooms (the pit stop 26 clips → 0, the courthouse 10 → 0); the fourteenth took eleven more and fixed two more kits (the hospital bed's rails, the security camera); the fifteenth took the seven rooms at 7 and the three worst overlap rooms to zero — the Centro break room's whole kitchenette faced the wall, and the crumpled barn's automaton hung inside a solid block (support 123, overlap 120). The sixteenth found 43 WINDOWS IN 34 ROOMS BUILT INSIDE THEIR WALLS (the window kit only built toward the room on north and east walls) — every one now on its room face — and took the diner to zero again (support 75, overlap 81). The seventeenth found the same fault in the wall kit's BASEBOARDS — 398 in 79 rooms built inside their walls — now on the room face (119 walls also had theirs pointed out of the room), and took eight more rooms to zero (support 45, overlap 75). The eighteenth took the rooms at 3 and the kwik stop (two Slurpee machines in one spot; an end-cap display built into another) to zero (support 27, overlap 56). The nineteenth took the support count to ZERO across all 114 measured locales — nothing floats — and overlap to 34 (the kwik stop's NE corner re-planned; new auburn road's ditches had been hidden under its ground sheet). The twentieth took overlap to ZERO too — both gates now hold every builder at zero (any float or clip fails the suite) — after the recorder learned a blob's true squashed shape and exposed 48 blobs seated as if round. THE SUPPORT PASS's measurable targets are met; its next draft is the Deck: see it rendered, and fix what the gates cannot see. The twenty-first added a gate that runs every builder's REAL kit code (two builds had been dying in Blender unseen) and fixed the sheet's worst cameras (D'Ambrosio's stood outside the building).

**Draft targets, by volume, by uses:**
- **Vol 7 (current):** `cabin_interior` (31) · `lena_apartment` (23)
  · `miller_back_porch` (12, shared with vol 6) · `salty_tome_alley`
  (10) · `hans_bakery_back_kitchen` (8) · `cabin_road` (8) ·
  `main_street` (8) · `finn_apartment` (7) · `board_lords_interior`
  (7). The cabin and Lena's are at draft 3 and closest to the bar;
  the bakery, Finn's and Board Lords are at draft 1–2.
- **Vol 6 (the biggest volume, 64 presets):** `cosmic_comics_interior`
  (12) · `miller_kitchen` (12, a model chapter) ·
  `cosmic_comics_back_office` (11) · `maya_bedroom` (10) ·
  `kwik_stop_interior` (9, model) · `sam_bedroom` (9) ·
  `centro_grocery_aisle` (9) · `school_field_evening` (8) ·
  `kowalski_kitchen` · `vehicle_cab` · `henderson_kitchen` ·
  `caldwell_porch_night` (7 each).
- **Vol 5:** the six arcana sets ran D4 deep already; `diner_interior`
  is the model. Next is the primitive upgrade across all six plus the
  cathedral exterior the Magician now cuts to.
- **Vols 1–2:** `missing_link_interior` and `shuttle_bench` (8 each)
  carry vol 1; the Briar Falls set carries vol 2. Draft 2 after the
  vol 6–7 rooms.
- **The 71 single-use presets** get D2 + light only, in batches, from
  the sheet's worst frames.

**Ceiling raisers (user-gated):** Meshy hero objects, and — a decision,
not a default — painted SKY panoramas as the horizon band for
exteriors once an image key exists (a sky is an environment, not a
mesh texture; it needs the user's yes because it is the first painted
thing behind a 3D set).

---

## 4 · Pillar B · MODELS

**What exists and what is missing:** seven vol 5 GLBs; fifteen vol 6–7
busts; the demon models; `Portrait3D` with per-character lighting
rigs, per-mood camera, breath bob; static meshes (the camera does the
acting). Sam's GNM portrait is on disk and was shelved on sight.

**The three routes, and who does what:**

| Route | User's part | Claude's part | Look |
|---|---|---|---|
| **Mixamo / RPM** (the 2026-06-16 decision) | ~30 min per character; fifteen characters; the paint-by-numbers list in `godot/HANDOFF_CHARACTER_MODELS.md` | lighting rig per model the same day; `PORTRAIT_3D_KEY_TO_GLB` re-mapped | game-character; consistent with the vol 5 seven |
| **Meshy from a reference image** | approve one image per character (ArtCraft or any generator, or a described prompt) | queue → mesh → normalize → GLB → rig; can also pose | faceted low-poly, flat colour — the diorama look the locales already have |
| **GNM heads + lofted bodies** (resume) | none | re-run with the wardrobe tables; a draft tier so vol 6–7 stop being busts while the real route runs | stylized faceted; shelved once — only as a stopgap and only if asked |

**Engine work regardless of route (Claude, now):**
- The bust tier's draft 3 (the ledger row): raise the 60×64 base
  canvas, more shading ramps — it stays the fallback forever.
- `Portrait3D` acting: expression already drives camera + light;
  add a per-character IDLE table (head turn, weight shift) so a
  static mesh reads alive in a 43-line dialogue.
- Contact-sheet frames per GLB per expression, so a model's lighting
  rig is tuned from a picture, not a guess.
- A `CharLayer` two-shot rule: when two 3D portraits share the frame,
  key them from the same practical (the room's light, not each
  bust's own).

**Order:** Lena → Gable → Petra → Wren → Tem (vol 7 core), then
Kai / Per / Sal / Finn, then the vol 6 six. The route is the user's
decision (§8).

---

## 5 · Pillar C · DIRECTION

**What exists:** the whole grammar, and audits that hold it at zero
(inside_out, wrong_room, mood_clock, page_length, trip_fight,
marker_aim, obstruction). What is missing is the eye.

**Arc 0 first.** Then, from the sheet:
- **The taste pass per volume** — every establish and closeup seen;
  notes in the direction playbook's voice ("finn B too low"); draft 6
  of coverage cut from the notes. The next marker tier (5–6-use
  presets: foxhole_bar, henderson_garage, faust_bedroom,
  jesse_bedroom, centro_break_room, bianca_kitchen_morning, the diner
  variants) only after the tier above reads.
- **Camera language, three additions:** a TWO-SHOT marker type (two
  busts framed by one setup, keyed from the room's practical); the
  letterbox on `establish~` drifts (a P2 that costs nothing);
  through-window INSERTS as the D5 bands land (the sink light at
  4:32, the garage window E).
- **The model-chapter cut rate as the bar:** the 09-12 lesson on the
  43-line uncut dialogue — the seeder now rotates holds; the sheet
  will show which chapters still sit on one wide for a page.
- **Registers by chapter, not by locale:** `[register:domestic]` went
  on the Lovers and Temperance; the other six domestic-locale vol 5
  chapters are the user's call (§8) — the Star is a cottage and not
  cozy.
- **Beats and kinetic text** keep seeding at the lines that turn as
  chapters are reread; never in bulk.

---

## 6 · Pillar D · DESIGN

**The honest state:** the game grammar has one row per pillar and the
VN's own game layer has never been designed as a system. The
program treats design like the other three: a numbered draft per arc,
one row at a time, played on the Deck before the next.

**Status (2026-09-17) · the map is drawn and the first row shipped.**
`consequence_map.py` → `_VN_CONSEQUENCE_MAP.md` (28 choices, 5 checks,
58 flags, 43 loose). Headline: nothing ever raised a skill, so no
check could pass. SKILLS EARN, draft 1: options train skills (70
tagged), checks re-sized to the earnable, `vn_skill_audit.py` gates
at zero. Next: the loose flags paid off; the decorative checks given
a pass branch; the model-chapter verb coins.

- **The VN consequence map (Claude, now):** one document per volume
  listing every `choice`, `check`, `flag` and what it changes
  downstream — the thing VnSweep implied when it found dead checks.
  From the map: (a) every skill check pays off at least once per
  volume or is cut; (b) three-way choices where a volume has only
  binary ones; (c) the five skills get a face (a line of UI on the
  choice plate that says which skill is listening).
- **Verb coins on the four model chapters** (the bible's queue): the
  diner's jukebox, the kwik stop's back cooler, the cathedral's
  workbench, the Henderson stove — SHIPPED 2026-09-19 (all four) —
  and the INVENTORY the coins feed (`only_if_flag` already gates on
  it). Wrong answers funny, not fatal.
- **The gauntlet's tempo rows:** score bursts on chained rounds, tempo
  as the difficulty axis, a per-arcana high-score card — the card
  SHIPPED 2026-09-19 (THE CARD line in the reading, SaveSystem
  records); bursts Deck-gated; the bed for the seventeen arcana still
  on shared drones.
- **Community Planned:** the BBS masthead in the zine's hand; a
  reader letter that answers a `[trip:]` beat — SHIPPED 2026-09-19
  (RUST_CODE's masthead; RN_010 answers the 6:12 sprinklers).
- **The Salmonberry overworld (Wave A)** — the flagship gameplay build,
  fully Claude-side, "starts on your word" since 2026-08. It is the
  largest single design item in the project and the one the user has
  to greenlight (§8).

---

## 7 · The arc sequence

Each arc is roughly one Claude session plus one Deck run, and every
arc ends with the sheet.

| Arc | Backgrounds | Models | Direction | Design |
|---|---|---|---|---|
| **0 · THE LENS** | stale rebuild list | GLB × expression frames | the contact-sheet rig | — |
| **1 · vol 7 core** | cabin_interior, lena_apartment, salty_tome_alley: primitive upgrade + light + wear | Lena (route per §8) | vol 7 taste pass → coverage draft 6 | vol 7 consequence map; the cabin's second coin |
| **2 · vol 6 rooms** | cosmic_comics ×2, maya_bedroom, sam_bedroom, centro, school_field | Maya, Diego, Rick | vol 6 taste pass; two-shot markers | vol 6 map; the kwik stop's coin |
| **3 · vol 5 arcana** | the six sets through the primitives; cathedral exterior | (the seven exist) lighting re-tune from frames | vol 5 taste pass; the domestic-register calls | gauntlet tempo rows |
| **4 · vols 1–2 + the tail** | missing_link, shuttle_bench, briar falls; the 71 singles in batches | Gable, Petra, Wren, Tem | vols 1–2 taste pass | the Henderson + diner coins; inventory |
| **5 ·** | the next visit to every room above (draft N+1) | Kai, Per, Sal, Finn; the vol 6 six | next marker tier | Salmonberry Wave A when greenlit |

Then repeat from 1. "Dozens and dozens."

---

## 8 · Decisions the user owns (each changes the sequence)

1. **Character route:** Mixamo sessions yourself · Meshy from a
   reference image you approve · resume GNM as a stopgap tier. (Or
   two of the three.)
2. **A Meshy key** for hero objects — yes / no. If yes, the first
   queue is the SCUMM machine, the riverboat, Olaf's woodstove,
   Lena's easel.
3. **The image route** (gate 1): ArtCraft exports by hand, a direct
   key at `godot/tools/art/.image_key`, or neither for now.
4. **The contact-sheet flow:** PNGs under `godot/qa/contact/`
   committed to the branch (a few hundred MB over time; a separate
   `qa` branch is the alternative).
5. **Salmonberry overworld:** go / not yet.
6. **Painted sky panoramas** behind exteriors once an image key
   exists: yes / keep the horizon geometric.
7. **The six other domestic-locale vol 5 chapters:** which get
   `[register:domestic]` (Death yes; Hanged Man / Moon / Priestess
   maybe; Devil / Tower / Strength no — Claude's read, your call).

---

## 9 · What starts now, without waiting

- The contact-sheet rig (Arc 0).
- The vol 7 consequence map.
- The cabin's primitive upgrade + light + wear pass (draft 4), Lena's
  apartment draft 4.
- The bust tier's draft 3 and the Portrait3D idle table.
- The stale-build paste for the next Deck session.
