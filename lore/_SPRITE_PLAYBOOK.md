# Sprite playbook

Hard-won rules for authoring, loading, and rendering 2D sprite
art in the Modern Mythology project. Companion to
`godot/scenes/games/estuary_3/SlowstockSprite.gd` (the loader),
`godot/scenes/games/estuary_3/HeroImage.gd` (the primitive-
language rasterizer), and the per-act sprite folders under
`godot/resources/games/vol7/estuary_3/sprites/`.

## Core rules

### Two sprite tiers. Different tools per tier.

The project uses two distinct sprite systems, matched to
purpose:

- **Palette-indexed bitmap sprites** (`SlowstockSprite`) · for
  characters, species icons, small silhouettes. Native-res
  hand-composed pixel arrays. `{palette, w, h, data, origin?,
  hotspots?}`. Bounded 4×2 (tiniest species) to 32×48
  (character portraits). No procedural math.
- **HeroImage vector-style scenes** (`HeroImage`) · for
  location backgrounds, room interiors, cartridge spines.
  Compositions of primitives (fill · hband · rect · hline ·
  vline · dot · polyline · poly · text with 3×5 font). Native
  low-res (typ. 160×90 or 44×128) upscaled nearest-neighbor to
  target size · chunky vector look survives the scale.

Pick the tier by asking: "would authoring this pixel-by-pixel
be tolerable?" If yes → SlowstockSprite. If the answer is "no,
this is a scene with shapes" → HeroImage.

### Every render path has a fallback.

`FifthSeasonBeach._render_creature` prefers a SlowstockSprite
loaded from `sprites/act4/<cid>.json`, falls back to a
per-species colored ColorRect placeholder if the file is
missing or malformed. Same pattern in `TownWalkabout._make_
hero_image` and `SlowstockShelf._make_cartridge_slot` and
`KwikStopRoom._render_room`. **Never remove the fallback** ·
if the JSON breaks in a live playtest, the game keeps drawing.

### PNG-override escape hatch is preserved everywhere.

`SlowstockSprite.load_from(path)` tries `.png` at the same stem
FIRST, then `.json`. Any placeholder JSON can be overridden by
dropping a hand-drawn PNG at the same path with the same
dimensions · zero code changes. This means:  a hand-drawn 32×48
character sprite drops in as `sprites/act1/mr_aandahl.png` and
the JSON pixel-composed version becomes the fallback.

### Palette index 0 is always transparent.

Convention across every sprite in the project. Palette 0 is
either the literal string `"transparent"`, an empty string
`""`, or a fully-transparent hex `"#00000000"`. Anything else
in the palette is opaque. Don't try to use partial alpha in
palette-indexed sprites · use the modulate on the containing
Control.

### Hotspots are named anchors, not required.

Sprites can declare named hotspots (`{"eye": [7, 2]}`,
`{"feet": [5, 12]}`). The loader returns Vector2 for
`sprite.hotspot("name")` · returns `origin` if the name doesn't
exist. Useful for anchoring dialogue bubbles, UI overlays,
sparkle animations. Not required · sprites without hotspots
just anchor at origin.

### HeroImage uses low-res + upscale for the chunky look.

Native canvas for hero images is small (160×90 for locations,
44×128 for cartridge spines). The rasterizer nearest-neighbor
upscales to the target size. This gives:

- Fast authoring (a 160×90 canvas fits ~30 layered primitives)
- Chunky pixels at 640×360 (4× upscale) that read as
  intentional-vector-style, not accidental-blur
- Tiny JSON footprint per sprite (~30-40 lines of shapes)

Don't author hero images at native 640×360. The primitive
count explodes and the vector-style look dissolves into over-
detailed noise.

### One palette per sprite. 4-6 colors per palette.

Every sprite carries its own palette inline. Common temptation:
"share the palette across all Act 2 species icons." Don't ·
each species's palette communicates something distinct (chum's
tiger stripes are dark green-purple; sturgeon's dorsal ridge is
olive; cutthroat's throat slash is red-orange). Six colors is
the sweet spot; 8-10 is too many; 3 is too few for anything
character-shaped.

### 3×5 pixel font is enough for signs and titles.

`HeroImage._draw_text()` ships uppercase A-Z, digits 0-9, and
a few punctuation. That's enough for cartridge spines
("ESTUARY 3", "PIRATE SUMMER"), building signs ("KWIK",
"CLOSED"), and location captions ("WELCOME BACK SAM"). Don't
try to add lowercase or fancy glyphs · the whole point is
chunky, era-appropriate.

## Recent lessons

### 2026-07-08 · sprite arc · 44 sprites across 6 categories, from placeholder to authored

Followed the audio arc's audit-driven cadence. In six commits:
4 Act 2 species icons · 6 Act 4 creature silhouettes · 9 Act 3
hero images · 3 Act 1 room lighting states · 5 Act 1 character
sprites · 10 shelf cartridge spines · plus a new `HeroImage`
rasterizer.

Lessons:

- **A primitive language for hero images beats hand-composed
  pixel data by 20:1.** A 160×90 hero image would be 14,400
  pixels of `data[]` if hand-composed. As a HeroImage scene
  it's ~30 layered primitives · a 30-line JSON. Every location
  hero image (~9 of them) fit in a single-sitting commit
  because the primitive language was the right abstraction.
- **Fallbacks are what make placeholder art shippable.** The
  first pass on every category used ColorRect placeholders.
  Adding the SlowstockSprite/HeroImage authored art was
  additive · every controller kept its ColorRect fallback
  path, so a missing sprite JSON gracefully degrades to the
  previous look. This is how you ship 44 sprites over one arc
  without breaking anything: never remove the fallback until
  the sprite is verified in-engine.
- **PNG-override is priceless.** Every path prefers PNG at the
  same stem, so a hand-drawn override drops in without code
  change. This unblocks future art passes · someone else can
  paint the Kwik Stop room in Aseprite and drop
  `kwik_stop_room.png` at the same path, and the JSON version
  becomes the placeholder. Never lock the pipeline to a single
  authoring path.
- **Palette-index-0-is-transparent is the discipline.** Every
  sprite in the project follows this. When a new spritesheet
  arrives that doesn't, it's the ONE thing to normalize before
  loading · everything else about the loader is robust.
- **Character sprites live for a moment then queue_free.** The
  KwikStopRoom counter render spawns a 16×24 character sprite
  at customer arrival, upscaled 3×, that queue_frees after 5
  seconds via a SceneTree timer. This gives the moment
  presence without cluttering the counter with five stacked
  figures on a busy turn. Same approach works for any
  "arrival" beat · don't try to persist visitors; let them
  arrive and leave.
- **The 3×5 font is enough for signs.** Wanting lowercase or
  bigger text is a signal to change the sprite's scale, not
  extend the font. If a cartridge spine title feels too
  cramped at 3×5, upscale the whole HeroImage · the text stays
  proportional and legible.

## TEMPLATE — new lesson entry

```
### YYYY-MM-DD · short session title

- **Punchy lesson, present tense.** Two-to-four sentences.
- **Next lesson.** Same shape.
```
