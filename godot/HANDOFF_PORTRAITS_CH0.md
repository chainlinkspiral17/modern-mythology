# HAND-OFF — Character portraits, Volume 5 Chapter 0

## What this is

The Fool's chapter (vol5 ch0) features three named characters:

- **John Frank** — grad student, mixed-media journalist, night waiter at
  D'Ambrosio's. POV character.
- **Frasier Temple** — the Magician figure. Bomber jacket, chaotic hair,
  notebook tucked under arm. Coalesces from the kitchen alcove.
- **The Stranger** — the figure from the booth. The catalyst. (Some
  scenes also refer to "the man in booth six".)

These show up in scenes via `{"t": "show", "char": "stranger", "pos": "left"}`
etc. CharLayer.gd currently renders placeholder silhouettes for characters
without PNG art. Your job is to author ASCII portrait pieces for each, and
choose how they integrate.

## Scenes that need portraits

| Scene id                    | Characters present (in dialog) |
|-----------------------------|--------------------------------|
| `vol5_ch0_booth6`           | john (narration), stranger      |
| `vol5_ch0_frasier`          | john, frasier                   |
| `vol5_ch0_model_city`       | john, frasier                   |
| `vol5_ch0_closing`          | john                            |

## Read first

1. `SUBSTRATE_README.txt` — architecture map.
2. `SUBSTRATE_STYLE_GUIDE.md` — palette, char vocab, naming.
3. `scenes/game/CharLayer.gd` — how portraits currently render. The
   `_make_placeholder()` function is the silhouette fallback you're
   replacing/augmenting.
4. `resources/scenes/vol5/vol5_ch0_*.json` — read the dialog to ground
   your character feel.
5. `tools/img2ascii.py`, `tools/text_render.py` — your conversion tools.

## Three integration options

Pick one before authoring:

### A — Standalone gallery portraits (lowest risk)
Each character gets a gallery composition you can view. No engine changes.
- `resources/substrates/pieces/portrait_john.json` (image or text-art)
- `resources/substrates/compositions/portrait_john.json` (manifest)
- Entry in `resources/substrates/gallery/_index.json` with
  `volume: 5`, `set: "Chapter 0 — Portraits"`,
  `unlock_pattern: "vol5_ch0_*"`

### B — Replace CharLayer placeholders
When `show` directive fires, render the ASCII portrait instead of the
silhouette. Engine change to `CharLayer.gd`. Pieces named e.g.
`pieces/portrait_<char>.json`. CharLayer would instantiate an
`AsciiWindow` per slot with the piece path computed from the char name.

### C — Both
Author the pieces once; use them in CharLayer AND as gallery items.

## Per-character authoring

### Without source art
You probably don't have character PNGs. Use `text_render.py` with the
character's dialog lines from `vol5_ch0_booth6.json` etc. as the char
vocabulary. Feed a stand-in silhouette image (or a hand-authored
silhouette JSON via build_substrates) as the shape source.

If you have time: hand-author the silhouettes following the Fool's
visual conventions (white-on-dark, density gradient with block chars).

### Suggested cell dimensions (per piece)
- Standalone gallery portrait: 80 wide × 110 tall, font_px ~14 for
  display in compositions (≈672 × 1540 px when rendered alone).
- CharLayer integration: match `CharLayer.SPRITE_W / SPRITE_H` =
  320 × 575 px (the existing slot dimensions). With font_px=11 → cell
  count ~48 × 52.

### Title piece (gallery option)
Same 3-line pattern as `pieces/title_fool.json`:
```
─── JOHN ───
 JOHN FRANK
────────────
```
3 rows, white fg, no bg. Composition adds black shadow.

## Style consistency targets

- Vol 5 palette (arcana) — see SUBSTRATE_STYLE_GUIDE.md
- Same char vocab as Fool/Magician
- If gallery item: drop shadow on title, black bg (#040610)
- Visualizer / spiral effects are NOT needed for portraits unless you
  want to add an idle "breathing" wash

## Pipeline commands

Crop reference (if you have art):
```bash
python3 - <<PY
from PIL import Image
src = Image.open('assets/characters/john_frank.png').convert('RGB')
src.crop((L, T, R, B)).save('/tmp/john_crop.png')
PY
```

Image-derived blocks-mono figure:
```bash
python3 tools/img2ascii.py /tmp/john_crop.png \
  --charset blocks --color mono -w 80 \
  -o resources/substrates/pieces/portrait_john.json
```

Text-art from dialog:
```bash
python3 tools/text_render.py /tmp/john_silhouette.png \
  --text resources/scenes/vol5/vol5_ch0_booth6.json \
  -w 80 --high 0.50 --mid 0.18 --shadow-bg "#0a0808" \
  -o resources/substrates/pieces/portrait_john_textual.json
```

Register in gallery (option A):
Append to `resources/substrates/gallery/_index.json`:
```json
{
  "id": "portrait_john",
  "title": "Portrait — John Frank",
  "set": "Chapter 0 — Portraits",
  "type": "composition",
  "path": "portrait_john",
  "volume": 5,
  "unlock_pattern": "vol5_ch0_*"
}
```

## Deliverable

For each character, you ship:
- `resources/substrates/pieces/portrait_<char>.json`
- `resources/substrates/pieces/title_<char>.json` (gallery option)
- `resources/substrates/compositions/portrait_<char>.json` (gallery option)
- Gallery `_index.json` entries
- If option B/C: modified `scenes/game/CharLayer.gd`

Zip the deliverables (preserving paths) and return as a single drop.
