# Harmony Creek Estates · Topography & Design Brief

The next locale set. Vol context, the suburbia in the volume where
the watchers watch and the surfaces lie. Brief from the user
2026-06-14:

> A green to yellow suburban sprawl from the start of summer
> vacation to the end of summer vacation. It has manicured lawns
> and maintained creeks and waterpathways with large natural
> parks and public pool complexes. A golf course maybe, skateparks
> and parks in general. Watched over by all. Drama and intrigue
> around every corner.

## Topographic foundation

**Relatively flat, but never truly level.** Per established lore
(see _3D_MODELING_PLAYBOOK.md): HCE and Graustark share "relatively
flat" topography — Smolvud carries the dramatic Oregon cliffs. For
HCE that means rolling 1–3% grades sufficient to motivate:

- A creek that actually flows (Harmony Creek) — meandering NW to SE
  through the middle of the district.
- A subtle high point where the country club / golf course sits
  (~6m above creek level).
- Lower-elevation cul-de-sacs nestled along the creek's flood plain.
- Storm drainage that visibly works — gentle swales between lawns.

No clifs, no terraces. The land reads "manicured nature" — every
contour planned, every slope mowed, never a wild edge.

## The seasonal palette

Calendar runs **early-June crisp green → late-August parched
gold**. The same locale needs to read both ways via a
build-script parameter (or a per-mesh vertex tint pass that the
runtime modulates).

| Element                | Early summer (June) | Late summer (August) |
|------------------------|---------------------|----------------------|
| Lawns                  | (0.22, 0.55, 0.18)  | (0.68, 0.62, 0.22)   |
| Trees (oak, maple)     | (0.18, 0.38, 0.16)  | (0.42, 0.40, 0.18)   |
| Creek-edge reeds       | (0.32, 0.52, 0.22)  | (0.65, 0.52, 0.20)   |
| Golf-course greens     | always (0.16, 0.48, 0.18) — irrigated |
| Concrete (sidewalks)   | (0.72, 0.70, 0.66)  | (0.72, 0.68, 0.58) (sun-baked) |
| Sky background         | (0.55, 0.68, 0.85)  | (0.78, 0.75, 0.62)   |
| Asphalt                | (0.20, 0.20, 0.21)  | (0.25, 0.23, 0.20)   |

Implementation: `SEASON ∈ [0.0, 1.0]` parameter at the top of every
HCE build script. June = 0.0, August = 1.0. Vertex colours
interpolate between the two palettes via a `lerp_palette(season,
green, gold)` helper. One script, two looks, gradual narrative arc.

## Spatial layout (rough)

District is ~600 m × 400 m, centered on the creek. Four district
sub-regions:

```
          ┌──────────────────────────────────────────────┐
          │  NORTH  ·  Country club + golf course        │
          │  (high ground, ~6m above creek)              │
          │                                              │
          ├───────  Hilltop Road  ────────────────────┤
          │                                              │
          │  WEST              CENTRE          EAST      │
          │  Single-family     Town park       Cul-de-sac│
          │  ranch homes       + pool complex  subdivisions
          │  on quiet loops    + bandshell     (gated)   │
          │                                              │
          ├─── ─── ─── HARMONY CREEK (winding) ─── ─── ─┤
          │                                              │
          │  SOUTH                                       │
          │  Skate park, basketball courts,              │
          │  Pop Warner fields, "the woods" (lightly     │
          │  managed natural park)                       │
          │                                              │
          └──────────────────────────────────────────────┘
```

## Locale build sequence

The user's stated priority is 1 → 2 → 3 progression. Suggested
sequence:

**HCE-1 · Harmony Park & Pool Complex** (the bandshell area)
The community heart. Bandshell, picnic shelters, swimming pool
complex with chain-link fence, lifeguard chair, snack-shack
concession, a public restroom block, a flag pole, a "Welcome to
Harmony Creek Estates" monument sign at the park entrance.
Manicured lawn, oak shade. Watch-tower-ish lifeguard chair sells
the "watched over by all" beat without being heavy-handed.

**HCE-2 · The Estates Entrance** (subdivision gateway)
Stone-and-brick monument signs flanking the entry road, planted
median with annuals, a model home behind a manicured display lawn,
a mailbox cluster, a hedge row. The architecture says "you have
arrived somewhere worth knowing." The drama beat: a single
detail off — a flag at half-mast, a yard sign for a missing dog,
a flyer stapled to the model home post. Suggests but never tells.

**HCE-3 · Harmony Creek Crossing** (the creek itself)
The creek's flood-plain corridor: a concrete pedestrian bridge,
willow trees, a paved trail along the bank, a few benches, a
storm drain outfall. Water tinted summer-warm. Reeds at the edge.
A children's play area on one side; a quieter natural-park feel
on the other. The creek is the spine that links the rest.

**Future HCE locales** to fill in after the spine is built:
- HCE-4 · Golf course clubhouse + putting green (the high ground)
- HCE-5 · Cul-de-sac residential loop (gated subdivision)
- HCE-6 · Skate park + adjacent woods edge
- HCE-7 · Single-family ranch street (west side)

## Watched-over-by-all design notes

For the "drama and intrigue around every corner" beat without
turning the asset library into a horror set:

- **Sightlines.** From the bandshell you can see the pool complex
  + the playground + half the main road. From the country club
  parking lot you can see down into both subdivisions. The
  cul-de-sac houses face inward. Visibility is the gentle threat.
- **Cameras and signs.** "Neighborhood watch" yard signs at most
  street entries. A blue stick-on alarm-company sticker on most
  homes. A discreet pole-mounted camera at the pool entrance.
  Never the dominant feature; always present.
- **One detail wrong per scene.** A single off-detail in each
  locale — a tipped-over flag, a curtain drawn at the wrong
  window, a single overgrown lawn in a row of manicured ones, a
  beat-up car in the country club lot, a flyer that doesn't fit
  the rest. The eye finds it. The reader notices.
- **Hedges and fences as MASS.** Hedges are dense, dark, somewhat
  too-tall. Fences are tall enough that you can't quite see over
  the next yard. The community is closed off in small ways.

## Shared HCE module conventions

Once the first build script lands these become canonical:

| Constant         | Value      | Meaning |
|------------------|------------|---------|
| `CREEK_Z`        | -1.40      | Water surface (Blender Z-up) |
| `BANK_Z`         |  0.00      | Creek-bank top (datum) |
| `LAWN_Z`         |  0.00      | Standard lawn elevation |
| `HIGH_GROUND_Z`  |  6.00      | Country club / golf course |
| `ROAD_W`         | 11.0       | Two-lane residential road |
| `SIDE_W`         |  1.8       | Standard sidewalk |
| `BUFFER_W`       |  2.5       | Planted strip between sidewalk and lawn |
| `SEASON`         | 0.0 → 1.0  | June → August palette interp |

Pipeline carries forward from the riverfront:
- Vertex-colour materials → screen-space lithograph shader
- KEY/FILL/BACK three-light + practicals at every visible fixture
- Lobster cursive for any signage with character ("Welcome to the
  Estates"); civic-sans for utility signage (street names)
- Sat-gated bleed mode for the lithograph mood
- Infrastructure-grid rule: nothing in road right-of-way

## What I'd build first

If you give the word, I'll start `build_harmony_park.py` —
the Harmony Park + Pool Complex (HCE-1). It establishes the
seasonal palette plumbing, the road/sidewalk/lawn elevation
constants, the watch-tower-and-amenity vocabulary, the first
"manicured public space" template. Once that's reading right,
HCE-2 (entrance) and HCE-3 (creek) get faster.

Confirm or redirect — and tell me whether to start at SEASON =
0.0 (early summer green) or SEASON = 0.6 (mid-July, the canonical
"watched over" peak heat).
