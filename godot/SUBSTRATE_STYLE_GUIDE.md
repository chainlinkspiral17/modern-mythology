# SCUMM / Modern Mythology — ASCII Substrate Style Guide

This document defines the visual, structural, and naming conventions
for ASCII substrates in the Modern Mythology project. A new chat with
this document plus the project tree should be able to author a piece,
add it to a composition, and have it look at home with everything else.


## 1 — Premise

Every visual in Modern Mythology is the SCUMM machine's rendering.
ASCII is its native output. Richer media (sprite art, video, photo)
sit *above* the ASCII substrate at controlled opacity, never replacing
it. When the simulation thins you see the cells underneath. Volume
transitions are veil animations on the upper media, not scene swaps.

Authoring follows from this: ASCII pieces are first-class art, not
placeholders waiting for "real" assets.


## 2 — File system

```
resources/substrates/
    gallery/_index.json          gallery manifest (what's listed in the UI)
    gallery/<id>.json            single-substrate gallery items (rasterized)
    compositions/<id>.json       multi-window composition manifests
    pieces/<id>.json             individual windows used in compositions
    scene/<scene_id>.json        auto-loaded substrate for an engine scene
    <volume>/<id>.json           named substrate addressable from scenes
    _pieces/<id>.json            inputs for hand-coded composers
                                 (build_substrates.py reads these)

assets/<set>/<id>.png            source images for img2ascii conversion
tools/img2ascii.py               image → ASCII grid converter
tools/build_substrates.py        Python composer for hand-authored substrates
scenes/game/AsciiSubstrate*.gd   live + rasterized substrate renderers
scenes/game/AsciiWindow.gd       composition window renderer
scenes/game/AsciiComposition.gd  composition layout container
```


## 3 — Piece JSON schema

```json
{
  "width":   <int>,
  "height":  <int>,
  "charset": "ascii" | "blocks" | "braille",
  "color":   "fg" | "fgbg" | "mono",
  "source":  "<human-readable origin>",
  "cells":   [ [ { "c": "#", "fg": "#rrggbb", "bg": "#rrggbb"|null }, ... ], ... ]
}
```

Every cell has `c` (single character), `fg` (hex string or null), `bg`
(hex string or null). `null` means transparent → layer below shows
through. Use `fg` mode for transparent imagery, `fgbg` for opaque
backdrops.

**Do not use the braille charset.** Glyphs U+2800–28FF are not in
SpaceMono and cause font fallback hangs at scale. `blocks` covers the
density spectrum well enough on its own.


## 4 — Composition manifest schema

```json
{
  "id":     "<composition_id>",
  "canvas": [1920, 1080],
  "bg":     "#06080e",
  "windows": [
    { "path": "pieces/<id>", "x": 100, "y": 50,
      "font_px": 14, "z": 5 }
  ]
}
```

Canvas is the **logical** pixel space. The composition Control fits
itself to its parent while preserving aspect, so the same manifest
renders correctly at any viewport size.

`path` is relative to `resources/substrates/`. `font_px` controls the
window's render scale — different windows in the same composition
have different font sizes (small for dense imagery, large for
readable text).


## 5 — Naming

- IDs: `<volume_or_set>_<noun>[_qualifier]`. Lowercase, snake_case.
  Examples: `vol5_diner_predawn`, `tarot_fool_card_figure`,
  `pigboy_cite_box_top`.
- Composition IDs: same scheme. `tarot_fool` for the canonical Fool
  dashboard; `tarot_fool_v2` etc. for revisions.
- Piece file paths use the path-relative form in manifests, no
  `.json` extension: `pieces/cathedral_top`.
- Source images live at `assets/<set>/<noun>.png`. Crops for img2ascii
  are temporary and don't ship.


## 6 — Palette (per volume)

Vol 5 (Arcana) — primary palette:

```
Background dark        #040610  (canvas), #06080e (panel bg)
Background panel       #0a0e1a
Text dim               #7a8198
Text                   #cdd2e6
Accent cyan            #9bc3ff
Accent warm            #ffd17a
Neon red               #ff5544
Neon dim               #aa3826
Halo bg                #2a0c06
Card / figure white    #ffffff
Card / figure mid      #cdd2e6
Sun warm               #ffd17a
```

Vol 5 (Arcana) — secondary (for backgrounds, structures):

```
Pilothouse / dock      #5a4632
Hull / structure dark  #1b1610
Hull highlight         #3a2e22
Window frame           #3a2a18
Window warm            #ffbb55
Water deep             #060c18
Water mid              #1c2a45
Water ripple highlight #2a3a55
```

When adding a new volume, define its palette block here. Pieces should
draw colors from their volume's palette only — no improvised hex
values. Consistency comes from shared swatches across pieces.


## 7 — Character vocabulary

- Atmosphere / texture: `. , ' \` * ~ : ;`
- Structure / connectors: `+ - = | / \ _`
- Frames: `┌ ┐ └ ┘ ─ │ ┼ ╔ ╗ ╚ ╝ ═ ║`
- Block shading (image density): `░ ▒ ▓ █`
- Annotation: `[ ] { } ( ) < >`

Avoid unless deliberate:
- Braille (font fallback issue).
- Greek letters, mathematical symbols, arrows. Use only when the
  source content actually calls for them (real equation, real arrow).
  In glitch states they're appropriate; in normal content they
  introduce visual noise.


## 8 — Image-derived pieces (img2ascii)

For visual elements (figures, illustrations, mountains, circuits):

```bash
python3 tools/img2ascii.py \
  /path/to/cropped/source.png \
  --charset blocks --color mono \
  -w <cell_width> \
  -o resources/substrates/pieces/<id>.json
```

Defaults that work:
- `--charset blocks` for most imagery
- `--charset ascii` for very sparse / line-art content
- `--color mono` for white-on-dark woodcut style (matches the SCUMM
  machine's monochrome native output)
- `--color fg` when you want the source colors preserved
- `-w` in the 30–100 range for windowed pieces

For the cell width, aim for the rendered window to be roughly the
same proportion of the canvas as the source region is of the source
image. A region 240 px wide in a 1376 px source → ~17% of canvas →
~325 px on a 1920-wide canvas. At font 12 (~7 px cell width) that's
~46 cells.


## 9 — Text-derived pieces (hand-authored)

Anything that must be **readable as text** — cite-boxes, equations,
labels, dialog overlays — is hand-authored at low cell density with
large `font_px`. A 4-cell wide "FOOL" piece rendered at font 56 is
240 px of crisp typography. The same 4 cells at font 9 is illegible.

Author text pieces in `pieces/text_<id>.json` (single-word labels) or
`pieces/cite_<id>.json` (multi-line framed content). Use frame
characters `┌─┐│└┘` for cite-boxes; reserve `+-+|` for the substrate
inside scene engine layer (live mode, no rasterizer).


## 10 — Composition layout principles

1. **Densely packed.** The SCUMM machine doesn't waste display
   real estate. Pieces should be near each other, with small or zero
   gutters. Reference image as benchmark — almost no empty space.
2. **Z-order from background to foreground:**
   - `z=1` — atmospheric (PCB traces, distant mountains)
   - `z=2` — secondary content (charts, glitch clusters)
   - `z=3` — text panels (cite-boxes, equations)
   - `z=5` — primary subject (the card figure, character portrait)
   - `z=6` — labels on top of subject (card number, card name)
3. **Pieces of the same volume share their bg color.** No piece
   should sit on a different-colored block than its neighbors. Use
   `bg: null` when you want canvas/parent to show through.
4. **One central subject per composition.** The Fool card is the
   center of the Fool composition. Mountains, equations, cite-boxes
   orbit it. Don't have two competing focal points.


## 11 — Glitch as design language

Glitch is part of the tarot sequence aesthetic, not noise. Convention:

- Glitch is **character substitution** within a region. The piece is
  authored clean; glitch is applied at render time.
- Substitution vocabulary: same vocabulary as a piece's normal
  characters, plus a small mix of block-shading and `≠ ≈ ¬ ⊥` for
  the most corrupted state.
- Severity ramps per card position in the deck. The Fool (card 0) is
  lightly glitched. The Tower (16) is heavily corrupted.
- Glitch animation is independent per region — different pieces in a
  composition glitch on different schedules.

(Glitch primitives in `tools/build_substrates.py`:
`_glitch_chars()`, `_glitch_band(grid, x, y, w, h, severity, fg, seed)`.
Currently applied at composer-build time; runtime animation is a
future addition.)


## 12 — Hand-off checklist for a new chat

When passing a piece-authoring task to a new chat, include:

1. This file.
2. The composition manifest the piece will live in (paths help with
   positioning context).
3. The relevant volume's palette block.
4. The source image at `assets/...` and the crop coordinates, if
   image-derived.
5. The target cell width and font_px.
6. Any glitch / animation behavior expected.

A new chat with those inputs should be able to:
- Author the piece JSON directly, or run img2ascii with the right
  flags
- Drop the file at `resources/substrates/pieces/<id>.json`
- Add a windows entry to the composition manifest
- Re-run `python3 tools/build_substrates.py` if it touches a
  composer-built substrate


## 13 — Open items (track here)

- [ ] Music player composition (BGM-reactive VU windows). See
      planned `AsciiVisualizer` node.
- [ ] Per-card composition for the remaining 21 Major Arcana.
- [ ] Veil shader for rich-media layering above the substrate.
- [ ] REXPaint `.xp` import path (for hand-authored pieces produced
      in a real ASCII editor).
- [ ] Runtime glitch animation (currently composer-time only).
