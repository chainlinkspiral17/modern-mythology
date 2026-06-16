# Graustark — Major Arcana Exterior Locale Map

Every interior locale in the project has a corresponding exterior
in Graustark (1200×840 m district). This doc is the spatial
authority — when a build pass lands a new building, it consults
this table for canon-correct positioning + style.

Cross-references:
- `_TAROT_LORE.md` — the arcana → character anchor table
- `_VOL5_WIKI.md`, `_VOL6_WIKI.md`, `_VOL7_WIKI.md` — narrative
  canon for what each interior is
- `_GRAUSTARK_DEEP_BUILD_PLAN.md` — the five-phase build plan
- `_GRAUSTARK_MAP.md` — the high-level downtown sketch

## Map zones

Used in the table below:

| Zone code | Region                           | X range       | Y range      |
|-----------|----------------------------------|---------------|--------------|
| `RF`      | Riverfront (preserved)           | -200 to +220  | -200 to +200 |
| `SW`      | Western suburban (Lafayette)     | -600 to -300  | +10 to +400  |
| `SR12`    | State Route 12 commercial spine  | -200 to -160  | -420 to +420 |
| `BQ`      | Bourbon Quarter (FQ block)       | -330 to -300  | +50 to +130  |
| `LEV-W`   | West levee crest (cottages)      | -100 to -50   | -420 to +420 |
| `MTL`     | Montreal block (NE corner)       | +450 to +510  | +300 to +360 |
| `BAYOU`   | Bayou corridor (water + flats)   | varies        | varies       |
| `SE-IND`  | South industrial (boatyard etc.) | +100 to +400  | -420 to -300 |
| `NW`      | NW open / cathedral horizon      | -600 to -400  | +400 to +420 |
| `NE-IND`  | NE industrial (Frasier's cathedral) | +200 to +400 | +300 to +420 |
| `SW-IND`  | SW open / hospital + asylum      | -600 to -400  | -420 to -250 |
| `CANE-W`  | Cane fields west                 | -600 to -540  | -200 to +10  |
| `CANE-E`  | Cane fields east (across HWY 90) | +540 to +600  | -420 to +200 |

## The 22 exteriors

| # | Card | Anchor | Exterior locale | Style | Coords | Status |
|---|------|--------|-----------------|-------|--------|--------|
| 0 | Fool | John (D'Ambrosio's) | **D'Ambrosio's riverboat** | Riverboat, clapboard hull, paddlewheel | RF (0,0) | ✅ built (riverfront) |
| I | Magician | Frasier (Cathedral of Rust) | **Cathedral of Rust and Code** | Converted 1920s warehouse, brick + corrugated tin roof, cathedral windows blocked with sheet metal, satellite dish + antenna farm on roof | NE-IND (+300, +380) | ✅ placed |
| II | High Priestess | Elicia (gift shop/archive) | **Elicia's Curio & Archive** | Narrow shotgun storefront with deep dark interior, tall French Quarter pilasters, "ARCHIVE" sign in faded gilt | BQ (-320, +66) — north end of FQ row | ✅ placed |
| III | Empress | Nicola + Aria (boat floor) | **Upper deck of the riverboat** | Already part of D'Ambrosio's exterior | RF (0, +4, deck Z) | ✅ built (riverfront) |
| IV | Emperor | Dante (sepia throne / boat helm) | **Helm cabin on the riverboat** | Already part of D'Ambrosio's exterior | RF (0, +9, upper deck Z) | ✅ built (riverfront) |
| V | Hierophant | Quentin/Paul (Sunday circuit) | **St Jude's Catholic Church** | Lafayette parish church: stucco facade, single steeple ~24m tall, hipped tin roof, rectory beside | SR12-side (-200, +200) | ✅ placed |
| Va | Hierophant | (circuit pt) | **Park bandstand** | Octagonal gazebo, cypress posts, copper-green hexagonal roof, between SR12 and the RF zone | (-150, +120) | ✅ placed |
| Vb | Hierophant | (circuit pt) | **Old Armory** | Brick + arched windows + crenellated tin roof, southern Lafayette National Guard style | SE-IND (+200, -340) | ✅ placed |
| VI | Lovers | Sanctuary on Cursed Ground | **Roadside chapel** | Tiny limestone chapel on raised mound in the cane fields, single bell tower, walled garden | CANE-W (-560, -120) | ✅ placed |
| VII | Chariot | TBD (the drive) | **Old Lacombe Service Garage** | Two-bay gas station + repair garage, painted-yellow concrete brick, vintage pump island, tow truck parked | SR12 (-180, -160) | ✅ placed |
| VIII | Strength | (lion-tamer, gentle) | **Abandoned Carnival Lot** | Sun-bleached merry-go-round + faded big-top tent + striped ticket booth + a long wagon for the lion cage (empty) | NW (-460, +400) | ✅ placed |
| IX | Hermit | TBD (the retreat) | **Bayou Lighthouse** | 18m tall whitewashed brick lighthouse on a cypress-pile platform, single dwelling at the base, deep south end of the bayou | BAYOU (+50, -380) | ✅ placed |
| X | Wheel of Fortune | TBD (the turn) | **Le Roulant casino** | Glassed-in storefront with neon wheel on the parapet, ex-bank building (limestone columns, ornate cornice) | (-200, +300) at SR12 north end | ✅ placed |
| XI | Justice | Erica + Anna | **Graustark Parish Courthouse** | Italianate town courthouse: square brick block + clock tower at one corner + four-column portico facing the town square | (-130, +250), the actual town square anchor | ✅ placed |
| XII | Hanged Man | Natalie (Simon's apartment) | **Simon's apartment building** | 3-storey brick walk-up, narrow shotgun proportions stacked vertically, fire escape on the front facade | BQ (-320, +98) — south end of FQ row | ✅ placed |
| XIII | Death | Ward C, Walpurgisnacht | **Graustark Parish Hospital + Asylum Wing** | Two-wing institutional building: brick hospital block + the older "Ward C" wing in faded green tile, broken-paned cupola | SW-IND (-460, -340) | ✅ placed |
| XIV | Temperance | Frank (Tuesday observation) | **The Mixing Glass cocktail lounge** | Narrow 2-storey building, no windows on the street face, single neon "THE MIXING GLASS" sign, hidden entrance down a side alley | BQ (-310, +130) — east of FQ row | ✅ placed |
| XV | Devil | Gumbo Limbo / Daigle's | **Daigle's Roadhouse** | One-storey cinderblock bar at the south HWY 90 strip, two ratty pickup trucks always out front, peeling "DAIGLE'S" sign, neon Schlitz | SE-IND (+260, -380) | ✅ placed |
| XVI | Tower | Evangeline (render queue) | **WGUR Broadcast Tower** | 90m red-and-white guyed radio tower on a small concrete pad, attached single-storey transmitter shack | NE-IND (+400, +380) | ✅ placed |
| XVII | Star | Glass Skin, Christian Ice | **Christian Ice Co.** | A 1950s ice plant: concrete brick facade, ICE in tall painted letters on the parapet, glass-fronted retail door, refrigerated truck dock | SE-IND (+180, -300) | ✅ placed |
| XVIII | Moon | Natalie (sigils in static) | **The Static Drive-In** | Single-screen drive-in cinema with massive blank white screen facing the parking lot, snack bar, neon-red marquee at the entrance | NW (-500, +200) | ✅ placed |
| XIX | Sun | Frank (dust motes) | **Solenade Memorial Garden** | Walled garden with a single oak in the center, brick paths, simple bronze sundial, low limestone bench wall | (-120, +120) east of bandstand | ✅ placed |
| XX | Judgement | Ensemble (dust notes) | **Graustark Parish Cemetery (above-ground)** | Above-ground tomb city: 40-60 raised cement vaults, narrow walkways, single large mausoleum at the center, all WHITE-bleached | (-360, -200) west of riverfront, just south of FQ | ✅ placed |
| XXI | World | Frog Knows Best | **Frog Knows Best — Aquarium & Bait Shop** | Small wooden roadside aquarium + bait shop, painted frog above the door, tin roof, screened porch | (+150, +300) east edge | ✅ placed |

## Notes by archetype

### "Already built" status
The four locales marked ✅ are inside the riverfront preservation
zone and ship with the existing `build_riverfront.py` output. No
new geometry required.

### Hierophant circuit
Canonically the Hierophant has SIX exterior touchpoints
(`_VOL5_WIKI.md`: "St Jude's Catholic Church, the black car, Table
17 of D'Ambrosio's (Sunday brunch), the park bandstand, the old
armory, the riverfront"). Table 17 sits inside the riverboat;
the black car is a propscape detail; the riverfront is shared.
The three NEW exteriors are church + bandstand + armory.

### Major narrative anchors (priority order)
If we have to choose what to build first:

1. **Cathedral of Rust and Code (Magician)** — vol5 climax locale,
   the anchor for Frasier's whole arc. Must be visible from
   anywhere in town as a silhouette.
2. **St Jude's + bandstand + armory (Hierophant)** — the Sunday
   circuit gets walked through canonically; these need to read
   from any angle.
3. **Daigle's (Devil)** — Gumbo Limbo cycle, key narrative
   gravitas, single-pose cinder-block roadhouse.
4. **Courthouse (Justice)** — the town square anchor; everything
   else organises around it visually.
5. **Hospital + Ward C (Death)** — Walpurgisnacht canonical setpiece.
6. **Cemetery (Judgement)** — already in plan; above-ground tombs.
7. The rest fall into background-detail tier.

### Foundation handling
Per the Graustark plan, "tall foundations" are CORRECT here (this
is delta country). Specifically:
- All bayou-side cottages (LEV-W zone) ride on visible cypress
  pilings 1.8-2.5 m tall.
- Hospital + Asylum on the SW dry plain — slab on grade, no
  pilings.
- Cathedral of Rust on the NE plain — slab on grade.
- Lighthouse — concrete platform on cypress piles in the bayou.

### Film-set theory
The Montreal block, Bourbon Quarter row, and abandoned carnival
all use the film-set approach already established in commit
`35dedaa`: detailed front facades, simplified back walls. Apply
the same rule to: drive-in screen (back is blank), broadcast
tower (only the silhouette matters), and any building further
than ~80m from a player walk path.

### What CHANGES on later passes
This is a v1 mapping. Later passes may shift coordinates to
resolve overlaps, adjust zone boundaries, or reassign locales
between zones. The CANON column (arcana → anchor → name) is
fixed; the coordinates and styles are subject to revision until
the locale is built and signed off.

---

*Filed 2026-06-16. Companion to `_GRAUSTARK_DEEP_BUILD_PLAN.md`
and `_TAROT_LORE.md`.*
