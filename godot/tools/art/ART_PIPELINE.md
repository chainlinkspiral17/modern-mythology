# The slowstick 2D art pipeline (2026-08-30 · THE CORRECTION)

**Target look:** rich, full-resolution modern painted illustration —
the art a sophisticated studio ships. Slowsticks are **alternate
reality games**: sophisticated modern games made in an alternate
timeline (user correction, 2026-08-30, verbatim in the aesthetic
bible's THE CORRECTION section). This replaces the flat-vector
HeroImage look for scene/hero art.

**The wrong turn, recorded:** the 2026-07 version of this file made
the "alt-reality prism" literal as an ERA FILTER — `svga_quantize.py`
crunching painted sources to 320×200/256-color dithered "SVGA." That
imported OUR timeline's early-90s PC hardware limits as a goal, which
is exactly the retro cosplay the aesthetic bible bans. The filter step
is retired for shipped assets; `svga_quantize.py` stays on disk
unused. The per-studio material look (gouache, halftone, ink bleed…)
comes from `SlowstickLook`'s demoscene_post presets at runtime — the
source art ships clean.

## The two source paths

1. **`scene_render.py`** — fetch an AI-painted source from an image
   model (needs a key; see below). This is the real path to
   hand-painted fidelity. Target register: contemporary key-art /
   painted-illustration discipline. NOT "AI does Sierra."
2. **`scene_painter.py`** — the procedural painter (gradient skies,
   atmospheric layered silhouettes, painterly pass: canvas grain,
   edge-hold ink, RGB wobble; grad_poly light, drop shadows).
   Best-effort PLACEHOLDERS until AI sources land.

Both paint at the project's native **1280×720** and ship as-is.

## Tools

- `scene_painter.py SCENE_ID out.png` · `--list` scenes. Writes the
  full-res painterly PNG straight to the asset path.
- `scene_render.py` — image-gen client (Meshy-pattern: key via env or
  `.image_key`, dry-run, queue JSON → PNG). PENDING an image service +
  key.
- `art_studio.html` — browser front end for generating/placing sources
  per studio asset slot. Its era-filter dials predate THE CORRECTION:
  use it for compose/place only; do NOT apply the quantize step to
  anything that ships.
- `svga_quantize.py` — retired for shipped assets. Kept for history.

## Generating sources · ArtCraft (storytold/artcraft)

ArtCraft remains the recommended interactive SOURCE generator (Flux /
GPT-Image / Nano Banana / Midjourney front end with compositing,
inpainting, posing). Artist-driven: generate/compose → export PNG at
1280×720 (or larger; downscale smoothly) → drop at the asset slot
path. For AUTOMATED batch runs, point `scene_render.py` at one model's
direct API with a key at `.image_key`.

## Output contract

Final PNGs land at the per-studio asset paths
(`godot/assets/art/<studio>/<scene>.png`) and are loaded PNG-first by
the host/scene as a TextureRect with **default (linear) filtering** —
never TEXTURE_FILTER_NEAREST, which is a pixel-art tell. The
HeroImage/ColorRect fallbacks stay until a PNG exists (sprite
playbook: never remove the fallback).

## Rollout

1. Salmonberry full set + estuary_4 / northwind_harbor / fey_faire
   title scenes shipped at 1280×720 procedural (draft 3).
2. AI-painted replacements, studio by studio, once the image-gen path
   has its interactive approval / key (user's keyboard required).
