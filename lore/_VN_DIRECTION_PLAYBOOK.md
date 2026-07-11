# VN SCENE DIRECTION · the 3D comic

How the visual novel gets a camera. The target is NOT film — it is
a COMIC read in 3D space: hard cuts between held frames, the way a
page moves panel to panel. Motion is the exception, not the rule.

## The grammar · four shot types

1. **ESTABLISH** — the locale wide. Where the reader learns the
   room. Default shot; every scene opens here.
2. **CLOSEUP** — a speaker or a face. The bust/portrait moment.
3. **INSERT** — a prop, held close: the register, the tape, the
   note on the counter. The comic's "detail panel."
4. **PANEL** — a 2D info card OVER the scene: a receipt, a page,
   a diagram. Rendered flat (HeroImage JSON or text card) inside
   a comic border, on a CanvasLayer in the "ui" group (F4 rule).

Cuts by default. A shot may DRIFT (slow push-in, ~2%/sec) when the
text lingers — mark it explicitly. Never ease between shots like a
camera operator walked there; a comic does not pan between panels.

## Script syntax (parsed + stripped at line display)

Directives lead a VN script line, square-bracketed:

    [shot:establish]           cut to the locale wide
    [shot:closeup sam]         cut to marker shot_closeup_sam
    [shot:insert register~]    cut to shot_insert_register, drifting
    [panel:receipt_47]         overlay panels/receipt_47.json
    [panel:off]                dismiss the panel

`~` suffix = drift. Unknown marker/panel = silent no-op (fallback
discipline — a script must never crash the reader).

## The machinery

- **Markers in the locale**: every shot is a `Marker3D` in the
  locale scene, named `shot_<type>_<id>` (or `shot_establish`),
  in group `"vn_shot"`. The marker's transform IS the framing —
  authored in the editor, where framing belongs. Optional metadata
  `fov` (default 50; inserts want ~35).
- **VnDirector** (`godot/scripts/vn/VnDirector.gd`, built): owns
  the cut. `cut_to("closeup_sam", drift)` finds the marker, snaps
  the active Camera3D, starts the drift tween if asked. Also owns
  the **letterbox** — thin bars that appear on closeup/insert
  (comic panel crop) and leave on establish. `panel(id)` /
  `panel_off()` for info cards.
- **Restore**: the director remembers the camera's original
  transform; `release()` puts it back (scene end, ESC menu).

## Wiring (BUILT — v1)

1. `GameEngine.gd` — `_dispatch` routes narrate/say/think through
   `_directed(n)`: regex `^\[(shot|panel):([^\]\r\n]+)\]\s*` strips
   stacked directives off the text front and dispatches each to
   `_director` before display. Zero directives = old behavior; the
   scene-data dict is never mutated (SceneDataDB caches it).
2. `VnDirector` (`godot/scripts/vn/VnDirector.gd`) is created once
   in `_build_layers` and drives the Background3D SubViewport
   camera via new hooks on `Background3D.gd`: `get_camera()`,
   `find_shot_marker(name)`, `has_locale_loaded()`,
   `restore_preset_vantage()`. A shot arriving before the deferred
   `load_location` finishes parks and retries up to 60 frames.
3. `[shot:establish]` falls back to the locale's CAMERA_PRESETS
   vantage when no `shot_establish` marker exists — every existing
   locale supports it with zero markup. closeup/insert with no
   marker = silent no-op (hold the current frame).
4. Letterbox: two ColorRects (z 95) inside GameEngine's own tree —
   NOT a CanvasLayer, so the F4 HUD sweep can't hide the picture.
   On for closeup/insert, off for establish. Panels are a bordered
   card (z 101) in the upper field; dialog owns the bottom.
5. Drift = FOV tighten at 2%/sec, floored at 86% of the shot's
   starting FOV. Cuts snap; nothing eases.
6. First directed locale: `kwik_stop.tscn` — five markers
   (insert_register / insert_door / insert_coffee / closeup_sam /
   closeup_customer). First directed scene:
   `vol6_ch1_shift_change.json` (five directives).
7. MoodCycler untouched — lights are the mood's job; the camera
   is the page's.
8. Panels dir: `godot/resources/vn/panels/*.json` (HeroImage
   schema). Missing file → bordered text card with the id.

## Voice rules for directing scripts

- Establish once per location change; do not re-establish on
  every beat.
- Insert BEFORE the text names the prop, not after — the comic
  shows, then the caption speaks.
- Closeups for decisions and reveals; hold them across the whole
  exchange, don't ping-pong between speakers.
- Drift is for dread and patience only. If everything drifts,
  nothing does.

## Recent lessons

### 2026-07-11 · v0 · grammar + director core

- **A comic, not a film.** The user's brief: "almost a 3D comic
  moving between close-ups, establishing shots, insert shots and
  prop/info/panels." Cuts are the default; that single decision
  removes all camera-path authoring and makes every shot an
  editor-placed Marker3D.
- **Framing lives in the editor, not in code.** Markers carry the
  whole shot. Code only cuts, drifts, letterboxes, restores.

### 2026-07-11 · v1 · director built + Kwik Stop pilot

- **Markers in .tscn are just position + rotation lines.** No
  hand-computed Transform3D basis: `position = Vector3(...)` and
  `rotation = Vector3(pitch, yaw, 0)` are valid tscn properties
  and read like a shot list. Yaw cheat-sheet for locale space
  (Blender→Godot: gx=bx, gy=bz, gz=-by): look WEST(-X) = +π/2,
  EAST(+X) = -π/2, SOUTH(+Z, toward the y=0 wall) = π.
- **Establish-with-no-marker must restore the preset.** The
  Background3D CAMERA_PRESETS vantage IS the authored wide; the
  director treats it as the implicit shot_establish so directing
  can roll out scene-by-scene with zero locale edits.
- **Deferred locale loads race the first directive.** GameEngine
  defers `load_location`; a `[shot:]` on the scene's first line
  lands before the locale instance exists. The director parks the
  spec and retries per-frame (60-frame cap) instead of dropping it.
- **The letterbox must not be a CanvasLayer.** F4's clean-screen
  sweep hides every CanvasLayer; the comic crop is part of the
  PICTURE, not HUD. Plain ColorRects in GameEngine's control tree
  at z 95 (under portraits/dialog at z 100).
- **Hold the closeup across the exchange.** In the pilot scene the
  camera cuts to Jen once at "Diego come by today?" and stays
  through Sam's answers — the no-ping-pong rule immediately felt
  right in markup; re-cutting per speaker read as noise.

## TEMPLATE — new lesson entry

```
### YYYY-MM-DD · short session title

- **Punchy lesson, present tense.** Two-to-four sentences.
- **Next lesson.** Same shape.
```
