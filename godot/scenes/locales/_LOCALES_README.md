# Locales · 3D Game Scenes for vol 5

Per-chapter Godot scenes that wrap the Blender-built GLBs with
dynamic lighting + the demoscene post-process. Each scene is a
walkable + cinematically-framable space.

## what's here

| chapter | locale | scene file | GLB | status |
|---|---|---|---|---|
| 0 · Fool | D'Ambrosio's diner | `diner.tscn` | `assets/3d/locales/diner.glb` | **shipped — testbed** |
| I · Magician | the Cathedral of Rust and Code | (uses `scenes/cathedral.tscn` from vol 6 game) | existing | shipped |
| II · Priestess | Elicia's bungalow | `bungalow.tscn` | `bungalow.glb` | queued |
| III · Empress | the riverboat (Nicola's floor) | `riverboat.tscn` | `riverboat.glb` | queued |
| IV · Emperor | the riverboat (Dante's helm) | (shares `riverboat.tscn`) | same GLB | queued |
| V · Hierophant | the circuit | multi-locale (`church.tscn` + `blackcar.tscn` + `bandstand.tscn` + `armory.tscn` + `riverfront.tscn`) | per-locale GLBs | queued |
| VI · Lovers | the Roberts house | `roberts.tscn` | `roberts.glb` | queued |
| VII · Chariot | Ember & Ash warehouse | `ember_ash.tscn` | `ember_ash.glb` | queued |

## the diner · build and open

```bash
# build the GLB (from /home/deck/Downloads/modern-mythology/)
cd godot/tools/blender/locales
blender --background --python build_diner.py
# (or, if you've copied run_cathedral.sh into this directory, use it)

# then open the godot/ project and load scenes/locales/diner.tscn
# press F5 to walk the diner
```

## the moods

The diner ships with five named light setups (driven by
`LightController.gd`):

- **`lunch`** — bright, clean, warm fluorescents + sun through the
  windows. Default. The canonical busy hour.
- **`dusk`** — warm orange directional + long shadows. The shift
  changing.
- **`night`** — interior point lights only + cool parking-lot
  sodium through the front windows.
- **`3_47_am`** — the canonical Fool hour. Counter lamp dim,
  cool river light from the west, dim sodium from the east.
  Triggers the ASCII overlay at 30% intensity.
- **`precipice`** — reserved for the chapter's climactic mode. A
  single cold-blue spotlight on the precipice door + low warm
  ambient. ASCII overlay at 60%. The post-process palette drops
  to 6 colors.

Switch moods from any script with:
```gdscript
var locale = $Diner   # or however you reference the root
locale.set_mood("3_47_am")
# or to animate the transition:
locale.tween_to_mood("3_47_am", 2.0)
```

The post-process uniforms (palette quantization, dither strength,
scanline strength, chromatic aberration, ASCII overlay strength)
all swap with the mood. The geometry doesn't move; the world
shifts register.

## the camera markers

The Blender script ships 8 named cameras exported as Camera3D
nodes in the GLB:

- `cam_player_entry` — at the front door, looking in (default
  spawn-adjacent)
- `cam_wide` — establishing shot from a southeast corner
- `cam_close_counter` — at the counter, looking at the back bar
- `cam_close_booth_6` — looking at booth 6 (the canonical booth)
- `cam_close_payphone` — in the back hallway at the payphone
- `cam_close_cardwall` — looking at the corkboard of pinned cards
- `cam_close_precipice` — looking at the precipice door (for the
  reveal moment)
- `cam_river_window` — looking out at the river

To cut to a named camera, use Godot's `Camera3D.make_current()`:
```gdscript
get_node("Geometry/cam_close_booth_6").make_current()
# scene plays...
$Player/Camera3D.make_current()   # back to player POV
```

## the precipice door

The "too-tall narrow door that doesn't match the trim" is built
into the geometry at the far end of the back hallway. By default
it's just there — visible if the player walks the hallway and
looks. The chapter's climactic reveal moment can:

1. Switch the mood to `precipice` (cold spotlight on the door)
2. Cut camera to `cam_close_precipice`
3. Play the prose / dialogue
4. The door's trim color is deliberately wrong — the player can
   see it without being told

The door's transform is exported with its mesh name; Godot can
find and animate it: `get_node("Geometry/Precipice_Door")`.

## the post-process

The demoscene_post.gdshader applies the substrate aesthetic as a
screen-space transformation:

- Restricted palette (quantized to N colors per mood)
- Bayer 4×4 ordered dither
- Scanlines (CRT signature)
- Sub-pixel chromatic aberration
- Optional ASCII overlay (luminance → density-mapped procedural
  glyphs)

It's a single ColorRect on a CanvasLayer at the top of the scene
hierarchy. Mouse passes through (mouse_filter = 2). No
performance cost beyond a fullscreen pass on the GPU.

To disable post-process entirely for debugging, set
`shader_parameter/palette_size = 256` and all other strengths to
0 — the scene will render through the post-process untouched.

## next per-locale

When you build the next locale (bungalow, riverboat, roberts,
etc.):

1. Copy `build_diner.py` as the template.
2. Adjust the geometry per the locale's canon (per
   `_VOL5_WIKI.md`).
3. Adjust the palette constants (per-locale color identity).
4. Add camera markers for that locale's framing.
5. Build a new `.tscn` mirroring `diner.tscn`:
   - Instance the new GLB
   - Add LightSetups groups appropriate to the locale's moods
   - Reuse the PostProcess + LightController + Player setup
6. Document the moods + cameras in this README.

The pattern stays the same. The locales accumulate.

## VN shot markers (scene direction)

Locales used as VN backgrounds can carry `Marker3D` shot nodes for
the 3D-comic direction system (`lore/_VN_DIRECTION_PLAYBOOK.md`):

- Name `shot_<type>_<id>` — types: `closeup`, `insert` (plus an
  optional `shot_establish` override; the Background3D camera
  preset is the implicit establish).
- Group `vn_shot`, optional `metadata/fov` (inserts ~35,
  closeups ~45).
- The marker's transform IS the camera framing. In .tscn text,
  `position` + `rotation` lines are enough — yaw cheat-sheet in
  the playbook. First marked-up locale: `kwik_stop.tscn`.
