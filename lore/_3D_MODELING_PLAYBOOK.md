# 3D Modeling Playbook · Modern Mythology

A working record of what we've learned about building this project's
locales in Blender → glTF → Godot. Refresh this file after every
significant modeling session — add the new rules in the
"Recent lessons" section at the bottom, and graduate stable rules up
to the "Core rules" section over time.

## How to use it

Before starting any new 3D modeling work, read the Core rules and the
last two "Recent lessons" entries. They will save you from re-making
mistakes that took specific user feedback to discover.

## Core rules

### Coordinate frame — Blender Z-up vs Godot Y-up (MUST READ)

**Same units (meters), different up-axis.** The build scripts use
Blender's native Z-up convention; the Godot runtime uses Y-up. The
default glTF exporter remaps on the way out:

| Blender axis (build script) | Godot world axis (runtime) |
|------------------------------|----------------------------|
| `+X` (east)                  | `+X` (east)                |
| `+Y` (north / forward)       | `-Z`                       |
| `+Z` (up)                    | `+Y` (up)                  |

A Blender position `(x_b, y_b, z_b)` lands in Godot world at
`(x_b, z_b, -y_b)`. A Blender direction vector remaps the same way.

**Scale is consistent — 1 unit = 1 meter in BOTH runtimes.** Do not
introduce scale factors in either; if something looks the wrong
size, find the bad number, don't compensate via transform.

**Implications for cross-runtime code** (e.g. `LocaleSetup.gd`
positioning Label3D nodes on panel meshes baked from the build
script):

- Mesh AABBs in the imported GLB are in Godot world coordinates.
  `panel.global_transform.origin + panel.get_aabb().get_center()`
  gives the correct world position with no manual remap.
- But ANY hand-written direction or offset vector (face normals,
  push-out offsets) in runtime code MUST be in Godot frame. A panel
  the build script faces toward Blender +Y faces toward Godot -Z at
  runtime — be explicit. (Bug we hit twice: passing Blender-frame
  face normals into Label3D basis builders. Symptom: text rotated
  90° around the panel's face axis. Fix: write face normals in Godot
  frame and use `world_up = Vector3(0, 1, 0)`.)
- For sanity-checks: a 1.7 m player capsule, a 12 m wide boat, a
  2 m tall sign panel — these dimensions read identically in both
  runtimes. If a measurement is off, the bug is in the build, not
  in the conversion.

**If you find yourself doing the remap by hand often**, add a
helper to LocaleSetup like:

```gdscript
func blender_to_godot(v: Vector3) -> Vector3:
    return Vector3(v.x, v.z, -v.y)
```

and document where it's used. **Do not** scale, only remap axes.

### Primitive selection — never reach for `make_box` first

The project's lowpoly aesthetic looks like Atari 2600 if everything is
axis-aligned boxes. Pick the right primitive for the shape:

| Shape                      | Use                          | Don't use                   |
|----------------------------|------------------------------|-----------------------------|
| Cloud, foliage canopy      | `make_sphere` clusters       | stacked `make_box`          |
| Lifebuoy, ring, halo       | `make_torus`                 | 12-segment box loop         |
| Smokestack, pole, column   | `make_cyl` (segments ≥ 8)    | tall thin box               |
| Sloped roof, lamp shade    | `make_prism`                 | stacked boxes               |
| Ramp, gangway, slope       | `make_ramp`                  | rotated box, stacked boxes  |
| Diagonal line, neon stroke | `make_tube_segment`          | axis-aligned box (stair-steps!) |
| Rounded car body           | `make_box` slab tiers OK     | (acceptable here)           |
| Trunk, branch, pipe        | `make_cyl` or `make_tube_segment` | thin box           |

If a shape needs a diagonal, curved, or organic edge, **do not** use
`make_box`. Reach for the right helper.

### Shaders are at screen level only

All visual effects come from the screen-space CanvasLayer post-process
stack. **Do not** assign per-mesh shaders to locale geometry — use
`StandardMaterial3D` with `vertex_color_use_as_albedo = true` and let
the screen shaders carry the look. LocaleSetup defaults to this and
should not be changed.

Active post-process stack (in render order):
1. **`ascii_render.gdshader`** — samples each cell of the screen and
   renders one of 10 ASCII glyphs based on luminance. The substrate
   look. Strength driven by MoodCycler per mood.
2. **`demoscene_post.gdshader`** — palette quantize, Bayer dither,
   scanlines, chromatic aberration.

Old shaders (`ascii_edges`, `glyph_field`) exist on disk but are no
longer wired into scenes. The "edges + drifting glyph field" approach
produces snow, not a working effect — do not bring them back.

### Reference proportions (Mississippi steamboat / dock / river)

Real proportions our build keys off of (Belle of Louisville, Natchez
IX). When you see something looking small or wrong, suspect scale:

| Element            | Real reference  | Our build (current) |
|--------------------|-----------------|---------------------|
| Boat length        | 58–80 m         | 24 m (under)        |
| Boat beam          | 12 m            | 12 m                |
| Boat height        | 12–15 m         | ~14 m               |
| Paddle wheel diam. | 6 m             | 4.8 m               |
| Dock above water   | 0.3–0.5 m       | 0.35 m              |
| Pilings proud      | 0.3–0.6 m       | 0.50 m              |
| River width        | 100–200 m       | ~80 m clear lane    |

### Layout — port vs starboard

Boat bow at +Y (north / upriver), stern at -Y (paddle wheel here).
Port = -X side, faces the dock and parking lot.
Starboard = +X side, faces the open river and the opposite shore.
**Never** put the dock at the same end as the paddle wheel.
**Never** put dock + parking lot on the same side as the open river.

### Dock above the waterline

The dock deck MUST sit visibly above `RIVER_LEVEL_Z` (use `DOCK_Z`
constant). Pilings run from below the riverbed UP THROUGH the deck
and stand 30–60 cm proud with darker caps. Gangway from boat to dock
slopes via `make_ramp` (real gangways are 15–25° pitched, never flat).
Ramp from dock to land at the other end.

### Bayou navigability

Bayou foliage must leave a navigable channel down the center wide
enough for a riverboat or two to pass. With `BAYOU_X = 55`, no cypress
should be placed at `|x - BAYOU_X| < CHANNEL_HALF + jitter`. Tree
placement uses Poisson-style rejection sampling with min-distance,
not a hand-typed grid.

### Tree species diversity

A locale's foliage must use multiple species with **randomized scale
0.7–1.4**. Don't paste the same tree builder 26 times. The bayou uses
5 species (bald cypress, water tupelo, live oak, palmetto, dead snag)
with a weighted random selector. Opposite shore uses 3 (cypress,
pine, oak).

### Sign mirroring for two-sided neon

For a sign that reads correctly from both faces, the mirror function
is `lx(local_x) = -local_x * face_sign`. **Both** the negation and
the face_sign multiplication are required — neither alone gives
correct text on both sides.

### Sign neon halos go BEHIND letters

Halo spheres inset toward the panel face (`face_y_off - offset *
face_sign`), never out in front. Halos in front occlude the letters
themselves and look like floating red dots.

### Underline arc geometry

For a "swoosh" underline below the baseline, use parametric points
with `z = baseline - sin(t * π) * dip` — do NOT use an `add_arc`
with a large radius and theta near π/0, which produces an arc that
peaks ABOVE the letters instead of below.

### Build script structure

- Helpers at top: `clear_scene`, `make_box`, `make_cyl`,
  `make_sphere`, `make_torus`, `make_tube_segment`, `make_prism`,
  `make_ramp`, `_finalize_mesh`.
- Constants below helpers: layout positions (`PARKING_X`, `BAYOU_X`,
  `OPPOSITE_X`, `DOCK_Z`, etc.).
- One `build_<region>()` function per logical area.
- `export_glb()` at the bottom using the version-safe RNA probe
  for `export_colors`/`export_normals`, `export_lights=False`,
  `export_cameras=False`.

### Blender export quirks

- `export_apply=True` bakes rotations into mesh vertex positions
  (important — the GLB doesn't carry Blender object rotations).
- `export_colors` and `export_normals` are flags that may or may not
  exist depending on Blender version. Use the RNA probe pattern.
- Cameras are NEVER exported — they hijack Godot's active camera.
- Lights are NEVER exported — set up real `Light3D` nodes in the
  `.tscn` instead.

### Use references, not memory

When modeling something real (boat, bridge, building, vehicle), cite
the reference in a code comment ("modeled after the Belle of
Louisville's hurricane-deck proportions"). Don't guess at numbers.

## Recent lessons

### 2026-06-14 · world needs ground + roads BEFORE features

- **A locale is not a set of isolated detail patches.** Every locale
  build should start with TWO foundational functions before any
  buildings, vehicles, or props go in:
    1. `build_ground()` — a continuous ground covering the entire
       world area (~340m × 340m for the riverfront).
    2. `build_road_network()` — driveways, sidewalks, crosswalks,
       access ramps connecting every developed patch to every other
       developed patch.
- **Without these two**, the world reads as floating asphalt islands
  in a gray Godot-void no matter how much detail you pack into each
  individual feature. The user explicitly called this out: "roads
  don't look functional, look at all this null space."
- **Order in main()**: ground first, road network second, THEN every
  feature build overlays on top.

#### Topography per locale (vol5–7 canon)

CORRECTION on previous note: "flat" was wrong. The bayou locales are
**RELATIVELY** flat — they have geology and topography. They are not
perfectly-level planes. The `build_ground()` implementation MUST
respect each locale's canon topography:

- **D'Ambrosio's riverfront** (vol5) — relatively flat bayou bottom-
  land with raised road berms, drainage ditches at lower-than-grade,
  ground that varies a few inches between developed lots / scrub /
  river edge. Not perfectly level.
- **Harmony Creek Estates** (vol5/6) — relatively flat suburban
  lawns with some rolling terrain. Has a CREEK (per the name) which
  means a lower drainage channel running through. Each lawn rises
  slightly off the street to its house.
- **Graustark, TX/LA** (vol5) — relatively flat small-town main
  street, BUT canon: **half of the town sinks into a sinkhole**
  during the story. The sinkhole geometry must be supported by
  build_ground from the start — a tilted / collapsed crater section
  through the town centre, dropping perhaps 8-15m below grade.
  Adjacent buildings lean into the void. Plan terrain accordingly.
- **Smolvud, central OR coast** (vol5/6) — emphatically NOT flat.
  Cold rain forest with dramatic cliffs and structures built on
  wildly varied geology. `build_ground()` for Smolvud needs:
    · Heightmap-style terrain (varied Z), NOT a flat plane.
    · Cliff faces as stacked angled prism walls.
    · Coastal rocky outcrops (sphere clusters + angled boxes).
    · Switchback roads zigzagging up/down elevation.
    · Houses on stilts / perched on cliff edges (the dramatic
      vertical builds the canon calls for).
    · Dense evergreen forest with multi-sphere conifer canopies.
    · A coastline (water at the lowest elevation tier).
  Don't reuse the flat `build_ground` straight from riverfront — it
  will produce the wrong character entirely. Plan a Smolvud-specific
  ground module: `build_terrain_heightmap()` or similar, that
  samples a hand-defined Z(x, y) function and tessellates it.

#### Tools likely needed for Smolvud

- A height-sampling helper: `terrain_z_at(x, y)` returning the
  ground Z at any world coordinate, so every prop (tree, house,
  road segment) snaps to the right elevation.
- A make_cliff() helper: stacked angled prism walls that fake a
  vertical rock face.
- A make_stilt_foundation() helper: 4 cylinders descending from
  a house's footprint down to wherever terrain_z lands.
- A make_switchback_road() helper: zigzag asphalt with painted
  guardrails on the outside edge.

These don't exist yet — call them out when Smolvud begins, and
add to the helper library at the top of the build script.

#### Bayou-city features that are EXPECTED (vol5 Graustark + riverfront)

The user explicitly called out these as required to read as a bayou
city. Build them or it doesn't feel right:

- **Raised roads on low berms** — the road sits a few inches above
  grade so it stays drivable through rain/flood. Suggested visually
  by drainage ditches sitting LOWER alongside, not necessarily by a
  dramatic earthen mound.
- **Drainage ditches** on both sides of every road, with a muddy
  floor and patches of standing tannin water (the bayou water table
  is high, the ditches stay damp).
- **Sewer grates** at curb-line intervals (every 28-30m), steel
  frames with parallel slats.
- **Wear and tear on asphalt** — darker splotches, patches, cracks.
  Real bayou roads are not pristine.
- **Public parks and green spaces** — lawn, picnic tables, swing
  sets, benches, shade trees with Spanish moss, winding concrete
  paths, signage, trash cans.
- **Houses with porches and yards** (for HCE and Graustark).
- **Telephone poles** with crossbars + ceramic insulators + sagging
  power cables strung between them, repeated every ~25m.
- **Streetlights** along the road every ~22m, with arms and lenses
  glowing warm.
- **Mailboxes** on posts along the road shoulder.
- **Fire hydrants** at intersections.
- **Trees lining the road** (cypress / live oak / pine, alternating).
- **Sidewalks** with seam-line concrete texture.

These items move a scene from "scattered objects on a flat plane"
to "actual block in a working town." Skip any of them and the
scene reads as empty.

### 2026-06-14 · the mood-cycler shader system is reusable

- The screen-space mood library (lunch / dusk / chillwave / sunset /
  lithograph / noir / ice / night / 3:47 am / precipice / substrate /
  raw) is locale-agnostic. Any new scene just adds the same three
  ColorRects (NeonQuad → AsciiQuad → Quad) with the same shaders;
  MoodCycler.gd drives them identically. Don't re-invent per locale.
- The HUD MoodLabel pattern (Label node at NodePath("../HUD/MoodLabel"))
  is also reusable — MoodCycler picks it up automatically if it exists.

### 2026-06-14 · cursive_type.py is the type tool for any signage

- The Bezier-based cursive type tool (`godot/tools/blender/locales/
  cursive_type.py`) defines D ' A m b r o s i in cubic Beziers
  with proper kerning and an explicit text_width() helper.
- For future signage (HCE realtor signs, Smolvud roadside markers,
  Graustark storefront names, the diner's interior "WELCOME"), extend
  the GLYPHS dict with the additional letters and call
  `make_neon_dambrosios`-style wrappers for each font face axis.
- A two-face sign (readable from both sides) requires:
    · 'Y' face: lx(x) = -x * face_sign
    · 'X' face: lx(x) =  x * face_sign
  The formulas differ — using one for both produces a correctly
  mirrored panel and an inverted panel. Don't unify them.

### 2026-06-14 · every feature needs a TRANSITION to its neighbours

Recurring failure mode I keep making: I build a feature (parking
lot, dock, gas station, strip mall, riverbank, quay wall, river
basin) as an isolated unit, and forget that **the player needs to
ARRIVE at this feature from another one**. The transitions are
where the world reads as functional vs. dropped-in-from-the-sky:

| Feature pair | Transition needed |
|--------------|-------------------|
| road → parking lot | driveway apron + curb cut, painted lines guiding the turn-in |
| parking lot → dock | stairs (if elevation drop) or ramp; the curb edge isn't a transition |
| highway → frontage road | proper off-ramp with deceleration lane + signage |
| land → river | quay wall OR sloped bank with vegetation, not a hard right-angle drop |
| dock → boat | gangway sloped to span the deck-to-dock height difference |
| sidewalk → building | a step or entrance landing, doesn't just abut the wall |
| commercial strip → residential | something between (a vacant lot, a small park, a fence line); they don't share a property line |

Durable rule:

- **After building any feature, draw an arrow on a mental map FROM
  every other feature TO this one.** If any of those arrows
  doesn't have a transition feature, build the transition before
  calling the feature done.
- **The transition is part of the feature, not optional polish.**
  A parking lot without a road entry is not a parking lot, it's
  a slab of asphalt floating in the world.
- **For the bayou-city locales specifically**, transitions that
  must exist:
    · Every developed lot needs a curb cut + apron to the road
      it sits on (NOT just a sidewalk edge).
    · Every building needs an entry path from the road (walkway,
      stairs, ramp).
    · Every elevation change needs a stair or ramp (the user can
      flag the same "the river is level / there's no transition"
      complaint for any feature, not just the river).

### 2026-06-14 · when a fix doesn't appear, the bug is somewhere ELSE

The "river-sink invisible 6+ times" disaster. User kept asking why
the river still looked level with the land. I kept iterating on
RIVER_LEVEL_Z, bank slopes, dock height — none of which addressed
the actual cause. The actual cause: `build_ground()` was a single
340m × 340m flat box at z=-0.10 covering the ENTIRE world including
the river area. The water surface WAS at z=-2.5 the whole time. It
was just hidden under an opaque ground plane.

Durable rules:

- **When a code change you believe is correct produces no visible
  result, the BUG IS NOT IN THE CHANGE.** Stop iterating on that
  layer. Investigate what's CONTAINING / OBSCURING / OVERRIDING
  the change. Common culprits:
    · An older layer is still rendered on top (this one — ground
      box hiding water below it)
    · The GLB cache hasn't refreshed in the editor (close + reopen
      Godot, or right-click → Reimport)
    · A `material_override` somewhere downstream is replacing the
      material I just set
    · Z-fighting between two coplanar surfaces
- **When you add a new lower / smaller / hole-in-the-world feature,
  REMOVE THE PIECE OF THE OLDER FEATURE THAT'S NOW IN THE WAY.**
  Adding a river basin = split the old ground plane around it.
  Adding a sinkhole = cut the affected ground geometry. Don't
  just stack new geometry on top of conflicting old geometry.
- **If the user has asked for the same fix 3+ times, STOP CODING
  ON THE OBVIOUS LAYER.** Take a step back and look for what
  could be HIDING the change you've already made.

### 2026-06-14 · use Godot Label3D for sign text, not procedural geometry

Procedural tube-letter approaches (cursive bezier sampling, block-
letter strokes, axis-aligned box approximations) ALL smear into
unreadable shapes at the screen post-process resolution at typical
viewing distance. I burned several commits iterating cursive vs
block vs Bezier-resolution vs stroke-thickness on the diner signs.
None worked.

**The right tool**: `Label3D` in Godot. It renders proper font
glyphs at native font resolution, then those pixels go through the
screen post-process at the screen's native resolution — strokes
stay crisp.

Pattern (see `LocaleSetup.gd` for the riverfront implementation):

1. In the GLB, build the sign as a dark BACKING PANEL mesh with
   a recognizable name (e.g. `Sign_Panel_N`, `BoatSign_Panel`).
2. In `LocaleSetup.gd` (or any scene-load script), walk
   MeshInstance3Ds, find the panel meshes by name, attach a
   `Label3D` child with:
   - `text = "D'Ambrosio's"`
   - `font_size = 96`, `pixel_size = 0.008` for ~77cm-tall letters
   - `modulate = Color(0.98, 0.18, 0.20)` (saturated booth red)
   - `outline_size = 6`, `outline_modulate` dark
   - `shaded = false` so it reads as self-lit neon
   - `double_sided = true`
   - Orient via `rotation` for the right face direction
3. Leave the procedural tube-letter library (`cursive_type.py`)
   alone — it's still useful for STYLIZED signage where exact
   legibility isn't the goal (a fragmented "D'A" mark, a glow
   pattern). Just don't use it where the user needs to actually
   read the text.

**Why I missed this for so long**: I treated text as a modeling
problem because the rest of the locale is modeling. It's actually
a font-rendering problem, and Godot has a font system. Use the
right tool instead of bending the wrong one.

### 2026-06-14 · screenshots are how I see the work

- **Always ask the user for a screenshot when debugging visuals.** I
  cannot run the editor or the game. The user's screenshot is the
  only window I have into what the work actually looks like. Concept-
  art references they share are equally valuable — they tell me what
  the target IS, not just what the current state isn't.
- **Specific complaints from a screenshot beat vague complaints by
  10x.** "The D'A is cramped" + screenshot showing exactly that = I
  find and fix the spacing in one round. "Sign looks bad" alone = I
  guess at five possible issues and ship four wrong fixes.
- **Verify cursive / fine detail BY THE SCREENSHOT, not by reading
  the code.** A bug like the missing 's' arc (`theta_start ==
  theta_end` ⇒ no geometry) was invisible in code review but obvious
  the moment the screenshot landed.
- **When the user says "it's not working," ask for a screenshot
  before iterating.** Diagnose visually first, code-edit second.
- **If a build won't show changes, the GLB cache is probably the
  culprit.** Godot caches imported GLBs while the editor is open —
  close the editor, rebuild, reopen. The user's report of "I'm not
  seeing improvements" can mean "the GLB never updated," not "your
  code change was wrong."

### 2026-06-14 · the riverfront pass

- **Boxes everywhere reads as Atari 2600.** The user said "feels
  Atari 2600 aesthetic as a primitive 3D game." The fix isn't more
  polygons — it's using the right primitive for the shape (spheres
  for clouds, torus for rings, tube segments for neon).
- **Without textures, MGS2 is out of reach.** Be honest about the
  ceiling. Procedural cubes with vertex colors caps at "stylized
  lowpoly diorama." If the user wants MGS2-level, they need to
  commission texture assets or accept a different aesthetic.
- **A true ASCII renderer beats overlay tricks.** The `ascii_render`
  shader (sample-per-cell, choose glyph by luminance) gives the
  "substrate" feel of code rendering. The previous approach (edge
  detection + drifting glyph field) produced uniform snow.
- **Cursive neon at lowpoly is hard.** Even with `make_tube_segment`,
  cursive letters at the screen post-process resolution barely read.
  Either accept that the sign is iconographic rather than legible,
  or use block letters for clarity.
- **River width matters for the picture.** Foliage too close to the
  boat makes the river look like a canal. Leave 30+ m of clear
  water beside the boat.
- **Set up lesson-capture as a recurring practice.** The user
  explicitly requested this — see CLAUDE.md cadence note.

### 2026-06-14 · angular hull via custom hex mesh + V-prow

The riverboat hull had three rebuilds in one session:
1. Three stacked boxes → "blocky, Atari-aesthetic" complaint.
2. Add cylinder chines + corner spheres → "poofy, fluffy lil clouds"
   complaint (the same critique that killed the round car-corner
   experiment).
3. Replaced with **ONE hexagonal-cross-section mesh** for the body +
   **ONE V-prow** wedge tapering to a vertical knife edge + a shallow
   `make_v_stern` rake at the back.

The hex hull has 12 vertices (6 per station × 2 stations) and 8
faces: deck top, port upper, port chamfer, keel, starboard chamfer,
starboard upper, plus stern and bow hexagon end-caps. The V-prow is
8 verts → 5 faces (rear hex + top triangle + bottom triangle + port
pentagon + starboard pentagon).

Key insight: **"angular" means flat facets meeting at sharp edges,
NOT smooth curves.** When the user says "PS2 era, not shovelware,"
the goal is faceted-but-purposeful geometry — think the Phantasy
Star Online style or low-poly Twisted Metal. Spheres and high-segment
cylinders are the WRONG tool for hull/car body forms.

Reusable rule for organic-looking objects without textures:
- **For a hull/body/fuselage shape** → custom mesh with hexagonal
  cross-section + tapered ends. ~14-20 verts gets you "stylized
  ship" silhouette at zero polycount cost.
- **For a corner round-off** → a single chamfer face (one prism per
  edge), NOT spheres or rounded cylinders.
- **For a wedge/prow** → custom mesh with one face collapsed to a
  line (V-prow pattern: 6 rear verts → 2 apex verts).

### 2026-06-14 · 3D models will become physical miniatures

The user clarified the long-term goal: **the 3D maps of Graustark,
Harmony Creek Estate, and the surrounding areas are the SOURCE OF
TRUTH for FT's physical miniatures**. Small Wood (a Smolvud
sub-area) will be designed fresh in this same pipeline and carries
forward to future Smolvud planning.

Implications for how we build:
- **Topology choices need to print well.** Thin overhangs, isolated
  floating geometry, and one-vertex-wide protrusions all break in
  a miniature workflow even if they look fine in Godot. When
  modelling something the user might miniaturize, prefer closed
  manifolds and minimum feature sizes ≥ 0.5mm at the print scale.
- **Vertex-color materials translate to paint masks.** The current
  vertex-color-as-albedo pipeline doubles as paint guides — each
  distinct color → one paint pass on the miniature. Use clearly
  distinguishable colors for masks (red booths, white columns,
  brass railings) rather than gradients/blends.
- **Locale-scale models are mini terrain, not heroic minis.** The
  riverboat at hull-scale ≈ 200mm if printed at 1:120 scale (matches
  N-scale gauge). Granularity choices (8-segment cyls, 14-vert
  hulls) read fine at that scale.
- **Maps need to tile or fit on standard footprints.** Graustark
  laid out as a 340m × 340m world maps to ~280mm × 280mm at 1:1200
  (board-game scale) or 700mm × 700mm at 1:500 (terrain-table
  scale). Future locale builds should respect these snapping points.

This is a long-term constraint — don't optimize for miniaturization
prematurely (the game look comes first), but when faced with a
between-equally-OK-options choice, pick the printable one.

### TEMPLATE for next session

```markdown
### YYYY-MM-DD · <session focus>

- **<headline lesson>.** <one-sentence summary of what went wrong /
  what we learned, plus the rule that came out of it>.
- ...
```
