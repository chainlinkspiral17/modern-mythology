# Shaders, Particles, and Screen Visuals Playbook

Hard-won rules for the Modern Mythology visual stack — screen-space
shaders, mood system, post-process ordering, particles (when we get
to them), and the "what tool fits which problem" decisions.

Companion to `_3D_MODELING_PLAYBOOK.md` (which covers Blender →
glTF → Godot geometry pipelines). When a fix involves a shader,
material, particle system, color grading, or post-process, read
this file first.

## How to use it

Refresh this file after every significant session that touches
visuals. Append a dated entry under "Recent lessons" using the
template at the bottom. Stable lessons graduate up to "Core rules"
when they've held across multiple sessions.

## Core rules

### Screen-space shaders only (per user directive)

Locale geometry renders via `StandardMaterial3D` with
`vertex_color_use_as_albedo = true`. All stylization comes from
the screen post-process stack — CanvasLayer + ColorRect + Shader.
**Do not** write per-mesh shaders for locales. (The Cathedral
scene's `gouraud_lambert.gdshader` is a legacy exception for the
baked-light cathedral interior and should NOT be a template for
locale work.)

### Post-process stack order (matters a lot)

The riverfront scene's `PostProcess` CanvasLayer has these
ColorRects, IN THIS ORDER (each shader's `hint_screen_texture`
sees the previous layer's output):

1. **NeonQuad** · `neon_edge.gdshader` — luma-Sobel silhouette
   outliner. Sees clean 3D scene. Used by chillwave, sunset,
   lithograph, blueprint_red, noir, ice.
2. **DirAsciiQuad** · `ascii_directional.gdshader` — per-cell
   directional ASCII. Sees the neon output. Used by blueprint
   mood (cyan, blueprint-paper background).
3. **AsciiQuad** · `ascii_render.gdshader` — full ASCII renderer
   (every cell is a glyph chosen by luminance). Used by 3:47 am
   / precipice / substrate.
4. **Quad** · `demoscene_post.gdshader` — palette quantize +
   Bayer dither + scanlines + chromatic aberration. Always last;
   stylizes everything above.

If you reorder these, the moods break. The Sobel needs the clean
scene; the ASCII needs to see the colored output before quantize;
the dither belongs at the end.

### Use the right tool for the problem

| Problem                              | Right tool                          | Wrong tool                          |
|--------------------------------------|--------------------------------------|--------------------------------------|
| Readable text in 3D (signage)        | `Label3D` (Godot's font renderer)    | Procedural tube/box letter geometry |
| Stylized text (logo mark, swoosh)    | `cursive_type.py` Bezier sampling    | Label3D (looks too "clean")         |
| Continuous edge outline              | Sobel in fragment shader (`neon_edge`) | Per-cell drawing in `ascii_directional` |
| Cell-by-cell ASCII glyph             | `ascii_render` / `ascii_directional` | None — needs per-cell logic         |
| Bloom on bright pixels               | Wider Sobel sample, multiply by edge_glow | Adding a separate "bloom pass"      |
| Warm scene tint through dark fill    | `scene_blend` uniform with smoothstep threshold | Lower fill colour values            |
| Tracking geometry edges through canvas_item | Luma Sobel on SCREEN_TEXTURE   | `hint_depth_texture` in canvas_item (flaky in Godot 4) |
| Mood-specific shader parameters      | `MoodCycler.gd` preset dict          | Per-scene hardcoded uniforms        |

### Mood preset structure

`MoodCycler.gd` holds an array of presets. Each preset is a dict
with keys for every shader uniform across all post-process layers:

```
{
    "name": "lithograph",
    "palette": 3.0, "dither": 0.18, "scanline": 0.60, "aberration": 0.0010,
    "ascii": 0.0, "ascii_cell": 10.0, "ascii_gamma": 0.85, ...
    "neon": 1.0, "neon_thresh": 0.03, "neon_edge": Color(0.95, 0.16, 0.14, 1),
    "neon_low": Color.BLACK, "neon_high": Color.BLACK, "neon_grad": 0.0,
    "neon_blend": 0.25, "neon_glow": 0.55,
    "dir_ascii": 0.0, "dir_cell": 12.0, ...
}
```

When adding a new mood:
1. Decide its INTENDED EFFECT first (one sentence).
2. Pick the PRIMARY shader layer that drives the effect (neon /
   ascii / directional / demoscene).
3. Set its strength to 1.0 and ALL OTHER shader strengths to 0.0.
4. Tune the primary shader's parameters.
5. Optionally enable secondary layers at low strength for
   crossfade / texture.

Don't make new moods that are just "preset N with dial-tweaks of
preset M" — that path has produced 12 moods that all look the same
and forced rework. Each mood needs a clear identity.

### scene_blend warmth threshold (the lithograph fix)

For "pure dark background with only the brightest pixels showing
warm color" looks (lithograph, blueprint_red, noir), the
`scene_blend` uniform on neon_edge MUST use a `smoothstep` threshold
on scene brightness, not a linear bleed:

```glsl
float scene_warmth = max(scene_now.r, max(scene_now.g, scene_now.b));
float warmth_mask = smoothstep(0.78, 0.96, scene_warmth);
fill = mix(fill, scene_now * 1.8, scene_blend * warmth_mask);
```

Without the threshold, every sun-lit pixel tints the fill warm and
the picture loses its high-contrast feel. With the threshold, only
truly bright pixels (lit windows, lamp glow, neon itself) bleed
through, and the rest of the screen stays in the dark fill.

### Procedural ASCII glyph caveats

ascii_directional draws per-cell strokes from a quantized edge
angle. The visible result is constrained by:

- **Strokes don't connect across cell boundaries automatically.**
  Each cell paints only within itself. If two adjacent cells both
  detect a horizontal edge, their stripes line up at the cell
  boundary — but if one cell's detection drops below threshold,
  the line breaks. Use a low edge threshold to keep continuity.
- **Cell size trades resolution for legibility.** Smaller cells
  (6-8 px) follow curves better but look noisy; larger cells
  (12-16 px) look architectural but lose detail on curves.
- **The shader can't draw a line that runs OUTSIDE its cell.** If
  you need a continuous architectural line, use `neon_edge`
  instead (the Sobel produces a continuous outline mask).

### Label3D for legible signage

Procedural geometry letters (cursive Bezier, block strokes) smear
through the screen post-process at typical viewing distance. Use
`Label3D` for any sign where the text actually needs to be read.

Pattern (see LocaleSetup.gd):
1. In the GLB, build sign panels as dark backing boxes with
   recognizable names (`Sign_Panel_N`, `BoatSign_Panel`, etc.).
2. In a scene-load script, walk MeshInstance3Ds, find panel
   meshes by name.
3. Find the panel's WORLD centre via `panel.get_aabb().get_center()`
   (NOT a local offset — GLB-baked vertices are in world coords).
4. Add a Label3D child with text + font size + pixel_size +
   modulate + outline_modulate + `shaded = false` + `double_sided
   = true` + `alpha_cut = Label3D.ALPHA_CUT_OPAQUE_PREPASS`.
5. Position via `label.global_position = panel_world_centre +
   face_normal_offset`.

Reserve `cursive_type.py` for STYLIZED text where exact legibility
isn't the goal (a fragmented mark, a glow pattern, decorative
swoosh underline).

### Edge-detection thresholds for matching a reference

When tuning a mood toward a concept-art reference:

- **Start with `edge_threshold` low (0.04-0.06)** so the Sobel
  catches all visible silhouettes.
- **Raise it ONLY if the reference has cleaner / simpler lines**
  than what you're producing.
- **For "noise" complaints (too many lines)**, raise threshold.
  For "missing edges" complaints, lower threshold.
- **`edge_thickness`** = Sobel sample distance in pixels. Larger
  = thicker outlines, less detail. Smaller = finer lines.
- **`edge_glow`** = how far the bloom halo extends past the line
  itself. Low (0.2-0.4) = crisp lines, no atmosphere. High
  (0.6-0.9) = soft glow around every edge, more "neon" feel.

### Particles (not yet implemented — checklist)

When we eventually add particles to the riverfront / other locales,
likely use cases:

- **Smoke** rising from refinery stacks (currently fake sphere
  clusters). Migrate to GPUParticles3D when ready, with
  emission_box covering the stack top and a slight wind drift.
- **River mist** drifting over the water surface at dawn / dusk
  moods. Low GPUParticles3D layer over the water plane.
- **Bayou fireflies** at night / 3:47 am moods. Point-light
  particles with random walk in the bayou volume.
- **Dust kicked up by cars** entering the parking lot. Short-lived
  small particle bursts.
- **Heat shimmer** over the asphalt at lunch mood. Subtle screen
  distortion as a post-process, NOT a per-mesh particle.

Defer particles until each locale's static geometry is shipped.
They're polish; static reads first.

## Active shader inventory

| Shader file                              | Purpose                              | Used by               |
|------------------------------------------|--------------------------------------|------------------------|
| `ascii_render.gdshader`                  | Per-cell luma-mapped ASCII glyph     | 3:47 am / precipice / substrate |
| `ascii_directional.gdshader`             | Per-cell directional ASCII           | blueprint              |
| `neon_edge.gdshader`                     | Sobel silhouette outline + gradient fill | chillwave / sunset / lithograph / blueprint_red / noir / ice |
| `demoscene_post.gdshader`                | Palette quantize / dither / scanlines / chromatic aberration | every mood             |
| `ascii_edges.gdshader` (legacy)          | Edge detection + ASCII overlay       | not wired (kept for ref) |
| `glyph_field.gdshader` (legacy)          | Drifting ASCII glyph field           | not wired (kept for ref) |
| `gouraud_lambert.gdshader`               | Cathedral baked vertex-color shader  | warehouse scene only   |
| `ps2_lit.gdshader` (legacy)              | PS2 vertex jitter + Gouraud          | not wired (kept for ref) |

## Active mood inventory

Each mood drives the shader stack via `MoodCycler.gd`. F3 cycles
through them in order.

| Mood          | Intended effect                              | Primary lever |
|---------------|-----------------------------------------------|---------------|
| lunch         | Bright noon, slight grain                     | demoscene mild |
| dusk          | Golden hour warmth                            | demoscene warm |
| chillwave     | Outrun synthwave — hot pink / magenta / purple | neon_edge full |
| sunset        | Western fire-sky — gold edges / orange-purple | neon_edge warm |
| lithograph    | Concept-art match — black + booth red + warm spots | neon_edge tight |
| blueprint     | Architectural drafting cyan-on-blueprint-blue | ascii_directional |
| blueprint_red | Architectural red lines on pure black         | neon_edge crisp |
| noir          | 1940s detective B&W                           | neon_edge white |
| ice           | Cold winter night — cyan / navy               | neon_edge cool |
| night         | Moonlit naturalistic                          | demoscene deep |
| 3_47_am       | Sleep-deprived jitter, ASCII bleeding in      | ascii_render mid |
| precipice     | About to break — red shift, glitch            | ascii_render heavy |
| substrate     | Full code rendering — phosphor green-on-black | ascii_render max |
| raw           | Unfiltered debug                              | none          |

## Recent lessons

### 2026-06-14 · spinning up this playbook

Split off from `_3D_MODELING_PLAYBOOK.md` once the shader/visual
lessons exceeded 8 distinct rules. Per the CLAUDE.md cadence:
"When a new domain accumulates ≥ 5 distinct lessons, spin up a
playbook for it." Captured here:

- screen-space shaders only (user directive)
- post-process stack ordering matters
- Label3D for legible text, procedural geometry for stylized text
- scene_blend warmth threshold for lithograph-style backgrounds
- ascii_directional per-cell strokes don't connect — use neon_edge
  for continuous outlines
- each mood needs an intended effect, not dial-tweaks of another
- the active shader + mood inventories live IN THIS DOC, not in
  scattered code comments
- particles deferred until static geometry is shipped

### 2026-06-14 · mono-with-red lithograph ASCII mode

The "look" the user has been driving toward all session is now
clearly defined: **solid black background · visible edges drawn as
near-approximate ASCII characters in white · density characters in
the brightness ramp creating a halftone-gray look for shadows · red
glyphs ONLY for specifically tagged items (sign text, booth red,
neon hotspots)**. Implemented as a new mode in `ascii_directional`:

```glsl
uniform bool mono_with_red = false;
uniform vec4 mono_white, mono_red;
uniform float red_threshold;

if (mono_with_red) {
    float red_dom = scene.r - max(scene.g, scene.b);
    line = (red_dom > red_threshold) ? mono_red : mono_white;
}
```

Driven by the `blueprint_red` mood preset (`dir_mono_red: true`,
`dir_fill: Color(0,0,0,1)`). Density ramp characters (`· ░ ▒ ▓`)
provide the halftone-gray gradient on non-edge cells, all in
mono_white. Tagged items naturally render red because their scene
color is red-dominant (sign Label3D modulate red, booth materials
COL_RED).

Lessons learned:

- **For two-colour stylization, snap the color choice per cell**
  rather than `tint_from_scene` (which produces a noisy multi-hue
  result). `r - max(g,b) > threshold` is a robust "is this red?"
  test that ignores warm-yellow lights.
- **Set the starting mood to the one you're tuning** while iterating.
  `current_index = 7` in MoodCycler so the user sees blueprint_red
  on scene-load instead of cycling through 7 moods first.
- **Dim the scene's directional and ambient light** before judging
  any ASCII mood. A sunlit Standard material reads as 100% white
  everywhere, killing the edge-detection contrast that drives the
  ASCII glyph choices. Reduced Sun energy 1.6 → 0.45, ambient 1.1
  → 0.35, background near-black for the lithograph look.

### 2026-06-14 · Label3D rotation via explicit basis, not Euler

Three iterations of Euler `Vector3` rotations for `Label3D` placement
on sign panels all produced wrong orientations:

- Pole sign N face (face +Y): `Vector3(-PI/2, 0, 0)` made the label
  face +Y but with up = world -Z (upside down).
- Pole sign S face (face -Y): worked accidentally.
- Boat sign (face -X): `Vector3(0, -PI/2, 0)` made the label face
  -X but with text running VERTICALLY along Z (90° rotated).

Root cause: Euler-angle rotations don't preserve "up" — applying a
single-axis rotation around X or Y rotates the up vector too, and
since Godot's `Node3D.rotation` is YXZ order, multi-axis combinations
introduce hard-to-predict twist.

Rule: **for a panel-mounted label, build the basis explicitly from a
forward direction + world-up**:

```gdscript
var fwd: Vector3 = face_normal.normalized()
var world_up := Vector3(0, 0, 1)
if abs(fwd.dot(world_up)) > 0.95:
    world_up = Vector3(0, 1, 0)
var right: Vector3 = world_up.cross(fwd).normalized()
var up: Vector3 = fwd.cross(right).normalized()
label.global_transform = Transform3D(Basis(right, up, fwd), pos)
```

This guarantees `+Z` faces the camera-facing normal, `+Y` is upright,
and `+X` is horizontal text-reading direction — for any panel
orientation. No Euler-order surprises.

### 2026-06-14 · multi-scale ASCII + linework mood + Y-up bug

Three rolled-up lessons from late-evening iteration on the look:

- **The "multi-pass" effect inside one shader.** User asked for
  "multiple rendering passes with different shaders, capturing
  geometry and edges lit by the camera as visible, and also the
  deep black and far off details." Instead of stacking more
  ColorRect layers (which double the bandwidth and complicate the
  stack ordering), the existing `ascii_directional` now does the
  multi-pass effect via three concentric sample rings INSIDE one
  fragment shader:
    Ring 1 (immediate N/S/E/W neighbors) → fine edges (`│ ─ ┌ ┐ └ ┘`)
    Ring 1 diagonals (NE/NW/SE/SW)        → `╱` or `╲`
    Ring 2 (2-cell distant)                → faint dot for distant silhouettes
    Plus the cell's own brightness via a logarithmic density ramp
    (`· ░ ▒ ▓`) starting at 0.02 so even deep shadows register.
  13 texture taps per cell; still cheap.

- **"Edges only" already had a tool — neon_edge.** User asked
  "is there a way to render the scene so only visible edges of
  geometry are pronounced and visible?" The answer was a new
  MOOD using the existing `neon_edge.gdshader`:
  `neon: 1.0, neon_thresh: 0.025, neon_low/high: pure black,
  neon_edge: near-white, neon_grad: 0` → pure ink linework, no
  fill, no halftone. Added as `linework` mood and set as the
  default boot mood so the user sees it on scene load.

- **Y-up vs Z-up bit us THREE times in one session.** The Blender
  build script writes Z-up; Godot runtime is Y-up. Any face-normal
  vector passed from Blender-frame code into Godot runtime code
  (e.g. `_attach_sign_label(panel, face_normal=...)`) MUST be
  remapped: `(x_b, y_b, z_b) → (x_b, z_b, -y_b)`. The Label3D
  basis-from-forward-and-up helper also needs `world_up = (0,1,0)`
  not `(0,0,1)`. Symptom of the bug: text rotated 90° around the
  panel's face axis, reading vertically instead of horizontally.
  Locked down in `_3D_MODELING_PLAYBOOK.md` "Coordinate frame"
  section as a top-of-playbook MUST-READ.

### 2026-06-14 · the lithograph recipe (saturation-gated bleed)

After ~10 iterations tuning the riverfront vs the vol5 Dante
D'Ambrosio's concept-art reference, the working recipe for a
"lithograph illustration on screen" look is locked:

```
neon_edge as the visible foundation:
  strength = 1.0
  edge_threshold ≈ 0.010   (low — catches every plank/spindle/seam)
  edge_glow ≈ 0.10         (tight bloom, crisp lines)
  fill_low = fill_high = pure black
  fill_gradient = 0

scene_blend > 0 ENABLED but THREE GATES filter what bleeds:
  bleed_lo / bleed_hi    ≈ (0.82, 0.96)   brightness gate
  sat_bleed = true
  sat_lo / sat_hi        ≈ (0.50, 0.68)   saturation gate
  scene_blend            ≈ 0.55           overall bleed strength
```

Why saturation matters: brightness alone can't tell
"lit cream wall at 0.95 max channel" from "saturated sign red at
0.98." Both clear the brightness gate; only the second has the
high-saturation that the sat gate enforces. Saturation
= (max - min) / max. Cream walls sit around 0.20 because their R,G,B
stay roughly equal even when lit; sign red is 0.82; lit windows
0.59; warm bulbs 0.64.

For "lithograph + ASCII halftone" (blueprint_red), add the ASCII
layer LIGHTLY on top:
  dir_ascii ≈ 0.40   (subtle halftone where surfaces are bright)
  dir_mono_red = true (white glyphs everywhere except saturated red)
  dir_red_thresh ≈ 0.32 (warm bulbs render WHITE; only sign reaches red)

Kill CRT artifacts in lithograph moods:
  aberration = 0.0         (no R/B fringing — clean print look)
  dither ≈ 0.01            (minimal — ink doesn't dither)
  palette ≈ 16             (wide enough to avoid colour banding on
                            bleed-through reds — the reference is
                            a CLEAN print, not a tight palette)

### 2026-06-14 · Lobster for D'Ambrosio's signage

The default Godot sans-serif was the wrong material for the
boat-life signage all along. Lobster (Pablo Impallari, OFL-licensed,
Italian-designed thick brush script) is the canonical cursive for
the D'Ambrosio's sign — both the parking-lot pole and the boat-top
marquee.

Lives at `godot/resources/fonts/Lobster-Regular.ttf`. Loaded by
LocaleSetup as `const CURSIVE_FONT = preload(...)` and assigned to
every D'Ambrosio's panel Label3D.

When sourcing a font from Google Fonts for a similar use:

- The OFL fonts mirror at `github.com/google/fonts/raw/main/ofl/<name>/<name>-Regular.ttf`
  is fetchable directly via curl.
- Pull the `OFL.txt` next to it so attribution stays clean.
- Lobster's strokes run ~25% wider per char than Godot's default
  sans — drop `pixel_size` (and bump `font_size`/`outline_size`) so
  the cursive still fits the panel boundaries. For a panel ≈ 6.4m
  wide × 2m tall, `font_size = 128`, `pixel_size = 0.008`,
  `outline_size = 10` puts "D'Ambrosio's" tight inside the panel.

Other appropriate alternatives if Lobster doesn't fit a future
sign: Pinyon Script (1880s copperplate elegant — fits steamboat
era), Parisienne (French brush, lighter), Allura (elegant
copperplate), Sacramento (modern handwritten).

### TEMPLATE for next session

```markdown
### YYYY-MM-DD · <session focus>

- **<headline lesson>.** <one-sentence summary of what went wrong /
  what we learned, plus the rule that came out of it>.
- ...
```
