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

### 2026-07-08 · procgen tiles + walk-cycle animation, procgen deterministic

Pirate Summer's tileset went from 100% ColorRect to ~95%
pixelart via a small procgen script (`godot/tools/sprites/
procgen_ps_tiles.py`).  Twenty-four 16×16 SlowstockSprite
tiles authored as deterministic Python patterns · no
Random.random, so `python3 procgen_ps_tiles.py` twice produces
byte-identical output.

Sam's walk cycle uses the same trick: `sam_<dir>_walk.json`
generated from `sam_<dir>.json` by shifting the leg pixels up
one row on the alternate side.  During movement tween, the
sprite swaps to walk-frame at step start and back to idle at
step end.  Two frames per direction, eight sprites total.

Lessons:

- **Procgen tiles are the right abstraction for 16×16.** Pixel-
  patterns at that resolution are noise + dots + bands + a few
  fixed positions.  Every tile fit in ~25 lines of Python.  A
  hand-drawn spritesheet would take an artist a day; the
  procgen version took one commit.  A future artist replaces
  the JSON with a PNG at the same stem and the loader picks it
  up automatically · zero-cost art upgrade path.
- **Deterministic procgen is not just for reproducibility · it
  makes iteration cheap.**  Tweak the pattern function, re-run
  the script, commit the diff.  Because there's no randomness,
  the diff is exactly the visual change intended.  This is why
  I can regen `path.json` a dozen times honing the pebble
  density without inspecting every generated pixel.
- **A two-frame walk cycle is legibly walking at 24-px tiles.**
  Sam's walk animation is idle + leg-shifted-up-one-row.  Two
  frames.  At 0.14s per step, alternating is enough motion for
  the eye to read as walking.  You don't need four frames to
  legibly walk at low resolution · you need one contrasting
  frame, and you need it to swap on move.
- **All-portraits-are-your-sprite works surprisingly well.**  The
  dialogue portrait uses the character's overworld sprite
  upscaled 3× in a bordered frame.  It's the same sprite Sam
  can see in the world.  This ties the two representations
  visually · when Wu Kai's overworld sprite is a green-sweater
  small figure, his dialogue portrait is a green-sweater
  small figure.  No cognitive translation between views.  A
  richer portrait pass (48×64 emotional variants) is a future
  Wave that slots in at the same call site without changing
  any other code.

### 2026-07-08 · palette-variant sprites carry seventeen speaking characters

Pirate Summer's cabin walls have five bunkmates each; the camp
has three counselors; the total speaking cast is seventeen.
Every one of them ships as a palette variant of Sam's 16×24
pose data · same body, different colors for skin, hair,
shirt, shorts, shoes, and outline.

Lessons:

- **Palette-variant sprites are enough at 16×24 to distinguish
  characters at a glance.** Bea's red hair and brown corduroy
  read as *Bea*; Wu Kai's green sweater and black hair read as
  *Wu Kai*. The player never confuses two speakers in a room.
  This is the shortcut that made shipping 17 characters in one
  session possible. It works because 16×24 leaves the palette
  doing most of the identification work · silhouette detail
  would fight the palette for the eye's attention.
- **Palette variants are honest placeholders, not permanent
  art.** They stop working the moment a character needs a
  unique action (Bear casting a fishing line, Wilson carrying
  his bag, Sylvie mid-song). Then a unique pose data set
  becomes worth authoring. Ship the palette variant first,
  come back to the silhouette when a specific scene demands
  it. Nothing in the pipeline breaks · the loader doesn't
  care whether two sprites share pose data.
- **Character palette hints belong in the character def, not
  the sprite file.** Every camper's JSON has a
  `portrait_palette_hint` string ("warm ochre · red hair ·
  freckles · brown corduroy overalls"). The sprite JSON's
  palette is *derived* from that hint. When we author the
  48×64 dialogue portraits later (Wave B-tail+), the hint
  carries forward · the portrait doesn't need to be
  re-designed from scratch. Character description outlives
  any specific rendering of the character.

## TEMPLATE — new lesson entry

```
### YYYY-MM-DD · short session title

- **Punchy lesson, present tense.** Two-to-four sentences.
- **Next lesson.** Same shape.
```
