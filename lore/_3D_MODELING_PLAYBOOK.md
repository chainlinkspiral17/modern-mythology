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

### TEMPLATE for next session

```markdown
### YYYY-MM-DD · <session focus>

- **<headline lesson>.** <one-sentence summary of what went wrong /
  what we learned, plus the rule that came out of it>.
- ...
```
