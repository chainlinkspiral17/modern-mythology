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

### 2026-07-09 · pixel-art polish for the 1976 cache · HeroImage as a moment card

Eight HeroImages authored in one sitting once the primitive
language + `_show_hero()` overlay were in place: four for the
Nika Voss cache reveal (cache reveal · group photo · cassette
playback · hollow spruce), four for surrounding mystery + ending
beats (watched island · federal boat · hunter's note · Saturday
bus).  Each is 90-140 layered ops · a 20-line Python function.
Plus six new east-forest-deep tile kinds and three cache item
sprites.

Lessons:

- **The 20:1 primitive-language ratio holds under load.** Eight
  fresh HeroImages · roughly 800 primitives total · fit in one
  commit including the overlay wiring, and every one is
  legible and thematic.  The abstraction never buckled.  If a
  future arc needs 20+ HeroImages, the language keeps working;
  the bottleneck is compositional taste, not authoring cost.
- **Wire the moment card first, THEN author the art.** The
  cache-reveal HeroImages sat unused for one commit because
  `_show_hero()` didn't exist.  Once the overlay was in the
  HUD CanvasLayer (~50 lines · F4-compliant · auto-dismiss),
  every subsequent HeroImage was one line to trigger.  The
  overlay is the multiplier · without it, HeroImages are
  scrapbook art with no on-screen surface.
- **One `_show_hero(id, caption)` per discovery, not per
  interaction.**  The Saturday bus-home card fires ONCE (at
  the day 5→6 transition), not on every day-advance.  Re-fires
  cheapen the moment.  Gate every HeroImage on the
  first-time-only branch of a `_discover_fact()` block · the
  authored art is per-reveal, not per-tap.
- **Palette-per-scene is worth the 20 slots.**  Every
  HeroImage authored today defined its own palette · 18-24
  entries · optimized for that specific mood (twilight
  offshore, overcast working-boat gray, sepia summer
  photograph, sunless forest deep).  A shared "pirate summer"
  palette would have flattened the eight moments into one
  mood.  Local palettes are how eight cards stay distinct.

### 2026-07-09 · animation arc · walk cycle, NPCs, environment, indicators

Extended the sprite system into motion.  In four commits:
Sam's 2-frame walk gait + idle bob + 3-frame dig · 187
procedurally-derived NPC directional sprites + face-Sam
behavior · 3-frame fire + 2-frame water env animation · 2-frame
"!" indicator above adjacent interactables.  Also 8 more
HeroImages spanning the remaining big story beats.

Lessons:

- **Shared-layout characters make procgen cheap.** All 17
  non-Sam characters have identical 16×24 pixel layouts,
  differing only by palette.  Once Sam had authored
  directional + walk variants, deriving the same set for every
  other character was mechanical: lift the head-region rows
  (facing) and foot-region rows (walk) from Sam, splat them
  onto each character's data, keep their palette.  187 sprites
  from 17 authored + 8 patch templates.  If future characters
  break the shared layout (new species / a taller kid), the
  patch approach fails — but until then it's the fastest way
  to N-x a character roster.
- **One `_env_anim_frame` counter, many consumers.** Fire
  cycles 3-frame, water 2-frame, interact-indicator 2-frame ·
  they all read from the same `_env_anim_frame` mod their own
  cycle length.  Adding a fourth animated thing costs one
  entry in `_ENV_ANIM_CYCLES`.  Multiple timers would drift
  against each other; a shared frame counter can't.
- **CanvasModulate for time-of-day.**  A single
  CanvasModulate under `_world_root` tints every tile / Sam /
  NPC in one call.  HUD (on `_hud_layer`) stays bright because
  it's a different CanvasLayer.  The block→color table is 10
  lines; a zone override table is another 7.  Beats
  per-sprite palette-swaps by three orders of magnitude and
  survives NPCs animating (the CanvasModulate re-tints each
  frame).
- **F4 masters everything visible.**  The interaction "!" is
  world-scrolling art in `_world_root`, but it's still UI · the
  player wants clean screenshots.  Two guards: join the "ui"
  group (F4 catches it) AND check `FirstPersonController.hud_visible`
  in the per-frame ticker (so we don't re-show it after F4).
  Belt and suspenders because F4 fires on a moment; the ticker
  fires every frame.

### 2026-07-09 · FeyPortrait · a third tier: procedural-with-override

Fey Faire needed 101 negotiation portraits. Authoring 101 JSONs was
wrong; one placeholder for all was worse.

- **Procedural-from-data beats both extremes when the roster is
  huge.** `FeyPortrait.gd` generates a deterministic 32×40 face
  from the fey's own catalog row: court → palette, tier → frame
  pips, id-hash → geometry (head, eyes, mouth, hair) + court
  feature (petal ears / horns / antlers). Same fey = same face,
  different feys = visibly different. Zero per-fey authoring.
- **Keep the authored-override escape hatch from day one.** The
  generator checks `portraits/<id>.json` first and defers to a
  HeroImage when present. We hand-authored the ten most-met feys
  (Ondine, Cricket, Titania, Oberon, Puck, Green Man, Morgan,
  Erlking, Moth, Caliban) the same day, with zero caller changes.
  This is the same two-tier discipline as SlowstockSprite/PNG,
  now three tiers: authored JSON > procedural > (implicit) frame.
- **Hash bytes, not RNG.** Traits pull from fixed bit-ranges of
  `id.hash()` so the face survives save/reload and engine
  versions. No seeded RandomNumberGenerator to keep stable.

### 2026-07-10 · graphics pass 1 · HeroImage gains a shading vocabulary

User feedback: "everything is feeling really primitive." First
response was not more art — it was more LANGUAGE. HeroImage got
seven new ops (`vgrad`/`hgrad` Bayer-dithered gradients, `disk`,
`ring`, `noise` hash speckle, `shade` partial coverage, `checker`),
then the Kwik Stop's three room states were regenerated through
them (137 layers each, from ~30) by a deterministic script
(`tools/sprites/gen_kwik_stop_rooms.py`).

- **Flatness comes from fills, not from resolution.** The old
  rooms were flat because every surface was one palette index.
  A dithered two-stop gradient on the wall, a checker + shade on
  the floor, and light pools under the fixtures fixed "primitive"
  without adding a single pixel of resolution. Reach for `vgrad`/
  `shade` before reaching for a bigger canvas.
- **Dither is a printmaker's tool here, not a CRT one.** Bayer
  banding at 160×90 scale reads as silkscreen — that's inside the
  aesthetic bible. The banned list is about pretend hardware, not
  about ordered dither as ink technique.
- **Generate variants from one geometry table.** The three
  lighting states share every fixture position, so the hotspot
  coordinates in act1_kwik_stop.json stay valid across all
  nights. When art carries interaction anchors, author the
  variants from one script or they WILL drift.
- **Preview before pushing.** A ~100-line Python mirror of the
  rasterizer renders any HeroImage JSON to PNG (scratchpad
  `preview_hero.py`). Both wall-speckle and counter-grain looked
  fine as numbers and wrong as pictures (flies; wormholes) —
  caught in the preview, not on the Deck.
- **Hotspots over art must be translucent.** The old opaque beige
  interactable panels erased the art behind them; now they're
  5%-alpha amber-bordered outlines with a shadowed caption that
  brighten on hover. If a clickable region is drawn IN the art,
  the UI element over it should only outline, never fill.
- **CanvasLayer ignores parent visibility.** A hidden host's
  SlowstickLook layer keeps post-processing the screen — two
  stacked treatments once a stick boots over the shelf.
  `SlowstickLook.apply` now syncs layer.visible to the host via
  visibility_changed. Any future CanvasLayer child of a
  show/hide Control needs the same sync.

### 2026-07-10 · graphics passes 2-3 · Act 3 scenes, shelf backdrop, planner map

- **Nine scenes from one generator with shared vocabulary.** The
  Act 3 rebuild put `spruce()`, `figure()`, `bike()` helpers in
  the generator, so every scene got trees/people/bikes for one
  call. When a batch of scenes shares a world, write the
  vocabulary once — per-scene palettes keep them from flattening
  into one mood (each still names its own inks).
- **Keep the preview renderer in lockstep with HeroImage.** The
  scratchpad previewer was missing `poly` and A-Z, and the first
  contact sheet looked like fills and signage were broken. An op
  added to HeroImage.gd must be added to preview_hero.py the same
  day, or every review after that lies.
- **Compress noise so gradients read as geography.** The Act 2
  planner map's FBM at full amplitude dissolved the authored
  landform (channel west / flats south / rise east) into blobs.
  `elev = n * 0.55 + 0.22` under the same positional gradients
  made it a place again. When noise fights composition, scale the
  noise, not the composition.
- **Texture per band, post-process per band-field.** The map keeps
  a PackedInt32Array of un-dithered band ids alongside the dithered
  pixels; shoreline shimmer and contour lines trace the band field,
  not the pixels — otherwise every dithered edge sprouts outlines.

### 2026-07-10 · pass 12 · FeyPortrait v2 + catalog-wide StickTheme

- **Upgrade a procedural generator without breaking identity: keep
  the bit layout.** FeyPortrait v2 (32×40 → 40×50, rounded head,
  shoulders + garment, dithered court aura, almond eyes with
  highlight, real horns/antlers/petal-ears) reads every trait from
  the SAME seed bit ranges as v1 — so every fey keeps its head
  shape, eye spread, mouth, and hair style through the quality
  jump. Faces upgraded; identities preserved.
- **Chrome themes scale by host, not by button.** StickTheme now
  has one preset per studio (9 total) and every one of the 15
  hosts applies its own after SlowstickLook — mirroring the look
  preset name exactly. ~200 stock-gray buttons across the catalog
  became studio chrome with 15 one-line edits. Godot Theme
  cascade is the multiplier; never style buttons inline in a
  stick again.

### 2026-07-10 · graphics passes 5-7 · procedural tier reaches cards and VN busts

- **The FeyPortrait third tier is now house-wide.** GauntletCardFace
  (card sigils from card-id hash) and VnBustPortrait (VN placeholder
  busts from char-key hash) both follow it: authored art wins if
  present, procedural face otherwise, blank chrome never. Any new
  "N things need faces" problem starts from this pattern.
- **At 30px, draw features as solid blocks, not speckle.** The first
  bust draft used corner-dot glasses, hash-speckled beards, and 75%
  curly hair — all three read as noise or damage. Full lens rings,
  a solid chin block, and 88% curl density fixed them. Dither and
  speckle are texture tools for SURFACES; facial features need
  silhouette.
- **Debug chrome defaults OFF in the reading experience.** CharLayer
  shipped with DEBUG_ASSET_OVERLAY=true — a file-path bar stamped on
  every VN portrait. Any debug overlay added to a play surface gets
  a const that ships false, same ethos as the F4 rule.
- **When a fallback path is broken, nobody reports it.** The
  placeholder expression-update branch read wrapper.get_child(0) —
  the static backdrop, not the placeholder — so placeholder faces
  never changed expression and no one noticed for weeks. Fallback
  tiers need the same eyes-on testing as the primary path.

### 2026-07-10 · pass 14 · FeyPortrait species — the strange and non-humanoid

- **Classify from the data you already have.** `true_form` in
  feys.json carries every fey's real shape; a ~40-id override map
  plus a keyword fallback (wing/wolf/moss/mermaid/ghost…) sorts all
  101 feys into 13 body plans with zero new data. 54 now render
  non-humanoid. When a catalog field describes appearance, the
  generator should read it — don't invent a parallel tag.
- **Two-lane species architecture: full painters vs modifiers.**
  Six truly inhuman plans (wisp, formless, swarm, abomination,
  insect, triad) branch before the face pipeline and paint from
  scratch inside the shared aura/frame/pips. Six others (beast,
  treefolk, aquatic, winged, wraith, bullhead) run the WHOLE
  humanoid pipeline first, then repaint over it with the head
  geometry passed in a ctx dict — hair color becomes fur, garment
  becomes bark, and the hash identity survives the transformation.
- **Dark-on-dark needs a backlight, not a brighter subject.** The
  sluagh swarm (near-black bodies on the unseelie night palette)
  was invisible until a dithered moon disc went BEHIND the flock —
  silhouette against light beats lightening the thing itself. Same
  move as the treefolk's lit knot-eyes and the wraith's burning
  eyes: one bright anchor makes a dark design legible.
- **Paint behind an existing figure by testing what you overwrite.**
  Moth wings only write where the pixel still equals bg or aura, so
  they slot behind head and hair with no z-buffer. Cheap and exact
  at this resolution.
- **The Python mirror now lives in the repo.** Losing the scratchpad
  mirror between sessions meant rewriting ~400 lines to preview one
  change. `godot/tools/sprites/preview_fey_portrait.py` mirrors
  FeyPortrait.gd (djb2 String.hash, int64 wraparound hash, exact
  paint order) and must be edited in lockstep with it.

### 2026-07-10 · pass 15 · Sisters Wyrd hexes + witch seats · Earthman boss plates

- **When a design doc promises a picture, the flat fill is a bug.**
  The Wyrd design doc says hexes are "terrain-inked like cover art,
  not like a wargame" — the crawl shipped with draw_colored_polygon
  fills. WyrdHexArt.gd now paints a deterministic 40×46 tile per
  (terrain, address hash): dust wind-streaks, half-buried ribs,
  sage clumps, dusk buttes, cracked salt pan, gallows wood with the
  rope, township rooflines. Same address, same picture, forever —
  the loom does not change its mind.
- **Hex tiles are just masked rectangles.** Paint the full canvas,
  then transparent-out everything failing a point-in-hexagon test,
  upscale nearest to the on-screen hex size, draw_texture at
  center − half-size, and keep the runtime polyline border on top.
  No polygon UVs, no shader.
- **Terrain labels need a contrast rule the moment terrain becomes
  art.** Ink text was invisible on the dark mesa/gallows tiles —
  any label drawn OVER generated art picks its color from the art's
  value range, not from the palette's default.
- **The dealing screens deserve the cover painting.** Each witch
  seat's PARLEY/DRAW/UNWEAVE screen now opens with a 160×72
  authored HeroImage of the arrival text's image (snow falling up,
  the three-shadowed dawn, the drought house, the patient gallows) —
  the arrival prose and the picture are the same sentence twice.
  Boss fights got the same treatment (three Earthman combat
  plates). Fix caught in preview: the east seat's three shadows
  read as propeller blades until thinned to 4px bases.
- **One shared palette per stick, indexed the same in every JSON.**
  All four seat heroes share one 12-color paperback-inks palette;
  all three boss plates share one 11-color instrument palette —
  authored images inherit palette discipline from the studio, not
  per-image whim.

### 2026-07-10 · pass 16 · EarthmanPortrait · species-driven NPC faces

- **The species IS the silhouette.** EarthmanPortrait draws five
  body plans from the design doc's own adjectives: humans get 1940s
  side-parts and ties; Kyrindi are taller-than-the-frame-expects
  with silver collars and a throat sigil; Delvanni read four-armed
  through a SECOND shoulder line below the first (a bust can't show
  arms — show where they attach); Kelait sit small and low in the
  frame under hoods; the Scarlet Woman is bone-white inside a
  dithered red glow. Nobody needs a label to tell a Kyrindi from a
  Delvanni at 48px.
- **Named specials ride on top of hash traits.** jack gets goggles
  pushed up, rocha gets full-ring glasses and the blue pen,
  yr_kelait_child renders smaller and bare-headed. One `pid ==`
  check each — the hash still drives everything else, so the
  specials survive palette or trait changes for free.
- **Same-species crowds need second-order variation.** The first
  Delvanni draft made six warriors identical but for skin tone.
  Topknot bit, war-paint bit, kept-scar bit, tusk length, and three
  garment hues fixed it — when a species has more than three cast
  members, budget at least three independent variation bits beyond
  the palette.
- **Portrait surfaces were already waiting.** The Codex NPC tab
  (rows keyed by npcs.json ids WITH a species field) and the hub
  party strip wired in with ~30 lines each — data-driven UI that
  lists people is a portrait surface the moment a generator exists.
  Mirror lives at godot/tools/sprites/preview_earthman_portrait.py,
  lockstep rule as with FeyPortrait.

## TEMPLATE — new lesson entry

```
### YYYY-MM-DD · short session title

- **Punchy lesson, present tense.** Two-to-four sentences.
- **Next lesson.** Same shape.
```
