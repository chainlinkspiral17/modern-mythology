# GEOMETRY AUDIT PLAYBOOK

How the headless geometry gates work, why they are trustworthy,
and the hard-won rules for keeping them that way. Read before
touching anything in `godot/tools/audit/` or before believing (or
disbelieving) an audit report.

**The suite** (`godot/tools/audit/run_all_audits.sh`, all gates
must pass):

- `locale_geometry_audit.py` — reach/horizon/camera-preset checks
  (the STUMP HUNT gate) + `check_gate_position()` (no code after
  `if __name__` in builders).
- `prop_overlap_audit.py` — pairwise AABB interpenetration with
  the natural-contact grammar (THE CLIPPING HUNT gate). Zero
  regressions: any locale outside the recorded holdouts reporting
  ANY clip fails the suite.
- `preset_vantage_audit.py` — every Background3D camera preset
  must SEE its locale's geometry (60° cone, 150m).

## Core rules

### 1. A recorded object must survive being USED

The recorder stubs stand in for real Blender objects. Builders do
arithmetic on helper returns, read `.name`/`.data`, assign items,
index palettes with results. `locale_geometry_audit._obj_stub()`
returns a `_StubVal` (float subclass answering every attribute /
call / index / iteration) with the real `.name` pinned. **Any
"partial: <error>" line in an overlap run is a stub-fidelity bug
to fix THAT DAY** — a builder that crashes mid-main() silently
drops the rest of its geometry from the audit. Riverfront recorded
141 of its 4,639 objects for the audit's whole first life this
way; graustark and the diner measured through the crash-fallback
path too.

### 2. Hook EVERY geometry helper, including vendored ones

`record_builder()` rebinds `make_box`/`make_cyl` in the builder's
globals AND `_make_box_local`/`_make_cyl_local` (harmony_terrain's
vendored copies — before that hook, the game's BIGGEST locale
recorded ZERO geometry and its six highway9 presets audited
blind). A new builder with its own local helper names needs a new
hook line; a locale whose recorded-object count looks absurdly low
probably has one.

### 3. Calibrate the grammar against the MODEL CHAPTERS

When the diner (best-verified space in the game) reports 130
clips, the grammar is missing construction classes — the diner is
not broken. Funnels pass through decks; tubs sit in sinks; seats
tuck under counters; ruins are rubble. Tune until the model
chapters read near-zero, THEN trust reports elsewhere. Every
excuse is BOUNDED (tuck ≤0.30, wall-join ≤0.30, container-press
≤0.25) so waist-deep burial still reports.

### 4. The `\b`-before-underscore regex trap

`\b` does NOT match between a word char and `_` — `stud\b` misses
`Stud_W`, `band\b` misses `RedBand_W`, `hump\b` misses `Hump_W`,
`path\b` misses `Path_Spine`. Every token that can be followed by
an underscore needs BOTH forms (`stud\b|stud_`) or a bare token.
This trap has bitten at least five separate times.

### 5. Deep interpenetration (≥0.2m) has been REAL every time

The audit's precision record across ~40 locales of triage: every
pair ≥0.2m that wasn't an explicit construction class was a
genuine defect — story props entombed in solid geometry (the
Bishop's letter inside the nurse counter, cedar_tower's folded
clothes inside the bunk frame, three cemetery lecterns inside the
solid mausoleum), double-booked wall stretches (montreal's
bookshelf vs kitchen, kwik stop's ice machine vs mag rack,
riverfront's strip mall vs TWO silhouette passes), vehicles parked
through fixtures, and camera-invisible ground errors. Treat a new
deep report as real until proven construction.

### 6. Wheels are a bug MAGNET — check the circle plane

Three distinct paddlewheel bugs in one day: riverfront's wheel
circle in the XZ plane while its axle ran along X (blades swung
through the stern every revolution); the diner computed the
fore-aft circle offset and NEVER USED IT (all blades stacked in a
vertical column diving under the road); graustark's paddlebox
naming split from its hull. Any rotating assembly: verify the
blade/spoke circle lies in the plane PERPENDICULAR to the axle,
and name every part into one assembly prefix.

### 7. Later passes double-book earlier passes' ground

The single most common real-defect class: a new dressing pass
authored blind to what already occupies the wall/lot/skyline.
Prevention: before placing at coordinates, grep the builder for
what else stands in that x/y range — and run the overlap audit on
the locale BEFORE committing the pass. The zero-regression gate
now enforces this repo-wide.

### 8. Silhouette/backdrop layers get NAMED as backdrop

Distant composed scenery (far bank, skyline masses, horizon
hills) legitimately interpenetrates itself — the grammar excuses
BACKDROP×BACKDROP only when BOTH names carry a backdrop token
(oppo/far/shore/skyline/_mass/billboard/...). A near object inside
a far one still reports. When authoring a new backdrop band, use
those tokens; when a detailed building pairs with a "mass", the
mass is probably standing in the playable field (riverfront's
armory was).

### 9. Camera presets cite builder coordinates

A CAMERA_PRESETS entry names the blender coordinates of the hero
objects it frames, in its comment (graustark entries are the
model). `preset_vantage_audit.py` enforces the geometric half
(the cone sees something), but only the comment proves someone
aimed at the right something. Diagnosis order for "scene renders
flat/empty": (1) GLB timestamp on the Deck, (2) preset origin vs
builder coordinates, (3) shot markers.

### 10. Never bump a gate ceiling to make the suite pass

The holdout ceilings in `run_all_audits.sh` (crumpled_barn — the
crumple IS the overlap; the diner's ≤6cm ticket tucks) are
records of ACCEPTED reality, not budgets. A regression means: fix
the builder, or — for genuinely natural contact — extend the
grammar with a BOUNDED, commented class. The grammar is the place
generosity lives; the ceilings are not.

## Natural-contact grammar index (draft 14)

Same-assembly prefixes (+ `Roof_<Bldg>` aliasing) · wall embeds
≤0.14 · wall-join ≤0.30 · container contents (center-inside, or
press ≤0.25) · surface z-seat ≤0.10 · furniture kiss ≤0.14 ·
struct joints + fastenings ≤0.15 · stair members through uncut
slabs ≤0.40 · stack/funnel through decks+ceilings · crowns ≤0.35
+ crown-over-roof + crown×flex (swing ropes) · plant×plant,
plant×(wall|rock), plant-holds-post ≤0.45, foliage nestle ≤0.15 ·
rock×rock, rock roots in ground · nonsolid volumetrics (water,
pools, falls, liquid, spray...) · buried infra · grounded-object
rule (proud of a ground/road sheet = standing; roads conceal
what's beneath) · backdrop×backdrop · vessel superstructure ·
terrain-water-bank-dock interlock · pier abutments ≤0.75 · berms
absorb planted things ≤0.65 · wheels seat ≤0.30 · seats tuck
≤0.30 · porches/porticos ≤0.30 · flex lines + drapes ≤0.30 ·
offerings ≤0.10 · mirror collage ≤0.10 · pillows/cushions ≤0.12 ·
mounted fixtures ≤0.20 · shelf-stored ≤0.10 · pew contents ≤0.20
· cues lean ≤0.10 · ducts along bands ≤0.15 · collars ≤0.10 ·
closet tools lean ≤0.20 · fork-enters-pallet.

Added 2026-08-12 when the shared modules became visible:
openings installed in walls (a window assembly occupies the
full thickness) · fitted cabinetry backs into its wall ≤0.40 ·
framing members BEAR into the wall they land on ≤0.24 ·
fixture bases/kicks abut ≤0.22 · mounted hardware through
walls and pegboards ≤0.22 · cords run into walls (any depth) ·
neon letters through their raceway ≤0.30 · tipped furniture
below the floor plane · knee walls are wall-class · blinds and
banisters classed · pans as containers.

## Recent lessons

### 2026-09-22 · THE SUPPORT GATE — everything stands on something

- **The question is connectivity, not height.** `support_audit.py`
  unions every recorded box with every box it touches (3 cm on all
  three axes, overlap allowed) and grounds a component that holds a
  shell piece (floor · wall · ceiling · ground · road · slab) or a
  box whose underside is at z ≤ 0.03. Everything else floats. The
  report names each component by its lowest member, its z span, and
  the gap to the nearest shell — a 0.03–0.10 gap is a cord or a
  fixture built short; a 0.5+ gap is a thing dressed by coordinate.
- **The furniture gate's FLOAT rule was three lies.** Prop-sized
  only (a cabinet run off the wall passed), MOUNTED by name (a lamp
  named Lamp could hang anywhere), and EMBEDDED-in-a-solid counted
  as held. Keep FLOAT for what it does; the support gate is the one
  that answers the user's sentence.
- **The recorder had a hole a wire wide.** `catenary` is pure math
  in geometry.py; the stubs replaced it with 0.9, so every
  `make_tube(catenary(...))` recorded as a point at (0.5, 0.5, 0.5).
  Fence strands, power lines, chains: unmeasured by every gate for
  a month. Any helper that RETURNS DATA (not geometry) needs a real
  stand-in in the recorder, not the generic stub.
- **Regex parts, never substrings.** "ridge" ate the Fridge, "smoke"
  ate the Smokers_Tin, "floor|ceil" in the vantage IGNORE list ate
  the very shells this gate stands on. Anchor on `(^|_)word(_|$)`.
- **Baseline, then only down.** `support_baseline.json` holds each
  locale's count; the suite fails a locale that floats MORE. After a
  pass, `--write-baseline` lowers the line. Terrain locales are
  skipped (their floor is a heightfield the recorder cannot see).
- **"On what?" — dump the region before moving anything.** A float
  with a 0.3–1.2 m gap is usually not short, it is placed against
  a thing that is not there: the kwik stop's ATM detail dressed a
  machine removed in v2, the diner's Hierophant hung where a wall
  was removed in July, the bayou lighthouse's calendar and life
  ring hung at r 3.2 in a 2.4 m tower. List every recorded box in
  a metre around the float (`VO.boxes_for(locale)`, filter by bbox)
  and read what the builder THINKS is there against what is.
- **The foliage list must not name furniture parts.** "crown"
  (tree crowns) dropped Candelabra_Crown and Register_Crown, so
  their candles and finial floated no matter what the builder did.
  Whole-name parts are not enough when the word is shared;
  `TREE_CROWN` requires a tree word ahead of `_crown`. Same trap
  waits for "cap", "arm", "leader", "spray" — check the dropped set
  when a fix does not land.
- **Two clean model chapters set the kinds.** With the kwik stop and
  the diner at zero, the remaining 913 floats sort into four kinds
  seen there: dressed a phantom · off the counter's end · a hair
  short (2–6 cm: coin slots, LEDs, rope ends, spray heads) · the
  audit's own blind spot. Fix the third kind in the kit when the
  same helper made it (sprinkler anchors, fluorescents), in the
  builder otherwise.
- **Never borrow another audit's drop list.** The support audit
  used the vantage audit's IGNORE, written to keep floors and far
  bands out of obstruction counts: its `plinth$` dropped the
  sundial's plinth (so the dial floated), its `band` dropped the
  cedar tower's floor bands (so every glass band floated), its
  `far` substring was the only thing hiding FarTown_E0 as sky.
  Each audit owns its own lists, part-anchored, with a comment
  naming the thing each word is FOR. Each time a word came off a
  list here, one or two real floats appeared behind it.
- **A variable named like a coordinate is not one.** The riverboat's
  notices computed `px` from the board's X and passed it as Y —
  eight papers hung in the next room for a month. When a float's
  gap is "in another room", read the placement's arithmetic before
  its numbers.
- **The gates were forgiving where the eye is not (2026-09-22, user
  after five passes: "still getting pillows floating away from beds
  … not seeing much difference"; "objects inside other objects,
  too").** Two causes. (1) The GLBs are not in git: nothing changes
  on the Deck until `list_stale_builds.sh`'s printed rebuild line
  is run there — a pull plus a contact sheet renders the OLD builds.
  Say this in every report that touches builders. (2) The
  tolerances: a 3 cm touch let 1,644 gaps of 1–3 cm through (a
  pillow 2 cm over its sheet, a smoke detector 2 cm under its
  ceiling in 22 rooms, a register 5 cm over its counter in 8, fence
  boards 2.5 cm off the ground in 3 — kit helpers, all); the
  overlap grammar's embed 0.14 / tuck 0.30 / flex 0.30 / contents
  0.25 let a chair back 12 cm into a wall pass. TOUCH is 1.2 cm
  now, the grammar 0.06 / 0.20 / 0.15 / 0.15, and BOTH gates hold a
  per-locale baseline (`support_baseline.json`,
  `overlap_baseline.json`) that only comes down. A tolerance is a
  claim about what the player can see from a Deck seat; 3 cm was
  never true.
- **A subject marker judges a cluster centroid.** shot_insert_*
  markers cast at the centroid of the cue's parts near the nearest
  one; lowering a part (the jukebox's quarters onto its marquee)
  lowered the centroid under the bar top and failed a shot that
  had passed by a hair. When a support fix moves a hero prop's
  part, re-run `--markers` for that locale before the suite.
- **A name with "case" in it is not a container (eighth pass).** The
  overlap gate's contents rule exempted any pair where one name was
  container-ish and the other's CENTRE fell inside it — with no size
  test. So the grocery's 2.4 m meat case swallowed the checkout lane
  (the queue posts, the candy rack and the card terminal all stood
  inside it), the deli case swallowed the bakery counter, and the
  gate reported both rooms "clean". Contents are now under 1 m in
  every dimension and must FIT the container. When a gate says a
  crowded room is clean, dump the room's big boxes and look for two
  fixtures sharing a footprint.
- **The assembly key: an index joins it, a part name does not.** The
  same gate paired any two names sharing their FIRST segment as one
  assembly, so `Aisle_2` (a 4.4 m gondola) sat bodily inside
  `Aisle_0` unreported for its whole life. Keying on the first two
  segments over-fired the other way (Radiator_Fin_4 x Radiator_Body,
  Spinner_Tier_1 x Spinner_Pole — 1,361 clips). The rule that holds:
  when the second segment is an integer it is a family index and
  joins the key (`Aisle_0`, `Cooler_3`); otherwise the first segment
  alone is the assembly. 247 under that rule against 208 under the
  old — and the 39 were real.
- **Compile every builder after a batch, not just the ones you
  meant to touch.** Replacing the front of a one-line make_* call and
  appending a `# comment` swallows the rest of the arguments into
  the comment: three builders (school field, cedar tower, cosmic)
  went to SyntaxError this way in one session, and a fourth
  (vehicle cab) to NameError, and the audits reported each as
  "partial" or ERR — which a skim reads as a clean row.
  `python3 -m py_compile locales/build_*.py _props/*.py` before any
  audit; put the comment on its own line above the call.
- **A region dump cut by `head` is a lie about what is there.** The
  deli's second home was chosen from a W-wall dump truncated at 50
  lines — the produce island and the dry-goods run were below the
  cut, and the case landed inside both. Filter the dump by NAME
  (the big fixtures: Body, Base, Bank, Shelf_0) rather than by
  count, and read the whole thing.
- **Hangers must reach the head, not just the wire.** A stoplight
  whose stub stopped 6 cm above its top lens floated even after the
  pole and the arm were built; a planter whose wire stopped 3 cm
  above the pot rim floated with all six leaves. After tethering a
  thing from above, check the LAST link (stub → head, wire → rim,
  cord → device) before the first.
- **"Approximate" in a comment is a float waiting to be found
  (ninth pass).** Simon's armchair wear sat 1.5 m west of the
  armchair ("Approximate armchair at (-1.0, +2.0)" — it is at
  (0.5, 2.4)); the asylum's boarded cupola pane stood at the
  room's SOUTH end ("cupola at (0, 0) … we approximate") while
  build_cupola put it at the north; the non-renewal form lay on
  a kitchen counter at (+2, 0.6) in a room whose kitchenette is the
  west wall. A dressing pass that guesses another function's
  anchor is placing against a thing that is not there. Read the
  anchor from the function that built it, or dump the region.
- **A fix can UNCOVER floats the wall was hiding.** Simon's coat peg
  sat inside the south wall (embedded = "touching" = grounded), and
  its hanging boot swung outward THROUGH the wall — grounded by the
  same embedding. Moving the mount onto the wall's face turned the
  boot into two new floats, then a lace loop 10 cm short of its
  hook. When a fix raises the count, the new rows are usually the
  old defect's children, not a regression — chase them in the same
  batch.
- **A wall gap is a shell the audit cannot see.** The Roberts
  kitchen's south wall halves stopped 40 cm short of the door header
  on each side, and the door hinges hung in the hole; the bindery's
  Borges sign hung at y 7.8 where the west cases end at 6.9. Before
  moving a prop to "the wall", check the wall's box spans the spot.
- **The recorder could not see spheres (tenth pass, 2026-09-23).**
  It rebinds a hand-rolled builder's own make_box / make_cyl /
  _finalize_mesh, but not its make_sphere_low / make_sphere — so the
  diner's 27 spheres, the roberts house's bird and knobs, and harmony
  terrain's every canopy, globe and shrub were measured by no gate.
  The cost was concrete: asset pass 3 saw the diner's six booth
  lights "floating bare" and built a table lamp for each — INSIDE the
  ceiling pendant that was already there, whose shade centre sat
  exactly on the light. Once seen: 15 floats in the model chapter
  (bulbs 2–4 cm off their cups and shades, candle flames off their
  wicks, the expo bell off the end of the expo), a lamp pole planted
  in a berm tree's trunk, a stop sign inside a conifer, a lamp globe
  inside a street tree, a flower bed in the church's parking stalls,
  and a whole HOUSE standing in the middle of the skatepark (its
  body was never flagged: the skatepark's floor is a mesh). Any new
  vendored primitive helper needs a recorder hook the day it is
  written; grep `^def make_` in a builder against the hook list.
- **Judge a sphere as a sphere.** Recording a sphere as its cube
  fills the corners: a grass tuft outside a canopy's ball but inside
  its cube read as a clip. The overlap gate now measures sphere
  pairs by centre distance and sphere-box pairs by the nearest point
  of the box — exact, not an exemption. Prefer a sharper test over a
  new name rule whenever the false positive is geometric.
- **A kit's return value is a placement for everything after it
  (twelfth pass).** `make_counter` returned its top as base+height
  +0.04; the slab ends at +0.06. Every register, bell and paperback
  dressed from it in 22 builders sat 2 cm INSIDE the counter, and
  neither gate could see it: the support gate calls embedding
  "touching", the overlap gate forgives 10 cm of "resting on a
  surface". When a helper returns a surface height, test it against
  the box it built — `top_z == box top` — the day it is written.
  Fixing the return lifts exactly the things placed from it; the
  few hand-tuned to the wrong value then hover, and the support gate
  names them.
- **A kit's axis is not the caller's assumption.** The counter kit
  runs its length along Y; chillwave dressed it as if along X — the
  register stood off one side, the bell off the other, the kick
  scuff ran across the counter's body. When a float sits a fixed
  distance off BOTH sides of a fixture, check the fixture's axis.
- **A wall can be holding things up that should not need it
  (thirteenth pass).** The pit stop's lot cars sat 10 cm INSIDE the
  building's west wall from outside; moving them clear made them
  float, because they had no wheels — the wall was their support.
  Same for the courthouse wainscot (built inside its walls) and the
  bungalow's closet boxes. When a clip fix turns into a float, the
  clip was hiding a missing support.
- **A scan finds candidates; each one still needs its room read.**
  A static scan for "a slab centred on the height its dressing is
  placed from" found seven builders. In two the dressing really was
  buried half a slab deep; in five the author had already added the
  half-thickness, and "fixing" the slab left everything hovering 3
  cm — the support gate caught it and the five were reverted.
- **Dressing placed for a fixture's OLD position survives the move.**
  Diego's desk moved to the north wall on 09-07; the laptop and the
  letter "on the desk's SE corner" stayed at the old coordinates in
  mid-air for two weeks. When a fixture moves, grep for everything
  that names it in a comment.
- **Compile inside the batch script, not after it (fourteenth pass).**
  The trailing-comment trap struck twice more; a batch's `rep()` now
  runs `py_compile.compile(path, doraise=True)` after every file it
  writes, so a broken builder stops the batch at the line that broke
  it. And a text block inserted into a loop must match the loop's
  indentation: an 8-space legs block dropped into a 12-space chair
  loop gave only the last chair legs and moved its back into the leg
  loop — the support gate caught it as "chair 0 still floats".
- **Furniture without an underside is the commonest float left.**
  Chairs as a seat and a back (cafe olimpico), shelves without sides
  (new orleans office), a rack's shelves without a frame (gym), a
  pedestal seat with no pedestal (pulldown), a guitar stand that is
  only a foot. When a float's lowest member is a seat or a shelf at
  its working height, the fix is the missing part, not a nudge.
- **A tabletop is not sky.** `template_land|template_sea` sat in the
  support audit's SKY list, so every model on the estuary 7 diorama
  (cedars, rivers, labels, the cursor) read as floating. A drop list
  entry needs the name of the thing it is FOR; that one had none.
- **"Into the wall" can mean "facing the wall" (fifteenth pass).** The
  overlap gate reported the Centro break room's fridge 16 cm into the
  N wall. Looking closer: the counter, the upper cabinets and the
  fridge all put their doors and pulls on the WALL side (`cx - 0.24`),
  and the whole run stood 8 cm inside the W wall. When a clip says a
  fixture is inside a wall, check which side its fronts are on before
  nudging it out.
- **A solid block with something inside it is a case with no inside.**
  The crumpled barn's automaton cabinet was one `Cab_Body` box, 1.9 m
  of solid wood with Jiggles hanging inside it — eight clips. The fix
  is to build the case hollow (base, back, sides, head), not to move
  the puppet.
- **`make_rot_box` pitch turns about local Y.** Sam's skateboard used
  `pitch` to "lean on the wall" and tipped over sideways instead, 10 cm
  off the wall with its trucks on air. To lean something against a
  wall that runs along X, use `roll` (about X); along Y, `pitch`.
- **When the prose names a surface, check the surface was built.**
  Finn's crow sat "on the south sill" with five sill marks around it;
  the window kit had built a frame in the wall and no interior sill,
  so the crow's marks were on air. New Orleans room's letter, pen and
  envelope sat at the desk's old x after the top moved 1.1 m.
- **A kit with a fixed build direction is right for half the walls
  (sixteenth pass).** `make_window` built from its anchor toward −Y
  (or −X): toward the room on a north or east wall, INTO the wall on
  a south or west one. Callers anchoring on the wall's centre line
  buried theirs on any wall. 43 windows in 34 rooms were invisible
  from inside — no gate could see it, because windows are WALLISH
  (embedded on purpose). The scan that found them asks a different
  question: is any window's GLASS wholly inside a wall solid? A kit
  that places things relative to a wall takes the room side as a
  parameter (`room_dir`), never assumes it. And a window on a solid
  wall is a panel, not a view: when a shot is written THROUGH a
  window (the cabin crow), the wall needs a real opening — and the
  lens audit must treat glass as see-through, or the first honest
  window reads as an occluder.
- **"clean" over a broken builder.** When a builder's main() raises
  under the recorder, it falls back to running each build_* alone —
  coverage survives, every part is recorded twice, and the gate said
  "clean". The riverboat's main() had a NameError from a renamed
  variable; the Deck build would have died. The suite now fails on
  any `(partial: …)` line. Watch the object count: it doubled.
- **An assembly key must survive both naming habits.** Index second
  (Aisle_0, Drum_0_band) and index last (NapkinDispenser_Slot_8) both
  occur. The ≥3-segment rule made two-segment siblings one assembly
  (blind to Aisle_0 inside Aisle_2) and a numbered whole a stranger
  to its own parts (Drum_0 vs Drum_0_band, a false clip). The fix
  pairs a BARE numbered whole (X_N) with any part carrying N, and
  checks the repo-wide deltas for both a rise AND a suspicious fall —
  a first try hid two real Kwik Stop clips by matching the upright's
  own index.
- **Once a kit is caught hiding things in walls, scan its siblings
  (seventeenth pass).** The window kit's fault had a twin in the
  wall kit: the baseboard was 6 cm thick centred 6 cm off the wall's
  centre line, so it sat inside every 20 cm wall — 398 of them, in
  79 rooms, since the kit was written. The scan is the same shape:
  "is `<X>_Base` wholly inside `<X>`?" And the fix has the same two
  halves: the kit puts the part ON the face, and a side check
  (room centre vs wall centre) flips every call whose sign points
  out of the room. Hand-copied patterns (the 0.06/0.06 baseboard in
  the kwik stop and three spandrels — and one written this session)
  need a grep for the old numbers too.
- **A re-aim tool aims at the nearest NAMED part, not the prose.**
  marker_reaim.py swung the vanity-mirror insert down 57° onto a
  drawer pull because the pull was the subject it resolved. Read every
  re-aim diff; revert the ones whose new subject is not the shot.
- **Two builders, one spot (eighteenth pass).** The kwik stop had
  two Slurpee machines — the coffee station's twin barrels and
  build_slurpee_fountain — built into each other, and an end-cap
  pyramid built on the aisle's end-cap shelving. Each "held the other
  up": remove one and the other floats (the fountain was 27 cm over
  its counter). When a clip is between two things of the same KIND
  from different build functions, one of them is a duplicate.
- **An exemption written for one pair excuses every pair (nineteenth
  pass).** "Closet tools lean together and against the bench" let a
  broom or mop overlap ANYTHING by 20 cm — so the kwik stop's broom
  stood through the break bench unflagged. Write an exemption for the
  pair it was meant for (tool vs tool), and name the new ones narrowly
  (creek_stone, not stone; sprinkler vs lawn, not sprinkler).
- **A ground sheet can hide what is cut into the ground.** New Auburn
  Road's 2.6 km far-ground sheet at z -0.06 lay over both roadside
  ditches (which bottom at -0.40) — the ditches were never visible. The
  overlap gate called it "ground x ditch, 7 cm". When a depression
  clips a ground plane, the plane is on top: cut the plane.
- **Record the shape the kit BUILDS, not the one its name suggests
  (twentieth pass).** make_blob recorded as a round ball of `radius`;
  the kit squashes it (default 0.8) and pushes noise outward. Two
  failures from one stub: false clips (a flat duffel "13 cm into the
  floor") and hidden floats — every blob seated at centre = radius
  hangs radius x (1 - squash) over its ground, and the ball's extra
  height was "touching" it. The recorder now runs the kit's own vertex
  ring. When a stub approximates a kit, check it against the kit's
  vertex maths once.
- **A gate that stubs the engine cannot see the engine fail.** Every
  audit ran builders under recorder stubs that take any arguments, so
  two builders that died in Blender (a mid-call comment swallowed
  make_cyl's colour) passed everything for eight passes while the Deck
  quietly skipped their GLBs. blender_dryrun_audit runs the REAL kits
  against a stand-in bpy and fails on any exception. And an automatic
  "re-vantage" can pick a spot outside the building — no obstruction
  out there; read what it chose.
- **A drop list hides a kit's bug in every caller at once.** The first
  read of the contact sheet showed flat slabs floating in the sky; the
  support gate said zero, because "far" was in its SKY list. The far-
  band kit had passed half-extents as sizes since it was written: every
  horizon band on 37 exteriors stood a quarter of its height off the
  ground, every crown hung over its band. Read the frames — a gate
  that exempts a word is blind to everything named with it. And when
  you ground something that used to float, check what it now stands
  in: the riverfront's grounded north band was a wall across a road.
- **"Wholly inside one segment" misses windows at a segment's end.**
  Elicia's SE window ran past Wall_S_E's end into the door opening, so
  the first buried-window scan passed it. The scan that holds: glass
  inside the wall's THICKNESS and overlapping it along the run and in
  height. Three more found.
- **Move the light with the lamp.** Jesse's bedside lamp moved 1.3 m;
  its practical OmniLight in the .tscn would have lit an empty corner.
  orphan_practical_audit catches it — and it also caught the reverse:
  a practical authored on a KELP float, because the name had "Bulb".
- **A back bar is not a block.** The riverboat's back bar was one 2 m
  solid with the mirror on its face and sixty bottles inside it; the
  overlap gate never saw them, because bottle and body share the Bar_
  assembly. When the object count of a family is high and its
  container is a single solid, look inside.
- **A key light is a direction, and nobody reads it (twenty-second
  pass).** 32 key / sun / moon / overhead DirectionalLight3Ds in 31
  scenes shone UPWARD — the transform's forward (−Z) had a positive Y
  (in a row-major .tscn basis the light's Y travel is −m12). They lit
  ceilings and the undersides of things; floors and faces went dark,
  and the night mood's 9-level quantise crushed those rooms to black
  frames on the contact sheet. light_direction_audit.py now gates it
  (nonzero on any key-named directional with Y travel > 0.05).
  contact_frame_screen.py (report only) lists near-black and one-flat-
  colour frames from a sheet, so the next read starts from a list.
- **"Offset from the wall" means from its FACE.** ~15 hand-built
  windows in 14 builders set frame and glass a few cm off the wall's
  CENTRE line — inside the wall, invisible (the window kit had been
  fixed in the sixteenth pass; these were hand-built). And a SOLID
  frame slab in front of the glass reads as a blank panel (the New
  Orleans office): frame a window with four bars, glass just in front.
  When a window moves, move what hangs off it (Faust's curtain rod
  was left standing 8 cm off the wall — it has brackets now).
- **A gate's exit code is the last command in its pipe.** The suite's
  marker_aim block was `AOUT="$(audit | grep -v …)" || fail` — grep's
  status, so it could never fail, and four misaims rode through two
  suites. Capture the audit's status first, filter second (fixed there
  and in orphan_practical). Test a new gate by making it fail once.
- **Cameras do not follow props.** The twentieth pass moved cedar
  tower's ESTUARY 7 poster onto the E wall; its two markers kept
  filming the door gap where it used to hang. Moving a hero prop: grep
  its shot markers. And marker_reaim aims at the nearest NAME match —
  read the story before trusting it (the riverboat "card" is Dean's
  calling card on the helm desk; the audit's nearest match was table
  14's reserved tent).

### 2026-09-06 · a builder that raises under the recorder is dropped without a flag

- **"0 flagged" can mean "not measured."** locale_geometry_audit runs
  each builder under the stubs; if run_path raises, the builder goes
  to an `errs` list and is skipped — it never appears in the table,
  and nothing in the summary says so. The DINER, the quality bar, had
  been in that state for its whole life: its vendored helpers raised
  under the stubs. The make_box delegation shim (detail draft 3C)
  happened to make it runnable, and the FIRST measurement flagged it
  ("exterior view stops at 69m" — the storefronts across River Road
  and then nothing). A river-town horizon fixed it in one call. Two
  builders still record zero boxes (harmony_district, harmony_terrain
  — heightfield terrain through bpy directly); they are unmeasured,
  not clean. Print the errs. Treat an absent row as a failure.
- **The chamfer policy lives in ONE make_box; vendored copies must
  delegate.** Fourteen builders carried their own make_box. Until
  they routed through _props.geometry, the de-blocking policy could
  not reach the model chapters — the sets players see most. A
  vendored helper is a fork of the pipeline; keep the fork as a
  fallback and the shared function as the path.
- **Kit swaps must keep the marker names.** The furniture kit names
  its parts <prefix>_Top / <prefix>_Leg_N; calling it with the old
  prefix ("Table", "Chair_2") keeps Table_Top and Chair_2_Seat, so
  every existing marker and synonym still lands after the swap.

### 2026-09-03 (evening) · the obstruction audit; the roads; cars were invisible

- **"Sees its locale" is not "sees the set."** preset_vantage_audit
  counts geometry inside the cone; a wall IS geometry, so the cabin's
  opening wide (camera inside the bed alcove, the partition across
  75% of frame) and Elicia's bungalow (a closet across 60%) both
  passed. vantage_obstruction_audit.py casts a 9x3 ray fan and fails
  a vantage on near-fill (a third of the frame within 1 m), a single
  surface owning the middle row within 2.6 m, or a camera INSIDE a
  box. 21 of 153 presets failed on its first run. It is a suite gate.
- **The "just inside the door" template put three kitchens inside
  the fridge.** kowalski / caldwell / ramos share a plan (fridge on
  the E wall at x 2.1..2.8) and all three presets copied the same
  "SE quadrant" origin at x 2.1. When a vantage is copied between
  sibling sets, cast it — a copied comment is not a survey.
- **The proposer needs an escape penalty.** The first --propose pass
  maximized depth and picked "median 200 m, 0 distinct" for half the
  flagged presets — views through a doorway into the void. Depth
  counts only where a ray lands on something; escaped rays cost.
  Even so, read every proposal against the preset's comment: three
  presets (the cab's dash, the rear bench, the dock end) are near-fill
  on purpose and live in the audit's DELIBERATE set.
- **A new _props module is invisible until it is whitelisted.**
  make_car() lived in _props/vehicles.py for a day without being on
  locale_geometry_audit's recorder whitelist: no car clipped, no
  marker could aim at one, and the substation truck marker found a
  van 200 m away. Add the module name the moment a helper is
  promoted.
- **One road per region, and a different camera per stretch.** vol1,
  vol2 and vol6 all rendered the vol5 Louisiana swamp road from one
  breakdown-lane vantage. The split (louisiana / new_auburn /
  small_wood / highway_101) is only half the fix; the other half is
  that every preset on a road set is a different place, height and
  lens — hood-low behind a car, seated in a lot, handlebar height on
  a verge, the ditch, the gate. A road preset at eye 2.3 looking
  north is the default that made them all the same.

### 2026-09-03 · re-homing draft 2: four locales from prose, zero-clip first pass

meadowlark_circle, vehicle_cab, lake_palestine, estuary_7_template —
each authored in one sitting against the zero-regression ceiling.
Lessons:

- **Hollow bodies are a stacking exercise: every plate TOUCHES its
  neighbor, nothing intersects.** The cab was designed on paper as
  z-bands first (pan 0.30..0.40, floor 0.40..0.46, belt line 1.20,
  roof 1.72) and x-bands second (shell ±0.90, skins ±0.90..0.925,
  glass ±0.905..0.925, wheels ±0.94..1.20). Write the bands down
  before the first make_box; the audit is EPS 1.5 cm and a 5 mm
  overlap is a clip. The lake's truck, dock and cleat were checked
  the same way on review and four latent clips (headlight inside
  the grille, stringers through the abutment, rust decal under the
  cleat base, rope through the plank) came out before the build.
- **Water is a slab; ground goes UNDER it, shores go BESIDE it.**
  A lake at z −0.10..−0.02 over a Ground_Far at −0.09..−0.07 is a
  full-plate clip. Stack them: Ground_Far below the water bottom,
  the two shores as separate plates at water height on either side
  of the cove, pilings and boat hulls standing ON the water top.
  Trees on the shore plates, not over the water.
- **make_gable's `center` is the bounding-box center, not the base.**
  The diorama's ridge at center z = land top sank half its height
  into the land and the plinth (2 clips). Roofs on named bodies are
  forgiven by the natural-contact grammar, which is why the same
  mistake on Cabin_Roof / Marit_House_Roof never showed — lift them
  anyway.
- **Never re-serialize a scene JSON to re-point it.** json.dumps
  with the file's apparent indent rewrote four vol6 scenes wholesale
  (3,800-line diffs). Splice the literal `"3d:<preset>"` at the nth
  occurrence in the raw text; verify with json.loads and a bg-node
  read-back. Inserting a node the same way (the submission's cabin
  bg) means copying node 0's raw block, not dumping.
- **The godot z sign flips on the way back from a builder.** The
  meadowlark van marker was authored at godot z −22.5 for a van at
  blender y −26 (godot z +26): 46.8 m away, aimed at nothing. Convert
  every marker from blender coordinates on paper — godot z = −by —
  and read the reaim distance line: anything over ~10 m on an insert
  is a sign error, not a long lens.
- **Off-frame subjects get a glyph, not a blind.** Eugene and Bandon
  are "off the template's frame"; the substrate-lines run to the
  frame edge / the ridge foot and end in a glyph named for the cue
  (Foundation_Glyph, Cove_Glyph), so the insert has a thing to
  frame. Bern (the press) has no line in the prose — deliberate
  blind.
- **A re-point can land a cue in the wrong room.** ch22_foxhole 168
  looked like a Civic beat ("he gets in the Civic") but its cue is
  the strip-mall unit across the lot — read to the next bg before
  re-pointing, not just the first line.
- **A blind cue on a fresh preset may be the scene's fault, not the
  set's.** meadowlark_circle_night showed three new blinds (map,
  Polaroid, envelope) the moment the codas landed on it; the fix was
  not three props on a sedan dash but a bg node — ch3_coda's
  interlude line is the street, and everything after it is Rick at
  the Cosmic Comics desk. When a new blind cue names something that
  does not belong outdoors, grep the segment for a room before
  modeling.
- **Parked vehicles want a helper, not a copy.** meadowlark's
  make_car() (body / cabin / glass plates outside the cabin /
  wheels outside the body, pickup + light-bar variants) is the
  third hand-built car in two days; the cab, the lake truck and the
  vigil sedan each re-derived the same non-intersecting bands. Next
  car goes through the helper or promotes it into _props.
- **A hole is a grid with a cell left out.** There is no subtraction
  in the builder; the tide pools are a 5x5 cell grid with two cells
  missing, each hole floored below and skinned with a 12 mm water
  plate at the top, the creatures standing on the floor UNDER the
  skin. Nothing sits inside a water box, so nothing clips, and the
  camera reads a pool through a translucent surface.
- **A wedge is its bounding box to the audit.** Anything resting on
  a slope — a rock on the drop wedge, a groove on the ramp slab — is
  inside the wedge's bbox and reports as a clip. Dress slopes with
  decals ON the flat neighbor, or don't dress them.
- **Two scenes over one glb need the tools to know it.** A second
  tscn (tideline_survey_second) over a shared glb was invisible to
  marker_aim + reaim because they resolved the builder from the
  scene's basename; geometry_godot now falls back to the tscn's glb
  reference. Use the pattern whenever one cue id must frame two
  different objects in one locale.
- **Name the cue's neighbors away from it.** The basement door's
  jambs were Basement_Door_Frame_L/R, so the "door" cue's NEAREST
  hit was a jamb 43° from where the door was; renaming them
  Basement_Jamb_* made the door itself the nearest hit. When a cue
  id is a common noun, keep it out of the names of the parts around
  the hero.
- **A blind cue over an existing prop is a matcher miss, not an art
  gap.** [shot:insert wooden_box] sat blind for a month while
  PersBox_* stood on the bakery bench: "wooden_box" is a multi-word
  stem, so it substring-matches "woodenbox" and nothing else. Run
  `shot_marker_audit.py --props` and READ the builder for the noun
  before modeling; a synonym line and a marker is the whole fix.
- **A slug line is a bg node that hasn't been written yet.** The
  interlude's "[ LENA — apartment above The Salty Tome ... ]" was the
  cue that the location changed; the scene never carried the bg. When
  a chapter uses bracketed slugs, every slug wants a bg after it.
- **The exterior threshold is a bbox, not a sky.** locale_geometry
  calls a locale outdoor when its bbox exceeds 40 m on a side and
  then wants a 120 m horizon; a 40.6 m hallway-plus-basement got
  the "exterior view stops" flag. Keep interiors under 40 m or give
  the audit a ceiling test (queued).

### 2026-09-01 · the blind-cue hero-prop program (six locales, 324 → 277)

Board Lords, lena_apartment, hans_bakery_back_kitchen, graustark
(star night), miller_kitchen, ramos_kitchen_morning — one method:
grep the cue's prose anchor, build the prop with names the matcher
hits, append transform-format markers with rotation zero, run
marker_reaim, run the suite. Lessons:

- **position-format markers are INVISIBLE to the marker tools.**
  `parse_markers` requires a `transform = Transform3D(...)` line;
  a `position = Vector3(...)` node is skipped silently — no aim
  audit, no reaim. lena_apartment carried five legacy markers the
  audit had never once checked (bakery has brotchen/mixer/establish
  in the same state). Author new markers transform-format ALWAYS;
  a repo-wide conversion of the legacy position markers is queued.
- **Synonym ties need decisive placement.** "window" accepts the
  stem `win_`, which matches `WinChair_*`; the bakery window
  marker's nearest-match race came down to 0.84 m vs 0.85 m and
  aimed at the chair. When a cue's synonyms are broad, place the
  marker so the intended subject wins by half a meter, not a
  centimeter.
- **Human contact renders as residue, not figures.** "hands"
  cues (five of them across three locales) became floured
  handprints on the baker's table and hand-worn patches in two
  family tables' finish — use-state grammar (D4), zero figure
  geometry, and the marker aims at the exact spot the beat
  happens. Name the residue with the cue's token (`Hands_*`).
- **A shared-world tscn clears sibling presets at once.** The
  four graustark star-night markers took the repo count down 11,
  not 7 — wall/crow markers also unblinded the chalk-wall and
  ruins presets that stage the same objects.
- **Check tower footprints before dressing a deck.** The
  lighthouse's ground segment owns a 3.6 m square of the deck the
  dump's center coordinates don't advertise; the desk vignette's
  first placement put both brick stacks inside it (7 clips).
  When placing near any tall structure, read its BASE extents
  from the builder, not the audit's center-point dump.

### 2026-09-01 (later) · eleven more waves; the matcher's exact-part rule

The program continued to 213 blind (from 324 at start of day):
pit_stop_interior, kwik_stop, daily_grind, houston_office,
graustark world-shore, nightmare_cell, nexcorp_gas_go,
sam_bedroom, school_field_evening, miller_back_porch,
henderson_garage. New lessons:

- **matches_for compares name PARTS exactly** (split on `_`);
  multi-word stems substring the flattened name. `HouseDoor` is
  ONE part and invisible to the "door" cue (renamed House_Door);
  `Finn_Toyota_Body` had no "truck" part (renamed Finn_Truck_*).
  Name every prop so the cue's word is its own `_`-separated
  token — or add a SYNONYMS entry (steamship→minstral,
  folding_chair→eileen_chair, drum_kit→kick/snare/hihat shipped
  today).
- **reaim's 1.6m cluster centroid can drag an aim sideways.**
  The kwik stop window marker's cluster swallowed the WinChair
  backs ("win_" synonym) and yawed the camera 90°. When synonyms
  are broad and furniture crowds the subject, park the marker
  close (0.3-0.5m) and, if reaim still fights, hand-set the
  rotation — the aim audit only checks the NEAREST hit's cone.
- **Respect explicit negative canon.** The nightmare cell's
  window cue tempted a dream-window; the builder docstring says
  "The room has no windows." A cue whose beat happens ELSEWHERE
  (a memory, another city) stays deliberately blind — VnDirector
  holds the wide. closeup_douglas and the cell window are the
  precedents.
- **human_figure geometry is invisible to the audit stubs** (all
  53 graustark NPCs record zero objects). A figure placed for a
  closeup needs audit-visible RESIDUE beside it (the Child's
  footprints/stick/crawdad hole) or the marker has nothing to aim
  at in-container.

### 2026-09-01 (sixth) · re-homing: the road aggregates were hiding real rooms

- **Survey by bg segment, not by cue.** Splitting each scene at its
  `bg` nodes and reading the first two prose lines of every
  road-staged segment sorted 61 segments into: real rooms that
  already existed (bakery, cabin, cedar tower, henderson porch,
  cosmic front door), one preset that already existed and nobody
  was using (salty_tome_alley — vol7's climax wall), two places
  worth building (Cape Perpetua, Main Street), and honest drives.
- **Presets are cheaper than locales.** Main Street is a camera on
  the Board Lords set's existing street plates plus one dressing
  pass; the alley was a preset with no scenes pointed at it. Check
  Background3D for a usable preset before opening a new builder.
- **A re-point moves its cues.** salty_tome_alley went 0 → 16 blind
  the moment nine scenes landed on it; budget the prop pass with
  the re-point, not after.
- **make_blob radii lie by ~30%.** Salal mounds placed at nominal r
  clipped the trail and the platform edge (five clips); keep blobs
  a full radius clear of anything you care about.

### 2026-09-01 (fifth stretch) · the 1-cue tail; the program's end state

Seventeen single-cue presets cleared (blind 85 → 68). Every
remaining blind cue is now one of three deliberate kinds:
(a) the two fallback-staging aggregates — cabin_road 43 and
louisiana_road 18 — which are a RE-HOMING decision, not a prop
wave; (b) cast closeups of characters with no char id
(coach_dale x2, douglas x2); (c) beats that happen in another
locale or on a person (the cathedral charcoal, the bar tattoo,
the cell window). The shot_marker count will not go to zero by
building props, and should not.

- **Seven of seventeen were already built** (the open book, the
  tower, the camera, the mirror shard, the set list, Mister the
  cat, the paper coffee cup) — three needed only a synonym
  (mirror → mirrorshard, photograph → print). Survey first.
- **A solid vehicle cabin puts the phone on the hood.** When the
  prop's true seat is inside a solid body and the body is not
  worth hollowing for one insert, put the prop where the insert
  can see it and say so in the docstring.
- **Shared-builder locales (diner = dambrosios_formal) map through
  Background3D, not by preset name** — the mapping regex in the
  survey script is the only reliable way to find the tscn.

### 2026-09-01 (fourth stretch) · cabin, the 3-cue and 2-cue tails

cabin_interior (15 cues), henderson kitchen, finn apartment, six
3-cue presets, twenty 2-cue presets — blind 171 → 85. Lessons:

- **Adding a far prop can flip a view into an EXTERIOR.** The
  stockroom's dock preset passed the stump hunt for a month; one
  translucent smear band 60m out made the audit class it exterior
  and demand a horizon ("view stops at 76m"). Any distant-band
  prop needs the full exterior kit with it: Ground_Far + receding
  make_far_bands on the open side.
- **NEAR_MAX is 40m for inserts.** A "far horizon" subject must
  still sit inside 40m of its marker or the aim audit calls it a
  miss (the smear went from 60m to 34m).
- **Hollow bodies for vehicles with visible interiors.** A seat or
  a dash inside a solid car box is a clip; build pan + sides +
  hood + roof as separate boxes and the interior props sit in
  real air (Doyle's sedan dash, the Subaru's quilt seat).
- **Half the tail was already built.** Fifteen of the thirty-eight
  2-cue cues had their prop standing under a name the matcher
  couldn't see (Guitar_ for telecaster, Bench_ for workbench,
  MorseKey_ for radio, Helm_CallingCard_ for card). Survey
  matches BEFORE writing geometry; a synonym line is the fix.
- **The stub can't see human_figure, so a figure's closeup needs
  residue** — and a cast closeup of a character with no char id
  (coach_dale) stays blind on purpose, like douglas.

### 2026-09-01 (third stretch) · the tail waves; four more tool truths

Eleven more presets cleared (natalie, bianca kitchen, montreal,
maya bedroom, new orleans bar, centro break room, kowalski, jesse
bedroom, both salty tome presets, the bakery's hidden three, the
cathedral) — blind 213 → 171. New tool truths:

- **The default cue listing truncates at SIX per locale.** The
  bakery "cleared" wave left three cues standing (brioche /
  coffee / bag) that only `--all` shows. Always open a locale
  with `--all`.
- **"tv" is under the matcher's 3-char stem floor** — the bar's
  existing Bar_TV was invisible to its own cue; a duplicate TV
  got drafted before the cause surfaced. Short cue ids need a
  SYNONYMS entry (tv → bar_tv), not new geometry.
- **Existing props answer more cues than expected** — the
  Telecaster was Guitar_*, the folding chair was Eileen_Chair,
  the floorboard station was already built in maya_bedroom, the
  salty tome cat was Cat_Loaf. Grep the geometry before building;
  five synonyms shipped today instead of five duplicate props.
- **The model chapter's builder (tools/blender/, BUILDERS_ALT) is
  invisible to geometry_godot** — cathedral markers must be
  hand-aimed and cannot be aim-audited. Teaching the recorder
  that path is queued.

### 2026-08-19 · a marker IS a camera; three blindness bugs in one day

- **A vn_shot marker's transform IS the camera pose** (VnDirector
  assigns `marker.global_transform` to the camera; Godot cameras
  look down −Z; yaw 0 faces −Z, yaw π faces +Z). A whole wave of
  hand-authored insert markers shipped with INVERTED YAW — the
  miller phone marker faced 180° from the phone, the eviction
  notice 179°, both crows ~170° — framing the opposite wall on
  every cue. Hand-deriving yaw from coordinates was the failure;
  `marker_aim_audit.py` (now a suite gate) computes each marker's
  forward cone against the recorded geometry and found 22 real
  misaims across 11 locales. A re-aim pass recomputed every bad
  rotation from the subject's actual position. Never hand-derive
  a camera angle again — author the position, let the tool aim.
- **The audit's own first verdicts were wrong twice.** (1) BOXES
  rows are `(name, CENTER, half_sizes)` — reading them as
  `(lo, hi)` and averaging halved every coordinate, so the first
  run measured a world at 50% scale and called well-aimed markers
  190m off. (2) Substring matching let "crow" match "Crown" and
  picked wrong subjects. Exact-part matching + center fix took the
  misaim list from 44 (half phantom) to 22 (all real).
- **record_builder never patched IMPORTED build_* modules.**
  graustark does `import build_harmony_terrain as ht` and runs
  most geometry through `ht._make_box_local` — the g-rebinds only
  touch the exec'd builder's own globals, so graustark recorded
  114 of its 8,641 objects for its whole audited life. Patching
  every `sys.modules` build_* entry opened the eyes a THIRD time:
  graustark 114 → 8,641 objects, 0 → 89 clips → triaged to 0
  (a power pole inside the Lacombe garage, the rectory ON SR12,
  the garage parcel ON the SR12 centerline, two ruin shells in
  the truss-bridge corridor, a palm through the courthouse, the
  statue on its own lamp ring, the cane plot swallowing the
  Lovers chapel, herbs through the lighthouse deck). Rule 2 now
  has three known scopes: function, module, AND import.



### 2026-08-12 · the audit could not see the SHARED modules (rule 2, at module scope)

- **Core rule 2 said "hook every geometry helper." It was true at
  FUNCTION scope and false at MODULE scope.** `install_stubs()`
  executed only `_props.detail` and `_props.trees` for real;
  everything else in `_props/` was replaced by `_Any`, whose
  `__getattr__` returns a recorder only for the eight primitive
  names. So every COMPOSITE helper — `make_wall`, `make_floor`,
  `make_window`, `make_counter`, `make_bottle`, `make_cooler_row`,
  and (once written) `make_drone` / `make_crow` — was a silent
  no-op. **The audit had never seen a single shared-module wall.**
- Discovered by accident: three crows placed in three locales left
  the object counts unchanged (76 → 76). Widening the whitelist to
  every composite module took finn_apartment from 76 to 195
  recorded objects and the repo from 18 clips to 286.
- **What that blindness was hiding:** eleven `make_window` calls
  passed `center_z = 0` — the helper's anchor is a CENTER, so those
  windows sat half-buried in the floor, spanning ankle to knee, in
  eleven rooms including three kitchens and the cabin. Also: the
  whole centro grocery was double-booked (bakery counter inside the
  chest freezer, aisle 2 through the checkout, meat case inside the
  cooler run, endcap shelves inside the card bale), and today's own
  drone sat 1.27m inside a Sitka spruce.
- **New construction classes the visible walls demanded:** openings
  installed in walls (window assemblies occupy the full thickness),
  fitted cabinetry backing into its wall (≤0.40 — a counter run is
  authored from the wall's centerline), fixture bases/kicks abutting
  (≤0.22), neon letters through their raceway, tipped furniture
  below the floor plane, and `floor`/`_slab` added to the
  grounded-object name list.
- **The rule: when a tool's coverage changes, RE-BASELINE loudly.**
  The holdout table in `run_all_audits.sh` now carries a dated,
  commented triage baseline (24 locales, 111 clips) with the debt
  written next to each name — not a budget, and never to be raised.



### 2026-08-12 · never-built beats stale: enumerate BOTH

- **The first Deck run of `list_stale_builds.sh` found six
  builders with NO GLB at all** — ben_bedroom, bindery,
  centro_stockroom, henderson_garage, miller_garage (five live VN
  backgrounds across 8 chapters) and ember_ash_office (the
  Chariot gauntlet board). All had been rendering the 2D fallback
  indefinitely.
- **The lesson: a missing artifact and a stale artifact present
  identically in-game** (fallback / month-old world), but only
  staleness gets talked about. Any build-freshness tool must
  report NEVER BUILT as a separate, louder category — and
  rebuild priority goes to never-built first, since those scenes
  have no correct version at all.



### 2026-08-11 · the founding day

Everything above was learned in one arc: 1,693 trustworthy clips
at dawn (the first full-coverage run) → 18 by night (the barn's
designed crumple + the diner's ticket tucks), across ~45 locales
of triage in eleven grammar drafts. The costliest single lesson:
**two independent failures mask each other** — graustark's stale
GLB hid the blind camera preset, and fixing either alone left the
scene identically brown. When a fix "doesn't take," enumerate the
failure paths separately before concluding anything.

<!-- TEMPLATE
### YYYY-MM-DD · title

- **What broke / what was learned.** Specifics with names and
  numbers. Graduate to Core rules once it has held across
  multiple sessions.
-->

### 2026-09-07 · the Deck session · markers were never checked

- **Read every marker form or the gate is a fiction.** 198 of 589
  vn_shot markers used `position = Vector3` and both marker tools
  read only `transform = Transform3D`; a third of all shots had never
  been aimed or seen. Rule: a parser over authored data must count
  what it SKIPPED and print it; a green audit over a silent skip is
  worse than no audit.
- **Name matching must split CamelCase.** `WallClock_Face` never
  answered to "clock". Parts are now split on "_" AND on case.
- **A fallback that passes is a hole.** Unresolved insert subjects
  fell through to "anything in a wide cone" — a blank wall qualifies.
  Unresolved now fails; a KNOWN_UNRESOLVED table prints WARN with the
  reason.
- **Judge a marker by its SUBJECT, not by fill.** The first
  marker pass flagged 374 of 589 because an insert of a mug at 0.8 m
  is "near" by construction. The right question is the
  cinematographer's: can the lens see the thing? Five rays
  lens→subject; blocked by a non-subject = OCCLUDED. That cut 374 to
  128 real defects (and the user had been looking at those 128).
- **Reframe, don't just reaim.** Turning a camera that stands inside
  a bookshelf does nothing. marker_reframe searches rings around the
  subject for a position that is not inside anything and sees it
  unoccluded, nearest the author's original — 96 of 128 fixed
  mechanically; 22 STUCK are content problems (the prop is behind a
  wall from every side).
- **Same-prefix exemption hides intra-assembly clips.** The overlap
  gate's assembly rule is right for wheels in bodies and wrong for a
  pillow through a mattress. furniture_grammar_audit reports INTRA
  separately, skipping structural joints (wall corners, crown mitres,
  roof/chimney) and contained parts (drawers in pedestals).
- **Dict literals keep the LAST duplicate key.** SYNONYMS had
  duplicate keys; the later, weaker entry silently won for
  speak_and_spell and radio. Lint for duplicate keys in any hand-
  maintained table.
- **This pipeline has no alpha.** A (r,g,b,0.35) "translucent" slab
  renders as an opaque slab. Water, glass, spray: model the THING
  (thin tubes, frames), never a tinted plane.

### 2026-09-07 (later) · working the queue · the furniture grammar's first real pass

- **Verify a new heuristic numerically before mass-fixing.** The
  chair check said 36 chairs faced away. Three were checked by hand
  (seat / back / table centres) and confirmed; the fix wave was then
  safe. But the KT chair was flipped on the audit's word alone and had
  to be reverted — it belonged to the kitchen table, not the desk the
  matcher picked. Rule: spot-check three, then batch.
- **"Nearest table" is the nearest EDGE, and a chair may face any of
  them.** Centre distance let a bar 1.5 m behind a meeting ring claim
  the ring's chairs; the ring's own coffee table was the real target.
- **Embedding is not occlusion.** A subject set INTO another surface
  (glass in a wall, a board on a floor, an envelope in a desk top's
  box) is hit "through" its mount from every angle. An 18 cm
  tolerance on the blocker distance freed 8 of 19 stuck markers.
- **Lots are not lanes.** The first LANE run flagged nine cars parked
  in parking lots (the diner, Lake Palestine, the strip-mall
  frontage). Any place-a-car-belongs word (lot, apron, frontage,
  driveway, garage, pad) excludes the surface; cul-de-sac bulbs are
  measured radially.
- **Desks off the wall are sometimes the point.** A judge's bench, a
  ship's helm, a newsroom island, an executive desk centred on the
  door. Allow-list by name AND by locale with the reason written down,
  never by loosening the rule.
- **A shared builder must keep the story's sightlines.** Swapping
  Maya's open bed frame for a solid platform occluded the three
  inserts that look UNDER her bed (the loose floorboard, the envelope,
  the photograph) — the marker gate caught it within the hour. When a
  kit replaces bespoke geometry, run the marker gates on that locale
  before moving on; the kit's default shape is not the author's.
- **Regex-anchored doc edits fail silently.** Two playbook lessons
  were "written" against an anchor this file never had and vanished.
  Assert the anchor, or append.

### 2026-09-07 (late) · raw meshes and what a bounding box is good for

- **Hook every geometry entry point, including raw meshes.** The
  recorder rebinds make_box / make_cyl / the vendored locals — and
  missed `_finalize_mesh`, the verts-and-faces helper eight builders
  use for terrain-following ribbons, ponds, ramps. Six presets on a
  Deck-verified stage audited against nothing for weeks. Rule: grep a
  builder for every function that ends in `bpy.data.meshes.new` and
  make sure the recorder answers to each name.
- **A mesh's bbox is a RAY fact, not an OVERLAP fact.** A 50 m sloped
  ribbon's box is a wall to a ray fan (right: it blocks the view) and
  a clip to every prop standing on the slope (wrong: the prop stands
  on the surface, not in the box). Raw-mesh boxes stay in the ray
  audits (ribbons themselves as fill) and are excluded from the
  overlap check. Do not "fix" this with a ceiling.

### 2026-09-10 (iv) · orientation is grammar too

- **A swap keeps the old origin.** The make_bed swaps of 2026-09-07
  reused each room's `bx, by` — mid-room values from the first
  draft — so eight beds stood a metre off their walls with perfect
  legs and pillows. Replacing a prop is the moment to re-place it.
- **Which end is the head is a check.** The ward bed's pillow was at
  the foot; Finn's lay along the long side. The BED rule reads the
  pillows' centroid against the mattress's long axis; if the two
  disagree the pillow is wrong before the wall is.
- **A moved bed drags its markers.** The hospice closeup framed the
  old pillow; run `--markers` on any room whose hero object moved.
- **Absolute-coordinate parts betray a moved top.** The New Orleans
  desk's legs stayed at x 0 when the top moved to 1.1 — the overlap
  audit only saw it once the bed slid into them. When moving any
  assembly, grep its sibling parts for literals.

### 2026-09-11 · a comment that says "copy this by hand" is a bug waiting

- **Every hand-synced duplicate rots, and the comment saying to sync
  it is the tell.** The gauntlet's standalone vantage mirror carried
  "when you update a host's SPACE_MAP, copy the change here too" and
  had five missing stations, two swapped booths and a stale podium.
  When you find that sentence, write the audit instead of trusting it.
- **Pair tables by CONTENT, not by name.** The diner's host is
  DinerGauntletHost and its location id is "dambrosios"; matching on
  key overlap paired all 23 correctly and, better, told the truth
  about the three whose host serves a different board.
- **When two tables disagree, ask the builder.** Booth_1 was at +3.75
  in one and −3.75 in the other; build_diner.py's boxes settled it in
  one query. The geometry is the source; the tables are copies.

### 2026-09-10 (iii) · the claim is in the source; audit the source

- **The phantom-surface bug is findable statically.** Every detail
  pass writes `foo_x = n`, `foo_y = n`, `bar_z = n` within a few
  lines; that triple IS the claim. `phantom_surface_audit.py` pairs
  them (stems need not match) and asks the recorded boxes whether a
  top exists under (x, y) near z. Eighteen locales, one query each.
- **The same room gets the same wrong bar twice.** Daigle's bar was
  authored at the south wall by two different passes months apart;
  the "approx" comment in the first was copied into the second. When
  one pass is wrong about a surface, grep the file for every other
  pass that names it.
- **A pass that draws a prop's FACE draws it on the prop's face.** The
  static-TV overlay was a second screen on a wall; the shirt "on the
  rack" was inside the rack's solid body. Look up the real object's
  orientation (thin axis) before placing a decal or a hung thing.

### 2026-09-10 (ii) · read the claims, not the counts

- **Thin, mounted and legged props hide from every geometry gate.**
  Six phantom passes survived FLOAT, POKE, OUTSIDE and the overlap
  gate because a paper label, a chart pocket, a jury seat with legs
  and a name card are all "held" by something. The only audit that
  found them was reading the docstring's "approx at (x, y)" and
  querying the builder's boxes at that point.
- **One query answers all of them.** `boxes_for(locale)` filtered by
  the real object's name and by "within 1.2 m of the claim" shows
  the real surface and what was authored at the phantom in one
  print. Do this for every location claim before trusting it.
- **"Ward 4's window" was a door.** A pass can be wrong about what
  the thing IS, not just where it is; check the name of what stands
  at the claimed spot.

### 2026-09-10 · OUTSIDE: legs to the floor hide a prop in the parking lot

- **A phantom surface with legs passes the float audit.** Daigle's
  "your stool" stood at y -3.5 with four chrome legs to z 0 — outside
  the south wall — and no gate saw it. The class is "touches no floor
  box" in interior locales, with exterior views (thru-window trees,
  facades, cars, docks, stairs leaving the slab) excluded.
- **"approx at (x, y)" in a detail-pass docstring is the bug's
  signature.** Eight locales now. The fix is always the same line:
  read the surface from the builder's constant, never from a comment.

### 2026-09-09 (night) · the residue is the vocabulary

- **When a count stops shrinking by class, the rest is vocabulary.**
  The last hundred floats were forty kinds of thing the grammar had
  no word for. Reading them one by one and naming each class
  (MOUNTED / hanging) is the work; there is no rule that finds a
  towel. Keep the MOUNTED list honest — every entry is a thing that
  really hangs.
- **A cone's bbox ends at its tip.** A cross set 0.30 m above a
  spire's bbox top is 0.30 m above the spire. Crosses, finials and
  beacons sit ON the tip; lower them to touch.
- **Stacks: spacing equals height.** Traps, ice blocks, comics,
  brochures: the tell is a uniform 5–10 cm gap in every layer.
- **A stair on a post is radial.** Square treads at a fixed radius
  can never touch the post; make_rot_box planks from the post out
  are the honest spiral (bayou lighthouse, riverboat).

### 2026-09-09 (later) · the phantom-surface query; rule ORDER is a rule

- **Query the residue for the pattern, not the count.** "gap between
  0.55 and 1.2 m over a floor-class support" is the phantom-surface
  signature; one query found four more locales the class lists had
  hidden among ropes and antlers. Every detail pass that wrote
  `desk_x =`, `counter_z =`, `mid_y =`, `bar_top_z =` from a comment
  is suspect until the builder's own box is under it.
- **A rule placed after an early `continue` never runs.** The EMBEDDED
  check sat below the "support tops out within 0.25 m" filter, so a
  bottle inside a 1.8 m vending body was "floating" for a week.
  When a rule seems not to fire, read the loop above it before
  loosening it.
- **Support is four things.** Under (a top within the gap), sibling
  running past (post through a face), hanging (body over a leg, rail
  over a bar) and backed (a wall face within 3 cm). The float audit
  needed all four before its residue was real.
- **"Only the display holds the head up" is a class too.** The Kwik
  pumps had base, display, head — no body. Look for the missing
  middle whenever a top part floats over its base by a round number.

### 2026-09-09 · solid things are solid; a phantom desk is a pattern

- **A shelf is a carcass, a freezer is a shell.** Anything the player
  is meant to see INTO must be built as back + sides + boards. A solid
  block with the contents authored inside it hides the contents and
  reads as floating to every audit. Maya's paperbacks and Christian
  Ice's blocks were both invisible in the GLB.
- **A stair is a solid, or it has stringers.** Slabs at rising z with
  air between them are a ladder of shelves. Either extend each step
  to the floor (kitchens, gym, lobby, Montreal rows) or model the
  structure that carries it (the spiral's radial planks from the
  pole). Then move whatever was tucked under the old air (the gym's
  deadlift platform).
- **The phantom-desk bug is a PATTERN, not a courthouse quirk.** The
  lighthouse's detail passes did the same: a hard-coded desk origin
  that never matched the builder's. Any pass that writes `desk_x =`
  from a comment must read it from the builder's constant, and the
  FLOAT audit's "0.79 m above the floor" is the tell.
- **A sibling that runs past you holds you.** A sign face beside its
  post, a mullion inside its frame, a leg under a body: support is
  not only "something topping out just under me". Check the sibling
  window before the top window.
- **Fix your own regressions before the class you came for.** Solid
  steps hit the platform under them; radial treads reached the wall;
  ziggurat steps nested. Three edits, three new clips, all caught by
  re-running the touched locales — never commit a class fix on the
  class audit alone.

### 2026-09-08 (night) · a class of 82 is a builder habit, not 82 bugs

- **Group floats by part class before reading one.** 1408 FLOAT lines
  were unreadable; 82 'seat' lines were one sentence: chairs get built
  as seat + back and nobody adds legs. Fix the habit with one patcher
  (seat centre ± offset, four posts rooted 2 cm) across sixteen files,
  not sixteen hand edits.
- **A prop "on a table" is on whatever the coordinates say.** Two
  courthouse detail passes wrote `pt_y = 2.50` for the plaintiff's
  table from a comment ("approximate") while the table stands at 5.5.
  Every hero object of that chapter — caption, pen, folder, motion,
  briefcase, two coffees — sat on a pew. When a detail pass hard-codes
  a surface, derive it from the builder's own constant.
- **Embedded is held.** A book inside a one-box bookshelf, a comic in
  a rack body, a deck on a wall board: the solid spans the underside,
  so it is not a float. Whether the embedding is ugly is the overlap
  audit's question.
- **Heightfield locales cannot say "nothing under it".** The terrain
  is a raw mesh the recorder never boxes; skip that verdict there and
  keep the sibling-gap one.
- **Moving a hero object moves its insert.** The folder's marker was
  framed at the pew; after the props moved, the pew back stood in the
  lens. Re-run `--markers` on any locale whose named subjects moved
  and reframe before commit.

### 2026-09-08 (later) · overlap inside an assembly is the grammar; POKE-THROUGH is the defect

- **Inside one named assembly, overlap is how parts are joined.**
  Rooted posts, mullions in rails, a head on a body, a door in its
  wall: 4544 INTRA findings were 95 % the rooting rule working. The
  defect the user sees is a member that comes out the OTHER side —
  a leg proud of its seat, a back panel to the floor, a hi-hat stand
  up through the snare. Measure that (top above AND bottom below),
  not penetration depth.
- **Thin in ONE plan dim is a sheet; thin in BOTH is a member.** A
  shelf-unit back panel, window glass, a jamb, a door frame all
  "pass through" shelves and slabs by design. Only members (and a
  chair back through its own seat) count.
- **A post through the slab it stands on is rooted, not poking.**
  Exclude ground-class solids (slab, deck, dais, platform, porch).
- **A stack of boxes sharing a plan overlap needs a slot each.** Le
  Roulant's letters sat inside the cornice because the neon disc
  owned the only free band above it; re-space the whole stack, don't
  nudge one element into the next.
- **When a chair is "on the wrong side", check which side the person
  sits.** The judge's chair stood in FRONT of the bench on the floor,
  passed the chair-facing rule (freestanding by name) and only the
  poke class caught its back running to the ground.

### 2026-09-08 · park against the ROAD, not along an axis; a bbox cannot see a diagonal

- **A fixed pull-out along the house's axis is a car in the street
  whenever the road is diagonal.** harmony_terrain's driveway cars
  sat 2.7 m past the garage face along ±X/±Y; on Phase II's winding
  road that axis met the asphalt after 2 m. The fix is a clearance
  function handed to the house builder (`road_edge(px, py)` → metres
  outside the road band) and a walk-back loop over the four corners.
  No driveway long enough → no car. Say so; don't fake it.
- **A bounding box cannot measure a diagonal road.** P2Road_1 is 7 m
  wide and its bbox is 15.6 m tall; the lane check read a car 0.5 m
  clear of the asphalt as 2.2 m inside it. Roads with a short bbox
  side over 10 m are now skipped — the honest gap is boulevards wider
  than that, which no locale has yet. When a class hits zero and the
  last two findings are on diagonal geometry, suspect the box before
  the builder.
- **Zero is when a class becomes a gate.** CHAIR · DESK · LANE were
  informational at 5 · 1 · 13 and gated the moment they reached 0.
  INTRA and FLOAT stay counts until their classes are worked the same
  way. Never raise a grammar ceiling; fix the builder or extend the
  grammar — the same rule as prop_overlap.

### 2026-09-07 (night) · the chair-back class; a helper's "facing" is a lie until checked

- **Classify before fixing, then fix the CLASS.** 1737 FLOAT findings
  were noise until grouped by part class: `back` above `seat` was 29
  real chairs — the user's "chairs not fully assembled" — and one
  patcher lowered them all. The rest of the class list (hub, cab,
  body) was vehicles, excluded as assembly.
- **A helper's facing argument means what its code does, not what
  its name says.** harmony_commercial's `_make_car(..., facing='+X')`
  lays the car's LONG axis along Y. Read the helper's size swap before
  trusting the word; the recorder's dump (`Car_Kwik_Body h=(0.9, 2.1)`)
  told the truth in one line.
- **A building can stand in the street too.** The Kwik Stop's front
  half sat inside the arterial's 16 m plane because its centre was
  authored before the lot edge was. When a car keeps ending up "in the
  road", check whether the road is where the building is.
