# The slowstick 2D art pipeline (2026-07 · direction change)

**Target look:** early-1990s 256-color SVGA graphic-adventure art — the
Sierra / LucasArts register (hand-painted-feeling backgrounds, dithered
256-color palettes, atmospheric depth). This REPLACES the flat-vector
HeroImage look for scene/hero art.

**The premise made literal:** slowsticks are "modern games seen through
an alt-reality prism." So the pipeline is: paint a rich modern source,
then press it through an ERA FILTER that quantizes it to a period
256-color dithered SVGA frame. The prism is a real script.

## The two halves (hybrid)

1. **Painted source** — the picture, at high res:
   - `scene_render.py` — fetch an AI-painted source from an image model
     (needs a key; see below). This is the real path to hand-painted
     fidelity.
   - `scene_painter.py` — a procedural painter (gradient skies,
     atmospheric layered silhouettes, soft-blurred edges, value-noise
     texture, glow, fog, vignette). Best-effort PLACEHOLDERS until AI
     sources land. Much richer than flat vector; still procedural, so it
     reads as clean atmospheric illustration, not busy hand-painting.
2. **Era filter** — `svga_quantize.py`: downscale to ~320×200, quantize
   to a 256-color (or tighter) palette with Floyd–Steinberg or ordered
   (Bayer) dithering. Deterministic, no network. This is the prism.

Both AI and procedural sources go through the SAME era-filter, so the
whole catalog shares one period register regardless of source.

## Tools

- `svga_quantize.py IN.png OUT.png [--width 320 --height 200 --colors
  256 --dither fs|ordered|none --palette FILE --preview N]`
  · `--selftest DIR` proves the transform on a synthesized source.
- `scene_painter.py SCENE_ID out.png [--preview N]` · `--list` scenes.
  Paints a source and era-filters it in one step.
- `scene_render.py` — image-gen client (Meshy-pattern: key via env or
  `.image_key`, dry-run, queue JSON → source → era-filter). PENDING an
  image service + key.
- `art_studio.html` — BUILT. Browser tool: drop a painted source (from
  ArtCraft or any model), dial the era-filter live (size / colors /
  dither / saturation, adaptive median-cut palette, FS or Bayer), and
  place it against a per-STUDIO asset slot (shows the repo target path,
  downloads the PNG). Source-agnostic — the companion to whatever
  generator we use. The definitive filter stays `svga_quantize.py`;
  the HTML previews it (JS twin) so you can dial before committing.

## Generating sources · ArtCraft (storytold/artcraft)

ArtCraft is the recommended interactive SOURCE generator — an
open-source desktop app fronting Flux / GPT-Image / Nano Banana
(Gemini) / Midjourney / etc., with compositing, inpainting, background
removal, character posing, and image-to-3D (which also complements the
Meshy hero pipeline). It has no headless/CLI/API, so it is a tool the
ARTIST drives, not one we automate: generate/compose in ArtCraft →
export PNG → `art_studio.html` (era-filter + place) → drop at the slot
path. For AUTOMATED batch runs, point `scene_render.py` at one
underlying model's direct API (Flux/BFL, OpenAI images, or Gemini) with
a key at `.image_key`.

## Getting an AI source (the front half)

`scene_render.py` needs an image model. Drop a key at
`godot/tools/art/.image_key` (git-ignored) or set an env var, and set
the endpoint/model in `scene_render.config.json`. Default target is the
OpenAI-images REST shape; other providers need a small adapter.

## Output contract

Final PNGs land next to the stick's existing art (e.g.
`resources/games/vol7/<stick>/scenes/<id>.png`) and are loaded by the
scene as a TextureRect (the HeroImage PNG-override path). The old
HeroImage JSON stays as the fallback until a PNG exists.

## Rollout

1. Sign off the STYLE on Salmonberry (title + endings).
2. Build `art_studio.html` (generate/replace, by studio).
3. Retrofit the whole catalog, studio by studio, through this pipeline.
