# THE SLOWSTICK AESTHETIC BIBLE

How every slowstick looks, and why. Read this before touching any
slowstick visuals, before authoring a new stick's LOOK section, and
before reviewing screenshots. It sits above the per-stick design
docs: where a design doc's look language conflicts with this file,
this file wins and the doc gets fixed.

---

## ⚑ DIRECTION CHANGE (2026-07-22) · this supersedes everything below for 2D scene art

User verdict: the flat-vector HeroImage look is not good enough. "I keep
asking for much better graphics." The bar, stated plainly:

> **Minimum early-1990s 256-color SVGA graphics, à la Sierra and
> LucasArts graphic adventures.** Slowsticks are modern games seen
> through an alt-reality prism — so their art is a rich painted source
> pressed through a period 256-color dithered SVGA "era filter."

What this changes:
- **Flat vector `HeroImage` (polys/gradients at 160×90) is retired for
  scene/hero art.** It stays only as a fallback and for tiny UI glyphs.
- **New pipeline (`godot/tools/art/`, see `ART_PIPELINE.md`):** a
  painted SOURCE (AI via `scene_render.py`, or procedural placeholder
  via `scene_painter.py`) → the ERA FILTER (`svga_quantize.py`,
  ~320×200, 256-color, dithered). Both source kinds share one filter,
  so the catalog keeps one register.
- **The old "banned list" below is REVERSED for slowstick 2D scenes:**
  low-res 256-color render targets, dithering, and a period SVGA look
  are now the GOAL, not banned. (The bans still apply to the 3D VN
  locales and the `demoscene_post` shader stack — those are a separate
  system.) Font floor 12 still holds for UI text drawn over scenes.
- **Rollout:** sign off the style on Salmonberry, build `art_studio.html`
  (generate/replace every asset, by studio), then retrofit the whole
  catalog studio by studio.

Everything below predates this change; treat it as the 3D/locale +
post-process guidance and the historical record of the flat era.

---

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
| `homebrew` | no publisher (Sweetgum) | one ink, one duplicator, dialed to near-nothing | 30 | 0.04 | 0.0 | 0.0 |
| `yumemi` | Yumemi Denshi · Kyoto | inked line on paper tones, a hanging scroll's patience | 26 | 0.06 | 0.0 | 0.0006 |
| `sagebrush` | Sagebrush Engineworks · Amarillo | pulp-paperback cover inks, one violet in reserve | 22 | 0.12 | 0.0 | 0.0010 |
| `ranch` | RANCH · San Francisco | laminate-and-signage commercial graphics, crispest image | 28 | 0.05 | 0.0 | 0.0004 |
| `shelf` | Olaf's cabin · 2048 frame | warm neutral | 24 | 0.08 | 0.04 | 0.0008 |

Current wiring: FeyFaireHost → `rocha_faire` ·
EarthmanChroniclesHost → `astro_cortex` · SamsSummerShiftsHost →
`ranch` · PirateSummerHost → `oneironautics` · SpiderdropsHost →
`pdp_toys` · SlowstockShelf → `shelf`. Estuary 3's host predates the layer and inherits the
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

---

## Per-studio render LANGUAGES (2026-07-21)

The presets used to differ only by uniform dials (palette/dither/
scanline/aberration). They now also select a render MODE in
`demoscene_post` (`look_mode`), a distinct treatment per design
culture — house STYLE, still subtle, still "material not filter":

| mode | `look_mode` | reads as | studios |
|---|---|---|---|
| none      | 0 | clean, crisp | pdp_toys, ranch, meridian |
| gouache   | 1 | paper-tooth grain + gentle wash toward stock | oneironautics, yumemi, shelf |
| halftone  | 2 | posterized silkscreen inks broken by the bayer dot | rocha_faire |
| ink bleed | 3 | darkening where luminance edges pool (linework) | astro_cortex, sagebrush |
| grain     | 4 | fine warm speckle, near-nothing | homebrew |

Rules:
- **`look_mode` defaults to 0**, and CP / TAROT GAUNTLET never set it —
  they render exactly as before. Modes are a slowstick-only layer on the
  shared shader; backward-compatible.
- Extra uniforms: `paper_tint` (gouache/grain wash + tint), `grain_amount`,
  `ink_amount`. Set per preset in `SlowstickLook.PRESETS`.
- Keep it a whisper. If a screenshot says "filter," dial the mode's
  amount down. The mode should read as the studio's chosen medium — a
  gouache field guide, a silkscreen playbill, an inked pulp cover — not
  as an effect. Deck-verify; shader modes can't be proofed in CI.
