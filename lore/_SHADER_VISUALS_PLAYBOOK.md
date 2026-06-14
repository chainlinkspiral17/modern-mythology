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

### TEMPLATE for next session

```markdown
### YYYY-MM-DD · <session focus>

- **<headline lesson>.** <one-sentence summary of what went wrong /
  what we learned, plus the rule that came out of it>.
- ...
```
