# 3D Modeling Playbook · Modern Mythology

A working record of what we've learned about building this project's
locales in Blender → glTF → Godot. Refresh this file after every
significant modeling session — add the new rules in the
"Recent lessons" section at the bottom, and graduate stable rules up
to the "Core rules" section over time.

## How to use it

Before starting any new 3D modeling work, read the Core rules and the
last two "Recent lessons" entries. They will save you from re-making
mistakes that took specific user feedback to discover.

## STOP RULE — "I'm not seeing improvements" means the pipeline is broken, not the work

**The single most important rule in this file.** If the user says any
form of "I don't see changes," "no improvements visible," "looks the
same," "this isn't working" — and you have committed work that
should be visible — **stop adding features immediately**. The default
hypothesis is NOT "user needs more features." The default hypothesis
IS "the user's GLB is stale because the build silently failed."

Verify in this order, before writing another line of build code:

1. Run a stubbed-bpy smoke test of the full `main()` to surface any
   `UnboundLocalError`, `TypeError`, missing-kwarg, or
   forward-reference bugs. `ast.parse()` does NOT catch these —
   Python only resolves them at runtime. The test below catches them:

   ```python
   class _Anything:
       def __getattr__(self, k): return _Anything()
       def __setattr__(self, k, v): pass
       def __getitem__(self, k): return _Anything()
       def __setitem__(self, k, v): pass
       def __call__(self, *a, **k): return _Anything()
       def __iter__(self): return iter([])
       def __contains__(self, k): return True
       def __bool__(self): return True
       def __float__(self): return 0.0
       def __int__(self): return 0
       def __len__(self): return 0
   class _Bpy:
       def __getattr__(self, k): return _Anything()
   sys.modules['bpy'] = _Bpy()
   # ... load module and call main()
   ```

2. Ask the user to paste the BLENDER OUTPUT of their build, not
   just to rebuild. Blender's `--background --python` prints any
   Python traceback right before "Blender quit" and the wrapper
   script does NOT exit non-zero on this (Blender's exit code is
   0 even with a script error). If the GLB timestamp doesn't
   advance, the build crashed; the traceback is in stdout.

3. Only AFTER 1 and 2 come back clean do you add more features.

This rule exists because I just spent ~30 commits adding per-house
detail / civil-engineering / park furniture / commercial-rooftop
mech that NEVER GOT BUILT — every rebuild crashed in
`_build_kwik_shop_strip` on an `UnboundLocalError` for `sw_y`
(forward reference: the trash bin block referenced a variable
defined 290 lines later in the same function). The user said
"I am not seeing improvements" multiple times in different words
before I finally ran the diagnostic and saw the traceback. That's
the EXACT failure mode the existing river-sink rule warned about,
and I made it anyway.

**Take "I don't see changes" as a hard signal to verify the
pipeline, not as encouragement to keep grinding.**

### Visual evidence is a HARD STOP

When the user provides a screenshot or video, weight that even
higher than verbal feedback. Screenshots are ground truth: they
prove exactly what the build produced at a specific moment.

If the user uploads a screenshot AND says "I'm not seeing
improvements" — that combination is not a request to add more,
it is a bug report against the build pipeline. Do NOT respond
by listing what should be visible or by adding more features.
Respond by:

1. Examining the screenshot carefully — what IS rendered? Is it
   consistent with the OLD GLB (pre-your-changes) or the NEW one?
2. Running the stubbed-bpy smoke test against `main()`.
3. Asking the user for the Blender build output so you can read
   the traceback.

The user is not your QA dept. When they hand you visual proof
of a problem, you owe them a diagnosis, not a longer feature
list.

Smoke-test cadence: run the stubbed-bpy main() at least once per
session, ideally after every commit that touches a `build_*` or
helper that's reached from main(). It's a 2-second check that
catches what `ast.parse()` can't.

## Core rules

### Infrastructure placement — align to a working grid

Every locale's signage, utility, and street furniture follows the
SAME placement discipline a real town planner would use. Players read
"this place is laid out by humans" or "this is a video-game blob"
within the first second — and the difference is almost entirely
this:

**Public right-of-way (roads, sidewalks, intersections):**
- Only the most essential public utilities — stop signs, traffic
  signals, hydrants, manhole covers, mailboxes, public lampposts.
- Streetlights and utility poles sit at the EDGE of the road on
  the buffer strip, NEVER in the road surface itself.
- Sidewalks belong to pedestrians; nothing planted in them except
  saplings and the utility access listed above.

**Private / commercial property:**
- All advertising signs (pole signs, marquees, monument signs)
  live on the owner's land — set back from the sidewalk by the
  buffer strip, but clearly on commercial ground.
- Parking-lot signs sit at the lot's road-facing corner, on
  commercial property, panel facing the road.
- Landscape grove / hedges / planters owned by the business sit
  on the business's lot, often as a buffer between parking and
  the public sidewalk.

**Cross-check rule** when placing anything new in a build script:
- Is `obj_x` between the road centerline and the sidewalk's outer
  edge? → only public infrastructure goes here.
- Is `obj_x` further out than the sidewalk's outer edge? → it's on
  someone's property; pick the right owner and put it there.
- Is `obj_x` in the middle of the road? → never, full stop.

Riverfront-specific anchors (Blender frame; remap to Godot at
runtime):

| Element                       | X            | Y          |
|-------------------------------|--------------|------------|
| Road centerline (FRONTAGE_X)  | -55          | varies     |
| Road surface edge (W/E)       | -55 ± 6      | varies     |
| Sidewalk outer edge           | -55 ± 8      | varies     |
| Commercial property starts    | -55 ± 9      | varies     |
| D'Ambrosio's parking lot      | x ∈ [-41, -19], y ∈ [-18, +18] | |
| D'Ambrosio's pole sign        | lot_cx - lot_x_w/2 + 1.0 | lot_cy - lot_y_l/2 + 2.0 |

Don't relocate a sign onto the road shoulder just because it makes
a composition look good — break the rule visibly enough and the
locale stops feeling like a place.

### Coordinate frame — Blender Z-up vs Godot Y-up (MUST READ)

**Same units (meters), different up-axis.** The build scripts use
Blender's native Z-up convention; the Godot runtime uses Y-up. The
default glTF exporter remaps on the way out:

| Blender axis (build script) | Godot world axis (runtime) |
|------------------------------|----------------------------|
| `+X` (east)                  | `+X` (east)                |
| `+Y` (north / forward)       | `-Z`                       |
| `+Z` (up)                    | `+Y` (up)                  |

A Blender position `(x_b, y_b, z_b)` lands in Godot world at
`(x_b, z_b, -y_b)`. A Blender direction vector remaps the same way.

**Scale is consistent — 1 unit = 1 meter in BOTH runtimes.** Do not
introduce scale factors in either; if something looks the wrong
size, find the bad number, don't compensate via transform.

**Implications for cross-runtime code** (e.g. `LocaleSetup.gd`
positioning Label3D nodes on panel meshes baked from the build
script):

- Mesh AABBs in the imported GLB are in Godot world coordinates.
  `panel.global_transform.origin + panel.get_aabb().get_center()`
  gives the correct world position with no manual remap.
- But ANY hand-written direction or offset vector (face normals,
  push-out offsets) in runtime code MUST be in Godot frame. A panel
  the build script faces toward Blender +Y faces toward Godot -Z at
  runtime — be explicit. (Bug we hit twice: passing Blender-frame
  face normals into Label3D basis builders. Symptom: text rotated
  90° around the panel's face axis. Fix: write face normals in Godot
  frame and use `world_up = Vector3(0, 1, 0)`.)
- For sanity-checks: a 1.7 m player capsule, a 12 m wide boat, a
  2 m tall sign panel — these dimensions read identically in both
  runtimes. If a measurement is off, the bug is in the build, not
  in the conversion.

**If you find yourself doing the remap by hand often**, add a
helper to LocaleSetup like:

```gdscript
func blender_to_godot(v: Vector3) -> Vector3:
    return Vector3(v.x, v.z, -v.y)
```

and document where it's used. **Do not** scale, only remap axes.

### Primitive selection — never reach for `make_box` first

The project's lowpoly aesthetic looks like Atari 2600 if everything is
axis-aligned boxes. Pick the right primitive for the shape:

| Shape                      | Use                          | Don't use                   |
|----------------------------|------------------------------|-----------------------------|
| Cloud, foliage canopy      | `make_sphere` clusters       | stacked `make_box`          |
| Lifebuoy, ring, halo       | `make_torus`                 | 12-segment box loop         |
| Smokestack, pole, column   | `make_cyl` (segments ≥ 8)    | tall thin box               |
| Sloped roof, lamp shade    | `make_prism`                 | stacked boxes               |
| Ramp, gangway, slope       | `make_ramp`                  | rotated box, stacked boxes  |
| Diagonal line, neon stroke | `make_tube_segment`          | axis-aligned box (stair-steps!) |
| Rounded car body           | `make_box` slab tiers OK     | (acceptable here)           |
| Trunk, branch, pipe        | `make_cyl` or `make_tube_segment` | thin box           |

If a shape needs a diagonal, curved, or organic edge, **do not** use
`make_box`. Reach for the right helper.

### Shaders are at screen level only

All visual effects come from the screen-space CanvasLayer post-process
stack. **Do not** assign per-mesh shaders to locale geometry — use
`StandardMaterial3D` with `vertex_color_use_as_albedo = true` and let
the screen shaders carry the look. LocaleSetup defaults to this and
should not be changed.

Active post-process stack (in render order):
1. **`ascii_render.gdshader`** — samples each cell of the screen and
   renders one of 10 ASCII glyphs based on luminance. The substrate
   look. Strength driven by MoodCycler per mood.
2. **`demoscene_post.gdshader`** — palette quantize, Bayer dither,
   scanlines, chromatic aberration.

Old shaders (`ascii_edges`, `glyph_field`) exist on disk but are no
longer wired into scenes. The "edges + drifting glyph field" approach
produces snow, not a working effect — do not bring them back.

### Reference proportions (Mississippi steamboat / dock / river)

Real proportions our build keys off of (Belle of Louisville, Natchez
IX). When you see something looking small or wrong, suspect scale:

| Element            | Real reference  | Our build (current) |
|--------------------|-----------------|---------------------|
| Boat length        | 58–80 m         | 24 m (under)        |
| Boat beam          | 12 m            | 12 m                |
| Boat height        | 12–15 m         | ~14 m               |
| Paddle wheel diam. | 6 m             | 4.8 m               |
| Dock above water   | 0.3–0.5 m       | 0.35 m              |
| Pilings proud      | 0.3–0.6 m       | 0.50 m              |
| River width        | 100–200 m       | ~80 m clear lane    |

### Layout — port vs starboard

Boat bow at +Y (north / upriver), stern at -Y (paddle wheel here).
Port = -X side, faces the dock and parking lot.
Starboard = +X side, faces the open river and the opposite shore.
**Never** put the dock at the same end as the paddle wheel.
**Never** put dock + parking lot on the same side as the open river.

### Dock above the waterline

The dock deck MUST sit visibly above `RIVER_LEVEL_Z` (use `DOCK_Z`
constant). Pilings run from below the riverbed UP THROUGH the deck
and stand 30–60 cm proud with darker caps. Gangway from boat to dock
slopes via `make_ramp` (real gangways are 15–25° pitched, never flat).
Ramp from dock to land at the other end.

### Bayou navigability

Bayou foliage must leave a navigable channel down the center wide
enough for a riverboat or two to pass. With `BAYOU_X = 55`, no cypress
should be placed at `|x - BAYOU_X| < CHANNEL_HALF + jitter`. Tree
placement uses Poisson-style rejection sampling with min-distance,
not a hand-typed grid.

### Tree species diversity

A locale's foliage must use multiple species with **randomized scale
0.7–1.4**. Don't paste the same tree builder 26 times. The bayou uses
5 species (bald cypress, water tupelo, live oak, palmetto, dead snag)
with a weighted random selector. Opposite shore uses 3 (cypress,
pine, oak).

### Sign mirroring for two-sided neon

For a sign that reads correctly from both faces, the mirror function
is `lx(local_x) = -local_x * face_sign`. **Both** the negation and
the face_sign multiplication are required — neither alone gives
correct text on both sides.

### Sign neon halos go BEHIND letters

Halo spheres inset toward the panel face (`face_y_off - offset *
face_sign`), never out in front. Halos in front occlude the letters
themselves and look like floating red dots.

### Underline arc geometry

For a "swoosh" underline below the baseline, use parametric points
with `z = baseline - sin(t * π) * dip` — do NOT use an `add_arc`
with a large radius and theta near π/0, which produces an arc that
peaks ABOVE the letters instead of below.

### Build script structure

- Helpers at top: `clear_scene`, `make_box`, `make_cyl`,
  `make_sphere`, `make_torus`, `make_tube_segment`, `make_prism`,
  `make_ramp`, `_finalize_mesh`.
- Constants below helpers: layout positions (`PARKING_X`, `BAYOU_X`,
  `OPPOSITE_X`, `DOCK_Z`, etc.).
- One `build_<region>()` function per logical area.
- `export_glb()` at the bottom using the version-safe RNA probe
  for `export_colors`/`export_normals`, `export_lights=False`,
  `export_cameras=False`.

### Blender export quirks

- `export_apply=True` bakes rotations into mesh vertex positions
  (important — the GLB doesn't carry Blender object rotations).
- `export_colors` and `export_normals` are flags that may or may not
  exist depending on Blender version. Use the RNA probe pattern.
- Cameras are NEVER exported — they hijack Godot's active camera.
- Lights are NEVER exported — set up real `Light3D` nodes in the
  `.tscn` instead.

### Use references, not memory

When modeling something real (boat, bridge, building, vehicle), cite
the reference in a code comment ("modeled after the Belle of
Louisville's hurricane-deck proportions"). Don't guess at numbers.

## Recent lessons

### 2026-07-19 · wrong-room sweep CLOSED · seven builds + eight repoints

- **The sweep is done.** vol6's cosmic_comics_back_office reuse went
  29 → 10, and the surviving 10 (ch12/ch21/ch3_back_room/ch4) are
  scenes genuinely SET in Rick's back office. Verified by narrate-
  dump, not by grep. Any future "same room again" complaint in vol6
  starts from a clean slate.
- **A multi-segment scene can need FOUR different rooms.** ch19
  "The Chains" cut drive→porch→Ben's bed→Coach K's bed, all on the
  comic shop. Repoint scripts must assign per-SEGMENT in order, not
  per-file — a single find/replace would have put Coach K in a
  Civic. Sequence-list assignment (seq[i] on each match) is the
  pattern.
- **Dream rooms get dream proportions.** nightmare_cell ships a 3.4m
  ceiling on a 3.4×4.2 floor, a door slightly too small with NO
  inside handle, and a low camera angled UP (+0.183 pitch) — the
  wrongness is composed, not shaded. One caged-tube practical, a
  fill at 0.06, saturation 0.75. Single-source dread needs the pack
  fully clean (nightmare_hum = raw, neon OFF).
- **Emotional-center lighting: build the story's light first.** The
  Henderson porch's entire design brief was "the kitchen light left
  on" — one LITGLASS window among dark ones, with the Omni sitting
  in it at 2.2 while the porch lamp is OFF geometry. When a chapter
  names a light source, that fixture is the hero prop.
- **Deterministic scatter without RNG:** the red-dot wall uses a
  golden-angle spiral (i*2.39996, r=0.085√i) — organic clustering,
  reproducible builds, no random module (which would break the
  rebuild-equality check).
- **Batch donor-transform scales to 7.** One python pass generated
  all seven tscns from five donors (bedrooms←jesse, yard←school
  field, porch←caldwell, gym+cell←stockroom, shed←garage), with the
  same assert suite (1 Environment, exact light count, no donor
  string leaks, fresh uid). Keep picking donors by LOOK.

### 2026-07-19 · wrong-room sweep round 2 · three locales in one pass

- **The audit names lie; the scene text doesn't.** The reuse list
  said "Substation Nine" and "Ben's room" — the actual rooms behind
  those segments were the HENDERSON GARAGE (band practice, 6 segments
  across ch5/ch14/ch20 — Substation Nine is the bill they're playing)
  and the Kowalski BACKYARD. Always dump the narrate lines under each
  reused bg before designing the replacement locale, or you'll build
  the wrong room with full confidence.
- **One GLB, two presets is the cheap win for inside/outside pairs.**
  centro_stockroom carries both the ch18 2AM interior AND the ch10/
  ch16 dock-break exterior: build the apron + bumpers + dock face
  outside the open roll-up, then add a second CAMERA_PRESETS entry
  (`centro_dock`) on the apron looking back at the light spilling
  out. Two rooms of story coverage for one Deck rebuild slot.
- **Generate sibling tscns by transforming an existing one, not by
  hand.** The post-process stack is ~200 lines of boilerplate that
  must stay in exact BackBufferCopy order. A python transform of
  miller_garage.tscn (swap uid / glb path / node name / Environment
  block / light blocks / strata+pack via regex) produced all three
  scenes; assert-check count of Environment blocks, light count, and
  that no donor-name string survives. Pick the DONOR by look: the
  dusk garage donated to a dusk garage (accent colors carry over
  sensibly); darkroom's red-accent shader params would have leaked
  red into every mood of the bookshop.
- **Reuse an existing style pack when the recipe matches.**
  henderson_garage ships `garage_dusk` (built for miller_garage) —
  same dusk-through-open-door recipe, zero new MoodCycler surface.
  Only bindery_day and stockroom_fluorescent were genuinely new.
- **Open-door locales need the outside built.** The garage's
  establishing shot is FROM the driveway; the dock preset is FROM the
  apron. Budget geometry beyond the doorway (driveway + lawn +
  hoop; apron + lane stripes + waiting pallets) or the framing
  vantage stares at void.

### 2026-07-16 · Anny full-body base under the GNM heads

- **naver/anny is the licensed realistic-body answer** (Apache 2.0
  code, CC0 MakeHuman-derived assets in the native topology; PyTorch,
  runs CPU). `gnm_portrait.py` now forwards MakeHuman-style phenotypes
  (gender/age/height/weight/muscle/cupsize — needs
  `all_phenotypes=True`; gender axis: 0=male, 1=female) and welds the
  GNM head on. 13.7k verts, metric, A-pose, height along +Z in its
  native frame → godot (x, z, -y).
- **Its bone names lie about position** — the "head" bone origin sits
  at EYE level, neck03 at the chin. Never cut/anchor by bone position;
  find the neck GEOMETRICALLY (narrowest cross-section band between
  0.80H and 0.93H) and take anchors as fixed drops below that cut.
  A widest-band "shoulder" scan also fails: the spread A-pose arms
  win. Fixed offsets below the neck cut are the reliable anchors.
- **Skinning weights are the garment segmentation** — ARGMAX over
  summed zone-bone weights (torso/upperarm/forearm/hand/legs/feet/
  neck+head) gives every vertex exactly one zone; independent >0.5
  thresholds spike. Then cut CLEAN HORIZONTAL lines (hem/ankle/crew)
  in BOTH directions after decimation, snap nearby verts onto each
  line (real edge loops), and give every triangle ONE color at
  flat-shade time — per-corner colors fringe every boundary.
- **Weld = geometric cut + skin bridge loft**, not radius-matching:
  cut GNM at chin-0.032, cut anny just above its narrowest neck, seat
  with 12mm overlap, and loft a tapered skin tube from the anny neck
  up into the hollow GNM head. Auto-scaling the head to match neck
  radii distorts it — the bridge absorbs the mismatch instead.

### 2026-07-16 · GNM parametric heads → stylized hero portraits

- **Google GNM (github.com/google/GNM, Apache 2.0) works as an
  OFFLINE portrait-face generator for the Portrait3D GLB tier.**
  `godot/tools/portraits/gnm_portrait.py` samples its statistical
  head model with a crc32-seeded identity per character (same
  character = same face, forever), strips interior anatomy, paints
  flat vertex-color zones from GNM's SEMANTIC VERTEX GROUPS (skin /
  lips / scleras / irises / pupils / brow cores / a computed scalp
  mask + offset hair shell), then vertex-cluster-decimates and
  flat-shades. Decimation IS the stylization step — full-res smooth
  GNM is photoreal-adjacent and clashes; 6 mm clustering + flat
  shading lands it in the faceted diorama look.
- **The head rides a procedural anatomical body.** Portrait3D's
  auto-scale expects a ~1.8 m Y-up figure framed thigh-to-head, so a
  bare head won't frame. v1 hex-prism slabs read "too primitive" —
  v2 is LOFTED octagonal cross-sections on real anthropometry:
  sloped trapezius shoulders, chest→waist→hip taper (separate female
  measurement table: narrower shoulders, waist, hip flare), visible
  neck, tapered limbs with elbows/wrists, thigh-thicker-than-calf
  legs. Garment boundaries are crisp because each loft band is its
  own vertex group colored by the LOWER ring — no gradient bleed.
  Wardrobe is data: outfit tables ("waiter" shirt/tie/half-apron,
  "kwikstop" short-sleeve polo + name tag, "bomber" ribbed jacket +
  patches incl. a boxed alien-head) with a front_z(y) interpolator
  so chest dressing follows the torso taper instead of floating.
- **Software-raster previews catch winding bugs before Godot does.**
  The first pass shipped a black-fronted torso (hex prism side quads
  wound inward → lambert 0). The tool's --preview PNG made it obvious
  in seconds. Never write preview PNGs into assets/ — Godot imports
  any PNG it sees; previews default to system temp.
- **Hero GLBs are COMMITTED (not gitignored like locale GLBs),** so
  generated portraits ship on pull with no Deck rebuild. New files go
  in as `<name>_gnm.glb` beside the old art; the CharLayer mapping is
  the switch, so rollback is a two-line revert.
- **GNM is a build-time dep only** — clone it anywhere, pass
  --gnm-path (weights are bundled in its repo, ~53 MB; deps: numpy,
  absl-py, etils[enp], pillow for previews). Nothing of it is
  vendored here and the runtime never sees Python.
- **Lighting rigs key on GLB basename** — Portrait3D now strips a
  `_gnm` suffix before the CHARACTER_LIGHTING lookup so variants
  inherit their character's rig (Sam's sodium Kwik-Stop key).

### 2026-07-15 · killing shared-bed clones + the verify-before-repoint rule

- **One bed model copy-pasted across N rooms reads as one room
  reskinned.** An audit found the exact bed (frame+mattress+pillow+
  headboard at `-ROOM_W/4, ROOM_D/2`, headboard N) byte-identical
  across finn / kai / diego / lena, with maya on the same footprint —
  finn and kai were line-for-line clones. Palette + dressing had been
  varied in an earlier pass; that is NOT enough. Re-arrange the
  SILHOUETTE: change the WALL, the ORIENTATION (rotate 90°), the
  MODEL (platform vs floor futon vs queen-with-footboard vs
  captain's), and the HEIGHT. finn→raised platform on posts w/ under-
  bed crates; kai→floor futon (lowest); diego→NW-corner E–W; lena→
  queen+footboard; maya→under the N window. The ex-clone pair must
  become the two most-different beds, not two shades of the same one.
- **Move the bed → move its satellites.** Each room re-declared
  `bx, by` in `build_dressing` to hang a nightstand/clock off the
  bed; a bed move that forgets this strands the nightstand at the old
  spot. Grep every `bx`/`by`/`nsx` reference, not just `build_bed`.
- **Fixed VN cameras: check the new bed is still in frame.** These
  rooms use a fixed SE-corner cam looking NW. Beds pushed to the N/
  centre land centre-back (good); a floor bed in the SW corner reads
  as foreground (acceptable). If you shove furniture to a wall the cam
  can't see, you've hidden it — reason the vantage before committing.
- **A multi-bg scene on `louisiana_road` is usually a LEGIT exterior→
  interior transition, not a wrong-room bug.** The audit flagged
  ch22_foxhole / ch16_el_rancho as "road standing in for an interior";
  inspection showed they cut road→`foxhole_bar`→stage, road→
  `el_rancho_taqueria` — the road IS the arrival beat. Read the FULL
  bg list of a scene before repointing. The real reuse bugs are
  SINGLE-bg scenes sitting on a generic fallback (the whole beat is
  the wrong room, it never cuts away).
- **Repoint to an EXISTING correct preset before building new.**
  Graciela's ch1 kitchen (892 Ashberry = the Ramos house) sat on
  `cosmic_comics_back_office`; `ramos_kitchen_morning` already exists
  with a built GLB and is the same household. One-line bg swap, right
  room, and — because the GLB ships — it's live on pull with no Deck
  rebuild. Always check the preset table for a real match before
  authoring a whole locale.

### 2026-07-15 · the darkroom — a bespoke locale to kill a shared-bg bug

- **One `3d:` bg reused for two different rooms is a bug the player
  WILL name.** `cosmic_comics_back_office` had become the catch-all
  small-interior fallback for 29 vol6 scenes. Two of them sit
  back-to-back in the ch0 prelude: "Graciela's Bedroom" (892
  Ashberry) and "The Darkroom" (3017 Verbena). Same bg → the user's
  exact words: "the darkroom is the same as graciela's bedroom."
  Fix: build ONE of the confused pair as a bespoke locale and
  repoint just that segment's bg node — they become distinct and the
  complaint dissolves. You don't have to re-home all 29 reuses; you
  have to break the specific collision the player saw.
- **Find the real bg the JSON uses, not the text that MENTIONS it.**
  `grep "darkroom"` matched a dozen scenes that only TALK about the
  darkroom. The scene that's SET there is the one whose `interlude`
  label is "The Darkroom" and whose next `{"t":"bg"}` node names the
  reused preset. Scan `nodes[]` for `t==interlude` (setting label) +
  the following `t==bg` (`src`), not raw substring hits.
- **Red-and-black comes from the tscn, NOT the geometry vertex
  colors.** Give the GLB believable albedo (white enamel trays,
  steel enlarger, amber chemistry, near-white prints, matte-black
  walls) and let darkroom.tscn do the tint: Environment bg near-black
  + deep-red ambient (0.56,0.10,0.08 @0.5) + red fog, and a single
  red practical `OmniLight3D` (1,0.16,0.12 @3.0, range 5.2) sitting
  exactly on the visible `Safelight_Dome` mesh. Paint the walls red
  in vertex color and the red light has nothing left to do; keep them
  black and the safelight reads.
- **Bloom the fixture, don't brighten the room.** Set the safelight
  dome/lens and the enlarger red filter to near-pure red
  (0.90,0.11,0.09) and lean on the env glow (hdr_threshold 0.85,
  intensity 0.85) so those small parts halo. That sells "the only
  light in here is red" without raising the ambient floor.
- **Small room ⇒ mood must be clean, never a heavy filter.** The
  darkroom ships `default_style_pack = "darkroom_safelight"` (mood
  `raw`, lighting `scene_default`, blend_mode 0 = neon fully OFF) and
  a `mood_strata` of safe moods only. A neon/linework mood over a dim
  red set is the wireframe-nightmare failure again — the post-process
  must stay out of the way and let the practical carry it.
- **Cross-runtime camera math held.** SE-corner vantage: cam blender
  (1.05, 0.5) inside the light-tight door, target the enlarger at
  blender (-0.3, 3.4); godot yaw = atan2(cam_x-tgt_x, cam_z-tgt_z) ≈
  24.5°, pitch ~-6°. Wet trays land frame-left, enlarger centre-back,
  drying line overhead — all in one 64° frame in a 2.6×3.4 room.
- **New `.py` locale = Deck rebuild before it shows.** darkroom.glb
  is gitignored; until `build_scenes.sh` runs on the Deck the bg3d
  preset's `requires_glb` misses and the scene falls back to 2D
  black — WORSE than the reuse it replaced. Always ship the repoint
  and the rebuild command together.

### 2026-07-11 · compound-silhouette detail passes, headless-verified

- **"Not just boxes" is achievable in this pipeline.** A prop reads
  as a THING when it's 4-10 primitives with silhouette variety and
  per-part color: tripod = splayed leg cylinders + hub + body box +
  lens cylinder + glass disc; kudzu = wandering stem-cylinder chain
  + leaf-cluster spheres; gantry hoist = beam + trolley + chain of
  alternating-axis small cylinders + three-box hook. Single-box
  props are placeholders, not set dressing.
- **Author blind, verify headless.** godot/tools/blender/survey.py
  executes any build script with a stubbed bpy (AABB dump, top-down
  maps, spatial queries) and the scratchpad check_shots.py
  ray-marches every VN camera through the result. New dressing is
  only committed after the checker shows no camera-inside-object
  and no blocked hero shot. This is how detail passes ship without
  a Blender render loop.
- **A window is a wall segment, rebuilt in bands.** The booth row's
  river view (pass 5): replace the one solid segment box with lower
  band + glass band in mullioned bays + upper band + sill/header
  trim. The tscn collision wall stays untouched — you still can't
  walk through glass, and no collider edit means no gauntlet risk.
- **Two builders can silently share a footprint.** The regional
  dioramas land on plinth pads that the arcana-station sweep later
  built props on top of (Graustark city under the Chariot's truck).
  Before placing anything, query the ASSEMBLED scene (all GLB
  builders merged), not just the one script you're editing.


### 2026-06-14 · world needs ground + roads BEFORE features

- **A locale is not a set of isolated detail patches.** Every locale
  build should start with TWO foundational functions before any
  buildings, vehicles, or props go in:
    1. `build_ground()` — a continuous ground covering the entire
       world area (~340m × 340m for the riverfront).
    2. `build_road_network()` — driveways, sidewalks, crosswalks,
       access ramps connecting every developed patch to every other
       developed patch.
- **Without these two**, the world reads as floating asphalt islands
  in a gray Godot-void no matter how much detail you pack into each
  individual feature. The user explicitly called this out: "roads
  don't look functional, look at all this null space."
- **Order in main()**: ground first, road network second, THEN every
  feature build overlays on top.

#### Topography per locale (vol5–7 canon)

CORRECTION on previous note: "flat" was wrong. The bayou locales are
**RELATIVELY** flat — they have geology and topography. They are not
perfectly-level planes. The `build_ground()` implementation MUST
respect each locale's canon topography:

- **D'Ambrosio's riverfront** (vol5) — relatively flat bayou bottom-
  land with raised road berms, drainage ditches at lower-than-grade,
  ground that varies a few inches between developed lots / scrub /
  river edge. Not perfectly level.
- **Harmony Creek Estates** (vol5/6) — relatively flat suburban
  lawns with some rolling terrain. Has a CREEK (per the name) which
  means a lower drainage channel running through. Each lawn rises
  slightly off the street to its house.
- **Graustark, TX/LA** (vol5) — relatively flat small-town main
  street, BUT canon: **half of the town sinks into a sinkhole**
  during the story. The sinkhole geometry must be supported by
  build_ground from the start — a tilted / collapsed crater section
  through the town centre, dropping perhaps 8-15m below grade.
  Adjacent buildings lean into the void. Plan terrain accordingly.
- **Smolvud, central OR coast** (vol5/6) — emphatically NOT flat.
  Cold rain forest with dramatic cliffs and structures built on
  wildly varied geology. `build_ground()` for Smolvud needs:
    · Heightmap-style terrain (varied Z), NOT a flat plane.
    · Cliff faces as stacked angled prism walls.
    · Coastal rocky outcrops (sphere clusters + angled boxes).
    · Switchback roads zigzagging up/down elevation.
    · Houses on stilts / perched on cliff edges (the dramatic
      vertical builds the canon calls for).
    · Dense evergreen forest with multi-sphere conifer canopies.
    · A coastline (water at the lowest elevation tier).
  Don't reuse the flat `build_ground` straight from riverfront — it
  will produce the wrong character entirely. Plan a Smolvud-specific
  ground module: `build_terrain_heightmap()` or similar, that
  samples a hand-defined Z(x, y) function and tessellates it.

#### Tools likely needed for Smolvud

- A height-sampling helper: `terrain_z_at(x, y)` returning the
  ground Z at any world coordinate, so every prop (tree, house,
  road segment) snaps to the right elevation.
- A make_cliff() helper: stacked angled prism walls that fake a
  vertical rock face.
- A make_stilt_foundation() helper: 4 cylinders descending from
  a house's footprint down to wherever terrain_z lands.
- A make_switchback_road() helper: zigzag asphalt with painted
  guardrails on the outside edge.

These don't exist yet — call them out when Smolvud begins, and
add to the helper library at the top of the build script.

#### Bayou-city features that are EXPECTED (vol5 Graustark + riverfront)

The user explicitly called out these as required to read as a bayou
city. Build them or it doesn't feel right:

- **Raised roads on low berms** — the road sits a few inches above
  grade so it stays drivable through rain/flood. Suggested visually
  by drainage ditches sitting LOWER alongside, not necessarily by a
  dramatic earthen mound.
- **Drainage ditches** on both sides of every road, with a muddy
  floor and patches of standing tannin water (the bayou water table
  is high, the ditches stay damp).
- **Sewer grates** at curb-line intervals (every 28-30m), steel
  frames with parallel slats.
- **Wear and tear on asphalt** — darker splotches, patches, cracks.
  Real bayou roads are not pristine.
- **Public parks and green spaces** — lawn, picnic tables, swing
  sets, benches, shade trees with Spanish moss, winding concrete
  paths, signage, trash cans.
- **Houses with porches and yards** (for HCE and Graustark).
- **Telephone poles** with crossbars + ceramic insulators + sagging
  power cables strung between them, repeated every ~25m.
- **Streetlights** along the road every ~22m, with arms and lenses
  glowing warm.
- **Mailboxes** on posts along the road shoulder.
- **Fire hydrants** at intersections.
- **Trees lining the road** (cypress / live oak / pine, alternating).
- **Sidewalks** with seam-line concrete texture.

These items move a scene from "scattered objects on a flat plane"
to "actual block in a working town." Skip any of them and the
scene reads as empty.

### 2026-06-14 · the mood-cycler shader system is reusable

- The screen-space mood library (lunch / dusk / chillwave / sunset /
  lithograph / noir / ice / night / 3:47 am / precipice / substrate /
  raw) is locale-agnostic. Any new scene just adds the same three
  ColorRects (NeonQuad → AsciiQuad → Quad) with the same shaders;
  MoodCycler.gd drives them identically. Don't re-invent per locale.
- The HUD MoodLabel pattern (Label node at NodePath("../HUD/MoodLabel"))
  is also reusable — MoodCycler picks it up automatically if it exists.

### 2026-06-14 · cursive_type.py is the type tool for any signage

- The Bezier-based cursive type tool (`godot/tools/blender/locales/
  cursive_type.py`) defines D ' A m b r o s i in cubic Beziers
  with proper kerning and an explicit text_width() helper.
- For future signage (HCE realtor signs, Smolvud roadside markers,
  Graustark storefront names, the diner's interior "WELCOME"), extend
  the GLYPHS dict with the additional letters and call
  `make_neon_dambrosios`-style wrappers for each font face axis.
- A two-face sign (readable from both sides) requires:
    · 'Y' face: lx(x) = -x * face_sign
    · 'X' face: lx(x) =  x * face_sign
  The formulas differ — using one for both produces a correctly
  mirrored panel and an inverted panel. Don't unify them.

### 2026-06-14 · every feature needs a TRANSITION to its neighbours

Recurring failure mode I keep making: I build a feature (parking
lot, dock, gas station, strip mall, riverbank, quay wall, river
basin) as an isolated unit, and forget that **the player needs to
ARRIVE at this feature from another one**. The transitions are
where the world reads as functional vs. dropped-in-from-the-sky:

| Feature pair | Transition needed |
|--------------|-------------------|
| road → parking lot | driveway apron + curb cut, painted lines guiding the turn-in |
| parking lot → dock | stairs (if elevation drop) or ramp; the curb edge isn't a transition |
| highway → frontage road | proper off-ramp with deceleration lane + signage |
| land → river | quay wall OR sloped bank with vegetation, not a hard right-angle drop |
| dock → boat | gangway sloped to span the deck-to-dock height difference |
| sidewalk → building | a step or entrance landing, doesn't just abut the wall |
| commercial strip → residential | something between (a vacant lot, a small park, a fence line); they don't share a property line |

Durable rule:

- **After building any feature, draw an arrow on a mental map FROM
  every other feature TO this one.** If any of those arrows
  doesn't have a transition feature, build the transition before
  calling the feature done.
- **The transition is part of the feature, not optional polish.**
  A parking lot without a road entry is not a parking lot, it's
  a slab of asphalt floating in the world.
- **For the bayou-city locales specifically**, transitions that
  must exist:
    · Every developed lot needs a curb cut + apron to the road
      it sits on (NOT just a sidewalk edge).
    · Every building needs an entry path from the road (walkway,
      stairs, ramp).
    · Every elevation change needs a stair or ramp (the user can
      flag the same "the river is level / there's no transition"
      complaint for any feature, not just the river).

### 2026-06-14 · when a fix doesn't appear, the bug is somewhere ELSE

The "river-sink invisible 6+ times" disaster. User kept asking why
the river still looked level with the land. I kept iterating on
RIVER_LEVEL_Z, bank slopes, dock height — none of which addressed
the actual cause. The actual cause: `build_ground()` was a single
340m × 340m flat box at z=-0.10 covering the ENTIRE world including
the river area. The water surface WAS at z=-2.5 the whole time. It
was just hidden under an opaque ground plane.

Durable rules:

- **When a code change you believe is correct produces no visible
  result, the BUG IS NOT IN THE CHANGE.** Stop iterating on that
  layer. Investigate what's CONTAINING / OBSCURING / OVERRIDING
  the change. Common culprits:
    · An older layer is still rendered on top (this one — ground
      box hiding water below it)
    · The GLB cache hasn't refreshed in the editor (close + reopen
      Godot, or right-click → Reimport)
    · A `material_override` somewhere downstream is replacing the
      material I just set
    · Z-fighting between two coplanar surfaces
- **When you add a new lower / smaller / hole-in-the-world feature,
  REMOVE THE PIECE OF THE OLDER FEATURE THAT'S NOW IN THE WAY.**
  Adding a river basin = split the old ground plane around it.
  Adding a sinkhole = cut the affected ground geometry. Don't
  just stack new geometry on top of conflicting old geometry.
- **If the user has asked for the same fix 3+ times, STOP CODING
  ON THE OBVIOUS LAYER.** Take a step back and look for what
  could be HIDING the change you've already made.

### 2026-06-14 · use Godot Label3D for sign text, not procedural geometry

Procedural tube-letter approaches (cursive bezier sampling, block-
letter strokes, axis-aligned box approximations) ALL smear into
unreadable shapes at the screen post-process resolution at typical
viewing distance. I burned several commits iterating cursive vs
block vs Bezier-resolution vs stroke-thickness on the diner signs.
None worked.

**The right tool**: `Label3D` in Godot. It renders proper font
glyphs at native font resolution, then those pixels go through the
screen post-process at the screen's native resolution — strokes
stay crisp.

Pattern (see `LocaleSetup.gd` for the riverfront implementation):

1. In the GLB, build the sign as a dark BACKING PANEL mesh with
   a recognizable name (e.g. `Sign_Panel_N`, `BoatSign_Panel`).
2. In `LocaleSetup.gd` (or any scene-load script), walk
   MeshInstance3Ds, find the panel meshes by name, attach a
   `Label3D` child with:
   - `text = "D'Ambrosio's"`
   - `font_size = 96`, `pixel_size = 0.008` for ~77cm-tall letters
   - `modulate = Color(0.98, 0.18, 0.20)` (saturated booth red)
   - `outline_size = 6`, `outline_modulate` dark
   - `shaded = false` so it reads as self-lit neon
   - `double_sided = true`
   - Orient via `rotation` for the right face direction
3. Leave the procedural tube-letter library (`cursive_type.py`)
   alone — it's still useful for STYLIZED signage where exact
   legibility isn't the goal (a fragmented "D'A" mark, a glow
   pattern). Just don't use it where the user needs to actually
   read the text.

**Why I missed this for so long**: I treated text as a modeling
problem because the rest of the locale is modeling. It's actually
a font-rendering problem, and Godot has a font system. Use the
right tool instead of bending the wrong one.

### 2026-06-14 · screenshots are how I see the work

- **Always ask the user for a screenshot when debugging visuals.** I
  cannot run the editor or the game. The user's screenshot is the
  only window I have into what the work actually looks like. Concept-
  art references they share are equally valuable — they tell me what
  the target IS, not just what the current state isn't.
- **Specific complaints from a screenshot beat vague complaints by
  10x.** "The D'A is cramped" + screenshot showing exactly that = I
  find and fix the spacing in one round. "Sign looks bad" alone = I
  guess at five possible issues and ship four wrong fixes.
- **Verify cursive / fine detail BY THE SCREENSHOT, not by reading
  the code.** A bug like the missing 's' arc (`theta_start ==
  theta_end` ⇒ no geometry) was invisible in code review but obvious
  the moment the screenshot landed.
- **When the user says "it's not working," ask for a screenshot
  before iterating.** Diagnose visually first, code-edit second.
- **If a build won't show changes, the GLB cache is probably the
  culprit.** Godot caches imported GLBs while the editor is open —
  close the editor, rebuild, reopen. The user's report of "I'm not
  seeing improvements" can mean "the GLB never updated," not "your
  code change was wrong."

### 2026-06-14 · the riverfront pass

- **Boxes everywhere reads as Atari 2600.** The user said "feels
  Atari 2600 aesthetic as a primitive 3D game." The fix isn't more
  polygons — it's using the right primitive for the shape (spheres
  for clouds, torus for rings, tube segments for neon).
- **Without textures, MGS2 is out of reach.** Be honest about the
  ceiling. Procedural cubes with vertex colors caps at "stylized
  lowpoly diorama." If the user wants MGS2-level, they need to
  commission texture assets or accept a different aesthetic.
- **A true ASCII renderer beats overlay tricks.** The `ascii_render`
  shader (sample-per-cell, choose glyph by luminance) gives the
  "substrate" feel of code rendering. The previous approach (edge
  detection + drifting glyph field) produced uniform snow.
- **Cursive neon at lowpoly is hard.** Even with `make_tube_segment`,
  cursive letters at the screen post-process resolution barely read.
  Either accept that the sign is iconographic rather than legible,
  or use block letters for clarity.
- **River width matters for the picture.** Foliage too close to the
  boat makes the river look like a canal. Leave 30+ m of clear
  water beside the boat.
- **Set up lesson-capture as a recurring practice.** The user
  explicitly requested this — see CLAUDE.md cadence note.

### 2026-06-14 · angular hull via custom hex mesh + V-prow

The riverboat hull had three rebuilds in one session:
1. Three stacked boxes → "blocky, Atari-aesthetic" complaint.
2. Add cylinder chines + corner spheres → "poofy, fluffy lil clouds"
   complaint (the same critique that killed the round car-corner
   experiment).
3. Replaced with **ONE hexagonal-cross-section mesh** for the body +
   **ONE V-prow** wedge tapering to a vertical knife edge + a shallow
   `make_v_stern` rake at the back.

The hex hull has 12 vertices (6 per station × 2 stations) and 8
faces: deck top, port upper, port chamfer, keel, starboard chamfer,
starboard upper, plus stern and bow hexagon end-caps. The V-prow is
8 verts → 5 faces (rear hex + top triangle + bottom triangle + port
pentagon + starboard pentagon).

Key insight: **"angular" means flat facets meeting at sharp edges,
NOT smooth curves.** When the user says "PS2 era, not shovelware,"
the goal is faceted-but-purposeful geometry — think the Phantasy
Star Online style or low-poly Twisted Metal. Spheres and high-segment
cylinders are the WRONG tool for hull/car body forms.

Reusable rule for organic-looking objects without textures:
- **For a hull/body/fuselage shape** → custom mesh with hexagonal
  cross-section + tapered ends. ~14-20 verts gets you "stylized
  ship" silhouette at zero polycount cost.
- **For a corner round-off** → a single chamfer face (one prism per
  edge), NOT spheres or rounded cylinders.
- **For a wedge/prow** → custom mesh with one face collapsed to a
  line (V-prow pattern: 6 rear verts → 2 apex verts).

### 2026-06-14 · 3D models will become physical miniatures

The user clarified the long-term goal: **the 3D maps of Graustark,
Harmony Creek Estate, and the surrounding areas are the SOURCE OF
TRUTH for FT's physical miniatures**. Small Wood (a Smolvud
sub-area) will be designed fresh in this same pipeline and carries
forward to future Smolvud planning.

Implications for how we build:
- **Topology choices need to print well.** Thin overhangs, isolated
  floating geometry, and one-vertex-wide protrusions all break in
  a miniature workflow even if they look fine in Godot. When
  modelling something the user might miniaturize, prefer closed
  manifolds and minimum feature sizes ≥ 0.5mm at the print scale.
- **Vertex-color materials translate to paint masks.** The current
  vertex-color-as-albedo pipeline doubles as paint guides — each
  distinct color → one paint pass on the miniature. Use clearly
  distinguishable colors for masks (red booths, white columns,
  brass railings) rather than gradients/blends.
- **Locale-scale models are mini terrain, not heroic minis.** The
  riverboat at hull-scale ≈ 200mm if printed at 1:120 scale (matches
  N-scale gauge). Granularity choices (8-segment cyls, 14-vert
  hulls) read fine at that scale.
- **Maps need to tile or fit on standard footprints.** Graustark
  laid out as a 340m × 340m world maps to ~280mm × 280mm at 1:1200
  (board-game scale) or 700mm × 700mm at 1:500 (terrain-table
  scale). Future locale builds should respect these snapping points.

This is a long-term constraint — don't optimize for miniaturization
prematurely (the game look comes first), but when faced with a
between-equally-OK-options choice, pick the printable one.

### 2026-06-14 · vol5 Graustark riverfront wrap — what stuck

- **Vertex-colour material zones held up.** No textures, every
  surface coloured at build time, lighting from real Light3Ds.
  The lithograph / ink-press filter family READS the scene
  perfectly when the geometry has clean material zones — vertex
  red on the sign letters and life rings is what lets the
  shader's `red_only` bleed gate fire. If the sign letters had
  been textured, the lithograph effect would have been mush.
  Rule: keep vertex-colour zoning as the primary material
  language for HCE.
- **Three-light + practicals scales gracefully to time-of-day.**
  The night-rated keys (Moon_Key 0.32 energy) and the practicals
  (sodium 1.6, bollards 0.55) sit at sensible *night base* values
  that the runtime can multiply UP for day or DOWN for moon. If
  base energies are tuned for night, the dir_mult / practical_mult
  framework lets a single scene cover every hour. Rule for HCE:
  tune base lighting for the scene's *primary* hour (HCE will be
  midday Texas), then let the runtime cycle pull other hours.
- **Naming conventions matter for runtime introspection.** The
  `_Key` suffix on `Moon_Key` is what lets MoodCycler identify
  which directional gets the sun rotation. In HCE name the key
  directional `Sun_Key`. Fill / Back stay generic.
- **Comments referencing geometry that doesn't exist accumulate.**
  Riverfront's scene file has a `; DockLamp_Pole + DockLamp_Glow
  mesh pair` comment, but there's no actual `_Glow` mesh in the
  tree — the lamp emission was meant to be a visible bulb mesh
  that was never built. For HCE: if a comment promises a mesh,
  add the mesh in the same commit or strike the comment.

### 2026-06-14 · figure-sculpt pipeline (human_sculpt.py)

- **What we learned.** First-pass Oliver Tree memorial was a stack
  of axis-aligned boxes (pants box, jacket box, head box). User
  feedback: "definitely abstract. I want something a bit more
  recognizable." Box-stacks read as Minecraft figures, not as
  people. Even a low-poly figure needs SHAPED parts: a spherical
  head, tapered legs, a torso that narrows at the waist.
- **The pipeline.** `human_sculpt.py` ships a single public entry
  point `human_figure(...)` that places a parametric standing
  figure at (base_x, base_y, base_z) with feet on the ground.
  Proportions baked into a `PROP` dict (real human dimensions at
  scale 1.0); the caller passes `scale = 2.0` for statues, `scale =
  1.0` for NPCs.
- **Parts.** Each call emits these as named MeshInstance3Ds:
  - Foot boxes (with forward offset based on facing axis)
  - Tapered-cylinder legs (`pants_flare` widens the cuff for the
    JNCO look; default 1.0 = normal trousers)
  - Pelvis bridge block
  - Tapered-cylinder torso (yoke = darker shoulder band)
  - Hanging arms with hand boxes at the wrist
  - Optional scarf/cravat collar wrap
  - Neck cylinder
  - Spheroid head (squashed slightly for egg-shape)
  - Hair style: `bowl` (mushroom dome + forward bang), `short`
    (flat cap), `bald`
  - Optional sunglasses band across the eye line
  - Optional chest accent: `star`, `stripe`
- **Facing-axis helper.** `_face_axis(facing)` returns the
  (forward_x, forward_y) unit vector for `+X`, `-X`, `+Y`, `-Y`.
  Every facing-dependent part (foot offset, face inset, chest
  accent, sunglasses) uses this so a single `facing='-Y'` parameter
  rotates the whole figure consistently.
- **Rule.** Any figure (NPC, statue, gauntlet portrait, memorial)
  goes through `human_figure(...)`. Don't stack boxes by hand. Add
  new hair styles + accent types + outfit options to the library
  rather than reinventing the geometry per call site.
- **Caller's responsibility.** Place the figure correctly on the
  terrain (`base_z = hce_elevation(...)` or the plinth top). The
  figure doesn't sample terrain itself — that's the caller's job.

### 2026-06-15 · gazebo foundation + commercial cluster + alignment

- **Floors with daylight under them are foundation bugs.** The
  gazebo used to ship a zero-thickness octagonal disc 5 cm above
  the terrace top, and the user kept calling out "the foundation
  of gazebo is, wait for it, not aligned." Fix is to extrude the
  floor down into a solid prism that touches the surface below.
  The wooden plank layer becomes a 2 cm decorative skin ON TOP
  of the stone foundation prism. Any "flat platform sitting on
  another flat platform" should be modelled as a real volume,
  not as a paper-thin disc with z-offset.
- **Pillars must connect to the roof they support.** The gazebo's
  posts ended at z = z_floor + height; the roof's outer eave ring
  was at the same z but at a wider radius. There was a 12.5 cm
  vertical gap of daylight between every post-top and the
  underside of the roof at the post's radius. Fix is two pieces:
  (a) a header beam ring connecting post-tops in a horizontal
  octagonal ring, and (b) a soffit annulus sealing the underside
  of the eave from the post ring out to the overhang. Same rule
  applies to any timber-framed building: never let the roof
  hover over the supporting columns with visible sky behind.
- **Tree-clip is a positioning bug, not a styling choice.** Flag
  pole was 6 m from an oak with canopy radius 5.8 m and the user
  called it out as "placement under/through a tree." Always check
  distance to every nearby canopy before placing a vertical prop
  taller than human scale.
- **Plate-glass storefronts → no opaque south wall.** Per the HCE
  project notes, convenience-store interiors are visible from the
  sidewalk. Don't model the front wall as a coloured panel; model
  only the structural mullions + top/bottom rails of the glass
  frame. The interior props (counter, aisles, cooler) become the
  visual content seen through the "glass."
- **Strip-mall props need a road, not just lots.** Parking lots
  floating in dirt with no road read as broken. Always pair a
  parking lot with a road segment (even a single quad) and
  driveway aprons connecting them. The road defines the
  orientation of the strip — buildings face the road, lots back
  onto the road, sidewalks parallel the road.

### 2026-06-15 · creek + pond + signage alignment

- **Water always sits inside the carved hole.** Both creek
  segments and pond water discs had been floating above their
  carved channels in places — creeks because the water surface
  was a single hardcoded `z`, ponds because the disc extended
  past the depression's flat-bottom plateau into the rising rim.
  Rules:
  - Creek segments sample `mesh_z` at each of the four corner
    quads and place the water plane at `mesh_z - 0.60`, so the
    surface tracks the carved channel everywhere.
  - Pond water discs cap at `0.48 × radius`, well inside the
    `pond_depression`'s `0.50 × radius` full-depth plateau.
  - Pond center MUST be deeper than `2 × radius` inside any
    settlement-flatten rect. If the pond crosses the rect edge
    the flatten cancels the carved depression on one side and
    the disc floats over the un-flattened hill.
- **Signage: text fits INSIDE the frame.** Stop attaching
  Label3D nodes with default `font_size = 64` and a `pixel_size`
  guessed from the panel's longest dimension — that overflows the
  short panels and reads as giant text hovering outside the sign.
  The rule:
  - Compute the panel's aabb (`mesh.get_aabb()`).
  - Pick `pixel_size` so `text_pixel_width × pixel_size ≤
    panel_width × 0.90` (10% margin) AND `text_pixel_height ×
    pixel_size ≤ panel_height × 0.85`.
  - If a multi-line string blows the height budget, drop a line
    or shrink `font_size` rather than letting the text escape
    the panel.
  - For one-word brands ("KWIK STOP", "NEXCORP", "COSMIC"), a
    rough heuristic: `pixel_size ≈ panel_width / (chars × 38)`
    keeps the word centered with a margin.

### 2026-06-15 · chapter-one block + sight lines

- **Storefronts in the same "block" sit on the same Y line.**
  Per user spec: "the qwik shop, gas and go, and comic shop and
  diner should all be in the same block ... characters can see
  each other at their jobs." Chapter-one storefronts now share
  `y = -360` and are spaced 30-50 m apart along x, well inside
  the plate-glass sight-line range. Whatever the player can see
  from the sidewalk in front of one store, the NPCs at the
  adjacent storefront counters can see back through their own
  glass. Don't break the line by rotating one building or
  burying one behind a fence — the line is the story.

- **Multi-bay strip building = one shell, partitioned bays.**
  Kwik Shop became `ARCADE | KWIK STOP | LAUNDROMAT` in one 28 m
  shell with single roof + parapet + back wall, two internal
  partition walls splitting the bays, each bay carrying its own
  plate-glass front + entry door + sign panel + interior. The
  rule: model the SHELL as one volume, then build per-bay
  interiors offset from the bay centre. Don't model three
  separate buildings butted together — you get duplicate
  partition geometry and the roof seams will fight.

- **Reposition props relative to BAY centre, not building
  centre.** When the Kwik Stop went from a 12 m standalone
  building to one bay of a 28 m strip, the ice machine /
  propane cage / cart corral that anchored to `ks_x ± offset`
  (where `ks_x` is now the STRIP centre) drifted to the middle
  of the strip. Fix is to anchor to the bay centre
  (`bay_cx = strip_x + bay_off`) and keep the offset modest. Any
  building that might grow into a strip should use the bay
  centre from day one.

- **Wide lots need a planted divider.** A 30 m wide single-row
  lot reads as a sea of asphalt. A small ~4 m island with curb
  + grass + an ornamental tree breaks the lot into recognisable
  approaches per bay — and gives the artist a place to anchor
  bag-of-leaves litter, an oil stain, etc.

### 2026-06-15 · NPC figures + interior aisle clearance

- **Place the human, then size the furniture around them.** When
  dropping `human_figure(...)` calls at counter positions, the
  figure has body thickness ~0.5 m at scale 1.0. The back-of-
  counter aisle has to be at LEAST 1.0 m (counter depth 0.7 m +
  clerk body 0.5 m + wall clearance 0.3 m), and ideally 1.5 m.
  My first chapter-one pass left only 0.6 m of clearance and
  every NPC was embedded inside the counter. Resize the counter
  (narrower depth, push further away from the wall) BEFORE
  placing the figure, not after.

- **Aisles end before they hit the counter.** When a counter
  moves, recompute every shelf / display / fixture that lives in
  the same room. The convenience-store aisles ran `depth * 0.45`
  long, set toward the back — when I pushed the counter south to
  make room for a clerk, the aisles' north end was now poking
  into the counter footprint. Rule: derive `aisle_y_end` from
  `counter_y - counter_d/2 - clearance` rather than using a
  fixed `depth * 0.45` formula.

### 2026-06-15 · water-vs-mesh sign convention

- **`mesh_z` returns the visible surface. Water lives just ABOVE
  it.** I burned a commit putting creek water at
  `mesh_z - 0.60` and the surface ended up buried under the
  terrain. The corners of a creek-water quad are sampled INSIDE
  the carved channel, so `mesh_z` there already gives the
  channel floor — water should be `mesh_z + 0.05` (just above
  the floor) for visibility, NOT below it. The "below" intuition
  comes from rim sampling (water below the RIM), but for in-
  channel corner samples the sign flips. Confusing because for
  POND water disc, `water_z` is below the rim sample (which is
  measured OUTSIDE the depression at `radius * 1.05`). The rule:
  if your sample is INSIDE the carved depression, water is `+`
  above it. If your sample is OUTSIDE the depression (rim
  ring), water is `-` below it.

### 2026-06-15 · interior aisle accounting + clerk placement

- **Every interior wall, partition and counter "eats" depth.**
  When packing a diner — booths + customer counter + waiter
  aisle + pass-through + cook aisle + prep counter + back wall —
  you have to budget at least 0.5 m per human aisle and 0.6 m
  per counter + add the wall thicknesses. My first diner had
  the pass-through and prep counter both at the same y, eating
  the entire kitchen aisle. Rule: list every layer along the
  depth axis with its size and clearance BEFORE placing
  geometry, and pad to ≥0.7 m where a human stands.
- **Place clerks where their actual workstation lives.** The
  laundromat doesn't have a counter — its "workstation" is the
  change machine and the folding table. Sticking the clerk
  behind the back wall like a convenience-store cashier put
  them inside a washer. The rule is: identify the workstation
  per building (counter, change machine, podium, fryer line),
  then put the clerk's marker in front of THAT.

### 2026-06-15 · sign orientation axes (Blender ↔ Godot)

- **Pick the THIN box axis to match the face direction.** A
  vertical sign that should face EAST/WEST needs its thin axis
  along X (`size = (0.04, h, w)`), not Y. I built a stop sign
  with thin Y (`size = (0.50, 0.04, 0.50)`), thinking I could
  just rotate the face_normal, and the sign faced N/S instead of
  E/W. Rule: the sign's THIN dimension and its world face
  direction MUST be the same axis in Blender BEFORE the glTF
  swap — picking it later via LocaleSetup orientation just
  rotates the label, not the panel.
- **`Vector3(-1, 0, 0)` for west-facing in Godot maps to a panel
  built thin-along-X in Blender** (Blender X = Godot X, both
  preserved through the gltf axis swap). For north/south facing
  panels, the THIN axis in Blender is Y (which becomes Godot Z).

### 2026-06-15 · marginal-value heuristic during grind sessions

- **Big alignment fix > 5 atmospheric additions.** During a 60-
  pass grind I noticed the highest-impact passes were the
  alignment / clip / position fixes (creek water, FoundersPond,
  NPC counter clearance, cars vs canopy columns). Atmospheric
  additions (extra props, light fixtures, lampposts, trees) read
  flat compared to a hovering pond or a clerk embedded in a
  washing machine. Rule of thumb when grinding:
  - If you find an alignment bug, fix it FIRST.
  - Add atmosphere only AFTER the alignment ledger is clean.
  - Capture a playbook lesson for every non-trivial alignment
    bug — they recur.

### 2026-06-15 · facing-axis bugs in parameterised builders

- **Always derive "depth-along-facing" from the depth variable,
  not the width variable.** When a builder is parameterised on
  `facing` and the box dimensions swap between X- and Y-facing
  orientations, the temptation is to write
  `front_off = main_d/2 if abs(fy) > 0.5 else main_w/2`. That's
  WRONG: `main_d` is always the depth along the facing axis
  regardless of orientation; `main_w` is always the width.
  Just write `front_off = main_d / 2` — no ternary. The same
  rule cost me 4 separate bugs in the suburban-house builder
  (slab dims, front door y, garage door y, driveway apron y).

- **Lines / stripes / decals lift ABOVE the slab they decorate.**
  My HS field had 11 yard lines, sidelines, endlines and mowing
  stripes all positioned at z = 0.06 with the grass slab at z =
  0.04 + 0.08 — every painted line was BURIED inside the grass
  slab and invisible. Rule: compute `slab_top_z = base + size_z`
  then put every line at `slab_top_z + small_offset` so they sit
  on top.

- **Painted accents go on the OUTSIDE wall face.** Nightclub's
  pink stripe was at `cy ± (depth/2 - 0.10)` — INSIDE the wall
  thickness so the pink was hidden between interior and
  exterior. Painted exterior decoration uses `cy ± (depth/2 +
  offset)` (outside) — never minus.

- **Plate-glass curtain wall + door must be coplanar.** I had
  the NexCorp HQ door 1.5 m INSIDE the south curtain wall — the
  player would walk into the glass and the door was unreachable.
  Rule: doors that should be enterable from the exterior sit AT
  the wall plane, not behind it. If you want a recessed
  vestibule, model the recess (cut a hole in the wall, build
  alcove walls).

- **Solid walls need EXPLICIT cutouts where doors go.** The
  nightclub south wall was a single 22 m box — the alcove + door
  + bouncers + velvet rope were all sitting BEHIND a solid wall.
  Rule: when you have a recessed entry, split the wall into
  LEFT, RIGHT and HEADER pieces around the opening.

### 2026-06-15 · house cluster spacing + driveway geometry

- **Houses on tight curves cluster at the corners.** I placed
  houses on the OUTER side of each loop segment 18 m off-road.
  Where the loop made a sharp corner (~90°), the outer-corner
  houses ended up only 5-6 m apart in world space even though
  they were on different road segments. Rule: when placing
  houses by segment, check the WORLD distance between adjacent
  outer-corner houses, not just road distance. For tight loops,
  drop houses to one per long side, or use a bigger off-road
  distance.

- **Closed road loops must close their polyline.** I built a
  loop neighborhood with 5 waypoints — that's 4 segments, an
  open polyline. The road dead-ended in the middle of the
  neighborhood. To close a loop, repeat the first waypoint at
  the end so the last segment closes back to the start.

- **Garage centre lives at `house_centre + perp * main_w/2`.**
  Not `perp * (main_w/2 + gar_w/2)`. In a builder that shifts
  `main_centre = house_centre - perp * gar_w/2` and then puts
  the garage at `main_centre + perp * (main_w/2 + gar_w/2)`, the
  +gar_w/2 and -gar_w/2 cancel. The garage centre is just
  perp*main_w/2 from the house centre. Helpers that take a
  house centre and need to compute the garage face / driveway
  apron position should use this short form, not the long
  one in the builder.

### 2026-06-15 · water layering inside rims + above ground

- **Water disc above ground OR inside a properly-modelled rim
  trough, NEVER below ground.** Two existing builds (OT Park
  reflecting pool, OT Park rill) and one new one (NexCorp HQ
  pool) all had water positioned BELOW the terrain / inside a
  solid rim box — invisible because the terrain mesh or rim
  faces hide it. The rules:
  - If the terrain at the pool location has NO carved
    depression (flat settlement zone), water `z = ground + 0.04`
    (ABOVE the surface).
  - If you build a stone rim as a solid base box, water goes ON
    TOP of the rim (e.g. `z = rim_top + 0.02`).
  - The "water below the rim" sign convention only makes sense
    when the terrain is carved (creek channel, pond depression)
    so the rim ring sits at carved-channel-rim height.

- **Apply collider hint coverage to NEW geometry.** When I
  added the suburban-house builder, the COLLIDER_NAME_HINTS in
  LocaleSetup.gd didn't include "Main" or "Garage" so houses
  had no colliders. Every time you add a NEW build function,
  audit the names against the hint list and either rename
  geometry to match existing hints (preferred — keeps the
  hint list short) or add new hints.

### 2026-06-15 · engine / asset-management notes

See `lore/_HCE_PERFORMANCE_PLAN.md` for the full dedicated doc.
Summary (currently DEFERRED — rough layout first):

- **Per-locale GLB splits.** Break the single
  `harmony_terrain.glb` into ~6 sub-GLBs (north / central /
  south-res / south-comm / east / west) and chunk-load via a
  `chunk_manager.gd` based on player position.
- **MultiMeshInstance3D for repeats.** Houses, street trees,
  lamps, parked cars, fence segments — all currently
  emit a fresh MeshInstance3D per instance. ~10× node-count
  reduction by collapsing each palette family into one
  `MultiMeshInstance3D` with per-instance transforms.
- **`visibility_range_begin/end` on small props.** Cars, NPCs,
  signs, mailboxes hidden past ~150 m via Godot 4.2+'s built-in
  visibility ranges.
- **Box colliders instead of trimesh for buildings.** The
  current `LocaleSetup.gd` builds a per-vertex trimesh collider
  for every wall the hint list matches. Way cheaper to use an
  axis-aligned `BoxShape3D` derived from the mesh AABB. Trimesh
  only needed for terrain.
- **Threshold to start.** ~60 fps drop on Steam Deck during
  fly-through, or initial load > 5 s, or GLB > 100 MB. Until
  then the monolithic build keeps iteration fast and the
  build-test-edit loop short.

### 2026-06-15 · long uninterrupted rough-layout session

50+ commits in one session. Key lessons:

- **Build first, optimise later.** The user explicitly asked to
  keep models PRIMITIVE during rough-layout. A 10k-line build
  script with one giant GLB is fine for iterating layout, even
  if it's not the right shape long-term. The performance plan
  in `lore/_HCE_PERFORMANCE_PLAN.md` is the WHEN-THEN.

- **Per-zone build functions scale better than one big function.**
  Each settlement gets its own `build_<name>()` invoked from
  `main()`. Adding a neighborhood is one function and one line
  in `main()`. Refactoring later (chunking, MultiMesh) becomes
  per-function, not per-line.

- **Standardise the road-emit helper across neighborhoods.**
  Phase 2 / West Estates / North Ranch / East CDS / OT Park /
  truck stop / drive-in all share the same road-polyline +
  curb + dash pattern. Defined inline 6 different ways across
  build functions — should hoist to a single module-level
  `_emit_road_polyline(pts, prefix, hw, with_dash)` so changes
  to road style only land once.

- **House-facing convention for road-bound builders.**
  Houses on the OUTSIDE of a road need to face TOWARD the road.
  Compute the direction from house to road centre (= `-side_sgn
  * perp`), then map to the closest cardinal facing. Three
  builders (Phase 2 / West Estates / North Ranch) got this
  wrong on first pass.

- **Settlement-zone pads pull pond depressions UP.** A 6 m-deep
  pond inside a flatness=0.55 zone yields only a 2.7 m carved
  bowl. Empirical disc sizing (probe outward, stop when terrain
  meets water_z) handles this correctly for any flatness.

### 2026-06-15 · reference-locale polish pattern (Kwik Stop)

User asked for "quality, polish sculpting and retail passes at
the qwik stop. this will become a reference locale for this
zone." The build that resulted from ~8 passes:

- **2 long E-W aisles** running across the bay with stacked
  product boxes in varied chip-bag palettes (top + middle
  shelves both sides)
- **West-wall fixture column** (south→north): slushie machine,
  coffee station (brewer + 2 carafes + cream/sugar caddy + cup
  stack), roller grill (4 rollers + 4 hot dogs + warm-red glow)
- **Back-wall cooler**: 3 glass doors with chrome handles +
  4×4 grid of visible cans through each door
- **Counter (NE corner)** with: cash register, scanner, lottery
  scratch-ticket case, tip jar, ID-check sign, receipt printer
  + paper, pinpad, counter-top
- **Backboard** with cigarette cartons in alternating colours +
  3 horizontal shelves
- **Impulse candy rack** on the customer side of the counter +
  6 candy boxes
- **2 aisle endcaps** at each aisle end (4 total) for promo
  stacks
- **Restocking cardboard-box stack** in NW corner
- **CAUTION WET FLOOR** yellow A-frame
- **Entry zone**: floor mat, wire-basket stack, magazine rack
  + 6 magazines, ceiling fluorescents (4)
- **EMPLOYEES ONLY** back-wall door + plaque
- **5 partition-wall posters** in 4 brand-poster colours
- **Door entry bell** on the storefront door interior
- **Exterior**: OPEN neon sign hung in the window, 4 window
  decals (LOTTERY / ATM / ICE / EBT), SE security camera w/
  red LED, outdoor ATM kiosk w/ screen + card slot + sign,
  3 gumball/sticker machines, hours plaque on door jamb,
  promo banner under the awning
- **3 customer NPCs**: impulse-rack shopper, slushie machine
  customer, south-aisle browser (plus Sam at register)

Rules for any other reference locale built going forward:

- **Build the SHELL first** (walls + roof + slab + sign frame +
  door + welcome mat). Then layer atmosphere.
- **Establish FIXTURE LANES** along walls so they don't clash
  with the counter + aisles. Wall fixtures along the west
  partition (slushie/coffee/grill) face EAST into the bay.
  Back-wall fixtures face SOUTH. Counter sits in the NE corner
  along the back wall.
- **Aisles run E-W** for an N-S-axis bay (perpendicular to the
  entry direction) so the player walking in sees product
  fronts, not aisle ends.
- **Sign panels are THIN along the face direction.** For a
  south-facing sign, build the panel thin along Blender -Y;
  LocaleSetup wires `Vector3(0, 0, 1)` face_normal (Blender
  -Y → Godot +Z) and the autosizer fits the text inside the
  aabb on the X-Z face.
- **NPC density**: 1 clerk at counter + 2-3 customers reading
  natural (impulse rack, fixture station, aisle browser). More
  NPCs cross the "set" threshold without adding life.

### 2026-06-15 · register placement rule

Per user design-guide direction:

- **Registers go near the main entry/exit, off to the FRONT-
  LEFT** (or behind partition glass). The clerk needs sight on
  everyone entering and leaving — that's the security
  rationale. Real US convenience-store convention.
- For Y-facing storefronts (south wall = entry), "front-left"
  is the SW quadrant of the interior. Counter LONG AXIS runs
  along the south wall, just behind the glass, west of the
  door.
- The CIGARETTE / LOTTERY backboard goes on the wall
  IMMEDIATELY ADJACENT to and BEHIND the clerk — typically
  the west wall when the counter sits in the SW corner. It
  must be within the clerk's reach.
- The IMPULSE-CANDY rack goes on the CUSTOMER side of the
  counter (the customer-facing edge), at hip-to-shoulder
  height.
- The clerk's standing position is in the strip BETWEEN the
  counter's back edge and the wall behind them — budget 0.7-
  1.0 m of clerk aisle.
- This is the OPPOSITE of where my chapter-1 build originally
  placed Kwik Stop's register (NE corner / back wall) — that
  put the clerk's back to the door, blind to comings + goings.
  Fix all the dependent fixtures (cigarette backboard, impulse
  rack, ID-check sign, clerk NPC, customer NPCs) when you move
  the counter; they all anchor off counter_(x, y).

### 2026-06-15 · carve terrain for roads (civil engineering)

After many sessions of "roads sample mesh_z per corner so they
follow the terrain", I still had floating-road / sunken-road
problems wherever an arterial crossed a hill or pond rim — because
the road quad followed terrain but the terrain itself had no idea
the road was there. Humans don't drape asphalt on hills; they
EXCAVATE.

Fix: a `ROAD_CORRIDORS` list of polylines with per-waypoint
`target_z` + a `road_carve(x, y)` function that returns the road
grade + a 0..1 weight. Applied as the LAST step of `hce_elevation`,
after settlements + berms, so roads override everything within
their corridor.

Each corridor has:
- **Full-grade half-width** (7m for arterials, 5m for collectors)
  — inside this band the terrain is locked to road grade.
- **Shoulder width** (~20m for arterials, ~16m collectors) — over
  this band terrain smoothstep-blends back to the natural height.
- **Per-waypoint target_z** matching the settlement platforms the
  road threads through (e.g. Harmony Blvd descends from +20 at the
  CC entry to -9 at the SouthComm truck route, hitting +14 at
  NorthComm, +1 at HarmonyPark on the way).

Rule of thumb for grades: residential collector ≤ 8%, arterial ≤
6%. Steepest segment in HCE is the CC entry ramp (~7.5% over 80m)
which is fine for a winding suburban arterial.

`LOT_PADS` is the same idea for parking lots / institutional pads
not covered by a SETTLEMENT rectangle — NexCorp HQ visitor lot,
hospital lot, drive-in pad, etc. Each rect pulls terrain to its
target_z inside, smooth shoulder out.

Order of operations inside `hce_elevation`:
1. base terrain (tilt + rises + dips + noise + creek)
2. ponds
3. settlements (max-weight blend)
4. berms (additive)
5. lot pads (override toward target_z by weight)
6. **road corridors** (override toward road grade by weight)

This is the civil-engineering pipeline: shape the land, then cut
roads through it. Buildings positioned via `mesh_z(cx, cy)` ride
whatever the terrain becomes, so they automatically sit flat on
the carved pads.

### 2026-06-15 · water carves too + cut-slope rules

Followup to "carve terrain for roads": water (creek + ponds)
also needs to carve, not just roads. Settlements + berms + lot
pads were fighting the analytic pond-depression and creek-dip
inside their rects, so ponds inside HarmonyPark and the creek
crossing OliverTreeMemPark surfaced ABOVE the carved water
plane. The fix:

- `POND_CARVES` mirrors `LOT_PADS` but with a circular geometry:
  `(name, cx, cy, full_r, shoulder, floor_z)`. Inside `full_r`
  terrain is locked to `floor_z`; through `shoulder` it grades
  back. `build_pond_water` reads `floor_z` directly and parks
  the water plane at `floor_z + 0.6`. No more probing mesh_z.
- `CREEK_CHANNEL` mirrors `ROAD_CORRIDORS` for the creek bed:
  polyline of `(x, y, floor_z)` waypoints. Channel half-width
  3 m; flood-plain shoulder 22 m. Water surface sits at
  `floor_z + 0.6` along the channel (per-corner z so the
  surface slopes naturally toward the outlet).
- Order in `hce_elevation`: settlements → berms → lot pads →
  WATER carve → ROAD carve. Road comes last but **yields** to
  water via `effective_road_w = road_w × (1 − water_w)` so the
  creek stays carved at crossings and an explicit BRIDGE DECK
  emits at the crossing point.

Civil-engineering cut-slope rules:

- **Linear** falloff in the carve shoulder, not smoothstep.
  Smoothstep concentrates the steepest gradient in the mid-
  shoulder, and on a coarse mesh (15 m cells) that produces
  visible terraced cells. Linear keeps every shoulder cell at
  the same batter slope.
- **Wider shoulders**: arterials at 36 m gives ~4:1 cut/fill
  slope across a 9 m elevation change (CountryClub +22 →
  NorthComm +14). Connectors 14–18 m, lot pads 14–22 m.
- **Subdivide road waypoints to ≤40 m segments** so target_z
  lerps smoothly. Catmull-Rom smoothing of the xy polyline
  then renders the road as a curve instead of a kinked
  polyline.
- **Ramp grade ≤ 10–12 %** for civil-engineering credibility.
  My first-pass NXHQLink (35 m corridor, 8 m elevation) was
  23 %; extended to 80 m gives ~10 %.
- **Bump ground mesh density** when the 15 m grid aliases the
  carve shoulder. Doubled to 10 m cells (120×84) for this
  district; the cost is ~2× more terrain vertices but the
  shoulder spans 3.6 cells instead of 2.4, smooth.
- **Bridge deck where roads cross water**: deck at road grade,
  parapets, piers descending to creek floor. Road carve
  yields to water carve at the channel so the deck spans a
  real dip instead of a flat strip.
- **Intersection slabs** at every road–road xy crossing,
  z = max(corridor_a, corridor_b). Plus crosswalk zebras on
  arterial × arterial junctions.

Discipline rule that emerged: every road I add as a corridor
also needs to match the polyline that the EMITTING build
function uses. If they diverge, the carved-flat band sits
next to where the asphalt actually draws. Several neighborhood
streets (Ridge Crest Dr, Phase 2 cul-de-sac, Magnolia Lane)
had to be re-aligned to the existing emit polylines.

### 2026-06-15 · hero-asset polish (the Kwik Stop pass)

When the user says "hero asset quality work" they want every
detail that signals "this is a real working _____" to be on the
model. Approach that works:

1. **Find the prose canon.** Pull every detail mentioned in the
   source files for that locale. For the Kwik Stop:
   - Vol 6 Ch 1 opening prose: AC at 68°, decals on the window
     (lottery / 2019 cigarette brand / TASTE HOME hamburger with
     missing eye), the convex security mirror, the back cooler
     with recursive reflection (Maya zine #11), Sam's phone face-
     up on the counter, the Hot Pocket, the microwave clock 9
     minutes fast, the roller-grill smell.
   - Sam Miller's character file: Diego leaning against the
     ice freezer, ROY the regular at 5:48 PM Friday, the zine
     stockpile under cleaning supplies.
   - The pylon reference photo: Texas star + 3 promo strips +
     gas-station cross-promo arrow.

2. **Add the "every real X has one of these" list.** For a Texas
   convenience store: ice freezer, propane cage, newspaper boxes,
   pay phone, coin-op air/water pump, sandwich board, cigarette-
   butt urn, bike rack, WE CARD sticker, credit-card logos,
   Help Wanted sign in the window, dedicated lot light pole at
   the SW corner, wet-floor sign, slushie machine, coffee station
   with two pots, roller grill with visible hot dogs, fluorescent
   ceiling fixtures, Coke door cling.

3. **Each detail names itself**, in the mesh name. `KwikStop_
   IceFreezer_GlassTop`, `KwikStop_TasteHome_BurgerBun`. Future
   passes can find and modify any specific element by grep.

4. **Tie at least one detail to canon** so the polish READS as
   "this writer paid attention" rather than "the engine emits
   stuff." The recursive-reflection nested rectangles on the
   middle cooler door are Maya zine #11's "infinite recursion"
   detail rendered as five shrinking nested panels.

5. **The visible cluster matters more than absolute count.** A
   real store has clutter ARRANGED in zones: door zone (sandwich
   board, butt urn, mat), corner zone (ice + propane + news
   boxes + air pump), the pylon zone (sign + lottery + plinth),
   the lot edge (lamp pole). Building one zone at a time keeps
   each meaningful instead of confetti.

6. **A canon-named NPC in the right spot** is worth ten anonymous
   props. Diego at the ice freezer makes the freezer mean
   something the next time the player sees it.

7. **The cluster makes the locale a REFERENCE for the rest of
   the chapter.** Once Kwik Stop is dressed to this level, the
   Diner / NexCorp Gas & Go / Cosmic Comics will read as less
   polished by comparison — that's the cue to apply the same
   pass to them.

### 2026-06-15 · automated building-road overlap audit

User complaint: "buildings bisecting roads, etc. Pass through
the whole map with a fine tooth comb, getting things looking
NORMAL." Manual checks were missing the marginal cases (road
quad reaches 2-5m into a building from a tangent angle).

Wrote a Python audit: load build module with stubbed bpy, walk
every `ROAD_CORRIDORS` segment, sample at 3m intervals along
each centerline, compute distance from each sample to every
known building rect; flag any case where `dist < road_hw`
(road quad overlaps building).

8 overlaps detected in one run, all fixable in 30 minutes:
- 2 false positives (multi-component "buildings" — TruckStop is
  a garage + fuel canopy + asphalt lot, audit needs the actual
  garage rect not the whole footprint)
- 6 real cases — fixed by either trimming the road corridor
  endpoint OR shifting the building footprint a few meters

Rule: every time the road corridor list changes or a building
position changes, RE-RUN THE AUDIT. The audit catches what eyes
miss after the third zoomed-out flythrough.

The audit script lives inline in the agent transcripts; should
be promoted to a real `tools/audit_overlaps.py` if this comes up
in a third pass.

### 2026-06-15 · human-figure anti-derpy pass

User complaint: "people look derpy, have you played with
sculpting by subtraction... see a picture in your head in three
dimensions and just whittle away?"

Can't do real boolean carving on the Blender-Python primitive
output without bloating the mesh, but I CAN approximate the
carved-sculpture silhouette by **stacking small primitives at the
anatomical landmarks every PS2-era character model uses.**
Working list captured in `human_sculpt.py`:

HEAD (formerly: 1 sphere + maybe hair):
- skull (squashed sphere, 10 segments for smoother hairline)
- cheekbones (2 small spheres at eye height, sides of head)
- jaw line (angular box across lower face)
- brow ridge (skin ridge above eye line)
- eyes (white sclera + dark pupil, always)
- nose (pyramidal skin nub) + nose shadow (darker strip)
- upper + lower lips (two-tone, lower slightly wider)
- eyebrows (hair-color accents above eye line)
- chin (skin extension below mouth)
- ears (when with_ears=True)

TORSO (formerly: 1 tapered cylinder):
- pelvis box
- BELT band + buckle on the front
- main torso cylinder
- chest cap (squashed sphere bulging forward at upper chest)
- waist band (darker contrast ring at natural waist height)
- collar (V-shape darker at top of torso, jacket-color * 0.65)
- shoulder caps (1.6x arm radius squashed sphere)
- yoke band + accent (existing, kept)

ARM split (formerly: 1 cylinder):
- shoulder cap
- upper arm
- elbow bump (1.05x arm radius)
- forearm (slightly thinner toward wrist)
- hand (squashed sphere fist)
- thumb stub
- 3 knuckle bumps on back of hand

LEG split (formerly: 1 cylinder):
- main leg taper
- knee bump (1.10x leg radius at 52% height)

POSE OPTIONS:
- standing (default; 10% lateral offset for relaxed natural)
- right_mic (existing)
- arms_out (existing)
- hands_on_counter (NEW — clerks at workstation)
- arms_crossed (NEW — observers / relaxed)
- hands_pockets (NEW — casual idle)
- one_arm_lean (NEW — leaning against something)

HAIR STYLES added:
- ponytail (crown + trailing cylinder + tie band)
- cap (baseball cap crown + bill)
- beanie (tall rounded knit + darker rolled brim)
- mohawk (center fin box)

After these 6+ passes the chapter-1 NPC cast reads as 8 visibly
distinct people in 4 different work poses, not 8 instances of
the same stiff figure. Distance from "block silhouette" to
"recognizable PS2-era human" is exactly the 20-ish anatomical
landmark primitives added.

Rule: when a figure reads "derpy," ENUMERATE the 8-12 silhouette
landmarks a real person has and add a primitive for each. Pure
sphere/box primitives at the right positions outperform
boolean-carved meshes for low-poly stylization.

### 2026-06-15 · neighborhood "lived-in" pass

When a residential block looks like "Roblox baseplate with
houses on it" instead of a real neighborhood, the missing
ingredients are usually:

1. **Curbside mailboxes** — one per house, alternating sides
   along the street at ~22m spacing. Wooden post + grey rural
   box + red flag. Without these the houses read as
   uninhabited.
2. **Continuous street tree canopy** — both sides of every
   residential street at 18m spacing (closer than arterial 25m
   so the canopy reads as continuous). FOUR SPECIES cycled
   per-block (oak / maple / pine cone / pink dogwood) so each
   block has visible variety instead of "identical green
   spheres."
3. **Residential streetlamps** — 4m pole single shoebox head
   at 30m spacing alternating sides. Different scale from the
   arterial 6m twin-head — uses the visible-from-distance
   difference to signal road class.
4. **Belt + buckle + ankle bumps on NPCs** — even at distance,
   the small per-person details register as "humans" rather
   than "props."

Each of these is ~10 lines of corridor-walking code wrapping
`_emit_X` in build_harmony_terrain.py. They add ~30 primitives
per residential street but the perceptual lift is large.

### 2026-06-15 · arterial civil-engineering + every-house micro-detail

Pass through HCE focused on roads + landscape design + adding
small per-house details that vanish individually but compound
into "designed neighborhood" perceptually.

**Arterials got the proper civil-engineering treatment:**
- Double-yellow centerline (no-passing arterial standard) +
  dashed white lane lines between center and edge for full 4-lane
  striping.
- Fire hydrants at ~120m spacing on the sidewalk side, alternating
  sides so no two hydrants sit on the same side in a row.
- Wooden utility poles at 50m spacing with crossarms, ceramic
  insulators, drum-shaped transformer cans every 4th pole, and
  3 sagging phase wires + 1 neutral neutral wire connecting
  consecutive poles. Custom `_wire()` oriented-box helper required
  for the diagonal wire runs since `_make_cyl_local` doesn't yaw.
- Red stop signs + white painted stop bars at every connector
  intersection with an arterial (NRLink, CCLink, NXHQLink,
  HospLink, OTLink, ECDSLnk, WCommL, TSLink, DILink). The
  CONNECTOR side stops; the arterial has right-of-way.
- Cul-de-sac center islands (East CDS + Phase 2): 3m circular
  curbed planter with shade tree + 4 ornamental flower clumps.

**HarmonyPark landscape pass** added a figure-eight walking loop
(pool + north park lobes), spur paths to playground and community
garden, an octagonal white-painted gazebo with hipped roof + low
railing skipping the south entry, 3 picnic tables on the east
lawn, 4 mulch flower beds with seasonal color, 5 ornamental
cherry/maple specimens at path corners, 4 extra benches along
the loop, and a stone-pier park entry sign.

**Per-house micro-details on _build_suburban_house** (which means
they propagate across every NorthRanch, Phase 2, East CDS, West
Estates, Phase 3 house in one touch — single point of insertion,
multiplier of effect):
1. Foundation shrubs — 4 evergreen shrubs in mulch rings along
   the front wall. Standard American yard staple.
2. Front walk — 1.2m × 3m concrete path from porch front edge
   out into the yard. Connects "porch" to "rest of yard."
3. Yard specimen tree — single deciduous tree seeded
   deterministically by house position (varies trunk height
   4.2-5.8m, canopy radius 1.8-2.55m, side of walk L/R, distance
   from front wall 5-6.5m, and seasonal color most green w/
   occasional autumn orange ~1/13 houses).

Lessons that came out of this pass:

- **Single insertion points are force multipliers.** Adding to
  `_build_suburban_house` instead of editing each neighborhood
  separately turns 28 lines into 80+ houses with the new detail.
  When considering any per-instance detail, ask first: "is there
  a shared builder I can extend?" Editing per-neighborhood is
  almost always wrong when the houses share a builder.

- **Use deterministic seeding for variety.** `(int(cx*7) +
  int(cy*13)) % 100` gives every house a per-position "DNA"
  number. Same house = same tree every build, but next-door
  houses get visibly different trees. Beats either pure random
  (non-reproducible) or no variation (every house identical).
  Reuse this pattern for foundation shrub variation, fence type
  variation, mailbox color variation, etc.

- **Civil-engineering road furniture is mostly corridor-walking
  loops.** `_emit_hydrants`, `_emit_utility_line`, `_emit_lamps`,
  `_emit_mailboxes` all share the same skeleton: walk a Catmull-Rom-
  smoothed polyline, accumulate arc length, emit a thing every N
  meters offset perpendicular by M meters. Could be a single
  `_corridor_walk(pts, spacing, side_offset, alternating, emit_fn)`
  helper. Worth refactoring once you have 5 of these.

- **For oriented thin geometry (wires, crossarms, railings)
  the helpers `_make_box_local` / `_make_cyl_local` are
  axis-aligned only.** Use `_finalize_mesh` directly with custom
  vertices for anything that needs to point along an arbitrary
  XY direction. Pattern: compute unit direction + perpendicular,
  emit 8-corner box verts using those basis vectors.

- **A 0.30m thin curb is visible from gameplay distance** but
  reads as detail rather than clutter. For pool decks, planter
  rings, cul-de-sac islands, gazebo skirts, this scale is the
  sweet spot.

### 2026-06-15 (cont.) · the position-seeded variety pattern

Continuing the per-house micro-detail grind, a clear authoring
pattern emerged that's worth codifying:

```python
seed_feature = (int(cx * PRIMEA) + int(cy * PRIMEB)) % 100
```

Where `(cx, cy)` is the entity's world position and `(PRIMEA,
PRIMEB)` is a per-feature prime pair (use a DIFFERENT pair for
each feature so that seeds decorrelate — same house should not
always get both a car AND a chimney on the same side).

Then the seed drives:

- **Presence gates**: `if seed < N` selects N% of instances
  (trash bins on 40%, parked cars on 55%, boulders on 30%).
- **Discrete variant choice**: `palette[seed % len(palette)]`
  picks a color / type from a fixed palette.
- **Count variants**: `n = 1 + (seed % 3)` picks 1-3 rocks etc.
- **Continuous size variants**: `(seed % 5) * 0.10` adds
  per-instance jitter to dimensions.
- **Sub-feature seeds**: `(seed + r * 11) % 100` derives a
  per-sub-instance seed for varying multiple things on the same
  parent (e.g., 3 rocks per yard each with different size/color).

Why this beats both alternatives:
- vs. pure random: every build of the same script produces the
  SAME map, but neighbors look different. Reproducible art.
- vs. no variation: solves the "identical houses" toybox feel.

The pattern stacks. Within `_build_suburban_house` we now have:
- yard tree (seed_yt = cx*7 + cy*13)
- foundation shrubs (no seed — present always)
- chimney + vent (seed_roof = cx*11 + cy*7)
- shutter color (seed_shut = cx*3 + cy*5)
- driveway car (seed_car = cx*17 + cy*23)
- curbside trash bins (seed_trash = cx*13 + cy*19)
- xeriscape rocks (seed_rock = cx*23 + cy*17)

All keyed off `(cx, cy)`, but each feature uses different primes
so two adjacent houses (~30m apart) have visibly uncorrelated
feature sets. Co-prime selection prevents the "every-other-house
clone" pattern that emerges if you share too many prime factors.

Architectural detail rule that came out of this:

**For any helper used by multiple call sites, supporting both
X- AND Y- alignment is mandatory.** The `_build_parked_car`
helper bakes in Y-axis orientation (4.4m long along Y), and as
a result the driveway-car pass had to skip X-facing houses.
That's a wart — half of one neighborhood gets cars and half
doesn't. Either pass the orientation through, or build the long
axis from a unit-vector argument computed from `_face_axis()`.
Next refactor target.

### 2026-06-15 (deep grind) · stacking and coordinating per-house features

After the seed-pattern was established, kept pushing more
optional per-house features. The list as of this session:

ALWAYS present (every house): foundation shrubs · front walk ·
yard tree · chimney + roof vent · gable vents · window shutters ·
backyard fence · backyard tree.

OPTIONAL (per-house seed gate): dormer 25% · parked car 55% ·
trash bins 40% · landscape boulders 30% · basketball hoop 25% ·
yard sign 12% · backyard pool 12% · garden shed 25% · front
hedge row 35% · rear patio + BBQ 30%.

Coordination patterns that worked:

1. **Anti-overlap coordination via shared seeds.** When two
   optional features want the same yard region (pool + shed),
   one reads the other's seed and flips its side. Stops the
   "pool inside the shed" rendering bug without needing global
   geometry checks. Cheap, deterministic, and the artist
   doesn't have to think about it.

2. **Side preference rolled into the seed.** Each feature
   picks a side (`sgn = -1 if seed % 2 == 0 else 1`) before
   choosing position. Different features use different parity
   so two features that often clash (yard sign + walk; trash
   bins + parked car) sit on opposite sides reliably.

3. **Decoration density felt good around 1 detail per ~30 m²
   of lot area.** Too sparse and the yard reads as empty;
   too dense (every feature present on every house) reads as
   game-spawned clutter rather than lived-in. The gating
   percentages above were tuned by gut, but match real
   neighborhood walking-tour aerial photos.

4. **Park furniture as the "small real park" cluster.** Trash
   cans, drinking fountains, dog waste stations, BBQ grills,
   benches — none of these matter individually, but the
   absence of ALL of them is what makes a park read as
   "video-game lawn." Hand-place them at path corners, not
   evenly distributed: real parks have furniture concentrated
   at the destinations (gazebo, picnic area, playground), not
   the connector paths.

5. **Adapter helpers > duplicated geometry.** When the
   `_build_parked_car` Y-only limitation caused half the
   driveways to be empty, the fix was a 20-line rewrite to
   compute body/cabin/wheels from a unit-direction vector
   instead of hard-coded Y geometry. Now all 4 cardinal
   orientations work. Pattern: when a helper is hard-axis,
   parameterize via a unit-vector + perp basis instead of
   if-branches. Less code, more flexible.

Arterial-level passes added this session: stop signs at every
connector approach, painted stop bars, cul-de-sac center
islands, school-zone speed bumps, storm drain grates,
commercial pole signs at EastComm businesses, landscape berms
in undeveloped arterial frontage, HarmonyPark furniture
cluster.

What still feels primitive (next pass targets):
- House wall color variation within a neighborhood. Currently
  cycles through 4-5 palettes; could be expanded to 10-15
  with seasonal accent variation.
- Driveway curb cuts (flared concrete apron where driveway
  meets road). Currently driveways T-bone the curb.
- Sidewalk seam joints on residential walks.
- More variety in commercial signage (lit channel letters,
  banner signs on smaller storefronts).
- Commercial loading docks / dumpsters more thoroughly placed.

Commercial rooftop HVAC + vents + ducts: DONE this session
(see build_commercial_rooftop_mech). Most visible-from-above
"this is a real commercial building" tell.

### 2026-06-15 (terrain triage) · the FOUR systemic failures behind "still looks busted"

After 30 commits of per-house micro-detail, the user reviewed the
result and said it still looked "busted" with specific complaints:
houses floating on hills, rivers floating, buildings in roads,
roads cut-and-pasted at corners, suburban house islands without
connection. The detail passes weren't the problem — the
foundational systems underneath were. Diagnosed and fixed in one
session:

**1. River floating above the channel** (most visible bug).
Cause: mesh grid was 120×84 (10 m cells) but the creek's full-
carve band was only 3 m wide. Vertices straddling the channel
fell OUTSIDE the carve, so triangulated terrain "tented up"
between samples — the water plane stayed at floor_z+0.6 but the
surrounding terrain rose 2-3 m above it, making the water look
like it was hovering in mid-air. Fix: GROUND_NX 120→200 (10 m →
6 m cells) AND CREEK_CHANNEL_HW 3 → 5 m. The carve band now
always catches both bordering grid vertices on a 6 m grid (worst-
case offset between channel CL and nearest column is 3 m < 5 m).
General rule: **a carve band's full-width must be ≥ the grid cell
half-diagonal** or the carved feature will visually disappear
between samples.

**2. Houses half-floating on hills.**
Cause: each suburban house's slab sat at `ground_z = mesh_z(cx,
cy)` — a single-point sample at the slab CENTER. Terrain across
a 14×9 m footprint varies up to 0.75 m, so the high corner
floated and the low corner buried. Fix: a FOUNDATION SKIRT — a
concrete-colored box extending from the slab down to MIN(mesh_z
at 9 footprint sample points) − 0.5 m. The visible foundation
ALWAYS meets the ground at the high corner; on the low side it
pokes 0.5 m below grade for safety margin. Same trick will apply
to commercial buildings.

**3. Building/road overlaps the curated audit missed.**
Cause: `audit_overlaps.py` used a hand-edited BUILDINGS list. Any
building added to the build script that wasn't ALSO added to the
audit silently slipped through. Fix: rewrote the audit to
intercept every `_make_box_local` call during a stubbed build,
filter to building-sized boxes (≥4×4×2 m, excluding slabs/roofs/
lots/sidewalks/etc.), and check each against ROAD_CORRIDORS.
Adding a new building no longer requires touching the audit.
Caught 4 overlaps in the wild: SS_Office 2.8 m into ECommS,
P2 cul-de-sac house straddling the inlet road, ECDS cul-de-sac
house straddling its inlet, and the original culprit. Lesson:
**curated audit lists rot silently; intercept-based audits catch
everything.**

**4. Roads cut-and-pasted at corners.**
Cause: `build_intersections()` emitted a SQUARE asphalt slab at
every road-road intersection. Square slabs read as obvious "step"
corners. Cause #2: polyline BENDS within a single corridor had
no corner geometry — two consecutive road quads met at an angle
with a visible angular seam. Fix #1: intersection slabs are now
16-sided regular polygons (radius = max(hw)+0.8 m), which read
as proper curb-radius junctions. Fix #2: new
`build_road_corner_fillets()` emits a 12-sided plate at every
waypoint where the turn angle exceeds 25°, hiding the angular
seam between adjacent quads. Lesson: **square slabs in a curve-
based world always read as stitched, even at intersections;
small round/octagonal plates fix the silhouette for ~16 verts
each.**

**5. House islands without connection.**
Cause: each house had a 3 m concrete front walk that ended in
midyard — so visually the house was disconnected from the
sidewalk by 6 m of grass. Driveways went straight from garage
to curb with no flare, just a rectangle butting up against the
road. Fix: walk extended to 9 m (full setback distance from porch
to sidewalk) AND `_build_driveway()` now emits a TRAPEZOIDAL
FLARE for the last 2.5 m before the curb, widening to 5 m so it
reads as a real curb-cut apron. House → road network now reads
as connected.

**6. Humans read as Figlo toys.**
Cause: baseline PROP had narrow shoulders + uniform-width torso
(0.46 m shoulder, 0.20 → 0.18 m torso radius). Reads as a
cylinder, not a body. Fix: PROP shoulder_w 0.46→0.50,
torso_r_top 0.20→0.23, torso_r_bot 0.18→0.15 — a clear V-taper
torso silhouette. PLUS introduced BODY_PROFILES dict with 8
variants (male_avg, male_tall, male_heavy, female_avg,
female_slim, teen, child, elderly) applied as PROP multipliers
in a try/finally around the build pipeline. Added skin + hair
color palettes. The ambient_npc cast went from 15 identical
silhouettes to 20 varied bodies (kids, a heavy-set truck stop
attendant, an elderly mourner, a teen with a ponytail, a mom
and toddler at the plaza, etc.). Same for the chapter-one cast.

---

### Workflow lessons baked in from this triage

1. **Before adding more detail, audit the systemic layers.**
   Particle-level fixes don't matter if the river is floating.
2. **Per-vertex sampling on coarse grids ALWAYS aliases narrow
   features.** If your feature is < grid cell width, either the
   grid gets finer or the feature gets wider (with a carve band
   that catches at least one cell vertex on each side).
3. **Single-point sampling for multi-point geometry is wrong.**
   A slab sitting on a tilted terrain has 4 corners, not 1; sample
   all of them and take min for foundation top.
4. **Curated lists rot.** Any tool that maintains a parallel list
   of "things to check" will silently miss the next addition.
   Intercept-based audits don't have this problem.
5. **Curve worlds need curve geometry.** Square slabs at curve
   intersections look stitched no matter how big they are.

### 2026-06-17 · Diner booth iterations + windows + cathedral gauntlet floor

- **Booth orientation matters — benches PERPENDICULAR to the
  window wall is the only configuration that works.** Iteration 1
  had benches parallel to the wall (long-axis along the wall);
  patrons couldn't enter because the dividers + table sealed the
  alcove. Iteration 4 finally got it right per the reference
  photo: benches' long axis is perpendicular to the wall, dividers
  only span wall→table (not to the aisle edge), east end is open,
  patrons step in from the aisle. **Rule:** before building any
  alcove seating, draw the entry path. If the aisle side isn't
  open at the bench's open end, the booth is sealed.

- **Picture windows: don't add a glass slab. Leave the opening
  empty.** Vertex-color builds can't express transparency. A solid
  "RiverWindow_Glass" box at the opening becomes an opaque blue
  wall the player can't see through. Solution: omit the glass
  slab entirely, add only the brass frame + mullion grid; the
  player sees straight to the exterior geometry built by
  build_enhanced_river_view. **Rule:** any window that should
  read as "see-through" gets NO glass — just frame + mullions.

- **Hull skin must wrap EVERY annex.** Adding a closet or hallway
  annex outside the main shell without extending the
  build_riverboat_superstructure hull-skin pass leaves those
  annex's outer walls looking unfinished / "exposed to the
  elements" per user feedback. **Rule:** every annex added to a
  building gets a corresponding `Hull_<Annex>_*` skin pass with
  red trim band + gingerbread cornice, matching the main hull.

- **Helpers don't auto-port between builders.** `make_sphere_low`
  was defined in build_diner.py but not in
  build_cathedral_interior.py; copying a code pattern that uses it
  fails with NameError. **Rule:** before reusing geometry code
  between builder files, grep for every helper it calls and verify
  the destination file has them all. If missing, copy the helper
  definition over too.

- **Pre-existing layout bugs surface when scenes restructure.**
  The diner's north wall had a 13m-wide segment centered at
  X=+5.85 extending 3.35m past the east shell wall — pre-existing
  but unnoticed until I added the bar door cut. **Rule:** when
  modifying a wall segment, verify the existing geometry's
  center+size math first; don't assume.

- **Round cylinders + spheres beat boxes at eye-level.** The
  rectangular ceiling fans were flagged immediately as "boxy."
  Replacing the box motor housing with a cylinder + downrod +
  spherical light globe + bladed cylinders read instantly as a
  real fan. **Rule:** anything the player sees at eye level
  (lamps, fans, kettles, wheels, pots) gets cylinder/sphere
  geometry, not box approximations. Boxes are fine for walls,
  floors, and far-distance silhouettes.

- **22-arcana floor stations work as canonical layout for the
  cathedral.** Per _GAUNTLET_BUILD_WIKI: "the whole tarot built
  into the floor." Each station gets a brass-stencil floor
  outline + Roman-numeral plaque + the canonical prop. This is
  more readable than dumping all 22 zones into a single open
  room: the outline makes each zone discoverable, and the prop
  signals which arcana lives there without text labels.

### TEMPLATE for next session

```markdown
### YYYY-MM-DD · <session focus>

- **<headline lesson>.** <one-sentence summary of what went wrong /
  what we learned, plus the rule that came out of it>.
- ...
```

---

### 2026-07-21 · Meshy image-to-3D hero-asset pipeline (untextured T2)

Added an external-API path to the 3D pipeline for HERO objects (statement
pieces a locale can't reach with procedural cubes) — image → low-poly
untextured GLB → normalized into the vertex-color pipeline. Two halves,
mirroring the house `runway_render.py` / `elevenlabs_render.py` pattern:

- `godot/tools/meshy_render.py` — stdlib runner. `POST /openapi/v1/
  image-to-3d`, poll, download `model_urls.glb` to `assets/3d/meshy/`.
  Auth via `MESHY_API_KEY` env or gitignored `.meshy_key`. Every request
  field passes through the queue's `params`, so the **T2 model id** and any
  new Meshy fields are data, not code. Defaults are the untextured low-poly
  workflow (`should_texture:false`, low `target_polycount`, triangle topo).
- `godot/tools/blender/build_meshy_import.py` — Deck-run normalizer:
  join → recenter (min Z→0) → scale to a real metre height → optional
  decimate → **bake a flat vertex-color layer + minimal material** (the T2
  output is untextured, so we give it the pipeline's flat identifier) →
  re-export GLB. Runs via `run_cathedral.sh` like every `build_*.py`.

Lessons worth keeping:
- **Keep the network half Blender-free and the Blender half network-free.**
  The runner runs anywhere (CI, this container); the normalizer runs on the
  Deck. Neither imports the other's world. Same split the audio/video tools use.
- **Pass API fields through as data.** A new model tier ("T2") or a renamed
  field shouldn't need a code edit — the queue's `params` dict is merged over
  defaults straight into the request body.
- **Untextured is the feature, not a gap.** T2's no-texture output drops
  cleanly into the vertex-color / Light3D / screen-space stack; the normalizer
  bakes one flat vertex color so it reads like every other locale mesh. Hero
  objects raise the silhouette ceiling, not the texture rule.
- Verified the Blender script with the STOP-RULE stubbed-bpy smoke test
  (main()/helpers run clean); real bpy-API correctness still needs a Deck run.
  Gitignore the key + raw `assets/3d/meshy/**/*.glb`; keep the manifest.

---

### 2026-07-21 · SlowstickDiorama · shallow 3D behind a 2D stick

`SlowstickDiorama.gd` (scenes/games/estuary_3/) puts a shallow 3D
diorama behind a slowstick's UI: a SubViewport with a slow-turning
UNTEXTURED low-poly hero object under a key+fill Light3D rig and a soft
ambient Environment. The flagship of the graphics program and the first
consumer of the Meshy pipeline — point `glb_path` at a normalized
assets/3d hero and it renders; with none it builds a procedural
"resonator" (stacked torus rings + core, one flat material) so the
pilot works before any asset exists.

Lessons / gotchas (Deck-verify — SubViewport 3D can't render in CI):
- **`show_behind_parent` on the SubViewportContainer** is how the 3D
  renders BEHIND a host Control's own `_draw` (e.g. Basilica's
  wireframe) instead of over it. A `_draw` parent draws beneath its
  children by default, so without this the diorama would cover the game.
- **`msaa_3d = DISABLED`** keeps the chunky low-fi silhouette — smoothing
  fights the silkscreen look. Tint/material come from the host's
  SlowstickLook on top; the diorama is the picture, joins "world_render"
  so F4 leaves it.
- Untextured is the point: a StandardMaterial3D flat albedo + Light3D
  gives the vertex-color-era read without any texture asset.
- Verify path: SlowstickDioramaDemo.tscn opens standalone (F6) to prove
  the diorama in isolation before any risky wire into a live stick.
