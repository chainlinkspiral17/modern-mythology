# Lighting Playbook · Modern Mythology

How to light a scene like a film/TV/game production team would,
within the Godot 4 + screen-post-process constraints of this
project. Companion to `_3D_MODELING_PLAYBOOK.md` (which covers
geometry) and `_SHADER_VISUALS_PLAYBOOK.md` (which covers post).

## How to use it

Read the Core rules before touching any `riverfront.tscn` (or any
locale scene) lighting block. Add dated entries to "Recent lessons"
after every session that changes lighting.

## Core rules

### One single sun-spot is not a film look

The cardinal sin is a scene lit by ONE directional light + maybe
one fill omni. That reads as "phone-flashlight on stage" because
real productions use **layered light** — key + fill + back + every
practical fixture visible in frame is also a Light3D. Even a 90-second
short film typically uses 6–10 lighting units.

Our economical budget for an exterior locale:
**~12 lights total** — three direction-anchored "key/fill/rim" plus
8–10 small practicals at visible fixtures.

### The three-light foundation

Every scene starts with three `DirectionalLight3D` nodes acting as
**KEY · FILL · BACK**:

| Light | Direction       | Color (typical night)   | Energy |
|-------|-----------------|--------------------------|--------|
| KEY   | upper-side, down 35–55° | Cool moonlight (0.66, 0.74, 0.95) | 0.45–0.6 |
| FILL  | opposite side, low angle | Warm bounce (0.98, 0.82, 0.62) | 0.15–0.25 |
| BACK  | behind subject, down 25° | Cool cyan rim (0.58, 0.78, 0.92) | 0.25–0.35 |

KEY shapes form. FILL recovers the shadow side from going pure
black. BACK pops the subject's edge against the background. Without
any one of them, the scene looks wrong:

- No FILL → high-contrast amateur look (security-camera vibe).
- No BACK → subject merges with background, no depth.
- No KEY → flat ambient, no shape.

For a day scene, KEY becomes the sun (warm, energy 1.0–1.4), FILL
is the sky bounce (cool, energy 0.3), BACK is still the rim. The
ratio matters more than absolute values: keep KEY:FILL:BACK roughly
**4 : 1 : 2** in energy for night, **5 : 2 : 1** for day.

### Practicals — every visible fixture is also a light

If you can SEE a lamp post / window / neon sign / lantern in the
scene, there must be a `Light3D` at that fixture's position
emitting the appropriate color. Each practical sells the believability
of the world ten times more than turning up the ambient.

Naming convention so the .tscn stays grep-able to its source
geometry:
- `Sodium_S` / `Sodium_N` / `Sodium_W` — parking-lot lamp head
- `DockLamp_S` / `DockLamp_N` — tall pier lamps at dock corners
- `DockBollard_0..3` — short bollard lanterns spaced along dock
- `DiningRoomGlow` — boat interior dining room window spill
- `PilothouseGlow` — boat pilothouse interior light
- `SignSpot` — spot pointing at signage

A practical's `omni_range` must be physically plausible — a 6m
sodium lamp lights ~14m around it, not 30m. Use range = 2× the
height of the fixture as a starting heuristic. `light_energy`:
2–5 for street lamps, 1–2.5 for lanterns, 0.8–1.5 for window
spills.

### Color gels for character

Light colour does enormous work. **Choose intentionally**:

| Source                | Kelvin     | Color (Color(r,g,b,1))        |
|-----------------------|------------|--------------------------------|
| High-pressure sodium  | 2100K      | (1.0, 0.62, 0.26)              |
| Tungsten interior     | 2800K      | (0.95, 0.78, 0.50)             |
| Halogen porch         | 3000K      | (0.94, 0.84, 0.66)             |
| Fluorescent shop      | 4000K      | (0.92, 0.92, 0.85) (slight green) |
| Daylight / sun midday | 5500K      | (1.0, 0.96, 0.88)              |
| Overcast sky          | 6500K      | (0.85, 0.92, 1.0)              |
| Moonlight             | 4100K *    | (0.66, 0.74, 0.95)             |
| Neon magenta          | n/a        | (1.0, 0.20, 0.85)              |
| Cyan rim              | n/a        | (0.58, 0.78, 0.92)             |

*Moonlight is technically warm (sun-reflected) but our brains
read dim light as cool — cinematographers cheat blue.

**Color contrast = depth**. Cool key + warm practicals (or vice
versa) gives a scene character. All-warm or all-cool tends to read
as monochrome.

### Diffusers and shadows

For now, all locale lights run `shadow_enabled = false` to keep
performance simple. Shadows can be opted in later for hero scenes
(interiors with strong directional spot, e.g. the boat dining room
interior). Until then, treat lights as if diffused — broader range,
softer falloff (linear attenuation curve in Godot 4's
`LightProjector` / `omni_attenuation`).

For ambient soft fill, two tools:
1. `WorldEnvironment.ambient_light_energy` (cheap global lift).
2. A single big-range, low-energy `OmniLight3D` placed high above
   the scene (a "sky-diffuser") — gives non-directional fill that
   biases toward downward.

If a scene reads too flat, the ambient is too high. If it reads
too contrasty (black abysses), ambient is too low. Aim for the
shadow side of objects being NOT pitch-black but clearly darker
than the lit side.

### Spotlights for signage and entries

The two places you want a `SpotLight3D` specifically (not an omni):
1. **Signage** — point a narrow-cone spot at the sign panel so it
   reads bright against an otherwise dark composition. Don't rely
   on the omni from the nearest streetlamp.
2. **Entry door / gangway** — gives the player a visual "this is
   where you go" cue, classic cinematography.

Cone angle 22–32° works for most. `spot_attenuation` 1.3–1.8 gives
a soft falloff that feels like a real fixture rather than a hard
cookie-cutter. Aim by computing direction = (target - position)
and building the basis from that (-Z faces target).

## Active lighting setup · `riverfront.tscn`

Updated 2026-06-14. Total: **14 lights** (3 directional + 11
practicals/spots).

| Node              | Type             | Role                     |
|-------------------|------------------|--------------------------|
| `Moon_Key`        | DirectionalLight | KEY · cool moon          |
| `Fill_Bounce`     | DirectionalLight | FILL · warm ground bounce |
| `Back_Rim`        | DirectionalLight | BACK · cyan from far shore |
| `Sodium_S/N/W`    | OmniLight × 3    | Parking-lot sodium lamps |
| `DockLamp_S/N`    | OmniLight × 2    | Tall pier-lamps at dock corners |
| `DockBollard_0..3`| OmniLight × 4    | Short bollard lanterns along dock edge |
| `PilothouseGlow`  | OmniLight        | Boat pilothouse window spill |
| `DiningRoomGlow`  | OmniLight        | Boat dining-room window spill |
| `SignSpot`        | SpotLight        | D'Ambrosio's pole-sign illumination |

Position note: lamp omnis are placed AT the lamp-head mesh position
(Blender → Godot remapped). If the build script moves a lamp, the
.tscn Light3D must move with it.

## Recent lessons

### 2026-06-14 · spinning up this playbook

The user's verdict on the prior single-spotlight setup: "this
camera spotlight is not professional. there's usually a whole
bunch of lights." They asked for "diffuse lights, strong lights,
back lights, gels and diffusers" — the language of a real DP, not
a programmer. Three lessons came out of the redesign:

- **Three-point lighting is non-negotiable.** Replaced the single
  Sun with KEY (cool moon) + FILL (warm bounce) + BACK (cyan rim).
  Ratio ≈ 4 : 1 : 2 for night. The picture got 80% of the way to
  "looks pro" from that alone.
- **Practicals tied to visible geometry sell the world.** Every
  visible lamp post / window / lantern in the build script now has
  a corresponding Light3D in the runtime scene at the same world
  coords (Blender → Godot remapped). The .tscn has explicit naming
  (Sodium_S, DockLamp_N, etc.) so you can grep one and find the
  other.
- **Economical, not crazy.** User: "don't go light crazy, economical
  but impactful." 14 lights for the riverfront — three direction-
  anchored + a handful of practicals at visible fixtures — beats
  thirty random omnis sprinkled around. Each light has a job; if
  you can delete one and not notice, it shouldn't have been there.

### 2026-06-14 · runtime time-of-day cycle requires directional/practical split

- **Lesson.** A scene's Light3Ds aren't all the same kind. The
  three-light foundation (key + fill + back) are
  `DirectionalLight3D` representing the sun/moon — they need to
  scale up *massively* for daytime (8-18× their night base).
  Practicals (sodium lamps, dock bollards, interior bulbs) are
  `OmniLight3D` / `SpotLight3D` representing visible fixtures —
  they need to scale to *zero* for noon and bump UP at night.
  Treating all lights with a single `energy_mult` produces
  "barely-less-dark midday" with daytime lamps still blazing.
- **Pattern.** Sort cached lights into two parallel arrays at
  collect time:
  ```
  if node is DirectionalLight3D: _directional_lights.append(node)
  elif node is Light3D:           _practical_lights.append(node)
  ```
  Then per-preset:
  - `dir_mult` ∈ [0.3 .. 18] · directional energy multiplier
  - `practical_mult` ∈ [0 .. 1.4] · practical energy multiplier
- **Sun rotation belongs on the KEY directional only.** Fill and
  back keep their cinematography rotation so the three-light
  geometry isn't disrupted. Match the key by `_Key` name suffix
  (vol5's is `Moon_Key`; HCE will likely use `Sun_Key`). Pitch
  reference points:
    high noon       -82°
    overcast        -55° / -65°
    golden hour     -12° to -8°  (yaw ±75° east/west)
    blue hour       -3°  (just below horizon)
    midnight moon   -28°
- **Ambient: absolute, never multiplied.** Don't scale ambient by
  the same factor you scale directionals — a night base of 0.50
  caps daytime ambient at ~1.0 even with a 2.0× multiplier. Per
  preset: `ambient_color` (Color) and `ambient_energy` (float,
  absolute; sentinel `< 0` means "keep the scene's cached base").
  Sky-blue daytime ambient hits 2.4 unencumbered.
- **Smooth cross-fade.** Lerp source → target preset over ~1.2 s
  with `smoothstep` ease. Lerp every animatable field (dir_mult,
  practical_mult, dir_tint, tint_mix, sun pitch/yaw, ambient
  color/energy, fog color, sky_top, sky_horizon, sky_energy).
  Never snap on a frame — the eye reads snaps as "broken."
- **Defer to mood-owned lights.** If a mood already drives lights
  (`lightshow_extreme` audio-pulses every Light3D), the lighting
  cycle must early-return when that mood is active. When the user
  exits that mood, re-apply the lighting selection so the
  visualizer doesn't strand the lights at their pumped-strobe
  state.

### TEMPLATE for next session

```markdown
### YYYY-MM-DD · <session focus>

- **<headline lesson>.** <one-sentence summary of what went wrong /
  what we learned, plus the rule that came out of it>.
- ...
```
