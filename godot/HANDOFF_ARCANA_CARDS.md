# HAND-OFF — Major Arcana cards 1–21

## What this is

The Fool (card 0) is built. Each remaining Major Arcana card needs its
own gallery composition, following the same pipeline. This is a
self-contained brief for a new chat session.

## Read first

1. `SUBSTRATE_STYLE_GUIDE.md` — palette, character vocabulary, naming
   conventions, glitch design language, composition layout principles.
2. `SUBSTRATE_README.txt` — file layout and how the pieces fit together.
3. `resources/substrates/compositions/fool_arcana.json` — reference
   composition for card 0 (single-piece textual card).
4. `resources/substrates/compositions/music_player.json` — fancier
   layered composition with image bg + shimmering ASCII + visualizer +
   shadowed title.

## Cards to build

| #  | Card             | Scene id                  |
|----|------------------|---------------------------|
| 1  | The Magician    | `vol5_ch1_magician`       |
| 2  | The Priestess   | `vol5_ch2_priestess`      |
| 3  | The Empress     | `vol5_ch3_empress`        |
| 4  | The Emperor     | `vol5_ch4_emperor`        |
| 5  | The Hierophant  | `vol5_ch5_hierophant`     |
| 6  | The Lovers      | `vol5_ch6_lovers`         |
| 7  | The Chariot     | `vol5_ch7_chariot`        |
| 8  | Strength        | `vol5_ch8_strength`       |
| 9  | The Hermit      | `vol5_ch9_hermit`         |
| 10 | Wheel of Fortune| `vol5_ch10_wheel`         |
| 11 | Justice         | `vol5_ch11_justice`       |
| 12 | The Hanged Man  | `vol5_ch12_hanged`        |
| 13 | Death           | `vol5_ch13_death`         |
| 14 | Temperance      | `vol5_ch14_temperance`    |
| 15 | The Devil       | `vol5_ch15_devil`         |
| 16 | The Tower       | `vol5_ch16_tower`         |
| 17 | The Star        | `vol5_ch17_star`          |
| 18 | The Moon        | `vol5_ch18_moon`          |
| 19 | The Sun         | `vol5_ch19_sun`           |
| 20 | Judgement       | `vol5_ch20_judgement`     |
| 21 | The World       | `vol5_ch21_world`         |

## Per-card pipeline

For each card, given a reference PNG at `assets/gallery/<name>.png`:

### 1. Crop the card region
```bash
python3 - <<PY
from PIL import Image
src = Image.open('assets/gallery/magician.png').convert('RGB')
# Determine card crop bounds from the reference image
# (usually the central tarot card panel)
card = src.crop((LEFT, TOP, RIGHT, BOTTOM))
card.save('/tmp/magician_card.png')
PY
```

### 2a. Image-derived piece (block-ASCII conversion)
```bash
python3 tools/img2ascii.py /tmp/magician_card.png \
  --charset blocks --color mono -w 80 \
  -o resources/substrates/pieces/magician_card_figure.json
```

### 2b. OR Text-as-art piece (figure rendered from chapter narrative)
```bash
python3 tools/text_render.py /tmp/magician_card.png \
  --text resources/scenes/vol5/vol5_ch1_magician.json \
  -w 110 --high 0.50 --mid 0.18 \
  --shadow-bg "#0a0808" \
  -o resources/substrates/pieces/magician_card_textual.json
```

### 3. Write the composition manifest
```
resources/substrates/compositions/magician_arcana.json
```

Follow the pattern in `fool_arcana.json` (single piece, fullscreen)
or `tarot_fool_v2.json` (multi-window dashboard). Use the per-volume
palette block in the style guide.

### 4. Author a title piece
```
resources/substrates/pieces/title_magician.json
```

Pattern (from `pieces/title_fool.json`):
```
─── 1 ─────────
  THE MAGICIAN
───────────────
```

3 rows, multiline, white fg, no bg. Shadow added by composition manifest
(`"shadow_color": "#000000", "shadow_offset": [4, 4]`).

### 5. Register in the gallery index
Append to `resources/substrates/gallery/_index.json`:
```json
{
  "id": "magician_arcana",
  "title": "1 — THE MAGICIAN  (textual)",
  "set": "Major Arcana",
  "type": "composition",
  "path": "magician_arcana",
  "always_unlocked": true
}
```

## Source images

If `assets/gallery/<card>.png` doesn't exist for a card you're authoring,
note it as a blocker and proceed with hand-authored ASCII figure pieces
instead. Pure hand-author pattern: use the helpers in
`tools/build_substrates.py` (Grid class, stamp, box, glyph stamps).

## Hand-off output

For each card, the deliverable is:
- `resources/substrates/pieces/<card>_card_*.json` — the figure piece(s)
- `resources/substrates/pieces/title_<card>.json` — title strip
- `resources/substrates/compositions/<card>_arcana.json` — manifest
- Patch entry appended to `resources/substrates/gallery/_index.json`

Zip those files (preserving paths) and return as a single drop.

## Style consistency targets

- All cards share the `arcana` volume palette (defined in the style guide).
- Title piece format is consistent (number — name, 3-row).
- Drop shadow on all title pieces: `"#000000"` / `[4, 4]` offset.
- Image conversion: blocks-mono at -w 80 for card figures, text-render
  at -w 110 for textual variants.
- Composition canvas: `[1920, 1080]` always; bg `#040610`.

## Testing

Run the project, open Gallery → ASCII SUBSTRATES section. Each new
composition should show as a tile with its title + "Major Arcana" set
label. Click to fullscreen-render.
