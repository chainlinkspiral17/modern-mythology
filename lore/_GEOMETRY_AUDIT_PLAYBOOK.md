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
