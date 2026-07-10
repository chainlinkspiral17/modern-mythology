# THE SLOWSTICK AESTHETIC BIBLE

How every slowstick looks, and why. Read this before touching any
slowstick visuals, before authoring a new stick's LOOK section, and
before reviewing screenshots. It sits above the per-stick design
docs: where a design doc's look language conflicts with this file,
this file wins and the doc gets fixed.

---

## The premise · alternate-universe tech

**Slowsticks are technology from an alternate timeline.** They
never passed through our world's hardware bottlenecks — no CRTs,
no phosphor monochrome, no 8-bit palettes forced by RAM, no
NTSC artifacts. Those constraints simply never existed there.

Therefore slowsticks must never COSPLAY our retro:

- **No hand-drawn scanline overlays** (the old ColorRect-per-line
  trick is banned; it was removed from Earthman Chronicles in the
  2026-07 look pass).
- **No "phosphor" fiction, no CRT curvature, no NTSC bleed,
  no dot-matrix / bitmap-font "authenticity" theater.**
- **No naming our-timeline hardware or games as reference points
  in design docs** ("Elite vectors", "1988 hardware sells the
  constraint"). The fictional YEAR stays; the idea that the year
  imposed a rendering limit goes.

What each stick DOES have is a **design culture**: a studio, a
city, a year, and a set of aesthetic choices its makers believed
in. Palette discipline, composition rules, type character — these
are house STYLE, chosen the way a printmaker chooses three inks.
Style is kept religiously. Limitation-cosplay is banned.

## The rendering · modern, Deck-native

- Target: **Steam Deck, 1280×720 project viewport**, GL
  Compatibility, stretch mode canvas_items. Full-res, smooth,
  no fake low-res buffers.
- Every slowstick renders through the SAME post-process language
  as TAROT GAUNTLET and COMMUNITY PLANNED:
  `godot/assets/shaders/demoscene_post.gdshader`, applied by
  **`SlowstickLook.apply(host, preset)`**
  (`godot/scenes/games/estuary_3/SlowstickLook.gd`) — one call in
  the host's `_ready`, right after `add_to_group("ui")`.
- The layer is named `SlowstickLook`, layer 80, joins
  `"world_render"` (the F4 escape-hatch group — it is the picture,
  not HUD), and its ColorRect uses `MOUSE_FILTER_IGNORE`.
- The treatment must read as **material, not filter**. If a
  screenshot makes someone say "oh, a CRT filter," the preset is
  too hot. Uniform values stay subtle (dither ≤ ~0.25, scanline
  ≤ ~0.10, aberration ≤ ~0.002).

## Type · Deck-readable floor

Handheld screen, couch distance. Font-size floor applied in the
2026-07 pass (the BUMP map): nothing below 12; body text 14–16;
old 8/9/10pt debug-sized labels are gone. New UI starts at 12
minimum, 14+ for anything the player actually reads.

## The per-studio presets

Defined in `SlowstickLook.PRESETS`. One preset per design culture,
not per game.

| preset | studio · city | reads as | palette | dither | scanline | aberr |
|---|---|---|---|---|---|---|
| `oneironautics` | Oneironautics · Portland | field-guide gouache, paper tooth | 24 | 0.10 | 0.06 | 0.0008 |
| `rocha_faire` | Rocha-era Oneironautics 1990 | hand-inked cel over cream stock, silkscreen banding | 20 | 0.14 | 0.05 | 0.0012 |
| `astro_cortex` | Astro-Cortex · Culver City | precision-instrument glass, the most machine-like | 14 | 0.22 | 0.10 | 0.0018 |
| `pdp_toys` | PDP Toys · Beaverton | injection-molded toy-bright, catalog photography | 32 | 0.03 | 0.0 | 0.0006 |
| `ranch` | RANCH · San Francisco | laminate-and-signage commercial graphics, crispest image | 28 | 0.05 | 0.0 | 0.0004 |
| `shelf` | Olaf's cabin · 2048 frame | warm neutral | 24 | 0.08 | 0.04 | 0.0008 |

Current wiring: FeyFaireHost → `rocha_faire` ·
EarthmanChroniclesHost → `astro_cortex` · SamsSummerShiftsHost →
`ranch` · PirateSummerHost → `oneironautics` · SlowstockShelf →
`shelf`. Estuary 3's host predates the layer and inherits the
shelf treatment when launched from it; give it `oneironautics`
if it ever gets its own pass.

New studios get new presets HERE (with a comment naming the
design culture), never inline uniform values in a host.

## How to write a LOOK section now

Right: *"One held wide shot per location — Oneironautics' tableau
discipline; the stillness is the point."* The style is a school of
design, defended on its own terms.

Wrong: *"One screen per location because 1988 hardware couldn't
scroll."* That imports our timeline's limits.

The year and place still saturate everything — through palette,
light, subject, sound, and what the makers cared about — just
never through pretend hardware failure. Deliberate authorial
artifacts (Sweetgum's fault-band, the mis-set wrap) are canon
because a PERSON made them, not because a machine did.

## Banned list (quick reference)

- ColorRect scanline loops, vignette-as-CRT, screen curvature
- "phosphor", "raster", "NTSC", "VGA" as look descriptions
- Our-timeline hardware/games named as visual reference in docs
- Fake low-resolution render targets / integer-downscale buffers
- Any font size under 12
- Per-mesh or per-scene bespoke post shaders (use the demoscene_post
  presets; if a stick truly needs a new uniform, extend the shader
  house-wide, don't fork it)
