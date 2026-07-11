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

## Wiring plan (next session)

1. `GameEngine.gd` — the line-display path (advance flow near
   `_advance()`, ~line 917): before rendering a line, regex
   `^\[(shot|panel):([^\]\r\n]+)\]\s*` off the front (repeat —
   multiple directives may stack), dispatch to VnDirector, render
   the remainder. Zero directives = today's behavior exactly.
2. VnDirector instanced by GameEngine when a locale with any
   `"vn_shot"` member loads; skipped entirely otherwise (scenes
   without markers behave as before — rollout is per-locale).
3. First directed locale: the riverfront or Kwik Stop interior —
   add `shot_establish`, one closeup per seat position, inserts
   for the register + door + tape deck.
4. MoodCycler untouched — lights are the mood's job; the camera
   is the page's.
5. Panels dir: `godot/resources/vn/panels/*.json` (HeroImage
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

## TEMPLATE — new lesson entry

```
### YYYY-MM-DD · short session title

- **Punchy lesson, present tense.** Two-to-four sentences.
- **Next lesson.** Same shape.
```
