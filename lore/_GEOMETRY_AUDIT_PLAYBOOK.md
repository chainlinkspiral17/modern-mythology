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

## Natural-contact grammar index (draft 11)

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

## Recent lessons

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
