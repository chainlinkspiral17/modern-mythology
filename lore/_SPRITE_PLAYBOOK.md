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

### 2026-07-16 · VnBustPortrait v2 — 60x64 busts, ramps, blink

- **Doubling the bust canvas (30x32 → 60x64, 5x upscale into the same
  300x320 slot) is where the quality lives.** Real eyes (lash line /
  sclera / 2x2 iris / pupil / 1px catchlight), a proper nose bridge,
  lip color under the mouth line, stepped-corner head. Same hash
  determinism, same _OVERRIDES contract — every override written for
  v1 carries over unchanged.
- **Bake the shading ramp at draw time, not as a repaint pass.** The
  head block picks its column color while drawing (x<=21 shadow,
  x>=38 rim light); repainting-by-color-compare is fragile in
  GDScript float colors. Hair gets strand texture + rim light via a
  single _hair_px helper; skin-compare is only used for the beard
  edge (approx compare, 0.02 tolerance).
- **Prototype pixel layouts in Python, eyeball a contact sheet, THEN
  port.** bust_v2.py (scratchpad) rendered 8 characters x 6
  expressions; three bugs (sparse afro, mangy beards, hash-bald
  Graciela) were caught on the sheet instead of on the Deck. The
  playbook rule "author blind, verify headless" applies to sprites
  exactly as it does to GLBs.
- **Blink is a frame parameter, not an animation system.**
  texture(key, expr, accent, frame="open"|"blink") — both frames
  cache like any expression; CharLayer swaps the TextureRect texture
  for 0.12s every 2-5s from _process with per-portrait metadata. The
  4th arg defaults, so every existing 3-arg caller (Community
  Planned board) keeps working untouched.
- **Pin characters the hash gets WRONG, not just the leads.** The
  hash made Graciela (71, abuela) bald and bearded. Any named
  character who appears more than once deserves an _OVERRIDES line —
  it's one dict entry.

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

### 2026-07-10 · pass 17 · EarthmanPortrait v2 · divorce the grammar, not the palette

- **Two portrait generators in one house must differ in GRAMMAR,
  not palette.** User feedback: Earthman portraits read "too
  similar to Fey Faire" — both were centered busts inside a
  radial dither aura with an ornamental frame and flat symmetric
  light. Recoloring would not have fixed that. The fix was five
  grammar swaps: graticule grid instead of radial aura · open
  registration brackets + calibration ticks instead of a closed
  frame · a spectral ID stamp (six seed-colored code bars — the
  machine's name for the subject) · tight dossier crops (heads
  ~30% bigger, shoulders clipped by the plate edge) · one HARD key
  light from the right, amber-warmed, which is the deliberate
  inversion of the fey busts' dark right side.
- **Pick one light direction per art system and write it down.**
  Fey: flat frontal, shadow falls right. Earthman: keyed from the
  right, shadow falls left. Once stated, every painter (head,
  neck, shoulders, second Delvanni shoulder pair) obeys it, and
  the two systems can never be mistaken for each other in a
  screenshot.
- **Instrument chrome earns background alignment.** The graticule
  meridian sits at the portrait eye-line (y 17), so every subject
  reads as measured by the plate — a composition idea that costs
  one row of pixels.
- **A light SHAFT is not an aura.** The Scarlet Woman's radial
  glow was fey language; a hard-edged vertical shaft with three
  dither bands reads as stage light from elsewhere — same budget,
  different theology.

### 2026-07-10 · pass 18 · EarthmanPortrait facial depth

- **A hair BLOCK reads as a hat; a hair SILHOUETTE reads as a
  haircut.** Full-width hair rows made every human look capped.
  Splitting the cut into a full band up top and a narrowed crown
  below (bare temples) plus 2px ears at eye height turned the same
  budget into a 1940s short-back-and-sides.
- **Brow bands read as hat brims; brow LEDGES read as brows.** The
  Delvanni's full-width double band became two 5px ledges, one
  over each eye socket, with a socket-shade row beneath — the
  heavy-browed read survived, the hat read died.
- **Depth at this size is four pixels: ear, cheek shadow, socket
  shade, lip catch-light.** Each placed to obey the declared key
  light (ears lit on the key side, cheek hollow on the off side).
  Cheap, and the faces stop being flat decals.

### 2026-07-10 · pass 19 · EarthmanPortrait v3 · profiles — change the POSE, not the chrome

- **If two art systems still look alike after a chrome pass, the
  SUBJECT is the problem.** Pass 17 swapped frame/aura/lighting and
  the user still said "nope, too similar" — because both generators
  drew the same doll: a front-facing symmetric bust. The fix that
  finally landed was drawing SIDE PROFILES. Pose is a bigger
  differentiator than any amount of chrome, palette, or lighting.
- **Profiles put the species in the silhouette.** A shared
  build_profile(spec) walks rows computing the face line (crown
  slope → forehead → brow jut → socket recess → nose wedge → lip
  notch → chin recede) and back-of-skull line (crown rounding, jaw
  slope). Species are just parameter sets: the Kyrindi's bx runs
  nearly to the plate edge (the long backswept cranium), the
  Delvanni gets a brow shelf, a barely-receding jaw and a tusk
  jutting past the lip IN SILHOUETTE, the Kelait is a small hooded
  curve, the human is a straight nose under a 1940s cut.
- **One parametric profile engine beats five hand-drawn heads.**
  Hash traits (nose length, skull depth, crest vs braid, topknot,
  war-paint, scar) and named specials (rocha's lens-ring + arm to
  the ear) all ride on the same spec dictionary.
- **Face the key light.** Profiles all look right, into the
  declared key — the lit face edge is the brightest line in the
  plate, which is what an instrument photographing a specimen
  would do.

### 2026-07-10 · pass 20 · EarthmanPortrait v4 · figures in scenes, not faces in frames

- **The user's reference boards settled a three-pass argument.**
  Frontal busts (too similar to Fey), chrome swaps (still too
  similar), and profiles (distinct but ugly) all failed because
  they were all FACE-DRAWING at 40px. The references — a cloaked
  figure at a campfire, a swordsman before a tower, a gunslinger
  whose face is just shadow under a hat — showed the actual craft:
  at this scale identity is COSTUME + POSE + HEIGHT, and the face
  is a glint. v4 draws full figures standing in a dithered Parsan
  dusk. This is the keeper.
- **Height inside a fixed frame is free characterization.** One
  36×60 plate, five species heights: the Delvanni fills it, the
  Kyrindi is a tall slender column, the human is mid, the Kelait
  is a small cone, the child Yr smaller still. No other trait
  reads faster.
- **Full figures unlock what busts never could.** The Delvanni's
  four arms are finally VISIBLE (two crossed, two hanging, bare
  rust skin against armor); the Scarlet Woman floats — no contact
  shadow, warm light cast DOWN onto the dust instead.
- **When a face is three pixels, spend them on shadow and one
  glint.** Eye-shadow px + lit-side skin px beats any attempt at
  eyes/nose/mouth. Kelait faces are two cream pixels inside a
  hood's darkness — the most legible faces on the sheet.
- **Ask for reference images sooner.** Three rejected passes
  preceded the boards that resolved the direction in one.

### 2026-07-10 · pass 21 · plate refinement · what "blocky" actually means

- **"Blocky" = rectangles + three flat tones. The fix is a ramp
  and a silhouette, not more pixels.** Same 36×60 canvas, same
  composition — the refinement was: a 5-value material ramp with
  Bayer-dithered transitions (deep shadow / mid / core /
  half-light / warm rim) applied per ROW via one shared
  _shaded_row() helper; sloped shoulders (width grows over two
  rows); tapered legs; rounded crowns (top row inset); robe hems
  that jitter ±1px; and _folds() — broken vertical fold lines
  inside every garment. Nothing is a naked rectangle anymore.
- **Background depth is three silhouettes and some speckle.** Two
  distant flat-topped buttes behind the horizon, a 7-stop sky
  instead of 5, ridge highlights with a shadow row under them,
  and two-tone ground speckle. The plate went from backdrop to
  place.
- **Put the ramp in ONE helper.** Every garment, boot, and head
  row goes through _shaded_row(), so the whole cast rounds and
  warms consistently — and future tuning is one function.

### 2026-07-10 · pass 22 · WyrdFigureArt · the drifter and the four sisters

- **A proven render language ports across sticks in one sitting.**
  The Earthman plate technique (_shaded_row 5-value ramp, _folds,
  dust-strip grounding, organic tapers) moved into WyrdFigureArt
  wholesale — only the palette (paperback inks) and the subjects
  changed. When a technique survives one stick's feedback cycle,
  copy the helpers, not the lessons.
- **The map marker is a character slot.** The crawl's player dot
  (draw_circle ×2) became the drifter — hat, shadowed face, flared
  duster, iron glint — drawn native-size on the current hex. The
  cheapest high-impact wire-in yet: one draw_texture call visible
  through 100% of gameplay.
- **Transparent-background figures with a dust strip composite
  anywhere.** Unlike the Earthman plates (self-contained scenes),
  the Wyrd figures carry only a dithered ground strip, so the same
  texture works on the title, the seat screens, and the map.
- **Each sister's figure quotes her arrival text.** North holds
  the net with snow rising; east stands in the arrested dawn with
  three shadows on her strip and the face-down mirror; south rocks
  with the offered water glinting real; west wears the only violet
  in the game at her collar. Prose and picture, same sentence —
  the seat-strip rule from pass 15, now at figure scale.

### 2026-07-10 · pass 23 · human bones · "they don't look human"

- **Figures need a skeleton before a costume.** The first Wyrd
  figures were cones with peg heads — dresses starting at the
  chin, no necks, no shoulders, single-pixel eyes. The fix is a
  small set of bone helpers used by every humanoid: _head6 (a
  rounded 5×6 head, TWO eyes, a mouth hint), _neck_shoulders (a
  neck row, shoulders sloping to ~two head-widths), _bodice
  (fitted torso tapering to a WAIST), _arm (upper arm, elbow,
  forearm, hand). Skirts flare from the waist, never from the
  neck. Costume drapes over the bones, not instead of them.
- **Two eyes is the humanity threshold.** Every figure that read
  as "not human" had one eye pixel or an eye-shadow smear. Two
  dark pixels at (cx−1, cx+1) on a 5px face, plus a mouth pixel,
  flips the read instantly — cheaper than any silhouette work.
  Applied across Earthman too (humans, Kyrindi, Delvanni got
  matched tusks + both deep-set eyes, the Scarlet Woman).
- **The drifter's face is shadow AND jaw.** All-shadow under the
  hat read as headless; two shadow rows with a LIT JAW row beneath
  keeps the mystery and the humanity both.

### 2026-07-13 · pass 24 · Earthman SHINE · HD-divergent hero plates

User direction: "abstract and early computer art, but really make some
corners shine · essentially HD computer art from a more advanced
technology, divergent artistically" + "art can ring the outside of the
bounds." Four Earthman hero plates rebuilt from the flat 20-26-layer
baseline to 159-212 layers each, in the Astro-Cortex house style. Beats
chosen for highest drama × weakest existing art: parsa_awakening (Ch2, the
self-labelled "money shot"), mines_lantern (Ch4 vista), academy_gate (Ch5
pivot, the flattest at 20 layers), and a NEW the_working (Ch5 Working VII
rite, which had no art at all). Generator: scratchpad
gen_earthman_shine.py (deterministic, JSON committed, generator not);
previewed through preview_hero.py.

- **"HD from more capable hardware, divergent art" = density + confident
  colour, NOT a bigger canvas.** Kept native 160×90 (playbook: flatness
  comes from fills, not resolution) and reached the HD read with 20-colour
  local palettes, multi-stop dithered vgrad skies/sands, layered
  foreground/mid/far silhouettes with lit rims, radial glows, and ~10×
  the primitive count. Upscaled to the same 220×124 slot the baseline
  used — no scene-layout change, no aspect risk.
- **"Ring the outside" belongs IN the plate, as the studio's grammar.**
  A shared register_frame() helper draws an Astro-Cortex instrument bezel
  on every plate: double outline rule, corner register brackets,
  calibration ticks, a faint dashed graticule meridian + centre reticle,
  and a 3×5 corner designation ("PARSA / 02 DAWN", "THE WORK / VII"). It
  frames the art AND carries the "precision-instrument glass" preset —
  one helper makes four heroes read as one instrument's output.
- **A full graticule GRID cages the art; a meridian CROSS measures it.**
  First draft ruled the whole interior every 12px — read as a grid over
  the picture. Two dashed centre axes + a small centre reticle give the
  same "the machine is aiming at the subject" read without fighting the
  composition. Same lesson as the portrait passes: instrument chrome
  should align to the subject, not tile the frame.
- **shade over empty dark reads as a hard rectangle — the moon/pool
  trap, again.** parsa's dying moon (a 36×36 gold shade cloud) and mines'
  lantern pool (a 74×48 orange shade rect) both boxed up. Fixes: the moon
  became disks only (halo/body/core/maria/limb); the light pool became
  four CENTRED stepped squares of rising amount on softer amber, which
  reads round. Reserve `shade` for laying texture over EXISTING art;
  never to conjure a soft shape out of flat dark.
- **Swap the hero plate per-beat when the picture is a sentence in the
  script.** Ch5 shows academy_gate normally but swaps to the_working
  during the Working VII/IX beats (content-based detection on the beat's
  speaker/text, so it survives reordering). Both textures pre-load in
  _build_frame; either may be null and the swap degrades to whatever
  loaded — fallback discipline intact. This is cheaper than a
  _show_hero overlay when a chapter already owns a static plate slot:
  one TextureRect, two cached textures, one swap call in the beat render.

## TEMPLATE — new lesson entry

```
### YYYY-MM-DD · short session title

- **Punchy lesson, present tense.** Two-to-four sentences.
- **Next lesson.** Same shape.
```
