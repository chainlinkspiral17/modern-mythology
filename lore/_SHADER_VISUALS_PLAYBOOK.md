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

### 2026-06-14 · cell shaders MUST be a true identity at strength = 0

- **The big invisible bug.** Every mood except a handful (substrate,
  psychedelic_substrate, lightshow_extreme) looked uniformly chunky —
  ~10 px cells stamped over the whole frame, including pure sky and
  even the `raw` mood. Spent a long detour chasing window stretch and
  filter_nearest before realising the cells were perfectly uniform
  and not following geometry → it had to be a cell-based shader,
  not edge detection.
- **The culprit.** `ascii_render.gdshader` was sampling SCREEN_TEXTURE
  at the *cell centre* and binding that single sample to both the
  glyph-density input AND the scene that `mix(scene, ascii, strength)`
  blends against. At `strength = 0` the shader is supposed to be a
  no-op, but it was instead emitting the cell-centre colour for every
  fragment inside the cell — a uniform 10 px quantization grid baked
  into the entire chain.
- **The fix.** Split the two samples cleanly. Per-fragment `SCREEN_UV`
  sample for the passthrough scene (true identity at strength 0).
  Cell-centre sample stays for glyph density and tint-from-scene
  foreground only. Every cell-based shader in the chain now has to
  be audited the same way: `motion_ascii`, `starscape`, and
  `ascii_directional` were already per-fragment for passthrough;
  `ascii_render` was the lone offender.
- **Rule.** When a post-process shader sits permanently in the chain
  and is gated by a `strength` uniform, the `strength = 0` path MUST
  read SCREEN_TEXTURE at SCREEN_UV per fragment — never at a
  quantized cell centre. Cell-aligned samples are fine for the
  STYLIZED branch (`ascii`, `line`, etc.) but the passthrough has to
  pass through pixel-perfect or it pollutes every mood that "isn't
  using" the shader.

### 2026-06-14 · neon_edge blend modes for "see the world underneath"

- **Why.** The lithograph family (`linework`, `blueprint_red`,
  `noir`, etc.) replaces the scene entirely with bleach-white edges
  on pure black — beautiful for the press-art look but it crushes
  the world detail the user wants to read.
- **What we added.** `blend_mode` uniform on `neon_edge.gdshader`:
  `0 = REPLACE` (classic, current behaviour), `1 = MULTIPLY`
  (stylization darkens scene, world detail visible through tint),
  `2 = OVERLAY` (Photoshop overlay; high contrast + tint),
  `3 = SCREEN` (additive-light blend), `4 = ADD` (preserves scene,
  adds stylization brightness on top).
- **Sibling mood pattern.** Rather than parameterise every mood
  with a blend-mode key, ship `linework_overlay` and
  `linework_multiply` as their own presets at the front of the
  strata. F3 / RMB-look cycles surface them naturally. Future
  passes (red/blue/green) can spawn the same `_overlay`/`_multiply`
  siblings cheaply by copying the base preset and changing
  `neon_blend_mode`.
- **Rule.** Adding a new blend mode is preset-cheap, not shader-
  cheap. Bake new modes into `neon_edge.gdshader`, expose via a
  single `blend_mode` int uniform, then spawn variant moods. Don't
  rebuild the chain.

### 2026-06-14 · F9/F10/F11/F12 sub-toggles · style packs · sky lerp

- **The "make it more subtle" debate.** User wanted overlay/multiply
  blend modes to let the raw scene show through. Their first
  instinct was a "swap source/target" toggle. Math: multiply,
  screen, and add are commutative — swap doesn't change the
  picture. Only overlay is asymmetric (becomes hard light). The
  user's actual want was "raw dominates, effect subtle on top." The
  right lever is a strength dial, not a math flip. Shipped F10 as a
  `BLEND_AMOUNTS = [1.0, 0.6, 0.3, 0.15]` cycle multiplier on the
  neon_edge layer's `strength` uniform. The picture now reads as
  raw scene plus a hint of ink.
- **Rule.** Before adding a blend-math toggle, identify whether the
  user wants asymmetric behaviour or whether they want LESS of an
  effect. Commutative blends never benefit from source/target swap.
- **Sub-toggles compose.** F9 (blend mode), F10 (blend amount), F11
  (lighting), F12 (style pack) all persist across F3 / RMB strata
  cycling. The HUD label appends each active override
  (`MOOD · linework (F3)  · blend=overlay (F9)  · amt=30% (F10)
  · light=blue_hour (F11)`) so the user can read the full visual
  state at a glance. Style packs (F12) are a curated bundle of
  mood + lighting + blend overrides for snapping to a per-location
  identity in one tap; manual sub-toggles still work on top.
- **Smooth time-of-day transitions.** Snapping between lighting
  presets feels broken; lerping over ~1.2 s with `smoothstep` ease
  reads as natural cross-fade. Pattern:
  1. Store `_light_lerp_source` (snapshot of current preset) and
     `_light_lerp_target` (new preset). On chained cycles,
     `source = previous target` so continuity holds.
  2. Each frame advance `_light_lerp_t = min(1.0, t + dt / DUR)`.
  3. `_apply_lighting_blended(src, dst, smoothstep(t))` lerps
     every animatable field (dir_mult, practical_mult, tint colour,
     tint_mix, sun pitch/yaw, ambient colour/energy, fog colour,
     sky_top, sky_horizon, sky_energy).
  Rule: any "transition between two named visual states" wants this
  same shape — NEVER snap on a frame, ALWAYS interpolate over time.

### 2026-06-14 · ProceduralSkyMaterial works in gl_compatibility

- **What we did.** Replaced the WorldEnvironment's flat
  `background_color` with `background_mode = 2` (Sky) and a
  `ProceduralSkyMaterial` sub-resource carrying `sky_top_color`,
  `sky_horizon_color`, `sky_energy_multiplier`, `ground_*`. Per
  lighting preset we lerp those colours/energies live, so day
  cycles from indigo-top + faint-horizon midnight → cyan-top +
  white-horizon midday with the sun directional pitching from -28°
  (under horizon) up to -82° (overhead).
- **Renderer constraint.** `ProceduralSkyMaterial` works under
  `renderer/rendering_method="gl_compatibility"`. `PhysicalSkyMaterial`
  does NOT. Stick with procedural unless we flip to Forward+.
- **glow_enabled is a no-op in gl_compatibility.** The Environment
  exposes the property but the Compatibility renderer ignores it.
  Setting it costs nothing — it'll just kick in if we ever switch.
  Don't promise bloom-driven visible-lamp glow without the
  renderer swap (Forward+ on Steam Deck handles this fine).
- **Rule.** Whenever adding sky / glow / SSAO / SSR, FIRST check
  whether the project's renderer supports the feature. List of
  Compatibility-mode unsupported features: SSAO, SSR, SDFGI,
  PhysicalSky, glow/bloom, screen-space refraction. Volumetric
  fog is restricted too. Procedural sky, basic fog, omni/spot
  lights, directional with shadow, MSAA — all fine.

### 2026-06-14 · time-of-day requires light category split

- **What broke.** First-pass time-of-day toggle just multiplied
  every cached `Light3D.light_energy` by an `energy_mult`. On the
  riverfront night scene that gave "less dark midday" instead of
  daylight — directional keys at 0.32 × 1.8 = 0.58 is still night.
  Worse, the sodium street lamps at 1.6 × 1.8 = 2.88 stayed
  blazing-on at midday.
- **The fix.** At light-collect time, sort nodes into TWO arrays:
  `_directional_lights` (sun/moon/key/fill/back) and
  `_practical_lights` (omni/spot — fixtures, lamps, bulbs). Each
  lighting preset then carries TWO scalars: `dir_mult` (8-18 for
  daytime, 0.3-0.6 for night) and `practical_mult` (0 for midday,
  1.4 for night when lamps are pumped up). Picture instantly
  flipped from "barely-less-dark" to "actually daylight" /
  "actually night."
- **Sun rotation.** Per preset, `sun_pitch_deg` and `sun_yaw_deg`
  override the KEY directional's rotation. Match the key by
  `_Key`-suffix naming (`Moon_Key` in vol5); fall back to the
  first DirectionalLight3D. Fill/back keep their cached rotations
  so the three-light cinematography geometry isn't disturbed.
  Pitch ranges: -82° (high noon), -55° (storm overhead), -12°
  (golden hour low west), -3° (blue hour just below horizon),
  -28° (deep night). Shadows actually arc with the sun.
- **Ambient becomes absolute, not multiplied.** A night-scaled
  base ambient of 0.50 capped daytime even with an `ambient_mult`
  of 1.6. New preset structure: `ambient_color` (Color) and
  `ambient_energy` (float, absolute; -1.0 = "keep cached base").
  Daytime ambient hits 2.4 sky-blue without fighting the night
  baseline.
- **Lights-owned-by-other-system rule.** `lightshow_extreme` mood
  already drives every Light3D from audio. The time-of-day apply
  function early-returns when the active mood is
  `lightshow_extreme`. When the user cycles OUT of that mood, the
  `_last_lightshow_active` latch fires `_apply_lighting()` again
  with the current F11 selection so the visualizer doesn't strand
  the lights.

### 2026-06-17 · Riverfront shader stack as the canonical baseline

- **Every new locale gets the full 8-shader riverfront stack as
  starting baseline, not a subset.** The diner and cathedral
  initially shipped with only `Mat_Ascii` + `Mat_Post` (2 quads).
  When the user ran them, the mood cycler had only 2 shaders to
  modulate so most moods were no-ops — the cathedral looked dead,
  diner looked flat. Porting the full riverfront set (Neon /
  DirAscii / Ascii / Starscape / Motion / Blur / Post / OldFilm +
  BackBufferCopies between each + 21-entry `mood_strata` array)
  restored every mood's visual range. **Rule:** when a new
  `*.tscn` adds a PostProcess CanvasLayer, copy the riverfront
  stack verbatim. Per-scene customisation lives in the DebugMenu,
  not in different stacks per scene.

- **Advanced mood/shader/lighting controls go in the DebugMenu
  going forward.** Per user direction: "the advanced mood/shaders/
  lighting need to be in the debug menu going forward. I'll relay
  instructions for scenes when we are putting those together in
  the future." So the per-scene PostProcess tree is always the
  same full stack; the scene-specific dialed-in defaults are set
  via DebugMenu state at runtime, not hard-coded in `*.tscn`.

- **Picture windows + shader linework looks great together but
  needs the opening to be EMPTY.** Linework / motion-ascii moods
  only ascii-ify the visible scene; if a blue glass slab covers
  the window opening, the linework just outlines the slab, not
  the bayou beyond. Removing the glass slab and leaving only the
  brass mullions = linework + ASCII traces the cypress trees and
  far refinery silhouette through the window. Big visual win.

- **HUD CanvasLayers must be in the `'ui'` group for F4 hiding.**
  The diner and cathedral HUD layers were missing the
  `groups=["ui"]` annotation; F4 still walked the tree and hit
  them, but adding the group makes the intent explicit and
  matches the riverfront pattern. **Rule:** every HUD CanvasLayer
  in a `*.tscn` carries `groups=["ui"]`.

### TEMPLATE for next session

```markdown
### YYYY-MM-DD · <session focus>

- **<headline lesson>.** <one-sentence summary of what went wrong /
  what we learned, plus the rule that came out of it>.
- ...
```
