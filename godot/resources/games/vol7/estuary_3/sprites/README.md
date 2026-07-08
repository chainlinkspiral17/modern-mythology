# Estuary 3 · sprite system

Palette-indexed JSON sprites, per-act. Each act has its own
visual language; the loader is common. Design intent is captured
in `lore/_ESTUARY_3_DESIGN.md` under §Sprite techniques.

## File format

Each sprite is one JSON file. Minimum viable schema:

```json
{
  "w": 12,
  "h": 12,
  "palette": ["transparent", "#7a8896", "#4a5866", "#e6d054"],
  "data": [ /* w * h ints, row-major, indexing into palette */ ]
}
```

Optional keys:

| key           | shape                       | meaning |
|---------------|-----------------------------|---------|
| `id`          | string                      | stable identifier · matches the filename stem |
| `origin`      | `[x, y]`                    | pivot (default: center of the sprite) |
| `hotspots`    | `{name: [x, y], ...}`       | named anchor points (eye, hand, muzzle, etc.) |
| `attribution` | string                      | authored-by tag |
| `notes`       | string                      | free-form design commentary |

### Palette rules

- Index `0` is always transparent by convention. The loader
  accepts either the literal string `"transparent"`, an empty
  string `""`, or a fully-transparent hex `"#00000000"` in slot 0.
- Everything else is `#rgb`, `#rgba`, `#rrggbb`, or `#rrggbbaa`.
- Godot's `Color("#hex")` parses all four forms.

### Data layout

`data` is a flat array of `w * h` ints, row-major (row 0 first).
Each int indexes into `palette`. Out-of-range indexes render as
palette index 0 (transparent) with a `push_warning`.

### PNG override

If a PNG exists at the same path with a `.png` extension, the
loader prefers it and ignores the JSON. This is the escape hatch
for hand-drawn art: replace `heron.json` with `heron.png` at the
same 12x12 dimensions and the game picks it up with no code
change.

## Per-act visual language

**Act 1 · THE SHIFT · SCUMM-era hand-authored.** Kwik Stop
interior is a single hand-drawn 640x480 background per lighting
state. Character sprites 32x48, walk cycle + idle + action per
customer. Dialogue portraits 96x96. Sprites live under `act1/`.
Placeholder JSONs authored per shape; expect hand-drawn PNGs to
override.

**Act 2 · THE ESTUARY · procedural + tiny icons.** Map background
generated at runtime (value-noise elevation, hand-authored color
ramp). Species icons 8x8 to 12x12, palette-indexed, deliberately
abstract. Sprites live under `act2/` (this directory).

**Act 3 · THE TOWN · vector-style hero images.** One 640x360
hero image per location. Flat-color line art, 6-color palette per
image, chunky lines. Nine images total. Sprites live under
`act3/`. Text-forward gameplay; hero image is the frame.

**Act 4 · THE FIFTH SEASON · canvas-native procedural.** Beach
is a procedural canvas (sand-grain value noise, waterline pixel
row, tide-pool ellipses). Sea creature sprites 6x6 to 10x10,
single-color silhouettes. The player's line is a real-time
stroke buffer. Almost no static sprites; most of Act 4 is
generated live. What static sprites exist live under `act4/`.

## Loader

`godot/scenes/games/estuary_3/SlowstockSprite.gd`. Usage:

```gdscript
var s := SlowstockSprite.new()
if s.load_from("res://resources/games/vol7/estuary_3/sprites/act2/heron.json"):
    var tex := s.texture()
    var eye := s.hotspot("eye")
    # draw at pivot s.origin, offset by (eye - origin) for the eye
```

`SlowstockSprite` is a plain `RefCounted`. Multiple sprites can
share memory by holding references. No node overhead.

## Currently authored

| Sprite         | Act | Size  | Status |
|----------------|-----|-------|--------|
| heron          | 2   | 12x12 | Placeholder, hand-composed pixels |
| otter          | 2   | 12x8  | Placeholder |
| coho           | 2   | 10x6  | Placeholder |
| sedge_wren     | 2   | 8x8   | Placeholder |
| chum           | 2   | 10x6  | Placeholder · spawning "tiger stripes" as the signal |
| sturgeon       | 2   | 14x5  | Placeholder · elongated with dorsal ridge as the signal |
| cutthroat      | 2   | 10x6  | Placeholder · red-orange throat slash as the signal |
| tidewater_goby | 2   | 8x4   | Placeholder · smallest sprite, scale-appropriate |

The full Act 2 species-boost row (all eight species) is now
sprite-backed.  `EstuaryPlanner.gd` picks them up automatically
via `SlowstockSprite.load_from()`.

## Authoring a new sprite

1. Decide the act (visual language must match).
2. Decide dimensions. Keep them small; the whole game targets
   640x480 at 4x pixel scale, so a 32-pixel-wide sprite already
   fills a chunk of the screen.
3. Design the palette. 4-8 colors per sprite is the sweet spot.
4. Author the `data` array by hand, or write a small Python
   generator under `godot/tools/sprites/` that emits the JSON.
5. Add the file to the appropriate `sprites/act{n}/` folder.
6. Validate with `python3 -c "import json; json.load(open(...))"`.
7. Preview in Godot by loading it into a `TextureRect`; adjust.

## Deferred

- Project-wide palette registry (so multiple sprites share a
  palette by reference rather than inlining it every file). Not
  yet implemented; palettes are inline per file.
- Animation frames as `frames: [{data, dur_ms}, ...]`. Not yet
  implemented; sprites are static.
- Sprite atlas format for batching. Not yet implemented; each
  sprite is one file.
- Runtime paletted-remapping (e.g. the heron in dusk light with
  a different palette). Not yet implemented.
