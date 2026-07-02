# Graustark — Deep Build Plan (next session)

Hand-off doc from the HCE polish + character-study session. The
existing Graustark surface is in `_GRAUSTARK_MAP.md` and the
riverfront stub is in `godot/tools/blender/locales/build_riverfront.py`.
Goal of the next session: take Graustark from "stub with a diner"
to a real **bayou-edge delta town** that holds up under the lessons
we ground out of HCE.

The whole place reads from one rule: **water + gravity made
everything you see, except the bits humans defied them with**.
Geology decides where the bayou goes. Bayou decides where you
can't build. The raised bits decide where the town actually is.

## Visual reference (2026-06-16)

**Lafayette, LA + New Orleans, weighted to Lafayette.** The map
is **theme-park sized like HCE** (1200×840 m district envelope),
not a 1:1 representation — every narrative locale arranged
logically, but compressed so the player can walk between them
in minutes rather than hours.

Lafayette characteristics we lean into (60-70% of the look):

- **Bayou Vermilion analog** as the central waterway, meandering
  with broad oxbow bends, NOT a straight channel.
- **Raised cottages on cypress stilts** — the dominant
  residential type. 1.8-2.5 m crawl space visible from street.
  Front porch with hipped roof, tin standing-seam roofing.
- **Cane-field horizons** at the district edge — flat, low,
  carved into rectangular plots, drainage canals between.
- **Compact "downtown core"** — modest height (1-3 storey),
  brick storefronts with awnings, NOT skyscrapers.
- **Strip-mall arteries on the outskirts** — Coastal-South
  vernacular. Half-empty parking lots, faded chain signs,
  drive-thru daiquiri stands.
- **Small businesses in shotgun-style buildings** — narrow,
  long, single-story, off-the-rack.

New Orleans flavour (the remaining 30-40%):

- **One compact "French Quarter" district** in the urban core
  — wrought-iron balconies on 2-3 storey row buildings,
  stucco in pastel washes (faded pink, yellow ochre, sage).
  Maybe 4-6 buildings deep — not the whole town.
- **Above-ground cemetery** as one outlying narrative locale
  (raised tombs because you can't dig in the delta water table).
- **Streetcar suggestion** — at minimum a steel-rail strip
  embedded in one downtown street, maybe one parked car at
  a station.
- **A grand cathedral / town-square anchor** referencing
  Jackson Square's gravity — modest scale (not Saint Louis),
  but a tower silhouette on the horizon from anywhere in town.
- **Mardi Gras hints** — bead garlands on a few balcony
  railings, a banner across one street.

What we DELIBERATELY avoid:

- Skyscrapers / Houston-style highrise. Lafayette has none.
- Tourist-mob Bourbon Street density. We're not French Quarter,
  we're "small French Quarter with one block."
- Pristine restored Garden District mansions. The town is
  lived-in, weathered, NOT a movie set.

### Map-scale framing (HCE-comparable)

- District envelope: **1200 × 840 m** (same as HCE) — gives
  us 1 km² of usable build area.
- Player-traversable in ~15 min on foot at jog-pace.
- All canonical narrative locales (D'Ambrosio's, river
  crossing, downtown anchor, the cathedral, the cemetery,
  Lafayette-style residential neighbourhood, cane-field
  edge) arranged so each is within 200-400 m of another.
  Theme-park compression — logical, not literal.

---

## Phase 1 — Top-down geology + strata (the foundation)

Before any roads, before any houses, the terrain must be authored
as a stack of strata that read in the elevation field:

```
+8 m  ─────────────────────── high natural levee / oak ridge
                              · loamy, ~5% sand
                              · old hardwood roots: oaks, cypress
                              · pre-existing settlements cluster here

+3 m  ─────────────────────── upper bayou bank / raised street
                              · cleared decades ago, fill on top
                              · road shoulders, drainage ditches

 0 m  ─────────────────────── MEAN SEA LEVEL / canonical "0"
                              · "the floor" of the bayou system
                              · most houses sit on stilts above this

-1 m  ─────────────────────── tidal mud flat, alga-stained
                              · still wet at low tide, fully
                                submerged at high
                              · cordgrass + black needlerush

-2 m  ─────────────────────── permanent shallow bayou channel
                              · cypress knees rise from this depth
                              · dark tannic water

-4 m  ─────────────────────── navigable channel bed
                              · only boats and crabs live here
                              · silt + clay floor
```

Build technique:
- ONE elevation field for the whole map (~600m × 600m).
- Stratum colours pulled from a top-down chart so each Z band is
  visually distinct (the player sees 5 bands not "muddy gradient").
- Generate elevation as a sum of: natural levee ridge (1D
  ridge function along bayou line), gentle delta slope toward
  the gulf, and Perlin micro-noise for bayou meander.

## Phase 2 — Natural weathering + erosion

The terrain should LOOK eroded, not procedurally smooth. Approach:

- **Channel cut-banks** — where the bayou bends, the OUTER bank
  is undercut (vertical drop into water), the INNER bank is a
  sand/silt bar (shallow ramp).
- **Cypress hummocks** — knee-rises around tree roots create
  small islands in the wet zones. Each hummock is a 3-5m radius
  bump in the elevation field, raised 0.5m above local water.
- **Tidal flats** — the -1 m band has parallel **rib lines**
  (cordgrass + drainage rills) running PERPENDICULAR to the
  channel.
- **Old crevasse splays** — fan-shaped deposits where the bayou
  has historically broken its bank. Small bumps a few hundred
  metres back from the channel, sediment-coloured.
- **Settled subsidence** — pockets where the ground has dropped
  0.5-1m because peat oxidised. Visible as low spots in the
  raised-fill zones.

## Phase 3 — Human carving (the cuts)

Where humans cut into the natural state. These are the bits that
read as "lived in":

- **Raised roads on fill** — every road in town is a 0.5-1.5m
  berm above local grade, with drainage ditches on both sides.
  This is the SINGLE most identifying feature of Louisiana delta
  towns — DO NOT skip the berm.
- **Levee crowns** — flood control along the bayou main channel.
  10-15m wide grassy crown, 3-4m above water. The road sometimes
  runs ALONG the levee crown.
- **Pile-cut foundations** — house lots are NOT graded flat the
  way HCE's were. Instead, each house sits on visible pilings
  driven into the wet ground, with the slab/floor 1.5-2.5m
  above grade. Crawl space is part of the silhouette.
- **Bayou-side bulkheads** — wooden seawalls at the back of
  riverside lots where the owner has fought the tide. Old,
  partially rotted, vines.
- **Drainage canals** — straight man-made channels at 45° to
  the natural bayou meander. Concrete-lined at the road
  crossings.

## Phase 4 — Infrastructure (roads + paths)

Two ROAD TYPES, distinct silhouettes:

1. **Raised arterials** — HWY 90, State Route 12, River Road.
   On the berm, ditches on both sides, painted lines, signposts.
   Already partially in `_GRAUSTARK_MAP.md`.
2. **Bayou-side lanes** — gravel or shell-paved, drift between
   houses, follow the contour rather than a grid. Half submerged
   at high tide in places.

Path types:

- **Boardwalks** — wooden plank paths over the tidal flats,
  connecting raised pads to neighbour houses or the boat dock.
  Pilings every 2m, 1m above mean water.
- **Truck Bridge** (already canonical) — at the south end where
  HWY 90 crosses the navigable channel.
- **Foot ferry slips** — small notches in the levee where a
  flat-bottomed boat ties up. Two on the west bank.

Reuse infrastructure pattern from HCE:
- `ROAD_CORRIDORS` for the berm arterials.
- Catmull-Rom polyline smoothing for bayou-curve roads.
- Polyline-bend fillet plates for the corners that aren't grid.

## Phase 5 — Buildings + homes

The four building archetypes, in order of frequency:

1. **Shotgun house on pilings** — long narrow rectangle, 5m wide
   × 14m deep, gable roof, 1.8-2.5m crawl space below. Front
   porch with railings. The dominant residential type.
2. **Levee-crown bungalow** — slightly grander, set back from
   the bayou on the high ground. 9m wide × 9m deep, hip roof,
   minimal crawl. These are the "old money" houses.
3. **Boatyard sheds + Quonsets** — south-end industrial pads.
   Corrugated metal, hipped or quonset roofs, no foundation
   stilt — slab on grade (because they're on the highest ground).
4. **D'Ambrosio's** — already canonical (riverfront diner).
   Iconic shape, doesn't replicate elsewhere in town.

Foundation rule (carryover from HCE polish):
- Crawl space height should be **author-set**, not derived from
  terrain — every shotgun house has 1.8m of pilings VISIBLE
  whether the lot needs it or not. Pilings ARE the silhouette,
  not a foundation skirt.
- That means we DON'T bridge the terrain Z-range with a flat
  skirt the way HCE houses do. Pilings are individual posts,
  and the gap underneath shows the bayou through.

## Audit set we'll port from HCE

Every audit from HCE applies, plus new ones:

| Audit | Carryover or new |
|-------|------------------|
| building × road overlap | carryover |
| building × water (bayou + tidal) | carryover (creek → bayou) |
| house × house spacing | carryover |
| connector grade match | carryover |
| tall foundation | **dropped** — tall foundations are CORRECT in Graustark |
| fence streaks / overlaps | carryover but expect fewer fences (delta culture) |
| **NEW: house on stilts has piling count ≥ 6** | new |
| **NEW: pile bottoms reach below mean-water-line** | new |
| **NEW: road berm height ≥ 0.5m above local grade** | new |
| **NEW: boardwalk follows the -1 m band, doesn't ford -2 m** | new |
| **NEW: every navigable bayou segment has clear hw ≥ 3m** | new |

## Lessons-learned baked in upfront

From HCE polish:
- **Build the stubbed-bpy smoke test FIRST** before adding features.
- **No props before terrain is right.** Roads, terrain, water, then
  houses, then props.
- **Audit everything you generate from the start.** A 5-house phase
  with audit-pass is better than 40 houses with 12 audit failures.
- **Per-house variety from a position seed**, not random. Reproducible.
- **Step long things on slopes** (back fences in HCE, boardwalks
  here).
- **Show the user visual evidence** of completed work — silhouettes,
  audits, screenshots. Don't assume changes registered.

From the planar human study:
- **Read the silhouette FIRST**, then add detail. A building's
  silhouette (gable / hip / quonset / piling) carries the look at
  player distance; siding texture wouldn't.
- **Hard normal shifts catch light**, smooth ones disappear. Even
  for buildings — chamfered eaves, hard porch ceiling planes.

## Starting point — extend the riverfront, don't start fresh

**User directive (2026-06-16):** start from
`godot/tools/blender/locales/build_riverfront.py`. That scene
already has:

- The D'Ambrosio's riverboat exterior (clapboard hull, brass
  rails, paddlewheel, smokestack, wraparound porch, gangway,
  upper-deck helm cabin)
- Parking lot adjacent (asphalt, painted lines, sodium
  streetlight, a few cars)
- River water plane + opposite shoreline (strip with cypress
  trees + far industrial buildings)
- 2-3 other boats (tugboats, fishing skiffs) scattered
- A bayou section with cypress + Spanish moss + small pier

This is the **vol5/vol6 canonical D'Ambrosio's site**. The
Graustark deep-build pass expands the world AROUND this anchor
— promoting the riverfront from "single locale" to "one
neighbourhood inside a full town."

**Strategy:**

1. RENAME the build script. `build_riverfront.py` →
   `build_graustark.py` (keep the old name as a thin shim that
   imports from the new one, so existing Godot scene refs don't
   break).
2. Preserve every existing canonical structure inside its current
   coordinates. The boat, parking lot, opposite shoreline, and
   bayou pier are anchors — Graustark's coordinate origin and
   the bayou-channel route are inherited from them.
3. EXPAND the world envelope from the riverfront's current
   extent out to the full 1200×840 m HCE-comparable district.
   The riverfront becomes the **southeast quadrant** of the
   map (the bayou-edge industrial / boatyard zone).
4. Layer the five-phase deep-build (geology → erosion → carving
   → infrastructure → buildings) on top of the existing
   riverfront content — NOT replacing it.

The first commit of the Graustark deep-build is therefore a
rename + envelope expansion + a TODO scaffold for the five phases.
Nothing visible changes on first build; subsequent passes fill in.

## Build-script structure proposal

`build_graustark.py` (extending today's `build_riverfront.py`):

```
0. EXISTING RIVERFRONT (preserved verbatim from build_riverfront)
   · boat, parking, opposite shore, 2-3 boats, bayou pier
1. CONSTANTS (sea level, levee height, bayou route, …)
2. ELEVATION FIELD (strata + erosion + carving)
3. WATER LAYER (mean tide + bayou main channel + drainage canals)
4. ROAD CORRIDORS (HWY 90, SR 12, River Rd, Wharf St, side lanes)
5. BUILDING PADS + PILING LOTS
6. _build_shotgun_house, _build_bungalow, _build_quonset
7. CHARACTER PLACEMENT (uses human_male_base / human_female_base
   from godot/assets/3d/characters/, scattered through downtown
   + porches; ONE base mesh per gender, variant deformation
   driven by per-NPC shape-key params)
8. PROP PASS (cypress trees, palms, boats, oyster shell piles,
   fishing gear, kid bikes — last)
9. AUDIT-INTERCEPT hooks (just like HCE)
10. EXPORT TO GLB
```

`tools/audit/graustark/*` — analog of the HCE audit folder,
with the carryover + new audits listed above.

---

## Open decisions for the user before next session

1. **Map scale.** HCE was ~600 × 600m. Should Graustark match,
   or do we want a tighter "downtown + 1-2 neighbourhoods" focus
   (~300 × 400m) so the bayou and the levee both fit in one
   draw distance?
2. **Sea-level absolute Z.** Right now HCE's mesh_z floor is at
   wherever the build script puts it. Pick: Z=0 is bayou bottom
   (the strata diagram above), OR Z=0 is mean sea level (with
   bayou floor at -4m). The strata diagram assumes the latter.
3. **How much canonical D'Ambrosio's stuff to preserve.** The
   existing `build_riverfront.py` is a stub; do we rebuild it
   inside the new terrain pass, or treat the new build as a
   superset that subsumes the riverfront?
4. **Sinkhole present or future?** Map doc says present-build is
   pre-sinkhole. Confirm we stay pre-sinkhole for this pass.

---

*Filed 2026-06-16, after the HCE fence polish + character study
session. Carry forward to the next session.*
