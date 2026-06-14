# Locale Design Manual · Modern Mythology

The canonical build order for every locale in this project,
established 2026-06-14 after the HCE district pass made the cost
of doing it any other way obvious.

> **THE LAW.** Topography is built first. Water is built second.
> Roads are laid against the terrain — not against a flat plane —
> third. Foundations sit on the terrain fourth. Infrastructure,
> buildings, and details follow. Build in this order or pay for it
> in re-work.

This manual is required reading before starting any new locale.
Both the riverfront and the HCE district learned the same lesson
the same way: lay roads against an imaginary flat plane, then
discover later that the terrain disagrees and the roads now float
or sink. Don't do that twice.

## Why topography first

Topography is the slowest thing to change once anything sits on
it. A road laid at z = 0 has to be lifted segment by segment if
the ground later acquires a 1° slope. A building dropped at
ground_z = 0 has to be re-rooted if the lot it sits on later
rises 2 m. Crosswalks painted on a flat intersection look broken
the moment the intersection becomes a saddle.

Topography is also the thing that gives a place its character.
HCE is not "suburban houses on flat ground." HCE is "suburban
houses on a 1-3 % grade with a creek dip dividing two halves of
the neighborhood." Graustark is "a riverbank with a 2.5 m drop
from the road to the water." Smolvud will be "the Oregon cliffs."
The terrain is the locale's identity. Build it first; everything
else is dressing on the terrain.

## The seven-step build order

1. **Topography.** Hills, ravines, slopes, plateaus. Define an
   `elevation(x, y) → z` function in the build script (or import
   it from the locale's landscape_sim parameters). Subdivide a
   ground plane finely enough that the function reads (~20 m
   cells is enough for an HCE-scale district; ~5 m cells for a
   sub-sector zoom-in).

2. **Water.** Rivers, creeks, ponds, drainage swales. Water bodies
   carve into the topography — the creek's flood-plain is part of
   the heightmap, not a sticker on top. Render the water surface
   as a separate plane at its surface elevation; the topography
   already provides the channel.

3. **Roads.** Lay road centerlines as polylines. **Sample the
   elevation function at every road vertex** — don't drop roads
   at z = 0 onto a hilly heightmap. For long segments crossing a
   slope, subdivide the segment into 3-5 m pieces and sample
   elevation at each subdivision so the road follows the grade.

4. **Foundations.** Building footprints sit at
   `z = elevation(building_cx, building_cy)`. A house on a slope
   uses a stepped foundation; a clubhouse on a hilltop uses
   `elevation(cx, cy)` as its base z. NEVER hard-code a foundation
   z of 0.0 in a build script that has a non-flat topography.

5. **Infrastructure.** Sidewalks, curbs, utility poles, fire
   hydrants, mailboxes, signs, lampposts. All sample the terrain
   for placement just like buildings. Fixtures along a sloped
   road tilt with the road (or we accept low-poly "step" placement
   for now and revisit later).

6. **Buildings.** Walls, roofs, signage, fixtures. Built on top of
   the foundation z. Materials are vertex-colour zoned per the
   _3D_MODELING_PLAYBOOK rules.

7. **Details / dressing.** Trees, benches, picnic tables, parked
   cars, the watch-detail flyer. Trees follow the terrain. Benches
   sit at sidewalk z. The one-detail-wrong beat is placed last,
   intentionally.

## The elevation function pattern

Every locale's build script declares (or imports) one function:

```python
def elevation(x, y) -> float:
    """Returns the ground z at world (x, y) in meters.
    Used by every downstream pass — roads, foundations, fixtures,
    trees, water-table calculations."""
    ...
```

Examples that have landed:
- `build_harmony_district.py · hce_elevation()` — NW country-club
  rise + creek flood-plain dip + fbm noise + NW-to-SE tilt.
- `landscape_sim/estuary_one.py · hce_elevation()` — same function,
  used by the planning previewer so the 2-D map and the 3-D build
  agree on every grade.

A locale built without an elevation function is built on a flat
plane; that's only OK for an indoor scene (the diner) where the
floor IS the locale. Outdoor locales always declare elevation.

## The water function pattern

For locales with water (rivers, creeks, ponds), declare:

```python
WATER_POLYLINE = [(x0, y0), (x1, y1), ...]
WATER_SURFACE_Z = -0.8     # absolute meters

def water_distance(x, y) -> float:
    """Closest distance from (x, y) to the water polyline.
    Used by elevation() to carve the flood-plain dip, and by the
    road-placement code to choose where bridges go."""
    ...
```

The `elevation()` function then bakes a dip near the polyline:

```python
def elevation(x, y):
    base = ...
    creek_d = water_distance(x, y)
    dip = -1.2 * math.exp(-creek_d * creek_d / (FLOOD_WIDTH ** 2))
    return base + dip
```

This couples water to topography correctly — the creek IS in the
ground, not painted over it.

## Road placement against terrain

The infra_library's `road_segment`, `suburban_drive`,
`highway_segment`, `four_way_intersection`, etc. currently accept
a single `z=0.0` parameter. For terrain-following roads, the
caller should subdivide the polyline and emit short segments:

```python
def road_following_terrain(name, p0, p1, width, elevation_fn,
                           sub_len=4.0):
    """Subdivide (p0, p1) into sub_len-long pieces and emit a
    road_segment for each, with z sampled from elevation_fn at
    the midpoint of each piece."""
    x0, y0 = p0; x1, y1 = p1
    total = math.hypot(x1 - x0, y1 - y0)
    n = max(1, int(total / sub_len))
    for i in range(n):
        t0 = i / n
        t1 = (i + 1) / n
        sp0 = (x0 + (x1 - x0) * t0, y0 + (y1 - y0) * t0)
        sp1 = (x0 + (x1 - x0) * t1, y0 + (y1 - y0) * t1)
        mid = ((sp0[0] + sp1[0]) / 2, (sp0[1] + sp1[1]) / 2)
        road_segment(f"{name}_{i}", sp0, sp1, width,
                     z=elevation_fn(*mid))
```

This is the canonical pattern. Use it (or write the equivalent in
infra_library when we add the elevation-aware variants) instead of
laying roads flat on a hilly map.

## Foundations on slopes

When a building footprint straddles a grade (~0.5 m elevation
change across the footprint or more), the foundation needs a step
or a retained edge:

```python
# Bad — house floats on the downhill side:
make_box("House", (cx, cy, 0 + h/2), (w, l, h), color)

# Good — house sits on its footprint's average elevation:
foundation_z = elevation(cx, cy)
make_box("House_Body", (cx, cy, foundation_z + h/2), (w, l, h), color)

# Better for steep grades — pour the foundation as a separate box:
ground_z_avg = elevation(cx, cy)
foundation_h = 0.8 if abs(elevation(cx-w/2,cy) - elevation(cx+w/2,cy)) > 1.0 else 0.3
make_box("House_Foundation",
         (cx, cy, ground_z_avg + foundation_h/2 - 0.4),
         (w, l, foundation_h), COL_CONCRETE)
make_box("House_Body",
         (cx, cy, ground_z_avg + foundation_h/2 + h/2),
         (w, l, h), color)
```

## Bridges and topography

Bridges are where roads cross water. Place them where:
- A road polyline and a water polyline intersect (within the
  road's width), AND
- The terrain on both sides supports an abutment elevation.

The `infra_library.bridge()` function takes a deck height
parameter — that's the deck z above the lower abutment. For HCE
the typical creek is at z ≈ -0.8 with bank tops at z ≈ 0, so a
deck at z = 1.6 reads as a normal road-grade overpass.

## Checking your work

Before exporting the GLB:

1. **Visualize the heightmap.** Run `estuary_one.py` (or equivalent
   sim) and confirm the contour lines match what you intend. Don't
   skip this step.

2. **Walk the map mentally.** Pick three points — a high ground
   landmark, a low ground landmark, a creek-side spot. Do their
   elevations differ as you expect? If the country club isn't
   on a hill, your elevation function isn't doing what you think.

3. **Drop a test object** at each test point with z = elevation(x, y)
   + 1.0 and confirm in Godot it sits 1 m above the visible ground.
   This catches "the elevation function gave the right numbers but
   my code is using the wrong sign" bugs early.

4. **Sample a road.** Drop a road_segment along a known slope
   (e.g. west arterial near the country club rise) and confirm
   in Godot the road follows the grade. A flat road on a slope
   reads as obviously broken.

## Settlement flattening + prosperity tiers

Per the 2026-06-14 session: **humans build on relatively flat
land; wild zones between them keep the topographic drama.** The
elevation function must respect this:

1. Compute the raw base terrain (hills, ravines, noise) normally.
2. Detect whether the point falls inside (or near) a settlement
   zone — typically a rectangular polygon with a smooth falloff.
3. If so, blend the base elevation toward a per-zone `target_z`
   platform. Flatness 0.70–0.85 inside the zone is the sweet
   spot; 1.0 reads as artificially perfect, 0.5 reads as
   not-flat-enough.
4. Smoothstep the blend over ~35 m so the transition between
   "platform" and "wild" reads natural.

**Tier the target_z by prosperity.** Higher altitude = higher
status in HCE:

| Zone                         | target_z |
|------------------------------|----------|
| Country Club + Golf          | +22 m    |
| North Commercial Belt        | +14 m    |
| North Ranch Homes            | +12 m    |
| East Cul-de-sac Estates      | +8 m     |
| East Commercial              | +5 m     |
| Harmony Park                 | +1 m     |
| Phase II construction        | +1 m     |
| West Commercial Strip        | -2 m     |
| West Estates                 | -3 m     |
| Phase III construction       | -8 m     |
| South Commercial / Truck Stop| -9 m     |

The hierarchy reads visually: walk from the truck stop up the
length of the district and you climb 30 m to the country club.

## Wild-zone features — ponds, pools, mini-valleys

The IN-BETWEEN spaces (creek corridor, Founders Grove, Wild Lot,
the east woods, the SE basin) should NOT be uniform lawn. Punch
in pond depressions, mini-valleys, drainage swales — features
that make the unbuilt zones feel like a real landscape.

Each pond is a circular Gaussian dip:

```python
PONDS = [
    ("FoundersPond",   -300,  160,  25,  5.0),
    ("HarmonyPond",      30,   80,  18,  3.0),
    ...
]

# In hce_elevation():
for (_n, cx, cy, r, depth) in PONDS:
    d = math.hypot(x - cx, y - cy)
    base += -depth * math.exp(-d * d / (r * r))
```

Ponds inside settlement zones get FLATTENED out by the
settlement_blend pass (which is fine — the Harmony Park "pond"
is really the community pool, a constructed water feature, and
should sit at platform z anyway). Ponds in wild zones survive
into the final terrain.

## Berms — the suburban view-blockers

Per user direction (2026-06-14): "suburbs have lots of artificial
slopes and hills to obstruct views of homes, brick fences and the
like." Real planned communities use:

- **Earth berms** along property lines + arterial frontages,
  typically 1.5–2.5 m tall, to screen homes from cars.
- **Brick privacy walls** at the same locations on commercial
  frontage and gated subdivision entrances.
- **Black iron lattice fencing** along amenity edges (golf course
  perimeter, pond/lake-facing backyards, the wrought-iron pattern
  the HOA spec mandates).

Berms are PART OF the elevation function — they're terrain.
Place them as polylines with a width (Gaussian falloff distance)
and a peak height. Apply AFTER settlement-flatten so the berm
sits on the flat platform's edge, not inside it.

```python
BERMS = [
    ("CC_Buffer",       [(-460, 340), (440, 340)],  14.0, 2.5),
    ("NorthRanch_Front",[(-460, 270), (-200, 270)], 10.0, 1.8),
    ...
]

# In hce_elevation, after settlement_flatten:
for (_n, polyline, width, height) in BERMS:
    d = polyline_dist(x, y, polyline)
    base += height * math.exp(-d * d / (width * width))
```

Brick walls and iron lattice fences are GEOMETRY — they sit on
the terrain. Use `infra_library.brick_wall(p0, p1, ...)` and
`iron_lattice_fence(p0, p1, ...)`. The library's iron-fence
primitive includes vertical bars + horizontal rails + thicker
posts at regular intervals + ball finials — the canonical HCE
wrought-iron pattern.

**The wall vs fence rule:**
- Backyard faces an arterial / commercial → BRICK WALL (privacy)
- Backyard faces a pond / golf course / park → IRON LATTICE
  FENCE (so the amenity view remains)
- Front yard → no fence; berms + landscaping do the job.

## When to break the rule

The rule "topography first" applies to OUTDOOR locales. Indoor
locales (diner, riverboat interior, model home interior) ARE
their own topography — the floor is the floor; there's no
"elevation function" to sample. Build the floor as a flat plane
and put everything on it.

Mixed locales (a house whose front lawn slopes to the road, a
cabin overlooking a ravine) follow the rule for the outdoor
portion and become flat on entry. Drop a `LocaleSetup.gd` script
node at the indoor threshold to handle the y-snap if needed.

## Cross-references

- `_3D_MODELING_PLAYBOOK.md` — vertex-colour zoning, coordinate
  frame, primitive shapes, polycount budgets.
- `_LIGHTING_PLAYBOOK.md` — three-light cinematography, sun
  rotation by hour, practical fixture placement.
- `_SHADER_VISUALS_PLAYBOOK.md` — screen-space filter family,
  mood presets, post-process stack order.
- `_HCE_TOPOGRAPHY.md` — the HCE-specific terrain brief (creek
  path, country club rise, district sub-regions, seasonal
  palette).
- `godot/tools/landscape_sim/estuary_one.py` — the planning
  previewer that visualizes elevation + roads + landmarks before
  any geometry is built.
- `godot/tools/blender/locales/infra_library.py` — reusable road
  and civic furniture primitives. Roads in this module currently
  take a fixed `z` parameter; the canonical pattern above (terrain
  subdivision in the caller) is required until the library grows
  terrain-aware variants.
