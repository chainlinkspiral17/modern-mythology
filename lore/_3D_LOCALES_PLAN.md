# 3D Locales · Build Plan

Branch: `claude/3d-locales` · forked from `claude/great-davinci-TyrUq`

The transition from 2D painted backgrounds to **3D models + game
scenes that can be dynamically lit and framed**. Volume by volume,
chapter by chapter. Portraits stay 2D PNGs for now; locales go 3D.

## why

- **Image-data savings.** A locale rendered as a 2D painted PNG
  across multiple times-of-day = N × few-MB. Same locale as one
  GLB + a handful of light setups = ~50-200 KB total. Order of
  magnitude smaller on disk.
- **Dynamic lighting.** The same diner at 3:47 AM looks different
  from the same diner at the lunch rush. With 2D, that's two
  different paintings. With 3D + Godot's runtime lighting, it's
  one geometry and two light setups.
- **Cinematic framing.** A camera can move through the room for a
  long take, frame a close-up, pull back for a reveal. Static 2D
  backgrounds can't do this.
- **The aesthetic still holds.** Low-poly + restrained lighting +
  warm/cool contrast + period-correct geometry = the same painted
  register, just renderable.

## what changes from the Cathedral approach

The Cathedral interior (vol 6 COMMUNITY PLANNED game) uses
**vertex-color Gouraud bake** — the lighting is baked into the mesh
at build time, the shader is unshaded. Static, no runtime lights
needed, ultra-cheap.

The vol 5 locales need to **support multiple lighting setups per
scene** — same geometry, different moods, different times of day,
different dramatic moments. So:

- The Blender scripts output meshes with **diffuse vertex colors
  only** (no baked lighting term). Per-face color identifies the
  material.
- Godot uses **StandardMaterial3D** (not the Gouraud shader) on
  these meshes — vertex colors as albedo, runtime lights shade
  them normally.
- Each locale ships with a **`.tscn` file** that includes:
  - The mesh instance from the GLB
  - 2-5 named light setups (lunch / dusk / 3:47 AM / etc.)
  - Optional Camera3D markers for cinematic framing
  - A small script that switches between light setups

This is a different shader path from the Cathedral. Both ship in
the project; both look right in their respective contexts.

## the build order

Vol 5 · Major Arcana — eight chapters, each one a locale (or
multi-locale for the Hierophant):

| # | chapter | locale | status |
|---|---|---|---|
| 0 | The Fool | D'Ambrosio's diner | **STARTING HERE** |
| I | The Magician | the Cathedral of Rust and Code | already exists (vol 6 game) |
| II | The High Priestess | Elicia's bungalow | next |
| III | The Empress | the riverboat interior (Nicola's floor) | |
| IV | The Emperor | the riverboat helm (above the dining room) | |
| V | The Hierophant | the circuit (multi-locale: church + black car + table 17 + bandstand + armory + riverfront) | |
| VI | The Lovers | the Roberts house | |
| VII | The Chariot | Ember & Ash warehouse | |

(VIII-XXI follow when their chapters land.)

Then the vol 6 locales beyond the Cathedral (Cosmic Comics, Kwik
Stop, NexCorp Gas & Go, Lot 47 model home, Wagner's Hardware,
Salty Tome, Pizza Pirate, Alsea Bay Cannery), then vol 7's
Smolvud roster.

## the file layout

```
godot/
├── tools/blender/
│   ├── build_cathedral_interior.py    # vol 6 game (unchanged)
│   ├── build_workbench_props.py        # vol 6 game (unchanged)
│   ├── ...
│   └── locales/                        # NEW · vol 5 chapter locales
│       ├── build_diner.py              # D'Ambrosio's
│       ├── build_bungalow.py           # Elicia's
│       ├── build_riverboat.py          # Empress + Emperor share geometry
│       ├── build_church.py             # St Jude's (Hierophant sub-locale)
│       ├── build_blackcar.py           # the long black car interior
│       ├── build_armory.py             # the old armory back room
│       ├── build_roberts_house.py      # the Lovers
│       ├── build_ember_ash.py          # the Chariot
│       └── build_all_locales.sh        # master runner
├── assets/3d/
│   └── locales/                        # NEW · per-chapter GLBs
│       ├── diner.glb
│       ├── bungalow.glb
│       ├── riverboat.glb
│       ├── church.glb
│       ├── blackcar.glb
│       ├── armory.glb
│       ├── roberts_house.glb
│       └── ember_ash.glb
└── scenes/
    └── locales/                        # NEW · per-chapter game scenes
        ├── diner.tscn
        ├── diner_LightController.gd    # mood switcher per locale
        ├── bungalow.tscn
        ├── riverboat.tscn
        ├── ...
        └── _LOCALES_README.md
```

## the lighting setup pattern

Each locale's `.tscn` file ships with multiple **named light setups**
the game switches between. Standard set across all locales:

| setup name | mood | when used |
|---|---|---|
| `dawn` | cool blue + low warm fill | very early morning scenes |
| `lunch` | warm + bright + clean | midday |
| `dusk` | warm orange directional + long shadows | evening |
| `night` | dark + interior point lights only | after hours |
| `precipice` | reserved · cold blue + a single hot spot | the chapter's climactic mode |
| `flashback` | desaturated · low contrast · soft | memory scenes |

Per-locale customization: each locale can add additional moods.
The diner has a `3:47_am` setup (the canonical Fool hour); the
bungalow has a `recording` setup (Elicia at the deck); the
Cathedral floor has a `tower_dim` setup (substrate weather).

The `LightController.gd` script attached to each scene's root
exposes a `set_mood(mood_name: String)` method that swaps which
Light3D nodes are visible/active. Simple, fast.

## the camera markers

Each locale ships with named Camera3D markers for cinematic
framing. Standard markers per locale:

- `player_entry` — where the player spawns when entering the scene
- `wide` — establishing shot
- `close_<name>` — close-up on a specific object/character anchor
  (e.g., `close_counter`, `close_booth_6`, `close_payphone`)

The novel-side prose can address camera markers by name when a
scene calls for cinematic framing.

## what stays 2D

- **Character portraits** — the painted Gauntlet-Studio register
  keeps working as 2D PNGs. Apply as image textures to flat-
  billboard quads in 3D scenes if needed (e.g., a wall photo, a
  framed picture).
- **Card art** (the 22 tarot cards) — stays 2D for now. May
  convert later but no benefit yet.
- **Painted CGs** for dramatic single-frame moments — stay 2D.

## the runtime aesthetic · substrate / demoscene reclaimed

The locales render through a **substrate / demoscene post-process
pipeline** — the geometry is low-poly, but the screen output is
transformed into the ASCII-art / dither / scanline register vol 5
has always reached for. The substrate art the user liked but
couldn't implement in 2D becomes achievable in 3D via shaders and
particles.

The aesthetic stack:

### object shaders (per-mesh)

- **Restricted-palette shading.** Each locale ships with a
  ~16-color palette (extending the project's warm-bg / paper /
  rust / phosphor-green / river-blue triad). Lit output is
  quantized to the nearest palette color. Banded shading,
  posterized highlights, no smooth gradients.
- **Ordered dithering.** A Bayer 4×4 matrix on color transitions
  — the dithering '90s CRT-era 256-color modes used. Gives the
  painted register a faint computational texture.
- **Optional outline pass.** Thin dark outline on screen-space
  edges (depth + normal discontinuities). Reads like ink on cel.

### post-process (screen-space)

A full-screen `demoscene_post.gdshader` on a CanvasLayer over
the 3D viewport. Layered:

- **Scanlines.** Horizontal dark lines, every 2-3 pixels, low
  amplitude. CRT signature.
- **Chromatic aberration.** Sub-pixel RGB shift, very subtle.
- **ASCII overlay** (per-mood). In certain moods (`precipice`,
  `3:47_am`, `substrate_dim`) the rendered scene gets a
  screen-space ASCII conversion — luminance mapped to characters
  from a 16-step ramp `@%#*+=-:.` — rendered as a transparent
  layer over the geometry. Default moods (lunch, day) skip this.
- **Phosphor decay.** Faint trail when the camera moves —
  previous frames bleed slightly into the current. CRT motion.

### particle effects

Per-locale atmospheric particles, free motion without geometry
cost:

- **Dust motes** drifting through warm light shafts (diner near
  windows, bungalow at dusk, Cathedral always).
- **ASCII glyphs** as drifting characters (`╱ ╲ ░ ▒ ▓ ·`) — BBS-
  adjacent moments, cathedral hum manifestations, substrate-
  flicker beats. Single-frame ASCII characters as billboard
  particles, fade in/out.
- **Phosphor sparks** off the BBS terminal and the workbench's
  active lamp.
- **Cicada vibration** — very-low-amplitude camera shake on warm
  evening scenes.

### the substrate art reclaimed

The vol 5 substrate art (the user's previously-developed
ASCII/demoscene paintings) gets reclaimed by this approach. The
geometry is the new canvas; the post-process is the new
brushwork. The substrate aesthetic was always trying to *describe
the underlying signal* — the BBS-era rendering of a world that
hums under the surface. In 3D + post-process, that's not a
metaphor; it's literally what's happening on the GPU.

## the arcana gauntlet upgrade path

If the 3D locales + demoscene aesthetic work well, the **Tarot
Gauntlet** (vol 5's gallery game) can be evolved to use them too.
Each gauntlet scenario is set in one of these locales already by
canon — the Fool scenario is at D'Ambrosio's, the Magician at the
Cathedral, the Empress on the boat, etc. Converting the gauntlet
from its current 2D-painted-substrate-board to a first-person
3D walk through the same locale, with the same dispatch /
visitor / connection mechanics layered as interactable nodes in
the 3D space, is a natural extension.

The order of operations there: prove the locales work for the
novel-side first; then extend each gauntlet scenario to use its
locale's 3D scene; then keep the 2D painted board as a togglable
fallback (or deprecate it entirely depending on how the new
register lands).

Either way, the locales are the shared asset layer across:
1. The vol 5 novel chapters (scene-setting for prose)
2. The Pomegranate Hour episodes (in-universe video filmed in
   these rooms)
3. The Tarot Gauntlet game (each scenario's playable space)
4. Vol 6 / vol 7 chapters where these rooms re-appear (the
   Cathedral in vol 6 COMMUNITY PLANNED is already this in
   action)

One locale, many uses.

## the player-camera approach

Two modes per locale:

- **First-person walk** — the player enters the locale, can walk
  around, can interact with named objects (the workbench, the
  booth, the payphone). Same FPC controller as the vol 6 Cathedral.

- **Fixed cinematic shots** — the novel-side prose triggers a
  framing change. The camera teleports to a named marker, the
  player loses control for the scene's duration, dialogue or
  description plays, the camera returns or switches to another
  marker.

The same locale supports both modes. The default is first-person
walk; cinematic shots are scene-script-triggered.

## status

- vol 6 Cathedral scene: SHIPPED (other branch, will merge back)
- vol 5 Fool (D'Ambrosio's diner): **building now**
- everything else: queued

When each locale lands, the corresponding vol 5 chapter's
existing 2D background asset can be deprecated. The
`_VOL5_WIKI.md` will gain a "3D locale shipped" annotation per
chapter as they convert.
