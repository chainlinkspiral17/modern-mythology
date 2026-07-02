# Graustark, TX/LA — City Map

A top-down plan of the bayou-edge town that contains D'Ambrosio's.
The city is canonically half-destroyed by a sinkhole during vol5
(see `_3D_MODELING_PLAYBOOK.md`), but the present build models the
pre-sinkhole state — the version that exists when the Fool walks
into the diner.

## How to read this

Every locale we build in Graustark consults this file first. The
map tells us:
- Which named arteries connect to which neighborhoods
- What's within 100m of any given anchor (player-POV scope)
- What's mid-distance (300-500m, silhouette / depth scope)
- What's far-distance (1km+, horizon scope)

Don't add buildings to a scene that aren't on this map.

## Arteries (functional road network)

```
              ┌─── HWY 90 (E-W) ────────────────────────► CROSSES RIVER
              │                                           via Truss Bridge
              │
              ▼
    ┌─────────┼────────────────────────────────────┐
    │         │                                    │
    │ WESTBROOK    DOWNTOWN GRAUSTARK              │ EAST RIVER BANK
    │ (resid.)     (Main + Front)                  │ (opposite shore)
    │         │                                    │
    │         ▼                                    │
    │    STATE ROUTE 12 (N-S) — main commercial    │
    │         │                                    │
    │         ▼                                    │
    │    RIVER ROAD (N-S) — parallels the river  ◄─┤── D'AMBROSIO'S is HERE
    │         │                                    │   on River Road
    │    WHARF ST (E-W) — crosses River Rd         │
    │    near the boat                             │
    │         │                                    │
    │         ▼                                    │
    │    INDUSTRIAL DIST. (south, rail+refinery)   │
    │                                              │
    └──────────────────────────────────────────────┘
```

### Road hierarchy

- **HWY 90** — interstate-spec, two lanes each way, crosses the
  river via the truss bridge at the south end of town. Visible in
  the far distance as the overpass + truss bridge.
- **STATE ROUTE 12** — main commercial spine, runs N-S through
  downtown. Two lanes, divided centerline. NOT modeled in the
  riverfront scene (lies west of the viewable area).
- **RIVER ROAD** — local arterial, runs N-S parallel to the river
  on the WEST bank. This is our "frontage road." Two lanes, double-
  yellow centerline, drainage ditches.
- **WHARF ST** — cross street east-west, dead-ends at the dock on
  the east side and feeds into Westbrook residential on the west.
- **Side streets** in Westbrook — simple residential, no markings,
  curving.

## Neighborhoods

### Riverfront (the scene we're building)

The strip along River Road between Wharf St (south) and Magnolia St
(north). Hosts D'Ambrosio's (the riverboat-diner), one filling
station, one strip mall, a public park, and a half-dozen houses
spaced along the west side of River Road.

The block radius is roughly 200m N-S × 100m E-W. Beyond that, the
horizon is filled with silhouette content only (see "Horizon scope"
below).

### Downtown (NOT modeled, sits west)

Main + Front intersection has the courthouse, post office, two
banks, the old movie theatre. SR-12 runs through. NOT visible from
the riverfront parking lot because of the Westbrook houses + tree
line between.

### Westbrook (residential west)

Small clapboard houses on small lots, oaks lining the streets,
mostly built 1920s-1950s. Visible from D'Ambrosio's only as a
distant rooftop silhouette over the tree line, ~500m west.

### Industrial District (south)

Sits along the rail line and the river south of Wharf St. Contains
the refinery (with stacks visible from D'Ambrosio's), warehouses,
container yard, fishing docks. Already represented in our build as
the "South horizon — port-industrial complex past the bridge."

### East River Bank (opposite shore)

Across the wide river. Lighter development — a few homes, the
opposite-shore industrial cluster, distant hills. Already in our
build as `build_opposite_shore()`.

### Bayou (NE, navigable side channel)

Cypress-and-tupelo swamp branching off the main river just north of
D'Ambrosio's. Has a wooden pier, a fishing camp on stilts. Already
in our build as `build_bayou()`.

## Scope radii from D'Ambrosio's parking lot

### Within 100m (PLAYER POV — must be high detail)

This is what the player sees clearly. Every element here gets full
fidelity. Player spawn is at Blender (-22, 0, 1.5) facing +X.

**Foreground (0-30m):**
- Parking lot itself (asphalt, painted lines, 8 cars, sodium lights,
  curbs, storm drain, dumpster, newspaper boxes, bus bench, signs)
- Dock (deck, pilings, cargo crates, drums, lanterns, mooring lines)
- D'Ambrosio's gangway sloping from dock to boat
- The cursive D'Ambrosio's neon pole sign

**Near-mid (30-60m):**
- D'Ambrosio's riverboat (full multi-deck detail — boiler / saloon /
  hurricane / pilothouse / paddle wheel / smokestacks / hull / sign
  on cabin roof)
- River Road itself with full road treatment (lanes, sidewalks,
  drainage ditches, sewer grates, telephone poles, streetlights,
  trees lining, fire hydrant, stop sign, mailboxes)
- The cross-street intersection (Wharf St)

**Mid (60-100m):**
- Gas station (full detail: canopy, pumps, store, price sign)
- Strip mall (full detail: storefronts, lit windows, signage, parking)
- Public park (lawn, picnic table, bench, swing set, path, trees)
- The bayou pier and first few cypress trees
- Other boats nearest the dock (tugboat, skiff, cruiser)

### 100-300m (mid-distance — moderate detail / silhouette OK)

- Westbrook houses just past the riverfront strip (rough shapes only)
- More bayou trees in the swamp
- Buoys, barge, more boats further out
- Approach to the truss bridge

### 300m+ (horizon scope — silhouette only)

- Opposite shore (full strip with refinery, water tower, billboard,
  power-line pylons, dense tree line)
- Far hills behind the opposite shore
- The truss bridge crossing the river
- North horizon town with the church spire + water tower + houses
- South horizon port-industrial with container cranes + refinery
- The highway overpass running parallel west

This radius logic carries to every other locale: anything within
100m of the player's primary anchor gets detail; everything beyond
fades to silhouette. **Stop adding random mid-detail buildings at
random distances** — every building should be on this map first.

## What's CURRENTLY in the riverfront build (June 2026)

**Within 100m, working but needs fixing:**

| Element             | Status                                    |
|---------------------|-------------------------------------------|
| Parking lot         | OK                                        |
| Dock + cargo        | OK                                        |
| Riverboat           | OK (recent multi-deck rebuild)            |
| Pole sign           | OK (after cursive_type pass)              |
| Boat sign on roof   | OK (after the relocation to saloon top)   |
| Gas station         | **WINDOWS FLOATING** — fix needed         |
| Strip mall          | **WINDOWS FLOATING** — fix needed         |
| Frontage road       | OK                                        |
| Drainage ditches    | OK                                        |
| Telephone poles     | OK                                        |
| Streetlights        | OK                                        |
| Cross street        | OK                                        |
| Public park         | OK                                        |
| Roadside trees      | OK                                        |
| Mailboxes/hydrant   | OK                                        |

**Within 100m, MISSING:**

| Element                              | Why we need it                |
|--------------------------------------|-------------------------------|
| 4-6 small Westbrook houses on west   | Fill the west-of-road space   |
|   side of River Road                 | currently empty               |
| House yards + porches + fences       | Bayou-city residential char.  |
| Wharf St visible to the east         | Cross-street that connects to |
|                                      | the dock — currently stubbed  |
| Visible foundations under buildings  | "from below water level up"   |
| Storefront awnings + sandwich-board  | Strip-mall character          |
|   signs on the sidewalk              |                               |

**Beyond 100m, working as silhouette:**

- North town, south port, opposite shore, bayou, bridges. Don't
  upgrade these to high detail — that's not where the player is.

## Build order for future passes

1. Fix floating windows on gas station and strip mall.
2. Embed building foundations into the ground (water-level + below).
3. Add 4-6 Westbrook houses on the west side of River Road within
   the 100m radius.
4. Add storefront awnings + sidewalk sandwich-board signs to the
   strip mall.
5. Stub Wharf St going east toward the dock so the cross-street
   intersection has both sides.

Anything outside this list goes through the playbook + this map
first.
